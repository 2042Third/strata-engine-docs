# Brief: `input/gamepads`

| Field | Value |
| --- | --- |
| Title | Gamepads |
| Kind | I |
| Size | M |
| Tracks | E |
| Needs | `input/devices-state`, `basics/math-vectors` |
| From | audio-input ch. 10 (mapping databases, conventions, axial and radial dead zones, hysteresis, several pads) |
| Unit | `plan/allocation/audio-input.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `input/gamepads` — Gamepads

**Covers.** The job: how Strata reads gamepads: the mapping database that turns hundreds of controller models into one
layout, the conventions of its axes, and the dead zones and hysteresis that turn noisy sticks into steady movement. The
page's example is the Third-Person robot walking with the left stick, and a stick at rest that reads a small value
instead of 0. In this order: the problem, taught from zero (controllers report buttons and axes in different orders;
sticks never rest at exactly 0); mapping databases (the SDL GameControllerDB that GLFW 3.4 compiles in) and the
Xbox-like layout; the conventions (15 buttons, 6 axes, 4 gamepads; sticks from -1 to 1 with +Y up; triggers from 0 to
1) with their diagram; the polling code that converts GLFW's values every frame (+Y down, triggers from -1 to 1) and
reports a disconnected pad at rest; raw axes in `Input`, without a dead zone. The toy version is a dead zone on one axis.

Then dead zones: axial, per axis, against radial, on the stick's length, and rescaling so that full tilt still reads 1,
with the plots; the real code is the SDK's `GetGamepadAxis` and `GetGamepadStick`, short enough for a game maker to copy.
Then hysteresis for an axis used as a button (on from 0.5, off below 0.35) and its plot; the action code that applies it
per pad is named and linked. The page is the book's home of the word hysteresis, and one sentence names its other use,
the world streamer's keep radius beyond its load radius (`worlds/streamer`). Then several gamepads
(`IsGamepadConnected`; gamepad bindings read every pad), and gamepads read while an exported game is in the background,
as the release notes say. What Strata does not do: force feedback; gamepads assigned to players; controllers missing
from GLFW's database, more than four gamepads and mappings that a game adds. Then the alternatives (SDL's own
controller API, XInput and GameInput, platform HID), the tests and changing it safely (gamepad codes are ABI). At the
end the reader can choose a dead zone for a stick, explain why diagonals snap with an axial one, and say why a stick
resting near a threshold needs two thresholds.

**Leaves out.**

- Actions that read gamepads, and the hysteresis code per pad → `input/actions`
- The world streamer's load and keep radii, the other use of hysteresis → `worlds/streamer`
- The rest of the GLFW feed and the per-frame state → `input/devices-state`
- Vector length and normalizing → `basics/math-vectors`

**Fit.** `over`: about 4,300 words against M (3,000). The concept of dead zones and hysteresis with its three plots
(about 820 words), the conventions and the polling code, one excerpt, three absences and three exercises go past M's
top. Proposed: L (5,000) by S2, whose range holds the estimate.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `audio-input:109` | feature | home | 15 Xbox-layout buttons, 6 axes, 4 gamepads; sticks -1 to 1 with +Y up, triggers 0 to 1; `GetGamepadAxisMinimum` |
| `audio-input:129` | feature | home | Polling after `glfwPollEvents`: `glfwJoystickIsGamepad` and `glfwGetGamepadState`, Y negated, triggers remapped, a disconnected pad at rest |
| `audio-input:321` | concept | home | B4: mapping databases, conventions, axial and radial dead zones, rescaling, hysteresis |
| `audio-input:383` | code | home | `StrataScriptCore/Include/StrataScript/Input.h:326-353`: an axial and a radial dead zone with rescaling |
| `audio-input:451-453` | figure | home | Diagram of the conventions; plots of the axial square and the radial circle with the rescaled response; plot of hysteresis at 0.5 and 0.35 |
| `audio-input:672-677` | term | home | Gamepad mapping; axis, stick and trigger; half axis; dead zone, axial and radial; rescaling; hysteresis |
| `worlds-runtime:524` | term | home | Hysteresis, one glossary entry with `audio-input:677`, passed by `worlds` (R31, D33; R46): different thresholds for turning on and for turning off, so that a value near a threshold does not flicker; the entry names both uses, the gamepad's 0.5 and 0.35 beside the plot `audio-input:453`, and the world streamer's keep radius beyond its load radius (`worlds/streamer` says the word in one sentence and links here) |
| `audio-input:379` | code | use | `Strata/src/Platform/GLFW/GLFWWindow.cpp:416-442`, the gamepad half of the feed (home `input/devices-state`) |
| `audio-input:753` | open | use | Gamepads are read while an exported game is in the background (`Docs/Releases/0.7.0.md:363`) |
| `audio-input:156` | feature | link | The thresholds as actions apply them |
| `audio-input:158` | feature | link | Gamepad bindings read every pad |
| `new:10` | not-done | home | Force feedback: no rumble or haptics; how engines expose them. Evidence: `git grep -niE "rumble\|vibrat\|haptic" 822a7a46 -- Strata/src StrataScriptCore` finds nothing |
| `new:11` | not-done | home | Gamepads assigned to players for local multiplayer: a gamepad binding reads every gamepad, and all players share one set of actions. Evidence: `Docs/DeveloperGuide.md:1460`; `Docs/Releases/0.7.0.md:361-362, 412`; `Docs/Roadmap.md:1707` |
| `new:12` | feature | home | GLFW 3.4 and its built-in mapping database (`src/mappings.h`, the SDL GameControllerDB, about 1,000 lines). Evidence: `Strata/vendor/glfw/include/GLFW/glfw3.h:287-301`; `Strata/vendor/glfw/src/mappings.h` |
| `new:20` | not-done | home | Controllers missing from GLFW's gamepad database, more than four gamepads, and gamepad mappings that a game adds: Strata reads GLFW's joystick slots 1 to 4 only, an unmapped controller reads as not connected and keeps its slot (so the first real pad may be gamepad 1), and nothing calls `glfwUpdateGamepadMappings`; how SDL's hints and Steam Input add mappings. Evidence: `Strata/src/Platform/GLFW/GLFWWindow.cpp:416-442`; `Strata/src/Strata/Input/GamepadCodes.h:42` (`c_MaxGamepads = 4`); `git grep -n glfwUpdateGamepadMappings 822a7a46 -- Strata/src StrataEditor/src StrataRuntime/src StrataScriptCore` finds nothing; `StrataScriptCore/Include/StrataScript/Input.h:301` |
| `new:30` | hands-on | home | Exercises (D27): a sketch with the SDK's dead-zone code that prints the axial and the radial response for a stick at (0.1, 0.1), (0.2, 0) and (0.6, 0.6) with the default dead zone 0.15, each predicted first (predict, then run; a sketch with its output: done); a breakpoint in `GLFWWindow::PollGamepads` with a pad connected shows the Y axes negated and the triggers remapped, and without one the pad reported at rest (trace); two thresholds for a trigger read as a button in a racing game, and what one threshold would do (design). Evidence: `StrataScriptCore/Include/StrataScript/Input.h:236`, `:326-353`; `Strata/src/Platform/GLFW/GLFWWindow.cpp:416-442`; `Strata/src/Strata/Input/InputActions.h:51-52` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Vector length and normalizing | `basics/math-vectors` | must |
| The per-frame state and the GLFW feed | `input/devices-state` | must |
| Static functions with default arguments | `basics/programming-2` | helps |
| Input actions, which apply the same thresholds | `input/actions` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `dead-zone` | Dead zone | - |
| `gamepad-mapping` | Gamepad mapping | - |
| `half-axis` | Half axis | - |
| `hysteresis` | Hysteresis | Hysteresis (stick), Hysteresis (H) |
| `rescaling` | Rescaling | - |
