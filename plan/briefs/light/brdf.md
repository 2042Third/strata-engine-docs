# Brief: `light/brdf`

| Field | Value |
| --- | --- |
| Title | The forward shader and the BRDF in code |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `light/reflectance`, `light/material-data`, `basics/signals` |
| From | render-direct ch. 3; 1.2 (GGX, Smith, Schlick, Lambert, minimum roughness, the six variants, the EQUAL test, `[earlydepthstencil]`, the derivative rule, specular anti-aliasing, `SanitizeHDR`), code #6, #7, #10, #19, figure 20, rules 6, 10, 29 |
| Unit | `plan/allocation/light.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `light/brdf` — The forward shader and the BRDF in code

**Covers.** The job: the forward pass shades every visible surface once, from its material, the lights and the indirect
light, into the HDR target; culling the lights and drawing the shadows are other pages'. One paragraph links
`light/reflectance` and `gpu/frame-tour` for the problem. The map: the six variants compiled from one source (`Forward`,
`ForwardTransparent` and four `ForwardGlass` variants, by defines), the passes that feed the forward pass in frame order
(a timeline diagram on `gpu/frame-tour`'s stages: setup, the GPU-driven frame's culling, light culling and the clusters
inside the stage before them, which is `GPU.Setup` on the CPU path and `GPU.Cull` on GPU-driven frames, aerial
perspective, shadows, prepass, screen shadows, AO, then the opaque pass; the inventory's slip that puts them in
`GPU.Cull` alone is an erratum here), and the shading order within one pixel (material, shading normal, roughness
widening, sun, cluster lights, indirect light, coat, emission, aerial perspective, fog, glass, pre-exposure,
`SanitizeHDR`). The contract: opaque surfaces are shaded after the depth prepass with an EQUAL test and
`[earlydepthstencil]`, and discard only by the level-of-detail fade; the forward shader samples everything before any
discard (that rule and its Mesa and MoltenVK reason are `gpu/shaders`', linked), and this page adds the rule's second
half: derivatives only of the primitive's own interpolants and textures, in quad-uniform control flow, with explicit
levels in non-uniform flow, so that the CPU and GPU-driven paths shade alike; every HDR write goes through `SanitizeHDR`
(NaN to 0, clamped to 65,000), and the opaque pass writes alpha 1 by the HDR target's alpha convention (its why is
`image/taa`'s). A toy forward shader of 40 lines with one light comes next. The real code: GGX, the height-correlated
Smith term and Schlick in 25 lines; `EvaluateLightWeighted` with Lambert weighted by (1 - F)(1 - metallic); the minimum
roughness 0.045; specular aliasing from zero (a highlight narrower than a pixel sparkles; Toksvig, LEAN and CLEAN maps,
Kaplanyan-Tokuyoshi's screen-space variance) and `WidenRoughness`, capped at 0.18; the shader's main, which samples
everything before any discard. Figures: the timeline and shading-order diagrams, and specular anti-aliasing off and on
with a crop (the switch is a specification field for tests, so the figure takes the test's crops or a build with the
switch). Alternatives: a deferred G-buffer (linked), Toksvig maps, leaving sparkle to TAA. How it is tested:
`GPU.SceneRenderer.Materials` and `.Specular`, `Architecture.Shaders`. Changing it safely: both draw paths, the prepass
and the forward pass agree to the bit (`GPU.SceneRenderer.GPUDriven`). The exercises write a CPU reference of
`EvaluateLightWeighted` and compare it with a one-pixel render, and trace the six variants from the shader list to the
pass that picks each. Afterwards the reader can read `Forward.frag.slang` and `PBR.slang` and change a term safely.

**Leaves out.**

- The cluster loop and local shadows inside `ShadeLitSurface` → `light/many-lights`
- The BRDF table and energy compensation → `light/energy`
- Highlights of sized sources → `light/area-lights`
- The indirect light's inputs and gathers → `indirect/seam`
- Glass and the clear coat → `light/clearcoat-transmission`
- The lighting debug views' branches → `light/measuring-light`
- Derivatives before a discard, and why → `gpu/shaders`
- The sun's shadow comparisons at an explicit level → `light/sun-shadows-2`
- Why the HDR target's alpha has a convention → `image/taa`
- Forward against deferred shading, the depth prepass → `gpu/frame-tour`
- Mirrored instances and flipped tangents → `draw/mirrors-camera-relative`
- The HDR target and the post chain → `image/why-post`

**Fit.** `fits`: about 4,700 words against L (5,000). Four excerpts and the nine lines of `SanitizeHDR`, a toy, specular
aliasing from zero and the contract's rules take the most; the two exercises add about 500.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-direct:56-57` | feature | home | Cook-Torrance GGX with height-correlated Smith, Schlick and weighted Lambert; `c_MinRoughness` 0.045 |
| `render-direct:60` | feature | home | Specular anti-aliasing: the lobe widened by the normal's variance over the pixel, `MaterialParams.z` |
| `render-direct:64-67` | feature | home | The forward variants, the opaque pass with EQUAL and `[earlydepthstencil]`, the derivative rule's own half (derivatives only of the primitive's own interpolants and textures, in quad-uniform flow, explicit levels in non-uniform flow) with the forward shader's use of its first half (everything sampled before any discard; that half's home is `gpu/shaders`), `SanitizeHDR` |
| `render-direct:335` | concept | home | Specular aliasing and how to filter a highlight |
| `render-direct:438` | code | home | `Strata/shaders/Include/PBR.slang:33-57`: GGX D, correlated Smith V, Schlick F |
| `render-direct:439` | code | home | `Strata/shaders/Include/PBR.slang:126-148`: `EvaluateLightWeighted`, the whole direct-light BRDF and its weights |
| `render-direct:442` | code | home | `Strata/shaders/Include/PBR.slang:73-91`: `WidenRoughness`, specular anti-aliasing by the normal's variance |
| `render-direct:451` | code | home | `Strata/shaders/Scene/Forward.frag.slang:374-427`: the main, everything sampled before any discard, the coat and glass set up |
| `render-direct:495` | figure | home | Diagram: the frame timeline of the passes that feed the forward pass, on `gpu/frame-tour`'s stages, with light culling and the clusters marked inside the stage before them: `GPU.Setup` on the CPU path, `GPU.Cull` on GPU-driven frames (`Strata/src/Strata/Renderer/SceneRenderer.cpp:3289`, `:3343-3376`) |
| `render-direct:517` | figure | home | Diagram: the shading order within one pixel |
| `render-direct:533` | figure | home | Specular anti-aliasing off and on, a bumpy metal sphere, with a crop |
| `render-direct:582` | rule | home | Clamp HDR with `SanitizeHDR` |
| `render-direct:588` | rule | home | Derivatives only of the primitive's own interpolants and textures, in quad-uniform flow, so both draw paths shade alike; the rule's half "before any discard" and its Mesa and MoltenVK reason are linked to `gpu/shaders` (`render-core:587`) |
| `render-direct:654` | hands-on | home | Exercise: a CPU reference of `EvaluateLightWeighted` against a one-pixel GPU render |
| `new:32` | hands-on | home | Exercise (trace it yourself): find with a search where the six forward variants are declared, each by its defines, and where a draw's pass picks the pixel shader it runs (opaque, transparent, glass with or without velocity). Evidence: `Strata/CMakeLists.txt:89`, `:174-178`; `Strata/src/Strata/Renderer/SceneRenderer.cpp:301-302`, `:2449-2460` |
| `render-direct:687-688` | term | home | Specular aliasing; specular anti-aliasing (geometric) |
| `render-direct:838` | open | home | The specular anti-aliasing figure needs the test's crops or a build with `SceneRendererSpecification::SpecularAntiAliasing`; the writer settles which |
| `render-direct:204` | feature | use | The area's GPU stages in frame order, for the timeline; their home is `gpu/frame-tour`; light culling and the clusters are timed in `GPU.Cull` only on GPU-driven frames (`new:33`) |
| `new:33` | erratum | home | `plan/inventory/render-core.md:162` and `plan/inventory/render-direct.md:205` time light culling and the light clusters in `GPU.Cull`, and the exercise of `render-direct.md:658` measures them there: `GPU.Cull` starts only on GPU-driven frames, and the light passes recorded after it are timed in `GPU.Cull` there and in `GPU.Setup` on frames of the CPU path. Evidence: `Strata/src/Strata/Renderer/SceneRenderer.cpp:3289`, `:3343`, `:3360`, `:3365-3376` |
| `render-image:35` | feature | use | The HDR alpha convention, one sentence: opaque writers write alpha 1 and blended ones multiply it by 1 - a; the why is `image/taa`'s |
| `render-direct:68` | feature | link | Mirrored instances; their home is `draw/mirrors-camera-relative` |
| `render-indirect:472` | rule | home | The derivative rule as render-indirect states it (`render-direct:588`) |
| `render-image:30` | feature | home | `SanitizeHDR` as render-image lists it (`render-direct:67`) |
| `render-image:397` | code | home | `Strata/shaders/Include/Common.slang:49-57`: `SanitizeHDR`, NaN to 0 and overflow to 65,000, and why neither may reach an HDR target |
| `render-image:525` | rule | home | Every HDR writer clamps with `SanitizeHDR` (the rule of `render-direct:582`) |
| `render-image:640` | term | home | `SanitizeHDR` |
| `render-core:603` | rule | home | HDR writers clamp with `SanitizeHDR`, as render-core states it (`render-direct:582`) |
| `render-indirect:71` | feature | home | GGX, height-correlated Smith and Schlick as render-indirect lists them (`render-direct:56`) |
| `render-indirect:73` | feature | home | Specular anti-aliasing as render-indirect lists it (`render-direct:60`) |
| `render-indirect:265` | concept | home | Specular aliasing and geometric specular anti-aliasing, with the derivative rule |
| `render-indirect:429` | figure | home | Specular anti-aliasing off and on; with `render-direct:533`, one figure |
| `render-scene:477` | rule | home | Shading must not depend on draw order or instance order: this page is the home of shading independent of draw order |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The reflection equation, D, G and F | `light/reflectance` | must |
| The material record and the texture table | `light/material-data` | must |
| Sampling, aliasing and filtering | `basics/signals` | must |
| Shaders in Slang, entry points and defines | `gpu/shaders` | must |
| The depth prepass, EQUAL and forward against deferred | `gpu/frame-tour` | must |
| Pixel quads and screen-space derivatives | `gpu/how-a-gpu-frame-works` | must |
| Derivatives and discard in shaders | `gpu/shaders` | must |
| The half-float range | `basics/color` | must |
| Pipelines and their variants | `gpu/binding` | helps |
| The GPU-driven path's draw order | `draw/gpu-driven` | helps |
| Level-of-detail fades | `draw/lod` | helps |
| Writing a GPU test | `gpu/first-triangle` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `sanitizehdr` | `SanitizeHDR` | - |
| `specular-aliasing` | Specular aliasing | - |
| `specular-anti-aliasing-geometric` | Specular anti-aliasing (geometric) | - |
