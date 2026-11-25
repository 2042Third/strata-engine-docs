# Brief: `image/grading`

| Field | Value |
| --- | --- |
| Title | White balance, grading and lookup tables |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `image/tone-mapping`, `assets/importing` |
| From | render-image ch. 5; 1.4 (chromaticity, the white locus, CAT02, ASC-CDL, `.cube` lookup tables and the `ColorLookup` asset) |
| Unit | `plan/allocation/image.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `3d-lut` | 3D LUT | color lookup, `.cube` |
| `color-temperature` | Color temperature | kelvin, mired |
| `daylight-locus` | daylight locus | - |
| `half-texel-remap` | Half-texel remap | - |
| `planckian-locus` | Planckian locus | - |
| `slope` | Slope | power (CDL) |
| `tint` | Tint | - |
| `trilinear-interpolation` | Trilinear interpolation | - |
| `white-balance` | White balance | - |
