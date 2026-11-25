---
id: editor-ui/immediate-mode
title: "Why immediate mode"
description: "Why Strata's editor draws its panels with Dear ImGui every frame while its games keep retained components, and what that choice costs."
kind: concept
size: M
tracks: [E]
needs: [editor/program, ui/what-game-ui-does]
time: 60
learn:
  - id: two-copies
    text: explain how a retained slider and the value it edits drift apart, and why immediate mode has no second copy
  - id: read-call
    text: explain what a widget call such as ToolbarButton or ToggleChip returns and where its state lives
  - id: why-split
    text: explain why Strata's editor UI is immediate mode while its game UI is retained
  - id: tooling-layer
    text: name the layer that holds Dear ImGui and say why a shipped game links none of it
  - id: limits
    text: name what an immediate-mode UI does badly and choose which tools to build retained
since: 0.3.0
status: final
---

Picture the smallest panel in an editor's user interface (UI): one slider that sets the intensity of a light. You drag the slider and the light in the scene gets brighter. You press Undo and the light gets dimmer again, and the slider must move back with it. Nothing could be smaller, and still it hides the problem this page is about.

Somewhere in the program the light has a number, say 0.5. On screen the slider shows a number too. The question is how many copies of that number exist, and who keeps them equal.

## Two copies of one number drift apart

The usual way to build a UI is to create objects once and keep them. You make a slider object, place it in a panel object, and give it a :term[callback]{id=callback}: a function the slider calls when the person drags it. The slider holds its own value, the light holds another, and the callback copies the first into the second. Libraries that work this way, such as Qt for desktop programs or the tree of a web page, are the retained kind you met on [what game UI does](../ui/what-game-ui-does.md).

Now count the ways the two numbers can differ. The person drags the slider: the callback runs and the light follows. Undo restores the light: nothing tells the slider, and it shows the old value. A script changes the light, a scene loads, or another panel edits the same light: the slider is stale each time. Every one of those events needs code that finds the slider and writes the new value into it.

That code can also go wrong in a second way. If you set the slider's value from the program, the slider may call its callback, which sets the light, which tells the slider again. Programmers add flags such as "ignore this change" to stop the loop. The flags are the sign that two copies are fighting.

A game's menu can live with this, because a menu changes rarely and a designer fixes it once. An editor changes every week. Each new field of each new component needs a slider, a callback, a way to refresh it and a test of all three. The work grows with the number of widgets times the number of ways their data can change.

## The idea: the code describes the interface every frame

Dear ImGui is a C++ library that draws a user interface in the opposite way, and Strata uses it for the editor. You do not create the slider once. Every frame, in the middle of your own code, you call a function that draws it:

```cpp pseudocode
if (Slider("Intensity", &light.Intensity, 0.0f, 10.0f))
	MarkLightChanged();
```

One call does three jobs. It draws the slider at the current place in the panel, using the number it finds at the address you passed. It reads the mouse and, if the person is dragging, writes the new number straight into your variable. It returns `true` in the frames where the person changed something, so your code can react in the same place.

There is no slider object and no copy. The program's own variable is the state, and the slider is a picture of it that the library draws again each frame. When Undo restores the light, the next frame's call draws the restored number, because it reads the variable again. Nothing has to be told.

:::question
The code on this page is C++. If a call such as `Slider(...)`, a `float*` pointer or a lambda looks strange, the pages on [classes and calls](../basics/programming-3.md), [pointers](../basics/cpp-memory.md) and [lambdas](../basics/cpp-generic.md) explain them first.
:::

The library is not stateless, though.

Some facts have to survive from one frame to the next: which widget the mouse pressed, which window is open, where a window was dragged to. Dear ImGui keeps those few facts itself, in a table keyed by an identifier (ID), a number made from the widget's label and the windows around it.
The label "Intensity" in one panel is a different ID from "Intensity" in another. The library remembers that the widget with this ID is being dragged, and nothing more. The value stays yours.

The diagram sets the two designs side by side.

```mermaid caption="In a retained library the widget tree keeps a copy of each value and the program must update both sides. In immediate mode the program's variable is the only copy, and each frame's code produces the draw data again." alt="Two flow charts. The first: the program creates a tree of widgets once; the widgets call back on a change, and the program must write each change into the widgets. The second: each frame the program calls widget functions with its own variables; the library keeps small state by ID and returns draw data that the renderer draws."
flowchart LR
    subgraph Retained
        direction TB
        RP["Program data"] -->|"creates once"| RT["Widget tree with its own values"]
        RT -->|"callback on a change"| RP
        RP -->|"must update on every other change"| RT
        RT --> RD["Draw"]
    end
    subgraph Immediate
        direction TB
        IP["Program data"] -->|"every frame: call a widget function with the variable"| IL["Library with a little state by ID"]
        IL -->|"returns what the person did"| IP
        IL --> ID["Draw data"]
    end
```

In the retained half, the arrow from the program to the tree is the work you must remember. In the immediate half, no such arrow exists, so no one can forget it. The price is in the other arrow: the program calls the library again for every widget in every frame.

Two kinds of graphical user interface (GUI) sort the designs. In a :term[retained-mode GUI]{id=retained-mode-gui} the interface is a tree of objects that stays between frames. In an :term[immediate-mode GUI]{id=immediate-mode-gui} the code describes the interface again each frame and the library keeps only a little state. [What game UI does](../ui/what-game-ui-does.md) compares them for games; this page compares them for tools.

## Worked example: three frames of one drag

Here is the light slider written both ways, in about ten lines each. Before the code, notice two things. The retained slider is an object that copies the light's value once and calls back on a change. The immediate one is a single call that writes into the caller's variable.

```cpp pseudocode
// Retained: built once, kept for the program's life.
Slider slider = CreateSlider(0.0f, 10.0f);
slider.Value = light.Intensity;   // the copy
slider.OnChange = [&light](float value)
	{ light.Intensity = value; };   // the callback

// After an Undo, a script or a scene load:
slider.Value = light.Intensity;   // a step people forget
```

The immediate version is shorter, because it has neither the copy nor the callback.

```cpp pseudocode
// Immediate: runs every frame, inside the panel's code.
if (Slider("Intensity", &light.Intensity, 0.0f, 10.0f))
	MarkLightChanged();                   // react in the same place
```

Three simulated frames drive both. In frames 1 and 2 the person drags to 0.4 and then to 0.7. Before frame 3 an Undo puts the light back to 0.5 and the mouse is idle. Exercise 2 asks you to write and run exactly this.

Follow the numbers by hand. In frame 1 both slider designs receive a drag to 0.4. The retained slider stores 0.4 and calls back, so the light becomes 0.4. The immediate call writes 0.4 into the light's variable directly. The lines agree.

In frame 3 the mouse is idle and Undo has changed the light to 0.5. The retained slider is never told, so it still holds 0.7 while the light holds 0.5: the person sees a slider at 0.7 on a light of 0.5. The immediate slider has no value of its own. It draws the light's 0.5, and the two cannot differ. To fix the retained slider you would add a line that copies the light into the slider after every Undo, and one for every other way the light can change.

:::example[The slider after Undo]
Take the light at 0.7 after two drags, then Undo. The retained design shows 0.7 on the slider and 0.5 on the light: a difference of 0.2 that stays until some code copies one into the other. The immediate design draws 0.5 in the next frame: a difference of 0, with no code written for Undo at all. At 60 :term[frames per second]{id=frame-rate} a frame lasts 16.7 ms, so the person never sees the wrong value for longer than that.
:::

## How engines build tools

Engines and applications have tried several answers. Each repairs a flaw of the one before.

A plain retained library builds the widget tree by hand and updates it through callbacks, as in the first section. It gives rich layout and mature support for people who use screen readers or keyboards alone, but it carries the two-copy problem to every widget.

A retained library with binding reduces that problem. The widget reads its value through a binding or a function, so it asks the data instead of holding a copy. `WPF`, Unreal's Slate and Unity's `UI Toolkit` offer forms of this. The copies shrink, but the tree, the declaration language and the binding rules remain to learn, and a new kind of field still needs its own widget and binding.

An immediate-mode library drops the tree. Dear ImGui is the best known, and Unity's older `IMGUI` system works the same way. The code is the interface, and a new field is one more line. The cost is that the library cannot look ahead through a tree, so its layout is simple and it spends work on every widget in every frame.

| Approach | Code per change | State kept in step | Layout power | Screen readers | Cost per frame | Used by |
| --- | --- | --- | --- | --- | --- | --- |
| Plain retained | A widget, a callback, a refresh | Every value, twice | High | Mature | Only what changed | Qt, web pages |
| Retained with binding | A widget and a binding | Fewer, by binding rules | High | Mature | Only what changed | `WPF`, Slate, `UI Toolkit` |
| Immediate mode | One call | None: the variable | Simple, top to bottom | Weak | Every widget, every frame | Dear ImGui, Unity `IMGUI` |

For a tool that grows by one field a week, the column of code per change decides. For a screen that millions of players must read with a screen reader, the column of screen readers decides, and the answer reverses.

## Strata's choice: Dear ImGui for tools, retained components for games

Strata uses both designs, each where its weakness matters least. The editor and every tool use Dear ImGui. The game's own UI, the menus and the heads-up display (HUD) players see, is retained and made of entities, as [what game UI does](../ui/what-game-ui-does.md) explains.

:::why[Why not one design for both?]
The two have different readers and different change rates. Players need a UI that lives in the scene, saves with it, works with prefabs and scripts, and costs almost nothing when nothing changes. People who make games need panels that follow the engine's features without a week of widget work per feature. Immediate mode gives the second and fails the first, and retained gives the first and slows the second. Strata accepts two designs rather than bend one.
:::

The choice has two consequences in the code. First, Dear ImGui lives in the `ImGui` layer, which the :term[layer table]{id=layer-table} marks as a :term[Tooling layer]{id=tooling-layer}: one that editors and tools contain and shipped games do not. The build links a game with the :term[runtime]{id=runtime} layers only, so an exported game contains no Dear ImGui, and nothing in a game can depend on it. [Layers and registries](../core/layers-registries.md) explains the table.

Second, the editor's UI is a library apart from its core. `StrataEditorCore` holds the project, the scene state, the commands and undo, and has no UI; `StrataEditorUI` draws it with Dear ImGui and links the core. A button therefore runs a command, and the command changes the core. Panels draw state and call commands; they own no copy of the scene that could drift. [The editor is a program](../editor/program.md) shows the split, and the pages on commands show why every change goes through one.

Here is a real piece of that UI. The camera popup in the viewport asks the camera for its :term[field of view]{id=field-of-view}, draws a slider over a :term[local variable]{id=local-variable}, and writes the variable back when the person changed it.

```cpp src="StrataEditor/src/Panels/ViewportPanel.cpp#L385-L396"
float fov = camera.GetFOV();
ImGui::SetNextItemWidth(fieldWidth);
if (ImGui::SliderFloat("Field of view", &fov, 10.0f, 120.0f, "%.0f deg"))
	camera.SetFOV(fov);
float clip[2] = { camera.GetNear(), camera.GetFar() };
ImGui::SetNextItemWidth(fieldWidth);
if (ImGui::DragFloat2("Near / far", clip, 0.1f, EditorCamera::c_MinNear, EditorCamera::c_MaxFar, "%.3g") && !camera.SetClipPlanes(clip[0], clip[1]))
	ST_WARN("The near clip plane must be closer than the far one");
float speed = camera.GetFlySpeed();
ImGui::SetNextItemWidth(fieldWidth);
if (ImGui::DragFloat("Fly speed", &speed, 0.1f, EditorCamera::c_MinFlySpeed, EditorCamera::c_MaxFlySpeed, "%.2f", ImGuiSliderFlags_Logarithmic))
	camera.SetFlySpeed(speed);
```

1. **Line 387:** the call draws the slider, reads the mouse and edits `fov`, all in one `if`.
2. **Line 388:** the body runs only in a frame where the person changed the value, and it writes into the camera, the real state.
3. **Lines 391-392:** a rejected change is reported in place, with no callback to wire up.

Read it as the three jobs again: the call draws, edits `fov` and reports in one step. The camera is the state and the local variable only a carrier for one frame.

Strata's own widget kit follows the same rule. `UI::ToolbarButton` returns `true` only in the frame in which the person clicked it, and `UI::ToggleChip` flips the caller's `bool` and returns `true` then. Neither stores whether the setting is on; the caller does. [Dear ImGui's frames, windows and IDs](imgui.md) are the next page's subject.

## What immediate mode cannot do

The design has real limits, and Strata lives with them in the editor.

- **Accessibility.** A retained tree can tell a screen reader what it contains. Dear ImGui draws pixels and has no such tree, so the editor does not offer that support. This is one reason players' UI is not immediate.
- **Rich layout.** The library places widgets as the code calls them, left to right and top to bottom, with helpers for rows and columns. It cannot solve constraints across a tree, so a layout of the kind a web page engine handles needs work by hand.
- **Layout decided one frame late.** A widget cannot know the size of what comes after it, because the code has not run yet. A window that sizes itself to its content uses the sizes measured in the frame before, and may show one frame of wrong size when its content changes.
- **A cost that grows with what is submitted.** The code runs again each frame, so a panel with 10,000 rows spends time on 10,000 rows unless the code skips the ones out of view. Strata's rule is to draw long lists through `ImGuiListClipper` and never to walk the scene per frame in UI code.

What Strata does not do here is listed in [what Strata does not do](../appendix/not-in-strata.md). The editor, for example, has one main viewport and does not tear panels out into windows of their own; [the shell page](shell.md) says more.

:::example[A cost by hand]
Suppose one widget call costs 2 microseconds and a panel submits 500 widgets. The panel costs 1,000 microseconds, which is 1 ms, or 6 % of a 16.7 ms frame. With 10,000 widgets it costs 20 ms, more than a whole frame, and the editor runs badly. Submitting only the 40 visible rows brings it back to 80 microseconds. The numbers are invented to show the shape: the cost follows what you submit, not what changes.
:::

## Common mistakes

- **Thinking the library stores the value.** The symptom: a field resets to its old value each frame, or edits seem to vanish. The fix: pass the address of a variable that lives longer than one frame, such as a member or the real property. A local copy works only if you write it back when the call returns `true`, as the camera popup does.
- **Waiting for a callback.** The symptom: you search for a place to attach a function to a button and find none. The fix: use the returned `true` and react on the spot, in the same frame, inside the `if`.
- **Forgetting that one call draws and reports.** The symptom: a button drawn twice by calling the function once to draw and again to test it, so two buttons appear, or a widget that is tested but never shown. The fix: call it once and keep the result in a variable.
- **Doing slow work inside the call's `if`.** The symptom: the editor freezes for a second after a click. The fix: the `if` should run a command, and a command that takes long defers its work rather than blocking the frame.
- **Reaching for immediate mode for a player's menu.** The symptom: a menu that cannot be laid out for several screen sizes or read with a screen reader. The fix: build player UI from the retained components.

## Summary

- A retained slider keeps its own copy of the value, so Undo, scripts and other panels leave it stale; immediate mode has no second copy to drift.
- A widget call draws, reads the person's input and returns what they did in one step; the program's variable is the state, and the library keeps only a little, keyed by ID.
- Strata's editor is immediate because tools change weekly and nobody ships them; its game UI is retained because players need a UI in the scene that is cheap, saved and accessible.
- Dear ImGui lives in the Tooling layer `ImGui`, so a shipped game links none of it, and the editor's UI is a library apart from the core, so a button runs a command.
- Immediate mode is weak at screen readers, rich layout and sizing in one frame, and its cost grows with what is submitted; a tool that players use may be better retained.

## Check yourself

1. A retained slider holds the value 0.7 and the light is changed to 0.5 by Undo. Which statement is right?

   - A. The slider calls its callback and moves to 0.5 by itself.
   - B. The slider still shows 0.7 until some code copies the light's value into it.
   - C. The slider is always correct, because the library stores the light.
   - D. Undo cannot change a light that has a slider.

   :::answer{tests="two-copies"}
   B. The slider owns a copy and nothing tells it about Undo. A is wrong: callbacks run on the person's input, not on changes made behind the widget. C describes immediate mode backwards, where the program stores the value. D is wrong, since Undo changes the light itself.
   :::

2. In one frame the person only moves the mouse over a `UI::ToolbarButton` and does not click. What does `UI::ToolbarButton` return, and where does a `UI::ToggleChip` keep whether it is on?

   :::answer{tests="read-call"}
   The call returns `false`, since it returns `true` only in the frame of a click, and hovering is not a click. A `UI::ToggleChip` keeps nothing; it reads and flips the `bool` the caller passed. The program's variable is the state, so two chips that pass the same variable always agree.
   :::

3. Which reason best explains why the editor is immediate and the game UI retained?
   - A. Dear ImGui is faster than every retained library.
   - B. Retained UIs cannot be written in C++.
   - C. Tools change often and nobody ships them, while players need a UI in the scene that costs little when idle and can be read with a screen reader.
   - D. The editor has no commands.

   :::answer{tests="why-split"}
   C. A is wrong: immediate mode pays for every widget every frame. B is wrong: Qt is a C++ library and Strata's own game UI is retained. D is wrong: every editor change goes through a command, which is why panels can be a thin drawing layer.
   :::

4. Why does a game exported from the editor contain no Dear ImGui, and what in the :term[repository]{id=repository} records it?

   :::answer{tests="tooling-layer"}
   Dear ImGui is in the `ImGui` layer, which `StrataTests/Architecture/Layers.json` marks `Tooling`, and the build links games only with the runtime layers. A game contains no code of a Tooling layer, so nothing in it can call ImGui.
   :::

5. A panel lists 20,000 assets, and each row is one widget call. The editor slows to a crawl. Name the cause and one fix.

   :::answer{tests="limits"}
   Immediate mode costs time for every submitted widget in every frame, so 20,000 calls run each frame. The fix is to submit only the visible rows through `ImGuiListClipper`, and to draw from a cached view rebuilt when the data changes, instead of walking the asset folder each frame.
   :::

## Exercises

1. **Basic.** A panel draws `if (UI::ToggleChip("grid", icon, "Grid", &m_ShowGrid, "Show the grid"))`. The person clicks it once. What are the values of `m_ShowGrid` and of the returned `bool` in that frame, and in the next frame if the person does nothing? Where could a second panel read the setting from?

   :::answer[Worked solution]{tests="read-call"}
   Suppose `m_ShowGrid` was `false`. In the click frame the chip flips it to `true` and returns `true`, so the program can react once, for example by marking the view dirty. In the next frame the call draws the chip as on, because it reads `m_ShowGrid`, and returns `false`: nothing was clicked. A second panel reads the same `m_ShowGrid` variable, so it can never disagree with the chip.
   :::

2. **Medium.** Write a complete program with the light slider both ways: a retained slider object with a callback and an immediate function that draws and returns the new value. Drive both with three simulated frames: a drag to 0.4, a drag to 0.7, and an idle frame after Undo sets the light to 0.5. Predict the third line before you run it.

   :::answer[Worked solution]{tests="two-copies" solution="sketches/editor-ui-immediate-mode-slider.cpp"}
   The retained slider is a class with a `Value` and an `OnChange` function. The immediate slider is a function taking the mouse and a pointer to the caller's variable; it writes the variable only while the person drags and returns whether it did. The program makes one `Light` for each design and sets both to 0.5 in frame 3, as Undo would.

   ```cpp sketch="editor-ui-immediate-mode-slider.cpp"
   #include <cstdio>
   #include <functional>

   struct Light
   {
   	float Intensity = 0.5f;
   };

   // What the person does with the mouse in one frame.
   struct Mouse
   {
   	bool Dragging = false;
   	float Position = 0.0f; // Where along the slider the mouse is, from 0 to 1
   };

   // Retained: a long-lived object that keeps its own copy of the value and calls back on a change.
   class RetainedSlider
   {
   public:
   	float Value = 0.0f;
   	std::function<void(float)> OnChange;

   	void Update(const Mouse& mouse)
   	{
   		if (!mouse.Dragging)
   			return;
   		Value = mouse.Position;
   		if (OnChange)
   			OnChange(Value);
   	}
   };

   // Immediate: one function that draws the slider from the caller's variable and reports a change.
   bool Slider(const Mouse& mouse, float* value)
   {
   	if (!mouse.Dragging)
   		return false;
   	*value = mouse.Position;
   	return true;
   }

   int main()
   {
   	const Mouse frames[3] = { { true, 0.4f }, { true, 0.7f }, { false, 0.0f } };

   	Light retainedLight;
   	RetainedSlider retained;
   	retained.Value = retainedLight.Intensity; // The copy is made once, when the slider is built
   	retained.OnChange = [&retainedLight](float value) { retainedLight.Intensity = value; };

   	Light immediateLight;
   	for (int frame = 0; frame < 3; frame++)
   	{
   		if (frame == 2)
   		{
   			// Undo restores the light's old value behind the slider's back.
   			retainedLight.Intensity = 0.5f;
   			immediateLight.Intensity = 0.5f;
   		}
   		retained.Update(frames[frame]);
   		Slider(frames[frame], &immediateLight.Intensity);
   		std::printf("frame %d: retained slider %.2f, light %.2f | immediate slider %.2f, light %.2f\n", frame + 1,
   			retained.Value, retainedLight.Intensity, immediateLight.Intensity, immediateLight.Intensity);
   	}
   	return 0;
   }
   ```

   ```text output-of="editor-ui-immediate-mode-slider.cpp"
   frame 1: retained slider 0.40, light 0.40 | immediate slider 0.40, light 0.40
   frame 2: retained slider 0.70, light 0.70 | immediate slider 0.70, light 0.70
   frame 3: retained slider 0.70, light 0.50 | immediate slider 0.50, light 0.50
   ```

   1. **Lines 20-21:** the retained slider owns a copy of the value and a function to call.
   2. **Lines 25-29:** a drag stores the value and calls back, the only path by which the light follows.
   3. **Lines 36-39:** the immediate slider writes the caller's variable and reports a change.
   4. **Line 48:** the copy is made once, when the retained slider is built.
   5. **Lines 56-58:** Undo changes the light behind the retained slider's back.

   Frames 1 and 2 agree in both designs.

   In frame 3 the retained slider still holds 0.70 while its light is 0.50, a difference of 0.20, because nothing copied the light into it. The immediate side prints 0.50 twice, since it has no copy to go stale. To repair the retained design you add a call that copies the light into the slider after Undo. Another call follows each script that sets the light, so the work grows with the number of ways the light can change.
   :::

3. **Hard.** A team must build three tools: a level editor, a settings screen for players, and a debug :term[overlay]{id=overlay-core} that shows :term[frame times]{id=frame-time}. For each, choose retained or immediate and give the reason in one or two sentences.

   :::answer[Worked solution]{tests="limits,why-split"}
   The level editor is immediate. It changes with every new component and only the team uses it. It must follow the scene's data exactly, so having no second copy of the state is worth more than rich layout.

   The settings screen for players is retained. Players need it to scale to their screen, work with a gamepad and be read by a screen reader. It should live in the game's scene like the rest of the game UI. It also changes rarely, so the cost of copies is small.

   The debug overlay is immediate. It exists for developers and shows numbers that change every frame anyway. In Strata the first and third would use Dear ImGui in a Tooling layer, and the second would use the UI components.
   :::

## Where it lives in Strata

- `Strata/src/Strata/ImGui/ImGuiModule.cpp` and `Strata/src/Strata/ImGui/ImGuiLayer.h`: the :term[engine module]{id=engine-module} that pushes the Dear ImGui layer as the top overlay and draws every layer's UI each frame.
- `StrataTests/Architecture/Layers.json`: the layer table; the `ImGui` layer has `Tooling` set, so games do not contain it.
- `StrataEditor/CMakeLists.txt`: the targets `StrataEditorCore` (no UI) and `StrataEditorUI` (the Dear ImGui interface on top of it).
- `StrataEditor/src/EditorLayer.h`: the editor's layer, whose `OnImGuiRender` draws the panels each frame.
- `StrataEditor/src/UI/Widgets.h`: the widget kit, including `UI::ToolbarButton`, `UI::IconButton` and `UI::ToggleChip`, which return what the person did.
- `StrataEditor/src/Panels/ViewportPanel.cpp`: the camera popup quoted above.

## Further reading

- Dear ImGui's repository and its frequently asked questions (github.com/ocornut/imgui): the library's own account of the immediate-mode style, its limits and its accessibility. Intermediate.
- Casey Muratori's talk "Immediate-Mode Graphical User Interfaces" (2005): the idea that made the style known. Beginner.
- Unity's manual pages on `IMGUI` and `UI Toolkit` (docs.unity3d.com): the same pair, retained and immediate, in one engine. Beginner.
- Qt's and WPF's documentation on signals and data binding: how retained libraries reduce the copy problem. Intermediate.
- Robert Nystrom, Game Programming Patterns (gameprogrammingpatterns.com): the chapter on the game loop and the observer pattern, the pattern behind callbacks. Beginner.
