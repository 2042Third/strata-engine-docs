# Brief: `basics/math-sphere`

| Field | Value |
| --- | --- |
| Title | Directions on a sphere: solid angles, spherical harmonics and octahedral maps |
| Kind | P |
| Size | L |
| Tracks | B, E |
| Needs | `basics/math-probability` |
| From | new by split of `basics/math-light`; solid angle, spherical coordinates, spherical harmonics, octahedral maps; home of the mathematics of spherical harmonics |
| Unit | `plan/allocation/basics-b.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `basics/math-sphere` — Directions on a sphere: solid angles, spherical harmonics and octahedral maps

**Covers.** In order: (1) directions as points on the unit sphere, and spherical coordinates: the polar angle from the
up axis and the azimuth around it (the yaw and pitch of `basics/math-rotations`, but measured from up), converted both
ways with sine, cosine, `acos` and `atan2`; (2) storing a value for every direction in a picture: the equirectangular
map with its rows of equal angle, and why it stretches at the poles (Strata's `DirectionToEquirect` guards
`atan2(0, 0)`); (3) cube maps: six square faces, the face chosen by the largest coordinate of the direction, and the
point on that face; (4) octahedral maps: the sphere wrapped in an eight-sided shape and unfolded into one square, and
the octahedral encoding of a unit vector into two numbers, read in Strata's `OctahedralEncode` and `OctahedralDecode`,
which store normals; (5) solid angle: the area a patch of directions covers on the unit sphere, the steradian, 4π for
the whole sphere and 2π for a hemisphere, the solid angle of a cone from its angular radius, 2π (1 - cos α), and of a
small disk such as the sun; (6) integrals over the sphere and the hemisphere: a value times the small solid angle of
each piece, added up, why a piece near the pole is smaller (sin θ), the cosine-weighted integral over a hemisphere that
equals π, the solid angle of one texel of a cube map, and directions drawn with a cosine-weighted density, read in
Strata's `SampleCosineHemisphere` (the Monte Carlo of `basics/math-probability`, on a sphere); (7) basis functions: a few
fixed patterns that, weighted and added, approximate a more complex one, first along a line; (8) spherical harmonics: the
patterns of bands 0, 1 and 2, nine coefficients, projecting a function onto them (the integral of the function times
each pattern) and evaluating it back, why they hold only light that changes slowly with direction, and the ringing that
can make values negative.

Figures: the polar angle and the azimuth on a sphere, an equirectangular map with its stretched poles, a cube map
unfolded, the octahedron unfolded, a cone's solid angle, the nine patterns of spherical harmonics. The common mistakes:
sin θ forgotten in a sum over the sphere, the poles of an equirectangular map, a normal stored as three numbers where
two would do, too few bands for sharp light. Practice (three to eight exercises, `style.md` §8) ends with the optional
Coin Run item: coins spread over a dome above the start, evenly by area, with the cosine of the polar angle drawn
uniformly by `Random`, against polar angles drawn uniformly, which bunch the coins at the top. "Where the book uses
it" names `light/units-exposure`, `light/sky`, `indirect/ibl`, `indirect/probes` and `indirect/gi-cascades`.

**Leaves out.**

- Radiance, irradiance and light units → `light/units-exposure`
- Strata's cube face conventions and its equirectangular captures → `indirect/ibl`
- Strata's probes with nine coefficients, their band factors and clamping → `indirect/probes`
- The GI field's octahedral probes → `indirect/gi-cascades`
- The normal buffer and screen-space reflections → `indirect/ssr`
- The sky's directions and the atmosphere's tables → `light/sky`
- Monte Carlo integration → `basics/math-probability`
- Yaw and pitch → `basics/math-rotations`

**Fit.** `fits`: about 5,200 words against L (5,000). The eight ideas at 300 to 600 words take the most (3,700); the
three short excerpts (450) and the fixed parts with the Test out box, Practice and the Coin Run item (1,100) take the
rest.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:109` | concept | home | The unit sphere of directions; spherical coordinates (polar angle and azimuth) and their conversions. Figure: the two angles. General knowledge. |
| `new:110` | concept | home | Equirectangular maps and their poles. Figure: an equirectangular map. General knowledge. |
| `new:111` | concept | home | Cube maps: six faces, the face from the largest coordinate. Figure: a cube map unfolded. General knowledge. |
| `new:112` | concept | home | Octahedral maps and the octahedral encoding of a unit vector. Figure: the octahedron unfolded. General knowledge. |
| `new:113` | concept | home | Solid angle, the steradian, a hemisphere, the solid angle of a cone from its angular radius. Figure: a cone's solid angle. General knowledge. |
| `new:114` | concept | home | Integrals over the sphere and the hemisphere: sin θ, the cosine-weighted integral equal to π, texel solid angles, cosine-weighted directions. General knowledge. |
| `new:115` | concept | home | Basis functions, first along a line. General knowledge. |
| `new:116` | concept | home | Spherical harmonics: bands 0 to 2, nine coefficients, projecting and evaluating, low frequencies only, ringing. Figure: the nine patterns. General knowledge. |
| `new:117` | code | home | `Strata/shaders/Include/Scene.slang:362-377`: `OctahedralEncode` and `OctahedralDecode`, a unit vector folded onto the octahedron and unfolded into [-1, 1]², and back |
| `new:118` | code | home | `Strata/shaders/Include/IBL.slang:59-65`: `SampleCosineHemisphere`, a cosine-weighted direction from two numbers, sin θ as the square root of one of them, turned into the normal's frame |
| `new:119` | hands-on | home | Coin Run practice, from `make/project-coin-run`'s end state: coins on a dome, evenly by area (the cosine of the polar angle uniform) against bunched (the angle uniform). Evidence: `StrataScriptCore/Include/StrataScript/Gameplay.h:81` (`Range` for floats), `StrataScriptCore/Include/StrataScript/Scene.h:192` (`InstantiateMany` with transforms) |
| `render-indirect:572` | term | home | Solid angle in steradians, 4π for the sphere; one glossary entry with the seed's |
| `render-indirect:585` | term | home | Spherical harmonics, nine coefficients in bands 0 to 2; one glossary entry with the seed's |
| `render-indirect:611` | term | home | Octahedral encoding, a unit vector in two numbers; beside the seed's octahedral map |
| `render-indirect:245` | concept | use | Strata's cube faces and equirectangular mapping, `DirectionToEquirect` (`Strata/shaders/Include/IBL.slang:28-34`) read for the pole; its home is `indirect/ibl` |
| `render-indirect:341` | code | link | The projection onto nine coefficients with texel solid angles, walked through on `indirect/ibl` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Monte Carlo integration and probability densities | `basics/math-probability` | must |
| Integrals as areas | `basics/math-change` | must |
| Sine, cosine, radians and `atan2` | `basics/math-vectors` | must |
| Vectors, length, normalizing and the dot product | `basics/math-vectors` | must |
| Random numbers with a seed (the SDK's `Random`) | `basics/math-probability` | must |
| Yaw and pitch as a direction | `basics/math-rotations` | helps |
| A cube face as a 90° view | `basics/math-projection` | helps |
| A frame of three axes as a matrix's columns, and a direction carried from a normal's frame to the world (tangent space) | `basics/math-bases` | helps |
| A script of the playground with `Log::Info` | `basics/programming-1` | must |

**Starting state.** The optional Coin Run item of Practice starts from the download of `make/project-coin-run`'s end
state, as the outline's introduction of part `basics` says for every primer after `basics/debugging`: Coin Run as
`make/project-coin-run` finishes it, with the rolling ball, the spinning coins, the HUD, the sounds, winning, losing and
the restart. The page's other examples and exercises run in the playground (`style.md` §8), which is no checkpoint.

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `basis-function` | basis function | - |
| `hemisphere` | hemisphere | - |
| `octahedral-encoding` | Octahedral encoding | - |
| `octahedral-map` | octahedral map | octahedral mapping |
| `solid-angle` | solid angle | - |
| `spherical-coordinates` | spherical coordinates | - |
| `spherical-harmonics` | spherical harmonics | SH |
| `steradian` | steradian | - |
| `unit-sphere` | unit sphere | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-basics-b-4 | should | order | `new:24` (`basics/math-bases`); `render-image:130`, `render-image:642` (`basics/color`); `render-scene:360` (`basics/signals`); `new:107`, `render-core:459` (`basics/math-probability`); `new:117`, `new:118`, `render-indirect:245` (`basics/math-sphere`) | Five pages quote Strata's shaders, which are written in Slang. No page before them teaches how to read Slang: `gpu/shaders` does, after part `basics` on track E and never on track B. No Assumes row names it, and style.md has a rule for Python fences but none for shader fences. The quotes rest on what differs from C++ and glm: `float3`, `float3x3` whose constructor takes rows (the point of `TangentBasis`), `mul`, swizzles such as `.yx`, `frac`, `select`, `reversebits`. | The first shader quote of each of the five pages is introduced by two or three sentences on what in it differs from C++ and glm, and each shader quote is followed by its explanation line by line, as R31 asks of Python (about 60 words a page). See forPlanner for a rule in style.md §9.1. | `allocation/basics-b.md:212`, `:697`, `:699`, `:779`, `:868`, `:878`, `:957-958`, `:963`; `allocation/gpu.md:189`, `:238`; `style.md:634-636`, `:679`; `tracks.md:208`; `Strata/shaders/Include/IBL.slang:41-48`; `Strata/shaders/Include/Common.slang:25-39`; `Strata/shaders/Include/Scene.slang:362-377` |
| critic-basics-b-15 | could | order | `new:119` on `basics/math-sphere` | The Coin Run item places the coins with `Scene::InstantiateMany`, which takes a list of matrices. No page on track B teaches it before: `make/scripting-scene` sends it to `make/performance`, on track G. | The item places each coin with `Scene::Instantiate` and a position, as `make/scripting-scene` teaches; or it builds the matrices with the TRS of `basics/math-matrices` and says what `InstantiateMany` does in two sentences (about 30 words). | `allocation/basics-b.md:959`; `allocation/make-a.md:1074`, `:1080`; `StrataScriptCore/Include/StrataScript/Scene.h:164`, `:188-192` |
| critic-basics-b-20 | could | order | `new:102` on `basics/math-probability` | Idea (7) takes a cosine-shaped density as its example of importance sampling. Densities over the hemisphere, with their sin θ, are taught on `basics/math-sphere`, the next page, and the Leaves out sends them there. If the example is the hemisphere's cosine weighting, the page uses what comes after it. | The row says that the example is a density on a line (cos x from 0 to π/2), and that cosine-weighted directions over the hemisphere are `basics/math-sphere`'s (`new:114`) (about 20 words). | `allocation/basics-b.md:812-814`, `:834`, `:863`, `:914-916`, `:954`; `allocation/indirect.md:399` |
