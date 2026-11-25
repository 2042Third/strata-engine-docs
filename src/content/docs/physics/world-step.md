---
id: physics/world-step
title: "Inside `PhysicsWorld`: one step"
description: "How one fixed step of a physics world copies entity transforms to bodies, steps the library and writes poses back, with equal results on any thread count."
kind: internals
size: L
tracks: [E]
needs: [physics/building-bodies, world/interpolation]
time: 95
learn:
  - id: two-copies
    text: explain why a physics world keeps two copies of each transform, and who writes which copy and when
  - id: trace-step
    text: trace one fixed step through its stages, from `OnFixedUpdate` to the write-back
  - id: choose-move
    text: choose between a transform write, `Teleport`, a force and an impulse for a given gameplay move
  - id: determinism
    text: explain why results stay equal with any number of worker threads, and how tests check it
  - id: script-face
    text: name the physics classes a script holds and what a script cannot call
since: 0.5.0
status: final
---

A physics world runs one :term[fixed step]{id=fixed-step} in three moves: it brings its bodies in line with the scene, asks the physics library to advance them, and brings the results back to the scene. This page follows that step through `PhysicsWorld::Simulate`. It teaches the two ideas that every engine with a physics library meets: keeping the library and the scene graph in step, and getting the same results on any number of threads. It does not read the contact events, move the characters, grow the world or run the fixed-step loop; other pages do. At the end it shows what a script can do to a body.

## The problem and how engines solve it

A physics library keeps its own list of bodies with poses, velocities and shapes, and your scene keeps entities with transforms; neither knows the other. Every engine that uses such a library must copy poses across in both directions, every step, without visiting the thousands of bodies that did not change. Engines choose between giving the library the transforms, polling every body each step, and listening for changes. Strata listens for signals and polls only awake bodies, and the price is a rule for you: the contract below. What the library computes inside a step is the subject of [Dynamics](../physics/dynamics.md).

## The map

The physics system acts at three places of a frame, shown in the first diagram. The scene's own loop, taught in [Systems and the frame](../world/systems.md), decides how often each one runs.

```mermaid caption="One frame of a scene, with the places where physics acts. Physics applies changes and dispatches events in the update call, steps zero or more times in the fixed loop, and dispatches events after each step." alt="A row of boxes. The update of every system, where physics applies changes and dispatches events, leads to a fixed loop that runs zero or more times. In each pass physics applies changes, steps and dispatches events. The late update and the drawing of the frame follow."
flowchart LR
    A["Update of every system: physics applies changes, dispatches events"] --> B["Fixed loop, 0 to N passes: physics applies changes, steps, dispatches events"]
    B --> C["Late update of every system"]
    C --> D["Render"]
```

The second diagram opens the fixed step. A **collision step** is one call of the library's step function inside a fixed step. The setting `CollisionSteps` (default 1) says how many calls divide the fixed step, and the library splits each call into 4 :term[sub-steps]{id=sub-step}. Dividing helps very fast bodies, because each call covers less time.

```mermaid caption="The stages of one fixed step, in order. The loop in the middle runs once for each collision step." alt="A column of boxes. Apply changes, grow room, disable parked bodies and a check whether to hold for meshes come first. Then come sync entities to bodies and the characters step. A loop applies forces, steps the library for four sub-steps and reads its events, once for each collision step. Write-back, the pair checks and the instruments finish the step."
flowchart TD
    S1["ApplyChanges"] --> S2["GrowRoom"]
    S2 --> S3["DisableParkedBodies"]
    S3 --> S4{"HoldForMeshes?"}
    S4 -- "yes: return" --> S9["Step skipped"]
    S4 -- "no" --> S5["SyncEntitiesToBodies"]
    S5 --> S6["StepCharacters"]
    S6 --> L1["Per collision step: ApplyPendingForces"]
    L1 --> L2["b3World_Step, 4 sub-steps"]
    L2 --> L3["ProcessStepEvents"]
    L3 -- "next collision step" --> L1
    L3 -- "last one" --> W["WriteBackDynamicBodies"]
    W --> U["Pair upkeep, instruments"]
```

Growth and parked bodies belong to [Scale and streaming](../physics/scale-streaming.md), the characters' step to [Character controllers](../physics/character-controllers.md), and the events to [Contacts and triggers](../physics/contacts-triggers.md). The :term[main thread]{id=main-thread} runs every stage. Worker threads help in three places: inside the library's step, in the scan that skips unchanged bodies, and in the write-back's chunks.

## Two copies of the truth

Take a crate that sleeps on the ground. Its entity has a `TransformComponent`, and its body has a pose inside the library. Both say the crate is at height 0.5 m, so the scene and the simulation agree. A gameplay script now moves the crate to height 3 m by writing the entity's transform. Until something copies that write to the body, the library still believes the crate is on the ground.

Every engine with a physics library meets this problem: there are two copies of the truth. **Synchronization** (sync) is the copy from entity to body before the step.

The **write-back** is the copy from body to entity after it. Each copy happens at one moment, and each has one writer. Strata keeps a record for each body, with its type, its flags and the last world matrix on which the two copies agreed.

| Moment | Writer | Source | What is copied |
| --- | --- | --- | --- |
| Before the step | Strata's sync | Entity transform | Only what was signalled or is awake |
| During the step | The library | Its own bodies | Nothing reaches the scene yet |
| After the step | Strata's write-back | Body pose | Only :term[dynamic bodies]{id=dynamic-body} that moved, parents first |

```mermaid caption="The two copies of a transform. Gameplay writes the entity and signals the change; the sync copies it to the body before the step. The write-back copies the simulated pose to the entity after it, and tells the scene without an update signal." alt="Two boxes side by side, labelled entity transform and body pose. An arrow from the entity to the body, before the step, carries signalled or awake changes. An arrow from the body to the entity, after the step, carries what moved. A note says the write-back marks transforms changed without an update signal."
flowchart LR
    E["Entity transform (the scene)"] -- "Before the step: sync of what was signalled or is awake" --> B["Body pose (the library)"]
    B -- "After the step: write-back of what moved, parents first" --> E
    G["Gameplay and editor writes"] -- "MarkModified or MarkTransformChanged" --> E
    B -. "MarkTransformsChanged, no update signal" .-> E
```

Two questions decide the cost. Which entities does the sync have to look at? Looking at all of them is simple and slow, because a scene holds tens of thousands of sleeping bodies that never change. Strata looks at awake bodies, at bodies whose entity was signalled, and at bodies below an entity that moved without a signal. The second question is which bodies the write-back must visit, and the library answers it: it reports the bodies that moved.

:::example[One step of a crate and a thousand bodies]
A scene holds 1,000 bodies. Forty are awake and 960 sleep, among them the crate at 0.5 m. A script writes the crate's height 3 m, and the engine function behind the script's call runs `MarkModified` on its transform. At the next fixed step the sync checks the 40 awake bodies, whose entities sit exactly where the last write-back left them, and finds nothing to do. It also visits the crate, because the signal put it on the list of records that need attention.

The crate's :term[world transform]{id=world-transform} differs from the one stored in its record, so the sync :term[teleports]{id=teleport} the body to 3 m, keeping its velocity (zero), and wakes it and anything that rested on it. The library steps and the crate falls a little. The write-back writes the crate's new height to its entity. The step touched 41 of 1,000 bodies.

Without the signal, as when engine code writes the field and tells nobody, the crate is asleep, not awake and not listed. Physics never looks at it, the body stays at 0.5 m, and the entity says 3 m. The two copies disagree until something else wakes the crate.
:::

A body written back is also found again in the next sync, so the engine must not mistake its own write for an edit. The write-back stores the matrix it produced in the body's record (`LastWorldTransform`), and the next sync compares the entity's cached world transform with that matrix. Equal means unchanged. The write-back also tells the scene with `MarkTransformsChanged`, which marks transforms dirty without the update signal, so physics does not hear its own writes.

## The contract

What callers may assume and must do follows from the two copies.

- Queries see the bodies as the last step or `Teleport` left them. A transform written since then reaches the bodies at the next fixed step.
- A body that is awake follows even a write that only told the scene (`Scene::MarkTransformChanged`). A sleeping or :term[static body]{id=static-body} follows only a signalled write.
- Forces act for one fixed step. Impulses and velocity changes act at once.

:::rule[Signal every transform write]
Code that writes `TransformComponent` fields directly must tell the scene: use `MarkModified`, `registry.patch` or `Scene::MarkTransformChanged`. The scene caches world transforms, and physics reads those caches. The first two also send the update signal that physics listens to; `Scene::MarkTransformChanged` only refreshes the caches, so it reaches awake bodies alone. A write that tells nobody is lost, also for an awake body, because the next write-back replaces it. The [Scene graph](../world/scene-graph.md) page gives the transform contract in full.
:::

1. **Signal transform writes.** A signalled write reaches the body at the next step; one told only through `Scene::MarkTransformChanged` reaches only awake bodies, and a silent one is lost.
2. **Use `Teleport` for instant moves.** A transform write moves the body at the next step, so a query in between sees the old place. `Teleport` moves body and entity together and breaks :term[interpolation]{id=interpolation}, so the move is drawn where it lands.
3. **Apply forces in `OnFixedUpdate`, every step they should act.** A force queued in a frame lives for the next fixed step only. A frame can run no fixed step or several, so a force added once per frame acts unevenly.

## A toy version

The toy below has entities with a height, bodies that fall, and the three stages: sync, step, write-back. It keeps only the rules that cost something. Sync looks at signalled entities and awake bodies, the step moves awake bodies, and the write-back copies bodies that moved. Look at how the counts change as bodies fall asleep.

```cpp sketch="physics-world-step-toy.cpp"
// A toy physics step: copy in what changed, step what is awake, copy out what moved.
#include <cstddef>
#include <cstdio>
#include <vector>

struct Entity
{
	float Height = 0.0f;
	bool Signalled = false;
};

struct Body
{
	float Height = 0.0f;
	float Speed = 0.0f;
	bool Awake = true;
	bool Moved = false;
};

struct StepCounts
{
	int Synced = 0;
	int Stepped = 0;
	int Written = 0;
};

class ToyWorld
{
public:
	std::vector<Entity> Entities;
	std::vector<Body> Bodies;

	StepCounts Step(float timestep)
	{
		StepCounts counts;
		SyncEntitiesToBodies(counts);
		Simulate(timestep, counts);
		WriteBack(counts);
		return counts;
	}
private:
	// Before the step: look only at signalled entities and awake bodies.
	void SyncEntitiesToBodies(StepCounts& counts)
	{
		for (std::size_t index = 0; index < Bodies.size(); index++)
		{
			Body& body = Bodies[index];
			Entity& entity = Entities[index];
			if (!entity.Signalled && !body.Awake)
				continue;
			counts.Synced++;
			if (entity.Height != body.Height)
			{
				body.Height = entity.Height;
				body.Awake = true;
			}
			entity.Signalled = false;
		}
	}

	// The library's step: only awake bodies fall, and a body that lands falls asleep.
	void Simulate(float timestep, StepCounts& counts)
	{
		for (Body& body : Bodies)
		{
			if (!body.Awake)
				continue;
			counts.Stepped++;
			body.Speed -= 9.81f * timestep;
			body.Height += body.Speed * timestep;
			if (body.Height <= 0.0f)
			{
				body.Height = 0.0f;
				body.Speed = 0.0f;
				body.Awake = false;
			}
			body.Moved = true;
		}
	}

	// After the step: copy back only the bodies that moved.
	void WriteBack(StepCounts& counts)
	{
		for (std::size_t index = 0; index < Bodies.size(); index++)
		{
			if (!Bodies[index].Moved)
				continue;
			Entities[index].Height = Bodies[index].Height;
			Bodies[index].Moved = false;
			counts.Written++;
		}
	}
};

void Report(const ToyWorld& world, int step, const StepCounts& counts)
{
	std::printf("step %3d: synced %d, stepped %d, written %d; last entity %.2f m, its body %.2f m\n", step, counts.Synced, counts.Stepped,
		counts.Written, world.Entities[3].Height, world.Bodies[3].Height);
}

int main()
{
	ToyWorld world;
	const float heights[] = { 3.0f, 2.0f, 1.0f, 0.0f };
	for (const float height : heights)
	{
		world.Entities.push_back(Entity { height, false });
		world.Bodies.push_back(Body { height, 0.0f, height > 0.0f, false });
	}

	const float timestep = 1.0f / 60.0f;
	Report(world, 1, world.Step(timestep));
	for (int step = 2; step <= 60; step++)
		world.Step(timestep);
	Report(world, 61, world.Step(timestep));

	world.Entities[3].Height = 5.0f; // A write nobody signalled
	Report(world, 62, world.Step(timestep));
	world.Entities[3].Signalled = true;
	Report(world, 63, world.Step(timestep));
}
```

```text output-of="physics-world-step-toy.cpp"
step   1: synced 3, stepped 3, written 3; last entity 0.00 m, its body 0.00 m
step  61: synced 0, stepped 0, written 0; last entity 0.00 m, its body 0.00 m
step  62: synced 0, stepped 0, written 0; last entity 5.00 m, its body 0.00 m
step  63: synced 1, stepped 1, written 1; last entity 5.00 m, its body 5.00 m
```

1. **Lines 49–50:** a sleeping entity that nobody signalled is skipped.
2. **Lines 52–55:** a changed entity moves its body and wakes it.
3. **Lines 66–67:** sleeping bodies cost nothing in the step.
4. **Line 77:** every stepped body is marked moved, one that has only now fallen asleep included.
5. **Lines 86–90:** only moved bodies are written back.

The first step touches the three awake bodies and the fourth sleeps. When everything has settled, a step costs nothing. Writing the sleeping entity's height without a signal changes nothing: the entity says 5 m while the body stays at 0. The signal makes the sync visit it, and the body falls.

The real world differs in three ways. It never loops over all bodies: it keeps a list of awake bodies and a list of records that need attention, and the write-back uses a bitmap of moved bodies. It handles three body types, and parents. And it does the loops in parallel chunks, with results that do not depend on the number of threads.

## The real code

### The frame and the step

`PhysicsSystem` is the :term[scene system]{id=scene-system} that owns the world. Look at what runs in the frame, and at what the fixed step adds.

```cpp src="Strata/src/Strata/Physics/PhysicsSystem.cpp#L158-L177"
void PhysicsSystem::OnUpdate(Timestep)
{
	ApplyPendingChanges();
	DispatchCollisionEvents();
}

void PhysicsSystem::OnFixedUpdate(float timestep)
{
	ST_PROFILE_FUNCTION();

	ApplyPendingChanges();
	if (!m_World)
		return;

	SyncGravity();
	SyncLayers();
	SyncSimulationSettings();
	m_World->Simulate(timestep);
	DispatchCollisionEvents();
}
```

1. **Line 160:** the update applies queued changes (component edits, changes of parents, destruction), so queries made later in the frame see them.
2. **Lines 168–170:** a fixed step starts with the same application, and does nothing without a world.
3. **Lines 172–174:** the scene's gravity, collision layers and the project's simulation settings are copied into the world; each call changes the library only when its value changed.
4. **Line 175:** one fixed step of the world.
5. **Line 176:** events collected during the step reach scripts, after the step and never inside it.

`Simulate` starts by preparing the world. Look at the early exit that holds the step.

```cpp src="Strata/src/Strata/Physics/PhysicsWorld.cpp#L4984-L5000"
ApplyChanges(data);
// Room reserved for bodies to come (PhysicsWorld::Reserve) counts before the step (see "Capacities").
GrowRoom(data, data.ReservedBodies);
DisableParkedBodies(data);
const Clock::time_point applyEnd = Clock::now();
data.HeldLastStep = HoldForMeshes(data, timestep);
if (data.HeldLastStep)
{
	data.HeldStepCount++;
	data.LastStepTime = millisecondsBetween(startTime, Clock::now());
	return;
}

data.StepCount++; // Identifies this step in the contact pairs' marks
SyncEntitiesToBodies(data, timestep);
std::vector<PairKey> characterPairs;
StepCharacters(data, timestep, characterPairs);
```

1. **Line 4984:** pending changes become bodies, shapes and removals.
2. **Lines 4986–4987:** reserved room is counted before the step, and bodies parked for streaming are disabled.
3. **Lines 4989–4995:** while mesh :term[colliders]{id=collider} wait for their meshes the step is held and returns early, so bodies never fall through a floor that has not loaded.
4. **Line 4998:** entities are brought in line with bodies.
5. **Line 5000:** the characters move before the library steps.

### The library's steps

Now the loop of collision steps. Note where forces, events and the end of the loop sit.

```cpp src="Strata/src/Strata/Physics/PhysicsWorld.cpp#L5014-L5046"
for (uint32_t step = 0; step < steps; step++)
{
	ApplyPendingForces(data, data.ForcedBodies);
	const Clock::time_point libraryStart = Clock::now();
	{
		ST_PROFILE_SCOPE("PhysicsWorld::Simulate - box3d");
		b3World_Step(data.World, subStep, c_SolverSubSteps);
	}
	const Clock::time_point libraryEnd = Clock::now();
	const float stepLibraryTime = millisecondsBetween(libraryStart, libraryEnd);
	libraryTime += stepLibraryTime;
	data.HasStepped = true;
	ReadLibraryStep(data, profile, counters);
	CountContactGrowth(data, b3World_GetMaxCapacity(data.World), data.PreviousLibraryStepMs);
	data.PreviousLibraryStepMs = stepLibraryTime;
	const Clock::time_point eventsStart = Clock::now();
	readTime += millisecondsBetween(libraryEnd, eventsStart);
	ProcessStepEvents(data, step + 1 == steps);
	eventTime += millisecondsBetween(eventsStart, Clock::now());
}
for (const entt::entity handle : data.ForcedBodies)
{
	if (BodyRecord* record = FindRecord(data, handle))
	{
		record->PendingForce = glm::vec3(0.0f);
		record->PendingTorque = glm::vec3(0.0f);
		record->HasPendingForce = false;
	}
}
data.ForcedBodies.clear();
const Clock::time_point stepsEnd = Clock::now();

WriteBackDynamicBodies(data, timestep);
```

1. **Line 5016:** queued forces and torques are applied again before every collision step, because the library clears them after each.
2. **Line 5020:** one call of the library, covering a fraction of the fixed step, in 4 sub-steps.
3. **Line 5031:** the events of this call are read now, because the library clears them at its next call.
4. **Lines 5034–5043:** after the last call the queued forces are erased, so a force acts in one fixed step only.
5. **Line 5046:** the write-back, once for the whole fixed step.

A force of 10 N queued in a step with `CollisionSteps` equal to 2 acts for both calls, each covering half of 1/60 s. An impulse changes the velocity at once, so it needs no queue.

### Entity to body

`SyncEntitiesToBodies` collects its candidates: the awake bodies, the records that need attention and, in the end, the bodies below an entity that moved without a signal. It drops unchanged awake bodies in parallel chunks (from 1,024 awake bodies), sorts the candidates by entity, and calls `SyncBody` for each, so the order does not depend on how bodies woke. `SyncBody` first compares the entity's world transform with the one in the record.

```cpp src="Strata/src/Strata/Physics/PhysicsWorld.cpp#L3344-L3356"
const glm::mat4 worldTransform = scene.GetWorldTransform(entity);
if (worldTransform == record->LastWorldTransform)
{
	// A kinematic body keeps the velocity of its last move; stop it at its target.
	if (record->KinematicMoving)
	{
		b3Body_SetLinearVelocity(record->BodyID, b3Vec3 { 0.0f, 0.0f, 0.0f });
		b3Body_SetAngularVelocity(record->BodyID, b3Vec3 { 0.0f, 0.0f, 0.0f });
		record->KinematicMoving = false;
	}
	record->TransformDirty = false;
	return;
}
```

1. **Lines 3344–3345:** an unchanged transform needs no work, with one exception.
2. **Lines 3348–3352:** a :term[kinematic body]{id=kinematic-body} keeps the velocity of its last move, so when its entity stops, the body must stop too.
3. **Line 3354:** the record is clean again; the signal is used up.

A transform that changed is split into position, rotation and scale, and checked: a degenerate or distant transform sends the body out of the simulation with a warning. Then the body type decides.

```cpp src="Strata/src/Strata/Physics/PhysicsWorld.cpp#L3394-L3420"
switch (record->Type)
{
	case RigidBodyType::Static:
		// Bodies resting on it at the old and the new place are woken up explicitly: static bodies have no island.
		WakeBodiesIn(data, b3Body_ComputeAABB(record->BodyID));
		b3Body_SetTransform(record->BodyID, ToB3(position), ToB3(rotation));
		WakeBodiesIn(data, b3Body_ComputeAABB(record->BodyID));
		break;
	case RigidBodyType::Kinematic:
		// Moved with a velocity that reaches the target in the step: the bodies it touches, also those resting on it,
		// wake up through their contacts.
		b3Body_SetTargetTransform(record->BodyID, b3WorldTransform { ToB3(position), ToB3(rotation) }, timestep, true);
		MarkAwake(data, record->BodyID);
		record->KinematicMoving = true;
		record->KinematicTargetPosition = position;
		record->KinematicTargetRotation = rotation;
		break;
	case RigidBodyType::Dynamic:
		// Moved from outside physics (gameplay code, editor gizmo, a moving parent): teleport, keeping velocity,
		// and wake the bodies that rested on it.
		WakeTouchingBodies(data, record->BodyID);
		b3Body_SetTransform(record->BodyID, ToB3(position), ToB3(rotation));
		b3Body_SetAwake(record->BodyID, true);
		MarkAwake(data, record->BodyID);
		break;
}
record->LastWorldTransform = worldTransform;
```

1. **Lines 3396–3400:** a static body belongs to no island, the library's group of touching bodies that sleep and wake together. So bodies resting on it at the old place and at the new place are woken explicitly.
2. **Lines 3402–3410:** a kinematic body gets a velocity that reaches the target in this step, and the contacts wake what it touches. The next sync stops it.
3. **Lines 3411–3418:** a dynamic body moved from outside is teleported and keeps its velocity; bodies that rested on it wake.
4. **Line 3420:** the record keeps the matrix, so the next step can tell a new edit from an old one.

Suppose a lift is a kinematic body and its script writes a new height each frame. The sync does not teleport it: the library moves it with a velocity, so a box on the lift is carried along instead of being left behind. A dynamic crate moved the same way is teleported and gets no such push.

### Body to entity

When a body moves in a step, the library lists it. Strata marks the body in a bitmap, one bit for each body slot, kept in 64-bit words. When a word gets its first bit, Strata adds the word's number to a list.

```cpp src="Strata/src/Strata/Physics/PhysicsWorld.cpp#L3628-L3637"
void MarkMoved(PhysicsWorldData& data, b3BodyId body)
{
	const int64_t index = static_cast<int64_t>(body.index1) - 1;
	if (index < 0 || static_cast<size_t>(index) >= data.BodySlots.size())
		return;
	uint64_t& word = data.MovedBodyBits[static_cast<size_t>(index) / 64];
	if (word == 0)
		data.MovedBodyWords.push_back(static_cast<uint32_t>(index / 64));
	word |= uint64_t(1) << (index % 64);
}
```

1. **Line 3630:** the slot number is the library's index minus one.
2. **Lines 3633–3635:** the first bit set in a 64-bit word puts the word on a list.
3. **Line 3636:** the bit for this body is set, and setting a bit twice changes nothing.

The write-back needs the moved bodies in a fixed order. Sorting them would cost more for every body that moved. The bitmap sorts only the words that got a bit and then reads each word's bits from the lowest. Moved bodies 130, 3, 71 and 70 give the words 2, 0 and 1 (in the order of the first bit), which sort to 0, 1, 2 and yield 3, 70, 71, 130. A world of 100,000 slots has 1,563 words, and the cost follows only the words that moved.

```cpp src="Strata/src/Strata/Physics/PhysicsWorld.cpp#L4211-L4230"
std::vector<uint64_t>& movedBits = data.MovedBodyBits;
std::vector<uint32_t>& movedWords = data.MovedBodyWords;
std::sort(movedWords.begin(), movedWords.end());
data.LastOrderedSlots = static_cast<uint32_t>(movedWords.size() * 64);

data.WriteBackPass++;
const uint64_t pass = data.WriteBackPass;
std::vector<PoseWrite>& writes = data.PoseWrites;
writes.clear();
for (const uint32_t word : movedWords)
{
	const uint64_t wordBits = std::exchange(movedBits[word], 0);
	for (uint64_t bits = wordBits; bits != 0; bits &= bits - 1)
	{
		const BodySlot& slot = data.BodySlots[size_t(word) * 64 + static_cast<size_t>(std::countr_zero(bits))];
		if (slot.Used && slot.Record)
			writes.push_back(PoseWrite { slot.Record, slot.Entity });
	}
}
movedWords.clear();
```

1. **Line 4213:** only the words that got bits are sorted.
2. **Line 4222:** reading a word also clears it, so the bitmap is empty for the next step.
3. **Line 4223:** `bits &= bits - 1` clears the lowest set bit, so the loop runs once for each moved body.
4. **Line 4225:** counting trailing zeros turns the lowest set bit into the body's slot.
5. **Line 4230:** the list of words is empty again.

The list holds record pointers and entities in body order. The records are not read here, because a read is a cache miss per body; the jobs read them. Now a single write. The body's pose is in :term[world space]{id=world-space}, and the entity's transform is local to its parent.

```cpp src="Strata/src/Strata/Physics/PhysicsWorld.cpp#L4144-L4179"
void WritePose(PoseWrite& item, const glm::mat4* parentWorld, SettlingSums& settling, float inverseTimestep, float sleepThreshold)
{
	BodyRecord& record = *item.Record;
	glm::vec3 position;
	glm::quat rotation;
	if (!ReadBodyPose(record.BodyID, position, rotation))
	{
		item.NonFinite = true;
		return;
	}
	const float displacement = glm::length(position - glm::vec3(record.LastWorldTransform[3]));

	// The same products, through the same function, as Scene::GetWorldTransform and UpdateWorldTransforms, so that
	// LastWorldTransform equals the matrix the scene will cache (the next step compares them).
	const glm::mat4 currentWorld = parentWorld ? Math::ComposeWorldTransform(*parentWorld, item.Transform->GetTransform())
		: item.Transform->GetTransform();
	glm::vec3 worldScale = record.WorldScale;
	if (currentWorld != record.LastWorldTransform)
	{
		glm::vec3 translation;
		glm::quat currentRotation;
		glm::vec3 scale;
		if (Math::DecomposeTransform(currentWorld, translation, currentRotation, scale))
			worldScale = scale;
		item.ScaleChanged = HasScaleChanged(worldScale, record.ShapeScale);
	}

	const glm::mat4 pose = Math::ComposeTransform(position, glm::normalize(rotation), worldScale);
	if (!SetLocalPose(*item.Transform, parentWorld ? glm::inverse(*parentWorld) * pose : pose))
		return;
	record.LastWorldTransform = parentWorld ? Math::ComposeWorldTransform(*parentWorld, item.Transform->GetTransform())
		: item.Transform->GetTransform();
	record.WorldScale = worldScale;
	item.Written = true;
	settling.Add(displacement, inverseTimestep, sleepThreshold);
}
```

1. **Line 4149:** a pose that is not finite is reported and never written.
2. **Line 4158:** the entity's current world matrix is composed with the same function the scene uses, so the stored matrix equals what the scene will cache.
3. **Line 4171:** the new world pose keeps the authored scale, because the body knows nothing of scale.
4. **Line 4172:** the pose is brought into the parent's space with the inverse of the parent's world transform.
5. **Line 4174:** the record keeps the matrix the scene will cache, and the next sync compares with it.

:::example[A child below a scaled parent]
A parent has translation (10, 0, 0) and uniform scale 2. Its child body ends the step at the world position (12, 3, 0). The child's world scale is 2, because the parent's scale carries into it. The offset from the parent is (2, 3, 0), and dividing it by the scale 2 gives the local translation (1, 1.5, 0). The local scale is 1, as authored: the write changed the translation and kept the scale.
:::

The write-back runs in two passes over the list. The first pass marks every dynamic body written and writes those without a parent. The second pass writes the parented bodies against their parent's current world matrix, except bodies below another written body, which wait. Look at how the work divides.

```cpp src="Strata/src/Strata/Physics/PhysicsWorld.cpp#L4237-L4256"
constexpr uint32_t c_ParallelWriteThreshold = 512;
const bool parallel = count >= c_ParallelWriteThreshold && JobSystem::IsInitialized();
std::mutex settlingMutex;
std::atomic<uint32_t> dynamicCount = 0;
std::atomic<uint32_t> parentedCount = 0;
std::atomic<uint32_t> deferredCount = 0;
const auto forEachChunk = [&](const auto& visit)
{
	const auto chunk = [&](uint32_t begin, uint32_t end)
	{
		SettlingSums sums;
		visit(begin, end, sums);
		std::scoped_lock<std::mutex> lock(settlingMutex);
		settling.Merge(sums);
	};
	if (parallel)
		JobSystem::ParallelFor(count, std::max<uint32_t>(64, count / ((JobSystem::GetWorkerThreadCount() + 1) * 4)), chunk);
	else
		chunk(0, count);
};
```

1. **Lines 4237–4238:** below 512 writes the chunks are not worth their cost, and without a job system the work stays on one thread.
2. **Lines 4247–4250:** each chunk keeps its own settling sums and merges them under a lock, once.
3. **Line 4253:** the chunk size is at least 64 writes, or the count divided by four chunks for each thread.
4. **Line 4255:** below the threshold, one chunk covers everything.

With 640 writes and 3 workers the chunk size is the larger of 64 and 640 divided by 16, which is 40, so it is 64: ten chunks. Nested bodies, whose ancestors are written in the same step, go to the main thread. First the main thread calls `MarkTransformsChanged` once for the bodies the jobs wrote, and fixes the bodies below moved parents. Then it sorts the nested bodies by depth and then by entity, so every parent is written before its children, each against the parent's new pose.

```mermaid caption="The parallel write-back. The main thread lists the moved bodies in order, jobs write chunks of roots and of children whose parents did not move, and the main thread tells the scene and then finishes the nested ones." alt="Three stages from left to right. The main thread lists moved bodies from the bitmap. Several chunks write poses in parallel, first the bodies without parents, then bodies whose parents did not move. The main thread then marks the written transforms changed and writes nested bodies by depth."
flowchart LR
    M1["Main thread: list moved bodies in body order"] --> J1["Jobs, fixed chunks: write roots"]
    J1 --> J2["Jobs, fixed chunks: write bodies under parents that did not move"]
    J2 --> M2["Main thread: MarkTransformsChanged, then nested bodies by depth"]
```

### Forces, teleports and gravity

A force queued by a script goes to the body's record and to a list of forced bodies, and wakes the body. The loop in `Simulate` applies it before each collision step, and erases it after the last. A `Teleport` does the work of the sync at once, for one body.

```cpp src="Strata/src/Strata/Physics/PhysicsWorld.cpp#L5320-L5353"
if (!WriteWorldTransform(scene, entity, Math::ComposeTransform(position, normalizedRotation, worldScale)))
{
	ST_CORE_WARN("Physics: cannot teleport '{}': its parent is scaled to (nearly) zero", entity.GetName());
	return false;
}
record->LastWorldTransform = scene.GetWorldTransform(entity);
record->WorldScale = worldScale;
record->KinematicTargetPosition = position;
record->KinematicTargetRotation = normalizedRotation;
record->KinematicMoving = false;

// Bodies resting on it must notice that it left.
if (record->Type == RigidBodyType::Static)
{
	WakeBodiesIn(data, b3Body_ComputeAABB(record->BodyID));
	b3Body_SetTransform(record->BodyID, ToB3(position), ToB3(normalizedRotation));
	WakeBodiesIn(data, b3Body_ComputeAABB(record->BodyID));
}
else
{
	WakeTouchingBodies(data, record->BodyID);
	if (record->Type == RigidBodyType::Kinematic)
	{
		b3Body_SetLinearVelocity(record->BodyID, b3Vec3 { 0.0f, 0.0f, 0.0f });
		b3Body_SetAngularVelocity(record->BodyID, b3Vec3 { 0.0f, 0.0f, 0.0f });
	}
	b3Body_SetTransform(record->BodyID, ToB3(position), ToB3(normalizedRotation));
	WakeRecord(data, *record);
}

// The entity's descendants moved with it.
UpdateDescendantsOfMovedBody(data, entity, false);
// A teleport is drawn where it lands, never blended from where the body was (with what rides on it).
scene.BreakInterpolation(entity);
```

1. **Line 5320:** the entity is written first, with its world scale kept; a parent scaled to zero makes the call fail.
2. **Line 5329:** a kinematic body stops being "moving", because it is already where it should be.
3. **Line 5340:** bodies resting on the one that left are woken.
4. **Line 5351:** the descendants moved with it, and their bodies follow at the next step.
5. **Line 5353:** the move is drawn where it lands, never blended from where the body was.

Gravity comes from the scene's settings, by default (0, -9.81, 0). `SyncGravity` compares it with the applied value at every fixed step, and a change wakes every body, because sleeping bodies would never learn that they should fall.

### The library's tasks

The library splits its stages into tasks, one for each worker. Strata gives it :term[callbacks]{id=callback} that run those tasks on its own job system, so that the process keeps one worker thread for each core.

```cpp src="Strata/src/Strata/Physics/PhysicsTaskSystem.cpp#L14-L49"
struct PhysicsTaskSystem::Callbacks
{
	// Starts one box3d task. Returns the slot finishTask waits on, or null when the task ran here already (box3d then
	// does not call finishTask for it).
	static void* Enqueue(b3TaskCallback* task, void* taskContext, void* userContext, const char*)
	{
		PhysicsTaskSystem& system = *static_cast<PhysicsTaskSystem*>(userContext);
		PhysicsTaskCounters* counters = system.m_Counters;
		if (counters)
			counters->Tasks.fetch_add(1, std::memory_order_relaxed);
		Task* slot = JobSystem::IsInitialized() ? system.AcquireTask() : nullptr;
		if (!slot)
		{
			task(taskContext);
			return nullptr;
		}

		slot->Handle = JobSystem::Submit([task, taskContext, counters]()
		{
			if (counters && JobSystem::IsWorkerThread())
				counters->WorkerTasks.fetch_add(1, std::memory_order_relaxed);
			task(taskContext);
		}, JobPriority::High);
		return slot;
	}

	// Blocks until a task started by Enqueue is done: it runs on this thread if no worker has started it yet.
	static void Finish(void* userTask, void* userContext)
	{
		PhysicsTaskSystem& system = *static_cast<PhysicsTaskSystem*>(userContext);
		Task* slot = static_cast<Task*>(userTask);
		slot->Handle.Wait();
		slot->Handle = JobHandle();
		system.ReleaseTask(slot);
	}
};
```

1. **Lines 24–28:** without a free slot or a job system the task runs at once on the calling thread; the library then does not wait for it.
2. **Line 31:** otherwise the task becomes a job of high priority.
3. **Line 37:** the slot is the token the library waits on.
4. **Line 45:** waiting on the job runs it on the waiting thread when no worker has started it, so a step ends even when every worker is busy.

## Determinism

The second idea is :term[determinism]{id=determinism}: the same input gives the same output, on any number of threads. Floating-point addition depends on order. $(a + b) + c$ can differ from $a + (b + c)$ in the last bits, and a pile of boxes can settle differently when the additions happen in another order. A replay, a network game and a regression test all need the same results. A fixed step and a fixed order do most of the work, and Strata adds four rules.

- Ordered records: candidates are sorted by entity, moved bodies come in body order, and nested writes go by depth and entity.
- Fixed chunks: a chunk is decided by the count and the worker count, and each chunk writes only its own bodies.
- :term[Integer]{id=integer} sums: the settling statistics keep squared displacements as integers in units of $10^{-8}$ m and combine in any order exactly.
- The library's own claim: its step gives the same results for any number of workers. Its stored **golden hash** is a :term[hash]{id=hash} of a reference run (falling jointed figures) that a changed behavior would break.

Strata does not trust the claim; it checks it. The twin-run test builds a pile of 24 bodies twice and compares every pose, then once more with 3 workers.

```cpp src="StrataTests/src/Physics/PhysicsSimulationTests.cpp#L821-L839"
TEST_CASE("Identical runs produce identical results, with or without worker threads")
{
	const std::vector<BodyPose> first = SimulatePile();
	const std::vector<BodyPose> second = SimulatePile();
	CHECK(first.size() == 25);
	CHECK(AreIdentical(first, second));

	// Bodies settled into a pile instead of falling through each other or the ground.
	for (size_t index = 1; index < first.size(); index++)
	{
		CHECK(IsFinite(first[index].Translation));
		CHECK(first[index].Translation.y > 0.15f);
	}

	// box3d's tasks run on Strata's worker pool when it is initialized; the results must not change.
	ScopedJobSystem jobSystem(3);
	const std::vector<BodyPose> threaded = SimulatePile();
	CHECK(AreIdentical(first, threaded));
}
```

1. **Lines 823–826:** two runs without workers give identical poses.
2. **Line 836:** a job system with 3 workers starts, so the library's tasks run in parallel.
3. **Line 838:** the poses must match the first run exactly, not nearly.

A second test, in `Physics.Box3D`, runs the library's own scenario without a job system and with four workers, and compares each result with the golden hash.

## The script face of bodies

A script never touches the world. It holds small classes of the script software development kit (SDK) that call host functions, and the engine runs the functions through the services above. The map of the classes:

| Class | :term[Header]{id=header} | What it holds | Shown on |
| --- | --- | --- | --- |
| `RigidBody` | `StrataScriptCore/Include/StrataScript/Physics.h` | A body's velocities, forces, impulses, torque and `Teleport` | This page |
| `Physics` | the same header | Raycasts and shape queries | [Queries](../physics/queries.md) |
| `RaycastHit` | the same header | One ray result | [Queries](../physics/queries.md) |
| `Collision` | the same header | A contact passed to a callback | [Contacts and triggers](../physics/contacts-triggers.md) |
| `CharacterController` | `StrataScriptCore/Include/StrataScript/CharacterController.h` | Moving and teleporting a character | [Character controllers](../physics/character-controllers.md) |
| `GroundState` | the same header | Where a character stands | [Character controllers](../physics/character-controllers.md) |

A script gets a body through its entity (`GetEntity().GetRigidBody()` in the sample scripts). Reading velocities works on any body; setting them, forces and impulses work on dynamic bodies only. Forces and torque act during the next fixed step, so a script applies them in `OnFixedUpdate`. Impulses change the velocity at once. `Teleport` takes a position and a rotation, or a position alone, which keeps the world rotation.

```cpp pseudocode
void OnFixedUpdate(float fixedDeltaTime)
{
	GetEntity().GetRigidBody().AddForce(glm::vec3(0.0f, 40.0f, 0.0f)); // acts in this step only
}

void OnJump()
{
	GetEntity().GetRigidBody().AddImpulse(glm::vec3(0.0f, 6.0f, 0.0f)); // at once
}
```

The first function shows the contract: a thrust must be applied in every fixed step it should act. The second applies an impulse once from an event.

The services behind the host functions offer more than the SDK: `IBodyMotionQuery` has `IsSleeping` and a point's velocity, and `IBodyControl` has `WakeUp` and `SetGravityScale`, but no host function exposes them. The SDK's `RigidBody` lacks them. A script that must change a body's type, mass, friction or layer writes a property of the `RigidBody` component through `Entity::SetProperty`. Every such change rebuilds the body, though the rebuilt body keeps its motion: a test sets the mass of a moving box and finds the velocity unchanged. A script that does this every frame pays for a rebuild every frame.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Poll every body every step | Simple engines and many prototypes | No signal rule: any write is seen | Cost grows with all bodies, sleeping ones too |
| The library owns the transforms; the scene reads them | Engines whose scene stores no transforms of its own | One copy of the truth | Scene features (hierarchy, editor, scripts) would work against the library's data |
| Event-driven sync only | Some component-based engines | The cheapest sync | Silent writes to awake bodies would be lost |
| Write back all bodies | Simple integrations | No bitmap | Cost grows with sleeping bodies, and sleeping entities would be marked changed |
| Own :term[thread pool]{id=thread-pool} for the library | Libraries run alone | Tasks tuned for the library | A second pool of threads per core |

Sources are listed in Further reading.

## How it is tested

The `Physics.Simulation` suite holds the step's behavior. It has the twin-run test above and the parented crowd of 643 bodies (640 written), which must come out equal on one thread and on several. Another test moves a body from under a resting one in three ways (`Teleport`, a transform edit and a kinematic move) and expects the top body to fall. `Physics.Lifecycle` holds the body rebuild after a property edit, and `Physics.Box3D` holds the golden hash. Run one suite directly:

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite="Physics.Simulation"
```

The tests need no graphics hardware, so `ctest --preset windows-debug -LE gpu` runs them too. Tests that compare worker counts use `ScopedJobSystem`, which starts a job system for the length of one scope.

## Changing it safely

The extension points are few. A new kind of body change enters through a component the world listens to, and a new stage of the step goes into `Simulate` with its own entry in the stage times (`PhysicsStats`). Rules to keep:

- A write to a transform must be signalled. This is why physics does not poll sleeping bodies (see the contract).
- The write-back changes translation and rotation only, and never emits `on_update`; a stage that writes poses must use `MarkTransformsChanged`.
- Everything that goes to worker threads writes only its own record, and results combine in an order fixed by the data. A new sum is an integer sum or a maximum.
- A step's duration is :term[constant time]{id=constant-time} in what it reports each frame; new instruments must not cost per body.
- Run the `Physics.*` suites, and the pile and golden-hash tests with and without workers, before you commit.

## Summary

- The scene and the world hold two copies of each transform; sync copies entity to body before the step, and write-back copies body to entity after it.
- A fixed step applies changes, may hold for meshes, syncs, steps characters, runs the collision steps with forces applied before each, writes back and keeps the pairs.
- Signal transform writes, use `Teleport` for instant moves, and apply forces in every step they should act.
- Results stay equal with any thread count through ordered records, fixed chunks, integer sums and the golden hash, checked by twin runs.
- A script holds `RigidBody`, `Physics` and others; it cannot call `IsSleeping` or `WakeUp`, and a property edit rebuilds the body.

## Check yourself

1. Engine code sets a sleeping crate's `Translation` field and does nothing else. What happens at the next fixed step, and why?

   :::answer{tests="two-copies,choose-move"}
   Nothing. A sleeping body is not polled, and the write sent no signal, so the body stays where it was. The fix is `MarkModified`, or `Teleport` for an instant move. A script never meets this case, because its transform calls signal the change.
   :::

2. Moved bodies 5, 64 and 2 are marked in a bitmap in that order. In which order does the write-back visit them?

   :::answer{tests="trace-step,determinism"}
   In the order 2, 5, 64. The words are 0, 1 and 0 in the order of their first bit; the list sorts to words 0 and 1, and each word reads its bits from the lowest.
   :::

3. A force acts for one step. Which choice is right, and why are the others wrong? (a) Add it once per frame in `OnUpdate`. (b) Add it in `OnFixedUpdate`. (c) Add it as an impulse.

   :::answer{tests="choose-move"}
   Choice (b). A force acts in the next fixed step only, and `OnFixedUpdate` runs once for each step, so the force acts in every step. Choice (a) acts in the next step only, and a frame with two steps leaves the second without it. Choice (c) changes the velocity at once, which is a different push.
   :::

4. Why does the golden hash alone not prove that a Strata world is deterministic?

   :::answer{tests="determinism"}
   The hash covers the library's own scenario. Strata's sync, write-back and sums run around the library, so Strata adds twin runs with and without workers.
   :::

5. Which of these can a script call on a body: `AddImpulse`, `IsSleeping`, `Teleport`, `SetGravityScale`?

   :::answer{tests="script-face"}
   `AddImpulse` and `Teleport`. The services have `IsSleeping` and `SetGravityScale`, but no host function exposes them, so the SDK's `RigidBody` lacks them.
   :::

## Exercises

1. **Basic.** Write a program that marks bodies 130, 3, 71 and 70 in a bitmap of three words and prints them in order, visiting only words that got a bit.

   :::answer[Worked solution]{tests="trace-step,determinism" solution="sketches/physics-world-step-bitmap.cpp"}
   Mark each body in the word `body / 64` at bit `body % 64`, and list the word on its first bit. Sort the list, then read each word from its lowest bit with `std::countr_zero`.

   ```cpp sketch="physics-world-step-bitmap.cpp"
   // Orders moved body numbers with a bitmap, visiting only the words that got a bit.
   #include <algorithm>
   #include <bit>
   #include <cstdint>
   #include <cstdio>
   #include <utility>
   #include <vector>

   int main()
   {
   	std::vector<uint64_t> bits(3, 0);
   	std::vector<uint32_t> words;
   	const uint32_t moved[] = { 130, 3, 71, 70 };
   	for (const uint32_t body : moved)
   	{
   		uint64_t& word = bits[body / 64];
   		if (word == 0)
   			words.push_back(body / 64);
   		word |= uint64_t(1) << (body % 64);
   	}

   	std::sort(words.begin(), words.end());
   	for (const uint32_t index : words)
   	{
   		for (uint64_t rest = std::exchange(bits[index], 0); rest != 0; rest &= rest - 1)
   			std::printf("%u ", index * 64 + static_cast<uint32_t>(std::countr_zero(rest)));
   	}
   	std::printf("\n");
   }
   ```

   ```text output-of="physics-world-step-bitmap.cpp"
   3 70 71 130 
   ```

   1. **Lines 16–19:** a body sets its bit, and the first bit of a word lists the word.
   2. **Line 22:** only the listed words are sorted.
   3. **Line 25:** each word is read from its lowest bit and cleared.
   :::

2. **Medium.** Trace it yourself: open one fixed step in Tracy and find the scopes for the sync, the library's step and the write-back. How do you take their times from one step?

   :::answer[Worked solution]{tests="trace-step"}
   Search the sources for `ST_PROFILE_FUNCTION` and `ST_PROFILE_SCOPE`. In `Strata/src/Strata/Physics/PhysicsWorld.cpp`, `SyncEntitiesToBodies` and `WriteBackDynamicBodies` start with a profile scope of their own function, and `Simulate` wraps the library's call in a scope named `PhysicsWorld::Simulate - box3d`. In Tracy, select one `PhysicsSystem::OnFixedUpdate` zone and read the three child zones; the rest of the zone is the other stages. The world reports the same split in `PhysicsStats` (`SyncTime`, `LibraryStepTime`, `WriteBackTime`).
   :::

3. **Hard.** Run the pile test with 0 and 3 workers and compare the poses by hand: what do you change in the test to print them, and what do you expect?

   :::answer[Worked solution]{tests="determinism"}
   Run `StrataTests.exe --test-case="Identical runs produce identical results*"`. Copy the test, print each pose of `first` and `threaded` with full precision, run it and compare. You expect all 25 poses to match to the last digit, because ordered records, fixed chunks and the library's own guarantee leave nothing that depends on timing. A difference would mean a stage that depends on the order in which threads finish.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Physics/PhysicsSystem.cpp`: `OnUpdate`, `OnFixedUpdate`, `SyncGravity`.
- `Strata/src/Strata/Physics/PhysicsWorld.cpp`: `Simulate`, `SyncEntitiesToBodies`, `SyncBody`, `MarkMoved`, `WriteBackDynamicBodies`, `WritePose`, `Teleport`, `ApplyPendingForces`.
- `Strata/src/Strata/Physics/PhysicsTaskSystem.cpp`: the library's task callbacks.
- `StrataScriptCore/Include/StrataScript/Physics.h` and `StrataScriptCore/Include/StrataScript/ScriptABI.h`: the SDK and the host functions of bodies.
- Tests: `StrataTests/src/Physics/PhysicsSimulationTests.cpp`, `StrataTests/src/Physics/PhysicsBox3DTests.cpp`, `StrataTests/src/Physics/PhysicsLifecycleTests.cpp`.

## Further reading

- Glenn Fiedler, "Fix Your Timestep" (beginner): why a physics step has a fixed length.
- Erin Catto, the Box2D and box3d documentation (intermediate): the library's step, sub-steps, sleeping and its determinism notes.
- Jason Gregory, "Game Engine Architecture" (advanced): physics integration in an engine and the scene's link to it.
