# Notes: light/sun-shadows-2

## New terms

None proposed. The page defines the glossary's eight terms (umbra and penumbra, contact hardening, PCSS, depth range pyramid, tent filter, screen-space shadow mask, edge-aware blur, contact shadows).

## Since

0.7.0: physical-width filter, depth ranges, fixed noise and the screen-space mask landed in 0.7.0 (inventory render-direct:123-128; PCSS itself dates from 0.3.0).

## Requests

- Figures: penumbra-poles, disk-taps, stair-steps and contact-shadows are not taken yet. penumbra-poles needs the look-dev shot `lookdev.thin` and the sun's `ShadowSoftness` set by `component.set` (property name assumed from `DirectionalLightComponent`). disk-taps, stair-steps and contact-shadows wait for "tier 2: renderer switches" (taps, the stair-step blur and contact steps are not switchable per variant at the pin, except through a Custom quality for taps and contact steps).
- Names for the word list: none required; Further reading names (Fernando, Donnelly, Lauritzen, Annen, Klein) are not read.
- The page links `../light/sun-shadows-1.md`, `shadow-basics`, `local-shadows`, `area-lights`, `../image/taa.md`, `../gpu/compute.md`: they must exist.

## Not verified

- The pole sizes (3, 5, 10 cm) of the brief's penumbra figure: the figure uses the look-dev shot `lookdev.thin` whose pole geometry was not read.
- The property name `ShadowSoftness` in `component.set` values and the quality `custom` field form were taken from `RendererComponents.h` and the figures tool, not run.
- Publication years and titles of the cited papers (2005, 2006, 2008, 2015) come from memory, not the pin.
- The 0.35-0.52 ms and 0.06-0.10 ms costs are quoted from the engine's developer guide, not measured.

## Findings not applied

- The brief lists no open findings. Item `render-direct:826` (contact shadows in 0.7.0's presets) was checked: `Docs/Releases/0.7.0.md` says High and Ultra drew them, and `RendererQuality.cpp` sets the row to 0 in all four presets (0.8.0 comment).
- Exercise "pyramid's first level as a debug overlay" is a design answer, not a patch.

## Figures

- `penumbra-poles` (taken 2026-11-17 at the pin, two rounds). The look-dev poles are `Pole 3cm`, `Pole 5cm` and `Pole 10cm`, all 2.5 m tall at x = 4, 5 and 6 (`Tools/LookDev/LookDevScene.json`): they differ in thickness, not height, so the caption's "tallest pole" was wrong. Through the shot `lookdev.thin` the shadows were thin lines a third of the frame wide; the recipe now has a camera of its own above the shadows. With the 2 degree sun every shadow blurs toward its tip and the 3 cm pole's shadow fades out; with 0.53 degrees they stay sharp. Caption, alt and shows say that now.
- `disk-taps`, `stair-steps` and `contact-shadows` waited for "tier 2: renderer switches" at 822a7a46.
- 2026-11-23, pin v0.8.0 (319075e3). `penumbra-poles` retaken: `figures.py compare` finds both pictures identical to
  the published ones (0 differing pixels); kept as published.
- `contact-shadows` (published, three rounds). Round 1, shot `lookdev.contact` at High: the shadow map already draws
  the plate's shadow and it falls behind the plate, so 0 and 16 steps looked alike. Round 2: a coarse map (Custom
  quality, 1 cascade of 1024 texels, the sun's `ShadowDistance` 200 m) loses the plate's shadow, but the camera still
  looked at the lit side. Round 3: camera on the shaded side (-z): with 0 steps nothing grounds the plate, with 16 a thin
  dark line runs along its lower edges. Caption, alt and shows now name the coarse map and the shaded side. The
  tier-2 waitsFor was wrong: taps and contact steps are Custom quality rows, no renderer switch.
- `contact-shadows`, a viewer's review (2026-11-23, two rounds). The dotted light seam between the plate's face and the
  line is real (single floor pixels at about 99 of 255 beside the line's 19 and the floor's 117): caption and alt now
  name it. The viewer read the line as 3 to 4 px; luminance columns of the published 16-step picture give a core of 7
  to 8 px (18 to 21 of 255) and a fade of 5 to 7 px, about 13 px in 1280. Moving the camera in does not widen it: at
  fov 13 and fov 8 (same position, target at the front edge) the line stayed a few pixels high (at fov 8 a 2 px core),
  so the published camera stays. The viewer's 2x crop of the front lower edge (rect about [0.30, 0.40, 0.69, 0.61],
  scale 2) needs `::figure{id=contact-shadows variant=steps-0 crop=…}` lines in the page beside the ::compare (a
  ::compare shows no crops): a page edit, left to the writer.
- `disk-taps` (not published, two rounds). Camera on the 10 cm pole's shadow with the sun's `ShadowSoftness` 6, then
  10 degrees, fov 35 then 18, anti-aliasing off, `ShadowFilterQuality` "8" against "32": the two pictures differ by at
  most 2 of 255 levels and neither shows grain. The pin cannot show the caption's "fine fixed grain" with 8 taps (the
  engine's test `GPU.SceneRenderer.ScreenShadows` asserts that wide penumbras have no grain without anti-aliasing).
  The page's words would need to say that 8 taps already leave no visible grain at the pin, or the figure is dropped;
  the nearest honest picture is the pair as taken, captioned "8 and 32 taps leave the same smooth edge". Marked with a
  tier-3 waitsFor naming that.
- `stair-steps` (blocked, not taken). No renderer switch, quality row or debug view turns the stair-step blur off at
  the pin (`viewport.capture` renderer switches have none), so the "without" picture cannot be made; waitsFor is now a
  tier-3 line naming a `StairStepBlur` switch. The nearest honest picture is one grazed hard edge with the blur on
  (straight), with a caption that does not claim a comparison.
- 2026-11-24, last figures at the pin v0.8.0 (319075e3). `disk-taps` taken and published: the writer's caption already
  says that 8 and 32 taps give the same smooth edge, which is what the pin draws (the two pictures differ by at most 2
  of 255 levels, 57 channel values by more than 1; an enlarged edge shows no grain in either). Alt and shows now say
  pictures, not crops, of the 10 cm pole's shadow band.
- `stair-steps` keeps its tier-3 waitsFor as the request for a later edition; its stand-in is the drawing
  `stair-step-blur` (made by `docs-work/photo/last-light-sun-shadows-2/stairs.py`): texels of 6 by 3 pixels, the left
  panel in whole texels (saw teeth), the right blurred along x then y with the stair-step radius of 4 pixels (sigma 2).
  The left panel omits the tent's narrow ramp, so the caption says "a drawing, not a capture". The page places it after
  the paragraph on `ReceiverTexelPixels`, with a sentence that introduces it. One capture of a straight grazed edge, the
  nearest picture, was not chosen: alone it shows no saw teeth and teaches less than the drawing.

## Clerk

- Nothing to admit.
