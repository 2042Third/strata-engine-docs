# Brief: `light/units-exposure`

| Field | Value |
| --- | --- |
| Title | Light by the numbers: radiometric and photometric units |
| Kind | C |
| Size | L |
| Tracks | E |
| Needs | `gpu/frame-tour`, `basics/numbers`, `basics/color`, `basics/math-sphere` |
| From | render-direct ch. 1; 1.5 (radiometry; lumen, candela, lux and nit conversions; the spot rule; the sun-to-sky ratio; the reference table; one paragraph on why the HDR target needs a pre-exposure); one sentence that 0.8.0's rectangle lights have units of their own, which `light/area-lights` gives (a movable claim, read again at the pin move to v0.8.0); home of "light in real units" |
| Unit | `plan/allocation/light.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `light/units-exposure` — Light by the numbers: radiometric and photometric units

**Covers.** The page opens with an experiment: the same scene lit by a 65,536 lux sun at exposure -16 and by a 1 lux sun
at exposure 0 gives the same image, so the numbers of light only mean something together with their units. Then
radiometry from zero: power, and the four quantities (flux, intensity, irradiance, radiance) on one diagram, each with
the solid angle or the area it is "per". Then photometry: the eye's weighting turns watts into lumens, and the four
photometric twins are lumen, candela, lux and nit. Worked conversions follow: a point light of P lumens has P / 4 pi
candela; a white diffuse surface under E lux has a luminance of E / pi nits; a spot light's candela is along its axis,
so a narrower cone does not brighten it, and P / (2 pi (1 - cos t)) keeps its lumens. The approaches engines use come
next (arbitrary "intensity", radiometric watts, photometric units as in Frostbite 2014, Unreal's physical units and
Filament), with a table of their costs. Strata's choice is photometric units on one scale with no hidden factor: lux for
the sun, candela for points and spots, nits for the sky, the ambient color and emission, read 1:1 from glTF; the page
shows the comment of `RendererComponents.h` that states it and the `Renderer.LightUnits` check. The reference table of
real values (sun, sky, overcast day, office, moon, lamp, candle, monitor) is placed on a log scale, and the sun-to-sky
ratio is defined as a quantity (its measurement is `light/measuring-light`'s). One paragraph and one diagram say why the
HDR target needs a pre-exposure: a 100,000 lux sun and a 1.3e9-nit sun disk do not fit half floats, and a power-of-two
scale fixes that exactly (the mechanism is `image/pre-exposure`'s). Both halves are `book.md`'s design decision "Light
is measured in real units, and a pre-exposure keeps the HDR values in range", stated once with its reason in a `:::why`
aside of about 80 words (`image/pre-exposure` names it and links back). One sentence says that 0.8.0's rectangle lights
have units of their own, which `light/area-lights` gives (a movable claim, read again at the pin move). The common
mistakes close the page: lumens taken for candela, a narrower cone expected to brighten, a 3 lux default sun mixed with
a real 120,000 lux one. The page's example is the Basic 3D template's sun with one lamp beside it; its exercise builds a
night scene from the reference values. Figures: no switch, so two diagrams (the units map and the half-float range) and
the equal pair of images. Afterwards the reader can convert between lumens, candela, lux and nits, read any light field
of Strata as a physical quantity, and say why a sunlit frame needs a pre-exposure.

**Leaves out.**

- Exposure, EV100, metering and the exposure key → `image/exposure`
- How the pre-exposure is chosen and kept exact → `image/pre-exposure`
- The light components, falloff and cones → `light/lights`
- Measuring luminance and the sun-to-sky ratio in a scene → `light/measuring-light`
- The units of rectangle lights → `light/area-lights`
- Lighting a scene with real values in the editor → `make/lighting`
- Linear and sRGB values and the half-float range as such → `basics/color`

**Fit.** `fits`: about 4,150 words against L (5,000). Radiometry and photometry taught from zero, with worked
conversions, take most of the page; it holds no code excerpt of its own.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-direct:278` | concept | home | Light as a quantity: radiometric and photometric units, the approaches engines use, Strata's choice and the mistakes |
| `render-direct:101` | feature | home | Photometric units on one scale with no hidden factor; the `Renderer.LightUnits` test that the tooltips name units |
| `render-direct:105` | feature | home | The reference values table (sun, sky, overcast, office, moon, lamp, candle, monitor), on a log scale |
| `render-direct:571` | rule | home | Every intensity has a unit, and nothing rescales it (imported glTF lights read 1:1) |
| `render-direct:573` | rule | home | A spot light's candela is along its axis; P / (2 pi (1 - cos t)) keeps its lumens |
| `render-direct:480` | figure | home | Diagram: the units map (lux on a surface, candela along a direction, nits off a surface), pi L = E, I = P / 4 pi, the reference values on a log scale |
| `render-direct:482` | figure | home | Diagram: the half-float range and a sunlit scene's values before and after a pre-exposure of 2^-19, for the paragraph on why |
| `render-direct:539` | figure | home | The same scene at 65,536 lux and exposure -16 and at 1 lux and exposure 0: equal images (the mirror of the units test) |
| `render-direct:640` | hands-on | home | Exercise: a night scene with a 0.2 lux moon, a 64 cd lamp (800 lm) and a 1 cd candle, exposure set from the reference table |
| `render-direct:695-698` | term | home | Lux, candela, nit and lumen (four glossary entries) |
| `render-direct:755` | term | home | The sun-to-sky ratio as a quantity |
| `new:26` | concept | home | The design decision "Light is measured in real units, and a pre-exposure keeps the HDR values in range", in the page's `:::why` aside (about 80 words): the shading computes photometric quantities on one scale with no factor between them, so real values and glTF lights work as they are and exposure maps them to the display; a sunlit frame's values do not fit the half-float target, so a power-of-two pre-exposure scales them exactly. Evidence: `Docs/DeveloperGuide.md:4005-4006`, `:5322-5323`, `:5335-5336`, `:5365-5372` |
| `render-image:97` | feature | home | The light units that feed exposure, as render-image lists them |
| `render-image:641` | term | home | Nit, lux and candela as render-image defines them (one glossary entry each, shared with `render-direct:695-697`) |
| `render-indirect:570-571` | term | home | Irradiance and radiance as radiometric quantities |
| `render-direct:433` | code | use | The comment of `RendererComponents.h:17-20` that gives each light's unit; the excerpt's home is `light/lights` |
| `render-direct:106` | feature | use | The Basic 3D template's 120,000 lux sun as the page's daylight example; its home is `make/lighting` |
| `render-direct:102` | feature | link | Exposure maps the scene's units to the display; its home is `image/exposure` |
| `render-direct:103` | feature | link | The pre-exposure, in one paragraph on why; its home is `image/pre-exposure` |
| `render-indirect:237` | concept | use | Radiance, irradiance and solid angle, as render-indirect lists them; the outline gives the concept to `light/reflectance` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Powers, logarithms and the exponential function | `basics/numbers` | must |
| Solid angle and the steradian | `basics/math-sphere` | must |
| Linear color and the luminance of an RGB value | `basics/color` | must |
| The half-float range | `basics/color` | must |
| The HDR target the scene renderer writes | `gpu/frame-tour` | must |
| Integrals as areas (flux summed over directions) | `basics/math-probability` | helps |
| Exposure and EV100 | `image/exposure` | helps |
| How the pre-exposure is chosen | `image/pre-exposure` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `candela` | Candela | cd |
| `irradiance` | Irradiance | - |
| `lumen` | Lumen | lm |
| `lux` | Lux | lx, nits |
| `nit` | Nit | - |
| `radiance` | Radiance | - |
| `sun-to-sky-ratio` | Sun-to-sky ratio | - |
