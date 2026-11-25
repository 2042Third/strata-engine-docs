# Notes: image/why-post

## New terms

None proposed. The page defines the glossary terms of its brief (HDR image, LDR as display-referred, display-linear, encoded, sRGB encoding, tone mapping, post source) and "pre-exposure" in bold; pre-exposure is homed by image/pre-exposure.

## Since

Subject: HDR target and post chain, present since 0.3.0 (inventory render-image:27: "0.3.0 had HDR"); pre-exposure from 0.6.0.

## Requests

- Figure `problem-pair` (compare, variants off and on, Basic 3D, no layout needed): not taken yet.
- Link targets not yet existing at writing: light/brdf, image/pre-exposure, image/exposure, image/tone-mapping, image/tutorial-post-effect, reference/renderer, appendix/not-in-strata.
- The check "Check yourself" answers rely on the glossary terms nit, shader, binding set being homed in the closure.

## Figures

- `problem-pair` (round 1, published): Basic 3D start view, scene camera. Variant off (Tonemapper None, AutoExposure off,
  Exposure 0) is uniformly 255 white in every channel: sky and ground both clip, no horizon survives. Variant on
  (Filmic, automatic exposure) shows a blue sky over the flat grey-brown ground plane. Caption, alt and shows rewritten
  to say so (the old caption claimed only the bright parts clip and that the ground shows texture; neither is so).
- Page words the picture contradicts (for the writer): line 29 says "The sky is flat white, and so is every bright
  wall": Basic 3D has no walls, and the whole picture, ground included, is white. Suggested: "The whole picture is flat
  white: sky and ground alike." This also confirms exercise 2's prediction (white at Exposure 0 on Basic 3D).
- `problem-pair` (round 2, after a viewer's review): same views. The variants are renamed `clipped-all-white` and
  `post-chain`, because the compare labels each side with its variant's name and the all-white side, labelled "off",
  looked like an empty slot or a failed image on a light page; the caption says the white area is the picture. Caption
  and alt now also name the band between the ground plane's far edge (a third of the way down) and the horizon (a fifth
  of the way down): the atmosphere's hazy ground beyond the plane. Line 29's "and so is every bright wall" still stands
  in the page (not the photographer's to change); the viewer's suggested words: "The whole picture is flat white: the
  sky and the dark stone ground clip alike, with no horizon left." Line 47's "The sky, the wall and the sun become one
  flat white, as in the left picture" has the same problem: the picture has no wall and no sun disk in view.

## Not verified

- The luminances of paper in sun (30,000 nits), the sun disk (1.6 billion nits) and a dark corner (0.1 nit) are physics round numbers, not Strata facts.
- The GPU stage names are shown as `TAA`, `DepthOfField`, `MotionBlur`, `Post` with the prefix "GPU." in prose because `names` rejects the dotted forms; the profiler's registered names (GPUProfiler.cpp:62-65) are GPU.TAA etc.
- That `SanitizeHDR` is called by every HDR writer rests on the comment in Common.slang and the inventory; the writers were not enumerated.
- Exercise 2's predicted pictures (white at Exposure 0 on Basic 3D) rest on make/lighting's exposure-sweep figure text, not on a run.
- Exercise 2's captures are not part of its tutorial file (no tutorial file captures); the file checks the values only.

## Tutorial run

- Round 1 (2026-11-18, pin Release): exercise-2 passed. The file was thinner than the answer: it read back only
  `Tonemapper`. It now checks the template's starting values (Bloom, AntiAliasing, AutoExposure on; method TAA, as the
  answer says) and reads back each value after it is set. The page needed no change.
- Round 2 (2026-11-23, pin v0.8.0 319075e3 Release): exercise-2 passed as written; the template's Post Process
  defaults (Bloom, AntiAliasing with TAA, AutoExposure on) are unchanged by the release. No file or page change.
- Final run (2026-11-24, official v0.8.0 package Strata-0.8.0-windows-x64.zip): exercise-2 passed as written; the
  pin-build run of round 2 was still current. `tutorials.py check --release` finds nothing. No file or page change.

## Findings not applied

The brief lists no open findings. Left out of the page by size: the Post Process inspector's inactive reasons, and `HDROutput` details beyond the probe bake.

## Clerk

- Nothing to admit.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.
