---
id: engineering/building
title: "Building Strata"
description: "Build Strata from source in the configuration and with the options a piece of work needs, find every result, and run Debug builds under validation."
kind: how-to
size: M
tracks: [E]
needs: [core/first-change]
time: 90
learn:
  - id: choose-preset
    text: choose the configure preset and the configuration that fit your system and your task
  - id: build-tree
    text: find where every result of a build lands and explain the folders of a build tree
  - id: change-options
    text: change a build option without being caught by the cache, and configure again when the sources change
  - id: validation
    text: set up the Vulkan validation layer on your system and check that a Debug build uses it
since: 0.3.0
status: final
---

You built Strata once, in `Debug`, to change one function. This page turns that single build into a skill. You choose the preset, the configuration and the options a piece of work needs. You learn where every result lands, and you run Debug programs under the Vulkan validation layer. Before you start:

- You have the clone at the book's commit, with its :term[submodules]{id=submodule} and one `Debug` build, as the [page on your first engine change](../core/first-change.md) left them.
- You have the C++ tools of [installing Strata](../start/install.md), and a network for the first :term[configure step]{id=configure-step}.
- You know the box on what a source build needs in that page, which says four things. :term[CMake]{id=cmake} is 3.25 or newer. The :term[compiler]{id=compiler} is as new as Microsoft Visual C++ (MSVC) 19.40, GCC 13, Clang 17 or Apple Clang 15. The first configure downloads Slang once into a cache of your user account. The Linux development packages and the Vulkan kit are optional.

## What you choose before you build

You pick three things for every build: a **preset**, a configuration and the options. A preset is a named set of build settings that CMake reads from `CMakePresets.json`. Without presets you would type a generator, a folder and several options on every :term[command line]{id=terminal-command}; with them you type one name.

The first setting a preset makes is the generator. A **generator** (CMake) is the part of CMake that writes the build files of one build tool, such as Visual Studio or Ninja.

A **multi-config generator** writes build files that hold every configuration, so that one build folder builds `Debug`, `Release` and `Dist` without a new configure step. Every generator that Strata's presets name is of that kind: the Visual Studio ones and `Ninja Multi-Config`.

Here is the start of Strata's list of configure presets. The hidden preset `base` holds what all others share, and the others inherit from it.

```json src="CMakePresets.json#L5-L23"
{
	"name": "base",
	"hidden": true,
	"binaryDir": "${sourceDir}/build/${presetName}"
},
{
	"name": "windows",
	"displayName": "Windows (Visual Studio 2026)",
	"inherits": "base",
	"generator": "Visual Studio 18 2026",
	"architecture": { "value": "x64", "strategy": "set" },
	"condition": { "type": "equals", "lhs": "${hostSystemName}", "rhs": "Windows" }
},
{
	"name": "windows-vs2022",
	"displayName": "Windows (Visual Studio 2022)",
	"inherits": "windows",
	"generator": "Visual Studio 17 2022"
},
```

1. **Line 8:** `binaryDir` makes the build folder `build/` plus the preset's own name, so `windows` builds into `build/windows` and no two presets share a folder.
2. **Line 13:** `inherits` copies every setting of `base` into `windows`, and the preset adds its generator and its architecture.
3. **Line 16:** `condition` makes the preset available only on a Windows host; on Linux or macOS, CMake does not offer it.
4. **Line 21:** `windows-vs2022` inherits `windows` and replaces only the generator, so it keeps the condition and the folder rule.

The other presets work the same way. `windows-ninja` inherits `base` and picks `Ninja Multi-Config` with the compiler `cl`; `linux` and `macos` use `Ninja Multi-Config` too, and `macos` also sets the deployment target 14.0, so its programs run on macOS 14 and later. Each configure preset has a build preset and a test preset for every configuration, named `<preset>-debug`, `<preset>-release` and `<preset>-dist`: 15 of each. A test preset also prints the output of a failed test, and counts a run that finds no tests as an error.

The second thing CMake keeps is the **cache variable**: a named setting that the configure step stores in the file `CMakeCache.txt` of the build folder and reads again at the next configure. Options such as `STRATA_BUILD_RUNTIME` are cache variables. The file is why a build folder remembers what you chose last week, and why that memory can surprise you; the options section below shows how.

:::why[Why a preset names a build folder]
Two builds in one folder corrupt each other, because both write the same cache and the same objects. A folder named after the preset lets you keep a `windows` and a `windows-ninja` build side by side, and the cost is disk space: each folder holds a full build.
:::

## Configure, build and test

:::::steps

1. Choose the configure preset of your system from this table.

   | Preset | Generator and compiler | Use it when |
   | --- | --- | --- |
   | `windows` | Visual Studio 2026, 64-bit | you build with Visual Studio 2026 |
   | `windows-vs2022` | Visual Studio 2022 | you have the older Visual Studio |
   | `windows-ninja` | Ninja Multi-Config with `cl` | you work in a Visual Studio developer environment, or want a compiler cache |
   | `linux` | Ninja Multi-Config | you build on Linux |
   | `macos` | Ninja Multi-Config | you build on macOS |

   **You should see:** one row for your system, or three on Windows. The command `cmake --list-presets` lists the presets of your host.

   **If you do not see it:** a preset that is missing from the list belongs to another host system; its condition is false here. The `windows-ninja` preset also needs `cl` on the path, which only a developer environment (the Developer PowerShell, or `vcvars64.bat`) provides.

2. Run the configure step with the name of the preset, in the clone's folder.

   ```sh
   cmake --preset linux
   ```

   **You should see:** the log of the configure step. Two lines matter. The line `Slang 2026.20: <path>/bin/slangc (downloaded)` appears on the first configure, preceded by a line that starts with `Downloading`; every later configure of any build folder prints `(cached)` instead. The line `Compiler cache: ccache (precompiled headers: OFF)` appears only when the compiler cache is on, with the name of its program.

   **If you do not see it:** the log names the problem in a line that starts with `CMake Error`. "In-source builds are not supported" means that you configured without a preset. "Third-party submodules are missing" means that `git submodule update --init --recursive --depth 1` has not run. A failed Slang download needs the network once, or `-DSTRATA_SLANG_ROOT=<folder>` with a Slang release you downloaded yourself.

3. Build the configuration you need with the build preset of the same name plus the configuration.

   ```sh
   cmake --build --preset linux-debug --parallel
   ```

   **You should see:** the compiler's lines, and at the end no error. The first build takes the longest; a later one compiles only what changed.

   **If you do not see it:** a :term[compiler error]{id=compile-error} in code you did not touch usually means a compiler older than the minimum. A warning is an error here, because `STRATA_WARNINGS_AS_ERRORS` is on.

4. Pick the configuration for the task. The three differ in what they keep:

   - `Debug` has no :term[optimization]{id=optimization}, and keeps the asserts and the log lines. Use it to follow code line by line, and to run under validation.
   - `Release` is optimized with debug information and keeps the asserts. Use it for everyday work and for timing.
   - `Dist` has the flags of `Release` but compiles the asserts out. It is what games ship, so it is the one that shows what a player's build does.

   **You should see:** a result in each configuration after `cmake --build --preset <preset>-release` and `-dist`, in the same build folder.

   **If you do not see it:** if a command says that it knows no such preset, you wrote a configuration the table does not list; the three names are `-debug`, `-release` and `-dist`.

5. Find the results in the build folder `build/<preset>`. The programs and the libraries they load land in `bin/<Config>/`, the :term[static libraries]{id=static-library} in `lib/<Config>/`, and the :term[shader]{id=shader} tool in `tools/<Config>/`. A multi-config generator adds the configuration's folder to each of the three.

   ```mermaid caption="The build folder of one preset: programs, one static library per layer, the shader tool and the cache file, each in its own place under the build folder." alt="A tree with the build folder at the top. Its branches lead to the programs, with one folder for each configuration, to the static libraries, to the shader tool and to a cache file."
   flowchart TD
       B["build/PRESET"] --> BIN["bin/CONFIG: StrataEditor, StrataRuntime, StrataCLI, StrataTests"]
       B --> LIB["lib/CONFIG: one static library per layer, such as Strata_Core"]
       B --> TOOLS["tools/CONFIG: StrataShaderTool"]
       B --> CACHE["CMakeCache.txt"]
       B --> CC["compile_commands.json, Ninja presets only"]
   ```

   **You should see:** for `linux-debug`, the file `build/linux/bin/Debug/StrataEditor`, and `StrataTests` beside it. A Visual Studio solution sorts its projects into folders: "Strata/Layers" holds the engine's layers, "Vendor" the libraries, and a folder beside the layers the test script modules. Inside a project, a group of files named "Generated Shaders" holds the shaders compiled into the engine.

   **If you do not see it:** a configuration you never built has no folder. The Ninja presets also write `compile_commands.json`, a list of the compiler commands that :term[code editors]{id=code-editor} read to find your includes; the Visual Studio presets do not.

6. Run the tests with the test preset of the same name, omitting two labels.

   ```sh
   ctest --preset linux-debug -LE "gpu|perf" -j 8
   ```

   The option `-LE` omits the tests that carry a label, and `-j 8` runs eight at once. The `gpu` label marks tests that need a :term[graphics card]{id=gpu}, and `perf` marks timing tests for the reference machine; the [page on the test program](test-program.md) explains both.

   **You should see:** one line per test group, and a final line that says all tests passed.

   **If you do not see it:** the test preset prints the output of each failed test. A run that finds no tests is an error, so a wrong label fails instead of passing with nothing.

:::::

## Change the options

The options are cache variables, and the first one you set stays set. Each step below changes one, and the page names only the options a builder changes; the full table is in the reference on the build.

:::::steps

1. Choose the program switches and extras you need, and pass them with `-D` to the configure step.

   ```sh
   cmake --preset linux -DSTRATA_BUILD_TESTS=OFF -DSTRATA_BUILD_CLI=OFF
   ```

   `STRATA_BUILD_EDITOR`, `STRATA_BUILD_RUNTIME`, `STRATA_BUILD_CLI` and `STRATA_BUILD_TESTS` are on by default and decide which programs exist. `STRATA_ENABLE_TRACY` is off; on, it adds the hooks that the [page on profiling](../core/profiling.md) uses. `STRATA_WARNINGS_AS_ERRORS` is on, and you disable it only for a local experiment, because continuous integration (CI) always builds with it.

   **You should see:** a configure log without the programs you switched off, and a build that skips them.

   **If you do not see it:** check the spelling of each name. CMake stores an option with a wrong name anyway, and the log ends with the warning `Manually-specified variables were not used by the project`.

2. Know what the optional modules and the window backend do. `STRATA_WITH_PHYSICS`, `STRATA_WITH_AUDIO` and `STRATA_WITH_ANIMATION` leave a module out of the build, with its library; `STRATA_WITH_GLFW=OFF` swaps the window backend for one that opens nothing, so programs run headless. The editor needs every module and a window.

   **You should see:** a configure that stops with "The editor is a tool with every engine module and a window" when you switch one off while the editor is on.

   **If you do not see it:** add `-DSTRATA_BUILD_EDITOR=OFF` to the same command. The [page on the layers and registries](../core/layers-registries.md) says what a module is.

3. Know three more options, one sentence each. `STRATA_COMPILER_CACHE=ON` compiles through `ccache` or `sccache`, as CI does, and refuses the Visual Studio generators. `STRATA_PRECOMPILED_HEADERS` is on by default and builds with precompiled headers, which the compiler cache disables. The `STRATA_USE_*` options choose the instruction sets, such as `STRATA_USE_AVX2`; the [page on flags and portability](flags-portability.md) shows what each costs.

   **You should see:** with the cache on, the log line `Compiler cache:` that the configure step of the previous section described.

   **If you do not see it:** the error that starts `STRATA_COMPILER_CACHE needs` means that neither `ccache` nor `sccache` is installed; install one, or name it with `STRATA_COMPILER_CACHE_PROGRAM`.

4. Meet the trap of the cache. Configure `cmake --preset linux -DSTRATA_BUILD_RUNTIME=OFF`, then later `cmake --preset linux` alone. The cache still holds `OFF`, so the :term[runtime]{id=runtime} is still missing, and a plain configure does not bring it back.

    ```sh
    cmake --preset linux -DSTRATA_BUILD_RUNTIME=ON
    ```

    **You should see:** the runtime built again. The other ways out are `-U STRATA_BUILD_RUNTIME`, which removes the entry so that its default returns, and a fresh build folder.

    **If you do not see it:** open `CMakeCache.txt` in the build folder and search for the option's name: its line shows what the cache holds.

5. Make a second build folder for a variant, and one per agent when several work side by side.

    ```sh
    cmake --preset linux -B build/agent-docs -DSTRATA_WITH_AUDIO=OFF -DSTRATA_BUILD_EDITOR=OFF
    ```

    **You should see:** a new folder `build/agent-docs` next to `build/linux`, with its own cache and its own bin folder. The first folder is untouched.

    **If you do not see it:** two builds in one folder corrupt each other, so if you meet strange :term[link errors]{id=link-error} after two commands ran at once, delete that folder and configure again.

6. Configure again after you add or remove a :term[source file]{id=source-file}. Strata collects its sources with a glob that CMake evaluates at configure time.

    **You should see:** with the Visual Studio generator, a new file missing from the build you ran: the generator collects the files again during the build, yet it compiles with the old project. The file appears one build later.

    **If you do not see it:** a file in a folder that no layer owns fails the configure and names it. The build lists shaders one by one instead: each is an entry in `strata_add_shaders` in `Strata/CMakeLists.txt`.

:::::

## Run Debug builds under validation

A **validation layer** checks every call the program makes to Vulkan and reports misuse, such as a wrong image layout. Debug builds ask for the standard layer `VK_LAYER_KHRONOS_validation` by default; Release and :term[Dist]{id=dist} do not. When it is missing, the program warns and continues without it, so nothing fails, but the checks do not run. What the layer reports is the subject of the [page on debugging the graphics card's work](../gpu/debugging.md).

:::::steps

1. Install the layer for your system.

    ::::tabs{sync=os}
    :::tab[Windows]
    Install the Vulkan software development kit (SDK) from LunarG. Its installer registers the layer with the Vulkan loader, and you set nothing else.
    :::
    :::tab[Linux]
    Install the Vulkan SDK from LunarG, or your distribution's package for the standard validation layer. The layer must appear in the loader's layer list.
    :::
    :::tab[macOS]
    Install Homebrew's packages `molten-vk`, `vulkan-loader` and `vulkan-validationlayers`. The layer's manifest names its library without a folder, and the loader does not search for it in Homebrew's `lib`, so copy the manifest with the library's :term[full path]{id=absolute-path} and point `VK_ADD_LAYER_PATH` at the copy.

    ```sh
    mkdir -p build/_tools/vulkan-layers
    sed "s|\"library_path\": *\"[^\"]*\"|\"library_path\": \"$(brew --prefix)/lib/libVkLayer_khronos_validation.dylib\"|" "$(brew --prefix)/share/vulkan/explicit_layer.d/VkLayer_khronos_validation.json" > build/_tools/vulkan-layers/VkLayer_khronos_validation.json
    export VK_ADD_LAYER_PATH="$PWD/build/_tools/vulkan-layers"
    ```

    :::
    ::::

    The first command makes a folder. The second rewrites the line `library_path` of the manifest so that it holds the full path, and saves the result in that folder. The third names the folder for every program you start from this terminal.

    **You should see:** on macOS, a file `build/_tools/vulkan-layers/VkLayer_khronos_validation.json` whose `library_path` starts with the output of `brew --prefix`.

    **If you do not see it:** without the SDK or the packages, the next step prints a warning that the layer is not installed. A new terminal forgets `VK_ADD_LAYER_PATH`; export it again.

2. Start a Debug program and read its log for the line that names the graphics device.

    ```sh
    build/linux/bin/Debug/StrataEditor --headless --frames 3
    ```

    **You should see:** a line that starts with `Graphics device:` and ends with `, validation enabled`.

    **If you do not see it:** the warning `Vulkan validation requested but VK_LAYER_KHRONOS_validation is not installed` means the loader did not find the layer: the SDK is missing, or on macOS `VK_ADD_LAYER_PATH` has no value. The warning `could not be loaded` means the loader found a manifest it could not use; on macOS check the full path in the copy.

:::::

## Result

You have a build tree you can explain folder by folder. `build/<preset>` holds the cache, `bin/<Config>` the programs, `lib/<Config>` one static library per layer, `tools/<Config>` the shader tool, and a Ninja preset adds `compile_commands.json`. You can choose the preset for your system and the options for the variant. You can choose the configuration for the task: `Debug` to follow code and to validate, `Release` for everyday work and timing, `Dist` for what ships. You changed one without the cache catching you, and you ran a Debug program under validation.

## Variations

- **A cached Windows build.** Configure `windows-ninja` from a developer environment with the cache on, and build as before: `cmake --preset windows-ninja -DSTRATA_COMPILER_CACHE=ON`, then `cmake --build --preset windows-ninja-debug --parallel`. The compiler cache needs `sccache` or `ccache` on the path. CI builds this way.
- **A Dist build of every target.** Configure as usual and run `cmake --build --preset <preset>-dist --parallel`, then `ctest --preset <preset>-dist -LE "gpu|perf"`. A release starts the same way, and [releasing](releasing.md) does the rest.
- **A build without physics and audio.** The command is `cmake --preset linux -B build/nophysics -DSTRATA_WITH_PHYSICS=OFF -DSTRATA_WITH_AUDIO=OFF -DSTRATA_BUILD_EDITOR=OFF`. There is no editor in it, because the editor needs every module; the [page on CMake](cmake.md) shows how a module drops out.
- **A game maker who wants a newer engine than the release.** Clone the engine at the commit you want, with its submodules, and use the same preset and the `Release` configuration: the editor lands in `build/<preset>/bin/Release/`. The first configure downloads Slang into the cache of your user account, and later builds use it again.

## Summary

- A preset names a generator, a build folder `build/<preset>` and its build and test presets; pick the one of your system, then `-debug`, `-release` or `-dist`.
- Programs land in `bin/<Config>/`, static libraries in `lib/<Config>/`, the shader tool in `tools/<Config>/`, and the Ninja presets write `compile_commands.json`.
- Options are cache variables that survive a new configure: set one with `-D`, remove it with `-U`, or use a fresh folder, and configure again after adding or removing a source file.
- A Debug build uses the Vulkan validation layer when the loader finds it; on macOS Homebrew's layer needs a manifest copy named by `VK_ADD_LAYER_PATH`.

## Check yourself

1. You ran `cmake --preset linux -DSTRATA_BUILD_RUNTIME=OFF` last week. Today you run `cmake --preset linux` and build, and `StrataRuntime` is missing. Why, and what is the shortest fix?

   :::answer{tests="change-options"}
   The cache variable `STRATA_BUILD_RUNTIME` still holds `OFF`, because a configure without `-D` reads the cache. Run `cmake --preset linux -DSTRATA_BUILD_RUNTIME=ON`. Removing the entry with `-U` or making a fresh build folder also works.
   :::

2. You use Visual Studio 2022 and want an optimized build that keeps the asserts. Which two names do you use?

   :::answer{tests="choose-preset"}
   The configure preset `windows-vs2022` and the build preset `windows-vs2022-release`, which builds the `Release` configuration. `Dist` would also be optimized, but it compiles the asserts out.
   :::

3. Where is the test program of `linux-dist`?

   :::answer{tests="build-tree"}
   The path is `build/linux/bin/Dist/StrataTests`: the folder is the preset's name, then `bin`, then the configuration. A static library of the same build is in `build/linux/lib/Dist`.
   :::

4. In Visual Studio you add `Foo.cpp` to a layer's folder and build. The build succeeds, but the file is not compiled. Why?

   :::answer{tests="change-options"}
   CMake collects sources at configure time. The Visual Studio generator collects the files again during the build, yet it compiles with the project it already had. The file joins one build later. Configure again after adding a file.
   :::

5. On Linux without the Vulkan SDK you start the Debug editor. What does the log say, and does the program run?

   :::answer{tests="validation"}
   The editor warns that `VK_LAYER_KHRONOS_validation` is not installed and that only the NVRHI validation is used. The program runs, but the checks of the layer do not.
   :::

## Exercises

1. **Basic.** From a clean clone on your system, configure a preset, build `Debug`, and run the tests without the `gpu` and `perf` labels. Write down the build folder and the path of the test program.

   :::answer[Worked solution]{tests="choose-preset build-tree"}
   Run `git submodule update --init --recursive --depth 1`, then `cmake --preset <preset>`, `cmake --build --preset <preset>-debug --parallel` and `ctest --preset <preset>-debug -LE "gpu|perf" -j 8`. With `linux`, the folder is `build/linux` and the test program is `build/linux/bin/Debug/StrataTests`. The run ends with all tests passed.
   :::

2. **Medium.** Configure a second folder with `cmake --preset <preset> -B build/agent-nocli -DSTRATA_BUILD_CLI=OFF` and read the log. Find the Slang line, the compiler cache line, and the packaging line.

   :::answer[Worked solution]{tests="change-options"}
   The Slang line ends with `(cached)`, because the first configure stored the download. There is no compiler cache line unless you passed `-DSTRATA_COMPILER_CACHE=ON`. The packaging line reads `Strata packaging: the editor, the runtime and the CLI are not all built; no install rules`, because you switched the command line client off.
   :::

3. **Hard.** Add a configure preset `linux-cached` to `CMakePresets.json` that inherits `linux` and turns the compiler cache on, so that `cmake --preset linux-cached` needs no `-D`. On Windows or macOS, inherit your own preset and keep its condition.

   :::answer[Worked solution]{tests="change-options choose-preset" solution="tutorials/engineering/building/exercise-3.patch"}
   Add one entry to `configurePresets`, after `linux`:

   ```json
   {
   	"name": "linux-cached",
   	"displayName": "Linux (Ninja Multi-Config, compiler cache)",
   	"inherits": "linux",
   	"cacheVariables": { "STRATA_COMPILER_CACHE": "ON" }
   }
   ```

   The entry inherits the generator and the condition of `linux`, and `base` gives it the folder `build/linux-cached`. Configure it with `ccache` or `sccache` on the path: the log shows `Compiler cache:` with precompiled headers `OFF`.
   :::

## Where it lives in Strata

- `CMakePresets.json`: the configure, build and test presets.
- `CMakeLists.txt`: the guards against in-source builds and missing submodules, the options, and the editor's refusal.
- `CMake/StrataConfigurations.cmake`: the three configurations, C++20 without extensions, `compile_commands.json` and the output folders.
- `CMake/StrataCompilerOptions.cmake`: the compiler cache and its log line.
- `CMake/StrataSlang.cmake`: the Slang download and its `(cached)` line.
- `CMake/StrataPackaging.cmake`: the packaging line.
- `Strata/src/Platform/Vulkan/VulkanGraphicsDevice.cpp` and `Strata/src/Strata/Renderer/GraphicsModule.cpp`: the validation layer's request and its log lines.

## Further reading

- CMake documentation, "cmake-presets(7)": every field of a preset file; intermediate.
- CMake documentation, "cmake(1)": the options `--preset`, `-D`, `-U`, `-B` and `--build`; beginner.
- Khronos, "Vulkan Validation Layers": what the layer checks and how the loader finds it; intermediate.
