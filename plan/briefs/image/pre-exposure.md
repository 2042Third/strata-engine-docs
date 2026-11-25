# Brief: `image/pre-exposure`

| Field | Value |
| --- | --- |
| Title | Pre-exposure |
| Kind | I |
| Size | M |
| Tracks | E |
| Needs | `image/exposure`, `basics/numbers`, `gpu/readback-timing` |
| From | render-image ch. 3; 1.2 (power-of-two scaling, asynchronous readbacks, epochs, settling, the TAA rescale); render-direct code #36 (`ChoosePreExposure`); the mechanism of "light in real units" |
| Unit | `plan/allocation/image.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `pre-exposure` | Pre-exposure | - |
