# Brief: `light/local-shadows`

| Field | Value |
| --- | --- |
| Title | Shadows of point and spot lights |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `light/sun-shadows-1`, `light/many-lights`, `light/area-lights` |
| From | render-direct ch. 9; 1.7 (the atlas, quadtree tiles, cube faces, guard bands, view caches, the redraw budget, fades); local shadow casters and culling (`FindLocalShadowCasters`); + the soft shadows of 0.8.0's rectangle lights · W8 |
| Unit | `plan/allocation/light.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `light/local-shadows` — Shadows of point and spot lights

**Covers.** The job: shadows for many point and spot lights from one atlas, without blinking and within a redraw budget.
This page carries the full section on the problem: a cube map per light, dual-paraboloid maps, a shared atlas, caching
static shadows, with a table. The map: the file's overview and constants. The atlas: one D32 texture whose size is the
`LocalShadowAtlasSize` row, with tiles from 128 texels to `LocalShadowMaxTile`; what it costs in memory and what happens
when it does not fit (it halves down to 2048, and that frame draws no local shadows; when no atlas can be made, point
and spot lights cast none). The quadtree allocator: tiles of powers of two in Morton order that merge when freed, the
same requests giving the same tiles. Tile sizes follow the pixels a light's range spans on screen, with a band of 1.25
and 0.4 so they do not toggle, halved in rounds from the least relevant light when the atlas is full; lights whose tiles
do not fit even at 128 texels cast no shadow. A spot light is one view (at most 80 degrees half angle), a point light
six cube faces chosen by the major axis; a guard band keeps every tap inside its face. Views are cached by a key in
world space and by content versions, following the bounds of up to 65,536 casters; the key ignores the camera, so a
light that moved keeps its old shadow until the redraw budget draws its views again; at most 12 views are drawn a frame,
nearest first; a light casts its shadow once all its views hold content, and fades in over 8 frames; ranks fade too.
Sampling: 16 Poisson taps clamped to the tile, turned per pixel by interleaved gradient noise that also turns with the
TAA frame (on main the exception to fixed noise). The data per slot at SRV 13 and the local-shadow vertex shaders. The
casters and the culling of local views (`FindLocalShadowCasters`) come with the draw unit's items, on both paths: on
GPU-driven frames the views are culled in batches of at most `ST_CULL_MAX_LOCAL_VIEWS`, later batches by the mode
`ST_CULL_MODE_LOCAL`, each batch drawn before the next is culled. The rule: keep the lamp's mesh out of its own light's
shadow. The quality rows are named with values from generated tables; the Manual's "at most 16" holds only from Medium
up. "What Strata does not do": soft shadows from a light's size. Then 0.8.0's rectangle lights' soft shadows, written in
phase B. A toy allocator of 40 lines. Figures: the atlas diagram with a view's states (no content, drawn, cached, dirty,
redrawn) and the fade; lanterns under trees (`tp.lantern`) with `CastShadows` off and on and `ShadowFilterRadius` 0
against 8. How it is tested: `Renderer.ShadowAtlas`, `GPU.SceneRenderer.LocalShadows`,
`PerfGPU.Renderer.ShadowRedraw4K*`. The exercises move the sampling rotation to the fixed blue-noise tile and show a
still frame identical with and without TAA, and trace one point light from its tile size to the forward pass's sample.
Afterwards the reader can explain the atlas, its caches and budget, and predict what a moving lamp costs.

**Leaves out.**

- Shadow maps and biases → `light/shadow-basics`
- The sun's cascades and their cache → `light/sun-shadows-1`
- Shadow slots in the forward loop → `light/many-lights`
- Interleaved gradient noise and Poisson disks from zero → `basics/math-probability`
- Lamps and their shadows in a game → `make/lamps`

**Fit.** `fits`: about 6,100 words against L (5,000): about 5,600 at the pin and about 500 for 0.8.0's rectangle-light
soft shadows as the outline gives them; the atlas, its allocator, the view caches and three excerpts take the most.
Phase B must read again: the local-lights stream (more than 16 shadowed lights, tile lifetime, fixed noise for local
lights, the scheduler), the soft shadows of rectangle lights, the numbers 16, 12 and 8 and the turning noise, the
exercise (which wave 8 may have done), and the erratum and the not-done entry.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-direct:136-145` | feature | home | The atlas, the quadtree allocator, tile fitting (lights whose tiles do not fit even at 128 texels cast no shadow), views and cube faces, guard bands, the view cache (its key ignores the camera, so a light that moved keeps its old shadow until the redraw budget draws its views again; `Docs/DeveloperGuide.md:4760-4762`, `:4769-4771`), the redraw budget and fades, sampling, the data per slot, the vertex shaders |
| `new:47` | feature | home | The atlas's memory and its failure path, about 100 words: Ultra's 8192 atlas takes 256 MiB (the values come from the generated quality tables); an atlas that cannot be made halves each way down to 2048, reported once, and that frame draws no local shadows while the tiles are placed again; when no atlas can be made, point and spot lights cast no shadows. Evidence: `Strata/src/Strata/Renderer/SceneRendererLocalShadows.cpp:38-39`, `:793-834` |
| `render-direct:191-193` | feature | home | The rows `LocalShadowAtlasSize`, `LocalShadowMaxTile` and `MaxShadowedLocalLights` (values from generated tables) |
| `render-direct:390` | concept | home | Shadows of local lights: atlases, cube faces, caching; the mistakes |
| `render-direct:461` | code | home | `Strata/shaders/Include/LocalShadows.slang:43-97`: cube face selection, biases in texels at depth, Poisson PCF clamped to a tile |
| `render-direct:462` | code | home | `Strata/src/Strata/Renderer/ShadowAtlasAllocator.h:21-59`: the allocator's contract and `FitTileSizes` |
| `render-direct:509` | figure | home | Diagram: the atlas with a point light's six faces and spot lights, guard bands, a view's states and its fade-in |
| `render-direct:553` | figure | home | Lanterns under trees: `CastShadows` off and on; `ShadowFilterRadius` 0 against 8 |
| `render-direct:614` | rule | home | Keep the lamp mesh out of its own light's shadow |
| `render-direct:662` | hands-on | home | Exercise: the sampling rotation moved to the fixed blue-noise tile, a still frame identical with and without TAA |
| `new:48` | hands-on | home | Exercise (trace it yourself): one point light followed with a search or a debugger from its tile size (`FitTileSizes`) through its slot's data (`BuildLocalShadowData`) and its views drawn (`DrawLocalShadows`) to the forward pass's `SampleLocalShadow`, which reads the slot at SRV 13. Evidence: `Strata/src/Strata/Renderer/SceneRendererLocalShadows.cpp:295`, `:762`, `:869`; `Strata/shaders/Scene/Forward.frag.slang:273`; `Strata/shaders/Include/LocalShadows.slang:22`, `:63` |
| `render-direct:739-741` | term | home | Shadow atlas, tile and guard band; quadtree allocator; cube shadow |
| `new:11` | not-done | home | Soft shadows from the size of point and spot lights. Evidence: `Docs/Roadmap.md:946-947, 1660`; `AGENTS.md:407-408`; `Docs/Releases/0.7.0.md:409-410` |
| `new:12` | erratum | home | `Docs/Manual/Lighting.md:180` says at most 16 point and spot lights in view cast shadows; Low allows 4 (`MaxShadowedLocalLights` 4, 16, 16, 16). Evidence: `Docs/Manual/Lighting.md:180`; `Strata/src/Strata/Renderer/RendererQuality.cpp:43` |
| `new:13` | code | home | `Strata/src/Strata/Renderer/SceneRendererLocalShadows.cpp:23-67`: the overview and the constants (tile sizes, hysteresis, rank margin, spot angle, near planes, the normal bias's reach, caster limits) |
| `render-scene:729` | open | home | The culling of local shadow views (`CullLocalShadowViews`, `RunLocalShadowCulling`), on the CPU and the GPU-driven path |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Shadow maps and biases | `light/shadow-basics` | must |
| Shadow caches and their versions | `light/sun-shadows-1` | must |
| The forward light loop and shadow slots | `light/many-lights` | must |
| Sized lights | `light/area-lights` | must |
| Perspective projections and cube faces | `basics/math-projection` | must |
| Trees | `basics/trees-graphs` | must |
| Noise patterns: Poisson disks, interleaved gradient noise | `basics/math-probability` | must |
| GPU-driven culling | `draw/gpu-driven` | must |
| Bit interleaving (Morton order) | `basics/numbers` | helps |
| The TAA frame index | `image/taa` | helps |
| Quality presets | `image/quality-settings` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `cube-shadow-six-faces` | Cube shadow (six faces) | - |
| `guard-band` | guard band | - |
| `quadtree-allocator` | Quadtree allocator | - |
| `shadow-atlas` | Shadow atlas | - |
| `tile` | tile | - |
