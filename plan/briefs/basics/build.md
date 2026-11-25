# Brief: `basics/build`

| Field | Value |
| --- | --- |
| Title | How a C++ program is built: from two files by hand to CMake |
| Kind | P |
| Size | L |
| Tracks | B, E |
| Needs | `basics/tools`, `basics/programming-3`, `basics/computer` |
| From | build-test "How a C++ program is built"; a two-file program built by hand and then with CMake; executables, static and shared libraries (foundation concept 1, which `core/map` needs) |
| Unit | `plan/allocation/basics-a.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `basics/build` — How a C++ program is built: from two files by hand to CMake

**Covers.** A two-file program built by hand, then with CMake, so that every later build is understood. From source to
machine code: the compiler turns one source file into an object file (`c++ -c main.cpp`, `cl /c main.cpp`, in OS tabs).
Translation units: the preprocessor copies each `#include`d header into the source file first (its directives are
`basics/cpp-modern`'s), so a header is never compiled alone; declarations against definitions, and the one-definition
rule. The linker joins object files and libraries, connects each use of a name to its definition (symbols), and reports
link errors (`undefined reference`, `unresolved external symbol`), which are not compile errors: the page shows one of
each. Executables and libraries: a static library is an archive of object files copied into each program that links
it, and on GNU's linker the order of static libraries on the link line matters (Strata's case stays an example of
`engineering/third-party`); a shared library (`.dll`, `.so`, `.dylib`) is loaded when a program starts; a module
library is loaded on purpose while the program runs, which is what a script module is. What runs before `main`:
globals are built in an order that C++ leaves open between translation units (static initialization and its order),
and a linker may drop an object file of a static library that nothing names. The worked example: `main.cpp`,
`Greeting.h` and `Greeting.cpp` compiled and linked in a terminal, run, then broken twice (a missing `;` and a missing
definition) to see both kinds of error. Build systems and incremental builds: compare file times and build only what
changed, and why changing a header rebuilds many files. CMake: a `CMakeLists.txt` with `add_executable`, `add_library`
and `target_link_libraries`, the configure step and the build step, generators (Visual Studio, Ninja), the cache, and
definitions passed to the code (`target_compile_definitions`); the two-file program built again with CMake. Build
configurations: Debug and Release, what optimization changes, debug information beside the machine code (what a
debugger reads, `basics/debugging`), and asserts that only some configurations keep. Linker optimizations: dropping
code nothing uses and folding identical functions into one (so two functions can share one address). The Practice
runs in a terminal on the two-file program, from easy to hard: what a changed file rebuilds predicted, then run; a link
error made and fixed; Debug against Release with an assert; a static library and the order of the link line; it ends
with the optional Coin Run item: read the `Scripts/CMakeLists.txt` the editor wrote and build the module by hand with
the two commands its comment gives.

**Leaves out.**

- The preprocessor's directives and macros → `basics/cpp-modern`
- Strata's CMake: layers as libraries, options and presets → `engineering/cmake`
- Building Strata from source → `engineering/building`, `core/first-change`
- Strata's configurations and Dist → `engineering/building`
- Shared libraries, symbol visibility and loading code at run time in Strata → `scripting/shared-libraries`
- How the editor builds scripts → `editor/script-builds`
- Building script modules outside the editor, as a game maker does it → `make/script-builds`
- Self-registration and Strata's composition root → `core/layers-registries`

**Fit.** `fits`: about 5,450 words against L (5,000). Ten ideas, with the two-file program built by hand with its real
output and its two errors and built again with CMake (about 4,150), and the common mistakes, the Practice's four
exercises, the Coin Run item and the fixed parts (about 1,300); libraries and CMake take the most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:164` | concept | home | The compiler: one source file into one object file, by hand. General knowledge. |
| `new:165` | concept | home | Translation units: headers copied in first, declarations and definitions, the one-definition rule. General knowledge. |
| `new:166` | concept | home | The linker, symbols, and link errors against compile errors. General knowledge. |
| `new:167` | concept | home | Executables, static libraries and their order on GNU's link line, shared libraries, module libraries. General knowledge. |
| `new:168` | concept | home | What runs before `main`: static initialization and its order; objects of a static library that a linker drops. General knowledge. |
| `new:169` | hands-on | home | The two-file program built and linked by hand, run, and broken twice. General knowledge. |
| `new:170` | concept | home | Build systems and incremental builds by file times; a changed header. General knowledge. |
| `new:171` | concept | home | CMake: `add_executable`, `add_library`, `target_link_libraries`, configure and build steps, generators, the cache, compile definitions. General knowledge. |
| `new:172` | concept | home | Build configurations: Debug and Release, optimization, debug information, asserts. General knowledge. |
| `new:173` | concept | home | Linker optimizations: unused code dropped, identical functions folded. Evidence: `CMake/StrataConfigurations.cmake:49-51` |
| `new:174` | hands-on | home | Optional practice on Coin Run: the module built by hand with the two commands in its `CMakeLists.txt`. Evidence: `StrataEditor/src/Editor/ScriptProject.cpp:216-218` |
| `new:221` | hands-on | home | Practice before the Coin Run item, in a terminal on the two-file program, from easy to hard: Basic, predict then run: which files a build compiles again after `Greeting.cpp` changes, and which after `Greeting.h` changes; Medium: a third file that declares a function and never defines it, and the link error read and fixed; Medium: the program built in Debug and in Release with CMake, and an `assert` that stops only one of them; Hard: `Greeting.cpp` made into a static library, and with GNU's linker two libraries swapped on the link line to see the error. General knowledge. |
| `build-test:271` | concept | home | From source files to a program: compiling per translation unit, then linking; the mistakes of thinking a header is compiled and of taking a link error for a compile error |
| `build-test:609` | term | home | Translation unit |
| `build-test:610` | term | home | Linker |
| `build-test:611` | term | home | Static library, shared library and module library |
| `gamedev:364` | code | use | The game's `CMakeLists.txt` as the editor writes it, read for the practice (its home is `make/script-builds`) |
| `foundation:208` | concept | use | An executable against a library, static against shared, the general half |
| `build-test:277` | concept | link | Configure, build and test as Strata's three steps, linked to `engineering/cmake` |
| `build-test:380` | code | link | Strata's three configurations, linked to `engineering/cmake` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| A terminal: running a program with arguments, quoting a path | `basics/tools` | must |
| Header and source files, `#include`, declarations | `basics/programming-3` | must |
| Machine code and a process | `basics/computer` | must |
| Macros and `#if` | `basics/cpp-modern` | helps |
| Debug information as a debugger uses it | `basics/debugging` | helps |

**Starting state.** The end state of `make/project-coin-run`, downloaded on track E, from which the optional Coin Run
item of the Practice starts. The other exercises run in a terminal on the page's two-file program.

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `build-configuration` | build configuration | - |
| `build-system` | build system | - |
| `cmake` | CMake | - |
| `compiler` | compiler | compiling, compilation |
| `configure-step` | configure step | - |
| `executable` | executable | executable file |
| `library` | library | - |
| `link-error` | link error | linker error |
| `linker` | linker | linking |
| `object-file` | object file | - |
| `shared-library` | shared library | dynamic library, DLL |
| `static-library` | static library | module library |
| `translation-unit` | translation unit | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-basics-a-4 | must | missing-item | `basics/build` | The page compiles by hand with `cl /c main.cpp` and runs `cmake` in a terminal. On Windows `cl`, and the CMake that `start/install` installed with Visual Studio's C++ CMake tools, are on the PATH only in Visual Studio's developer terminal: in a plain PowerShell both are "not recognized". On macOS the CMake.app that `start/install` names is not on the PATH either. The editor finds both by itself, so nothing before this page needed the PATH; CI enters the developer environment for the same reason. | The page's first terminal step opens the right terminal per OS: the x64 Native Tools prompt or Developer PowerShell for VS on Windows (x64, as the editor's modules are); on macOS `brew install cmake` or CMake.app's command-line install; then `cmake --version` and `cl` or `c++ --version` as the check (about 150 words). The Coin Run item's by-hand build runs in the same terminal. | `allocation/basics-a.md:1009`, `:1022-1024`, `:1030-1031`; `allocation/start.md:157-158`; `Docs/Releases/PackageReadme.md:53-60`; `StrataEditor/src/Editor/ScriptToolchain.cpp:303`, `:469`; `.github/workflows/ci.yml:95-113` |
| critic-basics-a-6 | must | missing-item | `basics/programming-3` (`new:70`) | The page has the reader write headers (`Coin.h`, a `Counter` class, `BobbingCoin` built on `Coin`), but no page of the plan teaches `#pragma once` or include guards. A header that one source file includes twice, directly and through another header, defines its class twice, and the build stops with a redefinition error. Every header of the samples and of the SDK starts with `#pragma once`, and AGENTS.md asks it of every header. | The section on files of code adds `#pragma once` as the first line of every header, with the error it prevents shown once (about 100 words); `basics/build` names include guards as the older form in one sentence beside translation units. | `allocation/basics-a.md:321-323`, `:363`, `:366-367`; a search of `allocation/*.md` for "pragma once" and "include guard" finds nothing; `Samples/Tetris/Scripts/TetrisGame.h:1`; `StrataScriptCore/Include/StrataScript/Script.h:1`; `AGENTS.md:150` |
| critic-basics-a-18 | should | missing-item | `basics/tools` | Terminal facts that later pages rely on are not on the page. Ctrl+C in a terminal stops the running program and does not copy; headless runs and `core/first-frame`'s exercises use it. `&&` joins two commands in a POSIX shell but is an error in Windows PowerShell 5.1, the PowerShell that Windows ships, and the scripts' `CMakeLists.txt` gives its build-by-hand line with `&&`, which `basics/build`'s Coin Run item runs. PowerShell reads `$env:LOCALAPPDATA`, not the `%LOCALAPPDATA%` the Covers writes. And the Covers runs `python Tools/<tool>.py`, but the release ships no `Tools` folder and no page installs Python. | Add Ctrl+C; joining commands (`&&` in bash and zsh; in Windows PowerShell 5.1 two lines, or `;` with a check of `$?`); and `$env:` beside `%...%` (about 180 words). The Python example says that the tools come with Strata's source on track E (`core/first-change`) and how Python is started on each OS. | `allocation/basics-a.md:95`, `:97-99`, `:1030-1031`; `Docs/Releases/PackageReadme.md:75-79`; `StrataEditor/src/Editor/ScriptProject.cpp:218`; `allocation/core.md:349`; `CMake/StrataPackaging.cmake:55-85` |
| critic-basics-a-19 | should | missing-item | `basics/build` (`new:172`, `new:221`) | The Practice builds the two-file program in Debug and in Release with CMake on every system, but the page never says that the choice is made in two different places. With Visual Studio and Xcode the build step takes `--config Release`; with Ninja and Makefiles, the usual generators on Linux and macOS, the configure step takes `-DCMAKE_BUILD_TYPE=Release` and `--config` changes nothing, so the reader gets an unoptimized build without a word. The editor makes the same distinction for scripts. The term "multi-config generator" is homed on `engineering/building`, later on track E. | The CMake section teaches single-config and multi-config generators and where each takes the configuration, and the Practice's step shows both in OS tabs (about 120 words); `engineering` passes the term's entry of `build-test:617-620` to `basics/build`, or the page holds a `use` row. | `allocation/basics-a.md:1022-1026`, `:1063`; `allocation/engineering.md:72`; `StrataEditor/src/Editor/ScriptBuild.cpp:434-436` |
| critic-basics-a-29 | could | shape | `basics/build` (`new:221`) | The Hard exercise swaps two static libraries on the link line to see the error, which only GNU's linker gives; the linkers of MSVC and Apple do not depend on that order, so readers on Windows and macOS cannot do it. | Mark the exercise as Linux only, with the captured output for the others, or give them a link error they can make (a library left off the link line) (about 40 words). | `allocation/basics-a.md:1014-1016`, `:1063` |
