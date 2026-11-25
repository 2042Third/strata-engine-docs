---
id: draw/render-scene-gpu
title: "The render scene's GPU copy"
description: "How Strata keeps a copy of the render scene in graphics memory, uploads only what changed, and draws a new object once its data has arrived."
kind: internals
size: M
tracks: [E]
needs: [draw/batching, gpu/upload-queue]
time: 65
learn:
  - id: copy-follows-logs
    text: explain why the GPU copy follows change logs and uploads only runs of changed elements
  - id: budget-frames
    text: compute the frames that a budget for new proxies needs and when a new proxy first draws
  - id: binding-versions
    text: explain why binding sets are rebuilt by comparing buffer versions and not scenes
  - id: four-rules
    text: name the four rules that keep the GPU copy correct and the reason for each
since: 0.4.0
status: final
---

A scene of 100,000 objects changes a few hundred of them in a frame, yet the :term[graphics card]{id=gpu} needs every object's data to draw. Sending all of it each frame would cost more than the drawing. This page covers the part of Strata that keeps a copy of the :term[render scene]{id=render-scene} in graphics memory and sends only the differences. It decides what is sent, in which order, and how much per frame, and it knows which objects may draw yet. It does not decide what the changes are, how :term[bytes]{id=byte} travel through staging, or how the culling :term[shader]{id=shader} reads the copy; other pages cover those.

## The problem and how engines solve it

A :term[renderer]{id=renderer} that reads data in a shader needs that data in graphics memory, and the scene lives in main memory and changes every frame. The approaches and their costs are the subject of [the render scene](render-scene.md), whose readers follow versioned change logs. The copy in the memory of the graphics processing unit (GPU) is the largest of those readers. It turns the logs into uploads of changed runs, and it spends a fixed number of bytes a frame on objects that appear.

## The map

The **GPU copy** is the set of buffers that holds the render scene's data in graphics memory, one per render scene and shared by every renderer of that scene. A renderer that draws the scene twice, as the main view and a preview do, finds everything already uploaded by the first. The class is `RenderSceneGPU`, and `RenderSceneGPUCache` owns all copies, keyed by the render scene's id.

```mermaid caption="The path of a change. The scene records it in a log, the update reads the log and puts runs in staging, and the queue copies them into the buffers that renderers read." alt="A flow from left to right. The render scene feeds three change logs. The update reads the logs and the asset tables and records runs of changed elements. The upload queue stages the runs and copies them into the buffers of the GPU copy. Renderers read the buffers, and a cache owns the copies by scene id."
flowchart LR
	Scene["RenderScene"] --> Logs["three change logs"]
	Logs --> Update["RenderSceneGPU::Update"]
	Assets["asset manager changes"] --> Update
	Update --> Queue["GPUUploadQueue::RecordSceneUpload"]
	Queue --> Buffers["buffers of the GPU copy"]
	Buffers --> Renderers["renderers and culling"]
	Cache["RenderSceneGPUCache"] -.owns.-> Update
```

The copy holds seven buffers, all in one set so that a released copy can hand them over together.

| Buffer | Holds | Element |
| --- | --- | --- |
| Instances | One record per drawn piece of a mesh: transform and per-piece data | 64 bytes |
| Proxies | The culling record of every proxy | 64 bytes |
| Palette | Joint matrices of posed skinned proxies | one matrix |
| Mesh table | Where each mesh slot's geometry lives | 4 bytes |
| Materials | Material data of each material slot | one record |
| Material flags | Bits that say how each material slot draws | 4 bytes |
| Light records | The scene's lights | one record |

The **culling record** (`GPUProxy`) is the 64-byte record per proxy that the culling shader reads: local and world bounds, the :term[first instance]{id=first-instance} and the number of instances, the mesh slot and flag bits.

The **mesh table** and the **material table** are per-slot tables in the copy: the first gives the geometry of each loaded mesh, the second the material data and flags of each loaded material. A slot is the number a proxy uses for a mesh or material, as [batching](batching.md) explains. Which fields a light record or a material record holds belongs to [lights](../light/lights.md) and [material data](../light/material-data.md); what culling does with the proxies belongs to [the GPU-driven path](gpu-driven.md).

## The contract

The copy knows only what the logs say. It never compares the scene with its own contents, because that would read everything each frame. So it obeys four rules, each with a reason.

:::rule
Record every change of instances or proxies in the change logs (`RecordInstanceChanges`, `RecordProxyChange`) so the GPU copy follows. A change that bypasses the log is a change the copy never sees: the screen shows the old object until something else touches it. See [the render scene](render-scene.md) for the logs.
:::

- **Compare buffer versions, never copies or scene ids.** A renderer rebuilds a :term[binding set]{id=binding-set} when the buffer version changes. A scene id can change while the buffers stay the same objects. A new copy can also take over an old copy's buffers, as [copies and caches](#copies-and-caches) shows; only the version says whether a set still names the right buffers.
- **Render again until no proxy waits.** A new proxy draws only once it is resident, which the next paragraph defines. Code that renders a single picture, such as a capture or a thumbnail, looks at `DeferredProxies` in the renderer's statistics and renders again while it is above zero.
- **Never write the copy with `writeBuffer`.** Every write goes through `GPUUploadQueue::RecordSceneUpload`, which stages it within the frame's order of copies and budget. A direct write skips the order and races with frames that still read the old data.

A proxy is **resident** when its culling record and its instances are in the copy. Only resident proxies draw. A proxy that is not resident has a record of zeros, which the culling shader reads as nothing to draw, so a late upload is safe and never shows garbage.

## A toy version

The toy keeps a list of numbers and a short log of changes, and a mirror of the list that follows the log. It shows the two ideas of the real code: send only what the log names, and send everything when the log does not reach back far enough. The log keeps four entries, so a reader that falls five changes behind must copy it all.

```cpp sketch="draw-render-scene-gpu-toy.cpp"
#include <cstdint>
#include <cstdio>
#include <vector>

struct Change
{
	uint64_t Version = 0;
	uint32_t Index = 0;
};

// The CPU side: values, and a short log that says which index changed at which version.
class Scene
{
public:
	static constexpr size_t c_MaxLog = 4;

	void Set(uint32_t index, int value)
	{
		if (index >= m_Values.size())
			m_Values.resize(index + 1, 0);
		m_Values[index] = value;
		m_Log.push_back({ ++m_Version, index });
		if (m_Log.size() > c_MaxLog)
		{
			// The reader that is older than the dropped entry can no longer follow the log.
			m_Floor = m_Log.front().Version;
			m_Log.erase(m_Log.begin());
		}
	}

	// Appends the indices changed after sinceVersion; false when the log does not reach back that far.
	bool GetChanges(uint64_t sinceVersion, std::vector<uint32_t>& outIndices) const
	{
		if (sinceVersion < m_Floor)
			return false;
		for (const Change& change : m_Log)
		{
			if (change.Version > sinceVersion)
				outIndices.push_back(change.Index);
		}
		return true;
	}

	uint64_t GetVersion() const { return m_Version; }
	const std::vector<int>& GetValues() const { return m_Values; }

private:
	std::vector<int> m_Values;
	std::vector<Change> m_Log;
	uint64_t m_Version = 0;
	uint64_t m_Floor = 0;
};

// The "GPU" side: a copy that follows the log and counts the elements it was sent.
class Mirror
{
public:
	uint32_t Update(const Scene& scene)
	{
		if (m_Initialized && scene.GetVersion() == m_Version)
			return 0;
		std::vector<uint32_t> changes;
		const bool followed = m_Initialized && scene.GetChanges(m_Version, changes);
		if (!followed)
		{
			m_Gpu = scene.GetValues();
			m_Version = scene.GetVersion();
			m_Initialized = true;
			return static_cast<uint32_t>(m_Gpu.size());
		}
		m_Gpu.resize(scene.GetValues().size(), 0);
		for (const uint32_t index : changes)
			m_Gpu[index] = scene.GetValues()[index];
		m_Version = scene.GetVersion();
		return static_cast<uint32_t>(changes.size());
	}

	bool Matches(const Scene& scene) const { return m_Gpu == scene.GetValues(); }

private:
	std::vector<int> m_Gpu;
	uint64_t m_Version = 0;
	bool m_Initialized = false;
};

int main()
{
	Scene scene;
	Mirror mirror;
	scene.Set(0, 10);
	scene.Set(1, 20);
	scene.Set(2, 30);
	std::printf("first update sent %u elements\n", mirror.Update(scene));
	scene.Set(1, 25);
	std::printf("one change sent %u element\n", mirror.Update(scene));
	std::printf("no change sent %u elements\n", mirror.Update(scene));
	for (int value = 1; value <= 5; value++)
		scene.Set(0, value);
	std::printf("five changes, a log of four, sent %u elements\n", mirror.Update(scene));
	std::printf("the copy matches: %s\n", mirror.Matches(scene) ? "yes" : "no");
	return 0;
}
```

```text output-of="draw-render-scene-gpu-toy.cpp"
first update sent 3 elements
one change sent 1 element
no change sent 0 elements
five changes, a log of four, sent 3 elements
the copy matches: yes
```

1. **Lines 22–27:** A change that pushes the oldest entry out of the log records its version as the floor.
2. **Lines 32–36:** A reader older than the floor gets false: the log cannot tell it what changed.
3. **Lines 63–70:** The copy sends everything the first time and whenever it cannot follow the log.
4. **Lines 71–75:** Otherwise it sends only the indices the log names.

The toy keeps one log and one array. The real code differs in four ways. It reads three logs and the lights, and it splits changes by whether the proxy is resident. It also spends a budget on new proxies, and it uploads through staging, not into a plain array.

## The real code

The walk follows one update. It runs on the :term[main thread]{id=main-thread} each frame that a renderer draws the scene. It records its copies in a :term[command list]{id=command-list} of its own and executes that list at once, so work recorded later reads them.

### Growing the buffers

Before anything is written, `EnsureCapacity` makes sure each buffer has room. The next excerpt shows the growth and what happens to the old buffer. Search for the doubling, the clear and the copy.

```cpp src="Strata/src/Strata/Renderer/RenderSceneGPU.cpp#L205-L246"
if (buffer.Buffer && buffer.ElementCount >= required)
	return true;
// Geometric growth, so a scene that grows a little at a time does not copy every frame.
uint64_t capacity = std::max<uint64_t>(buffer.ElementCount, 64);
while (capacity < required)
	capacity *= 2;

nvrhi::BufferDesc desc;
desc.byteSize = capacity * elementSize;
desc.structStride = elementSize;
desc.debugName = fmt::format("RenderSceneGPU.{}", name);
desc.initialState = nvrhi::ResourceStates::ShaderResource;
desc.keepInitialState = true;
nvrhi::BufferHandle created = m_Device->createBuffer(desc);
if (!created)
{
	ST_CORE_ERROR("RenderSceneGPU: failed to create its {} buffer ({} bytes)", name, desc.byteSize);
	return false;
}
// The clear, the copy and the update's uploads write the buffer one after the other: NVRHI places no barrier between
// transfers into a buffer that stays a copy destination, so each step ends with a transition of its own.
const auto barrier = [this, &created]()
{
	m_CommandList->setBufferState(created, nvrhi::ResourceStates::ShaderResource);
	m_CommandList->commitBarriers();
};
if (clear)
{
	m_CommandList->clearBufferUInt(created, 0);
	barrier();
}
if (buffer.Buffer)
{
	// What it holds moves over on the GPU; frames in flight may still read the old buffer.
	m_CommandList->copyBuffer(created, 0, buffer.Buffer, 0, buffer.ElementCount * elementSize);
	barrier();
	Renderer::ReleaseDeferred({ nvrhi::ResourceHandle(buffer.Buffer.Get()) });
}
buffer.Buffer = std::move(created);
buffer.ElementCount = capacity;
m_BufferVersion = ++s_LastBufferVersion;
return true;
```

1. **Lines 208–210:** The capacity doubles from at least 64 elements, so a scene that grows a little at a time does not copy every frame.
2. **Lines 231–235:** A buffer that must start cleared is cleared, then moved to the state that shaders read.
3. **Lines 236–242:** The old contents move over by a copy on the GPU, and the old buffer goes to :term[deferred release]{id=deferred-release} because :term[frames in flight]{id=frames-in-flight} may still read it.
4. **Line 245:** A new buffer version tells renderers to rebuild their binding sets.

### Proxies

Next the update follows the proxy log. Changes of resident proxies upload at once, destroyed proxies are cleared at once, and new ones go into a queue. Search for the three branches and the fallback that reads every proxy.

```cpp src="Strata/src/Strata/Renderer/RenderSceneGPU.cpp#L679-L715"
// Proxies: changes of resident ones upload now, destroyed ones are cleared, new ones wait for the budget.
m_Changes.clear();
const bool allProxies = !m_Initialized || !renderScene.GetProxyChanges(m_ProxyVersion, m_Changes);
if (allProxies)
{
	m_Changes.resize(proxyCount);
	for (uint32_t proxy = 0; proxy < proxyCount; proxy++)
		m_Changes[proxy] = proxy;
}
for (const uint32_t proxy : m_Changes)
{
	if (proxy >= proxyCount || m_Seen[proxy] == m_UpdateStamp)
		continue;
	m_Seen[proxy] = m_UpdateStamp;
	if (renderScene.GetEntity(proxy) == entt::null)
	{
		// Its record is cleared at once; a proxy that takes its index later is a new one.
		m_Records[proxy] = RenderData::GPUProxy {};
		MarkRecord(proxy);
		m_Resident[proxy] = 0;
		continue;
	}
	const uint32_t first = renderScene.GetFirstInstance(proxy);
	const uint32_t count = renderScene.GetInstanceCount(proxy);
	for (uint32_t index = 0; index < count; index++)
		m_InstanceOwners[first + index] = proxy;
	if (m_Resident[proxy])
	{
		m_Records[proxy] = MakeRecord(renderScene, proxy);
		MarkRecord(proxy);
	}
	else if (!m_Queued[proxy])
	{
		m_Queued[proxy] = 1;
		m_Pending.push_back(proxy);
	}
}
```

1. **Line 681:** When the log cannot answer, every proxy counts as changed.
2. **Lines 693–699:** A destroyed proxy gets a record of zeros at once and stops being resident.
3. **Lines 705–709:** A changed resident proxy has its new record marked for upload now.
4. **Lines 710–714:** A new proxy joins the queue once and waits for the budget.

### New proxies and the budget

The queue of new proxies is the interesting part. The **upload budget** is the number of bytes a frame may upload for new proxies, `NewInstanceBytesPerFrame`, 16 MiB by default. Search for the test that stops the loop, and for what a proxy costs.

```cpp src="Strata/src/Strata/Renderer/RenderSceneGPU.cpp#L737-L762"
// New proxies, oldest first, while the frame's budget lasts (and one each frame whatever its size).
while (m_PendingHead < m_Pending.size())
{
	const uint32_t proxy = m_Pending[m_PendingHead];
	if (proxy >= proxyCount || renderScene.GetEntity(proxy) == entt::null || m_Resident[proxy])
	{
		if (proxy < proxyCount)
			m_Queued[proxy] = 0;
		m_PendingHead++;
		continue;
	}
	const uint32_t count = renderScene.GetInstanceCount(proxy);
	const uint64_t bytes = sizeof(RenderData::GPUProxy) + static_cast<uint64_t>(count) * sizeof(RenderData::InstanceData);
	if (bytes > m_BudgetLeft && m_FrameNewProxies > 0)
		break;
	m_BudgetLeft -= std::min(m_BudgetLeft, bytes);
	m_FrameNewProxies++;
	m_Queued[proxy] = 0;
	m_Resident[proxy] = 1;
	m_Promoted.push_back(proxy);
	m_Records[proxy] = MakeRecord(renderScene, proxy);
	MarkRecord(proxy);
	MarkInstances(renderScene.GetFirstInstance(proxy), count);
	update.NewProxies++;
	m_PendingHead++;
}
```

1. **Lines 741–747:** Entries that were destroyed, or became resident, leave the queue.
2. **Lines 748–751:** A proxy costs its record plus its instances, and the loop stops when one does not fit, unless it is the first of the frame.
3. **Line 752:** The budget shrinks and never goes below zero.
4. **Lines 754–759:** The proxy becomes resident, and its record and instances are marked for upload.

After this loop the update counts what still waits. `GetDeferredProxies` and `GetDeferredBytes` report it, and the renderer's statistics show the same numbers. Palettes, lights and the asset tables follow, each as runs of changed elements, and one call to `RecordSceneUpload` sends all the regions. When staging cannot be had, the update logs an error and keeps the old versions. The next update then reads the same changes again, and the proxies it made resident in that update return to the queue.

### The asset tables

The mesh and material tables describe loaded assets, not scene data, so another trigger drives them. They are rebuilt only when the :term[asset manager]{id=asset-manager} reports a content change or the scene's slots change. A material is built again when it, the default material or one of its textures was loaded, reloaded or dropped; a reverse index from each texture to the materials that name it finds those. It is never rebuilt because a texture streamed in another level of detail, because the table names textures by their place in the :term[bindless]{id=bindless} table, which does not change then.

A material that is not loaded draws with the default material's data, and a mesh that is not loaded has a zero entry. The tables are therefore always complete, and the culling shader needs no check for an asset that is missing.

### Copies and caches

`RenderSceneGPUCache::Get` makes a copy the first time a scene asks for one. The next excerpt shows the two ways a new copy can start with data. Search for the clone and for the recycled buffers.

```cpp src="Strata/src/Strata/Renderer/RenderSceneGPU.cpp#L911-L939" symbol="RenderSceneGPUCache::Get"
RenderSceneGPU& RenderSceneGPUCache::Get(const RenderScene& renderScene)
{
	const uint64_t id = renderScene.GetId();
	auto found = m_Mirrors.find(id);
	if (found == m_Mirrors.end())
	{
		{
			std::lock_guard lock(s_Mutex);
			s_Mirrored.insert(id);
		}
		// A clone's mirror is copied from its source's on the GPU when that holds exactly what the clone started with.
		Scope<RenderSceneGPU> mirror;
		RenderSceneGPU* source = renderScene.GetCloneSource() != 0 ? Find(renderScene.GetCloneSource()) : nullptr;
		if (source && source->HoldsVersions(renderScene.GetCloneVersions()))
			mirror = RenderSceneGPU::CreateClone(*source, id);
		if (!mirror)
		{
			mirror = CreateScope<RenderSceneGPU>(m_Device, id);
			if (m_Recycled)
			{
				mirror->AdoptBuffers(std::move(*m_Recycled));
				m_Recycled.reset();
			}
		}
		found = m_Mirrors.emplace(id, std::move(mirror)).first;
		found->second->BeginFrame(m_Frame);
	}
	return *found->second;
}
```

1. **Lines 923–925:** The clone's source is searched, and its buffers are copied on the GPU when it holds exactly the clone's versions.
2. **Lines 926–934:** Otherwise a new empty copy starts, and it adopts a recycled set of buffers if one waits.
3. **Line 936:** The new copy learns the current frame, so that its budget starts.

A play start copies the scene, and the copy's render scene remembers its source and the versions it started from. When the source's copy holds exactly those versions and nothing later, `CreateClone` copies each buffer on the GPU. The clone's first frame then uploads nothing and draws the same as the source. Otherwise the new copy starts empty and fills by uploads.

A copy goes with its scene, and a copy no renderer updated for 300 frames goes too. If its buffers are small, 1 MiB or less in total, they wait for the next copy, which adopts them with their buffer version. The thumbnail renderer draws one small scene after another this way and never creates a buffer. Large buffers go to `Renderer::ReleaseDeferred`, because :term[frames in flight]{id=frames-in-flight} may still read them.

### Loading a scene

A loaded scene should not cost its showing frame anything. `PrepareLoadedScene` builds the proxies in chunks within the frame's loading budget, then fills the copy. Search for the two places where it returns false although the work is done.

```cpp src="Strata/src/Strata/Renderer/RenderScene.cpp#L302-L324" symbol="RenderScene::PrepareLoadedScene"
bool RenderScene::PrepareLoadedScene(Scene& scene, SceneWorkBudget& budget)
{
	const Ref<AssetManagerBase>& assets = AssetManager::GetActive();
	RenderScene& renderScene = Get(scene);
	const bool preparedBefore = renderScene.m_PreparedProxies;
	renderScene.m_PreparedProxies = Prepare(scene, assets, budget.GetRemainingTime());
	if (!renderScene.m_PreparedProxies)
		return false;
	if (!Renderer::IsInitialized())
		return true;
	// The GPU's copy too, within a frame's budget for new proxies, so that the frame that shows the scene uploads none. The
	// frame that completed the proxies with its loading time spent leaves it to the next one.
	if (!preparedBefore && !budget.HasTime())
		return false;
	RenderSceneGPUCache& mirrors = Renderer::GetRenderSceneGPUs();
	const bool made = mirrors.Find(renderScene.GetId()) == nullptr;
	RenderSceneGPU& mirror = mirrors.Get(renderScene);
	mirror.Update(renderScene, assets, c_PrepareUploadBytes);
	// The frame that made the copy (its buffers, their first upload and its submission) is not the one that shows the scene:
	// that frame builds the renderers' binding sets for the copy, and the two together were the longest frame of an
	// editor's open (0.4-0.7 ms for the copy of 100,000 empty entities alone, on a loaded machine).
	return !made && mirror.GetDeferredProxies() == 0;
}
```

1. **Line 307:** The proxies are built within the time the loading budget has left.
2. **Lines 314–315:** The frame that finished the proxies leaves the copy to the next call when no time remains.
3. **Lines 317–319:** The update gets the 16 MiB of `c_PrepareUploadBytes`.
4. **Line 323:** The call returns false while the copy is new or proxies still wait.

### What a renderer keeps

A renderer keeps state per scene: visibility bits, level-of-detail fades, :term[draw lists]{id=draw-list}, feedback and material resolution. At a play start the scene it draws is a clone of the one it drew last, with the same slots, proxies and instances. So `PrepareExtraction` keeps that state and changes only the scene id that tags it. For any other scene the slots mean something else, so the renderer clears all of it and the first frame builds it again.

## A worked example: 100,000 proxies

:::example[A scene of 100,000 cubes loads]
Each cube has one instance. A new proxy costs 64 bytes for its record and 64 for its one instance, 128 bytes. The upload budget of 16 MiB is 16,777,216 bytes, so one frame may take 16,777,216 divided by 128, which is 131,072 proxies. All 100,000 cubes cost 12,800,000 bytes and fit in one call.

`PrepareLoadedScene` first builds the proxies in chunks of 2,048, over several frames. In the call that completes them, while the loading budget still has time, `PrepareLoadedScene` makes the copy: the proxies buffer grows from 64 elements by doubling to 131,072, which is 8,388,608 bytes. The update takes every proxy within the budget. The call still returns false, because the frame that makes a copy is never the frame that shows the scene. The next call finds nothing waiting and returns true, and the frame that shows the scene uploads no proxy.

Now give each proxy three instances. A proxy costs 64 + 3 × 64 = 256 bytes, so a frame takes 65,536 proxies and 100,000 need two frames: 65,536 in the first, 34,464 in the second. In the first frame 34,464 proxies wait with records of zeros and draw nothing, and the second frame completes them. A picture rendered in the first frame would show a third of the scene missing.
:::

The state of one proxy through these frames is a small machine. A proxy is not seen, then queued, then resident, and it can be destroyed at any point.

```mermaid caption="The residency of one proxy. A new proxy is queued with a record of zeros and becomes resident when the frame's budget reaches it. A destroyed proxy is cleared at once." alt="A state diagram with three states. A proxy starts not seen. Creating it moves it to queued, and the budget moves it to resident. Changes keep it resident. Destroying it returns it to not seen."
stateDiagram-v2
	[*] --> NotSeen
	NotSeen --> Queued: created or index taken over
	Queued --> Resident: budget reaches it
	Queued --> NotSeen: destroyed
	Resident --> Resident: changed, uploaded at once
	Resident --> NotSeen: destroyed, record cleared
```

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Upload the whole scene every frame | Small engines and tools | No logs and no versions to keep right | A cost that grows with the scene, not with the change |
| `writeBuffer` for each change | Code that uploads a little data | Almost no upload code | No frame budget, no order with other copies |
| One copy per renderer | Engines with one view | No sharing rules | Memory and uploads for each view of the same scene |
| Compare the scene with the copy | Debug tools | Correct even when a change was never logged | A read of the whole scene per frame |
| New proxies upload without a budget | Engines with small scenes | Every object draws in its first frame | A long frame when a big scene loads |

## How it is tested

The suite `GPU.Renderer.RenderSceneGPU` shares one device with the other GPU suites, so it runs with the label `gpu`. Its cases cover:

- the shared copy, whose renderers upload what changed once;
- random edits, after which every resident proxy matches the render scene;
- the budget for new proxies ("New proxies upload within the frame's budget and are drawn once they arrived; destroyed ones are cleared at once");
- release and recycling of copies;
- prepared loads ("A loaded scene's GPU copy is filled while it is prepared, so the frame that shows it uploads no proxy");
- the asset tables and the light records;
- clones ("A copied scene's GPU copy is cloned from its source's: the copy's first frame uploads nothing and draws the same");
- the write logs that other readers use.

Run the suite from a build with `StrataTests --test-suite=GPU.Renderer.RenderSceneGPU`, or select the `gpu` label in `ctest`. The budget case counts frames: with a budget of 300 proxies for 1,000 cubes it expects 4 frames, 300, 300, 300 and 100.

## Changing it safely

- A new per-instance field goes to a parallel buffer, and its changes go through `RecordInstanceChanges`. `InstanceData` stays 64 bytes.
- A new buffer joins `BufferSet` and `GetGrowingBuffers`, and decides whether it starts cleared, so that an adopted buffer is cleared the same way.
- A new piece of data per proxy changes `MakeRecord` and has to be logged with `RecordProxyChange`, or the copy keeps the old record.
- Code that renders one picture renders again while `DeferredProxies` is above zero.
- Never write a buffer of the copy directly. Never compare copies or scene ids to decide about binding sets.
- Pass the suite above, and `GPU.SceneRenderer.GPUDriven` too when a record changes.

## Summary

- The GPU copy follows the change logs and uploads only runs of changed elements, once for all renderers of a scene.
- A new proxy costs its record plus its instances against a budget of 16 MiB a frame, takes at least one proxy a frame, and draws once resident.
- Binding sets compare buffer versions, because a recycled copy hands its buffers and their version to the next copy.
- Four rules keep the copy right: log every change, compare versions, render again until nothing waits, and write only through staging.

## Check yourself

1. A scene changes one proxy's transform and nothing else. What does the update upload?

   :::answer{tests="copy-follows-logs"}
   The proxy's culling record, whose world bounds moved, and the run that holds its instances. A transform change writes both logs, the proxy is resident, and the other buffers are untouched. A frame with no changes uploads nothing. If the log had overflowed, the update would read every proxy instead.
   :::

2. A budget holds 128 proxies of one instance. How many frames do 1,000 such proxies need, and how many are resident after the first?

   :::answer{tests="budget-frames"}
   Eight frames, because 1,000 divided by 128 is 7.8, rounded up. After the first frame 128 are resident, and the other 872 draw nothing yet.
   :::

3. A renderer draws a thumbnail of one small scene, then another. A developer proposes rebuilding binding sets whenever the scene id changes. Which statement is right?

   :::answer{tests="binding-versions"}
   The proposal wastes work. The new copy adopts the old copy's buffers and their version, so the sets still name the right buffers. Comparing the buffer version rebuilds a set only when a buffer really changed. Comparing the scene id would rebuild every time, and comparing copies would miss a buffer that grew.
   :::

4. Name a rule that a capture tool breaks when it renders a large scene once and saves the picture.

   :::answer{tests="four-rules"}
   Render again until no proxy waits. In the first frame only the proxies within the budget are resident, so the picture lacks the others. The tool should render until `DeferredProxies` reaches zero.
   :::

## Exercises

1. **Basic.** A scene has 2,000 proxies of two instances each. The budget is 100 KiB (102,400 bytes) a frame. How many proxies fit in a frame, and how many frames are needed?

   :::answer[Worked solution]{tests="budget-frames"}
   A proxy costs 64 + 2 × 64 = 192 bytes. A frame takes 102,400 divided by 192, which is 533.3, so 533 proxies; the next would not fit. Then 2,000 divided by 533 is 3.75, so 4 frames.
   :::

2. **Medium.** Write a program that counts the frames for a list of instance counts and a budget, with at least one proxy a frame. Run it for 100,000 proxies of three instances and a budget of 16 MiB.

   :::answer[Worked solution]{tests="budget-frames" solution="sketches/draw-render-scene-gpu-budget.cpp"}
   The inner loop mirrors the update: stop when a proxy does not fit and one was already taken.

   ```cpp sketch="draw-render-scene-gpu-budget.cpp"
   #include <algorithm>
   #include <cstdint>
   #include <cstdio>
   #include <vector>

   constexpr uint64_t c_RecordBytes = 64;
   constexpr uint64_t c_InstanceBytes = 64;

   // Counts the frames that a queue of new proxies needs. Each entry is a proxy's instance count, oldest first.
   uint32_t CountFrames(const std::vector<uint32_t>& instanceCounts, uint64_t budget)
   {
   	size_t head = 0;
   	uint32_t frames = 0;
   	while (head < instanceCounts.size())
   	{
   		uint64_t left = budget;
   		uint32_t taken = 0;
   		while (head < instanceCounts.size())
   		{
   			const uint64_t bytes = c_RecordBytes + instanceCounts[head] * c_InstanceBytes;
   			// A proxy that does not fit waits, but every frame takes at least one.
   			if (bytes > left && taken > 0)
   				break;
   			left -= std::min(left, bytes);
   			taken++;
   			head++;
   		}
   		frames++;
   	}
   	return frames;
   }

   int main()
   {
   	constexpr uint64_t c_SixteenMiB = 16ull << 20;
   	std::printf("1000 cubes, 128 proxies a frame: %u frames\n", CountFrames(std::vector<uint32_t>(1000, 1), 128 * 128));
   	std::printf("100000 cubes, 16 MiB: %u frame\n", CountFrames(std::vector<uint32_t>(100000, 1), c_SixteenMiB));
   	std::printf("100000 proxies of 3 instances, 16 MiB: %u frames\n", CountFrames(std::vector<uint32_t>(100000, 3), c_SixteenMiB));
   	std::printf("3 proxies, a budget of zero: %u frames\n", CountFrames(std::vector<uint32_t>(3, 1), 0));
   	return 0;
   }
   ```

   ```text output-of="draw-render-scene-gpu-budget.cpp"
   1000 cubes, 128 proxies a frame: 8 frames
   100000 cubes, 16 MiB: 1 frame
   100000 proxies of 3 instances, 16 MiB: 2 frames
   3 proxies, a budget of zero: 3 frames
   ```

   1. **Line 20:** A proxy costs its record plus one record per instance.
   2. **Lines 21–23:** A proxy that does not fit waits, unless it is the first of the frame.
   3. **Line 24:** The budget never goes below zero.
   :::

3. **Hard.** Trace it yourself: set a budget of 128 proxies for 1,000 cubes in the pattern of the test named in the budget case, then find which proxies the first frame took.

   :::answer[Worked solution]{tests="four-rules"}
   Copy the test in `StrataTests/src/Renderer/GPURenderSceneGPUTests.cpp` and set `NewInstanceBytesPerFrame` to 128 times the size of a record plus an instance. Put a breakpoint in `RenderSceneGPU::Update` in `Strata/src/Strata/Renderer/RenderSceneGPU.cpp` at the loop over `m_Pending`. The first frame takes the first 128 entries of `m_Pending`, the oldest proxies, and `DeferredProxies` is 872 after it. The count reaches zero after 8 frames.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Renderer/RenderSceneGPU.h` and `RenderSceneGPU.cpp`: `RenderSceneGPU`, `RenderSceneGPUCache`, `Update`, `EnsureCapacity`, `CreateClone`, `AdoptBuffers`.
- `Strata/src/Strata/Renderer/GPUSceneData.h`: `RenderData::GPUProxy`.
- `Strata/src/Strata/Renderer/RenderScene.cpp`: `RenderScene::PrepareLoadedScene`, with `c_PrepareUploadBytes` in the :term[header]{id=header}.
- `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp`: `SceneRenderer::PrepareExtraction`.
- Setting: `SceneRendererSpecification::NewInstanceBytesPerFrame`.
- Tests: `StrataTests/src/Renderer/GPURenderSceneGPUTests.cpp`, suite `GPU.Renderer.RenderSceneGPU`.

## Further reading

- NVRHI repository documentation (github.com): command lists and buffer states; intermediate.
