# Brief: `gpu/geometry-pool`

| Field | Value |
| --- | --- |
| Title | Meshes on the GPU and the geometry pool |
| Kind | I |
| Size | M |
| Tracks | E |
| Needs | `gpu/upload-queue`, `gpu/binding` |
| From | render-core; home of the geometry pool (`draw/batching` links) |
| Unit | `plan/allocation/gpu.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `gpu/geometry-pool` — Meshes on the GPU and the geometry pool

**Covers.** The job: hold every mesh's vertices and indices in a few shared buffers, so that draws of different meshes
share their state, and let the pool move geometry without the meshes knowing. The problem (a buffer per mesh means a
bind and often a draw per mesh) and the approaches (interleaved or separate streams, a buffer per mesh, one large
buffer per vertex format, pools with suballocation). The map is the pool's memory figure: the Static and Skinned arenas,
the index arena, handles, the allocation table, free ranges and a compaction moving a mesh. A mesh on the GPU: 12-byte
positions in their own stream (depth-only passes fetch nothing else), 36-byte attributes (normal, tangent with its
sign, UV), a 16-byte skin stream, submeshes with levels of detail, counter-clockwise faces, uploads through the queue
into the pool, and the positions and indices the CPU keeps for physics; `MeshFactory`'s primitives as built-in assets.
The contract: a stable `GeometryHandle`; ranges that move, so geometry is read through the pool every frame and binding
sets are made again when a buffer version changes; frees that wait for the GPU. The limits: each stream's buffer is at
most 2 GiB (about 59.6 million vertices per vertex arena, 536 million indices in all), ranges are rounded to 16
vertices and 64 indices, the pool starts at 65,536 static vertices, 4,096 skinned vertices and 262,144 indices and
doubles, a mesh that does not fit waits for the next frame's growth, and a mesh larger than one buffer fails with an
error.

The toy is a range allocator with free lists and coalescing in about 60 lines. The real code is the pool's design
comment, then compaction: moves planned within 8 MiB a frame when more than a quarter of an arena's free space is
scattered, copies on the GPU through a scratch buffer, the owner table updated, growth by copying into larger buffers.
Last, how a draw finds its mesh and its instance at the foundation level: indirect draw arguments at the mesh's place in
the pool, a 64-byte `InstanceData` per instance, the frame's draw list read with `SV_VulkanInstanceID`, all shown in the
scene vertex shader; instancing, the instance, the draw list and the indirect draw are each said in one sentence and
linked to their homes on `draw/batching` and `draw/render-scene`. Alternatives, tests (`GPU.Renderer.GeometryPool`),
changing safely; the exercise fragments the Static arena, compacts it and checks that a rendered frame is the same, and
a second traces one mesh to its range and back after a compaction.

**Leaves out.**

- Instancing, the draw list, indirect draws, the `SV_VulkanInstanceID` rule, sort keys, batches and buckets → `draw/batching`
- The instance and `InstanceData` as the render scene holds them → `draw/render-scene`
- The culling tables in the pool and GPU-driven drawing → `draw/gpu-driven`
- Levels of detail and how one is chosen → `draw/lod`
- Camera-relative positions in the vertex shader → `draw/mirrors-camera-relative`
- Skinning in the vertex shader → `draw/skinned`
- The glTF importer and cooked meshes → `assets/models-gltf`
- Mesh colliders that read the CPU's triangles → `physics/building-bodies`

**Fit.** `over`: about 5,050 words against M (3,000). Two concepts, three excerpts, the toy, the pool's limits and two
exercises pass M's top; the page takes L by S2 (5,050 is inside L's range).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-core:397` | concept | home | Vertex data layout: separate streams and shared geometry; the mistake of caching a mesh's offsets across frames |
| `render-core:402` | concept | home | Instancing, draw lists and indirect draws at the foundation level: the shape `gpu/frame-tour` needs; instancing is used here first on track E and defined in one sentence with a link to `draw/batching`, its home (ui-q5); the details are `draw/batching`'s |
| `render-core:110`, `render-core:111`, `render-core:113` | feature | home | The `Mesh` asset's GPU side; `GeometryPool`; `MeshFactory` |
| `new:13` | code | home | `Strata/src/Strata/Renderer/GeometryPool.h:62-72`: the pool's design: arenas, stable handles, frees after the GPU, growth and compaction in `BeginFrame` |
| `new:14` | code | home | `Strata/src/Strata/Renderer/GeometryPool.cpp:435-503`: `CompactArenas`: planned moves, GPU copies through the scratch buffer, the owners updated |
| `render-core:463` | code | home | `Strata/shaders/Scene/Mesh.vert.slang:35-60`, with its entry wrapper at lines 85-137: draw list, instance, position, clip; the tangent's handedness named |
| `render-core:500` | figure | home | The geometry pool's memory layout |
| `render-core:574` | rule | home | Read mesh geometry through the pool every frame |
| `render-core:586` | rule | link | `SV_VulkanInstanceID`, not `SV_InstanceID`, named where the vertex shader reads the draw list; the rule's home is `draw/batching` (R31 D33) |
| `new:43` | feature | home | The pool's limits and failure path: each stream's buffer at most 2 GiB (about 59.6 million vertices per vertex arena of 36-byte attributes, 536 million indices in all); ranges rounded to 16 vertices and 64 indices; start sizes of 65,536 static vertices, 4,096 skinned vertices and 262,144 indices, doubled on growth; a mesh that does not fit returns `Retry` and uploads after the next frame's growth; a mesh larger than one buffer fails with an error (about 120 words). Evidence: `Strata/src/Strata/Renderer/GeometryPool.h:77-94, 97-102`; `Strata/src/Strata/Renderer/GeometryPool.cpp:154-158, 546-572`; `Strata/src/Strata/Renderer/Mesh.cpp:351-358` |
| `render-core:653` | hands-on | home | Fragment, compact, compare a frame |
| `new:44` | hands-on | home | Exercise ("trace it yourself"): one mesh to its range: a breakpoint in `GeometryPool::Allocate` when a model loads on the source build, its handle and offsets read, then the same handle's new offsets found after `CompactArenas` moved it. Evidence: `Strata/src/Strata/Renderer/Mesh.cpp:351`; `Strata/src/Strata/Renderer/GeometryPool.cpp:151, 435-503` |
| `render-core:748`, `render-core:749`, `render-core:750` | term | home | Geometry pool and arena; range allocator; compaction |
| `render-core:751`, `render-core:752`, `render-core:753` | term | link | Instance and `InstanceData`; draw list; indirect draw: each said in one sentence, linked to its home (`draw/render-scene` for the instance, `draw/batching` for the other two; R31 D33) |
| `foundation:162` | feature | home | `RangeAllocator`: size-class free lists, coalescing and bounded compaction planning; the pool is its only user at the pin, and the toy is a small one |
| `foundation:645` | term | home | Offset (range) allocator; one entry with `render-core:749` |
| `render-scene:90` | feature | home | The geometry pool as the drawing part lists it, with the same subject as `render-core:111` |
| `render-scene:278` | concept | home | Shared geometry buffers, the same idea as `render-core:397` |
| `render-scene:403` | figure | home | The pool's memory map, drawn once with `render-core:500` |
| `render-scene:482` | rule | home | Read mesh geometry through the pool every frame, the same rule as `render-core:574` |
| `render-scene:574` | term | home | Submesh, met first with meshes on the GPU |
| `render-scene:588-591` | term | home | Geometry pool; arena (Static, Skinned); `GeometryHandle`; compaction |
| `render-scene:91` | feature | link | The culling tables in the pool (`Include/GeometryTables.slang`, as culling and the voxelizer read them), taught with GPU-driven drawing |
| `render-scene:370` | code | link | The same vertex shader from another angle: `draw/mirrors-camera-relative` quotes its lines 50-56 and 76-81 (the relative position, the normal, the mirrored handedness, the previous position), and this page's excerpt `render-core:463` holds lines 35-60 (duplicates.md, "Scene vertex shader excerpt") |
| `render-core:142` | feature | link | Camera-relative positions in the vertex shader |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Staging, the upload queue and tickets | `gpu/upload-queue` | must |
| Pipelines and input layouts | `gpu/binding` | must |
| Deferred release and event queries | `gpu/resources-lifetimes` | must |
| Data structures: arrays, free lists, hash maps | `basics/data-structures` | must |
| Levels of detail | `draw/lod` | helps |
| Camera-relative positions | `draw/mirrors-camera-relative` | helps |
| Batching and instancing | `draw/batching` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `geometryhandle` | `GeometryHandle` | - |
| `arena` | arena | - |
| `compaction-defragmentation` | Compaction (defragmentation) | - |
| `geometry-pool` | Geometry pool | - |
| `range-allocator` | Range allocator | Offset allocator |
| `submesh` | Submesh | - |
