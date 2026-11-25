# Brief: `image/lens-effects`

| Field | Value |
| --- | --- |
| Title | Lens effects: bloom, vignette, flares and fringes |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `image/tone-mapping`, `basics/signals` |
| From | render-image ch. 7; 1.6 (the bloom pyramid, the Karis average, radius independence, the cos^4 vignette, ghosts, halo and starburst, chromatic aberration) |
| Unit | `plan/allocation/image.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `bloom` | Bloom | - |
| `chromatic-aberration-lateral` | Chromatic aberration (lateral) | - |
| `field-angle` | Field angle | - |
| `firefly` | Firefly | - |
| `karis-average` | Karis average | - |
| `lens-flare` | Lens flare | starburst |
| `soft-knee` | Soft knee | - |
| `tent-filter-image` | Tent filter (image) | - |
| `vignette` | Vignette | cos^4 law |
