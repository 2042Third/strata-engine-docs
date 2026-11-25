# Notes: indirect/gi-cascades

## New terms

None proposed. The page defines the 24 terms the glossary homes on it, each once in bold. The penumbra condition, re-injection, multi-bounce, bounce gain and depth moments are used in plain text, because the glossary table of the brief does not list them.

## Since

0.8.0: `Docs/Releases/0.8.0.md` lists global illumination (experimental) as new in the release, and the brief's Needs closure has no earlier page for it.

## Requests

- Word list: "Chebyshev" (a name, three uses in prose and one in a table). It is the name of the visibility test of the Dynamic Diffuse Global Illumination paper that Strata dropped; the page cannot teach why without it. Please add it to `tools/data/names.txt`. This is the only `word-list` finding left.
- No layouts, no new hosts. The Further reading entries cite four sources without links.
- The sketch `sketches/indirect-gi-cascades-toy.cpp` has 94 lines, above the card's 30 to 80, because the sketch rules (warning-free, standalone, a reference beside the method) need them.

## Figures

Taken at the pin 319075e3 (v0.8.0) with its Release build, two rounds, all four published.

- `cornell-off-on`: round 1 failed: `Scenes/Cornell.stscene` has no light entity (only the emissive panel), so the capture used preview lighting. Round 2 takes `Scenes/CornellRect.stscene` (the same box with the panel made a rectangle light) at one manual exposure (`Exposure` -9.7); automatic exposure would have hidden the difference. Off: the ceiling is black; on: ceiling, box, sphere and walls two to three times as bright. The floor's tint of red and green is faint (samples 121, 117, 112 by the red wall and 97, 98, 91 by the green one), so the caption says so instead of a strong tint.
- `intensity-sweep`: round 1 at automatic exposure made one and two look alike (EV100 11.28 and 12.28: the meter undid the doubling). Round 2 holds `Exposure` -10.75 (0.53 - 11.28) for all three.
- `gi-views`: round 1 at automatic exposure blew the voxels view to white and the probes view to white spheres. Round 2 holds `Exposure` -11.5 (the gi view metered EV100 12.0). The voxels view now shows the sun's patch with stepped edges. The capture reports 0 dead probes in this view, so the caption no longer promises dark red ones.
- Mending after a viewer's report (2026-11-23, no retake). `::compare` draws only a recipe's first two variants (`src/plugins/figures.mjs`: `before = variants[0]`, `after = variants[1]`), and a crop reaches the page only through `::figure{id=… crop=…}`. So `gi-views` shows gi and open only: its voxels and probes pictures stay published but never reach the reader. The caption and alt now describe the two sides shown. The viewer's cure for the voxels view (a crop of the sun's patch, x 580 to 980, y 440 to 530, enlarged; the steps are 2 to 4 px at 1280 wide) needs a page line such as `::figure{id=gi-views variant=voxels crop=steps}` with a crop `steps` of `[0.45, 0.61, 0.77, 0.74]` at scale 3, and the probes view a line of its own. Proposed for the page's writer.
- `sealed-open`, viewer's report: the sealed picture is 0 in every pixel (the gi view's surface EV100 there is -6.2 at the median and -2.9 at p95, some 15 stops under the open room's, so the exposure of -11.5 draws it black). A third variant (the sealed room in the voxels view, which draws unlit voxels at a dark share of their albedo, `Strata/shaders/GI/VoxelView.frag.slang`, so the wall where the window was would show) would not reach the page: `::compare` shows two variants. The caption and alt now say the black covers every pixel and why. Needs a page line such as `::figure{id=sealed-open variant=voxels}` before that variant is added.
- `sealed-open`: round 1 metered the sealed room at EV100 -1 (13 stops brighter than the open room), which lifted a faint glow on its floor. Round 2 holds `Exposure` -11.5 for both: the sealed room is black. The gi view shows only bounce light, so the caption no longer names the sun's patch.

## Not verified

- The reading of the penumbra condition as "a neighbour's view of the end of an interval differs by about one ray patch" (the table of four cascades) is the page's own arithmetic from the layout, not a statement of the engine's documents. The page states the factors 2 and 4 as those of the published method (Sannikov); the pin's code and documents do not name the paper.
- The four Further reading entries are cited from memory, not checked against the sources.
- The 4.2 ms at 3840 by 2160 comes from the engine's guide and the release notes (the reference machine), not measured here.
- The claim that a closed mesh fills its inside and kills the probes in walls comes from the guide's description of `VoxelFill`; the page does not quote that shader.

## Findings not applied

- Brief, alternatives: "an octahedral-tile field and an SH field (both tried and not landed)". At the pin the nine spherical harmonics per probe (`FieldIrradiance`) are what drawn surfaces read, floored by the ambient cube; the octahedral tile survives only for the depth moments. The page says so and does not call the harmonics a rejected alternative.
- Brief, `new:13`: the guide says "16 to 1,024 directions"; the code gives 64, 64, 256 and 1,024 (`ComputeLayout`, tested by `GetRaysPerFrame` of 10,506,240 at High and 1,152,000 at Low). The page uses the code.
- Brief item 455: the slider with the path-traced reference. Not applied: the reference of `indirect/problem` is a 160 by 160 picture of an empty Cornell box made by a sketch, not of the look-dev Cornell scene, so the slider holds off and on only. The page links `indirect/problem`.
- Brief item 456: the four GI views of the Cornell box. The look-dev project has a shot of the Cornell box's `gi` view only; the page shows the four views of the sun room and the sealed room beside the open one.
- Brief E11 asks for a 1D toy. The toy is a flat two-dimensional world with probes on a line (one dimension of probes, directions as angles), because a one-dimensional world has two directions and cannot show four times the directions.
- Brief item 511 (the b3 buffer) is a `:::caution`, not a `:::rule`: `AGENTS.md` at the pin has no rule on it (its rule is on post effects and `FrameConstants`); the cause stays open, as the brief asks.
- Brief item 177 (level sampling) and 181 (statistics and readbacks) are covered in a sentence each, not in full: the page names `GlobalIllumination`, `GlobalIlluminationPending`, `GlobalIlluminationSettled`, `GIDeadProbes`, `GILiveProbes` and `GISurfaceVoxels`, and the blocking readbacks as a group, not every counter.
- Line anchors of the brief (`SceneRenderer.cpp:3069-3074`, `3320-3330`, `GIField.slang:181-236`, `GIMarch.slang:21-76`) differ at the pin; the page quotes the pin's lines (`GIMarch.slang` 21 to 75, `GIField.slang` 214 to 237, `Forward.frag.slang` 432 to 442).
- The brief's cost "about 1.8 times as bright" for Low is in the code comment at the pin (165 to 235 nits against 89 to 142): applied.
- Passive-voice and noun-stack warnings of the lint (about 34, mostly "is the merged radiance", "is dark red", "global illumination suites") were read and left: they are copulas or names, not hidden actors.

## Movable claims

- Cost: about 4.2 ms of GPU time at 3840 by 2160 and High; 10,506,240 rays a frame at High and 1,152,000 at Low.
- The layout at High: probe spacings 0.5, 1, 2 and 4 m; 64, 64, 256 and 1,024 directions; intervals 0 to 0.5, 0.5 to 2, 2 to 8 and 8 m onwards; field 24 by 20 by 24 m; field weight full within 7.5 m across and 5.5 m up and down, fading over 2 m.
- Constants: the occupancy gain 2.5, the march step 0.75 voxel, the lead-in occupancy 0.3, the run refresh at 0.1, the probe moves (half a spacing and 1.5 voxels), four relocation rings 0.1 spacings apart with a cost of 0.05 a ring, the normal bias 0.25 and view bias 0.3 spacings, 16 guard samples with a core of occupancy 0.6 to 0.72, the quarter floor on the visible weight, the albedo clamp 0.9.
- Settling: 12, 17 and 38 frames for the albedos 0.58, 0.73 and 0.9, with the 0.25 % threshold and two margin frames; captures and the project picture wait at most 54 frames.
- Low bounces once, and with every bounce its Cornell box would be about 1.8 times as bright as High's; High bounces on.
- The 0.17 % bound of the sealed-room tests; the fence-crawl figures 0.247 % and 0.0230 % (history).
- The feature is experimental: every item of the release notes' Known issues (thin gaps, angled walls, the range of the field, settling, repeats, moving objects) may change; the page leaves them to `indirect/gi-limits`.
