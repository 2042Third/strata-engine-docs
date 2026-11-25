# Brief: `draw/batching`

| Field | Value |
| --- | --- |
| Title | Batching and instancing |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `draw/asset-requests`, `gpu/geometry-pool`, `gpu/binding` |
| From | render-scene; sort keys and radix sort; the transparent pass's back-to-front order (blending is `light/clearcoat-transmission`'s) |
| Unit | `plan/allocation/draw.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `draw/batching` — Batching and instancing

**Covers.** The job: turn the visible proxies into as few draws as the pipeline states allow, the same way on every run
and with any number of threads. The problem section is one paragraph that links `draw/entities-to-draws`. The ideas in
order. Instancing and per-instance data: one draw for many copies, a structured buffer of persistent 64-byte instances,
a per-frame draw list of indices that the vertex shader reads as `u_DrawList[SV_VulkanInstanceID]` (which includes the
base instance, unlike `SV_InstanceID`), and materials read by slot from a buffer. Material-free instancing: the
material is not in the batch key, so 1,000 cubes with 1,000 colours draw in one opaque draw; `BatchAcrossMaterials` off
splits them, for comparison. Sort keys and radix sort: the draw's state packed into a 64-bit `SceneDrawKey` (cascade,
alpha mask, mirrored, double-sided, skinned, mesh slot, submesh, level of detail, and the material only when batching
across materials is off), why churning fields stay out of the high bits, and a stable LSD radix sort that skips bytes
equal in every key, with `SortIndices`, its form for lists of 32-bit values, which sorts the slots `ResolveAssets`
walks. Indirect drawing: draw arguments in a GPU buffer, `drawIndexedIndirect` and `multiDrawIndirect`
(the GPU-written count is `draw/gpu-driven`'s). The toy sorts and batches a list of (mesh, material) pairs in 50 lines.

The real code in the order data flows: extraction in chunks of 2,048 proxies on the job system, merged in chunk order;
the heart of `GatherDraws` (the residency check, size culling, the level of detail with its fade's double entry, the
transparent split, the sort item), with one sentence on the residency check: it asks the render scene's GPU copy whether
a proxy's upload arrived (`IsResident`), the vertex shader reads the instances from that copy's buffer, and
`draw/render-scene-gpu` teaches the copy; `SceneDrawKey` with the `static_assert` that its fields tile 64 bits;
`RadixSort`; `BuildBatches`, where runs of equal keys become batches and the draw list gets one entry per instance; the
draw-list entry (instance in 27 bits, the fade code above); transparent submeshes drawn one at a time, back to front,
glass first; uploads of only the changed range of a list; `BuildDrawArguments` at each mesh's place in the geometry
pool, and `DrawBuckets`, where consecutive batches of one `PipelineKey` and vertex arena share one `setGraphicsState`
and one indirect call where the device has `multiDrawIndirect` and `drawIndirectFirstInstance` (the glossary entry of
the three device features and limits is this page's), split at `maxDrawIndirectCount`. Beside the `SceneDrawKey`
excerpt, the key's widths as limits: submeshes past the 65,536th and levels past the 32nd are not drawn and reported,
material slots past 65,536 share keys and merge batches, which stays correct. How it is tested: the opaque draw counts
of `GPURenderSceneTests` and `RadixSortTests`, with the exercises that move the material into the key and build keys
that need one, three and eight passes, and a trace of one cube from its sort item to the call that draws it. The
measured proof of material-free instancing: 10,000 materials draw in one opaque call and 10,000 distinct meshes in 8
draw commands, values the page reads through generated keys. The page runs on 1,000 cubes with 1,000 materials. At the
end the reader can decode a sort key, predict the draws a scene makes, and say why the material is not in the key.

**Leaves out.**

- Pipeline state objects and the `PipelineKey` cache → `gpu/binding`
- The geometry pool, its arenas and compaction → `gpu/geometry-pool`
- Blending and premultiplied alpha → `light/clearcoat-transmission`
- How the level of detail is chosen and faded → `draw/lod`
- Buckets and indirect draws that the GPU fills → `draw/gpu-driven`
- The shadow passes' draws → `light/sun-shadows-1`

**Fit.** `fits`: about 5,650 words against L (5,000). Six excerpts and three concepts take the most, then three
exercises; the measured counts and the key's widths as limits add about 230 words, and `SortIndices` takes one sentence.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-scene:272` | concept | home | Instancing and per-instance data; the draw list; `SV_VulkanInstanceID` against `SV_InstanceID` |
| `render-scene:267` | concept | home | Sorting draws by an integer key; radix sort; what belongs in the high bits |
| `render-scene:282` | concept | home | Indirect drawing: arguments in a GPU buffer, `drawIndexedIndirect`, `multiDrawIndirect` |
| `render-scene:79-88` | feature | home | Parallel extraction, the sort key, radix sort, material-free instancing, batches and the draw list, the draw-list entry, transparent draws, changed-range uploads, indirect arguments per batch, buckets of pipeline state |
| `render-scene:352` | code | home | `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp:961-1047`: the heart of `GatherDraws` |
| `render-scene:353` | code | home | `Strata/src/Strata/Renderer/SceneDrawKey.h:9-43`: packing the key; the fields tile 64 bits |
| `render-scene:354` | code | home | `Strata/src/Strata/Core/RadixSort.cpp:14-67`: stable LSD radix sort that skips equal bytes |
| `render-scene:355` | code | home | `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp:845-869`: `BuildBatches`, runs of equal keys |
| `render-scene:356` | code | home | `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp:1271-1302`: uploading only the changed range of a list |
| `render-scene:357` | code | home | `Strata/src/Strata/Renderer/SceneRenderer.cpp:2042-2134`: indirect arguments at geometry-pool offsets; `DrawBuckets` |
| `render-scene:394` | figure | home | The 64-bit `SceneDrawKey` with its fields tiling the word |
| `render-scene:440` | figure | home | 1,000 cubes in 1,000 colours: one opaque draw; the same image with `BatchAcrossMaterials` off |
| `render-scene:530` | hands-on | home | Move the material into the key and compare the opaque draws on 1,000 materials |
| `render-scene:532` | hands-on | home | Keys that need one, three and eight passes; checking stability |
| `new:14` | hands-on | home | Exercise ("trace it yourself"): one cube of the 1,000 followed with a debugger from its sort item in `GatherDraws` through `RadixSort` and `BuildBatches` to its draw-list entry (`MakeDrawEntry`) and to the `DrawBuckets` call that draws its batch; the solution names each function and the entry's value. Evidence: `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp:845-869`, `:1036-1046`; `Strata/src/Strata/Renderer/SceneRenderer.cpp:2072-2134` |
| `new:23` | feature | home | The measured proof of the part's claims for batching: `PerfGPU.Renderer.Render10kMaterials.OpaqueDrawCalls` (10,000 materials in one opaque call) and `PerfGPU.Renderer.Render10kUniqueMeshes.DrawCommands` (10,000 distinct meshes in 8 draw commands), read through the keys `perf.PerfGPU.Renderer.Render10kMaterials.OpaqueDrawCalls.Measured` and `perf.PerfGPU.Renderer.Render10kUniqueMeshes.DrawCommands.Measured`; the method is `engineering/perf-lab`'s and the full table `reference/performance`'s. Evidence: `StrataTests/Perf/Budgets.json:155`, `:192`; `StrataTests/src/Perf/RendererPerfTests.cpp:325`, `:405-411`, `:499`, `:513-521` |
| `new:28` | rule | home | The sort key's widths are limits: a submesh past the 65,536th or a level past the 32nd is not drawn, and the renderer reports how many instances it skipped; material slots past 65,536 share keys and merge batches, which stays correct; mesh slots are bounded by `Scene::c_MaxEntities`. Evidence: `Strata/src/Strata/Renderer/SceneDrawKey.h:24-29`; `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp:996-1000`, `:1075` |
| `render-scene:575-578` | term | home | Draw list; draw entry; batch; bucket |
| `render-scene:580-583` | term | home | Sort key; radix sort; material-free instancing; indirect draw |
| `render-scene:585` | term | home | `multiDrawIndirect`, `drawIndirectFirstInstance`, `maxDrawIndirectCount`: the CPU path meets all three first (one indirect call per bucket where the device has the first two, split at the third: `Strata/src/Strata/Renderer/SceneRenderer.h:157-163`); `draw/gpu-driven` links it |
| `render-scene:586-587` | term | home | Base instance; `SV_VulkanInstanceID` |
| `render-core:752` | term | home | Draw list (the frame's array of instance indices the vertex shader reads per instance): one glossary entry with `render-scene:575`, feature and term homed here (R31, D33), passed by `gpu` |
| `render-core:753` | term | home | Indirect draw (a draw whose arguments the GPU reads from a buffer): one glossary entry with `render-scene:583`, passed by `gpu` |
| `render-core:586` | rule | home | `SV_VulkanInstanceID`, not `SV_InstanceID`: the draw list is indexed including the base instance; the rule beside the term `render-scene:587`, passed by `gpu` |
| `foundation:161` | feature | home | `RadixSort` and `SortIndices` (`Strata/src/Strata/Core/RadixSort.h`), the foundation inventory's view of `render-scene:81`; `SortIndices` sorts the used mesh and material slots in `ResolveAssets` |
| `foundation:644` | term | home | Radix sort: one glossary entry with `render-scene:581` |
| `render-scene:341` | code | use | The draw-list entry and `MakeDrawEntry`, read again from `draw/render-scene` |
| `render-scene:60` | feature | use | Size culling inside `GatherDraws` |
| `render-scene:89` | feature | link | The pipeline cache by key, at `gpu/binding` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Pipelines, the `PipelineKey` cache, structured buffers and bindless reads | `gpu/binding` | must |
| The geometry pool and its vertex arenas | `gpu/geometry-pool` | must |
| Bits, shifts and masks; packing keys | `basics/numbers` | must |
| Instances and their slots in the render scene | `draw/render-scene` | must |
| Residency of proxies and of meshes at draw time | `draw/asset-requests` | must |
| Deterministic parallel work in fixed chunks | `core/jobs` | must |
| Uploading buffers through staging | `gpu/upload-queue` | must |
| Sorting and the cost of operations | `basics/trees-graphs` | helps |
| Transparency, blending and glass | `light/clearcoat-transmission` | helps |
| Levels of detail and their fade codes | `draw/lod` | helps |
| The instances live in the render scene's GPU copy; a new proxy draws once its upload arrived | `draw/render-scene-gpu` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `sv-vulkaninstanceid` | `SV_VulkanInstanceID` | - |
| `base-instance` | Base instance | - |
| `batch-draw` | Batch (draw) | SceneDrawBatch |
| `bucket` | Bucket | - |
| `draw-entry` | Draw entry | - |
| `draw-list` | Draw list | draw command, draw data |
| `first-instance` | first instance | - |
| `indirect-draw` | Indirect draw | - |
| `material-free-instancing` | Material-free instancing | - |
| `radix-sort-lsd` | Radix sort (LSD) | Radix sort |
| `sort-key` | Sort key | SceneDrawKey |
