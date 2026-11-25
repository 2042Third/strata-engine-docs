---
id: start/coming-from
title: "Coming from Unity, Unreal or Godot"
description: "Find in Strata what you used in Unity, Unreal or Godot, and the page that teaches it: names, callbacks, prefab overrides, units and axes."
kind: how-to
size: M
tracks: [G, E]
needs: [start/what-an-engine-is]
time: 45
learn:
  - id: names
    text: name Strata's word for each idea of Unity, Unreal or Godot that the map lists
  - id: find
    text: find the player, a prefab override, a script's callback and the input actions in the Third-Person Adventure
  - id: units
    text: compute where a point lies in Strata's axes and units from its place in Unity or Unreal
  - id: callbacks
    text: compare the callbacks of a Strata script with those of your old engine
status: final
---

This page helps you find in Strata what you used in Unity, Unreal or Godot, and the page of this book that teaches it. You read a map of names, then open a finished game and find each idea in it. Before you start:

- You made something in Unity, Unreal or Godot: a scene, a script and a press of Play.
- You made [your first game](../start/first-game.md), so you know a copy of a sample, the **Inspector** and a script.
- You read [What an engine is](../start/what-an-engine-is.md).

The page is optional. If you have used no other engine, its map holds only new words, and you lose nothing by skipping it. Continue with [A tour of the editor](../make/editor-tour.md) if you make games, or with [How a computer runs a program](../basics/computer.md) if you build the engine. The steps of the last section need no other engine, if you want to explore a finished game first.

## The map of names

Every engine splits a game into the same few ideas, and each engine names them its own way. Strata keeps many of the common names, so several words already match. Four tables follow, one for each group of ideas. Most Strata cells link the page that teaches the idea, and the rows of callbacks share the link of their first row.

### Things in a scene and their parts

| Idea | Unity | Unreal | Godot | Strata |
| --- | --- | --- | --- | --- |
| A thing in the world | `GameObject` | `Actor` | `Node` | [Entity](../make/scenes-entities.md): a name and a list of components, with no class of its own |
| A part of a thing | Component | `ActorComponent` | A child node | [Component](../make/scenes-entities.md): data on the entity, such as **Transform** |
| One place of the game | Scene | Level | Scene | [Scene](../make/scenes-entities.md) |
| A group placed many times | Prefab | Blueprint class | `PackedScene` | [Prefab](../make/prefabs.md), with overrides for single properties |
| A label to search by | Tag | Actor tag | Group | The **Tag** component, one name for each entity |
| A body that physics moves | `Rigidbody` | A component that simulates physics | `RigidBody3D` | **Rigid Body** and its colliders ([Physics](../make/physics.md)) |
| A character that walks | `CharacterController` | Character movement | `CharacterBody3D` | **Character Controller** ([Physics](../make/physics.md)) |

### Game code and its functions

| Idea | Unity | Unreal | Godot | Strata |
| --- | --- | --- | --- | --- |
| The language | C# | Blueprints and C++ | GDScript | C++ script classes; no :term[visual scripting]{id=visual-scripting} ([Your first script](../make/first-script.md)) |
| Once, at the start | `Awake`, `Start` | `BeginPlay` | `_ready` | `OnCreate` ([The script loop](../make/script-loop.md)) |
| Every frame | `Update` | `Tick` | `_process` | `OnUpdate` |
| At the fixed step | `FixedUpdate` | `Tick`, with physics sub-steps | `_physics_process` | `OnFixedUpdate` |
| After the other updates | `LateUpdate` | A later tick group | A node's process priority | `OnLateUpdate` |
| At the end | `OnDestroy` | `EndPlay` | `_exit_tree` | `OnDestroy` |
| A contact | `OnCollisionEnter`, `OnTriggerEnter` | Hit and overlap events | The `body_entered` signal | `OnCollisionEnter`, `OnTriggerEnter`: Unity's names |

### Settings, assets and shipping

| Idea | Unity | Unreal | Godot | Strata |
| --- | --- | --- | --- | --- |
| Named controls | Input System | Enhanced Input | The input map | [Input and input actions](../make/input.md), in the project settings |
| The files of the game | The `Assets` folder | The `Content` folder | The project folder | The `Assets` folder; each file has a handle ([Assets](../make/assets.md)) |
| A game for players | Build | Package | Export | [Exporting and shipping](../make/export.md) |

### The editor's panels

| Idea | Unity | Unreal | Godot | Strata |
| --- | --- | --- | --- | --- |
| The tree of things | Hierarchy | `World Outliner` | Scene dock | **Hierarchy** ([A tour of the editor](../make/editor-tour.md)) |
| The values of one thing | Inspector | Details panel | Inspector | **Inspector** |
| The files | Project window | Content Browser | `FileSystem` dock | **Content Browser** |

### Three differences that matter more than names

First, an entity has no class: you never derive a new kind of entity, you give it components. Strata keeps behaviour in scripts and in engine systems, and a bigger world changes only how many entities exist; [What a game world is made of](../world/what-a-world-is.md) compares object models. Second, a prefab has overrides but no nested prefabs and no variants. Third, game code is a compiled module the engine loads, so setup goes in `OnCreate`, not in the constructor: the module builds one instance when it loads, only to read the fields' defaults.

### A prefab and its overrides

The Course holds twelve coins, and each one is an instance of the prefab `Coin`. The prefab has two entities: a root with a body, a collider, a script and a tag, and a child `Visual` that draws the mesh. Every coin stands in its own place and has its own name, and Strata never counts those two as overrides. Change the **Radius** of one coin and only that coin carries an override: the other eleven keep the prefab's value.

Unity would let you make a variant of the prefab, or nest one prefab inside another. Strata keeps one level. If you capture entities that are instances into a new prefab, the new prefab stores them without their links, as plain entities. The cost: a later change to `Coin` does not reach a bigger prefab built from coins. The gain is that a single rule tells you where any value comes from.

## What a callback looks like in C++

A **callback** is a function that you write and the engine calls for you at a set moment. In Unity you wrote `Update` inside a class; in Strata you write `OnUpdate` inside a class that derives from `Script`. In the sample below, two files hold it: a header declares the class, and a source file defines the functions.

:::question[I know C#, GDScript or Blueprints, not C++. Must I learn it now?]
No: you only read two small pieces below. [Programming from zero: values and variables](../basics/programming-1.md) teaches types and variables, [Programming from zero: classes and references](../basics/programming-3.md) classes and `::`, and [C++ classes in depth](../basics/cpp-classes.md) teaches `override`.
:::

The header lists the callbacks that the class replaces. Find the word `override`: it says that the function replaces the empty one of the base class `Script`.

```cpp src="Samples/ThirdPerson/Scripts/ThirdPersonPlayer.h#L41-L45"
glm::vec3 StartPosition = glm::vec3(0.0f); // Where it started (a field, so that a hot reload keeps it)

void OnCreate() override;
void OnReload() override;
void OnUpdate(float deltaTime) override;
```

The class declares three callbacks and no more, so the engine calls only those. The source file gives each function its body, and writes the class name and `::` before the function name, because the body stands outside the class.

```cpp src="Samples/ThirdPerson/Scripts/ThirdPersonPlayer.cpp#L54-L58"
void ThirdPersonPlayer::OnUpdate(float deltaTime)
{
	TransformComponent transform = GetTransform();
	CharacterController controller = GetEntity().GetCharacterController();
	const glm::vec3 position = transform.GetWorldPosition();
```

`deltaTime` is the length of the last frame in seconds, as in Unity's `Update`. The first line of the body reads the entity's Transform.

One order differs from Unity. Take a frame of 0.04 s, with the fixed step of 1/60 s that a scene has by default. Every script's `OnUpdate` runs first, once, with `deltaTime` at 0.04. The scene then runs two fixed steps, because 0.04 s holds two whole steps of 0.0167 s. Each `OnFixedUpdate` gets 0.0167.

The remaining 0.0067 s wait for the next frame. Last, every `OnLateUpdate` runs once, after the fixed steps. Unity runs `FixedUpdate` before `Update`; Strata runs its fixed steps after the updates.

When you rebuild the scripts while the game plays, Strata swaps the code and calls `OnReload` instead of `OnCreate`. [The script loop](../make/script-loop.md) teaches the whole order.

:::why[Why C++ scripts, and no visual scripting?]
Strata runs game code as a compiled module that the engine loads and reloads, so a crash inside a script stays inside it and a rebuild swaps the code while the game plays. A module needs a compiled language. The cost is real: a build step (**Ctrl+B**) before each test, and a language that is harder to learn than GDScript. Strata has no visual scripting. [Why game code lives outside the engine](../scripting/why-scripts.md) gives the whole argument.
:::

## Units and axes

Imported content breaks first at the axes and the units, because each engine chose its own. Strata is right-handed, with +Y up and -Z forward, in metres, with angles in degrees. Godot uses the same choices. Unity is left-handed with +Z forward. Unreal is left-handed, with +Z up and +X forward, in centimetres.

| | Strata | Godot | Unity | Unreal |
| --- | --- | --- | --- | --- |
| Handedness | Right | Right | Left | Left |
| Up | +Y | +Y | +Y | +Z |
| Forward | -Z | -Z | +Z | +X |
| Unit | 1 metre | 1 metre | 1 metre | 1 centimetre |

Take a crate 2 m in front of the camera, 1 m to its right and 0.5 m above it. In Strata the offset is (1, 0.5, -2): +X is right, +Y is up and forward is negative. Godot writes the same three numbers. Unity writes (1, 0.5, 2). Unreal writes X = 200 for forward, Y = 100 for right and Z = 50 for up.

The same rule fixes sizes. The player of the Third-Person Adventure stands 1.8 m tall: its **Height** reads 1.8 in Strata and would read 180 in Unreal. A model that arrives 100 times too large was made in centimetres, and the import's scale corrects it.

Two more habits matter. Models in the glTF format face +Z, while the forward of cameras, lights and scripts is -Z. A character that walks along the forward of its entity shows its back until the model turns 180 degrees around Y. And the Inspector and the commands take angles in degrees, while the script SDK's `SetEulerAngles` takes radians. [Positions, rotations and units](../make/transforms-units.md) teaches both in full.

:::elsewhere[The axes of the other engines]
The Unity manual's page on the Transform and the Godot documentation's introduction to 3D describe their axes and units; the Unreal Engine documentation's page on its coordinate system gives Unreal's. All three are in Further reading.
:::

## Find each idea in a finished game

You find each row of the map in a finished game: a character, a prefab, a script and the project's controls. Nothing here changes the sample for good.

:::::steps

1. Make your own copy of the Third-Person Adventure.

   ::::tabs{sync=how}
   :::tab[In the editor]
   In the launcher press **Open Sample...** and choose **Third-Person Adventure**. Keep the **Folder** name `ThirdPerson` and press **Copy and Open**.
   :::
   :::tab[With a command]

   ```json
   { "command": "project.openSample", "parameters": { "sample": "ThirdPerson", "directory": "<a new folder>/ThirdPerson" } }
   ```

   :::
   ::::

   **You should see:** the editor opens the copy with the scene of its main menu.

   **If you do not see it:** the dialog says that the folder exists. Type a new **Folder** name and press **Copy and Open** again.

2. Open the Course scene.

   ::::tabs{sync=how}
   :::tab[In the editor]
   In the **Content Browser**, open **Assets** and click **Scenes** in the folder tree. Double-click `Course`.
   :::
   :::tab[With a command]

   ```json
   { "command": "scene.open", "parameters": { "scene": "Scenes/Course.stscene" } }
   ```

   :::
   ::::

   **You should see:** the **Hierarchy** lists the entities of the course, among them `Camera` and `Player`.

   **If you do not see it:** the **Hierarchy** still lists the menu. You opened `MainMenu`: double-click `Course` instead.

3. Select `Player` and read its components.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Click `Player` in the **Hierarchy**.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.get", "parameters": { "entity": "AAE2EAF90F8A1799", "component": "CharacterController" } }
   ```

   `AAE2EAF90F8A1799` is the identifier (ID) of `Player`. The sample stores the ID in its scene, so every copy has the same one; `entity.find` with `{ "name": "Player" }` answers it as `{ "entities": ["AAE2EAF90F8A1799"] }`. `959D47C78B26E82F` in the next step is the ID of `Coin 1`, found in the same way.

   :::
   ::::

   **You should see:** the **Inspector** lists **Transform**, **Character Controller**, **Script** and **Tag**. The **Script** shows `ThirdPersonPlayer`, with fields such as `Camera` and `Robot` that name other entities.

   **If you do not see it:** the **Inspector** is empty or lists another entity. Click the name `Player` in the **Hierarchy** again.

   **Why:** the player is an entity, a name that holds components. The **Character Controller** gives it a walking body, as in Unity, and the **Script** gives it code. Nothing derives from a class of players.

4. Make an override on a placed coin, then undo it.

   ::::tabs{sync=how}
   :::tab[In the editor]
   In the **Content Browser**, open **Assets** and click **Prefabs**: `Coin` is the prefab. In the **Hierarchy**, expand `Coins` and click `Coin 1`. In the **Inspector**, set **Radius** of the **Sphere Collider** to `1.2`. Then right-click the label **Radius** and choose **Revert**.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "959D47C78B26E82F", "component": "SphereCollider", "values": { "Radius": 1.2 } } }
   ```

   Then undo the override:

   ```json
   { "command": "prefab.revert", "parameters": { "entity": "959D47C78B26E82F", "component": "SphereCollider", "property": "Radius" } }
   ```

   The bold label shows only in the window. Before the revert, `prefab.status` with the same `entity` lists the override under `overrides`, with `component` `SphereCollider` and `property` `Radius`; after it the list is empty, and `component.get` reads `Radius` 0.7.

   :::
   ::::

   **You should see:** after the edit, the label **Radius** turns bold, with a bar in the accent colour at the left of its row. After **Revert**, the value is 0.7 again and the label is plain.

   **If you do not see it:** the label stays plain after the edit. You selected the child `Visual`, not `Coin 1`: the **Sphere Collider** of the child does not exist.

   **Why:** a coin is an instance of the prefab, and a changed value is an override: this coin keeps it, whatever the prefab says later. The same right-click menu offers **Apply to Prefab**, which writes the value into the prefab so that every other coin follows. Do not choose it now; [Prefabs](../make/prefabs.md) teaches it.

5. Open `ThirdPersonPlayer.cpp` and find `OnUpdate`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   In the **Content Browser**, click **Scripts** in the folder tree and double-click `ThirdPersonPlayer.cpp`.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.open", "parameters": { "file": "Scripts/ThirdPersonPlayer.cpp", "line": 54 } }
   ```

   :::
   ::::

   **You should see:** the file in your code editor, and near line 54 the definition `ThirdPersonPlayer::OnUpdate` that you read above. The header `ThirdPersonPlayer.h` declares the class.

   **If you do not see it:** nothing opened. Set a code editor in **Scripts ▸ External Editor...**, as [your first game](../start/first-game.md) shows.

6. Open the project's input actions.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **File ▸ Project Settings...** and click **Input Actions** in the list of pages.
   :::
   :::tab[With a command]

   ```json
   { "command": "project.settings", "parameters": { "section": "Input.Actions" } }
   ```

   The answer is long: it describes the section first. Its `value` holds `Maps`, and the map whose `Name` is `Gameplay` lists `Actions`, each with its `Name`, `Kind` and `Bindings`, such as `Key/Space` for `Jump`.

   :::
   ::::

   **You should see:** a map named `Gameplay` with actions such as `Move`, `Look` and `Jump`, each with its keys and gamepad controls.

   **If you do not see it:** the window shows another page. Click **Input Actions** under Input in the left list.

   **Why:** a script asks for a control by name, as in `Input::IsActionPressed("Gameplay/Jump")`, so a player can choose other keys without a change in the code. This is Unity's Input System and Unreal's Enhanced Input; [Input and input actions](../make/input.md) teaches it.

:::::

## Result

You have a map of names of your own: for each idea of your old engine, you know Strata's word, the panel where it lives and the page that teaches it. You also hold the three differences. An entity has no class, a prefab has overrides but no variants, and a script is a compiled module that does its setup in `OnCreate`. Your copy of the sample stays on disk, and you can open it again from the launcher or play it.

## Variations

### You know a code-first engine

If your engine keeps entities and components in code, and its editor looks like Unity's, you can skip the first table. Entities and components work in Strata as you expect. What differs is the editor: every change of a scene goes through a command, so an agent can make the same change. [Scenes, entities and components](../make/scenes-entities.md) teaches that side.

### What Strata does not have

Several things you may search for have no Strata form. Each is listed on [What Strata does not do, and how engines do it](../appendix/not-in-strata.md), with what to do instead:

- Nested prefabs and prefab variants.
- Visual scripting: Blueprints, visual scripts and node graphs of logic.
- Mobile and web targets: Strata builds for Windows, Linux and macOS.
- A particle system.
- A terrain tool.

## Summary

- Strata names the entity, component, scene, prefab, script, input action and export, and the map links the page for each.
- The Third-Person Adventure shows the player as an entity, a coin's override in bold, a script's callbacks and the project's input actions.
- Strata is right-handed, with +Y up and -Z forward, in metres; Unity is left-handed, and Unreal counts centimetres with +Z up.
- `OnCreate`, `OnUpdate`, `OnFixedUpdate`, `OnLateUpdate` and `OnDestroy` replace the functions of your old engine, and setup goes in `OnCreate`.

## Check yourself

1. In Unity you put a crate at (0, 0, 5), 5 m in front of the camera. Where does Strata put it, if the camera is at the origin and faces forward?

   :::answer{tests="units"}
   At (0, 0, -5). Strata's forward is -Z, and Unity's is +Z, so the sign of z flips. The x and y values stay the same, because both engines use +X right, +Y up and metres.
   :::

2. A glTF character walks backwards when your script moves it along the forward of its entity. Why, and what fixes it?

   :::answer{tests="units"}
   The model faces +Z and the forward is -Z, so the model shows its back. Turn the model 180 degrees around Y, for example on a child entity that holds it.
   :::

3. Which Strata function do you write for Unity's `Start`, and why not the constructor?

   :::answer{tests="callbacks"}
   `OnCreate`. The module builds one instance of each class when it loads, only to read the fields' defaults, so game setup in the constructor would run at the wrong moment.
   :::

4. You change **Radius** on one coin. What shows it, and what do the other coins do?

   :::answer{tests="find"}
   The label turns bold with a bar in the accent colour. The other coins keep the value of the prefab, because only this coin has an override.
   :::

5. Give Strata's word for a `GameObject`, a Blueprint class and Enhanced Input.

   :::answer{tests="names"}
   An entity, a prefab and input actions. A prefab is the nearest Strata form of the Blueprint class that you place many times.
   :::

## Exercises

1. **Basic.** Find the camera that follows the player in the Course scene. Name its components in Strata's words, say what your old engine uses for each, and find the callback that moves it.

   :::answer[Worked solution]{tests="find,callbacks,names" solution="tutorials/start/coming-from/exercise-1.tutorial.json"}
   The entity `Camera` has a **Camera** component with **Primary** on, an **Audio Listener** and a **Script** with `FollowCamera`, whose **Target** field names `Player`. Unity would use a Camera, an Audio Listener and a script on one object; Unreal a camera component, often on a spring arm; Godot a `Camera3D` node with a script. In `FollowCamera.cpp` the function is `OnLateUpdate`. It runs every frame after the fixed updates, as Unity's `LateUpdate` runs after `Update`, so the camera sees the player after the player has moved.
   :::

2. **Medium.** An Unreal level puts a ramp at X = 1200, Y = -400, Z = 250, in centimetres, with +X forward and +Y to the right. Where does the ramp go in Strata?

   :::answer{tests="units"}
   Convert to metres: 12, -4 and 2.5. Forward is -Z in Strata, so Unreal's X gives z = -12. Unreal's Y is right, so y = -400 means 4 m to the left, which is x = -4. Up is Y: y = 2.5. The Translation is (-4, 2.5, -12).
   :::

## Where it lives in Strata

- `StrataScriptCore/Include/StrataScript/Script.h`: the base class `Script`, its callbacks and their order.
- `Strata/src/Strata/Scene/PrefabOverrides.h`: what an override is, and why the root's place and name are never one.
- `Strata/src/Strata/Scene/PrefabInstances.h`: the links of an instance, and the prefab that keeps none.
- `Strata/src/Strata/Math/Math.h`: the engine's conventions of axes.
- `Samples/ThirdPerson/`: the project that the steps open.

## Further reading

- [Unity Manual, "Transform"](https://docs.unity3d.com/Manual/class-Transform.html): positions, rotations and the units of Unity (beginner).
- [Unity Manual, "Order of execution for event functions"](https://docs.unity3d.com/Manual/ExecutionOrder.html): when `Awake`, `Update` and `LateUpdate` run (intermediate).
- [Godot documentation, "Introduction to 3D"](https://docs.godotengine.org/en/stable/tutorials/3d/introduction_to_3d.html): the axes and units of Godot (beginner).
- [Godot documentation, "Idle and Physics Processing"](https://docs.godotengine.org/en/stable/tutorials/scripting/idle_and_physics_processing.html): `_process` and `_physics_process` (beginner).
- Epic Games, Unreal Engine documentation, "Coordinate System and Spaces": the axes and units of Unreal (intermediate).
