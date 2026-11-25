---
id: make/large-worlds
title: "Large worlds"
description: "Turn a small level into a streamed world of cells, make the ball its streaming source, cook it, and teleport across it without falling through missing ground."
kind: tutorial
size: L
tracks: [G]
needs: [make/levels-saves]
time: 90
learn:
  - id: explain-streaming
    text: explain why a large level streams in cells around a source and what stays in the persistent scene
  - id: build-world
    text: build a world with layers, fill its cells with prefabs and read the cell of an entity
  - id: stream-player
    text: set a streaming source on the player, watch the cell map, cook the world and export it
  - id: teleport-safely
    text: write a script that prefetches the cells before a teleport and waits for the ground
  - id: world-limits
    text: name what a world cannot do and the distance from the origin it stays within
since: 0.4.0
status: final
---

## What you will make

You turn Coin Run's small level into a world that streams: ground and props load in squares around the ball and unload behind it. Then you teleport the ball to a far island without letting it fall into a gap.

::figure{id=result}

## Why a level streams

A small level loads whole: every entity, mesh and texture sits in memory, and the game starts only after all of it has loaded. That works for a room. It fails for an island a kilometer wide, because the memory it needs grows with the area and the wait before the first frame grows too. The player sees only a small part at any moment, so the rest need not be loaded.

A **world** is a level that is too big to hold in memory at once. Strata cuts it into square pieces and loads only the ones near the player. A **cell** is one such square of ground with the entities inside it, saved as a scene file of its own. The cells around the player load as the ball rolls toward them and unload as it rolls away.

Some things must never unload. The player, the camera, the sun, the sky and the score display belong to the whole game, not to one place. They live in the **persistent scene**, an ordinary scene that stays loaded for the whole run and holds the world's settings.

Cells come in layers. A **layer** is a grid of cells of one size with its own streaming distance, such as Terrain, Buildings, Props and Gameplay. A rock is small and few players need it from far away, so Props can load late and near. Ground is large and shows from far away, so Terrain loads early and far. One cell size for everything would make the ground pop in or the rocks waste memory.

What decides which cells load? A **streaming source** is an entity that cells stream around: the cells of each layer within the source's distance load, and the others unload. Usually the source is the player.

The diagram shows the idea. The persistent scene sits outside the grid. The source sits on the ground and each layer reaches its own distance.

```mermaid caption="The persistent scene never unloads. Around the streaming source, the Terrain layer loads cells out to a long distance and the Props layer only out to a short one." alt="A box for the persistent scene, holding the player, camera and sun, points to a streaming source. The source points to two rings of cells: a wide ring for Terrain and a narrow ring for Props. Cells outside the rings are marked unloaded."
flowchart LR
  P["Persistent scene: player, camera, sun, UI"] --> S["Streaming source on the player"]
  S -->|"long distance"| T["Terrain cells loaded"]
  S -->|"short distance"| R["Props cells loaded"]
  S -.->|"too far"| U["Other cells unloaded"]
```

Here is a worked example with the numbers this page uses. Each cell is 64 m wide and the Terrain layer streams four cells away, which is 256 m. A ground tile whose nearest corner is 814 m from the ball is far outside that distance, so it stays unloaded. Roll toward it and it loads once its corner comes within 256 m.

The same distance explains a trap. If you teleport the ball 814 m in one step, nothing near the target has loaded, so the ground may not be there when the ball arrives. Then the ball falls. A **prefetch** is a request that makes the cells around a place load before something goes there. You write one in the section on teleporting.

:::why
Strata splits a world into files of its own instead of one big file because a file that is not loaded costs nothing. The price is that every entity must belong to exactly one cell or to the persistent scene, and you choose which. Most mistakes with worlds are an entity in the wrong place.
:::

## What you need

- A project from the Basic 3D template, such as a new one or your Coin Run project, with the four parts below. Make them before you start, or take them from Checkpoint 1 at the end of [Make the world](#make-the-world). Its project holds the four parts and the empty world of that section, and its editor commands make both in a new Basic 3D project of your own. A :term[loading scene]{id=loading-scene} of [Levels and saves](levels-saves.md) is welcome at the export but not needed, and no download holds one.
- The player :term[prefab]{id=prefab-make} `Prefabs/Ball.stprefab`: a sphere with a **Rigid Body** and a **Sphere Collider**, as in [Physics](physics.md). Coin Run's ball with its **Move** action and rolling script does as well. Save it as a prefab as in [Prefabs](prefabs.md).
- Three prop prefabs in `Prefabs`: `Pine`, `Rock` and `Stump`. Import `tree_pineDefaultA.glb`, `rock_largeA.glb` and `stump_round.glb` from `<release folder>/Samples/OpenWorld/Assets/Models/Nature/` into a `Models` folder, place each one, rename it and save it as a prefab. They come from Kenney's Nature Kit, which is in the public domain (:term[CC0]{id=cc0}); the Open World sample's `CREDITS.md` names it.
- The `Teleport` script: copy the file `Teleport.cpp` from the first stage's checkpoint into `Scripts`, or type it from the section on teleporting. It reads the :term[input action]{id=input-action} `Gameplay/Teleport`: add that action, a Button with no key yet, to a `Gameplay` map.
- A computer that runs the editor and about an hour and a half. No world exists yet.

## Make the world

You start with the empty world and look at what Strata made for you.

:::::steps

1. Open the Content Browser, open the `Worlds` folder, and create a world named `Meadow`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **New ▸ World** in the Content Browser. Rename the new asset `Meadow`.
   :::
   :::tab[With a command]

   ```json
   { "command": "world.create", "parameters": { "path": "Worlds/Meadow" } }
   ```

   :::
   ::::

   **You should see:** a `Meadow` World asset and a `Meadow` scene beside it. The editor opens the scene. A `World` entity in the Hierarchy carries the component that names the world.

   **If you do not see it:** the editor asks about changes you have not written when your last scene has some. Save them, or answer that you discard them, and create the world again.

2. Select the `Meadow` World asset and read its layers in the Asset panel.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Click the asset in the Content Browser. The Asset panel lists the layers.
   :::
   :::tab[With a command]

   ```json
   { "command": "world.info", "parameters": { "world": "Worlds/Meadow.stworld" } }
   ```

   :::
   ::::

   **You should see:** four layers: Terrain, Buildings, Props and Gameplay. Each has 64 m cells and streams four cells away, which is 256 m. Only Terrain loads before a game starts.

   **If you do not see it:** you selected the scene and not the World asset. Select the asset with the world's icon.

   **Why:** a layer that loads before the start makes the game wait for its cells, so the ground is there when the ball drops. Props can stream in later without harm.

3. Remove two things the template put in the scene: the `Main Camera` and the `Ground`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select `Main Camera` in the Hierarchy and press **Delete**. Do the same for `Ground`.
   :::
   :::tab[With a command]

   ```json
   { "command": "entity.delete", "parameters": { "entities": ["<id of Main Camera>", "<id of Ground>"] } }
   ```

   :::
   ::::

   **You should see:** the Hierarchy keeps `World`, `Sun`, `Sky` and `Post Process`.

   **If you do not see it:** use `entity.find` with the name to learn an id.

   **Why:** a new world's persistent scene is filled from the Basic 3D template. The game draws with the first primary camera in Hierarchy order, so the template's camera, fixed in its place, would hide a camera that follows the ball. Its 20 m `Ground` also lies at height 0, and two surfaces at one height flicker where they overlap the tiles you lay next.

:::::

::checkpoint{stage=1}

::figure{id=world-created}

## Fill the cells

A new entity goes into a cell only if you say so first. This section lays the ground and the props, and shows where each entity went.

If you start this section, or any later one, from a downloaded checkpoint, open the scene `Worlds/Meadow` first: the editor opens a project's :term[start scene]{id=start-scene}, which is not the world. The command is `{ "command": "scene.open", "parameters": { "scene": "Worlds/Meadow.stscene" } }`, and each stage's command file starts with it.

:::::steps

1. Choose the layer your next entities belong to: Terrain.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Find the strip at the top of the Hierarchy. The strip names the world, counts its loaded cells and its cells with changes not yet written, and holds the **Edit layer** list. Open the **Edit layer** list and choose `Terrain`.
   :::
   :::tab[With a command]

   ```json
   { "command": "world.edit", "parameters": { "editLayer": "Terrain" } }
   ```

   :::
   ::::

   **You should see:** `Terrain` in the list.

   **If you do not see it:** no strip means the open scene is no world's persistent scene. Open `Meadow`.

   **Why:** the default is `Persistent`, which keeps a new top-level entity in the persistent scene. That is right for cameras and managers, and wrong for ground: it would never unload. Choose the layer before you create, because the entity goes into the cell under its position when it is made.

2. Lay four ground tiles around the origin, each 64 m wide.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Create a cube named `Tile`. Set its **Position** to 32, -0.5, 32 and its **Scale** to 64, 1, 64. Add a **Box Collider** with half extents 0.5, 0.5, 0.5. Duplicate it three times with positions -32, -0.5, 32 and 32, -0.5, -32 and -32, -0.5, -32.
   :::
   :::tab[With a command]

   Run it four times, with the translations 32, -0.5, 32 and -32, -0.5, 32 and 32, -0.5, -32 and -32, -0.5, -32.

   ```json
   { "command": "entity.create", "parameters": { "name": "Tile", "components": { "MeshRenderer": { "Mesh": "Builtin/Cube" }, "BoxCollider": { "HalfExtents": [0.5, 0.5, 0.5] }, "Transform": { "Translation": [32, -0.5, 32], "Scale": [64, 1, 64] } } } }
   ```

   :::
   ::::

   **You should see:** a square of ground, 128 m on a side, with its top at height 0. The strip may still read 0 cells loaded: it counts the cells streamed in from their files, and a new cell has no file until you save.

   **If you do not see it:** a tile with no :term[collider]{id=collider} looks right but the ball falls through it. Check each tile for the collider.

   **Why:** a cell covers the square from its number times 64 m to the next. A tile centered at 32 m, 32 m lies in cell (0, 0). The tile at -32 m, 32 m lies in cell (-1, 0), the one at 32 m, -32 m in cell (0, -1) and the one at -32 m, -32 m in cell (-1, -1). Each tile gets a cell file of its own.

3. Read the cell of a tile in the Inspector.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select a tile and look at the top of the Inspector.
   :::
   :::tab[With a command]

   The command counts the world's cells by state. Before the first save it reads 4 cells with changes not yet written (`dirty`) and 0 loaded, and its list of cells is empty. No command tells an entity's cell; the Inspector does.

   With commands you read the cells instead. A tile's cell follows from its position, as the last step says under Why. Once the cells have files, after the save of the next section, this command lists each cell by `layer`, `x` and `z`. The four tiles then stand as Terrain (0, 0), (-1, 0), (0, -1) and (-1, -1).

   ```json
   { "command": "world.status", "parameters": { "cells": true } }
   ```

   :::
   ::::

   **You should see:** a line such as "Cell: Terrain (0, 0)". The tile at -32, -32 reads "Cell: Terrain (-1, -1)".

   **If you do not see it:** "Persistent scene" means you made the tile with the edit layer on Persistent. Delete it, choose `Terrain` and create it again.

4. Switch the edit layer to `Props` and place the three prefabs on the ground.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose `Props` in the **Edit layer** list. Drag `Pine`, `Rock` and `Stump` from the Content Browser into the Scene view, onto the tiles. You learned to drop with the ghost in [Prefabs](prefabs.md).
   :::
   :::tab[With a command]

   ```json
   { "command": "prefab.instantiate", "parameters": { "prefab": "Prefabs/Pine.stprefab", "instances": [ { "components": { "Transform": { "Translation": [10, 0, -20] } } } ] } }
   ```

   :::
   ::::

   **You should see:** each instance reads "Cell: Props" with its coordinates. A prop with children (a tree has a trunk and a crown) puts the whole tree into one cell.

   **If you do not see it:** children belong to the cell of their top-level parent, never to the cell under their own position. Select the root of the tree, not a branch, when you read the cell.

5. Push the `Rock` over a cell border.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Place the `Rock` at x 60, then drag it to x 70 with the move :term[gizmo]{id=gizmo-start}, and read its cell again.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<id of Rock>", "component": "Transform", "values": { "Translation": [70, 0, -20] } } }
   ```

   The answer tells no cell. After the save of the next section, `world.status` with `cells` lists the Props cell (1, -1), which holds the Rock at x 70, beside (0, -1) of the Pine and (-1, 0) of the Stump.
   :::
   ::::

   **You should see:** the cell changes from (0, -1) to (1, -1) in the same step. **Ctrl+Z** puts the rock back in its old cell in one undo.

   **If you do not see it:** a moved entity stays in its own layer. A `Rock` that you made while the edit layer was Terrain stays a Terrain entity wherever you drag it.

6. Search the Hierarchy by layer.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Type `l:Props` in the Hierarchy's search field.
   :::
   :::tab[With a command]

   ```json
   { "command": "entity.find", "parameters": { "name": "Rock" } }
   ```

   :::
   ::::

   **You should see:** only the entities of the Props layer's cells. `l:persistent` shows the persistent scene's, and `cell:1,-1` one cell's.

   **If you do not see it:** the search matches entities in loaded cells only. Fly nearer to the cells, or load them in the next section.

:::::

::checkpoint{stage=2}

::figure{id=cells-filled}

## See the cells stream

Now watch the editor load and unload cells as you fly. A world you cannot see is a world you debug blind.

:::::steps

1. Enable the cell outlines in the viewport.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Click the **Cells** chip above the Scene view.
   :::
   :::tab[With a command]

   ```json
   { "command": "viewport.setSettings", "parameters": { "cellBounds": true } }
   ```

   :::
   ::::

   **You should see:** outlines of the cells around the camera, colored by state: loading, loaded and unloading.

   **If you do not see it:** the chip draws nothing in a scene that is no world.

2. Open the cell map.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **View ▸ Streaming**, or click the map button in the Hierarchy's strip. Open the section **World**.
   :::
   :::tab[With a command]

   ```json
   { "command": "world.status", "parameters": {} }
   ```

   :::
   ::::

   **You should see:** every cell of the world as a square. Cells with edits not yet written have an outline, and the streaming source's radius is a circle. Drag to pan, scroll to zoom and double-click to frame the sources.

   **If you do not see it:** the panel shows nothing for a world with no cells yet; make sure you did the last section.

3. Save, so that the new cells have files.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Ctrl+S**.
   :::
   :::tab[With a command]

   ```json
   { "command": "scene.save", "parameters": {} }
   { "command": "world.status", "parameters": { "cells": true } }
   ```

   The second command now counts 0 cells `dirty` and 7 `loaded`. Its `list` names the seven cells: Terrain (0, 0), (-1, -1), (0, -1) and (-1, 0), and Props (0, -1), (-1, 0) and (1, -1).
   :::
   ::::

   **You should see:** the strip no longer counts cells with changes not yet written. Strata writes the files of the persistent scene, the edited cells, new cells and the World asset's cell list, and no others. A cell you did not touch keeps its file as it was. A new cell joins the world's cell list only now.

   **If you do not see it:** a cell still counted is being written; wait a moment.

4. Pin a far cell, then fly away and back.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Right-click a cell in the map and choose **Load and pin**. Fly the editor camera 400 m away, and return.
   :::
   :::tab[With a command]

   ```json
   { "command": "world.loadCells", "parameters": { "cells": [ { "layer": "Terrain", "x": 0, "z": 0 } ], "wait": true } }
   ```

   The answer gives the cell's `state`, `Loaded`, and `entities`, the number of entities that loading its file created. A cell you made in this session has stayed loaded since, with the entities you made, so it reads 0 though it holds a tile. Open the scene again, with `scene.open` as above, and the same command reads 1: now the tile came from the file. `world.status` with `cells` counts the same way: 1 for each Terrain cell, and 3 for each Props cell, one prop with the entities of its model.
   :::
   ::::

   **You should see:** the pinned cell has a pin and stays loaded wherever the camera goes. A cell you did not pin unloads as you leave and loads again as you return. **Unpin** lets the cell go.

   **If you do not see it:** the cells you changed stay loaded until you write them, so an edited cell never unloads under you. That is on purpose. If the command answers that the world has no such cell, the cell has no file yet: save first.

:::::

::checkpoint{stage=3}

::figure{id=cell-map}

## Make the ball the streaming source

Until now the editor camera made the cells stream. In the game the camera is no good as the center, because a camera can look far from the player. You give the streaming job to the ball.

:::::steps

1. Choose Persistent as the edit layer, and place the player prefab.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Open the **Edit layer** list and choose `Persistent`. Drag `Ball` into the Scene view at position 0, 1, 0.
   :::
   :::tab[With a command]

   ```json
   { "command": "world.edit", "parameters": { "editLayer": "Persistent" } }
   ```

   :::
   ::::

   **You should see:** the ball reads "Persistent scene" in the Inspector.

   **If you do not see it:** "Cell: Props" means the edit layer was still `Props`. Delete the ball and choose again.

   **Why:** a body unloads with the cell it loaded with. A ball in a cell would vanish when the ball rolled out of that cell's range, and the game would lose its player. Everything that roams, such as the player, a vehicle or a flock, belongs in the persistent scene.

2. Add a **Streaming Source** component to the ball.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select the ball. Choose **Add Component** in the Inspector, and pick **Streaming Source**. Leave the fields as they are: **Radius** 0, **Layers** empty, **Priority** 0.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.add", "parameters": { "entity": "<id of Ball>", "component": "StreamingSource" } }
   ```

   :::
   ::::

   **You should see:** the component with its fields. A **Radius** of 0 means each layer's own streaming distance. A **Layers** list that is empty means every enabled layer. A higher **Priority** loads a source's cells first when several sources compete.

   **If you do not see it:** with no source, the primary camera streams. That is the fallback, and it hides the mistake until the camera looks elsewhere.

3. Play, and watch the map follow the ball.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Play**, roll the ball, and keep the Streaming panel open.
   :::
   :::tab[With a command]

   ```json
   { "command": "play.start", "parameters": {} }
   ```

   :::
   ::::

   **You should see:** the source's circle sits on the ball and cells near it load. Stop with **Play** again.

   **If you do not see it:** Play starts from the cells the editor has loaded around its camera; the others load from their saved files around the ball. Save first.

   **Why:** an exported game starts differently. It loads the cells around the sources saved in the persistent scene before any script runs. A player that a script creates or moves at the start, for example to a position from a :term[save file]{id=save-file}, has no cells under it yet. Such a script needs a prefetch, as the next section shows.

:::::

::checkpoint{stage=4}

::figure{id=player-source}

## Cook the world

Cooking measures the world so that the physics world has room for every body of the place with the most of them.

:::::steps

1. Cook from the Asset panel.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select the `Meadow` World asset and click **Cook**.
   :::
   :::tab[With a command]

   ```json
   { "command": "world.cook", "parameters": { "world": "Worlds/Meadow.stworld" } }
   ```

   :::
   ::::

   **You should see:** under the button, a line that reads "Cooked N cells (M read again): at most B bodies in reach, a capacity of C recommended". Above it, the panel keeps the last cook in a line of its own: "Cooked: N cells measured, at most B bodies within any source's reach, a physics capacity of C recommended". Here N counts the cells that have content, M the cells measured again, B the most bodies one source can reach, and C is B with room to spare. The command returns only the numbers, as `cells`, `cellsRead`, `maxBodiesInRadius` and `recommendedMaxBodies`.

   **If you do not see it:** the button is disabled while the game plays. Stop first.

   **Why:** a physics world that grows while a game plays costs time in the frames it grows. With the capacity set at the start, it never grows. An export cooks every world for you; cooking by hand lets you read the numbers and warnings.

2. Read the warnings.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Look under the **Cook** button for warnings.
   :::
   :::tab[With a command]
   Read the `warnings` list in the result of `world.cook` from the last step.
   :::
   ::::

   **You should see:** no warnings. Strata warns when a cell lies more than 20 km from the origin and when a cell is empty. Two cells that share an entity number make the cook fail and write nothing, and the message names them.

   **If you do not see it:** a warning about an empty cell means you made a cell and removed what it held. Delete the file's cell or fill it.

   **Why:** the reservation counts only the enabled streaming sources saved in the persistent scene, at least one, with the largest radius per layer. A source your game creates later is not counted. Save the player's source in the persistent scene, as you did.

:::::

::checkpoint{stage=5}

::figure{id=cooked}

## Teleport without falling

Now the trap from the start of the page. A far island needs a ground tile and a marker, and the ball needs a script.

:::question
What do `->` and `std::optional` mean in the code below? The arrow reads a member through a pointer ([Pointers and memory](../basics/cpp-memory.md)), and `std::optional` holds a value that may be absent ([Modern C++](../basics/cpp-modern.md)).
:::

The Open World sample solves the same problem for its explorer. Its code starts the request, in a function that you can read as the first half of the job. Look at the last two statements of `BeginTeleport`: the request is kept in a member, so it can be released later.

```cpp src="Samples/OpenWorld/Scripts/Explorer.cpp#L209-L221"
void BeginTeleport(int32_t landmark)
{
	Entity marker = Scene::FindEntityByName("Teleport" + std::to_string(landmark));
	if (!marker.IsValid())
		return;
	m_Target = marker.GetTransform().GetWorldPosition();
	m_TargetYaw = glm::degrees(std::atan2(-marker.GetTransform().GetForward().x, -marker.GetTransform().GetForward().z));
	m_TargetName = "Teleport" + std::to_string(landmark);
	m_Request = World::RequestCellsAround(m_Target, 48.0f);
	m_Teleporting = true;
	m_Fade = 0.0f;
	Log::Info("OpenWorld: teleporting to landmark ", landmark);
}
```

1. **Line 214:** the destination is read from a marker entity that lives in the persistent scene.
2. **Line 217:** the request asks for every cell within 48 m of it, on every enabled layer.

The second half runs every frame while the screen fades. The explorer waits until `IsLoadedAround` is true, then waits for a ray from 300 m above the target to hit ground, then moves, and last releases the request. Read the order of those four steps.

```cpp src="Samples/OpenWorld/Scripts/Explorer.cpp#L223-L247"
void UpdateTeleport(float deltaTime)
{
	m_Fade = std::min(1.0f, m_Fade + deltaTime * 4.0f);
	SetFade(m_Fade);
	if (m_Fade < 1.0f)
		return;
	// The cells around the destination and the ground under it (the terrain is in the persistent scene, its colliders
	// are there from the first step) before the explorer arrives.
	if (!World::IsLoadedAround(m_Target, 48.0f))
		return;
	const std::optional<RaycastHit> ground = Physics::Raycast(m_Target + glm::vec3(0.0f, 300.0f, 0.0f), c_Down, 900.0f, m_TerrainMask);
	if (!ground)
		return;
	if (Walking)
		GetEntity().GetCharacterController().Teleport(ground->Point + glm::vec3(0.0f, 0.05f, 0.0f));
	else
		GetTransform().SetWorldPosition(ground->Point + glm::vec3(0.0f, 3.0f, 0.0f));
	Yaw = m_TargetYaw;
	ApplyLook();
	m_Request.Release();
	m_Teleporting = false;
	SetFade(0.0f);
	TeleportsDone++;
	Log::Info("OpenWorld: arrived at ", m_TargetName);
}
```

1. **Line 231:** the first wait: the cells around the destination are loaded.
2. **Line 233:** the second wait: a ray from 300 m above finds ground. The sample's terrain is in the persistent scene, so its ground is there at once.
3. **Lines 236-239:** the move: a character controller while walking, a transform while flying.
4. **Line 242:** the request is released after the move.

The sample moves a character controller. Your ball is a dynamic body, which `RigidBody::Teleport` moves, as [Physics](physics.md) shows, because a transform you write reaches the body only at the next :term[fixed step]{id=fixed-step}. `Teleport` keeps the velocities, so the ball would arrive rolling as fast as it left. The script sets both velocities to zero after it.

```cpp src="book:tutorials/make/large-worlds/Teleport.cpp#L32-L45"
void Arrive()
{
	if (!World::IsLoadedAround(m_Target, ReachRadius))
		return;
	const std::optional<RaycastHit> ground = Physics::Raycast(m_Target + glm::vec3(0.0f, 100.0f, 0.0f), glm::vec3(0.0f, -1.0f, 0.0f), 200.0f);
	if (!ground)
		return;
	RigidBody body = GetEntity().GetRigidBody();
	body.Teleport(ground->Point + glm::vec3(0.0f, 1.0f, 0.0f));
	body.SetLinearVelocity(glm::vec3(0.0f));
	body.SetAngularVelocity(glm::vec3(0.0f));
	m_Request.Release();
	m_Waiting = false;
}
```

1. **Line 34:** `IsLoadedAround` says the cells within the radius are in. The ground may not collide yet.
2. **Line 36:** the ray starts 100 m above the marker and goes 200 m down. A hit proves collision exists there.
3. **Lines 40-43:** the teleport, the two velocities set to zero, and the request released so the cells can unload later.

:::::steps

1. Build the island: a tile and a rock far away, and a marker.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Set the edit layer to `Terrain` and create a `Tile` at 608, -0.5, 608 with scale 64, 1, 64 and a **Box Collider**, as before. Set the edit layer to `Props` and place a `Rock` at 608, 0, 600. Set it to `Persistent` and create an empty entity named `FarMarker` at 608, 0, 608.
   :::
   :::tab[With a command]

   ```json
   { "command": "world.edit", "parameters": { "editLayer": "Terrain" } }
   { "command": "entity.create", "parameters": { "name": "Tile", "components": { "MeshRenderer": { "Mesh": "Builtin/Cube" }, "BoxCollider": { "HalfExtents": [0.5, 0.5, 0.5] }, "Transform": { "Translation": [608, -0.5, 608], "Scale": [64, 1, 64] } } } }
   { "command": "world.edit", "parameters": { "editLayer": "Props" } }
   { "command": "prefab.instantiate", "parameters": { "prefab": "Prefabs/Rock.stprefab", "instances": [ { "components": { "Transform": { "Translation": [608, 0, 600] } } } ] } }
   { "command": "world.edit", "parameters": { "editLayer": "Persistent" } }
   { "command": "entity.create", "parameters": { "name": "FarMarker", "components": { "Transform": { "Translation": [608, 0, 608] } } } }
   ```

   :::
   ::::

   **You should see:** the tile in cell (9, 9) and the marker in the persistent scene. Its distance from the ball is about 860 m.

   **If you do not see it:** if the tile does not read "Cell: Terrain (9, 9)", the edit layer was wrong.

   **Why:** the marker is in the persistent scene so the script finds it while its cells are far away. Cells that are not loaded hold no entities a script could find.

2. Attach the `Teleport` script to the ball and build it.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select the ball. Choose **Add Component**, pick **Script**, choose the class `Teleport`, and build the project's scripts as in [Your first script](first-script.md).
   :::
   :::tab[With a command]

   ```json
   { "command": "script.build", "parameters": {} }
   { "command": "script.add", "parameters": { "entity": "<id of Ball>", "class": "Teleport" } }
   { "command": "script.get", "parameters": { "entity": "<id of Ball>" } }
   ```

   The last answer lists the script with its `class` and its `fields`.
   :::
   ::::

   **You should see:** the `Teleport` script on the ball, with its field `ReachRadius` at 48.

   **If you do not see it:** a class that is missing means the build failed or has not run yet. Read the build's errors in the Console.

3. Bind a key to the action `Gameplay/Teleport`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Open the project's input actions, find the action `Gameplay/Teleport` and bind a key to it, as you did for the ball's actions in [Input](input.md).
   :::
   :::tab[With a command]
   This step has no menu or button: run the command in the next step, which presses the action without a key.
   :::
   ::::

   **You should see:** the key beside the action.

   **If you do not see it:** a script that reads an action with no binding never sees it pressed.

4. Play, press the key and watch the ball cross the world.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Save with **Ctrl+S**, so that the island's cells have files. Press **Play**, open the cell map, and press your key.
   :::
   :::tab[With a command]

   ```json
   { "command": "scene.save", "parameters": {} }
   { "command": "play.start", "parameters": {} }
   { "command": "input.action", "parameters": { "action": "Gameplay/Teleport" } }
   ```

   :::
   ::::

   **You should see:** the far cells load on the map, then the ball stands on the far tile with no speed. The ball arrives after a moment, not at once.

   **If you do not see it:** nothing happens when the world has no source or the action has no key. Check the ball's **Streaming Source** and the key.

5. Take the prefetch away, to see what it guards against.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Open `Scripts/Teleport.cpp`. In `Begin`, after the line that sets `m_Target`, add two lines: `GetEntity().GetRigidBody().Teleport(m_Target + glm::vec3(0.0f, 1.0f, 0.0f));` and `return;`. Build, press **Play** and press your key again.
   :::
   :::tab[With a command]

   Make the same change to the file first: no command edits a script. Then build, play and press the action, and read where the ball is.

   ```json
   { "command": "script.build", "parameters": {} }
   { "command": "play.start", "parameters": { "paused": true, "build": false } }
   { "command": "play.step", "parameters": { "steps": 10 } }
   { "command": "input.action", "parameters": { "action": "Gameplay/Teleport" } }
   { "command": "play.step", "parameters": { "steps": 300 } }
   { "command": "component.get", "parameters": { "entity": "<id of Ball>", "component": "Transform" } }
   { "command": "play.stop", "parameters": {} }
   ```

   :::
   ::::

   **You should see:** in this world the ball still lands on the far tile, at 608, 0.5, 608, at once and without the wait. The ball is the streaming source, so the island's two cells start to load the moment it arrives, and their small files are in before the ball has fallen the half meter to the tile.

   **If you do not see it:** a ball that falls through met ground that came too late, which is the trap itself. Pinned cells play no part here: the island lies more than 700 m from every cell you pinned.

   **Why:** without the prefetch nothing waits for the ground, and the ball lands only because the cells won a race. A cell with more in it, a mesh collider that still builds its shape, or a player that is no streaming source loses that race, and then the ball falls without end. The prefetch turns the race into a wait. Remove the two lines and build again before you continue.

   A request that you never release keeps its cells loaded until you call `Release` or the scene stops. Requests and layer switches belong to the running scene, and a scene that streams no world refuses them and logs it once.

:::::

### Turn a layer off from a script

A script can switch a layer: `World::SetLayerEnabled("Props", false)` unloads its cells, and `World::IsLayerEnabled("Props")` reads the state, as an optional that is empty for a name the world lacks. You use this in the exercises. A forgotten `WorldCellRequest` keeps cells loaded, so release each one.

::checkpoint{stage=6}

::figure{id=teleport-done}

## Export the world

:::::steps

1. Make the world's persistent scene the :term[start scene]{id=start-scene} of the game.

   ::::tabs{sync=how}
   :::tab[In the editor]
   With `Worlds/Meadow` open, choose **File ▸ Set as Start Scene**.
   :::
   :::tab[With a command]

   ```json
   { "command": "project.setStartScene", "parameters": { "scene": "Worlds/Meadow.stscene" } }
   ```

   The answer's `startScene` is the handle of the scene `Meadow`.
   :::
   ::::

   **You should see:** `Meadow` in **Start Scene** on the page **Game** of **File ▸ Project Settings...**.

   **If you do not see it:** the project still starts with `Scenes/Main`, the template's scene, and its game would show no world. Open `Meadow` and choose the menu item again.

   **Why:** a game starts with its start scene, and the world streams only from its persistent scene. A loading scene of your own, from [Levels and saves](levels-saves.md), goes in **Loading Scene** on the same page: it plays while the start scene loads.

2. Export the game as in [Export](export.md).

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **File ▸ Export Game...**, press **Export**, and run the game.
   :::
   :::tab[With a command]

   ```json
   { "command": "project.export", "parameters": { "directory": "<absolute path outside the project>" } }
   ```

   :::
   ::::

   **You should see:** the ball on the ground, after your loading scene if you named one. The game waits for the Terrain cells around the saved source and for their collision before the ball drops.

   **If you do not see it:** a prop that is missing means its cell was never saved. Prefab changes reach a cell's instances when that cell loads in the editor, so load and save every cell that uses a prefab you changed before you export. This comes from reading Strata's code, not from running an export.

:::::

### What a world cannot do

A world has four limits, and each has a reason.

- Keep a world within 20 km of the origin. Positions are 32-bit numbers, precise to about 2 mm at that distance, and Strata does not move the origin to stay precise farther out.
- Cells far from the camera are not drawn at all, and there are no simplified far copies. Match fog and the camera's far plane to the streaming distances.
- Strata has no terrain system. The ground of the samples is made of meshes that tools write.
- A moving body cannot pass from one cell to another, because it unloads with the cell it loaded with.

For a last look, open the Open World sample's island: its terrain lives in the persistent scene, and its explorer prefetches the cells before each teleport.

::checkpoint{stage=7}

::figure{id=exported}

## Summary

- A large level streams in square cells around a source, while the persistent scene keeps the player, camera and sun loaded.
- You made a world, laid ground and props into the cells of two layers and read each entity's cell.
- You made the ball the streaming source, watched the cell map, cooked the world and exported it.
- You wrote a teleport that requests the cells, waits for them and for the ground, then moves the ball and releases the request.
- You named the limits: 20 km, no far drawing, no terrain system and no body that crosses cells.

## Check yourself

1. Why does the ball belong in the persistent scene?

   :::answer{tests="explain-streaming"}
   A body unloads with the cell it loaded with, so a ball in a cell would vanish when that cell unloaded. The persistent scene never unloads.
   :::

2. You create a rock while the edit layer is Terrain, and drag it to another cell. Which layer does it stay in?

   :::answer{tests="build-world"}
   Terrain. A moved entity changes cell within its own layer; only a new top-level entity takes the edit layer.
   :::

3. Why does the teleport wait for a :term[raycast]{id=raycast} hit after `IsLoadedAround` is true?

   :::answer{tests="teleport-safely"}
   `IsLoadedAround` says the cells are loaded. A mesh collider may still wait for its shape, so a hit is the proof of collision.
   :::

4. The exported game starts with the player moved by a script to a saved position 2 km away. What do you add?

   :::answer{tests="stream-player"}
   A prefetch. The game loads the start cells around the sources saved in the persistent scene, not around a position a script chooses later.
   :::

5. A friend builds a 100 km map. What goes wrong?

   :::answer{tests="world-limits"}
   Positions lose precision beyond 20 km and Strata does not move the origin, so the map jitters.
   :::

## Exercises

1. **Basic.** Set the ball's streaming **Radius** to 1000 and play. Read the cell map, or `world.status`, and say what changed.

   :::answer{tests="stream-player"}
   Nine cells load instead of seven: the island's Terrain and Props cells too. A **Radius** above 0 replaces every layer's own distance, here 1000 m instead of 256 m, and the island's nearest corner is 814 m from the ball. A **Radius** of 0 means each layer's own distance. A small one, such as 100, changes nothing in this world: all seven cells near the ball lie within 64 m of it.
   :::

2. **Medium.** Add a key that switches the `Props` layer off and on from a script, and show the cell map follow.

   :::answer[Worked solution]{tests="teleport-safely" solution="tutorials/make/large-worlds/exercise-1.tutorial.json"}
   The script reads `World::IsLayerEnabled("Props")` and calls `SetLayerEnabled` with the opposite value on a key press. Cells of Props unload while it is off, and load again from their files, over some frames, when it is back on.
   :::

3. **Hard.** Move a plain scene, with no world, 50 km from the origin. Does it shake? Why does 50 km still draw, and what loses precision there?

   :::answer{tests="world-limits"}
   The scene draws without shaking, because the :term[renderer]{id=renderer} subtracts the camera position before it converts to 32-bit numbers. At 50 km the gap between two neighboring 32-bit numbers is 4 mm: 2 to the power 15, divided by 2 to the power 23, in meters. Positions in scenes and physics then move in 4 mm steps. The limit concerns that precision, not the renderer. This comes from the design of the renderer, not from a measurement.
   :::

## Where it lives in Strata

The world code is in `Strata/src/Strata/World/`, and the script calls are in `StrataScriptCore/Include/StrataScript/World.h`. The editor's side, the cell map and the cook are under `StrataEditor/src/`.

## Further reading

- The engine's `Docs/Manual/Worlds.md`: the guide to worlds for makers (beginner).
- The engine's `Docs/Architecture.md`, section World partition: how the streamer works (advanced).
