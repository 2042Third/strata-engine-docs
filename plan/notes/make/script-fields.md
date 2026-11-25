# Notes: make/script-fields

## New terms

None.

## Since

0.3.0: script fields and the Script component exist since the first scripting release (inventory gamedev:131, row 0.3.0).

## Requests

None.

## Not verified

- The Hierarchy's Cube preset gives a Box Collider (`StrataEditor/src/Panels/SceneHierarchyPanel.cpp:76-77`); the step adds the RigidBody through Add Component (its list and the dynamic default were not read in the UI; `RigidBody: {}` of a command is dynamic, below).
- That Create Prefab on a plain row, drag from the Content Browser and drag of an entity onto a Hierarchy row behave as the page says (taken from the prefabs page).
- Exercise tutorial: the checks of script.setField results (pointer /script/fields/Interval) and prefab.revert with property Spawner.CratePrefab were not run.
- Figures: both wait for editor screenshots at the pin (taken only with the provisional build; see Figures).
- The Variation "Kind" field with a comment was not built or compiled; the Spawner.cpp of tutorials/make/script-fields was not compiled.

## Findings not applied

- critic-make-b1-3: only one Variation set was written (tuning many through the prefab, plus two small ones); the aiming and turret variations belong to other pages.
- critic-make-b1-4: applied (three messages, multi-selection limit with the prefab way, default reaching entities without a value, X button on a renamed class). The text kept as stored text of an unknown class is stated.

## Clerk

- No term or word asked.

## Figures

Taken with the provisional build (engine 5b975ad2), not published; both keep `waitsFor` until the pin moves.

- fields: round 1 good. The Inspector panel (layouts/make-sound.ini, 1280 x 800, Inspector 380 px) after `Spawner.cpp` is copied, built and added to an empty `Spawner`: Transform, then the Script section with the ten rows from Enabled to Crate Prefab; both references read None. The placeholder layout layouts/script-fields.ini was replaced by the existing one.
- result: round 1 showed the three crates stacked into one white column seen from close by, read as one tall block. Round 2 sets the Scene camera (target 0, 1.2, 0, distance 7, yaw 35, pitch -18) and the `Tilt` field to about 30 degrees, so that the crates land on an edge and lie apart; the caption says Tilt is set. The window (layouts/make-prefabs.ini, 960 x 540) is paused after `play.step` of 480 fixed steps, with the Crate prefab (Rigid Body dynamic, Box Collider), the spawn point at 0, 3, 0 and Max Crates 3. A still picture cannot show crates falling: the caption names the state after play instead. The page's step (no Tilt) gives one stack of three crates.
- Mend after a viewer's report (provisional build, engine 5b975ad2):
  - fields: the earlier take folder held no fields picture (only result had been taken). Retaken unchanged: the Inspector shows the ten rows from Enabled to Crate Prefab with their defaults (Max Crates 5, Interval 2, Label Crates, both references None) and ten equally dim reset buttons, as the caption and alt say.
  - result, stacked crates: round 2's Tilt (about 43 degrees about the X-Z diagonal) left one crate on top of another. `Jitter` cannot spread them: the page's spawner only shows it (the page says so). One hold tried four tilts as trial variants: a corner landing (two crates leaned together), 50 degrees about (2, 0, 1) (three in a row, the middle one tilted against its neighbours), 43 degrees with Offset 0, 3, 0 (a tight cluster), and 60 degrees about (1, 0, 0.3), quaternion [0.479, 0, 0.1437, 0.866] (all three flat on the ground, one behind, two side by side). The recipe keeps the last; the shows now says that none rests on another.
  - result, gizmo over the crates: the Spawner is created at 0, 0, 6, behind and left of the Scene camera, so its move gizmo is out of the frame; the Hierarchy and Inspector still show it selected. With no crate stacked, the camera frustum's line passes behind the crates instead of over one.
  - result, status bar "FiguresScripts · 2 classes": not mended. tools/figures.py (make_project) calls `project.create` with the fixed name `Figures` for every template project, and a recipe has no key for the name; the status bar's module name comes from it. The page's `ScriptFields` needs a `project.name` key in the figure tool (its owner's change, not this page's); until then the whole-window picture shows `FiguresScripts`.
- Pin v0.8.0 (319075e3): `waitsFor` removed as `check` asked; both taken once at the pin's Release build and published (never published before, so nothing to compare).
  - fields: the Inspector with Transform and the Script section, ten rows from Enabled to Crate Prefab with their defaults and ten dim reset buttons, as caption and alt say.
  - result: paused after 480 steps; three crates near the middle of the Scene view, one behind and two side by side, none on another; three Crate rows in the Hierarchy; the Inspector shows Max Crates 3 (its reset button lit) and Interval 2. The status bar still reads `FiguresScripts · 2 classes` (see above).

## Walk G-final-7

- WK12 and WK13: the command tab of the crate step had only `prefab.create`; a walker who made the crate with
  `entity.create` gave it no collider, and its crates hung at y 4. The tab now creates `Crate` with `MeshRenderer`,
  `BoxCollider` and `RigidBody: {}`, makes the prefab, deletes the entity and creates `Spawn Point` at 0, 3, 0, and says
  why the collider matters; the editor tab says that the Cube comes with a Box Collider. Checked with the 0.8.0 package
  (`docs-work/walkfix-G7/run`, `verify.py`): with `MaxCrates` 3 and 600 fixed steps the crates with a Box Collider stood
  at y 0.5, 1.5 and 2.5 under the spawn point, and those without one at y 4, 4 and 4.
- WK14: the private members (L42-L45) are quoted after the update's callouts, so the page shows the whole file.
