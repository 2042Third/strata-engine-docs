# Notes: `core/profiling`

## New terms

The glossary entries this page homes (profiler, Tracy, frame stage, median with P95 and nearest rank) are defined in
bold. The page also defines these in bold; the brief's items name them as homed here, and the page's term list does
not hold them, so please add them if the glossary lacks them:

- **self time**: the time spent in a stage without the time of the stages nested in it. Home: `core/profiling`.
  Aliases: self-time.
- **inclusive time**: the time spent in a stage with the time of the stages nested in it. Home: `core/profiling`.
- **percentile**: the sample that a given share of all samples does not exceed; P50 is the median, P95 the 95th
  percentile. Home: `core/profiling`. Aliases: percentiles, P95.
- **CPU-bound**: the CPU's work takes at least 90 % of the frame interval. Home: `core/profiling`.
- **GPU-bound**: the GPU's busy time takes at least 90 % of the interval and exceeds the work time. Home:
  `core/profiling`.
- **capped**: neither side reaches 90 % of the interval, so vsync, a cap or idle throttling sets the pace. Home:
  `core/profiling`.

## Requests

- `layouts/performance.ini` is no longer asked for: the figures `performance-panel` and `frame-pill` now use
  `layouts/make-performance-tall.ini` and `layouts/make-performance-960.ini` (see Figures).
- Engine: a command that pauses and resumes the Performance panel as its **Pause** button does (an `editor.showPanel`
  parameter, for example), for the variant `performance-panel.paused`.
- Host for a cited source without a link: Epic Games' documentation of Unreal Insights (an entry of Further reading).
- `names`: the stage names (`Input`, `Assets.Update`, ..., `Editor.Commands`, `World.Streaming`) are names of the
  frame profiler's stages, which the dumps do not hold; `names` reports them as unknown sections or tests (28) and
  `World.Streaming` as a component property (2). `ST_ENABLE_TRACY` is a compile definition that CMake sets
  (`Strata/CMakeLists.txt:47`), so `names` finds no `#define`.
- The warnings `passive` (34) and `noun-stack` (4) are left: nearly all are state words ("is still open", "is
  CPU-bound", "is registered") with no actor to name.

## Since

`since: 0.3.0`. `FrameProfiler.h` first appears in `58dabf98` ("Add an always-on frame profiler, editor.perf and
runtime perf logs"), which `v0.3.0` contains; `Profiling.h` and the Tracy macros come from the first commit
(`a0f2865f`). GPU stages came in 0.4.0, snapshots in wave 8.

## Not verified

- Tracy's on-demand mode sends data only while a viewer is connected, and the viewer must have the same Tracy version
  as the client: general Tracy knowledge; the engine sets `TRACY_ON_DEMAND` (`Strata/vendor/CMakeLists.txt:237`).
- The Tracy capture of the editor (figure `tracy-capture`) and which zones it holds on the worker threads: the engine
  has no `ST_PROFILE_SCOPE` in `JobSystem`, so the brief's "job zones on the workers" is not claimed; the exercise
  says only that a zone inside a job appears on the worker.
- `ST_PROFILE_THREAD` is defined but no engine code, editor code or test calls it at the pin (searched with `grep`).
- The sampling profilers named in the table (Linux perf, Visual Studio's profiler) and the trace recordings of Unreal
  Insights and Unity are cited from general knowledge; only the Tracy, Unity and Visual Studio entries link.
- The frame pill's tooltip is only described; its figure shows the pill (a tooltip needs a hover command).
- Figures `performance-panel`, `frame-pill` and `tracy-capture` wait for pictures; `editor-perf-json` is a text figure
  taken from a command's result, and its fence is empty until the figure is taken.

## Findings not applied

- `new:15` (Roadmap says eleven stages, there are twelve, `Present` outside the work time): applied; the page names
  twelve and `Present` as the one outside the work time.
- The brief's figure "the ring of 600 frames; GPU times attached frames later" is one part of the map diagram, not a
  figure of its own.
- The brief's figure of the pill's tooltip is not drawn (see Not verified).

## Clerk

- Admitted: self time, CPU-bound, GPU-bound, capped.
- Left for the planner: `dev.epicgames.com` (the fetch of its front page returned 403, nothing to confirm). (Unreal Insights)
- `ST_ENABLE_TRACY`: the macros dump at the pin holds CMake compile definitions since commit 856be6c; `names` accepts it.
- Left for the planner: `layouts/performance.ini`; the frame profiler's stage names in `names`.
- Not admitted, because the page check would then fail and the page is the writer's: inclusive-time (its paragraph would define 2 terms with self time (term-paragraph)); percentile (its paragraph would define 2 terms with Median (term-paragraph)). The part's reviewer splits the paragraph or section; the next clerk admits it then (the entries are in the wave-1b clerk's apply.py).

## Figures

- Retaken 2026-11-23 at the pin v0.8.0 (319075e3), one hold, one round each, recipes unchanged:
  - `editor-perf-json`: same fields and shape as the 822a7a46 take (`frames` 60, `frame`, `interval`, `stageSum`,
    `stages/Scene.Physics` with `inFrameTime` true); only the measured times moved (frame p50 1.08 ms, Scene.Physics
    avg 0.70 ms). Published; `fill` rewrote the page's fence.
  - `frame-pill`: first publish. The status bar's second pill reads "1.9 ms · 120 FPS · 0 jobs", legible scaled to
    768 px and enlarged; no toast, no hover; Performance open in the bottom tabs. Caption and alt hold. Published.
  - `performance-panel` (`paused` waits, tier 3) and `tracy-capture` (tool, owner) were not taken.
- Viewer's fault, 2026-11-23, `editor-perf-json` (note 3 under the fence): stands, but it is the page's words, not
  the picture. The published result has `interval.maxMs` 17.98 ms beside `frame.maxMs` 1.61 ms and `stageSum.maxMs`
  1.60 ms, so no frame's work was slow; the interval runs from one frame's `BeginFrame` to the next
  (`FrameProfiler.h`, `IntervalMs`), so the long one is a gap between frames. A retake cannot mend it: the numbers are
  measurements, and a run without a long gap would make "far above its median" false instead. Recipe and picture
  unchanged. A writer's edit of note 3: "**Lines 9–13:** the same four numbers for the interval between frames; here
  its maximum is far above its median: one gap between frames was long, though no frame's work time (line 5) was."

- `editor-perf-json` (text, `editor.perf`): published 2026-11-18 under R57. The recipe names its timings in
  `text.measured` (`/frame`, `/interval`, `/stageSum`, `/stages/Scene.Physics`); the two calls agree on the rest
  (`/frames` 60), and the first call's values are published (frame p50 1.12 ms, Scene.Physics avg 0.70 ms). The
  caption now says the times are one run's measurements. Earlier: blocked by the take tool, not by the engine. Round 1 (2026-11-17): the
  recipe now plays the Physics Playground for 120 fixed steps (`"play": {"steps": 120}`, so that the result is "for a
  playing game" as the page's line 512 says) before `editor.perf {"frames": 60}`. The editor answered both calls with
  good numbers (frames 60; frame p50 about 1.42 ms; Scene.Physics avg about 0.95 ms; `gpu.boundBy` `unknown`), but the
  two calls run a frame apart and every mean, median and P95 differs (frame avg 1.422 then 1.358 ms, interval P95 1.90
  then 16.57 ms), so `take_text_command` refuses the figure as nondeterministic. A command text figure has no `redact`,
  and timings never repeat, so no recipe change can pass; further rounds would only spend lock holds. Only `/frames`
  repeats, which would not show the caption's four numbers per time.
  - Needs a tool addition: a command text figure whose values are measurements (e.g. a `"measured": true` field that
    takes one call, or `redact`/rounding applied to command results before the comparison), with the caption then
    saying the numbers are one run's on the book's machine.
  - Nearest honest picture until then: none is published; the fence stays empty. The page's own description of the
    fields (line 504) stands without it.
- `performance-panel` (editor, compare `playing`/`paused`), settled 2026-11-18 with the provisional build (nothing
  published; `waitsFor` kept). The writer's recipe named `layouts/performance.ini`, which does not exist, and pictured
  the whole window. Round 1: the panel at its own pixels (`panel: "Performance"`), `layouts/make-performance-tall.ini`
  at 1280 by 1040 (the panel 860 by 760 px), `play.start` then 300 frames. `playing` is good: the CPU strip stacked by
  stage with the jump where play started, the GPU strip, and the stage table with Avg ms, p50 ms, p95 ms and Max ms
  readable (Scene.Physics avg 0.37 ms), down to the first GPU rows; the "Capped: ..." line is cut by the Stage column.
  - `paused` cannot be taken: the writer's step `play.pause` pauses the game, not the panel, whose numbers keep moving
    and which shows no "Paused · frames a-b" label; only the panel's **Pause** button or Space with the panel focused
    pause it (`PerformancePanel::Pause`), and no command does (searched the provisional build's commands). The variant
    keeps the `playing` steps and now waits for `tier 3: the Performance panel paused by its Pause button; ...`, so
    that it is never taken in the wrong state. Once a command pauses the panel (Requests), add it as the last step and
    change `waitsFor`.
  - What the page gets meanwhile: the `::compare` needs both pictures; nearest honest form is `::figure{id=performance-panel
    variant=playing}`, with the caption reduced to "The panel while the game plays." (a page edit for the writer).
  - Caption no longer says "with the strip moving" (a still picture shows no motion); alt names the CPU and GPU strips.
  - Viewer's faults, 2026-11-18 (round 2, recipe changed, retake not yet taken: the hold was queued behind another
    page's take and stopped):
    - Edit-mode frames in the strips and table (Scene.Physics p50 0.000 ms, Max 56.5 ms): stands. The ring holds 600
      frames and the recipe waited only 300 after `play.start`; both variants now wait 700 frames, as `frame-pill` does.
    - GPU strip 2 to 6 px tall: by design. `PerformancePanel::GetTimelineScale` gives both strips one scale ("so their
      heights compare"), the larger of the CPU's and GPU's P95 times times 1.25; the Physics Playground's GPU is busy
      about 0.5 ms of a 5 ms scale. The alt now says the strips share one scale. Retake to try: the Showcase
      (`project: {sample: "Showcase"}`, prepared in `docs-work/photo/core-profiling/manifest-showcase.json`, with
      `take-both.ps1` taking both forms in one hold); keep the Showcase only if its GPU bars read by stage.
    - "Capped: ..." cut by the Stage column: the pin cannot do better. The table is drawn with
      `ImGuiTableFlags_NoSavedSettings` and stretch weights 3:1:1:1:1 (`PerformancePanel::DrawStageTable`), so no layout
      file sets its widths (the saved layouts of the earlier take hold no `[Table]` section). The whole line (about 106
      characters) needs a Stage column near 575 px, a panel near 1340 px: wider than the 1280 px window, and unreadable at
      768 px. A request for the engine: wrap the bound line, or let it span the table's columns.
    - Caption and alt of two pictures: stands. Caption now "The panel while the game plays.", alt and shows for one
      picture; `paused` keeps its `waitsFor`. The page's `::compare` still wants `::figure{id=performance-panel
      variant=playing}` (a writer's edit), until a command can pause the panel.
- `frame-pill` (editor, whole window): no panel holds the status bar, so the recipe pictures the window at 960 by 540
  (`layouts/make-performance-960.ini`, Performance open in the bottom tabs). Round 1 (300 frames after `play.start`):
  the "Scripts built" toast from play's script build covered the Scene view. Round 2 waits 700 frames: no toast; the
  pill, second from the left in the status bar, reads "2.5 ms · 120 FPS · 0 jobs", legible at the page's 768 px
  (checked scaled and enlarged). Caption and alt now say where the pill is. Good.
- `tracy-capture`: kind `tool`, taken by the owner (tier 3).
- Finished 2026-11-24 at the final pin v0.8.0 (319075e3), R55: no addition comes before the book ships.
  - `performance-panel` `playing`: taken (one hold, one round, the pin's Release build) and published. The panel at its
    own 860 by 760 px: header "Frame 2.09 ms · p95 3.59 · max 6.16 · 120 FPS", **Pause** and **Copy as JSON**, the CPU
    strip stacked by stage, the thin GPU strip at the shared 5 ms scale, and the stage table with Avg ms, p50 ms, p95 ms
    and Max ms down to the first GPU rows (Scene.Physics avg 0.51 ms). No path, no tooltip, no toast. Caption, alt and
    the page's placement (`variant=playing`) hold. `paused` keeps its `waitsFor` as the request for a later edition and
    is not placed; the paragraph before the figure already describes **Pause** in words.
  - `tracy-capture` keeps its `waitsFor` as the request for a later edition: a Tracy build of the editor and the
    viewer, another program, which no take of the picture tool runs. Its stand-in is the drawing `tracy-frame`, placed
    where it stood; the sentence before it now says what the sketch shows and that it is drawn from the code, not
    captured, and that `ST_PROFILE_SCOPE` and `ST_PROFILE_FUNCTION` zones lie inside a stage or on a worker's row (the
    old words, "next to", did not say where they lie).
  - `tracy-frame` (diagram): one frame between two frame marks (`ST_PROFILE_FRAME` in `Application::Run`), not to
    scale. Main thread: `Scene.Animation`, `Scene.Physics`, `Render.Submit` in the pin's order (animation after the
    scripts and before physics, `AnimationRegistration.cpp`), with `PhysicsWorld::Simulate - box3d`
    (`PhysicsWorld.cpp:5019`) inside `Scene.Physics`; two worker rows hold `AnimationSystem::Evaluate`
    (`AnimationSystem.cpp:610`, inside `JobSystem::ParallelFor`) during `Scene.Animation`. Scene systems' stages are
    Tracy zones through `ST_PROFILE_STAGE_ID_ZONE` (`Scene.cpp:108`). Worker rows are not named after the pools:
    `ST_PROFILE_THREAD` is never called, and what name the viewer shows for a thread named only by the system was not
    run. Rendered light and dark, one round; `drawings.mjs check` passes.
  - The page's reading time went from 80 to 85 minutes (the lint's floor after the new sentence).

## Names of this page

- `Game.MyWork`: a stage name the reader makes up for their own work (the page's example and exercises).
- `Game.Pathfinding`: a stage name the reader makes up in an exercise.
- `Game.Cache`: a stage name the reader makes up in an exercise.
- `Group.Name`: the form of a stage name, a placeholder.
