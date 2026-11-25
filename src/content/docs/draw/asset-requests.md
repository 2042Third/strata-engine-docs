---
id: draw/asset-requests
title: "Asking for assets at draw time"
description: "How the renderer asks the asset manager for what a frame draws, at the right priority, without waiting, and lets go of every reference at the frame's end."
kind: internals
size: M
tracks: [E]
needs: [draw/bounds-culling, assets/residency]
time: 60
learn:
  - id: priority-from-view
    text: predict the request a mesh gets from what the camera sees, given its screen fraction and distance
  - id: cache-once
    text: explain why the resolve cache looks up each handle once per frame and lets go of its references when the frame ends
  - id: replay-rule
    text: explain when a still frame replays the previous frame's lookups and when it looks them up again
  - id: fallbacks
    text: name what the frame draws for a material, a mesh and a mesh of unknown bounds that are not loaded
since: 0.3.0
status: final
---

A scene can hold more assets than memory can keep, and a frame has about 16.7 ms to draw. This page teaches the part of the :term[renderer]{id=renderer} that bridges the two. Each frame it works out which meshes and materials the picture needs, asks the :term[asset manager]{id=asset-manager} for exactly those at the right priority, and draws what is loaded. It never waits for a load, and it holds no asset after the frame ends. It does not load files, choose what to drop or decide how many mip levels a texture keeps: those belong to the pages it links.

## The problem and how engines solve it

Think of a large outdoor world with thousands of meshes and tens of thousands of textures. All of it together may need many times the memory of the :term[graphics card]{id=gpu}. The engine must keep part of it loaded and swap the rest as the player moves.

Three questions follow. Which assets does the next frame need? How urgent is each? And what does the frame draw while an asset is still on its way?

Engines meet them in similar ways. They request by visibility: only what the camera can see, or soon will see, is asked for. They attach a priority, so that a large object in the middle of the screen arrives before a small one at the edge. They draw a stand-in meanwhile, and they free memory by use, so that assets nobody asked for lately leave first.

The costs are real. Requests made every frame cost time on the :term[main thread]{id=main-thread}. A request that is too eager fills the load queue with assets nobody sees. A stand-in that lasts too long looks like a bug.

Strata keeps these ideas and adds a rule that fits its :term[frame loop]{id=game-loop}: the renderer asks through a small per-frame cache and drops every reference when the frame ends. [Residency, eviction and pins](../assets/residency.md) teaches the eviction side, and [Loading without stalling](../assets/loading.md) the queue the requests enter.

## The map

Each frame, culling marks every mesh and material slot with a few **use bits**, which are flags that say why the slot is needed. `ResolveAssets` then reads the marks in slot order and turns each into one call on the resolve cache. The cache asks the asset manager and holds the answers until the frame ends.

```mermaid caption="Data flows from culling to use bits, then to the cache and the asset manager. The frame's end releases every reference." alt="A flow of boxes from left to right. Culling marks slots with use bits, and the resolve step reads the bits and calls the cache. The cache calls the asset manager once per handle. The frame ends and releases the references. A branch beside the cache records the lookups for the next frame."
flowchart LR
	Cull["CullView: marks slots with use bits"] --> Resolve["ResolveAssets: one call per slot"]
	Resolve --> Cache["AssetResolveCache: Resolve, Prefetch, FindResident"]
	Cache --> Manager["Asset manager: GetAsset, RequestLoad"]
	Cache --> Record["Recording of the lookups"]
	Record --> Replay["Replay in a still frame"]
	Cache --> End["EndFrame: releases references"]
```

All of this runs on the main thread. The cache is private to one renderer, so two renderers (the editor's view and a capture) never share one. The files are `SceneRendererExtraction.cpp` for the marks and the resolve steps, and `AssetResolveCache.h` and `.cpp` for the cache, both in `Strata/src/Strata/Renderer/`.

## The contract

Callers of the cache, and the code around it, follow a few rules, each with a reason.

1. The renderer requests what the frame draws, every frame. A request stamps the asset as used, and the manager drops assets by that stamp. An asset that is drawn but not requested looks unused and may leave.
2. The renderer never waits. A lookup returns null while an asset loads, and the frame draws without it.
3. The cache holds references only between `BeginFrame` and `EndFrame`. After that, the cache keeps no asset from being dropped and no asset manager alive.
4. A resident lookup never starts a load. It exists for things the frame draws only if they are already there.

:::rule[Never resolve assets per entity]
The engine's guide says that renderer code goes through the proxies and the frame's resolve cache, never one lookup per entity. A scene of 50,000 entities that share 300 meshes would otherwise make 50,000 lookups where 300 are needed.
:::

:::rule[Hold handles across frames, not Refs]
The guide asks for handles across frames because a `Ref` that lives on keeps its asset in memory whatever the budget says. The cache shows the rule applied: it drops every reference at `EndFrame`, so what left the view can be dropped. The rule and its reason belong to [Residency, eviction and pins](../assets/residency.md).
:::

## A toy version

The toy shows the cache's central idea. A **memo** is a table of answers kept for a short time, so that a question asked twice is answered once. Here the slow lookup stands for the asset manager, and the table lives for one frame.

```cpp sketch="draw-asset-requests-toy.cpp"
#include <cstdio>
#include <string>
#include <unordered_map>

// A slow lookup that stands for the asset manager: it counts how often it is asked.
class SlowManager
{
public:
	std::string Get(int handle)
	{
		m_Calls++;
		return "asset" + std::to_string(handle);
	}

	int GetCalls() const { return m_Calls; }
private:
	int m_Calls = 0;
};

// Answers each handle once per frame and forgets everything when the frame ends.
class FrameMemo
{
public:
	void BeginFrame(SlowManager* manager) { m_Manager = manager; }

	void EndFrame()
	{
		m_Answers.clear();
		m_Manager = nullptr;
	}

	const std::string& Resolve(int handle)
	{
		auto found = m_Answers.find(handle);
		if (found == m_Answers.end())
			found = m_Answers.insert({ handle, m_Manager->Get(handle) }).first;
		return found->second;
	}
private:
	SlowManager* m_Manager = nullptr;
	std::unordered_map<int, std::string> m_Answers;
};

int main()
{
	SlowManager manager;
	FrameMemo memo;

	const int frames[2][6] = { { 1, 2, 1, 3, 2, 1 }, { 1, 1, 1, 1, 1, 1 } };
	for (int frame = 0; frame < 2; frame++)
	{
		const int before = manager.GetCalls();
		memo.BeginFrame(&manager);
		for (const int handle : frames[frame])
			memo.Resolve(handle);
		memo.EndFrame();
		std::printf("frame %d: 6 lookups, %d manager calls\n", frame + 1, manager.GetCalls() - before);
	}
	return 0;
}
```

```text output-of="draw-asset-requests-toy.cpp"
frame 1: 6 lookups, 3 manager calls
frame 2: 6 lookups, 1 manager calls
```

1. **Lines 32–38:** `Resolve` asks the slow lookup only when the table has no answer, so a handle costs one call per frame.
2. **Lines 26–30:** `EndFrame` clears the table and lets go of the manager, as the real cache does.
3. **Line 49:** the first frame repeats handles; the second asks for one handle six times.
4. **Line 57:** the count of manager calls is read as a difference, so each frame reports its own.

The first frame draws six things but needs three answers: handles 1, 2 and 3. The second frame draws one handle six times and pays once. The table is cleared at the frame's end, so the second frame asks again. The real cache does the same, and adds three things the toy lacks: priorities, lookups that never start a load, and a recording that makes a still frame cheaper.

## The real code

The code below follows the order of the data: marks, the walk over slots, the cache, replay, fallbacks and what the frame publishes.

### Marking by visibility

Culling finds the proxies inside the :term[frustum]{id=view-frustum}. For each, `MarkVisibleProxies` computes the **screen fraction**, which is the diameter of the proxy's :term[bounding sphere]{id=bounding-sphere} divided by the height of the viewport. [Culling and bounds](../draw/bounds-culling.md) teaches how it is computed. A fraction above `HighPriorityScreenFraction`, which defaults to 0.05, marks the slot as High.

```cpp src="Strata/src/Strata/Renderer/SceneRendererExtraction.cpp#L310-L316" from="const float fraction" to="AppendMark(output.MaterialMarks, overrideSlot, usage);" symbol="SceneRenderer::MarkVisibleProxies"
const float fraction = GetScreenFraction(camera, bounds.GetCenter(), glm::length(bounds.GetExtents()));
m_VisibleFractions[item] = fraction;
const uint32_t usage = fraction > highFraction ? (c_UseView | c_UseHigh) : c_UseView;
const uint32_t overrideSlot = renderScene.GetOverrideMaterialSlot(proxy);
AppendMark(output.MeshMarks, renderScene.GetMeshSlot(proxy), usage | (overrideSlot == RenderScene::c_InvalidIndex ? usage << c_SubmeshMaterialsShift : 0u));
if (overrideSlot != RenderScene::c_InvalidIndex)
	AppendMark(output.MaterialMarks, overrideSlot, usage);
```

The marks are flags, and a slot's flags are merged into one set, so a bit once set stays set. Four of them exist: `c_UseView` (drawn, Normal), `c_UseHigh` (drawn large, High), `c_UsePrefetch` (near the camera but out of view, Low) and `c_UseShadow` (casts into a cascade from outside the view). Two proxies that share a mesh share a slot, so one large proxy makes the whole mesh High.

After the frustum query, `CullView` asks the :term[spatial index]{id=spatial-index} for everything within `PrefetchDistance` of the camera, which defaults to 100 units. A proxy that was not in view gets `c_UsePrefetch`. A **request priority** is the order in which the asset manager loads what is asked for: High, Normal or Low.

A **prefetch distance** is the radius around the camera inside which assets are requested at Low priority although nothing draws them yet.

:::example[Which priority does a unit cube get]
A cube of side 1 has half extents of 0.5 on each axis, so its bounding sphere has radius 0.5 times the square root of 3, about 0.866. The camera's vertical :term[field of view]{id=field-of-view} is 60 degrees, and the tangent of half of it is 0.577.

At a distance $d$ the view is $2 d$ times the tangent high, and the sphere's diameter is twice its radius, so the fraction is the radius divided by $d$ times the tangent.

At 10 units the fraction is 0.866 divided by (10 times 0.577), which is 0.150: High. At 60 units it is 0.025: Normal. The fraction falls to 0.05 at 0.866 divided by (0.05 times 0.577), which is 30 units. Inside 30 units a unit cube is High, and from 30 to the edge of the view it is Normal. A cube behind the camera at 40 units gets only the prefetch bit.
:::

One more case belongs here. `MarkMeshesWithoutBounds` handles meshes whose bounds the engine does not know, because they never loaded. Their proxies carry :term[placeholder bounds]{id=placeholder-bounds}, so the engine cannot tell whether they are in view. It requests each such mesh as if it were in view, at Normal, until the mesh loads and gives the proxies real bounds.

### Walking the slots

`ResolveAssets` turns the marks into calls. It sorts the used slots first, so that the order of requests, and of the loads queued from them, does not depend on the order of the proxies. The feedback from the graphics processing unit (GPU) lists slots in a different order every frame, so the sort is a radix sort. A comparison sort of 10,000 material slots took a sixth of a frame's render time, according to the code's comment.

```cpp src="Strata/src/Strata/Renderer/SceneRendererExtraction.cpp#L708-L730" from="SortIndices(m_UsedMeshSlots" to="m_FrameGeometry[slot] = *geometry;" symbol="SceneRenderer::ResolveAssets"
SortIndices(m_UsedMeshSlots, m_SlotSortItems, m_SortScratch);
for (const uint32_t slot : m_UsedMeshSlots)
{
	const uint32_t usage = m_MeshUsage[slot];
	const AssetHandle handle = renderScene.GetMeshHandle(slot);
	Ref<Mesh> mesh;
	if ((usage & (c_UseView | c_UseHigh)) != 0)
	{
		mesh = m_Assets.Resolve<Mesh>(handle, (usage & c_UseHigh) != 0 ? AssetPriority::High : AssetPriority::Normal);
	}
	else
	{
		if ((usage & c_UsePrefetch) != 0)
			m_Assets.Prefetch(handle);
		if ((usage & c_UseShadow) != 0)
			mesh = m_Assets.FindResident<Mesh>(handle);
	}
	// Held by the resolve cache until the frame ends; RenderScene::Sync keeps the mesh's layout current. Its place in the
	// geometry pool is read once per frame (compaction moves it between frames).
	const GeometryAllocation* geometry = mesh ? mesh->GetGeometry() : nullptr;
	m_FrameMeshes[slot] = geometry ? mesh.get() : nullptr;
	if (geometry)
		m_FrameGeometry[slot] = *geometry;
```

1. **Line 708:** the used slots are sorted first, so requests come in slot order.
2. **Lines 715–717:** a slot in view resolves the mesh, at High when the High bit is set.
3. **Lines 718–724:** out of view, a nearby slot is prefetched and a shadow caster is only found if resident.
4. **Lines 726–730:** the geometry place is read once per frame and a mesh without geometry leaves a null slot.

The branches decide the call. A slot drawn in view calls `Resolve`, at High when `c_UseHigh` is set and at Normal otherwise. A slot out of view may call `Prefetch`, which requests the load at Low and does not use the asset. A slot that casts a shadow from outside the view calls `FindResident`, so a caster that is not loaded costs nothing and starts no load. The place of the mesh's geometry in the shared pool is read once, here, because compaction can move it between frames.

Each mesh mark carries a second copy of the four flags, four bits higher, meant for the mesh's submesh materials. The loop reads that copy and marks those materials with it, so a material is as urgent as the most urgent mesh that uses it. A proxy with its own override material marks that material directly.

### One lookup per handle

The cache is the heart of the page. An **asset resolve cache** is a per-renderer table that answers each :term[asset handle]{id=asset-handle} once per frame and holds the answers, and their references, until the frame ends. `LookUp` is where a call turns into work.

```cpp src="Strata/src/Strata/Renderer/AssetResolveCache.cpp#L98-L133" symbol="AssetResolveCache::LookUp"
uint8_t AssetResolveCache::LookUp(Entry& entry, AssetHandle handle, AssetPriority priority, bool residentOnly)
{
	// Answered this frame: a request answers everything; a resident lookup answers other resident lookups, and requests
	// when it found the asset loaded.
	if ((entry.Lookups & c_Requested) != 0 || ((entry.Lookups & c_LookedUp) != 0 && (residentOnly || entry.Resolved)))
		return 0;

	if (residentOnly)
	{
		entry.Lookups |= c_LookedUp;
		m_Stats.ResidentLookups++;
		if (m_Manager->GetAssetState(handle) == AssetState::Ready)
		{
			entry.Resolved = m_Manager->GetAsset(handle, priority);
			m_Stats.GetAssetCalls++;
			if (entry.Resolved)
				m_Used.push_back(&entry);
		}
		return c_LookedUp;
	}

	entry.Lookups |= c_Requested;
	entry.Resolved = m_Manager->GetAsset(handle, priority);
	m_Stats.GetAssetCalls++;
	m_Stats.Requested++;
	if (entry.Resolved)
	{
		m_Used.push_back(&entry);
	}
	else if (m_Manager->GetAssetState(handle) == AssetState::Loading)
	{
		// Unknown handles stay Unloaded and failed ones Failed: only assets on their way are pending.
		m_Stats.Pending++;
	}
	return c_Requested;
}
```

1. **Lines 102–103:** a request answers everything, and a resident lookup answers resident lookups; these calls return at once.
2. **Lines 105–116:** a resident lookup fetches only an asset whose state is `Ready`, so it starts no load.
3. **Lines 119–122:** a request calls `GetAsset` once with the priority and counts it.
4. **Lines 127–131:** only an asset in the `Loading` state counts as pending.

Each entry remembers what the frame asked of it in a few flags. At the top, a request answers everything: once `c_Requested` is set, later calls return at once, and the count of manager calls stays at one. A resident lookup answers other resident lookups, and answers a request only when it found the asset loaded.

The resident branch looks at the asset's state first. Only a `Ready` asset is fetched, so a resident lookup cannot start a load. The request branch calls `GetAsset` with the priority, which starts or raises a load and stamps the asset as used. If the asset is not there and its state is `Loading`, it counts as pending. Unknown and failed handles are not counted, because nothing is on its way.

At `EndFrame` the cache walks its list of entries that hold references and lets each one go, then lets go of the manager. A renderer that stops rendering for a while, such as a capture renderer between captures or a hidden view, then keeps nothing alive. The GPU work already recorded keeps what it needs by itself: :term[command lists]{id=command-list} hold their buffers and the bindless table holds its textures.

:::why[A table that forgets everything every frame]
A cache that kept answers across frames would be faster, but it would hold references, and a held reference blocks eviction. It would also answer with an object the manager had already replaced. Forgetting costs one manager call per distinct handle per frame. Replay, below, removes most of that cost where nothing changed.
:::

### Recording and replay

A still frame, with the camera and the scene unchanged, asks for the same thousands of materials and textures as the frame before. Asking one by one costs a lock of the manager for every handle. A **replay** is a later frame's repeat of an earlier frame's lookups in one call to the manager, `TouchLoadedAssets`, which takes the lock once and stamps every asset as used.

`ResolveMaterials` calls `BeginRecording`, resolves the materials, and calls `EndRecording`. The recording holds the distinct handles, sorted, and a weak pointer to each loaded object. Weak pointers matter: a recording must not keep an asset from being dropped. The recording is refused if any lookup found nothing, because an asset that is loading cannot be touched.

```cpp src="Strata/src/Strata/Renderer/SceneRendererExtraction.cpp#L745-L777" symbol="SceneRenderer::ReuseResolvedMaterials"
bool SceneRenderer::ReuseResolvedMaterials(const RenderScene& renderScene)
{
	const MaterialResolution& resolution = m_MaterialResolution;
	if (!resolution.Valid || resolution.RenderSceneId != m_RenderSceneId || resolution.Slots.size() != m_UsedMaterialSlots.size())
		return false;
	for (size_t index = 0; index < resolution.Slots.size(); index++)
	{
		const MaterialResolution::Slot& resolved = resolution.Slots[index];
		const uint32_t slot = m_UsedMaterialSlots[index];
		if (resolved.Index != slot || resolved.Usage != m_MaterialUsage[slot] || resolved.Handle != renderScene.GetMaterialHandle(slot))
			return false;
	}
	// The data names textures by table index, the same for a texture's life: the textures being the same objects (the
	// replay) is all the data needs.
	if (!m_Assets.Replay(resolution.Lookups))
		return false;

	for (const MaterialResolution::Slot& resolved : resolution.Slots)
	{
		if ((resolved.Usage & (c_UseView | c_UseHigh | c_UseShadow)) == 0)
		{
			// Prefetched only (not recorded): requested again as ResolveMaterials does, which keeps loads that are not done
			// on their way.
			m_Assets.Prefetch(resolved.Handle);
			continue;
		}
		m_MaterialFlags[resolved.Index] = resolved.Flags;
		if ((resolved.Usage & (c_UseView | c_UseHigh)) != 0)
			m_Stats.Materials++;
		m_Stats.ReusedMaterials++;
	}
	return true;
}
```

1. **Lines 748–755:** the previous frame must have the same scene, slot count, indices, use bits and handles.
2. **Line 759:** `Replay` makes every recorded lookup in one call, or returns false and changes nothing.
3. **Lines 764–769:** slots that were only prefetched are requested again, because they were not recorded.
4. **Lines 771–774:** the flags and the counts are those of the recorded frame.

The test for a repeat is strict on purpose. The same :term[render scene]{id=render-scene}, the same number of slots, and in each slot the same index, the same use bits and the same material handle must match. Any difference returns false and the frame resolves as usual. Then `Replay` checks that every recorded asset is still loaded as the same object. If one is gone, it changes nothing and returns false.

Slots that were only prefetched are not recorded, since a request for what is not yet loaded must be made again. The loop at the end calls `Prefetch` for them, so loads in progress stay on their way. The statistics count as they did when recorded, so a replayed frame reports the same numbers.

### What happens when something is not loaded

The renderer never waits, so each missing asset needs a stand-in.

```cpp src="Strata/src/Strata/Renderer/SceneRendererExtraction.cpp#L823-L834" from="// The default material stands in" to="m_MaterialUVScales[slot] = 1.0f;" symbol="SceneRenderer::ResolveMaterials"
// The default material stands in while the material loads (or when it never will).
replayable = false;
if (!m_DefaultMaterialFlags)
{
	const Ref<Material> fallback = m_Assets.Resolve<Material>(BuiltinAssets::DefaultMaterial, AssetPriority::High);
	if (fallback)
		ResolveMaterialTextures(*fallback, false, nullptr);
	// Without an asset manager with built-in assets nothing can be drawn with this material.
	m_DefaultMaterialFlags = fallback ? MaterialGPU::GetFlags(fallback->GetProperties()) : 0u;
}
flags = *m_DefaultMaterialFlags;
m_MaterialUVScales[slot] = 1.0f;
```

1. **Line 824:** a frame that used the default material cannot be replayed.
2. **Line 827:** the default material is resolved at High priority, once.
3. **Line 831:** without :term[built-in assets]{id=built-in-asset} the flags are zero and nothing is drawn.
4. **Lines 833–834:** the slot takes the default flags and a texture scale of 1.

An unloaded material draws as the default material, resolved from `BuiltinAssets::DefaultMaterial` at High priority. The code remembers its flags, so the lookup happens once. If no asset manager has :term[built-in assets]{id=built-in-asset}, the flags are zero and nothing is drawn with that material. A frame that used the default material cannot be replayed, because the real material must be asked for again next frame. [Materials](../light/materials.md) teaches what the default material holds.

An unloaded mesh has no geometry, so `ResolveAssets` stores a null mesh for its slot and the draw is skipped. A mesh of unknown bounds is requested as if in view, as above. These choices cost a visible pop when an asset arrives, and the streaming view below shows them.

### What the frame publishes

After the draws are sorted, the renderer lists what the frame drew. Each material with a drawn pixel size gets a `VisibleMaterialUse` with the largest projected size in pixels, the largest tiling of its :term[texture coordinates]{id=texture-coordinates} (:term[UV]{id=texture-coordinates}) and the UV pixels. The UV pixels count how many pixels one unit of texture coordinates spans.

The frame also lists each loaded texture of those materials. The texture streamer reads both lists through `GetVisibleMaterials` and `GetVisibleTextures`, so it searches nothing itself. [Mip streaming](../draw/mip-streaming.md) teaches how it chooses levels from them.

### Seeing the requests

The editor shows the result. Click the debug view chip of the Scene view, which reads "Lit" while no debug view is chosen, and choose "Streaming"; or run `viewport.setSettings` with `debugView` set to `streaming`. Entities whose assets are still loading are tinted, entities whose assets failed get a second tint, and an entity whose mesh is missing is drawn as a box. The view is declared in `StreamingView.h` in `StrataEditor/src/Editor/`, and the editor's theme sets its colours. [Debug views](../gpu/debugging.md) teaches how such views are drawn.

Open the `OpenWorld` sample with the view chosen: loading entities are tinted until their requests are answered, and a legend counts them. The picture below comes from after the opening, so nothing is tinted.

::figure{id=streaming-view-opening}

The second figure shows one corner twice, some seconds apart; both legends read zero, because that corner had loaded before the first picture.

::figure{id=request-priorities variant=early}

::figure{id=request-priorities variant=later}

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Load everything at start | Small games | No requests at all | Worlds larger than memory |
| Request by distance only | Simple :term[loaders]{id=loader} | No :term[screen fraction]{id=screen-fraction} to compute | Large far objects arrive late, small near ones early |
| Cache references across frames | Many custom :term[loaders]{id=loader} | Fewer manager calls | Eviction blocked by held references |
| Priority labels set by artists | Level-design tools | Control of the order | Labels that fall out of date |
| Feedback from the GPU only | Virtual texturing engines | Exact visibility | A frame of delay, and nothing for the first frame |

Strata does use the GPU's feedback as well, in the GPU-driven path. [GPU-driven drawing](../draw/gpu-driven.md) teaches it.

## How it is tested

The suite `Renderer.AssetResolveCache`, in `StrataTests/src/Renderer/AssetResolveCacheTests.cpp`, has four cases. They check that each asset is asked for once per frame and let go at its end, and that no asset manager stays alive between frames. They also check that resident lookups start no loads, that prefetches ask at Low priority, and that a later frame replays loaded lookups in one call.

Run it with the test binary and a filter:

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=Renderer.AssetResolveCache
```

Every case must pass before a change to the cache lands.

## Changing it safely

Add a new kind of request to a pass by marking a use bit in culling and reading it in `ResolveAssets`; never call the manager from the pass. Each new call into the cache needs a place in recording, or replay will skip it and the stamps will differ. Keep the statistics in `AssetResolveStats` true, because tests and the streaming view read them.

Three rules apply. Do not hold a `Ref` past `EndFrame`, or eviction stops working. Do not block on a load, or one slow file stalls a frame. Do not ask for assets per entity, or the cost grows with entities instead of assets. The checks to pass are the `Renderer.AssetResolveCache` suite, the GPU suites for the renderer, and the feature test.

## Summary

- A mesh's request comes from what the camera sees: High above a screen fraction of 0.05, Normal below it, Low within the prefetch distance, and a resident-only lookup for an off-view shadow caster.
- The resolve cache asks the manager once per handle per frame and lets go of every reference at the frame's end, so what left the view can be dropped.
- A frame that matches the one before it repeats that frame's lookups in one call when every slot, use bits and handle match and every asset is still loaded as recorded.
- An unloaded material draws as the default material, an unloaded mesh is skipped, and a mesh of unknown bounds is requested as if in view.

## Check yourself

1. A cube has a bounding sphere of radius 1. The camera's vertical field of view is 90 degrees, so the tangent of half of it is 1. At what distance does the cube stop being High priority?

   :::answer{tests="priority-from-view"}
   The fraction is the radius divided by the distance times the tangent, so 1 divided by the distance. It equals 0.05 at 20 units. Closer than 20 units the cube is High, and farther it is Normal.
   :::

2. A frame resolves handle `A` three times and `B` once. How many manager calls does the cache make, and what happens to the references at the frame's end?

   :::answer{tests="cache-once"}
   Two calls, one per distinct handle. At `EndFrame` the cache lets go of both references, so a manager that wants to drop them finds no outside holder.
   :::

3. A scene stands still, but one material was still loading in the last frame. Does the next frame replay? (a) Yes, the slots are the same. (b) No, a recording is refused when a lookup found nothing. (c) Yes, but only for textures.

   :::answer{tests="replay-rule"}
   Option (b). The last frame drew the default material for the loading one, so its recording was refused and the next frame resolves one by one. Option (a) ignores that an asset that is loading cannot be touched. Option (c) names no rule of the engine.
   :::

4. What does a frame draw for a mesh that is not loaded, and for a material that is not loaded?

   :::answer{tests="fallbacks"}
   The mesh has no geometry, so its draw is skipped. The material draws as the default material until the real one loads. A mesh of unknown bounds is also requested as if in view.
   :::

## Exercises

1. **Basic.** Run the sketch below, and then change the distance of cube B so that it becomes High. State the distance at which it changes.

   :::answer[Worked solution]{tests="priority-from-view" solution="sketches/draw-asset-requests-priority.cpp"}
   The program computes the fraction for each cube and chooses a call from it and from the cube's place. Cube B is at 60 units with a fraction of 0.025. It becomes High when the fraction passes 0.05, at 30 units.

   ```cpp sketch="draw-asset-requests-priority.cpp"
   #include <cmath>
   #include <cstdio>

   constexpr float c_HighFraction = 0.05f;
   constexpr float c_PrefetchDistance = 100.0f;
   constexpr float c_Pi = 3.14159265f;

   struct Cube
   {
   	const char* Name;
   	float Distance;
   	bool InView;
   	bool CastsShadow;
   };

   // The bounding sphere's diameter over the height of the view at that distance.
   float GetScreenFraction(float radius, float distance, float verticalFov)
   {
   	return radius / (distance * std::tan(verticalFov * 0.5f));
   }

   void Describe(const Cube& cube, float radius, float verticalFov)
   {
   	if (cube.InView)
   	{
   		const float fraction = GetScreenFraction(radius, cube.Distance, verticalFov);
   		std::printf("%s: fraction %.3f, %s\n", cube.Name, fraction, fraction > c_HighFraction ? "Resolve at High" : "Resolve at Normal");
   		return;
   	}
   	if (cube.Distance <= c_PrefetchDistance)
   		std::printf("%s: out of view, within the prefetch distance, Prefetch\n", cube.Name);
   	if (cube.CastsShadow)
   		std::printf("%s: out of view, casts a shadow, FindResident\n", cube.Name);
   }

   int main()
   {
   	// A cube of side 1 has a bounding sphere of radius 0.866; the vertical field of view is 60 degrees.
   	const float radius = 0.866f;
   	const float verticalFov = c_Pi / 3.0f;
   	const Cube cubes[] = {
   		{ "A", 7.5f, true, false },
   		{ "B", 60.0f, true, false },
   		{ "C", 40.0f, false, false },
   		{ "D", 150.0f, false, true },
   	};
   	for (const Cube& cube : cubes)
   		Describe(cube, radius, verticalFov);
   	return 0;
   }
   ```

   ```text output-of="draw-asset-requests-priority.cpp"
   A: fraction 0.200, Resolve at High
   B: fraction 0.025, Resolve at Normal
   C: out of view, within the prefetch distance, Prefetch
   D: out of view, casts a shadow, FindResident
   ```

   1. **Lines 17–20:** the fraction is the sphere radius over half the height of the view at that distance.
   2. **Lines 24–29:** a cube in view gets High above 0.05 and Normal otherwise.
   3. **Lines 30–33:** a cube out of view is prefetched within 100 units, and a shadow caster is found if resident.

   :::

2. **Medium.** A frame has 500 entities that use 40 distinct meshes and 25 distinct materials, and each material has two textures. How many manager calls does the cache make if all are loaded and no replay happens? How many if the next frame replays?

   :::answer[Worked solution]{tests="cache-once,replay-rule"}
   The cache makes one call per distinct handle: 40 meshes, 25 materials and 50 textures, which is 115 calls, however many entities draw them. A replay of the materials' lookups makes one call to the manager for all 25 materials and their textures, so the frame makes 40 mesh calls plus 1.
   :::

3. **Hard.** Trace it yourself. Three cubes use three different mesh assets: one fills a fifth of the view, one is far and small in view, and one is out of view within 100 units. Predict each request, then follow each mesh slot's use bits with a breakpoint in `ResolveAssets`.

   :::answer[Worked solution]{tests="priority-from-view,fallbacks"}
   The function is `SceneRenderer::ResolveAssets` in `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp`. The first cube has `c_UseView | c_UseHigh` and calls `Resolve` at High. The second has `c_UseView` and calls `Resolve` at Normal. The third has `c_UsePrefetch` and calls `Prefetch`. Each mark repeats its bits four places higher for the submesh materials, so the debugger shows 51, 17 and 68.

   If the cubes shared one mesh, its slot would hold the combined bits of all three and the request would be High. The test `Resident lookups never start loads; prefetches request at low priority` covers the same calls.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Renderer/AssetResolveCache.h` and `.cpp`: the cache, `LookUp`, recording and replay.
- `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp`: use bits, `MarkVisibleProxies`, `ResolveAssets`, `ReuseResolvedMaterials`, `ResolveMaterials`.
- `Strata/src/Strata/Renderer/SceneRenderer.h`: `HighPriorityScreenFraction`, `PrefetchDistance`, `VisibleMaterialUse`.
- `StrataEditor/src/Editor/StreamingView.h`: the streaming view.
- `StrataTests/src/Renderer/AssetResolveCacheTests.cpp`: the suite `Renderer.AssetResolveCache`.

## Further reading

- Game Programming Patterns, "Data Locality" and "Object Pool" (Robert Nystrom): why engines keep working sets small. Beginner.
- Jason Gregory, Game Engine Architecture, the chapter on resource management: loading, streaming and caching in shipped engines. Intermediate.
