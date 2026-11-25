# Allocation: editor

## `editor/program` — The editor is a program: core, UI and host

**Covers.** The page starts from the problem a reader of `start/first-game` has met: a game needs levels, objects and
settings made by people who do not program, and the tool that makes them is not the game. The naive answer is a debug
menu inside the game, which breaks as soon as content must be saved, undone and shipped without the tool. The idea: an
editor is a separate program that links the same engine, holds the content being made, plays it in place, and is left
out of the exported game. The approaches follow with a table of their costs: in-engine editors that run the game code
(Unity, Unreal, Godot), external content tools with exporters, and data files edited by hand. The second idea is model
and view: UI code that changes state directly (simple, untestable) against a core without UI that the UI only draws and
calls. Strata's choice and its reason: `StrataEditorCore` holds all state and logic in `EditorContext`, `StrataEditorUI`
draws it and reaches the application only through `EditorHost`, so tests and agents drive the same core with no window.
`StrataEditor/CMakeLists.txt` builds the two as static libraries and the executable from one file,
`EditorApplication.cpp`; the editor's ImGui is a Tooling layer, so an exported game links neither ImGui nor the editor
(named here, taught on `editor-ui/immediate-mode`). The page then tours what `EditorContext` holds (project, asset manager, edited scene, running copy, selection, inspection
target, undo stack and the rest), each named in one line with the page that teaches it; the switches of
`EditorContextSpecification` that make tests deterministic; and one editor frame in order (`EditorLayer::OnUpdate`: the
last frame's time, `EditorContext::Update`, the command polls, automation, the command script, the panels), with the rule
that every command poll runs before the views render. It ends with the ways the editor runs: in a window; headless, by
one of two options (`--headless` runs without a window and keeps the graphics device, so captures still work; `--no-gpu`
drops the device and implies `--headless`; the word headless is `core/first-frame`'s and is linked); scripted with
`--commands`; and exit code 3 for a bad argument. The example is the editor of `start/first-game`, seen once as the
person sees it and once as three layers. The exercise runs the editor with a bad argument and reads its exit code, then
follows one frame of `EditorLayer::OnUpdate` with a debugger. Afterwards the reader can name the three layers, say which
one a change belongs in, and follow one editor frame from start to end.

**Leaves out.**

- What a command is and how it runs → `editor/commands`
- How the editor is drawn: host, layer, docking and panels → `editor-ui/shell`
- Why the editor's UI is immediate mode → `editor-ui/immediate-mode`
- Notifications, their model and their drawing → `editor-ui/status`
- The table of every command-line option → `reference/editor`
- Headless as a word, and the application's flag → `core/first-frame`
- The tour of the editor for game makers → `make/editor-tour`

**Fit.** `over`: about 4,050 words against M (3,000). Counted again from the sections, with the exercise (D27) and the
editor's two options of headless: two concepts from zero with the approaches' table, the tour of `EditorContext`, one
excerpt and three figures reach M's top; the next size is L (5,000) (S2).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-core:290` | concept | home | What an editor is and why it is a separate program from the game; the approaches and their costs |
| `editor-core:295` | concept | home | Model and view: a core without UI that the UI only draws and calls |
| `editor-core:39-43` | feature | home | The core/UI split, `EditorContext`, `EditorContextSpecification`, the per-frame update and the frame order |
| `editor-core:44-45` | feature | home | Selection (ordered, with a set and a version) and the inspection target as state of the core |
| `editor-core:48` | feature | home | The ways the editor runs (window, headless, scripted) and exit code 3 on a bad argument; the table is `reference/editor`'s |
| `editor-core:449` | code | home | `StrataEditor/src/EditorLayer.cpp:614-668`: the editor's frame order; the function runs on to line 701 (the last frame and quitting) |
| `editor-core:461` | figure | home | The layer stack: StrataEditor, StrataEditorUI, StrataEditorCore, the engine |
| `editor-core:467` | figure | home | The editor frame timeline, marking that command polls run before the views render |
| `editor-core:511` | figure | home | The whole editor with its panels docked, to name the parts once |
| `editor-core:648-650` | term | home | Editor core (`StrataEditorCore`), `EditorContext`, `EditorHost` |
| `editor-ui:747` | term | home | Editor host (`EditorHost`): what the editor's UI needs from the application; one entry with `editor-core:650`, as passed by `editor-ui` |
| `editor-core:739` | term | use | Headless, one entry of `core/first-frame`; the page states the editor's two options: `--headless` keeps the graphics device, `--no-gpu` drops it and implies `--headless` |
| `new:47` | erratum | home | `plan/inventory/editor-core.md:739` defines headless as running without a window or GPU (`--no-gpu`); these are two options, and the page states both: `--headless` runs without a window and keeps the graphics device, so captures still work; `--no-gpu` runs without a graphics device and implies `--headless` (process.md's table of errata, kind `inventory`). Evidence: `StrataEditor/src/EditorApplication.cpp:70-71`, `:323-324` |
| `new:48` | hands-on | home | Exercise (D27, done): run the editor with an unknown argument and read exit code 3 in the terminal; then, with a breakpoint in `EditorLayer::OnUpdate`, follow one frame of a project and name the line where the command polls run before the panels draw. Evidence: `StrataEditor/src/EditorApplication.cpp:272-281`; `Strata/src/Strata/Core/CommandLineOptions.h:27`; `StrataEditor/src/EditorLayer.cpp:614-668` |
| `editor-ui:284` | concept | home | What an editor is and why it is not the game, as the UI survey states it; one home with `editor-core:290`; the Tooling layers that keep ImGui out of games are named and linked to `editor-ui/immediate-mode` |
| `editor-ui:49` | feature | home | The two libraries and the executable of one file in `StrataEditor/CMakeLists.txt`; one home with `editor-core:39` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The editor as a person uses it to make a first game | `start/first-game` | must |
| What a game engine is; one frame from start to finish | `start/what-an-engine-is` | helps |
| The frame loop of an application | `core/frame-loop` | must |
| Windows, events and application layers | `core/windows-events` | must |
| The layer table, the composition root and no tooling in games | `core/layers-registries` | must |
| Scene systems and the scene's update | `world/systems` | must |
| Static libraries, executables and linking | `basics/build` | helps |
| Console and GUI programs, exit codes | `core/platform` | helps |
| Breakpoints in a debugger attached to the engine | `core/debugging` | helps |

## `editor/commands` — Commands

**Covers.** The problem: a person, an AI agent and a test must make the same edit in the same way, and get the same
answer. The idea is the command pattern: one named operation that takes a JSON object and returns JSON or an error. The
approaches (in-process command objects, scripting APIs, remote calls) come in one paragraph that links forward to the
pages on agents. Strata's choice, "commands are the API": every operation is a command named `<group>.<action>`, with a
description written for agents, a JSON Schema, a kind (Edit, Query, Session) and two flags, in one registry that the UI,
the automation server and command scripts all call. The contract follows in the order a call flows: `EditorCommand` and
`EditorCommandResult` (a value or an error whose kind tells a wrong request from a wrong moment), `Execute` (the journal
entry, the wait for the asset scan, the undo step attributed), the schema check before the handler (unknown and missing
parameters refused; exceptions caught only at the third-party boundary), `CommandArguments` collecting the first
problem, and `CommandUtils` (assets and entities resolved, components applied with the inspector's validation and value
ranges, files written for clients through `ResolveOutputPath`). The rules come with their reasons: every change goes
through a command; invalid input is rejected without side effects; one undo step per successful mutation; component
writes are signalled; commands are written for agents (a description that says what the command does and returns, a
complete schema with property descriptions and `required`, IDs as 16-digit hexadecimal strings, assets by handle or
path, results as JSON objects with camelCase keys, images as `{"Image": {"MimeType", "Data"}}`), because every command
is also an RPC method and an MCP tool whose description and schema are all an agent reads. The smallest complete
mutating command, `entity.rename`, is walked through line by line, with its transaction named and linked to
`editor/undo`. Kinds and flags are decisions a test checks (the kind lists of `CommandJournalTests.cpp`);
`editor.commands` lists the registry; the UI adds two commands of its own; owners add sections to `editor.status`
(status providers; the command itself is `automation/agents`', linked forward). A table maps every command group to what
it is for and the page that teaches it (the `ui` group names `ui/input` beside `make/automated-playtests`). The
`entity.*` row says more, because the clipboard is three commands: `entity.copy` is a Query whose result (entity data
under a format header) feeds `entity.paste`, an Edit that gives the copies new IDs under a parent at an index, points
references between the copies at each other (the remapping is `world/serialization`'s and is linked), makes names unique
and warns about data this build cannot read; `entity.duplicate` puts each copy right after its original, in one undo
step. Last, the reader runs one command from a terminal with `StrataCLI call <command>`, its parameters inline, from a
file (`@file`) or from standard input, which later pages of track E use for steps that have no menu or button. The
example renames the Ground of a `basic3d` project from the terminal, reads the answer, then sends a wrong parameter and
reads the error. The toy is a registry of three commands in 60 lines. The trace exercise follows a call with an unknown
parameter from `Execute` to the line of `CheckParameters` that refuses it. The page never types the number of commands
(`:value`). Afterwards the reader can read any command's registration, call it from a terminal and say why a call was
refused.

**Leaves out.**

- Undo steps, transactions and `FinishEdit` → `editor/undo`
- Commands that answer in a later frame (`Defer`, `MayDefer`, `WaitsForAssets`) → `editor/deferred-commands`
- The activity journal and replays → `editor/journal`
- Every command with its parameters → `reference/commands`
- How a request reaches the registry over the network → `automation/rpc-server`
- StrataCLI's structure and the MCP server → `automation/mcp`
- Adding a command → `editor/tutorial-command`

**Fit.** `over`: about 7,350 words against L (5,000). Counted again from the sections, with the clipboard of the
`entity.*` row, the rule on writing commands for agents and the trace exercise: two concepts, the contract in six
features, six excerpts, six rules, the group table and three hands-on pass L's top; the next size is XL (8,000) (S2).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-core:299` | concept | home | The command pattern and a single API for three clients; schema as contract; error kinds |
| `editor-core:305` | concept | home | Validate first and change nothing on failure; `CommandArguments` keeps the first problem |
| `editor-core:54-60` | feature | home | `EditorCommand`, `EditorCommandResult`, `Execute`, the schema check, `CommandArguments`, `CommandUtils`, kinds as a tested decision |
| `editor-core:62-65` | feature | home | `editor.commands`, the two UI-only commands, value ranges, output paths |
| `editor-core:47` | feature | home | Status providers: sections of `editor.status` that their owners register; the command `editor.status` is homed on `automation/agents` (`automation:148`), and the page's sentence on providers links it forward |
| `editor-core:74`, `editor-core:76-97` | feature | home | The map of every command group: what each is for and the page that teaches it; the `ui` group (`editor-core:93`) names `ui/input` beside `make/automated-playtests` (R44) |
| `editor-core:75` | feature | home | The `entity.*` row of the group map, with the clipboard: `entity.copy`, a Query whose result (entity data under a format header) feeds `entity.paste`, an Edit (new IDs, a parent and an index, references between the copies pointed at the copies, names made unique, warnings for data this build cannot read); `entity.duplicate`, each copy right after its original, one undo step; the remapping is `world/serialization`'s (`scene-ecs:33`), linked. At the pin: `StrataEditor/src/Editor/Commands/EntityCommands.cpp:220-224`, `:288-303`, `:305-345` |
| `editor-core:381` | code | home | `StrataEditor/src/Editor/EditorCommands.h:44-80`: `EditorCommandResult`, value, error, kind and defer in one struct |
| `editor-core:383` | code | home | `StrataEditor/src/Editor/EditorCommands.h:84-113`: `EditorCommand` and `MayDefer`, metadata as decisions |
| `editor-core:385` | code | home | `StrataEditor/src/Editor/Commands/EntityCommands.cpp:514-528`: `entity.rename`, the smallest complete mutating command |
| `editor-core:389` | code | home | `StrataEditor/src/Editor/EditorCommands.cpp:105-151`: `Execute`, the journal, the scan wait, the `MayDefer` assertion, undo attribution |
| `editor-core:391` | code | home | `StrataEditor/src/Editor/EditorCommands.cpp:174-221`: `Run` and `CheckParameters`, the schema as contract |
| `editor-core:463` | figure | home | Three clients, one registry |
| `editor-core:465` | figure | home | The command lifecycle; its deferred branch is drawn here and explained on `editor/deferred-commands` |
| `editor-core:542` | rule | home | Every change goes through a command (or a transaction or `SetPropertyWithUndo` for continuous UI edits) |
| `editor-core:546` | rule | home | Reject invalid input without side effects; one undo step per successful mutation |
| `editor-core:550` | rule | home | Signal component writes (`MarkModified`), shown in `entity.rename` |
| `editor-core:558` | rule | home | Mark every command's kind, its session results, `MayDefer` and `WaitsForAssets`; what each mark is for, with links forward |
| `editor-core:591` | rule | home | Files written for clients go through `ResolveOutputPath` |
| `new:69` | rule | home | Write commands for agents: a description that says what the command does and returns, a complete schema (property descriptions, `required`), IDs as 16-digit hexadecimal strings, assets by handle or path, results as JSON objects with camelCase keys, images as `{"Image": {"MimeType", "Data"}}`; the reason: every registered command is an RPC method and an MCP tool, whose description and `inputSchema` are what an agent reads (about 120 words; `automation/rpc-server`'s rule `automation:613` links it). Evidence: `Docs/DeveloperGuide.md:6281-6289` |
| `editor-core:651-656` | term | home | Command, command registry, JSON Schema, command kind, session results, `InvalidParameters` and `Failed` |
| `new:1` | erratum | home | The inventories count 151, 153 and 154 commands. At the pin `StrataEditorCore` registers 151 (63 Edit, 46 Query, 42 Session) and the UI adds `editor.showPanel` and `editor.showDialog`; the page writes `:value{key="commands.count"}`. Evidence: `StrataTests/src/Editor/CommandJournalTests.cpp:102-164` and `:234`; `StrataEditor/src/EditorLayer.cpp:177`, `:233` |
| `automation:192-193` | feature | use | `StrataCLI call` with parameters inline, `@file` or `-`, and its exit codes, at the level of running one command |
| `automation:155` | feature | home | The command contract as the automation survey states it (`EditorCommand`, `EditorCommandResult`, `CheckParameters`); one home with `editor-core:54-57` |
| `automation:149` | feature | home | `editor.commands`, which lists the registry with each command's kind and flags; one home with `editor-core:62` |
| `editor-ui:780` | term | home | Status provider: a section of `editor.status` that its owner registers; one home with `editor-core:47` |
| `scene-ecs:235` | feature | home | The commands on scenes, entities, components and prefabs, as rows of the group map |
| `gamedev:366` | code | home | `StrataEditor/src/Panels/SceneHierarchyPanel.cpp:129-151`: the Hierarchy's Create menu runs `entity.create`; with `:72-91`, the presets it sends |
| `gamedev:556` | hands-on | home | Exercise: a Hierarchy preset that goes through `entity.create`, which proves that the UI calls commands |
| `new:49` | hands-on | home | Trace it yourself (D27): with a breakpoint in `EditorCommandRegistry::Execute`, call `entity.rename` from a terminal with an unknown parameter, follow the call into `Run`, and name the line of `CheckParameters` that refuses it before the handler runs. Evidence: `StrataEditor/src/Editor/EditorCommands.cpp:105-151`, `:174-221` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The editor core, `EditorContext` and the frame order | `editor/program` | must |
| JSON: objects, arrays, strings, numbers | `basics/data-formats` | must |
| Lambdas and `std::function` | `basics/cpp-generic` | must |
| `std::optional` | `basics/cpp-modern` | helps |
| Errors returned, never thrown; exceptions caught at the call site | `core/conventions` | must |
| Entities and their UUIDs | `world/ecs` | must |
| The transform contract and change signals | `world/scene-graph` | must |
| Reflection: `ComponentInfo`, `PropertyInfo`, ranges | `world/reflection` | must |
| Entities serialized and made again with fresh IDs, references remapped | `world/serialization` | helps |
| A terminal: running a program with arguments, quoting a path | `basics/tools` | must |
| Reading a command's JSON in a book's command tab | `start/how-to-read` | helps |
| Paths that are safe to write (UTF-8 paths, reserved names) | `core/files` | helps |

## `editor/deferred-commands` — Commands that take frames

**Covers.** The problem: some commands cannot answer in the frame that runs them (open a scene, wait two frames, step a
paused game, build the scripts), and a command that blocks freezes the editor for the person and for every agent. The
naive answers are to block, or to start a thread that calls back into the editor's state, which races. The idea, from
zero: never block a frame; take a snapshot on the main thread, do the heavy work on a job, publish the result on the
main thread, and poll instead of calling back. Strata's choice: a handler returns `EditorCommandResult::Defer(poll)`;
`EditorCommandRunner` keeps pending commands in the order they were issued and polls each once per frame from the next
frame; the journal entry stays open until the poll gives a final answer. The rules a poll keeps, each with its reason:
it owns copies of its data (a captured reference dies with the request), allocates nothing per frame
(`FrameTimeRecorder` reserves its storage), and waits by the clock or a condition, never a count of frames. `MayDefer`
declares that a handler may defer: `Execute` asserts it in Debug builds and `editor.batch` refuses such commands up
front. `WaitsForAssets` and the scan wait: while a project's assets scan in the background (the asset scan, linked to
`assets/importing`), the registry itself defers Edit commands and commands marked `WaitsForAssets`, and
`DescribeAssetScanWait` gives the UI its reason. `editor.wait {frames}` is the smallest deferred command; `editor.perf`,
registered beside it, is none: it answers in its own frame from the frames the profiler already recorded
(`core/profiling`). `editor.quit` defers for another reason: it waits for saves in flight (`AfterSaves`, linked forward
to `editor/saving`), refuses unsaved changes unless `force`, and answers before the editor closes and cancels what is
pending. The example runs `editor.wait {frames: 2}` from the terminal and reads its frame times; the toy is a runner of
40 lines that polls lambdas. The exercise adds `editor.waitSeconds`, marks it `MayDefer`, lists it in the test's lists
and checks that `editor.batch` refuses it; the trace exercise counts the polls of `editor.wait {frames: 2}` in the
runner. Afterwards the reader can write a deferred command that cannot crash, stall or allocate in a frame.

**Leaves out.**

- Opening scenes and projects in the background → `editor/projects`
- `play.step`, a deferred command with a stateful poll → `editor/stepping`
- `script.build` and the build `play.start` waits for → `editor/script-builds`
- How the RPC server answers a deferred command → `automation/rpc-server`
- The background asset scan itself (`BeginScan`) → `assets/importing`

**Fit.** `over`: about 5,100 words against M (3,000). Counted again from the sections, with the trace exercise and the
sentence on `editor.perf`: two concepts, four excerpts, the toy, `editor.quit` and three hands-on in the shape of an
internals page pass M's top; the next size is L (5,000) (S2).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-core:322` | concept | home | Never block a frame: snapshot on the main thread, work on a job, publish on the main thread, poll |
| `editor-core:355` | concept | home | Asynchronous commands: `Defer(poll)`, the runner, `MayDefer`, polls that own copies |
| `editor-core:61` | feature | home | Edit and `WaitsForAssets` commands wait for the background asset scan; `DescribeAssetScanWait` |
| `editor-core:236-238` | feature | home | `Defer(poll)`, `EditorCommandRunner`, `FrameTimeRecorder` |
| `editor-core:239` | feature | home | `editor.wait {frames}`, the smallest deferred command (`MayDefer`); `editor.perf`, which is not deferred: a Query with session results that answers in its own frame from the frames the profiler recorded (at most 600), not `MayDefer` and not in the test's list of deferring commands; `core/profiling` uses it. At the pin: `StrataEditor/src/Editor/EditorStateCommands.cpp:883`, `:912-975`; `StrataTests/src/Editor/CommandJournalTests.cpp:175-187` |
| `editor-core:440` | code | home | `StrataEditor/src/Editor/EditorCommandRunner.cpp:274-309`: polling a pending result; with `:337-372`, the runner's update (why it copies the count, why completions issue commands for the next frame) |
| `new:2` | code | home | `StrataEditor/src/Editor/CommandUtils.h:118-145`: `FrameTimeRecorder`, storage reserved so that polls do not allocate |
| `new:3` | code | home | `StrataEditor/src/Editor/EditorCommands.cpp:153-172`: `WaitsForAssetScan` and `DescribeAssetScanWait`, the registry's own deferral and its reason |
| `new:4` | code | home | `StrataEditor/src/Editor/EditorStateCommands.cpp:883-911`: `editor.wait`, the smallest deferred command |
| `editor-core:465` | figure | use | The command lifecycle, its deferred branch |
| `editor-core:575` | rule | home | Commands never block a frame; polls own their data, allocate nothing per frame and wait by the clock |
| `editor-core:628` | hands-on | home | Exercise: a deferred `editor.waitSeconds`, refused by `editor.batch` |
| `new:50` | hands-on | home | Trace it yourself (D27): with breakpoints in `PollCommandResult` and `EditorCommandRunner::Update`, run `editor.wait {frames: 2}` from a terminal, count the polls until the final answer and name the line where the journal entry completes. Evidence: `StrataEditor/src/Editor/EditorCommandRunner.cpp:274-309`, `:337-372` |
| `editor-core:657-661` | term | home | Deferred command, poll function, `MayDefer`, `WaitsForAssets`, command runner |
| `editor-core:740` | term | use | Asset scan, homed on `assets/importing`: the page uses it for the scan wait of Edit and `WaitsForAssets` commands |
| `automation:153` | feature | home | `editor.wait`, one home with `editor-core:239`; `editor.quit`, deferred because it waits for saves in flight, refused with unsaved changes unless `force`, answered before the editor closes |
| `automation:156` | feature | home | Commands wait for the asset scan, as clients see it; one home with `editor-core:61` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Commands, `EditorCommandResult`, `Execute` and the journal entry | `editor/commands` | must |
| The editor's frame order | `editor/program` | must |
| Frame time and waiting by the clock | `core/time` | must |
| Jobs and returning results to the main thread | `core/jobs` | must |
| Lambdas capturing by value and by reference; object lifetimes | `basics/cpp-generic` | must |
| Heap allocation and why it can wait | `basics/cpp-memory` | helps |
| The background asset scan | `assets/importing` | must |

## `editor/undo` — Undo and redo

**Covers.** The problem: every edit, by a person or an agent, must be reversible in one step per action, whether it
touched one value, a hundred entities or a file on disk. Four approaches are compared with a table of their costs:
command objects that write their own inverse, the memento (state before and after), transaction buffers that serialize
the touched objects (Unreal's transactions, Unity's `Undo.RecordObject`), and persistent data structures. Strata's
choice: mementos at the grain of an entity for the scene, and polymorphic `EditorAction`s for files, documents and
settings. The history comes first, on a toy undo stack of integers taken from `UndoStackTests.cpp`: `EditorAction` (an
`Undo` that may fail with a reason and change nothing, `MergeWith`, `IsNoOp`, `ChangesScene`, `GetSceneChange`);
`UndoStack::Push` (the redo branch dropped, continuous edits merged until `BreakMerge`, a merged no-op dropped, the
capacity of 512 trimmed); the different failure rules of undo (the step stays) and redo (it and every later step go);
the save point and the modified flag (only steps that change the scene count, and a trim or a dropped redo branch makes
the save point unreachable); serials and generations; action groups that apply all or nothing, and the open group a
batch uses; the observer that the recovery journal and worlds listen with. Then the scene: why undo recreates entities
with the same UUID; `EntityState`; `SceneEditTransaction` (track before you change, track created entities after you
create them, `TrackSubtree` before you delete; commit only when something changed; rollback); `SceneEditAction` with its
shared, immutable states and its merge rule; `SceneEdit::ApplyEntities`, the central algorithm (one destroy batch, one
recreation with the same UUIDs, component differences, one placement batch per changed sibling list, and why every
recorded entity of a changed list is placed); names in steps ("Create 'Wall'", `QuoteName`, `MakeNameUnique`);
`SceneSettingsAction`. `CommitEdit` is the one gate (refused while playing, rolled back while a scene opens; the
upkeep of worlds and prefabs is named and linked); `FinishEdit` and `RollBackEdit` end a command; `entity.create` and
`entity.delete` show the tracking; `SetPropertyWithUndo` gives the inspector's continuous edits a merge key per entity,
component and property; `AssetDocumentAction` is the example of a step that does not change the scene. `edit.undo`,
`edit.redo` and `edit.history` close the page. The running example: a parent with two children is deleted and undone, and
a dragged value becomes one step. Exercises: run `Editor.Undo` and add a test that a merged drag, a save and another drag
give two steps; write an undo step for an asset rename whose undo checks its precondition; trace the undo of a deleted
parent through the three batches of `ApplyEntities`. Afterwards the reader can add an undo step of either kind and
predict what the history does with it.

**Leaves out.**

- Saves under concurrent edits, `SavePoint` as a background save uses it → `editor/saving`
- How the recovery journal follows the history → `editor/recovery`
- Undo steps of files and the trash → `editor/trash-references`
- Override upkeep inside `CommitEdit` → `editor/prefab-instances`
- Re-celling and cells in undo steps → `editor/worlds`
- The sibling index and the hierarchy's order → `world/scene-graph`
- The gizmo's drag (`TransformDrag`) → `editor-ui/scene-view`
- Undo and redo as a game maker uses them → `make/project-files`

**Fit.** `fits`: about 9,150 words against XL (8,000). Counted again from the sections, with the trace exercise: eleven
excerpts (the toy among them) and eighteen features take the most, beside three concepts, four figures, four rules and
four hands-on.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-core:307` | concept | home | Stable identity: undo, prefabs, replays and recovery recreate entities with the same UUID |
| `editor-core:310` | concept | home | Undo and redo: the four approaches, Strata's choice, merging, groups and failure |
| `editor-core:319` | concept | home | The modified flag as a save point in the history |
| `editor-core:103-106` | feature | home | `EditorAction`, `UndoStack`, the failure rules, the save point and the modified flag |
| `editor-core:108-114` | feature | home | Action groups, groups for batches, the observer, `EntityState`, `SceneEditTransaction`, `SceneEditAction`, `ApplyEntities` |
| `editor-core:116-120` | feature | home | Names in steps, `SceneSettingsAction`, `CommitEdit`, `FinishEdit` and `RollBackEdit`, `PropertyEdit` |
| `editor-core:122` | feature | home | `AssetDocumentAction`: a step that does not change the scene |
| `editor-core:124` | feature | home | `edit.undo`, `edit.redo`, `edit.history` |
| `editor-core:121` | feature | use | `TransformDrag` as an example of a merge key that ends with the drag |
| `editor-core:115` | feature | link | Steps that touch an unloaded world cell; `editor/worlds` has them |
| `editor-core:387` | code | home | `StrataEditor/src/Editor/Commands/EntityCommands.cpp:170-218`: `entity.create` and `entity.delete`, `TrackCreated`, `TrackSubtree`, `RollBackEdit` |
| `editor-core:393` | code | home | `StrataEditor/src/Editor/UndoStack.h:27-56`: `EditorAction`, the undo interface with failure and merge |
| `editor-core:395` | code | home | `StrataEditor/src/Editor/UndoStack.cpp:48-106`: `UndoStack::Push`, the central algorithm of the history |
| `editor-core:397` | code | home | `StrataEditor/src/Editor/UndoStack.cpp:156-221`: `Undo` and `Redo` with their different failure rules |
| `editor-core:398` | code | home | `StrataEditor/src/Editor/UndoStack.cpp:278-311`: `GetSavePoint`, `MarkSaved(point)`, `IsModified` |
| `editor-core:399` | code | home | `StrataTests/src/Editor/UndoStackTests.cpp:14-69`: the toy `AddAction`; with `:262-374`, the tests of merging, no-op drop and save points |
| `editor-core:401` | code | home | `StrataEditor/src/Editor/SceneEdit.h:21-37`: `EntityState`; with `:132-169`, the `SceneEditTransaction` API |
| `editor-core:403` | code | home | `StrataEditor/src/Editor/SceneEdit.cpp:187-281`: `ApplyEntities`, the central algorithm of scene undo |
| `editor-core:406` | code | home | `StrataEditor/src/Editor/SceneEdit.cpp:351-363`: the merge rule; with `:388-463`, the transaction's capture and commit |
| `editor-core:408` | code | home | `StrataEditor/src/Editor/PropertyEdit.cpp:135-155`: `SetPropertyWithUndo`, the inspector's path and its merge key |
| `editor-core:410` | code | home | `StrataEditor/src/Editor/EditorContext.cpp:1875-1891`: `CommitEdit`, the one gate |
| `editor-core:470` | figure | home | The undo stack's state: entries, serials, position, save point, merge flag |
| `editor-core:472` | figure | home | The flow of a `SceneEditTransaction` |
| `editor-core:474` | figure | home | `ApplyEntities` in three batches, on a small hierarchy whose positions agree by chance |
| `editor-core:515` | figure | home | `edit.history` or the Edit menu with named steps |
| `editor-core:548` | rule | home | Track before you change; track created entities after you create them; `TrackSubtree` before deleting |
| `editor-core:552` | rule | home | Give continuous edits a merge key and break the merge when the drag ends |
| `editor-core:554` | rule | home | Undo can fail; design for it |
| `editor-core:556` | rule | home | Steps that do not change the scene say so (`ChangesScene() == false`) |
| `editor-core:623` | hands-on | home | Exercise: read the undo tests and add one for merge and save point |
| `editor-core:631` | hands-on | home | Exercise: a non-scene undo step whose undo checks its precondition |
| `new:51` | hands-on | home | Trace it yourself (D27): delete a parent with two children with `entity.delete`, then run `edit.undo` with a breakpoint in `ApplyEntities`, and name its destroy batch, its recreation with the same UUIDs and its placement batch as they run. Evidence: `StrataEditor/src/Editor/SceneEdit.cpp:187-281`; `StrataEditor/src/Editor/Commands/EntityCommands.cpp:170-218` |
| `editor-core:671-684` | term | home | Undo step, history, redo branch, merge and merge key, no-op step, break the merge, action group, serial, save point, generation, memento, `EntityState`, scene edit transaction, rollback |
| `editor-core:685` | term | link | Sibling index, homed on `world/scene-graph`; the page names it where `ApplyEntities` places a changed sibling list |
| `editor-ui:762` | term | home | Undo merge: a drag's many changes combined into one step; one home with `editor-core:674` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Commands, `Execute` and how a command ends | `editor/commands` | must |
| Entities, components and UUIDs as stable identities | `world/ecs` | must |
| The hierarchy: parents, children, sibling order, changes through `Scene` | `world/scene-graph` | must |
| Components written as JSON; scene documents | `world/serialization` | must |
| Reflection: `ComponentInfo`, `PropertyInfo` | `world/reflection` | must |
| Virtual functions and interfaces | `basics/cpp-classes` | must |
| `unique_ptr` and `shared_ptr`, `Scope` and `Ref` | `basics/cpp-memory` | must |
| `std::deque` and the standard containers | `basics/cpp-generic` | must |
| A doctest test case | `core/first-change` | helps |

## `editor/saving` — Saving without stalling

**Covers.** The problem: in 0.3.0, saving a scene of a million entities froze the editor for 22 seconds on the
development machine (`Docs/Releases/0.4.0.md:60-62`), and a command that replaces the scene can drop edits nobody has
saved. The naive answers are named with their failure: save
on the main thread, set a dirty bit, mark everything saved when the save ends, write the file in place. The first idea,
saving safely: take a snapshot in the frame, serialize it on a job, write it atomically under a claim so that the file
watcher and moves leave it alone, publish the written document on the main thread, and let a newer save of the same
documents replace a queued one. The second idea, no silent data loss: every command that would discard work checks
first, waits for saves in flight, and discards only what it was told to. The code follows that order. `DocumentSaver` is
the one path (snapshot, `SceneDocumentWriter` on a job, reference scan, hash, atomic write under a claim, publish in
`Update`). A scene save runs `BeginSaveScene`, then `SubmitSceneSave` (break the merge, take the save point, copy the
scene's serialized state, take the recovery token), then `OnSceneSaveEnded` (mark that save point saved, the project
picture, the recovery journal; a failed Save As restores the scene's handle and name). `SavePoint` lets edits go on during
a save: what was copied is marked saved, later edits stay unsaved. `scene.save {wait}` and the `saving` section of
`editor.status` show it to clients. `SettingsFileWriter` writes the project file and the preferences the same way, and
`ProjectSettingsAction` makes a settings change an undo step whose file is written in the background. Then the guard:
`CheckUnsavedChanges` with `force`, its action and its `DiscardScope`; `AfterSaves`, a function that wraps a handler so
that `force` never discards a save in flight; `scene.new` as the pattern of guard, `AfterSaves` and `MayDefer` in one
command; `ResetScene`, every scene replacement in its order (the recovery journal first); `ReleaseProject`. What the
design cannot do yet: prefab and asset documents (`prefab.apply`, the Asset tab) are still written in the frame. The
example saves a large world scene with `scene.save {wait: false}`, edits on while the saving pill shows, then tries
`scene.open` without `force` and reads the refusal. Exercises: trace a held background save in a test; remove
`AfterSaves` from `scene.new` on a scratch branch and find the test of `Editor.Saves` or `Editor.DataSafety` that fails.
Afterwards the reader can add a command that replaces the scene without losing a save or an edit.

**Leaves out.**

- How the UI asks the person (modals, the re-ask rule, `DrawDiscardQuestion`) → `editor-ui/shell`
- The recovery journal that `ResetScene` writes first → `editor/recovery`
- Atomic writes, private files and UTF-8 paths → `core/files`
- The streamed scene document → `world/serialization`
- The world's two-step save → `editor/worlds`
- The project file and its settings sections → `world/projects-settings`
- Saving as a game maker does it → `make/project-files`

**Fit.** `fits`: about 5,200 words against L (5,000). Two concepts, five excerpts (the saver's is long), three figures,
three rules and two exercises; the asset manager's document writes take one paragraph.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-core:326` | concept | home | Saving safely: snapshot, job, atomic write, claims, coalescing, publish; save points under concurrent edits |
| `editor-core:330` | concept | home | No silent data loss: guards, `force`, waiting for saves in flight, unwritten settings |
| `editor-core:107` | feature | home | `SavePoint` for background saves: marking the saved step wherever the history moved |
| `editor-core:123` | feature | home | `ProjectSettingsAction`: settings as undo steps whose file is written in the background |
| `editor-core:130-137` | feature | home | `DocumentSaver`, the scene save, `scene.save {wait}`, `SettingsFileWriter`, the guard, `AfterSaves`, `ResetScene`, `ReleaseProject` |
| `editor-core:139` | feature | home | What the design cannot do yet: asset documents are written in the frame |
| `assets:143` | feature | home | The asset manager's native document writes: create, save, reserve, the write claim and its commit, publish |
| `editor-core:804` | open | home | Checked at the pin: `prefab.apply` writes through `AssetEdit::ApplyDocument` (`StrataEditor/src/Editor/EditorPrefabCommands.cpp:570`), which saves in the frame (`StrataEditor/src/Editor/AssetEdit.cpp:95`) |
| `editor-core:414` | code | home | `StrataEditor/src/Editor/CommandUtils.cpp:276-332`: `CheckUnsavedChanges` and `AfterSaves` |
| `editor-core:416` | code | home | `StrataEditor/src/Editor/EditorSceneCommands.cpp:379-406`: `scene.new`, the guard, `AfterSaves` and `MayDefer` together |
| `editor-core:418` | code | home | `StrataEditor/src/Editor/EditorContext.cpp:1045-1103`: `SubmitSceneSave` and `OnSceneSaveEnded` |
| `editor-core:420` | code | home | `StrataEditor/src/Editor/DocumentSaver.cpp:114-211`: the job; with `:218-268` (submit and coalescing) and `:293-343` (collect and publish) |
| `editor-core:423` | code | home | `StrataEditor/src/Editor/EditorContext.cpp:688-717`: `ResetScene`, everything a scene replacement does, in order |
| `editor-core:476` | figure | home | The background save timeline |
| `editor-core:478` | figure | home | The decision tree of the data-loss guard |
| `editor-core:517` | figure | home | The saving pill and the saving dialog while a large scene saves |
| `editor-core:561` | rule | home | Never serialize a document on the main thread for a save |
| `editor-core:563` | rule | home | Take the save point after `BreakMerge` |
| `editor-core:565` | rule | home | Commands that replace the scene, close the project or quit: `CheckUnsavedChanges`, `AfterSaves`, `MayDefer` |
| `editor-core:633` | hands-on | home | Exercise: trace a held background save |
| `editor-core:635` | hands-on | home | Exercise: break the guard and find the failing test |
| `editor-core:701` | term | home | Snapshot (of a save) |
| `editor-core:703-708` | term | home | Document claim, publish, coalescing, unwritten settings, discard scope, `force` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The undo stack, save points and `BreakMerge` | `editor/undo` | must |
| Deferred commands and `MayDefer` | `editor/deferred-commands` | must |
| Atomic writes and files you can trust | `core/files` | must |
| Jobs and returning results to the main thread | `core/jobs` | must |
| Atomics with acquire and release | `basics/threads` | must |
| Streamed scene documents (`SceneDocumentWriter`) | `world/serialization` | must |
| References an asset records | `assets/references` | helps |
| `Scene::Copy` with `SerializedOnly`, the snapshot a save writes | `world/systems` | helps |
| Releasing a scene in the background | `world/sub-scenes` | helps |
| The project file and its settings sections | `world/projects-settings` | must |
| A function that takes and returns a function | `basics/cpp-generic` | must |

## `editor/recovery` — Autosave and crash recovery

**Covers.** The problem: the editor crashes or the power fails an hour after the last save, or an agent forces a scene
open and the person's edits go with the old scene. The approaches, with their costs: periodic full copies of the scene
(common in content tools and engines), journals written ahead of the change (as databases do), and a snapshot plus
changes. Strata's choice and its reason: a journal of entity states since the last save, written against the hash of the
saved file it applies to, folded so that it grows only with structural edits, and written when the editor is quiet; and
"discard" means "kept as recovery data". The page teaches the observer pattern first (the journal follows the undo stack
without copying the scene), then `SceneRecovery` in the order of a session: the journal keeps the states of the steps
since the last save and writes `<project>/.strata/Recovery/<scene>-<session>.strecovery` two seconds after edits stop
and at least every ten seconds, building the text on a worker and writing it on an I/O job; the base hash is a SHA-256
read a megabyte at a time; folding merges every step that creates, removes or moves no entity into the segment before it
(`IsStructural`); a scene never saved is snapshotted whole, and steps of kind Other force a snapshot, both only up to
256 entities, because a snapshot is captured on the main thread: a never-saved scene that starts with more, or a larger
scene after a step of kind Other, is not journaled until it is saved, and `scene.recoveryStatus` says so and asks for
the save; forced discards and Don't Save write the journal marked Discarded, the newest eight are offered and older ones
move to `Recovery/Discarded` (twenty kept); a save in progress passes its token so that edits made during it are carried
into the journal of the saved document; files of a running editor (process id and start time) are left out of offers;
the journal follows a renamed or moved scene by its handle. `scene.recoveryStatus` and `scene.recover {apply, discard,
force}` finish it: apply opens the scene in the background and applies the changes as one undo step back to the saved
state. The rule: only `SceneRecovery` writes recovery files, and every scene replacement goes through `ResetScene`. The
example edits a scene, ends the editor's process, opens the project again and recovers. The exercise writes the segments
a sequence of steps produces on paper, then checks them with an `Editor.Recovery` test; the trace exercise follows one
edit from `OnApplied` to the file the quiet timer writes. Afterwards the reader can say what a crash at any moment
leaves, and change the journal without losing that guarantee.

**Leaves out.**

- The Recover Unsaved Changes dialog → `editor-ui/launcher-dialogs`
- Recovering a world's cells → `editor/worlds`
- Opening the scene in the background → `editor/projects`
- Recovering as a game maker does it → `make/project-files`

**Fit.** `over`: about 4,600 words against M (3,000). Counted again from the sections, with the limit of 256 entities
and the trace exercise: one concept, nine features in the order of a session, the excerpt in three parts and the shape
of an internals page pass M's top; the next size is L (5,000) (S2).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-core:333` | concept | home | Autosave and crash recovery: the approaches, the journal against a base hash, folding, discards kept |
| `editor-core:145-147`, `editor-core:149-153` | feature | home | The journal, the base hash, folding, discards, saves during journaling, ownership, following moves, `scene.recoveryStatus` and `scene.recover` |
| `editor-core:148` | feature | home | Complete journals: a never-saved scene snapshotted whole and steps of kind Other forcing a snapshot, both only up to `c_MaxSnapshotEntities` (256) because a snapshot is captured on the main thread; above it a never-saved scene, or a larger scene after a step of kind Other, is not journaled until it is saved, and the status says so and asks for the save. At the pin: `StrataEditor/src/Editor/SceneRecovery.h:121-126`, `:145`; `StrataEditor/src/Editor/SceneRecovery.cpp:463-468`, `:724-732`, `:1093`; `StrataEditor/src/Editor/EditorStateCommands.cpp:559-566` (`skipped` in `scene.recoveryStatus`) |
| `editor-core:425` | code | home | `StrataEditor/src/Editor/SceneRecovery.cpp:629-688`: `OnApplied` and the quiet timer; with `:61-77` (`IsStructural`) and `:754-767` (folding) |
| `editor-core:481` | figure | home | The recovery journal's file and its life |
| `editor-core:519` | figure | home | The Recover Unsaved Changes dialog after a crash, and the toast after an agent's forced `scene.open` |
| `editor-core:569` | rule | home | Only `SceneRecovery` writes recovery files; every scene replacement goes through `ResetScene` |
| `editor-core:639` | hands-on | home | Exercise: recovery folding on paper, then a test |
| `new:52` | hands-on | home | Trace it yourself (D27): with a breakpoint in `SceneRecovery::OnApplied`, make one edit in a saved scene, wait two seconds, and find the `.strecovery` file under `<project>/.strata/Recovery` that the quiet timer's job wrote. Evidence: `StrataEditor/src/Editor/SceneRecovery.cpp:629-688`, `:867` |
| `editor-core:709-712` | term | home | Recovery journal, base hash, structural step, discarded (recovery) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The undo stack, its observers and `EntityState` | `editor/undo` | must |
| `ResetScene`, background saves and the recovery token | `editor/saving` | must |
| SHA-256 and other hashes | `basics/data-formats` | must |
| I/O jobs | `core/jobs` | must |
| Process ids and their reuse | `core/platform` | helps |
| Opening a scene in the background (`BeginOpenScene`) | `editor/projects` | helps |

## `editor/projects` — Opening projects and scenes: templates, background loads and migration

**Covers.** The problem: a project of tens of thousands of assets, or a start scene of a million entities, must open
without freezing the editor, and opening or closing a project lets go of the edited scene, so it must not lose work. The
naive answers: load everything before the first frame (the window stays empty for minutes), or keep editing the old
scene while the new one loads (the edits vanish at the swap). The idea: open content in the background while the old
scene is shown, keep the old scene read-only, swap between two frames, and cancel a load when a newer request comes. The
code follows a project's life. `project.create` with a template (`empty`, or `basic3d` with its camera, sun, sky, ground
and post process) and `scene.new {template}`. `project.open` wraps `BeginOpenProject` in the guard and `AfterSaves`,
then `OpenProjectInternal`: the project file is read before the open project closes; the asset manager scans in the
background; the trash is purged of what is older than 30 days; the recovery scan waits for the asset scan; the script
engine opens; a project saved by 0.5.0 or older is migrated once (`ProjectMigration` reads every scene's collision
layers on a job, merges them into the project's table with the start scene's names first, reports conflicts, and the
file is written as version 3); the start scene waits for the scan and the migration; the project joins the recent
projects (at most 12, shared by every editor, read-only for scripted runs). The recent projects share `<user
data>/Strata/` with the person's other file, the preferences store (`EditorPreferences`, `Preferences.json`, format 1,
at most 64 KiB): the values of the settings registry's user sections for every project, each validated by its section
and kept as stored when its section refuses it, written in the background so that a failed write leaves the file
unwritten and the change in memory, a file that a later editor wrote left alone with changes refused, and 0.5.0's
`EditorSettings.json` imported once; `preferences.set` and `preferences.save` are Session commands and record no undo
step. Opening a scene: `BeginOpenScene` asks `SceneLoader` for the file as it is now and prepares the render proxies
while the old scene is shown; `CheckSceneEditable` is the read-only guard for code that edits outside `CommitEdit`;
`UpdateSceneLoad` swaps in `FinishOpenScene` (through `ResetScene`, a residency trim, the scene's stored camera or a
framing), then runs the prefab catch-up before anyone sees the scene; `scene.open` answers one frame after the swap with
the frames' times; `scene.loadStatus` reports progress; a newer request cancels. Samples open as copies without
`.strata` (`project.samples`, `project.openSample`), and `project.close` takes the same guard. The rules: a scene being
opened is read-only; scenes load through `SceneLoader`, never `LoadAssetSync`, and are let go with
`Scene::ReleaseInBackground`. The example opens a copy of `Samples/OpenWorld` with `project.openSample`, polls
`scene.loadStatus`, and tries an edit while the start scene opens to read the refusal. The trace exercise follows a
scene's open from `BeginOpenScene` to the frame `FinishOpenScene` swaps it in. Afterwards the reader can open, create
and close projects from code without a stalled frame or a lost edit.

**Leaves out.**

- The guard, `AfterSaves` and `ResetScene` themselves → `editor/saving`
- The launcher and the project dialogs as they are drawn → `editor-ui/launcher-dialogs`
- The scene loader's states, slices and prepared loads → `world/sub-scenes`
- The project file, its versions and settings sections → `world/projects-settings`
- The settings file writer and the Editor discard scope → `editor/saving`
- The Preferences window as it is drawn → `editor-ui/settings-windows`
- Project pictures → `editor/thumbnails`
- The default template's lighting → `make/lighting`
- The project folder as a game maker sees it → `make/project-files`

**Fit.** `fits`: about 5,650 words against L (5,000). Counted again from the sections, with the person's preferences
store and the trace exercise: a project's open, a scene's open and the migration with four excerpts take the most,
beside templates, samples, recent projects and the preferences.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-core:361` | concept | home | Opening content in the background: read-only while loading, swap between frames, cancel on a newer request |
| `editor-core:204-208` | feature | home | `BeginOpenScene`, `CheckSceneEditable`, `scene.open`, `scene.loadStatus`, `BeginOpenProject` |
| `editor-core:209-210` | feature | home | Templates (`empty`, `basic3d`) and samples as copies without `.strata`; recent projects |
| `new:70` | feature | home | The person's preferences store (`EditorPreferences`), beside the recent projects in `<user data>/Strata/`: `Preferences.json` (format 1, at most 64 KiB) holds the values of the settings registry's user sections for every project; a stored section is validated by its section and kept as stored when refused; writes run in the background, and a failed one keeps the change in memory and the file unwritten; a file a later editor wrote is left alone and changes are refused; 0.5.0's `EditorSettings.json` is imported once; `preferences.set` and `preferences.save` are Session commands with no undo step (about 250 words; the writer and the Editor discard scope stay `editor/saving`'s). Evidence: `StrataEditor/src/Editor/EditorPreferences.h:23-35`, `:37`, `:43-48`, `:64-79`; `StrataEditor/src/Editor/EditorContext.h:107-112`; `StrataEditor/src/EditorApplication.cpp:304`, `:363`; `StrataEditor/src/Editor/EditorPreferencesCommands.cpp:121-156`, `:158-183` |
| `new:5` | feature | home | The migration of projects saved by 0.5.0 or older: the scenes' collision layers read on a job and merged into the project's table, conflicts reported, the file written as version 3. Evidence: `StrataEditor/src/Editor/ProjectMigration.h:15-57`; `StrataEditor/src/Editor/EditorContext.cpp:488-550` |
| `new:6` | code | home | `StrataEditor/src/Editor/EditorContext.cpp:365-451`: `OpenProjectInternal`, a project that opens at once while its assets scan and its start scene waits |
| `new:7` | code | home | `StrataEditor/src/Editor/EditorContext.cpp:770-807`: `BeginOpenScene`; with `:869-879` (`CheckSceneEditable`) and `:899-942` (the swap and the prefab catch-up) |
| `new:8` | code | home | `StrataEditor/src/Editor/EditorContext.cpp:505-550`: `UpdateProjectMigration`, the merge on the main thread and the file written once |
| `editor-core:502` | figure | home | A scene opening in the background, from the request to `scene.open`'s answer |
| `editor-core:531` | figure | home | The viewport's load card and the read-only banner while a large scene opens |
| `editor-core:571` | rule | home | A scene being opened is read-only: check `CheckSceneEditable` outside `CommitEdit` |
| `editor-core:578` | rule | home | Never `LoadAssetSync`; load scenes through `SceneLoader`; release them with `Scene::ReleaseInBackground` |
| `worlds-runtime:177-179` | feature | home | Templates, recent projects and samples, as the worlds survey lists them |
| `worlds-runtime:181` | feature | home | The project and template commands |
| `gamedev:365` | code | home | `StrataEditor/src/Editor/ProjectTemplates.cpp:31-95`: what `basic3d` puts in a new scene |
| `gamedev:555` | hands-on | home | Exercise: read `PopulateBasic3D` and add a third template |
| `new:53` | hands-on | home | Trace it yourself (D27): open a copy of a sample with `project.openSample`, with breakpoints in `BeginOpenScene`, `UpdateSceneLoad` and `FinishOpenScene`; count the frames between the request and the swap, and name what runs after the swap before anyone sees the scene. Evidence: `StrataEditor/src/Editor/EditorContext.cpp:770-807`, `:899-942`, `:944` |
| `worlds-runtime:567-568` | term | home | Template, sample |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The unsaved-changes guard, `AfterSaves` and `ResetScene` | `editor/saving` | must |
| Deferred commands | `editor/deferred-commands` | must |
| `SceneLoader`, its states, prepared loads and `ReleaseInBackground` | `world/sub-scenes` | must |
| The project file, its versions and settings sections | `world/projects-settings` | must |
| Settings sections of user scope | `world/projects-settings` | helps |
| The settings file writer and unwritten settings files | `editor/saving` | helps |
| The project's collision layer table | `physics/collision-layers` | helps |
| The background asset scan | `assets/importing` | must |
| Residency, trims and pins | `assets/residency` | helps |
| Render proxies built before a scene is shown | `draw/render-scene` | helps |
| The recovery scan and its offer | `editor/recovery` | helps |
| The prefab catch-up when a scene opens | `editor/prefab-instances` | helps |

## `editor/trash-references` — The trash and references

**Covers.** The problem: a person deletes a material three scenes use, or an agent moves a texture, and undo must bring
the file back with the same handle, or refuse because something else now lives at that path. The naive answers are
`std::filesystem::remove`, and a delete that never asks who uses the asset. The idea: files are part of the history too;
deletes go to a trash, references are checked first (including unsaved uses in memory), handles are kept, and an undo
step checks its preconditions before it touches a file. Strata's code: the `AssetFileAction` family (trash, move, create,
create folder), steps that never change the scene and hold the asset manager weakly; `asset.delete` and
`asset.deleteFolder`, which move the file, its `.meta` and its cached import to `<project>/.strata/Trash` for 30 days,
undo restoring the handle; `AssetReferences::Find`, which joins the index of recorded referencers, a walk of the edited
scene in memory and the project's own references (start and loading scenes, icon, settings), and puts `referencedBy`
into the error's data; the preconditions (undo fails when something else is at the path; redo runs only when the path
still holds exactly those assets and the delete would be allowed now); deletes by agents and scripts are announced to the
person, the person's own are not; moves and trash refuse files that a save is writing; and the source scan that fails
any panel which writes, moves or removes a file. The example deletes a material the open scene uses (refused, with the
users listed), deletes an unused texture and undoes it (same handle), then moves it and tries an undo after a new file
took the old path. The trace exercise finds which of the three sources of `AssetReferences::Find` named the material's
user. Afterwards the reader can add a file operation that is undoable and never overwrites.

**Leaves out.**

- The reference graph, closures and prefetch → `assets/references`
- Handles and `.meta` files → `assets/handles-meta`
- The Delete Asset dialog as it is drawn → `editor-ui/launcher-dialogs`
- Document claims of a save → `editor/saving`
- Deleting and undoing as a game maker does it → `make/assets`

**Fit.** `over`: about 4,700 words against M (3,000). Counted again from the sections, with the trace exercise: one
concept, eight features, three excerpts and the shape of an internals page pass M's top; the next size is L (5,000)
(S2).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-core:338` | concept | home | Files are part of the history: trash, references checked first, handles kept, undo that re-checks |
| `assets:141` | feature | home | The asset manager's file operations the steps call: moves, the trash and its restore, the purge after 30 days; handles survive |
| `editor-core:160-166` | feature | home | The file actions, delete to trash, the reference check, preconditions, announced agent deletes, files a save writes, panels never touch files |
| `editor-core:427` | code | home | `StrataEditor/src/Editor/EditorAssetCommands.cpp:899-939`: `asset.delete` with `referencedBy` and its trash step; with `AssetFileAction.cpp:94-107` (trash and restore as a step) |
| `new:9` | code | home | `StrataEditor/src/Editor/AssetFileAction.cpp:62-92`: `CheckRedo`, a redo that runs only while the path still holds what it deleted |
| `new:10` | code | home | `StrataEditor/src/Editor/AssetReferences.h:19-77`: the referencers and `Find`, the index, the scene in memory and the project |
| `editor-core:484` | figure | home | An asset delete with the trash and its undo |
| `editor-core:521` | figure | home | The delete refusal listing the users, and the toast of an agent's delete |
| `assets:513` | figure | home | A delete refused with its `referencedBy` list, then the restore by undo; one picture with `editor-core:521` |
| `assets:628` | hands-on | home | The example: a safe delete, a forced one, and its undo |
| `new:54` | hands-on | home | Trace it yourself (D27): run `asset.delete` on a material the open scene uses, with a breakpoint in `AssetReferences::Find`, and name which of its sources (the index of recorded referencers, the edited scene in memory, the project's own references) found the user. Evidence: `StrataEditor/src/Editor/AssetReferences.h:19-77`; `StrataEditor/src/Editor/AssetReferences.cpp:162`; `StrataEditor/src/Editor/EditorAssetCommands.cpp:899-939` |
| `editor-core:544` | rule | home | Panels never write, move or remove files |
| `editor-core:713-714` | term | home | Trash, referencer |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Undo steps, their failure rules and `ChangesScene` | `editor/undo` | must |
| References an asset records and the reference graph | `assets/references` | must |
| Asset handles and `.meta` files | `assets/handles-meta` | must |
| Weak references (`weak_ptr`) | `basics/cpp-memory` | helps |
| Files a save claims | `editor/saving` | helps |

## `editor/prefab-instances` — How prefab instances stay linked

**Covers.** The problem: many instances of one prefab must stay in step with it while people edit both sides, in open and
closed scenes, with undo. The data model (links, instance roots, overrides and their computation), the approaches of
other engines and propagation are `world/prefabs`', and the page links them; this page keeps the model exact while
editing. Strata's choice: an override list kept current on every edit, and versions and hashes so that closed scenes
catch up, with "outdated" when both sides changed. The commands come first:
`prefab.create` (entities captured into a `.stprefab` and linked, as one step), `prefab.instantiate` (one or many,
checked up front, one step, names made unique, marked synced), `prefab.status` (changed, added and removed entities,
overrides, modified, outdated), `prefab.apply` (an instance or one override written into the prefab, added entities
linked, the other instances given the change except their overrides, as one step that wraps the document's step and the
scene's; refused for models, while playing, and for an outdated instance without `force`), `prefab.revert` (whole, one
component or one property, UUIDs kept), `prefab.unpack` and `prefab.select`. Then the upkeep: `UpdatePrefabOverrides`
inside `CommitEdit`, which tracks the instance roots an edit touched (so that a drag still merges) and updates their lists
incrementally unless the instance was reshaped. Then `PrefabSync`, every frame in edit mode: a baseline per prefab in use,
the source revisions it watches, a change on disk propagated in one undo step, the editor's own writes setting the
baseline first, settling over runs of edits. Then the catch-up when a scene opens: an instance whose recorded version
differs and whose synced hash still matches takes the new values; a modified one becomes outdated. The rules: code that
writes a prefab sets the baseline and marks instances synced; code that records a scene step outside `CommitEdit` keeps
override lists current; an outdated instance is never applied without `force`. The perf tests of override upkeep close
the testing section. The example is a crate prefab used in two scenes: change an instance in scene B, close it, apply
from scene A, open B again and read `prefab.status`. The trace exercise follows a drag of an instance's child through
`UpdatePrefabOverrides`. Afterwards the reader can change prefab code without double propagation, stale overrides or
lost values.

**Leaves out.**

- `PrefabInstanceComponent`, instance roots, `PrefabOverrides` and propagation as data, the approaches of other
  engines, and the words apply, revert and unpack → `world/prefabs`
- The inspector's prefab bar and overrides menu as they are drawn → `editor-ui/inspectors`
- Making and using prefabs as a game maker → `make/prefabs`
- No prefab edit mode, nested prefabs or variants → `make/prefabs`, `world/prefabs`
- Models as entity templates → `assets/models-gltf`

**Fit.** `fits`: about 5,400 words against L (5,000). Counted again from the sections, after the approaches and
propagation left for `world/prefabs` and with the trace exercise: nine features, three excerpts (the apply is long) and
five figures take the most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-core:340` | concept | home | Linked instances while editing: Strata's upkeep, versions, hashes and outdated instances; the approaches and propagation are `world/prefabs`' (`scene-ecs:349`), and the page links them |
| `editor-core:174-178` | feature | home | `prefab.create`, `prefab.instantiate`, `prefab.status`, `prefab.apply`, `prefab.revert`, `prefab.unpack`, `prefab.select` |
| `editor-core:180-183` | feature | home | Override upkeep on every edit, `PrefabSync`, the catch-up when a scene opens, the perf instrumentation |
| `editor-core:172-173` | feature | use | The instance link and the root's own transform and name, which `world/prefabs` teaches |
| `editor-core:179` | feature | use | The override API, which `world/prefabs` teaches |
| `editor-core:184` | feature | link | No prefab edit mode; `make/prefabs` says it |
| `editor-core:429` | code | home | `StrataEditor/src/Editor/EditorContext.cpp:1893-1981`: `UpdatePrefabOverrides`, touched instances, reshaped or incremental |
| `editor-core:431` | code | home | `StrataEditor/src/Editor/EditorPrefabCommands.cpp:436-583`: `prefab.apply`; with `:39-72` (`PrefabApplyAction`, one step for file and scene) |
| `editor-core:434` | code | home | `StrataEditor/src/Editor/PrefabSync.cpp:336-383`: `CatchUp`, where version and hash decide updated or outdated |
| `editor-core:486` | figure | home | The anatomy of an instance, with the version and the synced hash the catch-up reads |
| `editor-core:489` | figure | home | The states of an instance: synced, modified, outdated |
| `editor-core:491` | figure | home | Propagation of a change: from `prefab.apply` and from a file changed on disk |
| `editor-core:522` | figure | home | The inspector's prefab bar with overrides marked |
| `editor-core:524` | figure | home | The Hierarchy's marks of a modified and an outdated instance |
| `editor-core:582` | rule | home | Code that writes a prefab sets the sync's baseline and marks instances synced |
| `editor-core:585` | rule | home | Code that records a scene step outside `CommitEdit` keeps override lists current |
| `editor-core:587` | rule | home | Never apply an outdated instance without `force` |
| `editor-core:609` | hands-on | home | The example: outdated instances across two scenes |
| `new:55` | hands-on | home | Trace it yourself (D27): with a breakpoint in `EditorContext::UpdatePrefabOverrides`, drag a value of an instance's child in the Inspector and see the touched instance root updated incrementally; then add an entity under the instance and see its list computed again because the instance was reshaped. Evidence: `StrataEditor/src/Editor/EditorContext.cpp:1893-1981` |
| `editor-core:719` | term | use | Apply, revert, unpack, homed on `world/prefabs`; the page teaches the commands that do them |
| `editor-core:721-724` | term | home | Baseline, catch-up, outdated, part version and synced hash |
| `scene-ecs:173-175` | feature | use | Instance roots, per-property overrides and the root's own transform and name, from the data model |
| `scene-ecs:566` | rule | home | Code that writes a prefab or gives instances its values keeps the bookkeeping exact; taught with `editor-core:582` |
| `scene-ecs:674` | term | home | Outdated instance |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The prefab data model: links, instance roots, overrides, propagation | `world/prefabs` | must |
| Undo groups, `CommitEdit` and `AssetDocumentAction` | `editor/undo` | must |
| Asset documents written by the editor, and saves | `editor/saving` | must |
| Hashes | `basics/data-formats` | must |
| Source revisions and the file watcher | `assets/importing` | helps |
| When a scene's open swaps it in | `editor/projects` | helps |

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

## `editor/worlds` — Editing a streamed world

**Covers.** The problem: the editor shows only the part of a world around its camera, yet an edit must go into the right
cell's file, undo must know which cell an entity belongs to, a save must write only what changed, and Play must copy
only what is loaded. The naive answers are named with their failure: copy the whole world to play (it does not fit),
keep edits in the persistent scene (cells never change), save every cell (minutes for one moved crate). The idea: an
editor world that streams around the editor camera, marks what each undo step touched, moves edited entities into the
cell at their position within the same step, and saves in two steps. The code in order: `EditorWorld` is attached when
the edited scene is a world's persistent scene and streams with its own `WorldStreamer`; the edit settings (edit layer,
visible layers, radius scale: `world.edit`); the reasons a cell stays loaded (`world.loadCells` pins, the selection,
undo steps that asked for a cell until the next save, dirty and saving cells), merged in `SyncPins`; dirty tracking as
an observer of the undo stack; cells in undo steps (`EntityState::Cell`, `LinkCells`, `CheckCells`, and a step that
touches an unloaded cell fails, asks for the cell through `ISceneCellLoader`, and is retried); re-celling inside
`CommitEdit` (`Recell`, new cells made in memory with derived handles) and its rules: only top-level entities change
cell, and a child belongs to its top-level ancestor's cell, so editing a child moves nothing; an entity moves only
within its own layer; entities of the persistent scene stay there; a move into a cell that exists but is not loaded
leaves the entity in its old cell and loads the cell; `world.moveEntities`, the only way to another layer or to the
persistent scene, refuses children, checks every target before it moves one, and no menu runs it; the save in two
requests to the `DocumentSaver` (the persistent scene and the dirty cells from one snapshot, then the World document
with fresh index entries once their stamps exist; saved only after that); the play copy (`PrepareRuntimeCopy` adopts
fully loaded cells, drops partly loaded ones and pins dirty cells); recovery of a world's cells; cell IO (streamed,
cancellable reads of cell documents); the world commands and the defaults of `world.create`, and what `world.setLayers`
refuses: removing a layer that has cells, or changing a layer's cell size, unless `deleteCells` moves those cells to the
trash (content is never re-gridded), and cells loaded in the open world even with `deleteCells`; a rename moves the
layer's folder, and the whole change is one undo step. Then how a world looks in the editor: the cell map and the
viewport's cell bounds, rebuilt only when the world's state version changes, the Hierarchy's world strip and its search
by layer and cell, the Inspector's cell line, and the Asset panel with New > World. The rules: never `Scene::Copy` a
whole world; cell membership changes only through `Scene::SetSubSceneOf` and `EditorWorld`; only `EditorWorld` writes
cell documents, through the `DocumentSaver`; mark saved only after the World document is written; UI code draws cached
views. The example makes a first world with `world.create` and reads its edit layer and cell map; then, in a copy of
`Samples/OpenWorld`, it drags a crate across a cell border, undoes, redoes, saves, and reads `world.status` before and
after. The trace exercise stops in `Recell` during that drag. What `PrefabSync` does with instances in cells that load
later is stated as read in the code, not run (a check before writing). Afterwards the reader can change how the editor
edits worlds without losing an entity between cells.

**Leaves out.**

- Grids, cell keys and layers → `worlds/grids`
- How the streamer decides what loads → `worlds/streamer`
- The cook and the physics capacity of a world → `worlds/physics-scripts`
- The Streaming panel itself → `editor-ui/instrument-panels`
- Making a world as a game maker → `make/large-worlds`

**Fit.** `over`: about 7,350 words against L (5,000). Counted again from the sections, with the rules of re-celling,
what `world.setLayers` refuses, the Check item and the trace exercise: nineteen features, three excerpts, eleven figures
(eight of them screenshots), five rules and two examples pass L's top; the next size is XL (8,000) (S2).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-core:115` | feature | home | Cells in undo: a step that touches an unloaded cell fails, asks the world for the cell, and is retried |
| `worlds-runtime:274` | concept | home | Editing a streamed world: the problem and Strata's answer; the concept's mistake, editing a child entity whose cell is its top-level ancestor's, taught with the rules of re-celling (`worlds-runtime:104`) |
| `worlds-runtime:99-103`, `worlds-runtime:105-109` | feature | home | `EditorWorld`, edit settings, keep-loaded reasons, dirty tracking, cells in undo steps, `MoveEntities`, the world save, the play copy, recovery, cell IO |
| `worlds-runtime:104` | feature | home | Re-celling (`Recell` inside `CommitEdit`, new cells in memory with derived handles) and its rules (about 150 words): only top-level entities change cell, children follow their top-level ancestor; an entity moves only within its own layer; entities of the persistent scene stay there; only `world.moveEntities` moves an entity to another layer or to the persistent scene, and it refuses children, and no menu runs it; a move into a cell that exists but is not loaded leaves the entity in its old cell and loads the cell. At the pin: `StrataEditor/src/Editor/EditorWorld.cpp:289-296`, `:315-345`, `:347-391` (`:365`, `:378`); `git grep -n "world.moveEntities" -- StrataEditor/src/Panels StrataEditor/src/UI` finds nothing |
| `worlds-runtime:111-112` | feature | home | The world commands and the defaults of `world.create` |
| `new:73` | feature | home | What `world.setLayers` refuses (about 120 words, beside the world commands): removing a layer that has cells, or changing a layer's cell size, unless `deleteCells` moves those cells to the trash, since content is never re-gridded; cells loaded in the open world even with `deleteCells`; a rename moves the layer's cell folder; the whole change is one undo step. Evidence: `StrataEditor/src/Editor/EditorWorldCommands.cpp:670-675`, `:740-747`, `:748-754`, `:784-799` |
| `worlds-runtime:113-117` | feature | home | The cell map, the Hierarchy's world strip and search, the Inspector's cell line, the viewport's cell bounds, the Asset panel and New > World |
| `worlds-runtime:326` | code | home | `StrataEditor/src/Editor/EditorWorld.cpp:275-345`: `EnsureCellSubScene` and `Recell` |
| `worlds-runtime:327` | code | home | `StrataEditor/src/Editor/EditorWorld.cpp:477-535`: `SyncPins` and `Update` |
| `worlds-runtime:328` | code | home | `StrataEditor/src/Editor/EditorWorld.cpp:760-799`: `PrepareRuntimeCopy` |
| `worlds-runtime:364` | figure | home | The editor world |
| `worlds-runtime:366` | figure | home | The world save as a sequence |
| `worlds-runtime:369` | figure | home | Play from the editor |
| `worlds-runtime:388-392` | figure | home | Screenshots of a world in the editor: the Hierarchy's strip, the Cells chip, the cell map; the cell map of the Streaming panel (`worlds-runtime:392`) is one capture set with `editor-ui:579` on `editor-ui/instrument-panels`, made once (R34, D42), and this page's caption says what it teaches: the world's cells as the editor keeps them |
| `worlds-runtime:395-399` | figure | home | Screenshots: the cell map's menu, the Inspector's cell line and search, an unsaved cell, the Asset panel with `world.info`, New > World |
| `worlds-runtime:414-420` | rule | home | Never copy a whole world; membership only through `SetSubSceneOf` and `EditorWorld`; only `EditorWorld` writes cells; saved only after the World document |
| `worlds-runtime:455` | rule | home | UI code draws cached views of the world: the cell map and cell bounds rebuild only on a state version |
| `worlds-runtime:467` | hands-on | home | The example: a first world, its edit layer and its cell map |
| `new:57` | hands-on | home | Trace it yourself (D27): in a copy of `Samples/OpenWorld`, drag a crate across a cell border with a breakpoint in `EditorWorld::Recell`, and name the cell it leaves and the cell it joins within the same undo step. Evidence: `StrataEditor/src/Editor/EditorWorld.cpp:275-345` (`Recell` at `:315`) |
| `new:58` | open | home | Check: `PrefabSync` with cells. The claim: `PrefabSync` catches a prefab's instances up once per prefab and scene, the first time it looks at the prefab, so a cell that streams in after another cell already used the prefab may keep its old instances; cells not loaded since a prefab changed keep them in their files, and an export packs those files as they are. The page states it as read in the code, not run, and the brief is not blocked (R39); after a result, about 100 words. Evidence: `StrataEditor/src/Editor/PrefabSync.cpp:174-181`, `:205-241`; `Docs/Manual/Worlds.md:100` says prefab changes reach a cell's instances when the cell loads in the editor; `git grep -n -i prefab -- StrataTests/src/Editor/EditorWorldTests.cpp` finds nothing |
| `worlds-runtime:540` | term | use | Adoption |
| `worlds-runtime:541-545` | term | home | Re-celling, edit layer, dirty cell, cell map, cell bounds |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The streamer, its sources and pins | `worlds/streamer` | must |
| Grids, cell keys and layers | `worlds/grids` | must |
| Sub-scenes and `Scene::SetSubSceneOf` | `world/sub-scenes` | must |
| Undo observers, `CommitEdit` and `EntityState` | `editor/undo` | must |
| The `DocumentSaver` and save points | `editor/saving` | must |
| The running copy | `editor/play-mode` | must |
| The recovery journal | `editor/recovery` | must |
| Derived handles | `assets/handles-meta` | helps |
| Content stamps of assets | `assets/importing` | helps |
| The trash and undoable file operations | `editor/trash-references` | helps |

## `editor/script-builds` — Building scripts from the editor: toolchains, CMake, diagnostics

**Covers.** The problem: a game maker presses Play after changing a script, and the editor must build the game's module
with a C++ toolchain it may have to find on this machine, without blocking a frame, and show every compiler error at its
file and line. The naive answers are named with their failure: build on the main thread (the editor freezes), always
reconfigure (slow), never reconfigure (a new file is missing from the module), show the raw log (the cause is lost). The
page follows one build. It runs on the engine's `Process` (child processes, their output, timeouts and the process tree
ended as one, taught on `core/platform` and linked): `ScriptBuilder` runs CMake in such child processes, polled once per
frame, one build at a time, in the phases FindingToolchain, Configuring and Building, streams the output to the log in
bounded lines, and ends the whole process tree when cancelled. The toolchain: by default the one the engine was
configured with (baked into `ScriptBuildConfig.h`), so modules match the engine; an installed editor (the
`StrataInstall.json` marker) builds against the installation's SDK and finds a toolchain on this machine on an I/O job
(on Windows Visual Studio 2022 17.10 or later or 2026 through vswhere, and a CMake 3.25 or later that knows its
generator by `cmake -E capabilities`; on Linux and macOS the system compiler, Ninja or Make and CMake), and without one
the build fails with what to install. Configuring only when needed: the tree's stamp records the toolchain and the
sorted list of source files; another toolchain removes the tree; an added, removed or renamed file configures it again
where it is, because a Visual Studio build compiles the projects as they were configured. Build trees too deep for
MSBuild's file tracker (259 characters) move to a private per-user build directory. `Scripts/CMakePresets.json` gives
IDEs the same toolchain. Diagnostics: errors and warnings of MSVC, GCC, Clang, MSBuild, the linkers and CMake parsed
into file, line, column, code and message, summaries told apart from causes, a failure always naming its cause, and the
Console finding a source line in a message. Building before Play: `GetPlayBuildReason` compares the sources with what
the last build compiled, file by file; `play.start` waits for the build, fails with its first errors and asks for the
Problems panel. After a build the module loads or hot-reloads (the file watcher paused during the editor's own build), a
crashed module loads again even when unchanged, and one toast changes from "Building scripts" to its outcome. The second
half: the script directory as the editor lists it (dot-folders and build trees left out, as the module's glob does;
bounded; classes read from `ST_SCRIPT_CLASS` lines; listed on an I/O thread with a version); the project's script files
(`CMakeLists.txt` through the `StrataScriptCore` package, the `Spinner` example, `script.init`, `script.create` with
validated class and field names); and the external editor, a command template started without a shell, the user's
setting or `STRATA_EXTERNAL_EDITOR`, never the project's, with `script.open` opening only code, CMake and text files of
the project or the engine. The rule: projects never choose what runs. The example: in a `basic3d` project,
`script.create` a class, break it on purpose, press Play, read the build's diagnostics in `script.status`, fix it and
Play again. The trace exercise follows Play after a changed source from `GetPlayBuildReason` through the build's phases.
Afterwards the reader can change the editor's build pipeline and predict when a build configures, where it builds and
what it reports.

**Leaves out.**

- `Process`: child processes, their output and the process tree → `core/platform`
- What a script's crash during play does → `editor/play-mode`
- Shared libraries and the module's binary interface → `scripting/shared-libraries`
- `strata_add_script_module` and building outside the editor → `make/script-builds`
- Loading a module and hot reload → `scripting/hot-reload`
- The Problems panel, the Console and the build pills as they are drawn → `editor-ui/instrument-panels`
- The Preferences window's External Editor page → `editor-ui/settings-windows`
- Building in the editor as a game maker → `make/first-script`

**Fit.** `over`: about 6,700 words against L (5,000). Counted again from the sections after `Process` left for
`core/platform` and the crash during play for `editor/play-mode`, with the trace exercise: eleven features, seven
excerpts and the internals shape stand over L's top. The next size is XL (8,000) (S2); the split that editor-q3 named
stays the other way: `editor/script-builds` "Building scripts from the editor: toolchains, CMake, diagnostics" (L) and a
new page after it, `editor/script-sources` "Script sources, new scripts and the external editor" (M, with its own fixed
parts and exercise) (S3).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:14` | feature | home | `ScriptBuilder`: CMake in child processes polled once per frame, one build at a time, its phases, output streamed in bounded lines, the process tree ended on cancel. Evidence: `StrataEditor/src/Editor/ScriptBuild.h:192-283`; `StrataEditor/src/Editor/ScriptBuild.cpp:1125-1153`, `:1248-1262` |
| `new:15` | feature | home | The toolchain: the engine's own, baked at configure time; an installation's SDK and a toolchain found on this machine on an I/O job; what to install when none is found. Evidence: `StrataEditor/src/Editor/ScriptBuild.h:23-53`; `StrataEditor/src/Editor/ScriptBuildConfig.h.in:1-13`; `StrataEditor/src/Editor/ScriptToolchain.h:18-133`; `StrataEditor/src/Editor/ScriptToolchain.cpp:564-603`, `:708-721` |
| `new:16` | feature | home | Configuring only when needed: the tree's stamp of toolchain and source files; removed for another toolchain, configured again where it is for added or removed files. Evidence: `StrataEditor/src/Editor/ScriptBuild.h:206-219`; `StrataEditor/src/Editor/ScriptBuild.cpp:1021-1087` |
| `new:17` | feature | home | Build trees too deep for MSBuild's file tracker build in a private per-user directory; refused only when both are too deep. Evidence: `StrataEditor/src/Editor/ScriptBuild.h:61-92`; `StrataEditor/src/Editor/ScriptBuild.cpp:468-528`, `:993-1000` |
| `new:18` | feature | home | `Scripts/CMakePresets.json` for IDEs, with the engine's toolchain, rewritten only when Strata wrote it. Evidence: `StrataEditor/src/Editor/ScriptBuild.h:94-104`; `StrataEditor/src/Editor/ScriptBuild.cpp:530-623` |
| `new:19` | feature | home | Diagnostics of compilers, linkers and CMake; summaries; a failure that names its cause; source references in log messages; errors counted as the Problems panel counts them. Evidence: `StrataEditor/src/Editor/ScriptBuild.h:106-135`, `:179-180`; `StrataEditor/src/Editor/ScriptBuild.cpp:629-793`, `:1264-1268` |
| `new:20` | feature | home | Building before Play: why Play builds first, the build `play.start` waits for, its failure and cancellation, `build: false`. Evidence: `StrataEditor/src/Editor/EditorContext.h:576-591`; `StrataEditor/src/Editor/EditorContext.cpp:2288-2353`; `StrataEditor/src/Editor/Commands/PlayCommands.cpp:26-125` |
| `new:21` | feature | home | After a build: load or hot reload, the watcher paused during the build, a crashed module loaded again, one toast that changes; `script.build {wait}` and `script.status`. Evidence: `StrataEditor/src/Editor/EditorContext.cpp:2517-2544`, `:2562-2642`; `StrataEditor/src/Editor/EditorScriptCommands.cpp:247-256`, `:314-353` |
| `new:22` | feature | home | The script directory as the editor lists it: dot-folders and build trees left out, bounded listings, classes from `ST_SCRIPT_CLASS` lines, changes found file by file, a list kept on an I/O thread. Evidence: `StrataEditor/src/Editor/ScriptSources.h:16-124`; `StrataEditor/src/Editor/ScriptSources.cpp:198-324`, `:337-404` |
| `new:23` | feature | home | The project's script files: the `CMakeLists.txt`, the `Spinner` example, `script.init`, `script.create` with validated names. Evidence: `StrataEditor/src/Editor/ScriptProject.h:16-57`; `StrataEditor/src/Editor/ScriptProject.cpp:207-259`, `:307-370`; `StrataEditor/src/Editor/EditorScriptCommands.cpp:394-416` |
| `new:24` | feature | home | The external editor: a command template split into a program and its arguments and started without a shell; batch files refused but VS Code's launcher; the user's preference or `STRATA_EXTERNAL_EDITOR`; the default application otherwise; `script.open` limited to code, CMake and text files of the project or the engine. Evidence: `StrataEditor/src/Editor/ExternalEditor.h:20-117`; `StrataEditor/src/Editor/ExternalEditor.cpp:124-149`, `:215-257`, `:354-395`; `StrataEditor/src/Editor/EditorContext.cpp:2363-2404` |
| `new:25` | rule | home | Projects never choose what runs: a shared project must not start a program of its choosing when a file opens. Evidence: `AGENTS.md:362-363` |
| `new:26` | code | home | `StrataEditor/src/Editor/ScriptBuild.cpp:1021-1087`: configure or build, the stamp, a tree reused, configured again or removed |
| `new:27` | code | home | `StrataEditor/src/Editor/ScriptBuild.cpp:1177-1246`: `Update`, the child process polled, its output drained, configure then build |
| `new:28` | code | home | `StrataEditor/src/Editor/ScriptToolchain.cpp:234-341`: finding Visual Studio and a CMake that knows its generator, or saying what to install |
| `new:29` | code | home | `StrataEditor/src/Editor/EditorContext.cpp:2300-2345`: `GetPlayBuildReason`, sources compared with what the last build compiled |
| `new:30` | code | home | `StrataEditor/src/Editor/Commands/PlayCommands.cpp:99-125`: `play.start` waiting for its build; with `:45-96`, how it ends |
| `new:31` | code | home | `StrataEditor/src/Editor/ExternalEditor.cpp:215-257`: `ExpandCommand`, a template made into a program and arguments, never a shell |
| `new:32` | code | home | `StrataEditor/src/Editor/ScriptBuild.cpp:629-708`: `ParseScriptBuildDiagnostics` |
| `new:33` | feature | home | How it is tested: `Editor.ScriptBuild`, `Editor.ScriptToolchain` (machines described by a `ScriptToolchainEnvironment`), `Editor.ScriptSources`, `Editor.ScriptWorkflow` and `Package.ScriptBuild`. Evidence: `StrataTests/src/Editor/ScriptBuildTests.cpp:98-787`; `StrataTests/src/Editor/ScriptToolchainTests.cpp:241-775`; `StrataTests/src/Editor/ScriptSourcesTests.cpp:57-282`; `StrataTests/src/Editor/ScriptWorkflowTests.cpp:173-739`; `StrataTests/src/Editor/ScriptBuildPackageTests.cpp:176-438` |
| `new:59` | hands-on | home | Trace it yourself (D27): change a script's source, press Play with a breakpoint in `GetPlayBuildReason` and name the file it found changed; then step through `ScriptBuilder::Update` and name the phase it is in when CMake configures and when it builds. Evidence: `StrataEditor/src/Editor/EditorContext.cpp:2300-2345`; `StrataEditor/src/Editor/ScriptBuild.cpp:1177-1246` |
| `foundation:128` | feature | use | `Process`, homed on `core/platform`: the page uses its child processes, captured output and `TerminateTree` for CMake and the toolchain's search, and links `core/platform` |
| `scripting:144-145` | feature | use | `strata_add_script_module` and the `StrataScriptCore` package the script directory's `CMakeLists.txt` uses |
| `scripting:147` | feature | home | The editor's build pipeline as the scripting survey lists it |
| `scripting:197` | feature | home | The editor's script engine: one per project, hot reload on, Play builds first; what a crash during play does is `editor/play-mode`'s, linked |
| `scripting:205` | feature | home | The `script.*` commands |
| `scripting:426` | figure | home | The editor's loop of edit, build, load, Play and Problems |
| `scripting:434` | figure | home | The status bar's build pills |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Configuring and building with CMake, generators | `basics/build` | must |
| Shared libraries and script modules | `scripting/shared-libraries` | must |
| Hot reload of scripts | `scripting/hot-reload` | must |
| `play.start` and the running copy | `editor/play-mode` | must |
| Deferred commands | `editor/deferred-commands` | must |
| `Process`: child processes, their output, timeouts and the process tree; exit codes; finding a program on PATH (`FindProgram`) | `core/platform` | must |
| The terminal, PATH and environment variables | `basics/tools` | must |
| Private directories and files you can trust | `core/files` | must |
| I/O jobs | `core/jobs` | must |
| The user's settings sections (preferences) | `world/projects-settings` | helps |
| A crash location as file and line | `scripting/symbolization` | helps |
| The Problems panel and the build pills | `editor-ui/instrument-panels` | helps |

## `editor/stepping` — Pausing, stepping and exact tests

**Covers.** The problem: a test or an agent must run a game for exactly 60 fixed steps and then check a position; a test
that waits 60 frames gives another answer on a faster machine. The idea is one paragraph that links `core/time`: game
time counts fixed steps, never frames, and a paused game that runs one fixed step per frame gives the same state
whatever the frame rate. The code, from the scene up: `Scene::SetPaused` stops the running systems and tells them
(`OnPausedChanged`), `Scene::Step(n)` lets the next n updates each run exactly one fixed step, and `GetFixedStepCount`
counts the fixed steps since the start, the clock that tools count in; then the editor's `SetPaused` and `Step(n)` (one
fixed step per frame while paused; resuming drops the steps not run yet; the counters of resumes and of fixed steps at a
resume and at a stop; `UpdateInputSuspension`, which suspends input frames while the game is paused without a step to
run); `play.step {steps, wait}`, a deferred Session command whose poll keeps its own state, stacks after earlier calls
and fails with `stepsRun` when the game is resumed or stopped; the frame cap lifted while stepping; the editor's switch
for time dilation, off in tests and scripted runs; and the editor's simulated input: holds made by commands with their
durations in fixed steps, `input.sequence` (a timeline of events per fixed step, observations sampled every n steps,
holds released at the end unless kept) and `input.click` (the pointer moved to a UI element's center and a tap of n
steps, refused when something covers the element). A paragraph takes the commands that act on the game's input as a
whole: `input.action` holds an input action whatever its bindings (named as scripts name it, its value refused when it
does not fit the action's kind; an action has one value, so a new hold replaces the one before without letting the
action go; it reads as up while its map is disabled or a binding capture listens); `input.state` lists the held actions,
every action as the game reads it, the maps' enables, the players' bindings that replace the project's and whether a
capture listens; `input.type` queues typed text (1 to 1,024 bytes); `input.releaseAll` ends every hold and drops presses
still queued. The rule that tools count game time in fixed steps, never frames, is `core/time`'s, and the page links it;
it keeps the rule's exception for simulated input: holds count `EditorContext::GetInputStepCount`, the fixed steps plus
every frame in which a running game updates at time scale 0 without a step, so that a tap on a pause menu still ends.
The example starts a game paused (`play.start {paused: true}`), runs `play.step {steps: 30}` and reads `fixedSteps`,
then plays an `input.sequence` that presses a key at step 10 and samples the ball's height every 5 steps. The trace
exercise counts the fixed steps each frame runs during a `play.step`. Afterwards the reader can write a check of a game
that gives the same result on every machine.

**Leaves out.**

- The fixed step, the accumulator, time dilation and the rule "fixed steps, never frames" → `core/time`
- The simulated device, its merge rules, release and clear → `input/simulated`
- How a click finds a UI element → `ui/input`
- Files of such checks → `editor/command-scripts`
- Play-tests as a game maker writes them → `make/automated-playtests`

**Fit.** `over`: about 4,900 words against M (3,000). Counted again from the sections, with the paragraph on
`input.action`, `input.state`, `input.type` and `input.releaseAll`, the exception of simulated holds and the trace
exercise: the scene's and the editor's pause and step, the `input.*` commands, three excerpts and four figures pass M's
top; the next size is L (5,000) (S2).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-core:352` | concept | home | Fixed steps, pausing and stepping; why tests count steps |
| `editor-core:221-222` | feature | home | The editor's time dilation switch; pause and step with their counters |
| `foundation:186` | feature | home | The scene's pause and `Step`, one fixed step per update while paused, and `GetFixedStepCount` as the tools' clock (`Strata/src/Strata/Scene/Scene.h:427-438`); `core/time` uses the count |
| `editor-core:224-226` | feature | home | `play.step {steps, wait}`, the frame cap lifted while stepping, the editor's simulated input with `input.sequence` and `input.click` |
| `editor-core:438` | code | home | `StrataEditor/src/Editor/Commands/PlayCommands.cpp:191-256`: `play.step`, a deferred Session command with a stateful poll |
| `new:34` | code | home | `StrataEditor/src/Editor/EditorContext.cpp:1560-1624`: `SetPaused` and `Step`, one step per frame and the counters |
| `audio-input:178` | feature | home | `UpdateInputSuspension`: the editor suspends input frames while a paused game has no step to run, inside the excerpt of `new:34`; as passed by `audio-input`, whose `input/devices-state` keeps `Input::SetSuspended` |
| `new:35` | code | home | `StrataEditor/src/Editor/EditorInputCommands.cpp:679-760`: `input.sequence`, events per fixed step and observations |
| `editor-core:496` | figure | home | Fixed steps against frames: catch-up, time dilation, one step per frame while stepping, a tap of n steps |
| `editor-core:530` | figure | home | A paused game after `play.step {steps: 30}` |
| `editor-core:580` | rule | link | Tools count game time in fixed steps, never frames: homed in `core/time`'s rule box; the page links it and keeps the input tools' exception (`audio-input:521`) |
| `new:60` | hands-on | home | Trace it yourself (D27): start a game paused, run `play.step {steps: 3}` with breakpoints in `EditorContext::Step` and in `play.step`'s poll, and count the fixed steps each frame runs until `stepsRun` is 3. Evidence: `StrataEditor/src/Editor/EditorContext.cpp:1577-1582`; `StrataEditor/src/Editor/Commands/PlayCommands.cpp:191-256` |
| `editor-core:693` | term | home | Stepping |
| `editor-core:700` | term | home | Input sequence |
| `audio-input:357` | concept | use | Simulated input, determinism and fixed steps, as the input survey states it |
| `audio-input:179` | feature | home | The `input.*` commands: holds, `input.sequence` and `input.click`; and a paragraph (about 300 words) on `input.action` (an action held whatever its bindings; a new hold replaces the old one's single value; refused when the value does not fit the kind; up while its map is disabled or a capture listens), `input.state` (held actions, every action as read, map enables, players' bindings, the capture), `input.type` and `input.releaseAll`. At the pin: `Docs/DeveloperGuide.md:3746-3768`, `:3806-3807`; `StrataEditor/src/Editor/EditorInputCommands.cpp:761-824`, `:1035-1059`, `:1060-1139`, `:1343-1361` |
| `gameui:220` | feature | home | `input.click` on game UI, world canvases projected, refused when the element is covered |
| `audio-input:464` | figure | home | Simulated holds in fixed steps, as a timeline |
| `audio-input:480` | figure | home | The status bar's pill of simulated holds |
| `audio-input:521` | rule | home | Durations of simulated input count fixed steps, never frames, with the exception the page keeps: `EditorContext::GetInputStepCount` adds every frame in which a running game updates at time scale 0 without a step, so that a tap on a pause menu ends; the rule itself is `core/time`'s (`editor-core:580`). At the pin: `StrataEditor/src/Editor/EditorContext.h:349-352`; `StrataEditor/src/Editor/EditorContext.cpp:2763-2765`, `:2797` |
| `audio-input:689` | term | home | Hold (editor) |
| `scene-ecs:642` | term | home | Stepping |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Fixed steps, the accumulator and time dilation | `core/time` | must |
| Simulated devices and their merge rules | `input/simulated` | must |
| Input actions, their maps and kinds, and the players' bindings | `input/actions` | helps |
| The running copy and `play.start` | `editor/play-mode` | must |
| Deferred commands and polls that keep state | `editor/deferred-commands` | must |
| Game UI rects and hit tests | `ui/input` | helps |

## `editor/command-scripts` — Command scripts and batches

**Covers.** The problem: a regression test of the editor, or the content of a game, should be a file of commands that
runs without a window and fails loudly at the first wrong answer. The idea: data-driven test scripts, and batches that
run as one undo step. The format comes first, on the engine's own smoke script: a JSON array of steps, each a command
with its parameters and optionally `expect` (conditions on the result by JSON pointer: `equals`, `min`, `max`), `bind`
(a name for a value of the result) and `{"$ref": name}` (that value in a later step's parameters), and `until` (a query
step repeated until its expectation holds, bounded by steps or seconds). How `until` waits, with the lines of
`JudgeUntilAttempt`: in a paused game an attempt that misses runs one fixed step before the next, so a paused wait is
exact on any machine (physics checks wait this way, because an unpaused editor drops steps when a frame falls behind);
only the final attempt enters the journal, with its `attempts`; and before the first step runs, the script checks that
`until` repeats a Query and that its bounds hold (steps up to 10,000,000; seconds 300 by default, at most a day).
`EditorCommandScript` checks every reference before anything runs; a failed step is logged and marks the script failed
while the steps after it still run, a step whose binding has no value fails without running, and the editor exits with
code 1; `StrataEditor --commands <file> --no-gpu --quit-after-commands` runs one headless. Then `editor.batch {steps,
atomic}`: up to 1,000 steps run in one frame through `RunStepNow`, deferring, unknown, nested and `until` steps refused
before anything runs, one undo step through an open group, and an atomic batch that cancels the group when a step fails.
Last, the replay the journal exported runs as such a script on a copy of the project. The example and exercise: a script
that creates a project, builds a scene with `bind` and `$ref`, plays, pauses, runs `play.step {steps: 60}` with an
`expect` on a transform and quits, run headless with its exit code read in the terminal. The trace exercise follows a
failed `expect` to the editor's exit code 1. Afterwards the reader can turn any session or check into a file that the
engine's tests can run.

**Leaves out.**

- The journal and how a replay is built → `editor/journal`
- The suites that run these scripts in CTest → `engineering/test-kinds`
- Play-tests as a game maker writes them → `make/automated-playtests`
- Scripts that build a game's content → `make/commands`
- Agents that run scripts and batches → `automation/agents`

**Fit.** `over`: about 4,300 words against M (3,000). Counted again from the sections, with how `until` waits in a
paused game and the trace exercise: one concept, the format and `editor.batch`, three excerpts and the shape of an
internals page pass M's top; the next size is L (5,000) (S2).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-core:359` | concept | home | Scripts of commands, batches as one undo step, record and replay as a test |
| `editor-core:240-241` | feature | home | `EditorCommandScript` with `expect`, `bind`, `$ref` and `until`; `editor.batch {steps, atomic}` |
| `editor-core:245` | feature | home | The smoke command script that CTest runs |
| `editor-core:412` | code | home | `StrataEditor/src/Editor/Commands/BatchCommands.cpp:45-119`: `editor.batch`, refusals up front, the group, the atomic cancel |
| `editor-core:450` | code | home | `StrataTests/Editor/SmokeCommands.json.in:1-30`: a real command script with `bind`, `$ref` and `expect` |
| `build-test:411` | code | home | `StrataTests/Editor/SmokeCommands.json.in:1-30`: the same excerpt as `editor-core:450`, an end-to-end test of the editor as data; as passed by `engineering`, whose `engineering/test-kinds` links it |
| `new:37` | code | home | `StrataEditor/src/Editor/EditorCommandRunner.h:74-205`: the script's format and how it runs |
| `new:71` | code | home | `StrataEditor/src/Editor/EditorCommandRunner.cpp:683-706`: `JudgeUntilAttempt`, a short excerpt (about 150 words with its text): an attempt that misses runs one fixed step first while the game is paused, and the final attempt is the step's one journal entry, with `attempts`; with the checks before the first step, `:644-648` (`until` only on a Query) and `:160-176` with `EditorCommandRunner.h:136-138` (steps up to 10,000,000; seconds 300 by default, at most a day) |
| `editor-core:535` | figure | home | A command script's run in the terminal, with its exit code |
| `editor-core:615` | hands-on | home | The example: a first command script, run headless |
| `new:61` | hands-on | home | Trace it yourself (D27): run a command script whose `expect` cannot hold, headless with `--commands` and `--quit-after-commands`, and follow with a search or a breakpoint the failed step from the script's check to the line of `EditorLayer::UpdateCommandScript` that sets exit code 1. Evidence: `StrataEditor/src/Editor/EditorCommandRunner.h:74-205`; `StrataEditor/src/EditorLayer.cpp:549-558` |
| `editor-core:662-667` | term | home | Command script, `expect`, `bind` and `$ref`, `until`, JSON pointer, batch and atomic batch |
| `automation:150` | feature | home | `editor.batch` as automation clients use it; one home with `editor-core:241` |
| `automation:157` | feature | home | Command scripts: the format that `--commands`, `editor.batch` and the replay export share; one home with `editor-core:240` |
| `build-test:682` | term | home | Command script, as the build and test survey defines it; one home with `editor-core:662` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Commands and their results | `editor/commands` | must |
| Undo groups | `editor/undo` | must |
| Deferred commands and waiting by the clock | `editor/deferred-commands` | must |
| The journal and the replay export (a forward link: a script is also written by hand) | `editor/journal` | helps |
| `play.step` and `input.sequence` | `editor/stepping` | must |
| JSON | `basics/data-formats` | must |
| Exit codes and headless runs | `core/platform` | must |

## `editor/journal` — The activity journal and replays

**Covers.** The problem: when a person and an agent share an editor, the person must see what the agent did and undo it,
and an afternoon of work should become a test that repeats it. The approaches (logs, the undo history, macro recorders,
event sourcing) are compared on `automation/agents`, which the page links. Strata's choice: every command is journalled
once, in `Execute`, with its origin (UI, Automation with the client's name, CommandScript, Internal; nested commands as
children), its kind, its parameters (kept whole up to 256 KiB), its outcome, the IDs its result holds, its duration and
frames, the entities it touched and its undo step, in a ring of 2,000 entries and 8 MB; a deferred command's entry
completes on its final poll. The rule: UI code passes `CommandOrigin { CommandSource::UI }`, because an origin left out
is recorded as Internal and the journal would no longer say who did what. Edits outside commands (continuous UI edits
that record undo steps directly) are counted, because a replay cannot repeat them. The latest automation activity feeds
the agent's presence in the UI. Summaries read like "Rename 'Crate' to 'Box'". The person is told what others did:
toasts for an agent's deletes and discards, never for the person's own actions. `editor.activity` reads the journal, and
`editor.activity.export` builds a replay (`BuildReplayScript`): a forward pass finds which entry first produced each ID
and rewrites later parameters to refer to it, a backward pass adds the lookups the edits need; only Edit commands not
made on the running copy are repeated, so the kinds of `editor/commands` decide what a replay holds, and an unmarked
command counts as an edit. A paragraph says what a replay cannot hold: edits outside commands (inspector fields, gizmo
drags, the material editor), counted as `editsOutsideCommands`; IDs taken from the selection or from `editor.status`,
which stay as they are because the selection is not repeated; what `scene.recover` applied, counted as
`unrepeatableEdits`; and files no command wrote (script sources an agent edited, generated source assets), so the fresh
copy needs its `Scripts/` before the script runs. The file format of the exported script is the next page's; this page
shows an export only as a list of commands whose IDs became references. Tests: `Editor.Journal`, `Editor.Replay` in
process and the CTest `ReplaySession`, which exports a session, replays it on a copy of the project and compares the
documents. The example and exercise: work by hand and through `StrataCLI`, export the session, and read
`editsOutsideCommands`; the trace exercise finds where `BuildReplayScript` turns an ID into a reference. Afterwards the
reader can add a command whose work the journal records and a replay repeats.

**Leaves out.**

- The command script format (`bind`, `$ref`, `expect`) → `editor/command-scripts`
- The Activity panel as it is drawn → `editor-ui/instrument-panels`
- The agent chip and flash as they are drawn → `editor-ui/scene-view`
- Why accountability matters for agents, and logs, undo histories, macro recorders and event sourcing compared →
  `automation/agents`
- The activity journal as a game maker uses it with an agent, and copying `Scripts/` before a replay →
  `make/with-an-agent`

**Fit.** `over`: about 4,800 words against M (3,000). Counted again from the sections, with what a replay cannot hold
and the trace exercise, and with the comparison of approaches linked to `automation/agents`: the journal's items that
the unit `automation` passed here (section 1.9, the suites, an excerpt, a figure, the rule on origins) beside the unit's
own pass M's top; the next size is L (5,000) (S2).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-core:372` | concept | home | Telling the person what happened: origins, toasts for what agents did, never for the person's own actions |
| `editor-core:242-244` | feature | home | `CommandJournal`, `editor.activity` and `editor.activity.export`, the replay tests |
| `new:36` | code | home | `StrataEditor/src/Editor/CommandJournal.h:72-111`: one journal entry |
| `editor-core:504` | figure | home | Record and replay: entries, the export, a run on a copy, the comparison |
| `editor-core:513` | figure | home | The Activity panel listing commands of the person, an agent and a command script |
| `editor-core:618` | hands-on | home | The example: a session exported as a regression script |
| `new:62` | hands-on | home | Trace it yourself (D27): create an entity with `entity.create` and rename it with `entity.rename` from a terminal, export the session with `editor.activity.export`, and with a breakpoint in `CommandJournal::BuildReplayScript` find where the rename's entity ID becomes a `$ref` to the create's result. Evidence: `StrataEditor/src/Editor/CommandJournal.cpp:697-818`, `:368` |
| `editor-core:668-670` | term | home | Activity journal, origin, replay script |
| `automation:430` | concept | use | Accountability: the journal, presence and replay; the problem in one sentence, and the comparison of logs, undo histories, macro recorders and event sourcing linked to `automation/agents`, its home |
| `new:72` | feature | home | What a replay cannot hold (about 100 words): edits outside commands (`editsOutsideCommands`); IDs taken from the selection or `editor.status`, kept as they are because the selection is not repeated; what `scene.recover` applied (`unrepeatableEdits`); files no command wrote (script sources an agent edited, generated source assets), so a fresh copy needs its `Scripts/` before the script runs. Evidence: `StrataEditor/src/Editor/EditorStateCommands.cpp:489-500`, `:537-539`; `.claude/skills/strata-editor-automation/SKILL.md:742-747`; `.claude/skills/strata-make-a-game/SKILL.md:438-442` |
| `automation:166-175` | feature | home | The journal's entries, origins, kinds, results kinds, recording in `Execute`, edits outside commands, ID collection, `BuildReplayScript`, the latest automation activity, summaries; one home with `editor-core:242` |
| `automation:151`, `automation:152` | feature | home | `editor.activity` and `editor.activity.export` as clients call them; one home with `editor-core:243` |
| `automation:240` | feature | home | `Editor.Journal`: every source recorded once, a deferred command recorded when it finishes, every command's kind declared |
| `automation:241` | feature | home | `Editor.CommandScriptBindings` and `Editor.Replay`; `editor/command-scripts` may cite the bindings' suite |
| `automation:243` | feature | home | The CTest `ReplaySession`: a session exported, replayed on a copy and compared; one home with `editor-core:244` |
| `automation:506` | code | use | `Execute` journals every command |
| `automation:508` | code | home | `StrataEditor/src/Editor/CommandJournal.cpp:697-818`: `BuildReplayScript`, the forward pass for the IDs each result gave first and the backward pass for the lookups and bindings the edits need |
| `automation:564` | figure | home | The replay export as a data flow: produced IDs, parameters rewritten to `$ref`, lookups marked backward, the script with `bind`; beside `editor-core:504` |
| `automation:639` | rule | home | UI code passes `CommandOrigin { CommandSource::UI }`, so the journal says who did what |
| `automation:782`, `automation:784` | term | home | Presence; edits outside commands |
| `automation:780-781`, `automation:783` | term | use | Activity journal, command origin, replay script, homed here as `editor-core:668-670` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Commands, their kinds and `Execute` | `editor/commands` | must |
| Undo steps and the history | `editor/undo` | must |
| Deferred commands and their final poll | `editor/deferred-commands` | helps |
| The running copy | `editor/play-mode` | helps |
| JSON pointers into a result | `editor/command-scripts` | helps |

## `editor/placement` — Placing content

**Covers.** The problem: a person drags a prefab into the Scene view, or an agent calls `asset.place` with a point of the
view, and both must land the asset on the surface under that point, resting on it, the same way to the bit; the ghost
shown while dragging must show exactly that place and write nothing. The naive answers: place at the origin, rest the
box's center instead of its bottom, drop where the ghost was not. The idea, with its geometry: a ray from the camera
through a point of the image (from normalized device coordinates), candidates from a spatial index, exact tests on
triangles, fallbacks when nothing is hit, snapping, and a box resting on a slanted plane by its support distance along the
normal (`|n|·extents − n·center`). Strata's code: `SceneRaycast::Cast`, the editor's own ray against what the scene
draws, taught under its own name (the glossary's raycast, a query against colliders, is `physics/queries`' and is
linked): the render scene's spatial index, then the loaded triangles, or bounds while a mesh loads, with the entities
being placed ignored; `EditorPlacement::Place` (a surface hit,
else the grid plane y = 0 within 500 m, else a point in front; snapping across the normal's main axis, with a ray cast
down again on upward ground; `RestOn`); `FindPivotSurface`, where the create menus put new entities; `MakeRayRequest` and
`MakeViewRay`, one request with the same floats for the drop and for `asset.place`, the ray relative to the camera;
`PlacementPreview`, the ghost's box, ring and label, which writes nothing and casts again only when its key changes;
`AssetBounds`, what an asset draws around its origin, cached by content stamp; `scene.raycast` and `asset.place`, an Edit
command that waits by the clock; `entity.dropToGround` with five rays; `SceneBounds` for framing and placement. Placement
by a ray is new after 0.7.0. The rule: place through `EditorPlacement::Place`, and the drop and its ghost use one request.
The example calls `asset.place` for a crate at a point over a ramp and at a point of the sky, and compares the answers
with the ghost. The exercise adds a `stackOn` option that rests an asset on another entity's bounds; the trace exercise
compares the request of a drop with that of an `asset.place` call. Afterwards the reader can change how content is
placed and keep the person's drop and the agent's call identical.

**Leaves out.**

- Rays, planes, boxes and their tests → `basics/math-geometry`
- Bounds and the render scene's spatial index → `draw/bounds-culling`
- The drop and the ghost as the Scene view draws them → `editor-ui/scene-view`
- Physics raycasts against colliders, and the glossary's entry raycast → `physics/queries`
- Positions relative to the camera → `draw/mirrors-camera-relative`

**Fit.** `over`: about 5,300 words against M (3,000). Counted again from the sections, with the trace exercise: the
geometry of resting a box, nine features, four excerpts and two exercises pass M's top; the next size is L (5,000) (S2).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-core:363` | concept | home | Placing objects in 3D: rays from the camera, broad and narrow tests, fallbacks, snapping, resting a box |
| `editor-core:190-198` | feature | home | `SceneRaycast::Cast`, `EditorPlacement::Place`, `FindPivotSurface`, `MakeRayRequest`, `PlacementPreview`, `AssetBounds`, `scene.raycast` and `asset.place`, `entity.dropToGround`, `SceneBounds` |
| `editor-core:800` | open | home | Placement by a ray (`asset.place`, `scene.raycast`, the ghost) came after 0.7.0: its sections are marked new in 0.8.0; the other dates the survey could not find stay unstated |
| `editor-core:443` | code | home | `StrataEditor/src/Editor/EditorPlacement.cpp:125-213`: `Place` and `RestOn` |
| `new:38` | code | home | `StrataEditor/src/Editor/EditorPlacement.h:82-94`: `MakeViewRay` and `MakeRayRequest`, one request for the drop and the command |
| `new:39` | code | home | `StrataEditor/src/Editor/Commands/PlacementCommands.cpp:463-600`: `asset.place`, the Edit command that waits by the clock |
| `new:40` | code | home | `StrataEditor/src/Editor/SceneRaycast.h:17-41`: where a ray meets what a scene draws |
| `editor-core:498` | figure | home | The placement decision flow, and a box resting on a slanted surface |
| `editor-core:526` | figure | home | The placement ghost on a surface and over empty sky |
| `scene-ecs:482` | figure | home | The prefab placement ghost; one picture with `editor-core:526` |
| `editor-ui:568` | figure | home | Dragging a prefab over the Scene view: the box ghost and its label; one picture with `editor-core:526` and `scene-ecs:482` |
| `editor-core:589` | rule | home | Place through `EditorPlacement::Place`; the drop and its ghost use one request |
| `editor-core:637` | hands-on | home | Exercise: a `stackOn` option |
| `new:63` | hands-on | home | Trace it yourself (D27): drop a prefab on the Scene view, then call `asset.place` at the same point of the view, each with a breakpoint in `MakeRayRequest`, and compare the two requests' origin, direction and distances to the float. Evidence: `StrataEditor/src/Editor/EditorPlacement.h:82-94`; `StrataEditor/src/Editor/EditorPlacement.cpp:97-123` |
| `editor-core:725` | term | link | Raycast, one entry homed on `physics/queries`; the page teaches the editor's ray against the scene under its own name (`SceneRaycast`) and links the entry |
| `editor-core:727-729` | term | home | Support function, snapping, placement ghost |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Rays, planes, boxes and intersection tests | `basics/math-geometry` | must |
| Dot products and normals | `basics/math-vectors` | must |
| Bounds and the spatial index | `draw/bounds-culling` | must |
| Normalized device coordinates | `gpu/coordinates` | must |
| Positions relative to the camera | `draw/mirrors-camera-relative` | helps |
| Undo steps | `editor/undo` | must |
| Deferred commands | `editor/deferred-commands` | must |
| Prefab instances | `editor/prefab-instances` | helps |
| Content stamps of assets | `assets/importing` | helps |

## `editor/thumbnails` — Thumbnails

**Covers.** The problem: the Content Browser shows hundreds of assets as pictures; rendering each costs GPU time,
rendering them again at every start or edit wastes it, and a picture that no longer matches its asset misleads. The
idea: a cache keyed by content, whose key hashes the content stamps of the asset and of everything it depends on
together with a version of how the pictures are made; pictures rendered offscreen one at a time; pixels read back
without stalling a frame. The content stamp (`EditorAssetManager::GetContentStamp`) is `assets/importing`'s, and the
page links it: here it is what the key hashes. Strata's code: `ThumbnailCache` (textures from the levels of their mip
tail, read by byte range so that a thumbnail never loads a whole chain; materials on a sphere and meshes, models and
prefabs framed, rendered under the preview lighting by an offscreen `SceneRenderer` and read back with
`TextureReadback`; PNG files in the cache directory named by the key; `c_Version`, bumped when thumbnails would look
different; `Request` every frame for what is on screen only; large previews for the Asset tab, kept in memory);
`DisplayImage`, the RGBA8 textures of display colors the UI draws as they are; and `ProjectThumbnail`, the launcher's
picture taken after each scene save, rendered at three times 480x270 and averaged down once loads, exposure and TAA have
settled. The rule: bump `ThumbnailCache::c_Version` when thumbnails would look different. The example edits and saves a
material, watches its key change and its thumbnail render again, then restarts the editor and sees it read from its
file; the trace exercise stops in `ComputeKey` during that save. Afterwards the reader can add a kind of asset preview
that never stalls a frame and is never stale.

**Leaves out.**

- The content stamp, how it is built and what it lasts across → `assets/importing`
- Thumbnails drawn in the Content Browser's tiles → `editor-ui/lists`
- Readback and GPU timing → `gpu/readback-timing`
- The preview lighting → `light/lights`
- The launcher's cards → `editor-ui/launcher-dialogs`

**Fit.** `over`: about 4,200 words against M (3,000). Counted again from the sections, after the content stamp left for
`assets/importing` and with the trace exercise: one concept, the two cached kinds of picture, three excerpts and the
shape of an internals page pass M's top; the next size is L (5,000) (S2).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-core:370` | concept | home | Caches keyed by content; a version for how pictures are made; readback without stalls |
| `editor-core:256-257` | feature | home | `ThumbnailCache` and `ProjectThumbnail` |
| `new:41` | feature | home | `DisplayImage`: RGBA8 textures of display colors that the editor's UI draws as they are (thumbnails). Evidence: `StrataEditor/src/Editor/DisplayImage.h:11-20` |
| `new:42` | code | home | `StrataEditor/src/Editor/ThumbnailCache.cpp:1127-1134`: `ComputeKey`, the version and the content stamps of the dependency closure |
| `new:43` | code | home | `StrataEditor/src/Editor/ThumbnailCache.cpp:763-894`: `UpdateSceneJob`, one offscreen picture at a time, read back when ready |
| `new:44` | code | home | `StrataEditor/src/Editor/ProjectThumbnail.h:16-88`: the launcher's picture and what it waits for |
| `editor-core:533` | figure | home | The launcher's project cards and the Content Browser's thumbnails |
| `worlds-runtime:180` | feature | home | Project thumbnails, as the worlds survey lists them |
| `assets:145` | feature | use | The content stamp, homed on `assets/importing`: the thumbnail cache's key hashes the stamps of an asset's dependency closure |
| `assets:216` | feature | home | Thumbnails read a texture's cooked header and mip tail by byte range |
| `editor-core:593` | rule | home | Bump `ThumbnailCache::c_Version` when thumbnails would look different |
| `new:64` | hands-on | home | Trace it yourself (D27): edit and save a material with a breakpoint in `ThumbnailCache::ComputeKey`, see its key change through the content stamp of the material or of a texture it uses, then follow `UpdateSceneJob` as it renders the picture again and reads it back. Evidence: `StrataEditor/src/Editor/ThumbnailCache.cpp:1127-1134`, `:763-894` |
| `editor-core:735` | term | home | Thumbnail cache |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| A frame of the scene renderer | `gpu/frame-tour` | must |
| Readback without stalls | `gpu/readback-timing` | must |
| Residency: requests every frame, reads of a mip tail | `assets/residency` | must |
| Dependency closures | `assets/references` | must |
| Importing, cached imports and the content stamp | `assets/importing` | must |
| The preview lighting | `light/lights` | helps |
| TAA and its settling | `image/taa` | helps |
| Display colors and RGBA8 | `basics/color` | helps |
| Projects and their saves | `editor/projects` | must |

## `editor/camera-viewport` — The editor camera and viewport state

**Covers.** The problem: a person must look at any part of a scene quickly (orbit around what they look at, pan, dolly
in, fly through), frame a selection, find each scene as they left it, and every view (the Scene view, the Game view, a
capture) must know which camera it draws with. The idea, with its geometry: an orbit camera in spherical coordinates
(yaw and pitch in degrees, a distance around a target), pitch clamped at 89 degrees, panning by the units one pixel
covers at the target's depth, dollying by a factor per wheel step in double precision, framing a box by its eight
corners against the frustum, the position as the target minus the forward direction times the distance, and a reversed-Z
projection. The code: `EditorCamera` (Orbit, Look, Pan, Dolly by 0.85 per wheel step, Move, fly mode at a speed the
wheel changes by 1.25 per step and Shift makes four times faster, Focus on the bounding sphere at r·1.1/sin of the
narrower half field of view, `FitBounds`, `LookAt`, saved as JSON; the mouse buttons and keys that drive it are named
once); `EditorViewport` (the camera; a camera stored per scene; `ViewportSettings`; three renderers for the Scene view,
the Game view and captures; picking named and linked; `FrameScene`; saved to `<project>/.strata/EditorViewport.json`);
`ViewportSettings` (grid, outline, gizmos, colliders, stats, preview lighting, game UI, canvas mode, gizmo mode and
space, snap steps, debug view, cell bounds, the Game view's mode, piloting the game camera, edit pose, quality); the
first framing of a scene along its primary camera, framed again once loading meshes arrive unless the person moved the
camera; which camera each view uses (`ResolveViewportView`, `ResolveSceneView` with the Game camera on F8,
`ResolveGameView` with UI over black when there is no camera, `GetViewportRenderOptions` with preview lighting and the
HUD hidden in editor views); and the view commands `camera.get`, `camera.set`, `camera.focus`, `viewport.getSettings`,
`viewport.setSettings` and `viewport.capture`, which record no undo step. Then the section "Captures", because the
book's own figures come from it: a capture is not a screenshot of the viewport. It renders with the capture renderer,
which keeps its own history, through the camera it is asked for (the editor camera, the scene's, or one of its own made
from position, target and field of view, which leaves the person's view where it was), at the view's size or 1280x720
while the view is hidden; its poll renders again while glyphs, assets, finer mips, poses, new instances, shadow views,
the pre-exposure, global illumination or TAA are still pending, each with its own frame limit (glyphs 120, assets 300,
mips 120, poses 8, instances 120, shadow views 16, pre-exposure 8, TAA 16); the pixels are read back without a stall and
encoded as PNG on a job, and the result reports what was still pending (`pendingAssets`, `texturesBelowWanted`,
`waitedFrames`, `previewLighting`, the hidden canvases). Live captures (`live`, `atFixedStep`, `frames` up to 16) read
back what a view presented instead, its last frame, because the command polls run before the views render. The example
focuses the camera on a selection with `camera.focus`, turns it with `camera.set {yaw, pitch}`, reads `camera.get` and
takes a capture. The exercise derives `Pan`'s units per pixel from the field of view and the distance, and why
`FitBounds` uses the corners; the trace exercise checks `Focus`'s distance in a debugger. Afterwards the reader can
change the editor camera, the views' camera choice and the captures, which `editor-ui/scene-view` and the book's figures
build on.

**Leaves out.**

- Picking and gizmos → `editor-ui/scene-view`
- The Scene view's drags that drive the camera (mouse buttons, keys, the locked cursor) → `editor-ui/scene-view`
- The Game view's resolutions and letterboxing → `editor-ui/game-view`
- Projection, frustums and depth as mathematics → `basics/math-projection`
- Strata's clip space and reversed depth → `gpu/coordinates`
- Debug views and what each shows → `gpu/debugging`
- Reading pixels back without a stall → `gpu/readback-timing`
- TAA, its jitter and its history → `image/taa`

**Fit.** `fits`: about 5,300 words against L (5,000). Counted again from the sections: the section "Captures" (about 700
words with its excerpt) and the camera's concept with its geometry take the most, beside six features, two more
excerpts, one figure and three hands-on.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-core:367` | concept | home | Editor cameras: orbit, pan, dolly and fly, framing, reversed-Z, a view state per scene |
| `editor-core:230` | feature | home | Which camera each view uses and what editor views change |
| `editor-core:251-255` | feature | home | `EditorCamera`, `EditorViewport`, `ViewportSettings`, the first framing, the view commands |
| `editor-core:445` | code | home | `StrataEditor/src/Editor/EditorCamera.cpp:70-91`: orbit; with `:136-170` (`FitBounds` over eight corners) and `:256-259` (the position) |
| `editor-core:447` | code | home | `StrataEditor/src/Editor/ViewportRenderer.cpp:24-95`: which camera a view uses |
| `new:65` | feature | home | How `viewport.capture` works (the section "Captures", about 700 words, with `editor-core:255`): the capture renderer and its own history; the camera a capture uses (editor, scene, or its own from position, target and field of view, the person's view unmoved; 1280x720 while the view is hidden); the poll that renders again while glyphs (120 frames), assets (300), finer mips (120), poses (8), new instances (120), shadow views and probes (16), the pre-exposure (8), global illumination (54: its 38 settle frames plus 16) are pending, and then TAA (16) and spatial reflections (2) settle; the readback and the PNG encoded on a job; what the result reports (`pendingAssets`, `texturesBelowWanted`, `waitedFrames`, `previewLighting`, hidden canvases); live captures (`live`, `atFixedStep`, `frames` up to 16), which read back a view's last frame because polls run before views render. Evidence: `StrataEditor/src/Editor/EditorViewportCommands.cpp:36-81`, `:480-660`, `:723-735`, `:808-845`, `:878-962`, `:1211-1235`; `Strata/src/Strata/Renderer/SceneRenderData.h:771` (`c_GIMaxSettleFrames`) |
| `new:66` | code | home | `StrataEditor/src/Editor/EditorViewportCommands.cpp:808-845`: the capture's poll, what is still pending and the limit of each, and the history started again while the content is incomplete |
| `editor-core:500` | figure | home | The editor camera's model: target, distance, yaw, pitch, the pan plane, framing |
| `editor-core:641` | hands-on | home | Exercise: the camera's mathematics |
| `new:67` | hands-on | home | Trace it yourself (D27): select an entity, run `camera.focus` with a breakpoint in `EditorCamera::Focus`, and check the distance it sets against r·1.1/sin of the narrower half field of view, with r the bounding sphere's radius. Evidence: `StrataEditor/src/Editor/EditorCamera.cpp:117-134`; `StrataEditor/src/Editor/EditorCamera.h:57` |
| `editor-core:696` | term | home | Editor view |
| `editor-core:730-732` | term | home | Orbit camera, pivot, dolly, pan and fly |
| `editor-core:734` | term | home | Framing |
| `editor-ui:200` | feature | home | The editor camera as the UI survey lists it: orbit, pan, dolly, fly with Shift, Focus and `FitBounds`, saved per scene; one home with `editor-core:251`; the drags are `editor-ui/scene-view`'s |
| `editor-ui:516` | figure | home | The camera's geometry with the pitch clamp, pan's units per pixel and the focus distance; one picture with `editor-core:500` |
| `editor-ui:766`, `editor-ui:768` | term | home | Editor camera with orbit, pan, dolly and fly; framing (Focus, `FitBounds`); one home with `editor-core:730-732` and `editor-core:734` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Projection, the field of view and frustums | `basics/math-projection` | must |
| Angles, yaw and pitch, spherical coordinates | `basics/math-rotations` | must |
| Bounding boxes and their corners | `draw/bounds-culling` | must |
| The camera, clip space and reversed depth | `gpu/coordinates` | must |
| The editor core and `EditorContext` | `editor/program` | must |
| Commands and their kinds | `editor/commands` | must |
| The running copy, the Scene view and the Game view | `editor/play-mode` | helps |
| The placement preview | `editor/placement` | helps |
| Deferred commands and their polls (a capture is one; the page says so in a sentence) | `editor/deferred-commands` | helps |
| Readback without stalls | `gpu/readback-timing` | must |
| Jobs and returning results to the main thread | `core/jobs` | helps |
| TAA and its settling | `image/taa` | helps |

## `editor/tutorial-command` — Tutorial: adding a command

**Covers.** What the reader makes: the WindZone, as `scripting/tutorial-host-function` left it, gets two commands,
`wind.list` (a Query that lists every WindZone and its fields) and `wind.set` (an Edit that sets the fields of several
WindZones in one undo step), with their kinds declared, a unit test, and a run from the terminal. The sections follow
the command conventions of the engine's Developer Guide. First, where commands live: the registry's constructor calls
one `Register` function per group, so the page adds `Commands/WindCommands.cpp` with `RegisterWindCommands`, configures
again for the new file, and sees `Editor.Journal` fail because no kind list names the new commands, and
`CLI.McpToolsets` fail because the `wind` group is in no MCP toolset: the `wind.` prefix joins the `world` toolset in
`c_PrefixToolsets` (a toolset said in one sentence and linked to `automation/mcp`), and the patch names
`CLI.McpToolsets` in its tests (`patch.tests`), so that no later page starts from a failing test. Second, `wind.list`: a
schema with no parameters, an answer with entity IDs and values, the Query kind in its list; `StrataCLI call wind.list`
answers on the starting scene. Third, `wind.set`: a schema with `entities` and the values, `CommandArguments` with the
ranges the component's reflection declares, every input checked before anything changes, one `SceneEditTransaction` over
all entities, the change signalled, `FinishEdit`; modelled on `entity.rename`. Fourth, a test suite
`Editor.WindCommands`: two zones set in one step and undone; an invalid value refused with nothing changed; a call while
playing answered with the running-copy warning. Fifth, the run: the editor built, `wind.set` called with parameters from
`@wind.json`, `edit.undo`, and the journal entry read back. Each section ends with a checkpoint of the patch, and its
"You should see" is the build or test output as a text capture. The exercises: a `wind.reset` that restores the
defaults; making `wind.set` refuse an entity without a WindZone with the list of such entities in the error's data.
Afterwards the reader has added a complete, undoable command that people, agents and tests can call.

**Leaves out.**

- The command's place in the feature test, for commands a game relies on → `engineering/feature-test`
- A deferred command → `editor/deferred-commands`
- The WindZone's gizmo, host function and script API → `gpu/debug-drawing`, `scripting/tutorial-host-function`
- MCP toolsets and why the `core` toolset stays small → `automation/mcp`
- The WindZone as one change through every layer → `capstone/build`

**Fit.** `fits`: about 5,900 words against L (5,000). Counted again from the sections, with the step that adds the
`wind.` prefix to `c_PrefixToolsets` and names `CLI.McpToolsets` in `patch.tests`: eighteen steps in five sections and
six quoted hunks take the most, beside the checkpoints and two exercises.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-core:625` | hands-on | home | Adding a mutating command end to end, made the WindZone's `wind.*` commands |
| `new:45` | code | home | `StrataEditor/src/Editor/EditorCommands.cpp:41-80`: the registry's constructor, one `Register` call per group |
| `new:46` | code | home | `StrataTests/src/Editor/CommandJournalTests.cpp:209-239`: the test that every command declares its kind; with `:99-197`, the lists a new command joins |
| `new:68` | code | home | `StrataCLI/src/CLI/McpToolsets.cpp:43-54`: `c_PrefixToolsets`, the table from a command group's prefix to its MCP toolset, where the step adds `{ "wind.", "world" }` beside `world.` and `physics.`; with `StrataTests/src/Editor/EditorMcpToolsetsTests.cpp:54-59`, the check of `CLI.McpToolsets` that every command is in a toolset, which the patch names in `patch.tests` (D38, capstone-q7) |
| `editor-core:54-60` | feature | use | The command's metadata, result, arguments, utilities and kind lists |
| `editor-core:112` | feature | use | `SceneEditTransaction` over several entities |
| `editor-core:119` | feature | use | `FinishEdit` and `RollBackEdit` |
| `editor-core:385` | code | use | `entity.rename` as the model of a mutating command |
| `editor-core:542` | rule | use | Every change goes through a command |
| `editor-core:546` | rule | use | Reject invalid input without side effects; one undo step per mutation |
| `editor-core:550` | rule | use | Signal component writes |
| `editor-core:558` | rule | use | Mark every command's kind |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The WindZone component and its system | `world/tutorial-component` | must |
| The patch this page starts from: the host function, its scene service and the callback | `scripting/tutorial-host-function` | must |
| Building Strata from source and running one test suite | `core/first-change` | must |
| Commands, their conventions and `StrataCLI call` | `editor/commands` | must |
| Transactions and `FinishEdit` | `editor/undo` | must |
| Reflection and property ranges | `world/reflection` | must |
| The terminal | `basics/tools` | must |
| The running copy and the warning while playing | `editor/play-mode` | helps |

**Starting state.** The engine at the pin with the end state of `scripting/tutorial-host-function` applied
(`startsFrom {"tutorial": "scripting/tutorial-host-function"}`, the WindZone's chain in one line, R30 D5): the WindZone
component and its system of `world/tutorial-component`, their serialization test and the feature test's minimum, and
the host function behind `Wind::GetStrength` with its scene service, the callback and their tests. The source build of
`core/first-change` (its build folder, configured). A checkpoint project whose scene holds two WindZones, so that no
step of this page creates them. The page changes nothing of the host function or the callback, and needs no gizmo of
`gpu/debug-drawing`'s exercise.

**Command-only steps.**

- Every step that runs the new commands has no menu or button: `StrataCLI call wind.list`, `StrataCLI call wind.set
  @wind.json` and `StrataCLI call edit.undo`. `editor/commands`, which teaches running a command, is in the page's Needs
  closure through `editor/undo`.

## Passed on

| Item | Type | To | Why |
| --- | --- | --- | --- |
| `editor-core:46` | feature | `editor-ui/status` | Its home: notifications, their model (`EditorNotifications`) and their drawing (book.md) |
| `editor-core:121` | feature | `editor-ui/scene-view` | Its home: picking and gizmos (`TransformDrag`); `editor/undo` uses it as a merge-key example |
| `editor-core:138` | feature | `editor-ui/shell` | Asking the person (`RequestDiscardChanges` and its release and quit forms) is that page's home |
| `editor-core:154` | feature | `editor-ui/launcher-dialogs` | The Recover Unsaved Changes dialog is drawn there |
| `editor-core:172-173` | feature | `world/prefabs` | The instance link and the root's own transform and name are the data model (book.md); they repeat `scene-ecs:57`, `scene-ecs:173` and `scene-ecs:175` |
| `editor-core:179` | feature | `world/prefabs` | The override API is the data model; it repeats `scene-ecs:174` |
| `editor-core:184` | feature | `make/prefabs` | "A prefab edit mode" is an entry of book.md's "What Strata does not do", said on that page |
| `editor-core:228-229` | feature | `editor-ui/game-view` | Game input focus and the Game view's resolutions are that page's (book.md, input ownership) |
| `editor-core:258` | feature | `editor-ui/lists` | Its home: `HierarchyView` and `AssetBrowserView`, core code drawn there |
| `editor-core:516` | figure | `editor-ui/shell` | The unsaved-changes dialog is how the shell asks the person |
| `editor-core:567` | rule | `editor-ui/shell` | The re-ask rule is that page's home (book.md, no silent data loss) |
| `editor-core:580` | rule | `core/time` | "Fixed steps, never frames" joins `core/time`'s rule box (R31); `editor/stepping` links it and keeps the input tools' exception (`audio-input:521`) |
| `editor-core:595` | rule | `editor-ui/lists` | Cached views instead of walks per frame are that page's subject |
| `editor-core:604` | hands-on | `make/project-files` | The use home of undo, for game makers |
| `editor-core:606` | hands-on | `make/prefabs` | The use home of prefabs; the round trip suits its tutorial |
| `editor-core:611` | hands-on | `make/play-test-debug` | The use home of Play, pausing and stepping |
| `editor-core:613` | hands-on | `editor-ui/game-view` | The Game view's resolutions and letterboxing are taught there; the exercise checks a click where it is drawn |
| `editor-core:614` | hands-on | `make/project-files` | The use home of autosave and recovery |
| `editor-core:685` | term | `world/scene-graph` | Sibling index: one entry with `scene-ecs:626`, since the hierarchy is the scene graph's (duplicates.md:46); `editor/undo` links |
| `editor-core:686` | term | `world/ecs` | Handles and UUIDs as stable identities are that page's (book.md); asset handles are `assets/handles-meta`' |
| `editor-core:687` | term | `assets/handles-meta` | Its home |
| `editor-core:691-692` | term | `core/time` | The fixed step and time dilation are that page's concepts (book.md) |
| `editor-core:695` | term | `gpu/coordinates` | The camera and Primary are that page's (book.md) |
| `editor-core:697` | term | `light/lights` | Preview lighting is that page's (book.md) |
| `editor-core:699` | term | `input/simulated` | The virtual devices are that page's (book.md) |
| `editor-core:702` | term | `core/files` | Atomic writes are that page's (book.md) |
| `editor-core:715-718` | term | `world/prefabs` | Prefab, instance and instance root, template id and override name the data model |
| `editor-core:719` | term | `world/prefabs` | Apply, revert, unpack: one entry with `scene-ecs:672`, the same definitions (duplicates.md:40); `editor/prefab-instances` uses it for the commands |
| `editor-core:720` | term | `world/prefabs` | Propagation is part of the data model (book.md) |
| `editor-core:725` | term | `physics/queries` | Raycast: one entry with `physics:520` (R31); `editor/placement` teaches the editor's ray against the scene under its own name and links the entry |
| `editor-core:726` | term | `draw/bounds-culling` | The render scene's spatial index, which the editor's raycast uses, is taught there |
| `editor-core:733` | term | `basics/math-projection` | Reversed-Z: one entry with `foundation:634`, where the mathematics of depth is taught (duplicates.md:30); `gpu/coordinates` keeps Strata's convention and links |
| `editor-core:736` | term | `assets/importing` | Content stamp: one entry with `assets:145` beside cache validity (R31 D33); `editor/thumbnails` uses it |
| `editor-core:737` | term | `gpu/readback-timing` | Its home |
| `editor-core:738` | term | `editor-ui/status` | Notifications are that page's home |
| `editor-core:739` | term | `core/first-frame` | Headless: one entry with `foundation:583` (duplicates.md:44); the entry says that `--headless` keeps the graphics device and `--no-gpu` drops it; `editor/program` uses it and states both options |
| `editor-core:740` | term | `assets/importing` | Asset scan: homed with the scan itself, `assets:130` (critic-editor-core-10); `editor/deferred-commands` uses it for the scan wait |
| `editor-core:789` | open | `nowhere` | A note about the files the survey did not read in full; the new items of `editor/script-builds` and `editor/projects` cover what this unit read since |
| `editor-core:797` | open | `nowhere` | A note that engine pieces were read only by their headers; their pages are other parts' |
| `editor-core:807` | open | `nowhere` | A note that no screenshots were taken; the list of section 4 is a specification |
| `editor-core:808` | open | `nowhere` | A note that the feature test was not checked; at the pin it counts no editor commands, and a command a game relies on gets a step in its runs (`Docs/DeveloperGuide.md:850`), which `engineering/feature-test` teaches |

## Not taken

none

## Questions for the planner

none
