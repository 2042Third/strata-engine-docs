# Brief: `engineering/building`

| Field | Value |
| --- | --- |
| Title | Building Strata |
| Kind | H |
| Size | M |
| Tracks | E |
| Needs | `core/first-change` |
| From | build-test ch. 2 (every preset, configuration and option, where binaries land, when to configure again, the validation layer); the short source build is `core/first-change` |
| Unit | `plan/allocation/engineering.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `cache-variable` | Cache variable | `CMakeCache.txt` |
| `generator-cmake` | Generator (CMake) | - |
| `multi-config-generator` | Multi-config generator | - |
| `preset` | Preset | - |
