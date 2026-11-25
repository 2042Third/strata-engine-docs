# Notes: editor-ui/scene-view

## New terms

None proposed. The page defines the glossary's own terms in bold: Scene view (viewport), render target (render to texture), picking (entity-ID buffer), gizmo, ImGuizmo, snapping, World, debug view, game camera, canvas mode.

## Since

0.3.0: the Scene view, picking and the gizmo exist from the first editor; evidence not checked per tag.

## Requests

- Word list: "toolbar" (11 uses: the strip above the image and the editor's main toolbar, both UI names).
- Figures, all editor pictures of the Showcase sample, layout `layouts/scene-view.ini` (a Scene view alone), `waitsFor` tier 2: scene-view-layers, scene-view-gizmos (translate, rotate and scale, World against Local, on a tilted crate), scene-view-lod-legend (`viewport.setSettings` with `debugView` `lod` and stats on), scene-view-agent-flash (taken within 0.6 s of an automation command), scene-view-canvas-mode, scene-view-game-ui-chip (chip off and on; the recipe needs a `variants` entry the planner should add). The setup steps of gizmos, agent-flash, canvas mode and the chip are empty: the planner fills them.
- The drop's ghost picture is the one of `editor/placement`; the page links the placement page and adds none.

## Not verified

- Toasts in the view's corner (brief item `editor-ui:514`): no toast code was found in `ViewportPanel.cpp`; the page omits it.
- That the readback is ready "two or three frames" later is taken from `gpu/readback-timing`; the engine code polls and has no fixed count.
- ImGuizmo's snapping of the total offset: confirmed by the test case at `StrataTests/src/Editor/EditorUITests.cpp` and `ComputeSnap` on the cumulative delta in the vendored source.
- Settings names for `viewport.setSettings` (`debugView`, `showStats`) in the figure recipes are from the brief and `EditorViewport.cpp` keys, not run.

## Findings not applied

- The brief had no open findings.
- Brief items taken from the inventory with different lines at the pin (`ViewportPanel.cpp` 149-210, 867-930, 936-994, `EditorViewport.cpp` 415-454): the page quotes by the pin's own lines.
- Gizmo operation, World and Local and the snap toggle live in the editor's main toolbar (`EditorLayer.cpp`), not in the Scene view's chips; the page says so. The shortcuts (Q, W, E, R, F, Home, F8) are left to `editor-ui/game-view` as the brief says, except F8 and canvas-mode keys.
- Tests `GPUCanvasEditTests`, `EditorGameUITests`, `EditorUICommandTests` are named, not described case by case.

## Clerk

- Admitted to extra-words.txt: toolbar.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

## Figures

Photographer, 2026-11-18: two rounds with the provisional build (engine 5b975ad2), panel `Viewport` pictures of the
Showcase; nothing published (`waitsFor` stays until the pin moves).

- scene-view-layers: round 1 framed a wall of the oil tank (camera beside it); round 2 frames Drum12 beside the bus
  with the move gizmo on it, stats on and the `streaming` debug view so that a legend (Loading 0, Failed 0) stands at
  the bottom left over a normally lit image. Good.
- scene-view-gizmos: one picture, not the six the old caption described: a `::figure` shows one state, and six views
  need a `::compare` or more figures (page words). Drum12 tilted (Rotation 0, 30, 25), move gizmo in Local space; the
  green arrow leans along the drum's axis. Round 1 put the camera on the bus's roof. Good.
- scene-view-lod-legend: good. Page problem: the legend counts entities, not area. In the picture the ground (one
  entity, LOD 0, 69) covers most of the image while LOD 3+ counts 96, so "if the picture is mostly one color, that
  color's number is the largest" (the paragraph before the figure) is not true of it.
- scene-view-agent-flash: cannot. `take` runs the editor with `--no-automation` and the steps as a `--commands`
  script; the journal sets the latest automation activity (chip and flash) only for commands of the source
  `Automation`, so the window shows "Automation off" and neither chip nor outlines. The recipe is left as it was. The
  page needs a picture taken while an automation client drives the editor (a tool figure the owner takes, or a
  `take` that can connect a client), or a drawing of the strip with the chip and the outlines.
- scene-view-canvas-mode: the PhotoMode canvas's PhotoPanel made active, ExposureSlider selected, `canvasMode` on.
  Round 1 in `layouts/scene-view.ini` showed no bars (its image is 16:9, as the canvas); round 2 uses
  `layouts/scene-view-canvas.ini` (a copy of `layouts/hud.ini`, 1280 x 800, Scene view 797 x 600): bars above and
  below, handles on the slider, thin outlines on the others. Good.
- scene-view-game-ui-chip: one picture, chip on, not off and on (a `::compare` needs page words): the photo panel over
  the yard beside the bus. The Showcase has no world-space canvas, so the old caption's claim about world canvases
  cannot be shown with it. Good.

Photographer, 2026-11-18, round 3 (a viewer's faults; provisional build, engine 5b975ad2; nothing published):

- scene-view-lod-legend: the fault stands in the page's words, not the picture. The paragraph before the figure says
  "if the picture is mostly one color, that color's number is the largest"; the counts are entities, not area, and in
  the picture the ground (one entity) makes it mostly green (LOD 0: 69) while LOD 3+ counts 96. Retaken: same counts.
  The caption now says the counts are entities, not area. The paragraph needs rewording (planner): the legend counts
  entities, so one large entity can color most of the image while many small ones hold the largest count.
- scene-view-gizmos: the arrows are about 30 px long in the 797 x 499 picture, and ImGuizmo draws its handles at a
  fixed share of the view, so neither a closer camera nor another window size makes them larger. Added the crop
  `gizmo` (drum and gizmo, x 250-480, y 170-400, scale 3): enlarged, the green arrow leans with the drum's axis (both
  about 16 degrees from upright). The page shows a crop only when its directive names it: the page needs
  `::figure{id=scene-view-gizmos crop=gizmo}`, in place of or after the whole figure.
- scene-view-canvas-mode: the slider's handles are about 4 px squares. Added the crop `slider` (the photo panel's
  upper part, x 595-795, y 140-220, scale 3): enlarged, the exposure slider's orange outline and its eight square
  handles read clearly, with the time slider above for comparison. The page needs
  `::figure{id=scene-view-canvas-mode crop=slider}` after the whole figure. No command zooms canvas mode (the wheel
  only), so the whole picture cannot show the handles larger.

Photographer, 2026-11-23, at the pin v0.8.0 (319075e3), one take without `--provisional`, recipes unchanged:

- Published, each judged by eye: scene-view-layers (Drum12 with the move gizmo, stats box at the top left, streaming
  legend Loading 0, Failed 0 at the bottom left), scene-view-gizmos and its crop `gizmo` (the green arrow leans with
  the tilted drum), scene-view-lod-legend (ground green, the tank red; LOD 0: 69, LOD 3+: 96, as the caption says),
  scene-view-canvas-mode and its crop `slider` (bars above and below, the exposure slider's outline with square
  handles), scene-view-game-ui-chip (Game UI chip lit, the photo panel over the yard at the right). None had been
  published at 822a7a46, so there was nothing to compare.
- scene-view-agent-flash: still blocked, not taken. `take` still runs the editor with `--no-automation` and the steps
  as a `--commands` script, so no command has the source `Automation` and neither the agent chip nor the outlines
  appear. Nearest honest picture: a tool figure taken while a StrataCLI client drives the editor, or a drawing of the
  strip with the chip "Agent: entity.create · 3 s ago" and accent rectangles around the changed entities.

## Pin move to v0.8.0

- Debug view legends: the page now says what the legend shows beyond the LOD view (`DrawDebugViewLegend` at 319075e3): counts for `mip` and `culled` (Too small, Occluded), bands without counts for `luminance` and `clusters`, shares for `albedo`, and a note line only for `wireframe` (triangles), `voxels` (levels, sizes), `probes` (probes, dead ones) and the light views (`specular`, `diffuse`, `gi` and others: sun to sky ratio). The list of views stays on `gpu/debugging`.
- Figures: the six `waitsFor` "tier 2: editor screenshot" entries are removed, since the pin has `editor.screenshot`; the pictures are not yet taken.

Photographer, 2026-11-23, a viewer's faults at the pin v0.8.0 (319075e3):

- scene-view-layers: the statistics box (to x 395 of 797) covered the drum's upper left quarter. `camera.set`'s target
  moved 0.8 m to the camera's left (9.85, 0.6, -0.8 to 9.32, 0.6, -1.4); retaken under the lock: Drum12 and its gizmo
  now stand at x 437 to 525, clear right of the box, the bus behind, the red barrel at the right edge. Published.
- scene-view-canvas-mode: the lit Grid, Outline and Gizmos chips and the dark Game UI chip seemed to contradict the
  paragraph. They are the stored settings: `ViewportPanel.cpp` overrides them only in the frame's render settings
  (`ShowGameUI || canvasMode`, `EditorOverlays && !canvasMode`), never in `ViewportSettings`. The caption now says so;
  the picture is unchanged.

Photographer, 2026-11-24, at the pin v0.8.0 (319075e3), with the tool's new `automation` field:

- scene-view-agent-flash: taken and published. The recipe now runs with `automation: {client: "claude-code"}`, so
  StrataCLI mcp sends every step as an agent: it finds Drum0 to Drum4 (the cluster at about -2.4, 0.1, 19.8), sets the
  camera at (2.6, 2.4, 24.6) toward the cluster, waits 300 frames, and ends with one `component.set` of Transform
  Rotation (0, 0, 0) on all five, the edit the flash outlines. One round, judged by eye: the chip at the strip's right
  end reads "Agent: component.set · now", and an accent rectangle stands around each of the five drums (white, red,
  blue) beside the oil tank. Caption, alt and shows rewritten to the picture, without the command's name (captions
  carry no engine names). The page's words already match it; nothing else changed.
