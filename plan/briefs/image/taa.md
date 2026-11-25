# Brief: `image/taa`

| Field | Value |
| --- | --- |
| Title | Temporal anti-aliasing |
| Kind | I |
| Size | XL |
| Tracks | E |
| Needs | `image/spatial-aa`, `draw/motion-vectors`, `basics/math-projection` |
| From | render-image ch. 9; 1.8 (jitter on the frame's camera copy, history, reprojection, Catmull-Rom, clamping and clipping, the reactive mask, sharpening, settling); home of "nothing needs history to look right" |
| Unit | `plan/allocation/image.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `camera-cut` | Camera cut | - |
| `catmull-rom-filter` | Catmull-Rom filter | - |
| `disocclusion` | Disocclusion | - |
| `ghosting` | Ghosting | - |
| `golden-ratio-turn` | Golden-ratio turn | - |
| `halton-sequence` | Halton sequence | - |
| `history` | History | TAA history |
| `jitter` | Jitter | - |
| `jitter-taa` | Jitter (TAA) | - |
| `neighborhood-clamp` | Neighborhood clamp | - |
| `radical-inverse` | radical inverse | - |
| `reactive-mask` | Reactive mask | - |
| `reprojection` | Reprojection | - |
| `resampling-blur` | Resampling blur | - |
| `settle-frames` | Settle frames | - |
| `sharpening-taa` | Sharpening (TAA) | - |
| `taa` | TAA | - |
| `variance-clipping` | variance clipping | - |
| `ycocg` | YCoCg | - |
