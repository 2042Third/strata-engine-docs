# Brief: `light/fog`

| Field | Value |
| --- | --- |
| Title | Height fog |
| Kind | I |
| Size | M |
| Tracks | E |
| Needs | `light/atmosphere` |
| From | render-direct ch. 11; 1.9 (the closed-form integral, its lighting, the sky at infinity, `c_MinHeightFalloff`, what a fog without volume cannot do) |
| Unit | `plan/allocation/light.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `light/fog` — Height fog

**Covers.** The job: haze that thickens toward the ground, computed in closed form per pixel without a pass. The problem
and the approaches: distance fog, analytic height fog (Wenzel 2006, Unreal's exponential height fog), froxel volumetric
fog (Wronski 2014), with a table. The component `HeightFogComponent` in code: `Density`, `HeightFalloff`, `BaseHeight`,
`StartDistance`, `MaxOpacity`, `Color` as an albedo, `ColorFromSky`, `SunScattering`; the first active one applies, and
`SetHeightFog` keeps every value finite and subtracts the camera's height in double. The integral: the density falls as
exp(-falloff h); along a view ray it integrates in closed form (the diagram of density, ray and optical depth), written
so that no term overflows; the sky is fogged at an infinite distance; a falloff of 0 would make the integral toward the
sky endless, hence `c_MinHeightFalloff`. The fog's light: the sky's (the procedural horizon, an environment map's
irradiance from above, the atmosphere's horizon toward the ray, or the ambient color) and the sun's through the
Henyey-Greenstein phase. The fog is applied after aerial perspective. Its limits: no volume, so no light shafts, no
local lights and no shadows in fog ("What Strata does not do"). A toy compares the numeric and the closed-form integral.
Figures: sweeps of density and falloff, `SunScattering` 0 against 1 toward the sun, `ColorFromSky` off and on,
`MaxOpacity`, with a crop at the horizon. How it is tested: `GPU.SceneRenderer.Fog` (the integral matched, the sky at
infinity, density 0 bit-identical). Exercises: a valley fog tuned by its numbers; a second exponential layer added end
to end with an analytic test; a trace of `Density` from the component to the forward pass and the sky. Afterwards the
reader can tune fog by its parameters and derive its integral.

**Leaves out.**

- Extinction, transmittance and phase functions → `light/atmosphere`
- Aerial perspective → `light/atmosphere`
- Height fog in a game's look → `make/look`
- The first active component of a kind → `world/reflection`

**Fit.** `over`: about 4,500 words against M (3,000). The integral derived from zero, three excerpts and three exercises
pass M's top; by S2 the page takes L (5,000), whose range holds it.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-direct:167-169` | feature | home | The height fog component, the analytic integral, the fog's lighting |
| `render-direct:171` | feature | home | The fog's limits: no volume, no shafts, no local lights, no shadows |
| `render-direct:410` | concept | home | Fog: exponential height fog and aerial perspective; the mistakes |
| `render-direct:466` | code | home | `Strata/shaders/Include/Fog.slang:16-110`: the optical depth that cannot overflow, the in-scattering with Henyey-Greenstein, the blend, the sky at infinity |
| `render-direct:515` | figure | home | Diagram: the density against height, a view ray, the optical depth, the blend |
| `render-direct:560` | figure | home | Sweeps: density, falloff, `SunScattering` 0 against 1 toward the sun, `ColorFromSky` off and on, `MaxOpacity` |
| `render-direct:620-621` | rule | home | Height fog needs a falloff above 0; fog is not a volume |
| `render-direct:646` | hands-on | home | Exercise: valley fog, base at the floor, a 50 m layer, density that hides half at 35 m |
| `render-direct:663` | hands-on | home | Exercise: a second exponential layer end to end with an analytic test and a feature-test entry |
| `new:54` | hands-on | home | Exercise (trace it yourself): `HeightFogComponent::Density` followed with a search from the component through `SetHeightFog`, which fills the frame's `Fog*` constants, to `ApplyHeightFog` in the forward pass and `ApplyHeightFogToSky` behind it. Evidence: `Strata/src/Strata/Renderer/SceneRenderer.cpp:1405`, `:3296`; `Strata/shaders/Include/Fog.slang:7`, `:85`, `:100`; `Strata/shaders/Scene/Forward.frag.slang:445`; `Strata/shaders/Scene/Skybox.frag.slang:48` |
| `render-direct:753` | term | home | Height fog |
| `new:17` | not-done | home | Volumetric fog, light shafts and fog volumes: height fog has no volume. Evidence: `Strata/src/Strata/Renderer/RendererComponents.h:126-129`; `Strata/shaders/Include/Scene.slang:13-14` (SRVs 34 and 36 reserved); `Docs/Roadmap.md:948` |
| `new:18` | code | home | `Strata/src/Strata/Renderer/RendererComponents.h:126-151`: `HeightFogComponent`, its fields and `c_MinHeightFalloff` |
| `new:19` | code | home | `Strata/src/Strata/Renderer/SceneRenderer.cpp:1395-1445`: the first active fog, its values kept finite, the camera's height in double, which light the fog scatters |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Extinction, transmittance and the Henyey-Greenstein phase | `light/atmosphere` | must |
| Exponentials and their integrals | `basics/math-interpolation` | must |
| Overflow and the range of floats | `basics/numbers` | must |
| Where fog applies in the forward shader | `light/brdf` | must |
| Components and the first active one | `world/reflection` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `height-fog` | Height fog | - |
