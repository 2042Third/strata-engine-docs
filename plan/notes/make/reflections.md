# make/reflections notes

## Since

0.6.0: reflection probes, `lighting.bakeProbes` and screen-space reflections landed in 0.6.0 (inventory render-indirect rows 118-149, Docs/Manual/Lighting.md); ambient occlusion is older (0.3.0).

## New terms

- bake: to render a picture once, in the editor, and store it as a file; this page is the home (glossary id `bake`).
- reflection probe: an entity holding a picture of the scene around it that lights and reflects for the surfaces inside its box; this page is the home (glossary id `reflection-probe`).

## Requests

- None. No word or host was needed.

## Not verified

- The exact Inspector labels of the ambient occlusion and reflection fields (the page uses the Manual's names, e.g. "Ambient Occlusion Radius"; the inspector groups them under "Ambient occlusion" and "Reflections").
- The material editor's labels (page writes `Roughness` and `IOR` as code in the steps).
- What each picture looks like (the AO bands, the sky light inside the roofed room, the seam of two probes, the crescent): taken from the engine's code and Manual, never rendered.
- That the sky's light reaches the roofed room unoccluded (reasoned from the renderer: no visibility term besides AO and probes).
- The starting project's download: the page says "offered as a download beside it"; tutorials/make/reflections.tutorial.json builds it (stage 1, endState) from the Basic 3D template. The tutorial and exercise were checked offline only, never run.
- The `camera.set` call in step 16 sets only a position; its effect on the view direction was not checked.
- The sizes of the courtyard's cubes assume the built-in sphere is 1 m across (Builtin/Sphere).

## Findings not applied

- critic-make-b2-1 (Starting state): applied as the page's own starting project (tutorial file), no change to make/commands.
- critic-make-b2-23 (C++ pages): not applied as Assumes rows (the brief's table is the planner's); the page carries one question linking basics/programming-3 and basics/cpp-classes before the first excerpt, and notes `std::clamp`, `static_cast` only inside the quoted code.
- Sections of the brief not carried as steps: "Variations" lists the open yard, the cave, a probe per house; "what Strata does not do" (no probe gizmo) is in one sentence, the cube-map point (new:12) is not on the page (it would need a paragraph with no use for a game maker).

## Figures

Photographed 2026-11-18 at the pin in three takes (two failed on setup steps); all six pictures published.

- All three: round 1 failed from the second variant on, because the variants share one project copy and a second
  `material.create` of `Materials/Plaster.stmat` is refused. Each variant now builds the courtyard itself, with
  materials under `Materials/<figure>-<variant>/`.
- `result`: the recipe's camera (6.5 m outside) showed the front wall with a small dark doorway; with the template's
  sun (azimuth 20) no sunlight entered the room, so noon and dusk differed only in tint and no long shadow was visible.
  Now the camera stands in the doorway (0, 1.5, 2.6, fov 70) and both presets take `sunAzimuth` 70, the sun behind
  the camera: a short sun patch inside the door at noon, a long band across the floor and a door-shaped warm patch on
  the back wall at dusk. Caption and alt say so. The page never says where the sun stands; step 19's "long shadows"
  are what the dusk picture shows inside the room as the long band of light.
- `ao-views`: same doorway camera. The AO view shows the bands in every corner, around the soil bed's foot and under
  the sphere; in the lit view the darkening is slight (the floor is dark and only the sky's light is darkened), and the
  caption says so. The page places no `::figure{id=ao-views}`: steps 3 to 5 could carry it.
- `wet-floor`: the recipe's camera (-3, 1, 5.5) looked at the sphere through the closed front wall, and its
  `material.set` on `Materials/Ground.stmat` would have saved the wet floor into the copy the other figures share. Now a
  `Wet` material (Ground's color, Roughness 0.04, IOR 1.33) is put on `Ground` per variant, seen low from the doorway
  (0.3, 0.8, 2.6, fov 50). Off: the floor mirrors the blue sky, sharply rather than blurred; on: the sphere and the
  soil bed appear mirrored and the floor turns gray near the back wall. SSR also leaves a dotted noise on the sphere's
  lower half. The page places no `::figure{id=wet-floor}`: the wet-floor steps could carry it.

Mended 2026-11-18 after a viewer's report (three takes and two retakes alone):

- `result` (NOT published, recipe left as it was): the mended recipe adds the `Wet` material on `Ground`, Screen Space
  Reflections on, and the room and yard probes (the room's Priority 1 and Blend Distance 0.3, the yard's Blend
  Distance 0.5, boxes grown as below) baked four times after each preset, so noon and dusk each have their own set.
  Its pictures pass the eye: the sphere mirrors the room and the doorway instead of the sky, the floor mirrors the
  soil bed, the room turns neutral at noon and warm at dusk. But the dusk variant's two captures differed in all
  three takes: by 1 in about 1,300 pixels with TAA (twice), by up to 19 in 1,342 pixels with FXAA (the per-frame noise
  of SSR and AO no longer averaged). Noon passed every time. The pin cannot give the dusk pair byte-identical; the
  recipe (TAA) and the pairs are in `docs-work/photo/make-reflections/retake/` (`mended-recipes.json`,
  `result/nondeterministic/`). For the planner: a byte tolerance in `take`, or a retake later.
- `wet-floor` has the same baked probes in both variants: off, the floor mirrors the probe's smeared room (no sky);
  on, sharp upside-down copies of the sphere and the soil bed. With the probe the sphere's lower half reflects the
  room, so the SSR grain the viewer saw there is faint; a slight dotted grain stays in the darkest part of the
  mirrored sphere (named in the alt). The capture already waits for 8 TAA frames, and High quality needs no history,
  so more frames would not remove it.
- `ao-views` (NOT published, recipe left as it was): the mended recipe is the AO view, then the lit room with
  `AmbientOcclusion` off and on (the corners darken slightly and a soft patch lies under the sphere), with the camera
  looking lower (target 0, 0.3, -2) so the sphere's foot is in the frame. The AO view and AO off passed; the lit AO-on
  variant's two captures differed by 1 in 510 to 520 pixels in four takes running, with TAA and with FXAA, so it is
  systematic. Pairs in `docs-work/photo/make-reflections/retake/ao-views/nondeterministic/`.
- **Page fault, for the writer:** a probe's weight is 0 at its box's faces and reaches 1 only Blend Distance inside
  (`GetProbeWeight`, `Strata/shaders/Include/ReflectionProbes.slang` lines 60 to 70). The page's fitted box (center
  0, 1.5, 0, Extents 3, 1.5, 2) puts the floor, the walls and the ceiling exactly on its faces, so they keep the sky's
  light and reflect the sky: the first take with those numbers showed the wet floor mirroring the blue sky. The recipes
  grow the boxes by about the blend distance (room Extents 3.3, 1.8, 2.3; yard 4, 1.8, 2.5). Step 7's numbers and
  "half of each" should say the box must reach past the surfaces by the Blend Distance (step 6's default 1 needs
  even more), else step 13's "the floor reflects the probe's picture" is false.
- **Page fault, for the writer:** the page still places no `::figure{id=ao-views}` (after step 3's "You should see")
  or `::figure{id=wet-floor}` (after step 14's); the photographer may not edit the page. (Since placed: step 3 and
  step 14 now carry them.)

Retaken 2026-11-23 at the pin v0.8.0 (319075e3), two holds of the lock, all six pictures published or kept:

- `result`: the mended recipe of 2026-11-18 (wet floor, SSR, room and yard probes baked four times per preset) is now
  the manifest's. At v0.8.0 both pairs pass (dusk off by 1 in 0.14 % of pixels, inside the tolerance), so the
  nondeterminism that kept it out is gone. Seen: noon neutral gray with the short sun patch inside the door, dusk warm
  with the long band and the door patch and sphere shadow on the back wall; the sphere mirrors the room and the
  doorway, the floor mirrors the soil bed. Caption and alt as mended, split into shorter sentences for the lint.
- `ao-views`: round 1 (recipe unchanged) was byte-identical to the published pair, but the sphere's foot lay below the
  frame, so "under the sphere" (caption, alt, step 3's "You should see") was not visible. Round 2 lowers the target to
  (0, 0.3, -2): the AO view shows a banded gray crescent under the sphere, the lit view a soft dark patch there; the
  lit sphere mirrors the sky (no probes yet at step 3), which the alt now says. The page keeps two variants (ao, lit),
  so the mended AO off/on triple was not used.
- `wet-floor`: byte-identical to the published pair at the new pin; published files and stamps unchanged.

Mended 2026-11-23 after a second viewer's report (three rounds of `ao-views` alone, one hold each):

- `ao-views`: the viewer found the sphere's foot on the bottom edge and the AO crescent cut by the frame (the
  2026-11-18 framing, target 0, 0.9, -2). The target-0.3 framing published earlier that day left the crescent only
  about 30 px above the bottom edge. Round 1 (0.4, 2.6, 1.85, looking steeply down) hid the contact under the sphere
  itself; round 2 (0.6, 1.8, 1.9 toward -0.8, -0.1, -1.2) cut the soil bed at the right edge. Round 3, published:
  camera inside the doorway at (0.6, 1.8, 1.9), target (-0.5, -0.1, -1.2), fov 70. The crescent lies mid-frame (about
  y 520 to 620 of 720), the vertical back-left corner, the floor corners and the bed's foot are in the frame. The AO
  is weak at the pin: under the sphere the AO view reads 245 against 254 open floor, the lit view 52 against 54, so
  the lit picture shows only a faint shade; caption and alt now say "faint shade" instead of "soft dark patch", and
  the alt names the pale stripe of light from the doorway at the bottom left. Step 3's "You should see" stays true.
- `wet-floor` (unchanged): the viewer found step 14's "the sphere and the walls appear in the floor, upside down and
  sharp" untrue: off and on differ only at the sphere and the soil bed. Confirmed: with the baked room probe the floor
  already mirrors the walls with Screen Space Reflections off (the back-left corner's mirrored edge is in both
  pictures), and plain plaster walls look the same mirrored either way. **Page fault, for the writer:** step 14
  should read "the sphere and the soil bed appear in the floor, upside down and sharp", as the caption says.

## Clerk

- Nothing to admit: bake is already the glossary's, homed here. Refused: reflection probe, which the glossary homes on indirect/probes (only its home words it).

## Tutorial run

Run 2026-11-18 at the pin, two rounds; both files passed as written in round 1, and both were then strengthened with
the page's own values and passed again.

- `reflections.tutorial.json` built the courtyard but left the template's sun at azimuth 20; the page's table puts it
  at 70 degrees from +X toward +Z. It now ends with `lighting.applySkyPreset {"preset": "Clear", "sunAzimuth": 70}`
  (checks `sunDirection` 0.262, 0.643, 0.720) and checks `Ground`'s Roughness 0.9.
- `exercise-1.tutorial.json` checked only the build and the steps. It now checks, after 60 steps from 21:00, the fire
  at 100 cd, the moon at 0.2 lux and the light's rotation (the moon about 45 degrees up on the far side).
- The page has no checkpoint: its file is the starting project only, so steps 1 to 20's command tabs are run by no file.

## Engine

- Nothing found: every command did what its description says.

## Walk G-final-9

2026-11-24: the doorway view and step 16's views got `camera.set` lines with `target` (the doorway one is the result
figure's camera); the Hard exercise's answer says how to use its download (two commands files and
`Scripts/DayNight.cpp`, copied by hand between them). The files are unchanged; both passed again with the pin build and
the v0.8.0 package.
