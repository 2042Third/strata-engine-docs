# Notes: animation/editor

## New terms

None proposed. The page defines the three terms the glossary homes here (edit pose, pose preview, render transform) in bold.

## Requests

- Layout `layouts/animation-editor.ini` for the two editor figures (Scene view large, Inspector and Hierarchy visible). Settled: see ## Figures.
- Figure `edit-poses`: the robot in rest and in clip-start pose, side by side (two captures with `viewport.setSettings`); the manifest holds one recipe with the rest setting, the second variant is the planner's. Settled in one picture: see ## Figures.
- Figure `preview-chip`: needs `$Robot` resolved to the robot's entity id by the recipe runner. Settled: the recipe holds the ID.
- The bind-pose picture (screenshot 2) is a Mermaid diagram; a GPU test capture is not taken.

## Not verified

- Simulate mode draws the bind pose for skinned meshes: read from `AnimationRegistration.cpp`, `Scene.cpp` and `EditorContext.cpp`, not run (brief item new:33).
- An animator whose skeleton has not loaded draws the bind pose until the first pose arrives: inferred from `GetPose` having no pose, not run.
- The direction of the `Armature` quarter turn in the worked example (Z into Y) is illustrative; the page does not state the sign.
- Command lines were written from the schemas; none was run.

## Findings not applied

None: the brief lists no open finding beyond the Simulate check (new:33), applied above as a section (the screenshot after the photographer's capture is not made here).

## Since

0.3.0: the preview and the animation commands (inventory animation:164, 185-188); rest poses came in 0.4.0.

## Figures

Taken 2026-11-18 with the provisional build (engine 5b975ad2831e), three rounds; nothing published, `waitsFor` kept.

- Requests above, settled: no `layouts/animation-editor.ini`. `edit-poses` uses `layouts/scene-view.ini` (the Viewport panel, 797 × 499); `preview-chip` uses the new `layouts/animation-editor-wide.ini` (1440 × 810, Viewport 1318 × 589, Hierarchy and Inspector columns narrowed to about 60 px). `$Robot` is the robot's ID `A94EC4E371BEB484`, read from `Scenes/Course.stscene`.
- `edit-poses`, good. The page names `::figure{id=edit-poses}` with no variant, so the two poses cannot be two variants (check refuses a variant figure the page does not name), and `editPose` is one setting for the whole view. The recipe shows both in one picture: it copies the robot 1.4 m aside, keeps `editPose` at `"rest"` for the original, and poses the copy with `animation.preview` and no state at time 0, which is its clip-start pose by the command's definition. Round 1 showed that the sample's own default state, Idle, begins within 9 degrees of the rest pose (as do Dance, Wave and Sitting): the two robots looked alike. Round 2 compared Jump, Wave and Dance. Round 3 gives the copy no controller and the clip Standing (`9EBF72F09E01CD81`, derived from the model handle), whose first frame is a crouch: the right robot stands visibly lower, knees bent. Caption and alt now say "two copies" and "begins crouched". The narrow Viewport draws the preview chip as its bone icon at the toolbar's end, without a label. When the pin moves, a figure with two variants (page `::compare` or `variant=`) could show the edit pose itself; that is the page writer's choice.
- `edit-poses`, mended 2026-11-18 (provisional build): a viewer saw the grid's blue axis line cross the left robot's leg and white gizmo lines in the sky, neither taught by the page. The `viewport.setSettings` step now also sets `grid` and `sceneGizmos` to false; the retake shows only the two robots on the green ground under the sky, the toolbar's Grid and Gizmos chips off. Caption and alt unchanged: still true.
- `preview-chip`, failed after round 3. The chip shows its label only when the whole chip strip fits, so the 797 px Viewport drew it as an icon (round 1); the wide layout shows it, readable: "Previewing 'Run' at 0.30 s · Robot", and the crop `chip` enlarges it 2 ×. The robot was cut by a close camera (round 2), then hidden behind a wooden sign seen from the side at (3.5, 1.3, 0) (round 3). The recipe now looks from (-1.2, 1.3, -0.8), the side round 3's `edit-poses` showed clear of the sign; this camera is not taken yet. The alt follows the chip's real text (state, time and the entity's name).

Taken again 2026-11-23 at the pin v0.8.0 (319075e3), without `--provisional`; both published, `waitsFor` removed as `check` asked.

- `edit-poses`, round 1 at the pin: as at the provisional build. The left robot stands at rest, arms hanging; the right copy stands lower, knees bent, head below the left one's; grid and gizmos off. Published. The alt's "arms closer to its body" was dropped: the arms differ too little to see.
- `preview-chip`, three rounds at the pin. Round 1 (camera from (-1.2, 1.3, -0.8)): the robot clear and the chip readable, but the grid's blue axis crossed its leg, the game camera's white frustum lines crossed the sky, and from the front the Run pose at 0.30 s reads as standing. Round 2 adds `grid` and `sceneGizmos` false and looks from the robot's -X side at 3.3 m: too close, the head cut. Round 3 from (-5.2, 1.3, 2.2) at (0, 1.0, 3.0): the robot whole, seen from its side mid-stride, one leg and arm forward; the chip reads "Previewing 'Run' at 0.30 s · Robot", and the 2 × crop holds it alone. Published; the alt now says "seen from its side".

## Clerk

- Nothing to admit.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.
