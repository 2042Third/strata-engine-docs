# Notes: light/fog

## New terms

None proposed; Height fog is the glossary's term, defined in bold on the page.

## Since

0.6.0: the inventory (render-direct, "Height fog component" row) dates the component and its integral to 0.6.0; the atmosphere horizon as fog light is 0.7.0. Not checked against the 0.6.0 tag.

## Requests

- Words for `tools/data/extra-words.txt`: analytic, volumetric, falloff, opacity, numeric.
- Names for `tools/data/names.txt`: Wenzel, Wronski.
- Figures `density-sweep`, `sun-scattering`, `color-from-sky`: taken and published (see Figures).
- Links to `../basics/programming-2.md`, `../basics/programming-3.md`, `../core/conventions.md`; the brief's `world/reflection` link was dropped.

## Not verified

- Who uses distance fog ("older real-time engines") and "Not named in this page's sources" for fog volumes: general statements, not engine facts.
- Wenzel 2006 and Wronski 2014 as the origin of analytic height fog and froxel fog, and Unreal's exponential height fog: from the brief, no source read.
- That the frame setup calls `SetHeightFog` once per frame on the main thread: only the call at `SceneRenderer.cpp:3296` was read.
- The slot reservation text (SRV 34 and 36 for volumetric fog and fog volumes) is from the comment in `Strata/shaders/Include/Scene.slang`; the roadmap line was not read.
- The picture claims in the figure captions.

## Findings not applied

The brief lists no open findings. Not carried: the brief's "first active component of a kind" is left to `world/reflection` (the page states the rule in one sentence); a fog "crop at the horizon" and a `MaxOpacity` sweep are not requested as figures (the text states the effect); `Docs/Roadmap.md:948` was not read.

## Clerk

- Admitted to names.txt: Wenzel, Wronski.
- Admitted to extra-words.txt: analytic, opacity, numeric, falloff (volumetric was already there).
- Page fix for the acronym rule: GPU is spelled out at its first use.

## Figures

Photographed in one round (2026-11-18), all three published.

- All three: the basic3d ground is 20 x 20 m, so cubes past 10 m stood on nothing; the recipes now scale `Ground` to
  1000 m, use 3 m cubes and an explicit camera (`camera: "scene"` looked at the origin, past the row).
- `density-sweep`: the far cube is slightly pale at 0.01 and nearly gone at 0.04; the near cube greys a little.
  Caption names "four times the density" (the check refuses bare numbers in captions).
- `sun-scattering`: the basic3d sun is 40 degrees up behind the camera's right; `lighting.applySkyPreset` (Clear,
  elevation 8, azimuth -100) puts it low ahead of the camera. Scattering 0 is not perfectly even: the haze is a little
  brighter toward the sun (the sky behind it), so the caption says "only a little brighter" instead of "equally".
- `color-from-sky`: off, the fog's radiance is its `Color` under white light of unit radiance, far below daylight, so
  the horizon shows a dark grey band, not the "flat pale blue" the first alt guessed; caption and alt now say so.

Retaken at the pin v0.8.0 (319075e3, 2026-11-23), one round, recipes unchanged: four originals are identical to the
published ones; `sun-scattering` scatter-0 (mean 0.30, largest block 0.59) and `color-from-sky` sky-on (mean 0.16,
largest block 0.37) differ below the thresholds, so the files stay and their stamps record the check at 319075e3.
Looked at all six: the captions and alts still hold.
