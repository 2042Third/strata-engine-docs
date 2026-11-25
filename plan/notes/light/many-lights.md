# Notes: light/many-lights

## New terms

None proposed. The five glossary terms of the brief (clustered shading, froxel, exponential depth slices, light culling, relevance) are defined in bold. The page also defines stride and ordered float in plain text in bold; the planner may admit them as terms (stride: the number of values one cluster owns in the cluster buffer; ordered float: a float whose bits are changed so that unsigned comparison orders the floats).

## Since

0.3.0: clustered assignment and the CPU path date to 0.3.0 (inventory render-direct:90-95); the GPU path is 0.4.0. Not checked against the tags.

## Requests

- Figure `thousand-lights` (kind scene, project template basic3d, Lighting debug view): the setup holds one `entity.create` stub; the planner must expand it to a grid of 1,000 small point lights (40 by 25, spacing 2 m, Range 1.6) and switch the viewport to the lighting view. The component and property names of the stub are guesses.
- Words for extra-words: none (page avoids culls, culled, uncapped, tenfold, overwriting).
- Further reading cites Olsson, Billeter and Assarsson 2012, Sousa and Geoffroy 2016, and Olsson and Assarsson 2011 without links.
- The stage names GPU.Cull, GPU.Opaque and GPU.Setup stand as `Cull`, `Opaque`, `Setup` in code, since the `names` dump lacks them; they are real names at the pin (`Strata/src/Strata/Renderer/GPUProfiler.cpp`).

## Not verified

- That Doom (2016) shipped clustered shading and that Olsson published it in 2012 (general knowledge).
- Which stage times the light passes on each path: taken from the brief; the code shows the `Cull` stage opening before the GPU culling and the light passes following it.
- The default near 0.1 and far 1,000 of the worked numbers are an example, not engine defaults.
- The editor cannot switch the CPU path: the exercise edits `GPUDrivenMode` in the source (no editor setting found at the pin).
- The exercise's timings: no measured values are claimed.
- That the CPU path runs on the main thread (from the architecture rules, not traced).
- Alternatives table rows about other engines and the era of deferred shading.

## Findings not applied

None: the brief lists no open findings. Item `render-direct:822` is applied (no motive for forward shading is named). The erratum `new:33` is applied in the exercise (GPU.Cull on GPU-driven frames, GPU.Setup on the CPU path).

## Clerk

- Admitted the term ordered float, homed here. Refused stride: a common word (tools/data/common-words.txt); its bold may stay.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

## Movable claims

Reviewed at v0.8.0 (319075e3) against `Docs/Releases/0.8.0.md` (the debug views) and `Docs/DeveloperGuide.md`
(Lighting views, Area lights).

- Default grid 16 by 9 by 24, 256 lights per cluster, `MaxLights` 4,096 (stride 257, 3,456 clusters, the worked
  offsets): `Strata/src/Strata/Renderer/SceneRenderer.h:146-151`.
- Limits 64 per axis, 1,024 per cluster, 256 MiB of cluster buffer, with the warning:
  `Strata/src/Strata/Renderer/SceneRenderer.cpp:98-100`, `:345-354`.
- Point, spot and rect lights culled, ranked and capped together; the rect face rides beside the light; the warning's
  text: `Strata/src/Strata/Renderer/SceneRenderer.cpp:2760-2810` (`CollectLights`).
- Whether any rect light exists chooses the forward shader variant: `Strata/src/Strata/Renderer/SceneRenderer.cpp:2745-2750`.
- The forward loop's rect branch (`ST_AREA_LIGHTS`) and the skip of lights behind a surface without a clear coat:
  `Strata/shaders/Scene/Forward.frag.slang:320-394`.
- The Clusters debug view (bands none, 1, 2-3, 4-7, up to a full cluster; statistics as shares of the capacity; the
  name `clusters` of `viewport.setSettings` and `viewport.capture`): `Docs/Releases/0.8.0.md:85`,
  `Docs/DeveloperGuide.md:5076-5080`, `Docs/Manual/Lighting.md:484-486`,
  `StrataEditor/src/Editor/EditorViewportCommands.cpp:148`, `Strata/shaders/Include/Scene.slang:53`.
- The three tests and their numbers (500 lights, 10,000 lights, 4,096 and 5,904 dropped):
  `StrataTests/src/Renderer/GPUSceneLightingTests.cpp:429-609`.
- Prose numbers that link reference/renderer (`MaxLights`, `LightClusterGrid`, `MaxLightsPerCluster`, the stats
  `Lights`, `CulledLights`, `DroppedLights`) rechecked at v0.8.0: unchanged.

## Figures

- `thousand-lights`, published after 3 takes (2026-11-18). Take 1 failed: `entityName` sat inside `parameters`; it is a
  key of the step. Take 2: the grid of 1,000 lights (a `LightRow` of 40, duplicated 24 times, 2 m apart, 0.4 m high,
  Range 1.6) on the ground scaled to 84 by 54 m, Sun and Sky set inactive, Lighting view: the pools merged into a
  checkerboard, so the caption's "pools stay separate" did not show. Take 3: Range 1.2 (pool radius on the floor about
  1.13 m) and a steeper camera (from 0, 20, 32 toward 0, 0, 4, fov 45): round pools that touch only at their rims;
  renderStats: 692 lights in view, 0 dropped, GPU-driven. The caption and alt now say these numbers; the page's worked
  example (radius 1.5 m) is a supposition, not the figure, and stays true.
- `thousand-lights`, retaken at the v0.8.0 pin (319075e3, 2026-11-24) with the recipe unchanged (camera 0, 69.3, 40,
  fov 40, Range 1.2): one take, complete; renderStats lights 1000, droppedLights 0, GPU-driven. `figures.py compare`
  against the published original: 0 differing pixels, and the PNG has the stamp's SHA-256, so `publish` left the file
  and stamp unchanged (an identical original records no `checkedAt`; the stamp still names 822a7a46). Looked at: all
  40 by 25 pools and the grid's four edges in frame, round pools apart with grey gaps; caption and alt hold.
- `thousand-lights`, mended 2026-11-24 after a viewer's report, words only (no retake: the picture is right, the words
  were not). Sampled in the published shot: along a row the brightness between two pools falls only to about 143 to
  165 of 255 (Range 1.2 m at 0.4 m high reaches about 1.13 m out on the floor, so 2 m apart the pools overlap), and the
  dark gaps (about 80) sit only between diagonal neighbours. The caption, alt and shows now say the pools meet their
  row and column neighbours. The grey of bare floor: with the Sky inactive the frame's `AmbientColor` is the default
  (0.03, 0.03, 0.04) nits (`Strata/src/Strata/Renderer/SceneRenderer.cpp`, the loop over `SkyLightComponent`), and the
  Lighting view keeps the post chain (only the value and luminance views replace the image), so the bloom adds a glow:
  the black background rises from about 10 to 50 toward the grid, and the far floor margin (about 28 to 36) is brighter
  than background at the same distance. The caption names both.
