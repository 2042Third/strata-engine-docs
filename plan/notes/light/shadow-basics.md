# Notes: light/shadow-basics

## New terms

- caster: a surface that draws into a shadow map and so can cast a shadow; home this page; aliases: shadow caster, casters.
- receiver: a surface that reads a shadow map to learn whether it is lit; home this page; aliases: receivers.
- light space: the coordinate system of the light's camera, whose view-projection matrix gives a point's place in the shadow map; home this page.
- bias: a move of the depth comparison so that a surface does not shadow itself; home this page (slope bias, depth bias, normal offset and receiver-plane bias are bold on the page as parts of it).

The page also defines in bold slope bias, depth bias, normal offset and receiver-plane bias (the glossary lists them as entries, but the brief's terms table omits them): if the clerk admits them under other ids, the bold stays valid.

## Since

0.3.0: the inventory dates the biases to 0.3.0 (render-direct:122); the receiver plane came in 0.7.0 (same line). Shadow maps are the first-tag method.

## Requests

- Figure `acne-low-sun` (variants `zero`, `defaults`; OpenWorld sample, the `ow.lowsun` camera and Sun rotation from `Tools/LookDev/Shots.json`, crop `near-forest`): the `component.set` names `DirectionalLight` with `ShadowBias` and `ShadowNormalBias` come from `RendererComponents.cpp`. Taken on the look-dev Yard instead (see ## Figures).
- Words for `tools/data/extra-words.txt` if wanted: none left; the page was reworded to the common list.
- Exercise 1 is answered by reasoning and a run in the Scene view, with no `tutorials/light/shadow-basics/exercise-1.tutorial.json`; the planner may ask for one. Exercise 3 is the done exercise (`sketches/light-shadow-basics-sloped-line.cpp`).
- Links to pages not yet written: `light/lights`, `light/sun-shadows-2`, `appendix/not-in-strata`, `light/materials` (written).
- Hosts: none linked.

## Not verified

- General-knowledge claims: Doom 3 using shadow volumes, the three families' "Used by" cells, shadow volumes needing closed meshes, the odd-count rule, Williams 1978, Crow 1977, Reeves 1987 and the GPU Pro 4 chapter in Further reading.
- That the sun's box is fitted to what the player's camera sees "to give every texel the most use" (`ShadowCascades.cpp` fits slices of the view; the page states the purpose, not a checked comment).
- The slope bias is described through the hardware rule (slope scale times the largest depth change per texel); the engine passes `c_ShadowDepthBias = -16` and `c_ShadowSlopeDepthBias = -1.5` to NVRHI, and the 8.5-texel figure of the grazing-sun example applies that rule by hand.
- How the lamps' biases act (the lamps' tiles use texel biases per their tooltips; the receiver plane was found only in the sun's `SampleCascadeShadow`), so the page says nothing about the lamps' shaders beyond their projections and their atlas.
- The sketch is a two-dimensional model with a vertical light; it is not Strata's shader.

## Findings not applied

- The brief lists no open findings.

## Clerk

- Admitted terms homed here: light space, normal offset. Not admitted, left for the planner: receiver, bias, slope bias, depth bias and receiver-plane bias; as terms they put five and eight new terms into two sections (term-section allows 4), and depth bias then needs marks on light/sun-shadows-2. Their bold may stay.
- Refused caster: the glossary homes shadow caster on light/sun-shadows-1 (only its home words it); that this page teaches it first is the planner's.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

## Figures

- `acne-low-sun` (variants `zero`, `defaults`): published at v0.8.0 (pin 319075e3, 2026-11-24) as the honest picture of
  the pin, not as acne: the Yard under a 10-degree sun with both texel biases at 0 and at the defaults, clean lit ground
  in both, only shadow edges differing. The page's words (opening paragraph, the example's closing sentence) and the
  caption already teach that lesson, so they stay; `shows` now names the crop as the lit ground behind the fence, and the
  alt says the two pictures look the same. A picture of real acne still needs an engine switch for the rasterizer's
  slope bias and the receiver-plane bias (a request for a later edition). History of the earlier rounds:
- Mended after a viewer's report (2026-11-24): the old crop `near-ground` (0.25,0.6-0.6,0.95) held mostly fence posts
  and the blue block's shadow. A per-pixel diff of the two variants puts nearly all differences in the fence's shadow
  stripes at lower left (and the blue blocks' shadow edge at right), so the crop is now `fence-shadow` (0,0.75-0.16,1,
  enlarged 2 times): sunlit strips between shadow bars, where acne would show, and the band of the rails' shadow,
  which sits visibly elsewhere with the biases off (several pixels, not one). The caption names that place and that
  shift; the alt names the domes, blue blocks and the fence's and blocks' shadows (no hut shadow is in view).
- Earlier rounds of `acne-low-sun`: the pin cannot show acne through
  `ShadowBias` and `ShadowNormalBias`: the rasterizer's slope bias (`c_ShadowDepthBias`, `c_ShadowSlopeDepthBias`) and
  the sun's receiver-plane bias stay on and keep a grazing sun clean with both properties at 0.
  - Round 1 (OpenWorld, `camera: "scene"`, Sun rotation [-10, 70, 0]): the setup's `entityName` inside `parameters` is
    refused by `component.set`; with the Sun's ID the `zero` take was nondeterministic (the world's cells had not
    streamed in: one capture is sky only, 6 draws), and `defaults` showed a bare mountain from high above, no trees.
  - Round 2 (look-dev `Scenes/Yard.stscene`, its scene camera, Sun [-10, -74.36, 0]): both variants show long fence,
    boulder and hut shadows on clean ground; they differ only by a pixel or two along shadow edges (14,195 channel
    values over 8 of 8.3 M), no stripes anywhere.
  - Round 3 (the same at 3 degrees of elevation): again identical but for shadow edges (3,110 pixels over 8).
  - The manifest now holds the round 2 recipe (Yard, 10 degrees, step-level `entityName`), which takes cleanly.
  - Retake at v0.8.0 (pin 319075e3, 2026-11-23, the round 2 recipe unchanged): complete, and the same result. Both
    variants show the fence's long shadow stripes and clean lit ground near the barrels. They differ only along
    shadow edges (65,428 channel values over 1 of 8.3 M). The pin still hard-codes the rasterizer's slope bias
    (`SceneRenderer.cpp`, `c_ShadowDepthBias = -16`, `c_ShadowSlopeDepthBias = -1.5`) and has no switch for it, so
    the figure stays blocked. Pictures in `docs-work/photo/light-shadow-basics/`.
  - What the page's words would need: either a figure that shows the opposite lesson (with both texel biases at 0 a
    10-degree sun still leaves no acne in Strata, because the slope bias and receiver plane remain), with the opening
    paragraph, "as the figure at the start showed" (Shadow acne section) and the `ow.lowsun` sentence of the example
    reworded; or a diagram from the page's sketch (the stripe count of the zero-bias ramp) instead of an engine picture.
    An engine picture of acne needs an engine switch for the slope and receiver-plane biases, which the pin lacks.
  - Nearest honest picture: the round 2 pair (`docs-work/photo/light-shadow-basics-r2/`), captioned as "the same yard
    under a 10-degree sun with both texel biases at 0 and at the defaults: the ground stays clean in both, and only the
    shadow edges move by a pixel".
