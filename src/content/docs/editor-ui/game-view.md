---
id: editor-ui/game-view
title: "The Game view, shortcuts and who owns the keyboard"
description: "How the Game view shows a running game at its own resolution, and how Strata decides whether a key or a mouse move belongs to the game or the editor."
kind: internals
size: L
tracks: [E]
needs: [editor-ui/scene-view, editor/play-mode, input/mouse-cursor]
time: 80
learn:
  - id: letterbox-frame
    text: compute the image rectangle and the game pixel under the mouse for an aspect ratio or a fixed resolution
  - id: input-owner
    text: explain when the game gets the keyboard and the mouse, and how a person leaves it
  - id: route-shortcuts
    text: explain how a key chord reaches the global, the focused or the text field handler
  - id: trace-input
    text: trace the Game view's input ownership in the code
  - id: add-key
    text: add a Scene view key that follows the guards
since: 0.3.0
status: final
---

Two programs want the same keyboard. The editor wants **Ctrl+S** to save and **Delete** to remove the selection. The running game wants the same keys to jump or to crouch. This page explains how Strata lets the :term[Game view]{id=game-view} show the game at its own size and decides, for every key and every mouse move, who owns it.

The page also covers the editor's shortcuts and the rules that keep a stray key from changing your scene. It does not teach Play and Simulate, pausing, the :term[cursor modes]{id=cursor-mode}, or hit tests of the game's user interface. Each has its page, linked where it comes up.

## The problem and how engines solve it

Start with a simple wish: you press Play and want to try your game inside the editor. The editor is a program with panels, menus and shortcuts. The game is another program inside it, with its own idea of a window, a screen and a mouse. Four questions follow, and each has more than one answer.

**Whose camera is it?** The :term[Scene view]{id=scene-view} looks at your scene through the editor's own camera, which you fly around to build the level. The game looks through the camera that the scene marks as primary. If the editor showed only the :term[editor camera]{id=editor-camera}, you would never see what a player sees.

So an editor needs a second view of the same scene, drawn the way the game draws it. Strata calls it the Game view.

**What shape is the picture?** A game is made for a screen shape: wide, very wide, or nearly square. The panel in the editor has whatever shape you dragged it to. There are three ways out.

The view can fill the panel and stretch or crop the game. It can render the game at the panel's size, so the shape of the picture changes whenever you change the panel. Or it can keep the shape the game needs and put bars in the spare room.

The third way shows a player's picture honestly, but the bars cost :term[screen space]{id=screen-space}. The bars have a name: **letterboxing** is fitting an image of a fixed shape inside a larger area and filling the leftover strips with a flat color.

**Which pixel did the person click?** A mouse position arrives as a window pixel. The game wants a position on its own screen. These differ in two ways: the picture starts somewhere in the panel, and the game may render at 1920 by 1080 pixels while the picture takes only 900 pixels on your monitor. If the editor passes the raw window position, a button of the game's menu is hit some distance away from where it is drawn.

The editor must translate. [The mouse page](../input/mouse-cursor.md) taught this translation from the engine's side; here you see who supplies its numbers.

**Who gets the keys?** This is the hard one. While you play, the game wants every key, even **Ctrl+D**, where **Ctrl** may mean crouch. When you stop playing, those same keys must edit the scene.

The editor also has text fields: while you type a name in the Inspector, **Delete** must delete a character, and no key may reach the game or the scene. Engines answer with one of three designs.

- **Separate window.** The game runs in its own window, and the :term[operating system]{id=operating-system} sends keys to the window that has the focus. Ownership is simple, but you leave the editor to play.
- **Capture on click.** The game view takes the keyboard when you click it and gives it back on a special key. Ownership is explicit, and the view can show you how to leave.
- **Filter on every key.** The editor sees all keys and decides per key. This is flexible, but every shortcut needs its own guard, and one forgotten guard deletes your scene mid-game.

Strata takes the second design for the game and a careful version of the third for the editor's own shortcuts. The game receives input when the Game view is shown, has the focus and plays, and not otherwise. Everything else goes through two kinds of shortcuts, called global and focused, each with a short list of guards. The rest of the page builds these ideas one at a time.

A last question is the cursor. A first-person game hides the cursor and keeps it in the window, so it can read endless mouse movement. If the editor let the game do that without a way out, you would be trapped inside a panel. So the way out must be fixed, visible and out of the game's reach.

## The map

Two diagrams show where each key and each mouse move goes. The first covers :term[play mode]{id=play-mode}: it traces an event through the checks of the Game view panel and ends at either the game or the editor.

```mermaid caption="Who gets the keyboard and the mouse in play mode: the game only while its view is shown, focused and playing, and the person always has a way out." alt="A flow chart. One question comes first: is the Game view shown, focused and playing? If yes, the game reads the keys and the edit shortcuts are off, and a locked cursor makes the editor ignore the mouse. If no, the editor panels get the keys. Shift and F1, or Ctrl and P, lead back to the editor."
flowchart TD
    E["Key or mouse event"] --> Q{"Game view shown,<br/>focused and playing?"}
    Q -- yes --> G["Input module enabled<br/>game reads keys and mouse<br/>edit shortcuts off"]
    Q -- no --> P["Input module disabled<br/>editor panels get the keys"]
    G --> L{"Game locked<br/>the cursor?"}
    L -- yes --> N["UI ignores the mouse<br/>hint shown for 5 s"]
    L -- no --> M["Mouse positions in<br/>the game's pixels"]
    N -. "Shift+F1" .-> P
    G -. "Shift+F1" .-> P
    G -. "Ctrl+P" .-> S["Play stops"]
    S --> P
```

The second diagram covers a key chord, a combination such as **Ctrl+Z**, when nobody plays. It shows the two routes a shortcut can take and the guards on each.

```mermaid caption="How a key chord is routed: global shortcuts check for a modal dialog and for the game, selection shortcuts also need the keyboard focus of their panel." alt="A flow chart. An open modal dialog stops every chord. Otherwise the global route runs: Ctrl and P toggles play, and the edit chords run unless the game takes them. The focused route needs a panel with the keyboard focus and no text field, and it also stops while the game takes edit shortcuts."
flowchart TD
    K["Key chord"] --> D{"Modal dialog open?"}
    D -- yes --> X["Nothing happens"]
    D -- no --> GL["Global route"]
    D -- no --> FO["Focused route"]
    GL --> CP["Ctrl+P: always toggles play"]
    GL --> AE{"Game takes edit shortcuts?"}
    AE -- no --> ED["Ctrl+Z, Ctrl+Y, Ctrl+S,<br/>Ctrl+Shift+S, Ctrl+O, Ctrl+B"]
    AE -- yes --> X
    FO --> FP{"Panel has focus,<br/>no text field?"}
    FP -- yes --> SEL{"Game takes edit shortcuts?"}
    FP -- no --> TX["Text field or other panel<br/>keeps the key"]
    SEL -- no --> SS["Delete, Ctrl+D, Ctrl+C, Ctrl+X,<br/>Ctrl+V, End, Ctrl+A, F2"]
    SEL -- yes --> X
```

Four files own the pieces. `StrataEditor/src/Panels/GameViewPanel.cpp` draws the view and decides who owns the input. `StrataEditor/src/Editor/EditorViewport.cpp` computes the rectangle of the image. `StrataEditor/src/EditorLayer.cpp` handles the global shortcuts and Play and Stop. `StrataEditor/src/UI/EditorActions.cpp` handles the focused ones for the Hierarchy and the Scene view.

Everything runs on the :term[main thread]{id=main-thread}, in the same :term[ImGui]{id=dear-imgui} frame that draws the panels, so no lock is needed between them.

## The contract

Every caller can rely on the rules below, each with its reason.

1. **Three facts give the game its input: the view is shown, it has the focus and the scene plays.** A view hidden behind another tab, collapsed or closed is not shown. A view you have not clicked has no focus. Without these conditions your typing in another panel could move the player.
2. **A game that stops playing loses input at once.** `EditorContext::SetGameInputActive` can only hold true while the scene state is Play, so Stop ends it even if the view still has the focus.
3. **Shift+F1 always leaves.** The press moves the focus away from the view without stopping the game. A game that locked or hid the cursor gets it back, because the game no longer owns the input. Without this rule, a game that locks the cursor and ignores every other key would trap the person.
4. **Ctrl+P works whenever no modal dialog is open.** It is the only global shortcut that runs while the game has the input, so the person can stop the game from the keyboard.
5. **Nothing changes behind a modal dialog.** A modal dialog blocks the rest of the editor, but global shortcuts ignore that on their own, so every handler asks first.
6. **Edit shortcuts stay off while the game has the input.** Delete, undo, save and the rest of the list ask `EditorContext::AcceptsEditShortcuts`. A key meant for the game then never edits the scene.
7. **Selection shortcuts are focus-routed.** Delete, duplicate, copy, cut, paste and select all act only while the Hierarchy or the Scene view has the keyboard focus. A key in another panel cannot change the scene.
8. **A text field keeps its keys.** The Scene view and the Content Browser do nothing with single keys while a field takes text.

:::rule
Selection shortcuts are focus-routed. Global shortcuts check for a modal dialog and for `AcceptsEditShortcuts`. The reason is the same in both: a key press must never change the scene unless the person meant the scene. The contract above lists the guards in full.
:::

:::rule
The game receives the keyboard only from a focused Game view in play, and **Shift+F1** always leaves. The reason is that the person must never lose the keyboard and the mouse to a game they cannot stop.
:::

## A toy version

The toy below holds the three ideas of the page in about fifty lines. It fits a 16:9 image in a panel, turns a mouse position into a game pixel, and answers two yes-or-no questions: does the game get input, and are edit shortcuts allowed?

:::question
Do the C++ lines below look unfamiliar? Read [programming 1](../basics/programming-1.md), [programming 2](../basics/programming-2.md) and [programming 3](../basics/programming-3.md) first.
:::

The program takes a panel of 900 by 800 units that starts at (100, 50) in the window, a 16:9 image, and a game that renders 1920 by 1080 pixels. Look at `FitAspect`, which finds the largest rectangle of the shape, and at `ToGamePixel`, which undoes the offset and then scales.

```cpp sketch="editor-ui-game-view-toy.cpp"
// A toy Game view: fit an aspect ratio in a panel, map a mouse position to the game's pixels, decide who gets the keys.
#include <cmath>
#include <cstdio>
#include <glm/glm.hpp>

struct Frame
{
	glm::vec2 Offset;
	glm::vec2 Size;
};

// The largest rectangle of the aspect ratio inside the area, centered on whole units.
Frame FitAspect(const glm::vec2& area, float aspect)
{
	glm::vec2 size(area.x, area.x / aspect);
	if (size.y > area.y)
		size = glm::vec2(area.y * aspect, area.y);
	size = glm::floor(size);
	return { glm::floor((area - size) * 0.5f), size };
}

// A window position in the game's pixels: out of the panel, out of the bars, then scaled to the resolution.
glm::vec2 ToGamePixel(const glm::vec2& mouse, const glm::vec2& areaMin, const Frame& frame, const glm::vec2& resolution)
{
	return (mouse - areaMin - frame.Offset) * resolution / frame.Size;
}

struct EditorState
{
	bool Modal;
	bool Playing;
	bool GameShown;
	bool GameFocused;
};

bool GameGetsInput(const EditorState& state)
{
	return state.GameShown && state.GameFocused && state.Playing;
}

bool EditShortcutsAllowed(const EditorState& state)
{
	return !state.Modal && !GameGetsInput(state);
}

int main()
{
	const glm::vec2 areaMin(100.0f, 50.0f);
	const Frame frame = FitAspect(glm::vec2(900.0f, 800.0f), 16.0f / 9.0f);
	std::printf("image %.0f x %.0f at offset %.0f, %.0f\n", frame.Size.x, frame.Size.y, frame.Offset.x, frame.Offset.y);

	const glm::vec2 pixel = ToGamePixel(glm::vec2(550.0f, 400.0f), areaMin, frame, glm::vec2(1920.0f, 1080.0f));
	std::printf("mouse (550, 400) is game pixel %.1f, %.1f\n", pixel.x, pixel.y);

	const EditorState editing = { false, false, true, true };
	const EditorState playing = { false, true, true, true };
	const EditorState typing = { false, true, true, false };
	std::printf("editing: game %d, edit keys %d\n", GameGetsInput(editing), EditShortcutsAllowed(editing));
	std::printf("playing: game %d, edit keys %d\n", GameGetsInput(playing), EditShortcutsAllowed(playing));
	std::printf("typing in the Inspector: game %d, edit keys %d\n", GameGetsInput(typing), EditShortcutsAllowed(typing));
	return 0;
}
```

```text output-of="editor-ui-game-view-toy.cpp"
image 900 x 506 at offset 0, 147
mouse (550, 400) is game pixel 960.0, 433.3
editing: game 0, edit keys 1
playing: game 1, edit keys 0
typing in the Inspector: game 0, edit keys 1
```

1. **Lines 15–19:** `FitAspect` tries the full width, then the full height, floors the size and centers it.
2. **Line 25:** the mouse loses the panel's corner, then the bar, then is scaled to the game's resolution.
3. **Line 38:** the three facts of the contract, joined by and.
4. **Line 43:** edit shortcuts need no modal and no game input.

The first line shows letterboxing at work. A 16:9 image 900 units wide is only 506 units high, so it leaves 294 units of height. The bars take half each: 147 units above and 147 below.

The mouse at window position (550, 400) lies 450 units right and 350 units down from the panel's corner. The image starts 147 units down, so the mouse is 203 units down in the image. Scaling by 1920 divided by 900 and by 1080 divided by 506 gives the game pixel in the second line.

The last three lines show the guards. Editing and not playing: the game gets nothing and edit keys work. Playing with the view focused: the game gets the keys and the edit keys are off. Playing while you type in the Inspector: the view is not focused, so the game gets nothing and the edit keys work. The real code has the same three outcomes and more states.

:::example
You drag the Game view to a tall, narrow panel: 600 units wide and 1000 units tall, with a display scale of 1. You choose **16:9**. The image is 600 by 337.5 units; the engine floors it to 600 by 337. The leftover height is 663 units, so the bar above is 331 units high (663 halved, then floored).

You then choose **1920 x 1080**. The rectangle on screen does not change, because its shape is the same. The picture now holds 1920 by 1080 pixels, scaled down by 3.2 in each direction. A click 300 units across the image lands on game pixel 960, the middle of the game's width.
:::

## The real code

The real code follows the order of a frame: first the rectangle of the image, then the ownership of input, then the shortcuts that run around them, then the play and stop :term[hand-over]{id=hand-over}.

### The rectangle of the image

`ComputeGameViewFrame` turns the panel's size and the chosen mode into three things: the offset of the image, its size on screen, and the number of pixels to render. It treats two kinds of mode apart. **Free** fills the panel. An aspect ratio (**16:9**, **16:10**, **4:3**, **21:9**) or a fixed size (**1920 x 1080**, **1280 x 720**, a custom size, or the game's own request) needs the fit.

The next quote is the fit. Notice the order: try the full width, and if the height does not fit, take the full height instead. The floors keep whole units, which keeps the bars sharp.

```cpp src="StrataEditor/src/Editor/EditorViewport.cpp#L265-L270" from="glm::vec2 size(areaSize.x, areaSize.x / *aspect);" to="frame.Offset = glm::floor((areaSize - size) * 0.5f);" symbol="ComputeGameViewFrame"
glm::vec2 size(areaSize.x, areaSize.x / *aspect);
if (size.y > areaSize.y)
	size = glm::vec2(areaSize.y * *aspect, areaSize.y);
size = glm::max(glm::floor(size), glm::vec2(1.0f));
frame.Size = size;
frame.Offset = glm::floor((areaSize - size) * 0.5f);
```

An aspect ratio mode renders at the picture's own size, in pixels, and derives the height from the width, so the shape stays exact. A fixed mode renders at exactly the fixed pixels, and the image on screen is that picture scaled to fit.

Compare **16:9** and **1920 x 1080** in the resolution menu. The first picks the shape and follows the panel's pixels. The second also fixes the pixel count, so shadows and text look the same on a small laptop screen and a large monitor. The cost is a picture that is scaled when the panel is smaller or larger.

::figure{id=letterboxed-16x9}

::figure{id=fixed-1920x1080}

Two limits protect the :term[renderer]{id=renderer}. A custom size is clamped to the range 16 to 8192 in each direction when you press **Use**. And before rendering, the panel shrinks a fixed size that is beyond what the graphics device supports, keeping its shape, by `MaxTextureDimension2D`.

The resolution menu has these entries, in order: **Free (fills the panel)**, **16:9**, **16:10**, **4:3**, **21:9**, then a line, then **1920 x 1080** and **1280 x 720 (exported games' window)**. The last item is a **Custom** pair of fields and a **Use** button.

An entry **Game's request** appears while the game asked for a window size, or while that mode is chosen. In the editor, the shell records the request and does not apply it, as [the play mode page](../editor/play-mode.md) explains. This mode lets you see what the game would get. Without a request the mode behaves as Free, and the chip reads **Game's (none: free)**.

You can set the same values by a command, which is how a scripted test drives the view. The mode names are `free`, `16:9`, `16:10`, `4:3`, `21:9`, `1920x1080`, `1280x720`, `custom` and `game`.

```json
{
	"gameView": { "mode": "custom", "width": 1280, "height": 720 }
}
```

The :term[JSON]{id=json} holds the parameters of `viewport.setSettings`. Run it, then play, and click a button that the game draws on its screen. The button must react where it is drawn, because `Input::SetViewport` carries the image's offset, size and rendered resolution, as the next section shows.

### Who owns the input

The panel calls `UpdateGameInput` every frame it is drawn, and once more with `shown` false when it is hidden or removed. The first quote holds the escape and the ownership test. Read the condition of the first line, then the line that names `enabled`.

```cpp src="StrataEditor/src/Panels/GameViewPanel.cpp#L245-L257" from="if (shown && m_Focused && ImGui::GetIO().KeyShift" to="Input::SetEnabled(enabled);" symbol="GameViewPanel::UpdateGameInput"
if (shown && m_Focused && ImGui::GetIO().KeyShift && ImGui::IsKeyPressed(ImGuiKey_F1, false))
{
	ImGui::SetWindowFocus(nullptr);
	m_Focused = false;
}

// Scripts read Input: only the focused Game view feeds it, with positions in the image's pixels. A game that hid or
// locked the cursor gives it back when it loses the input and takes it again when it gets the input back
// (Input::SetGameCursorMode applies only while input is enabled).
const bool enabled = shown && m_Focused && context.GetSceneState() == SceneState::Play;
m_GameInputEnabled = enabled;
context.SetGameInputActive(enabled);
Input::SetEnabled(enabled);
```

1. **Line 245:** the chord is asked only while the view is shown, because `Reset` calls this function when the editor detaches and no ImGui frame exists then. The `false` stops :term[key repeat]{id=key-repeat}.
2. **Line 247:** giving the focus to no window means the next frame finds the view without the focus, so it withdraws the game's input.
3. **Line 254:** `enabled` is the whole contract: shown, focused and playing.
4. **Lines 256–257:** `SetGameInputActive` switches the edit shortcuts off, and `Input::SetEnabled` lets the game read the keys.

A game that asked for a hidden or locked cursor gets that mode only while input is enabled. When you leave, the engine gives the cursor back. When you return, it takes the cursor again.

A locked cursor needs one more rule. Without it, a click would reach another panel, because a locked cursor still has a position that the editor sees. The second quote sets the flag that stops this, starts the hint, and then tells the input module where the game's screen is.

```cpp src="StrataEditor/src/Panels/GameViewPanel.cpp#L260-L279" from="const bool gameOwnsMouse" to="m_Image.Size, glm::vec2(m_RenderSize));" symbol="GameViewPanel::UpdateGameInput"
const bool gameOwnsMouse = enabled && Input::GetGameCursorMode() == CursorMode::Locked;
// Detaching runs this after the ImGui context is gone.
if (gameOwnsMouse != m_GameOwnsMouse && ImGui::GetCurrentContext())
{
	m_GameOwnsMouse = gameOwnsMouse;
	ImGuiIO& io = ImGui::GetIO();
	if (gameOwnsMouse)
		io.ConfigFlags |= ImGuiConfigFlags_NoMouse;
	else
		io.ConfigFlags &= ~ImGuiConfigFlags_NoMouse;
	// Without a pointer nothing on screen leads out: the view says how, for a while after each time it took it.
	if (gameOwnsMouse)
		m_MouseHintUntil = ImGui::GetTime() + c_MouseHintSeconds;
}
// The game's screen is the image the view shows, in every frame it shows play, focused or not: the game's window size,
// UI hit tests and simulated mouse positions all read it (Input::GetViewportSize, at the rendered resolution).
if (shown && context.GetSceneState() == SceneState::Play && m_Image.Size.x > 0.0f && m_Image.Size.y > 0.0f)
{
	const ImVec2 origin = ImGui::GetMainViewport()->Pos;
	Input::SetViewport(glm::vec2(m_Image.Min.x - origin.x, m_Image.Min.y - origin.y), m_Image.Size, glm::vec2(m_RenderSize));
```

1. **Line 260:** a locked cursor counts only while the game has the input.
2. **Line 267:** `ImGuiConfigFlags_NoMouse` makes the editor's interface ignore the mouse; line 269 clears it again.
3. **Line 272:** the hint timer starts each time the game takes the mouse.
4. **Lines 276–279:** the image's offset, size and rendered resolution go to the input module, whatever the focus.

While `gameOwnsMouse` holds, the editor's interface ignores the mouse. The code changes the flag only when the state changes, and it checks that an :term[ImGui context]{id=imgui-context} exists, because detaching runs after the context is gone. Without a pointer nothing on screen leads out. So the panel starts a timer of five seconds, `c_MouseHintSeconds`, and for that time `DrawOverlays` shows a box at the top of the image: "Shift+F1 frees the mouse · Ctrl+P stops the game". The hint shows again each time the game takes the mouse.

The chips of the view, the resolution and the statistics, never take focus when you click them, so using a chip does not steal the game's keyboard. The [widget kit](../editor-ui/widget-kit.md) page explains that rule.

::figure{id=locked-cursor-hint}

The last block runs every frame the view shows play, focused or not. The game's window size, the hit tests of its interface and simulated mouse positions all read the screen the view supplies. So `Input::SetViewport` receives the offset of the image inside the window, its size on screen and the rendered resolution. The engine divides the resolution by the size to get game pixels per window pixel, as the [mouse page](../input/mouse-cursor.md) shows. In the toy's numbers, a click at the image's middle is pixel 960, 540 of 1920 by 1080.

The game's interface scale in play is the display's, or the value of the editor's `--ui-scale` option, without the factor you set for the editor; [the scale page](../editor-ui/ui-scale.md) explains the editor's side.

Two details keep the picture honest. A window flag, `ImGuiWindowFlags_NoNavInputs`, is set on the panel while the game has the input, so arrows, Space and Enter belong to the game and not to keyboard navigation of the chips. And when the view is hidden, `OnHidden` calls `Reset`, which disables input, sets the Game view's size in `EditorViewport` to zero and releases the :term[render targets]{id=render-target}. A hidden Game view keeps no render targets and renders nothing.

### Showing the game without a camera

When the scene has no entity with a :term[primary camera]{id=primary-camera}, the view releases its targets and draws a centered notice in the secondary text color. The notice says "No camera to show", then names the scene and the missing Camera component. An exported game shows the same text, so you see the same message in both places.

A scene with user interface but no camera, such as a main menu, is the exception. The view then shows the interface over black, as the game does.

::figure{id=no-camera}

### Play, stop and the keyboard

Play must hand the keyboard to the game, or the person would press Play and then have to click the view. `EditorLayer::StartPlay` does this when the command finishes.

```cpp src="StrataEditor/src/EditorLayer.cpp#L1543-L1547" from="const GameViewPanel* game = m_Panels.Get<GameViewPanel>(EditorPanels::c_Game);" to="m_PlayShowedGame = true;" symbol="EditorLayer::StartPlay"
const GameViewPanel* game = m_Panels.Get<GameViewPanel>(EditorPanels::c_Game);
if (result.Success && game && m_Panels.IsOpen(EditorPanels::c_Game) && !game->IsShown())
{
	m_Panels.Focus(EditorPanels::c_Game);
	m_PlayShowedGame = true;
```

Read the condition. The Game view must be open, and it must not already be shown. If it is docked behind the Scene view's tab, `Focus` brings it forward, which also gives it the keyboard focus, and the next frame `UpdateGameInput` enables the input. The flag `m_PlayShowedGame` remembers that Play did this.

```cpp src="StrataEditor/src/EditorLayer.cpp#L1552-L1559" symbol="EditorLayer::StopPlay"
void EditorLayer::StopPlay()
{
	RunEditorCommand(m_Context, m_Commands, "play.stop");
	// Back to the Scene view when Play had brought the Game view forward.
	if (m_PlayShowedGame && !m_Context.IsPlaying() && m_Panels.IsOpen(EditorPanels::c_Viewport))
		m_Panels.Focus(EditorPanels::c_Viewport);
	m_PlayShowedGame = false;
}
```

Stop reverses only what Play did. If the flag is set and the game really stopped, the Scene view comes back. A person who had the Game view open beside the Scene view from the start is left where they were. Pausing and stepping change none of this; see [the stepping page](../editor/stepping.md).

### The global shortcuts

Now the shortcuts. `EditorLayer::HandleShortcuts` runs once per frame, before the :term[dock space]{id=dock-space} is drawn.

```cpp src="StrataEditor/src/EditorLayer.cpp#L1240-L1261" from="if (ImGui::GetTopMostPopupModal())" to="SaveScene();" symbol="EditorLayer::HandleShortcuts"
if (ImGui::GetTopMostPopupModal())
	return;
const ImGuiInputFlags global = ImGuiInputFlags_RouteGlobal;
// Play mode toggles always: it is also the way out of a game that has the input.
if (ImGui::Shortcut(ImGuiMod_Ctrl | ImGuiKey_P, global))
{
	if (m_Context.IsPlaying())
		StopPlay();
	else
		StartPlay();
}
// Keys the running game receives (e.g. Delete, or Ctrl+D with Ctrl to crouch) must not edit the scene.
if (!m_Context.AcceptsEditShortcuts())
	return;
// Undo and redo go through their commands, so the activity journal shows them and replays repeat them.
if (ImGui::Shortcut(ImGuiMod_Ctrl | ImGuiKey_Z, global) && m_Context.GetUndoStack().CanUndo() && !m_Context.IsPlaying())
	RunEditorCommand(m_Context, m_Commands, "edit.undo");
if ((ImGui::Shortcut(ImGuiMod_Ctrl | ImGuiKey_Y, global) || ImGui::Shortcut(ImGuiMod_Ctrl | ImGuiMod_Shift | ImGuiKey_Z, global))
	&& m_Context.GetUndoStack().CanRedo() && !m_Context.IsPlaying())
	RunEditorCommand(m_Context, m_Commands, "edit.redo");
if (ImGui::Shortcut(ImGuiMod_Ctrl | ImGuiKey_S, global))
	SaveScene();
```

1. **Line 1240:** a modal dialog stops every shortcut, because global routes ignore modal dialogs.
2. **Line 1244:** **Ctrl+P** runs before the game test, as the way out of a game that has the input.
3. **Line 1252:** the edit shortcuts stop while the game owns the input.
4. **Lines 1255–1256:** undo runs the command `edit.undo`, so the journal records it; it needs something to undo and no play.

A **shortcut routing** is the rule that says which window may receive a key chord; ImGui offers several. **Shortcut routing** in Strata uses two of them: `ImGuiInputFlags_RouteGlobal`, which accepts the chord wherever the focus is, and `ImGuiInputFlags_RouteFocused`, which accepts it only while the window or a window inside it has the keyboard focus. The global route is what makes **Ctrl+S** save from any panel. Its cost is that it ignores modal dialogs, so the code asks first.

The guards stand in a fixed order, from the most general to the most specific. A modal stops everything. **Ctrl+P** comes next, before the game check, because it is the way out.

Then `AcceptsEditShortcuts` stops all the edit shortcuts while the game owns the input. Undo and redo run the commands `edit.undo` and `edit.redo` rather than calling the :term[undo stack]{id=undo-stack}, so the activity journal records them and a replayed script repeats them. Both also check `IsPlaying`: edits of a :term[running copy]{id=running-copy} are not part of the scene's history. The chords **Ctrl+Y** and **Ctrl+Shift+Z** both redo.

After the quote come **Ctrl+Shift+S** (save as), **Ctrl+O** (open) and **Ctrl+B** (build the scripts). Like the menu item and its button, **Ctrl+B** does nothing while a build runs.

### The focused shortcuts

The selection's shortcuts live in `StrataEditor/src/UI/EditorActions.cpp`, because the Hierarchy and the Scene view share them.

```cpp src="StrataEditor/src/UI/EditorActions.cpp#L318-L337"
void HandleSelectionShortcuts(EditorContext& context, const EditorCommandRegistry& commands, bool selectAll)
{
	if (ImGui::GetTopMostPopupModal() || !context.AcceptsEditShortcuts())
		return;
	// RouteFocused (ImGui::Shortcut's default): only while this window or one inside it has the keyboard focus.
	constexpr ImGuiInputFlags c_Focused = ImGuiInputFlags_RouteFocused;
	if (ImGui::Shortcut(ImGuiKey_Delete, c_Focused))
		DeleteSelection(context, commands);
	if (ImGui::Shortcut(ImGuiMod_Ctrl | ImGuiKey_D, c_Focused))
		DuplicateSelection(context, commands);
	if (ImGui::Shortcut(ImGuiMod_Ctrl | ImGuiKey_C, c_Focused))
		CopySelection(context, commands);
	if (ImGui::Shortcut(ImGuiMod_Ctrl | ImGuiKey_X, c_Focused))
		CutSelection(context, commands);
	if (ImGui::Shortcut(ImGuiMod_Ctrl | ImGuiKey_V, c_Focused))
		Paste(context, commands);
	if (ImGui::Shortcut(ImGuiKey_End, c_Focused))
		DropSelectionToGround(context, commands);
	if (selectAll && ImGui::Shortcut(ImGuiMod_Ctrl | ImGuiKey_A, c_Focused))
		SelectAll(context);
```

1. **Line 320:** the same two guards as the global route.
2. **Line 323:** `RouteFocused` accepts a chord only while the panel has the focus.
3. **Lines 324–335:** each chord calls one function, which the Edit menu calls too.
4. **Lines 336–337:** **Ctrl+A** works only where the caller asked for it with `selectAll`.

The Hierarchy calls this function with `selectAll` false, and the Scene view with true, so **Ctrl+A** selects all entities only in the Scene view. Every `ImGui::Shortcut` below uses `RouteFocused`, which is also ImGui's default. A press in the Inspector, the Console or the Content Browser never reaches these lines, because those panels do not call this function. **End** drops the selection to the ground.

The Edit menu items for cut, copy and paste call the same functions, so a menu click and a key press behave alike. The clipboard holds JSON text: `CopySelection` writes the entities' data with `ImGui::SetClipboardText`, and `Paste` reads it back and checks its format. Paste what you copied into a text editor and you can read it.

**F2** renames the primary selection. The Hierarchy and the Scene view each handle it with `RouteFocused`, and both skip it while the game takes the edit shortcuts. The Content Browser has its own handler for **Delete**, **F2** and **Backspace**, and it runs only while the browser has the focus, no text field takes text and no :term[popup]{id=popup} is open. There **Delete** opens a dialog for the selected asset or folder, which checks what uses it; it never deletes entities.

### The Scene view's keys

The Scene view adds single-letter keys for its tools, found in `ViewportPanel::HandleShortcuts`. Here the guard is longer, because these keys are bare letters and bare letters are also typing.

```cpp src="StrataEditor/src/Panels/ViewportPanel.cpp#L882-L911" from="if (!(m_Hovered || m_Focused)" to="settings.PilotGameCamera = !settings.PilotGameCamera;" symbol="ViewportPanel::HandleShortcuts"
if (!(m_Hovered || m_Focused) || io.WantTextInput || m_CameraDrag == CameraDrag::Fly || m_GizmoDrag || ImGuizmo::IsUsing() || io.KeyCtrl || io.KeyAlt
	|| io.KeySuper)
{
	return;
}

ViewportSettings& settings = context.GetViewport().GetSettings();
if (ImGui::IsKeyPressed(ImGuiKey_Q, false))
	settings.Gizmo = GizmoOperation::None;
if (ImGui::IsKeyPressed(ImGuiKey_W, false))
	settings.Gizmo = GizmoOperation::Translate;
if (ImGui::IsKeyPressed(ImGuiKey_E, false))
	settings.Gizmo = GizmoOperation::Rotate;
if (ImGui::IsKeyPressed(ImGuiKey_R, false))
	settings.Gizmo = GizmoOperation::Scale;
if (ImGui::IsKeyPressed(ImGuiKey_F, false) && !io.KeyShift)
{
	std::vector<Entity> selection;
	for (UUID id : context.GetSelection())
	{
		if (Entity entity = context.GetActiveScene()->GetEntityByUUID(id))
			selection.push_back(entity);
	}
	if (!selection.empty())
		context.GetViewport().Focus(context, selection);
}
if (ImGui::IsKeyPressed(ImGuiKey_Home, false))
	context.GetViewport().Focus(context, {});
if (ImGui::IsKeyPressed(ImGuiKey_F8, false))
	settings.PilotGameCamera = !settings.PilotGameCamera;
```

1. **Lines 882–883:** the guard: hovered or focused, no text input, no camera fly, no :term[gizmo]{id=gizmo-start} drag, no modifier key.
2. **Lines 889–896:** **Q**, **W**, **E** and **R** choose the gizmo.
3. **Lines 897–907:** **F** frames the selection, and not with **Shift** held.
4. **Lines 908–909:** **Home** frames the whole scene, with an empty list.
5. **Lines 910–911:** **F8** toggles piloting the :term[game camera]{id=game-camera-pilot}.

The quote starts with a guard that returns early in several cases. The view must be hovered or focused. No text field may want text.

The editor camera must not be flying, because **W**, **A**, **S**, **D**, **Q** and **E** move it then. No :term[gizmo]{id=gizmo-start} may be dragged, because its operation must not change under the mouse. And no **Ctrl**, **Alt** or **Super** key may be down, so **Ctrl+C** never selects a tool.

The keys are **Q** (no gizmo), **W** (move), **E** (rotate), **R** (scale), **F** (frame the selection; **Shift+F** is left free), **Home** (frame the whole scene) and **F8**, which toggles piloting the :term[game camera]{id=game-camera-pilot}. The Scene view then shows the scene through its primary camera, with the editor's :term[overlays]{id=overlay-core}. The [Scene view page](scene-view.md) teaches the tools these keys select.

Delete, duplicate and the other selection shortcuts run before this guard, with their own, shorter test: not during a camera fly and not during a gizmo drag.

### The macOS case

On macOS the chord **Cmd+Z** undoes, and the code says `ImGuiMod_Ctrl`. That works because :term[Dear ImGui]{id=dear-imgui} swaps the two keys when `ConfigMacOSXBehaviors` is set, which it sets on Apple builds. The platform backend passes keys as they are: the left Super key arrives as Super, and ImGui turns it into Ctrl. A test, `With macOS behaviors, Cmd is the shortcut modifier and Ctrl takes Cmd's place`, pins this. So the page's **Ctrl** chords are **Cmd** chords on macOS, and the code needs no special case.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Run the game in its own window | Editors that start the game as a separate program | The operating system routes keys; no ownership code | You leave the editor to play, and no shared panels or tools |
| Stretch the picture to the panel | Simple embedded previews | No bars and no fixed sizes | A picture whose shape changes while you drag the panel, so you judge the wrong shape |
| Editor shortcuts that a person can rebind | Many editors with a key settings page | A person with other habits could choose chords | A preference section, a conflict check and a way to show the chords; the chords are now literal keys in the code |
| One global key handler with a table | Editors with a central key table | One place to see every chord | Panels that know their focus would lose it, so guards move far from what they protect |
| Always capture the mouse in play | Games, not editors | A game that locks the cursor could not leak a click | A person with no visible way out; the hint and **Shift+F1** exist for this |

## How it is tested

The behavior has tests in three suites: `Editor.UI`, in `StrataTests/src/Editor/EditorUITests.cpp`; `Editor.Viewport`, in `StrataTests/src/Editor/EditorViewportTests.cpp`; and `Editor.UI.Hierarchy`, in `StrataTests/src/Editor/EditorAuthoringUITests.cpp`.

One test, `The Game view letterboxes aspect ratios and scales fixed resolutions to fit`, checks the rectangle and the render size. Another test, `While the game plays, the Game view gives it its screen at the rendered resolution, focused or not`, checks `Input::SetViewport`. A third, `A cursor the game locks stays in the game view, which says how to free it; Shift+F1 and stopping free it`, covers the lock, the hint and the way out. `The Game view is a tab beside the Scene view, and Play brings it forward and gives the game the keyboard` checks the hand-over. `Only a playing game takes the input, and edit shortcuts stay off meanwhile` pins `AcceptsEditShortcuts`, and `Delete deletes the selection only while the Hierarchy or the Viewport has the keyboard focus` pins the focus route.

Run the Game view tests with the doctest filter shown below, from the build folder of your preset.

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=Editor.UI --test-case="*Game view*"
```

The command runs every test of the suite whose name holds the words Game view. The tests that need a :term[graphics card]{id=gpu}, such as the one that renders a scene without a camera but with a user interface, sit in the `GPU.Editor.Viewport` suite.

## Changing it safely

Most changes add a key. The extension point is the handler of the panel that should own the key. A global chord belongs in `EditorLayer::HandleShortcuts`; a key for the Scene view in `ViewportPanel::HandleShortcuts`; a key on the selection in `EditorActions::HandleSelectionShortcuts`.

Follow these rules. Check for a modal first, because global routes ignore modal dialogs. Check `AcceptsEditShortcuts` for anything that edits the scene or the project, because the game may own the key.

Prefer `RouteFocused` unless the key must work from every panel. Let the key run a command, as `edit.undo` does, so the journal and replays see it. Never write a file from a shortcut; panels only draw and call commands, because every change goes through a command.

A new chord should also appear in the Edit menu or a tool tip. The generated shortcut table in [the editor reference](../reference/editor.md) holds the full list.

Strata does not let a person rebind the editor's shortcuts. The chords are literal keys in calls of `ImGui::Shortcut`, and no preference section holds them: the preferences have three sections, the external editor, the interface and the :term[frame rate]{id=frame-rate}. The file `Docs/Roadmap.md` of the engine leaves rebinding editor shortcuts for later. A game's own controls are different: those are input actions, which the player may rebind.

Before you commit a change, run the `Editor.UI`, `Editor.UI.Hierarchy` and `Editor.Viewport` suites, and add a test that fails without your guard.

## Summary

- The image is the largest rectangle of the mode's shape that fits the panel. A fixed resolution renders at its exact pixels and is scaled to fit, and `Input::SetViewport` maps mouse positions to the game's pixels.
- The game receives the keyboard and the mouse when the Game view is shown, focused and playing. **Shift+F1** frees the focus, **Ctrl+P** stops the game, and a locked cursor makes the editor ignore the mouse.
- A global shortcut checks for a modal and for the game; a focused shortcut also needs its panel's keyboard focus, and text fields keep their keys.
- `UpdateGameInput` sets `Input::SetEnabled`, `SetGameInputActive` and `ImGuiConfigFlags_NoMouse` from three facts: shown, focused and playing.
- A new Scene view key follows the guards of `ViewportPanel::HandleShortcuts`, and a new selection shortcut follows those of `EditorActions::HandleSelectionShortcuts`.

## Check yourself

1. You press Play in a layout where the Game view is a tab behind the Scene view. Which statement is true a moment later? (a) The Scene view keeps the focus and the game gets no input until you click. (b) The Game view comes forward and takes the keyboard, so the game gets input. (c) The Game view comes forward but the game gets input only after **Ctrl+P**.

   :::answer{tests="input-owner,trace-input"}
   Statement (b). `StartPlay` focuses a Game view that is open but not shown, and the next frame `UpdateGameInput` finds it shown, focused and playing. Statement (a) is wrong because Play does the focusing for you. Statement (c) is wrong because **Ctrl+P** is the chord that toggles Play itself, not a key that gives input.
   :::

2. A panel of 900 by 800 units shows 4:3 at a display scale of 1. Give the image's size and the offset of its top-left corner.

   :::answer{tests="letterbox-frame"}
   The width 900 gives a height of 675, which fits in 800. The size is 900 by 675. The leftover height is 125, so the offset is 0 across and floor(62.5) = 62 down.
   :::

3. The toy prints "typing in the Inspector: game 0, edit keys 1" while a game plays. Why is that the right answer, and what stops **Delete** from deleting an entity there?

   :::answer{tests="route-shortcuts"}
   The Inspector has the focus, so the Game view is not focused and the game gets no input. The edit keys are allowed, but **Delete** is a focused shortcut of the Hierarchy and the Scene view only, and the Inspector has neither. A text field also keeps the key for itself.
   :::

4. A modal dialog is open and you press **Ctrl+S**. What happens, and which line of the code decides it?

   :::answer{tests="route-shortcuts"}
   Nothing. Global routes ignore modal dialogs, so `HandleShortcuts` returns early when `ImGui::GetTopMostPopupModal()` is set. The same test stands in `HandleSelectionShortcuts`.
   :::

5. A first-person game locks the cursor, and the person clicks outside the Game view. Explain what the click does and how the person gets the mouse back.

   :::answer{tests="input-owner"}
   Nothing reaches the interface: `ImGuiConfigFlags_NoMouse` is set while the game owns a locked cursor, so no click lands on another panel. The person presses **Shift+F1**, which removes the focus, ends the game's input and frees the cursor, or **Ctrl+P**, which stops the game.
   :::

6. You want a bare **G** key in the Scene view. Which function gets the new line, and which guards come for free?

   :::answer{tests="add-key,route-shortcuts"}
   `ViewportPanel::HandleShortcuts`, after its early `return`. The guard before it requires a hovered or focused view, no text input, no camera fly, no gizmo drag and no **Ctrl**, **Alt** or **Super** key. A global handler would lack the focus test, so **G** would fire in every panel.
   :::

## Exercises

1. **Basic.** Set the Game view to **1280 x 720** in a panel 1000 units wide and 500 tall at scale 1. Give the image's size and offset, and the game pixel under a mouse at 278 units across and 125 down in the panel.

   :::answer{tests="letterbox-frame"}
   The shape is 16:9. The full width gives 562.5 tall, which is more than 500, so take the full height: 500 times 1.7778 is 888.9, floored to 888. The size is 888 by 500, the offset is floor(112 / 2) = 56 across and 0 down. The click lies 222 units into the image across and 125 down. Scale by 1280 / 888 and 720 / 500: the game pixel is (320, 180).
   :::

2. **Medium.** The sketch below routes a key to one owner. Predict its five lines, then run it. Then say what it omits compared with the real editor.

   :::answer[Worked solution]{tests="route-shortcuts" solution="sketches/editor-ui-game-view-router.cpp"}
   Delete in the Hierarchy goes to the focused panel. Delete while renaming goes to the text field. Delete while the game plays goes to the game. Ctrl+S goes to a global shortcut, and in a dialog it goes to the modal.

   ```cpp sketch="editor-ui-game-view-router.cpp"
   // A key press goes to the first owner that wants it: a modal, the game, a text field, the focused panel, then global shortcuts.
   #include <cstdio>
   #include <string>

   enum class Owner
   {
   	Modal,
   	Game,
   	TextField,
   	FocusedPanel,
   	Global,
   	Nobody
   };

   struct Situation
   {
   	bool Modal;
   	bool GameInput;
   	bool TextFocus;
   	bool PanelFocus;
   	bool KeyIsGlobal;
   };

   Owner Route(const Situation& situation)
   {
   	if (situation.Modal)
   		return Owner::Modal;
   	if (situation.GameInput)
   		return Owner::Game;
   	if (situation.TextFocus)
   		return Owner::TextField;
   	if (situation.PanelFocus)
   		return Owner::FocusedPanel;
   	return situation.KeyIsGlobal ? Owner::Global : Owner::Nobody;
   }

   std::string Name(Owner owner)
   {
   	switch (owner)
   	{
   		case Owner::Modal:        return "modal";
   		case Owner::Game:         return "game";
   		case Owner::TextField:    return "text field";
   		case Owner::FocusedPanel: return "focused panel";
   		case Owner::Global:       return "global shortcut";
   		case Owner::Nobody:       return "nobody";
   	}
   	return "nobody";
   }

   int main()
   {
   	const Situation delete1 = { false, false, false, true, false };
   	const Situation delete2 = { false, false, true, true, false };
   	const Situation delete3 = { false, true, false, false, false };
   	const Situation save = { false, false, false, false, true };
   	const Situation saveInDialog = { true, false, false, false, true };
   	std::printf("Delete in the Hierarchy: %s\n", Name(Route(delete1)).c_str());
   	std::printf("Delete while renaming: %s\n", Name(Route(delete2)).c_str());
   	std::printf("Delete while the game plays: %s\n", Name(Route(delete3)).c_str());
   	std::printf("Ctrl+S: %s\n", Name(Route(save)).c_str());
   	std::printf("Ctrl+S in a dialog: %s\n", Name(Route(saveInDialog)).c_str());
   	return 0;
   }
   ```

   ```text output-of="editor-ui-game-view-router.cpp"
   Delete in the Hierarchy: focused panel
   Delete while renaming: text field
   Delete while the game plays: game
   Ctrl+S: global shortcut
   Ctrl+S in a dialog: modal
   ```

   1. **Lines 26–27:** a modal dialog comes first and takes every key.
   2. **Lines 28–29:** the game comes next, so a key meant for it never reaches a panel.
   3. **Lines 30–33:** a text field keeps its keys before the focused panel sees them.
   4. **Line 34:** a global key works only when no one above wanted it.

   The sketch is one chain of tests. The real editor has two routes: a global handler in the layer, and focused handlers in the panels, each with its own guards. The sketch also omits that the focused handlers ask the game's state too.
   :::

3. **Medium.** Add a key **G** to the Scene view that toggles the grid, following the guards. Name the file, the function and the setting.

   :::answer[Worked solution]{tests="add-key"}
   Open `StrataEditor/src/Panels/ViewportPanel.cpp`, function `ViewportPanel::HandleShortcuts`. Add the line `if (ImGui::IsKeyPressed(ImGuiKey_G, false)) settings.ShowGrid = !settings.ShowGrid;` after the **F8** line, below the early `return`. Placing it there gives it every guard for free: hovered or focused, no text input, no fly, no gizmo drag, no **Ctrl**, **Alt** or **Super**. The setting `ViewportSettings::ShowGrid` already exists. A test presses **G** with the view focused and checks that the grid flips, and presses it with a text field active and checks that it does not.
   :::

4. **Hard.** Trace it yourself. Start a game in the editor with a debugger or a search, and find where the Game view switches the input module on and off; find where `ImGuiConfigFlags_NoMouse` is set; find what **Shift+F1** changes.

   :::answer[Worked solution]{tests="trace-input"}
   Put a breakpoint in `GameViewPanel::UpdateGameInput` in `StrataEditor/src/Panels/GameViewPanel.cpp`. While the game plays and the view is focused, `enabled` is true and `Input::SetEnabled(true)` runs. Click another panel: the next frame `m_Focused` is false and the call is `Input::SetEnabled(false)`. Let the game lock the cursor: `gameOwnsMouse` turns true and the code sets `ImGuiConfigFlags_NoMouse`.

   Press **Shift+F1**: the first lines call `ImGui::SetWindowFocus(nullptr)` and set `m_Focused` to false. The flag clears at once, because `enabled` is false.
   :::

## Where it lives in Strata

- Panel and input ownership: `StrataEditor/src/Panels/GameViewPanel.cpp`, `GameViewPanel::UpdateGameInput`, `DrawResolutionChip`, `DrawNoCamera`.
- The image rectangle: `StrataEditor/src/Editor/EditorViewport.cpp`, `ComputeGameViewFrame`, `GameViewMode`, `GameViewSettings`.
- Global shortcuts, Play and Stop: `StrataEditor/src/EditorLayer.cpp`, `EditorLayer::HandleShortcuts`, `StartPlay`, `StopPlay`.
- Focused shortcuts: `StrataEditor/src/UI/EditorActions.cpp`, `HandleSelectionShortcuts`; Scene view keys: `ViewportPanel::HandleShortcuts`.
- The guard flag: `EditorContext::SetGameInputActive`, `EditorContext::AcceptsEditShortcuts`.
- Tests: `Editor.UI` and `Editor.Viewport`; command: `viewport.setSettings`.

## Further reading

- The Dear ImGui project's comments on `ImGui::Shortcut` and its routing flags, in its header `imgui.h` (advanced).
