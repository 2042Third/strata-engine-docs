# Notes: image/tone-mapping

## New terms

- CPU twin: the same arithmetic as a shader function, written in C++ in `PostProcessMath` so that a test can run it without a GPU. Home: this page. Aliases: CPU reference.

## Since

0.3.0: the display pass with Reinhard and ACES is the engine's oldest post-processing (the page states that ACES was the default until 0.7.0, from the comment at `PostProcessComponent::Tonemapper`). Filmic arrived in 0.7.x (the comment names 0.7.0 as the last ACES default).

## Requests

- Hosts for Further reading (entries are cited without links except github.com): none required.
- Figures not drawn or taken: `tone-curves` and `hue-skew` (diagram requests, to be drawn), `lanterns` (scene, Showcase outpost; the camera `scene` and the lantern framing need a planner's check). The sweep of Toe and Shoulder (`render-image:493`) and the six-curve shot (`render-image:491`) are not placed: the page shows ACES against Filmic and a table of middle gray's values.
- Word list: none proposed beyond the term above.

## Not verified

- Statements about Hable's curve, the Gran Turismo curve and Hill's fit (who made them, that Hable's curve works per channel) come from general knowledge, not from the pin; the page names no person.
- The ACES, AgX and Neutral values for middle gray come from the page's sketch, which copies the shader's formulas; no GPU render was compared.
- The "Who uses it" cells of the alternatives table are general statements about other products.

## Findings not applied

- The brief had no open findings.
- The sweep figure (`render-image:493`) and the six-curve shot (`render-image:491`) are replaced by one comparison and a table (see Requests).
- AgX's and Khronos Neutral's own sources are cited in Further reading only.

## Figures

- `lanterns` (taken 2026-11-17 at the pin, three rounds). As written (camera `scene`, AutoExposure off, Exposure 0.8 and 0) the Showcase at Golden rendered pure white, and the lanterns do not burn at Golden. The recipe now uses `station: "Dusk"`, a camera of its own on the hut, lantern A and the fire pit, and changes only `Tonemapper`, so both sides have the same exposure, as the page's sentence before `::compare{id=lanterns}` says.
- What the picture shows: the lantern itself is a few pixels and its core is white under both curves; the hue difference is in the light it casts. Under ACES the lit wall is darker and redder (mean sRGB 43, 17, 6), under Filmic lighter and more orange (63, 35, 17). Caption and alt now say that. The page's "The lanterns are saturated, so they show the hue skew" fits the light, not the flames: a writer may want to say "the lantern light".
- `lanterns` retaken 2026-11-24 at v0.8.0 (319075e3), one round, recipe unchanged. `figures.py compare` against the 822a7a46 originals: about 1 % of pixels differ, by at most 16 levels; the ACES side stayed below the publish threshold (stamp checked at the new pin), the Filmic side was republished. The earlier numbers above were means of the whole frame, not of the wall. Measured on regions: the hut wall is 111, 43, 12 under ACES and 149, 80, 35 under Filmic; the hillside 61, 18, 3 and 89, 45, 17; the ground stays near black in both (13, 6, 2 and 24, 15, 9). The wall is lit evenly and the hut throws its shadow on the hill to its left, so its light is the low dusk sun, not the lantern, which lights only the lintel; the fire pit shows no flame. Caption, alt and shows now name the dusk light on the wall and hillside, not the lantern light or the ground.
- For a writer: the sentence before `::compare{id=lanterns}` ("The lanterns are saturated, so they show the hue skew") is not what the picture shows: the skew is seen in the warm sunlight on the wall and hillside. Something like "The dusk light is a saturated orange, so it shows the hue skew" would match.
- `lanterns` retaken 2026-11-24 at 319075e3 after a viewer's report (the lantern was a 10 px dot; the alt's white core could not be seen; the redder wall read as hue skew against the page). The camera now stands 3.5 m from lantern A ((-17.93, 1.6, -13.58) toward (-20.76, 1.75, -15.63), fov 30): the lantern is about 100 px tall. Measured: the lantern's 30 brightest pixels are 254, 250, 244 under ACES and 254, 248, 237 under Filmic (near white in both); the glow on the wall above it is 190, 129, 72 against 202, 144, 91 (same hue, 29 degrees); the wall right of the door 124, 55, 19 (hue 21) against 160, 90, 43 (hue 24). So ACES's wall is darker and slightly redder: its lower middle gray (the table), not hue skew, which the page teaches moves hues toward orange and white. Caption, alt and shows now say that. The lantern's glass clips to white under both curves, so no framing of this pin shows the skew on the lantern itself.
- For a writer (stands from the viewer's report): replace "The lanterns are saturated, so they show the hue skew" with a sentence that points at the wall: "At the same exposure ACES makes the dusk light darker and redder, because it puts middle gray lower."

## Clerk

- Admitted the term CPU twin, homed here, alias CPU reference.
