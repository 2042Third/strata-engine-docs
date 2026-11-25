# Notes: image/lens-effects

## New terms

None proposed. The page defines the nine glossary terms of its brief (bloom, firefly, Karis average, tent filter, vignette, field angle, chromatic aberration (lateral), lens flare, soft knee). Ghost, halo and starburst appear in italics inside the lens flare paragraph; the glossary names them as aliases of Lens flare.

## Requests

- Figures (not taken): `bloom-intensity` (Showcase, three variants), `vignette-sweep` (basic3d, three variants), `aberration-corner` (ThirdPerson, a 4 times crop of the corner), `flare-sun` (OpenWorld, the shots `ow.sunward` and `ow.sunward.flare`). No layout is needed.
- Not drawn: the brief's figure of the sun behind a wall, the bloom threshold and radius sweeps at two resolutions, and a flare-geometry diagram; the page carries the ghost positions as a worked example and the order of the passes as a Mermaid diagram.
- No word was proposed for the extra-words list.

## Not verified

- The meaning of "exposed luminance above 4" in `LensFlare.comp.slang` (the shader's comment says "times middle gray's display white"): the page says only "exceeds 4 in exposed luminance".
- The 2014 talk named in Further reading and the cos^4 content of the Physically Based Rendering book's camera chapter: cited from memory, no link.
- The `since` value 0.3.0: the introduction of bloom and the vignette in 0.3.0 was not checked.
- The figure recipes: scenes, sample projects and the `postProcess` variant keys follow other figure files; no view was taken.
- The entity name `Camera` in the exercise's JSON is a placeholder for the entity that holds the component.

## Findings not applied

- The brief lists no open findings.
- Brief items left out: the wall figure and the two-resolution bloom figure (see Requests); the flare sprite, hybrid blur and "Karis" person are not named because the pin does not document them.
- `Docs/Manual/Camera.md` says the starburst has six rays and `LensFlare.comp.slang` has a quarter-resolution flare: both agree with the page. The comment in `SceneRenderer.cpp` that sunUV is for perspective cameras only is not matched by the code (no orthographic test); the page does not claim either.

## Figures

Taken at the pin's Release build, 2026-11-17.

- `bloom-intensity`: published. Round 1 (Showcase, `camera: "scene"`, Golden): a rusty bus and a tank in daylight, no lamp in view; off and 0.2 barely differ. Round 2 (station Dusk, the tone-mapping figure's hut camera): the lantern is a few pixels; the variants differ only there. Round 3 (Dusk, camera 4 m from `LANTERN_A`, fov 35): at 0.2 a glow spreads from the lantern over the beam and into the doorway and the lantern's details soften; the default 0.04 is hardly told from off (doorway pixels 1.9 off, 2.1 default, 2.6 strong of 255; the even wall is unchanged, as the page's lerp predicts). Caption, alt and shows rewritten to say so; the page's "a faint glow shows around them" at the default is generous. A tighter frame (fov about 15 on the lantern) would show the glow larger.
- `vignette-sweep`: published. Round 1 (camera at eye height toward the origin): the basic3d scene is a ground and the sky, no wall; the sky's gradient makes "even" untrue at 0. Round 2: camera 6 m above the ground looking down, fov 60: an even gray-brown field. Measured (display values, center / top-middle / corner): 0 133 / 134 / 134; 0.12 133 / 130 / 126; 1 133 / 93 / 40. The page's factors (0.90 and 0.176 at the corner) are linear light; the picture shows them through the tone curve. Caption, alt and shows say "ground", not "wall".

### Mend, 2026-11-17 (a viewer's faults)

- `bloom-intensity`, wrong words: measured on the published pictures (display values, off to strong): doorway sides 1 to 5, window opening at its edges 1 to 5, beams under the roof 2 to 10, beside the lantern 0 to 17, the lit wall 96 unchanged. At threshold 0 the glow is mostly the lit wall's light spread over every dark neighbor; the lantern's own halo is small. Caption, alt and shows rewritten to say so.
- `bloom-intensity`, unreadable at page width: added the crop `lantern` ([0.4, 0.25, 0.62, 0.6], scale 3) and retook the figure so all three variants have it. The page's three directives name no crop, so the page still shows only the whole frames: the page writer should add `::figure{id=bloom-intensity variant=off crop=lantern}` (and `default`, `strong`) after the whole frames, or replace them.
- `vignette-sweep`, unclear words: measured (center / top / bottom / left / right / corners) at 1: 126 / 88 / 88 / 46 / 48 / 37-38. The side middles (factor 0.24 by the page's formula) are nearly as dark as the corners (0.18); the top and bottom middles (0.56) stay bright. Caption and alt rewritten; no retake.
- `aberration-corner`: blocked. The page's directives name no crop, so the page shows the whole pictures, where a fringe of at most 0.17 pixel (1280 wide) cannot be seen. Round 1 opened the Main Menu scene (corner: plain sky). Round 2 (`Scenes/Course.stscene`, scene camera, 3840 x 2160, fringe 0.5 pixel by the page's own numbers): the right edge's fence posts enlarged four times show no fringe the eye can find, off against on. The recipe is back to the page writer's. The pin cannot show this effect at a readable size; nearest honest picture: none from the engine (a diagram of the red and blue sample points scaled about the center, or the page dropping the figure and keeping its worked numbers).
- `aberration-corner`: published 2026-11-24 (rounds 3 and 4, the pin v0.8.0). With temporal anti-aliasing the half-pixel
  fringe spreads over the soft edges and cannot be seen; the recipe now sets `"antiAliasing": "off"`, so each edge is
  one step and the shift shows as a line one pixel wide. Round 3: the corner crop held only blue sky and a tree's edge
  (blue against green, low contrast; the largest change 33 levels of blue). Round 4: the crop `edge`
  ([0.935, 0.606, 0.974, 0.657], scale 5, 150 by 111 pixels) holds the fence at the right edge against the gray sky.
  Looked at enlarged: off, clean steps; on, a dark red line on the right side of each dark board, a blue line where the
  sky meets the first dark board, an olive line where a lit board meets the second dark board, as the shader predicts
  (red read farther out, blue nearer in). The page's directives now name `crop=edge`, and a new paragraph before them
  says what the crops show and why anti-aliasing is off. Caption, alt and shows rewritten; the caption no longer claims
  the center, which no crop shows.
- `flare-sun`: published 2026-11-18. Round 4: the recipe now sets `"world": {"loadAll": true}`, the recipe form's
  wait for a world (§5.4: `world.loadCells` over every cell within 20 km, pinned, with `wait`), so no cell streams in
  during the capture; the `complete` set (§5.3) has no pointer for world cells and the recipe's steps have no wait of
  their own, so no `until` step on `world.status` was needed. Both variants' captures are byte-identical. Looked at:
  off, a bright disk with its glow and its streak on the water; on, six rays and tinted ghosts, pink and green on the
  sun's side, a pale one past the center on the same line (scales -1.6, -0.7 and 1.2 by the page's formula), and long
  ghosts of the water's streak. The caption now says so (the next note's request). Earlier: failed, nondeterministic.
  Round 1 (the `ow.sunward` shot's camera): the on variant shows the sun with six rays and tinted ghosts along the line through the image's center (good), but the crops `sun` and `ghosts` looked at the wrong places (the sun is at about x 0.36, y 0.38): crops moved to [0.2, 0.15, 0.52, 0.55] and [0.5, 0.15, 0.9, 0.75]. Rounds 2 and 3: the off variant's two captures differ (920 thousand pixels, up to 60 levels); the difference map shows a dark near slab at the bottom left present in one capture and not the other, a world cell still streaming in. Images: `G:/GameEngineAI/.worktrees/docs-work/photo/image-lens-effects/nondeterministic/image.lens-effects.flare-sun.off/`. Next try: tilt the camera up (target y about 46) so the frame's bottom holds only the far sea, or let the cell load before the capture. The caption should also say that the ghosts lie on the line through the sun and the center, some on the sun's side (negative scales), not only "on the other side".

## Clerk

- Nothing asked.
