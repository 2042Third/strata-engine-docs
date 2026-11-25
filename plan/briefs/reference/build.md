# Brief: `reference/build`

| Field | Value |
| --- | --- |
| Title | CMake options, presets, test labels, tools |
| Kind | R |
| Size | S |
| Tracks | - |
| Needs | `basics/build` |
| From | build-test ch. 15 "Tools reference" |
| Unit | `plan/allocation/reference.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `reference/build` — CMake options, presets, test labels, tools

**Covers.** The paragraph on top says what the page is: what a person types to configure, build and test Strata, and
the tools of `Tools/`, parsed at the pin. The tables, in this order. (1) The CMake options, parsed from every
`option(` of `CMakeLists.txt` and `CMake/*.cmake`, each with its default and help text (the program switches, Tracy,
warnings as errors, the optional modules `ST_WITH_*`, the window backend, the compiler cache, precompiled headers, the
instruction set). (2) The presets of `CMakePresets.json`: configure, build and test presets, with their build folders.
(3) The CTest names and labels of `StrataTests/CMakeLists.txt` (`gpu`, `perf`, `package` and the others), with what each
label selects. (4) The shards of `StrataTests/CoreShards.json`, each with its suites, from the file, never from the
Developer Guide (its count is wrong there; `engineering`'s brief holds that erratum). (5) The tools, one row each with
what it does, how it is run and the page that teaches it: the 15 scripts of `Tools/` and the `LookDev` folder, and the
generators kept elsewhere (`StrataTests/FeatureTest/Tools/GenerateAssets.py`, `StrataEditor/Tools/GenerateIconHeader.py`,
the CI scripts); a hand-checked table, since no route lists them (`new:4`). Hand-written besides: one introduction per
table and `## Where it lives in Strata` (`CMakeLists.txt`, `CMake/`, `CMakePresets.json`, `StrataTests/CMakeLists.txt`,
`Tools/`). The tool is `tools/reference.py parse`, route "build".

**Leaves out.**

- Building Strata step by step → `engineering/building`
- Inside the CMake project → `engineering/cmake`
- Compiler flags and portability → `engineering/flags-portability`
- The test program, shards, sweeps and locks → `engineering/test-program`
- Test kinds and labels, with their reasons → `engineering/test-kinds`
- The perf lab's tools → `engineering/perf-lab`
- Generated code and its generators → `engineering/generated-code`

**Fit.** `fits`: about 1,100 words against S (1,500). The generated tables give the page its size: the CMake options,
the presets, the CTest names and labels and the shards, about 1,500 words. The prose is the paragraph on top, five
introductions, the tools table (about 20 rows of one line), the erratum and the strip.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:4` | erratum | home | `Docs/DeveloperGuide.md:828` writes `Tools/GenerateAssets.py`; the file is `StrataTests/FeatureTest/Tools/GenerateAssets.py`, and the tools table names it there. Evidence: `Docs/DeveloperGuide.md:828`; `git ls-tree --name-only 822a7a46 Tools/` has no `GenerateAssets.py`; `StrataTests/FeatureTest/Tools/GenerateAssets.py` exists at the pin |
| `build-test:28-39` | feature | link | The root project, its switches and options, the optional modules, `ST_WITH_*`, the compiler cache, precompiled headers, instruction sets and the configurations |
| `build-test:43` | feature | link | The output layout, `build/<preset>/bin/<Config>/` |
| `build-test:55-58` | feature | link | The configure, build and test presets and the parallel-agent build folders |
| `build-test:113-114` | feature | link | The shards and `Testing.Shards` |
| `build-test:118` | feature | link | The labels |
| `build-test:221-238` | feature | link | Every tool, from `Tools/CIStatus.py` to the CI scripts |
| `build-test:240` | feature | link | The rule that every tool is standard-library Python run with `python -I` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| How a C++ program is built: from two files by hand to CMake | `basics/build` | must |
| A terminal and its commands | `basics/tools` | must |
| Building Strata | `engineering/building` | helps |
| Test kinds and labels | `engineering/test-kinds` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

None: the glossary homes no term on this page.

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-reference-2 | should | shape | `reference/physics`, `reference/animation`, `reference/audio-input`, `reference/ui`, `reference/worlds-runtime`, `reference/editor`, `reference/automation`; some tables of `reference/renderer`, `reference/assets`, `reference/build` | The catalogue pages and `reference/scene`, `reference/core` and `reference/settings` name the teaching page of each group or table. These area pages plan only "one introduction per table", and their Covers never says that an introduction names where the subject is taught, so a reader who looks up a limit, a format or a service cannot go on to the page that explains it. | Each of these Covers says that every table introduction names the page that teaches its subject, one sentence each (about 20 words a table, about 40 tables, about 800 words in all; kind R has no size check). On `reference/renderer` this concerns the bindings, switches, fallbacks and device tables; on `reference/assets` the types, importers, budgets and statistics; on `reference/build` the options, presets, labels and shards. | `allocation/reference.md:480`, `:567`, `:629-630`, `:689`, `:744-745`, `:801`, `:867`, `:930`, `:1050`, `:394-395`; compare `:110-111`, `:190`, `:263`, `:328`, `:989` |
| critic-reference-9 | should | missing-item | `reference/build`, table (1) | The table parses only `option(`, so three cache variables that a person sets with `-D` are missing: `STRATA_SLANG_ROOT` (an extracted Slang release for a machine without a network, also read from the environment), `STRATA_PACKAGE_VERSION` (the archive's version with a suffix such as `-rc1`, for the dry run every release starts with) and `STRATA_COMPILER_CACHE_PROGRAM` (the ccache or sccache of `STRATA_COMPILER_CACHE`). `AGENTS.md` and the Developer Guide name the first two. | Route "build" also parses `set(STRATA_... CACHE <type> "<help>")` and `find_program(STRATA_... DOC "<help>")` in `CMakeLists.txt` and `CMake/*.cmake`, and table (1) shows them with their type; one sentence in its introduction (about 20 words). `../pipelines.md` §7.1, row "build", says so. | `allocation/reference.md:1041-1043`; `../pipelines.md:1100`; `CMake/StrataSlang.cmake:278-279`; `CMake/StrataPackaging.cmake:25-26`; `CMake/StrataCompilerOptions.cmake:9`; `AGENTS.md:89`, `:482`; `Docs/DeveloperGuide.md:365`, `:3916` |
| critic-reference-11 | should | missing-item | `reference/automation`, table (6) | The environment table lists Strata's own nine variables but no system variable that changes what the programs do: `CXX`, which picks the compiler of script builds when the compiler the engine was configured with is not on the machine (a release archive on Linux or macOS), and `XDG_DATA_HOME`, `XDG_RUNTIME_DIR` and `XDG_CACHE_HOME`, which move the user data and runtime folders on Linux. A search for `CXX` and `XDG_` in the plan finds nothing. | Table (6) gets a second part, "system variables Strata reads", one row each with the program and the effect, checked against `ScriptToolchain.cpp` and `PosixPlatform.cpp`, and a row for `STRATA_SLANG_ROOT` that names `reference/build`. About 80 words. | `allocation/reference.md:926-929`; `StrataEditor/src/Editor/ScriptToolchain.cpp:368-381`; `StrataEditor/src/Editor/ScriptBuild.cpp:400`; `Strata/src/Platform/Posix/PosixPlatform.cpp:356-362`, `:418-437`; `Strata/src/Strata/Core/Platform.h:71-77`, `:115-127` |
| critic-reference-17 | could | missing-item | `reference/build` | The layer table, `StrataTests/Architecture/Layers.json` (19 layers, each with its paths, what it may include, whether it is tooling and its option, and the `ExternalOwners`), has no reference table, though a contributor checks it before every include across folders. `core/layers-registries` teaches it with a figure and an excerpt of three layers. | `reference/build` adds a generated table from `Layers.json` (layer, paths, may include, tooling, option, notes) and the `ExternalOwners` list, with an introduction that names `core/layers-registries`. About 40 words; route "build" for the planner. | `allocation/core.md:743-745`, `:800-801`; `StrataTests/Architecture/Layers.json:5`, `:126`; `AGENTS.md:207` |
