# Brief: `input/mouse-cursor`

| Field | Value |
| --- | --- |
| Title | The mouse, the cursor and the game view |
| Kind | I |
| Size | M |
| Tracks | E |
| Needs | `input/devices-state` |
| From | audio-input ch. 9 (coordinate spaces, the render resolution, cursor modes in the game and the editor); Shift+F1, which frees a cursor the game locked, is editor code (`StrataEditor/src/Panels/GameViewPanel.cpp`) and `editor-ui/game-view`'s |
| Unit | `plan/allocation/audio-input.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `input/mouse-cursor` — The mouse, the cursor and the game view

**Covers.** The job: where the mouse is in the game's own pixels, how far it moved, and who may hide or lock the cursor.
The page's example is the Third-Person's follow camera, which turns with `GetMouseDelta` while the cursor is locked,
and its pause menu, which frees the cursor. In this order: the problem, taught from zero (window pixels, the game's
viewport inside an editor panel, the game's render resolution; positions against deltas; scroll as a delta; why a
first-person camera needs relative motion, and why positions stop at the screen's edge); the coordinate-mapping diagram
and its formula; the contract (the game's cursor mode applies only while the game has the input). The toy version maps
one point from window to viewport to game pixels.

The real code: `GetMousePosition` and `GetMouseDelta` with the viewport's scale; `SetViewport(origin, size,
resolution)` and the fallbacks of `GetViewportSize` (resolution, else size, else window); the simulated pointer, which
replaces the device's position once moved (named; `input/simulated` teaches it); the cursor modes Normal, Hidden and
Locked as GLFW's modes (Locked is GLFW's disabled cursor: hidden, grabbed, a virtual position without limits, and raw,
unaccelerated motion where the platform has it, so that only deltas mean something while it is locked);
`SetCursorMode`, which the editor's fly camera uses, against `SetGameCursorMode`, the game's wish, applied only while
input is enabled, Normal while it is not and reset when play stops; the units of a position in the editor (the Game
view's game pixels) and in an exported game (the window's screen coordinates, while `Game::GetWindowSize` reports
framebuffer pixels: on a scaled display they differ by the content scale), which the page says was read, not run. The
Game view's resolution modes, its letterboxing and Shift+F1 are named and linked. Then the alternatives, set against
what Locked already does (the pointer lock and raw motion that GLFW asks of the operating system): warping the cursor
back to the center by hand each frame, and a raw input API read beside the window's events; the tests of
`InputTests.cpp` for viewports and cursor modes, and changing it safely. At the end the reader can compute a game pixel
from a window pixel for a letterboxed view, and explain why mouse look reads deltas.

**Leaves out.**

- The Game view's resolution modes, letterboxing, the cursor lock's hint and Shift+F1 → `editor-ui/game-view`
- The editor camera's fly mode → `editor/camera-viewport`
- Mouse buttons and their edges → `input/devices-state`
- The simulated pointer and its merge rules → `input/simulated`
- Hit-testing UI under the pointer → `ui/input`

**Fit.** `fits`: about 3,550 words against M (3,000). The concept of mouse spaces with its figure (about 570 words),
the mapping code with its excerpt and the cursor modes take the most; the three exercises add about 600.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `audio-input:120` | feature | home | `SetViewport(origin, size, resolution)`: positions relative to the viewport, scaled to the rendered resolution; `GetViewportSize` |
| `audio-input:122` | feature | home | `SetCursorMode` against `SetGameCursorMode`; Normal while input is disabled; reset at play stop |
| `new:19` | feature | home | The cursor modes as GLFW's: Normal, Hidden and Locked are `GLFW_CURSOR_NORMAL`, `GLFW_CURSOR_HIDDEN` and `GLFW_CURSOR_DISABLED`, which hides and grabs the cursor and gives virtual, unlimited motion; with Locked the window also turns on raw (unscaled and unaccelerated) motion where `glfwRawMouseMotionSupported` says the platform has it; while locked only deltas mean something, positions do not. Evidence: `Strata/src/Platform/GLFW/GLFWWindow.cpp:555-568`; `Strata/src/Strata/Input/MouseCodes.h:38`; `Strata/vendor/glfw/include/GLFW/glfw3.h:4684-4689`, `:4714-4718` |
| `new:18` | open | home | Check: Mouse units on a scaled display. The claim: only the editor's Game view sets an input viewport, so in the editor a mouse position is in the Game view's game pixels, while in an exported game it is in the window's screen coordinates and `Game::GetWindowSize` reports the framebuffer's pixels; on a scaled display (Retina) the two differ by the content scale, and the Physics Playground's cursor ray divides one by the other. The page states what the code shows and says in one sentence that it was read, not run; the brief is not blocked (R39). Evidence: `git grep -n "Input::SetViewport" 822a7a46 -- Strata/src StrataEditor/src StrataRuntime/src` finds only the definition (`Strata/src/Strata/Input/Input.cpp:631`) and `StrataEditor/src/Panels/GameViewPanel.cpp:279`; `Strata/src/Strata/Core/Window.h:74-75`; `StrataScriptCore/Include/StrataScript/ScriptABI.h:576-577`; `Samples/PhysicsPlayground/Scripts/Playground.cpp:193-204` |
| `audio-input:315` | concept | home | B3: mouse spaces and cursor modes; mouse look with positions, DPI and panel offsets forgotten, a locked cursor left behind |
| `audio-input:381` | code | home | `Strata/src/Strata/Input/Input.cpp:364-375`: window to viewport to game pixels, and the simulated pointer; with the scale, `:137-145` |
| `audio-input:449` | figure | home | Diagram: the window, the panel's image rect (origin, size) and the render resolution, with the formula of `GetMousePosition` |
| `audio-input:537` | rule | home | The game's cursor mode applies only while it has the input |
| `audio-input:669-671` | term | home | Viewport (input), cursor mode, mouse delta |
| `editor-ui:777` | term | home | Cursor lock: the game hiding the cursor and taking its motion, Strata's `CursorMode::Locked` (`Strata/src/Strata/Input/MouseCodes.h:38`); one glossary entry with cursor mode (`audio-input:670`) |
| `audio-input:177` | feature | use | The Game view gives `Input` its rect and resolution, and a locked cursor makes ImGui ignore the mouse (home `editor-ui/game-view`) |
| `audio-input:479` | figure | link | The Game view with a locked cursor and the Shift+F1 hint (home `editor-ui/game-view`) |
| `audio-input:138` | feature | use | The simulated pointer (home `input/simulated`) |
| `audio-input:108` | feature | use | The mouse codes and `CursorMode` (home `input/devices-state`) |
| `new:29` | hands-on | home | Exercises (D27): the game pixel of window pixel (520, 300) for a 1920 by 1080 game shown at origin (40, 30) in 960 by 540 window pixels, by the formula (computation); the same case as a doctest beside "A viewport with a resolution of its own reports the mouse in the game's pixels", with the delta of a move, predicted first (predict, then run; a patch: done); a breakpoint in `Input::SetGameCursorMode` while the Third-Person's pause menu opens and closes shows the game's wish and the mode the window gets (trace). Evidence: `Strata/src/Strata/Input/Input.cpp:137-145`, `:364-375`, `:530-535`; `StrataTests/src/Core/InputTests.cpp:72-90`; `Samples/ThirdPerson/Scripts/PauseMenu.cpp:106`, `:120` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The per-frame state, the enabled flag and the window seam | `input/devices-state` | must |
| 2D vectors, added and scaled per component | `basics/math-vectors` | must |
| The window's size in screen coordinates and in framebuffer pixels, and the content scale | `core/windows-events` | must |
| The Game view, its resolution modes and letterboxing | `editor-ui/game-view` | helps |
| The editor camera's fly mode | `editor/camera-viewport` | helps |
| Play mode | `editor/play-mode` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `cursor-mode` | Cursor mode | Cursor lock |
| `mouse-delta` | Mouse delta | - |
| `viewport-input` | Viewport (input) | - |
