# Notes: `core/reading-code`

## New terms

- **trail**: the list of files and lines that leads from something the reader can see (an option, a message, a label)
  to the code where it acts, each line with a few words on what happens there. Home: `core/reading-code`. Aliases:
  trails, code trail.

## Requests

- `tools/data/names.txt`: Diomidis, Spinellis (the author of *Code Reading: The Open Source Perspective*, cited in
  Further reading). These are the page's only two `word-list` failures.

## Since

`since: 0.4.0`. `Docs/DeveloperGuide.md` and the table "Where the details are" of `AGENTS.md` first appear at `v0.4.0`
(`git ls-tree v0.3.0 Docs/` has no `DeveloperGuide.md`; `git show v0.4.0:AGENTS.md` has the table at line 456). At
`v0.4.0`, `StrataEditor/src/EditorApplication.cpp` already holds `CommandLineOption c_Arguments[]`, the `--idle-timeout`
check, `c_HeadlessFrameRate` and `specification.MaxFrames` from `--frames`.

## Not verified

- Code-editor facts, not Strata's: the Visual Studio menu path File, Open, Project/Solution, the commands "Go to
  Definition" and "Find All References", **Ctrl+G** (go to line) and **Ctrl+F**; `clangd` reading
  `compile_commands.json`. Written from general knowledge.
- `build/windows/Strata.slnx`: seen in the pin clone's own build folder (Visual Studio 2026 generator); the
  `windows-vs2022` preset writes `Strata.sln`, which the page does not state.
- That the Ninja Multi-Config presets (`linux`, `macos`, `windows-ninja`) write `build/<preset>/compile_commands.json`:
  from `CMAKE_EXPORT_COMPILE_COMMANDS ON` (`CMake/StrataConfigurations.cmake:31`), `Docs/DeveloperGuide.md:2067` and
  `Docs/Manual/Scripting.md:101`; no Linux or macOS build was looked at.
- Windows PowerShell 5.1 dropping double quotes inside single-quoted arguments to native programs: general behaviour of
  PowerShell, not checked here.
- doctest's `--test-case="<name>"` filter and its summary line ("1 passed"): doctest behaviour; `AGENTS.md` shows only
  `--test-suite`.
- The counts of files and lines (about 1,270 files, 451,000 lines): `git ls-files` at the pin, `.cpp`, `.h` and `.inl`
  files of `Strata/src`, `StrataEditor/src`, `StrataTests/src`, `StrataRuntime/src`, `StrataCLI/src` and
  `StrataScriptCore`. The 1,000 lines an hour is a stated supposition, not a measurement.
- The search counts (42 files for `--frames`, 10 for `"--frames"`, 7 lines below `StrataEditor/src`, 4 hits for
  `Engine modules:`, 4 commits for `git log -S c_HeadlessFrameRate` without a path) were run in the pin clone; a clone
  at a later commit gives other numbers.
- Check yourself 1: the message format is `RuntimeApplication.cpp:193` at the pin; the numbers 10.017 s and 601 frames
  are made up for the question.
- The "Engine modules:" line is written by every program: `RegisterBuiltinModules` is called from `main` in
  `Strata/Engine/EntryPoint.h:30`; which log sinks print INFO lines to a terminal was not checked, so the page says
  only "its log".

## Findings not applied

- The brief has no open findings.
- The brief writes the platform code as `Strata/src/Platform/<OS>/`; at the pin the folders are per system or library
  (`GLFW`, `NoWindow`, `Posix`, `Vulkan`, `Windows`), and the page says so.
- The brief's step 2 names `Docs/DeveloperGuide.md` as a map; the worked trail finds its facts in `AGENTS.md` (the
  rule about `c_Arguments`) and `Docs/Architecture.md` ("Application and frame loop"), because "Where the details are"
  has no row for command-line options. The page describes the guide's role but does not open a guide section.
- The page carries no sketch: a how-to whose exercises are trails in the reader's clone has no code to run; the Basic
  exercise's answer is the worked solution, without a `solution=` file.

## Clerk

- Admitted: "trail" (alias code trail), homed here.
- `tools/data/names.txt`: Diomidis Spinellis added.
