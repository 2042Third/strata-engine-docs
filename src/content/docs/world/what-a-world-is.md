---
id: world/what-a-world-is
title: "What a game world is made of"
description: "Why an engine stores a game world as entities, components and systems instead of one class per kind of thing, and what Strata chose."
kind: concept
size: M
tracks: [E]
needs: [basics/computer, basics/cpp-classes, basics/data-structures, core/frame-loop]
time: 45
learn:
  - id: ecs-parts
    text: explain what an entity, a component, a system and a scene are
  - id: hierarchy-limits
    text: name the places where a class for each kind of thing breaks
  - id: storage-models
    text: compare object hierarchies, objects that own components, sparse sets and archetypes by cost, cache use and flexibility
  - id: strata-choice
    text: explain why Strata keeps plain-data components in one registry and its behaviour in scene systems
  - id: door
    text: write one door three times, in a class hierarchy, with a game object and with a component and a system
since: 0.3.0
status: final
---

When you opened your [first game](../start/first-game.md), two panels held everything you did to the scene. The **Hierarchy** listed the things in it, and the **Inspector** showed the parts of the one you selected. The figure shows the same two panels for a larger scene, the Course scene of the `Samples/ThirdPerson` project. It holds 288 things: a camera, a sun, a sky and islands built of blocks.

::figure{id=hierarchy-inspector}

That list is the problem of this page. A game world holds a player, a crate, a light and a camera, and a larger game holds thousands more. The engine must store all of them, find any one by name, update each one every frame and draw it. It must also save them to a file, load them again, and show each one in the editor so that you can change it and undo the change. The question is which shape the stored data takes, so that all of these jobs stay possible with 288 things or with a million.

This page needs no project and no download. Its one exercise is a program for the compiler of [How a C++ program is built](../basics/build.md#open-a-terminal-that-finds-a-compiler). The figure's scene opens as a copy from the launcher: press **Open Sample...** and choose **Third-Person Adventure**. The next pages of this part use two programs you already have: the installed Strata sends commands, and the source build of [your first engine change](../core/first-change.md) runs the exercises that trace or test the engine.

## The first answer: one class for each kind of thing

The answer most programmers try first uses what [C++ classes](../basics/cpp-classes.md) give. Each kind of thing becomes a class. A :term[base class]{id=base-class} has a virtual `Update`, and every kind derives from it and writes its own version. The engine keeps a list of pointers to the base class and calls `Update` on each one every frame.

The :term[pseudocode]{id=pseudocode} below shows a small family. Look at where `Mimic`, a chest that attacks, has to go.

```cpp pseudocode
class Thing { virtual void Update(float deltaTime); };
class Creature : public Thing { Health, Move() };
class Enemy : public Creature { Attack() };
class FlyingEnemy : public Enemy { Fly() };
class Chest : public Thing { Open() };
class Mimic : public ???   // a chest that attacks
```

The `Mimic` is a chest and an enemy, and the two sit on different branches of the tree. The design breaks in five places.

1. **A thing needs two branches.** C++ allows two base classes, but then every mix of kinds needs a class of its own. The number of classes grows with the number of combinations.
2. **The base class grows.** Everything needs a position, so `Thing` gets one. Then a name, a mesh, a body for physics and a sound. Soon each light and each invisible marker carries fields that only a few kinds use, and the base class knows the :term[renderer]{id=renderer}, the physics and the audio.
3. **Behaviour cuts across the classes.** "Can burn" applies to crates, enemies and trees, which share no base class. You either copy the code into each class or move it up into `Thing`, which is the second break again.
4. **The objects lie scattered in memory.** Each `new` puts an object wherever memory is free, so a loop over the list jumps around memory, and the processor loads a new :term[cache line]{id=cache-line} for almost every object. Every `Update` is also a virtual call whose target changes from one object to the next.
5. **Saving and showing need code for each class.** Every class has its own fields, so each one needs its own code to write a file, read it back and draw an Inspector.

## The idea: an identity, plain data and behaviour that visits the data

The fix splits a thing into three parts. An entity is only an identity: a number that names one thing of the scene and holds nothing else. A component is a plain piece of data attached to an entity, such as a position or a mesh, and an entity holds at most one component of each type. A system is code that runs every frame over each entity that has the components it needs. A scene is the world that holds the entities with their components and, while the game plays, the systems.

The whole design is an **entity-component system (ECS)**. The Course scene shows what it looks like. The table lists three of its entities and their components, named as the scene stores them.

| Entity | Components |
| --- | --- |
| `Camera` | `AudioListener`, `Camera`, `Name`, `Script`, `Transform` |
| `Sun` | `DirectionalLight`, `Name`, `Transform` |
| `BlockTall (1)` | `MeshCollider`, `MeshRenderer`, `Name`, `PrefabInstance`, `RigidBody`, `Transform` |

No class `Camera` or `Block` exists in this picture. All three entities hold `Name` and `Transform`, so one piece of data and one piece of code serve them all. The camera is also a listener and the home of a script only because it holds two more components. A block is drawn and moves under physics because it holds the parts those jobs need, and the class of a thing never enters.

```mermaid caption="Entities hold data only. Each system reads the kinds of data it needs, from every entity that has them." alt="Two entities on the left, a block and a sun. The block is joined to its position, mesh and body. The sun is joined to its position and light. On the right a draw system reads position, mesh and light, and a physics system reads position and body."
flowchart LR
    B["Block"] --> P1["position"]
    B --> M["mesh"]
    B --> R["body"]
    S["Sun"] --> P2["position"]
    S --> L["light"]
    D["draw system"] -.reads.-> P1
    D -.reads.-> M
    D -.reads.-> L
    Y["physics system"] -.reads.-> P1
    Y -.reads.-> R
```

The diagram shows the three roles. The boxes in the middle are the data, and the entities on the left only name which data belongs together. A system on the right never asks what kind of thing an entity is, only which components it has. Adding a mimic then costs nothing new: an entity with the chest's component and the enemy's component.

:::example[Reading 10,000 positions]
A system moves 10,000 things and so reads the position of each. A position is three floats, 12 :term[bytes]{id=byte}. A cache line is 64 bytes, as in [How a computer runs a program](../basics/computer.md).

In the object design each thing is an object of about 200 bytes, allocated on its own. Each position lies in a different cache line, so the loop loads 10,000 lines of 64 bytes, which is 640,000 bytes. It uses 120,000 of them, 19 %.

With the positions in one array, the loop reads 10,000 × 12 = 120,000 bytes in a row. That is 120,000 / 64 = 1,875 lines, 5.3 times fewer, and every loaded byte is used. Strata's `Transform` also holds a rotation and a scale, so it is 12 + 16 + 12 = 40 bytes. Then 10,000 of them fill 400,000 bytes, 6,250 lines, still 1.6 times fewer than the objects.

The count assumes that no two objects share a line and ignores that the processor guesses a sequential read and loads ahead, which favours the array again.
:::

## Four ways engines store a world

Engines have answered the problem in four ways, and each way answers a flaw of the one before.

### Object hierarchies

The oldest way is the tree of classes above. Unreal's `AActor` is the base of such a tree: a `Character` derives from a `Pawn`, which derives from an `AActor`. Unreal also lets an actor hold components, which softens the five breaks. Where the tree decides the type of a thing, every break returns.

### Objects that own components

The second way keeps one object for each thing and hangs behaviour on it as separate parts. Unity's `GameObject` holds a list of components, and your own scripts are components too. A mimic is a game object with a chest component and an attack component, and "can burn" is one component that any game object can hold.

Components fix the first three breaks. The flaw is that every component is still an object with its own data, its own update function and its own place in memory. A frame makes one call for each component of each object, and the data lies as scattered as before.

### Entities, components and systems

The third way, an entity-component system (ECS), takes the data out of the objects. Components hold only data, and a system holds the code. The components of one type can now lie side by side in one array, which answers the fourth break. The way to store those arrays splits into two forms.

### Sparse sets and archetypes

A **sparse set** keeps one packed array for each component type, plus an index that finds an entity's place in it ([data structures](../basics/data-structures.md) teaches the structure). EnTT, the library Strata uses, works this way. Adding or removing one component touches only the arrays of its type, so it costs the same for every scene size. A loop over one type is a straight run through memory. A loop over several types walks the shortest array and looks the entity up in the others.

An **archetype** is the set of component types that an entity has. The `flecs` library, Unity's Data-Oriented Technology Stack (DOTS) and Bevy store entities of one archetype together in one table with a column for each type. A loop over several types reads whole columns in a row, the best cache use of the four. The flaw is that adding a component changes the archetype, so the engine copies the entity's whole row into another table.

| Model | Cost of adding a component | Cache use | Flexibility | Used by |
| --- | --- | --- | --- | --- |
| Object hierarchy | A new class | One object each, scattered | Low: a mix needs a class | Unreal's `AActor` |
| Objects that own components | One new object | Data in many objects, scattered | High: mix at run time | Unity's `GameObject` |
| ECS, :term[sparse sets]{id=sparse-set} | One array write | Good for one type, lookups for several | High | EnTT, Strata |
| ECS, archetypes | The whole entity moves | Best for several types | High, but changes move data | `flecs`, Unity DOTS, Bevy |

:::elsewhere
Unity's own manual describes a `GameObject` as a container for components, and its DOTS packages store entities in archetype chunks. Bevy keeps entities in archetype tables by default, and `flecs` does the same. The writer of EnTT explains sparse sets in the series "ECS back and forth". The sources are in the further reading.
:::

## Strata keeps one registry, plain data and scene systems

Strata takes the sparse-set form. A `Scene` owns one EnTT registry, the container of all entities and all component arrays. Each module declares its components as plain :term[structs]{id=struct} and registers them by name. The excerpt shows the first four components of the file.

```cpp src="Strata/src/Strata/Scene/Components.h#L28-L48"
struct IDComponent
{
	UUID ID;
};

struct NameComponent
{
	std::string Name;
};

// Optional gameplay label used to find groups of entities ("Enemy", "Pickup").
struct TagComponent
{
	std::string Tag;
};

// Present while an entity is deactivated. Inactive entities (and their descendants) are not rendered,
// simulated or updated by scripts.
struct InactiveComponent
{
};
```

1. **Line 30:** the identity is one 64-bit number, which survives saving and loading.
2. **Line 35:** a name is a string in a component, not the name of a class.
3. **Lines 38–42:** a tag is a label that finds groups of entities, such as every enemy.
4. **Lines 44–48:** a component with no field is a tag component: its presence is the information.

Look at what the structs lack: no pointer to the engine, no function that acts on the entity. They hold values, so the scene file, a copy of the scene and the Inspector can all handle them the same way. `InactiveComponent` has no field at all. It is a tag, and its presence is the whole information: the entity is switched off.

The behaviour is in **scene systems**. A scene system is a class derived from `SceneSystem` that the scene creates when it starts to play and destroys when it stops. The scene calls its `OnUpdate` once per frame, its `OnFixedUpdate` zero or more times per frame at the fixed step of the :term[frame loop]{id=game-loop}, and its `OnLateUpdate` after the others.

Strata registers several, among them `Physics`, `Audio`, `Animation`, `UI` and `Scripting`. [Systems](../world/systems.md) shows their order and their code. Game makers write their own behaviour as script classes. The `Script` component names the classes, and the `Scripting` system runs them for each entity.

The registry alone lacks three things a game needs, and the `Scene` class adds them. An entity gets a persistent identity, a 64-bit number in `IDComponent`, because EnTT recycles its own handles. Entities get a hierarchy of parents and children, which [the scene graph](../world/scene-graph.md) explains. The scene also keeps caches, such as the world position of each entity, which follow what changed and not the size of the scene. [Entities and components](../world/ecs.md) shows how the `Entity` class and the registry fit together.

:::why[Why plain data in one registry?]
Three reasons decided it. A loop over one component type reads packed memory, as the example counted. A scene can hold about a million entities: the limit `Scene::c_MaxEntities` is 1,048,575, and the per-frame cost follows what changed. One description of each component's fields drives the scene file, the Inspector, the commands `component.list` and `component.set`, undo and the functions that scripts call. A new component therefore needs no extra code for each of them.

The price is that a loop over several types looks entities up in more than one array. Strata accepts that for the cheap addition and removal of components, which the editor does all day.
:::

## What this choice cannot do

An entity has no methods and no type of its own. You cannot write `door.Open()`, and you cannot ask whether an entity "is a" door. You ask whether it holds the components that make a door, and a system or a script changes them.

An entity also holds at most one component of each type. A lamp with two lights needs a child entity for the second light. The command `component.add` adds a `PointLight` only where it is missing, so a second add changes the light the entity has. The `Script` component is the exception that proves the point: it holds a list of scripts inside its one component.

Strata does not group entities by their component set. A system that needs five types pays five lookups for each entity, and Strata does not offer the table scan of an archetype engine. [What Strata does not do](../appendix/not-in-strata.md) lists the other things it omits.

## Common mistakes

- **Thinking an entity is an object with methods.** The symptom is a search for `entity.Move()` that finds nothing. Write a function or a system that takes the components and changes them.
- **Putting behaviour into a component.** The symptom is a component that needs a pointer to the renderer or to physics, and a scene that cannot be saved. Keep components to values, and put the code in a system or a script.
- **Adding a second component of one type.** The symptom is that the second add changes the first component's values, or that engine code calling `AddComponent` stops at the assertion "Entity already has the component". Make a child entity for the second one.
- **Holding a reference to a component across a change.** The symptom is a crash or garbage after another entity gains or loses a component of that type, because the arrays move. Look the component up again after each change; [Entities and components](../world/ecs.md) says when it is safe to keep one.

## Summary

- An entity is an identity, and a component is plain data on it, one of each type. A system is code that runs over the entities that have the components it needs, and a scene holds them.
- A class for each kind of thing breaks in five places: two branches, a growing base class, behaviour across classes, scattered objects, and save code for each class.
- Object hierarchies, objects that own components, sparse-set ECS and archetype ECS trade cost of change, cache use and flexibility, as the table shows.
- Strata keeps plain-data components in one EnTT registry and its behaviour in scene systems, so that loops are cache-friendly, scenes are large and one description of the data serves files and editor.
- The same door written three ways gives the same result: as a hierarchy class, as a game object with a behaviour, and as a component with a system. Only the last keeps data apart from code.

## Check yourself

1. A crate in a Strata scene holds `Name`, `Transform` and `MeshRenderer`. Which statement is right?

   - A. The crate is an object of a class `Crate` with a `Draw` method.
   - B. The crate is an identity, and the three are components attached to it.
   - C. The crate is the `MeshRenderer` component, and the others are extras.
   - D. The crate holds two `Transform` components, one local and one world.

   :::answer{tests="ecs-parts"}
   B. An entity is only an identity, and the components are data attached to it. A is the mistake of this page: there is no class and no method. C mixes up the entity with one of its components. D is wrong because an entity holds at most one component of each type.
   :::

2. A designer asks for a `Mimic`, a chest that attacks. Which of the five breaks does a class `Mimic : public Chest, public Enemy` start?

   - A. The number of classes grows with every combination of kinds.
   - B. The objects of the two classes lie in different places in memory.
   - C. The scene file can no longer be read.
   - D. `Update` is no longer virtual.

   :::answer{tests="hierarchy-limits"}
   A. Each mix of two kinds needs a class of its own. B is a real break, but every class has it, and a `Mimic` is no worse. C and D do not follow from a second base class.
   :::

3. A scene has 20,000 things, each with a 12-byte position. A system reads every position, and a cache line is 64 bytes. How many lines does it load when each position sits in its own 200-byte object, and how many from one packed array?

   :::answer{tests="storage-models"}
   The objects need 20,000 lines, one for each position. The array holds 20,000 × 12 = 240,000 bytes, which is 240,000 / 64 = 3,750 lines. The array loads 5.3 times fewer lines.
   :::

4. A teammate proposes `class Door : public Entity` with a method `Open()`, so that `door.Open()` reads well. Which reason against it fits Strata's design?

   - A. Entities are plain numbers, so they cannot have classes in C++.
   - B. The scene, the Inspector and the commands handle components as plain data, and a class for each kind of entity would need its own code for each of them.
   - C. :term[Virtual functions]{id=virtual-function} are not allowed in Strata.
   - D. A scene may hold at most one door.

   :::answer{tests="strata-choice"}
   B. One description of the component fields drives the file, the Inspector and the commands, and the behaviour goes in a system or a script. A is false: the `Entity` class exists, but it is only a handle. C is false: `SceneSystem` has virtual functions. D has nothing to do with the choice.
   :::

5. The door of the exercise below uses a reach of 1.5 instead of 2.5, and the player stands at 4, 3, 2 and 1 on four frames. On which frame does the door open, and why not earlier?

   :::answer{tests="door"}
   On frame 4. The distances are 4, 3, 2 and 1, and the door opens when the distance is below 1.5, which first holds at 1. All three forms use the same test, so they agree.
   :::

## Exercises

1. **Medium.** Write a door that opens when the player comes near, in three object models, and run it for four frames. The player stands at 4, 3, 2 and 1, the door stands at 0, and the reach is 2.5. Use a class hierarchy with a virtual `Update`, a game object that owns a behaviour, and a door component with one system, and print the state of all three each frame. Then say which form Strata uses, and what changes in the other two when the door must also play a sound.

   :::answer[Worked solution]{tests="door strata-choice" solution="sketches/world-what-a-world-is-door.cpp"}
   The program holds the three doors side by side. The distance is the absolute difference of the positions, and each form opens its door when that distance is below the reach.

   ```cpp sketch="world-what-a-world-is-door.cpp"
   // A door that opens when the player comes near, written in three object models.
   #include <cmath>
   #include <cstdio>
   #include <memory>
   #include <vector>

   const float c_Reach = 2.5f;

   // 1. A class hierarchy: the door is a class with its own virtual Update.
   struct Thing
   {
   	float X = 0.0f;
   	virtual ~Thing() = default;
   	virtual void Update(float playerX) = 0;
   };

   struct HierarchyDoor : Thing
   {
   	bool Open = false;
   	void Update(float playerX) override { if (std::fabs(playerX - X) < c_Reach) Open = true; }
   };

   // 2. A game object that owns components, and each component has its own virtual Update.
   struct GameObject;

   struct Behaviour
   {
   	GameObject* Owner = nullptr;
   	virtual ~Behaviour() = default;
   	virtual void Update(float playerX) = 0;
   };

   struct GameObject
   {
   	float X = 0.0f;
   	std::vector<std::unique_ptr<Behaviour>> Behaviours;
   };

   struct OpenWhenNear : Behaviour
   {
   	bool Open = false;
   	void Update(float playerX) override { if (std::fabs(playerX - Owner->X) < c_Reach) Open = true; }
   };

   // 3. An entity component system: the door is data, and one system runs over every door.
   struct DoorComponent
   {
   	float X = 0.0f; // Strata keeps the position in a Transform component of its own
   	bool Open = false;
   };

   void DoorSystem(std::vector<DoorComponent>& doors, float playerX)
   {
   	for (DoorComponent& door : doors)
   		if (std::fabs(playerX - door.X) < c_Reach)
   			door.Open = true;
   }

   int main()
   {
   	HierarchyDoor hierarchyDoor;
   	GameObject gameObject;
   	gameObject.Behaviours.push_back(std::make_unique<OpenWhenNear>());
   	gameObject.Behaviours[0]->Owner = &gameObject;
   	std::vector<DoorComponent> doors(1);
   	for (int frame = 1; frame <= 4; frame++)
   	{
   		const float playerX = 5.0f - static_cast<float>(frame);
   		hierarchyDoor.Update(playerX);
   		gameObject.Behaviours[0]->Update(playerX);
   		DoorSystem(doors, playerX);
   		const OpenWhenNear& behaviour = static_cast<const OpenWhenNear&>(*gameObject.Behaviours[0]);
   		std::printf("frame %d, player at %g: hierarchy %d, objects %d, ecs %d\n", frame, playerX, hierarchyDoor.Open, behaviour.Open, doors[0].Open);
   	}
   	return 0;
   }
   ```

   ```text output-of="world-what-a-world-is-door.cpp"
   frame 1, player at 4: hierarchy 0, objects 0, ecs 0
   frame 2, player at 3: hierarchy 0, objects 0, ecs 0
   frame 3, player at 2: hierarchy 1, objects 1, ecs 1
   frame 4, player at 1: hierarchy 1, objects 1, ecs 1
   ```

   1. **Line 20:** the data and the behaviour of the door share one class, and the `Update` call is virtual.
   2. **Line 42:** the behaviour reaches the position through `Owner`, a pointer to the object that holds it.
   3. **Lines 46–50:** the third door is a struct of values with no function.
   4. **Lines 52–57:** one function visits every door, and a door needs no method.
   5. **Line 73:** the three forms print the same: the door is closed at distances 4 and 3 and open from distance 2.

   All three forms give the same result for one door, so the difference lies in what happens next. For a sound, the hierarchy needs a new class, `SoundDoor`, or a sound field in `Door` that every door then carries. The game object needs a second behaviour, a small addition, but each behaviour is its own object with its own call. The component form needs a `SoundComponent` and a second system, or one more component that the door system reads, and no existing struct changes.

   Strata uses the third form: a plain-data component and a scene system, with the entity as a name for them. For a door in a real game, the data would be a component you declare, and the code would be a script that the `Scripting` system runs.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Scene/Scene.h`: `Scene`, `GetRegistry`, `GetAllEntitiesWith` and `c_MaxEntities`.
- `Strata/src/Strata/Scene/Components.h`: `IDComponent`, `NameComponent`, `TagComponent`, `InactiveComponent` and `TransformComponent`.
- `Strata/src/Strata/Scene/Entity.h`: the `Entity` handle and its `AddComponent`.
- `Strata/src/Strata/Scene/SceneSystem.h`: `SceneSystem`, `SceneSystemDescriptor` and `MakeSceneSystemDescriptor`.
- `StrataEditor/src/Panels/SceneHierarchyPanel.cpp` and `StrataEditor/src/Panels/InspectorPanel.cpp`: the **Hierarchy** and **Inspector** panels.
- Commands: `entity.find` lists the entities that match a name, a tag or a component, and `component.list` lists every component type with its properties.
- `StrataTests/src/Scene/SceneSystemTests.cpp`: the tests of the scene systems.

## Further reading

- [Robert Nystrom, "Component", in Game Programming Patterns](https://gameprogrammingpatterns.com/component.html): the second way, objects that own components, and why it was invented. Beginner.
- [Michele Caini, "ECS back and forth"](https://skypjack.github.io/2019-02-14-ecs-baf-part-1/): the writer of EnTT on entity-component systems and sparse sets. Intermediate.
- [The Unity manual, "GameObjects"](https://docs.unity3d.com/Manual/GameObjects.html): how Unity builds a thing from components. Beginner.
- [The EnTT repository](https://github.com/skypjack/entt): the registry and its documentation, which Strata uses. Advanced.
- The documentation of `flecs` and the Bevy book, chapters on the ECS: archetype storage in two engines, cited without a link. Intermediate.
- The Unreal Engine documentation, "Actors": the class tree around `AActor`, cited without a link. Beginner.
