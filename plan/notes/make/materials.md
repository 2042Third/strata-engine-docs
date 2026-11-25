# Notes: make/materials

## New terms

None. The page defines the glossary terms material and PBR only; "texture" and "normal map" are explained in a sentence (homed outside the closure).

## Requests

- Editor layout file `layouts/materials.ini` for the figures `material-editor` and `normal-warning` (Asset tab and Inspector open, Content Browser visible).
- Figure `normal-warning` is marked `waitsFor: tier 2: editor screenshot`; it needs the ball's material with a normal map imported as Color, which the recipe's steps do not create (no texture import in figure steps).
- Figures with the ball use a plain grey metal material, not the textured one, because figure recipes cannot import textures.
- The stages after `make/assets`: the tutorial assumes the root `Coin` with a child `coin-gold` holding the mesh, and an entity `Ball` with a Mesh Renderer (from `make/scenes-entities`).
- Word list: none requested; hosts: none (Further reading entries carry no link).

## Since

0.3.0: material documents, the material editor and the commands exist since 0.3.0 (inventory gamedev 1.6, "0.3.0; clear coat and glass 0.6.0").

## Not verified

- Typical reflectance numbers of gold, copper, iron and silver and the 0.04 / 0.85 real-world reflectance remarks come from public tables, not from the engine.
- Ctrl+click on a slider to type a value (standard Dear ImGui behavior, not checked in the editor's widget code).
- That 50 nits is invisible in the template's sunlight (derived from the sun's 120,000 lux in the skill, not measured).
- Names of the Basic 3D template's Cube preset (`+ ▸ Cube`) and the Ball entity's name come from the briefs of earlier pages.
- That the Albedo legend text and the red stripes appear as the manual says (manual and code agree; not run).
- Tutorial commands were never run.

## Findings not applied

- critic-make-a-20: applied (step 3 selects the child `coin-gold`).
- critic-make-a-21: applied (the ball's section sets `Metallic` and `Roughness` to 1 and explains the multiplication).
- Brief item: "drop of the material on the coin" is in step 3; clear coat, Unlit and Double Sided are one sentence each; "New ▸ Material" is the Content Browser's toolbar button (the right-click menu item reads New Material).

## Clerk

- No term or word asked.
- Left for the planner: the layout file, figure `normal-warning`, the figures' materials, the stages after `make/assets`.

## Figures

Retaken 2026-11-23 at the pin v0.8.0 (319075e3, Release build), all ten figures in one hold of the lock, recipes
unchanged except for the two `waitsFor` lines `check` asked to remove:

- `result`, `sphere-grid`, `gold-coin`, `ball-metal`, `coin-glow`, `albedo-view`, `final`: `figures.py compare`
  against the published originals: 0 of 7 differ (0 pixels). Published again (files unchanged, stamps moved to the pin).
- `material-editor`: published (first time): the Asset tab with Gold at its first values (white Base Color, Metallic 0,
  Roughness 0.5), the other rows and the texture slots at None, as caption, alt and shows say. The window's lower edge
  cuts the next row (Clearcoat) below Emissive Map; the rows the caption names are whole.
- `normal-warning`: published (first time): below Normal Map the warning "Metal032_NormalGL is imported as Color: its
  normals will be wrong" and the whole button Import as Normal Map, then Occlusion Map and Emissive Map.
- `ball-normal`: still blocked, not published: the v0.8.0 take shows a smooth grey ball with a soft highlight and no
  bumps, like `ball-metal`, because `Metal032_NormalGL.jpg` is flat (see below). Nearest honest picture and the words
  the page needs: as below.

Photographed 2026-11-18 at the pin (Release build, basic3d template). The ball's recipes now import the pin's
`Samples/PhysicsPlayground/Assets/Textures/Metal/Metal032_*.jpg` (setup `asset.import`, absolute paths into the pin
clone) and build `Ball.stmat` as the page does (maps, `Metallic` and `Roughness` 1, `UVTiling` 2); each figure keeps
its materials and textures under its own folder (`Materials/<id>/`, `Textures/<id>/`), because the figures of a take
share one project copy and `material.create` refuses a path that exists. The coin stands on the ground (y 0.4).

- `result`: published (round 3). Round 1: coin upright and floating (bottom 0.2 m above the ground), matte ochre face.
  Round 2: face turned to the half vector of the sun (elevation 40, azimuth 20) and the camera: the whole face blown
  white. Round 3: face 16 degrees off that vector, fov 30: a pale gold face, lighter at the top, and the grey ball.
- `sphere-grid`: published 2026-11-18 under R57 (a pair within 1 level in at most 0.5 per cent of the pixels is one
  picture): retaken alone, its captures differ in 4,210 pixels (0.203 per cent) by 1 level; the picture shows the
  caption. Earlier: not published, nondeterministic. Round 1 put the gold row behind the red row, half hidden. Round 2
  stacks the rows (red row floating at y 1.75, gold row on the ground), camera in front, fov 27: the picture shows what
  the caption says. Every take's two captures differ by 1 level in 4,374 bytes, the same count four times, also taken
  alone: `docs-work/photo/make-materials-grid/nondeterministic/make.materials.sphere-grid/`. For the planner.
- `gold-coin`: published 2026-11-18 under R57: retaken alone, its captures differ in 93 pixels (0.004 per cent) by 1
  level; a warm gold face lighter toward the top, its long shadow on the left. Earlier: not published, nondeterministic.
  Round 1 failed (material path taken), round 2 face blown white, round 3
  pale cream, round 4 (face 26 degrees off the half vector) a warm gold face, lighter toward the top. No round shows a
  "sharp highlight": a flat face reflects the sun on all of it or on none of it. Round 4's two captures differ by 1
  level in 94 bytes, twice, also alone: `docs-work/photo/make-materials/nondeterministic/make.materials.gold-coin/`.
  Its caption now says only that the coin shows the warm yellow of gold.
- `ball-metal`: published: a smooth grey metal ball with a soft highlight. No worn marks: the Metal032 color map varies
  by about 3 levels (standard deviation) and the roughness channel only between 89 and 117 of 255.
- `ball-normal`: blocked. `Metal032_NormalGL.jpg` is flat (every channel 126 to 129, standard deviation 0.2 levels):
  the picture with the normal map differs from `ball-metal` by at most 10 levels in 2,043 bytes, no bumps visible.
  Nearest honest picture: none with these files; the page would need a texture set with real relief (and the same for
  the `FlipGreen` step), or words saying the bumps of this set are too fine to see.
- `coin-glow`: published: as the page says, the 50-nit glow makes no visible change in the sun (47 bytes differ from
  `final` by at most 7 levels). Shows and alt say so.
- `albedo-view`: published: the wall in fine red stripes, the coin plain yellow, the ball plain grey. Captures draw no
  overlays, so the legend `Above 0.85` is not in the picture; the alt no longer names it.
- `final`: published (the coin as in `result`).
- `material-editor` and `normal-warning` (kind editor, both wait for tier 2: editor screenshot): settled 2026-11-18
  with the provisional build (engine 5b975ad2), not published; publish them when the pin moves. Both picture the
  Asset tab (`AssetInspector`) at 1:1 in `layouts/materials.ini` (1280 x 800, Inspector column 380 px).
  - `material-editor`, round 1: the recipe made Gold at the values of gold, but the figure follows step 1, which makes
    Gold with no values. Now `material.create` without properties: a white Base Color, Metallic 0, Roughness 0.5,
    then the other rows and the texture slots, all None; shows and alt say so. Gained `waitsFor`.
  - `normal-warning`, round 1: in the PhysicsPlayground sample, Ball with its three maps, the normal map's Usage set
    to Color: below Normal Map the warning "Metal032_NormalGL is imported as Color: its normals will be wrong" and
    the button Import as Normal Map, as the page says.
  - Page words: step 1's "You should see" names the rows `BaseColor` and `EmissiveColor`; the tab labels them
    Base Color and Emissive Color.

Mended 2026-11-18 after a viewer's report:

- `result`, `final`, `coin-glow`: retaken with the coin leaning back (Rotation 115, -35, 0; y 0.38), its axis at right
  angles to the half vector of the sun and the camera, so the rim's curve catches the sun's highlight as a white streak
  and the flat face, far from that vector, shows a warm gold. A flat face at roughness 0.3 under the sun is either all
  blown white or all pale (GGX's tail spans the whole face), so the gleam can only sit on the rim. Trials in
  `docs-work/photo/make-materials-trial/` (face 21 and 26 degrees off the half vector: pale and flat; rim pose chosen).
  `final`'s caption no longer claims the Albedo view (it is the lit view); it says the wall is gone.
- `ball-metal`: caption now says Metal032 varies so little that the ball looks smooth, with no visible wear.
- `albedo-view`: caption now says the Scene view also shows a legend that the picture leaves out (captures draw no
  overlays).
- For the planner (page words): line 27 "a ball of scratched metal" and line 242 "worn marks ... dull where it is
  scratched" need "smooth grey metal" (Metal032 has no visible wear). Line 482 places `Wall` at Translation
  [0, 1, 3], between the reader's camera and the coin and ball, so the reader's wall hides them; the figure's wall stands
  at [0, 1, -1.5], behind them, and the page's command should say so.

Page words the pictures contradict: line 131 ("a sharp highlight from the sun" on the coin), lines 27 and 242
("scratched", "worn marks, shiny where the metal is clean and dull where it is scratched"), lines 275, 315 and 334
(bumps and dents of the normal map, their inversion by `FlipGreen`).

Mended 2026-11-18 (editor figures) after a viewer's report:

- `normal-warning`: in 1280 x 800 the Asset tab ended at the button Import as Normal Map and cut its lower border.
  Round 2 at 1280 x 880 showed the button whole but cut the Clearcoat row at the new edge. Round 3 at 1280 x 866 with
  `layouts/materials-tall.ini` (`materials.ini` with every column 66 px taller; the Asset tab 380 x 788): the warning,
  the whole button, then Occlusion Map and Emissive Map, the edge in the blank gap below them. Caption, alt and shows
  unchanged (still true). Provisional build, not published; `waitsFor` kept.

Finished 2026-11-24 at the pin v0.8.0 (319075e3, Release build):

- `ball-normal`: taken and published. Its caption already said what the pin shows (the map of this set is nearly
  flat, so the ball still looks smooth and even), so the picture can show its caption: a smooth grey metal ball with a
  soft white highlight at its upper right and a long shadow to its left, like `ball-metal`, as `coin-glow` shows the
  unchanged look of its checkpoint. The alt said "a dark ground"; the ground is grey, and the alt now says so. The
  checkpoint's words (step 1's and step 4's "You should see") already say the map is too flat to show its dents.

## Settled with the editor (2026-11-18)

- The steps now name the material editor's rows by their labels (`Base Color`, `Emissive Color`, `Emissive Intensity`, `Base Color Map`, `Metal/Rough Map`, `UV Tiling`), as code: the `names` check does not know the material editor's labels, so they cannot be bold. `Metal/Rough Map` is the display name `Material.cpp` gives `MetallicRoughnessMap`.

## Tutorial run (2026-11-18)

- Round 1 (chain from make/assets): the tutorial and exercise 1 passed as written.
- Mended: stage 2 copied the textures into the project and imported them in setup; it now imports them from the
  release (`@RELEASE@/Samples/PhysicsPlayground/…`) as the page's tab does, and waits on `asset.info` (`importing`
  false) for each texture, checking the page's usages (Color, Data, NormalMap). The page's tab names
  `<release folder>` like the other Coin Run pages, not `<path of the release>`.
- Strengthened with the page's values: gold's base color, roughness and emission; the warning's property and text
  (`Metal032_NormalGL is imported as Color: its normals will be wrong`); the usages and `FlipGreen` the import answers
  report; Mask's cutoff and the alpha 0.4, Blend, and the glass's four values.
- Page tabs now list every command the file runs per step: the gold's values put back, the other two `asset.info`
  calls, `material.get` after each usage change, `FlipGreen` off again, Blend, and the wall's delete and the Lit view
  before the save (the file's order now follows step 4's).
- Round 2: both files pass with the mended file; stamped.
- Final run (2026-11-24, pin v0.8.0): the pin-build stamps were current; with the official v0.8.0 package
  (`Strata-0.8.0-windows-x64.zip`) the tutorial (5 stages, chain from make/assets) and exercise 1 passed as written.
  `tutorials.py check --release` finds nothing.

## Engine

None found: every command did what its description says.

## Track walk G, final, segment 3 (2026-11-24)

Answers to `plan/walks/G-final-3.md`, WK1 to WK5:

- WK1: What you need now names the download of Assets' end state (the box at the end of its Result) for a reader
  who arrives here.
- WK2: the zip's top folder is named after the page (`Assets`, `tools/tutorials.py` `project_files`), which What you
  need now says. Basic 3D already made `Materials` (with `Ground.stmat`, `ProjectTemplates.h:49`), so step 1 opens it
  instead of making it, for every reader.
- WK3: the first command with `<the ID of …>` says to take the ID from `entity.find` (as `make/scenes-entities`
  taught); the Scratch and Wall steps say that `entity.create` answers `id` and that `entity.find` with `Wall` also
  finds `Walls/Wall`.
- WK4: the level's four walls use the default material, white (1, 1, 1) (`Material.h:26`), so the Albedo view stripes
  them too; the steps say so and that they stay striped. The legend is drawn only in the window: the command tab says
  so. The figure's caption names the walls out of its view.
- WK5: rejected; a reader who uses the command tabs drives the editor's window and sees the Scene view.
