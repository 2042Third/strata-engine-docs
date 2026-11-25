---
id: reference/build
title: "CMake options, presets, test labels, tools"
description: "What a person types to configure, build and test Strata: its CMake options, presets, test labels and shards, and the scripts of Tools."
kind: reference
size: S
tracks: []
needs: [basics/build]
status: final
---

This page lists what you type to configure, build and test Strata, and the scripts that help around the build. The included tables are read from the build files of the engine at the pin, so a row is what the files say. Each section says what a row and its columns mean. The tools table is written by hand and is checked again when the pin moves. To build Strata step by step, read [Building Strata](../engineering/building.md); to learn how :term[CMake]{id=cmake} itself is used, read [Inside the CMake project](../engineering/cmake.md).

## CMake options

An option is a switch you give CMake when you configure, written `-D<name>=<value>`, such as `-DSTRATA_ENABLE_TRACY=ON`. A row shows the option, its default, its help text and the file and line that define it. The `STRATA_BUILD_*` switches choose which programs are built. The `STRATA_WITH_*` switches choose the optional modules. The `STRATA_USE_*` switches choose which instruction sets the engine's code may use.

The roles of these switches and of the :term[compiler]{id=compiler} flags behind them are taught in [Building Strata](../engineering/building.md) and [Compiler flags and portability](../engineering/flags-portability.md).

Three more variables are set with `-D` but are not switches, so the table does not hold them. `STRATA_SLANG_ROOT` names an extracted release of Slang, the compiler of Strata's shaders, for a machine that cannot download the pinned one; the :term[environment variable]{id=environment-variable} of the same name gives its default. `STRATA_PACKAGE_VERSION` names the version in a release archive's name: empty for the project's version, or that version with a suffix such as `-rc1`. `STRATA_COMPILER_CACHE_PROGRAM` names the `ccache` or `sccache` program that `STRATA_COMPILER_CACHE` uses when none is found on the path.

::include{file="build.md"}

The included file also holds the presets, the tests and the shards. The next sections say how to read each of its tables.

## Presets

A **configure preset** is a named set of CMake settings in `CMakePresets.json`: you pass its name to `cmake --preset`, and CMake chooses the generator and the build folder. A build preset names a configure preset and a configuration (`Debug`, `Release` or `Dist`) for `cmake --build --preset`. A test preset does the same for `ctest --preset`. The preset named `base` is hidden: the others build on it, so every build folder is `build/<preset>`. Binaries land in `build/<preset>/bin/<Config>/`.

When several agents build at once, each one gives its own folder, as in `cmake --preset windows -B build/agent-<name>`, because two builds in one folder corrupt each other. The presets are used step by step in [Building Strata](../engineering/building.md).

## Test names and labels

CTest runs many tests, and a **label** is a tag on a test that lets you select a group: `ctest -L gpu` runs only the tests with the label, and `ctest -LE gpu` runs all the others. In the table of tests, a row is one CTest name and the labels it carries. A test with no label is omitted by `-L` and kept by `-LE`.

| Label | What it selects |
| --- | --- |
| `core` | The unit tests of `StrataTests`, split into shards. |
| `fuzz` | Every corruption sweep in full, in Release and Dist only. |
| `perf` | The speed tests against their budgets, in Release and Dist only. |
| `gpu` | Tests that need a :term[graphics card]{id=gpu} (GPU) and a Vulkan driver. |
| `package` | Tests that build and install with CMake and a compiler. |
| `feature` | The feature test project and its games. |
| `tools` | The Python tools of the next section, run on their own. |

Why each label exists, and when to run it, is taught in [Test kinds and labels](../engineering/test-kinds.md). For example, a machine with no GPU runs `ctest --preset linux-debug -LE gpu`.

## Shards

A **shard** is one slice of the unit tests, run as its own CTest so that the slices run side by side. A suite is a named group of unit tests. A row of the table of shards gives a CTest name, the suites it runs (doctest filters, where `*` matches any text) and the suites it leaves to another. The first rows are tests that run their suites on their own. Every suite runs in exactly one place: the unit tests of the suite `Testing.Shards` fail and name a suite that runs in none or in two.

How the test program works is taught in [The test program](../engineering/test-program.md).

## Tools

This table is written by hand from the files named in its first column, since no generator lists them. A row names a script, what it does, how its own text says to run it and the page that teaches it. The Python scripts use only the Python standard library, and a script that shows `python -I` in its usage runs in isolated mode. A script marked "committed output" writes files that are committed to the repository: you run it again only to change what it makes.

| Tool | What it does | Run | Taught in |
| --- | --- | --- | --- |
| `Tools/CIStatus.py` | Shows the state of a commit's continuous integration (CI) runs and their failure notes. | `status <commit>` or `annotations <commit>` | [Continuous integration](../engineering/ci.md) |
| `Tools/CompatLint.py` | Compiles files with GCC 14 and LLVM 16, which stand in for CI's compilers, before a push. | `--changed-since main` | [Continuous integration](../engineering/ci.md) |
| `Tools/PerfLock.py` | Runs a command while it holds a lock, so measurements never overlap. | `--label <who> -- <command>` | [The perf lab](../engineering/perf-lab.md) |
| `Tools/PerfStability.py` | Runs the perf tests several times and reports how stable each metric is. | `--runs 5` | [The perf lab](../engineering/perf-lab.md) |
| `Tools/PhysicsSweep.py` | Sweeps the physics tuning over the settle scenes. | `distances`, `knobs`, `workers` or `pits` | [Physics tuning](../physics/tuning.md) |
| `Tools/LookDev.py` with the `Tools/LookDev` folder | Takes fixed shots through headless editors and compares two sets. | `python -I Tools/LookDev.py capture --build <bin dir>` | [Look-dev](../engineering/look-dev.md) |
| `Tools/GenerateBlueNoise.py` | Writes the sun shadows' blue-noise tile (committed output); `--check` verifies it. | `python Tools/GenerateBlueNoise.py` | [Generated code](../engineering/generated-code.md) |
| `Tools/FitFilmic.py` | Fits the tone curve's constants (committed output). | `--check` or none | [Generated code](../engineering/generated-code.md) |
| `Tools/FitAOMultiBounce.py` | Fits ambient occlusion's multi-bounce (committed output). | `--write` | [Generated code](../engineering/generated-code.md) |
| `Tools/GenerateAreaTable.py` | Writes the anti-aliasing area table (committed output). | none | [Generated code](../engineering/generated-code.md) |
| `Tools/GenerateWhiteBalance.py` | Writes the white balance's locus table (committed output). | none | [Generated code](../engineering/generated-code.md) |
| `Tools/ConvertLTCTable.py` | Converts the published fit that rectangle lights are shaded with into two tables (committed output); `selftest` checks them. | `python -I`, `<ltc.js> <output>`, `--check` or `selftest` | [Generated code](../engineering/generated-code.md) |
| `Tools/GenerateBrandAssets.py` | Draws the Strata mark and its icons (committed output). | none | [Generated code](../engineering/generated-code.md) |
| `Tools/GenerateIslandTerrain.py` | Makes the Open World sample's island terrain and scatter (committed output). | `terrain` or `scatter` | [Generated code](../engineering/generated-code.md) |
| `Tools/GenerateShowcaseTerrain.py` | Makes the Showcase ground and checks its shots; a test keeps it equal to the files. | `python3 -I`, `terrain`, `check` or `stations` | [Generated code](../engineering/generated-code.md) |
| `Tools/GenerateShowcaseProps.py` | Makes the Showcase props, maps and command scripts; a test keeps it equal. | `python3 -I`, `props` or `materials` | [Generated code](../engineering/generated-code.md) |
| `StrataTests/FeatureTest/Tools/GenerateAssets.py` | Makes the tiny assets of the feature test project (committed output). | none | [Feature test](../engineering/feature-test.md) |
| `StrataEditor/Tools/GenerateIconHeader.py` | Writes the editor's icon header from the `Lucide` font. | `--version <release>` | [Generated code](../engineering/generated-code.md) |
| `.github/scripts/annotate_failures.py` | Turns build and test failures in CI logs into annotations. | `annotate_failures.py <log>...` | [Continuous integration](../engineering/ci.md) |
| `.github/scripts/validate_shaders.sh` | Checks every embedded shader with `spirv-val`. | `validate_shaders.sh <EmbeddedShaders folder>` | [Continuous integration](../engineering/ci.md) |
| `.github/scripts/convert_shaders_to_metal.sh` | Converts every embedded shader to Metal and compiles it. | `convert_shaders_to_metal.sh <folder> <output>` | [Continuous integration](../engineering/ci.md) |

The Developer Guide names the feature test's generator without its folder, `StrataTests/FeatureTest/`. No such script stands in the top `Tools` folder at the pin: the script lives in the feature test project, as the table says.

## Where it lives in Strata

- `CMakeLists.txt`: the program switches, the optional modules, the compiler cache and precompiled headers.
- `CMake/StrataCompilerOptions.cmake`: the instruction sets and the compiler cache program.
- `CMake/StrataSlang.cmake`: `STRATA_SLANG_ROOT`.
- `CMake/StrataPackaging.cmake`: `STRATA_PACKAGE_VERSION`.
- `CMakePresets.json`: the configure, build and test presets.
- `StrataTests/CMakeLists.txt`: every CTest name and its labels.
- `StrataTests/CoreShards.json`: the shards, their suites and the suites of the fuzz test.
- `Tools/`, `.github/scripts/`, `StrataEditor/Tools/` and `StrataTests/FeatureTest/Tools/`: the scripts of the tools table.
