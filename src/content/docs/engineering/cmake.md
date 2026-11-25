---
id: engineering/cmake
title: "Inside Strata's CMake"
description: "How Strata's CMake turns the layer table into one library per layer, and proves twice that exported games contain no tooling."
kind: internals
size: L
tracks: [E]
needs: [core/layers-registries]
time: 95
learn:
  - id: usage-requirements
    text: explain which of PUBLIC, PRIVATE and INTERFACE a link needs and what a wrong choice leaks to its users
  - id: owner-target
    text: find the target that a source file builds into and its entry in LayerLibraries.json
  - id: read-error
    text: predict the configure error of a file in no layer or of a forbidden link, and fix its cause
  - id: no-tooling
    text: explain how Strata proves twice that a game contains no tooling
  - id: add-correctly
    text: add a source file, a folder or a vendor library without widening a MayInclude row
since: 0.4.0
status: final
---

A :term[build system]{id=build-system} turns a tree of :term[source files]{id=source-file} into programs. Strata's :term[CMake]{id=cmake} does one more job: it turns the :term[layer table]{id=layer-table} into the build, so that the architecture's rules hold because the targets are made that way. It makes one library for each layer, links each library only to the layers its row allows, and keeps the tooling out of every game. This page teaches how: the targets and what they pass on, the functions that read `Layers.json`, the checks that run at the end of configure, and the check of the :term[runtime's]{id=runtime} linker map. :term[Compiler]{id=compiler} flags, generated code and the vendor folder have their own pages; the rules of the table are taught in [Layers, registries and the composition root](../core/layers-registries.md).

## The problem and how engines solve it

A :term[game engine]{id=game-engine} has hundreds of source files and several programs: a runtime that plays games, an editor, a command-line client and a test program. Each program needs some files and must not contain others. The build system must say, for each program, which files it contains, which folders its compiler searches for :term[headers]{id=header}, and which definitions the code sees.

Writing that for each program by hand does not last. A new folder of headers must reach every program that uses it, and a new vendor library must reach every file that includes it. CMake solves this with **targets**. A target is a named thing to build, such as a library or a program, and it carries its own include folders, definitions and links. A program that links a target receives what the target says its users need.

The things a target hands to its users are its **usage requirements**. The keywords `PUBLIC`, `PRIVATE` and `INTERFACE` say who receives them.

The second problem is harder. A target graph lets any file reach any other, so nothing yet stops physics code from including a :term[renderer]{id=renderer} header, or a game from containing the editor's code. Engines enforce their layers in five ways, and each catches what the one before it can miss.

| Approach | What it catches | What it misses |
| --- | --- | --- |
| Convention | A reviewer who knows the rule | Everything else; people forget |
| Include checker | A forbidden `#include` line, read from the text | A dependency that reaches the program through a link, not an include |
| Separate libraries | A file that uses a symbol of a layer it does not link: the link fails | A header-only use, which needs no symbol |
| Link-closure check | A target that reaches a forbidden library through any chain of links | What the :term[linker]{id=linker} really puts into the program |
| Linker-map check | The objects and libraries that are in the finished program | Nothing at that point, once the map is known to be complete |

Strata uses all five. The conventions are in `AGENTS.md`, and `Architecture.Layering` is the include checker. CMake makes the separate libraries from the table itself. A walk at the end of configure is the closure check, and a test reads the runtime's linker map. The cost of the proof that games contain no tooling falls on the build, not on the people who write code.

## The map: three steps and the target graph

A build has three steps, and each reads and writes files. **Configure** runs CMake, which reads the `CMakeLists.txt` files and the options, and writes the build files, the cache in `CMakeCache.txt` and Strata's own outputs. **Build** runs the compiler and the linker through those files. **Test** runs the programs the build made. A preset is one name for the options of a step, as [Your first change](../core/first-change.md) showed.

```mermaid caption="Configure, build and test as three steps. Each step reads files and writes files, and the later steps read what the earlier ones wrote." alt="Three boxes in a row for configure, build and test. Configure reads the source tree, the layer table and the options, and writes the cache, the library description and the shader list. Build reads those and writes programs and libraries in the bin folder. Test reads the programs and the library description."
flowchart LR
  subgraph C[Configure]
    direction TB
    c1[CMakeLists.txt, CMake/*.cmake, Layers.json, options] --> c2[CMakeCache.txt, build files, LayerLibraries.json, ShaderEntries.txt]
  end
  subgraph B[Build]
    direction TB
    b1[build files, sources] --> b2[bin/Config: programs, StrataRuntime.map]
  end
  subgraph T[Test]
    direction TB
    t1[bin/Config, LayerLibraries.json] --> t2[pass or fail]
  end
  C --> B --> T
```

Configure runs when you ask for it and when a file it read has changed, which includes `Layers.json` and the folders that a :term[glob]{id=glob} read. A mistake in this step shows as a message that names the file, and the message of the rules below says how to fix it. Cached options are the usual surprise: `-DSTRATA_WITH_AUDIO=OFF` stays in `CMakeCache.txt` until you change it, so a later configure without the flag still leaves audio out.

The programs and libraries form a graph, and a link is an arrow.

```mermaid caption="The targets of the build. The editor, the runtime and the test program link a game's libraries; only tools link the tooling libraries. The runtime must reach none of the marked ones." alt="A graph of targets. The test program, the editor and the runtime link the game interface target, and the command-line client links only the network layer. The tooling interface target links the three tooling layer libraries, which the test program and the tool libraries use. The game interface target links the runtime layer libraries, which link the vendor libraries. The runtime must reach none of the tooling layers, tool-only vendor libraries or editor libraries."
flowchart TB
  Runtime[StrataRuntime]
  Editor[StrataEditor] --> EUI[StrataEditorUI] --> ECore[StrataEditorCore]
  CLI[StrataCLI] --> CLILib[StrataCLILib]
  Tests[StrataTests]
  Game([Strata: INTERFACE])
  Tool([StrataTooling: INTERFACE])
  TL1[Strata_AssetPipeline]
  TL2[Strata_Network]
  TL3[Strata_ImGui]
  Tool --> TL1
  Tool --> TL2
  Tool --> TL3
  Runtime --> Game
  ECore --> Game
  ECore --> TL1
  ECore --> TL2
  EUI --> TL3
  CLILib --> TL2
  Tests --> Game
  Tests --> Tool
  Game --> RL[Strata_Core ... Strata_Engine, 16 runtime layers]
  RL --> V1[glm, EnTT, spdlog, nvrhi, box3d, miniaudio]
  TL1 --> V2[imgui, ImGuizmo, cgltf, zstd_compress, nfd]
  TL3 --> V2
  EUI --> V2
  Runtime -. forbidden .-> TL1
  Runtime -. forbidden .-> TL2
  Runtime -. forbidden .-> TL3
  Runtime -. forbidden .-> V2
  Runtime -. forbidden .-> ECore
```

Two interface targets name what programs link. `Strata` is every layer a game contains, and `StrataTooling` is the layers only tools contain. The runtime links `Strata` alone, the test program links both, and the editor's libraries link the :term[tooling layers]{id=tooling-layer} they use. A third kind of target is a script module, built against `StrataScriptCore` and never against the engine, as [Scripting](../scripting/loading.md) explains.

## Targets and usage requirements

The 19 layers make 19 targets, and each must pass the right things to its users. Take a toy of three libraries and a program, and ask what the program sees.

```cmake
cmake_minimum_required(VERSION 3.25)
project(Toy CXX)

add_library(Base STATIC base.cpp)
target_include_directories(Base PUBLIC include/base)

add_library(Mid STATIC mid.cpp)
target_include_directories(Mid PUBLIC include/mid)
target_link_libraries(Mid PUBLIC Base)

add_library(Fast INTERFACE)
target_compile_definitions(Fast INTERFACE TOY_FAST=1)

add_executable(Game main.cpp)
target_link_libraries(Game PRIVATE Mid Fast)
```

1. **Lines 4–5:** `Base` is a :term[static library]{id=static-library} whose include folder is `PUBLIC`: its own files and its users both see it.
2. **Line 9:** `Mid` links `Base` `PUBLIC`; this is the line that leaks.
3. **Lines 11–12:** `Fast` has no files, only a definition for its users.
4. **Line 15:** `Game` links `Mid` and `Fast` `PRIVATE`, because nothing links `Game`.

`Base` offers `base.h` and `Mid` offers `mid.h`. `mid.cpp` includes `base.h` and uses it only inside. The link of `Mid` to `Base` says `PUBLIC`, so `Base`'s include folder is a usage requirement that `Mid` passes on. `Game` receives both folders, and `main.cpp` can include `base.h` although the author of `Mid` never meant it as part of `Mid`'s interface.

The three keywords say who receives a requirement. `PUBLIC` means the target itself and its users. `PRIVATE` means only the target itself. `INTERFACE` means only its users. With `target_link_libraries(Mid PRIVATE Base)`, `main.cpp` no longer finds `base.h`, and the compile fails where the leak would have hidden.

For a static library the linker still sees `Base`, because the objects of `Mid` need it, but the include folder and the definitions stay inside `Mid`.

An **interface library** is a target with no files to compile. It only holds usage requirements for its users, such as `Fast` above. A program that links `Fast` receives `TOY_FAST=1` and nothing else. CMake knows more kinds of library than this page needs; four matter here.

- A static library is an archive of objects that the linker copies from. Strata makes one for each layer that has code.
- A :term[shared library]{id=shared-library} is a file that a program loads when it runs. Strata makes them only for a few test helpers.
- A module library is a file that a program loads by name, with no link at build time. Strata makes one for each script module.
- An interface library has no file at all.

Two more tools complete the picture. A **generator expression** is text in the form `$<...>`. CMake evaluates it when it writes the build files, not when it reads the line, so it can depend on the configuration: `$<$<CONFIG:Dist>:ST_DIST>` is `ST_DIST` in a :term[Dist]{id=dist} build and nothing otherwise. A `SYSTEM` include folder tells the compiler to treat its headers as the system's. Their warnings stay quiet, so warnings as errors apply to Strata's own code only.

**`EXCLUDE_FROM_ALL`** marks a target that the plain build command skips; it builds only when something asks for it or depends on it. The tooling layers carry it, so a build that goes only for the game programs does not compile the asset pipeline.

:::why[Layers link PUBLIC, most vendor libraries PRIVATE]
A layer's header may include a header of a layer below it, so every user of the layer needs the lower include folders: its links to the layers in its `MayInclude` are `PUBLIC`. A vendor library is `PRIVATE` unless the layer's headers show its types. Physics links `box3d` `PRIVATE`, so game code that links physics receives no `box3d` include folder; `Core` links `glm` and `EnTT` `PUBLIC`, because its headers use them. The cost is that `PUBLIC` layer links do not stop a wrong include by themselves, since every lower folder is visible. `Architecture.Layering` closes that gap by reading the include lines.
:::

## The contract: the layer table is the build

The table in `StrataTests/Architecture/Layers.json` is read twice: by the tests, and by CMake. So what the table says about a layer is true of its library.

:::rule[One table, no second list]
Every source under `Strata/src` is in the library of the one layer whose `Paths` match it and whose `Exclude` does not. Each library links the built layers of its `MayInclude` and nothing else of the engine. The reason is that a library list kept by hand drifts from the table, and a drifted list is a rule that nothing enforces. Never widen `MayInclude` to make an include pass: invert the dependency, as [Layers, registries and the composition root](../core/layers-registries.md) teaches.
:::

The contract has four parts. A new source file needs a configure before it is in any library. A new folder needs a pattern in some layer's `Paths`. A vendor library needs a `strata_layer_link` row. A game program never links a tooling layer, and two checks prove it.

## A toy of the ownership loop

The core of the layer libraries is a loop: for each source file, find the layers whose patterns match it, and demand exactly one. The toy below does that with `std::regex` for four layers and five files. The toy turns a :term[glob]{id=glob} into a :term[regular expression]{id=regular-expression}. Read the printed pattern first, then check which file fails and how.

```cpp sketch="engineering-cmake-owners.cpp"
// A toy of the ownership loop of strata_add_layer_libraries: globs become regular expressions, and every source
// file must match exactly one layer.
#include <iostream>
#include <regex>
#include <string>
#include <vector>

struct Layer
{
	std::string Name;
	std::vector<std::string> Paths;
	std::vector<std::string> Exclude;
};

// '**/' is any directories or none, '**' anything, '*' and '?' stay within one path component.
static std::string GlobToRegex(const std::string& glob)
{
	std::string regex = "^";
	for (size_t i = 0; i < glob.size(); i++)
	{
		if (glob.compare(i, 3, "**/") == 0)
		{
			regex += "(.*/)?";
			i += 2;
		}
		else if (glob.compare(i, 2, "**") == 0)
		{
			regex += ".*";
			i += 1;
		}
		else if (glob[i] == '*')
			regex += "[^/]*";
		else if (glob[i] == '?')
			regex += "[^/]";
		else if (std::string("\\.+^$()[]{}|").find(glob[i]) != std::string::npos)
			regex += std::string("\\") + glob[i];
		else
			regex += glob[i];
	}
	return regex + "$";
}

static bool AnyMatches(const std::vector<std::string>& globs, const std::string& file)
{
	for (const std::string& glob : globs)
	{
		if (std::regex_match(file, std::regex(GlobToRegex(glob))))
			return true;
	}
	return false;
}

int main()
{
	const std::vector<Layer> layers = {
		{ "Core", { "Strata/Core/**" }, { "Strata/Core/Application.*" } },
		{ "App", { "Strata/Core/Application.*" }, {} },
		{ "Audio", { "Strata/Audio/**" }, {} },
		{ "Extra", { "Strata/Audio/*.h" }, {} },
	};
	const std::vector<std::string> files = {
		"Strata/Core/StringUtils.h", "Strata/Core/Application.cpp", "Strata/Audio/Mixer.cpp",
		"Strata/Audio/AudioClip.h", "Strata/Video/Player.cpp",
	};

	std::cout << GlobToRegex("Strata/Core/Application.*") << "\n";
	for (const std::string& file : files)
	{
		std::string owners;
		int count = 0;
		for (const Layer& layer : layers)
		{
			if (AnyMatches(layer.Paths, file) && !AnyMatches(layer.Exclude, file))
			{
				owners += (count == 0 ? "" : ", ") + layer.Name;
				count++;
			}
		}
		if (count == 0)
			std::cout << file << " is in no layer\n";
		else if (count > 1)
			std::cout << file << " is in several layers (" << owners << ")\n";
		else
			std::cout << file << " belongs to " << owners << "\n";
	}
	return 0;
}
```

```text output-of="engineering-cmake-owners.cpp"
^Strata/Core/Application\.[^/]*$
Strata/Core/StringUtils.h belongs to Core
Strata/Core/Application.cpp belongs to App
Strata/Audio/Mixer.cpp belongs to Audio
Strata/Audio/AudioClip.h is in several layers (Audio, Extra)
Strata/Video/Player.cpp is in no layer
```

1. **Lines 16–41:** `GlobToRegex` reads the glob from left to right and writes the matching regular expression.
2. **Lines 43–51:** a file matches a layer's list when any of its globs does.
3. **Lines 55–60:** the layers of the toy; `Extra` is a deliberate clash with `Audio`.
4. **Lines 67–85:** the loop counts the owners of each file, as the real one does.

The first line shows that `.` becomes `\.`, so only a real dot matches, and `*` becomes `[^/]*`, so it never crosses a folder. `StringUtils.h` belongs to `Core`, and `Application.cpp` matches `Core` by its path but is excluded by `Core`'s `Exclude`, so it belongs to `App` alone. `AudioClip.h` matches two layers, and `Player.cpp` matches none. The real code treats both as errors at configure time.

The real code differs from the toy in four ways. It reads the table from :term[JSON]{id=json}, it skips files of other platforms, it uses CMake's regular expressions, and it then makes libraries.

## The root file

Configure starts at the root `CMakeLists.txt`. It guards the build, declares options, includes helper modules and adds the project folders in an order that matters. Look first at the two guards.

```cmake src="CMakeLists.txt#L9-L17"
if(PROJECT_SOURCE_DIR STREQUAL PROJECT_BINARY_DIR)
	message(FATAL_ERROR "In-source builds are not supported. Configure with a preset, e.g. `cmake --preset windows`.")
endif()

if(NOT EXISTS "${PROJECT_SOURCE_DIR}/Strata/vendor/glfw/CMakeLists.txt")
	message(FATAL_ERROR "Third-party submodules are missing. Run `git submodule update --init --recursive --depth 1`.")
endif()

list(APPEND CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}/CMake")
```

The two guards print the fix in their messages. An in-source build, where the source and the build folder are the same, would mix generated files with sources, so configure fails and names the preset to use. Missing :term[submodules]{id=submodule} fail with the command that fetches them. Failing at once beats a build that stops later with an unrelated "file not found".

The options come next. Search for the optional modules, and for the guard that refuses an editor build when one of them is off.

```cmake src="CMakeLists.txt#L25-L48"
# The optional engine modules (their layers' "Option" in StrataTests/Architecture/Layers.json): a game without one builds
# without its layer and vendor library. Code tests ST_WITH_PHYSICS (and so on), a definition every engine target gets.
# The editor is a tool with every module.
option(STRATA_WITH_PHYSICS "Build the physics module (box3d)" ON)
option(STRATA_WITH_AUDIO "Build the audio module (miniaudio)" ON)
option(STRATA_WITH_ANIMATION "Build the animation module" ON)
# The window backend (Strata/src/Platform/GLFW). Off: the engine has no window system (Platform/NoWindow: Window::Create
# opens nothing), so its programs run headless only: the configuration a console port starts from, which CI builds
# (Docs/DeveloperGuide.md, "Platform seams"). Code tests ST_WITH_GLFW, a definition like ST_WITH_PHYSICS.
option(STRATA_WITH_GLFW "Build the GLFW window backend" ON)
set(strataAbsentModules "")
foreach(module IN ITEMS PHYSICS AUDIO ANIMATION)
	if(NOT STRATA_WITH_${module})
		list(APPEND strataAbsentModules "STRATA_WITH_${module}")
	endif()
endforeach()
if(NOT STRATA_WITH_GLFW)
	list(APPEND strataAbsentModules "STRATA_WITH_GLFW")
endif()
if(strataAbsentModules AND STRATA_BUILD_EDITOR)
	list(JOIN strataAbsentModules ", " strataAbsentModules)
	message(FATAL_ERROR "The editor is a tool with every engine module and a window: configure with -DSTRATA_BUILD_EDITOR=OFF to build without "
		"${strataAbsentModules}.")
endif()
```

1. **Lines 28–30:** the three optional modules, each an option that is `ON` by default and that names the layer in `Layers.json` through its `Option` field.
2. **Line 34:** the window backend is an option too; off, the engine has no window system and its programs run headless.
3. **Lines 35–43:** the loop collects the names of the options that are off.
4. **Lines 44–48:** the editor is a tool with every module and a window, so a configure that turns a module off must also turn the editor off. The message gives the flag.

```cmake src="CMakeLists.txt#L66-L91"
add_subdirectory(Strata/vendor)
add_subdirectory(StrataScriptCore)
add_subdirectory(Strata)

if(STRATA_BUILD_EDITOR)
	add_subdirectory(StrataEditor)
endif()

if(STRATA_BUILD_RUNTIME)
	add_subdirectory(StrataRuntime)
	# Games contain no tooling: neither a tooling layer nor what only tools link (StrataRuntime.NoTooling checks the
	# linked executable too). Checked once every directory below has been added (StrataCLILib comes later).
	strata_check_link_closure(StrataRuntime FORBID imgui ImGuizmo nfd cgltf zstd_compress StrataEditorCore StrataEditorUI StrataCLILib doctest)
endif()

if(STRATA_BUILD_CLI)
	add_subdirectory(StrataCLI)
endif()

# The installed layout and the release archives (cmake --install, cpack).
include(StrataPackaging)

if(STRATA_BUILD_TESTS)
	enable_testing()
	add_subdirectory(StrataTests)
endif()
```

1. **Lines 66–68:** the vendor libraries come first, then the script software development kit (SDK), then the engine, so that every later folder can link what the earlier ones made.
2. **Lines 74–79:** the runtime is added, and its link-closure check is requested. The list names the targets games must never reach.
3. **Line 78:** the check is deferred, because `StrataCLILib` does not exist yet when the line runs.
4. **Lines 86–90:** packaging and tests come last, so the tests can use every target.

## Three configurations

`CMake/StrataConfigurations.cmake` makes the :term[build configurations]{id=build-configuration}. Debug runs with no :term[optimization]{id=optimization} and asserts. Release is optimized, keeps debug information and keeps asserts, and Dist is the build of exported games, with asserts compiled out. The names follow the Hazel engine's convention. A test run on Debug alone proves little about Dist, where `ST_CORE_ASSERT` has vanished and the optimization works on different code.

```cmake src="CMake/StrataConfigurations.cmake#L18-L51"
# Dist uses the Release toolchain flags; only the ST_DIST define differs.
foreach(lang C CXX)
	set(CMAKE_${lang}_FLAGS_DIST "${CMAKE_${lang}_FLAGS_RELEASE}" CACHE STRING "Flags used by the ${lang} compiler for Dist builds" FORCE)
endforeach()
foreach(kind EXE SHARED MODULE STATIC)
	set(CMAKE_${kind}_LINKER_FLAGS_DIST "${CMAKE_${kind}_LINKER_FLAGS_RELEASE}" CACHE STRING "Linker flags for Dist builds" FORCE)
endforeach()
# Imported targets: prefer their Release variant, else the configuration-less location (the empty entry).
set(CMAKE_MAP_IMPORTED_CONFIG_DIST "Release" "")

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set_property(GLOBAL PROPERTY USE_FOLDERS ON)

# Third-party projects with old cmake_minimum_required() calls should still honor these.
set(CMAKE_POLICY_DEFAULT_CMP0077 NEW) # option() honors normal variables
set(CMAKE_POLICY_DEFAULT_CMP0091 NEW) # MSVC runtime library abstraction
set(CMAKE_POLICY_DEFAULT_CMP0141 NEW) # MSVC debug information format abstraction
set(CMAKE_POLICY_VERSION_MINIMUM 3.5)

# Statically link the MSVC runtime everywhere so exported games need no redistributable.
set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
# Compiler caches cannot cache objects whose debug information goes into a PDB that every compile of the target shares:
# with STRATA_COMPILER_CACHE the objects carry it (/Z7) and the linker gathers it as before.
if(STRATA_COMPILER_CACHE)
	set(CMAKE_MSVC_DEBUG_INFORMATION_FORMAT "Embedded")
else()
	set(CMAKE_MSVC_DEBUG_INFORMATION_FORMAT "ProgramDatabase")
endif()
if(MSVC)
	add_link_options("$<$<CONFIG:Release,Dist>:/DEBUG;/OPT:REF;/OPT:ICF>")
endif()
```

1. **Lines 19–24:** Dist copies the flags of Release for the compiler and for the linker. Nothing in the flags differs: the one difference is a definition, `ST_DIST`, which `strata_configure_target` adds to a Dist build.
2. **Line 26:** libraries that vendor projects build offer a Release and a Debug file; a Dist target maps to the Release file, or to the file with no configuration.
3. **Line 41:** the MSVC runtime is linked statically, as `MultiThreaded` in Release and Dist and `MultiThreadedDebug` in Debug, so an exported game needs no extra installer.
4. **Lines 44–48:** a compiler cache cannot cache an object whose debug information goes into a program database (PDB) file that every compile of the target shares. With the cache option, each object holds its own (`Embedded`).
5. **Line 50:** Release and Dist link with `/DEBUG` for symbols, and `/OPT:REF` and `/OPT:ICF` drop unused functions and fold identical ones.

Lines 54 to 56 of the file put programs and loaded libraries into `build/<preset>/bin` and static libraries into `build/<preset>/lib`. Each configuration gets its own folder below them, so programs land in `build/<preset>/bin/<Config>`.

## The layer libraries

The engine's `Strata/CMakeLists.txt` makes the libraries with one call.

```cmake src="Strata/CMakeLists.txt#L14-L29"
strata_add_layer_libraries(
	TABLE "${PROJECT_SOURCE_DIR}/StrataTests/Architecture/Layers.json"
	SOURCE_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/src"
	LIBRARIES_FILE "${CMAKE_CURRENT_BINARY_DIR}/LayerLibraries.json")

# Every layer reaches the engine's headers and the generated ones through Core.
target_include_directories(Strata_Core PUBLIC
	"${CMAKE_CURRENT_SOURCE_DIR}/src"
	"${CMAKE_CURRENT_BINARY_DIR}/Generated")
# Which optional modules and backends the engine has (STRATA_WITH_*), 1 or 0, for every target that links the engine: definitions rather
# than a generated header, so that no file can read one as 0 for want of an include.
target_compile_definitions(Strata_Core PUBLIC
	"ST_WITH_PHYSICS=$<BOOL:${STRATA_WITH_PHYSICS}>"
	"ST_WITH_AUDIO=$<BOOL:${STRATA_WITH_AUDIO}>"
	"ST_WITH_ANIMATION=$<BOOL:${STRATA_WITH_ANIMATION}>"
	"ST_WITH_GLFW=$<BOOL:${STRATA_WITH_GLFW}>")
```

1. **Lines 14–17:** the call names the table, the source folder and the file that records the result.
2. **Lines 20–22:** every layer reaches the engine's headers and the generated ones through `Core`, so one `PUBLIC` include folder serves all.
3. **Lines 25–29:** the optional modules reach the code as definitions that are 1 or 0. `$<BOOL:...>` turns the option into 1 or 0 when the build files are written.

The definitions are on `Strata_Core`, never in a header. A generated header such as `Features.h` would work, until a file used `#if ST_WITH_PHYSICS` and forgot to include it: the :term[preprocessor]{id=preprocessor} reads an unknown name as 0, and the physics code compiles out in silence. A definition reaches the compiler for every file that links the engine, so there is nothing to forget.

:::rule[`ST_WITH_<MODULE>` is a definition, never a macro of a header]
A file that misses an include must not compile a module out. The definitions are 1 or 0 on `Strata_Core`. The tests, the runtime, the asset pipeline and the composition root are the four places that may test them with `#if`. Other code reaches a module through a service, as [Layers, registries and the composition root](../core/layers-registries.md) says.
:::

Compile-time exclusion differs from the loaded extensions of other engines. A build without audio contains no audio code at all, and no test can find it. An extension that loads while the program runs is always in the file, and the program decides to use it. Strata chooses the first for its modules and the second only for game scripts. A build that leaves a module out is smaller and has fewer ways to fail.

### Giving each file one owner

The function `strata_add_layer_libraries` first globs the sources. **`GLOB_RECURSE CONFIGURE_DEPENDS`** collects every file that matches a pattern in the tree under a folder, and with the keyword CONFIGURE_DEPENDS the build checks the folder again and configures again when the list changes. It filters out the folders of other platforms and of the window backend not built. Then it reads the table into a regular expression for each glob, with the same meaning as the checker behind `Architecture.Layering`, and runs the ownership loop that the toy showed.

```cmake src="CMake/StrataLayers.cmake#L155-L186"
# Every file in exactly one layer: the rule Architecture.Layering enforces.
foreach(source IN LISTS sources)
	set(owners "")
	foreach(name IN LISTS layerNames)
		set(matched OFF)
		foreach(regex IN LISTS layer_${name}_Paths)
			if(source MATCHES "${regex}")
				set(matched ON)
				break()
			endif()
		endforeach()
		if(matched)
			foreach(regex IN LISTS layer_${name}_Exclude)
				if(source MATCHES "${regex}")
					set(matched OFF)
					break()
				endif()
			endforeach()
		endif()
		if(matched)
			list(APPEND owners "${name}")
		endif()
	endforeach()
	list(LENGTH owners ownerCount)
	if(ownerCount EQUAL 0)
		message(FATAL_ERROR "The engine source '${source}' is in no layer of ${ARG_TABLE}: give its folder or file a pattern")
	elseif(ownerCount GREATER 1)
		string(REPLACE ";" ", " ownerList "${owners}")
		message(FATAL_ERROR "The engine source '${source}' is in several layers of ${ARG_TABLE} (${ownerList}): exclude it from all but one")
	endif()
	list(APPEND layer_${owners}_Sources "${source}")
endforeach()
```

1. **Lines 156–177:** for each source, every layer is tested: some `Paths` regular expression must match, and no `Exclude` expression may. Matching layers go into `owners`.
2. **Lines 179–180:** no owner is a configure error that names the file and says what to do: give its folder or file a pattern.
3. **Lines 181–184:** several owners is an error as well, and it lists them and says to exclude the file from all but one.
4. **Line 185:** the single owner receives the file in its list of sources.

A configure error stops the build at once, which beats a file that no library compiles and that no test reads.

### Making the libraries

For each layer whose option is on, the function makes the target.

```cmake src="CMake/StrataLayers.cmake#L222-L243"
	set(excludeFromAll "")
	if(layer_${name}_Tooling)
		set(excludeFromAll EXCLUDE_FROM_ALL)
	endif()
	if(compiled)
		add_library(${target} STATIC ${excludeFromAll} ${absoluteSources})
		strata_configure_target(${target})
		target_link_libraries(${target} PRIVATE StrataEngineCodegen)
		strata_precompile_headers(${target} "${ARG_SOURCE_ROOT}/stpch.h")
		set(scope PUBLIC)
	else()
		add_library(${target} INTERFACE ${excludeFromAll} ${absoluteSources})
		target_compile_features(${target} INTERFACE cxx_std_20)
		set(scope INTERFACE)
	endif()
	add_library(Strata::${name} ALIAS ${target})
	set_target_properties(${target} PROPERTIES FOLDER "Strata/Layers" STRATA_LAYER "${name}" STRATA_TOOLING ${layer_${name}_Tooling})
	source_group(TREE "${ARG_SOURCE_ROOT}" FILES ${absoluteSources})
	foreach(dependency IN LISTS links)
		target_link_libraries(${target} ${scope} Strata_${dependency})
	endforeach()
endif()
```

1. **Lines 222–225:** a tooling layer gets `EXCLUDE_FROM_ALL`.
2. **Lines 226–231:** a layer with a `.c`, `.cpp`, `.m` or `.mm` file is a static library with the engine's flags, its own precompiled header and the shared code generation options. Its links are `PUBLIC`.
3. **Lines 232–236:** a layer with only headers is an interface library, and its links are `INTERFACE`.
4. **Lines 240–242:** the library links the built layers of its `MayInclude`, in the table's order; a layer that is off is skipped.

A layer that is switched off has no target, and the layers that listed it link no library in its place. `Strata_Audio` therefore links `Core`, `App`, `Asset`, `Reflection` and `Scene`, the five layers of its row.

### Vendor libraries

A layer that needs a vendor or system library adds one row to the table in `Strata/CMakeLists.txt`, through `strata_layer_link`.

```cmake src="CMake/StrataLayers.cmake#L341-L365"
function(strata_layer_link layer scope)
	if(NOT layer IN_LIST STRATA_BUILT_LAYERS)
		return()
	endif()
	get_target_property(type Strata_${layer} TYPE)
	if(type STREQUAL "INTERFACE_LIBRARY" AND NOT scope STREQUAL "INTERFACE")
		message(FATAL_ERROR "strata_layer_link: the ${layer} layer has nothing to compile; link its libraries INTERFACE")
	endif()
	foreach(item IN LISTS ARGN)
		set(isLayer OFF)
		if(item MATCHES "^Strata(_|::)")
			set(isLayer ON)
		elseif(TARGET "${item}")
			get_target_property(itemLayer "${item}" STRATA_LAYER)
			if(itemLayer)
				set(isLayer ON)
			endif()
		endif()
		if(isLayer)
			message(FATAL_ERROR "strata_layer_link: '${item}' is a layer's library: the ${layer} layer links the layers of its "
				"MayInclude (StrataTests/Architecture/Layers.json) and no others")
		endif()
	endforeach()
	target_link_libraries(Strata_${layer} ${scope} ${ARGN})
endfunction()
```

1. **Lines 342–344:** a layer that is not built makes the row a no-op, so a build without physics skips `box3d` with no condition at the call.
2. **Lines 345–348:** an interface layer can only take `INTERFACE` links.
3. **Lines 349–363:** an item that is a layer's library is a configure error; layers link each other only as their `MayInclude` says.

Linking another layer by hand would satisfy the compiler, but it would widen the row without the table. The function refuses.

### What programs link

Two interface targets collect the layers for programs. Search for the two loops, one over the runtime layers and one over the tooling layers.

```cmake src="Strata/CMakeLists.txt#L238-L245"
add_library(Strata INTERFACE)
foreach(layer IN LISTS STRATA_RUNTIME_LAYERS)
	target_link_libraries(Strata INTERFACE Strata_${layer})
endforeach()
add_library(StrataTooling INTERFACE)
foreach(layer IN LISTS STRATA_TOOLING_LAYERS)
	target_link_libraries(StrataTooling INTERFACE Strata_${layer})
endforeach()
```

`Strata` links each runtime layer and `StrataTooling` each tooling layer. A program links `Strata` to get the engine, and a tool adds `StrataTooling`.

## Recording what was really linked

A library description must show what the targets really link, not what the table says they should. Other folders add their own links after `Strata/CMakeLists.txt` has run, so the description is written at the very end of configure. **`cmake_language(DEFER)`** is the CMake command that delays a call until the end of a folder's file. Strata wraps it in a small function.

```cmake src="CMake/StrataLayers.cmake#L33-L39"
function(strata_defer_to_end command)
	set(arguments "")
	foreach(argument IN LISTS ARGN)
		string(APPEND arguments " [==[${argument}]==]")
	endforeach()
	cmake_language(EVAL CODE "cmake_language(DEFER DIRECTORY [==[${PROJECT_SOURCE_DIR}]==] CALL ${command}${arguments})")
endfunction()
```

The function writes the values into the text of the call. A deferred call expands variables only when it runs, in the scope of that folder, where the values may be gone. When the deferred call runs, `strata_write_layer_libraries` reads each target's links back from CMake. It writes `build/<preset>/Strata/LayerLibraries.json`, which holds for every layer its target, whether it is built, its tooling flag, its option, the layers it links and its sources.

The test `Architecture.Libraries` reads that file. A link added by hand in another file shows in the layer's `Links`, and the test compares it with `MayInclude` and fails.

## Proving that games contain no tooling

A game must not contain the asset pipeline, the network layer, Dear ImGui or the importers. Three facts make the proof harder than it looks.

A link can come in through a chain of libraries. A name that is no target yet cannot be checked. And a linker may take only the objects a program refers to, so a library that is linked may add nothing. Strata therefore proves the claim twice, at two moments, from two views.

```mermaid caption="Two proofs for one rule. The configure check walks the links of the runtime, and the test reads the linker map of the finished runtime." alt="A flow in two rows. Row one: the end of configure walks every library the runtime links and reports a forbidden one with its path, or passes. Row two: the runtime is linked with a map file; the test script reads the required objects first, then fails if any forbidden object or library is named."
flowchart LR
  A[End of configure] --> B[Walk the links of StrataRuntime]
  B -->|forbidden target| X1[Configure fails with the path]
  B -->|none| C[Build and link StrataRuntime with a map]
  C --> D[CheckNoTooling.cmake reads the map]
  D -->|required objects missing| X2[Fails: the map proves nothing]
  D -->|forbidden object or library| X3[Fails with the lines]
  D -->|none| OK[Pass]
```

### At configure: the link closure

The **link closure** of a target is the set of all targets it links, directly or through any chain of links. The function `strata_check_link_closure` computes it and compares it with a list.

```cmake src="CMake/StrataLayers.cmake#L401-L429"
function(strata_check_link_closure_now target)
	cmake_parse_arguments(ARG "" "" "FORBID" ${ARGN})
	if(NOT TARGET ${target})
		message(FATAL_ERROR "strata_check_link_closure: ${target} is no target")
	endif()
	set_property(GLOBAL PROPERTY STRATA_LINK_CLOSURE "")
	foreach(property IN ITEMS LINK_LIBRARIES INTERFACE_LINK_LIBRARIES)
		get_target_property(linked ${target} ${property})
		if(linked)
			foreach(item IN LISTS linked)
				strata_collect_link_closure("${item}" "${target}")
			endforeach()
		endif()
	endforeach()
	get_property(closure GLOBAL PROPERTY STRATA_LINK_CLOSURE)
	set(problems "")
	foreach(name IN LISTS closure)
		get_target_property(tooling ${name} STRATA_TOOLING)
		if("${name}" IN_LIST ARG_FORBID OR tooling)
			get_property(path GLOBAL PROPERTY STRATA_LINK_PATH_${name})
			list(APPEND problems "  ${path}")
		endif()
	endforeach()
	if(problems)
		string(REPLACE ";" "\n" problems "${problems}")
		message(FATAL_ERROR "${target} links tooling that games must not contain:\n${problems}\n"
			"Runtime layers never include tooling layers (Layers.json); a program links tooling only through StrataTooling.")
	endif()
endfunction()
```

1. **Lines 406–414:** the walk starts from the target's own links and collects everything below, remembering the path by which each name was first reached.
2. **Lines 417–423:** a name is a problem when it is in the forbidden list or its target is marked as tooling. The marker is the `STRATA_TOOLING` property that the layer function sets from the table.
3. **Lines 424–428:** the error lists every path and names the rule: runtime layers never include tooling layers, and a program links tooling only through `StrataTooling`.

The check runs at the end of configure because every folder must have added its targets by then. A name that is no target when the check runs would be skipped, whatever it links. The sketch of the second exercise walks a small graph and prints paths in the same form.

### At test time: the linker map

A **linker map** is a text file that the linker writes, listing every object and library it put into a program. Strata links `StrataRuntime` with a map next to the program.

The test `StrataRuntime.NoTooling` reads the map in **script mode**. That is a run of `cmake -P`: CMake executes a file of commands as a script, with no project and no build. The script does its work in two passes over the map, so note what it requires before what it forbids.

```cmake src="StrataTests/Architecture/CheckNoTooling.cmake#L47-L80"
# One pass per kind over the map's lines (maps reach hundreds of megabytes: the lines are filtered as they are read).
string(REPLACE ";" "|" requiredNames "${requiredObjects}")
string(REPLACE ";" "|" objectNames "${forbiddenObjects}")
string(REPLACE ";" "|" libraryNames "${forbiddenLibraries}")
# "dir/Name.cpp.o", "lib.a(Name.cpp.o)", "Name.obj", "lib:Name.obj"
set(objectPrefix "(^|[/\\\\(: \t])")
set(objectSuffix "(\\.(c|cpp|m|mm))?\\.(o|obj)([^A-Za-z0-9_]|$)")
file(STRINGS "${MAP}" requiredLines REGEX "${objectPrefix}(${requiredNames})${objectSuffix}")
foreach(required IN LISTS requiredObjects)
	set(seen FALSE)
	foreach(line IN LISTS requiredLines)
		if(line MATCHES "${objectPrefix}${required}${objectSuffix}")
			set(seen TRUE)
			break()
		endif()
	endforeach()
	if(NOT seen)
		message(FATAL_ERROR "CheckNoTooling: the linker map '${MAP}' names no ${required} object, which every runtime contains: "
			"it is empty, truncated or in a format this check does not read, so it proves nothing about tooling")
	endif()
endforeach()
file(STRINGS "${MAP}" objectLines REGEX "${objectPrefix}(${objectNames})${objectSuffix}")
# "dir/libName.a", "Name.lib"
file(STRINGS "${MAP}" libraryLines REGEX "(^|[/\\\\(: \t])(lib)?(${libraryNames})\\.(a|lib)([^A-Za-z0-9_]|$)")

set(found ${objectLines} ${libraryLines})
list(REMOVE_DUPLICATES found)
list(LENGTH found count)
if(count GREATER 0)
	list(SUBLIST found 0 20 shown)
	string(REPLACE ";" "\n  " shown "${shown}")
	message(FATAL_ERROR "The game executable contains tooling or what this build leaves out (${MAP}), ${count} lines name it, among them:\n  ${shown}")
endif()
message(STATUS "No tooling or what this build leaves out in ${MAP}")
```

1. **Lines 48–67:** before any forbidden name, the script requires the objects every runtime contains. The map must name `RuntimeApplication` and `Application`.
2. **Lines 64–66:** an empty map, a truncated one or one in a format the patterns do not read proves nothing by naming no tooling, so that case fails with its own message.
3. **Lines 68–70:** one pass for each kind reads the lines of the map and keeps those that name a forbidden object or library. Maps reach hundreds of MB, so the lines are filtered as they are read.
4. **Lines 75–79:** a found name is an error with a count and the first 20 lines.

The two proofs cover different ground. The closure check sees links, including those a linker would drop; the map sees what really entered the program, including an object that came in by another way. The script accepts the formats of MSVC, `GNU ld` and Apple `ld`, because it matches object and library file names wherever they appear.

### The application manifest

On Windows, `StrataEditor`, `StrataRuntime`, `StrataCLI` and `StrataTests` add `CMake/Strata.manifest` to their sources. It makes :term[UTF-8]{id=utf-8} the process code page, so narrow strings, `argv` and file paths are UTF-8 everywhere, and it allows long paths. A helper that copies a resource folder next to a binary, `strata_copy_runtime_resources`, exists in `CMake/StrataCompilerOptions.cmake`, but no target calls it at the pin.

## A source file followed through the build

:::example[The path of one file]
[Your first change](../core/first-change.md) added `ToUpper` to `Strata/src/Strata/Core/StringUtils.h`. Follow that file through the build. The text below shows the strings that matter, written relative to the source folder `Strata/src`: the file, the pattern of `Core`, and the first pattern of its `Exclude`, each beside its regular expression.

```text
file     Strata/Core/StringUtils.h
Paths    Strata/Core/**                ->  ^Strata/Core/.*$
Exclude  Strata/Core/Application.*     ->  ^Strata/Core/Application\.[^/]*$
```

The steps then run as follows.

1. The glob returns the file with the path of the first row.
2. The `Core` pattern becomes the expression of the second row, and the path matches it.
3. `Core` has six `Exclude` globs, and none of their expressions matches, so `Core` is an owner.
4. No other layer has a pattern that matches, so there is exactly one owner.
5. `Core` has `.cpp` files, so `Strata_Core` is a static library. It links no layer, because its `MayInclude` is empty, and the file is in its list of sources.
6. At the end of configure, `LayerLibraries.json` gets the entry of `Core`: target `Strata_Core`, built `true`, tooling `false`, links `[]`, and a list of sources that holds the file.

The test `Architecture.Libraries` compares that file with the table and the source tree, and passes when the file is in the library of its layer.
:::

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| One library for the whole engine | Small engines and many open-source projects | A short build file, no ownership loop | No target to say what a layer may link; no way to leave a layer out |
| Libraries listed by hand | Most projects | Plain lists | A second source of truth that drifts from the table |
| Visibility rules of the build tool | `Bazel` declares which targets may see which | The build tool refuses a bad link itself | A new build system, and a rule file that must match the include checker |
| Extensions that load while the program runs | Unreal Engine loads modules by name | Features added without a rebuild | A stable interface for every type, a crash boundary, and no proof of what a game contains |

Strata keeps the CMake it has because a script that reads one table and checks the rest is short, and because CMake is what every platform's tools already read.

## How it is tested

`Architecture.Libraries` reads `LayerLibraries.json` and the table. The checks are three. Each layer's target is `Strata_<Layer>`, each built library links exactly the built layers of its `MayInclude`, and every source file of the tree is in the library of its own layer. A file added without a configure fails with "configure again after adding files".

`StrataRuntime.NoTooling` is a CTest test that runs `CheckNoTooling.cmake` on the runtime's map. The configure errors are checks too: a configure that hits one stops, so no build exists to test.

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=Architecture.Libraries
ctest --preset windows-debug -R StrataRuntime.NoTooling
```

The first command runs the suite on a Windows Debug build. The second runs the map check, which needs the build of `StrataRuntime`. A build without the window backend adds the GLFW objects to the forbidden list and `NoWindow` to the required list, so the same script checks that configuration.

## Changing it safely

- **A new source file:** run the :term[configure step]{id=configure-step} again (`cmake --preset <preset>`), because the glob lists the files at configure time. `Architecture.Libraries` names a file that no library holds.
- **A new folder:** add a pattern to the `Paths` of the layer that should own it, and check that no other layer matches. Configure names a folder no layer matches.
- **A new vendor library:** add one `strata_layer_link` row in `Strata/CMakeLists.txt`, `PRIVATE` unless a header of the layer shows the library's types.
- **A new dependency between layers:** invert it. Never widen a `MayInclude` row; that is the one change the rule forbids.
- **A new optional module:** a layer entry with its `Option`, a CMake option in the root, and a row for its definition on `Strata_Core`.

Before the change is done, run `Architecture.Layering`, `Architecture.Libraries` and `StrataRuntime.NoTooling`, then a configure with `-DSTRATA_WITH_PHYSICS=OFF -DSTRATA_WITH_AUDIO=OFF -DSTRATA_BUILD_EDITOR=OFF` in a second build folder.

## Summary

- Targets carry usage requirements: `PUBLIC` passes them to users, `PRIVATE` keeps them inside, and `INTERFACE` only passes them. Linking `PUBLIC` what should be `PRIVATE` leaks headers to code that must not see them.
- `strata_add_layer_libraries` gives every engine source to exactly one layer. It makes `Strata_<Layer>` from that layer's files and links the built layers of its row.
- A source in no layer, or in several, fails configure and names the file and the fix. `strata_layer_link` refuses a layer's library.
- Games contain no tooling, proven twice. The link-closure walk at the end of configure reports a path; the linker map test first requires the objects every runtime holds.
- A new file needs a configure, a new folder a layer pattern, and a vendor library a `strata_layer_link` row. No change widens a `MayInclude` row.

## Check yourself

1. In the toy, `Mid` links `Base` `PUBLIC` and `main.cpp` includes `base.h`. What happens with `PUBLIC`, and what with `PRIVATE`?

   :::answer{tests="usage-requirements"}
   With `PUBLIC` the program compiles, because the include folder of `Base` reaches `Game` through `Mid`: a leak. With `PRIVATE` the compile fails on the include, because the folder stays inside `Mid`. The link step still works in both cases, since `Mid`'s objects need `Base`.
   :::

2. Which of these fail the configure? (a) A new `.cpp` file in a new folder `Video` of the engine source that no layer lists. (b) A file that two layers list. (c) `strata_layer_link(Physics PRIVATE Strata_Core)`. (d) A new `.cpp` file in `Strata/src/Strata/Core/` that was added without a configure.

   :::answer{tests="read-error"}
   (a), (b) and (c) fail: (a) with "is in no layer", (b) with "is in several layers", and (c) because the item is a layer's library. (d) does not fail configure, because no configure ran; the file is in no library yet, and `Architecture.Libraries` reports it as such.
   :::

3. A teammate says the configure check of the runtime is enough, and the map test can go. Give a case the closure check cannot see.

   :::answer{tests="no-tooling"}
   An object that entered the program by another way than a link, for example a source file added to a runtime target by hand. The closure sees only links. The map lists what the linker really put in, and it also fails when it names no runtime objects at all, so a broken map cannot pass.
   :::

4. A game is configured with audio and physics off. Which targets does the build not make, and what does `ST_WITH_AUDIO` read in a file?

   :::answer{tests="add-correctly"}
   The build makes no `Strata_Audio` and `Strata_Physics`, and the vendor libraries `miniaudio` and `box3d` are not built. `ST_WITH_AUDIO` is the definition 0 on every target that links the engine, so `#if ST_WITH_AUDIO` is false everywhere, without any include.
   :::

5. A new `.cpp` file is added to the audio folder `Strata/src/Strata/Audio/` and you configure. Which target does it compile into, and what does `LayerLibraries.json` show?

   :::answer{tests="owner-target"}
   The file compiles into `Strata_Audio`, the library of the layer whose pattern matches the folder. The `Audio` entry lists the file under `Sources`, relative to the source folder, and shows `Built` as true. With `-DSTRATA_WITH_AUDIO=OFF` the entry shows `Built` as false, and the file compiles into no target.
   :::

## Exercises

1. **Basic.** Add an empty `.cpp` file in a new folder `Video` under `Strata/src/Strata/`, configure, and read the error. Then change `Layers.json` so that the file has an owner, and say which layer you chose and why.

   :::answer[Worked solution]{tests="read-error"}
   Configure fails with `The engine source '<path>' is in no layer of <Layers.json>: give its folder or file a pattern`, where `<path>` is the file relative to the source folder. Choose the lowest existing layer whose `MayInclude` row holds what the file needs, and add a pattern for the new folder to its `Paths`; a new layer is a larger change. Configure again; the error is gone. Then `Architecture.Layering` checks the includes of the new file against that row.
   :::

2. **Medium.** On a scratch branch, make a file of `Strata/src/Strata/Scene/` include a header of `Strata/src/Strata/Asset/AssetPackWriter.h`, and add `target_link_libraries(Strata_Scene PUBLIC Strata_AssetPipeline)` after the layer call. Say what `Architecture.Layering` reports and what the configure error looks like. The sketch below mirrors the closure walk of the configure error.

   :::answer[Worked solution]{tests="read-error,no-tooling" solution="sketches/engineering-cmake-closure.cpp"}
   `Architecture.Layering` reports `<file>(<line>): includes Strata/Asset/AssetPackWriter.h, but layer Scene may not include layer AssetPipeline`. Without the link, a call into that header would leave a function that the runtime's link cannot find. With the link added, `Architecture.Libraries` fails too, and configure stops with `StrataRuntime links tooling that games must not contain:` followed by one line for each path. The sketch builds a graph with that link and prints the paths in the same form:

   ```cpp sketch="engineering-cmake-closure.cpp"
   // A toy of the link-closure walk: collect everything a target links, directly or through other libraries, and report
   // the path to each forbidden name.
   #include <iostream>
   #include <map>
   #include <set>
   #include <string>
   #include <vector>

   using Graph = std::map<std::string, std::vector<std::string>>;

   static void Collect(const Graph& graph, const std::string& name, const std::string& path, std::map<std::string, std::string>& paths,
   	std::vector<std::string>& order)
   {
   	if (paths.count(name) > 0)
   		return;
   	paths[name] = path + " -> " + name;
   	order.push_back(name);
   	const auto links = graph.find(name);
   	if (links == graph.end())
   		return;
   	for (const std::string& next : links->second)
   		Collect(graph, next, path + " -> " + name, paths, order);
   }

   int main()
   {
   	const Graph graph = {
   		{ "StrataRuntime", { "Strata" } },
   		{ "Strata", { "Strata_Core", "Strata_Scene" } },
   		{ "Strata_Scene", { "Strata_Core", "Strata_AssetPipeline" } },
   		{ "Strata_AssetPipeline", { "Strata_Core", "cgltf" } },
   	};
   	const std::set<std::string> forbidden = { "Strata_AssetPipeline", "cgltf" };

   	std::map<std::string, std::string> paths;
   	std::vector<std::string> order;
   	for (const std::string& item : graph.at("StrataRuntime"))
   		Collect(graph, item, "StrataRuntime", paths, order);

   	for (const std::string& name : order)
   	{
   		if (forbidden.count(name) > 0)
   			std::cout << "  " << paths[name] << "\n";
   	}
   	return 0;
   }
   ```

   ```text output-of="engineering-cmake-closure.cpp"
     StrataRuntime -> Strata -> Strata_Scene -> Strata_AssetPipeline
     StrataRuntime -> Strata -> Strata_Scene -> Strata_AssetPipeline -> cgltf
   ```

   1. **Lines 11–23:** `Collect` records the path of each name once, the first time it is reached, then follows its links.
   2. **Lines 27–32:** the graph has the added link from `Strata_Scene` to `Strata_AssetPipeline`.
   3. **Lines 40–44:** only forbidden names are printed, in the order the walk met them.

   The first line is the path to the tooling library; the second shows that the closure continues into what that library links. The fix is the inversion of the dependency, not a wider row.
   :::

3. **Medium.** Configure a second build folder with `-DSTRATA_WITH_PHYSICS=OFF -DSTRATA_WITH_AUDIO=OFF -DSTRATA_BUILD_EDITOR=OFF`. Say which layers, vendor libraries and test files the build omits.

   :::answer[Worked solution]{tests="add-correctly"}
   `Strata_Physics` and `Strata_Audio` are not made, and `LayerLibraries.json` shows them with `Built` set to false. `box3d` and `miniaudio` are not built either. The tests of `src/Physics/` and `src/Audio/`, the files that test little else of them, and `src/FeatureTest/` leave the test program. With the editor off, `src/Editor/` tests go too. Without that last flag, the root file would refuse the configure and tell you to turn the editor off.
   :::

4. **Hard.** Trace it yourself: follow a source file of `Strata/src/Strata/Audio/`, as the example followed `StringUtils.h`, from its pattern in `Layers.json` to `Strata_Audio` and its entry in `LayerLibraries.json`.

   :::answer[Worked solution]{tests="owner-target"}
   The pattern for the audio folder is in the layer `Audio` of `StrataTests/Architecture/Layers.json`, with the `Option` `STRATA_WITH_AUDIO`. In `CMake/StrataLayers.cmake` the glob at lines 99 to 103 finds the file, the regular expression comes from `strata_glob_to_regex`, and the ownership loop at lines 155 to 186 gives it to `Audio`. The function at lines 226 to 231 makes `Strata_Audio`, linked to `Core`, `App`, `Asset`, `Reflection` and `Scene`. Its entry in `build/<preset>/Strata/LayerLibraries.json` lists the file under `Sources`.
   :::

## Where it lives in Strata

- `CMakeLists.txt`: the guards, options, folders and the deferred closure check.
- `CMake/StrataConfigurations.cmake`: configurations and output folders.
- `CMake/StrataLayers.cmake`: `strata_add_layer_libraries`, `strata_layer_link`, `strata_check_link_closure`.
- `Strata/CMakeLists.txt`: the call, the `ST_WITH_*` definitions, the vendor rows, `Strata` and `StrataTooling`.
- `StrataTests/Architecture/Layers.json`, `CheckNoTooling.cmake`: the table and the map check.
- Tests: `Architecture.Libraries` (`StrataTests/src/Architecture/LibrariesTests.cpp`), `StrataRuntime.NoTooling`.
- Output: `build/<preset>/Strata/LayerLibraries.json`.

## Further reading

- CMake documentation, "cmake-buildsystem(7)" (intermediate): targets, usage requirements and the kinds of libraries.
- CMake documentation, "cmake-generator-expressions(7)" (intermediate): the `$<...>` forms.
- Craig Scott, "Professional CMake: A Practical Guide" (advanced): the book on targets and good build structure.
