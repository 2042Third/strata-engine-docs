# Notes: indirect/problem

## New terms

None proposed. The page defines the three terms the glossary homes on it: indirect light, global illumination (GI) and radiosity.

## Since

0.3.0: the sky light and its constant `AmbientColor` are as old as the first tag (see the notes of light/sky); the experimental global illumination of 0.8.0 is only one of the page's subjects.

## Requests

- Names for tools/data/names.txt: Cornell (the Cornell box), Kajiya (the rendering equation's author), Crysis (the table's "Used by" cell).
- Word for tools/data/extra-words.txt: lightmap, lightmaps (also the home page `appendix/not-in-strata`).
- Figures not taken: `cornell-gi-off` (a scene figure of the look-dev project: shot `lookdev.cornell` with the Post Process entity's `GlobalIllumination` set false, recipe plays 2 steps; `complete` asserts `/previewLighting` false) and `cornell-reference` (a reference figure: `sketches/indirect-problem-pathtracer.cpp` run with the argument `picture` writes a 160 by 160 PPM). Both need the planner to take them.
- No new external hosts: Further reading cites without links.

## Not verified

- The claims about other engines and papers in the table and Further reading (Crysis, Quake, Unity, Unreal, Filament, Lumen's software and hardware modes, Metro Exodus, Path of Exile 2, the years of the papers) come from general knowledge, not from the pin.
- What the Cornell shot looks like with global illumination off (that the walls and objects receive no light from the panel) is the brief's statement; no picture was taken at the pin, so the first figure's alt text follows the brief.
- The thin-wall leak is stated as the general limit of a voxel method; the page `indirect/gi-limits` owns Strata's exact behavior.

## Figures

- `cornell-gi-off`, published after two rounds. Round 1 (shot `lookdev.cornell`, fov 70 from z 4.6): the side walls
  filled the frame and the panel's bloom spread a large white glow over the ceiling and the tops of both walls, which
  read as light reaching them. Round 2: camera at (0, 2.75, 8.5) looking at (0, 2.75, 0), fov 55, so the whole box
  shows through its open front, and `Bloom` off beside `GlobalIllumination` off. The panel is the only bright part; the
  walls, floor, ceiling, box and sphere show one dim constant gray, darker only where ambient occlusion acts. Caption,
  alt and shows rewritten to say so. The page's sentence ("only a dim constant color") holds.
  Retaken at the pin v0.8.0 (319075e3) with the same recipe in one round: `figures.py compare` found 0 differing
  pixels against the published file, so `publish` kept it unchanged (its stamp still names 822a7a46, the identical
  original). Looked at again: the caption, alt and shows still say what the picture shows.
- `cornell-reference`, published at the pin v0.8.0 (319075e3) in one round: `take --kinds reference` compiled
  `sketches/indirect-problem-pathtracer.cpp` with MinGW g++ (on the PATH) and ran it with `picture` (160 by 160, 256
  samples per pixel, 8 bounces, seed 4); two runs agreed. The picture is visibly noisy at that sample count, so the
  tints are faint to the eye; measured in linear color over the floor, near the left wall red 0.35 against green 0.28,
  near the right wall green 0.31 against red 0.30, at the centre 0.40 and 0.38; the ceiling averages about 0.10 against
  the back wall's 0.40, lit only by bounces. Caption and alt now say the picture is noisy and the tints faint, and the
  page's sentence after the figures says "faintly red" and "faintly green" instead of "turns red" and "turns green".
  The sketch is unchanged (more samples would change the page's code fence).
  Mended after a viewer's report (the tints and the ceiling's gradient read as even salt-and-pepper grain at 160
  pixels and 256 samples): the program's picture line, in the page's fence and the sketch file alike, now renders
  `Render(320, 4096, 8, 4)` at 320 by 320 (same line count, so the fence's line callouts hold; the text output of a run
  without an argument is unchanged). The recipe's `size` is [320, 320]. Taken again at the pin v0.8.0 (319075e3): the
  grain is fine, the floor near the red wall reads pink and near the green wall greenish when enlarged, the ceiling is
  lit and brightest by the back wall. Shows names the 4,096 samples; caption and alt name the remaining fine noise
  (the caption writes no number, which check would ask to record). One picture run takes about five minutes at the
  sketch's unoptimized build.

## Findings not applied

None open in the brief.

## Clerk

- Admitted to names.txt: Cornell, Kajiya, Crysis.
- Admitted the term lightmap (alias lightmaps), homed on appendix/not-in-strata as the request names, defined from this page's sentence.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.
