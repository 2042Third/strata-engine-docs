# Brief: `light/sky`

| Field | Value |
| --- | --- |
| Title | The sky as a light: sources, sun extraction and presets |
| Kind | I |
| Size | M |
| Tracks | E |
| Needs | `light/lights`, `assets/texture-cooking` |
| From | render-direct ch. 10; 1.8 (source rows: the three sky sources, the procedural sky, environment maps, Extract and Remove Sun, presets with `groundIlluminance`, the sun-to-sky ratio), concept 19 |
| Unit | `plan/allocation/light.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `light/sky` — The sky as a light: sources, sun extraction and presets

**Covers.** The job: light the scene from every direction by the sky, and draw the sky behind it. This page carries the
full section on the problem for itself and `light/atmosphere`: constant ambient light, HDR photographs, analytic skies
(Preetham, Hosek-Wilkie) and physical atmospheres (Bruneton 2008, Hillaire 2020), with a table. The component
`SkyLightComponent`: the first active one applies; `Source` (EnvironmentMap, Procedural, Atmosphere), `Intensity`,
`Rotation`, `ShowBackground`, `BackgroundBlur`, an `AmbientColor` in nits for a scene without an environment, the
procedural colors, the sun's size and intensity; inactive reasons per source; the atmosphere's own fields
(`AtmosphereDensity`, `AtmosphereHaze`, `GroundAlbedo`, `AerialPerspective`, `AerialPerspectiveScale`) are named and
linked to `light/atmosphere`, which teaches them. The code that picks the source each frame, with the constant ambient
used until a map arrives. The environment-map source: an equirectangular HDR texture turned into a 512 cube, then the
filter chain every source shares (the chain is `indirect/ibl`'s). The procedural sky: a zenith, horizon and ground
gradient in nits with the sun's disk where the directional light comes from, recomputed only when its parameters change.
The presets Clear, Hazy, Overcast and GoldenHour as real values in code: a sky and a sun in one undo step, automatic
exposure on with MaxEV 16, and the `groundIlluminance` they return. Extract Sun and Remove Sun: an HDR map's sun becomes
the shadow-casting directional light, and the importer paints it out of the map (the `HDRSun` setting is
`assets/texture-cooking`'s); the mistake of a double sun. What Strata does not do here: no clouds, stars or moon (the
atmosphere's haze is clear aerosol, and the Overcast preset is a nearly uniform procedural sky). A toy gradient sky in
30 lines. Figures: the three sources side by side, the four presets on Basic 3D as a sweep, an HDR map before and after
Extract Sun with Remove Sun (shadows appear). How it is tested: `GPU.ProceduralSky`, `Editor.Lighting`. Exercises: each
preset on Basic 3D with `groundIlluminance` and the sun-to-sky ratio read from the Lighting view; Extract Sun on an HDR
map; a trace of `lighting.applySkyPreset` to its values and its one undo step. Afterwards the reader can choose a sky
source, apply a preset, extract a sun, and say what each source computes.

**Leaves out.**

- The physical atmosphere → `light/atmosphere`
- The sky light's atmosphere fields (density, haze, ground albedo, aerial perspective) → `light/atmosphere`
- The environment filter chain and image-based light → `indirect/ibl`
- The exposure settings the presets change → `image/exposure`
- The `HDRSun` import setting → `assets/texture-cooking`
- The sun-to-sky ratio as a measurement → `light/measuring-light`
- Choosing a sky in a game → `make/lighting`

**Fit.** `over`: about 4,400 words against M (3,000). Three sources, the presets, Extract Sun, three excerpts and three
exercises pass M's top; by S2 the page takes L (5,000), whose range holds it.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-direct:151-153` | feature | home | The sky light component, the environment-map source, the procedural sky; the component's atmosphere fields (`AtmosphereDensity`, `AtmosphereHaze`, `GroundAlbedo`, `AerialPerspective`, `AerialPerspectiveScale`) are named here and linked to `light/atmosphere`, which teaches them |
| `render-direct:159-160` | feature | home | The sun and sky presets; Extract Sun and Remove Sun |
| `render-direct:396` | concept | home | The sky as a light source: approaches, Strata's three sources into one chain, the double-sun mistake |
| `render-direct:555` | figure | home | The three sky sources side by side in one scene |
| `render-direct:558` | figure | home | Sweep: Clear, Hazy, Overcast and GoldenHour on Basic 3D |
| `render-direct:564` | figure | home | Off and on: an HDR map with its sun, before and after Extract Sun and Remove Sun |
| `render-direct:639` | hands-on | home | Exercise: each preset, `groundIlluminance` and the sun-to-sky ratio from the Lighting view's legend |
| `render-direct:648` | hands-on | home | Exercise: Extract Sun, shadows appear and the sky no longer lights twice |
| `new:49` | not-done | home | Clouds, stars and a moon: the atmosphere's haze is clear aerosol, and the Overcast preset is a nearly uniform procedural sky (about 70 words). Evidence: `Strata/src/Strata/Renderer/SkyPresets.cpp:35-37`; `git grep -niwE -e moon -e stars -e starfield -e "clouds?" 822a7a46 -- Strata/src Strata/shaders` finds only that comment, a tooltip's full-moon illuminance (`Strata/src/Strata/Renderer/RendererComponents.cpp:289`) and two comments on cloud placeholder files (`Strata/src/Platform/Windows/WindowsFileSecurity.h:28`, `Strata/src/Strata/Core/Platform.h:104`) |
| `new:50` | hands-on | home | Exercise (trace it yourself): `lighting.applySkyPreset` followed with a search from its registration to `GetSkyPresetValues` and the one `SceneEditTransaction` that makes its undo step. Evidence: `StrataEditor/src/Editor/EditorLightingCommands.cpp:638-641`, `:953`; `Strata/src/Strata/Renderer/SkyPresets.cpp:83` |
| `render-direct:742-743` | term | home | Environment map (equirectangular HDR), procedural sky |
| `new:14` | code | home | `Strata/src/Strata/Renderer/SceneRenderer.cpp:927-1029`: `UpdateEnvironment`, the first active sky light, its three sources, the constant ambient until a map arrives |
| `new:15` | code | home | `Strata/shaders/IBL/ProceduralSky.comp.slang:23-51`: the procedural gradient and the sun's disk with its edge smoothed over a texel |
| `new:16` | code | home | `Strata/src/Strata/Renderer/SkyPresets.cpp:20-59`: the presets as real values (sun illuminance above the air, elevations, the overcast sky in nits) |
| `render-image:99` | feature | home | What the presets do to exposure: manual exposure made automatic, MaxEV raised |
| `render-indirect:53` | feature | home | The sky light component as render-indirect lists it (`render-direct:151`) |
| `render-indirect:63-64` | feature | home | Extract Sun and Remove Sun, and the sky presets, as render-indirect lists them (`render-direct:159-160`) |
| `assets:157` | feature | home | The HDR sun finder (`HDRSun::Find` and `Remove`): it finds the sun in an equirectangular sky, measures its illuminance and paints it out |
| `assets:511` | figure | home | An HDR sky with and without `RemoveSun`, with `lighting.extractSun`; with `render-direct:564`, one figure |
| `render-direct:196` | feature | link | `EnvironmentResolution`, the prefiltered sky's size; its home is `indirect/ibl` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Nits and lux | `light/units-exposure` | must |
| The directional light and preview lighting | `light/lights` | must |
| HDR textures and their import | `assets/texture-cooking` | must |
| Directions on a sphere, equirectangular and cube maps | `basics/math-sphere` | must |
| Loading assets and "not loaded yet" | `assets/loading` | must |
| Compute shaders | `gpu/compute` | must |
| The environment filter chain | `indirect/ibl` | helps |
| Exposure and MaxEV | `image/exposure` | helps |
| Commands and undo steps | `editor/commands` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `environment-map-equirectangular-hdr` | Environment map (equirectangular HDR) | Environment map |
| `procedural-sky` | Procedural sky | - |
