# Notes: gpu/debug-drawing

## New terms

- None proposed. The page defines the four terms the glossary homes on it (overlay, gizmo, overlay pass, screen view) in bold.

## Requests

- None. Every word passed the word-list check. Further reading cites the Unity manual, the Unreal Engine documentation and "Game Programming Patterns" without links.

## Since

- 0.3.0: `DebugDraw` and `DrawSceneGizmos` are listed since 0.3.0 in inventory render-core:221 and render-core:222; the overlay set in render-core:220.

## Not verified

- The two figures overlays-off and overlays-on: the `viewport.setSettings` keys (`grid`, `selectionOutline`, `sceneGizmos`) and the `BoxCollider` property name `HalfExtents` in `entity.create` come from the pin's code, but the recipes were not run.
- The patch `tutorials/gpu/debug-drawing/exercise-3.patch` was built against the pin plus the hunks of `tutorials/world/tutorial-component.patch` for `PhysicsComponents.cpp` and `WindZoneTests.cpp` (it applies to those); it was not compiled and the new test was not run.
- The Alternatives table and Further reading: what Unity and Unreal offer for debug drawing is general knowledge, not checked against their documents.
- That the editor's streaming, LOD and mip views are the debug views that fill `EntityTints` (read from `ViewportRenderer.cpp` comments and the inventory, not run).
- That no test covers `SceneOverlayRegistry` itself: a search of `StrataTests/src` found no file that names it.

## Findings not applied

- The brief lists no open findings.
- `new:19` to `new:22`, `new:49` and `new:50` are not in `plan/inventory/` at this checkout (no file `new.md`); the page took their facts from the code named in the brief's Items (`DebugDraw.h`, `SceneRenderer.cpp` `RenderOverlays`, `SceneOverlay.h`, `SceneGizmos.cpp`, `PhysicsComponents.cpp`). The line ranges the brief names had moved; the page quotes by symbol.
- `new:22` (no debug drawing from scripts): `git grep -niE -e debugdraw -e drawline` in `StrataScriptCore` at the pin finds nothing; the page says so.
- The brief says the exercise gizmo is drawn "in the one gizmo group the pin has, `Collider`": applied; the page also says that a component gizmo is drawn with the colliders.
- `capstone/build` adding the arrow of a Directional zone: not on this page, by the brief.

## Clerk

- Nothing asked.

## Figures

- entity-tints, round 1 (published). The recipe asked for the streaming view, but at the pin that view tints only entities
  whose mesh, material or textures are still loading (Sulfur) or failed (Cinnabar) (`StreamingView::BuildStreaming`): a
  loaded built-in cube is not tinted, so the picture would have shown no tint. The recipe now uses the LOD view
  (`StreamingView::BuildLOD` tints every drawn entity by its level, level 0 green at alpha 0.55) and a camera of its own
  (2.6, 1.9, 3.6 toward the cube, fov 35) instead of the scene camera. Seen: cube and ground green, the cube's two lit
  faces and its shadow still lighter and darker, the sky untinted; the result reports 2 tinted entities, both at level 0,
  nothing pending. Caption, alt and shows rewritten to say so; the paragraph ("the editor uses this for its streaming,
  LOD and mip views") stays true.
- overlays-off, overlays-on (editor; settled with the provisional build, two rounds, not published: they keep
  `waitsFor: tier 2: editor screenshot` until the pin moves). The window figures became pictures of the `Viewport`
  panel (the Scene view at 797 x 499 in `layouts/scene-view.ini`, which now exists), so the toolbar and lines read at
  the column's width. Both recipes now select the crate, set the editor camera (2.4, 2.5, 3.3 toward 0, 0.4, 0, fov 40),
  turn the transform gizmo and the stats off and differ only in `grid`, `selectionOutline` and `sceneGizmos`.
  - Round 1: the scene gizmos draw colliders only of the selection (`allColliders` is off by default), so the crate is
    now selected; its collider, of the cube's own size, lay under the orange outline and showed only on two edges.
  - Round 2: the collider's half extents are 0.6 (a box a little larger than the cube) and the camera is closer. Seen:
    off, the white cube on the gray floor with Grid, Outline and Gizmos off in the toolbar and no line; on, the grid's
    thin lines with a red and a blue axis line, the orange outline and the green box, the red line hidden inside the
    cube. Captions, alts and shows rewritten to say so: the old caption named a light marker the picture does not
    show (the sun's gizmo is not in the frame) and did not name the outline.
  - Round 3, after a viewer's report (provisional build, not published). Two faults of overlays-on stood. A short
    light gray line at the top left was an edge of the template's Main Camera frustum (SceneGizmos draws every
    camera's frustum, up to 10 m, in `CameraColor` 0.85 gray; from (0, 2, 6) its far left edge falls at the frame's
    left, its lower part hidden by the floor); and the collider box (center 0.5, half height 0.6) reached 0.1 below
    the floor, which hid its bottom edges. Both recipes now delete Main Camera (`entity.find`, `entity.delete`; the
    Scene view draws through the editor camera) and give the box half extents (0.6, 0.55, 0.6) and offset (0, 0.06,
    0), so it spans y 0.01 to 1.11. Seen: no line at the top left; the box's front bottom edges run along the floor
    and close it; off unchanged. Caption, alt and shows stay true.
- Pin v0.8.0 (319075e3), one take of all three in one hold. overlays-off and overlays-on: `check` named the
  `waitsFor` lines as met, so they are gone; taken without `--provisional` and published. Seen: off, the white cube
  on the gray floor with Grid, Outline and Gizmos off and no line; on, thin grid lines (checked enlarged), the red
  and blue axis lines, the orange outline, the green box a little larger than the cube, the red line hidden inside
  the cube. entity-tints: `compare` with the published file found 0 differing pixels (the original is byte-identical,
  so `publish` kept the file and its stamp); the result again reports 2 entities tinted at level 0, nothing pending.
  Its caption and shows called the untinted ground "dark gray"; the Scene view shows it mid gray, so they now say
  "gray".
- overlays-on, after a viewer's report that the grid is hard to find at page size. Enlarged, the published picture's
  grid lines are a few levels lighter than the floor near the cube and read best on the far floor and the lighter band
  at the top. The grid's color and opacity are the editor's own (`viewport.setSettings` has no key for them), so a
  lower camera would crowd the lines but not lighten them, and both overlay figures share one camera. No retake: the
  caption, alt and shows now call the grid faint gray squares on the floor, clearest on the far floor near the top;
  the picture is unchanged.

## Tutorial run

- 2026-11-24, pin 319075e3: `tutorials.py patch gpu/debug-drawing`. The tutorial file changes no engine code and is
  `tutorials.py run`'s (skipped here). `exercise-3.patch` passes as written on top of
  `world/tutorial-component.patch`: it applies, builds, `Architecture.Layering` and the feature test pass; stamped.
- The run tested only `Architecture.Layering`: an exercise patch takes its suites from its page's `patch.tests`, and
  this page has no patch, so the exercise's own test (`Physics.WindZone`, one more case) is not in the stamp. Run by
  hand on the same patch build: `StrataTests.exe --test-suite=Physics.WindZone`, 3 cases, 205 assertions, all passed.
  For the tool's owner: an exercise patch should also run its chain's suites (here `world/tutorial-component`'s).
