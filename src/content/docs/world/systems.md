---
id: world/systems
title: "Systems, phases and fixed steps"
description: "How a playing scene calls its systems in a built order, runs fixed steps, keeps time, destroys entities safely and lets modules meet through services."
kind: internals
size: L
tracks: [E]
needs: [world/ecs, basics/threads, core/time, core/engine-modules, core/layers-registries]
time: 120
learn:
  - id: placement
    text: write a scene system with soft constraints and predict where it runs in the update order
  - id: frame
    text: trace which functions one runtime frame calls on which systems, in order
  - id: steps
    text: compute how many fixed steps a frame runs, what the accumulator carries and what is dropped
  - id: lifetime
    text: explain why destroying an entity during an update waits for the end of the frame and who hears of it first
  - id: services
    text: write a scene service that one system offers and another uses without including its module
since: 0.3.0
status: final
---

While a scene plays, something must run its scripts, step its physics, pose its animated characters and mix its sound. In Strata each of those jobs belongs to a **scene system**: an object that the scene creates when play starts and calls in a fixed order on every frame until play stops. This page teaches how that order is built and what a frame calls and when. It also covers how the scene keeps time, how entities are destroyed while systems run, and how systems of different modules meet without including each other. What each built-in system does is left to the pages of its own module.

## The problem and how engines solve it

Suppose a camera follows a player whose body moves by physics. The body runs at 4 m/s and physics steps 60 times a second, so the body advances 4 / 60 = 0.067 m in each step. If the camera updates before physics, it looks at where the body stood one step ago. The picture then shows the player 6.7 cm off the middle of the screen, and the offset changes with every change of speed. Order is not decoration: it decides which values each system reads.

Engines choose among three ways to fix an order. The first is a hard-coded order: the :term[main loop]{id=game-loop} calls input, scripts, physics and audio one after the other. Everything is visible in one place, but that loop must include every module, so a build without audio still names audio, and a game cannot add a step in the middle.

The second is priority numbers. Each system carries a number and the engine sorts by it, so a game adds a system by choosing a number between two others. The numbers mean nothing alone, two modules may choose the same one, and nothing records why physics is 100 and a camera 110.

The third is a :term[dependency graph]{id=dependency-graph}. Each system names the systems it must run after or before, and the engine sorts them with a topological sort, which [Engine modules](../core/engine-modules.md) teaches. The constraint records the reason, and a cycle can be found and reported.

:::elsewhere
Bevy lets you declare that a system runs `before` or `after` another one, and Unity's Entities package has the attributes `UpdateBefore` and `UpdateAfter` for the same purpose. Both name the neighbor instead of a number. The sources are in Further reading.
:::

Strata takes the third way and adds two rules of its own. A constraint toward another module's system is soft, so it is ignored when that module is not in the build. Among systems that no constraint orders, registration order decides. [Time](../core/time.md) teaches why physics runs in fixed steps; this page shows only the scene's code for them.

## A map of the systems

Three kinds of things take part, and each lives in one place. The registry of system descriptions is one object for the whole process. Each running scene owns its own system objects, its clocks and four lists of the systems to call in each phase. A system object is made at the start of play and destroyed at its end.

```mermaid caption="The six built-in systems in update order with the arrows of their soft constraints, and where two systems of a game fall." alt="Six boxes: UI, Scripting, Animation, World, Physics and Audio. Arrows run from UI to Scripting, from Scripting to Animation and World, from Animation and World to Physics, and from Physics to Audio. A box for a wind system stands before Physics, and a box for a camera system with no constraint stands after Audio."
flowchart LR
    UI["UI"] --> SC["Scripting"]
    SC --> AN["Animation"]
    SC --> WO["World"]
    AN --> PH["Physics"]
    WO --> PH
    WI["Wind (a game's system)"] --> PH
    PH --> AU["Audio"]
    AN --> AU
    WO --> AU
    AU --> CF["CameraFollow (no constraint)"]
```

The files follow the same split:

- `Strata/src/Strata/Scene/SceneSystem.h` holds the interface, the description of a system and the registry's functions.
- `Strata/src/Strata/Scene/SceneSystem.cpp` holds the registry and the code that builds the update order.
- `Strata/src/Strata/Scene/Scene.cpp` holds the :term[runtime]{id=runtime}: start, stop, one frame, destruction and the copy for play.
- `Strata/src/Strata/Scene/SceneServices.h` holds the interfaces that systems offer each other.
- Each module's `<Module>Registration.cpp` registers its system, and `Strata/src/Strata/Engine/BuiltinModules.cpp` is the :term[composition root]{id=composition-root} that opens the registry.

Everything runs on the :term[main thread]{id=main-thread}. The one exception is `Scene::Copy`, which copies component storages on the job system's threads while the main thread waits for the result.

## The contract

What may code that writes a system assume, and what must it do? Seven rules follow, each with its reason.

1. **Derive from `SceneSystem`, override only the functions you need, make them public and build the description with `MakeSceneSystemDescriptor<T>`.** The helper records the class for `GetSystem<T>` and detects what you override, so frames call only those functions.
2. **Order toward a system of another module with soft constraints.** A hard constraint to an absent system refuses your registration, and a soft one is ignored, so your system also works in a build without that module.
3. **Register before any scene runs.** Running scenes created their systems from the registry, so changes are refused while any scene plays.
4. **Destroy entities through the scene.** During an update the destruction waits for the end of the frame, so every handle stays valid until then.
5. **Meet other modules through scene services.** A service is null when its module is absent, and the layer rules forbid including a module that sits beside yours.
6. **Read the step through `GetFixedTimestep` and `GetMaxFixedSteps`.** The project's rate may override the scene's setting.
7. **Signal your writes.** A system that changes a transform in place tells the scene, as [The scene graph](../world/scene-graph.md) explains.

:::rule[Destruction during an update is deferred]
Code that runs inside an update never destroys an entity at once; `DestroyEntity` queues it and the scene destroys it after the late update. A system could otherwise remove a component while another system loops over that storage, and scripts need their entity complete when `OnDestroy` runs.
:::

:::rule[Order toward other modules with soft constraints]
A system names another module's system only in `AfterIfPresent` or `BeforeIfPresent`, so the engine still runs when that module is not built. Build every description with `MakeSceneSystemDescriptor<T>`, and let modules meet through scene services, never through `GetSystem` of a class they would have to include.
:::

## A toy version

Two short programs show the two jobs. The first builds the update order. Each system lists the systems that must run before it, and the program builds the order twice: from the back, as Strata does, and from the front. A :term[priority queue]{id=priority-queue} picks which ready system goes next. Search for `isBelow`, the comparison that makes the queue take the system registered last or first.

```cpp sketch="world-systems-order.cpp"
// Orders systems by their constraints twice: from the back, as Strata does, and from the front.
#include <cstdio>
#include <functional>
#include <queue>
#include <string>
#include <vector>

namespace
{
	struct System
	{
		std::string Name;
		std::vector<int> After; // indices of the systems that must run before this one
	};

	// Both builds take the ready system that is registered last (from the back) or first (from the front).
	std::vector<int> BuildOrder(const std::vector<System>& systems, bool fromBack)
	{
		const int count = static_cast<int>(systems.size());
		std::vector<std::vector<int>> released(count); // systems that may become ready once this one is placed
		std::vector<int> waiting(count, 0);            // systems each one still waits for
		for (int second = 0; second < count; second++)
		{
			for (int first : systems[second].After)
			{
				// From the back the walk runs against the update order.
				const int from = fromBack ? second : first;
				const int to = fromBack ? first : second;
				released[from].push_back(to);
				waiting[to]++;
			}
		}

		const auto isBelow = [fromBack](int a, int b) { return fromBack ? a < b : a > b; };
		std::priority_queue<int, std::vector<int>, decltype(isBelow)> ready(isBelow);
		for (int index = 0; index < count; index++)
		{
			if (waiting[index] == 0)
				ready.push(index);
		}

		std::vector<int> placed;
		while (!ready.empty())
		{
			const int index = ready.top();
			ready.pop();
			placed.push_back(index);
			for (int next : released[index])
			{
				if (--waiting[next] == 0)
					ready.push(next);
			}
		}
		if (placed.size() != systems.size())
			return {}; // a cycle: Strata refuses the registration
		if (fromBack)
			return std::vector<int>(placed.rbegin(), placed.rend());
		return placed;
	}
}

int main()
{
	// In registration order. Physics runs after Scripting and after Wind; CameraFollow has no constraint.
	const std::vector<System> systems = {
		{ "Scripting", {} },
		{ "Physics", { 0, 3 } },
		{ "CameraFollow", {} },
		{ "Wind", {} },
	};
	for (bool fromBack : { true, false })
	{
		std::printf("%s:", fromBack ? "from the back " : "from the front");
		for (int index : BuildOrder(systems, fromBack))
			std::printf(" %s", systems[index].Name.c_str());
		std::printf("\n");
	}
	return 0;
}
```

```text output-of="world-systems-order.cpp"
from the back : Scripting Wind Physics CameraFollow
from the front: Scripting CameraFollow Wind Physics
```

1. **Lines 22–32:** each constraint becomes an arrow, and each system counts the systems it still waits for.
2. **Lines 34–35:** the queue takes the largest registration index when building from the back, and the smallest from the front.
3. **Lines 43–53:** a placed system lets the systems that waited for it become ready.
4. **Lines 54–57:** systems that never become ready form a cycle, and the list built from the back is reversed at the end.

Only `Wind` has to come before Physics, and `CameraFollow` has no constraint at all. The back's order keeps `CameraFollow` after Physics because it was registered after Physics. The front's order moves it ahead of both `Wind` and Physics, which is the camera that lags in the problem above. [What went wrong before](#what-went-wrong-before) tells the real case.

The second program is a small scene. It calls three phases and runs fixed steps from an :term[accumulator]{id=accumulator}, with a cap that drops the owed steps. It counts in whole milliseconds so that every number is exact. Search for the loop that holds `c_MaxSteps`.

```cpp sketch="world-systems-frame.cpp"
// A toy scene: systems called in three phases, fixed steps from an accumulator, and a cap that drops the backlog.
#include <cstdio>
#include <vector>

namespace
{
	// Whole milliseconds keep the numbers exact; Strata's scene uses floats of seconds.
	constexpr int c_StepMs = 10;
	constexpr int c_MaxSteps = 8;

	class System
	{
	public:
		virtual ~System() = default;
		virtual void OnUpdate(int) {}
		virtual void OnFixedUpdate(int) {}
		virtual void OnLateUpdate(int) {}
	};

	class Counter : public System
	{
	public:
		void OnUpdate(int) override { Updates++; }
		void OnFixedUpdate(int) override { FixedUpdates++; }
		void OnLateUpdate(int) override { LateUpdates++; }

		int Updates = 0;
		int FixedUpdates = 0;
		int LateUpdates = 0;
	};

	class Scene
	{
	public:
		void AddSystem(System& system) { m_Systems.push_back(&system); }

		void Update(int frameMs)
		{
			for (System* system : m_Systems)
				system->OnUpdate(frameMs);

			m_AccumulatorMs += frameMs;
			int steps = 0;
			while (m_AccumulatorMs >= c_StepMs && steps < c_MaxSteps)
			{
				for (System* system : m_Systems)
					system->OnFixedUpdate(c_StepMs);
				m_AccumulatorMs -= c_StepMs;
				steps++;
			}
			int dropped = 0;
			if (steps == c_MaxSteps && m_AccumulatorMs > c_StepMs)
			{
				dropped = (m_AccumulatorMs - c_StepMs) / c_StepMs;
				m_AccumulatorMs = c_StepMs;
			}

			for (System* system : m_Systems)
				system->OnLateUpdate(frameMs);
			std::printf("frame of %5d ms: %d steps, %d dropped, %d ms carried\n", frameMs, steps, dropped, m_AccumulatorMs);
		}
	private:
		std::vector<System*> m_Systems;
		int m_AccumulatorMs = 0;
	};
}

int main()
{
	Scene scene;
	Counter counter;
	scene.AddSystem(counter);
	for (int frameMs : { 35, 6, 10000 })
		scene.Update(frameMs);
	std::printf("calls: %d update, %d fixed, %d late\n", counter.Updates, counter.FixedUpdates, counter.LateUpdates);
	return 0;
}
```

```text output-of="world-systems-frame.cpp"
frame of    35 ms: 3 steps, 0 dropped, 5 ms carried
frame of     6 ms: 1 steps, 0 dropped, 1 ms carried
frame of 10000 ms: 8 steps, 991 dropped, 10 ms carried
calls: 3 update, 12 fixed, 3 late
```

1. **Lines 15–17:** the three phases are empty functions that a system overrides only when it needs them.
2. **Lines 42–50:** the frame's time joins the accumulator, and each step takes one step's length away until a whole step is no longer due or the cap is reached.
3. **Lines 51–56:** at the cap, all owed steps but one step's worth are dropped.

The 35 ms frame ran three steps and kept 5 ms. The 6 ms frame joined those 5 ms, so 11 ms made one step and left 1 ms. The 10 s frame owed 1,000 steps: eight ran, 991 were dropped and one step's worth stayed.

The toy omits what makes the real scene cheap and safe. It has no lists of the systems that take part in each phase, no pause, no clocks, no destruction that waits and no news to systems before an entity dies. The next sections add them in the order the data flows.

## Declaring a system

A system is a class with up to nine functions that the scene may call, and it declares its own mode and order.

:::question
This code uses a class with :term[virtual functions]{id=virtual-function} and `override`. If those are new, read [Classes](../basics/cpp-classes.md) first.
:::

The quote below holds the two run modes and the :term[base class]{id=base-class}. Notice which functions take a time and which do not.

```cpp src="Strata/src/Strata/Scene/SceneSystem.h#L20-L62"
enum class SceneRuntimeMode : uint8_t
{
	Play,    // Full game simulation: scripts, physics, audio
	Simulate // Physics only (editor "simulate" mode); no scripts or audio
};

// A runtime subsystem attached to a scene while it is playing (physics world, script instances, audio).
// Systems are created on Scene::OnRuntimeStart in update order (SceneSystemRegistry::GetAll) and destroyed on
// OnRuntimeStop in reverse. Starting has two phases: every system's OnRuntimeStart, then every system's
// OnRuntimeStarted (both in update order), so that game code run while starting (the scripts' OnCreate, in
// OnRuntimeStarted) finds every system running.
// Per frame the scene calls OnUpdate, then OnFixedUpdate zero or more times at the fixed timestep,
// then OnLateUpdate (of the systems whose descriptor asks for them: SceneSystemDescriptor::CallsUpdate and the others);
// a paused scene calls OnPausedUpdate instead.
// React to entity/component changes through the registry's EnTT signals.
class SceneSystem
{
public:
	virtual ~SceneSystem() = default;

	virtual void OnRuntimeStart() {}
	// After every system of the scene ran OnRuntimeStart: work that uses other systems, or that should see what earlier
	// systems did here (the scripts' OnCreate runs in the scripting system's).
	virtual void OnRuntimeStarted() {}
	virtual void OnRuntimeStop() {}
	virtual void OnUpdate(Timestep) {}
	virtual void OnFixedUpdate(float) {}
	virtual void OnLateUpdate(Timestep) {}

	// Called while the scene is running when it is paused or resumed (Scene::SetPaused, e.g. the editor's pause button).
	// While paused the scene calls no update functions (except for Scene::Step), so systems that keep running on their own
	// (audio playback) halt here.
	virtual void OnPausedChanged(bool) {}
	// Called once per frame while the scene is paused (and not stepping) instead of the update functions: work whose
	// result the paused frame shows and that advances no time (the animation system poses animators that skipped their
	// poses while unseen once a renderer reports them).
	virtual void OnPausedUpdate() {}

	// Called while the scene is running, right before an entity is destroyed (descendants before their ancestors).
	// The entity is still complete and valid. Destruction requested from here is deferred; entities attached to
	// the dying hierarchy from here are announced (and destroyed) as well.
	virtual void OnEntityDestroying(const Entity&) {}
};
```

1. **Lines 22–23:** `Play` runs the whole game, and `Simulate` is the editor's mode without scripts or audio. The comment says physics only, but the World system runs there too.
2. **Lines 40–44:** starting has two phases, and the stop function is called once for each system.
3. **Lines 45–47:** the three per-frame functions are `OnUpdate` once per frame, `OnFixedUpdate` zero or more times at the fixed step, and `OnLateUpdate` once after the steps.
4. **Lines 52–56:** a paused scene calls `OnPausedUpdate` instead of the three, and `OnPausedChanged` tells systems about the change.
5. **Line 61:** `OnEntityDestroying` runs before an entity goes, with the entity still valid.

The **update phases** are those three functions together: the points in one frame at which a system may do its work. `OnUpdate` suits work that follows the frame's time, such as reading input. `OnFixedUpdate` suits work that must advance in equal steps, such as physics. `OnLateUpdate` suits work that wants the result of the steps, such as audio following the moved sources.

A system takes part in a phase only if it overrides that function. Next is what the system declares about itself.

```cpp src="Strata/src/Strata/Scene/SceneSystem.h#L64-L102"
struct SceneSystemDescriptor
{
	std::string Name;
	bool RunsInSimulateMode = false;
	std::function<Scope<SceneSystem>(Scene&)> Create;
	// Update order: the system runs after the systems named in After and before those named in Before (names of
	// registered systems). Registration order decides the rest as far as the constraints allow (see
	// SceneSystemRegistry::GetAll): a system that no constraint involves runs after every system registered before it.
	//
	// Hard constraints (After, Before) name systems that must be registered: a system of the same module, or of a module
	// this one cannot work without; a registration that names an absent one is refused. Soft constraints
	// (AfterIfPresent, BeforeIfPresent) order the system against another module's systems when that module is part of
	// the build: they are ignored while the named system is not registered, apply as soon as it is (the order is
	// recomputed over every registered system), refuse cycles like hard ones, and never keep the named system from being
	// unregistered. Constraints toward another module's system are soft, so that the engine runs without that module.
	std::vector<std::string> After;
	std::vector<std::string> Before;
	std::vector<std::string> AfterIfPresent;
	std::vector<std::string> BeforeIfPresent;
	// entt::type_id of the class Create makes (set by MakeSceneSystemDescriptor), by which Scene::GetSystem finds the
	// running system; 0 for a system that is not looked up by type.
	entt::id_type Type = 0;
	// The FrameProfiler stage the system's start and update callbacks are timed in (e.g. "Scene.Physics"); empty: the
	// system is not timed on its own (its time counts for the stage around the scene's update).
	std::string ProfileStage;
	// The per-frame callbacks the scene calls: all of them by default; MakeSceneSystemDescriptor keeps only those the
	// class overrides, so a system costs nothing in the phases it takes no part in (a scene's idle play frame is the
	// sum of these calls).
	bool CallsUpdate = true;
	bool CallsFixedUpdate = true;
	bool CallsLateUpdate = true;
	bool CallsPausedUpdate = true;
	// Work on a loaded scene before it first runs, while its load is Preparing (SceneLoadOptions::PrepareSystems): called
	// once per frame with the frame's budget until it returns true; the systems' hooks run in update order, one after the
	// other (a hook starts once the hooks before it returned true), before the load's own Prepare. The system keeps what
	// it prepared in the scene (Scene::SetPreparedState) and takes it in OnRuntimeStart; a scene that starts without
	// preparation (a play copy, tools) is built there as before. Empty: nothing to prepare.
	std::function<bool(Scene&, SceneWorkBudget&)> PrepareLoadedScene;
};
```

1. **Line 67:** a system runs in `Simulate` mode only when this flag is set; Physics and World set it, and the other four built-ins do not.
2. **Lines 79–82:** the four lists of names are the order constraints, taught in the next section.
3. **Line 85:** the type that `GetSystem<T>` finds.
4. **Line 88:** the profiler stage that times the system's start and update functions.
5. **Lines 92–101:** the `Calls*` flags choose the phases the scene calls, and `PrepareLoadedScene` lets a system work on a loaded scene before it first runs, which [Sub-scenes](../world/sub-scenes.md) teaches.

The flags are on by default, so a description written by hand calls everything. `MakeSceneSystemDescriptor` sets them from what the class overrides.

```cpp src="Strata/src/Strata/Scene/SceneSystem.h#L110-L138"
	template<typename T>
	constexpr bool c_OverridesUpdate = !std::is_same_v<decltype(&T::OnUpdate), void (SceneSystem::*)(Timestep)>;
	template<typename T>
	constexpr bool c_OverridesFixedUpdate = !std::is_same_v<decltype(&T::OnFixedUpdate), void (SceneSystem::*)(float)>;
	template<typename T>
	constexpr bool c_OverridesLateUpdate = !std::is_same_v<decltype(&T::OnLateUpdate), void (SceneSystem::*)(Timestep)>;
	template<typename T>
	constexpr bool c_OverridesPausedUpdate = !std::is_same_v<decltype(&T::OnPausedUpdate), void (SceneSystem::*)()>;

}

// A descriptor for a system of class T, which Scene::GetSystem<T> finds while the scene runs. The scene calls only the
// per-frame callbacks T overrides.
template<typename T>
SceneSystemDescriptor MakeSceneSystemDescriptor(std::string name, bool runsInSimulateMode, std::function<Scope<T>(Scene&)> factory)
{
	static_assert(std::is_base_of_v<SceneSystem, T>, "Scene systems derive from SceneSystem");
	SceneSystemDescriptor descriptor;
	descriptor.Name = std::move(name);
	descriptor.RunsInSimulateMode = runsInSimulateMode;
	if (factory)
		descriptor.Create = [factory = std::move(factory)](Scene& scene) -> Scope<SceneSystem> { return factory(scene); };
	descriptor.Type = entt::type_id<T>().hash();
	descriptor.CallsUpdate = Detail::c_OverridesUpdate<T>;
	descriptor.CallsFixedUpdate = Detail::c_OverridesFixedUpdate<T>;
	descriptor.CallsLateUpdate = Detail::c_OverridesLateUpdate<T>;
	descriptor.CallsPausedUpdate = Detail::c_OverridesPausedUpdate<T>;
	return descriptor;
}
```

1. **Line 111:** `&T::OnUpdate` names a member of `SceneSystem` when `T` does not override it, and a member of `T` (or of a base between them) when it does. The two types differ, and the :term[compiler]{id=compiler} can tell.
2. **Line 126:** a class that is no scene system fails to compile.
3. **Line 132:** the class's type is stored for `GetSystem<T>`.
4. **Lines 133–136:** each flag becomes true only for a function the class overrides.

The comparison uses types, not pointers, because the language leaves the comparison of pointers to virtual :term[member functions]{id=member-function} open. That is also why a system must declare its overrides public: the expression `&T::OnUpdate` must be visible to the helper.

:::why[Why the scene calls only what a system overrides]
The perf budget of an idle play frame in a scene of a million entities is under a tenth of a microsecond (the metric `IdlePlayFrame1M` of the `Perf.Scene` suite). The built-ins cost nine calls in it: the game's user interface (UI), Animation and World in `OnUpdate`, Scripting in all three phases, Physics in `OnUpdate` and `OnFixedUpdate`, and Audio in `OnLateUpdate`. The price is that every system must declare its overrides public and use the helper; a hand-built description pays for all four phases.
:::

## Ordering the systems

The registry stores the descriptions in registration order and keeps a second list in update order, which it builds again on every registration. A **hard** constraint, written in `After` or `Before`, names a system that must be registered; a registration that names an absent one is refused.

A **soft constraint**, written in `AfterIfPresent` or `BeforeIfPresent`, orders the system against another module's system only while that system is registered. It is ignored while the named system is absent, applies as soon as that system registers, and refuses cycles like a hard one. A soft constraint never stops the named system from being removed.

Each constraint becomes an arrow from the system that runs first to the one that runs later. The order must follow all arrows and, between systems with no arrow, registration order. The function that builds it uses a queue and a loop.

```cpp src="Strata/src/Strata/Scene/SceneSystem.cpp#L122-L157"
	// Systems whose successors are all placed, the latest registered on top.
	std::vector<uint32_t> remainingSuccessors(registered.size());
	std::priority_queue<size_t> ready;
	for (size_t index = 0; index < registered.size(); index++)
	{
		remainingSuccessors[index] = static_cast<uint32_t>(successors[index].size());
		if (remainingSuccessors[index] == 0)
			ready.push(index);
	}

	std::vector<size_t> placedFromBack;
	placedFromBack.reserve(registered.size());
	while (!ready.empty())
	{
		const size_t index = ready.top();
		ready.pop();
		placedFromBack.push_back(index);
		for (size_t predecessor : predecessors[index])
		{
			if (--remainingSuccessors[predecessor] == 0)
				ready.push(predecessor);
		}
	}

	if (placedFromBack.size() != registered.size())
	{
		outError = fmt::format("the update order of the scene systems has a cycle: {}", DescribeCycle(registered, successors, remainingSuccessors));
		return false;
	}
	std::vector<SceneSystemDescriptor> ordered;
	ordered.reserve(registered.size());
	for (auto it = placedFromBack.rbegin(); it != placedFromBack.rend(); ++it)
		ordered.push_back(registered[*it]);
	outOrdered = std::move(ordered);
	return true;
}
```

1. **Lines 123–130:** each system counts its successors; a system with none is ready to be placed.
2. **Line 124:** the queue is a max-heap on the registration index, so the system registered last comes out first.
3. **Lines 136–143:** the chosen system goes at the back of the placed list, and each system that waited for it loses one successor.
4. **Lines 146–150:** if some systems never become ready, they wait on each other, and the error names the cycle by walking successors.
5. **Lines 153–154:** the list was built from the back, so it is reversed.

:::example[Four systems, ordered by hand]
Register Scripting, Physics (after Scripting and after `Wind`), `CameraFollow` and `Wind`, in that order. Physics and `CameraFollow` have no successors, so both are ready, and the queue takes `CameraFollow`, the larger index. It goes last, and Physics next.

Scripting and `Wind` are now ready, and `Wind` (index 3) goes before Scripting. The reversed list is Scripting, `Wind`, Physics, `CameraFollow`, as the toy printed.
:::

A system with no constraint therefore lands after every system registered before it. A later system moves ahead of an earlier one only when it must run before something that is ahead of that one. Taking the first registered ready system from the front would let `CameraFollow` run before `Wind` and Physics.

Registration refuses a description without a name or factory, a class registered under another name and a hard constraint naming an absent system. It also refuses a system that names itself, a cycle and any change while a scene runs. A refusal logs an error that names the systems and leaves the registry as it was. A cycle prints as `TestA -> TestB -> TestC -> TestA`. Registering a name again replaces the old entry, which then counts as registered last.

The composition root logs the result once the modules are registered. Notice the two strings that the code builds before the log call.

```cpp src="Strata/src/Strata/Engine/BuiltinModules.cpp#L163-L173"
std::string order;
for (const SceneSystemDescriptor& descriptor : SceneSystemRegistry::GetAll())
	order += (order.empty() ? "" : ", ") + descriptor.Name;
std::string absent;
for (const std::string& constraint : SceneSystemRegistry::GetAbsentSoftConstraints())
	absent += (absent.empty() ? "" : ", ") + constraint;
std::string modules;
for (const std::string& name : s_RegisteredModules)
	modules += (modules.empty() ? "" : ", ") + name;
ST_CORE_INFO("Engine modules: {}. Scene systems update in the order {}{}", modules, order.empty() ? std::string("(none)") : order,
	absent.empty() ? std::string() : fmt::format("; soft constraints naming absent systems: {}", absent));
```

1. **Lines 163–168:** the update order and the soft constraints that name absent systems, each written as `<system> after <name>` or `<system> before <name>`.
2. **Lines 172–173:** one information line holds both, so a missing module shows in the log.

To learn where a new system runs, read the information line that starts with `Engine modules` in the log. After the words `Scene systems update in the order` it lists every system. When a soft constraint of yours names a system that is not built, the line ends with `soft constraints naming absent systems` and your entry.

## Starting and stopping

A scene that plays is not the edited scene but a copy of it, so play never changes what you edit. `Scene::Copy` keeps the same EnTT identifiers and copies every component storage whole, through the copy function that each component's registration supplies. It does that on the job system's threads, the largest storages first. The map from identifiers to entities, the hierarchy links and the caches are copied as they are.

The end of the function shows what must come last.

```cpp src="Strata/src/Strata/Scene/Scene.cpp#L358-L378"
// The hierarchy links and caches hold as they are: the same identifiers.
destination->m_RootEntities = source->m_RootEntities;
destination->m_FirstRoot = source->m_FirstRoot;
destination->m_LastRoot = source->m_LastRoot;
destination->m_RootIndicesValid = source->m_RootIndicesValid;
// What is stale in the source is stale in the copy (the nodes' dirty flags came with them), and the nodes' memo of the
// transform pass is the source's, so the copy's passes continue its numbering. A snapshot has no world transforms.
if (!options.SerializedOnly)
{
	destination->m_DirtyTransforms = source->m_DirtyTransforms;
	destination->m_TransformPass = source->m_TransformPass;
}
destination->m_HierarchyVersion++;
destination->ConnectSignals();
// The modules' context data of a complete copy (a render scene's clone); a snapshot to save needs none.
if (!options.SerializedOnly)
{
	for (const SceneContextCopier copier : GetContextCopiers())
		copier(*source, *destination);
}
return destination;
```

1. **Lines 359–362:** the root list and its indexes are the source's, because the entities have the same identifiers.
2. **Lines 370–371:** signal handlers connect only now; nothing listens to a new registry while it is filled, so the storages can be copied at the same time.
3. **Lines 373–377:** the context copy functions of the modules run; the :term[renderer]{id=renderer} registers one that clones the render scene.

The option `SceneCopyOptions::SerializedOnly` makes the snapshot that a background save writes. It copies what a document holds, also the components that play copies omit, and no world transforms, and it runs no context copy function. Such a copy is only read, never played. `Scene::RegisterContextCopier` works only while the composition root registers modules.

`OnRuntimeStart` then resets the clocks (pause, steps, accumulator, dropped steps, time, frame count), clears the interpolation set, brings the world transforms up to date and creates the systems in update order.

```cpp src="Strata/src/Strata/Scene/Scene.cpp#L2111-L2139"
	// In update order. Systems may look up the ones created before them (GetSystem) while they are constructed.
	for (const SceneSystemDescriptor& descriptor : SceneSystemRegistry::GetAll())
	{
		if (mode != SceneRuntimeMode::Play && !descriptor.RunsInSimulateMode)
			continue;
		Scope<SceneSystem>& system = m_Systems.emplace_back(descriptor.Create(*this));
		const FrameStageID stage = descriptor.ProfileStage.empty() ? c_InvalidFrameStage : FrameProfiler::Get().RegisterStage(descriptor.ProfileStage);
		m_SystemStages.push_back(stage);
		if (descriptor.Type != 0)
			m_SystemsByType[descriptor.Type] = system.get();
		// A frame calls only the callbacks a system takes part in.
		if (descriptor.CallsUpdate)
			m_UpdateCalls.push_back(SystemCall { system.get(), stage });
		if (descriptor.CallsFixedUpdate)
			m_FixedUpdateCalls.push_back(SystemCall { system.get(), stage });
		if (descriptor.CallsLateUpdate)
			m_LateUpdateCalls.push_back(SystemCall { system.get(), stage });
		if (descriptor.CallsPausedUpdate)
			m_PausedUpdateCalls.push_back(SystemCall { system.get(), stage });
	}

	// Systems may create or destroy entities while starting (e.g. scripts in OnCreate).
	m_IsUpdating = true;
	ForEachSystem(m_Systems, m_SystemStages, [](SceneSystem& system) { system.OnRuntimeStart(); });
	ForEachSystem(m_Systems, m_SystemStages, [](SceneSystem& system) { system.OnRuntimeStarted(); });
	m_IsUpdating = false;
	FlushPendingDestroys();
	UpdateWorldTransforms();
}
```

1. **Lines 2114–2115:** in `Simulate` mode a system without `RunsInSimulateMode` is skipped.
2. **Lines 2116–2120:** the factory runs in update order, so a system can find the ones made before it with `GetSystem`.
3. **Lines 2122–2129:** four lists collect the systems that take part in each phase; the frame walks these lists only.
4. **Lines 2133–2137:** every `OnRuntimeStart` runs, then every `OnRuntimeStarted`, with `m_IsUpdating` set so that destruction requested here waits.

The two phases exist for scripts. The scripting system calls the scripts' `OnCreate` in `OnRuntimeStarted`, when every other system, physics included, is already running.

`OnRuntimeStop` is the mirror image. Sub-scenes being unloaded go first, so that their scripts still get `OnDestroy`. Then the systems stop in reverse order, the four lists are cleared, the systems are destroyed in reverse order, and queued destruction is flushed. A system that is being destroyed still finds the systems made before it.

```mermaid caption="The life of a running scene: start in two phases, running with paused and stepping states, and stop in reverse order." alt="A scene that does not run moves to starting when play begins. Starting moves to running after every start function and then every started function have run. Running holds three states: free running, paused and stepping. Stop leaves running, calls the systems in reverse order and returns to the scene that does not run."
stateDiagram-v2
    [*] --> NotRunning
    NotRunning --> Starting: OnRuntimeStart(mode)
    Starting --> Running: all Start, then all Started
    state Running {
        [*] --> Free
        Free --> Paused: SetPaused(true)
        Paused --> Free: SetPaused(false)
        Paused --> Stepping: Step(n)
        Stepping --> Paused: n steps done
    }
    Running --> NotRunning: OnRuntimeStop (reverse order)
```

## One runtime frame

Frames are where the order pays off. The editor or the runtime calls `OnUpdateRuntime` once per frame with the frame's time. The first lines run the sub-scene slices, so that the systems see their entities in this very update, and the function returns early when the scene does not run. A paused scene without a due step brings the world transforms up to date, calls `OnPausedUpdate` on the systems that asked, flushes destruction and returns.

```mermaid caption="One runtime frame in order: sub-scene slices, world transforms, the update, the fixed steps in a loop, the late update, the flush of destruction and the last update of world transforms." alt="A column of steps. Sub-scenes come first, then world transforms, then the update function on every system that takes part. Next is a loop that calls the fixed update function while a whole step is due and the cap is not reached. Then come the late update function, the flush of queued destruction and world transforms again. Physics takes part in the update and the steps, and Audio in the late update."
flowchart TD
    A["Sub-scene slices (loads and unloads)"] --> B["World transforms"]
    B --> C["OnUpdate: UI, Scripting, Animation, World, Physics"]
    C --> D{"accumulator at least one step, and fewer than the cap?"}
    D -- yes --> E["OnFixedUpdate: Scripting, Physics"]
    E --> D
    D -- no --> F["OnLateUpdate: Scripting, Audio"]
    F --> G["Flush queued destruction"]
    G --> H["World transforms; Debug check"]
```

The first part of the frame fixes the time of the frame.

```cpp src="Strata/src/Strata/Scene/Scene.cpp#L2239-L2262"
const float fixedTimestep = GetFixedTimestep();
const float deltaTime = stepping ? fixedTimestep : static_cast<float>(timestep) * m_TimeScale;
const bool interpolating = IsInterpolating();
// Stepped frames draw exactly; a new rate (the project's FixedRate, scene.setSettings) leaves poses of the old one.
if (stepping || (interpolating && m_InterpolationTimestep != 0.0f && fixedTimestep != m_InterpolationTimestep))
	ClearInterpolation();
// Unscaled time goes on at time scale 0 (a pause menu's fades): the frame's timestep before the time scale, the fixed
// step while stepping.
m_UnscaledDeltaTime = stepping ? fixedTimestep : std::max(static_cast<float>(timestep), 0.0f);
m_UnscaledTime += m_UnscaledDeltaTime;

m_IsUpdating = true;
UpdateWorldTransforms();

ForEachSystemCall(m_UpdateCalls, [deltaTime](SceneSystem& system) { system.OnUpdate(Timestep(deltaTime)); });

if (stepping)
{
	ForEachSystemCall(m_FixedUpdateCalls, [fixedTimestep](SceneSystem& system) { system.OnFixedUpdate(fixedTimestep); });
	m_StepFrames--;
	m_FixedSteps++;
}
else
{
```

1. **Line 2240:** the frame's time is the real time times the :term[time scale]{id=time-scale}; while stepping it is exactly one fixed step.
2. **Lines 2247–2248:** :term[unscaled time]{id=unscaled-time} ignores the scale, so a pause menu can fade at time scale 0.
3. **Lines 2250–2253:** `m_IsUpdating` is set, world transforms update, and every system in the update list gets `OnUpdate`.
4. **Lines 2255–2260:** a stepping frame, which happens while paused, runs exactly one fixed step and counts it.

The accumulator is the idea that [Time](../core/time.md) teaches; this is its code.

```cpp src="Strata/src/Strata/Scene/Scene.cpp#L2267-L2295"
m_FixedTimeAccumulator += deltaTime;
const uint32_t maxSteps = GetMaxFixedSteps();
// The wall time one step stands for: the fixed timestep, stretched by slow motion.
const double realTimePerStep = static_cast<double>(fixedTimestep) / static_cast<double>(m_TimeScale > 0.0f ? m_TimeScale : 1.0f);
// The steps are timed only when time dilation could stop one: it is on and a second step is due (the first always
// runs). Other frames do not read the clock. (While the accumulator holds less than two steps, subtracting one
// step is exact and leaves less than a step, so no second step can run.)
std::optional<std::chrono::steady_clock::time_point> stepsStart;
if (m_TimeDilation && maxSteps > 1 && m_FixedTimeAccumulator >= 2.0f * fixedTimestep)
	stepsStart = std::chrono::steady_clock::now();
uint32_t steps = 0;
bool dilated = false;
m_InFixedSteps = interpolating;
while (m_FixedTimeAccumulator >= fixedTimestep && steps < maxSteps)
{
	if (stepsStart && steps > 0)
	{
		const double elapsed = std::chrono::duration<double>(std::chrono::steady_clock::now() - *stepsStart).count();
		if (elapsed >= realTimePerStep * steps)
		{
			dilated = true;
			break;
		}
	}
	ForEachSystemCall(m_FixedUpdateCalls, [fixedTimestep](SceneSystem& system) { system.OnFixedUpdate(fixedTimestep); });
	m_FixedTimeAccumulator -= fixedTimestep;
	steps++;
	m_FixedSteps++;
}
```

1. **Lines 2267–2268:** the frame's time joins the accumulator, and the cap is read through `GetMaxFixedSteps`.
2. **Lines 2274–2276:** the clock is read only when :term[time dilation]{id=time-dilation} could stop a step; other frames never read it.
3. **Lines 2280–2290:** the loop runs while a whole step is due and the cap is not reached; with time dilation it stops once the steps took longer in real time than they simulated.
4. **Lines 2291–2294:** each pass calls `OnFixedUpdate` on every system in the fixed list, takes one step from the accumulator and counts it.

What the loop does not run, the next lines drop.

```cpp src="Strata/src/Strata/Scene/Scene.cpp#L2297-L2331"
	if (dilated)
	{
		// Behind real time: the steps still due are dropped, the simulation runs slower than the clock.
		const float dropped = std::floor(m_FixedTimeAccumulator / fixedTimestep);
		m_DroppedFixedSteps += static_cast<uint64_t>(dropped);
		// Rounding of the quotient must not leave a negative remainder.
		m_FixedTimeAccumulator = std::max(0.0f, m_FixedTimeAccumulator - dropped * fixedTimestep);
	}
	else if (steps == maxSteps && m_FixedTimeAccumulator > fixedTimestep)
	{
		// Too far behind (e.g. after a hitch): drop the backlog instead of simulating it all next frame.
		m_DroppedFixedSteps += static_cast<uint64_t>(std::floor((m_FixedTimeAccumulator - fixedTimestep) / fixedTimestep));
		m_FixedTimeAccumulator = fixedTimestep;
	}
	m_InFixedSteps = false;

	if (interpolating)
	{
		if (steps > 0)
			CaptureInterpolation(steps, fixedTimestep);
		// Drawn one step behind the clock: the latest step ended at T, the set holds the poses at T - n h and T, and
		// T + a - h lies 1 - (1 - a / h) / n of the way between them (Docs/DeveloperGuide.md, "Interpolation").
		const float behind = 1.0f - std::min(m_FixedTimeAccumulator / fixedTimestep, 1.0f);
		m_StepAlpha = std::clamp(1.0f - behind / static_cast<float>(m_InterpolationSteps), 0.0f, 1.0f);
	}
}

ForEachSystemCall(m_LateUpdateCalls, [deltaTime](SceneSystem& system) { system.OnLateUpdate(Timestep(deltaTime)); });

m_Time += deltaTime;
m_FrameIndex++;
m_IsUpdating = false;

FlushPendingDestroys();
UpdateWorldTransforms();
```

1. **Lines 2300–2303:** after a frame cut short by time dilation, the steps still owed are dropped and counted, and a part of a step stays in the accumulator.
2. **Lines 2305–2309:** after a frame that reached the cap, all but one step's worth of the owed steps is dropped.
3. **Lines 2313–2320:** when drawing between steps is on, the poses are captured and the step alpha is set, which [Drawing between fixed steps](../world/interpolation.md) teaches.
4. **Lines 2324–2331:** `OnLateUpdate` runs, time and the frame index grow, destruction is flushed and the world transforms are brought up to date.

:::example[The numbers of the engine's own test]
The test `Runtime update runs systems at the fixed timestep` sets the step to 0.01 s. A frame of 0.035 s runs three steps and keeps 0.005 s. A frame of 0.006 s makes 0.011 s, so one more step runs, four in all. After a pause and two single steps there are six, and a frame of 10 s runs the cap of eight and keeps one step's worth.

The slow-system test sets a step of 1/64 s. A frame of 4/64 s plus 1/256 s owes four steps. The first step takes longer than 1/64 s, so the three steps still due are dropped, and 1/256 s stays.
:::

Debug builds end the update with a check that the caches equal a full count made again. The editor's own update, `OnUpdateEditor`, is far shorter: it updates sub-scenes and world transforms and calls no system at all.

## The time the scene keeps

A scene has its own clock, and it starts at zero in `OnRuntimeStart`. `GetTime` adds the frames' scaled time, and `GetUnscaledTime` adds the time before scaling. `SetTimeScale` multiplies the time that enters the frame. At 0.5 the accumulator grows half as fast, so steps come half as often and each is still 1/60 s long. At 0 no time enters, so only a step the accumulator still holds can run, and unscaled time continues.

Pausing and stepping give the game its own time base. `SetPaused(true)` tells every system with `OnPausedChanged`. `Step(n)` asks for n single frames while paused: each calls `OnUpdate` with the fixed step as its time, runs one `OnFixedUpdate` and counts it. `GetFixedStepCount` counts the steps since the start, run on the clock or stepped. Tools count in it instead of frames, as the rule of [Time](../core/time.md) says.

The step length has two sources. `SceneSettings` holds the scene's own values, and the project's `Scene.Timing` section may override them.

```cpp src="Strata/src/Strata/Scene/Scene.cpp#L244-L251"
uint32_t Scene::GetMaxFixedSteps() const
{
	// At the project's rate the scene's own cap, chosen for its own step, does not apply: 8 steps of a 240th would drop
	// time on every frame longer than 33 ms.
	if (m_ProjectFixedRate > 0)
		return ProjectSceneTiming::GetMaxSteps(m_ProjectFixedRate);
	return std::max(1u, m_Settings.MaxFixedStepsPerFrame);
}
```

The function answers with the project's cap, and its steps come from a second small function.

```cpp src="Strata/src/Strata/Scene/ProjectSceneTiming.cpp#L118-L123"
uint32_t GetMaxSteps(uint32_t stepsPerSecond)
{
	// In 64 bits: no rate overflows the doubling.
	const uint64_t steps = (static_cast<uint64_t>(stepsPerSecond) * 2 + 14) / 15;
	return static_cast<uint32_t>(std::clamp<uint64_t>(steps, 1, c_MaxStepsLimit));
}
```

The cap at a project rate is the steps of 2/15 s, rounded up and kept between 1 and 64. The rates 30, 60, 120 and 240 give caps of 4, 8, 16 and 32, so every cap covers 133 ms of simulated time. The scene's own cap of 8 at 240 steps a second would cover only 33 ms, so a longer frame would lose time. That is why a project rate brings its own cap. The fields of `SceneSettings` are:

| Field | Default | Meaning |
| --- | --- | --- |
| `Gravity` | (0, -9.81, 0) | The pull the physics world applies, in m/s². |
| `FixedTimestep` | 1/60 s | The scene's own step; a project rate wins. |
| `MaxFixedStepsPerFrame` | 8 | The scene's own cap; a project rate wins. |
| `PhysicsCapacity` | automatic | The room of the physics world; 0 sizes it from the bodies at start. |
| `MaxEntitiesInstantiatedPerFrame` | 5000 | Entities that sub-scene loads may create in one update. |
| `MaxEntitiesDestroyedPerFrame` | 5000 | Entities that sub-scene unloads may destroy in one update. |

## Entities that die during an update

Destroying an entity destroys its whole :term[subtree]{id=subtree}. When many entities go in one call, `DestroyEntities` handles them as a batch, and when an update is running it only writes down the request.

```cpp src="Strata/src/Strata/Scene/Scene.cpp#L436-L459"
void Scene::DestroyEntities(std::span<const Entity> entities)
{
	std::vector<entt::entity> roots;
	roots.reserve(entities.size());
	for (const Entity entity : entities)
	{
		if (!entity.IsValid() || entity.GetScene() != this)
			continue;

		if (m_IsUpdating)
		{
			const UUID uuid = entity.GetUUID();
			if (m_PendingDestroySet.insert(uuid).second)
				m_PendingDestroy.push_back(uuid);
			continue;
		}
		roots.push_back(entity.GetHandle());
	}
	if (roots.empty())
		return;
	DestroyRoots(std::move(roots));
	// Systems reacting to the destruction may have requested more.
	FlushPendingDestroys();
}
```

1. **Lines 445–451:** during an update the entity's `UUID` goes into a pending list, and the entity stays complete; the list holds a `UUID`, never a handle.
2. **Lines 454–458:** outside an update the roots are destroyed now, and then requests that the systems made in reaction are flushed.

The flush at the end of a frame destroys all queued requests together, and repeats until none are left, because destruction may queue more. Before any entity goes, each system hears of it.

```cpp src="Strata/src/Strata/Scene/Scene.cpp#L573-L591"
const bool wasUpdating = m_IsUpdating;
m_IsUpdating = true;
std::unordered_set<entt::entity> notified;
bool notifiedAny = true;
while (notifiedAny && m_Registry.valid(root))
{
	notifiedAny = false;
	const std::vector<entt::entity> subtree = CollectSubtree(root);
	for (auto it = subtree.rbegin(); it != subtree.rend(); ++it)
	{
		if (!notified.insert(*it).second)
			continue;
		notifiedAny = true;
		const Entity entity(*it, this);
		for (const Scope<SceneSystem>& system : m_Systems)
			system->OnEntityDestroying(entity);
	}
}
m_IsUpdating = wasUpdating;
```

1. **Lines 573–574:** while systems react, the destruction they request is deferred too.
2. **Lines 580–588:** the walk goes from the last descendant back to the root, so children are announced before their parents. The subtree is collected again afterwards, so entities attached in the meantime are announced as well.

Scripts use this to run `OnDestroy` with the entity complete: its components and children are all still there. The engine's test `Systems see entities before they are destroyed` shows the order `Grandchild`, `Child`, `Root`, then a `LateChild` that a system attached while it was told, then another root. A batch also compacts each list of siblings once instead of once for each entity, which matters when you delete many entities of a long list.

## Services between modules

Scripts need physics, audio needs the transforms that physics wrote, and the world streamer needs the physics capacity. Yet the layer rules forbid a module to include a module beside it. A **scene service** is an interface, defined in the Scene layer, that a running system offers to the other systems of its scene. The offering module implements it, and the using module sees only the interface.

```cpp src="Strata/src/Strata/Scene/Scene.cpp#L2182-L2197"
bool Scene::RegisterServiceProvider(entt::id_type type, std::string_view typeName, void* provider)
{
	ST_CORE_ASSERT(provider, "Scene::RegisterService: no provider");
	auto [it, inserted] = m_Services.try_emplace(type, provider);
	if (inserted || it->second == provider)
		return true;
	ST_CORE_ERROR("Scene '{}': the service {} is already provided by another system; the second provider is ignored", m_Name, typeName);
	return false;
}

void Scene::UnregisterServiceProvider(entt::id_type type, const void* provider)
{
	auto it = m_Services.find(type);
	if (it != m_Services.end() && it->second == provider)
		m_Services.erase(it);
}
```

1. **Lines 2185–2189:** a scene has at most one provider for each interface, found by the interface's type; a second one logs an error and is ignored.
2. **Lines 2192–2196:** only the provider can remove its entry.

A system registers each service it offers in its :term[constructor]{id=constructor} and removes it in its :term[destructor]{id=destructor}. Whoever needs one asks `GetService<T>()` and gets null when no running system offers it: the module is not built, or its system does not run in this mode. A script host therefore asks physics through `IPhysicsQueries` and never includes `PhysicsSystem`. The physics system offers seven.

```cpp src="Strata/src/Strata/Physics/PhysicsSystem.cpp#L61-L67"
m_Scene.RegisterService<ICollisionEventSource>(*this);
m_Scene.RegisterService<IBodyMotionQuery>(*this);
m_Scene.RegisterService<IBodyControl>(*this);
m_Scene.RegisterService<IPhysicsQueries>(*this);
m_Scene.RegisterService<ICharacterControl>(*this);
m_Scene.RegisterService<IPhysicsCapacity>(*this);
m_Scene.RegisterService<IPhysicsDiagnostics>(*this);
```

The comment at the top of `Strata/src/Strata/Scene/SceneServices.h` names six services for physics, and the constructor registers seven: `IPhysicsDiagnostics` is the one the comment omits. The code wins. This table lists every scene service of the :term[header]{id=header} and its provider; what each interface does belongs to its module's page.

| Interface | Provider | Used for |
| --- | --- | --- |
| `ICollisionEventSource` | Physics | contact begin and end events |
| `IBodyMotionQuery` | Physics | reading the motion of bodies |
| `IBodyControl` | Physics | setting velocities, forces and impulses |
| `IPhysicsQueries` | Physics | rays and other spatial queries |
| `ICharacterControl` | Physics | character controllers |
| `IPhysicsCapacity` | Physics | the room of the physics world |
| `IPhysicsDiagnostics` | Physics | numbers for logs and panels, in :term[constant time]{id=constant-time} |
| `IAudioPlayback` | Audio | the sounds of a playing scene |
| `ISkinningPoses` | Animation (and the editor's pose preview) | poses that the renderer reads |
| `IAnimatorControl` | Animation | setting animator parameters and states |
| `IAnimationEventSource` | Animation | animation events |
| `IWorldStreaming` | World | prefetching and layers of a streamed world |
| `IUIEvents` | Game UI | the events of the frame's widgets |
| `IUIControl` | Game UI | reading and setting widget values |

A scene service belongs to one scene. `IAudioOutput`, defined in the same header, belongs to the whole process: it is an engine service, which [Engine modules](../core/engine-modules.md) teaches. A scene in `Simulate` mode has physics but no audio, so `GetService<IAudioPlayback>()` is null there.

```mermaid caption="Scene services: each module's system offers interfaces that sit in the Scene layer, and other modules use the interfaces and never the other module." alt="A box for the Scene layer's interfaces stands in the middle. The Physics, Audio, Animation, World and Game UI systems point to it with the word offers. The Scripting system and the renderer point to it with the word uses. There is no arrow between any two modules."
flowchart TD
    I["Scene layer: SceneServices.h interfaces"]
    PH["Physics system"] -- offers --> I
    AU["Audio system"] -- offers --> I
    AN["Animation system"] -- offers --> I
    WO["World system"] -- offers --> I
    UI["Game UI system"] -- offers --> I
    SC["Scripting system"] -- uses --> I
    RE["Renderer"] -- uses --> I
```

:::why[Why services instead of `GetSystem`]
`GetSystem<PhysicsSystem>()` needs the class's header, so scripting would include the physics module and fail the layer check. A service costs one interface in the lower layer and a null check in the user. It gains builds without a module, and tests with a fake provider.
:::

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| A hard-coded order in the main loop | Small engines and many game loops | The simplest code, with all calls in one place | A game cannot insert a step, and every module is included by the loop |
| Priority numbers | Godot's node process priority; Unity's script execution order | Order set by one number, no graph to sort | Numbers that mean nothing alone and can collide; no reason recorded |
| A graph that runs systems in parallel by the data they touch | Bevy's system graph | More work done at once on many cores | The rule that one thread owns the scene and everything in it |
| Systems that only react to events | Many editors and user interface libraries | No order at all to maintain | Results that depend on the order of delivery; hard to replay |
| Building the order from the front | The textbook form of the sort | A slightly shorter loop | Free systems that overtake earlier ones |

Strata keeps named constraints with soft links to other modules, because the engine must run with any mix of its modules and the same registration must give the same order each time. The statements about other engines come from their public documentation, listed in Further reading.

## How it is tested

The suite `Scene.Systems` in `StrataTests/src/Scene/SceneSystemTests.cpp` checks the registry. The test `The built-in systems update in the order UI, Scripting, Animation, World, Physics, Audio` checks the six names, their soft constraints and their stages. The test `A system moves ahead of earlier registered ones only as far as its constraints require` registers `CameraFollow`, `Wind` and `EarlyInput` and checks the order. A third, `A cycle or an unknown name is refused with the systems named, and the registry stays unchanged`, checks the errors, and `The registry refuses changes while a scene runs` checks the third rule of the contract.

The test `A frame calls only the per-frame callbacks a system takes part in` checks the `Calls*` flags for a class that overrides one function, for a :term[derived class]{id=derived-class} and for a description built by hand. The test `Soft constraints order the systems that are registered and ignore the others` checks `GetAbsentSoftConstraints`.

The suite `Scene.Services` in `SceneServicesTests.cpp` checks one provider per interface and the built-in providers in both modes. The suite `Scene` in `SceneTests.cpp` holds the accumulator numbers, time dilation and the two tests on destruction, and `Scene.Timing` in `SceneTimingTests.cpp` checks the project's rate. Run them directly, for example:

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=Scene.Systems
build/windows/bin/Debug/StrataTests.exe --test-suite=Scene.Services
build/windows/bin/Debug/StrataTests.exe --test-suite=Scene --test-case="Runtime update runs systems*"
```

Each command runs without a :term[graphics card]{id=gpu}. The perf metric `IdlePlayFrame1M` of the `Perf.Scene` suite, built for Release and :term[Dist]{id=dist}, guards the cost of an idle play frame.

## Changing it safely

To add a system, write the class, build its description with `MakeSceneSystemDescriptor<T>` and register it in your module's registration function, which only the composition root calls. Give every constraint toward another module's system as soft. Then read the log line of the update order and check that your system stands where you meant. A game or a test passes its registration in `ModuleRegistrationOptions::Extra`.

Four checks come before a change merges:

- A new system overrides only the functions it needs and declares them public.
- A system that offers a service registers it in its constructor and removes it in its destructor.
- No system keeps an `Entity` across a frame; it keeps a `UUID`.
- The step is read with `GetFixedTimestep`, never from `GetSettings()`.

Changing `ComputeUpdateOrder` changes a contract: run `Scene.Systems` and read the `CameraFollow` test before any other.

## What went wrong before

The registry once built the order from the front, taking the earliest registered ready system first. A game registered `CameraFollow` with no constraint and then `Wind` before Physics. The order became Scripting, `CameraFollow`, `Wind`, Physics and Audio, so a camera following a rigid body lagged a frame because an unrelated system was registered. Commit `58f6ccad` builds the order from the back and adds the test case with `CameraFollow`, `Wind` and `EarlyInput`, which fails with the old algorithm.

:::history
Before that commit the documented contract already said that registration order decides between systems with no constraint; the old code did not keep it. The fix changed the code, not the rule.
:::

## Summary

- A game that plays registers scene systems; the scene calls them in a :term[topological order]{id=topological-order-basics} of their hard and soft constraints, with registration order deciding where no constraint does.
- A frame calls the update, then the fixed steps from the accumulator, then the late update, then flushes destruction. The cap drops the owed steps, and time dilation stops steps that cannot match the clock. Only systems that override a function are called in its phase.
- Destruction during an update is queued until the frame ends, and every system hears of a dying entity first, descendants before ancestors.
- A scene service is an interface in the Scene layer that one system offers and others find with `GetService`, null when absent, so modules never include each other.
- A system registered with soft constraints runs where the log line of the update order says, and a project's fixed rate overrides the scene's step and cap.

## Check yourself

1. Register four systems in this order: A, B (after A), C (no constraint) and D (before B). What is the update order? (a) A, D, B, C. (b) A, C, D, B. (c) A, B, C, D.

   :::answer{tests="placement"}
   Option (a). From the back, B and C have no successors; C is registered last and goes last, then B, then D and A. Option (b) is the order from the front, where C overtakes D and B. Option (c) ignores that D must run before B.
   :::

2. The step is 10 ms, the cap is 8, the accumulator holds 3 ms and the frame lasts 200 ms. How many steps run, how many are dropped and what does the accumulator hold afterwards?

   :::answer{tests="steps"}
   The accumulator becomes 203 ms. Eight steps run and leave 123 ms. That is more than one step, so $\lfloor (123 - 10) / 10 \rfloor = 11$ steps are dropped, and one step's worth, 10 ms, stays. The code sets the accumulator to one step, so the last 3 ms go without being counted as a step.
   :::

3. A system overrides only `OnLateUpdate`, and a scene is paused with no step due. Which function does the scene call on that system? (a) `OnPausedUpdate`. (b) `OnLateUpdate`. (c) None.

   :::answer{tests="frame"}
   Option (c). The description built by `MakeSceneSystemDescriptor` has `CallsLateUpdate` set and the other three flags off, and a paused frame walks the paused list, which does not hold this system. Option (b) would run while the scene plays, and option (a) needs an override of `OnPausedUpdate`.
   :::

4. A script destroys an enemy in `OnUpdate`, and Physics reads that enemy in `OnFixedUpdate` of the same frame. What does physics find, and when does the enemy go?

   :::answer{tests="lifetime"}
   Physics finds the enemy complete, because destruction waits for the frame's end. After `OnLateUpdate` the scene flushes: every system gets `OnEntityDestroying` for the enemy's subtree, descendants first, and only then the entities are destroyed.
   :::

5. Which value does `GetService<IAudioPlayback>()` return in a scene started in `Simulate` mode, and why is that no error?

   :::answer{tests="services"}
   The call returns null. The Audio system's description does not set `RunsInSimulateMode`, so no Audio system exists in that scene and nothing offers the service. Code that uses a service tests for null, so a missing module or mode costs nothing.
   :::

## Exercises

1. **Basic.** Write a `Spinner` system that rotates the entities with a `SpinComponent` in `OnFixedUpdate`, ordered after Scripting and before Physics with soft constraints. Predict its place in the update order, and which of the four phases the scene calls on it.

   :::answer[Worked solution]{tests="placement,frame"}
   The class overrides only `OnFixedUpdate`. In it, a loop over `GetAllEntitiesWith<TransformComponent, SpinComponent>()` changes the rotation through `registry.patch<TransformComponent>`, which signals the change. The registration is:

   ```cpp pseudocode
   SceneSystemDescriptor descriptor = MakeSceneSystemDescriptor<SpinnerSystem>("Spinner", false, [](Scene& scene) { return CreateScope<SpinnerSystem>(scene); });
   descriptor.AfterIfPresent = { "Scripting" };
   descriptor.BeforeIfPresent = { "Physics" };
   const bool registered = SceneSystemRegistry::Register(std::move(descriptor));
   ```

   `Spinner` is registered last, but it must run before Physics, so it moves ahead of Physics and stands after World: `GetAll()` lists UI, Scripting, Animation, World, `Spinner`, Physics, Audio. `CallsFixedUpdate` is true, and `CallsUpdate`, `CallsLateUpdate` and `CallsPausedUpdate` are false, so it adds one call to an idle frame.
   :::

2. **Medium.** Trace it yourself. Put a breakpoint in the `Spinner`'s `OnFixedUpdate` and follow the call stack toward the loop that calls it. Find where that loop is, and which list it walks.

   :::answer[Worked solution]{tests="frame"}
   The caller is `ForEachSystemCall` in `Strata/src/Strata/Scene/Scene.cpp`, called from `Scene::OnUpdateRuntime` inside the accumulator loop, near line 2291, with the list `m_FixedUpdateCalls`. `Scene::OnRuntimeStart` fills that list near line 2124 for each system whose description has `CallsFixedUpdate` set. `MakeSceneSystemDescriptor` in `Strata/src/Strata/Scene/SceneSystem.h` sets the flag from `c_OverridesFixedUpdate<T>`. A system that overrides no `OnUpdate` is therefore never in `m_UpdateCalls`.
   :::

3. **Medium.** Let a `Wind` system offer a scene service `IWindQuery` and let `Spinner` use it, so that `Spinner` spins faster in wind and still works without `Wind`.

   :::answer[Worked solution]{tests="services,placement"}
   Put the interface in a header that both can include, in a lower layer. `Wind` registers in its constructor and removes in its destructor; `Spinner` asks in each fixed step:

   ```cpp pseudocode
   WindSystem::WindSystem(Scene& scene) : m_Scene(scene) { m_Scene.RegisterService<IWindQuery>(*this); }
   WindSystem::~WindSystem() { m_Scene.UnregisterService<IWindQuery>(*this); }
   const IWindQuery* wind = m_Scene.GetService<IWindQuery>();
   const float strength = wind ? wind->GetStrength() : 0.0f;
   ```

   Without `Wind` registered, the scene has no provider and the call returns null, so `strength` is zero. Give `Spinner` a soft constraint to run after `Wind`, so that it reads this frame's wind.
   :::

4. **Hard.** Build the order from the front for the engine's `CameraFollow` test in a separate program, and show that it fails the expected order. Then say how you would break the engine's test the same way.

   :::answer[Worked solution]{tests="placement" solution="sketches/world-systems-front.cpp"}
   The program lists the six built-ins with their soft arrows, then `CameraFollow`, `Wind` (before Physics) and `EarlyInput` (before Scripting), and builds the order both ways. The engine registers the six as Physics, Audio, Animation, Scripting, World and UI; the program lists them in update order, and both builds give the same results either way. The whole program and its output:

   ```cpp sketch="world-systems-front.cpp"
   // The engine's test case for CameraFollow, Wind and EarlyInput, ordered from the front and from the back.
   #include <cstdio>
   #include <functional>
   #include <queue>
   #include <string>
   #include <vector>

   namespace
   {
   	struct System
   	{
   		std::string Name;
   		std::vector<int> After; // indices of the systems that must run before this one
   	};

   	std::vector<int> BuildOrder(const std::vector<System>& systems, bool fromBack)
   	{
   		const int count = static_cast<int>(systems.size());
   		std::vector<std::vector<int>> released(count);
   		std::vector<int> waiting(count, 0);
   		for (int second = 0; second < count; second++)
   		{
   			for (int first : systems[second].After)
   			{
   				const int from = fromBack ? second : first;
   				const int to = fromBack ? first : second;
   				released[from].push_back(to);
   				waiting[to]++;
   			}
   		}

   		const auto isBelow = [fromBack](int a, int b) { return fromBack ? a < b : a > b; };
   		std::priority_queue<int, std::vector<int>, decltype(isBelow)> ready(isBelow);
   		for (int index = 0; index < count; index++)
   		{
   			if (waiting[index] == 0)
   				ready.push(index);
   		}

   		std::vector<int> placed;
   		while (!ready.empty())
   		{
   			const int index = ready.top();
   			ready.pop();
   			placed.push_back(index);
   			for (int next : released[index])
   			{
   				if (--waiting[next] == 0)
   					ready.push(next);
   			}
   		}
   		if (fromBack)
   			return std::vector<int>(placed.rbegin(), placed.rend());
   		return placed;
   	}

   	std::string Join(const std::vector<System>& systems, const std::vector<int>& order)
   	{
   		std::string text;
   		for (int index : order)
   			text += (text.empty() ? "" : ", ") + systems[index].Name;
   		return text;
   	}
   }

   int main()
   {
   	// Registration order: the six built-ins, then CameraFollow, Wind (before Physics) and EarlyInput (before Scripting).
   	const std::vector<System> systems = {
   		{ "UI", {} },
   		{ "Scripting", { 0, 8 } },
   		{ "Animation", { 1 } },
   		{ "World", { 1 } },
   		{ "Physics", { 1, 2, 3, 7 } },
   		{ "Audio", { 1, 2, 3, 4 } },
   		{ "CameraFollow", {} },
   		{ "Wind", {} },
   		{ "EarlyInput", {} },
   	};
   	const std::string expected = "UI, EarlyInput, Scripting, Animation, World, Wind, Physics, Audio, CameraFollow";
   	const std::string fromBack = Join(systems, BuildOrder(systems, true));
   	const std::string fromFront = Join(systems, BuildOrder(systems, false));
   	std::printf("from the back : %s\n", fromBack.c_str());
   	std::printf("from the front: %s\n", fromFront.c_str());
   	std::printf("the test expects the back's order: back %s, front %s\n", fromBack == expected ? "passes" : "fails", fromFront == expected ? "passes" : "fails");
   	return 0;
   }
   ```

   ```text output-of="world-systems-front.cpp"
   from the back : UI, EarlyInput, Scripting, Animation, World, Wind, Physics, Audio, CameraFollow
   from the front: UI, CameraFollow, Wind, EarlyInput, Scripting, Animation, World, Physics, Audio
   the test expects the back's order: back passes, front fails
   ```

   1. **Lines 69–79:** the systems in registration order, each with the indices of the systems that must run before it.
   2. **Line 80:** the order that the engine's test expects.
   3. **Lines 81–82:** the two builds, from the back and from the front.

   The back's order equals the test's. The front's puts `CameraFollow` second, ahead of Scripting. In the engine you change the queue of `ComputeUpdateOrder` to take the smallest ready index from the front, and the test case `A system moves ahead of earlier registered ones only as far as its constraints require` fails at its first `CHECK`.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Scene/SceneSystem.h` and `SceneSystem.cpp`: `SceneSystem`, `SceneSystemDescriptor`, `MakeSceneSystemDescriptor`, `SceneSystemRegistry`, `ComputeUpdateOrder`.
- `Strata/src/Strata/Scene/Scene.h` and `Scene.cpp`: `OnRuntimeStart`, `OnRuntimeStop`, `OnUpdateRuntime`, `OnUpdateEditor`, `Copy`, `DestroyEntities`, `RegisterService`, `GetService`.
- `Strata/src/Strata/Scene/SceneServices.h`: the scene service interfaces; `Strata/src/Strata/Scene/ProjectSceneTiming.h`: the `Scene.Timing` section.
- `Strata/src/Strata/Engine/BuiltinModules.cpp`: the composition root and the log line of the update order.
- Tests: `StrataTests/src/Scene/SceneSystemTests.cpp` (`Scene.Systems`), `SceneServicesTests.cpp` (`Scene.Services`), `SceneTests.cpp` (`Scene`), `SceneTimingTests.cpp` (`Scene.Timing`).
- Other pages: [Drawing between fixed steps](../world/interpolation.md), [Sub-scenes](../world/sub-scenes.md) and [Entities and components, with EnTT inside](../world/ecs.md).

## Further reading

- Glenn Fiedler, "Fix Your Timestep!", on gafferongames.com: the accumulator and drawing between steps (beginner).
- Bevy's documentation of system ordering with `before` and `after`, cited without a link: the dependency-graph form (intermediate).
- Unity's manual of the Entities package on `UpdateBefore` and `UpdateAfter`, cited without a link: the same idea with attributes (intermediate).
- Robert Nystrom, "Game Programming Patterns", chapter "Game Loop", on gameprogrammingpatterns.com: fixed and variable steps (beginner).
