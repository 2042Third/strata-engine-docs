# Brief: `core/frame-loop`

| Field | Value |
| --- | --- |
| Title | The frame loop |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `core/first-frame`, `basics/threads` |
| From | foundation "The frame loop" (§1.2: `Run`, `RunFrame`, skipping, work time, `SubmitToMainThread`, `FramePacer`, timers, shutdown; §1.6: `SleepUntil`) |
| Unit | `plan/allocation/core.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `core/frame-loop` — The frame loop

**Covers.** The job: what one turn of Strata's main loop does, in what order, what it counts and how it waits. The
problem section is the part's full one for the loop: why games loop instead of waiting for events as a desktop program
does (the world changes without input); the stages of a frame and why their order matters (input before the update, the
UI after it, presenting last); frame pacing (vsync and the FIFO present mode, caps for headless runs, bursts that catch
up, and why a frame's time must not include its waits). The map is one frame on a time line. The contract, in order:
`Run` (the wall clock, the step clamped to `MaxTimestep`, whose reason is `core/time`'s, a `try` and `catch` around the
frame, in which an escaping exception logs a critical line and ends the loop in order while nothing sets the exit code,
so the program exits with 0, an absence of "What Strata does not do"; the frame counted only when it ran, `MaxFrames`,
the interrupt polled, the pacer's wait); `RunFrame` (the main-thread queue drained; the Input stage, in which the
window's events arrive; a minimized window's frame skipped with a 16 ms sleep and not counted; the modules'
`OnBeginFrame` with Continue, Skip or Close; the layers' `OnUpdate`, then the modules' `OnUpdate` and `OnRenderUI`; the
work time measured; `OnEndFrame` in reverse, where the image is presented, the term Present linked to
`gpu/how-a-gpu-frame-works`); the work time (`GetLastFrameWorkTime`: the frame without what modules wait for and without
stages outside the work time, with its term) and the rule that modules report their waits; `SubmitToMainThread` (a queue
under a mutex, drained at the start of every frame and once after the last); `FramePacer` and `SetMaxFrameRate` (a fixed
schedule without bursts, changed while running; the editor's idle throttling uses it) and the promise of
`Platform::SleepUntil`; `Timer`, `Time::GetTime` and `Timestep`; the shutdown order in `Run` and in the destructor. The
module hooks and the layers are named as what the loop calls; their contracts follow on `core/windows-events` and
`core/engine-modules`. The toy is a loop of 50 lines; the real code is `Run`, `RunFrame` and `FramePacer`. The exercise
traces one frame of the editor with breakpoints. At the end the reader can say what runs in a frame and in which order,
why a frame is skipped or not counted, and what the frame's work time leaves out.

**Leaves out.**

- Delta time, the fixed step and time scale → `core/time`
- Events, the window and the layer stack → `core/windows-events`
- The module hooks' contracts and their order → `core/engine-modules`
- How the GPU frame is begun, waited for and presented → `gpu/vulkan-nvrhi`
- Frames in flight, and the term Present → `gpu/how-a-gpu-frame-works`
- How each OS sleeps until a deadline → `core/platform`
- The frame profiler and its stages → `core/profiling`
- The editor's idle throttling and its preferences → `editor-ui/status`

**Fit.** `fits`: about 4,400 words against L (5,000). The problem section's three concepts and the contract of `Run` and
`RunFrame` with three quotes take the most; the missing failure exit code takes one paragraph.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `foundation:214` | concept | home | The game loop: why games loop, and its general forms |
| `foundation:220` | concept | home | The stages of a frame and why their order matters |
| `foundation:234` | concept | home | Frame pacing and vsync: present modes, caps for headless runs, schedules without catch-up bursts, a frame's time without its waits; the precision of sleeping is named, and taught on `core/platform` |
| `foundation:46` | feature | home | `Run` and `RunFrame`; with the `Run` excerpt, one sentence on an exception that escapes a frame: the critical line, the ordered end, and exit code 0, since nothing sets another (`new:24`) |
| `foundation:47` | feature | home | Frame skipping: a minimized window or a module's Skip sleeps 16 ms and is not counted |
| `foundation:48` | feature | home | The frame's work time and what it leaves out |
| `editor-ui:779` | term | home | Frame work time, the CPU time a frame costs without its waits: one entry with `foundation:582` (work time), beside its feature `foundation:48`, passed by `editor-ui` (the merge "Frame work time"); `editor-ui/status` links it |
| `foundation:49` | feature | home | `SubmitToMainThread` and its queue |
| `foundation:52` | feature | home | The shutdown order, in `Run` and in the destructor |
| `foundation:54` | feature | home | `FramePacer` and `SetMaxFrameRate`; the editor's idle throttling as one user |
| `foundation:55` | feature | home | `Timer`, `Time::GetTime` (double seconds since the start) and `Timestep` (float seconds) |
| `foundation:344` | code | home | `Strata/src/Strata/Core/Application.cpp:226-283`: `Run`: the clamped step, the `try` and `catch`, the frame count, the interrupt, the pacer and the ordered end |
| `foundation:345` | code | home | `Strata/src/Strata/Core/Application.cpp:285-344`: `RunFrame`: the queue, the Input stage, the skipped frame, the hooks' order, the work time |
| `foundation:363` | code | home | `Strata/src/Strata/Core/Timer.h:51-104`: `FramePacer`, a fixed schedule without catch-up bursts |
| `foundation:395` | figure | home | One frame on a time line, the waits shaded, a brace over what `GetLastFrameWorkTime` counts |
| `foundation:463` | rule | home | Report waits in `EngineFrame::WaitSeconds`, and time waits outside the work time as stages outside it |
| `foundation:514` | hands-on | home | Trace a frame: breakpoints in `Application::RunFrame` and in the built-in modules' hooks, the order written down and compared with the code |
| `foundation:570` | term | home | Frame loop, also called game loop |
| `foundation:578` | term | home | Two entries: frame pacing and frame-rate cap |
| `foundation:579` | term | home | Two entries: vsync and the FIFO present mode |
| `foundation:582` | term | home | Work time |
| `foundation:588` | term | home | Main thread |
| `foundation:589` | term | home | Main-thread queue |
| `render-core:55` | feature | home | The frame's order as the renderer's inventory states it (the Graphics module's `OnBeginFrame`, ImGui's `OnRenderUI` with `PrepareBackBuffer`, the present in `OnEndFrame`), taught with the loop that runs it |
| `foundation:183` | feature | use | The clamp of the step to 0.25 s, seen in `Run`; why it exists is `core/time`'s |
| `foundation:112` | feature | use | `Platform::SleepUntil`, as the pacer's promise; its implementations are `core/platform`'s |
| `foundation:569` | term | link | Frame, whose entry is `start/what-an-engine-is`' |
| `foundation:581` | term | link | Present, named where `OnEndFrame` presents the image; its entry is `gpu/how-a-gpu-frame-works`' (R31, Present) |
| `new:24` | not-done | home | No failure exit code after an exception leaves the frame loop: `Run` catches it, logs a critical line and ends in order, and nothing sets the exit code, so the program exits with 0 unless a layer set another code; no test covers the path. One paragraph by book.md's rule 1, beside the sentence of `foundation:46`; the page says what the pin does, and the fix asked of the engine (pipelines.md §11; R34, R47) is not the page's. Evidence: `Strata/src/Strata/Core/Application.cpp:243-253`; `Strata/src/Strata/Engine/EntryPoint.h:35-36`; `git grep -n "Unhandled exception" 822a7a46 -- StrataTests` finds nothing |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The startup, `ApplicationSpecification` and the `Application` | `core/first-frame` | must |
| Threads and mutexes | `basics/threads` | must |
| `std::function` and lambdas | `basics/cpp-generic` | must |
| `std::span` | `basics/cpp-modern` | helps |
| Reverse iterators | `basics/cpp-generic` | helps |
| The frame map: the CPU prepares a frame while the GPU draws the one before | `start/what-an-engine-is` | must |
| Breakpoints and stepping, for the exercise | `basics/debugging` | must |
| Events and the layer stack | `core/windows-events` | helps |
| The module hooks | `core/engine-modules` | helps |
| Frames in flight and the wait for vsync | `gpu/how-a-gpu-frame-works` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `fifo-present-mode` | FIFO present mode | FIFO present modes |
| `frame` | frame | - |
| `frame-pacing` | frame pacing | - |
| `frame-rate` | frame rate | frames per second, FPS |
| `frame-rate-cap` | frame-rate cap | frame rate cap |
| `main-thread-queue` | Main-thread queue | - |
| `vsync` | vsync | vertical synchronization, V-sync |
| `work-time` | Work time | Frame work time |
