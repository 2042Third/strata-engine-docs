# Notes: make/physics

## New terms

None proposed.

## Since

0.3.0: physics with Jolt was in 0.3.0 (inventory physics: rows of RigidBody and colliders, "0.3.0 (Jolt), box3d since 0.5.0"); project-wide layers 0.6.0.

## Requests

None.

## Not verified

- The ball's name `Ball`, the prefab path `Prefabs/Coin.stprefab`, the `Gameplay/Move` and `Gameplay/Jump` actions and the Coin script's spin and bob follow the briefs of the earlier pages, not the engine.
- The command tab values "Kinematic" and a layer by name in `component.set`, and the Add Component menu path, are not run.
- The tutorial and its figures were never run.

## Findings not applied

- Steps 7 and 8 (the Streaming panel's Physics section, the Sleep Threshold on a pile of balls, `physics.stats`, `RaycastAll`, the overlaps, the gun exercise) belong to the follow-up how-to the brief's Fit names.
- A `Coin` layer is not named: layer step uses `Ball` and `Ghost` only.

## Figures

Taken on the pin's Release build from the Basic 3D template, without scripts (the recipes cannot build the tutorial's `BallControl`, `Coin` or `GhostSwitch`). Every recipe now makes its own materials in the look of [materials](materials.md) (a worn metal ball, a gold coin from `Builtin/Cylinder` rotated 90 degrees about X, scale 0.6, 0.06, 0.6) under a figure's own path (`Materials/Ball-<id>.stmat`), because the figures of a page share one project copy and `material.create` refuses a path that exists (round 1 failed there). Every camera was `"scene"` (6 m away, fov 60, the subject small) and is now placed by hand.

- result: published. The ball (layer 1 `Ball`) falls from 3 m and rests after 120 steps; the coin is a Kinematic trigger at (1.8, 1, 0.5); the wall (4, 1, 0, scale 0.5, 2, 4, pale blue-grey) has a Static Rigid Body on layer 2 `Ghost`, and `project.setCollisionLayers` clears the pair, as step 1 of the ghost wall says. Before, the coin was a grey sphere and the wall a plain collider on layer 0, so the caption's "a wall the ball can pass" was false (exercise 5 of the page says why).
- ball-falls: published. The ball after 120 steps, at rest with its shadow touching it; camera 3.7 m away.
- ball-rolls: published, with a stand-in for the push. Without `BallControl` nothing can push the ball (no velocity property, no impulse command), so the recipe tilts the scene's gravity to (4, -9.81, 0): a steady sideways force, which the caption calls a steady push. After 90 steps the ball is about 3 m to the right of a pale disc that marks its start (the recipe's old `Marker` had no mesh, so the start was invisible). A take with the real script would need a figure kind that builds scripts.
- ball-jumps: published, staged. No impulse can be given without the script, so the ball is placed, not played, at the top of the page's jump (centre at 0.5 + 1.27 = 1.77 m, where its speed is 0, the same state the jump reaches). Round 3 tried a higher camera (2 m): the ball's bottom met the horizon and it read as far away; round 2's camera (1.2 m) is kept. Before, 20 steps of a fall from 3 m: falling, not a jump.
- coins-collected: published 2026-11-18 under R57 (a pair within 1 level in at most 0.5 per cent of the pixels is one picture): retaken alone, its captures differ in 127 pixels (0.006 per cent) by 1 level; the picture shows the caption. Earlier: not published: nondeterministic. Its two captures differed by 1 level in 62 pixels (round 2, page take), 127 (round 3, page take) and again 127 (round 4, taken alone with a fresh editor in `docs-work/photo/make-physics-coins/nondeterministic/make.physics.coins-collected/`, both images and results there), scattered over the whole frame; the five other figures of the same takes were stable. For the planner. The picture itself passes the eye: two gold coins are Kinematic triggers at y = 1; the ball, dropped from 3 m onto the left one, falls through it and rests with the coin cutting into its top: a trigger pushes nothing. Collection (the coin destroyed on entry) needs the `Coin` script and is not shown; the caption says so. Round 2's front camera hid the cut (the coin read as behind the ball); round 3 looks from the left front.
- ghost-wall: published. Ball on `Ball`, wall Static on `Ghost`, the pair cleared; the ball is dropped onto the wall at (4, 3.5, 0) and rests on the ground inside it, half of it bulging out of the wall's face. The page has the ball roll through the wall; a still of a roll cannot show that it passed, the ball inside the wall can. Before, the wall was a plain collider on layer 0 beside a ball: no layer at work.
- 2026-11-23, pin v0.8.0 (319075e3) Release build: all six retaken in one page take with the recipes unchanged (one round). `figures.py compare` against the published originals: 0 of 6 differ (0 differing pixels each), so `publish` left every file and stamp unchanged; the six stamps' `checkedAt` now name 319075e3 by hand, because `publish` records a check only for a retake whose original differs. Looked at again: each picture still shows its caption.

## Clerk

- Nothing asked.

## Tutorial run

- 2026-11-18, pin build: passed (5 stages and exercise 1) in a scratch copy of the book whose `make/editor-tour` and
  `make/assets` were mended (see `make/first-script`'s notes).
- 2026-11-18, pin build, in this book after the chain's links were mended: passed as written (5 stages with the
  reader's copies, and exercise 1), stamped, stage zips written.
- Mended so page and file say the same: stage 1 sets the ball's Y to 3 in the command tab too, and the file checks the
  page's 43 steps (Y 0.5 after 45 steps and after 120); stage 4's command tab adds the Sphere Collider and the Rigid Body
  before `component.set` (the coin has neither, so the old tab failed) and names the coin by its ID; the file now
  builds after the apply, in the page's order; stage 5's step 2 tab creates the wall, and step 3 gets its build and
  `script.add` tabs.
- 2026-11-23, pin v0.8.0 (319075e3) Release build: passed as written (5 stages with the reader's copies, and exercise
  1), restamped, stage zips rewritten; pagecheck passes.
- 2026-11-24, official v0.8.0 package (Strata-0.8.0-windows-x64.zip): passed as written (5 stages with the reader's
  copies, and exercise 1); the pin-build run of 2026-11-23 was still current, so not repeated; `tutorials.py check
  --release` finds nothing; pagecheck passes.
- Not checked: the speeds and bounce heights of stages 2 and 3 (they need held keys: `input.sequence`).
- 2026-11-24, track G walk segment 5 (WK11-WK15): the tabs pass the Ball's ID (`entityName` is the tutorial file's
  own key, which no engine program reads); the editor tab sets the Translation to 0, 3, 0 as the command does; the
  scripts are quoted whole; stage 2 removes and adds `BallControl` again, and checks that a play then logs no warning
  (the earlier runs' reader copies of stages 2 and 3 logged `has no field 'Speed'`, for example
  `docs-work/tutorial-runs/make-physics-1/log/0501-reader-copy-make-physics-stage-2.log`). Passed with the pin build and the 0.8.0 package.

## Engine

- A Script component keeps a stored value of a field that its class no longer has, and warns
  `Script fields: script 'BallControl' has no field 'Speed'; the stored value is ignored` on every play
  (`Strata/src/Strata/Scripting/ScriptSystem.cpp:756-761`). Nothing but removing the script clears it: the Inspector
  draws only the class's fields (`StrataEditor/src/Panels/InspectorPanel.cpp:120-180`), and `script.setField` with
  `null` refuses a field the class lacks (`StrataEditor/src/Editor/EditorScriptCommands.cpp:666`). The page says what
  the reader meets and attaches the script again. For the engine's agents: a way to drop stored values of fields the
  class lost (the Inspector's list of stored overrides, or `script.setField` on them).

