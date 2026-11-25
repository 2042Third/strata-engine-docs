---
id: scripting/why-scripts
title: "Why game code lives outside the engine"
description: "Why an engine loads game code as a separate module, how other engines script, and what Strata's native choice costs."
kind: concept
size: M
tracks: [E]
needs: [world/ecs]
time: 45
learn:
  - id: why-modules
    text: explain why an engine loads game code as a module instead of compiling it into the engine
  - id: compare-approaches
    text: compare five ways of scripting a game by speed, time to see a change, safety and tools
  - id: name-costs
    text: name the three costs of native scripts and the page of this part that answers each
since: 0.3.0
status: final
---

In [Your first game](../start/first-game.md) you opened the `Spinner` script, changed one number and pressed **Ctrl+B**. A few seconds later the cube turned at a new speed. The editor never closed, and nobody rebuilt the engine.

That small success hides a design decision. Your change touched one short file. Something made it possible to replace that file while everything else kept running. This page explains what that something is, why engines need it, which other ways exist and what Strata pays for its choice.

## Game code changes by the hour, the engine does not

An engine is large and general. It draws triangles, plays sound, simulates physics and loads files, for every game made with it. Its code changes when its authors find a better method or a bug.

Game code is the opposite: small, specific and unstable. A designer decides that a jump should be a little higher, that a coin should be worth five points, that an enemy should wait one second before it turns. Each decision changes one line, and a designer makes dozens in a day. Making a game means trying a change, looking at the result and trying another.

The speed of that loop decides how good the game gets. A person who sees a result in five seconds tries a hundred ideas in an afternoon. A person who waits ten minutes tries a dozen.

A second pressure comes from mistakes. Game code is written fast, by many people, and it is the part most likely to contain an empty pointer, a loop that never ends or a division by zero. If that code runs inside the engine's own process, one mistake closes the editor, and the work you have not saved goes with it.

## The naive answer: compile game code into the engine

The simplest design puts game code beside the engine's code. You write the `Spinner` class in a file of the engine's project, build the whole program and run it. Many small games and early engines work this way: one language, one build, nothing new to learn.

The design breaks in two places. The first is the loop. Every change, even a number, goes through the build of the whole program, and then the program restarts, which throws away the level you were standing in.

Suppose the build and restart take four minutes, a plausible figure for a large C++ program. A designer who makes thirty tweaks in a day waits 30 × 4 = 120 minutes. If a build of only the game code took fifteen seconds, the same thirty tweaks would cost 30 × 0.25 = 7.5 minutes. The numbers are assumed; what matters is that the gap repeats with every tweak, because building and linking a whole engine takes far longer than building a small library.

The second break is about knowledge. If game code lives in the engine's project, it can reach every internal detail: the :term[renderer's]{id=renderer} private lists, the scene's caches, the memory of the physics world. Game authors will use them, because nothing stops them. The engine's authors then cannot change a detail without breaking someone's game, and the engine stops improving. A wall between engine and game protects both sides.

## The idea: the engine loads the game as a separate piece

The remedy is to build game code apart from the engine, as a :term[shared library]{id=shared-library} the engine loads while it runs. The engine offers game code a small, stable set of services. The game offers the engine a small, stable set of entry points. Everything else stays private on both sides.

In Strata that library is a **script module**: a file of :term[machine code]{id=machine-code} made from your C++ classes. The classes inside are called scripts, although nothing is read line by line. The word means "game code the engine loads". The engine opens the file, asks which classes it holds and makes an instance for each entry of each Script component in the scene that plays. When you press **Ctrl+B**, only the module is built, and the engine swaps the old file for the new one.

The page [Shared libraries and binary interfaces](../scripting/shared-libraries.md) explains how a library loads. Here only the picture matters: a stack of layers with one line through it.

```mermaid caption="Game code sits above a line that only plain C data crosses. Below the line the engine has four parts, and the table of host functions leads on to the scene and the engine's services." alt="A stack of boxes. At the top are game code and the software kit, then the module's entry points. A thick line marks the boundary of the C interface. Below it are the module loader, the script engine, the script system and the host table, which reaches the scene and engine services and calls back into the entry points."
flowchart TB
    G["Game code: your Script classes"] --> S["SDK: header-only C++ helpers"]
    S --> E["Module entry points"]
    E ==>|"C ABI line"| M["ScriptModule: loads the library, guards every call"]
    M --> N["ScriptEngine: the loaded module, reloads, faults"]
    N --> Y["ScriptSystem: instances of one playing scene"]
    Y --> H["ScriptHostAPI: table of engine services"]
    H --> V["Scene services and engine services"]
    H -.->|"calls back into"| E
```

Read the diagram from the top. Your classes derive from `Script`, a type of the software development kit (SDK): :term[header files]{id=header-file} you include. The SDK turns your classes into a few plain functions, the module's entry points, and those are all the engine ever calls.

The thick line is an application binary interface (ABI). It is a list of functions and data layouts that both sides agree on, and nothing else. Below it, `ScriptModule` loads the file and guards every call into it. `ScriptEngine` holds the loaded module and replaces it when you rebuild. `ScriptSystem` owns the instances of the playing scene and calls their functions each frame.

`ScriptHostAPI` is the host application programming interface (API): a table of functions the engine hands to the module. With it a script can read input, move an entity or play a sound. It needs no engine header for any of that.

The pages of this part open these boxes in turn: [the ABI and the SDK](../scripting/abi-sdk.md), [loading a module](../scripting/loading.md), [the script system](../scripting/script-system.md) and [the host API](../scripting/host-api.md). Hold the picture, because every cost on this page is a property of that line.

## How engines script their games

Engines solved this problem in at least five ways, and each answers a flaw of the one before. The statements about other products come from their public documentation, listed in the further reading.

### An embedded interpreted language

The first fix replaces C++ with a small language that the engine reads while it runs. `Lua` is the classic example: it is tiny, made to be embedded, and a script is a text file. To change a rule you save the file and the engine reads it again, with no compile step.

The price is speed and tools. An interpreter does extra work for each operation, so scripts run slower than compiled code, and heavy loops must move back into the engine. The editor support is usually thin, and a script that names something wrongly fails only when that line runs.

### A managed runtime

The second fix keeps the idea but uses a stronger language. Unity runs game code written in C#, and Godot also supports C#. The code is compiled to an intermediate form and run by a :term[runtime]{id=runtime} that manages memory and catches many errors.

A managed runtime gives better tools, real types and good speed, though a little less than native code. The price moves to the engine: it must carry a whole runtime. Memory that the runtime collects on its own schedule can cause pauses, and every call between C++ and managed code crosses a boundary with a cost. Changing code still takes a compile.

### A language of the engine's own

The third fix says that if no existing language fits, make one that does. GDScript in Godot has a form close to Python and knows the engine's objects. `UnrealScript` served the same purpose in older versions of Unreal Engine.

A tailored language can be pleasant, and its tools can match the engine exactly. The flaw is that the engine's authors must now build a language: its :term[compiler]{id=compiler} or interpreter, its editor support, its debugger and its documentation. Nobody learns it anywhere else, and it is usually slower than the compiled choices.

### Visual scripting

The fourth fix removes text. Unreal's Blueprints let you place nodes on a canvas and draw wires between them. A person who has never programmed can make a door open when the player comes near.

Graphs suit small behavior owned by designers, and they grow hard to keep. They are hard to compare in :term[version control]{id=version-control} and hard to search, and a large graph reads worse than the same logic as text. They run on a virtual machine, so they are slower than native code.

### Native code in plug-in libraries

The fifth fix returns to the engine's own language. Game code is built as a library, loaded while the engine runs, and replaced when it changes. Unreal Engine's C++ game modules work this way, and its Live Coding feature rebuilds changed code and patches the running editor. Many in-house engines of game studios do the same with the plain mechanism of loading and unloading a shared library.

The gain is full speed, one language for engine and game, and the debuggers and editors that C++ programmers already use. The costs are the ones this page keeps returning to. Native code can crash the process, a binary boundary needs careful rules, and compiling C++ takes longer than reading a script.

| Approach | Speed | Time to see a change | Safety | Tools | Used by |
| --- | --- | --- | --- | --- | --- |
| Interpreted (`Lua`) | Slow to medium | Seconds: save and reload | A mistake fails that script | Few, varies by host | Many engines that embed `Lua` |
| Managed (C#) | Fast, with pauses | Seconds to a minute: compile and reload | The runtime catches most errors | Very good | Unity, Godot's C# |
| Own language (GDScript) | Slow to medium | Seconds | A mistake fails that script | Made by the engine's authors | Godot; `UnrealScript` in older Unreal |
| Visual (Blueprints) | Slow, except nodes that call native code | Seconds | A graph cannot write through a bad pointer | Graph editor, weak for comparing | Unreal |
| Native in libraries | Full speed | Seconds to a minute: compile C++ | A crash can take the process down | The best: every C++ tool | Unreal's C++ modules, in-house engines, Strata |

Read down the table and a pattern appears. Moving up trades speed and control for safety and gentleness, and the last row is the only one with no second language to learn or maintain.

## Where game code attaches to the world

Choosing how to write code leaves a second question: what does a piece of game code belong to? The answer shapes what a script can do. The page on [entities and components](../world/ecs.md) described the pieces; engines use three main models for game code.

A script component attaches a class to an entity, and the engine calls the class's functions each frame. Unity's `MonoBehaviour` is the best known: an entity holds several, each with its own data. It is simple to grasp and suits designers, but many small objects update in an order nobody wrote down.

In a pure entity-component-system, game code has no objects at all. You write systems: functions that visit every entity holding certain components. This is fast and orderly, but it asks the author to think in tables rather than in "this enemy does this".

Unreal uses actor :term[subclasses]{id=derived-class}. The game derives a class from the engine's `Actor` and overrides its functions, so the script and the object are one thing. Inheritance gives a lot for free and ties game code tightly to the engine's class tree.

Strata takes the first model with one plain rule. An entity holds one Script component, and that component holds an ordered list of entries. Each entry names a class and may override its field values.

:::question
New to C++? Structs and `std::vector` are taught in [Programming 2](../basics/programming-2.md), classes and member functions in [Programming 3](../basics/programming-3.md).
:::

The two structs below are the whole component. Search for what they store: names and values, no code and no pointer to an instance.

```cpp src="Strata/src/Strata/Scripting/ScriptingComponents.h#L21-L37"
struct ScriptEntry
{
	std::string ClassName;
	std::vector<ScriptFieldValue> Fields; // Overrides of the script's default field values

	ScriptFieldValue* FindField(std::string_view name);
	const ScriptFieldValue* FindField(std::string_view name) const;
};

// Native C++ behaviours from the project's script module attached to this entity.
struct ScriptComponent
{
	std::vector<ScriptEntry> Scripts;

	ScriptEntry* FindScript(std::string_view className);
	const ScriptEntry* FindScript(std::string_view className) const;
};
```

1. **Line 23:** the class's name is a string, not a pointer to code.
2. **Line 24:** the overrides are names with values, so a scene file can hold them.
3. **Lines 31–33:** the component is only a list of entries, in the order the scripts run.

The list order is the order in which the entity's scripts run. When the scene starts to play, the script system makes one instance for every entry, and those instances live in the system, outside the registry of components. A scene can therefore be saved, copied and edited without touching script memory: it holds names, and the system holds objects.

## Strata's choice: native C++20 behind a C interface

Strata uses the fifth approach. Game code is C++20, built into a shared library, loaded by the engine and talking to it across a C interface.

:::why[Why not a second language?]
One language means a game author learns one thing, and the engine's authors write no compiler, no virtual machine and no binding layer for another. Scripts run at the speed of the engine's own code, which matters when a game updates thousands of entities each frame. The debugger, the profiler and the editor that a C++ programmer already uses work on game code without change. The price is three costs, and the rest of this part pays them one by one.
:::

Each cost has its own page. First, a crash in native code is a crash of the process. A script that writes through an empty pointer would close the editor, the very problem that opened this page. Strata therefore runs every call into the module under a guard that catches the fault, records it and keeps the editor alive. [Crash containment](../scripting/crash-containment.md) explains how.

The binary boundary is the second cost. Engine and module are compiled separately, perhaps by different compiler versions, so they cannot share C++ types, strings or exceptions. Only plain data of the C language crosses the line, and the header-only SDK hides that from you. [The ABI and the SDK](../scripting/abi-sdk.md) shows the rules, and [Shared libraries](../scripting/shared-libraries.md) shows why they exist.

:term[Compile time]{id=compile-time} is the third. Strata makes the compile small, one module of your files, and makes the swap invisible. [Hot reload](../scripting/hot-reload.md) describes how the engine replaces a module while the game plays and keeps your field values.

One rule of the engine's layers follows from this choice. The Scripting layer may include only Core, Input, Asset, Reflection and Scene. It cannot include physics, audio or animation, so the host API reaches them through interfaces the scene declares, called scene services. For a script, the host API is the only door. [The host API](../scripting/host-api.md) and [Layers and registries](../core/layers-registries.md) explain the rule.

:::example[Counting the cost of one tweak]
You decide the `Spinner` should turn at 180 degrees a second instead of 90. In a design that compiles game code into the engine, you edit the file, build the whole program, restart, load the level and walk to the cube. With the numbers assumed earlier, that is four minutes of build before you even start walking.

In Strata you edit the file, press **Ctrl+B** and watch. The editor builds the module alone and writes it into the project's `.strata/Scripts/Bin` folder, and the engine loads the new file. No engine file rebuilds, and a playing game keeps its scene. At fifteen seconds for the build, thirty tweaks cost 7.5 minutes of waiting against 120 minutes in the first design.

A change to the engine, like the one in [Your first engine change](../core/first-change.md), is different in kind: it rebuilds engine libraries and restarts the editor.
:::

## What Strata's choice cannot do

Native scripts are not the right tool for everyone. A designer who cannot program cannot write a script. :term[Visual scripting]{id=visual-scripting} exists for that person, and Strata has none: :term[game logic]{id=game-logic} is C++ script classes. The editor's components cover movement, physics, sound and animation, but behavior beyond them needs code.

Strata supports no other script language. It embeds no `Lua`, no C# runtime and no Python for game code. Every extra language would need its own binding of the host API, its own crash handling and its own tools.

The shared library also limits where games can run. A platform that forbids loading code at run time, such as a console that requires all code to be linked before shipping, cannot load a module. The engine's plan for a console port names static linking of modules as work to do, and Strata has no such path.

The index of what the engine lacks is in [Not in Strata](../appendix/not-in-strata.md).

## Common mistakes

**Reading "script" as "interpreted".** The symptom is a belief that Strata scripts are slow, run from a text file or change without a build. A Strata script is compiled machine code. The fix: say "game code in a module", and remember that the build exists and the swap is fast.

**Underestimating what a native choice costs.** The symptom is surprise at the first crash, the first compiler difference or the first slow build. Plan for the three costs: a script can crash, only plain C data crosses the line, and the module must be compiled.

**Reaching into the engine from a script.** The symptom is a script that wants a physics or renderer type. The fix: ask the host API for the service, and if it lacks one, the engine needs a new host function, not a shortcut.

## Summary

- Game rules change far faster than an engine does, and a mistake in game code must not close the editor. The engine therefore loads game code as a module that is built and swapped alone.
- Engines script with an embedded interpreter, a managed runtime, a language of their own, visual graphs or native libraries; the choice trades speed, time to see a change, safety and tools.
- Strata's native choice costs crashes, the binary boundary and compile time, and the pages on crash containment, the ABI and SDK, and hot reload answer them in turn.

## Check yourself

1. Game code is compiled into the engine, and a build with a restart takes four minutes. A designer changes one number. Which description is right?

   - A. The change is free, because a number is not code.
   - B. The whole program is built and restarted, so the loop of tries gets slow.
   - C. Only the changed line is compiled, so the cost is small.
   - D. The engine must be rewritten.

   :::answer{tests="why-modules"}
   B. Game code inside the engine's project is part of its build and its process. A is wrong because a number in code is still compiled. C is wrong: the whole program links again, and the restart loses the level's state. D is wrong: no rewrite is needed, only a long wait.
   :::

2. Which approach of the table suits a designer who cannot program and wants a door to open, and which suits a game that updates ten thousand entities each frame?

   :::answer{tests="compare-approaches"}
   The designer suits visual scripting, where nodes replace text. The ten thousand entities suit native code in a library, because it runs at full speed with no interpreter between the logic and the processor. An interpreted language would slow the second case, and native C++ would shut out the first person.
   :::

3. Someone says: "Strata scripts are interpreted, so they are slow." What is wrong with that?

   :::answer{tests="why-modules, compare-approaches"}
   Strata scripts are C++ classes compiled into a shared library, so they run as machine code at the speed of the engine. The word "script" means game code that the engine loads, not text it reads. The change loop is fast because only the module is built, not because anything is interpreted.
   :::

4. Which page of this part answers each cost: a script writes through an empty pointer; the engine and the module use different compilers; a build of the module takes too long to wait for?

   :::answer{tests="name-costs"}
   The crash goes to [Crash containment](../scripting/crash-containment.md). The compiler difference goes to [the ABI and the SDK](../scripting/abi-sdk.md), with background in [Shared libraries](../scripting/shared-libraries.md). The wait goes to [Hot reload](../scripting/hot-reload.md), because the engine swaps the module while the game plays.
   :::

5. A scene file holds a Script component with the entries `Spinner` and `Logger`. Does the file contain the instances?

   :::answer{tests="why-modules"}
   No. It holds the class names and the field overrides, as the component's struct shows. The instances live in the script system and exist only while the scene plays, so saving and copying a scene never touches script memory.
   :::

## Exercises

1. **Basic.** Open the project of [Your first game](../start/first-game.md), change `DegreesPerSecond` in `Scripts/Spinner.cpp` to `180.0f` and press **Ctrl+B**. Find the file the build wrote, and time how long the change takes to show. Compare it with a build of the engine from [Your first engine change](../core/first-change.md).

   :::answer[Worked solution]{tests="why-modules, compare-approaches"}
   After the build, the module file appears in the project's `.strata/Scripts/Bin` folder, the output folder that the project's build file names. Time the steps from your edit to the moment the cube turns faster: for a small script this takes seconds, and no engine file changes. A build of the engine compiles many files and ends in a restart. Write both numbers down, because the gap is what the module design buys. The figures depend on your machine, so none is given here.
   :::

2. **Medium.** Read the sketch in the answer, predict its output, then run it. It models how the script system treats the entries of a component.

   :::answer[Worked solution]{tests="why-modules" solution="sketches/scripting-why-scripts-entries.cpp"}
   The sketch is below, with its output.

   ```cpp sketch="scripting-why-scripts-entries.cpp"
   #include <cstdio>
   #include <memory>
   #include <string>
   #include <utility>
   #include <vector>

   struct Script
   {
   	virtual ~Script() = default;
   	virtual void OnUpdate(float deltaTime) = 0;
   };

   struct Spinner : Script
   {
   	float Angle = 0.0f;
   	void OnUpdate(float deltaTime) override
   	{
   		Angle += 90.0f * deltaTime;
   		std::printf("Spinner at %.1f degrees\n", Angle);
   	}
   };

   struct Logger : Script
   {
   	void OnUpdate(float) override { std::printf("Logger ran\n"); }
   };

   std::unique_ptr<Script> Create(const std::string& className)
   {
   	if (className == "Spinner")
   		return std::make_unique<Spinner>();
   	if (className == "Logger")
   		return std::make_unique<Logger>();
   	return nullptr;
   }

   int main()
   {
   	const std::vector<std::string> entries = { "Spinner", "Logger", "Missing" };
   	std::vector<std::unique_ptr<Script>> instances;
   	for (const std::string& className : entries)
   	{
   		std::unique_ptr<Script> instance = Create(className);
   		if (instance)
   			instances.push_back(std::move(instance));
   		else
   			std::printf("No class named %s\n", className.c_str());
   	}
   	for (int step = 0; step < 2; ++step)
   		for (const std::unique_ptr<Script>& instance : instances)
   			instance->OnUpdate(0.5f);
   }
   ```

   ```text output-of="scripting-why-scripts-entries.cpp"
   No class named Missing
   Spinner at 45.0 degrees
   Logger ran
   Spinner at 90.0 degrees
   Logger ran
   ```

   1. **Line 28:** a factory that turns a class name into an instance, as the engine turns an entry's name into an object of the module.
   2. **Lines 44–47:** a name with no class is reported, and the other entries continue.
   3. **Lines 49–51:** instances update in the order of the list, so the output alternates between the two.

   The `Spinner` angle rises by 45 degrees per update, since 90 degrees a second times 0.5 seconds is 45.
   :::

3. **Hard.** Pick an approach from the table for each game and name the cost that decides it. (a) A puzzle game whose rules a designer changes every day. (b) A game in which players write and share their own extensions. (c) A console game on a platform that allows no loading of code at run time.

   :::answer[Worked solution]{tests="compare-approaches, name-costs"}
   (a) Time to see a change decides it. An interpreted language or visual graphs show a change within seconds, and Strata's hot reload narrows the gap for native code.

   (b) Safety decides it: code from strangers must not crash or harm the game, so an interpreted language in a restricted area fits best. Native code in a shared library would run strangers' machine code with full rights, and Strata has no such restriction.

   (c) The binary boundary decides it: a library cannot be loaded, so game code must be linked into the program. The engine's plan names static linking of modules for this case, and Strata has no such path.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Scripting/ScriptingComponents.h`: the `ScriptComponent` and its `ScriptEntry` list.
- `StrataScriptCore/Include/StrataScript/ScriptABI.h`: the C interface; `StrataScriptCore/Source/ScriptModuleEntry.cpp`: the module's entry points.
- `Strata/src/Strata/Scripting/ScriptModule.h`, `Strata/src/Strata/Scripting/ScriptEngine.h`, `Strata/src/Strata/Scripting/ScriptSystem.h` and `Strata/src/Strata/Scripting/ScriptHostAPI.cpp`: the four engine-side boxes of the diagram.
- `Strata/src/Strata/Scripting/ScriptingRegistration.cpp`: registers the component and the "Scripting" scene system.
- The menu **Scripts ▸ Build Scripts** (**Ctrl+B**) and the command `script.build` build the module into `.strata/Scripts/Bin`; `script.add` attaches a class to an entity.
- `StrataTests/Architecture/Layers.json`: the layer table that limits the Scripting layer.

## Further reading

- Lua reference manual, by the Lua authors: how a small language is embedded in a host program (intermediate).
- Unity Manual, scripting and `MonoBehaviour`: the script component model and managed code (beginner).
- Godot documentation, GDScript and C#: a custom language beside a managed one (beginner).
- Unreal Engine documentation, Blueprints, C++ gameplay classes and Live Coding: visual, actor-based and native scripting in one engine (intermediate).
- Robert Nystrom, "Game Programming Patterns", the chapters "Bytecode" and "Component": why games use scripts and components (beginner).
