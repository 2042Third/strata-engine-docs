# Brief: `basics/signals`

| Field | Value |
| --- | --- |
| Title | Sampling, aliasing and filtering |
| Kind | P |
| Size | L |
| Tracks | B, E |
| Needs | `basics/math-interpolation`, `basics/color` |
| From | new; curricula 1.2 ("Signals"); sampling and Nyquist, kernels, mip prefiltering, ordered dither, spatial denoising; noise and sampling patterns are `basics/math-probability`'s |
| Unit | `plan/allocation/basics-b.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `basics/signals` — Sampling, aliasing and filtering

**Covers.** In order: (1) a signal and its samples: the brightness along a row of pixels, the pressure of a sound,
measured at separate places or moments; frequency as repeats per second or per metre, with the sine wave of
`basics/math-vectors`; (2) sampling and the sample rate, and reading between samples again: nearest reads and linear
reads, bilinear in two dimensions (bilinear filtering of a texture), whose mathematics `basics/math-interpolation`
taught; (3) the Nyquist limit and aliasing: a frequency above half the sample rate shows up as a false, lower one (a
wheel that turns backward on film, moiré on a fine fence, stair steps along edges, shimmer as the camera moves), and why
sound is sampled 48,000 times a second; (4) filtering: a weighted average of nearby samples, the filter kernel (box,
tent, Gaussian) whose weights add to 1, and convolution as sliding the kernel along the signal; (5) prefiltering:
filtering before sampling, so that nothing above the limit is left; mips as prefiltered copies of a picture, each half
the size of the one before, and choosing the mip whose texels match the pixel; (6) resampling a picture with a filter:
a box filter against a wider one (Strata's texture cooker makes its mips with a Mitchell filter on linear values); (7)
quantization and dithering: rounding to 256 levels bands, and a small planned offset added first turns the bands into
fine grain; ordered dither with the 4×4 Bayer table, which Strata also uses to fade between two levels of detail; (8)
spatial denoising: averaging each pixel with similar neighbors, with weights that stop at edges.

Figures: a sine sampled above and below the Nyquist limit, a checkered floor drawn with and without mips, one signal
under a box, a tent and a Gaussian kernel, a gradient quantized, dithered with noise and with the Bayer table, the Bayer
table itself. The common mistakes: filtering after sampling, a kernel whose weights do not add to 1, a mip chain built
from sRGB values, a dither that changes every frame where a still picture is wanted. Practice (three to eight
exercises, `style.md` §8) ends with the optional Coin Run item: a coin turned by 350° each frame (not scaled by
`deltaTime`) seems to turn 10° backward each frame, the wagon wheel of aliasing; the reader predicts what 370° and 180°
per frame look like, then tries them. "Where the book uses it" names `assets/textures`, `image/spatial-aa`,
`light/shadow-basics`, `indirect/ao` and `audio/sound-in-a-computer`.

**Leaves out.**

- Mips, texture reads and their filters in Strata → `assets/textures`
- How Strata cooks mips → `assets/texture-cooking`
- Anti-aliasing methods: FXAA, morphological AA and TAA → `image/spatial-aa`
- The final picture's dither → `image/encoding`
- Noise and sampling patterns → `basics/math-probability`
- The LOD cross-fade and its masks → `draw/lod`
- The edge-aware blurs of shadows → `light/sun-shadows-2`
- Sound as samples in Strata's audio → `audio/sound-in-a-computer`
- Lerp and bilinear interpolation as mathematics → `basics/math-interpolation`

**Fit.** `fits`: about 5,100 words against L (5,000). The eight ideas at 400 to 600 words take the most (3,800); the
Bayer excerpt (200) and the fixed parts with the Test out box, Practice and the Coin Run item (1,100) take the rest.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:87` | concept | home | Signals and signal samples; frequency. General knowledge. |
| `new:88` | concept | home | Sampling and the sample rate; nearest, linear and bilinear reads between samples. General knowledge. |
| `new:89` | concept | home | The Nyquist limit and aliasing: false low frequencies, moiré, stair steps, shimmer. Figure: a sine sampled above and below the limit. General knowledge. |
| `new:90` | concept | home | Filtering, filter kernels (box, tent, Gaussian) and convolution. Figure: one signal under three kernels. General knowledge. |
| `new:91` | concept | home | Prefiltering, and mips as prefiltered copies of a picture; choosing a mip. Figure: a floor with and without mips. General knowledge. |
| `new:92` | concept | home | Resampling a picture with a filter: box against wider filters. General knowledge. |
| `new:93` | concept | home | Quantization and dithering; ordered dither with the 4×4 Bayer table. Figure: a gradient quantized, dithered and ordered-dithered. General knowledge. |
| `new:94` | concept | home | Spatial denoising: averaging similar neighbors, weights that stop at edges. General knowledge. |
| `new:95` | hands-on | home | Coin Run practice, from `make/project-coin-run`'s end state: a coin turned by a fixed angle per frame (350°, 370°, 180°) to see aliasing at the frame rate. Evidence: `StrataEditor/src/Editor/ScriptProject.cpp:246-250` (the `Spinner`'s turn in `OnUpdate`) |
| `render-image:691` | term | home | Aliasing: artifacts from undersampling (stair steps, crawling, shimmer); one glossary entry with the seed's |
| `render-scene:605` | term | home | Ordered dither and the Bayer matrix, a fixed 4×4 pattern of thresholds 0 to 15; one glossary entry with the seed's |
| `render-scene:360` | code | use | The Bayer table of `IsLODFadeDrawn`, `Strata/shaders/Include/Scene.slang:155-166`, read as an ordered dither; the fade itself is `draw/lod`'s |
| `assets:155` | feature | use | Strata's texture cooker: mips filtered with a Mitchell filter on linear values |
| `assets:716` | term | link | The Mitchell and the box filter, defined on `assets/texture-cooking` |
| `render-image:677` | term | link | Dither and TPDF, as the final picture's encoding uses them, on `image/encoding`; dither's idea and the seed's entry stay this page's (book.md's row of display encoding; basics-b-q8) |
| `render-direct:737` | term | link | The edge-aware (bilateral) blur, defined on `light/sun-shadows-2` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Sine waves, their amplitude and period | `basics/math-vectors` | must |
| Lerp, weighted averages and bilinear interpolation | `basics/math-interpolation` | must |
| Quantization to 8 bits, banding, linear and sRGB values | `basics/color` | must |
| Powers of two and the base-2 logarithm (the number of mips) | `basics/numbers` | must |
| A pixel and a frame | `start/what-an-engine-is` | helps |
| A script of the playground: `OnUpdate` and `Log::Info` | `basics/programming-1` | must |

**Starting state.** The optional Coin Run item of Practice starts from the download of `make/project-coin-run`'s end
state, as the outline's introduction of part `basics` says for every primer after `basics/debugging`: Coin Run as
`make/project-coin-run` finishes it, with the rolling ball, the spinning coins, the HUD, the sounds, winning, losing and
the restart. The page's other examples and exercises run in the playground (`style.md` §8), which is no checkpoint.

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `aliasing` | aliasing | - |
| `convolution` | convolution | - |
| `denoising` | denoising | spatial denoising |
| `dithering` | dithering | - |
| `filter-kernel` | filter kernel | convolution kernel |
| `filtering` | filtering | - |
| `frequency` | frequency | - |
| `nyquist-limit` | Nyquist limit | Nyquist frequency |
| `ordered-dither` | ordered dither | Bayer dither, Ordered dither (4x4 Bayer order), Bayer matrix |
| `prefiltering` | prefiltering | - |
| `sample-rate` | sample rate | sampling rate |
| `sampling` | sampling | - |
| `signal` | signal | entt signal, Signal (on_update) |
| `signal-sample` | signal sample | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-basics-b-4 | should | order | `new:24` (`basics/math-bases`); `render-image:130`, `render-image:642` (`basics/color`); `render-scene:360` (`basics/signals`); `new:107`, `render-core:459` (`basics/math-probability`); `new:117`, `new:118`, `render-indirect:245` (`basics/math-sphere`) | Five pages quote Strata's shaders, which are written in Slang. No page before them teaches how to read Slang: `gpu/shaders` does, after part `basics` on track E and never on track B. No Assumes row names it, and style.md has a rule for Python fences but none for shader fences. The quotes rest on what differs from C++ and glm: `float3`, `float3x3` whose constructor takes rows (the point of `TangentBasis`), `mul`, swizzles such as `.yx`, `frac`, `select`, `reversebits`. | The first shader quote of each of the five pages is introduced by two or three sentences on what in it differs from C++ and glm, and each shader quote is followed by its explanation line by line, as R31 asks of Python (about 60 words a page). See forPlanner for a rule in style.md §9.1. | `allocation/basics-b.md:212`, `:697`, `:699`, `:779`, `:868`, `:878`, `:957-958`, `:963`; `allocation/gpu.md:189`, `:238`; `style.md:634-636`, `:679`; `tracks.md:208`; `Strata/shaders/Include/IBL.slang:41-48`; `Strata/shaders/Include/Common.slang:25-39`; `Strata/shaders/Include/Scene.slang:362-377` |
