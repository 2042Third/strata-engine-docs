---
id: input/mouse-cursor
title: "The mouse, the cursor and the game view"
description: "How Strata turns window pixels into the game's own pixels, why mouse look reads deltas, and who may hide or lock the cursor."
kind: internals
size: M
tracks: [E]
needs: [input/devices-state]
time: 50
learn:
  - id: map-pixels
    text: compute a game pixel from a window pixel for a view that shows the game at a different size
  - id: read-delta
    text: explain why mouse look reads the mouse delta and not the position
  - id: cursor-owner
    text: explain when the game's cursor mode reaches the window and when it does not
  - id: trace-mode
    text: trace a script's cursor request down to the window
since: 0.3.0
status: final
---

A mouse gives a game two things: where the pointer is, and how far it moved. This page follows both from the window system to the script. It shows how Strata moves a position into the game's own pixels, why a first-person camera reads movement and not position, and who may hide or lock the cursor. It does not teach mouse buttons, the simulated pointer, user interface hit tests or the Game view's own settings; each has its page, linked where it comes up.

## The problem and how engines solve it

Start with a number. The window system reports the pointer at (520, 300). Pixels of what? You can name at least three answers.

The window system counts pixels of the window, from its top-left corner. In the editor the game does not fill the window: the Game view shows it as a picture inside a panel, and the picture starts at some offset. The game itself renders a fixed number of pixels, say 1920 by 1080, whatever size the picture has on screen.

A script that asks "is the pointer over the button at game pixel (960, 540)?" needs the third kind of pixel. Reading the window's number would be wrong by the offset and by the size ratio.

Engines solve this in one of two ways. Some hand the game the raw window position and leave each game to convert; every game then repeats the arithmetic, and each editor panel breaks it again. Others convert once, at the edge of the input system, so that the game never learns where its picture lies. Strata chooses the second.

A second problem is that a position and a movement are different things. A **mouse delta** is how far the pointer moved since the last frame, in pixels, and it is the difference of two positions. A position says where; a delta says how much. Scrolling follows the same idea: the wheel reports an amount of notches since the last frame, never an absolute place, so Strata reports it as a delta too.

A first-person or third-person camera wants to turn as far as the hand moved. Think of a player who pushes the mouse right until the pointer touches the right edge of the screen. The position stops at the last pixel, because a visible pointer cannot leave the screen. If the camera turned by the position, it would stop turning, although the hand still moves. A delta from a visible pointer is also zero once the pointer sits at the edge.

So engines let a game take the pointer away. The window system then keeps a virtual position without edges and reports only movement, often straight from the mouse without the :term[operating system's]{id=operating-system} pointer acceleration. This is the **cursor mode**: whether the pointer is shown, hidden, or locked to the game, a setting a game may change at any time. A locked cursor is also called a cursor lock. Strata has three modes: Normal, Hidden and Locked.

The costs are real. While the cursor is locked, positions mean nothing: the game must read deltas. A game that locks the cursor and then crashes or loses focus leaves the player without a pointer, so an editor must take the lock back. Both costs shape the rest of the page.

## The map

Three coordinate spaces meet in `Input`. Window pixels come from the window system, which :term[GLFW]{id=glfw} wraps: a library that opens windows and reports the mouse. The **viewport** is the rectangle in which the game's picture lies, given as an origin and a size, both in window pixels. The resolution is the game's own pixel grid. The picture shows that resolution at the viewport's size.

```mermaid caption="A position moves from window pixels to viewport pixels to game pixels; a movement skips the first step." alt="Three boxes in a row: window pixels, viewport pixels and game pixels, with the arrows labeled subtract the origin and multiply by the scale."
flowchart LR
    W["Window pixels<br/>(0, 0) is the window's corner"] -->|"subtract the origin"| V["Viewport pixels<br/>(0, 0) is the picture's corner"]
    V -->|"multiply by resolution / size"| G["Game pixels<br/>what scripts read"]
```

The mapping of a position is one formula, applied to each axis:

$$p_{game} = (p_{window} - o) \cdot \frac{r}{s}$$

Here $p_{window}$ is the pointer position in window pixels, $o$ is the viewport's origin in window pixels, and $s$ is the viewport's size in window pixels. Then $r$ is the resolution in game pixels, and $p_{game}$ is the result in game pixels. Read it as: subtract the origin from the window position, then multiply by the resolution divided by the size. The fraction $r / s$ is the number of game pixels in one window pixel.

Check it with numbers. A 1920 by 1080 game is shown at origin (40, 30) in 960 by 540 window pixels, so $r / s$ is 2 on both axes. The pointer at window (520, 300) is 480 pixels right of and 270 below the picture's corner. Doubled, that is game pixel (960, 540): the exact center of the game.

Now test the limits. The pointer on the picture's corner gives (0, 0) and on the opposite corner (1920, 1080). A pointer outside the picture gives a negative number or one past the resolution; Strata does not clamp.

A delta skips the subtraction: a movement has no origin, so only the scale applies. The next section lists what the callers may count on.

## The contract

Callers of `Input` may assume the following, and must do the rest.

- Mouse positions are in the game's own pixels: Strata removes the viewport's origin and applies the scale, so `GetMousePosition` answers in game pixels in the editor. A shipped game differs, as the section on units shows.
- The game's screen size is `GetViewportSize`: the resolution when one was given, else the viewport's size, else the window's size. A user interface tests hits against this size, so that it matches what is drawn.
- A mouse delta is the movement since the :term[input frame]{id=input-frame} began, scaled like a position. Scroll is a sum of wheel amounts, not scaled.
- A game asks for a cursor mode with `SetGameCursorMode`, which scripts reach as `Input::SetCursorMode`. That wish applies to the window only while the game has the input.
- Code that is not the game, such as the editor's fly camera, uses `SetCursorMode`. It writes to the window at once and leaves the game's wish alone.
- Code that moves, hides or locks the pointer outside these two calls breaks the rules, because the editor could not take the pointer back.

:::why
The game's cursor mode applies only while the game has the input. When the Game view loses focus the game's input is disabled, so the window's cursor returns to Normal; when the game gets the input back, the cursor returns to the game's wish. The reason: a locked pointer must never trap a person in a window that no longer shows the game. See [the devices page](devices-state.md) for the enabled flag.
:::

## A toy version

Before the real code, a small program does the job with plain numbers. It maps one point and one movement, then compares a visible pointer that stops at the edge of an 800 pixel window with a locked one that has none.

:::question
New to C++? Read [the first programming chapter](../basics/programming-1.md), [the second](../basics/programming-2.md) and [the third](../basics/programming-3.md) first; they cover the variables, functions and classes below.
:::

The sketch has three functions: one for a position, one for a delta, and one that clamps. Look at how the position subtracts the origin and the delta does not, and at the printed deltas of the visible pointer.

```cpp sketch="input-mouse-cursor-toy.cpp"
#include <algorithm>
#include <cstdio>

#include <glm/glm.hpp>

// Where the game's picture lies inside the window, and how many pixels the game renders into it.
struct Viewport
{
	glm::vec2 Origin;     // Window pixels of the picture's top-left corner
	glm::vec2 Size;       // The picture's size in window pixels
	glm::vec2 Resolution; // The game's own pixels
};

glm::vec2 ToGamePixels(const glm::vec2& windowPoint, const Viewport& viewport)
{
	const glm::vec2 scale = viewport.Resolution / viewport.Size;
	return (windowPoint - viewport.Origin) * scale;
}

glm::vec2 ToGameDelta(const glm::vec2& windowDelta, const Viewport& viewport)
{
	// A movement has no origin: only the scale applies.
	return windowDelta * (viewport.Resolution / viewport.Size);
}

// A visible cursor cannot leave the window: its position stops at the last pixel.
float MoveVisible(float x, float dx, float windowWidth)
{
	return std::clamp(x + dx, 0.0f, windowWidth - 1.0f);
}

int main()
{
	const Viewport viewport = { { 40.0f, 30.0f }, { 960.0f, 540.0f }, { 1920.0f, 1080.0f } };

	const glm::vec2 point = ToGamePixels({ 520.0f, 300.0f }, viewport);
	std::printf("window (520, 300) is game pixel (%.0f, %.0f)\n", point.x, point.y);

	const glm::vec2 delta = ToGameDelta({ 10.0f, -5.0f }, viewport);
	std::printf("a move of (10, -5) is (%.0f, %.0f) game pixels\n", delta.x, delta.y);

	// The player pushes the mouse right by 20 pixels, three frames in a row, near the edge of an 800 pixel window.
	float visible = 790.0f;
	float virtualPosition = 790.0f;
	for (int frame = 1; frame <= 3; ++frame)
	{
		const float next = MoveVisible(visible, 20.0f, 800.0f);
		const float seenDelta = next - visible;
		visible = next;
		virtualPosition += 20.0f; // A locked cursor has no edge
		std::printf("frame %d: visible position %.0f, its delta %.0f; locked position %.0f, its delta 20\n", frame, visible, seenDelta, virtualPosition);
	}
	return 0;
}
```

```text output-of="input-mouse-cursor-toy.cpp"
window (520, 300) is game pixel (960, 540)
a move of (10, -5) is (20, -10) game pixels
frame 1: visible position 799, its delta 9; locked position 810, its delta 20
frame 2: visible position 799, its delta 0; locked position 830, its delta 20
frame 3: visible position 799, its delta 0; locked position 850, its delta 20
```

1. **Line 17:** the position subtracts the origin, then scales.
2. **Line 23:** the delta only scales.
3. **Line 29:** a visible pointer cannot pass the last pixel of the window.

The first line confirms the hand calculation: window (520, 300) is game pixel (960, 540). The visible pointer reaches its edge in the first frame and reports a delta of 9, then 0 and 0, although the hand keeps pushing. The locked pointer reports 20 every frame. That difference is the reason mouse look reads deltas from a locked cursor.

## The real code

The scale comes first. `GetViewportPixelScale` returns the game pixels per window pixel, and falls back to 1 when no viewport and resolution were given, so a shipped game needs no setup.

```cpp src="Strata/src/Strata/Input/Input.cpp#L137-L145"
// Game pixels per window pixel of the viewport (1 without a resolution of its own).
glm::vec2 GetViewportPixelScale()
{
	const glm::vec2 size = s_State.ViewportSize;
	const glm::vec2 resolution = s_State.ViewportResolution;
	if (!(size.x > 0.0f && size.y > 0.0f && resolution.x > 0.0f && resolution.y > 0.0f))
		return glm::vec2(1.0f);
	return resolution / size;
}
```

Then the two readers. They use the scale; the position also removes the origin. The simulated pointer, which tools and tests use to act as a player, replaces the device position once moved; [the simulated input page](simulated.md) teaches its merge rules.

```cpp src="Strata/src/Strata/Input/Input.cpp#L364-L375"
glm::vec2 Input::GetMousePosition()
{
	if (s_State.Simulated.MousePosition)
		return *s_State.Simulated.MousePosition;
	return (s_State.MousePosition - s_State.ViewportOrigin) * GetViewportPixelScale();
}

glm::vec2 Input::GetMouseDelta()
{
	// Simulated movements are given in the game's pixels already.
	return (s_State.Enabled ? s_State.MouseDelta * GetViewportPixelScale() : glm::vec2(0.0f)) + s_State.Simulated.MouseDelta;
}
```

1. **Lines 366–367:** once a simulated pointer has moved, its position wins; it is in game pixels already.
2. **Line 368:** the window position minus the origin, times the scale.
3. **Line 374:** the delta only scales, and is zero while input is disabled; simulated movement adds to it.

The window delivers positions through `ProcessMouseMove`, which adds the difference of two positions to the frame's delta. The first position of a session makes no delta, because there is nothing to subtract from. `BeginFrame` clears the delta and the scroll once the game has seen them, and `GetMouseDelta` reports zero while input is disabled.

Who sets the viewport? Only the editor's Game view does, in every frame that shows play, whether the view is focused or not.

```cpp src="StrataEditor/src/Panels/GameViewPanel.cpp#L276-L280"
if (shown && context.GetSceneState() == SceneState::Play && m_Image.Size.x > 0.0f && m_Image.Size.y > 0.0f)
{
	const ImVec2 origin = ImGui::GetMainViewport()->Pos;
	Input::SetViewport(glm::vec2(m_Image.Min.x - origin.x, m_Image.Min.y - origin.y), m_Image.Size, glm::vec2(m_RenderSize));
}
```

The origin is the image's corner relative to the main window, the size is the image's size and the resolution is the rendered size. Letterboxing, the resolution modes and the focus rules are the Game view's own, taught in [the Game view page](../editor-ui/game-view.md). The viewport hands them to `Input` only as a rectangle. While a game holds the cursor locked, the editor ignores the mouse in its own panels, and **Shift+F1** frees the cursor from the view.

The fallbacks of `GetViewportSize` follow the contract: resolution, else size, else the window.

```cpp src="Strata/src/Strata/Input/Input.cpp#L542-L551"
glm::vec2 Input::GetViewportSize()
{
	if (s_State.ViewportResolution.x > 0.0f && s_State.ViewportResolution.y > 0.0f)
		return s_State.ViewportResolution;
	if (s_State.ViewportSize.x > 0.0f && s_State.ViewportSize.y > 0.0f)
		return s_State.ViewportSize;
	if (s_State.TargetWindow)
		return glm::vec2(s_State.TargetWindow->GetWidth(), s_State.TargetWindow->GetHeight());
	return glm::vec2(0.0f);
}
```

1. **Line 544:** the resolution wins when the Game view gave one.
2. **Line 546:** otherwise the viewport's size.
3. **Lines 548–549:** otherwise the window's size in screen coordinates; with no window, zero.

### Units in the editor and in an exported game

Only the Game view calls `SetViewport`; a search of the engine finds no other caller. So the unit of a position differs between the two programs. In the editor a position is in the Game view's game pixels.

In an exported game no viewport is set, and a position is what the window system reported: the window's screen coordinates. Meanwhile the scripts' `Game::GetWindowSize` reports the pixels the game renders into, which for a window is its :term[framebuffer]{id=framebuffer} size.
On a display with a :term[content scale]{id=content-scale} above 1, such as a Retina screen, a screen coordinate and a framebuffer pixel differ by that scale.
The Physics Playground's cursor ray divides the position by the framebuffer size, so on a scaled display the two units disagree. This was read in the code, not run.

### The cursor modes

`CursorMode` has three values, and the window maps them to GLFW's modes. Normal is the normal cursor, and Hidden is a cursor that is invisible over the window but free to leave it. Locked is GLFW's disabled cursor. A disabled cursor is hidden and grabbed, and gives a virtual position without limits. The window also asks for raw motion, which is movement without the system's scaling and acceleration, where the platform has it.

```cpp src="Strata/src/Platform/GLFW/GLFWWindow.cpp#L556-L569" symbol="GLFWWindow::SetCursorMode"
void GLFWWindow::SetCursorMode(CursorMode mode)
{
	int glfwMode = GLFW_CURSOR_NORMAL;
	switch (mode)
	{
		case CursorMode::Normal: glfwMode = GLFW_CURSOR_NORMAL; break;
		case CursorMode::Hidden: glfwMode = GLFW_CURSOR_HIDDEN; break;
		case CursorMode::Locked: glfwMode = GLFW_CURSOR_DISABLED; break;
	}
	glfwSetInputMode(m_Window, GLFW_CURSOR, glfwMode);
	if (mode == CursorMode::Locked && glfwRawMouseMotionSupported())
		glfwSetInputMode(m_Window, GLFW_RAW_MOUSE_MOTION, GLFW_TRUE);
	m_CursorMode = mode;
}
```

1. **Lines 561–563:** each mode becomes one of GLFW's.
2. **Lines 566–567:** Locked also asks for raw motion, only where the platform has it.
3. **Line 568:** the window remembers the mode it set.

With Locked, only deltas mean something: the position is virtual, and the game must not use it.

### Who owns the cursor

`SetGameCursorMode` stores the game's wish and applies it only while input is enabled.

```cpp src="Strata/src/Strata/Input/Input.cpp#L530-L535"
void Input::SetGameCursorMode(CursorMode mode)
{
	s_State.GameCursor = mode;
	if (s_State.Enabled)
		ApplyCursorMode(mode);
}
```

`SetEnabled` completes the contract. When the game loses the input, a game that wanted a mode other than Normal sees the window go Normal. When it regains the input, the stored wish applies again.

```cpp src="Strata/src/Strata/Input/Input.cpp#L611-L619"
void Input::SetEnabled(bool enabled)
{
	if (enabled == s_State.Enabled)
		return;
	s_State.Enabled = enabled;
	// The game's cursor applies while the game has the input (see SetGameCursorMode).
	if (s_State.GameCursor != CursorMode::Normal)
		ApplyCursorMode(enabled ? s_State.GameCursor : CursorMode::Normal);
}
```

The editor's `ResetGameShell` sets the game's wish back to Normal when a play session starts and when it stops, so a game that locked the cursor never leaves the lock behind.

:::example
The Third-Person sample's follow camera reads `Input::GetMouseDelta` while the cursor is locked, or while the right button is down. It turns by 0.12 degrees per pixel times the player's sensitivity. A mouse move of (20, -10) game pixels, with sensitivity 1 and no inversion, changes the yaw by -2.4 degrees and the pitch by +1.2 degrees. The same script reads the scroll delta to zoom, 0.75 meters per notch.

Its pause menu calls `Input::SetCursorMode(CursorMode::Normal)` to free the cursor so a player can click, and `CursorMode::Locked` when the game resumes. Set a breakpoint in `Input::SetGameCursorMode` to watch the game's wish; the window follows only while input is enabled.
:::

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Warp the cursor to the window's center each frame and read how far it was from the center | Programs whose window layer offers no locked cursor | Works on any window system, with no special cursor mode | A visible jump of the pointer, lost movement when events queue, no raw motion, and the pointer can leave the window |
| Read the mouse straight from the operating system, beside the window's events | Programs that need every bit of movement | Movement before any system scaling, and several mice | Code for each operating system, and a second path to keep in step with the window's focus rules |
| Give the game window positions and let each game convert | Programs that leave the mapping to each game | No viewport state in `Input` | Every game repeats the arithmetic and breaks in an editor panel |

Locked already asks the operating system for the two things the first two rows want: a grabbed pointer and, where available, raw motion. GLFW provides both behind one setting, so Strata writes no per-system code.

## How it is tested

The suite `Core.Input` in `StrataTests/src/Core/InputTests.cpp` holds the tests. Run the suite with `build/windows/bin/Debug/StrataTests.exe --test-suite=Core.Input`. Three cases cover this page.

- `Mouse position, deltas and viewport offset` checks that the first position makes no delta, that a viewport offset moves the position, and that the next frame clears deltas and scroll.
- `A viewport with a resolution of its own reports the mouse in the game's pixels` uses the viewport of the worked example above, checks that a move of (10, -5) window pixels becomes (20, -10), and checks `GetViewportSize` with and without a resolution.
- `The game's cursor mode applies to the window only while the game has the input` uses a test window that records the modes it receives, so no real window is needed.

## Changing it safely

Extension points are few: a new cursor mode needs a value in `CursorMode`, a mapping in the GLFW window, and a matching value in the script interface, which a `static_assert` in `Strata/src/Strata/Scripting/ScriptHostAPI.cpp` keeps equal. New window systems implement `InputWindow`, whose `SetCursorMode` is all `Input` needs.

Keep these rules. Never write the window's cursor from game code, only through `SetGameCursorMode`; the reason is the contract above. Never read positions while the cursor is locked. Keep the unit of a position the game's pixels wherever a viewport exists, because user interface hit tests take their screen from `GetViewportSize`. Add a test beside the three above for each change, and run `Core.Input` before the others.

## Summary

- A position moves from window pixels to game pixels by subtracting the viewport's origin and multiplying by the resolution over the size; a delta only scales.
- A mouse look reads deltas, because a visible position stops at the screen's edge and a locked one means nothing.
- The game's cursor mode applies to the window only while the game has the input, and resets when a play session starts or stops.
- A script's cursor request goes through the host to `SetGameCursorMode`, then to the window, which asks GLFW for the matching mode.

## Check yourself

1. A viewport has origin (100, 40), size (640, 480) and no resolution of its own. The pointer is at window (110, 45). What does `GetMousePosition` return?

   :::answer{tests="map-pixels"}
   (10, 5). Without a resolution the scale is 1, so only the origin is removed: 110 minus 100 and 45 minus 40. The same numbers appear in the test `Mouse position, deltas and viewport offset`.
   :::

2. A camera script turns by `GetMousePosition` minus the last frame's position, with the cursor in Normal mode. What goes wrong when the player pushes the mouse right at the screen's edge? (a) The camera turns too far. (b) The camera stops turning. (c) The camera turns the other way.

   :::answer{tests="read-delta"}
   (b). A visible pointer stops at the last pixel, so the difference of positions is zero while the hand still moves. (a) is wrong because nothing adds movement; (c) is wrong because the position never decreases. Locked has no edge and reports a delta every frame.
   :::

3. The Game view loses focus while a game has its cursor Locked. What is the window's cursor, and what does `GetGameCursorMode` return? Then the view regains focus.

   :::answer{tests="cursor-owner"}
   The window's cursor is Normal, because the game's wish applies only while input is enabled; `GetGameCursorMode` still returns Locked, the stored wish. When the view regains focus, input is enabled and the window locks again, with no call from the game.
   :::

4. Which call does the editor's fly camera use, and why not the game's call? (a) `SetGameCursorMode`, because it is faster. (b) `SetCursorMode`, because it writes the window at once and keeps the game's wish.

:::answer{tests="trace-mode"}
(b). The fly camera is not the game, and the game's wish applies only while input is enabled. (a) is wrong: speed is no reason, and the call would replace what the game asked for.
:::

## Exercises

1. **Basic.** A 1920 by 1080 game is shown at origin (40, 30) in 960 by 540 window pixels. Compute the game pixel of window pixel (520, 300), and the delta in game pixels of a move of (10, -5) window pixels.

   :::answer[Worked solution]{tests="map-pixels"}
   The scale is 1920 / 960 = 2 and 1080 / 540 = 2. The position: (520 - 40, 300 - 30) = (480, 270), doubled to (960, 540). The delta: (10, -5) doubled is (20, -10), with no origin to subtract. The toy sketch prints the same values.
   :::

2. **Medium.** A panel of 1000 by 600 window pixels at (100, 50) shows a 1920 by 1080 game, centered at the largest size that keeps its shape. Compute the picture's rectangle, then the game pixel of window (350, 200) and of window (350, 60). Predict, then run the sketch.

   :::answer[Worked solution]{tests="map-pixels" solution="sketches/input-mouse-cursor-letterbox.cpp"}
   The width gives 1000 / 1920 = 0.521 and the height 600 / 1080 = 0.556; the smaller wins, so the picture is 1000 by 562.5. The bars above and below are 18.75 pixels each, so the origin is (100, 68.75). The point (350, 200) is (250, 131.25) from the corner, times 1.92: (480, 252). The point (350, 60) lies in the top bar: the y is negative, about -16.8.

   ```cpp sketch="input-mouse-cursor-letterbox.cpp"
   #include <algorithm>
   #include <cstdio>

   #include <glm/glm.hpp>

   int main()
   {
   	// A panel of 1000 x 600 window pixels at (100, 50) shows a 1920 x 1080 game.
   	const glm::vec2 panelOrigin = { 100.0f, 50.0f };
   	const glm::vec2 panelSize = { 1000.0f, 600.0f };
   	const glm::vec2 resolution = { 1920.0f, 1080.0f };

   	// Assumption of this exercise: the picture is centered, at the largest size that keeps the game's shape.
   	const float fit = std::min(panelSize.x / resolution.x, panelSize.y / resolution.y);
   	const glm::vec2 size = resolution * fit;
   	const glm::vec2 origin = panelOrigin + (panelSize - size) * 0.5f;
   	std::printf("picture origin (%.2f, %.2f), size (%.2f, %.2f)\n", origin.x, origin.y, size.x, size.y);

   	const glm::vec2 clicks[] = { { 350.0f, 200.0f }, { 350.0f, 60.0f } };
   	for (const glm::vec2& click : clicks)
   	{
   		const glm::vec2 game = (click - origin) * (resolution / size);
   		std::printf("window (%.0f, %.0f) is game pixel (%.2f, %.2f)\n", click.x, click.y, game.x, game.y);
   	}
   	return 0;
   }
   ```

   ```text output-of="input-mouse-cursor-letterbox.cpp"
   picture origin (100.00, 68.75), size (1000.00, 562.50)
   window (350, 200) is game pixel (480.00, 252.00)
   window (350, 60) is game pixel (480.00, -16.80)
   ```

   1. **Line 14:** the smaller of the two ratios keeps the game's shape.
   2. **Line 16:** the spare space is split into two equal bars.
   3. **Line 22:** the same mapping as the formula, with the picture's rectangle.
   :::

3. **Hard.** Trace it yourself: find where a script's `Input::SetCursorMode` call becomes a change of the window's cursor. Place a breakpoint, or search the engine, and name the files and functions on the way. Then pause the Third-Person sample's game and see what the breakpoint shows.

:::answer[Worked solution]{tests="trace-mode"}
The script calls the host function `HostSetCursorMode` in `Strata/src/Strata/Scripting/ScriptHostAPI.cpp`, which reports a value past Locked as a problem and otherwise calls `Input::SetGameCursorMode` in `Strata/src/Strata/Input/Input.cpp`. That stores the wish and, while input is enabled, calls `ApplyCursorMode`, which calls the window's `SetCursorMode` in `Strata/src/Platform/GLFW/GLFWWindow.cpp`. When the pause menu opens, `GameCursor` becomes Normal and the window follows; when it closes, both become Locked.
:::

## Where it lives in Strata

- `Strata/src/Strata/Input/Input.cpp`: `GetMousePosition`, `GetMouseDelta`, `SetViewport`, `GetViewportSize`, `SetCursorMode`, `SetGameCursorMode`, `SetEnabled`.
- `Strata/src/Strata/Input/MouseCodes.h`: `CursorMode`.
- `Strata/src/Platform/GLFW/GLFWWindow.cpp`: the mapping to GLFW's modes.
- `StrataEditor/src/Panels/GameViewPanel.cpp`: the call of `SetViewport`.
- `StrataTests/src/Core/InputTests.cpp`: the suite `Core.Input`.
- `Samples/ThirdPerson/Scripts/FollowCamera.cpp` and `PauseMenu.cpp`: the example.

## Further reading

- The GLFW documentation, input guide, on cursor modes and raw mouse motion (intermediate).
- Robert Nystrom, Game Programming Patterns, chapter "Game Loop" (beginner): why a game reads input once per frame.
