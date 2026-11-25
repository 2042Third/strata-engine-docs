---
id: world/prefabs
title: "Prefabs: the data model"
description: "How Strata compiles a saved group of entities into a prototype, copies it in slices, links the copies to it and brings its changes to them."
kind: internals
size: L
tracks: [E]
needs: [world/serialization]
time: 105
learn:
  - id: prototype
    text: explain why Strata compiles a prefab into a prototype that never changes, and what a copy takes from it
  - id: slices
    text: write engine code that makes instances from a prototype in slices, with every failure found before anything is created
  - id: overrides
    text: compute the override records of an instance by comparing its part with the prefab's part
  - id: propagation
    text: predict which values a change of a prefab reaches in each instance, and which values it leaves
  - id: limits
    text: name what linked instances cannot do, nested prefabs and variants, and what a prefab made from linked entities stores
since: 0.3.0
status: final
---

A street has forty lamp posts. Each one is an arm, a bulb and a cable, and the day you want a warmer bulb you do not want to visit forty places. A **prefab** is a saved group of entities that you place many times, and whose copies stay linked to it.

This page describes the data behind that. It traces a prefab file as it becomes a compiled prototype, is copied into a scene without stalling a frame, and gives each copy a link and a list of what the copy keeps different. It then shows how a change of the prefab reaches the copies. The editor's side is not here: placing prefabs, the Inspector's prefab bar, undo steps and the catch-up of scenes that were closed while a prefab changed. [Prefab instances in the editor](../editor/prefab-instances.md) teaches those, and [Prefabs for game makers](../make/prefabs.md) shows how to use prefabs.

The hands-on parts use the installed Strata, its samples and `StrataCLI` ([How to read this book](../start/how-to-read.md)). The :term[source files]{id=source-file} are in your clone of [your first engine change](../core/first-change.md).

## The problem and how engines solve it

Take the street again. Each lamp post has an arm, a bulb with a light and a humming sound. You build one post and place forty. Three questions decide the design:

- What happens to the forty when you improve the first?
- How can one post differ from the others?
- How fast can the engine make them?

The first approach is copy on place. Placing copies the entities into the scene and forgets where they came from. Copies are cheap and need no rules, because each one is a plain group of entities. The cost shows on the day you change the bulb: the forty copies know nothing of the original, so you edit forty groups by hand.

The second approach keeps a link. Each copy remembers its source, and a change of the source reaches every copy. A link alone is too strict, because the post by the harbor needs a bluer bulb, and a copy that cannot differ is of little use.

So the copy also records its **overrides**: the values it keeps different from its source. A change of the source then reaches each copy except where the copy overrides it. The cost is a list to maintain. Somebody must decide what counts as an override, store the list and keep it right while you edit.

The third approach lets prefabs hold prefabs, and lets a prefab derive from another one. A lamp post can hold a bulb prefab, and a street can hold lamp posts. A variant is a prefab that is another prefab plus its own overrides. The cost is depth: a change travels through several links, overrides sit at several levels, and a cycle must be refused.

| Approach | A change of the source reaches the copies | A copy may differ | What it costs |
| --- | --- | --- | --- |
| Copy on place | No | Freely, but it is a new group | One edit by hand per copy |
| Linked instances with overrides | Yes, except where overridden | Property by property | A list of overrides to keep right |
| Nested prefabs and variants | Yes, through several levels | At every level | Levels, cycles and harder rules |

:::elsewhere[Prefabs in Unity and Unreal Engine]
Unity's manual describes prefab instances, their overrides, nested prefabs and prefab variants. Unreal Engine's documentation describes Blueprint classes, whose defaults a placed instance may override. The Further reading section names both sources.
:::

Strata takes the second approach and stops there. A second pressure is time. A forest of 10,000 trees is 10,000 copies of one prefab, and reading the text of the prefab again for each copy is slow. Strata therefore reads a prefab once into a compiled prototype and copies from that.

The engine's architecture document records the effect: a prefab of 1,000 entities took about 17 ms to make when every copy read the text, and takes about 0.3 ms from the prototype. The price of the second approach is that a prefab made from linked entities cannot hold links. [What Strata does not do](#what-strata-does-not-do) states what you lose.

## The map

A prefab file reaches a scene in four steps. A loading worker reads the file and compiles it into a prototype. The :term[main thread]{id=main-thread} copies the prototype into the scene, entity by entity, in slices. Each copy gets a link to its prefab. Later, a change of the prefab travels the other way, from the file to the copies.

```mermaid caption="A prefab file is compiled once and copied many times; an apply writes an instance back and brings the change to the other instances." alt="A diagram. A prefab file is read on a loading worker into a prototype, which the main thread copies into linked instance entities. Applying an instance writes its part back into the file. A change of the file reaches every other instance except its overrides. Reverting an instance takes the prefab's values back."
flowchart LR
    File[".stprefab file"] -->|"EntityTemplate::Read, loading worker"| Prototype["EntityPrototype"]
    Prototype -->|"BeginInstantiation, ContinueInstantiation, main thread"| Instances["Instance entities with PrefabInstanceComponent"]
    Instances -->|"apply: MakeTemplate, ReplaceTemplate"| File
    File -->|"change of the prefab"| Others["Other instances"]
    Others -->|"Propagate, except overrides"| Instances
    Instances -->|"revert: Replace, Revert"| Instances
```

The files are in `Strata/src/Strata/Scene/`:

- `EntityPrototype.h` and `EntityPrototype.cpp` hold the compiled hierarchy.
- `SceneInstantiation.cpp` holds the scene's functions that copy it.
- `Prefab.h` and `Prefab.cpp` hold the asset classes that own a prototype.
- `PrefabInstances.h` and `PrefabOverrides.h` hold the :term[namespaces]{id=namespace} that work on linked instances and their overrides.

The commands that call them, `prefab.apply` among them, are in `StrataEditor/src/Editor/EditorPrefabCommands.cpp`.

## The contract

Each rule below is something a caller may rely on or must do, and each has its reason.

- A prototype never changes after `EntityPrototype::Compile` or `EntityPrototype::FromSnapshot` returns it. The loading worker builds it and the main thread reads it, so the two share it without a lock; a write from either side would be a :term[data race]{id=data-race} with the other. [Jobs](../core/jobs.md) explains such sharing.
- Copies are made on the main thread only. The scene belongs to the main thread, as [The scene graph](../world/scene-graph.md) explains for its caches.
- Every failure is reported before the call creates anything. `BeginInstantiation` returns false and `ContinueInstantiation` returns 0, each with a message. A failed call leaves the scene as it was before that call, so a caller never has to clean up half an instance.
- The `PrototypeInstantiation` object and its prototype stay alive until the last slice is done. The object holds the identifiers and handles that later slices need.
- A linked entity changes its parent only through `Scene`. The link, the hierarchy and the caches must change together.
- The root's transform and name belong to the instance. Comparisons skip them, `Replace` keeps them, and `MakeTemplate`, which writes an instance in the prefab's form, swaps them for the prefab's own. Placing and naming an instance must not count as a change that blocks the prefab's later changes.

:::rule[Keep instances exact]
Code that writes a prefab, brings a prefab's values to instances or records scene undo steps must keep the version, :term[hash]{id=hash} and override records exact. The reason: an instance with a wrong record looks changed when it is not, or unchanged when it is, and the next change of its prefab then skips it or writes over it. [Prefab instances in the editor](../editor/prefab-instances.md) teaches these records.
:::

## A toy version

The first toy shows copying in slices. A prototype is a list of names and parent indexes, with parents before their children, and a scene has a capacity. `Begin` checks the capacity and creates nothing. `Continue` makes at most a given number of entities and returns how many it handled. Notice the second `Begin` at the end: it is refused before any entity exists.

```cpp sketch="world-prefabs-slices.cpp"
// A toy prototype copied into a toy scene in slices: capacity is checked first, parents are created before children.
#include <algorithm>
#include <cstdio>
#include <string>
#include <vector>

struct Prototype
{
	std::vector<std::string> Names;
	std::vector<int> Parents; // Index of each entity's parent, -1 for a top-level entity; parents come first
};

struct ToyEntity
{
	std::string Name;
	int Parent;           // Index of the parent in the scene, -1 for none
	size_t TemplateIndex; // The prototype entity this one was made from
};

struct Instantiation
{
	const Prototype* Source = nullptr;
	std::vector<int> Handles; // Per prototype entity: its index in the scene
	size_t Next = 0;
};

struct ToyScene
{
	std::vector<ToyEntity> Entities;
	size_t Capacity = 0;

	bool Begin(const Prototype& prototype, Instantiation& out) const
	{
		if (prototype.Names.size() > Capacity - Entities.size())
			return false; // Nothing is created
		out.Source = &prototype;
		out.Handles.assign(prototype.Names.size(), -1);
		out.Next = 0;
		return true;
	}

	size_t Continue(Instantiation& work, size_t maxEntities)
	{
		const Prototype& prototype = *work.Source;
		const size_t end = std::min(prototype.Names.size(), work.Next + maxEntities);
		for (size_t index = work.Next; index < end; index++)
		{
			const int parent = prototype.Parents[index];
			work.Handles[index] = static_cast<int>(Entities.size());
			const int parentHandle = parent < 0 ? -1 : work.Handles[static_cast<size_t>(parent)];
			Entities.push_back({ prototype.Names[index], parentHandle, index });
		}
		const size_t handled = end - work.Next;
		work.Next = end;
		return handled;
	}
};

int main()
{
	const Prototype lamp { { "Post", "Arm", "Bulb", "Shade", "Cable" }, { -1, 0, 1, 1, 0 } };
	ToyScene scene;
	scene.Capacity = 10;
	scene.Entities.push_back({ "Ground", -1, 0 });
	scene.Entities.push_back({ "Tree", 0, 0 });

	Instantiation work;
	if (scene.Begin(lamp, work))
	{
		for (int frame = 1; work.Next < lamp.Names.size(); frame++)
		{
			const size_t handled = scene.Continue(work, 2);
			std::printf("frame %d: made %zu, the scene holds %zu\n", frame, handled, scene.Entities.size());
		}
	}
	for (const ToyEntity& entity : scene.Entities)
		std::printf("%s under %s\n", entity.Name.c_str(), entity.Parent < 0 ? "nothing" : scene.Entities[static_cast<size_t>(entity.Parent)].Name.c_str());

	scene.Capacity = 8;
	Instantiation second;
	std::printf("a second lamp: %s\n", scene.Begin(lamp, second) ? "begun" : "refused, nothing made");
	return 0;
}
```

```text output-of="world-prefabs-slices.cpp"
frame 1: made 2, the scene holds 4
frame 2: made 2, the scene holds 6
frame 3: made 1, the scene holds 7
Ground under nothing
Tree under Ground
Post under nothing
Arm under Post
Bulb under Arm
Shade under Arm
Cable under Post
a second lamp: refused, nothing made
```

1. **Lines 7–11:** A prototype is two parallel lists; a parent's index is smaller than its children's.
2. **Lines 20–25:** This object keeps what the next slice needs: the scene index of each entity made, and where to continue.
3. **Lines 32–39:** `Begin` fails before it changes anything; line 34 is the capacity check.
4. **Lines 42–57:** `Continue` handles at most `maxEntities` entities, and lines 48–51 find a parent that already exists.

Five entities took three frames of at most two entities. Each entity found its parent already made, because the prototype lists parents first. The same toy refuses a second lamp when the scene has too little room, and makes nothing.

The second toy compares one entity of a prefab with the same entity in an instance, and writes a record for each difference. A component is a map from property names to values. Notice that the root's transform does not occur: the toy has one ordinary entity, and [Overrides](#overrides) returns to the root's special case.

```cpp sketch="world-prefabs-overrides.cpp"
// A toy override list: the components of one entity in a prefab and in an instance, compared as values.
#include <cstdio>
#include <map>
#include <string>
#include <vector>

using Properties = std::map<std::string, std::string>;
using Components = std::map<std::string, Properties>;

struct Override
{
	std::string Component;
	std::string Property;
	std::string Kind;
};

std::vector<Override> Compare(const Components& prefab, const Components& instance)
{
	std::vector<Override> result;
	for (const auto& [name, properties] : prefab)
	{
		const auto found = instance.find(name);
		if (found == instance.end())
		{
			result.push_back({ name, "", "RemovedComponent" });
			continue;
		}
		for (const auto& [property, value] : properties)
		{
			const auto other = found->second.find(property);
			if (other == found->second.end() || other->second != value)
				result.push_back({ name, property, "Property" });
		}
		for (const auto& [property, value] : found->second)
		{
			if (!properties.contains(property))
				result.push_back({ name, property, "Property" });
		}
	}
	for (const auto& [name, properties] : instance)
	{
		if (!prefab.contains(name))
			result.push_back({ name, "", "AddedComponent" });
	}
	return result;
}

void Print(const char* title, const std::vector<Override>& overrides)
{
	std::printf("%s: %zu override(s)\n", title, overrides.size());
	for (const Override& entry : overrides)
		std::printf("  %s %s.%s\n", entry.Kind.c_str(), entry.Component.c_str(), entry.Property.c_str());
}

int main()
{
	const Components bulb { { "PointLight", { { "Intensity", "5" }, { "Range", "10" } } }, { "AudioSource", { { "Volume", "1" } } } };

	Components brighter = bulb;
	brighter["PointLight"]["Intensity"] = "8";
	Components silent = bulb;
	silent.erase("AudioSource");
	Components flickering = bulb;
	flickering["Flicker"] = { { "Rate", "3" } };

	Print("untouched", Compare(bulb, bulb));
	Print("brighter", Compare(bulb, brighter));
	Print("silent", Compare(bulb, silent));
	Print("flickering", Compare(bulb, flickering));
	return 0;
}
```

```text output-of="world-prefabs-overrides.cpp"
untouched: 0 override(s)
brighter: 1 override(s)
  Property PointLight.Intensity
silent: 1 override(s)
  RemovedComponent AudioSource.
flickering: 1 override(s)
  AddedComponent Flicker.
```

1. **Lines 7–15:** A component is a map of property names to values; a record names a component, a property and a kind.
2. **Lines 22–27:** A component the instance lacks gives a `RemovedComponent` record.
3. **Lines 28–38:** A property that differs, is missing or is new gives a `Property` record.
4. **Lines 40–44:** A component only the instance has gives an `AddedComponent` record.

An untouched instance has no records. A changed value, a missing component and an added component each give one record. The real code does the same on :term[JSON]{id=json} values and adds entities, scripts and the root's rule.

## The prototype: a compiled hierarchy

The loading worker turns a prefab's JSON snapshot into a **prototype**, a compiled copy of the entities that never changes and that scenes copy from. [Snapshots and sinks](../world/serialization.md) describes the snapshot. The prototype keeps the entities in hierarchy order, each with the index of its parent, and for each entity the list of its components. A component's value is a real object of its type, held in one packed array per type (`ComponentValueArray`, from [Reflection](../world/reflection.md)). The prototype also keeps the list of references between its entities, found once, so that a copy can point each reference at the copy of its target.

The excerpt is the :term[header's]{id=header} own account of the class. Read the comment above the class for what is compiled, and the three functions `Compile`, `FromSnapshot` and `Serialize` for the ways in and out.

```cpp src="Strata/src/Strata/Scene/EntityPrototype.h#L24-L50"
// Entity hierarchies compiled for copying into scenes: their entities in hierarchy order (parents before their children)
// with what instantiation needs worked out once - each entity's parent in that order, its components (real objects of
// their types, kept in one compact array per type, ComponentValueArray) and the entity references between its entities
// that a copy with fresh IDs points at the copies. EntityTemplate (prefabs, models) compiles its snapshot into one on the
// loading worker; additive scene loads compile the prepared scene they merge. Instances are made with
// Scene::BeginInstantiation (see there), which copies the components (ComponentInfo::EmplaceCopy) rather than reading JSON.
//
// Immutable once compiled, so the loading worker that compiles it and the main thread that instantiates it share it
// without locks.
class EntityPrototype
{
public:
	static constexpr uint32_t c_NoParent = std::numeric_limits<uint32_t>::max();
	static constexpr size_t c_NotFound = std::numeric_limits<size_t>::max();

	EntityPrototype() = default;
	~EntityPrototype();

	EntityPrototype(const EntityPrototype&) = delete;
	EntityPrototype& operator=(const EntityPrototype&) = delete;

	// Compiles the entities of a scene (a copy: the scene can go afterwards). Any thread, while nothing changes the scene.
	static Ref<EntityPrototype> Compile(const Scene& scene);
	// Reads a snapshot ({"Entities": [...]}, SceneSerializer::SerializeEntities) into a prototype (EntityPrototypeBuilder,
	// no scene). Null, with the error, when the entity data is invalid; what it could not read as written goes to
	// outWarnings.
	static Ref<EntityPrototype> FromSnapshot(const nlohmann::json& snapshot, std::string* outError = nullptr,
```

1. **Lines 24–29:** What is compiled: entities in hierarchy order, one array of values per type, references found once.
2. **Lines 31–32:** The promise that makes sharing safe, and its reason.
3. **Lines 42–43:** Copying is deleted: scenes share one prototype and never copy it.
4. **Lines 46–50:** `Compile` reads a scene, `FromSnapshot` reads JSON, and the second reports invalid data through `outError`.

`Compile` builds a prototype from a scene's entities, and `FromSnapshot` builds one from a snapshot without making a scene. It returns null with an error text when the entity data is invalid, and it reports what it could not read as written as warnings. `Serialize` writes the snapshot back: the engine does not keep the JSON, it writes it again from the prototype when a tool needs it.

The prototype owns its arrays instead of using the scene's storage for a reason of memory. The EnTT storage of a component type allocates a page of 1,024 elements at a time, and the engine's architecture document records that a small prefab's private registry then cost about 400 KiB. The packed arrays hold exactly the values the prefab has. Copying values out of real objects is also the speed gain: `ComponentInfo::EmplaceCopy` copies a value of the right type, where the old way parsed the JSON for each instance. That is the change from 17 ms to 0.3 ms per prefab of 1,000 entities.

## Making instances in slices

A slice is the part of a long job that one call does in one frame. `Scene::BeginInstantiation` starts the job and `Scene::ContinueInstantiation` does a slice of it. Why slice? The measurement above, 0.3 ms per 1,000 entities, is for one prefab of 1,000 entities.

If the cost stays proportional (an assumption), a part of the world with 100,000 entities costs 30 ms, almost two frames of 16.7 ms at 60 :term[frames per second]{id=frame-rate}. A game that creates it in one call shows a pause. In slices, each frame creates only a share of the entities and the picture keeps moving.

How big a slice may be in a frame is the budget of [Sub-scenes](../world/sub-scenes.md). That page's code calls `ContinueInstantiation` with chunks of at most 512 entities (`c_InstantiationChunk` in `Strata/src/Strata/Scene/SceneSubScenes.cpp`).

`BeginInstantiation` does the checks that need no entity. The parent must belong to this scene. The scene must have room for every entity of the prototype: `Scene::c_MaxEntities` is the scene's limit, and the message names the numbers. With `InstantiationOptions::KeepIDs`, which an additive scene load uses, no identifier of the prototype may exist in the scene already. It also gives every prototype entity its identifier up front, so a reference to an entity of a later slice already has a target.

`ContinueInstantiation` then does a slice, and the excerpt below shows its checks. Notice the order: nothing is created until the last check has passed, and an entity whose parent has gone is not created.

```cpp src="Strata/src/Strata/Scene/SceneInstantiation.cpp#L114-L154"
// Everything that can stop this slice is checked before anything is created.
if (instantiation.m_HasParent && !options.Parent.IsValid())
	return fail("The parent entity was destroyed");

// Entities whose parent is gone are not created: one created in an earlier slice may have been destroyed since (by
// gameplay, the editor, or an unload it was moved under), and destroying an entity destroys its descendants, so they
// go with it, as do the descendants of those not created. Parents come before their children, so each entity's
// parent was decided already: created in an earlier slice (and alive or not), or in this one (or skipped). The first
// slice (every Instantiate) has no earlier one, so it creates everything it covers.
const std::span<const uint32_t> parents = prototype.GetParentIndices();
std::vector<uint8_t>& skipped = instantiation.m_SliceSkipped;
skipped.clear();
size_t count = end - begin;
if (begin > 0)
{
	skipped.assign(end - begin, 0);
	for (size_t index = begin; index < end; index++)
	{
		const uint32_t parentIndex = parents[index];
		if (parentIndex == EntityPrototype::c_NoParent)
			continue;
		if (parentIndex >= begin ? skipped[parentIndex - begin] != 0 : !IsInstantiatedEntityAlive(instantiation, parentIndex))
		{
			skipped[index - begin] = 1;
			count--;
		}
	}
}
const auto isSkipped = [&skipped, begin](size_t index) { return !skipped.empty() && skipped[index - begin] != 0; };

const size_t existing = std::min(GetRegistryEntityCount(), c_MaxEntities);
if (count > c_MaxEntities - existing)
	return fail(fmt::format("Cannot add {} entities to a scene with {}: a scene holds at most {} entities", count, existing, c_MaxEntities));
if (options.KeepIDs)
{
	for (size_t index = begin; index < end; index++)
	{
		if (!isSkipped(index) && m_EntityMap.contains(instantiation.m_IDs[index]))
			return fail(fmt::format("The scene already has an entity with ID {}", instantiation.m_IDs[index].ToString()));
	}
}
```

1. **Lines 114–116:** The first check: the parent from the options must still exist, or the call returns 0 with a message.
2. **Lines 118–122:** Why entities can be skipped: a parent made by an earlier slice may be gone.
3. **Lines 127–141:** From the second slice on, an entity is skipped when its parent was skipped or has died; `count` shrinks.
4. **Lines 144–146:** The capacity check counts only the entities that will exist.
5. **Lines 147–154:** With kept identifiers, a collision fails the call before anything exists.

:::example[A prototype of 1,000 entities in slices of 300]
`ContinueInstantiation(instantiation, 300)` is called four times and returns 300, 300, 300 and 100. A fifth call returns 0 and sets no error, because every entity was handled.

Now let gameplay destroy the entity with prototype index 40 between the first and second calls. That destroys its descendants made so far, and the prototype's entity 300 has the parent 40. The second slice finds that parent gone, so it skips entity 300, and entity 301, whose parent is 300, is skipped with it.

That slice creates 298 entities and still returns 300, because it handled 300. After it, `GetHandledCount` reports 600, `GetCreatedCount` 598 and `GetSkippedCount` 2. If the parent given in the options is destroyed, the call returns 0 with the message "The parent entity was destroyed" and creates nothing.
:::

A slice that passes its checks does its work in a fixed order. It creates the entities with their identifiers, relationship, :term[world transform]{id=world-transform} and components, and emits each component's construction signal with its final value. It links each entity under its parent, and the top-level ones under the options' parent. The next excerpt is the rest: the references, the link to the prefab, the final signals and the :term[return value]{id=return-value}. Read the comment above the last loop: it says why every component signals again.

```cpp src="Strata/src/Strata/Scene/SceneInstantiation.cpp#L220-L270"
// References among the prototype's entities name the copies (the IDs the scene gives them); kept IDs need nothing.
if (!options.KeepIDs)
{
	const auto& references = prototype.m_References;
	auto reference = std::lower_bound(references.begin(), references.end(), static_cast<uint32_t>(begin),
		[](const EntityPrototype::EntityReference& entry, uint32_t entity) { return entry.Entity < entity; });
	for (; reference != references.end() && reference->Entity < end; ++reference)
	{
		if (isSkipped(reference->Entity))
			continue;
		const entt::entity handle = instantiation.m_Handles[reference->Entity];
		const UUID target = instantiation.m_IDs[reference->Target];
		void* component = reference->Component->Get(m_Registry, handle);
		if (reference->Extra)
			reference->Component->ExtraReferences.Set(component, reference->Property, reference->Subslot, target);
		else
			reference->Component->Properties[reference->Property].Setter(component, target);
	}
}

const bool linkToPrefab = options.SourcePrefab.IsValid();
for (size_t index = begin; index < end; index++)
{
	if (linkToPrefab && !isSkipped(index))
		m_Registry.emplace_or_replace<PrefabInstanceComponent>(instantiation.m_Handles[index], PrefabInstanceComponent { options.SourcePrefab, prototype.GetEntityID(index) });
}

// Components were constructed before their entities were linked and their references remapped: every component of
// every created entity now emits on_update (in registration order), so systems see the final state, e.g. when spawning
// during play. The components each entity has are known, so nothing is looked up.
const std::vector<const ComponentInfo*>& registered = ComponentRegistry::GetAll();
for (size_t index = begin; index < end; index++)
{
	if (isSkipped(index))
		continue;
	const entt::entity handle = instantiation.m_Handles[index];
	const std::span<const ComponentInfo* const> components = prototype.GetComponents(index);
	size_t next = 0;
	for (const ComponentInfo* info : registered)
	{
		const bool copied = next < components.size() && components[next] == info;
		if (copied)
			next++;
		if (copied || info == core.ID || info == core.Relationship || (linkToPrefab && info == core.PrefabInstance))
			info->MarkModified(m_Registry, handle);
	}
}

instantiation.m_Next = end;
instantiation.m_Skipped += (end - begin) - count;
return end - begin;
```

1. **Lines 221–238:** Each reference points at the copy of its target, unless identifiers are kept.
2. **Lines 240–245:** The link: the prefab's handle and the entity's identifier in the prototype, its template id.
3. **Lines 247–266:** Every component signals a change once everything is in place; the loop signals only the components the entity has.
4. **Lines 268–270:** The slice records its progress and returns how many entities it handled, skipped ones included.

Two differences from the toy matter. First, the real function remaps references: a reference between two entities of the prototype must point at their copies, and the copies have fresh identifiers. Second, it signals every component after everything is in place, as [The scene graph](../world/scene-graph.md) requires of code that writes in place, so that systems that listen see complete entities.

`Scene::Instantiate` is one slice as large as the prototype. `EntityTemplate::InstantiateMany` makes many instances in one call, each placed by a transform. It uses one `PrototypeInstantiation` object again for each instance, and it checks the room for all instances before it makes the first.

## Prefabs and models

`EntityTemplate` is the asset :term[base class]{id=base-class} that owns a prototype and offers `Instantiate`, `InstantiateMany`, `GetSnapshot` and `CompareInstance`. Its two kinds differ in who writes them. A `Prefab` is authored: `Prefab::CreateFromEntities` captures entities and their descendants, and `WriteDocument` writes the file, one entity per line, without the links of its entities, because a prefab stores none and its instances do. A **model** is imported, for example from a glTF file, and is read-only: `prefab.apply` refuses it and offers `prefab.unpack` instead. [Models from glTF files](../assets/models-gltf.md) describes how an importer makes one.

The Scene module registers a loader for each of the types Scene, Prefab and Model in `Strata/src/Strata/Scene/SceneRegistration.cpp`. The loaders read the document as a stream on a loading worker, and stop reading when the load is cancelled. The prefab document is `{ "Strata": { "Format": "Prefab", "Version": 1 }, "Prefab": { "Entities": [...] } }`, and a model's has `"Model"` in both places. `EntityTemplate::Instantiate` sets `InstantiationOptions::SourcePrefab` to its own handle, which is what links the copies. How an asset handle finds its asset is the subject of [Handles and meta files](../assets/handles-meta.md).

`CompareInstance` lists the entities of an instance with the prototype entity each came from and the components whose values differ. It is the entity-by-entity form of the comparison that the next sections do on JSON.

## Linked instances

Every entity made from a template carries a `PrefabInstanceComponent`. Its `Prefab` field is the asset handle of the template. Its `PrefabEntityID` is the **template id**, the identifier the entity has inside the prefab, which is the identifier of its prototype entity.

The two other fields, `PrefabVersion` and `SyncedHash`, date from the last moment the instance took the prefab's values. They hold the version of the prefab's entities it came from, and a hash of its own values. The catch-up of closed scenes uses these numbers, and [Prefab instances in the editor](../editor/prefab-instances.md) teaches it. The last field, `Overrides`, is the list of records that the next section describes.

The registration in `Strata/src/Strata/Scene/ComponentRegistration.cpp` flags the component `EngineAdded`: it can be seen and removed, but no user and no tool adds it. The identifier and the two numbers are read-only text properties. The identifier is no scene entity, so no copy may change it to point at another entity. The numbers are written as 16 :term[hexadecimal]{id=hexadecimal} digits, or as nothing when not known. The overrides are :term[extra data]{id=extra-data} of the component, written to a scene only when the list is not empty.

An instance is a :term[subtree]{id=subtree} that starts at its **instance root**. The root is an entity with a link whose parent has none to the same prefab, or has no parent at all.

A prefab with two top-level entities, say a lamp and a bench, gives each instance two roots. Each root stands for one **part** of the prefab: its template root and everything below it. Overrides, versions and the hash all belong to one root and its part.

`PrefabInstances` is the namespace of operations on this structure. The snapshot in the table is the `{"Entities": [...]}` form of the prefab.

| Function | What it does |
| --- | --- |
| `ExtractTemplate` | Cuts one part out of a snapshot: the template root first, then its descendants, parents before children |
| `MakeTemplate` | Makes the template of an instance: the same form, with the prefab's identifiers in place of the instance's, references between entities changed to match, no links, and the prefab's own root transform and name |
| `Compare` | Lists the entities that changed, were added to the instance or are missing from it, ignoring the root's transform and name |
| `Replace` | Reverts an instance to the template's values; entities keep their identifiers, and the root keeps its place, transform and name |
| `ReplaceTemplate` | Applies: puts a part made by `MakeTemplate` into the prefab's snapshot in place of the old part |
| `Link` | Links entities that were captured into a prefab to it, each with its own identifier as its template id |
| `Unpack` | Removes the links of an instance's entities, so that they become plain entities |
| `StripLinks` | Removes every link from a snapshot |

To **unpack** an instance is to remove its links, so that its entities stay as plain entities. `prefab.unpack` runs `Unpack` and is the way to edit a model's entities as your own.

## Overrides

An override is a record of what one instance keeps different. The :term[struct]{id=struct} `PrefabOverride` has four fields: the template id of the entity, the registered name of the component, the property, and a kind. The kinds are `Property` (a value differs) and `AddedComponent` (the instance's entity has a component its prefab entity lacks). The others are `RemovedComponent` (it lacks one the prefab entity has) and `RemovedEntity` (the instance lacks an entity of the prefab). A script is one component named `Script`, and its fields are overridden one by one as `<Class>.<Field>`; the list lives on the instance root.

Consider which differences are not overrides. The root's transform and name belong to the instance, so they are never overrides. Entities the instance added are its own too: they have no template id, so no record can name them.

`ComputeOverrides` finds the records by comparing two JSON values, which [JSON values and their comparison](../basics/data-formats.md) explains. One is the part of the prefab, and the other is the instance made into a template by `MakeTemplate`. Template ids are in both, so equal entities line up.

:::example[Four lamp posts and one change]
The prefab `Lamp` has two entities: a root `Post` and its child `Bulb`. The prefab's `Bulb`, written as `ExtractTemplate` gives it, holds a light and a sound. The lines below omit the names and transforms.

```json
{ "ID": "B", "Parent": "P", "Components": {
  "PointLight": { "Color": [1, 1, 1], "Intensity": 5.0, "Range": 10.0 },
  "AudioSource": { "Volume": 1.0 } } }
```

Four instances stand in a scene. Instance A is untouched. Instance B has its bulb's intensity set to 8. Instance C has had the `AudioSource` removed from its bulb. Instance D is the one you will apply from, and so far it has no difference.

The template of B, made by `MakeTemplate`, has the same shape with `"Intensity": 8.0`. Comparing it with the part gives one record, `{ B, "PointLight", "Intensity", Property }`. The template of C lacks `AudioSource`, so the record is `{ B, "AudioSource", "", RemovedComponent }`. A has no records. Moving any instance's root, or renaming it, gives no record for any of them.

Now change D's bulb: intensity 5 to 6, range 10 to 15 and volume 1.0 to 0.5, and apply D. The prefab's part now holds those values, and `Propagate` runs for A, B and C with the old part as `previousPart` and the new part as `nextPart`. Only the properties that differ between the two parts move.

| Value of the bulb | Prefab before | Prefab after | A | B | C |
| --- | --- | --- | --- | --- | --- |
| Intensity | 5 | 6 | 6 | 8, its override | 6 |
| Range | 10 | 15 | 15 | 15 | 15 |
| Volume | 1.0 | 0.5 | 0.5 | 0.5 | no component |
| Records afterwards | none | none | none | the intensity | the removed `AudioSource` |

B keeps 8 but takes the new range and volume, because it overrides only the intensity. C takes the new intensity and range. It has no `AudioSource`, and the prefab did not add one, so C stays without it. D itself has no records, because it is now the prefab's version.
:::

The code that makes the records is `CompareComponents`, with `IsRootOwn` for the rule of the root. The excerpt shows both. Look at the two loops: the first goes through the prefab's components, and the second through the instance's components that the prefab lacks.

```cpp src="Strata/src/Strata/Scene/PrefabOverrides.cpp#L159-L210"
// The instance root's transform and name are its own, never overrides.
bool IsRootOwn(bool root, std::string_view component)
{
	return root && (component == "Transform" || component == "Name");
}

void CompareComponents(UUID entity, bool root, const nlohmann::json& templateComponents, const nlohmann::json& instanceComponents,
	std::vector<PrefabOverride>& result)
{
	for (const auto& [name, value] : templateComponents.items())
	{
		if (IsRootOwn(root, name))
			continue;
		const nlohmann::json* instance = JsonUtils::Find(instanceComponents, name);
		if (IsScript(name))
		{
			CompareScripts(entity, value, instance ? *instance : nlohmann::json::object(), result);
			continue;
		}
		if (!instance)
		{
			result.push_back({ entity, name, {}, PrefabOverrideKind::RemovedComponent });
			continue;
		}
		if (!value.is_object() || !instance->is_object())
		{
			if (value != *instance)
				result.push_back({ entity, name, {}, PrefabOverrideKind::Property });
			continue;
		}
		for (const auto& [property, propertyValue] : value.items())
		{
			const nlohmann::json* other = JsonUtils::Find(*instance, property);
			if (!other || *other != propertyValue)
				result.push_back({ entity, name, property, PrefabOverrideKind::Property });
		}
		for (const auto& [property, propertyValue] : instance->items())
		{
			if (!value.contains(property))
				result.push_back({ entity, name, property, PrefabOverrideKind::Property });
		}
	}
	for (const auto& [name, value] : instanceComponents.items())
	{
		if (templateComponents.contains(name) || IsRootOwn(root, name))
			continue;
		if (IsScript(name))
			CompareScripts(entity, nlohmann::json::object(), value, result);
		else
			result.push_back({ entity, name, {}, PrefabOverrideKind::AddedComponent });
	}
}
```

1. **Lines 159–163:** The rule of the root: its `Transform` and `Name` are never compared.
2. **Lines 168–188:** Components of the prefab: one the instance lacks gives `RemovedComponent` (line 180), and scripts go to their own function.
3. **Lines 189–199:** Properties are compared both ways: those that differ or are missing, then those only the instance has.
4. **Lines 201–209:** Components only the instance has give `AddedComponent`.

`ComputeOverrides` calls `CompareComponents` for each entity of the part, in the part's order, and writes a `RemovedEntity` record for each entity of the part that the instance lacks. `UpdateOverrides` is the incremental form: it works out again the records of the entities an edit touched and keeps the others, so a :term[gizmo]{id=gizmo-start} drag costs one entity per frame, however large the instance is.

### Propagation

To **propagate** a prefab's change is to give each of its instances the change, except where the instance overrides it. `PrefabOverrides::Propagate` takes an instance root and the prefab's part before and after the change. It does not copy the prefab's state onto the instance.

Propagation applies the difference between the two parts, and the overrides decide what that difference may touch. The overrides are the list recorded on the root or, when none is recorded, how the instance differs from the old part. The rules, which the example above used, are these:

- Properties that changed in the prefab take their new values, through reflection and signaled like any edit, unless the list overrides them. A component whose override is a whole-component record, such as an added one, keeps all its values.
- Entities the instance added are its own, and nothing removes them.
- Components and entities the prefab added are made in the instance, unless a `RemovedComponent` or `RemovedEntity` record says the instance removed them.
- Components and entities the prefab removed go from the instance, unless the instance added them. A component the instance changed in any property stays, because any record of a component blocks its removal. An entity has no such block: it goes even when the instance changed a property inside it.
- What the instance keeps below a removed entity moves up to the nearest entity that stays, and keeps its place in the world.
- The root's transform and name stay.

The fifth rule has an example. The prefab's `Bulb` hangs on an `Arm`, and instance F carries a `Moth` that its maker put under the bulb. The prefab removes the bulb.

`Propagate` removes F's bulb, and the moth, which is not the prefab's, moves to the arm and keeps its world position. The code searches for the kept children before it destroys anything. The excerpt is that step.

```cpp src="Strata/src/Strata/Scene/PrefabOverrides.cpp#L803-L840"
// Entities the prefab removed go. What the instance keeps below them (entities it added, and linked ones the prefab
// still has) moves up to the nearest entity that stays, keeping its place in the world: a weapon the instance put in
// a hand the model no longer has stays in the instance.
std::vector<Entity> removed;
std::unordered_set<UUID> removedIds;
for (const auto& [id, entity] : previous)
{
	if (next.contains(id) || id == templateRoot)
		continue;
	const auto instance = linked.find(id);
	if (instance == linked.end())
		continue;
	removed.push_back(instance->second);
	removedIds.insert(instance->second.GetUUID());
}
std::vector<std::pair<Entity, Entity>> kept; // An entity that stays and its new parent
for (const Entity entity : removed)
{
	change(entity);
	// The root is never removed, so an ancestor that stays is always found.
	Entity parent = entity.GetParent();
	while (parent && removedIds.contains(parent.GetUUID()))
		parent = parent.GetParent();
	// A child that stays takes its own subtree along; a removed child is one of `removed`, with what it keeps.
	for (const Entity child : entity.GetChildren())
	{
		if (!removedIds.contains(child.GetUUID()))
			kept.emplace_back(child, parent ? parent : root);
	}
}
for (const auto& [entity, parent] : kept)
{
	change(entity);
	if (!scene.SetParent(entity, parent, true))
		return Fail(outError, fmt::format("'{}' could not be kept: moving it out of what the prefab removed failed", entity.GetName()));
}
if (!removed.empty())
	scene.DestroyEntities(removed);
```

1. **Lines 806–817:** The entities the prefab removed and the instance still has; the root is never one.
2. **Lines 823–825:** Walk up to the nearest ancestor that stays.
3. **Lines 827–838:** Children that stay are queued and moved with `SetParent`; `true` keeps their world transform.
4. **Lines 839–840:** Only then are the removed entities destroyed.

Afterwards `Propagate` works out the list again against the new part and stores it when it changed. The records of an entity that went are not in the new list, because the instance no longer has the entity. It reports what it did in `PropagateResult`: the entities that changed, the ones it created, and the instance's content hash for `MarkSynced`. It calls the function given as `beforeChange` for each entity before it changes, which is how an undo step learns what to restore. It returns false with a reason when the new part lacks the root's template or the scene is full, and `prefab.apply` then rolls back its undo transaction.

Two smaller operations act on one entity. `Revert` gives an entity the prefab's value of a component, or of one property: a component the prefab lacks goes, and one the entity lacks comes back. To **revert** is to take the prefab's value in place of the instance's own. For a script field that the prefab does not store, the stored value goes and the field returns to the class default. `ApplyToPart` is the reverse: it takes a component or property from the instance into a copy of the part, and is what `prefab.apply` uses when you apply one override instead of the whole instance.

## What Strata does not do

Strata has no nested prefabs and no prefab variants. A prefab holds plain entities and no links, and an instance is linked to exactly one prefab.

You meet the limit when you make a prefab from entities that are linked already. Take a lamp post whose bulb is an instance of a bulb prefab. `prefab.create` captures the post. `WriteDocument` omits the links from the file, and `StripLinks` removes them from the snapshot that the instances are marked in sync with.

The new `LampPost` prefab holds the bulb's entities as plain ones, and the bulb prefab's later changes do not reach them. The command's description says the links of another prefab are replaced. A change of the bulb prefab still reaches the bulbs that stand alone in a scene, and the lamp posts carry their own bulb.

Nesting would add the cost that the table of the first section names: more places where a change can come from and where an override can sit. `Propagate` as written handles one part, one previous part and one list.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Copy on place | Duplicating an entity with `Scene::DuplicateEntity`, in Strata itself | No links, no lists, nothing to keep right | A change of the original reaches no copy |
| Nested prefabs | Unity | A bulb prefab shared by every lamp post and street | Several levels of change and of overrides; a cycle check |
| Prefab variants | Unity | A blue lamp that is the lamp prefab plus a few overrides | A second kind of link between prefabs |
| Class defaults with instance changes | Unreal Engine's Blueprints | One model of inheritance for objects and levels | A class system that the engine's plain data does not have |
| Reading the JSON for each copy | Strata before the prototype | No compile step and no prototype memory | 17 ms instead of 0.3 ms per prefab of 1,000 entities |

## How it is tested

The three suites live in `StrataTests/src/Scene/` and run together with a doctest filter: `build/windows/bin/Debug/StrataTests.exe --test-suite=Scene.Prefab*`. Slices are tested in `Scene.Streaming`.

- `Scene.Prefab` (`PrefabTests.cpp`) checks that prefabs compile once and write back unchanged (`Prefabs compile their snapshot once and write it back unchanged`), that copies keep references and links (`Prefab instances copy the prototype: references, links, nested links and unknown components`), and that many instances come in one call (`Many instances of a prefab are made in one call, each placed by its transform`).
- `Scene.PrefabInstances` (`PrefabInstancesTests.cpp`) checks instance roots (`Instance roots are linked entities whose parent is not of the same prefab`), `Replace` (`Replace gives the instance the template's values, keeping UUIDs and the root's place, transform and name`) and the removal of links.
- `Scene.PrefabOverrides` (`PrefabOverridesTests.cpp`) checks the records, including `An unchanged instance has no overrides; the root's transform and name never count`, and propagation in `Propagate gives every instance the prefab's changes except what it overrides` and `Propagate keeps what the instance added below an entity the prefab removed, in its place in the world`.
- `Scene.Streaming` has `Entities whose parent was destroyed after an earlier slice created it are not created`, the case of the example above.

## Changing it safely

The extension points are few. A new component needs no prefab code: its properties are compared and copied through the registry, and entity references in properties and extra data are found by `FindReferences`. A new override kind would need `ComputeOverrides`, `IsOverridden`, `Propagate`, `Revert` and `ApplyToPart` to change together.

Keep these rules of the engine's `AGENTS.md` in mind, each with its reason. Code that writes a component of a linked entity in place signals the change, so that the scene's caches and the override records hear it. Instances change their parent only through `Scene`. A new regression test must fail without its fix.

The checks to pass are the three suites above, the feature test project that the engine's rules require for every new feature, and, when you change the copying code, the streaming suite. If you change `Propagate`, run the exercise of this page again: three instances, one apply, and the table of the example.

## Summary

- A prefab is read once on a loading worker into a prototype that never changes. It keeps the hierarchy order, parent indexes, one packed array of values per component type and a list of references, so that a copy costs about 0.3 ms per 1,000 entities instead of 17 ms.
- `BeginInstantiation` checks everything that needs no entity, and `ContinueInstantiation` makes at most the entities it is given, skips the children of destroyed parents and fails before it creates anything.
- Overrides are records computed by comparing the part's JSON with the instance's, each naming a template id; the root's transform and name are omitted, and the entities an instance added are never named.
- `Propagate` applies the difference between a prefab's old and new part to an instance, except where the list overrides it, and keeps what the instance added.
- Strata has no nested prefabs or variants, an instance is linked to one prefab, and a prefab made from linked entities stores no links.

## Check yourself

1. Why can the loading worker and the main thread share a prototype without a lock?
   (a) Each thread gets its own copy. (b) The prototype never changes after it is built. (c) Only the worker reads it. (d) The job system locks it for them.

   :::answer{tests="prototype"}
   The answer is (b). Nothing writes to a prototype after `Compile` or `FromSnapshot` returns it, so concurrent reads are safe. Option (a) is wrong: copying a prototype for each thread would cost the memory and time that the design saves. Option (c) is wrong: the main thread reads it to make instances. Option (d) is wrong: no lock exists, and none is needed.
   :::

2. A prototype has 1,000 entities, and you call `ContinueInstantiation` with a limit of 400 until it is complete. What do the calls return, and what does a fourth call return?

   :::answer{tests="slices"}
   The first three calls return 400, 400 and 200. The fourth call returns 0 and sets no error, because every entity was handled. A return of 0 with an error message is the failure case.
   :::

3. A prefab's `Bulb` has a `PointLight` with an `Intensity` of 5 and a `Range` of 10. In an instance, the bulb's light has `Intensity` 5 and `Range` 12, the bulb carries an added `Flicker` component, and the root stands 5 m from where the prefab's root stands. Which records does `ComputeOverrides` write?

   :::answer{tests="overrides"}
   Two records: `{ Bulb, "PointLight", "Range", Property }` and `{ Bulb, "Flicker", "", AddedComponent }`. The intensity is equal. The root's position is the instance's own and never a record: `IsRootOwn` skips the `Transform` and `Name` of the root.
   :::

4. The prefab removes the `AudioSource` of its bulb. Instance X changed that `AudioSource`'s `Volume` to 0.2, and instance Y did not. What does `Propagate` do to each?

   :::answer{tests="propagation"}
   Y loses its `AudioSource`. X keeps it, with its volume of 0.2, because any record of a component blocks the component's removal. The rule protects a change that somebody made on purpose.
   :::

5. A lamp post prefab is saved from entities, one of which is an instance of the bulb prefab. The bulb prefab changes. What reaches the lamp post prefab, and why?

   :::answer{tests="limits"}
   Nothing reaches it. `prefab.create` replaces the links of another prefab and stores none, so the bulb's entities in the lamp post prefab are plain entities. Strata has no nested prefabs.
   :::

6. Which of these moves of an instance of a prefab adds a record to its list: moving its root, renaming its root, changing one property of its child's light, or adding a child entity?

   :::answer{tests="overrides"}
   Only the change of the light's property. The root's transform and name are never overrides, and an added entity has no template id, so no record can name it.
   :::

## Exercises

1. **Basic.** Take the prefab `Torch`, with a root and a child `Flame`. The `Flame` holds a `PointLight` with `Intensity` 3 and `Range` 6, and an `AudioSource` with `Volume` 0.8.

   Instance T1 is untouched. T2 sets the range to 9. T3 removes the `AudioSource`. From a fourth instance T4 you change the intensity to 4, the range to 8 and the volume to 0.4, and you apply it. Predict the three values in T1, T2 and T3, then check them with `prefab.status` and the Inspector.

   To build it, run these lines in PowerShell in the Strata folder, with a project open in the editor, such as your copy of `OpenWorld`; on Linux and macOS, pipe with `echo`. A line that makes an entity prints its `id`: write the root's in place of `<Torch>`.

   ```powershell
   '{"name": "Torches"}' | .\StrataCLI call scene.new -
   '{"name": "Torch"}' | .\StrataCLI call entity.create -
   '{"name": "Flame", "parent": "<Torch>", "components": {"PointLight": {"Intensity": 3, "Range": 6}, "AudioSource": {"Volume": 0.8}}}' | .\StrataCLI call entity.create -
   '{"entities": ["<Torch>"], "path": "Prefabs/Torch.stprefab"}' | .\StrataCLI call prefab.create -
   '{"prefab": "Prefabs/Torch.stprefab"}' | .\StrataCLI call prefab.instantiate -
   ```

   `prefab.create` links `Torch` itself as the first instance, T1. Run the last line three times for T2, T3 and T4. `'{"entity": "<root>"}' | .\StrataCLI call entity.get -` lists a root's `Flame` under `children`. These lines make the three changes and apply T4:

   ```powershell
   '{"entity": "<Flame of T2>", "component": "PointLight", "values": {"Range": 9}}' | .\StrataCLI call component.set -
   '{"entity": "<Flame of T3>", "component": "AudioSource"}' | .\StrataCLI call component.remove -
   '{"entity": "<Flame of T4>", "component": "PointLight", "values": {"Intensity": 4, "Range": 8}}' | .\StrataCLI call component.set -
   '{"entity": "<Flame of T4>", "component": "AudioSource", "values": {"Volume": 0.4}}' | .\StrataCLI call component.set -
   '{"entity": "<T4>"}' | .\StrataCLI call prefab.apply -
   ```

   Then `entity.get` and `prefab.status` of each flame show the result. [Commands](../editor/commands.md) teaches commands in full.

   :::answer{tests="propagation,overrides"}
   T1 takes everything: intensity 4, range 8, volume 0.4. T2 keeps its range of 9, and takes intensity 4 and volume 0.4. T3 takes intensity 4 and range 8, and still has no `AudioSource`, because the prefab changed the sound's volume and did not add the component. `prefab.status` lists the instance's overrides: for T2 one of kind `Property` for `Range`, and for T3 one of kind `RemovedComponent` for `AudioSource`. The answer of `prefab.apply` reports `updatedInstances` as 3.
   :::

2. **Medium.** Trace it yourself: find where `prefab.apply` brings a change to the other instances. Write down the file, the loop and the function it calls for each other instance, and what it does with the result.

   :::answer{tests="propagation"}
   The command is registered in `StrataEditor/src/Editor/EditorPrefabCommands.cpp`, near the line `registry.Register({ "prefab.apply"`. After it builds the new snapshot, it collects the roots from `PrefabInstances::FindInstanceRoots` and skips the instance applied from. In a loop over those roots it gets the old and new parts from a `PrefabOverrides::PartChangeCache` and calls `PrefabOverrides::Propagate` with a `beforeChange` that tracks the entity in the undo transaction. Then it calls `PrefabInstances::MarkSynced` with the version and `result.ContentHash`.

   If one call fails, the transaction is rolled back and the command fails. Search the file for `Propagate` to find it.
   :::

3. **Hard.** Write a toy `Propagate` for one entity, on the maps of the toy above. It receives the prefab's components before and after, and an instance's. It computes the overrides, and gives the instance the changed properties that the list does not override, the components the prefab added, and the removal of components the prefab removed. Run it on the example's instances A, B and C.

   :::answer[Worked solution]{tests="propagation,overrides" solution="sketches/world-prefabs-propagate.cpp"}
   The solution computes the overrides against the old prefab, as `Propagate` does when no list is recorded. A property moves only when it differs between the old and the new prefab and is not overridden. A component the instance removed stays removed, and a component with any record is not removed by the prefab. The output shows A and B as the table of the example gives them, and C without a sound.

   ```cpp sketch="world-prefabs-propagate.cpp"
   // A toy Propagate for one entity: a prefab's change reaches an instance except where the instance overrides it.
   #include <cstdio>
   #include <map>
   #include <string>
   #include <vector>

   using Properties = std::map<std::string, std::string>;
   using Components = std::map<std::string, Properties>;

   struct Override
   {
   	std::string Component;
   	std::string Property;
   	std::string Kind;
   };

   std::vector<Override> Compare(const Components& prefab, const Components& instance)
   {
   	std::vector<Override> result;
   	for (const auto& [name, properties] : prefab)
   	{
   		const auto found = instance.find(name);
   		if (found == instance.end())
   		{
   			result.push_back({ name, "", "RemovedComponent" });
   			continue;
   		}
   		for (const auto& [property, value] : properties)
   		{
   			const auto other = found->second.find(property);
   			if (other == found->second.end() || other->second != value)
   				result.push_back({ name, property, "Property" });
   		}
   	}
   	for (const auto& [name, properties] : instance)
   	{
   		if (!prefab.contains(name))
   			result.push_back({ name, "", "AddedComponent" });
   	}
   	return result;
   }

   // An empty property asks about the whole component: any override of it counts.
   bool IsOverridden(const std::vector<Override>& overrides, const std::string& component, const std::string& property)
   {
   	for (const Override& entry : overrides)
   	{
   		if (entry.Component != component)
   			continue;
   		if (entry.Kind != "Property" || property.empty() || entry.Property == property)
   			return true;
   	}
   	return false;
   }

   void Propagate(const Components& previous, const Components& next, Components& instance)
   {
   	const std::vector<Override> overrides = Compare(previous, instance);
   	for (const auto& [name, values] : next)
   	{
   		const auto before = previous.find(name);
   		if (before == previous.end() && !instance.contains(name))
   		{
   			instance[name] = values; // The prefab added it
   			continue;
   		}
   		if (!instance.contains(name))
   			continue; // The instance removed it
   		for (const auto& [property, value] : values)
   		{
   			const bool known = before != previous.end() && before->second.contains(property);
   			const bool changed = !known || before->second.at(property) != value;
   			if (changed && !IsOverridden(overrides, name, property))
   				instance[name][property] = value;
   		}
   	}
   	for (const auto& [name, values] : previous)
   	{
   		if (!next.contains(name) && !IsOverridden(overrides, name, ""))
   			instance.erase(name); // The prefab removed it
   	}
   }

   void Print(const char* title, const Components& components)
   {
   	std::printf("%s:", title);
   	for (const auto& [name, properties] : components)
   	{
   		for (const auto& [property, value] : properties)
   			std::printf(" %s.%s=%s", name.c_str(), property.c_str(), value.c_str());
   	}
   	std::printf("\n");
   }

   int main()
   {
   	const Components before { { "PointLight", { { "Intensity", "5" }, { "Range", "10" } } }, { "AudioSource", { { "Volume", "1" } } } };
   	const Components after { { "PointLight", { { "Intensity", "6" }, { "Range", "15" } } }, { "AudioSource", { { "Volume", "0.5" } } } };

   	Components untouched = before;
   	Components brighter = before;
   	brighter["PointLight"]["Intensity"] = "8";
   	Components silent = before;
   	silent.erase("AudioSource");

   	Propagate(before, after, untouched);
   	Propagate(before, after, brighter);
   	Propagate(before, after, silent);
   	Print("untouched", untouched);
   	Print("brighter ", brighter);
   	Print("silent   ", silent);
   	return 0;
   }
   ```

   ```text output-of="world-prefabs-propagate.cpp"
   untouched: AudioSource.Volume=0.5 PointLight.Intensity=6 PointLight.Range=15
   brighter : AudioSource.Volume=0.5 PointLight.Intensity=8 PointLight.Range=15
   silent   : PointLight.Intensity=6 PointLight.Range=15
   ```

   1. **Lines 44–54:** An empty property asks about the whole component, and any record of it answers yes.
   2. **Lines 58–68:** The list comes from the old prefab; a component the prefab added is made, and one the instance removed stays removed.
   3. **Lines 69–76:** A property moves only when the old and new prefab differ and the list does not override it.
   4. **Lines 77–81:** The prefab's removal of a component reaches the instance unless it has a record.

   :::

## Where it lives in Strata

- `Strata/src/Strata/Scene/EntityPrototype.h` and `EntityPrototype.cpp`: `EntityPrototype`, `InstantiationOptions`, `PrototypeInstantiation`.
- `Strata/src/Strata/Scene/SceneInstantiation.cpp`: `Scene::BeginInstantiation`, `Scene::ContinueInstantiation`, `Scene::Instantiate`.
- `Strata/src/Strata/Scene/Prefab.h` and `Prefab.cpp`: `EntityTemplate`, `Prefab`, `Model`, `CompareInstance`.
- `Strata/src/Strata/Scene/SceneRegistration.cpp`: the loaders of Scene, Prefab and Model.
- `Strata/src/Strata/Scene/PrefabInstances.h` and `PrefabInstances.cpp`: instance roots, `ExtractTemplate`, `MakeTemplate`, `Compare`, `Replace`, `ReplaceTemplate`, `Link`, `Unpack`, `StripLinks`.
- `Strata/src/Strata/Scene/PrefabOverrides.h` and `PrefabOverrides.cpp`: `ComputeOverrides`, `UpdateOverrides`, `Propagate`, `Revert`, `ApplyToPart`.
- `Strata/src/Strata/Scene/Components.h` and `ComponentRegistration.cpp`: `PrefabInstanceComponent`, `PrefabOverride`.
- Commands: `prefab.apply`, `prefab.revert`, `prefab.unpack` and `prefab.status`, in `StrataEditor/src/Editor/EditorPrefabCommands.cpp`; `prefab.create`, in `StrataEditor/src/Editor/EditorAssetCommands.cpp`.
- Tests: the suites `Scene.Prefab`, `Scene.PrefabInstances`, `Scene.PrefabOverrides` and `Scene.Streaming`.

## Further reading

- Unity Manual, "Prefabs" (docs.unity3d.com/Manual/Prefabs.html): instances, overrides and the apply and revert of Unity's prefabs; beginner.
- Unity Manual, "Nested Prefabs" and "Prefab Variants" (docs.unity3d.com/Manual/NestedPrefabs.html and docs.unity3d.com/Manual/PrefabVariants.html): the deeper forms that Strata omits; intermediate.
- Unreal Engine documentation, "Blueprint Class" pages (Epic Games): classes whose defaults an instance in a level may override; intermediate.
