# Brief: `editor/play-mode`

| Field | Value |
| --- | --- |
| Title | Play mode: the running copy |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `editor/deferred-commands`, `editor/undo`, `scripting/script-system` |
| From | editor-core ch. 9 (the running copy, edits while playing, the game shell, scene switches and quitting); home of Play and Simulate; the Game view's drawing is `editor-ui/game-view` |
| Unit | `plan/allocation/editor.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `editor/play-mode` — Play mode: the running copy

**Covers.** The problem: the person wants to try the game inside the editor and come back to the scene exactly as it was;
scripts and physics must not change the edited content, and the game must not move the editor's window, take its cursor
or keep its volume. The approaches, with their costs: duplicate the world in memory (Unreal's play in editor), save and
reload (Unity's play mode), run a separate process (Godot). Strata's choice: a copy of the edited scene runs, commands act
on that running copy while it plays, edits to it are not recorded and are gone after Stop, and the game's requests to its
window are recorded instead of applied. The code in order: `SceneState` (Edit, Play, Simulate with physics only); `Play`
and `StartRuntime` (the copy, the world's pins named and linked, a session counter, simulated input and the game shell
reset, the players' bindings and graphics options loaded, time dilation and interpolation from the specification, the
runtime's start); `Stop` (the copy released in the background, the master volume taken at Play restored, because a
game's volume setting belongs to the game session); `GetActiveScene`; edits
while playing, whose results carry a warning and the running-copy mark while settings changes stay; `play.start {build,
paused}`, whose build is `editor/script-builds`' and whose pause is `editor/stepping`'; the runtime's requests (a quit
stops play; a scene switch loads in the background, swaps once ready and logs `play.sceneSwitched`); what a script's
crash does (`StopOnScriptFault` logs the class, callback and entity, posts an error toast that leads to the Problems
panel and the Console, and stops play; a crash while the scripts start ends play at once; `play.start` then fails until
`script.build` or `script.reload`; `UpdateScriptFaultLocation` logs where it happened once the symbolization job is
done; the crash itself is `scripting/crash-containment`'s); the game shell
(`EditorGameWindow` records window requests, saves go to `<project>/.strata/Saves`, the players' bindings and graphics
options). The Scene view shows the editor camera and the Game view the primary camera. What play mode cannot do: edit
several scenes at once (`scene.loadAdditive` works in play mode only). The rule: edits while playing are not recorded and
`play.stop` discards them, and every result says so. The example plays a copy of a sample, changes a light while playing,
reads the warning, stops, and sees the light as it was. Afterwards the reader can tell for any command whether it acts on
the edited scene or the running copy, and add a game service the shell must stand in for.

**Leaves out.**

- Pausing and stepping → `editor/stepping`
- Building scripts before Play → `editor/script-builds`
- The Game view's resolutions, letterboxing and input focus → `editor-ui/game-view`
- Scene switches in a shipped game → `worlds/runtime`
- The script system's start and its callbacks → `scripting/script-system`
- How a script's crash is contained and symbolized → `scripting/crash-containment`, `scripting/symbolization`
- The play copy of a streamed world → `editor/worlds`
- Play and Simulate as a game maker uses them → `make/play-test-debug`

**Fit.** `fits`: about 4,850 words against L (5,000). Counted again from the sections, with a script's crash during play
(one addition of about 150 words, R31) and the master volume: eight features and three excerpts take the most, beside
one concept, two figures, one rule and one exercise.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-core:347` | concept | home | Play in the editor: the approaches and Strata's running copy |
| `editor-core:216-220` | feature | home | `SceneState`, `Play`, `StartRuntime` and `Stop`, `GetActiveScene`, edits while playing, the runtime's requests |
| `editor-core:223` | feature | home | `play.start {build, paused}` |
| `editor-core:227` | feature | home | The game shell: window requests recorded, saves, the players' bindings and graphics options |
| `editor-core:436` | code | home | `StrataEditor/src/Editor/EditorContext.cpp:1363-1433`: `StartRuntime` and `Stop`, what play mode copies, resets and restores |
| `new:11` | code | home | `StrataEditor/src/Editor/EditorContext.cpp:1435-1553`: `HandleRuntimeRequests`, a quit and a scene switch loaded in the background |
| `new:12` | code | home | `StrataEditor/src/Editor/CommandUtils.cpp:427-455`: `GetRunningCopyWarning`, `FinishEdit` and `RollBackEdit`, the running-copy warning |
| `new:56` | code | home | `StrataEditor/src/Editor/EditorContext.cpp:2644-2695`: `StopOnScriptFault` and `UpdateScriptFaultLocation`, what a script's crash during play does (the log line, the toast with Show Problems and the Console, `Stop`, the location once symbolized); with `:1340-1355` (`Play` refused while the module's crash stands, and a crash while the scripts start). The one addition of about 150 words on a script's crash during play (R31) |
| `audio-input:97` | feature | home | The editor keeps the master volume at Play and restores it at Stop: a game's volume setting belongs to the game session; beside `editor-core:216-220`, as passed by `audio-input` |
| `editor-core:494` | figure | home | The play mode state machine |
| `editor-core:528` | figure | home | The Scene view and the Game view side by side while playing |
| `editor-core:573` | rule | home | Edits while playing are not recorded and are discarded by `play.stop`; say so in the result |
| `editor-core:688-690` | term | home | Running copy; edited scene and active scene; Play and Simulate |
| `editor-core:694` | term | home | Game view: one glossary entry with `editor-ui:763`, homed here; the glossary step homes "Scene view" on `editor-ui/scene-view` (R46) |
| `editor-ui:763` | term | home | Game view, the game's view through its primary camera: one entry with `editor-core:694`, as passed by `editor-ui`; "Scene view" and "viewport" of the item are homed on `editor-ui/scene-view`, whose `use` row says so (R46) |
| `editor-core:698` | term | home | Game shell |
| `gamedev:368` | code | home | `StrataEditor/src/Editor/EditorContext.cpp:1363-1433`: the same excerpt as `editor-core:436`, the running copy's start and stop |
| `gamedev:561` | hands-on | home | Exercise: trace `Game::LoadScene` from the SDK to `HandleRuntimeRequests` and the swap |
| `audio-input:654` | term | home | Play mode, Simulate mode |
| `scene-ecs:643` | term | home | Simulate mode |
| `new:13` | not-done | home | Editing several scenes at once: the editor edits one scene and a world's loaded cells, and `scene.loadAdditive` works in play mode only. Evidence: `StrataEditor/src/Editor/EditorSceneCommands.cpp:458-460` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Deferred commands | `editor/deferred-commands` | must |
| `CommitEdit`, `FinishEdit` and the undo stack | `editor/undo` | must |
| `Scene::Copy`, the copy that play runs | `world/systems` | must |
| Sub-scenes, `RequestSceneLoad` and `ReleaseInBackground` | `world/sub-scenes` | must |
| The script system's start | `scripting/script-system` | must |
| A script's crash as the module's guard catches it | `scripting/crash-containment` | helps |
| Scene systems and scene services | `world/systems` | must |
| Engine services a game's host provides | `core/engine-modules` | must |
| Time dilation | `core/time` | helps |
| Drawn transforms and interpolation | `world/interpolation` | helps |
| The camera and the primary camera | `gpu/coordinates` | must |
| Players' bindings | `input/rebinding` | helps |
| Players' graphics options | `image/quality-settings` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `active-scene` | active scene | - |
| `edited-scene` | Edited scene | - |
| `game-shell` | Game shell | - |
| `game-view` | Game view | - |
| `play` | Play | - |
| `play-mode` | Play mode | - |
| `running-copy` | Running copy | - |
| `simulate` | Simulate | - |
| `simulate-mode` | Simulate mode | - |
