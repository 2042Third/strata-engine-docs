# Brief: `indirect/ssr`

| Field | Value |
| --- | --- |
| Title | Screen-space reflections |
| Kind | I |
| Size | XL |
| Tracks | E |
| Needs | `indirect/probes`, `image/taa`, `light/clearcoat-transmission`, `indirect/ao` |
| From | render-indirect ch. 7; 1.7 (screen-space rays, the Checkerboard and Spatial traces, validation, the resolve, fallbacks and limits; Checkerboard's use of the TAA history as the exception to "nothing needs history") |
| Unit | `plan/allocation/indirect.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `indirect/ssr` — Screen-space reflections

**Covers.** The job: reflections of what is on screen, traced through the depth buffer every frame and laid over the
probes' and the sky's specular light. Transparent surfaces get none. The problem section teaches screen-space ray
marching from zero: a reflected ray is a straight line in (UV, depth) under perspective; stepping, bisection, thickness
tolerances, hierarchical-Z tracing and why Strata rejected it for grazing floors, confidence and fades, and reusing the
previous frame's color along motion vectors. A table compares linear marches, Hi-Z, stochastic SSR with temporal
reuse, planar reflections and ray-traced reflections.

The map is the diagram of the two pipelines: Checkerboard (Medium: half resolution, one pixel of each 2x2 block per
frame, 24 quadratic steps and 6 bisections, interleaved gradient noise that turns per frame, colors from the TAA history
along the hit's motion) against Spatial and SpatialHigh (High and Ultra: every pixel at full resolution, 32 or 48 steps
offset by GTAO's fixed order, validated crossings, a 5x5 resolve, the previous frame's color copy). Around it: the
component's three fields, the quality row `Reflections`, the prepass's surface target (octahedral normal, widened
roughness, metallic), the color copy (sharp up to roughness 0.05, blurred levels from 0.15), memory (about 20 MiB for
Checkerboard at 1080p, about 150 MiB more for Spatial at 4K) and the first frame of a Spatial mode, which has no copy yet
(captures render one more frame). The contract is seven rules: SSR light is visible light (ambient occlusion must not
darken what a ray found); fade only where rays leave the screen; keep only validated crossings; the Hi-Z march was
rejected; never fill an object's back in a mirror with its front's colors; Checkerboard needs TAA, the one named
exception to "nothing needs history" (`image/taa` is the decision's home); results are premultiplied. A toy version is
exercise E8: a CPU march with bisection over a synthetic depth buffer, which also shows the Hi-Z march running out of
steps over a grazing floor.

The real code, in data order: `BeginScreenRay` (the line in (UV, depth), cut at the screen's edge and at the far and
near planes, rays into the surface refused); `GetHitConfidence` (back faces get 0; the edge fade only near the exit the
ray leaves through); Checkerboard's `TraceReflection`; the Spatial trace with `BisectCrossing`, `ValidateCrossing`,
`RefineCrossing` and `RefinePlaneCrossing`, up to `MaxCandidates` rejected crossings, the last point half a pixel before
the end; `ReflectionResolve.comp`'s ratio estimator under a GGX lobe weight with plane and normal weights; the forward
mix `radiance (1 - a) + rgb` before the split sum, where only the material's occlusion map darkens what the ray found.
What went wrong before: 0.7.0 took any point behind a surface as a hit (thin posts became ghosts), faded near every edge
(sky wedges) and let AO darken wet ground; exercise E7 brings the first back and watches its test fail. An erratum: the
component's comment says "with TAA only", which is true of Checkerboard alone. What Strata does not do: reflections of
and through transparent surfaces, glass behind glass, and screen-space reflections on a clear coat (they cover its base
only; the coat's image light is the probes', the sky's or the ambient's). Tests: `GPU.SceneRenderer.SSR`,
`GPU.SceneRenderer.IndirectFlicker` with the flicker meter of `engineering/test-kinds`, `Renderer.ReflectionMetrics`.
Figures: the modes as a sweep (Off, Checkerboard with TAA, Spatial, SpatialHigh), the maximum roughness as a sweep,
crops of the edge fade, the thin posts and the wall's edge, the crescent of a ball's back, and wet ground beside an
object that AO no longer darkens; six diagrams, the screen door before and after the resolve among them. A trace
exercise follows which trace a quality row runs and what it reads. The reader can explain both traces and change them
without bringing back a fixed failure.

**Leaves out.**

- TAA's history, reprojection and jitter → `image/taa`
- Motion vectors and the motion history → `draw/motion-vectors`
- The half-resolution scene-color copy that glass reads → `light/clearcoat-transmission`
- Fresnel and F0 from the IOR → `light/reflectance`
- The flicker meter and image metrics in tests → `engineering/test-kinds`
- The look-dev shots and how they are captured → `engineering/look-dev`
- A wet floor in a game → `make/reflections`
- The `Reflections` row among the presets → `image/quality-settings`

**Fit.** `fits`: about 7,450 words against XL (8,000). Screen-space ray marching from zero, two traces, a resolve, seven
rules, six diagrams and six pictures take the most words; the toy is exercise E8's sketch, so it is not counted twice.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-indirect:293` | concept | home | Screen-space ray marching: lines in (UV, depth), stepping, bisection, thickness, Hi-Z and its rejection, confidence and fades, the previous frame's color along motion; Strata's two modes; errors: fading near every edge, any point behind a surface as a hit, back faces, SSR on rough surfaces |
| `render-indirect:137` | feature | home | The component's fields `ScreenSpaceReflections` (off), `...Intensity` (1), `...MaxRoughness` (0.5, fading over the last quarter) |
| `render-indirect:138` | feature | home | The quality row `Reflections`: Off (Low), Checkerboard (Medium), Spatial (High), SpatialHigh (Ultra), and `GetScreenReflectionSteps` |
| `render-indirect:139` | feature | home | The surface target: the prepass variant `ST_PREPASS_SURFACE` writing the octahedral view normal, widened roughness and metallic (RGBA16F) |
| `render-indirect:140` | feature | home | The shared ray setup `BeginScreenRay` |
| `render-indirect:141` | feature | home | Hit confidence: back-facing hits 0; the edge fade only where the ray leaves the screen |
| `render-indirect:142` | feature | home | The Checkerboard trace and its use of the TAA history |
| `render-indirect:143` | feature | home | The Spatial trace with validated crossings and its candidate budget |
| `render-indirect:144` | feature | home | The previous frame's color copy (B10G11R11), sharp up to roughness 0.05, blurred levels from 0.15 |
| `render-indirect:145` | feature | home | The spatial resolve: a 5x5 ratio estimator, kernel (0.5, 1, 1, 1, 0.5), GGX-lobe weight, plane and normal weights |
| `render-indirect:146` | feature | home | The forward mix, premultiplied, over the probes' and the sky's specular before the split sum |
| `render-indirect:147` | feature | home | The pending first frame of the Spatial modes, and the extra frame captures render |
| `render-indirect:148` | feature | home | Memory: Checkerboard about 20 MiB at 1080p, Spatial about 150 MiB more at 4K (`ReflectionsBytes`) |
| `render-indirect:149` | feature | home | Transparent surfaces get none (`#ifndef ST_FORWARD_TRANSPARENT` around the sample, `Strata/shaders/Scene/Forward.frag.slang:141-147`) |
| `render-indirect:111` | feature | home | SSR keeps its light: only the material's occlusion map darkens what a screen ray found (`ScreenReflectionOcclusion`) |
| `render-indirect:356` | code | home | `Strata/shaders/Include/ScreenReflections.slang:39-102`: `BeginScreenRay` and `GetHitConfidence` |
| `render-indirect:357` | code | home | `Strata/shaders/Effects/ScreenSpaceReflections.comp.slang:51-115`: the classic march, bisection and thickness, colors from the TAA history along the hit's motion |
| `render-indirect:358` | code | home | `Strata/shaders/Effects/ScreenSpaceReflectionsSpatial.comp.slang:151-274`: validated crossings, the central algorithm, shown in two pieces |
| `render-indirect:359` | code | home | `Strata/shaders/Effects/ReflectionResolve.comp.slang:75-120`: the ratio estimator under the GGX lobe weight with plane and normal weights |
| `render-indirect:397` | figure | home | Diagram: a view-space ray as a line in (UV, depth), cut at the edge and the far plane, steps denser near the start, bisection |
| `render-indirect:399` | figure | home | Diagram, two panels: a ray passing behind a thin post (0.7.0's ghost) against a validated crossing; the plane crossing at a wall's top edge |
| `render-indirect:401` | figure | home | Diagram: the Checkerboard and Spatial pipelines with their memory per pixel |
| `render-indirect:403` | figure | home | Diagram: why the screen cannot show an object's back (the crescent) |
| `render-indirect:404` | figure | home | Diagram: the edge fade only near the edge the ray leaves through |
| `render-indirect:446` | figure | home | Sweep: Off, Checkerboard with TAA, Spatial and SpatialHigh on `lookdev.mirror`, by the quality row and Post Process |
| `render-indirect:448` | figure | home | Sweep: `ScreenSpaceReflectionsMaxRoughness` 0.2 against 0.5 on the polished, satin and glossy crops of `lookdev.mirror` |
| `render-indirect:449` | figure | home | Crop: the edge fade on wet ground (`lookdev.wet.sunward`, left and right) |
| `render-indirect:450` | figure | home | Crop: thin posts and a wall's edge (`lookdev.sheet`, `post-wall`) |
| `render-indirect:451` | figure | home | Crop: the crescent of a ball's back (`lookdev.sheet.angle`, `crescents`) |
| `render-indirect:452` | figure | home | Diagram: the rough sheet's reflection before the resolve (the screen door of single samples) and after it; a diagram because tier 2 has no capture switch that skips the resolve (R34, D42: one request extends tier 2) |
| `render-indirect:453` | figure | home | Crop: AO no longer darkening what SSR found, wet ground beside an object (`lookdev.wet`, `edge`) |
| `render-indirect:486` | rule | home | SSR light is visible light: AO must not darken what a screen ray found (0.7.0's dark smudges on wet ground) |
| `render-indirect:488` | rule | home | Fade only where rays leave the screen (`GetHitConfidence`); fading near every edge drew sky wedges |
| `render-indirect:489` | rule | home | Keep only validated crossings in Spatial; "any point behind a surface" read thin posts as ghosts |
| `render-indirect:491` | rule | home | The Hi-Z march was rejected for Spatial: grazing rays over floors ran out of iterations (stripes at 4K); the textbook algorithm is not always right |
| `render-indirect:493` | rule | home | Never fill an object's back in a mirror with its front's colors ("option F", tried and rejected: front-lit rims) |
| `render-indirect:494` | rule | home | Checkerboard needs TAA: Medium's named exception to "nothing needs history", keeping 0.6.0's costs |
| `render-indirect:495` | rule | home | Premultiplied results: a texel that found nothing adds no black at a reflection's edge |
| `render-indirect:552` | hands-on | home | E7: bring back 0.7.0's acceptance in the Spatial trace and watch `GPU.SceneRenderer.SSR` "Thin posts..." fail |
| `render-indirect:553` | hands-on | home | E8: a CPU march with bisection over a synthetic depth buffer, and the Hi-Z march's grazing-floor failure (the toy version) |
| `new:25` | hands-on | home | Exercise (trace it yourself, R32, D27): which trace a quality row runs in a frame and what it reads: the Spatial modes need the color copy of the renderer's previous frame without a cut or a reset, Checkerboard needs TAA with a history of more than one frame, and `ReflectionParams.x` tells the forward pass to sample the result; the solution names the lines and says why a bake and a first frame get none. Evidence: `Strata/src/Strata/Renderer/SceneRenderer.cpp:2982-2984`, `:3047-3065`, `:3118`; `Strata/shaders/Scene/Forward.frag.slang:139-147` |
| `render-indirect:707` | open | home | The component's comment contradicts the Spatial modes; the page follows the code and states the erratum (`new:11`) |
| `new:10` | not-done | home | No reflections of or through transparent surfaces, no glass behind glass, and no screen-space reflections on a clear coat: they cover the coat's base only, and the coat's image light comes from the probes, the sky or the ambient (`SampleSpecularLight`). Evidence: `Docs/Roadmap.md:939-942` ("screen-space reflections cover a clear coat's base only and trace no transparent surface"; glass behind glass does not show) and `:947-948` ("SSR for transparent surfaces" left for later); `Strata/shaders/Scene/Forward.frag.slang:141-147` (no sample on transparent surfaces), `:323-333` (the coat's image light) |
| `new:11` | erratum | home | The comment at `Strata/src/Strata/Renderer/RendererComponents.h:313-314` says screen-space reflections work "with TAA only"; at the pin only Checkerboard reads the TAA history, and Spatial and SpatialHigh run with or without TAA. Evidence: `Strata/src/Strata/Renderer/RendererQuality.h:88-91` |
| `render-indirect:608` | term | home | Screen-space reflections (SSR) |
| `render-indirect:610` | term | home | Surface target, its own entry; "prepass" is `render-core:733`'s entry (depth prepass) |
| `render-indirect:612` | term | home | Ray march, step and bisection, three entries |
| `render-indirect:613` | term | home | Thickness tolerance |
| `render-indirect:614` | term | home | Candidate and validated crossing, two entries |
| `render-indirect:615` | term | home | Hi-Z (hierarchical depth) march |
| `render-indirect:616` | term | home | Confidence |
| `render-indirect:621` | term | home | Checkerboard, Spatial and SpatialHigh, Strata's three modes |
| `render-indirect:622` | term | home | Ratio estimator |
| `render-indirect:197` | feature | use | The flicker meter (`GPUSceneIndirectFlickerTests.cpp`, `ReflectionMetrics.h`) in the tests of this page; its home is `engineering/test-kinds` |
| `render-image:700` | term | use | The TAA history Checkerboard reads (`render-indirect:619` repeats it) |
| `render-indirect:520` | rule | link | No blocking, as the probes fall back for a ray that found nothing; taught on `indirect/probes` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Projection, NDC, UVs and reversed Z | `gpu/coordinates` | must |
| The depth prepass and its variants | `gpu/frame-tour` | must |
| Motion vectors | `draw/motion-vectors` | must |
| TAA's history and reprojection, and "nothing needs history to look right" | `image/taa` | must |
| Octahedral encoding of a unit vector | `basics/math-sphere` | must |
| Interleaved gradient noise | `basics/math-probability` | must |
| The scene-color copy | `light/clearcoat-transmission` | must |
| Premultiplied alpha | `light/clearcoat-transmission` | must |
| Probes as the fallback of a ray that found nothing | `indirect/probes` | must |
| The specular gather and the specular occlusion it replaces | `indirect/seam` | must |
| GTAO's fixed 4x4 order (the Spatial steps' offsets) and Lagarde's specular occlusion | `indirect/ao` | must |
| The GGX lobe and Fresnel from the IOR | `light/reflectance` | must |
| Pre-exposure (the history's scale) | `image/pre-exposure` | must |
| Compute shaders and shared memory | `gpu/compute` | must |
| Quality rows and their presets | `image/quality-settings` | helps |
| The flicker meter | `engineering/test-kinds` | helps |
| The look-dev harness | `engineering/look-dev` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `candidate` | Candidate | - |
| `checkerboard` | Checkerboard | SpatialHigh |
| `confidence` | Confidence | - |
| `hi-z-march` | Hi-Z march | - |
| `prepass` | Prepass | surface target |
| `ratio-estimator` | Ratio estimator | - |
| `screen-space-reflections` | Screen-space reflections | SSR |
| `thickness-tolerance` | Thickness tolerance | - |
| `validated-crossing` | validated crossing | - |
