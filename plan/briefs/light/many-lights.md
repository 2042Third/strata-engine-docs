# Brief: `light/many-lights`

| Field | Value |
| --- | --- |
| Title | Many lights: culling and clustered forward shading |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `light/lights`, `gpu/compute`, `draw/bounds-culling`, `draw/gpu-driven` |
| From | render-direct ch. 5; 1.4 (the CPU and GPU paths, clusters, overflow bisection, the forward loop, stats); tiled against clustered shading (forward against deferred is `gpu/frame-tour`'s) · W8r (the forward light loop) |
| Unit | `plan/allocation/light.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `light/many-lights` — Many lights: culling and clustered forward shading

**Covers.** The job: give each pixel the few lights that reach it, out of thousands in view. The problem and the
approaches (this page carries the full section; forward against deferred is `gpu/frame-tour`'s): one pass per light,
tiled forward shading with 2D tiles, clustered shading with 3D froxels (Olsson 2012, Doom 2016), with a table of their
costs. The map follows a light from a component change to the cluster lists (the record-flow diagram), with the CPU
branch beside the GPU one. The CPU path: frustum culling of each record's bounding sphere, ranking by relevance (lights
around the camera first, then the projected size r / (d - r)), a cap at `MaxLights` (4,096) with one warning, and the
upload camera-relative with the subtraction in double. The GPU path: `LightCull.comp` tests every record against the
camera-relative frustum and `LightCompact.comp` packs the visible ones in record order, with no cap. The clusters: 16 x
9 x 24 froxels with exponential depth slices, at most 256 lights per cluster, one thread per cluster testing spheres
against the cluster's box through shared memory (the froxel-grid diagram, with the buffer's stride of 257). An advanced
box shows how a full cluster on the GPU path keeps the most relevant lights: a bisection over the ordered bits of the
relevance. The forward loop: the pixel's cluster from its screen tile and log depth, then per light the range test, the
attenuation, the local shadow, the source's lobe and `LightSurface`. The statistics (`CulledLights`, `DroppedLights`,
the GPU counts). A toy assigns lights to 2D tiles on the CPU. The figure is a grid of 1,000 small point lights in the
Lighting view. Alternatives: deferred and tiled deferred, per-object light lists. How it is tested: clustered against
brute force, culling and relevance, the GPU path beyond `MaxLights`. Changing it safely: change the CPU and GPU paths
together, keep the cluster stride in sync. The exercises change the grid to 32 x 18 x 32 and measure the light passes
and `GPU.Opaque` (the light passes are timed in `GPU.Cull` on GPU-driven frames and in `GPU.Setup` on the CPU path, so
the exercise names the path it forces; the inventory's slip is the erratum of `light/brdf`), and trace one pixel's
cluster and the lights it loops over. Afterwards the reader can explain clustered shading, follow the four excerpts and
measure what the grid costs.

**Leaves out.**

- What a light record holds → `light/lights`
- Forward against deferred shading → `gpu/frame-tour`
- Frustum tests in general → `draw/bounds-culling`
- The GPU-driven path and compaction in general → `draw/gpu-driven`
- The shadow slots of shadowed lights → `light/local-shadows`
- The source's lobe → `light/area-lights`
- Measuring GPU time → `gpu/readback-timing`

**Fit.** `fits`: about 4,650 words against L (5,000). Four excerpts, two diagrams and the advanced box take the most.
Phase B reads again the section on the forward light loop (W8r): what 0.8.0's rectangle lights and the local-lights
stream change in it.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-direct:90-95` | feature | home | The CPU and GPU light paths, clustered assignment, the overflow that keeps relevance, the forward cluster loop, the statistics |
| `render-direct:353` | concept | home | Many lights: tiled against clustered shading; the mistakes (linear slices, a cap thought to drop random lights) |
| `render-direct:447` | code | home | `Strata/src/Strata/Renderer/SceneRenderer.cpp:2612-2697`: CPU light culling, ranking, the cap, the camera-relative upload in double |
| `render-direct:448` | code | home | `Strata/shaders/Include/Clusters.slang:4-52`: log depth slices, the cluster index, relevance (the inventory's 49-78 is not at the pin: the file has 54 lines) |
| `render-direct:449` | code | home | `Strata/shaders/Scene/LightClusters.comp.slang:42-101`: building the cluster lists with shared memory; 103-189, the relevance bisection, as an advanced box |
| `render-direct:450` | code | home | `Strata/shaders/Scene/Forward.frag.slang:198-279`: `ShadeLitSurface`, the sun with its mask and the cluster loop with local shadows and source lobes |
| `render-direct:490` | figure | home | Diagram: the light record flow from a component change to the cluster lists, with the CPU branch |
| `render-direct:493` | figure | home | Diagram: the froxel grid, one cluster's box, a light sphere across clusters, the buffer layout |
| `render-direct:538` | figure | home | A grid of 1,000 small point lights built by commands, in the Lighting view |
| `render-direct:658` | hands-on | home | Exercise: change the cluster grid and measure with `editor.perf` the light passes, which are timed in `GPU.Cull` on GPU-driven frames and in `GPU.Setup` on the CPU path (the exercise names the path it forces), and `GPU.Opaque` |
| `new:33` | erratum | use | The inventory's slip about `GPU.Cull`, where the exercise measures the light passes; the erratum's home is `light/brdf` |
| `new:38` | hands-on | home | Exercise (trace it yourself): for one pixel, find with a search which cluster it reads (`GetClusterIndex`, from the screen tile and the log depth) and which lights it loops over, from the forward loop back to `BuildLightClusters`, which dispatches `LightClusters.comp`. Evidence: `Strata/shaders/Include/Clusters.slang:13-24`; `Strata/shaders/Scene/Forward.frag.slang:252-256`; `Strata/src/Strata/Renderer/SceneRenderer.cpp:2745`, `:3375` |
| `render-direct:711-714` | term | home | Relevance, clustered shading and froxel, exponential depth slices, light culling |
| `render-direct:198` | feature | use | `MaxLights`, `LightClusterGrid` and `MaxLightsPerCluster`, the switches this page tunes; the list's home is `reference/renderer` |
| `render-direct:822` | open | use | The documents give no reason for forward over deferred: the page states the trade-off and attributes no motive |
| `render-scene:731` | open | home | The GPU culling of light records (`LightCull.comp`, `LightCompact.comp`) is taught here, though its code lives with the render scene |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Light records and `LightData` | `light/lights` | must |
| Compute shaders, group-shared memory and barriers | `gpu/compute` | must |
| Frustum tests of spheres | `draw/bounds-culling` | must |
| The GPU-driven path and compaction | `draw/gpu-driven` | must |
| Forward against deferred shading | `gpu/frame-tour` | must |
| Logarithms | `basics/numbers` | must |
| The bits of a floating-point number | `basics/numbers` | must |
| Sorting | `basics/trees-graphs` | helps |
| GPU stages and their timing | `gpu/readback-timing` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `clustered-shading` | Clustered shading | - |
| `exponential-depth-slices` | Exponential depth slices | - |
| `froxel` | froxel | - |
| `light-culling` | Light culling | - |
| `relevance` | Relevance | - |
