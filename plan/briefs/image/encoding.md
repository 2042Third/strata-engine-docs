# Brief: `image/encoding`

| Field | Value |
| --- | --- |
| Title | Encoding, dithering and grain |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `image/grading`, `basics/signals` |
| From | render-image ch. 6; 1.5 (sRGB encoding, banding, TPDF dither, film grain, the 10-bit intermediate); a forward sentence on FXAA and grain |
| Unit | `plan/allocation/image.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `10-bit-intermediate-r10g10b10a2` | 10-bit intermediate (R10G10B10A2) | - |
| `dither` | Dither | - |
| `film-grain` | Film grain | - |
| `noise-modulation` | Noise modulation | - |
| `tpdf` | TPDF | - |
