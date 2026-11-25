# Brief: `draw/gpu-driven`

| Field | Value |
| --- | --- |
| Title | GPU-driven culling and indirect drawing |
| Kind | I |
| Size | XL |
| Tracks | E |
| Needs | `draw/lod`, `draw/mirrors-camera-relative`, `draw/render-scene-gpu`, `gpu/compute`, `gpu/readback-timing` |
| From | render-scene; thumbnails force the CPU path; local shadow views' culling is `light/local-shadows`'; its last section is the visibility feedback, which the counting pass writes (merged from `draw/visibility-feedback`) |
| Unit | `plan/allocation/draw.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `draw/gpu-driven` — GPU-driven culling and indirect drawing

**Covers.** The job: cull the render scene and build the frame's draw commands on the GPU, so that the CPU's cost no
longer follows the number of proxies, drawing exactly the pixels the CPU path draws. The problem and how engines solve
it: CPU culling of a million proxies costs milliseconds; keep the scene on the GPU, cull in compute and compact the
survivors into indirect arguments (Haar and Aaltonen, SIGGRAPH 2015; Wihlidal, GDC 2016). Why Strata counts first and
writes second instead of appending with one atomic: deterministic ranges per record and draws per bucket with known
slots. The map: the passes and their buffers as a data-flow diagram. The contract: the GPU path is chosen per renderer
(`GPUDriven` Auto on devices with `drawIndirectFirstInstance`, else Off, and a fallback when shaders or resources cannot
be set up), the switches are code only, thumbnails force the CPU path, and every culling rule has a CPU twin that must
change with it. The toy is a two-pass count-then-write over an array in a compute shader, building on `gpu/compute`'s
prefix sum.

The real code, in the order of a frame: the culling tables in the geometry pool (a `GeometryEntry` per handle, a
`GeometrySubmesh` per submesh, a `GeometryLOD` draw record per level); the culling constants; `Cull.comp`'s `CullProxy`,
one thread per proxy (active and indexed flags, the camera-relative frustum test, size culling, the level of detail per
instance and material, the emit into counts per bucket and LOD record); `Emit` and `EmitViewInstances`, which count and
write through one function; `CullBuild.comp`'s prefix allocation by atomics (a range of the draw list and an indirect
slot per record, overflow, the 64-bit triangle count by carry); `RunGPUCulling`'s sequence count, build, feedback,
write, and why dispatches through one binding set need explicit UAV barriers. Buckets: pipeline state times vertex
arena, with the bit layout of a bucket index and only the buckets a frame can have given dense indices. One sentence
points forward to `light/sun-shadows-1`, which teaches how the sun's casters are culled and drawn into the cascades on
both paths. The indirect modes chosen from the device: `drawIndexedIndirectCount` with a GPU-written count, `NoCount`
with bounded zeroed slots, and `PerDraw`, split at `maxDrawIndirectCount` (MoltenVK runs `NoCount`), shown as a decision
tree. What bounds a bucket's draw slots without a GPU-written count (every MoltenVK device, so every Mac): the LOD
records of the meshes the CPU's marks found in view, and on feedback frames the feedback's count plus a quarter and 16;
draws beyond the bound are counted as overflow and not drawn in that frame, and the CPU walks the view once; with a
GPU-written count the GPU's number is exact. The 128-byte counters read back two to three frames late. The empty render
scene that records no culling (and the rule for resources that matter without proxies). Transparent materials left to
the CPU's sorted pass. Shading that must not depend on draw order, because the GPU places instances in scheduling order
(the derivative rule is `light/brdf`'s). What Strata does not do here: mesh shaders and meshlets. How it is tested:
`GPU.SceneRenderer.GPUDriven`, whose `CompareScenes` helper draws the same scenes on both paths and compares them;
`GPU.SceneRenderer.GPUDrivenFallback`, a renderer whose GPU path cannot be set up drawing through the CPU path and
keeping none of the path's resources; and `GPU.SceneRenderer.IndirectFallback`, draws without a GPU-written count, one
draw per slot, local shadow views a batch at a time and buckets split over several calls, each drawing what the CPU path
draws. CI's hosted runners have no GPU and leave the `gpu` suites out. The cost, measured: the CPU's frame for 100,000
and for 1,000,000 cubes against the GPU's, read through generated keys, so the reader sees the CPU's cost stop following
the number of proxies. The exercises add a per-instance value the right way, port a CPU culling rule to the GPU, and
trace one proxy from `CullProxy` to the indirect call that draws it. The page runs on `CompareScenes`' scenes.

The page's last section is the visibility feedback, which the counting pass writes. Its job: let the GPU, which knows
what it culled and drew, tell the CPU which meshes and materials to request and how large they looked, without the CPU
walking the proxies. The section first teaches feedback loops from the GPU to the CPU in general (texture streaming
feedback, virtual texturing) and their price: latency. The real code: the counting pass marks each touched mesh and
material slot with use bits (view, high, prefetch, shadow), the largest pixel size and the UV pixels, with a read before
the atomic so that most threads skip it, and appends first touches to a list that `CullFeedback.comp` packs; the GPU's
port of the texture streaming measure (`Include/TextureStreaming.slang`). The CPU applies the newest feedback it has
(`ApplyFeedback`) and still walks transparent users, skinned proxies and meshes of unknown bounds. It walks instead in
the first frames, after a camera cut, when the tables changed since the feedback's frame, when the feedback is older
than 8 frames, and once after an overflow (`UsesFeedback`); the test "Without a GPU-written draw count, draws beyond the
slots the feedback foresaw run the CPU's walk once" shows the last of these. The feedback reaches the texture streamer
by no road of its own: the sizes `ApplyFeedback` writes into the material slots are published with the frame's visible
textures, and `ReportView` receives them as it does on the CPU path. A timeline shows a frame writing feedback, its
readback two or three frames later, the requests, the loads and the tables catching up. The section runs on its
exercise: add a mesh in a GPU test and count the frames until it is requested. At the end the reader can follow a proxy
from `Cull.comp` to an indirect draw, name what must change on both paths when a rule changes, say how late a request
driven by feedback comes, and say when the CPU walks instead.

**Leaves out.**

- Compute shaders, thread groups, atomics, prefix sums and UAV barriers → `gpu/compute`
- Culling the local lights' shadow views → `light/local-shadows`
- Culling lights into clusters → `light/many-lights`
- Culling the sun's cascades and their occlusion → `light/sun-shadows-1`
- The second phase against the depth pyramid → `draw/occlusion`
- Skinned buckets and posed bounds → `draw/skinned`
- The derivative rule and shading order in the forward shader → `light/brdf`
- The requests and priorities the feedback replaces → `draw/asset-requests`
- How the published sizes choose mip levels → `draw/mip-streaming`
- Readback without stalling → `gpu/readback-timing`

**Fit.** `fits`: about 6,750 words against XL (8,000). Five excerpts, three diagrams and the GPU path's features take the
most; the visibility feedback, the last section, adds a concept, a two-part excerpt, four features, a timeline and an
exercise in about 1,350 words, as the page has one set of fixed parts.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-scene:287` | concept | home | The GPU scene and GPU-driven culling; count, build and write against one atomic append |
| `render-scene:91` | feature | home | The culling tables in the geometry pool: entries, submeshes, LOD records |
| `render-scene:123-132` | feature | home | The mode switch, `Cull.comp`, count, build and write, buckets, indirect modes with what bounds a bucket's draw slots without a GPU-written count (the CPU's marks, the feedback's count plus a quarter and 16, overflow: `Strata/src/Strata/Renderer/SceneRendererGPUDriven.cpp:79`, `:514-566`, `:1199-1203`), culling constants, GPU counters, the empty render scene, transparent left to the CPU; of order-independent shading only the cause, the GPU appending instances in scheduling order (`Strata/shaders/Scene/Cull.comp.slang:12-15`), with a link to `light/brdf`, which teaches the rule and its reason |
| `render-scene:362` | code | home | `Strata/shaders/Scene/Cull.comp.slang:448-511`: `CullProxy`, from flags to emit |
| `render-scene:363` | code | home | `Strata/shaders/Scene/Cull.comp.slang:195-232`: `EmitViewInstances`, with `Emit` at 58-80 counting and writing through one function |
| `render-scene:364` | code | home | `Strata/shaders/Scene/CullBuild.comp.slang:49-109`: prefix allocation by atomics, overflow, the 64-bit triangle count |
| `render-scene:365` | code | home | `Strata/src/Strata/Renderer/SceneRendererGPUDriven.cpp:923-1026`: count, build, feedback, write; the explicit UAV barriers |
| `render-scene:373` | code | home | `Strata/src/Strata/Renderer/GPUSceneData.h:113-151`: the bit layout of bucket indices, with `GetGPUIndirectPath` at `SceneRendererGPUDriven.cpp:177-194`, and `UsesFeedback` at `SceneRendererGPUDriven.cpp:1619-1628`: every reason the CPU walks instead |
| `render-scene:395` | figure | home | The bucket index's bits: view buckets, shadow buckets per cascade, local view buckets, the dense table |
| `render-scene:405` | figure | home | The GPU-driven passes with their buffers, from the proxies to indirect draws per bucket |
| `render-scene:421` | figure | home | The decision tree from `GPUDriven` and device features to the indirect mode |
| `render-scene:474` | rule | home | Change the CPU rule and the GPU rule together |
| `render-scene:509` | rule | home | A GPU-culling resource that matters without proxies is cleared in the empty-scene branch too |
| `render-scene:513` | rule | home | Explicit UAV barriers between culling dispatches through one binding set |
| `render-scene:534` | hands-on | home | Add a per-instance value as a parallel buffer, log its changes and show both paths agree |
| `render-scene:536` | hands-on | home | Port a CPU culling rule (a maximum draw distance) to `Cull.comp` and extend the comparison test |
| `new:17` | hands-on | home | Exercise ("trace it yourself"): one proxy of `CompareScenes`' scenes followed from `CullProxy` through `Emit`'s count, the slot and draw-list range `CullBuild.comp` gives its record, and the write pass, to the indirect call of `DrawGPUBucket` that draws it, with a GPU debugger's capture or a search of the buffers' names; the solution names each pass, buffer and function. Evidence: `Strata/shaders/Scene/Cull.comp.slang:58-80`, `:448-511`; `Strata/shaders/Scene/CullBuild.comp.slang:49-109`; `Strata/src/Strata/Renderer/SceneRendererGPUDriven.cpp:1195-1226` |
| `new:24` | feature | home | The GPU path's cost, measured: the CPU's frame for 100,000 and 1,000,000 cubes against the GPU's, read through `perf.PerfGPU.Renderer.Render100kCubes.Measured`, `perf.PerfGPU.Renderer.Render1MCubes.Measured`, `perf.PerfGPU.Renderer.Render100kCubesGPU.Measured` and `perf.PerfGPU.Renderer.Render1MCubesGPU.Measured` (the measured renderer leaves `GPUDriven` at Auto); the method is `engineering/perf-lab`'s and the full table `reference/performance`'s. Evidence: `StrataTests/Perf/Budgets.json:152`, `:173-175`; `StrataTests/src/Perf/RendererPerfTests.cpp:325-388`; `StrataTests/src/Perf/RendererPerfUtils.h:37-42` |
| `render-scene:584` | term | home | `drawIndexedIndirectCount` |
| `render-scene:585` | term | link | `multiDrawIndirect`, `drawIndirectFirstInstance`, `maxDrawIndirectCount`, at `draw/batching`, where the CPU path meets them first |
| `render-scene:592` | term | home | LOD record (`GeometryLOD`) |
| `render-scene:615` | term | home | GPU-driven rendering |
| `render-scene:624` | term | home | Counting pass and write pass |
| `render-scene:626` | term | home | Overflow |
| `render-scene:715` | open | home | How it is tested: the writer reads `CompareScenes` (`GPUSceneRendererGPUDrivenTests.cpp:610`) for the scenes both paths draw |
| `render-scene:722` | open | home | The switches are code only (`SceneRendererSpecification`); thumbnails force the CPU path (`SceneRenderer.cpp:248-251`); comparison figures need a harness |
| `render-scene:725` | open | home | The GPU-driven path's device reach as the 0.4.0 and 0.5.0 release notes state it (`Docs/Releases/0.4.0.md:264-269`); CI's hosted runners have no GPU and skip the `gpu` label (`.github/workflows/ci.yml:195-215`) |
| `new:4` | not-done | home | No mesh shaders or meshlets: culling is per proxy and per instance, drawing through the classic pipeline. Evidence: `git grep -niE "meshlet\|mesh ?shader\|EXT_mesh_shader\|taskShader" 822a7a46 -- Strata/src Strata/shaders` finds nothing |
| `render-scene:306` | concept | home | Feedback loops from the GPU to the CPU and their latency |
| `render-scene:148-151` | feature | home | The GPU marks requests, the CPU applies the newest feedback, when the CPU walks instead (with the test of the walk after an overflow, `StrataTests/src/Renderer/GPUSceneFeedbackTests.cpp:329`), the texture streaming port |
| `render-scene:368` | code | home | `Strata/shaders/Scene/Cull.comp.slang:84-100`: a read before the atomic, with `ApplyFeedback` at `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp:344-386` |
| `render-scene:415` | figure | home | The feedback loop as a timeline: frame N, the readback at N+2 or N+3, requests, loads, tables |
| `render-scene:543` | hands-on | home | Count the frames until a new mesh is requested by feedback |
| `render-scene:628` | term | home | Visibility feedback |
| `assets:802` | open | home | Settled at the pin: the feedback changes the streamer's inputs only through `ReportView`. `ApplyFeedback` writes the GPU's pixel sizes and UV pixels into the material slots (`Strata/src/Strata/Renderer/SceneRendererExtraction.cpp:344-386`), `GatherDraws` publishes them as the visible textures (lines 1111-1123), and `ReportTextureUse`, the only caller of `ReportView`, hands them over (`Strata/src/Strata/Renderer/SceneRenderer.cpp:2835-2853`) |
| `render-scene:60` | feature | use | Size culling on both paths |
| `render-scene:99-100` | feature | use | The halving and error rules, which `Cull.comp` repeats |
| `render-scene:172` | feature | use | The camera-relative frustum test |
| `render-scene:110` | feature | use | The GPU copy that `Cull.comp` reads |
| `render-scene:68` | feature | use | The use bits and priorities the feedback carries |
| `render-scene:505` | rule | use | Tests of requests wait for feedback or turn it off |
| `render-scene:477` | rule | link | Shading must not depend on draw order, at `light/brdf` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Compute shaders, thread groups, atomics, prefix sums and UAV barriers | `gpu/compute` | must |
| Readback of GPU data a few frames late | `gpu/readback-timing` | must |
| Device features and limits, and the graphics device's capabilities | `gpu/vulkan-nvrhi` | must |
| The render scene's GPU copy and its records | `draw/render-scene-gpu` | must |
| The CPU path's culling rules and the screen fraction | `draw/bounds-culling` | must |
| Batches, buckets, the draw list and indirect arguments | `draw/batching` | must |
| The level-of-detail rules | `draw/lod` | must |
| Mirrored instances and camera-relative positions | `draw/mirrors-camera-relative` | must |
| Writing a GPU test with the shared `GPUContext` | `gpu/first-triangle` | must |
| Requests by visibility and their priorities | `draw/asset-requests` | must |
| The derivative rule and shading order | `light/brdf` | helps |
| Continuous integration and its machines | `engineering/ci` | helps |
| Texel density and the wanted level | `draw/mip-streaming` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `drawindexedindirectcount` | `drawIndexedIndirectCount` | - |
| `counting-pass` | Counting pass | write pass |
| `gpu-driven-rendering` | GPU-driven rendering | - |
| `lod-record` | LOD record | GeometryLOD |
| `visibility-feedback` | Visibility feedback | - |
