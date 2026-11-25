# Brief: `editor/deferred-commands`

| Field | Value |
| --- | --- |
| Title | Commands that take frames |
| Kind | I |
| Size | M |
| Tracks | E |
| Needs | `editor/commands`, `core/time`, `assets/importing` |
| From | editor-core ch. 11 (`Defer`, the runner, poll rules, `FrameTimeRecorder`, `editor.wait` and `editor.perf`, `MayDefer`, `WaitsForAssets` and the asset-scan wait); opening scenes and projects is `editor/projects` |
| Unit | `plan/allocation/editor.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `maydefer` | `MayDefer` | - |
| `waitsforassets` | `WaitsForAssets` | - |
| `command-runner` | Command runner | - |
| `deferred-command` | Deferred command | - |
| `poll-function` | Poll function | - |
