# Notes: image/pre-exposure

## New terms

- epoch: a counter that the renderer raises when earlier exposure readbacks stop describing the frames to come (a reset, a stretch of manual exposure, the end of a value view); each readback carries the epoch of the frame that recorded it and only the current epoch is read. Home: image/pre-exposure. Aliases: epochs.

## Requests

- Words: Frostbite (a name, used twice), epoch and epochs (the proposed term above).
- Host: none linked; Further reading cites Lagarde and de Rousiers (SIGGRAPH 2014 course notes) and the Wikipedia article on the half-precision format without links.

## Since

- since 0.6.0: commit b4fcc933 "Pre-expose the HDR target by a power of two" (2026-10-22) is first contained in v0.6.0.

## Not verified

- Why the 2 stops of headroom exist: the header comment names the sun's disk; the page states only the arithmetic (P is a quarter of the exposure factor).
- That fog and the clear color multiply by P: taken from the header comment of SceneRendererStats::PreExposure, not read in the shaders.
- The sun's disk luminance in Strata; the page uses 31,800 nits for a white surface at 100,000 lux (E over pi, albedo 1).
- The project's picture wait (ProjectThumbnail, c_MaxExposureFrames = 8) is mentioned only as "the project's picture".

## Findings not applied

- The brief's text capture of the statistics (`PreExposure`, `PreExposureSettled`): the page has no figures file; the capture command and keys were not verified (viewport.capture returns `preExposureSettled`; no `preExposure` key was found).
- The cases "settling after a reset" and "the history follows a step" appear in How it is tested; the case of the 100,000 lux sun is named only, not described.

## Clerk

- Admitted the term epoch, homed here (its plural follows).
- Admitted to names.txt: Frostbite.
