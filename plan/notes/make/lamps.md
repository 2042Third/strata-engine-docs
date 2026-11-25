# Notes: make/lamps

## New terms

None proposed. The brief homes no term on this page; every term it uses (lux, candela, lumen, nits, exposure, prefab, input action) is homed elsewhere and appears unbold.

## Since

- since 0.3.0: point and spot lights, their Range and cone angles exist from the first tag (render-direct inventory lines 76-79, 0.3.0). Shadows of lamps are 0.6.0, Source Radius and rect lights 0.8.0 (the page teaches all together, so it takes the oldest).

## Requests

- Layout: `layouts/make-lamps.ini` for the editor figure `point-light-inspector` (Inspector panel, window 1280 x 800). It has no `waitsFor`: the pin has `editor.screenshot`.
- Figures (not yet taken): nine entries in `src/content/figures/make/lamps.json`: eight scene figures (`result` and one per checkpoint) and one editor figure. Each scene figure rebuilds the yard with `entity.create` steps in its `setup` (a figure cannot start from the tutorial's state), generated from one definition by a script. The lanterns are plain entities there, not prefab instances.
- Tutorial `tutorials/make/lamps.tutorial.json` starts from the template `basic3d`. Its stage 1 builds the yard with commands, saves it with `scene.saveAs` as `Scenes/Yard.stscene`, then sets the moon. The page tells readers to download the "start checkpoint": the integrator should offer the state after the yard build (before the moon commands) as that start, or split stage 1. Stages 2 to 8 follow the sections.
- Stage 7 copies `tutorials/make/lamps/LanternSwitch.cpp` to `Scripts/LanternSwitch.cpp` after `script.create`. The `script.setField` value for the entity field `Lamp` is written as a `$ref` to the arm's light: the value form of an entity field was not verified.
- Exercise 2: `tutorials/make/lamps/exercise-2.tutorial.json`, starting from this page's tutorial.
- Words and names: `acne` is written as code in the page (the pin's tooltip word; the word lists lack it): please add it to `tools/data/extra-words.txt` or the glossary. The `names` check reports seven bold labels in steps that the dumps lack: `Emissive Color` and `Emissive Intensity` (material editor labels, Strata/src/Strata/Renderer/Material.cpp:33-36) and `Roughness` (Material.cpp:32). They are real labels of the material editor; left in place as the card allows.
- Link hosts: none.

## Findings not applied

- critic-make-b2-12: names `make/reflections`; its fix belongs to that page. This page already teaches the 0.2 lux moon and candela for lamps, as that finding expects.
- critic-make-b2-21: applied (the two biases and what they fight: acne, and shadows detached from their casters; from the pin's tooltips, RendererComponents.cpp:103-107).
- critic-make-b2-22: applied (point light defaults 10 cd and 10 m, spot light 20 cd and 15 m, cone angles 20 and 30 as half angles, so 60 degrees wide).
- Brief: "the viewport's Stats overlay shows the shadow draw calls rise while a lamp moves" does not hold at the pin. The overlay's `shadow` draw calls count the sun's cascades (`ShadowDrawCalls`, SceneRenderer.h:571). The lamp counts are on its shadowed lights line (`N of M shadowed lights ...; V views drawn, W waiting`, ViewportToolbar.cpp:118-130). The page reads `views drawn`.
- Brief: "16 in view, 4 at the Low preset" is the 0.7.0 state. The pin has 4, 16, 64 and 256 (RendererQuality.cpp:45). The page says only that the lowest preset allows four and the others more, with a link to `make/quality`, and names no number beside a preset.
- Brief: the redraw budget of the local-lights stream (12, 24, 48 views a frame) and the 8-frame fade-in are not on the page. It keeps to "a still lamp draws nothing, a moving one draws its views again each frame" and a fade of a fifth of a second (Manual, Lighting.md, Shadows).
- Brief: the figures `render-direct:536-537` (radius sweep, spot cone on a wall) and `:553` (filter radius 0 against 8) are not requested; the page asks for checkpoint pictures only.
- Brief: the exercise is done in the editor with a worked solution file; the page's answer gives the exposure arithmetic.

## Not verified

- That the housing's solid cylinder (the light 0.04 m above its top) blacks out the yard with Cast Shadows on, and that clearing it brings the pools back (derived from the local shadow pass drawing with no culling, SceneRendererLocalShadows.cpp:1476, and from the Manual's advice).
- The submenu path **Create Child ▸ Mesh only ▸ Cylinder** (a **Create Child** menu exists, SceneHierarchyPanel.cpp:931; its contents were not read).
- That the Stats line reads `4 of 4 shadowed lights` with the four lanterns in view, and that `views drawn` is 0 for a still lamp and six or more for the swinging one.
- That the pool is white at Exposure +4 and bright but not white at +1, and where the glint appears (arithmetic from the page's own numbers, not looked at).
- That raising Auto Exposure Min EV toward 0 darkens the yard (the night yard's average brightness was not measured; the command example uses 0).
- That the engine bounds a lamp's cost by its Range, as the page says (render-direct inventory: "also its culling bound").
- The value form of an entity field for `script.setField`, and the key `scene` of `scene.open`.
- That the field of the example script `Spinner` shows as `Degrees Per Second` in the Inspector (the script itself is written for every new project, EditorContext.cpp:262).
- That `input.key` presses reach a paused game that is then stepped.

## Movable claims

- Four lamps are the lowest preset's limit of shadowed point and spot lights (RendererQuality.cpp:45); the higher presets allow 16, 64 and 256 at the pin.
- A point light draws 6 shadow views, a spot light 1, a rect light 6 (5 for a one-sided panel); at most four rect lights cast shadows at once (Docs/Releases/0.8.0.md, Known issues, Rect lights).
- A fade of a fifth of a second for a lamp's shadow in and out (Manual).
- Defaults: point light 10 cd, 10 m, Source Radius 0, Shadow Filter Radius 1.5, biases 1 and 1.5; spot light 20 cd, 15 m, 20 and 30 degrees; rect light 25 nits, 1 by 0.5 m, one-sided; Shadow Filter Radius at most 8; Source Radius at most 2 m.
- A scene with any rect light draws every surface with costlier shaders (the release's Known issues give 2.7 % of the opaque pass in the showcase at Medium; the page gives no number).
- Make Area Light fails while playing and adds a child light with shadows on by default.
- Global Illumination of the Post Process is off by default.
- The Stats overlay's shadowed lights line and its wording; a Stats chip in the Scene view and one in the Game view.
- No light cookies, IES profiles, light linking or lighting channels (checked with git grep at the pin).

## Names of this page

- `Emissive Color`: the material editor's label of `EmissiveColor` (`Strata/src/Strata/Renderer/Material.cpp:33`), a display name the property registry derives from the property's name; no dump holds the material's properties.
- `Emissive Intensity`: the material editor's label of `EmissiveIntensity` (`Strata/src/Strata/Renderer/Material.cpp:36`), derived the same way.
- `Roughness`: the material editor's label of `Roughness` (`Strata/src/Strata/Renderer/Material.cpp:32`), derived the same way.

## Figures

None taken. The captions and alts describe the expected pictures from the yard's numbers; the integrator checks them after taking.

## Figures

Photographed at the pin 319075e3 (release 0.8.0); all nine published, none taken before.

- All scene figures: the figures of a page share one project, so `material.create` of `Materials/Bulb.stmat` failed from the second figure on, and the wet ground of `result` (Roughness 0.1) leaked into the figures after it. Each figure now makes its own `Materials/Bulb-<id>.stmat` and sets the ground's roughness itself (the template's 0.9, or 0.1 where the ground is wet).
- `night-yard`: the recipe had Exposure 1, the page sets +4 before this picture; now 4. At +4 the moonlit yard looks like a dull day under a blue sky (physically right: the exposure gives back the stops the moon lost). Caption and alt say so. The page's "You should see: a dim yard under a dark sky" (section "Make the yard dark", step 3) does not hold: the sky is blue and the yard plain gray.
- `point-light-inspector`: the figure follows step 1, which makes the lamp with the default point light; the recipe now does the same (10 cd, 10 m) instead of 64 cd and 8 m, and alt and shows name the defaults. It uses `layouts/make-lighting.ini` (1280 x 800, a 380 px Inspector) instead of the requested `layouts/make-lamps.ini`, which was never made.
- `wet-glint`: from the page's camera (3 m high) the glints of the front lanterns fall below the frame and those of the back ones lie beyond the lamps' 8 m range (one faint glint, one hidden by the sign post). Round 2 (camera 2.2 m high, farther back) showed two dim streaks at the range's end. Round 3, from 6 m high looking down, shows a soft glint for each of the four lanterns; the glint is wider than the bulb (roughness 0.1), so the caption no longer says "the size of its bulb".
- `moving-lamp`: the arm turned by 110 degrees carries its lantern away from the camera, behind the post, not toward it; alt corrected.
- `result`, `one-lamp`, `sign-spot`, `four-lanterns`, `lantern-shadows`: one take each; the pictures show what captions and alts say (alts of `result` and `sign-spot` reworded to what is seen: shiny ground mirroring the hut's lit floor, the spot's patch spreading onto the ground and the hut).

Mended after a viewer's review (take 5, all scene figures in one hold):

- `sign-spot`: the figure follows step 3, which narrows the cone; the recipe now sets 8 and 12 degrees (was 14 and 22) and keeps stage 2's `Lamp` and `Bulb`. The picture shows a round patch on the board, white in the middle with a soft rim, and a faint glow on the ground under it.
- `result`, `four-lanterns`, `lantern-shadows`, `wet-glint`, `moving-lamp`: the reader's yard keeps the Sign Spot from stage 3 on, so each recipe now has it at 60 cd, 8 and 12 degrees (`result` had 14 and 22). Alts name the patch.
- `lantern-shadows`: the dark disc about 1.4 m wide at the foot of each post under a lantern is the post's own shadow: the post's top (radius 0.07 m) stands 0.34 m under the light, so it shades a disc of radius 0.07 x 3.34 / 0.34 = 0.69 m. The caption says so.
- `moving-lamp`: the caption now says where to look (the lantern behind the post, the post's shadow falling to the right).
- `night-yard`: the picture is right for the page's values (Exposure +4 gives back the stops the moon lacks: blue sky, gray ground, sharp shadows), and the caption now says the yard looks like a dull day, not a dark night. The page's words are still wrong: step 3 of "Make the yard dark" should read "a yard that looks like a dull day: blue sky, gray ground, sharp moon shadows", and its failure "the picture is white".
- `wet-glint`: at the page's Roughness 0.1 each glint is about 0.5 m wide, many times the 4 cm bulb; a lower roughness would contradict step 1. The caption now says the roughness spreads the glint. The page's first paragraph of "Size the bulb for its glint" is wrong for this ground: it should say the ground's roughness spreads the glint well beyond the bulb and Source Radius only adds to it, and step 2's "at 0.04 a small soft disc" should not promise a disc the size of the bulb.

## Tutorial run

Run at the pin 319075e3 (pin build, six rounds) and with the v0.8.0 package (one round); both files pass.

- Stage 4: the check counted 5 point lights; the yard has four lanterns, so 4.
- Stage 4: an instance made with `prefab.instantiate` under `Arm` is named `Lantern`, like the first lantern (names are unique among siblings only), so `entityName "Lantern"` matched two. The file renames it `Lantern (3)`, the name the editor's way (drop at the root, then drag onto `Arm`) gives it; the page's command tab of step 5 says the same.
- Stages 5 and 6 found `/entities/0` of the name `Light` and `Housing`, which in hierarchy order is the arm's lantern, not the first one the page names; they now find the first lantern's light and housing by a box around (-4, 3.34, 1). Stage 5 checks that the arm's light took `CastShadows` from the apply.
- The reader's copies of stages 2 to 8 opened `Scenes/Main.stscene`, the project's start scene, not the yard (stage 4's failed). Stage 1 now sets the yard as start scene (`project.setStartScene`), and "What you need" says so.
- Stage 3 created the spot light with the values of step 2; it now creates it with defaults and sets 60 cd, 14 and 22 as the page's step 2 does.
- Stage 7 copied `LanternSwitch.cpp` before `script.create`, which then refused the class; the file is now copied on `script.build`. Added: the build succeeds without diagnostics, and the arm's light reads 0 cd after the first L and 64 after the second (input reaches the paused, stepped game).
- Stage 2 checks the new point light's defaults, 10 cd and 10 m.

## Walk G-final-9

Checked 2026-11-24 with the v0.8.0 package, GPU captures in `docs-work/walkfix-G9` (`results.json`; the project of
Checkpoint 8's zip).

- The capture's `renderStats` carries the Stats line's numbers: `localShadowLights`, `localShadowRequested`,
  `localShadowViewsDrawn`, `localShadowViewsPending`; `viewport.setSettings` answers the settings only. The two Stats
  tabs now add a `viewport.capture`.
- `entity.setParent` keeps the world placement by default (`keepWorldTransform`), so `Lamp` and `Bulb`, standing at
  the root's place, read Translation 0, 0, 0 after the move; the step no longer asks to type it, and stage 4 checks it.
- Exercise 2 on Checkpoint 8 with the exposure at -2 by hand: with `Ceiling Panel` active the hut is a bright room
  (mean 196, 191, 184); with it inactive, a dark hut lit by the doorway lamp and the candle (mean 68, 62, 52),
  `surfaceEv100` p50 0.6, nearly all of it in the Luminance view's lowest band (from EV100 5). The exercise file and
  the answer deactivate the panel first.
