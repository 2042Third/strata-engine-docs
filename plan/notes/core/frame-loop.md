# Notes: `core/frame-loop`

## New terms

- **frame loop**: a loop that repeats frames until the program closes. Home: `core/frame-loop`. Aliases: frame
  loops. (The glossary already holds "game loop", homed at `start/what-an-engine-is`, while the brief homes "Frame
  loop, also called game loop" here: the planner decides whether "frame loop" joins that entry as an alias.)
- **frame pacing**: deciding when each frame may start, so that frames come at a steady rate. Home: `core/frame-loop`.
- **vsync**: handing a finished image to the display only when the display starts its next refresh. Home:
  `core/frame-loop`. Aliases: vertical synchronization, V-sync.
- **FIFO present mode**: the present mode in which finished images wait in a line, first in, first out, and the
  display takes one at each refresh; the mode that gives vsync. Home: `core/frame-loop`. Aliases: FIFO present
  modes. (markterms marks "FIFO" itself as the glossary's `queue`, so FIFO is not proposed as an alias.)
- **frame-rate cap**: a highest frame rate that a loop does not exceed. Home: `core/frame-loop`. Aliases: frame rate
  cap, cap.

The page also defines the glossary's own entries homed here: frame, main thread, main-thread queue, work time (with
"frame work time" in the text), frame rate.

## Requests

- `breakpoint` (and plural): a term the closure assumes (`basics/debugging`, "Breakpoints and stepping", depth must),
  but the glossary has no entry markterms finds; please add it with home `basics/debugging`. The word-list findings
  for "breakpoint" and "breakpoints" are left until then.
- `tools/data/names.txt`: Robert Nystrom, Glenn Fiedler (authors named in Further reading). The word-list findings
  for "Robert", "Nystrom", "Glenn" and "Fiedler" are left until then.
- `vsync`: proposed above under New terms; its word-list finding is left until the term exists.

## Since

`since: 0.3.0`, the earliest release the field allows. `Application::Run` exists since the engine's first commit
(`a0f2865f`, "Add build system, pinned dependencies and engine core"); `FramePacer` came with `d9116fc5` ("Pace the
frames of headless applications"), which `v0.3.0` contains. Later changes: the drain after the loop (`60a197ed`, in
`v0.4.0`), the display wait at the first use of the back buffer outside the work time (`61e2384e`, in `v0.4.0`), and
`Platform::SleepUntil` for the pacer (`bb1e5299`, after `v0.7.0`, so in 0.8.0). At 0.8.0 an exception that leaves a
frame sets exit code 1 (`Application::c_UnhandledExceptionExitCode`; release notes, Fixes); the page's former section
"What Strata does not do: a failure exit code" became "A failure in a frame and the exit code", and the test case of
`ApplicationFrameTests.cpp` joined "How it is tested".

## Not verified

- The figure `frame-timeline` uses example numbers chosen to add up (the page says so); they are not a measurement.
- The table of alternatives and Further reading cite other engines and documents from general knowledge; the URLs were
  not opened in this session: Godot's `OS.low_processor_usage_mode`, Unreal Engine's game thread and rendering thread
  ("Threaded Rendering"), Microsoft's `timeBeginPeriod` page (its note on Windows 10 version 2004), the Vulkan
  specification's `VkPresentModeKHR`, Game Programming Patterns and Gaffer on Games.
- "On Windows it wakes within about 1 ms" comes from the comments of `Platform.h` and `Timer.h` and the measurements in
  commit `bb1e5299`, not from a run in this session.
- The macOS numbers in "What went wrong before" (7.3 ms, 0.41 ms, 7.41 ms, 0.91 ms) come from the message of commit
  `61e2384e`; the exit code 139 from commit `60a197ed`.
- The exercise "trace it yourself" was not run with a debugger; the stop order follows the code of `RunFrame`, the
  editor's module list (`StrataEditor/src/EditorApplication.cpp` 332-345) and the hooks each built-in module overrides.

## Findings not applied

- The brief lists `foundation:569` (Frame) as a link to `start/what-an-engine-is`, but the lint reports this page as
  the home of "frame" and asks for its definition; the page follows the lint and defines it.
- The brief's figure `foundation:395` is drawn as an SVG of my own (`src/assets/figures/core/frame-loop/frame-timeline.svg`)
  rather than taken; the brace is drawn as brackets over the two runs of work.

## Clerk

- Admitted (`plan/glossary/admitted.json`): "frame pacing", "vsync" (aliases vertical synchronization, V-sync), "FIFO
  present mode", "frame-rate cap" (alias frame rate cap; "cap" dropped as one everyday word).
- Refused: "frame loop": the glossary holds it as an alias of "game loop", homed on `start/what-an-engine-is`; which
  page homes the entry is the planner's.
- "breakpoint": no request needed; the glossary has it, homed on `basics/debugging`.
- `tools/data/names.txt`: Robert Nystrom, Glenn Fiedler added.

## Track walk E-final-6

Checks in `docs-work/walkfix-E6`, 2026-11-24, with the official 0.8.0 package and the pin clone's `build/docs-patch`, under the perf lock; no editor left running, the clone clean afterwards.

- WK1, WK6: a paragraph after the introduction says that the page needs no project and no download, that the toy is a
  program for the compiler of How a C++ program is built, that the one editor command runs with the installed Strata,
  and that the test commands and the trace need the source build of Your first engine change; How it is tested says
  "in the folder of your source build".
- WK3: `StrataEditor --no-gpu --frames 3 --screenshot x.png | Out-Host` in the package folder (with and without
  `--no-automation`) logs `[error] App: Screenshot failed: Image is empty`, shuts down in order and sets
  `$LASTEXITCODE` to 1 in 0.15 s; no PNG is written. That is the intended result: the pin's ctest
  `StrataEditor.ScreenshotWithoutGPU` (`StrataTests/CMakeLists.txt:505-512`) expects that line and a failing exit
  code. The page now says so. Not an engine fault.
- WK8: `FramePacer::WaitForNextFrame` (`Strata/src/Strata/Core/Timer.h:91-95`) places the first slot
  one period after the call, as the toy's line 74 does. The frame-rate cap section, the toy's callout 5 and the
  `FramePacer` callout 3 now say so.
- Words cut to stay within size L: the 16 ms paragraph, the `float` paragraph, the macOS paragraph and four short
  sentences.
