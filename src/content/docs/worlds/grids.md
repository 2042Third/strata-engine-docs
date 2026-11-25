---
id: worlds/grids
title: "Grids, keys and layers"
description: "The data of a world: layers, cells, the packed key, the document and its rules, and the grid arithmetic that finds the cell of a point."
kind: internals
size: M
tracks: [E]
needs: [assets/handles-meta, world/serialization, worlds/why-streaming]
time: 50
learn:
  - id: cell-key
    text: compute the cell and the packed key of a point, also for negative positions
  - id: layers
    text: choose the cell sizes and streaming distances of a world's layers
  - id: validate
    text: name the rules that make Strata refuse a world document
  - id: cell-files
    text: find the file and the handle of a cell
since: 0.8.0
status: final
---

A world is too big to keep in memory, so Strata cuts it into cells and loads the ones near the player. This page covers the data that makes the cutting possible and the arithmetic on it.

The **world asset** is the document, stored as a `.stworld` file, that names the :term[persistent scene]{id=persistent-scene}, the layers and the cells that hold content. It answers "which cell holds this point?" with one division and one lookup, never a search. Which cells load is the job of [the streamer](streamer.md). The cook that measures cells is on [the physics and scripts page](physics-scripts.md), and the writing of cell files is on [the editor's worlds page](../editor/worlds.md).

## The problem and how engines solve it

Think of a game map ten kilometres wide. The player stands somewhere on it, and the engine must find the pieces of the map near that spot, every frame. Your first idea may be to place boxes by hand: an artist draws a volume around each village, and the engine loads the village when the player enters the box. That works for a few places. It fails when the map grows, because every query walks all the boxes, boxes overlap, and each new area needs a person to draw it.

A second idea is a tree of squares that splits where the map is busy. A crowded town gets many small squares and a desert gets one large square. This saves memory on uneven maps, but a square that splits changes its name, and everything that pointed at it must change too. A lookup also walks down the tree level by level.

A third idea is a uniform grid: square cells of one size, laid side by side from a corner. Finding the cell of a point is school arithmetic. Divide the distance from the corner by the cell size, once for each axis. With 64 m cells, a point 200 m east and 70 m south of the corner lies in column 3 (200 / 64 = 3.1) and row 1 (70 / 64 = 1.1). No tree, no search, and a cell never changes its name.

A uniform grid wastes space where the map is empty. Strata therefore keeps a sparse grid: only cells that have content are listed, and a lookup that finds nothing means "empty here". A hash map from the cell's number to its entry keeps the lookup constant in time ([data structures](../basics/data-structures.md)).

One cell size cannot serve everything. Mountains must be visible from far away, and 256 m cells suit them. Bushes and crates matter only near the player, and 64 m cells suit them. A world therefore has layers, and each layer is its own grid with its own cell size and its own streaming distance. Terrain streams far in large cells, props stream near in small ones.

## The map

The grid arithmetic does not depend on the asset, so the streamer, the editor's cell map and the tests all use it. The asset holds the document, its rules and the lookup.

```mermaid caption="The files of the world data. The grid file holds the key and the arithmetic, the asset file holds the document and its rules, and the loader, the streamer and the editor call them." alt="A diagram with five boxes. The grid file feeds the asset file, and the asset file feeds the loader registration. The streamer and the editor call into both the grid file and the asset file."
flowchart LR
  Grid["WorldGrid.h and WorldGrid.cpp: WorldCellKey, CellAt, CellBounds, Distance"]
  Asset["WorldAsset.h and WorldAsset.cpp: WorldData, FromJson, Validate, FindCell"]
  Reg["WorldRegistration.cpp: the loader"]
  Streamer["WorldStreamer.cpp"]
  Editor["EditorWorld.cpp and CellMap.cpp"]
  Grid --> Asset
  Asset --> Reg
  Streamer --> Grid
  Streamer --> Asset
  Editor --> Grid
  Editor --> Asset
```

The engine files are in `Strata/src/Strata/World/`. The editor's files are in `StrataEditor/src/Editor/` and `StrataEditor/src/UI/`. All of it runs on the :term[main thread]{id=main-thread}, where the scene lives.

## The contract

Callers of the world data may rely on these rules. Each has a reason.

- **A world is valid or it does not exist.** `WorldData::FromJson` and `WorldData::Validate` refuse bad data with a reason and never assert. The reason: a `.stworld` file is untrusted input, as [robustness](../assets/robustness.md) explains.
- **Cells are squares on the ground.** A cell has a size in X and Z only and reaches from minus to plus infinity in Y, so a point's height never changes its cell.
- **Cells include their lower edges.** A point exactly on a boundary belongs to the cell above and to the right of it. Without a rule, two cells would both claim the boundary.
- **Layers are named by ID inside the data.** Cells and keys store the layer's ID (1 to 255), and the name is a label. The reason: renaming a layer then changes one field, not every cell.
- **A cell's scene is its own.** A cell never uses the persistent scene as its scene, and two cells never share a scene.
- **Entity IDs are unique across the cells and the persistent scene.** The cook fails and names the IDs that two scenes share. The reason: all loaded cells live in one scene together, and an ID must name one entity.

:::rule
`AGENTS.md` says that bad data returns an error and logs, and never asserts. The world document follows it: `Validate` returns `false` with a message. See [the conventions page](../core/conventions.md).
:::

## A toy version

Here is the arithmetic without the engine: a key type, a cell lookup and a function that packs a key into 64 bits. The program shows the one place where beginners go wrong, which is the rounding of negative numbers.

The **cell key** is the number that names a cell. It holds the layer's ID and the cell's column X and row Z, packed into one 64-bit :term[integer]{id=integer}. The layer takes the top 8 bits, and X and Z take 28 bits each, so 8 + 28 + 28 = 64. X and Z can be negative, and a bit field has no sign, so each gets 2^27 (134,217,728) added first. That moves the range from −134,217,727 to 134,217,727 onto 1 to 268,435,455, all positive.

```cpp sketch="worlds-grids-toy.cpp"
#include <cmath>
#include <cstdint>
#include <cstdio>

struct CellKey
{
	uint8_t Layer = 0;
	int32_t X = 0;
	int32_t Z = 0;
};

// Floor, not truncation: -0.0003 cells is cell -1, not cell 0.
int32_t ToCell(double offset, double cellSize)
{
	return static_cast<int32_t>(std::floor(offset / cellSize));
}

CellKey CellAt(uint8_t layer, double cellSize, double originX, double originZ, double x, double z)
{
	return CellKey { layer, ToCell(x - originX, cellSize), ToCell(z - originZ, cellSize) };
}

// The layer goes in the top 8 bits, then X and Z shifted by 2^27 into 28 bits each.
uint64_t Pack(const CellKey& key)
{
	const int64_t offset = int64_t(1) << 27;
	const uint64_t x = static_cast<uint64_t>(key.X + offset);
	const uint64_t z = static_cast<uint64_t>(key.Z + offset);
	return (uint64_t(key.Layer) << 56) | (x << 28) | z;
}

void Print(const char* label, const CellKey& key)
{
	std::printf("%s: layer %d, cell (%d, %d), key 0x%016llx\n", label, key.Layer, key.X, key.Z, static_cast<unsigned long long>(Pack(key)));
}

int main()
{
	// A layer of 32 m cells whose grid starts at (200, -100).
	Print("origin", CellAt(3, 32.0, 200.0, -100.0, 200.0, -100.0));
	Print("just below", CellAt(3, 32.0, 200.0, -100.0, 199.99, -100.01));
	Print("far", CellAt(3, 32.0, 200.0, -100.0, 264.0, -36.0));
}
```

```text output-of="worlds-grids-toy.cpp"
origin: layer 3, cell (0, 0), key 0x0380000008000000
just below: layer 3, cell (-1, -1), key 0x037ffffff7ffffff
far: layer 3, cell (2, 2), key 0x0380000028000002
```

1. **Line 15:** `std::floor` rounds toward minus infinity, so −0.0003 cells becomes cell −1. Cutting off the decimals would give 0 and put the point in the wrong cell.
2. **Lines 18–21:** the cell is the layer's ID, with the floor of each offset from the grid's corner divided by the cell size.
3. **Lines 24–30:** adding 2^27 makes X and Z positive, and both then fit 28 bits.
4. **Line 29:** `<<` shifts bits to the left: the layer moves by 56 bits and X by 28, so the three fields cannot overlap.
5. **Lines 40–42:** three points of one layer: the corner, a point slightly below it and a point two cells away.

:::example
The first point lies exactly on the corner, so both offsets are 0 and the cell is (0, 0). Each :term[hexadecimal]{id=hexadecimal} digit holds 4 bits, so the layer takes two digits and each 28-bit coordinate seven. Its X is 0 + 2^27 = 0x8000000, and its Z is the same, so the key is layer 3 (`03`), then `8000000`, then `8000000`: 0x0380000008000000.

The second point lies 0.01 m below the corner in X and in Z. Both offsets are negative and small, so the floor gives −1, and −1 + 2^27 = 0x7FFFFFF, which makes the key 0x037FFFFFF7FFFFFF. Cutting off the decimals would give cell (0, 0), the neighbour across the corner, which does not hold the point.
:::

The packed form is also an order: 0x7FFFFFF (X = −1) is less than 0x8000000 (X = 0), and the layer comes before X, which comes before Z. Sorting the numbers sorts the cells by (layer, X, Z), the order the streamer sorts by.

## The real code

Now the engine's version, in the order the data flows. The structures come first.

```cpp src="Strata/src/Strata/World/WorldAsset.h#L21-L29"
struct WorldLayer
{
	uint8_t ID = 1;   // 1-255, unique in the world
	std::string Name; // Unique, non-empty, without control characters, commas or surrounding spaces (sources list layers by name)
	float CellSize = 256.0f;          // Side of the cells' squares, world units
	float StreamingDistance = 1024.0f; // Cells within this distance of a source load (WorldComponent::DistanceScale scales it)
	bool EnabledByDefault = true;     // Whether the layer streams until a game disables it
	bool LoadBeforeStart = false;     // Whether a game's loads wait for its cells around the sources before the world starts
};
```

A layer has an ID, a name, a cell size and a streaming distance, plus two flags. `EnabledByDefault` says whether the layer streams until a game disables it. `LoadBeforeStart` says whether the game waits for the cells around the player before it starts. The name may not contain a comma, because a streaming source lists its layers in one comma-separated string.

```cpp src="Strata/src/Strata/World/WorldAsset.h#L32-L40"
struct WorldCell
{
	uint8_t Layer = 1;
	int32_t X = 0;
	int32_t Z = 0;
	AssetHandle Scene = UUID::Null();

	WorldCellKey GetKey() const { return WorldCellKey { Layer, X, Z }; }
};
```

A cell lists a layer ID, a column, a row and the handle of its scene. Only cells with content exist in the list. The toy has no document, no limits and no list of layers, and the real data has all three.

The :term[loader]{id=loader} registered for `.stworld` files hands the :term[bytes]{id=byte} to `WorldAsset::Deserialize`, which parses the text, and `WorldAsset::FromJson` checks the :term[header]{id=header}, which must read `{"Strata": {"Format": "World", "Version": 1}}`. Then `WorldData::FromJson` reads the `World` object field by field. A small helper names the field it was reading when it fails, so a message says "Layer 2" and not only "bad number".

### The document and its limits

A small world file has this shape, with a header and a content object as in [the scene format](../world/serialization.md).

```json
{
	"Strata": { "Format": "World", "Version": 1 },
	"World": {
		"Name": "Island", "PersistentScene": "3A8A714892F1CC38",
		"GridOrigin": [0.0, 0.0],
		"Layers": [{ "ID": 1, "Name": "Vegetation", "CellSize": 64.0, "StreamingDistance": 192.0, "EnabledByDefault": true, "LoadBeforeStart": true }],
		"Cells": [{ "Layer": 1, "X": -5, "Z": 1, "Scene": "7FF764CA19D5ADA7" }]
	}
}
```

The `GridOrigin` is the **grid origin**: the X and Z position of the corner of cell (0, 0), shared by every layer. No command and no panel changes it: `world.create` takes none, and `world.info` only reports it. A new origin therefore appears only when someone edits the `.stworld` by hand, and then the square of every cell moves. The feature test's world sits at (200, 200).

The limits are constants of `WorldData`:

| Limit | Value | What it bounds |
| --- | --- | --- |
| Layers | 1 to 32 | The list that `Validate` compares layer by layer. |
| Cells | 2^20 (1,048,576) | The lists the loader builds from untrusted data. |
| Cell size | 1 to 65,536 m | The side of a square. |
| Streaming distance | 0 to 1,000,000 m | How far a layer's cells load around a source. |
| Extent | 1,000 km | Every cell lies within this distance of the origin, in X and in Z. |
| Supported extent | 20 km | Float positions lose precision beyond it, and the cook warns about cells there. |

The key's coordinate limit of 2^27 − 1 is far above what the extent allows even for 1 m cells (1,000,000 columns), so a valid world always packs.

### Validate

`Validate` checks every rule, whether the data came from a file or from code. Look at how it treats one layer, and notice that each failure starts with the layer's name.

```cpp src="Strata/src/Strata/World/WorldAsset.cpp#L388-L393" from="if (layer.Name.empty() ||" to="c_MinCellSize, c_MaxCellSize));" symbol="WorldData::Validate"
if (layer.Name.empty() || layer.Name.size() > c_MaxNameLength || HasControlCharacter(layer.Name))
	return Fail(outError, fmt::format("{}: the name must have 1 to {} characters and no control characters", what, c_MaxNameLength));
if (layer.Name.find(',') != std::string::npos || layer.Name.front() == ' ' || layer.Name.back() == ' ')
	return Fail(outError, fmt::format("{}: the name must not contain commas or start or end with a space (sources list layers separated by commas)", what));
if (!std::isfinite(layer.CellSize) || layer.CellSize < c_MinCellSize || layer.CellSize > c_MaxCellSize)
	return Fail(outError, fmt::format("{}: CellSize must be from {} to {} m", what, c_MinCellSize, c_MaxCellSize));
```

The name must have 1 to 64 characters and no control characters. It must not contain a comma or start or end with a space. The cell size must be a finite number from 1 to 65,536. A person who edits a file by hand sees which entry to fix.

The same function then checks the cells. Look at what it computes before it accepts a cell.

```cpp src="Strata/src/Strata/World/WorldAsset.cpp#L419-L423" from="const WorldCellSquare square = WorldGrid::CellBounds" to="if (!keys.insert(cell.GetKey().Pack()).second)" symbol="WorldData::Validate"
const WorldCellSquare square = WorldGrid::CellBounds(*layer, GridOrigin, cell.X, cell.Z);
const double farthest = std::max({ std::abs(square.Min.x), std::abs(square.Min.y), std::abs(square.Max.x), std::abs(square.Max.y) });
if (farthest > c_MaxExtent)
	return Fail(outError, fmt::format("{}: it lies {:.0f} km from the origin, beyond the {:.0f} km a world may reach", what, farthest / 1000.0, c_MaxExtent / 1000.0));
if (!keys.insert(cell.GetKey().Pack()).second)
```

The code asks the grid math for the cell's square and takes the corner farthest from the origin. If it lies beyond 1,000 km, the world is refused with the distance in the message. The packed key then goes into a set, so a cell listed twice is refused. More rules follow: the cell's scene must exist, must not be the persistent scene and must belong to no other cell. Layer IDs and names must be unique, and an index may list only cells that exist, each once, with finite bounds.

### Lookup and memory

`WorldAsset` builds two hash maps when it is created: one from packed cell keys to positions in the cell list, and one for the index entries. A lookup packs the key and asks the map.

```cpp src="Strata/src/Strata/World/WorldAsset.cpp#L615-L621" symbol="WorldAsset::FindCell"
int32_t WorldAsset::FindCell(const WorldCellKey& key) const
{
	if (std::abs(key.X) > WorldCellKey::c_MaxCoordinate || std::abs(key.Z) > WorldCellKey::c_MaxCoordinate)
		return -1;
	const auto it = m_CellIndex.find(key.Pack());
	return it != m_CellIndex.end() ? it->second : -1;
}
```

The size test comes first because `Pack` asserts that its coordinates fit, and a caller may hand in any number. A result of −1 means the cell has no content, the normal case in a sparse grid.

The asset reports its memory to the residency budgets, as [residency](../assets/residency.md) describes. `GetMemoryUsage` counts the lists and the nodes and buckets of both maps, because a world of a million cells would otherwise look small while its maps are large.

### The grid arithmetic

The offset from the origin, divided by the cell size, goes through a function that floors it and clamps the result.

```cpp src="Strata/src/Strata/World/WorldGrid.cpp#L22-L28" from="const double cell = std::floor(offset / cellSize);" to="return static_cast<int32_t>(cell);" symbol="ToCellCoordinate"
const double cell = std::floor(offset / cellSize);
// Positions far outside any world (and NaN) clamp to the outermost cells a key can name.
if (!(cell >= -static_cast<double>(WorldCellKey::c_MaxCoordinate)))
	return -WorldCellKey::c_MaxCoordinate;
if (cell > static_cast<double>(WorldCellKey::c_MaxCoordinate))
	return WorldCellKey::c_MaxCoordinate;
return static_cast<int32_t>(cell);
```

The first test is written `!(cell >= -max)` so that :term[NaN]{id=nan}, for which every comparison is false, takes the clamp. The toy skipped the clamp. All of the arithmetic runs in `double`, because a float has 24 bits of precision, so at 20 km its steps are already about 2 mm wide, as [numbers](../basics/numbers.md) explains.

```cpp src="Strata/src/Strata/World/WorldGrid.cpp#L33-L39" symbol="WorldCellKey::Pack"
uint64_t WorldCellKey::Pack() const
{
	ST_CORE_ASSERT(std::abs(X) <= c_MaxCoordinate && std::abs(Z) <= c_MaxCoordinate, "Cell ({}, {}) is outside what a key can pack", X, Z);
	const uint64_t x = static_cast<uint64_t>(static_cast<int64_t>(X) + c_CoordinateOffset) & c_CoordinateMask;
	const uint64_t z = static_cast<uint64_t>(static_cast<int64_t>(Z) + c_CoordinateOffset) & c_CoordinateMask;
	return (static_cast<uint64_t>(Layer) << 56) | (x << 28) | z;
}
```

`Pack` matches the toy, with the mask `c_CoordinateMask`, which keeps each value within 28 bits so that a bad value cannot spill into its neighbour in a build without asserts. The last function measures how far a point is from a cell's square.

```cpp src="Strata/src/Strata/World/WorldGrid.cpp#L68-L73" symbol="WorldGrid::Distance"
double Distance(const WorldCellSquare& square, const glm::dvec3& point)
{
	const double dx = std::max({ square.Min.x - point.x, 0.0, point.x - square.Max.x });
	const double dz = std::max({ square.Min.y - point.z, 0.0, point.z - square.Max.y });
	return std::sqrt(dx * dx + dz * dz);
}
```

Along each axis the gap is 0 when the point lies between the edges, and the distance to the nearest edge otherwise. The two gaps are the legs of a right triangle, so the distance is its hypotenuse. A point inside gets 0, whatever its height. The streamer compares this distance with a layer's streaming distance.

## Layers in practice

The Open World sample, `Samples/OpenWorld/Assets/Worlds/Island.stworld`, has three layers with 64 m cells and different distances: Vegetation (ID 1) at 192 m, Wildlife (ID 2) at 128 m and Landmarks (ID 3) at 320 m. Its origin is (0, 0). One of its cells has X = −5 and Z = 1, so its square runs from (−320, 64) to (−256, 128).

How many cells lie within 192 m of a player in the middle of one cell? Along an axis the nearest edge of cell k is 64 k − 32 m away, so cells −3 to 3 qualify (160 m, while cell 4 is 224 m away). The rows 0, 1 and 2 cells out hold seven cells each, and the corner of row 2 is sqrt(160² + 96²) = 186.6 m away. Rows 3 out hold five cells, because their corners are 226 m away. The total is 7 + 4 × 7 + 2 × 5 = 45 cells.

Now take a hypothetical world whose mountains must show from 1,024 m. In 64 m cells, a circle of that radius holds π × 16² ≈ 804 cells, and more with the cells its edge cuts. In 256 m cells it holds a few dozen. Props stay in a second layer of 64 m cells at 192 m. The number of loaded cells grows with the square of the distance over the size, and that is why a world mixes sizes.

:::why
One cell size for everything forces a choice between two failures: tiny cells that load hundreds of entries for far terrain, or huge cells that load whole villages of props nobody can see. Layers cost one more table to keep, and each cell belongs to one layer, so an object must live in the layer that fits its biggest use.
:::

## Cell files and derived handles

A cell's scene is a normal `.stscene` document. The editor creates it at `<world folder>/<World>/<Layer>/<X>_<Z>.stscene`. Cell (−5, 1) of the layer Vegetation in the world Island is `Worlds/Island/Vegetation/-5_1.stscene` when the world file lies in `Worlds`.

The handle of that scene is not random. `EditorWorld::DeriveCellScene` calls `DeriveSubAssetHandle(world, "Cell/<layer ID>/<X>/<Z>")`, as [handles](../assets/handles-meta.md) explains for sub-assets. The same world and key always give the same handle. The reason: an undo step can know the cell's handle before the file exists, and a restored cell gets its old handle back. The key uses the layer's ID, so renaming the layer keeps every handle.

## The index and the references

The **index** is the cook's measurement of each cell, stored in the document so that the streamer can plan without loading cells. For each cell it holds the cell document's content stamp at the time of measuring, the entities, the physics bodies, the bounds and the stored bytes that loading the cell would load. The index as a whole adds `MaxBodiesInRadius` and `PersistentBodies`. The cook fills them, and [the physics and scripts page](physics-scripts.md) explains how.

`AssetDependencies::Scan` lists the persistent scene and the scene of every cell as the world's references, so an export ships them all. A load stops at scenes, as [references](../assets/references.md) describes for closures. The persistent scene references the world, and the world references the cells, but loading the persistent scene never loads a cell. The streamer chooses cells later.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Hand-placed streaming volumes | Unreal Engine's level streaming volumes | Total control of what loads where | A person draws each volume; every query walks all volumes |
| A tree of squares that splits | Terrain :term[renderers]{id=renderer}, as Ericson describes | Fewer cells in empty or flat areas | Cells that rename when they split; a walk down the tree per lookup |
| A dense array of every cell | Simple tile games | No hash map, the fastest lookup | Memory for empty cells: up to 2^20 entries for a small world |
| One cell size for the world | Small open worlds | One grid, one rule | Terrain and props cannot both stream well |

Unreal Engine's World Partition runs several grids of different cell sizes, the closest relative of layers. Sources are in Further reading.

## How it is tested

The World.Asset suite in `StrataTests/src/World/WorldAssetTests.cpp` has four test cases for this page. The first round-trips a world through :term[JSON]{id=json} and bytes and finds cells by key. The second gives every validation rule a bad world and checks the reason. The third feeds truncated and garbage bytes to the loader and expects errors, never a crash. The fourth checks the grid math with an origin of (200, −100) and 32 m cells: negative positions, NaN, `Pack` and `Unpack` round trips, key order and distances.

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=World.Asset
```

The command runs only the cases of that suite.

## Changing it safely

- Add a new rule to `Validate`, with a test case that gives a bad world and checks the reason. `WorldData::FromJson` checks only the shape of each field and then calls `Validate`, so one rule there guards files and code alike.
- Never change the key's layout. Keys order the streamer's cells and index the hash maps, and a changed layout changes both silently. A new layout needs a new version of the document.
- Keep the arithmetic in `double` and keep the lower edge inside the cell. A cell moved by a rounding slip loads its neighbour's content.
- Never read a cell's position from a layer name or a :term[file path]{id=path}: the key holds it.
- Run `ctest --preset windows-debug -R World` after a change, and all tests before a commit.

## Summary

- A cell key packs the layer, the column and the row into 64 bits: 8, 28 and 28, with 2^27 added to the coordinates, so sorted keys sort by (layer, X, Z).
- A layer is a grid with its own cell size and streaming distance, so that terrain streams far in large cells and props near in small ones.
- `FromJson` and `Validate` refuse bad worlds with a reason: layers, names, sizes, extent, duplicate cells and shared scenes.
- A cell's file lies in the world's folder under its layer and coordinates, and its handle derives from the world and the key.

## Check yourself

1. A layer has ID 2 and 64 m cells, with the grid origin at (0, 0). What is the packed key of the cell that holds the point (−10, 5, 130)?

   :::answer{tests="cell-key"}
   X is floor(−10 / 64) = −1 and Z is floor(130 / 64) = 2. The offset coordinates are 0x7FFFFFF and 0x8000002, so the key is 0x027FFFFFF8000002.
   :::

2. A programmer replaces `std::floor` by a cast to an integer. For 32 m cells and a point at X = −0.5, which cell does each give? (a) Both give cell 0. (b) The cast gives 0 and the floor gives −1. (c) The cast gives −1 and the floor gives 0.

   :::answer{tests="cell-key"}
   Answer (b). A cast cuts toward zero, so −0.0156 becomes 0, while the floor rounds toward minus infinity and gives −1. Answer (a) forgets the negative side, and answer (c) swaps the two.
   :::

3. Which of these changes does `Validate` refuse? (a) A layer named "Hills, Low". (b) A cell whose scene is the persistent scene. (c) Two layers with different names and equal cell sizes.

   :::answer{tests="validate"}
   (a) and (b) are refused: names must not contain commas, and a cell's scene is never the persistent scene. (c) is allowed, as the Island world shows with three layers of 64 m cells.
   :::

4. Where does the file of cell (3, −2) of the layer Props in the world Hills lie, when Hills.stworld is in Worlds?

   :::answer{tests="cell-files"}
   At `Worlds/Hills/Props/3_-2.stscene`. Its handle derives from the world's handle and the text `Cell/<layer ID>/3/-2`.
   :::

5. A terrain layer streams at 1,024 m. Should its cells be 64 m or 256 m, and why?

   :::answer{tests="layers"}
   256 m. A circle of radius 1,024 m covers about 50 cells of 256 m but more than 800 of 64 m, so larger cells keep the number of loaded cells low.
   :::

## Exercises

1. **Basic.** Write a function `Distance` that returns the distance on the ground from a point to a cell's square. Test it on the square from (264, −132) to (296, −100) with a point inside, a point 4 m east of the edge and a point beyond the corner.

   :::answer[Worked solution]{tests="cell-key" solution="sketches/worlds-grids-distance.cpp"}
   Along each axis the gap is the largest of three numbers: the point's distance below the minimum, 0 and the point's distance above the maximum. The gaps join as the legs of a right triangle.

   ```cpp sketch="worlds-grids-distance.cpp"
   #include <algorithm>
   #include <cmath>
   #include <cstdio>

   double Distance(double minX, double minZ, double maxX, double maxZ, double x, double z)
   {
   	const double dx = std::max({ minX - x, 0.0, x - maxX });
   	const double dz = std::max({ minZ - z, 0.0, z - maxZ });
   	return std::sqrt(dx * dx + dz * dz);
   }

   int main()
   {
   	// The square of cell (2, -1) of a layer of 32 m cells whose grid starts at (200, -100).
   	std::printf("inside: %.1f\n", Distance(264.0, -132.0, 296.0, -100.0, 270.0, -110.0));
   	std::printf("beside: %.1f\n", Distance(264.0, -132.0, 296.0, -100.0, 300.0, -100.0));
   	std::printf("corner: %.1f\n", Distance(264.0, -132.0, 296.0, -100.0, 299.0, -96.0));
   }
   ```

   ```text output-of="worlds-grids-distance.cpp"
   inside: 0.0
   beside: 4.0
   corner: 5.0
   ```

   1. **Lines 7–8:** the gap on each axis, 0 inside the edges.
   2. **Line 9:** the distance from the two gaps, 3 and 4 at the corner, so 5.
   :::

2. **Medium.** Make a world with `world.create`, then tune it with `world.setLayers`: one layer Terrain with 256 m cells that streams at 1,024 m and loads before the game starts. Why does the command work now and refuse later?

   :::answer[Worked solution]{tests="layers"}
   Create the world with `{"path": "Worlds/Hills", "cellSize": 64}`. Then run `world.setLayers` with `{"world": "Worlds/Hills", "layers": [{"id": 1, "name": "Terrain", "cellSize": 256, "streamingDistance": 1024, "loadBeforeStart": true}]}`; [the commands page](../editor/commands.md) shows how to run a command. A world without cells has nothing to move. Once layer 1 has cells, a new cell size would change the square of every cell, so the command refuses unless `deleteCells` is true, which moves those cells to the trash.
   :::

3. **Hard.** Trace it yourself. Move an entity of an open world in the editor with a breakpoint in `WorldGrid::CellAt`, find where the floor division and the key come from, then search for the other callers of `CellAt`.

   :::answer[Worked solution]{tests="cell-key"}
   The function is `WorldGrid::CellAt` in `Strata/src/Strata/World/WorldGrid.cpp`, and the editor reaches it through `EditorWorld::GetCellAt` in `StrataEditor/src/Editor/EditorWorld.cpp`. The breakpoint shows the offsets and `ToCellCoordinate` flooring them. A search for `CellAt` also finds the streamer's squares around a source in `Strata/src/Strata/World/WorldStreamer.cpp` and the cell map in `StrataEditor/src/UI/CellMap.cpp`.
   :::

## Where it lives in Strata

- `Strata/src/Strata/World/WorldGrid.h` and `WorldGrid.cpp`: `WorldCellKey`, `CellAt`, `CellBounds`, `Distance`.
- `Strata/src/Strata/World/WorldAsset.h` and `WorldAsset.cpp`: `WorldData`, `WorldLayer`, `WorldCell`, `WorldIndex`, `FromJson`, `Validate`, `FindCell`, `GetMemoryUsage`.
- `Strata/src/Strata/World/WorldRegistration.cpp`: the loader of `.stworld` bytes.
- `StrataEditor/src/Editor/EditorWorld.cpp`: `DeriveCellScene` and the cell file path.
- `StrataTests/src/World/WorldAssetTests.cpp`: the World.Asset suite.
- Commands: `world.create`, `world.info`, `world.setLayers`.

## Further reading

- Unreal Engine documentation, "World Partition" and "Level Streaming Volumes" (intermediate): runtime grids and volumes, the nearest relatives of layers and hand-placed volumes.
- Christer Ericson, "Real-Time Collision Detection", the chapter on spatial partitioning (advanced): uniform grids, trees of squares and their costs.
- David Goldberg, "What every computer scientist should know about floating-point arithmetic" (advanced): why positions far from the origin lose precision.
