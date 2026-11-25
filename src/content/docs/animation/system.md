---
id: animation/system
title: "The Animation system"
description: "How Strata plays the animators of a running scene in parallel, publishes the results in a fixed order, and offers poses and events through scene services."
kind: internals
size: L
tracks: [E]
needs: [animation/blending, animation/root-motion, world/systems, core/jobs, assets/residency]
time: 85
learn:
  - id: threads
    text: name which thread does each phase of one animation update and what it reads and writes
  - id: determinism
    text: explain why the update gives the same bytes on 0, 1 or 7 threads
  - id: assets
    text: predict what a character shows while its skeleton, controller or clips are missing
  - id: attachments
    text: compute what an attachment writes to its entity and when it writes nothing
  - id: services
    text: trace how a renderer, a script and a listener reach animation without including its module
since: 0.3.0
status: final
---

Strata plays a character in four steps. Time advances, the controller decides which clip plays, the clip gives a pose, and the :term[renderer]{id=renderer} skins the mesh with that pose. The Animation system does the first three steps for all animators of a playing scene, once per frame, and hands the pose to the renderer for the fourth. It keeps one record for each animator, shares loaded assets between animators that use the same ones, and spreads the work over the cores.

The system is also the only place where animation changes the scene: :term[root motion]{id=root-motion}, attachments and events all leave it from the :term[main thread]{id=main-thread}, in a fixed order. Through three :term[scene services]{id=scene-service} it is the module's face to the renderer, the scripts and the editor. It does not decide what a state machine means, how a clip blends, or which poses nobody sees; other pages teach those.

## The problem and how engines solve it

A game can hold a thousand animated characters, and each needs a pose every frame. At 60 :term[frames per second]{id=frame-rate} a frame lasts 16.7 ms, and animation gets a small share of it. One core cannot finish a thousand poses in that share, so the work must spread over the cores. The [job system](../core/jobs.md) gives that: a loop is cut into batches and every thread takes batches. The hard part starts after the loop is cut.

Three questions follow. Who may write what? If two threads write the same data, the result depends on their timing, and the bug appears once in a thousand runs. When do the results reach the scene? Scripts, physics and listeners read the scene, and a half-finished frame is a wrong frame.

In which order? If four animators fire an event in the same frame, a script that plays four sounds must hear them in the same order every time. Otherwise a replay of the game differs from the original.

Engines answer in three ways. The first puts a lock around the shared state: each job takes the lock and writes straight into the scene. The code is short, but jobs wait on each other, and the order of the writes still follows the order in which threads win the lock.

The second gives each system a thread of its own and sends messages between them. The [job system page](../core/jobs.md) explains why Strata keeps one thread in charge of the scene instead. The third gives every unit of work its own data, lets jobs write only there, and applies the results to the shared world later, in one fixed order, on one thread.

Strata takes the third way. The data of one unit is the **animator record**: one record for each animator, which holds its playing state, its pose and the events of the current update. A job reads the scene and the shared assets and writes only its own record. Then the main thread walks the records in a fixed order and publishes what each one holds.

The price is that nothing a job computes is visible to the scene until the walk, and that the walk itself runs on one thread. The gain is a result that does not depend on how many threads ran, so one test can compare a run on seven threads with a run on none, :term[byte]{id=byte} for byte.

## The map: layers, frame and threads

The module is a layer above Scene. It may include Core, Asset, Reflection and Scene, and no other layer. Only the Engine layer and the asset pipeline include it. The Engine registers it. The pipeline needs it because the glTF :term[importer]{id=importer} writes skeletons and clips and the dependency scanner reads the clips of a controller.

The renderer and the script host never include it. They meet it through scene services, defined in the Scene layer. A build can leave the module out with the :term[CMake]{id=cmake} option `STRATA_WITH_ANIMATION`.

```mermaid caption="The Animation layer sits above Scene, and only the Engine and asset pipeline layers include it; renderers and scripts reach it through services in the Scene layer." alt="A box for the Animation layer with arrows down to Core, Asset, Reflection and Scene. Boxes for the Engine layer and the asset pipeline layer have arrows to the Animation box. Boxes for the renderer and the script host have dashed arrows to a services box in the Scene layer, and the Animation box has a dashed arrow to the same services box."
flowchart TB
  Engine --> Animation
  AssetPipeline --> Animation
  Animation --> Scene
  Animation --> Asset
  Animation --> Reflection
  Animation --> Core
  Renderer -.-> Services["Scene services"]
  Scripting -.-> Services
  Animation -.-> Services
  Services --- Scene
```

In the frame, the system sits between the scripts and physics. Scripts set parameters and play states in their update. Animation then reads those parameters, advances every animator by the frame's :term[delta time]{id=delta-time} and moves entities by their root motion. Physics steps next, so a body that animation moved is where the step expects it.

The system runs only in Play mode. A scene that plays gets one; a scene that does not play has none, and the editor installs a separate preview for it.

```mermaid caption="One frame: scripts set parameters, animation steps and publishes, physics steps with the moved bodies, and the renderer reads the poses." alt="Four boxes in a row joined by arrows: scripts, animation, physics and renderer. A note under scripts says it sets parameters and plays states. A note under animation says it moves entities by root motion. A note under the renderer says it reads poses through a service."
flowchart LR
  Scripts["Scripts: set parameters"] --> Animation["Animation: step and publish"]
  Animation --> Physics["Physics: step"]
  Physics --> Renderer["Renderer: reads poses"]
```

The update itself crosses threads. The main thread resolves assets, then a first parallel loop classifies and steps records. The main thread then brings the few records that need it up to date, a second parallel loop steps those, and the main thread publishes, places attachments and dispatches events. The diagram shows who does what and what each phase writes.

```mermaid caption="One update across threads: the main thread frames the work, and the two parallel loops write only into records." alt="A diagram with a main thread lane and a worker threads lane. The main thread resolves asset sets, then workers classify and step records in batches of eight. The main thread then brings queued records up to date in record order, workers step those, and the main thread publishes poses, root motion, attachments and events in record order."
sequenceDiagram
  participant M as Main thread
  participant W as Worker threads
  M->>M: resolve asset sets (writes sets)
  M->>W: loop 1, batches of 8
  W->>W: classify, step in place (write own record)
  W-->>M: all batches done
  M->>M: synchronize queued records, in order
  M->>W: loop 2, batches of 8
  W->>W: step (write own record)
  W-->>M: all batches done
  M->>M: publish, attach, dispatch (write the scene)
```

## The contract

Callers and neighbours may rely on a few rules, and each has a reason.

- **The system runs in Play mode only.** Scripts, audio and animation all skip Simulate. Without a system no service is registered, so code that asks for a service gets null and must test for it. The reason is cost and meaning: Simulate runs the physics of a scene without the game's logic.
- **Jobs write only their own record.** Everything else is read-only while the jobs run. The reason is :term[determinism]{id=determinism}: a record has one writer, so no timing can change the bytes in it.
- **Animation changes the scene in three places, all on the main thread, after both loops:** root motion, attachments and events. The reason is that the scene may be read by listeners the moment it changes, so it changes only when every record is complete.
- **Events are dispatched after all poses, outside the jobs, over a snapshot of the listeners.** A listener may destroy an animator or add a listener; doing so in the middle of the loops would break the records.
- **Hold handles, request every update, never block.** The system holds :term[asset handles]{id=asset-handle}, asks for the assets each update, and never waits for a load. The reason is that an asset may arrive late, change or fail, and a frame must not wait for it.
- **Joints are not entities.** A pose is an array of matrices in a record. The reason is cost: a skeleton of 60 joints as entities would add 60 transform updates to every animator in every frame.

:::rule[Only scene services cross the module's boundary]
Other modules reach animation through `ISkinningPoses`, `IAnimatorControl` and `IAnimationEventSource`, and only the Engine and asset pipeline layers include the module. The reason is that the layer rules of the engine forbid a renderer or a script host from depending on a module above Scene. See [Layers, registries and the composition root](../core/layers-registries.md).
:::

:::rule[Animation is parallel and deterministic]
Evaluation jobs write only their animator's record. The main thread makes every change to the scene afterwards. Root motion moves entities only in `AnimationSystem::ApplyRootMotion`. The reason is one result on every machine and every thread count. See [Threads and the job system](../core/jobs.md).
:::

## A toy version

Before the real code, a system of about eighty lines does the same job on one thread. It keeps a list of records, steps each record, publishes in record order and dispatches events over a snapshot of its listeners. It has no assets, no state machine and no threads, and it shows the order of work that the real system keeps.

```cpp sketch="animation-system-toy.cpp"
// A toy animation system on one thread: records, a step per record, an ordered publish, then event dispatch.
#include <algorithm>
#include <cstdio>
#include <functional>
#include <utility>
#include <vector>

struct Clip
{
	float Duration;
	float EventTime;
	float Travel;
};

struct Record
{
	int Entity = 0;
	const Clip* Source = nullptr;
	bool Removed = false;
	float Time = 0.0f;
	float Pose = 0.0f;
	float RootMove = 0.0f;
	bool EventFired = false;
	int PoseVersion = 0;
};

struct Event
{
	int Entity;
	float Time;
};

class ToySystem
{
public:
	std::vector<float> Positions = std::vector<float>(2, 0.0f);
	std::vector<std::function<void(const Event&)>> Listeners;

	void Add(int entity, const Clip* clip)
	{
		Record record;
		record.Entity = entity;
		record.Source = clip;
		m_Records.push_back(record);
	}

	void Remove(int entity)
	{
		for (Record& record : m_Records)
			record.Removed = record.Removed || record.Entity == entity;
	}

	void Update(float deltaTime)
	{
		std::erase_if(m_Records, [](const Record& record) { return record.Removed; }); // Keeps the order of the rest.
		for (Record& record : m_Records)
			Step(record, deltaTime);
		for (Record& record : m_Records) // Publish in record order.
		{
			record.PoseVersion++;
			if (record.EventFired)
				m_Pending.push_back({ record.Entity, record.Time });
			Positions[record.Entity] += record.RootMove; // Root motion last.
			std::printf("  entity %d: pose %.2f, position %.2f\n", record.Entity, record.Pose, Positions[record.Entity]);
		}
		const std::vector<Event> events = std::move(m_Pending);
		m_Pending.clear();
		const auto listeners = Listeners; // A snapshot: a listener may change the list.
		for (const Event& event : events)
			for (const auto& listener : listeners)
				listener(event);
	}

private:
	void Step(Record& record, float deltaTime) const
	{
		const Clip& clip = *record.Source;
		const float before = record.Time;
		record.Time = std::min(before + deltaTime, clip.Duration);
		record.EventFired = before < clip.EventTime && record.Time >= clip.EventTime;
		record.Pose = 90.0f * record.Time / clip.Duration;
		record.RootMove = clip.Travel * (record.Time - before) / clip.Duration;
	}

	std::vector<Record> m_Records;
	std::vector<Event> m_Pending;
};

int main()
{
	const Clip wave { 1.0f, 0.5f, 2.0f };
	const Clip swing { 2.0f, 0.5f, 4.0f };
	ToySystem system;
	system.Add(0, &wave);
	system.Add(1, &swing);
	system.Listeners.push_back([](const Event& event) { std::printf("  event: entity %d at %.2f\n", event.Entity, event.Time); });
	for (int update = 1; update <= 3; update++)
	{
		std::printf("update %d\n", update);
		if (update == 3)
			system.Remove(0);
		system.Update(0.25f);
	}
	return 0;
}
```

```text output-of="animation-system-toy.cpp"
update 1
  entity 0: pose 22.50, position 0.50
  entity 1: pose 11.25, position 0.50
update 2
  entity 0: pose 45.00, position 1.00
  entity 1: pose 22.50, position 1.00
  event: entity 0 at 0.50
  event: entity 1 at 0.50
update 3
  entity 1: pose 33.75, position 1.50
```

1. **Line 55:** the records of removed animators leave in one pass that keeps the order of the others.
2. **Lines 56–57:** the step reads and writes only its own record, which is what lets the real system run it in parallel.
3. **Lines 58–65:** the publish walks the records in order: a new pose version, an event queued, root motion last.
4. **Lines 66–71:** events leave after everything else, over a snapshot of the listeners.

Read the output from the top. In update 2 both clips pass their event time of 0.5 seconds, and the wave's event comes first, because its record comes first. In update 3 entity 0 is removed: its record leaves at the start of the update, so only entity 1 prints. The system never lets a listener see half an update, because events go out last.

The toy has no parallel loop, so it never needed the rules of the previous section. The real system keeps the toy's order of work and splits only the step.

## The real code

The real system adds four things to the toy: assets that arrive over time, a step that runs in parallel, scene changes that go through the :term[transform contract]{id=transform-contract}, and services. The code follows the data from registration to dispatch.

### Registration

`RegisterAnimationModule` registers the animation components, three asset :term[loaders]{id=loader} (skeletons and clips as cooked binary data, controllers as their source) and the :term[scene system]{id=scene-system}. The descriptor names the system "Animation", leaves Simulate out and orders it between two other modules.

```cpp src="Strata/src/Strata/Animation/AnimationRegistration.cpp#L36-L41"
SceneSystemDescriptor descriptor = MakeSceneSystemDescriptor<AnimationSystem>("Animation", false, [](Scene& scene) { return CreateScope<AnimationSystem>(scene); });
descriptor.AfterIfPresent = { "Scripting" };
descriptor.BeforeIfPresent = { "Physics" };
descriptor.ProfileStage = "Scene.Animation";
const bool registered = SceneSystemRegistry::Register(std::move(descriptor));
ST_CORE_VERIFY(registered, "The animation module could not register its scene system");
```

The two ordering lists hold names, and `IfPresent` makes them soft: a build without scripting or physics still runs animation. `ProfileStage` names the frame's profiler stage for animation, so the [profiler](../core/profiling.md) shows the cost of animation as one bar. The composition root calls the function only when the build includes the module.

### Records

`AnimationSystem` connects to the registry's signals in its :term[constructor]{id=constructor}. When an `AnimatorComponent` is constructed, a record is added. When one is destroyed, its record is flagged, not erased, so that the other records never move. The next `CompactRecords` removes flagged records in one pass that keeps the order of the others.

At the start of a scene, the system sorts the records by entity, the order in which a freshly loaded scene created them. Animators added later follow in the order they were added. This order decides the order of the publish, and with it the order of events.

An animator that is switched off resets and loses its pose; one switched on again starts over, with `PlayOnStart` if the component asks. Animators of an additive sub-scene get records of their own while it is loaded and lose them when it leaves. So do the animators of the prefabs that `InstantiateMany` makes: every instance has its own record, and the skins and attachments of an instance follow its animator.

### Asset sets

Most characters of one kind share a skeleton, a controller and a clip. Loading and binding those once for a hundred animators is far cheaper than a hundred times. The system therefore keeps an **asset set** for each distinct triple of skeleton, controller and clip handles: the shared assets, their bindings and their reach. A binding says which joint each channel of a clip moves; the reach says how far the clips can carry the mesh, which [culling](culling.md) uses. A map from the triple finds the set, a record holds the set while it uses it, and a set with no users becomes a free slot.

Each update the main thread resolves every set that has users, once. It requests the assets from the :term[asset manager]{id=asset-manager}, rebuilds the bindings of a clip to a skeleton only when an object changed, and logs a failure once for the set. A reloaded asset is a new object with a new id, so bindings follow the id.

A clip that a script plays directly through `PlayClip` has its own binding in its record, bound again when the skeleton changes. The engine's rule is at work here: hold handles, request every update and never block. The [residency page](../assets/residency.md) explains why. Today the system finds its assets through the active asset manager, by static calls in `AnimationSystem.cpp`, and not through its scene.

What a character shows while something is missing depends on which asset is missing. The table lists what the code does, and what the renderer does with the answer.

| Missing | What the update does | What the character shows |
| --- | --- | --- |
| Skeleton, controller or a clip still loading | The record is Waiting and counts in the statistics | No pose, so the renderer draws the bind pose |
| Skeleton that will not load | The record stays Waiting; one warning for the set | The bind pose, for as long as it fails |
| Controller that will not load | One warning; the animator plays the component's Clip | That clip |
| Clip of a state that will not load | One warning for the set | The :term[rest pose]{id=rest-pose} in that state |
| Skeleton with fewer joints than the skin needs | The pose is published | The renderer ignores the pose and draws the bind pose |

The two last rows differ in who decides. For a failed clip the system evaluates the state and gets the rest pose. For a short skeleton the system publishes a pose, and the renderer refuses it. The bind pose is the mesh's pose as modelled; the rest pose is the skeleton's own rest transforms.

### The update

Here is the first half of `AnimationSystem::OnUpdate`. Search for what the job writes and what it only reads.

```cpp src="Strata/src/Strata/Animation/AnimationSystem.cpp#L608-L619" from="JobSystem::ParallelFor(static_cast<uint32_t>(m_Records.size()), c_EvaluationBatchSize" to="StepRecord(record, deltaTime, t_Scratch);" symbol="AnimationSystem::OnUpdate"
JobSystem::ParallelFor(static_cast<uint32_t>(m_Records.size()), c_EvaluationBatchSize, [this, &registry, &queued, deltaTime](uint32_t begin, uint32_t end)
{
	ST_PROFILE_SCOPE("AnimationSystem::Evaluate");
	thread_local std::vector<JointPose> t_Scratch;
	for (uint32_t index = begin; index < end; index++)
	{
		AnimatorRecord& record = m_Records[index];
		record.Update = record.Removed ? RecordUpdate::None : ClassifyRecord(record, registry);
		if (record.Update == RecordUpdate::Sync)
			m_SyncQueue[queued.fetch_add(1, std::memory_order_relaxed)] = index;
		else if (record.Update == RecordUpdate::Step)
			StepRecord(record, deltaTime, t_Scratch);
```

1. **Line 608:** one loop over all records, in batches of at most `c_EvaluationBatchSize`, which is 8.
2. **Line 611:** each thread keeps its own scratch buffer in a `thread_local` variable, so no two jobs share one.
3. **Line 615:** a job classifies its record and writes only that record's `Update` field.
4. **Line 617:** a `Sync` record queues its index through an atomic counter, and the main thread handles it later.
5. **Lines 618–619:** a `Step` record advances and computes its pose right there, inside the job.

The loop covers every record in batches of at most eight, which is `c_EvaluationBatchSize`. Each job classifies its record: `None` for inactive or removed, `Waiting` while assets load, `Sync` when activity, assets or a played clip changed, and `Step` otherwise. A `Step` record advances and computes its pose right there, using a scratch buffer that each thread keeps in a `thread_local` variable, so no two threads share one. A `Sync` record cannot be brought up to date in a job, because that touches shared state. Its index goes into a queue through an atomic counter.

The second half handles the queue and the second loop.

```cpp src="Strata/src/Strata/Animation/AnimationSystem.cpp#L624-L653" from="const std::span<uint32_t> synced" to="StepRecord(m_Records[m_Work[item]], deltaTime, t_Scratch);" symbol="AnimationSystem::OnUpdate"
const std::span<uint32_t> synced(m_SyncQueue.data(), queued.load());
std::sort(synced.begin(), synced.end());
m_Work.clear();
for (const uint32_t index : synced)
{
	AnimatorRecord& record = m_Records[index];
	const AnimatorComponent& component = registry.get<AnimatorComponent>(record.Handle);
	const WorldTransformComponent* world = registry.try_get<WorldTransformComponent>(record.Handle);
	if (!SyncRecord(record, component, world && world->ActiveInHierarchy))
	{
		record.Update = RecordUpdate::None;
		continue;
	}
	ResolveSet(m_Sets[record.Set]);
	ResolvePlayedClip(record, m_Sets[record.Set]);
	if (!IsReady(record))
	{
		record.Update = RecordUpdate::Waiting;
		continue;
	}
	PrepareStep(record, component);
	record.Update = RecordUpdate::Step;
	m_Work.push_back(index);
}
JobSystem::ParallelFor(static_cast<uint32_t>(m_Work.size()), c_EvaluationBatchSize, [this, deltaTime](uint32_t begin, uint32_t end)
{
	ST_PROFILE_SCOPE("AnimationSystem::Evaluate");
	thread_local std::vector<JointPose> t_Scratch;
	for (uint32_t item = begin; item < end; item++)
		StepRecord(m_Records[m_Work[item]], deltaTime, t_Scratch);
```

1. **Lines 624–625:** the queue's raw order follows thread timing; sorting brings back record order.
2. **Lines 632–636:** the main thread brings a record up to date; an inactive animator is dropped.
3. **Lines 637–643:** the shared set and the played clip are resolved, and a record whose assets are missing waits.
4. **Lines 644–646:** a ready record is prepared and joins the work list.
5. **Lines 648–653:** the second loop has the same batch size and the same rule: a job steps one record.

The queue holds the records in the order the threads arrived, which is not stable. The main thread therefore sorts it, and then brings each record up to date in record order. Records that become ready join `m_Work` and step in a second parallel loop with the same batch size. Records that are not ready become `Waiting`.

:::example[One update of twenty records]
Twenty animators have records 0 to 19. The first loop cuts them into batches of 8: records 0 to 7, 8 to 15 and 16 to 19, so three batches. Records 3 and 11 were switched on again before this update, so their jobs return `Sync` and queue their indices. Thread timing may queue 11 before 3, so the queue holds 11, 3. The main thread sorts it to 3, 11, brings both up to date, and steps them in a second loop of one batch.

Records 2 and 5 also passed an event time. Each wrote its event into its own record, and nothing else happened. The publish walks the records from 0 to 19, so the pending events are 2, then 5, whichever thread finished first. On 0, 1 or 7 threads the list is the same, and so are the pose bytes.
:::

Now the publish and the end of the update.

```cpp src="Strata/src/Strata/Animation/AnimationSystem.cpp#L657-L707" from="bool posesChanged = false;" to="ApplyRootMotion(Entity(record.Handle, &m_Scene), record.Instance.GetRootMotion());" symbol="AnimationSystem::OnUpdate"
bool posesChanged = false;
for (uint32_t index = 0; index < m_Records.size(); index++)
{
	AnimatorRecord& record = m_Records[index];
	if (record.Removed || record.Update == RecordUpdate::None)
		continue;
	stats.ActiveAnimators++;
	if (record.Update != RecordUpdate::Step)
	{
		stats.Waiting++;
		continue;
	}
	stats.Advanced++;
	stats.ReachUpdates += record.ReachComputed ? 1u : 0u;
	if (record.Evaluated)
	{
		record.PoseVersion = m_NextPoseVersion++;
		record.PoseStale = false;
		posesChanged = true;
		stats.Evaluated++;
	}
	else
	{
		if (!record.Evaluate)
		{
			stats.Culled++;
			record.PoseStale = true;
		}
		// The pose stays, where its clips take it changed (a transition while unseen).
		if (record.ReachChanged && record.PoseVersion != 0)
		{
			record.PoseVersion = m_NextPoseVersion++;
			posesChanged = true;
		}
	}
	if (!record.Events.empty())
	{
		// Names are copied: listeners may change or remove the animator.
		const AnimationController* controller = m_Sets[record.Set].Controller.get();
		const UUID id = registry.get<IDComponent>(record.Handle).ID;
		for (const AnimatorFiredEvent& fired : record.Events)
		{
			if (!controller || fired.State >= controller->GetStates().size() || fired.Event >= controller->GetStates()[fired.State].Events.size())
				continue;
			const AnimationState& state = controller->GetStates()[fired.State];
			m_PendingEvents.push_back(PendingEvent { record.Handle, id, state.Events[fired.Event].Name, state.Name, fired.Time });
		}
	}
	// Last: the transform's signal reaches listeners, which must not find the record half processed.
	if (record.Settings.ApplyRootMotion)
		ApplyRootMotion(Entity(record.Handle, &m_Scene), record.Instance.GetRootMotion());
```

1. **Lines 661–668:** records without work are skipped, and waiting ones are counted but not published.
2. **Lines 671–677:** a new pose takes the next version from one counter, in record order.
3. **Lines 680–684:** an unseen animator that skipped its pose counts as skipped and is marked stale.
4. **Lines 692–704:** the names of fired events are copied into the pending list.
5. **Lines 705–707:** root motion comes last, because its transform signal reaches listeners.

After the loop the function raises the poses version when a pose changed, places attachments, compacts the records again and dispatches the events. The second compaction is there because listeners of the transform signals that root motion raised may remove animators.

### Publishing

The publish is a single loop on the main thread. For each live record it counts statistics, gives an evaluated pose a new version from `m_NextPoseVersion`, copies the names of the events into `PendingEvent`, and applies root motion last. The names are copied because a listener may change or remove the animator, and the record's strings would then be gone. Root motion comes last because the transform signal it raises reaches listeners, and a listener must not find the record half processed.

A `WhenVisible` animator that was not evaluated keeps its old pose and is marked stale. [Culling](culling.md) teaches that case. A renderer reads versions, not pose data: if the global poses version did not change, every pose it has seen is current.

### Attachments

An **attachment** (also called a socket) puts an entity at a joint of an animator's skeleton. The entity carries an `AttachToJointComponent` that names the animator and the joint. After the publish, the system computes a :term[local transform]{id=local-transform} for the entity and writes it. The picture shows a case from the sample game: the menu robot holds a flag in its raised hand, where the orange outline of the selection marks it.

::figure{id=menu-robot}

The flag's holder is the entity with the component. The flag itself is a child of the holder with its own offset and scale. The holder's translation, rotation and scale are replaced every update, so an offset on the holder would be lost. An offset belongs on a child, as the flag shows.

The next quote is the middle of `PlaceAttachments`. Search for the cycle guard, the two ways of computing the local transform and the skip.

```cpp src="Strata/src/Strata/Animation/AnimationSystem.cpp#L852-L880" from="// An entity above its animator would move it along" to="entity.MarkModified<TransformComponent>();" symbol="AnimationSystem::PlaceAttachments"
// An entity above its animator would move it along: the transforms would chase each other.
if (m_Scene.IsDescendantOf(animator, entity))
	continue;
// The local transform that puts the entity at the joint: the pose itself under the animator (the usual case, which
// then does not change when the animator moves), else through the parent's world transform.
glm::mat4 local = record->Pose[joint];
const Entity parent = entity.GetParent();
if (parent != animator)
{
	const glm::mat4 parentWorld = parent ? m_Scene.GetWorldTransform(parent) : glm::mat4(1.0f);
	if (!(std::abs(glm::determinant(glm::mat3(parentWorld))) > Scene::c_MinInvertibleDeterminant))
		continue;
	local = glm::inverse(parentWorld) * m_Scene.GetWorldTransform(animator) * local;
}
TransformComponent& transform = entity.GetTransform();
AttachmentState& state = m_Attachments[handle];
// The same placement as last time, and nobody moved the entity since: nothing to write, no transform to update.
if (state.Valid && SameMatrix(local, state.Local) && transform.Translation == state.Translation && transform.Rotation == state.Rotation
	&& transform.Scale == state.Scale)
	continue;
glm::vec3 translation;
glm::quat rotation;
glm::vec3 scale;
if (!Math::DecomposeTransform(local, translation, rotation, scale))
	continue;
transform.Translation = translation;
transform.Rotation = rotation;
transform.Scale = scale;
entity.MarkModified<TransformComponent>();
```

1. **Lines 852–854:** the cycle guard skips an entity above its animator.
2. **Lines 857–865:** the local transform is the joint's pose, or goes through the parent's :term[world transform]{id=world-transform}.
3. **Lines 868–871:** the same placement as last time on an untouched entity writes nothing.
4. **Lines 877–880:** translation, rotation and scale are all written, and the change is signaled.

An entity above its animator is refused, because the animator would move with it and the two transforms would chase each other. When the holder is a direct child of the animator, its local transform is the joint's pose itself. That case needs no parent matrix, and the value does not change when the animator moves.

Otherwise the system goes through the parent's world transform and skips a parent whose matrix cannot be inverted. If the placement is the same as last time and nobody has touched the entity since, nothing is written. The skip matters because a write raises a transform signal and costs a world-transform update. The last line is the transform contract: a direct write must be signaled.

An attachment under a character that is drawn between :term[fixed steps]{id=fixed-step} stays on its joint on frames without a step. The test for it is named in [How it is tested](#how-it-is-tested); the drawn transforms themselves are taught on [Drawing between fixed steps](../world/interpolation.md).

### Event dispatch

Events leave after everything else. The dispatch moves the pending list into a local, counts it, and copies the list of listeners before it calls any of them.

```cpp src="Strata/src/Strata/Animation/AnimationSystem.cpp#L898-L914" from="// Listeners may add or remove listeners while being called" to="listener->Callback(info);" symbol="AnimationSystem::DispatchEvents"
// Listeners may add or remove listeners while being called; iterate over a snapshot.
const std::vector<Ref<EventListener>> listeners = m_Listeners;
for (const PendingEvent& event : events)
{
	const Entity animator(event.Animator, &m_Scene);
	if (!animator.IsValid())
		continue;
	AnimationEventInfo info;
	info.Animator = animator;
	info.AnimatorID = event.AnimatorID;
	info.Name = event.Name;
	info.State = event.State;
	info.Time = event.Time;
	for (const Ref<EventListener>& listener : listeners)
	{
		if (!listener->Removed)
			listener->Callback(info);
```

1. **Line 899:** the copy of the listener list is the snapshot.
2. **Lines 902–904:** an animator that an earlier listener destroyed is skipped.
3. **Lines 908–910:** the event's strings come from the copied names of the pending event.
4. **Lines 913–914:** a listener removed in the meantime is skipped through its flag.

A listener may add or remove listeners while it runs, which would change the list during the loop. The loop therefore runs over a copy, and each listener is a shared object with a `Removed` flag. `RemoveAnimationEventListener` sets the flag and erases the entry from the real list, so a copy that still holds the listener skips it. An animator that listeners destroyed earlier in the dispatch is skipped too, through `IsValid`. The script system is one listener, and the [script system page](../scripting/script-system.md) shows how it turns an event into `OnAnimationEvent`.

### The services

The system derives from the three service interfaces. It registers each in its constructor and removes each in its :term[destructor]{id=destructor}. While the system exists, any code with the scene can ask for a service and use it without knowing the module. This is the module's public contract, and it lives in the Scene layer.

The first interface is the one renderers read. **`ISkinningPoses`** is the scene service through which renderers read the poses of animators and report which animators they drew.

```cpp src="Strata/src/Strata/Scene/SceneServices.h#L293-L315"
class ISkinningPoses
{
public:
	virtual ~ISkinningPoses() = default;

	// The current pose of the animator on `animator` (an entity with an AnimatorComponent); false while it has none (no
	// skeleton loaded yet, not evaluated yet, inactive).
	virtual bool GetPose(entt::entity animator, SkeletonPose& outPose) const = 0;
	// Changes whenever any pose changes: a renderer that saw this version has seen every pose.
	virtual uint64_t GetPosesVersion() const = 0;
	// A renderer drew (in its view or its shadows) a mesh this animator poses, or would have, had it been posed. Returns
	// whether the pose it drew is older than the animator's time (a WhenVisible animator that skipped its poses while
	// unseen): the provider poses it for the next frame, also while the scene is paused, so a renderer that must show the
	// pose of the moment (a capture) renders again then.
	virtual bool ReportVisible(entt::entity animator) = 0;

	// Entities renderers draw at other world transforms than the scene's: a provider that may not change the scene (the
	// editor's pose preview of a scene that does not play) places attachments (AttachToJointComponent), and the meshes
	// under them, at their joints this way. Valid until the provider changes them; the version changes whenever they do.
	// None by default: the animation system of a playing scene moves attachments in the scene.
	virtual std::span<const RenderTransform> GetRenderTransforms() const { return {}; }
	virtual uint64_t GetRenderTransformsVersion() const { return 0; }
};
```

1. **Lines 298–300:** `GetPose` fails while an animator has no pose.
2. **Lines 301–302:** the version changes whenever any pose changes.
3. **Lines 303–307:** a renderer reports each animator it drew, and learns whether the pose was old.
4. **Lines 309–314:** a provider that may not change the scene gives attachments as render transforms.

A **provider** of poses is whatever implements `ISkinningPoses` for a scene. A playing scene's provider is the Animation system. For an edited scene the editor's pose preview is the provider, and it moves attachments by `GetRenderTransforms` instead of writing the scene, because a preview must not change scene data. The version belongs to the provider, so a renderer compares versions of the provider it has, not of any other.

`IAnimatorControl` offers commands and queries over animators. Commands play a state or a clip, :term[cross-fade]{id=cross-fade} to a state, set the speed, and set or reset the controller's parameters (`SetFloat`, `SetBool`, `SetTrigger`, `ResetTrigger`). Queries give the current state, the :term[normalized time]{id=normalized-time}, whether a transition runs, and the world transform of a joint. Each call fails with a value, not with an assert, for an entity without an animator. The [host functions page](../scripting/host-api.md) shows what the script host does with them.

`IAnimationEventSource` is the smallest: two calls, one to add a listener and one to remove it.

### What an idle scene costs

At the top of `OnUpdate` the system resets its per-update statistics, compacts the records and reads the skin changes. If no record is left, it returns. A scene without animators therefore pays for a few counter resets and one compaction check. The statistics are in `AnimationSystemStats`: animators, active ones, those advanced, evaluated and skipped, waiting ones, asset sets, attachments moved, reach updates, paused evaluations and events dispatched. The tests and the editor read them.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Locks around the scene, jobs write directly | Simple engines that run one loop in parallel | Less code and no record to publish from | Results that follow the timing of threads, and jobs that wait |
| A :term[task graph]{id=task-graph} of animation stages, with jobs for blending and skinning | Large engines with animation graphs; Unreal's parallel animation evaluation is one example | Finer :term[parallelism]{id=parallelism} inside one character | A graph to describe and keep true, and more states to test |
| Update only every few frames at a distance | Many engines, as animation level of detail | Large savings for far characters | Visible stepping, and a second rule for events and root motion |
| Poses as entities, one per joint | Some small engines and tools | Joints that any entity code can use | Dozens of transform updates for each animator in each frame |
| Compressed clips sampled by a library | `ozz-animation` and others | Smaller clips and faster sampling | Work in the importer; Strata reduces keys only and defers compression |

## How it is tested

The `Animation.*` suites in `StrataTests/src/Animation/` test the system: `Animation.System` for services, waiting, events, attachments and prefab instances; `Animation.StateMachine` for the thread-count test; `Animation.RootMotion`; `Animation.Streaming` for sub-scenes and `InstantiateMany`; `Animation.Preview`; and `Animation.Interpolation`. Their neighbours test the renderer's side, the script host and the editor. Counts of cases change, so this page gives none.

The thread-count test builds two hundred animators, drives them for forty updates with changing parameters and triggers, and records every pose byte and every event. It runs once with no job system, and then with a job system of one and of seven threads. The next quote is the comparison.

```cpp src="StrataTests/src/Animation/AnimationSystemTests.cpp#L1085-L1094"
const auto reference = run();
REQUIRE_FALSE(reference.first.empty());
REQUIRE_FALSE(reference.second.empty());
for (const uint32_t threads : { 1u, 7u })
{
	CAPTURE(threads);
	ScopedJobSystem jobs(threads, 1);
	const auto threaded = run();
	CHECK(threaded.first == reference.first);
	CHECK(threaded.second == reference.second);
```

1. **Line 1085:** the reference run has no job system, so everything runs on the test's thread.
2. **Lines 1086–1087:** the reference must hold poses and events, or the comparison proves nothing.
3. **Lines 1088–1091:** the same scenario runs with one thread and with seven.
4. **Lines 1093–1094:** the pose bytes and the event list must equal the reference.

Run a suite directly with `build/windows/bin/Debug/StrataTests.exe --test-suite=Animation*`, or all tests with `ctest --preset windows-debug -j 8`. Two performance tests, the metrics `Evaluate1000` and `CulledAnimators10k` of the `Perf.Animation` suite, measure an update of a thousand evaluated animators and of ten thousand unseen ones. Their budgets live in one file of the engine and appear on the [performance reference](../reference/performance.md), never on this page. The engine's feature test has an arm rig that exercises controller states, events, an attachment and root motion, in `StrataTests/FeatureTest/Scripts/AnimationFeatures.cpp`.

## Changing it safely

New work in this module follows a few rules.

- A new thing a job computes goes into the record, never into the scene or a shared member. If you need a new shared input, the main thread must set it before the first loop.
- A new write to the scene belongs in the publish, after both loops, and goes through the transform contract: `MarkModified`, `registry.patch` or `Scene::MarkTransformChanged`.
- A new event or listener behaviour keeps the snapshot and the `Removed` flag.
- A new host function for scripts is appended to the host function table, and the control service gets the matching call.
- A change to what plays or how an asset binds must keep the thread-count test green, then the `Animation.*` suites, then the renderer's skin tests.
- A change that affects cost runs the two perf tests on the reference machine.

## Summary

- One update has two phases on the main thread around two parallel loops, and jobs read the scene and write only their own record.
- A record has one writer, and the main thread publishes records in a fixed order, so the bytes equal those of any thread count.
- A character shows the bind pose until its skeleton, controller and clips are in; failures are logged once for the set.
- An attachment replaces its entity's translation, rotation and scale every update, skips unchanged placements and refuses an entity above its animator.
- Poses, control and events reach other modules only through three scene services, and the provider of poses can be swapped.

## Check yourself

1. Two jobs of one update finish in different order on two runs. Which of these changes between the runs? (a) The list of events. (b) The order of records in the queue of `Sync` records before sorting. (c) The pose bytes.

   :::answer{tests="determinism,threads"}
   Option (b). The queue is filled by whichever thread arrives first, so its raw order varies, and the main thread sorts it. Options (a) and (c) do not vary, because jobs write their own record and the publish walks the records in order.
   :::

2. A record's skeleton does not load. How often does the log warn, and what does the character show?

   :::answer{tests="assets"}
   The set logs one warning, however many updates pass, because failures are reported once per set. The record stays Waiting, so no pose exists and the renderer draws the bind pose.
   :::

3. A holder entity is a child of the animator, with translation (0, 1, 0) set by hand and an attachment to a hand joint at (0.2, 1.5, 0). What is its translation after the next update, and what if nothing else changes?

   :::answer{tests="attachments"}
   After the first update it is (0.2, 1.5, 0): the system replaces the translation with the joint's pose. While the pose and the entity stay the same, later updates write nothing, because the placement equals the last one and nobody touched the entity.
   :::

4. A script listener removes itself inside the dispatch of an event, and a second event waits behind the first. Is the removed listener called for the second event?

   :::answer{tests="services"}
   No. The dispatch loops over a copy of the list, but removal sets the `Removed` flag on the shared listener object, and the loop tests the flag before each call.
   :::

5. A renderer includes `AnimationSystem.h` to read a pose faster. Which rule does that break?

   :::answer{tests="services,threads"}
   The layer rule: only the Engine and asset pipeline layers include the module. A renderer reads poses through `ISkinningPoses`, which the Scene layer defines.
   :::

## Exercises

1. **Basic.** A scene has 1,000 animators and the batch size is 8. How many batches does the first loop have, and how many does the second have if 17 records need a :term[sync]{id=synchronization}?

   :::answer[Worked solution]{tests="threads"}
   The first loop has $\lceil 1000 / 8 \rceil = 125$ batches. The second covers the 17 queued records, so it has $\lceil 17 / 8 \rceil = 3$ batches: records of 8, 8 and 1.
   :::

2. **Medium.** Run `sketches/animation-system-order.cpp` in your head: why do two orders of the same four moves give two answers, and why does that matter for the publish?

   :::answer[Worked solution]{tests="determinism" solution="sketches/animation-system-order.cpp"}
   Float addition rounds after each step. The program adds the same four moves in record order and in a finish order.

   ```cpp sketch="animation-system-order.cpp"
   // Why the order of publishing matters: the same four root moves, applied in two orders, end at different positions.
   #include <array>
   #include <cstdio>

   int main()
   {
   	// Each animator's job produced one move; the sizes are chosen so that float rounding shows.
   	const std::array<float, 4> moves = { 3.0f, 3.0f, 100000000.0f, -100000000.0f };
   	const std::array<int, 4> recordOrder = { 0, 1, 2, 3 };
   	const std::array<int, 4> finishOrder = { 2, 0, 3, 1 }; // The order four threads might finish in.

   	float byRecord = 0.0f;
   	for (const int index : recordOrder)
   		byRecord += moves[static_cast<size_t>(index)];
   	float byFinish = 0.0f;
   	for (const int index : finishOrder)
   		byFinish += moves[static_cast<size_t>(index)];

   	std::printf("in record order: %.1f\n", static_cast<double>(byRecord));
   	std::printf("in finish order: %.1f\n", static_cast<double>(byFinish));
   	return 0;
   }
   ```

   ```text output-of="animation-system-order.cpp"
   in record order: 8.0
   in finish order: 3.0
   ```

   1. **Line 8:** the four moves: two small ones and two huge ones that cancel.
   2. **Lines 9–10:** the two orders; the finish order stands for thread timing.
   3. **Lines 12–17:** the same sum in each order.
   4. **Lines 19–20:** the two printed results.

   The first order gives 8. The two small moves make 6, and 6 added to 100,000,000 rounds to 100,000,008, because floats of that size step by 8. The second order adds 3 to 100,000,000 first, which rounds back to 100,000,000. The large moves then cancel, and the second 3 is added exactly, giving 3.

   The exact sum is 6, and neither order reaches it. The publish adds root motion into the scene in record order, so a thread's finish order never enters the result.
   :::

3. **Hard.** Break determinism on purpose. In `StepRecord`'s caller, make the job push its events straight into `m_PendingEvents` instead of into its record, and run the suite `Animation.StateMachine`. Say what you expect to see and why.

   :::answer[Worked solution]{tests="determinism,threads"}
   Several jobs then write one vector without a lock, which is a :term[data race]{id=data-race}, and the order of events follows thread timing. The test's reference run has no threads, so its events are in record order; the run on seven threads may differ, and the comparison of the event lists then fails. Because a race depends on timing, expect the failure in some runs only: run the suite several times before you trust a pass.
   :::

4. **Hard.** Trace it yourself: find every write of the Animation system to the scene, and show which thread runs each.

   :::answer[Worked solution]{tests="threads,services"}
   Search `AnimationSystem.cpp` for `MarkModified<TransformComponent>`. The hits are in `ApplyRootMotion` (two places) and in `PlaceAttachments`. In `OnUpdate`, the two `JobSystem::ParallelFor` calls come first, then the publish loop calls `ApplyRootMotion`, then `PlaceAttachments`, then `DispatchEvents`. All three run after both loops on the main thread, because the jobs' :term[lambdas]{id=lambda} only call `ClassifyRecord` and `StepRecord`, which write one record.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Animation/AnimationSystem.h` and `AnimationSystem.cpp`: `AnimationSystem`, `AnimatorRecord`, `AssetSet`, `AnimationSystemStats`.
- `Strata/src/Strata/Animation/AnimationRegistration.cpp`: `RegisterAnimationModule`.
- `Strata/src/Strata/Scene/SceneServices.h`: `SkeletonPose`, `ISkinningPoses`, `IAnimatorControl`, `IAnimationEventSource`.
- `StrataTests/Architecture/Layers.json`: the Animation layer and the option `STRATA_WITH_ANIMATION`.
- Tests: `StrataTests/src/Animation/AnimationSystemTests.cpp`, `StrataTests/src/Perf/AnimationPerfTests.cpp`, `StrataTests/FeatureTest/Scripts/AnimationFeatures.cpp`.
- Other pages: [Blending](blending.md), [Root motion](root-motion.md) and [Culling](culling.md).

## Further reading

- Jason Gregory, "Game Engine Architecture", chapter on animation systems: how engines organize pose evaluation (intermediate).
- Unity manual, the Animator and animation jobs, cited without a link: a parallel animation design to compare (intermediate).
- Unreal Engine documentation on parallel animation evaluation, cited without a link: a second design to compare (intermediate).
- Robert Nystrom, "Game Programming Patterns", chapter "Update Method", on gameprogrammingpatterns.com: the update loop that systems like this one extend (beginner).
