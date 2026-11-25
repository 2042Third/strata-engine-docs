# Brief: `image/why-post`

| Field | Value |
| --- | --- |
| Title | Why images need post-processing, and Strata's post chain |
| Kind | C |
| Size | M |
| Tracks | E |
| Needs | `gpu/frame-tour`, `light/brdf` |
| From | render-image ch. 1; 1.1 whole (the HDR target, the chain's order, `PostSource`, the fullscreen pass, the CPU twins in `PostProcessMath`); code #1, and a few lines of code #2, which `image/tutorial-post-effect` walks whole; code #3 (`SanitizeHDR`) is `light/brdf`'s |
| Unit | `plan/allocation/image.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `display-linear` | display-linear | - |
| `encoded` | encoded | - |
| `hdr-image` | HDR image | - |
| `ldr` | LDR | display-referred |
| `post-source` | Post source | - |
| `srgb-encoding` | sRGB encoding | - |
| `tone-mapping-image` | tone mapping (image) | tone curve |
