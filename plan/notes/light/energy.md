# Notes: light/energy

## New terms

None proposed; the four homed terms (BRDF table, directional albedo, energy compensation, white furnace test) are defined in bold.

## Since

0.7.0: the page's subject is the compensation and its furnace tests. `GetSpecularEnergy` first appears in commit 586cd4e4 (2026-10-27, "Compensate specular light for multiple scattering"), whose first tag is v0.7.0; the test's comment says 0.6.0 kept 0.31. The BRDF table itself dates from 320fffe1, before v0.3.0.

## Requests

- Words for tools/data/extra-words.txt: "bidirectional" (the expansion of BRDF, first plain use) and "refraction" (the expansion of IOR).
- Figure `furnace-pair` (compare, variants off and on of the compensation, look-dev Furnace scene, Tonemapper None): done; the variants set the recipe field `renderer` (`SpecularEnergyCompensation`), which the tool now passes to the figure's own captures.
- The chart of E and of 1 / E asked for by the brief is replaced by the toy's output of nine points; a plotted chart is not requested.

## Not verified

- v0.8.0 (pin move): the quote of the surface setup is now `Forward.frag.slang` L281-L296; its calls go through `GetFrameSpecularEnergy` (1 when a capture turns the compensation off), and the page says so after the callouts.

- The claims about Kulla and Conty (two tables, second lobe), Fdez-Aguera (closed form for image light) and Filament (the factor) rest on the cited papers, not on the pin.
- The look-dev furnace's sky: LookDevScene.json sets a procedural sky of 0.5 gray at intensity 1; the page says only "uniform sky" for the shot and 1 for the tests.

## Findings not applied

- The brief lists no open findings.
- Figure render-direct:486 (plot of E and 1/E): replaced by a table-like output, see Requests.

## Figures

- `furnace-pair`, v0.8.0 (319075e3), round 1: not published, blocked by the book's tool, not by the pin or the recipe. `check` passes; the take completed, but the two variants' shots are byte-identical and both results echo `renderer: {}`: `capture_parameters` in tools/figures.py sends no `renderer` field to the figure's own capture, and a `viewport.capture` setup step takes a separate picture that is thrown away (the same gap as image/encoding's `banding-pair`). Needed: a recipe field `renderer` (variant-settable) passed to the capture; then the variants become `{"renderer": {"SpecularEnergyCompensation": false|true}}`.
  - The recipe itself is right. In the same hold, the setup steps were given a path for that round only (manifest restored afterwards) so their thrown-away pictures were kept: with the switch off, the lower row (the metals) darkens from left to right, center codes 183, 182, 177, 148, 107 against a sky of 188, the right sphere plainly dark; with it on they read 183, 183, 183, 181, 180, all close to the sky. The upper row (the non-metals) reads 139 to 140 in both. The scene camera frames both rows at a good size; the `metals` crop [0.12, 0.36, 0.88, 0.57] holds the whole lower row. The caption and alt are true of these pictures (alt: the spheres are gray in a light gray sky; the upper row of non-metals is in the picture too and does not change).
  - Round 2 (final pin v0.8.0, 319075e3): the tool passes `renderer`; the variants now set `{"renderer": {"SpecularEnergyCompensation": false|true}}` instead of the setup steps. Taken and published: the results echo each switch, the shots differ. Off: the lower row (metals) darkens from left to right, the right sphere plainly dark; on: all five metals the same light gray near the sky. The upper row (non-metals) is the same in both. Caption and alt now name both rows and the roughness order (left smooth, right rough) and say the non-metals do not change; the caption carries no numbers (figures lint). The page's words were unchanged.
  - Round 3 (v0.8.0, 319075e3), after a viewer's report: the scene camera (fov 45 at 7 m) left the rows in the upper middle of a 1920 x 1080 frame, the lower 45 percent empty sky, and stretched the outer spheres into tilted ovals. The recipe now has its own camera, position [0, 1.1, 11.86], target [0, 1.1, 0], fov 16, at 1920 x 800: the two rows fill the frame from about y 0.17 to 0.83, and the spheres are round. The `metals` crop moved to [0.04, 0.5, 0.96, 0.86] with it. The pictures show the same thing as round 2 (off: the metals darken to the right; on: they match, close to the sky; non-metals unchanged). The caption and alt now say that with the compensation on the lower row almost vanishes into the sky, as a metal that keeps its light should.

## Clerk

- Admitted to extra-words.txt: bidirectional, refraction.
