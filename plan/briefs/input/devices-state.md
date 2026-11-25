# Brief: `input/devices-state`

| Field | Value |
| --- | --- |
| Title | Input devices and per-frame state |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `core/time`, `basics/bytes`, `input/how-input-works` |
| From | audio-input ch. 8; 1.6, 1.7 (codes and names, the GLFW feed, edges, input frames and suspension, the enabled flag, typed text, captures, raw reads) |
| Unit | `plan/allocation/audio-input.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `input/devices-state` — Input devices and per-frame state

**Covers.** The job: `Input` is the engine's static, main-thread state of keyboard, mouse and gamepads as of the
current input frame, fed by the platform; it knows nothing of actions or of the UI. The page's example is Space, the
Third-Person robot's jump, followed from GLFW's callback to a script's `IsKeyPressed`. In this order: codes and names
(`KeyCode` named by the position on a US keyboard, with GLFW's values, never renumbered because compiled scripts embed
them; mouse codes; `InputNames` for commands, bindings and the editor); the map (the input data flow, the Input stage of
the frame, the window seam `InputWindow` that keeps `Input` below the application shell); the contract (main thread,
updated once per frame; Pressed read in `OnUpdate`; input frames suspended while the game does not update). The toy
version is three bitsets and a frame boundary.

The real code, in the order the data flows: `ButtonStates`, whose one `Set` records the edges; the GLFW callbacks, which
feed the state and also send events, with key repeat only as an event, the releases GLFW reports for every held key and
button when the window loses focus (nothing stays down after Alt+Tab), and keys GLFW cannot name, which never reach
`Input`; the Input stage of `Application`'s frame; `BeginFrame`, which clears transitions only once the game has seen
them, stops while suspended, applies the simulated queue at the boundary and counts input frames; the suspension
timeline (`Input::SetSuspended`), with a link to `editor/stepping` for the editor's call that suspends input frames; the
enabled flag (device queries report nothing while the Game view lacks focus, the state keeps tracking, simulated input
still reaches the game); typed text (UTF-8 assembled and checked, at most 1,024 bytes, control characters and surrogates
dropped, malformed text as U+FFFD; `GetTypedText` empty while the keyboard is captured, `GetUncapturedTypedText` for the
text field that holds it); pointer capture and keyboard capture, which the game UI sets, and the raw queries that
binding capture reads, with a table of who sees what; `Reset`; the SDK's `Input` as scripts see it. Then the alternatives
(event queues for gameplay, snapshots per system, raw input APIs), the tests of `InputTests.cpp`, changing it safely
(codes are ABI; platform code stays in `Platform/`) and the exercises (a second window backend, a test of keyboard
capture, a traced tap). At the end the reader
can say what `IsKeyPressed` returns in each frame of a tap, a hold and a paused game, and who sees a key while a text
field is being edited.

**Leaves out.**

- Events, polling and capture as ideas → `input/how-input-works`
- Mouse positions, the viewport and cursor modes → `input/mouse-cursor`
- Gamepad conventions, the gamepad half of the feed and dead zones → `input/gamepads`
- The simulated device and its merge rules → `input/simulated`
- The editor's call that suspends input frames while a paused game has no step (`UpdateInputSuspension`) → `editor/stepping`
- The Game view that sets the enabled flag → `editor-ui/game-view`
- How the game UI uses the captures → `ui/input`
- Editing text in a text field → `ui/text`

**Fit.** `fits`: about 5,500 words against L (5,000). Five excerpts (about 1,250 words), three figures, three rules and
the features of the feed, the suspension, typed text and the captures take the most; the three exercises add about 650.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `audio-input:107-108` | feature | home | `KeyCode` (`c_MaxKeyCode` 512) and the mouse codes with `CursorMode` |
| `audio-input:110` | feature | home | `InputNames`: names, aliases, case-insensitive lookups and name lists |
| `audio-input:116-119` | feature | home | The polling API, the input frame, suspension and the enabled flag |
| `audio-input:121` | feature | home | The window seam `InputWindow` |
| `audio-input:123-128` | feature | home | Typed text, pointer capture, keyboard capture, raw queries, `Reset` and the GLFW feed; in the feed, the releases GLFW reports for every held key and mouse button when the window loses focus, and keys GLFW cannot name (a code below 0), which never reach `Input` (`Strata/vendor/glfw/src/window.c:50-68`; `Strata/src/Platform/GLFW/GLFWWindow.cpp:286-289`) |
| `gameui:195` | feature | home | Typed text as the game UI reads it: `GetTypedText`, `GetUncapturedTypedText` while a text field holds the keyboard, `c_MaxTypedTextBytes` = 1,024 (`Strata/src/Strata/Input/Input.h:88-92, 101-108`); the same feature as `audio-input:123` |
| `audio-input:130` | feature | home | The Input stage: `BeginFrame`, `ProcessEvents`, `InputActions::Update`, before modules and layers |
| `audio-input:173`, `scripting:122` | feature | home | The SDK's `Input` as scripts see it (`StrataScriptCore/Include/StrataScript/Input.h:232-530`), one entry with the scripting inventory's `Input`, passed by `scripting` (R31, D26); its actions and capture are used on `input/actions` and `input/rebinding` |
| `audio-input:376` | code | home | `Strata/src/Strata/Input/Input.cpp:19-41`: `ButtonStates`, three bitsets and the one `Set` that records the edges |
| `audio-input:377` | code | home | `Strata/src/Strata/Input/Input.cpp:553-586`: `BeginFrame`, the transitions cleared once seen, suspension, the simulated queue |
| `audio-input:379` | code | home | `Strata/src/Platform/GLFW/GLFWWindow.cpp:286-319`: the key callback, state and event, repeat only as an event; the gamepad half, `:416-442`, is shown on `input/gamepads` |
| `audio-input:380` | code | home | `Strata/src/Strata/Core/Application.cpp:294-305`: where input sits in the frame |
| `audio-input:382` | code | home | `Strata/src/Strata/Input/Input.cpp:182-281`: UTF-8 encoding and a decoder that refuses overlong forms, surrogates and truncation |
| `audio-input:443` | figure | home | Diagram: the operating system, GLFW's callbacks and joystick polling, `Input::Process*`, the simulated queue, the merged queries and their readers |
| `audio-input:448` | figure | home | Timeline: the editor paused, presses accumulating, the step frame reporting them, the frame index standing still |
| `audio-input:462` | figure | home | Table: gameplay queries, `GetPointerState` and `GetKeyState`, raw queries and actions against the enabled flag and the three captures |
| `audio-input:517` | rule | home | Input is main-thread polling state, updated once per frame: read Pressed and Released in `OnUpdate` |
| `audio-input:523` | rule | home | Suspend input frames while the game does not update |
| `audio-input:535` | rule | home | Key codes are ABI and never renumbered |
| `audio-input:599` | hands-on | home | Exercise: what a second, non-GLFW window backend must translate |
| `audio-input:659-660` | term | home | Input frame; suspended input frames |
| `audio-input:668` | term | home | Surrogate |
| `audio-input:691` | term | home | Pointer capture and keyboard capture |
| `audio-input:440` | figure | use | The frame timeline (home `audio/scene-system`) |
| `audio-input:190` | feature | use | The game UI sets the captures and reads `UIActionState` (home `ui/input`) |
| `audio-input:177` | feature | link | The Game view's focus, which sets the enabled flag (home `editor-ui/game-view`) |
| `audio-input:178` | feature | link | The editor's `UpdateInputSuspension`, which suspends input frames while a paused game has no step to run; the page keeps `Input::SetSuspended` and its timeline (home `editor/stepping`, critic-audio-input-13) |
| `audio-input:667` | term | use | Code point and U+FFFD (home `basics/bytes`) |
| `new:28` | hands-on | home | Exercises (D27): a doctest case beside "Keyboard capture hides keys and typed text from the game, never from the key state" that captures the keyboard, presses W and types "w", and checks what `IsKeyDown`, `GetKeyState`, `GetTypedText` and `GetUncapturedTypedText` report in that input frame and the next, predicted first (predict, then run; a patch: done); trace it yourself: breakpoints in `Input::ProcessKey` and `Input::BeginFrame` while Space is tapped in the Third-Person sample show the callback's call, the edge that `ButtonStates::Set` records and the transition cleared at the next input frame. Evidence: `StrataTests/src/Core/InputTests.cpp:681`; `Strata/src/Strata/Input/Input.h:101-108`; `Strata/src/Strata/Input/Input.cpp:19-41`, `:553-586`, `:638-642` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Polling, events, edges, typed text and capture as ideas | `input/how-input-works` | must |
| Bits, shifts and masks | `basics/numbers` | must |
| Templates, lambdas and `std::bitset` | `basics/cpp-generic` | must |
| Unicode code points and UTF-8's bytes | `basics/bytes` | must |
| The frame loop's stages and `ST_PROFILE_STAGE` | `core/frame-loop` | must |
| The window and its events | `core/windows-events` | must |
| Layers, and a seam that keeps one module below another | `core/layers-registries` | must |
| Static member functions | `basics/programming-2` | helps |
| The main thread and the threading model | `core/jobs` | helps |
| The editor's Game view, which calls `SetEnabled` | `editor-ui/game-view` | helps |
| The script ABI and the SDK | `scripting/abi-sdk` | helps |
| Pausing and stepping a game in the editor | `editor/stepping` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `input-frame` | Input frame | - |
| `pointer-capture` | Pointer capture | keyboard capture |
| `surrogate` | Surrogate | - |
| `suspended-input-frames` | Suspended input frames | - |
