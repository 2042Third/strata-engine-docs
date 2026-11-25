# Notes: make/performance

## New terms

None.

## Requests

- Extra word: "spreadsheet" (the critic's finding asks for a paragraph on CSV files and a free program that opens them; the word has no listed synonym).
- Layout file `layouts/make-performance.ini` for the five editor figures: the Performance panel docked at the bottom, the viewport above it.
- Layout file `layouts/make-performance-scene.ini` for `field-stats`: an 860 × 620 px Scene view over 100 px bottom tabs, so the horizon of the page's camera falls below the Stats overlay; the recipe's fov is 60 so rocks show on both sides of the hut.
- The tutorial asset pack's rock prefab `Prefabs/Rock.stprefab` (CC0, with its credit in the pack's `CREDITS.md`) and the starting checkpoint with the hut of built-in cubes; the tutorial file's first stage copies only `FieldSpawner.cpp` and builds.
- Figure `perf-chart` (kind tool, taken by the owner): a spreadsheet chart of the `WorkMs` column of a perf log.
- Figures of steps inside a section share the section's checkpoint figure; no step has its own picture.
- Stage names `Render.Extract`, `GPU.Shadows`, `Scene.Animation` are real profiler stages (listed in the `editor.perf` command's description at the pin) that the `names` dumps lack.

## Not verified

- The path `Prefabs/Rock.stprefab` and that the rock's mesh renderer sits where the page says (depends on the asset pack).
- That the rock has simpler levels of detail: the page says a mesh with one level shows one tint.
- The settings screen's vsync control of an exported game (Variations): the page says only that vsync produces a capped frame.
- `WorldCellsLoaded` as a perf log column of a game with a world (taken from the inventory, not from code).
- Menu path **View ▸ Performance** (the panel is registered as "Performance" and listed in the View menu by the panel registry; the label was not run).
- The exact counts a run shows (the page states none for the field).

## Findings not applied

- critic-make-b2-16 is applied (a paragraph on the log file as a table and a program that opens it); the one deviation: it is written in the last section.
- W8r: the presets' values are not stated in prose (rule `w8r-preset`), so the quality row's numbers 2, 1, 1, 0.5 are omitted.

## Movable claims

Reviewed at 319075e3 (v0.8.0); paths from the engine's root.

- Stats chip lines (draw calls with opaque and shadow, instances, occluded, triangles, the new `shadowed lights` line of point, spot and rect lights, `visible of N proxies`, `loading`): `StrataEditor/src/Panels/ViewportToolbar.cpp:116-146`.
- The panel's top line `Frame N ms · p95 N · max N · N FPS`: `StrataEditor/src/Panels/PerformancePanel.cpp:255`; Pause or Space and Copy as JSON: `:271-290`, 0.8.0.md line 83; the bound lines CPU-bound, GPU-bound, Capped, unknown: `:306-322`; columns Avg, p50, p95, Max: `:567-569`; 600 frames: `Strata/src/Strata/Core/FrameProfiler.h:169`.
- `editor.perf` keys the page reads (`frame`, `interval`, `gpu`, `boundBy`, `renderStats.occludedProxies`, `.shadowDraws`, `.pendingAssets`) and the stage names (`Scene.Transforms`, `Render.Extract`, `Scene.Animation`, `GPU.Shadows`): `StrataEditor/src/Editor/EditorStateCommands.cpp:236-280`, `:927-975`. `renderStats.shadowFit` is gone (0.8.0.md line 139); the page never named it. Moving objects (interpolation) are in `editor.status`, not on this page.
- Idle redraws 30 and 10 frames per second: `StrataEditor/src/Editor/EditorFrameRate.cpp:88-90`.
- 10,000 materials in at most four draws (was "one opaque draw call", corrected): `StrataTests/src/Renderer/GPURenderSceneTests.cpp:182-205`.
- The rock keeps one level (simplification stops below 36 triangles or when a halving keeps more than three quarters): `Strata/src/Strata/Renderer/Mesh.cpp:694-708`.
- Quality row **Level of detail error (pixels)**: `Strata/src/Strata/Renderer/RendererQuality.cpp:765`; `CastShadows` on by default: `Strata/src/Strata/Renderer/RendererComponents.h:26`.
- Perf log columns `WorkMs`, `IntervalMs`, `GPUBusyMs`: `Strata/src/Strata/Runtime/FramePerfLog.cpp:103-114`; renderer columns, now with `LocalShadowLights` and `LocalShadowViewsDrawn`: `Strata/src/Strata/Runtime/GameRenderer.cpp:181-182`; `WorldCellsLoaded`: `Strata/src/Strata/Runtime/GameRuntime.cpp:367`.
- 100,000 empty `OnUpdate` scripts about 1.9 ms: `StrataTests/Perf/Budgets.json:40` (measured 1.856 ms).

## Since

Performance panel and Stats overlay exist since 0.3.0 (inventory: gamedev:56 "0.3.0").

## Clerk

- Admitted to extra-words.txt: spreadsheet (G0 has 1).
- Left for the planner: `layouts/make-performance.ini`, the rock prefab and checkpoint, figure `perf-chart`, the stage names the dumps lack (Render.Extract, GPU.Shadows, Scene.Animation).

## Figures

Photographer, 2026-11-18, provisional build (engine 5b975ad2831e): three rounds, nothing published; every editor recipe keeps its `waitsFor`.

- The tutorial's rock (`Prefabs/Rock.stprefab` of the asset pack) does not exist, and a recipe's `files` copy only `book:tutorials/…` (a sample's assets only through a tutorial stage, which is not the photographer's file). The four field recipes therefore open a copy of the Open World sample, replace its scene with a new Basic 3D scene (`scene.new`), save its `rock_largeA` mesh as `Prefabs/Rock.stprefab` (`prefab.create`), and copy `FieldSpawner.cpp` with `{"stage": 1}`. The status bar of `result` names the sample's script module. When the asset pack's rock exists, add it to stage 1 of the tutorial (`Samples/*/Assets/` paths are allowed there) and return the recipes to `project: {template: "basic3d"}` without the three prefab steps.
- Layouts: `layouts/make-performance-960.ini` (960 × 540, `result` and `streaming-view`: Streaming in the right column, Performance in the bottom tabs), `layouts/make-performance.ini` (1280 × 800, the Scene view 797 × 380 for `field-stats` and `lod-view`), `layouts/make-performance-tall.ini` (1280 × 1040, Performance 797 × 760 for `panel-bound`: the line that names what bounds the frame is a row of the stage table's GPU part, below about twenty CPU rows, and no command scrolls the table).
- `result`: round 1 a "Scripts built" toast over the view and the Stats overlay hiding the field; round 2 (wait of 600 frames after the build, a taller Scene view) passed. The overlay still covers the left half of the view at this window size.
- `field-stats`: round 2 passed with a hut of 10 × 3 × 4 m. The overlay counts about 2,000 occluded proxies against about 2,900 visible ones: the visible count does not fall below the occluded one, so the caption names the hidden rocks, not "high" and "low".
- `panel-bound`: passed in round 2. The editor ran at the display's 120 Hz, so the line says Capped; its end is cut by the column's width.
- `lod-view`: the sample's rock has one level (the legend counts every rock at level 0 and none at 1 to 3+), so the picture cannot show farther rows at simpler levels as the page's "You should see" says; the caption says what it shows, which matches the step's "If you do not see it". A rock with simpler levels (the asset pack's, if it has them) is what the page's words need.
- `streaming-view`: round 2 in edit mode drew an empty cell map; round 3 with `play.start` drew the map (loaded cells around the player) but the "Scripts built" toast of the build inside `play.start` covered the view. The recipe now builds first and waits 600 frames (untaken: no fourth round). The tinted entities the page names cannot be shown: the screenshot waits until nothing loads, so nothing is tinted; the caption says that, as the step's "If you do not see it" does.

### Mend after the viewer's report (2026-11-18, provisional build 5b975ad2831e, one round, nothing published)

- `result`, status bar naming OpenWorldScripts and an open Streaming tab: stands (photo-editor.md: no other project's name). A recipe-level `files` entry may not name `Samples/…/Assets/` (the schema allows only `book:tutorials/…`), so a Basic 3D project cannot get the Open World rock; the recipe is now `project: {template: "basic3d"}` with stage 1's files and the built-in sphere as the prefab's mesh, and its caption, alt and shows say that spheres stand in for the rock. The status bar reads `FiguresScripts · 2 classes` (the take's project is named Figures). New layout `layouts/make-performance-result.ini` (960 × 640, Streaming closed, a 540 × 300 Scene view, 260 px bottom tabs): the panel now draws two graphs about 35 px tall and the table's Frame, Untimed, Input and Assets.Update rows. When stage 1 of the tutorial copies the asset pack's rock, put the rock back in the recipe.
- `result`, the panel too short: stands; fixed by that layout.
- `lod-view`, every rock green: stands. The Open World rock (`rock_largeA`, about 80 flat-shaded triangles) has no generated levels: `MeshUtils::GenerateLODs` stops when a halving keeps more than three quarters of the triangles. The recipe now opens a Showcase copy and uses its scanned boulder (`Scans/namaqualand_boulder_02_1k`, mesh `A245B2D06B14B7C3`, about 98,000 triangles, six generated levels). Round 1: the legend counts 4,876 boulders at LOD 3+ (0.98 px) and none at levels 1 and 2 (the 2 at LOD 0 are the ground and the hut): the scan's simplified levels are off by far less than a pixel from 8 m, so not even the near rows draw the full level. No camera in the field changes that (a 3 mm error passes 1 px only within about 1.4 m), so the caption now says every boulder is tinted for its simplest levels. The page's "You should see" (near rows full, far rows simpler) needs a mesh whose levels have coarser errors, such as the asset pack's rock if its levels are generated from a mesh of a few thousand smooth triangles.
- `panel-bound`, the Capped line and Copy as JSON cut: half stands. `layouts/make-performance-tall.ini` now has a 160 px Hierarchy and an 860 px Performance panel, so Copy as JSON shows whole. The Capped line (`Capped: 8.3 ms frames, CPU 0.7 ms, GPU 0.2 ms busy (vsync, a frame-rate cap or idle redraws set the pace)`, about 570 px) sits in the Stage column, which gets 3/7 of the table (`TableSetupColumn("Stage", WidthStretch, 3.0f)` against 1.0 for each of four figure columns). It would need a panel of about 1,400 px, which the 768 px column shrinks to about 55 %: unreadable. The caption, alt and shows now say that the line runs on past the column; the word Capped and its figures show.

### Published at v0.8.0 (2026-11-23, pin 319075e3 Release build, one round)

All five editor figures taken once without `--provisional` and published; none had been published before, so nothing was compared.

- `result`: spheres behind the Stats overlay (3 draw calls, 4,792 instances), Performance panel below with the frame line, both graphs and the first table rows. Passed as written; shows and alt shortened.
- `field-stats`: the hut hides the middle of the field; the overlay reads 1,998 occluded and 2,901 visible of 5,002 proxies. Passed as written.
- `panel-bound`: the GPU part's `Capped: 8.3 ms frames, CPU 0.8 ms, GPU 0.2 ms busy (vsync, a f…` line, cut at the Stage column as the caption says. Passed; shows and alt shortened.
- `lod-view`: the legend counts 4,876 boulders at LOD 3+ (0.98 px), none at 1 and 2, two at 0 (ground and hut). Passed as written; the page's "You should see" (near rows full, far rows simpler) still needs a mesh with coarser levels, as above.
- `streaming-view`: nothing tinted (view legend Loading 0, Failed 0); the map shows 45 loaded cells in orange and 2 loading in yellow at the left edge of the circle, so caption and alt now name the two loading cells. The sample's rocks are orange by their own material, not by a tint.
- Captions, alt and shows were trimmed so the page stays within size M (3,989 prose words after the change).

### Last figure at v0.8.0 (2026-11-24, final pin 319075e3)

- `perf-chart` (kind tool, a spreadsheet program's chart of `WorkMs`) cannot be taken at the pin: no engine program draws a chart, and the take's `runtime` kind runs the game only for a screenshot. Its `waitsFor` stays as the request for a later edition; its stand-in is the drawing `perf-log-chart`.
- `perf-log-chart` (diagram): the first lines of `run.csv` as text (the header's first columns Frame, WorkMs, IntervalMs joined by commas, `FramePerfLog.cpp:103`, `:123-128`), the step "select WorkMs, insert a line chart", and the chart of made-up values (a flat run near 4 ms, three single-row spikes). The caption says the values are made up and that it is a sketch. The page places it where `perf-chart` stood, after checkpoint 5 (pages requires a figure there), so the checkpoint's box introduces it; a sentence before it would push the page past size M.
- Size: the stand-in's caption and alt pushed the page to 4,091 prose words. Cut to 4,000: `perf-chart`'s caption and alt shortened (they stay as the request), and two sentences of the perf log's paragraphs that repeated others ("The file has a row for every frame.", the perf log's lead says it; "Every log also has columns for world streaming and physics.", the Variations item on streaming columns says it).

## Tutorial run

Runner, 2026-11-18, pin 822a7a46 (Release build, `--no-gpu` editor). Round 1 passed as written, but the file was thinner than the page; rounds 2 to 4 strengthened it with the page's own values.

- Stage 1 now does what "What you need" and the steps say: the hut (a built-in cube at 148, 1.5, -14, scaled 10, 3, 4, as the figures' recipes place it; the page now names that cube), `script.build` without diagnostics, `script.get` (Spacing 3), `play.start`, `play.state` until the running scene holds 15,000 entities (5,000 rocks of three entities each: `rock_largeA` > `tmpParent` > `rock_largeA` with the mesh renderer), the Stats chip, and `camera.set` behind the hut before `editor.perf` (the step's command tab now shows that move instead of "move the camera in the editor").
- Stage 2: `editor.perf` asks again until a frame is profiled (a fresh editor answers 0 frames at once, as the step's "If you do not see it" says).
- Stage 3: the presets are checked; the shadow step stops the game (`play.stop`), instantiates the prefab, clears Cast Shadows on the innermost `rock_largeA` (the root has no mesh renderer: the page's editor tab and command tab now say so), applies, deletes the copy and plays; a spawned rock then reads CastShadows false.
- Exercise 1 makes ten materials and gives each to one strip of 500 rocks while playing (`entity.find` by name, component and box), with `editor.perf` before and after.
- Not checkable in the run: every `renderStats` figure (draw calls, occluded, triangles, shadow draws, LOD legend) and the GPU bound, since the run's editor has no GPU (`renderStats` null, `boundBy` unknown). Stage 4 stays in the field project: the page opens a copy of the Open World sample there, which a stage cannot do without making the sample the stage's checkpoint; stage 5 runs the exported game from a terminal, which no editor command does.

## Track walk G, final, segment 10 (2026-11-24)

- Checked with the 0.8.0 package in a headless editor with the GPU (`docs-work/walkfix-G10`, `results-all.json`,
  `results-pf2-ow.json`): `editor.perf` gives `renderStats` and `gameRenderStats` null and `boundBy` unknown; a
  `viewport.capture` with the editor camera reads 0 occluded and 4539 visible proxies from 148, 30, -80 and 1982 and
  3283 behind the hut; its last frame keeps the sun's cascades (`cachedCascades` 5), so `shadowDraws` and
  `shadowCasters` read 0 with Cast Shadows on and off; `entity.find` by the name `rock_largeA` gives two IDs, with the
  component `MeshRenderer` one; on the Open World `world.status` after `camera.set` counts 4 loading and 19 loaded at
  once, 50 loaded three seconds later.
- Page mended (WK6 to WK8): no starting download, Checkpoint 1 named; the hut step reads the capture; unknown bound in
  an editor without a window; the shadows step's still-camera case; `entity.find` with the component; "Watch streaming"
  reads `world.status`. Cuts kept the page at 3,998 words (the animated-characters variation, which the Hard exercise
  repeats, and shorter sentences).
- The capture was not added to the tutorial file: a file with `viewport.capture` is skipped by `tutorials.py run`
  (it needs `--pictures`, which the tool still refuses). The file is unchanged and its stamps are current.
