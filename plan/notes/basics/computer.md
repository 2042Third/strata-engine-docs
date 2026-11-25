# Notes: basics/computer

## New terms

| Term | Definition | Home | Aliases |
| --- | --- | --- | --- |
| clock rate | The number of ticks a second at which a processor's clock runs; a simple instruction takes about one tick. | basics/computer | - |
| hardware thread | One of the lists of instructions a core keeps in progress at the same time; many x64 cores have two. | basics/computer | - |
| logical processor | What the operating system shows for each hardware thread. | basics/computer | - |
| register | One of the few dozen places inside a core where the numbers wait that an instruction works on right now. | basics/computer | registers |
| process id | The number the operating system gives a running process to name it. | basics/computer | - |
| child process | A process that another process, its parent, started. | basics/computer | parent process |

The page also describes without bold: instruction set, environment, exit code, operating system (homed in the closure).

## Requests

- Word: "SSE" (written once as "Streaming SIMD Extensions (SSE) 4.2", then four more uses): a name of an x64 instruction extension, proposed for `tools/data/extra-words.txt`.
- Hosts for Further reading (no link written, so none needed): Ulrich Drepper's paper, Charles Petzold's book, Intel's Intrinsics Guide (an Intel site).
- A tutorial file `tutorials/basics/computer/exercise-3.tutorial.json` with `exercise-3/Spinner.cpp` (the first-game Spinner with one comment character changed) is part of the page's files.

## Not verified

- The process viewers' labels and paths (Task Manager's **Details**, **PID**, **Threads** columns, **Select columns**, **Change graph to**, Activity Monitor's **CPU History**, the System Monitor's **Resources** tab) are general knowledge, not at the pin.
- The rough waiting times and sizes of the table, 16 to 64 GB of memory, a stack of a few MB, the cache line of 128 bytes and one hardware thread per core on Apple silicon, hardware prefetching: general knowledge.
- That a program built for AVX2 stops with an "illegal instruction" error on a processor without it: general knowledge (critic finding critic-basics-a-24, from critic-build-test-5).
- That a build with nothing changed starts CMake and the build tool but no compiler, and that it lasts about a second: critic finding, not run here (no engine program was started).
- The log line's exact appearance: the code writes `[Scripts] > <executable> <arguments>` through `ST_INFO` (`StrataEditor/src/Editor/ScriptBuild.cpp`, `ScriptBuilder::StartProcess`); the Console reads the log buffer (`StrataEditor/src/Panels/ConsolePanel.cpp`), but a picture of the line was not taken.

## Findings not applied

- critic-basics-a-27 (`basics/programming-2`, a frozen editor closed from the process viewer): belongs to that page, not this one; this page teaches the process viewer it can link.
- critic-basics-a-28 (`basics/debugging`): a change of that page's brief rows, not this page.

Applied here: critic-basics-a-21 (Common mistakes: memory taken for storage, more cores for a faster single task, plus two more), critic-basics-a-24 (two lines on many x64 processors, 64 bytes on x64 and 128 on Apple silicon, "stops at the first such instruction", the Ctrl+B exercise changes one character of a comment first and reads the command lines in the Console).

## Since

Not applicable: a primer has no `since`.

## Clerk

- Admitted: hardware thread, register.
- `names.txt`: "SSE". The Further reading hosts named no host to admit.
- Not admitted, because the page check would then fail and the page is the writer's: clock-rate (the section "A program is a list of instructions in a file" would define 5 terms (term-section)); logical-processor (its paragraph would define 2 terms with hardware thread (term-paragraph)); process-id (its paragraph would define 2 terms with process (term-paragraph)); child-process (the page bolds only "parent", so term-defined would fail). The part's reviewer splits the paragraph or section or bolds the term; the next clerk admits it then.

## Track walk E-final-1

Measured with the official 0.8.0 package under the perf lock, on the project of checkpoint 5 of `start/first-game`
(`docs-work/walkfix-E1/measure.ps1`, results in `measure.txt`, 2026-11-24):

- Windowed editor with a GPU (`StrataCLI launch --window-size 1280x720`): working set 225 to 229 MB, private bytes 746
  MB, 80 threads (`Get-Process`). Headless without a GPU (`--no-gpu`): working set 28 MB, private bytes 18 MB, 55
  threads. Practice 1 gives both. Task Manager's **Memory** column is the private working set, which was not read.
- `script.build`: the `[Scripts] >` lines read `cmake.exe -S <Scripts> -B <.strata/Scripts/Build> -G ...` (first build
  only) and `cmake.exe --build <.strata/Scripts/Build> --parallel --config Dist -- /nodeReuse:false`
  (`StrataEditor/src/Editor/ScriptBuild.cpp:451-460`, `MakeScriptBuildArguments`).
- The process tree of the second build, after the comment change: editor, `cmake.exe`, `MSBuild.exe`, a second
  `MSBuild.exe`, `Tracker.exe`, `cl.exe`.
- The solution of Practice 3 is the `Spinner.cpp` of `start/first-game` with the full stop of
  `// Turns its entity around the world's Y axis.` changed to "!"; the template's own file has 90 degrees and no
  `OnCreate`, so the answer tells a reader of another project to change the character instead of copying.
