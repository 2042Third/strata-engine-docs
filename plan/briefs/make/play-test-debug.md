# Brief: `make/play-test-debug`

| Field | Value |
| --- | --- |
| Title | Playing, testing and debugging |
| Kind | H |
| Size | M |
| Tracks | G, B |
| Needs | `make/hud`, `basics/debugging` |
| From | gamedev "Playing, testing and debugging" (§1.17); a Coin Run script debugged with the debugger that `basics/debugging` attached to the editor (Manual/Scripting "Debugging with a debugger" is that page's); use home of Play and Simulate, pausing and stepping, determinism ("same inputs, same game") and debugging scripts |
| Unit | `plan/allocation/make-a.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `make/play-test-debug` — Playing, testing and debugging

**Covers.** The goal: play Coin Run on purpose, freeze it, step it, change it while it runs, and find a bug in one of
its scripts. What must be true first: Coin Run at the end of `make/hud`, and the debugger that `basics/debugging`
attached to the editor. The steps. (1) **Play** and **Stop** again, with the figure of the running copy: Play runs a
copy of the edited scene and Stop throws the copy away, which is why the coins come back. (2) **Simulate**: physics
without the game's scripts, for trying bodies without playing; the sentence on what else Simulate leaves out (no
sound, no animation, characters in their bind pose) waits for the check of `new:40`. (3) **Pause** and **Step**: Pause
freezes the game; Step runs one fixed update, and the status bar counts the steps; a coin's turn per step read in the
Inspector. (4) Edits while playing: drag the ball in the Scene view and change a script's field; they change the running
copy and are gone at Stop, while a change in Project Settings applies at once and stays. (5) Watch values: the Inspector
shows a script's fields live while the game plays. (6) The editor's feedback and the log: the status bar's pills and the
toasts each lead to the panel that explains (a failed build to Problems, a warning to the Console); `Log::Info`, `Warn`
and `Error` lines in the Console with their file and line, and the editor's log file in the user's data folder; the
exported game writes its own `Game.log`, which `make/export`'s run reads. If you do not see the lines of a run that
crashed: every start empties the program's log file, and every editor of the user writes the same `StrataEditor.log`, so
read or copy the log before starting the editor again. (7) The debugger: a breakpoint in the `Coin` script's
`OnTriggerEnter`, roll into a coin, step and read the call stack, as `basics/debugging` taught; the Linux and macOS tabs
say what the pin does: a Release or Dist editor builds scripts with GCC or Clang without debug information, so the
breakpoint very likely does not bind, and the log and the Inspector stand in; the page says in one sentence that this
was read from the build files, not run (`new:41`, `new:42`). (8) A planted bug in the tutorial's file (the HUD counts a
coin that was destroyed in the same frame) found with the breakpoint and the rule of `make/script-loop` that destruction
happens at the end of the frame, and fixed. (9) "Same inputs, same game": the game counts time in fixed steps and every
body moves the same way for the same steps, so a bug seen after 200 steps is seen again; Pause and Step reproduce it,
and play-tests by command are `make/automated-playtests`'. `## Result`: Coin Run free of the bug, and a way to stop and
look at any moment of a game; it ends with the download of the page's end state. `## Variations`: the debugger of each
system (Visual Studio, VS Code, lldb) in OS tabs; Simulate for tuning physics. What Strata does not do here: no debug
drawing from scripts (`new:9`), no in-game console or console variables (`new:10`), no debug information in the script
modules that a released editor builds with GCC or Clang (`new:42`); the log and the Inspector stand in for them. The
exercises (`new:43`) are done in the editor and in a script.

**Leaves out.**

- The running copy, the game shell and edits while playing inside → `editor/play-mode`
- Pausing and stepping inside; holds counted in fixed steps → `editor/stepping`
- A debugger, breakpoints and the call stack from zero → `basics/debugging`
- Simulated input, command scripts and captures → `make/automated-playtests`
- Measuring the frame → `make/performance`
- Deterministic parallel work inside → `core/jobs`
- The Game view's resolutions and input ownership inside → `editor-ui/game-view`
- The index of everything Strata does not have → `appendix/not-in-strata`

**Fit.** `fits`: about 3,450 words against M (3,000). Nine steps take most of it, with the Linux and macOS tabs of the
debugger, the paragraph on determinism, the figure of the running copy, two pictures, the three absences and two
exercises.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:222` | feature | home | Play, Simulate, Stop, Pause and Step; the toolbar's play color |
| `gamedev:223` | feature | home | Edits while playing go to the running copy; project settings apply live and stay |
| `gamedev:408` | figure | home | The running copy: the edited scene copied at Play, thrown away at Stop |
| `gamedev:596` | term | home | Play, Simulate, Pause, Step |
| `editor-core:611` | hands-on | home | Steps 1 to 3: play, pause, step on Coin Run |
| `editor-ui:692` | hands-on | home | Step 6's feedback: a failed build followed from its pill and toast to Problems, as `make/first-script` first did; the Activity panel's Undo to here and Copy as script are named for `make/with-an-agent` |
| `foundation:542` | hands-on | home | Step 6: the log files, the editor's now and the exported game's `Game.log` with a script's warning after `make/export`; its "If you do not see it": every start empties the log file and every editor of the user writes the same `StrataEditor.log`, so the log of a crashed run is read or copied before the editor starts again. Evidence: `Strata/src/Strata/Core/Log.cpp:224` (the file sink truncates); `StrataEditor/src/EditorApplication.cpp:283-287`; `StrataRuntime/src/RuntimeApplication.cpp:458` (read at the pin) |
| `new:9` | not-done | home | Debug drawing from scripts. Evidence: `git grep -niE "DebugDraw\|DrawLine\|DrawDebug\|Gizmo" 822a7a46 -- StrataScriptCore/Include/StrataScript` finds nothing (run at the pin) |
| `new:40` | open | home | Check: Simulate and skinned meshes. In Simulate the running copy has no scripts, no sound and no Animation system, and the editor's animation preview serves only the edited scene, so skinned characters draw in their bind pose (read from the code, not run; the photographer's capture in the pin's editor settles it, and the page's sentence on Simulate replaces this item). Evidence: `Strata/src/Strata/Scene/SceneSystem.h:23`; `Strata/src/Strata/Animation/AnimationRegistration.cpp:33-35`; `Strata/src/Strata/Scene/Scene.cpp:2114-2115`; `StrataEditor/src/Editor/EditorContext.cpp:2697-2704`; `StrataEditor/src/Editor/EditorContext.h:313`, `:823`; `Strata/src/Strata/Renderer/RenderScene.cpp:1286`, `:1374-1384` |
| `new:41` | open | home | Check: Script breakpoints on Linux and macOS. A breakpoint in a script very likely does not bind on Linux and macOS with a Release or Dist editor, because script modules built with GCC or Clang get no `-g` there (read from the build files, not run; the page is written from the code and says so in one sentence). Evidence: `StrataScriptCore/CMake/StrataScriptModule.cmake:110-133` (a program database for MSVC only); `StrataScriptCore/CMake/StrataScriptCoreConfig.cmake:37-52` (Dist takes Release's flags); `StrataEditor/src/Editor/ScriptBuild.cpp:402` (scripts are built in the editor's own configuration) |
| `new:42` | not-done | home | Debug information in script modules that a Release or Dist editor builds with GCC or Clang: only MSVC builds get it in every configuration, and the editor builds scripts in its own configuration, whose Release and Dist flags hold no `-g`. Evidence: `StrataScriptCore/CMake/StrataScriptModule.cmake:110-133`; `StrataScriptCore/CMake/StrataScriptCoreConfig.cmake:37-52`; `StrataEditor/src/Editor/ScriptBuild.cpp:402` (read at the pin, not run; the check is `new:41`) |
| `new:43` | hands-on | home | Exercises: **Basic.** in Simulate, drop the ball from 3 m and predict whether the coins spin and bob (they do not: Simulate runs no scripts); **Medium.** log the ball's height with `Log::Info` in an `OnFixedUpdate`, Pause, Step ten times, and match the ten new lines of the Console with the steps the status bar counts. Evidence: `Strata/src/Strata/Scene/SceneSystem.h:23` (Simulate: physics only, no scripts or audio); `StrataEditor/src/Editor/Commands/PlayCommands.cpp:191-196` (`play.step`: fixed steps while paused) |
| `new:10` | not-done | home | In-game consoles and console variables. Evidence: `git grep -niE "cvar\|console ?variable\|ConsoleVariable" 822a7a46 -- Strata/src StrataRuntime/src StrataScriptCore` finds nothing (run at the pin) |
| `editor-core:217` | feature | use | Play, the running copy and Stop |
| `editor-core:219` | feature | use | Edits while playing |
| `editor-core:222-224` | feature | use | Pause and step; `play.start` and `play.step` in the command tabs |
| `editor-core:347` | concept | use | Play-in-editor, at the maker's level |
| `editor-core:352` | concept | use | Fixed steps, pausing and stepping, at the maker's level |
| `editor-core:494` | figure | use | The play mode state machine, simplified |
| `editor-core:530` | figure | use | A paused game after steps, with the step count |
| `editor-core:573` | rule | use | Edits while playing are not recorded and go at Stop |
| `editor-core:688` | term | use | Running copy |
| `editor-core:693` | term | use | Stepping |
| `editor-ui:189` | feature | use | Script fields shown live while playing |
| `editor-ui:689` | hands-on | home | Play, the Game view's resolutions, Pause and Step, Shift+F1 and the Game camera (F8), as steps 1 to 4 |
| `scene-ecs:109` | feature | use | Pause and steps, the game's own time base |
| `scene-ecs:643` | term | use | Simulate mode |
| `scripting:124` | feature | use | `Log` |
| `physics:149` | feature | use | Physics gives the same results for the same steps |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| A debugger attached to the editor: breakpoints, stepping, the call stack | `basics/debugging` | must |
| The fixed step and destruction at the end of the frame | `make/script-loop` | must |
| The HUD's count and the `Coin` script's trigger | `make/hud` | must |
| The Console and `Log::Info` | `make/first-script` | must |
| Edits through the Inspector and the gizmo | `make/scenes-entities` | must |

**Starting state.** The end state of `make/hud` (`startsFrom {"tutorial": "make/hud"}`), with the bug of step 8
planted by the tutorial's file in `CoinHud`. The page ends with the bug fixed; `make/export` starts there.

**Command-only steps.** none

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `play` | Play (use) | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-make-a-29 | could | other | `make/play-test-debug` (step 8) | The planted bug, "the HUD counts a coin that was destroyed in the same frame", shows only if `CoinHud` counts after the fixed steps. A frame runs every `OnUpdate`, then the fixed steps (where `OnTriggerEnter` collects and destroys the coin), then `OnLateUpdate`, and destroys at its end; a count in `OnUpdate`, as `make/hud` step 7 writes it, never sees a destroyed coin. | The row says that the tutorial's planted `CoinHud` counts in `OnLateUpdate`, so the breakpoint shows the coin still valid after its `Destroy`, and that the fix counts in `OnUpdate` or skips collected coins (about 40 words). | `allocation/make-a.md:1610-1612`, `:1519-1520`; `Strata/src/Strata/Scene/Scene.cpp:2253-2330`; `StrataScriptCore/Include/StrataScript/Script.h:35`, `:54-59` |
