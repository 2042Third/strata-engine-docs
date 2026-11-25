---
id: physics/collision-layers
title: "Collision layers"
description: "How Strata decides which bodies collide and which a query sees: the project's table of 32 layers, its filter bits and how a change reaches the world."
kind: internals
size: M
tracks: [E]
needs: [physics/building-bodies, world/projects-settings]
time: 70
learn:
  - id: predict-pair
    text: predict, for any two layers, whether their bodies collide and whether a query sees them
  - id: filter-bits
    text: compute the category and mask bits that a shape on a layer receives from the table
  - id: runtime-path
    text: trace how a change of the table reaches the physics world, from the project file and from a script
  - id: ghost-layer
    text: create a Ghost layer with the command that sets the project's collision layers
since: 0.5.0
status: final
---

A game must say which bodies may collide and which bodies a query may see. A ball bounces on the floor. A ghost box falls through the balls but lands on the floor. A ray fired from the player still hits the ghost.

Strata answers with collision layers: each :term[rigid body]{id=rigid-body} and each character controller is on one of 32 layers, and a table decides which layers collide. This page follows the table from the project's file to the filter that the physics library keeps for each shape. It does not teach how settings sections work ([Project settings](../world/projects-settings.md)), how queries use layer masks ([Physics queries](../physics/queries.md)) or how a game uses layers ([Physics in a game](../make/physics.md)).

## The problem and how engines solve it

Open the Physics Playground and press play. Balls pour into a pit, and ghost boxes fall beside them. The ghosts sink through the balls but land on the floor. Physics must know that this pair of bodies passes through each other while every other pair collides.

Engines use four approaches. The first is a **per-pair ignore list**: each body keeps a list of the bodies it ignores. With 100 balls and 20 ghosts, that is 2,000 pairs to list, and every body spawned later needs its own entries. The list is exact but grows with the number of bodies, and a forgotten entry is a bug that nothing reports.

The second approach is a **group number**: two shapes with the same positive group always collide, and two with the same negative group never do. Groups suit the limbs of one character. They cannot say that ghosts pass through balls but not through the floor.

The third approach gives every shape two :term[bit masks]{id=bit-mask}. The **category bits** name what the shape is, one bit per kind; the mask bits name the kinds it accepts. Shape A and shape B collide only if A's mask holds B's category and B's mask holds A's category.

The 120 bodies of the example now need one category bit each, and a new body costs nothing. The cost is that the author writes raw bit patterns on every shape, and one wrong digit makes a pair behave differently from what the author meant.

The fourth approach adds names and a table on top of the bits. A **collision layer** is a named class of bodies; the table says which pairs of layers collide, and the engine turns each row into category and mask bits. Strata takes this fourth approach. You write "Ghost does not collide with Ball" once, in one table, and every body that names its layer follows. Triggers follow the same table: a trigger reports only bodies on layers that collide with its own.

The table has a price. It is limited by the mask width: 32 layers, so a game with 33 kinds of body must merge two. It also says nothing about single bodies: two balls on one layer either all collide or none do. Cases that need single-body rules use other tools, such as triggers or scripts.

## The map

Four things hold collision data, and each has one owner:

- The project's section `Scene.CollisionLayers` holds the table: names and the pairs that do not collide. It is saved in the project file.
- Each scene holds a working copy, read through `Scene::GetPhysicsLayers`. The copy is not saved.
- The physics world holds one 32-bit mask per layer, which `PhysicsSystem` combines from the scene's copy and its own settings.
- Each shape holds a filter: a category and a mask of 64 bits each.

```mermaid caption="Where a collision layer table lives and how a change travels from the project file to a shape's filter. A script changes only the scene's copy." alt="A flow from the project settings section to the scene's working copy, then to the physics system, the physics world and the filter of each shape. A script arrow joins the working copy."
flowchart TD
	P["Project file: Scene.CollisionLayers"] -->|"Scene::ApplyProjectLayers (main thread)"| S["Scene working copy: GetPhysicsLayers"]
	X["Script: Physics::SetLayersCollide"] --> S
	S -->|"SyncLayers at each fixed step"| Y["PhysicsSystem: 32 combined masks"]
	Y -->|"SetLayerCollisionMasks"| W["PhysicsWorld"]
	W -->|"b3Shape_SetFilter"| F["Each shape: category and mask"]
	Q["Query: layer mask"] -->|"MakeQueryFilter"| F
```

A body's `RigidBodyComponent::Layer` picks its row. The filter functions live in `Strata/src/Strata/Physics/PhysicsFilters.h`, and the table's type in `Strata/src/Strata/Scene/PhysicsLayerSettings.h`.

## The contract

Code that reads or changes layers follows these rules, each with its reason.

- **The layers are the project's.** One name stands for one layer in every scene and prefab. If each scene had its own table, a prefab placed in two scenes could collide differently in each.
- **A script changes only the running copy.** `Physics::SetLayersCollide` writes the scene's copy, which lasts as long as the scene. The project file stays as it was, so the next play starts from the table the maker wrote.
- **Settings reach the world on the main thread.** The scene takes the project's table when it is handed over to the main thread, and again after every change of the table. A worker thread that builds a scene never reads the settings service, because that service belongs to the main thread.
- **Both masks must agree.** Two layers collide only if each one's row lets the other in. `SetCollide` writes both rows, so the table reads the same from both layers, and an edit of one row alone disables the pair.
- **Everything collides by default.** A project that sets no layers keeps all 32 names empty and every mask full.
- **Queries ignore what a body collides with.** A shape's filter always accepts one extra bit, the **query category**, which no shape owns and every query asks as, so a query finds a body whatever that body collides with.
- **A layer outside 0 to 31 is refused.** A body on layer 40 is logged and put on layer 0, and `DoCollide` answers false for such a layer.

:::rule[Collision layers are the project's]
`AGENTS.md` says that the table belongs to the project and that the scene works on a copy, applied on the main thread. The reason is the first and third rule above. Code that reads the table through the scene is right; code that reads the project's section from a worker thread is a :term[data race]{id=data-race}. See [Settings sections](../world/projects-settings.md).
:::

## A toy version

The toy below keeps the whole idea in about 80 lines: a matrix of 32 masks, the filter of a shape on a layer, and the test two filters pass. The matrix is a grid with one row per layer: row `i` is layer `i`'s mask, and its bit `j` says whether layer `i` collides with layer `j`. It adds the extra query bit, so you can see why a query still hits a body that collides with nothing.

The program prints the filters of a floor (layer 0), a ball (layer 1) and a ghost (layer 2). Search the code for three things. `SetCollide` touches two rows. `MakeShapeFilter` turns a layer number into one category bit and a matrix row. `Accepts` is the only place where a pair is decided.

```cpp sketch="physics-collision-layers-toy.cpp"
#include <array>
#include <cstdint>
#include <cstdio>

namespace
{

	constexpr uint32_t c_LayerCount = 32;
	constexpr uint32_t c_AllLayers = 0xFFFFFFFFu;
	constexpr uint64_t c_QueryCategory = uint64_t(1) << 63;

	struct Matrix
	{
		std::array<uint32_t, c_LayerCount> Masks;

		Matrix()
		{
			Masks.fill(c_AllLayers);
		}

		void SetCollide(uint32_t a, uint32_t b, bool collide)
		{
			if (collide)
			{
				Masks[a] |= 1u << b;
				Masks[b] |= 1u << a;
			}
			else
			{
				Masks[a] &= ~(1u << b);
				Masks[b] &= ~(1u << a);
			}
		}
	};

	struct Filter
	{
		uint64_t Category;
		uint64_t Mask;
	};

	Filter MakeShapeFilter(uint32_t layer, const Matrix& matrix)
	{
		return { uint64_t(1) << layer, uint64_t(matrix.Masks[layer]) | c_QueryCategory };
	}

	Filter MakeQueryFilter(uint32_t layerMask)
	{
		return { c_QueryCategory, layerMask };
	}

	// Each side's mask must hold the other side's category.
	bool Accepts(const Filter& a, const Filter& b)
	{
		return (a.Mask & b.Category) != 0 && (b.Mask & a.Category) != 0;
	}

	void Print(const char* name, const Filter& filter)
	{
		std::printf("%-5s category %016llx mask %016llx\n", name, static_cast<unsigned long long>(filter.Category),
			static_cast<unsigned long long>(filter.Mask));
	}

	const char* YesNo(bool value)
	{
		return value ? "yes" : "no";
	}

}

int main()
{
	Matrix matrix;
	matrix.SetCollide(1, 2, false);
	const Filter floor = MakeShapeFilter(0, matrix);
	const Filter ball = MakeShapeFilter(1, matrix);
	const Filter ghost = MakeShapeFilter(2, matrix);
	Print("floor", floor);
	Print("ball", ball);
	Print("ghost", ghost);

	std::printf("ball and ghost collide: %s\n", YesNo(Accepts(ball, ghost)));
	std::printf("ghost and floor collide: %s\n", YesNo(Accepts(ghost, floor)));
	std::printf("query on all layers sees the ghost: %s\n", YesNo(Accepts(MakeQueryFilter(c_AllLayers), ghost)));
	std::printf("query without layer 2 sees the ghost: %s\n", YesNo(Accepts(MakeQueryFilter(c_AllLayers & ~(1u << 2)), ghost)));

	Matrix oneSided;
	oneSided.Masks[1] &= ~(1u << 2);
	std::printf("one-sided edit, ball and ghost collide: %s\n",
		YesNo(Accepts(MakeShapeFilter(1, oneSided), MakeShapeFilter(2, oneSided))));
	return 0;
}
```

```text output-of="physics-collision-layers-toy.cpp"
floor category 0000000000000001 mask 80000000ffffffff
ball  category 0000000000000002 mask 80000000fffffffb
ghost category 0000000000000004 mask 80000000fffffffd
ball and ghost collide: no
ghost and floor collide: yes
query on all layers sees the ghost: yes
query without layer 2 sees the ghost: no
one-sided edit, ball and ghost collide: no
```

1. **Lines 12–19:** the matrix holds one 32-bit mask per layer, and the :term[constructor]{id=constructor} makes every mask full.
2. **Lines 21–33:** `SetCollide` sets or clears the bit in both rows.
3. **Lines 42–45:** a shape's category is one bit for its layer; its mask is its row plus the query bit.
4. **Lines 47–50:** a query has the query bit as its category and the layers it wants as its mask.
5. **Lines 53–56:** `Accepts` is the only place that decides a pair.

The ball's mask ends in `b` (binary 1011): bit 2 is clear, so the ball refuses layer 2. The ghost's mask ends in `d` (1101): bit 1 is clear. Both rows changed, so the pair is parted from either side.

The top digit 8 in each mask is bit 63, the query bit. A query on all layers sees the ghost; a query that omits layer 2 does not. The last line shows what the two-sided write protects: with only the ball's row changed, `Accepts` still says no, because it needs both sides.

## The real code

Strata has the same pieces, with names for layers, a :term[stored form]{id=stored-form} and the machinery that moves changes into a running world. The order below is the order the data flows.

### The table

The table is `PhysicsLayerSettings`. Read its three members first: the names, the masks and the :term[constructor]{id=constructor}.

```cpp src="Strata/src/Strata/Scene/PhysicsLayerSettings.h#L24-L67"
struct PhysicsLayerSettings
{
	static constexpr size_t c_MaxNameLength = 64;
	// A collision mask with every layer's bit.
	static constexpr uint32_t c_AllLayersMask = 0xFFFFFFFFu;

	// Empty for a layer without a name (shown as "Layer <index>").
	std::array<std::string, c_PhysicsLayerCount> Names;
	// Bit j of CollisionMasks[i] is set when layer i collides with layer j; kept symmetric by SetCollide.
	std::array<uint32_t, c_PhysicsLayerCount> CollisionMasks;

	PhysicsLayerSettings()
	{
		CollisionMasks.fill(c_AllLayersMask);
	}

	bool operator==(const PhysicsLayerSettings& other) const = default;

	// Layers outside [0, c_PhysicsLayerCount) are ignored (false).
	void SetCollide(uint32_t layerA, uint32_t layerB, bool collide)
	{
		if (layerA >= c_PhysicsLayerCount || layerB >= c_PhysicsLayerCount)
			return;
		const uint32_t bitA = 1u << layerA;
		const uint32_t bitB = 1u << layerB;
		if (collide)
		{
			CollisionMasks[layerA] |= bitB;
			CollisionMasks[layerB] |= bitA;
		}
		else
		{
			CollisionMasks[layerA] &= ~bitB;
			CollisionMasks[layerB] &= ~bitA;
		}
	}

	// Both masks must allow the pair.
	bool DoCollide(uint32_t layerA, uint32_t layerB) const
	{
		if (layerA >= c_PhysicsLayerCount || layerB >= c_PhysicsLayerCount)
			return false;
		return (CollisionMasks[layerA] & (1u << layerB)) != 0 && (CollisionMasks[layerB] & (1u << layerA)) != 0;
	}
```

1. **Lines 31–33:** one name and one 32-bit mask per layer. Bit `j` of `CollisionMasks[i]` says that layer `i` collides with layer `j`.
2. **Lines 35–38:** the constructor fills every mask with ones, so everything collides until a pair is parted.
3. **Lines 43–58:** `SetCollide` ignores layers out of range and writes both rows, setting or clearing one bit in each.
4. **Lines 62–67:** `DoCollide` reads both rows, the same rule as `Accepts` in the toy.

A layer without a name shows as "Layer 5" in the editor. `FindLayer` finds a layer by name, ignoring case. A name is at most 64 characters, has no control characters, does not start or end with a space and differs from every other layer's name.

### The stored form

The project's section stores the table as the layers' names by index and the pairs that do not collide. This is the value from the Playground's project file:

```json
{
	"Names": { "1": "Ball", "2": "Ghost" },
	"NoCollisions": [[1, 2]]
}
```

The table stays small because only the exceptions are written. A table where everything collides stores an empty list, and a project with no names and no exceptions stores no section at all. The section is **complex**: its value is one object that `PhysicsLayerSettings::FromJson` reads, not a list of simple fields. `FromJson` skips what it cannot read and reports each problem, and the section refuses a value with any problem. Scene documents that 0.5.0 wrote also carry this form; for them a problem only warns.

### The hand-over to the scene

The section is read through `ProjectCollisionLayers::Find`, which parses the project's value once for each version of the settings. `Scene::ApplyProjectLayers` then copies the table into the scene.

```cpp src="Strata/src/Strata/Scene/Scene.cpp#L218-L227" symbol="Scene::ApplyProjectLayers"
bool Scene::ApplyProjectLayers()
{
	const ProjectCollisionLayers::Table* table = ProjectCollisionLayers::Find();
	if (!table || table->Version == m_ProjectLayersVersion)
		return false;
	m_PhysicsLayers = table->Layers;
	m_ProjectLayersVersion = table->Version;
	m_StoredLayersDiffer = m_StoredPhysicsLayers && *m_StoredPhysicsLayers != table->Layers;
	return true;
}
```

1. **Lines 220–222:** with no project, or with the version the copy already came from, nothing changes and the function returns false.
2. **Lines 223–225:** the scene copies the table, remembers its version and notes whether a stored 0.5.0 table differs.

The version check is the reason a script's change survives an edit of another settings section: the table's version does not change, so the copy stays. Callers are the scene asset's hand-over, the load request and the editor, all on the main thread ([The hand-over to scenes](../world/projects-settings.md)). The editor calls it again after every change of the table.

### From the scene to the world

`PhysicsSystem` combines the scene's copy with its own settings: row by row, `PhysicsSettings::LayerCollisionMasks & CollisionMasks`. The own settings start full, so the scene's rows decide. `SyncLayers` runs in every :term[fixed step]{id=fixed-step}. It compares the 32 combined masks with the ones it applied last. It calls `PhysicsWorld::SetLayerCollisionMasks` only when something differs.

A body's layer reaches box3d, the physics library, when the world creates its shapes: `MakeBodySetup` passes the `Layer` of the `RigidBodyComponent` to `PhysicsFilters::MakeShapeFilter`. A layer out of range is logged once, and layer 0 is used.

```cpp src="Strata/src/Strata/Physics/PhysicsFilters.h#L18-L49"
constexpr uint64_t c_QueryCategory = uint64_t(1) << 63;
static_assert(c_PhysicsLayerCount <= 63, "The user layers and the query category share box3d's 64 category bits");

inline b3Filter MakeShapeFilter(uint32_t layer, const std::array<uint32_t, c_PhysicsLayerCount>& masks)
{
	b3Filter filter = b3DefaultFilter();
	filter.categoryBits = uint64_t(1) << layer;
	filter.maskBits = static_cast<uint64_t>(masks[layer]) | c_QueryCategory;
	filter.groupIndex = 0;
	return filter;
}

// The filter of a parked shape (a static body out of the simulation that box3d still holds, see PhysicsWorld's
// ParkStaticBody): its layer's category, which box3d's trees sort by, and an empty mask, so that no shape pairs with it and
// no query or sensor finds it.
inline b3Filter MakeParkedShapeFilter(uint32_t layer)
{
	b3Filter filter = b3DefaultFilter();
	filter.categoryBits = uint64_t(1) << layer;
	filter.maskBits = 0;
	filter.groupIndex = 0;
	return filter;
}

// A query of the shapes on the layers of `layerMask` (bit L: user layer L).
inline b3QueryFilter MakeQueryFilter(uint32_t layerMask)
{
	b3QueryFilter filter = b3DefaultQueryFilter();
	filter.categoryBits = c_QueryCategory;
	filter.maskBits = static_cast<uint64_t>(layerMask);
	return filter;
}
```

1. **Line 18:** bit 63 is the query category. The `static_assert` below keeps the 32 user layers and this bit inside box3d's 64 category bits.
2. **Lines 24–26:** a shape on layer `L` has category bit `L`; its mask is its matrix row plus the query bit. `groupIndex` stays 0, so box3d's group rule is never used.
3. **Lines 33–39:** a parked shape (a :term[static body]{id=static-body} out of the simulation, see [Scale and streaming](../physics/scale-streaming.md)) keeps its category but takes an empty mask, so nothing pairs with it and no query finds it.
4. **Lines 43–48:** a query asks as the query category, with a mask of the layers it wants. Its category is the bit every shape's mask holds.

The toy's `MakeQueryFilter` and `MakeShapeFilter` are these two functions, and `Accepts` is box3d's own test. The real code adds the parked filter and a character controller's filter, `MakeLayerQueryFilter`, which asks as a layer so that a character moves through what its layer ignores.

### Changes while the game runs

A change after the world exists goes through `SetLayerCollisionMasks`.

```cpp src="Strata/src/Strata/Physics/PhysicsWorld.cpp#L5112-L5137" symbol="PhysicsWorld::SetLayerCollisionMasks"
void PhysicsWorld::SetLayerCollisionMasks(const std::array<uint32_t, c_PhysicsLayerCount>& masks)
{
	PhysicsWorldData& data = *m_Data;
	if (data.Settings.LayerCollisionMasks == masks)
		return;
	const std::array<uint32_t, c_PhysicsLayerCount> previous = data.Settings.LayerCollisionMasks;
	data.Settings.LayerCollisionMasks = masks;
	// box3d keeps a filter per shape: the shapes of the layers whose masks changed take the new ones (rare, O(bodies)).
	// box3d destroys their contacts and finds them again at the next step, so their pairs wait for it to confirm them,
	// and only the pairs whose layers the change parts end. Parked bodies keep colliding with nothing: they take the new
	// masks when they come back or are disabled (UnparkBody).
	for (auto& [handle, record] : data.Bodies)
	{
		if (!record.HasBody() || record.Parked || previous[record.Layer] == masks[record.Layer])
			continue;
		const b3Filter filter = PhysicsFilters::MakeShapeFilter(record.Layer, masks);
		for (const b3ShapeId shape : record.Shapes)
			b3Shape_SetFilter(shape, filter, true);
		MarkPairsUnconfirmed(data, record.EntityID, LostContacts::Solid);
	}
	std::vector<UUID> refilteredCharacters;
	data.Characters->RefreshFilters(refilteredCharacters);
	for (const UUID entityID : refilteredCharacters)
		MarkPairsUnconfirmed(data, entityID, LostContacts::Solid);
	WakeAllBodies(data);
}
```

1. **Lines 5115–5116:** the same masks as before change nothing.
2. **Lines 5123–5131:** the loop skips records that have no box3d body, parked bodies and layers whose row did not change; the others take a new filter and their pairs wait for confirmation.
3. **Lines 5132–5135:** character controllers refresh their own filters in the same way.
4. **Line 5136:** every body wakes, so that resting bodies notice.

box3d keeps one filter on each shape, so a new matrix means new filters; the cost grows with the bodies, but changes are rare. Strata marks the pairs of the new filters as waiting for confirmation, so that only the pairs the change parted end, and wakes resting bodies, which would not notice that their floor has gone.

A script calls the SDK's `Physics::SetLayersCollide(a, b, collide)`. It returns false for a layer outside 0 to 31, and it writes only the scene's copy. `PhysicsSystem::SetLayersCollide` does the same and syncs the world at once.

:::example[Ball, ghost and floor]
The Playground's table: layer 1 `Ball`, layer 2 `Ghost`, the pair (1, 2) in `NoCollisions`. Layer 0 is the floor.

The ball's row is all ones except bit 2: `0xFFFFFFFB`. The ghost's row is all ones except bit 1: `0xFFFFFFFD`. A ball shape gets category `0x2` and mask `0x80000000FFFFFFFB`, a ghost shape category `0x4` and mask `0x80000000FFFFFFFD`.

Ball against ghost: the ball's mask combined with the ghost's category is `0xFFFFFFFB & 0x4`, which is 0, so they pass through each other. Ghost against floor: `0xFFFFFFFD & 0x1` is not zero, and the floor's mask holds bit 2, so they collide. A raycast with a mask of all layers has category bit 63, which the ghost's mask holds, and mask bit 2, which is the ghost's category: it hits the ghost. A raycast with `~(1u << 2)` has no bit 2, so it misses.

A script then calls `SetLayersCollide(1, 2, true)`. Both rows get their bit back, `SyncLayers` notices at the next step, the two layers' shapes get new filters and the resting bodies wake. The next ball that falls on a ghost lands on it.
:::

## The editor's side

The maker never writes the :term[JSON]{id=json} by hand. The **Collision Layers** page of Project Settings has a name field for each named layer, a button **Name a Layer** and a matrix of check boxes. The matrix has a row for layer 0 and for each layer that is named or parted from another, and one box per pair. A checked box means the pair collides.

Layout and drawing belong to [Settings windows](../editor-ui/settings-windows.md). The drawing below shows the page with the Playground's table.

::figure{id=settings-page-drawing}

Every edit on the page runs the command `project.setCollisionLayers`. Its parameters are `layerNames` (index to name; an empty name clears one), `resetLayerCollisions` and `layerCollisions` (a list of `{layers, collide}` pairs). It applies them in that order, and an invalid request changes nothing.

The command is one undo step that leaves the scene saved, because layers are not part of any scene, and it writes the project file in the background. It is allowed while the game plays: the running game takes the table at once, replacing what its scripts changed, and the change stays after the game stops. The Playground's Ghost layer is made like this:

```json
{
	"layerNames": { "1": "Ball", "2": "Ghost" },
	"layerCollisions": [{ "layers": ["Ball", "Ghost"], "collide": false }]
}
```

A layer in a pair is an index or a name. `scene.setSettings` has refused layer parameters since 0.6.0 and names `project.setCollisionLayers` in its error. The Playground's own notes still call the rule a scene setting; at the pin the table is in the project file.

A project saved by 0.5.0 kept its layers in each scene's document. When the editor opens such a project, a background job reads the layers of its scenes and makes them the project's before the start scene opens. A scene that still stores layers different from the project's gets a warning, and saving it drops the stored copy.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Per-pair ignore lists | Physics libraries that can ignore one pair of objects | Exact rules for single bodies | A list that grows with the bodies; nothing names the rule |
| Group numbers | box3d's `groupIndex`, the limbs of one character | A simple way to keep one object's parts apart | Cannot express "ghosts pass balls but hit the floor" |
| Raw category and mask bits on each shape | Box2D and box3d used directly | One-sided rules, such as a sensor that sees what does not see it | Raw patterns on every shape; no names; mistakes |
| A table in each scene | Strata 0.5.0 | Scenes that differ without a project | A name that means two things in two scenes; prefabs with no fixed rule |
| 63 layers, wider masks | box3d has 64 category bits | More kinds of body | A matrix of 63 rows in the editor; scripts' 32-bit masks change |

## How it is tested

The suite `Physics.Layers` in `StrataTests/src/Physics/PhysicsLayerTests.cpp` checks the table, the stored form and the running world. One case keeps the matrix the same from both layers and finds layers by name. One round-trips the table through `ToJson` and `FromJson`. One loads scenes saved before layer settings and reports invalid entries. Two cases drop a box through a floor it must pass, and change the matrix during play in both directions.

Another checks that a change ends only the pairs it parted.

The suite `Physics.Queries` holds the case `Bodies on a layer that collides with nothing are still hit by queries`: it parts a layer from all others and checks that raycasts and overlaps still find the body. Run both with:

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=Physics.Layers
build/windows/bin/Debug/StrataTests.exe --test-suite=Physics.Queries
```

Each command prints the failing checks with their lines.

## Changing it safely

New code that makes shapes calls `PhysicsFilters::MakeShapeFilter`; it never writes a filter by hand, because a missing query bit makes the body invisible to every query. A new kind of query builds its filter in the same :term[header]{id=header}. A parked body gets `MakeParkedShapeFilter`, and takes the current masks when it returns.

Changes to the table's stored form must keep `FromJson`, the section's schema (`additionalProperties` is false) and the migration of 0.5.0 documents in step. Keep both rows of a pair equal by writing the matrix only through `SetCollide`. Do not cache a layer's mask across steps: read the scene's copy.

:::rule[Settings reach the world on the main thread]
The physics settings and the table are applied by `PhysicsSystem` on the main thread, as it applies the project's `Physics.Simulation` section. Worker threads that build scenes never read the project's settings service. The reason is that the service, like every :term[engine service]{id=scene-service}, belongs to the main thread; see [Settings sections](../world/projects-settings.md).
:::

A change here passes `Physics.Layers`, `Physics.Queries` and the feature test, which must still exercise every layer function.

## Summary

- A pair of bodies, and a query, is decided by the filter bits of the shapes: the category and the mask, 64 bits each, built from the project's table.
- A shape on layer `L` has category bit `L` and, as its mask, its matrix row plus the query bit 63; two shapes collide only if each mask holds the other's category.
- The project's section `Scene.CollisionLayers` holds the table. The scene works on a copy, applied on the main thread; a script changes the copy, and a change of the table reaches the world at the next fixed step.
- The command `project.setCollisionLayers` names layers and parts pairs, such as `Ball` and `Ghost`, and the running game takes the change at once.

## Check yourself

1. A project has layers 3 and 7. The matrix parts 3 and 7, and nothing else is changed. What is bit 7 of layer 3's mask, and does a raycast with all layers hit a body on layer 7?

   :::answer{tests="predict-pair,filter-bits"}
   Bit 7 of layer 3's row is 0, and bit 3 of layer 7's row is 0. Bodies on the two layers pass through each other. A raycast asks as the query category, which every shape's mask holds, and its own mask holds all layers, so it hits the body on layer 7.
   :::

2. Someone clears bit 2 of the ball's row only, and leaves the ghost's row full. Do ball and ghost collide? Choose: (a) yes, since the ghost accepts the ball; (b) no, since both masks must agree; (c) only while the ball falls.

   :::answer{tests="predict-pair"}
   Answer (b). Strata and box3d need each shape's mask to hold the other's category, so one cleared bit parts the pair. Answer (a) forgets the ball's side. Answer (c) invents a rule that depends on motion; filters do not look at velocity.
   :::

3. A script calls `Physics::SetLayersCollide(1, 2, false)` during play, and the maker then edits the project's setting `Physics.Simulation`. Does the script's change stay?

   :::answer{tests="runtime-path"}
   Yes. The scene applies the project's table only when the table's version changes, and an edit of another section does not change it. The change ends when the scene ends, or when the maker edits the collision layers with `project.setCollisionLayers`.
   :::

4. What are the category and mask of a shape on layer 5 when layer 5 collides with layers 0 and 5 only?

   :::answer{tests="filter-bits"}
   The category is `1 << 5`, that is `0x20`. The row is bits 0 and 5, `0x21`, and the mask adds bit 63: `0x8000000000000021`.
   :::

5. A maker wants layer 2, named `Ghost`, to pass through layer 1, named `Ball`, while the game plays. Which command do they run, and what happens to an earlier change of a script?

   :::answer{tests="ghost-layer,runtime-path"}
   The maker runs `project.setCollisionLayers` with `layerNames` for the two names and a `layerCollisions` pair of `Ball` and `Ghost` with `collide` false. The running game takes the table at once and drops what its scripts changed. The change stays after the game stops, because it is written into the project.
   :::

## Exercises

1. **Basic.** Write the command call that creates a layer `Trigger` on index 3 and parts it from layer 0.

   :::answer[Worked solution]{tests="ghost-layer"}
   The parameters are `{"layerNames": {"3": "Trigger"}, "layerCollisions": [{"layers": [3, 0], "collide": false}]}`. Names apply first, so the pair can name the layer by its new name or by index. In the editor you type the name in the row of layer 3 and clear the box in the matrix.
   :::

2. **Medium.** Write a program with 32 masks, all full, that counts the layers layer 3 collides with. Count at the start, after parting 3 and 4, after parting 3 with itself, and after clearing only bit 3 of layer 5's mask. Predict the four numbers first.

   :::answer[Worked solution]{tests="predict-pair"}
   Layer 3 starts with 32 partners, itself included. Parting 3 and 4 leaves 31. Parting 3 with itself leaves 30. Clearing only bit 3 of layer 5's row removes 5, because `DoCollide` needs both rows, so the count is 29.

   ```cpp sketch="physics-collision-layers-exercise.cpp"
   #include <array>
   #include <cstdint>
   #include <cstdio>

   namespace
   {

   	constexpr uint32_t c_LayerCount = 32;

   	std::array<uint32_t, c_LayerCount> s_Masks;

   	void SetCollide(uint32_t a, uint32_t b, bool collide)
   	{
   		if (collide)
   		{
   			s_Masks[a] |= 1u << b;
   			s_Masks[b] |= 1u << a;
   		}
   		else
   		{
   			s_Masks[a] &= ~(1u << b);
   			s_Masks[b] &= ~(1u << a);
   		}
   	}

   	bool DoCollide(uint32_t a, uint32_t b)
   	{
   		return (s_Masks[a] & (1u << b)) != 0 && (s_Masks[b] & (1u << a)) != 0;
   	}

   	uint32_t CountPartners(uint32_t layer)
   	{
   		uint32_t count = 0;
   		for (uint32_t other = 0; other < c_LayerCount; other++)
   		{
   			if (DoCollide(layer, other))
   				count++;
   		}
   		return count;
   	}

   }

   int main()
   {
   	s_Masks.fill(0xFFFFFFFFu);
   	std::printf("layer 3 starts with %u partners\n", CountPartners(3));
   	SetCollide(3, 4, false);
   	std::printf("after parting 3 and 4: %u\n", CountPartners(3));
   	SetCollide(3, 3, false);
   	std::printf("after parting 3 and 3: %u\n", CountPartners(3));
   	s_Masks[5] &= ~(1u << 3);
   	std::printf("after a one-sided edit of layer 5: %u\n", CountPartners(3));
   	return 0;
   }
   ```

   ```text output-of="physics-collision-layers-exercise.cpp"
   layer 3 starts with 32 partners
   after parting 3 and 4: 31
   after parting 3 and 3: 30
   after a one-sided edit of layer 5: 29
   ```

   1. **Lines 12–24:** `SetCollide` writes both rows of a pair.
   2. **Lines 26–29:** `DoCollide` needs both rows to agree.
   3. **Lines 31–40:** `CountPartners` asks `DoCollide` about every layer, itself included.
   :::

3. **Hard.** Trace it yourself: find where a `RigidBodyComponent`'s `Layer` becomes box3d's filter, and where a raycast's layer mask becomes a query filter.

   :::answer[Worked solution]{tests="filter-bits,runtime-path"}
   Search `Strata/src/Strata/Physics/` for `MakeShapeFilter`. `MakeBodySetup` in `PhysicsWorld.cpp` checks that the layer is below 32 (else it logs and uses 0) and stores the filter in the shape definition. Searching for `MakeQueryFilter` leads to the query functions, which pass the caller's mask to it.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Scene/PhysicsLayerSettings.h` and `.cpp`: the table, its stored form and its names.
- `Strata/src/Strata/Scene/ProjectCollisionLayers.cpp`: the section `Scene.CollisionLayers` and `Find`.
- `Strata/src/Strata/Scene/Scene.cpp`: `ApplyProjectLayers` and the working copy.
- `Strata/src/Strata/Physics/PhysicsFilters.h`, `PhysicsSystem.cpp` and `PhysicsWorld.cpp`: filters, `SyncLayers`, `SetLayerCollisionMasks`.
- `StrataScriptCore/Include/StrataScript/Physics.h`: `Physics::SetLayersCollide`.
- `StrataEditor/src/UI/CollisionLayersPage.cpp` and `StrataEditor/src/Editor/EditorProjectSettingsCommands.cpp`: the page and `project.setCollisionLayers`.
- Tests: the suites `Physics.Layers` and `Physics.Queries`.

## Further reading

- Box2D documentation, "Collision filtering" (category bits, mask bits and groups; intermediate).
- Unity manual, "Layer-based collision detection" (a layer matrix in another engine; beginner).
- Godot documentation, "Physics introduction", the section on collision layers and masks (beginner).
