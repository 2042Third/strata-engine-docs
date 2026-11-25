# Brief: `light/reflectance`

| Field | Value |
| --- | --- |
| Title | How surfaces reflect light: the reflection equation and microfacets |
| Kind | C |
| Size | L |
| Tracks | E |
| Needs | `light/materials`, `basics/math-vectors`, `basics/math-probability`, `basics/math-sphere` |
| From | new; the theory the BRDF code needs first: render-direct concepts 6-7, render-indirect concepts 2-3 (radiance and irradiance in use, the reflection equation, Lambert, microfacets with D, G and F derived, Fresnel and F0 from IOR) |
| Unit | `plan/allocation/light.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `light/reflectance` — How surfaces reflect light: the reflection equation and microfacets

**Covers.** The problem as the reader meets it: light arrives at a point from one direction; how much leaves toward the
eye? The page shows a rough and a smooth sphere under one light, and water, glass and diamond side by side. The naive
answer, Phong's cosine power, breaks: it is not reciprocal, it adds energy and it has no Fresnel. The idea: radiance in,
radiance out, and the BRDF as their ratio per unit of irradiance; the reflection equation for one light (outgoing
radiance = BRDF times incoming radiance times the cosine), and for light from every direction as an integral over the
hemisphere (the full rendering equation is `indirect/problem`'s). Lambert's diffuse term, albedo over pi, with the pi
derived. Microfacets: a rough surface as many tiny mirrors; the distribution D (GGX, also called Trowbridge-Reitz: how
roughness widens it and why it is normalized), the masking-shadowing term G (Smith, height-correlated, folded with the
denominator into the visibility V), and the Fresnel term F (Schlick's approximation), each derived as far as the primers
carry E1. Fresnel and F0: reflectance rises toward grazing angles; a dielectric's F0 comes from its IOR as ((n - 1) / (n
+ 1))^2 (water 0.02, glass 0.04, diamond 0.17), a metal's from its albedo; diffuse light gets what the specular leaves.
The approaches engines use (Phong, Blinn-Phong, Cook-Torrance with Beckmann or GGX, Disney's principled model) end in a
table. Strata's choice: GGX, height-correlated Smith, Schlick, Lambert weighted by (1 - F)(1 - metallic), F0 from the
IOR clamped to [1, 3] and stored in the record; a bridge to `light/brdf`. What the choice cannot do: single scattering
loses energy at high roughness (`light/energy`). The common mistakes: forgetting the cosine, dividing diffuse by pi
twice or never, an uncorrelated Smith term, water taken for 4%. Figures: the microfacet diagram (D, G and F panels, the
Fresnel curve for 1.33, 1.5, 2.42 and metals) and the IOR sweep. Exercises: F0 and Schlick's F computed in a sketch and
compared with `GetDielectricF0`; D times the cosine integrated to 1 at two roughnesses. Afterwards the reader can write
the BRDF from its three parts and say what each does.

**Leaves out.**

- The BRDF in shader code → `light/brdf`
- Energy lost to multiple scattering → `light/energy`
- The full rendering equation and indirect light → `indirect/problem`
- Radiometric quantities and units → `light/units-exposure`
- Highlights of sized sources → `light/area-lights`
- Image light and the split sum → `indirect/ibl`

**Fit.** `fits`: about 5,150 words against L (5,000). D, G and F derived from zero take the most; the two exercises add
about 500.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-direct:313` | concept | home | The reflection equation for a single light and the BRDF; the mistakes |
| `render-direct:319` | concept | home | Fresnel, F0 and the index of refraction; the mistakes |
| `render-direct:45` | feature | home | F0 from IOR in Strata: n clamped to [1, 3], stored in `MaterialData::Absorption.w`, metals from the albedo (the literal 0.04 is `light/material-data`'s rule) |
| `render-direct:484` | figure | home | Diagram: the microfacet BRDF's anatomy, D widening with roughness, the Fresnel curves |
| `render-direct:530` | figure | home | Sweep: water (1.33), glass (1.5) and diamond (2.42); the Showcase's puddles at 1.33 |
| `render-direct:674-681` | term | home | BRDF, microfacet, GGX, Smith visibility, Fresnel and Schlick, F0, IOR, Lambert |
| `render-direct:56` | feature | use | GGX, Smith, Schlick and Lambert as Strata's choice; the code is `light/brdf`'s |
| `render-indirect:237`, `render-indirect:241` | concept | home | Radiance, irradiance, solid angle and cosine weighting in use; the microfacet recap (GGX, Smith, Fresnel, F0, roughness against alpha) |
| `render-indirect:74` | feature | home | F0 from IOR as render-indirect lists it, taught with `render-direct:45` (passed to `light/material-data`, whose excerpt computes it) |
| `render-indirect:432` | figure | home | Dielectric spheres at IOR 1.33, 1.5 and 2.42 (`lookdev.ior`); with `render-direct:530`, one sweep |
| `render-indirect:578` | term | home | GGX and alpha ("alpha" gets an entry of its own); perceptual roughness links its one entry on `light/materials` (`render-direct:673`) |
| `new:29` | hands-on | home | Exercises: a sketch that computes F0 from the IOR for water, glass and diamond and Schlick's F at 60 and 85 degrees, compared with what `GetDielectricF0` returns (0.04 written out at 1.5); predict, then check with a sketch, that GGX's D times the cosine integrates to 1 over the hemisphere at roughness 0.2 and 0.6 while its peak falls. Evidence: `Strata/src/Strata/Renderer/MaterialData.cpp:51-59`; `Strata/shaders/Include/PBR.slang:33-57` |
| `render-indirect:470` | rule | use | Diffuse gets what specular leaves |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Radiance, irradiance and the light units | `light/units-exposure` | must |
| The material model | `light/materials` | must |
| Vectors, dot products, angles, sine and cosine | `basics/math-vectors` | must |
| Solid angle and integrals over the hemisphere | `basics/math-sphere` | must |
| Integrals as areas | `basics/math-probability` | must |
| Powers and the exponential function | `basics/numbers` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `alpha` | alpha | - |
| `brdf` | BRDF | - |
| `f0` | F0 | - |
| `fresnel` | Fresnel | Fresnel (Schlick) |
| `ggx` | GGX | Trowbridge-Reitz |
| `ior` | IOR | - |
| `lambert` | Lambert | Lambert diffuse |
| `microfacet` | Microfacet | - |
| `reflectance` | reflectance | - |
| `schlick-approximation` | Schlick approximation | - |
| `smith-visibility-height-correlated` | Smith visibility (height-correlated) | - |
