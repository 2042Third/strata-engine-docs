# Notes: image/encoding

## New terms

- TPDF (triangular probability density function): noise that is the sum of two independent rectangular noises, minus 1, so that the rounding error has the same power at every value; home: image/encoding; aliases: triangular dither.
- 10-bit intermediate, dither, film grain, noise modulation: defined in bold on the page as the brief's glossary terms list them.

## Requests

- Word "triangular" appears once in the expansion of TPDF; the lint passes it at the last run, but it is on no word list by itself (ask for extra-words.txt if the alias is dropped).
- Figure `banding-pair`: needs the variant fields for a renderer switch (`DitherOutput` off and on) of tier 2's `viewport.capture {renderer}`; the recipe uses setup steps with that command as a stand-in, and the figure carries `waitsFor` "tier 2: renderer switches". The Mermaid diagram of the bands stands in until the capture exists.
- Figure `grain-sweep`: shot `tp.grain` of `Tools/LookDev/Shots.json` with its center crop; variants set `FilmGrain` to 0, 0.3 and 1. The brief names mid-gray; the shot's center crop is what the pin has.
- The diagram of the code staircase and the noise densities (render-image:456) is not drawn as a picture: the page gives a table of the noise powers and a Mermaid flowchart of the passes instead.
- Mermaid diagrams: the bands (stand-in for the banding pair) and the passes that write the display image.
- Acronyms new to the page: none outside the glossary.

## Not verified

- That the engine's float targets hold every stage before the tone mapping (a sentence says Strata keeps earlier stages at a high precision).
- The rows "Who uses it" of the alternatives table (older games, tools that reduce colors, engines that average frames, engines with high dynamic range displays) are general knowledge, not checked at the pin.
- The Further reading entries (INSIDE talk, Wannamaker and others) are cited from memory.
- That a captured still of the editor's Scene view dithers: the field defaults to true, and no file of `StrataEditor/src` names it. (v0.8.0: `banding-pair`'s on side, `DitherOutput` true, shows the dither's grain.)

## Findings not applied

- render-image:456 diagram as a picture (staircase and densities): replaced by a table and a flowchart, see Requests.
- render-image:503 sweep on mid-gray: the figure uses the shot's own crop.
- new:4 evidence line range 1131-1136 was rechecked at the pin and holds; the page names the preferred formats.

## Clerk

- Added the alias triangular dither to TPDF, homed here (the page's wording replaces the definition kept); triangular is then a glossary word.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

## Figures

- `grain-sweep`, published (round 3 of the take). Round 1 took the recipe as written (shot `tp.grain`): the shot also sets `ChromaticAberration` 1, its center crop is 192 by 108 pixels, and `::compare` shows the first two variants' whole 1920 by 1080 pictures, never a crop, so at the column's width the 0.3 grain was averaged away and the third variant would never show. Round 2 failed: the sample opens `MainMenu`, not `Course`, so the UI canvas and robot had other ids. Round 3: a camera of its own on the main menu's robot (0.85, 0.85, 2.2 toward 1.55, 1.1, 0.1, fov 40), 768 by 432 so that the slider shows it near one picture pixel per screen pixel, the menu's `UI` canvas made inactive, and two variants, `FilmGrain` 0 and 1 (the slider shows only two). Seen enlarged: the grain is strong on the gray rings, the yellow body, the tree and the clouds, and faint on the near-black goggles, as the paragraph's weight predicts. The page's 0.3 example has no picture; a third side would need a ::figure of its own.
- `grain-sweep`, v0.8.0 (pin 319075e3): taken again with the same recipe; `figures.py compare` with the published originals found 0 differing pixels on both sides, so `publish` left the files and stamps unchanged. Seen: the grain covers the rings, the yellow body, the tree and the clouds at FilmGrain 1; the caption holds.
- `banding-pair`, v0.8.0: blocked by the book's tool, not by the pin. The pin has `viewport.capture {renderer: {DitherOutput}}` (check now refuses the `waitsFor`, so it is removed), but a recipe has no field that passes `renderer` to the figure's own capture: `capture_parameters` in tools/figures.py sends size, camera, overlays, quality, debugView and waitForAssets only, and a `viewport.capture` setup step takes a separate picture that is thrown away. Round 1 took both variants: the two PNGs are byte-identical and both results echo `renderer: {}`. Not published (the same gap as light/energy's `furnace-pair`). Needed: a recipe field `renderer` (variant-settable) passed to the capture; then the variants become `{"renderer": {"DitherOutput": false|true}}`.
  - Recipe changed meanwhile: the ThirdPerson sample's skies are bright blue with clouds (MainMenu's environment map), never a dark sky, so the figure now uses the Showcase at `station: "Dusk"`, camera (-2, 1.6, -2) toward (-16, 7, -16), fov 50, 1280 by 720. Round 1 shows a dark blue sky over the upper 40 % of the picture, from about code 24 at the top to 41 at the ridge over 280 rows (about 16 rows per code at the middle column), above the lit ridge, the hut and the fuel tank. Stretched eight times in contrast, the dithered sky shows only a fine grain and no bands, so the off side should show bands about 16 pixels wide. At the page's width the bands of one code will be faint; a `crops` entry on the sky (for example [0.35, 0, 0.55, 0.38], scale 4) would let a `::figure{crop}` enlarge them, which needs a page change.
  - Nearest honest picture until then: none from the engine; the page's Mermaid diagram of the bands stands in, as its paragraph says.
- `banding-pair`, published (v0.8.0, last round). The tool now passes a recipe's or variant's `renderer` to the figure's own captures; the variants are `{"renderer": {"DitherOutput": false|true}}` and the setup steps are gone. Both results echo their switch, and the PNGs differ. Measured at the middle column of the off side: the sky's blue climbs from code 38 at the top to 54 at the ridge in 17 flat bands of 13 to 21 rows; stretched eight times in contrast, the off side shows the bands and the on side a fine grain without them. At normal contrast the bands are faint (one code of a dark blue), and the page now says so. The Mermaid stand-in of the bands is removed (its numbers are the sketch's, which the page shows later), and the paragraph names the measured bands instead. Seen beside the caption: ridge, rocks, lit hut and fuel tank under the sky.
- `banding-pair`, mended after a viewer's report (v0.8.0). The sky held only the top 280 of 720 rows under the lit hut, the fuel tank and the rocks: the camera now looks up at about 40 degrees (target -16, 18.2, -16), so the sky fills the top 628 rows above a thin strip of ridge and rocks, and the hut and tank are out of the frame. Measured at the middle column of the off side: the blue climbs from code 28 at the top to 57 at the ridge, one code per flat band, bands of 16 rows near the ridge to 40 at the top; stretched eight times in contrast, the off side shows the bands and the on side a fine grain. The page's paragraph and the caption now say so. Not done: a contrast-stretched crop beside the pair. A recipe's crops are cut at the capture's own pixels (`check` compares each crop with its rectangle of the capture), and the tool has no step that changes a picture's contrast, so a stretched picture would be a picture the engine did not make, published past the tool; the caption says instead that the bands are faint and where to see them.
