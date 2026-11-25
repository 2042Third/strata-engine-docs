# Brief: `indirect/ibl`

| Field | Value |
| --- | --- |
| Title | Image-based lighting and the split sum |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `light/energy`, `light/sky`, `basics/math-sphere`, `gpu/compute` |
| From | render-indirect ch. 2; 1.1 (the sky's sources as cube maps, the filter chain, filtered importance sampling, the budget, shared environments, constant ambient, the atmosphere cube); the split sum's prefiltered half, reusing `light/energy`'s table; home of the horizon fade |
| Unit | `plan/allocation/indirect.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `indirect/ibl` — Image-based lighting and the split sum

**Covers.** The job: turn the sky, whatever its source, into image light that every surface can read in one or two
texture reads. Strata does it with one chain for every source: an environment cube, an irradiance cube and a
prefiltered cube. The sky's own look and its sources are `light/sky`'s; the BRDF table is `light/energy`'s.

The problem section stays within a fifth of the page and teaches three ideas from zero. Environment maps: an
equirectangular image against a cube map, the face conventions (`CubeTexelDirection`), a texel's solid angle, and the
guard for `atan2(0, 0)` at the pole. Diffuse image light: the environment convolved with a cosine lobe, stored as a
small cube (the sky, 32 texels a face), as nine spherical-harmonic coefficients (the probes, `indirect/probes`) or as an
ambient cube (the GI field, `indirect/gi-cascades`). Specular image light and the split sum (Karis 2013): prefiltered
radiance per roughness level, with N = V = R assumed, times `light/energy`'s table of scale and bias of F0; where the
split sum fails (grazing angles; no stretched reflections).

The map is the filter-chain diagram: a source (an HDR map, the procedural sky, the atmosphere) becomes mip 0 of a
512-texel cube; `CubeDownsample` makes its levels; `Irradiance.comp` and `Prefilter.comp` make the irradiance cube and
six prefiltered levels for roughness 0 to 1 in steps of 0.2, at the quality row's `EnvironmentResolution`. The page
shows how each source becomes the cube: `EquirectToCube` for maps, `ProceduralSky.comp` recomputed only when its
parameters change (the `EnvironmentUpdates` statistic), and the atmosphere's cube, which the atmosphere refreshes over
14 frames (`light/atmosphere` teaches the refresh). A toy version convolves a tiny cube on the CPU. The real code
follows the data: `FilterEnvironment` and its steps, then the prefilter shader with filtered importance sampling (a
sample reads the source mip that matches its solid angle, so 512 samples give no noise), its sample budget
(`GetPrefilterSamples`), then the irradiance shader. Shared environments (`FindSharedEnvironment`) let renderers reuse
one texture's maps. Without an environment, the constant `AmbientColor` lights diffuse only. While a sky's map loads (it
is requested at High priority), the constant ambient lights the frame and the map counts as pending; the renderer holds
the map whole until the chain has read it, and then it drops to its mip tail, the same idea as a probe's capture hold
(`indirect/probes`); a new `EnvironmentResolution` filters the prefiltered cube again from the radiance cube, never from
the map, whose levels are gone. In the forward pass the surface reads the irradiance along its normal and the
prefiltered radiance along R at `roughness` times `EnvironmentParams.z`; the horizon fade then removes image light that
a normal map turned below the geometric surface, by `clamp(1 + R . Ng / 0.25, 0, 1)` squared, which reaches 0 about 15
degrees below it (this page is its home).

Alternatives Strata did not choose: SH-9 for the sky too, per-pixel importance sampling at run time, offline
prefiltering tools, octahedral environment maps. What Strata does not do here: cube-map texture assets (skies and probe
captures are equirectangular HDR textures, made into cubes at run time); it links `appendix/not-in-strata`. How it is
tested: `GPU.ProceduralSky` and the furnace tests (`light/energy`). Changing it safely: the `EnvironmentResolution` row
(256 at Low and Medium, 512 at High and Ultra, any other value clamped to 256) with its memory (`EnvironmentBytes`: six
RGBA16F faces with six levels, and a second set under the atmosphere while the sun moves) and no GPU stage of its own,
because the chain runs only when the sky changes; every source through the same chain; and a `:::history` of the
releases (image light from HDR maps and the procedural sky since 0.3.0, the atmosphere in 0.6.0, 512-texel prefiltering
at High and the horizon fade in 0.7.0). Figures: the sky source as a sweep (Procedural, Environment Map, Atmosphere, and
the constant ambient as "off") on a white sphere and rough and smooth metal spheres, their Indirect view
(`light/measuring-light`'s), the roughness sweep of a mirror ball, and five diagrams, the horizon fade among them (no
capture switch turns it off). The exercises trace a change of the procedural sky to the prefiltered cube and break, in a
patch, the rule that a still sky makes no new cube. The reader can then explain and change the chain.

**Leaves out.**

- The sky light component, the sky's sources, presets and Extract Sun → `light/sky`
- The physical atmosphere and its tables → `light/atmosphere`
- The BRDF table, directional albedo and energy compensation → `light/energy`
- The mathematics of spherical harmonics and solid angles → `basics/math-sphere`
- Where the sky's image light meets probes, SSR and GI in the shader → `indirect/seam`
- Reflection probes, which reuse the chain → `indirect/probes`
- The `EnvironmentResolution` row among the presets → `image/quality-settings`

**Fit.** `fits`: about 6,100 words against L (5,000). Three concepts from zero, four excerpts with the chain's steps and
seven figures, five of them diagrams, take the most words; about 400 words remain below L's top.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-indirect:245` | concept | home | Environment maps and cube maps: equirectangular against cube, the face conventions (`CubeTexelDirection`, `Include/IBL.slang:10-24`), a texel's solid angle; errors: face orientation, the pole of an equirectangular map (`atan2(0, 0)`, guarded at `IBL.slang:30-33`) |
| `render-indirect:249` | concept | home | Diffuse image light: the cosine convolution and its three stores (irradiance cube, SH-9, ambient cube) and which part of Strata uses which; errors: the band factors, negative ringing |
| `render-indirect:254` | concept | home | Specular image light and the split sum: prefiltered radiance per roughness (N = V = R) times the BRDF table; 6 levels, mip from `roughness * EnvironmentParams.z`; where it fails |
| `render-indirect:54` | feature | home | The procedural sky as a cube: written into mip 0, recomputed only when `ProceduralSkyParameters` change (`EnvironmentUpdates`); its colors and sun disk are `light/sky`'s |
| `render-indirect:55` | feature | home | `EquirectToCube` and `DirectionToEquirect` (`IBL.slang:28-34`): maps and probe captures into cubes |
| `render-indirect:56` | feature | home | The one filter chain for every source: cube mips, irradiance (32 a face, 256 cosine samples), 6 prefiltered levels at `EnvironmentResolution` (256 Low and Medium, 512 High and Ultra) |
| `render-indirect:57` | feature | home | Filtered importance sampling: the source mip from the sample's solid angle against the texel's |
| `render-indirect:58` | feature | home | The prefilter budget `GetPrefilterSamples`: 512 at 256; at 512, 128 for levels 1 and 2 |
| `render-indirect:60` | feature | home | Shared environments (`FindSharedEnvironment`) |
| `render-indirect:61` | feature | home | The constant ambient: `AmbientColor` lights diffuse only, the form `ST_INDIRECT_AMBIENT`, when there is no environment and while the sky's map loads (`new:17`) |
| `new:17` | feature | home | The sky's image light while its map loads: the map requested at High priority, the constant ambient until it is loaded (counted as pending), the map held whole in the streamer until the chain has read it and then dropped to its mip tail (the same idea as the probes' capture hold, `indirect/probes`), and a new `EnvironmentResolution` filtered again from the radiance cube, never from the map. Evidence: `Strata/src/Strata/Renderer/SceneRenderer.cpp:986-1022` (the fallback, the hold and the resize), `:1040-1055` (`HoldEnvironmentMap`), `:747` (`ResizePrefilteredMap`) |
| `render-indirect:65` | feature | home | The atmosphere's cube as a source of the chain, in one clause: the atmosphere refreshes it over 14 frames (`c_AtmosphereRefreshSteps`, `Strata/src/Strata/Renderer/SceneRenderer.h:872`); the refresh and its half degree of sun are `light/atmosphere`'s (`render-direct:157`), linked |
| `render-indirect:76` | feature | home | The horizon fade (`GetHorizonFade`): image light fades when a normal map turns R below the geometric surface; this page is its home (book.md) |
| `render-direct:62` | feature | home | The horizon fade as the light area lists it: `clamp(1 + R . Ng / 0.25, 0, 1)` squared (`Strata/shaders/Include/PBR.slang:93-102`), applied through the specular occlusion (`Strata/shaders/Scene/Forward.frag.slang:162-164`) and to the coat (330-332); one home with `render-indirect:76` |
| `render-direct:196` | feature | home | The quality row `EnvironmentResolution`: 256 at Low and Medium, 512 at High and Ultra, any other value clamped to 256 (`Strata/src/Strata/Renderer/RendererQuality.cpp:51`, `500`), its memory `EnvironmentBytes` (72-84) and no GPU stage (168); the presets side by side are `image/quality-settings`' |
| `render-direct:824` | open | home | Settled at the pin: the horizon fade shipped in 0.7.0. `git grep GetHorizonFade v0.6.0` finds nothing; at `v0.7.0` it is `Strata/shaders/Include/PBR.glsl:77`, added by commit `2ad3d736` ("Hold specular at 4K: specular AA, horizon fade, sky at 512"), and the Manual at that tag names it (`Docs/Manual/Lighting.md:235`). The page's `:::history` says 0.7.0 |
| `render-indirect:339` | code | home | `Strata/shaders/IBL/Prefilter.comp.slang:22-59`: the prefiltered level with N = V = R, `ImportanceSampleGGX` and `Hammersley`, the pdf D/4 and the mip from the sample's solid angle |
| `render-indirect:340` | code | home | `Strata/shaders/IBL/Irradiance.comp.slang:22-43`: the cosine-hemisphere convolution with the same mip choice |
| `render-indirect:344` | code | home | `Strata/shaders/Include/PBR.slang:93-102`: the horizon fade only; lines 73-91 of the inventory's range (`WidenRoughness`) are `render-direct` code 10, quoted on `light/brdf` |
| `new:6` | code | home | `Strata/src/Strata/Renderer/SceneRenderer.cpp:863-897`: `FilterEnvironment` and `FilterEnvironmentStep`, the chain as steps (cube levels, irradiance, each prefiltered level) that the atmosphere can spread over frames; constants at `SceneRenderer.cpp:50-61` |
| `render-indirect:378` | figure | home | Diagram: the split sum as an illustrated equation, prefiltered radiance by roughness times the table (the table's plot is `light/energy`'s figure) |
| `render-indirect:380` | figure | home | Diagram: the environment filter chain, with the probes' branch drawn faint and linked to `indirect/probes` |
| `render-indirect:382` | figure | home | Diagram: cube face conventions and the equirectangular mapping |
| `render-indirect:383` | figure | home | Diagram: filtered importance sampling, the sample's solid angle against the texel's and the mip it chooses |
| `render-indirect:424` | figure | home | Screenshot sweep: a white sphere and rough and smooth metal spheres lit only by the sky, Procedural, Environment Map and Atmosphere, with the constant ambient as "off"; the same spheres in the Indirect view |
| `render-indirect:426` | figure | home | Screenshot sweep: a mirror ball at roughness 0, 0.2 ... 1 under an HDR map, the prefiltered levels made visible |
| `render-indirect:431` | figure | home | Diagram: the horizon fade on a strong normal map at a grazing view, the reflected vector below the geometric surface and the fade's ramp; a diagram because tier 2 has no capture switch that turns the fade off (R34, D42: one request extends tier 2) |
| `new:18` | not-done | home | No cube-map texture assets: skies and probe captures are equirectangular HDR textures, made into cubes at run time; what Strata offers instead is an equirectangular HDR map as the sky's source. Evidence: `Strata/src/Strata/Asset/AssetTypes.h:14-31` (no cube texture type; its `.cube` files are color lookups, `ColorLookup`); `Docs/Roadmap.md:947` ("cube texture assets" left for later); `git grep -n "TextureDimension::TextureCube" 822a7a46 -- Strata/src` finds only the renderer's own cubes (`Renderer.cpp`, `SceneRenderer.cpp`, `SceneRendererReflectionProbes.cpp`) |
| `new:19` | hands-on | home | The page's exercises (R32, D27): **Basic.** trace it yourself: a change of the procedural sky followed from the sky light component to the prefiltered cube (`UpdateEnvironment` compares the sky's parameters with the cube's and calls `GenerateProceduralSky` only when they differ, which writes mip 0, calls `FilterEnvironment` and counts `EnvironmentUpdates`); **Medium.** modify: a patch against the pin that drops the comparison in `UpdateEnvironment`, so the cube is made again every frame; predict which check of the test fails first and why the sky's intensity, background and blur never made the cube again, then run it. Evidence: `Strata/src/Strata/Renderer/SceneRenderer.cpp:917-984`, `:827-861`; `StrataTests/src/Renderer/GPUProceduralSkyTests.cpp:193` ("The procedural cube is computed again only when the sky or the sun changes"), `:228-232` (intensity, background and blur make no new cube) |
| `render-indirect:565` | term | home | Image-based lighting (IBL) |
| `render-indirect:567` | term | home | Equirectangular |
| `render-indirect:568` | term | home | Cube map and cube array: two terms, each its own glossary entry; the cube array is defined here in one sentence and used by `indirect/probes` |
| `render-indirect:580` | term | home | Split-sum approximation (`render-direct:682` repeats it: see Questions) |
| `render-direct:682` | term | home | Split sum, as the light area words it; one glossary entry with `render-indirect:580` |
| `render-indirect:582` | term | home | Prefiltered environment |
| `render-indirect:583` | term | home | Filtered importance sampling, its entry here; the glossary step splits the item (R48): "importance sampling" is homed on `basics/math-probability`, which teaches it as mathematics, and `light/energy` applies it to the GGX lobe |
| `render-indirect:590` | term | home | Horizon fade (`render-direct:689` repeats it: see Questions) |
| `render-direct:689` | term | home | Horizon fade, as the light area words it; one glossary entry with `render-indirect:590` |
| `render-direct:151` | feature | use | The sky light component that chooses the source (`SceneRenderer::UpdateEnvironment`); its home is `light/sky` |
| `render-direct:58` | feature | use | The split-sum BRDF table the specular half multiplies by |
| `render-indirect:346` | code | link | `GetIndirectInputs` reads the irradiance and prefiltered maps; quoted on `indirect/seam` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The BRDF table: scale and bias of F0 over NoV and roughness, directional albedo | `light/energy` | must |
| Importance sampling the GGX lobe and dividing by its pdf (the table's integral) | `light/energy` | must |
| GGX, alpha as roughness squared, the lobe around R | `light/reflectance` | must |
| Monte Carlo estimates, importance sampling as mathematics and the Hammersley set | `basics/math-probability` | must |
| Solid angles, spherical coordinates, spherical harmonics | `basics/math-sphere` | must |
| Mips as prefiltered copies of an image | `basics/signals` | must |
| The sky's three sources and the sky light component | `light/sky` | must |
| The atmosphere's sky view, as a source | `light/atmosphere` | helps |
| Compute dispatches, thread groups and push constants | `gpu/compute` | must |
| Texture views of a cube as a 2D array, subresource sets | `gpu/resources-lifetimes` | helps |
| Normal maps and the geometric normal | `light/materials` | must |
| Quality rows and their presets | `image/quality-settings` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `cube-array` | cube array | - |
| `cube-map` | Cube map | - |
| `equirectangular` | Equirectangular | - |
| `filtered-importance-sampling` | filtered importance sampling | - |
| `horizon-fade` | Horizon fade | - |
| `image-based-lighting` | Image-based lighting | IBL |
| `prefiltered-environment` | Prefiltered environment | - |
| `split-sum-approximation` | Split-sum approximation | Split sum |
