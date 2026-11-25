# Brief: `light/atmosphere`

| Field | Value |
| --- | --- |
| Title | Earth's atmosphere and aerial perspective |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `light/sky`, `gpu/compute` |
| From | new; split from `light/sky`, which held two chapters: render-direct 1.8 (atmosphere rows), 1.9 (aerial perspective), concept 20; home of participating media (extinction, transmittance, phase functions) |
| Unit | `plan/allocation/light.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `light/atmosphere` — Earth's atmosphere and aerial perspective

**Covers.** The job: compute Earth's sky, the sun's color at the ground and the haze of distance from the physics of
air. First the home of participating media, from zero: extinction, scattering and absorption, optical depth,
transmittance (the Beer-Lambert law), phase functions (Rayleigh's, and Henyey-Greenstein's for aerosols), single against
multiple scattering, and why engines precompute tables (Bruneton 2008, Hillaire 2020). Strata's model: Earth's Rayleigh,
Mie and ozone, the ground at y = 0, radii of 6,360 and 6,460 km, and the tables (transmittance 256 x 64, multiple
scattering 32 x 32, sky view 192 x 108; the tables diagram with their axes and readers). The sky light's own atmosphere
fields, as `GetMedium` reads them and kept finite: `AtmosphereDensity` scales the air and the aerosols, `AtmosphereHaze`
the aerosols once more, `GroundAlbedo` is the light the ground sends back into the sky, and `AerialPerspectiveScale`
above 1 gives small worlds the haze of large ones. The code in data order: the extinction profiles and a midpoint
quadrature in double on the CPU; how the multiple-scattering table is computed (after the first bounce the light is
taken to arrive equally from every direction; the second order is gathered over a sphere of 64 directions, the ground's
reflection included; every higher order is f times the one before, so all of them sum to the second order over (1 - f),
the idea that makes Hillaire's model cheap); one integration segment of single and multiple scattering and the quadratic
step distribution of the sky-view table; the sun's color through the air, computed in double and faded by the share of
the disk above the horizon, so the light's intensity is the sun above the air (the mistake of dimming it twice); the
storage scale of 2^14 that keeps twilight out of half-float subnormals, and the readers that multiply by
`EnvironmentParams.x`; the environment refresh, double-buffered in 14 steps once the sun moved 0.5 degrees (a state
diagram); the background with the analytic sun disk as illuminance over solid angle; aerial perspective: a 32 x 32 x 32
froxel volume of in-scattering and transmittance per frame, slices at D ((k + 0.5) / 32)^2, two fetches per pixel,
applied before height fog. A toy computes the optical depth of one ray in 30 lines. Figures: times of day as a sweep of
the sun's elevation (60, 20, 6, 0 and -6 degrees) with the ground's illuminance; aerial perspective off and on and its
scale 1 against 6. How it is tested: `GPU.Atmosphere` (the GPU table against the CPU within 1%, a night sky without
bands, no daytime clamp), the aerial perspective tests. The exercises evaluate the transmittance at sunset on the CPU
and compare it with `SceneRendererStats::SunTransmittance`, and trace a change of `AtmosphereHaze` to the tables
computed again. Afterwards the reader can explain the atmosphere's tables, why the sun's intensity is above the air, and
what aerial perspective adds.

**Leaves out.**

- The sky's sources and presets → `light/sky`
- Height fog → `light/fog`
- The atmosphere's environment cube in the filter chain → `indirect/ibl`
- Marching through volumes for global illumination → `indirect/gi-cascades`
- The pre-exposure → `image/pre-exposure`
- A day cycle in a game → `make/reflections`

**Fit.** `fits`: about 5,800 words against L (5,000). Participating media from zero, five excerpts and multiple
scattering made cheap take the most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-direct:154-158` | feature | home | The physical atmosphere, with the sky light's atmosphere fields where the page presents the model (`GetMedium`, settings kept finite: `AtmosphereDensity` scales the air and the aerosols, `AtmosphereHaze` the aerosols once more, `GroundAlbedo` the light the ground sends back into the sky; `Strata/src/Strata/Renderer/RendererComponents.h:110-123`, `Strata/src/Strata/Renderer/Atmosphere.h:50-59`, `Strata/src/Strata/Renderer/SceneRendererAtmosphere.cpp:224-226`), the sun's color through the air, the storage scale, the environment refresh, the background |
| `render-direct:170` | feature | home | Aerial perspective: the froxel volume, its slices, before height fog; `AerialPerspectiveScale` above 1 gives small worlds the haze of large ones |
| `new:51` | concept | home | Multiple scattering made cheap, about 150 words: after the first bounce the light is taken to arrive equally from every direction; the second order is gathered over a sphere of directions, the ground's reflection of the sun included; the same gathering of a light that is 1 everywhere gives the share f that scattering returns, and every higher order is f times the one before, so all of them sum to the second order over (1 - f). Evidence: `Strata/shaders/IBL/AtmosphereMultipleScattering.comp.slang:5-10` |
| `render-direct:402` | concept | home | Participating media and the physical atmosphere; the mistakes |
| `render-direct:463` | code | home | `Strata/src/Strata/Renderer/Atmosphere.cpp:18-33`: extinction profiles and the distance to the top; with 61-101, the midpoint transmittance and the sun's transmittance with the disk's share |
| `new:52` | code | home | `Strata/shaders/IBL/AtmosphereMultipleScattering.comp.slang:18-81`: the multiple-scattering table, per height and sun height: 8 rings by 8 sectors of directions, 20 steps along each, the single scattering toward the point with an even phase and the ground's diffuse reflection of the sun (the second order), the transfer f gathered beside it, and all orders summed as the second over (1 - f), stored times the storage scale; with 5-10, the idea in the file's comment (the finding's 18-92 holds the entry point's boilerplate from 83 on) |
| `render-direct:464` | code | home | `Strata/shaders/Include/AtmospherePass.slang:73-89`: one segment of single and multiple scattering; with `Strata/shaders/IBL/AtmosphereSkyView.comp.slang:16-51`, the quadratic steps |
| `render-direct:465` | code | home | `Strata/shaders/Scene/Skybox.frag.slang:12-50`: the sky background, the sun's disk as illuminance over solid angle, the fogged sky, the pre-exposure |
| `render-direct:467` | code | home | `Strata/shaders/Include/AerialPerspective.slang:17-26`: reading the froxel volume with a quadratic depth mapping |
| `render-direct:511-513` | figure | home | Diagrams: the atmosphere's tables; the environment refresh as a state machine |
| `render-direct:556` | figure | home | Sweep: times of day by `lighting.applySkyPreset {sunElevation}`, with `groundIlluminance` |
| `render-direct:559` | figure | home | Aerial perspective off and on, its scale 1 against 6 (Open World's mountains) |
| `render-direct:575` | rule | home | The sun's intensity is above the atmosphere under the Atmosphere source |
| `render-direct:618` | rule | home | Atmosphere table readers multiply by `EnvironmentParams.x` |
| `render-direct:664` | hands-on | home | Exercise: the transmittance at sunset on the CPU against `SceneRendererStats::SunTransmittance` |
| `new:53` | hands-on | home | Exercise (trace it yourself): a change of `AtmosphereHaze` followed with a debugger through `UpdateAtmosphere`: the settings kept finite, the transmittance and multiple-scattering tables dispatched again (counted in `AtmosphereTableUpdates`), the sky view, and the sun's transmittance computed again from `GetMedium`. Evidence: `Strata/src/Strata/Renderer/SceneRendererAtmosphere.cpp:195`, `:224-226`, `:232`, `:246-253`, `:341-344` |
| `render-direct:692` | term | home | The Beer-Lambert law (`light/clearcoat-transmission` links it) |
| `render-direct:744-752` | term | home | Physical atmosphere, Rayleigh and Mie scattering, ozone absorption, extinction, optical depth and transmittance, phase function and Henyey-Greenstein, single and multiple scattering, the tables, aerial perspective, storage scale |
| `render-direct:754` | term | home | In-scattering |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The sky light and its sources | `light/sky` | must |
| Compute shaders | `gpu/compute` | must |
| The exponential function and the number e | `basics/numbers` | must |
| Accumulating small steps | `basics/math-change` | must |
| The geometric series and its sum | `basics/math-interpolation` | must |
| Solid angle and directions on a sphere | `basics/math-sphere` | must |
| Lux and nits | `light/units-exposure` | must |
| Half-float subnormals | `basics/numbers` | must |
| 3D textures and trilinear filtering | `gpu/how-a-gpu-frame-works` | helps |
| The pre-exposure | `image/pre-exposure` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `aerial-perspective` | Aerial perspective | - |
| `beer-lambert-law` | Beer-Lambert law | - |
| `extinction` | Extinction | - |
| `henyey-greenstein` | Henyey-Greenstein | - |
| `in-scattering` | In-scattering | - |
| `lut` | LUT | - |
| `mie-scattering` | Mie scattering | - |
| `multiple-scattering` | multiple scattering | - |
| `optical-depth` | optical depth | - |
| `ozone-absorption` | Ozone absorption | - |
| `phase-function` | Phase function | - |
| `physical-atmosphere` | Physical atmosphere | - |
| `rayleigh` | Rayleigh | - |
| `single` | Single | - |
| `storage-scale` | Storage scale | - |
| `transmittance-light` | transmittance (light) | - |
