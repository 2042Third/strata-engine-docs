# Notes: `basics/color`

## New terms

- **luma**: a weighted sum of the channels of encoded values, as opposed to the luminance of linear ones. Home:
  `basics/color`. Aliases: none. (The brief leaves it to the glossary step; `image/spatial-aa` links it.)
- **linear data**: numbers in a texture that mean something other than color (a direction, a roughness, a mask), stored
  as they are and never decoded. Home: `basics/color`. Aliases: none.
- **subnormal**: a half float below 2^-14, whose step stays 2^-24 so that precision falls. Home: `basics/color`
  (an alias of the glossary entry half-float would do). Aliases: subnormal number, subnormals.
- **XYZ** (CIE XYZ): three numbers X, Y and Z that describe any color the eye sees, Y being the luminance. Home:
  `basics/color`. The page writes it as inline math, `$XYZ$`.

The page defines in bold the entries that the brief lists: color channel, linear color, quantization, banding, gamma
encoding, transfer function, sRGB, sRGB transfer function, high dynamic range, scene-linear, half-float, luminance,
chromaticity, color space, white point, D65, gamut, working color space, and Rec. 709 (by its alias BT.709, see
Requests), also gamma, half precision and HDR as aliases.

## Requests

- `tools/data/extra-words.txt`: "decode", "decoded", "decodes", "decoding" (the page converts stored values to light
  in 28 places; every other phrase is longer and less exact) and "subnormal". Their `word-list` findings are left.
- Glossary entry `luminance-y` ("Luminance (Y)") and `luminance` match the same words before the parenthesis, so the
  page's bold **Luminance** and **Luminance (Y)** both go to `luminance` and `term-defined` reports `luminance-y` as
  never used. The page defines both in bold; merge the entries as aliases or let the matcher use the parenthesis.
- Glossary entry `rec-709`: the term "Rec. 709" is not found in prose (the period ends a sentence, "709" is a number),
  so the page defines it in bold by the alias "BT.709" (**BT.709**, written Rec. 709 in this book) and uses "BT.709"
  where "Rec. 709" would inflate sentence counts. An alias "Rec 709" or a tokenizer rule would let pages write the name.
- Hosts for Further reading (cited without links): `registry.khronos.org` (the glTF 2.0 specification) and
  `webstore.iec.ch` (IEC 61966-2-1).
- Figures: four diagram requests in `src/content/figures/basics/color.json` (the ramp stored linearly and as sRGB, the
  sRGB curve, a half mix of black and white done both ways, the chromaticity diagram with the Rec. 709 triangle and
  D65). None is drawn yet.
- Erratum for the engine (not the book): `Strata/src/Strata/Reflection/Property.h:32-33` calls every `Color3` and
  `Color4` property linear, which the UI colors, `TextComponent::Color` and `CameraComponent::ClearColor` are not
  (display sRGB). The page says so in one sentence.

## Not verified

- That the Inspector's color fields show the stored numbers on a 0 to 1 scale, not bytes: `PropertyWidgets.cpp` has
  no conversion in `DrawColor`, but I did not read `ColorSwatch` and `DrawColorPicker` in full.
- That the point light's and spot light's `Color` are linear: only the directional light's tooltip and the critic's
  finding say so; the shader's use was not read.
- The purpose of the pre-exposure (a power-of-two scale that keeps HDR values inside the half-float range): from the
  inventory (`render-direct:703`); the code names the power of two (`RenderSettings` comment, `SceneRenderer.h`), not
  the purpose.
- That a lit sign is about 1,000 nits and a monitor about 200: from the `EmissiveIntensity` tooltip in `Material.cpp`.
- The Coin Run item: `make/project-coin-run` is not written, so the script lines are `pseudocode`; I checked
  `GetEntity().GetUI().SetColor(glm::vec4)` and `Log::Info` against `StrataScriptCore/Include/StrataScript/UI.h` and
  `Log.h`, not a build. That Coin Run's time bar is a UI element whose color `SetColor` takes is the brief's.
- General knowledge, not engine facts: the eye's response to ratios, the 2.2 power of displays, the Rec. 709 to XYZ
  matrix and the Rec. 2020 primaries (the sketches print results of the primaries; the matrix of
  `basics-color-chromaticity.cpp` is the published one and reproduces the primaries 0.64/0.33, 0.30/0.60, 0.15/0.06).
- That `RGBA16F` is the format of the HDR render target in every configuration: `SceneRenderer.h` sets
  `c_HDRFormat` to RGBA16_FLOAT; I did not read whether a device can fall back.

## Findings not applied

- `critic-basics-b-1`: applied (the table of Strata's color fields, the caution about sRGB numbers in a linear field,
  the common mistake, the import setting **Base Color Factors Are sRGB**, the erratum sentence). The Covers' claim
  that base colors are sRGB data is narrowed to the base color maps (usage `Color`).
- `critic-basics-b-4`: applied (each Slang quote is introduced by what differs from C++ and glm and explained after).
- The brief's Fit splits the page into `basics/color` (ideas 1 to 7) and `basics/color-spaces` (ideas 8 to 10). The
  task gave this page the whole Covers, so ideas 8 to 10 are here in about 1,400 words, and the page is 5,800 words.
  No `basics/color-spaces` page was written.
- The brief's "the eye tells more dark shades apart" and the figure of a 50 % blend are kept as general knowledge;
  the figures are requests only.

## Clerk

- Admitted for this page's words: subnormal is an alias of "subnormal number", homed on `basics/numbers` (asked by both pages; floats are taught there).
- Refused: luma (homed on `image/spatial-aa`), linear data (homed on `assets/textures`): the planner may move them. XYZ: the page writes it as math only, so a term would fail `term-defined`; left out.
- `extra-words.txt`: "decode", "decoding" (the endings rule covers decoded and decodes).
- `external-hosts.txt`: `registry.khronos.org`, `webstore.iec.ch` (front pages fetched).
- Left for the planner: `luminance-y` against `luminance` and the "Rec. 709" tokenizing (matcher changes); the engine erratum.

## Track walk E-final-4

Each sketch of the page compiled with `cl /std:c++20 /EHsc` (Visual Studio 2026, 19.50) and with g++ 15 `-std=c++20`, glm from the 0.8.0 package's `StrataScriptCore/ThirdParty/glm`; both printed the same output (`docs-work/walkfix-E4/cl/`, 2026-11-24). The exact Windows line of the page was run in PowerShell in a Visual Studio developer environment (`cmdtest/`).
