# Notes: image/spatial-aa

## Since

0.3.0: FXAA exists since 0.3.0 (inventory render-image:195); the subpixel blend changed from 0.75 to 0.25 in 0.7.0; the morphological method is later and shares the page.

## New terms

- Point sample: the color of a scene at one point, the center of a pixel, taken as the pixel's value. Home: image/spatial-aa. Aliases: sample at a pixel's center.
- Post pass: a full-screen pass over a finished picture, here an anti-aliasing pass. Home: image/spatial-aa. Aliases: post-process anti-aliasing.

## Requests

- Figure `aliasing-floor`: Physics Playground floor crop (rect 0.4557, 0.5324 to 0.5495, 0.6991 at 3840x2160, scale 4) in four variants through the recipe's antiAliasing field; the crop rect is computed from the DG's region 1750,1150 360x360 and is not a shot of Shots.json.
- Figure `subpixel-pair`: variants low (0.25) and high (0.75) need a build with c_Subpixel changed; waitsFor tier 2: renderer switches. The brief asked for a diagram; a scene recipe was used because the point is texture detail.
- No hosts requested: the Further reading entries carry no links.

## Not verified

- Which draw paths the test "Both draw paths anti-alias equally" compares: read from its code (CPU-driven and GPU-driven), not run.
- The cost of about 0.31 ms of the morphological method and the detail shares (0.88, 0.86, 0.93) come from Docs/DeveloperGuide.md, not measured; the page quotes only the subpixel numbers and slope errors.
- Alternatives table's "who uses it" column is general knowledge, not checked at the pin.

## Findings not applied

- None: the brief lists no open findings.

## Figures

- `aliasing-floor` (published, round 2). Round 1, the writer's rect 0.4557, 0.5324 to 0.5495, 0.6991: only floor tiles. The tiles are texture detail filtered by mipmaps, not geometry edges, so the four variants looked the same, with no staircase at all. Round 2: rect 0.4375, 0.7315 to 0.4896, 0.8009 (200x149 pixels at 3840x2160), the far end of the ramp, where its dark rail crosses the floor. Off shows whole-pixel staircases along the rail's slanted edges; FXAA, morph and TAA show smooth gradients; the tiles look almost the same in all four. Caption, alt and shows rewritten to say so.
- Page words the picture contradicts (not changed here): line 29 "Look at the floor ..." and line 35 "every tile edge is a staircase". The steps are on the ramp rail's edges, and the tiles show none; the paragraph should name the rail's edges over the floor.
- Viewer's review (round 3, no retake): confirmed both faults on the published crops. The tiles cannot show staircases at the pin: they are texture detail filtered by mipmaps, so no recipe makes line 35 true; the page's words must change. Proposed: line 29 "Look at the end of the ramp's rail over the floor of the Physics Playground in four ways."; line 35 "The first picture has no anti-aliasing: the rail's slanted edges are staircases. The other three trade the steps for soft gradients in different ways; the tiles look alike in all four." The second slider (line 33, before=morph after=taa) shows no unsmoothed rail; the page's directives should become `::compare{id=aliasing-floor before=off after=morph}` and a third `::compare{id=aliasing-floor before=off after=taa}` (the recipe already has every variant, no retake needed). Meanwhile the caption names which versions each slider pairs and no longer reads as if every slider held the version without anti-aliasing.
- `subpixel-pair`: not taken; it waits for tier 2: renderer switches. Its crop still uses the old floor-only rect, which suits that figure because it compares texture detail.
- Pin v0.8.0 (319075e3), 2026-11-23. `aliasing-floor` taken again: `figures.py compare` found all four crops identical to the published files (0 differing pixels), so publish left them unchanged; the off crop still shows the rail's staircases and FXAA's gradient. Lines 29 and 35 of the page now name the rail and agree with the picture.
- `subpixel-pair` at the pin, round 1, blocked (not published). The pin has the switch (`viewport.capture {renderer: {"FXAASubpixel": 0.25 | 0.75}}`), so `waitsFor` is removed and each variant gets a setup step with it, as light/energy and image/encoding do. The take ran, but the two crops are byte-identical (mean difference 0) and both results echo `"renderer": {}`: a setup step's `viewport.capture` is a separate capture whose picture is thrown away, and `capture_parameters` in tools/figures.py passes no `renderer` to the figure's own two captures. No recipe field reaches the figure's capture, so the pin cannot be photographed for this pair until figures.py gains a recipe field `renderer` copied into the capture parameters (a tools change, not a photographer's). Then the recipe needs only `"renderer": {"FXAASubpixel": …}` per variant in place of the setup steps; retake and check that the 0.75 crop really is softer before publishing. The same defect means light/energy and image/encoding variants that differ only by a renderer switch are probably identical too. Nearest honest picture meanwhile: none at the pin (both values give the same pixels through the tool); the page can show the FXAA crop of `aliasing-floor` alone, or the pair can stay out until the tool passes the switch.

## Clerk

- Admitted the term post pass, homed here (its asked alias is unused on the page and stays out). Not admitted, left for the planner: point sample, which would make the section "The problem and how engines solve it" define five new terms (term-section allows 4); its bold may stay.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.
- `subpixel-pair`, round 2 (pin v0.8.0, 2026-11-24): published. The tool now passes a recipe's `renderer` to the figure's own captures, so the setup steps became `"renderer": {"FXAASubpixel": 0.25 | 0.75}` per variant; both results echo their switch. Same rect as before (the guide's measured region of the floor). The crops differ in 16 % of their values (mean 0.6, at most 35 of 255); the Laplacian energy of the 0.75 crop is 23 % lower than the 0.25 crop's, in line with the page's "about a fifth". By eye at five times the difference is small but real: the single-pixel dots of the blue pattern blend at 0.75. Caption and alt say so and that the difference is small. The page places the pair as one `::compare` (low before, high after) in place of two figures, so a reader can move between them, with a lead-in sentence.
