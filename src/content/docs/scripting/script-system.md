---
id: scripting/script-system
title: "The script system"
description: "How ScriptSystem turns Script components into instances, calls their callbacks in a fixed order and stays consistent while scripts change the scene."
kind: internals
size: L
tracks: [E]
needs: [scripting/loading, world/systems, assets/residency, physics/contacts-triggers, animation/time-events]
time: 95
learn:
  - id: callback-order
    text: predict the order of the callbacks a scene's scripts receive in one frame
  - id: safe-destroy
    text: explain why a script may destroy the entity whose callback is running
  - id: entries
    text: trace how an entry of the Script component gains, keeps or loses an instance
  - id: dispatch-cost
    text: explain how the update order, the dispatch lists and the prefetch keep thousands of scripts cheap
  - id: asset-requests
    text: explain how a script's asset requests are held, shared and released
since: 0.3.0
status: final
---

`ScriptSystem` runs the scripts of one playing scene. It reads the Script components and makes one object of the right class for each entry. It calls the class's :term[callbacks]{id=callback} in a fixed order every frame and keeps its lists correct while the scripts create and destroy entities under it. It does not load the module: [the loading page](../scripting/loading.md) covers that.

Replacing instances on a hot reload is the subject of [hot reload](../scripting/hot-reload.md). The functions that scripts call form the engine's application programming interface (API) for scripts, which [the host API](../scripting/host-api.md) describes. Finding contacts and :term[animation events]{id=animation-event-notify} belongs to their own pages. Game makers meet the same life of a script from the other side in [the script loop](../make/script-loop.md). The page names the callbacks first, because you need their order before you read the code that produces it.

## The problem and how engines solve it

A game has thousands of small pieces of behaviour: a door that opens, a coin that spins, an enemy that turns. Each piece is a script written by a different person, and the engine knows nothing about what it does. The engine must call every script every frame, in an order that gives the same result on every run, and it must do so while those scripts create entities, destroy entities and remove each other. [Why games use scripts](../scripting/why-scripts.md) explains why the logic lives outside the engine; this page is about running it safely.

Consider one script that destroys the entity it is attached to. If the engine frees the entity at once, the engine is still inside that script's callback, and the rest of the callback reads memory that no longer exists. Consider a second script that spawns a prefab with three scripted children while the engine walks the list of all scripts. If the walk appends to the list it is reading, the list may move in memory. Consider a third: a script on a destroyed entity wants to say goodbye in `OnDestroy`, but the entity must still exist for that call.

Engines answer in a few ways: a plain design gives every object an update function and calls it, with no lists and nothing that waits, which is the simplest and breaks in the cases above. A second design records every change in a :term[command buffer]{id=command-list} and applies the buffer at known moments. A third gives every entity a number that also counts how often the slot was used again, so a stale reference is detected instead of followed. Strata mixes the second and third. Changes that endanger running code wait for a sync point, and every callback runs against copies of the lists it walks.

A **sync point** is a moment at which no script code is running, where the system applies the changes scripts asked for: destroying entities, creating instances, calling `OnReload` and `OnCreate`.

The price is latency. A script that asks to destroy an entity sees it alive for the rest of the frame, and a script created in a frame starts at the next sync point, not at once. The rest of the page shows where the sync points are and why the delays are the right price.

## The map: files, threads and one frame

All the code lives in `Strata/src/Strata/Scripting/`. `ScriptingRegistration.cpp` registers the Script component and the :term[scene system]{id=scene-system}. `ScriptingComponents.h` and `.cpp` hold the component and its :term[serialization]{id=serialization}. `ScriptSystem.h` and `.cpp` hold the system, about 1,560 lines; `ScriptModule.cpp` makes the guarded calls into the module, and `ScriptEngine.cpp` owns the module and its reload. Everything on this page runs on the :term[main thread]{id=main-thread}: scripts never run anywhere else, and the host functions refuse other threads.

### The callbacks and their order

A **callback** is a method of a script class that the engine calls: `OnUpdate` once per frame, `OnTriggerEnter` when a trigger is entered. A class implements the callbacks it needs and leaves the others empty. The :term[class descriptor]{id=class-descriptor}, the C structure that the module completes to describe one class, lists 15 callbacks. The table gives each one, when it runs and when it was added to the interface.

| Callback | Runs | Arrived |
| --- | --- | --- |
| `OnCreate` | once per instance, at a sync point, before its first update | the first set |
| `OnUpdate` | once per frame, with the frame's scaled :term[delta time]{id=delta-time} | the first set |
| `OnFixedUpdate` | once per :term[fixed step]{id=fixed-step}, so zero or more times per frame | the first set |
| `OnLateUpdate` | once per frame, after the fixed steps | the first set |
| `OnDestroy` | once, while the entity still exists | the first set |
| `OnReload` | after a hot reload recreated the instance | the first set |
| `OnCollisionEnter`, `OnCollisionExit`, `OnTriggerEnter`, `OnTriggerExit` | after the step that found the contact change | added next, for physics contacts |
| `OnAnimationEvent` | when an animator state passes a named event | added for animation |
| `OnUIClick`, `OnUIValueChanged`, `OnUIFocusChanged` | from the player's input, before the frame's `OnUpdate` | added for the game's user interface (UI) |
| `OnUISubmit` | when an input field's text is submitted | added last |

Four lists must agree on these callbacks. They are the members of the C structure `StrataScriptClassDesc`, the engine's enum `ScriptCallback`, the :term[SDK's]{id=sdk} `CallbackFlag` bits, and the engine's `ClassFunctions` copy of the module's :term[function pointers]{id=function-pointer}. Adding a callback means adding it to all four, at the end. The count `c_ScriptCallbackCount` follows the last enum value by itself. A module built before a callback existed has a smaller descriptor, and the engine reads a callback only when the descriptor's `StructSize` covers it.

The frame has one order, and the scene's update builds it. The figure follows one frame from the scripts' side.

```mermaid caption="One frame of a playing scene as the scripts see it, from the game interface events to the destruction at the end." alt="A flow chart with ten boxes. World transforms settle first, then come interface events, the update callbacks, animation events and physics changes. A loop of fixed steps follows, each with script steps, a physics step and contacts. After the loop the step alpha is final, then the late callbacks run, and destruction ends the frame."
flowchart TD
	A["World transforms settle"] --> B["UI system: OnUIClick, OnUIValueChanged, OnUIFocusChanged"]
	B --> C["Scripting: OnUpdate, sync point before and after"]
	C --> D["Animation: OnAnimationEvent"]
	D --> E["Physics: pending changes applied, contacts of those changes"]
	E --> F{"Fixed step due?"}
	F -->|"yes, up to the limit"| G["Scripting: OnFixedUpdate, sync point; Physics: step, then OnCollision and OnTrigger"]
	G --> F
	F -->|"no"| H["Step alpha is final"]
	H --> I["Scripting: OnLateUpdate, sync point"]
	I --> J["End of frame: deferred destroys, OnDestroy"]
```

The order comes from the systems' constraints, as [the page on systems](../world/systems.md) explains. The game UI system names the scripts as the system it runs before. Animation, physics, audio and the world each name the scripts as a system they run after. So scripts move entities before anything simulates them, and scripts set animator parameters before the animators evaluate. Two facts in the figure matter for game code.

First, the step alpha, the fraction of the way between the last two fixed poses that the frame draws (see [interpolation](../world/interpolation.md)), is set after the last fixed step and before `OnLateUpdate`. Code in `OnUpdate` reads the value of the previous frame. A camera that follows a drawn pose therefore reads it in `OnLateUpdate`. A platform that carries a player moves in `OnFixedUpdate`, because the physics step that follows must see the platform's new pose.

Second, press and release edges are changes since the previous frame. `OnFixedUpdate` can run twice in a frame or not at all, so an edge read there is repeated or missed. Read edges in `OnUpdate`, once per frame, and held state anywhere.

### The life of an instance

An **instance** is one object of a script class that the system makes for one entry of a Script component. It has a small number of states, shown in the second figure.

```mermaid caption="The states of one script instance, from construction to destruction, with the branches for an exception and a module reload." alt="A state diagram. An instance is constructed with its fields, waits for its start, then is created. From created it can be disabled by an exception, removed, or reconstructed by a module reload, which returns it to created. Removed instances are destroyed at a sync point."
stateDiagram-v2
	[*] --> Constructed: Create, then field overrides
	Constructed --> PendingStart: appended to the update order
	PendingStart --> Created: OnCreate at a sync point
	Created --> Disabled: a callback throws
	Created --> Reconstructed: module reload, fields restored
	Reconstructed --> Created: OnReload
	Created --> Removed: script removed or entity destroyed
	Disabled --> Removed
	PendingStart --> Removed
	Removed --> [*]: OnDestroy and destructor at a sync point
```

Two states deserve a sentence. A disabled instance stays alive and keeps its fields, but gets no more callbacks, not even `OnDestroy` when it is removed. Only a module reload, which constructs it again, gives it callbacks again. A faulted module is one that crashed inside script code. The system makes no further call into it, and its instances are abandoned on purpose, because nothing in that module can be trusted.

## The contract

What callers may assume, and what script code and engine code must do, each with its reason.

- **Order is deterministic.** Instances run in hierarchy order, parents first, then in the entry order of each entity's Script component. Reason: a result must not depend on the order in which memory was allocated, or two runs would differ.
- **Callbacks run only on active entities.** An entity that is inactive in the hierarchy gets no `OnUpdate`, `OnFixedUpdate` or `OnLateUpdate`, no new contacts and no animation events. `OnCreate` and `OnDestroy` run anyway. Reason: an inactive entity is switched off, but its object still must start and end properly. No `Scripting.*` test plays a script on an entity that is inactive at its start, so the `OnCreate` half is read from the code, not tested.
- **An exception disables the instance.** A crash faults the module. Reason: after an exception the module's memory is consistent, because the call stack was cleaned up; after a crash nothing is known.
- **`OnCreate` runs once.** An instance gets it once, even if that call throws, because the system marks the instance before the call.

:::rule
Script code must not run while the engine holds state that the code could break. Destroy entities through `ScriptSystem::DestroyEntity`. Reason: `OnDestroy` and :term[destructors]{id=destructor} are script code, and they may touch the lists the engine is walking. See [systems, phases and fixed steps](../world/systems.md) for the way the scene itself delays destruction.
:::

- **Never keep a `T*` from `GetScript<T>()` across frames.** Store the `Entity` and ask again. Reason: the instance may be destroyed or rebuilt by a reload, and the pointer then points to freed memory.
- **Request assets early.** `Instantiate` never waits, so it returns nothing for an asset that is not loaded yet. Reason: waiting on the main thread would freeze the frame.
- **Read press edges in `OnUpdate`, the drawn pose in `OnLateUpdate`, and move ridden platforms in `OnFixedUpdate`.** Reason: see the two facts above.

## A toy version

The toy keeps three ideas of the real system and drops the rest. It has a list of instances, a frame with a sync point at both ends of the update, and destruction that waits for the sync point. Each instance may ask to destroy another one, or spawn a new one, in its first update. Look at the walk in `Frame`: the count is taken once, and the destroy list is copied before it is applied.

```cpp sketch="scripting-script-system-toy.cpp"
// A toy script system: instances, a deferred destroy and a sync point at both ends of the update.
#include <cstdio>
#include <memory>
#include <string>
#include <vector>

struct Instance
{
	std::string Name;
	std::string Target; // Another instance this one asks to destroy in its first update
	bool Spawns = false;
	bool Created = false;
	bool Removed = false;
};

class ToySystem
{
public:
	void Add(const std::string& name, const std::string& target, bool spawns)
	{
		auto instance = std::make_shared<Instance>();
		instance->Name = name;
		instance->Target = target;
		instance->Spawns = spawns;
		m_Order.push_back(instance);
		m_PendingStart.push_back(instance);
	}

	void Frame(int number)
	{
		std::printf("frame %d\n", number);
		SyncPoint();
		// The count is taken once: instances added during the walk wait for the next frame.
		const size_t count = m_Order.size();
		for (size_t index = 0; index < count; index++)
		{
			Instance& instance = *m_Order[index];
			if (instance.Removed)
				continue;
			std::printf("  update %s\n", instance.Name.c_str());
			if (!instance.Target.empty())
				m_Deferred.push_back(instance.Target);
			instance.Target.clear();
			if (instance.Spawns)
				Add("D", "", false);
			instance.Spawns = false;
		}
		SyncPoint();
	}

private:
	void SyncPoint()
	{
		// Copies: the callbacks may ask for more destroys and creations.
		const std::vector<std::string> destroys = std::move(m_Deferred);
		m_Deferred.clear();
		for (const std::string& name : destroys)
		{
			for (const std::shared_ptr<Instance>& instance : m_Order)
			{
				if (instance->Name == name && !instance->Removed)
				{
					instance->Removed = true;
					std::printf("  destroy %s\n", name.c_str());
				}
			}
		}
		const std::vector<std::shared_ptr<Instance>> starts = std::move(m_PendingStart);
		m_PendingStart.clear();
		for (const std::shared_ptr<Instance>& instance : starts)
		{
			instance->Created = true;
			std::printf("  create %s\n", instance->Name.c_str());
		}
	}

	std::vector<std::shared_ptr<Instance>> m_Order;
	std::vector<std::shared_ptr<Instance>> m_PendingStart;
	std::vector<std::string> m_Deferred;
};

int main()
{
	ToySystem system;
	system.Add("A", "B", false);
	system.Add("B", "B", false);
	system.Add("C", "", true);
	system.Frame(1);
	system.Frame(2);
	return 0;
}
```

```text output-of="scripting-script-system-toy.cpp"
frame 1
  create A
  create B
  create C
  update A
  update B
  update C
  destroy B
  create D
frame 2
  update A
  update C
  update D
```

1. **Line 34:** the count is taken once, so an instance added during the walk waits for the next frame.
2. **Line 42:** a script's request to destroy only records the name.
3. **Line 45:** a spawn only appends; the new instance starts at the next sync point.
4. **Line 55:** the destroy list is moved out and applied from the copy.
5. **Line 63:** destruction sets a flag; the walk skips flagged instances.

The toy output shows the contract at work. `B` asks to destroy itself in frame 1, yet it still updates before the frame ends. `D` is created by a script, but it starts at the sync point and first updates in frame 2.

The real system differs in many ways. Its instances live in the module, behind guarded calls; it has three :term[update phases]{id=update-phases}; it keeps lists per callback; and it creates instances in reaction to changes of the components, not from a function. The next sections follow the data in the order it flows.

## The real code

### Registration and the Script component

The Script component holds a list of entries. Each entry has a class name and a list of field overrides. A **field override** is a value stored in the entry for one field of its class. A field the entry does not list keeps the default its class gives it.

Entity and asset fields are references: the component reports them to the registry, which can remap them and compare them like the references of any other component. The component has a :term[JSON]{id=json} form (`Class` and `Fields` with a type and a value per field) and a binary one.

The module registers the component and the scene system. The next quote shows the system's registration: a name, a flag that keeps it out of Simulate mode, and the profile stage that times it.

```cpp src="Strata/src/Strata/Scripting/ScriptingRegistration.cpp#L11-L24" symbol="RegisterScriptingModule"
void RegisterScriptingModule()
{
	RegisterScriptingComponents();

	// Scripts update first, so gameplay code moves entities before they are simulated (Physics runs after Scripting).
	// They do not run in simulate mode. Scenes use the script engine that is active when they start playing.
	SceneSystemDescriptor descriptor = MakeSceneSystemDescriptor<ScriptSystem>("Scripting", false, [](Scene& scene)
	{
		return CreateScope<ScriptSystem>(scene, ScriptEngine::GetActive());
	});
	descriptor.ProfileStage = "Scene.Scripts";
	const bool registered = SceneSystemRegistry::Register(std::move(descriptor));
	ST_CORE_VERIFY(registered, "The scripting module could not register its scene system");
}
```

1. **Line 13:** the component is registered first, so scenes can hold and save scripts.
2. **Line 17:** the name, and `false` for Simulate mode: scripts run in Play only.
3. **Line 21:** the profile stage, which the profiler names Scene.Scripts, times all scripts together.
4. **Line 23:** a duplicate name would stop the program, because the engine cannot run without its scripts.

The factory creates the system with the script engine that is active when the scene starts to play. Physics, animation, audio and the world declare that they run after the scripts, so no registration here names them.

### Starting and stopping play

`OnRuntimeStart` connects the system to the registry and to the three event services of the scene (contacts, animation, game UI). It then marks every scripted entity as changed, in hierarchy order, so creation is :term[deterministic]{id=determinism}. When the scripted entities are few among many, the system sorts them by comparing hierarchy positions; walking a hierarchy of a million entities for a few scripts would be wasteful. It creates nothing yet.

The creation happens in `OnRuntimeStarted`, which the scene calls after every system ran `OnRuntimeStart`. There the system runs its first sync point: it makes the instances and runs each `OnCreate`. Because every system exists by then, `OnCreate` can use physics and animation.

`OnRuntimeStop` removes the listeners, blocks creation and destroys every instance in the reverse of the update order. Descendants are therefore destroyed before their ancestors, and the last script of an entity goes first. It destroys the instances before it clears the asset pins, because `OnDestroy` may still request or release an asset.

### Calls, results and the three update phases

Every call into the module goes through `ScriptModule`, which guards it. The system looks at the result. An exception from the script disables the instance and logs an error naming the script, the entity and the callback. A crash faults the module, and from then on `GetUsableModule` returns nothing, so no further call happens.

The next quote shows the three phases of a frame. Look at the sync points and at the one call that only the first phase makes.

```cpp src="Strata/src/Strata/Scripting/ScriptSystem.cpp#L195-L221"
void ScriptSystem::OnUpdate(Timestep timestep)
{
	ST_PROFILE_FUNCTION();

	m_DeltaTime = timestep;
	SyncPoint();
	RebuildUpdateOrder();
	RunCallbacks(ScriptCallback::OnUpdate, timestep);
	SyncPoint();
}

void ScriptSystem::OnFixedUpdate(float fixedTimestep)
{
	ST_PROFILE_FUNCTION();

	RunCallbacks(ScriptCallback::OnFixedUpdate, fixedTimestep);
	SyncPoint();
}

void ScriptSystem::OnLateUpdate(Timestep timestep)
{
	ST_PROFILE_FUNCTION();

	m_DeltaTime = timestep;
	RunCallbacks(ScriptCallback::OnLateUpdate, timestep);
	SyncPoint();
}
```

1. **Lines 200–203:** a sync point first, the order brought up to date, the callbacks, a sync point again.
2. **Line 201:** the rebuild of the order, the one call that only the first phase makes; the other two phases keep the order as it is.
3. **Lines 210–211:** each fixed step ends with a sync point, so `OnCreate` of a script spawned in a step runs before the next step.
4. **Lines 219–220:** the late phase runs the late callbacks and a last sync point; the scene's destruction follows after it.

### Sync points and reconciliation

A sync point is a loop. Each round runs four steps:

1. The round destroys the entities that scripts asked to destroy.
2. The round matches the entries of each changed entity against its instances, which the system calls reconciliation.
3. The round runs `OnReload` for instances that a reload recreated.
4. The round runs `OnCreate` for new instances.

The loop repeats while any step left work behind, because script code in those steps can create more work.

The loop is bounded at 64 rounds. A script that spawns its own prefab in `OnCreate` would otherwise hang the frame. After 64 rounds the system reports a problem, finishes the removals (each instance is destroyed once, so that ends) and leaves creation for the next sync point.

```cpp src="Strata/src/Strata/Scripting/ScriptSystem.cpp#L487-L505" symbol="ScriptSystem::SyncPoint"
void ScriptSystem::SyncPoint()
{
	for (uint32_t round = 0; m_Running && HasPendingWork(); round++)
	{
		if (round == c_MaxSyncRounds)
		{
			ReportProblem("Scripting", fmt::format("scripts keep creating scripted entities while starting; the rest is created at the next update "
				"(after {} rounds)", c_MaxSyncRounds));
			// Removals still complete now (each instance is destroyed once, so this ends); creation waits.
			DestroyRemovedInstances(m_UpdateOrder);
			return;
		}

		FlushDeferredDestroys();
		ReconcileDirtyEntities(true);
		RunPendingReloads();
		RunPendingStarts();
	}
}
```

1. **Line 489:** the loop runs while any work is pending and the scene is playing.
2. **Line 491:** the bound; the problem report names the cause.
3. **Line 496:** removals finish even at the bound, so no instance is left half destroyed.
4. **Lines 500–503:** the four steps, in this order.

Reconciliation is driven by the registry's signals. The system connects to the construction, update and destruction of Script components, and each signal marks the entity as dirty. At a sync point, `ReconcileEntity` destroys the instances whose entry is gone, creates the instances of the entries that lack one, and sorts the entity's instances into entry order. An entity whose entries all have instances costs one scan, and no copy.

### Entries the module cannot serve

An entry can name a class that the loaded module does not have: the class was renamed or deleted, or the module is another game's. The system creates no instance for it and reports a problem naming the entity, the class and the module. A class listed twice on one entity runs once, and the duplicate is reported.

On a hot reload the rule is the same. A class that no longer exists loses its instances, with a problem, while its entries stay in the scene. After the reload every entity is matched again, so the entries get an instance again once a module has the class. Renaming a class therefore detaches it from every entity that used it, as renaming a field loses the value stored for it. Both are reported, and neither crashes anything.

### Deferred mutation

Script code can change the scene in the middle of any callback. The system protects itself in three ways. The first is deferred destruction.

`ScriptSystem::DestroyEntity` calls `Scene::DestroyEntity` while the scene updates, and the scene then only records the request. At the end of the frame, `FlushPendingDestroys` destroys the entities and calls `OnEntityDestroying` on each system. So `OnDestroy` runs while the entity is still valid. Outside an update, such as during a reload, the request waits in a list for the next sync point.

```cpp src="Strata/src/Strata/Scripting/ScriptSystem.cpp#L1485-L1496" symbol="ScriptSystem::DestroyEntity"
void ScriptSystem::DestroyEntity(Entity entity)
{
	if (!entity.IsValid())
		return;

	// While the scene updates it defers destruction itself. Otherwise (script code run during a module reload) this
	// waits for the next sync point, so script code is never destroyed while it runs.
	if (m_Scene.IsUpdating())
		m_Scene.DestroyEntity(entity);
	else
		m_DeferredDestroys.push_back(entity.GetUUID());
}
```

1. **Lines 1492–1493:** while the scene updates, the scene's own delay of destruction is used.
2. **Lines 1494–1495:** otherwise the request waits in a list for the next sync point.

The second way is flags. Removing a script sets the instance's `Removed` flag at once, and the instance is skipped from then on; its `OnDestroy` and destructor run at the next sync point. The third way is copies: wherever the system calls script code while it walks a list, it walks a copy, because a callback may add or remove scripts. The comments in `ScriptSystem.cpp` say "A copy" at each place.

A script may therefore destroy the entity whose callback is running. Nothing is freed while the callback is on the stack, and every list that the engine reads is a copy or stays untouched until the callback returns.

The copies and flags prevent the mistakes of the problem section. Those mistakes are holding a position in a list across a call to script code, freeing what a running callback uses, and letting scripts create work without a bound.

### Dispatch lists and prefetching

Looking at every instance every frame, and asking whether its class implements `OnUpdate`, would waste time on the many classes that do not. The system therefore keeps a **dispatch list** for each update callback, which is the list of the instances, in update order, whose class implements that callback. A frame calls only the instances in the list of its phase.

The loop that walks a list is the hottest code of the system. Look at how it reads the list, what it skips and what it fetches ahead.

```cpp src="Strata/src/Strata/Scripting/ScriptSystem.cpp#L241-L287" symbol="ScriptSystem::RunCallbacks"
void ScriptSystem::RunCallbacks(ScriptCallback callback, float argument)
{
	ScriptModule* module = GetUsableModule();
	if (!module || !m_Running)
		return;

	// Only instances whose class implements the callback are listed. Instances created during this phase are appended
	// and wait for the next phase (indices stay valid; the list is read by index because appending may reallocate it).
	// The instances stay alive while listed: m_UpdateOrder owns them and is not rebuilt during the walk.
	const std::vector<Instance*>& dispatch = GetDispatchList(callback);
	const entt::registry& registry = m_Scene.GetRegistry();
	const bool wasDispatching = m_Dispatching;
	m_Dispatching = true;
	const size_t count = dispatch.size();
	for (size_t index = 0; index < count; index++)
	{
		// Instances live in heap blocks of their own, and so do the module's script objects, so the first read of each
		// waits for memory unless it was fetched ahead. The hardware prefetchers do that only when they recognize the
		// allocation pattern, which they track by the address of the reading instruction: with identical sources, a
		// frame of 300,000 trivial scripts took 6.6 or 9.8 ms depending on where unrelated code moved this loop. The
		// loop fetches ahead itself, so it is fast in every code layout. Prefetching never faults, so it may name module
		// memory outside a guarded call (and instances the walk will skip).
		if (index + c_InstancePrefetchDistance < count)
		{
			const Instance* ahead = dispatch[index + c_InstancePrefetchDistance];
			Prefetch(ahead);
			Prefetch(&ahead->Removed);
		}
		if (index + c_ScriptObjectPrefetchDistance < count)
			Prefetch(dispatch[index + c_ScriptObjectPrefetchDistance]->Handle);

		Instance& instance = *dispatch[index];
		if (instance.Removed || instance.Disabled || !instance.Created || !instance.Handle)
			continue;

		// Entities destroyed during this frame keep updating until the frame ends, like every other system sees them.
		// Activity is read from the cache the scene keeps exact.
		const entt::entity handle = instance.EntityHandle;
		if (!registry.valid(handle) || registry.get<IDComponent>(handle).ID != instance.Entity || !registry.get<WorldTransformComponent>(handle).ActiveInHierarchy)
			continue;

		Invoke(instance, callback, argument);
		if (module->IsFaulted())
			break;
	}
	m_Dispatching = wasDispatching;
}
```

1. **Line 254:** the count is taken once, so instances created during the phase wait for the next phase.
2. **Lines 266–270:** the two prefetches, for the instance and for the module's object.
3. **Line 273:** the skip conditions on the instance's own flags.
4. **Line 279:** the activity read from the scene's cache, after the identifier check.
5. **Lines 282–284:** the call, and a stop when the module faulted.

Memory is the problem. Each instance is a heap block of its own, and so is the module's script object behind it. A callback of a small script takes about 20 ns, and a read that misses the cache takes about 100 ns. Take 300,000 scripts: the callbacks add up to 300,000 × 20 ns = 6 ms, and if every first read waited the full 100 ns, the waits would add up to 30 ms more.

A **prefetch** is an instruction that asks the processor to start loading a piece of memory into its cache before the code needs it. Processors also prefetch by themselves, but only when they recognize the pattern of addresses, and they track it by the address of the reading instruction. A comment in the code reports the result: with identical sources, a frame of 300,000 small scripts took 6.6 ms or 9.8 ms depending on where unrelated code moved this loop. The loop therefore prefetches itself, 12 instances ahead and, once the instance is there, the module's object 4 ahead, and it is fast in every layout. Prefetching never faults, so it may name module memory outside a guarded call.

:::example
Take a list of 100,000 instances at index 1,000. The loop prefetches the instance at index 1,012 and its `Removed` flag, and the script object of the instance at index 1,004. A fetch started 12 callbacks ahead has about 12 × 20 ns = 240 ns to finish, which is longer than the 100 ns a miss costs. The instance at index 1,004 was fetched 8 steps earlier, so its object can be requested without waiting for the instance.
:::

The skip conditions stand before the call. An instance that is removed, disabled, not created or without a handle is skipped. The loop reads the entity's activity from the :term[world transform]{id=world-transform} component's cached flag, which the scene keeps exact, so it does not walk the hierarchy to ask. The loop also checks that the entity handle still carries the same unique identifier, since the handle of a destroyed entity may be used again by another entity.

Entities destroyed during the frame keep updating until it ends. If the module faults, the loop stops.

### Update order and its cost

The **update order** is the order in which instances get their callbacks: hierarchy order, then entry order. The simplest way to keep it is to walk the whole scene hierarchy whenever something changes. That costs a pass over every entity, even when a single door spawned. Strata keeps the order incrementally.

The system keeps a flat array of all instances. The first `m_PlacedCount` of them are in hierarchy order, and new instances follow in creation order. At the start of a frame, `RebuildUpdateOrder` compares two version numbers, the scene's :term[hierarchy version]{id=hierarchy-version} and its own instance-set version. It returns when neither changed.

Otherwise it places each new instance at its entity's position, found by :term[binary search]{id=binary-search} among the placed ones. It also places again the instances of scripted entities that moved in the hierarchy, asking the scene which :term[subtrees]{id=subtree} moved.

```mermaid caption="Placing a new instance into the update order: it first waits in the tail, then a binary search puts it between the instances it belongs between." alt="Two chains of boxes. In the first, three placed instances of the Door and the Crate are followed by a tail box for a new Window instance. In the second, the Window instance sits between the Door instances and the Crate instance."
flowchart TD
	subgraph A["Frame 1: placed prefix, appended tail"]
		direction LR
		a1["Door.Hinge"] --> a2["Door.Lock"] --> a3["Crate.Spin"] -.-> a4["tail: Window.Open"]
	end
	subgraph B["Frame 2: placed by binary search"]
		direction LR
		b1["Door.Hinge"] --> b2["Door.Lock"] --> b3["Window.Open"] --> b4["Crate.Spin"]
	end
	A --> B
```

Take the figure with numbers. With 1,000 placed instances, a binary search needs at most 10 comparisons, because 2 to the power 10 is 1,024. Walking the whole hierarchy would read every entity, so one spawn in a scene of 100,000 entities costs 10 comparisons and one move of the array's entries, not 100,000 reads. When many instances arrive at once, the system estimates both costs and takes the walk if it is cheaper.

Destroyed instances are not removed at once. They stay in the list as dead entries, which the dispatch skips, and a counter records how many there are. When that count passes one eighth of the placed instances, the next rebuild compacts the lists in one pass. With 800 placed instances, the 101st removal triggers the compaction, since 101 is more than 800 / 8 = 100. The price of waiting is a little memory and a few skipped entries; the gain is that destroying a few scripted entities per frame costs nothing in the order.

The system exposes counters for tests: `GetReconcileCount`, `GetUpdateOrderRebuildCount` and `GetFullUpdateOrderBuildCount`. They let a test check that frames without changes do no work.

### Contacts, animation events and UI events

Physics reports contact changes through a :term[scene service]{id=scene-service}, and the system registers a listener. Only entities whose scripts implement a contact callback are watched, so physics tracks the contacts of no others. Each event reaches both entities, and the normal points toward the other one, so the system passes the flipped normal to the second entity.

```cpp src="Strata/src/Strata/Scripting/ScriptSystem.cpp#L340-L383" symbol="ScriptSystem::DeliverContact"
void ScriptSystem::DeliverContact(UUID entityID, UUID otherID, bool begin, ScriptCallback callback, const glm::vec3& point, const glm::vec3& normal)
{
	if (!m_Running || !GetUsableModule())
		return;
	auto it = m_Instances.find(entityID);
	if (it == m_Instances.end())
		return;
	// Like the update callbacks, contacts begin for the scripts of active entities only (entities destroyed during this
	// frame included). A contact that began ends for the scripts that were told, also when their entity was deactivated
	// meanwhile (that ends its contacts): every Enter has its Exit.
	const Entity entity = m_Scene.GetEntityByUUID(entityID);
	if (!entity || (begin && !m_Scene.IsActiveInHierarchy(entity)))
		return;

	StrataScriptCollision contact = {};
	contact.StructSize = sizeof(StrataScriptCollision);
	contact.Other = static_cast<uint64_t>(otherID);
	for (int axis = 0; axis < 3; axis++)
	{
		contact.Point[axis] = point[axis];
		contact.Normal[axis] = normal[axis];
	}

	// A copy: the callbacks may add or remove scripts (removed instances are flagged and skipped).
	const std::vector<Ref<Instance>> instances = it->second;
	for (const Ref<Instance>& instance : instances)
	{
		if (instance->Removed || instance->Disabled || !instance->Created || !instance->Handle)
			continue;
		// Whether or not the script implements the callback: one that only implements the Exit still gets it.
		if (begin)
			instance->Contacts.insert(otherID);
		else if (instance->Contacts.erase(otherID) == 0)
			continue;
		if (!instance->Class->Implements(callback))
			continue;

		ScriptModule* module = GetUsableModule();
		if (!module)
			return;
		const ScriptCallSite site = MakeCallSite(*instance, ScriptCallbackToString(callback));
		HandleCallResult(*instance, callback, module->InvokeContactCallback(site, instance->Handle, callback, contact));
	}
}
```

1. **Line 351:** a contact begins only for an active entity; an end is always delivered.
2. **Line 364:** a copy of the instance list, since callbacks may add or remove scripts.
3. **Lines 371–372:** an Enter records the other entity; an Exit goes only to instances that recorded it.
4. **Line 374:** an instance without the callback is still recorded, but not called.

Contacts begin only for active entities, but a contact that began always ends. Each instance that got an Enter gets the matching Exit, even if its entity was switched off meanwhile. The same holds if its class implements only the Exit. The list `Contacts` of each instance records whom it was told about.

Animation events and UI events follow the same shape: find the instances of the entity, walk a copy of the list, skip the removed and disabled, call those whose class implements the callback. The animation event goes to the scripts of the animator's entity if it is active.

```cpp src="Strata/src/Strata/Scripting/ScriptSystem.cpp#L389-L409" symbol="ScriptSystem::OnAnimationEvent"
void ScriptSystem::OnAnimationEvent(const AnimationEventInfo& event)
{
	if (!m_Running || !GetUsableModule())
		return;
	auto it = m_Instances.find(event.AnimatorID);
	if (it == m_Instances.end() || !event.Animator || !m_Scene.IsActiveInHierarchy(event.Animator))
		return;

	// A copy: the callbacks may add or remove scripts (removed instances are flagged and skipped).
	const std::vector<Ref<Instance>> instances = it->second;
	for (const Ref<Instance>& instance : instances)
	{
		if (instance->Removed || instance->Disabled || !instance->Created || !instance->Handle || !instance->Class->Implements(ScriptCallback::OnAnimationEvent))
			continue;
		ScriptModule* module = GetUsableModule();
		if (!module)
			return;
		const ScriptCallSite site = MakeCallSite(*instance, ScriptCallbackToString(ScriptCallback::OnAnimationEvent));
		HandleCallResult(*instance, ScriptCallback::OnAnimationEvent, module->InvokeAnimationEventCallback(site, instance->Handle, event.Name));
	}
}
```

1. **Line 394:** the entity must have instances and be active.
2. **Line 398:** a copy of the list, as for contacts.
3. **Line 401:** the skip conditions, with the class's flag for this callback.
4. **Line 407:** the event's name is passed to the module's :term[thunk]{id=thunk}.

A UI event goes to the scripts of the widget's entity and then to those of its event target, each instance once.

### Fields

The class's fields are described by the module, and the entry stores a value per field. When an instance is constructed, the system applies the overrides by name and type. A name the class lacks, or a stored type that differs from the field's, is ignored with a reported problem; the instance keeps its default. Enum values are stored as :term[integers]{id=integer}.

Renaming a field in the source therefore loses the stored value, and changing its type does the same. The inspector and `script.get` read a live instance through `GetFieldValue`, and the inspector writes through `SetFieldValue`; both are guarded calls into the module, and `SetFieldValue` checks that the value has the field's type.

### Assets from game code

A script that wants an asset calls `Assets::RequestLoad`. The system asks the :term[asset manager]{id=asset-manager} for an `AssetPin` at normal priority, which keeps the asset resident, and stores the pin by the asset's handle. A second request for an asset the scene already pins only asks for the load again, in case the asset was unloaded on purpose. A progress query makes a group request for the asset's dependency closure and keeps that too. Stopping play releases every pin after the last `OnDestroy`.

The requests are the scene's, not the script's, and they do not add up. One `Assets::Release` ends a request that two scripts made. The asset may then be unloaded while the other script still uses it.

The rule follows: request early, in `OnCreate` or before a level starts, and spawn when the asset is loaded. `Instantiate` starts a load and returns nothing for an asset that is not ready, because blocking would freeze the frame. [Residency and pins](../assets/residency.md) explains what a pin does inside the asset manager.

### The example: the coin script

The `ThirdPerson` sample's `Coin` is a complete small script. It has three fields, finds its model in `OnCreate`, and counts itself in `OnTriggerEnter`. Look at what the first half does with entities.

```cpp src="Samples/ThirdPerson/Scripts/Coin.cpp#L10-L26"
class Coin : public Script
{
public:
	float SpinSpeed = 180.0f; // Degrees per second
	float BobHeight = 0.12f;  // Meters
	bool Collected = false;

	void OnCreate() override
	{
		const std::vector<Entity> children = GetEntity().GetChildren();
		m_Visual = children.empty() ? Entity() : children.front();
		if (m_Visual.IsValid())
			m_VisualTranslation = m_Visual.GetTransform().GetTranslation();
		m_Phase = static_cast<float>(GetEntity().GetID() % 628) * 0.01f; // Coins bob out of step
	}

	void OnReload() override { OnCreate(); }
```

1. **Line 17:** all setup is in `OnCreate`, never in a :term[constructor]{id=constructor}.
2. **Lines 19–20:** the model is the first child of the trigger entity.
3. **Line 26:** a reload calls `OnCreate` again, because only fields survive it.

The second half is the trigger and the class registration.

```cpp src="Samples/ThirdPerson/Scripts/Coin.cpp#L38-L59"
	void OnTriggerEnter(const Collision& collision) override
	{
		if (Collected || !collision.Other.IsValid() || collision.Other.GetTag() != "Player")
			return;
		Collected = true;
		if (CourseState* course = Scene::FindEntityByName("Game").GetScript<CourseState>())
			course->AddCoin(GetTransform().GetWorldPosition());
		GetEntity().SetActive(false);
	}
private:
	Entity m_Visual;
	glm::vec3 m_VisualTranslation = glm::vec3(0.0f); // Where the model sits on the trigger
	float m_Time = 0.0f;
	float m_Phase = 0.0f;
};

ST_SCRIPT_CLASS(Coin)
{
	ST_SCRIPT_FIELD(SpinSpeed);
	ST_SCRIPT_FIELD(BobHeight);
	ST_SCRIPT_FIELD(Collected);
}
```

1. **Line 38:** the trigger callback receives the other entity.
2. **Line 43:** the other script is found by name when needed, never kept across frames.
3. **Lines 54–59:** the registration lists the three fields the inspector shows.

:::example
A player walks through the coin's trigger at 60 :term[frames per second]{id=frame-rate} with a fixed step of 20 ms. The step that finds the overlap ends with the physics system reporting the contact. The system calls `OnTriggerEnter` on the coin's instance with the player as `Other` and the normal pointing at the player. The tag is `Player`, so the coin finds the `Game` entity and calls `AddCoin` on its `CourseState` script, then switches itself off. When the player leaves, the system forgets the contact, and the coin has no `OnTriggerExit`, so nothing is called.
:::

The `Collected` field is registered, so the inspector shows it and a saved game could keep it. `OnReload` calls `OnCreate` again, because a reload recreates the instance and only fields survive.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| An update function on every object, no lists | Simple engines and the "Update Method" pattern | Less code and no list care | A call for every object that does nothing, and an order that follows memory |
| A command buffer for every change | Frameworks built on entity-component data | One place where changes apply, simple to follow | Scripts could not read their own changes at once, and every host function would queue |
| Sorting the order again each frame | Designs that favour simplicity | No incremental code and no dead entries | A pass over every instance every frame, even when nothing moved |
| Only stable ids, no waiting | Libraries whose entity ids carry a generation | Destruction at once, with stale ids detected | A callback could free its own entity and then read it |

## How it is tested

The suite `Scripting.Lifecycle` plays scenes against a test module. Its cases check the order (hierarchy, then entries) and that inactive entities get no updates. They check that a few scripts among many entities start without a walk of the hierarchy. They also check that components changed while playing create and destroy instances, and that scripts create and destroy entities during updates. `Scripting.Fields` checks that overrides apply before `OnCreate`, that unknown overrides and those of the wrong type are ignored, and that they survive a scene file round trip.

`Scripting.Order` checks the incremental order against random spawns, moves and destructions, and that frames without changes never rebuild it. `Scripting.Collisions` checks that both entities get the callbacks with the normal pointing at the other one, and that every Enter ends with an Exit. It also checks that scripts may destroy their own entity or the other one inside a contact callback.

The suite `Perf.Scripting` measures dispatch. The metric `TrivialUpdate100k` of the `Perf.Scripting` suite runs frames of 100,000 small scripts against a budget and checks that the order is not rebuilt. Run it in a Release build: `build/windows/bin/Release/StrataTests.exe --test-suite=Perf.Scripting`. To see what the prefetch buys, comment out the three prefetch statements of `RunCallbacks`, rebuild and run it again. The comment in the code warns that the result also depends on where the :term[compiler]{id=compiler} puts the loop.

## Changing it safely

- Add a callback at the end of all four lists, and never change their order. Exercise it in the API test module, in a test of the scripting suites and in the feature scripts.
- Any code that calls script code while it walks a list must walk a copy or index by position, as every "A copy" comment shows. Reason: script code can change the lists.
- Destroy entities for scripts only through `ScriptSystem::DestroyEntity`. Reason: see the rule above.
- A change to the order must keep `Scripting.Order` and the rebuild count of the perf test at zero for frames without changes.
- A new engine event for scripts follows the shape of the animation event: a scene service, a listener that is removed at stop, a copy of the instance list, the skip conditions.
- Keep host functions at the end of the table and wrap them in `HostCall`; that is the host API's page.

## Summary

- The callbacks of a frame run in a fixed order: UI events, `OnUpdate`, animation events, the fixed steps with contacts, then `OnLateUpdate`, then destruction.
- Script code runs only at known points; destruction and creation wait for sync points, and lists are copied, so a script may destroy its own entity.
- An entry becomes an instance when the system matches the component against the module, and loses it when the class is missing or renamed.
- The update order, the dispatch lists and the prefetch keep the cost of a frame proportional to the scripts that act.
- A script's asset requests are the scene's, are shared, and end at one release or when play stops.

## Check yourself

1. A `Door` script implements `OnUpdate`, `OnFixedUpdate`, `OnTriggerEnter` and `OnLateUpdate`. In one frame two fixed steps run and the player enters the trigger during the second. In which order does `Door` receive its callbacks?
   :::answer{tests="callback-order"}
   `OnUpdate`, then `OnFixedUpdate` for step 1, then `OnFixedUpdate` for step 2, then `OnTriggerEnter`, then `OnLateUpdate`. The contact is found by the physics step, which runs after the scripts' fixed update of the same step, so the Enter comes after the second `OnFixedUpdate`. Choosing the Enter before step 2 forgets that scripts update before physics. Choosing it after `OnLateUpdate` forgets that contacts are delivered right after their step.
   :::
2. A script calls `ScriptSystem::DestroyEntity` on its own entity in `OnUpdate` and then reads its own transform. Is that safe, and when does its `OnDestroy` run?
   :::answer{tests="safe-destroy"}
   The call is safe. While the scene updates, the destruction is only recorded, and the entity stays valid until the end of the frame. Then `FlushPendingDestroys` destroys it, and `OnEntityDestroying` runs `OnDestroy` while the entity is still complete. Freeing it at once would leave the rest of the callback reading freed memory.
   :::
3. You rename the class `Coin` to `Pickup` in the source and rebuild. The scene holds 20 entries named `Coin`. What does the system do, and what must you do?
   :::answer{tests="entries"}
   The system creates no instance for the entries, because the module lacks the class, and it reports a problem for each entity. The entries stay in the scene. You must change the entries to `Pickup` in the editor, and the stored field values are lost as well, because the entries do not match the new class. Renaming detaches a class from every entity, like renaming a field loses its value.
   :::
4. A scene destroys 90 of its 700 placed instances in one frame. Does the next rebuild compact the lists, and what do the destroyed instances cost until then?
   :::answer{tests="dispatch-cost"}
   Yes. The limit is 700 / 8 = 87 in whole numbers, and 90 is more than 87, so the next rebuild compacts. Until then the dispatch skips each destroyed instance, at the price of one flag test. With 87 destroyed instances it would not compact. A reader who answers no has taken the limit as a half, not an eighth.
   :::
5. Two scripts request the same texture with `Assets::RequestLoad`, and one of them calls `Assets::Release`. Can the texture be unloaded?
   :::answer{tests="asset-requests"}
   Yes. Requests do not add up, so one release ends the scene's request, and the other script's use is not protected anymore. The two scripts must agree on who releases, or neither should release before play stops.
   :::

## Exercises

1. **Basic.** A scene has 1,600 placed instances. How many removals does it take before the lists are compacted? How many comparisons does a binary search need to place one new instance among them, at most?
   :::answer[Worked solution]{tests="dispatch-cost"}
   The limit is 1,600 / 8 = 200, so compaction happens at the 201st removal. A binary search halves the range each time: 2 to the power 11 is 2,048, which is at least 1,601, so 11 comparisons are enough, and 10 are not, since 1,024 is below 1,601.
   :::
2. **Medium.** Find every comment in `Strata/src/Strata/Scripting/ScriptSystem.cpp` that starts with "A copy" and, for one of them, build the bug that the copy prevents.
   :::answer[Worked solution]{tests="safe-destroy"}
   Search the file for the text "A copy". `ScriptSystem::OnEntityDestroying` is one place: it copies the entity's instance list, because `OnDestroy` runs script code that can add or remove scripts on the same entity. Without the copy, the loop would read a vector that its callbacks change, and an erase inside the loop would skip an instance or read past the end. The same holds in `DeliverContact`, `OnAnimationEvent` and `ReconcileEntity`. `OnUIEvent` copies its lists too, but its comment says so in the middle of a sentence.
   :::
3. **Hard.** Write a program that holds a placed order of eight instances by hierarchy position, inserts three new ones by binary search, and prints for each the index it takes and how many comparisons it needed.
   :::answer[Worked solution]{tests="dispatch-cost" solution="sketches/scripting-script-system-insert.cpp"}
   The program uses `std::upper_bound`, which finds the first entry whose position comes after the new one, with a function that counts its calls. Inserting before that entry keeps the order, as the system does for a new instance.

   ```cpp sketch="scripting-script-system-insert.cpp"
   // Places new instances into a placed update order by binary search and counts the comparisons.
   #include <algorithm>
   #include <cstdio>
   #include <vector>

   struct Entry
   {
   	int Position; // Hierarchy position of the entity: smaller runs first
   	const char* Name;
   };

   int main()
   {
   	std::vector<Entry> order = { { 10, "A" }, { 20, "B" }, { 30, "C" }, { 40, "D" }, { 50, "E" }, { 60, "F" }, { 70, "G" }, { 80, "H" } };
   	const std::vector<Entry> arrivals = { { 35, "X" }, { 5, "Y" }, { 75, "Z" } };

   	for (const Entry& arrival : arrivals)
   	{
   		int comparisons = 0;
   		// The first entry whose position comes after the arrival's: the arrival goes right before it.
   		const auto after = std::upper_bound(order.begin(), order.end(), arrival.Position, [&comparisons](int position, const Entry& entry)
   		{
   			comparisons++;
   			return position < entry.Position;
   		});
   		const size_t index = static_cast<size_t>(after - order.begin());
   		order.insert(after, arrival);
   		std::printf("%s goes to index %zu after %d comparisons\n", arrival.Name, index, comparisons);
   	}

   	for (const Entry& entry : order)
   		std::printf("%s ", entry.Name);
   	std::printf("\n");
   	return 0;
   }
   ```

   ```text output-of="scripting-script-system-insert.cpp"
   X goes to index 3 after 3 comparisons
   Y goes to index 0 after 4 comparisons
   Z goes to index 9 after 3 comparisons
   Y A B C X D E F G Z H 
   ```

   1. **Line 17:** one pass per arriving instance.
   2. **Line 21:** `std::upper_bound` finds the first entry that comes after the arrival.
   3. **Line 23:** the comparison function counts its own calls.
   4. **Line 27:** inserting before that entry keeps the order.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Scripting/ScriptSystem.h` and `ScriptSystem.cpp`: the system, its instances, sync points, update order, dispatch lists, events and asset requests.
- `Strata/src/Strata/Scripting/ScriptingRegistration.cpp` and `ScriptingComponents.cpp`: the registration, the component and its serialization.
- `Strata/src/Strata/Scripting/ScriptTypes.h`: the enum `ScriptCallback`. `StrataScriptCore/Include/StrataScript/ScriptABI.h` and `Script.h`: the class descriptor and `CallbackFlag`.
- `Samples/ThirdPerson/Scripts/Coin.cpp`: the example script.
- Tests: `StrataTests/src/Scripting/ScriptLifecycleTests.cpp`, `ScriptSystemOrderTests.cpp`, `ScriptCollisionTests.cpp` and `StrataTests/src/Perf/ScriptingPerfTests.cpp`.
- Commands: `script.get` reads the fields of live instances.

## Further reading

- Robert Nystrom, "Game Programming Patterns", chapters "Update Method" and "Data Locality": the simple design and the cost of memory order (beginner).
- Ulrich Drepper, "What Every Programmer Should Know About Memory", the sections on caches and prefetching: why a miss costs about 100 ns and how prefetching hides it (advanced).
- The EnTT documentation on entities and versions: how stale identifiers are detected (intermediate).
