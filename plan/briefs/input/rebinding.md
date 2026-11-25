# Brief: `input/rebinding`

| Field | Value |
| --- | --- |
| Title | Players' bindings inside the engine: the bindings file and capture |
| Kind | I |
| Size | M |
| Tracks | E |
| Needs | `input/actions` |
| From | audio-input ch. 12 (the code side) and 1.9 (players' bindings, binding capture in `InputActions`); the rebinding screen and binding capture's use side are `make/menus`' |
| Unit | `plan/allocation/audio-input.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `input/rebinding` — Players' bindings inside the engine: the bindings file and capture

**Covers.** The job: the engine's side of players' bindings and of "press a key to bind": the replacements a player
makes, the bindings file in the game's save directory, the session that resets them, and the one binding capture that
the editor's Input Actions page and a game's rebinding menu share. The page's example is a player of the Third-Person
game who rebinds Jump from Space to a gamepad button and finds it again in the next session. In this order: the
problem, taught from zero (the press that is captured must trigger nothing and must not click the button that started
the capture; capture must work while the game is paused; several owners share one listener); the map (the players'
bindings from the project's section and `InputBindings.json` into `Compile`; Save, Load and Delete; the editor's
`.strata/Saves` and a shipped game's user data folder) and the capture's state machine; the contract (only
`InputActions` touches the bindings file; a capture's press triggers nothing). The toy version compares the raw state
with the state at the capture's start.

The real code: the players' bindings (`SetBindings` validated, an empty list unbinding; `ResetBindings`;
`GetPlayerBindings`; `SaveBindings`, written atomically; `LoadBindings`, at most 64 KiB and forgiving per entry;
`ReadSavedBindings`; `DeleteSavedBindings`) and the file's header; sessions (`ResetSession` at play start and stop; the
editor and `GameRuntime` load the bindings when a game starts); binding capture (the first control going down from the
raw state, in device order, half axes with hysteresis, every action up while it listens, the captured control
suppressed for actions until released, numbered captures that are taken or cancelled only by their owner); a script
owns only the capture it started; the editor's "In play" markers and Reset Player Bindings, which show what the next
session starts with. Then what Strata does not do (key names that follow the player's keyboard layout: a game shows a
key by its US position), the alternatives (a capture per owner, a capture inside a UI widget), the capture tests of
`InputActionsTests.cpp` and changing it safely. At the end the reader can say where a player's binding is stored and
when it applies, and why the key that was captured does not also close the menu.

**Leaves out.**

- The rebinding screen a game builds, and capture as a game maker uses it → `make/menus`
- The Input Actions page, its chips and the capture's countdown → `editor-ui/settings-windows`
- Where a shipped game's save directory is → `worlds/game-identity`
- Atomic writes in general → `core/files`
- The grammar of a binding's text → `input/actions`

**Fit.** `fits`: about 3,950 words against M (3,000). The concept of "press a key to bind", the players' bindings and
binding capture with its excerpt (about 1,000 words) take the most; the estimate stands about 50 words below M's top.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `audio-input:162-163` | feature | home | The players' bindings and their file (header `{"Strata": {"Format": "InputBindings", "Version": 1}}`); sessions and `ResetSession` (`StrataEditor/src/Editor/EditorContext.cpp:1395, 1633-1641`) |
| `audio-input:165` | feature | home | Binding capture: `BeginCapture`, the raw state, suppression, `GetCaptureId`, `TakeCapturedBinding`, `CancelCapture`, `GetCapturedControl` |
| `audio-input:352` | concept | home | B9: "press a key to bind" |
| `audio-input:390` | code | home | `Strata/src/Strata/Input/InputActions.cpp:596-667`: edges against the raw state at the start, device order, half axes with hysteresis, suppression |
| `audio-input:458` | figure | home | State machine: idle, listening (every action up), captured (the text waiting), taken; suppression until release; replaced by another owner; cancelled |
| `audio-input:460` | figure | home | Data flow: the project's section and `InputBindings.json` into `Compile`; Save, Load and Delete; the editor's `.strata/Saves` and the runtime's user data folder |
| `audio-input:478` | figure | home | Screenshot: the "In play" markers and Reset Player Bindings after a play session saved bindings |
| `audio-input:527` | rule | home | Only `InputActions` touches the players' bindings file |
| `audio-input:533` | rule | home | A capture's press triggers nothing |
| `audio-input:685-687` | term | home | Players' bindings, binding capture, suppression (capture) |
| `editor-ui:782`, `scripting:566` | term | home | Binding capture, as the editor's and the scripting glossaries word it; one glossary entry with `audio-input:686` |
| `audio-input:408` | code | use | `Strata/src/Strata/Scripting/ScriptHostAPI.cpp:2961-2991`: a script polls and cancels only the capture it started |
| `audio-input:180` | feature | use | `inputActions.resetPlayerBindings` |
| `audio-input:181` | feature | link | The Input Actions page and `BindingCapture` (home `editor-ui/settings-windows`) |
| `audio-input:477` | figure | link | The capture's listening line with its countdown (home `editor-ui/settings-windows`) |
| `new:21` | not-done | home | Key names that follow the player's keyboard layout: a game shows a key's name by its US position (binding text, a rebinding screen), and only the editor's shortcuts follow the layout, through `Window::GetLayoutKey`; how engines ask the platform for a key's label. Evidence: `Docs/Releases/0.7.0.md:361-362`; `Strata/src/Platform/GLFW/GLFWWindow.cpp:626-651`; `git grep -n GetLayoutKey 822a7a46 -- Strata/src StrataScriptCore` finds only the window's code (`Strata/src/Platform/GLFW/GLFWWindow.cpp:626`, `Strata/src/Platform/GLFW/GLFWWindow.h:48`, `Strata/src/Strata/Core/Window.h:117`) and the ImGui platform's (`Strata/src/Strata/ImGui/ImGuiPlatform.cpp:180`, a comment at `Strata/src/Strata/ImGui/ImGuiPlatform.h:22`) |
| `new:32` | hands-on | home | Exercises (D27): the test "The captured control stays up for actions until it is released" extended so that the key is let go one input frame later, with the frame in which its action can press again predicted first (predict, then run; a patch: done); a breakpoint in `GetBindingsFile` while a play session in the editor saves bindings shows the save directory that `IGameSaves` gives and the file's name (trace); one capture per owner instead of one shared capture, and what breaks when the Input Actions page and a game's menu listen at once (design). Evidence: `StrataTests/src/Core/InputActionsTests.cpp:997`; `Strata/src/Strata/Input/InputActions.cpp:670-681`, `:938-950` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Actions, bindings, the compiled set and `SetBindings` | `input/actions` | must |
| Raw queries and suspended input frames | `input/devices-state` | must |
| Atomic writes of files | `core/files` | must |
| A JSON file with a format header | `basics/data-formats` | must |
| The game's save directory (`IGameSaves`) | `worlds/game-identity` | helps |
| Bounded reads of untrusted files | `assets/robustness` | helps |
| Play sessions in the editor | `editor/play-mode` | helps |
| The editor's Input Actions page and `BindingCapture` | `editor-ui/settings-windows` | helps |
| Host functions | `scripting/host-api` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `binding-capture` | Binding capture | - |
| `players-bindings` | Players' bindings | - |
| `suppression-capture` | Suppression (capture) | - |
