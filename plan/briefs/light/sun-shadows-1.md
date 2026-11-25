# Brief: `light/sun-shadows-1`

| Field | Value |
| --- | --- |
| Title | Sun shadows I: stable cascades |
| Kind | I |
| Size | XL |
| Tracks | E |
| Needs | `light/shadow-basics`, `draw/gpu-driven`, `draw/occlusion` |
| From | render-direct ch. 7; 1.6 (the stable layout, the fifth cascade, the GPU depth fit, containment, blend bands, stats); + sun caster selection (`FindShadowCasters`, `CanShadowView`), the cascade cache and its versions, cascade occlusion (`draw/occlusion` links here for it); + the shadows view |
| Unit | `plan/allocation/light.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `light/sun-shadows-1` — Sun shadows I: stable cascades

**Covers.** The job: cover the whole view with the sun's shadow maps, finely near the camera, with texels that stay put
when the camera moves. This page carries the full section on the problem: one map cannot cover a view finely; the
approaches are cascaded and parallel-split maps, maps fitted to the receivers (SDSM), stable cascades (Valient 2008) and
virtual shadow maps, with a table. Strata's history is "What went wrong before": 0.7.0 fitted the cascades to the
receivers by readback, so shadows sharpened over a second after a turn and jumped when a ball passed the camera. The
map: one D32 array with a layer per cascade, made with the first shadowed sun; what it costs in memory (five 8192 layers
take 1.25 GiB; the values come from the generated quality tables) and what happens when it does not fit (the size halves
down to 1024, reported once). The layout in code: splits from a fixed 1.5 m, a blend of logarithmic and uniform spacing
by `CascadeDistribution`, the first split at most 7.5 m; the smallest sphere around each slice, from the lens alone;
squares that cover the sphere, the filter's reach and one snapping texel, centered on whole texels of absolute light
space in double; the fifth, near cascade at High and Ultra. Selection by containment: the first cascade whose split lies
beyond the depth and whose square holds the point 33 texels inside, never by depth alone; the blend bands into the next
cascade. The GPU's depth fit for each cascade: why each cascade's depth range is fitted (it spans from the slice's far
side only to the nearest caster toward the light, so the depth's precision goes where the casters are), casters beyond
`c_MaxShadowCasterDistance` (100 km) pancaked onto the near plane, and `CascadeFit.comp` writing `u_Cascades`, which
every shadow reader reads, never `FrameConstants`. The casters, in a section of about 450 words on both paths: the
deterministic search (a job per cascade, chunks merged in order), casters under a texel left out, `FindShadowCasters`
and `CanShadowView`; on GPU-driven frames `CullShadow.comp` (`Cull.comp` built with `ST_CULL_SHADOW`) tests each
caster's light-space box against each cascade's square with the sub-texel test (`GetCasterCascades`), and `CullCascades`
widens the cascades' depth ranges for the fit, keeps the cascade mask under occlusion culling and emits draws into each
cascade's shadow buckets, none into a cached cascade; on feedback frames `FindShadowCasters` only places the cascades;
on the CPU path `GatherShadowDraws` batches the casters by the sort key's cascade field. The cascade cache and the
versions it compares, which run only on GPU-driven frames (the CPU path redraws every cascade every frame), and the
cascades' occlusion culling (`draw/occlusion` links here). The statistics per slice, and the shadows debug view:
receivers colored by screen pixels per shadow texel, cascade edges, hatched bands, with its statistics. The quality rows
`ShadowResolution` and `ShadowCascades` are named, with values from generated tables. A toy computes splits for one lens
in 30 lines. Figures: the stable-cascades and containment diagrams; the shadows view at Medium and at High; cascade
blend 0 against 0.1 across a split; four against five cascades; a sweep of `CascadeDistribution` in the shadows view.
"What Strata does not do": a second shadowed directional light, virtual shadow maps. The Manual's table of cascades per
preset is wrong and the page takes the code's numbers (an erratum). How it is tested: `Renderer.ShadowCascades`, and the
GPU cases (the first frame after a turn final, a strafe without shimmer, the ball shot, the cache, the blend seam).
Exercises: shadow tuning on the Third-Person course; a unit test for `GetLayout`; selection by depth only on a branch; a
trace of one caster into a cascade's draws on both paths. Afterwards the reader can explain and change the cascade
layout, follow a caster into the cascades and read the shadows view.

**Leaves out.**

- Shadow maps, biases and pancaking → `light/shadow-basics`
- The soft filter, the screen-space mask and contact shadows → `light/sun-shadows-2`
- Occlusion culling in general → `draw/occlusion`
- Presets and players' options → `image/quality-settings`
- Shadows of point and spot lights → `light/local-shadows`

**Fit.** `fits`: about 7,450 words against XL (8,000). Five excerpts, the casters section on both paths (about 450), the
shadows view and the caches take the most; the four exercises add about 1,000.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-direct:112-115` | feature | home | The cascade map, the stable layout, the fifth cascade, the GPU depth fit: each cascade's depth range spans from its slice's far side to the nearest caster toward the light, so the depth's precision goes where the casters are; casters beyond `c_MaxShadowCasterDistance` (100 km) are pancaked onto the near plane; `CascadeFit.comp` writes `u_Cascades`, which every shadow reader reads, never `FrameConstants` (`Docs/DeveloperGuide.md:4526-4530`; `Strata/shaders/Scene/CascadeFit.comp.slang:6-10`) |
| `render-direct:117-121` | feature | home | Sub-texel casters dropped, the deterministic caster search, containment selection, cascade blend, the cascade cache, which runs only on GPU-driven frames: the CPU path (`GPUDriven` off, devices without `drawIndirectFirstInstance`, thumbnails) redraws every cascade every frame (`Strata/src/Strata/Renderer/SceneRenderer.cpp:3343-3349`, `:248-251`; `Strata/src/Strata/Renderer/SceneRendererGPUDriven.cpp:164-168`; `Strata/src/Strata/Renderer/SceneRenderer.h:233-239`) |
| `new:43` | feature | home | The cascades' memory and their failure path, about 100 words: five 8192 layers take 1.25 GiB (the values come from the generated quality tables; `image/quality-settings` keeps the estimators); a map that cannot be made halves each way down to 1024, the size every reader then uses, reported once. Evidence: `Strata/src/Strata/Renderer/SceneRenderer.cpp:64-65`, `:1734-1749`; `Docs/DeveloperGuide.md:4691-4692` |
| `render-direct:130` | feature | home | Cascade statistics in `SceneRendererStats::Cascades` and `renderStats.cascades` |
| `render-direct:177` | feature | home | The shadows debug view and its statistics |
| `render-direct:189-190` | feature | home | The quality rows `ShadowResolution` and `ShadowCascades` (values from generated tables) |
| `render-direct:369` | concept | home | Cascaded shadow maps and their stability; why receiver fitting was dropped; the mistakes |
| `render-direct:452` | code | home | `Strata/src/Strata/Renderer/ShadowCascades.cpp:14-21`: logarithmic and uniform splits; with 56-71, why the splits start at a fixed distance |
| `render-direct:453` | code | home | `Strata/src/Strata/Renderer/ShadowCascades.cpp:73-102`: the smallest sphere around a slice, from the lens alone |
| `render-direct:454` | code | home | `Strata/src/Strata/Renderer/ShadowCascades.cpp:104-141`: the layout with blend bands; snapping to texels in double |
| `render-direct:455` | code | home | `Strata/shaders/Include/Shadows.slang:45-92`: selection by containment and the blend weights |
| `render-direct:499` | figure | home | Diagram: stable cascades from above, a second panel with the camera turned 90 degrees and identical spheres |
| `render-direct:501` | figure | home | Diagram: containment, a position near a square's edge moved by the normal offset |
| `render-direct:542` | figure | home | The shadows view at Medium against High on the Third-Person course, with the legend |
| `render-direct:544` | figure | home | Cascade blend 0 against 0.1 across a split (a long fence) |
| `render-direct:551` | figure | home | Four against five cascades in the shadows view (Showcase shot 5) |
| `render-direct:599-604` | rule | home | Select with `SelectShadowCascade`; layouts come only from `GetLayout`; snap in double in absolute light space |
| `render-direct:610` | rule | home | A new input of how casters are drawn changes a version the shadow caches compare |
| `render-direct:627` | rule | home | The Manual's drift: the page takes the code's values, not the Manual's; the cascades' erratum is `new:44`, and the 16 shadowed lights are `new:12` on `light/local-shadows` |
| `new:44` | erratum | home | `Docs/Manual/Lighting.md:156` gives the sun's shadow 3, 4, 4 and 4 cascades at Low, Medium, High and Ultra, and `:160` speaks of "four 8192 texel cascades" that "take 1 GiB" at High and Ultra; the presets' row gives 3, 4, 5 and 5 (`c_ShadowCascadesRow`), and five 8192 layers take 1.25 GiB. Evidence: `Docs/Manual/Lighting.md:156`, `:160`; `Strata/src/Strata/Renderer/RendererQuality.cpp:40`; `Docs/DeveloperGuide.md:4691` |
| `render-direct:642` | hands-on | home | Exercise: acne at a low sun on the Third-Person course, the biases, peter-panning, Medium against High in the shadows view |
| `render-direct:659-660` | hands-on | home | Exercises: a unit test for `ShadowCascades::GetLayout`; selection by depth alone, shown failing in the shadows view |
| `render-direct:721-728` | term | home | CSM, split and slice, logarithmic and uniform splits, stable cascades, texel snapping, blend band, containment, pixels per texel |
| `new:9` | not-done | home | A second shadowed directional light (the moon); virtual shadow maps. Evidence: `Docs/Roadmap.md:949-950, 1670` |
| `new:10` | figure | home | Sweep: `CascadeDistribution` 0, 0.5, 0.9 and 1 in the shadows view, showing where the detail goes. Evidence: `Strata/src/Strata/Renderer/RendererComponents.h:36-39` |
| `render-scene:61`, `render-scene:62`, `render-scene:141`, `render-scene:142` | feature | home | The caster search (`FindShadowCasters`), off-view casters for animators (`CanShadowView`), cascade occlusion, the cascade cache and its versions (on GPU-driven frames only: the CPU path redraws every cascade) |
| `render-scene:448` | figure | home | The cascade cache in numbers on a GPU-driven frame: a still view with `renderStats.cachedCascades` at the cascade count, then a moving object that redraws only the cascades it reaches |
| `render-scene:124` | feature | use | `Cull.comp`'s shadow variant, `CullShadow.comp` (`ST_CULL_SHADOW`, `Strata/CMakeLists.txt:192`), for the casters section; the culling's home is `draw/gpu-driven`, which keeps one sentence that points here |
| `new:42` | code | home | `Strata/shaders/Scene/Cull.comp.slang:399-434`: `CullCascades`, the heart of the casters section (about 450 words with what follows): a caster's light-space box tested against each cascade's square with the sub-texel test (`GetCasterCascades`, 238-270), the cascades' depth ranges widened toward the light for the fit, the cascade mask under occlusion culling, and the draws emitted into each cascade's shadow buckets except those of cached cascades (`EmitShadowInstances`, 314-325; drawn by `DrawGPUShadows`, `Strata/src/Strata/Renderer/SceneRendererGPUDriven.cpp:1382-1412`); on feedback frames `FindShadowCasters` only places the cascades (`Docs/Architecture.md:2504-2507`); on the CPU path `GatherShadowDraws` batches the casters by the sort key's cascade field (`Strata/src/Strata/Renderer/SceneRendererExtraction.cpp:1126-1254`) |
| `new:45` | hands-on | home | Exercise (trace it yourself): one fence post followed into a cascade's draws: on the CPU path from `FindShadowCasters` to its cascade mask and its sort keys in `GatherShadowDraws`, on a GPU-driven frame from `GetCasterCascades` to `EmitShadowInstances`; then `renderStats.cascades` read for both. Evidence: `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp:418`, `:1126-1254`; `Strata/shaders/Scene/Cull.comp.slang:238-270`, `:314-325` |
| `render-scene:489` | rule | home | A new input of how casters are drawn changes a version the shadow caches compare (`render-direct:610`) |
| `render-scene:652-654` | term | home | Shadow caster and cascade, sub-texel caster, shadow cascade cache |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Shadow maps, comparisons and biases | `light/shadow-basics` | must |
| GPU-driven culling | `draw/gpu-driven` | must |
| Occlusion culling and depth pyramids | `draw/occlusion` | must |
| Frustums and bounding spheres | `basics/math-geometry` | must |
| Float precision far from the origin | `basics/numbers` | must |
| Deterministic parallel jobs | `core/jobs` | must |
| Overlay passes | `gpu/debug-drawing` | must |
| The render scene's change logs | `draw/render-scene` | must |
| Blending between two values | `basics/math-interpolation` | helps |
| Quality presets | `image/quality-settings` | helps |
| Running `viewport.capture` | `editor/commands` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `cascade-light` | cascade (light) | - |
| `cascade-blend-band` | Cascade blend band | - |
| `cascaded-shadow-maps` | Cascaded shadow maps | CSM |
| `containment-cascade-selection` | Containment (cascade selection) | - |
| `shadow-cascade-cache` | Shadow cascade cache | - |
| `shadow-caster` | Shadow caster | - |
| `slice-light` | slice (light) | - |
| `split` | Split | - |
| `stable-cascades` | Stable cascades | - |
| `sub-texel-caster` | Sub-texel caster | - |
| `texel-density-light` | Texel density (light) | pixels per texel |
| `texel-snapping` | Texel snapping | - |
