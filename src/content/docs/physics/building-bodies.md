---
id: physics/building-bodies
title: "From entities to bodies: records, shapes, mesh colliders"
description: "How Strata turns entities with a RigidBody and colliders into box3d bodies and shapes, and keeps them in line with every edit."
kind: internals
size: L
tracks: [E]
needs: [physics/dynamics, world/systems, core/jobs, assets/loading]
time: 90
learn:
  - id: follow-entity-to-body
    text: trace an entity with colliders to its owner, its record, its box3d body and its shapes
  - id: bake-scale
    text: compute the shape that scale baking gives a box, a sphere and a capsule
  - id: explain-rebuild
    text: explain what an edit rebuilds and what a rebuilt body keeps
  - id: mesh-pipeline
    text: explain how a mesh collider gets its shape without blocking a frame
  - id: pending-suspended
    text: name the reason a body is pending or suspended
since: 0.3.0
status: final
---

A crate in your scene is an entity: a transform, a mesh to draw, a `RigidBody` and a `BoxCollider`. The physics library, box3d, knows nothing about entities. It holds bodies, which are masses with a pose, and shapes attached to them. This page follows the work in between. Strata turns entities with a `RigidBody` and :term[colliders]{id=collider} into box3d bodies and shapes, and keeps them in line with every edit you make while the game runs.

The step itself, which moves the bodies and copies their poses back, belongs to [the world step](world-step.md).

## The problem and how engines solve it

A scene is a tree of entities that people edit, copy, move and destroy at any moment. A physics library wants a flat set of bodies with fixed shapes, held in arrays that its code can walk fast. Engines bridge the two in three ways. The first is to rebuild the whole physics world from the scene before every step, which costs far too much. The second is to make the scene's own components the library's objects, which ties every edit to the library.

The third way is to keep a small record for each entity, listen for edits and rebuild only what an edit touches. Strata takes it. [Collision detection](collision-detection.md) explains what the library does with shapes and [dynamics](dynamics.md) what it does with mass; this page is the glue between them and the scene.

## The map

Physics is a stack of layers. Other systems never touch the library. They reach physics through :term[scene services]{id=scene-service} that the physics system registers while it exists, and only `PhysicsWorld` holds box3d's world. The diagram shows who owns and who uses whom.

```mermaid caption="Other systems reach physics through scene services. The physics system owns one world, which owns the library's world and uses a character controller set, a cache of cooked shapes, a mesh provider and a task system that borrows the job system." alt="A column of boxes from top to bottom: scene systems, scene services, the physics system, the physics world and the library's world. Beside the physics world stand the character controller set, the shape cache and the mesh provider, which leads to the mesh geometry registry. The library's world leads to the task system, which leads to the job system."
flowchart TB
  systems["Scene systems: Scripting, Animation, World, Physics, Audio"]
  services["Scene services"]
  system["PhysicsSystem"]
  world["PhysicsWorld"]
  b3["box3d world"]
  chars["CharacterControllerSet"]
  cache["PhysicsMeshShapes cache"]
  provider["AssetMeshProvider"]
  registry["MeshGeometryRegistry"]
  tasks["PhysicsTaskSystem"]
  jobs["JobSystem"]
  systems --> services --> system --> world --> b3
  world --- chars
  world --> cache
  world --> provider --> registry
  b3 --> tasks --> jobs
```

The "Physics" :term[scene system]{id=scene-system} is registered by `RegisterPhysicsModule` in `Strata/src/Strata/Physics/PhysicsRegistration.cpp`. It runs in Play and Simulate modes. Its order is soft: it runs after "Scripting" when that system exists, so the position a script writes this frame is the position physics simulates. Its profiling stage is Scene.Physics. [Scene systems](../world/systems.md) explains what a soft order is.

The world is made lazily. When the scene starts running, `PhysicsSystem` creates a world only if the scene already has a physics component. Otherwise it listens for the first one and creates the world the next time physics is needed, before a step, query or body call, because a component is usually completed right after it is added. A scene without physics costs nothing.

box3d holds at most 128 worlds at once. Before it makes a world, `PhysicsSystem` asks `PhysicsWorld::HasFreeWorld`. When none is free, the scene plays without physics and the log carries one error.

The library itself is shared by the whole process through `PhysicsRuntime`, which counts its users. The first user installs box3d's hooks: its failed asserts go through Strata's assert handling and its log messages become warnings that start with "box3d: ". Mesh cooking holds a reference too, so the hooks stay until the last user leaves.

Now the data. For every entity that needs a body, `PhysicsWorld` keeps one **body record**: the data that ties an entity to its box3d body, its shapes, its build state and the motion it must resume. A record exists as long as the entity needs a body, also while the body cannot be built. The records live in a `std::map` keyed by entity, which keeps every record at a fixed address until it is erased. Three flat arrays then give constant-time lookups from every direction.

- `RecordIndex` holds a pointer to the record, by entity index. An :term[ordered map]{id=ordered-map} costs a cache miss for each level of its tree, and a streamed cell can read tens of thousands of records in a frame.
- `BodySlots` holds, by box3d body index, the body's generation, its entity and its record.
- `ShapeSlots` holds, by box3d shape index, the generation of the shape and the entity it belongs to.

```mermaid caption="From an entity index, a box3d body or a box3d shape, one array read reaches the record or the entity. Slots remember a generation so that a slot taken by a new shape is recognized." alt="Three rows of arrows. An entity index goes to the record index, which points to a record in the ordered map. A body identifier goes to the body slots, which point to the same record. A shape identifier goes to the shape slots, which hold an entity. The record lists its shapes."
flowchart LR
  ent["Entity index"] --> idx["RecordIndex"] --> rec["BodyRecord in the ordered map"]
  bid["box3d body id: index and generation"] --> bs["BodySlots: generation, entity, record"] --> rec
  sid["box3d shape id: index and generation"] --> ss["ShapeSlots: generation, entity"]
  rec --> shapes["the body's box3d shapes"]
```

A slot stores a generation: a counter that grows each time a new shape or body takes the slot. box3d hands out an index again after its owner is destroyed, so an identifier that names a shape destroyed a moment ago may point at a slot that now holds another shape. Comparing generations tells the two apart.

## The contract

Callers of `PhysicsWorld` and `PhysicsSystem` may assume three things and must do three.

Callers may assume that every body follows its entity's components. Before any step, query or body call, `ApplyPendingChanges` brings the bodies up to date, so a query after an edit sees the edit. A record exists as long as its entity needs a body, and failures :term[return values]{id=return-value} instead of asserting. The identifiers of box3d are resolved safely, as the second rule below explains.

Callers must call from the :term[main thread]{id=main-thread}, signal every edit, and never read an identifier without the check. The first rule has a reason that you know from [the job system](../core/jobs.md).

:::rule[Main thread only]
box3d's world slots are not thread-safe and the scene belongs to the main thread, so worlds are created, changed and destroyed there. Physics runs in parallel inside a step, on the job system, but the result is :term[deterministic]{id=determinism} and no caller sees it.
:::

The second rule protects against stale identifiers. The step reports contacts by shape, and a shape may be destroyed in the same step, for example when a script destroys an entity from a :term[callback]{id=callback}. Strata never trusts an identifier: it resolves shapes and bodies through slots and compares generations.

```cpp src="Strata/src/Strata/Physics/PhysicsWorld.cpp#L1158-L1167" symbol="ResolveShape"
// The entity a shape belongs to as of now, or nullptr for a shape the world does not know (any more): events may name
// shapes destroyed since, whose slots may hold other shapes now.
const ShapeSlot* ResolveShape(const PhysicsWorldData& data, b3ShapeId shape)
{
	const int64_t index = static_cast<int64_t>(shape.index1) - 1;
	if (index < 0 || static_cast<size_t>(index) >= data.ShapeSlots.size())
		return nullptr;
	const ShapeSlot& slot = data.ShapeSlots[static_cast<size_t>(index)];
	return slot.Used && slot.Generation == shape.generation ? &slot : nullptr;
}
```

1. **Line 1160:** The function takes a box3d shape identifier and returns a slot of Strata's, never a pointer into box3d.
2. **Lines 1162–1164:** An index outside the array, such as an identifier that was never issued, resolves to nothing.
3. **Line 1166:** The slot must be in use and carry the same generation, so a stale identifier finds nothing.

The third rule is about edits. The world learns about a change through the scene registry's signals, so code that writes a component's field must signal it: `Entity::MarkModified`, `ComponentAccess` or `Scene::MarkTransformChanged`. A write without a signal is invisible to a sleeping or :term[static body]{id=static-body}. This is the transform contract of [the scene graph](../world/scene-graph.md), applied to physics.

:::rule[Kinematic bodies never recycle contacts]
A :term[kinematic body]{id=kinematic-body}, and the presence body that a character controller keeps (a kinematic capsule on which other bodies land, see [character controllers](character-controllers.md)), turns :term[contact recycling]{id=contact-recycling} off. Recycling stores a contact's points in each body's own frame, which goes wrong while a platform turns and carries riders. On a platform turning at 30 degrees per second the riders drifted 0.70 m in four seconds with recycling, and 17 mm without it.
:::

## A toy version

Before the real code, here is a world that does the job in about a hundred lines. Each entity has a parent, an optional :term[rigid body]{id=rigid-body} and an optional sphere collider. The toy keeps a map from owner entity to body. It records which entities changed, and `ApplyChanges` turns changes into rebuilt bodies, in rounds. It omits almost everything real: boxes and capsules, scale, mass distribution, motion, meshes and failures other than "no collider".

:::question
The sketch uses classes, `std::map` and `std::set`; if those are new, read [classes](../basics/programming-3.md) and [maps and sets](../basics/cpp-generic.md) first.
:::

The sketch builds six entities, prints the bodies, edits one collider, then removes a rigid body. Watch which bodies get built twice.

```cpp sketch="physics-building-bodies-toy.cpp"
#include <cstdio>
#include <map>
#include <set>
#include <string>
#include <utility>
#include <vector>

struct Entity
{
	std::string Name;
	int Parent = -1;
	bool HasRigidBody = false;
	float Mass = 1.0f;
	float Radius = 0.0f; // A sphere collider when above zero
};

struct Body
{
	std::vector<float> Radii;
	float Mass = 0.0f;
	int Builds = 0;
};

// The entity whose body holds this entity's colliders, or -1 when it has no physics components.
int FindOwner(const std::vector<Entity>& entities, int index)
{
	if (entities[index].HasRigidBody)
		return index;
	if (entities[index].Radius <= 0.0f)
		return -1;
	for (int parent = entities[index].Parent; parent >= 0; parent = entities[parent].Parent)
	{
		if (entities[parent].HasRigidBody)
			return parent;
	}
	return index;
}

class ToyWorld
{
public:
	explicit ToyWorld(std::vector<Entity> entities)
		: m_Entities(std::move(entities))
	{
		for (int index = 0; index < static_cast<int>(m_Entities.size()); index++)
			MarkChanged(index);
		ApplyChanges();
	}

	Entity& Get(int index) { return m_Entities[index]; }
	void MarkChanged(int index) { m_Changes.insert(index); }

	// Rounds: a change can hand a collider to another body, which is a change in turn.
	void ApplyChanges()
	{
		for (int round = 0; round < c_MaxRounds && !m_Changes.empty(); round++)
		{
			std::set<int> owners;
			for (int index : m_Changes)
			{
				const int owner = FindOwner(m_Entities, index);
				if (owner != index)
					m_Bodies.erase(index);
				if (owner >= 0)
					owners.insert(owner);
			}
			m_Changes.clear();
			for (int owner : owners)
				Build(owner);
		}
	}

	void Print() const
	{
		for (const auto& [index, body] : m_Bodies)
		{
			std::printf("%-8s shapes %zu, mass %.1f, built %d time(s)%s\n", m_Entities[index].Name.c_str(), body.Radii.size(), body.Mass,
				body.Builds, body.Radii.empty() ? ", pending: no collider" : "");
		}
	}
private:
	void Build(int owner)
	{
		Body& body = m_Bodies[owner];
		body.Radii.clear();
		body.Mass = m_Entities[owner].HasRigidBody ? m_Entities[owner].Mass : 0.0f;
		for (int index = 0; index < static_cast<int>(m_Entities.size()); index++)
		{
			if (m_Entities[index].Radius > 0.0f && FindOwner(m_Entities, index) == owner)
				body.Radii.push_back(m_Entities[index].Radius);
		}
		body.Builds++;
	}
private:
	static constexpr int c_MaxRounds = 16;
	std::vector<Entity> m_Entities;
	std::map<int, Body> m_Bodies;
	std::set<int> m_Changes;
};

int main()
{
	ToyWorld world({ { "Crate", -1, true, 4.0f, 0.0f }, { "Lid", 0, false, 1.0f, 0.5f }, { "Handle", 0, false, 1.0f, 0.25f },
		{ "Boulder", 0, true, 10.0f, 1.0f }, { "Rock", -1, false, 1.0f, 0.3f }, { "Marker", -1, true, 1.0f, 0.0f } });
	world.Print();

	std::printf("-- the handle grows\n");
	world.Get(2).Radius = 0.4f;
	world.MarkChanged(2);
	world.ApplyChanges();
	world.Print();

	std::printf("-- the boulder loses its rigid body\n");
	world.Get(3).HasRigidBody = false;
	world.MarkChanged(3);
	world.ApplyChanges();
	world.Print();
	return 0;
}
```

```text output-of="physics-building-bodies-toy.cpp"
Crate    shapes 2, mass 4.0, built 1 time(s)
Boulder  shapes 1, mass 10.0, built 1 time(s)
Rock     shapes 1, mass 0.0, built 1 time(s)
Marker   shapes 0, mass 1.0, built 1 time(s), pending: no collider
-- the handle grows
Crate    shapes 2, mass 4.0, built 2 time(s)
Boulder  shapes 1, mass 10.0, built 1 time(s)
Rock     shapes 1, mass 0.0, built 1 time(s)
Marker   shapes 0, mass 1.0, built 1 time(s), pending: no collider
-- the boulder loses its rigid body
Crate    shapes 3, mass 4.0, built 3 time(s)
Rock     shapes 1, mass 0.0, built 1 time(s)
Marker   shapes 0, mass 1.0, built 1 time(s), pending: no collider
```

1. **Lines 25–37:** `FindOwner` is the composition rule: a rigid body owns itself and a collider climbs to the nearest rigid body.
2. **Lines 54–71:** `ApplyChanges` loops in rounds, at most 16, until no change is left.
3. **Lines 62–63:** An entity whose owner is another entity loses its own body, as `RefreshOwner` does.
4. **Lines 82–93:** `Build` makes the owner's body from the entities again; the real code visits only the owner's :term[subtree]{id=subtree}.

Three things happened. The first build gave `Crate` two shapes, because `Lid` and `Handle` have no rigid body and belong to the nearest owner above them. `Boulder` and `Rock` each got a body, and `Marker`, a rigid body with no collider, got a record that waits.

The second step rebuilt only `Crate`: the other bodies were not touched. The third step changed `Boulder`'s owner: its sphere moved into the crate's body, so the crate was rebuilt with three shapes. A change to one entity therefore reached the body of a different entity, and that is why changes are applied in rounds.

## The real code

The real world follows the toy's shape and adds what a production engine needs: scale, mass, motion that survives a rebuild, meshes that load late, and a precise answer to why a body is missing. The sections follow the order in which data flows.

### From signals to change lists

The world listens to the scene's EnTT registry. A signal handler never changes a body. It only writes the entity into a list, so that a hundred edits to one entity cost one rebuild.

```cpp src="Strata/src/Strata/Physics/PhysicsWorld.cpp#L3086-L3099" from="ConnectChangeSignals<RigidBodyComponent, &OnStructureChanged>(data, registry);" to="data.Connections.emplace_back(registry.on_destroy<IDComponent>().connect<&OnEntityDestroyed>(data));" symbol="ConnectSignals"
ConnectChangeSignals<RigidBodyComponent, &OnStructureChanged>(data, registry);
ConnectChangeSignals<BoxColliderComponent, &OnStructureChanged>(data, registry);
ConnectChangeSignals<SphereColliderComponent, &OnStructureChanged>(data, registry);
ConnectChangeSignals<CapsuleColliderComponent, &OnStructureChanged>(data, registry);
ConnectChangeSignals<MeshColliderComponent, &OnStructureChanged>(data, registry);
ConnectChangeSignals<MeshRendererComponent, &OnMeshRendererChanged>(data, registry);
// Reparenting (Scene::SetParent) patches the moved entity's relationship; entity creation and destruction are
// reported by the other signals.
data.Connections.emplace_back(registry.on_update<RelationshipComponent>().connect<&OnHierarchyChanged>(data));
data.Connections.emplace_back(registry.on_update<TransformComponent>().connect<&OnTransformChanged>(data));
data.Connections.emplace_back(registry.on_construct<InactiveComponent>().connect<&OnActivityChanged>(data));
data.Connections.emplace_back(registry.on_destroy<InactiveComponent>().connect<&OnActivityChanged>(data));
// Every entity has an IDComponent until it is destroyed, so its removal reports entity destruction.
data.Connections.emplace_back(registry.on_destroy<IDComponent>().connect<&OnEntityDestroyed>(data));
```

1. **Lines 3086–3090:** A rigid body or a collider raises a structure change when it is added, edited or removed.
2. **Line 3091:** A `MeshRenderer` has its own handler, which acts only for entities with a mesh collider.
3. **Lines 3094–3095:** Parent and transform edits feed the subtree and transform lists.
4. **Lines 3096–3097:** Adding or removing the inactive marker is an activity change.
5. **Line 3099:** Destruction is seen as the removal of the identity component, which every entity has until it dies.

There are four lists. Component edits of a rigid body or a collider, and the destruction of an entity, go to the structure list. A `MeshRenderer` edit goes there too when the entity has a mesh collider, because a mesh collider without a mesh of its own borrows the :term[renderer's]{id=renderer}. A parent change goes to the :term[subtree]{id=subtree} list, activity changes to the activity list and transform edits to the transform list. Each list is a vector plus one slot per entity index, so adding an entity twice costs nothing and clearing the list costs what it holds.

`ApplyChanges` empties the lists in rounds, at most 16. A round turns each list into a set of owners to refresh, and a refresh builds, rebuilds or removes a body. Because a refresh can move colliders to another body, which is a new change, the loop runs until the lists are empty. A consistent hierarchy always settles within the limit, so reaching it means a bug: Strata logs an error and drops the rest. Rounds with 256 owners or more build their shapes in parallel; [scale and streaming](scale-streaming.md) explains how.

```cpp src="Strata/src/Strata/Physics/PhysicsWorld.cpp#L2527-L2542" symbol="RefreshOwner"
// Re-evaluates an entity that may own a body: builds or rebuilds the body, or removes the record if the entity no
// longer owns one (destroyed, lost its components, or its colliders now belong to an ancestor's rigid body).
void RefreshOwner(PhysicsWorldData& data, entt::entity handle)
{
	const Entity entity(handle, data.OwnerScene);
	const Entity owner = FindBodyOwner(entity);
	if (owner == entity && entity.IsValid())
	{
		BuildBody(data, entity);
		return;
	}

	DestroyRecord(data, handle);
	if (owner.IsValid())
		data.OwnerRefreshes.Add(owner.GetHandle()); // Its colliders are part of the ancestor's body now
}
```

1. **Lines 2531–2533:** The entity asks `FindBodyOwner` who owns its colliders; one that owns itself gets a body.
2. **Line 2535:** `BuildBody` builds a new body or rebuilds an old one with the same call.
3. **Line 2539:** An entity that no longer owns a body loses its record.
4. **Lines 2540–2541:** If an ancestor owns its colliders now, the ancestor joins the next round's refreshes.

What an edit rebuilds depends on what it touched.

- A property edit of a rigid body or a collider rebuilds that body: the whole body is made again from its components.
- A transform change marks the bodies below the entity so that the next step moves them. It rebuilds a body only if the world scale changed by more than 1e-4 relative to the scale baked into its shapes. Scale 1.0 edited to 1.00005 changes nothing; edited to 1.001 it rebuilds.
- Moving a merged collider, or making it inactive, rebuilds its owner only if that changes the owner's shape. The check compares the collider's pose in the body with the pose the shape was built with.
- A parent change rebuilds only the bodies whose colliders change. A subtree that moves as a whole keeps its bodies and only follows the transform.

### The owner of a collider

The composition rule of [bodies and colliders](bodies-colliders.md) is a loop up the parent chain.

```cpp src="Strata/src/Strata/Physics/PhysicsWorld.cpp#L209-L226" symbol="FindBodyOwner"
// The entity whose body holds this entity's colliders: the entity itself if it has a rigid body, else (if it has
// colliders) its nearest ancestor with a rigid body, or the entity itself (a static body of its own). Invalid for
// entities without physics components.
Entity FindBodyOwner(Entity entity)
{
	if (!entity.IsValid())
		return {};
	if (entity.HasComponent<RigidBodyComponent>())
		return entity;
	if (!HasCollider(entity))
		return {};
	for (Entity parent = entity.GetParent(); parent.IsValid(); parent = parent.GetParent())
	{
		if (parent.HasComponent<RigidBodyComponent>())
			return parent;
	}
	return entity;
}
```

1. **Lines 216–217:** A rigid body always owns itself, even below another one.
2. **Lines 218–219:** An entity with neither a rigid body nor a collider owns nothing.
3. **Lines 220–224:** The loop climbs from the parent and stops at the nearest rigid body.
4. **Line 225:** With no rigid body above, the collider is a static body of its own.

An entity with a rigid body owns itself, even if its parent has one. An entity with colliders and no rigid body asks its ancestors from the nearest one up, and becomes a static body of its own when none has a rigid body. An entity with no physics component returns an invalid entity. A companion, `CollectMergedEntities`, walks the subtree of an owner depth first and stops at descendants with their own rigid body. Events and queries report the owner, so a script sees the crate, not the lid.

### Shapes and baked scale

`AddColliderParts` turns one entity's colliders into shape parts, given the entity's transform in body space. The key idea is that box3d shapes carry no scale, so Strata applies the scale when it builds the shape and writes the result into the shape's numbers. The scale is baked.

```cpp src="Strata/src/Strata/Physics/PhysicsWorld.cpp#L1860-L1890" from="const glm::vec3 absoluteScale = glm::abs(scale);" to="part.Sphere = b3Sphere { ToB3(placeAt(sphere->Offset)), std::max(std::abs(sphere->Radius) * maxScale, c_MinColliderExtent) };" symbol="AddColliderParts"
const glm::vec3 absoluteScale = glm::abs(scale);
const float maxScale = std::max({ absoluteScale.x, absoluteScale.y, absoluteScale.z });
const auto placeAt = [&](const glm::vec3& offset) { return translation + rotation * (offset * scale); };
const size_t partCount = build.Parts.size();

if (const BoxColliderComponent* box = entity.TryGetComponent<BoxColliderComponent>())
{
	build.ColliderCount++;
	if (IsFinite(box->HalfExtents) && IsFinite(box->Offset))
	{
		// Boxes are symmetric, so mirroring needs nothing: the half extents scale by the absolute scale.
		const glm::vec3 halfExtents = glm::max(glm::abs(box->HalfExtents) * absoluteScale, glm::vec3(c_MinColliderExtent));
		ShapePart part;
		part.Type = ShapePart::Kind::Hull;
		part.Hull = GetBoxHull(data, build, halfExtents, ToB3Transform(placeAt(box->Offset), rotation));
		build.Parts.push_back(std::move(part));
	}
	else
	{
		WarnNonFiniteCollider(data, build, entity, "box collider");
	}
}

if (const SphereColliderComponent* sphere = entity.TryGetComponent<SphereColliderComponent>())
{
	build.ColliderCount++;
	if (std::isfinite(sphere->Radius) && IsFinite(sphere->Offset))
	{
		ShapePart part;
		part.Type = ShapePart::Kind::Sphere;
		part.Sphere = b3Sphere { ToB3(placeAt(sphere->Offset)), std::max(std::abs(sphere->Radius) * maxScale, c_MinColliderExtent) };
```

1. **Lines 1860–1862:** The absolute scale, its largest axis and a helper that scales and rotates an offset are made once.
2. **Line 1871:** Box half extents multiply by the absolute scale and never fall under 1 mm.
3. **Line 1874:** The box hull is shared through `GetBoxHull`.
4. **Line 1890:** A sphere's radius uses the largest axis, and its offset is scaled like the box's.

A box scales exactly on each axis, and a mirrored axis needs nothing because a mirrored box is the same box. A sphere has one radius, so it takes the largest absolute axis scale. A capsule takes the larger of the X and Z scales for its radius and the Y scale for its half height.

```cpp src="Strata/src/Strata/Physics/PhysicsWorld.cpp#L1904-L1918" from="const float radius = std::max(std::abs(capsule->Radius) * std::max(absoluteScale.x, absoluteScale.z), c_MinColliderExtent);" to="part.Capsule = b3Capsule { ToB3(center - axis), ToB3(center + axis), radius };" symbol="AddColliderParts"
const float radius = std::max(std::abs(capsule->Radius) * std::max(absoluteScale.x, absoluteScale.z), c_MinColliderExtent);
const float halfHeight = std::abs(capsule->HalfHeight) * absoluteScale.y;
const glm::vec3 center = placeAt(capsule->Offset);
ShapePart part;
if (halfHeight < c_MinColliderExtent)
{
	part.Type = ShapePart::Kind::Sphere; // No cylindrical part
	part.Sphere = b3Sphere { ToB3(center), radius };
}
else
{
	// Along the collider's Y axis, through its center.
	const glm::vec3 axis = rotation * glm::vec3(0.0f, halfHeight, 0.0f);
	part.Type = ShapePart::Kind::Capsule;
	part.Capsule = b3Capsule { ToB3(center - axis), ToB3(center + axis), radius };
```

1. **Line 1904:** The radius uses the larger of the X and Z scales.
2. **Line 1905:** The half height uses the Y scale.
3. **Lines 1908–1911:** A capsule with no straight part becomes a sphere.
4. **Lines 1916–1918:** Otherwise the two end points lie along the collider's Y axis, rotated into body space.

:::example[One scale, three colliders]
An entity has a world scale of (2, 4, 1). Its box has half extents (0.5, 0.5, 0.5), so the shape's half extents are (1, 2, 0.5). Its sphere has radius 0.5 and the largest scale is 4, so the radius becomes 2: a sphere under uneven scale stays round and grows to fit the largest axis. Its capsule has radius 0.3 and half height 0.5, so the radius is 0.3 × 2 = 0.6, the larger of 2 and 1, and the half height is 0.5 × 4 = 2.

Mirroring changes nothing here: a scale of (-2, 4, 1) gives the same numbers, because the code uses absolute values. Every dimension is at least 1 mm, so a sphere of radius 0.0004 becomes 0.001. A capsule whose half height falls under 1 mm becomes a sphere.
:::

Shear is the one case with no exact answer. A non-uniform scale under a rotated parent cannot be written as scale then rotation, so the world uses the scale it finds when it splits the matrix, which approximates it. Three more rules keep building cheap and safe:

- Boxes are shared hulls, made once for each pair of half extents and placement and used again by every body (at most 4,096 shared hulls; later ones belong to their body).
- Spheres and capsules are values: four or seven numbers copied into the shape.
- :term[Convex]{id=convex} mesh colliders use box3d's transformed hulls, which take any non-zero scale including mirroring. Triangle meshes become mesh shapes, except one placed away from its body's origin, which becomes a :term[baked compound]{id=baked-compound} that holds the mesh with its offset.

### The body's definition and its mass

`MakeBodySetup` turns the `RigidBody` component into box3d's definitions. It never trusts the component. Friction and damping that are not finite numbers fall back to the defaults, and negative values become zero. The :term[restitution]{id=restitution} is clamped between 0 and 1. A layer outside 0 to 31 becomes layer 0 with one warning.

```cpp src="Strata/src/Strata/Physics/PhysicsWorld.cpp#L2020-L2037" from="setup.Shape.baseMaterial.friction = SanitizeNonNegative(rigidBody->Friction, defaults.Friction);" to="setup.Body.enableContactRecycling = false;" symbol="MakeBodySetup"
setup.Shape.baseMaterial.friction = SanitizeNonNegative(rigidBody->Friction, defaults.Friction);
setup.Shape.baseMaterial.restitution = std::isfinite(rigidBody->Restitution) ? std::clamp(rigidBody->Restitution, 0.0f, 1.0f) : defaults.Restitution;
setup.Trigger = rigidBody->IsTrigger;
setup.Shape.isSensor = rigidBody->IsTrigger;
setup.Shape.enableContactEvents = !rigidBody->IsTrigger;
if (type == RigidBodyType::Static)
	return setup;

setup.Body.sleepThreshold = data.Settings.SleepThreshold;
setup.Body.linearDamping = SanitizeNonNegative(rigidBody->LinearDamping, defaults.LinearDamping);
setup.Body.angularDamping = SanitizeNonNegative(rigidBody->AngularDamping, defaults.AngularDamping);
setup.Body.gravityScale = std::isfinite(rigidBody->GravityScale) ? rigidBody->GravityScale : defaults.GravityScale;
if (type == RigidBodyType::Kinematic)
{
	// Kinematic bodies never recycle contacts (so neither does what touches them): a recycled contact keeps its points
	// in the bodies' frames while a turning platform carries its riders, which then creep (0.70 m in 4 s on one
	// turning at 30 degrees/s, against 17 mm without recycling; DeveloperGuide "Contact recycling").
	setup.Body.enableContactRecycling = false;
```

1. **Lines 2020–2021:** Friction and restitution are checked and clamped.
2. **Lines 2022–2024:** A trigger makes sensors and reports no contacts.
3. **Lines 2025–2026:** A static body returns here.
4. **Lines 2028–2031:** A moving body gets its :term[sleep threshold]{id=sleep-threshold}, damping and :term[gravity scale]{id=gravity-scale}.
5. **Lines 2032–2037:** A kinematic body turns contact recycling off.

A trigger's shapes become sensors and report no contacts. A static body returns early, because nothing else applies to it. The kinematic branch is the contract's second rule in code: recycling off, and an early return because a kinematic body has no mass. Every shape of a body shares one material.

Mass has two parts that Strata keeps apart: the total, which the component states, and the distribution, which only the shapes know. Every shape is made at density 1, so box3d computes the center of mass and inertia from the shapes alone. `ApplyMass` then scales mass and inertia to the component's mass.

```cpp src="Strata/src/Strata/Physics/PhysicsWorld.cpp#L2100-L2112" symbol="ApplyMass"
// Scales the mass the shapes give a dynamic body (density 1) to the component's mass; the distribution (center and
// inertia) stays the shapes'.
void ApplyMass(b3BodyId body, float mass)
{
	b3Body_ApplyMassFromShapes(body);
	b3MassData massData = b3Body_GetMassData(body);
	if (!(massData.mass > 0.0f) || !std::isfinite(massData.mass))
		return;
	const float factor = mass / massData.mass;
	massData.mass = mass;
	massData.inertia = b3MulSM(factor, massData.inertia);
	b3Body_SetMassData(body, massData);
}
```

1. **Line 2104:** box3d computes mass, center and inertia from the shapes at density 1.
2. **Lines 2106–2107:** A body whose shapes give no usable mass keeps what box3d computed.
3. **Lines 2108–2110:** One factor scales mass and inertia, and the center stays.
4. **Line 2111:** The scaled data replace the body's own.

:::example[A heavy box]
A box of half extents (0.5, 0.5, 0.5) has volume 1 m³, so at density 1 box3d gives it a mass of 1 and, about each axis, an inertia of $m(a^2 + b^2)/12 = 2/12 \approx 0.167$. The component says Mass 4. The factor is 4 / 1 = 4, so the mass becomes 4 and each inertia value becomes 0.667. Add a sphere of radius 0.5 (volume about 0.524) and a component mass of 3. The shapes sum to 1.524, the factor is 3 / 1.524 ≈ 1.97, and the box carries about 66 % of the mass.
:::

:::why[Why density 1 and then a scale]
A designer thinks in kilograms of the whole object ("a crate is 20 kg"), not in density per collider. Scaling afterwards makes the component's number exact, whatever the shapes, and keeps the distribution right when scale changes the shapes. The cost is that two colliders of the same size always weigh the same: a body cannot have a lead core and a hollow shell.
:::

### What a rebuild keeps

A rebuild destroys the box3d body and makes another, but the entity must not notice. The new body starts with the motion the old one had.

```cpp src="Strata/src/Strata/Physics/PhysicsWorld.cpp#L2270-L2286" symbol="GetBuildVelocities"
// The motion a dynamic body (re)built now starts with: a body rebuilt because a property changed keeps moving as before;
// one that was out of the simulation (or had no body after a failed build) resumes the motion it had.
void GetBuildVelocities(const BodyRecord& record, RigidBodyType type, glm::vec3& outLinear, glm::vec3& outAngular)
{
	outLinear = glm::vec3(0.0f);
	outAngular = glm::vec3(0.0f);
	if (type != RigidBodyType::Dynamic)
		return;
	if (record.HasBody() && record.InSimulation)
	{
		outLinear = ToGlm(b3Body_GetLinearVelocity(record.BodyID));
		outAngular = ToGlm(b3Body_GetAngularVelocity(record.BodyID));
		return;
	}
	outLinear = record.SavedLinearVelocity;
	outAngular = record.SavedAngularVelocity;
}
```

1. **Lines 2276–2277:** Only :term[dynamic bodies]{id=dynamic-body} carry motion; the others start at rest.
2. **Lines 2278–2283:** A body in the simulation gives its live velocities.
3. **Lines 2284–2285:** Any other body gives the velocities saved when it left.

A :term[dynamic body]{id=dynamic-body} in the simulation hands its live velocities to its successor. A body that was out of the simulation, or had no body after a failed build, resumes the velocities that `SaveVelocities` stored when it left. Kinematic and static bodies start at rest. The touching pairs also survive, because contacts are tracked per pair of entities and not per shape: the rebuild sends neither an End nor a Begin event.

The test `Property edits rebuild the body and keep its motion` of the suite `Physics.Lifecycle` shows it with numbers. A box moves at 2 m/s. Its `Mass` changes from 1 to 8 through the reflection layer, and the box still moves at 2 m/s. An impulse of 8 then adds 8 / 8 = 1 m/s and gives 3 m/s, so the new mass applies but the motion stayed.

### Mesh colliders

A mesh collider names a mesh asset, or falls back to the mesh of the entity's `MeshRenderer` when it names none. The triangles live in the asset system and the shape is expensive to make, so three players cooperate and none may block a frame.

A **mesh provider** is the source of triangle data for mesh colliders: an object that answers, without blocking, whether the data of a mesh is ready. `GetMeshData` returns nothing while a mesh is unknown or loading, and `PeekMeshData` returns what is loaded without ever starting a load. The provider also reports a version and the meshes that changed since a version, so that physics checks again only the colliders that use them.

The default provider, `AssetMeshProvider`, reads from the active :term[asset manager]{id=asset-manager}. It requests an unloaded mesh, reports it unavailable until it loads and builds the collision data once for each mesh object. It must read triangles without knowing `Mesh`, because physics sits below the renderer in the layering. The asset layer therefore owns a registry, `MeshGeometryRegistry`, and the renderer registers a reader for it in `Strata/src/Strata/Renderer/RendererRegistration.cpp`.

The reader copies the vertex positions and, for every submesh, the indices of its full-detail level, each moved by the submesh's base vertex so that they index the whole vertex list. [Models and glTF](../assets/models-gltf.md) describes the asset side.

**Cooking** is computing collision data ahead of use from those triangles. A convex collider gets a :term[convex hull]{id=convex-hull}. A static collider gets a triangle mesh with its shared edges marked, so that bodies slide over inner edges without catching.

`PhysicsMeshShapes` cooks on the job system and caches the result process-wide for each data object, so that every Play start uses it again. The first request answers "cooking"; the collider is missing from its body until the cook ends, like mesh data still loading. A body whose only collider waits is pending.

Convex hulls need one more step. box3d's hulls hold at most 128 vertices, faces and edges each. A hull of $V$ vertices made only of triangles has $2V - 4$ faces and $3V - 6$ edges.

```cpp src="Strata/src/Strata/Physics/PhysicsMeshShapes.cpp#L72-L86" symbol="CookHull"
// The convex hull of the points: at most c_PreferredHullVertices vertices, else c_SafeHullVertices (see
// PhysicsMeshShapes); null if box3d refuses both.
b3HullData* CookHull(const std::vector<b3Vec3>& points)
{
	const int count = static_cast<int>(points.size());
	{
		// The first attempt may exceed box3d's face or edge limits, which box3d logs; that is expected here.
		Box3DLogSuppression suppression;
		if (b3HullData* hull = b3CreateHull(points.data(), count, std::min(count, PhysicsMeshShapes::c_PreferredHullVertices)))
			return hull;
	}
	if (count <= PhysicsMeshShapes::c_SafeHullVertices)
		return nullptr;
	return b3CreateHull(points.data(), count, PhysicsMeshShapes::c_SafeHullVertices);
}
```

1. **Lines 77–81:** The first attempt asks for at most 64 vertices, and box3d's complaint is hidden.
2. **Lines 83–84:** A point set of 44 points or fewer has nothing smaller to try, so it fails.
3. **Line 85:** The second attempt asks for 44 vertices.

The edge count decides: $3V - 6 \le 128$ allows 44 vertices, with 84 faces and 126 edges, while 64 vertices would need 186 edges. `CookHull` asks for at most 64 vertices first, with box3d's complaint hidden, and on refusal asks for 44, which any hull fits. A hull that fails at 44 has degenerate points and is not usable.

Four more behaviors complete the pipeline.

- Waiting at the start: before the first step, the world holds the simulation while a mesh collider that already exists waits for its data or shape. Nothing moves and no collision events occur, but queries and changes still work, so bodies do not fall through floors that are not there yet. Each held step adds the length of one :term[fixed step]{id=fixed-step} to the held time. At `MeshWaitTimeout` (10 s by default) the simulation starts anyway and warns, naming up to five missing colliders. With a step of 1/60 s that is 600 held steps, and colliders added later are never waited for.
- Hot reload: when the provider reports that a mesh has new data, the bodies that use it rebuild.
- Unloading: a built collider keeps its shape when the asset system unloads its mesh. Physics checks built colliders with `PeekMeshData`, which never loads a mesh again, and the body holds a reference to the cooked shape until it is rebuilt.
- Skinned meshes: the collider of a skinned mesh uses the bind pose, because the pose is drawn and not collided; see [skinning](../animation/skinning.md).

Two limits come from box3d. A triangle mesh has no inside, so a non-convex mesh collider works only on static bodies. A triangle mesh in a trigger must sit at its body's origin, because an offset one is a compound and a compound cannot be a sensor. Both cases log one warning and ignore the collider.

### Bodies out of the simulation

Some entities have a record and no body in the simulation. The record says why.

A pending body has a record but no box3d body. Its `BuildFailure` names the reason, and the table names the event that tries the build again.

| Failure | Meaning | Tried again when |
| --- | --- | --- |
| `NoCollider` | A rigid body with no collider at its entity or below | A component changes |
| `InvalidColliders` | Every collider has data that cannot be used | A component changes |
| `DegenerateTransform` | The :term[world transform]{id=world-transform} cannot be used | A transform change is signaled |
| `MissingMesh` | A mesh collider waits for data or a cook | The provider reports data or a cook ends |
| `WaitingForSlot` | The world is at its growth limit | Another body leaves and frees room |

A **degenerate transform** is a world matrix that cannot be split into translation, rotation and scale, such as one with a zero scale. A body more than 100,000 m from the origin waits in the same way, because box3d's single precision ends there. For a dynamic body, a parent scaled to nearly zero counts as well, because the simulated pose is written back relative to the parent and a zero scale cannot be inverted.

A **suspended body** is a body that was built and then left the simulation because its world transform became degenerate. It returns when a signaled change makes the transform valid. A pending body never had a box3d body in this state, while a suspended one keeps its body and shapes, disabled, and the engine leaves its entity's transform as it is.

Warnings follow a rule that keeps the log short. Each kind is reported once for each entity. The kinds that describe a state, such as a missing collider or a degenerate transform, are reset when the body is built, so a recurring problem is reported again.

An entity also leaves the simulation without any fault. An inactive entity, or one pending destruction, stops colliding in that update, and its contacts end. A dynamic body saves its velocities and resumes them when it returns, also after a rebuild. [Scale and streaming](scale-streaming.md) teaches the parking of static bodies, which makes leaving cheap for a whole cell.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Rebuild the physics world from the scene on every edit | Simple tools and prototypes | No records and no change tracking | Lost motion and contacts at each edit, and cost that grows with the scene |
| Components are the library's objects (the body lives in the component) | Engines built around one physics library | No lookup arrays; edits write straight to the body | Scene code tied to box3d, hard saving and copying, no hierarchy composition |
| Rebuild in place with the library's own functions that change one property | Engines that patch shapes | No destroyed body, so no resumed motion to manage | Many paths to get right; some shape changes have no such function |
| Store scale in each shape and let the library apply it | Libraries with scaled shapes | No baked numbers and no rebuild on scale change | A feature box3d's spheres and capsules lack; the scale rule would live in two places |
| Cook meshes when the asset is imported, store the result | Engines with pipelines that cook ahead of time | No cooking at Play start | Cooked data tied to the library's version, a larger asset and one more import step |

## How it is tested

Tests of this part live in `StrataTests/src/Physics/` and use the helpers of `PhysicsTestUtils.h`: `StepScene` advances a running scene by whole fixed steps, `GetPhysics` returns the system, and `CreateStaticBox`, `CreateDynamicBox` and `CreateDynamicSphere` make entities. `FunctionMeshProvider` and `ScopedMeshProvider` stand in for the asset system. These suites matter most.

- `Physics.Hierarchy` checks the composition rule, new groups when a rigid body is added or removed, a parent change, and that it rebuilds only the bodies that change.
- `Physics.Lifecycle` checks creation and removal of bodies, that property edits rebuild and keep motion, switching an entity off, bodies that wait for a valid transform, and a rebuild in a full world.
- `Physics.MeshColliders` and `Physics.AssetMeshes` check static triangle floors, convex hulls that share a shape, the renderer-mesh fallback, hot reload, ignored meshes that cannot be used, and that unloading a mesh keeps the shape.
- The case `Entity scale is applied to colliders` of `Physics.Simulation` checks scale baking, and `Physics.Settling` checks riders on a moving platform.

Run one suite directly with `build/windows/bin/Debug/StrataTests.exe --test-suite=Physics.Hierarchy`, or the whole physics group through `ctest`. A good regression test fails without its fix: remove the change and watch it fail before you commit.

## Changing it safely

Extension points are narrow. A new collider type touches these places. `AddColliderParts` gets its shape and its scale rule, and `HasCollider` and `CollectMergedEntities` count it as a collider. `ConnectSignals` listens to it, the component registration names it, and the tests cover each scale case and the feature test project. A new body property goes through `MakeBodySetup`, checked like its neighbors, with a rebuild test that checks the motion survives.

Rules that apply, each with its reason:

- Call physics only from the main thread: box3d's world slots are not thread-safe.
- Never use a box3d identifier without resolving it through the slots, because events name shapes that are already gone.
- Keep recycling off for kinematic and presence bodies, or riders creep.
- Every failure to build becomes a `BuildFailure` and a once-only warning, never an assert: bad data comes from users, and a :term[recoverable failure]{id=recoverable-failure} returns and logs.
- Code that writes a component field signals it, or sleeping bodies never learn of the edit.
- A new input that changes how shapes are built must also be a case of the rebuild tests: a rebuild keeps motion and contacts, and a change that loses either is a bug.

Before you commit, run the physics suites in Debug, then the whole test set, since Debug and Release builds check the record index against the map.

## What went wrong before

Riders on a turning kinematic platform drifted 0.70 m in four seconds. The cause was contact recycling: a recycled contact stores its points in each body's own frame, which goes wrong while one body turns under the other. The fix turned recycling off for kinematic bodies in `MakeBodySetup`. The regression test `Boxes ride a moving and turning kinematic platform` of the suite `Physics.Settling` measures how far the riders creep and fails when the branch is removed.

## Summary

- An entity with colliders is followed through its owner, its record in the map, its box3d body and its shapes.
- Scale is baked into shapes: boxes exactly, spheres by the largest axis, capsules by X and Z for the radius and Y for the half height, at least 1 mm.
- An edit rebuilds the body it touches, and the rebuilt body keeps its motion and its contacts.
- A mesh collider waits for the provider and for cooking on jobs, with no blocked frame, and its hulls are reduced to 64 or 44 vertices.
- A pending body has a `BuildFailure`; a suspended body left the simulation with a degenerate transform.

## Check yourself

1. A `Cart` has a kinematic `RigidBody` and a box. Its child `Wheel` has a sphere collider, its child `Seat` has a `RigidBody` and a capsule, and a distant `Sign` has only a box. Which entity does `FindBodyOwner` return for each of the four colliders, and which are static?

   :::answer{tests="follow-entity-to-body"}
   The cart's box returns `Cart`, and `Wheel` returns `Cart`, because its nearest ancestor with a rigid body is the cart. `Seat` returns itself, a separate body. `Sign` returns itself and is the only static body, because it has no rigid body on itself or above. The cart is kinematic, so it never recycles contacts.
   :::

2. A sphere collider has radius 0.5 and a capsule has radius 0.4 and half height 0.6. Their entity has a world scale of (3, 2, 2). What are the shapes' numbers?

   :::answer{tests="bake-scale"}
   The sphere takes the largest scale, 3, so its radius is 1.5. The capsule's radius uses the larger of X and Z, which is 3, so it is 1.2, and its half height uses Y, so it is 0.6 × 2 = 1.2.
   :::

3. A dynamic ball moves at 5 m/s and you change its `Friction` in the inspector. What happens next?

   - A: the body is rebuilt and starts at rest.
   - B: the body is rebuilt, keeps 5 m/s and keeps its touching pairs.
   - C: nothing changes until the next step.
   - D: the body is rebuilt and its pairs end and begin again.

   :::answer{tests="explain-rebuild"}
   B is right: a property edit rebuilds the body, `GetBuildVelocities` hands the live velocities to the new body, and contacts are tracked per pair of entities, so no event is sent. A forgets the motion. C is wrong: the signal queues the edit, and the body is rebuilt before the next step or query, so a query right after the edit sees the new friction. D describes a rebuild that tracks contacts per shape.
   :::

4. A scene starts with a box above a floor made of a mesh collider whose mesh is still loading. What do the first steps do, and what happens after 10 s if the mesh never arrives?

   :::answer{tests="mesh-pipeline"}
   The world holds the steps: nothing moves and no collision events occur, while queries and changes still work. After `MeshWaitTimeout` of simulation time the simulation starts without the floor and logs a warning that names the missing collider. A mesh that arrives later still rebuilds the body, so the floor appears then.
   :::

5. You scale the parent of a dynamic body to zero while the game runs. Is the body pending or suspended, and what brings it back?

   :::answer{tests="pending-suspended"}
   Suspended. The body was built, so it keeps its record and its shapes. It leaves the simulation with one warning, because its pose cannot be written back relative to a parent that cannot be inverted. A signaled transform change that makes the parent valid brings it back, and the engine leaves the entity's transform as it is meanwhile.
   :::

## Exercises

1. **Basic.** Run the sketch to see how many vertices an all-triangle hull may have, then change the limit to 256 and predict the new answer before you run it.

   :::answer[Worked solution]{tests="mesh-pipeline" solution="sketches/physics-building-bodies-hull-limits.cpp"}
   The sketch tries every vertex count, computes $2V - 4$ faces and $3V - 6$ edges, and keeps the largest count under the limit. With 128 the edges decide: 44 vertices. With 256 faces allow 130 vertices and edges allow 87, so the answer is 87. Edges bind first because $3V - 6$ grows faster than $2V - 4$.

   ```cpp sketch="physics-building-bodies-hull-limits.cpp"
   #include <cstdio>
   #include <initializer_list>

   // box3d's hulls hold at most this many vertices, faces and edges each.
   constexpr int c_Limit = 128;

   int main()
   {
   	int largest = 0;
   	for (int vertices = 4; vertices <= 200; vertices++)
   	{
   		// A hull whose faces are all triangles: Euler's formula gives its faces and edges.
   		const int faces = 2 * vertices - 4;
   		const int edges = 3 * vertices - 6;
   		if (faces <= c_Limit && edges <= c_Limit)
   			largest = vertices;
   	}
   	std::printf("largest all-triangle hull that fits: %d vertices\n", largest);

   	for (const int vertices : { 44, 45, 64, 128 })
   	{
   		const int faces = 2 * vertices - 4;
   		const int edges = 3 * vertices - 6;
   		std::printf("%3d vertices: %3d faces, %3d edges, %s\n", vertices, faces, edges, faces <= c_Limit && edges <= c_Limit ? "fits" : "too many");
   	}
   	return 0;
   }
   ```

   ```text output-of="physics-building-bodies-hull-limits.cpp"
   largest all-triangle hull that fits: 44 vertices
    44 vertices:  84 faces, 126 edges, fits
    45 vertices:  86 faces, 129 edges, too many
    64 vertices: 124 faces, 186 edges, too many
   128 vertices: 252 faces, 378 edges, too many
   ```

   1. **Lines 13–14:** Euler's formula gives the faces and edges of an all-triangle hull.
   2. **Line 15:** A hull fits only when both counts stay within the limit.
   3. **Line 20:** The loop then shows four counts, two of which are 44 and 64.
   4. **Line 24:** Each count is printed with its verdict.
   :::

2. **Medium.** An entity has a world scale of (-3, 0.5, 2) and a capsule of radius 0.5 and half height 0.0016. Compute the capsule's shape. Then say what changes when the scale becomes (-3, 1, 2).

   :::answer[Worked solution]{tests="bake-scale"}
   Step 1: the radius is 0.5 × max(3, 2) = 1.5, because the code takes absolute values and the sign of X vanishes. Step 2: the half height is 0.0016 × 0.5 = 0.0008, under 1 mm, so there is no straight part and the capsule becomes a sphere of radius 1.5. Step 3: with Y at 1 the half height is 0.0016, above 1 mm, so the shape is a capsule again, with the same radius 1.5.
   :::

3. **Medium.** Trace it yourself. Start a scene with a rigid body that has two child colliders, a child with its own rigid body, a lone collider and a kinematic platform. Set breakpoints in `FindBodyOwner` and `MakeBodySetup`. For each collider, note the entity returned as owner, and find the branch that turns contact recycling off.

   :::answer[Worked solution]{tests="follow-entity-to-body"}
   `FindBodyOwner` is in `Strata/src/Strata/Physics/PhysicsWorld.cpp`. The two child colliders return the parent that has the rigid body, the child with its own rigid body returns itself, and the lone collider returns itself as a static body. `MakeBodySetup` is in the same file; the kinematic platform reaches the branch `if (type == RigidBodyType::Kinematic)`, which sets `enableContactRecycling` to false and returns early.
   :::

4. **Hard.** Design a hinge joint as a component. Say where its box3d joint lives, when it is created, and what must happen when one of its two bodies is rebuilt.

   :::answer[Worked solution]{tests="explain-rebuild"}
   Step 1: keep the joint in a record of its own, keyed by the joint's entity, and store the two body entities, never box3d identifiers. Step 2: create it only when both bodies exist in the simulation; a missing body gives a pending state like `WaitingForSlot`. Step 3: a rebuild destroys the old body, and box3d destroys the joints attached to it, so the joint must be destroyed and made again after every rebuild of either body, in the same round. Step 4: :term[serialization]{id=serialization} stores the entity references and the anchors, and the rebuild keeps the motion, so the bodies do not jump when the joint is remade.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Physics/PhysicsWorld.cpp` and `PhysicsWorld.h`: records and slots, `FindBodyOwner`, `AddColliderParts`, `MakeBodySetup`, `ApplyMass`, `ApplyChanges`, `RefreshOwner`, `HoldForMeshes` and the signal handlers.
- `Strata/src/Strata/Physics/PhysicsTypes.h`: `PhysicsMeshProvider`, `PhysicsMeshData` and `PhysicsSettings` with `MeshWaitTimeout`.
- `Strata/src/Strata/Physics/PhysicsMeshShapes.h` and `.cpp`: cooking and its cache, `CookHull`, the 64 and 44 vertex limits.
- `Strata/src/Strata/Physics/AssetMeshProvider.h` and `.cpp`: the default provider; `Strata/src/Strata/Renderer/RendererRegistration.cpp`: `ReadMeshGeometry`.
- `Strata/src/Strata/Physics/PhysicsSystem.cpp`, `PhysicsRegistration.cpp` and `PhysicsRuntime.h`: the "Physics" scene system, the lazy world, the world limit and the hooks.
- Tests: `StrataTests/src/Physics/PhysicsTestUtils.h` and the suites `Physics.Hierarchy`, `Physics.Lifecycle`, `Physics.MeshColliders`, `Physics.AssetMeshes`, `Physics.Simulation` and `Physics.Settling`.
- Settings: `MeshWaitTimeout` of the physics settings (10 s).

## Further reading

- Erin Catto, the box3d project and its documentation: how the library's bodies, shapes and hulls work; intermediate.
- Christer Ericson, "Real-Time Collision Detection": convex hulls and the cost of shapes; advanced.
- Ian Millington, "Game Physics Engine Development": mass, inertia and bodies from first principles; intermediate.
- Robert Nystrom, "Game Programming Patterns", chapter "Data Locality": why records are indexed by flat arrays; beginner.
