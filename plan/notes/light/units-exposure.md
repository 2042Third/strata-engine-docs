# Notes: light/units-exposure

## New terms

None proposed. The seven glossary terms homed here (candela, irradiance, lumen, lux, nit, radiance, sun-to-sky ratio) are defined in bold.

## Requests

- Extra words: nm (units), watt, watts, joule, radiometry, radiometric, photometry, photometric, illuminance, emissive, albedo (if absent), Frostbite, Filament (names), Lagarde, Rousiers.
- Hosts for Further reading (cited without links): the SIGGRAPH course notes host of the Frostbite 2014 talk, the Filament documentation host, the Unreal documentation host, the Blender manual host.
- Figure `equal-pair` (kind scene, a compare of two variants): the Basic 3D scene with a cube, the sky light turned off, sun at 65536 lux and manual exposure -16 versus sun at 1 lux and manual exposure 0. The entity names `Sun` and `Sky` and the component names `DirectionalLight` and `SkyLight` follow the other figures of the book; the sky light's `Intensity` of 0 is accepted by the pin (not tried).

## Not verified

- That `component.set` accepts `SkyLight` `Intensity` 0 and `DirectionalLight` `Intensity` 65536 on the Basic 3D template's entities.
- That the Basic 3D template contains an entity named `Sky`.
- Statements about Frostbite, Unreal, Filament and Blender (units they use) come from memory of their public documents, not from the engine.
- The sun disk's 1.3 billion nits is the Developer Guide's figure; the page's own check (100,000 lux over 6.7e-5 steradians gives 1.5e9) is arithmetic.
- The wording "inverse-square law" and the 683 lm/W peak of the eye's weighting are general physics, not checked at the pin.

## Findings not applied

- The brief's pre-exposure of 2^-19 for the half-float diagram: the page uses 2^-15, the power of two nearest the manual exposure -14.58 of the Basic 3D sun, which the pin's rule (nearest power of two to 2^Exposure) gives.
- Brief item `render-direct:433` (excerpt of the comment, lines 17-20): shown as a block quote, not a code excerpt, since a code fence would need the struct's C++ taught outside the page's closure.
- The units map's "pi L = E" and the reference table on a log scale are a Mermaid flow and a table with a powers-of-ten column, not pictures.

## Figures

- `equal-pair` (scene, round 1, published): the recipe as written, the Basic 3D template's camera. Both variants show
  the cube at the origin with its hard shadow to the left on the dark ground, the sky black (sky light at 0). A
  pixel compare of the two PNGs found 0 differing bytes, so the page's "down to the last bit" holds at the pin. Alt
  and shows were rewritten to name the black sky and the identical pixels. The picture is dim (1 lux equivalent on a
  0.16 albedo ground), which is what the page's numbers give; the cube's shading and shadow stay readable.
- `equal-pair`, v0.8.0 (319075e3), round 1: taken again with the recipe unchanged. `figures.py compare` against the
  published originals: 0 of 2 pictures differ (0 differing pixels), and the two variants' PNGs are byte-identical, so
  "down to the last bit" still holds. The picture, caption and alt are as before; `publish` left both files and their
  stamps unchanged (same original).

## Since

0.6.0: the inventory dates the photometric units and the reference table to 0.6.0 (`render-direct` lines 101 and 105).

0.8.0 (pin move): the sentence on rectangle lights now states their units, checked at the pin: `RectLightComponent::Intensity` is nits or lumens by its `Units` (default Nits, 25), in `Strata/src/Strata/Renderer/RendererComponents.h` and the tooltips of `RendererComponents.cpp`. `Renderer.LightUnits` lists only the sun, point, spot and sky lights, so the test paragraph names those instead of "every light"; the lumens bullet now names point and spot lights.

## Clerk

- Admitted to extra-words.txt: illuminance, radiometry, radiometric, photometry, photometric, emissive, joule, watt, watts, nm.
- Admitted to names.txt: Frostbite, Filament, Rousiers.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.
