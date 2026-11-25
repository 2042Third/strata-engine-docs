---
id: physics/contacts-triggers
title: "Contacts and triggers"
description: "How Strata tells game code when two entities start and stop touching, and when something enters or leaves a trigger, with one Begin and one End per pair."
kind: internals
size: L
tracks: [E]
needs: [physics/world-step, physics/collision-layers]
time: 85
learn:
  - id: fold
    text: explain why Strata folds the physics library's shape contacts into one Begin and one End per entity pair
  - id: count
    text: compute the Begin and End events that a sequence of shape contacts produces
  - id: delivery
    text: explain why events come after the step on the main thread and what a listener may do
  - id: balance
    text: explain why every Begin has exactly one End, also when an entity is destroyed or rebuilt
  - id: script
    text: write a trigger script with enter and exit callbacks and name what Strata does not report
since: 0.3.0
status: final
---

A game needs to know when things touch. A coin must vanish when the player reaches it, a door must open when someone stands in front of it, and a crate must thud when it hits the floor. Physics decides where bodies are, and game code decides what that means. This page covers the bridge between them: the events that say two entities **started** touching, or **stopped**, and that something entered or left a trigger. It does not cover how a script system calls a script's :term[callbacks]{id=callback} (see [the script system](../scripting/script-system.md)), the contacts of character controllers (see [character controllers](../physics/character-controllers.md)), or sounds that grow louder with harder hits (see [sound](../make/sound.md)).

## The problem and how engines solve it

Start with the goal basket of the Physics Playground, a sample scene. Balls roll down a ramp and fall through a funnel into a basket, and the game must count each ball that lands in it. The basket must not stop the balls: it is a zone, not a wall. What does the game ask the physics library, and when?

The first idea is to ask every frame. For each ball, the game tests whether the ball lies inside the basket and compares with the last frame. That works for one basket and ten balls. It fails for a scene of 615 bodies, because the game tests every body against every zone every frame, work the library has already done to find collisions. Asking again duplicates that work and misses touches that start and end between two asks.

The second idea is to let the library say it. Physics libraries solve this with two features, and Strata uses both.

A **trigger** is a :term[collider]{id=collider} that reports what overlaps it and has no collision response: bodies pass through it. Libraries often call the same thing a sensor. The library checks the zone's overlaps while it steps and keeps a list of what began and what stopped overlapping. Triggers give events and nothing else: no force, no bounce, no :term[contact point]{id=manifold} from the library.

A solid contact needs the other feature. When two solid shapes touch, the library creates a contact between them, and it reports the step in which the contact begins and the step in which it ends. A **collision event** is Strata's notification of such a change: a `Begin` when two entities start touching (or an entity enters a trigger) and an `End` when they stop.

Two details make the library's events awkward for game code. The first is shapes against entities. A bench has a seat and four legs, and the floor touches each leg.

The library reports a contact per pair of shapes, so the bench landing gives four Begin events, all for the same two entities. A script that plays a thud for each would play four. Game code thinks in entities, so someone must fold the shape events into one answer per pair of entities.

The second detail is timing. The library finds contacts inside its step, while it changes positions and velocities. If a script ran there and destroyed a body, the step would read freed memory.

Engines solve it in two ways: they queue the events and hand them out after the step, or they let scripts run inside the step and forbid most actions there. Strata queues.

There is also a cost. Tracking a contact costs memory and time for each pair, and most pairs in a scene (a floor under a thousand crates) matter to nobody. A good design tracks a pair only when someone wants its events.

Strata's answer has four parts:

- Triggers are `box3d` sensors, and solid contacts come from `box3d`'s contact events.
- Strata folds shape events into one **touching pair** per two entities: the tracked record of two entities that touch now, with a count of the shape contacts that hold them together.
- Events are queued during the step and delivered after it, on the :term[main thread]{id=main-thread}.
- **Contact interest** is a scene's list of entities whose contacts someone wants. Pairs that no one wants are not tracked, so a scene with no listener pays nothing.

## The map

The pieces sit in two files and one service. `PhysicsWorld.cpp` owns the library's world and the folding. `PhysicsSystem.cpp` owns the listeners and the dispatch. `SceneServices.h` declares the contract between them and every other system.

```mermaid caption="Events travel one way, from the library's step to the listeners that run after it." alt="A flow from the library step, through an event reader that folds contacts into pairs and a queue, to a dispatch after the step that calls listeners, among them the script system."
flowchart LR
    L["Library step: contacts, sensor visits"] --> P["Event reader: touching pairs"]
    P --> Q["Queue of events"]
    Q --> D["Dispatch after the step"]
    D --> S["Script system listener"]
    D --> T["Other listeners"]
```

Four things own the data. The library owns shapes, contacts and the lists of begin and end reports of its latest step, and clears them at its next step. The world owns the touching pairs and the queue. The physics system owns the listener list and the watch counts. The listeners own whatever they do with an event.

All of this runs on the main thread, which owns the scene (see [one step](../physics/world-step.md)).

## The contract

A script or a tool that uses events can rely on these rules. Each has a reason in the design above.

- **Events come after the step.** `PhysicsSystem` delivers them when the step is over, never from inside the library's step. The reason is the second detail above: nothing a listener does can corrupt a step.
- **Delivery runs on the main thread.** Listeners may use the whole scene and the physics application programming interface (API), including destroying entities and changing bodies. The reason is that the main thread owns the scene.
- **One Begin and one End per pair.** A pair begins with its first shape contact and ends with its last. The reason is that game code thinks in entities.
- **Every Begin has exactly one End.** Destroying an entity, removing its collider or making it inactive ends its pairs, with an `End` each; rebuilding its body ends them only if the new shapes stop touching. The one exception is that a scene that stops running throws its simulation away without events.
- **Listeners get events in registration order.** A listener added during a dispatch gets events from the next dispatch on. A listener removed during a dispatch is not called again, even for the rest of that dispatch.
- **Events carry the other entity, a point and a normal, never an impulse.** A `CollisionEvent` names both entities by `UUID`, so an `End` can name an entity that is already gone.

:::rule
Events wait until the step is over. A listener may destroy entities, and no code may change state that the step still reads. See [one step](../physics/world-step.md) for the order of a step.
:::

The scripts' side adds a small rule of its own: when a pair begins, a script receives `OnCollisionEnter` or, for a trigger, `OnTriggerEnter`. When it ends, the script receives `OnCollisionExit` or `OnTriggerExit`. All four receive the SDK's `Collision`, which holds the other entity, a point and a normal pointing from the script's entity toward the other.

## A toy version

The toy below counts shape contacts per entity pair and queues events until the step ends, as Strata does. It omits triggers, rebuilds, interest and the library. Entities are plain numbers. The pair key puts the smaller number first, so the pair of 1 and 0 is the same pair as 0 and 1.

:::question
If a class, a `std::map` or a call such as `std::printf(` is new to you, read [classes and calls](../basics/programming-3.md) and [maps and lambdas](../basics/cpp-generic.md) first.
:::

The program below has a bench with two legs and a ball, on a ground with number 0. It reports the events of three steps, so look at which steps print which pairs.

```cpp sketch="physics-contacts-triggers-toy.cpp"
// A toy of Strata's contact folding: shape contacts are counted per entity pair, and a pair begins
// with its first contact and ends with its last one. Events wait in a list until the step is over.

#include <cstdio>
#include <map>
#include <utility>
#include <vector>

struct Event
{
	bool IsBegin = true;
	int First = 0;
	int Second = 0;
};

class PairCounter
{
public:
	void CountBegin(int a, int b)
	{
		const auto key = MakeKey(a, b);
		if (m_Counts[key]++ == 0)
			m_Pending.push_back({ true, key.first, key.second });
	}

	void CountEnd(int a, int b)
	{
		const auto key = MakeKey(a, b);
		const auto it = m_Counts.find(key);
		if (it == m_Counts.end())
			return;
		if (--it->second == 0)
		{
			m_Pending.push_back({ false, key.first, key.second });
			m_Counts.erase(it);
		}
	}

	// The step is over: hand out the events and start a new list.
	std::vector<Event> Take()
	{
		std::vector<Event> events = std::move(m_Pending);
		m_Pending.clear();
		return events;
	}

private:
	static std::pair<int, int> MakeKey(int a, int b) { return a < b ? std::make_pair(a, b) : std::make_pair(b, a); }

	std::map<std::pair<int, int>, int> m_Counts;
	std::vector<Event> m_Pending;
};

int main()
{
	// Entity 0 is the ground, entity 1 a bench with two legs, entity 2 a ball.
	PairCounter counter;
	const int ground = 0;
	const int bench = 1;
	const int ball = 2;

	counter.CountBegin(bench, ground); // First leg lands.
	counter.CountBegin(ground, bench); // Second leg lands: same pair, no new event.
	counter.CountBegin(ball, ground);
	for (const Event& event : counter.Take())
		std::printf("step 1: %s %d-%d\n", event.IsBegin ? "Begin" : "End  ", event.First, event.Second);

	counter.CountEnd(bench, ground); // One leg lifts: the pair still touches.
	counter.CountEnd(ground, ball);
	for (const Event& event : counter.Take())
		std::printf("step 2: %s %d-%d\n", event.IsBegin ? "Begin" : "End  ", event.First, event.Second);

	counter.CountEnd(bench, ground); // The last leg lifts.
	for (const Event& event : counter.Take())
		std::printf("step 3: %s %d-%d\n", event.IsBegin ? "Begin" : "End  ", event.First, event.Second);
	return 0;
}
```

```text output-of="physics-contacts-triggers-toy.cpp"
step 1: Begin 0-1
step 1: Begin 0-2
step 2: End   0-2
step 3: End   0-1
```

1. **Line 22:** The first contact of a pair raises the count from 0 to 1 and queues the Begin; later contacts only raise it.
2. **Line 32:** The pair ends when the count falls to zero, so one lifted leg changes nothing.
3. **Lines 40–45:** `Take` hands the queued events out in one batch and starts a new list: events leave after the step.
4. **Line 48:** The smaller number goes first, so both orders name one pair.

The first step has three contacts and prints two events: the two legs fold into one pair. The second step ends a leg's contact, and the bench pair stays, because one contact is still counted. It ends only in step 3, with the last leg. That count is the whole idea. Everything else in the real code serves it: where the count lives, what happens when its owner changes, and how many pairs it must track.

## The real code

The real code keeps the toy's shape and adds the things a running game needs. Follow the data in the order it flows: the pair record, the counters, the reading of the library's reports, the interest, the points, the dispatch, and last the scripts.

### The touching pair

A pair holds the two entities, a count and the last known contact point. Search for the count and for the two fields that make removal fast.

```cpp src="Strata/src/Strata/Physics/PhysicsWorld.cpp#L419-L441"
// A pair of entities that touch, tracked while someone wants its contacts (see ICollisionEventSource). box3d reports a
// contact per pair of shapes (and per child of a compound or mesh) and a sensor visit per pair of a sensor shape and a
// visitor shape, so a pair counts them: it begins when its first contact begins and ends when its last one ends.
struct TouchingPair
{
	UUID A = UUID::Null();
	UUID B = UUID::Null();
	// Positions of the pair in the touching pairs of A and of B (PhysicsWorldData::EntityPairs), so that removing it
	// takes constant time.
	uint32_t IndexInA = 0;
	uint32_t IndexInB = 0;
	bool IsTrigger = false;
	// One of the entities' bodies was rebuilt since the pair began: its old shapes' contacts are gone, and the new shapes'
	// contacts of the next step confirm the pair, or it ends then (see ResolveRecheckedPairs).
	bool Unconfirmed = false;
	uint32_t ContactCount = 0;      // Shape contacts and sensor visits of the pair that touch now
	uint64_t CharacterStep = 0;     // Last step in which a character controller's move reported the pair
	uint64_t CheckStep = 0;         // Last step whose refresh visited the pair (see CollectCheckedPairs)
	uint64_t SortKey = 0;           // When the pair began (PhysicsWorldData::NextPairOrder): orders the ends of removals
	b3ContactId Contact = {};       // A contact of the pair, for the point of its End (null for triggers and characters)
	glm::vec3 Point = glm::vec3(0.0f);
	glm::vec3 Normal = glm::vec3(0.0f); // From A towards B
};
```

1. **Line 422:** A pair is a plain record of two entities and what the steps learned about them.
2. **Lines 428–429:** The pair's place in the two entities' lists, for constant-time removal.
3. **Line 433:** The flag of a pair that waits for a rebuilt body's new shapes.
4. **Line 434:** The count of shape contacts and sensor visits that touch now: the pair's life depends on it.
5. **Lines 438–440:** A contact, a point and a normal, kept so that the End has a point.

The toy had a map from pairs to counts. A `TouchingPair` keeps more, for reasons that each cost something.

- A pair names entities by `UUID`, not by handle, so that a pair stays after its entity is destroyed, long enough to report its `End`.
- `ContactCount` counts shape contacts and also sensor visits, the library's reports of a shape inside a sensor.
- `IndexInA` and `IndexInB` give the pair's place in the list of touching pairs of each entity. Removing a pair takes the last pair of that list and puts it in the freed place, so the list never shifts and a floor under thousands of boxes pays a constant cost per removal.
- `Unconfirmed` is the rebuild flag. A rebuilt body has new shapes, and the pair waits for the new shapes' first contacts instead of ending and beginning again.

The pair's end event takes its point from `Contact`, a contact that still exists, and from `Point` when none does. That is why an `End` carries the last known point.

### Counting a begin and an end

The two functions below are the toy's counter. Read `CountBegin` first, then `CountEnd`, and watch where the event is queued.

```cpp src="Strata/src/Strata/Physics/PhysicsWorld.cpp#L3596-L3609" symbol="CountBegin"
// One contact or visit of a pair began: the pair begins with it, or counts it (a pair that waited for a rebuilt body's
// new shapes is confirmed by it).
void CountBegin(PhysicsWorldData& data, UUID a, UUID b, bool trigger, const glm::vec3& point, const glm::vec3& normal, b3ContactId contact)
{
	if (a == b || !IsWanted(data, a, b))
		return;
	const PairKey key = MakePairKey(a, b);
	auto it = data.TouchingPairs.find(key);
	TouchingPair& pair = it != data.TouchingPairs.end() ? it->second : BeginPair(data, key, a, b, trigger, point, normal, contact);
	pair.ContactCount++;
	pair.Unconfirmed = false;
	if (B3_IS_NULL(pair.Contact) || !b3Contact_IsValid(pair.Contact))
		pair.Contact = contact;
}
```

1. **Line 3600:** A pair of an entity with itself, or one nobody wants, is dropped before any work.
2. **Line 3604:** The pair is found, or begun: only a new pair queues a `Begin`.
3. **Lines 3605–3606:** The contact is counted, and a pair that waited after a rebuild is confirmed.

`CountEnd` is the other half. Search for its last condition, which has three parts.

```cpp src="Strata/src/Strata/Physics/PhysicsWorld.cpp#L3611-L3625" symbol="CountEnd"
// One contact or visit of a pair ended: the pair ends with its last one, unless a character controller's move reported
// it in this step or it waits for a rebuilt body's new shapes.
void CountEnd(PhysicsWorldData& data, UUID a, UUID b)
{
	if (a == b)
		return;
	auto it = data.TouchingPairs.find(MakePairKey(a, b));
	if (it == data.TouchingPairs.end())
		return;
	TouchingPair& pair = it->second;
	if (pair.ContactCount > 0)
		pair.ContactCount--;
	if (pair.ContactCount == 0 && !pair.Unconfirmed && pair.CharacterStep != data.StepCount)
		EndPair(data, it);
}
```

1. **Lines 3621–3622:** The count goes down, never below zero.
2. **Line 3623:** The pair ends only at zero, when it is not waiting after a rebuild and no character move reported it in this step.

`CountBegin` refuses two cases that the toy ignored: a pair of an entity with itself (a body of several shapes), and a pair nobody wants (`IsWanted`). Then it finds the pair or begins a new one, and a new one queues the `Begin`. It counts the contact and clears `Unconfirmed`. A first contact of the new shapes confirms a rebuilt body's pair silently.

`CountEnd` has more conditions than the toy's single test. It ends the pair when the count reaches zero, and only if the pair is not `Unconfirmed` and no character controller reported the pair in this same step. Character controllers move through their own queries, so they have no solid contact that could keep a pair alive: their reports are the evidence that the pair holds (see [character controllers](../physics/character-controllers.md)).

:::example[A bench lands, lifts and a leg is rebuilt]
A bench has three legs and stands above the ground. A script on the bench makes its pairs wanted. Take the steps one at a time, with the pair of the bench and the ground, counted as in `CountBegin` and `CountEnd`.

In step 20 the library reports two Begin events, one for the left leg and one for the middle leg. The first creates the pair with count 1 and queues one `Begin`. The second raises the count to 2 and queues nothing. In step 21 the right leg lands: the count is 3, and still one `Begin` has been queued in all. The script receives one `OnCollisionEnter`, not three.

In step 60 a tool changes the bench's collider, so the body is rebuilt. Strata sets the count to 0 and `Unconfirmed` to true. Ends that the library reports for the old shapes do not end the pair.

The new shapes touch the ground in step 61, and `CountBegin` finds the pair, counts 3 contacts, and clears the flag. No `End` and no new `Begin` reaches the script. Had the new shapes not touched the ground, the pair would have ended after step 61 through `ResolveRecheckedPairs`, with one `End`.

Last, in step 90 the bench is pushed away and the three contacts end in steps 90, 90 and 91. The count goes 3, 2, 1 and then 0 in step 91, and only that step queues the `End`. One `Begin` and one `End`, so the script sees one enter and one exit.
:::

The figure below is the pair's life as a small state machine. A pair does not exist before its first contact. It is `Touching` while its count is above zero, and `Unconfirmed` from a rebuild until the next step shows contacts.

```mermaid caption="The life of a touching pair, from its first contact to its end. A rebuild makes it wait for the new shapes." alt="A state machine with the states touching and waiting. The first contact creates the pair with a Begin event, a rebuild moves it to waiting, and its last contact or a failed wait ends it with an End event."
stateDiagram-v2
    [*] --> Touching: first contact (Begin)
    Touching --> Touching: contact begins or ends, count above 0
    Touching --> Unconfirmed: body rebuilt, count reset
    Unconfirmed --> Touching: a new contact (no event)
    Touching --> [*]: last contact ends (End)
    Unconfirmed --> [*]: no contact by the step's end (End)
```

### Reading the library's reports

After each library step, `ProcessStepEvents` reads the lists of begin and end reports and folds them into pairs. The first half handles the ends. Look at the two flags, `anyTracked` and `anyWanted`, which decide whether a loop runs at all.

```cpp src="Strata/src/Strata/Physics/PhysicsWorld.cpp#L3664-L3680" from="const bool anyTracked = !data.TouchingPairs.empty();" to="CountEnd(data, sensor->Entity, visitor->Entity);" symbol="ProcessStepEvents"
const bool anyTracked = !data.TouchingPairs.empty();
const bool anyWanted = data.TrackAll || !data.ContactInterest.empty();
for (int index = 0; anyTracked && index < contactEvents.endCount; index++)
{
	const b3ContactEndTouchEvent& event = contactEvents.endEvents[index];
	const ShapeSlot* a = ResolveShape(data, event.shapeIdA);
	const ShapeSlot* b = ResolveShape(data, event.shapeIdB);
	if (a && b)
		CountEnd(data, a->Entity, b->Entity);
}
for (int index = 0; anyTracked && index < sensorEvents.endCount; index++)
{
	const b3SensorEndTouchEvent& event = sensorEvents.endEvents[index];
	const ShapeSlot* sensor = ResolveShape(data, event.sensorShapeId);
	const ShapeSlot* visitor = ResolveShape(data, event.visitorShapeId);
	if (sensor && visitor && !(sensor->BodyType == RigidBodyType::Static && visitor->BodyType == RigidBodyType::Static))
		CountEnd(data, sensor->Entity, visitor->Entity);
```

1. **Lines 3664–3665:** Two flags decide whether a loop runs at all: something tracked, for the ends, and something wanted, for the begins.
2. **Lines 3668–3672:** Both shapes resolve to entities; a report that names a gone shape is skipped.
3. **Lines 3674–3680:** Sensor ends skip pairs of two :term[static bodies]{id=static-body}.

Ends run before begins, within each step. When a body leaves one contact and enters another in the same step, the old pair ends before the new one begins, so a script never holds two contacts that the physics scene does not. Strata also reads the library's end reports only when at least one pair is tracked, and the begin reports only when something is wanted. Reading a report means resolving two shapes through the world's slot tables, and with no listener that work would be wasted.

A report can name a shape that is gone: a destroyed entity's shapes. `ResolveShape` then returns nothing, and the report is skipped. This is safe because removing an entity ended its pairs already, in `EndContactsOf`, which queues the ends in the order the pairs began.

The second half handles sensors, the trigger side. Here the static-static rule appears.

```cpp src="Strata/src/Strata/Physics/PhysicsWorld.cpp#L3694-L3708" from="for (int index = 0; anyWanted && index < sensorEvents.beginCount; index++)" to="CountBegin(data, sensor->Entity, visitor->Entity, true, point, normal, b3ContactId {});" symbol="ProcessStepEvents"
for (int index = 0; anyWanted && index < sensorEvents.beginCount; index++)
{
	const b3SensorBeginTouchEvent& event = sensorEvents.beginEvents[index];
	const ShapeSlot* sensor = ResolveShape(data, event.sensorShapeId);
	const ShapeSlot* visitor = ResolveShape(data, event.visitorShapeId);
	// Neither body moves (a static trigger and a static collider or static trigger): no pair, as in the physics
	// engines whose triggers only detect what can move into them.
	if (!sensor || !visitor || (sensor->BodyType == RigidBodyType::Static && visitor->BodyType == RigidBodyType::Static))
		continue;
	if (sensor->Entity == visitor->Entity || !IsWanted(data, sensor->Entity, visitor->Entity))
		continue;
	glm::vec3 point;
	glm::vec3 normal;
	ComputeTriggerPoint(event.sensorShapeId, event.visitorShapeId, point, normal);
	CountBegin(data, sensor->Entity, visitor->Entity, true, point, normal, b3ContactId {});
```

1. **Lines 3701–3702:** Static against static makes no pair.
2. **Line 3703:** An entity against itself, or a pair nobody wants, is dropped.
3. **Lines 3705–3708:** The library gives no point, so one is computed, and the pair begins as a trigger.

A static trigger and a static collider can never meet, since neither moves into the other, so Strata drops such pairs and the library's reports of them. A trigger sees dynamic and :term[kinematic bodies]{id=kinematic-body} and characters. It does not see triangle meshes: the library's sensors test :term[convex]{id=convex} shapes only, and `Docs/Roadmap.md` lists this.

A trigger's `IsTrigger` flag is set from the body component: Strata makes the shape a sensor and turns its contact events off. Every shape lets sensors see it, so a ball needs no setting to be seen.

### Wanting a pair

Whether a pair is wanted comes from two sources. A listener of the scope `AllEntities` wants every pair, and `SetTrackAllContacts` enables that. A listener of the scope `WatchedEntities` wants pairs where at least one entity is watched, and `WatchCollisions` adds a watch. Watches add up: an entity is watched until each `WatchCollisions` has its `UnwatchCollisions`.

The script system uses a `WatchedEntities` listener. It watches an entity exactly when a script on it implements one of the four callbacks. A scene whose scripts implement none, with no other listener, tracks no pairs, and `ProcessStepEvents` skips both loops.

A pair can become wanted while its bodies already touch. The library reported that contact's Begin while nobody wanted the pair, and Strata dropped it, so no Begin will come again. `SeedWantedPairs` therefore looks at the library's contacts and sensors for such pairs and begins them after the next step. The reverse also holds: a pair nobody wants any more ends at the next step, through `EndUnwantedPairs`, so every Begin keeps its End.

### The point and the normal

An event carries a point, and the library gives it for solid contacts only. For a solid contact Strata takes the point halfway between the two surfaces, averaged over the points of the contact's first manifold (the library's set of touch points). The normal points from the first shape toward the second. For a trigger the library reports no point, so `ComputeTriggerPoint` takes the centre of the overlap of the two shapes' :term[bounding boxes]{id=bounding-box}. Its normal points from the trigger's box centre to the visitor's.

Those boxes are loose around curved shapes, so a trigger's point is a good guess, not a contact. The goal basket passes that point to its score display, and a script that needs more can read the ball's own position.

### The dispatch

When the step is over, the physics system takes the queue out of the world and gives each event to the listeners.

```cpp src="Strata/src/Strata/Physics/PhysicsSystem.cpp#L636-L660" symbol="PhysicsSystem::DispatchCollisionEvents"
void PhysicsSystem::DispatchCollisionEvents()
{
	if (!m_World)
		return;

	const std::vector<CollisionEvent> events = m_World->TakeCollisionEvents();
	if (events.empty() || m_CollisionListeners.empty())
		return;

	ST_PROFILE_FUNCTION();

	// Listeners may add or remove listeners while being called; iterate over a snapshot.
	const std::vector<Ref<CollisionListener>> listeners = m_CollisionListeners;
	for (const CollisionEvent& event : events)
	{
		// Watches may change during the dispatch too; each event is judged when its turn comes.
		const bool watched = IsWatchingCollisions(event.AID) || IsWatchingCollisions(event.BID);
		for (const Ref<CollisionListener>& listener : listeners)
		{
			if (listener->Removed || (listener->Scope == CollisionListenerScope::WatchedEntities && !watched))
				continue;
			listener->Callback(event);
		}
	}
}
```

1. **Line 641:** The queue leaves the world, and each event's entity handles are found now.
2. **Line 648:** A copy of the listener list, so that callbacks may change the list.
3. **Line 652:** The watches are read when the event's turn comes.
4. **Line 655:** A listener removed meanwhile is skipped.

The function checks three guards. Nothing runs when the queue is empty or when no one listens. The loop runs over a copy of the listener list, because a callback may add or remove listeners, and a removed listener keeps a `Removed` flag that the loop tests before each call. The watch test sits inside the loop, so a callback that stops watching an entity changes what the next event reaches.

`TakeCollisionEvents` also turns each `UUID` into an entity handle immediately before the dispatch. If the entity was destroyed in between, the handle is invalid, and the `UUID` still names it. A listener that needs the entity must test the handle.

### The scripts

The script system's listener maps each event to a callback and calls it for both sides.

```cpp src="Strata/src/Strata/Scripting/ScriptSystem.cpp#L314-L322" symbol="ScriptSystem::OnCollision"
void ScriptSystem::OnCollision(const CollisionEvent& event)
{
	const bool begin = event.Type == CollisionEventType::Begin;
	ScriptCallback callback = begin ? ScriptCallback::OnCollisionEnter : ScriptCallback::OnCollisionExit;
	if (event.IsTrigger)
		callback = begin ? ScriptCallback::OnTriggerEnter : ScriptCallback::OnTriggerExit;
	DeliverContact(event.AID, event.BID, begin, callback, event.Point, event.Normal);
	DeliverContact(event.BID, event.AID, begin, callback, event.Point, -event.Normal);
}
```

A trigger event becomes `OnTriggerEnter` or `OnTriggerExit`, and a solid one `OnCollisionEnter` or `OnCollisionExit`. The second call flips the normal, so each script sees the normal pointing away from its own entity. `DeliverContact` also keeps a set of entities each script instance was told about, so a script that was told of a Begin gets the End, even if it was made inactive since. Delivery is in [the script system](../scripting/script-system.md).

The Physics Playground's basket is the smallest useful trigger script. It counts each ball once.

```cpp src="Samples/PhysicsPlayground/Scripts/GoalBasket.cpp#L1-L26"
// The goal's basket: a trigger under the funnel that counts every ball that falls into it, once.

#include "Playground.h"

#include <cstdint>
#include <unordered_set>

using namespace Strata;

class GoalBasket : public Script
{
public:
	void OnTriggerEnter(const Collision& collision) override
	{
		if (!collision.Other.IsValid() || collision.Other.GetTag() != "Ball" || !m_Counted.insert(collision.Other.GetID()).second)
			return;
		if (Playground* playground = Scene::FindEntityByName("Game").GetScript<Playground>())
			playground->AddScore(collision.Point);
	}
private:
	std::unordered_set<uint64_t> m_Counted; // Balls already counted, so one that bounces out and back counts once
};

ST_SCRIPT_CLASS(GoalBasket)
{
}
```

1. **Line 13:** The engine calls this when a ball starts overlapping the trigger.
2. **Lines 15–16:** Anything invalid, not tagged `Ball`, or already in the set, is ignored; `insert` reports whether the ball is new.
3. **Lines 17–18:** The score display gets the event's point.
4. **Line 21:** The set remembers counted balls.

The script ignores anything that is not a ball, and it remembers counted balls in a set, so that a ball that bounces out and back counts once. The set is needed because the engine reports every enter, and a ball that leaves and enters again is two pairs in a row. The launch pad is shorter still, and it uses the collision's `Other` to act on the body that touched it.

```cpp src="Samples/PhysicsPlayground/Scripts/LaunchPad.cpp#L1-L22"
// The launch pad at the top of the ramp: a trigger that sends every ball touching it down the ramp toward the pins.

#include "StrataScript/StrataScript.h"

using namespace Strata;

class LaunchPad : public Script
{
public:
	glm::vec3 LaunchVelocity = glm::vec3(9.0f, 1.0f, 0.0f);

	void OnTriggerEnter(const Collision& collision) override
	{
		if (collision.Other.IsValid() && collision.Other.GetTag() == "Ball")
			collision.Other.GetRigidBody().SetLinearVelocity(LaunchVelocity);
	}
};

ST_SCRIPT_CLASS(LaunchPad)
{
	ST_SCRIPT_FIELD(LaunchVelocity);
}
```

1. **Line 10:** A field of the script, set in the editor.
2. **Lines 12–15:** On entering, a ball gets the launch velocity.
3. **Lines 19–22:** The registration exposes the field.

Both scripts test `collision.Other.IsValid()` first, because the other entity can be destroyed already when a callback runs.

## What Strata does not report

Three things are missing, and each is on purpose or listed in `Docs/Roadmap.md`.

- Triggers do not see triangle-mesh colliders. Put a convex collider on whatever must trigger.
- There is no stay event. Scripts get Enter and Exit, no `OnCollisionStay`. A script that needs per-step logic keeps a flag in `OnTriggerEnter` and clears it in `OnTriggerExit`, and works in `OnFixedUpdate`.
- A contact carries no impulse and no impact speed, because Strata does not use `box3d`'s hit events. The Playground's impact sounds measure a hit from the bodies' velocities along the normal, which is available at `OnCollisionEnter` since the contact is reported after the step that solved it.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Report every shape contact | Libraries' raw events | No pair counts, no folding code | A script gets four Begin events for one bench |
| Poll overlaps each frame | Simple games | No event machinery | Work for every body each frame, and missed touches between asks |
| Callbacks inside the step | Some engines, with restrictions | Events at the moment of contact, with exact impulses | Scripts must not change bodies there; crashes if they do |
| Track every pair always | Tools that record all contacts | No seeding when a listener appears | Memory and time for pairs nobody wants |
| Stay events every step | Many engines | Per-step contact logic in the engine | A call for each touching pair each step |
| Impulses from hit events | Many engines | Hard-hit effects without velocity math | Extra library work for every contact |

## How it is tested

The suites live in `StrataTests/src/Physics/` and run with the other physics tests. `PhysicsEventTests.cpp` holds the behavior of the events, and `PhysicsBox3DBehaviorTests.cpp` the folding.

- `Trigger volumes report balanced Begin and End events`: a ball falls through a static trigger and passes it. It counts one Begin and one End, a point inside the trigger, and no collision response.
- `A body of several shapes touching another body begins one contact`: a bench with three legs lands. One Begin, no End, one pair in the statistics.
- `Destroying a touching entity ends its contacts`: the End arrives with the entity's `UUID` and an invalid handle, and in the end every Begin has an End.
- `Rebuilding a touching body reports neither End nor Begin`: the case of `Unconfirmed`.
- `Listeners can be removed, also while events are dispatched` and `Listeners may destroy entities while handling events`: the dispatch rules.
- `Begin and End stay balanced in a busy scene`: the invariant under load.

The tests record events with `CollisionRecorder` from `PhysicsTestUtils.h`, which registers a listener and counts events by type and pair. A test steps the scene by a count of steps with `StepScene`, never by frames. Run them from the build folder with the doctest filter, for example `StrataTests --test-suite=Physics*`.

## Changing it safely

Extend events through the registries and services, not by calling into the physics world. A new consumer registers a listener through `ICollisionEventSource` and chooses the narrowest scope: `WatchedEntities` plus a watch costs nothing for entities no one watches, and `AllEntities` makes every pair tracked.

Keep these rules when you change the code.

- A change to folding keeps the invariant that every Begin has exactly one End. Test it with a body that is destroyed, made inactive and rebuilt while touching, and keep `Begin and End stay balanced in a busy scene` passing.
- Keep ends before begins within a step, and keep the pairs' removal in the order they began (`SortKey`), so event order does not depend on :term[hash]{id=hash} order.
- Nothing in `ProcessStepEvents` may call a listener. Events wait in the queue until the step is over.
- Keep the constant-time pair removal: a change that scans a list per removal makes a floor under thousands of boxes cost more with each pair.
- A new thing the physics reports every frame stays :term[constant time]{id=constant-time}, and a pair nobody wants stays free.
- When you add a script callback, append it at the end of the script class description (see [the script system](../scripting/script-system.md)), and cover it in the feature test.

## Summary

- Strata folds the library's shape contacts into one Begin and one End per pair of entities, so a script reacts once to a bench landing on its four legs.
- A pair counts its contacts: it begins with the first, ends with the last, and a rebuilt body marks its pairs as waiting instead of ending them.
- Events wait in a queue and go to the listeners after the step on the main thread, so a listener may destroy entities or call the physics API.
- Every Begin has exactly one End, also for a destroyed or inactive entity, and a scene that stops running throws its simulation away without events.
- A trigger script implements `OnTriggerEnter` and `OnTriggerExit`; Strata reports no stay events, no impulse, and no triangle-mesh triggers.

## Check yourself

1. A bench stands on a floor with four legs, each a box collider on the bench's body. All four legs land in one step. How many `Begin` events does a script on the bench receive?

   A. Four, one per leg.

   B. One, because the four contacts fold into one touching pair.

   C. None, because a body of several shapes reports nothing.

   D. Two, one for the bench and one for the floor.

   :::answer{tests="fold"}
   B is right. The library reports four shape contacts, and the pair counts them: it begins with the first and queues one event. A describes the library's raw reports. C is wrong, since a pair of two different entities is tracked. D is wrong: the floor's script, if it has one, gets its own event for the same pair, but the bench gets one.
   :::

2. A ball touches a floor with three contacts that begin in steps 1, 1 and 2, and end in steps 5, 6 and 6. Which events are queued, and in which steps?

   :::answer{tests="count"}
   One `Begin` in step 1, from the first contact (the count goes 1, 2 and then 3 in step 2 with no new event). The count goes 2 in step 5, 1 and then 0 in step 6, so one `End` is queued in step 6, and none in step 5.
   :::

3. A listener destroys the entity that a contact event names, in the middle of a dispatch of ten events. Which events can still reach it, and what must the listener check?

   :::answer{tests="delivery"}
   Events that name the destroyed entity can still come, because the queue is already full, and an `End` is queued for it by the destruction. The entity's `UUID` still names it, but its handle is invalid, so the listener tests the handle before it reads components. The dispatch is safe because it runs after the step, over a copy of the listeners.
   :::

4. A ball is inside a trigger when you destroy it. Does the trigger's script see an exit, and why does the design want one?

   :::answer{tests="balance"}
   Yes. Removing the ball's body ends every pair it is in (`EndContactsOf`), the `End` is queued, and the script receives `OnTriggerExit`, even though the ball's entity is gone. A script that counts the balls in the basket keeps a correct count only if each enter is matched by an exit.
   :::

5. A script needs to do something every step while a ball is in its trigger. There is no `OnTriggerStay`. Which two callbacks and which other one does the script combine?

   :::answer{tests="script"}
   `OnTriggerEnter` sets a flag (or adds the ball to a set), `OnTriggerExit` clears it, and `OnFixedUpdate` does the work each :term[fixed step]{id=fixed-step} while the flag is set. The engine reports pairs, not steps of a pair.
   :::

## Exercises

1. **Basic.** Trace it yourself. Put breakpoints in `CountBegin` and `CountEnd`, and drop a body of two box colliders on the ground in a doctest. Report how many shape contacts, touching pairs and Begin events you see.

   :::answer[Worked solution]{tests="fold,count"}
   The code is `CountBegin` and `CountEnd` in `Strata/src/Strata/Physics/PhysicsWorld.cpp`. Install a listener first, for example with `CollisionRecorder`, because with no listener nothing is wanted and `ProcessStepEvents` never calls `CountBegin`. The `CountBegin` breakpoint hits twice, once per box, and `CountEnd` does not hit while the body rests. The first hit creates the pair in `BeginPair` and queues the event, and the second only raises `ContactCount` to 2. The result is two shape contacts, one touching pair and one Begin.
   :::

2. **Medium.** Run the toy's rule for an entity that is destroyed while touching. Extend `PairCounter` with `Remove(entity)` that ends every pair the entity is in. Predict the output for the sequence in the solution, then run it.

   :::answer[Worked solution]{tests="balance,count" solution="sketches/physics-contacts-triggers-removal.cpp"}
   Entity 5 touches the trigger 0 twice and entity 6 touches it once, so the pairs 0-5 and 0-6 begin. `Remove(5)` finds pair 0-5 and ends it, so the output has a Begin and an End for 0-5. The late `CountEnd(0, 5)` finds no pair and does nothing, as in the real `CountEnd`. Pair 0-6 ends with its single contact.

   ```cpp sketch="physics-contacts-triggers-removal.cpp"
   // The toy with one more rule: an entity that leaves the simulation ends every pair it is in,
   // so every Begin still gets exactly one End.

   #include <cstdio>
   #include <map>
   #include <utility>
   #include <vector>

   class PairCounter
   {
   public:
   	void CountBegin(int a, int b)
   	{
   		const auto key = MakeKey(a, b);
   		if (m_Counts[key]++ == 0)
   			std::printf("Begin %d-%d\n", key.first, key.second);
   	}

   	void CountEnd(int a, int b)
   	{
   		const auto key = MakeKey(a, b);
   		const auto it = m_Counts.find(key);
   		if (it == m_Counts.end())
   			return;
   		if (--it->second == 0)
   		{
   			std::printf("End   %d-%d\n", key.first, key.second);
   			m_Counts.erase(it);
   		}
   	}

   	// The entity is destroyed while touching: its contacts will never report an end.
   	void Remove(int entity)
   	{
   		for (auto it = m_Counts.begin(); it != m_Counts.end();)
   		{
   			if (it->first.first == entity || it->first.second == entity)
   			{
   				std::printf("End   %d-%d (removed)\n", it->first.first, it->first.second);
   				it = m_Counts.erase(it);
   			}
   			else
   				++it;
   		}
   	}

   private:
   	static std::pair<int, int> MakeKey(int a, int b) { return a < b ? std::make_pair(a, b) : std::make_pair(b, a); }

   	std::map<std::pair<int, int>, int> m_Counts;
   };

   int main()
   {
   	PairCounter counter;
   	counter.CountBegin(0, 5); // Entity 5 touches the trigger 0 with two shapes.
   	counter.CountBegin(5, 0);
   	counter.CountBegin(0, 6);
   	counter.Remove(5);
   	counter.CountEnd(0, 6);
   	counter.CountEnd(0, 5); // A late End of the removed entity finds no pair and is ignored.
   	return 0;
   }
   ```

   ```text output-of="physics-contacts-triggers-removal.cpp"
   Begin 0-5
   Begin 0-6
   End   0-5 (removed)
   End   0-6
   ```

   1. **Line 33:** `Remove` walks every pair of the toy.
   2. **Line 37:** A pair matches when the entity is either of its two numbers.
   3. **Line 40:** `erase` returns the next position, so the loop stays valid.
   4. **Line 61:** A late end finds no pair and is ignored.
   :::

3. **Hard.** Write a doctest that checks that a second ball, destroyed while it is inside a static trigger, still ends its pair, so that every Begin has its End. Say which helpers you use and what you check.

   :::answer[Worked solution]{tests="balance,script"}
   Build the scene as `Trigger volumes report balanced Begin and End events` does: a static trigger box with `IsTrigger` set, and two dynamic spheres placed inside it. Start the scene, create a `CollisionRecorder` from the scene's physics system, and step a few times with `StepScene` until two Begin events have arrived. Destroy the second ball through the scene, step once more, and check that the recorder holds one End for the pair of the trigger and that ball. Check last that `Count(Begin)` equals `Count(End)` after you also let the first ball fall out. Run the test once with the call of `EndContactsOf` removed to see it fail.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Physics/PhysicsWorld.cpp`: `TouchingPair`, `CountBegin`, `CountEnd`, `ProcessStepEvents`, `ReadContactPoint`, `ComputeTriggerPoint`, `MarkPairsUnconfirmed`, `SeedWantedPairs`.
- `Strata/src/Strata/Physics/PhysicsSystem.cpp`: the listener list, the watches and `DispatchCollisionEvents`.
- `Strata/src/Strata/Scene/SceneServices.h`: `CollisionEvent` and `ICollisionEventSource`.
- `Strata/src/Strata/Scripting/ScriptSystem.cpp`: `OnCollision` and `DeliverContact`.
- `StrataScriptCore/Include/StrataScript/Script.h`: the four callbacks.
- `Samples/PhysicsPlayground/Scripts/`: `GoalBasket.cpp`, `LaunchPad.cpp` and `Impact.cpp`.
- `StrataTests/src/Physics/PhysicsEventTests.cpp` and `PhysicsTestUtils.h`: the tests and `CollisionRecorder`.

## Further reading

- Erin Catto, the `box3d` and Box2D documentation on contact and sensor events: what the library reports and when (intermediate).
- Christer Ericson, "Real-Time Collision Detection": contact manifolds and pair management (advanced).
