# Notes: `core/debugging`

## New terms

- **logger**: a named object that takes the calls of one family of macros and gives every line to the same sinks. Home: `core/debugging`. Aliases: loggers. (The page's word-list findings for "logger" and "loggers" stay until the term exists.)
- **sequence number**: the number a `LogBuffer` gives each entry, one higher than the last and never used twice. Home: `core/debugging`.
- **assert handler**: a function that gets a failed assert's condition, file, line and message and answers Break, Abort or Continue. Home: `core/debugging`. Aliases: assertion handler.
- **Console run**: a run of a program whose output is the point (`--help`, a headless or scripted run), which prints into the terminal that started it. Home: `core/debugging` (the engine's Developer Guide names it; the glossary may home it elsewhere).
- **asynchronous logging** is the brief's own term and is defined in bold on the page.

The page also defines **ring buffer** in one sentence beside the link to its home, `basics/data-structures`.

## Requests

- `tools/data/extra-words.txt` or the glossary: "logger" and "loggers" (see New terms).
- `tools/external-hosts.txt`: `sourceware.org` (the GDB manual), `lldb.llvm.org` (the LLDB tutorial) and `chromium.googlesource.com` (Crashpad). Two sources stand in Further reading, and one in the table, without a link until then.
- The figure `console-panel` (kind editor) needs the layout file `layouts/console-panel.ini`, which holds the Console panel docked and visible; the recipe only shows the panel.
- `breakpoint` and `call stack` are marked by markterms from the closure; no request.

## Since

`since: 0.3.0`. `Log.cpp` and `Assert.cpp` exist since the first commit (`a0f2865f`). The test crash reporter (`da84ac7b`) and `STRATA_TEST_TRACE` (`8f50c129`) are in `v0.3.0`. `BackgroundLogSink` (`1ad74df0`) first appears in `v0.4.0`.

## Not verified

- Debugger behaviour was not run: the Visual Studio labels ("Set as Startup Project", "Debugging", "Command Arguments", "Call Stack", "Locals"), the keys F5 and F9, what `gdb` and `lldb` print at a trap, and that Visual Studio names the stop a triggered breakpoint. The pin's build was not made, so the example test was not compiled or run.
- That the Visual Studio generator writes the solution `build/windows/Strata.sln` (the project name is `Strata`; CMake's default naming).
- Where a Ninja Multi-Config build writes `compile_commands.json` (the engine's own guide says only that Ninja builds write it into the build folder) and that the Visual Studio generator writes none.
- That `Release` carries debug information on Linux and macOS: the CMake file's comment says so, and only the MSVC link option (`/DEBUG`) was read.
- The caution box's statements about the operating systems' own crash dumps (Windows error reporting, Linux core files, macOS crash reports) are general knowledge.
- The table's Chromium and Unreal Engine rows are from general knowledge; the Further reading URLs were not fetched.
- `doctest`'s line `test case CRASHED` on Windows was read in the vendored header, not run. The text `Fatal signal 6 in test case:` was read in the reporter's code (signal 6 as `SIGABRT` on Linux and macOS is general knowledge).

## Findings not applied

The brief lists no open findings. Differences between the brief and the pin:

- The toy is 80 lines, not the brief's 40: the sketch must compile with the queue's bound, the writer and the warning's wait.
- The log's path (`foundation:416`) is a Mermaid sequence diagram, and the map is a Mermaid flowchart; the Console panel (`foundation:436`) is the only figure of the figures file.
- `Log.cpp:193-268` and `Assert.cpp:32-66` are quoted in smaller pieces (lines 200-227, 241-267 and 16-66) to stay within the quote limit.
- The trace exercise adds a temporary test case that starts the log with a file, because the test program writes no log file; the editor's log file would need a warning that its start does not log.
- The assert example's test code is a `pseudocode` fence: it is real code the reader types into an engine test file, which no sketch can be.
- `foundation:97` (`CrashGuard`, `Symbolizer`) is only named, with links to `scripting/crash-containment` and `scripting/symbolization`.

## Clerk

- Admitted: sequence number, assert handler (alias assertion handler).
- Refused: logger (homed on `core/conventions`, brief item `foundation:613`), Console run (homed on `core/first-frame`, brief item `foundation:623`), ring buffer (homed on `basics/data-structures`): only their homes word them.
- `external-hosts.txt`: `sourceware.org`, `lldb.llvm.org`, `chromium.googlesource.com` (front pages fetched: Sourceware, LLDB, Chromium's Git repositories).
- Left for the planner: `layouts/console-panel.ini`.

## Figures

- `console-panel` (editor; round 1 with the provisional build, not published): the recipe's `layouts/console-panel.ini` did not exist, and a fresh `basic3d` project gives no script lines and no warnings. The recipe now opens the sample PhysicsPlayground, plays 960 fixed steps and pictures the Console at 1280 × 800 in `layouts/console-panel.ini` (a copy of `layouts/console-audio.ini`, Console 876 px wide). The picture shows Trace off, the filter box, `Script` goal lines, yellow `Strata` audio warnings and `App` command lines. A line carries no level word: its color gives the level, and the caption says so. Keep `waitsFor` until the pin has `editor.screenshot`; then take without `--provisional` and publish.
  Round 2 at the pin v0.8.0 (319075e3), without `--provisional`, `waitsFor` removed as `check` asked: one take shows Clear, Trace unchecked, Info, Warnings, Errors and Auto-scroll checked, the filter box, `Script` goal lines, yellow `Strata` audio warnings and `App` command lines (the longest App line is cut at the right edge, which hides nothing the caption names). Published unchanged.
