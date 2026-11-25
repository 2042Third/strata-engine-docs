# Brief: `input/actions`

| Field | Value |
| --- | --- |
| Title | Input actions |
| Kind | I |
| Size | XL |
| Tracks | E |
| Needs | `input/mouse-cursor`, `input/gamepads`, `world/projects-settings` |
| From | audio-input ch. 11; 1.9 (the model, the grammar, the section, compilation, evaluation, map enables, live edits, UI actions and menu repeat, performance); home of UI actions and menu key repeat |
| Unit | `plan/allocation/audio-input.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `input/actions` — Input actions

**Covers.** The job: `InputActionSet` is the project's definition of the game's actions (the settings section
`Input.Actions`), and `InputActions` evaluates them once per input frame from the devices, the players' bindings, the
map enables and simulated holds; the game UI reads its six actions through `UIActionState`. The page's example is the
Third-Person's `Gameplay` map (Move as a Vector2 from `2D:Key/W,Key/S,Key/A,Key/D` and `Gamepad/LeftStick`; Look,
Jump, Run, Pause, Wave, Dance and Respawn) and the reserved `UI` map that its menus navigate with. In this order: the
problem and how engines solve it, in one paragraph that links `input/how-input-works`; the map (the model as a class
diagram and its compiled form as arrays of indices); the contract (gameplay reads rebindable controls as actions; a map
disabled while an action is held releases it once; an edit keeps the state of unchanged actions). Then the model with the
Project Settings page as its picture (maps, actions, the kinds Button, Axis and Vector2, the limits, the dead zone);
names (`<Map>/<Action>` or an unambiguous bare name, and an ambiguity refused with every match named); the binding
grammar as a data type with the rule of which kind takes which binding; the hand-written parser of `1D:` and `2D:`
composites with its error messages; the reserved `UI` map (`UI/Submit`, `UI/Cancel` and the four directions) and its
default bindings, as the code gives them, whose stick bindings are half axes and so hold with the hysteresis of every
button action, not values of their own; the settings section, its schema and its registration. The toy version evaluates one Button and one Vector2 from a list of bindings.

The real code: compiling the set into flat arrays while the state of each action is carried across by its lower-case
qualified name, so a live edit presses nothing again; `Update` and `Evaluate` (only when an input frame started;
bindings combined by kind; composites normalized, so a diagonal of two keys has length 1; the radial dead zone, rescaled
by the length in `ApplyDeadZone` as the SDK's `GetGamepadStick` does; Pressed and Released derived; a disabled map
releasing); a half axis read per gamepad with hysteresis; a whole axis taken from the gamepad pushed furthest, and the
Apple Clang 17 miscompile that shaped that code; map enables from the next input frame; fast reads (`FindIndex`,
`GetStateAt`, `GetStateVersion`) and the perf test `Perf.Input.Actions256`, whose numbers come from the generated table;
simulated actions; the UI actions and menu key repeat (0.4 s, then every 0.1 s of unscaled time, at most one repeat per
update, idle updates skipped by version) with its timeline, which the game UI's edit keys share; that this repeat is
the engine's, of the six rebindable UI actions, and another mechanism than the SDK's `KeyRepeat`, which a script runs in
its own module on one key (0.25 s, then every 0.05 s by default; `make/timers-events`), so the page says which is
which; how scripts reach input
across the ABI: first the device functions (keys and mouse in the initial set, gamepads and the cursor, typed text
through the text buffer, and `SetCursorMode`, which records the game's wish through `Input::SetGameCursorMode`), then the
ten action functions and three capture functions appended to the ABI, names and bindings passed as text, misuse reported
once; the editor's `inputActions.*` commands.
One sentence dates the actions to 0.6.0. Then what Strata does not do (modifiers, chords, processors and interactions;
mouse motion and scroll are no action sources), the alternatives, the tests of `InputActionsTests.cpp` and changing it
safely. Exercises: a mouse-wheel binding control, modifiers as a design, profiling the actions, and an evaluation of
Move traced in a debugger. At the end the reader
can write bindings in the grammar, predict an action's state in each frame of a press, a map disable and a live edit, and
explain why evaluation runs on compiled arrays.

**Leaves out.**

- Actions instead of keys as an idea, and the engines' action systems → `input/how-input-works`
- Dead zones and hysteresis as ideas → `input/gamepads`
- The players' bindings file and binding capture → `input/rebinding`
- The simulated device and its merge rules → `input/simulated`
- The Input Actions page's drawing (chips, popups, the capture countdown) → `editor-ui/settings-windows`
- UI navigation, which reads the UI actions → `ui/input`
- The SDK's `KeyRepeat` helper for scripts → `make/timers-events`
- Settings sections, versions and validation in general → `world/projects-settings`

**Fit.** `fits`: about 7,550 words against XL (8,000). Eight excerpts (two items share the grammar's; about 2,000
words) and twenty-three features with the internals sections take the most; the four exercises add about 800.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `audio-input:148-161` | feature | home | The model and its limits, the grammar, kind fitting, names, the reserved `UI` map, the section `Input.Actions`, evaluation, combining bindings, thresholds and hysteresis, the radial dead zone, several gamepads, map enables, live edits, fast reads |
| `audio-input:164` | feature | home | Simulated actions: `SimulateAction` from the next input frame whatever the bindings, `ReleaseAllSimulated`, `ClearSimulated` |
| `audio-input:166-167` | feature | home | `UIActionState` (down, pressed, repeated); `Perf.Input.Actions256`, its measurement and budget read from `StrataTests/Perf/Budgets.json:218`, never typed |
| `audio-input:175-176` | feature | home | The input functions of the ABI and their host functions: the device functions (keys and mouse in the initial set, `StrataScriptCore/Include/StrataScript/ScriptABI.h:389-398`; gamepads and the cursor; typed text through the text buffer; `SetCursorMode`, whose host function records the game's wish through `Input::SetGameCursorMode`, `Strata/src/Strata/Scripting/ScriptHostAPI.cpp:1142-1156`), then the appended action and capture functions |
| `audio-input:180` | feature | home | `inputActions.setMap` and `inputActions.setAction` (Edit, one project undo step) and `inputActions.resetPlayerBindings` (Session) |
| `audio-input:183` | feature | home | The Third-Person's `Gameplay` map and its UI actions in menus, as the running example |
| `audio-input:347` | concept | home | B8: compiled once, evaluated once per input frame, state kept across rebuilds by a stable key, versions for cached indices |
| `audio-input:384` | code | home | `Strata/src/Strata/Input/InputActionSet.h:63-95`: the binding grammar as a data type; with `FitsKind`, `Strata/src/Strata/Input/InputActionSet.cpp:488-501` |
| `audio-input:385` | code | home | `Strata/src/Strata/Input/InputActionSet.cpp:414-472`: the parser of controls and composites, with precise errors |
| `audio-input:386` | code | home | `Strata/src/Strata/Input/InputActions.cpp:452-558`: `Evaluate`, the heart of the area |
| `audio-input:387` | code | home | `Strata/src/Strata/Input/InputActions.cpp:341-381`: a button-like control read for a Button, half axes with hysteresis per gamepad |
| `audio-input:388` | code | home | `Strata/src/Strata/Input/InputActions.cpp:405-420`: a whole axis from the gamepad pushed furthest, and why the comment names a compiler's version |
| `audio-input:389` | code | home | `Strata/src/Strata/Input/InputActions.cpp:115-239`: `Compile`, flat arrays and state carried across by the qualified name |
| `audio-input:391` | code | home | `Strata/src/Strata/Input/UIActions.cpp:39-87`: menu key repeat and idle updates skipped by version |
| `gamedev:369` | code | home | `Strata/src/Strata/Input/InputActionSet.h:63-95`: the same excerpt as `audio-input:384`, the binding grammar and the kinds (the router's L61-96 starts two lines early and ends one late) |
| `gamedev:370` | code | home | `Strata/src/Strata/Input/InputActions.cpp:441-450`: `ApplyDeadZone`, the radial dead zone rescaled by the length; the 2D composite normalized so that diagonals have length 1 (the router's L513-531) is shown inside the excerpt of `audio-input:386` |
| `gameui:185` | feature | home | The game UI's view of the `UI` map: `UI/Submit`, `UI/Cancel`, `UI/Up`, `UI/Down`, `UI/Left`, `UI/Right`, repeat after 0.4 s then every 0.1 s of unscaled time, an idle update costing a comparison (`Strata/src/Strata/Input/UIActions.h:11-64`); the same features as `audio-input:152` and `audio-input:166` |
| `gameui:471` | figure | home | Timeline of menu key repeat: the press at 0 s, repeats at 0.4, 0.5 and 0.6 s, at most one an update; the game UI's edit keys repeat on the same constants (`Strata/src/Strata/GameUI/GameUISystem.cpp:591-609`, taught on `ui/text`) |
| `gameui:737` | open | home | Settled at the pin: the `UI` map's stick bindings are half axes (`Gamepad/LeftY+` and the others, `Strata/src/Strata/Input/InputActionSet.cpp:149-152`), so they hold with every button action's hysteresis, on from 0.5 and off below 0.35 (`Strata/src/Strata/Input/InputActions.h:43, 51-52`); the map has no values of its own |
| `audio-input:454` | figure | home | Class diagram of `InputActionSet`, `InputActionMap`, `InputAction` and `InputBinding`, and the compiled form (`ActionRecord[]`, `CompiledBinding[]`, `InputControl[]`, `HalfAxisHeld[]`) |
| `audio-input:456` | figure | home | Flowchart of evaluation per kind: the dead zone, hysteresis, the simulated override, Pressed and Released |
| `audio-input:474` | figure | home | Screenshot: Project Settings > Input Actions in the Third-Person project, with the `UI` map and the `Gameplay` map's actions, kinds, dead zones and binding chips |
| `audio-input:525` | rule | home | Gameplay reads rebindable controls as input actions; devices only for what nobody rebinds (mouse look, text, debug keys) |
| `audio-input:529-531` | rule | home | Disabling a map releases its held actions once; an edit of the actions keeps the state of unchanged actions |
| `audio-input:591-593` | hands-on | home | Exercises: a mouse-wheel half-axis control end to end; modifiers and chords as a design |
| `audio-input:597` | hands-on | home | Exercise: run `Perf.Input.Actions256` in Release and explain the flat arrays and `GetStateVersion` |
| `audio-input:678-684` | term | home | Input action, action kind, binding, composite (1D and 2D), action map, qualified name and bare name, UI map |
| `audio-input:339` | concept | use | Actions instead of keys (home `input/how-input-works`) |
| `audio-input:365` | concept | use | Crossing the script ABI with names and bindings as text (home `scripting/host-api`) |
| `audio-input:543` | rule | use | A misspelled action is reported once and reads as up (home `scripting/host-api`) |
| `audio-input:162` | feature | link | The players' bindings (home `input/rebinding`) |
| `new:13` | not-done | home | Action modifiers, chords, processors and interactions; mouse motion and scroll as action sources (they stay on the raw API); how Unity and Unreal provide them. Evidence: `Docs/DeveloperGuide.md:1464-1465`; `Docs/Releases/0.7.0.md:361-362, 412`; `Strata/src/Strata/Input/InputActionSet.cpp:102` refuses every binding but `Key/`, `Mouse/<button>` (`:48-58`), `Gamepad/`, `1D:` and `2D:` |
| `new:14` | erratum | home | The comment above `UIAction` gives the UI's default bindings as Enter, Escape and the arrows with the gamepad's A, B, d-pad and left stick; the code also binds Submit to keypad Enter and Space. The page gives the code's list. Evidence: `Strata/src/Strata/Input/UIActions.h:11-13`; `Strata/src/Strata/Input/InputActionSet.cpp:146-153`; `StrataScriptCore/Include/StrataScript/UI.h:16-18` |
| `new:15` | feature | home | The release history in one sentence: input actions with rebinding arrived in 0.6.0 (`appendix/history` has the rest). Evidence: `Docs/Releases/0.6.0.md:94-100` |
| `new:31` | hands-on | home | Trace it yourself (D27): a breakpoint in `Evaluate` while the Third-Person's Move is held with W and D shows the 2D composite normalized to length 1, and, with a gamepad, the radial dead zone of `Gamepad/LeftStick` applied by `ApplyDeadZone`. Evidence: `Strata/src/Strata/Input/InputActions.cpp:452-558`, `:441-450` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Actions instead of keys, intents and the engines' action systems | `input/how-input-works` | must |
| The per-frame state, input frames, suspension and captures | `input/devices-state` | must |
| Dead zones, half axes and hysteresis | `input/gamepads` | must |
| Settings sections, `IProjectSettings`, versions and validation | `world/projects-settings` | must |
| JSON objects and arrays | `basics/data-formats` | must |
| `std::optional` and `std::string_view` | `basics/cpp-modern` | must |
| Hash maps | `basics/data-structures` | must |
| Unscaled time | `core/time` | must |
| Writing a parser by hand | `basics/data-formats` | helps |
| The script ABI and why functions are appended | `scripting/abi-sdk` | helps |
| Host functions and `ReportProblem` | `scripting/host-api` | helps |
| Editor commands and their kinds | `editor/commands` | helps |
| Undo steps of the project's settings | `editor/undo` | helps |
| Perf tests and budgets | `engineering/perf-lab` | helps |
| Differences between compilers | `engineering/flags-portability` | helps |
| UI navigation | `ui/input` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `action-map` | Action map | - |
| `bare-name` | bare name | - |
| `composite` | Composite | - |
| `input-action` | Input action | - |
| `qualified-name` | Qualified name | - |
| `ui-map` | UI map | UI actions |
