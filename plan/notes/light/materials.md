# Notes: light/materials

## New terms

- dielectric: a material that does not conduct electricity (wood, plastic, stone, skin, paint, glass), which scatters most light inside it as diffuse color and mirrors a small share; home this page; aliases: dielectrics.
- specular power: the exponent of Phong's model that sharpens a highlight as it grows; home this page; aliases: shininess.

## Since

0.3.0: the metallic-roughness `MaterialProperties` is the first-tag material model (inventory render-direct:35, "0.3.0"). Emission in nits and the coat and glass fields came later (0.6.0); evidence not checked against the first tag.

## Requests

- Words for `tools/data/extra-words.txt`: dielectric (if not admitted as a term), toon, cel, sheen, anisotropy, iridescence, subsurface, specular (check), diffuse (check).
- Names for `tools/data/names.txt`: Phong, Blinn, Disney, Burley, Karis.
- Figure `furnace-sweep` (kind scene, project lookdev, scene `Scenes/Furnace.stscene`, shot `lookdev.furnace`, crops `metals` and `dielectrics` copied from `Tools/LookDev/Shots.json`): the page names the bottom row metal (base color 0.95, Metallic 1) and the top row dielectric (0.5, Metallic 0), from `Tools/LookDev/LookDevScene.json` at the pin; the picture itself is not taken.
- Figure `normal-map-compare` (variants `map-off`, `map-on`, Showcase sample): the material path `Assets/Generated/Props/WeatheredSteel.stmat` and a camera on a surface that uses `WeatheredSteel_nor_gl.png` are guesses (no `.stmat` of that name was found at the pin); the planner must choose the shot. The page asks for no separate crop picture.
- Hosts: none linked; Further reading cites Burley 2012, Karis 2013, the glTF 2.0 specification and Phong 1975 without links (hosts of the Khronos registry and the SIGGRAPH course notes would be needed to link them).
- Exercises 1 and 2 are answered with command JSON, with no `tutorials/light/materials/exercise-<n>.tutorial.json`: the brief names them "predict, then run" and I judged the page past `basics/programming-1`; the planner may ask for the tutorial files.
- Links to pages not yet written (`light/reflectance`, `light/material-data`, `light/clearcoat-transmission`, `light/lights`, `light/measuring-light`, `light/units-exposure`, `appendix/not-in-strata`) follow the brief's names.

## Not verified

- The importer's treatment of the tangents (the page only links `assets/models-gltf`).
- That the `lookdev.furnace` render shows near-uniform spheres: the example states the expectation from the formulas (0.95 L for the metal row, about 0.52 L for the dielectric row), not from a captured image.
- The general-knowledge claims: Phong 1975, Burley 2012, Karis 2013, glTF 2.0 in 2017, the fixed-function use of Blinn-Phong, "older glTF files" using specular-glossiness; the table's "Used by" column for these is not an engine fact.
- Plausible albedo range: only the engine's limits (0.03 and 0.85, `Strata/src/Strata/Renderer/SceneRenderData.h`) are stated; the sRGB bytes 48 and 237 are computed by hand.
- That Blend sorting "can sort wrongly" in Strata (general to sorted blending; the engine's sort was read only as "back to front" in `Material.h`).
- A dielectric's 4 % mirror and a metal's behaviour are the model's statements (`Forward.frag.slang` f0 line), not measurements.

## Findings not applied

None: the brief lists no open findings.

## Clerk

- Admitted terms homed here: dielectric (its plural follows), specular power (alias shininess).
- Admitted to names.txt: Phong, Blinn, Blinn-Phong, Disney, Burley.
- Admitted to extra-words.txt: toon, cel, subsurface; sheen, anisotropy, iridescence, specular and diffuse raised no finding and stay out.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

## Figures

- furnace-sweep, round 1 (scene camera, uniform sky only): the spheres showed as flat disks, the metal row nearly
  vanished, and no sphere showed a reflection, so the alt's "sharp reflection" was false. Round 2 frames both rows
  (camera at 0, 1.1, 7) and adds one small directional light (Intensity 1.5) by `setup`: the highlight is a point on
  the smooth spheres and a broad glow on the rough ones. The look-dev scene has no tone mapper, so the smooth spheres'
  highlights clip and the eye cannot judge "how bright each sphere is overall": the caption no longer claims it.
  Crops moved with the new framing.
- normal-map-compare: the recipe named `Assets/Generated/Props/WeatheredSteel.stmat`, which does not exist; the
  material is `Materials/WeatheredSteel.stmat` (handle 7FF4C3E4EB768032) and `check` did not catch it. Round 1 used
  the oil tank's shell (center 2.7, 17.2, radius 4) from 3.5 m at fov 40: the difference was too small at page width.
  Round 2 narrows to fov 22 on the edge of the low sun's reflection, where the map breaks the reflection into waves
  and dents. The texts now say a steel tank at golden hour, not "a surface under one light", and the crop the old
  `shows` named was never in the recipe.
- Viewer's review (retaken at pin 319075e3): furnace-sweep's caption promised a broad glow on all rough spheres, but
  only the metal row (bottom) shows it; the plastic row's highlight spreads too faint to see at roughness 0.75 and 1,
  and the smooth metal mirrors the even gray room and almost vanishes. Caption and alt now say so and name the rows.
  normal-map-compare: no dents show; with the map the streaks of the reflection break into soft gray spots, clearest in the darker
  right half. Caption and alt say that, and the recipe gains the crop `right` ([0.45, 0.05, 0.9, 0.75], scale 2),
  published for both variants. For the page's writer: the two stacked `::figure` lines (around line 193) differ
  subtly; replace them with `::compare{id=normal-map-compare before=map-off after=map-on}` and show the crops with
  `::figure{id=normal-map-compare variant=map-off crop=right}` and `variant=map-on crop=right`, and let the paragraph
  name the right half instead of dents.
