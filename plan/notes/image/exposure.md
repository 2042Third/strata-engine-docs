# Notes: image/exposure

## New terms

None proposed. The ten glossary terms homed here (EV100, exposure, exposure compensation, exposure key, gray card, histogram, light/dark adaptation, metering, middle gray, percentile window) are defined in bold.

## Requests

- Extra words: multiplier (the factor M of the page), bin, bins (histogram ranges; 41 uses, central to the page).
- Hosts for Further reading (cited without links): the Frostbite course notes host, the Filament documentation host.
- Figure `exposure-sweep` (variants minus16, minus14, minus12) and `metering-modes` (variants average, center): Basic 3D template with `component.set`-style `postProcess` values; the variant keys follow `make/lighting`'s `exposure-sweep`.

## Not verified

- That the Basic 3D view shows the pictures the captions of `exposure-sweep` and `metering-modes` describe (balanced at -14, bright sky pulling the average down); no picture was taken.
- That `AutoExposureMetering` accepts the strings "Average" and "CenterWeighted" in a figure's `postProcess` recipe.
- The table of alternatives (who uses a technique) and the sentences about cameras (f-number formula, K = 12.5 for meters, sunny sixteen) are general knowledge, not read at the pin; the Developer Guide gives K = 12.5 and the sunny-sixteen EV100 of 15.
- The Further reading entries come from memory.

## Findings not applied

- The brief's figure for the key at 0 and 0.12 on `lookdev.room` and the adaptation sequence (leaving an interior at light speed 3 and 0): not placed, since a lookdev scene recipe and a live capture recipe were not checked; the key is taught by numbers, including the guide's measurement of the room (EV100 14.040, card 15.191).
- The brief's histogram diagram (`render-image:448`): the histogram's range and window are in the toy and the worked example, not in a picture.
- The brief's luminance-view figure: the page links `light/measuring-light` and does not repeat its figure.
- The brief's "meters around EV 15 with MaxEV 16": the page states the unit difference (MaxEV is log2 nits, EV100 minus 3) and says a sun scene averages EV100 15 to 15.6, which is 12 to 12.6 in log2 nits.
- Brief item `render-image:77-95` readback and pre-exposure: only named, as the brief says.

## Since

0.3.0: `Docs/Releases/0.3.0.md` lists HDR with automatic exposure.

## Clerk

- Admitted to extra-words.txt: bin, bins, multiplier (the page's word-list findings).
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

## Figures

- `exposure-sweep` (published, round 1): the recipe as written. The Basic 3D view at Exposure -16 is dark (ground dark gray, deep blue sky), at -14 balanced, at -12 washed out (pale ground, sky nearly white at the horizon) but not white: the caption now says so instead of "loses the bright ground to white".
- `metering-modes` (published, round 2): round 1 on the template's own view metered alike (EV100 15.09 Average, 15.06 CenterWeighted; no visible difference), since the ground fills both the middle and the edges. Round 2 adds a 3 m cube of `Materials/Ground.stmat` at the origin and looks at it from (-7.5, 1.5, -2.7), toward the sun's azimuth, so its shaded face sits in the middle against bright sky and sunlit ground: Average reads EV100 14.59, CenterWeighted 14.02, and the center-weighted picture is visibly brighter. Caption and alt rewritten for the block; the page's sentence before the figure does not describe it, so nothing in the page contradicts it.
- `exposure-sweep` (mend, 2026-11-17): a viewer found the three stacked figures unlabelled (each repeats the recipe's caption and alt, and the plugin has no per-variant caption). Pictures unchanged (checked again: -16 dark, -14 balanced, -12 washed out, in page order); the caption now begins "Top to bottom: Exposure -16, -14, -12." and the alt names the pictures in that order. No retake.
- `metering-modes` (mend, 2026-11-17): a viewer asked for `::compare{id=metering-modes}` in place of the two stacked `::figure` lines (page lines 453-455), so the half-stop difference shows on one labelled average/center slider. The recipe is ready for it (two variants, same size and encoding; the default before/after are average and center, and the caption and alt already speak of "first" and "second" in that order), but the swap is a change to the page, which the photographer may not make: the writer should replace the two lines with `::compare{id=metering-modes}`. No retake.
- Retaken 2026-11-23 at v0.8.0 (pin 319075e3), one round, work folder `docs-work/photo/image-exposure`. `figures.py compare` against the published originals: 5 pictures, 0 differ (byte-identical PNGs), so `publish` left all five files and stamps unchanged (the stamps still name 822a7a46; publish records no `checkedAt` for an identical original). Looked again: -16 dark, -14 balanced, -12 washed out; the block is darker under Average than under CenterWeighted, EV100 14.59 and 14.02 as the `numbers` say. Captions, alt and the page's text still hold. `check --release` reports nothing for the page.
