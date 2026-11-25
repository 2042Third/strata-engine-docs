# Walk E-final-6: track E (engine builder, persona E1), segment 6

Entries walked: `core/frame-loop`, `core/time`, `core/windows-events`, `core/engine-modules`, `core/layers-registries`, `core/jobs`.
Package: Strata 0.8.0 Windows x64 (official package from `docs-package-0.8.0`: StrataEditor, StrataCLI; every engine program run under the perf lock).
Book: the built site at 127.0.0.1:4329; engine source read at 319075e3 in `docs-pin` (read only, through `git show` and `git apply --check`).
Work folder: `G:/GameEngineAI/.worktrees/docs-work/walk-E-final-6/` (page texts and HTML, `sk/` the extracted sketches and their outputs, `run1.ps1` to `run3.ps1` with `run-out/`, `cli-out/`, `cli-out2/`, `prm/` the program runs, `PhysicsPlayground/` the sample copy, `dl/` the page's patch).

How the walk went: every page read to the end. Checked and equal: 38 quoted engine excerpts (data-source and line range) against the file at 319075e3; all 12 sketches extracted from the pages, compiled with g++ 15 `-std=c++20 -Wall -Wextra -pthread` (no warning) and run, every "Output of the sketch" block equal to the real output, the "Line N" notes of the frame-loop and jobs-last-ref sketches equal to the numbered lines; the answers of the exercises that can be computed (frame-loop Basic with c_Period 10: turns at 0, 19, 29, 45 ms; engine-modules Basic (a) and (c) and Check yourself 1 through the toy with edited tables; jobs Basic and Check yourself ParallelFor numbers; the time accumulator and spiral tables); Layers.json against the page's 19-row table and the "13 layers" of Engine; the pool-size table of jobs against `GetDefaultBackgroundThreadCount` and, on this 24-thread machine, the package's log line "23 worker threads, 2 I/O threads, 20 background threads"; the module list and the six scene systems of `Engine::RegisterBuiltinModules` against the package's startup log; the cap table of time (30 steps a second gives a cap of 4, 240 gives 32) with `project.setSettings` and `scene.info` on a copy of the Physics Playground (cap 4 and 32, steps per second 30 and 240, 34 and 260 fixed steps in about 60 frames of play, mean frame work time 1.0 ms against 5.3 ms); the 15 event types, the five Layer hooks, the ten cursor shapes; the exercise-1 patch of engine-modules (`git apply --check` passes on the pin).

Not walked: every step that needs a source build (the `StrataTests.exe --test-suite=...` commands of the "How it is tested" sections; no test program is in the package), every "Trace it yourself" exercise (Debug build, breakpoints; no IDE or debugger), the Hard exercise of windows-events, the Medium exercise of engine-modules (patch checked, not built), the Medium exercise 1 of time (a GUI preference), the Linux and macOS tabs.

Side steps: none to other book pages. The "Definition of ..." popups and the links to primers were not followed.

## WK1
- Entry: `core/frame-loop` (and the same on the five others)
- Page: `core/frame-loop`
- Step or section: the start of the entry ("What you need", the stage download)
- What happened: the task for this segment says to start at the page's "What you need" section and the stage download it offers a reader who arrives there. None of the six pages has either. Each has a "Before you start" list (frame-loop: From main to the first frame, Threads, atomics and races; time: The frame loop, Change over time; the others one earlier page) and a note "Level 2: also needs the engine's core (parts 3 to 5) or earlier pages of this part". The only download on the six pages is the solution patch of the engine-modules Medium exercise. A reader who arrives from the start pages gets no project or code stage to start from; every step here needed only the sketches (copied from the page) and the package.
- Kind: did not match

## WK2
- Entry: `core/time`
- Page: `core/time`
- Step or section: "Drawing between steps hides the step's rhythm" and "What Strata's choice cannot do"
- What happened: the first says interpolation costs "one step of latency: the picture always shows a moment one step behind the simulation" and that Strata draws "a constant one step behind"; the second says it "adds latency of half a step on average, about 8 ms at 60 steps a second". I could not tell which number is right (16.7 ms or about 8 ms), and the page gives no reason that would make half a step an average. I took the first as the fixed offset and guessed that the second counts something else.
- Kind: guessed

## WK3
- Entry: `core/frame-loop`
- Page: `core/frame-loop`
- Step or section: "What went wrong before", the command `StrataEditor --no-gpu --frames 3 --screenshot x.png`
- What happened: the page says that before the fix the command logged that the screenshot failed and crashed with exit code 139, and that since then Run drains the queue. It does not say what the command does now. I ran it on the 0.8.0 package (with `--no-automation` added): it logs `[error] App: Screenshot failed: Image is empty`, shuts the audio engine down and ends with exit code 1, no crash. With no statement of the expected outcome I had to guess that the error line and exit code 1 are the intended result for a program with no graphics device and not a remaining bug.
- Kind: guessed

## WK4
- Entry: `core/time`
- Page: `core/time`
- Step or section: Exercises, Medium 1 (File > Preferences, "Active frame rate" in the Frame Rate section)
- What happened: the exercise is written only for the editor window. The task forbids changing the editor's preferences and the page gives no command tab for it, so I did not do it. The expected numbers (an object that moves per OnUpdate travels a distance that follows the frame rate, one that moves per OnFixedUpdate does not) are only derivable from the page's text; I did not measure them.
- Kind: left the book

## WK5
- Entry: `core/time`
- Page: `core/time`
- Step or section: Exercises, Medium 2 (Physics Playground, Fixed Rate in "the physics Timing section")
- What happened: the exercise says File > Project Settings and "the physics Timing section", while the text of the page and "Where it lives in Strata" call it the `Scene.Timing` section and name `project.setSettings`, without a parameter example. I did it through the CLI on a copy of the sample: `project.setSettings` with section `Scene.Timing` and value `{"FixedRate":"30"}`. I guessed the section id and that the value is the string "30", not the number 30 (the first try with the quotes lost by PowerShell failed with "params must be a JSON object or array" until I used `@file`). `scene.info` then showed `source: project`, cap 4 (30) and 32 (240); `play.state` after `play.start` and `editor.wait` of 60 frames showed 34 and 260 fixed steps, and the mean frame work time rose from 1.0 ms to 5.3 ms at 240. This agrees with the page's cap table and its remark on cost. The crate tower and the keys 1 to 6 were not walked (no window).
- Kind: guessed

## WK6
- Entry: all six
- Page: the "How it is tested" sections (frame-loop, windows-events, engine-modules, layers-registries, jobs) and the exercises that ask for a Debug build or breakpoints (frame-loop Medium; windows-events Medium and Hard; engine-modules Medium (trace); layers-registries Hard; jobs Medium)
- Step or section: the commands `build/windows/bin/Debug/StrataTests.exe --test-suite=...` and the traces
- What happened: they need the source build of "your first change", which the package does not contain (no `StrataTests.exe`), and a debugger. I did not run them. I checked by reading the pin that the test cases, helpers (`MakeStubSpecification`, `RecordingLayer`, `QueueResize`, `QueueContentScale`, `OnProcessEvents`), files and functions that the pages and worked solutions name exist; all do.
- Kind: left the book

## WK7
- Entry: `core/engine-modules`
- Page: `core/engine-modules`
- Step or section: Exercises, Medium (FrameCounterModule) and its download `exercise-1.patch`
- What happened: I downloaded the patch (1,964 bytes) and checked it with `git apply --check` on the pin: it applies cleanly. I did not build or run its test case, so the page's claim "which makes 10 in the suite" is unchecked.
- Kind: left the book

## WK8
- Entry: `core/frame-loop`
- Page: `core/frame-loop`
- Step or section: "A toy version", Basic exercise (c_Period 10)
- What happened: no mismatch: the worked solution's start times (0, 19, 29, 45 ms) equal the output of the edited sketch. Recorded because a reader who predicts turn 2 at 10 ms is wrong, and nothing before the exercise says that the first slot starts one period after the end of the first frame (9 + 10 = 19). I predicted 10 first and had to read line 74 of the toy to see why.
- Kind: guessed

## Observation, not a book defect
The worktree `docs-pin` has uncommitted changes (`git status` shows Docs/Architecture.md and Strata/src/Strata/Physics/PhysicsComponents.* modified). All comparisons used `git show HEAD:<path>` or files those changes do not touch; the patch check of WK7 ran against the working tree, where EngineModuleTests.cpp is unmodified.

## Answers

Checks were run under the perf lock in `docs-work/walkfix-E6`, 2026-11-24, with the official 0.8.0 package (`shot.ps1`,
`timing.ps1` and their `.out`) and the pin clone's `build/docs-patch` (`patch/`, `patch.out`). No editor was left
running, and the clone is clean. The log lists no patches under "## Built by the integrator". The one tutorial file
that changed, the new `tutorials/core/engine-modules.tutorial.json`, is a file for an engine exercise, which
`tutorials.py run` does not take; `tutorials.py patch core/engine-modules` passed (WK7). No engine fault was found, so
no page got an `## Engine` note; each page's notes have a section "Track walk E-final-6". Every changed page passes
`tools/pagecheck.py`.

### WK1
- Fixed on all six pages. Why: concept and internals pages have no "What you need" and no stage download by the
  book's style (style.md §7.4 gives them to tutorials, as the answers of E-final-1 to E-final-5, E-final-8 and E-final-9
  say), but none of the six said in words that it needs no project, nor which programs its parts use.
- Change: a paragraph after the introduction of each page says that the page needs no project and no download, that
  its sketches are whole programs for the compiler of How a C++ program is built (linked to "Open a terminal that
  finds a compiler"), and that its test commands and traces need the source build of Your first engine change, in
  `Debug` (linked to "Build the engine and start the editor"). frame-loop adds that its one editor command runs with
  the installed Strata; time names its two editor exercises (a project of your own, a copy of the Physics Playground
  from **Open Sample...**); engine-modules names the patch of exercise 2. Words were cut on frame-loop and jobs to stay
  within size L.

### WK2
- Fixed on `core/time`. Why: both numbers are true, of two marks, and the page did not say so; the first section also
  called the clock "the simulation". At the pin the drawn moment is T + a - h for the newest step T, the step h and
  the accumulator a (`Strata/src/Strata/Scene/Scene.cpp`, the end of the fixed steps in `OnUpdateRuntime`): a constant
  one step behind the clock, and h - a behind the newest step, which is 0 to one step, half a step on average.
- Change: "Drawing between steps" says that latency can be counted in two ways: one step behind the game's clock and,
  for the newest step, 0 to one step later than a picture of it, half a step on average, about 8 ms at 60 steps a
  second. "What Strata's choice cannot do" says the same in one sentence. Exercise 3's answer said that a higher rate
  "halves" the latency; it now gives half a step at 30 and 240 (about 17 ms and 2 ms).

### WK3
- Fixed on `core/frame-loop`. Why: the page gave the old result only. Measured with the package in PowerShell:
  `.\StrataEditor.exe --no-gpu --frames 3 --screenshot x.png | Out-Host`, with and without `--no-automation`, logs
  `[error] App: Screenshot failed: Image is empty`, shuts down in order and sets `$LASTEXITCODE` to 1 (0.15 s); no PNG.
  That is the intended result: the pin's ctest `StrataEditor.ScreenshotWithoutGPU` (`StrataTests/CMakeLists.txt:505-512`)
  runs that command and expects that line and a failing exit code.
- Change: "What went wrong before" now says that the command still logs that line, since without a graphics card
  there is no image, then ends in order with exit code 1, as the engine's test `StrataEditor.ScreenshotWithoutGPU`
  expects, and that PowerShell needs `| Out-Host` and `$LASTEXITCODE`.

### WK4
- Fixed on `core/time`. Why: the Frame Rate preferences apply only to an editor with a window; the section's own
  description says that headless, `--frames` and command-script runs ignore it
  (`StrataEditor/src/Editor/EditorFrameRate.cpp`), so no command tab can do the step. The walker's rule forbids
  preferences; a reader may change them, but the exercise did not say that the numbers are a prediction first, nor how
  to restore the setting.
- Change: exercise 2 asks to predict the distances at 60 and 240 frames a second, then says that the check needs the
  editor with a window, that the setting is the person's own and has no command, and to set **Active frame rate**
  back to **Unlimited**, its default. The worked solution is unchanged (30 m and 120 m; 30 m both times).

### WK5
- Fixed on `core/time`. Why: the exercise named only the window's labels, and the page gave `project.setSettings`
  without parameters; the settings page **Timing** of the **Physics** category is the section `Scene.Timing`, and
  **Fixed Rate** is a list of choices whose value is text.
- Change: exercise 3 has two tabs. In the editor: **File ▸ Project Settings...**, the **Physics** category, its
  **Timing** page, the **Fixed Rate** list. With a command: the section's id, that the value is the text `"30"`, the
  PowerShell lines `'{"section": "Scene.Timing", "value": {"FixedRate": "30"}}' | .\StrataCLI call project.setSettings -`
  and `.\StrataCLI call scene.info` (the pipe keeps the quotes that PowerShell 5.1 drops from an argument), a link to
  The editor's commands, what both answers show, `"reset": true`, and the message for the number 30. Run with the
  package on a copy made by `project.openSample`: `FixedRate` "30", `isDefault` false; `scene.info` `source` project,
  30 steps, cap 4, at 240 cap 32; 60 frames of play gave 34 and 259 fixed steps; reset gives `Scene`; the number fails
  with `'FixedRate' must be one of 'Scene', '30', '60', '120', '240'`. "Where it lives in Strata" names the page and the
  section the same way.

### WK6
- Fixed on all six pages. Why: the steps need the source build, which the package does not hold, and only jobs said
  so at its test command.
- Change: WK1's paragraph names the source build of Your first engine change for the test commands and traces, and the
  "How it is tested" sections of frame-loop, windows-events, engine-modules and layers-registries say that the
  commands run in the folder of that build (jobs already did, now in fewer words). Not run here: the Debug suites and
  the traces need a Debug source build, which `build/docs-patch` (Release) is not; the walker checked that every test
  case, helper and function named exists at the pin.

### WK7
- Checked; the page's claim holds, and the exercise now runs its suite. Why: the exercise patch had no tutorial file
  naming its suite, so `tutorials.py patch` had run only `Architecture.Layering` and the feature test, and "makes 10
  in the suite" was unchecked by the book's tools too.
- Change: `tutorials/core/engine-modules.tutorial.json` starts from `core/first-change` (the reader's clone) and names
  `Core.EngineModules` for exercise 1's patch. `tutorials.py patch core/engine-modules` in `build/docs-patch`,
  configured after applying: `Core.EngineModules` 10 test cases, 10 passed (`[doctest] Status: SUCCESS!`), as the
  worked solution says; `Architecture.Layering` 18 and the feature test passed; stamps
  `tutorials/core/engine-modules.stamp.json` and `exercise-1.stamp.json`. The patch was reverted and the clone is
  clean.

### WK8
- Fixed on `core/frame-loop`. Why: the rule was in the code (`FramePacer::WaitForNextFrame`, `Timer.h:91-95`, and the
  toy's line 74) but nowhere in the prose before the exercise.
- Change: "The frame-rate cap" says that the first wait has no last slot, so it sleeps one whole period from the moment
  the frame ended, and so does the first wait after a new rate. The toy's callout 5 says that the first slot lies one
  period after turn 1 ends at 9 ms, so turn 2 starts at 29 ms; the `FramePacer` callout 3 covers lines 85 to 95 and
  says that a wait with no schedule places its slot one period after now.

### Steps for the confirming walker
- From the start of each of the six pages: read the paragraph after the introduction (WK1, WK6).
- `core/time`: "Drawing between steps" and "What Strata's choice cannot do" (WK2); exercise 2 (WK4); exercise 3's
  "With a command" tab on a copy of the Physics Playground with the package, both lines and the 240 run (WK5).
- `core/frame-loop`: "What went wrong before", running the command with the package in PowerShell with `| Out-Host`
  and reading `$LASTEXITCODE` (WK3); "The frame-rate cap", the toy's callout 5, then the Basic exercise, predicting
  before running (WK8).
- `core/engine-modules`: exercise 2's patch, built by the integrator with `tutorials.py patch core/engine-modules`
  (WK7).

## Confirm

Run 2026-11-24 with the 0.8.0 package under the perf lock (`docs-work/walk-E-final-6/v/`: `run5.ps1`, `shot.ps1`, `out/`, `toy.cpp`);
no editor or game left running.

Side step, logged: the served book at 127.0.0.1:4329 is the build of 18:53, before the fixes (commit 19:29); its pages lack the new
paragraphs (`curl` of `core/time` finds no "needs no download"). I read the pages as the fixed sources
`src/content/docs/core/*.md`. The integrator must rebuild the preview before a reader sees the fixes there.

- WK1: confirmed. On all six pages the paragraph after the introduction says: no project, no download (time: no download), the
  sketches are whole programs for the compiler of "How a C++ program is built", and the test commands and traces need the
  source build of "your first engine change" in `Debug`; the two link anchors exist (`build.md` "Open a terminal that finds a
  compiler", `first-change.md` "Build the engine and start the editor"). I got through without guessing.
- WK2: confirmed. "Drawing between steps" and "What Strata's choice cannot do" now agree: one step behind the game's clock, and
  the newest step 0 to one step later, half a step on average, about 8 ms at 60 steps a second; the exercise 3 answer (17 ms at
  30, 2 ms at 240) is consistent.
- WK3: confirmed. `.\StrataEditor.exe --no-gpu --frames 3 --screenshot x.png | Out-Host` logs `[error] App: Screenshot failed:
  Image is empty`, shuts down in order, `$LASTEXITCODE` is 1, no PNG: what the page says.
- WK4: confirmed. Exercise 2 asks for a prediction first (30 m and 120 m; 30 m and 30 m), says the check needs a window, that
  the setting is the reader's own and has no command, and how to restore it. No command is offered for the windowed check. I did
  not run the windowed check (no window).
- WK5: confirmed. On a new copy (`project.openSample`) the two tab lines as written in PowerShell worked: `FixedRate` "30",
  `isDefault` false; `scene.info` `source` project, `stepsPerSecond` 30, `maxFixedSteps` 4; 240 gives 32; the number 30 fails
  with `'FixedRate' must be one of 'Scene', '30', '60', '120', '240'`; `"reset": true` gives `Scene`, `isDefault` true. All equal to the
  page. Minor: the tab does not say how to get the copy open in the editor from a command (`project.openSample` with `sample` and
  `directory`); a command reader who does not know it must look in the editor's commands page (no mismatch, a small gap).
- WK6: confirmed. The same paragraph, and the "How it is tested" sections of frame-loop, windows-events, engine-modules,
  layers-registries and jobs say that the commands run in the folder of the source build; no reader is left to guess.
- WK7: confirmed from the integrator's stamp, not run by me (no source build):
  `tutorials/core/engine-modules/exercise-1.stamp.json` holds `Core.EngineModules` 10 test cases passed, `Architecture.Layering`
  18, the feature test passed, with hashes equal to the current tutorial file.
- WK8: confirmed. "The frame-rate cap" now says the first wait sleeps one whole period from the end of the frame; the toy's
  callout 5 says turn 2 starts at 29 ms. I predicted 19 ms for c_Period 10 from that text, ran the toy edited to 10: turns start
  at 0, 19, 29 and 45 ms, equal to the worked solution.
