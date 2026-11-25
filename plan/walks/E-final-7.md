# Walk E-final-7: track E (engine builder, persona E1), segment 7

Entries walked: `core/platform`, `core/files`, `core/profiling`, `core/debugging`, `core/math`.
Package: Strata 0.8.0 Windows x64 (official package from `docs-package-0.8.0`: StrataEditor, StrataCLI; every engine program run under the perf lock). Book: the built site at 127.0.0.1:4329, engine source only as the pages quote it (read in `docs-pin` at 319075e3).
Work folder: `G:/GameEngineAI/.worktrees/docs-work/walk-E-final-7/` (page texts and HTML, `sk/` the 13 extracted sketches, `h1/` `h2/` `h3/` the editor and test runs, `hold1.ps1` `hold2.ps1` `hold3.ps1` the scripts run under the lock, `killloop.py` the page's script).

How the walk went: every page read in full. All 13 sketches (4 platform, 2 files, 3 profiling, 2 debugging, 2 math) were taken from the pages' copy buttons, compiled with g++ `-std=c++20 -Wall -Wextra` (glm from the pin's vendor folder for the two math sketches) and run: no warnings, and every output equals the page's output. The "Lines N-M" notes of the sketches and of the engine excerpts match the code (the quoted blocks on the page leave out the blank lines the file has; the notes count the file's lines, which is right). `DecomposeTransform` copied from the pin gives (-1, 1, 1) and a half turn about Z for a Y mirror and false with outputs untouched for a zero matrix, as the page says. Check-yourself and exercise answers recomputed by hand (frame times, ring numbers 905, 5,905, 7,905, 904 lost, self times, 90 % rule, depths 0.125 and 0.000125): all as printed. The five stage files of the profiling Hard exercise and `MakeViewRay`'s three files exist as named; `Render.Extract` is timed in ten places; `ST_PROFILE_THREAD` has no caller; capacity 600, 64 stages, depth 32, share 0.9, queue 65,536 and ring 4,096 equal the code.
Editor runs (one lock hold each, no editor left running): `StrataEditor --version`, `--headless --frames 120` piped to Out-Host (log lines, order and the 2.2 s match the platform page's capture), the same without a pipe, a headless project session driven by StrataCLI (`editor.status` with the memory section, `editor.perf`, `log.read`, `play.start`).
Test program: no Debug build exists for a reader here, so the suites were run from the pin's prebuilt Release `StrataTests.exe`: Core.Platform 52, Core.Log 9, Core.FrameProfiler 19, Math 11, Core.BoundedRead 3, Core.FileSystem 16, Core.AtomicFileWriter 3, Editor.Perf 2 test cases, all passed; `STRATA_TEST_TRACE=1` printed `[test case] <suite> / <name>` lines as the debugging page says.

Not walked: building from source (Debug presets, Visual Studio, gdb, lldb), so the debugging page's worked example (adding the failing test case, the stop at the assert, the Locals window), the platform page's Medium and Hard exercises (trace and `GetHostName`), the profiling page's Tracy exercise and the "Changing it safely" test runs; Ctrl+C steps of the platform page (no terminal that can send Ctrl+C) and the second-Ctrl+C behavior; the Linux and macOS tabs; the Hard exercise of core/debugging (breakpoints). `EndToEnd.StandardStreams` could not pass in the prebuilt tree (it has no StrataRuntime.exe: "is not built"); that is the tree, not the book.
Side steps: the primer pages were not opened. I opened `make/with-an-agent` and `start/install` to learn how a CLI reaches an editor (`StrataCLI launch`, session file). I used the prebuilt Release test program of `docs-pin/build/docs-patch` in place of the Debug build the pages show. I looked at the pin's source for facts the pages state (listed above).

## WK1
- Entry: `core/platform` (and the four after it)
- Page: Talking to the operating system; Files you can trust; Measuring the frame; Debugging the engine; Strata's math toolkit
- Step or section: the start of the entry ("What you need", stage download)
- Kind: guessed
- What happened: the task says a reader starts at the "What you need" section of the first entry and may take the stage download for it. None of the five pages has a "What you need" section or a download: each has only "Before you start", a list of earlier pages (`core/platform`: Threads and the job system). I took the installed package for the programs and the pin for the source, and walked on; nothing on the page says what a reader who arrives here has built or installed (core/debugging and its exercises say a Debug build "as in your first engine change").

## WK2
- Entry: `core/profiling`
- Page: Measuring the frame: the frame profiler, Tracy and the method
- Step or section: "A stage of your own", the command `StrataCLI call editor.perf '{"frames": 120}'`
- Kind: failed
- What happened: in Windows PowerShell 5.1 (the persona's terminal on Windows) the command as written prints `error: params must be a JSON object or array`: PowerShell 5.1 removes the inner double quotes of a single-quoted argument it passes to a program. The same happened with the `log.read` parameters of `core/debugging` ("The log as a tool", `{ "after": 120, "minLevel": "Warn", ... }`, shown as bare JSON without a command line, so I used the same form). With the JSON piped (`'{"frames": 120}' | StrataCLI call editor.perf -`, the form of `make/with-an-agent`) both work. The page does not say which form to use on Windows.

## WK3
- Entry: `core/platform`
- Page: Talking to the operating system
- Step or section: "Why PowerShell does not wait" and Check yourself, question 2
- Kind: did not match
- What happened: `StrataEditor.exe --headless --frames 10` without a pipe returned to the prompt after 0.06 s, as the page says, but `$LASTEXITCODE` then read 0 (the value left by the command before), not "no answer yet": a reader who checks it reads 0 as success for a run that was still going. `Start-Process -Wait -PassThru` gave `ExitCode` 0 after the run, as the page says. The page's wording ("has no answer yet") does not match what PowerShell shows.

## WK4
- Entry: `core/files`
- Page: Files you can trust
- Step or section: Medium exercise, worked solution (`python -I killloop.py run`)
- Kind: failed
- What happened: I took the script from the page and ran it three times on Windows (Python 3 of MSYS2, in an empty folder). Two runs ended with `PermissionError: [WinError 5] Access is denied: 'payload.bin.tmp'` at `os.remove(name)` (line 30, the clean-up at the start of a round, after the previous round killed the child while it held the temporary file); the third printed `inplace damaged: 2 of 40` and `atomic damaged: 0 of 40`, as the page's statement (in-place damaged, atomic never) leads one to expect. The script has no retry or `try` around `os.remove`, so on Windows it often stops before its answer.

## WK5
- Entry: `core/profiling`
- Page: Measuring the frame: the frame profiler, Tracy and the method
- Step or section: "A stage of your own", the text figure "the result of the editor command `editor.perf`" and its notes
- Kind: did not match
- What happened: the figure lists one stage and the note says "this answer lists only `Scene.Physics`". The real answer of the package (headless editor, project PhysicsPlayground, playing, 120 frames) lists all 17 stages of the main thread (the twelve and the five the page names) and has the fields `frames`, `framesPerSecond`, `frame`, `interval`, `stageSum`, `untimed`, `stages`, `jobs`, `gpu`, `gameRenderStats`, `renderStats`; the text before the figure names `frame`, `interval`, `stageSum`, `untimed`, `stages`, `jobs` and `gpu` but not `framesPerSecond`, `gameRenderStats` or `renderStats`, and the figure drops `untimed`, `jobs` and `gpu` without saying that it is cut. In a headless editor `gpu.boundBy` read `unknown` (first call: `capped`), which the page explains only as "no GPU times". Also the call asked for 120 frames and the first answer covered 55 (the editor had run for that long): the page says "at most 600" but not that fewer is answered.

## Answers

No patches are listed under "## Built by the integrator", and none of the five pages has a tutorial file, so no
`tutorials.py run` or `patch` applies. Every changed page passes `tools/pagecheck.py`. The PowerShell steps were rerun
with the official v0.8.0 package in Windows PowerShell 5.1, in one hold of the perf lock
(`docs-work/walkfix-E-final-7`, `hold.ps1`, the answers beside it); the editor this run started quit, and the pin
clone is untouched. No engine fault was found.

### core/platform (and the four after it)

- **WK1** rejected. "What you need" and a stage download belong to tutorial and how-to pages (`plan/card/kind-T.md`,
  `kind-H.md`); the five pages are internals pages, which the card `kind-I.md` gives none. Their start is the track's:
  Before you start leads every one of them back through `core/jobs` ... `core/conventions` to `core/first-change`
  (entry 38 of track E), whose tutorial builds the engine from source in Debug, and `core/debugging` names that build
  where it needs it ("a source build, as in your first engine change"). The steps that run a program on these pages
  (`StrataEditor --headless --frames`, `StrataCLI call`) run with that build or with the package alike, as the walk
  showed.

### core/platform

- **WK3** fixed (page). Rerun: after `cmd /c exit 7`, `StrataEditor.exe --headless --frames 10` with nothing piped left
  `$LASTEXITCODE` at 7 right after the call and 6 s later; `Start-Process -Wait -PassThru` gave 0, the piped run 0.
  PowerShell does not touch `$LASTEXITCODE` for a GUI program it did not wait for. "Why PowerShell does not wait" now
  says that `$LASTEXITCODE` keeps the code of the command before, often 0 (the paragraph split in two), and the answer
  of Check yourself 2 says the same.

### core/files

- **WK4** fixed (page). The script of the Medium exercise has two helpers: `read_bytes`, and `patiently`, which tries
  `os.remove` and the read again for up to 5 s while Windows answers `PermissionError` (another program, such as a
  virus scanner, can hold the file for a moment after the killed child ended). The callouts follow the new lines and
  say why the retry is there. Three runs of the page's old script here passed (5, 5 and 6 of 40 in place, 0 atomic),
  three of the new one printed 11, 9 and 12 of 40 in place and 0 atomic; the page now gives "In six runs ... 5 to 12
  damaged files of 40 and the atomic mode none". The script on the page equals the one run (compared byte for byte).

### core/profiling

- **WK2** fixed (page). Rerun in PowerShell 5.1: `StrataCLI call editor.perf '{"frames": 120}'` prints
  `error: params must be a JSON object or array`; `'{"frames": 120}' | StrataCLI call editor.perf -` and
  `StrataCLI call editor.perf '@perf.json'` answer. The command now stands in Windows, Linux and macOS tabs: the
  Windows tab pipes the parameters in and says why (PowerShell 5.1 drops the quotes inside a JSON argument), as
  `start/how-to-read` and `make/commands` do. On `core/debugging` ("The log as a tool") the `log.read` parameters now
  come with the line to send them, `StrataCLI call log.read '@logread.json'`, which works in every shell (rerun:
  answered with `latest`, `messages`, `more`), and the same reason.
- **WK5** fixed (page). The text figure's recipe keeps only `/frames`, `/frame`, `/interval`, `/stageSum` and
  `/stages/Scene.Physics` of the answer, taken in a `--no-gpu` editor (its `gpu.frames` is 0). The sentence before the
  figure now says that the figure is part of the result, which fields it keeps, and that the full result lists every
  stage of the main thread and the other fields; note 5 says that the figure keeps only `Scene.Physics`. The field list
  now names `frames`, `framesPerSecond`, `renderStats` and `gameRenderStats` (the Scene view's and the Game view's
  latest frame, null while a view draws nothing; `EditorStateCommands.cpp`, `editor.perf`), and says that a
  `--headless` editor draws its views only for pictures (`EditorApplication.cpp`, "rendering stays available for
  captures") and a `--no-gpu` one has no device, so both fields are null and `boundBy` reads `unknown` once the frames
  asked for hold no GPU times; the walk's first call read `capped` from 12 earlier GPU frames. The paragraph before
  the command now says that an editor that recorded fewer frames answers with fewer and `frames` says how many (the
  walk's 55 of 120).

## Confirm

Segment 7 confirm walk (persona E1, Windows PowerShell 5.1.26100, the v0.8.0 package, one perf-lock hold per step).
Important for the reader: the preview served at port 4329 was built from `site/preview` at 17:51 and does not hold the
answer commits (0fbcdbef to 9eb543d2) of this walk's fixes. Its core/platform still says "`$LASTEXITCODE` has no answer
yet", its Check yourself 2 does not mention the old code, and it was not rebuilt by this confirm walk. The fixed
text was read from `src/content/docs/core/*.md` of `book/write`. Rebuild the preview (`scripts/preview.ps1`) before a
reader looks at it.

- **WK2 holds.** `'{ "frames": 120 }' | StrataCLI call editor.perf -` in a headless editor (`StrataCLI launch --headless`)
  answered JSON at once (fields frame, frames, framesPerSecond, gameRenderStats, gpu, interval, jobs, renderStats,
  stageSum, stages, untimed). `frames` was 6 (the editor had just started; the page now says an editor with fewer
  recorded frames answers with fewer). The page's `log.read` parameters saved as `logread.json`, `StrataCLI call log.read
  '@logread.json'` answered `{"latest": 120, "messages": [], "more": false}`. A reader sees an empty list, because a fresh
  headless editor holds 120 entries and the filter asks for warnings after entry 120; that is correct, but the page's
  "reply holds a list of entries" is only true when a warning came after 120. The editor quit with `editor.quit` (force); no
  process was left.
- **WK3 holds** (as the source says; the served page is stale, see above). `cmd /c exit 7`, then the unpiped
  `StrataEditor.exe --headless --frames 10`: `$LASTEXITCODE` 7 at once and still 7 after 8 s, and the editor's log lines
  came into the console. The piped form (`| Out-Host`) left 0; `Start-Process -Wait -PassThru` gave `ExitCode` 0
  (`$LASTEXITCODE` stays 7 there, as the page's "keeps the code of the command before" says).
- **WK4 holds.** The worked solution's script copied into an empty folder as `killloop.py` (61 lines), `python -I
  killloop.py run` three times: in place damaged 7, 5 and 7 of 40, atomic 0 of 40 each time; both lines printed, exit 0,
  no PermissionError (the page says 5 to 12).
- **WK5 holds.** `project.openSample` with `PhysicsPlayground` and `directory`, `play.start` (built the scripts first,
  10.8 s), `editor.perf` with `frames` 120 in a headless editor: all the page's fields are there; `frames` 120,
  `framesPerSecond` 59.997, `renderStats` and `gameRenderStats` null, `gpu.frames` 0 and `gpu.boundBy` `unknown`;
  `Scene.Physics` 0.94 ms, `Scene.Scripts` 0.35 ms. The text before the figure says it shows part of the result and
  which fields it keeps. A small remark: the result also lists `Scene.Animation` and `Scene.UI`, which the page's "twelve
  stages" count does not need to name; a reader is not led wrong.
- **WK1 holds.** The tops of core/platform to core/math read without a "What you need": the internals pages carry "Before
  you start" (platform and profiling: core/jobs; files: platform and bytes; debugging: first-change, platform and
  debugging basics, and its text names the source build and links first-change; math: the rotation, projection and
  geometry primers and conventions).

Verdict: WK2, WK3, WK4 and WK5 get through without guessing, leaving the book or a mismatch, once the preview is rebuilt
from `book/write`.
