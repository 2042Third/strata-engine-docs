# Notes: basics/build

## New terms

- symbol: a name that an object file defines or needs, such as a function; this page is the home; aliases: none.
- declaration: a statement that a name exists and what type it has, without its body; this page is the home.
- definition: the one place that makes a declared thing exist, such as a function's body; this page is the home.
- one-definition rule: a name may be declared in many translation units and must be defined in exactly one program-wide; this page is the home.
- static initialization: the building of a program's global variables before `main` begins, in an order C++ leaves open between source files; this page is the home.
- target (CMake): a thing CMake builds, such as an executable or a library; this page is the home.
- generator (CMake): the part of CMake that writes the files of one build system; this page is the home.
- multi-config generator: a generator whose build folder holds every configuration and takes it in the build step with `--config`; this page defines it (the glossary may home it on `engineering/building`).
- cache (CMake): the file `CMakeCache.txt`, where CMake keeps its settings between runs of the configure step; this page is the home.
- optimization: the compiler rewriting code into machine code that does the same job in less time; this page is the home.
- debug information: data beside the machine code that tells a debugger which instruction belongs to which line and where each variable lives; this page is the home.

## Requests

- extra-words.txt: optimization, optimizes, optimized (the page uses them 7 times; the topic of the Debug and Release section has no common word).
- No external host: the Further reading entries cite Kitware, John R. Levine and Microsoft without links.
- The words "GNU" and "Makefiles" are avoided on the page (Linux's linker `ld`, the generator `Unix Makefiles` as code); a page about the GNU tools needs "GNU" and its acronym entry.

## Not verified

- The MSVC command lines `cl /EHsc /c`, `link ... /OUT:` and their output: no MSVC at hand; they follow Microsoft's documented flags.
- That MSVC's and Apple's linkers do not depend on the order of static libraries; the wording "Undefined symbols" and "unresolved external symbol" (`LNK2019`, `LNK1120`); general knowledge.
- The menu item "How to Install For Command Line Use" of CMake.app, and that **Developer PowerShell for VS** starts the 64-bit tools (the check `cl` ending in "for x64" is general knowledge).
- Every shown output (`nm`, the compile and link errors, the Ninja lines, `-O3 -DNDEBUG`, the assert message, the file sizes and the 0.63 s and 0.10 s times) comes from MinGW GCC 15.2 and CMake with Ninja on Windows, one run; Linux, macOS and Visual Studio word them differently, which the page says.
- That `/OPT:ICF` gives two functions one address (general knowledge); at the pin it is only seen in `CMake/StrataConfigurations.cmake` and `StrataScriptCore/CMake/StrataScriptModule.cmake`.
- That the tests also link the engine's static libraries (the page names the editor and the runtime); `CMake/StrataLayers.cmake` makes each layer `STATIC`.

## Findings not applied

- critic-basics-a-6 names `basics/programming-3` for the `#pragma once` teaching; this page only adds the sentence on include guards beside the first header, as the finding asks (applied); the rest is not this page's.
- critic-basics-a-18 names `basics/tools`; the `&&` fact it needs from this page is in the answer of Practice 5.
- critic-basics-a-4, -19 and -29 are applied (terminal section; single-config and multi-config generators with tabs; the Hard exercise's variant for Windows and macOS). The term "multi-config generator" is defined here in bold, though the glossary homes it on `engineering/building`.
- Item `build-test:277` and `build-test:380` are linked only: the page names the three configurations and links `engineering/building` and `engineering/cmake`; it does not teach configure, build and test as three steps (test is Strata's ctest, left to `engineering/cmake`).

## Clerk

- Admitted: symbol, definition, static initialization, Target (CMake), Cache (CMake), optimization (aliases optimize, optimizes, optimized, optimizing: a word of the field, a term rather than extra words).
- Refused: declaration (homed on `basics/programming-3`), one-definition rule (an alias of ODR, `scripting/abi-sdk`), generator and multi-config generator (homed on `engineering/building`), debug information (homed on `basics/debugging`): only their homes word them.

## Track walk E-final-2

Checked on Windows 11 with Visual Studio 2026 Community (19.50) in `docs-work/walkfix-E2/hello/` (`run.cmd`, `run2.cmd`, `pipe.ps1`, `pipe2.ps1`), 2026-11-24:

- The Start-menu shortcut **Developer PowerShell for VS** runs the 32-bit Windows PowerShell (`SysWOW64`) with `Enter-VsDevShell <instance>` and no `-Arch`: `cl` prints "for x86", `VSCMD_ARG_TGT_ARCH=x86`. **x64 Native Tools Command Prompt for VS** runs `vcvars64.bat`: "for x64". `where cmake` there lists the MSYS2 CMake first on this machine, then the one in `Common7\IDE\CommonExtensions\Microsoft\CMake`; MSYS2's CMake also offers the Visual Studio generators (the editor used it with "Visual Studio 18 2026").
- Every Windows line of the page runs in the Command Prompt as written: `cl /EHsc /c`, `link ... /OUT:hello.exe`, `.\hello.exe`, `lib`, the CMake lines, `echo -5 | .\stop.exe` (Debug: `Assertion failed: coins >= 0 && "coins cannot be negative", file ...stop.cpp, line 10`, exit 3; Release: `coins: -5`).
- `dumpbin /symbols main.obj | findstr MakeGreeting`: `UNDEF notype () External | ?MakeGreeting@@... (class std::basic_string<...> __cdecl MakeGreeting(...))`; for `Greeting.obj` `SECT5 ... External` plus lines marked `Static` (`$unwind$`, `$pdata$` ...).
- The missing `;` at the end of line 7: `main.cpp(8): error C2143: syntax error: missing ';' before 'return'`.
- Windows PowerShell 5.1 piping `echo -5` to a program: with the console at code page 65001 it sends `ef bb bf 2d 35 0a` (a byte order mark), also with `$OutputEncoding` ASCII, and `std::cin >> coins` fails (`coins: 0`); under `chcp 437` it sends `2d 35 0a`. Setting `[Console]::InputEncoding` to UTF-8 without a mark also removes it. The Command Prompt sends the text alone.
- The test-out answers "4. ..." and "0. ..." were parsed as ordered lists, so their numbers vanished; they now start with words.
- `tools/sketches.py` runs a sketch without `stdin=subprocess.DEVNULL` (line 216), so `basics-build-stop.cpp`, which reads `std::cin`, waited and failed the 10-second limit once when pagecheck ran from a shell with an open input; reported to the tool builder.
