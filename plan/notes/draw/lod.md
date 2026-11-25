# Notes: draw/lod

## New terms

None proposed. The page defines the glossary's error threshold, LOD error, LOD cross-fade, level of detail and relative error in bold.

## Since

0.3.0: the halving rule, the screen fraction and the LOD debug view (Releases/0.3.0.md:31). The error rule and the cross-fade came in 0.4.0 (Releases/0.4.0.md:47-48).

## Requests

- Name "Nanite" (Unreal Engine's virtual geometry) for tools/data/names.txt; the page uses it in the problem section, the alternatives table and Further reading.
- Figure `lod-view` (compare, two variants low and ultra): the Showcase sample, Scene view layout `layouts/scene-view.ini`; the variants use a `quality` key that the planner must map to the preset; the Showcase props may lack generated levels with errors (see Not verified).
- Figure `lod-fade-dither`: a live capture of one prop mid-cross-fade, zoomed so that both levels' dither shows; no debug view shows it.
- Hosts for Further reading: none linked.

## Not verified

- Which sample (Showcase or OpenWorld) has props with generated levels and errors; the figures name Showcase unchecked.
- That the Low and Ultra presets show the difference in the LOD view that the caption states (no capture was taken).
- The menu path of the debug view list; only the entry text "LOD: level of detail drawn" (ViewportPanel.cpp) was verified.
- That the unit-test statement "cases of GPU.Editor.StreamingView" runs without a graphics card is not claimed; the suite is a GPU suite.

## Findings not applied

- The brief's open item render-scene:727 (which sample has generated levels): not checkable without the sample's import records; left to the figure request.
- The staircase figure (render-scene:411) and the Bayer-mask figure (render-scene:413): the page carries the worked numbers and the 4x4 table as text and a table, and no SVG.

## Clerk

- Admitted to names.txt: Nanite.

## Figures

- `lod-view` (editor, provisional build 5b975ad2831e, keeps `waitsFor`): round 1 took the recipe as written, made
  runnable (an editor figure takes no `quality`: each variant now sets `Renderer.Quality` `Preset` through
  `project.setSettings`; the debug view, statistics and camera moved into `editorWindow.steps`; panel `Viewport` of
  `layouts/scene-view.ini`). The Showcase yard framed from (-10, 4, -10) changed by two entities only between Low and
  Ultra: its props already sit at their last level at both presets. Round 2 frames the scanned boulders at about
  (-56, 1, 8) from (-42, 4, -4), fov 35: at Low the boulders are red (key: 0 at level 1, 4 at level 2, 13 at 3+, 142,990
  triangles), at Ultra blue and yellow (6, 8, 1; 480,338 triangles). Passed. The caption names colors and rows instead
  of numbers (pagecheck asks numbers from `{stats.…}`); a few far boulders sit under the statistics box on both sides.
  Round 3, after a viewer's faults (boulders under the statistics box, one counted at LOD 3+ in Ultra; a cliff cut by
  the top edge, yellow at Low; the caption not pointing at the triangles line): camera from (-42, 10, -2) to
  (-52, -0.5, 11), fov 35, aimed with the scene's positions so the group of `namaqualand_boulder_02_1k` sits right of
  the box and the far `boulder_03` pair and the cliffs leave the frame. Low: every boulder red (key 6, 0, 2, 11;
  126,703 triangles); Ultra: yellow, the nearest blue (8, 2, 9, 0; 429,245 triangles, 3.4 times). Caption now names the
  key at the bottom left and the triangles line of the statistics at the top left; alt follows the counts.
  Published at the pin 319075e3 (v0.8.0), one take without `--provisional`, `waitsFor` removed as `check` asked: the
  same frames and counts as round 3 (Low: key 6, 0, 2, 11, every boulder red, 126,703 triangles; Ultra: 8, 2, 9, 0,
  boulders yellow, the nearest blue, 429,245 triangles, 3.4 times). Caption, alt and the page's paragraph hold.
- `lod-fade-dither` (scene, waits for tier 3): not taken; no command shows a fade halfway. At the final pin v0.8.0
  the tool's `renderer` field can only turn `FadeLevelsOfDetail` off, and a `live` take holds the scene's camera still,
  so no level changes while it records: no take can catch a fade at its middle. The entry keeps `waitsFor` as the
  request for a later edition and names its stand-in `lod-fade-masks`.
- `lod-fade-masks` (diagram, stand-in for `lod-fade-dither`): the masks of steps 1, 8 and 15 on four tiles, filled for
  the new level and open for the old, from the table of `IsLODFadeDrawn` (Scene.slang:178). The page places it in the
  cross-fade section after the dither table, introduced by one sentence; the old placement after the debug view's note
  had no paragraph about the fade and is gone.
