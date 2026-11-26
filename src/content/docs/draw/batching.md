---
id: draw/batching
title: "Batching and instancing"
description: "How Strata turns the visible proxies into as few draws as the pipeline states allow, sorted the same way on every run and with any number of threads."
kind: internals
size: L
tracks: [E]
needs: [draw/asset-requests, gpu/geometry-pool, gpu/binding]
time: 90
learn:
  - id: draw-list-read
    text: explain how a vertex shader finds its instance through the draw list and why the base instance matters
  - id: decode-key
    text: compute the sort key of a draw and decode a key back into its fields
  - id: predict-draws
    text: predict the opaque draws of a scene with and without batching across materials
  - id: radix-passes
    text: compute how many passes the radix sort makes for a set of keys
  - id: trace-draw
    text: trace one instance from its sort item to the call that draws it
since: 0.3.0
status: final
---

A scene holds thousands of things to draw, and the :term[graphics card]{id=gpu} is fastest when it receives few, large orders. This page is about the step that turns the list of visible proxies into those orders. The step collects one entry per drawn :term[submesh]{id=submesh} and sorts the entries by a number that describes their state. It then cuts the sorted list into runs that one draw can handle and writes the draw arguments. It gives the same result on every run, whatever the number of threads.

The step does not choose which proxies are visible. It does not build the draws that the graphics card makes for itself ([the GPU-driven path](gpu-driven.md)), choose a level of detail ([levels of detail](lod.md)) or draw the sun's shadows ([sun shadows](../light/sun-shadows-1.md)).

## The problem and how engines solve it

Every draw call costs the :term[central processing unit]{id=processor} (CPU) time to record and the graphics processing unit (GPU) time to start, and a call that changes pipeline state costs more. An engine therefore wants few draws, in an order that changes state rarely. Engines get there by drawing many copies of one mesh in one call (instancing), by sorting draws on their state, and by moving the draw arguments into a buffer. [From entities to draws](entities-to-draws.md) shows where this step sits in the frame; the sections below build each idea from one scene of 1,000 cubes with 1,000 different colours.

## The map

The step runs on the :term[main thread]{id=main-thread}, with the job system doing its heaviest work. Extraction cuts the visible proxies into chunks of 2,048 and gives each chunk to a worker. The main thread merges the chunks' outputs in chunk order, sorts, builds batches, and uploads what changed. Recording the frame's commands then draws the batches.

```mermaid caption="The path of a draw from a visible proxy to a draw call: parallel gathering, a merge in chunk order, a sort, batches, an upload of what changed, and one indirect call for each bucket." alt="A chain of boxes from visible proxies through gathering in chunks, merging, sorting, building batches and uploading to drawing buckets."
flowchart LR
	A[Visible proxies] --> B["GatherDraws: chunks of 2,048 on workers"]
	B --> C["Merge in chunk order"]
	C --> D["RadixSort by SceneDrawKey"]
	D --> E["BuildBatches: batches and draw list"]
	E --> F["Upload changed ranges, BuildDrawArguments"]
	F --> G["DrawBuckets: one indirect call each"]
```

Four files hold the work. `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp` has the gathering and `BuildBatches`. `Strata/src/Strata/Renderer/SceneDrawKey.h` packs the key. `Strata/src/Strata/Core/RadixSort.cpp` sorts. `Strata/src/Strata/Renderer/SceneRenderer.cpp` builds the draw arguments and records the draws.

## Instances and the draw list

Take the 1,000 cubes. They share one mesh, so the graphics card needs the mesh once and a list of 1,000 places to draw it. A **batch** is a run of draws that one draw call handles: the same mesh, submesh, level of detail and pipeline state, with a first instance and an instance count. A batch of 1,000 cubes is one call instead of 1,000.

The :term[render scene]{id=render-scene} keeps one record per drawn submesh, an instance, in a :term[structured buffer]{id=structured-buffer} that persists between frames. Each record is 64 :term[bytes]{id=byte}: a 3 by 4 world matrix of 48 bytes, the material slot, the entity identifier, flags, and the first joint of a skin palette. Only records that changed are uploaded, so a still scene uploads nothing. The 1,000 cubes take 1,000 records of 64 bytes, which is 64,000 bytes. A frame does not draw instances in buffer order, because that order follows the proxies and the batches need runs.

The frame therefore builds a second array. The **draw list** is the frame's array of 32-bit entries, one per drawn instance, in batch order. A batch's instances are consecutive entries, so the batch is only a first position and a count. The 1,000 cubes need a draw list of 4,000 bytes. The vertex :term[shader]{id=shader} reads the entry for its instance, keeps its low 27 bits, and reads the instance record they name.

A **draw entry** is one value of the draw list. Its low 27 bits hold the instance's index. The 5 bits above them hold a code for the cross-fade of levels of detail, where 0 means no fade. The low 27 bits give a limit: a render scene holds at most 134,217,728 instances (the constant `c_MaxRenderInstances`). The function `MakeDrawEntry` joins the two parts: it shifts the code left by 27 bits and adds the instance.

:::example
Cube number 700 is the instance with index 700 in the instance buffer, and no cross-fade runs, so its draw entry is 700. Suppose the batch of cubes starts at position 0 of the draw list. A cube that is behind a wall is not drawn, so the list has 999 entries, and cube 700 may sit at position 699. The vertex shader that draws list position 699 reads 700, and then reads cube 700's matrix. With a fade code of 3 the same entry reads 700 + 3 × 134,217,728, which is 402,653,884.
:::

The shader never needs to know which batch it is in. It needs only its position in the draw list, which the next section explains.

## Reading the draw list in the shader

A draw call with 1,000 instances makes the graphics card run the vertex shader for each instance, numbering the instances from a start value. :term[Vulkan]{id=vulkan} lets a draw pick that start value. The **first instance** is the draw argument that sets it.

The **base instance** is the number the card adds to every instance index of that draw, and it equals the first instance. A batch whose entries begin at list position 5,000 is drawn with first instance 5,000.

Shading languages offer two instance numbers. `SV_InstanceID` counts from 0 inside each draw and leaves the base instance out. The **`SV_VulkanInstanceID`** is the shader input that counts from the first instance, so it includes the base instance, and it is the value that the draw list is indexed with. Strata's mesh vertex shaders declare `int instanceIndex : SV_VulkanInstanceID` and read `u_DrawList[st_InstanceIndex]`.

Read the difference as arithmetic. A batch of 3 instances at first instance 5,000 runs the shader with `SV_VulkanInstanceID` equal to 5,000, 5,001 and 5,002, which are the batch's own entries. With `SV_InstanceID` the shader sees 0, 1 and 2, the entries of some other batch, and draws the wrong objects without any error. With the first form a draw call needs no extra input to say where its entries are: the draw's own first instance does it.

:::rule
The draw list is indexed with `SV_VulkanInstanceID`, never `SV_InstanceID` (`Docs/DeveloperGuide.md`, Shaders). The reason is the base instance: only the first form includes it, and every batch reads its entries from one shared list. The other [binding](../gpu/binding.md) rules apply as well.
:::

## Material-free instancing

Colours are the next problem. In the 1,000-cube scene each cube has its own material. Many engines put the material in the draw's state, so each material is a separate draw: 1,000 draws for 1,000 cubes, and the card does no better than before instancing.

**Material-free instancing** is batching in which the material is not part of the batch: instances of one mesh, submesh and level of detail share a draw whatever their materials. The instance record holds a material slot. The fragment shaders read `u_Materials[instance.MaterialIndex]`, one entry of a structured buffer, so a draw call needs no material change between instances. The :term[bindless textures]{id=bindless} of the materials are found by their slots in the same way.

The cost is on the shader side, not in the draw. Every shader of the scene must read its material through the instance, and a material cannot change the pipeline state. A material that needs other state, such as a transparent one, leaves this path: transparent surfaces are drawn one by one, as a later section shows. The setting `BatchAcrossMaterials` of the :term[renderer's]{id=renderer} specification turns the sharing off, for comparison and debugging, and then batches split by material as well.

The numbers decide the case. With sharing on, the 1,000 cubes draw in 1 opaque call. With it off, they draw in 1,000 opaque calls and produce the same pixels. The test `GPU.RenderScene` named "A thousand materials draw with one opaque call per pass, with the pixels of batches split by material" checks both counts and compares the images. The performance tests measure the same at ten times the size: 10,000 materials draw in :value{key="perf.PerfGPU.Renderer.Render10kMaterials.OpaqueDrawCalls.Measured"} opaque call, the measured value that `StrataTests/Perf/Budgets.json` records.

:::why
Batching splits only on pipeline state, mesh, submesh and level of detail. A draw that needs another pipeline cannot share a call, but a draw that needs another colour can, so Strata keeps the colour out of the key. The cost is that every opaque shader reads its material through the instance, and a material cannot choose its own pipeline state.
:::

## Sort keys

To cut the list into batches the engine must bring equal draws next to each other. A **sort key** is a 64-bit :term[integer]{id=integer} that packs everything that decides which draws share a batch, so that draws sort together by comparing one number. Engines pick this over a comparison of several fields because one integer compares in one step and feeds the fast sorts of the next section.

In Strata the `SceneDrawKey` packs the fields from the top bit down. This table gives the layout.

| Bits | Width | Field |
| --- | --- | --- |
| 63 to 61 | 3 | Cascade (0 for the view) |
| 60 | 1 | Alpha mask |
| 59 | 1 | Mirrored |
| 58 | 1 | Double-sided |
| 57 | 1 | Skinned |
| 56 to 37 | 20 | Mesh slot |
| 36 to 21 | 16 | Submesh |
| 20 to 16 | 5 | Level of detail |
| 15 to 0 | 16 | Material slot (0 when batching across materials) |

The order matters because a sort puts the highest bits first. The pipeline state sits in the top bits, so all draws of one pipeline are one run, and a bucket of the next sections is one stretch of the sorted list. The mesh comes next, then the submesh and the level. The material takes the lowest bits, and only when batching splits by material: a key with the material in it would otherwise put equal draws apart.

A field that changes often should sit low. Levels of detail change as the camera moves, and a material swap changes a draw's key at once. When such a field is low, a change moves an entry only within the run of its own mesh, and the rest of the sorted list keeps its place. The sorted order of whole meshes stays steady.

Take a cube with mesh slot 5, submesh 0, level 0, no flag and no cascade. Its key is $5 \cdot 2^{37}$, which is 687,194,767,360 or `0xA000000000`. A double-sided draw of submesh 2, level 1, of the same mesh, adds $2^{58}$ for the flag, $2 \cdot 2^{21}$ for the submesh and $2^{16}$ for the level. The sum is `0x040000A000410000`. To decode it, shift the key right by the field's start bit and mask the field's width: the mesh is `(key >> 37) & 0xFFFFF`, which gives 5.

The widths are limits. A mesh with a submesh past the 65,536th, or a level past the 32nd, does not draw those instances: the renderer counts them and reports how many it skipped. Material slots past 65,536 share keys, so their batches merge, which stays correct because the shader reads the material from the instance. Mesh slots stay within 20 bits because each entity holds at most one, and `Scene::c_MaxEntities` bounds entities.

## Radix sort

Sorting 100,000 keys with a comparison sort costs about $n \log_2 n$ steps, close to 1.7 million comparisons. A **radix sort (LSD)** sorts integers by their digits instead of comparing them: least significant digit first, one stable pass for each digit. Strata uses one byte as the digit, so a 64-bit key needs at most 8 passes of $n$ steps each, and the cost grows in line with $n$.

A pass counts how many keys have each byte value, turns the counts into start positions, and then moves each item to the next free position of its byte value. Take keys with low bytes 3, 1, 3, 2. The counts are one 1, one 2, two 3s, the start positions 0, 1, 2 for the values 1, 2, 3, and the items move to the order 1, 2, 3, 3. The two items with value 3 keep their original order, and that property is **stability**: items with equal keys stay in the order they came in. Passes from the low byte up give a correct final order only because each pass is stable.

:::example
Take three keys: `0x0201`, `0x0102` and `0x0101`. Pass 1 sorts by the low byte, which is 1, 2 and 1, so the order becomes `0x0201`, `0x0101`, `0x0102`; the two keys with low byte 1 keep their order. Pass 2 sorts by the high byte, which is 2, 1 and 1. The keys with high byte 1 move first and keep the order of pass 1, so the result is `0x0101`, `0x0102`, `0x0201`, which is sorted.
:::

Strata adds a trick for draw keys. Draw keys differ in a byte or two, because one scene has few cascades, a few thousand meshes and few other fields. The sort first collects the bits in which any key differs from the first key. A byte without such a bit is equal in every key, so the sort skips it.

The 1,000 cubes have equal keys: no pass, no histogram, and the items stay where they are. Where the keys differ in bytes 0, 3 and 6, the sort makes 3 passes.

Stability gives the promise of the page: the same result on every run. The gathering order is the chunk order, which is the order of the visible proxies, and equal keys keep it. The batches and the draw list are therefore the same on every run, with one thread or sixteen.

`SortIndices` is the same sort for lists of 32-bit values.

A list shorter than 256 values goes to `std::sort`, a sorted list is left alone, and the rest goes through `RadixSort`. The renderer uses it on the mesh and material slots that `ResolveAssets` walks, which a GPU's atomics may list in any order.

## Indirect drawing

A direct draw call carries its arguments in the command: index count, instance count and where the data starts. An **indirect draw** is a draw whose arguments the graphics card reads from a buffer at the time it runs. The call names the buffer position instead of the numbers.

Strata writes the arguments of each batch as a `DrawIndexedIndirectArguments`. They hold the index count of the level and the instance count of the batch. They also hold the first index and base vertex at the mesh's place in the :term[geometry pool]{id=geometry-pool}, and the first instance, which is the batch's position in the draw list. The buffer is uploaded where it changed, and the draws point into it. A batch is then 20 bytes of arguments, and a bucket becomes one call that lists many of them.

A **bucket** is a run of consecutive batches that share one pipeline state and one vertex arena (and, for shadows, one cascade), so one setting of the graphics state serves them all.

Three device properties decide how a bucket is drawn. The feature `multiDrawIndirect` lets one call issue many draws from consecutive arguments. The feature `drawIndirectFirstInstance` lets those draws use a first instance other than 0, and without it the draw list scheme fails. The limit `maxDrawIndirectCount` is the most draws one call may issue, at least 65,535 on a device with `multiDrawIndirect`, so a bigger bucket takes several calls.

Where the device lacks either feature, each batch is a direct draw, and the state is still set once for the bucket. The draw arguments that the graphics card itself fills belong to [the GPU-driven path](gpu-driven.md).

## Transparent draws

Blending depends on order: a sheet of glass in front of a wall looks different from the same sheet behind it. Batching by state would change the order of the sheets, so transparent submeshes are not sorted by key. Each one becomes its own batch of one instance, and the list is sorted by distance.

The sort puts glass first. Glass writes depth and reads a copy of what the frame drew before it, so it must come before the blended surfaces that are drawn over it. Within each group the draws run from far to near by the view depth of the proxy's bounds centre. Equal depths use the entity and then the submesh, so the order does not depend on the proxies' order.

For example, three blended sheets at view depths 10, 4 and 7 draw in the order 10, 7, 4. A thousand blended cubes cost 1,000 draws instead of 1, and this is why a scene should keep most of its surfaces opaque. How blending combines the colours is the subject of [clear coat and glass](../light/clearcoat-transmission.md).

## The contract

What callers may assume and must do:

- The same scene gives the same draw order on every run. Gathering writes only to the chunk's own output, the merge follows the chunk order, and the sort is stable. Code that adds to the gathering must not depend on the worker that runs a chunk.
- Gathering draws an instance only when its proxy is resident in the render scene's copy on the graphics card. The vertex shader reads the instances from that buffer, so a draw before the upload would read old data. A new proxy may wait for a later frame ([the GPU copy](render-scene-gpu.md) teaches why).
- Every draw reads its material from the instance. Pipeline state is the only thing a batch splits on. A feature that needs different state adds a key field; one that needs only different data goes in the instance or the material.
- A key's fields tile its 64 bits, checked by a `static_assert`. A new field takes bits from the material, and the assertion fails until the widths add up.

:::rule
Per-instance additions go to parallel buffers and `InstanceData` stays 64 bytes. The record is read for every drawn instance in every pass, so its size is paid each time.
:::

## A toy version

The toy sorts and batches a list of (mesh, material) pairs. It packs a key, sorts it with a stable radix sort that skips bytes equal in every key, and turns runs of equal keys into batches, as the real code does.

:::question
New to C++ here? The toy uses structs, `std::vector`, functions and loops; the basics pages [first programs](../basics/programming-1.md), [functions and loops](../basics/programming-2.md) and [classes and references](../basics/programming-3.md) teach them.
:::

The sketch runs eight draws. Look at how the key's bits change when the material joins, and at the batch list that comes out.

```cpp sketch="draw-batching-toy.cpp"
// A toy of the CPU path's batching: pack each draw's state into a key, sort stably by key, and turn runs of equal keys
// into batches. The draw list holds one entry (the draw's index) per instance, in batch order.
#include <cstdint>
#include <cstdio>
#include <vector>

namespace
{

	struct Draw
	{
		uint32_t Mesh = 0;
		uint32_t Material = 0;
	};

	struct SortItem
	{
		uint64_t Key = 0;
		uint32_t Value = 0;
	};

	struct Batch
	{
		uint32_t Mesh = 0;
		uint32_t FirstInstance = 0;
		uint32_t InstanceCount = 0;
	};

	// Mesh in the high bits; the material in the low 16 bits only when batches are split by material.
	uint64_t MakeKey(const Draw& draw, bool acrossMaterials)
	{
		return (static_cast<uint64_t>(draw.Mesh) << 16) | (acrossMaterials ? 0u : (draw.Material & 0xFFFFu));
	}

	// Least significant byte first, stable, and a byte equal in every key gets no pass.
	void RadixSort(std::vector<SortItem>& items)
	{
		uint64_t differing = 0;
		for (const SortItem& item : items)
			differing |= item.Key ^ items[0].Key;
		for (uint32_t shift = 0; shift < 64; shift += 8)
		{
			if (((differing >> shift) & 0xFF) == 0)
				continue;
			uint32_t offsets[257] = {};
			for (const SortItem& item : items)
				offsets[((item.Key >> shift) & 0xFF) + 1]++;
			for (uint32_t digit = 0; digit < 256; digit++)
				offsets[digit + 1] += offsets[digit];
			std::vector<SortItem> sorted(items.size());
			for (const SortItem& item : items)
				sorted[offsets[(item.Key >> shift) & 0xFF]++] = item;
			items = sorted;
		}
	}

	void Run(const std::vector<Draw>& draws, bool acrossMaterials)
	{
		std::vector<SortItem> items;
		for (uint32_t index = 0; index < draws.size(); index++)
			items.push_back(SortItem { MakeKey(draws[index], acrossMaterials), index });
		RadixSort(items);

		std::vector<Batch> batches;
		std::vector<uint32_t> drawList;
		uint64_t batchKey = 0;
		for (const SortItem& item : items)
		{
			if (batches.empty() || item.Key != batchKey)
			{
				batchKey = item.Key;
				batches.push_back(Batch { draws[item.Value].Mesh, static_cast<uint32_t>(drawList.size()), 0 });
			}
			drawList.push_back(item.Value);
			batches.back().InstanceCount++;
		}

		std::printf("%s materials: %zu draws\n", acrossMaterials ? "across" : "split by", batches.size());
		for (const Batch& batch : batches)
			std::printf("  mesh %u: first instance %u, count %u\n", batch.Mesh, batch.FirstInstance, batch.InstanceCount);
		std::printf("  draw list:");
		for (const uint32_t entry : drawList)
			std::printf(" %u", entry);
		std::printf("\n");
	}

}

int main()
{
	const std::vector<Draw> draws = { { 2, 5 }, { 0, 1 }, { 2, 7 }, { 0, 1 }, { 1, 3 }, { 2, 5 }, { 0, 9 }, { 1, 3 } };
	Run(draws, true);
	Run(draws, false);
	return 0;
}
```

1. **Lines 30–33:** The key puts the mesh above bit 16 and adds the material in the low 16 bits only when batches split by material.
2. **Lines 38–43:** The sort collects the bits in which keys differ and skips every byte without one.
3. **Line 69:** A new key starts a new batch, and an equal key extends the current one.
4. **Lines 74–75:** Each sorted item adds one entry to the draw list and one instance to its batch.

```text output-of="draw-batching-toy.cpp"
across materials: 3 draws
  mesh 0: first instance 0, count 3
  mesh 1: first instance 3, count 2
  mesh 2: first instance 5, count 3
  draw list: 1 3 6 4 7 0 2 5
split by materials: 5 draws
  mesh 0: first instance 0, count 2
  mesh 0: first instance 2, count 1
  mesh 1: first instance 3, count 2
  mesh 2: first instance 5, count 2
  mesh 2: first instance 7, count 1
  draw list: 1 3 6 4 7 0 5 2
```

Across materials the eight draws form 3 batches, one for each mesh, and the draw list is 1, 3, 6, 4, 7, 0, 2, 5. Split by material they form 5 batches, because mesh 0 uses two materials, mesh 1 one and mesh 2 two. Stability shows in the list: the draws 1 and 3 share a key, and 1 stays first. The real code differs in six ways. It packs more fields, gathers in parallel chunks, skips draws that are not resident, drops draws that are too small, cross-fades levels, and writes draw entries instead of plain indices.

## The real code

Gathering runs on each chunk of 2,048 visible proxies. First a proxy is checked: its mesh must be loaded, its instance count must match the mesh's submeshes, and the render scene's GPU copy must hold its instances. Then a proxy whose size on screen is below the quality setting's minimum pixels is counted and dropped (:term[size culling]{id=size-culling}).

```cpp src="Strata/src/Strata/Renderer/SceneRendererExtraction.cpp#L966-L982"
const uint32_t meshSlot = renderScene.GetMeshSlot(proxy);
const Mesh* mesh = m_FrameMeshes[meshSlot];
const uint32_t count = renderScene.GetInstanceCount(proxy);
// Drawn once the GPU holds its instances (a new proxy may wait for a later frame's upload).
if (!mesh || count == 0 || mesh->GetSubmeshes().size() != count || !m_SceneGPU->IsResident(proxy))
	continue;

const AABB& bounds = renderScene.GetWorldBounds(proxy);
const float fraction = m_VisibleFractions[item];
if (minPixels > 0.0f && fraction * viewportHeight < minPixels)
{
	output.SizeCulled++;
	// The culled view's boxes, where the CPU draws the view (the GPU's culling records its own: Scene/Cull.comp).
	if (culledView)
		output.Culled.push_back(proxy | (RenderData::c_CulledBySize << RenderData::c_CulledReasonShift));
	continue;
}
```

1. **Line 966:** The proxy's mesh slot indexes the frame's table of meshes.
2. **Line 970:** A proxy is skipped when its mesh is missing, its instance count does not match, or the GPU copy has not received its instances.
3. **Lines 975–981:** A proxy too small on screen is counted and dropped; when the debug view of dropped objects is on, the proxy is also recorded with the reason.

The test `IsResident` asks whether the upload of the proxy's instances arrived in the GPU copy. The copy's buffer is what the vertex shader reads, and [the render scene's GPU copy](render-scene-gpu.md) teaches it. Next, each submesh of the proxy picks its level and makes its draw.

```cpp src="Strata/src/Strata/Renderer/SceneRendererExtraction.cpp#L1025-L1051"
if (transparent)
{
	output.Transparent.push_back(TransparentDraw { viewDepth, renderScene.GetEntityID(proxy), submeshIndex, instance, meshSlot, lod, doubleSided, mirrored, skinned,
		(materialFlags & c_MaterialTransmissive) != 0 });
	continue;
}
if (opaqueDraws)
{
	const uint32_t keyMaterial = batchAcrossMaterials ? 0u : materialSlot;
	// Submeshes with one level have nothing to fade (nor any state).
	LODSelection::LODFade fade;
	if (fades && submeshes[submeshIndex].LODs.size() > 1)
	{
		fade = LODSelection::UpdateLODFade(m_LODFades[instance], lod, static_cast<uint32_t>(submeshes[submeshIndex].LODs.size()),
			instances[instance].EntityID, fadeFrame, true);
		m_LODFades[instance] = fade.State;
	}
	output.Draws.push_back(SortItem { SceneDrawKey::Make(0, false, mirrored, doubleSided, skinned, meshSlot, submeshIndex, lod, keyMaterial),
		RenderData::MakeDrawEntry(instance, fade.Code), 0 });
	// Both levels while the fade is under way, the old one on the pixels the new one leaves (faded levels are at most
	// 15, within the key's).
	static_assert(SceneDrawKey::c_MaxLODs > 15);
	if (fade.Code != 0)
	{
		output.Draws.push_back(SortItem { SceneDrawKey::Make(0, false, mirrored, doubleSided, skinned, meshSlot, submeshIndex, fade.From, keyMaterial),
			RenderData::MakeDrawEntry(instance, fade.Code + RenderData::c_LODFadeOutgoing), 0 });
	}
```

1. **Lines 1025–1030:** Transparent submeshes go to their own list and skip the key.
2. **Line 1033:** The material enters the key only when batching across materials is off.
3. **Lines 1036–1040:** A submesh with several levels keeps a fade state for its instance.
4. **Lines 1042–1043:** The draw is a sort item: the key from `SceneDrawKey::Make` and the draw entry.
5. **Lines 1046–1051:** While a fade runs, a second entry draws the old level with the outgoing code.

The key's :term[header]{id=header} says what is packed; the next excerpt shows the layout and the check that it adds up.

```cpp src="Strata/src/Strata/Renderer/SceneDrawKey.h#L10-L43"
// The sort key of a CPU-path draw, which SceneRenderer::BuildBatches decodes: pipeline state first (cascade, alpha mask,
// winding, culling, skinning), then mesh, submesh and level of detail, which together make a batch; the material in the
// lowest bits only when batches are split by material. The view's draws, the sun's cascades and the point and spot
// lights' views (cascade 0: each view keeps its own list) share the layout.
namespace SceneDrawKey
{
	constexpr uint32_t c_CascadeShift = 61; // Three bits: RenderData::c_MaxCascades
	constexpr uint32_t c_AlphaMaskShift = 60;
	constexpr uint32_t c_MirroredShift = 59;
	constexpr uint32_t c_DoubleSidedShift = 58;
	constexpr uint32_t c_SkinnedShift = 57;
	constexpr uint32_t c_MeshShift = 37;
	constexpr uint32_t c_SubmeshShift = 21;
	constexpr uint32_t c_LODShift = 16;
	constexpr uint32_t c_MeshBits = 20;     // Mesh slots: at most one per entity (Scene::c_MaxEntities)
	constexpr uint32_t c_SubmeshBits = 16;
	constexpr uint32_t c_LODBits = 5;
	constexpr uint32_t c_MaterialBits = 16; // Material slots beyond this share keys: their batches merge, which is still correct
	constexpr uint32_t c_MaxSubmeshes = 1u << c_SubmeshBits;
	constexpr uint32_t c_MaxLODs = 1u << c_LODBits;
	static_assert(RenderData::c_MaxCascades <= (1u << (64 - c_CascadeShift)), "The key's cascade bits hold every cascade");
	static_assert(c_MeshShift + c_MeshBits == c_SkinnedShift && c_SubmeshShift + c_SubmeshBits == c_MeshShift
		&& c_LODShift + c_LODBits == c_SubmeshShift && c_MaterialBits == c_LODShift, "The key's fields tile its 64 bits");

	inline uint64_t Make(uint32_t cascade, bool alphaMask, bool mirrored, bool doubleSided, bool skinned, uint32_t meshSlot, uint32_t submesh, uint32_t lod,
		uint32_t material)
	{
		return (static_cast<uint64_t>(cascade) << c_CascadeShift) | (static_cast<uint64_t>(alphaMask) << c_AlphaMaskShift)
			| (static_cast<uint64_t>(mirrored) << c_MirroredShift) | (static_cast<uint64_t>(doubleSided) << c_DoubleSidedShift)
			| (static_cast<uint64_t>(skinned) << c_SkinnedShift) | (static_cast<uint64_t>(meshSlot) << c_MeshShift)
			| (static_cast<uint64_t>(submesh) << c_SubmeshShift) | (static_cast<uint64_t>(lod) << c_LODShift)
			| static_cast<uint64_t>(material & ((1u << c_MaterialBits) - 1));
	}
}
```

1. **Lines 16–20:** The cascade and the four flags take the top bits.
2. **Lines 21–23:** The shifts of mesh, submesh and level.
3. **Lines 24–29:** The widths are limits: past them a submesh or a level is not drawn.
4. **Lines 31–32:** The `static_assert` checks that the fields tile the 64 bits.
5. **Lines 37–41:** `Make` shifts each field into place and masks the material to 16 bits.

Chunks merge in chunk order, then `RadixSort` runs.

```cpp src="Strata/src/Strata/Core/RadixSort.cpp#L14-L67"
void RadixSort(std::vector<SortItem>& items, std::vector<SortItem>& scratch)
{
	const size_t count = items.size();
	if (count < 2)
		return;
	ST_CORE_ASSERT(count <= std::numeric_limits<uint32_t>::max(), "RadixSort: {} items are more than its 32-bit counters hold", count);

	// The bits in which some key differs from the first: a byte without any needs no pass, and no histogram either.
	// Draw keys differ in a byte or two (the cascade, the mesh), or not at all.
	const uint64_t first = items[0].Key;
	uint64_t differing = 0;
	for (const SortItem& item : items)
		differing |= item.Key ^ first;
	if (differing == 0)
		return;
	std::array<uint32_t, 8> shifts = {};
	uint32_t passes = 0;
	for (uint32_t byte = 0; byte < 8; byte++)
	{
		if (((differing >> (byte * 8)) & 0xFF) != 0)
			shifts[passes++] = byte * 8;
	}

	// The histograms of the bytes that differ, in one pass over the keys.
	std::array<std::array<uint32_t, 256>, 8> histograms;
	for (uint32_t pass = 0; pass < passes; pass++)
		histograms[pass].fill(0);
	for (const SortItem& item : items)
	{
		for (uint32_t pass = 0; pass < passes; pass++)
			histograms[pass][(item.Key >> shifts[pass]) & 0xFF]++;
	}

	scratch.resize(count);
	std::vector<SortItem>* source = &items;
	std::vector<SortItem>* destination = &scratch;
	for (uint32_t pass = 0; pass < passes; pass++)
	{
		std::array<uint32_t, 256>& histogram = histograms[pass];
		uint32_t offset = 0;
		for (uint32_t& bucket : histogram)
		{
			const uint32_t size = bucket;
			bucket = offset;
			offset += size;
		}
		const uint32_t shift = shifts[pass];
		for (const SortItem& item : *source)
			(*destination)[histogram[(item.Key >> shift) & 0xFF]++] = item;
		std::swap(source, destination);
	}
	if (source != &items)
		items.swap(scratch);
}
```

1. **Lines 23–28:** Collect the bits in which some key differs from the first; with none, return and leave the items in place.
2. **Lines 31–35:** List the bytes that differ; only they get a pass.
3. **Lines 38–45:** All histograms come from one read of the keys.
4. **Lines 52–59:** Counts become start positions.
5. **Lines 61–63:** Items move to the next free position of their byte value, which keeps the order of equal keys, and the two lists swap roles.

`BuildBatches` reads the sorted keys and decodes each run.

```cpp src="Strata/src/Strata/Renderer/SceneRendererExtraction.cpp#L845-L869"
void SceneRenderer::BuildBatches(std::vector<SortItem>& draws, std::vector<SceneDrawBatch>& outBatches, std::vector<uint32_t>& outDrawList)
{
	outBatches.clear();
	uint64_t batchKey = 0;
	for (const SortItem& draw : draws)
	{
		if (outBatches.empty() || draw.Key != batchKey)
		{
			batchKey = draw.Key;
			SceneDrawBatch batch;
			batch.MeshSlot = static_cast<uint32_t>((draw.Key >> SceneDrawKey::c_MeshShift) & ((1ull << SceneDrawKey::c_MeshBits) - 1));
			batch.SubmeshIndex = static_cast<uint32_t>((draw.Key >> SceneDrawKey::c_SubmeshShift) & (SceneDrawKey::c_MaxSubmeshes - 1));
			batch.LOD = static_cast<uint32_t>((draw.Key >> SceneDrawKey::c_LODShift) & (SceneDrawKey::c_MaxLODs - 1));
			batch.DoubleSided = ((draw.Key >> SceneDrawKey::c_DoubleSidedShift) & 1) != 0;
			batch.Mirrored = ((draw.Key >> SceneDrawKey::c_MirroredShift) & 1) != 0;
			batch.Skinned = ((draw.Key >> SceneDrawKey::c_SkinnedShift) & 1) != 0;
			batch.AlphaMask = ((draw.Key >> SceneDrawKey::c_AlphaMaskShift) & 1) != 0;
			batch.Cascade = static_cast<uint32_t>(draw.Key >> SceneDrawKey::c_CascadeShift);
			batch.FirstInstance = static_cast<uint32_t>(outDrawList.size());
			outBatches.push_back(batch);
		}
		outDrawList.push_back(draw.Value);
		outBatches.back().InstanceCount++;
	}
}
```

1. **Line 851:** A key that differs from the previous one starts a new batch.
2. **Lines 855–862:** The batch's fields are decoded from the key.
3. **Line 863:** The first instance is the draw list's size at that moment.
4. **Lines 866–867:** Every item adds one entry to the list and one to the batch's count.

Transparent submeshes skip the key and become batches of one instance, as the section on transparent draws explained.

The lists then go to the graphics card. The upload compares the new list with the one the buffer holds and writes only the range between the first and the last entry that differ. If a frame changes the entries 40 to 52 of a list, the upload writes 13 entries of 4 bytes, which is 52 bytes, whatever the list's length.

```cpp src="Strata/src/Strata/Renderer/SceneRendererExtraction.cpp#L1278-L1309"
template<typename T>
uint64_t SceneRenderer::UploadChangedRange(nvrhi::ICommandList* commandList, nvrhi::IBuffer* buffer, std::vector<T>& list, std::vector<T>& uploaded, bool full)
{
	const auto equal = [](const T& a, const T& b) { return std::memcmp(&a, &b, sizeof(T)) == 0; };
	size_t first = 0;
	size_t last = list.size();
	if (!full)
	{
		// The range from the first to the last entry that differs from what the buffer holds.
		const size_t common = std::min(list.size(), uploaded.size());
		first = static_cast<size_t>(std::mismatch(list.begin(), list.begin() + static_cast<ptrdiff_t>(common), uploaded.begin(), equal).first - list.begin());
		if (list.size() <= uploaded.size())
		{
			last = first;
			for (size_t index = common; index > first; index--)
			{
				if (!equal(list[index - 1], uploaded[index - 1]))
				{
					last = index;
					break;
				}
			}
		}
	}
	uint64_t bytes = 0;
	if (last > first)
	{
		bytes = (last - first) * sizeof(T);
		commandList->writeBuffer(buffer, list.data() + first, bytes, first * sizeof(T));
	}
	// The buffer now holds the new list; the old one is the scratch of the next frame's list.
	uploaded.swap(list);
```

1. **Lines 1283–1300:** Unless the whole list is sent, the range runs from the first entry that differs to the last.
2. **Line 1306:** Only that range is written to the buffer.
3. **Line 1309:** The lists swap, so the old one is the next frame's scratch.

`BuildDrawArguments` turns each batch into arguments at its mesh's place in the geometry pool.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L2100-L2128"
void SceneRenderer::BuildDrawArguments()
{
	m_DrawArgumentsBuild.clear();
	const auto append = [this](const SceneDrawBatch& batch)
	{
		const GeometryAllocation& geometry = m_FrameGeometry[batch.MeshSlot];
		const Submesh& submesh = m_FrameMeshes[batch.MeshSlot]->GetSubmeshes()[batch.SubmeshIndex];
		const MeshLOD& lod = submesh.LODs[batch.LOD];
		nvrhi::DrawIndexedIndirectArguments arguments;
		arguments.indexCount = lod.IndexCount;
		arguments.instanceCount = batch.InstanceCount;
		arguments.startIndexLocation = geometry.FirstIndex + lod.IndexOffset;
		arguments.baseVertexLocation = static_cast<int32_t>(geometry.FirstVertex + submesh.BaseVertex);
		arguments.startInstanceLocation = batch.FirstInstance;
		m_DrawArgumentsBuild.push_back(arguments);
	};
	// Opaque batches (the prepass and the opaque pass draw them alike), transparent ones, the shadow batches, the selection
	// mask's, then the local shadow views'.
	for (const SceneDrawBatch& batch : m_OpaqueBatches)
		append(batch);
	for (const SceneDrawBatch& batch : m_TransparentBatches)
		append(batch);
	for (const SceneDrawBatch& batch : m_ShadowBatches)
		append(batch);
	for (const SceneDrawBatch& batch : m_SelectionBatches)
		append(batch);
	for (const SceneDrawBatch& batch : m_LocalShadowBatches)
		append(batch);
}
```

1. **Lines 2105–2108:** The batch's geometry allocation, submesh and level.
2. **Lines 2109–2113:** The counts, the offsets in the pool and the first instance fill the arguments.
3. **Lines 2118–2127:** Opaque batches come first, so a batch's argument sits at its own index.

`DrawBuckets` records the draws.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L2136-L2182"
state.indexBuffer = nvrhi::IndexBufferBinding { pool.GetIndexBuffer(), nvrhi::Format::R32_UINT, 0 };
state.indirectParams = indirect ? m_DrawArgumentBuffer.Get() : nullptr;
size_t first = 0;
while (first < batches.size())
{
	// A bucket: the batches up to the next change of pipeline state or vertex arena (and, for shadows, of cascade).
	const SceneDrawBatch& head = batches[first];
	const PipelineKey key = getKey(head);
	const GeometryArena arena = m_FrameGeometry[head.MeshSlot].Arena;
	size_t end = first + 1;
	while (end < batches.size() && getKey(batches[end]) == key && m_FrameGeometry[batches[end].MeshSlot].Arena == arena && batches[end].Cascade == head.Cascade)
		end++;

	state.pipeline = GetScenePipeline(key);
	state.vertexBuffers = {
		nvrhi::VertexBufferBinding { pool.GetPositionBuffer(arena), 0, 0 },
		nvrhi::VertexBufferBinding { pool.GetAttributeBuffer(arena), 1, 0 }
	};
	if (key.Skinned)
		state.vertexBuffers.push_back(nvrhi::VertexBufferBinding { pool.GetSkinBuffer(), 2, 0 });
	if (prepareState)
		prepareState(head, state);
	commandList->setGraphicsState(state);
	if (afterState)
		afterState(head);
	if (indirect)
	{
		// Calls of at most the device's (or the specification's) draws each.
		const size_t maxDraws = GetMaxDrawsPerIndirectCall();
		for (size_t call = first; call < end;)
		{
			const size_t draws = std::min(maxDraws, end - call);
			commandList->drawIndexedIndirect(static_cast<uint32_t>((firstArgument + call) * sizeof(nvrhi::DrawIndexedIndirectArguments)),
				static_cast<uint32_t>(draws));
			m_Stats.DrawCommands++;
			call += draws;
		}
	}
	else
	{
		for (size_t index = first; index < end; index++)
		{
			// The frame's arguments: the upload made them what the argument buffer holds (m_DrawArguments).
			const nvrhi::DrawIndexedIndirectArguments& arguments = m_DrawArguments[firstArgument + index];
			nvrhi::DrawArguments draw;
			draw.vertexCount = arguments.indexCount;
			draw.instanceCount = arguments.instanceCount;
```

1. **Lines 2139–2147:** A bucket grows while the :term[pipeline key]{id=pipeline-key} and the vertex arena stay equal.
2. **Lines 2149–2158:** One setting of the graphics state serves the whole bucket.
3. **Lines 2164–2171:** An indirect call issues at most the limit's draws, and a larger bucket takes several calls.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| One draw per object and material | Simple renderers and many older engines | No draw list and no instance buffer to keep | Thousands of calls and state changes; 1,000 cubes cost 1,000 draws |
| The material in the batch key | Renderers without per-instance materials | Shaders that need no material buffer | One draw per material on the 1,000 cubes; the sorting work stays |
| A comparison sort of draw items | Many engines | Less code than a radix sort | A cost that grows faster than the number of draws, and no skipped bytes |
| Direct draws per batch only | Renderers without `multiDrawIndirect` | Works on every device | One call per batch instead of one per bucket |
| Culling and building draws on the GPU | Modern engines with large scenes | The processor does no per-draw work | Complex code; Strata's [GPU-driven path](gpu-driven.md) does this and keeps this one as its reference |

## How it is tested

`GPU.RenderScene` renders the 1,000 cubes with 1,000 materials on both paths. It checks 1 opaque draw call across materials and 1,000 with `BatchAcrossMaterials` off, with identical pixels and entity identifiers, and that the shadow batches have one batch per cascade. `Core.RadixSort` compares the sort with `std::stable_sort` on 20,000 random keys under five masks, checks that equal keys leave the list in place without a pass, and compares `SortIndices` with `std::sort`.

The measured proof is in the `PerfGPU.Renderer` suite: `StrataTests/Perf/Budgets.json` records that 10,000 materials draw in :value{key="perf.PerfGPU.Renderer.Render10kMaterials.OpaqueDrawCalls.Measured"} opaque call and 10,000 distinct meshes in :value{key="perf.PerfGPU.Renderer.Render10kUniqueMeshes.DrawCommands.Measured"} draw commands. Run the first two suites with `StrataTests.exe --test-suite=GPU.RenderScene` and `--test-suite=Core.RadixSort`; the perf suites need a Release build and the label `perf`. [The performance lab](../engineering/perf-lab.md) teaches the method.

## Changing it safely

To add a field to the key, take its bits from the material, edit `SceneDrawKey::Make` and `BuildBatches` together, and let the `static_assert` guide you. A field that changes often goes low. To add a state that splits batches, also add it to `PipelineKey`, because buckets compare that. A change to what is drawn must keep the CPU path and the GPU-driven path equal: the `GPU.SceneRenderer.GPUDriven` tests compare them.

:::rule
Gathering is parallel and the merge is in chunk order, so the result never depends on threads. Shading must stay independent of draw order. These rules keep the draws the same on every run, which the shadow caches and the tests rely on.
:::

Run `GPU.RenderScene`, `Core.RadixSort` and the perf counts before a change.

## Summary

- A shader finds its instance through the draw list, indexed with the vertex input that includes the base instance.
- A 64-bit key packs the state; a decode reverses it field by field.
- Batching across materials makes 1,000 cubes in 1,000 colours one opaque draw.
- The radix sort makes one pass for each byte that differs in some key.
- One instance goes from its sort item through a batch and its arguments to one indirect call.

## Check yourself

1. Decode the key `0x040000A000410000`. Which flag is set, and what are the mesh slot, submesh and level?

   :::answer{tests="decode-key"}
   Bit 58 is set (the top byte `0x04` is $2^{58}$), so the draw is double-sided. The mesh is `(key >> 37) & 0xFFFFF`, which is 5. The low part `0x410000` is $2 \cdot 2^{21} + 2^{16}$: submesh 2, level 1. The material is 0 because batching across materials omits it.
   :::

2. A scene has 600 instances of mesh A with 40 materials and 400 of mesh B with 25 materials, all single-sided and not skinned, one submesh each, one level. How many opaque draws with and without `BatchAcrossMaterials`?

   :::answer{tests="predict-draws"}
   With it, 2 draws: one for each mesh. Without it, 65: the keys differ by material, so each of the 40 materials of A and 25 of B starts its own batch, if every material is used.
   :::

3. A batch holds 3 instances at first instance 5,000. Which values reach the shader with `SV_InstanceID` and with `SV_VulkanInstanceID`, and which list entries does each read?

   :::answer{tests="draw-list-read"}
   `SV_VulkanInstanceID` gives 5,000, 5,001 and 5,002: the batch's own entries. `SV_InstanceID` gives 0, 1 and 2, the first entries of the list, which belong to another batch, so the wrong objects draw. Strata uses the first because it includes the base instance.
   :::

4. Two keys are `0x0000000000FF0001` and `0x0000000000020001`. How many passes does the sort make?

   :::answer{tests="radix-passes"}
   One. The keys differ only in the bits of `0xFD0000`, which lie in one byte (byte 2). The other bytes are equal in both keys and get no pass.
   :::

5. Which function writes the first instance, the index count and the geometry pool offsets of a batch into draw arguments?

   :::answer{tests="trace-draw"}
   `SceneRenderer::BuildDrawArguments`. `BuildBatches` makes the batch with its first instance and count, and `DrawBuckets` records the call that reads the arguments; neither writes the offsets.
   :::

## Exercises

1. **Basic.** The toy draws 1,000 cubes of one mesh with 1,000 different materials in slots 0 to 999. How many batches and how many sort passes result across materials, and with the material in the key?

   :::answer[Worked solution]{tests="predict-draws,radix-passes"}
   Across materials every key is equal, so the sort makes no pass and the result is 1 batch. With the material in the low 16 bits the keys differ in bytes 0 and 1, because slots up to 999 need 10 bits. That makes 2 passes and 1,000 batches, one for each material.
   :::

2. **Medium.** Build key sets that need one, three and eight passes, and check that equal keys keep their order.

   :::answer[Worked solution]{solution="sketches/draw-batching-passes.cpp" tests="radix-passes"}
   One pass needs keys that differ only in one byte, three need bytes 0, 3 and 6, and eight need every byte. The sketch builds them from small numbers: `0x1200 + i`, `i` repeated in three bytes, and `i * 0x0101010101010101`. It sorts each set twice with distinct values and checks order and stability.

   ```cpp sketch="draw-batching-passes.cpp"
   // How many passes a radix sort of 64-bit keys makes: one per byte in which some key differs from the first, and whether
   // equal keys keep their order.
   #include <cstdint>
   #include <cstdio>
   #include <vector>

   namespace
   {

   	struct SortItem
   	{
   		uint64_t Key = 0;
   		uint32_t Value = 0;
   	};

   	// Sorts the items and returns the number of passes it made.
   	uint32_t RadixSort(std::vector<SortItem>& items)
   	{
   		uint64_t differing = 0;
   		for (const SortItem& item : items)
   			differing |= item.Key ^ items[0].Key;
   		uint32_t passes = 0;
   		for (uint32_t shift = 0; shift < 64; shift += 8)
   		{
   			if (((differing >> shift) & 0xFF) == 0)
   				continue;
   			passes++;
   			uint32_t offsets[257] = {};
   			for (const SortItem& item : items)
   				offsets[((item.Key >> shift) & 0xFF) + 1]++;
   			for (uint32_t digit = 0; digit < 256; digit++)
   				offsets[digit + 1] += offsets[digit];
   			std::vector<SortItem> sorted(items.size());
   			for (const SortItem& item : items)
   				sorted[offsets[(item.Key >> shift) & 0xFF]++] = item;
   			items = sorted;
   		}
   		return passes;
   	}

   	// Every key twice: values 0 to 3 in falling key order, then 100 to 103 in rising order, so a sort that is not stable shows.
   	void Report(const char* name, uint64_t (*makeKey)(uint32_t))
   	{
   		std::vector<SortItem> items;
   		for (uint32_t index = 0; index < 4; index++)
   			items.push_back(SortItem { makeKey(3 - index), index });
   		for (uint32_t index = 0; index < 4; index++)
   			items.push_back(SortItem { makeKey(index), 100 + index });
   		const uint32_t passes = RadixSort(items);
   		bool stable = true;
   		for (size_t index = 1; index < items.size(); index++)
   		{
   			const bool ascending = items[index - 1].Key <= items[index].Key;
   			const bool keepsOrder = items[index - 1].Key != items[index].Key || items[index - 1].Value < items[index].Value;
   			stable = stable && ascending && keepsOrder;
   		}
   		std::printf("%s: %u passes, sorted and stable: %s\n", name, passes, stable ? "yes" : "no");
   	}

   }

   int main()
   {
   	Report("low byte only", [](uint32_t i) { return static_cast<uint64_t>(0x1200 + i); });
   	Report("bytes 0, 3 and 6", [](uint32_t i) { return static_cast<uint64_t>(i) | (static_cast<uint64_t>(i) << 24) | (static_cast<uint64_t>(i) << 48); });
   	Report("all eight bytes", [](uint32_t i) -> uint64_t { return static_cast<uint64_t>(i) * 0x0101010101010101ull; });
   	return 0;
   }
   ```

   ```text output-of="draw-batching-passes.cpp"
   low byte only: 1 passes, sorted and stable: yes
   bytes 0, 3 and 6: 3 passes, sorted and stable: yes
   all eight bytes: 8 passes, sorted and stable: yes
   ```

   1. **Lines 19–22:** The bits in which some key differs from the first decide which bytes get a pass.
   2. **Lines 25–27:** A byte without such a bit is skipped; every other byte counts one pass.
   3. **Lines 50–55:** The check demands ascending keys and, for equal keys, ascending values, which is stability.

   Each line names a key set, the passes its sort made, and whether the result was sorted and stable.
   :::

3. **Medium.** A scene has material slots 1 and 65,537 on two instances of one mesh, batching across materials off. What happens?

   :::answer[Worked solution]{tests="decode-key"}
   The key keeps the low 16 bits of the slot, `65,537 & 0xFFFF`, which is 1, so both instances have the same key and merge into one batch. This stays correct because the shader reads each instance's own material; the batches only lose their split.
   :::

4. **Hard.** Trace it yourself: follow one cube of the 1,000 with a debugger from its sort item to the call that draws it. Name each function and the entry's value.

   :::answer[Worked solution]{tests="trace-draw"}
   In `SceneRenderer::GatherDraws` (`SceneRendererExtraction.cpp`) the cube's chunk pushes a `SortItem` with the key from `SceneDrawKey::Make` and the value `RenderData::MakeDrawEntry(instance, 0)`, which equals its instance index. The merge copies it into `m_Draws`, `RadixSort` leaves it in place (all keys equal), and `BuildBatches` appends the entry to the draw list and counts it in the single batch of 1,000. `BuildDrawArguments` turns the batch into arguments with instance count 1,000. `DrawBuckets` (`SceneRenderer.cpp`) sets the state once and calls `drawIndexedIndirect`.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp`: `GatherDraws`, `BuildBatches`, `UploadChangedRange`.
- `Strata/src/Strata/Renderer/SceneDrawKey.h`: the key.
- `Strata/src/Strata/Core/RadixSort.cpp`: `RadixSort` and `SortIndices`.
- `Strata/src/Strata/Renderer/SceneRenderer.cpp`: `BuildDrawArguments`, `DrawBuckets`.
- Tests: `GPU.RenderScene`, `Core.RadixSort`, `PerfGPU.Renderer`.
- Setting: `BatchAcrossMaterials`, `IndirectMode` and `MaxDrawsPerIndirectCall` of `SceneRendererSpecification`.

## Further reading

- Vulkan specification, draw commands and `vkCmdDrawIndexedIndirect` (advanced): the arguments an indirect draw reads.
- Christer Ericson, "Order your graphics draw calls around!" (intermediate): sort keys for draws.
- Introduction to Algorithms, chapter on counting and radix sort (intermediate): why passes must be stable.
