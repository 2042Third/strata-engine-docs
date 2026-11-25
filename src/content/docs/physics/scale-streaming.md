---
id: physics/scale-streaming
title: "Physics at scale and in streaming worlds"
description: "How Strata sizes its physics storage, grows it, parks static bodies and keeps bodies safe when a streamed world brings hundreds of thousands of them."
kind: internals
size: M
tracks: [E]
needs: [physics/world-step, world/sub-scenes]
time: 45
learn:
  - id: size-room
    text: compute the automatic room and the reserved memory of a physics world for a given number of bodies
  - id: explain-growth
    text: explain how a world grows, when a body must wait and which waiting body is served first
  - id: explain-parking
    text: explain why a cell's static bodies leave the simulation in two stages spread over many steps
  - id: name-limits
    text: name the two limits a body can meet, the growth limit and the coordinate limit, and what happens beyond each
since: 0.5.0
status: final
---

A streamed level can hold hundreds of thousands of physics bodies, and cells of it arrive and leave while the game runs. This page is about two promises the physics module keeps at that size. It stays fast, because it never does work in one step that grows with a whole cell. It stays safe, because a body that cannot be built yet waits in a known place and never silently loses its collision. The page does not cover how the streamer decides which cells to load, or how a game maker reserves room through the cook: [the world streamer's physics page](../worlds/physics-scripts.md) has that.

## The problem and how engines solve it

Physics storage costs memory before it costs time. Every body needs a slot for its position, its shapes, its place in the :term[broad phase's]{id=broad-phase} trees and its contacts. A world that must hold 100,000 bodies needs room for them all, and room means :term[bytes]{id=byte}.

An engine can size that room in three ways. It can fix it at a number the game maker chooses, which wastes memory when the number is high and fails when it is low. It can allocate every body on demand, which never fails but pays for a request to the memory system on each body and spreads bodies across memory. Or it can reserve a block in advance and grow the block when it fills. Strata takes the third way, with a cap so growth cannot eat all memory.

Streaming adds a second problem: cost arrives in lumps. A cell of 25,000 bodies that loads in one frame, or leaves in one frame, can stall that frame. Engines answer by doing the work in slices, by doing independent parts on several threads at once, and by making removal cheap now and finishing it later. Strata does all three. The loading side builds on [loading scenes in slices](../world/sub-scenes.md), which this page assumes.

## The map

Five parts take part.

The scene's settings and the project's physics settings say how much room a world starts with. The world streamer tells the module how many bodies are about to arrive. The module builds bodies in slices while a scene loads. The step grows the room when it holds fewer bodies than the scene has. Bodies that leave are parked first and disabled later.

```mermaid caption="Who asks for room, who builds bodies and who removes them, all on the main thread except the shape building" alt="The streamer reserves room, the loaded scene's prepared world builds bodies in slices, the step grows the room, and parked bodies are disabled by the step later."
flowchart LR
  Streamer["World streamer"] -->|"Reserve(bodies)"| Cap["IPhysicsCapacity"]
  Cap --> World["PhysicsWorld room"]
  Prep["PrepareLoadedScene slices"] -->|"builds bodies"| World
  World -->|"GrowRoom in the step"| World
  World -->|"full at the growth limit"| Queue["Waiting queue"]
  Queue -->|"freed slots, oldest first"| World
  World -->|"cell leaves"| Park["Parked bodies"]
  Park -->|"60 steps later"| Disabled["Disabled in box3d"]
```

`IPhysicsCapacity` is a :term[scene service]{id=scene-service} in `Strata/src/Strata/Scene/SceneServices.h`. It reports how many bodies a world holds and has room for, and its `Reserve` function asks for room ahead of need. The streamer calls it in `Strata/src/Strata/World/WorldStreamer.cpp` with the sum of the body counts of the persistent scene and of the cells that are loaded or about to load. `PhysicsSystem` implements it. A reservation made before the world exists applies once the world is created.

## The contract

Two words need a definition before the rules. **Capacity** is the number of bodies a physics world has room for, and its **growth limit** is the number it may never grow beyond: a cap on the memory physics uses. The limit is held in `PhysicsSettings::GrowthLimit`, where 0 means the engine's limit of 2^21.

The room is what the world has now, and the demand is the most it has needed, which Strata remembers for the scene's next world.

Callers may assume, and the module must keep, these rules.

- A world never leaves a body without collision while it is below its growth limit. box3d grows its storage in place while bodies are created, so a body gets a slot.
- At the growth limit, bodies wait in a queue in the order they started waiting. No step polls the queue: a slot freed by a removed body is handed to the front of it during the next round of changes.
- box3d computes in single precision and refuses coordinates beyond 1e5 m (100 km) from the origin. A body farther out waits like a body with a broken transform and gets its body when it is back within. Worlds themselves are supported within 20 km of the origin, the range in which the engine keeps positions precise enough.
- Every creation, sliced or parallel, gives the same body identifiers whatever the number of threads.

:::rule
The engine's guide forbids a body without collision while room remains, and bids full worlds to keep waiters in a queue that no step reads. The reason is safety: a body that silently lacks collision lets a player fall through the floor, and a queue read every step costs time for bodies that cannot be built anyway. [The world step](world-step.md) shows where the changes are applied.
:::

## A toy version

The toy models only the pool. It has a room that doubles up to a limit, a count of bodies in use, and a queue of waiters. It has no physics. Read how `Create` decides between growing and waiting, and how `Destroy` hands a slot to the oldest waiter.

```cpp sketch="physics-scale-streaming-toy.cpp"
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <deque>

// A pool of body slots: the room doubles while bodies arrive, up to a limit; beyond it bodies wait in order.
class BodyPool
{
public:
	BodyPool(uint32_t room, uint32_t limit)
		: m_Room(room), m_Limit(limit)
	{
	}

	// Gives the body a slot, or queues it when the pool is at its limit.
	void Create(uint32_t id)
	{
		if (m_Used >= m_Limit)
		{
			m_Waiters.push_back(id);
			return;
		}
		if (m_Used >= m_Room)
		{
			m_Room = std::min(m_Room * 2, m_Limit);
			m_Growths++;
		}
		m_Used++;
	}

	// Frees a slot and hands it to the body that waited longest.
	void Destroy()
	{
		m_Used--;
		if (m_Waiters.empty())
			return;
		const uint32_t id = m_Waiters.front();
		m_Waiters.pop_front();
		m_Used++;
		std::printf("body %u leaves the queue\n", id);
	}

	void Print() const
	{
		std::printf("used %u, room %u, growths %u, waiting %zu\n", m_Used, m_Room, m_Growths, m_Waiters.size());
	}

private:
	uint32_t m_Room;
	uint32_t m_Limit;
	uint32_t m_Used = 0;
	uint32_t m_Growths = 0;
	std::deque<uint32_t> m_Waiters;
};

int main()
{
	BodyPool pool(4, 8);
	for (uint32_t id = 0; id < 10; id++)
		pool.Create(id);
	pool.Print();
	pool.Destroy();
	pool.Destroy();
	pool.Destroy();
	pool.Print();
	return 0;
}
```

```text output-of="physics-scale-streaming-toy.cpp"
used 8, room 8, growths 1, waiting 2
body 8 leaves the queue
body 9 leaves the queue
used 7, room 8, growths 1, waiting 0
```

1. **Lines 18–22:** at the limit the body goes to the back of the queue and nothing else changes.
2. **Lines 23–26:** below the limit but with a full room, the room doubles, never beyond the limit, and one growth is counted.
3. **Lines 34–39:** a destroyed body frees a slot, and the front of the queue takes it at once.

The pool starts with room for 4 and a limit of 8. Ten bodies arrive: the room doubles once, from 4 to 8, and the last two wait. The first removal hands a slot to body 8 and the second to body 9, so the queue is served in arrival order. The third removal finds nobody waiting, so a slot stays free.

## The real code

The real world differs from the toy in four ways. It chooses its first room from what the scene holds. It grows to the next power of two. It builds shapes on several threads. It also has to remove bodies without stalling a step.

### Sizing the room

When play starts, or when a scene is prepared, `PhysicsSystem::MakeWorldSettings` lets a scene's own capacity win over the defaults. A scene holds its capacity in `SceneSettings::PhysicsCapacity`, with the fields `MaxBodies` and `MaxContactConstraints`. A value of 0 means automatic. The largest values are 2^21 bodies and 2^19 contacts.

The command `scene.setSettings` sets them with the object `physicsCapacity`. The older field `maxBodyPairs` is read and ignored since 0.5.0, with a warning, because box3d has no buffer of pairs to size.

Whatever is left automatic goes to `PhysicsWorld::ResolveCapacities`.

```cpp src="Strata/src/Strata/Physics/PhysicsWorld.cpp#L4775-L4787" symbol="PhysicsWorld::ResolveCapacities"
PhysicsSettings PhysicsWorld::ResolveCapacities(const PhysicsSettings& settings, uint32_t bodyCount, const PhysicsCapacityDemand& demand)
{
	PhysicsSettings resolved = settings;
	const uint64_t bodies = std::max(bodyCount, demand.Bodies);
	if (resolved.MaxBodies == 0)
		resolved.MaxBodies = ClampCapacity(std::max<uint64_t>(c_MinAutomaticBodies, NextPowerOfTwo(2 * bodies)), PhysicsCapacitySettings::c_MaxBodiesLimit);
	if (resolved.MaxContactConstraints == 0)
	{
		resolved.MaxContactConstraints = ClampCapacity(std::max({ uint64_t(c_ContactsPerBody) * c_MinAutomaticBodies, c_ContactsPerBody * bodies,
			uint64_t(demand.ContactConstraints) }), PhysicsCapacitySettings::c_MaxContactConstraintsLimit);
	}
	return resolved;
}
```

1. **Line 4778:** the count is the larger of the scene's candidate bodies and the demand an earlier world recorded.
2. **Lines 4779–4780:** the body room is the next power of two of twice that count, never below the minimum of 1,024, and never above the limit of 2^21.
3. **Lines 4781–4784:** the contact room is two contacts a body, never below 2,048, and at least the remembered demand.
4. **Line 4786:** the copy returns with every value the settings already held, since only values of 0 were replaced.

The bodies counted are the larger of the scene's candidate bodies and the demand an earlier world of the scene recorded. The body room is the next power of two of twice that count, never below 1,024. The contact room is two contacts a body, never below 2,048, and at least the demand's contacts.

:::example
A scene starts playing with 3,000 bodies. Twice that is 6,000, and the next power of two is 8,192, so `MaxBodies` becomes 8,192. The contact room is 2 × 3,000 = 6,000, above the minimum of 2,048.

What does this cost? `PhysicsWorld::EstimateReservedBytes` multiplies: 2,120 bytes a body, 250 bytes a contact, and a fixed 32 KiB. The sum is 8,192 × 2,120 + 6,000 × 250 + 32,768 = 18,899,808 bytes, about 19 MB. The constants are fitted to box3d's own byte counts, so the estimate takes :term[constant time]{id=constant-time} and costs no walk over the world.
:::

The estimate is why the growth limit exists. A game with a memory budget sets a limit, and the world stops growing there. At creation box3d reserves at most 2^17 bodies and 2^18 contacts, unless the automatic room is larger. A bigger room counts as growth, so the largest room a scene may ask for does not take a very large amount of memory at once.

### Growing the room

Bodies arrive in rounds of changes. At the end of each call that applies changes, and again before each step, the world calls `GrowRoom`.

```cpp src="Strata/src/Strata/Physics/PhysicsWorld.cpp#L2297-L2316" symbol="GrowRoom"
// Grows the room of a world to hold `required` bodies: box3d grows its storage itself while bodies are created, and the
// world counts it as a growth to the next power of two of at least twice the room (and records it as the scene's
// demand, so that its next world reserves the room at once). Returns whether the room grew.
bool GrowRoom(PhysicsWorldData& data, uint64_t required)
{
	if (required <= data.RoomBodies)
		return false;
	const uint32_t from = data.RoomBodies;
	const uint32_t to = static_cast<uint32_t>(std::min<uint64_t>(std::max<uint64_t>(NextPowerOfTwo(std::max<uint64_t>(2ull * from, required)), required),
		PhysicsCapacitySettings::c_MaxBodiesLimit));
	if (to <= from)
		return false;
	data.RoomBodies = to;
	data.GrowthCount++;
	data.LastGrowthFrom = from;
	data.LastGrowthTo = to;
	data.GrewThisRound = true;
	data.Demand.Bodies = std::max(data.Demand.Bodies, to);
	return true;
}
```

1. **Lines 2302–2303:** a world that already has the room does nothing, which is the common case.
2. **Lines 2304–2306:** the new room is the next power of two of the larger of twice the room and the need, capped at the engine's limit of 2^21.
3. **Lines 2309–2313:** one growth is counted however many bodies the round created, and its sizes are kept for the log and the statistics.
4. **Line 2314:** the demand records the new room, so the scene's next world starts with it.

Say `required` is 3,000 and the room is 1,024. Twice the room is 2,048, below 3,000, so the larger value, 3,000, is rounded up to 4,096: one growth, however many bodies the round created. Say instead the room is 4,096 and 4,097 bodies are required: twice the room, 8,192, is already a power of two. The doubling means a world that grows from a small start makes few growths, and each is counted (`GrowthCount`) and recorded as demand, so the scene's next world reserves the room at once. The log also advises cooking the world or raising its capacity, so that play starts at that size.

Reserving ahead uses the same function. `Reserve(bodies)` stores a number; each call that applies changes passes the larger of the used slots and that number to `GrowRoom`, and the step passes the number again before it runs. A streamer that reserves for a cell about to load therefore pays for growth before the cell's bodies exist, in a step that has nothing else new to do.

At the growth limit the world cannot grow, and `InstallBody` refuses the body.

```cpp src="Strata/src/Strata/Physics/PhysicsWorld.cpp#L2328-L2332" from="if (!record.HasBody() && GetUsedBodySlots(data) >= GetGrowthLimit(data.Settings))" to="SetBuildFailure(data, handle, record, BuildFailure::WaitingForSlot, pose.WorldTransform);" symbol="InstallBody"
if (!record.HasBody() && GetUsedBodySlots(data) >= GetGrowthLimit(data.Settings))
{
	record.SavedLinearVelocity = linearVelocity;
	record.SavedAngularVelocity = angularVelocity;
	SetBuildFailure(data, handle, record, BuildFailure::WaitingForSlot, pose.WorldTransform);
```

The record keeps the body's motion and takes the failure `WaitingForSlot`. One error names the first waiting entity and counts the others, so a cell of thousands that cannot fit logs once, not thousands of times. Waiting bodies count toward the demand, so the next world is sized for them.

When bodies are destroyed, `GiveSlotsToWaiters` runs in the same call. The function adds as many of the oldest waiters as there are free slots to the owners that the next round rebuilds. Nothing scans waiting bodies in a step, which is why waiting costs steps nothing.

### Building in parallel and in slices

A round with at least 256 owners (entities that own a body) to refresh builds the shapes on the job threads, in chunks of 512 owners that do not depend on how many threads exist. The bodies themselves are made afterwards on the :term[main thread]{id=main-thread} in record order, because box3d's world is not thread-safe and because the order fixes the identifiers. Shape building scales with the threads; the creation order does not change with them.

Static shapes get one more saving. Before the world's first step, a static shape does not search for contacts when it is made, since the first step finds every pair anyway. After the first step a new static shape does search, or it would miss bodies already resting where it appears. With 100,000 :term[static bodies]{id=static-body} built in one round, that is 100,000 searches saved.

A scene that loads in the background does not wait for play to build its bodies. `PhysicsSystem::PrepareLoadedScene` creates the world in a sliced mode and builds bodies 8,192 owners at a time, until the frame's time budget is spent, with at least one slice per call. When the scene starts, `OnRuntimeStart` builds any slices still left and adopts the world, so a scene prepared to the end builds no body in its first frame.

### Parking and disabling

Taking a body out of box3d's trees costs about 0.13 µs a body, and twice that the first time in a world. A cell of 25,000 bodies unloading costs 6.6 ms in a library-only measurement, which is 40 % of a frame at 60 :term[frames per second]{id=frame-rate}. Strata splits the removal in two.

A **parked body** is a static body without contacts that has left the simulation but is still in box3d's trees, with a filter that collides with nothing. Parking is the first stage.

```cpp src="Strata/src/Strata/Physics/PhysicsWorld.cpp#L1534-L1540" from="const b3Filter parked" to="return true;" symbol="ParkStaticBody"
const b3Filter parked = PhysicsFilters::MakeParkedShapeFilter(record.Layer);
for (const b3ShapeId shape : record.Shapes)
	b3Shape_SetFilter(shape, parked, false); // No contacts to end, and the proxies stay where they are
record.Parked = true;
data.ParkedBodies++;
data.ParkedRecords.emplace_back(handle, data.StepCount);
return true;
```

The filter makes the body invisible to every pair, query and sweep from this step on. Bodies with contacts, and triggers, are disabled at once, because box3d keeps a contact whatever the filters say.

The second stage is `DisableParkedBodies`, which the step calls before it moves any body.

```cpp src="Strata/src/Strata/Physics/PhysicsWorld.cpp#L1567-L1579" from="while (!data.ParkedRecords.empty()" to="disabled++;" symbol="DisableParkedBodies"
while (!data.ParkedRecords.empty() && disabled < c_ParkedDisablesPerStep && visited < c_ParkedEntriesPerStep)
{
	const auto [handle, parkedAt] = data.ParkedRecords.front();
	if (parkedAt + c_ParkedSteps > data.StepCount)
		break;
	data.ParkedRecords.pop_front();
	visited++;
	BodyRecord* record = FindRecord(data, handle);
	if (!record || !record->Parked || record->LeftSimulationAt != parkedAt)
		continue; // Back, gone or parked again since (a later entry)
	b3Body_Disable(record->BodyID);
	UnparkBody(data, *record, false);
	disabled++;
```

1. **Line 1567:** each step looks at no more than 1,024 disables and 8,192 entries, so its work has a fixed top.
2. **Lines 1570–1571:** entries are in parking order, so the first one not yet due ends the loop.
3. **Lines 1575–1576:** a body that came back, went or was parked again since is skipped.
4. **Lines 1577–1578:** box3d disables the body, and the record leaves the parked state.

A parked body is disabled `c_ParkedSteps` steps later, which is 60, a second at the default :term[timestep]{id=time-step}, and at most 1,024 bodies a step. A cell's entities are destroyed within that second, so most of its static bodies are never disabled at all: their records are dropped, at most 8,192 entries a step. A body that comes back before its time gets its filter back, and the entry is skipped.

```mermaid caption="Static bodies of an unloaded cell are parked at once and disabled in slices from 60 steps later" alt="A schedule: at step S the filters are emptied, steps S+1 to S+59 cost nothing, and from step S+60 at most 1,024 bodies are disabled each step."
flowchart LR
  A["Step S: filters emptied"] --> B["Steps S+1 to S+59: nothing"]
  B --> C["Step S+60: up to 1,024 disabled"]
  C --> D["Next steps: 1,024 more each"]
```

The diagram shows two costs. Only the first step after parking pays for the filters, and the later steps pay in bounded slices.

### The coordinate limit

box3d computes in single precision and asserts on coordinates beyond 1e5 m. `IsWithinCoordinateRange` tests each of a body's three coordinates against that limit. A body outside it gets no body and a warning, and keeps waiting with the degenerate ones until a change of transform brings it back. The engine does not simulate bodies farther than that. Why worlds stay within 20 km is [the streaming page's](../worlds/why-streaming.md) topic.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Fixed pool, set by the game maker | Many small physics libraries | No growth work in play | A failure or waste when the guess is wrong |
| One allocation per body | Simple engines | No reserved memory | Slow creation and scattered memory |
| Disable all bodies of a cell at once | Direct use of box3d | No parked state to track | A spike when a cell of 25,000 unloads |
| Reject bodies at the limit with an error | Engines that assert on overflow | No waiting queue | Lost collision, and crashes in shipping builds |

Sources are in Further reading.

## How it is tested

The suites live in `StrataTests/src/Physics/PhysicsCapacityTests.cpp`, `PhysicsPrepareTests.cpp` and `PhysicsLifecycleTests.cpp`. One test is named "At its growth limit a full world keeps bodies waiting, reported in one error, counted and remembered". It sets a limit of 4 and creates 10 boxes: 4 get bodies and 6 wait, with one error logged. Another checks that bodies waiting get freed slots in the order they started waiting.

`PhysicsPrepareTests.cpp` checks that a loaded scene's bodies are built a slice per frame and that the first frame builds none. `PhysicsLifecycleTests.cpp` checks that parked bodies collide with nothing until box3d drops them, a second later, 1,024 a step.

The performance tests in `StrataTests/src/Perf/PhysicsPerfTests.cpp` create 100,000 static bodies in one update and 65,536 bodies in a world reserved for them. Run the physics suites directly with `build/windows/bin/Debug/StrataTests.exe --test-suite=Physics*`; ctest runs them among its systems tests, under no name that holds the word Physics. The performance tests run only in Release and :term[Dist]{id=dist}, with `ctest --preset windows-release -L perf`.

## Changing it safely

Extend capacity behaviour in `PhysicsWorld`, never by letting a layer above set storage directly. Read the rules that apply, with their reasons.

- Every call into the world runs on the main thread, because worlds are created and destroyed there and box3d's world slots are not thread-safe.
- Never add polling of waiting bodies to a step: their cost must stay zero.
- Keep the order of creation fixed, or identifiers differ with the number of threads and the test of parallel creation fails.
- Change the constants of reserved bytes only with the test that holds the estimate within 15 % of box3d's own count.

Pass the capacity, prepare and parking test files before a commit.

## Summary

- A world's room is the next power of two of twice its bodies, at least 1,024 bodies and two contacts a body, and its memory is estimated from fixed byte constants.
- The room doubles when bodies need more room than it has, up to the growth limit; beyond it bodies wait in order and a freed slot goes to the oldest waiter.
- Static bodies without contacts are parked at once and disabled 60 steps later, at most 1,024 a step, so a cell leaving never stalls a step.
- A body farther than 1e5 m from the origin waits like a body with a bad transform.

## Check yourself

1. A world starts with room for 1,024 bodies, and a round creates 5,000. What is the room afterwards?

   :::answer{tests="size-room,explain-growth"}
   The room grows once, to 8,192. Twice 1,024 is 2,048, which is below 5,000, so the larger value is rounded up to the next power of two. The wrong answer 5,000 forgets the rounding; 2,048 forgets that the round needs more.
   :::

2. At the growth limit, ten bodies wait and three bodies are destroyed. Which bodies get slots?

   :::answer{tests="explain-growth"}
   The three that started waiting first. The queue keeps arrival order and the world hands freed slots from the front. The seven others keep waiting without any cost to the steps.
   :::

3. Why are the static bodies of an unloaded cell not disabled in the step they leave?

   :::answer{tests="explain-parking"}
   Disabling removes shapes from box3d's trees, which costs time for each body and adds up to a spike for a large cell. A parked body already collides with nothing, so waiting costs nothing, and the actual disabling spreads over later steps.
   :::

4. A body sits at x = 150,000 m. What does Strata do?

   :::answer{tests="name-limits"}
   Strata logs a warning and builds no body until the body is back within 1e5 m, as with a :term[degenerate transform]{id=degenerate-transform}. box3d computes in single precision and asserts on coordinates beyond that limit.
   :::

## Exercises

1. **Basic.** A scene holds 100,000 static bodies. Compute the automatic body room and the contact room.

   :::answer[Worked solution]{tests="size-room"}
   Twice the bodies is 200,000, and the next power of two is 262,144. The contacts are 2 × 100,000 = 200,000, above the minimum.
   :::

2. **Medium.** Write a sketch that parks 2,500 static bodies at step 10 and prints what each later step disables.

   :::answer[Worked solution]{tests="explain-parking"}
   The bodies become eligible at step 70. The program steps through, skips steps before 70 and disables at most 1,024 each time.

   ```cpp sketch="physics-scale-streaming-park.cpp"
   #include <algorithm>
   #include <cstdint>
   #include <cstdio>

   constexpr uint64_t c_ParkedSteps = 60;
   constexpr uint32_t c_DisablesPerStep = 1024;

   int main()
   {
   	// 2,500 static bodies are parked together at step 10; count what each later step disables.
   	const uint64_t parkedAt = 10;
   	uint32_t waiting = 2500;
   	for (uint64_t step = parkedAt; waiting > 0; step++)
   	{
   		if (step < parkedAt + c_ParkedSteps)
   			continue;
   		const uint32_t disabled = std::min(waiting, c_DisablesPerStep);
   		waiting -= disabled;
   		std::printf("step %llu disables %u, %u left\n", static_cast<unsigned long long>(step), disabled, waiting);
   	}
   	return 0;
   }
   ```

   ```text output-of="physics-scale-streaming-park.cpp"
   step 70 disables 1024, 1476 left
   step 71 disables 1024, 452 left
   step 72 disables 452, 0 left
   ```

   1. **Lines 5–6:** the two constants of the engine, copied from the real code.
   2. **Lines 12–13:** the loop starts at the parking step and stops when nobody waits.
   3. **Lines 15–16:** steps before the 60th after parking disable nothing.
   4. **Lines 17–18:** a step disables at most 1,024 bodies, so the last step takes the rest.
   :::

3. **Hard.** Trace it yourself: find where a waiting body is handed a slot when another body is destroyed.

   :::answer[Worked solution]{tests="explain-growth"}
   The function is `GiveSlotsToWaiters` in `Strata/src/Strata/Physics/PhysicsWorld.cpp`, called from `ApplyChanges`. Search for it and put a breakpoint there.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Physics/PhysicsWorld.cpp`: `ResolveCapacities`, `GrowRoom`, `ParkStaticBody`, `DisableParkedBodies`.
- `Strata/src/Strata/Scene/SceneServices.h`: `IPhysicsCapacity`.
- `Strata/src/Strata/Physics/PhysicsSystem.cpp`: `PrepareLoadedScene`, `Reserve`.
- Tests: `StrataTests/src/Physics/PhysicsCapacityTests.cpp`.

## Further reading

- box3d's documentation: the library the world wraps (advanced).
