# Brief: `image/tone-mapping`

| Field | Value |
| --- | --- |
| Title | Tone mapping and the Filmic curve |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `image/exposure` |
| From | render-image ch. 4; 1.3 (tone curves, hue skew, the five classic operators, Filmic's form and its fit, Toe and Shoulder, contrast and saturation) |
| Unit | `plan/allocation/image.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `contrast` | contrast | - |
| `filmic-strata` | Filmic (Strata) | - |
| `hue-skew` | Hue skew | - |
| `ictcp` | ICtCp | - |
| `inset` | Inset | outset (gamut compression) |
| `saturation` | Saturation | - |
| `toe` | Toe | - |
