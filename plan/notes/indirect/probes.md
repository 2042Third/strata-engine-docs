# Notes: indirect/probes

## New terms

None proposed. The three terms the glossary homes here (reflection probe, box projection, probe priority) are defined in bold on the page. "Slot", "capture", "bake" and "influence box" are explained in plain words and not bolded.

## Since

0.6.0: `Docs/Releases/0.6.0.md` lists the Reflection Probe component, the bake and `lighting.bakeProbes` as new in 0.6.0 (the 0.5.0 and 0.4.0 notes name probes only as planned).

## Requests

- Word: "parallax" (the parallax problem, parallax correction). The glossary's name "Box projection (parallax correction)" has it in parentheses, and the lint does not take it as an alias word.
- Links to ../indirect/ibl.md, ../indirect/ssr.md and ../indirect/seam.md point at pages written by other agents.
- Figures: `src/content/figures/indirect/probes.json` holds `probe-on-off`, `box-projection`, `resolution` and `bake-sun-disk`, all of the look-dev project's scene `Scenes/Specular.stscene` (it holds the entities `Probe Yard` and `Probe Patch`). `resolution` waits for `tier 2: renderer switches`; `bake-sun-disk` waits for the 0.7.0 baseline set (`tier 3`). The recipes of `box-projection` and `probe-on-off` are not checked against a take: the camera of `box-projection` is `lookdev.patch`'s, the camera of `probe-on-off` is `lookdev.polished`'s.
- Figures of the brief not drawn: `BlendDistance` 0 against 1 m on two overlapping boxes (`render-indirect:442`), bakes 1, 2 and 8 (`render-indirect:445`) and the Cornell box lit by one baked probe (`new:8`). The first two have no recipe at the pin that I could verify; the Cornell figure needs the id of the reference figure of `indirect/problem`.
- Sketches: `sketches/indirect-probes-toy.cpp` (box projection and blend by hand), `sketches/indirect-probes-slots.cpp` (exercise 2).

## Not verified

- No take of a figure was made or looked at; the captions state what the pictures should show.
- The Alternatives table's "Who uses it" column names kinds of engines, not products, and no source was read for the claims about other engines.
- That `Probe Yard`'s capture is committed in the look-dev scene: the `probe-on-off` recipe turns the probe on and does not bake.

## Findings not applied

- The brief's exercise E5 (a probe-weight debug view) is exercise 3 as a prose solution naming the files to change; no patch under `tutorials/` was written, and the card allows one done exercise, which is exercise 2 (a sketch).
- The brief's stage name `GPU.Reflections` is not a code span on the page: `names` rejects it; the stage is described as "the reflections stage".
- Brief: "a bake renders ... Medium's Checkerboard needs TAA": the page states it as the brief and `Docs/DeveloperGuide.md` do; the code that disables it was not read.
- Brief: "the Scene view draws no box": checked only through the brief's own grep evidence (`SceneGizmos.cpp`), not re-run.

## Figures

Finishing, 2026-11-24, pin v0.8.0 (319075e3), the edition's final pin.

- `bake-sun-disk`: cannot be taken at the pin. Its picture with the disk needs a 0.7.0 bake, and the pin's bake always
  runs in the probe-capture mode (no switch keeps the disk or the highlights); a picture of the pin's bake alone would
  show even wet ground and teach nothing of the fault. The entry keeps its `waitsFor` as the request for a later
  edition and names `standIn: sun-in-bake`.
- `sun-in-bake` (new, diagram): a side view of the old bake. From the probe's center the bake sees the sun's disk and
  the sun's highlight on a polished tank (the sun's ray off the tank's vertical face reaches the probe); the camera's
  ray reflected off the wet ground leaves in the probe-to-highlight direction, so the lookup returns the highlight and
  the ground shows a bright blurred patch. Drawn, rendered in both themes, `drawings.mjs check` passes; one round
  moved it 40 units up (empty band above the sun) and gave the patch a pale fill (it read dark in the light theme).
  The page now places it and introduces it as "how the old bake's highlight came to lie on the wet ground".

Photographer, 2026-11-23 (mending a viewer's report), pin v0.8.0 (319075e3) Release build.

- `probe-on-off`: auto exposure metered the two variants differently (EV100 15.35 off, 14.65 on), so the whole frame
  moved by about 25 levels. The figure now sets `postProcess` `AutoExposure: false`, `Exposure: -14.8` (the probe-off
  multiplier: log2 0.18 minus the metered log2 luminance 12.35). Retaken: outside the panel the two pictures differ by
  at most 2 levels (the ground's faint probe specular); the caption says one fixed exposure is used.
- `box-projection`: words only (the take is unchanged). Caption and alt now name the band of wet ground across the
  middle (the dark lower part is dry ground in shadow) and say that the right block (`Sheet`, metal, roughness 0.18)
  stands inside the probe's box, so its right end turns from brown-grey to light grey and the metal balls change a little.
- `resolution`: the alt named "the left half" of a ball shown whole. A crop cannot reach the page without a
  `::figure{crop=…}` line (page words are not mine to edit), so the camera now frames the ball's left side
  (target -7.384, 0.549, 1.012, fov 5.5, about 2.6 times closer than before): the yellow wall, the white and red posts
  and the two crates fill the picture, soft at 128 and sharp at 256 at page width. Round 1 (fov 5) cut the crates at
  the bottom. Caption and alt rewritten; the teal wall and the sun are out of frame now.

Photographer, 2026-11-23, pin v0.8.0 (319075e3) Release build.

- `probe-on-off`, `box-projection`: retaken at the new pin; `figures.py compare` against the published originals: 0 of
  4 pictures differ. Looked at again: the captions still match. Publish left the files unchanged.
- `resolution`: published. The pin now has the custom quality the recipe needs, so `waitsFor` is gone; the variants
  set `ReflectionProbeResolution` to 128 and 256 through a custom `Renderer.Quality` (other fields at High), turn
  screen-space reflections off and make `Probe Yard` active. The look-dev scene has no mirror ball in a room, so the
  recipe uses `Ladder 0` (metal, roughness 0) in the yard. Round 1: the whole ball at fov 28; the difference showed
  only when enlarged. Round 2: camera aimed at the ball's left half, fov 14; at page width the reflected yellow wall,
  posts and crates are soft at 128 and sharp at 256. Caption, alt and shows rewritten to say so ("a room" was wrong).
- `bake-sun-disk`: still waits (tier 3), not taken.

Photographer, 2026-11-18, pin Release build, look-dev `Scenes/Specular.stscene`.

- `box-projection`: published. Round 1: the `entity.setActive` steps carried `entityName` inside `parameters`
  (the command refused it); moved to the step level. Round 2: with screen-space reflections on, the wet ground's
  reflections of everything on screen came from SSR and both variants looked alike, so both variants now start by
  turning `ScreenSpaceReflections` off on `Post Process`. Now box off: the reflected tanks and blocks lie well left of
  the objects and the yellow West Block has no reflection; box on: the yellow wall, the tanks and the blocks are
  reflected below themselves (close, not exact: the objects stand inside the box, not on its faces). Caption, alt
  and shows rewritten to say so and to say that SSR is off. The page's sentence ("Without the correction the
  reflected objects sit in the wrong places") stays true.
- `probe-on-off`: published 2026-11-18 under R57 (a pair within 1 level in at most 0.5 per cent of the pixels is one
  picture): retaken, `probe-off`'s captures are byte-identical and `probe-on`'s differ in 210 pixels (0.023 per cent) by
  1 level; looked at side by side, the panel shows sky over plain brown ground, then the dark red-brown back wall and
  the grey ground with a shadow. Earlier: waits, not published. Round 1: same `entityName` fault. Round 2: fov 60 to 40 so the polished
  panel fills most of the frame (the tanks at the edges are outside the probe's box and do not change). The picture
  is right: probe off, the panel shows only sky over a plain brown ground; probe on, it shows the brick Back Wall and
  the yard's grey ground with a shadow. But `probe-on` is nondeterministic in every take: three takes (TAA, TAA
  alone, `antiAliasing: off`) gave two captures that differ in 250, 250 and 210 pixels by at most 2, 2 and 1 levels,
  spread over the whole frame (72 to 102 of them inside the panel). The pair is in
  `docs-work/photo/indirect-probes/nondeterministic/indirect.probes.probe-on-off.probe-on/`; `probe-off` is stable.
  For the planner: with `Probe Yard` active (the recipe does not bake; it uses the capture the look-dev script
  baked), two captures of one editor are not bit-identical. The recipe, captions and camera are ready; publish once the pin is deterministic or the take tolerates a
  1-level difference. Nearest honest picture meanwhile: none needed (the captions match the takes).

## Clerk

- Admitted to extra-words.txt: parallax (school physics).
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.
