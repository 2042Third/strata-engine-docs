---
id: world/scene-graph
title: "The scene graph: hierarchy, transforms and the transform contract"
description: "How Strata stores which entity hangs below which, keeps every world transform current at the cost of what changed, and what every writer must do."
kind: internals
size: XL
tracks: [E]
needs: [world/ecs, basics/math-rotations, core/math, core/jobs]
time: 150
learn:
  - id: dual-hierarchy
    text: explain why Strata keeps its hierarchy in two forms and how every change keeps them in step
  - id: dirty-walk
    text: predict which entities an update of the world transforms computes, and in which order
  - id: contract
    text: change transforms and the hierarchy from engine code without leaving a cache of the scene wrong
  - id: frame-cost
    text: compute what a frame of transform updates costs from the entities it has to compute
  - id: lookups
    text: explain how names, tags and the primary camera are found in hierarchy order without a walk of the scene
since: 0.3.0
status: final
---

A wheel belongs to a car: when the car drives away, the wheel must come along, and when the wheel turns, the car must
stay as it is. The scene graph is the part of Strata's `Scene` that makes this work. It stores which entity hangs below
which, and keeps for every entity a transform relative to its parent and a cached transform in the world. It also keeps
the scene's other caches true as entities change: the order of the hierarchy, the activity parents pass to their
children, and indexes of names and tags. The scene graph draws
and simulates nothing: the :term[renderer]{id=renderer}, physics and the editor build
on what it keeps.

## The problem and how engines solve it

### Where is the wheel?

Put a car on a road, 10 meters from the start. Its wheel sits 2 meters in front of the car's center, and a bolt sits
1 meter from the wheel's center. The wheel is half the size of the model it was made from, so the bolt's meter in the
wheel's own units is half a meter in the car's.

Where is the bolt on the road? Start at the car: 10 meters. Add the
wheel's 2 meters: 12. Add the bolt's 1 meter, made half as long by the wheel's size: 12.5 meters.

Now the car drives to 20 meters. Nobody writes the wheel or the bolt, yet the wheel is now at 22 meters and the bolt at
22.5. That is the point of storing each entity relative to its parent: one write moves everything that hangs below.
What each entity stores is its :term[local transform]{id=local-transform}, the offset, rotation and size it has relative to its parent. What the
renderer and physics need is its :term[world transform]{id=world-transform}, where it is in the scene, which only exists after composing the local
transforms from the top down.

The same sum, written with matrices, is the one [Matrices](../basics/math-matrices.md) teaches. In words: a child's world
matrix is its parent's world matrix times its own local matrix.

$$
W_{\text{child}} = W_{\text{parent}} \, L_{\text{child}}
$$

$W_{\text{child}}$ is the child's world matrix and $W_{\text{parent}}$ its parent's; $L_{\text{child}}$ is the child's
local matrix. All three are 4 by 4 matrices whose last column holds a position in meters. The two letters side by side
are read "times": the matrix product, with the parent on the left. A **root entity** is an entity that has no parent;
its world matrix is its local matrix, as if $W_{\text{parent}}$ were the identity.

Two questions follow. How does a tree live in a store of components, where an entity is
a number and its data sits in one storage per type ([The entity component system](../world/ecs.md))? And when are the
world matrices computed: every frame, when something moves, or when someone asks?

### Storing a tree among components

There are four common answers to the first question, and each makes one operation cheap and another one costly.

- **A parent field only.** Each child stores its parent's handle, and nothing else. A change of parent is one write. But
  finding an entity's children means visiting every entity of the scene, and the order of siblings has no place to live.
- **A list of children per parent.** The parent keeps a vector of its children's handles, in order. Children are found
  at once, but removing one shifts every handle behind it, and each parent with children owns memory of its own.
- **A linked list inside the entities.** Each entity stores its parent, its first child and its next sibling, so the
  links live in the entities themselves. Adding and removing take a few writes and no memory, but the position of the 500th child
  is known only after counting 499 siblings.
- **One array in tree order.** All entities sit in one array sorted so that parents come before their children, often by
  depth. Computing every world matrix is one pass over memory, but each change of the tree moves elements of the array.

### Keeping world matrices current

The second question also has three common answers.

- **Compute everything, every frame.** One pass from the roots down computes every world matrix. Nothing can go stale,
  and a scene of a million entities pays for a million matrices in a frame where nothing moved.
- **Dirty flags.** A **dirty flag** is a mark that says a cached value no longer matches the data it was computed from.
  A write to a local transform marks its entity; the next update computes the marked entities and everything below them.
  A frame where nothing moved costs nothing. The price is that every writer must mark what it wrote.
- **Change versions.** A counter goes up with every change, and each piece of data remembers the counter of its last
  write. A reader that remembers the counter it last saw asks "what changed since then?" and touches only that.

Strata takes the :term[linked list]{id=linked-list} inside the entities for its hot paths and keeps a saved list of
children beside it. It uses dirty flags for the world matrices, and versions with [change logs](../draw/render-scene.md) for the readers outside
the scene. The rest of this page shows how
and what each choice costs.

## A map of the code

The scene graph lives in a few files of `Strata/src/Strata`. One class, `Scene`, owns everything; its components carry
the data, and readers in other modules follow what it reports.

```mermaid caption="Writers change local data and signal; the scene keeps its caches; readers follow its reports." alt="A diagram. Editor commands, scripts and systems write components and signal through the registry, while physics marks its writes without a signal. The signals reach the dirty list, the activity flags and the name and tag indexes, and structural changes reach the two hierarchy forms. The update of world transforms reads the dirty list and writes the world matrices, the change log and the version. The render scene and the game interface read the change log; physics reads current world matrices."
flowchart LR
    Writers["Editor commands, scripts, systems"] -->|"write, then patch"| Signals["Registry signals"]
    Physics["Physics write-back"] -->|"MarkTransformChanged"| Dirty["Dirty list"]
    Signals -->|"OnTransformChanged"| Dirty
    Signals -->|"OnInactiveAdded, OnInactiveRemoved"| Activity["ActiveInHierarchy"]
    Signals -->|"OnNameChanged, OnTagChanged"| Indexes["Name and tag indexes"]
    Structure["SetParent, SetSiblingIndex, PlaceEntities"] --> Links["RelationshipComponent and HierarchyComponent"]
    Dirty --> Update["UpdateWorldTransforms"]
    Update --> World["WorldTransformComponent"]
    Update --> Log["Change log and transforms version"]
    Log --> Readers["Render scene, game interface"]
    World --> PhysicsRead["Physics reads current matrices"]
```

| File | What it holds |
| --- | --- |
| `Scene/Components.h` | `TransformComponent`, `RelationshipComponent`, `WorldTransformComponent`, `InactiveComponent`, `NameComponent` and `TagComponent` |
| `Scene/SceneHierarchy.h` | `HierarchyComponent`: the handle links, the depth, the position among siblings and the update's scratch fields |
| `Scene/Scene.h` and `Scene/Scene.cpp` | every change of the hierarchy, the signal handlers, the dirty list, the walk, the change logs, the indexes and the `Debug` check |
| `Math/Math.cpp` | `ComposeTransform`, `DecomposeTransform` and `ComposeWorldTransform` |
| `Core/AmortizedCheck.h` | how often the `Debug` check runs |
| `Renderer/RenderScene.cpp`, `GameUI/GameUIScene.cpp` | readers of the change log |
| `Physics/PhysicsWorld.cpp` | a reader of current world matrices from worker threads, and a writer that marks without a signal |

Every `Scene` function runs on the :term[main thread]{id=main-thread}, as the class comment in `Scene.h` demands. Two places reach other
threads. The update of world matrices hands wide levels of the tree to `ParallelFor` from
[Jobs](../core/jobs.md), and each job writes only the world matrices of the :term[subtrees]{id=subtree} it was given. And
`FindCurrentWorldTransform` only reads, so physics calls it from its workers while no thread changes the scene.

## The contract

What a caller may count on:

- After `UpdateWorldTransforms`, every `WorldTransformComponent::Matrix` equals its parent's world matrix times its own
  local matrix. Between updates, `GetWorldTransform` returns the value the next update will cache.
- `IsActiveInHierarchy` is exact at every moment, not only after an update.
- `FindEntityByName`, `FindEntitiesByTag` and `GetPrimaryCameraEntity` answer in hierarchy order, the order of the
  **Hierarchy** panel.
- `GetWorldTransformChanges` and `GetHierarchyMoves` list every entity that changed since a version, or say that they no
  longer remember that far back.

What a caller must do, each with its reason:

- **Signal every direct write** of a `TransformComponent`, a `NameComponent` or a `TagComponent`. The scene learns about
  writes only through signals, the calls the registry makes to listening functions when a component changes (the
  section on signals below shows them). A silent write leaves a cache that the renderer and physics read wrong.
- **Mark with `MarkTransformChanged`** where your own listeners must not hear the write. Physics writes simulated poses
  back, and it listens to transform signals for edits; a signal would make it handle its own write as an edit.
- **Change the hierarchy only through `Scene`** (`SetParent`, `SetSiblingIndex`, `PlaceEntities`, `DestroyEntities`).
  Two forms of the hierarchy, depths, positions, activity and a version must change together.
- **Call `Scene` on the main thread.** Its caches have no locks.

The **transform contract** is Strata's rule that every direct write to a transform is followed by a signal, so that the
scene's caches learn of it. The names and tags follow the same rule.

:::rule[Signal what you write in place]
Code that writes the fields of a `TransformComponent` directly must tell the scene, through
`Entity::MarkModified<TransformComponent>()`, `registry.patch` or `Scene::MarkTransformChanged`. Writes to names, tags,
mesh renderers and light fields must signal too, and the hierarchy changes only through the functions of `Scene`. The
reason: the scene and the [render scene](../draw/render-scene.md) cache what they computed from these fields and learn of changes only through
signals. The rule's full form is in the engine's `AGENTS.md`, "Architecture rules".
:::

## A toy version

A toy does the whole job in one file. Each entity has a parent, a linked list of children, a
local transform made of one offset along a road and one size, and a cached world transform. A write is followed by a
mark, and an update computes only what was marked and what hangs below it. In `Update`, notice the **frontier**, the set
of dirty entities that have no dirty ancestor, and what happens to the tree after a write without a mark.

```cpp sketch="world-scene-graph-toy.cpp"
// A toy scene graph: children in an intrusive list, world transforms cached and computed only below changes.
#include <cstdio>
#include <vector>

constexpr int c_None = -1;

struct Node
{
	int Parent = c_None, FirstChild = c_None, LastChild = c_None, NextSibling = c_None;
	float LocalX = 0.0f, LocalScale = 1.0f; // relative to the parent: an offset in metres and a size
	float WorldX = 0.0f, WorldScale = 1.0f; // the cache: the same two numbers in the world
	bool Dirty = false;
};

std::vector<Node> s_Nodes;
std::vector<int> s_DirtyList;

void MarkDirty(int entity)
{
	if (!s_Nodes[entity].Dirty)
		s_DirtyList.push_back(entity);
	s_Nodes[entity].Dirty = true;
}

int Create(int parent, float localX, float localScale)
{
	const int entity = static_cast<int>(s_Nodes.size());
	s_Nodes.push_back(Node { parent, c_None, c_None, c_None, localX, localScale });
	if (parent != c_None)
	{
		const int last = s_Nodes[parent].LastChild;
		(last == c_None ? s_Nodes[parent].FirstChild : s_Nodes[last].NextSibling) = entity;
		s_Nodes[parent].LastChild = entity;
	}
	MarkDirty(entity); // a new entity is computed at the next update
	return entity;
}

bool HasDirtyAncestor(int entity)
{
	for (int current = s_Nodes[entity].Parent; current != c_None; current = s_Nodes[current].Parent)
		if (s_Nodes[current].Dirty)
			return true;
	return false;
}

void Update(const char* what)
{
	std::vector<int> level; // the frontier: dirty entities with no dirty ancestor
	for (const int entity : s_DirtyList)
		if (!HasDirtyAncestor(entity))
			level.push_back(entity);
	s_DirtyList.clear();
	int computed = 0;
	while (!level.empty())
	{
		std::vector<int> next;
		for (const int entity : level)
		{
			Node& node = s_Nodes[entity];
			const Node parent = node.Parent == c_None ? Node {} : s_Nodes[node.Parent];
			node.WorldX = parent.WorldX + parent.WorldScale * node.LocalX;
			node.WorldScale = parent.WorldScale * node.LocalScale;
			node.Dirty = false;
			computed++;
			for (int child = node.FirstChild; child != c_None; child = s_Nodes[child].NextSibling)
				next.push_back(child);
		}
		level.swap(next);
	}
	std::printf("%-20s computed %d, world x:", what, computed);
	for (const Node& node : s_Nodes)
		std::printf(" %5.1f", node.WorldX);
	std::printf("\n");
}

int main()
{
	const int car = Create(c_None, 10.0f, 1.0f);
	const int wheel = Create(car, 2.0f, 0.5f);
	const int bolt = Create(wheel, 1.0f, 1.0f);
	const int tree = Create(c_None, 50.0f, 3.0f);
	Update("first update:");
	Update("nothing changed:");
	s_Nodes[bolt].LocalX = 3.0f;
	MarkDirty(bolt); // a write, then its signal
	s_Nodes[car].LocalX = 20.0f;
	MarkDirty(car);
	Update("bolt and car moved:");
	s_Nodes[tree].LocalX = 60.0f; // a write without a signal
	Update("silent write:");
}
```

```text output-of="world-scene-graph-toy.cpp"
first update:        computed 4, world x:  10.0  12.0  12.5  50.0
nothing changed:     computed 0, world x:  10.0  12.0  12.5  50.0
bolt and car moved:  computed 3, world x:  20.0  22.0  23.5  50.0
silent write:        computed 0, world x:  20.0  22.0  23.5  50.0
```

1. **Lines 18–23:** a mark is set once. A second write in the same frame finds the flag set and adds nothing, so the
   dirty list never holds an entity twice.
2. **Lines 29–34:** the linked list. Adding a child at the end writes the old last child's `NextSibling`, or the parent's
   `FirstChild` when there was none, and no memory moves.
3. **Lines 49–53:** the frontier. The bolt was marked, but so was the car above it; computing the car's subtree
   computes the bolt anyway, so only the car starts a walk: the frontier is the car alone. That is why the third update computes 3 entities, not 4.
4. **Lines 61–63:** the composition for this toy's transforms, the parent's offset plus the parent's size times the
   local offset. A root composes with a default `Node`, whose world offset is 0 and size 1.
5. **Lines 90–91:** the silent write. The tree's local offset is 60, but no mark was set, so the update computes nothing
   and the cache still says 50. Every reader of the cache now sees a tree where there is none.

Each line shows the car, the wheel, the bolt and a tree beside the road. The third update also moved the bolt to 3
meters from the wheel: $22 + 0.5 \times 3 = 23.5$. The toy omits a full transform with a rotation, positions among
siblings, a saved form, activity, indexes, threads and a check that catches the silent write. The next sections add
each one.

## Transforms: local, world and back

A `TransformComponent` is the local transform as three parts: a translation, a rotation and a scale. The world matrix
is not in it; it lives in a separate :term[runtime]{id=runtime} component that is never saved. Notice which of the three components a
file keeps and which only the running scene keeps.

```cpp src="Strata/src/Strata/Scene/Components.h#L50-L81"
struct TransformComponent
{
	glm::vec3 Translation = { 0.0f, 0.0f, 0.0f };
	glm::quat Rotation = { 1.0f, 0.0f, 0.0f, 0.0f };
	glm::vec3 Scale = { 1.0f, 1.0f, 1.0f };

	// Local transform relative to the parent entity.
	glm::mat4 GetTransform() const
	{
		return Math::ComposeTransform(Translation, Rotation, Scale);
	}

	// Returns false (keeping the current values) if the matrix cannot be decomposed.
	bool SetTransform(const glm::mat4& transform)
	{
		return Math::DecomposeTransform(transform, Translation, Rotation, Scale);
	}
};

// Hierarchy links. Children order is the display/serialization order.
struct RelationshipComponent
{
	UUID Parent = UUID::Null();
	std::vector<UUID> Children;
};

// Runtime cache computed by Scene::UpdateWorldTransforms(); not serialized.
struct WorldTransformComponent
{
	glm::mat4 Matrix = glm::mat4(1.0f);
	bool ActiveInHierarchy = true;
};
```

1. **Lines 52–54:** translation, rotation and scale. The rotation is a :term[quaternion]{id=quaternion} ([Rotations](../basics/math-rotations.md)),
   with the identity $(1, 0, 0, 0)$ as its default; the Inspector edits it as Euler angles in degrees.
2. **Lines 57–60:** `GetTransform` composes the three into a local matrix; the result is relative to the parent, never
   the world.
3. **Lines 63–66:** `SetTransform` goes the other way and can fail. On failure the component keeps its old values.
4. **Lines 70–74:** the saved form of the hierarchy, by `UUID`, the entity's lasting identity: the parent's and the
   children's, in order.
5. **Lines 77–81:** the cached world matrix and the activity flag. Nothing saves this component; the update writes it.

A common mistake follows from this layout: `Translation` is a position relative to the parent, not in the world. A
script that reads it for a child gets the child's offset from its parent.

### From a matrix to local values

Some operations know the world matrix they want and need the local values that produce it. Moving a child to a new
parent without moving it in the world is one; placing copies of a saved group at given matrices (`Prefab::InstantiateMany`) is another. Both end in
`TransformComponent::SetTransform`, which calls `Math::DecomposeTransform`. The :term[decomposition]{id=decomposition-of-a-transform} reads the translation
from the last column, the scale from the lengths of the other three, and the rotation from those columns once divided
by their lengths ([Bases](../basics/math-bases.md) explains each step). Notice the four places where it refuses a
matrix, and what it does without refusing.

```cpp src="Strata/src/Strata/Math/Math.cpp#L9-L54"
bool DecomposeTransform(const glm::mat4& transform, glm::vec3& outTranslation, glm::quat& outRotation, glm::vec3& outScale)
{
	// Outputs are only written on success, so callers keep their previous values for degenerate input.
	for (int column = 0; column < 4; column++)
	{
		for (int row = 0; row < 4; row++)
		{
			if (!std::isfinite(transform[column][row]))
				return false;
		}
	}

	glm::mat4 localMatrix(transform);
	if (glm::abs(localMatrix[3][3]) < glm::epsilon<float>())
		return false;

	// Normalize so the homogeneous coordinate is 1. Projective components are ignored.
	if (glm::abs(localMatrix[3][3] - 1.0f) > glm::epsilon<float>())
		localMatrix /= localMatrix[3][3];

	const glm::vec3 translation = glm::vec3(localMatrix[3]);
	glm::vec3 columns[3] = { glm::vec3(localMatrix[0]), glm::vec3(localMatrix[1]), glm::vec3(localMatrix[2]) };
	glm::vec3 scale(glm::length(columns[0]), glm::length(columns[1]), glm::length(columns[2]));
	if (scale.x < glm::epsilon<float>() || scale.y < glm::epsilon<float>() || scale.z < glm::epsilon<float>())
		return false;

	columns[0] /= scale.x;
	columns[1] /= scale.y;
	columns[2] /= scale.z;

	// A left-handed basis means an odd number of negative scale axes; fold the reflection into X.
	if (glm::dot(columns[0], glm::cross(columns[1], columns[2])) < 0.0f)
	{
		scale.x = -scale.x;
		columns[0] = -columns[0];
	}

	const glm::quat rotation = glm::normalize(glm::quat_cast(glm::mat3(columns[0], columns[1], columns[2])));
	if (!std::isfinite(rotation.x) || !std::isfinite(rotation.y) || !std::isfinite(rotation.z) || !std::isfinite(rotation.w))
		return false;

	outTranslation = translation;
	outRotation = rotation;
	outScale = scale;
	return true;
}
```

1. **Lines 12–19:** any element that is not a finite number refuses the whole matrix.
2. **Lines 22–27:** the bottom right element must not be near zero; any other value divides the matrix out.
3. **Lines 31–33:** a column shorter than `glm::epsilon<float>()`, about 0.0000001, means a scale near zero on that
   axis, which has no rotation to recover.
4. **Lines 40–44:** a mirror. When the three columns form a :term[left-handed]{id=handedness} set, an odd number of axes was flipped, and the
   code flips X alone, whatever axis the author flipped.
5. **Lines 46–53:** the rotation is made from the columns as they are, and a rotation that is not finite is the fourth
   refusal. The outputs are written only now, so a refusal leaves the caller's values untouched.

What the code does not check matters as much. A matrix with shear, whose columns are not at right angles to each other,
is not refused. Its columns are made unit length and turned into a quaternion as they are, and the shear is dropped
without a warning. The same holds for a mirror: the result stores it on the X axis.

:::example[A sheared child loses its shape]
A parent has the scale $(2, 1, 1)$, and its child is turned 45 degrees about Z. The child's world matrix has the
columns $(1.414, 0.707, 0)$ and $(-1.414, 0.707, 0)$ for its first two axes: the parent's stretch along X, applied after
the turn. Their :term[dot product]{id=dot-product} is $-2 + 0.5 = -1.5$, not 0, so the axes are not at right angles: a square the child draws
appears as a diamond.

Now the child moves to the top level and keeps its world transform. The scene asks the decomposition for local values
that give that matrix. Both columns are 1.581 long, so the scale becomes $(1.581, 1.581, 1)$, and the rotation is made
from the two columns divided by their length. No translation, rotation and scale can hold a diamond, so the call
succeeds with a pose it can build: the diamond becomes a square of side 1.581. A keep-world `SetParent`, a
`SetWorldTransform` and an `InstantiateMany` with such a matrix all succeed and lose the shear the same way.
:::

```mermaid caption="Local values compose into matrices from the top down; the way back divides out the parent and takes the matrix apart." alt="Two chains. In the first, a local translation, rotation and scale become a local matrix, which the parent's world matrix multiplies into the child's world matrix. In the second, the inverted parent's world matrix multiplies a wanted world matrix. The decomposition turns the result into translation, rotation and scale. It fails for values that are not finite, a zero scale or a zero bottom right element, and it drops shear."
flowchart LR
    TRS["Local translation, rotation, scale"] -->|"GetTransform"| Local["Local matrix"]
    ParentWorld["Parent's world matrix"] --> Compose["ComposeWorldTransform"]
    Local --> Compose
    Compose --> World["Child's world matrix"]
    Wanted["Wanted world matrix"] --> Inverse["Inverted parent's world, times the wanted"]
    Inverse -->|"SetTransform"| Decompose["DecomposeTransform"]
    Decompose --> Back["New local translation, rotation, scale"]
```

`ComposeWorldTransform` is the one function every path uses to multiply a parent's world matrix with a local matrix;
[Math in Strata](../core/math.md) explains why it is compiled once, in `Math.cpp`, so that every caller rounds alike.

## Two forms of one hierarchy

The hierarchy has to serve two masters. A saved scene needs links that mean the same after loading again, so it names
entities by `UUID`, the 64-bit identity that never changes. The running scene needs links it can follow without a search,
so it names entities by their registry handle ([The entity component system](../world/ecs.md)), which is an index into
the storages. Strata keeps both forms.

`RelationshipComponent` is the saved form: the parent's `UUID` and the vector of the children's `UUID` values. Its vector is the
authority on the order of children; the file writes it, the **Hierarchy** panel shows it. `HierarchyComponent` is the
runtime form: handle links in a doubly linked list inside the entities, kept beside the saved form and never saved
itself. Notice the fields that make each operation cheap.

```cpp src="Strata/src/Strata/Scene/SceneHierarchy.h#L10-L37"
// Runtime hierarchy links of a scene entity, kept by Scene next to RelationshipComponent (which stays the serialized form
// and the authoritative child order). Hot paths (world transforms, subtrees, ancestry, hierarchy order) walk these EnTT
// handles instead of looking UUIDs up. Every structural operation of Scene maintains them; nothing else may write them.
// Not registered with ComponentRegistry (like WorldTransformComponent): never serialized, copied or shown.
struct HierarchyComponent
{
	entt::entity Parent = entt::null;      // entt::null for root entities
	entt::entity FirstChild = entt::null;
	entt::entity LastChild = entt::null;   // Appending a child is O(1)
	entt::entity NextSibling = entt::null; // Siblings in child order (roots: in root order)
	entt::entity PrevSibling = entt::null;
	uint32_t Depth = 0;                    // Roots have depth 0
	uint32_t ChildCount = 0;
	// Position among the siblings; current only while the parent's ChildIndicesValid (or, for roots, the scene's root
	// indices) are. Read it through Scene::GetSiblingIndex, which refreshes the whole sibling list in one pass.
	uint32_t SiblingIndex = 0;
	// Scratch of Scene::UpdateWorldTransforms (which entities have a dirty ancestor, memoized per update).
	uint32_t TransformPass = 0;
	bool DirtyAbove = false;
	// The entity's local transform or parent changed since the last UpdateWorldTransforms: its cached world transform and
	// those of its descendants are stale.
	bool TransformDirty = false;
	// The SiblingIndex of every child is current. Appending keeps it; other changes of the child list clear it.
	bool ChildIndicesValid = true;
	// UpdateWorldTransforms computed the cached world matrix at least once (an interpolation capture tells entities created
	// during the fixed steps by it).
	bool HasWorldTransform = false;
};
```

1. **Lines 16–20:** the links. `LastChild` lets a new child go to the end without a walk, and `PrevSibling` lets an
   entity leave the list without one.
2. **Line 21:** the depth, with roots at 0. Comparing two entities' order starts from it.
3. **Lines 23–25:** the cached position among siblings, which is current only while the parent's `ChildIndicesValid`
   says so.
4. **Lines 26–31:** scratch fields of the update. `TransformDirty` is the dirty flag of the whole subtree below.
5. **Line 36:** set once the update has computed the entity. The capture of poses reads it, for the drawing between
   [fixed steps](../core/time.md), the updates of constant length that physics runs
   ([Drawing between fixed steps](../world/interpolation.md)).

A **sibling index** is an entity's position among its parent's children, or among the roots for a root entity. In the
saved form it is the place of the entity in the parent's vector; in the handle form it is the count of siblings before
it, cached in `SiblingIndex`.

```mermaid caption="One small tree, stored twice: by identity for the file and by handle links for the running scene." alt="On the left, the saved form: the car has no parent and the children wheel A and wheel B in that order. Wheel A has the parent car and the child bolt. On the right, the runtime form: the car's first child is wheel A and its last child is wheel B. Wheel A's next sibling is wheel B, wheel B's previous sibling is wheel A, and each child points to its parent. Wheel A's first and last child is the bolt."
flowchart LR
    subgraph Saved["Saved form, by identity"]
        SCar["Car: Parent none, Children: Wheel A, Wheel B"]
        SWheel["Wheel A: Parent Car, Children: Bolt"]
        SWheelB["Wheel B: Parent Car, Children: none"]
        SBolt["Bolt: Parent Wheel A, Children: none"]
    end
    subgraph Runtime["Runtime form, by handle"]
        Car["Car, depth 0"]
        WheelA["Wheel A, depth 1, index 0"]
        WheelB["Wheel B, depth 1, index 1"]
        Bolt["Bolt, depth 2, index 0"]
        Car -->|"FirstChild"| WheelA
        Car -->|"LastChild"| WheelB
        WheelA -->|"NextSibling"| WheelB
        WheelB -->|"PrevSibling"| WheelA
        WheelA -->|"Parent"| Car
        WheelB -->|"Parent"| Car
        WheelA -->|"FirstChild, LastChild"| Bolt
        Bolt -->|"Parent"| WheelA
    end
```

:::why[Why two forms?]
A form by `UUID` alone would make every hot path pay a search: from a `UUID` to its entity, then to its component, at every
step of every walk. A handle form alone could not be saved, because handles are used again and change from one load to the
next. With both, the file keeps stable identities and the update follows plain links. The cost is that every change of
the hierarchy writes both forms, and nothing outside `Scene` may write either. That is why the two components are not
part of any editor command or script function.
:::

The two forms stay in step because one function adds a child to both at once. `Scene::LinkLast` puts an entity at the
end of its new parent's children, or of the roots. Notice the two writes of the saved form at its end.

```cpp src="Strata/src/Strata/Scene/Scene.cpp#L942-L974" symbol="Scene::LinkLast"
void Scene::LinkLast(entt::entity child, entt::entity parent)
{
	HierarchyComponent& node = GetHierarchy(child);
	const UUID id = m_Registry.get<IDComponent>(child).ID;
	node.Parent = parent;
	node.NextSibling = entt::null;
	if (parent == entt::null)
	{
		node.PrevSibling = m_LastRoot;
		if (m_LastRoot != entt::null)
			GetHierarchy(m_LastRoot).NextSibling = child;
		else
			m_FirstRoot = child;
		m_LastRoot = child;
		// Appending keeps the other positions current.
		node.SiblingIndex = static_cast<uint32_t>(m_RootEntities.size());
		m_RootEntities.push_back(id);
		m_Registry.get<RelationshipComponent>(child).Parent = UUID::Null();
		return;
	}

	HierarchyComponent& parentNode = GetHierarchy(parent);
	node.PrevSibling = parentNode.LastChild;
	if (parentNode.LastChild != entt::null)
		GetHierarchy(parentNode.LastChild).NextSibling = child;
	else
		parentNode.FirstChild = child;
	parentNode.LastChild = child;
	node.SiblingIndex = parentNode.ChildCount;
	parentNode.ChildCount++;
	m_Registry.get<RelationshipComponent>(parent).Children.push_back(id);
	m_Registry.get<RelationshipComponent>(child).Parent = m_Registry.get<IDComponent>(parent).ID;
}
```

1. **Lines 948–960:** a root goes to the end of the scene's root list, which has its own first and last links and its
   own vector of `UUID` values, `m_RootEntities`.
2. **Line 957:** the new root's position is the length of the list before it, so the positions of the others stay
   current.
3. **Lines 963–971:** the same for a child: four link writes, the position and the parent's child count.
4. **Lines 972–973:** the saved form: the child's `UUID` added at the end of the parent's vector, and the parent's
   `UUID` in the child. Both forms now agree, in a fixed number of steps whatever the number of children.

## Changing the hierarchy

`Scene::SetParent` moves an entity below a new parent, or makes it a root when the parent is invalid. By default it
keeps the entity where it is in the world. Notice the order of its steps: the checks first, the links next, the
caches after, and the signal last.

```cpp src="Strata/src/Strata/Scene/Scene.cpp#L1270-L1304" symbol="Scene::SetParent"
bool Scene::SetParent(Entity child, Entity parent, bool keepWorldTransform)
{
	if (!child.IsValid() || child.GetScene() != this)
		return false;
	const entt::entity childHandle = child.GetHandle();
	// A cycle needs the new parent below the child; without children nothing is below it (building long chains
	// stays linear).
	if (parent.IsValid() && (parent.GetScene() != this || parent == child || (GetHierarchy(childHandle).ChildCount > 0 && IsDescendantOf(parent, child))))
		return false;

	const entt::entity parentHandle = parent.IsValid() ? parent.GetHandle() : entt::null;
	if (GetHierarchy(childHandle).Parent == parentHandle)
		return true;

	const glm::mat4 worldTransform = keepWorldTransform ? GetWorldTransform(child) : glm::mat4(1.0f);
	// A top-level entity of a sub-scene that becomes a child belongs to its new top-level ancestor's.
	if (parentHandle != entt::null)
		LeaveSubScene(childHandle);
	Unlink(childHandle);
	LinkLast(childHandle, parentHandle);
	m_HierarchyVersion++;
	RecordHierarchyMoves(std::span<const entt::entity>(&childHandle, 1));
	RefreshSubtreeDepth(childHandle, true);
	RefreshSubtreeActivity(childHandle, true);
	// The new parent's world transform applies from now on.
	MarkTransformDirty(childHandle);

	if (keepWorldTransform)
		SetWorldTransform(child, worldTransform);

	// Systems that build state from the hierarchy (physics merges descendants' colliders into a body) learn about the
	// move through the child's on_update signal, emitted once the hierarchy and transform are final.
	m_Registry.patch<RelationshipComponent>(childHandle);
	return true;
}
```

1. **Line 1277:** the cycle check. An entity cannot become its own descendant; the check walks up from the new parent,
   and only when the entity has children, so building a long chain one link at a time stays linear.
2. **Line 1284:** the world transform is read before anything changes.
3. **Lines 1288–1291:** the links change in both forms, the scene's counter of hierarchy changes rises, and the move enters
   the log.
4. **Lines 1292–1298:** the depth and activity of the moved subtree follow the new parent, the entity is marked dirty,
   and with `keepWorldTransform` the old world matrix is set back through `SetWorldTransform`.
5. **Line 1302:** the `RelationshipComponent` signal goes out last, once the hierarchy and transform are final.
   Physics listens to it, because a collision shape below a body joins that body.

:::example[Keeping a child in place]
A parent stands at $x = 10$ with the uniform scale 2, and an entity at the top level stands at $x = 14$. The entity
becomes the parent's child and keeps its world transform. The scene needs a local transform $L$ such that the parent's
world times $L$ gives the old world matrix, so it multiplies the old world matrix by the inverted matrix of the parent.

In one dimension the inverted matrix undoes the parent: subtract its 10, then divide by its 2. The local offset becomes
$(14 - 10) / 2 = 2$ and the local scale $1 / 2 = 0.5$. Check it the forward way: $10 + 2 \times 2 = 14$. Had the
parent's scale been 0, there would be nothing to divide by; `SetWorldTransform` refuses parents whose determinant, the number that says how much a
matrix scales volumes, is not above $10^{-12}$ in size (`c_MinInvertibleDeterminant`). `SetParent` then keeps the entity's old local values,
and the entity moves in the world.
:::

$$
L_{\text{child}} = W_{\text{parent}}^{-1} \, W_{\text{wanted}}
$$

$W_{\text{wanted}}$ is the world matrix the child must keep, and $W_{\text{parent}}^{-1}$ is the parent's world matrix
inverted, read "W parent to the minus one". Multiplied in this order, the parent's part cancels and the local
matrix is left.

The **hierarchy version** is a counter of the scene that rises whenever the order of the hierarchy may have changed:
an entity created, destroyed, moved to another parent or among its siblings. A cache built from the order remembers the
version it was built at, and builds again only when the counter differs. `GetEntitiesInHierarchyOrder` is such a
cache: a walk of the whole tree, parents before children, done once per version.

### Positions among siblings

Moving an entity among its siblings is `SetSiblingIndex`. It changes only the order, so no component signal goes out,
but the version rises and the move is logged. The cached `SiblingIndex` fields of the other siblings are not rewritten
at once. The removal clears the parent's `ChildIndicesValid`, unless the removed child was the last one, and the next
`GetSiblingIndex` on that list numbers all of it in one walk. A list that only grows at its end stays numbered.

The laziness has a cost. A thousand changes followed by one query cost one walk. A change and a
query in turn, repeated, cost a walk each time: the square of the list's length over many deletes (the last section
shows what that cost once).

`PlaceEntities` moves many entities at once, each to a parent and a position: undo uses it to put deleted or moved
entities back. It rebuilds each sibling list it touches once, so restoring a thousand positions in a long list stays
linear. Unlike `SetParent` it keeps local transforms, not world transforms. `IsDescendantOf` walks up from an entity
through its parents and answers whether it meets the given ancestor; its cost is the entity's depth.

### Which entity comes first?

Name searches and the camera search must answer "which of these two entities comes first in the hierarchy?" without a walk
of the scene. `CompareHierarchyOrder` answers by finding where the two paths to the roots meet. Notice the two
climbs and the one comparison at the end.

```cpp src="Strata/src/Strata/Scene/Scene.cpp#L1448-L1476" symbol="Scene::CompareHierarchyOrder"
int Scene::CompareHierarchyOrder(Entity a, Entity b) const
{
	ST_CORE_ASSERT(a.IsValid() && b.IsValid() && a.GetScene() == this && b.GetScene() == this, "CompareHierarchyOrder needs entities of this scene");
	if (a == b)
		return 0;

	entt::entity x = a.GetHandle();
	entt::entity y = b.GetHandle();
	uint32_t depthX = GetHierarchy(x).Depth;
	uint32_t depthY = GetHierarchy(y).Depth;
	for (; depthX > depthY; depthX--)
		x = GetHierarchy(x).Parent;
	// An ancestor comes before its descendants.
	if (x == y)
		return 1;
	for (; depthY > depthX; depthY--)
		y = GetHierarchy(y).Parent;
	if (x == y)
		return -1;

	// Up to the children of the closest common ancestor (or to the roots).
	while (GetHierarchy(x).Parent != GetHierarchy(y).Parent)
	{
		x = GetHierarchy(x).Parent;
		y = GetHierarchy(y).Parent;
	}
	RefreshSiblingIndices(GetHierarchy(x).Parent);
	return GetHierarchy(x).SiblingIndex < GetHierarchy(y).SiblingIndex ? -1 : 1;
}
```

1. **Lines 1458–1466:** the deeper entity climbs until both stand at the same depth. If one is then the other, it was
   an ancestor, and an ancestor comes first.
2. **Lines 1469–1473:** both climb together until they are siblings: children of their closest common ancestor, or two
   roots.
3. **Lines 1474–1475:** the sibling indices decide. If that list changed since it was numbered, it is numbered now,
   once.

For the tree in the diagram above, compare the bolt (depth 2) with wheel B (depth 1). The bolt climbs once, to wheel A.
Wheel A and wheel B have the same parent, so the loop of lines 1469–1473 does nothing. Wheel A's index 0 is less than
wheel B's 1, so the bolt comes first, as it does in the **Hierarchy** panel. The cost is the depth of the deeper
entity, not the size of the scene.

### A log of moves

Caches outside the scene, such as the game interface's ordered lists, need to know which entities moved without
rebuilding everything. `GetHierarchyMoves(sinceVersion, out)` adds to `out` every entity that changed parent or
position after that version. The log holds the latest 4,096 moves (`c_MaxHierarchyMoves`); a reader that asks about
older versions gets `false` and must assume that anything moved. Creating and destroying entities are not moves: they
leave the order of the other entities as it was.

## Signals: how the caches hear about writes

The registry of [EnTT](../world/ecs.md) can call functions when components change. A **signal** is such a call that
the registry makes to every function connected to it when a component of one type is added, updated or removed. EnTT
names the three `on_construct`, `on_update` and `on_destroy`. Adding and removing go through the registry, so their
signals always fire. A write through a reference does not: the registry never sees it.

To **patch** a component is to tell the registry that it was written in place, which fires its `on_update` signal;
`Entity::MarkModified<T>()` patches, and it is the engine-wide way to say "I wrote this". `MarkModified` does nothing
for an entity without that component. Editor commands, scripts and `SetWorldTransform` all patch after they write.

`Scene::ConnectSignals` subscribes the scene's caches when a scene is made. Notice which signals each component gets,
and the one that is missing.

```cpp src="Strata/src/Strata/Scene/Scene.cpp#L194-L206" symbol="Scene::ConnectSignals"
void Scene::ConnectSignals()
{
	m_Connections.emplace_back(m_Registry.on_construct<TransformComponent>().connect<&Scene::OnTransformChanged>(*this));
	m_Connections.emplace_back(m_Registry.on_update<TransformComponent>().connect<&Scene::OnTransformChanged>(*this));
	m_Connections.emplace_back(m_Registry.on_construct<InactiveComponent>().connect<&Scene::OnInactiveAdded>(*this));
	m_Connections.emplace_back(m_Registry.on_destroy<InactiveComponent>().connect<&Scene::OnInactiveRemoved>(*this));
	m_Connections.emplace_back(m_Registry.on_construct<NameComponent>().connect<&Scene::OnNameChanged>(*this));
	m_Connections.emplace_back(m_Registry.on_update<NameComponent>().connect<&Scene::OnNameChanged>(*this));
	m_Connections.emplace_back(m_Registry.on_destroy<NameComponent>().connect<&Scene::OnNameRemoved>(*this));
	m_Connections.emplace_back(m_Registry.on_construct<TagComponent>().connect<&Scene::OnTagChanged>(*this));
	m_Connections.emplace_back(m_Registry.on_update<TagComponent>().connect<&Scene::OnTagChanged>(*this));
	m_Connections.emplace_back(m_Registry.on_destroy<TagComponent>().connect<&Scene::OnTagRemoved>(*this));
}
```

1. **Lines 196–197:** adding a transform and patching one both mark the entity dirty. Removing is not connected:
   `TransformComponent` is registered with a flag that forbids removing it.
2. **Lines 198–199:** adding and removing `InactiveComponent` change activity. The component has no fields, so it has
   no updates.
3. **Lines 200–205:** names and tags: added and patched values are indexed, removed ones leave the index.

The handlers are short; each forwards to the cache it serves. Notice the checks that skip an entity which is not
linked yet.

```cpp src="Strata/src/Strata/Scene/Scene.cpp#L2039-L2064"
void Scene::OnTransformChanged(entt::registry&, entt::entity handle)
{
	MarkTransformDirty(handle);
}

void Scene::OnInactiveAdded(entt::registry& registry, entt::entity handle)
{
	// Components being copied or deserialized before the entity is linked: the linking step computes activity.
	if (m_DestroyingEntities || m_DeferActivityRefresh || !registry.all_of<HierarchyComponent, WorldTransformComponent>(handle))
		return;
	RefreshSubtreeActivity(handle, true);
}

void Scene::OnInactiveRemoved(entt::registry& registry, entt::entity handle)
{
	// Emitted before the component is gone, so the entity counts as active already.
	if (m_DestroyingEntities || !registry.all_of<HierarchyComponent, WorldTransformComponent>(handle))
		return;
	RefreshSubtreeActivity(handle, true, true);
}

void Scene::OnNameChanged(entt::registry& registry, entt::entity handle)
{
	if (m_NameIndex.Built)
		IndexLookupValue(m_NameIndex, handle, registry.get<NameComponent>(handle).Name);
}
```

1. **Line 2041:** a transform write marks the entity dirty, nothing more. The work waits for the next update.
2. **Line 2047:** entities being copied or loaded are not linked yet; the linking step computes their activity later.
3. **Lines 2054–2057:** `on_destroy` fires before the component is gone, so the handler passes `true` to count the
   entity as active already.
4. **Lines 2062–2063:** the name index is updated only once it exists; before the first name search there is nothing to
   keep.

`CreateEntityWithUUID` relies on these handlers: it adds `HierarchyComponent` before every other component, because
`OnTransformChanged` marks through it. The new entity's `TransformComponent` therefore fires `on_construct`, the
entity lands on the dirty list, and the next update computes it whatever its values are by then.

```mermaid caption="A write reaches the world matrix through a signal or a mark; a silent write reaches nothing until the check catches it." alt="A diagram. A write followed by a patch fires the update signal, whose handler marks the entity on the dirty list. Physics marks the entity without a signal. The update reads the dirty list, writes the world matrix and adds to the change log, which the render scene and the game interface read. A write without a signal goes nowhere; in builds made for finding errors the check after the update computes every matrix again and stops at the entity whose cache differs."
flowchart LR
    Write["Write a field"] --> Patch["patch or MarkModified"]
    Patch -->|"on_update"| Handler["OnTransformChanged"]
    PhysicsWrite["Physics writes a pose"] -->|"MarkTransformChanged"| Mark["MarkTransformDirty"]
    Handler --> Mark
    Mark --> DirtyList["Dirty list"]
    DirtyList --> Update["UpdateWorldTransforms"]
    Update --> WorldMatrix["World matrix"]
    Update --> Log["Change log"]
    Log --> Readers["Render scene, game UI"]
    Silent["Write without a signal"] -.->|"nothing"| WorldMatrix
    WorldMatrix --> Check["Debug check after the update"]
    Check -->|"differs"| Assert["Assert naming the entity"]
```

## World transforms, computed where they changed

### Marking

Every path into the dirty list goes through one small function, `Scene::MarkTransformDirty`: it sets the entity's
`TransformDirty` flag and adds the entity to the scene's dirty list, unless the flag was set already. A thousand writes
to one entity in a frame add it once. Marking costs the same whatever the size of the scene, and the work it asks for
waits until the next update.

### The update

`Scene::UpdateWorldTransforms` runs at the end of every editor update and every runtime update. The runtime update
also calls it before the systems run, and around the fixed steps when it draws between them; any code may call it. Notice how it chooses where to start, and how little it does when nothing moved.

```cpp src="Strata/src/Strata/Scene/Scene.cpp#L1597-L1636"
void Scene::UpdateWorldTransforms(TransformPass pass)
{
	ST_PROFILE_FUNCTION();

	if (m_DirtyTransforms.empty())
		return;
	// After the check: a clean update takes nanoseconds, less than timing it would.
	ST_PROFILE_STAGE("Scene.Transforms");

	// The memo of HasDirtyAncestor is keyed by the update; when the key wraps around, old marks could match again.
	if (++m_TransformPass == 0)
	{
		for (HierarchyComponent& node : m_Registry.storage<HierarchyComponent>())
			node.TransformPass = 0;
		m_TransformPass = 1;
	}

	// Subtrees to recompute: the dirty entities without a dirty ancestor (the others are recomputed with that ancestor).
	// Each starts from its parent's cached matrix, which is current.
	std::vector<entt::entity> frontier;
	for (const entt::entity handle : m_DirtyTransforms)
	{
		if (!m_Registry.valid(handle))
			continue;
		const HierarchyComponent& node = GetHierarchy(handle);
		if (node.TransformDirty && !HasDirtyAncestor(node.Parent))
			frontier.push_back(handle);
	}
	m_DirtyTransforms.clear();
	if (frontier.empty())
		return;

	// The walk is instantiated per hook: a scene that does not interpolate (its set is empty) walks without one.
	if (pass == TransformPass::Capture)
		WalkWorldTransforms<TransformHook::Capture>(frontier);
	else if (m_InterpolatedEntities.empty())
		WalkWorldTransforms<TransformHook::None>(frontier);
	else
		WalkWorldTransforms<TransformHook::PerFrame>(frontier);
}
```

1. **Lines 1601–1602:** an empty dirty list returns at once, before even the timing stage starts. A frame where nothing
   moved costs a test of one vector.
2. **Lines 1607–1612:** each update gets a new pass number for the memo of `HasDirtyAncestor`, the answers it stores on
   the entities it climbs through (the next section shows them). When the counter wraps
   around to 0, every stored pass number is set back to 0, so that an old memo can never match again.
3. **Lines 1616–1624:** the frontier: of the dirty entities, those still marked and with no dirty ancestor. An entity
   destroyed since its mark is skipped.
4. **Lines 1630–1635:** the walk is a template, a function the :term[compiler]{id=compiler} makes once for each value of `Hook`. A scene
   that draws no poses between steps walks with no extra test per entity.

Each entity of the frontier starts a walk of its subtree, and every other dirty entity lies inside one of those
subtrees. Each walk starts from its parent's cached matrix, which is
current, because the parent is neither dirty nor below a dirty ancestor.

### Who has a dirty ancestor?

Asking "is any ancestor dirty?" for each dirty entity could cost the depth of the tree each time.

Picture a chain of 1,000 clean entities, one below the other, with 1,000 dirty leaves hanging below the last. Asked naively, each leaf
climbs 1,000 steps: a million steps to find a frontier of 1,000. `HasDirtyAncestor` remembers its answer on every entity
it passes. Notice where it stops early and what it writes on the way back.

```cpp src="Strata/src/Strata/Scene/Scene.cpp#L1530-L1562" symbol="Scene::HasDirtyAncestor"
bool Scene::HasDirtyAncestor(entt::entity parent)
{
	// Memoized for the current update: every entity on a walked path remembers the answer for itself (whether it or an
	// ancestor is dirty), so all the queries of one update together cost at most the number of entities.
	std::vector<entt::entity>& path = m_PathScratch;
	path.clear();
	bool result = false;
	for (entt::entity current = parent; current != entt::null;)
	{
		HierarchyComponent& node = GetHierarchy(current);
		if (node.TransformPass == m_TransformPass)
		{
			result = node.DirtyAbove;
			break;
		}
		if (node.TransformDirty)
		{
			node.TransformPass = m_TransformPass;
			node.DirtyAbove = true;
			result = true;
			break;
		}
		path.push_back(current);
		current = node.Parent;
	}
	for (const entt::entity entity : path)
	{
		HierarchyComponent& node = GetHierarchy(entity);
		node.TransformPass = m_TransformPass;
		node.DirtyAbove = result;
	}
	return result;
}
```

1. **Lines 1540–1544:** an entity already visited in this update knows the answer for itself and everything above it.
2. **Lines 1545–1551:** a dirty entity ends the climb with "yes".
3. **Lines 1555–1560:** every entity on the climbed path stores the answer, with this update's pass number.

In the chain, the first leaf climbs 1,000 steps and leaves the answer "no" on each entity. The second leaf's parent
already knows, so its climb is one step. The whole frontier costs about 2,000 steps instead of a million: in each
update, every entity is climbed through at most once. The test "Many changed entities below unchanged deep ancestors
are found in linear time" holds this.

:::example[Dirty marks walked through]
Take the tree below: root A with children B and C, B with children D and E, C with child F. Three writes this frame
mark B, D and F, in that order. Which entities does the update compute, and in which order?

The frontier: B has no dirty ancestor, so it starts a walk. D's parent B is dirty, so D is not in the frontier: it
will be computed inside B's walk. F's parent C is clean, and so is A, so F starts a walk. The frontier is B and F.

The walk goes level by level. The first level computes B and F, each from its parent's cached matrix. The next level
holds their children: D and E (F has none). Then the level is empty and the walk ends. Four entities were computed, in
the order B, F, D, E; A and C were not touched, and D was computed once, although it was marked.
:::

```mermaid caption="Three marks, two walks: the frontier starts where no dirty ancestor is above." alt="A tree. A has the children B and C, B has the children D and E, and C has the child F. B, D and F are marked. B and F form the frontier and are computed first; D and E are computed in the next level. A and C are not computed."
flowchart TD
    A["A: clean, not computed"] --> B["B: marked, frontier, level 1"]
    A --> C["C: clean, not computed"]
    B --> D["D: marked, below B, level 2"]
    B --> E["E: clean, below B, level 2"]
    C --> F["F: marked, frontier, level 1"]
```

### The walk, level by level

The walk computes a level, gathers the children of everything it computed into the next level, and repeats. Notice
where each entity enters the change log.

```cpp src="Strata/src/Strata/Scene/Scene.cpp#L1734-L1751"
	next.clear();
	for (const entt::entity handle : frontier)
	{
		compute(handle, !firstLevel, m_Captures);
		updated++;
		if (changeCount++ < c_MaxTransformChanges)
			changes.push_back(handle);
		for (entt::entity child = hierarchy.get(handle).FirstChild; child != entt::null; child = hierarchy.get(child).NextSibling)
			next.push_back(child);
	}
	frontier.swap(next);
	firstLevel = false;
}

if (setRecomputed.load(std::memory_order_relaxed))
	m_DrawnStale = true;
m_TransformUpdateCount += updated;
RecordTransformChanges(++m_TransformsVersion, changes, changeCount > c_MaxTransformChanges);
```

1. **Line 1737:** `compute` reads the entity's local transform and composes it with the parent's cached matrix, which
   the previous level wrote.
2. **Lines 1739–1740:** the changed entity enters this update's list of changes, up to the log's size.
3. **Lines 1741–1744:** the children form the next level.
4. **Lines 1750–1751:** the counter that tests read rises by the number computed, the transforms version rises once,
   and the list enters the change log.

### Going parallel

One moved root fans out: its level holds one entity, the next a few, the one after a few more. A level of a handful of
entities is not worth sending to other threads. Once a level holds at least 1,024 independent subtrees
(`c_ParallelTransformWidth`), the walk hands the whole rest of the job to `ParallelFor`. Notice what each job does with
its share of the level.

```cpp src="Strata/src/Strata/Scene/Scene.cpp#L1684-L1731"
if (frontier.size() >= c_ParallelTransformWidth && JobSystem::IsInitialized())
{
	std::atomic<uint64_t> parallelUpdated = 0;
	std::atomic<size_t> parallelChanges = changeCount;
	std::mutex changesMutex;
	const uint32_t count = static_cast<uint32_t>(frontier.size());
	const uint32_t batchSize = std::max<uint32_t>(1, count / (std::max<uint32_t>(1, JobSystem::GetWorkerThreadCount() + 1) * 4));
	JobSystem::ParallelFor(count, batchSize, [&](uint32_t begin, uint32_t end)
	{
		std::vector<entt::entity> stack;
		std::vector<entt::entity> localChanges;
		std::vector<TransformCapture> localCaptures;
		uint64_t localUpdated = 0;
		for (uint32_t index = begin; index < end; index++)
		{
			stack.push_back(frontier[index]);
			bool below = !firstLevel;
			while (!stack.empty())
			{
				const entt::entity current = stack.back();
				stack.pop_back();
				compute(current, below, localCaptures);
				below = true; // Everything after the frontier's entity lies below it
				localUpdated++;
				if (localChanges.size() <= c_MaxTransformChanges)
					localChanges.push_back(current);
				for (entt::entity child = hierarchy.get(current).FirstChild; child != entt::null; child = hierarchy.get(child).NextSibling)
					stack.push_back(child);
			}
		}
		parallelUpdated.fetch_add(localUpdated, std::memory_order_relaxed);
		const size_t first = parallelChanges.fetch_add(static_cast<size_t>(localUpdated), std::memory_order_relaxed);
		if (first < c_MaxTransformChanges || Hook == TransformHook::Capture)
		{
			std::scoped_lock<std::mutex> lock(changesMutex);
			if (first < c_MaxTransformChanges)
			{
				const size_t take = std::min(localChanges.size(), c_MaxTransformChanges - first);
				changes.insert(changes.end(), localChanges.begin(), localChanges.begin() + static_cast<ptrdiff_t>(take));
			}
			if constexpr (Hook == TransformHook::Capture)
				m_Captures.insert(m_Captures.end(), localCaptures.begin(), localCaptures.end());
		}
	});
	updated += parallelUpdated.load(std::memory_order_relaxed);
	changeCount = parallelChanges.load(std::memory_order_relaxed);
	m_ParallelTransformUpdateCount++;
	break;
```

1. **Line 1684:** the switch: 1,024 subtrees in the level, and a job system to run them.
2. **Line 1690:** the batch size gives each thread about four batches, so that a thread that finishes early takes
   another.
3. **Lines 1697–1712:** each job walks its subtrees to the bottom, depth first, with a stack of its own. No two jobs
   share an entity, and each subtree's parent was computed before the jobs began, so they need no locks to compute.
4. **Lines 1714–1726:** each job adds its count to the shared totals once, with an atomic addition, and its changes
   once, under one lock.
5. **Line 1731:** the jobs finished the whole rest of the tree, so the level loop ends.

The parallel walk gives the same matrices as the serial one, because each entity is still computed from its parent's
cached matrix by the same function. Only the order of the entries in the change log differs, and the log's readers
treat it as a set. The test "Large updates run on the job system with the serial results" checks both.

## Reading world transforms between updates

The cache is exact only after an update. Between two updates, a script or an editor tool may move an entity and ask at
once where its child is now. `GetWorldTransform` gives the answer the next update will cache. Notice when it returns
the cache at once and how it computes otherwise.

```cpp src="Strata/src/Strata/Scene/Scene.cpp#L1754-L1787" symbol="Scene::GetWorldTransform"
glm::mat4 Scene::GetWorldTransform(Entity entity) const
{
	if (!entity.IsValid())
		return glm::mat4(1.0f);
	if (entity.GetScene() != this)
		return entity.GetScene()->GetWorldTransform(entity);

	const entt::entity handle = entity.GetHandle();
	const glm::mat4& cached = m_Registry.get<WorldTransformComponent>(handle).Matrix;
	if (m_DirtyTransforms.empty())
		return cached;

	// The path up to the topmost entity that changed since the last update; above it the cache is current.
	std::vector<entt::entity>& path = m_PathScratch;
	path.clear();
	size_t topmost = SIZE_MAX;
	for (entt::entity current = handle; current != entt::null; current = GetHierarchy(current).Parent)
	{
		path.push_back(current);
		if (GetHierarchy(current).TransformDirty)
			topmost = path.size() - 1;
	}
	if (topmost == SIZE_MAX)
		return cached;

	// Top-down like UpdateWorldTransforms, so that the result equals what the cache will hold.
	const entt::entity above = GetHierarchy(path[topmost]).Parent;
	const glm::mat4 topLocal = m_Registry.get<TransformComponent>(path[topmost]).GetTransform();
	glm::mat4 result = above == entt::null ? topLocal
		: Math::ComposeWorldTransform(m_Registry.get<WorldTransformComponent>(above).Matrix, topLocal);
	for (size_t index = topmost; index-- > 0;)
		result = Math::ComposeWorldTransform(result, m_Registry.get<TransformComponent>(path[index]).GetTransform());
	return result;
}
```

1. **Lines 1763–1764:** with an empty dirty list, every cache is current.
2. **Lines 1770–1775:** the climb to the root notes the topmost dirty entity on the path; above it the caches are
   current.
3. **Lines 1780–1785:** from there down, the same composition in the same order as the update, so that the result and
   the later cache agree to the last bit.

`FindCurrentWorldTransform` is the read-only form for worker threads. It climbs the same way but computes nothing: when
the entity or an ancestor is dirty it returns `nullptr`, and the caller treats the entity as changed. Physics compares
its bodies with their entities this way, from several threads, while no thread changes the scene.

`SetWorldTransform` is the writing form. It multiplies the wanted world matrix by the inverted matrix of the parent's world
matrix, turns the result into the local transform through the decomposition and patches it, so every listener hears the change. It refuses
a parent whose determinant is not above $10^{-12}$ in size, and a matrix the decomposition refuses; in both cases it
logs a warning and changes nothing.

`InvalidateAllTransforms` marks every root, so the next update computes the whole scene. Tests use it to compare a full
pass with an update of the changed parts.

### Reports for readers outside the scene

The render scene keeps a copy of every visible entity's world matrix, and the game interface keeps which of its
elements are shown. Neither can afford to read a million entities each frame.

Both remember the transforms version they last
saw and ask `GetWorldTransformChanges(sinceVersion, out)` for the entities whose world matrix or activity changed after
it; the game interface looks only at the activity of the entities it holds. The log holds the latest 16,384 entries (`c_MaxTransformChanges`). An update that computes more than that clears
the log and moves its floor, so a reader asking about an older version gets `false` and copies everything once.
[The render scene](../draw/render-scene.md) shows how the renderer follows the log.

## The transform contract, enforced

### The three rules for writers

The rules of the contract each come from one mechanism of the previous sections.

- **A direct write signals.** For a writer, `OnTransformChanged` is the only door to the dirty list besides
  `MarkTransformChanged`. `ComponentAccess`, the access to component fields that the inspector, the commands and undo
  share, already patches, and so do the script functions and `SetWorldTransform`. Your engine code must do the same
  after writing through `Entity::GetTransform()`.
- **`MarkTransformChanged` marks without a signal.** Physics writes simulated poses back with `MarkTransformsChanged`, the
  form for many entities. A patch would fire `on_update`, which physics itself listens to: it would take its own
  output for an edit, as if someone had moved each body by hand.
- **Writes made after `AddComponent` and before the next update need no signal.** The construct signal marked the
  new entity, and the next update reads its values, whatever they are by then. The same holds for a new `TransformComponent` on any entity.
  For a name or a tag, give the value to `AddComponent` itself: the construct signal indexes the value the component
  has at that moment.

The engine proves the first two rules in one test. Notice the write without a signal, the check that catches it, and
the repair.

```cpp src="StrataTests/src/Scene/SceneTransformTests.cpp#L368-L388"
TEST_CASE("Validation finds transforms written without a signal")
{
	Scene scene;
	Entity parent = scene.CreateEntity("Parent");
	Entity child = scene.CreateChildEntity(parent, "Child");
	scene.UpdateWorldTransforms();

	parent.GetTransform().Translation.x = 5.0f;
	scene.UpdateWorldTransforms();
	std::string error;
	CHECK_FALSE(scene.ValidateWorldTransforms(&error));
	CHECK(error.find("'Parent'") != std::string::npos);
	CHECK(error.find("MarkModified") != std::string::npos);

	// Told without an on_update signal, as physics does.
	scene.MarkTransformChanged(parent);
	CHECK(scene.GetWorldTransform(child)[3].x == doctest::Approx(5.0f));
	scene.UpdateWorldTransforms();
	CHECK(scene.ValidateWorldTransforms(&error));
	CHECK(child.GetComponent<WorldTransformComponent>().Matrix[3].x == doctest::Approx(5.0f));
}
```

1. **Line 375:** a write through the reference, with no signal.
2. **Lines 376–380:** the update computes nothing, and `ValidateWorldTransforms` fails with a message naming the entity
   and asking about `MarkModified`.
3. **Lines 383–384:** `MarkTransformChanged` marks without a signal, and `GetWorldTransform` already gives the child's
   new place before any update.
4. **Lines 385–387:** after the update the cache is right again, and the check passes.

### The check in `Debug` builds

A silent write does no harm on its own frame; the harm shows later, as a wheel drawn where it was. To catch it near
where it happens, `Debug` builds compare the caches with a full pass after each runtime and editor update.
`ValidateWorldTransforms` computes every world matrix again from the roots and compares within a relative $10^{-5}$,
and `ValidateHierarchy` checks the links, depths, positions and indexes. A difference asserts with the entity's name and
`UUID`. Other builds compile the check out ([Conventions](../core/conventions.md)).

A full check costs about 0.01 ms per entity in `Debug`, which the comment in `Scene.h` measured: after every
update, a world of 11,000 entities spent 100 ms a frame on it. So the check is paced by `AmortizedCheck`, which counts
calls, never time. Notice how a call earns its share.

```cpp src="Strata/src/Strata/Core/AmortizedCheck.h#L23-L37"
// Whether to check `elements` elements at this call; true starts the next budget.
bool IsDue(uint64_t elements)
{
	if (!m_Started)
	{
		m_Started = true;
		m_Budget = 0;
		return true;
	}
	m_Budget += m_ElementsPerCall;
	if (m_Budget < elements)
		return false;
	m_Budget = 0;
	return true;
}
```

1. **Lines 26–31:** the first call always checks.
2. **Lines 32–34:** every later call adds its budget, 512 entities for the scene (`c_CacheCheckEntitiesPerUpdate`), and
   checks only once the budget saved since the last check covers the whole scene.
3. **Lines 35–36:** a check starts the next budget from zero.

:::example[When does a scene of 1,111 entities get checked?]
Update 1 checks, because it is the first. Update 2 saves 512, less than 1,111, and update 3 saves 1,024, still less.
Update 4 saves 1,536, which covers 1,111: it checks and starts again from zero. The same count gives checks at updates 7, 10
and so on. A scene of up to 512 entities is checked at every update, because one update's budget always covers it.

On average the check costs about 512 entities' worth per update, about 5 ms in `Debug`, whatever the size of the scene.
The update that checks still pays for every entity. A silent write may be caught a few updates late, or never, when a
later signaled write to the entity or one of its ancestors fixed the cache before the check came. The engine's test for the pace counts exactly updates 1, 4 and 7 in nine:
`Debug builds check a small scene's caches after every update and a large one's every few updates`.
:::

The render scene paces its own check of the [render proxies](../draw/render-scene.md) against the scene the same way, with a budget of 1,024
proxies per `Sync` (`c_ValidatedProxiesPerSync` in `RenderScene.h`). Tests do not wait for the pace: they call
`Tests::CheckSceneCaches`, which checks at once.

### Counters that prove "no walk"

A test cannot see that an update skipped work by looking at the result: a full walk gives the same matrices. So the
scene counts. `GetTransformUpdateCount` is the number of world matrices computed since the scene was made, and
`GetParallelTransformUpdateCount` the number of updates that used the job system. `GetHierarchyOrderBuildCount`,
`GetLookupVisitCount` and `GetLookupIndexBuildCount` count full order builds, entities examined by searches and index
builds. A test reads a counter, does one thing, and checks the difference: moving one leaf of 1,111 entities must add
exactly 1.

## Activity in the hierarchy

An entity can be switched off: `Entity::SetActive(false)` adds `InactiveComponent`, a tag with no fields. Such an
entity and everything below it is not drawn, simulated or updated by scripts. Asking "is any ancestor switched off?" each
time would cost the depth, and the renderer asks for every entity.

**Active in hierarchy** is the state of an entity when neither it nor any of its ancestors has `InactiveComponent`. Strata
stores the answer in `WorldTransformComponent::ActiveInHierarchy` and keeps it exact at once, not at the next update.
`OnInactiveAdded`, `OnInactiveRemoved` and `SetParent` call `RefreshSubtreeActivity`, which walks the affected subtree
and stops below any entity whose flag did not change. `IsActiveInHierarchy` reads the flag in :term[constant time]{id=constant-time}. A common
mistake is to test `HasComponent<InactiveComponent>()` instead: that misses a parent switched off.

Strata keeps no separate version for activity. When the walk changes the flag of some entities, it raises the
transforms version and enters them in the same change log as moved entities, at once. The render scene and the game
interface read activity changes through `GetWorldTransformChanges`, with no second log to follow. A test shows the other side,
`Only the subtrees of changed entities are recomputed`: switching an entity off computes no world matrix.

## Finding entities by name, tag and camera

Games search for entities: the player by name, every enemy by tag, the camera that draws the frame. A search through
every entity would cost the scene's size each time. The scene keeps two indexes instead, one for names and one for
tags, built on the first search and kept current by the signals.

Each index is a :term[hash map]{id=hash-map}: it maps the :term[hash]{id=hash} of a string to a bucket, a vector of
the entities with that name or tag ([Trees and graphs](../basics/trees-graphs.md)). The first search builds its index
in one pass over the entities that have the component. A slot per entity remembers its hash and its place in the
bucket, so removal needs no search. Notice how an entity leaves a bucket of a million.

```cpp src="Strata/src/Strata/Scene/Scene.cpp#L770-L791" symbol="Scene::RemoveLookupValue"
void Scene::RemoveLookupValue(LookupIndex& index, entt::entity handle) const
{
	const size_t slotIndex = static_cast<size_t>(entt::to_entity(handle));
	if (slotIndex >= index.Slots.size() || !index.Slots[slotIndex].Indexed)
		return;

	LookupSlot& slot = index.Slots[slotIndex];
	auto bucket = index.Buckets.find(slot.Key);
	ST_CORE_ASSERT(bucket != index.Buckets.end(), "Scene lookup index: an indexed entity has no bucket");
	if (bucket != index.Buckets.end())
	{
		// Swap with the last entry, so removal does not depend on the bucket's size.
		std::vector<entt::entity>& entities = bucket->second;
		const entt::entity moved = entities.back();
		entities[slot.Position] = moved;
		index.Slots[static_cast<size_t>(entt::to_entity(moved))].Position = slot.Position;
		entities.pop_back();
		if (entities.empty())
			index.Buckets.erase(bucket);
	}
	slot.Indexed = false;
}
```

1. **Lines 776–777:** the entity's slot gives its bucket's key directly.
2. **Lines 781–786:** the last entity of the bucket takes the leaving entity's place, its slot learns its new position,
   and the vector loses its last element. The cost is the same for a bucket of two and a bucket of a million.
3. **Lines 787–788:** an empty bucket leaves the map.

:::example[Renaming a crate]
A bucket for "Crate" holds four entities in the order 7, 12, 30, 41, and entity 12 is renamed "Barrel". The rename
patches its `NameComponent`; `OnNameChanged` finds that the new hash differs and removes 12 first. Entity 41, the last,
moves into position 1, its slot now says 1, and the bucket becomes 7, 41, 30. Then 12 joins the end of the "Barrel"
bucket. The order inside a bucket means nothing; searches sort by hierarchy order when they answer.
:::

`FindEntityByName` looks in one bucket, compares the strings, since two names may share a hash, and keeps the first
entity in hierarchy order with `CompareHierarchyOrder`. `FindEntitiesByTag` collects the bucket's matches and sorts
them the same way. Their cost is the number of entities with that name or tag, plus the comparisons, which may number a
sibling list once. `HasChildNamed` asks whether a parent already has a child of a name, which the editor needs to make
names unique among siblings. It examines the parent's children or the name's bucket, whichever is shorter.

The [primary camera](../gpu/coordinates.md) needs no index. Notice the two tests each camera must pass.

```cpp src="Strata/src/Strata/Scene/Scene.cpp#L867-L881" symbol="Scene::GetPrimaryCameraEntity"
Entity Scene::GetPrimaryCameraEntity()
{
	// Few entities have cameras: examining them all is cheap, and reading Primary here keeps direct writes visible.
	Entity first;
	for (const auto [handle, camera] : m_Registry.view<CameraComponent>().each())
	{
		m_LookupVisitCount++;
		if (!camera.Primary || !m_Registry.get<WorldTransformComponent>(handle).ActiveInHierarchy)
			continue;
		const Entity candidate(handle, this);
		if (!first || CompareHierarchyOrder(candidate, first) < 0)
			first = candidate;
	}
	return first;
}
```

1. **Line 871:** a view over the entities with a `CameraComponent`; few entities have one, so visiting them all is cheap.
2. **Line 874:** a camera counts only when its Primary field is set and it is active in the hierarchy. Reading the field
   here, instead of indexing it, keeps a direct write visible without a signal.
3. **Line 877:** of the cameras that count, the first in hierarchy order wins.

The camera's projection, its fields and how the renderer uses it are [Coordinates](../gpu/coordinates.md)'s subject.

## What a frame of transform updates costs

The performance tests of the `Perf.Scene` suite measure the cost of the walk on the [reference machine](../engineering/perf-lab.md), in a `Release` build, with budgets in
`StrataTests/Perf/Budgets.json`. Their numbers give a cost model you can apply to any frame.

:::example[Pricing a frame]
The test hierarchy has 100,000 entities under one root, ten children per entity, six levels. Moving its root computes
all 100,000 matrices: the metric `MoveRoot100k` measured 0.328 ms, about 3.3 ms per million entities, with the job
system. Moving a leaf computes one: the metric `MoveLeaf100k` measured 0.000114 ms per move. A frame in which
nothing moved computes nothing: the metric `CleanTransformUpdate1M` measured 0.0000013 ms for a million entities, the
cost of finding an empty list.

Now price a frame of your own. Three roots move, each with 1,110 descendants at ten per entity, and one leaf moves
elsewhere. The frontier is 4 entities; the levels hold 4, then 30, then 300, then 3,000.

The level of 3,000 reaches 1,024 subtrees, so it goes to `ParallelFor`. The update computes
$3 \times 1{,}111 + 1 = 3{,}334$ matrices, and at 3.3 ms per million that is about 0.011 ms. Even a million entities moved at once, the metric `MoveRoot1M`, measured
6.6 ms.
:::

The model has one trap. Moving a parent computes its whole subtree, however small the move. A root with 100,000
descendants that sways a little every frame costs 0.33 ms every frame, while 1,000 independent leaves cost a fraction of
that.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Compute every world matrix every frame | small engines and many teaching examples | no dirty marks, no contract for writers | a frame where nothing moved would cost a full walk of a million entities instead of nothing |
| A parent field only, children found by search | the simplest form in the EnTT author's article on hierarchies | one field per entity to keep | finding children would cost a walk of the scene, and siblings would have no order |
| A vector of child handles per parent | Unreal Engine's scene components, which keep their attached children in an array | children and their order in one place, with positions known at once | removals that shift every later child, and memory of its own for every parent |
| Update children at once on every write | Unreal Engine, whose scene components pass a move to their attached children when it happens | world matrices exact at every moment, with no update step | ten writes to one parent in a frame would walk its subtree ten times |
| Compute on read, behind a dirty flag per node | Godot, whose 3D nodes compute their global transform when asked after a change | no update step, and no work for nodes nobody reads | every read would pay a climb, and worker threads could not read while a read fills a cache |
| Change versions per block of entities | Unity's Entities package, whose systems skip blocks of components no one wrote since they last ran | no dirty list per entity | a write to one entity marks a whole block, and readers would still need a finer list to update their copies |

## How it is tested

The scene graph's unit tests live in `StrataTests/src/Scene/`, in three [doctest](../engineering/testing.md) suites, and the performance tests in
`StrataTests/src/Perf/ScenePerfTests.cpp`.

- `Scene.Hierarchy` (`HierarchyTests.cpp`) checks that the handle links follow the saved form through every structural
  change and that positions stay right as sibling lists change. It checks batches of deletes and placements, the order
  built once per version, the moves reported since a version, and `CompareHierarchyOrder` against the hierarchy order.
  Other cases check that the name, tag and camera searches use their indexes.
- `Scene.Transforms` (`SceneTransformTests.cpp`) checks that updates without changes visit nothing and that only
  changed subtrees are computed. It checks that reads between updates equal the next cache and that the parallel walk
  gives the serial results. Its other cases cover activity, the change log and the check that catches a silent write.
- `Scene.Transforms.Sweep` makes random edits and checks every cache against a full pass after each.
- `Perf.Scene.*` holds the walk to its budgets: a clean update of a million entities, and moves of a root and of a leaf.
  Their counts of computed matrices must be exact.

Run them from the engine's build folder; the performance tests need a `Release` or `Dist` build
([The performance lab](../engineering/perf-lab.md)).

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=Scene.Hierarchy,Scene.Transforms*
ctest --preset windows-release -L perf
```

The first line runs the unit suites in `Debug`, where the cache check is on; the second, the performance tests.

## Changing it safely

The scene graph has few extension points: its value is that nothing else writes its data.

- **A new cache of the hierarchy or of world matrices** belongs outside the scene and follows the logs. Remember the
  hierarchy version or the transforms version, ask `GetHierarchyMoves` or `GetWorldTransformChanges`, and rebuild
  everything when they return `false`. The render scene and the game interface do this.
- **A new indexed component field** needs a signal handler connected in `ConnectSignals`, a check in
  `ValidateHierarchy`, and a test that writes with and without a signal.
- **A change of the walk** must keep the composition order of `GetWorldTransform` and `ValidateWorldTransforms`, the one
  function `ComposeWorldTransform`, and the counts the tests read.

:::rule[Change the hierarchy only through the scene]
Hierarchy changes go through the functions of `Scene`, such as `SetParent` and `DestroyEntities`; code never edits
`RelationshipComponent` or `HierarchyComponent` itself. The reason: the two forms, the depths, the positions, the
activity and the hierarchy version must all change together, and only `Scene` writes all of them. The engine's
`AGENTS.md` states the rule under "Architecture rules".
:::

Two more rules protect the costs. Read positions among siblings with `GetSiblingIndex`, which is cached, never by
searching a parent's child vector. And remove many entities with one `DestroyEntities` call ([Scene systems](../world/systems.md) explains
the call). Before
a commit, run `Scene.Hierarchy`, `Scene.Transforms` and its sweep in `Debug`, and the `Perf.Scene` tests in
`Release`.

## What went wrong before

Before wave 1 of the engine's plan rebuilt the scene, deleting 10,000 of 100,000 root entities took 54.6 seconds. The work
gave the scene its cached hierarchy and batched deletes, and the same delete then took about 45 ms, as
`Docs/Roadmap.md` records. Removing one entity from the middle of a long
list makes the list's positions stale, and the next position query numbers all of it. Done one entity at a time,
10,000 removals from a list of 100,000 cost about a billion steps.

`DestroyEntities` removes the whole batch, compacts each sibling list once, and changes the hierarchy version once. The
test `Destroying several entities compacts each sibling list once` in `HierarchyTests.cpp` checks that the version
rises by exactly one for a batch. A performance test in `StrataTests/src/Editor/EditorPerfTests.cpp` holds its metric `Delete10kOf100kRoots` to its
budget (47 ms measured):
`Deleting 10,000 of 100,000 roots is one undo step, and undoing it is fast`.

## Summary

- The hierarchy lives twice: by `UUID` in `RelationshipComponent` for files and order, by handle links in
  `HierarchyComponent` for every hot path, and only `Scene` writes both, together.
- An update computes the subtrees below the frontier, the dirty entities without a dirty ancestor, level by level and in
  parallel once a level holds 1,024 subtrees.
- Engine code that writes a transform, a name or a tag in place signals it, uses `MarkTransformChanged` when its own
  listeners must not hear, and changes the hierarchy only through `Scene`.
- A frame costs the number of matrices it computes, about 3.3 ms per million: a moved parent costs its whole subtree, a
  frame where nothing moved costs nothing.
- Names and tags are found through indexes kept by signals, the primary camera through a pass over the cameras, and
  every answer is put in hierarchy order with `CompareHierarchyOrder`.

## Check yourself

1. A tree has root R with children S and T; S has children U and V; V has child W. This frame marks W, then S, then T.
   Which entities does the update compute, and in which order?

   :::answer{tests="dirty-walk"}
   The frontier is S and T: W has the dirty ancestor S, and R is clean. The first level computes S and T, the second
   their children U and V (T has none), the third W. Five entities, in the order S, T, U, V, W; R is not computed, and W
   is computed once.
   :::

2. Why does `UpdateWorldTransforms` follow `HierarchyComponent` links instead of the `Children` vectors of
   `RelationshipComponent`?

   :::answer{tests="dual-hierarchy"}
   The vectors hold `UUID` values, and each would have to be found in the scene's map to reach the entity's
   components, at every step of every walk. The handle links reach the next entity's storage at once. The vectors stay,
   because handles change between loads and only `UUID` values can be saved; `LinkLast` and the other link functions write both
   forms in each change.
   :::

3. A new system writes the poses of 500 animated props back into their `TransformComponent`s every frame, and patches
   each one, although the system itself listens to `on_update<TransformComponent>` to learn about edits. What goes
   wrong, and what should it call?

   :::answer{tests="contract"}
   Its own patches reach its own listener, so it takes its output for 500 edits and acts on them as if someone had
   moved each prop by hand. It should call `MarkTransformsChanged` with the 500 entities:
   the scene marks them dirty, the world matrices follow, and no `on_update` goes out.
   :::

4. A `Debug` editor holds a scene of 2,000 entities. At which updates does the cache check run, counting from the first?

   :::answer{tests="contract"}
   Update 1 checks because it is the first. Updates 2, 3 and 4 save 512, 1,024 and 1,536, all less than 2,000. Update 5
   saves 2,048, checks and starts again. So the check runs at updates 1, 5, 9, 13 and so on, every fourth update after
   the first.
   :::

5. A frame moves one root with 49,999 descendants in a scene of a million entities. About how long does its transform
   update take on the reference machine, and what does the next frame cost if nothing moves?

   :::answer{tests="frame-cost"}
   The update computes 50,000 matrices; at about 3.3 ms per million, measured by the metric `MoveRoot100k`, that is
   about 0.17 ms. The next frame finds an empty dirty list and computes nothing, whatever the size of the scene.
   :::

6. A scene of 100,000 entities holds 12 tagged "Enemy". What does `FindEntitiesByTag("Enemy")` examine the first time,
   and what the second time?

   :::answer{tests="lookups"}
   The first search builds the tag index, one pass over the entities with a `TagComponent`, then examines the 12
   entities of the "Enemy" bucket and sorts them with `CompareHierarchyOrder`. The second search finds the index built
   and examines only the 12, plus the comparisons of the sort. Tag writes that were signaled kept the index current in
   between.
   :::

## Exercises

1. **Basic.** Trace it yourself in the source build of [your first engine change](../core/first-change.md): the
   installed Strata holds no source. Start `StrataEditor` with `--project` and a sample's copy under the debugger, as
   [Debugging the engine](../core/debugging.md#the-engine-under-a-debugger) starts `StrataTests`. Make it stop in
   `Scene::MarkTransformDirty` once the project is open, send `component.set` for a root entity's `Transform` from `StrataCLI`, and write down
   every function on the chain between the command and the dirty list.

   Then write a doctest case in `StrataTests/src/Scene/SceneTransformTests.cpp` that builds a tree of three levels: a
   root, two children, two children each. Move the root with a signal, and check with `GetTransformUpdateCount` that
   the update computed 7 matrices and a second one none.

   :::answer{tests="dirty-walk,contract"}
   The chain runs from the handler of `component.set`, registered in
   `StrataEditor/src/Editor/Commands/EntityCommands.cpp`, to `CommandUtils::ApplyComponents` in
   `StrataEditor/src/Editor/CommandUtils.cpp`, which writes the values and calls the component's `MarkModified`, a
   `registry.patch`. The patch fires `on_update<TransformComponent>`, which `Scene::ConnectSignals` connected to
   `Scene::OnTransformChanged`, which calls `Scene::MarkTransformDirty` in `Strata/src/Strata/Scene/Scene.cpp`; that
   adds the root to the dirty list that `Scene::UpdateWorldTransforms` reads. In the test, read the counter after a
   first update, move the root, update, and expect a difference of 7; update again and expect 0. Compare yours with
   `Only the subtrees of changed entities are recomputed` in `SceneTransformTests.cpp`.
   :::

2. **Basic.** Reproduce a breach of the contract: in a doctest case, write a parent's `Translation` through
   `Entity::GetTransform()` without a signal, update, and show that `ValidateWorldTransforms` fails with a message that
   names the parent. Then fix the write with `MarkModified<TransformComponent>()` and show that the check passes.

   :::answer{tests="contract"}
   After the silent write, `UpdateWorldTransforms` finds an empty dirty list and computes nothing, so the child's cached
   matrix still holds the old position. `ValidateWorldTransforms(&error)` returns false, and `error` holds the parent's
   name in quotes and asks whether a `TransformComponent` was written without `Entity::MarkModified`. With the patch,
   the parent lands on the dirty list, the update computes it and its child, and the check returns true. The engine's
   own form of this is `Validation finds transforms written without a signal`.
   :::

3. **Medium.** Create 100,000 entities in a tree with ten children per entity, update once, then time 100 updates that
   each move the root, and 100 that each move one leaf. Predict both results before you measure, in matrices computed
   and in time, and compare with the metric `MoveRoot100k` and the metric `MoveLeaf100k`.

   :::answer{tests="frame-cost"}
   Each root move computes 100,000 matrices, and each leaf move computes 1, which `GetTransformUpdateCount` shows
   exactly. In a `Release` build on the reference machine a root move measured 0.33 ms and a leaf move 0.000114 ms; on
   another machine the ratio, about 3,000 to 1, matters more than the numbers. A `Debug` build is far slower and also
   runs the cache check. With the job system running, `GetParallelTransformUpdateCount` rises at each root move, because
   the level of 10,000 entities passes 1,024 subtrees.
   :::

4. **Hard.** Build random trees: create entities, move them under random parents with `SetParent`, and move some among
   their siblings with `SetSiblingIndex`. Number every entity by its place in `GetEntitiesInHierarchyOrder`, and check that the sign of
   `CompareHierarchyOrder(a, b)` matches the sign of the difference of the numbers for many random pairs. Change the tree
   between rounds of comparisons, so that the lazy numbering of sibling lists is tested too.

   :::answer{tests="dual-hierarchy,lookups"}
   Use a fixed random seed so that a failure can be repeated, and skip the cycles `SetParent` refuses: it returns
   false, and the tree stays as it was. For each round, take the order once, map each entity to its position, and
   compare a few thousand pairs, including an entity with itself (0) and an entity with its ancestor (the ancestor
   first). Then move a few entities and run another round without asking any position first: the first comparison that
   meets a changed sibling list numbers it. The engine's own test with fixed trees is `Hierarchy order comparisons agree
   with the hierarchy order` in `HierarchyTests.cpp`; a random form belongs in a suite whose name ends in `.Sweep`.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Scene/Components.h`: `TransformComponent`, `RelationshipComponent`, `WorldTransformComponent`,
  `InactiveComponent`, `NameComponent`, `TagComponent`.
- `Strata/src/Strata/Scene/SceneHierarchy.h`: `HierarchyComponent`.
- `Strata/src/Strata/Scene/Scene.h` and `Scene.cpp`: `SetParent`, `SetSiblingIndex`, `PlaceEntities`,
  `CompareHierarchyOrder`, `UpdateWorldTransforms`, `GetWorldTransform`, `FindCurrentWorldTransform`,
  `SetWorldTransform`, `MarkTransformChanged`, `IsActiveInHierarchy`, `GetWorldTransformChanges`, `GetHierarchyMoves`,
  `FindEntityByName`, `FindEntitiesByTag`, `HasChildNamed`, `GetPrimaryCameraEntity`, `ValidateWorldTransforms`,
  `ValidateHierarchy`, and the diagnostic counters.
- `Strata/src/Strata/Scene/Entity.h`: `Entity::MarkModified`, `Entity::GetTransform`.
- `Strata/src/Strata/Math/Math.cpp`: `DecomposeTransform`, `ComposeTransform`, `ComposeWorldTransform`.
- `Strata/src/Strata/Core/AmortizedCheck.h`: the pacing of the `Debug` checks.
- Tests: `StrataTests/src/Scene/HierarchyTests.cpp`, `StrataTests/src/Scene/SceneTransformTests.cpp`,
  `StrataTests/src/Perf/ScenePerfTests.cpp`; budgets in `StrataTests/Perf/Budgets.json`.
- Commands: `component.set` writes a transform through a patch.
- Other pages: [Drawing between fixed steps](../world/interpolation.md), [The render scene](../draw/render-scene.md),
  [The physics step](../physics/world-step.md), [The contract of the game interface](../ui/contract.md),
  [Sub-scenes](../world/sub-scenes.md), and, for game makers, [Transforms and units](../make/transforms-units.md).

## Further reading

- [Game Programming Patterns, "Dirty Flag"](https://gameprogrammingpatterns.com/dirty-flag.html): the pattern this page
  applies, worked through with a scene graph; beginner.
- [Game Programming Patterns, "Observer"](https://gameprogrammingpatterns.com/observer.html): the idea behind signals,
  with its costs; beginner.
- [Hierarchies, part 4 of a series on entity component systems by the author of EnTT](https://skypjack.github.io/2019-06-25-ecs-baf-part-4/):
  the ways to store a tree in components; intermediate.
- [Unity, "Transforms in Entities"](https://docs.unity3d.com/Packages/com.unity.entities@1.0/manual/transforms-concepts.html):
  parents, children and world matrices in Unity's Entities package; intermediate.
- [Godot, "Node3D"](https://docs.godotengine.org/en/stable/classes/class_node3d.html): local and global transforms of a
  node in Godot; intermediate.
- [Epic Games, the scene component of Unreal Engine](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/Engine/Components/USceneComponent):
  attachment and transforms of Unreal Engine's scene components; advanced.
