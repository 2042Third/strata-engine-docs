# Brief: `editor/command-scripts`

| Field | Value |
| --- | --- |
| Title | Command scripts and batches |
| Kind | I |
| Size | M |
| Tracks | E |
| Needs | `editor/stepping` |
| From | editor-core ch. 12 (`--commands` scripts with `expect`, `bind` and `$ref`, `until`; `editor.batch`) |
| Unit | `plan/allocation/editor.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `ref` | `$ref` | - |
| `bind` | `bind` | - |
| `expect` | `expect` | - |
| `until` | `until` | - |
| `batch-editor` | Batch (editor) | - |
| `command-script` | Command script | - |
| `json-pointer` | JSON pointer | - |
