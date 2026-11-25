# Notes: make/lighting

## New terms

None proposed. The page defines the four glossary terms of its brief in bold (lux, nits, candela, exposure, preview lighting).

## Since

- since 0.3.0: directional light, procedural sky and automatic exposure exist from the first tag (Docs/Manual/Lighting.md at the pin; the brief's inventory rows give automatic exposure 0.3.0, units 0.6.0, presets and the Luminance view 0.7.0). The page teaches them together, so it takes the oldest.

## Requests

- Figures (all not yet taken): eight entries in `src/content/figures/make/lighting.json`. The three editor figures need `layouts/make-lighting.ini`. They start from `basic3d` (a cube and, for the result, a ball stand in for the coins), because a figure project cannot start from the tutorial's end state; the integrator may swap in the real level.
- Only the checkpoint pictures are requested, not one editor picture per step.
- The tutorial file starts from `make/prefabs`; the fixed exercise file `tutorials/make/lighting/exercise-2.tutorial.json` starts from `make/lighting`.
- The tutorial's stage 3 copies the HDR from the engine's samples (`Samples/ThirdPerson/Assets/Environment/`) to `Assets/Environment/` but runs no command that sets the map or extracts the sun (not verified how `component.set` takes an asset path); the integrator may add `component.set` of `EnvironmentMap` and `lighting.extractSun`.
- Word and name requests: the words `Overcast` and `Hazy` are written as bold labels; `Emissive Color` and `Emissive Intensity` are the labels of the material's Inspector (Strata/src/Strata/Renderer/Material.cpp registers `EmissiveColor` and `EmissiveIntensity`), which the names dump lacks, so `names` reports five findings left in place.
- Names to add to `tools/data/names.txt` for the heading-case warnings: Basic 3D, Coin Run.
- Link hosts: none.

## Findings not applied

- critic-make-a-14: applied (step 3 of "Tell preview lighting from real light" adds a cube and a camera to the new scene, and step 1 says that the editor asks about changes you did not save).
- critic-make-a-16: applied (the sun's softness is written **Angular Diameter**, with its stored name `ShadowSoftness` once).
- Brief item (3), "turn the Sun off": not applied as written. The page lowers the sun's **Intensity** to 120 lux (ten stops) instead, because the effect of a disabled sun on the atmosphere sky could not be checked in the code, and the lower intensity gives a computable gray failure.
- Brief item (9), the Albedo view: only named, with a link to the materials chapter.

## Not verified

- Name and path of the coin material (`Materials/Gold.stmat`) and that the gold material is the one every coin but `Coin (1)` uses.
- That clicking an empty area of the Hierarchy clears the selection, and that the Sky section shows only with nothing selected in the button flow described.
- That **Auto Exposure Min EV** 6 darkens the 120 lux scene to dusk (an estimate: the scene's metered brightness was not measured), and that -15 looks close to the automatic picture.
- That 200 nits of emission shows in shade and 1,000 nits in the sun (the brightness of the sunlit ground was not measured).
- That `component.set` accepts an asset path for `EnvironmentMap`, and the exact keys of `scene.open` (`scene`, `force`) in the preview step.
- The pin's Inspector label of the sky's `SunSize` (the page uses **Angular Diameter** for the sun only).
- Which ring of the Rotate gizmo raises the sun (the page says "drag the rings").

## Clerk

- No term asked.
- Admitted to names.txt: Basic 3D, Coin Run.
- Left for the planner: the figures and their layout, stage 3's commands, the names the dumps lack (Emissive Color, Emissive Intensity).

## Names of this page

- `Emissive Color`: the material inspector's label of `EmissiveColor` (Strata/src/Strata/Renderer/Material.cpp:33), named by `PascalCaseToDisplayName` (Strata/src/Strata/Reflection/PropertyBuilder.cpp:25) and drawn by StrataEditor/src/UI/MaterialEditor.cpp:105; the dumps list no material property.
- `Emissive Intensity`: the same, for `EmissiveIntensity` (Strata/src/Strata/Renderer/Material.cpp:36).

## Figures

Photographed 2026-11-18 at the pin (Release build), two rounds, all five scene figures published.

- Round 1 (`camera: "scene"`, the template's camera at 0, 2, 6): every picture complete but the cube small in the frame;
  `exposure-sweep` showed only ground and sky (no object), and the captions and alts named coins, dark stone and band
  counts the picture did not show.
- Round 2: each figure got its own camera (cube figures from -0.3, 1.2, 4.5 toward -0.8, 0.4, 0 with fov 40, so sky and
  shadow both show; `shadow-low-sun` from above and in front so the shadow's length reads; `result` closer on the cube
  and ball); `exposure-sweep` gained the cube. Captions and alts rewritten to what the pictures show.
- `luminance-view`: the capture records surface EV100 median 14.9 (band 9, orange-yellow) and a sun-to-sky ratio of
  8.1; the shadow is in band 6 (yellow-green) with a green contact rim (band 5). The caption names the two colors and
  says the bands between them are absent: without the editor's legend a reader cannot count them in the picture.
- `exposure-sweep`: manual -15 comes out a little darker than automatic exposure; the caption says "come out close",
  not "agree".
- Not taken (kind `editor`, not this card's): `inspector-template`, `sky-inspector`, `preview-lighting`; their layout
  `layouts/make-lighting.ini` does not exist yet.
- Page text the pictures contradict: "What you will make" promises Coin Run with coins whose shadows read, but `result`
  is Basic 3D with a cube and a ball (no coins); the nearest honest fix is words saying the result figure shows the
  lighting on test shapes, or a recipe built on the Coin Run project once the book has one to load.

Mended 2026-11-18 after a viewer's report (words only, no retake: the pictures were right, their words were not).

- `exposure-sweep`: the page draws only `variant=auto`, and the figure plugin renders the recipe's caption and alt for
  every variant, so both now describe the automatic picture alone. The page would need
  `::compare{id=exposure-sweep before=auto after=zero}` and `::figure{id=exposure-sweep variant=minus15}` to show the
  white and the -15 pictures (published, unused).
- `sky-presets`: four `::figure` lines share one caption and alt (variants have no words of their own in the plugin), so
  the caption names the presets in the pictures' order and the alt labels each part. Measured: Hazy's top sky is paler
  and grayer than Clear's (79,124,164 against 96,135,169), its horizon slightly darker (152,165,170 against
  145,156,165), its shadow lighter (19,26,37 against 26,33,43) and longer (left edge at x 436 against 481). Better:
  two `::compare` figures (clear/hazy, overcast/golden-hour), whose labels name the presets.
- `luminance-view`: the earlier words were wrong. The bands' colors are the editor's ramp (`EditorLayer.cpp`:
  Basalt, Azurite, Malachite, Sulfur, Limestone mixed in sRGB over 12 bands from EV 5); the pixels match band 9 for
  the sunlit ground (233,204,116: sand yellow), band 7 for the shadow (155,193,105: yellow-green), band 6 for its rim
  (92,191,128: green), band 10 for the upper sky (cream) and band 11 for the cube's face and the sky at the horizon
  (off-white). Ground and shadow are two bands apart in color, with only band 8 (yellow) missing, though the capture's
  ground median (EV 14.9) and sun-to-sky ratio (8.1) put them nearly three stops apart. The page's step says "about
  three bands above its shadow"; the picture shows two: the words would need "two to three bands".

Editor figures, 2026-11-18, taken with the provisional build (engine 5b975ad2; nothing published, `waitsFor` kept),
two rounds in two holds of the lock. Layouts made: `layouts/make-lighting.ini` (1280 × 800, a copy of
`first-game-tall.ini` with its 380 px Inspector), `make-lighting-short.ini` (960 × 440, a copy of
`make-scenes-entities-short.ini`) and `make-lighting-side.ini` (960 × 540, from `editor-tour-side.ini`: the Scene and
Game views side by side, 388 px each, the Inspector closed).

- `inspector-template`: round 1 pictured the Inspector panel (no longer the whole window) with `Sun` selected: Transform,
  then Directional Light with Color 1, 1, 1, Intensity 120000, Angular Diameter 0.53, Cast Shadows checked and the
  shadow rows; all of it fits at 1280 × 800. Good. The caption's "in lux" is the page's fact (the field's hint text);
  the picture shows the number only.
- `sky-inspector`: the scene's Inspector draws Physics, Streaming and Sky as closed sections, the Sky row reading
  "Atmosphere" at its right; no command opens a section (`editor.showPanel` has no such parameter), so the Source row
  and the preset buttons (`InspectorPanel::DrawSky`) cannot be pictured. Round 2 pictures the state before "Open its
  Sky section" in a 960 × 440 window (round 1's 1280 × 800 left two thirds of the panel empty); caption, alt and shows
  now say closed sections and the source in the Sky row. What the step's "You should see" names (the Source row, the
  presets) would need a command that opens an Inspector section, or a diagram of the open section.
- `preview-lighting`: the recipe's `make-lighting.ini` held Scene and Game as tabs of one node, so `editor.showPanel
  Game` hid the Scene view; round 1 used the side-by-side layout (Inspector cut at the right edge), round 2 closed the
  Inspector, cleared the selection and set the editor camera (`camera.set` from 2.2, 1.8, 3.2 toward 0, 0.3, 0) so the
  cube is large. The Scene view shows the white cube with a lit top and front and a darker side; the Game view is not
  black: the cube's front face is a dim gray-blue square on near-black. Caption and alt say "dim
  on black". The page's step 2 ("The Game view shows black") and step 3 ("as black as in the Game view") would need
  "almost black, the cube a dim gray shape", unless the pin's renderer differs from the provisional build here.

Viewer's report, 2026-11-18, on `preview-lighting`: the Game view shows a gray cube on near-black, against step 2's
"The Game view shows black" and step 3's "as black as in the Game view". Measured on the provisional take: the cube's
front face 72, 73, 85, the view's background 10, 11, 16. The fault is in the page's words, not the recipe: the recipe
repeats the reader's steps (new scene, cube, camera at 0, 1, 5, no light), and darkening the Game view (a manual
exposure, another camera) would picture what the reader does not see. Recipe, caption and alt unchanged ("dim on
black", "a dim gray cube"); no retake. The page needs, in step 2, "The Game view is dark: a dim gray cube on black" and,
in step 3, "as dark as in the Game view"; the paragraph before the steps ("draws black in the game", "stays black")
and the summary line "the game draws it black" would need "dark" as well.
- Settled 2026-11-18 (page words): the game draws a scene without light dark, not black: without a sky the renderer uses the constant ambient (0.03, 0.03, 0.04; `SceneRenderer.cpp`, `RendererComponents.h`). Steps 2 and 3, the paragraph before them, the summary and question 6 say dark. Step 3 of reading the sky now says the closed Sky row names Atmosphere and the open section shows Source and the presets.

Taken again 2026-11-23 at the pin v0.8.0 (319075e3, Release build), one round in one hold of the lock, recipes unchanged.

- Scene figures (`result`, `exposure-sweep` x3, `sky-presets` x4, `shadow-low-sun`, `luminance-view`): `figures.py
  compare` against the originals of pin 822a7a46 found 0 of 10 pictures differing (largest block 0); publish left the
  files unchanged.
- Editor figures, taken without `--provisional` and published (`waitsFor` removed, as `check` asked), layouts unchanged:
  `inspector-template` shows the Sun's Inspector with Intensity 120000, Angular Diameter 0.53 and Cast Shadows checked,
  the whole panel readable; `sky-inspector` shows the scene Main with Physics, Streaming and Sky closed, the Sky row
  reading Atmosphere; `preview-lighting` shows the Scene view's cube with a light top and front and a shaded side, and
  the Game view's cube a dim gray square on near-black, as the settled words say ("dark").

## Tutorial run

Run 2026-11-18 at the pin (Release build), after the chain from make/editor-tour through make/prefabs: the tutorial
(7 stages) and exercise 2 passed in the first round, with the file mended before it ran.

- The file was thinner than the page and now does what the tabs say: stage 1 checks every "You should see" value (the
  sun's 120000 lux, Angular Diameter 0.53 and Cast Shadows, the four exposure values, the sky's Atmosphere source);
  stage 2 sets the sun back to 120000 after the 60000 lux test and raises Auto Exposure Min EV to 8, the page's value
  (the file had 6); stage 3 sets the HDR map as the sky's source (`component.set` takes the asset's path), runs
  `lighting.extractSun` and `asset.setImportSettings {"RemoveSun": true}`, and applies Clear before the four presets in
  the page's order; stage 5 saves, makes the scene `Dark` with a cube, a camera and a directional light, switches the
  preview off and on, and opens `Scenes/Main.stscene` again; stage 6 sets the gold's emission (200, 1000, 200); stage 7
  plays 60 paused steps. Stages 4 and 7 and the exercise check the sun's height through `sunDirection` (25, 35 and 6
  degrees).
- Page: the Extract Sun tab passed `"sky": "Sky"`, but `sky` takes an entity ID; it now runs with no parameters (the
  first active sky light). The Coin Run tab of `scene.open` names `Scenes/Main.stscene`; the preview tab turns the chip
  on again as the editor tab does; the emission tabs name the 1000 and the 200. Three sentences were cut to keep the
  page under its 6,500 words.
- Measured answers: Extract Sun wrote 4.43 lux (map's sun not clipped, 3.3 degrees across, 70 texels); the presets'
  `groundIlluminance` was Clear 97,912, Hazy 88,882, Overcast 1,500 and Golden Hour 40,904 lux. Verified since "Not
  verified" above: `component.set` accepts an asset path for `EnvironmentMap`, and `scene.open` takes `scene` and
  `force`.
- Run again 2026-11-23 at the pin v0.8.0 (319075e3), Release build, after the chain through make/prefabs: the tutorial
  and exercise 2 passed in the first round as written.

## Engine

None found by the run.

## Track walk G, final, segment 3 (2026-11-24)

Answers to `plan/walks/G-final-3.md`, WK7 to WK11:

- WK7: the command tabs showed the tutorial file's `entityName`, which no engine program reads (`component.get`
  wants a 16-hex ID). They now pass `"entity": "<the ID of Sun>"` (and Post Process, Sky), and the first says to take
  the ID from `entity.find`. Step 4's tab also lists the sun's reset to 120000, which the file runs.
- WK8: matched; nothing to change.
- WK9: the presets' tab lists the four commands in the file's order and spells `GoldenHour`; it gives the
  `groundIlluminance` of each (97,912, 88,882, 40,904, 1,500 at v0.8.0, package run) and says no command answers the
  sky's light. The Overcast paragraph says the 1,300 lux are 1,500 times 0.87 (flat ground). Extract Sun's result
  says the map's sun is about 4.4 lux (`illuminance` 4.40, `intensity` 4.43 with the sky's Intensity 1). Exercise 2's
  answer said its solution checks the ratio; it checks `sunDirection`, which the answer now says.
- WK10: the play camera of Basic 3D looks down 55 degrees (rotation x -0.4617, vertical field of view 60), so the
  Game view holds no sky; step 1 places the blue sky in the Scene view and step 2 says the Game view shows none.
- WK11: rejected; the reader looks at the editor's window.
- To keep the page within size L after these lines, the intros of the exposure experiments, "Why 16?", preview
  lighting and the Luminance bands were tightened (no fact removed).
