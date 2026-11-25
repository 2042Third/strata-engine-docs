---
id: world/ecs
title: "Entities and components, with EnTT inside"
description: "How a Strata scene stores its entities and their components in an EnTT registry, names each entity by a UUID, and what a program may keep."
kind: internals
size: L
tracks: [E]
needs: [world/what-a-world-is, basics/cpp-generic, core/conventions]
time: 80
learn:
  - id: storage
    text: predict where a sparse set puts an element and which element moves when another is removed
  - id: identifiers
    text: explain which identifier of an entity survives saving, copying and destruction
  - id: contract
    text: write engine code that adds, reads, removes and visits components without keeping a reference past its safe moment
  - id: creation
    text: trace what the scene creates for every new entity and in which order
  - id: kinds
    text: name which components are plain data, tags, registered or runtime-only
since: 0.3.0
status: final
---

A scene holds many things: a crate, a player, a lamp, a camera. The `Scene` class stores each of them as an entity and
keeps their data in one registry of the library EnTT, version 3.16. It also gives every entity a persistent identifier,
a universally unique identifier (UUID), so that a saved file, a copy of the scene and a script can all name the same crate. Every call runs on the :term[main thread]{id=main-thread}.

This page covers how entities are named, created, given data and found. The links between parents and children, the
systems that run every frame and the files that store scenes belong to later pages.

## The problem and how engines solve it

Suppose a level holds 2,000 things: 1,500 crates, 400 lamps, 99 enemies and the player. Every thing has a position.
Only the lamps have a light, and only the enemies and the player have health. A program asks two questions all the time:
which data does this one thing have, and which things have this kind of data, so that the lamps can all be visited?

[What a world is](../world/what-a-world-is.md) compares the answers. Objects with inherited classes make the data of a
thing a fixed shape from the day it is written. Entities and components keep the data apart from the thing and let you
add or remove a piece at any time.

Strata takes the second, and lets a library do the storing instead of writing the storage itself. The rest of this page
builds that storage from the bottom up. Three words carry the design.

An **entity** is a number that names one thing in the scene and holds no data of its own.

A **component** is a small plain record of data about one side of an entity, such as its position or its name, stored
under the entity's number.

A thing is then the set of components that carry its number. Give a crate a `TransformComponent` and a
`MeshRendererComponent` and it can be seen. Give it a light component as well and it is a lamp, with no new class written.

## A map of the code

The scene owns a handful of structures. Most of the page's questions reduce to which one of them holds what, so read the
map first and return to it.

```mermaid caption="What a scene holds: one registry with a storage for each component type, and the lookups, lists and running parts beside it." alt="A box for the scene points to six boxes: the registry, a map from identifiers to entities, a list of root entities, the caches, the systems with their services, and the context. The registry box points to the storage of entity numbers and to one storage for each component type."
flowchart TD
    S["Scene: main thread only"]
    R["entt::registry"]
    M["m_EntityMap: UUID to entity"]
    L["m_RootEntities: UUIDs of entities without parent"]
    C["caches: dirty list, hierarchy links, name and tag indexes"]
    Y["systems and services of a running scene"]
    X["context: one object per type"]
    E["storage of entity numbers"]
    T["one storage per component type"]
    S --> R
    S --> M
    S --> L
    S --> C
    S --> Y
    R --> X
    R --> E
    R --> T
```

The **registry** is EnTT's container: it owns the entity numbers and one storage for each component type. The scene
asks it to create, destroy, add, read and remove, and never keeps a second copy of what it stores. Beside it stands
`m_EntityMap`, a dense map from `UUID` to entity number, so that a persistent name leads to the entity in one lookup.
The list `m_RootEntities` holds the `UUID` of every entity that has no parent, in order.

The caches belong to the scene graph: the dirty list of transforms, the hierarchy links, and the indexes of names and
tags. [The scene graph](../world/scene-graph.md) teaches how they stay true. The systems and the services they offer to
one another exist only while a scene runs, and [Scene systems](../world/systems.md) teaches them. The context is a
place inside the registry for one object per type; a later section shows what lives there.

## The contract

What may a caller assume, and what must it do? Six rules follow, each with its reason. The sections after them show the
reasons in code.

1. **Call from the main thread.** The scene is not locked. Background work hands results to the main thread, as
   [Jobs](../core/jobs.md) teaches.
2. **Hold a `UUID`, never an `Entity` or a `T&`, across a frame, a copy or a change of components.** A removal moves
   another component, a handle is recycled, and a copy of the scene is a different scene.
3. **Never call `GetComponent` for a tag component.** An empty type has no data to return, and the :term[compiler]{id=compiler} refuses
   the call.
4. **Check the entity that creation returns.** A scene holds at most 1,048,575 entities, and one more returns an
   invalid entity and logs an error.
5. **Signal a write in place.** Code that changes a component in the registry without adding it tells the scene with
   `MarkModified`; [The scene graph](../world/scene-graph.md) says why.
6. **Change the hierarchy through `Scene`.** Parents and children have two stored forms that only `Scene` keeps equal.

:::rule[Hold UUIDs, not handles]
Do not keep an `Entity`, an EnTT handle or a `T&` across frames or across copies of a scene; keep the `UUID` and find
the entity again with `GetEntityByUUID`. Handles are recycled, play mode runs on a copy of the edited scene, and EnTT
moves components when others are removed. [Handles and UUIDs](#handles-and-uuids) shows each of the three.
:::

## A toy version

Before EnTT's code, here is the structure it is built on, as a short program. A :term[sparse set]{id=sparse-set} stores the elements of a set
in a packed array and finds each one from its key through a second, sparse array indexed by the key.
[Data structures](../basics/data-structures.md) teaches the structure and its cost; the program adds what a game needs
on top, a value stored with each element.

:::question
This sketch uses a class template, `std::vector` and a :term[lambda]{id=lambda}. If those are new, read [Classes](../basics/programming-3.md)
and [Generic C++](../basics/cpp-generic.md) first.
:::

The set below keeps three arrays. The sparse array is indexed by the entity number and holds the position of that
entity in the packed arrays, or an empty mark. The dense array holds the entity numbers one after another, and a third
array holds their values in the same order. Search for `Remove`: it fills the hole by moving the last element into it.

```cpp sketch="world-ecs-toy.cpp"
// A toy sparse set (emplace, remove by swapping with the last element, contains, iterate) and a view over two of them.
#include <cstdint>
#include <cstdio>
#include <string>
#include <vector>

namespace
{
	constexpr uint32_t c_Empty = 0xFFFFFFFF;

	template<typename T>
	class SparseSet
	{
	public:
		void Emplace(uint32_t entity, T value)
		{
			if (entity >= m_Sparse.size())
				m_Sparse.resize(entity + 1, c_Empty);
			m_Sparse[entity] = static_cast<uint32_t>(m_Dense.size());
			m_Dense.push_back(entity);
			m_Values.push_back(value);
		}

		void Remove(uint32_t entity)
		{
			const uint32_t hole = m_Sparse[entity];
			const uint32_t last = m_Dense.back();
			m_Dense[hole] = last; // the last element moves into the hole
			m_Values[hole] = m_Values.back();
			m_Sparse[last] = hole;
			m_Sparse[entity] = c_Empty;
			m_Dense.pop_back();
			m_Values.pop_back();
		}

		bool Contains(uint32_t entity) const { return entity < m_Sparse.size() && m_Sparse[entity] != c_Empty; }
		uint32_t PositionOf(uint32_t entity) const { return m_Sparse[entity]; }
		T& Get(uint32_t entity) { return m_Values[m_Sparse[entity]]; }
		const std::vector<uint32_t>& Entities() const { return m_Dense; }
	private:
		std::vector<uint32_t> m_Sparse; // entity -> position in the packed arrays
		std::vector<uint32_t> m_Dense;  // the entities, packed
		std::vector<T> m_Values;        // their values, in the same order
	};

	// Walks the shorter set and asks the other one: the work follows the rarer component.
	template<typename A, typename B, typename Function>
	void ForEachWith(SparseSet<A>& first, SparseSet<B>& second, Function function)
	{
		const auto visit = [&](uint32_t entity)
		{
			if (first.Contains(entity) && second.Contains(entity))
				function(entity, first.Get(entity), second.Get(entity));
		};
		const std::vector<uint32_t>& walked = first.Entities().size() <= second.Entities().size() ? first.Entities() : second.Entities();
		for (uint32_t entity : walked)
			visit(entity);
	}

	void Print(const char* label, const std::vector<uint32_t>& entities)
	{
		std::printf("%s:", label);
		for (uint32_t entity : entities)
			std::printf(" %u", entity);
		std::printf("\n");
	}
}

int main()
{
	SparseSet<std::string> names;
	SparseSet<int> healths;
	const char* spelled[] = { "Ada", "Bo", "Cy", "Di", "Ed" };
	for (uint32_t entity = 0; entity < 5; entity++)
		names.Emplace(entity, spelled[entity]);
	healths.Emplace(1, 10);
	healths.Emplace(3, 30);
	healths.Emplace(4, 40);

	Print("names, packed", names.Entities());
	std::printf("entity 4 sits at position %u\n", names.PositionOf(4));
	names.Remove(1);
	Print("names after removing entity 1", names.Entities());
	std::printf("entity 4 sits at position %u, entity 1 has a name: %s\n", names.PositionOf(4), names.Contains(1) ? "yes" : "no");

	ForEachWith(names, healths, [](uint32_t entity, const std::string& name, int health)
	{
		std::printf("view: entity %u is %s with %d health\n", entity, name.c_str(), health);
	});
	return 0;
}
```

```text output-of="world-ecs-toy.cpp"
names, packed: 0 1 2 3 4
entity 4 sits at position 4
names after removing entity 1: 0 4 2 3
entity 4 sits at position 1, entity 1 has a name: no
view: entity 3 is Di with 30 health
view: entity 4 is Ed with 40 health
```

1. **Lines 24–34:** `Remove` fills the hole with the last element in the packed arrays, points the moved entity's sparse
   entry at the hole, and empties the removed entity's entry.
2. **Line 36:** `Contains` reads one array, the sparse one, so "does this entity have the component" costs one read.
3. **Lines 41–43:** the three arrays: sparse by entity number, and two packed arrays that move together.
4. **Lines 46–58:** `ForEachWith` walks the shorter set and asks the other, so the work follows the rarer component.
5. **Line 82:** the removal in `main`; the lines around it print the positions before and after.

:::example[Five names, three healths, one removal]
Entities 0 to 4 get a name; entities 1, 3 and 4 get health. The names set holds the dense array 0, 1, 2, 3, 4, and the
sparse array maps each number to its own position. Removing the name of entity 1 empties position 1. The last element,
entity 4, moves into it: the dense array becomes 0, 4, 2, 3, and the sparse entry of entity 4 changes from 4 to 1.
Nothing else moved, so the removal cost three writes whatever the size of the set.

Now visit every entity that has a name and a health. The view walks the shorter set: the healths hold 3 entities, the
names 4 after the removal. It visits 1, 3 and 4 and asks the names about each. Entity 1 has none, so only 3 and 4 are
visited.
:::

The picture shows the removal of the example: the packed array of names before and after.

```mermaid caption="Removing the name of entity 1 does not close the gap by shifting; the last entry, entity 4, fills the hole." alt="Two rows of boxes. The first row holds the entities 0, 1, 2, 3 and 4 in order. The second row holds 0, 4, 2 and 3: the box of entity 4 stands where entity 1 stood, and the row is one box shorter."
flowchart LR
    subgraph before["Before: entities 0 to 4"]
        direction LR
        b0["0"] --> b1["1"] --> b2["2"] --> b3["3"] --> b4["4"]
    end
    subgraph after["After removing entity 1"]
        direction LR
        a0["0"] --> a1["4"] --> a2["2"] --> a3["3"]
    end
    before --> after
```

The toy showed four things. Adding and removing take a fixed number of steps. A packed array is visited without a gap.
A check "does this entity have the component" reads one array. And the entity whose component moved, 4 here, changed its
position without anyone telling the holder of a reference to it.

## The real code

### Removal moves another element

EnTT's :term[sparse set]{id=sparse-set} does what the toy does, with extra care for entities that were destroyed and numbers that carry a
version. A component storage is a sparse set of entity numbers plus the matching component values. EnTT keeps the values
in pages of 1,024 elements and the sparse array in pages of 4,096 entries, so numbers that were never used cost
nothing. The core of removing one entity is this function.

```cpp src="vendor:entt/src/entt/entity/sparse_set.hpp#L264-L276"
    void swap_and_pop(const basic_iterator it) {
        ENTT_ASSERT(mode == deletion_policy::swap_and_pop, "Deletion policy mismatch");
        auto &self = sparse_ref(*it);
        const auto entt = traits_type::to_entity(self);
        sparse_ref(packed.back()) = traits_type::combine(entt, traits_type::to_integral(packed.back()));
        packed[static_cast<size_type>(entt)] = packed.back();
        // unnecessary but it helps to detect nasty bugs
        // NOLINTNEXTLINE(bugprone-assert-side-effect)
        ENTT_ASSERT((packed.back() = null, true), "");
        // lazy self-assignment guard
        self = null;
        packed.pop_back();
    }
```

1. **Lines 266–267:** find where the removed entity sits in the packed array.
2. **Line 268:** the last entity's sparse entry now points at that position.
3. **Line 269:** the last entity is copied into the hole of the packed array.
4. **Lines 274–275:** the removed entity's sparse entry is emptied and the packed array loses its last entry.

The storage moves the component value in the same way, in `pop` of `storage.hpp`, so the entity numbers and the values
stay in step. The consequence is the one the toy printed. After `RemoveComponent<T>()` on one entity, the last
entity's component of type `T` lives where the removed one did.

A `T&` or `T*` taken for that last entity before the removal now names another entity's data, or nothing. EnTT does not
promise that addresses stay put when components are added either. Strata's rule is therefore blunt: take the reference,
use it, and drop it before anything adds or removes a component of that type.

A component whose type cannot be moved is the exception. EnTT leaves a hole for such a type instead of moving another
element, and its addresses stay. Strata's scene components are ordinary :term[structs]{id=struct} that EnTT may move, so the rule applies to all of
them.

### Handles and UUIDs

An entity is a number, and there are two kinds of number for it. A **handle (EnTT)** is the 32-bit value that EnTT
gives an entity: the low 20 bits are an index and the high 12 bits a version. The index says which slot of the registry
the entity uses. When the entity is destroyed, its slot is free again and the next entity can take it. The version
counts how often the slot was used, so an old handle can be told from the new one.

:::example[One slot, two entities]
An entity sits in slot 5 with version 0: its value is $0 \times 2^{20} + 5 = 5$. Destroy it, and the
slot's version becomes 1. The next entity created takes slot 5 again, and its value is
$1 \times 2^{20} + 5 = 1{,}048{,}581$. A program that kept the value 5 asks the registry whether it is valid; the registry
compares versions, finds 0 against 1, and answers no. Without the version the program would have written to the new,
unrelated entity.

The version is only 12 bits. EnTT counts 0 up to 4,094 and then returns to 0, so after 4,095 destructions in one slot an
old handle is valid again. The sketch in the exercises shows it.
:::

The index uses 20 bits and its largest value is the null mark, so a registry holds at most $2^{20} - 1 = 1{,}048{,}575$
live entities. `Scene::c_MaxEntities` is that number, taken from EnTT's own constant.

A handle fits the registry well and the file badly. Its value depends on the order in which entities were created and
destroyed, and a loaded scene creates its entities again. Strata therefore adds a second identifier, the `UUID`: a
64-bit random value, held in `IDComponent`, that never changes while the entity lives, is written to files, and is
carried by copies. The whole class is short.

```cpp src="Strata/src/Strata/Core/UUID.h#L13-L44"
	// 64-bit random identifier used for entities and assets. Zero is reserved as the invalid/null value
	// and is never generated. The canonical text form is 16 upper-case hexadecimal digits.
	class UUID
	{
	public:
		UUID(); // Generates a new random, non-zero UUID
		constexpr UUID(uint64_t uuid)
			: m_UUID(uuid)
		{
		}

		constexpr operator uint64_t() const { return m_UUID; }
		constexpr bool IsValid() const { return m_UUID != 0; }

		std::string ToString() const;
		static std::optional<UUID> FromString(std::string_view text);

		static constexpr UUID Null() { return UUID(uint64_t(0)); }
	private:
		uint64_t m_UUID;
	};

}

template<>
struct std::hash<Strata::UUID>
{
	size_t operator()(const Strata::UUID& uuid) const noexcept
	{
		return std::hash<uint64_t>()(static_cast<uint64_t>(uuid));
	}
};
```

1. **Lines 13–14:** the comment states the choices: 64 bits, random, zero reserved as the null.
2. **Line 18:** the default :term[constructor]{id=constructor} makes a new random, non-zero value.
3. **Line 25:** `IsValid` is false only for zero.
4. **Lines 27–28:** the text form and its parser, which returns nothing for bad text.
5. **Lines 37–44:** the :term[hash]{id=hash} for the scene's map is the hash of the 64-bit number.

Two choices stand in the class. Zero is the null: `IsValid()` is false for it and the random generator never returns
it, so a field of zero means "no entity" and never names a real one. The text form is 16 upper-case :term[hexadecimal]{id=hexadecimal} digits,
for 64 bits at 4 bits a digit; [Data formats](../basics/data-formats.md) teaches hexadecimal text. The `std::hash`
part at the end lets the scene use a `UUID` as the key of its map.

:::why
Standard UUIDs have 128 bits. Strata uses 64 because the value has to be cheap to compare, copy and :term[hash]{id=hash}, and to
store in every file that names an entity. With a random 64-bit value, two entities of one scene collide with a chance
near one in $1.8 \times 10^{19}$ per pair. The scene also checks every new `UUID` against its map, so a collision costs
a replaced value and an error message, never two entities with one name. The price is that 64 random bits are not a global
guarantee between machines: a tool that merges scenes made apart must still check.
:::

The table shows what survives what.

| Event | Handle value | `Entity` object | `UUID` |
| --- | --- | --- | --- |
| The entity is destroyed and its slot is taken again | Old value fails the version check, until the version returns to 0 | Invalid, as it holds the old handle | Gone with the entity |
| The scene is saved and loaded | Not written; the load creates new handles | Not saved | Written and read back |
| The scene is copied to play it | The same value today, which Strata does not promise | Still points at the source scene | Equal in the copy |

The last cell of the second column is the trap. An `Entity` holds a handle and a pointer to its scene. Copy the scene
for play mode and an `Entity` kept from the edited scene still points at the edited scene, so a write through it changes
the original. [Scene systems](../world/systems.md) teaches the copy.

### The Entity class

Engine code rarely uses the registry directly. It uses `Entity`, a handle plus a pointer to the scene, and calls that
forward to the registry. The class does not own the entity; copies are cheap, and destroying a copy destroys nothing.

:::question
The next quotes use templates, perfect forwarding with `std::forward` and `decltype(auto)`. If they are new, read
[Generic C++](../basics/cpp-generic.md) and [Modern C++](../basics/cpp-modern.md).
:::

The first excerpt shows the :term[constructor]{id=constructor} and the two ways to add a component. Look at what they return.

```cpp src="Strata/src/Strata/Scene/Entity.h#L12-L35"
// Lightweight handle to an entity in a scene (an EnTT entity plus its scene). Copy freely; it does not own
// the entity. Handles of destroyed entities become invalid (IsValid() returns false).
class Entity
{
public:
	Entity() = default;
	Entity(entt::entity handle, Scene* scene)
		: m_EntityHandle(handle), m_Scene(scene)
	{
	}

	// Returns the new component (nothing for empty tag components, which carry no data).
	template<typename T, typename... Args>
	decltype(auto) AddComponent(Args&&... args)
	{
		ST_CORE_ASSERT(!HasComponent<T>(), "Entity already has the component");
		return m_Scene->m_Registry.emplace<T>(m_EntityHandle, std::forward<Args>(args)...);
	}

	template<typename T, typename... Args>
	decltype(auto) AddOrReplaceComponent(Args&&... args)
	{
		return m_Scene->m_Registry.emplace_or_replace<T>(m_EntityHandle, std::forward<Args>(args)...);
	}
```

1. **Lines 18–21:** the constructor stores a handle and a scene pointer and owns nothing.
2. **Lines 25–28:** `decltype(auto)` hands back what `emplace` returns; the assertion checks the entity lacks the
   component; the arguments are forwarded unchanged.
3. **Lines 31–35:** `AddOrReplaceComponent` is the same call with `emplace_or_replace`.

`AddComponent` forwards its arguments to `emplace`, which builds the component in the storage from them. Its return type
is `decltype(auto)`, so for an ordinary component the caller receives a reference to the new component, and for an empty
tag component nothing, as the comment says. `ST_CORE_ASSERT` stops a program in Debug and Release builds that adds a
component an entity already has, and compiles out of :term[Dist]{id=dist} builds. Use `AddOrReplaceComponent` where the entity may
already have one.

The second excerpt shows the reading side, and the rule about tags.

```cpp src="Strata/src/Strata/Scene/Entity.h#L37-L51"
template<typename T>
T& GetComponent()
{
	static_assert(!std::is_empty_v<T>, "Tag components carry no data; use HasComponent");
	ST_CORE_ASSERT(HasComponent<T>(), "Entity does not have the component");
	return m_Scene->m_Registry.get<T>(m_EntityHandle);
}

template<typename T>
const T& GetComponent() const
{
	static_assert(!std::is_empty_v<T>, "Tag components carry no data; use HasComponent");
	ST_CORE_ASSERT(HasComponent<T>(), "Entity does not have the component");
	return m_Scene->m_Registry.get<T>(m_EntityHandle);
}
```

1. **Line 40:** the `static_assert` refuses an empty type at :term[compile time]{id=compile-time}.
2. **Line 41:** the assertion catches a missing component in Debug and Release builds.
3. **Lines 46–51:** the `const` overload repeats both checks.

An empty struct stores no values, so there is nothing to return a reference to. The `static_assert` turns the mistake
into a :term[compile error]{id=compile-error} with a message, in the same way for the plain and the `const` version. For a tag, ask
`HasComponent`. `TryGetComponent` returns a pointer or null, and also null for an invalid entity, which makes it the call
for data that may be absent.

The third excerpt is the way to say "I changed this in place".

```cpp src="Strata/src/Strata/Scene/Entity.h#L84-L90"
// Notifies systems (through the registry's on_update signal) that a component was modified in place.
template<typename T>
void MarkModified()
{
	if (HasComponent<T>())
		m_Scene->m_Registry.patch<T>(m_EntityHandle);
}
```

`MarkModified` calls EnTT's `patch`, which fires the `on_update` signal of that component type. The scene graph's caches
listen for it. What the signal means and who must send it is the subject of [The scene graph](../world/scene-graph.md).

Last, the validity check and the data members.

```cpp src="Strata/src/Strata/Scene/Entity.h#L103-L114"
	bool IsValid() const { return m_Scene && m_Scene->m_Registry.valid(m_EntityHandle); }
	explicit operator bool() const { return IsValid(); }
	operator entt::entity() const { return m_EntityHandle; }
	entt::entity GetHandle() const { return m_EntityHandle; }
	Scene* GetScene() const { return m_Scene; }

	bool operator==(const Entity& other) const { return m_EntityHandle == other.m_EntityHandle && m_Scene == other.m_Scene; }
	bool operator!=(const Entity& other) const { return !(*this == other); }
private:
	entt::entity m_EntityHandle = entt::null;
	Scene* m_Scene = nullptr;
};
```

1. **Line 103:** the validity check, through the registry and its versions.
2. **Line 105:** the conversion that lets an `Entity` stand for its handle.
3. **Line 109:** equality needs the same handle and the same scene.
4. **Lines 112–113:** the only data: a handle and a scene pointer.

`IsValid` asks the registry whether the handle is current, through its version. An `Entity` is also valid only if its
scene exists, and two `Entity` values are equal only if both the handle and the scene match. The conversion to
`entt::entity` lets an `Entity` go straight into an EnTT call.

The script software development kit (SDK) has a class that is also named `Entity`. Its `Entity` is a `UUID` value that a script keeps in a field.
Every call on one whose entity is gone does nothing and returns an empty result, and destroyed entities stay valid until
the end of the frame. That is why a script may store its `Entity` while engine code may not store the engine's: the
engine's is a handle, the script's is a name. [The script interface](../scripting/abi-sdk.md) teaches it.

### Creating an entity

Every entity the scene creates carries the same core components, and the order matters. Read the function from the top,
and watch what it does before it touches the registry.

```cpp src="Strata/src/Strata/Scene/Scene.cpp#L386-L415" symbol="Scene::CreateEntityWithUUID"
Entity Scene::CreateEntityWithUUID(UUID uuid, const std::string& name)
{
	if (GetRegistryEntityCount() >= c_MaxEntities)
	{
		ST_CORE_ERROR("Scene '{}': cannot create entity '{}': the scene already has the maximum of {} entities", m_Name, name, c_MaxEntities);
		return {};
	}

	if (!uuid.IsValid() || m_EntityMap.find(uuid) != m_EntityMap.end())
	{
		if (uuid.IsValid())
			ST_CORE_ERROR("Scene '{}': entity UUID {} already exists; assigning a new UUID", m_Name, uuid.ToString());
		uuid = UUID();
	}

	// The hierarchy node comes first: the signals of the other components rely on it.
	const entt::entity handle = m_Registry.create();
	m_Registry.emplace<HierarchyComponent>(handle);
	Entity entity(handle, this);
	entity.AddComponent<IDComponent>(uuid);
	entity.AddComponent<NameComponent>(name.empty() ? std::string("Entity") : name);
	entity.AddComponent<TransformComponent>();
	entity.AddComponent<RelationshipComponent>();
	entity.AddComponent<WorldTransformComponent>();

	m_EntityMap.emplace(uuid, handle);
	LinkLast(handle, entt::null);
	m_HierarchyVersion++;
	return entity;
}
```

1. **Lines 388–392:** the limit guard: an error in the log and an invalid `Entity`.
2. **Lines 394–399:** a zero or taken `UUID` is replaced by a new one, and a taken one is logged.
3. **Lines 401–403:** the registry makes the number and the hierarchy node comes first.
4. **Lines 404–409:** the core components, in order.
5. **Lines 411–413:** the map entry, the end of the root list and the version of the hierarchy.

The function guards the limit first. At 1,048,575 live entities it logs an error and returns an invalid `Entity`, so the
caller must check `IsValid`. Next it repairs the `UUID`. A zero is replaced silently, because a caller may pass none.
A value already in the map is replaced and logged, since two entities of one name would break every lookup.

The registry then makes the entity number, and the hierarchy node, `HierarchyComponent`, is the first component. The
comment says the signals of the other components rely on it. The reason shows a few lines later. Adding a
`TransformComponent` fires `OnTransformChanged`, which marks the entity dirty by setting a flag in its hierarchy node.
With no node the signal finds no flag to set and returns, and the entity's world transform would never be computed.

Then come the `IDComponent`, the name (`Entity` if none was given), a transform with its default values, a
`RelationshipComponent` and a `WorldTransformComponent`.

Last, the entity enters the map under its `UUID`, joins the end of the root list through `LinkLast`, and the scene's
hierarchy version increases so that cached orderings know something changed. `CreateChildEntity` does the same and then
moves the entity under its parent.

### Components, tags and views

Strata's components are plain data: a struct of fields with defaults, no pointers into the engine, no behavior that
needs the scene. Anything a system computes and could work out again, such as the world matrix, lives in a separate,
runtime-only component, so that the data a person wrote and the data an engine derived never mix.

A **tag component** is an empty struct whose presence is the information. `InactiveComponent` is one: an entity that
has it, and everything below it, is not drawn, simulated or updated. To test for one, call `HasComponent`; to switch
it, `AddComponent` or `RemoveComponent`. A tag costs no value storage, since EnTT gives an empty type pages of size
zero, and only the entity numbers of its sparse set remain.

To visit every entity that has certain components, ask the scene for a view.

A **view** is a thing you can loop over, built by EnTT on request: it yields each entity that has all the components asked
for, without copying anything.

```pseudocode
for each (entity, transform, name) in scene.GetAllEntitiesWith<TransformComponent, NameComponent>().each():
    use transform and name; do not add or remove these components here
```

`GetAllEntitiesWith<...>()` is a one-line call of the registry's `view`. A view does what the toy's did. It takes the
smallest of the storages it is asked about as its leading storage and walks that storage's packed array. It keeps an
entity only if every other storage contains it. Asking for a rare component first or last makes no difference.

The price is the same as in the toy: while the loop runs, adding or removing a component of the viewed types moves
elements under the loop. Collect entities in a list first and change them after the loop.

The registry also holds objects that are not components. Its **context** keeps one object per type for the whole
registry. The :term[renderer]{id=renderer} keeps its `RenderSceneContext` there, and the game's interface its `GameUISceneContext`: each
holds the owning pointer to one object that belongs to this scene alone. Both find it with a lookup and create it on the
first request.

A module that stores per-scene state here gets it destroyed with the scene. When a scene is copied, the registry does
not copy the context's objects. A module registers a function with `Scene::RegisterContextCopier` that copies its own
object, and the scene calls it after the copy is whole.

### The Scene module's components

The scene's own components, with the page that teaches each one:

| Component | What it holds | Where it is taught |
| --- | --- | --- |
| `IDComponent` | The entity's `UUID`; hidden, cannot be removed, not written as a component | This page |
| `NameComponent` | A name; cannot be removed; indexed for lookup | [The scene graph](../world/scene-graph.md) |
| `TagComponent` | A label such as "Enemy" that game code uses to find groups; indexed | [The scene graph](../world/scene-graph.md) |
| `InactiveComponent` | Nothing: a tag that switches the entity and its descendants off | [The scene graph](../world/scene-graph.md) |
| `TransformComponent` | Translation, rotation and scale relative to the parent | [The scene graph](../world/scene-graph.md) |
| `RelationshipComponent` | The parent's `UUID` and the children's, in order | [The scene graph](../world/scene-graph.md) |
| `PrefabInstanceComponent` | The prefab an entity came from and how it differs | [Prefabs](../world/prefabs.md) |
| `CameraComponent` | Projection, field of view, clipping planes, lens settings | [Coordinates](../gpu/coordinates.md) |

Three flags on `IDComponent` explain its row. The flag `Hidden` keeps it out of the inspector and the add menu. The flag
`NotRemovable` means every entity keeps it. The flag `NoSerialize` means the file's list of components does not contain
it; the code that writes scene files writes the `UUID` itself, as the entity's `ID`.

Two more types are declared in this module but registered by others. `MeshRendererComponent` is registered by the
renderer module, and `SkinComponent` by the animation module. They stand in the Scene layer because other layers that may
not include the renderer or the animation module, such as physics, still have to read them. The module that registers
a component is the one that lets the editor change it and files hold it. [Drawing entities](../draw/entities-to-draws.md) and
[Skinning](../animation/skinning.md) teach them.

Four components are never registered, saved or shown: `HierarchyComponent`, `WorldTransformComponent`,
`SubSceneComponent` and `UnknownComponentsComponent`. The first two are derived caches. The third marks entities that a
sub-scene's load created, so that unloading removes them. The fourth keeps components that this build does not know,
word for word, so that loading and saving a scene never loses them. [How components are described](../world/reflection.md)
teaches what registering means.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| One table for each set of components: entities with the same set share a table | Unity's Entities package | Faster visits of exact component sets; no per-type moves of one component | Adding a component moves the whole entity between tables; a change in the middle of a frame costs more |
| EnTT groups: storages kept sorted together | EnTT users who need the fastest fixed visit | A visit with no membership checks | Extra work on every add and remove, and a group owns its storages' order |
| Objects with inheritance | Older engines and many scripting layers | A familiar model with data and methods together | A fixed shape for a thing; a change of kind means a new class |
| One :term[shared pointer]{id=shared-pointer} per component | Simple toy engines | Pointers that stay valid when others are removed | A heap block per component and slow, scattered visits |
| Writing the sparse set in Strata itself | Engines that came before EnTT | Exact control of memory and no vendored library | Months of work to match a tested library's behavior |

Strata uses EnTT's plain storages and views because the engine's loops visit one or two component types and the tests
check them. The statements about other engines come from their public documentation; see Further reading.

## How it is tested

The `Scene` suite in `StrataTests/src/Scene/SceneTests.cpp` holds the test case `Entities are created with core
components`. It checks the core components, the name `Entity` that an unnamed entity gets, lookup by `UUID`, and that a
taken `UUID` yields an entity with another one. The test `Scene copies preserve UUIDs, data and hierarchy` checks that
copies keep the values.

The suite `Scene.Hierarchy` in `HierarchyTests.cpp` holds the limit test, `Creating more entities than an EnTT registry
can hold fails cleanly`. It fills the registry almost to the limit with plain EnTT entities, which are quicker to make, and adds scene entities up
to it. It then checks that the next scene
entity, number 1,048,576, comes back invalid with the log text `maximum of 1048575 entities`, and that the scene stays
as it was.

Run them directly:

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=Scene
build/windows/bin/Debug/StrataTests.exe --test-suite=Scene.Hierarchy
```

The first command runs the suite `Scene` and the second the hierarchy suite, which holds the limit test; both run without a :term[graphics card]{id=gpu}.

## Changing it safely

What do you extend, and what must stay true? To add a component, write a plain struct in its module's components header
and register it in that module's registration function; [How components are described](../world/reflection.md) shows the
steps, and the feature test must exercise it. To store per-scene state that is not a component, use the context, and
register a copy function if a copy of the scene needs it.

:::rule[Signal your writes, use handles briefly]
Code that writes a transform, a name or a tag in place signals it; code that keeps an entity longer than one call keeps
its `UUID`. The reasons are on this page and in [The scene graph](../world/scene-graph.md): caches hear only signals, and
handles and references are recycled or moved.
:::

Three checks before a change merges:

- No `Entity`, `entt::entity` or reference is stored in a member, a :term[lambda capture]{id=lambda-capture} or a queue that lasts longer than the call.
- No loop over a view adds or removes a component of the viewed types.
- Every creation checks `IsValid`.

Run the `Scene` suites and the feature test after a change.

## Summary

- A sparse set stores each element at the end of a packed array and finds it through a sparse index. A removal fills the
  hole with the last element, so it moves one other element.
- A handle is a 20-bit index and a 12-bit version that is recycled after a destruction; a `UUID` is a random, non-zero
  64-bit value that survives saving, loading and copies.
- Engine code holds `UUID` values across frames and copies, never `Entity`, handles or `T&`, never calls `GetComponent`
  for a tag and checks the entity that creation returns.
- Creating an entity makes the hierarchy node first, then the `IDComponent`, name, transform, relationship and world transform, and
  registers the `UUID` in the map.
- Components are plain registered data, tags carry only presence, and four runtime-only components are never
  registered, saved or shown.

## Check yourself

1. A sparse set holds the entities 6, 2, 9 and 4 in its dense array, in that order. Entity 2 is removed. What does the
   dense array hold afterwards, and which entity's position changed?

   :::answer{tests="storage"}
   The last element, 4, moves into the hole at position 1: the dense array becomes 6, 4, 9. Entity 4's position
   changed from 3 to 1, and no other entity moved.
   :::

2. A system keeps the `Entity` of the player in a member, and the editor copies the scene to enter play mode. Which of
   the following is true? (a) The `Entity` names the copy's player. (b) The `Entity` names the edited scene's player.
   (c) The `Entity` is invalid in the copy.

   :::answer{tests="identifiers"}
   Option (b). An `Entity` holds a handle and a pointer to its scene, and the copy is another scene, so the member still
   names the edited scene's player. Option (a) fails for that reason, and (c) fails because the handle value is the
   same in the copy today and the source scene still exists. The fix is to keep the player's `UUID` and call
   `GetEntityByUUID` on the running scene.
   :::

3. The slot of index 9 has had 3 entities destroyed in it, so its version is 3. What is the value of the handle of the
   entity that uses it now?

   :::answer{tests="identifiers"}
   The value is $3 \times 2^{20} + 9 = 3{,}145{,}737$: the version in the high bits and the index in the low bits.
   :::

4. A programmer writes `entity.GetComponent<InactiveComponent>().` to read whether an entity is switched off. What
   happens, and what is the right call?

   :::answer{tests="kinds,contract"}
   The program does not compile: `InactiveComponent` is an empty tag component, and `GetComponent` has a
   `static_assert` that refuses empty types. The right call is `HasComponent<InactiveComponent>()`, or `IsActive()`,
   which checks it.
   :::

5. Creating an entity with a `UUID` that the scene already uses: what does `CreateEntityWithUUID` return, and what
   does it log?

   :::answer{tests="creation"}
   The call returns a valid entity that carries a new random `UUID`, and logs an error that names the old value. Only
   the limit of 1,048,575 entities returns an invalid entity.
   :::

## Exercises

1. **Basic.** Take the toy's names set after entity 1 was removed, whose dense array is 0, 4, 2, 3. Remove the name of
   entity 0 next. Write the dense array and the sparse entries of the entities 0, 3 and 4 afterwards.

   :::answer[Worked solution]{tests="storage"}
   Entity 0 sits at position 0 and the last element is entity 3. Entity 3 moves into position 0, so the dense array
   becomes 3, 4, 2. The sparse entry of 3 changes from 3 to 0, the entry of 4 stays 1, and the entry of 0 is empty.
   :::

2. **Medium.** Trace it yourself: start a Debug build of the tests, put a breakpoint inside a loop over
   `GetAllEntitiesWith<TransformComponent, NameComponent>()`, and step into the view's :term[iterator]{id=iterator}. Find which storage the
   view walks, and what it does with an entity that the other storage lacks.

   :::answer[Worked solution]{tests="storage,kinds"}
   The function is `Scene::GetAllEntitiesWith` in `Strata/src/Strata/Scene/Scene.h`, which returns the registry's `view`.
   Stepping into the iterator leads to `view_iterator` in `Strata/vendor/entt/src/entt/entity/view.hpp`, whose
   `seek_next` skips every entity for which `valid` is false. The view's leading storage is the smaller of the two,
   chosen in `unchecked_refresh`, and `valid` asks each other storage whether it contains the entity. In the debugger,
   watch the leading storage's packed array: the loop moves down it one position at a time. Remove one of the components
   in the loop body to see the last element move into the hole, as in the toy.
   :::

3. **Hard.** Write a handle table with a 20-bit index and a 12-bit version that is recycled: `Create`, `Destroy` and
   `Valid`. Show that an old handle fails after its slot is used again, and find how many uses bring it back.

   :::answer[Worked solution]{tests="identifiers,storage"}
   Keep a vector of versions per index and a list of free indices; a handle is the version shifted left by 20 bits
   ORed with the index. `Destroy` increases the version, skips the largest value as EnTT does, and frees the index;
   `Valid` compares the stored version with the handle's. The whole program and the output it prints are:

   ```cpp sketch="world-ecs-handles.cpp"
   // Handles made of an index and a version, recycled after destruction as an EnTT identifier is (20 bits and 12 bits).
   #include <cstdint>
   #include <cstdio>
   #include <vector>

   namespace
   {
   	constexpr uint32_t c_IndexBits = 20;
   	constexpr uint32_t c_IndexMask = (1u << c_IndexBits) - 1;
   	constexpr uint32_t c_VersionMask = 0xFFF;

   	class Handles
   	{
   	public:
   		uint32_t Create()
   		{
   			uint32_t index = 0;
   			if (m_Free.empty())
   			{
   				index = static_cast<uint32_t>(m_Versions.size());
   				m_Versions.push_back(0);
   			}
   			else
   			{
   				index = m_Free.back();
   				m_Free.pop_back();
   			}
   			return (m_Versions[index] << c_IndexBits) | index;
   		}

   		void Destroy(uint32_t handle)
   		{
   			const uint32_t index = handle & c_IndexMask;
   			uint32_t next = m_Versions[index] + 1;
   			if (next == c_VersionMask) // the largest version stays unused, as in EnTT
   				next = 0;
   			m_Versions[index] = next;
   			m_Free.push_back(index);
   		}

   		bool Valid(uint32_t handle) const
   		{
   			const uint32_t index = handle & c_IndexMask;
   			return index < m_Versions.size() && m_Versions[index] == (handle >> c_IndexBits);
   		}
   	private:
   		std::vector<uint32_t> m_Versions; // the current version of each index
   		std::vector<uint32_t> m_Free;     // indices waiting to be reused
   	};
   }

   int main()
   {
   	Handles handles;
   	const uint32_t first = handles.Create();
   	const uint32_t second = handles.Create();
   	handles.Destroy(first);
   	const uint32_t third = handles.Create();
   	std::printf("first %u, second %u, third %u\n", first, second, third);
   	std::printf("first is valid: %d, third is valid: %d\n", handles.Valid(first), handles.Valid(third));

   	uint32_t latest = third;
   	for (int round = 0; round < 4094; round++)
   	{
   		handles.Destroy(latest);
   		latest = handles.Create();
   	}
   	std::printf("after 4095 reuses of index 0, first is valid again: %d\n", handles.Valid(first));
   	return 0;
   }
   ```

   ```text output-of="world-ecs-handles.cpp"
   first 0, second 1, third 1048576
   first is valid: 0, third is valid: 1
   after 4095 reuses of index 0, first is valid again: 1
   ```

   1. **Lines 18–27:** a new slot starts at version 0; a freed slot is taken again with the version it already has.
   2. **Line 28:** the handle packs the version above the 20 index bits.
   3. **Lines 34–37:** `Destroy` raises the version and skips the largest value.
   4. **Line 44:** `Valid` compares the stored version with the handle's.
   5. **Lines 62–67:** 4,094 more destroy and create rounds bring the slot's version back to 0.

   The first handle has value 0; the third has index 0 and version 1, so its value is 1,048,576. The old handle is
   invalid until the slot has been destroyed and taken again 4,095 times.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Scene/Entity.h`: `Entity`.
- `Strata/src/Strata/Scene/Scene.h` and `Scene.cpp`: `Scene`, `CreateEntityWithUUID`, `GetEntityByUUID`,
  `GetAllEntitiesWith`, `c_MaxEntities`, `RegisterContextCopier`.
- `Strata/src/Strata/Scene/Components.h`: the Scene module's components; `SceneHierarchy.h`, `SubScene.h` and
  `UnknownComponents.h`: three runtime-only ones.
- `Strata/src/Strata/Core/UUID.h` and `UUID.cpp`: `UUID`.
- `Strata/vendor/entt/src/entt/entity/`: `sparse_set.hpp`, `storage.hpp`, `view.hpp` and `entity.hpp`.
- Tests: `StrataTests/src/Scene/SceneTests.cpp` (suite `Scene`) and `HierarchyTests.cpp` (suite `Scene.Hierarchy`).
- Other pages: [Scene systems](../world/systems.md), [The scene graph](../world/scene-graph.md) and
  [Handles and meta files](../assets/handles-meta.md).

## Further reading

- [EnTT, "Crash Course: entity-component-system"](https://github.com/skypjack/entt/wiki/Crash-Course:-entity-component-system):
  the library's own description of registries, storages and views (intermediate).
- Robert Nystrom, "Game Programming Patterns", chapter "Component": why games separate data from things (beginner).
- Michele Caini's blog series about the design of EnTT, on the author's own blog: how a design built on sparse sets
  grew (advanced).
