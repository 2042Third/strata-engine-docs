# Allocation: engineering

## `engineering/building` — Building Strata

**Covers.** The goal: build Strata from source in the configuration, with the generator and with the options a piece
of work needs, and know where every result lands. What must be true first: the clone at the book's pin with its
submodules and one Debug build, as `core/first-change` left them, and the C++ tools of `start/install`; the supported
minimums (CMake 3.25, MSVC 19.40, GCC 13, Clang 17, Apple Clang 15) and the network for the first configure, which
downloads Slang once into a per-user cache, with a link to the box of `core/first-change` that names the Linux
development packages and the Vulkan SDK as optional (about 80 words). The steps, in
order. Choose the configure preset of the reader's OS: `windows` (Visual Studio 2026), `windows-vs2022`,
`windows-ninja` (Ninja Multi-Config with `cl`, from a Visual Studio developer environment), `linux` and `macos` (with
its deployment target of macOS 14); a short excerpt of `CMakePresets.json` shows the hidden `base` preset, inheritance
and the host conditions. Configure, and read the log: the Slang line (downloaded once, then cached), the line of the
compiler cache when it is on, and the packaging line a build without the CLI prints. Build Debug, Release or Dist
through the build presets `<preset>-debug`, `-release` and `-dist`, with one sentence on each (Release keeps the
asserts; Dist compiles them out and is what games ship). Find the results: programs in `build/<preset>/bin/<Config>/`,
static libraries in `lib/`, the shader tool in `tools/`, `compile_commands.json` for code editors (the Ninja presets
write it), and the Visual Studio solution's folders. Run the tests through the test presets, by label and side by side
(`ctest --preset <preset>-debug -LE "gpu|perf" -j 8`). Turn options on and off: the program switches
`STRATA_BUILD_EDITOR`, `_RUNTIME`, `_CLI` and `_TESTS`; `STRATA_ENABLE_TRACY`; `STRATA_WARNINGS_AS_ERRORS`, for local
experiments only; the optional modules and `STRATA_WITH_GLFW`, which a build with the editor refuses; precompiled
headers, the compiler cache and the instruction sets, each named in one sentence with a link. The option list includes
`STRATA_WITH_GLFW`, which the Developer Guide's list in "Building" leaves out. The trap of this step: cached options
survive a new configure, so a missing program may be an old `OFF` (`cmake -U`, or a fresh build directory). Make a
second build directory for a variant, and one per agent when several work side by side (`-B build/agent-<name>`).
Configure again after adding or removing a source file. Set up the Vulkan validation layer per OS, in tabs: the
Vulkan SDK's layer on Windows and Linux; on macOS Homebrew's layer, whose manifest is copied with the library's full
path into a folder that `VK_ADD_LAYER_PATH` names. Each step says its one or two common failures and the way back.
Result: a build tree the reader can explain folder by folder. Variations: a cached Windows build with `windows-ninja`
and `STRATA_COMPILER_CACHE=ON`; a Dist build of every target; a build without physics and audio, and so without the
editor; a game maker who wants a newer engine than the release. Exercises: build from a clean clone on the reader's OS
and run the tests without the `gpu` and `perf` labels; read the configure log of a build configured with
`-DSTRATA_BUILD_CLI=OFF`. The whole table of options, presets and labels is
`reference/build`'s; this page names the options a builder changes. At the end the reader can choose a preset and a
configuration for a task, change options without being caught by the cache, and run Debug builds under validation on
their OS.

**Leaves out.**

- The Linux development packages and the rest of what a source build needs, in the short build's box → `core/first-change`
- What each CMake file does and how the targets are made → `engineering/cmake`
- What precompiled headers, compiler caches and instruction-set options cost and change → `engineering/flags-portability`
- How the test program, its shards and its labels work → `engineering/test-program`
- The CI's jobs and the presets they build → `engineering/ci`
- Every CMake option, preset and test label in one table → `reference/build`
- What the validation layer reports and how to read it → `gpu/debugging`
- Installing a build and packing an archive → `engineering/releasing`

**Fit.** `fits`: about 3,385 words against M (3,000). Ten steps with their failures, the excerpt of the presets, two
figures, four variations and two exercises take the most; the options are a short list, because the full table is
`reference/build`'s.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `build-test:55-58` | feature | home | The configure presets with their generators, host conditions and the macOS deployment target; the 15 build presets and 15 test presets named `<preset>-<config>`; `test-base` (output on failure, no tests found is an error); one build directory per agent working side by side |
| `build-test:29`, `build-test:30` | feature | home | The program switches and `STRATA_ENABLE_TRACY`, as options a builder turns off or on; what Tracy shows is `core/profiling`'s |
| `build-test:39` | feature | home | Debug, Release and Dist: what each keeps and which build preset makes it; how Dist is made is `engineering/cmake`'s |
| `build-test:40` | feature | home | C++20 without extensions, and the `compile_commands.json` that configures with the Ninja generators write for code editors (`CMAKE_EXPORT_COMPILE_COMMANDS`) |
| `build-test:43` | feature | home | Where programs, shared libraries and static libraries land |
| `build-test:250` | feature | home | The validation layer set up per OS: the Vulkan SDK's layer; on macOS Homebrew's manifest copied with the library's full path, named by `VK_ADD_LAYER_PATH` |
| `build-test:379` | code | home | `CMakePresets.json:4-49`: the configure presets, the hidden `base` with `build/${presetName}`, inheritance, the generators and the host conditions; the build and test presets are named after them |
| `build-test:458` | figure | home | A text capture of a configure log: the Slang line (`(cached)` on the second configure) and the compiler-cache status line |
| `build-test:461` | figure | home | Visual Studio's Solution Explorer after a configure: the `Strata/Layers`, `Vendor`, `Strata/TestScripts` and "Generated Shaders" folders |
| `build-test:478` | rule | home | Configure again after adding or removing a source file: the Visual Studio generator re-globs during the build but compiles with the stale project |
| `build-test:482` | rule | home | Each agent working side by side gets its own build directory: two builds in one tree corrupt each other |
| `build-test:498` | rule | home | Cached options survive a new configure: a missing target may be an old cached `OFF` |
| `build-test:551` | hands-on | home | Build from a clean clone on your OS: configure a preset, build Debug, run the tests without the `gpu` and `perf` labels |
| `build-test:553` | hands-on | home | Read the configure log: find the Slang line, the compiler-cache line, and the packaging line of a build configured with `-DSTRATA_BUILD_CLI=OFF` |
| `build-test:597` | hands-on | home | The variation for a game maker who wants a newer engine: the presets, the per-user Slang cache, where the editor lands |
| `build-test:617-620` | term | home | Four entries: generator (CMake); multi-config generator; preset; cache variable and `CMakeCache.txt` (two entries) |
| `build-test:627` | term | home | Two entries, Debug and Release; the page teaches every configuration in full and uses the term Dist, whose entry is `core/first-change`'s (`foundation:612`, R31 D33) |
| `scripting:578` | term | link | Dist, the shipping configuration (no host call counters), whose entry is `core/first-change`'s |
| `build-test:759` | open | home | The page's option list includes `STRATA_WITH_GLFW`, which the Developer Guide's "Building" list omits (it is described under "Optional modules") |
| `build-test:91` | feature | use | The submodules the clone already holds, and updating them after a pull |
| `build-test:31` | feature | use | `STRATA_WARNINGS_AS_ERRORS` as an option, off only for local experiments |
| `build-test:32-35` | feature | use | The optional modules and the window backend as options, and the editor's refusal to build without them; their CMake is `engineering/cmake`'s |
| `build-test:36-38` | feature | use | The compiler cache, precompiled headers and instruction sets as options, one sentence each |
| `build-test:277` | concept | use | Configure, build and test as three steps, each one command with a preset |
| `build-test:118` | feature | use | The labels the test step leaves out (`gpu`, `perf`), named and linked |
| `build-test:561` | hands-on | use | The variation without physics and audio; the exercise that inspects it is `engineering/cmake`'s |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The short source build: clone, submodules, configure, build Debug, run one test | `core/first-change` | must |
| Running the tests by label with `ctest` | `core/first-change` | must |
| A terminal: run a program with arguments, quote a path, set an environment variable | `basics/tools` | must |
| CMake's configure and build steps; compiling and linking | `basics/build` | must |
| The C++ build tools of the reader's OS | `start/install` | must |
| Strata's programs: the editor, the runtime, the CLI and the test program | `core/map` | helps |
| Optional modules | `core/layers-registries` | helps |
| Precompiled headers and compiler caches | `engineering/flags-portability` | helps |
| What the validation layer reports | `gpu/debugging` | helps |
| Tracy | `core/profiling` | helps |

**Starting state.** No checkpoint: the page changes no engine code. The reader's clone of the engine at the book's
pin, with its submodules and the Debug build `core/first-change` made in `build/<preset>/`; the C++ tools and CMake of
`start/install`; for the validation step, the Vulkan SDK (Windows, Linux) or Homebrew's `molten-vk`,
`vulkan-loader` and `vulkan-validationlayers` (macOS).

**Command-only steps.** none

## `engineering/cmake` — Inside Strata's CMake

**Covers.** The job: turn the source tree into targets (one library per layer, the programs, the tests) so that the
architecture's rules hold by construction. Compiler flags are `engineering/flags-portability`'s and generated code is
`engineering/generated-code`'s. The problem, in the part's full section on it: a large C++ project needs targets that
carry their include folders, definitions and links to whoever uses them, and something that stops code from
depending on what it should not; the approaches to enforcing layers (conventions, include checkers, separate
libraries, link-closure checks, linker-map checks) in a table, and Strata's choice: all of them. The map: configure,
build and test as three steps with the files each reads and writes (`CMakeCache.txt`, `Layers.json`,
`LayerLibraries.json`, `ShaderEntries.txt`, `bin/<Config>`), and the target graph (the layer libraries, `Strata` and
`StrataTooling`, the editor's two libraries, the runtime, the CLI, the tests, the script modules and the vendor
libraries, with the runtime's forbidden set marked). Targets and usage requirements taught on a toy of 40 lines: two
static libraries and an interface target, where a header leaks through a link made PUBLIC that should be PRIVATE;
static, shared, module and interface libraries; SYSTEM includes; `EXCLUDE_FROM_ALL`; generator expressions. The
contract: the layer table is the build. The real code in the order configure runs it. The root `CMakeLists.txt`: the
guards with their fix in the message (in-source builds, missing submodules), the options, the editor's need for every
module and a window, the subdirectories, the deferred link-closure check, packaging and tests. The three
configurations: Dist reuses Release's flags and adds `ST_DIST`, imported targets map Dist to Release, the static MSVC
runtime so that exported games need no redistributable, `/OPT:REF /OPT:ICF` in Release and Dist, and the debug
information format a compiler cache needs. The glob of every engine source; `strata_add_layer_libraries`, which gives
each file to exactly one layer (the ownership loop, and globs turned into regular expressions with the analyzer's
meaning) and makes `Strata_<Layer>` static, or interface when nothing compiles, linking only the built layers of its
`MayInclude`, tooling layers `EXCLUDE_FROM_ALL`; `strata_layer_link`, which attaches vendor libraries and refuses
layer libraries; `Strata` and `StrataTooling` as what a game and what a tool links; `LayerLibraries.json`, written at
the end of configure with `cmake_language(DEFER)` from what the targets really link. Optional modules:
`STRATA_WITH_PHYSICS`, `_AUDIO` and `_ANIMATION` leave their layer and its vendor library unbuilt, and `STRATA_WITH_GLFW` swaps
`Platform/GLFW` for `Platform/NoWindow`; `ST_WITH_*` are 1 or 0 definitions on `Strata_Core`, never a header, so a
file that misses an include cannot read 0; compile-time exclusion set against plugins loaded at run time. The
Windows application manifest that `StrataEditor`, `StrataRuntime`, `StrataCLI` and `StrataTests` get (UTF-8 code page,
long paths); `strata_copy_runtime_resources` is named as a helper that no target calls at the pin. Last, "games contain no tooling" proven twice: the
link-closure walk at the end of configure, which reports the path to a forbidden target, and `CheckNoTooling.cmake`,
which reads the runtime's linker map and first requires the objects every runtime holds, because a map that names
nothing proves nothing. The page's example: `StringUtils.h` of `core/first-change`, followed from the glob to
`Strata_Core` and its entry in `LayerLibraries.json`. Alternatives: one library, libraries listed by hand,
visibility rules of other build systems, run-time plugins. How it is tested: `Architecture.Libraries`,
`StrataRuntime.NoTooling` and the configure errors. Changing it safely: a new source file needs a configure, a new
folder a layer pattern, a vendor library a `strata_layer_link` row, never a wider `MayInclude`. Exercises: a file in a
folder no layer matches; a forbidden include and the closure error with its path; a build without physics and audio;
trace it yourself: follow a source of the audio layer, as the example followed `StringUtils.h`, from its pattern in
`Layers.json` through the glob and the ownership loop to `Strata_Audio` and its entry in `LayerLibraries.json`.
At the end the reader can say which target a file builds into and what it may link, read a configure error of the
layer table, and add a source, a folder or a vendor library correctly.

**Leaves out.**

- The rules of the layer table, their reasons and `Architecture.Layering` → `core/layers-registries`
- Choosing presets, configurations and options → `engineering/building`
- Warning flags, instruction sets, precompiled headers and compiler caches → `engineering/flags-portability`
- The vendor wrapper and the Slang fetch → `engineering/third-party`
- The shader build and the generated sources → `engineering/generated-code`
- The test program's target and its CTests → `engineering/test-program`
- The install rules and CPack → `engineering/releasing`
- Compiling and linking in general → `basics/build`

**Fit.** `fits`: about 6,475 words against L (5,000). Five concepts, six excerpts, five figures, two rules, three
exercises and the trace take the most. The count puts the page 25 words below L's top, so it has no room for more.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `build-test:277` | concept | home | Configure, build and test: what each step reads and writes, presets as one name per step; the mistakes (cached options, a file added without a configure) |
| `build-test:282` | concept | home | Targets and usage requirements: static, shared, module and interface libraries; PUBLIC, PRIVATE and INTERFACE; SYSTEM; `EXCLUDE_FROM_ALL`; the mistake of linking PUBLIC what should be PRIVATE |
| `build-test:286` | concept | home | Build configurations: what asserts compile to, why a shipping build differs, how other engines name theirs; Dist as Release's flags plus a definition; the mistake of testing only Debug |
| `build-test:319` | concept | home | Architecture enforced by the build: the approaches table (conventions, include checkers, separate libraries, link-closure and linker-map checks); the rules and their reasons stay `core/layers-registries`' |
| `build-test:323` | concept | home | Optional modules at compile time against plugins at run time; `ST_WITH_*` as definitions, not macros of a header; the guard rule is linked to `core/layers-registries` |
| `build-test:28` | feature | home | The root project and its guards with the fix in the message |
| `build-test:32-35` | feature | home | The optional modules, the window backend and `Platform/NoWindow`, the editor's need for every module, `ST_WITH_*` as definitions on `Strata_Core` |
| `build-test:41`, `build-test:42` | feature | home | The static MSVC runtime; `/DEBUG /OPT:REF /OPT:ICF` in Release and Dist |
| `build-test:47-49` | feature | home | `strata_copy_runtime_resources`, named as a helper that no target calls at the pin; the Windows application manifest (UTF-8 code page, long paths) that `StrataEditor`, `StrataRuntime`, `StrataCLI` and `StrataTests` add; the glob of sources with `CONFIGURE_DEPENDS`, shaders listed instead |
| `build-test:64-71` | feature | home | `strata_add_layer_libraries`, glob-to-regex, `LayerLibraries.json`, `strata_layer_link`, `Strata` and `StrataTooling`, the link-closure check, the linker-map check, the vendor libraries only tools build |
| `foundation:174`, `foundation:177` | feature | home | The per-layer static libraries and the tooling-free runtime, as the foundation inventory lists them: taught with `build-test:64-71` |
| `build-test:378` | code | home | `CMakeLists.txt:1-91`: a whole top-level file: the project, the guards, the options, the editor's rule, the subdirectories, the deferred closure check, packaging, tests |
| `build-test:380` | code | home | `CMake/StrataConfigurations.cmake:1-56`: three configurations, Dist with Release's flags, the static runtime, the debug information format a cache needs, the output folders |
| `new:1` | code | home | `Strata/CMakeLists.txt:14-29`: the call that makes the layer libraries from `Layers.json`, and `ST_WITH_*` as 1 or 0 definitions on `Strata_Core`, with the comment that says why not a header |
| `build-test:385` | code | home | `CMake/StrataLayers.cmake:155-186`: every file in exactly one layer, with the two configure errors |
| `build-test:386` | code | home | `CMake/StrataLayers.cmake:367-429`: the transitive walk of what a target links, with the path to each forbidden name, deferred to the end of configure |
| `build-test:387` | code | home | `StrataTests/Architecture/CheckNoTooling.cmake:47-80`: the required objects first, then the forbidden objects and libraries in the map (the inventory's lines 47-107 run past the file's 80 lines) |
| `build-test:420` | figure | home | The three steps and the files each reads and writes |
| `build-test:423` | figure | home | The target graph, tooling set apart from what games link, the runtime's forbidden set marked |
| `build-test:425` | figure | home | Sources, the rules of `Layers.json`, one library per layer, and the two configure errors |
| `build-test:427` | figure | home | "Games contain no tooling" proven twice: at configure by the closure walk, at link time by the map, at test time by `CheckNoTooling.cmake` |
| `build-test:459` | figure | home | Text captures of two configure failures made in a scratch copy: a source in no layer, and "StrataRuntime links tooling" with its path |
| `build-test:491` | rule | home | `ST_WITH_*` are definitions, never macros of a header: a missing include must not compile a module out |
| `build-test:496` | rule | home | Games link no tooling, proven at configure and on the linker map; a map that names nothing proves nothing, so required objects are checked first |
| `build-test:555` | hands-on | home | Add an empty source, build without configuring in Visual Studio, configure again; then a file in a folder no layer matches, and the error |
| `build-test:558` | hands-on | home | On a scratch branch, include an asset-pipeline header from a runtime layer: `Architecture.Layering` fails, and with the link added, the closure error names its path |
| `build-test:561` | hands-on | home | A second build directory with `-DSTRATA_WITH_PHYSICS=OFF -DSTRATA_WITH_AUDIO=OFF -DSTRATA_BUILD_EDITOR=OFF`: which libraries and test files are left out |
| `new:23` | hands-on | home | Trace it yourself, by a search: a source of `Strata/src/Strata/Audio/` from the pattern `Strata/Audio/**` of the layer `Audio` through the glob and the ownership loop to `Strata_Audio`, then its entry in the build's `LayerLibraries.json`; the answer names the lines (about 200 words). Evidence: `StrataTests/Architecture/Layers.json:56-60`; `CMake/StrataLayers.cmake:99-103`, `:155-186`; `Strata/CMakeLists.txt:14-17` |
| `build-test:613`, `build-test:615` | term | home | Interface library (CMake); usage requirements, with PUBLIC, PRIVATE and INTERFACE |
| `build-test:621-625` | term | home | Generator expression; `GLOB_RECURSE CONFIGURE_DEPENDS`; script mode (`cmake -P`); `cmake_language(DEFER)`; `EXCLUDE_FROM_ALL` |
| `build-test:655`, `build-test:656` | term | home | Link closure; linker map |
| `build-test:107` | feature | use | The test files a build without a module leaves out, read in the exercise; `engineering/test-program` teaches them |
| `build-test:478` | rule | use | Configure again after adding a file, as the glob explains it |
| `build-test:180`, `build-test:181` | feature | link | `Architecture.Layering` and `Architecture.Libraries`, which read the table and the file this page writes |
| `foundation:173` | feature | link | The layer table's fields, taught on `core/layers-registries` |
| `foundation:470` | rule | link | Never widen `MayInclude`; invert the dependency |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Compiling, linking and static libraries; `add_library` and `target_link_libraries` | `basics/build` | must |
| The layer table: `Paths`, `Exclude`, `MayInclude`, `Tooling`, `Option`; "no tooling in games" as a rule | `core/layers-registries` | must |
| Optional modules, and `#if ST_WITH_*` only in the composition root | `core/layers-registries` | must |
| Strata's programs and libraries | `core/map` | must |
| Debug, Release and Dist; configuring with a preset | `core/first-change` | must |
| Preprocessor definitions, macros and `#if` | `basics/cpp-modern` | must |
| JSON | `basics/data-formats` | helps |
| Graphs and walking them | `basics/trees-graphs` | helps |
| Regular expressions | `basics/data-formats` | helps |

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

## `engineering/third-party` — Third-party code and pinned tools

**Covers.** The job: how Strata takes in other people's code and tools, pins them, builds them its own way and ships
their notices. The problem, with the approaches in a table of cost (copies in the tree, git submodules, package
managers such as vcpkg and Conan, CMake's FetchContent, system packages) and the mistakes (code copied without its
notice; a library upgraded together with other changes). Strata's choice: 19 pinned shallow submodules in
`Strata/vendor/`, one CMake file that wraps them all, and one tool, the Slang compiler, fetched as a pinned archive;
Strata uses no package manager. The map: the vendor tree, the per-user cache, and which libraries games link and
which only tools build. The real code. The vendor wrapper's CMake ground (about 80 words): policy defaults for
third-party projects with old `cmake_minimum_required` calls (CMP0077, CMP0091 and CMP0141 set to NEW, and
`CMAKE_POLICY_VERSION_MINIMUM` 3.5, which newer CMake needs to configure them), and why the project requires CMake 3.25:
`add_subdirectory(... SYSTEM)`, which came with 3.25 and takes in every vendor library. The vendor wrapper: each library's options forced as internal cache entries,
NVRHI Vulkan-only with validation, the `nvrhi_vk` to `nvrhi` link that GNU ld's order of static libraries needs, glm's
defines kept free of layout changes because glm types cross the script ABI, spdlog with its bundled fmt, JSON without
implicit conversions; stb as one object per header so that the linker drops what games never call; the libraries only
tools build, named with a link. box3d built from its sources instead of its own CMake, with a reason for every flag
(C17 with extensions, `-ffp-contract=off` for cross-platform determinism, `/arch:AVX2` on `wide8.c` for MSVC, asserts
that follow `ST_CORE_ASSERT`, a raised limit of mesh contact triangles), and its determinism scenario compiled for the
tests. zstd split into a decoder games link and a compressor only the pack writer uses. Licenses: permissive against
copyleft and why an engine cares (games ship the notices); `ThirdPartyNotices.md` with its "shipped in games" column,
the fonts, the code derived from other projects with its license text; copyleft code is read for ideas only.
Reproducible, verified downloads: `strata_slang_fetch` walked as a state machine (the stamp's fast path with no lock
and no network, the cache folder made private to its user, a file lock against concurrent configures with its
15-minute limit, a second look after the lock, three download attempts, the SHA-256 check, extraction of only the
listed files by a child CMake, the stamp, the atomic rename, and on every failure an error message instead of a failed
configure); `STRATA_SLANG_ROOT` for machines without a network; the rule never to change the digest to match a
download. Upgrades: a submodule in a commit of its own, notices updated, every test run; box3d's golden values taken
only from box3d's own test file. How it is tested: `StrataSlang.Fetch`, which serves a fake archive over `file://`
into a private cache, and the physics golden hash. Exercises: read `ThirdPartyNotices.md` and a sample's `CREDITS.md`
and list what an exported game must credit; trace it yourself: configure a fresh build directory twice, then a third
with `STRATA_SLANG_ROOT`, and follow with a search, or `cmake --trace-source=CMake/StrataSlang.cmake`, the path each
configure takes through `strata_find_slang` and `strata_slang_fetch` (the download, the stamp's fast path, the fetch
skipped). At the end the reader can add or upgrade a dependency the way Strata
does, say which licenses a game carries, and explain why a pinned download is safe to run.

**Leaves out.**

- Warnings off for vendor code and SYSTEM includes → `engineering/flags-portability`
- The libraries only tools build, in the proof that games hold no tooling → `engineering/cmake`
- How Slang compiles the shaders and with which flags → `gpu/shaders`
- The physics golden hash and determinism of the step → `physics/world-step`
- Credits for the book's pictures and the sample assets they show → `appendix/credits`
- Linking static libraries in general → `basics/build`

**Fit.** `fits`: about 4,630 words against L (5,000). Two concepts, the long fetch algorithm walked as a state machine,
the vendor wrapper's reasons and the licenses take the most, with three excerpts, three rules and two exercises.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `build-test:305` | concept | home | Third-party dependencies: the approaches and their costs; licenses, permissive against copyleft, and why games care; the mistakes |
| `build-test:310` | concept | home | Reproducible, verified downloads: pinning by SHA-256, per-user caches, file locks for concurrent configures, atomic renames, offline overrides; the mistake of "updating the digest to match" |
| `build-test:91-99` | feature | home | The 19 submodules; the vendor wrapper; box3d from sources; the zstd split; stb one object per header; `ThirdPartyNotices.md`; the upgrade procedure; the rule for code from other projects; box3d's determinism scenario for the tests |
| `build-test:81`, `render-core:123` | feature | home | The Slang pin (2026.20, four archives with their digests, `STRATA_SLANG_ROOT`, the `slangc -v` check), as both inventories list it |
| `build-test:170` | feature | home | `StrataSlang.Fetch`: digest, cache hits, error texts, per-user folders and the host key, tested with a fake archive |
| `build-test:383` | code | home | `Strata/vendor/CMakeLists.txt:144-182`: box3d built from its sources, a reason for every flag |
| `build-test:384` | code | home | `Strata/vendor/CMakeLists.txt:184-227`: a dependency split so that shipped games get only the decoder |
| `build-test:393` | code | home | `CMake/StrataSlang.cmake:123-251`: `strata_slang_fetch`, the algorithm kept whole |
| `build-test:434` | figure | home | The Slang fetch as a state machine, every failure edge ending in an error message |
| `build-test:502` | rule | home | Never change the Slang digest to match a download: a different hash means the release was replaced; bump Slang in a commit of its own |
| `build-test:504` | rule | home | Upgrade a submodule in its own commit, update the notices, run every test; box3d's golden values only from box3d's own test |
| `build-test:506` | rule | home | Copyleft code is read for ideas only: copied copyleft code would choose Strata's license |
| `build-test:603` | hands-on | home | Read `ThirdPartyNotices.md` and a sample's `CREDITS.md`: what an exported game must credit |
| `new:28` | hands-on | home | Trace it yourself: configure a fresh build directory twice, then once with `STRATA_SLANG_ROOT`, and follow by a search or `cmake --trace-source=CMake/StrataSlang.cmake` the path of each configure: the download, the stamp's fast path with no lock and no network, the fetch skipped for `STRATA_SLANG_ROOT` (about 200 words). Evidence: `CMake/StrataSlang.cmake:128-147`, `:275-310` |
| `build-test:637-641` | term | home | Submodule (git), shallow; vendoring; permissive and copyleft license (two entries); SHA-256 pin; per-user cache |
| `new:4` | not-done | home | No package manager (vcpkg, Conan): dependencies are pinned submodules wrapped by one CMake file. Evidence: `git ls-tree -r --name-only 822a7a46 \| grep -iE "vcpkg\|conanfile"` finds nothing; `Strata/vendor/CMakeLists.txt:3-7` |
| `new:27` | feature | home | The vendor wrapper's CMake ground: policy defaults for third-party projects with old `cmake_minimum_required` calls (`CMAKE_POLICY_DEFAULT_CMP0077`, `CMP0091` and `CMP0141` set to NEW, `CMAKE_POLICY_VERSION_MINIMUM` 3.5, which newer CMake needs to configure them); the project's CMake 3.25, the version that brought `add_subdirectory(... SYSTEM)`, which takes in every vendor library (about 80 words). Evidence: `CMake/StrataConfigurations.cmake:34-38`; `CMakeLists.txt:1`; `Strata/vendor/CMakeLists.txt:32`, `:46`, `:57`, `:245` |
| `build-test:45` | feature | link | Vendor warnings off, taught on `engineering/flags-portability` |
| `build-test:71` | feature | link | The vendor libraries only tools build, taught on `engineering/cmake` |
| `foundation:628` | term | link | Atomic write, whose entry is `core/files`' |
| `build-test:642` | term | link | File lock, whose entry is `core/files`', where `FileLock` is taught |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| git: clone, commits and submodules | `basics/git` | must |
| Hashes and SHA-256 | `basics/data-formats` | must |
| File locks and atomic writes | `core/files` | must |
| CMake functions, `add_library`, `EXCLUDE_FROM_ALL`, the vendor libraries in the target graph | `engineering/cmake` | must |
| Vendor warnings off and SYSTEM includes | `engineering/flags-portability` | must |
| FMA contraction and floating-point determinism | `engineering/flags-portability` | must |
| Slang and the shader build | `gpu/shaders` | helps |
| Asset packs and their compression | `assets/packs-export` | helps |
| The order of static libraries on the link line | `basics/build` | helps |

## `engineering/generated-code` — Generated code: shaders, embedded files, version stamps and committed generators

**Covers.** The job: the code and data the build writes instead of people (compiled shaders and their registry,
embedded files, version stamps, the samples copied beside the programs) and the generators whose outputs are
committed. The problem: the approaches for shaders (compiled at run time, compiled offline and loaded from files,
compiled offline and embedded in the binary) and for other data. Strata embeds everything, so a game is one executable
and its pack, and the bytes do not depend on the configuration. The rule that keeps generated headers cheap: write a
file only when its content changed (`file(CONFIGURE)`), or everything that includes it recompiles every build. The
map: the shader pipeline from a `.slang` source and its includes through slangc (which validates what it writes) to
`<name>.raw.spv`, StrataShaderTool to `<name>.spv` and `<name>.h`, and the generated registry compiled into
`Strata_Renderer`, with the side branches that `ShaderEntries.txt` feeds (spirv-val on Linux, the Metal conversion on
macOS, the HLSL target check). The real code, in the order a build runs it: the two custom commands of every entry and
its line in the manifest; the generated `EmbeddedShaderRegistry.cpp`; StrataShaderTool, with the SPIR-V word layout
first (a five-word header; each instruction's word count in the high 16 bits and its opcode in the low 16),
`ParseSpirv`'s defensive checks, `DecoratePositionInvariant`, which collects every insertion before it inserts and
inserts from the back (why the depth prepass needs the decoration is linked), and `WriteFileAtomically`, so that a
failed build leaves no output a later build would take as current; `strata_embed_file`, a configure-time hex dump of
the default font into a function that returns a `std::span`; the version header, made at configure, and the commit
header, rewritten at build time only when the commit changes; the target that copies the samples beside the programs.
Committed generators: one table of every generator with what it writes, how it is checked and the page that explains
its output (`GenerateBlueNoise.py`, `FitFilmic.py`, `FitAOMultiBounce.py`, `GenerateAreaTable.py`,
`GenerateWhiteBalance.py`, `GenerateBrandAssets.py`, `GenerateIslandTerrain.py`, `GenerateShowcaseTerrain.py`,
`GenerateShowcaseProps.py`, `StrataTests/FeatureTest/Tools/GenerateAssets.py` and
`StrataEditor/Tools/GenerateIconHeader.py`); checks are `--check` run by hand, or the CTests
`StrataTools.ShowcaseTerrain` and `.ShowcaseProps` that compare committed outputs with regenerated ones, with `PythonMissing.cmake` standing in
when Python 3.10 or newer is absent; every tool uses only the standard library and is run with `python -I` where the
documents say so. Where the page quotes a generator's Python, the paragraph that introduces its first Python fence
says in one or two sentences what differs from C++ in it: no page of the book teaches reading Python, so the page
supplies it (R45). The page
never types the number of shader entries: it reads it from a build's `ShaderEntries.txt`. How it is tested:
`Renderer.ShaderTool` and `Renderer.ShaderModules`, named, and the Showcase checks. Exercises: add a shader variant and
find its `.raw.spv`, `.spv`, `.h` and manifest line; write a small SPIR-V inspector with `SpirvModule.h`; trace it
yourself: follow one name the renderer looks up, by a search or a debugger, from `EmbeddedShaders::Find` in
`ShaderLibrary` back to its entry in the generated `EmbeddedShaderRegistry.cpp`, the header of words it includes and the
custom command that wrote them. At the end
the reader can follow a shader from its source to the bytes the renderer looks up, patch a binary format safely, and
change a committed generator's output the right way.

**Leaves out.**

- Writing and registering a shader, slangc's flags and the dialect's checks → `gpu/shaders`
- Why the depth prepass needs invariant positions → `gpu/frame-tour`
- The Slang pin and its fetch → `engineering/third-party`
- The CI's shader steps → `engineering/ci`
- What the Filmic fit is → `image/tone-mapping`
- The morphological area table → `image/spatial-aa`
- The white-balance locus → `image/grading`
- The blue noise of the sun's shadow filter → `light/sun-shadows-2`
- The ambient-occlusion fit → `indirect/ao`
- The icon header and the editor's fonts → `editor-ui/design-system`
- Atomic writes in general → `core/files`

**Fit.** `fits`: about 4,310 words against L (5,000). Seven short excerpts in the order a build runs them, the table of
eleven committed generators, two figures, one concept and three exercises take the most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `build-test:313` | concept | home | Code generation in the build: embedding binary data, version headers that change only when their content changes, shaders compiled at build time, generated registries; the mistake of regenerating a header every build |
| `build-test:77`, `build-test:79` | feature | home | `strata_add_shaders`' two commands per entry, the manifest, the stage from the suffix, every entry depending on every include; StrataShaderTool, standard library only, built into `build/<preset>/tools` |
| `render-core:121`, `render-core:124` | feature | home | The build pipeline and StrataShaderTool as the render-core inventory lists them: taught with `build-test:77` and `build-test:79` |
| `build-test:82-85` | feature | home | `strata_embed_file`; the version header; the build commit header; the sample copy |
| `foundation:165`, `foundation:166` | feature | home | `EmbeddedFiles` (the default font) and `Version.h`, as the foundation inventory lists them |
| `build-test:172` | feature | home | The `StrataTools.*` CTests (label `tools`): the Showcase checks compare committed outputs with regenerated ones, the look-dev ones are named for `engineering/look-dev`; `PythonMissing.cmake` |
| `build-test:227-237` | feature | home | The table of committed generators: what each writes, how it is checked, the page that explains its output |
| `build-test:240` | feature | home | Every Python tool uses only the standard library and is run with `python -I` (isolated mode) where the documents say so |
| `build-test:388` | code | home | `CMake/StrataShaders.cmake:170-191`: slangc with `SLANG_RUN_SPIRV_VALIDATION=1`, then StrataShaderTool, then the registry and manifest lines; the flags above them are `gpu/shaders`' |
| `build-test:389` | code | home | `CMake/StrataShaders.cmake:198-221`: the manifest file and the generated registry source |
| `build-test:390` | code | home | `CMake/StrataShaderTool/SpirvModule.cpp:27-65`: `ParseSpirv`, a binary format read defensively (magic number, header, word counts) |
| `build-test:391` | code | home | `CMake/StrataShaderTool/SpirvModule.cpp:101-166`: `DecoratePositionInvariant`, insertions collected first and made from the back |
| `build-test:392` | code | home | `CMake/StrataShaderTool/StrataShaderTool.cpp:83-116`: `WriteFileAtomically`, a temporary file renamed into place |
| `build-test:394` | code | home | `CMake/StrataVersionCommit.cmake:1-24`: a header that changes only when the commit changes; its target is `Strata/CMakeLists.txt:31-42` |
| `build-test:395` | code | home | `CMake/StrataEmbeddedFiles.cmake:8-46`: a file embedded as a byte array with two regular expressions |
| `build-test:429` | figure | home | The shader pipeline with the side branches of `ShaderEntries.txt` (spirv-val, Metal, the HLSL target) |
| `build-test:432` | figure | home | SPIR-V's word layout: the header, word count and opcode, and the inserted `OpDecorate %v Invariant` after `OpDecorate %v BuiltIn Position` |
| `build-test:568` | hands-on | home | Add a `VARIANTS` line with a define, configure, find the new outputs and the manifest line |
| `build-test:570` | hands-on | home | A tiny SPIR-V inspector with `ParseSpirv`: list opcodes, find the decorations of an embedded module |
| `new:29` | hands-on | home | Trace it yourself, by a search or a debugger: one name the renderer looks up, from `EmbeddedShaders::Find` in `ShaderLibrary` back to its entry in the generated `EmbeddedShaderRegistry.cpp`, the header of words it includes, and the two custom commands that wrote the module and the header (about 200 words). Evidence: `Strata/src/Strata/Renderer/ShaderLibrary.cpp:12`, `:60`; `CMake/StrataShaders.cmake:172-191`, `:202-221` |
| `build-test:650`, `build-test:698` | term | home | Embedded shader registry; committed generator |
| `build-test:760` | open | home | The number of shader entries is read from a build's `ShaderEntries.txt` and never typed (the inventories count about 113 and 114) |
| `build-test:769` | open | home | Which generators have a CTest: only the two Showcase ones; `GenerateBlueNoise.py --check` and `FitFilmic.py --check` run by hand |
| `render-core:502` | figure | link | The shader build as a writer of shaders sees it, `gpu/shaders`' figure |
| `render-image:278`, `render-image:280`, `render-image:281`, `render-image:282` | feature | link | The outputs of the Filmic, white-balance, area-table and blue-noise generators, each explained on its page |
| `editor-ui:66` | feature | link | `Icons.h`, explained on `editor-ui/design-system` |
| `build-test:78` | feature | link | slangc's flags, taught on `gpu/shaders` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Writing and registering a shader; slangc and its flags | `gpu/shaders` | must |
| CMake targets, custom commands, `file(CONFIGURE)` and script mode | `engineering/cmake` | must |
| Binary and hexadecimal numbers, bit fields and 32-bit words | `basics/numbers` | must |
| Bytes and binary file formats | `basics/bytes` | must |
| `std::span`, `std::optional` and `std::vector` | `basics/cpp-modern` | must |
| The depth prepass, its `EQUAL` test and invariant positions | `gpu/frame-tour` | must |
| Atomic writes | `core/files` | must |
| Regular expressions | `basics/data-formats` | helps |

## `engineering/testing` — Testing an engine

**Covers.** The problem as a reader meets it: a test that passed on its author's machine fails on CI's macOS runner,
which has three hardware threads, and passes when it runs again; and a bug fixed last month is back. The naive answer:
run the program and look, or add a check once. Where it breaks: nobody looks at every change, and a test that waits a
fixed number of frames or reads the user's files is a coin toss. The idea: a test is a program that checks one claim
and fails loudly, and a suite is worth as much as it is repeatable. The approaches, each introduced by the flaw of the
one before, with a table of cost, speed, what each catches and who uses them: unit, integration, end-to-end and smoke
tests; snapshot (golden-file) tests, with the component schema snapshot as Strata's example (a committed JSON of every
component's name, metadata and properties in order, which `Reflection.ComponentSchema` compares with the live
registry, about 80 words); golden images against before-and-after image comparisons; corruption sweeps and fuzzing;
performance gates.
Test frameworks: doctest's `TEST_SUITE`, `TEST_CASE`, `CHECK` against `REQUIRE`, `INFO` and `CAPTURE`, filters, and a
runner such as CTest above the test binary, extending the one case of `core/first-change`; doctest's
`expected_failures` as the way to test code whose job is to fail a test, with the perf harness's cases that must fail,
such as a confirmed check over its budget in every attempt (about 60 words). Determinism and flakiness:
wait on a condition or the clock, never on frames; private temporary folders, free ports and private sessions; no
shared process state; fixed seeds; the slowest machine as the yardstick; why a flaky test is worse than none.
Regression tests: a test that has never failed proves nothing, so a new regression test is checked to fail without its
fix. Strata's choice: everything ships with tests, and no test is disabled, skipped or weakened to pass (golden rule
2); coverage by construction instead of line coverage, in one paragraph with a link, and Strata measures no line
coverage; sweeps as an idea, in one paragraph with a link. The page's example: one timer test written three ways
(sleep then check, count frames, wait for the condition with a clock limit) and run on a loaded machine. Common
mistakes: a sleep followed by an assert, a test that cannot fail, a test that depends on a program outside the build.
Exercises: break the reader's `ToUpper` of `core/first-change`, see its test case fail and restore it; rewrite a
test that counts frames to wait with `Tests::WaitUntil` and a clock limit, and run it beside a loaded machine's other
work; for three changes (a parser, a shader fix, an editor command) name the kind of test each needs and why.
At the end the reader can say which kind of test a change needs, write a test that cannot flake, and check that a
regression test fails without its fix.

**Leaves out.**

- StrataTests' main, helpers, shards, labels, fixtures and locks → `engineering/test-program`
- Corruption sweeps and fuzzing in Strata → `engineering/test-program`
- GPU, end-to-end and package tests → `engineering/test-kinds`
- The feature test → `engineering/feature-test`
- Performance tests and their budgets → `engineering/perf-lab`
- Image comparisons with the look-dev harness → `engineering/look-dev`
- Play-tests of a game through command scripts → `make/automated-playtests`

**Fit.** `fits`: about 3,230 words against M (3,000). Two concepts from zero, the approaches table with its snapshot
row, the frameworks in short (the reader wrote one case already), two rules, the timer example and three exercises take
the most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `build-test:327` | concept | home | What a test is; unit, integration and end-to-end; test frameworks (doctest's suites, cases, `CHECK` and `REQUIRE`, filters, and `expected_failures` for code whose job is to fail a test, with the perf harness's cases that must fail); every change ships with tests; the mistake of weakening a test to get green |
| `new:30` | concept | home | Snapshot (golden-file) tests, a row of the approaches table: a committed file of the expected output compared with what the code makes now, and rewritten on purpose; Strata's example is `StrataTests/Architecture/ComponentSchema.json`, every component's name, metadata and properties in order, which `Reflection.ComponentSchema` compares with the live registry and the helper mode `write-component-schema` writes again (about 80 words). Evidence: `StrataTests/src/Reflection/ComponentSchemaTests.cpp:14-50`; `StrataTests/src/TestMain.cpp:240-246`; `.claude/skills/strata-add-component/SKILL.md:57` |
| `build-test:335` | concept | home | Determinism and flakiness: conditions or the clock, never frames; private folders, ports and sessions; no environment changes for children; the slowest CI machine as the yardstick; the mistake of a sleep then an assert |
| `build-test:514` | rule | home | Wait by the clock or a condition, never by frames; size job pools explicitly: CI's macOS runners have three hardware threads |
| `build-test:520` | rule | home | Check that a new regression test fails without its fix |
| `build-test:657` | term | home | doctest, with `TEST_SUITE`, `TEST_CASE`, `CHECK`, `REQUIRE`, `INFO` and `CAPTURE` |
| `build-test:683`, `build-test:684` | term | home | End-to-end test; smoke test |
| `new:31` | hands-on | home | The page's exercises (about 250 words): break the reader's `ToUpper` of `core/first-change`, see its case in `Core.StringUtils` fail and restore it; rewrite a test that counts frames to wait with `Tests::WaitUntil` and a clock limit; name the kind of test three changes need (a parser, a shader fix, an editor command). Evidence: `Strata/src/Strata/Core/StringUtils.h:13`; `StrataTests/src/Core/StringUtilsTests.cpp:9`; `StrataTests/src/TestHelpers.h:62-63` |
| `new:5` | not-done | home | No measurement of line coverage: the feature test's coverage by construction stands in its place. Evidence: `git grep -niE "\-\-coverage\|llvm-cov\|gcov\|OpenCppCoverage\|fprofile-instr" 822a7a46 -- CMakeLists.txt CMake StrataTests/CMakeLists.txt .github Tools` finds nothing |
| `build-test:246` | feature | link | Golden rule 2, whose home is `engineering/contributing` |
| `build-test:345` | concept | link | Sweeps as an idea, taught on `engineering/test-program` |
| `build-test:356` | concept | link | Coverage by construction, taught on `engineering/feature-test` |
| `build-test:127` | feature | link | `Tests::WaitUntil` and the other helpers that keep tests repeatable |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| One test case in a suite, `CHECK`, running a suite with doctest's filter | `core/first-change` | must |
| Threads and races | `basics/threads` | helps |
| Random numbers and seeds | `basics/math-probability` | helps |
| Processes and their environment | `basics/computer` | helps |
| The job system and its threads | `core/jobs` | helps |
| Frames, fixed steps and the clock | `core/time` | helps |

## `engineering/test-program` — Inside StrataTests

**Covers.** The job: one test binary, `StrataTests`, holds the module tests, runs as its own helper processes, and
CTest runs its suites side by side in shards; the GPU, end-to-end and package tests are `engineering/test-kinds`'.
The problem, in the part's full section on it: test organisation at scale (one big binary against many, running in
parallel, splitting by suite name and keeping a shard under a minute, labels for what a machine can do and for cost,
fixtures, locks), how CTest describes a test (a command with properties), and the mistake of a suite that silently
runs nowhere. The map: the shard figure (every suite of the binary in one column, arrows to the eight own CTests and
the 13 shards, the check that each suite runs exactly once, the `.Sweep` suites also to `StrataTests.Fuzz`). The
contract: every test case belongs to a `TEST_SUITE` and every suite prefix to a shard or an own CTest; tests write only
into `CreateTemporaryDirectory()`, never open a sample in place, never set the process's environment for a child.
The toy: a test runner's `main` with one helper mode, in 40 lines. The real code. What the binary compiles: the
module tests without the files of a module a build leaves out (`STRATA_TESTS_OF_*`), the test script modules built
with `strata_add_script_module`, the definitions the tests read (`STRATA_SOURCE_DIR`, `ST_TESTS_HAVE_EVERY_MODULE`,
`ST_TESTS_HAVE_EDITOR`, `DOCTEST_CONFIG_NO_POSIX_SIGNALS`). `main`: console streams, the log at Warn, the helper modes
and the composition root as every program runs it, the fake CMake and the fake editor, execution-speed throttling off,
private `STRATA_RUNTIME_DIR`, `STRATA_RECENT_PROJECTS` and `STRATA_SCRIPT_BUILDS_DIR`, the shared GPU shut down last.
The test binary as its own helper process: `--strata-test-helper=<mode>` with about 50 modes, among them
`run-with-environment` and `write-component-schema`, which writes the component schema snapshot again, and why a unit
test never depends on `cat`, Python or a real CMake. Crash containment against
the framework: doctest's signal handlers would replace `CrashGuard`'s and leave script crashes uncontained, so they
are off, and `TestCrashReporter.cpp` names the crashing case itself, with `STRATA_TEST_TRACE=1` printing each case
as it starts. Shards: `CoreShards.json` turned into `StrataTests.Core.<Shard>` CTests (label `core`); `Testing.Shards`,
which asks the binary for its suites in a child process, matches doctest's filters with backtracking and fails on a
suite in no shard or two, and on a case outside any suite; what the shards bought, in one sentence: after wave 4 a
Debug ctest on the Mac took 94 to 163 s with `-j 8` instead of 500 to 804 s serially. Labels (`core`, `fuzz`, `gpu`,
`perf`, `package`, `feature`, `tools`), fixtures, `RESOURCE_LOCK toolchain`, with its reason (concurrent builds
through one toolchain fail at random, with MSBuild's and mspdbsrv's C1090 and LNK errors) and the trap beside it (the
`Package*` suites build in the system temporary folder, where MSBuild does not track files, MSB8029, and may relink an
unchanged module), and `RUN_SERIAL`. Corruption sweeps, the book's home of
sweeps and fuzzing: exhaustive against sampled offsets, fixed seeds so a failure repeats, `SelectSweepOffsets`
(headers, the bytes near every block edge, and 512 offsets from a fixed seed), the whole sweep in `StrataTests.Fuzz`
with `STRATA_TEST_SWEEP=full` in Release and Dist, the pack sweep as the example; Strata has no coverage-guided
fuzzer. The helper catalogue: `WaitUntil`, `LogCapture`, `ScopedEnvironmentVariable`, `CopySampleProject`,
`CheckSceneCaches`, `RunCommandToCompletion`, and `ImGuiHarness` named with its page. The page states the 13 shards,
`SceneTiming` among them, where the Developer Guide and the build-test skill name 12; it never types the number of
CTests, which `ctest -N` prints. What went wrong before: a crash in static initialization leaves the Linux loader's
lock held, so such tests live in the `LoaderFaults` shard. Exercises: a suite with a new prefix and the failure of
`Testing.Shards`; a corruption sweep for a small parser, sampled and full; a helper-mode process test; trace it
yourself: follow `--strata-test-helper=run-with-environment` by a search from `main` to `RunHelperMode` and the mode's
code, and say what the child's environment holds. At the end the
reader can add a suite where CTest will run it, write a test that starts a child process without outside programs,
and write a sweep whose failures repeat.

**Leaves out.**

- What tests are for, the kinds of tests and flakiness → `engineering/testing`
- The GPU suites, the end-to-end suites and the package tests → `engineering/test-kinds`
- The feature test → `engineering/feature-test`
- The perf suites and their budgets → `engineering/perf-lab`
- Debugging a test that crashes → `core/debugging`
- `CrashGuard` itself → `scripting/crash-containment`
- Testing the editor's UI with `ImGuiHarness` → `editor-ui/ui-testing`
- Validating untrusted bytes in loaders → `assets/robustness`

**Fit.** `fits`: about 6,460 words against L (5,000). Four concepts, five excerpts, three figures, five rules, three
exercises and the trace take the most. The count puts the page 40 words below L's top, so it has no room for more.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `build-test:330` | concept | home | Test organisation at scale: runners, CTest, labels, sharding, fixtures and locks; the mistake of a suite prefix that matches no shard |
| `build-test:339` | concept | home | The test binary as its own helper process: spawning, crashes, consoles and exit codes tested without outside programs |
| `build-test:342` | concept | home | Crash containment against the test framework: signal handlers are process-wide, so doctest's are off and the reporter names the case |
| `build-test:345` | concept | home | Fuzzing and corruption sweeps: exhaustive and sampled offsets, fixed seeds, full sweeps in optimized runs; the mistake of seeds that change per run |
| `build-test:105-118` | feature | home | The binary and what it links; its definitions; the module-dependent test files; the test script modules; `main`; the helper modes, `write-component-schema` among them; the fake CMake; crash naming; the shards, and the Debug ctest they bought (94 to 163 s with `-j 8` against 500 to 804 s serially, on the Mac after wave 4); `Testing.Shards`; sweeps and the fuzz run; the resource lock with its reason (C1090 and LNK errors from concurrent builds through one toolchain) and the trap of the `Package*` suites in the system temporary folder (MSB8029, relinked modules); fixtures; labels |
| `build-test:127-129` | feature | home | The helper catalogue: the general helpers, the editor's (`RunCommandToCompletion`, `ImGuiHarness`), `CheckSceneCaches` |
| `build-test:396` | code | home | `StrataTests/CMakeLists.txt:209-255`: the shards read from `StrataTests/CoreShards.json` (shown beside it, lines 1-36) and turned into CTests, the own CTests' suites always excluded |
| `build-test:397` | code | home | `StrataTests/src/Testing/ShardTests.cpp:118-153`: `CheckShards`, "exactly once"; with `MatchesFilter` at lines 26-58 and the test case at 244-277 that asks the binary for its suites |
| `build-test:398` | code | home | `StrataTests/src/TestHelpers.cpp:700-737`: `SelectSweepOffsets`, all offsets in a full sweep, else the ranges, the block edges and seeded offsets; used by `StrataTests/src/Asset/AssetPackTests.cpp:984-1031` |
| `build-test:399` | code | home | `StrataTests/src/TestMain.cpp:1309-1370`: a test runner's `main`: the user's environment kept out, modules registered, helper modes |
| `build-test:400` | code | home | `StrataTests/src/TestCrashReporter.cpp:19-87`: a doctest listener that remembers the running case, and why doctest's signal handling is off |
| `build-test:436` | figure | home | The shards: every suite to exactly one own CTest or shard, the `Testing.Shards` check, the sweeps also to `StrataTests.Fuzz` |
| `build-test:462` | figure | home | Text captures of `ctest --preset windows-debug -N -L core` listing the shards, and the summary of a `ctest -j 8` run |
| `build-test:463` | figure | home | A text capture of `Testing.Shards` failing on a suite in no shard |
| `build-test:508` | rule | home | Every test case in a `TEST_SUITE`, every new suite prefix in a shard; shards under about a minute in Debug |
| `build-test:510` | rule | home | Tests that crash the dynamic loader go in `LoaderFaults` |
| `build-test:516` | rule | home | Never set the test process's environment for a child; use `run-with-environment` |
| `build-test:518` | rule | home | Tests write only into `CreateTemporaryDirectory()` and never open samples in place |
| `build-test:521` | rule | home | doctest's POSIX signal handling is off, because it would take `CrashGuard`'s handlers away |
| `build-test:572` | hands-on | home | Add a suite with a new prefix, watch `Testing.Shards` fail, add it to `CoreShards.json` |
| `build-test:574` | hands-on | home | A corruption sweep for a small parser with `SelectSweepOffsets` in a `.Sweep` suite, sampled in Debug and full with `STRATA_TEST_SWEEP=full` |
| `build-test:582` | hands-on | home | A new `--strata-test-helper=` mode and a test that runs it with `Process::Run` and checks its output and exit code |
| `new:32` | hands-on | home | Trace it yourself, by a search: `--strata-test-helper=run-with-environment` from `main` to `RunHelperMode` and the mode's code; what the child's environment holds and why the test process's own stays untouched (about 150 words). Evidence: `StrataTests/src/TestMain.cpp:238`, `:289-320`, `:1340` |
| `build-test:658-667` | term | home | CTest; label; shard; fixture; resource lock; `RUN_SERIAL`; helper mode; fake CMake and fake editor (two entries); sweep and `.Sweep` suite; fuzz run |
| `build-test:756` | open | home | The page states the shards of `CoreShards.json`, as `new:6` corrects the guide and the skill |
| `build-test:762` | open | home | The number of CTests depends on the configuration and the programs built; the page shows `ctest -N` instead of a count |
| `new:6` | erratum | home | `Docs/DeveloperGuide.md:402-405` and `.claude/skills/strata-build-test/SKILL.md:73-74` name 12 shards; `CoreShards.json` has 13: they omit `SceneTiming`, which runs `Scene.Timing*`. The page names the 13. Evidence: `StrataTests/CoreShards.json:14-35` |
| `new:7` | not-done | home | No coverage-guided fuzzer (libFuzzer, AFL): the sweeps test fixed, seeded offsets. Evidence: `git grep -niE "libfuzzer\|LLVMFuzzerTestOneInput\|fsanitize=fuzzer" 822a7a46 -- Strata/src StrataTests CMake CMakeLists.txt .github` finds nothing |
| `editor-ui:256` | feature | link | `ImGuiHarness`, taught on `editor-ui/ui-testing` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Kinds of tests, doctest, flakiness and its rules | `engineering/testing` | must |
| CMake targets, functions and generator expressions | `engineering/cmake` | must |
| Processes, exit codes, the standard streams and environment variables | `basics/tools` | must |
| Signals, exit codes and console programs | `core/platform` | must |
| JSON | `basics/data-formats` | must |
| The composition root and `ModuleRegistrationOptions` | `core/layers-registries` | must |
| Crash containment with `CrashGuard` | `scripting/crash-containment` | helps |
| Script modules and the dynamic loader | `scripting/loading` | helps |
| Random generators and fixed seeds | `basics/math-probability` | helps |
| Validating untrusted input | `assets/robustness` | helps |

## `engineering/test-kinds` — GPU, end-to-end and package tests

**Covers.** The job: the tests that need more than the test binary's own process: a GPU, the built programs, a
toolchain, an installation. The problem: GPU testing, with what `gpu/first-triangle` teaches linked (headless devices,
the one shared device and its reason, validation errors as failures, the error count, readback) and what this page
adds (exact pixels against tolerances; counts that arrive frames later; the perf suites with validation off; the
helpers), and end-to-end testing of programs (private sessions,
free ports, `--no-gpu`, killing what a failed test started). The map: the CTest fixture chains (the export chain, the
feature-test chain, the sample exports with their windowed checks and the samples' GPU perf test, the clean of the
perf results). The contract: GPU suites share one device and end with no new validation errors; end-to-end suites own
what they start. The toy: a test that starts a program, waits for its output by the clock and checks its exit code. The
GPU suites, from the test program's side: the shared device made on first use and the error count taken when a
context starts, `STRATA_TEST_GPU_VALIDATION=0`, which the GPU perf tests set so that they measure without validation,
and the command-buffer recycling of `ExecuteAndWait`; writing a GPU test is `gpu/first-triangle`'s. The helpers:
`GetDrawnCounts`, `ReadBufferRange`, `ReadMeshGeometry`, `MeasureNoise`; `ExactSpecification` and
`AddNeutralPostProcess` are named with a link to `image/tutorial-post-effect`. The flicker metrics of `FlickerMetrics.h`,
the book's home of measuring flicker in tests: each pixel of the newest frame reprojected by depth into the two before,
the second difference measured only where all three saw the same surface, with per-pixel and 32-pixel-block
statistics. A table of the GPU suites by area, with the light area's as the example (`GPU.SceneRenderer.Lighting`,
`.Shadows`, `.ShadowFilter` and the CPU suites beside them). End-to-end: the `EndToEnd` suites (`StandardStreams`,
`EditorAutomation`, `Recovery`) that run the built editor, CLI and runtime; the runners `ExpectFailure.cmake` and
`RunAndExpect.cmake`; command scripts as test data (the smoke script itself is quoted on `editor/command-scripts` and
linked), and the editor's smoke test followed from its CTest to
`SmokeViewport.png`; the scripts that must fail, wait or quit; the export chain and the runtime's option tests.
Sample regressions: `SampleProject.cmake` copies a sample, runs its `<Sample>Commands.json.in`, exports the game full
and pruned, runs both headless and fails on any warning nobody listed. Package and install tests:
`StrataScriptCore.Package` and `.PackageDist` build a project against the installed-style SDK; `StrataTests.Package`;
`StrataEditor.Scripts` makes, builds, plays and exports a scripted game with the real editor; `StrataEditor.Install`
installs into a fresh prefix, checks the exact top-level layout and makes a game with the installed editor alone. How
it is tested: `GPU.TestUtils`. Exercises: a GPU readback test with `ReadBufferRange`; a new `expect` in a sample's
command script, run through its CTest; trace it yourself: follow the export chain by a search for its fixtures, from
`StrataExport.Clean` through `StrataEditor.Export` to every CTest that requires the exported game, and check the
order with `ctest -N`. At the end the reader can choose the kind of suite a change needs, write a GPU
check that respects the shared device, and extend an end-to-end or sample test.

**Leaves out.**

- Writing a GPU test: `GPUContext`, the shared device and its reason, validation, the error count and pixel readback → `gpu/first-triangle`
- `ExactSpecification` and `AddNeutralPostProcess` → `image/tutorial-post-effect`
- The validation layer and frame captures → `gpu/debugging`
- The command-script format: `expect`, `bind` and `until`, and the smoke script quoted whole → `editor/command-scripts`
- Image comparisons between builds → `engineering/look-dev`
- The feature test's runners → `engineering/feature-test`
- The perf suites → `engineering/perf-lab`
- The install rules the install test checks → `engineering/releasing`
- Play-tests a game maker writes for a game → `make/automated-playtests`

**Fit.** `fits`: about 4,715 words against L (5,000). The two problems (the GPU testing this page adds, end-to-end
testing), four excerpts, two figures, the table of GPU suites by area and the package and install tests take the most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `build-test:348` | concept | home | GPU testing, the part `gpu/first-triangle` does not teach: exact pixels against tolerances, counts that arrive frames later (`GetDrawnCounts`), the perf suites with validation off, the helper catalogue; the shared device and its reason, validation, the error count and readback are linked to `gpu/first-triangle` |
| `build-test:119-124` | feature | home | The expect-failure and run-and-expect runners; command scripts as test data; the editor's smoke and script checks; the export chain and the runtime's option tests; the `EndToEnd` suites |
| `build-test:126` | feature | home | The GPU test helpers `GetDrawnCounts`, `ReadBufferRange`, `ReadMeshGeometry` and `MeasureNoise`; `ExactSpecification` and `AddNeutralPostProcess` are named with a link to `image/tutorial-post-effect`, their home |
| `build-test:164-168` | feature | home | The script-SDK package tests; `StrataTests.Package`; `StrataEditor.Scripts`; the sample tests; the install test |
| `gamedev:229` | feature | home | Sample regressions: one command script per sample, run by `SampleProject.cmake` |
| `render-indirect:197` | feature | home | The flicker meter, as the indirect area uses it in a strafe |
| `render-direct:228` | feature | home | The light area's CPU and GPU suites, as rows of the page's table of renderer suites; each light page's "How it is tested" names its own |
| `build-test:401` | code | home | `StrataTests/src/Renderer/GPUTestUtils.cpp:29-50`: `GPUContext`'s constructor, cut to what `gpu/first-triangle` does not show: the device made on first use, validation off for the perf suites, the error count's starting value |
| `build-test:411` | code | link | An end-to-end test as data: the smoke script, `StrataTests/Editor/SmokeCommands.json.in`, quoted on `editor/command-scripts` |
| `new:8` | code | home | `StrataTests/src/Renderer/FlickerMetrics.h:11-50`: the flicker meter's contract, the frame it reads and the statistics it reports |
| `new:9` | code | home | `StrataTests/Editor/SampleProject.cmake:1-20`: the sample runner's steps and options, as its header states them |
| `new:10` | code | home | `StrataTests/Editor/InstallEndToEnd.cmake:43-60`: `cmake --install` into a fresh prefix and the exact top-level layout |
| `build-test:438` | figure | home | The CTest fixture chains as graphs |
| `build-test:472` | figure | home | `SmokeViewport.png`, the smoke test's capture of floor, crate and lights, as an end-to-end artifact |
| `build-test:576` | hands-on | home | A GPU readback test: write a buffer, read it with `ReadBufferRange`, end with the error-count check, under validation |
| `gamedev:562` | hands-on | home | Extend a sample's command script with a new `expect` for a feature you added; run its CTest |
| `new:33` | hands-on | home | Trace it yourself, by a search for the fixtures' names: the export chain from `StrataExport.Clean` through `StrataEditor.Export`, which sets up `StrataExportedGame`, to every CTest that requires it (`StrataRuntime.PerfLog`, `.Render`, `.Resolution`, `.PerfLogWindowed`), then the order checked with `ctest -N` (about 150 words). Evidence: `StrataTests/CMakeLists.txt:591`, `:598`, `:673`, `:718`, `:726`, `:760` |
| `render-indirect:649` | term | home | Flicker meter |
| `build-test:125` | feature | use | `GPUContext` from the test program's side; `gpu/first-triangle` teaches it |
| `render-core:607` | rule | use | GPU tests share one device and end with zero new errors, as the suites keep it |
| `build-test:117` | feature | use | CTest fixtures, the mechanism of the chains |
| `render-image:273` | feature | link | `ExactSpecification` and `AddNeutralPostProcess`, taught on `image/tutorial-post-effect` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The test program: shards, labels, fixtures and helper modes | `engineering/test-program` | must |
| Writing a GPU test: `GPUContext`, the shared device and its reason, validation, the error count, pixel readback | `gpu/first-triangle` | must |
| `ExactSpecification` and `AddNeutralPostProcess` | `image/tutorial-post-effect` | helps |
| Command scripts: `expect`, `bind` and `$ref`, `until` | `editor/command-scripts` | must |
| Headless runs and `--no-gpu` | `core/first-frame` | helps |
| An exported game and its folder | `worlds/export` | helps |
| Script modules and the SDK they build against | `scripting/shared-libraries` | helps |
| Reprojection by depth and motion | `draw/motion-vectors` | helps |
| Luminance | `basics/color` | helps |
| TAA and its jitter | `image/taa` | helps |

## `engineering/feature-test` — The feature test

**Covers.** The job: one project that must exercise everything the engine registers, and the runners that play it;
it exists for golden rule 6, keep the feature test current. The problem: coverage by construction against line
coverage. Line coverage says which lines ran, not which features were checked; the registries make "every"
enumerable, so a check can demand each registered thing. The map: the coverage loop (the registries of components,
settings sections, host functions, SDK names, field types and asset types; the feature project that must exercise each;
the runners: headless in the test process, the in-process editor, the exported game, the real executables, the GPU).
The contract, what counts: every registered component on some entity, with every property non-default on some entity
and every reference resolving; every settings section non-default in `FeatureTest.stproj`; every script field type
overridden; every callback called (the journal); every host function called (the call counters); every public class,
function and macro of the SDK used, as `SDKReader` reads the headers; an asset of every type that imports without
warnings and leaves its `.meta` untouched; no warning or error the run does not expect. The toy: a coverage check over
a registry of two entries. The real code: the component check walking `ComponentRegistry` against a default-made
instance; the headless play (audio without a device, a window service without a window, saves in a folder of the test,
interpolation on, every host function's call count checked after the scenario); the SDK coverage check; the script
side, `FeatureScript` with `Expect`, `Checks`, `Failure` and `Completed`, and `Journal()`. The runners:
`StrataTests.FeatureTest` (headless, then in the in-process editor and as an exported game in `GameRuntime`, 200 frames
with a hot reload halfway and the scene's caches checked every frame), `GPU.FeatureTest`, `StrataEditor.FeatureTest`
and `StrataRuntime.FeatureTest` on a copy, `StrataRuntime.FeatureTestQuality`, `StrataEditor.InputSequence`. Extending
it: what to add for a component, a property, a settings section, a host function, a callback, a field type and an
asset type, and the tiny binary assets from `StrataTests/FeatureTest/Tools/GenerateAssets.py`, whose outputs are
committed (the Developer Guide writes `Tools/GenerateAssets.py`). The rule, in one box with the scripting side (every
new host function, SDK name, callback and field type is exercised by the feature test): a feature without its entry
cannot land. Exercises: add a component and watch the feature test fail until the feature scene holds it with
non-default values; trace it yourself: follow `Time::SetTimeScale` by a search from the SDK through its host table
entry to the feature script that calls it and the check that fails when no script does. At
the end the reader can say what the feature test demands of a new feature and extend the project so that it passes.

**Leaves out.**

- Reflection and the component registry → `world/reflection`
- The host API and its call counters → `scripting/host-api`
- The feature test's minimum for a new component → `world/tutorial-component`
- A new host function's feature script → `scripting/tutorial-host-function`
- The engine's test modules built to fail at load → `scripting/loading`
- Regression tests of a game from command scripts → `make/automated-playtests`
- The feature test in a whole change → `capstone/land`
- The test program's shards and CTests → `engineering/test-program`
- The committed generators as a workflow → `engineering/generated-code`

**Fit.** `fits`: about 3,860 words against M (3,000). One concept, four excerpts, the contract's eight checks, the
runners and the guide to extending it take the most; the page is 140 words below M's top.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `build-test:356`, `scripting:345` | concept | home | Coverage by construction, one entry with testing the script API: a project that must hold every registered thing with non-default values; the feature test's coverage of host functions, SDK names and callbacks, and the call counters; the mistake of adding a component or host function without extending it. The test modules built to fail are `scripting/loading`'s, and regression tests of a game from command scripts `make/automated-playtests`' |
| `build-test:155-158` | feature | home | The feature project; the coverage checks; the runners; the script side |
| `assets:218` | feature | home | The check that fails when a registered asset type has no asset in the project |
| `build-test:407` | code | home | `StrataTests/src/FeatureTest/FeatureTests.cpp:152-196`: coverage by walking the component registry against a default-made instance |
| `new:11` | code | home | `StrataTests/src/FeatureTest/FeatureTests.cpp:229-281`: the headless play and the check that every host function was called |
| `new:12` | code | home | `StrataTests/src/FeatureTest/SDKCoverageTests.cpp:381-404`: every class, function and macro of the SDK used by the feature scripts |
| `new:13` | code | home | `StrataTests/FeatureTest/Scripts/FeatureScript.h:77-90`: the script side's check channel |
| `build-test:451` | figure | home | The coverage loop: registries, the project, the runners |
| `build-test:532`, `scripting:496` | rule | home | One rule box: keep the feature test current; every new host function, SDK name, callback and field type is exercised by it; it fails on what goes unexercised, so a feature without its entry cannot land |
| `build-test:584` | hands-on | home | Add a component; watch the feature test fail on the missing entity and property; extend `Feature.stscene` |
| `new:34` | hands-on | home | Trace it yourself, by a search: `Time::SetTimeScale` from the SDK's header through its entry of the host table to the feature script that calls it, and the check after the headless play that names a host function no script called (about 150 words). Evidence: `StrataScriptCore/Include/StrataScript/Time.h:49-52`; `StrataScriptCore/Include/StrataScript/ScriptABI.h:328`; `StrataTests/FeatureTest/Scripts/TimeFeatures.cpp:40`, `:42`; `StrataTests/src/FeatureTest/FeatureTests.cpp:270-275` |
| `build-test:680`, `scripting:583` | term | home | Feature test, one entry |
| `build-test:681` | term | home | Journal (feature test), one of the qualified entries of "journal" |
| `build-test:758` | open | home | The generator's path, which `new:14` corrects |
| `scripting:691` | open | home | The runner and the SDK reader (`FeatureTestUtils.cpp`, `SDKReader.cpp`), which this page reads for its runner and SDK sections |
| `new:14` | erratum | home | `Docs/DeveloperGuide.md:828` names `Tools/GenerateAssets.py`; the file is `StrataTests/FeatureTest/Tools/GenerateAssets.py`, and `Tools/` holds no such file. The page writes the full path. Evidence: `StrataTests/FeatureTest/Tools/GenerateAssets.py`; `git ls-tree --name-only 822a7a46 Tools/` lists no `GenerateAssets.py` |
| `build-test:236` | feature | link | The generator of the project's tiny assets, in `engineering/generated-code`'s table |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The component registry and its properties | `world/reflection` | must |
| The script ABI, the host table and the SDK | `scripting/abi-sdk` | must |
| The end-to-end suites and CTest's fixture chains | `engineering/test-kinds` | must |
| Settings sections | `world/projects-settings` | helps |
| The host API's call counters | `scripting/host-api` | helps |
| Hot reload | `scripting/hot-reload` | helps |
| Asset types and `.meta` files | `assets/handles-meta` | helps |

## `engineering/perf-lab` — Measuring performance honestly: noise, percentiles, budgets and the perf lab

**Covers.** The job: Strata's performance tests, the tools around them, and the method that makes their numbers
honest; the home of the design decision "trade-offs are measured on the reference machine, and the numbers are shown",
stated in a `:::why`. The problem, in the part's full section on it: benchmarks against gates; warm-up; median, mean and
percentiles; noise only adds, because the machine's other work never makes code faster, so one attempt within the
budget decides; confirmation by measuring again; reference machines; budgets with headroom; ratchets; provisional
metrics; canaries; interleaved A/B runs; layout effects (48 bytes of moved code shifted CPU medians by about 7%);
hybrid CPUs with performance and efficiency cores; the mistakes (raising a budget to pass, trusting one run, measuring
on a busy machine, numbers from a Debug build). The map: the perf suites as CTests (`StrataTests.Perf` for `Perf.*`,
`StrataTests.PerfGPU` for `PerfGPU.*` with validation off, `StrataTests.PerfGPU.Samples` after the sample exports),
in Release and Dist only, `RUN_SERIAL`, after the clean of the results file. The contract: limits live only in
`Budgets.json`; budgets only go down; a budget is at most 1.5 times the measurement; a commit that adds or lowers one
states the measured values; a budget goes up only for a change of machine shown by an interleaved A/B against the
commit that set it, or once for a cost the owner accepted by name; perf tests measure the Medium preset unless the
metric names another; measure with the Visual Studio preset the budgets were set with (`ctest --preset
windows-release -L perf`), never `windows-ninja`, whose MSVC builds get no `/arch:AVX2` and so compile other engine
code (about 60 words). The toy: measure, summarize and check against a budget in 40 lines. The real code: `Measure`
and `Summarize` (warm-up, the median, the nearest-rank p95 in integers so that no rounding moves it); the budget file,
whose comment is its specification (the reference machine, the units, `Target`, `Provisional`); `CheckConfirmed`
(every metric known before anything is measured, decided once within the budget, up to three attempts, every attempt
recorded); the results file, which holds nothing of one run so that two can be compared; the canary
`Perf.Harness.Sort200k`, the median of 31 sorts of fixed numbers, whose slowness says the machine is slow;
`Tools/PerfStability.py`, which turns repeated runs into budget proposals under the ratchet (`classify`) and compares
against a baseline; `Tools/PerfLock.py`, one measurement at a time on a machine, with its exit codes; the scene
generators and world fixtures; peak memory measured in a fresh helper process; GPU timing through `MeasureFrames` and
`MeasureGPU`. The paragraph that introduces the page's first Python fence (`classify`) says in one or two sentences
what differs from C++ in it: no page of the book teaches reading Python, so the page supplies it (R45). Every suite and every budget, with the machine, are `reference/performance`'s table. How it is tested:
the `PerfLab` suite in the Core shard, in every configuration, and `Perf.Harness`. Exercises: add a provisional metric,
measure it inside a confirmed check, run `ctest --preset <preset>-release -L perf`, read `PerfResults`, then read what
`PerfStability.py --runs 3 --propose-budgets` would write; trace it yourself: follow one `[perf]` line of the run by a
search back to the `printf` that wrote it, the confirmed check that measured it and the entry of `Budgets.json` that
decided it. At the end the reader can add a perf metric with an honest
budget, tell a regression from a noisy machine, and explain every number a perf run prints.

**Leaves out.**

- Measuring a frame: percentiles, self time, Tracy, "CPU, GPU or capped" → `core/profiling`
- GPU timestamps and stages → `gpu/readback-timing`
- Every perf suite and every budget, and the machine they were measured on → `reference/performance`
- Tuning physics and its sweep → `physics/tuning`
- A perf budget for a new feature → `capstone/land`
- Measuring a shipped game with `--perf-log` → `make/performance`

**Fit.** `fits`: about 5,380 words against L (5,000). One large concept (about 900 words, the design decision's home),
five excerpts, four figures, six rules and the lab's tools take the most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `build-test:351` | concept | home | Performance testing and noise: benchmarks and gates, warm-up, median and percentiles, noise only adds, confirmations, reference machines, budgets with headroom, ratchets, provisional metrics, canaries, A/B, layout effects, hybrid CPUs; the mistakes |
| `build-test:135-145` | feature | home | The perf suites; `Measure`; the budget file; confirmed checks; the results file; the canary; the lab's self-tests; scene generators and fixtures; peak-memory helpers; GPU timing; the Medium preset rule |
| `build-test:147-149`, `build-test:223`, `build-test:224` | feature | home | The ratchet and re-baselining; `Tools/PerfStability.py` and `Tools/PerfLock.py`, which the inventory lists twice (in the lab and among the tools) |
| `build-test:402` | code | home | `StrataTests/src/Perf/PerfUtils.cpp:104-146`: `Summarize` and `Measure`, the median and the nearest-rank p95 in integers, the warm-up |
| `build-test:403` | code | home | `StrataTests/src/Perf/PerfUtils.cpp:291-370`: `CheckConfirmed`, decided once within budget, the rest measured again, every attempt recorded |
| `build-test:404` | code | home | `StrataTests/Perf/Budgets.json:2-27`: a budget file whose comment is its specification, and the canary's entry |
| `build-test:405` | code | home | `StrataTests/src/Perf/PerfHarnessTests.cpp:512-543`: the canary, a fixed workload that probes the machine's health |
| `build-test:406` | code | home | `Tools/PerfStability.py:348-390`: `classify`, repeated runs turned into proposals that never raise a budget unless re-baselined |
| `build-test:440` | figure | home | The confirmed check as a flowchart, with a sketch of noise that only adds (a distribution with a hard lower floor) |
| `build-test:443` | figure | home | A budget's life: provisional, measured on the reference machine, 1.5 times the measurement, lowered when cheaper, re-baselined only by A/B |
| `build-test:464` | figure | home | Text captures of `[perf]` lines, an "over the budget in attempt 1 of 3, measuring again" line and a `PerfResults` excerpt |
| `build-test:466` | figure | home | A text capture of the report of `Tools/PerfStability.py --runs 5` |
| `build-test:523` | rule | home | Limits only in `Budgets.json`; budgets only go down; at most 1.5 times measured; commits state the measurement |
| `build-test:525` | rule | home | A failure on a busy machine says nothing about the code: run again on a quiet machine, look at the canary |
| `build-test:527` | rule | home | Perf numbers only from optimized builds, without validation layers, through `ExecuteAndWait` |
| `build-test:530` | rule | home | Peak-memory metrics in a fresh helper process |
| `build-test:531` | rule | home | Complexity claims belong in deterministic unit tests, which run everywhere |
| `new:35` | rule | home | Measure with the Visual Studio preset the budgets were set with (`ctest --preset windows-release -L perf`, the `windows` preset), never `windows-ninja`: MSVC gets `/arch:AVX2` only with the Visual Studio generators, so a `windows-ninja` build compiles other engine code than the one the budgets measured (about 60 words). Evidence: `StrataTests/Perf/Budgets.json:9-11`; `CMakePresets.json:11-14`, `:25-29`, `:75`; `CMake/StrataCompilerOptions.cmake:40-55` |
| `build-test:578` | hands-on | home | Add a provisional metric, measure it in a confirmed check, run `-L perf`, read `PerfResults` and the proposals of `PerfStability.py` |
| `new:36` | hands-on | home | Trace it yourself, by a search: one `[perf]` line of a run back to the `printf` that wrote it, the confirmed check that measured the metric and its entry in `Budgets.json` (about 150 words). Evidence: `StrataTests/src/Perf/PerfUtils.cpp:96-100`, `:141-143`, `:291-370`; `StrataTests/Perf/Budgets.json:27` |
| `build-test:671-678` | term | home | Perf lab; metric, budget, target and provisional (four entries); reference machine; confirmed check; ratchet; canary; interleaved A/B |
| `foundation:303` | concept | use | Percentiles by nearest rank, self time and "CPU, GPU or capped", as `core/profiling` taught them |
| `build-test:146` | feature | link | The catalogue of perf suites, `reference/performance`'s |
| `build-test:116` | feature | use | `RUN_SERIAL` and why the perf tests run alone |
| `build-test:679` | term | link | Median, p95 and nearest rank, whose entries are `core/profiling`'s |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Percentiles by nearest rank, self time, "CPU, GPU or capped", Tracy | `core/profiling` | must |
| The GPU suites and the sample exports as CTests | `engineering/test-kinds` | must |
| Labels, fixtures and `RUN_SERIAL` of CTest | `engineering/test-program` | must |
| Release and Dist, the optimized configurations | `core/first-change` | must |
| GPU timestamps and stages | `gpu/readback-timing` | helps |
| Caches, and why the place of code in memory matters | `basics/computer` | helps |
| Distributions and noise | `basics/math-probability` | helps |
| File locks | `core/files` | helps |
| JSON | `basics/data-formats` | helps |

## `engineering/look-dev` — The look-dev harness

**Covers.** The job: the look-dev harness takes fixed pictures of the samples, of a new project and of a look-dev
scene through headless editors, and compares two sets of them; it is how a rendering change is judged, and the source
of many of the book's pictures. The problem: image regression testing; golden images, which break across GPUs and
drivers, against before-and-after comparisons with signed differences, deterministic repeats, crops of the regions
that matter and GPU times beside the pictures; the mistake of reading a number without looking at the signed image.
The map: capture (copy the samples and never open them in place; build the Basic 3D and look-dev projects with command
scripts; every shot at every size, anti-aliasing mode and repeat; crops enlarged four times; each repeat's
`renderStats` and its difference with the first; a table of GPU stage times; a static page) and compare (differing
pixels, the absolute and the signed difference images, crops side by side, the ratio of GPU times). The contract:
shots are appended and never changed, so that captures of every build keep comparing; the repeats of one build differ
by zero pixels; the harness uses only Python's standard library, its PNG reader and writer included. The toy: the
absolute difference of two images in 25 lines. The real code: the shots file and its projects; `capture_still`, which
drives `viewport.capture` for every repeat; `signed_difference`, red where the after picture is brighter and blue
where it is darker, and why an absolute difference cannot show a region that shifted as a whole; `compare` and
`ratio`; shots with `--debug-view`, `--aa`, `--quality`, and live shots with simulated input. The paragraph that
introduces the page's first Python fence says in one or two sentences what differs from C++ in it: no page of the
book teaches reading Python, so the page supplies it (R45). The shots by area, as the
rendering parts use them, in a table read from `Tools/LookDev/Shots.json` at the pin and never typed from the
inventories: the white furnace, the contact, thin and room shots, the low sun; the mirror, sheet, wet,
patch and Cornell shots of the indirect light, with the lighting views (`lookdev.view.*`), `lookdev.polished` and the
GI shots of the yard, the room, the sun room and the sealed room, about 30 more than the inventory names. How it is tested: `StrataTools.LookDevOffline` without a GPU, and
`StrataTools.LookDev`, which runs `selftest`. Exercises: capture one shot twice and see zero differences, then compare
it against a build with one small change and read the signed image; trace it yourself: follow one shot by a search
from its entry in `Shots.json` through `capture_still` to the `viewport.capture` call and the editor's command that
answers it. At the end the reader can capture and compare
two builds and tell a real change from noise.

**Leaves out.**

- Finding a conversion slip in a shader with the compare → `gpu/shaders`
- What each debug view shows → `gpu/debugging`
- The white furnace as a test of energy → `light/energy`
- How a figure of the book is made from a shot, and the machine that rendered it → `reference/figures`
- The flicker metrics → `engineering/test-kinds`
- Driving the editor with command scripts → `editor/command-scripts`

**Fit.** `fits`: about 3,295 words against M (3,000). One concept, three excerpts, two figures, the toy and the table of
shots by area, read from `Tools/LookDev/Shots.json`, take the most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `build-test:359` | concept | home | Image regression testing: golden images against signed before-and-after differences, deterministic repeats, crops, GPU timings beside pictures; the mistake of a number read without the image |
| `build-test:226`, `render-direct:181`, `render-image:286` | feature | home | The harness and its shots, as three inventories list them (the build's, the light area's furnace and contact shots, and the image area's `--aa`, `--debug-view` and `--live`) |
| `render-indirect:196` | feature | home | The indirect area's shots in the page's table of shots by area, read from `Tools/LookDev/Shots.json` at the pin: the inventory's nine and about 30 more (the lighting views `lookdev.view.lighting`, `.ao`, `.indirect`, `.luminance` and `.albedo`, the probe shot `lookdev.polished`, and the GI shots `lookdev.yard*`, `lookdev.room.view.*`, `lookdev.sunroom*`, `lookdev.sealedroom.view.gi`, `lookdev.grass.view.indirect`) |
| `new:15` | code | home | `Tools/LookDev/Shots.json:1-14`: the format, the rule never to change a shot, the projects and the first shot with its crops |
| `new:16` | code | home | `Tools/LookDev.py:750-769`: `capture_still`, every repeat of a shot through `viewport.capture` |
| `new:17` | code | home | `Tools/LookDev.py:340-359`: `signed_difference`, and the reason in its docstring |
| `build-test:454` | figure | home | The harness: capture (copies, headless editors, shots by sizes, modes and repeats) and compare (differences, signed differences, crops, GPU ratio) |
| `build-test:469` | figure | home | The `index.html` of `Tools/LookDev.py compare`: one pair side by side with its signed difference |
| `new:37` | hands-on | home | Trace it yourself, by a search: one shot from its entry in `Shots.json` through `capture_still` to the `viewport.capture` call and the editor's command that answers it (about 150 words). Evidence: `Tools/LookDev/Shots.json:27`; `Tools/LookDev.py:750-769`; `StrataEditor/src/Editor/EditorViewportCommands.cpp:1211` |
| `build-test:696`, `build-test:697`, `render-image:736` | term | home | Look-dev harness, with look-dev as the image inventory words it (one entry); signed difference image |
| `build-test:172` | feature | use | `StrataTools.LookDevOffline` and `StrataTools.LookDev`, homed with the other `tools` CTests on `engineering/generated-code` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Command scripts run by a headless editor | `editor/command-scripts` | must |
| The passes of a frame, anti-aliasing and TAA | `gpu/frame-tour` | must |
| The test suites and their CTests | `engineering/test-kinds` | must |
| `viewport.capture` and the editor's cameras | `editor/camera-viewport` | helps |
| The debug views | `gpu/debugging` | helps |
| GPU stages and their times | `gpu/readback-timing` | helps |
| Images as bytes: pixels and channels | `basics/bytes` | helps |

## `engineering/ci` — Continuous integration

**Covers.** The job: what runs on every push to `main`, every pull request and every push to a `ci/<name>` branch, and
how a failure is read. The problem: continuous integration; matrix builds; caches and their eviction; builds that keep
going after an error; logs against annotations; the limits of runners; which tests a hosted runner can run (no GPU,
not the reference machine); the mistake of merging a large integration without green CI on the oldest compilers. The
map: the CI matrix (each job against what it builds and tests: configurations, compilers, caches, shader steps, the
labels it leaves out). The contract: CI always builds with warnings as errors; the test step leaves out `gpu` and
`perf`; a branch that lands many changes goes through `ci/<name>` and waits for green CI before it moves `main`. The
toy: a workflow of ten lines with one job; the workflow format (jobs, steps, a matrix, `if`) is taught as the page
needs it. The real code: the triggers and the concurrency group that cancels a superseded run; the matrix (Windows
Release and Debug with `windows-ninja` and sccache, Linux with GCC 14, macOS on `macos-15` with Apple Clang 17, and
Linux without Audio, Physics and GLFW, without the editor and without the package tests); the Visual Studio developer
environment imported on Windows; the compiler cache in GitHub Actions (a key per job and commit, restored by prefix
from the branch or `main`, saved even when tests fail, size caps, and the superseded entries of a branch deleted so
that `main`'s set survives GitHub's 10 GB eviction); the build with `-k 0`, so one run reports every compile error;
the shader steps (`spirv-val` for Vulkan 1.2 on Linux, after StrataShaderTool's patch; the Metal conversion and Apple's
compiler on macOS, whose list of known failures only shrinks); the test step (labels, four at a time, a 900-second
timeout, `STRATA_TEST_TRACE=1`, Linux `ulimit`s so that a runaway test fails alone, and tests that run even after a
failed shader step); the failure annotations of `annotate_failures.py`, because job logs need admin rights and
annotations are public; the Windows Dist job with the Visual Studio generator and the package tests, added after a
change broke Dist unnoticed in wave 3, and kept for a second reason: script builds use the generator the editor was
built with, so its package tests are the only ones that build scripts through the Visual Studio generator (the cached
jobs build with Ninja; linked to `editor/script-builds`); `Tools/CIStatus.py`, which reads a commit's runs, jobs and annotations through
GitHub's API and never prints the token. Strata runs no sanitizer builds, and nothing runs a format check: neither CI
nor a test runs clang-format, so `.clang-format` and `.editorconfig` act only in editors that read them (about 40
words). Pictures of CI's pages need access to
GitHub; where the brief gives none, the page uses text captures and its figures. Exercises: read a failure from its
annotations alone with `CIStatus.py`; trace it yourself: follow one job of the matrix by a search in
`.github/workflows/ci.yml`, from its `preset`, `config` and `exclude` to the test step's `ctest` command line, and say
which labels it leaves out. At the end the reader can say what CI checks for a push, read a failure without
the log, and land a large change through a `ci/<name>` branch.

**Leaves out.**

- The compilers' traps and `CompatLint.py`, run before a push → `engineering/flags-portability`
- The labels and shards the test step selects → `engineering/test-program`
- Why perf budgets are measured on the reference machine, not in CI → `engineering/perf-lab`
- The release workflow → `engineering/releasing`
- How a script build takes the generator the editor was built with → `editor/script-builds`
- The shader dialect and its checks → `gpu/shaders`
- How MoltenVK runs shaders at run time → `gpu/vulkan-nvrhi`

**Fit.** `fits`: about 4,005 words against L (5,000). One concept, two excerpts, three figures and the workflow's
features (the matrix, the cache, the shader and test steps, the annotations, the Dist job) take the most. The count puts
the page at the bottom of L's range.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `build-test:362` | concept | home | Continuous integration: matrices, caches and eviction, keep-going builds, logs and annotations, runners' limits, what hosted runners can test; the `ci/<name>` gate; the mistake of merging without green CI |
| `build-test:192-201`, `build-test:221` | feature | home | The triggers; the matrix; the developer environment; the compiler cache in Actions; `-k 0`; the shader steps; the test step; the annotations; the Windows Dist job and its two reasons (the wave-3 Dist break; its package tests are the only ones that build scripts through the Visual Studio generator, linked to `editor/script-builds`); `Tools/CIStatus.py`, which the inventory lists twice |
| `build-test:238` | feature | home | `.github/scripts`: `annotate_failures.py`, `validate_shaders.sh`, `convert_shaders_to_metal.sh` |
| `build-test:408` | code | home | `.github/workflows/ci.yml:19-60`: a CI matrix, each job with its preset, configuration, cache and key |
| `new:18` | code | home | `.github/workflows/ci.yml:195-215`: the test step with its labels, trace, `ulimit`s and timeout, and the comment that says why |
| `build-test:445` | figure | home | The CI matrix: jobs against what each builds and tests |
| `build-test:446` | figure | home | The compiler cache's keys in GitHub Actions: restore by prefix, deletion of superseded entries, why `main`'s set would otherwise be evicted |
| `build-test:467` | figure | home | GitHub's pages: a CI run, an annotation in a pull request, a release page with its archives and `SHA256SUMS.txt` (see `build-test:774`) |
| `build-test:500` | rule | home | Push large integrations as `ci/<name>` and wait for green: older compilers and libraries reject what local ones accept |
| `build-test:539` | rule | home | Annotations, not logs, carry CI's failures; `known failure:` lines are not error lines |
| `build-test:591` | hands-on | home | Read a CI failure from its annotations alone with `Tools/CIStatus.py annotations <commit>` |
| `new:39` | hands-on | home | Trace it yourself, by a search in `.github/workflows/ci.yml`: one job of the matrix (the Linux job without modules) from its `preset`, `config`, `options` and `exclude` to the test step's `ctest` command line; which labels it leaves out and why (about 150 words). Evidence: `.github/workflows/ci.yml:50-60`, `:213-215` |
| `build-test:646` | term | home | spirv-val |
| `build-test:685-689` | term | home | CI; runner (GitHub Actions); matrix; annotation; `ci/<name>` branch |
| `build-test:772` | open | home | The page names the macOS step's list of known failures as the script's and leaves MoltenVK's run time to `gpu/vulkan-nvrhi` |
| `build-test:774` | open | home | Pictures of CI's pages need GitHub access; the brief decides their source, or the page uses text captures |
| `new:19` | not-done | home | No sanitizer builds (AddressSanitizer, UndefinedBehaviorSanitizer). Evidence: `git grep -niE "fsanitize" 822a7a46 -- CMakeLists.txt CMake StrataTests/CMakeLists.txt .github CMakePresets.json` finds nothing; `.github/scripts/annotate_failures.py:40` only recognizes the word "Sanitizer" in a log |
| `new:38` | not-done | home | No format check: neither CI nor a test runs clang-format, so `.clang-format` and `.editorconfig` act only in editors that read them, although `AGENTS.md` calls the formatting enforced (about 40 words; book.md, "What Strata does not do"). Evidence: `git grep -n -i "clang-format" 822a7a46 -- . ":!Strata/vendor" ":!Docs/Plans"` finds only `AGENTS.md:144` |
| `build-test:202` | feature | link | `Tools/CompatLint.py`, run before a push |
| `build-test:118` | feature | use | The labels the test step leaves out |
| `build-test:483` | rule | use | Warnings as errors in every CI build |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Test labels, shards and `STRATA_TEST_TRACE` | `engineering/test-program` | must |
| Compiler caches, warnings as errors and the three compilers | `engineering/flags-portability` | must |
| git branches and pushes to a remote | `basics/git` | must |
| The Dist configuration | `core/first-change` | must |
| The shader build's outputs and `ShaderEntries.txt` | `engineering/generated-code` | helps |
| MoltenVK | `gpu/vulkan-nvrhi` | helps |
| Shell scripts in bash | `basics/tools` | helps |
| Script builds and the generator they take from the editor | `editor/script-builds` | helps |

## `engineering/releasing` — Packaging and releasing

**Covers.** The job: how a build becomes the archive a person downloads, and how a release is cut and checked. The
problem: packaging, installation and releases; install trees, relocatable installs and a marker; archives; versions
with pre-release suffixes; dry runs; checksums; checking the artifact as a person gets it; release notes; one
publishing job with the right to write; the mistake of testing the build tree instead of the installed layout. The
map: the release workflow (the version job; three build jobs that build Dist, run the Dist tests, pack, unpack and run
the archive and write its checksum; the publish job, which runs only for a tag `vX.Y.Z`) and the installed layout as a
tree. The contract: install rules exist only when the editor, the runtime and the CLI are all built; a file that
releases must ship gets an install rule and an entry in the layout `StrataEditor.Install` checks; release tests run
Dist, and a test whose expectation differs there says so with `#if defined(ST_DIST)`. The toy: `install()` rules and
`include(CPack)` for a program of two files. The real code: `StrataPackaging.cmake` (the executables at the top,
because an export copies the runtime from beside the editor and the launcher finds the samples there; the
`StrataInstall.json` marker, which makes the editor build scripts against the installation's SDK; the README made from
`PackageReadme.md`; the notices; the samples without `.strata`; the script SDK with glm's headers and license; the
manual and the agent skills; CPack's ZIP on Windows and TGZ elsewhere, named `Strata-<version>-<platform>` with that
folder at the top, Linux executables stripped); `strata_resolve_package_version`, which accepts only the project's
version with an optional pre-release suffix; the release workflow's version gate (the tag against
`project(Strata VERSION)`, `Docs/Releases/X.Y.Z.md` present, a run without a tag as a dry run that is never
published); the package step, which unpacks the archive into a fresh folder, checks its files and runs `--version`,
with CMake's own `cpack` because Chocolatey's comes first on the Windows runners; `SHA256SUMS.txt`, checked, and
`gh release create --verify-tag`. The procedure at the end of every wave: bump the version, write the notes, run
`ctest --preset <platform>-dist -LE "gpu|perf"`, push `v<version>-rc1` as a dry run, then the real tag. Strata's
archives are not signed and there are no installers. One sentence on the samples an archive carries:
`Samples.Content` bounds how much they grow it (linked to `engineering/contributing`). How it is tested: `StrataPackaging.Version` in script mode, and
`StrataEditor.Install`, linked. Exercises: make a local package and compare its tree with the install test's list;
dry-run a release on a fork; install a release archive, run `StrataEditor --version` and open a sample; trace it
yourself: follow `StrataInstall.json` by a search from the rule that writes and installs it to the editor's code
that looks for it, and say what changes for script builds when it is there. At the end the
reader can add a file to the release correctly, cut a dry run, and check an archive the way a person would get it.

**Leaves out.**

- Exporting a game and what its folder holds → `worlds/export`
- The install test's steps and the other package tests → `engineering/test-kinds`
- Release notes as the history of features → `appendix/history`
- Building scripts against the installed SDK → `editor/script-builds`
- The CI workflow → `engineering/ci`

**Fit.** `fits`: about 4,295 words against L (5,000). One concept, three excerpts, three figures, three rules, three
exercises and the trace take the most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `build-test:365` | concept | home | Packaging, installation and releases: install trees and markers, archives, pre-release versions, dry runs, checksums, the artifact checked as a person gets it, one job that may publish; the mistakes |
| `build-test:208-215` | feature | home | The install rules; the installation marker; CPack; the package version; the release workflow; the release notes; the release procedure; expectations that differ in Dist |
| `build-test:169` | feature | home | `StrataPackaging.Version`, the test of the package version in script mode |
| `worlds-runtime:169` | feature | home | The installed layout that puts the editor, the runtime and the CLI side by side, as the worlds inventory lists it |
| `build-test:409` | code | home | `.github/workflows/release.yml:45-93`: the version gate: the tag against the project's version, the notes present, a dry run without a tag |
| `new:20` | code | home | `.github/workflows/release.yml:175-226`: the archive unpacked into a fresh folder, its files checked, its programs run for their version, its checksum written |
| `build-test:410` | code | home | `CMake/StrataPackaging.cmake:54-107`: the install rules and CPack; with `CMake/StrataPackageVersion.cmake:7-24`, the version check |
| `build-test:448` | figure | home | The release workflow: the version job, three build jobs, publish only for `vX.Y.Z`; the tags of a dry run |
| `build-test:450` | figure | home | The installed layout as a tree, from the comment of `StrataPackaging.cmake` |
| `build-test:471` | figure | home | The installed folder of a release archive in a file browser |
| `build-test:534` | rule | home | Release tests run Dist; expectations that differ say `#if defined(ST_DIST)`: CI tests Release, only the release steps test Dist |
| `build-test:536` | rule | home | A file that releases must ship needs an install rule and an entry in `StrataEditor.Install`'s layout |
| `build-test:538` | rule | home | Use CMake's own `cpack` on the Windows runners |
| `build-test:586` | hands-on | home | Make a local package with `cmake --install` and `cpack`, and compare the tree with the install test's expected entries |
| `build-test:589` | hands-on | home | Dry-run a release on a fork with a `-rc1` tag of the project's version, and read the version job's checks |
| `build-test:595` | hands-on | home | Install a release archive and check it: unpack, run `StrataEditor --version`, open a sample from the launcher |
| `new:40` | hands-on | home | Trace it yourself, by a search: `StrataInstall.json` from the rule that writes and installs it to the editor's code that looks for it beside its executable; what changes for script builds when it is there (about 150 words). Evidence: `CMake/StrataPackaging.cmake:57-63`; `StrataEditor/src/Editor/ScriptToolchain.h:22`; `StrataEditor/src/Editor/ScriptToolchain.cpp:566` |
| `new:41` | feature | link | One sentence: `Samples.Content` bounds how much the samples grow a release archive; the check and its budgets are taught on `engineering/contributing` |
| `build-test:690-695` | term | home | Install tree and prefix (two entries); CPack; installation marker; pre-release suffix and release candidate (two entries); dry run; checksum file |
| `new:21` | not-done | home | Strata's release archives are not signed or notarized, and there are no installers: CPack writes a ZIP on Windows and a TGZ elsewhere. Evidence: `git grep -niE "signtool\|codesign\|notari" 822a7a46 -- .github CMake CMakeLists.txt` finds nothing; `CMake/StrataPackaging.cmake:95-99` |
| `build-test:168` | feature | use | `StrataEditor.Install`, which checks the layout this page makes; `engineering/test-kinds` teaches it |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| CI workflows: jobs, matrices, steps and annotations | `engineering/ci` | must |
| The Dist configuration | `core/first-change` | must |
| SHA-256 checksums | `basics/data-formats` | must |
| CMake targets and options | `engineering/cmake` | must |
| git tags and pushes | `basics/git` | helps |
| The install test | `engineering/test-kinds` | helps |
| An export copies the runtime from beside the editor | `worlds/export` | helps |
| Script builds and the SDK the editor finds | `editor/script-builds` | helps |

## `engineering/contributing` — The review checklist and the way a change lands

**Covers.** The goal: land a change to Strata the way every change lands. What must be true first, as a list: a change
and its test in the reader's clone (the `ToUpper` change of `core/first-change` serves); a fork with GitHub Actions
on, for the CI step. The frame, in a short list: the golden rules (everything ships with tests, review before every
commit, follow the code style, no hacks or shortcuts, keep the feature test current, and take code from other projects
only under a permissive license with its notice, copyleft only for ideas). The steps: make the change one logical
change; cover new behavior with a test, and for a fix check that the regression test fails without it; extend the
feature test when something registered changed; update `Docs/` and `AGENTS.md` when behavior or a workflow changed,
with `AGENTS.md` under 40,000 characters (`Docs.AgentGuide` checks it and its links); stage the change and review
`git diff --staged` against the six items of the pre-commit checklist (correctness, tests, style, portability,
documentation, commit hygiene), shown as a table with what to look for in each; run every test locally
(`ctest --preset <platform>-debug -j 8`), and `-L perf` in Release for a change that can move performance; verify
exactly what is staged in a clean worktree, in Debug and Release, with the skill's commands; write the commit message
(an imperative subject under 72 characters, a body that says what and why); push a change that lands much as
`ci/<name>` and wait for green CI, reading a failure with `Tools/CIStatus.py`; then merge. Each step names its usual
failure. Result: one commit on `main`, its tests green locally and in CI. Variations: a submodule upgrade, in a commit
of its own with the notices and every test; a change that adds or lowers a perf budget, with the measured values in
the message and `Tools/PerfStability.py --runs 5`; code taken from another project; a change to a sample, whose
command script must keep passing and which `Samples.Content` checks (every sample listed in `Samples.json`, every
source asset credited by exactly one row of `CREDITS.md`, the packs in `ThirdPartyNotices.md`, and the budgets: 25 MB
of source assets, 80 MB for a showcase; three screenshots in 3 MB, six in 8 MB for a showcase; totals that bound how
much a release archive grows; about 100 words). Exercises: take a second small change of the reader's own through
every step, from the staged diff reviewed against the checklist to a `ci/<name>` push read with `CIStatus.py`; find
what a given staged diff breaks of the six items. At the end the reader can take any change of their own through review, a clean
verification and CI to `main`.

**Leaves out.**

- How tests are written and kept from flaking → `engineering/testing`
- The feature test in full → `engineering/feature-test`
- The CI jobs → `engineering/ci`
- Licenses and the notices file → `engineering/third-party`
- Perf budgets and their ratchet → `engineering/perf-lab`
- The code style's rules → `core/conventions`
- A whole feature landed this way → `capstone/land`

**Fit.** `fits`: about 3,090 words against M (3,000). Nine steps, the checklist as a table, one excerpt, four variations
and two exercises take the most. The concept of process discipline (`build-test:369`) is homed on this how-to because no
concept page of the book teaches reviewing and landing a change: the reader learns it by doing the steps, each with its
why in at most two sentences (R31 D25).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `build-test:369` | concept | home | Process discipline: the review checklist, commit hygiene, verification in a clean worktree; the mistake of committing what the working tree compiles, not what is staged |
| `build-test:246-248` | feature | home | Golden rules 2, 3, 5 and 6 (with rules 1 and 4 named); the six-item pre-commit checklist; verifying in a clean worktree |
| `build-test:186` | feature | home | `Docs.AgentGuide`: `AGENTS.md` under 40,000 characters, its links resolving to files and anchors |
| `new:22` | code | home | `.claude/skills/strata-build-test/SKILL.md:210-223`: the staged patch applied to a clean worktree, built and tested in Debug and Release |
| `build-test:543` | rule | home | Verify exactly what is staged in a clean worktree, Debug and Release: the working tree often holds other work, and some bugs show in one configuration only |
| `new:41` | feature | home | `Samples.Content`, the check a change to a sample must pass, in the variation "a change to a sample": every sample listed in `Samples.json` and no directory unlisted, every source asset credited by exactly one `CREDITS.md` row, the packs in `ThirdPartyNotices.md`, and the budgets (MB of 1,000,000 bytes: 25 MB of source assets, 80 MB for a showcase; three screenshots in 3 MB, six in 8 MB for a showcase; totals that keep the standard samples' growth of a release archive to about 60 MB, about 145 MB with showcases); its shard is `Samples` (about 100 words). Evidence: `StrataTests/src/Samples/SampleContentTests.cpp:77-178`; `Docs/DeveloperGuide.md:6479-6490`; `StrataTests/CoreShards.json:24` |
| `new:42` | hands-on | home | The page's exercises (about 250 words): take a second small change of the reader's own through every step, from the staged diff reviewed against the six items to a `ci/<name>` push on a fork read with `Tools/CIStatus.py`; and find in a given staged diff what breaks which item of the checklist. Evidence: `AGENTS.md:457-474`; `.claude/skills/strata-build-test/SKILL.md:210-223` |
| `build-test:520` | rule | use | A regression test checked to fail without its fix |
| `build-test:532` | rule | use | The feature test kept current |
| `build-test:500` | rule | use | Large integrations through `ci/<name>` |
| `build-test:523` | rule | use | A commit that adds or lowers a budget states the measured values |
| `build-test:504`, `build-test:506` | rule | use | A submodule upgraded in its own commit; copyleft code for ideas only |
| `build-test:201` | feature | use | `Tools/CIStatus.py`, to read a failed run |
| `build-test:97` | feature | use | The upgrade procedure of a submodule, as a variation |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| git: staging, diff, commit, branches and push | `basics/git` | must |
| The short source build and one test case | `core/first-change` | must |
| Regression tests that fail without their fix | `engineering/testing` | must |
| The CI jobs and `ci/<name>` branches | `engineering/ci` | must |
| The feature test and how to extend it | `engineering/feature-test` | must |
| The code style | `core/conventions` | helps |
| Perf budgets | `engineering/perf-lab` | helps |
| Licenses and the notices file | `engineering/third-party` | helps |
| git worktrees | `basics/git` | helps |

**Starting state.** No checkpoint download: the page starts from the change `core/first-change` ends with, not yet
committed (`ToUpper` beside `StringUtils::ToLower` in `Strata/src/Strata/Core/StringUtils.h`, and its test case in the
suite `Core.StringUtils`), in the reader's clone at the pin. For the CI step, a fork of the engine's repository with
GitHub Actions on.

**Command-only steps.** none

## Passed on

| Item | Type | To | Why |
| --- | --- | --- | --- |
| `build-test:78` | feature | `gpu/shaders` | slangc's flags are taught there with their reasons (`render-core:122`, and its excerpt of `CMake/StrataShaders.cmake:64-86`) |
| `build-test:80` | feature | `gpu/shaders` | `EmbeddedShaders::GetAll` and `Find` are taught there with `ShaderLibrary` (`render-core:125`) |
| `build-test:171` | feature | `gpu/shaders` | The HLSL target check is one of the dialect's checks, homed there (`render-core:129`, `render-core:131`) |
| `build-test:185` | feature | `gpu/shaders` | `Architecture.Shaders` checks the dialect, whose checks are taught there (`render-core:129`) |
| `build-test:480` | rule | `gpu/shaders` | The same rule as `render-core:576`, homed there |
| `build-test:644`, `build-test:645` | term | `gpu/shaders` | Slang, slangc and SPIR-V are defined there (`render-core:720`, `render-core:721`); the word layout is taught on `engineering/generated-code` |
| `build-test:125` | feature | `gpu/first-triangle` | `book.md` makes it the home of writing a GPU test with the shared `GPUContext`; `engineering/test-kinds` uses it |
| `build-test:512` | rule | `gpu/first-triangle` | The same rule as `render-core:607`, homed there |
| `build-test:648` | term | `gpu/frame-tour` | The home of invariant positions and the prepass's `EQUAL` test |
| `build-test:647` | term | `gpu/vulkan-nvrhi` | MoltenVK's entry (`render-core:682`) is there |
| `build-test:668` | term | `gpu/debugging` | The validation layer's entry (`render-core:691`) is there |
| `build-test:669` | term | `gpu/readback-timing` | The readback entry (`render-core:758`) is there |
| `build-test:146` | feature | `reference/performance` | The catalogue of perf suites is that page's table, beside every budget |
| `build-test:180`, `build-test:181` | feature | `core/layers-registries` | `Architecture.Layering` and `Architecture.Libraries` are taught there with the layer table (`foundation:175`); `engineering/cmake` writes the file the second reads and links both |
| `build-test:494` | rule | `core/layers-registries` | The same rule as `foundation:470`, homed there |
| `build-test:652`, `build-test:654` | term | `core/layers-registries` | The layer table's entries (`foundation:561`, `foundation:563`) and the composition root (`foundation:549`) are there |
| `build-test:651` | term | `core/map` | The meanings of "layer" (`foundation:558`) are separated there |
| `build-test:628` | term | `core/conventions` | `book.md` makes it the home of `ST_CORE_ASSERT` and `ST_CORE_VERIFY` |
| `build-test:643` | term | `core/files` | The home of atomic writes (`foundation:628`) |
| `build-test:642` | term | `core/files` | File lock: one OS lock, homed where `FileLock` is taught (`foundation:126`); `engineering/third-party` links it (duplicates.md:52) |
| `build-test:670` | term | `core/first-frame` | The headless entry (`foundation:583`) is there |
| `build-test:679` | term | `core/profiling` | Percentiles and the nearest rank (`foundation:608`) are taught there |
| `build-test:249` | feature | `core/debugging` | `book.md` makes it the home of debugging one test |
| `build-test:184` | feature | `scripting/abi-sdk` | It checks that page's rule (`scripting:490`), which names it |
| `build-test:225` | feature | `physics/tuning` | The sweep is taught there with the settle scenes (`physics:150`) |
| `build-test:682` | term | `editor/command-scripts` | The command script's entry (`editor-core:662`) is there |
| `build-test:411` | code | `editor/command-scripts` | The smoke script (`StrataTests/Editor/SmokeCommands.json.in:1-30`) is quoted once, beside `editor-core:450`; `engineering/test-kinds` links it as an end-to-end test as data (duplicates.md:37) |
| `build-test:271` | concept | `basics/build` | `book.md`: how a C++ program is built is that primer's; GNU ld's order of static libraries stays an example on `engineering/third-party` |
| `build-test:609-611` | term | `basics/build` | Translation unit, linker, and static, shared and module libraries are that primer's words |
| `build-test:598` | hands-on | `make/automated-playtests` | A game maker's smoke test by command script is a play-test, taught there |
| `build-test:601` | hands-on | `make/export` | Running the exported game headless, with a screenshot and a perf log, belongs with running the export |
| `build-test:765` | open | `appendix/history` | The dating of the build and test features belongs with "which release brought what" |
| `build-test:541` | rule | `nowhere` | It repeats `foundation:496`, homed on `core/platform` |
| `build-test:746` | open | `nowhere` | A note on the files the survey did not read |
| `build-test:755` | open | `nowhere` | The lead line of a list whose entries are `build-test:756`, `build-test:758` and `build-test:759` |

## Not taken

none

## Questions for the planner

none
