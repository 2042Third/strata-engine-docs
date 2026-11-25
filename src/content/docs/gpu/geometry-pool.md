---
id: gpu/geometry-pool
title: "Meshes on the GPU and the geometry pool"
description: "How Strata keeps every mesh's vertices and indices in a few shared buffers, hands out stable handles and moves geometry without the meshes knowing."
kind: internals
size: M
tracks: [E]
needs: [gpu/upload-queue, gpu/binding]
time: 60
learn:
  - id: shared-buffers
    text: explain why Strata keeps all meshes in a few shared buffers and reaches each one by offsets
  - id: range-sizes
    text: compute the rounded ranges, the bytes and the grown capacity a mesh takes in the pool
  - id: compaction
    text: trace how compaction moves a mesh while its handle stays valid
  - id: pool-contract
    text: name what code that draws a mesh must do each frame, and why
since: 0.4.0
status: final
---

A mesh is a list of corner points (vertices) and a list of triangles that join them. Each triangle is three indices: the numbers of its three corners in the vertex list, so a corner shared by many triangles is stored once. The geometry pool is the part of the :term[renderer]{id=renderer} that keeps the vertices and triangles of every mesh in the scene on the :term[graphics processing unit]{id=gpu} (GPU), in a few large shared buffers. It decides where each mesh lives, grows the buffers when they fill, gathers the gaps that deleted meshes leave, and frees memory only when the card no longer reads it. It does not decide what is drawn, in which order, or at which level of detail: those belong to the draw pages.

## The problem and how engines solve it

Suppose a scene holds 1,000 different meshes and each owns a buffer for its vertices and one for its indices. Before every draw the renderer must bind that mesh's buffers, so a frame costs 1,000 binds and at least 1,000 draw calls. Draws that could be merged into one call cannot be, because they read different buffers.

Engines meet this in four common ways, and each has a price.

- **A buffer per mesh.** Simple, and freeing a mesh frees its buffer. The price is the bind and the draw call per mesh, and thousands of small allocations.
- **One buffer per vertex format.** All meshes of one format share a buffer, so draws of the same material can share state. The price is that the buffer must be sized in advance, and a deleted mesh leaves a hole.
- **A pool with suballocation.** One large buffer is cut into ranges that an :term[allocator]{id=allocator} hands out and takes back. The price is the allocator itself, the small gaps that deleted meshes leave and the need to move ranges.
- **Streams.** Within any of these, a vertex can be stored with its position, normal and :term[texture coordinates]{id=texture-coordinates} side by side, or as separate streams (all positions in one buffer, all normals in another). Side by side reads one place per vertex; separate streams let a pass that needs only positions read only positions.

Strata takes the third way and separate streams. A draw binds the pool's buffers once and then reaches any mesh by offsets, so draws of different meshes share their state. That is also what allows one indirect draw call to cover many meshes, which [Batching, buckets and indirect draws](../draw/batching.md) teaches.

## The map: one pool, a few buffers

The **geometry pool** is the object that owns the shared buffers holding every mesh's vertices and indices, and the tables that say where each mesh lives.

Its memory has two kinds of buffer. A vertex buffer set is an **arena**: one large block of memory, from which the pool cuts ranges for meshes. The Static arena holds ordinary meshes. The Skinned arena holds meshes that bend with a skeleton, and it has one more stream. A third arena, the index arena, holds the 32-bit indices of every mesh.

```mermaid caption="The pool's memory. A mesh holds only a handle. The allocation table turns the handle into a range in the vertex arena and a range in the index arena, and compaction can change that range without touching the mesh." alt="Boxes joined by arrows. A mesh with a handle points to the allocation table. The table points to the Static or Skinned vertex arena and to the index arena. Each arena has used ranges and free gaps, and compaction slides the used ranges toward the start."
flowchart LR
  Mesh["Mesh: handle 7"] --> Table["Allocation table: handle 7 to ranges"]
  Table --> Static["Static arena: positions, attributes"]
  Table --> Skinned["Skinned arena: positions, attributes, skin"]
  Table --> Index["Index arena: 32-bit indices"]
  Static --> Free["Free gaps between meshes"]
  Index --> Free
  Compaction["Compaction"] -. slides ranges down .-> Free
```

A mesh never stores where it is. A **`GeometryHandle`** is a number that names a mesh's place in the pool and stays the same for the mesh's whole life, while the pool's table maps it to the ranges the mesh holds now. The mesh stores only this number.

The table gives the current ranges as a `GeometryAllocation`: the arena, the first vertex and the vertex count, the first index and the index count. Handle 0 is `c_InvalidGeometry`. Later meshes receive freed handles again.

### A mesh on the GPU

A vertex in Strata's pool takes 48 :term[bytes]{id=byte}, split into two streams that are separate buffers. The first holds the position, three 32-bit floats: 12 bytes.

The second holds the attributes. The normal takes 12 bytes. The tangent takes 16: three floats for the direction and one whose sign says which way the :term[bitangent]{id=bitangent} points. The texture coordinates take 8, so the stream is 36 bytes per vertex.

A skinned vertex has a third stream of 16 bytes: four joint numbers and four weights, each stored in 16 bits.

Why two streams and not one? A pass that needs only where a vertex is does not have to read the other 36 bytes. The shadow passes read the position and the texture coordinates, so their :term[input layouts]{id=input-layout} name only those attributes, and the :term[shader]{id=shader} code that never reads a stream costs no memory traffic for it.

Each mesh is cut into **submeshes**: parts of the mesh that each use one material, with their own base vertex, vertex count and levels of detail. A level of detail is a simpler copy of the part for use when it is far away; [Levels of detail](../draw/lod.md) says how one is chosen. A submesh's indices count from its base vertex, so one draw adds the mesh's first vertex to the submesh's base vertex and the indices stay small.

Triangles are counter-clockwise: seen from outside, a :term[front face]{id=winding-order} lists its three vertices against the clock. Upload goes through the queue from [the upload queue](upload-queue.md): a mesh asks the pool for ranges, and the queue copies its positions, attributes, skin and indices into them in steps within the frame's budget.

After the upload, the mesh keeps its positions and indices in ordinary memory, because physics collision shapes read them; [Building bodies](../physics/building-bodies.md) uses them. Only shading reads the attributes, so the mesh frees its copy of them, and of the skin stream, once they are on the graphics card. The built-in shapes (cube, sphere, plane, quad and more) come from `MeshFactory`, a set of functions that build procedural meshes. The engine registers all eight of them as built-in assets with reserved handles, so a scene names a cube like any other mesh.

## The contract

The pool promises one thing and asks several. It promises that a handle stays valid for the mesh's life, whatever happens to the buffers. In return, callers follow these rules.

- **Hold the handle, never the offsets.** Compaction and growth change a mesh's ranges between frames. A cached first vertex from last frame points at another mesh's vertices, or at nothing.
- **Read geometry through the pool every frame.** `Mesh::GetGeometry` returns the current ranges; they stay valid until the next `BeginFrame` or `Allocate` of the pool. The scene renderer copies each drawn mesh's ranges once, when it gathers the frame.
- **Make binding sets again when the buffer version changes.** Growth replaces whole buffers, and `GeometryPool::GetBufferVersion` changes when it does; a binding set that holds an old buffer would read memory the pool has let go.
- **Free from any thread, but expect the memory later.** `Free` records the handle; the ranges return only after the GPU has finished the frames that might read them, which the pool learns through :term[event queries]{id=fence}, like the deferred release of [Resource lifetimes](resources-lifetimes.md).
- **Geometry in an upload never moves.** While `SetUploading` is on for a handle, compaction skips it; otherwise the copies in the queue would write to the old place.

:::rule
The engine's guide forbids storing where a mesh lives: compaction and growth move geometry, so each frame asks the pool again. The pool's table and `Mesh::GetGeometry` are the only places that know where a mesh is now. See [Changing it safely](#changing-it-safely).
:::

The limits shape what the pool can hold.

| Quantity | Value | Why |
| --- | --- | --- |
| Largest buffer, per stream | 2 GiB | One buffer must stay within what the driver allows to create |
| Vertices per vertex arena | about 59.6 million | 2 GiB divided by the 36-byte attribute stream |
| Indices in all | 536 million | 2 GiB divided by 4 bytes |
| Vertex range rounding | 16 vertices | Fewer, larger free ranges |
| Index range rounding | 64 indices | The same |
| Start sizes | 65,536 static vertices, 4,096 skinned vertices, 262,144 indices | A small scene costs little |

Growth doubles a buffer's capacity, or adds what a failed request needed if that is more. A mesh that does not fit makes the pool grow at once. If the open :term[upload batch]{id=batch-gpu} already wrote into the buffers, `Allocate` answers with `Retry`, and the mesh uploads after the next frame's growth. A mesh larger than one whole buffer can never fit; it fails with an error in the log.

:::example
A mesh has 100 vertices and 300 indices and goes into the Static arena. Its vertex range rounds up to 7 times 16, which is 112 vertices, and its index range to 5 times 64, which is 320 indices. In bytes: 112 times 48 is 5,376 for vertices and 320 times 4 is 1,280 for indices, 6,656 in all.

The pool starts with 65,536 vertices, which is 3 MiB (3,145,728 bytes) of vertex data. Now a second mesh of 100,000 vertices arrives. No free range holds it, so the pool must grow: the doubled capacity is 131,072, the capacity plus the request is 165,536, and the larger wins. 165,536 divides by 16 exactly, so the new buffers hold 165,536 vertices and the old data is copied across on the GPU.
:::

## A toy version: a range allocator

The pool cuts its buffers into ranges with a **range allocator** (also called an offset allocator). It is an object that holds no memory, only a record of which ranges of a numbered space are used and which are free. Asked for a number of units, it answers with an offset.

:::question
The toy uses classes, a `std::map` and a loop over the map. If those are new, read [C++ classes](../basics/cpp-classes.md) and [data structures](../basics/data-structures.md) first.
:::

The toy below is such an allocator in about 110 lines. Allocation takes the lowest free range that is large enough; freeing merges a range with its free neighbours; compaction moves the highest block into the lowest hole that holds it. The test in `main` makes eight blocks of 128 units, frees every second one, and compacts.

```cpp sketch="gpu-geometry-pool-toy.cpp"
// A toy range allocator: first fit, free ranges that merge, and a compaction that moves blocks down into holes.
#include <cstdint>
#include <cstdio>
#include <map>
#include <vector>

struct Move
{
	uint32_t From;
	uint32_t To;
	uint32_t Size;
};

class ToyAllocator
{
public:
	explicit ToyAllocator(uint32_t capacity)
		: m_Capacity(capacity)
	{
		m_Free[0] = capacity;
	}

	// The lowest offset whose free range holds `size` units, or ~0u when none does.
	uint32_t Allocate(uint32_t size)
	{
		for (const auto& [offset, freeSize] : m_Free)
		{
			if (freeSize < size)
				continue;
			const uint32_t start = offset;
			const uint32_t rest = freeSize - size;
			m_Free.erase(start);
			if (rest > 0)
				m_Free[start + size] = rest;
			m_Used[start] = size;
			return start;
		}
		return ~0u;
	}

	void Free(uint32_t offset)
	{
		uint32_t size = m_Used.at(offset);
		m_Used.erase(offset);
		const auto next = m_Free.find(offset + size);
		if (next != m_Free.end())
		{
			size += next->second;
			m_Free.erase(next);
		}
		auto previous = m_Free.lower_bound(offset);
		if (previous != m_Free.begin() && (--previous)->first + previous->second == offset)
			previous->second += size;
		else
			m_Free[offset] = size;
	}

	// The free units outside the largest free range, as a share of the capacity.
	float GetScatteredFreeShare() const
	{
		uint32_t total = 0;
		uint32_t largest = 0;
		for (const auto& [offset, size] : m_Free)
		{
			total += size;
			largest = size > largest ? size : largest;
		}
		return static_cast<float>(total - largest) / static_cast<float>(m_Capacity);
	}

	// Moves the highest block into the lowest hole that holds it, until no block can move down.
	std::vector<Move> Compact()
	{
		std::vector<Move> moves;
		for (bool moved = true; moved;)
		{
			moved = false;
			for (auto block = m_Used.rbegin(); block != m_Used.rend() && !moved; ++block)
			{
				const uint32_t from = block->first;
				const uint32_t size = block->second;
				Free(from);
				const uint32_t to = Allocate(size);
				if (to != from)
				{
					moves.push_back(Move { from, to, size });
					moved = true;
				}
			}
		}
		return moves;
	}

private:
	uint32_t m_Capacity;
	std::map<uint32_t, uint32_t> m_Free; // Offset to size
	std::map<uint32_t, uint32_t> m_Used; // Offset to size
};

int main()
{
	ToyAllocator allocator(1024);
	uint32_t offsets[8];
	for (uint32_t index = 0; index < 8; index++)
		offsets[index] = allocator.Allocate(128);
	for (uint32_t index = 1; index < 8; index += 2)
		allocator.Free(offsets[index]);
	std::printf("scattered share before: %.3f\n", allocator.GetScatteredFreeShare());
	for (const Move& move : allocator.Compact())
		std::printf("move %u units from %u to %u\n", move.Size, move.From, move.To);
	std::printf("scattered share after: %.3f\n", allocator.GetScatteredFreeShare());
}
```

```text output-of="gpu-geometry-pool-toy.cpp"
scattered share before: 0.375
move 128 units from 768 to 128
move 128 units from 512 to 384
scattered share after: 0.000
```

1. **Lines 24–39:** `Allocate` walks the free ranges from the lowest offset and takes the first that holds the size; the rest stays free.
2. **Lines 41–56:** `Free` joins the freed range to a free range right after it and right before it, so neighbours never stay split.
3. **Lines 82–84:** freeing a block and allocating it again finds the lowest hole that holds it; a new offset is a move.

Before the compaction, four free holes of 128 units sit between four blocks. The scattered share is the free units outside the biggest hole (512 free minus 128) over the capacity of 1,024: 0.375. Two moves gather them: the block at 768 goes to 128, and the block at 512 goes to 384. Afterward one free range of 512 units remains at the end.

The real allocator differs from the toy in four ways. It keeps free ranges in lists by size class, so finding a fit does not scan every range. It supports alignment. Its compaction has a second rule, a slide, for when no hole holds a block whole. And it stops after a budget of units per call and skips blocks that must not move now.

## The real code, in the order data flows

A mesh meets the pool in `Mesh::FinalizeOnMainThread`, which runs when the mesh's data is ready. It asks the pool for ranges. The pool's own :term[header]{id=header} describes what happens next.

```cpp src="Strata/src/Strata/Renderer/GeometryPool.h#L62-L72"
// Every mesh's GPU geometry, in shared buffers (Renderer::GetGeometryPool): two vertex arenas - Static (positions 12 B
// and attributes 36 B per vertex, in two buffers) and Skinned (the same plus the 16-byte skin stream) - and one index arena
// of 32-bit indices. A draw binds the arena's buffers once and reaches any mesh by its offsets, so draws of different
// meshes share their state (and indirect draws).
//
// Meshes get a stable GeometryHandle; the pool's table maps it to the current GeometryAllocation, so moving geometry
// changes no mesh. Freed ranges become reusable once the GPU finished the work submitted before they were freed (event
// queries, like DeferredReleaseQueue). The pool grows by creating larger buffers and copying on the GPU (the old ones go
// through Renderer::ReleaseDeferred), and compacts by GPU copies within c_MaxDefragBytesPerFrame when the scattered free
// space exceeds c_CompactionThreshold of an arena: both in BeginFrame, between upload batches, never moving geometry
// whose upload is in progress. Main thread only, but for Free.
```

1. **Lines 62–65:** two vertex arenas and one index arena; a draw binds the buffers once and reaches any mesh by offsets.
2. **Lines 67–72:** handles are stable, frees wait for the GPU, and growth and compaction happen in `BeginFrame` between upload batches.

### Allocating

`Allocate` rounds the request up to the rounding sizes and refuses at once a request that cannot fit any buffer. It then tries both arenas, and when either fails it records how much more it needs.

```cpp src="Strata/src/Strata/Renderer/GeometryPool.cpp#L154-L200" from="const uint32_t vertexUnits" to="GeometryHandle handle = c_InvalidGeometry;" symbol="GeometryPool::Allocate"
const uint32_t vertexUnits = RoundUp(vertices, c_VertexGranularity);
const uint32_t indexUnits = RoundUp(indices, c_IndexGranularity);
// A mesh larger than the largest buffer never fits.
if (static_cast<uint64_t>(vertexUnits) * c_AttributeStride > c_MaxBufferBytes || static_cast<uint64_t>(indexUnits) * c_IndexStride > c_MaxBufferBytes)
	return {};

uint32_t firstVertex = RangeAllocator::c_InvalidOffset;
uint32_t firstIndex = RangeAllocator::c_InvalidOffset;
const auto tryAllocate = [&]()
{
	firstVertex = vertexArena.Allocator.Allocate(vertexUnits);
	firstIndex = m_Indices.Allocator.Allocate(indexUnits);
	if (firstVertex != RangeAllocator::c_InvalidOffset && firstIndex != RangeAllocator::c_InvalidOffset)
		return true;
	if (firstVertex != RangeAllocator::c_InvalidOffset)
		vertexArena.Allocator.Free(firstVertex);
	else
		vertexArena.Requested = std::max(vertexArena.Requested, vertexUnits);
	if (firstIndex != RangeAllocator::c_InvalidOffset)
		m_Indices.Allocator.Free(firstIndex);
	else
		m_Indices.Requested = std::max(m_Indices.Requested, indexUnits);
	return false;
};
if (!tryAllocate())
{
	// The ranges the GPU is done with first, then growth: at once while the open batch has not written into the buffers
	// (its later copies go to the new ones), else at the next BeginFrame, between batches; the mesh asks again then.
	CollectFrees();
	vertexArena.Requested = 0;
	m_Indices.Requested = 0;
	if (!tryAllocate())
	{
		if (uploadBatch != 0 && m_LastWriteBatch == uploadBatch)
			return AllocateResult { c_InvalidGeometry, true };
		std::vector<nvrhi::ResourceHandle> replaced;
		GrowRequested(replaced);
		SubmitCommandList(std::move(replaced));
		if (!tryAllocate())
		{
			// Growth failed (logged): it is tried again at the next frame.
			return AllocateResult { c_InvalidGeometry, true };
		}
	}
}

GeometryHandle handle = c_InvalidGeometry;
```

1. **Lines 157–158:** a mesh larger than the largest buffer gets no handle and no `Retry`, because it can never fit.
2. **Lines 162–177:** both ranges are taken together; when only one fits, it is given back and the arena records how much it lacked.
3. **Lines 187–188:** when the open upload batch already wrote into the buffers, the pool does not grow at once but answers `Retry`.

The toy had no such step: when no range fits, the pool takes back what the GPU has finished with, and only then grows.

### Growing

`GrowRequested` runs in `BeginFrame`, and in `Allocate` when growing at once is safe. The new capacity follows the growth rule above, cut to the limit and rounded down to a multiple of 16. The pool makes new buffers, copies what the old ones hold up to the highest allocation, then hands the old buffers to `Renderer::ReleaseDeferred`, so that the GPU finishes any frame still reading them. It bumps the buffer version, which makes binding sets rebuild.

### Freeing

`Free` may be called from any thread, because a worker thread may drop a mesh's last reference. It only records the handle. At the next call of `CollectFrees`, the pool marks the freed handles with an event query on the graphics queue and keeps them in a queue. When the GPU passes the query, the allocators take the ranges back and the handle number goes to a later mesh. Nothing waits.

### Compaction

**Compaction** is the move of used ranges toward the start of an arena so that the free space gathers into one range at the end. It runs in `BeginFrame` when more than a quarter of an arena's capacity is free space outside its largest free range, and it moves at most 8 MiB per frame.

A move cannot be one copy: the old and new ranges of a slide may overlap, and a copy inside one buffer may not. So each move goes through a scratch buffer, in two copies. Here is the part for the vertex arenas. Watch the plan from the allocator, the copies and the table update.

```cpp src="Strata/src/Strata/Renderer/GeometryPool.cpp#L452-L472" from="const uint32_t vertexBytes = GetVertexBytes(arena);" to="budget -= std::min(budget, bytes);" symbol="GeometryPool::CompactArenas"
const uint32_t vertexBytes = GetVertexBytes(arena);
const uint32_t maxUnits = static_cast<uint32_t>(std::max<uint64_t>(budget / vertexBytes, 1));
const std::vector<RangeAllocator::Move> moves = arena.Allocator.PlanCompaction(maxUnits, movable(arena.Owners));
for (const RangeAllocator::Move& move : moves)
{
	if (!EnsureScratch(static_cast<uint64_t>(move.Size) * c_AttributeStride))
	{
		ST_CORE_ERROR("GeometryPool: no scratch buffer for compaction");
		return moved;
	}
	RecordMove(commandList, arena.Positions, uint64_t(move.From) * c_PositionStride, uint64_t(move.To) * c_PositionStride, uint64_t(move.Size) * c_PositionStride);
	RecordMove(commandList, arena.Attributes, uint64_t(move.From) * c_AttributeStride, uint64_t(move.To) * c_AttributeStride, uint64_t(move.Size) * c_AttributeStride);
	if (arena.Skinned)
		RecordMove(commandList, arena.Skin, uint64_t(move.From) * c_SkinStride, uint64_t(move.To) * c_SkinStride, uint64_t(move.Size) * c_SkinStride);
	const GeometryHandle handle = arena.Owners.at(move.From);
	arena.Owners.erase(move.From);
	arena.Owners[move.To] = handle;
	m_Entries[handle - 1].Allocation.FirstVertex = move.To;
	WriteEntry(handle);
	const uint64_t bytes = static_cast<uint64_t>(move.Size) * vertexBytes;
	budget -= std::min(budget, bytes);
```

1. **Lines 454–455:** the allocator plans the moves, within the byte budget and without geometry in an upload, and the loop follows the plan.
2. **Lines 462–465:** each stream is copied through the scratch buffer: positions, attributes and, in the Skinned arena, the skin.
3. **Lines 466–470:** the owner table and the handle's entry change, so the handle finds the new place.

The index arena goes the same way with 4-byte units. The budget counts bytes: with a 48-byte vertex, 8 MiB is 174,762 vertices per frame. The two moves of the toy example are 256 vertices, 12,288 bytes, a small part of one frame's budget.

### How a draw finds its mesh

The renderer gathers the frame's draws and builds indirect draw arguments. An **indirect draw** is a draw whose arguments (counts and offsets) the card reads from a buffer, so many draws can issue in one call. The next excerpt shows how the pool's place becomes those arguments.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L2105-L2114" from="const GeometryAllocation& geometry" to="m_DrawArgumentsBuild.push_back(arguments);" symbol="SceneRenderer::BuildDrawArguments"
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
```

1. **Lines 2111–2112:** the first index and the base vertex are the pool's place plus the level's and the submesh's own offsets.
2. **Line 2113:** the start instance is where the batch begins in the draw list.

The first index is the mesh's first index in the pool plus the level of detail's own offset. The base vertex is the mesh's first vertex plus the submesh's base vertex. If the mesh sits at vertex 4,096 with a submesh base of 0, its draw reads from vertex 4,096; after compaction moves it to 128, only this number changes. The instance count says how many copies to draw, and the start instance is where the batch begins in the frame's draw list.

An **instance** is one placed copy of a mesh in the scene, with its `InstanceData`, a 64-byte record of its transform and flags; [Render scene](../draw/render-scene.md) teaches it. **Instancing** draws many copies of one mesh in one call, and the **draw list** is the frame's array of instance numbers in draw order; [Batching, buckets and indirect draws](../draw/batching.md) is the home of both. The vertex shader joins the two worlds.

```slang src="Strata/shaders/Scene/Mesh.vert.slang#L35-L60"
void st_Main()
{
	uint entry = u_DrawList[st_InstanceIndex];
	uint instanceIndex = entry & ST_DRAW_ENTRY_INSTANCE_MASK;
	InstanceData instance = u_Instances[instanceIndex];
#ifdef ST_SKINNED
	JointMatrix skin = BlendJoints(instance, a_Joints, a_Weights);
	float3 position = SkinPosition(skin, a_Position);
	float3 normal = SkinNormal(skin, a_Normal);
	float3 tangent = SkinDirection(skin, a_Tangent.xyz);
#else
	float3 position = a_Position;
	float3 normal = a_Normal;
	float3 tangent = a_Tangent.xyz;
#endif
	float3 relativePosition = TransformPositionRelative(instance, position);
	v_RelativePosition = relativePosition;
	v_Normal = normalize(TransformNormal(instance, normal));
	// A mirroring transform reverses the handedness of the tangent frame: cross(N, T) then points opposite to the
	// transformed bitangent, so its sign flips.
	float handedness = (a_Tangent.w < 0.0 ? -1.0 : 1.0) * ((instance.Flags & ST_INSTANCE_MIRRORED) != 0u ? -1.0 : 1.0);
	v_Tangent = float4(normalize(TransformDirection(instance, tangent)), handedness);
	v_TexCoord = a_TexCoord;
	v_InstanceIndex = instanceIndex;
	v_LODFade = entry >> ST_DRAW_ENTRY_INSTANCE_BITS;
	st_Position = mul(u_Frame.ViewProjection, float4(relativePosition, 1.0));
```

1. **Lines 37–39:** the draw list entry holds the instance number, which finds the instance record.
2. **Lines 55–56:** the tangent's sign flips when the instance mirrors the mesh.

The shader reads the draw list at its own instance number, which the :term[entry point]{id=entry-point-gpu} takes from `SV_VulkanInstanceID`, the value that includes the draw's start instance; the batching page gives the rule. The shader then reads the instance's transform record and places the position relative to the camera ([Camera-relative space](../draw/mirrors-camera-relative.md)). Notice the tangent: its sign flips when the instance's transform mirrors the mesh, so the shading frame stays :term[right-handed]{id=handedness}.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| A buffer per mesh | Simple renderers | No allocator and no compaction; freeing is one release | A bind per mesh, no shared indirect draws, many small allocations |
| One buffer per vertex format, never compacted | Engines with fixed asset sets | No moves, no table | A hole for each deleted mesh until the program ends |
| Interleaved vertices | Many engines and :term[file formats]{id=file-format} | One read per vertex | Passes that need only positions would read all 48 bytes |
| :term[Bindless]{id=bindless} buffer addresses, vertices fetched in the shader | Engines that fetch geometry in shaders | Meshes may live in any buffer | Fixed-function vertex fetch lost, a new shader path |

## How it is tested

The suite `GPU.Renderer.GeometryPool` in `StrataTests/src/Renderer/GPUGeometryPoolTests.cpp` runs on the shared GPU device. Its cases check that freed ranges return only after the GPU finishes earlier work, and that growth keeps what the pool holds. They check that growth works under an open upload batch, and that compaction moves geometry while the tables follow and an upload in progress stays. One renders a frame before and after a compaction and compares the pixels. The suite `Core.RangeAllocator` tests the allocator alone, without a GPU: first fit, merging, growth, and that a compaction plan leaves no gap and respects alignment.

CTest does not list them by name: it runs `Core.RangeAllocator` inside a shard `StrataTests.Core.<name>`, and every GPU suite inside `StrataTests.GPU`. To run only these two, start the test :term[executable]{id=executable} with `--test-suite=GPU.Renderer.GeometryPool,Core.RangeAllocator`. `StrataTests.GPU` carries the label `gpu`, so a machine without a graphics card skips it with `ctest -LE gpu`.

## Changing it safely

A new vertex stream needs a stride, a buffer in each arena that holds it, copies in growth and in every compaction move, and an input layout. A new table of per-mesh data follows `SetLayout` and `RecordTableUploads`: the pool writes the entries again when compaction moves a mesh.

Three rules from the engine's guide apply. Read geometry through the pool every frame, so compaction cannot strand a stored offset. Per-instance additions go to parallel buffers, so `InstanceData` stays 64 bytes. Changing what is drawn means changing both the :term[central processing unit]{id=processor} (CPU) path and the culling shader, as [GPU-driven drawing](../draw/gpu-driven.md) explains.

Before a change merges, run `GPU.Renderer.GeometryPool` and `Core.RangeAllocator`; the GPU tests end by checking that the :term[validation layer]{id=validation-layer} logged no new error.

## Summary

- Strata keeps all meshes in a few shared arenas, so that draws share state and one indirect call can draw many meshes.
- A range is rounded to 16 vertices or 64 indices. A vertex takes 48 bytes, plus 16 when skinned. Buffers start at 65,536 static vertices and double when a request does not fit.
- Compaction slides used ranges down within 8 MiB per frame through a scratch buffer, updates the owner table and the entry, and leaves the handle unchanged.
- Code that draws a mesh reads its ranges through the pool every frame and remakes binding sets when the buffer version changes.

## Check yourself

1. A script author caches `FirstVertex` of a mesh at load and draws with it every frame. What goes wrong?

   - A. Nothing, because the handle never changes.
   - B. After a compaction or growth, the cached offset may point into another mesh's vertices.
   - C. The pool refuses to draw the mesh after the first frame.

   :::answer{tests="pool-contract,shared-buffers"}
   B. The handle stays valid, but the ranges it maps to move (A confuses the two). The pool does not refuse anything (C); the draw reads the wrong memory.
   :::

2. Why does compaction copy through a scratch buffer?

   - A. The GPU cannot copy within one buffer at all.
   - B. A slide's old and new ranges overlap, and a copy inside one buffer may not overlap itself.
   - C. The scratch buffer is faster.

   :::answer{tests="compaction"}
   B. A is too strong: copies inside a buffer work when the ranges do not overlap, but a slide may. C is wrong; the scratch buffer costs a second copy.
   :::

3. A mesh has 3,000 vertices and 10,000 indices. How many bytes does it take in the Static arena?

   :::answer{tests="range-sizes"}
   Vertices: 3,000 divided by 16 is 187.5, so 188 times 16 is 3,008; 3,008 times 48 is 144,384 bytes. Indices: 10,000 divided by 64 is 156.25, so 157 times 64 is 10,048; times 4 is 40,192 bytes. Total 184,576 bytes.
   :::

4. A mesh has 70 million vertices. What does the pool do?

   :::answer{tests="range-sizes,pool-contract"}
   The attribute stream would need 70 million times 36, about 2.5 GB. That is more than the 2 GiB largest buffer, so `Allocate` returns no handle and no `Retry`, and the log shows an error. A mesh that fits a buffer but not the free space returns `Retry` instead.
   :::

## Exercises

1. **Basic.** Five meshes of 128 vertices fill the start of a Static arena of 1,024 vertices. The 2nd and 4th are deleted. What is the scattered free share, and does compaction start?

   :::answer[Worked solution]{tests="compaction"}
   The free ranges are the two holes of 128 and the tail of 1,024 minus 640, which is 384. The tail is the largest, so the scattered units are 128 plus 128, which is 256. 256 over 1,024 is 0.25. Compaction starts only above 0.25, so it does not.
   :::

2. **Medium.** In the toy, free only the 2nd, 4th and 6th of the eight blocks. Predict the moves, then run the toy to check.

   :::answer[Worked solution]{tests="compaction"}
   The blocks sit at 0, 128, 256 and so on, and the freed ones at 128, 384 and 640. The highest used block, at 896, moves into the lowest hole, 128. The next highest, at 768, moves into the hole at 384. The block at 512 has no hole below it, and neither have the others. Two moves: from 896 to 128 and from 768 to 384.
   :::

3. **Medium.** Trace it yourself: find where a mesh gets its range, and what changes after compaction.

   :::answer[Worked solution]{tests="compaction,pool-contract"}
   Set a breakpoint in `GeometryPool::Allocate` (`Strata/src/Strata/Renderer/GeometryPool.cpp`) on a source build while a model loads. The call comes from `Mesh::FinalizeOnMainThread` in `Strata/src/Strata/Renderer/Mesh.cpp`. Note the returned handle, then `Find(handle)` and its `FirstVertex`. Break again in `GeometryPool::CompactArenas` after fragmenting the arena: the owner table changes and `Find` returns new offsets for the same handle.
   :::

4. **Hard.** Write a program that prints the arena capacity after each growth for requests of 100,000, 200,000, 70,000 and 60,000,000 vertices, starting at 65,536.

   :::answer[Worked solution]{tests="range-sizes" solution="sketches/gpu-geometry-pool-growth.cpp"}
   Each growth takes the larger of double and capacity plus request, cuts it to the limit (59,652,323 vertices, from 2 GiB over 36 bytes) and rounds down to 16.

   ```cpp sketch="gpu-geometry-pool-growth.cpp"
   // The capacity a vertex arena has after each growth, for requests that did not fit.
   #include <algorithm>
   #include <cstdint>
   #include <cstdio>
   #include <initializer_list>

   constexpr uint64_t c_MaxBufferBytes = 2ull << 30;
   constexpr uint64_t c_AttributeStride = 36;
   constexpr uint64_t c_VertexGranularity = 16;

   uint64_t Grow(uint64_t capacity, uint64_t requested)
   {
   	const uint64_t wanted = std::max(capacity * 2, capacity + requested);
   	const uint64_t limit = c_MaxBufferBytes / c_AttributeStride;
   	return std::min(wanted, limit) / c_VertexGranularity * c_VertexGranularity;
   }

   int main()
   {
   	uint64_t capacity = 65536;
   	for (const uint64_t requested : { 100000ull, 200000ull, 70000ull, 60000000ull })
   	{
   		capacity = Grow(capacity, requested);
   		std::printf("request %llu: capacity %llu vertices\n", static_cast<unsigned long long>(requested), static_cast<unsigned long long>(capacity));
   	}
   }
   ```

   ```text output-of="gpu-geometry-pool-growth.cpp"
   request 100000: capacity 165536 vertices
   request 200000: capacity 365536 vertices
   request 70000: capacity 731072 vertices
   request 60000000: capacity 59652320 vertices
   ```

   1. **Line 13:** the larger of double the capacity and the capacity plus the request.
   2. **Lines 14–15:** the cut to the limit, then down to a multiple of 16.

   The last request hits the limit: the capacity stops at 59,652,320 vertices.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Renderer/GeometryPool.h` and `Strata/src/Strata/Renderer/GeometryPool.cpp`: the pool, arenas, `Allocate`, `Free`, `BeginFrame`, `CompactArenas`.
- `Strata/src/Strata/Core/RangeAllocator.h`: the range allocator, with `PlanCompaction`.
- `Strata/src/Strata/Renderer/Mesh.h` and `Strata/src/Strata/Renderer/Mesh.cpp`: the mesh asset and its upload.
- `Strata/src/Strata/Renderer/MeshFactory.h`: the primitive meshes.
- `Strata/shaders/Scene/Mesh.vert.slang`: the scene vertex shader.
- Tests: `GPU.Renderer.GeometryPool`, `Core.RangeAllocator`.

## Further reading

- Sebastian Aaltonen, OffsetAllocator, a public offset allocator with size-class free lists, on GitHub: advanced.
- The Vulkan specification, the drawing commands chapter, for the indirect draw command and its argument structure: advanced.
