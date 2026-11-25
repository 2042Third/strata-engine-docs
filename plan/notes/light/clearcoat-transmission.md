# Notes: light/clearcoat-transmission

## New terms

None beyond the five the brief lists.

## Since

0.6.0: the coat and glass fields entered with that release (inventory render-direct:46-48, "0.6.0"); the first tag is not checked.

## Requests

- Figures `coat-roughness`, `coat-normal-map`, `glass-index`, `glass-thickness` (Physics Playground sample): the camera positions and the coat normal map setup are guesses; `Assets/Materials/PlasticBlue.stmat` and `Glass.stmat` exist at the pin, a scene object of the ball pit's walls was not looked up. The planner chooses the shots. `coat-normal-map` has no setup: it needs a normal map assigned to the coat.
- Hosts: no links in Further reading (Weidlich and Wilkie 2007, Khronos registry, McGuire and Bavoil 2013).
- Links to pages not yet written follow the brief's names: `light/area-lights`, `image/taa`, `indirect/ssr`, `light/atmosphere`.

- Names for `tools/data/names.txt`: Snell (Snell's law).

## Not verified

- The values of the BRDF table (about 0.04 head-on for a smooth coat's image light) are not stated on the page.
- That a map not yet loaded reads as its default (not stated on the page).
- The table's "Who uses it" column: general knowledge, not engine facts.
- Whether `Opaque` and `Mask` surfaces never blend: read from the flags and the pass, not from a test.

## Findings not applied

None: the brief lists no open findings.

## Figures

Photographed 2026-11-18 at the pin, Physics Playground, all four published (coat figures in two rounds, glass in one).

- Recipes: material paths were `Assets/Materials/...`; `setup` paths are relative to `Assets/`, now `Materials/...`.
- `coat-roughness`: the scene camera framed the pit's mixed balls small; now a close camera (fov 16) on one `PlasticBlue`
  ball inside the pit, sun behind the camera. Coat 0 gives a pin-point highlight, 0.5 a wide soft glow.
- `coat-normal-map`: had no setup; now `ClearcoatNormalMap` = `Textures/Concrete/Concrete034_NormalGL.jpg` and the base
  `NormalMap` removed, fov 10 on the same ball. Round 1 put the camera among the stacked balls. The dents show as small
  flecks in the coat's sheen around the sun; the highlight itself stays a soft blob (the coat's roughness widens where
  its normal changes quickly, as the page says).
- `glass-index`, `glass-thickness`: camera above the south wall (`Pit Wall South`, scale 0.3 along its normal) looking
  down into the pit, so the frame holds direct view, the wall's top edge and its face. `Thickness` 0.1 is 0.03 m on
  that wall (thickness scales with the instance), too small to see, so the figures use the sample's own `Thickness` 1
  (0.3 m). The top face's normal runs along the wall's 2.5 m height, so its path is long: that band refracts and tints
  most. The page's worked example (0.1, 0.047 sideways) is not what the figure shows; its words stay true.

Retaken 2026-11-23 at the pin v0.8.0 (319075e3), one round, recipes unchanged. `figures.py compare`: six pictures
identical to the published originals, `glass-thickness` `thin` off by one level in two pixels; publish kept every
file (the `thin` stamp records the check at 319075e3). Looked at again: the captions still hold.

Mended 2026-11-23 after a viewer's report, three takes at 319075e3:

- `coat-roughness` was unreadable (the variants differed in a 60 px patch). The proposed crop needs a
  `::figure{... crop}` directive on the page, which a photographer may not add, so the camera narrows instead
  (fov 16 to 7, same position and target): the halo is now about 130 px, the coat's point about 10 px, the 0.5 glow
  about 200 px; the metal, wooden and red balls stay at the corners. Probes taken and dropped: with `Clearcoat` 0 the
  same soft halo stays and the point goes; with base `Roughness` 1 the halo grows dimmer and wider and the point
  stays. So the halo is the base's own highlight, the point the coat's; the caption now says so.
- Material changes with `save: false` carry over between a figure's variants in one take (a probe after
  `Clearcoat` 0 still had no coat). Harmless here, since both variants set the same one property; a recipe whose
  variants set different properties must set every one in each variant.
- `coat-normal-map`: caption now opens by naming the concrete normal map on the coat alone; picture unchanged.

## Clerk

- Admitted to names.txt: Snell.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.
