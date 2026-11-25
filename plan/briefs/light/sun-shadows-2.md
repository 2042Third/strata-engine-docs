# Brief: `light/sun-shadows-2`

| Field | Value |
| --- | --- |
| Title | Sun shadows II: the soft shadow of a real sun |
| Kind | I |
| Size | XL |
| Tracks | E |
| Needs | `light/sun-shadows-1`, `basics/signals` |
| From | render-direct ch. 8; 1.6 (PCSS at physical width, the depth-range classification, the tent and the Vogel disk with fixed blue noise, the screen-space mask and stair blur, contact shadows, transparent receivers, why nothing depends on the frame) |
| Unit | `plan/allocation/light.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `light/sun-shadows-2` — Sun shadows II: the soft shadow of a real sun

**Covers.** The job: soften the sun's shadow by the sun's real size, the same in every frame. This page carries the full
section on the problem: penumbrae widen with the distance between blocker and receiver; the approaches are fixed PCF,
PCSS (Fernando 2005), variance, exponential and moment shadow maps, and ray-traced shadows, with a table. It is XL, in
six sections with their own anchors. One, the geometry: a sun of angular radius a over a blocker at separation s draws a
penumbra 2 s tan(a) wide, which a disk of radius s tan(a) reproduces (the PCSS diagram). Two, the classification: a
pyramid of (nearest, farthest) depths over cells of 4, 8 and 16 texels, rounded outward and built right after the
layers, decides lit and umbra exactly and never misses a thin caster (the pyramid diagram and its shader). Three, the
filter in `SampleCascadeShadow`, shown whole: the blocker estimate, a fixed four-tap tent below a texel, a Vogel disk of
8 to 32 taps above one or two texels, turned per pixel by a fixed 64 x 64 blue-noise tile; its comparisons take an
explicit level (`SampleCmpLevelZero` in `CompareShadowMap`): the classification returns early, so the sun is shaded in
non-uniform flow, and zero gradients made the evaluation cost 2.2 to 2.4 times as much; the rule that nothing changes
per frame (never `TemporalParams.z`), so a still view is the same image with and without TAA; the `ShadowFilterQuality`
row. Four, the screen-space mask: after the prepass, every opaque pixel gets the filter into RG8 (the square root of the
visibility, a blur radius), blurred horizontally then vertically with plane-distance and normal weights, and the forward
pass reads it at SRV 28 (the mask-pipeline diagram); the stair-step blur where the tent leaves an edge on a receiver the
light grazes. Five, contact shadows: a screen-space march toward the sun over the prepass depth, which sees every opaque
pixel, ignores `CastShadows`, shimmers in motion and is therefore on in no preset (Custom only; 0.7.0's High and Ultra
had drawn them). Six, transparent receivers: they call `SampleDirectionalShadow` per pixel without blur or contacts, and
both paths change together. A toy is a 1-D PCSS. Figures: the penumbra growing with distance (poles of 3, 5 and 10 cm at
Angular Diameter 0.53 and 2), 8 against 32 taps without TAA, stair steps without and with the blur (a crop), contact
shadows 16 steps against 0, and the sun's Angular Diameter on shadows. Alternatives. How it is tested:
`GPU.SceneRenderer.ShadowFilter` (penumbra width, independence from TAA, a thin caster never lost, tent smoothness,
ranges that hold every texel, contacts), `.ScreenShadows`, `.ContactShadows`, `PerfGPU.Renderer.ScreenShadows4K*`.
Exercises: a penumbra study measured against s tan(a); the pyramid's first level as a debug overlay; a trace of one
pixel's sun visibility from the mask to the forward pass, and of a transparent pixel's. Afterwards the reader can derive
PCSS at physical width, follow `SampleCascadeShadow`, and change the filter without making it depend on history.

**Leaves out.**

- The cascades and their selection → `light/sun-shadows-1`
- Blue noise and the Vogel pattern from zero → `basics/math-probability`
- Temporal anti-aliasing and "nothing needs history" → `image/taa`
- Shadows of point and spot lights → `light/local-shadows`
- The highlight of a sized sun → `light/area-lights`
- Presets and players' options → `image/quality-settings`

**Fit.** `fits`: about 7,200 words against XL (8,000). Three excerpts, the central one long, four diagrams, five figures
and six sections take the most; the three exercises add about 750.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-direct:123-128` | feature | home | The physical PCSS filter, the depth ranges, the screen-space mask, the stair-step blur, contact shadows, transparent receivers |
| `render-direct:194-195` | feature | home | The rows `ShadowFilterQuality` (disk taps) and `ContactShadows` (Custom only) |
| `render-direct:377` | concept | home | Soft shadows: PCF, PCSS, contact hardening, noise; the mistakes |
| `render-direct:384` | concept | home | Screen-space shadow passes and contact shadows; the mistake about `CastShadows` |
| `render-direct:457` | code | home | `Strata/shaders/Include/Shadows.slang:143-260`: `SampleCascadeShadow` whole: classification, blocker estimate, tent, Vogel disk with blue noise |
| `render-direct:458` | code | home | `Strata/shaders/Scene/ShadowRanges.comp.slang:27-70`: a conservative min-max pyramid with outward rounding |
| `render-direct:460` | code | home | `Strata/shaders/Effects/ScreenShadows.frag.slang:53-92`: position and normal from the prepass, visibility encoded as a square root, the blur radius |
| `render-direct:503-507` | figure | home | Diagrams: PCSS geometry and the filter's decisions; the depth-range pyramid; the screen-space mask pipeline |
| `render-direct:545-546` | figure | home | The penumbra growing with distance (`lookdev.thin`); filter taps 8 against 32 without TAA |
| `render-direct:548-550` | figure | home | Stair steps without and with the blur (a crop); contact shadows (`lookdev.contact`) 16 against 0 |
| `render-direct:605-608` | rule | home | The sun's filter uses fixed noise; change both shadow paths together |
| `render-direct:625` | rule | home | The sun's comparisons take an explicit level, about 100 words beside `SampleCascadeShadow`: `CompareShadowMap` calls `SampleCmpLevelZero` because the classification returns early, so the sun is shaded in non-uniform flow, and sampling with zero gradients made the evaluation cost 2.2 to 2.4 times as much (`Strata/shaders/Include/Shadows.slang:119-126`; `Docs/DeveloperGuide.md:4716-4717`) |
| `render-direct:612` | rule | home | Contact shadows come from every opaque pixel on screen |
| `render-direct:643` | hands-on | home | Exercise: the penumbra study, measured against 1.374 s tan(a) |
| `render-direct:661` | hands-on | home | Exercise: the pyramid's first level as a debug overlay |
| `new:46` | hands-on | home | Exercise (trace it yourself): one opaque pixel's sun visibility followed with a search from `ScreenShadows.frag`, which `RenderScreenShadows` draws and blurs, to the forward pass's read at SRV 28; then a transparent pixel's call of `SampleDirectionalShadow`, which skips the mask. Evidence: `Strata/src/Strata/Renderer/SceneRendererScreenShadows.cpp:14-15`, `:186`; `Strata/shaders/Scene/Forward.frag.slang:69`, `:238-240`; `Strata/shaders/Include/Shadows.slang:285` |
| `render-direct:729-733` | term | home | PCSS, umbra and penumbra, contact hardening, depth range pyramid, tent filter |
| `render-direct:736-738` | term | home | Screen-space shadow mask, edge-aware (bilateral) blur, contact shadows |
| `render-direct:826` | open | home | Whether a shipped preset drew contact shadows: the page says 0.7.0's High and Ultra did and 0.8.0 turned them off; the writer checks the 0.7.0 rows |
| `render-image:282` | feature | home | `Tools/GenerateBlueNoise.py` writes the 64 x 64 void-and-cluster tile of `BlueNoise.h` that turns the sun's filter |
| `render-direct:535` | figure | use | The sun's Angular Diameter on shadows; the figure's home is `light/area-lights` |
| `render-direct:734-735` | term | link | Vogel disk and blue noise; their home is `basics/math-probability` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Stable cascades and their selection | `light/sun-shadows-1` | must |
| Shadow maps and biases | `light/shadow-basics` | must |
| Sampling, kernels and filtering | `basics/signals` | must |
| Noise and sampling patterns: blue noise, the Vogel disk | `basics/math-probability` | must |
| Octahedral normals | `basics/math-sphere` | must |
| The depth prepass | `gpu/frame-tour` | must |
| Compute shaders | `gpu/compute` | must |
| Temporal anti-aliasing and its history | `image/taa` | helps |
| The transparent pass | `draw/batching` | helps |
| Quality presets | `image/quality-settings` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `contact-hardening` | Contact hardening | - |
| `contact-shadows` | Contact shadows | - |
| `depth-range-pyramid` | Depth range pyramid | - |
| `edge-aware-blur` | Edge-aware blur | Bilateral filter |
| `pcss` | PCSS | - |
| `screen-space-shadow-mask` | Screen-space shadow mask | - |
| `tent-filter-light` | Tent filter (light) | - |
| `umbra` | Umbra | penumbra |
