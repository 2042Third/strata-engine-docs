# Brief: `engineering/cmake`

| Field | Value |
| --- | --- |
| Title | Inside Strata's CMake |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `core/layers-registries` |
| From | build-test ch. 3 (targets and usage requirements, `strata_add_layer_libraries`, `strata_layer_link`, the link closure, the linker map, `LayerLibraries.json`, optional modules and `ST_WITH_*`) |
| Unit | `plan/allocation/engineering.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `cmake-language-defer` | `cmake_language(DEFER)` | - |
| `exclude-from-all` | `EXCLUDE_FROM_ALL` | - |
| `glob-recurse-configure-depends` | `GLOB_RECURSE CONFIGURE_DEPENDS` | - |
| `generator-expression` | Generator expression | - |
| `interface-library-cmake` | Interface library (CMake) | - |
| `link-closure` | Link closure | - |
| `linker-map` | Linker map | - |
| `script-mode` | Script mode | cmake -P |
