# Notes: `core/first-frame`

## New terms

None proposed. The page defines the glossary's own entries homed here in bold: Application, Headless, Console run and Interactive run.

## Requests

None. Every word of the prose is on a list or is a glossary word, and every link of Further reading points to a host of `tools/external-hosts.txt`.

## Since

`since: 0.3.0`, the earliest release the field allows. `Application.cpp` exists since the engine's first commit (`a0f2865f`, in `v0.3.0`). `Application::ReportFatalError`, the Console and Interactive runs, `ConnectStandardStreams` and `STRATA_ERROR_DIALOG_FILE` came with `6013314c` ("Leave terminals to windowed runs, quit on Ctrl+C, show fatal errors"), which `v0.3.0` contains. The engine modules and their failure report came with `7d66c367` ("Run the engine's services as EngineModules the programs list"), in 0.4.0 according to the inventory.

## Not verified

- No program was started in this session (the card forbids it). The run of `StrataEditor --headless --frames 120`, its "at least 2 seconds", the exit codes of the four runs of the first exercise and the two commands of the failing-start example come from the code and from the tests `GPU.Startup` and `EndToEnd.StandardStreams`, not from a run.
- The failing-start example copies the editor test's way of making a computer without a driver (`VK_DRIVER_FILES` pointing at a file that does not exist); that the Vulkan loader then finds no driver on every system is the test's claim, not checked here. The dialog's file is shown as a shape with placeholders, because the advice text and the log path depend on the system.
- Further reading: the Game Programming Patterns chapter "Singleton" and the cppreference page "Static order initialization fiasco" (the path `w/cpp/language/siof`) were not opened; Jason Gregory's book has no link, and its section on start-up and shut-down of subsystems was cited from general knowledge.
- The "Who uses it" cells of the alternatives table name kinds of programs and one book, not products; they are general statements, not measurements.
- `GetProgramRun` and the usage of the runtime, and what its `--game` does, were read only as far as the example needs.
- That `JobSystem::Shutdown` may be called twice (once by `StartModules` after a module fails, once by the destructor) is assumed from the passing test `A module that cannot start ends the program, and only the modules that started end`; the page does not state it.

## Findings not applied

- The brief's exercise 3 (Hard) reads the dialog text of a startup step that fails "in a test application" through `STRATA_ERROR_DIALOG_FILE`. That does not hold: the test program connects its streams as a Console run (`StrataTests/src/TestMain.cpp`, `ConnectStandardStreams(ProgramRun::Console)`), so `ReportFatalError` only logs and returns before the file. The page's exercise checks the journal, the exit code and the log in a test application, and says why no file appears; the dialog file is read in the example, from a built program.
- The brief's figure `foundation:439` (the fatal-error dialog as a picture) is not requested: no recipe can show a dialog, and the text capture holds only a command's standard output. The page shows the dialog's text as a fenced shape instead. A figures file is absent, since the one picture (`foundation:391`) is a Mermaid sequence diagram.
- The brief asks for "four quotes" of the real code; the page has four (`EntryPoint.h` 16-41, `Application.cpp` 64-112, 126-160 and 42-62) and a fifth, `EditorApplication.cpp` 319-333, for the specification of `--headless` and `--no-gpu`.
- The brief's `build-test:123` row (`StrataRuntime.Arguments.Help` and `.Unknown`) is used in "How it is tested". The programs' own exit codes are one sentence with the two links, as the brief asks; the runtime's `worlds/runtime` and the editor's `editor/command-scripts` links lead to pages that may not exist yet.
- `new:22` (headless is two options) is applied in the definition of headless and in the table of the specification.

## Engine

- Windows, PowerShell 5.1, the official 0.8.0 package (track walk E-final-5, WK7 and WK8; measured 2026-11-24 in a console
  of its own, started through the pin's `StrataTests --strata-test-helper=console-output`, scripts in
  `docs-work/walkfix-E5`). `StrataEditor --bogus | Out-Host` sets `$LASTEXITCODE` to 3, but the message and the usage
  on standard error never reach the terminal; `2>&1 | Out-Host` shows them, the first line as a PowerShell error.
  Ctrl+C on `StrataEditor --headless | Out-Host` makes PowerShell end the editor itself: `$LASTEXITCODE` is -1 and the
  `Interrupted (Ctrl+C or a request to terminate): closing` line never comes. `Start-Process -NoNewWindow` and `cmd`
  (`start /wait /b`, or the program alone) hand the editor the console's own handles; it then printed nothing, and
  Ctrl+C did not end it. Only the engine's helper, which passes handles of `CONOUT$`
  (`StrataTests/src/TestHelpers.cpp`, `RunInConsole`), sees the 130 of
  `On Windows Ctrl+C in the terminal ends a headless editor in order`. The page's Basic exercise says what a reader
  of PowerShell meets (3 without the message, -1 for Ctrl+C). For the engine's agents, a cause read in the code and not
  checked: `ConnectStandardStreams` (`Strata/src/Platform/Windows/WindowsPlatform.cpp:755-793`) counts a stream as
  passed when `GetConsoleMode` fails on it, which may hold for a console handle in a process not yet attached, so the
  program would never attach.

## Clerk

- Admitted: Console run (the brief's item `foundation:623` homes both here; the glossary lacked them). Also asked by `core/debugging`, decided here.
- Not admitted, because the page check would then fail and the page is the writer's: interactive-run (its paragraph would define 2 terms with Console run (term-paragraph)). The part's reviewer splits the paragraph or section; the next clerk admits it then (the entries are in the wave-1b clerk's apply.py).
