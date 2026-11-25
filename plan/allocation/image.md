# Allocation: image

## `image/why-post` — Why images need post-processing, and Strata's post chain

**Covers.** The page opens on one frame shown twice: the HDR image put on the screen as it is (Tonemapper None,
Exposure 0: a white, clipped sky) and the same frame after Strata's chain (`render-image:485`). From it the reader
learns, in this order: a frame is an array of numbers, and the renderer's numbers are light in nits, not display codes;
why rendering straight to 8-bit values and clamping breaks (the sky, the sun, light that spans about ten orders of
magnitude), and why LDR with gamma tricks does not save it; the idea of an HDR
target followed by a chain of full-screen passes; the formats engines choose (R11G11B10F, RGBA16F, RGBA32F), with their
range, precision and cost in one table; and Strata's choice, an RGBA16F target that holds luminance times a power-of-two
pre-exposure and is kept finite by `SanitizeHDR` (one sentence each, linking `light/brdf` and `image/pre-exposure`).

Then the chain itself, as diagram `render-image:437` draws it: the TAA resolve, depth of field, motion blur, exposure,
bloom with the lens flare between its downsamples and upsamples, tone mapping, FXAA or the morphological AA, and the
overlays. The page says why this order holds (temporal and geometric effects work on linear light first, metering comes
after them, spatial anti-aliasing works on display values last), what `PostSource` is (the one texture the chain reads
this frame), and which frames end with the HDR image (`HDROutput`, the probe bake). Code #1, the overview comment of
`SceneRendererPost.cpp`, gives the chain in the engine's words; a few lines of code #2 show the source switching (the
whole block is walked in `image/tutorial-post-effect`). The machinery is named once: `DrawFullscreen` and `Copy.frag`,
with one linking sentence each for the fullscreen triangle (`gpu/coordinates`) and the cached fullscreen pipelines
(`gpu/binding`), the four GPU stages, the CPU twins of `PostProcessMath` (one sentence). The Post Process component
holds every setting of the chain, and the first active one in the scene applies, so Strata has no post-process volumes
(`new:1`). When a pass cannot make its resources, the chain goes on without it (`new:31`): depth of field, motion blur
and the lens flare are skipped, the morphological AA falls back to FXAA, the lookup and the flare bind dummies, and the
error is logged once while frames stay degraded. Common mistakes: reading 1.0 as white, expecting a doubled value to
look twice as bright, lighting or tone mapping sRGB-encoded values, ignoring the half-float limits (65,504 at most,
subnormals below 2^-14). At the end the reader can name every pass of the chain, say what each reads and writes, and say
which pass to look at when an image is too dark, banded or jagged. The exercise turns the chain's effects off one at a
time and predicts each picture (`new:13`). Each later page of the part takes one pass.

**Leaves out.**

- `SanitizeHDR`'s code, and why every HDR writer calls it → `light/brdf`
- Metering and the exposure multiplier → `image/exposure`
- How the pre-exposure is chosen and divided out → `image/pre-exposure`
- The pass order of the whole frame, before the post chain → `gpu/frame-tour`
- How motion vectors are made → `draw/motion-vectors`
- The orchestration code of `RenderFrame`, walked line by line → `image/tutorial-post-effect`
- Every property of the Post Process component with its range and default → `reference/components`
- The statistics the chain reports (`renderStats`) → `reference/renderer`
- Using the post effects in a game → `make/look`

**Fit.** `fits`: about 3,600 words against M (3,000). The concepts taught from zero (a frame as numbers, why clamping
breaks, the HDR formats) and the chain's order with code #1 take the most words; code #2 is a few lines here and is
walked whole in `image/tutorial-post-effect`, and the CPU twins are taught in `image/tone-mapping`.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-image:313` | concept | home | A frame is an array of numbers, and light is not color; the newcomer's errors (1.0 is not white, double the value is not twice as bright) |
| `render-image:318` | concept | home | HDR formats as a choice: R11G11B10F, RGBA16F, RGBA32F, scaling; one NaN spreading through bloom and TAA as the reason for the rules (the half-float bits are `basics/color`'s) |
| `render-image:27` | feature | home | The HDR scene color target: RGBA16F (`c_HDRFormat`), luminance times the frame's pre-exposure, `GetHDRTexture` |
| `render-image:38` | feature | home | The chain's order; `PostSource` {HDR, History, DepthOfField, MotionBlur} and `SelectPostSet` (`SceneRendererPost.cpp:441-456`); the orchestration in `RenderFrame` named |
| `render-image:44` | feature | home | `HDROutput` frames: the reflection-probe bake ends with the HDR image and runs no post pass |
| `render-image:46` | feature | home | The fullscreen pass as the post chain uses it: `DrawFullscreen` and `Copy.frag` for the overlays' copy; the triangle without a vertex buffer and `GetFullscreenPipeline` are named in one linking sentence each (their homes are `gpu/coordinates` and `gpu/binding`) |
| `render-image:55` | feature | home | The chain's GPU stages: `GPU.TAA`, `GPU.DepthOfField`, `GPU.MotionBlur`, `GPU.Post` |
| `render-image:268` | feature | home | The Post Process component: one component for the whole chain, its inspector sections, inactive reasons, the first active entity wins (`GetPostProcessSettings`) |
| `render-image:395` | code | home | `Strata/src/Strata/Renderer/SceneRendererPost.cpp:22-31`: the post chain in the engine's words, from the HDR image to the display; post passes take no `FrameConstants` fields |
| `render-image:437` | figure | home | Diagram: the post chain's data flow in one frame, with the GPU stages marked |
| `render-image:485` | figure | home | The problem picture, the chain off and on: Tonemapper None with Exposure 0 against Filmic; the clipped sky |
| `render-image:634-636`, `render-core:754` | term | home | HDR image; LDR and display-referred; scene-linear, display-linear and encoded; one entry with the renderer core's "HDR, tone mapping, sRGB encoding" (passed by `gpu`), whose tone mapping links `image/tone-mapping` |
| `render-image:723` | term | home | Post source |
| `render-image:724` | term | link | The fullscreen triangle, named in one linking sentence; its home is `gpu/coordinates` |
| `new:1` | not-done | home | No post-process volumes: the first active Post Process component applies, with no shape and no blending. Evidence: `Strata/src/Strata/Renderer/SceneRenderer.cpp:1447-1455` (`GetPostProcessSettings` returns the first active one), run again at the pin |
| `new:31` | feature | home | The chain's failure path: an effect whose resources cannot be made is skipped and the frame is drawn without it (depth of field, motion blur, the lens flare); the morphological AA falls back to FXAA; the color lookup and the flare bind dummies; the error is logged once and stays while frames are degraded, and is cleared by the first frame drawn whole. Evidence: `Strata/src/Strata/Renderer/SceneRenderer.cpp:3181, 3588-3606, 3747-3748`; `Strata/src/Strata/Renderer/SceneRendererPost.cpp:1073, 1261-1263, 1280-1282`; `Strata/src/Strata/Renderer/SceneRenderer.h:1621-1622, 1651, 2050` |
| `new:13` | hands-on | home | Exercise (predict, then run): on a copy of a sample, turn the chain's effects off one at a time with `component.set` on the Post Process (Bloom, then AntiAliasing, then AutoExposure with Exposure 0, last Tonemapper None), predict before each `viewport.capture` which pass's output changes and how, and end on the page's problem picture. Evidence: `Strata/src/Strata/Renderer/RendererComponents.h:263-298` (the fields); `StrataEditor/src/Editor/EditorViewportCommands.cpp:1211` (`viewport.capture`) |
| `render-direct:287` | concept | home | Linear color, HDR targets and the floating-point range as the light area frames them: light over ten orders of magnitude, LDR with gamma tricks against float targets, Strata's RGBA16F target; the errors of lighting on sRGB values, ignoring the half-float limits and letting a NaN spread (`SanitizeHDR` stays `light/brdf`'s, the half-float bits `basics/color`'s) |
| `render-image:396` | code | use | The source switching of `RenderFrame` (`SceneRenderer.cpp:3582-3607`), a few lines; its home is `image/tutorial-post-effect` |
| `render-image:53` | feature | use | One sentence: the shaders' math has CPU twins for tests; `image/tone-mapping` teaches the pattern |
| `render-image:30` | feature | link | `SanitizeHDR`, named in one sentence; its home is `light/brdf` |
| `render-image:70` | feature | link | The pre-exposure, named in one sentence; its home is `image/pre-exposure` |
| `render-image:57` | feature | link | The chain reports its state in `renderStats`; the keys are `reference/renderer`'s |
| `render-core:176` | feature | use | The post block's place in the frame's pass order, as `gpu/frame-tour` gives it |
| `render-core:139` | feature | link | The fullscreen triangle and its UVs, in one linking sentence; `gpu/coordinates` |
| `render-core:95` | feature | link | The fullscreen pipelines cached per framebuffer (`GetFullscreenPipeline`), in one linking sentence; `gpu/binding` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| How surfaces reflect light: radiance and irradiance in use | `light/reflectance` | must |
| Light units: nits and lux | `light/units-exposure` | helps |
| Color: linear and sRGB values, the sRGB transfer function, the half-float range | `basics/color` | must |
| Binary, integers, floating point, precision and rounding | `basics/numbers` | must |
| How a GPU works and draws a frame: render targets, pixels as samples, frames in flight | `gpu/how-a-gpu-frame-works` | must |
| Forward, deferred and visibility buffers; the frame's scene passes; a feature that is off is invisible bit for bit | `gpu/frame-tour` | must |
| The HDR target, half-float limits, `SanitizeHDR` | `light/brdf` | must |
| Compute shaders: dispatches | `gpu/compute` | helps |
| The fullscreen triangle and its UVs | `gpu/coordinates` | helps |
| Fullscreen pipelines cached per framebuffer | `gpu/binding` | helps |
| Readback and GPU timestamps and stages | `gpu/readback-timing` | helps |
| Reflection: one registration, many uses (the component's sections and inactive reasons) | `world/reflection` | helps |
| Motion vectors and motion history | `draw/motion-vectors` | helps |
| Running an editor command from a line to paste (the exercise) | `start/how-to-read` | helps |

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

## `image/pre-exposure` — Pre-exposure

**Covers.** The job: keep HDR values inside the half-float range without changing the image. One sentence names the
design decision this page is the mechanism of, "Light is measured in real units, and a pre-exposure keeps the HDR values
in range", and links back to its `:::why` aside on `light/units-exposure`. The problem: a 100,000 lux
sun and its disk give values far above 65,504. The approaches, in one short section that links `image/exposure`: scale
by the previous frame's exposure (Frostbite), or by a fixed scale. Strata multiplies every HDR write by a power of two P
(`FrameConstants::TemporalParams.y`), and every reader divides it out: the histogram and the bloom threshold, the tone
map with M/P, the TAA history rescaled by P/P_prev. The page teaches why a power of two is exact (it only moves the
exponent, so a change of P changes no pixel), why the exposure is never read back synchronously, and the hysteresis that
changes P only when it is more than a stop off, with 2 stops of headroom and a range of 2^±24. The map is diagram
`render-image:444` (frames N, N+1, N+2: metering on the GPU, the readback ring, the step, the history's rescale); the
states are diagram `render-image:446` (manual, automatic, held for the value views, reset; settled).

The toy chooses P from the last metered value in about 20 lines. The real code: code #4 (`GetPreExposureFor`,
`StartPreExposureEpoch`, `ChoosePreExposure`), the ring of `BufferReadback`s that brings the metered value back frames
later, and the history's rescale in `ResolveTemporal`; `SceneRenderOptions::PreExposure` forces a value, and
`viewport.capture` and the project's picture wait, at most 8 frames, for a settled pre-exposure. The page changes no
image by design: it has the two diagrams and a text capture of the statistics (`PreExposure`, `PreExposureSettled`),
and no rendered figure (the exemption of `outline-3.md`). How it is
tested: the cases of `GPU.SceneRenderer.PostProcess` ("The pre-exposure is a power of two that changes no image", the
100,000 lux sun that reaches no clamp, settling after a reset, the history that follows a step without a flash). The
exercises reproduce the bit-identity case with two forced pre-exposures and trace every pass that multiplies or divides
by P (`new:15`). At the end the reader can say why the image
never changes when P does, and where a new HDR writer must multiply and a new reader must divide.

**Leaves out.**

- The paragraph on why the HDR target needs a pre-exposure, in light units → `light/units-exposure`
- How the forward shader writes HDR values with P → `light/brdf`
- Value views, written without the pre-exposure → `light/measuring-light`
- The TAA history beyond its rescale → `image/taa`
- The pre-exposure of the reflection-probe bake → `indirect/probes`
- How `BufferReadback` works → `gpu/readback-timing`

**Fit.** `fits`: about 3,700 words against M (3,000). One long excerpt (code #4, 85 lines) with two shorter quotes, two
diagrams and two exercises take the most words; there is no rendered figure to describe, and the light area's items add
one clause on who waits for a settled pre-exposure.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-image:326` | concept | home | Why a pre-exposure; the approaches; Strata's power of two from readbacks, 2 stops of headroom, change only beyond a stop, epochs, exact rescale; the errors (a factor that is no power of two, a synchronous readback) |
| `render-image:70` | feature | home | Writers multiply, readers divide; `ChoosePreExposure`, `GetPreExposureFor`, headroom and range (`SceneRenderer.h:991-996`), the readback ring (`SceneRendererPost.cpp:978-997`), epochs, the forced value (`SceneRenderer.h:421-424`); the rescale in `ResolveTemporal` (`SceneRenderer.cpp:1694`) |
| `render-image:398` | code | home | `Strata/src/Strata/Renderer/SceneRenderer.cpp:1514-1598`: `GetPreExposureFor`, `StartPreExposureEpoch` and `ChoosePreExposure`, a power of two chosen from asynchronous readbacks with hysteresis and epochs |
| `render-image:527-529` | rule | home | The pre-exposure is a power of two and is divided out exactly; the exposure is never read back synchronously |
| `render-image:444`, `render-image:446` | figure | home | Diagrams: the exposure timeline over frames; the exposure state machine |
| `render-image:616` | hands-on | home | Exercise: prove the pre-exposure exact with two forced values |
| `new:15` | hands-on | home | Exercise (trace it yourself): a search for `InversePreExposure` and `TemporalParams.y` finds every reader that divides the pre-exposure out (the histogram, the bloom's threshold, the TAA's luminance weights, the tone map), where the CPU writes it, and the writers that multiply by it; the reader says which list a new HDR pass joins. Evidence: `Strata/shaders/PostProcess/Histogram.comp.slang:63`; `Strata/shaders/PostProcess/Bloom.comp.slang:118`; `Strata/shaders/PostProcess/TAA.comp.slang:240`; `Strata/shaders/PostProcess/Tonemap.frag.slang:87`; `Strata/src/Strata/Renderer/SceneRendererPost.cpp:951, 1016, 1233`; `Strata/shaders/Scene/Forward.frag.slang:465`; `Strata/shaders/Scene/Skybox.frag.slang:50` |
| `render-image:653` | term | home | Pre-exposure |
| `render-direct:103` | feature | home | The light area's entry for the same pre-exposure: P in `FrameConstants::TemporalParams.y`, so that a 100,000 lux sun and its disk fit in half floats; the headroom and range constants; the HDR writers of the forward pass and the sky named (their lines are `light/brdf`'s) |
| `render-direct:104` | feature | home | Settled pre-exposure: `viewport.capture` and the project's picture wait, at most 8 frames, for a readback drawn with the current P (`SceneRendererStats::PreExposureSettled`, `Strata/src/Strata/Renderer/SceneRenderer.h:695-699`) |
| `render-direct:468` | code | home | `Strata/src/Strata/Renderer/SceneRenderer.cpp:1531-1598`: `ChoosePreExposure` alone, the light area's listing of the excerpt; the page shows it as the end of code #4 (`render-image:398`), after the two helpers |
| `render-direct:577` | rule | home | Every HDR writer multiplies by the pre-exposure and every reader divides it out; a pass that forgets either is wrong only when P is not 1, in daylight scenes |
| `render-direct:702` | term | home | Pre-exposure, in the light area's words |
| `render-image:654` | term | use | Readback, here over a ring of buffers; its home is `gpu/readback-timing` |
| `render-direct:293` | concept | use | The light area's concept's pre-exposure half: the error of thinking a pre-exposure changes the image; its home is `image/exposure` |
| `render-direct:580` | rule | use | Value views are written without pre-exposure (the held state of the diagram) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Camera exposure, EV100, metering | `image/exposure` | must |
| Binary, floating point and precision: exponent and significand | `basics/numbers` | must |
| The half-float range | `basics/color` | must |
| Readback and GPU timestamps | `gpu/readback-timing` | must |
| How a GPU draws a frame: frames in flight | `gpu/how-a-gpu-frame-works` | must |
| Why images need post-processing; the HDR target and the post chain | `image/why-post` | must |
| Light in real units; the paragraph on why the HDR target needs a pre-exposure | `light/units-exposure` | helps |
| Temporal anti-aliasing: the history (only its rescale is used) | `image/taa` | helps |
| The forward shader that writes HDR values | `light/brdf` | helps |

## `image/tone-mapping` — Tone mapping and the Filmic curve

**Covers.** The job: map exposed light, from 0 to far above 1, to display values in [0, 1], keeping the mid-tones and
rolling off the highlights. The page starts with the tone curves plot (diagram `render-image:450`): the S-curve of film,
with its toe, its linear part and its shoulder, on a log axis in stops from middle gray. The full section "The problem
and how engines solve it" follows: Reinhard, Hable, ACES with Hill's fit, AgX, Khronos PBR Neutral and the GT
tonemapper, each from the flaw of the one before; per-channel curves and hue skew against luminance curves (diagram
`render-image:452`); gamut compression with inset and outset matrices. Strata keeps five operators (`TonemapOperator`,
whose values are only appended) and adds its own Filmic, fitted offline by `Tools/FitFilmic.py` against stated targets:
a luminance-scaled toe, a per-channel shoulder blended by stops, middle gray kept. The figures: `render-image:491` (one
shot under the six curves, None as the off, ACES at +0.8 EV, saturated lanterns that show hue skew) and the sweep
`render-image:493` (Toe and Shoulder at 0, 0.5 and 1).

The map is the tone-mapping pass itself, the frame's one display pass: diagram `render-image:442` and code #12, walked
as a skeleton (chromatic aberration, exposing with `ExposeSceneColor` and its clamp, TAA sharpening, bloom, flare,
vignette, white balance and grading, contrast, the curve, saturation, sRGB encoding, the color lookup, grain and
dither). Later pages zoom into their own lines. The contract: `TonemapConstants` is a volatile constant buffer of 176
bytes, because the parameters outgrew NVRHI's 128 bytes of push constants, and it grows only by appending vec4-aligned
blocks that static_asserts check; the operators' values are file and script API; the Filmic constants are generated and
never edited by hand. The toy is Reinhard and a simple filmic curve. The real code: code #11 (the classic operators side
by side), code #9 (Filmic's curve and operator), code #10 (its CPU twin, and the pattern of CPU twins in
`PostProcessMath` that the tests compare with). Contrast works in log space before the curve and saturation after it;
a short table gives middle gray's display value under each curve. How it is tested: `Renderer.PostProcessMath`, the
contrast case of `GPU.SceneRenderer.PostProcess`, `FitFilmic.py --check`. Exercises: pick a tone curve, add a debug
curve after tracing the operator from the component to the shader's switch (the trace exercise), write a CPU-twin
test, refit Filmic. At the end the reader can choose and defend a curve and change Filmic
without breaking its targets.

**Leaves out.**

- White balance, grading and the color lookup → `image/grading`
- sRGB encoding, dither and grain → `image/encoding`
- Bloom, vignette, flares and chromatic aberration → `image/lens-effects`
- TAA's sharpening, which runs in this pass → `image/taa`
- Committed generators as a workflow of the build → `engineering/generated-code`
- Choosing a curve in a game → `make/look`

**Fit.** `fits`: about 6,000 words against L (5,000). The operators engines use, four excerpts with the walk of the
whole pass, five figures and four exercises take the most words; the pass's later stages are only named here.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-image:339` | concept | home | Tone mapping: the S-curve, per-channel against luminance curves, hue skew, gamut compression; the operators engines use; the errors (curves on encoded values, ACES darkening middle gray, saturation before the curve) |
| `render-image:106-118` | feature | home | `TonemapOperator` and the shader's switch; Reinhard, ACES, AgX, Khronos Neutral and None; Filmic (`Filmic.slang`, the generated constants, the CPU reference, Toe and Shoulder); contrast and saturation; middle gray's display value per curve |
| `render-image:33` | feature | home | `ExposeSceneColor` and `c_MaxExposedValue` = 1e8 (`Tonemap.frag.slang:72-89`): exposed values clamped before the curves |
| `render-image:51` | feature | home | `TonemapConstants`, a 176-byte volatile constant buffer, and why (`SceneRendererPost.cpp:110-121`) |
| `render-image:53` | feature | home | The CPU twins of `PostProcessMath` (sRGB, the dither's noise, Filmic, white balance, grading, the motion-blur profile) and why tests compare with them |
| `render-image:278` | feature | home | `Tools/FitFilmic.py`: the form and the targets T1 to T9 of its header; `--check`, `--from-committed`, `--rewrite` |
| `render-image:403` | code | home | `Strata/shaders/Include/Filmic.slang:11-40`: the Filmic curve and operator: toe in log-log, shoulder power, inset and outset, the shadow and highlight blend |
| `render-image:404` | code | home | `Strata/src/Strata/Renderer/PostProcessMath.cpp:111-137`: the CPU twin of the curve; how Toe and Shoulder become the curve's parameters, matching slopes at middle gray |
| `render-image:405` | code | home | `Strata/shaders/PostProcess/Tonemap.frag.slang:121-171`: four classic operators side by side (Hill's ACES, AgX, Khronos Neutral; Reinhard in the switch) |
| `render-image:406` | code | home | `Strata/shaders/PostProcess/Tonemap.frag.slang:173-275`: the whole display pass in order, walked as the map of this page and the next three |
| `render-image:538` | rule | home | `TonemapConstants` grows only by appending vec4-aligned blocks: std140 must match the shader byte for byte |
| `render-image:547` | rule | home | Generated constants are never edited by hand; their generators verify the targets (`FitFilmic.py --check`) |
| `render-image:570` | rule | home | Preset numbers and enum values are file and script API: `TonemapOperator`, `RendererQualityPreset`, the anti-aliasing and TAA presets are only appended |
| `render-image:442` | figure | home | Diagram: inside the tone-mapping pass, each stage with its domain (scene-linear exposed, display-linear, encoded) |
| `render-image:450`, `render-image:452` | figure | home | Diagrams: the six curves on a log axis with middle-gray marks and Filmic's Toe and Shoulder variations; hue skew against Filmic's blend |
| `render-image:491`, `render-image:493` | figure | home | The six curves on one shot (None as the off; saturated lights for hue skew); the Toe and Shoulder sweep |
| `render-image:591` | hands-on | home | Exercise: pick a tone curve and describe the hue of a red lamp under each |
| `render-image:609`, `render-image:611` | hands-on | home | Exercises: an appended false-color debug curve, which starts with a trace (the page's "trace it yourself"): `PostProcessComponent::Tonemapper` followed from its registration through `tonemap.Operator` in `RenderPostDisplay` and `TonemapConstants::Operator` at offset 16 to the shader's switch (`RendererComponents.cpp:452`, `SceneRendererPost.cpp:1231`, `PostProcessData.h:25, 116`, `Tonemap.frag.slang:249`); a CPU-twin test of `EvaluateFilmicCurve` |
| `render-image:627` | hands-on | home | Exercise: refit Filmic with a changed target and see which tests move |
| `render-image:656-663` | term | home | Tone mapping, tone curve, operator; toe and shoulder; Reinhard, ACES, AgX, Khronos PBR Neutral; Filmic; inset and outset; hue skew; ICtCp; saturation and contrast |
| `render-image:426` | code | use | `TonemapConstants` with its static_asserts (`PostProcessData.h:19-51`), one of the short snippets |
| `render-image:725` | term | use | Push constants, whose home is `gpu/binding`, and the volatile constant buffer, whose entry is on `gpu/resources-lifetimes` (`render-core:708`; duplicates.md, "Volatile constant buffer") |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Camera exposure and the multiplier M | `image/exposure` | must |
| Why images need post-processing; the HDR target and the post chain | `image/why-post` | must |
| Matrices, transforms and their products | `basics/math-matrices` | must |
| Color: chromaticity, gamut, the working color space, the sRGB transfer function | `basics/color` | must |
| Powers and logarithms: stops | `basics/numbers` | must |
| Pipelines and binding: push constants, constant buffers, std140 layouts | `gpu/binding` | must |
| The volatile constant buffer, written again each frame | `gpu/resources-lifetimes` | helps |
| The shader build: writing and registering a shader | `gpu/shaders` | must |
| One test case, written and run | `core/first-change` | helps |
| Committed generators and their checks | `engineering/generated-code` | helps |
| Reflection: a registered property and its enum values | `world/reflection` | helps |

## `image/grading` — White balance, grading and lookup tables

**Covers.** The job: give the image a white point and a grade on scene-linear light before the curve, and a lookup made
in another tool after it. The page starts from the white balance sweep `render-image:494` (3200, 6500 and 9000 K, tint −1
and +1, on an interior lit by lamps). The full section "The problem and how engines solve it": chromaticity in CIE 1931
xy and CIE 1960 uv, the Planckian and daylight loci and mireds (diagram `render-image:454`), why multiplying RGB by a
color is no adaptation and what von Kries and CAT02 do, the ASC CDL's slope, offset and power, 3D lookup tables with
trilinear reads and the half-texel remap, and grading on scene-linear light against display values. Strata's order:
white balance and slope, offset and power on scene-linear light around middle gray, before the curve; saturation after
the curve; the lookup after the curve, on encoded values, as grading tools assume. The toy is a von Kries adaptation in
LMS and a CDL in about 30 lines.

The real code: code #13 (`GetWhiteBalanceMatrix` by CAT02 in double over the generated locus; `MakeColorGrading`; the
Active flag that keeps the defaults bit-identical), the grading and lookup lines of the tone-mapping pass, and the
`ColorLookup` asset: the `.cube` parser (`new:3`), which rejects a bad file with its line number and can be cancelled,
the Size setting (17, 33, 65 or the file's; a table of another size is resampled), the cooked STLU form, and the
per-frame resolve with dummies, so that the post sets never change while the lookup loads. The rules: neutral settings
render bit-identically; the lookup loads asynchronously and nothing applies until it is there. The figures:
`render-image:495` (slope, offset and power against the defaults, the off and on) and `render-image:496` (the feature
test's `Warm.cube` at 0, 0.5 and 1, from the look-dev shot `tp.lut`). How it is tested: `Renderer.PostProcessMath`,
`Renderer.ColorLookup`, `GPU.SceneRenderer.ColorLookup`, and `Asset.ColorLookupImporter` (`new:33`: malformed files
refused with the line and the reason, resampling exact). The page states the code's names for the lookup's binding set,
not the guide's (`new:2`). Exercises: a night look justified step by step, a LUT made by the reader, and a `.cube` file
traced from the importer to the frame (`new:16`). At the end the reader can grade a scene by numbers, import a lookup
and say where in the pass each control works.

**Leaves out.**

- The tone curve between the grade and the lookup → `image/tone-mapping`
- Encoding the graded values → `image/encoding`
- Import records, settings and background imports in general → `assets/importing`
- Untrusted input as a rule of the asset pipeline → `assets/robustness`
- Chromaticity, white point and D65 from zero → `basics/color`
- Grading a game's look in the editor → `make/look`

**Fit.** `fits`: about 4,800 words against L (5,000). The color science, new to the reader (chromaticity, the loci,
chromatic adaptation, the CDL and 3D lookups), takes the most words, then two excerpts with the pass's lines and the
importer, four figures and three exercises.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-image:349` | concept | home | Color grading and white balance: the loci, mireds, chromatic adaptation, the CDL, 3D lookups and their addressing, scene-linear against display grading; the errors |
| `render-image:123` | feature | home | White balance: temperature (2000 to 15000 K, 6500 neutral) and tint; CAT02 von Kries in double; the locus over `WhiteBalanceLocus.inl`; the cache per key in `GetColorGrading` (`SceneRendererPost.cpp:1335-1348`) |
| `render-image:127` | feature | home | Slope, offset and power on scene-linear light around middle gray; the shader's lines; the skip bit `c_TonemapColorGrading` |
| `render-image:131` | feature | home | The `ColorLookup` asset: cooked STLU, the `.cube` importer and its Size setting, the half-texel sample, the per-frame resolve and the tone mapping's second set with dummies |
| `render-image:280` | feature | home | `Tools/GenerateWhiteBalance.py` → `WhiteBalanceLocus.inl` (91 entries, 60 to 510 mireds) |
| `render-image:407` | code | home | `Strata/src/Strata/Renderer/PostProcessMath.cpp:163-201`: white balance by CAT02 von Kries in double; the grading's composition; the Active flag that makes the defaults bit-identical |
| `new:3` | code | home | `Strata/src/Strata/Asset/ColorLookupImporter.cpp:185-305`: `ParseCubeFile`, a `.cube` file read as untrusted text: keywords before values, `LUT_3D_SIZE` bounds, `DOMAIN_MIN` and `DOMAIN_MAX` against `LUT_3D_INPUT_RANGE`, 1D tables refused, an error with its line number, cancellation every few lines |
| `render-image:545` | rule | home | Neutral settings render bit-identically: grading's Active flag, `ColorLookupIntensity` 0, uniform branches |
| `render-image:577` | rule | home | The color lookup loads asynchronously: nothing applies while it loads, the frame counts it as pending, bindings swap through dummies |
| `render-image:454` | figure | home | Diagram: the Planckian and daylight loci in CIE 1960 uv, the blend from 4000 to 5000 K, the tint normal; CAT02 as a chain of matrices |
| `render-image:494-496` | figure | home | The white balance sweep; slope, offset and power against the defaults (the off and on); the lookup at 0, 0.5 and 1 from the look-dev shot `tp.lut` (`Warm.cube` on the robot at intensity 1, crops of the robot and the sky; 0 and 0.5 set in its setup; `Tools/LookDev/Shots.json:61`) |
| `render-image:593`, `render-image:595` | hands-on | home | Exercises: a night look from the Manual's recipe, each step justified; a LUT exported or written by hand, imported with Size 33, applied at 0.5 |
| `new:16` | hands-on | home | Exercise (trace it yourself): follow a `.cube` file from the importer's call of `ParseCubeFile` to the frame: `ResolveColorLookup` in `RenderFrame`, `GetTonemapInputSet` with its dummies, and the lookup's lines in the tone-mapping shader; the reader says on which frame the lookup first applies and what the frames before it draw. Evidence: `Strata/src/Strata/Asset/ColorLookupImporter.cpp:185, 363`; `Strata/src/Strata/Renderer/SceneRenderer.cpp:3642`; `Strata/src/Strata/Renderer/SceneRendererPost.cpp:1159, 1167, 1255-1263`; `Strata/shaders/PostProcess/Tonemap.frag.slang:263-270` |
| `render-image:664-669` | term | home | White balance; color temperature, kelvin and mired; Planckian and daylight loci; CIE 1931 xy and CIE 1960 uv; tint; chromatic adaptation, von Kries and CAT02 |
| `render-image:671-674` | term | home | Slope, offset and power; 3D LUT, color lookup and `.cube`; trilinear interpolation; half-texel remap |
| `new:2` | erratum | home | The Developer Guide names the tone mapping's second layout and set `m_ColorLookupLayout` and `GetColorLookupSet`; the code names them `m_TonemapInputLayout` and `GetTonemapInputSet`, and the set holds the lens flare as well as the lookup. The page states the code's names. Evidence: `Docs/DeveloperGuide.md:5682-5684`; `Strata/src/Strata/Renderer/SceneRendererPost.cpp:102-109, 1167`; `Strata/src/Strata/Renderer/SceneRenderer.h:1663, 2300`; `git grep -n -e m_ColorLookupLayout -e GetColorLookupSet 822a7a46 -- Strata/src` finds nothing |
| `new:33` | feature | home | How it is tested, beside the suites the inventory names: `Asset.ColorLookupImporter`, whose cases check that malformed files are refused with the line and the reason, and that resampling keeps a table of its size, refines exactly and maps the file's domain. Evidence: `StrataTests/src/Asset/ColorLookupImporterTests.cpp:59, 91, 120` |
| `assets:161` | feature | home | The color lookup importer as the asset area lists it: `.cube` tables parsed, resampled to `Size` 17, 33, 65 or the file's own, stored as STLU (`Strata/src/Strata/Asset/ColorLookupImporter.h:28-43`) |
| `render-image:406` | code | use | The grading (`Tonemap.frag.slang:237-244`) and lookup (263-270) lines of the pass |
| `render-image:670` | term | link | D65; its home is `basics/color` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Tone mapping: the curve and the order of the display pass | `image/tone-mapping` | must |
| Color: chromaticity, white point, gamut, the working color space | `basics/color` | must |
| Matrices, transforms and their products | `basics/math-matrices` | must |
| Importing: import records, settings as properties, background imports, cancellation | `assets/importing` | must |
| Loading without stalling | `assets/loading` | must |
| Textures for the GPU; sampling and filtering | `assets/textures` | helps |
| Untrusted input: validate before use, bounded sizes | `assets/robustness` | helps |
| Blending and smoothing: lerp and its weight | `basics/math-interpolation` | helps |
| The post chain's binding sets per source | `image/why-post` | helps |

## `image/encoding` — Encoding, dithering and grain

**Covers.** The job: turn display-linear values into the codes the target stores, with no bands, and add noise once
only. The page starts with a dark sky gradient at 8 bits, without and with the dither, enlarged four times
(`render-image:497`). The problem: the sRGB transfer function as Strata's code writes it (`Common.slang`, with its CPU
twin), and what 256 codes do to a dark gradient. The approaches, in one short section: rectangular against triangular
noise, noise modulation, temporal against static noise, 10-bit intermediates (diagram `render-image:456`). Strata's
choice: a triangular dither from a static integer hash of the pixel, exact at black and white and mean-preserving, added
once in the last pass that writes the display image. Code #14 walks `Dither.slang`; `GetDitherLevels` gives the levels
per target format. Which pass is last is decided in `RenderPostDisplay` (code #18): without spatial anti-aliasing the
tone mapping dithers into the output; with FXAA or the morphological AA it writes the 10-bit intermediate undithered,
and the AA pass dithers. A sentence points forward to `image/spatial-aa` for those passes, and to the film grain below,
which goes into the same last pass. The contrast case is the sun shadows' blue noise, fixed and spatial for another
reason.

Film grain (code #15): mid-tone weighted, near-Gaussian from summed uniforms, new every frame, added in the last pass
just before the dither, so that FXAA does not take it for edges; `GrainSeed` makes stills deterministic; the sweep
`render-image:503` shows grain at 0, 0.3 and 1 on mid-gray, cropped (the look-dev shot `tp.grain`). The rules: dither
once, in the encoded domain, with grain just before it; the dither is static, not temporal. `DitherOutput` is only a
switch of the renderer's specification (the exact-pixel tests' `ExactSpecification` turns it off); the editor has none,
so figure `render-image:497` waits for tier 2's capture switch (`waitsFor`), and a diagram of the same gradient stands
in its place until v0.8.1. Strata writes sRGB output only: there is no HDR10 or
scRGB swap chain (`new:4`). How it is tested: the twins of `Renderer.PostProcessMath`, the dither cases of
`GPU.SceneRenderer.Camera` ("Dithering keeps a gradient's mean and breaks up its bands", "DitherOutput false quantizes
without noise"). Exercises: predict the gradient with and without the dither, then run those two cases (`new:17`); trace
which pass dithers for each anti-aliasing setting (`new:18`). At the end the reader can explain every code the target
receives and why the image shows no bands.

**Leaves out.**

- FXAA and the morphological AA, the passes that dither when they run → `image/spatial-aa`
- The blue noise of the sun's shadow filter → `light/sun-shadows-2`
- The swap chain and its formats → `gpu/vulkan-nvrhi`
- Ordered dither as an idea of signals → `basics/signals`
- Exact-pixel tests as a kind of test → `engineering/test-kinds`

**Fit.** `fits`: about 4,650 words against L (5,000). Quantization and the two noise designs, then the choice of the
last pass (code #18, 114 lines) and the grain take the most words, with three excerpts, three figures and two exercises.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-image:345` | concept | home | Display encoding and quantization: banding in dark gradients, rectangular and triangular dither, noise modulation, temporal against static noise, 10-bit intermediates; the errors (dithering twice, dithering linear values, FXAA seeing dither as edges) |
| `render-image:130` | feature | home | sRGB encoding (`Common.slang:25-39`) and its CPU twin `PostProcessMath::LinearToSRGB` |
| `render-image:140` | feature | home | The triangular dither, static per pixel, exact at black and white; levels by target format; which pass dithers (`SceneRendererPost.cpp:1285-1294`); the switch `DitherOutput` |
| `render-image:144` | feature | home | The 10-bit LDR intermediate (`c_LDRFormat`, R10G10B10A2_UNORM), written undithered when FXAA or the morphological AA follows |
| `render-image:161` | feature | home | Film grain: mid-tone weighted, near-Gaussian, per frame, after the anti-aliasing; `c_FilmGrainAmplitude`; `GrainSeed` for deterministic stills |
| `render-image:408` | code | home | `Strata/shaders/Include/Dither.slang:10-51`: integer hash noise and the triangular dither with exact ends |
| `render-image:409` | code | home | `Strata/shaders/Include/Grain.slang:17-25`: zero-mean grain from summed uniforms, weighted to the mid-tones |
| `render-image:412` | code | home | `Strata/src/Strata/Renderer/SceneRendererPost.cpp:1220-1333`: `RenderPostDisplay`: which pass tone-maps into which target, who dithers, who adds grain, the fallback between FXAA and the morphological AA, the constant buffer's write |
| `render-image:426` | code | home | `Strata/src/Strata/Renderer/SceneRendererPost.cpp:57-75`: `GetDitherLevels`. The other short snippets of the item are quoted on their own pages: `StepSeconds` on `image/exposure`, `TonemapConstants` on `image/tone-mapping`, `GetVignetteTangents` on `image/lens-effects`, the Graphics example on `image/quality-settings`, `AddNeutralPostProcess` on `image/tutorial-post-effect` |
| `render-image:549`, `render-image:551` | rule | home | Dither once, in the last pass, in the encoded domain, with grain just before it; the dither is static, not temporal |
| `render-image:456` | figure | home | Diagram: the code-value staircase, rectangular and triangular noise densities, the rule that snaps the ends, why noise modulation matters |
| `render-image:497` | figure | home | Banding against dither, the off and on: a dark sky gradient with `DitherOutput` off and on, enlarged four times. `DitherOutput` off is a switch of tier 2's `viewport.capture {renderer}` (pipelines.md §11), so the figure carries `waitsFor` that switch and the page shows a diagram of the gradient in its place until v0.8.1 (R34, D42; image-q7) |
| `render-image:503` | figure | home | The film grain sweep at 0, 0.3 and 1 on mid-gray, cropped: 0.3 is the look-dev shot `tp.grain` with its center crop (`Tools/LookDev/Shots.json:59`), 0 and 1 set in its setup |
| `render-image:676-680` | term | home | Banding and quantization; dither and TPDF; noise modulation; 10-bit intermediate; film grain |
| `render-image:809` | open | home | Checked at the pin: `DitherOutput` is a field of `SceneRendererSpecification` only (`SceneRenderer.h:254`, read at `SceneRendererPost.cpp:1287`); no file of `StrataEditor/src` names it, so the figure of the banding cannot be made in the editor at the pin: it waits for tier 2's capture switch, with a diagram until v0.8.1 (`render-image:497`) |
| `new:4` | not-done | home | No HDR display output (HDR10, scRGB): the swap chain is sRGB only. Evidence: `Strata/src/Platform/Vulkan/VulkanGraphicsDevice.cpp:1131-1136`, run again at the pin (only `VK_COLOR_SPACE_SRGB_NONLINEAR_KHR` surface formats are chosen) |
| `new:17` | hands-on | home | Exercise (predict, then run): predict from the triangular noise's density what an 8-bit dark gradient's mean and largest step do with the dither and without it, then run the two dither cases of `GPU.SceneRenderer.Camera` with `--test-case` and read their checks; the reader says which check a rectangular dither would fail. Evidence: `StrataTests/src/Renderer/GPUSceneCameraTests.cpp:279, 281, 421` |
| `new:18` | hands-on | home | Exercise (trace it yourself): for anti-aliasing off, FXAA, the morphological AA and TAA, find the one pass that dithers: the levels that `RenderPostDisplay` hands each pass and the three shaders that call `DitherToCodes`. Evidence: `Strata/src/Strata/Renderer/SceneRendererPost.cpp:1287-1288, 1308, 1324`; `Strata/shaders/PostProcess/Tonemap.frag.slang:274`; `Strata/shaders/PostProcess/FXAA.frag.slang:27`; `Strata/shaders/PostProcess/MorphologicalBlend.frag.slang:55` |
| `render-image:675` | term | use | The sRGB transfer function; its home is `basics/color` |
| `render-image:282` | feature | link | The sun shadows' void-and-cluster blue noise, the contrast case for the dither's static white noise; `light/sun-shadows-2` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Color: the sRGB transfer function | `basics/color` | must |
| Sampling, aliasing and filtering; ordered dither | `basics/signals` | must |
| Probability, random numbers and seeds; white and blue noise | `basics/math-probability` | must |
| Binary integers, shifts and masks | `basics/numbers` | must |
| Hashes | `basics/data-formats` | helps |
| Tone mapping: the display pass and its order | `image/tone-mapping` | must |
| Why images need post-processing; the chain's targets | `image/why-post` | must |
| FXAA and the morphological AA as the last pass | `image/spatial-aa` | helps |
| The swap chain and presentation | `gpu/vulkan-nvrhi` | helps |
| Writing a GPU test that compares pixels | `gpu/first-triangle` | helps |
| Building Strata from source and running one test case | `core/first-change` | helps |

## `image/lens-effects` — Lens effects: bloom, vignette, flares and fringes

**Covers.** The job: add what a real lens adds around bright light (bloom, the lens's vignette, lateral chromatic
aberration and flares), restrained, and off or low by default. The page starts with bloom off, at the default 0.04 and at
0.2 (`render-image:499`). The full section "The problem and how engines solve it": a lens's point spread and
convolution; separable blurs against pyramids; downsample filters, from the box to the 13-tap filter of Call of Duty:
Advanced Warfare; fireflies and the Karis average; thresholds against an energy-conserving mix; resolution
independence. Then the lens models: the cos^4 law, chromatic aberration as a radial scale per channel, ghosts as mirrored
images through the optical center, a halo, a starburst from the aperture. The toy is a box-filtered pyramid, down and up,
in about 40 lines.

Bloom in the real code: code #16 (the 13-tap downsample as five weighted boxes, Karis weights on the first level, the
tent upsample, the soft-knee threshold) and code #17 (the span from a radius given as a share of the image's height, the
fractional deepest level, the loop). The chain is at half resolution down to 4 pixels, at most 8 levels (diagram
`render-image:458`); the tone map mixes it in at threshold 0 and adds it above. The vignette: cos^4 on scene-linear
light before the grading, its tangents from the projection (`GetVignetteTangents`), the orthographic case
(`render-image:501`, at 0, 0.12 and 1). Chromatic aberration: red magnified and blue shrunk about the center
(`render-image:502`, a corner cropped four times, from the shot `tp.grain`). Lens flares: `new:5` walks the ghosts
mirrored at four scales, the halo, the bright part above four times middle gray's display white only, and the sun's
visibility from 16 depth taps; the flare reads the bloom chain's level 1 as its downsample left it, before the
upsamples, whose tent filters would leave contours the flare's threshold would cut out, so the chain runs for the flare
even with Bloom off (one paragraph); the starburst is drawn at full resolution in the tone map (diagram
`render-image:460`; `render-image:504` with the sun in view, from the shots `ow.sunward` and `ow.sunward.flare`, and
behind a wall). How it is tested: the bloom cases of `GPU.SceneRenderer.PostProcess`, `GPU.SceneRenderer.LensFlare`,
`GPU.SceneRenderer.GrainAndAberration`. Exercises: the bloom's reach predicted and measured at two resolutions
(`new:19`); the sun traced from the frame to the starburst (`new:20`). At the end the reader can tune bloom so that it
keeps its size at every resolution, and explain each element of a flare.

**Leaves out.**

- The tone-mapping pass that composes these effects → `image/tone-mapping`
- Depth of field, the lens's other effect → `image/depth-of-field`
- Motion blur → `image/motion-blur`
- Mips of textures and how they are made → `assets/textures`
- Lens effects in a game's look → `make/look`

**Fit.** `fits`: about 5,050 words against L (5,000). Four effects, each in a short section of its own, with three
excerpts, six figures and two exercises; the flares take the most words, with their excerpt, their diagram and the
paragraph on the bloom chain's level 1.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-image:354`, `render-image:358` | concept | home | Convolution, mip chains and bloom; lens models for the vignette, chromatic aberration and flares; the errors (thresholded bloom that darkens the rest, a halo that shrinks at 4K, a vignette after the curve, flares from the whole image) |
| `render-image:149` | feature | home | Bloom: the 13-tap downsample with the Karis average, the tent upsample, the chain (`SceneRendererPost.cpp:323-362`), the composition in the tone map, the four settings and their defaults |
| `render-image:155` | feature | home | The vignette: cos^4 on scene-linear light, before the grading (`Tonemap.frag.slang:229-236`), `GetVignetteTangents` |
| `render-image:158` | feature | home | Chromatic aberration: lateral, red magnified and blue shrunk about the center; `c_ChromaticAberrationScale` |
| `render-image:164` | feature | home | Lens flares: ghosts, halo and the sun's starburst; `EnsureLensFlareResources`, `RenderLensFlare` (`SceneRendererPost.cpp:1085-1148`); the starburst in the tone map; the sun's place on screen; the flare reads the bloom chain's level 1 between the downsamples and the upsamples, whose tents would leave contours its threshold would cut out, so the chain runs for the flare even with Bloom off (`Strata/src/Strata/Renderer/SceneRendererPost.cpp:1056-1074`; `Docs/Manual/Camera.md:166`) |
| `render-image:410` | code | home | `Strata/shaders/PostProcess/Bloom.comp.slang:38-100`: the 13-tap downsample as five weighted boxes, Karis weights, the tent upsample, the soft-knee threshold |
| `render-image:411` | code | home | `Strata/src/Strata/Renderer/SceneRendererPost.cpp:999-1047`: the bloom's span from a radius fraction, the fractional deepest level, the loop of downsamples and upsamples |
| `new:5` | code | home | `Strata/shaders/PostProcess/LensFlare.comp.slang:72-137`: the bright part above a threshold with its excess compressed, the edge fade, the sun's visibility from 16 depth taps, four tinted ghosts mirrored through the center, the halo |
| `render-image:458`, `render-image:460` | figure | home | Diagrams: the bloom's mip chain with the 13-tap footprint and the tent; the flare's geometry (ghosts at −1.6, −0.7, 0.45 and 1.2, the halo ring, the sun's taps) |
| `render-image:499`, `render-image:501`, `render-image:502`, `render-image:504` | figure | home | Bloom off and on with its intensity, threshold, radius and resolution sweeps; the vignette sweep; chromatic aberration off and on, cropped, from the look-dev shot `tp.grain` (aberration 1, its corner crop; `Tools/LookDev/Shots.json:59`); the flare off and on from the shots `ow.sunward` and `ow.sunward.flare` (crops of the sun and the ghosts; `Shots.json:62-63`), and with the sun behind a wall |
| `new:19` | hands-on | home | Exercise (predict, then run): with `component.set` give a sample's Post Process a strong bloom (BloomIntensity 0.2), capture one view at 1280x720 and at 2560x1440 with `viewport.capture`'s width and height, predict and then measure the glow's reach as a share of the image height in both, and say why it is the same (`BloomRadius` is a share of the height). Evidence: `Strata/src/Strata/Renderer/RendererComponents.h:274-279`; `StrataEditor/src/Editor/EditorViewportCommands.cpp:1252` |
| `new:20` | hands-on | home | Exercise (trace it yourself): follow the sun from `RenderFrame`, which projects the directional light's disk to `sunUV`, through `RenderPostHDR` and `RenderLensFlare` to the starburst's place in the tone map's constants; the reader says why the starburst goes when a wall covers the sun. Evidence: `Strata/src/Strata/Renderer/SceneRenderer.cpp:3617-3629`; `Strata/src/Strata/Renderer/SceneRendererPost.cpp:1072, 1121-1134, 1273` |
| `render-image:681` | term | home | Bloom |
| `render-image:683-690` | term | home | Karis average; firefly; tent filter; soft knee; vignette and the cos^4 law; field angle; chromatic aberration (lateral); lens flare, ghost, halo and starburst |
| `render-image:426` | code | use | `GetVignetteTangents` (`SceneRendererPost.cpp:1150-1157`), one of the short snippets |
| `render-image:396` | code | use | The sun's place on screen for the starburst (`SceneRenderer.cpp:3617-3628`), from the orchestration |
| `render-image:682` | term | link | Mip chain and pyramid; the home of mips is `assets/textures` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Tone mapping: the display pass and its order | `image/tone-mapping` | must |
| Camera exposure: exposed values and middle gray | `image/exposure` | must |
| Sampling, aliasing and filtering: kernels and mip prefiltering | `basics/signals` | must |
| Textures for the GPU: mips | `assets/textures` | must |
| Compute shaders: dispatches and thread groups | `gpu/compute` | must |
| The camera: field of view and projection; reversed depth, the sky at depth 0 | `gpu/coordinates` | must |
| Color: luminance as a weighted sum | `basics/color` | must |
| Projection: from a direction to a point on the screen | `basics/math-projection` | helps |
| Lights: the sun and its disk | `light/lights` | helps |
| Running an editor command from a line to paste (the exercise) | `start/how-to-read` | helps |

## `image/spatial-aa` — Anti-aliasing in one frame: FXAA and morphological AA

**Covers.** The job: remove jagged edges from one finished frame, without history, working on display values. The page
starts with the aliasing figure `render-image:506`: the Physics Playground's tiled floor in crops enlarged four times,
with anti-aliasing off, FXAA, the morphological AA and TAA Sharp. The full section "The problem and how engines solve
it": pixels as point samples; geometric, shading and temporal aliasing; supersampling and MSAA and what they cost;
anti-aliasing as a post pass (MLAA, SMAA, FXAA). Strata has neither supersampling nor MSAA, and the renderer refuses a
target that is not single-sampled (`new:6`). One sentence names Strata's first design decision, never below native
resolution (no render scale below 1, no dynamic resolution, no temporal upscaling), and links its home
`image/quality-settings`: a frame is drawn at native size with one sample per pixel, and these passes and TAA are its
anti-aliasing. Strata's choice: `PostProcessComponent::AntiAliasing` with
`AntiAliasingMethod` (FXAA by default, TAA, Morphological). The toy is an edge detector on luma and a blend across the
edge, in about 40 lines.

FXAA (diagram `render-image:462`, code #19): luma of display-encoded values, the local contrast test, the edge's
orientation from second differences, a 12-step walk along the edge, the subpixel blend, whose factor 0.7.0 lowered from
0.75 to 0.25 to keep the texture's detail (`render-image:508`, a diagram until tier 2 has the switch). Strata's
morphological AA (diagram `render-image:463`), in three passes: the edges (`new:7`: luma differences kept by local
contrast adaptation, and depth jumps), the weights (code #20: a run search, the crossings at its ends, the area table
that `Tools/GenerateAreaTable.py` integrates exactly; Z, L and U shapes, and a U blends nothing), and the blend in
linear light. It shares no table with the published SMAA. The pass that runs last also dithers and adds the grain, as
`image/encoding` taught (`RenderPostDisplay` chooses between the two methods). How it is tested: the FXAA case of
`GPU.SceneRenderer.PostProcess`, `GPU.SceneRenderer.Morphological`. Exercises: the anti-aliasing shoot-out, still and in
a slow pan; the morphological AA traced to its passes and its fallback (`new:21`); FXAA's subpixel factor changed and
measured with the look-dev harness's crops. At the end the reader can choose a spatial AA for a scene and say what each
method cannot fix.

**Leaves out.**

- Temporal anti-aliasing → `image/taa`
- Specular aliasing of highlights and its filter in the shader → `light/brdf`
- Sampling and the Nyquist limit from zero → `basics/signals`
- Choosing the anti-aliasing in a game → `make/quality`
- Committed generators as a workflow of the build → `engineering/generated-code`
- The look-dev harness that makes the crops → `engineering/look-dev`

**Fit.** `fits`: about 4,550 words against L (5,000). The two algorithms, FXAA and the three passes of the
morphological AA, take the most words with three excerpts, four figures and three exercises; the sampling theory is
linked, not taught again.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-image:362`, `render-image:364` | concept | home | Sampling and aliasing in rendering (geometric, shading, temporal; supersampling, MSAA, post AA; AA is not blur); spatial post AA (FXAA, MLAA and SMAA, depth-aware edges; FXAA expects encoded luma) |
| `render-image:194-198` | feature | home | `AntiAliasing` and `AntiAliasingMethod` {FXAA, TAA, Morphological}; FXAA after FXAA 3.11 with `c_Subpixel` 0.25; Strata's morphological AA, its resources (`SceneRendererPost.cpp:862-919`) and passes (1303-1320) |
| `render-image:281` | feature | home | `Tools/GenerateAreaTable.py` → `MorphologicalAreaTable.inl`, 132x132 RG8 |
| `render-image:413` | code | home | `Strata/shaders/PostProcess/FXAA.frag.slang:51-169`: the local contrast test, the edge's orientation, the walk along the edge, the subpixel blend |
| `render-image:414` | code | home | `Strata/shaders/PostProcess/MorphologicalWeights.frag.slang:17-78`: the run search, the crossings' classification and the area-table lookup |
| `new:7` | code | home | `Strata/shaders/PostProcess/MorphologicalEdges.frag.slang:44-81`: the edges pass: luma differences kept only against half the largest neighboring difference, and depth jumps beyond the neighbors' steps |
| `render-image:462`, `render-image:463` | figure | home | Diagrams: FXAA's steps; the morphological AA's edge map, a run with its two crossings, the Z, L and U shapes, the area table's layout |
| `render-image:506` | figure | home | Off, FXAA, morphological and TAA Sharp in crops (the off and on) |
| `render-image:508` | figure | home | FXAA's subpixel 0.25 against 0.75, drawn as a diagram: tier 2 has no switch for `c_Subpixel` (`Strata/shaders/PostProcess/FXAA.frag.slang:37`), so the figure carries `waitsFor` the one request that extends tier 2 (pipelines.md §11; R34, D42) |
| `render-image:597` | hands-on | home | Exercise: the anti-aliasing shoot-out on the Physics Playground's floor, still and in a slow pan |
| `render-image:621` | hands-on | home | Exercise: rebuild with FXAA's subpixel at 0.75 and 0.25 and measure the detail with the look-dev crops |
| `new:21` | hands-on | home | Exercise (trace it yourself): follow `AntiAliasingMethod` Morphological from `RenderPostDisplay`'s choice through `EnsureMorphologicalResources` to the three passes and the statistic that reports them, and find the line where a failure to make the resources draws FXAA instead. Evidence: `Strata/src/Strata/Renderer/SceneRendererPost.cpp:862-919, 1276-1283, 1303-1320` |
| `render-image:643` | term | home | Luma (FXAA's weights of encoded values) |
| `render-image:692-697` | term | home | Supersampling and MSAA; FXAA; MLAA, SMAA and morphological AA; area table; Z, L and U shapes; subpixel blend |
| `new:6` | not-done | home | MSAA and supersampling (a render scale above 1): neither exists, and the renderer refuses a target with more than one sample. Evidence: `Strata/src/Strata/Renderer/SceneRenderer.cpp:2767` (`info.sampleCount != 1` refused); `Docs/Roadmap.md:944, 1670, 1672`; `Docs/Releases/0.7.0.md:409, 411`, run again at the pin |
| `render-image:412` | code | use | The choice between FXAA and the morphological AA in `RenderPostDisplay` |
| `render-image:286` | feature | use | The look-dev harness's `--aa` and its crops, for the figure and the exercise; its home is `engineering/look-dev` |
| `render-image:691` | term | link | Aliasing; its home is `basics/signals` |
| `new:11` | not-done | link | The first design decision, never below native resolution, named in one sentence (`book.md`, "Strata's design decisions"); its home is `image/quality-settings` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Sampling, aliasing and filtering; the Nyquist limit | `basics/signals` | must |
| Display encoding, the 10-bit intermediate, the last pass's dither | `image/encoding` | must |
| How a GPU draws a frame: rasterization takes pixels as samples | `gpu/how-a-gpu-frame-works` | must |
| Strata's depth conventions: reversed Z | `gpu/coordinates` | must |
| Color: luminance and luma | `basics/color` | must |
| Tone mapping: the display pass | `image/tone-mapping` | helps |
| Specular anti-aliasing | `light/brdf` | helps |
| Committed generators | `engineering/generated-code` | helps |

## `image/taa` — Temporal anti-aliasing

**Covers.** The job: accumulate jittered frames into one sharp image without blur or trails, while staying one choice
among others. This page is the home of the design decision that nothing needs history to look right (a `:::why` aside:
TAA stays one anti-aliasing choice; the sun shadows' fixed noise, the ambient occlusion resolved within the frame, the
static dither and motion-blur offsets all look right in one frame; the one named exception, Medium's Checkerboard
reflections, links `indirect/ssr`; and, as the decision holds at the pin, the point and spot lights' shadow filter still
turns its noise with the TAA frame, so its grain is static without TAA and averaged with it, in one sentence that links
`light/local-shadows`). The full section "The problem and how engines solve it": sub-pixel jitter,
accumulation as an exponential moving average, reprojection along motion vectors, neighborhood clamping and clipping,
disocclusion, and the engines' TAA and TSR; the upscalers (DLAA, FSR) are outside Strata's policy. Diagram
`render-image:465` gives the overview; the toy is a TAA in about 80 lines (jitter, reproject, clamp, blend).

The real code, in the order data flows. The jitter: 8 phases of Halton (2, 3) (code #21), only in the frame's copy of
the projection, because jittering the shared camera would change culling, levels of detail and the cascade cache's key;
the history's continuation rules and the golden-ratio turn of other effects' noise (code #22); overlays keep unjittered
matrices; the ping-pong RGBA16F history and its post sets. The resolve (code #24): nearest-depth motion, the history
through Catmull-Rom in nine bilinear taps (code #23, diagram `render-image:467`), the YCoCg clamp or the variance clip
(code #25, diagram `render-image:468`), the luminance-weighted blend, the motion weight and the resampling term, the
reactive mask for transparent surfaces built on the HDR alpha convention, and disocclusion from the view distance stored
in the history's alpha (diagram `render-image:469`). Sharpening works on the displayed image only, never on the history,
and never where depth of field or motion blur blurred (code #26, in the tone map: it reads the blur mask they write in
the image's alpha, whose home is `image/motion-blur`). The presets Sharp, Original and Custom are tables, normalized so
that equal looks compare equal (code #27). The history's life (diagram `render-image:470`): it is counted in frames,
owned by each renderer, reset on cuts, scene changes and resizes; single images settle for 8 frames or use FXAA.
Figures: `render-image:509` (the presets in a slow pan), `render-image:510` (a trail under MinMax and Variance; a
disocclusion ghost), `render-image:511` (TransparentWeight 0 and 0.5); TAA off and on is figure `render-image:506` of
`image/spatial-aa`, and the Post Process inspector's TAA preset drawer with the tunables greyed until Custom is
`editor-ui:560`, captured once for `editor-ui/inspectors`. A short section "What it cannot do" states TAA's documented
limits (`new:30`): a surface that recedes faster than the disocclusion threshold loses its history while it does, a band
a moving object uncovers stays less smooth for about 17 frames, and Original keeps about half of fine texture detail in
slow pans (Sharp about three quarters). How it is tested: `GPU.SceneRenderer.TAA` with the flicker metrics, and
`Renderer.TAASharpening`. The page names the sharpening field as the code does (`new:8`). Exercises: tune Custom; trace
the noise turn to the shaders that read it (`new:22`); turn the clamp off on a throwaway branch, then write a variance
clip from scratch. At the end the reader can read and change the resolve and say which rule protects the image from
which artifact.

**Leaves out.**

- How motion vectors and the motion history are made → `draw/motion-vectors`
- FXAA and the morphological AA → `image/spatial-aa`
- The Checkerboard reflections that use the history → `indirect/ssr`
- The flicker metrics and the TAA suites as tests → `engineering/test-kinds`
- The fixed noise of the sun's shadow filter → `light/sun-shadows-2`
- The look-dev harness → `engineering/look-dev`
- The preset rows that choose the anti-aliasing per machine → `image/quality-settings`

**Fit.** `fits`: about 7,450 words against XL (8,000). Seven excerpts with six diagrams and three screenshots take the
most words, the resolve alone about 1,650 with three excerpts and three diagrams; the problem section stays under a
fifth of the prose.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-image:371` | concept | home | Temporal anti-aliasing: jitter, accumulation, reprojection with a sharp filter, clamping and clipping in YCoCg, luminance weighting, disocclusion, reactive masks, motion-adaptive weights, resampling blur and sharpening, history invalidation; the approaches and the errors |
| `render-image:203-223` | feature | home | TAA as a whole; the Halton jitter and its phases; the history's lifetime and reset rules; the ping-pong resources; the resolve; the golden-ratio noise turn; the settings, presets and tunables; sharpening; settling of single images; the guide and the Manual, and the release (0.6.0, used by the Basic 3D template); overlays with unjittered matrices |
| `render-image:35` | feature | home | The HDR alpha convention: alpha 1 for opaque writers, multiplied by 1 − a by blended surfaces, so it is transmittance after the transparent pass, read only by the reactive mask |
| `render-image:415` | code | home | `Strata/src/Strata/Renderer/SceneRenderer.cpp:2800-2816`: the Halton (2, 3) radical inverse, a low-discrepancy jitter in 15 lines |
| `render-image:416` | code | home | `Strata/src/Strata/Renderer/SceneRenderer.cpp:3006-3043`: the history's continuation rules; with 3092-3117, the jitter only in the frame's projection copy and the golden-ratio noise turn |
| `render-image:417` | code | home | `Strata/shaders/PostProcess/TAA.comp.slang:162-190`: Catmull-Rom in nine bilinear taps, by merging weights |
| `render-image:418` | code | home | `Strata/shaders/PostProcess/TAA.comp.slang:192-272`: the resolve: nearest-depth motion, the inside test, the clamp, the weights, the luminance-weighted blend, alpha as the view distance |
| `render-image:419` | code | home | `Strata/shaders/PostProcess/TAA.comp.slang:83-142`: variance clipping toward the mean in compressed YCoCg; the one-sided disocclusion test with `GatherAlpha` |
| `render-image:420` | code | home | `Strata/shaders/PostProcess/Tonemap.frag.slang:91-119`: bounded, contrast-adaptive sharpening of luminance on the displayed image |
| `render-image:421` | code | home | `Strata/src/Strata/Renderer/RendererComponents.h:220-256`: the presets as tables; with `RendererComponents.cpp:680-718`, the normalization that makes equal looks compare equal and Custom's start |
| `render-image:553` | rule | home | Jitter only the frame's copy of the camera |
| `render-image:557-563` | rule | home | Sharpen only the displayed image; the history is counted in frames and belongs to the renderer; single images settle or turn TAA off; the HDR alpha convention is load-bearing |
| `render-image:574` | rule | home | Nothing may need temporal accumulation to look right, so every effect is stable without TAA: the home of the design decision, stated as it holds at the pin (the Checkerboard reflections are the named exception, and the point and spot lights' filter still turns its noise with the TAA frame: `Strata/shaders/Include/LocalShadows.slang:32-38`, `Docs/DeveloperGuide.md:4789`); the native-resolution half of the rule is taught by `image/quality-settings` |
| `new:30` | rule | home | What TAA cannot do, its documented limits: a surface that recedes faster than the disocclusion threshold each frame looks uncovered and loses its history while it does; the band a moving object uncovers starts from one frame and stays less smooth for about 17 frames; Original keeps about half of fine texture detail in slow pans and Sharp about three quarters. Evidence: `Docs/Manual/AntiAliasing.md:167-176` |
| `render-image:465-470` | figure | home | Diagrams: the TAA overview with 8 Halton points and a trail clamped away; Catmull-Rom's weight merging; variance clipping in YCoCg; the disocclusion test; the history's life with its weights |
| `render-image:509-511` | figure | home | The presets Original, Sharp and Custom in a slow pan; a trail under MinMax and Variance, and the disocclusion ghost; a transparent surface with TransparentWeight 0 and 0.5 |
| `render-image:599` | hands-on | home | Exercise: start Custom from Sharp and find where the resample weight brings back stair-steps |
| `render-image:623` | hands-on | home | Exercise: TAA without its clamp on a throwaway branch; then a variance clip from scratch, compared with `TAA.comp` |
| `new:22` | hands-on | home | Exercise (trace it yourself): find where the CPU writes the golden-ratio turn into `TemporalParams.z` and, with a search, every shader that reads it (the screen-space reflections' noise and the point and spot lights' shadow filter); the reader says what each looks like without TAA, which of them the design decision names as its exception, and why the sun's filter is not in the list. Evidence: `Strata/src/Strata/Renderer/SceneRenderer.cpp:3114-3117`; `Strata/shaders/Effects/ScreenSpaceReflections.comp.slang:69`; `Strata/shaders/Include/LocalShadows.slang:32-38` |
| `render-image:698-701` | term | home | TAA; jitter, Halton sequence and radical inverse; history; reprojection |
| `render-image:704-714` | term | home | Catmull-Rom filter; neighborhood clamp and variance clipping; YCoCg; ghosting and trail; disocclusion; reactive mask; resampling blur; sharpening (TAA); camera cut; settle frames; golden-ratio turn |
| `new:8` | erratum | home | The Developer Guide writes `TonemapParameters::Sharpening`; the field is `Sharpening` of `RenderData::TonemapConstants`, and no `TonemapParameters` exists in the code. Evidence: `Docs/DeveloperGuide.md:4466`; `Strata/src/Strata/Renderer/PostProcessData.h:19, 28`; `git grep -n -e TonemapParameters 822a7a46 -- Strata/src Strata/shaders` finds nothing |
| `render-core:774` | term | home | Jitter (TAA), in the renderer core's words: a sub-pixel offset of the projection each frame |
| `render-image:506` | figure | use | TAA off and on, from `image/spatial-aa` |
| `render-image:171` | feature | use | The velocity target: unjittered current minus previous position; its home is `draw/motion-vectors` |
| `render-image:368` | concept | use | Motion vectors recalled in one paragraph; their home is `draw/motion-vectors` |
| `render-image:189` | feature | use | The blur mask that the sharpening respects; its home is `image/motion-blur` |
| `render-image:286` | feature | use | The look-dev harness's shots with `--aa` and `--live` for the figures |
| `render-indirect:494` | rule | link | Checkerboard reflections need TAA: the named exception to the decision |
| `render-direct:143` | feature | link | The point and spot lights' filter, whose noise still turns with the TAA frame, named in the decision's aside; `light/local-shadows` |
| `editor-ui:560` | figure | use | The Post Process inspector's TAA preset drawer, the tunables greyed until Custom: one capture, homed on `editor-ui/inspectors` (critic-render-image-16) |
| `render-indirect:619` | term | use | TAA history, as the indirect-light area names it |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Anti-aliasing in one frame; the kinds of aliasing | `image/spatial-aa` | must |
| Motion vectors and motion history | `draw/motion-vectors` | must |
| Projection: view and projection matrices, clip space | `basics/math-projection` | must |
| Blending and smoothing: exponential smoothing; curves through keys | `basics/math-interpolation` | must |
| Mean and standard deviation | `basics/math-probability` | must |
| Sampling and filtering: bilinear reads | `basics/signals` | must |
| Number bases, for the radical inverse | `basics/numbers` | must |
| Color: linear RGB and luminance | `basics/color` | must |
| Why images need post-processing; the post chain and `PostSource` | `image/why-post` | must |
| Sun shadow casters, the cascade cache and its versions | `light/sun-shadows-1` | must |
| The sun's filter with fixed blue noise | `light/sun-shadows-2` | helps |
| Pre-exposure: the history's rescale | `image/pre-exposure` | helps |
| Transparency, blending and premultiplied alpha | `light/clearcoat-transmission` | helps |
| Measuring pictures in tests: the flicker metrics | `engineering/test-kinds` | helps |
| CPU and GPU culling paths; levels of detail | `draw/bounds-culling` | helps |
| The blur mask that depth of field and motion blur write in the image's alpha: the sharpening reads it and skips the pixels they blurred | `image/motion-blur` | helps |

## `image/motion-blur` — Motion blur

**Covers.** The job: blur what moves while the shutter is open, as a film camera does, without blurring the UI and
without blurring across a cut. The page starts from `render-image:513`: the Third-Person course while the camera turns,
with motion blur off, at a 90 and at a 180 degree shutter, and a crop of the far course and the robot. The section "The
problem and how engines solve it": the shutter angle, the blur a sample-and-hold display adds by itself, scatter against
gather, McGuire's reconstruction with tile maxima and neighbor maxima, depth-aware weights, static stratified offsets
against temporal noise. Strata's variant (diagram `render-image:472`): the tile maximum, the neighbor maximum with its
diagonal rule, a gather along two directions, depth weights, and no blur under a pixel at 1080 rows. The toy is a
gather along each pixel's own motion in about 30 lines.

The real code: code #28 (`GetBlurVelocity` with the shutter's share, the clamp and the sub-pixel drop; the gather's
depth weights), the CPU model `GetMotionBlurProfile` that the tests compare with, and the CPU side `RenderMotionBlur`
with its conditions: no motion history on the first frame, after a resize or on a camera cut. Which views blur
(`new:32`): only the game's camera while the game plays; the editor camera, captures and thumbnails never do, while
depth of field shows in every view and capture through a scene camera. The blur mask in the output's alpha stops the
TAA's sharpening where motion blur or depth of field blurred. The fields `MotionBlur`, `MotionBlurShutterAngle` and
`MotionBlurMaxLength`; the `MotionBlurSamples` quality row and the players' row are named here, with their cost, and the
rows as a system are taught in `image/quality-settings`; the motion view of `draw/motion-vectors` helps to read the
blur. How it is tested: `GPU.SceneRenderer.MotionBlur`, `Renderer.PostProcessMath`. Exercises: a streak's length
predicted and measured at two shutters, and the editor camera that stays sharp (`new:23`); the frames that never blur
traced to their lines (`new:24`). At the end the reader can set a shutter, predict the blur's length in pixels, and say
why a cut and the UI are never blurred.

**Leaves out.**

- How motion vectors and the motion history are made, and the motion view → `draw/motion-vectors`
- Depth of field, the other effect that writes the blur mask → `image/depth-of-field`
- Quality rows, presets and the players' rows as a system → `image/quality-settings`
- Motion blur in a game's look → `make/look`

**Fit.** `fits`: about 3,650 words against M (3,000). The reconstruction (tile and neighbor maxima, the gather with
depth weights), with one excerpt in two files, the CPU model, one diagram and one figure with its sweep, takes the most
words, then the two exercises.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-image:378` | concept | home | Motion blur: shutter angle, sample-and-hold blur, tile-max and neighbor-max reconstruction, depth-aware scatter as gather, stratified offsets; the errors (blurring a cut, blurring the UI) |
| `render-image:175` | feature | home | The three shaders and `Include/MotionBlur.slang`; `EnsureMotionBlurResources` and `RenderMotionBlur` (`SceneRendererPost.cpp:538-695`); the CPU model `GetMotionBlurProfile` (`PostProcessMath.cpp:212-267`); the fields and their defaults; the conditions (`SceneRenderer.cpp:2989, 3598-3607`) |
| `render-image:189` | feature | home | The blur mask in alpha: no sharpening where depth of field or motion blur blurred (`c_TonemapBlurMask`, `MotionBlurParameters::SourceMask`) |
| `render-image:422` | code | home | `Strata/shaders/Include/MotionBlur.slang:25-39`: the blur velocity with the shutter, the clamp and the sub-pixel drop; with `MotionBlur.comp.slang:25-54`, the depth-aware sample weights |
| `render-image:579` | rule | home | Motion blur skips the first frame and camera cuts, and never blurs the UI or the overlays |
| `render-image:472` | figure | home | Diagram: tiles, the neighbor maximum with the diagonal rule, samples along two directions, depth weights |
| `render-image:513` | figure | home | Motion blur off, at 90 and at 180 degrees on `tp.live.turn` (the off and on, and the sweep), with a crop of the far course and the robot |
| `render-image:715-717` | term | home | Shutter angle; tile max and neighbor max; sample-and-hold blur |
| `new:32` | feature | home | Which views blur: only the game's camera, and only while the game plays, in the live views (the Game view, a Scene view through the game's camera); the editor camera and renderers of single images (captures, thumbnails) never blur. Depth of field is a lens's, not a moment's: every view and capture through a scene camera with depth of field shows it, playing or not. Evidence: `StrataEditor/src/Editor/ViewportRenderer.cpp:222-227`; `Strata/src/Strata/Renderer/SceneRenderer.h:440-445`; `Docs/Manual/Camera.md:122-123, 147-148` |
| `new:23` | hands-on | home | Exercise (predict, then run): predict from `GetBlurVelocity` how long a streak the camera's turn leaves at a 180 and at a 90 degree shutter, then run what the look-dev shots `tp.live.turn.mb180` and `tp.live.turn.mb90` run (the Post Process's MotionBlur and MotionBlurShutterAngle, a turn by the `Gameplay/Look` action, a live capture) and measure it; then look at the same turn through the editor camera, which never blurs. Evidence: `Strata/shaders/Include/MotionBlur.slang:25-39`; `Tools/LookDev/Shots.json:40-41`; `StrataEditor/src/Editor/ViewportRenderer.cpp:222-225` |
| `new:24` | hands-on | home | Exercise (trace it yourself): find the frames that never blur and the line that decides each: `motionBlurWanted` (the view's option, a HDR output, the component's field and its shutter), the camera cut from `IsCameraCut`, the motion history, and the condition that runs the pass. Evidence: `Strata/src/Strata/Renderer/SceneRenderer.cpp:2989, 3010, 3598`; `Strata/src/Strata/Renderer/SceneRenderer.h:1739` |
| `render-image:512` | figure | use | The motion view while the camera turns; its home is `draw/motion-vectors` |
| `render-image:171` | feature | use | The velocity target that the blur reads; its home is `draw/motion-vectors` |
| `render-image:238` | feature | use | The players' `MotionBlur` row; its home is `image/quality-settings` |
| `render-scene:173` | feature | use | Motion vectors as the render-scene area gives them |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Temporal anti-aliasing: the history, camera cuts, sharpening | `image/taa` | must |
| Motion vectors and motion history | `draw/motion-vectors` | must |
| Compute shaders: thread groups, shared memory | `gpu/compute` | must |
| Strata's depth conventions and view distance | `gpu/coordinates` | must |
| Noise and sampling patterns: stratified offsets | `basics/math-probability` | helps |
| Players' graphics options; presets and traits | `image/quality-settings` | helps |
| Running an editor command from a line to paste (the exercise) | `start/how-to-read` | helps |

## `image/depth-of-field` — Depth of field

**Covers.** The job: blur what is out of focus as a real lens does, and stay stable under the TAA's jitter. The page
starts from `render-image:514`: the Third-Person robot at f/2 against depth of field off, then f/1.4 against f/8, then
the focus held on an entity. The full section "The problem and how engines solve it": the thin lens and the circle of
confusion with its formula (diagram `render-image:473`), near and far fields, scatter as gather, a premultiplied near
field, tile dilation, and the two classic faults, a halo of sharp foreground over the background and flicker at
in-focus silhouettes. The camera's fields (`CameraComponent::DepthOfField`, `FocusDistance`, `FocusEntity`, `Aperture`,
`SensorHeight`) and `CameraLens::FromEntity`, which turns the field of view and the sensor into a focal length (code
#29). The toy is a gather over a disk of each pixel's own circle in about 40 lines.

The five passes in the order data flows: Prepare (half resolution, the signed circle of confusion from
`Include/DepthOfField.slang` in alpha), Tiles and Dilate (the near field's maxima), Gather (`new:9`: 48 Vogel samples on
a disk turned per pixel; the pixel's own field and the near field, each with its cover weights), and Composite
(`new:10`: the sharp image kept exactly within a pixel of focus, a fade from in-focus depth that keeps it stable under
the jitter, the near field over everything, alpha 1 where it changed, which stops the sharpening). Depth of field runs
only for perspective views and when the players' row allows it, and it shows in every view and capture through a scene
camera, playing or not (`new:32`, taught with motion blur's views). No circle of confusion is wider than 2% of the image
height (`c_DepthOfFieldMaxDiameter`), the page's limit. How it is tested: `Renderer.CameraLens`, and
`GPU.SceneRenderer.DepthOfField`, whose cases prove the focus plane bit-identical to depth of field off and an in-focus
silhouette under TAA no more flickering than without the lens. The exercises are a racing camera with both motion blur
and depth of field, and the programs that set a lens traced (`new:25`). At the end the reader can compute a circle of
confusion by hand, set a lens for a shot, and explain why the composite fades from in-focus depth.

**Leaves out.**

- The camera component as a whole, its projection and Primary → `gpu/coordinates`
- How the scene finds its primary camera → `world/scene-graph`
- Motion blur, the other effect that writes the blur mask → `image/motion-blur`
- The players' row that turns it off → `image/quality-settings`
- Depth of field in a game's look → `make/look`

**Fit.** `fits`: about 4,300 words against L (5,000). The thin lens and its circle of confusion, taught from zero, and
the five passes in a short section each take the most words, with three excerpts, one diagram, one figure with its
sweep and two exercises.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-image:381` | concept | home | Depth of field: the thin lens, the circle of confusion, near and far fields, scatter as gather on a Vogel disk, a premultiplied near field, tile dilation, the interaction with TAA's jitter; the errors (haloing, flicker at in-focus silhouettes) |
| `render-image:182` | feature | home | The five shaders and `Include/DepthOfField.slang`; `CameraLens` (`SceneRenderer.h:85-102`), `FromEntity` and the circle's math; `RenderDepthOfField` (`SceneRendererPost.cpp:815-860`); the camera's fields (`Strata/src/Strata/Scene/Components.h:142-150`); the limit: no circle of confusion wider than 2% of the image height (`c_DepthOfFieldMaxDiameter`, `Strata/src/Strata/Renderer/PostProcessData.h:111-113`; `Docs/Manual/Camera.md:145`); tested by `Renderer.CameraLens` and `GPU.SceneRenderer.DepthOfField`, whose cases prove the focus plane bit-identical to depth of field off and no more flicker under TAA than without the lens (`StrataTests/src/Renderer/GPUSceneDepthOfFieldTests.cpp:179, 181, 268`) |
| `render-image:423` | code | home | `Strata/src/Strata/Renderer/SceneRendererPost.cpp:254-299`: the thin lens's focal length from the field of view and the sensor; the circle of confusion |
| `new:9` | code | home | `Strata/shaders/PostProcess/DepthOfFieldGather.comp.slang:26-110`: Vogel samples turned per pixel; the pixel's own field and the near field, each with cover weights; the near field's coverage |
| `new:10` | code | home | `Strata/shaders/PostProcess/DepthOfFieldComposite.comp.slang:5-82`: the composite at full resolution: sharp within a pixel of focus, the fade from in-focus depth through group-shared memory that keeps the image stable under the jitter, the premultiplied near field over everything, alpha 1 where it changed |
| `render-image:473` | figure | home | Diagram: the thin lens, the circle of confusion against distance, near and far fields, the composite's fade near in-focus depth |
| `render-image:514` | figure | home | Depth of field off and on at f/2 on `tp.dof`, the sweep f/1.4 against f/8, focus on an entity |
| `render-image:601` | hands-on | home | Exercise: a racing camera with a 180 against a 90 degree shutter, focus on the car at f/2.8, and the players' rows |
| `new:25` | hands-on | home | Exercise (trace it yourself): with a search for `Lens =`, find every program that gives the renderer a lens (the runtime's `GameRenderer`, the editor's viewport renderer) and the conditions under which `RenderFrame` runs the depth of field; the reader says why a Scene view through the editor camera is never defocused. Evidence: `Strata/src/Strata/Runtime/GameRenderer.cpp:125`; `StrataEditor/src/Editor/ViewportRenderer.cpp:34, 227`; `Strata/src/Strata/Renderer/SceneRenderer.cpp:3588` |
| `render-image:718-720` | term | home | Circle of confusion; thin lens, f-number, focal length and sensor height; near field and far field |
| `render-image:722` | term | home | Scatter-as-gather |
| `scene-ecs:58` | feature | use | `CameraComponent`: this page teaches its depth-of-field fields, and `gpu/coordinates` the rest |
| `render-image:721` | term | use | The Vogel disk; its home is `basics/math-probability` |
| `render-image:189` | feature | use | The blur mask that the composite writes; its home is `image/motion-blur` |
| `render-image:238` | feature | use | The players' `DepthOfField` row, read in `RenderFrame` (`SceneRenderer.cpp:3588`) |
| `new:32` | feature | use | Which views show depth of field: every view and capture through a scene camera, playing or not; the editor camera never does |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The camera: `CameraComponent`, projection, field of view | `gpu/coordinates` | must |
| Temporal anti-aliasing: jitter and history | `image/taa` | must |
| Noise and sampling patterns: the Vogel disk | `basics/math-probability` | must |
| Compute shaders: shared memory, group barriers | `gpu/compute` | must |
| Projection: inverse projection and depth | `basics/math-projection` | must |
| Transparency, blending and premultiplied alpha | `light/clearcoat-transmission` | helps |
| The blur mask | `image/motion-blur` | helps |
| Handles instead of pointers; UUIDs as stable identities | `world/ecs` | helps |
| Players' graphics options and their rows | `image/quality-settings` | helps |

## `image/quality-settings` — Quality settings and players' graphics options

**Covers.** The job: keep a scene's look apart from a machine's cost, and let players choose within it. The page opens
with the Physics Playground's look-dev shot `pp.scene` at Low, Medium, High and Ultra (`render-image:515`): the scene
asks for no screen-space reflections, global illumination or motion blur, so the caption names what changes from the
generated table (the detail of its shadows, its ambient occlusion, its levels of detail, its sky's prefiltered
reflections), while its exposure, curve and grade stay as the scene set them. The full section "The problem and how
engines solve it": quality presets in engines, cost knobs against look controls, dynamic resolution and temporal
upscalers. This page is the home of Strata's first design
decision, never below native resolution (a `:::why` aside: no render scale below 1, no dynamic resolution, no temporal
upscaling; the price is a GPU cost that does not adapt, and MSAA and supersampling are the alternatives the Roadmap
keeps; `new:11`). The map (diagram `render-image:475`, which also draws the runtime's layering of `worlds-runtime:380`):
the section's default (High), the project's value, the players' choices, the `--quality` option; rows that follow the
preset, and the players' rows; `GameRenderer` pulls the result by its version. Medium is Strata 0.6.0's costs and
`SceneRendererSpecification`'s default, so tests, tools and perf scenes keep their cost and a new row's default is
Medium's value; High is the `Renderer.Quality` section's default, the programs' (`AGENTS.md`'s rule, with its reason).
The toy is a preset table and an override layer in about 40 lines.

The real code: code #30 (`PresetRow`, one line per knob with its four values; the row traits; `ApplyQualityOverrides` on
the frame's copy of the Post Process component), `RendererQualitySettings` and its enums, `GetPreset`, `Clamp`,
`ResolveShadowMapSize`, the `Renderer.Quality` section (`MakeSection`, `FromSectionValue`, `ToSectionValue`, its
version) and the live changes of `SetQuality`. The players' options: `IGameGraphics` (quoted from `EngineServices.h`),
`GameGraphicsService` and `GraphicsOptions.json`, written atomically and read within a bound, the value pulled when
asked by a version compare, so that the service does no work per frame; how a player's choices combine: a row that
follows the preset, when set, switches the player's preset to Custom from the look in effect, choosing a preset keeps
only the preset and the rows that do not follow it, each option reports its source (project, player or command line), a
reset of the preset also removes the rows that follow it, choices go by name and never by number, and a file that is no
options file is ignored with one warning while a load never rewrites it; the script SDK's `Graphics` (`Options`, `Get`,
`Set`, `SetPreset`, `Reset`, `Save`, with `GraphicsOption` and `QualityPreset`; the Manual's example) and its seven host
functions; who follows which quality (diagram `render-image:477`: the game, the Game view, the Scene view's chip,
captures, thumbnails and bakes, `--quality` and its log line). Figures: `render-image:517` (the Graphics Quality page
and the Scene view's chip; the Post Process inspector's TAA tunables are `editor-ui:560`'s picture, shown on
`image/taa`) and `render-image:519` (the Third-Person sample's Graphics menu). The rules: a quality row never changes a
look control (exposure, curve, grade) and never adds an effect, but scales or drops the cost of what a scene asks for
(some presets drop a scene's reflections or motion blur, others give global illumination to the scenes that ask for it;
the generated table shows which); the four comfort rows (`MotionBlur`, `DepthOfField`, `FilmGrain`,
`ChromaticAberration`) only turn off, and the `AntiAliasing` row is a preference that may turn anti-aliasing on and
choose its method, where the guide's table says otherwise (`new:12`); adding a row touches every place the guide lists
and bumps the section's version; only `GameGraphicsService` touches the options file. Each effect's own row and its cost
are taught on that effect's page; this page has the table as a whole, generated, and states no preset value in prose.
How it is tested: `Renderer.Quality`, `GPU.SceneRenderer.Quality` (`new:29`: `SetQuality` makes again only what a
changed knob sizes; changing the quality and back draws the same image), `Runtime.GameGraphics` and its sweep,
`Scripting.Graphics`, `Editor.GameGraphics`. The exercises trace a player's choice from a script to the renderer
(`new:26`) and add a quality row. At the end the reader can add a row, say what a player's choice overrides, and defend
native resolution.

**Leaves out.**

- Each effect's own quality row and its cost → `light/sun-shadows-1`, `light/local-shadows`, `indirect/ao`, `indirect/ssr`, `indirect/probes`, `indirect/gi-cascades`, `image/motion-blur`
- The script ABI and how host functions are added → `scripting/host-api`
- How the Graphics Quality page is drawn → `editor-ui/settings-windows`
- A game's settings screen and its Graphics row → `make/menus`, `make/quality`
- The runtime that owns the players' options in a shipped game → `worlds/runtime`
- Every measured cost and its budget → `reference/performance`
- Every row with its four preset values → `reference/renderer`

**Fit.** `fits`: about 5,400 words against L (5,000). The decision, the layers with their two diagrams, three excerpts
and the players' options with the rules of how their choices combine take the most words; each effect's row stays on
its own page. Phase B must read again the rows that wave 8 adds and changes
(reflections modes, probe resolution, global illumination, the section's version) and the presets table, which this
W8r page's named section holds, and the entry of "What Strata does not do" that the page states, rendering below native
resolution (`new:11`), a claim checked again at the pin move (rule 6).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-image:384` | concept | home | Quality presets as a product concept: look against cost, rows, presets, Custom, players' overrides, memory estimates; never below native as a policy with trade-offs; the errors (look controls in a row, players turning on an effect a scene never authored; the `AntiAliasing` row is a preference, not an effect, and may turn anti-aliasing on) |
| `render-image:227-260` | feature | home | `RendererQualitySettings` and its enums; Medium is 0.6.0's costs and the specification's default, so tests, tools and perf scenes keep their cost and a new row's default is Medium's value, and High is the section's default (`Strata/src/Strata/Renderer/RendererQuality.h:26-27`; `AGENTS.md:397`; `Docs/DeveloperGuide.md:4040-4045`); the preset table, `GetPreset`, `Clamp`, `ResolveShadowMapSize`; the `Renderer.Quality` section; the row traits and memory estimators; the players' rows: the four comfort rows (`MotionBlur`, `DepthOfField`, `FilmGrain`, `ChromaticAberration`, `SceneEffectChoice`) only turn off, and the `AntiAliasing` row (`AntiAliasingChoice`) is a preference that may turn anti-aliasing on and choose its method (`SceneRendererPost.cpp:458-486`); `SetQuality`; who follows what; `IGameGraphics` (`Strata/src/Strata/Core/EngineServices.h:152-184`), `GameGraphicsService` and the options file, and how a player's choices combine (a row that follows the preset switches the player to Custom from the look in effect; a preset keeps only the preset and the rows that do not follow it; each option's source; reset; names, never numbers; a bad file ignored with one warning and never rewritten by a load: `EngineServices.h:139-183`, `StrataScriptCore/Include/StrataScript/ScriptABI.h:705-725`, `Docs/DeveloperGuide.md:4123-4152`); the script SDK and its host functions; the editor's page, chip and commands; `--quality` and its log line; no render scale |
| `render-image:424` | code | home | `Strata/src/Strata/Renderer/RendererQuality.cpp:32-55`: the presets as a row per knob; with 156-179, the row traits; with `SceneRendererPost.cpp:458-486`, the players' overrides applied to the frame's copy |
| `render-image:565`, `render-image:567` | rule | home | Quality rows never change a scene's look, said precisely: a row never changes a look control (exposure, curve, grade) and never adds an effect, but scales or drops the cost of what a scene asks for (presets drop a scene's reflections or motion blur, or give global illumination to scenes that ask for it: `RendererQuality.cpp:52-54`, `SceneRendererPost.cpp:480`); the four comfort rows only turn off, and the `AntiAliasing` row is a preference that may turn anti-aliasing on and choose its method; adding a quality row, every place it touches |
| `render-image:572` | rule | home | Only `GameGraphicsService` touches `GraphicsOptions.json`: written atomically, read at most 64 KiB, validated |
| `render-image:475`, `render-image:477` | figure | home | Diagrams: the quality layers from the section's default to `--quality`; where quality is chosen in the editor |
| `render-image:515-519` | figure | home | The look-dev shot `pp.scene` at the four presets (the sweep): the Physics Playground asks for no screen-space reflections, global illumination or motion blur, so the caption names what changes from the generated table (shadows, ambient occlusion, levels of detail, the sky's prefiltered reflections) (`Samples/PhysicsPlayground/Assets/Scenes/Main.stscene:6`: `ScreenSpaceReflections` and `MotionBlur` false, no `GlobalIllumination`, whose default is false at `Strata/src/Strata/Renderer/RendererComponents.h:295`; `Tools/LookDev/Shots.json:19`); the editor's Graphics Quality page and quality chip (the Post Process inspector's TAA tunables are dropped here: `editor-ui:560` shows them, captured once, and `image/taa` uses it); the Third-Person sample's Graphics menu |
| `render-image:625` | hands-on | home | Exercise: add a quality row (a cap on the bloom's levels, or the depth of field's samples), with its traits, memory estimate, section version and feature-test value |
| `new:26` | hands-on | home | Exercise (trace it yourself): follow one `Graphics::Set` of a script from the SDK through the host function and `GameGraphicsService::SetOption` to the version that `GameRenderer::FollowQuality` compares and the call of `SceneRenderer::SetQuality`; the reader says on which frame the change shows and what a frame with no change costs. Evidence: `StrataScriptCore/Include/StrataScript/Graphics.h:180-188`; `Strata/src/Strata/Scripting/ScriptHostAPI.cpp:3238-3300`; `Strata/src/Strata/Runtime/GameGraphicsService.cpp:502`; `Strata/src/Strata/Runtime/GameRenderer.cpp:57-78` |
| `render-image:728-732` | term | home | Quality preset, row and knob; Custom; row traits; players' rows; graphics options |
| `render-image:734` | term | home | Render scale, dynamic resolution and temporal upscaling |
| `new:29` | feature | home | How it is tested, beside the suites the inventory names: `GPU.SceneRenderer.Quality`, whose cases check that `SetQuality` makes again only what a changed knob sizes and that changing the quality and back draws the same image. Evidence: `StrataTests/src/Renderer/GPUSceneQualityTests.cpp:110, 197, 297` |
| `new:12` | erratum | home | The Developer Guide's table says that the five players' rows (`AntiAliasing`, `MotionBlur`, `DepthOfField`, `FilmGrain`, `ChromaticAberration`) only turn off what a scene uses. At the pin the four comfort rows only turn off (`SceneEffectChoice`), and the `AntiAliasing` row can also choose FXAA, TAA or Morphological, which turns anti-aliasing on for a scene that has it off, as the Manual says; the page states what the code does. Evidence: `Docs/DeveloperGuide.md:4031`; `Strata/src/Strata/Renderer/RendererQuality.h:55-70, 173-177`; `Strata/src/Strata/Renderer/SceneRendererPost.cpp:458-486`; `Docs/Manual/AntiAliasing.md:58-59` |
| `new:11` | not-done | home | Rendering below native resolution, dynamic resolution, temporal upscalers: left out by decision (the first design decision). Evidence: `Docs/Roadmap.md:1642-1643`; `Docs/Releases/0.7.0.md:408-409`, run again at the pin |
| `scripting:130` | feature | home | The SDK's `Graphics`, `GraphicsOption` and `QualityPreset` (`StrataScriptCore/Include/StrataScript/Graphics.h:18-107`): players' graphics options by name, presets, reset, save |
| `worlds-runtime:92` | feature | home | Graphics options from scripts: `Graphics::Options`, `Get`, `Set`, `SetPreset`, `Reset` and `Save` reach `IGameGraphics` |
| `worlds-runtime:135` | feature | home | `GameGraphicsService` as `IGameGraphics`: the project's quality, the player's `GraphicsOptions.json` and `--quality`; the value pulled when asked, an integer compare when nothing changed, no per-frame work (`Strata/src/Strata/Runtime/GameGraphicsService.h:43-46`); the rules by which a player's choices combine, as the service applies them: a row that follows the preset switches the player to Custom from the look in effect, a chosen preset keeps only the preset and the rows that do not follow it, each option's source, the resets, choices by name, and a bad options file ignored with one warning and never rewritten by a load (`Docs/DeveloperGuide.md:4123-4152`) |
| `worlds-runtime:380` | figure | home | The graphics option layering, the project's `Renderer.Quality` under the player's file under `--quality`: drawn as one diagram with `render-image:475`, with the versions `GameRenderer` pulls |
| `worlds-runtime:451` | rule | home | Only `GameGraphicsService` touches `GraphicsOptions.json`, in the runtime area's words: one owner of a player's file avoids conflicting writes and keeps validation in one place |
| `worlds-runtime:565` | term | home | Graphics preset |
| `render-image:574` | rule | use | The native-resolution half of the rule; its temporal half is taught by `image/taa` |
| `render-image:426` | code | use | The Manual's example of the SDK's `Graphics` (`Docs/Manual/Graphics.md:99-109`), one of the short snippets |
| `render-image:733` | term | use | Settings section; its home is `world/projects-settings` |
| `render-image:603` | hands-on | link | A Graphics options menu made by a game maker; `make/quality` |
| `editor-core:97` | feature | use | `graphics.resetPlayerOptions` |
| `editor-ui:229` | feature | link | The Graphics Quality page's drawing; `editor-ui/settings-windows` |
| `render-direct:189` | feature | link | `ShadowResolution`, a row taught on its feature's page |
| `render-scene:183` | feature | link | The render-scene area's quality rows, taught on their pages |
| `render-indirect:138`, `render-indirect:163` | feature | link | The reflections and global illumination rows, taught on their pages |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Projects and settings sections: versions, validation, `IProjectSettings` | `world/projects-settings` | must |
| Engine services and engine modules | `core/engine-modules` | must |
| Temporal anti-aliasing | `image/taa` | must |
| Files you can trust: atomic writes, private files | `core/files` | must |
| Sun shadows (rows of the table) | `light/sun-shadows-2` | helps |
| A script at the use level: a call into the SDK | `basics/programming-1` | helps |
| A script at the use level: a class | `basics/programming-3` | helps |
| The host API: engine services behind a C table | `scripting/host-api` | helps |
| Inactive reasons: a property that another property turns off (`SetInactiveReason`) | `world/reflection` | helps |
| Running an editor command from a line to paste | `start/how-to-read` | helps |
| The runtime: `GameRuntime` | `worlds/runtime` | helps |
| Readback and GPU timestamps and stages | `gpu/readback-timing` | helps |
| Reflection: properties with titles and descriptions | `world/reflection` | helps |

## `image/tutorial-post-effect` — Tutorial: adding a post effect

**Covers.** What you will make: a post effect of the reader's own, end to end: a letterbox, the first of the two effects
the engine-developer hands-on proposes, black bars that crop the image to a wider aspect, with a picture of it off and
on rendered from the tutorial's patch. Its neutral value (off) leaves the image exact and its GPU test checks exact
pixels; no letterbox pass exists in the renderer at the pin (the editor's letterboxing of the Game view's panel is
another thing, named in one sentence). What you need: the source build of `core/first-change` and the GPU test of
`gpu/first-triangle`. The step sections, each ending in a checkpoint of the patch whose result is a build or test
output: (1) a property on the Post Process component, registered with its range, and an inactive reason where another
property turns it off; (2) its parameters by push constants in `PostProcessData.h`, never by new `FrameConstants` fields,
with a static_assert of their layout; (3) the shader, listed in `strata_add_shaders`; (4) the pass in
`SceneRendererPost.cpp`, between the TAA resolve and the tone mapping, reading the frame's `PostSource` through one
binding set per source and becoming the next source (code #2 is walked here as the place where it goes); when its
resources cannot be made, the pass returns failure and `RenderFrame` sets `degraded`, as the other passes do, and the
frame goes on without it; (5) off in
`Tests::AddNeutralPostProcess` and bit-identical at its neutral value; (6) the GPU stage it belongs to, `GPU.Post` or a
stage of its own; (7) a GPU test with `Tests::GPUContext`, `ExactSpecification` and the error count; (8) a value in the
feature test.

Each change is quoted from the patch, and each "You should see" is the build or test output as a text capture; the last
checkpoint shows the effect in the editor's viewport after the property is set in the inspector. The two rules of the
inventory frame the steps: post passes take their parameters by push constants or by buffers of their own, and a new
effect runs between the TAA resolve and the tone mapping, reads the post source, is off in the neutral helper and keeps
the image bit-identical at its neutral value. At the end the reader can add a post effect that passes the review
checklist. The bottom strip's exercises are open extensions: bars of a color the component sets (`new:27`), and a GPU
stage of the effect's own (`new:28`).

**Leaves out.**

- Why the chain has this order and these rules → `image/why-post`
- Every preset, configuration and option of the build → `engineering/building`
- The feature test in full → `engineering/feature-test`
- The GPU suites and the tests that compare exact pixels → `engineering/test-kinds`
- Registering a GPU stage in general → `gpu/readback-timing`

**Fit.** `fits`: about 4,350 words against L (5,000). Eight step sections, each with its patch quote and its text
capture, and the walk of code #2 in step 4 take the most words; the two open exercises add about 450.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-image:618` | hands-on | home | The tutorial's subject, a letterbox (R32, D43): a new post effect with push constants, `PostSource` sets, off in `AddNeutralPostProcess`, bit-identical at neutral, a GPU stage only if its own, the feature test; no letterbox pass exists at the pin (`git grep -n -i letterbox 822a7a46 -- Strata/src/Strata/Renderer Strata/shaders` finds nothing) |
| `render-image:396` | code | home | `Strata/src/Strata/Renderer/SceneRenderer.cpp:3582-3629`: the post block of `RenderFrame`: the source switching from HDR to History, DepthOfField and MotionBlur, the key's reference, the sun's place on screen; where the new pass goes |
| `render-image:49` | feature | home | The post passes' GPU data in `PostProcessData.h`: constant buffers, push constants, slots, static_asserted offsets |
| `render-image:273` | feature | home | `Tests::AddNeutralPostProcess`, `AddTemporalPostProcess` and `ExactSpecification` (`SceneRendererTestUtils.h:237-277`) |
| `render-image:535`, `render-image:542` | rule | home | Post passes take parameters by push constants or their own buffers, never new `FrameConstants` fields; a new post effect runs between the TAA resolve and the tone mapping, reads the frame's `PostSource`, is off in `AddNeutralPostProcess` and bit-identical at its neutral value |
| `new:27` | hands-on | home | Exercise (extend, make it yours): bars of a color the component sets, a second property with its range, its push constant and its feature-test value; the GPU test reads a bar's pixel, and the neutral value still renders bit-identically. The worked solution is a patch against the tutorial's last checkpoint. Evidence: the patch chain starts at the pin (`pipelines.md` §6.6); `StrataTests/src/Renderer/SceneRendererTestUtils.h:251` (`AddNeutralPostProcess`) |
| `new:28` | hands-on | home | Exercise (extend): give the letterbox a GPU stage of its own beside `GPU.Post`, read its time in `viewport.capture`'s `gpuMs`, and say when a stage of its own is worth its line in every profile. Evidence: `Strata/src/Strata/Renderer/GPUProfiler.cpp:44-66` (the stages registered in one order); `StrataEditor/src/Editor/EditorViewportCommands.cpp:1244` (`viewport.capture` reports `gpuMs` per stage) |
| `render-image:38` | feature | use | `PostSource` and `SelectPostSet` |
| `render-image:46` | feature | use | `DrawFullscreen` and `GetFullscreenPipeline`, for an effect drawn as a fragment pass |
| `render-image:545` | rule | use | Neutral settings render bit-identically |
| `render-image:426` | code | use | `AddNeutralPostProcess` (`StrataTests/src/Renderer/SceneRendererTestUtils.h:248-267`), one of the short snippets |
| `render-image:723` | term | use | Post source |
| `new:31` | feature | use | The chain's failure path in step 4: the new pass returns failure and sets `degraded` as the other passes do |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Building Strata from source; one test case written and run | `core/first-change` | must |
| Writing a GPU test: the shared `GPUContext`, the error count, pixel readback | `gpu/first-triangle` | must |
| Why images need post-processing; the post chain, `PostSource`, the fullscreen pass | `image/why-post` | must |
| Temporal anti-aliasing: the resolve that the effect follows | `image/taa` | must |
| The shader build: writing and registering a shader | `gpu/shaders` | must |
| Pipelines and binding: push constants | `gpu/binding` | must |
| Readback and GPU timestamps and stages | `gpu/readback-timing` | must |
| Reflection: registering a component's property | `world/reflection` | must |
| The feature test's minimum | `world/tutorial-component` | must |
| A feature that is off is invisible bit for bit | `gpu/frame-tour` | must |
| Neutral settings render bit-identically | `image/grading` | must |

**Starting state.** The engine's source at the pin, configured and built in Debug as `core/first-change` builds it, with
the unit tests and the GPU suites passing (the test of `gpu/first-triangle` runs). The page starts from no checkpoint of
an earlier tutorial: its patch chain starts at the pin and is not part of WindZone's. The tutorial's patch and its
stages are written with the page (`pipelines.md` §6.6). Every step changes code or runs CMake, the build and `ctest` in
a terminal; the effect is turned on in the editor's inspector.

**Command-only steps.** none

## Passed on

| Item | Type | To | Why |
| --- | --- | --- | --- |
| `render-image:30` | feature | `light/brdf` | `book.md` puts the home of `SanitizeHDR` on `light/brdf`, the first pass that writes HDR values; `image/why-post` names it in one sentence |
| `render-image:724` | term | `gpu/coordinates` | The fullscreen triangle is taught there with its code and exercise (`render-core:139`); `image/why-post` keeps `DrawFullscreen` and `Copy.frag` and links the triangle in one sentence (critic-render-image-7). "Post source" (`render-image:723`) stays on `image/why-post` |
| `render-image:397` | code | `light/brdf` | Code #3, `SanitizeHDR` itself (`Common.slang:49-57`), goes with its home |
| `render-image:525` | rule | `light/brdf` | Every HDR writer clamps with `SanitizeHDR`: the rule of its home |
| `render-image:640` | term | `light/brdf` | The term `SanitizeHDR` goes with its home |
| `render-image:57` | feature | `reference/renderer` | The list of statistics and their `renderStats` keys is reference material, generated there; each page of the part names its own statistics |
| `render-image:97` | feature | `light/units-exposure` | Light units are the home of "light in real units" |
| `render-image:641` | term | `light/units-exposure` | Nit, lux and candela are defined with the units |
| `render-image:99` | feature | `light/sky` | Sky presets, and what they do to exposure, are taught with the presets |
| `render-image:101` | feature | `light/measuring-light` | The luminance view's home is the page of the lighting views |
| `render-image:171` | feature | `draw/motion-vectors` | The velocity target is made by the render-scene area; this part only reads it |
| `render-image:174` | feature | `draw/motion-vectors` | The motion view is read where motion vectors are taught |
| `render-image:368` | concept | `draw/motion-vectors` | Motion vectors and their unjittered matrices are taught there; `image/taa` recalls them in one paragraph |
| `render-image:512` | figure | `draw/motion-vectors` | The motion view's figure belongs to its home |
| `render-image:555` | rule | `draw/motion-vectors` | Motion vectors use unjittered matrices built in double: a rule of how they are made |
| `render-image:702` | term | `draw/motion-vectors` | Motion vector and velocity target |
| `render-image:703` | term | `draw/motion-vectors` | Motion history |
| `render-image:282` | feature | `light/sun-shadows-2` | The blue noise is the sun's shadow filter's; `image/encoding` links it as a contrast case |
| `render-image:286` | feature | `engineering/look-dev` | The look-dev harness has its own page; the image pages use its shots |
| `render-image:736` | term | `engineering/look-dev` | Look-dev |
| `render-image:603` | hands-on | `make/quality` | A Graphics options menu written as a script is a game maker's task, and `make/quality` is the use home of players' graphics options |
| `render-image:638` | term | `basics/color` | The half-float range is the home of `basics/color` |
| `render-image:642` | term | `basics/color` | Luminance as a weighted sum of linear Rec. 709 values is color science of the primer |
| `render-image:670` | term | `basics/color` | D65, the white point of sRGB |
| `render-image:675` | term | `basics/color` | The home of the sRGB transfer function |
| `render-image:639` | term | `basics/numbers` | NaN and Inf belong to floating point |
| `render-image:691` | term | `basics/signals` | Aliasing in general is the primer's |
| `render-image:721` | term | `basics/math-probability` | The Vogel disk is one of the sampling patterns of the primer; the sun shadows and depth of field both use it |
| `render-image:682` | term | `assets/textures` | Mips and mip chains are taught with textures; the bloom's pyramid links them |
| `render-image:654` | term | `gpu/readback-timing` | Readback has its home there |
| `render-image:725` | term | `gpu/binding` | Push constants are a binding concept; the volatile constant buffer the item also names is one entry with `render-core:708` on `gpu/resources-lifetimes`, which `gpu/binding`'s row links (duplicates.md, "Volatile constant buffer") |
| `render-image:726` | term | `gpu/binding` | std140 is a layout rule of constant buffers |
| `render-image:727` | term | `gpu/how-a-gpu-frame-works` | Uniform and divergent branches are taught with how a GPU runs waves |
| `render-image:733` | term | `world/projects-settings` | Settings sections have their home there; `Renderer.Quality` is one of them |
| `render-image:783` | open | `nowhere` | A surveyor's note about shader bodies it did not read; the writers read them at the pin (the excerpts of `new:5`, `new:7`, `new:9` and `new:10` were read for this file) |
| `render-image:787` | open | `nowhere` | A surveyor's note: parts of `RendererQuality.cpp` read only by their signatures |
| `render-image:789` | open | `nowhere` | A surveyor's note: the players' options service, the host functions and the editor's page located, not read |
| `render-image:792` | open | `nowhere` | A surveyor's note: the color lookup's code known from the guide only; `new:3` was read at the pin for this file |
| `render-image:793` | open | `nowhere` | A surveyor's note: only test names were read |
| `render-image:796` | open | `nowhere` | A surveyor's note: sections of the guide and the architecture not read |
| `render-image:798` | open | `nowhere` | A note to the planner; its two real drifts are the errata `new:2` (`image/grading`) and `new:8` (`image/taa`), checked at the pin; the third is no drift, because `RenderData::c_TemporalSkyDistance` exists (`SceneRenderData.h:542`, 65504) and the TAA shader keeps a local constant of the same value |
| `render-image:804` | open | `nowhere` | A surveyor's note on release dates; each writer finds a page's `since` from the release tags (`process.md`, the notes' `## Since`) |
| `render-image:808` | open | `nowhere` | A surveyor's note that the GPU costs came from the documents; pages take costs from the generated tables and `values.json` |
| `render-image:810` | open | `nowhere` | Ownership questions that this file settles: depth of field on `image/depth-of-field`, motion vectors on `draw/motion-vectors`, light units on `light/units-exposure`, each effect's quality row on its own page, the blue noise on `light/sun-shadows-2` |

## Not taken

none

## Questions for the planner

none
