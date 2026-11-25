# Notes: make/prefabs

## New terms

None: the badge and the prefab bar are described in plain words, not defined.

## Requests

- Figures: six figures, all not yet taken; the editor ones need `layouts/make-prefabs.ini`. They start from basic3d with a cube standing in for the coin, because a figure project cannot start from the tutorial's end state; the integrator may swap in the real coin.
- The tutorial file starts from `make/materials` (a tutorial that does not exist yet); positions of coins and the entity-find boxes assume the ground is free at (-2, 0) and (2, 0); the integrator's first run may need the boxes moved.
- Tutorial commands assume `entity.find` returns `/entities/0` and the tag `Coin` stays on the prefab's root.

## Findings not applied

- critic-make-a-2: applied (step 4 changes the mesh child's Scale, not emission).
- critic-make-a-20: applied (steps 3 and 4 select the mesh child; the page states the root holds only position and name).

## Not verified

- Name of the mesh child of a placed model (the page says "the child that holds the mesh").
- That the Hierarchy badge shows on every row of an instance, or the root only.
- That the Scene view toolbar's Snap button carries the label "Snap" (taken from the engine's manual).
- The Hierarchy rename gesture; the Content Browser's folder drag target for Create Prefab (from the manual).

## Tutorial run

- 2026-11-18, pin Release build: the tutorial and exercise 1 pass (two rounds; the first passed as written but did less than the page). Mended: the file now places the coins as the page does (`asset.place` by a ray straight down at (-2, 0), a snapped `asset.place` at (2, 0), the page's two `prefab.instantiate` instances at (3, 1, 0) and (-3, 1, 0)), finds each coin's mesh child by name and `entity.get` children instead of world boxes, moves and renames the root of `Coin (1)` (step 3), checks the overrides' component and property, the scale every coin takes after the apply, and saves. The page's stage 2 tabs use a ray instead of a Scene view pixel (deterministic), step 2 cancels its drag with Escape (otherwise the level held six coins, not five), step 3 got its command tab, and the rename in stage 3 names `Coin (1)` back.
- 2026-11-23, pin v0.8.0 (319075e3) Release build: the tutorial (5 stages, chain from make/materials) and exercise 1 pass as written in one round; nothing mended. `pagecheck` fails only in figures: the five editor figures' `waitsFor "tier 2: editor screenshot"` is stale (the pin has `editor.screenshot`), left for the figure runner.
- 2026-11-24, final runs at the v0.8.0 pin (319075e3): the tutorial (5 stages) and exercise 1 pass as written with the pin's Release build and with the official v0.8.0 package (`Strata-0.8.0-windows-x64.zip`); nothing mended; `tutorials.py check --release` finds nothing.

## Since

- Prefabs: 0.3.0 (inventory gamedev:96, `prefab.create` and `prefab.instantiate` in editor-core:174-175); the drop ghost came in wave 8.

## Clerk

- No term or word asked.
- Left for the planner: the six figures and their layout, the tutorial's start and positions.
- The build's checkpoint rule: the note after checkpoint 4 moved before it, and "What a prefab does not do here" and "Outdated instances" became ### sections of the last step section, before its checkpoint.

## Figures

- result (scene): published after two rounds. Round 1 failed: `entity.create` takes no `tag` parameter, so the tag was dropped (the picture does not need it). The recipe now makes `Materials/Gold.stmat` and `Materials/Silver.stmat`, a standing coin from `Builtin/Cylinder` (rotated 90 degrees about X, scale 0.7, 0.07, 0.7, centre at y = 0.35 so it rests on the ground), creates the prefab and four instances at the page's positions, and gives the first instance (-2, 0) the silver material as an override. The camera at (1.6, 2.4, 5.6) aims at the centre, fov 34. Before, the recipe had a grey cube floating 0.25 m above the ground, no gold or silver material and camera "scene". Alt and shows now name the silver coin at the left.
- made, placed, overridden, applied, finished (editor): settled in three rounds with the provisional build (`--provisional`, nothing published; `waitsFor` kept). The figure project cannot start from the Materials page's end state, so every recipe builds a stand-in coin with the page's structure: a root `Coin` (Transform only: Translation (0, 0.6, 0), Rotation 90 about X, Scale 0.7, 0.07, 0.7) with a child `Visual` (the name of the ThirdPerson sample's coin child) holding the Mesh Renderer (`Builtin/Cylinder`, `Materials/Gold.stmat`), then `prefab.create`. The root carries the disc's shape, so the child's Scale of 1.5 in each field makes a coin 1.5 times larger, as the page says. Each recipe then does the page's steps up to its figure: `placed` the four instances at the tutorial's places; `overridden` the silver material on the child of `Coin (1)` (found by box, as the tutorial does) and selects it; `applied` the child of `Coin (2)` scaled to 1.5 and `prefab.apply`; `finished` `prefab.revert` of the material, `prefab.unpack` of `Coin (4)`, `edit.undo`, `scene.save`, with `Coin (4)` selected. All are the whole window at 960 × 540 with `layouts/make-prefabs.ini` (copied from `make-scenes-entities.ini`; Inspector 340 px wide, Scene view 436 px) and the editor camera at (0.4, 2.5, 5.3) toward (0, 0.45, 0), fov 46.
  - Round 1: the 300 px Inspector cut the chip to "Overrides (", and the coins were small. Round 2: Inspector 400 px and a taller Content Browser; the chip read whole, but the Scene view's toolbar wrapped and the Content Browser showed only its `Materials` folder, never `Prefabs` (its folders cannot be shown by command). Round 3: Inspector 340 px, the Content Browser back to its short strip and out of the `made` caption, the camera closer.
  - What commands cannot show: the badge's hover tip (step 2 of the first section), the drag with its ghost and label, the magnet's snapping, the `Overrides` menu and the right-click menus (Revert, Unpack Prefab). The pictures show the state before or after each; the page's words describe the menus.
  - The old `finished` caption said the unpacked coin stays a plain entity after the undo; the page says the undo makes it an instance again, and the picture shows that.
  - overridden, mended after a viewer's report (provisional build, two rounds): from (0.4, 2.5, 5.3) the silver coin was about 50 px wide, the same grey-beige as the default ground, and the move handles covered its middle: it read as an orange ring. Round 1 moved the camera close to `Coin (1)`: the disc filled the left of the view but still matched the ground, because its metal reflects the sky's ground color. Round 2 gives the figure the darker ground of `result` (`material.set` of `Materials/Ground.stmat`, BaseColor 0.06, 0.055, 0.05) and the camera at (-1.0, 1.3, 2.6) toward (-1.0, 0.6, 0), fov 44: the silver coin is a pale disc about 100 px wide around the small handles, with two gold coins at the right. The alt names that. `applied` keeps the default ground (its silver coin reads without it).
- At the v0.8.0 pin (319075e3), one take of all six in one hold, recipes unchanged: `result` came out pixel for pixel like the picture published at 822a7a46 (`figures.py compare`: 0 differing pixels), so `publish` left it and its stamp records the new pin in `checkedAt`. The five editor figures were published without `--provisional`, their `waitsFor` lines removed as `check` asked. Each shows its caption: `made` the Coin row's badge and the bar with `Overrides (0)` (the gold coin is small under its handles, but the subject is the two panels); `placed` five rows with blue badges and five gold coins in a cross; `overridden` the yellow badge of `Coin (1)`, `Overrides (1)` and the bold Material label with its orange bar; `applied` Scale 1.5, `Overrides (0)`, larger coins with the silver one at the left; `finished` `Coin (4)` selected with its bar back and every badge blue.

## Track walk G, final, segment 3 (2026-11-24)

- WK6 of `plan/walks/G-final-3.md`: the command tabs now run `prefab.status` wherever a "You should see" names the
  badge or the `Overrides` chip, as the tutorial file already did, and say what its `linked` and `overrides` read; the
  first tab says where the IDs come from (`entity.find`, `entity.get` for a child). The steps without a tab (move and
  rename the root, undo the unpack, save) got one with the file's commands. The tutorial file did not change.
