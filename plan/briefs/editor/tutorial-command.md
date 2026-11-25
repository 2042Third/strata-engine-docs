# Brief: `editor/tutorial-command`

| Field | Value |
| --- | --- |
| Title | Tutorial: adding a command |
| Kind | T |
| Size | L |
| Tracks | E |
| Needs | `editor/undo`, `scripting/tutorial-host-function`, `core/first-change` |
| From | new; from editor-core ch. 2 and the Developer Guide's command conventions: the WindZone gets `wind.*` commands; it starts from the end state of `scripting/tutorial-host-function` |
| Unit | `plan/allocation/editor.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

None: the glossary homes no term on this page.
