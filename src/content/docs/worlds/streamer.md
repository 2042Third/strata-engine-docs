---
id: worlds/streamer
title: "The streamer"
description: "How WorldStreamer decides which cells of a world load, in which order and when they go, and how it follows each cell while it loads, fails or unloads."
kind: internals
size: L
tracks: [E]
needs: [worlds/grids, core/jobs]
time: 100
learn:
  - id: wanted-set
    text: compute the wanted cells and the kept cells of a source on a grid from its radius and its keep distance
  - id: load-order
    text: predict which cells one update starts and in which order, from priority, view bias, distance and the limit of four loads
  - id: evaluate
    text: trace one update of the streamer, naming the steps of its update and of its evaluation and when the evaluation runs at all
  - id: cell-states
    text: name the five states of a cell, how each follows the state of its sub-scene and what happens to a cell that failed
  - id: change-safely
    text: choose the changes to the streamer that keep its decisions in a total order and cheap while nothing moves
since: 0.4.0
status: final
---

A streamed world has more cells than memory can hold, so `WorldStreamer` decides, every frame, which of them exist right now. It reads the places the world should be ready around, compares them with the world's cells and asks the scene to load or unload :term[sub-scenes]{id=sub-scene}. It does not create entities, decide where the places come from or size the physics room. This page teaches how it decides, from the problem to the last tie-break, and how it tracks every cell while the cell loads, fails or goes.

## The problem and how engines solve it

An island a few hundred metres wide can hold tens of thousands of trees. A world of kilometres holds far more than memory, the disk and one frame can handle. A streamed world cuts the ground into cells, as [the grids page](../worlds/grids.md) describes, and keeps only the cells near the player ([why worlds stream](../worlds/why-streaming.md)). The question of this page is which cells, in which order and for how long. Each simple answer fails in a way a player notices.

The first simple answer is to load the cells around the camera. It works until the camera is not where the game happens. A script teleports the player, and the ground at the arrival point is missing. A vehicle drives out of the camera's range and falls through ground that never loaded. The mistake is to treat interest as the camera: Strata treats it as a list of points, called sources, and the camera is only one of them.

The second simple answer is one distance: load a cell when it comes within the radius and unload it when it leaves. A player who stands on that border and shifts by a few centimetres loads and unloads the cell on every frame. Each load costs a read, a compile and the creation of the cell's entities, all thrown away at once. The fix is two distances.

The third simple answer is to start every wanted load at once. The nearest cells then wait behind the farthest, because the disk and the worker threads spread over cells nobody needs yet. The fourth is to decide in whatever order a :term[hash map]{id=hash-map} lists its entries, or to decide on every frame. Different machines or thread counts then load cells in different orders, and tests cannot compare them. Strata ranks cells in a total order, starts at most four loads at once and decides only when something changed.

## The map

Two programs drive one core: in Play and Simulate the world system calls the streamer from its update, and in Edit the editor owns a streamer of its own, around the editor camera. Both run on the :term[main thread]{id=main-thread}, which owns the scene, so the streamer needs no locks. The streamer's inputs are the sources, the pins, the enabled layers and the :term[World asset]{id=world-asset}. Its outputs are three scene calls: start a sub-scene load, start an unload, and cancel a load that has not finished, which is also an unload.

```mermaid caption="Two drivers call one streamer on the main thread. It reads the sources, pins, layer toggles and the world asset, and it answers with sub-scene loads, unloads and cancellations." alt="A left to right diagram. Two boxes on the left, the world system for Play and Simulate and the editor for Edit, each send arrows into a central box, the streamer. Four small boxes feed the streamer: sources, pins, enabled layers and the world asset. Three arrows leave the streamer toward the scene: load a sub-scene, unload a sub-scene and cancel a load."
flowchart LR
    Sys["World system (Play, Simulate)"] --> S["WorldStreamer"]
    Ed["Editor (Edit)"] --> S
    Src["Sources"] --> S
    Pins["Pins"] --> S
    Lay["Enabled layers"] --> S
    Wld["World asset"] --> S
    S --> Load["LoadSubScene"]
    S --> Unload["UnloadSubScene"]
    S --> Cancel["Cancel a load"]
```

The streamer lives in `Strata/src/Strata/World/WorldStreamer.h` and `WorldStreamer.cpp`. The world system's update in `Strata/src/Strata/World/WorldStreamingSystem.cpp` gathers the sources, hands them over with `SetSources` and calls `Update`. Where the sources come from, and the physics room the streamer asks for, belong to [the page on physics and scripts](../worlds/physics-scripts.md). The rest of this page has two halves: what to load, then the cells :term[in flight]{id=in-flight}.

## What to load

### A source

A **streaming source** is a point on the ground that cells stream around, such as a player, a vehicle, a camera or a script's request. The streamer sees each one as the six fields of `WorldStreamingSource`, shown here.

```cpp src="Strata/src/Strata/World/WorldStreamer.h#L32-L37"
glm::vec3 Position { 0.0f };
glm::vec3 Forward { 0.0f, 0.0f, -1.0f }; // Cells ahead rank nearer (ViewBias); zero: no direction
float Radius = 0.0f;                     // 0: each layer's StreamingDistance times the world's DistanceScale
uint32_t LayerMask = ~0u;                // Bit i: the world's layer i (in WorldData::Layers order) streams
int32_t Priority = 0;                    // Higher-priority sources' cells load first
float ViewBias = 0.25f;                  // Cells ahead rank as if this share of the radius nearer (ordering only)
```

The position and the forward direction say where the source is and which way it faces. The radius is in metres; a radius of 0 means that each layer uses its own distance. The layer mask has one bit for each layer of the world, in the order of the world's layer list, so a source can stream the ground and ignore the props. The priority orders the loads of several sources. The view bias is explained below.

The **streaming distance** of a layer is the radius, in metres, within which its cells load around a source with a radius of 0. The world's distance scale multiplies it and stays between 0.1 and 10. A source with a radius above 0 uses it for every layer instead. The streamer drops a source whose position or radius is not a number, because such a source cannot stream anything.

### Wanted cells

A **wanted cell** is a cell of an enabled layer whose square lies within some source's radius, or a pinned cell. The streamer works on each pair of a source and a layer that the source's mask includes. For each pair it measures the distance from the source to the cell's square on the ground plane: zero when the source stands inside the square. Height plays no part, so a cell reaches from the bottom of the world to its top.

Which cells to measure is a search problem. The grid squares around the source form a small block, but a layer may hold only a few cells in a huge area. The streamer finds the corner cells of the block, counts its squares and compares that count with the length of the layer's cell list. If the block is larger it walks the list, and otherwise it finds each square in the world's index.

```cpp src="Strata/src/Strata/World/WorldStreamer.cpp#L39-L60"
template<typename Visit>
void ForEachCellAround(const WorldAsset& world, const WorldLayer& layer, std::span<const int32_t> layerCells, const glm::dvec3& position, double radius,
	Visit&& visit)
{
	const WorldData& data = world.GetData();
	const SquareRange range = GetSquaresAround(layer, data.GridOrigin, position, radius);
	if (range.GetCount() > static_cast<double>(layerCells.size()))
	{
		for (const int32_t index : layerCells)
			visit(index);
		return;
	}
	for (int32_t x = range.Min.X; x <= range.Max.X; x++)
	{
		for (int32_t z = range.Min.Z; z <= range.Max.Z; z++)
		{
			const int32_t index = world.FindCell(WorldCellKey { layer.ID, x, z });
			if (index >= 0)
				visit(index);
		}
	}
}
```

1. **Line 45:** `GetCount` multiplies the block's width by its height; the comparison picks the shorter walk.
2. **Lines 47–48:** a sparse layer, such as a few landmark cells, visits its whole list, which is shorter than the block of squares around the source.
3. **Lines 51–57:** a dense layer visits each square of the block and keeps the ones that exist, found by key.

The scan covers the keep radius, which the next section defines, because the same pass finds both the cells to start and the cells to keep.

### Two rings

Take cells 32 m wide and a source with a radius of 40 m. The cell on row 0 that spans x from 96 m to 128 m lies 96 − x metres from a source at x on the same row, at z = 16 m. The streamer wants it when 96 − x is at most 40, so from x = 56 m on. Now let the player stand on 56 m and shift by a centimetre each frame, between 55.99 m and 56.01 m. With one threshold the cell is wanted on one frame and not on the next, so it loads and unloads on every frame, 99 times in 100 frames.

Two radii end that. The load radius is the source's radius: cells within it are wanted. The keep radius is larger: a loaded cell stays while it lies within it. The extra distance is called the hysteresis, a word for two thresholds that stop a value from flickering between two states, which [the page on gamepads](../input/gamepads.md) teaches with buttons. Strata computes it from the layer's cell size and the source's radius.

$$H = \max\left(\frac{s}{2},\ 0.1\,r\right)$$

Here $H$ is the extra keep distance in metres, $s$ is the layer's cell size in metres and $r$ is the load radius in metres. The sign $\max$ is read "the larger of": half a cell, or a tenth of the radius. The keep radius is $r + H$. In the example $H$ is the larger of 16 m and 4 m, so 16 m, and the keep radius is 56 m. The cell stays loaded until 96 − x passes 56, at x = 40 m, so the player must walk 16 m back before it unloads, and the shifting costs one load and nothing more.

:::why[Two rings, not a timer]
A timer would delay each unload by some seconds, but it would still load and unload the cell, only more slowly. A distance gap works at any walking speed and needs no clock. The cost is memory: the ring between the radii holds cells nobody needs yet.
:::

The same border can be drawn. Take a 6 by 6 grid of 32 m cells with its corner at 0, a source at (16, 16) and a radius of 48 m. With the rule above $H$ is the larger of 16 m and 4.8 m, so 16 m and the keep radius is 64 m. The map marks each cell by the first word that fits: **S** is the wanted cell that holds the source, **W** is wanted, **K** is kept only, and a dot is neither.

```text
      x=0  x=1  x=2  x=3
z=0    S    W    W    .
z=1    W    W    K    .
z=2    W    K    .    .
z=3    .    .    .    .
```

Six cells are wanted. The cell (2, 0) is exactly 48 m away, which counts, because the test is "at most". The cell (2, 1) is 50.6 m away, outside the radius and inside the keep radius, so a loaded (2, 1) stays but an unloaded one does not start.

### The order of loads

Wanted cells compete for at most four load slots. The streamer ranks them in a total order: no two cells tie, so the same inputs always give the same list. The keys are, in turn, the priority (higher first), the view-biased distance (smaller first) and the packed key of the cell (smaller first), which breaks every remaining tie. [The grids page](../worlds/grids.md) explains that the packed key sorts by layer, then x, then z.

The **view bias** of a source is the share of its radius by which cells ahead of it rank as if they were nearer. It changes the order of loads and never the set of wanted cells. The streamer takes the direction from the source to the cell's centre and finds its :term[cosine]{id=cosine} against the source's forward direction on the ground plane. It clamps a negative cosine to 0 and subtracts that share of the radius.

$$d' = d - b\,r\,a$$

Here $d'$ is the ranking distance in metres and $d$ is the distance to the cell's square. $b$ is the view bias from 0 to 1, and $a$ is the cosine of the angle between the facing and the direction to the cell, from 0 to 1. Cells beside or behind the source have $a = 0$ and rank by $d$. A cell straight ahead ranks $b\,r$ metres nearer. A source with a forward direction of zero has no facing, so every cell ranks by $d$.

Cells within half the radius also start with the asset priority `High`; farther ones start with `Normal`. That decides how the cell's scene competes with other asset loads, not the order among cells.

:::example[Which four cells start first]
Use the grid above, with the source facing +Z and a view bias of 0.25, so $b\,r$ = 12 m. The cell (0, 0) holds the source: $d' = 0$. The cell (0, 1) is 16 m away and straight ahead: $d' = 16 - 12 = 4$. The cell (1, 1) is 22.6 m away at a cosine of 0.71: $d' = 22.6 - 8.5 = 14.1$.

The cell (1, 0) is 16 m away at the side: $d' = 16$. Those four start in that order, and (0, 2) with $d' = 36$ and (2, 0) with $d' = 48$ wait. Face -Z, the default, and every cell is beside or behind the source, so $d'$ equals $d$. The order becomes (0, 0), (0, 1), (1, 0), (1, 1), with the tie of 16 m broken by key, as the test below expects.
:::

The limit of four counts cells in the `Loading` state, which the second half defines. A fast source never queues more than four reads, so its nearest cells never wait behind its farthest.

## The contract

A caller of the streamer may assume the following, and must do the following. Each rule has its reason.

- Call `Update` on the main thread once per frame, after `SetSources`: the scene it calls belongs to that thread.
- Pair every `PinCell` with an `UnpinCell`. A pin keeps a cell loaded whatever the sources do, and it is counted: two pins need two calls of `UnpinCell` before the cell may unload.
- Set layers by name. A name set before the world loads is remembered and applied on load, so a game can choose its layers at start.
- Read the cells' states, not the decisions: `GetLastDecisions` lists what the last update started, for tools and tests.
- Expect the same decisions from the same inputs and cell states, whatever the thread count. Loads finish at different times, so only the states they leave behind may differ.

:::rule[Request the World asset every update, never hold it]
The streamer asks the :term[asset manager]{id=asset-manager} for the World asset on every update and keeps only a weak reference between updates. A weak reference finds the object while it exists but never keeps it alive. A reference held across frames would keep the asset resident by itself, and residency would stop following what the game uses. [Residency](../assets/residency.md) explains why.
:::

## A toy version

Before the real code, here is the whole decision for one source over one layer. It has a 6 by 6 grid of 32 m cells, the keep radius, the view bias, the order of loads and the cap of four, and a load finishes at once. It reads the grid of the map above but faces +Z.

:::question
This page shows C++ from here on. If classes, lambdas and `std::sort` are new, read [the classes page](../basics/cpp-classes.md) and [the page on generic code](../basics/cpp-generic.md) first.
:::

The program evaluates four frames: the source at (16, 16), the same again, a small step to x = 6 and then a jump to x = -20. Watch for the unloads before the loads, and for the cells that stay.

```cpp sketch="worlds-streamer-toy.cpp"
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <set>
#include <vector>

namespace
{

	constexpr int c_GridSize = 6;
	constexpr double c_CellSize = 32.0;
	constexpr size_t c_MaxLoads = 4;

	struct Source
	{
		double X = 0.0;
		double Z = 0.0;
		double ForwardX = 0.0;
		double ForwardZ = 1.0;
		double Radius = 0.0;
		double ViewBias = 0.25;
	};

	struct Candidate
	{
		uint64_t Key = 0;
		double Distance = 0.0; // View-biased
	};

	uint64_t Pack(int x, int z)
	{
		return (static_cast<uint64_t>(x) << 32) | static_cast<uint64_t>(z);
	}

	// Zero inside the cell's square, else the distance to its nearest point.
	double DistanceToCell(int x, int z, const Source& source)
	{
		const double dx = std::max({ x * c_CellSize - source.X, 0.0, source.X - (x + 1) * c_CellSize });
		const double dz = std::max({ z * c_CellSize - source.Z, 0.0, source.Z - (z + 1) * c_CellSize });
		return std::sqrt(dx * dx + dz * dz);
	}

	// One evaluation: unloads first, then at most c_MaxLoads loads, best first. A load finishes at once in this toy.
	void Evaluate(int frame, const Source& source, std::set<uint64_t>& loaded)
	{
		const double keepRadius = source.Radius + std::max(c_CellSize * 0.5, 0.1 * source.Radius);
		std::set<uint64_t> keep;
		std::vector<Candidate> candidates;
		for (int x = 0; x < c_GridSize; x++)
		{
			for (int z = 0; z < c_GridSize; z++)
			{
				const double distance = DistanceToCell(x, z, source);
				if (distance > keepRadius)
					continue;
				keep.insert(Pack(x, z));
				if (distance > source.Radius)
					continue;
				const double toX = (x + 0.5) * c_CellSize - source.X;
				const double toZ = (z + 0.5) * c_CellSize - source.Z;
				const double length = std::sqrt(toX * toX + toZ * toZ);
				const double ahead = length > 1e-6 ? std::max(0.0, (toX * source.ForwardX + toZ * source.ForwardZ) / length) : 0.0;
				candidates.push_back({ Pack(x, z), distance - source.ViewBias * source.Radius * ahead });
			}
		}

		std::printf("frame %d:", frame);
		for (auto it = loaded.begin(); it != loaded.end();)
		{
			if (keep.contains(*it))
			{
				++it;
				continue;
			}
			std::printf(" unload (%d,%d)", static_cast<int>(*it >> 32), static_cast<int>(*it & 0xFFFFFFFFu));
			it = loaded.erase(it);
		}
		std::sort(candidates.begin(), candidates.end(), [](const Candidate& a, const Candidate& b)
		{
			return a.Distance != b.Distance ? a.Distance < b.Distance : a.Key < b.Key;
		});
		size_t started = 0;
		for (const Candidate& candidate : candidates)
		{
			if (started == c_MaxLoads)
				break;
			if (!loaded.insert(candidate.Key).second)
				continue;
			std::printf(" load (%d,%d)", static_cast<int>(candidate.Key >> 32), static_cast<int>(candidate.Key & 0xFFFFFFFFu));
			started++;
		}
		std::printf("\n");
	}

}

int main()
{
	std::set<uint64_t> loaded;
	Source source;
	source.X = 16.0;
	source.Z = 16.0;
	source.Radius = 48.0;
	Evaluate(1, source, loaded);
	Evaluate(2, source, loaded);
	source.X = 6.0;
	Evaluate(3, source, loaded);
	source.X = -20.0;
	Evaluate(4, source, loaded);
	return 0;
}
```

```text output-of="worlds-streamer-toy.cpp"
frame 1: load (0,0) load (0,1) load (1,1) load (1,0)
frame 2: load (0,2) load (2,0)
frame 3:
frame 4: unload (2,0)
```

1. **Line 47:** the keep radius is the radius plus the larger of half a cell and a tenth of the radius.
2. **Lines 54–58:** a cell farther than the keep radius is ignored; one inside it is kept; only one inside the radius is also a candidate.
3. **Line 63:** the cosine of the angle to the cell, clamped to 0, scales the bias.
4. **Lines 69–78:** unloads come first, in key order, because the set keeps its keys sorted.
5. **Lines 79–91:** the loads are sorted by biased distance, then key, and only the first four that are not loaded start.

The first frame starts four cells and the second the other two, as the cap says. The third frame, with the source at x = 6, starts nothing: the cell (2, 0) is now 58 m away, outside the radius and inside the keep radius. The fourth frame, at x = -20, finds it 84 m away, beyond 64 m, and unloads it. The real streamer adds cells that take many frames to load, failures, several sources, pins, layers and a world that can change.

## Evaluate and update

The real code follows the order in which data flows. `Update` runs every frame and decides whether to evaluate. `Evaluate` finds the wanted and kept sets, unloads, ranks and starts. The cell states and their polling come after.

### One update

`Update` runs on every frame, so its first lines matter most. It requests the asset, polls the cells in flight and returns early when nothing changed.

```cpp src="Strata/src/Strata/World/WorldStreamer.cpp#L228-L253"
void WorldStreamer::Update()
{
	ST_PROFILE_FUNCTION();
	m_Decisions.clear();
	m_Stats.EntitiesCreatedLastUpdate = 0;
	m_Stats.EntitiesDestroyedLastUpdate = 0;
	m_Stats.EvaluatedCells = 0;
	AssetManagerBase* assets = m_Scene.GetAssetManager();
	if (!assets || !m_World.IsValid())
		return;

	// Requested every update: the World asset stays resident while it streams, without a reference held across frames.
	const Ref<WorldAsset> world = assets->GetAsset<WorldAsset>(m_World, AssetPriority::High);
	if (PollCellsInFlight())
		m_Dirty = true;
	if (!world)
		return;
	if (RefreshWorld(world))
		m_Dirty = true;
	if (RetryChangedFailures())
		m_Dirty = true;
	if (!m_Dirty && !SourcesMoved())
		return;
	Evaluate(*world);
	m_Dirty = false;
}
```

1. **Line 240:** the World asset is requested at `High` priority every update, in a local `Ref` that dies at the end of the function.
2. **Lines 241–242:** cells in flight are polled before anything else, so a finished load marks the streamer dirty.
3. **Lines 249–250:** with nothing dirty and no source moved, the update ends here; this is the idle cost.

The evaluation runs only when the :term[dirty flag]{id=dirty-flag} is set or a source moved. `SourcesMoved` compares each source with the copy kept by the last evaluation: a new count of sources, a move of more than `c_SourceEpsilon` (1 cm), or a different radius, layer mask, priority or view bias. The facing alone does not count, because it only orders loads and every evaluation reads it when it runs. Pins, layer toggles, a new world or scale, a finished load, a reloaded World asset and a failed cell with a changed scene all set the flag.

```mermaid caption="One update of the streamer: it requests the asset, polls the cells in flight, refreshes its tables, tries changed failures again, and evaluates only when something changed." alt="A diagram read from top to bottom. The boxes are request the world asset, poll cells in flight, refresh from a new asset, try changed failures again and a decision box that asks whether anything is dirty or a source moved. The answer no leads to the end. The answer yes leads to a box evaluate, then to the end."
flowchart TD
    A["Request the World asset (High)"] --> B["PollCellsInFlight"]
    B --> C{"World loaded?"}
    C -- no --> Z["End"]
    C -- yes --> D["RefreshWorld"]
    D --> E["RetryChangedFailures"]
    E --> F{"Dirty, or a source moved?"}
    F -- no --> Z
    F -- yes --> G["Evaluate"]
    G --> Z
```

The test `A still source costs no evaluation; one that moved more than a centimeter does` in `StrataTests/src/World/WorldStreamerTests.cpp` checks this: a source that shifts by 0.005 m leaves `EvaluatedCells` at 0, and one that shifts by 0.02 m makes it positive.

### The wanted set and the keep set

`Evaluate` begins with a small function that merges what several sources say about one cell. A cell seen by two sources keeps the better priority, and among equal priorities the smaller distance. It is `High` if any source has it within half its radius.

```cpp src="Strata/src/Strata/World/WorldStreamer.cpp#L432-L447"
auto want = [this](uint64_t key, int32_t priority, double distance, bool high)
{
	const auto [it, inserted] = m_CandidateIndex.try_emplace(key, m_Candidates.size());
	if (inserted)
	{
		m_Candidates.push_back(Candidate { key, priority, distance, high });
		return;
	}
	Candidate& candidate = m_Candidates[it->second];
	if (priority > candidate.Priority || (priority == candidate.Priority && distance < candidate.Distance))
	{
		candidate.Priority = priority;
		candidate.Distance = distance;
	}
	candidate.High = candidate.High || high;
};
```

1. **Line 434:** the first source to want a cell adds a candidate; `try_emplace` reports whether the key was new.
2. **Line 441:** a higher priority replaces the rank at once, even if its distance is larger.
3. **Line 446:** the `High` flag is a union over sources.

The loop over sources then does the work of the previous sections, one layer at a time.

```cpp src="Strata/src/Strata/World/WorldStreamer.cpp#L449-L481"
for (const WorldStreamingSource& source : m_Sources)
{
	const glm::dvec3 position(source.Position);
	glm::dvec2 forward(source.Forward.x, source.Forward.z);
	const double forwardLength = glm::length(forward);
	forward = forwardLength > 1e-6 ? forward / forwardLength : glm::dvec2(0.0);
	const double viewBias = std::isfinite(source.ViewBias) ? std::clamp(static_cast<double>(source.ViewBias), 0.0, 1.0) : 0.0;
	for (size_t layerIndex = 0; layerIndex < data.Layers.size() && layerIndex < 32; layerIndex++)
	{
		if (!IsLayerOn(layerIndex) || (source.LayerMask & (1u << layerIndex)) == 0)
			continue;
		const WorldLayer& layer = data.Layers[layerIndex];
		const double radius = GetRadius(source, layerIndex);
		const double hysteresis = std::max(static_cast<double>(layer.CellSize) * 0.5, 0.1 * radius);
		const double keepRadius = radius + hysteresis;
		ForEachCellAround(world, layer, m_LayerCells[layerIndex], position, keepRadius, [&](int32_t index)
		{
			const WorldCell& cell = data.Cells[static_cast<size_t>(index)];
			const WorldCellSquare square = WorldGrid::CellBounds(layer, data.GridOrigin, cell.X, cell.Z);
			const double distance = WorldGrid::Distance(square, position);
			evaluated++;
			if (distance > keepRadius)
				return;
			const uint64_t key = cell.GetKey().Pack();
			m_Keep.insert(key);
			if (distance > radius)
				return;
			// Cells ahead of the source rank as if a share of the radius nearer.
			const glm::dvec2 toCell = (square.Min + square.Max) * 0.5 - glm::dvec2(position.x, position.z);
			const double toCellLength = glm::length(toCell);
			const double ahead = toCellLength > 1e-6 ? std::max(0.0, glm::dot(toCell / toCellLength, forward)) : 0.0;
			want(key, source.Priority, distance - viewBias * radius * ahead, distance <= radius * 0.5);
		});
```

1. **Lines 452–454:** the forward vector is flattened to the ground plane and :term[normalized]{id=normalization}, or becomes zero when it is too short.
2. **Line 462:** the keep distance of the formula, in double precision.
3. **Lines 470–474:** a cell beyond the keep radius is dropped; one inside joins the keep set; one beyond the radius stops there.
4. **Line 480:** the rank subtracts the biased share, and the `High` flag is a test against half the radius.

Pins come next. They are wanted before any source's cells, and the streamer looks each one up in the world and ignores a pin for a cell the world does not have.

```cpp src="Strata/src/Strata/World/WorldStreamer.cpp#L485-L491"
for (const auto& [key, count] : m_Pins)
{
	if (world.FindCell(WorldCellKey::Unpack(key)) < 0)
		continue;
	m_Keep.insert(key);
	want(key, std::numeric_limits<int32_t>::max(), 0.0, true);
}
```

A pinned cell joins the keep set and enters the candidates with the largest priority, a distance of 0 and the `High` flag, so it ranks before every source's cells.

### Unloads first

Unloads come before loads, so that the memory and the physics room of a cell that goes are on their way back before another cell asks for them.

```cpp src="Strata/src/Strata/World/WorldStreamer.cpp#L499-L537"
m_Keys.clear();
for (auto& [key, record] : m_Cells)
{
	if (record.Status == WorldCellStatus::Loaded)
	{
		const SubSceneStatus* status = m_Scene.GetSubSceneStatus(record.SubScene);
		if (!status || status->State != SubSceneState::Loaded)
		{
			m_Keys.push_back(key);
			continue;
		}
	}
	if ((record.Status == WorldCellStatus::Loading || record.Status == WorldCellStatus::Loaded) && !m_Keep.contains(key))
		m_Keys.push_back(key);
}
std::sort(m_Keys.begin(), m_Keys.end());
for (const uint64_t key : m_Keys)
{
	CellRecord& record = m_Cells.at(key);
	const SubSceneStatus* status = m_Scene.GetSubSceneStatus(record.SubScene);
	if (record.Status == WorldCellStatus::Loaded && (!status || status->State != SubSceneState::Loaded))
	{
		// Gone or going without the streamer: follow it.
		if (status && status->State == SubSceneState::Unloading)
		{
			record.Status = WorldCellStatus::Unloading;
			record.EntitiesAtUnload = status->CreatedEntities;
			record.DestroyedSeen = status->DestroyedEntities;
			m_InFlight.push_back(key);
		}
		else
		{
			m_Cells.erase(key);
		}
		m_Stats.StateVersion++;
		continue;
	}
	Unload(key, record);
}
```

1. **Lines 500–513:** the cells to unload are the loaded ones whose sub-scene is no longer loaded and the loading or loaded ones outside the keep set.
2. **Line 514:** the keys are sorted, because the cell map is a hash map and its order is not stable.
3. **Lines 519–534:** a loaded cell whose sub-scene went without the streamer is followed: it is marked as unloading when its sub-scene is, and forgotten when it is gone.
4. **Line 536:** every other cell goes through `Unload`, which calls `UnloadSubScene`: on a loading cell that cancels the load.

A cell leaves the keep set for three reasons: it is outside every ring, its layer is disabled, or its cell is gone from the world. The streamer does not tell them apart; none of the sources keep it.

### Loads in rank order

Loads are the last step of an evaluation. Look at how the slots are counted, how candidates that already have a record are skipped and why the front is sorted twice.

```cpp src="Strata/src/Strata/World/WorldStreamer.cpp#L540-L573"
uint32_t loading = 0;
for (const auto& [key, record] : m_Cells)
	loading += record.Status == WorldCellStatus::Loading ? 1 : 0;
std::sort(m_Candidates.begin(), m_Candidates.end(), [](const Candidate& a, const Candidate& b)
{
	if (a.Priority != b.Priority)
		return a.Priority > b.Priority;
	if (a.Distance != b.Distance)
		return a.Distance < b.Distance;
	return a.Key < b.Key;
});
size_t starting = 0;
std::vector<Candidate>& candidates = m_Candidates;
for (size_t index = 0; index < candidates.size() && loading + starting < c_MaxConcurrentCellLoads; index++)
{
	if (m_Cells.contains(candidates[index].Key))
		continue;
	// Moved to the front, in rank order: the cells this update starts.
	std::swap(candidates[starting], candidates[index]);
	starting++;
}
if (starting == 0)
	return;
std::sort(candidates.begin(), candidates.begin() + static_cast<std::ptrdiff_t>(starting), [](const Candidate& a, const Candidate& b)
{
	if (a.Priority != b.Priority)
		return a.Priority > b.Priority;
	if (a.Distance != b.Distance)
		return a.Distance < b.Distance;
	return a.Key < b.Key;
});
ReserveBodies(world, std::span<const Candidate>(candidates.data(), starting));
for (size_t index = 0; index < starting; index++)
	StartLoad(world, candidates[index]);
```

1. **Lines 541–542:** the streamer counts the cells that are loading, which is the number of slots already taken.
2. **Lines 543–550:** the sort rule is the total order: priority, biased distance, key.
3. **Lines 553–560:** the loop skips every candidate that has a record already, loaded, loading, unloading or failed, and moves the others to the front until the slots are full.
4. **Lines 563–570:** the swaps disturbed the order of the front, so it is sorted again.
5. **Lines 571–573:** the physics reservation comes first, then each load starts.

The reservation call, `ReserveBodies`, tells physics how many bodies the :term[persistent scene]{id=persistent-scene}, the held cells and the starting cells need together, so that physics grows once before their bodies arrive instead of in small steps. It runs only for a world with a cooked index. [The physics and scripts page](../worlds/physics-scripts.md) teaches why.

`StartLoad` asks the scene for a sub-scene of the cell's scene file, with the priority chosen above, and records the cell as `Loading`. When the scene refuses at once, the cell is recorded as `Failed` with the scene's message, and the load still counts as a decision.

:::example[The first test, line by line]
The test `A source loads the cells within its radius nearest first, four at a time, and keeps them within the hysteresis` runs the grid of the map. The source stands at (16, 16) with the default facing and a 48 m radius, so six cells are wanted. The first frame must start (0, 0), (0, 1), (1, 0) and (1, 1) in that order. The source then swings back and forth between x = 6 and x = 16 for 60 frames, and no decision may follow. At x = -20 exactly one cell, (2, 0), unloads.
:::

In the test, look at how the wanted set is found without the streamer and how the first four decisions are checked.

```cpp src="StrataTests/src/World/WorldStreamerTests.cpp#L169-L194"
TEST_CASE("A source loads the cells within its radius nearest first, four at a time, and keeps them within the hysteresis")
{
	ScopedJobSystem jobs(2, 1);
	MountedWorld mounted("WorldStreamerRadius", SmallWorld());
	Scene scene("Streamed");
	StreamerDrive drive(mounted, scene);
	const WorldData& data = mounted.World.Data;

	// 48 m around the middle of cell (0, 0), whose cells are 32 m: H = max(16, 4.8) = 16.
	const WorldStreamingSource source = SourceAt(16.0f, 16.0f);
	const std::set<WorldCellKey> wanted = CellsWithin(data, 1, source.Position, 48.0);
	REQUIRE(wanted.size() == 6);
	drive.FramesUntil(source, [&]() { return LoadedCells(drive.Streamer) == wanted; });
	CHECK(drive.MostLoading <= WorldStreamer::c_MaxConcurrentCellLoads);
	CHECK(drive.Streamer.IsLoadedAround(source.Position, 48.0f));
	CHECK(drive.Streamer.GetStats().CellsWanted == 6);
	CHECK(drive.Streamer.GetStats().LoadsStarted == 6);
	// The first frame starts the four nearest cells, nearest first (ties by key).
	REQUIRE(drive.Decisions[0].size() == 4);
	CHECK(drive.Decisions[0][0].Key == WorldCellKey { 1, 0, 0 });
	CHECK(drive.Decisions[0][1].Key == WorldCellKey { 1, 0, 1 });
	CHECK(drive.Decisions[0][2].Key == WorldCellKey { 1, 1, 0 });
	CHECK(drive.Decisions[0][3].Key == WorldCellKey { 1, 1, 1 });
	const SubSceneID first = drive.Streamer.GetCellSubScene(WorldCellKey { 1, 0, 0 });
	REQUIRE(first != 0);
	CHECK(scene.GetSubSceneStatus(first)->CreatedEntities == 20);
```

1. **Line 178:** the source of the example, with no radius, so the layer's streaming distance of 48 m applies.
2. **Lines 179–180:** the wanted cells are found independently of the streamer, by the grids page's distance function.
3. **Lines 187–191:** the first frame's four decisions, in order.

## Cells in flight

The second half follows a cell after the decision. The streamer keeps one record for each cell that is not plain unloaded, and a short list of the keys that are in flight.

### The five states

A cell is in one of five states, from `WorldCellStatus`.

```cpp src="Strata/src/Strata/World/WorldStreamer.h#L42-L46"
Unloaded = 0,
Loading,   // Its scene loads, or its entities are created
Loaded,
Unloading, // Its entities go a slice per update
Failed     // Its load failed (Error says why); not retried until its scene changes
```

`Unloaded` is the absence of a record. The other four are real states, and each follows the state of the sub-scene that the scene keeps for the cell.

```mermaid caption="The states of a cell. A load that finishes makes it loaded; a failed load keeps its error; an unload, from the streamer or from someone else, leads to unloaded." alt="A state diagram with five boxes: unloaded, loading, loaded, unloading and failed. Unloaded goes to loading when a load starts. Loading goes to loaded, to failed or, when cancelled, to unloading. Loaded goes to unloading when the cell leaves the keep set or someone else unloads it. Unloading returns to unloaded when its last entity is gone, and failed returns to unloaded when its scene changes."
stateDiagram-v2
    [*] --> Unloaded
    Unloaded --> Loading: a load starts
    Loading --> Loaded: sub-scene loaded
    Loading --> Failed: sub-scene failed
    Loading --> Unloading: cancelled
    Loaded --> Unloading: left the keep set
    Unloading --> Unloaded: last entity gone
    Failed --> Unloaded: its scene changed
```

| Cell state | Sub-scene state | What it means |
| --- | --- | --- |
| `Loading` | `Loading` or `Instantiating` | The scene reads and compiles, then its entities are created in slices |
| `Loaded` | `Loaded` | Every entity exists |
| `Unloading` | `Unloading` | The entities are inactive and go a slice per update |
| `Failed` | none: the streamer unloaded it | The load failed; the cell keeps the error text |

### Polling only what moves

Most cells are loaded and quiet. Asking each of them for news every frame would cost as much as the world is big, so the streamer polls only the keys in its in-flight list: the cells that are loading or unloading. A cell that finishes leaves the list. The same pass counts the entities created and destroyed since the last update, which the statistics report.

```cpp src="Strata/src/Strata/World/WorldStreamer.cpp#L300-L354"
CellRecord& record = it->second;
const SubSceneStatus* status = m_Scene.GetSubSceneStatus(record.SubScene);
bool done = false;
if (record.Status == WorldCellStatus::Unloading)
{
	if (!status)
	{
		// Its last entities went in the last update.
		if (record.EntitiesAtUnload > record.DestroyedSeen)
			m_Stats.EntitiesDestroyedLastUpdate += static_cast<uint32_t>(record.EntitiesAtUnload - record.DestroyedSeen);
		m_Cells.erase(it);
		done = true;
	}
	else if (status->State == SubSceneState::Unloading)
	{
		m_Stats.EntitiesDestroyedLastUpdate += static_cast<uint32_t>(status->DestroyedEntities - std::min(status->DestroyedEntities, record.DestroyedSeen));
		record.DestroyedSeen = status->DestroyedEntities;
	}
}
else if (!status)
{
	// Unloaded by someone else to its last entity.
	m_Cells.erase(it);
	done = true;
}
else
{
	m_Stats.EntitiesCreatedLastUpdate += static_cast<uint32_t>(status->CreatedEntities - std::min(status->CreatedEntities, record.CreatedSeen));
	record.CreatedSeen = status->CreatedEntities;
	if (status->State == SubSceneState::Loaded)
	{
		record.Status = WorldCellStatus::Loaded;
		done = true;
	}
	else if (status->State == SubSceneState::Failed)
	{
		// Kept as failed (with its error) until its scene changes; the failed sub-scene goes.
		record.Status = WorldCellStatus::Failed;
		record.Error = status->Error;
		m_FailedCells++;
		m_Scene.UnloadSubScene(record.SubScene);
		record.SubScene = 0;
		if (AssetManagerBase* assets = m_Scene.GetAssetManager())
			record.FailedRevision = assets->GetSourceRevisions(record.Scene).Current;
		done = true;
	}
	else if (status->State == SubSceneState::Unloading)
	{
		// Someone else unloads it: it goes like one the streamer unloads.
		record.Status = WorldCellStatus::Unloading;
		record.EntitiesAtUnload = status->CreatedEntities;
		record.DestroyedSeen = status->DestroyedEntities;
		m_Stats.StateVersion++;
	}
}
```

1. **Lines 303–318:** an unloading cell is done when its sub-scene is gone; until then the destroyed count grows by what the last slice removed.
2. **Lines 319–324:** a loading cell whose sub-scene vanished was unloaded by someone else to its last entity, and its record goes.
3. **Lines 327–333:** the created count grows, and a loaded sub-scene makes the cell loaded.
4. **Lines 334–345:** a failed sub-scene makes the cell failed, keeps the error, unloads the broken sub-scene and remembers the scene's revision.
5. **Lines 346–353:** a sub-scene that someone else started to unload is followed as if the streamer had.

Following others is the reason the poll reads states instead of trusting its own commands. A script may call the scene's unload on a sub-scene the streamer loaded. Loaded cells are not polled, so each evaluation checks them again against their sub-scenes.

### Failures and second tries

A failed cell stays in the cell map with its error, and `Evaluate` skips it, because it has a record. It would fail again, and a new try on every update would repeat the failure forever. The streamer tries again only when the cell's scene changes: a new import, or a repair by hand, raises the scene's :term[source revision]{id=source-revision}.

```cpp src="Strata/src/Strata/World/WorldStreamer.cpp#L368-L390"
bool WorldStreamer::RetryChangedFailures()
{
	// A changed scene publishes a content change (ReloadAsset): only then are the failed cells' sources compared.
	AssetManagerBase* assets = m_Scene.GetAssetManager();
	const uint64_t version = assets->GetContentVersion();
	if (m_FailedCells == 0 || version == m_FailureVersion)
		return false;
	m_FailureVersion = version;
	bool retry = false;
	for (auto it = m_Cells.begin(); it != m_Cells.end();)
	{
		if (it->second.Status == WorldCellStatus::Failed && assets->GetSourceRevisions(it->second.Scene).Current != it->second.FailedRevision)
		{
			it = m_Cells.erase(it);
			m_FailedCells--;
			m_Stats.StateVersion++;
			retry = true;
			continue;
		}
		++it;
	}
	return retry;
}
```

1. **Lines 372–373:** the asset manager's :term[content version]{id=content-version} is compared first; with no failed cells, or no new version, the function returns at once.
2. **Lines 379–385:** a failed cell whose scene revision differs from the failing one loses its record, and the next evaluation may start it again.

The test `A cell that fails to load is not retried until its scene changes` breaks one cell, waits for the failure, walks 30 frames and checks that the load count did not grow, then reloads the scene and expects one more load.

### Adoption and the world that changes

**Adoption** is the streamer taking over sub-scenes that already exist, so that it treats them like the cells it loaded itself. A :term[prepared start]{id=prepared-start} loads the wanted cells of the layers marked `LoadBeforeStart` before the first frame, and the editor adopts cells into a play copy of its scene. In `AdoptCells` the streamer visits each cell of the world, finds a sub-scene whose source is the cell's scene and takes it unless it is unloading or failed. It marks the cell loading or loaded by the sub-scene's state. Without adoption the streamer would load a second copy of every cell, or leave the first copy loaded forever.

The streamer also notices a reloaded World asset. It keeps a weak reference to the asset object that its tables were built from. When `GetAsset` returns another object, `RefreshWorld` rebuilds the per-layer cell lists and layer flags, applies the toggles that were remembered by name, adopts cells and sets the dirty flag.

### Asking it questions

Everything above is read by tools through a few queries. `GetStats` returns counts of wanted, loading, loaded, unloading, pinned and failed cells, the loads and unloads started, and the entities created and destroyed in the last update. It also returns the cells the last evaluation looked at and a `StateVersion` that changes whenever a cell's state does, so that a view rebuilds only then. `GetCellStates` lists every cell, `GetActiveCells` the ones the streamer holds, and `IsLoadedAround` tells a script whether all cells within a radius are loaded. `SetReloadCells` makes the editor's streamer read cell files as they are now, not from a cache.

:::example[The island, walking]
The Open World sample has a world of 64 m cells with three layers. Vegetation streams within 192 m, Wildlife within 128 m and Landmarks within 320 m. For Vegetation, $H$ is the larger of 32 m and 19.2 m, so 32 m, and the keep radius is 224 m. A player walking north with a view bias of 0.25 ranks a cell 150 m straight ahead at 150 − 48 = 102 m, and a cell 120 m to the side at 120 m. The cell ahead loads first although it is farther away.
:::

The editor's cell map draws these states while the island plays.

::figure{id=island-cells}

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Stream around the camera only | Small games and prototypes | One input to gather, no source list | Ground missing where a vehicle or a teleport needs it |
| A single threshold, no keep radius | Simple designs | One number to tune | A cell on a border loads and unloads on every frame |
| Evaluate on every frame | Simple update loops | No dirty flag to forget to set | A cost that grows with the world even while nothing moves |
| Start every wanted load at once | Designs without a limit | A full ring sooner on a fast machine | The nearest cells wait behind far ones, and the work comes in spikes |
| Rank by distance only | Designs without a facing | One input fewer | Cells ahead of a fast player arrive late |
| Stream by volumes the level designer draws | Engines with hand-placed streaming volumes | Exact control of which cells load where | Every area needs a volume, and sources that move freely stream nothing |

Streaming around several sources with a loading range, as Unreal Engine's World Partition does, is the idea Strata follows, with a keep radius, a total order and a cap added.

## How it is tested

The streaming suite, named in the command below, holds this page's tests, in `StrataTests/src/World/WorldStreamerTests.cpp` and `WorldStreamingTests.cpp`. The first file drives a streamer by hand, one frame at a time, and settles every started load before the next frame, so that decisions depend on the decisions alone. Its tests check the order, the hysteresis numbers, the idle cost, layers, pins, priorities, the entity budgets, failures, adoption and the physics reservation. One test walks a source around a world and compares the decisions with one worker thread and with many: they must be equal.

The second file runs the world system itself, through requests, layer toggles and a world packed in cooked cells. Other suites touch the streamer from the sides: the asset and coordinate tests of the world, `Editor.World`, `Editor.WorldCook` and the `Perf.World` tests that measure cost against budgets. Run the streamer's tests alone with:

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=World.Streaming
```

The runner takes the suite's name, so the same command with another name runs another suite.

## Changing it safely

The extension points are few. A new input to the ranking goes into `Candidate`, `want` and both sort rules of `Evaluate`. A new statistic goes into `WorldStreamingStats`, set in `Update` or `GetStats`. A new cell state goes into `WorldCellStatus` and into the polling.

- **Keep the order total.** Every new key of the ranking must end in the packed key. Two cells that tie make the result depend on how `std::sort` swaps them, and drives that should be identical then differ.
- **Never decide in the cell map's own order.** It is a hash map: sort the keys first, as the unload pass does. The test of one worker against many catches a slip only when the sources and the world expose it.
- **Stay cheap when idle.** A new input must be part of `SourcesMoved` or the dirty flag, or the streamer will not notice it. Nothing may walk every cell of the world on an update that evaluates nothing.
- **Request the asset, never hold it.** The rule on residency applies to the World asset and to every asset a change adds.
- **Stay on the main thread.** Work that takes time goes through the job system, and its result returns through the main thread's queue, never by calling the streamer from a worker.

Before you commit, run the suite above, the other world suites and, when a change can alter the cost of an update, the perf tests of worlds.

## Summary

- A source's wanted cells are those within its radius, and its kept cells are those within the radius plus H, the larger of half a cell and a tenth of the radius.
- One update starts at most four loads, ordered by priority, then biased distance, then key, with cells ahead ranking nearer by the view bias.
- An update asks for the asset, polls the cells in flight, refreshes, tries changed failures again and evaluates only when something changed or a source moved more than a centimetre.
- A cell is unloaded, loading, loaded, unloading or failed, follows its sub-scene, including one that someone else unloads, and a failed cell loads again only when its scene changes.
- A change to the streamer keeps the decisions in a total order, never decides in the hash map's order, holds no asset and costs nothing while nothing moves.

## Check yourself

1. A layer has cells of 64 m and a source has a radius of 100 m. A loaded cell lies 120 m from the source. What does the streamer do with it?

   - A. It unloads the cell, because 120 m is more than the radius.
   - B. It keeps the cell, because 120 m is within the keep radius.
   - C. It cancels the cell, because it is not wanted.

   :::answer{tests="wanted-set"}
   B. $H$ is the larger of 32 m and 10 m, so 32 m, and the keep radius is 132 m. The cell is not wanted any more, so the streamer starts no new load for it, but it holds a loaded cell inside the keep radius. A is wrong because the radius only decides what to start. C is wrong because a cancellation applies to a load in progress, and this one finished.
   :::

2. The radius is 100 m, the view bias is 0.25 and the cells P, Q and R start at the same priority. P is 60 m away straight ahead, Q is 50 m away at the side and R is 35 m away behind the source. R has a smaller key than P. In which order do they start?

   :::answer{tests="load-order"}
   R, P, Q. P ranks $60 - 0.25 \cdot 100 \cdot 1 = 35$ m, Q ranks 50 m and R ranks 35 m, because a cell behind has $a = 0$. P and R tie, and R's smaller key puts it first. All three start in one update, because the limit is four.
   :::

3. A source shifts by 5 mm on every frame in alternating directions for 600 frames, and no load or unload finishes in that time. How many evaluations run after the first?

   :::answer{tests="evaluate"}
   None. The move is below `c_SourceEpsilon` of 1 cm, nothing marks the streamer dirty and the source's other fields are the same, so `Update` returns after its checks. The cost of each frame is a check of the source, a poll of the cells in flight and a request for the World asset.
   :::

4. A script unloads the sub-scene of a loaded cell that the streamer holds, while the cell is still wanted. What happens?

   - A. The streamer keeps showing the cell as loaded until the source leaves.
   - B. The streamer follows the unload, then loads the cell again when the unload ends.
   - C. The streamer reports an error and stops streaming.

   :::answer{tests="cell-states"}
   B. Loaded cells are not polled, so the streamer notices at its next evaluation, once a source moves or something sets the dirty flag. That evaluation sees a loaded cell whose sub-scene is not loaded and marks it unloading. When the last entity is gone the record disappears, and the finished poll sets the dirty flag, so the next evaluation starts the load again. A and C are wrong: the streamer trusts the scene over its own record and raises no error for this.
   :::

5. A colleague replaces the sort of the candidates by a loop over the cell map that starts every wanted cell it meets, up to four. Which property is lost?

   :::answer{tests="change-safely"}
   The total order. The hash map's order is not defined, so two runs, or two machines, can start different cells first, and the test that compares one worker with many, and every drive comparison, can fail. The nearest cells no longer start first either.
   :::

## Exercises

1. **Basic.** Run the source jittering at the border of the page's first example and count the decisions with and without a keep radius.

   :::answer[Worked solution]{tests="wanted-set" solution="sketches/worlds-streamer-hysteresis.cpp"}
   The program applies the page's rule to the cell that spans x from 96 m to 128 m, for a source that alternates between 55.99 m and 56.01 m.

   ```cpp sketch="worlds-streamer-hysteresis.cpp"
   #include <algorithm>
   #include <cstdio>

   namespace
   {

   	constexpr double c_CellSize = 32.0;
   	constexpr double c_Radius = 40.0;

   	// Counts the loads and unloads of the cell that spans x from 96 to 128 for a source that jitters at its border.
   	int CountDecisions(double hysteresis)
   	{
   		bool loaded = false;
   		int decisions = 0;
   		for (int frame = 0; frame < 100; frame++)
   		{
   			const double x = frame % 2 == 0 ? 55.99 : 56.01;
   			const double distance = std::max(3.0 * c_CellSize - x, 0.0);
   			if (!loaded && distance <= c_Radius)
   			{
   				loaded = true;
   				decisions++;
   			}
   			else if (loaded && distance > c_Radius + hysteresis)
   			{
   				loaded = false;
   				decisions++;
   			}
   		}
   		return decisions;
   	}

   }

   int main()
   {
   	std::printf("decisions with no keep ring: %d\n", CountDecisions(0.0));
   	std::printf("decisions with a keep ring of 16 m: %d\n", CountDecisions(std::max(c_CellSize * 0.5, 0.1 * c_Radius)));
   	return 0;
   }
   ```

   ```text output-of="worlds-streamer-hysteresis.cpp"
   decisions with no keep ring: 99
   decisions with a keep ring of 16 m: 1
   ```

   1. **Line 17:** the source alternates every frame, the jitter of the example.
   2. **Lines 19–23:** a cell that is not loaded loads when it is within the radius.
   3. **Lines 24–28:** a loaded cell unloads only beyond the radius plus the keep distance, which is 0 in the first call.
   4. **Line 38:** the second call uses the page's formula, 16 m here.

   With no keep ring the cell loads and unloads on every frame after the first, 99 decisions. With the ring the cell loads once and stays.
   :::

2. **Medium.** Two sources want the same cell. A has priority 0 and the cell is 30 m away from it. B has priority 5 and the cell is 80 m away. Which priority and distance does the candidate keep, and what does that mean for its rank?

   :::answer[Worked solution]{tests="load-order"}
   The first source to want the cell adds the candidate. The second one calls the merge function: B has the higher priority, so the candidate takes priority 5 and distance 80 m at once, although 80 m is larger than 30 m. The candidate ranks among priority 5 cells, ahead of every cell of priority 0, whatever their distances. The `High` flag is the union of the two sources' flags.
   :::

3. **Medium.** Trace it yourself: find where the streamer keeps a loaded cell while its source is past the radius and inside the keep radius, and show it in a debugger.

   :::answer[Worked solution]{tests="evaluate"}
   The decision is in `WorldStreamer::Evaluate` in `Strata/src/Strata/World/WorldStreamer.cpp`, near lines 462 to 475: the keep radius is the radius plus the larger of half the cell size and a tenth of the radius. Set a breakpoint on `m_Keep.insert(key);` and run the test that swings the source, in `StrataTests/src/World/WorldStreamerTests.cpp`. The cell enters the keep set while its distance lies between the radius and the keep radius, and the unload pass at line 511 does not list it. Change the cell size or the radius in the test, and the decisions change where the keep radius passes the cell.
   :::

## Where it lives in Strata

- `Strata/src/Strata/World/WorldStreamer.h` and `WorldStreamer.cpp`: `WorldStreamer`, `WorldStreamingSource`, `WorldCellStatus`, `WorldCellState`, `WorldActiveCell` and `WorldStreamingDecision`.
- `Strata/src/Strata/World/WorldStreamingSystem.cpp`: the world system that gathers the sources and calls `Update` in Play and Simulate.
- `StrataEditor/src/Editor/EditorWorld.h` and `EditorWorld.cpp`: the editor's streamer for Edit.
- `Strata/src/Strata/Scene/SceneServices.h`: `WorldStreamingStats`, `IWorldStreaming`.
- Tests: the streaming suite in `StrataTests/src/World/WorldStreamerTests.cpp` and `WorldStreamingTests.cpp`.
- Settings: the layers' streaming distances and cell sizes in the World asset, and the distance scale of the world component.

## Further reading

- Epic Games, documentation of World Partition and streaming sources in Unreal Engine, cited without a link: streaming around several points with a loading range (intermediate).
- Robert Nystrom, "Game Programming Patterns", chapter "Spatial Partition", on gameprogrammingpatterns.com: why a grid makes nearby queries cheap (beginner).
- Jason Gregory, "Game Engine Architecture", the chapter on resource management and streaming, cited without a link: how engines load content as the player moves (advanced).
