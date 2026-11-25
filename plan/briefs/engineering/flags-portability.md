# Brief: `engineering/flags-portability`

| Field | Value |
| --- | --- |
| Title | Compiler flags, compile time and portability |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `engineering/cmake`, `basics/numbers` |
| From | build-test ch. 4 (the warning policy, instruction sets, precompiled headers, header weight, compiler caches, three compilers and their traps, CompatLint); home of FMA contraction and floating-point determinism |
| Unit | `plan/allocation/engineering.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `engineering/flags-portability` — Compiler flags, compile time and portability

**Covers.** The job: how every first-party object is compiled (the warnings, the instruction sets, the precompiled
headers) and how the build stays fast and portable across three compilers and two standard libraries; targets are
`engineering/cmake`'s and vendor flags `engineering/third-party`'s. The problem: one source gives different programs,
warnings and even numbers under different compilers and flags. Warnings as a policy: `/W4 /permissive-` and
`-Wall -Wextra`, errors in first-party code (`STRATA_WARNINGS_AS_ERRORS`, which also makes Slang's warnings errors),
vendor code silenced as a whole with `/W0` or `-w` and taken in as SYSTEM includes, the test program's workaround for
GCC before 14.4 with its reason, and the rule never to silence a warning where it appears. The code is
`strata_configure_target`: configuration definitions through generator expressions, the MSVC switches (`/utf-8`,
`/Zc:__cplusplus`, `/Zc:preprocessor`, `/bigobj`), `NOMINMAX`, `WIN32_LEAN_AND_MEAN` and `_CRT_SECURE_NO_WARNINGS`,
which turns off MSVC's deprecation of standard C functions in favour of `_s` variants that other platforms lack: a
silencing for the whole project, set beside the rule and with its reason. Instruction sets and
floating-point determinism, the book's home of FMA contraction: what an instruction-set extension is; why `-mfma`
lets a compiler fuse `a*b+c` into one rounding and so change a result, shown by a toy whose two results differ in the
last bit; `strata_engine_cpu_options` and the one `StrataEngineCodegen` target every engine object links, so that
leaving a module out changes no other code generation; `-mfma` by default, left out only when
`STRATA_CROSS_PLATFORM_DETERMINISTIC` is on (off by default), so that of the engine's code only box3d's results match
across platforms, through its own `-ffp-contract=off`, named with a link. MSVC gets `/arch:AVX2` only with the Visual
Studio generators, and zstd's `/arch:AVX2` follows the same test: `cl` under Ninja gets none, so CI's `windows-ninja`
jobs and every cached Windows build compile other engine code than the `windows-vs2022` release and the `windows`
preset the perf budgets were measured with (about 120 words). The processor a release needs: the Windows and Linux
archives compile every engine object for AVX2 (the macOS archive is ARM64), so the editor, the runtime and every
exported game need a processor with AVX2, and nothing checks for it at startup: an older processor stops at an illegal
instruction without a message (about 100 words, and a row of "What Strata does not do"). Compile time: a precompiled header per target (`stpch.h` per layer library,
`EditorPch.h`, `TestsPch.h`), and what may go in one (`Architecture.PrecompiledHeaders`: the standard library, vendor
headers and the Core basics, never a header that changes); include what you use anyway; light headers (forward
declarations, `json_fwd.hpp`, `Scope<>` with the destructor out of line, no `std::span` of a declared-only JSON type,
`Architecture.HeaderWeight`); compiler caches (ccache or sccache as a launcher, Ninja or Makefiles only, `/Z7` debug
information, precompiled headers off by default because the caches do not cache MSVC's); unity builds, which Strata
does not use. What the work measured (about 70 words): in Debug the precompiled headers cut the compile time of the
editor's and the tests' objects by about 40%; after wave 4's work on compile time a clean Debug build on the Mac took
13% less CPU time and an edit of `Scene/Components.h` 28% less, and warm CI builds took 2 to 6 minutes instead of 13
to 22. Portability: MSVC, GCC and Clang with libstdc++ and libc++, and what "works on my machine" hides (a
missing include, `size_t` against `uint64_t` on macOS, no floating-point `std::from_chars` in Apple Clang 15's libc++);
the supported minimums (MSVC 19.40, GCC 13, Clang 17, Apple Clang 15) against what CI builds with (GCC 14, and Apple
Clang 17 on `macos-15`), so that GCC 13, Ubuntu 24.04's default `g++`, is never built and Apple Clang 15 is stood in
for only by CompatLint's LLVM 16 (about 60 words); `Tools/CompatLint.py`, which compiles changed files with GCC 14 and
LLVM 16 from the Debug build's exact commands without the precompiled header, and which needs a configured and built
Ninja Multi-Config tree of the `linux` or `macos` preset (`build-Debug.ninja`) and those two compilers (Homebrew's
paths by default; `--build`, `--gcc`, `--clang` and `--libcxx` name others), and exits 0 when every file compiles
without errors or warnings, 1 otherwise and 2 for a usage error (a missing compiler, a build it cannot read). The paragraph that introduces the page's first
Python fence (`adapt`) says in one or two sentences what differs from C++ in it: no page of the book teaches reading
Python, so the page supplies it (R45). What went wrong before: Apple Clang 17 miscompiled `std::abs(x) > 0 ? x : 0`, and every
gamepad axis held to its negative side read 0; a `std::span` of declared-only JSON broke CI's macOS build. Exercises:
time a clean Debug build with and without precompiled headers, and twice through a cache; run CompatLint on a change
that leans on the precompiled header (Linux and macOS only, since it reads a Ninja build of those presets); trace it
yourself: follow the instruction sets by a search from the `STRATA_USE_*` options through `strata_engine_cpu_options`
and `StrataEngineCodegen` to one engine object's compile line, and say why it holds `-mfma` on Linux x64,
`/arch:AVX2` in a Visual Studio build, and neither under `windows-ninja` or on ARM64. At the end the reader can say why a warning fails the build, why a flag can
change a number, what belongs in a precompiled header, and how to catch what CI's older compilers reject before a
push.

**Leaves out.**

- How targets are made and linked → `engineering/cmake`
- box3d's own flags and the vendor wrapper → `engineering/third-party`
- The CI matrix and the compilers it builds with → `engineering/ci`
- Floating point and rounding in general → `basics/numbers`
- `stpch.h` first in every engine source, as a rule of the code style → `core/conventions`
- Determinism of parallel work → `core/jobs`
- Choosing these options for a build → `engineering/building`
- The processor an exported game needs, as a game maker reads it → `make/export`

**Fit.** `fits`: about 5,980 words against L (5,000). Four concepts (warnings, instruction sets and FMA, compile time,
portability) of 400 to 450 words each before the code take the most, with three excerpts, five rules, the toy, the
history of two breaks and three exercises.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `build-test:290` | concept | home | Warnings as a policy: `/W4`, `-Wall -Wextra`, errors in first-party code, vendor code silenced; the mistake of silencing a warning where it appears |
| `build-test:301` | concept | home | Instruction sets and floating-point determinism: SSE, AVX, FMA; why `-mfma` changes results; one code-generation set for every engine object; the mistake of thinking flags never change numbers |
| `build-test:296` | concept | home | Compile time: precompiled headers, forward declarations, header weight, compiler caches, unity builds (not used); the trade-off that precompiled headers hide missing includes; the measured payoff (about 40% less Debug compile time of the editor's and tests' objects; after wave 4, 13% less CPU time for a clean Debug build on the Mac, 28% for an edit of `Scene/Components.h`, warm CI builds of 2 to 6 minutes instead of 13 to 22) |
| `build-test:292` | concept | home | Portability across compilers and standard libraries; the supported minimums (MSVC 19.40, GCC 13, Clang 17, Apple Clang 15) against what CI builds with (GCC 14, Apple Clang 17), so GCC 13 is never built and Apple Clang 15 is stood in for only by CompatLint's LLVM 16; CI on three OSes, `ci/<name>` branches and CompatLint as Strata's answers; the mistake of taking the newest local compiler for CI |
| `build-test:31` | feature | home | `STRATA_WARNINGS_AS_ERRORS`, and Slang's warnings made errors with it |
| `build-test:36-38` | feature | home | The compiler cache (launcher, refused with Visual Studio generators, `/Z7`, precompiled headers off by default); precompiled headers per target; the `STRATA_USE_*` options to `StrataEngineCodegen`; MSVC's `/arch:AVX2` only with the Visual Studio generators (zstd's too), so `windows-ninja` builds, CI's Windows jobs and every cached build among them, compile other engine code than the `windows-vs2022` release and the `windows` preset of the perf budgets |
| `build-test:44-46` | feature | home | The warning policy of `strata_configure_target`, with `_CRT_SECURE_NO_WARNINGS` and why a project defines it (MSVC deprecates standard C functions for `_s` variants other platforms lack: a project-wide silencing set against the rule); vendor warnings off; the tests' GCC workaround and its reason |
| `foundation:167` | feature | home | `stpch.h` and what it holds, as the foundation inventory lists it; the rule that every engine source includes it first stays `core/conventions`' |
| `build-test:182`, `build-test:183` | feature | home | `Architecture.PrecompiledHeaders` and `Architecture.HeaderWeight`: what each refuses |
| `build-test:202`, `build-test:222` | feature | home | `Tools/CompatLint.py`, which the inventory lists twice (in CI and among the tools): what it needs (a configured and built Ninja Multi-Config tree of the `linux` or `macos` preset, read from `build-Debug.ninja`; GCC 14 and LLVM 16, Homebrew's paths by default), the options `--build`, `--gcc`, `--clang` and `--libcxx`, and its exit codes 0, 1 and 2 |
| `build-test:381` | code | home | `CMake/StrataCompilerOptions.cmake:95-120`: the warning policy and the configuration definitions through generator expressions |
| `build-test:382` | code | home | `CMake/StrataCompilerOptions.cmake:39-93`: `strata_engine_cpu_options`, the flags per compiler; `-mfma` by default, left out only when `STRATA_CROSS_PLATFORM_DETERMINISTIC` is on (off by default), so of the engine's code only box3d's results match across platforms |
| `new:2` | code | home | `Tools/CompatLint.py:64-92`: `adapt`, which takes the Debug build's command, drops the precompiled header in both compilers' forms and swaps the compiler |
| `new:3` | not-done | home | No unity builds: every source compiles as its own translation unit. Evidence: `git grep -niE "UNITY_BUILD" 822a7a46 -- CMakeLists.txt CMake Strata/CMakeLists.txt StrataTests/CMakeLists.txt StrataEditor/CMakeLists.txt` finds nothing |
| `new:24` | feature | home | A limit: the release builds need a processor with AVX2. The Windows archive is built with the Visual Studio generator (`windows-vs2022`), so MSVC compiles every engine object with `/arch:AVX2`; the Linux archive with GCC and `-mavx2 -mbmi -mpopcnt -mlzcnt -mf16c -mfma`; the macOS archive is ARM64 and gets none. The editor, the runtime and every exported game inherit the requirement (about 100 words). Evidence: `CMake/StrataCompilerOptions.cmake:30`, `:44-83`; `Strata/CMakeLists.txt:5-12`; `.github/workflows/release.yml:102-116` |
| `new:25` | not-done | home | No check at startup for the processor's AVX2: an older processor stops at an illegal instruction without a message (book.md, "What Strata does not do"; on the engine's list for v0.8.1). Evidence: `git grep -niE -e avx2 -e cpuid -e cpu_supports 822a7a46 -- Strata/src StrataRuntime StrataEditor/src StrataCLI` finds only `Strata/src/Strata/Core/Hash.cpp:13`, `:109`, `:112`, `:119`, the SSE 4.2 check for CRC32 (`Hash.cpp:107-121`) |
| `build-test:483` | rule | home | CI always builds with warnings as errors; never silence a warning where it appears; vendor code is silenced as a whole |
| `build-test:485` | rule | home | Never put an engine, editor or test header that changes into a precompiled header |
| `build-test:487` | rule | home | Include what you use, although the precompiled header has it: the lint and cached CI builds compile without it |
| `build-test:489` | rule | home | Keep headers light; no `std::span` of a declared-only JSON type, which old libc++ instantiates |
| `build-test:499` | rule | home | Compiler caches need Ninja or Makefiles and embedded debug information, and do not cache MSVC's precompiled headers |
| `build-test:564` | hands-on | home | Time a clean Debug build with and without `STRATA_PRECOMPILED_HEADERS`, and twice through a cache with `windows-ninja` |
| `build-test:566` | hands-on | home | `Tools/CompatLint.py --changed-since main` on a change that leans on the precompiled header; Linux and macOS only: it needs a configured and built Debug tree of the `linux` or `macos` preset and GCC 14 and LLVM 16, and exits 2 without them |
| `new:26` | hands-on | home | Trace it yourself, by a search: the instruction sets from the `STRATA_USE_*` options through `strata_engine_cpu_options` and `StrataEngineCodegen` to one engine object's compile line; why it holds `-mfma` on Linux x64, `/arch:AVX2` in a Visual Studio build and neither under `windows-ninja` or on ARM64 (about 200 words). Evidence: `CMake/StrataCompilerOptions.cmake:27-37`, `:44-93`; `Strata/CMakeLists.txt:5-12`; `CMake/StrataLayers.cmake:229` |
| `build-test:626` | term | home | SYSTEM include |
| `build-test:629-636` | term | home | Precompiled header; forward declaration; compiler cache; compiler launcher; `/Z7` and PDB (two entries); instruction set extension; FMA contraction; determinism (cross-platform) |
| `foundation:618`, `foundation:641` | term | home | The precompiled header (`stpch.h`), one entry with `build-test:629`; FMA, one entry with `build-test:635` |
| `build-test:93` | feature | link | box3d's `-ffp-contract=off`, taught on `engineering/third-party` |
| `build-test:193` | feature | link | The compilers of the CI matrix |
| `build-test:500` | rule | link | Large integrations go through `ci/<name>` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Floating point, rounding, and why two results can differ in the last bit | `basics/numbers` | must |
| Translation units, object files, headers and the preprocessor | `basics/build` | must |
| `#include`, macros and `#if` | `basics/cpp-modern` | must |
| Targets, PUBLIC and PRIVATE, generator expressions, the layer libraries | `engineering/cmake` | must |
| CPU instructions and SIMD | `basics/computer` | helps |
| `std::span` and incomplete types | `basics/cpp-modern` | helps |
| Smart pointers and destructors (`Scope<>`) | `basics/cpp-memory` | helps |
| The code style's include rule | `core/conventions` | helps |
| CI's jobs | `engineering/ci` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `compiler-cache` | Compiler cache | - |
| `compiler-launcher` | Compiler launcher | - |
| `determinism-cross-platform` | Determinism (cross-platform) | - |
| `fma-contraction` | FMA contraction | - |
| `forward-declaration` | Forward declaration | - |
| `instruction-set-extension` | Instruction set extension | - |
| `precompiled-header` | Precompiled header | pch, stpch.h, FMA, fused multiply-add |
| `system-include` | SYSTEM include | - |
