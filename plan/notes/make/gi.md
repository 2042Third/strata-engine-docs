# make/gi notes

## Since

0.8.0: global illumination (experimental), its Post Process fields, the Graphics Quality row and the Voxels, GI, Open and Probes debug views landed in 0.8.0 (`Docs/Releases/0.8.0.md`, `Docs/Manual/Lighting.md`, `Docs/DeveloperGuide.md` "Global illumination").

## New terms

None. The page explains global illumination and voxel in plain words (their homes are `indirect/gi-voxels` and the glossary's own) and bolds no term.

## Requests

- Figures `result` (a compare of the variants `off` and `on`) and `thin-wall` (the Voxels view): scene figures on the Basic 3D template, rebuilt by `setup` with the room's commands (a tutorial's state is no project of a figure); no editor layout is needed.
- The page asks for `Ultra` as a bold UI label (the preset's name) because it is on no word list; if the clerk adds it to the extra words, the bold can go.

## Not verified

- No picture of the room was seen: every "You should see" comes from the engine's documents and code at the pin, not from a run of the editor. The look of the room with and without global illumination (the walls and the ceiling, the red tint near the floor) is stated only as far as `Docs/Manual/Lighting.md` states it.
- The thinnest wall that keeps one-sided voxels: the guide says "thinner than two voxels" (20 cm at High). Run 2026-11-24 (see "Walk G-final-9" below): the Voxels view marks a wall only where both faces lie inside one voxel.
- How the Scene view's camera moves when the editor frames a selection (`F`) was not checked; the page makes the engine rebuild its voxels by disabling and enabling Global Illumination instead of moving the camera far away.
- That a thin emissive panel of 0.2 m (the first variation) lights the ceiling at High as `Docs/Manual/Lighting.md` says of "a lamp in its ceiling" was not run.
- The settle frames of the page's room (17) assume the brightest voxel albedo is the 0.73 gray; the code reads the largest albedo of the voxels (`VoxelClipmap::GetBounceAlbedo`), whose channel rule was not read.
- The editor's wording of the Inspector section ("Global illumination") and of the debug view entries is read from `RendererComponents.cpp` and `ViewportPanel.cpp`; the property labels "Global Illumination" and "Global Illumination Intensity" are the manual's.

## Findings not applied

- critic-make-b2-2 names `make/commands` (its Starting state), not this page; the page's tutorial stage is the download of the room with Global Illumination on that the finding asks for (`tutorials/make/gi.tutorial.json`, stage 1).
- The brief's "lamps and moving or skinned objects add no bounce light": at the pin moving objects take part as oriented boxes (`Docs/DeveloperGuide.md` "Moving objects"), glowing surfaces light their surroundings, and only point and spot lights, posed skinned meshes' bounce, specular light and the rest of the list are missing. The page says so.
- The brief's "make one wall 10 cm thick and see it lit from both sides": the code makes such a voxel two-sided that sends no light (`Strata/shaders/GI/VoxelFinalize.comp.slang`, `VoxelInject.comp.slang`); the manual says "lit from both sides" and the developer guide "dark from both sides". The page shows the error color and "no bounce" only.
- The brief's "frame the camera elsewhere and back": replaced by disabling and enabling Global Illumination, which rebuilds the voxels the same way (`Docs/DeveloperGuide.md` "The clipmap"); no menu jumps the Scene view's camera and `make/commands` is outside the closure.
- The brief's "about twelve frames": 12 holds for a plaster of albedo 0.58; the page's room is 0.73 and says 17 (the manual gives both).
- The brief's cost "about 4 ms": the release notes measure 4.2 ms at 3840 x 2160 and High; the page uses 4.2 ms.

## Movable claims

- Global illumination is experimental; the quality row is Off at Low and Medium and High at High and Ultra.
- Voxel sizes (10 cm at High, 20 cm at Low), the limit of two voxels (20 cm, 40 cm), the finest levels' four levels "10-80 cm" in the legend, probes 0.5 m apart at High.
- The field's reach: full within 7.5 m horizontally and 5.5 m up and down at High, faded out by 9.5 m and 7.5 m (Low: 7 m and 2.8 m).
- The settle frames: 12 (albedo 0.58), 17 (0.73), up to 38; 15 bounces under 0.25 % plus two spare frames.
- The cost: about 4.2 ms of GPU time at 3840 x 2160 and High (25 % of a frame at 60 frames per second) and about 156 MiB of memory for each view that uses it, measured on one Windows machine.
- Low bounces once and is too dark; round objects read a few percent dark.
- Moving objects take part as boxes, at most 64 parts at once; characters receive bounce light but neither block nor bounce it.
- Point and spot lights add no bounce light; a rect light whose panel glows counts twice.
- The five things that do not exist: an Ultra level, a color of each voxel from its texture, hardware ray queries, nested probe fields, denser probes near surfaces.
- The legend texts "Two-sided: no bounce" and the entries of the debug view chip.

## Figures

Published 2026-11-24 at v0.8.0 (pin 319075e3), work folder `docs-work/photo/last-make-gi`, one hold, first round.

- `result` (compare off/on): the room from its southwest corner, the slot, a band of sun on the red floor. `off`: blue-gray walls, a pale tan ceiling (pair: 0.059 % of pixels by 1 level). `on`: walls and ceiling tinted pink and red, brightest beside the band, the floor a lighter red (pair: 0.248 % by 1 level, within R57). The caption now names the off picture's colors instead of "cool light".
- `thin-wall` (Voxels view): `Wall East Low` at Scale X 0.06, Translation X 2.05 (both faces inside one voxel) is a flat coral red, the Error color of the legend's "Two-sided: no bounce"; the thicker walls keep their shaded voxel colors (pair identical).
- What settled them: the recipes enable Global Illumination in `setup` and throw away one capture at the figure's pose before the compared pair (the steps written by `docs-work/photo/last-make-gi.warmup.py`, kept beside the work folder). Without that capture, the two captures of the 2026-11-23 take differed (`result.on` 3.8 % of pixels by up to 4 levels, `thin-wall` 84.7 % by up to 33) although each reported `globalIlluminationSettled` true.
- Finding for the engine: `viewport.capture` calls the GI settled before its bounce light stops rising after the voxels are first built (`SceneRendererGlobalIllumination.cpp` sets `GlobalIlluminationSettled` from the voxelization work alone; the bounce settle frames of `SettleGlobalIllumination` did not cover the first build here). A capture should wait for the bounces, not only for voxelization.
- Exercise 3's thicknesses were captured on 2026-11-24 (not published): see "Walk G-final-9" below; only 0.06 m inside one voxel is photographed.

## Tutorial run

2026-11-24, pin 319075e3, with the pin build and the v0.8.0 package (both pass). The stage now runs every command tab of the page, not only the room and the Post Process switch: the camera, the four debug views, the thin wall and its restore, the off and on of Global Illumination, the sun turn, the three intensities and the Medium chip with its return to the project's preset. The page's tabs gained the lines their steps told but did not run (the Voxels view and the wall's restore, the GI view, the Lit view, intensities 0.5 and 1, quality `project`). The checks read the answers' settings and values only; no picture of the views was judged by the run.

## Walk G-final-9

Checked 2026-11-24 with the v0.8.0 package, GPU captures in `docs-work/walkfix-G9` (`tools/drive.py`, `results.json`,
pixels of the two-sided color 229, 82, 74 counted in `out/gi-*.png`; about 110 pixels of the axis lines in every take).

- Probes view of the page's room: `deadProbes` 0, `liveProbes` 92,160. Cascade 0's probes that a surface covers move off
  it or search their cell for open space (`Strata/shaders/GI/ProbeValidity.comp.slang`, comment at the top), so no probe
  of 0.3 m walls stays dead. A 2 m solid cube in the room gives 48 dead probes. Step 5's "You should see" says so.
- Thin walls (`Wall East Low`, Voxels view): inner face at x = 2 and thickness 0.25, 0.20, 0.15, 0.10, 0.05: no wall
  turns two-sided. A face adds only to the voxels not wholly behind it (`Strata/shaders/GI/VoxelFinalize.comp.slang`,
  comment; `WriteVoxel`), so a face on a grid line counts in the voxel in front of it alone. Inner face at 2.02: 0.05
  turns two-sided (60,598 pixels, as the 0.06 m wall at 2.05), 0.08, 0.10 and 0.15 do not; inner face at 2.05: 0.10
  and 0.15 do not. Exercise 3 now sets the five walls with the inner face at 2.02 and then 0.05 at x = 2.
