# Brief: `core/profiling`

| Field | Value |
| --- | --- |
| Title | Measuring the frame: the frame profiler, Tracy and the method |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `core/jobs` |
| From | foundation "Measuring the frame: the frame profiler and Tracy" (§1.5); home of the measuring method: percentiles (taught here, from the average a reader knows), self time, "CPU, GPU or capped" (the CPU and GPU working on different frames is `start/what-an-engine-is`' frame map; the reference machine and the perf tests are `engineering`'s) |
| Unit | `plan/allocation/core.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `core/profiling` — Measuring the frame: the frame profiler, Tracy and the method

**Covers.** The job: how Strata measures where a frame's time goes, all the time and at almost no cost, and how a person
reads the numbers. The problem in the part's full section on measuring, as the home of the method: instrumenting against
sampling profilers; zones and frame markers; Tracy; stage timers that are always on; self time against inclusive time;
percentiles taught from the average the reader knows (the median as P50, P95, by nearest rank; why P50 alone hides the
stutter that P95 shows); "CPU, GPU or capped", from the frame map's CPU and GPU working on different frames; GPU times
that arrive frames late. The map: stages on the main thread, the ring of 600 frames, the summaries, the pools' busy
shares, the GPU stages attached later, listeners and snapshots. The contract: the Tracy macros (`ST_PROFILE_FRAME`,
`ST_PROFILE_FUNCTION`, `ST_PROFILE_SCOPE`, `ST_PROFILE_THREAD`), compiled out unless `STRATA_ENABLE_TRACY`;
`ST_PROFILE_STAGE` and `FrameProfiler` (twelve built-in stages, each named in a list, with one sentence that points
forward to `gpu/upload-queue` for the Present stage; the stages that scene systems, the game UI and the editor add, in
the generated table of every CPU stage on `reference/performance`, which the page links; nested self time; a stage
that counts only on the frame thread, inside a frame, so a stage written inside a job records nothing; the mean, P50,
P95 and maximum, the busy shares from `JobSystem::GetStats`, GPU stages attached late, the classification CPU, GPU or
Capped by its 90% rule on the summarized frames' medians, with one frame at 60 Hz worked through, snapshots while
paused); the rule that a stage wraps a unit of frame work, never calls of nanoseconds (self-time accounting, and a limit
of 64 stages). The toy is a stage timer with a fixed-depth stack of nested scopes, in 50 lines; the real code is
`BeginStage`, the scope class and the macro with its static stage id. The readers of the numbers: the editor's
Performance panel, the status bar's frame pill and `editor.perf`, given as one complete line to paste with one sentence
on what it does (a query that answers in its own frame from the frames the profiler recorded, at most 600) and a link
forward to `editor/commands`. The page's example: a stage added to a layer, nested inside another, read in the panel.
The exercises: that stage and its self time; the editor built with Tracy, its zones compared with the stages; a search
for where each stage beyond the twelve is registered. At the end the reader can add a stage, read a frame's stages and
percentiles, and say whether a frame is CPU-bound, GPU-bound or capped.

**Leaves out.**

- Benchmarks, noise, budgets and the perf lab → `engineering/perf-lab`
- GPU timestamps and readback → `gpu/readback-timing`
- How the Performance panel draws and keeps its own cost low → `editor-ui/instrument-panels`
- Measuring a game, for game makers → `make/performance`
- Every budget and the reference machine, and the generated table of every CPU stage → `reference/performance`
- The Present stage and the display wait it counts → `gpu/upload-queue`

**Fit.** `fits`: about 4,750 words against L (5,000). The measuring method taught from zero (percentiles from the
average; CPU, GPU or capped) and the contract of `FrameProfiler` with its 90% rule take the most; five figures and three
exercises follow.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `foundation:303` | concept | home | Profiling: instrumentation and sampling, zones, frame markers, stage timers that are always on, self time, percentiles by nearest rank, CPU, GPU or capped, GPU times that arrive late; the mistakes (P50 read as the frame time while P95 stutters, stages around calls of nanoseconds) |
| `foundation:95` | feature | home | The Tracy macros, compiled out unless `STRATA_ENABLE_TRACY` |
| `foundation:96` | feature | home | `ST_PROFILE_STAGE` and `FrameProfiler`: the twelve built-in stages, with one sentence that points forward to `gpu/upload-queue` for the Present stage (R31, Present); a link to the generated table of every CPU stage on `reference/performance` (pipelines.md §7.1, `tools/reference.py`; R34, D42; R48), which holds the five that scene systems, the game UI and the editor add (`Scene.UI`, `Scene.Animation`, `World.Streaming`, `Render.UI`, `Editor.Commands`); one sentence that a stage counts only on the frame thread, inside a frame, so a stage inside a job records nothing (`Strata/src/Strata/Core/FrameProfiler.h:158-165`, `:203-205`); self time, the ring of 600 frames, the summaries, the busy shares, GPU stages attached late, listeners, snapshots; the bound classification with its rule (about 100 words): on the medians of the summarized frames, GPU when the GPU's busy time is at least 90% of the frame interval and longer than the work time, CPU when the work time is at least 90% of it, Capped otherwise (vsync, a cap or idle throttling), Unknown without GPU times; why medians (one slow frame does not flip the verdict); one frame at 60 Hz worked through (an interval of 16.7 ms, a bound at 15 ms) (`Strata/src/Strata/Core/FrameProfiler.h:49-56`, `:229-232`; `Strata/src/Strata/Core/FrameProfiler.cpp:152`, `:603-612`) |
| `foundation:362` | code | home | `Strata/src/Strata/Core/FrameProfiler.cpp:409-434`: self-time accounting of nested scopes on a fixed-depth stack; with `Core/Profiling.h` 39-42 (the macro, a static stage id per call site) and `Core/FrameProfiler.h` 386-406 (the scope class) |
| `foundation:418` | figure | home | Nested stages on a time bar, the outer one paused while the inner runs; the ring of 600 frames; GPU times attached frames later |
| `foundation:431` | figure | home | The editor's Performance panel with the stacked stages, while the Physics Playground plays and while it is paused |
| `foundation:433` | figure | home | The status bar's frame pill and its tooltip (CPU, GPU or Capped) |
| `foundation:434` | figure | home | A Tracy capture of the editor built with `STRATA_ENABLE_TRACY`: stage zones on the main thread, job zones on the workers |
| `foundation:441` | figure | home | `editor.perf`'s JSON beside the panel: the same numbers through a command |
| `foundation:487` | rule | home | `ST_PROFILE_STAGE` around a unit of frame work, never around calls that take nanoseconds |
| `foundation:518` | hands-on | home | A custom `ST_PROFILE_STAGE("Game.MyWork")` in a layer, then nested, its self time read in the Performance panel or through `editor.perf` |
| `foundation:519` | hands-on | home | The editor built with `-DSTRATA_ENABLE_TRACY=ON`, captured with Tracy, its `ST_PROFILE_SCOPE` zones compared with the stages |
| `new:32` | hands-on | home | Trace it yourself: with `git grep` for `ProfileStage`, `RegisterStage` and `ST_PROFILE_STAGE`, where each stage beyond the twelve built-in ones is registered or timed (`Scene.UI`, `Scene.Animation`, `World.Streaming`, `Render.UI`, `Editor.Commands`), checked against the generated table and `editor.perf`'s stages. Evidence: `Strata/src/Strata/GameUI/GameUIRegistration.cpp:23`; `Strata/src/Strata/Animation/AnimationRegistration.cpp:39`; `Strata/src/Strata/World/WorldRegistration.cpp:63`; `Strata/src/Strata/GameUI/GameUIRenderer.cpp:72`; `StrataEditor/src/Editor/EditorCommands.cpp:110` |
| `foundation:604` | term | home | Two entries: instrumenting profiler and sampling profiler |
| `foundation:605` | term | home | Tracy |
| `foundation:606` | term | home | Frame stage |
| `foundation:607` | term | home | Two entries: self time and inclusive time |
| `foundation:608` | term | home | Two entries: percentile (P50, P95) and nearest rank |
| `build-test:679` | term | home | Three entries: median, p95 and nearest rank, as the build's inventory words them; the same entries as `foundation:608`, which the perf lab uses (`engineering/perf-lab`) |
| `foundation:609` | term | home | Three entries: CPU-bound, GPU-bound and capped |
| `new:15` | erratum | home | `Docs/Roadmap.md:106` speaks of eleven built-in stages; there are twelve, `Present` among them, outside the work time. Evidence: `Strata/src/Strata/Core/FrameProfiler.h:67-81` (`c_BuiltinFrameStages`, an array of 12) |
| `foundation:109` | feature | use | `JobSystem::GetStats`, the source of the pools' busy shares |
| `editor-core:239` | feature | use | `editor.perf`, the one line to paste: a Query with session results that answers in its own frame, not deferred, from the frames the profiler already recorded (at most 600); the home of the commands stays on `editor/deferred-commands`, which names `editor.wait` alone as the smallest deferred command (`StrataEditor/src/Editor/EditorStateCommands.cpp:912-975`) |
| `build-test:30` | feature | use | The `STRATA_ENABLE_TRACY` switch in CMake |
| `foundation:610` | term | link | GPU timestamp, whose entry is `gpu/readback-timing`'s |
| `foundation:541` | hands-on | link | Reading the Performance panel while a game plays, `make/performance`'s exercise for game makers |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The frame loop, its stages and the work time | `core/frame-loop` | must |
| The pools and `GetStats` | `core/jobs` | must |
| RAII and `static` locals | `basics/cpp-memory` | must |
| The CPU and the GPU working on different frames | `start/what-an-engine-is` | must |
| A build with a CMake option | `core/first-change` | must |
| Reading and running a command | `start/how-to-read` | helps |
| GPU timestamps | `gpu/readback-timing` | helps |
| The Performance panel | `editor-ui/instrument-panels` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `frame-stage` | Frame stage | - |
| `median` | Median | p95, nearest rank |
| `profiler-instrumenting-vs-sampling` | Profiler (instrumenting vs sampling) | - |
| `tracy` | Tracy | - |
