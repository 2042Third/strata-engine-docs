---
id: make/scripting-scene
title: "Scripts and the scene: finding, spawning and changing entities"
description: "Make Coin Run's coins bob, place them from a script and remove each coin the ball reaches, with the script SDK's Entity, Scene and Assets."
kind: how-to
size: L
tracks: [G, B]
needs: [make/script-loop]
time: 75
learn:
  - id: namespaces
    text: name the script SDK's classes and the page that teaches each one
  - id: request-early
    text: write a script that asks for a prefab early and places instances once it has loaded
  - id: find-entities
    text: find entities by name and by tag, and keep an Entity safely between frames
  - id: change-entities
    text: change an entity's transform and a component's properties from a script
  - id: collect-coin
    text: build a coin that hides, glows and is destroyed when the ball reaches it
since: 0.3.0
status: final
---

Coin Run's coins spin. This page makes them bob up and down, places them from a script instead of by hand, and removes each coin the ball reaches. On the way you meet the three parts of the script library that a game uses most: the entity, the scene and the assets. Before you start:

- Coin Run is at the end of [your first script](first-script.md): five hand-placed coin instances that spin, and the ball `Ball` at (0, 0.5, 6). Continue your own project, or download it at the last checkpoint of [that page](first-script.md#change-the-code-while-playing-then-crash-it).
- You read [the page on a script's frame](script-loop.md), whose example is the bob built in the first step here.
- You read "The same ideas in code" of [the page on positions, rotations and units](transforms-units.md) again.
- The scene holds an entity named `Ball`. The coin :term[prefab]{id=prefab-make} is `Prefabs/Coin.stprefab`; its root carries the tag `Coin` and the `Coin` script.

## The script SDK at a glance

Every script includes one header, `StrataScript/StrataScript.h`, and sees only the classes it declares. That header opens the software development kit (:term[SDK]{id=sdk}) of scripts: the code you write scripts against, which holds no engine code. The table lists the classes a game uses most and the page that teaches each one. The facts of every class and every call are in the [complete reference of the script calls](../reference/script-api.md).

| Class | What a script does with it | Taught on |
| --- | --- | --- |
| `Entity` | Refers to one entity: its name, tag, activity, parent, children, components and removal | This page |
| `Component` | Reads and writes any component by its name | This page |
| `TransformComponent` | Reads and writes an entity's position, rotation and scale | This page |
| `Scene` | Creates and finds entities, and places prefab instances | This page |
| `Assets` | Asks for assets and follows their loading | This page |
| `SubScene` | A scene loaded next to the playing one | [Levels and saves](levels-saves.md) |
| `Input` | Keys, the mouse and gamepads | [Input](input.md) |
| `Physics`, `RigidBody` | Bodies, forces and rays | [Physics](physics.md) |
| `AudioSource`, `Audio` | Sound | [Sound](sound.md) |
| `UIElement` | Text and widgets of the game's screen | [The heads-up display](hud.md) |
| `Time` | Delta time and clocks | [A script's frame](script-loop.md) and [timers and events](timers-events.md) |
| `Game` | Quitting, loading scenes and save files | [Levels and saves](levels-saves.md) |

Two members of `Script` matter at once. `GetEntity()` returns the entity the script is attached to, and `GetTransform()` is a short form of `GetEntity().GetTransform()`. The spinning script of the first page already used the second one. Hiding or destroying "my own coin" in step 8 uses the first one.

An `Entity` is a small value that holds the identity number of an entity. You copy it freely and keep it in a member variable. It does not keep the entity alive: if the entity is destroyed, every call on your copy does nothing and returns an empty result. `IsValid()` tells you which case you are in.

## Make the coins bob

A coin that only spins looks flat. A coin that also rises and falls looks alive. The height needs a number that swings smoothly between a low and a high value, and the sine function gives one. The sine of an angle is a value between -1 and 1, and it repeats as the angle grows.

The height of the coin at time $t$ is the height where it was placed, plus a swing.

Take a `BobHeight` of 0.1 metres and a `BobSpeed` of 2. Then the swing is $0.1 \cdot \sin(2t)$. Here are three moments. At $t = 0$ the sine is 0, so the coin sits at its base. At $t = 0.785$ seconds the angle $2t$ is about 1.57, the sine is 1 and the coin is 0.1 metres above its base.

At $t = 2.36$ seconds the sine is -1 and the coin is 0.1 metres below. One full swing lasts about 3.14 seconds.

All the numbers come from `Time::GetElapsedTime()`: the seconds of game time since the scene started playing. It returns a `double`, a number with more digits than the `float` that glm and the fields use. A `float` times a `double` gives a `double`, and storing that in a `float` drops digits, so the script converts once.

:::question
What does `override` mean after a function? [Inheritance and `override`](../basics/cpp-classes.md) explains it.
:::

:::::steps

1. Change the code of the `Coin` script to add the bob. The script keeps its spin, adds two fields and stores its starting height in `OnCreate`, which runs once before the first update.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Open `Scripts/Coin.cpp` in your code editor, replace its whole text with the two parts below, one after the other, and save. Then choose **Scripts ▸ Build Scripts** (**Ctrl+B**).
   :::
   :::tab[With a command]
   No command writes a file: replace the text of `Scripts/Coin.cpp` with the two parts below in your code editor, then run the build.

   ```json
   { "command": "script.build" }
   ```

   :::
   ::::

   The first part holds the includes, the fields and `OnCreate`. Look at the two new fields and where the height is stored.

   ```cpp src="book:tutorials/make/scripting-scene/Coin.step1.cpp#L1-L20"
   // The Coin script of Coin Run: it turns, and now it also bobs.

   #include "StrataScript/StrataScript.h"

   #include <cmath>

   using namespace Strata;

   class Coin : public Script
   {
   public:
   	float DegreesPerSecond = 90.0f; // Fields: editable per entity
   	float BobHeight = 0.1f;
   	float BobSpeed = 2.0f;

   	void OnCreate() override
   	{
   		// The height the coin was placed at: the bob swings around it.
   		m_BaseHeight = GetTransform().GetTranslation().y;
   	}
   ```

   1. **Line 5:** `<cmath>` declares `std::sin`.
   2. **Lines 13–14:** the two new fields, beside the spin's `DegreesPerSecond`.
   3. **Line 19:** the height at which the coin was placed. The bob swings around it, so a coin placed higher bobs higher.

   The second part keeps the spin of the first page and adds the bob. Look at where the stored height is used.

   ```cpp src="book:tutorials/make/scripting-scene/Coin.step1.cpp#L22-L43"
   	void OnUpdate(float deltaTime) override
   	{
   		TransformComponent transform = GetTransform();
   		const glm::quat turn = glm::angleAxis(glm::radians(DegreesPerSecond * deltaTime), glm::vec3(0.0f, 1.0f, 0.0f));
   		transform.SetRotation(turn * transform.GetRotation());

   		// Time::GetElapsedTime() is a double; the sine and the fields are floats.
   		const float swing = std::sin(BobSpeed * static_cast<float>(Time::GetElapsedTime()));
   		glm::vec3 position = transform.GetTranslation();
   		position.y = m_BaseHeight + BobHeight * swing;
   		transform.SetTranslation(position);
   	}
   private:
   	float m_BaseHeight = 0.0f;
   };

   ST_SCRIPT_CLASS(Coin)
   {
   	ST_SCRIPT_FIELD(DegreesPerSecond);
   	ST_SCRIPT_FIELD(BobHeight);
   	ST_SCRIPT_FIELD(BobSpeed);
   }
   ```

   1. **Line 25:** the same turn as the first page, scaled by the frame's delta time.
   2. **Line 29:** the sine, with the time since the start converted to a `float` by `static_cast`.
   3. **Lines 30–32:** read the position, change only its height, and write it back.
   4. **Lines 34–35:** the member that keeps the height, below `private:`.
   5. **Lines 38–43:** every field needs its `ST_SCRIPT_FIELD` line, or the Inspector does not show it.

   Play the game with **Play** (**Ctrl+P**).

   **You should see:** every coin turn and rise and fall, about once in three seconds.

   **If you do not see it:** the status bar says "Build failed". Click it and read the :term[Problems panel]{id=problems-panel}. A missing `;` or a field without its `ST_SCRIPT_FIELD` line are common slips: compare your code with the code above.

:::::

:::caution
This script keeps `m_BaseHeight` in an ordinary member, not in a field. A :term[hot reload]{id=hot-reload} constructs the script again, so the member starts over at 0 and the coin drops to the ground. Stop and play again after you change this script.
:::

## Place the coins from a script

Five coins placed by hand are five things to move whenever the level changes. A script can hold their positions in one list and place the coins when the game starts. That also removes the five instances from the scene, so you can delete them now.

<!-- markdownlint-disable MD029 -->
:::::steps

2. Add an empty entity and a new script. The entity `Coins` is the parent of the coins you place; the script `CoinPlacer` does the placing. Keep `Coins` at the origin: the positions below count from its position.

   ::::tabs{sync=how}
   :::tab[In the editor]
   In the Hierarchy panel press **+**, choose **Empty** and rename the entity `Coins`. Choose **Scripts ▸ New Script...**, name the class `CoinPlacer` and create it. Build the scripts, select `Coins` and choose **Add Component ▸ Script** in the Inspector, then pick `CoinPlacer`.
   :::
   :::tab[With a command]

   ```json
   { "command": "entity.create", "parameters": { "name": "Coins" } }
   ```

   Then run `script.create` with `{ "class": "CoinPlacer" }`, `script.build`, and `script.add` with the id of `Coins` and the class `CoinPlacer`.
   :::
   ::::

   **You should see:** the entity `Coins` in the Hierarchy, with a Script component that names `CoinPlacer`.

   **If you do not see it:** `CoinPlacer` is not in the list of the Script component. The scripts are not built, or the build failed: build them and read the Problems panel.

3. Ask for the prefab early. A prefab is a file on disk, and reading it takes time. Strata never makes a frame wait for the disk. So you ask for the asset in `OnCreate`, and you use it later, when it has loaded.

   ::::tabs{sync=how}
   :::tab[In the editor]
   In the Content Browser, right-click `Coin.stprefab` and choose **Copy Path**. The text it copies is the path the calls below take: relative to the Assets folder, with `/` between folders.
   :::
   :::tab[With a command]
   Use the path `Prefabs/Coin.stprefab` as it is: the asset commands list every path of the project, and `Assets::Find` takes the same text.
   :::
   ::::

   The two calls below do the asking. `Assets::Find` turns a path into a handle, which is a number that names the asset; the handle is empty when no asset has that path. `Assets::RequestLoad` starts loading in the background and keeps the asset loaded while the scene plays.

   Replace the whole text of `Scripts/CoinPlacer.cpp`, which `script.create` wrote with an example field `Speed`, with the file below and save. The class needs no field, so its `ST_SCRIPT_CLASS` block stays empty.

   ```cpp src="book:tutorials/make/scripting-scene/CoinPlacer.step3.cpp#L1-L20"
   // Places Coin Run's coins when the game starts. Attach it to the empty entity Coins, which stays at the origin.

   #include "StrataScript/StrataScript.h"

   using namespace Strata;

   class CoinPlacer : public Script
   {
   public:
   	void OnCreate() override
   	{
   		// Ask early: loading takes frames, and Instantiate never waits for it.
   		m_CoinPrefab = Assets::Find("Prefabs/Coin.stprefab");
   		Assets::RequestLoad(m_CoinPrefab);
   	}
   private:
   	AssetHandle m_CoinPrefab;
   };

   ST_SCRIPT_CLASS(CoinPlacer) {}
   ```

   1. **Lines 13–14:** the asking, in `OnCreate`.
   2. **Line 17:** the handle stays in this member, so every later frame uses it without a new `Find`.
   3. **Line 20:** the registration of a class without fields.

   :::rule
   Request assets early. `Scene::Instantiate` never waits: for an asset that is not loaded it starts the load and returns an empty entity. No frame of the game waits for the disk, so your script must handle "not loaded yet" in every frame ([asset requests](../assets/residency.md)).
   :::

   **You should see:** nothing yet. The scripts build without errors.

   **If you do not see it:** the build lists an error such as "Assets was not declared". The line `#include "StrataScript/StrataScript.h"` is missing at the top of the file.

:::::
<!-- markdownlint-enable MD029 -->

The picture below shows the order that the next step builds. The request goes first, the waiting continues over frames, and the placing happens once.

```mermaid caption="The order of the calls: the request in the creation callback, a check in every update until the prefab has loaded, then one placing." alt="A flow from the request in the creation callback to a check in each update. While the prefab is not loaded, the flow returns to the check. Once it is loaded, the flow reaches the placing, which runs once."
flowchart TD
    A["OnCreate: Find, then RequestLoad"] --> B["Every OnUpdate: is it loaded?"]
    B -->|"not yet"| B
    B -->|"loaded"| C["Instantiate five times, once"]
```

<!-- markdownlint-disable MD029 -->
:::::steps

4. Place the coins when the prefab has loaded. `OnUpdate` returns early while the prefab loads or after the coins are placed. Then a loop walks a list of positions and places one instance at each. Look at the arguments of `Instantiate`: the last one is the parent.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Delete the five hand-placed coins: select them in the Hierarchy and press **Delete**. Then change `Scripts/CoinPlacer.cpp` as the two parts below show, build, and play.
   :::
   :::tab[With a command]
   Delete the five hand-placed coins first. `entity.find` with `{ "tag": "Coin" }` answers their identifiers (IDs) as a list, and `entity.delete` takes that list as `entities`:

   ```json
   { "command": "entity.delete", "parameters": { "entities": [ "<ID 1>", "<ID 2>", "<ID 3>", "<ID 4>", "<ID 5>" ] } }
   ```

   Its answer names the five IDs under `deleted`. Change `Scripts/CoinPlacer.cpp` in your code editor as the two parts below show, then run `script.build` and `play.start`.
   :::
   ::::

   The first part is the list of positions. It goes at the top of the file, below `using namespace Strata;` and above the class.

   ```cpp src="book:tutorials/make/scripting-scene/CoinPlacer.cpp#L7-L14"
   static const glm::vec3 c_CoinPositions[] =
   {
   	{ -4.0f, 0.8f, 0.0f },
   	{ -2.0f, 0.8f, 2.0f },
   	{ 0.0f, 0.8f, 3.0f },
   	{ 2.0f, 0.8f, 2.0f },
   	{ 4.0f, 0.8f, 0.0f },
   };
   ```

   These five positions lie on a half circle in front of the origin, a little less than a metre above the ground. Use positions of your own if you like.

   The second part goes below `OnCreate`, to the end of the file: the function `OnUpdate`, then the class's end with the new member `m_Placed` below `m_CoinPrefab`. The function runs in every frame. Look at the early return and at the loop that places the coins.

   ```cpp src="book:tutorials/make/scripting-scene/CoinPlacer.cpp#L26-L43"
   	void OnUpdate(float deltaTime) override
   	{
   		if (m_Placed || !Assets::IsLoaded(m_CoinPrefab))
   			return;

   		const glm::quat noTurn(1.0f, 0.0f, 0.0f, 0.0f);
   		for (const glm::vec3& position : c_CoinPositions)
   			Scene::Instantiate(m_CoinPrefab, position, noTurn, glm::vec3(1.0f), GetEntity());
   		m_Placed = true;

   		Log::Info("Coins placed: ", Scene::FindEntitiesByTag("Coin").size());
   	}
   private:
   	AssetHandle m_CoinPrefab;
   	bool m_Placed = false;
   };

   ST_SCRIPT_CLASS(CoinPlacer) {}
   ```

   1. **Line 28:** `IsLoaded` is false while the prefab loads, so the function returns and tries again next frame.
   2. **Line 31:** a rotation that turns nothing: the four numbers are the :term[quaternion]{id=quaternion} for "no turn".
   3. **Line 33:** the full call: handle, position, rotation, scale and parent. The position counts from the parent, here `Coins`.
   4. **Line 34:** remembers that the coins exist, so the loop never runs twice.
   5. **Line 36:** writes the number of entities with the tag `Coin` to the Console.

   **You should see:** five coins appear at once, a moment after Play, and the Console prints `Coins placed: 5`.

   **If you do not see it:** the Console prints `Coins placed: 10`. The five hand-placed coins are still in the scene: stop, delete them and play again. No coin appears and the Console is silent: the path is wrong, so `Assets::Find` returned an empty handle and `IsLoaded` stays false. Copy the path again with **Copy Path**.

:::::
<!-- markdownlint-enable MD029 -->

Two details of `Instantiate` surprise people. The call that takes a position replaces the root's whole transform, so its scale is the `glm::vec3(1.0f)` you pass, not the prefab's own scale. A prefab whose root is scaled to 2 would come out half as big as in the editor. Pass its scale as the fourth argument.

The second detail is the load progress. `Assets::IsLoaded` says the prefab file has loaded. `Assets::GetLoadProgress` returns a number from 0 to 1 for the prefab and everything it uses, such as its meshes and textures: at 1 an instance draws complete in its first frame. Its first call also starts the loading, and it returns a negative number for an unknown asset. Use it for a loading bar or to wait until 1 before a level starts.

A request ends when you call `Assets::Release(handle)` or when the game stops. Requests belong to the scene, not to the script that made them, and they do not add up. If `CoinPlacer` and another script both request the coin prefab and one of them calls `Release`, the request is over for both. The engine may then unload the prefab when memory is short, and load it again when something uses it. `Release` returns false when the scene holds no request for the asset.

:::why
Script code runs on the main thread, which also draws the frame, so a call that waited for a file would freeze the whole game while the disk works. Strata chose to return an empty entity at once. The cost is yours: a script that places things needs a waiting state, as `CoinPlacer` has in `m_Placed`. A forgotten early request shows as an empty result in the first test, not as a hidden stall that appears only on a slow disk.
:::

## Find and change entities

The coins now exist. The next steps find the ball and the coins, and change them. Every call here is on `Scene` or `Entity`.

<!-- markdownlint-disable MD029 -->
:::::steps

5. Find entities by name and by tag. `Scene::FindEntityByName` returns the first entity with a name, in hierarchy order: parents before children, in the order of the Hierarchy panel. `Scene::FindEntitiesByTag` returns all entities that carry a tag. The tag `Coin` is the one the coin prefab carries.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Add the three lines below to the end of `OnCreate` in `Scripts/Coin.cpp` and the member `Entity m_Ball;` below `private:`, then build and play.
   :::
   :::tab[With a command]
   Run `script.build` and `play.start`.
   :::
   ::::

   The code below finds the ball once and warns when the scene has no such entity.

   ```pseudocode
   m_Ball = Scene::FindEntityByName("Ball");
   if (!m_Ball.IsValid())
       Log::Warn("The scene has no entity named Ball");
   ```

   The `Entity` named `m_Ball` is a member of the class: you find the ball once and keep it. You never keep anything else about it, such as a position, because the ball moves. Every frame you ask the stored `Entity` for what you need, and you check `IsValid()` first, because the ball may be destroyed one day.

   Suppose you stored the ball's position at the start, (0, 0.5, 6), and the player later moves the ball to (3, 0.5, 6). Your coin still measures against the old place. A stored `Entity` always answers with the ball's position of this frame.

   **You should see:** no warning in the Console.

   **If you do not see it:** the warning appears. No entity is named `Ball`, or the name has other letters: names are compared exactly, with capitals.

:::::
<!-- markdownlint-enable MD029 -->

The finds have two limits that matter for counting. They see inactive entities, and they see entities destroyed in the current frame until the frame ends. A coin hidden with `SetActive(false)` is still in the result of `FindEntitiesByTag("Coin")`. A count of what is left should skip those entities with `IsActive()`, or count after the destruction has happened. A hidden panel found by its name is found too.

<!-- markdownlint-disable MD029 -->
:::::steps

6. Read and write a transform. `GetTransform()` returns a `TransformComponent`, a view of the entity's transform. Its plain functions, such as `GetTranslation` and `SetTranslation`, work in the local space, relative to the parent. The ones with `World` in the name work in the space of the whole scene. A coin placed at local (2, 0.8, 2) under `Coins` at (10, 0, 0) has the :term[world position]{id=world-position} (12, 0.8, 2).

   ::::tabs{sync=how}
   :::tab[In the editor]
   The Inspector shows the local values under **Transform**. Select a coin while the game plays to compare them with what the script reads.
   :::
   :::tab[With a command]
   While the game plays, run `entity.find` with `{ "tag": "Coin" }` for the ids of the coins, then `component.get` with `{ "entity": "<id of a coin>", "component": "Transform" }` to read the same values.
   :::
   ::::

   The code below reads the position in both spaces, then writes the position, the world position and the scale. It shows the calls only: this step adds nothing to your files.

   ```pseudocode
   TransformComponent transform = GetTransform();
   glm::vec3 local = transform.GetTranslation();
   glm::vec3 world = transform.GetWorldPosition();
   transform.SetTranslation(local + glm::vec3(0.0f, 1.0f, 0.0f));
   transform.SetWorldPosition(glm::vec3(0.0f, 5.0f, 0.0f));
   transform.SetScale(glm::vec3(2.0f));
   ```

   The first two lines read the position twice. The functions that write change the entity at once, and Strata notices the change, so the coin is drawn in its new place. Rotation works the same way: `GetRotation` and `SetRotation` take a quaternion, and `GetEulerAngles` gives the angles in radians.

   **You should see:** the coin's Inspector values change as the game plays, because the bob rewrites its height.

   **If you do not see it:** the values stay still. The game is paused, or the Coin script is not on the coin.

:::::
<!-- markdownlint-enable MD029 -->

The local and world versions differ only while a parent moves or turns. For a root entity they are the same. That is why the bob works on the local height: the coin's parent `Coins` never moves.

<!-- markdownlint-disable MD029 -->
:::::steps

7. Reach components by name. The typed classes, such as `TransformComponent`, cover the components a game uses most. Every other component is reached by its registered name. `HasComponent("MeshRenderer")` asks whether it exists, and `GetProperty` and `SetProperty` read and write one of its properties by name.

   ::::tabs{sync=how}
   :::tab[In the editor]
   To learn a name, select an entity, open a component's menu in the Inspector and choose **Copy Values**. The editor copies the component's name and its values as JSON text.
   :::
   :::tab[With a command]
   Run `component.list` to read every registered component name, or `component.get` to read one component with its property names.
   :::
   ::::

   The registered name is mostly the label without its spaces: `MeshRenderer` for **Mesh Renderer**, `CastShadows` for **Cast Shadows**. Some differ more: the sun's **Angular Diameter** is `ShadowSoftness`. The comparison ignores capitals. The [list of components](../reference/components.md) shows every name. A wrong name does not crash the game: the call fails and the Console shows a problem.

   The `Component` class bundles an entity and a component name, so you write the name once.

   ```pseudocode
   Component renderer = mesh.GetComponent("MeshRenderer");
   const bool casts = renderer.Get<bool>("CastShadows", true);
   renderer.Set("CastShadows", false);
   ```

   The coin's glow shows both calls at work. The emission, the light a surface gives out, belongs to the material asset, which every gold coin shares. A Mesh :term[Renderer]{id=renderer} holds only the mesh, the material and `CastShadows`. So the coin does not raise its own emission: it swaps its material for `GoldGlow`, which you asked for early, like the prefab. The Mesh Renderer sits on a descendant of the prefab's root, so the code first searches the children.

   ```cpp src="book:tutorials/make/scripting-scene/Coin.cpp#L48-L68"
   // The Mesh Renderer sits on a descendant of the prefab's root: search the children.
   static Entity FindMeshEntity(Entity entity)
   {
   	if (entity.HasComponent("MeshRenderer"))
   		return entity;
   	for (Entity child : entity.GetChildren())
   	{
   		const Entity found = FindMeshEntity(child);
   		if (found.IsValid())
   			return found;
   	}
   	return Entity();
   }

   void Glow()
   {
   	if (m_Glowing || !Assets::IsLoaded(m_GlowMaterial))
   		return;
   	Entity mesh = FindMeshEntity(GetEntity());
   	m_Glowing = mesh.IsValid() && mesh.SetProperty("MeshRenderer", "Material", m_GlowMaterial);
   }
   ```

   1. **Lines 49–60:** a search that checks the entity, then asks each child to search in the same way, and returns the first entity that has a Mesh Renderer.
   2. **Line 64:** waits until the glow material has loaded, and does nothing once the coin glows.
   3. **Line 66:** the search starts at the coin's own entity.
   4. **Line 67:** `SetProperty` returns whether it worked, and the result is stored.

   The type of a property comes from the value you pass. The SDK converts `bool`, `int32_t`, `uint32_t`, `int64_t`, `float`, the glm vectors, `glm::quat`, `std::string`, `Entity` and `AssetHandle`. A `double` does not compile, and the error talks about an incomplete `ValueTraits`.

   The literal `0.5` is a `double`: write `0.5f`, or name the type, `SetProperty<float>(...)`. A text literal does not compile either: write `std::string("text")`. A float property accepts an integer value; an integer property refuses a float when the game runs.

   Make the material the glow swaps in: `GoldGlow`, a copy of `Gold` with a stronger emission. At 1,000 :term[nits]{id=lux} it glows like a lit sign, five times as bright as `Gold`'s 200.

   ::::tabs{sync=how}
   :::tab[In the editor]
   In the Content Browser open the `Materials` folder, press **New ▸ Material**, type `GoldGlow` and press **Enter**. In the Asset tab give it the values of `Gold`: `Base Color` (1.0, 0.77, 0.34), `Metallic` 1, `Roughness` 0.3 and `Emissive Color` (1.0, 0.75, 0.3); then set `Emissive Intensity` to `1000`.
   :::
   :::tab[With a command]

   ```json
   { "command": "material.create", "parameters": { "path": "Materials/GoldGlow.stmat", "properties": { "BaseColor": [1.0, 0.77, 0.34, 1.0], "Metallic": 1.0, "Roughness": 0.3, "EmissiveColor": [1.0, 0.75, 0.3], "EmissiveIntensity": 1000 } } }
   ```

   :::
   ::::

   Put the code above into the class in `Coin.cpp`, below `private:` and above the members: `FindMeshEntity` is a `static` function of the class, which needs no coin to run. Add the field `float GlowDistance = 2.0f;` with its `ST_SCRIPT_FIELD` line, and below `private:` the members `AssetHandle m_GlowMaterial;` and `bool m_Glowing = false;`. At the end of `OnCreate`, ask for the material early with `m_GlowMaterial = Assets::Find("Materials/GoldGlow.stmat");` and `Assets::RequestLoad(m_GlowMaterial);`.

   **You should see:** the scripts build without errors. Nothing glows yet: step 8 calls `Glow()` when the ball comes near.

   **If you do not see it:** the build lists an error such as "m_Glowing was not declared". A member is missing: add it below `private:`.

:::::
<!-- markdownlint-enable MD029 -->

## Collect a coin and look at the hierarchy

<!-- markdownlint-disable MD029 -->
:::::steps

8. Hide the coin, then destroy it. The coin tests the distance between itself and the ball in every update, with `glm::distance`. The distance between two points is the length of the straight line between them (`glm::distance(a, b)` returns it, in metres): [the vectors page](../basics/math-vectors.md) explains why. The first version only hides the coin.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Put the lines below at the end of `Coin::OnUpdate` and add the field `float CollectDistance = 0.7f;` with its `ST_SCRIPT_FIELD` line. Build, play, and drag the ball onto a coin with the :term[gizmo]{id=gizmo-start}. Moving the ball by script is a matter of [the input page](input.md).
   :::
   :::tab[With a command]
   Run `script.build` and `play.start`. While the game plays, `component.set` moves the ball in the running copy of the scene: first near the coin at (0, 0.8, 3), then onto it.

   ```json
   { "command": "component.set", "parameters": { "entity": "<id of Ball>", "component": "Transform", "values": { "Translation": [0, 0.8, 1.5] } } }
   ```

   Then run the same command with the `Translation` `[0, 0.8, 2.6]`.
   :::
   ::::

   Suppose the coin is at (0, 0.8, 3). With the ball at (0, 0.8, 1.5) the distance is 1.5 metres: the coin glows but stays. With the ball at (0, 0.8, 2.6) the distance is 0.4 metres, under the limit of 0.7, and the coin is collected. The code below makes that test and hides the coin.

   ```pseudocode
   const float distance = glm::distance(transform.GetWorldPosition(), m_Ball.GetTransform().GetWorldPosition());
   if (distance < CollectDistance)
       GetEntity().SetActive(false);
   ```

   `SetActive(false)` hides the coin and stops its updates, but the entity stays. It still counts in a find by tag, and `IsActive()` returns false. That is right for a coin you want back, as a pooled object. For a collected coin, destroy it. `Destroy()` removes the entity and its descendants at the end of the frame, so the rest of your `OnUpdate` still runs with a valid entity.

   :::why
   Other scripts run in the same frame, and some may hold the entity. If `Destroy` removed it at once, they would meet a half-removed entity. Waiting for the end of the frame keeps every script's view of the frame the same. The cost is that the entity is still there, and still found, until the frame ends.
   :::

   The lines below make the test and the destruction. Look at the early return for a missing ball and at the last line.

   ```cpp src="book:tutorials/make/scripting-scene/Coin.cpp#L39-L45"
   if (!m_Ball.IsValid())
   	return;
   const float distance = glm::distance(transform.GetWorldPosition(), m_Ball.GetTransform().GetWorldPosition());
   if (distance < GlowDistance)
   	Glow();
   if (distance < CollectDistance)
   	GetEntity().Destroy();
   ```

   Line 45 is the whole change: `GetEntity().Destroy()` replaces `SetActive(false)`. Lines 39 and 40 leave the update early when the ball is gone, and line 43 starts the glow from step 7.

   **You should see:** the coin turns brighter when the ball comes within 2 metres. It vanishes within 0.7 metres, and the Hierarchy loses its entry. In the Console, `Coins placed: 5` appeared at the start only.

   **If you do not see it:** the coin stays while the ball sits on it. The ball is not at the same height: the test uses the distance in all three dimensions, so a ball 1 metre above the coin is too far. Raise `CollectDistance` in the Inspector. A coin that never brightens: a problem such as "has no property" in the Console means a wrong name, and silence means `GoldGlow.stmat` has not loaded.

9. Walk the hierarchy. The `Coins` entity is the parent of the coins, and an `Entity` knows its relatives. `GetChildren()` returns a list, `GetParent()` the parent, and `SetParent` moves an entity, keeping its world position unless you pass `false` as the second argument. `SetParent` returns false if the change would make an entity its own ancestor.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Drag an entity onto another in the Hierarchy to change its parent. The script calls below do the same from code.
   :::
   :::tab[With a command]
   While the game plays, run `entity.find` with `{ "name": "Coins" }` for its id, then `entity.get` with that id to read its children. In edit mode the list is empty: `CoinPlacer` places the coins only when the game starts.
   :::
   ::::

   The code below lists the coins with their parent, creates an entity under `Coins`, makes it a root and asks for the camera. Like the code of step 6, it shows the calls only and goes into no file.

   ```pseudocode
   Entity coins = Scene::FindEntityByName("Coins");
   for (Entity coin : coins.GetChildren())
       Log::Info(coin.GetName(), " is under ", coin.GetParent().GetName());
   Entity spare = Scene::CreateEntity("Spare", coins);
   spare.SetParent(Entity());
   Entity camera = Scene::GetPrimaryCamera();
   ```

   `Scene::CreateEntity` makes an empty entity with a transform, below the parent you pass or as a root. `SetParent(Entity())` with an empty entity makes `spare` a root again. `Scene::GetRootEntities()` lists all roots, and `Scene::GetPrimaryCamera()` returns the camera the game view draws from, or an empty entity.

   **You should see:** while the game plays, the five coins under `Coins` in the Hierarchy, and their five IDs under `children` in the answer of `entity.get`. `parent` is `null`, because `Coins` is a root.

   **If you do not see it:** `Coins` has no children. The game is not playing: the coins exist only while it plays.

:::::
<!-- markdownlint-enable MD029 -->

## Result

Coin Run's coins bob and spin. A script, `CoinPlacer`, places them from a list of positions once the prefab has loaded, as children of `Coins`. Each coin watches the ball, glows when the ball comes within 2 metres and destroys itself within 0.7 metres. The Console reports the count at the start, and the finished scripts are `Scripts/Coin.cpp` and `Scripts/CoinPlacer.cpp` of the project you built. The download below holds the project with both files whole: compare yours with them when a build fails.

## Variations

- **Destroy every entity of a tag at once.** Loop over `Scene::FindEntitiesByTag("Coin")` and call `Destroy()` on each. All the entities go at the end of the frame, so the list you loop over stays valid during the loop. A level that ends can clear its coins this way.
- **Many copies in one call.** A forest or a crowd places hundreds of instances. `Scene::InstantiateMany` does that in one call; [the performance page](performance.md) teaches it.
- **A prefab chosen in the Inspector.** A :term[script field]{id=script-field} of the type `AssetHandle` lets a designer pick the prefab and skips the path in the code. [Script fields](script-fields.md) shows how.
- **Scripts that call each other.** `GetScript<T>` reaches a script on another entity: [timers and events](timers-events.md).

## Summary

- The script SDK has a class for each area of the game; `Entity`, `Component`, `TransformComponent`, `Scene` and `Assets` are taught here, the others on the pages of the table.
- Ask for assets early with `Assets::Find` and `Assets::RequestLoad`, and place instances once `Assets::IsLoaded` is true: `Scene::Instantiate` never waits.
- Find entities with `Scene::FindEntityByName` and `Scene::FindEntitiesByTag`; keep an `Entity`, not its data, and check `IsValid()`. The finds see inactive entities.
- Change a transform with the local and world functions, and any other component through its registered name with `GetProperty`, `SetProperty` or the `Component` class.
- `SetActive(false)` hides an entity but keeps it; `Destroy()` removes it at the end of the frame.

## Check yourself

1. A script calls `Scene::Instantiate` for a prefab that is still loading. What does it return, and what does it start?

   :::answer{tests="request-early"}
   `Scene::Instantiate` returns an empty entity, and it starts loading the prefab in the background. It never waits. So the script asks early with `RequestLoad` and places instances only when `Assets::IsLoaded` is true.
   :::

2. Two scripts both call `Assets::RequestLoad` for the same prefab. One of them calls `Assets::Release`. Does the other script's request still hold?

   :::answer{tests="request-early"}
   No. Requests belong to the scene, and they do not add up. One `Release` ends the request for both, and the engine may unload the prefab when memory is short.
   :::

3. In one frame a coin calls `SetActive(false)` and another calls `Destroy()`. What does `FindEntitiesByTag("Coin").size()` count in that frame, and in the next?

   :::answer{tests="find-entities,collect-coin"}
   In that frame it counts both coins: finds see inactive entities and entities destroyed in the current frame. In the next frame it counts the hidden coin but not the destroyed one. Skip hidden coins with `IsActive()` when you count.
   :::

4. A coin has the :term[local position]{id=local-position} (3, 1, 0) under a parent at (10, 0, 0), with no rotation and a scale of 1. What do `GetTranslation()` and `GetWorldPosition()` return?

   :::answer{tests="change-entities"}
   `GetTranslation()` returns (3, 1, 0), relative to the parent. `GetWorldPosition()` returns (13, 1, 0): the parent's position plus the local one.
   :::

5. A script writes `mesh.SetProperty("MeshRenderer", "Foo", 0.5);` for a float property. Why does it not compile, and how do you fix it?

   :::answer{tests="change-entities"}
   The literal `0.5` is a `double`, and the SDK converts no `double`. Write `0.5f`, or name the type with `SetProperty<float>(...)`.
   :::

6. Which page teaches reading the keyboard from a script?

   :::answer{tests="namespaces"}
   The page on input, [Input](input.md): the `Input` class is in the table at the top of this page.
   :::

## Exercises

Exercise 3 asks for a small program of its own, a sketch. Running it needs a C++ compiler, which [Installing Strata and the C++ build tools](../start/install.md) gives you, and [How a C++ program is built](../basics/build.md) shows how to compile one file. Without them, work the distances out by hand and check them against the printed output.

1. **Basic.** In `CoinPlacer`, log the number of coins left once a second. Predict the count after the ball collected two coins.

   :::answer{tests="find-entities"}
   Count `Scene::FindEntitiesByTag("Coin").size()` and log it when `Time::GetElapsedTime()` passes the next whole second. After two coins are destroyed and their frame has ended, the count is 3. The function is `Scene::FindEntitiesByTag` in `Strata/src/Strata/Scene/Scene.cpp`; it does no check of activity.
   :::

2. **Medium.** Disable the coins from `CoinPlacer` five seconds after they are placed, and enable them again three seconds later. Predict whether the coins bob while they are disabled.

   :::answer[Worked solution]{tests="change-entities,collect-coin" solution="tutorials/make/scripting-scene/exercise-2.tutorial.json"}
   The coins do not bob: inactive entities get no updates, so `Coin::OnUpdate` does not run. The solution switches the children of `Coins` off and on with `SetActive`. It does not switch `GetEntity()`, because an inactive `CoinPlacer` would receive no more updates and could never enable the group again. The file is `exercise-2/CoinPlacer.cpp` of this page's tutorial folder.
   :::

3. **Medium.** The ball stands at (0, 0.8, 2.6). By hand, work out its distance to the coin at (0, 0.8, 3) and to the coin at (-2, 0.8, 2). Then write a small program that prints the distance of every coin, whether it glows within 2.1 metres, and how many coins are left.

   :::answer[Worked solution]{tests="collect-coin" solution="sketches/make-scripting-scene-reach.cpp"}
   The first distance is 0.4 metres, since only the depth differs: the coin is collected. The second is the square root of 4 plus 0.36, about 2.09 metres: it glows and stays. The program applies `glm::distance` to each coin.

   ```cpp sketch="make-scripting-scene-reach.cpp"
   #include <glm/glm.hpp>

   #include <cstdio>
   #include <vector>

   int main()
   {
   	const std::vector<glm::vec3> coins = { { -4.0f, 0.8f, 0.0f }, { -2.0f, 0.8f, 2.0f }, { 0.0f, 0.8f, 3.0f }, { 2.0f, 0.8f, 2.0f }, { 4.0f, 0.8f, 0.0f } };
   	const glm::vec3 ball(0.0f, 0.8f, 2.6f);
   	int left = 0;
   	for (const glm::vec3& coin : coins)
   	{
   		const float distance = glm::distance(coin, ball);
   		const bool collected = distance < 0.7f;
   		std::printf("coin at x=%.1f: distance %.2f, glows %d, collected %d\n", coin.x, distance, distance < 2.1f ? 1 : 0, collected ? 1 : 0);
   		if (!collected)
   			left++;
   	}
   	std::printf("coins left: %d\n", left);
   }
   ```

   ```text output-of="make-scripting-scene-reach.cpp"
   coin at x=-4.0: distance 4.77, glows 0, collected 0
   coin at x=-2.0: distance 2.09, glows 1, collected 0
   coin at x=0.0: distance 0.40, glows 1, collected 1
   coin at x=2.0: distance 2.09, glows 1, collected 0
   coin at x=4.0: distance 4.77, glows 0, collected 0
   coins left: 4
   ```

   1. **Line 13:** the distance between the coin and the ball, as in the Coin script.
   2. **Line 14:** collected means closer than 0.7 metres.
   3. **Line 15:** prints the distance and both results for each coin.
   4. **Line 17:** counts the coins that stay.
   :::

## Where it lives in Strata

- `StrataScriptCore/Include/StrataScript/Entity.h`: `Entity`, `Component` and `TransformComponent`.
- `StrataScriptCore/Include/StrataScript/Scene.h`: `Scene`, `Assets` and `SubScene`.
- `StrataScriptCore/Include/StrataScript/Script.h`: the :term[base class]{id=base-class}, `GetEntity` and the :term[callbacks]{id=callback}.
- `Strata/src/Strata/Scene/Scene.cpp`: `Scene::FindEntityByName` and `Scene::FindEntitiesByTag`.
- `Strata/src/Strata/Scripting/ScriptSystem.h`: the scene's asset requests of scripts.

## Further reading

- The [complete script API](../reference/script-api.md): every class, call and argument of the SDK (all levels).
- The Strata manual's chapter on scripting: the lifecycle, builds and hot reload (beginner).
