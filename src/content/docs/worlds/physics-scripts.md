---
id: worlds/physics-scripts
title: "Worlds meet physics and scripts"
description: "How a running scene drives the world streamer, how the cook sizes physics room before cells arrive, and how scripts prefetch cells."
kind: internals
size: L
tracks: [E]
needs: [worlds/streamer, physics/scale-streaming, scripting/abi-sdk]
time: 75
learn:
  - id: explain-world-system
    text: explain how the World scene system turns components, sources and script requests into streaming each frame
  - id: compute-cook-numbers
    text: compute a cook's MaxBodiesInRadius and the recommended physics capacity from the bodies of each cell
  - id: explain-safe-start
    text: explain why an exported world starts with its ground in place, and where a script can still break that
  - id: write-prefetch
    text: write a prefetch that moves a player only after the cells and the ground at the destination are there
since: 0.7.0
status: final
---

A world is too big to hold in memory, so its cells load and unload while the game runs. Something must tell the streamer where the player is, something must make room for the physics bodies that each cell brings, and something must let a script say "I am about to go there". This page covers those three jobs: the scene's World system and its two components, the cook's numbers and the :term[prepared start]{id=prepared-start} that keep the ground solid, and the script side. It does not cover how the streamer decides which cells to load ([the streamer page](streamer.md)), how physics grows its storage ([physics at scale](../physics/scale-streaming.md)), or how an export cooks a world ([the export page](export.md)).

## The problem and how engines solve it

Picture a game that starts on a hill. The player is a capsule with a :term[rigid body]{id=rigid-body}, the hill is a mesh in a streamed cell, and the first frame runs. If the cell has not loaded, the hill does not exist, and gravity does its work. After 2 s the capsule has fallen about 19.6 m, which is half of 9.81 m/s² times the time squared.

The cell loads a moment later, with the player already far below its ground. The player is lost, and no error message appears. The page is built around this failure. Every rule below prevents it or a cousin of it.

Three facts make it hard. Cells load on background threads, so no code can know on which frame the ground arrives. Physics storage needs room before bodies arrive, because making room in the middle of a frame costs time. And a script may move a player a kilometre in one call, to a place that nothing has loaded.

Engines meet this in three ways. The first is a loading screen: the game waits for everything near the start, then begins. It is safe, but it says nothing about what happens after the start. The second is to hold the player still until the ground below reports ready, which needs a ground check on every move.

The third is to size physics from numbers measured in advance, so that a cell never has to wait for room. Strata takes the first and the third as the engine's own rule, and gives scripts the tools for the second.

The cost of the third way is a step before the game runs. Someone must measure every cell, and the measurements go stale when a cell changes. Strata keeps them current with a stored fingerprint of each cell, so a measuring run reads only the cells that changed.

## The map

Four owners take part, and one thread runs all of them.

The scene owns two components, which are plain data. The World system reads them every frame in the :term[main thread]{id=main-thread}, gathers :term[streaming sources]{id=streaming-source}, adds the requests of scripts and hands the list to the streamer. The streamer starts loads, and before each batch it asks physics for room through the capacity service. The editor's cook is a separate program step: it reads the cells on input and output jobs and writes numbers into the :term[World asset]{id=world-asset}, which the streamer reads at run time.

```mermaid caption="One game frame: scripts move sources and make requests, the world system streams, then physics and audio see the changed scene" alt="A line of boxes for one frame: scripts, then the world streaming stage, then physics and audio, then rendering. Arrows from scripts to the world stage carry moved sources and cell requests."
flowchart LR
  Scripts["Scripting: OnUpdate"] -->|"moves sources, requests cells"| World["World: World.Streaming"]
  World -->|"Reserve(bodies) before loads"| Physics["Physics step"]
  World --> Audio["Audio"]
  Physics --> Render["Rendering"]
  Cook["Editor cook"] -.->|"index with body counts"| World
```

The order is not an accident. Scripts run first, so a source that a script moved this frame already counts. Physics runs after, so the cells that loaded this frame have bodies in the step. The constraints are soft: a program without Audio still runs.

## The contract

Callers may assume the following, and the module must keep it.

- A scene without a `WorldComponent` costs the system one check of a component storage per update, and streams nothing. A scene with one streams the world of the first active `WorldComponent` in hierarchy order.
- Sources come from enabled `StreamingSourceComponent`s on entities that are active in the hierarchy. When none is active, the :term[primary camera]{id=primary-camera} streams, with the streamer's defaults.
- A source faces its -Z axis, the direction a camera looks, and the cells ahead of it rank as if they were nearer.
- The system runs in Play mode and in the editor's Simulate mode.
- Nothing in the system waits for a load. Loads advance across frames, and a script asks whether they are done.
- Requests and layer toggles belong to the running scene. When the scene stops, the cells and the requests go with it.

:::rule
The engine's guide asks that a scene which will run loads with `SceneLoadOptions::PrepareSystems`, so that the World system can load start cells before play. It also forbids a body without collision while physics can still grow. The reason is safety: a missing body is a player falling through the floor, with no error to read. See [loading scenes in slices](../world/sub-scenes.md).
:::

**Distance scale** is the number on a `WorldComponent` that multiplies every layer's :term[streaming distance]{id=streaming-distance}, from 0.1 to 10. A layer that streams within 1,024 m streams within 512 m at a scale of 0.5. It is a quality knob: a device with less memory loads less.

The scale touches only layers' own distances. A source with its own `Radius` above 0 ignores it, because the radius already says how far to stream. The system reads the scale every update, so a game may change it while it plays. No graphics preset sets it at the pin.

## A toy version

The cook's central number is the most bodies a source can ever keep loaded at once. The toy below computes it for one row of cells, which is the real calculation with one dimension removed.

A cell's body count is known. A source streams every cell within its radius, so the worst place for a source to stand is the place where the cells within reach hold the most bodies. The toy tries each cell as the centre of that place, sums the bodies of the cells within reach and keeps the largest sum.

```cpp sketch="worlds-physics-scripts-toy.cpp"
// A toy of the world cook's count: the most bodies one source can keep loaded at once, one row of cells.
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <vector>

// Cell i covers [i * cellSize, (i + 1) * cellSize] along X. A source streams the cells within `radius`.
uint64_t MostBodiesInRadius(const std::vector<uint64_t>& bodies, double cellSize, double radius)
{
	// The cook widens the radius: a source may stand anywhere in its cell, and sizes are guesses.
	const double reach = radius + std::max(cellSize * 0.5, 0.1 * radius);
	uint64_t most = 0;
	for (size_t centre = 0; centre < bodies.size(); centre++)
	{
		uint64_t sum = 0;
		for (size_t other = 0; other < bodies.size(); other++)
		{
			// The gap between two cells' edges: 0 for a cell and for its neighbours.
			const double steps = std::abs(static_cast<double>(other) - static_cast<double>(centre));
			const double gap = std::max(0.0, (steps - 1.0) * cellSize);
			if (gap <= reach)
				sum += bodies[other];
		}
		most = std::max(most, sum);
	}
	return most;
}

// 1.25 times the total, rounded up, in integers: a quarter of a number is exact in integer arithmetic.
uint64_t Recommended(uint64_t total)
{
	return total / 4 * 5 + (total % 4 * 5 + 3) / 4;
}

int main()
{
	const std::vector<uint64_t> bodies = { 10, 20, 40, 5, 0, 60 };
	const uint64_t persistent = 30;
	const uint64_t most = MostBodiesInRadius(bodies, 100.0, 100.0);
	std::printf("busiest place: %llu bodies\n", static_cast<unsigned long long>(most));
	for (uint64_t sources = 1; sources <= 2; sources++)
	{
		const uint64_t total = most * sources + persistent;
		std::printf("%llu source(s): total %llu, recommended %llu\n", static_cast<unsigned long long>(sources),
			static_cast<unsigned long long>(total), static_cast<unsigned long long>(Recommended(total)));
	}
	return 0;
}
```

```text output-of="worlds-physics-scripts-toy.cpp"
busiest place: 125 bodies
1 source(s): total 155, recommended 194
2 source(s): total 280, recommended 350
```

1. **Line 12:** the reach is wider than the radius, because a source stands anywhere in its cell.
2. **Lines 20–23:** the gap between two cells is zero for neighbours, and a cell counts when its gap is inside the reach.
3. **Line 33:** the :term[integer]{id=integer} form of 1.25 times a total, rounded up.
4. **Lines 42–44:** each number of sources scales the busiest place, and the :term[persistent scene]{id=persistent-scene} is added once.

The toy rounds up when it recommends room. A recommendation of 1.25 times the total leaves a quarter extra for bodies that a game creates itself, such as spawned crates, and that the cook cannot see.

:::example
Take six cells of 100 m with 10, 20, 40, 5, 0 and 60 bodies, a source radius of 100 m, and 30 bodies in the :term[persistent scene]{id=persistent-scene}. The reach is 100 + max(50, 10) = 150 m. Cells two steps apart have a gap of 100 m between their edges, which is inside the reach; cells three steps apart have 200 m, which is not. So each window holds the cell and up to two cells on each side.

The windows hold 70, 75, 75, 125, 105 and 65 bodies. The largest is 125, so the sources need 125 bodies for one source and 250 for two. With the persistent scene added, `MaxBodiesInRadius` is 155 and 280. Times 1.25, rounded up, the recommended capacity is 194 and 350 bodies.
:::

The toy shows the shape of the answer: a sum over a window, a maximum over windows, one factor for the sources and one for the spare. The real code does the same per layer and by squares. It also has two problems the toy lacks, a very large world with many cells, and the reading of the sources, which the sections below take in the order of data flow.

## The real code

### Components and registration

The two components are plain data with ranges, in `Strata/src/Strata/World/WorldComponents.h`. `WorldComponent` holds the :term[asset handle]{id=asset-handle} of the World asset and the `DistanceScale`. `StreamingSourceComponent` holds `Enabled`, a `Radius` from 0 to 1,000,000, a comma-separated `Layers` string, a `Priority` from -100 to 100, and a `ViewBias` from 0 to 1 with a default of 0.25. A radius of 0 means each layer's own streaming distance.

The ranges are written twice on purpose. The registration puts them into the property tables, which the inspector's widgets read. The gathering code clamps each value itself, because a script or a damaged scene file can write any number.

`Strata/src/Strata/World/WorldRegistration.cpp` registers the :term[loader]{id=loader} for World assets, the two components and the :term[scene system]{id=scene-system}. Look at how the system is declared.

```cpp src="Strata/src/Strata/World/WorldRegistration.cpp#L60-L68" from="SceneSystemDescriptor descriptor =" to="descriptor.PrepareLoadedScene = &WorldStreamingSystem::PrepareLoadedScene;" symbol="RegisterWorldModule"
SceneSystemDescriptor descriptor = MakeSceneSystemDescriptor<WorldStreamingSystem>("World", true, [](Scene& scene) { return CreateScope<WorldStreamingSystem>(scene); });
descriptor.AfterIfPresent = { "Scripting" };
descriptor.BeforeIfPresent = { "Physics", "Audio" };
descriptor.ProfileStage = "World.Streaming";
// Registered now rather than when a scene first plays, so that perf logs created before (StrataRuntime's) have its
// column.
FrameProfiler::Get().RegisterStage(descriptor.ProfileStage);
// A loaded world's start cells load while its load prepares it, before physics builds their bodies.
descriptor.PrepareLoadedScene = &WorldStreamingSystem::PrepareLoadedScene;
```

The two lists of names are the order: after "Scripting", before "Physics" and "Audio", each only when present. The profile stage World.Streaming is registered at once, so that a performance log created before the first scene plays still has its column. The last line hands the system a function that runs while a loaded scene prepares, which is the prepared start below.

### Gathering the sources

Each update, the system rebuilds the list of sources from the scene. The code below visits every enabled source and converts it into the streamer's own type.

```cpp src="Strata/src/Strata/World/WorldStreamingSystem.cpp#L101-L138" symbol="WorldStreamingSystem::GatherSources"
void WorldStreamingSystem::GatherSources(Scene& scene, const WorldStreamer& streamer, std::vector<WorldStreamingSource>& outSources, std::set<std::string>* warnedLayers)
{
	outSources.clear();
	const Ref<WorldAsset> world = streamer.GetWorldAsset();
	const WorldData* data = world ? &world->GetData() : nullptr;
	const entt::registry& registry = scene.GetRegistry();
	if (const auto* storage = registry.storage<StreamingSourceComponent>(); storage && !storage->empty())
	{
		for (const entt::entity handle : static_cast<const entt::sparse_set&>(*storage))
		{
			const StreamingSourceComponent& component = registry.get<StreamingSourceComponent>(handle);
			const Entity entity(handle, &scene);
			if (!component.Enabled || !scene.IsActiveInHierarchy(entity))
				continue;
			const glm::mat4 transform = scene.GetWorldTransform(entity);
			WorldStreamingSource source;
			source.Position = glm::vec3(transform[3]);
			source.Forward = -glm::vec3(transform[2]);
			source.Radius = std::isfinite(component.Radius) ? std::clamp(component.Radius, 0.0f, 1'000'000.0f) : 0.0f;
			source.Priority = std::clamp(component.Priority, -100, 100);
			source.ViewBias = std::isfinite(component.ViewBias) ? std::clamp(component.ViewBias, 0.0f, 1.0f) : WorldStreamer::c_DefaultViewBias;
			source.LayerMask = ParseLayerMask(data, component.Layers, warnedLayers);
			outSources.push_back(source);
		}
	}
	// Without an active source, the primary camera streams.
	if (outSources.empty())
	{
		if (const Entity camera = scene.GetPrimaryCameraEntity())
		{
			const glm::mat4 transform = scene.GetWorldTransform(camera);
			WorldStreamingSource source;
			source.Position = glm::vec3(transform[3]);
			source.Forward = -glm::vec3(transform[2]);
			outSources.push_back(source);
		}
	}
}
```

1. **Line 113:** a source counts only when it is enabled and active in the hierarchy.
2. **Lines 117–118:** the position is the fourth column of the :term[world transform]{id=world-transform}, and forward is the third column with its sign reversed.
3. **Lines 119–121:** each number is clamped to its range, and a value that is not a number falls back to a safe one.
4. **Line 122:** the layer names become a mask.
5. **Lines 127–136:** without an active source, the primary camera is the source.

A :term[world transform]{id=world-transform} is a matrix, and its columns hold the axes and the position. The fourth column is the position, and the third column with its sign reversed is the forward axis, because Strata looks along -Z.

The layer list is parsed once per update into a mask with one bit per layer of the world. A name that the world does not have is dropped, and the system warns once for each such name, so a typing mistake does not fill the log. An empty list means every layer. When no source is active, the primary camera becomes one, with the streamer's defaults.

The idle cost shows in `SyncWorld`, which every update calls. It first checks whether the scene has any `WorldComponent` at all, and only then searches for the first active one. A game without a world pays for a single storage lookup.

### Requests

The update itself is short.

```cpp src="Strata/src/Strata/World/WorldStreamingSystem.cpp#L194-L204" symbol="WorldStreamingSystem::OnUpdate"
void WorldStreamingSystem::OnUpdate(Timestep)
{
	SyncWorld();
	if (!m_Streamer)
		return;
	GatherSources(m_Scene, *m_Streamer, m_Sources, &m_WarnedLayers);
	for (const auto& [id, source] : m_Requests)
		m_Sources.push_back(source);
	m_Streamer->SetSources(m_Sources);
	m_Streamer->Update();
}
```

1. **Line 196:** the world is found again every update, so a game can change it while it plays.
2. **Lines 199–201:** the sources of the scene come first, then the held requests.
3. **Lines 202–203:** the streamer takes the list and evaluates it.

Sources from the scene come first, then every held request is appended as one more source, and the streamer receives the whole list. A request is therefore a source without an entity. Look at how it is made.

```cpp src="Strata/src/Strata/World/WorldStreamingSystem.cpp#L218-L226" from="WorldStreamingSource source;" to="m_Requests.emplace(id, source);" symbol="WorldStreamingSystem::RequestCellsAround"
WorldStreamingSource source;
source.Position = position;
source.Forward = glm::vec3(0.0f);
// A radius of 0 asks for the cells at the position (a source's 0 would mean each layer's distance).
source.Radius = std::max(radius, 0.001f);
source.Priority = c_RequestPriority;
source.ViewBias = 0.0f;
const uint64_t id = m_NextRequest++;
m_Requests.emplace(id, source);
```

A request has priority 100, the top of the range, so its cells load before the cells of every real source with a lower priority. It has no facing, so the :term[view bias]{id=view-bias-worlds} does nothing. For a real source, a radius of 0 would mean each layer's own distance. The code therefore replaces 0 with 0.001 m, so a request of radius 0 asks for the cells at the position and nothing more. The request is stored under a number that grows by one, and a script holds that number.

### Measuring: the world cook

The streamer can reserve physics room only if it knows how many bodies each cell holds, and the cell's file does not say. The **world cook** is the editor step that reads every cell, counts its entities and physics bodies, and writes the results into the World asset as its index. It is the command `world.cook`, and an export runs it for every world of the project. The editor page ([worlds in the editor](../editor/worlds.md)) shows how to run it and read its report.

The cook does not read every cell every time. It compares each cell's content stamp with the one in the index or in the session's cache. Only cells that differ are read, on input and output jobs. A stamp is a number that changes when the cell's inputs change ([importing](../assets/importing.md)).

The cook fails if two cells use the same entity identifier (ID), because a cell loads only when its IDs are new to the scene. It warns about cells beyond 20 km, where float positions lose precision, and about empty cells. When the work ends, the editor writes the index as one undo step.

One number of the index matters most here.

**MaxBodiesInRadius** is the most bodies that the persistent scene and any set of sources can keep loaded at the same time anywhere in the world, a worst case, stored in the index. The cook counts sources and radii from the persistent scene as it was saved: every enabled `StreamingSourceComponent` counts, and there is at least one. Each layer streams within the largest radius of those sources; a source with radius 0 contributes the layer's own distance times the world's distance scale. The sources' layer masks are ignored.

The number is conservative in one way and silent in another. Every source is assumed to stream every layer, which can only count too much. But a source that a game spawns, a source inside a cell, and a request from a script have no room in it. A game that adds such sources makes physics grow while cells load.

```cpp src="StrataEditor/src/Editor/WorldCook.cpp#L348-L389" from="const double radius = std::max(layerRadii[layerIndex], 0.0);" to="most = std::max(most, sum);" symbol="WorldCook::ComputeMaxBodiesInRadius"
const double radius = std::max(layerRadii[layerIndex], 0.0);
const double reach = radius + std::max(static_cast<double>(layer.CellSize) * 0.5, 0.1 * radius);
std::vector<const WorldCellSummary*> layerCells;
for (const WorldCellSummary& cell : cells)
{
	if (cell.Layer == layer.ID)
		layerCells.push_back(&cell);
}
const int64_t span = static_cast<int64_t>(std::ceil(reach / static_cast<double>(layer.CellSize))) + 1;
const bool scanGrid = static_cast<double>(2 * span + 1) * static_cast<double>(2 * span + 1) < static_cast<double>(layerCells.size());
uint64_t most = 0;
for (const WorldCellSummary* cell : layerCells)
{
	const WorldCellSquare square = WorldGrid::CellBounds(layer, data.GridOrigin, cell->X, cell->Z);
	uint64_t sum = 0;
	auto add = [&](int32_t x, int32_t z, uint64_t count)
	{
		if (SquareDistance(square, WorldGrid::CellBounds(layer, data.GridOrigin, x, z)) <= reach)
			sum += count;
	};
	if (scanGrid)
	{
		for (int64_t dx = -span; dx <= span; dx++)
		{
			for (int64_t dz = -span; dz <= span; dz++)
			{
				const int64_t x = cell->X + dx;
				const int64_t z = cell->Z + dz;
				if (std::abs(x) > WorldCellKey::c_MaxCoordinate || std::abs(z) > WorldCellKey::c_MaxCoordinate)
					continue;
				const auto it = bodies.find(WorldCellKey { layer.ID, static_cast<int32_t>(x), static_cast<int32_t>(z) }.Pack());
				if (it != bodies.end())
					add(static_cast<int32_t>(x), static_cast<int32_t>(z), it->second);
			}
		}
	}
	else
	{
		for (const WorldCellSummary* other : layerCells)
			add(other->X, other->Z, other->Bodies);
	}
	most = std::max(most, sum);
```

1. **Line 349:** the reach is the radius, widened by half a cell or a tenth of the radius, whichever is more.
2. **Lines 356–357:** the span counts cells in one direction, and the grid is scanned only when its square is smaller than the layer's list.
3. **Lines 368–383:** the grid scan finds each neighbour in a map of body counts.
4. **Lines 384–388:** the list walk adds every cell of the layer that is within reach.
5. **Line 389:** the busiest place of the layer is the largest sum over all cells.

The toy's loop is here with two changes. The reach is a distance between squares, not a count of steps. The code also chooses between two ways to find the neighbours of a cell.

When the square of cells around a cell is smaller than the layer's list of cells, it scans the grid around it with a map lookup. Otherwise it walks the list. Both give the same sum, and the choice keeps a world with a million empty grid positions from costing a million steps per cell. After the loop, each layer adds its best sum, and the function returns the total times the number of sources, plus the persistent scene's bodies.

The index then recommends room.

```cpp src="Strata/src/Strata/World/WorldAsset.cpp#L507-L511" symbol="WorldIndex::GetRecommendedMaxBodies"
uint32_t WorldIndex::GetRecommendedMaxBodies() const
{
	const uint64_t withSpawns = MaxBodiesInRadius / 4 * 5 + (MaxBodiesInRadius % 4 * 5 + 3) / 4;
	return static_cast<uint32_t>(std::min<uint64_t>(withSpawns, PhysicsCapacitySettings::c_MaxBodiesLimit));
}
```

The line `total / 4 * 5 + (total % 4 * 5 + 3) / 4` is 1.25 times the total rounded up, written so that no number overflows: :term[floating point]{id=floating-point-number} could lose a body at large totals, and multiplying first could overflow 64 bits at the extreme. The result is capped at the physics growth limit, so a recommendation never asks for more than physics will give.

### Reserving before loads

When the streamer is about to start loads, it sums what the physics world will need and asks for it.

```cpp src="Strata/src/Strata/World/WorldStreamer.cpp#L585-L598" from="uint64_t bodies = data.Index->PersistentBodies;" to="capacity->Reserve(static_cast<uint32_t>(std::min<uint64_t>(bodies, std::numeric_limits<uint32_t>::max())));" symbol="WorldStreamer::ReserveBodies"
uint64_t bodies = data.Index->PersistentBodies;
for (const auto& [key, record] : m_Cells)
{
	if (record.Status == WorldCellStatus::Failed)
		continue;
	if (const WorldCellSummary* summary = world.FindSummary(WorldCellKey::Unpack(key)))
		bodies += summary->Bodies;
}
for (const Candidate& candidate : starting)
{
	if (const WorldCellSummary* summary = world.FindSummary(WorldCellKey::Unpack(candidate.Key)))
		bodies += summary->Bodies;
}
capacity->Reserve(static_cast<uint32_t>(std::min<uint64_t>(bodies, std::numeric_limits<uint32_t>::max())));
```

1. **Line 585:** the persistent scene's bodies start the sum.
2. **Lines 586–592:** cells that hold bodies add theirs, and a failed cell adds nothing.
3. **Lines 593–597:** cells about to start add theirs before their loads begin.
4. **Line 598:** the sum, capped to 32 bits, is the request for room.

The sum is the persistent scene, plus every cell that still holds bodies (failed cells hold none), plus every cell about to start. Without an index the function returns at once and nothing is reserved: a world that was never cooked works, but physics grows while cells load. The reservation is a request for room, not a guarantee: [physics at scale](../physics/scale-streaming.md) explains growth, and what happens at the growth limit.

### The prepared start

The reservation protects the world while it runs. The prepared start protects its first frame. **`LoadBeforeStart`** is a flag of a world layer that says its cells around the sources must be loaded, with their collision, before the game's first frame. A layer of ground has it set; a layer of far decoration usually does not.

A game loads its start scene through a loading scene that keeps playing. The World module hooks into that load. Each frame of the load, within the frame's budget, the hook loads the start cells and returns false until they are done. Then physics' own hook builds their bodies in slices, and the :term[renderer]{id=renderer} builds its proxies. The scene swaps in only after all of that, so frame one has ground.

```cpp src="Strata/src/Strata/World/WorldStreamingSystem.cpp#L311-L330" from="if (!prepared->LayersChosen)" to="scene.UpdateSubScenes(budget);" symbol="WorldStreamingSystem::PrepareLoadedScene"
if (!prepared->LayersChosen)
{
	for (const WorldLayer& layer : asset->GetData().Layers)
	{
		if (!layer.LoadBeforeStart)
			streamer.SetLayerEnabled(layer.Name, false);
	}
	prepared->LayersChosen = true;
	// A game never starts with less physics room than its world's cook found it needs: the world physics' hook
	// creates next is sized for it (exports save it into the packed persistent scene too; packs built otherwise may
	// lack it).
	if (const std::optional<WorldIndex>& index = asset->GetData().Index)
	{
		PhysicsCapacitySettings& capacity = scene.GetSettings().PhysicsCapacity;
		capacity.MaxBodies = std::max(capacity.MaxBodies, index->GetRecommendedMaxBodies());
	}
	streamer.Update();
}
// A slice of the cells' entities within the frame's budget (their loads advance with the asset manager).
scene.UpdateSubScenes(budget);
```

1. **Lines 313–317:** only the layers marked `LoadBeforeStart` stay enabled for the start.
2. **Lines 319–326:** the physics capacity rises to the index's recommendation when the scene's own setting is lower.
3. **Line 330:** the cells' entities are created in slices that fit the frame's budget.

The state of the preparation lives on the scene, so the hook can return false on one frame and resume on the next. The first time through, it switches off every layer that is not `LoadBeforeStart`, so only the start layers load. It also raises the physics capacity to the index's recommendation if the scene's own setting is lower, so that the physics world the next hook creates starts with the right room. When the cells are done, the preparation drops its streamer but keeps the cells, and the system that starts with the scene adopts them in `OnRuntimeStart`.

The start cells are loaded around the sources as the persistent scene was saved, or around its primary camera, before any script runs. That has a consequence the page must state plainly. A player that a script spawns, or moves in `OnCreate` to a position restored from a save file, starts in a place for which nobody waited. The prepared start protects the start the scene was saved with, and nothing else. A game that restores a position from a save, or moves the player in `OnCreate`, uses the script tools below.

Play in the editor behaves differently and waits for no start cells. The play copy begins with the cells the editor holds near its camera, and the rest stream from their saved files. Cells with edits that are not yet saved stay loaded: the editor's play copy calls `PinCell` on the system for them, and [worlds in the editor](../editor/worlds.md) covers it. Tools and tests that start a scene without preparing it use `WaitForStartCells`, which blocks until a timeout and is meant only for them.

### The script side

Scripts reach the streamer through the :term[scene service]{id=scene-service} `IWorldStreaming`, which has a function for each action: `RequestCellsAround`, `ReleaseCells`, `IsLoadedAround`, `SetLayerEnabled`, `IsLayerEnabled`, `GetStats` and `IsStreaming`. The software development kit (:term[SDK]{id=sdk}) of the scripts wraps five of them, in `StrataScriptCore/Include/StrataScript/World.h`: four in a class `World`, and the release in a small value `WorldCellRequest`. A `WorldCellRequest` holds a plain number, 0 when the engine refused the request.

The host functions are `WorldRequestCellsAround`, `WorldReleaseCells`, `WorldIsLoadedAround`, `WorldSetLayerEnabled` and `WorldIsLayerEnabled`, in `Strata/src/Strata/Scripting/ScriptHostAPI.cpp`. Each follows the host function conventions ([the host function page](../scripting/host-api.md)). A scene that streams no world gets the misuse reported once, and a failure value comes back. A position that is not finite, or a negative radius, is refused with a report. An unknown layer name is a failure for `SetLayerEnabled`, but only an answer for `IsLayerEnabled`: it returns "no value", as collision layers do.

The Open World sample prefetches before a :term[teleport]{id=teleport}. Its script asks for the cells around the landmark when the player chooses it, fades the screen, and moves only when the cells are in and a ray hits the ground.

```cpp src="Samples/OpenWorld/Scripts/Explorer.cpp#L223-L247" symbol="Explorer::UpdateTeleport"
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

1. **Lines 231–232:** wait until the cells around the destination are loaded.
2. **Lines 233–235:** a ray from 300 m above the destination must hit the terrain, which is the test of collision.
3. **Lines 236–239:** only then the explorer moves, onto the ground or a little above it.
4. **Line 242:** the request is released so that the cells can go.

The order is the lesson. The request was made earlier, in `BeginTeleport`, so loading runs while the screen fades. `IsLoadedAround` says the cells are in. The raycast then finds the ground height and is the real test of collision: a hit means a body exists there. Only then does the script move the player and call `Release`, which lets the cells go once no source wants them.

What `IsLoadedAround` promises needs care, and the page states how it was checked. It reports that every existing cell of every enabled layer within the radius is loaded, which means its entities exist. The comment in the script :term[header]{id=header} says more: that the ground there has collision. For a mesh collider, the physics code says otherwise: the body stays pending until its mesh data is in and its shape is cooked on a job.

So a cell whose ground is a mesh collider may count as loaded before it collides. This was read in the code at the pin and not run. A raycast hit is the safe test, and the sample uses one. Its island ground is in the persistent scene, so its :term[colliders]{id=collider} are there from the first step.

A request lasts until it is released. Only `Release`, or the scene stopping, lets its cells go. A script that ends, or an object that is destroyed, releases nothing, because the request is a plain number and the engine holds the request. A forgotten request keeps its cells loaded for the rest of the session. Layer toggles belong to the scene too: after `Game::LoadScene` or `ReloadScene`, every layer starts again from its `EnabledByDefault`.

The feature test has a small world of its own for these calls, `StrataTests/FeatureTest/Assets/Worlds/FeatureWorld.stworld`. It has a Ground layer of 32 m cells and a Props layer of 16 m cells, each in a 2 by 2 grid. Its script, `StrataTests/FeatureTest/Scripts/WorldFeatures.cpp`, requests a corner and moves the source away. It then turns Props off and on, releases the request, and checks at each phase what is loaded.

:::why
Strata makes a request a source and not a call that blocks. A blocking call would stall the frame for as long as a cell reads from disk, which the engine's rules forbid. A source costs nothing until the next update and uses the streamer's loading order, its budget and its unloading again, so a request has no code of its own to go wrong.
:::

### Rules for scripts and a limit

When a cell unloads, its entities are destroyed in slices, and each entity's `OnDestroy` runs. A script that holds an entity handle from a cell must expect that handle to go. References between cells resolve only while both are loaded. An object that roams, such as a player, a vehicle or a herd, belongs in the persistent scene, which never unloads.

There is a limit the pin does not lift: bodies do not move from one cell to another. A moving body unloads with the cell it was loaded with. A crate that rolls out of its cell is not moved into the next one, and disappears with its first cell. The remedy is the persistent scene. The release notes of 0.7.0 list it as a known issue.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Loading screen before every teleport | Many console games | No ground check by scripts | A wait for every move, even to a loaded place |
| Measure cells at run time instead of cooking | Small tools and prototypes | No stale index, no cook step | Room unknown before loads, so physics grows mid-frame |
| Blocking prefetch call | Some scripting systems | One line instead of a loop | A frame that stalls on disk |
| Per-cell body hand-over | Engines with entity streaming | Moving bodies could cross cells | Bodies in two places, with owners that disagree |
| A fixed physics size chosen by hand | Simple engines | No cook | Wasted memory, or a failure when the number is low |

## How it is tested

The suite World.Streaming, in `StrataTests/src/World/WorldStreamingTests.cpp`, checks the following. The system streams around the primary camera when no source exists. Requests load far regions first, layers toggle, and unknown names warn once. A scene without a world streams nothing. A world loaded to run starts with its `LoadBeforeStart` cells in place and their bodies built.

The suite `Scripting.World` in `StrataTests/src/Scripting/WorldScriptingTests.cpp` runs the five host functions from a script. It also checks that a scene without a world fails each of them, reported once.

The suite `Editor.WorldCook` in `StrataTests/src/Editor/WorldCookTests.cpp` compares the cook's index with an independent count, and its `MaxBodiesInRadius` with a complete evaluation. It checks that a second cook reads only changed cells, and that shared entity IDs fail the cook. It also checks that an export cooks stale worlds and starts with the cooked capacity. Run a suite with `StrataTests --test-suite=World.Streaming`. The feature test, run through `ctest`, fails when no scene uses a world feature.

## Changing it safely

- To add a field to a component, add it in `WorldComponents.h` and register it in `WorldRegistration.cpp` with a range. Clamp it where the system reads it. Extend the feature test, which fails for a property that no scene sets to a non-default value.
- To add a source of cell demand, make it a source in the list the system builds. Never load a cell from a script call directly: the streamer owns the order and the budget.
- To change what the cook counts, change the cook and the reservation together, and extend `Editor.WorldCook`. A number that is too low lets physics grow in the middle of a frame, and one that is too high wastes memory in every game.
- To add a host function, append it at the end of the host table and of the host function list. Let the SDK check for it, and call it from the script module that tests the host functions, a `Scripting.*` test and the feature scripts.
- Keep the system's order. A World system that runs before Scripting sees last frame's sources, and one that runs after Physics gives the step cells it has not seen.

:::rule
The engine's guide says that code which works for a scene reaches assets through `Scene::GetAssetManager()` and that nothing waits for a load. The World system follows both: `WaitForStartCells` is the one blocking form, named for tools and tests, and a game never calls it. See [the streamer](streamer.md).
:::

## Summary

- The World system reads two plain components every frame, gathers sources with -Z as forward, adds script requests at priority 100 and hands them to the streamer, after scripts and before physics.
- The cook measures every cell, finds the most bodies the persistent scene and any sources can keep loaded, and recommends 1.25 times that, rounded up, for physics room.
- The prepared start loads the `LoadBeforeStart` cells around the saved sources and raises the capacity before the first frame, so an exported world has ground from frame one.
- A prefetch requests cells, waits for `IsLoadedAround`, uses a raycast as the test of collision, moves and releases the request.

## Check yourself

1. A world layer streams within 1,024 m. The world component has a distance scale of 0.5. A source has `Radius` 300 and another has `Radius` 0. Within what distance does each stream that layer?

   - A. 512 m and 512 m.
   - B. 300 m and 512 m.
   - C. 150 m and 512 m.
   - D. 300 m and 1,024 m.

   :::answer{tests="explain-world-system"}
   B. The scale multiplies only a layer's own distance, which a source with radius 0 uses: 1,024 × 0.5 = 512 m. A source with its own radius ignores the scale, so 300 m. A and C apply the scale to the radius; D forgets it on the second source.
   :::

2. With the toy's cells, a busiest place of 125 and 30 persistent bodies, a game has three sources. What capacity does the index recommend?

   :::answer{tests="compute-cook-numbers"}
   The total is 125 × 3 + 30 = 405. Divide by 4 and keep the remainder: 405 = 101 × 4 + 1. So the result is 101 × 5 + (1 × 5 + 3) / 4 = 505 + 2 = 507, which is 506.25 rounded up.
   :::

3. A script spawns the player in `OnCreate` at a place far from the saved sources. Why can the player fall, although the world has a `LoadBeforeStart` layer of ground?

   - A. The prepared start ran after `OnCreate`, so the cells arrived late.
   - B. The prepared start loaded the cells around the saved sources, before any script ran, and nobody waited for cells at the new place.
   - C. A `LoadBeforeStart` layer is ignored when a script exists.

   :::answer{tests="explain-safe-start"}
   B. The preparation uses the sources as the persistent scene was saved. A is wrong in order: the preparation runs first. C is false: the flag always applies, to the saved sources.
   :::

4. `World::IsLoadedAround` returns true for a destination. What may you still not assume, and what is the test?

   :::answer{tests="write-prefetch"}
   You may not assume that the ground collides: a mesh collider's body can still be pending. A raycast that hits the ground is the test of collision.
   :::

5. A script makes a request and its object is destroyed before it calls `Release`. What happens to the cells?

   :::answer{tests="write-prefetch explain-world-system"}
   The cells stay loaded. The request is a plain number that the engine holds, and only `Release` or the scene stopping removes it.
   :::

## Exercises

1. **Basic.** Run the toy's calculation by hand with a source radius of 200 m, the same cells and 30 persistent bodies. What does the index recommend for one source?

   :::answer[Worked solution]{tests="compute-cook-numbers"}
   The reach is 200 + max(50, 20) = 250 m, so cells up to three steps away count (a gap of 200 m). The windows hold 75, 75, 135, 135, 125 and 105 bodies, so the busiest place has 135. The total is 135 + 30 = 165, and the recommendation is 165 / 4 = 41, 41 × 5 = 205, plus (1 × 5 + 3) / 4 = 2, which gives 207.
   :::

2. **Medium.** Write a sketch that sums what the streamer reserves. The persistent scene has 30 bodies. Held cells are A with 40, B with 5 and a failed D with 20, and starting cells are C with 60 and E with 10.

   :::answer[Worked solution]{tests="compute-cook-numbers" solution="sketches/worlds-physics-scripts-reserve.cpp"}
   The sum starts at the persistent scene, skips failed cells and adds the cells about to start.

   ```cpp sketch="worlds-physics-scripts-reserve.cpp"
   // What the streamer reserves before it starts loads: the persistent scene, held cells and the cells about to start.
   #include <cstdint>
   #include <cstdio>
   #include <vector>

   struct Cell
   {
   	const char* Name = "";
   	uint64_t Bodies = 0;
   	bool Failed = false;
   };

   int main()
   {
   	const uint64_t persistent = 30;
   	const std::vector<Cell> held = { { "A", 40, false }, { "B", 5, false }, { "D", 20, true } };
   	const std::vector<Cell> starting = { { "C", 60, false }, { "E", 10, false } };
   	uint64_t bodies = persistent;
   	for (const Cell& cell : held)
   		if (!cell.Failed) // a failed cell holds no bodies
   			bodies += cell.Bodies;
   	for (const Cell& cell : starting)
   		bodies += cell.Bodies;
   	std::printf("reserve %llu bodies\n", static_cast<unsigned long long>(bodies));
   	return 0;
   }
   ```

   ```text output-of="worlds-physics-scripts-reserve.cpp"
   reserve 145 bodies
   ```

   1. **Lines 16–17:** held and starting cells as data, with D a failed held cell.
   2. **Lines 19–21:** failed cells hold no bodies, so the sum skips them.
   3. **Lines 22–23:** every starting cell counts, before its load begins.
   :::

3. **Hard.** Trace it yourself: find where the cook takes the radii and the number of sources from the persistent scene.

   :::answer[Worked solution]{tests="explain-world-system"}
   The function is `ReadPersistent` in `StrataEditor/src/Editor/WorldCook.cpp`, which `WorldCook::Finish` uses. Put a breakpoint in `WorldCook::ComputeMaxBodiesInRadius` while `world.cook` runs, and read `layerRadii` and `sourceCount`.
   :::

4. **Hard.** Write the prefetch of a teleport as :term[pseudocode]{id=pseudocode}: it requests the cells, waits, finds the ground, moves and releases.

   :::answer[Worked solution]{tests="write-prefetch"}
   The script moves only when the cells are in and the ray has hit.

   ```cpp pseudocode
   begin: request = World::RequestCellsAround(destination, 48)
   each frame:
       if not World::IsLoadedAround(destination, 48): return
       hit = Physics::Raycast(destination + 300 up, down, 900)
       if no hit: return
       move the player to hit.Point plus a small lift
       request.Release()
   ```

   The ray is the test of collision, so the script never moves on the loaded cells alone.
   :::

## Where it lives in Strata

- `Strata/src/Strata/World/WorldComponents.h`: `WorldComponent`, `StreamingSourceComponent`.
- `Strata/src/Strata/World/WorldRegistration.cpp`: the registration and the system's order.
- `Strata/src/Strata/World/WorldStreamingSystem.cpp`: `GatherSources`, `OnUpdate`, `PrepareLoadedScene`, `WaitForStartCells`.
- `Strata/src/Strata/World/WorldStreamer.cpp`: `ReserveBodies`. `Strata/src/Strata/World/WorldAsset.cpp`: `GetRecommendedMaxBodies`.
- `StrataEditor/src/Editor/WorldCook.cpp`: `ComputeMaxBodiesInRadius`. Commands: `world.cook`, `world.info`.
- `StrataScriptCore/Include/StrataScript/World.h` and `Strata/src/Strata/Scripting/ScriptHostAPI.cpp`: the SDK and host functions.
- Tests: the suite World.Streaming, the suites `Scripting.World` and `Editor.WorldCook`, and the feature test's `WorldFeatures.cpp`.

## Further reading

- Unreal Engine's documentation on World Partition: the same streaming idea in another engine (intermediate).
- Game Engine Architecture by Jason Gregory: the chapter on streaming and the resource manager (intermediate).
