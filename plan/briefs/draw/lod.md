# Brief: `draw/lod`

| Field | Value |
| --- | --- |
| Title | Levels of detail |
| Kind | I |
| Size | M |
| Tracks | E |
| Needs | `draw/batching` |
| From | render-scene; the lod view |
| Unit | `plan/allocation/draw.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `draw/lod` — Levels of detail

**Covers.** The job: draw fewer triangles where a mesh is small on screen, without popping and with the same level on
both paths. The problem section teaches the approaches: discrete levels chosen by distance, by screen size or by
geometric error (the screen-space error metric that HLOD systems and Nanite use), continuous levels; transitions by
popping, by a dithered cross-fade or by geomorphing. Strata's choice: discrete levels generated at import with their
error (the import side is `assets/models-gltf`'s), and older levels without errors chosen by halving. The toy picks a
level from a fraction and a list of errors in 30 lines.

The real code. The halving rule (level n below `LODThreshold / 2^(n-1)`) and the error rule (the coarsest level whose
projected error spans at most `LODErrorPixels`), and why the arithmetic looks strange: doublings, one multiplication and
no logarithm, so that the CPU and the GPU choose the same level for the same fraction; the rules are pure functions,
which tools call to show the drawn level; the GPU's copy of the rule in `Include/LODSelection.slang`, where `precise`
keeps the one multiplication from being fused or reordered, and the test shader that runs it for 10,000 fractions. The
quality rows "Level of detail error (pixels)" and "Smallest drawn size (pixels)", with their four presets from a
generated table. `LODCriteria`, which a renderer exposes so that tools show the drawn level. The cross-fade: when a view
instance's level changes, both levels draw for 16 frames with complementary masks of the 4x4 ordered dither, and the
prepass and the forward pass discard by the same test, so the `EQUAL` depth test holds; the fade's state machine
(continuing, reversing, restarting) and its fade codes in the draw-list entry. The LOD debug view tints entities by the
level drawn and reports error pixels per level. What Strata does not do here: billboards and impostors. How it is
tested: `LODSelectionTests`, the test shader of `GPU.Renderer.LODSelection`, and `GPU.SceneRenderer.LODFade`, whose
cases cross-fade a changed level through complementary masks on both paths, switch at once on a camera cut, and fade
levels that cover the same pixels at the same depth by the same mask in the forward pass. The exercise drives
`UpdateLODFade` through a target that changes at frame 5 and back at frame 9, and a "trace it yourself" finds the CPU's
and the GPU's choice of a level. The page runs on a field of props with generated levels, seen in the LOD view at the
Low and Ultra presets. At the end the reader can compute the level a fraction selects under both rules and explain why a
fade must discard alike in both passes.

**Leaves out.**

- Generating levels and their errors at import → `assets/models-gltf`
- The screen fraction → `draw/bounds-culling`
- Ordered dither as a signal idea → `basics/signals`
- The depth prepass and the `EQUAL` test → `gpu/frame-tour`
- The presets and players' graphics options → `image/quality-settings`
- The GPU's level choice inside `Cull.comp` → `draw/gpu-driven`
- Distant cells of a world, which are not drawn → `worlds/why-streaming`

**Fit.** `fits`: about 3,700 words against M (3,000). Four figures (two of them screenshots that need a live capture),
two two-part excerpts and the GPU's copy of the rule take the most, then two exercises.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-scene:253` | concept | home | Levels of detail: the approaches to choosing and to transitions; Strata's choice and why CPU and GPU must agree |
| `render-scene:99-104` | feature | home | The halving rule, the error rule, cross-fades, `LODCriteria`, the LOD debug view, the agreement test shader |
| `render-core:226` | feature | home | LOD selection as pure functions, the render-core inventory's view of `render-scene:102` and `render-scene:104`; `precise` keeps the shader's multiplication of the error rule unfused (`Strata/shaders/Include/LODSelection.slang:24-39`) |
| `render-scene:183` | feature | home | The quality rows "Level of detail error (pixels)" and "Smallest drawn size (pixels)" |
| `render-scene:359` | code | home | `Strata/src/Strata/Renderer/LODSelection.cpp:19-87`: the halving rule and the error rule, written so CPU and GPU agree |
| `render-scene:360` | code | home | `Strata/src/Strata/Renderer/LODSelection.cpp:99-159`: the fade state machine and `IsLODFadeDrawn`, with the Bayer mask of `Strata/shaders/Include/Scene.slang:155-166` |
| `render-scene:411` | figure | home | LOD selection by error: levels and their relative errors against the screen fraction; the halving staircase |
| `render-scene:413` | figure | home | The cross-fade: the 4x4 Bayer matrix, the masks at steps 1, 8 and 15, the state machine |
| `render-scene:430` | figure | home | The LOD debug view on a prop field, at the Low and Ultra presets |
| `render-scene:433` | figure | home | A cross-fade mid-transition, zoomed so both levels' dither shows (a live capture) |
| `render-scene:541` | hands-on | home | Simulate a fade with `UpdateLODFade` and check the codes against `LODSelectionTests` |
| `new:15` | hands-on | home | Exercise ("trace it yourself"): with a search, find the two places that choose a submesh's level, `SceneRenderer::SelectLOD` (called by `GatherDraws`) and `ChooseLODFor` (called by `Cull.comp` through `ChooseLOD`), and show that each takes the levels' errors where the submesh has them and halves the fraction otherwise; the solution names the files, functions and lines. Evidence: `Strata/src/Strata/Renderer/SceneRenderer.cpp:2018-2021`, `Strata/src/Strata/Renderer/LODSelection.cpp:72-87`, `Strata/shaders/Include/Culling.slang:200-213` |
| `render-scene:600-604` | term | home | Level of detail; geometric error; relative error; error threshold; LOD cross-fade |
| `render-scene:727` | open | home | Which sample has generated levels with errors to show: the writer checks the samples' import records first |
| `new:2` | not-done | home | No billboards or impostors for distant objects. Evidence: `git grep -niE "billboard\|impostor" 822a7a46 -- Strata/src Strata/shaders` finds nothing |
| `render-scene:84` | feature | use | The fade code above the instance bits of a draw-list entry |
| `render-scene:98` | feature | use | The screen fraction the rules take |
| `render-scene:479` | rule | link | Prepass and forward pass agree to the bit, at `gpu/frame-tour` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The screen fraction | `draw/bounds-culling` | must |
| Batches, the draw list and its entries | `draw/batching` | must |
| The depth prepass, the `EQUAL` test and invariant positions | `gpu/frame-tour` | must |
| Ordered dither | `basics/signals` | must |
| Floating point: which operations are exact; logarithms | `basics/numbers` | must |
| A shader that discards a pixel | `gpu/shaders` | must |
| How levels and their errors are generated at import | `assets/models-gltf` | helps |
| The quality rows and their presets | `image/quality-settings` | helps |
| Choosing a debug view in the Scene view | `gpu/debugging` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `error-threshold` | Error threshold | - |
| `level-of-detail` | Level of detail | LOD |
| `lod-cross-fade` | LOD cross-fade | - |
| `lod-error` | LOD error | - |
| `relative-error` | Relative error | - |
