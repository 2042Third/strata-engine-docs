# Brief: `indirect/ao`

| Field | Value |
| --- | --- |
| Title | Ambient occlusion without history |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `indirect/seam`, `gpu/compute`, `basics/signals` |
| From | render-indirect ch. 4; 1.4, 1.5 (GTAO, the fixed pattern and denoiser, the radius clamp, thin occluders, the multi-bounce fit, specular occlusion); the AO view |
| Unit | `plan/allocation/indirect.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `indirect/ao` — Ambient occlusion without history

**Covers.** The job: occlusion of the indirect light, computed in screen space from the prepass's depth and normals each
frame, without history, and how it enters shading (diffuse through the multi-bounce fit, specular through Lagarde's
specular occlusion). The material's occlusion map is `light/materials`'; shadows are the direct light's.

The problem section teaches what occlusion of ambient light means (visibility against obscurance) and the approaches
with their costs: Crytek's SSAO, HBAO, GTAO (Jimenez et al. 2016), baked AO maps and ray-traced AO. Then the second
idea: why few samples per pixel are enough when a fixed interleaved pattern is resolved in space, against frame noise
that TAA must clean (it ghosts, and the image differs between anti-aliasing modes). This is "nothing needs history to
look right" at work (`image/taa` is its home).

The map: `RenderAmbientOcclusion` clamps the component's values, fills push constants and makes two dispatches (GTAO,
then the denoiser) in `GPU.AO`; targets are R16F where the device stores it, else R32F, with the shader variants
`GTAOHalf` and `AODenoiseHalf`; the quality row sets slices and steps (Low 1x4, Medium 2x6, High 3x8, Ultra 4x12); the
component's fields are on, radius 1 m, intensity 1 and multi-bounce on. The contract is four rules: AO darkens indirect
light only; no history (the fixed 4x4 pattern, never the frame); the radius is clamped on screen between 0.3% (at least
1.5 px) and 12% of the view's height; the fit changes only by running `Tools/FitAOMultiBounce.py --write`. A toy version
computes horizon AO over a 1D height field. The real code: `GTAO.comp` (slices, the two horizons, the cosine-weighted
arc, the radius clamp, the thin-occluder relaxation `1 - 0.9^(6/steps)`, the pattern's rotations and step jitter);
`AODenoise.comp` (the 5x5 tent whose weights 0.5, 1, 1, 1, 0.5 weigh each of the 16 phases once, then a bilateral blur,
separable in a 24x24 shared tile, one dispatch); the multi-bounce fit (`x / (1 - rho (1 - x) h)`, fitted to 2D radiosity
in grooves and trenches, and why the planned polynomial was rejected); where AO applies (indirect light only, not on
transparent surfaces); Lagarde's specular occlusion, multiplied by the horizon fade of `indirect/ibl`, on the fallback
only.

Alternatives: HBAO+, temporally accumulated GTAO, ray-traced AO, bent normals and cones. How it is tested:
`Renderer.AmbientOcclusion` (the fit against the script's reference) and `GPU.SceneRenderer.AmbientOcclusion` (no
pattern without TAA), with the exercises E2 and E4 and a trace of the radius from metres to pixels. Changing it safely:
the generator, the no-history rule, and the `ao` view's repeats when frame constants change (the GI's own buffer,
`indirect/gi-cascades`). What went wrong before: a `:::history` of 0.6.0's AO and its blur, made history-free in 0.7.0
with the radius clamp and the multi-bounce. Figures: AO off and on with the `ao` view, the quality rows as a sweep, the
radius at 0.25, 1 and 3 m with a near and a far object, a crop of thin occluders, multi-bounce on a white and a dark
corner, the same AO under TAA, FXAA and none, and the Cornell box with AO against the reference. The reader can explain
GTAO and change it without breaking a rule.

**Leaves out.**

- Material occlusion maps and their import → `light/materials`
- Where the occlusion terms enter the gathers, as a whole → `indirect/seam`
- What the screen-space reflections keep of their light under AO → `indirect/ssr`
- Using AO in a game: radius, intensity and multi-bounce on real materials → `make/reflections`
- The AO view among the other debug views → `light/measuring-light`
- The quality row among the presets → `image/quality-settings`

**Fit.** `over`: about 6,850 words against L (5,000). Four ideas from zero, four excerpts, four diagrams, seven pictures
and three exercises pass L's top; by S2 the page takes the next size, XL (8,000), one page with anchored sections,
because a split would cut the one mechanism (pattern, resolve, fit) in two.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-indirect:269` | concept | home | Ambient occlusion: visibility against obscurance, the screen-space methods, baked and ray-traced AO, with a table of costs; errors: AO on direct light, AO on specular unchanged, dark halos from thin occluders, radius in pixels against metres |
| `render-indirect:274` | concept | home | Noise, patterns and denoising without history: a 4x4 ordered-dither pattern whose 16 phases a separable 5x5 tent weighs exactly once, so one frame is complete; the error of frame-varying noise left to TAA |
| `render-indirect:280` | concept | home | Multi-bounce AO: occluded light is not lost; Jimenez's polynomial against Strata's rational fit; the error that AO darkens white corners as much as black ones |
| `render-indirect:283` | concept | home | Specular occlusion from AO: Lagarde's specular occlusion (2014), multiplied by the horizon fade of `indirect/ibl`; the error of occluding what SSR saw (its fix is `indirect/ssr`'s) |
| `render-indirect:95` | feature | home | GTAO: horizon-based, cosine-weighted visibility per screen slice; the dispatch in `RenderAmbientOcclusion` |
| `render-indirect:96` | feature | home | The quality samples Low 1x4 to Ultra 4x12 (`AmbientOcclusionLevel`) |
| `render-indirect:97` | feature | home | The fixed 4x4 pattern: slice rotation and step jitter from the ordered-dither order, never the frame |
| `render-indirect:98` | feature | home | The history-free denoiser: tent resolve of the 16 phases and a bilateral blur, one dispatch, 24x24 shared tile |
| `render-indirect:99` | feature | home | The radius clamp: 0.3% (at least 1.5 px) to 12% of the view's height (`c_AOMinRadiusFraction`, `c_AOMaxRadiusFraction`) |
| `render-indirect:100` | feature | home | The thin-occluder relaxation `1 - 0.9^(6/steps)` |
| `render-indirect:101` | feature | home | The multi-bounce fit: shader, C++ header and generator, applied in the forward pass |
| `render-indirect:102` | feature | home | Half-float targets where the device stores them, R32F else, and the `Half` shader variants |
| `render-indirect:103` | feature | home | The component's fields: `AmbientOcclusion`, `AmbientOcclusionRadius`, `AmbientOcclusionIntensity`, `AmbientOcclusionMultiBounce` |
| `render-indirect:104` | feature | home | Where AO applies: indirect light only (diffuse through the occlusion color, specular through Lagarde); not on transparent surfaces |
| `render-indirect:110` | feature | home | Lagarde's specular occlusion `clamp(pow(NoV + ao, exp2(-16 r - 1)) - 1 + ao)` times the horizon fade, on the fallback |
| `render-indirect:348` | code | home | `Strata/shaders/Effects/GTAO.comp.slang:41-141`: slices, horizons, the cosine-weighted arc, the radius clamp, the relaxation and the pattern (its order at lines 32-33) |
| `render-indirect:349` | code | home | `Strata/shaders/Effects/AODenoise.comp.slang:1-90`: the header's account of the design and `ResolveAlong` (68-90) |
| `render-indirect:350` | code | home | `Strata/shaders/Include/AmbientOcclusionFit.slang:1-17`: the generated fit; with the docstring of `Tools/FitAOMultiBounce.py:2-43` on the reference and the rejected polynomial |
| `render-indirect:351` | code | home | `Strata/src/Strata/Renderer/SceneRendererAmbientOcclusion.cpp:116-143`: the CPU side of a compute effect, clamping user values, push constants and two dispatches |
| `render-indirect:385` | figure | home | Diagram: a GTAO slice with the horizons h0 and h1, the projected normal's angle and the cosine-weighted arc |
| `render-indirect:387` | figure | home | Diagram: the 4x4 pattern and the 5x5 tent kernel, each phase weighed once |
| `render-indirect:388` | figure | home | Plot: the horizon over steps behind a pole, with and without relaxation |
| `render-indirect:389` | figure | home | Chart: the multi-bounce curves for several albedos against the radiosity means |
| `render-indirect:433` | figure | home | Off and on: Post Process `AmbientOcclusion` on a sample scene, with the `ao` view (the shot `lookdev.view.ao`, `Tools/LookDev/Shots.json:65`) |
| `render-indirect:434` | figure | home | Sweep: the quality rows Low, Medium, High and Ultra |
| `render-indirect:435` | figure | home | Sweep: `AmbientOcclusionRadius` 0.25, 1 and 3 m, a near and a far object to show the clamp |
| `render-indirect:436` | figure | home | Crop: thin occluders (the look-dev poles, fence and plate) in the `ao` view |
| `render-indirect:437` | figure | home | Multi-bounce on and off on a white plaster corner and a dark soil corner, `ao` view against the lit image |
| `render-indirect:438` | figure | home | The same AO under TAA, FXAA and none (LookDev `--aa`): the proof that nothing needs history |
| `new:7` | figure | home | The Cornell box with AO and without GI, in a slider with the path-traced reference of `indirect/problem` (`new:2`): what AO approximates and what it misses. The box's only source is its emissive panel, which lights nothing without GI, so the recipe gives the box the light that AO darkens (a sky light, with a map or with its constant ambient) and captures in play (its `play` field), and its `complete` asserts `/previewLighting` false (pipelines.md §5.2, §5.3). Evidence: `Tools/LookDev/LookDevScene.json:253-268`, `Tools/LookDev/Shots.json:148` |
| `render-indirect:479` | rule | home | AO darkens indirect light only; direct light has shadows; specular uses Lagarde, not raw AO |
| `render-indirect:480` | rule | home | No history for AO: the same image with TAA, FXAA or none, two frames of a still view identical |
| `render-indirect:482` | rule | home | The radius clamped on screen: constant cost and look at every resolution |
| `render-indirect:484` | rule | home | The multi-bounce fit changes only through `Tools/FitAOMultiBounce.py --write`: three generated copies must agree |
| `render-indirect:547` | hands-on | home | E2: read and run `Renderer.AmbientOcclusion`; run the fit script (print only) and explain its errors table |
| `render-indirect:549` | hands-on | home | E4: a frame-varying pattern on a scratch branch makes "no pattern without TAA" fail |
| `new:21` | hands-on | home | Exercise (trace it yourself, R32, D27): `AmbientOcclusionRadius` followed from the component to a pixel's radius on screen: `RenderAmbientOcclusion` clamps it to 0.01 to 10 m and sets the bounds in pixels from the view's height, and `GTAO.comp` projects it and clamps it there; the solution names the lines and works the radius out for a near and a far surface. Evidence: `Strata/src/Strata/Renderer/SceneRendererAmbientOcclusion.cpp:116-128`; `Strata/shaders/Effects/GTAO.comp.slang:61-68` |
| `render-indirect:591` | term | home | Ambient occlusion (AO) |
| `render-indirect:592` | term | home | GTAO |
| `render-indirect:593` | term | home | Slice and horizon angle, two entries |
| `render-indirect:596` | term | home | Tent kernel (0.5, 1, 1, 1, 0.5), qualified against the shadows' tent filter (`render-direct:733`) |
| `render-indirect:597` | term | home | Multi-bounce AO |
| `render-indirect:599` | term | home | Specular occlusion (Lagarde) |
| `render-scene:605` | term | use | The ordered-dither order the pattern shares with the LOD fade (`render-indirect:595` repeats it) |
| `render-direct:737` | term | use | The bilateral (edge-aware) blur, taught on `light/sun-shadows-2` (`render-indirect:594` repeats it) |
| `render-indirect:598` | term | use | Radiosity, the reference the fit was made against; its home is `indirect/problem` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| View positions from depth through the inverse projection; reversed Z; UVs and NDC | `gpu/coordinates` | must |
| The depth prepass and the normals it writes | `gpu/frame-tour` | must |
| Compute shaders: thread groups, shared memory and barriers | `gpu/compute` | must |
| Kernels, sampling, ordered dither and spatial denoising | `basics/signals` | must |
| Integrals as accumulation, cosine weighting | `basics/math-probability` | helps |
| Push constants | `gpu/binding` | must |
| The inputs `DiffuseOcclusion` and `SpecularOcclusion` of the seam | `indirect/seam` | must |
| TAA, its history and "nothing needs history to look right" | `image/taa` | must |
| FXAA, for the comparison of anti-aliasing modes | `image/spatial-aa` | helps |
| Half floats and their range | `basics/color` | helps |
| Material occlusion maps | `light/materials` | must |
| The bilateral blur | `light/sun-shadows-2` | helps |
| Running a Python tool from a terminal | `basics/tools` | helps |
| Writing and running a GPU test | `gpu/first-triangle` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `ambient-occlusion` | Ambient occlusion | AO |
| `horizon-angle` | horizon angle | - |
| `multi-bounce-ao` | Multi-bounce AO | - |
| `slice-indirect` | Slice (indirect) | - |
| `specular-occlusion-lagarde` | Specular occlusion (Lagarde) | - |
| `tent-kernel` | Tent kernel | - |
