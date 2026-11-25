# Walk E-final-5: track E (engine builder, persona E1), segment 5

Entries walked: `core/map`, `core/first-change`, `core/conventions`, `core/reading-code`, `core/first-frame`.
Package: Strata 0.8.0 Windows x64 (official package: StrataEditor, StrataRuntime and StrataCLI from `docs-package-0.8.0`; every engine program run under the perf lock, one hold, no editor left running).
Book: the built site at 127.0.0.1:4329, engine source read in a scratch worktree of docs-pin at 319075e3 (removed at the end).
Work folder: `G:/GameEngineAI/.worktrees/docs-work/walk-E-final-5/` (page texts and HTML, `sk/` the extracted sketches, `run1.ps1` and `run1-out/` the program runs, `dl/` the page's patch downloads).

How the walk went: every page read in full. Every quoted engine excerpt (22 of them, data-source and line range on the page) compared with the file at 319075e3: all equal. Every sketch (5) extracted from the page, compiled with g++ 15 `-std=c++20 -Wall -Wextra` and run: no warnings, all outputs and all "Line N" notes match. Layers.json (19 rows, MayInclude of Core, Scene, Renderer, Physics, the three Tooling rows, Audio's note), CoreShards.json (13 shards), the 17 and 12 options of `--help` and the five shared ones, the git grep, git blame and git log -S results of reading-code (43 and 10 files, seven lines, two lines, one commit d40f9a03, four commits for c_HeadlessFrameRate), all file and line numbers of its Variations and exercises, the names of the tests the pages cite, the exit codes 0, 1, 3 (and 130 by its constant) were checked against source or by running the package. The change of first-change was made in the scratch worktree (see below) and equals the page's download `first-change.patch` in content; the downloads of exercises 1 and 2 apply with `git apply --check` on top of it.

Not walked: the build and test steps of first-change (the integrator does them, see below); `git clone` of GitHub and `git submodule update` (the pinned worktree stood in for the clone); Ctrl+C exit code 130 of first-frame's Basic exercise (my tool cannot send a Ctrl+C to a program); the editor-side jumps of reading-code ("Go to Definition" in Visual Studio or clangd) and the "A call stack as a trail" variation (no IDE, no debugger session); the Linux and macOS tabs.

## Built by the integrator

Patch file: `G:/GameEngineAI/.worktrees/docs-work/walk-E-final-5/core-first-change.patch` (the page's change: `StringUtils::ToUpper` in `Strata/src/Strata/Core/StringUtils.h`, one test case in `StrataTests/src/Core/StringUtilsTests.cpp`; 17 lines added). Apply it to a clean checkout of 319075e3 with `git apply`. The page's steps, in order:
1. `cmake --preset windows` (configure; expected "Slang 2026.20:" line).
2. `cmake --build build/windows --config Debug --parallel` (first build; no error line; programs in `build/windows/bin/Debug/`).
3. `build\windows\bin\Debug\StrataEditor.exe --version | Out-Host` (expected `Strata Editor 0.8.0`); the window start is not needed for the check.
4. Apply the patch, then `cmake --build build/windows --config Debug --parallel` again (no new configure step; the page claims 58 source files include StringUtils.h, which `git grep -l '#include.*StringUtils\.h'` confirms).
5. `cmake --build build/windows --config Debug --target StrataTests --parallel`, then `build\windows\bin\Debug\StrataTests.exe --test-suite=Core.StringUtils`. Expected: test cases 3 | 3 passed | 0 failed, checks 21 | 21 passed | 0 failed, `Status: SUCCESS!`.
6. Break it: in ToUpper only, `std::toupper` to `std::tolower`; build the test program; run the suite again. Expected: 3 | 2 passed | 1 failed test cases, 21 | 17 passed | 4 failed checks, `Status: FAILURE!`, and four "is NOT correct!" reports. Then restore and run once more (SUCCESS).
7. `ctest --preset windows-debug -L core` (13 groups, all Passed; names as the page lists them; `ctest -N -L core` lists 13).
8. Exercise Basic (download exercise-1.patch, applies on top of the change): suite counts 23 checks, all passed; with std::tolower in ToUpper the empty check passes and the check of "été" fails.
9. Exercise Medium (download exercise-2.patch): suite counts 4 test cases, no new configure step.
10. Exercise Hard (patch `core-first-change-exercise-hard.patch` in the same folder: the page's two lines plus the empty check of Basic): Debug run of `--test-suite=Core.StringUtils` should log `Assertion '!text.empty()' failed at ...`, show the abort() message box on Windows and report the test case crashed with SIGABRT; then `cmake --build build/windows --config Dist --target StrataTests --parallel` and `build\windows\bin\Dist\StrataTests.exe --test-suite=Core.StringUtils` should pass 23 checks; also `ctest --preset windows-dist -L core` as an alternative.
11. reading-code: `build/windows/bin/Debug/StrataTests.exe --test-case="CommandLine parses flags and options"` (expected one test case passed). The page shows the Linux path; the test case name exists in CoreTests.cpp line 236.
12. first-frame and conventions: `build\windows\bin\Debug\StrataTests.exe --test-suite=Core*` and `--test-suite=Core.ErrorThrottle`, `--test-suite=Core.EngineModules`; the Hard exercise's new test in EngineModuleTests.cpp is not part of any patch of mine.

## WK1
- Entry: `core/map`
- Page: How Strata is put together: programs, libraries, modules and layers
- Step: the start of the page ("What you need", the stage download)
- What happened: the page has no "What you need" section and offers no stage download; it has "Before you start" with two links (the CMake page and "What a game engine is"). The next entry, `core/first-change`, has a "What you need" that says "No project, sample or file to import" and starts from a git clone of GitHub; it offers no stage download either. I started the segment with the installed package for map and used a worktree of the pinned commit in place of the clone for first-change (a side step the book does not describe; a reader without a clone has no stage to arrive at).

## WK2
- Entry: `core/map`
- Page: How Strata is put together: programs, libraries, modules and layers
- Step: Exercises, Medium ("In a terminal, run the installed StrataEditor --help and StrataRuntime --help")
- What happened: in Windows PowerShell 5.1 `& StrataEditor.exe --help` printed nothing at the command; the help text appeared later and out of order after the next command (the editor is a GUI-subsystem program), and `$LASTEXITCODE` was empty. `StrataRuntime.exe --help | Out-String` printed at once. first-change tells the reader `| Out-Host` for the editor; this exercise does not. With `| cat` in Git Bash and with redirected output the counts match the worked solution exactly (17 and 12 options, five shared: --headless, --windowed, --frames, --screenshot, --help; 12 and 7 alone).

## WK3
- Entry: `core/first-change`
- Page: Your first engine change: build from source, change one thing, test it
- Step: "Get the source at the book's commit", step 3 (the box that quotes the CMake error)
- What happened: the page quotes the configure error as `Third-party submodules are missing. Run git submodule update --init --recursive --depth 1.` The line in CMakeLists.txt (line 14) is `Run \`git submodule update --init --recursive --depth 1\`.` with backticks around the command, so the text a reader would see in the terminal has backticks the page leaves out. I did not run the configure step (no build); the difference is read from the source.

## WK4
- Entry: `core/first-change`
- Page: Your first engine change: build from source, change one thing, test it
- Step: Build the engine and start the editor; Prove the change with a test (every build and test command)
- What happened: I did not build (this segment hands builds to the integrator). I made the change in the scratch worktree by hand from the page's two hunks: the result is 9 lines added to StringUtils.h and 8 to StringUtilsTests.cpp, as the page's picture says ("9 lines added", "4 checks, 8 lines added"), at the lines the page names (12-19 and 9-20 quoted, hunks at 18-23 and 40-43). The page's own `first-change.patch` download gives the same content and applies cleanly. The page's predictions (7 + 10 + 4 = 21 checks, 3 test cases; after the mistake 2 | 1 failed and 17 | 4 failed) agree with my count of the checks in the test file. The commands are listed under "Built by the integrator".

## WK5
- Entry: `core/reading-code`
- Page: Finding your way in a large codebase
- Step: "Why you cannot read it all" (the counts)
- What happened: the page says the C++ source without the third-party libraries is about 1,270 files and 451,000 lines: 152,000 engine, 83,000 editor, 207,000 tests, 9,000 for the rest. I counted the tracked .cpp and .h files outside Strata/vendor at 319075e3: 1,389 files and about 475,000 lines: Strata 154,940, StrataEditor 83,835, StrataTests 227,625 (page: 207,000), StrataRuntime + StrataCLI + StrataScriptCore 8,928 (page: 9,000). Editor and "rest" match; tests are 10% higher, files 9% higher. The conclusion (eleven weeks) holds.

## WK6
- Entry: `core/reading-code`
- Page: Finding your way in a large codebase
- Step: "Write down the trail, and close its gaps" (`git grep -n -w CreateApplication -- Strata/src`)
- What happened: the page says the search "leads past its declaration to Strata/src/Strata/Engine/EntryPoint.h". The search prints 12 lines (ApplicationLaunch.h declaration, EntryPoint.h:25, and ten lines of comments in Application.cpp, Application.h, BuiltinModules.cpp/.h, GamePresentation.h). I had to guess which one is the caller: the line with `= Strata::CreateApplication(commandLine);`. The page does not say how many lines to expect, unlike its other searches.

## WK7
- Entry: `core/first-frame`
- Page: From main to the first frame
- Step: "The example: an editor to its first frame", the two terminal examples
- What happened: (a) `StrataEditor --headless --frames 120` in PowerShell: the editor is a GUI-subsystem program, so a reader at a Windows terminal sees nothing and cannot read the exit code unless the output is redirected or piped to Out-Host; the page says nothing about it here (first-change does). I ran it with Start-Process and redirected output: exit 0, 3.1 s (the page says at least 2 s), log in `%LOCALAPPDATA%\Strata\Logs\StrataEditor.log` (the page says "Logs/StrataEditor.log in your user data folder": matches). (b) The failing-driver example is written for Linux and macOS only (`VAR=value StrataEditor --windowed 2>/dev/null; echo $?`). I translated it myself: `$env:VK_DRIVER_FILES`, `$env:VK_ICD_FILENAMES`, `$env:STRATA_ERROR_DIALOG_FILE` and Start-Process with stderr to NUL. It gave exit 1 and a dialog file whose text matches the page's shape exactly (title `Strata Editor`, the problem, the advice "Install or update the GPU driver...", `The log has the details: C:/Users/.../Strata/Logs/StrataEditor.log`, with forward slashes). The shell tab for Windows is missing; a reader has to guess the PowerShell form.

## WK8
- Entry: `core/first-frame`
- Page: From main to the first frame
- Step: Exercises, Basic (the fourth run, `--headless` stopped with Ctrl+C, expected 130)
- What happened: not run: my terminal tool cannot send Ctrl+C to a child program. The other three runs gave 0 (`--help`), 3 (`--bogus`) and 0 (`--headless --frames 10`, with a GPU): as the solution says. Also checked: `--frames 0` and `--frames abc` exit 3 with the message `--frames expects a positive number of frames` and the usage on standard error; `StrataRuntime --bogus` exits 3 with `Unknown argument '--bogus'`; `--no-gpu --no-automation --frames 3` and `--windowed --frames 3` exit 0; `--no-gpu --idle-timeout 2` closes after about 2 s with the log line `No automation client for 2 s (--idle-timeout): closing the editor`, as the reading-code Medium exercise's trail says.

## Answers

Checks were run under the perf lock in `docs-work/walkfix-E5`, with the official 0.8.0 package. PowerShell 5.1 runs
were made in a console of their own through the pin's `StrataTests --strata-test-helper=console-output` (`console.py`,
`cases.py`, `cmdcase.py`; one result file per case). The configure error was taken from a copy of the pin's
`CMakeLists.txt` and `CMakePresets.json` without submodules (`nosub.out`). The patches under "## Built by the
integrator" were applied to the pin clone and built in `build/docs-patch` (`patch/`, `extra/`); the clone was left
clean. No tutorial file changed: `core/first-change` has the only one of the five pages, and its patch run is in WK4.

### WK1
- Fixed on `core/map`. Why: a concept page has no "What you need" by the book's style (style.md §7.4 gives it to
  tutorials; the top strip's "Before you start" lists the Needs), and `core/first-change` starts from a clone of GitHub
  as style.md asks of the tutorial that makes the source build. But `core/map` asks the reader to read
  `Layers.json`, `EntryPoint.h` and other source files, and the installed package holds none of them (checked: its
  folder has `Docs`, `Samples`, `Skills`, `StrataScriptCore` and the three programs). A reader of the package had no
  place named where to read them.
- Change: a paragraph after the introduction says that the installed Strata holds no source files, links the engine's
  files on GitHub at the book's commit (319075e3), and says that the next page makes a clone. The walker's pinned
  worktree stood for that clone, as the walk's rules ask; no change to `core/first-change` for this entry.

### WK2
- Fixed on `core/map`. Why: both programs are windowed programs on Windows; PowerShell does not wait for them unless
  their output is piped. Measured: `.\StrataEditor.exe --help` alone printed nothing and left `$LASTEXITCODE` empty;
  `.\StrataEditor.exe --help | Out-Host` printed the usage (17 options) and set 0; the same for
  `.\StrataRuntime.exe --help | Out-Host` (12 options, 0). The counts of the worked solution stand.
- Change: the Medium exercise says that PowerShell does not wait for windowed programs, gives the two lines with
  `| Out-Host` to run in the folder of the installed Strata, and says what each prints (`Usage:`, `Options:`, a line per
  option). Words were cut elsewhere on the page to stay within size M (4,000).

### WK5
- Fixed on `core/reading-code`. Why: the page's counts were older than the pin (they match no commit checked: at
  822a7a46 the same folders hold 1,329 files). Counted at 319075e3 with `git ls-files -- Strata StrataEditor
  StrataTests StrataRuntime StrataCLI StrataScriptCore`, `.cpp` and `.h` only (submodule files are not listed): 1,343
  files and 475,311 lines; engine 154,931, editor 83,835, tests 227,617, runtime, CLI and script interface 8,928. The
  walker's 1,389 files include `Samples/` (43) and `CMake/` (3), which the page's list does not name.
- Change: about 1,340 files and 475,000 lines, without the third-party libraries and the samples: 155,000, 84,000,
  228,000 and 9,000; 475 hours, about twelve weeks.

### WK6
- Fixed on `core/reading-code`. Why: the page named the result of the search but not how many lines it prints or
  which one is the caller. At the pin `git grep -n -w CreateApplication -- Strata/src` prints ten lines (not 12):
  eight comments (`Application.cpp:24`, `Application.h:64`, `ApplicationLaunch.h:15` and `:24`, `BuiltinModules.cpp:124`,
  `BuiltinModules.h:37`, `EntryPoint.h:4`, `GamePresentation.h:13`), the declaration `ApplicationLaunch.h:30` and the
  call `EntryPoint.h:25`.
- Change: step 5 says that the search prints ten lines, eight comments, the declaration on line 30 of
  `ApplicationLaunch.h` and the call, which ends in `CreateApplication(commandLine);`, on line 25 of `EntryPoint.h`.
  Two sentences elsewhere were shortened to keep size M.

### WK7
- Fixed on `core/first-frame`. Why: both terminal examples were written for a POSIX shell only, and the editor is a
  windowed program, which PowerShell does not wait for. Measured with the package in PowerShell 5.1:
  `.\StrataEditor.exe --headless --frames 120 | Out-Host` printed the log and set `$LASTEXITCODE` to 0 after 2.2 s.
  The failing driver: `$env:VK_DRIVER_FILES` and `$env:VK_ICD_FILENAMES` set to `C:\nowhere\NoDriver.json`,
  `$env:STRATA_ERROR_DIALOG_FILE` to a file, then `(Start-Process .\StrataEditor.exe -ArgumentList '--windowed' -Wait
  -PassThru).ExitCode` printed 1, and the file held the page's shape (title, problem, the driver advice, `The log has
  the details: C:/Users/.../Strata/Logs/StrataEditor.log`). `Start-Process` passes no standard streams, so the dialog
  is allowed, as the null device is on Linux.
- Change: the example gives the PowerShell lines with `| Out-Host` and `$LASTEXITCODE`. The failing-driver example is
  a tab set (Windows, Linux, macOS): the Windows tab sets the three variables, runs `Start-Process` with `-Wait
  -PassThru`, prints `ExitCode` and removes the variables, and says why; the other tabs keep the POSIX line and say
  what `2>/dev/null` and `echo $?` do. The sentence after it says "its standard error reaches no reader: the null
  device, or no stream at all".

### WK8
- Fixed on `core/first-frame`. Why: the walker's tool could not press Ctrl+C, but the exercise also gave no Windows
  way to read the codes, and in PowerShell two of the four runs differ from the answer. Measured in a console through
  the pin's helper (`--interrupt-when "Started in"` presses Ctrl+C as a terminal does): with
  `.\StrataEditor.exe --headless | Out-Host`, Ctrl+C makes PowerShell end the editor; `$LASTEXITCODE` is -1 and the
  `Interrupted` warning never comes. `Start-Process -NoNewWindow` and `cmd` (`start /wait /b`, or the program alone)
  did not pass Ctrl+C to the editor; those runs were stopped by hand. `.\StrataEditor.exe --bogus | Out-Host` sets 3
  but shows no message; `2>&1 | Out-Host` shows it, the first line as a PowerShell error. `--help | Out-Host` and
  `--headless --frames 10` (with `Start-Process -NoNewWindow -Wait -PassThru` too) give 0. The 130 stands on Linux and
  macOS (the POSIX test sends SIGINT and SIGTERM) and on Windows when a console hands the key to the editor, as
  `On Windows Ctrl+C in the terminal ends a headless editor in order` does.
- Change: the exercise says how to read each code (`echo $?`; in PowerShell `| Out-Host`, then `$LASTEXITCODE`). The
  answer adds a paragraph for Windows PowerShell: the unknown option shows 3 without its message (`2>&1` shows it as
  an error), and Ctrl+C makes PowerShell end the editor, so the code reads -1; the engine's test gets 130. The page's
  notes record the Windows behavior under "## Engine" for the engine's agents.

### WK3
- Fixed on `core/first-change`. Why: the page quoted the source line of `CMakeLists.txt` as a block quote, in which
  the backquotes became code, so it did not show what the terminal shows. Measured: `cmake --preset windows` on a copy
  of the pin's `CMakeLists.txt` and `CMakePresets.json` without `Strata/vendor/` prints, after the compiler lines,
  `CMake Error at CMakeLists.txt:14 (message):`, the message wrapped onto two lines with two spaces after its first
  full stop and the command between backquotes, then `-- Configuring incomplete, errors occurred!`.
- Change: the block quote is replaced by that output in a text fence, with a sentence that CMake breaks the message
  into lines and that the command stands between two `` ` `` marks, and one that says to run it (step 3) and configure
  again.

### WK4
- Built by the integrator; no change to the page. `tutorials.py patch core/first-change` in `build/docs-patch`
  (Release) passed the page's patch (Core.StringUtils 3 | 3 passed, 21 | 21 passed, `Status: SUCCESS!`;
  Architecture.Layering and the feature test passed), exercise 1 (23 checks, all passed) and exercise 2 (4 test cases,
  26 checks, no new file, so no new configure step). By hand, in the same build: `std::tolower` in `ToUpper` gave
  3 | 2 passed | 1 failed, 21 | 17 passed | 4 failed, four `is NOT correct!` and `Status: FAILURE!`, as step 3 says;
  with exercise 1 on top the check of `été` failed and the empty one passed, as its answer says. The walker's Hard
  patch logged `Assertion '!text.empty()' failed at …StringUtils.h:26: ToUpper was given empty text`, then `test case
  CRASHED: SIGABRT` and `Status: FAILURE!`, as the answer says for Windows. The clone was reverted and is clean.
- Not run: the Debug and Dist configurations (only Release is built in `build/docs-patch`; a first build of either is
  the whole engine), so the Debug `abort()` box, the Dist pass of 23 checks, `ctest --preset windows-debug -L core` and
  the editor's `--version` from a Debug build were not run here. The 13 groups stand from `StrataTests/CoreShards.json`
  and the version line from the package (`Strata Editor 0.8.0`); the Dist claim stands on `Base.h`, which defines
  `ST_ENABLE_ASSERTS` only without `ST_DIST`. The 58 files that include `StringUtils.h` were counted again with
  `git grep -l` (58).

## Answers (after confirm)

The confirmer's locked runs never got their turn, so the four entries were run again under the perf lock, with no
change to the pages (the source at `book/write` is what was checked). PowerShell 5.1 lines ran in a console of their own
through the pin's `StrataTests --strata-test-helper=console-output`, in the 0.8.0 package's folder, with
`$LASTEXITCODE` set to 7 first (`docs-work/walk-final-fix/console`, one result file per case).

### WK2 core/map, Exercises, Medium
- Holds. `.\StrataEditor.exe --help | Out-Host` printed `Usage: StrataEditor [options]`, `Options:` and 17 option lines
  in order, then `$LASTEXITCODE` 0; `.\StrataRuntime.exe --help | Out-Host` printed 12 option lines and 0. The worked
  solution's 17, 12 and five shared stand.

### WK4 core/first-change, build and test steps
- Holds. `tutorials.py patch core/first-change core/first-change/exercise-1 core/first-change/exercise-2` in
  `build/docs-patch` under the lock: three passed (the page's patch, then each exercise on top; two doctest suites and the
  feature test each); the stamps were written again unchanged and the clone is clean. The mistake step and the Hard
  exercise were not repeated: the answer of the first fix above measured them by hand in the same build.

### WK7 core/first-frame, The example
- Holds. `.\StrataEditor.exe --headless --frames 120 | Out-Host` printed the log from `App: Strata Editor 0.8.0
  (Windows)` to `AudioEngine: shut down`, `$LASTEXITCODE` 0 after 2.29 s. The Windows tab of the failing-driver example
  (the three `$env:` lines, `(Start-Process .\StrataEditor.exe -ArgumentList '--windowed' -Wait -PassThru).ExitCode`,
  `Remove-Item`) printed 1, and the dialog file held the page's shape: `Strata Editor`, `Strata Editor cannot start: no
  usable graphics device was found (it needs Vulkan 1.2 or later).`, the driver advice and `The log has the details:
  C:/Users/.../Strata/Logs/StrataEditor.log`.

### WK8 core/first-frame, Exercises, Basic
- Holds for every run the answer names on Windows: `--help | Out-Host` 0; `--bogus | Out-Host` 3 with no message on the
  screen; `--bogus 2>&1 | Out-Host` 3 with the message as a PowerShell error record and the usage; `--headless --frames 10
  | Out-Host` 0; `--headless | Out-Host` with Ctrl+C sent by the helper after `Started in` gave -1. The 130 of Linux and
  macOS was not run here (no such machine); the page takes it from the engine's POSIX test.

## Confirm (after the second answers)

Read as a fresh reader: the pages at book/write, the 0.8.0 package, the pin, under the perf lock; results in `docs-work/walk-final-confirm-2`. Every entry below: through without guessing, leaving the book or a mismatch.

### WK2 core/map, Medium exercise
- Holds. `.\StrataEditor.exe --help | Out-Host` and the runtime's, in a PowerShell 5.1 console in the package folder: Usage, Options in order, 17 and 12 option lines, `$LASTEXITCODE` 0 each.

### WK4 core/first-change
- Holds as read: the fixer's answer (no change; `tutorials.py patch` passed 3 of 3, clone clean) agrees with the page, whose steps and counts (3 test cases, 21 checks, exercises 1 and 2) stand. Not built or patched here, as the task says.

### WK7 core/first-frame, The example
- Holds. `--headless --frames 120 | Out-Host` printed the log and `$LASTEXITCODE` 0 after about 2 s. The Windows tab of the failing-driver example printed 1, and dialog.txt held the title, `cannot start: no usable graphics device was found (it needs Vulkan 1.2 or later)`, the driver advice and the log path, as the page says; its last line removed the variables.

### WK8 core/first-frame, Basic exercise
- Holds. `--help | Out-Host` 0; `--bogus | Out-Host` 3 with no message; `2>&1 | Out-Host` showed the error record and usage; `--headless --frames 10` 0; `--headless` stopped with Ctrl+C by the helper gave -1, as the page's answer says (the 130 of Linux and macOS not run).
