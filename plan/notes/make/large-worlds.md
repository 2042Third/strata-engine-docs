# Notes: make/large-worlds

## New terms

None proposed. The page defines `prefetch-make` (its glossary home) in bold; world, cell, layer, persistent scene and streaming source are defined in plain words (bold) where the page first needs them.

## Since

0.4.0: `Docs/Releases/0.4.0.md:29` lists "Worlds streamed in cells" as new in that release.

## Requests

- Figure layout file `layouts/large-worlds.ini` for the eight editor figures (the file does not exist yet). All eight use the OpenWorld sample as the project with an empty step list; the integrator should give each its own steps. If a capture shows the fox, its caption must name the fox's authors and license (see the sample's `CREDITS.md`); the captions as written do not mention it.
- The tutorial starts from the `basic3d` template because the book's start checkpoint (player prefab `Prefabs/Ball.stprefab`, props `Pine`, `Rock`, `Stump`, loading scene, `Teleport` script with its action) is a download that does not exist yet and `tutorials/make/levels-saves` was not written when this page was. The checkpoint's files (the prefabs, the `Gameplay/Teleport` action) must be added to stage 1 or to a start tutorial by the integrator. Stage 2 onward names `Prefabs/Pine.stprefab` and `Prefabs/Ball.stprefab`. `tutorials/make/large-worlds/Teleport.cpp` is the page's script; no stage copies it into a project yet.
- Editor steps have no per-step whole-editor picture, only the section's "You should now have" picture.

## Not verified

- The menu path **View ▸ Streaming** (the panel is registered as "Streaming"; the menu grouping was not read).
- The Content Browser's **New ▸ World** label and that the new asset can be renamed to `Meadow` at once (`world.create` takes a path; the UI names it "World").
- **Add Component** and **Script** as the Inspector's labels for adding a component and attaching a script class.
- That `entity.delete` takes `entities` (a list), that `world.loadCells` takes `cells: [{layer, x, z}]`, `prefab.instantiate` instance shape as in `make/prefabs`.
- That the Inspector shows "Persistent scene" for the ball (the line exists in `InspectorPanel.cpp:483`).
- The 814 m and 860 m distances are computed by hand from the layout (nearest corner (576, 576) of cell (9, 9) and the marker at (608, 608)).
- That a ball teleported to a tile whose cell has not loaded falls without end: run 2026-11-24 and false in this world (the ball, the streaming source, lands at 608, 0.5, 608; the page says so now). That a fuller cell, a mesh collider still building or a player that is no source makes it fall is derived from the design, not run.
- The 4 mm spacing at 50 km is arithmetic on 32-bit floats; that a plain scene at 50 km draws without shaking is the brief's statement, not run.
- Mesh colliders pending after `IsLoadedAround` (critic new:9) and `PrefabSync` catching up cells only when they load (new:8): read in the code, not run; the page says so.
- The Hierarchy's search `cell:1,-1` form (from `plan/inventory/worlds-runtime.md`: `cell:<x>,<z>`).
- That the exported game starts in the world: the page now sets `Worlds/Meadow` as the start scene (stage 7 runs `project.setStartScene`); the export itself and the game were not run. A loading scene is optional.

## Findings not applied

- critic-make-b2-2 concerns `make/commands`; this page's end checkpoint is the one it names for `world.setLayers` (tutorial stage 7 is the end state).
- Applied: critic-make-b2-4 (step 3 of "Make the world" deletes the template's `Main Camera` and `Ground`, with the reason), critic-make-b2-14 (the ball's `RigidBody::Teleport` with both velocities set to zero, after the sample's excerpts), new:8, new:9 as above.
- The brief's items on `Load Before Start` changes and `world.setLayers` are left to `make/commands`, as its Leaves out says.
- The Hierarchy world strip is described without the map button's tooltip; the viewport's chip colors (yellow, ochre, gray in the engine's manual) are not named, only "colored by state".

## Figures

Editor figures settled 2026-11-18 with the provisional build (engine 5b975ad2831e, `--provisional`); nothing published,
every recipe keeps `waitsFor`. Layout `layouts/make-large-worlds.ini` (960 × 540; Inspector column 300 px, the
Streaming panel docked as a tab of that column so its map is tall, the Scene view 330 px high). The recipes' layout
`layouts/large-worlds.ini` is also named by `worlds/why-streaming` at 1280 × 720, so this page has its own file.

- The project is the Open World sample (its Kenney Nature Kit prefabs stand in for the checkpoint's props: `PineDefault`
  and `RockLargeA`, renamed `Pine` and `Rock`; no stump exists, so there are two props). The steps rebuild the page's
  tutorial in order: `world.create Worlds/Meadow`, delete `Main Camera` and `Ground`, four tiles on Terrain, props on
  Props, Cells chip, save, pin Terrain (0, 0), save, the ball (sphere, dynamic body, sphere collider, Streaming
  Source) in the persistent scene, cook, the far island, the `Teleport` script (copied from
  `tutorials/make/large-worlds/Teleport.cpp`) with a `Gameplay/Teleport` action. The ball is a plain sphere with no
  follow camera, since the checkpoint's `Ball` prefab does not exist.
- result, cells-filled, cell-map, player-source, teleport-done: whole window. world-created, cooked: the Asset panel.
- teleport-done really teleports: the take presses the action in a paused game and runs 300 steps; the ball reads
  608, 0.5, 608 and the map shows the far cell loaded.
- exported: cannot be taken. The picture is the exported game's window, which an editor screenshot cannot show
  (`runtime` figures are not taken yet). The recipe is left with no steps. The page needs a runtime figure of the
  exported game, or, nearest now, the editor's Export dialog (`editor.showDialog {dialog: "export"}`) with a caption
  that says so.

Found while taking (the page's words are not changed here):

- "Make the world" step 1 and the tutorial's stage 1 bind `/entities/0/id` of `entity.find`; the answer is
  `{"entities": ["<id>"]}`, so the binding fails and nothing is deleted: bind `/entities/0`.
- "See the cells stream" step 3 pins Terrain (0, 0) before step 4 saves: `world.loadCells` then fails with "The world
  has no cell Terrain (0, 0)" because unsaved cells are not yet the world's. The recipe saves first; the page's order
  (and stage 3) needs a save before the pin.
- "Cook the world": the line the build writes is "Cooked: 6 cells measured, at most 7 bodies within any source's
  reach, a physics capacity of 9 recommended", not the page's "Cooked N cells (M read again): at most B bodies in
  reach, a capacity of C recommended". Check at the pin's new release.
- The strip above the Hierarchy counts "0 cells loaded" until the first save, although four tiles exist.

Mended 2026-11-18 after a viewer's faults (provisional build 5b975ad2831e, the five figures retaken in one hold):

- teleport-done: the move gizmo hid the ball and the rock was a speck. The selection is cleared after the steps and
  the camera stands at 605, 3, 615 looking at 608, 0.5, 604 (fov 40): the ball fills about 60 px, the rock behind it
  shows.
- player-source: the gizmo hid the ball. The selection is cleared and the camera stands at 3, 2, 4 (fov 40); shows and
  alt no longer say "selected".
- cell-map: the map shows five squares for six loaded cells, since the Props cell (0, -1) lies on the Terrain cell
  (0, -1). Alt and shows say five squares; the picture is unchanged.
- cooked: the picture shows the stored line under the table ("Cooked: 6 cells measured, at most 7 bodies within any
  source's reach, a physics capacity of 9 recommended", AssetInspectorPanel.cpp:719). The page's step quotes the
  outcome line that only a click on **Cook** adds below it (AssetInspectorPanel.cpp:302, "Cooked N cells (M read
  again): ..."); no command clicks the button, so the picture cannot show that line. The caption now names the stored
  line. The page's "You should see" needs the stored line, or both lines.
- cells-filled: the Hierarchy column (200 px) dropped the strip's "· N unsaved". The figure uses its own layout
  `layouts/make-large-worlds-wide.ini` (Hierarchy 280 px, Scene 376 px); the strip reads "0 cells loaded · 6 unsaved",
  and caption and alt say so.

Taken 2026-11-23 at the pin v0.8.0 (319075e3), Release build, one hold, one round; `check` named the seven
`waitsFor "tier 2: editor screenshot"` lines as met, and they are removed:

- Published, each as its caption and alt say: result (four tiles with orange cell outlines, the map with five orange
  squares, one pinned, in the camera's blue circle), world-created (four layers, 64 m, 256 m, Terrain Loaded), cells-filled
  ("0 cells loaded · 6 unsaved", Edit layer Props, "Cell: Terrain (0, 0)"), cell-map, player-source (the source's dot at
  the circle's center, the ball on the ground), cooked (the stored line reads "Cooked: 6 cells measured, at most 7
  bodies within any source's reach, a physics capacity of 9 recommended", as at the provisional build), teleport-done
  (the ball on the far tile, the rock behind it, the map with one square, 2 cells loaded). No recipe changed.
- exported: still not taken. Its `waitsFor` now reads "tier 3: the exported game's window; ...": the picture is the
  exported game's window, which no editor screenshot shows, and `runtime` figures are not taken yet. Nearest honest
  picture now: the Export dialog (`editor.showDialog {dialog: "export"}`) with a caption that says so; the page's
  "The exported game shows its loading scene" needs a runtime figure.
- exported, taken 2026-11-24 at v0.8.0 as a `runtime` figure (one hold, one round) and published: the setup rebuilds the
  tutorial's world up to the cook (world, Main Camera and Ground deleted, four tiles, Pine and Rock, the ball with its
  Streaming Source), adds a primary `Camera` at -5, 4, 10 in the persistent scene (the tutorial's world has none once
  Main Camera is gone, and the checkpoint's follow camera does not exist), cooks, saves, and sets
  `Worlds/Meadow.stscene` as the start scene. The game ran 4 s at 1280 × 720, High, and exited 0; its log shows the four
  Terrain sub-scenes loaded before "Started 'OpenWorld'", the Props cells after. The picture: the ball at rest with its
  shadow on the tiles, the pine behind, the ground's far edge. Caption and alt say that this export has no loading scene
  and that a fixed camera stands in for one that follows the ball; the page's words are unchanged. The loading scene
  of `make/levels-saves` is still not shown by any picture.
- Still true at v0.8.0 (page words unchanged here): the cooked line differs from the page's quoted "Cooked N cells (M
  read again): ..." (that line follows only a click on **Cook**); the strip counts "0 cells loaded" until the first save.

## Tutorial run

- 2026-11-18, pin build, `tools/tutorials.py run`, three rounds: the tutorial (7 stages) and exercise 1 pass.
- The start checkpoint the page offered was no download and no tutorial made it (`make/levels-saves` has none). Stage 1
  now makes the four parts "What you need" names, and the page tells how: a `Ball` prefab (sphere, Rigid Body, Sphere
  Collider), `Pine`, `Rock` and `Stump` prefabs from the release's `Samples/OpenWorld/Assets/Models/Nature/`
  (`tree_pineDefaultA.glb`, `rock_largeA.glb`, `stump_round.glb`, imported with `asset.import`), `Teleport.cpp` and the
  Button action `Gameplay/Teleport` with no binding. The loading scene of `make/levels-saves` is not made.
- A copy of a stage opens the project's start scene, not the world: stages 2 to 7 and the exercise start with
  `scene.open Worlds/Meadow.stscene`, and the page says so before "Fill the cells".
- Thin parts made whole: four tiles (the tab says so), the three props and the Rock moved from x 60 to 70, the
  status before and after the first save, the Streaming Source's defaults (Radius 0, Layers empty, Priority 0), a
  paused play with the ball's source (7 cells loaded), the cook (7 cells, `maxBodiesInRadius` 5,
  `recommendedMaxBodies` 7, no warnings), the island (tile, rock, marker; the tab lists all six commands), the build and
  `script.add Teleport`, a save, play and `input.action Gameplay/Teleport`: after 300 steps the ball rests at 608,
  0.5, 608. The page's step 4 now saves before Play.
- "Fill the cells" step 3's command tab said `world.status` lists four Terrain cells with one entity each; before the
  first save it counts 4 dirty cells, 0 loaded, and lists none. The tab says that now.
- Exercise 1: `LayerToggle` on the ball; P drops the playing count from 7 to 4 cells, P again wants 7, and the Props
  cells load over some frames (`until` on `/playing/loaded`). The answer says they load again over some frames.
- 2026-11-23, pin v0.8.0 (319075e3), Release pin build, one round: the tutorial (7 stages) and exercise 1 pass as
  written.
- Not run: step 5 of "Teleport without falling" (the prefetch taken out) and the export of stage 7 (no loading scene
  in the run's project); stage 7 only saves.

## Engine

- `world.status {cells: true}` lists no cell while four new cells are pinned and dirty, though its description lists
  "the cells that are not plain unloaded ones".
- `world.status` and `world.loadCells` give `entities: 0` for loaded cells that hold a tile made and saved in the same
  session: the count is what the streamer created (`WorldStreamer.h:60`), which the descriptions do not say.

## Clerk

- No term or word asked.
- Left for the planner: `layouts/large-worlds.ini` and the figures' steps, the start checkpoint's files.
- Page fix for the build's checkpoint rule: "Why a level streams" moved before "## What you need"; "Turn a layer off from a script" and "What a world cannot do" became ### sections of the step sections before them, before their checkpoints.

## Track walk G, final, segment 10 (2026-11-24)

- Checked with the 0.8.0 package (`docs-work/walkfix-G10`, `results-all.json`): no command gives an entity's cell
  (`entity.get` with `world` has none); after the save `world.status {cells: true}` lists Terrain (0, 0), (-1, -1),
  (0, -1), (-1, 0) and Props (0, -1), (-1, 0), (1, -1), each with `entities` 0, and after `scene.open` 1 and 3; the
  start scene of the end checkpoint was `Scenes/Main`; the Radius exercise: 0 and 100 want 7, 50 wants 6 and keeps 7
  loaded, 1000 loads 9; without the prefetch the ball lands at 608, 0.5, 608.
- Page and file mended (WK1 to WK5): "What you need" names Checkpoint 1 and no loading scene; the cells are read from
  `world.status` in the command tabs; `entities` explained, stage 3 checks it after opening the scene again; `script.get`
  for `ReachRadius`; step 5 of the teleport runs (stage 6, `TeleportNoPrefetch.cpp`) and says the ball lands; the export
  sets the start scene first (stage 7); the Basic exercise uses a Radius of 1000. Passed with the pin build and with
  the 0.8.0 package (`docs-work/walkfix-G10/runs`).
