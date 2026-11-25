---
id: make/script-builds
title: "Building and shipping script modules"
description: "Build a game's scripts from a terminal and from an IDE, read the file that controls the build, and add a library of your own without breaking hot reload."
kind: how-to
size: M
tracks: [G]
needs: [make/project-coin-run, basics/tools|start/install]
time: 90
learn:
  - id: build-terminal
    text: build a project's scripts from a terminal with the strata preset and see the editor reload them
  - id: read-cmake
    text: explain each line of the Scripts/CMakeLists.txt that the editor writes
  - id: build-ide
    text: build the scripts from an IDE and explain why the preset stays out of version control
  - id: add-library
    text: add a static library beside Scripts and explain where a shared library must sit
since: 0.3.0
status: final
---

You build the scripts of your game outside the editor: in a terminal, in an **integrated development environment** (IDE), and with a library you wrote yourself. The editor builds them for you with **Ctrl+B**, so you build by hand to see what it does, to use a tool you like better, or to add code that is not a script. Before you start:

- A project whose scripts the editor built once, as [Your first script](first-script.md) did for Coin Run. That first build finds your compiler and writes the files this page uses. This page offers no project of its own: use your Coin Run, or download Checkpoint 4 at the end of [Ship the finished game](project-coin-run.md#ship-the-finished-game) and open it with **File ▸ Open Project...**. Then press **Ctrl+B** once, so that the editor writes `Scripts/CMakePresets.json`.
- A terminal and the habit of running a command in it, from [Install Strata](../start/install.md).
- The editor open on the project, so that you can watch it load what you build.

## What a module is

All the scripts of a game live in one **script module**, a single shared library file. Every `.cpp` and `.h` file below the project's `Scripts` folder is compiled into it. The editor and the exported game load that file, and your classes appear in the **Add Component** list.

The module never contains the engine. It talks to the engine through a small list of plain C functions, an **application binary interface** (ABI): the exact shape of the calls between two compiled programs. Strata's script interface is version 1, and new functions are only added at the end of its tables. A module built last year therefore still loads after the engine grows.

```mermaid caption="Your source files become one module. The engine loads a private copy of it, so a new build can replace the original while the game runs." alt="A flow from left to right. Your source files in the Scripts folder are built by CMake into one module, a shared library. The module talks through a C interface of version 1 to the engine, which is the editor or the exported game. A dotted arrow from the module shows that the engine runs a private copy of it."
flowchart LR
    A["Your .cpp and .h files in Scripts"] -->|"built by CMake"| B["The module: one shared library"]
    B <-->|"C interface, version 1"| C["The engine: editor or exported game"]
    B -.->|"a private copy is loaded"| D["The copy that runs"]
```

## The file that controls the build

CMake is a program that reads a text file named `CMakeLists.txt` and builds what it describes. The editor writes one into `Scripts` when it creates the project, and never replaces it afterwards. You may edit it, and you will in the exercise.

The next quote shows what the editor writes. Look at the last two lines: they are the whole recipe.

```cmake src="StrataEditor/src/Editor/ScriptProject.cpp#L219-L224" overload="1" from="cmake_minimum_required(VERSION 3.25)" to="strata_add_script_module({1} SOURCE_DIR" symbol="MakeScriptCMakeLists"
cmake_minimum_required(VERSION 3.25)
project({1} CXX)

set(STRATA_ENGINE_DIR "" CACHE PATH "The Strata folder, a source checkout or an installation (the editor sets it)")
find_package(StrataScriptCore CONFIG REQUIRED PATHS "${{STRATA_ENGINE_DIR}}/StrataScriptCore/CMake" NO_DEFAULT_PATH)
strata_add_script_module({1} SOURCE_DIR "${{CMAKE_CURRENT_SOURCE_DIR}}")
```

The editor completes the doubled braces, so for the project `CoinRun` the module is `CoinRunScripts`. Read the lines in order:

- `cmake_minimum_required` refuses a CMake older than 3.25, so an old tool fails at once with a clear message.
- `project` names the module and says that it holds C++.
- `set(STRATA_ENGINE_DIR ...)` declares a setting for the folder of Strata: a copy of the source or an installed release. The editor completes it when it builds, and the preset you meet below carries the same value.
- `find_package(StrataScriptCore ...)` reads the file `StrataScriptCore/CMake/StrataScriptCoreConfig.cmake` below that folder. It gives the build the headers of the script kit and the math library glm, and a build configuration named `Dist` beside `Debug` and `Release`. `NO_DEFAULT_PATH` means that no other copy on your machine can be found by mistake.
- `strata_add_script_module` makes a library of the kind that is loaded at run time (a CMake `MODULE`) from every `.cpp`, `.h` and `.hpp` file below the folder. It skips folders whose names start with a dot and build folders, and it adds the module's entry points.

The same function sets what a module needs to be safe. Only the entry points are visible outside the file. On Windows the C runtime is linked into the module, and a debug database lets a crash report name a line. Everything the module needs from the engine comes through the C interface, so the build never links the engine.

## Build from a terminal

The editor builds in its own way: its generator (the kind of build files CMake writes for your compiler), its configuration and an output folder it watches, `.strata/Scripts/Bin`. A build by hand must use the same settings, or the module lands somewhere the editor never looks. The editor wrote them into `Scripts/CMakePresets.json` as a preset, a named set of CMake settings, called `strata`, so you only name the preset.

The configuration is the one the engine itself was built with, because a module must match the engine that loads it. The Strata you installed is the shipping build, so the preset builds `Dist`, and the compile lines name a folder `Dist` inside `.strata/Scripts/IDE`. An engine you built yourself in `Release` builds the scripts in `Release`.

:::::steps

1. Open a terminal in the project's `Scripts` folder.

   ::::tabs{sync=os}
   :::tab[Windows]
   Open the folder in File Explorer, click its address bar, type `powershell` and press **Enter**.
   :::
   :::tab[Linux]
   Open the folder in your file manager and choose "Open in Terminal", or run `cd` with the folder's path in a terminal.
   :::
   :::tab[macOS]
   Open Terminal, type `cd ` and drag the `Scripts` folder into the window, then press **Enter**. <!-- markdownlint-disable-line MD038 -->
   :::
   ::::

   **You should see:** a prompt whose folder ends in `Scripts`.

   **If you do not see it:** you are in the project's folder one level up. Type `cd Scripts`.

2. Check that the terminal finds CMake.

   ```sh
   cmake --version
   ```

   **You should see:** a line such as `cmake version 3.31.0`, at least 3.25.

   **If you do not see it:** the terminal does not know CMake. Open `CMakePresets.json` in a text editor: its `cmakeExecutable` line names the CMake that the editor uses, and you may run that file by its whole path. On Windows the "Developer PowerShell" of Visual Studio also finds a CMake.

3. Configure the build with the preset.

   ```sh
   cmake --preset strata
   ```

   **You should see:** CMake prints the lines of its configure step and ends with `-- Build files have been written to:` followed by a path that ends in `.strata/Scripts/IDE`.

   **If you do not see it:** CMake says that there is no preset named `strata`, and the file `CMakePresets.json` is missing. Press **Ctrl+B** once in the editor: the build that finds your compiler writes the file.

4. Build the module with the same preset.

   ```sh
   cmake --build --preset strata
   ```

   **You should see:** one compile line for each of your `.cpp` files, then a link line, then the end of the run with no error. The lines name the configuration `Dist`, as the start of this section explains. The file `CoinRunScripts.dll` (`.so` on Linux, `.dylib` on macOS) is new in `.strata/Scripts/Bin`.

   **If you do not see it:** a line with `error` names a file and a line, as the :term[Problems panel]{id=problems-panel} does. Fix that line and run the build again; CMake compiles only the files that changed.

5. Switch to the editor and look at the Console.

   **You should see:** the line `Reloaded script module 'CoinRunScripts' (1 class)`, with the number of classes you have. The editor watches `.strata/Scripts/Bin`, so it loads the new file by itself, exactly as it does after its own build.

   **If you do not see it:** you changed nothing, so the build left the module as it was. Add a space in a script, save and build again, or look in `.strata/Scripts/Bin` for the file time.

:::::

## Build from an IDE

An IDE is a code editor with a build button. Both of the common ones read `CMakePresets.json`, so they build with the settings that the editor uses. They also complete names and show errors as you type, a feature that Visual Studio calls IntelliSense.

:::::steps

1. Open the `Scripts` folder, not the project folder, in your IDE. In Visual Studio use "File > Open > Folder...". In Visual Studio Code, install the "CMake Tools" and "C/C++" extensions first, then use "File > Open Folder...".

   **You should see:** the IDE reads the folder and offers the preset `strata`, shown as `Strata (<generator>, <configuration>)` with the generator and the configuration of your editor.

   **If you do not see it:** the IDE opened the project's folder one level up and found no `CMakeLists.txt`. Close the folder and open `Scripts` itself.

2. Choose the `strata` preset in the IDE's configuration list (Visual Studio Code: the status bar at the bottom), then build the project with the IDE's build command.

   **You should see:** the same compile and link lines as in the terminal, in the IDE's own output window. The module is written to `.strata/Scripts/Bin` and the Console of the editor reports `Reloaded script module`.

   **If you do not see it:** the IDE built with another configuration than the preset. Select the preset again, and delete the cache of the build in the IDE's CMake menu so that it configures from the preset again.

:::::

The preset holds paths of this machine: your compiler, the folder of the engine and your user name inside both. The editor therefore writes a `.gitignore` beside it that lists `/CMakePresets.json`, so a copy of the project in version control stays free of them. A teammate gets their own file when their editor first builds, and the editor rewrites it when the engine or its compiler changes. To keep a file you edited by hand, remove the vendor entry named `strata.dev/editor` from it; the editor then leaves it alone.

## Result

You can now build the module by hand and in an IDE, and both produce the file the editor loads. You know what the lines of `CMakeLists.txt` do and where the build's folders are: `.strata/Scripts/Build` for the editor, `.strata/Scripts/IDE` for the preset, `.strata/Scripts/Bin` for the module.

## Variations

### A plain build, as a check on another machine

The comment in the generated file gives another recipe: `cmake -S Scripts -B build -DSTRATA_ENGINE_DIR=<Strata folder>`, then `cmake --build build`. That build uses the default generator and configuration of the machine, and the module lands in the `build` folder, which the editor does not watch. It is no way to get a module into the editor. It does check that your code compiles with another compiler, and that is worth doing.

### Another compiler

A script that compiles on your machine may fail on another. The Windows compiler accepts a use of `std::string` or `std::vector` without the include that names it, because another header already pulled it in. GCC on Linux and Clang on macOS refuse it, with an error that names the missing type. Add the include the missing name belongs to: `<string>`, `<vector>`, `<cstdint>`. Warnings differ too, so read them on each system before you ship.

The module must be built with the compiler family and configuration of the engine that loads it. That is why the editor's preset records both, and why you copy the preset's values to a build you script yourself.

### A project in a deep folder on Windows

Visual Studio builds through a program that logs the files it touches, and it cannot create a log at a path longer than 259 characters. A project in a deep folder would fail with an error that does not name the cause. The editor measures this before it builds. When the build folder inside the project would be too deep, it builds in your user data instead: in the `Builds` folder of `Strata`, in a folder named by a hash of the project's folder. The first line of the build log says so, and the preset's folder moves there too.

Only when even that folder is too deep does the editor refuse the build. The error then names a shorter folder to move the project to, below your home folder.

### Libraries

Sooner or later you want code that is not a script: a library for a file format, or a few functions you share between games. A **static library** is a file of compiled code that the build copies into the module, so afterwards the module needs nothing beside it. A **shared library** stays a separate file that the system loads next to the module when it starts.

Prefer a static library. A shared one adds a way to fail: the system must find it.

- On Windows, the system looks in the folder of the module file, and also when the editor runs a copy: it searches the original's folder, never the current folder or `PATH`. Put the `.dll` in `.strata/Scripts/Bin`, or let the build copy it there.
- On Linux and macOS, the loader finds a library through the module's run-time search path (RUNPATH), a list of folders stored in the file. The default that CMake writes is an absolute path, and it works. The popular form `$ORIGIN` (macOS: `@loader_path`) does not, because it means the folder of the file that is loaded.

The reason is :term[hot reload]{id=hot-reload}. The editor never loads your module from `.strata/Scripts/Bin`. It copies the file to a private folder in your user data and loads the copy, so that a build can replace the original at any moment. With `$ORIGIN` the loader looks in the copy's folder. Your `libfoo.so` is beside the original, not the copy, and the load fails.

A game exported from the editor loads its module in place, so the same setting works there, and fails only while you edit.

To add a static library of your own, keep its folder beside `Scripts`, never under it. Every `.cpp` and `.h` file below `Scripts` belongs to the module itself, so the build would compile library sources there twice. Five lines of CMake do the work:

- `add_library(Triple STATIC Triple.cpp)`, in the library's own `CMakeLists.txt`, makes the library from its sources.
- `target_include_directories(Triple PUBLIC ...)` lets every target that links it write `#include "Triple.h"`.
- `set_target_properties(Triple PROPERTIES POSITION_INDEPENDENT_CODE ON ...)` builds the library as the module is built: position independent code, and on Windows the same C runtime. Without it the link fails.
- `add_subdirectory(<library folder> <build folder>)`, in `Scripts/CMakeLists.txt`, reads the library's file. CMake refuses a source folder outside `Scripts` unless you also give a folder in the build tree.
- `target_link_libraries(<module> PRIVATE Triple)` copies the library into the module. Write it after `strata_add_script_module`, because the module's target must exist.

One more trap waits. **Play** builds first only when a file below `Scripts` changed, so after an edit in the library's folder Play runs the old module. Press **Ctrl+B** instead: **Scripts ▸ Build Scripts** always builds.

## Summary

- A terminal build with `cmake --preset strata` and `cmake --build --preset strata` writes the module where the editor watches, and the editor reloads it.
- `CMakeLists.txt` names the engine folder, reads the `StrataScriptCore` package, and compiles every source below `Scripts` into one module with `strata_add_script_module`.
- An IDE builds the same way through the `strata` preset; the preset holds machine paths, so a `.gitignore` keeps it out of version control.
- A static library beside `Scripts` is linked with `target_link_libraries` after the module is declared; a shared library must sit next to the module, and `$ORIGIN` fails under hot reload.

## Check yourself

1. You run `cmake -S Scripts -B build` and `cmake --build build` as the comment in `CMakeLists.txt` says. The build succeeds, but the editor shows no reload. Why?

   :::answer{tests="build-terminal"}
   The module landed in the `build` folder, and the editor watches only `.strata/Scripts/Bin`. The preset passes that folder as the output folder, with the editor's generator and configuration.
   :::

2. What happens if you delete the `find_package` line?

   :::answer{tests="read-cmake"}
   The next line fails, because the function `strata_add_script_module` is not defined: that package supplies it, with the script kit's headers and glm.
   :::

3. Why does the editor write `/CMakePresets.json` into a `.gitignore`?

   :::answer{tests="build-ide"}
   The file holds the compiler and engine paths of one machine. Another machine needs different values, which its own editor writes.
   :::

4. A module links `libfoo.so` through a RUNPATH of `$ORIGIN`. It loads when you run the exported game and fails in the editor. Why?

   :::answer{tests="add-library"}
   The editor loads a private copy of the module, so `$ORIGIN` names the copy's folder, which has no `libfoo.so`. The exported game loads the module in place.
   :::

## Exercises

1. **Basic.** Add a static library `Triple` beside `Scripts` whose function `Triple(int value)` returns `value * 3`, and call it from a script `TripleLog` that logs `Triple(14)` when it starts. Predict the Console line, build with **Ctrl+B**, then change the factor to 4 and build while the game plays.

   :::answer[Worked solution]{tests="add-library" solution="tutorials/make/script-builds/exercise-1.tutorial.json"}
   Create `Libraries/Triple` with `Triple.h`, `Triple.cpp` and a `CMakeLists.txt` of four lines.

   ```cmake
   add_library(Triple STATIC Triple.cpp)
   target_include_directories(Triple PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}")
   # A static library is copied into the module, so it is built as the module is: position independent code and the same C runtime.
   set_target_properties(Triple PROPERTIES POSITION_INDEPENDENT_CODE ON MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
   ```

   The first line makes the library, the second shares its folder for `#include`, the third is a comment, and the fourth sets two properties. A library copied into a module needs position independent code and the C runtime that the module uses.

   Then add `add_subdirectory` and `target_link_libraries` to `Scripts/CMakeLists.txt` as above. The script holds `#include "Triple.h"` and `Log::Info("Triple of ", Value, " is ", Triple(Value));` in `OnCreate`, with `Value` a field of 14.

   The Console shows `Triple of 14 is 42`, since 14 times 3 is 42. After the change to 4, the Console reports a reload and the next start shows 56.

   The download holds the files and two command scripts, which create no files. Copy `Libraries` and `Scripts` into your project and run `stage-1.commands.json`: it builds, plays and shows 42. Then open `Libraries/Triple/Triple.cpp` of your project in your code editor, change the 3 to 4 and save; the folder `stage-2` holds the file as it then reads. Run `stage-2.commands.json`. It plays the old module, builds while the game plays and starts again, and the Console shows 56.

   Save the file in your editor even if you copy the `stage-2` file over yours instead. A copied file keeps the time of the archive, which is older than your first build. The build then finds nothing changed: the Console says the module was up to date, and both starts show 42.
   :::

2. **Medium.** On Linux you build with `cmake -S Scripts -B build` and have no preset. Where is the module file, and what must you add to put it where the editor looks?

   :::answer{tests="build-terminal"}
   The module is in the top of the `build` folder, since nothing sets an output folder. Add `-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=<project>/.strata/Scripts/Bin` to the configure command, with the engine's generator and configuration; the preset does this for you.
   :::

3. **Hard.** A module on Linux links a shared library of a partner. You want a layout that works in the editor and in the exported game. Choose one.

   :::answer{tests="add-library"}
   Link with an absolute RUNPATH, which CMake writes by default into a build tree, or link the partner's code statically if it offers a static library. Both work with the private copy. For the export, check that the library is shipped beside the module, as [Exporting and shipping](export.md) describes for the game's files.
   :::

## Where it lives in Strata

- `StrataEditor/src/Editor/ScriptProject.cpp`: writes the project's `CMakeLists.txt` and the example script.
- `StrataEditor/src/Editor/ScriptBuild.cpp`: the arguments of the editor's two CMake runs, the build folders, the long path rule and `CMakePresets.json`.
- `StrataScriptCore/CMake/StrataScriptModule.cmake`: `strata_add_script_module` and the settings it gives a module.
- `StrataScriptCore/CMake/StrataScriptCoreConfig.cmake`: the package that a game project finds.
- `StrataScriptCore/Include/StrataScript/ScriptABI.h`: the C interface and its version number.

## Further reading

- The CMake tutorial, on cmake.org: how a `CMakeLists.txt`, libraries and presets work (beginner to intermediate).
- The documentation of `target_link_libraries` and of the RPATH properties of CMake (intermediate).
