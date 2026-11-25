# Brief: `image/spatial-aa`

| Field | Value |
| --- | --- |
| Title | Anti-aliasing in one frame: FXAA and morphological AA |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `image/encoding` |
| From | render-image ch. 8; 1.8 (FXAA's algorithm, Strata's morphological AA and its area table) |
| Unit | `plan/allocation/image.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `image/spatial-aa` — Anti-aliasing in one frame: FXAA and morphological AA

**Covers.** The job: remove jagged edges from one finished frame, without history, working on display values. The page
starts with the aliasing figure `render-image:506`: the Physics Playground's tiled floor in crops enlarged four times,
with anti-aliasing off, FXAA, the morphological AA and TAA Sharp. The full section "The problem and how engines solve
it": pixels as point samples; geometric, shading and temporal aliasing; supersampling and MSAA and what they cost;
anti-aliasing as a post pass (MLAA, SMAA, FXAA). Strata has neither supersampling nor MSAA, and the renderer refuses a
target that is not single-sampled (`new:6`). One sentence names Strata's first design decision, never below native
resolution (no render scale below 1, no dynamic resolution, no temporal upscaling), and links its home
`image/quality-settings`: a frame is drawn at native size with one sample per pixel, and these passes and TAA are its
anti-aliasing. Strata's choice: `PostProcessComponent::AntiAliasing` with
`AntiAliasingMethod` (FXAA by default, TAA, Morphological). The toy is an edge detector on luma and a blend across the
edge, in about 40 lines.

FXAA (diagram `render-image:462`, code #19): luma of display-encoded values, the local contrast test, the edge's
orientation from second differences, a 12-step walk along the edge, the subpixel blend, whose factor 0.7.0 lowered from
0.75 to 0.25 to keep the texture's detail (`render-image:508`, a diagram until tier 2 has the switch). Strata's
morphological AA (diagram `render-image:463`), in three passes: the edges (`new:7`: luma differences kept by local
contrast adaptation, and depth jumps), the weights (code #20: a run search, the crossings at its ends, the area table
that `Tools/GenerateAreaTable.py` integrates exactly; Z, L and U shapes, and a U blends nothing), and the blend in
linear light. It shares no table with the published SMAA. The pass that runs last also dithers and adds the grain, as
`image/encoding` taught (`RenderPostDisplay` chooses between the two methods). How it is tested: the FXAA case of
`GPU.SceneRenderer.PostProcess`, `GPU.SceneRenderer.Morphological`. Exercises: the anti-aliasing shoot-out, still and in
a slow pan; the morphological AA traced to its passes and its fallback (`new:21`); FXAA's subpixel factor changed and
measured with the look-dev harness's crops. At the end the reader can choose a spatial AA for a scene and say what each
method cannot fix.

**Leaves out.**

- Temporal anti-aliasing → `image/taa`
- Specular aliasing of highlights and its filter in the shader → `light/brdf`
- Sampling and the Nyquist limit from zero → `basics/signals`
- Choosing the anti-aliasing in a game → `make/quality`
- Committed generators as a workflow of the build → `engineering/generated-code`
- The look-dev harness that makes the crops → `engineering/look-dev`

**Fit.** `fits`: about 4,550 words against L (5,000). The two algorithms, FXAA and the three passes of the
morphological AA, take the most words with three excerpts, four figures and three exercises; the sampling theory is
linked, not taught again.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-image:362`, `render-image:364` | concept | home | Sampling and aliasing in rendering (geometric, shading, temporal; supersampling, MSAA, post AA; AA is not blur); spatial post AA (FXAA, MLAA and SMAA, depth-aware edges; FXAA expects encoded luma) |
| `render-image:194-198` | feature | home | `AntiAliasing` and `AntiAliasingMethod` {FXAA, TAA, Morphological}; FXAA after FXAA 3.11 with `c_Subpixel` 0.25; Strata's morphological AA, its resources (`SceneRendererPost.cpp:862-919`) and passes (1303-1320) |
| `render-image:281` | feature | home | `Tools/GenerateAreaTable.py` → `MorphologicalAreaTable.inl`, 132x132 RG8 |
| `render-image:413` | code | home | `Strata/shaders/PostProcess/FXAA.frag.slang:51-169`: the local contrast test, the edge's orientation, the walk along the edge, the subpixel blend |
| `render-image:414` | code | home | `Strata/shaders/PostProcess/MorphologicalWeights.frag.slang:17-78`: the run search, the crossings' classification and the area-table lookup |
| `new:7` | code | home | `Strata/shaders/PostProcess/MorphologicalEdges.frag.slang:44-81`: the edges pass: luma differences kept only against half the largest neighboring difference, and depth jumps beyond the neighbors' steps |
| `render-image:462`, `render-image:463` | figure | home | Diagrams: FXAA's steps; the morphological AA's edge map, a run with its two crossings, the Z, L and U shapes, the area table's layout |
| `render-image:506` | figure | home | Off, FXAA, morphological and TAA Sharp in crops (the off and on) |
| `render-image:508` | figure | home | FXAA's subpixel 0.25 against 0.75, drawn as a diagram: tier 2 has no switch for `c_Subpixel` (`Strata/shaders/PostProcess/FXAA.frag.slang:37`), so the figure carries `waitsFor` the one request that extends tier 2 (pipelines.md §11; R34, D42) |
| `render-image:597` | hands-on | home | Exercise: the anti-aliasing shoot-out on the Physics Playground's floor, still and in a slow pan |
| `render-image:621` | hands-on | home | Exercise: rebuild with FXAA's subpixel at 0.75 and 0.25 and measure the detail with the look-dev crops |
| `new:21` | hands-on | home | Exercise (trace it yourself): follow `AntiAliasingMethod` Morphological from `RenderPostDisplay`'s choice through `EnsureMorphologicalResources` to the three passes and the statistic that reports them, and find the line where a failure to make the resources draws FXAA instead. Evidence: `Strata/src/Strata/Renderer/SceneRendererPost.cpp:862-919, 1276-1283, 1303-1320` |
| `render-image:643` | term | home | Luma (FXAA's weights of encoded values) |
| `render-image:692-697` | term | home | Supersampling and MSAA; FXAA; MLAA, SMAA and morphological AA; area table; Z, L and U shapes; subpixel blend |
| `new:6` | not-done | home | MSAA and supersampling (a render scale above 1): neither exists, and the renderer refuses a target with more than one sample. Evidence: `Strata/src/Strata/Renderer/SceneRenderer.cpp:2767` (`info.sampleCount != 1` refused); `Docs/Roadmap.md:944, 1670, 1672`; `Docs/Releases/0.7.0.md:409, 411`, run again at the pin |
| `render-image:412` | code | use | The choice between FXAA and the morphological AA in `RenderPostDisplay` |
| `render-image:286` | feature | use | The look-dev harness's `--aa` and its crops, for the figure and the exercise; its home is `engineering/look-dev` |
| `render-image:691` | term | link | Aliasing; its home is `basics/signals` |
| `new:11` | not-done | link | The first design decision, never below native resolution, named in one sentence (`book.md`, "Strata's design decisions"); its home is `image/quality-settings` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Sampling, aliasing and filtering; the Nyquist limit | `basics/signals` | must |
| Display encoding, the 10-bit intermediate, the last pass's dither | `image/encoding` | must |
| How a GPU draws a frame: rasterization takes pixels as samples | `gpu/how-a-gpu-frame-works` | must |
| Strata's depth conventions: reversed Z | `gpu/coordinates` | must |
| Color: luminance and luma | `basics/color` | must |
| Tone mapping: the display pass | `image/tone-mapping` | helps |
| Specular anti-aliasing | `light/brdf` | helps |
| Committed generators | `engineering/generated-code` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `area-table` | Area table | - |
| `fxaa` | FXAA | - |
| `luma` | Luma | - |
| `mlaa` | MLAA | SMAA, morphological AA |
| `msaa` | MSAA | - |
| `subpixel-blend` | Subpixel blend | - |
| `supersampling-ssaa` | Supersampling (SSAA) | - |
