# Notes: make/assets

## New terms

- license: the author's statement of what you may do with a file; this page is the home (bold in "Where assets come from"); no aliases.

## Requests

- Word list: `Quaternius`, `ambientCG` (written as code now); words "tooltip" avoided.
- Layout: done by the photographer, `layouts/make-assets.ini` (1280 x 720, the Content Browser 797 x 250).
- The tutorial `tutorials/make/scenes-entities.tutorial.json` must exist for `startsFrom`; its placeholder entity is named `Coin`.

## Since

- since 0.3.0: asset import, trash and `.meta` files date from 0.3.0 (inventory gamedev:77, 80, 82).

## Not verified

- The figure content-browser-models: settled by the photographer (see Figures); a running import is not pictured.
- Tutorial command shapes (`entity.find` result `/entities/0/id`, `component.add` of `Tag` with the value `Tag`, `files` copy then registration by the file watcher) were not run.
- The Delete Asset dialog and the Delete Anyway picture are not drawn (no figure).
- The Hierarchy shows the placed model's root and one child named like the file (read from GltfImporter, not seen in the editor).

## Findings not applied

- Brief step 9 says Delete... is refused while the scene uses the model: at the pin the dialog warns and offers **Delete Anyway** (it passes `force`); only the command `asset.delete` refuses. The page says so.
- critic-make-a-20 applied (step 4 and the Result diagram); the edits to make/materials and make/prefabs belong to those pages.
- Brief step 6's "texture usage guessed from names" shown with `_normal`/`_nor`/`_rough`/`_ao` tokens (code: nor, normal, rough, ao).
- Four pictures of the brief: one editor figure and two diagrams only; the refused delete and the import running are not drawn.

## Clerk

- Refused: the term license, a common word (tools/data/common-words.txt) in its everyday sense; the bold sentence may stay.
- Admitted to names.txt: Quaternius, ambientCG.
- Left for the planner: the layout with a large Content Browser, the tutorial's start.

## Figures

- content-browser-models, round 1 (provisional build 5b975ad2831e, not published): the recipe was the ThirdPerson sample's
  root folder in the whole window. Now a basic3d project with the tutorial's stage 1 files; `selection.set` of the model's
  first sub-asset opens `Models/coin-gold` and expands the model (the Content Browser follows the inspected asset), then
  the model is selected. The panel showed the Textures folder, the model, and its mesh, material and texture, with the
  panel's lower half empty.
- Round 2: the layout `layouts/make-assets.ini` (the bottom tabs 250 px high); picture passes. Caption, alt and shows
  rewritten to it: the sub-assets follow the model in the grid (tinted tiles to its right), not below it.
- For the page's words: step 2's "You should see" says the sub-assets sit "below the model"; in the grid view they
  follow it to the right. The texture tile's name is cut ("colormap (C..."): the grid's tiles have a fixed width.
- Round 3 (viewer's faults): two tiles read coin-gold and two colormap, and the caption named none. Caption, alt and
  shows now name the tiles left to right (model, mesh, material, texture) and say the sub-assets follow the model to
  its right in the grid, since step 2's "below the model" is the page's to change. The picture and recipe are
  unchanged: no retake.
- Settled 2026-11-18 (page words): step 2's "You should see" says the sub-assets follow the model to its right on tinted tiles (grid view, `ContentBrowserPanel::DrawGrid`).
- 2026-11-24, pin v0.8.0 (319075e3), published: `waitsFor` removed as `check` asked. `{"stage": 1}` now copies no file
  (stage 1 imports the coin with `asset.import`), so the first take found no `Models/coin-gold/coin-gold.glb`; the
  window steps now create `Models` and import the coin from the pin's ThirdPerson sample, as the stage does. The
  picture matches round 2's: Textures, the selected model with its arrow, then the mesh, the material and the texture
  on tinted tiles. Alt no longer says the material and texture "share one name": the texture tile reads "colormap (C...".

## Tutorial run

- 2026-11-18, pin build, `tools/tutorials.py run`: passed, with exercise 1. Step 1 imports the coin as the page does,
  `asset.import` of `@RELEASE@/Samples/ThirdPerson/Assets/Models/Platformer/coin-gold.glb` (the reader's copy writes
  `<release folder>`, so the page does too), instead of copying it into `Assets/`, which left it unregistered when
  `asset.info` ran; the file follows steps 1 to 9 in order; `entity.find` binds `/entities/0` (it answers IDs).
  Exercise 1 imports `barrel.glb` the same way.
- Step 8: `asset.moveFolder` back to `Models` right after the first move failed in the engine's runner ("Could not
  move 'Props' to 'Models'"): the moved model is imported again (`asset.info` answered `importing: true`) and its
  files are busy. The file waits with `asset.info` until `importing` is false, and the page says so in the step.

## Engine

- `asset.moveFolder` fails with "Could not move" while the folder's assets are being imported again after a move; its
  description says only that it fails when the destination exists. For the planner: wait for imports, or say so.

## Track walk G-final-2 (2026-11-24)

Answers in `plan/walks/G-final-2.md` (WK27 to WK37). Step 2 names the sub-assets as the import names them (texture
`colormap (Color)`); step 3 names the answer's `asset` field; step 4's tab drops `bind` (a command script's key, which
`StrataCLI call` refuses inside parameters) and says what the Inspector shows (prefab bar and Transform; the name in
the header, `PrefabInstance` as the bar: `StrataEditor/src/Panels/InspectorPanel.cpp:428-431`). Steps are named, not
numbered, where the text points at them.
