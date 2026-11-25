---
id: core/map
title: "How Strata is put together: programs, libraries, modules and layers"
description: "Which programs, libraries and script modules make up Strata, and the four words that each mean two things."
kind: concept
size: M
tracks: [E]
needs: [basics/build, start/what-an-engine-is]
time: 40
learn:
  - id: program-library-split
    text: name the programs and libraries Strata is built from, and explain why the runtime holds no editor code
  - id: compare-approaches
    text: compare three ways an engine can split its code into programs, libraries and modules
  - id: script-module
    text: explain what a script module links and why game code lives in one
  - id: place-file
    text: find the program and the library that hold a given source file of Strata
  - id: two-meanings
    text: name which meaning of module, layer, registry and service a sentence uses
since: 0.4.0
status: final
---

In [your first game](../start/first-game.md) you started the editor, played a copy of the `Tetris` sample and built the
`Spinner` script. Ask now where "the engine" was during all that. The window you clicked in belongs to the program
`StrataEditor`. The Play button ran the game inside that window.

The build of `Spinner` made a file of its own, which the editor loaded while it ran. Three different pieces worked
together, and each has its own place in the repository.

The question matters as soon as you read or change Strata's code. A person who asks "which program runs this, and which
library holds it?" finds the right folder at once. A person who guesses adds a call that works in the editor and breaks
the shipped game.

The page names files of Strata's source, such as `StrataTests/Architecture/Layers.json`. The installed Strata holds no
source files, so read them on GitHub, in
[the engine's files at the book's commit](https://github.com/2042Third/GameEngine/tree/319075e3f92b316db5cdd30560de08c1ffe0ae26).
The [next page](first-change.md) makes a clone of your own.

## The editor is not the engine

The first picture most people form is that Strata is one big program, the editor, and that a game is a scene inside it.
The picture breaks at the first export. **File ▸ Export Game...** writes a folder that players run without the editor.
A program that plays the game without the editor cannot be the editor.

Two more facts break it. The command-line program `StrataCLI` drives a running editor from outside, so it needs only the
engine's network code. The test program `StrataTests` runs the engine's code in a process with no editor window at all.

A second picture says the engine is one big library and each program adds a little code. That fails as well. The editor
needs importers, which read model and image files, and a network server for automation. A shipped game needs neither,
and code a game carries is code its players download, load and must trust.

## Libraries below, programs above, modules beside

Here is the model in one paragraph. An engine is a set of libraries. A program is a small starting point, a `main`
function, plus the libraries it needs. Game code is a module of its own: a file that the program loads while it runs.
[Linking](../basics/build.md) joins the first two when the program is built, and loading joins the third later.

The map below shows them for Strata. An arrow means "links". A box named `Strata_<Layer>` is the library of one layer,
and the boxes `Strata` and `StrataTooling` bundle many of them.

```mermaid caption="Programs link libraries; script modules link only the script core; the runtime reaches no tooling library." alt="A diagram in which the editor program links the editor's interface library, which links the editor core library and the interface-drawing layer. The editor core links the game layers, the asset pipeline layer and the network layer. The runtime program links only the game layers, the command-line program only the network layer, and script modules only the script core. The test program links the game layers, the tooling layers and the editor and command-line libraries."
flowchart TD
	Editor["StrataEditor"] --> EditorUI["StrataEditorUI"]
	EditorUI --> ImGui["Strata_ImGui"]
	EditorUI --> EditorCore["StrataEditorCore"]
	EditorCore --> Game["Strata: the game layers"]
	EditorCore --> Pipeline["Strata_AssetPipeline"]
	EditorCore --> Network["Strata_Network"]
	Runtime["StrataRuntime"] --> Game
	CLI["StrataCLI"] --> Network
	Tests["StrataTests"] --> Game
	Tests --> Tooling["StrataTooling: the tooling layers"]
	Tests --> EditorUI
	Tests --> CLILib["StrataCLILib"]
	Scripts["script modules"] --> ScriptCore["StrataScriptCore"]
```

Follow the arrows from `StrataRuntime`. They reach the game layers and nothing else: no editor library, no importer, no
network code. The editor reaches those too, and so reaches everything.

## How engines split their code

Engines choose among three splits, and each one answers the flaw of the one before.

The first split is one program with the tools inside. It is the simplest to build: one target, one link. Its flaw shows
at the first shipped game, which carries the whole editor, because no one can tell which parts the game uses.

The second split puts the engine in libraries under several programs: an editor, a player, command-line tools. Each
program links only what it needs, so the player is free of tools. Its flaw is that the game's own code is still part of
the player, so every change to a script builds and links the whole program again, and a crash in game code stops it.

The third split loads modules while the program runs. Game code becomes a file that the program opens and closes, so it
can change without a new start. Its flaw is the boundary: the program and the module must agree on the layout of every
piece of data they share, and C++ gives no such promise between different :term[compilers]{id=compiler}.

| Approach | Cost | Quality | Complexity | Used by |
| --- | --- | --- | --- | --- |
| One program, tools inside | One link step; every game ships its tools | Nothing proves what a game holds | Lowest | Godot's editor build; its export templates strip the tools |
| Libraries under several programs | One link step per program; a table of who may link whom | A game holds only what it links, and a check can prove it | Medium | Strata; Unreal Engine, where editor modules stay out of a packaged game |
| Modules loaded while running | A stable boundary to design and keep | Game code changes without a new start, and a crash can stay inside | Highest | Unity, which loads compiled script assemblies; Strata, for game code only |

Strata uses the second split for the engine and the third for game code only. [Further reading](#further-reading) names
the sources of the last column.

## One static library for each layer

Strata's libraries follow a table. The file `StrataTests/Architecture/Layers.json` lists the engine's **architecture
layers** from the bottom up, each as a row: a name, the folders it owns (`Paths`, minus `Exclude`) and the layers whose
headers it may include (`MayInclude`). The table lists 19 layers. :term[CMake]{id=cmake} reads it and builds one
:term[static library]{id=static-library} for each row, named `Strata_<Layer>`, which links exactly the layers of its
`MayInclude`. [Layers and registries](layers-registries.md) teaches how the table is enforced.

:::example[What do three libraries link?]
Read three rows. `Core` has `MayInclude` of `[]`, so `Strata_Core` links no other engine library: it is the bottom.
`Scene` has `[Core, Asset, Reflection]`, so `Strata_Scene` links three. `Renderer` lists six layers, `Core`, `Input`,
`App`, `Asset`, `Reflection` and `Scene`, so `Strata_Renderer` links six.

Now count what the programs link. Three rows carry `Tooling`: `Network`, `ImGui` and `AssetPipeline`. The other 16 rows
are the layers a game contains, with the three optional ones (physics, audio, animation) on, as they are by default.
`Strata` links those 16, and `StrataRuntime` links `Strata` alone: 16 of the 19.

`StrataEditorCore` adds `Strata_AssetPipeline` and `Strata_Network`, which makes 18, and `StrataEditorUI` adds
`Strata_ImGui`: all 19.
:::

Three programs and a test program stand on that base.

- `StrataEditor` is a `main` over two static libraries of its own. `StrataEditorCore` is the editor without a user
  interface, and `StrataEditorUI` is the interface, drawn with Dear ImGui, a library for buttons and panels.
- `StrataRuntime` plays exported games and links `Strata` only.
- `StrataCLI` is a thin `main` over `StrataCLILib`, which links `Strata_Network` only. It talks to a running editor over
  a local connection and starts none of the engine's modules.
- `StrataTests` links everything, so that tests can draw the editor without a window and reach every layer.

The editor and the :term[runtime]{id=runtime} share one starting point, the `main` of `Strata/src/Strata/Engine/EntryPoint.h`. Each program
defines what it creates, and `main` does the same work around it.

:::question[What do `->`, `Scope` and `std::optional` mean?]
The arrow `->` follows a pointer, `Scope` owns what it points to, and `std::optional` holds a value that may be missing;
[pointers and memory](../basics/cpp-memory.md) and [modern C++](../basics/cpp-modern.md) teach them. You can follow the
fence below without them.
:::

The fence shows the middle of `main`. Look at the order of the steps: the program's own code first, then the
composition root, the one function that registers every engine module, and the application last.

```cpp src="Strata/src/Strata/Engine/EntryPoint.h#L25-L35" from="std::optional<Strata::ApplicationLaunch> launch = Strata::CreateApplication(commandLine);" to="application->Run();" symbol="main"
std::optional<Strata::ApplicationLaunch> launch = Strata::CreateApplication(commandLine);
if (!launch || !launch->Create)
	return Strata::Application::GetStartupExitCode();

// The composition root, before anything touches a registry: the application, its layers and its modules all may.
Strata::Engine::RegisterBuiltinModules(launch->Registration);

Strata::Scope<Strata::Application> application = launch->Create();
if (!application)
	return Strata::Application::GetStartupExitCode();
application->Run();
```

1. **Line 25:** the program's own code decides what it launches. The editor returns its editor application, the runtime its player.
2. **Line 30:** the composition root registers every engine module, before anything touches a registry.
3. **Lines 32–35:** only now does the program's `Application` exist, and the loop runs until the program ends.

The repository's folders lie on the same map.

| Folder | What it holds | What the build makes |
| --- | --- | --- |
| `Strata/` | The engine's modules and platform code | The `Strata_<Layer>` libraries, `Strata`, `StrataTooling` |
| `StrataEditor/` | The editor | `StrataEditorCore`, `StrataEditorUI`, `StrataEditor` |
| `StrataRuntime/` | The player of exported games | `StrataRuntime` |
| `StrataScriptCore/` | A C header and a C++ kit for scripts | The interface library `StrataScriptCore` |
| `StrataCLI/` | The automation client | `StrataCLILib`, `StrataCLI` |
| `StrataTests/` | The tests and the layer table | `StrataTests` |

Installing Strata copies three programs, `StrataEditor`, `StrataRuntime` and `StrataCLI`, to the top of its folder. The
test program stays in the build.

### Game code stays outside the engine

A game's scripts belong to none of those libraries. They form a **script module**: a :term[shared library]{id=shared-library}
that `strata_add_script_module` builds against `StrataScriptCore` alone and that a program loads while it runs. The file
ends in `.dll` on Windows, `.so` on Linux and `.dylib` on macOS. The `Tetris` sample builds its module this way, from
`Samples/Tetris/Scripts/CMakeLists.txt`.

`StrataScriptCore` holds a C header, the application binary interface (ABI) between engine and module, and a C++ kit that
wraps it. A module never links the engine, and the engine includes only the C header. Only plain data crosses the
boundary, and the engine guards every call into the module, so a crashing script stops the game and not the editor. A
changed script loads again while the editor runs.
[Loading a script module](../scripting/loading.md) teaches how the engine opens and calls one.

:::why[Why one library for each layer, and not one for the whole engine?]
Because the build then follows the table. Each library links exactly the layers its row lists, and the test
`Architecture.Layering` checks every include against the table. A :term[source file]{id=source-file} that no row owns, or that two rows own, stops the
configure and names the file.

At the end of the configure, a check walks everything `StrataRuntime` links and fails when a tooling layer appears. The
test `StrataRuntime.NoTooling` repeats the proof on the linker's own map of the built program.

The price is 19 targets, a table to keep current, and a rule that every :term[source file]{id=source-file} belongs to
exactly one row. The reward is that "games contain no tooling" is a fact the build checks, not a promise.
[The CMake page](../engineering/cmake.md) shows how the table becomes libraries.
:::

## Module: three things with one name

The word "module" appears in three places, and a sentence rarely says which.

An **engine module registration** is the one function, `Register<Module>Module`, that an engine folder offers to add its
components, asset loaders, scene systems and settings to the engine's tables at startup. The folder
`Strata/src/Strata/Scene/` has `RegisterSceneModule`. The composition root, `Engine::RegisterBuiltinModules`, calls them
in order: `Input`, `Scene`, `Renderer`, `Physics`, `Audio`, `Animation`, `Scripting`, `World` and `GameUI`. It runs once,
before the application exists.

An `EngineModule` is a different thing: a service that a program starts and keeps until it ends, with hooks that the
:term[frame loop]{id=game-loop} calls. The editor lists four in its `ApplicationSpecification::Modules`: graphics, audio,
Dear ImGui and the project. The runtime lists three, without Dear ImGui. [Engine modules](engine-modules.md) teaches the
hooks and their order.

The two sets share little more than a word. The graphics module is an `EngineModule` in the `Renderer` layer, while that
layer registers through `RegisterRendererModule`. The project and ImGui modules have no `Register<Module>Module` at all,
and none of the editor's four has the name `Scene`, `Physics` or `World`. Only audio has both, which is why the word hides
the difference.

The third use is the script module. The table sets the three side by side.

| Use | What it is | Lives | Runs |
| --- | --- | --- | --- |
| Engine module registration | A function in an engine folder | In the engine's libraries | Once at startup, before the application |
| `EngineModule` | An object with frame hooks | In the application | From the program's start to its end |
| Script module | A shared library of game code | In a file of the game | When the program loads it, and again after a reload |

## Layer: two things with one name

The second word is "layer". An **application layer**, the class `Layer` in a `LayerStack`, is a slice of a program's own
behaviour. `EditorLayer` draws the editor, and the runtime's layer plays the game. The stack updates its layers in order
and gives them events in reverse order, so the top one sees input first.

The other meaning is the architecture layer: a row of `Layers.json`, a group of engine folders and the static library
built from it. The `Renderer` layer is a library, and it is never a member of a `LayerStack`.

The two meet in one file. The class `Layer` is defined in `Strata/src/Strata/Core/Layer.h`, in the folder `Core`, but the
table gives that file to the architecture layer `App`, because the `Exclude` list of `Core` names the `Layer` files. So
`Layer.h` holds an application layer and lives in an architecture layer. Ask of any "layer" whether the program pushes it
onto a stack or the table lists it as a row.

## Registry: two things with one name

A **registry** in Strata's meaning is a table that modules fill at startup. One holds the component types, one the asset
loaders, one the scene systems and one the settings sections. The component and settings registries open, accept
registrations and then close, while the loader and scene-system registries stay open with rules of their own. After
`RegisterBuiltinModules` has run, the component and settings registries are frozen: they never change again, so any
thread can read them without a lock.

The other registry is `entt::registry`, from the EnTT library. It stores the entities of one scene and the values of
their components, and `Scene::GetRegistry()` returns it. Strata's registry knows what kinds exist: that a
`TransformComponent` has a position, a rotation and a scale. EnTT's registry holds the instances: the position of one
entity.

[Layers and registries](layers-registries.md) teaches the first, and [entities](../world/ecs.md) the second.

## Service: two things with one name

A **service** is an interface, a class of functions with no code of its own, that one part of the engine offers and another part uses, without the second including the
first. The word has two senses, which differ by lifetime.

An **engine service** belongs to the whole process. `EngineServices::Register` makes a provider the process's provider of
an interface, and `EngineServices::Get` returns it, or null when nothing provides it. The game's window, the save files
and the graphics options are such interfaces. A caller treats null as a missing feature.

A **scene service** belongs to one running scene. A system registers it with `Scene::RegisterService`, and
`Scene::GetService` finds it. The physics system offers queries such as `IPhysicsQueries` this way and removes them when
the scene stops. The `Scripting` layer may not include `Physics`, so scripts reach physics through that interface, which
the `Scene` layer defines. [Engine modules](engine-modules.md) teaches the first, and
[scene systems](../world/systems.md) the second.

:::example[Read one sentence for its meanings]
Take the note on the `Audio` row of the table, in short: "`Audio` may include `App`, because the Audio module implements an
`EngineModule`." The words `Audio` and `App` in code are rows of `Layers.json`: architecture layers. "The Audio module"
is the folder and its registration. The `EngineModule` is the object the program runs. So the sentence uses "layer" in one
sense and "module" in two.

Now change a sentence: "The `Audio` layer is pushed onto the stack." That uses the other meaning of "layer", an
application layer, and it is wrong for `Audio`, because architecture layers are never pushed anywhere.
:::

## What Strata's choice cannot do

- The engine's code is linked in. Only game code reloads while a program runs, and nothing loads an engine module from a
  file, so a change to the engine means a build and a new start. The [appendix of what Strata lacks](../appendix/not-in-strata.md)
  says so.
- The table must stay true. A new source file goes into one row, and CMake finds it only after the :term[configure step]{id=configure-step} runs
  again. A dependency in the wrong direction fits no row, so the code must change shape, for example with an interface
  in a lower layer.
- A script module sees only the C boundary. It cannot call an engine function that the boundary does not list, and it
  cannot use an engine type.
- A shipped game contains no tools. It cannot import a model or serve automation, and it reads the files the editor
  prepared.

## Common mistakes

- **Taking the editor for the engine.** The symptom: you search `StrataEditor/` for the engine's code, or you think
  players need the editor. The fix: the engine is `Strata/`, the editor is a program on top of it, and a player starts
  `StrataRuntime`.
- **Reading the wrong meaning of a word.** The symptom: "add a layer" sends you to write a class when the plan meant a new
  row of the table, or "register a module" makes you write an `EngineModule`. The fix: ask whether the word names a row
  of `Layers.json` or an object in a program, a function that runs once or a service that lives on.
- **Including a tool in a game layer.** The symptom: the configure stops with a message that names a tooling library on
  the path of `StrataRuntime`, or the test `Architecture.Layering` fails. The fix: do not widen the table. Define an
  interface in a lower layer and let the higher one provide it.
- **Searching for a registration function of every engine module.** The symptom: no `RegisterProjectModule` exists. The
  fix: only the folders of the registration list have one, and an `EngineModule` is a different thing.

## Summary

- Strata is one static library for each of 19 layers, three installed programs (`StrataEditor`, `StrataRuntime`,
  `StrataCLI`) and a test program. `StrataRuntime` links only the 16 game layers, and a configure check and a test prove
  it holds no tooling.
- An engine can be one program with tools inside, libraries under several programs, or modules loaded while running.
  Strata uses the second for the engine and the third for game code.
- A script module is a shared library of game code, built against `StrataScriptCore` alone, so that a crashing or changed
  script touches the game and not the program that loads it.
- A file's place follows its folder: a `Strata/src` file belongs to the row of `Layers.json` whose `Paths` match and whose
  `Exclude` does not, and every other top folder is its own program or library.
- Module, layer, registry and service each name two or three things, and the sentence shows which by naming a function, a
  row of the table, an object or an interface.

## Check yourself

1. A player opens an exported game on a computer where Strata is not installed. Which program runs the game:
   `StrataEditor`, `StrataRuntime`, `StrataCLI` or `StrataTests`?

   :::answer{tests="program-library-split"}
   `StrataRuntime`, renamed after the game by the export. `StrataEditor` is the tools, and the game does not ship it.
   `StrataCLI` only drives an editor, and `StrataTests` is a test program that nobody installs. The runtime links the game
   layers alone, so it needs no editor.
   :::

2. The row of `Physics` has `MayInclude` of `[Core, Asset, Reflection, Scene]`. How many layer libraries does
   `Strata_Physics` link, and does it link `Strata_Renderer`?

   :::answer{tests="program-library-split"}
   `Strata_Physics` links four, one for each entry. It does not link `Strata_Renderer`, because the row does not list `Renderer`.
   Physics code that included a :term[renderer]{id=renderer} header would fail the layering test.
   :::

3. A teammate wants players of a shipped game never to run an importer. Which of the three splits lets you prove that, and
   which check does Strata run?

   :::answer{tests="compare-approaches"}
   The second split, libraries under several programs. The importers live in the tooling layer `AssetPipeline`, which
   `StrataRuntime` does not link. The configure walks what the runtime links and fails on a tooling layer, and the test
   `StrataRuntime.NoTooling` reads the linker map. The first split cannot prove it, and the third does not decide it.
   :::

4. Your script module crashes in its `OnUpdate`. Which libraries did it link, and why did the editor stay alive?

   :::answer{tests="script-module"}
   Only `StrataScriptCore`, with glm, the math library behind it, and never the engine. The engine includes only the C
   header and calls the module across a boundary of plain data, so it can contain what goes wrong inside the module.
   :::

5. Which meaning does each use have? (a) "`EditorLayer` is pushed onto the layer stack." (b) "`Scripting` is a layer that
   may include `Scene`." (c) "`Scene::GetService<T>` returns null when no system offers T."

   :::answer{tests="two-meanings"}
   (a) An application layer, an object of a `LayerStack`. (b) An architecture layer, a row of `Layers.json` and a static
   library. (c) A scene service, because it belongs to a running scene and not to the process.
   :::

6. The file `Strata/src/Strata/Core/Application.cpp` lies in the folder `Core`. Which library holds it?

   :::answer{tests="place-file"}
   `Strata_App`. The `Core` row lists the `Application` files under `Exclude`, and the `App` row lists them under
   `Paths`. The folder alone does not decide the layer: the table does.
   :::

## Exercises

1. **Basic.** For each of six files, name the program that uses it and the library or module that holds it:
   `Strata/src/Strata/Engine/EntryPoint.h`, `StrataEditor/src/Panels/ActivityPanel.cpp`,
   `Samples/Tetris/Scripts/TetrisGame.cpp`, `Strata/src/Platform/GLFW/GLFWWindow.cpp`,
   `Strata/src/Strata/Core/JobSystem.cpp` and `StrataTests/src/Architecture/LayeringTests.cpp`. Use `Layers.json` and the
   folder table above.

   :::answer[Worked solution]{tests="place-file"}
   `EntryPoint.h` lies in the folder of the `Engine` layer, so `Strata_Engine` holds it, and the editor and the runtime
   both use it. `ActivityPanel.cpp` is a panel of `StrataEditorUI`, in the program `StrataEditor`. `TetrisGame.cpp` is in
   the script module `TetrisScripts`, which links `StrataScriptCore`.

   `GLFWWindow.cpp` lies in `Strata/src/Platform/GLFW/`, which the `App` layer owns. `JobSystem.cpp` lies in
   `Strata/src/Strata/Core/`, so `Strata_Core` holds it. Both are game layers, so the editor, the runtime and the tests use them. `LayeringTests.cpp` is in the program `StrataTests`.
   :::

2. **Medium.** In a terminal, run the installed `StrataEditor --help` and `StrataRuntime --help`. Count the options of
   each, list those they share, and say which program holds the editor's tools.

   On Windows both are windowed programs, which PowerShell does not wait for. Send their output to `Out-Host`, so that
   PowerShell waits and prints it in order. In the folder of the installed Strata, run:

   ```powershell
   .\StrataEditor.exe --help | Out-Host
   .\StrataRuntime.exe --help | Out-Host
   ```

   Each program prints `Usage:` and `Options:`, then one line per option.

   :::answer[Worked solution]{tests="program-library-split"}
   The editor lists 17 options and the runtime 12 (each program's `c_Arguments`, in `StrataEditor/src/EditorApplication.cpp`
   and `StrataRuntime/src/RuntimeApplication.cpp`). They share five: `--headless`, `--windowed`, `--frames`,
   `--screenshot` and `--help`. Twelve belong to the editor alone, among them `--project`, `--commands` and
   `--automation-port`: they open projects, run command scripts and serve automation. Seven belong to the runtime alone,
   such as `--game`, `--seconds` and `--quality`. Only the editor offers to open a project and serve commands, so it holds
   the tools.
   :::

3. **Hard.** Write a program that decides in which layer a file belongs from a table of `Path` and `Exclude` prefixes.
   Make it show a file that no layer owns and a file that two layers own.

   :::answer[Worked solution]{tests="place-file" solution="sketches/core-map-placement.cpp"}
   The program keeps three rows of the real table, with folder prefixes in place of globs, and adds a made-up row,
   `Clash`, that overlaps `Engine`. A row owns a file when the file starts with its `Path` and not with its `Exclude`.

   ```cpp sketch="core-map-placement.cpp"
   // Places files in layers: a layer owns a file that starts with its Path, unless it starts with its Exclude too.
   #include <cstdio>
   #include <string>
   #include <vector>

   struct Layer
   {
   	std::string Name, Path, Exclude;
   };

   int main()
   {
   	const std::vector<Layer> table = { { "Core", "Strata/Core/", "Strata/Core/Application" }, { "App", "Strata/Core/Application", "" },
   		{ "Engine", "Strata/Engine/", "" }, { "Clash", "Strata/Engine/Entry", "" } };
   	for (const std::string file : { "Strata/Core/JobSystem.cpp", "Strata/Core/Application.cpp", "Strata/Engine/EntryPoint.h", "Strata/Foo/Bar.cpp" })
   	{
   		std::string owners;
   		for (const Layer& layer : table)
   			if (file.starts_with(layer.Path) && (layer.Exclude.empty() || !file.starts_with(layer.Exclude)))
   				owners += " " + layer.Name;
   		std::printf("%-30s%s\n", file.c_str(), owners.empty() ? " none: the configure fails" : owners.c_str());
   	}
   }
   ```

   ```text output-of="core-map-placement.cpp"
   Strata/Core/JobSystem.cpp      Core
   Strata/Core/Application.cpp    App
   Strata/Engine/EntryPoint.h     Engine Clash
   Strata/Foo/Bar.cpp             none: the configure fails
   ```

   1. **Lines 13–14:** `Core` excludes the `Application` files, and `App` owns them, as in the real table.
   2. **Line 15:** each file in turn is placed by asking every row.
   3. **Line 19:** the rule: the path matches and the exclude does not.
   4. **Line 21:** a file with no owner prints a failure, and a file with two owners prints both names. The real
      configure stops on either and names the file.
   :::

## Where it lives in Strata

- `StrataTests/Architecture/Layers.json`: the layer table, with `Paths`, `Exclude`, `MayInclude`, `Tooling` and `Option`.
- `CMake/StrataLayers.cmake`: `strata_add_layer_libraries` and `strata_check_link_closure`. `Strata/CMakeLists.txt`: the
  interface libraries `Strata` and `StrataTooling`. `CMake/StrataPackaging.cmake`: the three installed programs.
- `StrataEditor/CMakeLists.txt`, `StrataRuntime/CMakeLists.txt`, `StrataCLI/CMakeLists.txt` and
  `StrataScriptCore/CMakeLists.txt`: the other targets. `StrataScriptCore/CMake/StrataScriptModule.cmake`:
  `strata_add_script_module`.
- `Strata/src/Strata/Engine/EntryPoint.h` and `BuiltinModules.cpp`: `main`, `RegisterBuiltinModules` and the list of engine
  modules. `Strata/src/Strata/Core/EngineModule.h`, `Layer.h` and `LayerStack.h`: the `EngineModule`, `Layer` and
  `LayerStack`.
- `Strata/src/Strata/Core/EngineServices.h` and `Strata/src/Strata/Scene/SceneServices.h`: the two kinds of service.
- Tests: `Architecture.Layering` and `Architecture.Libraries` (`StrataTests/src/Architecture/`), and the CTest
  `StrataRuntime.NoTooling` (`StrataTests/Architecture/CheckNoTooling.cmake`).

## Further reading

- Godot Engine documentation, "Introduction to the buildsystem": how one source tree builds an editor and export
  templates without it; intermediate.
- Epic Games, "Unreal Engine Modules": how the engine and a game divide into modules, and which kinds a packaged game
  leaves behind; advanced.
- [Unity Manual, "Assembly definitions"](https://docs.unity3d.com/Manual/assembly-definition-files.html): how a Unity
  project's scripts compile into assemblies that the editor and the player load; intermediate.
- Jason Gregory, Game Engine Architecture, the chapters on the tools and the runtime layers: a survey of how engines
  divide their code; advanced.
