---
id: core/layers-registries
title: "Layers, registries and the composition root"
description: "How Strata keeps lower code from using higher code, and how every module registers once, in one place, before any code reads a registry."
kind: internals
size: L
tracks: [E]
needs: [core/engine-modules, basics/data-formats]
time: 80
learn:
  - id: layer-rule
    text: predict whether an include passes the layer table, and fix a forbidden one by inverting the dependency
  - id: composition-root
    text: explain why Strata registers every module from one function and not from static constructors
  - id: two-registries
    text: name the registries that freeze and the ones that stay open, and what each allows after startup
  - id: register-game
    text: add a game's component or settings section through the options of the root and predict what a late registration does
  - id: trace-root
    text: trace Engine::RegisterBuiltinModules from main and find what it opens, runs and freezes
since: 0.3.0
status: final
---

Strata keeps its :term[source code]{id=source-code} in 19 layers, and a table says which layer may use which. A lower layer never uses a higher one, so you can leave a module out of a game, test a layer alone and read the code from the bottom up. This page teaches that table and the test that enforces it. It also teaches `Engine::RegisterBuiltinModules`, the one function that every program calls at startup, where each module adds its components, loaders and systems to the tables that the rest of the engine reads. Other pages teach the :term[CMake]{id=cmake} that builds a library for each layer, the builder that describes a component, and the order of scene systems.

[Engine modules](engine-modules.md) showed that a module has two sides: an `EngineModule` that runs for the whole life of a program, and a `Register<Module>Module` function that runs once at startup. This page is about the second side.

This page needs no project and no download. Its sketches are whole programs for the compiler of [How a C++ program is built](../basics/build.md#open-a-terminal-that-finds-a-compiler). Its test commands and its trace need the source build of [your first engine change](first-change.md#build-the-engine-and-start-the-editor), in `Debug`.

## The problem and how engines solve it

Start with a question that every engine meets. The physics code wants the triangles of a mesh, and the :term[renderer]{id=renderer} owns the mesh. The quick answer is an include of a renderer :term[header]{id=header} in a physics file. The price comes later: a test of physics alone now needs the renderer to compile, and a build without physics still has code that reaches for it. When the renderer later calls into physics, each part depends on the other, and neither can change alone.

The usual cure is to sort the code into layers, bottom to top, with one rule: code may use its own layer and the layers below it, never a layer above. The rule has four rewards. A cycle cannot form, and a layer needs only the layers under it to build and test. A program that does not need a layer can omit it. A tool can check the rule by reading the include lines.

Strata has 19 layers. The `Physics` layer may use four others (`Core`, `Asset`, `Reflection` and `Scene`), and the `Renderer` six. So no physics file can include a renderer header, and `-DSTRATA_WITH_PHYSICS=OFF` leaves physics out of a build without touching the renderer.

The rule leaves the first question open: physics still needs triangles. **Dependency inversion** answers it: code in a higher layer provides an implementation of something that a lower layer defines, so the lower layer needs no knowledge of the higher one. Strata uses three forms:

- An interface below. `Input` defines `InputWindow`, and the window in `App` implements it, so input code reaches the window without including it.
- A table below, filled from above. The asset layer defines `MeshGeometryRegistry`, the renderer fills it, and physics reads the triangles of a mesh from it with no renderer header.
- A service, an object that one part of the engine finds by its type, as [Engine modules](engine-modules.md) taught.

A **registry** is a table that modules fill at startup and other code reads: component names to component descriptions, asset types to loader functions, scene systems, settings sections. The word names a different thing from the registry of EnTT that holds entities, as [How Strata is put together](map.md) explains. A registry is dependency inversion made into a table: the code that reads it knows only the table, and the many modules that fill it are unknown to the reader.

Someone must call the code that fills the tables, and engines choose among three ways.

### Self-registration

Each module owns a global object whose :term[constructor]{id=constructor} adds the module to the registry before `main` starts. Adding a file then adds a module, and no list needs an edit. The scheme fails in two ways.

The first fault is in the :term[linker]{id=linker}. A linker that builds a program from :term[static libraries]{id=static-library} takes an :term[object file]{id=object-file} only when some code refers to a symbol in it. Nothing refers to a file that exists only to register. The linker drops it, and the module silently never registers.

The second fault is in the order. The language leaves the order of constructors in different files undefined, so a module may register into a table that does not exist yet. Both faults change with the :term[compiler]{id=compiler}, the linker and the platform, and Strata builds with three compilers on three platforms.

### One function that names every module

One function runs each module's registration function by name, in a written order. Nothing is dropped, because the call refers to the symbol. You can read the order on the page. The place that wires a program together like this is the **composition root**. Its costs are that it names every module, so it must stand at the top of the layers, and that a new module needs one more line.

### Extensions loaded while the program runs

The program finds :term[shared libraries]{id=shared-library} in a folder and loads them while it runs. Anyone can add a feature without rebuilding the engine. Each extension must meet the engine across a stable binary interface, a crash inside one can end the program, and each platform loads libraries in its own way. Strata uses this only for game scripts, which [Loading, calling and validating modules](../scripting/loading.md) teaches.

Strata chooses the second way for the engine's own modules. The next sections show the layers that let a tool check the rule, then the function itself.

## The map: nineteen layers

The rule lives in one file, `StrataTests/Architecture/Layers.json`. This **layer table** lists the layers from the bottom up, with the files each one owns and the layers each one may include. The figure groups them in bands.

```mermaid caption="Layers stand in bands from base to program. Higher bands build on lower ones, the three tooling layers stand apart with no arrow leading into them, and two dashed arrows mark the layers that include the application shell to implement its interface." alt="A diagram of five groups of layers. The base group sits at the bottom, the data group above it, the feature group above that, and the program group at the top, with an arrow from each group to the one below. A separate tooling group has no arrows into it. Two dashed arrows lead from layers in the feature group to a layer in the base group."
flowchart BT
  subgraph Program["Program layers"]
    Runtime
    Engine
  end
  subgraph Features["Feature layers"]
    Renderer
    Physics
    Audio
    Animation
    Scripting
    World
    GameUI
    Project
  end
  subgraph Data["Data layers"]
    Asset
    Reflection
    Scene
  end
  subgraph Base["Base layers"]
    Core
    Input
    App
  end
  subgraph Tooling["Tooling layers"]
    Network
    ImGui
    AssetPipeline
  end
  Program --> Features
  Features --> Data
  Data --> Base
  Audio -.->|implements EngineModule| App
  Project -.->|implements EngineModule| App
```

The base layers hold what everything needs: `Core` has platform services, logging, jobs, files and math, `Input` the events and the input state, and `App` the application shell and the window. The data layers hold assets, the descriptions of components and the scene. The feature layers hold what a game builds on those, and the program layers hold the :term[runtime]{id=runtime} for exported games and the composition root with its entry point.

Three layers stand to the side: `Network`, `ImGui` and `AssetPipeline`. Each carries `"Tooling": true` in the table. A **tooling layer** is a layer that no shipped game contains, because it serves the editor and the other tools. Three more layers carry an `"Option"`: `Physics`, `Audio` and `Animation` exist only in builds that ask for them. The table gives the exact lists.

| Layer | Marked | May include |
| --- | --- | --- |
| `Core` | - | nothing |
| `Input` | - | `Core` |
| `App` | - | `Core`, `Input` |
| `Asset` | - | `Core` |
| `Reflection` | - | `Core`, `Asset` |
| `Scene` | - | `Core`, `Asset`, `Reflection` |
| `Renderer` | - | `Core`, `Input`, `App`, `Asset`, `Reflection`, `Scene` |
| `Physics` | `STRATA_WITH_PHYSICS` | `Core`, `Asset`, `Reflection`, `Scene` |
| `Audio` | `STRATA_WITH_AUDIO` | `Core`, `App`, `Asset`, `Reflection`, `Scene` |
| `Animation` | `STRATA_WITH_ANIMATION` | `Core`, `Asset`, `Reflection`, `Scene` |
| `GameUI` | - | `Core`, `Input`, `Asset`, `Reflection`, `Scene`, `Renderer` |
| `Scripting` | - | `Core`, `Input`, `Asset`, `Reflection`, `Scene` |
| `World` | - | `Core`, `Asset`, `Reflection`, `Scene` |
| `Project` | - | `Core`, `App`, `Asset`, `Reflection` |
| `Runtime` | - | `Core`, `Input`, `App`, `Asset`, `Reflection`, `Scene`, `Renderer`, `Physics`, `Audio`, `Scripting`, `Project` |
| `Network` | tooling | `Core` |
| `ImGui` | tooling | `Core`, `Input`, `App`, `Renderer` |
| `AssetPipeline` | tooling | `Core`, `Asset`, `Reflection`, `Scene`, `Renderer`, `Audio`, `Animation`, `World` |
| `Engine` | - | every game layer except `Project` and `Runtime` (13 layers) |

Read the table for what it forbids. `Physics` may not include `Audio`, and `Scripting` may not include `Physics`: layers of one band do not use each other. They meet through scene services, objects that a playing scene offers by type. `Engine` lists every game layer except `Project` and `Runtime`, and lists no tooling layer, which keeps the importers out of games.

The order of the file is part of the rule. A layer may list only layers above it in the file, and the table :term[parser]{id=parser} refuses a table that lists a later one. A cycle is therefore impossible: the order of the file is the order of the layers.

## The layer table and the tests that read it

The first lines of the table show its fields. The file starts with a description that states the rules in one long sentence, then the settings and the layers.

```json src="StrataTests/Architecture/Layers.json#L3-L24"
"SourceRoot": "Strata/src",
"MaxAllowlistEntries": 0,
"Layers": [
	{
		"Name": "Core",
		"Notes": "Platform services, logging, jobs, files, processes and math. The OS implementations of Core interfaces live in Platform/<OS>; the socket implementations belong to Network.",
		"Paths": [ "stpch.h", "Strata/Core/**", "Strata/Math/**", "Platform/Windows/**", "Platform/Posix/**", "Platform/MacOS/**" ],
		"Exclude": [ "Strata/Core/Application.*", "Strata/Core/EngineModule.*", "Strata/Core/Layer.*", "Strata/Core/LayerStack.*", "Strata/Core/Window.*", "Platform/*/*Socket.cpp" ],
		"MayInclude": []
	},
	{
		"Name": "Input",
		"Notes": "Events and the input state; Input reaches the window through InputWindow, which Window implements.",
		"Paths": [ "Strata/Events/**", "Strata/Input/**" ],
		"MayInclude": [ "Core" ]
	},
	{
		"Name": "App",
		"Notes": "The application shell: Application, layers, the EngineModule interface the modules implement (Application runs their hooks and names none of them), the window and its GLFW implementation. VulkanLoader and VulkanPresentation belong here, not to Renderer: the window system implements them (GLFW initializes its Vulkan loader from VulkanLoader, as surfaces must come from the graphics device's loader, and creates surfaces for the device through VulkanPresentation), and they depend only on Core.",
		"Paths": [ "Strata/Core/Application.*", "Strata/Core/EngineModule.*", "Strata/Core/Layer.*", "Strata/Core/LayerStack.*", "Strata/Core/Window.*", "Platform/GLFW/**", "Platform/Vulkan/VulkanLoader.*", "Platform/Vulkan/VulkanPresentation.h", "Platform/NoWindow/**" ],
		"MayInclude": [ "Core", "Input" ]
	},
```

1. **Line 4:** `MaxAllowlistEntries` is 0: no include breaks the rules, and the test holds the list of exceptions to exactly this length.
2. **Lines 9–10:** a file belongs to the layer whose `Paths` match it and whose `Exclude` does not. The application shell lies in the folder `Strata/src/Strata/Core/` but belongs to `App`, so the patterns decide, not the folder.
3. **Line 11:** `Core` may include nothing: every other layer stands on it.
4. **Line 17:** `Input` may include `Core` only.
5. **Line 23:** `App` may include `Core` and `Input`.

Other fields appear further down. `Tooling` and `Option` mark the layers described above. `Notes` records why a layer is special. The `Asset` layer has `MayNotIncludeExternal`, a list of third-party header prefixes (`nvrhi/`, `vulkan/` and `vk_`), because assets record their uploads into an object the renderer provides and know no graphics interface.

The test `Architecture.Layering` reads the table and every :term[source file]{id=source-file} under `Strata/src`. It parses each `#include`, quoted or in angle brackets, and skips comments, string literals and `#if 0` blocks. Then it maps the including file and the included header to layers. It fails in four cases:

- A file lies in no layer, or in several.
- A file includes a header that its layer may not include.
- An allowlist line matches no forbidden include.
- The number of allowlist lines differs from `MaxAllowlistEntries`.

:::example[One forbidden include, read from its failure]
The test of the include checker appends one line to the end of `Strata/src/Strata/Scripting/ScriptEngine.cpp`: `#include "Strata/Physics/PhysicsSystem.h"`. The test then follows five steps.

1. The file matches the `Paths` of `Scripting` and no `Exclude`, so its layer is `Scripting`.
2. The header lies under the folder `Strata/src/Strata/Physics/`, so its layer is `Physics`.
3. The row of `Scripting` lists five layers: `Core`, `Input`, `Asset`, `Reflection` and `Scene`. `Physics` is not among them.
4. The allowlist has 0 lines, so nothing covers the include.
5. The test reports it with the file, the line and both layers.

The report is exactly one line: `Strata/Scripting/ScriptEngine.cpp(<line>): includes Strata/Physics/PhysicsSystem.h, but layer Scripting may not include layer Physics`, where the number after the file is the appended line. The fix is not to add `Physics` to the row. Scripts reach physics through a scene service, an interface in `Scene` that the physics module implements, so no include is needed.
:::

An **allowlist** is the list of known exceptions to the layer rules. Strata keeps it in `StrataTests/Architecture/LayeringAllowlist.txt`, one line for each exception with the include, the work that removes it and the reason. It can only shrink, and at the pin it is empty: the file holds comments only. A line that matches no forbidden include fails the test, so fixing an exception forces the line out, and lowering `MaxAllowlistEntries` keeps anyone from adding one.

`Architecture.Libraries` checks the other half of the table. CMake builds one static library for each layer, and the test reads the file `LayerLibraries.json`, which the :term[configure step]{id=configure-step} writes. It checks that every source file lies in the library of its one layer, and that each library links exactly the built layers its row lists. [CMake](../engineering/cmake.md) teaches how the table becomes libraries. Two more suites of the same folder, `Architecture.PrecompiledHeaders` and `Architecture.HeaderWeight`, belong to [Compiler flags and portability](../engineering/flags-portability.md).

The table has a second part, `ExternalOwners`. Each entry names header prefixes that only some folders may include, whatever their layer. `GLFW/` belongs to `Platform/GLFW/`, `vulkan/` and `nvrhi/vulkan` to `Platform/Vulkan/`, the Windows headers to `Platform/Windows/` and the Linux and macOS headers to `Platform/Posix/`. A violation reads like `Platform/Vulkan/VulkanGraphicsDevice.cpp(21): includes GLFW/glfw3.h, but only Platform/GLFW/** may include GLFW/*`. With these owners a program swaps the window backend, or the :term[operating system]{id=operating-system}, by swapping one folder; [Talking to the operating system](platform.md) teaches the folders.

:::rule[Never widen `MayInclude` or add an allowlist line]
An include that crosses sideways or upward is a design fault, not a permission missing from the table. The table is also the build, so a wider row would link the library that the row names, and one allowlist line would let the fault stay. Invert the dependency: an interface in the lower layer, a registry that the higher module fills, a scene service or an engine service. A downward dependency that is proven right may widen a row, with the reason in the layer's `Notes`. `Audio` and `Project` list `App` because each implements `EngineModule`, an interface that `App` defines; `App` includes neither of them.
:::

One more rule follows from the tooling layers. Games link no tooling: `StrataRuntime` and every exported game hold no editor, no asset pipeline and no network layer, and read cooked packs only. The CMake configure walks what the :term[runtime]{id=runtime} links and fails on a tooling layer, and a second test reads the linker's map of the built runtime. Both are the subject of [CMake](../engineering/cmake.md); this page needs only the rule, because the composition root obeys it.

## The composition root

The function `Engine::RegisterBuiltinModules` is the composition root. It lives in `Strata/src/Strata/Engine/BuiltinModules.cpp`, in the top layer `Engine`, which the table lets include every game layer and no tooling layer.

Every program that uses the engine calls it once, on the :term[main thread]{id=main-thread}, before anything reads a registry. Programs built on `Strata/src/Strata/Engine/EntryPoint.h` get the call from its `main`: the program's `CreateApplication` returns an `ApplicationLaunch`, `main` calls the root with the options in `ApplicationLaunch::Registration`, and only then makes the application. `Application` never calls the root. The test program calls it in its own `main`.

The options are the three fields of `ModuleRegistrationOptions`:

- `AssetPipeline` is a function that opens the importer registry and registers the importers. The editor passes `RegisterAssetPipeline`. `StrataRuntime` passes nothing, so the root never names an importer, and no importer is linked into a game.
- `Extra` is a list of functions that run after the modules and the asset pipeline, while the registries are still open. The editor registers its preference sections here, and a game registers its components and settings sections here.
- `Exclude` lists engine modules not to register, by name. A test uses it to learn what a game without a module does.

The root does these steps in this order:

1. The root checks its state and returns early on a second call.
2. The root opens six registries: the components, the asset loaders, the asset-manager extensions, the built-in assets, the mesh geometry and the scene systems.
3. The root runs the registration function of each module in its own table of modules, in layer order, except the modules that `Exclude` names.
4. The root runs `AssetPipeline`, then each function of `Extra`.
5. The root freezes the component registry and the settings registry.
6. The root logs the modules and the order of the scene systems.

Nine modules stand in the root's table: `Input`, `Scene`, `Renderer`, `Physics`, `Audio`, `Animation`, `Scripting`, `World` and `GameUI`. Six of them register a scene system: `Physics`, `Audio`, `Animation`, `Scripting`, `World` and `GameUI`, whose system is named `UI`. `Input` registers one settings section, `Input.Actions`. `Scene` registers two, `Scene.CollisionLayers` and `Scene.Timing`, because the layers and the fixed step belong to every build, with or without physics.

Three modules are optional. A build made with `-DSTRATA_WITH_PHYSICS=OFF`, `-DSTRATA_WITH_AUDIO=OFF` or `-DSTRATA_WITH_ANIMATION=OFF` has no library for that layer and no row in the root's table, because that table holds `#if ST_WITH_PHYSICS`, `#if ST_WITH_AUDIO` and `#if ST_WITH_ANIMATION` around those rows. Those `#if` lines may appear only in the root, the asset pipeline, the runtime program and the tests. Everywhere else, code reaches an optional module through a service that is absent without it.

A build can omit the window system too, although it is no module. A build made with `-DSTRATA_WITH_GLFW=OFF` compiles the folder `Strata/src/Platform/NoWindow/` into `App` in place of `Strata/src/Platform/GLFW/`. `Window::Create` then returns null, so its programs run only without a window. No layer has an `Option` for it and the root's table has no row for it.

`Input`, `Scene` and `Renderer` are required: excluding one logs an error and the module registers anyway; a name the table lacks logs an error and is ignored. Scripting is in the table without an `#if`, so a build cannot omit it. Strata chooses its modules when the engine is compiled, and only script modules load while a program runs. A game without physics, for example, keeps the physics components of its scenes as unknown components and saves them back unchanged, and a script that calls physics is told that the scene plays without it.

### What the root remembers

The root keeps a state, `NotRegistered`, `Registering` or `Registered`, in an atomic variable. A second call in `Registered` changes nothing and logs an error if it carries an asset pipeline or extra registrations that would be lost. A call in `Registering`, made from inside a registration function, fails a verify: a check that stays in every build and stops the program with a message. Three functions report what happened: `GetBuiltinModuleNames` lists the table of this build, `GetRegisteredModules` lists what registered (empty before the root ran), and `AreBuiltinModulesRegistered` tells whether the root has finished.

A registry used before the root opened it fails a verify too, whose message names `Engine::RegisterBuiltinModules`. A program that forgot the root stops at its first lookup, and does not run on without components or loaders. The importer registry is the one exception, because the asset pipeline opens it: in a game it stays closed, and a game that reaches for an importer stops there too.

### Two kinds of registry

Not every registry ends the same way. Two of them, the component registry and the process's settings registry, open, accept registrations and then freeze. To **freeze** a registry is to close it for good: nothing in it changes again, so any thread may read it with no lock. The others stay open.

| Registry | Layer | After the root |
| --- | --- | --- |
| `ComponentRegistry` | `Reflection` | Frozen. A later `Register` logs an error and does nothing. |
| `SettingsRegistry`, the process's | `Core` | Frozen. A later section is refused with an error. |
| `AssetLoaderRegistry` | `Asset` | Open. Each lookup takes a lock, and a later loader replaces an earlier one. |
| `AssetManagerExtensionRegistry` | `Asset` | Open. An extension applies to the asset managers made afterwards. |
| `BuiltinAssets` | `Asset` | Open. |
| `MeshGeometryRegistry` | `Asset` | Open. |
| `SceneSystemRegistry` | `Scene` | Open. A system is refused only while a scene runs. |
| `AssetImporterRegistry` | `AssetPipeline` | Opened by the asset pipeline, not the root. Open, and a later importer wins. |

The two kinds fit two jobs. The component list must never change while worker threads read it to load scenes, and the Inspector and the scene loader read it too, so the registry freezes and reads cost no lock. A tool or a test that wants to add a loader or an importer later is a normal case, so those registries stay open and pay for a lock, or a rule, on each use.

Each registry also lives in a low layer, below the modules that fill it. The figure shows the three states of the component registry.

```mermaid caption="The component registry is closed until the root opens it, open while the modules, the asset pipeline and the extra registrations register, and frozen for the rest of the program." alt="A state diagram with three states in a row. The closed state, where any use fails a verify, leads to the open state when the root opens the registry. The open state, where registration works, leads to the frozen state when the root freezes it. In the frozen state reads need no lock and a late registration is refused with an error."
stateDiagram-v2
  [*] --> Closed
  Closed --> Open: root opens it
  Open --> Frozen: root freezes it
  Closed: Closed - any use fails a verify
  Open: Open - modules, asset pipeline, extra registrations
  Frozen: Frozen - reads need no lock, late registration is refused
```

## A toy composition root

:::question[What do `::`, `static inline` and `std::function` mean?]
`Toy::Open()` names a function inside a :term[namespace]{id=namespace}, `static inline` gives a class one shared variable, and `std::function` holds any function that you can call. [Classes and objects](../basics/cpp-classes.md), [modern C++](../basics/cpp-modern.md) and [generic C++](../basics/cpp-generic.md) teach them; the comments say what each part does.
:::

The toy below does the job in about 100 lines, with two registries and three modules. The component registry has the three states of the figure, and the loader registry has none. The root registers the three modules, runs the extra registrations of a game and freezes the components. The `main` function then tries to register too early, registers too late and calls the root twice.

```cpp sketch="core-layers-registries-toy.cpp"
// A composition root with two registries: components open, accept and freeze; loaders stay open.
#include <cstdio>
#include <functional>
#include <map>
#include <string>
#include <vector>

namespace Toy
{

	enum class State
	{
		Closed,
		Open,
		Frozen
	};

	class ComponentRegistry
	{
	public:
		static void Open() { s_State = State::Open; }
		static void Freeze() { s_State = State::Frozen; }

		static bool Register(const std::string& name)
		{
			if (s_State != State::Open)
			{
				std::printf("  refused %s: the registry is %s\n", name.c_str(), s_State == State::Closed ? "closed" : "frozen");
				return false;
			}
			s_Names.push_back(name);
			return true;
		}

		static const std::vector<std::string>& GetAll() { return s_Names; }

	private:
		static inline State s_State = State::Closed;
		static inline std::vector<std::string> s_Names;
	};

	// Never frozen: a later registration replaces an earlier one.
	class LoaderRegistry
	{
	public:
		static void Register(const std::string& type, const std::string& name) { s_Loaders[type] = name; }
		static const std::string& Find(const std::string& type) { return s_Loaders[type]; }

	private:
		static inline std::map<std::string, std::string> s_Loaders;
	};

	void RegisterSceneModule() { ComponentRegistry::Register("Transform"); LoaderRegistry::Register("Scene", "built-in"); }
	void RegisterRendererModule() { ComponentRegistry::Register("MeshRenderer"); LoaderRegistry::Register("Mesh", "built-in"); }
	void RegisterPhysicsModule() { ComponentRegistry::Register("RigidBody"); }

	struct Module
	{
		const char* Name;
		void (*Register)();
	};

	constexpr Module c_Modules[] = { { "Scene", RegisterSceneModule }, { "Renderer", RegisterRendererModule }, { "Physics", RegisterPhysicsModule } };

	struct Options
	{
		std::vector<std::function<void()>> Extra;
	};

	void RegisterBuiltinModules(const Options& options)
	{
		static bool s_Registered = false;
		if (s_Registered)
		{
			std::printf("  error: called again, ignoring %zu extra registration(s)\n", options.Extra.size());
			return;
		}
		s_Registered = true;

		ComponentRegistry::Open();
		for (const Module& module : c_Modules)
			module.Register();
		for (const std::function<void()>& registration : options.Extra)
			registration();
		ComponentRegistry::Freeze();
	}

}

int main()
{
	std::printf("before the root:\n");
	Toy::ComponentRegistry::Register("Early");

	Toy::Options game;
	game.Extra.push_back([]() { Toy::ComponentRegistry::Register("Spinner"); });
	Toy::RegisterBuiltinModules(game);

	std::printf("after the root:\n");
	Toy::ComponentRegistry::Register("Late");
	Toy::LoaderRegistry::Register("Scene", "a tool's loader");
	Toy::RegisterBuiltinModules(game);

	std::printf("components:");
	for (const std::string& name : Toy::ComponentRegistry::GetAll())
		std::printf(" %s", name.c_str());
	std::printf("\nScene loader: %s\n", Toy::LoaderRegistry::Find("Scene").c_str());
	return 0;
}
```

```text output-of="core-layers-registries-toy.cpp"
before the root:
  refused Early: the registry is closed
after the root:
  refused Late: the registry is frozen
  error: called again, ignoring 1 extra registration(s)
components: Transform MeshRenderer RigidBody Spinner
Scene loader: a tool's loader
```

1. **Lines 24–33:** `Register` accepts a name only while the state is `Open`, and says why it refuses otherwise.
2. **Lines 42–51:** the loader registry has no state: it accepts a registration at any time, and the last one wins.
3. **Line 63:** the table is a name and a :term[function pointer]{id=function-pointer} for each module, in the order the root runs them.
4. **Lines 72–78:** a second call changes nothing and reports the extra registrations it ignores.
5. **Lines 80–85:** the root opens the registry, runs the modules, then the extra functions, and freezes.

The output shows the three outcomes. `Early` is refused because the registry is closed, `Late` because it is frozen, and the second call is ignored. The loader registry shows the other kind: a tool replaced the scene loader after the root, and the replacement stayed. Strata's root does the same work with more care, as the next section shows.

## The real code

The root starts from a table of modules. Search for the `#if` lines, the order, and the one place where names are listed.

```cpp src="Strata/src/Strata/Engine/BuiltinModules.cpp#L51-L77"
struct BuiltinModule
{
	std::string_view Name;
	void (*Register)();
};

// The engine's modules, lower layers first, those of the optional modules the build has. The order is also the order
// of the modules' components in ComponentRegistry::GetAll (the Inspector, Add Component, component.list). Scene systems
// order themselves against other modules' systems with soft constraints (SceneSystemDescriptor::AfterIfPresent,
// BeforeIfPresent), which apply whatever the registration order and whichever modules are present.
constexpr BuiltinModule c_BuiltinModules[] = {
	{ "Input", RegisterInputModule },
	{ "Scene", RegisterSceneModule },
	{ "Renderer", RegisterRendererModule },
#if ST_WITH_PHYSICS
	{ "Physics", RegisterPhysicsModule },
#endif
#if ST_WITH_AUDIO
	{ "Audio", RegisterAudioModule },
#endif
#if ST_WITH_ANIMATION
	{ "Animation", RegisterAnimationModule },
#endif
	{ "Scripting", RegisterScriptingModule },
	{ "World", RegisterWorldModule },
	{ "GameUI", RegisterGameUIModule },
};
```

1. **Line 54:** a module is a name and one function pointer, which is what the toy has.
2. **Lines 57–60:** the order also fixes the order of the components in the Inspector and in `component.list`. Scene systems order themselves with soft constraints, so the order of registration does not decide the order of updates.
3. **Lines 61–64:** `Input`, `Scene` and `Renderer` come first, because every engine has them.
4. **Lines 65–73:** each optional module has its row only when the build has the module. These are the `#if` lines that the rules allow.
5. **Lines 74–76:** `Scripting` has no `#if`, and `World` and `GameUI` come last.

The root is one function. The first part decides whether to run at all.

```cpp src="Strata/src/Strata/Engine/BuiltinModules.cpp#L118-L132"
void RegisterBuiltinModules(const ModuleRegistrationOptions& options)
{
	const RegistrationState state = s_State.load(std::memory_order_acquire);
	ST_CORE_VERIFY(state != RegistrationState::Registering, "Engine::RegisterBuiltinModules() is called while the engine's modules are being registered");
	if (state == RegistrationState::Registered)
	{
		// E.g. a program whose CreateApplication registered by itself before EntryPoint.h's main registers
		// launch->Registration, or a test helper that registers again in a process whose main already did.
		if (options.AssetPipeline)
			ST_CORE_ERROR("Engine::RegisterBuiltinModules() is called again with the asset pipeline, which is ignored: the modules are registered already");
		if (!options.Extra.empty())
			ST_CORE_ERROR("Engine::RegisterBuiltinModules() is called again with {} extra registrations, which are ignored: the modules are registered already", options.Extra.size());
		return;
	}
	s_State.store(RegistrationState::Registering, std::memory_order_release);
```

1. **Lines 120–121:** the state is read with acquire order, and a call during `Registering` fails a verify: a registration function must not call the root.
2. **Lines 122–131:** after a successful run, a second call returns early, and it logs an error only when it carries something that would be lost.
3. **Line 132:** the state changes to `Registering` before any registry opens.

The second part opens, registers and freezes.

```cpp src="Strata/src/Strata/Engine/BuiltinModules.cpp#L134-L161"
ComponentRegistry::BeginRegistration();
AssetLoaderRegistry::BeginRegistration();
AssetManagerExtensionRegistry::BeginRegistration();
BuiltinAssets::BeginRegistration();
MeshGeometryRegistry::BeginRegistration();
SceneSystemRegistry::BeginRegistration();

const std::vector<std::string_view> excluded = GetExcludedModules(options);
for (const BuiltinModule& module : c_BuiltinModules)
{
	if (std::find(excluded.begin(), excluded.end(), module.Name) != excluded.end())
		continue;
	module.Register();
	s_RegisteredModules.emplace_back(module.Name);
}
// Tooling, handed in by the program (see ModuleRegistrationOptions::AssetPipeline).
if (options.AssetPipeline)
	options.AssetPipeline();

for (const std::function<void()>& registration : options.Extra)
{
	if (registration)
		registration();
}

ComponentRegistry::Freeze();
SettingsRegistry::GetProcessRegistry().Freeze();
s_State.store(RegistrationState::Registered, std::memory_order_release);
```

1. **Lines 134–139:** six registries open. The importer registry is not among them.
2. **Line 141:** `GetExcludedModules` logs an error for a required or an unknown name and returns the rest.
3. **Lines 142–148:** the table runs in order, skipping the excluded modules, and each module that ran is recorded for `GetRegisteredModules`.
4. **Lines 149–157:** the tooling comes first and the extra functions after it, each only if it holds a function.
5. **Lines 159–161:** two freezes, then the state `Registered`, which later calls read.

What does a frozen registry do with a late call? The component registry decides at the start of its creation function.

```cpp src="Strata/src/Strata/Reflection/ComponentRegistry.cpp#L121-L132"
ComponentInfo* ComponentRegistry::CreateInfo(std::string name, entt::id_type typeId)
{
	RegistryData& data = GetData();
	std::scoped_lock<std::mutex> lock(data.Mutex);
	const RegistryState state = data.State.load(std::memory_order_acquire);
	ST_CORE_VERIFY(state != RegistryState::Closed, "Component '{}' is registered before Engine::RegisterBuiltinModules() opened the component registry", name);
	if (state == RegistryState::Frozen)
	{
		ST_CORE_ERROR("Component '{}' is not registered: the component registry is frozen once the engine's modules are registered "
			"(register components through Engine::ModuleRegistrationOptions::Extra)", name);
		return nullptr;
	}
```

1. **Line 124:** a :term[mutex]{id=mutex} lets one thread register at a time while the registry is open; reading after the freeze needs no lock.
2. **Lines 125–126:** a registry that was never opened fails a verify that names the root, the same check that the toy makes for a closed registry.
3. **Lines 127–132:** a frozen registry logs an error that points at `ModuleRegistrationOptions::Extra`, returns a :term[null pointer]{id=null-pointer}, and the builder that the caller holds converts to false and discards what it is given. The program continues.

The real root differs from the toy in several ways. Its state is atomic, and a call during registration fails a verify. The table has `#if` rows and a list of required modules. The root also runs `AssetPipeline`, freezes the settings registry and logs one line.

:::example[The editor's startup line]
Suppose you start the editor of a full build. Its `CreateApplication` fills `launch.Registration.AssetPipeline` with `RegisterAssetPipeline` and adds one function to `Extra`, which registers the editor's preference sections. The root then runs nine table rows, the asset pipeline and one extra function. It freezes two registries and logs one line at the info level, built from this format: `Engine modules: {}. Scene systems update in the order {}{}`.

The first braces hold the nine names in table order, `Input, Scene, Renderer, Physics, Audio, Animation, Scripting, World, GameUI`. The second hold the six systems in update order, `UI, Scripting, Animation, World, Physics, Audio`. The tests `Engine.Modules` and `Scene.Systems` check both lists. The order of systems is not the order of the modules: each system names, with soft constraints, the systems it must run before or after, so `UI` is first although `GameUI` registers last.

Now leave `Physics` out in a test. The helper of the test `Without the physics module the others register...` prints `Input Scene Renderer Audio Animation Scripting World GameUI` and the systems `UI Scripting Animation World Audio`. The other constraints still order what remains. The third braces of the format show soft constraints that name an absent system, and in a full build they are empty.
:::

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Self-registration in static constructors | The `doctest` library, which registers every `TEST_CASE` this way | A new file adds a module, with no list to edit | A linker may drop a file that nothing refers to, and the order of constructors across files is undefined |
| Extensions loaded while the program runs | Unreal Engine loads modules and extensions by name | Features added without rebuilding the engine | A stable binary interface for every engine type, a crash boundary, and one loading path for each platform |
| A registration list that a build tool writes | Godot builds the list of its modules in its :term[build system]{id=build-system} | No hand-written table to keep current | A build step and a generated file between the reader and the order |
| Registries that never freeze | Strata's own loader registry | Late registration for every table | A lock on every read, and readers that race with a writer |

Strata already uses the loaded kind in one place, game scripts, because a script crash must not end the editor. The composition root stays explicit because a table of nine rows costs less to keep than any of the other three, and because the build then decides what a program contains.

## How it is tested

Three groups of suites cover the page. `Architecture.Layering` reads the real sources and the table, and also tests the checker on small file sets built in memory, with a table of two layers. `Architecture.Libraries` reads `LayerLibraries.json`. `Engine.Modules` tests the root.

Registration happens once in a process, and the test program has already used it in its own `main`. So the cases of `Engine.Modules` that need another registration run the test program again as a child process, with `--strata-test-helper=<mode>`. The parent reads the output of the child.

Four modes matter here:

- `custom-component` registers a game component through `Extra`, then a late one that the registry refuses.
- `register-without` passes `Exclude`.
- `no-asset-pipeline` registers as a game does.
- `unregistered-registry` uses each registry before the root.

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=Architecture.Layering
build/windows/bin/Debug/StrataTests.exe --test-suite=Architecture.Libraries
build/windows/bin/Debug/StrataTests.exe --test-suite=Engine.Modules
```

The commands run the three suites on Windows, in the folder of your source build after a `Debug` build. Cases whose result depends on an optional module compare with `ST_WITH_PHYSICS` and its siblings, so they pass in a build without it.

## Changing it safely

- **A game's component or settings section** goes into `ModuleRegistrationOptions::Extra`, because the component and settings registries freeze at the end of the root. Register before the freeze or not at all.
- **A new engine module** needs a layer entry in the table, a folder that its `Paths` match, a `Register<Module>Module` function in `<Module>/<Module>Registration.cpp`, and one row in the table of the root, in dependency order. Only the root and its own module include the registration header, and a test checks it. After adding or removing source files, run the configure step again.
- **A new scene system** is made with `MakeSceneSystemDescriptor<T>` and ordered with soft constraints toward other modules.
- **A new include** between layers follows the rule above: invert the dependency, never widen the row.

:::rule[Register only through the composition root]
Registration happens only in the root, before anything reads a registry, and nothing registers after the freeze of the component and settings registries. The reason is that a registry read before it is complete shows a program with missing components, and a reader that needs no lock is safe only if the writers are gone. The other registries stay open, and tools and tests may add to them later.
:::

:::rule[Put `ST_WITH_<MODULE>` only in the root, the asset pipeline, the runtime and tests]
The three options are definitions that every target linking the engine receives from `Strata_Core`, never :term[macros]{id=macro} in a header, so no file reads one as 0 for lack of an include. Code elsewhere reaches an optional module through a service, so it needs no `#if`.
:::

Before you finish a change, run the three suites above, and in a Debug build the whole set with `ctest --preset windows-debug -j 8`.

## What went wrong before

Version 0.7.0 had a GLFW include in the Vulkan device of the renderer, which broke the plan that only the window backend knows GLFW. The old table could forbid a third-party header only for a whole layer, and the window backend and the application shell shared the `App` layer, so no layer rule could keep GLFW in one folder. The commit that added `ExternalOwners` shows the failure that the checker then printed: the Vulkan device, line 21, includes `GLFW/glfw3.h`, but only `Platform/GLFW/**` may include it. The test `0.7.0's GLFW include in the Vulkan device is reported` appends that include to the file and checks the report.

## Summary

- A file may include its own layer and the layers its row of `Layers.json` lists. `Architecture.Layering` fails any other include, and the fix is to invert the dependency, never to widen a row or add an allowlist line.
- One function, `Engine::RegisterBuiltinModules`, registers every module from a table in layer order, so no linker drops a module and no order is left to chance.
- The component and settings registries open, accept and freeze, and need no lock afterwards; the loader, extension, built-in asset, mesh geometry, scene-system and importer registries stay open with their own rules.
- A game or a tool registers components and settings sections through `ModuleRegistrationOptions::Extra`, and a registration after the freeze is refused with an error.
- The root logs its order and can be followed from `main`: it opens six registries, runs nine modules, the asset pipeline and `Extra`, then freezes two registries.

## Check yourself

1. Which of these includes fails `Architecture.Layering`? (a) A `Renderer` file includes a `Scene` header. (b) A `Scene` file includes a `Renderer` header. (c) A `Physics` file includes a `Scene` header. (d) An `Audio` file includes an `App` header.

   :::answer{tests="layer-rule"}
   (b) fails. The row of `Scene` lists `Core`, `Asset` and `Reflection`, and `Renderer` is above it. (a) and (c) pass, because the rows of `Renderer` and `Physics` list `Scene`. (d) passes too, although `App` is no data layer: the row of `Audio` lists it as a downward dependency, with the reason in its `Notes`.
   :::

2. A team makes each module register itself with a global object in a file of its static library. A build has 8 of the 9 modules and no error. What probably happened, and what does Strata do instead?

   :::answer{tests="composition-root"}
   The linker dropped the object file of the missing module, because no code referred to a symbol in it. Strata calls each module's `Register<Module>Module` from the table of `Engine::RegisterBuiltinModules`, so a reference to every function exists and no linker can drop it. The call order is also written in the table, where self-registration would leave it to the compiler.
   :::

3. After the root ran, a tool registers a second loader for the scene asset type, and a game registers the component `Late`. What happens to each?

   :::answer{tests="two-registries,register-game"}
   The loader registry stays open, so the tool's loader replaces the earlier one. The component registry is frozen, so `Late` is refused: an error is logged that points at `ModuleRegistrationOptions::Extra`, the builder converts to false, and the program continues. The game should have put the registration into `Extra`.
   :::

4. An `Extra` function of a game calls `Engine::RegisterBuiltinModules` again. In which state is the root, and what happens?

   :::answer{tests="trace-root"}
   The root is in `Registering`, because `Extra` runs before the state changes to `Registered`. The first check of the function fails a verify with the message that the root is called while the modules register, and the program stops. A call in `Registered` would only log an error and return.
   :::

5. A game is built with all three optional modules off. How many rows does the root's table hold, and how many game layers does the build make?

   :::answer{tests="composition-root"}
   The table holds 9 - 3 = 6 rows: `Input`, `Scene`, `Renderer`, `Scripting`, `World` and `GameUI`. The layer table has 19 layers; the three tooling layers are no game layers, which leaves 19 - 3 = 16, and without the three options 16 - 3 = 13 game layers are built.
   :::

## Exercises

1. **Basic.** Add `#include <GLFW/glfw3.h>` to a file of `Strata/src/Strata/Scene/`. Say which suite fails and what its report line says, then fix the file by inversion when it wanted the refresh rate of the monitor.

   :::answer[Worked solution]{tests="layer-rule"}
   `Architecture.Layering` fails. `GLFW/` has an owner in `ExternalOwners`, so the report reads `<file>(<line>): includes GLFW/glfw3.h, but only Platform/GLFW/** may include GLFW/*`. Neither widening the row of `Scene` nor an allowlist line is allowed. Instead, define in `Core`, which `Scene` may include, an interface that returns the rate. The code in `Platform/GLFW/` implements it, and the application hands it to the scene, as `InputWindow` is handed to `Input`.
   :::

2. **Medium.** A game has a component `Spinner` with a field `Speed`. Write the registration that goes into `Extra`, then add a second registration of `Late` after the root. Say what each does.

   :::answer[Worked solution]{tests="register-game"}
   A game's `CreateApplication` fills `launch.Registration.Extra` with one function. The function registers `Spinner` with `ComponentRegistry::Register<Spinner>("Spinner")` and chains `.Property("Speed", &Spinner::Speed)`. The root runs it while the registry is open, so `Spinner` registers. A call such as `ComponentRegistry::Register<Late>("Late")` at any later point logs the error `Component 'Late' is not registered: the component registry is frozen`, with the hint about `Extra`, and `ComponentRegistry::Find("Late")` returns null. The test `A game registers its components through ModuleRegistrationOptions::Extra` does both in a child process.
   :::

3. **Medium.** A test helper passes `Exclude` with `Physics`, `Scene` and a name that no module has. Write a small program that applies the rule of the root to this list of six modules and prints what registers.

   :::answer[Worked solution]{tests="two-registries"}
   The program tests each name. A required name logs an error and stays; an unknown name logs an error and is ignored; any other name is omitted. This is the exclusion step of the root, `GetExcludedModules`, on a shorter table.

   ```cpp sketch="core-layers-registries-exclude.cpp"
   // The root's exclusion step: required and unknown names are refused, the others are left out.
   #include <algorithm>
   #include <array>
   #include <cstdio>
   #include <string>
   #include <string_view>
   #include <vector>

   namespace
   {

   	constexpr std::array<std::string_view, 6> c_Modules = { "Input", "Scene", "Renderer", "Physics", "Audio", "Scripting" };
   	constexpr std::array<std::string_view, 3> c_Required = { "Input", "Scene", "Renderer" };

   	template<typename List>
   	bool Contains(const List& list, std::string_view name)
   	{
   		return std::find(list.begin(), list.end(), name) != list.end();
   	}

   	std::vector<std::string_view> GetExcluded(const std::vector<std::string>& names)
   	{
   		std::vector<std::string_view> excluded;
   		for (const std::string& name : names)
   		{
   			if (Contains(c_Required, name))
   				std::printf("error: the %s module cannot be excluded; it is registered\n", name.c_str());
   			else if (!Contains(c_Modules, name))
   				std::printf("error: %s is no module of this build\n", name.c_str());
   			else
   				excluded.push_back(name);
   		}
   		return excluded;
   	}

   }

   int main()
   {
   	const std::vector<std::string> exclude = { "Physics", "Scene", "Teleportation" };
   	const std::vector<std::string_view> excluded = GetExcluded(exclude);

   	std::printf("registered:");
   	for (std::string_view module : c_Modules)
   	{
   		if (!Contains(excluded, module))
   			std::printf(" %.*s", static_cast<int>(module.size()), module.data());
   	}
   	std::printf("\n");
   	return 0;
   }
   ```

   ```text output-of="core-layers-registries-exclude.cpp"
   error: the Scene module cannot be excluded; it is registered
   error: Teleportation is no module of this build
   registered: Input Scene Renderer Audio Scripting
   ```

   1. **Lines 26–27:** a required module logs an error and is not excluded.
   2. **Lines 28–29:** an unknown name logs an error and is ignored.
   3. **Line 31:** only a known, optional module reaches the excluded list.
   4. **Lines 44–48:** the loop prints the modules that remain.

   In the real engine the list of a full build is `Input Scene Renderer Audio Animation Scripting World GameUI` after `Physics` goes, and the physics components of a scene load as unknown components.
   :::

4. **Hard.** Trace it yourself. Set breakpoints from `main` into `Engine::RegisterBuiltinModules` in a Debug build of the editor. Write down which registries it opens, in which order the modules run, and which two registries it freezes. Compare your list with the editor's startup log.

   :::answer[Worked solution]{tests="trace-root"}
   Start in `main` of `Strata/src/Strata/Engine/EntryPoint.h`, where the call stands after `CreateApplication` and before `launch->Create()`. Step into `RegisterBuiltinModules` in `Strata/src/Strata/Engine/BuiltinModules.cpp`. You see six `BeginRegistration` calls (components, asset loaders, manager extensions, built-in assets, mesh geometry, scene systems), then the table run: `Input`, `Scene`, `Renderer`, `Physics`, `Audio`, `Animation`, `Scripting`, `World`, `GameUI`. Then `RegisterAssetPipeline` opens the importer registry, then one extra function registers the editor's preference sections. The last two calls freeze `ComponentRegistry` and the process's `SettingsRegistry`, and the log line afterwards repeats the nine names and the six systems.
   :::

## Where it lives in Strata

- `StrataTests/Architecture/Layers.json` and `LayeringAllowlist.txt`: the layer table and the empty list of exceptions.
- `StrataTests/src/Architecture/LayeringTests.cpp`, `LayeringAnalyzer.cpp` and `LibrariesTests.cpp`: the suites `Architecture.Layering` and `Architecture.Libraries`.
- `Strata/src/Strata/Engine/BuiltinModules.cpp` and `BuiltinModules.h`: `RegisterBuiltinModules`, `ModuleRegistrationOptions`, `GetBuiltinModuleNames`, `GetRegisteredModules` and `AreBuiltinModulesRegistered`.
- `Strata/src/Strata/Engine/EntryPoint.h`: the `main` that calls the root. `StrataEditor/src/EditorApplication.cpp`: the editor's options.
- `Strata/src/Strata/Reflection/ComponentRegistry.cpp` and `Strata/src/Strata/Core/SettingsRegistry.h`: the two registries that freeze.
- `StrataTests/src/Engine/BuiltinModulesTests.cpp`: the suite `Engine.Modules`, with the helper modes in `StrataTests/src/Engine/ModuleRegistrationHelpers.cpp`.

## Further reading

- cppreference, "Initialization": what the language says about the order of static initialization across files; intermediate.
- Robert Nystrom, Game Programming Patterns, the chapter "Service Locator": how a program finds a service without a global that knows its type; beginner.
- Godot Engine documentation, "Custom modules in C++": how an engine module registers its classes; intermediate.
- Epic Games, "Unreal Engine Modules": how the engine splits into modules that load by name; advanced.
