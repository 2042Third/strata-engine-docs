# Notes: make/look

## New terms

None proposed. The page defines the one glossary term of its brief, **tone mapping**, in bold.

## Since

- since 0.3.0: Post Process exposure and the Camera exist from the first tag (the brief's inventory rows; Docs/Manual/Camera.md at the pin dates most of the effects to 0.7.0). The page teaches them together, so it takes the oldest.

## Movable claims

Reviewed at v0.8.0 (319075e3) against `Docs/Releases/0.8.0.md` ("Upgrading from 0.7.0").

- Motion Blur off by default in a new Post Process: `Strata/src/Strata/Renderer/RendererComponents.h:320`.
- Off in the template and every sample since 0.8.0, because it smeared moving edges too wide or too narrow:
  `Docs/Releases/0.8.0.md:482`; the Course's Post Process stores `"MotionBlur":false`
  (`Samples/ThirdPerson/Assets/Scenes/Course.stscene:5`).
- Motion blur samples Off, 8, 12, 16 by preset: `Strata/src/Strata/Renderer/RendererQuality.cpp:56`; more samples show
  less streak noise: `Docs/Manual/Camera.md:124-126`.
- The players' rows Motion blur, Depth of field, Film grain and Chromatic aberration, Scene or Off under every preset:
  `Strata/src/Strata/Renderer/RendererQuality.cpp:182-185` (outside the preset loop at lines 456-476);
  `Docs/Manual/Graphics.md:77-81`.
- The cost table's numbers and the 12 samples of the turning-camera row: `Docs/Manual/Camera.md:170-183` ("What it
  costs"), unchanged by the release.
- The figure `motion-blur` waited for `editor.screenshot`, which the pin has; it now waits (tier 3) for a command that
  scrolls the Inspector, since the pin's `editor.showPanel` and `editor.screenshot` take no section or property
  (`StrataEditor/src/EditorLayer.cpp:276`, `:332`).

## Requests

- Words for `tools/data/extra-words.txt`: decals, volumetric (the not-done list of "What each effect costs"; the words name the missing features).
- Names the dumps lack, left as `names` findings: the labels Center Weighted (the display name of `AutoExposureMetering`'s second option in `Strata/src/Strata/Renderer/RendererComponents.cpp`), Emissive Color and Emissive Intensity (`Strata/src/Strata/Renderer/Material.cpp`).
- Figures, none taken: `src/content/figures/make/look.json`, ten entries on the `ThirdPerson` sample (`scene.open` of `Scenes/Course.stscene` in each setup). The editor figure `motion-blur` needs `layouts/make-look.ini`. Motion blur cannot be photographed (captures never blur), so that figure shows the Inspector. The `tone-curves` and `lookup-intensity` figures use variants (`filmic`, `aces`; `zero`, `half`, `full`); the page places `variant=filmic` and `variant=half`.
- The tutorial file starts from the `ThirdPerson` sample with no download in its first stage. Stage 4 copies `book:tutorials/make/look/warm-look.cube` (since walk G-final-9 a 2-point warm table that the page prints whole, an affine map that the 17-point table of before held up to its clamp at 1) to `Assets/Lookups/warm-look.cube`; the page's step imports it with `asset.import` from the download folder.
- The fixed exercise file is `tutorials/make/look/exercise-3.tutorial.json`; it starts from the end state of this tutorial.
- Link hosts: Wikipedia (Further reading, not linked).

## Not verified

- That the Inspector's Sky section shows with nothing selected and then offers **Add Height Fog** (`StrataEditor/src/Panels/InspectorPanel.cpp:1714` shows the button while the scene has no fog; the context of the section was not read).
- That `component.set` accepts a lookup by path and an entity id for `FocusEntity`, and that the command tab of step 3 of "Use the Camera as a lens" needs the id of `entity.find`.
- That `asset.import` accepts the `.cube` file with `directory` `Lookups`.
- What the Course shows at each value (exposure, fog, moonlight at Sun Intensity 0.2 and Sky Intensity 0.001, the red lamp): no picture was taken; the "You should see" lines come from the engine's guide and the code's rules.
- The cost numbers are those of `Docs/Manual/Camera.md` ("What it costs"), not measured again; they hold for a 3840x2160 image on the guide's reference card.
- That Max EV 16 is not reached in the Course's own light (the sun is 4.4 lux in the scene; the page does not claim it).

## Findings not applied

- critic-make-b2-17: applied in a changed form. The exercise lays the fog as a sea below the islands (base at -2 m, falloff 0.02 for a layer whose density falls by e every 50 m), not in a valley. The Course's lowest islands stand at height 0.
- The page's learn lines are five, so the brief's cost objective is a part of `add-lens`.
- Brief item: "Max EV 16 for a real sun ... checked in the Luminance view" is applied as words and one Luminance step; the Course's sun is too weak to show the cap, so no step sets Max EV.
- Brief item: the orthographic near and far planes are named, not set in a step.
- The "valley" copy (High Desert Outpost) is not used.

## Left failing (round limit)

- `copied-text` at the sentences on Contrast and Saturation (line 255) and on White Balance Temperature (line 365), against `Docs/Manual/Camera.md`.
- `paragraph-length`: the paragraphs on Filmic and on ACES hold six sentences.

## Clerk

- Admitted to extra-words.txt: decals (G0 has 5), volumetric (G0 has 1).
- Left for the planner: the names the dumps lack (Center Weighted, Emissive Color, Emissive Intensity), the ten figures, `layouts/make-look.ini`, the lookup download.
- Page fixes for the build's rules: "How a camera makes a picture" moved before "## What you need"; "What each effect costs" became a ### section of "Use the Camera as a lens", before its checkpoint; the link to reference/quality.md (no page of the outline) now goes to image/quality-settings, the outline's page of the quality rows and their presets.

## Names of this page

- `Center Weighted`: the display name of the option `CenterWeighted` of Auto Exposure Metering (Strata/src/Strata/Renderer/RendererComponents.cpp:570), which the inspector draws (StrataEditor/src/UI/PropertyWidgets.cpp:1035); the components dump lists the option's name only.
- `Emissive Color`: the material inspector's label of `EmissiveColor` (Strata/src/Strata/Renderer/Material.cpp:33), named by `PascalCaseToDisplayName` (Strata/src/Strata/Reflection/PropertyBuilder.cpp:25) and drawn by StrataEditor/src/UI/MaterialEditor.cpp:105; the dumps list no material property.
- `Emissive Intensity`: the same, for `EmissiveIntensity` (Strata/src/Strata/Renderer/Material.cpp:36).

## Figures

Photographed 2026-11-18 on the pin's Release build (work folder `docs-work/photo/make-look`). Every scene recipe now names
`"scene": "Scenes/Course.stscene"` (the sample's start scene is the main menu, so `check` read the wrong scene) and turns
`HUD` and `Menus` off. The book's `tutorials/make/look/warm-look.cube` is imported with `asset.import` by its absolute
path in this worktree (the command takes absolute paths only, and no recipe field resolves a book file); `camera-lens`
names the Robot by its id (A94EC4E371BEB484 in the scene document) instead of a `$ref` to `entity.find`.

Published, round 1 (eight figures; captions rewritten from the pictures):

- `result`: no lantern is in the scene camera's view, so the caption drops "soft glow around the lanterns"; it shows the
  warm grade and the haze over the far islands.
- `start-course`, `height-fog`, `lookup-intensity` (sky blue 105, 99, 93 at 0, 0.5, 1): as captioned.
- `exposure-luminance`: the meter's EV100 is the same as the starting picture's (1.796 in both results), so Exposure
  adds its full stop; the old caption's "the meter pulls part of it back" was false and is gone.
- `tone-curves`: ACES at +0.8 is a little brighter and more saturated than Filmic (numbers in the manifest); the bright
  parts keep their hue, so the caption no longer points at it.
- `lens-effects`: vignette and grain show (grain plain in an enlarged crop of the sky); no light source is in view, so
  bloom 0.15 shows no glow, and the caption says so.
- `camera-lens`: at 30 degrees the robot fills the frame and stays sharp; the islands behind blur. There is nothing near
  the camera to soften, so the caption names only the far blur.

Waits: `night-look` (three rounds).

- Round 1, camera at (-1.5, 2.6, -14) toward Lantern A: the ground is a bright, saturated teal under a black sky; the
  lantern's head clips to white.
- Round 2, the page's recipe through the scene camera and from closer to Lantern A: the same. The meter sits at its floor
  (EV100 -1.0 = Auto Exposure Min EV -4 plus 3), so it lifts the moonlit scene as far as it may; the lit ground measures
  4/144/142 (the day's grass 69/141/103): as bright as the day, only teal. The lantern head measures 249/249/247.
- Round 3 (trials, not the page's recipe): Auto Exposure Min EV -2.5 gives EV100 0.5 and a dim teal course under a black
  sky (ground 2/75/73) through the scene camera, the nearest honest "dark, cool" picture; the lantern head still reads
  white (232/231/228), so "the lanterns glow warm" is not shown either way. Min EV -1.5 (EV100 1.5) is darker still.
- What the page would need: a step that raises **Auto Exposure Min EV** (about -2.5) or turns Auto Exposure off with a
  manual Exposure, since the meter, not the -1.5, sets the night's brightness here; and a lantern that reads warm at
  4500 K (a warmer EmissiveColor or a lower emissive intensity), or words that do not promise warm lanterns. With such a
  step, the scene-camera recipe of round 3 (Min EV -2.5) is the picture to take.
- `motion-blur` (kind `editor`) is not a photographer's figure; it also waits for `layouts/make-look.ini`.

Mended 2026-11-18 after a viewer's report (captions from the pictures; `camera-lens` taken again):

- `tone-curves`: the page shows only `variant=filmic` at checkpoint 3, byte-identical to `start-course`; that variant now
  has its own caption ("Back on Filmic at Exposure 0: the starting picture"). The ACES comparison is on no page. What
  the page would need: `::compare{id=tone-curves before=filmic after=aces}` in "Choose the tone curve", outside the
  checkpoint.
- `lookup-intensity`: the page shows `variant=half` at checkpoint 4, but step 4 leaves the intensity at 1. The half
  variant's caption now says it is the half strength and that step 4 ends at 1. What the page would need: `variant=full`
  at the checkpoint (the full grade: a gray-yellow sky, yellower grass), and the three strengths elsewhere if wanted.
- `lens-effects`: grain 0.2 is invisible at page width (sky standard deviation about 2.7 levels); the caption and alt no
  longer promise it. A crop shows only with `::figure{... crop=}` on the page; what it would need for the grain: a crop of
  the upper-right sky (about x 900-1220, y 20-200 of 1280x720) at scale 3 and a figure that names it.
- `camera-lens`: now the checkpoint-8 state (default 60-degree view, f/2.8, Depth Of Field on, focus on the robot), so
  the islands and the robot's feet are in frame; the blur is slight (castle edge energy 351 against 507 in the starting
  picture), and the caption says so and points at Perspective FOV 30, as the page's step 4 does.
- `height-fog`, `result`: captions name what changes (the castle bluish and paler, the horizon clouds gone into haze; a
  gray, hazy sky rather than a warm one).

Editor figure `motion-blur`, 2026-11-18, one round with the provisional build (engine 5b975ad2; work folder
`docs-work/photo/make-look`); not taken for the page, the recipe left waiting:

- The recipe now pictures the Inspector panel (`editorWindow.panel`) of the checkpoint-7 state: the Course open
  (`"scene"`, so the take opens it with `force`), Motion Blur set on with `component.set`, the Post Process selected;
  its old `scene.open` and `editor.showPanel` steps are gone (the take runs both), and it keeps
  `waitsFor: tier 2: editor screenshot`. The caption no longer says the limits are grey: the step turns the blur on, so
  they are not; caption and alt name the three values (on, 180, 0.02, the scene's own).
- Round 1, window 1280 x 1360 (`layouts/make-look.ini`, the tallest window the 1440-row display holds, Inspector 380 px
  wide): the panel ends at Ambient Occlusion Intensity. The Inspector draws the Post Process in section order (Tone and
  color, Exposure, Bloom, Ambient occlusion, Global illumination, Anti-aliasing, Reflections, Lens, Motion), so Motion
  is the last of its nine sections, about 2200 px below the panel's top (the scroll bar covers about half the content).
  No command scrolls a panel, and no display holds the window that would reach it.
- What commands cannot show: the Motion section. What the page gets instead: nothing yet; the nearest honest picture is
  a text figure of `component.get` on the Post Process cut to `MotionBlur`, `MotionBlurShutterAngle` and
  `MotionBlurMaxLength` (true, 180, 0.02), or no figure at checkpoint 7. What the recipe would need: a command that
  scrolls the Inspector to a section or property (for example `editor.showPanel {panel: "Inspector", property:
  "MotionBlur"}`); then this recipe with a 960 x 540 or 1280 x 720 window takes the picture.

Taken again 2026-11-23 at the pin v0.8.0 (319075e3, Release build; work folders `docs-work/photo/make-look` and
`make-look-r2`; dumps `reference/_dumps/319075e3…`):

- `result`, `start-course`, `exposure-luminance`, `tone-curves`, `lookup-intensity`, `height-fog`, `camera-lens`: the
  new takes match the published files within site.md's thresholds (`figures.py compare`: largest pixel difference 4 to
  21 levels, mean below 0.02; publish: mean 0.22 to 0.28); the files stay, their stamps name the new pin. Looked at
  again: they still show their captions.
- `lens-effects`: published anew (mean 0.67 against the old file): the film grain is random per take; corners and sky
  look the same. Caption shortened (same claims) to keep the page within size L.
- `night-look`, published (two rounds). The page now raises **Auto Exposure Min EV** to -2.5 (the step the last take
  asked for), so the recipe sets `AutoExposureMinEV` -2.5 too. Round 1, scene camera: a dim teal course under a black
  sky (meter EV100 0.5), but no lantern in view, so "the lanterns glow" did not show. Round 2: a recipe camera at
  (-1.2, 2.6, -15) toward Lantern A (2.3, 1, -22), fov 45: a dark blue-green island (mean 5/37/34 against the day's
  79/120/99), the lantern head white with a soft bloom halo, lighting the tree above it. The glow reads white, not warm
  (the lantern's light is warm, 1/0.72/0.4, but 4500 K cools it and the head clips), so caption and alt say "white"
  and no longer promise warm lanterns. The page's "a dark, cool picture with the lanterns glowing" holds.
- `motion-blur`: still waits (tier 3, a command that scrolls the Inspector); not taken.
- Size: the page stood at 6,509 prose words with the old captions (limit 6,500); the shorter `night-look` and
  `lens-effects` texts bring it to 6,497.

Mended 2026-11-23 after a viewer's report (pin v0.8.0, work folder `docs-work/photo/make-look`):

- `camera-lens`: at the default 60 degrees the castle looked as sharp as in the starting picture, so no blur showed.
  The page shows one `::figure{id=camera-lens}`, so no 60/30 pair is possible without a page edit; the recipe now sets
  `PerspectiveFOV` 30 (step 4's "If you do not see it") with f/2.8 and the robot in focus. One round: the robot fills
  the frame and is sharp; the barrels and islands behind it are plainly soft (the castle is above the frame). Caption,
  alt, shows and numbers say so and name 60 degrees as the default. What the page would need for the pair: a figure
  recipe with variants `fov60` and `fov30` and `::compare{id=camera-lens before=fov60 after=fov30}`.
- `lookup-intensity`: not taken again. The page shows only `variant=half`, which alone hardly differs from the plain
  picture (sky above the castle 90/99/116 at 0, 94/99/109 at 0.5, 98/100/102 at 1; grass at the lower left
  75/157/113, 79/157/106, 82/158/99). The half caption now points at those two places and at the starting picture near
  the top of the page; the values are in `numbers`. What the page would need: `::compare{id=lookup-intensity
  before=zero after=full}` in step 4 (even at 1 the grade is gentle, so only a slider shows it plainly).

Finished 2026-11-24 at the final pin v0.8.0 (319075e3, Release build; work folder `docs-work/photo/last-make-look`):

- `motion-blur` (editor, the Inspector's Motion section) keeps its `waitsFor` (tier 3: a command that scrolls the
  Inspector), the request for a later edition, and names its stand-in `motion-blur-turn`; the page places the stand-in
  at checkpoint 7.
- `motion-blur-turn`, new, kind `live` (the tool now takes live figures), published in one round: the recipe of
  image/motion-blur's `turn-mb180` at 1280 x 720, quality high (Motion Blur on with the Course's own shutter angle 180
  and Max Length 0.02, automatic exposure held still, the look pressed at 0.75 from fixed step 24, frames 30 to 33;
  the three takes agree). Looked at enlarged: the far course (castle, barrel, coins) and the pine at the left streak
  sideways; the robot, which the camera follows, and the HUD text stay sharp, as the section's paragraph and step 1's
  "You should see" say. The picture is the state of step 1 (blur on, 180), the checkpoint's state after step 2's stop.
  The HUD stays: it is the game the Game view shows, and it shows that text never blurs.
- Size: caption and alt of the stand-in count as prose; the page stood at 6,484, so two sentences were shortened to
  hold 6,500: "**Scene** shows the look of the game and **Off** never shows the effect." is cut (the next sentence says
  what a row does), and the quality rows' links read "list its value for each preset ... explains presets".

## Tutorial run

Run 2026-11-18 on the pin's Release build (work folders `docs-work/tutorial-runs/make-look-1` and `-2`); both files
pass in two rounds.

- The tutorial file was thinner than the page and now does and checks what the page's steps do: the starting values of
  stage 1 (Exposure 0, Auto Exposure and Bloom on, Bloom Intensity 0.04) and the `component.get` of the Camera; the
  Luminance view and its return to None (stages 2 and 9); White Balance 4500 (stage 4); the lookup's import checked
  with `asset.info` (import setting `Size` `33`, the importer's default stored size; the file itself was then a 17-point
  table) and its intensity at 0, 0.5 and 1; `play.start` and `play.stop` around the shutter angles (stage 7, Motion Blur
  still on at 180 after the stop); the Clear Color and Aperture 2, 8 and 2.8 (stage 8); the moonlight's intensities.
- The page's command tabs now say what the file does: the view back to None before Exposure, the `asset.info` check,
  the lookup intensity from 0, and the Luminance view before None in the night's step 3. Two sentences were cut to stay
  within size L ("A slower card takes longer.", "Two rules matter.").
- Exercise 3 failed at first: a fresh editor opens the sample's start scene (MainMenu), so it found no `Height Fog`;
  the file now opens `Scenes/Course.stscene` first (the reader's Course is still open).

## Engine

Nothing found: every command did what its description says.

## Walk G-final-9

Checked 2026-11-24 with the v0.8.0 package (GPU captures in `docs-work/walkfix-G9`, `results.json`).

- `warm-look.cube` was in no download: a tutorial that starts from a sample publishes no zip, and a stage's setup file
  is no download. The page now prints the table (`LUT_3D_SIZE 2`, eight colors) and the tutorial folder holds the same
  nine lines. The old 17-point table was red 0.01 + 1.06 r clamped at 1, green 0.005 + 0.995 g, blue 0.88 b; the
  2-point table gives the same map, red above 1 at full, which the tone pass clamps
  (`Strata/shaders/PostProcess/Tonemap.frag.slang:269`). Scene-camera takes of the Course with both: largest difference
  2 levels at intensity 1 (mean 0.19), 3 at 0.5 (mean 0.09), so the published pictures stand.
- The Luminance view's bands start at EV100 5 (`LuminanceFirstEV100`, `Strata/src/Strata/Renderer/SceneRenderer.h:382`)
  and the Course's sun gives 3.26 lux on flat ground (`sunIlluminance`): `surfaceEv100` p50 1.9 (editor camera) and 2.3
  (scene camera), so the whole view is the lowest band. At night (the recipe) p50 0.83. Steps 1 of "Set the exposure"
  and 3 of the night say so.
- Night recipe: the editor camera's picture is nearly black (mean 5, 7, 7), the scene camera's a dark teal course under
  a black sky (mean 8, 49, 48); with `camera.focus` on `Lantern A` the lantern's head glows white. Step 2's "You should
  see" says where a lantern shows.
