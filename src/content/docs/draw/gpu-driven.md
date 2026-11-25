---
id: draw/gpu-driven
title: "GPU-driven culling and indirect drawing"
description: "How Strata culls the render scene and builds each frame's draw commands on the GPU, and how its visibility feedback tells the CPU what to load."
kind: internals
size: XL
tracks: [E]
needs: [draw/lod, draw/mirrors-camera-relative, draw/render-scene-gpu, gpu/compute, gpu/readback-timing]
time: 120
learn:
  - id: trace-proxy
    text: trace one proxy from the culling shader to the indirect call that draws it
  - id: count-first
    text: explain why Strata counts first and writes second instead of appending with one atomic
  - id: twin-rules
    text: name what must change on both paths when a culling rule changes
  - id: indirect-path
    text: choose the indirect draw mode a device gets and the slots a bucket draws
  - id: feedback-late
    text: predict how late a request driven by feedback comes and when the CPU walks the view instead
since: 0.4.0
status: final
---

Every frame, the :term[renderer]{id=renderer} must decide which meshes of the :term[render scene]{id=render-scene} the camera can see, which :term[level of detail]{id=level-of-detail} (LOD) each one needs, and which of them can share one :term[draw command]{id=draw-list}. With a million objects, that decision costs more than the drawing. This page teaches how Strata hands the decision to the :term[graphics processing unit]{id=gpu} (GPU). The cost on the :term[central processing unit]{id=processor} (CPU) then no longer follows the number of objects, and the picture stays the one the CPU's own path draws.

The page does not teach four topics. They are how the sun's cascades and the local lights' shadow views choose their casters, the second culling phase against a depth pyramid, skinned meshes, and the order rules of the forward :term[shader]{id=shader}. Each has its own page, and the text links it where the code first touches it.

## The problem and how engines solve it

Imagine a game with 1,000,000 crates, each a :term[render proxy]{id=render-proxy} with a box around it. The camera sees a few thousand. To find them, a CPU loop tests every box against the six planes of the view, and each test reads 24 :term[bytes]{id=byte} of bounds and does a few dozen multiplications. If one test costs 20 ns (an assumption for the arithmetic, not a measurement), the loop costs 1,000,000 × 20 ns = 20 ms. A frame at 60 :term[frames per second]{id=frame-rate} lasts 16.7 ms, so the loop alone is too slow.

Two things make the loop a poor fit. Its cost follows the number of proxies, not the number of crates you see. And the GPU, which has thousands of threads and already holds the proxies' data in the [GPU copy of the render scene](render-scene-gpu.md), sits idle while the CPU works.

Engines solve the problem in one of three ways:

- **Cull on the CPU, draw on the GPU.** This is simple and portable, and its cost follows the proxies. Strata keeps this path as its fallback.
- **Cull on the GPU, read the result back.** The CPU then builds the draw commands. The GPU's answer arrives frames late, or the CPU waits for it.
- **Cull on the GPU and let it write the draw commands.** The CPU issues a few :term[indirect draw]{id=indirect-draw} calls, and the GPU wrote their arguments into a buffer. Two conference talks, in 2015 and 2016, describe this for shipped games (see Further reading).

An indirect draw call takes its arguments from a buffer. There are five numbers: how many indices to draw, how many instances, where the indices start in the pool, where the vertices start, and the number of the :term[first instance]{id=first-instance}. In the 1,000,000 crates, the GPU writes one such record per mesh level, not one per crate. Say the crates use a cube of 36 indices (12 triangles), 3 of them are visible, and their range of the draw list starts at 5. The record reads 36, 3, the cube's place in the pool, its vertex base and 5, where the place and the base are invented numbers.

**GPU-driven rendering** is the third way: the GPU selects what to draw and builds its own draw commands. It has one hard part, which is packing. Each thread tests one proxy, and the survivors must form a list that one instanced draw can read. All instances of one mesh level and one pipeline state must stand side by side, because one draw call covers one range of the list.

The obvious way to pack is one atomic counter. Every surviving thread adds one to it and writes its instance at the place it got. That takes one pass, but the list has no groups: where the first thread of a mesh writes depends on timing, and a draw call needs the instances of its mesh in one range.

Strata counts first and writes second. A **counting pass** runs the culling decisions and only adds one to a counter per draw record; a **write pass**, the same decisions run a second time, then places each instance inside its record's range. Between the two passes, a build step turns the counts into ranges.

:::example[Ten proxies and three records]
Take the ten proxies of the table, where a record is a mesh level of the draw.

| Proxy | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| In view | yes | yes | no | yes | yes | yes | no | yes | yes | yes |
| Record | 2 | 0 | 1 | 2 | 0 | 1 | 0 | 2 | 0 | 1 |

The counting pass finds 3 instances for record 0 (proxies 1, 4 and 8), 2 for record 1 (5 and 9) and 3 for record 2 (0, 3 and 7). The build step gives them the ranges starting at 0, 3 and 5, in a list of 8 entries. In the write pass each thread places its proxy inside its record's range, and the three draws read entries 0 to 2, 3 to 4 and 5 to 7. Which of the three proxies of record 2 lands first depends on timing, and no draw cares.
:::

:::why[Two passes instead of one atomic append]
The draw's arguments need the instance count of each record before any instance is written, and the instances of a record need a range of their own. Counting first gives both. The cost is that the culling decisions run twice per frame, and that every decision must come out the same in both passes. Strata accepts this because the decisions are cheap next to a draw call, and because a draw per record needs no sorting afterward.
:::

## The map: passes, buffers and buckets

A frame's culling is a chain of compute passes over a few buffers. The diagram shows the chain for the view. The sun's cascades and the local shadow views go through the same passes with more buckets.

```mermaid caption="The GPU path counts, builds, then writes, and the indirect draws read the arguments and the draw list." alt="A flow from the proxies and the tables into the counting pass of the culling shader. The counts feed the build shader and the feedback shader. The build shader writes offsets, arguments and a draw count per bucket. The write pass of the culling shader then fills the draw list, and the indirect calls of each bucket read the arguments, the counts and the list."
flowchart TD
  P["proxies, 64 bytes each"] --> C1["Cull.comp: counting pass"]
  T["geometry tables, material flags"] --> C1
  C1 --> N["counts per bucket and LOD record"]
  N --> B["CullBuild.comp"]
  N --> F["CullFeedback.comp"]
  B --> O["offsets, arguments, draws per bucket"]
  O --> C2["Cull.comp: write pass"]
  C2 --> D["draw list"]
  O --> X["DrawGPUBucket: one indirect call per bucket"]
  D --> X
```

The :term[main thread]{id=main-thread} records all of it into one :term[command list]{id=command-list}, and the GPU runs it. The :term[geometry pool]{id=geometry-pool} owns the tables, the render scene's GPU copy owns the proxies and materials, and `SceneRenderer` owns the culling buffers, most of whose names start with `m_Cull`. The CPU reads nothing back to draw: only the statistics and the feedback come back, frames later.

| Buffer | Written by | Holds |
| --- | --- | --- |
| `m_CullCountBuffer` | counting pass, then write pass | one count per key (dense bucket, LOD record) |
| `m_CullOffsetBuffer` | build step | each key's range start in the draw list, or none |
| `m_CullArgumentBuffer` | build step | five-word indirect arguments, per bucket slot |
| `m_CullBucketCountBuffer` | build step | the number of draws in each bucket |
| `m_GPUDrawListBuffer` | write pass | one entry per drawn instance |
| `m_CullCounterBuffer` | all passes | the frame's statistics |

A **bucket** is a group of draws that share a pipeline state and a vertex arena. The shader names a bucket with a number, and that number has a layout of its own.

```mermaid caption="A bucket index has three ranges: the view's, the cascades' and the local shadow views'." alt="Three boxes in a row. The first covers indices 0 to 31 for the view, with bits for mirrored, double-sided, geometry and second phase. The second covers 32 to 351, five cascades of 64 buckets each. The third covers 352 to 735, twelve local shadow views of 32 buckets each."
flowchart LR
  V["0 to 31: view buckets"] --> VB["bit 0 mirrored, bit 1 double-sided, bits 2 and 3 geometry, bit 4 second phase"]
  S["32 to 351: five cascades of 64"] --> SB["a view bucket's bits, plus bit 4 alpha mask and bit 5 second phase"]
  L["352 to 735: twelve local views of 32"] --> LB["a view bucket's bits, plus bit 4 alpha mask"]
```

:::example[Three bucket numbers]
A mirrored, double-sided, posed skinned instance in the view: 1 + 2 + (2 × 4) = 11. An alpha-masked, single-sided, static caster in cascade 2: 32 + 2 × 64 + 16 = 176. A mirrored static instance in local shadow view 3: 352 + 3 × 32 + 1 = 449. The last index of all is 735, so the table has 736 entries.
:::

Most of the 736 buckets never occur: a scene without mirrored proxies has no odd buckets. A table of dense indices maps the buckets a frame can have to the numbers 0, 1, 2 and so on, so the count, offset and argument buffers hold only those. The other buckets map to the value `c_CullNoBucket`.

## The contract: what callers may assume

The GPU path promises the picture of the CPU's path, and each rule below protects that promise.

- **The path is chosen per renderer.** The `GPUDriven` field of `SceneRendererSpecification` is `Auto` or `Off`. `Auto` runs on the GPU only when the culling shaders and resources exist and the device has the `drawIndirectFirstInstance` feature. Otherwise the renderer draws through the CPU path, and a renderer whose resources cannot be created does the same and keeps none of them.
- **The switch is set in code.** No editor setting changes `GPUDriven`. Only the command `viewport.capture` turns the path off, for one picture, through the `GPUDriven` switch of its `renderer` parameter; otherwise the editor shows only whether the draws of a frame came from the GPU.
- **Thumbnails force the CPU path.** A thumbnail shows a few objects of a scene that no other frame will draw, so the path's fixed costs per frame and per scene buy nothing (`SceneRenderer.cpp`, the thumbnail specification).
- **Transparent materials stay with the CPU.** Their sorted pass needs back to front order, and the GPU places instances in scheduling order.
- **Shading cannot depend on draw order.** The GPU stores the instances of a record in scheduling order, so a pixel must come out the same whatever order its triangles arrive in. The derivative rule behind this is taught in [lighting and the forward shader](../light/brdf.md).

:::rule[Change the CPU rule and the GPU rule together]
Every culling decision exists twice: in `Cull.comp` and in the CPU's code (`CullView`, `FindShadowCasters`, `GatherDraws`, `GatherShadowDraws`). A change to one without the other makes the two paths draw different pictures, and the test suite `GPU.SceneRenderer.GPUDriven` fails. See [Architecture rules](https://github.com/2042Third/GameEngine/blob/319075e3f92b316db5cdd30560de08c1ffe0ae26/AGENTS.md).
:::

:::rule[Clear in the empty-scene branch what the frame reads without proxies]
A render scene that never had a proxy skips the culling passes, yet the lights' counts and the statistics still read the counters. `RunGPUCulling` clears them in a branch of its own. Any resource that the frame reads without proxies needs its clear in that branch as well. See [the GPU-driven path in the engine's guide](https://github.com/2042Third/GameEngine/blob/319075e3f92b316db5cdd30560de08c1ffe0ae26/Docs/DeveloperGuide.md#gpu-driven-path).
:::

:::rule[Put explicit barriers between culling dispatches]
:term[NVRHI]{id=nvrhi} places a barrier when the :term[binding set]{id=binding-set} changes. All culling passes use one set, so each pass needs `CullBarrier` before it can read what the pass before wrote. See [Architecture rules](https://github.com/2042Third/GameEngine/blob/319075e3f92b316db5cdd30560de08c1ffe0ae26/AGENTS.md).
:::

Every rule has one reason: a picture that differs between the paths is a bug in one of them, and nobody can tell which without the twin. That is why the tests compare the paths with each other, not with stored images.

Tests follow two more rules. A test that counts draws renders one frame more, or disables occlusion, because the first frames draw by their own rules. A test of requests waits for the feedback or disables it, as the last sections show.

## A toy version: count first, then write

:::question
The toy uses functions, a `struct` and `std::vector`, and passes values by reference. If those are new, read [programming 2](../basics/programming-2.md) and [programming 3](../basics/programming-3.md) first.
:::

The toy runs the table's ten proxies through a counting pass, a build step and a write pass. A loop stands in for the GPU's threads: it visits the proxies in an order given as a list, and the program runs twice, forward and backward, to show that timing changes nothing that matters. Look at `Emit`, which both passes call.

```cpp sketch="draw-gpu-driven-toy.cpp"
#include <cstdint>
#include <cstdio>
#include <vector>

constexpr uint32_t c_Records = 3;
constexpr uint32_t c_None = 0xFFFFFFFFu;

// A thing the scene could draw: its record names the mesh level and material it would use.
struct Proxy
{
	bool Inside;
	uint32_t Record;
};

struct Cull
{
	std::vector<uint32_t> Counts = std::vector<uint32_t>(c_Records, 0);
	std::vector<uint32_t> Offsets = std::vector<uint32_t>(c_Records, 0);
	std::vector<uint32_t> DrawList;
};

// Both passes call this. Counting adds one to the record's count; writing counts it down and uses the result as the
// place inside the record's range, so the count ends at zero.
void Emit(Cull& cull, bool writing, uint32_t proxy, uint32_t record)
{
	if (!writing)
	{
		cull.Counts[record]++;
		return;
	}
	cull.Counts[record]--;
	cull.DrawList[cull.Offsets[record] + cull.Counts[record]] = proxy;
}

// One "thread" per proxy: the same decision in both passes.
void CullProxy(Cull& cull, const std::vector<Proxy>& proxies, bool writing, uint32_t index)
{
	if (proxies[index].Inside)
		Emit(cull, writing, index, proxies[index].Record);
}

// The build step: a running total gives each record its range of the draw list.
void Build(Cull& cull)
{
	uint32_t total = 0;
	for (uint32_t record = 0; record < c_Records; record++)
	{
		cull.Offsets[record] = total;
		total += cull.Counts[record];
	}
	cull.DrawList.assign(total, c_None);
}

void Run(const std::vector<Proxy>& proxies, const std::vector<uint32_t>& order, const char* name)
{
	Cull cull;
	for (const uint32_t index : order)
		CullProxy(cull, proxies, false, index);
	Build(cull);
	std::printf("%s: counts %u %u %u, starts %u %u %u\n", name, cull.Counts[0], cull.Counts[1], cull.Counts[2],
		cull.Offsets[0], cull.Offsets[1], cull.Offsets[2]);
	for (const uint32_t index : order)
		CullProxy(cull, proxies, true, index);
	std::printf("%s: draw list", name);
	for (const uint32_t entry : cull.DrawList)
		std::printf(" %u", entry);
	std::printf("\n");
}

int main()
{
	const std::vector<Proxy> proxies = { { true, 2 }, { true, 0 }, { false, 1 }, { true, 2 }, { true, 0 },
		{ true, 1 }, { false, 0 }, { true, 2 }, { true, 0 }, { true, 1 } };
	Run(proxies, { 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 }, "forward");
	Run(proxies, { 9, 8, 7, 6, 5, 4, 3, 2, 1, 0 }, "backward");
	return 0;
}
```

```text output-of="draw-gpu-driven-toy.cpp"
forward: counts 3 2 3, starts 0 3 5
forward: draw list 8 4 1 9 5 7 3 0
backward: counts 3 2 3, starts 0 3 5
backward: draw list 1 4 8 5 9 0 3 7
```

1. **Lines 26–29:** the counting pass only adds one to the record's count; on the GPU this is `InterlockedAdd` on a buffer.
2. **Lines 31–32:** the write pass counts the record down and uses the result as the place in its range; the count ends at zero.
3. **Lines 43–52:** the build step turns counts into starts with a running total and sizes the list.
4. **Lines 74–75:** the same proxies visited in two orders.

Both runs give the counts 3, 2, 3 and the starts 0, 3, 5, as the example predicted. Inside a record the order differs: forward puts proxy 7 first in its range, backward puts proxy 0 first. The ranges, and so the draws, are the same.

The toy omits what the engine adds: many buckets, levels of detail, overflow, feedback and real atomics. It also runs its threads one after another, so it cannot show a race. The real code below keeps the toy's shape: one function emits for both passes, and the build step sits between them.

The two passes must agree. Suppose the counting pass counted 2 instances for a record, but the write pass finds 3 of them visible, because an input changed between the passes. Without a guard, the third thread counts the record down from 0 to 4,294,967,295, the largest 32-bit number, and writes far outside the record's range. The engine takes care of one such input, the fade state of a level of detail: `EmitViewInstances` reads it in both passes and stores it only in the write pass.

## The real code, in the order of a frame

The sections follow a frame: the tables the shaders read, the three shader passes, the C++ that runs them and issues the draws, and last the feedback. Each quote is a part of the source, and the numbered notes after it count the lines of the file, so you can find a line by its number.

### The culling tables

The shader needs to know where a mesh's indices live and how many levels it has, without asking the CPU. The geometry pool keeps three tables for this, uploaded with the pool's other data.

```cpp src="Strata/src/Strata/Renderer/GPUSceneData.h#L33-L67"
// A mesh's place in the geometry pool (GeometryPool's entry table, by GeometryHandle).
struct GeometryEntry
{
	uint32_t FirstVertex = 0;
	uint32_t FirstIndex = 0;
	uint32_t FirstSubmesh = 0; // In the submesh table
	uint32_t SubmeshCount = 0;
};
static_assert(sizeof(GeometryEntry) == 16);

struct GeometrySubmesh
{
	uint32_t BaseVertex = 0; // Relative to the mesh's first vertex
	uint32_t FirstLOD = 0;   // In the LOD table: the draw record of each level (GPU culling counts per record)
	uint32_t LODCount = 0;
	uint32_t Flags = 0;                    // c_GeometrySubmesh* bits
	glm::vec4 UVDensity = glm::vec4(0.0f); // xyz: Submesh::UVDensity (texture streaming's UV pixels, from feedback)
};
static_assert(sizeof(GeometrySubmesh) == 32);
// The submesh's levels are chosen by their errors (MeshUtils::HasLODErrors; else by halving the screen fraction).
constexpr uint32_t c_GeometrySubmeshLODErrors = 1u << 0;

// A level of detail of a submesh: the draw record GPU culling counts instances per.
struct GeometryLOD
{
	uint32_t IndexOffset = 0; // Relative to the mesh's first index
	uint32_t IndexCount = 0;
	uint32_t BaseVertex = 0;  // Its submesh's, relative to the mesh's first vertex
	uint32_t Mesh = 0;        // The GeometryHandle the level belongs to (CullBuild reads the mesh's offsets from it)
	float RelativeError = 0.0f; // MeshUtils::GetRelativeLODError of the level's MeshLOD::Error (LODSelection::SelectLODByError)
	uint32_t Reserved0 = 0;
	uint32_t Reserved1 = 0;
	uint32_t Reserved2 = 0;
};
static_assert(sizeof(GeometryLOD) == 32);
```

1. **Lines 34–39:** a `GeometryEntry` per mesh handle says where its vertices and indices start in the pool and which :term[submeshes]{id=submesh} are its own.
2. **Lines 43–49:** a `GeometrySubmesh` per submesh holds its first level, the number of levels and the texture-coordinate density that feedback needs.
3. **Lines 56–62:** a `GeometryLOD` per level is the unit of drawing. The page calls it an **LOD record**: one level of one submesh, the draw record that GPU culling counts instances per.
4. **Line 61:** the record names its mesh, so `CullBuild.comp` can find the mesh's place in the pool from a record number alone.

### One thread per proxy

`CullProxy` runs once per proxy, in a dispatch of `ProxyCount` threads. A million proxies take 15,625 groups of 64 threads, below the limit of 65,535 groups per dispatch; larger counts fill rows of that size. `CullProxy` is the CPU path's `CullView` and `GatherDraws` written in :term[Slang]{id=slang}. Read it for the order of its tests: cheap flags first, then the :term[frustum]{id=view-frustum}, then the size.

```slang src="Strata/shaders/Scene/Cull.comp.slang#L472-L504"
void CullProxy(uint proxyIndex)
{
	GPUProxy proxy = u_Proxies[proxyIndex];
	const uint drawable = ST_PROXY_ACTIVE | ST_PROXY_INDEXED;
	if ((proxy.Flags & drawable) != drawable || proxy.MeshSlot >= u_Cull.MeshSlotCount)
		return;
	bool feedback = IsCounting() && u_Cull.Feedback != 0u;
	uint mesh;
	GeometryEntry entry;
	bool meshDrawable = IsDrawable(proxy, mesh, entry);
	bool skinnedArena = (mesh & ST_CULL_MESH_SKINNED_ARENA) != 0u;
	uint geometry = skinnedArena ? ((proxy.Flags & ST_PROXY_SKINNED) != 0u ? ST_CULL_GEOMETRY_SKINNED : ST_CULL_GEOMETRY_SKINNED_ARENA) : ST_CULL_GEOMETRY_STATIC;
	uint mirrored = (proxy.Flags & ST_PROXY_MIRRORED) != 0u ? 1u : 0u;
	float3 center = (proxy.WorldMin + proxy.WorldMax) * 0.5;
	float3 extents = (proxy.WorldMax - proxy.WorldMin) * 0.5;
	float fraction = GetScreenFraction(center, length(extents));

#ifndef ST_CULL_SHADOW
	// Within the prefetch distance (SpatialIndex::QuerySphere's test): requested at low priority, in view or not.
	float prefetch = u_Cull.ViewParameters.z;
	if (feedback && prefetch > 0.0)
	{
		float3 outside = max(max(proxy.WorldMin - u_Cull.CameraPosition.xyz, u_Cull.CameraPosition.xyz - proxy.WorldMax), float3(0.0));
		if (dot(outside, outside) <= prefetch * prefetch)
		{
			MarkMeshFeedback(proxy.MeshSlot, ST_FEEDBACK_PREFETCH, 0.0);
			MarkProxyMaterials(proxy, ST_FEEDBACK_PREFETCH, false, 0.0, entry);
		}
	}
	// Camera-relative: the frustum's planes and the box, so precision does not depend on the distance from the origin.
	float3 relativeMin = proxy.WorldMin - u_Cull.CameraPosition.xyz;
	float3 relativeMax = proxy.WorldMax - u_Cull.CameraPosition.xyz;
	if (!IsBoxInFrustum(relativeMin, relativeMax))
```

1. **Lines 475–477:** a proxy that is not active and indexed draws nothing; a record of zeros, as for a destroyed proxy, fails here.
2. **Line 487:** the :term[screen fraction]{id=screen-fraction}, the :term[bounding sphere's]{id=bounding-sphere} size against the view, which the level of detail and :term[size culling]{id=size-culling} both use.
3. **Lines 490–500:** the prefetch feedback for proxies near the camera, in view or not; the last sections return to it.
4. **Lines 502–504:** the frustum test works on the box minus the camera position, the camera-relative space of [mirrors and camera-relative drawing](mirrors-camera-relative.md), so far-away scenes keep their precision.

```slang src="Strata/shaders/Scene/Cull.comp.slang#L505-L538"
		return;
	float pixels = fraction * u_Cull.ViewParameters.x;
	if (u_Cull.LODParameters.w > 0.0 && pixels < u_Cull.LODParameters.w)
	{
		// Counted (and shown by the culled view) as the CPU path counts them: among the proxies it could draw.
		if (meshDrawable)
		{
			Count(ST_COUNTER_SIZE_CULLED);
			RecordCulled(proxyIndex, ST_CULLED_BY_SIZE);
		}
		return;
	}
	if (feedback)
	{
		uint use = ST_FEEDBACK_VIEW | (fraction > u_Cull.ViewParameters.w ? ST_FEEDBACK_HIGH : 0u);
		MarkMeshFeedback(proxy.MeshSlot, use, pixels);
		MarkProxyMaterials(proxy, use, meshDrawable, pixels, entry);
	}
	if (!meshDrawable)
		return;
	Count(ST_COUNTER_VISIBLE_PROXIES);
	// Occlusion culled: the first phase draws what the view saw in the previous frame; the second the rest it finds
	// visible against the first phase's depth (CullSecondPhase).
	if (u_Cull.OcclusionParameters.w > 0.5 && (u_Visibility[proxyIndex] & (1u << u_Cull.VisibilityParity)) == 0u)
		return;
	EmitViewInstances(proxy, entry, fraction, geometry, mirrored, 0u);
#else
	if ((proxy.Flags & ST_PROXY_CAST_SHADOWS) == 0u || (proxy.Flags & ST_PROXY_MESH_BOUNDS) == 0u || proxy.InstanceCount == 0u)
		return;
	if ((u_Parameters.Mode & ST_CULL_MODE_LOCAL) == 0u)
		CullCascades(proxyIndex, proxy, meshDrawable, entry, fraction, geometry, mirrored, feedback);
	CullLocalShadowViews(proxy, meshDrawable, entry, geometry, mirrored, feedback);
#endif
}
```

1. **Lines 506–516:** size culling: a proxy in the frustum that covers fewer than `MinProjectedPixels` pixels (0.5 by default) is not drawn. The statistics count it only if it could be drawn, as on the CPU path, and `RecordCulled` keeps it for the **Culled** debug view, which shows what culling omitted and why.
2. **Lines 517–522:** feedback for what the view saw, with the high bit when the proxy is large.
3. **Line 525:** the count of visible proxies, which the statistics and the tests read.
4. **Lines 528–530:** occlusion culling can end the thread here; otherwise `EmitViewInstances` places the proxy's instances.

A small case shows the size test. A proxy that covers 0.4 pixels meets `pixels < 0.5` and leaves the frame, and one that covers exactly 0.5 pixels stays. The perf test of a million cubes says in a comment that its far cubes below half a pixel do not reach the draws.

### Counting and writing through one function

A proxy has one instance per submesh. `EmitViewInstances` finds each instance's material, chooses its level, builds its bucket number and emits it. Transparent materials and materials not loaded yet are skipped: the CPU draws the first group, and nobody draws the second before it loads.

```slang src="Strata/shaders/Scene/Cull.comp.slang#L197-L234"
void EmitViewInstances(GPUProxy proxy, GeometryEntry entry, float fraction, uint geometry, uint mirrored, uint phaseBit)
{
	for (uint submesh = 0u; submesh < proxy.InstanceCount; submesh++)
	{
		uint instance = proxy.FirstInstance + submesh;
		uint materialSlot = u_CullInstances[instance].MaterialIndex;
		uint material = materialSlot < u_Cull.MaterialSlotCount ? u_MaterialFlags[materialSlot] : 0u;
		if ((material & ST_CULL_MATERIAL_AVAILABLE) == 0u || (material & ST_CULL_MATERIAL_TRANSPARENT) != 0u)
			continue;
		GeometrySubmesh geometrySubmesh = u_GeometrySubmeshes[entry.FirstSubmesh + submesh];
		uint lod = ChooseLOD(geometrySubmesh, fraction);
		uint doubleSided = (material & ST_CULL_MATERIAL_DOUBLE_SIDED) != 0u ? 2u : 0u;
		uint bucket = mirrored | doubleSided | (geometry << 2) | phaseBit;
		// A changed level cross-fades: both levels are drawn, with complementary masks. The writing pass keeps the state (an
		// instance is drawn in one phase only, so each frame reads the previous frame's).
		// Submeshes with one level have nothing to fade (nor any state), as on the CPU path.
		bool fades = u_Cull.LODFade != 0u && geometrySubmesh.LODCount > 1u;
		uint fadeCode = 0u;
		uint fadeFrom = lod;
		if (fades)
		{
			uint2 state = UpdateLODFade(u_LODFades[instance], lod, geometrySubmesh.LODCount, u_CullInstances[instance].EntityID, u_Cull.LODFadeFrame, true,
				fadeCode, fadeFrom);
			if (!IsCounting())
				u_LODFades[instance] = state;
		}
		Emit(instance | (fadeCode << ST_CULL_DRAW_ENTRY_INSTANCE_BITS), bucket, geometrySubmesh.FirstLOD + lod);
		Count(ST_COUNTER_VIEW_INSTANCES);
		if (fadeCode != 0u)
		{
			Emit(instance | ((fadeCode + ST_LOD_FADE_OUTGOING) << ST_CULL_DRAW_ENTRY_INSTANCE_BITS), bucket, geometrySubmesh.FirstLOD + fadeFrom);
			Count(ST_COUNTER_VIEW_INSTANCES);
		}
		Count(ST_COUNTER_INSTANCES_PER_LOD + int(min(lod, uint(ST_LOD_STAT_COUNT - 1))));
		if (geometry == ST_CULL_GEOMETRY_SKINNED)
			Count(ST_COUNTER_SKINNED_INSTANCES);
	}
}
```

1. **Lines 204–205:** an unavailable or transparent material skips the instance.
2. **Line 207:** `ChooseLOD` applies the halving or error rule of [levels of detail](lod.md) to the screen fraction, the same rule as the CPU's `SelectLOD`.
3. **Line 209:** the bucket number is the layout of the map section: mirrored, double-sided, geometry, phase.
4. **Lines 213–229:** a level that changed fades: both levels are emitted with complementary masks, and only the write pass stores the new fade state, so the counting pass sees the same state.

`Emit` is where the two passes differ, and they differ in a few lines.

```slang src="Strata/shaders/Scene/Cull.comp.slang#L60-L82"
void Emit(uint instance, uint bucket, uint lodRecord)
{
	uint dense = u_BucketTable[bucket];
	if (dense == ST_CULL_NONE)
	{
		// A bucket the CPU did not expect: never drawn (the counters say so).
		if (IsCounting())
			InterlockedAdd(u_Counters[ST_COUNTER_OVERFLOW], 1u);
		return;
	}
	uint key = dense * u_Cull.LODCapacity + lodRecord;
	if (IsCounting())
	{
		InterlockedAdd(u_Counts[key], 1u);
		return;
	}
	uint offset = u_Offsets[key];
	if (offset == ST_CULL_NONE)
		return; // No room in the draw list (counted by CullBuild)
	uint st_Atomic1; InterlockedAdd(u_Counts[key], 0xFFFFFFFFu, st_Atomic1);
	uint slot = st_Atomic1 - 1u;
	u_CullDrawList[offset + slot] = instance;
}
```

1. **Lines 62–69:** a bucket the CPU did not expect has no dense index. It counts as overflow and is never drawn.
2. **Lines 71–75:** the counting pass adds one to the count of its key, the dense bucket times the LOD capacity plus the record.
3. **Lines 76–78:** a record with no range, because the draw list had no room, writes nothing.
4. **Lines 79–81:** the write pass counts the key down and uses the result as its slot: the toy's `Emit`, with a real atomic.

### Giving each record its range

`CullBuild.comp` runs one thread per key. A key with a count owns a part of the draw list and one slot among its bucket's indirect arguments.

```slang src="Strata/shaders/Scene/CullBuild.comp.slang#L51-L88"
void st_Main()
{
	if ((u_Parameters.Mode & ST_BUILD_RESET_LOCAL) != 0u)
	{
		// Dispatched in rows of at most 65,535 work groups.
		ResetLocalBuckets(st_GlobalInvocationID.x + st_GlobalInvocationID.y * c_CullRowItems);
		return;
	}
	uint key = st_GlobalInvocationID.x;
	if (key >= u_Cull.BucketCount * u_Cull.LODCapacity)
		return;
	uint count = u_Counts[key];
	if (count == 0u)
		return;
	uint dense = key / u_Cull.LODCapacity;
	uint record = key - dense * u_Cull.LODCapacity;
	uint phase = 0u;
	if (dense >= u_Cull.FirstPhaseViewBuckets && dense < u_Cull.ViewBucketCount)
		phase = 2u;
	else if (dense >= u_Cull.FirstLocalBucket)
		phase = ST_BUILD_LOCAL_PHASE;
	else if (dense >= u_Cull.SecondPhaseShadowBuckets)
		phase = 4u;
	if (phase != (u_Parameters.Mode & 14u))
		return;
	uint st_Atomic1; InterlockedAdd(u_Counters[ST_COUNTER_DRAW_LIST_USED], count, st_Atomic1);
	uint offset = st_Atomic1;
	uint st_Atomic2; InterlockedAdd(u_BucketCounts[dense], 1u, st_Atomic2);
	uint slot = st_Atomic2;
	bool listRoom = count <= u_Cull.DrawListCapacity && offset <= u_Cull.DrawListCapacity - count;
	if (!listRoom || slot >= u_Cull.ArgumentsPerBucket)
	{
		u_Offsets[key] = ST_CULL_NONE;
		InterlockedAdd(u_Counters[ST_COUNTER_OVERFLOW], count);
		if (slot < u_Cull.ArgumentsPerBucket)
			WriteArguments(dense, slot, 0u, 0u, 0u, 0u, 0u);
		return;
	}
```

1. **Lines 62–64:** keys with no instances end at once; most keys are empty.
2. **Lines 67–75:** a pass handles the buckets of one phase only, so each phase's build sees its own counts.
3. **Lines 76–79:** two atomic adds: the draw list's used length gives the range's start, and the bucket's draw count gives the slot.
4. **Lines 80–87:** no room in the list, or no slot left: the record's instances count as overflow, its offset becomes none, and the write pass skips it.

Strata does not scan. A scan would give the records their ranges in key order every time, while the atomic add gives them in the order threads arrive, so which record comes first can differ from run to run. The ranges never overlap and each holds exactly its record's count, which is all a draw needs. The scan's fixed order would cost one more pass and its barriers.

```slang src="Strata/shaders/Scene/CullBuild.comp.slang#L89-L109"
u_Offsets[key] = offset;
// Beyond the slots the draws read without a GPU-written count: written, but not drawn (the CPU's bound missed it).
if (u_Cull.DrawsBounded != 0u && slot >= u_BucketTable[ST_CULL_BUCKETS + dense])
	InterlockedAdd(u_Counters[ST_COUNTER_OVERFLOW], count);
GeometryLOD lod = u_GeometryLODs[record];
GeometryEntry entry = u_GeometryEntries[lod.Mesh];
WriteArguments(dense, slot, lod.IndexCount, count, entry.FirstIndex + lod.IndexOffset, entry.FirstVertex + lod.BaseVertex, offset);
if (dense < u_Cull.ViewBucketCount)
{
	InterlockedAdd(u_Counters[ST_COUNTER_VIEW_DRAWS], 1u);
	// Triangles, 64 bits: the product's high word, plus the carry of the low word's addition.
	uint high;
	uint low;
	UnsignedMultiplyExtended(count, lod.IndexCount / 3u, high, low);
	uint st_Atomic3; InterlockedAdd(u_Counters[ST_COUNTER_TRIANGLES_LOW], low, st_Atomic3);
	uint previous = st_Atomic3;
	if (previous + low < previous)
		high++;
	if (high != 0u)
		InterlockedAdd(u_Counters[ST_COUNTER_TRIANGLES_HIGH], high);
}
```

1. **Lines 91–92:** without a GPU-written draw count, a slot beyond the number the CPU foresaw is written but not drawn, and it counts as overflow.
2. **Line 95:** the indirect arguments of the record: index count, instance count, first index, base vertex and, as first instance, the start of the range, which the vertex shader reads the draw list from.
3. **Lines 100–108:** a count of triangles in 64 bits, because 400,000,000 instances of a 12-triangle cube make 4,800,000,000 triangles, more than 32 bits hold. The product's high word is added, and a carry from the low word adds one more.

:::example[One crate from count to draw]
Take three visible crates of one cube level. Say the level is LOD record 7, its bucket has the dense index 0, and the draw list is empty so far. The numbers 7 and 0 are invented for the example.

The counting pass adds one to key 7 for each crate, so the key reads 3. In the build step, the thread of key 7 adds 3 to the draw list's used length and gets the start 0. It adds 1 to bucket 0's draw count and gets slot 0, and it writes the arguments of slot 0: 36 indices, 3 instances, the cube's first index and vertex, and first instance 0.

In the write pass, the three crates each subtract one from key 7 and receive 2, 1 and 0, in some order. They store their instance numbers at entries 2, 1 and 0 of the draw list. The indirect call for bucket 0 reads slot 0, and the vertex shader reads entry 0 plus the instance's number from the draw list, which names the crate to draw.
:::

### The sequence of a frame, and its barriers

The C++ that runs the passes is short. Search it for the order: counting, build, feedback, write, and a barrier wherever a pass reads what an earlier one wrote. The build and the feedback both read the counts and not each other, so they share one barrier.

```cpp src="Strata/src/Strata/Renderer/SceneRendererGPUDriven.cpp#L1001-L1047"
	nvrhi::ComputeState state;
	state.bindings = { m_CullBindingSet };
	// The cascades and the first batch of local shadow views are culled together; later batches after the first's draws
	// (DrawGPULocalShadows).
	const uint32_t localViews = static_cast<uint32_t>(m_LocalShadowViews.size());
	const uint32_t localMode = GetLocalShadowCullMode(0, std::min(localViews, RenderData::c_CullMaxLocalShadowViews));
	const auto cullPasses = [&](uint32_t mode)
	{
		state.pipeline = m_CullViewPipeline;
		commandList->setComputeState(state);
		commandList->setPushConstants(&mode, sizeof(mode));
		Dispatch(commandList, constants.ProxyCount);
		if (!shadows)
			return;
		state.pipeline = GetCullShadowPipeline();
		commandList->setComputeState(state);
		const uint32_t shadowMode = mode | localMode;
		commandList->setPushConstants(&shadowMode, sizeof(shadowMode));
		Dispatch(commandList, constants.ProxyCount);
	};
	const auto barrier = [&]() { CullBarrier(commandList); };

	cullPasses(c_CullModeCount);
	barrier();
	state.pipeline = m_CullBuildPipeline;
	commandList->setComputeState(state);
	const uint32_t mode = c_CullModeCount;
	commandList->setPushConstants(&mode, sizeof(mode));
	Dispatch(commandList, static_cast<uint64_t>(constants.BucketCount) * constants.LODCapacity);
	if (localViews > 0)
	{
		commandList->setPushConstants(&c_CullModeLocal, sizeof(c_CullModeLocal));
		Dispatch(commandList, static_cast<uint64_t>(constants.BucketCount) * constants.LODCapacity);
	}
	// The feedback is packed once every counting pass ran: after the last batch of local shadow views.
	if (feedback && localViews <= RenderData::c_CullMaxLocalShadowViews)
	{
		// The touched slots' feedback, packed (it reads the counting passes' writes, as the build does).
		state.pipeline = m_CullFeedbackPipeline;
		commandList->setComputeState(state);
		commandList->setPushConstants(&mode, sizeof(mode));
		Dispatch(commandList, 1 + static_cast<uint64_t>(constants.MeshSlotCount) + constants.MaterialSlotCount);
	}
	barrier();
	cullPasses(c_CullModeWrite);
	barrier();
}
```

1. **Lines 1007–1020:** `cullPasses` dispatches the view's shader and, with shadows, the cascades' shader over the same proxies, in the mode it is given.
2. **Lines 1023–1024:** the counting passes, then a barrier.
3. **Lines 1025–1033:** the build, once for the view and the cascades, and once more for the local shadow views.
4. **Lines 1036–1043:** feedback packing, after every counting pass has run.
5. **Lines 1045–1046:** the write passes, and a last barrier before the draws.

Why the barriers are explicit: all passes bind one set, and NVRHI places barriers only when the set changes.

```cpp src="Strata/src/Strata/Renderer/SceneRendererGPUDriven.cpp#L1049-L1058"
void SceneRenderer::CullBarrier(nvrhi::ICommandList* commandList)
{
	// The passes go through one binding set, and NVRHI places barriers only when binding sets change: each pass must see
	// the previous one's writes.
	for (nvrhi::IBuffer* buffer : { m_CullCountBuffer.Get(), m_CullOffsetBuffer.Get(), m_CullArgumentBuffer.Get(), m_CullBucketCountBuffer.Get(),
		m_CullCounterBuffer.Get(), m_GPUDrawListBuffer.Get(), m_FeedbackMeshBuffer.Get(), m_FeedbackMaterialBuffer.Get(), m_FeedbackListBuffer.Get(),
		m_FeedbackRecordBuffer.Get(), m_CasterDepthBuffer.Get(), m_VisibilityBuffer.Get(), m_LODFadeBuffer.Get() })
		commandList->setBufferState(buffer, nvrhi::ResourceStates::UnorderedAccess);
	commandList->commitBarriers();
}
```

1. **Lines 1053–1055:** every buffer a pass may write is listed.
2. **Lines 1056–1057:** each goes to the unordered-access state again, and `commitBarriers` places the barrier. Without it, the build could read half-finished counts.

### The bucket numbers in code

The map section drew the layout; the :term[header]{id=header} builds it with three small functions, and the table of dense indices is made each frame from what the frame can have.

```cpp src="Strata/src/Strata/Renderer/GPUSceneData.h#L113-L151"
// Draw buckets: one per pipeline state and vertex arena. A view bucket's index: mirrored (bit 0), double-sided (bit 1),
// geometry (bits 2-3, c_CullGeometry*), the occlusion culling's second phase (bit 4: what the first phase did not draw,
// found visible against the depth pyramid); shadow buckets follow the view's, c_CullShadowBucketsPerCascade per
// cascade, alpha-masked in bit 4 and the cascade's second phase in bit 5; then the local shadow views' (point and spot
// lights), c_CullLocalShadowBucketsPerView per view of a batch of at most c_CullMaxLocalShadowViews, alpha-masked in bit
// 4. Buckets the frame cannot have get no storage: the bucket table maps the present ones to dense indices
// (c_CullNoBucket for the others).
constexpr uint32_t c_CullGeometryStatic = 0;       // Static arena, unskinned pipelines
constexpr uint32_t c_CullGeometrySkinnedArena = 1; // Skinned arena drawn in its bind pose: unskinned pipelines
constexpr uint32_t c_CullGeometrySkinned = 2;      // Skinned arena, posed: the skinned pipelines
constexpr uint32_t c_CullViewBuckets = 32;
constexpr uint32_t c_CullShadowBucketsPerCascade = 64;
constexpr uint32_t c_CullMaxCascades = 5; // RenderData::c_MaxCascades
constexpr uint32_t c_CullLocalShadowBucketsPerView = 32;
constexpr uint32_t c_CullMaxLocalShadowViews = 12; // A batch of views: frames that draw more cull them a batch at a time
constexpr uint32_t c_CullFirstLocalShadowBucket = c_CullViewBuckets + c_CullMaxCascades * c_CullShadowBucketsPerCascade;
constexpr uint32_t c_CullBuckets = c_CullFirstLocalShadowBucket + c_CullMaxLocalShadowViews * c_CullLocalShadowBucketsPerView;
constexpr uint32_t c_CullNoBucket = ~0u;

constexpr uint32_t MakeViewBucket(bool mirrored, bool doubleSided, uint32_t geometry, bool secondPhase = false)
{
	return (mirrored ? 1u : 0u) | (doubleSided ? 2u : 0u) | (geometry << 2) | (secondPhase ? 16u : 0u);
}

constexpr uint32_t c_CullShadowAlphaMask = 16;   // A shadow bucket's alpha-masked bit
constexpr uint32_t c_CullShadowSecondPhase = 32; // A shadow bucket's second-phase bit

constexpr uint32_t MakeShadowBucket(uint32_t cascade, bool mirrored, bool doubleSided, uint32_t geometry, bool alphaMask, bool secondPhase = false)
{
	return c_CullViewBuckets + cascade * c_CullShadowBucketsPerCascade + MakeViewBucket(mirrored, doubleSided, geometry)
		+ (alphaMask ? c_CullShadowAlphaMask : 0u) + (secondPhase ? c_CullShadowSecondPhase : 0u);
}

// The bucket of a local shadow view's draws: its place in its batch (`view`), then as a view bucket, alpha-masked in bit 4.
constexpr uint32_t MakeLocalShadowBucket(uint32_t view, bool mirrored, bool doubleSided, uint32_t geometry, bool alphaMask)
{
	return c_CullFirstLocalShadowBucket + view * c_CullLocalShadowBucketsPerView + MakeViewBucket(mirrored, doubleSided, geometry)
		+ (alphaMask ? c_CullShadowAlphaMask : 0u);
}
```

1. **Lines 123–130:** the constants are the ranges of the diagram: 32, 5 × 64 and 12 × 32 buckets.
2. **Lines 132–135:** a view bucket is bits, so the shader builds it by joining them, as `EmitViewInstances` does.
3. **Lines 140–144:** a cascade's buckets follow the view's, 64 per cascade.
4. **Lines 147–151:** the local views come last, 32 per view of a batch of at most twelve; a frame with more views goes through the shader one batch at a time.

`PrepareGPUCulling` fills the dense table. A bucket gets a number only if the frame can have it: its arena has records, the scene has mirrored proxies, or its materials include double-sided or alpha-masked ones.

### Choosing how to issue the draws

After the write pass, each bucket's draws sit in the argument buffer, and a count says how many. How the CPU issues them depends on the device. The three modes are `Count`, which calls **`drawIndexedIndirectCount`** (an indirect multi-draw whose count the GPU also writes into a buffer), `NoCount`, which issues the slots without a count, and `PerDraw`, one call per slot.

```cpp src="Strata/src/Strata/Renderer/SceneRendererGPUDriven.cpp#L178-L195"
SceneRenderer::GPUIndirectPath SceneRenderer::GetGPUIndirectPath(uint32_t argumentsPerBucket) const
{
	const GraphicsDeviceInfo& info = Renderer::GetGraphicsDevice().GetInfo();
	switch (m_Specification.IndirectMode)
	{
		case IndirectDrawMode::PerDraw:
			return GPUIndirectPath::PerDraw;
		case IndirectDrawMode::NoCount:
			return info.SupportsMultiDrawIndirect ? GPUIndirectPath::NoCount : GPUIndirectPath::PerDraw;
		case IndirectDrawMode::Auto:
			break;
	}
	// A bucket's GPU-written count is at most its slots (its draws are records of its arena), and the count must stay
	// within the limit: buckets of more slots are drawn without it, by calls of at most the limit.
	if (info.SupportsDrawIndirectCount && argumentsPerBucket <= GetMaxDrawsPerIndirectCall())
		return GPUIndirectPath::Count;
	return info.SupportsMultiDrawIndirect ? GPUIndirectPath::NoCount : GPUIndirectPath::PerDraw;
}
```

1. **Lines 183–186:** a specification can force `PerDraw` or `NoCount`; `NoCount` still needs `multiDrawIndirect`.
2. **Line 192:** `Count` needs the device feature and a bucket whose slots fit the device's `maxDrawIndirectCount` limit.
3. **Line 194:** otherwise `NoCount`, or `PerDraw` without multi-draw support.

The tree shows the whole choice, from the mode of the specification to the call.

```mermaid caption="The device and the specification choose one of three ways to issue a bucket's draws." alt="A decision tree. Without the automatic mode, ready shaders or the first-instance feature the renderer uses the CPU path. Otherwise a per-draw mode gives one call per slot. A no-count mode gives multi-draw calls if the device has the multi-draw feature. The automatic mode gives the counted call when the device writes counts and the slots fit the limit."
flowchart TD
  A{"GPUDriven Auto, shaders ready, drawIndirectFirstInstance?"} -- no --> CPU["CPU path"]
  A -- yes --> M{"IndirectMode"}
  M -- PerDraw --> PD["PerDraw: one call per slot"]
  M -- NoCount --> NM{"multiDrawIndirect?"}
  M -- Auto --> AC{"drawIndirectCount, slots within maxDrawIndirectCount?"}
  AC -- yes --> CT["Count: drawIndexedIndirectCount"]
  AC -- no --> NM
  NM -- yes --> NC["NoCount: calls of at most maxDrawIndirectCount"]
  NM -- no --> PD
```

:term[MoltenVK]{id=moltenvk}, the layer that runs :term[Vulkan]{id=vulkan} on Apple's Metal, does not offer GPU-written counts, as the 0.4.0 release notes say. Every Apple computer therefore draws without them, and because Metal has no multi-draw, MoltenVK turns each indirect draw into a draw of its own.

```cpp src="Strata/src/Strata/Renderer/SceneRendererGPUDriven.cpp#L1227-L1258"
void SceneRenderer::DrawGPUBucket(nvrhi::ICommandList* commandList, uint32_t dense, uint32_t slots)
{
	const uint32_t perBucket = m_CullConstants.ArgumentsPerBucket;
	slots = std::min(slots, perBucket);
	const uint32_t offset = dense * perBucket * static_cast<uint32_t>(sizeof(nvrhi::DrawIndexedIndirectArguments));
	switch (GetGPUIndirectPath())
	{
		case GPUIndirectPath::Count:
			// The GPU's count is exact: every slot of the bucket's storage may be drawn, whatever the CPU foresaw.
			commandList->drawIndexedIndirectCount(offset, dense * static_cast<uint32_t>(sizeof(uint32_t)), perBucket);
			m_Stats.DrawCommands++;
			break;
		case GPUIndirectPath::NoCount:
		{
			// Calls of at most the device's (or the specification's) draws each.
			const uint32_t maxDraws = GetMaxDrawsPerIndirectCall();
			for (uint32_t first = 0; first < slots;)
			{
				const uint32_t draws = std::min(maxDraws, slots - first);
				commandList->drawIndexedIndirect(offset + first * static_cast<uint32_t>(sizeof(nvrhi::DrawIndexedIndirectArguments)), draws);
				m_Stats.DrawCommands++;
				first += draws;
			}
			break;
		}
		case GPUIndirectPath::PerDraw:
			for (uint32_t slot = 0; slot < slots; slot++)
				commandList->drawIndexedIndirect(offset + slot * static_cast<uint32_t>(sizeof(nvrhi::DrawIndexedIndirectArguments)), 1);
			m_Stats.DrawCommands += slots;
			break;
	}
}
```

1. **Lines 1234–1238:** with a GPU-written count, one call covers all of the bucket's storage, and the GPU's number says how many slots draw. The count is exact.
2. **Lines 1239–1251:** without one, the calls cover only `slots` entries, in pieces of at most the device's limit.
3. **Lines 1252–1256:** `PerDraw` issues one call per slot, so it counts one draw command for each.

Without a GPU-written count, the CPU must guess how many slots a bucket has, and a wrong guess costs pictures. Slots the guess adds without need draw empty arguments, which is harmless; instances beyond the guess are not drawn. The guess comes from the CPU's own marks: the LOD records of the meshes it found in view, for the view's buckets, and the casters' records for each cascade. On feedback frames the marks are the feedback's, which are older, so `PrepareGPUCulling` adds a quarter of them and 16 more, up to the records of the arena. With 40 records in view that gives 40 + 10 + 16 = 66 slots.

Draws beyond the bound count as overflow and are not drawn in that frame. The CPU then walks the view once, as the feedback sections show. With a GPU-written count, none of this applies, because the GPU's number is exact.

### Counters, empty scenes and what stays out

The frame also fills a `CullCounters` :term[struct]{id=struct} of 128 bytes: visible proxies, draws, overflow, triangles, instances per level. A `BufferReadback` copies it to a buffer the CPU can read, and the answer arrives two to three frames later, as [readback without stalling](../gpu/readback-timing.md) explains. The renderer keeps six such records, and the statistics show the newest completed one.

A render scene that never had a proxy skips the passes and records only the clears of the counters. Strata does not use mesh shaders or `meshlet` clusters: culling is per proxy and per instance, and the draws go through the classic vertex pipeline. A search for `meshlet`, mesh shader or task shader in the engine's source and shaders at the pin finds nothing.

### Feedback loops from the GPU to the CPU

The GPU now knows, at no extra cost, what is in view and how large each thing looks. The CPU must decide which meshes and materials to load, and it used to walk every proxy to learn that. A **feedback loop** from the GPU to the CPU closes the gap: the GPU writes what it saw into a buffer, and the CPU reads the buffer later.

The price is latency. The GPU runs frames behind the CPU, and a read that waits for it stalls the whole frame. So the read waits until the copy is ready, two or three frames after the frame that wrote it. Any system that loads data from what the GPU saw has this delay. It loads what the old frame saw, and it accepts a few frames of low detail when the camera turns fast.

**Visibility feedback** is Strata's form of it: the GPU's record of which mesh and material slots a frame used, and how, read back to drive asset requests. The counting pass writes it, and the sections below follow it from the shader to the streamer.

### The GPU marks what it touched

For every proxy it tests, the counting pass records the mesh slot and the material slots with four use bits. The bits say that the proxy was seen in the view or seen large (above the high-priority fraction of the viewport, 5 % by default). They also say that it lies within the :term[prefetch distance]{id=prefetch-distance} (100 units by default) or casts a shadow into a cascade or a shadow view of a point or spot light.

A proxy whose sphere spans 8 % of the viewport height gets the high bit, and one that spans 3 % does not: on a viewport of 1080 lines the line lies at 54 pixels. The pass also records the largest projected size in pixels and, for textured materials, the pixels one texture-coordinate unit spans. Thousands of proxies share one mesh, so one atomic per proxy would queue them all on one address.

```slang src="Strata/shaders/Scene/Cull.comp.slang#L84-L102"
// Feedback for a mesh or material slot: its use bits, its largest sizes, and its place in the touched lists the first time
// a frame touches it. Read before the atomics: thousands of proxies of one mesh mostly find their use recorded already.
void MarkMeshFeedback(uint slot, uint use, float pixels)
{
	uint base = slot * 2u;
	if ((u_MeshFeedback[base + 1u] & use) != use)
	{
		uint st_Atomic2; InterlockedOr(u_MeshFeedback[base + 1u], use, st_Atomic2);
		uint previous = st_Atomic2;
		if (previous == 0u)
		{
			uint st_Atomic3; InterlockedAdd(u_FeedbackLists[0], 1u, st_Atomic3);
			u_FeedbackLists[ST_FEEDBACK_LIST_HEADER + st_Atomic3] = slot;
		}
	}
	uint bits = asuint(pixels);
	if (pixels > 0.0 && u_MeshFeedback[base] < bits)
		InterlockedMax(u_MeshFeedback[base], bits);
}
```

1. **Line 89:** the read comes first: if the use bits are already recorded, the thread does nothing more. Most threads stop here.
2. **Lines 91–96:** the first touch of a slot appends it to a list, so the packing pass visits only touched slots.
3. **Lines 99–101:** the size keeps the largest value; positive floats order like :term[integers]{id=integer}, so `InterlockedMax` works on their bits.

`CullFeedback.comp` then packs the touched slots into records of 16 bytes (`FeedbackRecord`: slot, use bits, pixels, texture-coordinate pixels), the touched ones first. The sizes come from `Include/TextureStreaming.slang`, a port of the texture streamer's `GetWorldPixels` and `GetUVPixels`, which a comment asks to keep in sync with the CPU's version. A copy of the records goes into a readback buffer after the frame.

### The CPU applies the newest feedback

The CPU reads the newest ready feedback and turns it into the marks that its own walk would have made.

```cpp src="Strata/src/Strata/Renderer/SceneRendererExtraction.cpp#L344-L386"
void SceneRenderer::ApplyFeedback(RenderScene& renderScene, const SceneCamera& camera, const Frustum& frustum)
{
	ST_PROFILE_FUNCTION();
	ST_PROFILE_STAGE("Render.Extract");
	// The slots the feedback's frame touched, as it used them (its culling ran with the mesh and material tables the scene's
	// GPU copy holds now: UsesFeedback).
	const uint32_t meshSlots = renderScene.GetMeshSlotCapacity();
	const uint32_t materialSlots = renderScene.GetMaterialSlotCapacity();
	for (const RenderData::FeedbackRecord& record : m_Feedback.Meshes)
	{
		if (record.Slot >= meshSlots || !renderScene.GetMeshHandle(record.Slot).IsValid() || (record.Use & c_UseMask) == 0)
			continue;
		MarkMesh(record.Slot, record.Use & c_UseMask);
	}
	for (const RenderData::FeedbackRecord& record : m_Feedback.Materials)
	{
		if (record.Slot >= materialSlots || !renderScene.GetMaterialHandle(record.Slot).IsValid() || (record.Use & c_UseMask) == 0)
			continue;
		MarkMaterial(record.Slot, record.Use & c_UseMask);
		// Sizes as GatherDraws records them for drawn instances (the GPU's are of its drawn instances).
		if (std::isfinite(record.Pixels) && record.Pixels > 0.0f)
			m_MaterialPixelSizes[record.Slot] = std::max(m_MaterialPixelSizes[record.Slot], record.Pixels);
		if (record.UVPixels > 0.0f && !std::isnan(record.UVPixels))
			m_MaterialUVPixels[record.Slot] = std::max(m_MaterialUVPixels[record.Slot], record.UVPixels);
	}

	// What the CPU still draws or tells in the view: the users of transparent materials (drawn sorted), and skinned
	// proxies (their animators learn that they are seen). The spatial index's test, proxy by proxy.
	m_UserScratch.clear();
	renderScene.CollectMaterialUsers(m_SceneGPU->GetTransparentMaterialSlots(), m_UserScratch);
	for (uint32_t index = 0; index < renderScene.GetSkinProxyCount(); index++)
		m_UserScratch.push_back(renderScene.GetSkinProxy(index));
	std::sort(m_UserScratch.begin(), m_UserScratch.end());
	m_UserScratch.erase(std::unique(m_UserScratch.begin(), m_UserScratch.end()), m_UserScratch.end());
	m_VisibleProxies.clear();
	for (const uint32_t proxy : m_UserScratch)
	{
		if ((renderScene.GetProxyFlags(proxy) & RenderProxyFlags::Indexed) != 0 && frustum.IsAABBVisible(renderScene.GetWorldBounds(proxy)))
			m_VisibleProxies.push_back(proxy);
	}
	MarkVisibleProxies(renderScene, camera);
	MarkMeshesWithoutBounds(renderScene);
}
```

1. **Lines 352–357:** each mesh record becomes a mark, if its slot still holds a valid mesh.
2. **Lines 358–367:** each material record becomes a mark and raises the slot's pixel and texture-coordinate sizes, as `GatherDraws` does for drawn instances.
3. **Lines 370–383:** the CPU still walks the users of transparent materials and the skinned proxies, which the GPU does not draw or cannot judge.
4. **Line 385:** meshes of unknown bounds get marks too, because the GPU cannot place them.

Feedback is not always usable. `UsesFeedback` lists every reason the CPU walks the view instead.

```cpp src="Strata/src/Strata/Renderer/SceneRendererGPUDriven.cpp#L1676-L1685"
bool SceneRenderer::UsesFeedback(const RenderScene& renderScene) const
{
	if (!m_GPUDrivenFrame || !m_Specification.VisibilityFeedback || !m_Feedback.Valid || m_Feedback.RenderSceneId != renderScene.GetId())
		return false;
	const uint64_t frame = m_RenderCount + 1;
	if (m_Feedback.Render < m_CutRender || frame - m_Feedback.Render > c_MaxFeedbackAge || m_Feedback.TablesVersion != m_SceneGPU->GetTablesVersion())
		return false;
	// Draws beyond the slots a feedback frame foresaw were left out: the CPU's marks bound them exactly once.
	return !(m_GPUStats.HasCounters && m_GPUStats.Overflow > 0 && m_GPUStats.CountersRender > m_MarksRender);
}
```

1. **Line 1678:** no feedback without the GPU path, the specification's switch (on by default) or a valid read of the render scene's own feedback; the first frames fail here.
2. **Lines 1680–1682:** the feedback must be newer than the last camera cut, at most 8 frames old, and made with the tables the scene has now.
3. **Line 1684:** after an overflow, the CPU walks once, so its exact marks bound the slots again.

Four cases send the CPU back to its walk: the first frames, a camera cut, a table that changed since the feedback's frame (a mesh finished loading), and feedback older than 8 frames. A fifth, an overflow, sends it back once. The test `Without a GPU-written draw count, draws beyond the slots the feedback foresaw run the CPU's walk once` builds the last case: 60 meshes beside the view, one mesh in it, then a camera turn. The first frame after the turn overflows, the next walks the view and draws all, and the third uses feedback again.

The feedback reaches the texture streamer by no road of its own. `ApplyFeedback` writes the sizes into the material slots, `GatherDraws` publishes the slots as the frame's visible textures, and `ReportTextureUse` hands them to `ReportView`, as it does on the CPU path. [Mip streaming](mip-streaming.md) teaches how the streamer uses them.

### How late a request comes

```mermaid caption="A frame's feedback reaches the CPU two or three frames later, and the loads finish later still." alt="Four steps from left to right. The GPU of frame N marks slots and packs feedback. In frame N plus two or three the CPU reads it and requests assets. A few frames later the loads finish and the tables change. Then the CPU walks the view once until feedback from a later frame matches the tables."
flowchart LR
  subgraph N["frame N"]
    N1["counting pass marks slots"] --> N2["records packed and copied"]
  end
  subgraph R["frame N+2 or N+3"]
    R1["newest ready feedback read"] --> R2["ApplyFeedback marks requests"]
  end
  subgraph L["a few frames later"]
    L1["loads finish"] --> L2["tables version grows"]
  end
  subgraph W["next frames"]
    W1["CPU walks the view"] --> W2["feedback of a later frame matches"]
  end
  N --> R --> L --> W
```

At 60 frames per second, two to three frames are 33 ms to 50 ms before a request exists, and the load comes after it. So the requests of the CPU's walk and of the feedback differ in timing but not in content, and a test of requests must wait for feedback or disable it. The test `Feedback is a few frames late: a material no longer drawn stops being requested once the GPU's culling saw it go` shows the delay from the other side: a cube goes away, and its material is requested for one more frame.

### The measured cost

The perf tests render grids of cubes with a renderer that leaves `GPUDriven` at `Auto`, and record the CPU's :term[frame time]{id=frame-time} and the GPU's busy time.

| Cubes | CPU frame (ms) | GPU busy time (ms) |
| --- | --- | --- |
| 100,000 | 0.173 | 1.436 |
| 1,000,000 | 0.285 | 12.85 |

The table holds the values measured on the reference machine. Ten times the cubes cost the CPU about 1.6 times the time (0.285 against 0.173), and the GPU about 9 times (12.85 against 1.436). That is the point of the design: the CPU's work stops following the number of proxies, and the work lands on the GPU, which has thousands of threads for it. The method of such measurements is in [the performance lab](../engineering/perf-lab.md), and the full table in [performance](../reference/performance.md).

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| CPU culling with instanced draws | Strata's own fallback path | Works on every device; simple | A cost that grows with the number of proxies |
| One global atomic append | The simplest compute culling | One pass, and no second run of the decisions | Ranges per record: draws need instances grouped, and the list's order follows timing |
| GPU culling, the CPU builds the draws from a readback | Systems without indirect draws | Runs where indirect draws are missing | Frames of latency, or a stall that waits for the GPU |
| A scan for the ranges | Textbook stream packing | Ranges in a fixed order every run | One more pass and its barriers, for an order no draw reads |
| Mesh shaders and small clusters of triangles | Hardware with the Vulkan mesh shader extension | Culling per cluster, finer than per proxy | A new shader stage, new hardware requirements and a rewrite of the vertex path |

## How it is tested

The suite `GPU.SceneRenderer.GPUDriven` holds the main test. Its helper `CompareScenes` builds a list of scenes: meshes, masks, mirrors, skins, shadows, transparency, glass, levels of detail and local shadows. It draws each with the CPU's path and with the GPU's, and compares the pictures and the counts of drawn instances. It also checks, per scene, that the second frame takes its requests from feedback and that a turning camera writes the same motion vectors.

The suite `GPU.SceneRenderer.GPUDrivenFallback` makes one of the path's shaders missing at a time. The renderer must draw through the CPU path and keep none of the path's resources. The suite `GPU.SceneRenderer.IndirectFallback` runs `CompareScenes` in `NoCount` and `PerDraw` modes, with local shadow views a batch at a time and buckets split over several calls. The suite `GPU.SceneRenderer.Feedback` covers requests and the walk after an overflow.

All of these need a GPU and carry the `gpu` label. The hosted runners of continuous integration (CI) have none, so they omit the label. The 0.4.0 release notes add that the wave was made on an Apple computer, and that paths of NVIDIA, AMD and Intel drivers, such as GPU-written counts, had not yet run anywhere.

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=GPU.SceneRenderer.GPUDriven
```

The command runs the first suite on a machine with a GPU, and the other suites run the same way. If a comparison fails, the output names the scene, because `CompareScenes` records it.

## Changing it safely

Extension points are few and clear. A new culling input goes into `CullConstants` (filled in `PrepareGPUCulling`) and into the shader's matching struct. A new per-instance value goes into a parallel buffer, as the level-of-detail fade state does, never into `InstanceData`, which stays at 64 bytes. Changes to the render scene's instances are logged (`RecordInstanceChanges`, `RecordProxyChange`), so its GPU copy follows.

The rules that apply, with their reasons:

- Change the CPU's rule and the GPU's together, or the two paths disagree.
- Shading must not depend on draw order, because the GPU's order is timing.
- Clear what the frame reads in the empty-scene branch too, or it reads old data.
- Keep a barrier between culling dispatches.
- Count first and write second with the same decisions: a decision that differs between passes writes outside a range.

Before merging, run `GPU.SceneRenderer.GPUDriven`, the fallback suites and `GPU.SceneRenderer.Feedback`, and the exact-pixel suites of any pass you touched. A rule change has five steps:

1. Change the CPU function.
2. Change the shader function.
3. Extend a scene of `CompareScenes` so that it separates the old rule from the new one.
4. Run the suites on a device with GPU-written counts and on one without.
5. Update the engine guide's text for the rule.

## Summary

- A proxy goes through `CullProxy`, then `Emit` counts it, `CullBuild.comp` gives its record a range and a slot, the write pass places it, and `DrawGPUBucket` issues the draw that reads it.
- Strata counts first and writes second because draws need each record's instances in one range, and a single atomic append gives no ranges.
- A change to a culling rule must change the shader and its CPU twin, and the tests must compare them.
- The device and the specification choose the counted call, `NoCount` or `PerDraw`; without a GPU-written count, the bound on a bucket's slots comes from the CPU's marks.
- Feedback reaches the CPU two to three frames late, and the CPU walks the view in the first frames, after a cut, after table changes, after 8 frames and once after an overflow.

## Check yourself

1. Three records have the counts 4, 0 and 6. Give their starting offsets and the draw list's length.

   :::answer{tests="count-first"}
   The starts are 0, 4 and 4, and the list holds 10 entries. The second record owns no entries and no draw, because `CullBuild.comp` skips keys with a count of 0.
   :::

2. Why does Strata not append every surviving instance with one atomic counter?
   - A. Atomics are slow on every GPU.
   - B. The instances of one record would not stand side by side, and one indirect draw reads one range.
   - C. The CPU cannot read the counter.

   :::answer{tests="count-first"}
   B. Atomics work and are fast enough (A is wrong), and the CPU never needs the counter (C is wrong). Draws need a range per record, which only counting first can size.
   :::

3. A device lacks `drawIndirectCount` but has `multiDrawIndirect` and a limit of 64. A bucket has 100 slots, the CPU's bound is 40, and the mode is `Auto`. Which path runs, and how many calls?

   :::answer{tests="indirect-path"}
   `NoCount`, because `Count` needs the device feature. The calls cover the bound of 40 slots, not 100, and 40 is within the limit of 64, so one call is enough.
   :::

4. A developer adds a maximum draw distance to the CPU's `GatherDraws` only. What happens, and which test fails?

   :::answer{tests="twin-rules"}
   The GPU path still draws far proxies that the CPU's path omits, so the two pictures differ. `CompareScenes`, run by `GPU.SceneRenderer.GPUDriven`, fails on a scene that has far proxies.
   :::

5. The camera cuts to a new place in frame 100, and the newest ready feedback is from frame 98. Which path selects frame 100's draws, and when do requests follow feedback again?

   :::answer{tests="feedback-late"}
   The CPU walks the view, because `UsesFeedback` rejects feedback older than the cut. A frame after the cut writes new feedback, and once the CPU reads it, two to three frames later, requests follow it again.
   :::

6. Put these steps in the order that one proxy meets them: the write pass, the counting pass, the indirect call, `CullBuild.comp`.

   :::answer{tests="trace-proxy"}
   The counting pass, `CullBuild.comp`, the write pass, the indirect call. The counts must exist before the build gives ranges, and the ranges must exist before the write pass fills them.
   :::

## Exercises

1. **Basic.** Find where one proxy of a `CompareScenes` scene is counted, gets its place in a range, and is drawn. Use a search of the :term[repository]{id=repository} or the capture of a GPU debugger, and name each pass, buffer and function.

   :::answer[Worked solution]{tests="trace-proxy"}
   Search for `CullProxy` in `Strata/shaders/Scene/Cull.comp.slang`. The counting pass runs it, `EmitViewInstances` calls `Emit`, and `Emit` adds one to `u_Counts` at the key (dense bucket times `LODCapacity` plus record). `CullBuild.comp` reads that count in `st_Main`, takes a range of the draw list from `u_Counters` and a slot from `u_BucketCounts`, and writes the arguments to `u_Arguments`, with the range's start as first instance. In the write pass, `Emit` counts the key down and stores the instance in `u_CullDrawList`. `DrawGPUBucket` in `Strata/src/Strata/Renderer/SceneRendererGPUDriven.cpp` then issues `drawIndexedIndirectCount`, `drawIndexedIndirect` or the per-slot form.
   :::

2. **Medium.** Add a maximum draw distance to the toy's two twins: the CPU's counting loop and the GPU's `CullProxy`. Show that both agree for three limits.

   :::answer[Worked solution]{tests="twin-rules" solution="sketches/draw-gpu-driven-distance.cpp"}
   The sketch writes the rule twice, as the engine does, and compares the counts for each limit.

   ```cpp sketch="draw-gpu-driven-distance.cpp"
   #include <cstdint>
   #include <cstdio>
   #include <vector>

   constexpr uint32_t c_Records = 2;

   struct Proxy
   {
   	float Distance;
   	uint32_t Record;
   };

   // The CPU's rule: a simple loop that counts what each record draws.
   std::vector<uint32_t> CountOnCPU(const std::vector<Proxy>& proxies, float maxDistance)
   {
   	std::vector<uint32_t> counts(c_Records, 0);
   	for (const Proxy& proxy : proxies)
   	{
   		if (proxy.Distance <= maxDistance)
   			counts[proxy.Record]++;
   	}
   	return counts;
   }

   // The GPU's twin: the same rule, written again where the other code cannot see it, as one thread per proxy.
   void CullProxy(std::vector<uint32_t>& counts, const Proxy& proxy, float maxDistance)
   {
   	if (proxy.Distance > maxDistance)
   		return;
   	counts[proxy.Record]++; // InterlockedAdd on the GPU
   }

   int main()
   {
   	const std::vector<Proxy> proxies = { { 5.0f, 0 }, { 40.0f, 1 }, { 120.0f, 0 }, { 80.0f, 1 }, { 100.0f, 0 } };
   	for (const float maxDistance : { 1000.0f, 100.0f, 10.0f })
   	{
   		const std::vector<uint32_t> cpu = CountOnCPU(proxies, maxDistance);
   		std::vector<uint32_t> gpu(c_Records, 0);
   		for (const Proxy& proxy : proxies)
   			CullProxy(gpu, proxy, maxDistance);
   		std::printf("max %.0f: cpu %u %u, gpu %u %u, %s\n", maxDistance, cpu[0], cpu[1], gpu[0], gpu[1],
   			cpu == gpu ? "agree" : "DIFFER");
   	}
   	return 0;
   }
   ```

   ```text output-of="draw-gpu-driven-distance.cpp"
   max 1000: cpu 3 2, gpu 3 2, agree
   max 100: cpu 2 2, gpu 2 2, agree
   max 10: cpu 1 0, gpu 1 0, agree
   ```

   1. **Line 19:** the CPU's version keeps proxies up to the limit.
   2. **Lines 28–29:** the twin rejects the same proxies, written separately.
   3. **Line 36:** three limits, from none to a short one.
   4. **Lines 42–43:** the comparison; a difference prints `DIFFER`, and an engine test would fail.

   In the engine the same rule also lives in the specification (a field), in the constants (a new `CullConstants` member), in `Cull.comp` and in `GatherDraws`. `CompareScenes` needs a scene with proxies on both sides of the limit.
   :::

3. **Medium.** In a GPU test, add a mesh to a scene and count the frames until `FeedbackRequests` requests it. Predict the number before you run the test.

   :::answer[Worked solution]{tests="feedback-late"}
   Start from `FeedbackWorld` and `FrameAndResolve` in `GPUSceneFeedbackTests.cpp`, add an entity, render frames and test `GetStats().FeedbackRequests` and the material count after each. Predict two cases. A mesh new to the scene gets a new slot, which changes the tables version, so `UsesFeedback` fails and the CPU's walk requests it in its first frame. A mesh already in a slot waits for feedback: one frame with resolved readbacks, as the helper does, two to three with real ones. Write the measured numbers down.
   :::

4. **Hard.** Add a per-instance tint to the GPU path without changing `InstanceData`. Say which buffer, which logs and which test show that both paths agree.

   :::answer[Worked solution]{tests="twin-rules"}
   Add a parallel buffer in `RenderSceneGPU`, beside its instance data; the fade state is such a buffer too, though `SceneRenderer` keeps it (`m_LODFadeBuffer`). Write it from the render scene's instance log (`RecordInstanceChanges`), and bind it in the culling set and the scene set at the next free slot. Read it in the forward shader through the instance index, which both paths provide. Extend `CompareScenes` with a scene whose instances carry tints and compare the pictures. The test fails if the buffer follows only one path or misses an instance change.
   :::

## Where it lives in Strata

- `Strata/shaders/Scene/Cull.comp.slang`, `CullBuild.comp.slang` and `CullFeedback.comp.slang`: the three shaders.
- `Strata/src/Strata/Renderer/SceneRendererGPUDriven.cpp`: `IsGPUDriven`, `GetGPUIndirectPath`, `PrepareGPUCulling`, `RunGPUCulling`, `DrawGPUBucket`, `UsesFeedback`.
- `Strata/src/Strata/Renderer/GPUSceneData.h`: the tables, `CullConstants`, `CullCounters`, the bucket layout and `FeedbackRecord`.
- `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp`: `ApplyFeedback` and the CPU's culling twins.
- `StrataTests/src/Renderer/GPUSceneRendererGPUDrivenTests.cpp` and `GPUSceneFeedbackTests.cpp`: the suites above.
- `StrataTests/Perf/Budgets.json`: the four cube measurements.

## Further reading

- Ulrich Haar and Sebastian Aaltonen, "GPU-Driven Rendering Pipelines", SIGGRAPH 2015: the pipeline this page describes, from a shipped game (intermediate).
- Graham Wihlidal, "Optimizing the Graphics Pipeline with Compute", GDC 2016: culling and packing with compute (advanced).
- Khronos, "Vulkan specification: drawing commands and VK_EXT_mesh_shader": the indirect calls and the mesh shaders Strata does not use (advanced).
