# Notes: `basics/debugging`

## New terms

None proposed. The page defines in bold the eleven terms the brief lists (bug, debugging, debugger, debug information,
attaching a debugger, breakpoint, stepping through code, call stack, stack frame, stack trace, crash) and also **process**
(a running program; home `basics/computer`, one sentence here), **condition** (of a breakpoint), **variables** and
**watch** (of the debugger's windows). None is meant as a glossary home.

## Requests

- `tools/external-hosts.txt`: `code.visualstudio.com`. Further reading cites the Visual Studio Code documentation without
  a link until the host is allowed.
- Figures: none requested. The page has one Mermaid diagram (the six steps) and no figure manifest. Pictures of Visual
  Studio's dialogs are not Strata's and are not requested.
- Sketches: three files, `sketches/basics-debugging-stack.cpp`, `-radians.cpp` and `-counter.cpp`. All compile with the
  sketch check and their output is filled in.

## Not verified

- Everything about Visual Studio, Visual Studio Code, `gdb`, `lldb`, Ubuntu's `kernel.yama.ptrace_scope` and macOS's
  debugger prompt (menu names, F-keys, the launch.json fields `cppvsdbg`, `cppdbg`, `MIMode`, `${command:pickProcess}`,
  that `cppdbg` attach needs `program`). They are not in the pin; the page states them as general knowledge of those tools.
- That a script breakpoint binds with GCC or Clang in every configuration: read at v0.8.0 from the `-g` that
  `StrataScriptCore/CMake/StrataScriptModule.cmake` adds outside MSVC (its comment: in the module on ELF, in the objects
  the debug map names on macOS) and `Docs/Releases/0.8.0.md` (Fixes). Nothing was run on Linux or macOS. Pin move to
  0.8.0: the debug information section, the Linux and macOS tabs, the Practice's opening and exercise 5 no longer give
  those systems a `Log` route.
- That the downloaded Strata is built in `Dist`: read in `.github/workflows/release.yml` (`Build (Dist)`, `cpack -C Dist`).
- The line the reader's `Coin` script turns with: the page assumes it reads like the `Spinner` of
  `StrataEditor/src/Editor/ScriptProject.cpp` (`glm::radians(DegreesPerSecond * deltaTime)`); `make/first-script` at this
  commit teaches a `Spinner` on a cube, not `Coin`.
- The Console's line shape `[time] [Script] text` comes from `ConsolePanel.cpp` and `Log.cpp`, not from a run.
- The log file is truncated at each editor start (`basic_file_sink_mt` with truncate set): the page says it keeps every
  line of the editor's run.
- Links to pages not written yet: `basics/data-formats`, `basics/computer`, `make/play-test-debug`, `core/debugging`,
  `scripting/crash-containment`, `scripting/symbolization`.

## Findings not applied

- critic-basics-a-9: applied in part. The tabs and the section on debug information say what the pin does for the
  downloaded Strata (read, not run); the Practice marks the exercises that need a binding breakpoint and gives
  Linux and macOS readers `Log` lines for exercises 4 and 5. Not applied: trying whether a `-g` in `Scripts/CMakeLists.txt`
  makes breakpoints bind (no run allowed).
- critic-basics-a-10: applied. The launch-file section gives a complete `launch.json` per system, its place (a `.vscode`
  folder inside `Scripts`, a dot folder the module neither compiles nor watches) and the extension and `gdb` steps. Not
  verified: that the editor writes none, shown only by a search of the pin for "launch.json".
- critic-basics-a-11: applied: place named in the text, Trace box, 4,096 lines, the log file; the Console opens only
  compiler and crash lines.
- critic-basics-a-28: applied: the process stays one paragraph that links `basics/computer`.
- critic-basics-a-1: applied: the Practice runs in `Playground` on its own entity.
- Brief item `new:211` (not-done) is stated only as what the pin does, not as a promise.
- `scripting:157`'s private copy and `scripting:384`'s PDB in every configuration are used in the debug information section.

## Clerk

- `external-hosts.txt`: `code.visualstudio.com` (front page fetched).
