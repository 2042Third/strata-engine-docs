# Brief: `image/exposure`

| Field | Value |
| --- | --- |
| Title | Exposure: camera, eye and meter |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `gpu/compute`, `gpu/coordinates`, `light/measuring-light`, `image/why-post` |
| From | render-image ch. 2; 1.2 (the camera exposure and EV100, histogram metering, percentiles, center weighting, adaptation, the key, the debug views) |
| Unit | `plan/allocation/image.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `image/exposure` — Exposure: camera, eye and meter

**Covers.** The job: turn the light of the HDR image into the multiplier M that the tone mapping applies, set by hand or
measured. The page starts from the camera: exposure, EV and stops, EV100, middle gray and the gray card, the
reflected-light meter's constant K = 12.5 and "sunny 16". Then Strata's model, with no hidden factor: M = 2^Exposure,
and the conversion Exposure ≈ 0.5 − EV100 with the guide's table (MinEV and MaxEV are EV100 − 3). The sweep
`render-image:486` shows manual exposure at −16, −14 and −12 on a sunlit sample. The full section "The problem and how
engines solve it" follows: metering by the average of log luminance from a mip chain against a histogram; average,
center-weighted and spot weights; percentile windows; adaptation speeds. Then the map (`Histogram.comp` →
`Exposure.comp` → the exposure buffer → the tone map; the CPU's `UpdateExposure`; the readback that feeds the
pre-exposure, named only) and a toy: a CPU histogram of log2 luminance, a percentile-clipped mean and an exponential
smoothing step, in about 40 lines.

The real code, in the order data flows: code #5 bins luminance (NaN goes to bin 0 by a negated comparison, black is
ignored); code #6 is a compute shader with group-shared bins, `InterlockedAdd` and the center-weighted weight; code #7
holds the percentile window, the asymmetric adaptation and the key; code #8 is the CPU side, with steps that do not
depend on the frame rate and are capped at 0.25 s (`StepSeconds`), the clamps, and the explicit barrier between two
dispatches through one binding set. The exposure key gets its own section: the gray card facing the sun, k = clamp(key
(a − log2 Lref), −2, 0), and why it only darkens; `render-image:488` shows `lookdev.room` at key 0 and 0.12. Then the
reset and jump on a scene change, the min and max EV (a real sun needs automatic exposure with MaxEV 16: a sunlit scene
meters around EV 15, and files that store 0.5.0's default of 12 keep it and clip), and the luminance view as the way to
judge exposure (`render-image:489`; the view's mechanism is `light/measuring-light`'s). More figures: `render-image:487`
(automatic exposure off and on, Average against CenterWeighted), `render-image:490` (leaving an interior at light speed
3 and 0), diagram `render-image:448` (the histogram with its window and the weight map). How it is tested: the exposure
cases of `GPU.SceneRenderer.PostProcess` (average to middle gray, the black background, light faster than dark, center
weighting, the key). Changing it safely: enum values are appended, the barrier stays, tests set `AdaptationSeconds`.
Exercises: find your exposure, interior against exterior, the metering mode traced from the component to the shader
(`new:14`), spot metering. At the end the reader can set a scene's exposure by numbers, say what the meter sees, and add
a metering mode.

**Leaves out.**

- Light units, their conversions and the reference values → `light/units-exposure`
- The luminance view's drawing and its statistics → `light/measuring-light`
- The pre-exposure that the metered value chooses → `image/pre-exposure`
- Sky presets that switch exposure to automatic → `light/sky`
- Exposure as a game maker sets it, in EV stops → `make/lighting`
- The tone curve that follows the exposure → `image/tone-mapping`

**Fit.** `fits`: about 5,900 words against L (5,000). Four excerpts with the toy and six figures take the most words,
then the four exercises; the light units stay on `light/units-exposure`, and the light area's items repeat the page's
model and terms, adding only the MaxEV rule.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-image:322` | concept | home | The camera exposure model: EV100, middle gray, K = 12.5, sunny 16; physical units with camera exposure against arbitrary units; Exposure about 0.5 − EV100; the error of EV in the engine against EV100 (off by 3) |
| `render-image:330` | concept | home | Metering: a histogram of log2 luminance, average, center-weighted and spot weights, percentile windows, ignoring black; the mip-chain average as the older approach |
| `render-image:334` | concept | home | Adaptation and intent: `1 - exp(-dt k)`, light and dark speeds, clamping, "meter everything to gray" against the key |
| `render-image:66` | feature | home | Manual exposure: `PostProcessComponent::Exposure` in EV, registered [−16, 16]; M = 2^Exposure written by the CPU (`SceneRendererPost.cpp:927-935`) |
| `render-image:68` | feature | home | The exposure buffer's four floats (`PostProcessData.h:150-158`) and the histogram's range (`Exposure.slang:1-21`) |
| `render-image:77-95` | feature | home | The luminance histogram; the metering modes; the percentile window; the adaptation speeds with `StepSeconds` and `c_MaxStepSeconds`; the min and max EV; the exposure key and its gray card (`SceneRenderer.cpp:3609-3616`); reset and jump on a scene change (`GameRenderer.cpp:103-121`); the EV100 conversion and its table |
| `render-image:399` | code | home | `Strata/shaders/Include/Exposure.slang:23-37`: log-luminance binning, NaN to bin 0 by a negated comparison |
| `render-image:400` | code | home | `Strata/shaders/PostProcess/Histogram.comp.slang:39-71`: a compute shader with group-shared bins and atomics; the center-weighted weight |
| `render-image:401` | code | home | `Strata/shaders/PostProcess/Exposure.comp.slang:40-98`: the percentile-window weighted mean, the asymmetric adaptation, the key, the multiplier |
| `render-image:402` | code | home | `Strata/src/Strata/Renderer/SceneRendererPost.cpp:921-976`: the CPU side, with frame-rate-independent adaptation, clamped parameters and the explicit barrier between two dispatches through one binding set |
| `render-image:531`, `render-image:533` | rule | home | Adaptation does not depend on the frame rate and a pause is capped; the exposure key only darkens, and why |
| `render-image:540` | rule | home | NVRHI places barriers only when binding sets change: the histogram and then the exposure need `setBufferState` and `commitBarriers` (`SceneRendererPost.cpp:970-972`) |
| `render-image:448` | figure | home | Diagram: 256 bins over log2 [−12, 16], bin 0 excluded, the window, the weighted mean; the center weight map |
| `render-image:486-490` | figure | home | The sweep of manual exposure; automatic exposure off and on with Average and CenterWeighted; the key at 0 and 0.12; the luminance view (the page's debug view); the adaptation sequence |
| `render-image:587`, `render-image:589` | hands-on | home | Exercises: find your exposure from `renderStats.exposure.ev100`; an interior and an exterior under key 0, 0.12 and 0.3 |
| `render-image:613` | hands-on | home | Exercise: an appended `ExposureMetering::Spot` with its GPU test |
| `new:14` | hands-on | home | Exercise (trace it yourself): follow `AutoExposureMetering` with a search or a debugger from its registration through `UpdateExposure`, which writes it into the histogram's parameters, to `MeteringWeight` in the histogram shader; the solution names each file and function, the path that the Spot exercise extends. Evidence: `Strata/src/Strata/Renderer/RendererComponents.cpp:570`; `Strata/src/Strata/Renderer/SceneRendererPost.cpp:959`; `Strata/shaders/PostProcess/Histogram.comp.slang:42-64` |
| `render-image:644-652` | term | home | Exposure, EV and stop; EV100; middle gray; exposure compensation; metering; percentile window; light and dark adaptation; exposure key; gray card |
| `render-image:655` | term | home | Histogram |
| `render-direct:102` | feature | home | The light area's statement of the same exposure model: M = 2^Exposure by hand, M = 2^Exposure · 0.18 / 2^a · 2^k when metered, EV100 = log2(L) + 3, Exposure about 0.5 − EV100 |
| `render-direct:293` | concept | home | Exposure and EV100 as the light area frames them: fixed exposure, eye adaptation from an average, camera EV settings; the error of clipping a real sun with MaxEV 12. Its pre-exposure half is used on `image/pre-exposure` |
| `render-direct:624` | rule | home | A real sun needs automatic exposure with MaxEV 16: a sunlit scene meters around EV 15; files that store 0.5.0's default of 12 keep it (`Docs/DeveloperGuide.md:5384-5386`) |
| `render-direct:699-701` | term | home | EV100, middle gray and exposure key, in the light area's words |
| `render-image:426` | code | use | `StepSeconds` (`SceneRendererPost.cpp:79-87`), one of the short snippets, quoted inline |
| `render-image:396` | code | use | The key's reference, the gray card facing the light (`SceneRenderer.cpp:3609-3616`), from the orchestration |
| `render-image:101` | feature | use | The luminance view read to judge exposure; its home is `light/measuring-light` |
| `render-image:97` | feature | use | Lux, candela and nits feeding exposure; their home is `light/units-exposure` |
| `render-image:99` | feature | link | Sky presets that turn manual exposure automatic and raise MaxEV; `light/sky` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Light units: radiometric and photometric quantities, conversions, reference values | `light/units-exposure` | must |
| Why images need post-processing; the post chain, `PostSource` | `image/why-post` | must |
| Powers and logarithms: EV stops | `basics/numbers` | must |
| Blending and smoothing: exponential smoothing | `basics/math-interpolation` | must |
| Compute shaders: dispatches, thread groups, shared memory, atomics, UAV barriers | `gpu/compute` | must |
| Color: luminance as a weighted sum of linear Rec. 709 values | `basics/color` | must |
| Measuring light: the luminance view and its statistics | `light/measuring-light` | must |
| Readback | `gpu/readback-timing` | helps |
| Frame time; unscaled and real time | `core/time` | helps |
| Lights: the sun | `light/lights` | helps |
| Running an editor command from a line to paste (the exercises) | `start/how-to-read` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `ev100` | EV100 | - |
| `exposure` | Exposure | EV |
| `exposure-compensation` | Exposure compensation | - |
| `exposure-key` | Exposure key | - |
| `gray-card` | Gray card | - |
| `histogram` | Histogram | - |
| `light-dark-adaptation` | Light/dark adaptation | - |
| `metering` | Metering | - |
| `middle-gray` | Middle gray | - |
| `percentile-window` | Percentile window | - |
