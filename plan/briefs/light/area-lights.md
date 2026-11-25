# Brief: `light/area-lights`

| Field | Value |
| --- | --- |
| Title | Lights with size: sized highlights and area lights |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `light/many-lights`, `light/energy` |
| From | render-direct concept 12, 1.13; sized highlights (`GetSourceLobeAlpha2`, `GetLobeAlpha`, `RenderData::GetSunLobeAlpha2`); new: 0.8.0's rectangle lights (LTC shading, light surfaces, editor and script support; disk lights if stage 5 lands), the units of their intensity and how they convert to the quantities of `light/units-exposure`, and the clear coat under them; their soft shadows are `light/local-shadows`' · W8 |
| Unit | `plan/allocation/light.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `light/area-lights` — Lights with size: sized highlights and area lights

**Covers.** The problem: real lights have size, and a point light gives a pin-point highlight on a mirror. The
approaches: the representative point (Karis 2013), area lights shaded with linearly transformed cosines (Heitz 2016),
and widening the lobe (roughness modification), with a table. What the pin has: the sun's Angular Diameter and the
`SourceRadius` of point and spot lights widen only the distribution D and keep it normalized; a source of angular radius
t adds (tan t / 1.287)^2, less what the smallest roughness spreads already, to the lobe's alpha squared, and the same
formula runs on the CPU for the sun and on the GPU per pixel for bulbs. The rule: widen only D and renormalize, because
widening the visibility or skipping the normalization adds light; a source radius larger than the real bulb dims and
spreads the highlight, it does not soften the light. Figures: sweeps of the sun's Angular Diameter (0, 0.53 and 10
degrees) on a mirror sphere and of a point light's Source Radius (0, 0.05 and 0.3 m) on wet ground. "What Strata does
not do" at the pin: no disk lights, no diffuse light from a light's size. Then 0.8.0's rectangle lights, as the outline
describes them: their shading with linearly transformed cosines, the light surfaces, editor and script support, disk
lights if their stage lands, the units of their intensity and how they convert to the quantities of
`light/units-exposure`, and the clear coat under them; their soft shadows are `light/local-shadows`'. The exercises
sketch where a rectangle light enters `LightRecord`, `LightData`, the clusters and `ShadeLitSurface`, and compare the
sketch with the merged code, and trace the sun's Angular Diameter and a bulb's Source Radius to the lobe they widen.
Afterwards the reader can explain why a sized highlight keeps its energy, and choose between a sized point light and an
area light.

**Leaves out.**

- The soft shadows of rectangle lights → `light/local-shadows`
- The sun's soft shadow from its Angular Diameter → `light/sun-shadows-2`
- The clear coat in general → `light/clearcoat-transmission`
- Light units in general → `light/units-exposure`
- Placing area lights in a game → `make/lamps`
- Probe bakes that draw no highlights → `indirect/probes`

**Fit.** `fits`: about 4,980 words against L (5,000), with 0.8.0's rectangle lights as the outline gives them (about
2,200); the items at the pin fill about 2,800 with the two exercises. Phase B must read again: the rectangle lights'
components, records and LTC shading, the light surfaces, their units and conversion, the coat under them, disk lights
(stage 5), and whether the two not-done entries still hold.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-direct:61` | feature | home | Highlights of sized sources: D widened and kept normalized, for the sun's disk and for bulbs and flames |
| `render-direct:217` | feature | home | Area lights at the pin: none in `Strata/src` or `Strata/shaders`; what "area-like" lights main has |
| `render-direct:347` | concept | home | Sized sources and highlights: the approaches and the mistake of a large source radius |
| `render-direct:443` | code | home | `Strata/shaders/Include/PBR.slang:12-31`: `GetSourceLobeAlpha2`; with `GetLobeAlpha` at 119-124 and `RenderData::GetSunLobeAlpha2` at `Strata/src/Strata/Renderer/SceneRenderData.h:115-128` |
| `render-direct:535-536` | figure | home | Sweeps: the sun's Angular Diameter on a mirror sphere; a point light's Source Radius on wet ground (the Showcase's fire and lanterns) |
| `render-direct:593` | rule | home | Sized sources widen only D and keep it normalized |
| `render-direct:665` | hands-on | home | Exercise: sketch a rectangle light's path through the renderer, then compare with the merged code |
| `new:39` | hands-on | home | Exercise (trace it yourself): follow with a search the sun's Angular Diameter from the light into the frame constants through `RenderData::GetSunLobeAlpha2`, and a bulb's `SourceRadius` from `LightData::SpotAngles.w` into `GetSourceLobeAlpha2` in the cluster loop, both ending in `GetLobeAlpha`, which widens only D. Evidence: `Strata/src/Strata/Renderer/SceneRenderer.cpp:2573`; `Strata/src/Strata/Renderer/SceneRenderData.h:121`; `Strata/shaders/Scene/Forward.frag.slang:244`, `:276`; `Strata/shaders/Include/PBR.slang:121`, `:143` |
| `render-direct:707-709` | term | home | Source radius and angular diameter, lobe widening, area light and LTC |
| `render-direct:829` | open | home | Area lights and the local-lights stream were branches at the pin; phase B writes the page from 0.8.0 |
| `render-indirect:75` | feature | home | Sized highlights as render-indirect lists them (`render-direct:61`) |
| `render-indirect:454` | figure | home | The sun's sized highlight, Clear against Overcast on a mirror sphere (0.53 against 10 degrees), part of the Angular Diameter sweep |
| `render-indirect:477` | rule | home | A light's size widens only its highlight's D (`render-direct:593`) |
| `new:7` | not-done | home | Disk-shaped area lights (0.8.0 brings rectangle lights; disk lights only if their stage lands). Evidence: `git grep -nw LTC 822a7a46 -- Strata/src Strata/shaders` and `git grep -n -e AreaLight -e RectLight 822a7a46 -- Strata/src Strata/shaders` find nothing |
| `new:8` | not-done | home | Diffuse light from the size of point and spot lights: a light's size widens only its highlight. Evidence: `Docs/Roadmap.md:946-947, 1660`; `AGENTS.md:407-408`; `Docs/Releases/0.7.0.md:409-410` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| GGX's alpha and its normalized lobe | `light/brdf` | must |
| Energy conservation | `light/energy` | must |
| The forward light loop | `light/many-lights` | must |
| Light units | `light/units-exposure` | must |
| Solid angle and angular radius | `basics/math-sphere` | must |
| Linear transforms of directions | `basics/math-matrices` | must |
| The clear coat | `light/clearcoat-transmission` | helps |
| Soft shadows of local lights | `light/local-shadows` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `area-light` | Area light | - |
| `lobe-widening` | Lobe widening | - |
| `ltc` | LTC | - |
| `source-radius` | Source radius | angular diameter |
