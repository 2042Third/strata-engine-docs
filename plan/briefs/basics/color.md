# Brief: `basics/color`

| Field | Value |
| --- | --- |
| Title | Color and light for programmers: linear, sRGB and HDR |
| Kind | P |
| Size | L |
| Tracks | B, E |
| Needs | `basics/numbers`, `basics/math-matrices` |
| From | new; linear and sRGB values, chromaticity, white point and gamut, the working color space (scene-linear Rec. 709); home of the sRGB transfer function and of the half-float range |
| Unit | `plan/allocation/basics-b.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `basics/color` — Color and light for programmers: linear, sRGB and HDR

**Covers.** In order: (1) a color as numbers: red, green and blue color channels from 0 to 1, stored in a file as 0 to
255 each (RGBA8, eight bits per channel, the display colors of a picture or a thumbnail), and alpha as a fourth channel
for opacity; (2) linear color: values in proportion to the amount of light, so that adding two lights adds their values
and averaging works; (3) why pictures are not stored that way: the eye tells more dark shades apart, so 256 levels
spread evenly over the light would band in the shadows; gamma encoding, quantization and banding; (4) the sRGB
transfer function, exactly (the straight piece below 0.0031308 and the 2.4 power above it), decoding and encoding, read
in Strata's `LinearToSRGB` and `SRGBToLinear`; which data is sRGB (photographs, base colors, UI colors) and which is
linear (normal maps, roughness, masks), and why blending and filtering work on linear values; (5) high dynamic range:
scene-linear values with no top limit (the sun is thousands of times brighter than a white wall), which need floating
point; (6) half floats: 16 bits, values up to 65504, about three significant digits, and the subnormal values below
2^-14 that lose precision; (7) luminance: how bright a color looks, the weighted sum 0.2126 R + 0.7152 G + 0.0722 B of
linear Rec. 709 values, read in Strata's `Luminance`, against luma, the same kind of sum on encoded values; (8)
chromaticity: what a color is apart from its brightness, two numbers x and y on the horseshoe diagram of the colors the
eye sees; (9) primaries, white point and gamut: a color space as three primaries, a white (D65, daylight) and a transfer
function; Rec. 709 and sRGB share their primaries and white; colors outside a gamut; (10) the working color space:
Strata lights in scene-linear Rec. 709, and changing from one color space to another is a 3×3 matrix applied to
(r, g, b).

Figures: an 8-bit ramp stored linearly and in sRGB (banding in the first), the sRGB curve, a 50% blend done on linear
and on sRGB values, the chromaticity diagram with the Rec. 709 triangle and D65. The common mistakes: blending or
filtering sRGB values, a normal map marked as sRGB, a luma compared with a luminance, HDR values clamped at 1 too early.
Practice (three to eight exercises, `style.md` §8) ends with the optional Coin Run item: the time bar's color blended
from green to red, once on the sRGB values that UI colors are and once in linear (decode, lerp, encode), with the
luminance of each midpoint logged. "Where the book uses it" names `assets/textures`, `image/why-post`,
`image/tone-mapping`, `image/encoding` and `ui/drawing`.

**Leaves out.**

- Light units: lux, nits and exposure → `light/units-exposure`
- HDR targets, the post chain and pre-exposure in Strata → `image/why-post`
- Tone mapping from scene light to the screen → `image/tone-mapping`
- White balance and color grading → `image/grading`
- Quantizing the final picture, its dither and the 10-bit path → `image/encoding`
- sRGB texture formats and how the GPU decodes them → `assets/textures`
- Floating point and its bits → `basics/numbers`
- Dithering as an idea of signals → `basics/signals`
- Premultiplied alpha → `light/clearcoat-transmission`
- The editor's palette and theme tokens → `editor-ui/design-system`

**Fit.** `over`: about 7,500 words against L (5,000). The ten ideas from zero at 500 words each, the upper value for B0
(5,000), the four figures (600), the four common mistakes (480), the sRGB and `Luminance` excerpts (250), the opening
(100) and the fixed parts with the Test out box, Practice and the Coin Run item (1,100). A primer is at most L, so the
page splits (S3): `basics/color`, "Color for programmers: linear, sRGB and HDR" (L, about 5,900: ideas 1 to 7), and
after it `basics/color-spaces`, "Color spaces: chromaticity, white point, gamut and the working space" (M, about 2,900:
ideas 8 to 10, with the 3×3 matrix).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:76` | concept | home | Color channels from 0 to 1 and from 0 to 255 (RGBA8), and alpha as opacity. General knowledge. |
| `new:77` | concept | home | Linear color: values in proportion to light, which add and average. General knowledge. |
| `new:78` | concept | home | Gamma encoding, quantization and banding: why 8-bit pictures are not linear. Figure: a ramp stored linearly and in sRGB. General knowledge. |
| `new:79` | concept | home | The sRGB transfer function, decoding and encoding; sRGB data against linear data; blending and filtering on linear values. Figures: the sRGB curve, a 50% blend both ways. General knowledge. |
| `new:80` | concept | home | High dynamic range and scene-linear values. General knowledge. |
| `new:81` | concept | home | Half floats: range, precision and subnormals. General knowledge. |
| `new:82` | concept | home | Luminance as a weighted sum of linear Rec. 709 values, against luma on encoded values. General knowledge. |
| `new:83` | concept | home | Chromaticity: x and y, the diagram of visible colors. Figure: the chromaticity diagram. General knowledge. |
| `new:84` | concept | home | Primaries, white point and gamut; a color space; Rec. 709 and sRGB. General knowledge. |
| `new:85` | concept | home | The working color space, Strata's being scene-linear Rec. 709 (the primaries of sRGB), and a change of color space as a 3×3 matrix. Evidence: `Strata/src/Strata/Renderer/PostProcessMath.h:62` ("scene-linear sRGB light"), `Strata/shaders/Include/Exposure.slang:18-21` (luminance weights of linear Rec. 709) |
| `new:86` | hands-on | home | Coin Run practice, from `make/project-coin-run`'s end state: the time bar's color blended from green to red on sRGB values and in linear, with the luminance of both midpoints logged. Evidence: `StrataScriptCore/Include/StrataScript/UI.h:75` (UI colors are display sRGB values) and `:86` (`SetColor`) |
| `assets:712` | term | home | sRGB, the nonlinear encoding of color images, and why filtering happens on linear values; one glossary entry with the seed's |
| `render-image:675` | term | home | The sRGB transfer function, the piecewise 2.4 power; one glossary entry with the seed's transfer function |
| `render-direct:703` | term | home | Half float, RGBA16F and subnormals below 2^-14; one glossary entry with `render-image:638`, `render-core:757` and the seed's |
| `render-image:638` | term | home | Half float: largest value 65504, about three decimal digits |
| `render-core:757` | term | home | Half float (RGBA16F) as the GPU part's glossary words it: the 16-bit floating-point channel format of HDR targets, largest value 65504; one glossary entry with `render-direct:703` and `render-image:638`; `gpu/frame-tour` links |
| `render-image:642` | term | home | Luminance (Y), 0.2126 R + 0.7152 G + 0.0722 B of linear Rec. 709 values, shown with Strata's `Luminance` (`Strata/shaders/Include/Exposure.slang:18-21`) |
| `render-image:670` | term | home | D65, sRGB's white point (6504 K daylight) |
| `render-image:130` | feature | use | Strata's sRGB encoding and decoding, `Strata/shaders/Include/Common.slang:25-39`, read as the formula's code; its home is `image/encoding` |
| `gameui:52` | feature | use | The game UI's colors are display (sRGB) values, the space of the Coin Run item's blend |
| `editor-ui:60` | feature | use | The editor's palette as named sRGB tokens, an example of display colors with alpha |
| `render-image:643` | term | link | Luma as FXAA weighs encoded values, on `image/spatial-aa`; the general entry, luma, is this page's at the glossary step (basics-b-q8) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Bits and 8-bit unsigned integers (0 to 255) | `basics/numbers` | must |
| Floating-point numbers: sign, exponent and fraction; precision | `basics/numbers` | must |
| Powers and exponents | `basics/numbers` | must |
| A 3×3 matrix applied to three numbers | `basics/math-matrices` | must |
| A weighted sum of three numbers as a dot product | `basics/math-vectors` | helps |
| Lerp: blending two values by a weight | `basics/math-interpolation` | helps |
| A pixel | `start/what-an-engine-is` | helps |
| A script of the playground with `Log::Info` | `basics/programming-1` | must |
| A UI element's color set from a script | `make/hud` | helps |

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
| `banding` | banding | - |
| `chromaticity` | chromaticity | - |
| `color-channel` | color channel | - |
| `color-space` | color space | - |
| `d65` | D65 | - |
| `gamma-encoding` | gamma encoding | gamma |
| `gamut` | gamut | - |
| `half-float` | half-float | half precision |
| `high-dynamic-range` | high dynamic range | HDR |
| `linear-color` | linear color | - |
| `luminance` | luminance | - |
| `luminance-y` | Luminance (Y) | - |
| `quantization` | quantization | - |
| `rec-709` | Rec. 709 | BT.709 |
| `scene-linear` | scene-linear | - |
| `srgb` | sRGB | - |
| `srgb-transfer-function` | sRGB transfer function | - |
| `transfer-function` | transfer function | - |
| `white-point` | white point | - |
| `working-color-space` | working color space | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-basics-b-1 | must | stale-item | `new:79` and `new:85` on `basics/color` | The Covers counts base colors among the sRGB data. At the pin the material's Base Color and Emissive Color numbers are linear, and so are the light colors and the fog's color. The colors of UI images and UI texts, of the Text component and the camera's clear color are display (sRGB) values. The Inspector shows both kinds with one widget and the stored numbers, and only some tooltips say which kind a field is. A reader who types an sRGB color into a material gets a paler surface. | Idea (4) separates the two: base color maps are sRGB; the Base Color factor is linear, as glTF's factor is (the import setting Base Color Factors Are sRGB exists for exporters that get this wrong). Add a short table of Strata's color fields, linear or display, and a common mistake: sRGB numbers typed into a linear field. About 200 words. Add an erratum item: `Property.h:32-33` calls every color property linear, which the UI and text colors are not (see forPlanner). | `allocation/basics-b.md:636-638`, `:684`, `:690`; `Strata/src/Strata/Renderer/Material.h:26`; `Strata/src/Strata/Renderer/Material.cpp:30-35`; `Strata/src/Strata/Renderer/RendererComponents.cpp:285`, `:322`, `:418`, `:646`; `Strata/src/Strata/Renderer/RendererComponents.h:388`; `Strata/src/Strata/Scene/Components.h:140`; `Strata/src/Strata/GameUI/GameUIComponents.h:18-19`; `Strata/src/Strata/GameUI/GameUIComponents.cpp:263`, `:290`; `Strata/src/Strata/Reflection/Property.h:32-33`; `StrataEditor/src/UI/PropertyWidgets.cpp:459-488`; `Docs/Manual/Lighting.md:303-304` |
| critic-basics-b-4 | should | order | `new:24` (`basics/math-bases`); `render-image:130`, `render-image:642` (`basics/color`); `render-scene:360` (`basics/signals`); `new:107`, `render-core:459` (`basics/math-probability`); `new:117`, `new:118`, `render-indirect:245` (`basics/math-sphere`) | Five pages quote Strata's shaders, which are written in Slang. No page before them teaches how to read Slang: `gpu/shaders` does, after part `basics` on track E and never on track B. No Assumes row names it, and style.md has a rule for Python fences but none for shader fences. The quotes rest on what differs from C++ and glm: `float3`, `float3x3` whose constructor takes rows (the point of `TangentBasis`), `mul`, swizzles such as `.yx`, `frac`, `select`, `reversebits`. | The first shader quote of each of the five pages is introduced by two or three sentences on what in it differs from C++ and glm, and each shader quote is followed by its explanation line by line, as R31 asks of Python (about 60 words a page). See forPlanner for a rule in style.md §9.1. | `allocation/basics-b.md:212`, `:697`, `:699`, `:779`, `:868`, `:878`, `:957-958`, `:963`; `allocation/gpu.md:189`, `:238`; `style.md:634-636`, `:679`; `tracks.md:208`; `Strata/shaders/Include/IBL.slang:41-48`; `Strata/shaders/Include/Common.slang:25-39`; `Strata/shaders/Include/Scene.slang:362-377` |
