---
id: worlds/why-streaming
title: "Why levels must stream"
description: "Why a big level cannot stay in memory, how engines load only what is near the player, and what limits the size of a Strata world."
kind: concept
size: M
tracks: [E]
needs: [world/sub-scenes, assets/residency, basics/numbers]
time: 40
learn:
  - id: cost
    text: explain what a loaded level costs in memory and in work every frame, and compute why a large level cannot stay loaded
  - id: approaches
    text: compare loading the whole level, level switches, hand-placed streaming volumes and a grid of cells by cost, quality and effort
  - id: anatomy
    text: name the parts of a Strata world, the persistent scene, the layers and the cells, and say why Strata streams by a grid
  - id: precision
    text: compute the gap between neighbouring float values at a distance and explain why Strata supports worlds within 20 km of the origin
  - id: limits
    text: name what Strata cannot do for a distant cell, with no simplified far version and no origin rebasing, and what to match to the streaming distances
since: 0.4.0
status: final
---

Open the Open World sample in the editor and walk across its island. The island is a map of 640 m by 640 m, and the editor's **Streaming** panel draws it as a grid of squares. Each square is a piece of the level, and the colored ones are in memory. As you walk, squares ahead of you appear and squares behind you disappear, so the game holds a window of the island and never the whole of it.

::figure{id=cell-map-island}

This page asks why a game works this way. The answer starts with the price of a loaded level, goes through the ways engines pay it, and ends with two limits that Strata's choice cannot escape.

## A loaded level costs memory and work

A **level** here means everything the player can meet in one place: entities with their components, and the assets those entities name. The assets are meshes, textures, materials, sounds and clips. Loading a level pays three prices, and the level keeps paying them until you release it.

The first price is main memory, the random access memory (RAM) of the processor: entities, scene data and decoded assets live there. The second is the memory of the :term[graphics card]{id=gpu}, where textures and meshes must sit before the card draws them. The third is the work of every frame. Each loaded entity may be tested for visibility, moved, updated by a script or simulated by physics, so the frame grows with the number of loaded entities and not with the number you can see.

The Open World sample shows real numbers. The Island world file stores an index with the size of every cell, and its cells add up to 20,158 entities. The stored :term[bytes]{id=byte} of what loading each cell needs add up to about 45.8 MB. Two cells that share a texture each count its bytes, so the true total is lower, and the sum is an upper bound. A real game has more of everything: the island is only 0.41 km².

Creating entities costs time too. Suppose creating one entity takes 2 microseconds, an assumption for the sum and no measurement. Then 20,158 entities take about 40 ms, and a frame at 60 :term[frames per second]{id=frame-rate} lasts 16.7 ms. The picture would freeze for two and a half frames. [Loading scenes: whole, additive and in slices](../world/sub-scenes.md) teaches how Strata spreads that work over many frames, and [Residency](../assets/residency.md) teaches why what is loaded stays in memory until someone releases it.

## Loading the whole level breaks as the level grows

The naive answer is to load the whole level before play and keep it. For a small game this is right: a puzzle game with one screen has nothing to stream. The answer breaks in two ways when the level grows.

First, memory. Suppose the map reached the limit that Strata supports, 20 km in each direction from the origin. That is a square 40 km on a side, an area of 1,600 km², and the island covers 0.41 km². The map holds about 3,900 islands.

At the island's density that is about 79 million entities and about 179 GB of cell data, far more than the memory of any machine. The density is an assumption for the calculation: no real map is so uniform, but even a tenth of it does not fit.

Second, time. A level that holds everything needs everything read from disk before the first frame, so the wait grows with the size of the level, although the player sees only the part around them.

The two failures have one cause: the cost depends on the size of the level and not on what the player can reach. Streaming changes the cost to depend on the player's surroundings.

## A world is a persistent scene plus cells that stream

The idea in one paragraph: split the level into pieces, keep in memory only the pieces near the player, and load and release pieces as the player moves. Strata names the parts. A **world** is a level split into cells that stream in and out while the game runs.

The **persistent scene** is the scene of a world that never unloads: it holds the player, the sky, the managers and the `WorldComponent` that names the world. In the Open World sample it also holds the island's ground tiles and its water, so the ground never unloads.

A layer is one grid of cells with one cell size and one streaming distance, and a world has up to 32 of them. A **cell** is a square of that grid with content in it, and it lives in a scene file of its own. The streaming sources, such as the player, decide which cells load around them.

```mermaid caption="A world is one persistent scene plus a World asset that lists layers and cells, and each cell is a scene file that loads and unloads on its own." alt="A diagram in four boxes joined by arrows. The persistent scene, which holds a world component, points to the World asset. The World asset points to its layers and its cooked index. Each layer points to its cells, and each cell points to a cell scene file on disk."
flowchart TB
    P["Persistent scene<br/>player, sky, WorldComponent"] --> W["World asset (.stworld)"]
    W --> L["Layers: Vegetation, Wildlife, Landmarks"]
    W --> I["Cooked index<br/>entities, bytes, bodies per cell"]
    L --> C["Cells: squares with content"]
    C --> F["Cell scene files<br/>Worlds/Island/Vegetation/X_Z.stscene"]
```

The diagram shows where each piece lives. The persistent scene is always in memory and points to the World asset. The World asset is a document that lists the layers, the cells and the index. The cells' content is in many small scene files, and only the files of the nearby cells are read.

The island has three layers of 64 m cells. Vegetation streams within 192 m of the player, Wildlife within 128 m and Landmarks within 320 m. Its 97 cells divide as 81, 10 and 6. A layer with far larger reach and few cells keeps distant landmarks in view, while the many small vegetation cells load only near the player.

## Engines hold levels in four ways

Each way below is a response to the flaw of the one before.

**The whole level** loads at start and stays. Its flaw is the one above: the cost grows with the level.

**Level switches behind a loading screen** cut the game into separate levels. The game unloads one, shows a loading screen and loads the next. Memory is bounded by the largest level, but the player meets a pause at every door, and a place cannot be seen from the level beside it.

**Hand-placed streaming volumes** cut one big level into scenes and let designers place trigger boxes that load and unload them. The player no longer waits. The cost moves to the designers: every box must be placed, and a wrong box shows empty ground or loads too much.

**Automatic grid partitioning** lets the engine cut the world into cells by position and decide by distance which load. No one places a box, and the cells follow the content. The cost is a heavier tool chain: the engine needs an index of the cells and a streamer that decides.

| Approach | Cost | Quality | Complexity | Used by |
| --- | --- | --- | --- | --- |
| Whole level | Memory and load time grow with the level | Perfect while small | Lowest | Small games, one-screen games |
| Level switches | Memory bounded by the largest level; a pause at each switch | A visible break between levels | Low | Many linear games |
| Streaming volumes | Memory bounded by what the volumes hold | Seamless where the volumes are right | Designer work for every volume | Unity additive scenes, Unreal level streaming |
| Grid partitioning | Memory bounded by the streaming distances | Seamless everywhere | An index and a streamer | Unreal World Partition, Strata worlds |

:::elsewhere[Unity and Unreal]
Unity loads scenes additively, beside the open one, and teams write their own code to decide when. Unreal Engine offers level streaming volumes and, in version 5, World Partition, which divides a level into a grid of cells that stream by distance. Both are described in their manuals, listed in Further reading.
:::

:::example[What the player at spawn keeps in memory]
The Open World's player starts at x = 120 m, z = 256 m. A cell loads when the distance from the player to the cell's square is within its layer's streaming distance. For Vegetation that distance is 192 m, so cells whose squares come within 192 m of the player load. Counting in the cooked index gives 22 Vegetation cells, 4 Wildlife cells and 4 Landmarks cells, 30 of the 97.

Those 30 cells hold 5,701 of the 20,158 entities, 28 %, and about 15.2 MB of the 45.8 MB, 33 %. At the island's western corner, at x = -300 m and z = -300 m, only 10 cells load, with 2.7 MB. The cost follows the player. Walk to the middle and it grows, walk to the shore and it shrinks, and a 20 km map would cost the same near any player.
:::

## Strata keeps all three ways and streams by a grid

Strata offers every way to hold a level. A game can switch scenes: `GameRuntime::LoadScene` replaces the running scene once the new one is loaded. A scene can load another scene into itself as a :term[sub-scene]{id=sub-scene}, which is how a streaming volume placed by hand would work. And a world is a uniform grid per layer, whose cells stream around sources. The Open World project also names a loading scene, `Scenes/Loading.stscene` with `Scripts/LoadingScreen.cpp`, which the :term[runtime]{id=runtime} plays and which shows progress while the start scene loads.

The world's decisions come from a cooked index. The command `world.cook` measures every cell once, and the index stores its entities, its bytes, its bounds and its bodies. The streamer then decides which cells to load from the index, without opening a cell. For the island the index also records `MaxBodiesInRadius`, 9161: the most physics bodies that any source can keep loaded at once. [The grid](../worlds/grids.md) teaches the arithmetic of cells, and [The streamer](../worlds/streamer.md) teaches how sources decide.

:::why[Why a uniform grid and not hand-placed volumes?]
A streamer that reads an index decides cheaply: it compares distances and never opens a file. It decides in a fixed order, so the same positions give the same loads at any speed of disk, and a test can check it. And no designer places a volume, so a new tree in a new corner joins the cell that holds it. The cost is that a cell is a square. A hand-placed volume can follow a valley, and a grid cannot.
:::

The choice has a price beyond squares. A grid must be cooked again when content moves, and a stale index misleads the streamer, so Strata keeps a stamp per cell and reports stale cells. [Editing a streamed world](../editor/worlds.md) teaches how the editor shows it.

## Floating point sets a limit on the size of a world

Every position in a scene is a 32-bit :term[floating point]{id=floating-point-number} number, a float. [Numbers in a computer](../basics/numbers.md) taught that a float keeps 24 significant bits and that the gap between neighbouring floats grows with the size of the number. Here is that fact worked for the gap, with a number between $2^{14}$ and $2^{15}$.

A float in $[2^{14}, 2^{15})$ is a whole multiple of one fixed gap, because 24 bits cover that range with 23 bits after the leading one. For a number with leading power $2^{e}$ the step is

$$s = 2^{e-23}$$

where $s$ is the gap to the next float, in metres, and $e$ is the :term[exponent]{id=exponent}, the power of two at or below the number. Take a distance of 20,000 m. The power of two at or below it is $2^{14} = 16{,}384$, so $e = 14$ and $s = 2^{-9}$ m, which is 0.00195 m, about 2 mm. At 16,383 m the power is $2^{13}$, so the step is $2^{-10}$ m, about 1 mm. At 32,768 m, which is $2^{15}$, the step doubles to $2^{-8}$ m, about 4 mm.

A position far from the origin can only land on these steps. An object at 20 km moves in jumps of about 2 mm, and at 100 km, where $e = 16$, in jumps of $2^{-7}$ m, about 8 mm. Slow movement then shows as jitter, and the vertices of a model, which are added to a position, shake against each other. The chart shows the steps from 1 km to 100 km.

::figure{id=spacing-chart}

The line is flat inside each range of powers of two and jumps at the powers. The dashed line at 20 km marks the limit Strata supports, and the dot on it shows that the gap there is still about 2 mm. A map of 100 km has steps four times as large.

Engines answer in three ways. They can shift the world so that the player stays near zero (origin rebasing). They can store positions in double precision, and they can draw relative to the camera. [Camera-relative rendering and the other answers to distance](../draw/mirrors-camera-relative.md) compares them. What belongs to the world is Strata's choice: scenes and physics stay in float, drawing is camera-relative, and a world is supported within 20 km of the origin.

That limit is the constant `WorldData::c_SupportedExtent` in `Strata/src/Strata/World/WorldAsset.h`, 20,000 m in both X and Z. Two guards hold the engine to it. The tests of the World.Coordinates suite put a world 20 km out, and its cells stream, its bodies rest on the ground and its bodies are hit by rays. The cook of a world warns about each cell that lies beyond 20 km, and names how far it lies. The document format is looser: it accepts cells to 1,000 km, so the cook's warning is the limit's signal.

## What Strata's choice cannot do

Streaming changes what the player sees as well as what is in memory. A cell that is not loaded is not drawn. Strata has no **HLOD** (hierarchical level of detail), a simplified stand-in for a whole far cell, as many engines draw for distant areas. Beyond the loaded cells there is only the persistent scene, the sky and what the persistent scene holds. The island's ground tiles and water lie in its persistent scene, so past the last loaded cell the player sees bare ground: no trees, no animals and no landmarks.

Two numbers must then agree. The streaming distance of a layer decides how far its content reaches, and the camera's :term[far plane]{id=far-plane} decides how far anything is drawn. The island's camera has a far plane at 1,500 m, while its largest layer reaches 320 m, so the camera can look past the end of the loaded world. A game that wants no visible edge hides it, for example with fog that grows thick before the streaming distance and a far plane that stops near it.

Strata does not do three things. It does not support worlds beyond 20 km from the origin, because cells farther out lose precision. It has no hierarchical level of detail (HLOD), so far cells are absent and not simplified. And it has no origin rebasing, so the player does not return to zero when they walk far. The release notes list all three as later work, and [What Strata does not do](../appendix/not-in-strata.md) keeps the list.

## Common mistakes

- **Thinking that streaming means textures only.** The symptom is a plan that streams the textures of a big level and keeps all entities loaded, then runs out of memory in the entity data or the :term[frame time]{id=frame-time}. Strata streams whole entities with their assets, cell by cell. Texture streaming exists too, as [Residency](../assets/residency.md) teaches, but it does not shrink the level.
- **Building a map far beyond 20 km.** The symptom is shaking bodies and meshes at the far edge, and a cook warning that names the cell. The fix is to keep the world inside the extent, or to split the game into several worlds that each stay within it.
- **Matching nothing to the streaming distances.** The symptom is a visible edge: trees and landmarks that end in a ring around the player, with bare ground beyond, and pop in as the player walks. The fix is fog and a far plane that agree with the layers' distances.

## Summary

- A loaded level costs memory and frame work for every entity, so a 40 km map at the island's density would need about 179 GB.
- A whole level, level switches, streaming volumes and a grid of cells trade cost, quality and effort differently, and Strata has the scene switch, the sub-scene and the world.
- A world is a persistent scene plus layers of cells, each cell a scene file, and Strata streams by a grid because an index makes its decisions cheap and needs no placed volumes.
- The gap between float values is $2^{e-23}$ m, about 2 mm at 20 km and 8 mm at 100 km, so Strata supports worlds within 20 km.
- Strata draws no far version of an unloaded cell and does no origin rebasing, so match fog and the far plane to the streaming distances.

## Check yourself

1. A teammate says: "Streaming only means loading textures as the camera nears." Which statement is right?
   - A. Right: only textures are big enough to stream.
   - B. Wrong: Strata streams whole cells of entities and their assets.
   - C. Right: entities are cheap, so they stay loaded.
   - D. Wrong: Strata streams only sounds.

   :::answer{tests="cost"}
   B. A is wrong because entities cost memory and frame work too, and the island's 20,158 entities are mostly in its Vegetation cells. C is the same mistake: entities cost work every frame. D names a content type that nothing in the world code singles out.
   :::

2. At spawn the island loads 30 of its 97 cells, and its cells add up to 45.8 MB. About how much of the 45.8 MB is loaded?
   - A. All of it.
   - B. About one third.
   - C. About one tenth.

   :::answer{tests="cost"}
   B. The 30 cells at spawn hold about 15.2 MB, which is 33 % of 45.8 MB. A is what the whole-level approach loads. C is too low, because Vegetation cells are heavy and 22 of them load.
   :::

3. Which approach needs a designer to place a box for each region?
   - A. Level switches.
   - B. Hand-placed streaming volumes.
   - C. Grid partitioning.

   :::answer{tests="approaches"}
   B. A switch needs a loading screen and no box. A grid cuts the world by position and needs no placed volume.
   :::

4. A float is between 32,768 and 65,535. What is the gap to the next float, in mm?
   - A. About 2.
   - B. About 4.
   - C. About 8.

   :::answer{tests="precision"}
   B. The leading power is $2^{15}$, so $e = 15$ and the gap is $2^{-8}$ m, 3.9 mm. A is the gap from 16,384 to 32,767, and C is the gap above 65,536.
   :::

5. You build a game map 60 km across and place its centre at the origin. What does the cook do?
   - A. Nothing: the extent counts only the world's width.
   - B. It warns about each cell farther than 20 km from the origin.
   - C. It refuses to cook.

   :::answer{tests="precision,limits"}
   B. Every cell beyond 20 km in X or in Z gets a warning that names its distance. A is wrong because the extent is a distance from the origin. C is wrong because the document accepts cells to 1,000 km.
   :::

6. A world has a persistent scene, layers and cells. Which part never unloads?
   - A. Every cell.
   - B. The persistent scene.
   - C. The layer with the largest streaming distance.

   :::answer{tests="anatomy"}
   B. It holds the player, the sky and the world component. A is wrong because cells load and unload by distance. C is wrong because a layer is only a grid, and its cells still unload.
   :::

## Exercises

1. **Basic.** Run a sketch that prints the gap between a float and its next neighbour at 1 km, at 20 km and at 100 km. Use it to find where the gap doubles between 16 km and 33 km.

   :::answer[Worked solution]{tests="precision"}
   :::question
   New to calls such as `std::nextafter(`, loops and arrays? Read [Programming 2](../basics/programming-2.md) and [Programming 3](../basics/programming-3.md) first.
   :::

   The function `std::nextafter` returns the float after its first argument in the direction of its second, and subtracting the number gives the gap. The sketch lists seven distances, and its loop prints each gap in mm. Compare the gap between the fifth and the sixth line.

   ```cpp sketch="worlds-why-streaming-spacing.cpp"
   // The gap between a float and the next float above it, at several distances from the origin.
   #include <cmath>
   #include <iostream>

   int main()
   {
   	const float distances[] = { 1000.0f, 16383.0f, 16384.0f, 20000.0f, 32767.0f, 32768.0f, 100000.0f };
   	for (const float distance : distances)
   	{
   		const float next = std::nextafter(distance, 1.0e9f);
   		std::cout << distance << " m: gap " << (next - distance) * 1000.0f << " mm\n";
   	}
   	return 0;
   }
   ```

   ```text output-of="worlds-why-streaming-spacing.cpp"
   1000 m: gap 0.0610352 mm
   16383 m: gap 0.976562 mm
   16384 m: gap 1.95312 mm
   20000 m: gap 1.95312 mm
   32767 m: gap 1.95312 mm
   32768 m: gap 3.90625 mm
   100000 m: gap 7.8125 mm
   ```

   1. **Line 7:** the distances to test. They include both sides of the powers of two $2^{14}$ and $2^{15}$.
   2. **Line 10:** `std::nextafter` finds the next float above the distance.
   3. **Line 11:** the gap times 1,000 turns metres into mm.

   The gap is 0.061 mm at 1 km, 1.95 mm at 20 km and 7.8 mm at 100 km, which are the chart's three dots. It jumps from 1.95 mm to 3.9 mm between 32,767 m and 32,768 m, the power $2^{15}$. The supported 20 km lies below that jump.
   :::

2. **Medium.** Design origin rebasing on paper. When the player is 2,000 m from the origin, you shift every entity by the player's position. List what must move, and what must not be shifted twice.

   :::answer[Worked solution]{tests="limits"}
   Shift the persistent scene's entities, every loaded cell and every physics body by the same amount, in one frame, so no frame shows two states. A cell that loads later needs the sum of all earlier shifts, so the streamer remembers the offset. Streaming sources move with the shift, and the distance rule holds because every distance is a difference of two shifted numbers. Never shift a child entity whose parent moved: the child keeps its local position. A save file stores the offset beside the shifted positions.
   :::

3. **Hard.** Sketch HLOD for Strata on paper: where would a far version of each cell live, and how does it swap with the full cell as the player comes near?

   :::answer[Worked solution]{tests="limits"}
   Give each cell a far scene, a few merged meshes with simple materials, stored beside the cell's file and listed in the index. The streamer keeps far versions loaded in a wide ring, beyond the cell's streaming distance. When the full cell is wanted, load it first and swap the far version out only when the full cell is ready, so no gap shows. When the player leaves, unload the full cell and bring the far version back. The far version holds no bodies, so the physics capacity stays the same.
   :::

## Where it lives in Strata

- The World asset and its limits: `Strata/src/Strata/World/WorldAsset.h`, with `WorldData::c_SupportedExtent` and `WorldData::c_MaxExtent`.
- The cook and its warning for cells beyond the supported extent: `StrataEditor/src/Editor/WorldCook.cpp`, run by the command `world.cook`.
- The sample: `Samples/OpenWorld/Assets/Worlds/Island.stworld`, its player in `Samples/OpenWorld/Assets/Worlds/Island.stscene`, and `Samples/OpenWorld/Scripts/Explorer.cpp`, which loads the cells around a teleport target before the player arrives.
- Scene switches: `GameRuntime::LoadScene` in `Strata/src/Strata/Runtime/GameRuntime.h`; sub-scenes: `Scene::LoadSubScene`.
- The precision guard: the World.Coordinates test suite in `StrataTests/src/World/WorldCoordinatesTests.cpp` and `StrataTests/src/Editor/EditorWorldTests.cpp`.
- The cell map: the **Streaming** panel, its **World** section, and the button in the Hierarchy panel's strip.
- Building and editing a world: [Large worlds](../make/large-worlds.md) and [Editing a streamed world](../editor/worlds.md); how shipped games switch levels: [Level switches in a shipped game](../worlds/runtime.md).

## Further reading

- Unity manual, "Multi-scene editing" and additive scene loading (beginner): how a Unity game loads scenes beside each other. <https://docs.unity3d.com/Manual/MultiSceneEditing.html>
- Unreal Engine documentation, "World Partition" and "Level Streaming" (intermediate): the grid and the volumes Unreal offers. No link, because its host is not on the list.
- "What every programmer should know about floating-point arithmetic" (intermediate): why the gap between floats grows. No link, because its host is not on the list.
