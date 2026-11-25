# Inventory: Building, testing, CI, packaging and releases

Area key: `build-test`. Surveyed at G:/GameEngineAI, branch `main`, commit 822a7a46 (project version 0.7.0; wave 8
work in progress, so features marked "wave 8" ship first in 0.8.0). All paths are relative to the repository root.
Line numbers are for this commit.

Abbreviations for document references:
- DG = `Docs/DeveloperGuide.md`. Headings: Building (l.149), Precompiled headers (l.223), Optional modules (l.256),
  macOS and MoltenVK (l.288), Windows subsystem (l.316), Packages (l.339), Releases (l.353), Testing (l.374), Unit tests
  (l.385), Shards, sweeps and locks (l.400), GPU tests (l.431), Perf tests (l.466), Look-dev harness (l.666), End-to-end
  tests (l.775), Test rules and helper processes (l.782), Feature test (l.814), Script modules and package tests (l.883),
  Platform seams (l.1086), Shaders (l.3855, items 4 "The build", 5 "The pin", 6 "The checks"), Working with third-party
  code (l.6411), Samples (l.6451).
- ARCH = `Docs/Architecture.md`, "Targets and dependencies" (l.26-187).
- AG = `AGENTS.md`: Golden rules (l.17), Building (l.49), Testing (l.92), Pre-commit review checklist (l.457), Working with
  third-party code (l.475).
- SK = `.claude/skills/strata-build-test/SKILL.md` (223 lines).
- RM = `Docs/Roadmap.md` (Status l.34ff, waves l.1099ff).

---

## 1. Features

### 1.1 The CMake project and its options

| Feature | What it is | Where it lives | Documented | Arrived |
| --- | --- | --- | --- | --- |
| Root project | `project(Strata VERSION 0.7.0)`, C and C++, refuses in-source builds and missing submodules with the fix in the message | `CMakeLists.txt` l.1-15 | AG Building; DG Building | first release 0.3.0 (versions bumped per wave) |
| Program switches | `STRATA_BUILD_EDITOR`, `_RUNTIME`, `_CLI`, `_TESTS` (all ON) | `CMakeLists.txt` l.19-22, l.70-91 | DG Building l.172 | |
| Tracy switch | `STRATA_ENABLE_TRACY` (OFF): adds Tracy client (`TRACY_ON_DEMAND`) | `CMakeLists.txt` l.23; `Strata/vendor/CMakeLists.txt` l.234-239; `Strata/CMakeLists.txt` l.48 | DG Building | |
| Warnings as errors | `STRATA_WARNINGS_AS_ERRORS` (ON; CI always on); also turns Slang warnings into errors | `CMakeLists.txt` l.24; `CMake/StrataCompilerOptions.cmake` l.106-116; `CMake/StrataShaders.cmake` l.84-86 | AG Building; DG Building l.174 | |
| Optional engine modules | `STRATA_WITH_PHYSICS`, `_AUDIO`, `_ANIMATION`: a layer with an `"Option"` in `Layers.json` is not built, nor its vendor library (box3d, miniaudio) | `CMakeLists.txt` l.25-30; `CMake/StrataLayers.cmake` l.192-196; `Strata/vendor/CMakeLists.txt` l.134, l.149 | DG Optional modules l.256 | wave 4 (0.4.0) |
| Optional window backend | `STRATA_WITH_GLFW`: OFF swaps `Platform/GLFW` for `Platform/NoWindow` (headless only; "the configuration a console port starts from") | `CMakeLists.txt` l.31-34; `CMake/StrataLayers.cmake` l.112-117 | DG Optional modules l.280; DG Platform seams l.1086 | wave 8 (CI job renamed "no GLFW") |
| Editor needs every module | Configure fails if a module or GLFW is off while the editor is on | `CMakeLists.txt` l.35-48 | DG Optional modules | 0.4.0 |
| `ST_WITH_*` definitions | 1/0 compile definitions on `Strata_Core` PUBLIC, never a header, so no file reads 0 for want of an include | `Strata/CMakeLists.txt` l.22-29 | DG Optional modules l.263 | 0.4.0 |
| Compiler cache | `STRATA_COMPILER_CACHE` (+ `STRATA_COMPILER_CACHE_PROGRAM`): ccache/sccache as compiler launcher; refuses Visual Studio generators; switches MSVC debug info to embedded `/Z7`; turns precompiled headers off by default | `CMakeLists.txt` l.50-58; `CMake/StrataCompilerOptions.cmake` l.6-18; `CMake/StrataConfigurations.cmake` l.42-48 | DG Building l.191 | wave 4 (0.4.0) |
| Precompiled headers | `STRATA_PRECOMPILED_HEADERS`: `strata_precompile_headers` force-includes `stpch.h` (per layer library), `EditorPch.h`, `TestsPch.h` | `CMake/StrataCompilerOptions.cmake` l.122-130; `Strata/src/stpch.h`; `StrataTests/src/TestsPch.h`; `StrataTests/CMakeLists.txt` l.160-163 | DG Precompiled headers l.223 | wave 4 (0.4.0) |
| Instruction-set options | `STRATA_USE_SSE4_1 ... AVX512`, `LZCNT`, `TZCNT`, `F16C`, `FMADD`, `STRATA_CROSS_PLATFORM_DETERMINISTIC`, `STRATA_CROSS_COMPILE_ARM` -> `strata_engine_cpu_options` -> `StrataEngineCodegen` INTERFACE target linked PRIVATE by every layer | `CMake/StrataCompilerOptions.cmake` l.20-93; `Strata/CMakeLists.txt` l.5-12 | DG Building l.179 "Instruction sets" | defaults kept from before 0.5.0 (box3d move) |
| Build configurations | Debug / Release (optimized, asserts on) / Dist (Release flags + `ST_DIST`, asserts compiled out); imported targets map Dist -> Release | `CMake/StrataConfigurations.cmake` l.1-26; `strata_configure_target` defines `ST_DEBUG`/`ST_RELEASE`/`ST_DIST` (`StrataCompilerOptions.cmake` l.100-103) | AG Building; DG Releases item 3 | |
| C++20, no extensions, compile_commands | global settings | `StrataConfigurations.cmake` l.28-32 | | |
| Static MSVC runtime | `MultiThreaded[Debug]` everywhere "so exported games need no redistributable" | `StrataConfigurations.cmake` l.40-41 | | |
| Release linker flags (MSVC) | `/DEBUG /OPT:REF /OPT:ICF` in Release and Dist | `StrataConfigurations.cmake` l.49-51 | | |
| Output layout | executables and DLLs in `build/<preset>/bin/<Config>`, static libs in `lib/` | `StrataConfigurations.cmake` l.53-56 | AG Building | |
| Warning policy | `strata_configure_target`: MSVC `/W4 /permissive- /utf-8 /Zc:__cplusplus /Zc:preprocessor /Zc:inline /bigobj [/WX] [/MP]`, `NOMINMAX WIN32_LEAN_AND_MEAN`; GCC/Clang `-Wall -Wextra -Wno-missing-field-initializers [-Werror]` | `StrataCompilerOptions.cmake` l.95-120 | AG Code style | |
| Vendor warnings off | vendor dir strips `/W*`, adds `/W0` or `-w`; everything added `SYSTEM` | `Strata/vendor/CMakeLists.txt` l.12-20 | AG Working with third-party code | |
| GCC <14.4 workaround | `-Wno-array-bounds -Wno-stringop-overflow` for the tests only, with the reason | `StrataTests/CMakeLists.txt` l.110-118 | (comment) | |
| Runtime resource copy | `strata_copy_runtime_resources` POST_BUILD copy | `StrataCompilerOptions.cmake` l.132-140 | | |
| Windows application manifest | UTF-8 active code page, long paths, Win10/11 | `CMake/Strata.manifest`; added to `StrataTests` l.199-203 (and the programs) | AG Code style (UTF-8 strings) | |
| Source globbing | `file(GLOB_RECURSE ... CONFIGURE_DEPENDS)`; re-configure after adding/removing files; shaders are not globbed (listed) | `CMake/StrataLayers.cmake` l.99-118; `StrataTests/CMakeLists.txt` l.62-64 | AG Building; DG Building l.187 | |

### 1.2 Presets

| Feature | What it is | Where | Documented |
| --- | --- | --- | --- |
| Configure presets | `windows` (VS 2026, x64), `windows-vs2022`, `windows-ninja` (Ninja Multi-Config with `cl`, from a dev environment; CI's cached Windows builds), `linux` and `macos` (Ninja Multi-Config; macOS deployment target 14.0); all to `build/<presetName>`, host-conditioned | `CMakePresets.json` l.1-48 | AG Building; DG Building |
| Build presets | `<preset>-debug/-release/-dist` (15) | `CMakePresets.json` l.49-65 | |
| Test presets | same 15 names, inherit `test-base`: output on failure, `noTestsAction: error` | `CMakePresets.json` l.66-89 | AG Testing |
| Parallel-agent build dirs | `cmake --preset windows -B build/agent-<name>` | (convention) | AG Building "Parallel agents" |

### 1.3 Engine library structure in the build (the layer table is the build)

| Feature | What it is | Where | Documented | Arrived |
| --- | --- | --- | --- | --- |
| Layer libraries | `strata_add_layer_libraries`: reads `StrataTests/Architecture/Layers.json`, globs sources once, gives each file to exactly one layer (configure fails naming files in none or two), makes `Strata_<Layer>` STATIC (or INTERFACE if nothing compiles) linking PUBLIC only built layers of `MayInclude`; `Tooling` layers `EXCLUDE_FROM_ALL`; `Option` layers built only when on | `CMake/StrataLayers.cmake` l.1-278 (ownership l.155-186, targets l.188-243) | ARCH l.31-46; SK "Configure and build" | wave 1 table, wave 4 libraries (0.4.0) |
| Glob-to-regex | `strata_glob_to_regex` with LayeringAnalyzer's `**/`, `**`, `*`, `?` semantics | `StrataLayers.cmake` l.41-54 | ARCH l.34 | |
| `LayerLibraries.json` | written at end of configure via `cmake_language(DEFER)`, the real links read from targets; checked by `Architecture.Libraries` | `StrataLayers.cmake` l.30-39 (defer), l.315-339 (write); `StrataTests/src/Architecture/LibrariesTests.cpp` | ARCH l.44-46 | 0.4.0 |
| `strata_layer_link` | attaches vendor/system libs to a layer, refuses layer libraries (layers link only by MayInclude) | `StrataLayers.cmake` l.341-365; table of rows `Strata/CMakeLists.txt` l.44-77 | ARCH l.72-85 | |
| `Strata` and `StrataTooling` | INTERFACE libraries of runtime layers / tooling layers | `Strata/CMakeLists.txt` l.206-214 | ARCH l.107-119 | |
| Link-closure check | `strata_check_link_closure(StrataRuntime FORBID imgui ImGuizmo nfd cgltf zstd_compress StrataEditorCore StrataEditorUI StrataCLILib doctest)`: walks LINK_LIBRARIES and INTERFACE_LINK_LIBRARIES transitively at end of configure, fails naming the path | `CMakeLists.txt` l.74-79; `StrataLayers.cmake` l.367-429 | ARCH l.89-92 | 0.4.0 |
| Linker-map check | `StrataRuntime` links with a map (`/MAP`, `-Map=`, `-map,`); CTest `StrataRuntime.NoTooling` greps it for forbidden objects/libraries, requiring `RuntimeApplication` and `Application` objects first | `StrataRuntime/CMakeLists.txt` l.13-23; `StrataTests/Architecture/CheckNoTooling.cmake`; `StrataTests/CMakeLists.txt` l.372-383 | ARCH l.92-97; SK | 0.4.0 |
| Vendor libraries only tools use | `imgui`, `ImGuizmo`, `cgltf`, `zstd_compress`, `nfd` `EXCLUDE_FROM_ALL`; stb one object per header so linker drops unused | `Strata/vendor/CMakeLists.txt` l.87-131, l.206 | ARCH l.87-89 | |

### 1.4 Generated code at build/configure time

| Feature | What it is | Where | Documented | Arrived |
| --- | --- | --- | --- | --- |
| Shader build | `strata_add_shaders(<target> SOURCE_DIR SHADERS VARIANTS INVARIANT_POSITION INCLUDE_DIRS)`: per entry slangc -> `<name>.raw.spv` (with `SLANG_RUN_SPIRV_VALIDATION=1`), then `StrataShaderTool` -> `<name>.spv` + `<name>.h`; generated `EmbeddedShaderRegistry.cpp`; `ShaderEntries.txt` manifest; stage from name suffix; variants = same source + defines; every entry depends on every include | `CMake/StrataShaders.cmake` l.1-226; call `Strata/CMakeLists.txt` l.79-201 (about 113 entries) | DG Shaders item 4 (l.3887ff) | Slang: wave 8; registry earlier with glslang |
| slangc flags | `-target spirv -profile spirv_1_5 -matrix-layout-column-major -fvk-{t,s,b,u}-shift 0/128/256/384 -default-image-format-unknown -warnings-disable 39001,41012 [-warnings-as-errors all]`, each with a reason; what is not passed and why | `StrataShaders.cmake` l.64-86 | DG Shaders item 4 | wave 8 |
| StrataShaderTool | host tool, standard library only: parses SPIR-V, decorates `BuiltIn Position` `Invariant` for `INVARIANT_POSITION` sources (`Scene/Mesh.vert` and variants), writes atomically (temp + rename), formats the header | `CMake/StrataShaderTool/StrataShaderTool.cpp`, `SpirvModule.h/.cpp`; target built in `strata_add_shader_tool` (`StrataShaders.cmake` l.30-44) into `build/<preset>/tools` | DG Shaders item 4; tests `Renderer.ShaderTool` | wave 8 |
| Runtime lookup | `Strata::EmbeddedShaders::GetAll/Find` | `Strata/src/Strata/Renderer/EmbeddedShaders.h` | DG Shaders | |
| Slang pin | `strata_find_slang`: `STRATA_SLANG_ROOT` (cache var, default env var) or a pinned archive per host (Windows x64, Linux x64, macOS arm64/x64) with SHA-256, fetched once into a per-user cache under a file lock (900 s), 3 download attempts, digest check, extraction of only listed files by a child CMake, stamp file, atomic rename; `slangc -v` version check | `CMake/StrataSlang.cmake` l.1-332 | DG Shaders item 5 (l.3911ff); AG Working with third-party code | wave 8 |
| Embedded files | `strata_embed_file(<target> <file> <function>)`: configure-time hex dump into a `std::span<const uint8_t>` function; reconfigures on edit | `CMake/StrataEmbeddedFiles.cmake`; used for Roboto Medium `Strata/CMakeLists.txt` l.203-204, editor fonts | DG Working with third-party code l.6432 | |
| Version header | `Version.h.in` -> `Generated/Strata/Core/Version.h` (`ST_VERSION_*`, `c_EngineVersion`) | `Strata/src/Strata/Core/Version.h.in`; `Strata/CMakeLists.txt` l.31 | ARCH l.102-105; DG Releases item 1 | |
| Build commit header | `StrataVersionCommit` custom target runs `CMake/StrataVersionCommit.cmake` in script mode at every build; `git rev-parse --short=12 HEAD` or "unknown"; `file(CONFIGURE)` rewrites only on change | `CMake/StrataVersionCommit.cmake`; `Strata/CMakeLists.txt` l.32-42 | ARCH l.103-105 | |
| Sample copy | `StrataCopySamples.cmake` script-mode sync of `Samples/` next to executables (skips `.strata`, removes stale files) via the `StrataSamples` target | `CMake/StrataCopySamples.cmake`; `StrataEditor/CMakeLists.txt` (target) | DG Repository layout l.137 | |

### 1.5 Third-party code

| Feature | What it is | Where | Documented |
| --- | --- | --- | --- |
| 19 pinned shallow submodules | glfw, NVRHI, glm, miniaudio, entt, spdlog, json, imgui (docking), ImGuizmo, stb, cgltf, meshoptimizer, MikkTSpace, doctest, tracy, nfd, Vulkan-Headers, zstd, box3d | `.gitmodules`; `Strata/vendor/` | AG Working with third-party code; DG l.6411 |
| Vendor wrapper | each library's options forced (`strata_vendor_option` = CACHE INTERNAL), NVRHI Vulkan-only with validation, `nvrhi_vk -> nvrhi` link order fix for GNU ld, glm defines (`GLM_FORCE_DEPTH_ZERO_TO_ONE`; no layout-changing defines because glm crosses the script ABI), spdlog with bundled fmt, json without implicit conversions | `Strata/vendor/CMakeLists.txt` l.22-85 | |
| box3d built from sources | not its own CMake (would set a cache entry in-tree, add /W4, install rules); C17 with extensions; `-ffp-contract=off` for cross-platform determinism; `/arch:AVX2` on `wide8.c` for MSVC; asserts follow `ST_CORE_ASSERT`; `B3_MAX_MESH_CONTACT_TRIANGLES=4096` | `Strata/vendor/CMakeLists.txt` l.144-182 | DG Working with third-party code l.6437-6449 |
| zstd split | `zstd_decompress` (games) and `zstd_compress` (`EXCLUDE_FROM_ALL`, tooling only); no ASM, no legacy, no threading; `/arch:AVX2` on MSVC for BMI2 | `Strata/vendor/CMakeLists.txt` l.184-227 | |
| stb one object per header | `Strata/vendor/Implementations/Stb*.c` | `Strata/vendor/CMakeLists.txt` l.107-116 | ARCH l.87-89 |
| Third-party notices | table of library, version, license, "shipped in games", purpose; fonts; "Code derived from other projects" with full license text; sample asset packs | `ThirdPartyNotices.md` (96 lines) | DG Working with third-party code l.6417-6430 |
| Upgrade procedure | check out new tag, rebuild, all tests, update notices, separate commit; box3d keeps `Physics.Box3D` golden hash (values from box3d's own `test/test_determinism.c`) | (process) | AG l.475; DG l.6446-6449; SK |
| Code-from-other-projects rule | permissive only, copyleft for ideas only, notice row + license text + commit message | (process) | AG golden rule 1; DG l.6417 |
| Box3D determinism scenario for tests | `StrataTestsBox3DScenarios` compiles box3d's `shared/determinism.c` etc. for tests only | `StrataTests/CMakeLists.txt` l.127-150 | DG l.6446 |

### 1.6 Test programs and CTest organisation

| Feature | What it is | Where | Documented | Arrived |
| --- | --- | --- | --- | --- |
| `StrataTests` executable | doctest; all of `StrataTests/src` (minus editor tests without the editor and modules' tests without the module); links `Strata StrataTooling StrataScriptCore doctest stb StrataShaderToolCore meshoptimizer` (+box3d, `StrataEditorUI`, `ImGuizmo`, `StrataCLILib`) | `StrataTests/CMakeLists.txt` l.62-203 | DG Unit tests; ARCH l.118 | |
| Test-build definitions | `STRATA_SOURCE_DIR`, `STRATA_FEATURE_TEST_DIR`, `STRATA_LAYER_LIBRARIES_FILE`, `STRATA_PERF_RESULTS_FILE`, `STRATA_TEST_SCRIPTS_<KIND>`, `ST_TESTS_HAVE_EVERY_MODULE`, `ST_TESTS_HAVE_EDITOR`, `STRATA_TESTS_HAVE_CLI`, `STRATA_TESTS_HAVE_RUNTIME`, `DOCTEST_CONFIG_NO_POSIX_SIGNALS` | `StrataTests/CMakeLists.txt` l.164-197 | DG Optional modules l.273-279 | |
| Module-dependent test files | `STRATA_TESTS_OF_PHYSICS/AUDIO/ANIMATION/GLFW` lists, feature test left out without every module | `StrataTests/CMakeLists.txt` l.73-102 | DG Optional modules l.273 | 0.4.0 |
| Test script modules | `StrataTestScripts{API,ReloadV1,ReloadV2,Faults,LoadFault,ABIMismatch,Malformed,NewerSDK,Dependent,FeatureTest,World}` + `StrataTestScriptDependency`, `StrataTestLibrary`, built through `strata_add_script_module` | `StrataTests/CMakeLists.txt` l.7-60; `StrataScriptCore/CMake/StrataScriptModule.cmake` l.21 | DG Script modules and package tests l.885 | |
| `main` of the test runner | console streams; log at Warn; helper-mode dispatch; registers engine modules with asset pipeline (+editor preference sections); fake CMake; fake editor; disables execution-speed throttling; private `STRATA_RUNTIME_DIR`, `STRATA_RECENT_PROJECTS`, `STRATA_SCRIPT_BUILDS_DIR`; `doctest::Context`; shuts down shared GPU | `StrataTests/src/TestMain.cpp` l.1309-1370 | DG Unit tests l.388; DG Test rules l.795-801 | |
| Helper modes | `--strata-test-helper=<mode>`: the test binary as a child process (about 50 modes: `record-arguments`, `console-output`, `run-with-environment`, `echo`, `exit-code`, `sleep`, `guarded-abort`, `broad-phase-churn`, `physics-settle`, `streaming-sweep`, `check-image`, `check-perf-log`, `check-icon`, `check-version`, `write-stress-project`, `write-stress-game`, `write-world-project`, `write-world-game`, `compare-documents`, `write-component-schema`...) | `TestMain.cpp` l.216-1260 (`RunHelperMode` from l.235); module registration helpers `StrataTests/src/Engine/ModuleRegistrationHelpers.cpp` | DG Test rules l.802-812 | |
| Fake CMake | `STRATA_TEST_FAKE_CMAKE=succeed|fail|fail-configure` makes the test binary stand in for CMake in script builds | `TestMain.cpp` l.1262-1307 | DG Test rules l.809-812 | |
| Crash naming | `TestCrashReporter.cpp`: a doctest listener remembers the running case; a fatal-signal handler prints it (doctest's POSIX signals disabled because `CrashGuard` owns them); `STRATA_TEST_TRACE=1` prints each case as it starts (CI sets it) | `StrataTests/src/TestCrashReporter.cpp` l.19-144; `StrataTests/CMakeLists.txt` l.164-168 | ci.yml l.204 | |
| Shards | `CoreShards.json`: `OwnTests` (8 CTests with their own suites), `FuzzSuites` (`*.Sweep`), `Shards` (13: Core, Asset, Scene, SceneTiming, Systems, Settling, LoaderFaults, Renderer, Network, Samples, EditorUI, EditorData, Editor); CMake makes `StrataTests.Core.<Shard>` with `--test-suite` / `--test-suite-exclude` (own tests' suites always excluded), label `core` | `StrataTests/CoreShards.json`; `StrataTests/CMakeLists.txt` l.205-255 | DG Shards, sweeps and locks l.402-417 | wave 4 (0.4.0) |
| `Testing.Shards` | checks every suite of the binary (`--list-test-suites` in a child) runs in exactly one shard/own CTest, no test case outside a `TEST_SUITE`, every `.Sweep` in `FuzzSuites`; unused filters only reported | `StrataTests/src/Testing/ShardTests.cpp` (278 lines) | DG l.413-416 | 0.4.0 |
| Sweeps and the fuzz run | `*.Sweep` suites test a deterministic sample (`Tests::SelectSweepOffsets`, `SelectSweepIterations`); `StrataTests.Fuzz` (Release, Dist, label `fuzz`) runs them with `STRATA_TEST_SWEEP=full` | `StrataTests/src/TestHelpers.h` l.181-199, `TestHelpers.cpp` l.700-750; `StrataTests/CMakeLists.txt` l.257-271; example `StrataTests/src/Asset/AssetPackTests.cpp` l.984-1031 | DG l.418-424 | 0.4.0 |
| Resource lock | label `package` tests hold `RESOURCE_LOCK toolchain`; perf tests `RUN_SERIAL` | `StrataTests/CMakeLists.txt` l.308-314, l.401, l.418, l.840 ... | DG l.425-429 | |
| CTest fixtures | setup/cleanup chains (`FIXTURES_SETUP/REQUIRED`): `StrataExport.Clean -> StrataEditor.Export -> StrataRuntime.*`, `StrataFeatureTest.Clean -> .Copy -> StrataEditor.FeatureTest -> StrataRuntime.FeatureTest`, `StrataPerfResults`, sample exports -> windowed checks -> `StrataTests.PerfGPU.Samples` | `StrataTests/CMakeLists.txt` l.420-1121 | SK "Run the tests" | |
| Labels | `core`, `fuzz`, `gpu`, `perf`, `package`, `feature`, `tools` (and unlabelled ones such as `StrataShaders.TargetHLSL`); CI runs `-LE "gpu|perf"` | `StrataTests/CMakeLists.txt` passim | AG Testing; DG Testing | |
| Expect-failure runner | `ExpectFailure.cmake`: exit code (1 or 3) and output regex | `StrataTests/ExpectFailure.cmake` | SK | |
| Run-and-expect runner | `RunAndExpect.cmake`: exit 0, output contains texts, paths exist, minimum duration | `StrataTests/Editor/RunAndExpect.cmake` | DG Feature test l.849 | |
| Command scripts | JSON lists of editor commands with `expect`, `until`, `bind`/`$ref`; `.json.in` configured with build paths | `StrataTests/Editor/*.json(.in)`, e.g. `SmokeCommands.json.in` (30 lines) | DG Deferred commands and command scripts (l.3176; editor area) | |
| Editor smoke and script checks | `StrataEditor.Smoke` (+`SmokeClean`, `SmokeCaptureCheck`), `QuitScreenshot`, `LauncherSmoke`, `FailingScript`, `WaitingScript`, `UnfinishedScript`, `CaptureWithoutGPU`, `ScreenshotWithoutGPU`, `QuitScript`, `QuitBeforeScriptEnds`, `Replay`, `Icon` | `StrataTests/CMakeLists.txt` l.420-525 | SK | |
| Export chain and runtime option tests | `StrataEditor.Export`, `StrataRuntime.Smoke/Identity/Icon/GameIcon/VersionInfo/HeadlessPacing/AssetBudget/InvalidAssetBudget/InvalidFrames.*/InvalidSeconds.*/InvalidScreenshot/Seconds/PerfLog(+Check)/InvalidPerfLog/InvalidSaveDirectory/World*/Render(+Check)/Resolution(+Check)/InvalidResolution/InvalidQuality.*/QualityHeadless/Quality/PerfLogWindowed(+Check)/NoCameraScreenshot`, `Arguments.Help/Unknown` | `StrataTests/CMakeLists.txt` l.573-772 | SK | |
| End-to-end suites | `EndToEnd.StandardStreams`, `EndToEnd.EditorAutomation`, `EndToEnd.Recovery`: start built editor/CLI/runtime (`STRATA_TEST_EDITOR_PATH` etc.), `--no-gpu`, private sessions, free ports, kill on failure; run as `StrataEditor.Automation` | `StrataTests/src/Editor/StandardStreamsProcessTests.cpp`, `EditorAutomationProcessTests.cpp`; `StrataTests/CMakeLists.txt` l.522 | DG End-to-end tests l.775 | |
| GPU test context | `Tests::GPUContext`: one headless device per process (validation unless `STRATA_TEST_GPU_VALIDATION=0`), `GetNewErrorCount`, `ExecuteAndWait` (recycles command buffers), `ShutdownShared` | `StrataTests/src/Renderer/GPUTestUtils.h` l.21-48; `GPUTestUtils.cpp` l.17-127 | DG GPU tests l.433-441 | |
| GPU test helpers | `ExactSpecification()`, `AddNeutralPostProcess`, `GetDrawnCounts`, `ReadBufferRange`, `ReadMeshGeometry`, flicker meter (`Renderer/FlickerMetrics.h`), `MeasureNoise`; GI scenes | `StrataTests/src/Renderer/*TestUtils.h`, `FlickerMetrics.h`, `GIScenes.h` | DG GPU tests l.447-464 (rendering area owns details) | |
| General test helpers | `CreateTemporaryDirectory`, `CopySampleProject`, `CopySamples`, `LogCapture`, `DescribeJsonFile`, `WaitUntil`, `CountLogMessages`, `ScopedLogLevel`, `CreateSineWav`, `EncodePNG`, `ScopedEnvironmentVariable`, `FreshPages`, Windows `RunInConsole`, icon/version readers | `StrataTests/src/TestHelpers.h` (224 lines), `TestHelpers.cpp` | DG Test rules l.784-812 | |
| Editor test helpers | `Tests::RunCommandToCompletion`, `ImGuiHarness` | `StrataTests/src/Editor/CommandTestUtils.h`, `ImGuiHarness.h` | DG Unit tests l.391-398 (editor area) | |
| Scene cache checks in tests | `CheckSceneCaches`; Debug asserts after every update for small scenes | `StrataTests/src/Scene/SceneTestUtils.h` | DG Test rules l.791-794; SK | |

### 1.7 The perf lab

| Feature | What it is | Where | Documented | Arrived |
| --- | --- | --- | --- | --- |
| Perf suites | `Perf.*` (CPU) -> `StrataTests.Perf`; `PerfGPU.*` -> `StrataTests.PerfGPU` (also `gpu`, `STRATA_TEST_GPU_VALIDATION=0`); `PerfGPU.Samples*` -> `StrataTests.PerfGPU.Samples` after sample exports; Release/Dist only, `RUN_SERIAL`, after `StrataTests.PerfResults.Clean` | `StrataTests/CMakeLists.txt` l.273-306, l.1043-1048 | DG Perf tests l.468-472 | wave 1 |
| Measurement | `Perf::Measure(name, warmup, iterations, fn)` -> median, p95 (nearest rank), min, max; `Summarize` | `StrataTests/src/Perf/PerfUtils.h` l.23-86; `PerfUtils.cpp` l.104-146 | DG l.474-475 | |
| Budget file | `StrataTests/Perf/Budgets.json` (about 248 entries, 73 provisional): `Measured`, `Budget` <= 1.5 x Measured, `Unit` in ms/us/MB/count/ratio, optional `Target`, or `Provisional: true`; parser enforces rules | `StrataTests/Perf/Budgets.json` l.2-24 (format), `PerfUtils.cpp` `ParseBudgets` | DG l.489-497 | |
| Confirmed checks | `CheckBudgetConfirmed` / `CheckBudgetsConfirmed`: re-measure up to `c_ConfirmationAttempts` (3), fail only when every attempt over budget; provisional metrics never fail | `PerfUtils.h` l.60-159; `PerfUtils.cpp` l.291-370 | DG l.476-481 | |
| Results file | `build/<preset>/PerfResults/<config>.json`: per metric value, unit, budget/provisional, target, attempts, sorted keys, nothing run-specific (diffable) | `PerfUtils.h` l.161-176; `PerfUtils.cpp` `MergeResults` | DG l.482-486 | |
| Canary | `Perf.Harness.Sort200k`: xorshift32 input, median of 31 sorts; shows a throttled/oversubscribed machine | `StrataTests/src/Perf/PerfHarnessTests.cpp` l.28-33, l.512-541 | DG l.533-537 | |
| Lab self-tests | suite `PerfLab` (in Core shard, every config) and `Perf.Harness` | `PerfHarnessTests.cpp` l.95-541; `PerfGPUHarnessTests.cpp` | DG l.472 | |
| Scene generators and fixtures | `Perf/SceneGenerators.h`, `Perf/StressProject.h`, `Perf/WorldFixture.h` (deterministic worlds 250k/1M), `ScopedApplicationJobSystem` | `StrataTests/src/Perf/` | DG l.552-612 | |
| Peak-memory helpers | measured work in a helper process (`ImportMemoryMeasurement`, `LocalShadowsMemory`, `WorldGameMeasurement`, `streaming-sweep`) | `StrataTests/src/Perf/*Measurement*`, `TestMain.cpp` | DG l.613-618 | |
| GPU timing in perf | `Perf/RendererPerfUtils.h`: `MeasureFrames`, `MeasureGPU`, `MeasuresGPU` | `StrataTests/src/Perf/RendererPerfUtils.h` | SK | |
| Medium preset rule | perf tests measure Medium unless the metric names a preset | (convention) | DG l.662-664 | 0.7.0 |
| Perf suites inventory | `Perf.Scene`, `.Runtime`, `.Scripting`, `.Physics`, `.TextureCook`, `.Animation`, `.Jobs`, `.FrameProfiler`, `.FramePacer`, `.World*`, `.Editor`, `.EditorPanels`, `PerfGPU.Renderer`, `.Editor`, `.Streaming`, `.Pack`, `.Samples` | `StrataTests/src/Perf/*.cpp`, `StrataTests/src/Editor/*Perf*` | DG l.552-661 (each area's book chapter should own its numbers) | waves 1-8 |
| Ratchet and re-baselining | budgets only go down; up only for a machine change shown by an interleaved A/B against the commit that set it, or once for an owner-accepted cost | `Budgets.json` comment l.14-19 | AG Testing; DG l.497-510 | |
| `Tools/PerfStability.py` | runs `ctest -L perf` N times; per-run machine load, canary ratio, confirmations; per-metric min/median/max, pass rate; `--wait-quiet`, `--results`, `--propose-budgets` (+`--rebaseline`), `--baseline/--max-ratio/--slack` A/B | `Tools/PerfStability.py` (531 lines; `classify` l.348-391, `propose_budgets` l.393-447, `compare_baseline` l.449) | DG l.520-546 | wave 1-4 |
| `Tools/PerfLock.py` | runs a command under an OS file lock in the user temp dir (fcntl/msvcrt), process group killed at the limit; exit 75 not acquired, 124 timed out; `--status` | `Tools/PerfLock.py` (179 lines) | DG Repository layout l.138; DG l.502, l.758 | wave 4 step 0 |

### 1.8 The feature test (golden rule 6)

| Feature | What it is | Where | Documented |
| --- | --- | --- | --- |
| Feature project | real project `StrataTests/FeatureTest/` (`FeatureTest.stproj`, `Assets/` of every asset type with committed `.meta`, `Scripts/` module of 22 feature script files); tiny binary assets from `StrataTests/FeatureTest/Tools/GenerateAssets.py` | `StrataTests/FeatureTest/` | DG Feature test l.814-881 |
| Coverage checks | every registered component present with every property non-default on some entity; every settings section non-default; every script field type overridden; every callback called (journal); every host function called (`GetScriptHostCallCounts`); every public SDK name used (`SDKReader`); no unexpected warnings (`c_ExpectedLogMessages`); assets import without warnings and `.meta` untouched | `StrataTests/src/FeatureTest/FeatureTests.cpp` (l.60-229), `SDKCoverageTests.cpp` (l.265-406), `SDKReader.h/.cpp`, `FeatureTestUtils.h/.cpp` | DG l.853-874 |
| Runners | `StrataTests.FeatureTest` (headless, in-process editor, exported game in `GameRuntime`; 200 frames, hot reload halfway, cache validation every frame), `GPU.FeatureTest`, `StrataEditor.FeatureTest` and `StrataRuntime.FeatureTest` (real executables on a copy), `StrataRuntime.FeatureTestQuality`, `StrataEditor.InputSequence(Windowed)` | `StrataTests/CMakeLists.txt` l.316-321, l.774-818, l.1095-1121; `src/FeatureTest/GPUFeatureTests.cpp` | DG l.832-852 |
| Script side | `FeatureTest::FeatureScript` (`Expect`, `Checks`, `Failure`, `Completed`), `Journal()` | `StrataTests/FeatureTest/Scripts/FeatureScript.h` l.1-92 | DG l.829-831 |

### 1.9 Package, install and sample tests

| Feature | What it is | Where | Documented |
| --- | --- | --- | --- |
| Script-SDK package tests | `StrataScriptCore.Package` and `.PackageDist` build `StrataTests/PackageProject` through the installed-style package with the engine's generator, check glm definitions match, load the module | `StrataTests/PackageProject/`, `BuildPackageProject.cmake`; `StrataTests/CMakeLists.txt` l.385-418 | DG Script modules and package tests l.885-889 |
| `StrataTests.Package` | doctest suites `Package*` (e.g. `Package.ScriptBuild`) | `StrataTests/CMakeLists.txt` l.308-314 | DG l.889-891 |
| `StrataEditor.Scripts` | real editor creates, builds, attaches, plays, exports a scripted game | `StrataTests/Editor/ScriptsEndToEnd.cmake`; CMakeLists l.832-840 | DG l.891-892 |
| Sample tests | `StrataEditor.Tetris/.PhysicsPlayground/.OpenWorld/.ThirdPerson/.Showcase` via one runner: copy sample, run `<Sample>Commands.json.in`, export full and pruned, run games headless, `ALLOWED_MESSAGES` whitelist; windowed `gpu` checks on the exports; `StrataEditor.OpenWorldRender`, `ShowcaseRender` | `StrataTests/Editor/SampleProject.cmake` (170 lines); CMakeLists l.860-1092 | DG l.892-911; AG Testing (last bullet) |
| Install test | `StrataEditor.Install`: `cmake --install` into a fresh prefix, exact top-level layout, `StrataInstall.json` version, PE subsystems, `--version`, create project from `basic3d`, build script with the installed SDK (`STRATA_ENGINE_DIR` must be the installation), play, export, run the game | `StrataTests/Editor/InstallEndToEnd.cmake` (221 lines; layout l.52-59) | DG l.912-917; DG Packages l.351 |
| Package version test | `StrataPackaging.Version` (script mode) | `StrataTests/Packaging/PackageVersionTests.cmake` | |
| Slang fetch test | `StrataSlang.Fetch`: fake archive over `file://` into a private cache: digest, cache hits, error texts, per-user folders, host key | `StrataTests/Shaders/SlangFetchTests.cmake` (167 lines); CMakeLists l.341-345 | DG Shaders item 6 |
| HLSL target check | `StrataShaders.TargetHLSL`: `slangc -target hlsl` over `ShaderEntries.txt`, no label so every CI test job runs it | `StrataTests/Shaders/TargetHLSL.cmake`; CMakeLists l.347-355 | DG Shaders items 6, 8 |
| Tools tests | `StrataTools.LookDevOffline` (`tools`), `StrataTools.LookDev` (`gpu;tools`), `StrataTools.ShowcaseTerrain`, `StrataTools.ShowcaseProps` (committed outputs equal regenerated); `PythonMissing.cmake` stand-in when Python 3.10+ is absent | CMakeLists l.357-370, l.526-570; `StrataTests/Tools/PythonMissing.cmake` | DG Look-dev harness l.761-768 |

### 1.10 Architecture and documentation checks that run as tests

(Owned in depth by the architecture chapter; listed because the build area enforces them.)

| Suite | What it guards | Where |
| --- | --- | --- |
| `Architecture.Layering` | includes follow `Layers.json`; allowlist stale lines fail; `ExternalOwners` | `StrataTests/src/Architecture/LayeringTests.cpp`, `LayeringAnalyzer.h/.cpp` |
| `Architecture.Libraries` | `LayerLibraries.json` links equal MayInclude | `LibrariesTests.cpp` |
| `Architecture.PrecompiledHeaders` | pch holds only std, vendor, Core basics | `PrecompiledHeaderTests.cpp` |
| `Architecture.HeaderWeight` | headers include `json.hpp` only when needed; no `std::span` of declared-only JSON; `EditorContext.h` forward-declares | `HeaderWeightTests.cpp` |
| `Architecture.ScriptSDK` | no engine/editor/tool/test TU includes the SDK's C++ headers | `ScriptSDKTests.cpp` |
| `Architecture.Shaders` | derivatives before discard; Slang only; HLSL syntax | `ShaderSourceTests.cpp` |
| `Docs.AgentGuide` | AGENTS.md under 40,000 characters (code points); links resolve to files and GitHub-style anchors | `StrataTests/src/Docs/AgentGuideTests.cpp` l.402-490 |

### 1.11 CI

| Feature | What it is | Where | Documented | Arrived |
| --- | --- | --- | --- | --- |
| Triggers | push to `main` and `ci/**`, pull requests; concurrency group per ref, cancel in progress | `.github/workflows/ci.yml` l.1-11 | AG Building "CI before main"; DG Building l.199 | |
| Matrix | Windows Release and Debug (`windows-ninja`, sccache), Linux Release (GCC 14, ccache), macOS Release (`macos-15`, Apple Clang 17, ccache), "Linux (no Audio, no Physics, no GLFW)" (`-DSTRATA_BUILD_EDITOR=OFF`, excludes `package`) | `ci.yml` l.19-60 | DG Building l.199-204; DG Optional modules l.285 | Windows Debug + cache: wave 4 |
| Dev environment import | vswhere + `vcvars64.bat` diffed into `GITHUB_ENV` | `ci.yml` l.95-113 | | |
| Compiler cache in Actions | restore by prefix, save even on test failure, size caps (250M ccache, 1G sccache), delete superseded entries of the ref with `gh cache` so main's set survives GitHub's 10 GB LRU | `ci.yml` l.115-193 | DG Building l.202-206 | 0.4.0 |
| Build with keep-going | `-- -k 0` so one run reports every compile error | `ci.yml` l.135-141 | | |
| Shader checks | Linux: `spirv-val --target-env vulkan1.2` over the final modules (`.github/scripts/validate_shaders.sh`); macOS: MoltenVK converter + Apple Metal compiler (`.github/scripts/convert_shaders_to_metal.sh`, `c_KnownFailures` only shrinks, lines read `known failure:`) | `ci.yml` l.143-160; `.github/scripts/*.sh` | DG Shaders item 6 | wave 8 |
| Test step | `ctest -LE "gpu|perf" -j 4 --timeout 900`, `STRATA_TEST_TRACE=1`, Linux `ulimit -v/-f` so a runaway test fails alone; runs even after a failed shader step | `ci.yml` l.195-215 | DG Building l.208-212 | |
| Failure annotations | `.github/scripts/annotate_failures.py`: GCC/Clang/MSVC/doctest/slangc error patterns -> GitHub annotations (logs need admin rights; annotations are public) | `.github/scripts/annotate_failures.py` (184 lines); `ci.yml` l.217-224 | | |
| Windows Dist job | Visual Studio generator (as people build), no cache, Dist build of every target, `ctest -L package` | `ci.yml` l.226-266 | DG Building l.206-208 | wave 4 step 0 (after a wave-3 Dist break) |
| `Tools/CIStatus.py` | reads a commit's runs, jobs and annotations through the GitHub API (token from env or `gh`, never printed); exit 3 while running | `Tools/CIStatus.py` (130 lines) | DG Repository layout l.138 | wave 4 step 0 |
| `Tools/CompatLint.py` | compiles changed TUs with GCC 14 and LLVM 16 (libc++) using the Debug build's exact commands without the pch, warnings as errors, before a push | `Tools/CompatLint.py` (166 lines; `adapt` l.64-94) | AG Building "CI before main"; DG Building l.216-218, Precompiled headers l.237 | wave 4 step 0 |

### 1.12 Packaging and releases

| Feature | What it is | Where | Documented | Arrived |
| --- | --- | --- | --- | --- |
| Install rules | only when editor, runtime and CLI are built: executables at top, `StrataInstall.json` marker, `README.md` (from `Docs/Releases/PackageReadme.md`), `ThirdPartyNotices.md`, `Samples/` without `.strata`, `StrataScriptCore/` (CMake, Include, Source, glm headers + license), `Docs/Manual/`, `Skills/<three skills>/SKILL.md` | `CMake/StrataPackaging.cmake` l.1-86 | DG Packages l.339-351; AG Building "Packages and releases" | 0.3.0 |
| Installation marker | `StrataInstall.json` (`Format: Installation`, `EngineVersion`) makes the editor build scripts against the installation's SDK | `StrataPackaging.cmake` l.57-62 | DG Packages; Scripting "Building and loading scripts" | |
| CPack | ZIP on Windows, TGZ elsewhere, `Strata-<version>-<windows-x64|linux-x64|macos-arm64>`, top-level directory, Linux stripped | `StrataPackaging.cmake` l.87-107 | DG Packages | |
| Package version | `STRATA_PACKAGE_VERSION` empty = project version, else project version + pre-release suffix; anything else fails configure | `CMake/StrataPackageVersion.cmake` l.7-24; `StrataPackaging.cmake` l.24-30 | DG Packages | |
| Release workflow | tag `vX.Y.Z` publishes, `vX.Y.Z-<suffix>` dry run, manual dispatch; checks tag == `project(Strata VERSION)` and `Docs/Releases/X.Y.Z.md` exists; builds Dist on three OSes, `ctest -LE "gpu|perf"` in Dist, `cpack`, unpacks into a fresh folder, checks files and `--version`, SHA-256 per archive, uploads artifacts; publish job (only one with `contents: write`) makes `SHA256SUMS.txt`, verifies, `gh release create --verify-tag` | `.github/workflows/release.yml` (281 lines; version l.29-93, build l.95-242, publish l.244-281) | DG Releases l.353-372 | 0.3.0 |
| Release notes | `Docs/Releases/0.3.0.md ... 0.7.0.md`, `PackageReadme.md` | `Docs/Releases/` | DG Releases item 2 | |
| Release procedure | bump version, write notes, local `ctest --preset <p>-dist -LE "gpu|perf"`, `-rc1` dry run, real tag; one release per wave | (process) | DG Releases; AG Building | |
| Dist-only expectations | `#if defined(ST_DIST)` in tests whose expectations differ | (convention) | AG Testing; DG Releases item 3 | |

### 1.13 Tools/ (every tool)

| Tool | Kind | What it does | Checked by | Documented |
| --- | --- | --- | --- | --- |
| `Tools/CIStatus.py` | CI helper | commit CI status and annotations | none | DG l.138 |
| `Tools/CompatLint.py` | CI helper / lint | GCC 14 + LLVM 16 compile without pch | none | AG, DG l.216 |
| `Tools/PerfLock.py` | perf | machine-wide measurement lock | none | DG l.138, l.502 |
| `Tools/PerfStability.py` | perf | repeat perf runs, propose budgets, A/B | none | DG l.520-546 |
| `Tools/PhysicsSweep.py` | perf/tuning | sweeps physics tuning over settle scenes and the Physics Playground | none | DG "Settling and the sweep" l.2409 (physics area) |
| `Tools/LookDev.py` (+ `Tools/LookDev/LookDevScene.json`, `Shots.json`) | image regression | capture fixed shots through headless editors, compare two sets, ratio of GPU stages, selftest | `StrataTools.LookDev`, `StrataTools.LookDevOffline` | DG Look-dev harness l.666-773 |
| `Tools/GenerateBlueNoise.py` | committed generator | void-and-cluster 64x64 blue noise -> `Renderer/BlueNoise.h`; `--check` | (`--check` manual) | DG l.138 (rendering area) |
| `Tools/FitFilmic.py` | committed fit | Filmic tone curve gamut matrices -> `FilmicConstants.slang/.h`; `--check`, `--rewrite` | manual | DG Post-processing (rendering area) |
| `Tools/FitAOMultiBounce.py` | committed fit | AO multi-bounce fit against 2D radiosity reference | manual | DG Ambient occlusion (rendering area) |
| `Tools/GenerateAreaTable.py` | committed generator | MLAA area table `Renderer/MorphologicalAreaTable.inl` | manual | DG Post-processing |
| `Tools/GenerateWhiteBalance.py` | committed generator | white locus `Renderer/WhiteBalanceLocus.inl` | manual | DG Post-processing |
| `Tools/GenerateBrandAssets.py` | committed generator | strata mark PNG/RGBA/ICO by signed distances | manual | DG l.134 |
| `Tools/GenerateIslandTerrain.py` | sample content | Open World island terrain and scatter command script | manual | DG Samples |
| `Tools/GenerateShowcaseTerrain.py` | sample content | Showcase ground, layout, stations, shot checks (`checkshots`) | `StrataTools.ShowcaseTerrain` | DG "The showcase" l.6493; AG Asset pipeline |
| `Tools/GenerateShowcaseProps.py` | sample content | Showcase props, steel maps, material/prefab command scripts | `StrataTools.ShowcaseProps` | DG "The showcase" |
| `StrataTests/FeatureTest/Tools/GenerateAssets.py` | committed generator (test) | feature project's tiny assets | (none; outputs committed) | DG Feature test l.828 (which names it `Tools/GenerateAssets.py`) |
| `StrataEditor/Tools/GenerateIconHeader.py` | committed generator | Lucide `UI/Icons.h` | none | DG l.6435 (editor area) |
| `.github/scripts/annotate_failures.py`, `validate_shaders.sh`, `convert_shaders_to_metal.sh` | CI scripts | see 1.11 | CI | DG Shaders item 6 |

All Python tools are standard-library only and are run with `python -I` where the docs say so (isolated mode).

### 1.14 Review and commit process

| Feature | What it is | Where |
| --- | --- | --- |
| Golden rules 2, 3, 5, 6 | everything ships with tests, review before commit, no hacks, keep feature test current | AG l.17-31 |
| Pre-commit review checklist | 6 items: correctness, tests, style, portability, documentation (AGENTS.md under 40,000 chars, rule stated in full in DG), commit hygiene | AG l.457-473 |
| Verify in a clean worktree | apply the staged patch to `.worktrees/verify`, build and test Debug and Release | SK "Verify a commit in a clean worktree" |
| Debugging a crashing test | temporary `fprintf(stderr)` checkpoints | SK "Debugging a crash in a test" |
| Validation layer setup | `VK_ADD_LAYER_PATH`; macOS manifest copy with full library path | DG Building l.164-170; SK |

### How completeness was checked

- Every file of `CMake/` (12 files + `StrataShaderTool/` 3 files) read and listed; every `function()` in them (25,
  `grep -n "^function"`) is accounted for in 1.1-1.4 and 1.12.
- `CMakeLists.txt` and `CMakePresets.json` read whole; every `option()` (17 in the root and compiler options) listed.
- `Strata/vendor/CMakeLists.txt` read whole; all 19 `.gitmodules` paths listed; `ThirdPartyNotices.md` read.
- Both workflows and the three `.github/scripts` read (the Python annotator's header and patterns only).
- `Tools/`: all 15 `.py` files and `Tools/LookDev/` listed from their docstrings; also the two generators outside `Tools/`.
- `StrataTests/CMakeLists.txt`: every `add_test` (about 88 calls, some in loops) grepped with labels and fixtures; the
  structural ones are named above, the per-sample/per-option variants are grouped.
- `StrataTests/` top level: every folder accounted for (Architecture, Editor, FeatureTest, PackageProject, Packaging,
  Perf, Scripts, Shaders, TestLibrary, Tools, src); `src/` infrastructure files (TestMain, TestHelpers, TestCrashReporter,
  StubWindow, TestsPch, Testing/, Perf/, FeatureTest/, Architecture/, Docs/) listed. The 491 `TEST_SUITE` declarations
  of the module tests were not enumerated (out of scope: "not every test").

---

## 2. Concepts to teach (dependency order)

1. **From source files to a program: compiling and linking.**
   Problem: C++ is compiled per translation unit, then linked. Approaches: a hand-written makefile, IDE projects, a
   meta-build system generating native projects (CMake, Premake, GN, Bazel, Meson). Strata uses CMake 3.25+ generating
   Visual Studio or Ninja Multi-Config projects. Newcomer mistakes: thinking a header "is compiled"; confusing compile
   errors with link errors (`undefined reference`); not knowing that the order of static libraries matters on GNU ld
   (Strata's comment at `Strata/vendor/CMakeLists.txt` l.47-49).
2. **Meta-build: configure vs build vs test steps.** CMake's configure step reads `CMakeLists.txt`, the cache
   (`CMakeCache.txt`), generators; the build step runs the native tool; CTest runs tests. Strata adds presets so the
   three steps are one name each. Mistake: cached options survive re-configures (SK: "Cached options survive a
   re-configure"); forgetting to re-configure after adding files because of `GLOB_RECURSE CONFIGURE_DEPENDS` (DG
   Building l.187: the VS generator re-globs during the build but compiles with the stale project).
3. **Targets and usage requirements.** Static, shared, module, interface libraries; PUBLIC/PRIVATE/INTERFACE
   propagation; `SYSTEM` includes; `EXCLUDE_FROM_ALL`. Strata: one static library per architectural layer, linking only
   what the layer table allows; `Strata` and `StrataTooling` interface libraries as "what a game links" and "what tools
   link". Mistake: linking a library PUBLIC when it should be PRIVATE leaks headers to dependents (ARCH l.136-140).
4. **Build configurations and preprocessor-driven builds.** Debug/Release/Dist (Hazel convention), what assertions
   compile to, why shipping builds differ (`ST_DIST`). Engines typically have Debug, Development/Release, Shipping
   (Unreal), Profile. Strata's Dist = Release flags plus a define. Mistake: testing only Debug and shipping Dist; a
   wave-3 change broke Dist unnoticed, hence the CI Dist job (ci.yml l.226-229).
5. **Compiler warnings as a policy.** /W4, -Wall -Wextra, warnings as errors in first-party code, silenced vendor
   code. Mistake: silencing a warning locally instead of fixing it (AG golden rule 5; SK).
6. **Portability across compilers and standard libraries.** MSVC, GCC, Clang, libstdc++, libc++; what "works on my
   machine" hides (missing includes, `size_t` vs `uint64_t` on macOS, no floating-point `std::from_chars` in old libc++,
   a real Apple Clang miscompile: DG Building l.213-221). Strata's answers: CI on three OSes, `ci/<name>` branches,
   `CompatLint.py`. Mistake: assuming the newest local compiler represents CI.
7. **Compile time engineering.** Precompiled headers, forward declarations, header weight, compiler caches
   (ccache/sccache), unity builds (not used). Strata: per-target pch with only std/vendor/Core basics; headers that only
   declare JSON include `json_fwd.hpp`; `Scope<>` with out-of-line destructor for forward-declared members; cache in CI.
   Trade-off: pch hide missing includes, so a pch-off lint exists; MSVC pch are not cacheable so cache turns pch off.
   Measured payoff in RM l.381-385 (wave 4). Mistake: putting a frequently edited engine header into the pch.
8. **CPU instruction sets and floating-point determinism.** SSE/AVX/FMA flags, why `-mfma` changes results
   (contraction), why box3d compiles with `-ffp-contract=off` for cross-platform determinism. Strata keeps one
   code-generation option set for every engine object (`StrataEngineCodegen`) so leaving a module out changes nothing
   else. Mistake: thinking optimization flags never change numeric results.
9. **Third-party dependencies.** Approaches: vendoring copies, git submodules, package managers (vcpkg, Conan),
   FetchContent, system packages. Strata: pinned shallow submodules wrapped by one CMake file, licenses tracked in
   `ThirdPartyNotices.md`, "shipped in games" column; one tool (Slang) fetched as a pinned, hashed archive instead.
   Licenses: permissive vs copyleft and why an engine cares (games ship the notices). Mistake: copying code without its
   notice; upgrading a library together with other changes.
10. **Reproducible, verified downloads.** Pinning by SHA-256, per-user caches, file locks for concurrent configures,
    atomic rename, offline overrides. Strata's `strata_slang_fetch`. Mistake: "updating the digest to match" a changed
    download (the error text at `StrataSlang.cmake` l.203 forbids it).
11. **Code generation in the build.** Embedding binary data (fonts) as arrays, generating version headers that change
    only when the content changes, compiling shaders to SPIR-V at build time, generated registries. Approaches for
    shaders: runtime compilation, offline compiled blobs loaded from files, compiled blobs embedded into the binary.
    Strata embeds everything so a game is one executable plus its pack; bytes are configuration-independent. Mistake:
    regenerating a header every build, so everything recompiles every build (Strata writes with `file(CONFIGURE)`,
    unchanged content keeps the timestamp).
12. **Architecture enforced by the build.** Layering (lower layers never include higher ones), why it matters at scale,
    how to enforce: conventions, include checkers, separate libraries, link-closure checks, linker-map checks. Strata uses
    all of them: the layer table is the build; games are proven to contain no tooling, twice. Mistake: widening an
    allowlist instead of inverting the dependency (AG Architecture rules, "Layers").
13. **Optional modules and feature flags.** Compile-time module exclusion vs runtime plugins. Strata: CMake options,
    `ST_WITH_*` as definitions (not header macros), guards only in the composition root/asset pipeline/runtime/tests,
    unknown components preserved. Mistake: `#if ST_WITH_X` sprinkled in modules; a macro defined in a header that a file
    forgot to include silently reads as 0.
14. **What a test is; unit vs integration vs end-to-end; test frameworks.** doctest's TEST_SUITE/TEST_CASE, CHECK vs
    REQUIRE, filters, `expected_failures`. Strata's rules: every change ships with tests, regression tests must fail
    without the fix. Mistake: weakening or skipping a test to get green (golden rule 2).
15. **Test organisation at scale: test runners, CTest, labels, sharding, fixtures, resource locks.** One big binary vs
    many; running in parallel; splitting by suite name; keeping a shard under a minute; labels as machine capability
    (`gpu`, `package`, `tools`) and cost (`perf`, `fuzz`). Strata's `CoreShards.json` plus a test that every suite runs
    exactly once. Mistake: a new suite prefix that matches no shard and silently never runs (which is exactly what
    `Testing.Shards` catches), or a TEST_CASE outside any TEST_SUITE.
16. **Determinism and flakiness.** Wait on conditions or the clock, never frames; private temp dirs, free ports, private
    sessions; no environment changes for children; the slowest CI machine (3 hardware threads) as the yardstick.
    Strata's `Tests::WaitUntil`, `ScopedJobSystem`, `run-with-environment` helper. Mistake: `sleep(100)` then assert, or
    counting frames.
17. **The test binary as its own helper process.** Testing process spawning, crashes, consoles, exit codes without
    external programs: `--strata-test-helper=<mode>`, the fake CMake, the fake editor. Mistake: depending on `cat`,
    `python` or a real CMake in a unit test.
18. **Crash containment vs test frameworks.** Signal handlers are process-global; doctest's would remove the script
    crash guard's, so Strata disables them and names a crashing test itself (`TestCrashReporter.cpp`). Teaches why
    "the framework does it" can conflict with the engine.
19. **Fuzzing and corruption sweeps.** Exhaustive byte-offset sweeps vs sampled ones; deterministic seeds so failures
    repeat; full sweeps in optimized nightly-like runs. Strata: `SelectSweepOffsets` (headers + block boundaries +
    512 seeded offsets), full in `StrataTests.Fuzz`. Mistake: random seeds that change per run.
20. **GPU testing.** Headless devices, one shared device per process (VkInstance churn crashed drivers: DG GPU tests;
    memory note), validation layer errors as test failures, readback of pixels, exact-pixel vs tolerant tests, GPU work
    whose results arrive frames later. Mistake: creating a device per test; forgetting `CHECK(gpu.GetNewErrorCount() == 0)`.
21. **Performance testing and noise.** Benchmarks vs gates; warm-up; median vs mean vs percentiles; noise only adds;
    confirmation by re-measuring; reference machines; budgets with headroom; ratchets; provisional metrics; canaries;
    interleaved A/B; layout effects (48 bytes of code moved CPU medians by +-7%: DG l.526-530); hybrid CPU scheduling
    (P/E cores). Mistake: raising a budget to pass; trusting one run; measuring on a busy machine; perf numbers from a
    Debug build (`IsOptimizedBuild`).
22. **Coverage by construction (the feature test).** Instead of line coverage, a project that must contain every
    registered thing with non-default values; the registries make "every" enumerable. Mistake: adding a component or
    host function without extending the project (the run fails).
23. **Image regression testing.** Golden images vs before/after comparisons with signed differences, deterministic
    repeats, crops, GPU timings beside pictures (`Tools/LookDev.py`). Mistake: reading a numeric diff without looking
    at the signed image.
24. **Continuous integration.** Matrix builds, caches and their eviction, keep-going builds, logs vs annotations,
    resource limits on runners, which tests a hosted runner can run (no GPU, no reference machine). Strata's `ci/<name>`
    gate before main. Mistake: merging a large integration without green CI on the oldest compilers.
25. **Packaging, installation and releases.** Install trees, relocatable installs and markers, archives (CPack),
    versioning with pre-release suffixes, dry runs, checksums, verifying the artifact as a user gets it (unpack, run
    `--version`), release notes, one publishing job with write permission. Mistake: testing the build tree instead of
    the installed layout (so `StrataEditor.Install` exists); forgetting an install rule for a new shipped file.
26. **Process discipline: review checklist, commit hygiene, clean-worktree verification.** Mistake: committing what
    the working tree compiles, not what is staged.

---

## 3. Code worth showing

| # | File and lines | What it teaches | Reader must know first |
| --- | --- | --- | --- |
| 1 | `CMakeLists.txt` l.1-91 | A whole top-level CMake file: project, guards with fix-it messages, options, the editor-needs-every-module rule, subdirectories, the deferred link-closure check, packaging, tests | Concepts 1-3 |
| 2 | `CMakePresets.json` l.1-89 | Configure/build/test presets; inheritance; host conditions | CMake basics |
| 3 | `CMake/StrataConfigurations.cmake` l.1-56 | Three configurations; Dist reusing Release flags; static MSVC runtime; debug-info format for caches | Concept 4 |
| 4 | `CMake/StrataCompilerOptions.cmake` l.95-120 (`strata_configure_target`) | Per-target warning policy and configuration defines via generator expressions | Targets, generator expressions |
| 5 | `CMake/StrataCompilerOptions.cmake` l.44-93 (`strata_engine_cpu_options`) | Instruction-set flags per compiler, FMA and determinism | Concept 8 |
| 6 | `Strata/vendor/CMakeLists.txt` l.144-182 | Building a library from sources instead of its CMake, with a reason per flag (determinism, AVX2 kernel, asserts, a raised limit) | Concepts 8-9 |
| 7 | `Strata/vendor/CMakeLists.txt` l.184-227 | Splitting a dependency so shipped games get only the decoder | Concept 12 |
| 8 | `CMake/StrataLayers.cmake` l.155-186 | Every file in exactly one layer: the central ownership algorithm (small, readable) | Concept 12, regex |
| 9 | `CMake/StrataLayers.cmake` l.367-429 | Transitive link-closure walk with path reporting, deferred to the end of configure | Targets, recursion |
| 10 | `StrataTests/Architecture/CheckNoTooling.cmake` l.47-107 | Proving absence from a linker map, and requiring presence first so an unreadable map proves nothing | Linkers, map files |
| 11 | `CMake/StrataShaders.cmake` l.64-86 and l.170-191 | slangc flags each with a reason; two custom commands per shader; the manifest line | Shaders exist (rendering chapter); custom commands |
| 12 | `CMake/StrataShaders.cmake` l.202-221 | A generated registry source | 11 |
| 13 | `CMake/StrataShaderTool/SpirvModule.cpp` l.27-65 (`ParseSpirv`) | Parsing a binary format defensively: magic number, header, word counts | Binary formats, `std::span` |
| 14 | `CMake/StrataShaderTool/SpirvModule.cpp` l.101-166 (`DecoratePositionInvariant`) | Patching a binary module: collect insertions first, insert from the back | 13; why invariance matters (depth prepass EQUAL) |
| 15 | `CMake/StrataShaderTool/StrataShaderTool.cpp` l.83-116 (`WriteFileAtomically`) | Write-to-temp-then-rename so failed builds leave no "current" output | Files |
| 16 | `CMake/StrataSlang.cmake` l.128-251 (`strata_slang_fetch`) | The central reproducible-download algorithm: stamp fast path, lock, re-check after lock, retries, digest, child extraction, stamp, atomic rename; never fails the configure itself | Concept 10 |
| 17 | `CMake/StrataVersionCommit.cmake` l.1-24 and `Strata/CMakeLists.txt` l.31-42 | A header that changes only when the commit changes | Build-time vs configure-time |
| 18 | `CMake/StrataEmbeddedFiles.cmake` l.8-46 | Embedding a file as a byte array with regex | |
| 19 | `StrataTests/CoreShards.json` (36 lines) and `StrataTests/CMakeLists.txt` l.209-255 | Data-driven test sharding | CTest, doctest filters |
| 20 | `StrataTests/src/Testing/ShardTests.cpp` l.26-58 (`MatchesFilter`) and l.118-153 (`CheckShards`), l.244-277 | Wildcard matching with backtracking; the "exactly once" check; asking the binary for its own suites in a child process | 19 |
| 21 | `StrataTests/src/TestHelpers.cpp` l.700-737 (`SelectSweepOffsets`) and `Asset/AssetPackTests.cpp` l.987-1031 | Sampled vs full corruption sweeps, fixed seeds | Concept 19 |
| 22 | `StrataTests/src/TestMain.cpp` l.1309-1370 | A test runner's `main`: isolation of the user's environment, module registration, helper modes | doctest |
| 23 | `StrataTests/src/TestCrashReporter.cpp` l.19-80 | A doctest listener and why doctest's signal handling is off | Signals (briefly) |
| 24 | `StrataTests/src/Renderer/GPUTestUtils.cpp` l.17-50 and `GPUTestUtilsTests.cpp` l.23-57 | Shared GPU device, validation errors as failures, command-buffer recycling | NVRHI basics (rendering chapter) |
| 25 | `StrataTests/src/Perf/PerfUtils.cpp` l.104-146 (`Summarize`, `Measure`) | Median and nearest-rank p95 in integer arithmetic; warm-up | Statistics basics |
| 26 | `StrataTests/src/Perf/PerfUtils.cpp` l.291-370 (`CheckConfirmed`) | The confirmed-check algorithm: decided once within budget, re-measure the rest, record all attempts | 25 |
| 27 | `StrataTests/Perf/Budgets.json` l.2-30 | A budget file whose comment is its specification | 26 |
| 28 | `StrataTests/src/Perf/PerfHarnessTests.cpp` l.512-541 | The canary: a deterministic workload as machine-health probe | 25-26 |
| 29 | `Tools/PerfStability.py` l.348-391 (`classify`) | Turning repeated runs into budget proposals under the ratchet rule (never raises unless re-baselined) | 26-27 |
| 30 | `StrataTests/src/FeatureTest/FeatureTests.cpp` l.152-196 and `FeatureTest/Scripts/FeatureScript.h` l.77-90 | Coverage by enumerating the component registry; the script-side check channel | Reflection registry (scene chapter) |
| 31 | `.github/workflows/ci.yml` l.19-60, l.195-215 | A CI matrix and the test step (labels, ulimits, trace) | Concept 24 |
| 32 | `.github/workflows/release.yml` l.45-93, l.175-226 | Version gate and checking the artifact as a user gets it | Concept 25 |
| 33 | `CMake/StrataPackaging.cmake` l.54-107 and `CMake/StrataPackageVersion.cmake` l.7-24 | Install rules, CPack, version validation | Concept 25 |
| 34 | `StrataTests/Editor/SmokeCommands.json.in` l.1-30 | An end-to-end test as data: editor commands with `expect` and `bind` | Editor commands (editor chapter) |

(34 entries; a chapter author should pick 10-30 for their chapter. The algorithms to keep even when long: 16, 26, 8/9.)

---

## 4. Figures

Diagrams:
1. **The three steps.** configure (CMake reads lists, presets, cache, `Layers.json`, fetches Slang) -> build (compile,
   shaders, link) -> test (CTest by labels). Data flow with the files each step reads and writes
   (`CMakeCache.txt`, `LayerLibraries.json`, `ShaderEntries.txt`, `bin/<Config>`, `PerfResults/<config>.json`).
2. **Target graph.** Update of ARCH l.48-67: layer libraries, `Strata`, `StrataTooling`, editor core/UI, runtime, CLI,
   tests, script modules, vendor; colour tooling vs runtime; show the FORBID set of the runtime.
3. **Layer table to libraries.** A source tree on the left, `Layers.json` rules in the middle, one static library per
   layer on the right, with "file in no layer / two layers -> configure error".
4. **"Games contain no tooling" proven twice.** Timeline: configure-time link-closure walk, link-time map file,
   test-time `CheckNoTooling.cmake`.
5. **Shader pipeline.** `.slang` + includes -> slangc (validated) -> `.raw.spv` -> StrataShaderTool (Invariant patch) ->
   `.spv` + `.h` -> `EmbeddedShaderRegistry.cpp` -> `Strata_Renderer`; side branches: `ShaderEntries.txt` -> spirv-val
   (Linux CI), Metal conversion (macOS CI), HLSL target test.
6. **SPIR-V word layout.** Header 5 words; an instruction word = word count (high 16 bits) | opcode (low 16); the
   `OpDecorate %v BuiltIn Position` followed by the inserted `OpDecorate %v Invariant`.
7. **Slang fetch state machine.** stamp matches -> use; else lock -> re-check -> download (3 attempts) -> hash ->
   extract to staging -> check slangc -> stamp -> rename -> unlock; every failure edge returns an error message.
8. **Shards.** All suites of the binary as a column; arrows to own CTests and 13 shards; the `Testing.Shards` check of
   "exactly one"; `.Sweep` suites also to `StrataTests.Fuzz`.
9. **CTest fixture chains.** DAGs: Export chain; feature-test chain; sample export -> windowed -> image/perf checks ->
   `PerfGPU.Samples`; `PerfResults.Clean` -> perf tests.
10. **Confirmed perf check.** Flowchart of `CheckConfirmed`: measure -> per metric within budget? decided : re-measure
    (up to 3) -> record attempts -> pass/fail. Plus a plot sketch of noise-only-adds (distribution with a hard lower
    floor).
11. **The budget lifecycle.** Provisional -> measured on reference machine -> Budget = 1.5 x Measured -> lowered when
    cheaper -> re-baselined only by the A/B procedure.
12. **CI matrix.** Jobs x what each builds/tests (configurations, compilers, caches, shader steps, labels excluded).
13. **Compiler cache keys in GitHub Actions.** Key = cache-job-sha, restore by prefix from branch or main, deletion of
    superseded entries; why main's set would otherwise be evicted.
14. **Release workflow.** version job -> three build jobs (Dist build, Dist tests, cpack, unpack and run, checksums) ->
    publish (only on vX.Y.Z); tag variants (rc = dry run).
15. **Installed layout.** Tree of a release archive (from `StrataPackaging.cmake` l.7-18).
16. **Feature test coverage loop.** Registries (components, settings sections, host functions, SDK names, field types,
    asset types) -> feature project must exercise each -> runners (headless, in-process editor, exported game, real
    executables, GPU).
17. **Look-dev harness.** capture (copy samples -> headless editors -> shots x sizes x AA x repeats) -> compare
    (difference, signed difference, crops, GPU ratio).

Screenshots (this area is not a rendering feature; screenshots are of tools and outputs):
1. A configure log showing `-- Slang 2026.20: ... (cached)` and the compiler-cache status line.
2. A configure failure naming a source file in no layer (made in a scratch copy) and the "StrataRuntime links tooling"
   message with its path.
3. Visual Studio's Solution Explorer folders (`Strata/Layers`, `Vendor`, `Strata/TestScripts`, "Generated Shaders").
4. `ctest --preset windows-debug -N -L core` output listing the shards; a `ctest -j 8` run summary.
5. A failing `Testing.Shards` message (suite in no shard).
6. Perf output lines `[perf] ...` and an "over the budget in attempt 1 of 3, measuring again" line; a `PerfResults`
   JSON excerpt.
7. `Tools/PerfStability.py --runs 5` report table.
8. GitHub Actions: CI matrix run page; a failure annotation in a pull request; the Release page with archives and
   `SHA256SUMS.txt`.
9. `Tools/LookDev.py compare` `index.html` with side-by-side and signed difference images (one pair is enough here; the
   rendering chapters reuse the harness for their own features).
10. The installed folder of a release archive in a file browser.
11. `StrataEditor.Smoke`'s `SmokeViewport.png` capture (floor, crate, lights) as an example of an end-to-end artifact.

---

## 5. Rules and pitfalls (the "why" boxes)

1. **Re-configure after adding or removing sources** (AG Building). The globs are evaluated at configure; the VS
   generator re-globs during the build but compiles with the stale project (DG l.187-189).
2. **Shaders are listed, not globbed** (SK). Every entry of `strata_add_shaders` is explicit; a stage comes from the name
   suffix; a missing entry is a missing shader at run time.
3. **Each parallel agent gets its own build directory** (AG). Two builds in one tree corrupt each other.
4. **CI always builds with warnings as errors; never silence a warning locally** (AG, SK). Vendor code is silenced as a
   whole instead, and consumed as SYSTEM includes so it never trips first-party `/WX`.
5. **Never put an engine/editor/test header that changes into a precompiled header** (DG l.232-235): every object of the
   target rebuilds; `Architecture.PrecompiledHeaders` refuses it.
6. **Include what you use even though the pch has it** (DG l.236-239): the lint and cached CI builds compile without
   pch, so a hidden missing include breaks there.
7. **Keep headers light** (DG l.240-254): forward-declare, `json_fwd.hpp`, `Scope<>` with out-of-line destructors; and no
   `std::span` of a declared-only JSON type, because old libc++ instantiates it (a real CI break).
8. **`ST_WITH_*` are definitions, never header macros; `#if ST_WITH_<MODULE>` only in the composition root, asset
   pipeline, runtime and tests** (AG Building; DG l.263-269): a missing include must not silently compile a module out;
   modules reach optional ones through services.
9. **Never widen `MayInclude` or add an allowlist line to make an include pass; invert the dependency** (AG Architecture
   rules). The table is the build: libraries can only link what layers may include.
10. **Games link no tooling** (AG Layers): proven at configure (closure walk) and on the linker map; a map that names
    nothing proves nothing, so required objects are checked first.
11. **Cached CMake options survive re-configure** (SK): a missing target may be an old cached OFF.
12. **Compiler caches need Ninja/Makefiles and embedded debug info; caches do not cache MSVC pch** (DG l.191-197).
13. **Push large integrations as `ci/<name>` and wait for green** (AG "CI before main"): older compilers and libraries
    reject what local ones accept; Apple Clang 17 even miscompiled `std::abs(x) > 0 ? x : 0` (DG l.218-221).
14. **Never change the Slang digest to match a download** (`StrataSlang.cmake` l.203): a different hash means the
    release was replaced; bump Slang only in a commit of its own with the full check list (DG Shaders item 5).
15. **Upgrade a submodule in its own commit, update `ThirdPartyNotices.md`, run every test** (AG); box3d's golden values
    come only from box3d's own test file, never from a Strata run (SK).
16. **Copyleft code is read for ideas only** (AG golden rule 1, DG l.6424-6426): copied copyleft code would choose
    Strata's license.
17. **Every test case belongs to a TEST_SUITE, every new suite prefix to a shard** (AG Testing): otherwise it runs in no
    CTest; `Testing.Shards` fails naming it. Keep shards under about a minute in Debug.
18. **Tests that crash the dynamic loader go in `LoaderFaults`** (DG l.406-411): on Linux a crash in static
    initialization leaves the loader lock held; any later `thread_local` with a destructor would hang.
19. **Never create a graphics device in a test; end GPU tests with `CHECK(gpu.GetNewErrorCount() == 0)`** (AG Testing):
    repeated `VkInstance` creation crashed drivers under load; validation errors must fail tests.
20. **Wait by the clock or a condition, never by frames; size job pools explicitly** (DG l.786-790): CI's macOS runners
    have 3 hardware threads.
21. **Never set the test process's environment for a child; use `run-with-environment`** (DG l.805-807): the
    environment is process-global and shared by concurrently running tests.
22. **Tests write only into `CreateTemporaryDirectory()` and never open samples in place** (AG Testing): the source tree
    and the user's data stay untouched (`STRATA_RUNTIME_DIR`, `STRATA_RECENT_PROJECTS`, `STRATA_SCRIPT_BUILDS_DIR`).
23. **Check that a new regression test fails without its fix** (AG Testing).
24. **doctest's POSIX signal handling is disabled** (`StrataTests/CMakeLists.txt` l.164-166): it would replace the
    script `CrashGuard`'s handlers, uncontaining script crashes.
25. **Perf limits live only in `Budgets.json`; budgets only go down; at most 1.5 x measured; commits that add or lower
    budgets state the measurement** (AG Testing; DG l.489-510): otherwise gates drift up with every regression.
26. **A failure on a busy machine says nothing about the code** (DG l.534-537): confirmations take about a minute, so
    a build running beside them can fail every attempt; rerun on a quiet machine, look at the canary.
27. **Perf numbers only from optimized builds, without validation layers, through `ExecuteAndWait`** (DG l.546-550,
    `PerfUtils.h` l.169-170): Debug and validation multiply costs; a plain `executeCommandList + waitForIdle` makes every
    later `open()` create a command pool.
28. **Peak-memory metrics in a fresh helper process** (DG l.613-614): a process's peak includes everything before.
29. **Complexity claims belong in deterministic unit tests, not perf tests** (DG l.550): they run everywhere.
30. **Keep the feature test current** (golden rule 6): it fails on unexercised registrations, so a feature without its
    feature-test entry cannot land.
31. **Release tests run Dist; expectations that differ say `#if defined(ST_DIST)`** (AG Testing, DG Releases item 3):
    CI tests Release, only release steps test Dist.
32. **A file releases must ship needs an install rule and an entry in `StrataEditor.Install`'s layout** (AG Building):
    the test checks the exact top-level entries.
33. **Use CMake's own `cpack` on Windows runners** (`release.yml` l.181): Chocolatey's `cpack` comes first on PATH.
34. **Annotations, not logs, carry CI failures** (`ci.yml` l.217-218): logs need admin rights; `known failure:` lines
    are not error lines so they do not crowd out real failures (`convert_shaders_to_metal.sh` header).
35. **PowerShell does not wait for GUI-subsystem programs** (DG l.334-336): pipe their output or `Start-Process -Wait`
    when the exit code matters.
36. **Verify exactly what is staged in a clean worktree, Debug and Release** (SK): the working tree often holds other
    work; some bugs only show in one configuration.

---

## 6. Hands-on

For engine developers:
1. **Build from scratch on your OS** (easy). Clone, submodules, configure a preset, build Debug, run
   `ctest --preset <p>-debug -LE "gpu|perf" -j 8`. Proves: the three steps, presets, labels.
2. **Read the configure log** (easy). Find the Slang line, the compiler-cache line, the absent packaging message
   (configure with `-DSTRATA_BUILD_CLI=OFF`). Proves: what configure does.
3. **Add a source file and see why re-configure matters** (easy). Add an empty `.cpp` to a module, build without
   re-configure in VS, then re-configure. Then add a file in a folder no layer matches (scratch copy) and read the error.
   Proves: globbing, layer ownership.
4. **Break the layering on purpose** (medium, scratch branch). Include an AssetPipeline header from a runtime layer and
   observe `Architecture.Layering` and, if you add the link, the link-closure error with its path. Proves: the table is
   the build; "games contain no tooling".
5. **Build a game without physics and audio** (medium). Configure a second build directory with
   `-DSTRATA_WITH_PHYSICS=OFF -DSTRATA_WITH_AUDIO=OFF -DSTRATA_BUILD_EDITOR=OFF`, run `ctest -LE "gpu|perf|package"`,
   inspect which test files were left out (`STRATA_TESTS_OF_*`). Proves: optional modules.
6. **Measure pch and cache effects** (medium). Time a clean Debug build with and without `STRATA_PRECOMPILED_HEADERS`;
   with ccache/sccache via `windows-ninja`, build twice. Proves: compile-time engineering trade-offs.
7. **Run `Tools/CompatLint.py --changed-since main`** on a change that relies on the pch (medium). Proves: why
   include-what-you-use.
8. **Add a shader variant** (medium). Add a `VARIANTS` line with a define to `strata_add_shaders`, re-configure, find the
   new `.raw.spv`, `.spv`, `.h` and the `ShaderEntries.txt` line. Proves: the shader build.
9. **Write a tiny SPIR-V inspector with `SpirvModule.h`** (hard). Use `ParseSpirv` to list opcodes and find decorations
   of an embedded module. Proves: binary formats, the tool's algorithm.
10. **Add a new test suite with a new prefix** (easy). See `Testing.Shards` fail, then add it to `CoreShards.json`.
    Proves: sharding and its guard.
11. **Write a corruption sweep for a small parser** (medium). Use `SelectSweepOffsets` in a `*.Sweep` suite; run it
    sampled in Debug and full with `STRATA_TEST_SWEEP=full`. Proves: deterministic fuzzing.
12. **Write a GPU readback test** (medium). With `Tests::GPUContext`, write a buffer, read it back with
    `ReadBufferRange`, end with the error-count check; run under the validation layer. Proves: GPU test rules.
13. **Add a perf metric** (hard). Add a provisional `Budgets.json` entry, measure with `Perf::Measure` inside
    `CheckBudgetConfirmed`, run `ctest --preset <p>-release -L perf`, read `PerfResults`. Then run
    `Tools/PerfStability.py --runs 3 --propose-budgets out.json` and read what it would write. Proves: the perf lab and
    the ratchet.
14. **Write a helper-mode process test** (hard). Add a `--strata-test-helper=` mode and a test that runs it with
    `Process::Run` and checks output and exit code. Proves: process tests without external programs.
15. **Add a component and satisfy the feature test** (medium-hard; with the component chapter). Watch the feature test
    fail on the missing entity/property, then extend `Feature.stscene`. Proves: coverage by construction.
16. **Make a local package** (medium). `cmake --install build/<p> --config Dist --prefix <dir>`, then
    `cpack --config build/<p>/CPackConfig.cmake -C Dist`; compare the tree with `StrataPackaging.cmake`'s comment and
    `InstallEndToEnd.cmake`'s expected entries. Proves: install layout and the install test.
17. **Dry-run a release on a fork** (hard). Push `v0.7.0-rc1`-style tag on a fork with the project's version; read the
    version job's checks and artifacts. Proves: the release workflow.
18. **Read a CI failure from annotations only** (easy). Use `Tools/CIStatus.py annotations <commit>`. Proves: CI
    diagnostics.

For game developers (lighter, they mostly use installed builds):
1. **Install a release archive and check it** (easy): unpack, run `StrataEditor --version`, open a sample from the
   launcher. Proves: what a release contains.
2. **Build Strata from source to get a newer engine** (medium): presets, the per-user Slang cache, where the editor lands.
3. **Write a command script as a smoke test for your game** (medium; with the editor automation chapter): model it on
   `SmokeCommands.json.in` with `expect` steps, run `StrataEditor --commands ... --quit-after-commands | Out-Host`.
   Proves: end-to-end tests for games; why PowerShell needs the pipe.
4. **Check your exported game headless** (easy): `StrataRuntime`-based game with `--headless --frames 120`,
   `--screenshot` (windowed), `--perf-log`. Proves: runtime check options the CTests use.
5. **Read `ThirdPartyNotices.md` and your sample's `CREDITS.md`** (easy): what attribution your exported game must show.

---

## 7. Glossary

- **Translation unit**: one `.cpp` file after the preprocessor has included its headers; the unit the compiler compiles.
- **Linker**: combines object files and libraries into an executable; resolves symbols.
- **Static library / shared library / module library**: an archive of objects linked in; a DLL/.so loaded at run time;
  a shared library loaded explicitly (script modules).
- **Interface library (CMake)**: a target with no compiled code that carries usage requirements (`Strata`,
  `StrataTooling`, `StrataEngineCodegen`, `glm`).
- **Usage requirements, PUBLIC/PRIVATE/INTERFACE**: whether a target's include dirs, definitions and links apply to
  itself, its dependents, or both.
- **Generator (CMake)**: the native build system CMake writes (Visual Studio, Ninja Multi-Config).
- **Multi-config generator**: one build tree holding Debug, Release and Dist (`--config`).
- **Preset**: a named configure/build/test setup in `CMakePresets.json`.
- **Cache variable / `CMakeCache.txt`**: values (options) CMake remembers between configures.
- **Generator expression**: `$<...>` evaluated at generate time (per configuration), e.g. `$<CONFIG:Dist>`.
- **`GLOB_RECURSE CONFIGURE_DEPENDS`**: collect files by pattern and re-check at build time.
- **Script mode (`cmake -P`)**: CMake running a script without a project (version header, sample copy, test scripts).
- **`cmake_language(DEFER)`**: run a call at the end of a directory's processing.
- **`EXCLUDE_FROM_ALL`**: a target built only when something needs it.
- **SYSTEM include**: a header directory whose warnings the compiler suppresses.
- **Debug / Release / Dist**: Strata's configurations; Dist = shipping, asserts out, `ST_DIST`.
- **`ST_CORE_ASSERT` / `ST_CORE_VERIFY`**: checks compiled out of Dist / kept in Dist.
- **Precompiled header (pch)**: a header compiled once and reused by every TU of a target.
- **Forward declaration**: naming a type without its definition to avoid including its header.
- **Compiler cache (ccache, sccache)**: reuses object files for identical compile commands and inputs.
- **Compiler launcher**: a program CMake puts in front of every compile (the cache).
- **`/Z7` vs PDB**: debug info inside each object vs in one shared program database.
- **Instruction set extension**: SSE, AVX2, FMA, F16C...; compiler flags that allow those instructions.
- **FMA contraction**: compiling `a*b+c` into one fused instruction, which changes rounding.
- **Determinism (cross-platform)**: the same inputs giving bit-identical results on every machine.
- **Submodule (git)**: a pinned commit of another repository inside this one; shallow = without history.
- **Vendoring**: keeping third-party code inside the repository.
- **Permissive / copyleft license**: MIT/BSD/zlib-style vs GPL-style licenses that impose terms on derived works.
- **SHA-256 pin**: a cryptographic digest that a download must match.
- **Per-user cache**: a folder in the user's profile (`%LOCALAPPDATA%\Strata\Toolchains` etc.).
- **File lock**: an OS lock on a file that serializes processes (Slang fetch, `PerfLock.py`).
- **Atomic rename**: replace a file or folder in one step so readers never see half of it.
- **Slang / slangc**: the shader language and compiler Strata uses (HLSL syntax) since wave 8.
- **SPIR-V**: Vulkan's binary shader format: 32-bit words, a 5-word header, instructions with a word count and opcode.
- **spirv-val**: the SPIRV-Tools validator.
- **MoltenVK**: Vulkan on top of Metal (macOS).
- **Invariant (position)**: a guarantee that the same computation of a vertex position gives bit-identical results
  across shaders (needed by the depth prepass's EQUAL test).
- **Embedded shader registry**: generated table of shader name -> SPIR-V array.
- **Layer (Strata)**: an architectural group of engine folders in `Layers.json` with the layers it may include.
- **Layer table / `MayInclude` / `Tooling` / `Option`**: the table's entries, allowed dependencies, "only tools contain
  it", the CMake option that builds it.
- **Composition root**: the one place that registers every module (`Engine::RegisterBuiltinModules`).
- **Link closure**: everything a target links, transitively.
- **Linker map**: a text file the linker writes listing what went into the executable.
- **doctest**: the header-only C++ test framework; `TEST_SUITE`, `TEST_CASE`, `CHECK`, `REQUIRE`, `INFO`, `CAPTURE`.
- **CTest**: CMake's test driver; a CTest test is a command with properties.
- **Label (CTest)**: a tag for selecting tests (`-L`, `-LE`).
- **Shard**: a slice of one test binary's suites run as its own CTest so slices run in parallel.
- **Fixture (CTest)**: setup/cleanup tests other tests require (`FIXTURES_SETUP`/`REQUIRED`).
- **Resource lock**: CTest property that keeps tests sharing a resource from running together.
- **`RUN_SERIAL`**: a CTest that runs alone.
- **Helper mode**: the test executable started as a child process with `--strata-test-helper=<mode>`.
- **Fake CMake / fake editor**: the test binary standing in for those programs in tests.
- **Sweep / `.Sweep` suite**: tests over many byte offsets or random corruptions of a format.
- **Fuzz run**: `StrataTests.Fuzz`, the sweeps in full.
- **Validation layer**: Vulkan's debug layer that reports API misuse.
- **Readback**: copying GPU results to the CPU to check them.
- **Headless**: without a window (and, for the editor, possibly without a GPU: `--no-gpu`).
- **Perf lab**: Strata's performance test harness (`StrataTests/src/Perf`).
- **Metric / budget / target / provisional**: a measured quantity; its gating limit; a goal below the limit; a metric
  not yet measured on the reference machine.
- **Reference machine**: the Windows box budgets are measured on (i7-13700K, RTX 5090).
- **Confirmed check**: re-measuring a metric over budget, failing only if every attempt is over.
- **Ratchet**: a limit that may only tighten.
- **Canary**: a fixed workload whose time tells whether the machine itself is slow.
- **Interleaved A/B**: alternating runs of two builds to compare them under the same conditions.
- **Median / p95 / nearest rank**: the middle sample; the smallest sample at least 95% do not exceed.
- **Feature test**: the project and runners that must exercise every registered feature.
- **Journal (feature test)**: the text property where feature scripts record events.
- **Command script**: a JSON list of editor commands (with `expect`, `until`, `bind`).
- **End-to-end test**: a test that runs the real executables.
- **Smoke test**: a quick check that a program starts, does its basics and quits.
- **CI (continuous integration)**: building and testing every push on shared machines.
- **Runner (GitHub Actions)**: the machine a CI job runs on; hosted runners have no GPU.
- **Matrix**: one job definition expanded over OSes/configurations.
- **Annotation**: a GitHub check message attached to a file/line, readable without the log.
- **`ci/<name>` branch**: a branch that triggers CI before merging to main.
- **Install tree / prefix**: where `cmake --install` lays out the product.
- **CPack**: CMake's packager (ZIP, TGZ).
- **Installation marker**: `StrataInstall.json`, which tells the editor it runs from an installation.
- **Pre-release suffix / release candidate (rc)**: `-rc1` etc.; a dry run that is never published.
- **Dry run**: running the release pipeline without publishing.
- **Checksum file**: `SHA256SUMS.txt`, digests of every archive.
- **Look-dev harness**: `Tools/LookDev.py`, fixed shots captured and compared between builds.
- **Signed difference image**: after minus before, red brighter, blue darker.
- **Committed generator**: a script whose outputs are committed (CI never runs it), sometimes with a check test.

---

## 8. Proposed chapters (teaching order)

1. **How a C++ program is built** (concept, both, S/M): compilation, linking, headers, static vs shared, why build
   systems exist. Prerequisites: a little programming.
2. **Building Strata: CMake, presets and configurations** (tutorial, both, M): clone, submodules, presets, Debug /
   Release / Dist, options, where binaries land, re-configure rules; the validation layer setup. Prerequisite: 1.
3. **Inside Strata's CMake: targets, layers and the "no tooling in games" proof** (internals, engine, L): targets and
   usage requirements, `strata_add_layer_libraries`, `strata_layer_link`, link closure, linker map,
   `LayerLibraries.json`, optional modules and `ST_WITH_*`. Prerequisites: 2, the architecture chapter's layers concept
   (or a short intro here).
4. **Compiler flags, compile time and portability** (internals, engine, M): warning policy, instruction sets and FMA
   determinism, precompiled headers, header weight, compiler caches, three compilers and their traps, CompatLint.
   Prerequisite: 3.
5. **Third-party code and pinned tools** (internals, engine, M): submodules, vendor wrapper, box3d and zstd specifics,
   licenses and notices, the Slang pin and its fetch algorithm. Prerequisites: 2, 4.
6. **Generated code: shaders, embedded files and version stamps** (internals, engine, M): `strata_add_shaders`,
   StrataShaderTool and SPIR-V patching, the registry, `strata_embed_file`, version/commit headers, sample copy.
   Prerequisites: 3; a shader primer from the rendering part (can be forward-referenced).
7. **Testing an engine: doctest, CTest and Strata's test program** (concept + internals, engine, L): test kinds, the
   test binary, main, helpers, helper modes, shards and `Testing.Shards`, labels, fixtures, locks, sweeps and fuzzing,
   determinism rules, crash naming. Prerequisites: 2.
8. **GPU, end-to-end and package tests** (internals, engine, M): `GPUContext`, validation errors, readback; EndToEnd
   suites; editor smoke/export chains; sample runners; package and install tests. Prerequisites: 7; editor commands
   chapter for command scripts.
9. **The feature test: coverage by construction** (internals, engine, M): the project, the coverage checks, the
   runners, extending it. Prerequisites: 7; component/registry and scripting chapters.
10. **Measuring performance: the perf lab** (concept + internals, engine, L): benchmarking statistics, noise, budgets,
    confirmed checks, results files, canary, ratchet, provisional metrics, reference machine, PerfStability, PerfLock,
    A/B and layout effects; the catalogue of perf suites as a reference table. Prerequisites: 7, 8.
11. **Image regression: the look-dev harness** (tutorial + internals, engine, S/M): capture, compare, signed images,
    metrics, its self-tests. Prerequisites: 8; rendering basics. (Could move into the rendering part.)
12. **Continuous integration** (internals, engine, M): the CI matrix, caches and eviction, shader steps, annotations,
    the Dist job, `ci/<name>` branches, CIStatus. Prerequisites: 4, 7.
13. **Packaging and releasing Strata** (tutorial + internals, both, M): install layout, the marker, CPack, versions,
    the release workflow, release procedure, verifying an archive. Prerequisites: 2, 12.
14. **Working on Strata: the review checklist and contribution workflow** (reference, engine, S): golden rules, the
    pre-commit checklist, clean-worktree verification, commit hygiene, the third-party rule.
15. **Tools reference** (reference, both, S): every tool of `Tools/` with what it does, how it is run, and which chapter
    teaches it (generators belong to their rendering/sample chapters).

---

## 9. Not determined

- Did not read: `StrataTests/src/TestHelpers.cpp` beyond the sweep functions; most of `TestMain.cpp`'s ~50 helper modes
  (only their names); `StrataTests/src/Engine/ModuleRegistrationHelpers.cpp`; `StubWindow.h`; the perf suites' sources
  (only `PerfUtils`, harness tests, file list); `RendererPerfUtils.h`; the end-to-end suites' bodies; `SampleProject.cmake`,
  `ScriptsEndToEnd.cmake`, `ReplaySession.cmake`, `BuildPackageProject.cmake`, `SlangFetchTests.cmake` beyond headers;
  `PackageProject/CMakeLists.txt`; `Tools/*.py` beyond their docstrings and a few functions (`PerfStability.classify`,
  `PerfLock` lock calls, `CompatLint` function list); `annotate_failures.py` beyond its patterns;
  `convert_shaders_to_metal.sh` beyond l.60; `StrataScriptCore/CMake/StrataScriptModule.cmake` (scripting area);
  `StrataEditor/CMakeLists.txt` and `StrataRuntime/CMakeLists.txt` beyond the map option (resource files, `/ENTRY`,
  `StrataSamples` target); `LayeringAnalyzer`; `Docs/Releases/*.md` beyond a grep.
- Documentation drift found (worth a correction in the engine docs, and care in the book):
  - DG Shards (l.404-405) and SK list 12 shards; `StrataTests/CoreShards.json` has 13 (`SceneTiming`, suites
    `Scene.Timing*`, is missing from both texts).
  - DG Feature test l.828 names `Tools/GenerateAssets.py`; the file is `StrataTests/FeatureTest/Tools/GenerateAssets.py`.
  - DG Building l.172-177's option list omits `STRATA_WITH_GLFW` (described in Optional modules instead).
- Exact shader count: about 113 registered entries counted by a rough grep of `Strata/CMakeLists.txt` l.80-200 (RM
  speaks of "all 103 shaders" in the Slang spike); the book should take the number from a build's `ShaderEntries.txt`.
- Exact count of CTests per configuration not determined (about 88 `add_test` calls, several in loops, some only in
  Release/Dist or only with the editor/runtime/Python/Apple/Windows); `ctest -N` on a build would give it (no build was
  run, per the ground rules).
- Release history per feature is partial: the documents date the perf lab (wave 1), layer libraries, optional modules,
  pch, shards, fuzz, compiler cache and Windows Debug CI (wave 4, 0.4.0), release 0.3.0 with the Dist CI job, PerfLock,
  CompatLint and CIStatus (wave 4 step 0), the look-dev harness (wave 7, 0.7.0), Slang and the no-GLFW option (wave 8,
  unreleased); other items have no date in the documents.
- Whether `Tools/PhysicsSweep.py` and the committed generators have CTests other than the two Showcase ones: none found
  in `StrataTests/CMakeLists.txt` besides `StrataTools.*`; `GenerateBlueNoise.py --check` and `FitFilmic.py --check` are
  manual.
- macOS Metal known-failure list and how MoltenVK runs the bindless table at run time: only the script's header read;
  the rendering area owns it.
- Screenshots of CI pages require GitHub access, which this survey did not use.
