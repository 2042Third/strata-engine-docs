# Allocation: indirect

## `indirect/problem` — The indirect-light problem

**Covers.** The page opens with the part's running example, the Cornell box. Strata's box (the look-dev scene's) is lit
only by a glowing panel under its ceiling. On the left it is drawn with GI off: the panel glows, but a glowing surface
lights nothing else without GI, and the red and green walls do not bleed onto the floor. On the right is the reference
image from the page's own path tracer sketch. The reader sees what is missing before any word about it. The naive
answer is a constant ambient color (Strata keeps one, `AmbientColor`, but only as the last fallback). The page shows
where it breaks: no occlusion, no color from nearby walls, the same light in a cave and on a beach.

Then the idea. The rendering equation extends `light/reflectance`'s reflection equation: the light leaving a point is
what it emits plus what it reflects of all the light arriving from every direction, and that arriving light is itself
light leaving other points. Direct light arrives from a light in one step. Indirect light has bounced first, and the
sky is a distant emitter. A diagram splits the equation into three terms (direct, indirect diffuse, indirect specular)
and names the proxy that approximates each in Strata and the page that teaches it. The path tracer sketch then solves
the equation the slow, exact way: Monte Carlo sampling of random bounces, noisy with few samples, converging with many.
Its image is the ground truth that `indirect/ao`, `indirect/probes` and `indirect/gi-cascades` compare against.

The approaches engines use, each introduced by the flaw of the one before: a constant or a hemisphere ambient; image
light from the sky; local probes; screen-space effects (SSAO, SSR, SSGI); baked lightmaps, radiosity and irradiance
volumes; dynamic world-space methods (DDGI's probes, voxel cone tracing, signed distance fields as in Lumen, radiance
cascades); hardware ray tracing. A table gives cost, quality, complexity and who uses each. Strata's choice: the split
made explicit in two gathers, layer over layer, and global illumination that traces world data, never the screen (a
`:::why` aside with its reason). The page states what Strata does not do here: no hardware ray tracing, no lightmaps and
no baked GI (reflection probes are the only bake). Common mistakes close it: ambient light as "a constant to brighten
shadows", GI expected to be free bounce light, and leaks through thin walls ignored. The exercises run the sketch at
growing sample counts and choose a family for three games. At the end the reader can name the parts of indirect light,
say which technique approximates which part, and read the part's map.

**Leaves out.**

- The reflection equation, radiance, irradiance and microfacets → `light/reflectance`
- How each technique works in Strata → `indirect/ibl`, `indirect/ao`, `indirect/probes`, `indirect/ssr`, `indirect/gi-voxels`
- The join of every indirect term in the forward shader, and the fallback stack → `indirect/seam`
- Seeing the indirect light alone with the Indirect debug view → `light/measuring-light`
- The general technique of lightmaps and of ray-traced lighting, which Strata lacks → `appendix/not-in-strata`
- What Strata's GI cannot do → `indirect/gi-limits`

**Fit.** `fits`: about 3,700 words against M (3,000). The rendering equation, the path tracer sketch (a fence shown in
two short pieces) and the families table take the most words; the exercises run the same sketch.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-indirect:230` | concept | home | What indirect light is: direct against bounced light, the sky as a distant emitter, the rendering equation as the definition, why real-time engines split it (direct lights analytic, the rest from cheap proxies); the error that ambient light is a constant that brightens shadows |
| `render-indirect:303` | concept | home | The families of GI and their trade-offs (baked lightmaps, irradiance volumes and DDGI, voxel cone tracing, screen-space GI, signed distance fields and ray tracing as in Lumen, radiance cascades): dynamic against baked, history against per-frame determinism, memory, thin walls; Strata's world-space radiance cascades over a voxel clipmap, experimental, as the bridge to `indirect/gi-voxels` |
| `render-indirect:508` | rule | home | The design decision "GI traces world data, never the screen", in a `:::why` aside: screen-space GI needs temporal accumulation and misses what is off screen, and determinism keeps frames free of flicker and smear. Evidence `AGENTS.md:405-406` |
| `render-indirect:564` | term | home | Indirect light |
| `render-indirect:623` | term | home | Global illumination (GI) |
| `render-indirect:598` | term | home | Radiosity, the classic offline family of the table; `indirect/ao` uses it for its multi-bounce fit |
| `new:1` | concept | home | Monte Carlo path tracing as ground truth: the page's sketch `sketches/indirect-problem-pathtracer.cpp` traces the Cornell box by random bounces with a fixed seed; few samples are noisy, many converge. General knowledge. |
| `new:2` | figure | home | The reference image (kind `reference`): the sketch's Cornell box in a slider with Strata's look-dev Cornell box with GI off, from the same camera; the opening picture of the page, and the image the part's later pages compare with. The box's only source is an emissive panel and the scene has no light component, so a capture through the editor camera outside play mode would add preview lighting (`Strata/src/Strata/Renderer/SceneRenderer.cpp:180-185`; the capture's own camera is an editor view only outside play, `StrataEditor/src/Editor/EditorViewportCommands.cpp:444`): the recipe captures in play (its `play` field), and its `complete` asserts `/previewLighting` false (pipelines.md §5.2, §5.3). Evidence: `Tools/LookDev/LookDevScene.json:253-268` (the Cornell scene, its panel at line 267 and its Post Process asking for GI at line 259), `Tools/LookDev/Shots.json:148` (the shot `lookdev.cornell` and its camera) |
| `new:3` | figure | home | Diagram: the rendering equation split into direct light, indirect diffuse and indirect specular, with the proxy that approximates each in Strata (sky, probes, screen-space reflections, the GI field, ambient occlusion) and the page of the part that teaches it. Evidence: `Strata/shaders/Include/IndirectLight.slang:52-129` (the two gathers and the compose step) |
| `new:4` | not-done | home | No hardware ray tracing. Evidence: `git grep -niE "accelerationstructure\|RayQuery<\|ray_query\|raytracing\|TraceRay\|VK_KHR_ray" 822a7a46 -- Strata/src Strata/shaders` finds nothing; the word `RayQuery` alone matches only physics (`struct RayQuery` at `Strata/src/Strata/Physics/PhysicsWorld.cpp:4480` and `Strata/src/Strata/Physics/CharacterControllers.cpp:430`) |
| `new:5` | not-done | home | No lightmaps and no baked global illumination: reflection probes are the only bake. Evidence: `git grep -ni lightmap 822a7a46 -- Strata/src Strata/shaders` finds nothing; the only bake is `lighting.bakeProbes` (`StrataEditor/src/Editor/EditorLightingCommands.cpp:872`); `Docs/Releases/0.7.0.md:410-411` lists "a baked irradiance volume" under "Not in this release" (quoted, never dated) |
| `new:16` | hands-on | home | The page's exercises (R32, D27): **Basic.** predict, then run: the page's path tracer sketch at 4, 64 and 1,024 samples per pixel with its fixed seed, the error against a 4,096-sample image halving each time the samples grow four times (a sketch with its output); **Medium.** design: a family of the table for three games (a fixed indoor level, an open world with a day and night cycle, a small game for phones), with what each choice costs. General knowledge. |
| `render-indirect:61` | feature | use | The constant ambient as the naive answer and the last fallback; its home is `indirect/ibl` |
| `render-indirect:375` | figure | link | The fallback stack, drawn in full on `indirect/seam` |
| `render-indirect:455` | figure | use | GI off and on in the Cornell box, named as where the part ends; its home is `indirect/gi-cascades` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The reflection equation, radiance and irradiance in use, Lambert diffuse | `light/reflectance` | must |
| Microfacets and the GGX lobe, as far as "rough surfaces blur reflections" | `light/reflectance` | helps |
| Monte Carlo integration with random samples and a seed | `basics/math-probability` | must |
| Solid angles and integrating over the hemisphere | `basics/math-sphere` | must |
| The forward shader's anatomy: where the lights are added | `light/brdf` | helps |
| The sky's three sources (map, procedural, atmosphere) | `light/sky` | must |
| Light units: nits and lux | `light/units-exposure` | helps |
| What the depth buffer and the prepass hold (why the screen sees only the front of what is on screen) | `gpu/frame-tour` | helps |
| Temporal accumulation and history, as the cost of screen-space GI | `image/taa` | helps |
| The look-dev harness and its shots | `engineering/look-dev` | helps |

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

## `indirect/seam` — Where indirect light meets the surface: inputs, gathers and fallbacks

**Covers.** The job: the one place in the forward pass where every kind of indirect light meets the surface. One struct
of inputs is filled once per pixel, two gathers read it (diffuse and specular), and a compose step adds them. How each
input is made is the job of the later pages of the part; this page is their common map. The problem section is one
paragraph that links `indirect/problem`.

The map starts with the frame. On the CPU, `PrepareGlobalIllumination` and `GatherReflectionProbes` run first; on the
GPU the prepass, the screen shadows, then `GPU.AO`, `GPU.RadianceCascades` and `GPU.Reflections` (probe conversions,
then the SSR trace) all run before `GPU.Opaque`, which reads their results: ambient occlusion at SRV 11, the probes at
SRV 9 and 10, the reflections at SRV 18, the GI field at b3 and SRVs 35 to 40 and 54. The fallback-stack diagram then
shows one pixel: screen-space reflections (confidence a) over the probes (weight w, two blended) over the sky (1 - w)
over the constant ambient, in a diffuse and a specular column, with the places where occlusion, specular occlusion and
the multi-bounce fit multiply and where the GI field replaces the diffuse part.

The contract: `IndirectInputs` is filled once; new streams add their fields at the end; Strata 0.7.0's four forms
(`ST_INDIRECT_PROBES`, `SCREEN`, `SKY`, `AMBIENT`) keep their branch order and their expressions bit for bit; a feature
that is off costs nothing and changes no bit, because its input is a dummy (a black cube array without probes, a black
reflection texture, the GI's dummy views). That rule of the renderer has its home on `gpu/frame-tour`; this page shows
it at work. Global illumination that is off changes no bit either, but its gather is compiled in and still costs a
little, which `indirect/gi-limits` states as measured. A toy version of the stack follows in about 40 lines. The real
code is walked in data order: `IndirectLight.slang` in three pieces (the struct and the forms; the diffuse and specular
gathers; compose, with the field gather shown as structure only), `GetIndirectInputs` (the split-sum reflectance with
its energy compensation, the probes' evaluation, the SSR sample, the sky reads, the form chosen in 0.7.0's order, and
Lagarde's specular occlusion, named here and taught on `indirect/ao`), and the end of `ShadeLitSurface`, where ambient
occlusion and the multi-bounce enter, the field joins (one sentence, linking `indirect/gi-cascades`) and the clear coat
takes its own image light with its own occlusion and horizon fade, from the probes, the sky or the ambient only: the
coat gets no screen-space reflections. The fallback hierarchy is taught as an idea of its own: each layer replaces the
next by a weight, premultiplied, so a texel that found nothing adds no black.

Alternatives Strata did not choose: a separate deferred ambient pass, one target per term composed later, a branch per
feature. How it is tested: `GPU.SceneRenderer.Lighting` and `GPU.SceneRenderer.ReflectionProbes` keep the default image
bit for bit. Changing it safely: the required exercise adds a field to `IndirectInputs` and keeps the default image bit
for bit, and a trace exercise finds which form a pixel takes and where the CPU sets what the choice reads. The reader
can then trace any indirect term of a pixel back to the pass that made it.

**Leaves out.**

- How the sky's maps are made → `indirect/ibl`
- GTAO, the multi-bounce fit and Lagarde's specular occlusion as a model → `indirect/ao`
- How probes are gathered, converted and blended, and why a bake drops the lights' highlights → `indirect/probes`
- How screen-space reflections are traced and resolved → `indirect/ssr`
- The field gather's weights and the join's bit-for-bit form → `indirect/gi-cascades`, `indirect/gi-limits`
- "A feature that is off is invisible bit for bit" as a rule of the whole renderer → `gpu/frame-tour`
- The clear coat as a material, and premultiplied alpha → `light/clearcoat-transmission`

**Fit.** `over`: about 4,350 words against M (3,000). One 131-line shader in three pieces, three more excerpts, the
frame's order, the fallback stack and two exercises (E13 with its worked solution, and the trace) pass M's top; by S2
the page takes the next size, L (5,000).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-indirect:82` | feature | home | `IndirectInputs`: the per-pixel struct both gathers read, filled by `GetIndirectInputs` |
| `render-indirect:83` | feature | home | The four forms and 0.7.0's branch order, kept bit for bit |
| `render-indirect:84` | feature | home | The diffuse gather: probes' SH irradiance plus the sky's share, or the sky, or the ambient; times the occlusion color |
| `render-indirect:85` | feature | home | The specular gather: probes' radiance plus the sky's share; SSR mixed premultiplied; specular occlusion only on the fallback |
| `render-indirect:86` | feature | home | The field gather as one of the gathers: field irradiance on the diffuse albedo under the diffuse occlusion, without the multi-bounce fit; its weight and the join are `indirect/gi-cascades`' |
| `render-indirect:87` | feature | home | Compose: each form's scale where 0.7.0 applied it |
| `render-indirect:88` | feature | home | The clear coat's image light: `SampleSpecularLight` with its own Lagarde occlusion and horizon fade; the probes', the sky's or the ambient's light only, so the coat gets no screen-space reflections (`Strata/shaders/Scene/Forward.frag.slang:323-333`; `Docs/Roadmap.md:941-942`) |
| `render-indirect:201` | feature | home | The frame placement of the area: the CPU gathers, `GPU.AO`, `GPU.RadianceCascades`, `GPU.Reflections` before `GPU.Opaque`, and the bindings the forward pass reads |
| `render-indirect:300` | concept | home | The fallback hierarchy SSR, probes, sky, constant ambient, each layer replacing the next by a weight (premultiplied, no black edges); the error of mixing unpremultiplied colors |
| `render-indirect:345` | code | home | `Strata/shaders/Include/IndirectLight.slang:1-131`: the struct and the forms (9-39), the gathers (52-107), the field gather and compose (109-129), shown in three pieces |
| `render-indirect:346` | code | home | `Strata/shaders/Scene/Forward.frag.slang:118-171`: `GetIndirectInputs`, from the split-sum reflectance to Lagarde's specular occlusion |
| `render-indirect:347` | code | home | `Strata/shaders/Scene/Forward.frag.slang:280-338`: the end of `ShadeLitSurface`, where AO, the multi-bounce, the GI join and the clear coat meet |
| `render-indirect:360` | code | home | `Strata/src/Strata/Renderer/SceneRenderer.cpp:3453-3490`: AO, GI and reflections before the opaque pass, each in a GPU stage, and what a failed GI frame does to the field's constants |
| `render-indirect:375` | figure | home | Diagram: the indirect-light fallback stack, per pixel, diffuse and specular columns, with the multipliers and the field |
| `render-indirect:506` | rule | home | Features cost nothing when off and the image stays bit for bit: the dummy black cube array, black SSR texture and GI dummy views, checked by tests; named as the renderer's rule from `gpu/frame-tour`; GI off keeps the image bit for bit while its compiled-in gather still costs a little, stated on `indirect/gi-limits` (book.md's design decision) |
| `new:20` | hands-on | home | Exercise (trace it yourself, R32, D27): for one pixel, find which of the four forms `GetIndirectInputs` chooses and where the CPU sets each value the choice reads (the probes' weight, `ReflectionParams.x` for screen-space reflections, `EnvironmentParams.w` for the sky's maps); the solution names the files and functions. Evidence: `Strata/shaders/Scene/Forward.frag.slang:157-159`; `Strata/shaders/Include/IndirectLight.slang:9-12`; `Strata/src/Strata/Renderer/SceneRenderer.cpp:1029`, `:3118` |
| `render-indirect:558` | hands-on | home | Required exercise E13: add a field to `IndirectInputs` for a new term and keep the default image bit for bit (`GPU.SceneRenderer.Lighting`, `GPU.SceneRenderer.ReflectionProbes`) |
| `render-indirect:329` | concept | link | "Bit for bit when off" as a rule of the whole renderer, taught on `gpu/frame-tour` |
| `render-indirect:470` | rule | use | Diffuse gets what specular leaves (`1 - SpecularColor`), visible in the gathers; taught on `light/energy` |
| `render-indirect:110` | feature | use | Lagarde's specular occlusion in `GetIndirectInputs`, named and linked to `indirect/ao` |
| `render-indirect:367` | code | link | The join's `x * 1 + 0` form, quoted on `indirect/gi-cascades` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The irradiance and prefiltered maps and the split sum | `indirect/ibl` | must |
| The forward shader's anatomy, `ShadeLitSurface` and the variants | `light/brdf` | must |
| Energy compensation (`SurfaceData::SpecularEnergy`) and the BRDF table | `light/energy` | must |
| Clear coat and its Fresnel | `light/clearcoat-transmission` | must |
| Premultiplied alpha | `light/clearcoat-transmission` | must |
| Registers, constant buffers and SRVs of the scene layout | `gpu/binding` | must |
| The frame's passes in order, and the rule that an off feature changes no bit | `gpu/frame-tour` | must |
| GPU stages and markers | `gpu/readback-timing` | helps |
| Shader variants made by preprocessor defines | `gpu/shaders` | helps |
| The debug views, as the tool to check a change | `light/measuring-light` | helps |

## `indirect/ao` — Ambient occlusion without history

**Covers.** The job: occlusion of the indirect light, computed in screen space from the prepass's depth and normals each
frame, without history, and how it enters shading (diffuse through the multi-bounce fit, specular through Lagarde's
specular occlusion). The material's occlusion map is `light/materials`'; shadows are the direct light's.

The problem section teaches what occlusion of ambient light means (visibility against obscurance) and the approaches
with their costs: Crytek's SSAO, HBAO, GTAO (Jimenez et al. 2016), baked AO maps and ray-traced AO. Then the second
idea: why few samples per pixel are enough when a fixed interleaved pattern is resolved in space, against frame noise
that TAA must clean (it ghosts, and the image differs between anti-aliasing modes). This is "nothing needs history to
look right" at work (`image/taa` is its home).

The map: `RenderAmbientOcclusion` clamps the component's values, fills push constants and makes two dispatches (GTAO,
then the denoiser) in `GPU.AO`; targets are R16F where the device stores it, else R32F, with the shader variants
`GTAOHalf` and `AODenoiseHalf`; the quality row sets slices and steps (Low 1x4, Medium 2x6, High 3x8, Ultra 4x12); the
component's fields are on, radius 1 m, intensity 1 and multi-bounce on. The contract is four rules: AO darkens indirect
light only; no history (the fixed 4x4 pattern, never the frame); the radius is clamped on screen between 0.3% (at least
1.5 px) and 12% of the view's height; the fit changes only by running `Tools/FitAOMultiBounce.py --write`. A toy version
computes horizon AO over a 1D height field. The real code: `GTAO.comp` (slices, the two horizons, the cosine-weighted
arc, the radius clamp, the thin-occluder relaxation `1 - 0.9^(6/steps)`, the pattern's rotations and step jitter);
`AODenoise.comp` (the 5x5 tent whose weights 0.5, 1, 1, 1, 0.5 weigh each of the 16 phases once, then a bilateral blur,
separable in a 24x24 shared tile, one dispatch); the multi-bounce fit (`x / (1 - rho (1 - x) h)`, fitted to 2D radiosity
in grooves and trenches, and why the planned polynomial was rejected); where AO applies (indirect light only, not on
transparent surfaces); Lagarde's specular occlusion, multiplied by the horizon fade of `indirect/ibl`, on the fallback
only.

Alternatives: HBAO+, temporally accumulated GTAO, ray-traced AO, bent normals and cones. How it is tested:
`Renderer.AmbientOcclusion` (the fit against the script's reference) and `GPU.SceneRenderer.AmbientOcclusion` (no
pattern without TAA), with the exercises E2 and E4 and a trace of the radius from metres to pixels. Changing it safely:
the generator, the no-history rule, and the `ao` view's repeats when frame constants change (the GI's own buffer,
`indirect/gi-cascades`). What went wrong before: a `:::history` of 0.6.0's AO and its blur, made history-free in 0.7.0
with the radius clamp and the multi-bounce. Figures: AO off and on with the `ao` view, the quality rows as a sweep, the
radius at 0.25, 1 and 3 m with a near and a far object, a crop of thin occluders, multi-bounce on a white and a dark
corner, the same AO under TAA, FXAA and none, and the Cornell box with AO against the reference. The reader can explain
GTAO and change it without breaking a rule.

**Leaves out.**

- Material occlusion maps and their import → `light/materials`
- Where the occlusion terms enter the gathers, as a whole → `indirect/seam`
- What the screen-space reflections keep of their light under AO → `indirect/ssr`
- Using AO in a game: radius, intensity and multi-bounce on real materials → `make/reflections`
- The AO view among the other debug views → `light/measuring-light`
- The quality row among the presets → `image/quality-settings`

**Fit.** `over`: about 6,850 words against L (5,000). Four ideas from zero, four excerpts, four diagrams, seven pictures
and three exercises pass L's top; by S2 the page takes the next size, XL (8,000), one page with anchored sections,
because a split would cut the one mechanism (pattern, resolve, fit) in two.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-indirect:269` | concept | home | Ambient occlusion: visibility against obscurance, the screen-space methods, baked and ray-traced AO, with a table of costs; errors: AO on direct light, AO on specular unchanged, dark halos from thin occluders, radius in pixels against metres |
| `render-indirect:274` | concept | home | Noise, patterns and denoising without history: a 4x4 ordered-dither pattern whose 16 phases a separable 5x5 tent weighs exactly once, so one frame is complete; the error of frame-varying noise left to TAA |
| `render-indirect:280` | concept | home | Multi-bounce AO: occluded light is not lost; Jimenez's polynomial against Strata's rational fit; the error that AO darkens white corners as much as black ones |
| `render-indirect:283` | concept | home | Specular occlusion from AO: Lagarde's specular occlusion (2014), multiplied by the horizon fade of `indirect/ibl`; the error of occluding what SSR saw (its fix is `indirect/ssr`'s) |
| `render-indirect:95` | feature | home | GTAO: horizon-based, cosine-weighted visibility per screen slice; the dispatch in `RenderAmbientOcclusion` |
| `render-indirect:96` | feature | home | The quality samples Low 1x4 to Ultra 4x12 (`AmbientOcclusionLevel`) |
| `render-indirect:97` | feature | home | The fixed 4x4 pattern: slice rotation and step jitter from the ordered-dither order, never the frame |
| `render-indirect:98` | feature | home | The history-free denoiser: tent resolve of the 16 phases and a bilateral blur, one dispatch, 24x24 shared tile |
| `render-indirect:99` | feature | home | The radius clamp: 0.3% (at least 1.5 px) to 12% of the view's height (`c_AOMinRadiusFraction`, `c_AOMaxRadiusFraction`) |
| `render-indirect:100` | feature | home | The thin-occluder relaxation `1 - 0.9^(6/steps)` |
| `render-indirect:101` | feature | home | The multi-bounce fit: shader, C++ header and generator, applied in the forward pass |
| `render-indirect:102` | feature | home | Half-float targets where the device stores them, R32F else, and the `Half` shader variants |
| `render-indirect:103` | feature | home | The component's fields: `AmbientOcclusion`, `AmbientOcclusionRadius`, `AmbientOcclusionIntensity`, `AmbientOcclusionMultiBounce` |
| `render-indirect:104` | feature | home | Where AO applies: indirect light only (diffuse through the occlusion color, specular through Lagarde); not on transparent surfaces |
| `render-indirect:110` | feature | home | Lagarde's specular occlusion `clamp(pow(NoV + ao, exp2(-16 r - 1)) - 1 + ao)` times the horizon fade, on the fallback |
| `render-indirect:348` | code | home | `Strata/shaders/Effects/GTAO.comp.slang:41-141`: slices, horizons, the cosine-weighted arc, the radius clamp, the relaxation and the pattern (its order at lines 32-33) |
| `render-indirect:349` | code | home | `Strata/shaders/Effects/AODenoise.comp.slang:1-90`: the header's account of the design and `ResolveAlong` (68-90) |
| `render-indirect:350` | code | home | `Strata/shaders/Include/AmbientOcclusionFit.slang:1-17`: the generated fit; with the docstring of `Tools/FitAOMultiBounce.py:2-43` on the reference and the rejected polynomial |
| `render-indirect:351` | code | home | `Strata/src/Strata/Renderer/SceneRendererAmbientOcclusion.cpp:116-143`: the CPU side of a compute effect, clamping user values, push constants and two dispatches |
| `render-indirect:385` | figure | home | Diagram: a GTAO slice with the horizons h0 and h1, the projected normal's angle and the cosine-weighted arc |
| `render-indirect:387` | figure | home | Diagram: the 4x4 pattern and the 5x5 tent kernel, each phase weighed once |
| `render-indirect:388` | figure | home | Plot: the horizon over steps behind a pole, with and without relaxation |
| `render-indirect:389` | figure | home | Chart: the multi-bounce curves for several albedos against the radiosity means |
| `render-indirect:433` | figure | home | Off and on: Post Process `AmbientOcclusion` on a sample scene, with the `ao` view (the shot `lookdev.view.ao`, `Tools/LookDev/Shots.json:65`) |
| `render-indirect:434` | figure | home | Sweep: the quality rows Low, Medium, High and Ultra |
| `render-indirect:435` | figure | home | Sweep: `AmbientOcclusionRadius` 0.25, 1 and 3 m, a near and a far object to show the clamp |
| `render-indirect:436` | figure | home | Crop: thin occluders (the look-dev poles, fence and plate) in the `ao` view |
| `render-indirect:437` | figure | home | Multi-bounce on and off on a white plaster corner and a dark soil corner, `ao` view against the lit image |
| `render-indirect:438` | figure | home | The same AO under TAA, FXAA and none (LookDev `--aa`): the proof that nothing needs history |
| `new:7` | figure | home | The Cornell box with AO and without GI, in a slider with the path-traced reference of `indirect/problem` (`new:2`): what AO approximates and what it misses. The box's only source is its emissive panel, which lights nothing without GI, so the recipe gives the box the light that AO darkens (a sky light, with a map or with its constant ambient) and captures in play (its `play` field), and its `complete` asserts `/previewLighting` false (pipelines.md §5.2, §5.3). Evidence: `Tools/LookDev/LookDevScene.json:253-268`, `Tools/LookDev/Shots.json:148` |
| `render-indirect:479` | rule | home | AO darkens indirect light only; direct light has shadows; specular uses Lagarde, not raw AO |
| `render-indirect:480` | rule | home | No history for AO: the same image with TAA, FXAA or none, two frames of a still view identical |
| `render-indirect:482` | rule | home | The radius clamped on screen: constant cost and look at every resolution |
| `render-indirect:484` | rule | home | The multi-bounce fit changes only through `Tools/FitAOMultiBounce.py --write`: three generated copies must agree |
| `render-indirect:547` | hands-on | home | E2: read and run `Renderer.AmbientOcclusion`; run the fit script (print only) and explain its errors table |
| `render-indirect:549` | hands-on | home | E4: a frame-varying pattern on a scratch branch makes "no pattern without TAA" fail |
| `new:21` | hands-on | home | Exercise (trace it yourself, R32, D27): `AmbientOcclusionRadius` followed from the component to a pixel's radius on screen: `RenderAmbientOcclusion` clamps it to 0.01 to 10 m and sets the bounds in pixels from the view's height, and `GTAO.comp` projects it and clamps it there; the solution names the lines and works the radius out for a near and a far surface. Evidence: `Strata/src/Strata/Renderer/SceneRendererAmbientOcclusion.cpp:116-128`; `Strata/shaders/Effects/GTAO.comp.slang:61-68` |
| `render-indirect:591` | term | home | Ambient occlusion (AO) |
| `render-indirect:592` | term | home | GTAO |
| `render-indirect:593` | term | home | Slice and horizon angle, two entries |
| `render-indirect:596` | term | home | Tent kernel (0.5, 1, 1, 1, 0.5), qualified against the shadows' tent filter (`render-direct:733`) |
| `render-indirect:597` | term | home | Multi-bounce AO |
| `render-indirect:599` | term | home | Specular occlusion (Lagarde) |
| `render-scene:605` | term | use | The ordered-dither order the pattern shares with the LOD fade (`render-indirect:595` repeats it) |
| `render-direct:737` | term | use | The bilateral (edge-aware) blur, taught on `light/sun-shadows-2` (`render-indirect:594` repeats it) |
| `render-indirect:598` | term | use | Radiosity, the reference the fit was made against; its home is `indirect/problem` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| View positions from depth through the inverse projection; reversed Z; UVs and NDC | `gpu/coordinates` | must |
| The depth prepass and the normals it writes | `gpu/frame-tour` | must |
| Compute shaders: thread groups, shared memory and barriers | `gpu/compute` | must |
| Kernels, sampling, ordered dither and spatial denoising | `basics/signals` | must |
| Integrals as accumulation, cosine weighting | `basics/math-probability` | helps |
| Push constants | `gpu/binding` | must |
| The inputs `DiffuseOcclusion` and `SpecularOcclusion` of the seam | `indirect/seam` | must |
| TAA, its history and "nothing needs history to look right" | `image/taa` | must |
| FXAA, for the comparison of anti-aliasing modes | `image/spatial-aa` | helps |
| Half floats and their range | `basics/color` | helps |
| Material occlusion maps | `light/materials` | must |
| The bilateral blur | `light/sun-shadows-2` | helps |
| Running a Python tool from a terminal | `basics/tools` | helps |
| Writing and running a GPU test | `gpu/first-triangle` | helps |

## `indirect/probes` — Reflection probes

**Covers.** The job: local reflections and ambient light inside boxes, from captures baked in the editor. The page
holds the component, the renderer's gather per frame, the probe cache, the GPU conversion of a capture, the shader's
blend and box projection, and the bake. The sky's image light is `indirect/ibl`'s, screen-space reflections are
`indirect/ssr`'s.

The problem section: a reflection of the distant sky is wrong inside a room (the parallax problem); box projection
(Lagarde and Zanuttini 2012, "parallax-corrected cubemaps") fixes it for box-shaped rooms; overlapping probes blend; a
probe is baked, not captured while the game runs; priorities decide overlaps; cube arrays hold many probes. A table
compares static cube maps, parallax-corrected boxes, clustered probe lists, run-time capture and irradiance volumes. The
map is the cache diagram: up to 16 slots in a cube array, chosen least recently used, two conversions a frame, and the
takeover after a change of resolution. The contract is six rules: probes are baked in the editor, never at run time, and
a bake draws no sun disk and no lights' highlights; a bake renders where the probe stands now; a bake replaces only its
own earlier capture and trashes it in the same undo step; captures are held whole until converted; conversions are
spread, two a frame, in interactive renderers; nothing blocks (a capture not loaded lights nothing). A toy version is
box projection by hand in about 30 lines (exercise E6).

The real code, in data order: the component (`Capture`, `Extents`, `BlendDistance`, `BoxProjection`, `Intensity`,
`Priority`); `GatherReflectionProbes` and `IsStronger` (active probes with a capture, a frustum test of the bounding
sphere, priority first, then the smaller box, then the entity; non-finite transforms refused); the cache, its slots and
`acquireSlot`; the residency holds (`hold`, `holdWhole`, `ReleaseStaleReflectionProbeHolds`), because nothing draws a
capture and the streamer would never raise its levels; `ConvertReflectionProbes` (equirectangular to a scratch cube, its
levels, the six prefiltered levels by `GetProbePrefilterSamples`, then the SH projection); the SH projection itself
(texel solid angles, a shared-memory reduction, band factors 1, 2/3 and 1/4: Ramamoorthi and Hanrahan's pi, 2 pi/3 and
pi/4 divided by pi, because the probes store irradiance over pi); the shader (`ToProbeBox`, `GetProbeWeight`,
`GetProbeLookup`, two probes blended, the stronger over the weaker). Then the bake: `lighting.bakeProbes` renders with
its own renderer six 256-texel views of 90 degrees with HDR output and the probe-capture mode (`MaterialParams.w`: the
lights' diffuse light only), at a power-of-two pre-exposure, assembles a 1024x512 equirectangular `.hdr` on jobs, writes
it on an I/O job, imports it to `Assets/Lighting/<scene>/<id>.hdr` and records one undo step. What a bake sees and waits
for: its renderer (`ForBake`) takes Medium's values as Custom, without TAA, texture streaming or spreading, so a bake
never depends on a person's Graphics Quality, and a capture holds no global illumination (Medium's row is Off) and no
screen-space reflections (Medium's Checkerboard needs TAA); each probe's six views are rendered again every frame until
nothing they show is pending, for at most two minutes, after which the result says `complete: false`; the background is
the primary camera's clear color; a scene change or Play before the import ends the bake with nothing changed. Each bake
adds a bounce (the Showcase bakes eight times); a set of probes per time of day is switched with `SetActive` (the how-to
is `make/reflections`'). The bake is a step only a command can do on this track: the page gives the whole line to paste,
one sentence on what it does, and a link forward to `editor/commands`.

What Strata does not do: probes captured while the game runs, and a gizmo for a probe's box (the Scene view draws no box
for its `Extents`; exercise E5's probe-weight view shows a box's reach). Alternatives, tests
(`GPU.SceneRenderer.ReflectionProbes`, `GPU.Editor.Lighting`, `Editor.Lighting`) and changing it safely (bakes through
commands, the trash, undo) follow, with a trace of one bake through its four stages. What went wrong before: 0.7.0's
bakes drew the sun disk and the lights' highlights, shown from the v0.7.0 baseline set. Figures: a probe on and off in
the Showcase hut, box projection on and off, `BlendDistance` 0 against 1 m, 128 against 256 texels, the bake with and
without the sun disk, bakes 1, 2 and 8, and the Cornell box lit by a baked probe against the reference. The reader can
place, bake and debug probes and change their code.

**Leaves out.**

- The filter chain the conversion reuses → `indirect/ibl`
- Where the probes' light meets SSR and the sky in the shader → `indirect/seam`
- Placing probes, fitting boxes and times of day in a game → `make/reflections`
- Holds, residency and why a texture's levels rise → `assets/residency`, `draw/mip-streaming`
- Pre-exposure as a mechanism → `image/pre-exposure`
- Commands, undo steps and the trash in general → `editor/commands`, `editor/undo`, `editor/trash-references`
- The `ReflectionProbeResolution` row among the presets → `image/quality-settings`

**Fit.** `fits`: about 7,300 words against XL (8,000). The renderer's half (gather, cache, holds, conversion, SH
projection, shader) and the editor's bake with what it sees and waits for take the most words, beside seven pictures
and four diagrams.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-indirect:286` | concept | home | Local reflections: the parallax problem, box projection, blending, baking, priorities, cube arrays; Strata's choices (editor bakes, at most 16 per view, two blended per pixel, LRU slots, equirectangular captures converted at run time); errors: baking the sun disk or highlights, a box that does not fit the room, expecting probes to update at run time |
| `render-indirect:118` | feature | home | `ReflectionProbeComponent` and `c_MinExtent` (`Strata/src/Strata/Renderer/RendererComponents.h:153-170`) |
| `render-indirect:119` | feature | home | The gather and ranking per frame: priority, then the smaller volume, then the entity; at most `MaxReflectionProbes` |
| `render-indirect:120` | feature | home | The shader's two-probe blend over at most 16 box tests, with `GetProbeWeight` |
| `render-indirect:121` | feature | home | Box projection: the ray's exit from the box, looked up from the box's center |
| `render-indirect:122` | feature | home | SH irradiance: nine RGB coefficients per slot from the cube's 32-texel level, read by `EvaluateProbeIrradiance` |
| `render-indirect:123` | feature | home | The probe cache: an RGBA16F cube per slot at `ReflectionProbeResolution` (128 Low and Medium, 256 High and Ultra), six levels, LRU reuse, made with the first probe in view, kept while the scene has a probe with a capture (in view or not), released when it has none; out of view only the stale holds are let go (`Strata/src/Strata/Renderer/SceneRendererReflectionProbes.cpp:200-207`, `:234-243`; `Strata/src/Strata/Renderer/SceneRenderer.h:272-275`) |
| `render-indirect:124` | feature | home | The residency hold: High priority, held whole until converted, then released to its mip tail |
| `render-indirect:125` | feature | home | The GPU conversion chain, at most two a frame with `SpreadLightingUpdates` |
| `render-indirect:126` | feature | home | The resolution takeover: new cubes filled beside the shown ones, swapped once every probe in view is converted |
| `render-indirect:127` | feature | home | The bindings: SRV 9 the cube array (a black one-slot array without probes), SRV 10 the probe buffer |
| `render-indirect:128` | feature | home | The statistics `ReflectionProbes`, `ReflectionProbeConversions`, `ReflectionProbesPending` |
| `render-indirect:129` | feature | home | The bake `lighting.bakeProbes` from end to end (own renderer, six views, pre-exposure, assembly, import, one undo step that trashes the previous bake); what its renderer sees and waits for is `new:22` |
| `new:22` | feature | home | What a bake sees and waits for: `ForBake` takes Medium's quality values as Custom, with no TAA, no texture streaming and no spreading, so a bake never depends on a person's Graphics Quality; so a capture holds no global illumination (Medium's row is Off) and no screen-space reflections (Medium's Checkerboard needs TAA); each probe's six views are rendered again every frame until nothing they show is pending (assets, proxies, shadow views, probe conversions, poses), at most two minutes, after which the result says `complete: false`; the background is the primary camera's clear color; a scene change or Play before the import ends the bake with nothing changed. Evidence: `Strata/src/Strata/Renderer/SceneRenderer.cpp:261-277`, `:3063`, `:3073`; `Strata/src/Strata/Renderer/RendererQuality.cpp:52`, `:54`; `StrataEditor/src/Editor/EditorLightingCommands.cpp:59`, `:184-210`, `:360`, `:403-407`, `:931-933`; `Docs/DeveloperGuide.md:4087-4088`, `:4968` |
| `render-indirect:130` | feature | home | Bounces by re-baking: each bake adds a bounce |
| `render-indirect:131` | feature | home | The times-of-day pattern, as the mechanism (one probe set per time, `SetActive`); the how-to is `make/reflections`' |
| `render-indirect:89` | feature | home | The probe-capture mode (`MaterialParams.w`, `LightSurface`): a bake keeps the lights' diffuse light only; taught with the bake, where a reader looks for it |
| `render-direct:63` | feature | home | The probe-capture mode as the light area lists it: `MaterialParams.w` 1 sets `LightSurface`'s specular weight to 0 (`Strata/shaders/Scene/Forward.frag.slang:84-103`); one home with `render-indirect:89`, here with the bake rather than on `indirect/seam`, because it changes the lights' direct light in a capture, not the indirect light's join |
| `render-indirect:341` | code | home | `Strata/shaders/IBL/ProbeIrradiance.comp.slang:42-87`: SH-9 projection with texel solid angles and a shared-memory reduction; with the basis at `Strata/shaders/Include/SphericalHarmonics.slang:6-17`; the band factors divided by pi |
| `render-indirect:352` | code | home | `Strata/shaders/Include/ReflectionProbes.slang:54-125`: the box-local transform, the weight, box projection and the two-probe blend |
| `render-indirect:353` | code | home | `Strata/src/Strata/Renderer/SceneRendererReflectionProbes.cpp:193-260`: the gather with its validation of transforms; `IsStronger` at lines 59-67 |
| `render-indirect:354` | code | home | `Strata/src/Strata/Renderer/SceneRendererReflectionProbes.cpp:451-506`: a capture's conversion chain reusing the sky's pipelines |
| `render-indirect:355` | code | home | `StrataEditor/src/Editor/ProbeBake.h:19-47`: what a bake is: face cameras, equirectangular assembly, the power-of-two pre-exposure, the staging folder's lifetime |
| `render-indirect:701` | open | home | Settled at the pin: in `GatherReflectionProbes` (193-429) the lambdas are `findSlot` 260-268, `holdsConverted` 269-273, `acquireSlot` 279-299, `hold` 300-311, `holdWhole` 313-319 and `convert` 320-334 of `Strata/src/Strata/Renderer/SceneRendererReflectionProbes.cpp`; the page quotes the slot and hold lambdas from these lines |
| `render-indirect:390` | figure | home | Diagram: box projection in a room, the probe at the center, the reflected ray hitting a face, the lookup from the center |
| `render-indirect:392` | figure | home | Diagram: two overlapping boxes, the blend ramps, stronger over weaker |
| `render-indirect:393` | figure | home | Diagram: the cache, 16 slots, LRU, two conversions a frame, the takeover |
| `render-indirect:395` | figure | home | Diagram: the bake's timeline (six renders, readback, assembly on jobs, write on an I/O job, import, one undo step, trash) |
| `render-indirect:439` | figure | home | Off and on: a probe in the Showcase hut (toggled with its entity) |
| `render-indirect:441` | figure | home | Box projection on and off (`lookdev.patch` uses a probe without it) |
| `render-indirect:442` | figure | home | Sweep: `BlendDistance` 0 against 1 m on two overlapping boxes with different captures |
| `render-indirect:443` | figure | home | Sweep: `ReflectionProbeResolution` 128 against 256 on a mirror ball |
| `render-indirect:444` | figure | home | Crop, before and after: a bake with the sun disk (0.7.0, from the v0.7.0 baseline set) against one without (`lookdev.patch`, crop `patch`) |
| `render-indirect:445` | figure | home | Sweep: bakes 1, 2 and 8 times, bounces adding up |
| `new:8` | figure | home | The Cornell box lit by one baked probe, in a slider with the path-traced reference of `indirect/problem` (`new:2`): the probe's SH irradiance as a coarse bounce (the bake sees the glowing panel, so the capture carries its light); the figure is captured in play (its `play` field), so no preview lighting is added, and its `complete` asserts `/previewLighting` false (pipelines.md §5.2, §5.3). Evidence: `Tools/LookDev/LookDevScene.json:253-268` (the box, which holds no probe: the recipe adds one and bakes it, `StrataEditor/src/Editor/EditorLightingCommands.cpp:872`) |
| `new:9` | not-done | home | No reflection probes captured while the game runs. Evidence: `Docs/Roadmap.md:943` ("probes are baked, so a moving sun does not relight them") and `:947` ("run-time probe capture" left for later); `Docs/Releases/0.7.0.md:410-411` |
| `new:23` | not-done | home | No gizmo for reflection probes: the Scene view draws no box for a probe's `Extents`, so a box is fitted by the walls' sizes and checked after a bake by its reflections; the page names it under "What Strata does not do" and links exercise E5, whose probe-weight view shows a box's reach. Evidence: `Strata/src/Strata/Renderer/SceneGizmos.cpp:224-345` draws lights and cameras; `git grep -n "\.Gizmo(" 822a7a46 -- Strata/src StrataEditor/src` finds only the colliders and the character controller (`Strata/src/Strata/Physics/PhysicsComponents.cpp:143-184`) and the call that draws them (`Strata/src/Strata/Renderer/SceneGizmos.cpp:176`); `git grep -l ReflectionProbeComponent 822a7a46 -- Strata/src StrataEditor/src` names no gizmo or viewport file |
| `render-indirect:496` | rule | home | Probes are baked in the editor, never at run time; a bake draws no sun disk and no lights' highlights |
| `render-indirect:498` | rule | home | Bake where the probe stands now (`Scene::GetWorldTransform`, not the cached matrix) |
| `render-indirect:500` | rule | home | A bake replaces only its own earlier capture and trashes it in the same undo step |
| `render-indirect:502` | rule | home | Captures are held whole until converted, and released after |
| `render-indirect:504` | rule | home | Conversions are spread, two a frame, in interactive renderers, not in bakes and captures |
| `render-indirect:520` | rule | home | No blocking: a capture not loaded lights nothing and only captures wait for it; GI pending shows today's light (named again on `indirect/gi-cascades`) |
| `render-indirect:550` | hands-on | home | E5: a probe-weight view behind a debug view |
| `render-indirect:551` | hands-on | home | E6: box projection by hand, checked against `GetProbeLookup` (the toy version) |
| `new:24` | hands-on | home | Exercise (trace it yourself, R32, D27): one bake followed from the command to the probe's new capture through its four stages (Render, Encode, Write, Import): `RenderNextProbe` renders the six views until nothing is pending, `PollBake` moves the stages on each frame, and the solution names the function and the thread of each stage. Evidence: `StrataEditor/src/Editor/EditorLightingCommands.cpp:85-91` (the stages), `:184-221` (`RenderNextProbe`), `:397-445` (`PollBake`) |
| `render-indirect:600` | term | home | Reflection probe |
| `render-indirect:601` | term | home | Capture and bake, two entries |
| `render-indirect:602` | term | home | Influence box, extents and blend distance, three entries |
| `render-indirect:603` | term | home | Box projection (parallax correction) |
| `render-indirect:604` | term | home | Probe priority |
| `render-indirect:605` | term | home | Probe cache and slot, two entries |
| `render-indirect:607` | term | home | HDR output and ProbeCapture, two entries |
| `render-indirect:568` | term | use | The cube array, defined on `indirect/ibl` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The forms of the seam and the probes' place in the stack | `indirect/seam` | must |
| The filter chain and filtered importance sampling | `indirect/ibl` | must |
| Spherical harmonics and texel solid angles | `basics/math-sphere` | must |
| Rays against boxes | `basics/math-geometry` | must |
| A frustum test of a bounding sphere | `draw/bounds-culling` | must |
| ECS views over components and the world transform | `world/ecs` | must |
| Resolving an asset with a priority, every frame | `draw/asset-requests` | must |
| Residency, holds and pins | `assets/residency` | must |
| Resident mip levels of a streamed texture | `draw/mip-streaming` | must |
| Power-of-two pre-exposure | `image/pre-exposure` | must |
| Jobs and I/O jobs | `core/jobs` | must |
| Reading back a render target | `gpu/readback-timing` | must |
| Importing an HDR texture | `assets/importing` | helps |
| Editor commands and one undo step per change | `editor/commands` | helps |
| The trash | `editor/trash-references` | helps |

## `indirect/ssr` — Screen-space reflections

**Covers.** The job: reflections of what is on screen, traced through the depth buffer every frame and laid over the
probes' and the sky's specular light. Transparent surfaces get none. The problem section teaches screen-space ray
marching from zero: a reflected ray is a straight line in (UV, depth) under perspective; stepping, bisection, thickness
tolerances, hierarchical-Z tracing and why Strata rejected it for grazing floors, confidence and fades, and reusing the
previous frame's color along motion vectors. A table compares linear marches, Hi-Z, stochastic SSR with temporal
reuse, planar reflections and ray-traced reflections.

The map is the diagram of the two pipelines: Checkerboard (Medium: half resolution, one pixel of each 2x2 block per
frame, 24 quadratic steps and 6 bisections, interleaved gradient noise that turns per frame, colors from the TAA history
along the hit's motion) against Spatial and SpatialHigh (High and Ultra: every pixel at full resolution, 32 or 48 steps
offset by GTAO's fixed order, validated crossings, a 5x5 resolve, the previous frame's color copy). Around it: the
component's three fields, the quality row `Reflections`, the prepass's surface target (octahedral normal, widened
roughness, metallic), the color copy (sharp up to roughness 0.05, blurred levels from 0.15), memory (about 20 MiB for
Checkerboard at 1080p, about 150 MiB more for Spatial at 4K) and the first frame of a Spatial mode, which has no copy yet
(captures render one more frame). The contract is seven rules: SSR light is visible light (ambient occlusion must not
darken what a ray found); fade only where rays leave the screen; keep only validated crossings; the Hi-Z march was
rejected; never fill an object's back in a mirror with its front's colors; Checkerboard needs TAA, the one named
exception to "nothing needs history" (`image/taa` is the decision's home); results are premultiplied. A toy version is
exercise E8: a CPU march with bisection over a synthetic depth buffer, which also shows the Hi-Z march running out of
steps over a grazing floor.

The real code, in data order: `BeginScreenRay` (the line in (UV, depth), cut at the screen's edge and at the far and
near planes, rays into the surface refused); `GetHitConfidence` (back faces get 0; the edge fade only near the exit the
ray leaves through); Checkerboard's `TraceReflection`; the Spatial trace with `BisectCrossing`, `ValidateCrossing`,
`RefineCrossing` and `RefinePlaneCrossing`, up to `MaxCandidates` rejected crossings, the last point half a pixel before
the end; `ReflectionResolve.comp`'s ratio estimator under a GGX lobe weight with plane and normal weights; the forward
mix `radiance (1 - a) + rgb` before the split sum, where only the material's occlusion map darkens what the ray found.
What went wrong before: 0.7.0 took any point behind a surface as a hit (thin posts became ghosts), faded near every edge
(sky wedges) and let AO darken wet ground; exercise E7 brings the first back and watches its test fail. An erratum: the
component's comment says "with TAA only", which is true of Checkerboard alone. What Strata does not do: reflections of
and through transparent surfaces, glass behind glass, and screen-space reflections on a clear coat (they cover its base
only; the coat's image light is the probes', the sky's or the ambient's). Tests: `GPU.SceneRenderer.SSR`,
`GPU.SceneRenderer.IndirectFlicker` with the flicker meter of `engineering/test-kinds`, `Renderer.ReflectionMetrics`.
Figures: the modes as a sweep (Off, Checkerboard with TAA, Spatial, SpatialHigh), the maximum roughness as a sweep,
crops of the edge fade, the thin posts and the wall's edge, the crescent of a ball's back, and wet ground beside an
object that AO no longer darkens; six diagrams, the screen door before and after the resolve among them. A trace
exercise follows which trace a quality row runs and what it reads. The reader can explain both traces and change them
without bringing back a fixed failure.

**Leaves out.**

- TAA's history, reprojection and jitter → `image/taa`
- Motion vectors and the motion history → `draw/motion-vectors`
- The half-resolution scene-color copy that glass reads → `light/clearcoat-transmission`
- Fresnel and F0 from the IOR → `light/reflectance`
- The flicker meter and image metrics in tests → `engineering/test-kinds`
- The look-dev shots and how they are captured → `engineering/look-dev`
- A wet floor in a game → `make/reflections`
- The `Reflections` row among the presets → `image/quality-settings`

**Fit.** `fits`: about 7,450 words against XL (8,000). Screen-space ray marching from zero, two traces, a resolve, seven
rules, six diagrams and six pictures take the most words; the toy is exercise E8's sketch, so it is not counted twice.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-indirect:293` | concept | home | Screen-space ray marching: lines in (UV, depth), stepping, bisection, thickness, Hi-Z and its rejection, confidence and fades, the previous frame's color along motion; Strata's two modes; errors: fading near every edge, any point behind a surface as a hit, back faces, SSR on rough surfaces |
| `render-indirect:137` | feature | home | The component's fields `ScreenSpaceReflections` (off), `...Intensity` (1), `...MaxRoughness` (0.5, fading over the last quarter) |
| `render-indirect:138` | feature | home | The quality row `Reflections`: Off (Low), Checkerboard (Medium), Spatial (High), SpatialHigh (Ultra), and `GetScreenReflectionSteps` |
| `render-indirect:139` | feature | home | The surface target: the prepass variant `ST_PREPASS_SURFACE` writing the octahedral view normal, widened roughness and metallic (RGBA16F) |
| `render-indirect:140` | feature | home | The shared ray setup `BeginScreenRay` |
| `render-indirect:141` | feature | home | Hit confidence: back-facing hits 0; the edge fade only where the ray leaves the screen |
| `render-indirect:142` | feature | home | The Checkerboard trace and its use of the TAA history |
| `render-indirect:143` | feature | home | The Spatial trace with validated crossings and its candidate budget |
| `render-indirect:144` | feature | home | The previous frame's color copy (B10G11R11), sharp up to roughness 0.05, blurred levels from 0.15 |
| `render-indirect:145` | feature | home | The spatial resolve: a 5x5 ratio estimator, kernel (0.5, 1, 1, 1, 0.5), GGX-lobe weight, plane and normal weights |
| `render-indirect:146` | feature | home | The forward mix, premultiplied, over the probes' and the sky's specular before the split sum |
| `render-indirect:147` | feature | home | The pending first frame of the Spatial modes, and the extra frame captures render |
| `render-indirect:148` | feature | home | Memory: Checkerboard about 20 MiB at 1080p, Spatial about 150 MiB more at 4K (`ReflectionsBytes`) |
| `render-indirect:149` | feature | home | Transparent surfaces get none (`#ifndef ST_FORWARD_TRANSPARENT` around the sample, `Strata/shaders/Scene/Forward.frag.slang:141-147`) |
| `render-indirect:111` | feature | home | SSR keeps its light: only the material's occlusion map darkens what a screen ray found (`ScreenReflectionOcclusion`) |
| `render-indirect:356` | code | home | `Strata/shaders/Include/ScreenReflections.slang:39-102`: `BeginScreenRay` and `GetHitConfidence` |
| `render-indirect:357` | code | home | `Strata/shaders/Effects/ScreenSpaceReflections.comp.slang:51-115`: the classic march, bisection and thickness, colors from the TAA history along the hit's motion |
| `render-indirect:358` | code | home | `Strata/shaders/Effects/ScreenSpaceReflectionsSpatial.comp.slang:151-274`: validated crossings, the central algorithm, shown in two pieces |
| `render-indirect:359` | code | home | `Strata/shaders/Effects/ReflectionResolve.comp.slang:75-120`: the ratio estimator under the GGX lobe weight with plane and normal weights |
| `render-indirect:397` | figure | home | Diagram: a view-space ray as a line in (UV, depth), cut at the edge and the far plane, steps denser near the start, bisection |
| `render-indirect:399` | figure | home | Diagram, two panels: a ray passing behind a thin post (0.7.0's ghost) against a validated crossing; the plane crossing at a wall's top edge |
| `render-indirect:401` | figure | home | Diagram: the Checkerboard and Spatial pipelines with their memory per pixel |
| `render-indirect:403` | figure | home | Diagram: why the screen cannot show an object's back (the crescent) |
| `render-indirect:404` | figure | home | Diagram: the edge fade only near the edge the ray leaves through |
| `render-indirect:446` | figure | home | Sweep: Off, Checkerboard with TAA, Spatial and SpatialHigh on `lookdev.mirror`, by the quality row and Post Process |
| `render-indirect:448` | figure | home | Sweep: `ScreenSpaceReflectionsMaxRoughness` 0.2 against 0.5 on the polished, satin and glossy crops of `lookdev.mirror` |
| `render-indirect:449` | figure | home | Crop: the edge fade on wet ground (`lookdev.wet.sunward`, left and right) |
| `render-indirect:450` | figure | home | Crop: thin posts and a wall's edge (`lookdev.sheet`, `post-wall`) |
| `render-indirect:451` | figure | home | Crop: the crescent of a ball's back (`lookdev.sheet.angle`, `crescents`) |
| `render-indirect:452` | figure | home | Diagram: the rough sheet's reflection before the resolve (the screen door of single samples) and after it; a diagram because tier 2 has no capture switch that skips the resolve (R34, D42: one request extends tier 2) |
| `render-indirect:453` | figure | home | Crop: AO no longer darkening what SSR found, wet ground beside an object (`lookdev.wet`, `edge`) |
| `render-indirect:486` | rule | home | SSR light is visible light: AO must not darken what a screen ray found (0.7.0's dark smudges on wet ground) |
| `render-indirect:488` | rule | home | Fade only where rays leave the screen (`GetHitConfidence`); fading near every edge drew sky wedges |
| `render-indirect:489` | rule | home | Keep only validated crossings in Spatial; "any point behind a surface" read thin posts as ghosts |
| `render-indirect:491` | rule | home | The Hi-Z march was rejected for Spatial: grazing rays over floors ran out of iterations (stripes at 4K); the textbook algorithm is not always right |
| `render-indirect:493` | rule | home | Never fill an object's back in a mirror with its front's colors ("option F", tried and rejected: front-lit rims) |
| `render-indirect:494` | rule | home | Checkerboard needs TAA: Medium's named exception to "nothing needs history", keeping 0.6.0's costs |
| `render-indirect:495` | rule | home | Premultiplied results: a texel that found nothing adds no black at a reflection's edge |
| `render-indirect:552` | hands-on | home | E7: bring back 0.7.0's acceptance in the Spatial trace and watch `GPU.SceneRenderer.SSR` "Thin posts..." fail |
| `render-indirect:553` | hands-on | home | E8: a CPU march with bisection over a synthetic depth buffer, and the Hi-Z march's grazing-floor failure (the toy version) |
| `new:25` | hands-on | home | Exercise (trace it yourself, R32, D27): which trace a quality row runs in a frame and what it reads: the Spatial modes need the color copy of the renderer's previous frame without a cut or a reset, Checkerboard needs TAA with a history of more than one frame, and `ReflectionParams.x` tells the forward pass to sample the result; the solution names the lines and says why a bake and a first frame get none. Evidence: `Strata/src/Strata/Renderer/SceneRenderer.cpp:2982-2984`, `:3047-3065`, `:3118`; `Strata/shaders/Scene/Forward.frag.slang:139-147` |
| `render-indirect:707` | open | home | The component's comment contradicts the Spatial modes; the page follows the code and states the erratum (`new:11`) |
| `new:10` | not-done | home | No reflections of or through transparent surfaces, no glass behind glass, and no screen-space reflections on a clear coat: they cover the coat's base only, and the coat's image light comes from the probes, the sky or the ambient (`SampleSpecularLight`). Evidence: `Docs/Roadmap.md:939-942` ("screen-space reflections cover a clear coat's base only and trace no transparent surface"; glass behind glass does not show) and `:947-948` ("SSR for transparent surfaces" left for later); `Strata/shaders/Scene/Forward.frag.slang:141-147` (no sample on transparent surfaces), `:323-333` (the coat's image light) |
| `new:11` | erratum | home | The comment at `Strata/src/Strata/Renderer/RendererComponents.h:313-314` says screen-space reflections work "with TAA only"; at the pin only Checkerboard reads the TAA history, and Spatial and SpatialHigh run with or without TAA. Evidence: `Strata/src/Strata/Renderer/RendererQuality.h:88-91` |
| `render-indirect:608` | term | home | Screen-space reflections (SSR) |
| `render-indirect:610` | term | home | Surface target, its own entry; "prepass" is `render-core:733`'s entry (depth prepass) |
| `render-indirect:612` | term | home | Ray march, step and bisection, three entries |
| `render-indirect:613` | term | home | Thickness tolerance |
| `render-indirect:614` | term | home | Candidate and validated crossing, two entries |
| `render-indirect:615` | term | home | Hi-Z (hierarchical depth) march |
| `render-indirect:616` | term | home | Confidence |
| `render-indirect:621` | term | home | Checkerboard, Spatial and SpatialHigh, Strata's three modes |
| `render-indirect:622` | term | home | Ratio estimator |
| `render-indirect:197` | feature | use | The flicker meter (`GPUSceneIndirectFlickerTests.cpp`, `ReflectionMetrics.h`) in the tests of this page; its home is `engineering/test-kinds` |
| `render-image:700` | term | use | The TAA history Checkerboard reads (`render-indirect:619` repeats it) |
| `render-indirect:520` | rule | link | No blocking, as the probes fall back for a ray that found nothing; taught on `indirect/probes` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Projection, NDC, UVs and reversed Z | `gpu/coordinates` | must |
| The depth prepass and its variants | `gpu/frame-tour` | must |
| Motion vectors | `draw/motion-vectors` | must |
| TAA's history and reprojection, and "nothing needs history to look right" | `image/taa` | must |
| Octahedral encoding of a unit vector | `basics/math-sphere` | must |
| Interleaved gradient noise | `basics/math-probability` | must |
| The scene-color copy | `light/clearcoat-transmission` | must |
| Premultiplied alpha | `light/clearcoat-transmission` | must |
| Probes as the fallback of a ray that found nothing | `indirect/probes` | must |
| The specular gather and the specular occlusion it replaces | `indirect/seam` | must |
| GTAO's fixed 4x4 order (the Spatial steps' offsets) and Lagarde's specular occlusion | `indirect/ao` | must |
| The GGX lobe and Fresnel from the IOR | `light/reflectance` | must |
| Pre-exposure (the history's scale) | `image/pre-exposure` | must |
| Compute shaders and shared memory | `gpu/compute` | must |
| Quality rows and their presets | `image/quality-settings` | helps |
| The flicker meter | `engineering/test-kinds` | helps |
| The look-dev harness | `engineering/look-dev` | helps |

## `indirect/gi-voxels` — Global illumination I: a voxel copy of the world

**Covers.** The job: the first half of Strata's experimental global illumination, a voxel copy of the static world
around the camera that the cascades of `indirect/gi-cascades` march. The page first shows the whole at a glance: the
scene asks with Post Process `GlobalIllumination` (off by default; `GlobalIlluminationIntensity` 0 to 4, with an
inactive reason), the quality row `GlobalIllumination` (Off at Low and Medium, Low and High layouts), the GPU stage
`GPU.RadianceCascades` between `GPU.AO` and `GPU.Reflections`, and the overview diagram from the geometry pool to the
forward gather. The opening picture is GI off and on in the Cornell box; the voxels view shows what this page builds.

The problem section is one paragraph that links `indirect/problem`'s families. The concept is taught from zero:
voxelization by a conservative triangle-box test (Akenine-Moller's separating axes), buffer atomics, solid fill by
counting windings along columns, two-sided voxels, clipmap levels each twice the size of the one before, toroidal
addressing so that a scroll writes only the slabs that entered, anchors so that the same scene gives the same bits
wherever the camera is, and budgets per frame. The layout comes from first principles in `ComputeLayout`: High has four
voxel levels of 128x64x128 from 10 cm and four cascades from 0.5 m; Low three levels of 64x32x64 from 20 cm and three
cascades from 1 m; the field's extent; High bounces on and Low once (`indirect/gi-cascades` says why); the memory per
view that runs GI, at any resolution, 146.4 MiB at High and 22.6 MiB at Low, so two views that run GI hold it twice
(exercise E9 computes it).

The contract: anchors for voxel coordinates (worlds stay within 20 km); walls thicker than two voxels (20 cm at High,
40 cm at Low) or they turn two-sided and dark from both sides; GI traces world data, never the screen (`indirect/problem`).
A toy version is exercise E10: the triangle-box test on the CPU, voxelizing a box against `Tests::ReferenceVoxels`. The
real code: the CPU clipmap (`VoxelClipmap`: per level a camera-centered window snapped to 4-voxel steps, toroidal
storage, the region queue of changes, slabs and whole windows, budgets of 500,000 and 4 million triangles a frame) and
its arithmetic (`GetVoxelIndex`, `GetWindowMinimum`, `GetTexel`, `GetScrollSlabs`, `GetAnchorVoxel`); what enters the
voxels (indexed opaque and alpha-masked submeshes of the static arena, a level of detail within half a voxel, material
means; movers wait 30 frames, `indirect/gi-limits`); the GPU passes `VoxelTriangles` (a thread per triangle),
`VoxelTiles` (large triangles, indirect), `VoxelFill` (closed meshes become solid) and `VoxelFinalize` (material,
emission in RGB9E5, normal, two-sided detection); the closed-mesh test (every directed edge has one opposite). The
voxel classes diagram shows a surface, a solid interior, a two-sided thin wall and an alpha-masked partial voxel.

Alternatives: sparse voxel octrees (SVOGI), voxel cone tracing on clipmaps (VXGI), signed distance fields (Lumen),
DDGI's ray-traced probes. Tests: `Renderer.GlobalIlluminationLayout` ("Memory adds up"), `Renderer.VoxelClipmap`,
`Renderer.Mesh` ("Closed meshes are found"), and a trace of one batch through the four voxel passes. Two errata: a stale
memory comment and the cascades' direction counts. Figures: Low against High as a sweep, the clipmap and the voxel
classes as diagrams, the overview diagram, and the voxels view and GI off and on, both homed on `indirect/gi-cascades`.
The reader can explain how the world becomes voxels and change the voxelizer safely.

**Leaves out.**

- The families of GI and why Strata traces the world → `indirect/problem`
- Light injection, the cascades, the field and the GI debug views → `indirect/gi-cascades`
- Moving and skinned objects, local lights and the other limits → `indirect/gi-limits`
- The geometry pool's arenas and submeshes → `gpu/geometry-pool`
- The render scene's proxies and change logs → `draw/render-scene`
- The 20 km limit of worlds → `worlds/why-streaming`
- Turning GI on in a game → `make/gi`

**Fit.** `fits`: about 6,050 words against L (5,000). The GI at a glance, the concept of voxelization and clipmaps in
eight parts, three excerpts and the four GPU passes take the most words; about 450 words remain below L's top. Phase B
must look again at: which GI batches landed after the pin (`render-indirect:698`), the files the survey did not read in
full (`VoxelClipmap.cpp`, the bodies of `VoxelTriangles`, `VoxelTiles`, `VoxelFill`, `VoxelFinalize`, most of
`SceneRendererGlobalIllumination.cpp`: `render-indirect:687`), the spec's "Review corrections" (`render-indirect:695`),
the layout's numbers and the two errata, the memory per view and whether Low still bounces once (`render-indirect:163`,
`:164`).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-indirect:309` | concept | home | Voxelization and clipmaps: conservative triangle-box overlap, atomics, solid fill by winding, two-sided voxels, levels, toroidal addressing and scrolling, anchors, budgets; errors: recomputing the volume when the camera moves, floating-point origins far from zero |
| `render-indirect:162` | feature | home | The scene's ask: `PostProcessComponent::GlobalIllumination` (off) and `GlobalIlluminationIntensity` (1, 0 to 4, with an inactive reason) |
| `render-indirect:163` | feature | home | The quality row `Renderer.Quality.GlobalIllumination`: Off, Low, High (Off at Low and Medium); High bounces on and Low once (`GlobalIlluminationLayout::Bounces`, taught on `indirect/gi-cascades`) |
| `render-indirect:164` | feature | home | The layout of Low and High and its memory (146.4 MiB and 22.6 MiB) per view that runs GI, at any resolution (`Strata/src/Strata/Renderer/RendererQuality.h:166-168`; `Docs/DeveloperGuide.md:4975`); the direction counts per cascade as the erratum `new:13` states them |
| `render-indirect:165` | feature | home | The CPU clipmap: windows snapped to 4-voxel steps, toroidal storage, anchors, the region queue, budgets |
| `render-indirect:166` | feature | home | What enters the voxels: static indexed opaque and alpha-masked submeshes, LOD within half a voxel, material means; movers excluded for 30 frames |
| `render-indirect:167` | feature | home | The GPU voxelization: `VoxelTriangles`, `VoxelTiles`, `VoxelFill`, `VoxelFinalize`, dispatched in `RecordGlobalIllumination` |
| `render-indirect:168` | feature | home | The closed-mesh test (`MeshUtils::IsClosed`, `Mesh::IsClosed`) |
| `render-indirect:183` | feature | home | The GPU stage `GPU.RadianceCascades`, after `GPU.AO` and before `GPU.Reflections` |
| `render-indirect:361` | code | home | `Strata/src/Strata/Renderer/GlobalIlluminationLayout.cpp:147-192`: a layout from first principles (voxel levels, cascades with spacing x2, directions x4, intervals x4, the field's extent) |
| `render-indirect:362` | code | home | `Strata/shaders/Include/Voxelize.slang:160-196`: Akenine-Moller's triangle-box overlap by separating axes |
| `new:14` | code | home | `Strata/src/Strata/Renderer/GlobalIlluminationLayout.h:142-167`: the clipmap's arithmetic: voxel index, window minimum, toroidal texel, scroll slabs, anchors, and the camera-independent voxel coordinate |
| `render-indirect:405` | figure | home | Diagram: the GI overview from the geometry pool to the forward gather, the previous field feeding the injection |
| `render-indirect:407` | figure | home | Diagram: the clipmap levels (10, 20, 40, 80 cm), a scroll writing only the slabs that entered, the anchor cells |
| `render-indirect:409` | figure | home | Diagram: the voxel classes (surface, solid interior, two-sided thin wall, alpha-masked partial) |
| `render-indirect:457` | figure | home | Sweep: the quality row's Low against High in the same room: the shot `lookdev.room` at Low and High, with the Post Process's `GlobalIllumination` set as the Setup of `lookdev.sunroom.lit.gi` sets it, since the room's own scene does not ask for GI (`Tools/LookDev/Shots.json:28`, `:141`; `Tools/LookDev/LookDevScene.json:22`) |
| `render-indirect:513` | rule | home | Anchors for voxel coordinates: the same scene voxelizes to the same bits wherever the camera is; worlds stay within 20 km |
| `render-indirect:517` | rule | home | Walls must be thicker than two voxels (20 cm High, 40 cm Low), or they turn two-sided and dark from both sides |
| `render-indirect:554` | hands-on | home | E9: compute the Low layout's memory by hand and check "Memory adds up" |
| `render-indirect:555` | hands-on | home | E10: the CPU triangle-box test, a voxelized box against `Tests::ReferenceVoxels` (the toy version) |
| `new:26` | hands-on | home | Exercise (trace it yourself, R32, D27): one batch of the frame's regions followed from the CPU's frame to the voxels: `PrepareGlobalIllumination` builds the frame with the clipmap, and `RecordGlobalIllumination` clears the scratch buffer, dispatches `VoxelTriangles` in parts of at most `c_MaxDispatchGroups` groups, `VoxelTiles` as an indirect dispatch whose group count `VoxelTriangles` wrote, then `VoxelFill` per column and `VoxelFinalize` per voxel, with a barrier after each; the solution names the lines and says why the tiles' dispatch is indirect. Evidence: `Strata/src/Strata/Renderer/SceneRendererGlobalIllumination.cpp:514-524`, `:639-644`, `:780-830` |
| `new:12` | erratum | home | The comment at `Strata/src/Strata/Renderer/RendererQuality.h:166-168` gives 18 MiB at Low and 111 MiB at High; `GetMemory` gives 23,659,120 and 153,469,552 bytes (22.6 and 146.4 MiB). Evidence: `StrataTests/src/Renderer/GlobalIlluminationLayoutTests.cpp:153`, `:167`; `Docs/DeveloperGuide.md:4975-4976` |
| `new:13` | erratum | home | `Docs/DeveloperGuide.md:4974` and the inventory (`render-indirect:164`, figure `render-indirect:411`) give the cascades 16 to 1,024 directions; at the pin cascade 0 marches cascade 1's 64 directions, so High's cascades have 64, 64, 256 and 1,024 and Low's 64, 64 and 256. Evidence: `Strata/src/Strata/Renderer/GlobalIlluminationLayout.cpp:167-169`; `StrataTests/src/Renderer/GlobalIlluminationLayoutTests.cpp:102-105`, `:127-129` |
| `render-indirect:624` | term | home | Voxel and voxelization, two entries |
| `render-indirect:625` | term | home | Clipmap |
| `render-indirect:626` | term | home | Toroidal addressing |
| `render-indirect:627` | term | home | Slab, region, brick and anchor, four entries |
| `render-indirect:628` | term | home | Triangle-box overlap (Akenine-Moller) |
| `render-indirect:629` | term | home | Winding and solid fill, two entries |
| `render-indirect:630` | term | home | Closed mesh |
| `render-indirect:631` | term | home | Two-sided voxel |
| `render-indirect:632` | term | home | RGB9E5 |
| `render-indirect:455` | figure | use | GI off and on in the Cornell box as the opening picture; its home is `indirect/gi-cascades` |
| `render-indirect:456` | figure | use | The `voxels` view of the sun room (`lookdev.sunroom.view.voxels`); its home is `indirect/gi-cascades` |
| `render-indirect:508` | rule | use | GI traces world data, never the screen; the decision's home is `indirect/problem` |
| `render-indirect:515` | rule | link | Movers stay out of the voxels for 30 frames; taught on `indirect/gi-limits` |
| `render-indirect:303` | concept | link | The families of GI, taught on `indirect/problem` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The families of GI and the decision to trace world data | `indirect/problem` | must |
| The geometry pool's static arena and submeshes | `gpu/geometry-pool` | must |
| Render-scene proxies, their records and change logs | `draw/render-scene` | must |
| Compute atomics and indirect dispatches | `gpu/compute` | must |
| Separating axes and triangle-box tests | `basics/math-geometry` | must |
| Floating point far from the origin | `basics/numbers` | must |
| Levels of detail of a mesh | `draw/lod` | helps |
| Where the field joins the shading | `indirect/seam` | must |
| A material's base color, emission and their maps | `light/materials` | must |
| Inactive reasons (`SetInactiveReason`): a property that another property turns off | `world/reflection` | helps |
| Quality rows and their presets | `image/quality-settings` | helps |
| The 20 km limit of worlds | `worlds/why-streaming` | helps |

## `indirect/gi-cascades` — Global illumination II: radiance cascades and the irradiance field

**Covers.** The job: from the voxels to light on surfaces, every frame and without history. The page holds light
injection, the level downsample, probe validity and relocation, probe weights, the cascade marches and their merge, the
field reduce, multi-bounce by re-injection, the forward gather and the join, and GI's debug views and statistics. The
problem section is one paragraph that links `indirect/problem`; then three ideas are taught from zero. Radiance
cascades: the penumbra condition (near a probe, light needs few directions and many places; far away, the opposite),
cascades with four times the directions and four times the interval length, a child's unabsorbed ray continued in its
parents' merged rays, only the top cascade reading the sky, and the lead-in and overlap rules against leaks and doubled
light at interval borders. Probe fields and visibility: trilinear interpolation, dead probes, relocation, DDGI's
Chebyshev test on depth moments and why Strata weights by a voxel-transmittance guard instead (fence crawl), normal and
view bias, and the error of renormalizing a weight that vanishes. Multi-bounce by re-injection: last frame's field read at
each voxel, a geometric series of albedo, settle frames, still frames identical bit for bit; "uses last frame" is not
temporal accumulation; only High bounces on, and Low bounces once, because Low's coarser field with every bounce makes
the Cornell box's ceiling about 1.8 times as bright as High's. The guarantee these rules buy is taught as its own case:
a sealed room stays dark (the sun lights no voxel inside it, and of two rooms that share a wall the sealed one stays
dark, whether the light's source is on screen or not), the case from which a reader learns why the lead-in, the overlap
and the guard exist.

The map lists the passes in order (`VoxelInject`, `VoxelDownsample`, `ProbeValidity`, `ProbeWeights`, `CascadeMarch`
from the top cascade down to 1, `FieldReduce`) and then the forward pass's `SampleIrradianceField`, with three diagrams
(the cascades, the field gather, re-injection over frames). The contract: captures and the project picture wait for GI
to settle, within bounds; GI's constants live in their own buffer at b3, not in `FrameConstants`, for a reason the
engine's documents leave unexplained (added fields made recompiled GTAO and SSR repeat differently), and the page says
so; while GI is pending a surface keeps today's light; a frame without GI keeps the old expression bit for bit (the
decision's home for GI is `indirect/gi-limits`). A toy version is exercise E11: radiance cascades in 1D, two cascades and
the merge rule against brute force.

The real code: injection (every voxel of every level every frame: albedo times the sun's irradiance times a shadow walk
through the voxels, plus emission, plus last frame's field); the downsample; validity, the move off surfaces and the
relocation of cascade-0 probes (four rings of 26 directions); the weights (eight parents' trilinear weights times
validity times transmittance); the march in `GIMarch.slang` (front to back with transmittance, runs, the lead-in, the
depth moments) and the merge in `CascadeMarch.comp`; the field reduce (cascade 0's 64 directions continued by cascade 1,
summed into an ambient cube of six RGBA16F faces per probe, with depth moments in a 10x10 octahedral tile); multi-bounce
(`BounceGain`, albedo clamped to 0.9, `GetSettleFrames`: exercise E12 derives 12 and 17 frames for albedos 0.58 and
0.73); the forward gather (eight cascade-0 probes around the normal-biased point, trilinear times validity times facing
times the voxel guard, the minimum-visible normalization, the fade at the field's edge, `PushOutOfSolid`); the level
sampling; the join (`ReflectionParams.y` and `.z`: today's diffuse times 1 - w plus the field times w, specular
untouched, `x * 1 + 0` where w is 0). Then the debug views `voxels`, `gi`, `open` and `probes` (a GI view runs GI even
where the scene does not ask or the row is Off, and at Off shows High's layout) and the statistics and readbacks, read
as `light/measuring-light` teaches. Alternatives: DDGI's Chebyshev weighting, an octahedral-tile field and an SH field
(both tried and not landed), voxel cone tracing, screen-space GI (refused by the decision). Tests: the
`GPU.SceneRenderer.GlobalIllumination` suites (`Join`, `Bounce`, `Stitching`, `Room`) and the CPU references, and a
trace of `GlobalIlluminationIntensity` from the Post Process to the join. Figures: GI off and on in the Cornell box in a
slider with the path-traced reference, the four GI views on the Cornell box and the sun room, the sealed room's `gi`
view beside the open sun room's, the sun room at `GlobalIlluminationIntensity` 0, 1 and 2, and one bounce against every
bounce as a diagram. The reader can follow one frame of GI from the voxels to a pixel.

**Leaves out.**

- The voxels, the clipmap, the layout and the voxelizer → `indirect/gi-voxels`
- What GI does not do, and the bit-for-bit decision for GI → `indirect/gi-limits`
- Transmittance and front-to-back marching through a medium, in general → `light/atmosphere`
- The other debug views and how statistics are read → `light/measuring-light`
- Waiting for GI in captures from a client → `editor/camera-viewport`
- Trying GI in a game → `make/gi`

**Fit.** `fits`: about 7,550 words against XL (8,000). Three ideas from zero, eleven stages, five excerpts, the sealed
room and eight figures, four of them diagrams, take the most words. Phase B must look again at: the stages that changed
after the pin (the GI batches still landing, `render-indirect:698`), the bodies the survey did not read
(`ProbeValidity`, `ProbeWeights`, `FieldReduce`, `Include/GIProbes.slang`, `Include/GlobalIllumination.slang`:
`render-indirect:687`), the spec's "Review corrections" (`render-indirect:695`), the list of statistics and the
direction counts (`new:13`), whether Low still bounces once (`render-indirect:175`), the sealed-room tests (`new:27`)
and the GI views' exception (`render-indirect:180`).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-indirect:313` | concept | home | Radiance cascades: the penumbra condition, 4x directions and 4x intervals, the merge, only the top reading the sky; the error of leaks or doubling at interval borders |
| `render-indirect:318` | concept | home | Probe fields and their visibility: trilinear probes, dead probes, relocation, DDGI's Chebyshev test and Strata's voxel guard, normal and view bias; the error of renormalizing a vanishing weight |
| `render-indirect:322` | concept | home | Multi-bounce by re-injection and convergence: the geometric series, settle frames, determinism without temporal blending |
| `render-indirect:169` | feature | home | Light injection (`VoxelInject.comp`) |
| `render-indirect:170` | feature | home | The level downsample (`VoxelDownsample.comp`) |
| `render-indirect:171` | feature | home | Probe validity, move and relocation (`ProbeValidity.comp`) |
| `render-indirect:172` | feature | home | Probe weights (`ProbeWeights.comp`) |
| `render-indirect:173` | feature | home | The cascade march and the merge, top cascade down to 1 |
| `render-indirect:174` | feature | home | The field reduce: ambient cubes and depth moments per cascade-0 probe |
| `render-indirect:175` | feature | home | Multi-bounce by re-injection: `BounceGain`, the clamped albedo, `GetSettleFrames`, `SettleGlobalIllumination`; High bounces on and Low once (`GlobalIlluminationLayout::Bounces`), because Low's coarser field with every bounce makes the Cornell box's ceiling about 1.8 times as bright as High's (165 to 235 nits per albedo against 89 to 142); the test "High bounces on, Low once" (`Strata/src/Strata/Renderer/GlobalIlluminationLayout.h:97-100`, `GlobalIlluminationLayout.cpp:190`; `StrataTests/src/Renderer/GlobalIlluminationLayoutTests.cpp:525`; `Docs/DeveloperGuide.md:5128`, `:5269`) |
| `render-indirect:176` | feature | home | Sampling the field in the forward pass (`SampleIrradianceField`, `ReadAmbientCube`, `GetFieldWeight`, `PushOutOfSolid`) |
| `render-indirect:177` | feature | home | Level sampling: the finest level whose valid box holds the point, blended by the distance from the camera |
| `render-indirect:178` | feature | home | The join: `ReflectionParams.y` and `.z`, today's diffuse times 1 - w plus the field times w, specular untouched, 0.7.0's image when off |
| `render-indirect:179` | feature | home | The field's constants at b3 in their own buffer, not in `FrameConstants` |
| `render-indirect:180` | feature | home | The GI debug views `voxels`, `gi`, `open`, `probes` (`DrawVoxelView`, `DrawProbeView`); a GI view runs GI even where the scene does not ask or the row is Off, and at Off it shows High's layout, the one exception to "nothing is made when off" (`Strata/src/Strata/Renderer/SceneRenderer.cpp:3069-3074`; `Docs/DeveloperGuide.md:4966-4967`) |
| `render-indirect:181` | feature | home | The GI statistics and readbacks |
| `render-indirect:182` | feature | home | Capture waits: `viewport.capture` and the project picture wait for `GlobalIlluminationSettled` |
| `render-indirect:363` | code | home | `Strata/shaders/Include/GIMarch.slang:21-76`: the front-to-back march with transmittance, runs, the lead-in and the depth moments |
| `render-indirect:364` | code | home | `Strata/shaders/GI/CascadeMarch.comp.slang:25-100`: the merge into eight parents' directions; only the top reads the sky |
| `render-indirect:365` | code | home | `Strata/shaders/Include/GIField.slang:181-236`: the forward gather; with `ReadAmbientCube` at lines 41-51 |
| `render-indirect:366` | code | home | `Strata/src/Strata/Renderer/GlobalIlluminationLayout.cpp:405-412`: frames until a bounce adds less than 0.25% |
| `render-indirect:367` | code | home | `Strata/shaders/Include/IndirectLight.slang:109-118`: the field gather; with the join at `Strata/shaders/Scene/Forward.frag.slang:301-321`, `x * 1 + 0` where the field's weight is 0 |
| `render-indirect:411` | figure | home | Diagram: the radiance cascades (probe grids 0.5, 1, 2, 4 m; directions per probe as `new:13` gives them; intervals; lead-in and overlap; the merge to eight parents) |
| `render-indirect:413` | figure | home | Diagram: the field gather (the point, normal and view bias, eight probes, facing, the guard through the voxels, a dead probe) |
| `render-indirect:415` | figure | home | Diagram: re-injection over frames, the first k terms after k frames, the settle curve |
| `render-indirect:455` | figure | home | Off and on: GI in the Cornell box (`lookdev.cornell` with Post Process `GlobalIllumination`, quality High), in a slider with the path-traced reference (`new:2` of `indirect/problem`) |
| `render-indirect:456` | figure | home | The GI views: `lookdev.cornell.view.gi`, and the sun room's `lookdev.sunroom.view.gi`, `lookdev.sunroom.view.open`, `lookdev.sunroom.view.voxels` and `lookdev.sunroom.view.probes` (`Tools/LookDev/Shots.json:132-135`, `:149`); the Cornell box has a shot of its `gi` view only, so its other three views need a recipe |
| `render-indirect:458` | figure | home | Diagram: one bounce against every bounce, the light of each bounce adding up over frames; a diagram because tier 2 has no capture switch for `BounceGain` 0, which only the tests set (R34, D42: one request extends tier 2) |
| `new:27` | concept | home | A sealed room stays dark: the sun lights no voxel inside it, and of two rooms that share a wall the sealed one stays dark, whether the light's source is on screen or not; GI's main guarantee against leaks, the case from which a reader learns why the lead-in, the overlap and the guard exist. Evidence: `StrataTests/src/Renderer/GPUSceneGlobalIlluminationRoomTests.cpp:443` ("Paired rooms: the sealed one stays dark"), `:716` ("The sun lights no voxel inside a sealed room"), `:1169` ("A sealed room stays dark"), in the suite `GPU.SceneRenderer.GlobalIlluminationRoom`; `Docs/Manual/Lighting.md:325` |
| `new:28` | figure | home | The sealed room's `gi` view (`lookdev.sealedroom.view.gi`) beside the open sun room's (`lookdev.sunroom.view.gi`), from the same camera. Evidence: `Tools/LookDev/Shots.json:137`, `:132` |
| `new:29` | figure | home | Sweep of GI's main setting: the sun room at `GlobalIlluminationIntensity` 0, 1 and 2 (the shot `lookdev.sunroom.lit.gi`, whose Setup turns GI on, with the intensity set as well); at 0 the field still replaces today's diffuse light inside its reach, scaled to nothing. Evidence: `Tools/LookDev/Shots.json:141`; `Strata/src/Strata/Renderer/SceneRenderer.cpp:3325-3330` (the intensity clamped to 0 to 4 as `ReflectionParams.z`); `Strata/shaders/Scene/Forward.frag.slang:311-319` |
| `render-indirect:511` | rule | home | GI's constants live in their own buffer at b3; a new frame constant must check the `ao` view's repeats |
| `render-indirect:519` | rule | home | Captures and the project picture wait for GI to settle, within bounds: bounces arrive one frame each |
| `render-indirect:703` | open | home | The cause of the non-repeating GTAO and SSR after new frame constants is unexplained in the engine's own documents; the page states it as open, with the rule it led to |
| `render-indirect:556` | hands-on | home | E11: radiance cascades in 1D, two cascades and the merge rule against brute force (the toy version) |
| `render-indirect:557` | hands-on | home | E12: derive `GetSettleFrames` for albedos 0.58 and 0.73 (12 and 17) |
| `new:30` | hands-on | home | Exercise (trace it yourself, R32, D27): `GlobalIlluminationIntensity` followed from the Post Process to a pixel: the CPU sets `ReflectionParams.y` to 1 and `.z` to the clamped intensity only where the scene asked, the field ran and it is not pending, and the forward pass scales the field's irradiance by `.z` and weighs it by the field's weight; the solution names the lines and says what a pending frame draws. Evidence: `Strata/src/Strata/Renderer/SceneRenderer.cpp:3320-3330`; `Strata/shaders/Scene/Forward.frag.slang:303-321` |
| `render-indirect:586` | term | home | Ambient cube |
| `render-indirect:633` | term | home | Light injection |
| `render-indirect:634` | term | home | Probe, cascade, interval and direction tile, four entries |
| `render-indirect:635` | term | home | Radiance cascades |
| `render-indirect:636` | term | home | Merge and miss rule, two entries |
| `render-indirect:637` | term | home | Lead-in and overlap, two entries |
| `render-indirect:638` | term | home | Occupancy, its own entry; transmittance is `render-direct:747`'s entry (participating media) |
| `render-indirect:639` | term | home | Dead probe, validity and relocation, three entries |
| `render-indirect:640` | term | home | Irradiance field |
| `render-indirect:641` | term | home | Depth moments and the Chebyshev test (DDGI), two entries |
| `render-indirect:642` | term | home | Guard (voxel guard) |
| `render-indirect:643` | term | home | Normal bias and view bias, two entries, qualified against the shadows' normal offset (`render-direct:719`) |
| `render-indirect:644` | term | home | Open share |
| `render-indirect:645` | term | home | Re-injection, multi-bounce and bounce gain, three entries; "multi-bounce" qualified against multi-bounce AO (`render-indirect:597`) |
| `render-indirect:646` | term | home | Settled and pending, two entries |
| `render-indirect:647` | term | home | Join |
| `new:13` | erratum | use | The direction counts of the cascades, stated as the code gives them |
| `render-indirect:520` | rule | use | No blocking: GI pending shows today's light; taught on `indirect/probes` |
| `render-indirect:510` | rule | link | A frame without GI keeps the old expression bit for bit; the decision for GI is taught on `indirect/gi-limits` |
| `new:2` | figure | use | The path-traced reference of `indirect/problem`, compared in the slider of `render-indirect:455` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The voxels, their levels, anchors and classes | `indirect/gi-voxels` | must |
| Transmittance and marching front to back through a medium | `light/atmosphere` | must |
| Solid angles, octahedral maps and integrating over directions | `basics/math-sphere` | must |
| Trilinear interpolation | `basics/math-interpolation` | must |
| Powers and logarithms (the settle frames) | `basics/numbers` | must |
| A geometric series and its sum | `basics/math-interpolation` | must |
| Ambient occlusion and the multi-bounce fit the field does without | `indirect/ao` | must |
| The debug views and how their statistics are read | `light/measuring-light` | must |
| Emission in nits | `light/materials` | must |
| Readbacks polled per frame | `gpu/readback-timing` | must |
| The seam's field gather and the forms | `indirect/seam` | must |
| Temporal accumulation, to tell it apart from re-injection | `image/taa` | helps |
| The sun's light and its direction in the frame constants | `light/lights` | helps |

## `indirect/gi-limits` — Global illumination III: moving objects, limits and what comes next

**Covers.** A concept page. It opens with three honest pictures: the row of small dark notches under the Cornell box's
sphere, a wall thinner than two voxels that the voxels view shows two-sided, and the edge of the field around the
camera outdoors in the yard. The naive answer, "GI is free bounce light everywhere", breaks on each of them. The idea:
what a voxel copy of the static world and a probe field around the camera can hold, and what they cannot. Only static
geometry enters (movers wait 30 frames, skinned meshes never enter); only the sun and glowing surfaces light the voxels;
the field changes diffuse light only, and specular stays today's; it resolves no more than its probes (0.5 m apart at
High, 1 m at Low); it reaches only a box around the camera (High full within 7.5 m across and 5.5 m up and down, Low
within 7 m and 2.8 m, faded to today's light over 2 m more); an ambient cube is exact only for normals along the axes;
textures count by their means. The limits of the guide's "What it cannot do" follow, each with its cause in one
sentence: a surface that sees none of its eight probes gets no field light, so it is dark, never the sky, and darker
than without GI, outdoors too (gaps, ledges, wall feet); thin props become blobs of whole voxels; a model colored from
one palette texture takes the palette's mean everywhere; double-sided materials' voxels have no facing; glowing values
above 65,408 nits clamp; an editor top view far above a scene shows only the coarse levels; submeshes past a mesh's
256th are left out (logged once); Low bounces once; and the field does not reach baked probe captures (a bake renders
at Medium's row, where GI is Off: `indirect/probes`).

The approaches engines use for what Strata lacks, each with its cost: moving objects in a dynamic occupancy or traced by
rays (DDGI, Lumen); local lights injected into the voxels; skinned meshes voxelized as they pose; specular GI; hardware
ray queries. Strata's choice and its reason: GI is experimental, deterministic and free of history, and global
illumination that is off is invisible bit for bit, while what it still costs is measured and stated. This page is that
decision's home for GI, in a `:::why` aside: when the scene does not ask, when the row is Off, and while the field is
pending, the frame keeps the indirect light's old expression bit for bit (the join's `x * 1 + 0`, the dummy views); off,
GI still spends 0.010 to 0.014 ms more in `GPU.Opaque` (Medium with TAA at 3840 x 2160, measured at the tag), because
the forward shader's gather is compiled in although it does not run; and one exception runs GI where nothing asks for
it: a GI debug view, which at Off shows High's layout. What Strata does not do: GI from local lights, from moving
objects and from skinned objects; specular light from GI (the field changes only the diffuse indirect light); and the
rest of the spec's list "below the cut" (the open share in specular occlusion, an Ultra layout, textured albedo per
voxel, hardware ray queries), with nested probe-field levels and denser probes near surfaces, each quoted from the
documents and never dated (probe relocation, the spec's item 7, is at the pin and taught on `indirect/gi-cascades`); it
links `appendix/not-in-strata`. The exercises predict which limit decides three scenes and break, in a patch, the rule
that movers wait 30 frames. Common mistakes: walls thinner than two voxels, a moving door expected to change the bounce
at once, judging GI before it has settled, and reading the GI stage's time as stable when the release notes record it
varying between runs. The reader can say before trying it whether GI will help a scene.

**Leaves out.**

- How the voxels are made → `indirect/gi-voxels`
- How the field is traced, sampled and joined → `indirect/gi-cascades`
- "A feature that is off is invisible bit for bit" as a rule of the whole renderer → `gpu/frame-tour`
- Trying GI in a game and avoiding its pitfalls → `make/gi`
- Local lights and their records → `light/lights`
- The general techniques of dynamic GI that Strata lacks → `appendix/not-in-strata`

**Fit.** `fits`: about 3,650 words against M (3,000). The three honest pictures, what the voxels and the field can hold,
the guide's limits one by one and the approaches engines use for what Strata lacks take the most words. Phase B must
look again at: every absence at the new pin (`v0.8.0`, then `v0.8.1`), since the spec's list may shrink; the guide's
paragraph "What it cannot do" (`Docs/DeveloperGuide.md:5259-5296` at the pin) and the numbers it gives, with the limits
of `new:31`; the 0.8.0 release notes' "Known issues"; the cost of GI when off, measured again at the tag; the entry of
book.md's table "Checked when the W8 page is written" that names this page (`new:15`: GI from local lights and from
moving or skinned objects, specular light from GI, the open share in specular occlusion, an Ultra level, textured albedo
per voxel, hardware ray queries, nested probe-field levels, denser probes near surfaces); the page's movable claims.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-indirect:153` | feature | home | What the pin has (stages 1 to 4, the batches "smooth light between probes" and "light at contacts") and what it has not (the spec's list below the cut, nested field levels, denser probes near surfaces, the octahedral and SH fields tried and not landed) |
| `render-indirect:112` | feature | home | The open share in specular occlusion, planned and not landed (spec D18.4) |
| `render-indirect:510` | rule | home | A frame without GI (not asked, the row Off, pending) keeps the old expression bit for bit, the join in `x * 1 + 0` form; what GI still costs when off is measured and stated (0.010 to 0.014 ms more in `GPU.Opaque`, the gather compiled in: `Docs/Plans/Wave8/ReleaseNotes.md:383-386`); a GI debug view runs GI where nothing asks for it, at Off with High's layout (`Strata/src/Strata/Renderer/SceneRenderer.cpp:3069-3074`): the design decision's home for GI, in a `:::why` aside (`AGENTS.md:405-406`; book.md's design decisions) |
| `render-indirect:515` | rule | home | Movers stay out of the voxels for 30 frames and skinned meshes never enter: no voxel work per frame for moving things, no popping of light |
| `render-indirect:459` | figure | home | The artefacts: dark notches under the Cornell sphere (`lookdev.cornell`, whose scene asks for GI), a thin wall two-sided in the voxels view (no shot at the pin is named for it: a recipe), the field's edge in the yard (`lookdev.yard.lit.gi`) (`Tools/LookDev/Shots.json:148`, `:150`; `Tools/LookDev/LookDevScene.json:259`) |
| `render-indirect:704` | open | home | The GI stage's time varies between runs of one build (4.4 against 6.5 ms) for a cause the release notes leave open; stated as a known issue, quoted |
| `new:15` | not-done | home | No global illumination from local lights, from moving objects or from skinned objects; no specular light from global illumination (the field changes only the diffuse indirect light); no open share in specular occlusion, no Ultra level, no textured albedo per voxel, no hardware ray queries for global illumination, no nested probe-field levels and no denser probes near surfaces (book.md's row in "Checked when the W8 page is written"; probe relocation, the spec's item 7, is at the pin). Evidence: `Docs/Plans/Wave8/specs/radiance-cascades-world.md:896-917` (D18 "Below the cut", items 1 to 6 and 8; item 7 is at the pin: `Docs/DeveloperGuide.md:5090`); `Docs/DeveloperGuide.md:4960-4961` (nested probe-field levels and local lights follow), `:5164` (specular is untouched), `:5271` (denser probes near surfaces are the next step); movers excluded for 30 frames (`Strata/src/Strata/Renderer/SceneRenderData.h:686`) |
| `new:31` | feature | home | The limits of the guide's "What it cannot do", each with its cause in one sentence: a surface that sees none of its eight probes gets no field light (dark, never the sky, darker than without GI, outdoors too: gaps, ledges, wall feet); thin props become blobs of whole voxels; a palette texture gives the whole model one mean color; double-sided materials' voxels have no facing; glowing values above 65,408 nits clamp; an editor top view far above a scene shows only the coarse levels; submeshes past a mesh's 256th are left out (logged once); Low bounces once; a baked probe capture holds no GI (the bake renders at Medium's row). Evidence: `Docs/DeveloperGuide.md:5272-5277`, `:5287-5289`, `:4968`; `Docs/Manual/Lighting.md:346-352`; `Strata/src/Strata/Renderer/SceneRendererGlobalIllumination.cpp:605-611`; `Strata/src/Strata/Renderer/SceneRenderData.h:799`; `StrataTests/src/Renderer/GlobalIlluminationLayoutTests.cpp:525` |
| `new:32` | hands-on | home | The page's exercises (R32, D27): **Basic.** predict which limit of the page decides each of three scenes (a cave lit only by torches, a sunlit hall whose door swings, a grove of thin poles); **Medium.** modify: a patch against the pin that lets a moved mesh back into the voxels in the frame after it stops (`c_GIMovingFrames` 1); predict whether the CPU test "A moved proxy queues its old and new bounds", which counts its frames by the constant, still passes and what a door that swings back and forth would then cost the voxelizer, and run it. Evidence: `StrataTests/src/Renderer/VoxelClipmapTests.cpp:303-352` (suite `Renderer.VoxelClipmap`, `:253`); `Strata/src/Strata/Renderer/SceneRenderData.h:686`; `Strata/src/Strata/Renderer/VoxelClipmap.cpp:398-458`; `Docs/Plans/Wave8/specs/radiance-cascades-world.md:896-917` |
| `render-indirect:517` | rule | use | Walls thinner than two voxels go two-sided; taught on `indirect/gi-voxels` |
| `render-indirect:166` | feature | use | What enters the voxels, as the source of the limits on movers and textures |
| `render-indirect:178` | feature | use | The join, specular untouched |
| `render-indirect:367` | code | use | The join's `x * 1 + 0` form, shown in one line |
| `render-indirect:519` | rule | use | Waiting for GI to settle, as a common mistake's fix |
| `render-indirect:329` | concept | link | The renderer's rule that an off feature changes no bit, on `gpu/frame-tour` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The GI pipeline from the voxels to the join | `indirect/gi-cascades` | must |
| The voxel classes and two-sided walls | `indirect/gi-voxels` | must |
| The renderer's rule that an off feature changes no bit | `gpu/frame-tour` | must |
| Point and spot lights and their records | `light/lights` | helps |
| Skinned meshes in the renderer | `draw/skinned` | helps |
| Temporal accumulation, as other engines' GI uses it | `image/taa` | helps |
| What a probe bake renders with (`ForBake`, Medium's row) | `indirect/probes` | helps |

## Passed on

| Item | Type | To | Why |
| --- | --- | --- | --- |
| `render-indirect:53` | feature | `light/sky` | The sky light component and its fields belong with the sky's sources (book.md); `render-direct:151` is the same component; `indirect/ibl` uses it |
| `render-indirect:59` | feature | `light/energy` | The BRDF table is `light/energy`'s (outline: `BRDFLut.comp.slang`); `render-direct:58` is the same table |
| `render-indirect:62` | feature | `light/lights` | Preview lighting is in book.md's row of lights; `render-direct:84` is the same feature |
| `render-indirect:63-64` | feature | `light/sky` | Extract Sun, Remove Sun and the sky presets are the sky's (book.md); `render-direct:159-160` |
| `render-indirect:71` | feature | `light/brdf` | GGX, Smith and Schlick in code (`render-direct:56`) |
| `render-indirect:72` | feature | `light/energy` | Multiple-scattering energy compensation (`render-direct:59`) |
| `render-indirect:73` | feature | `light/brdf` | Specular anti-aliasing is in `light/brdf`'s row (`render-direct:60`) |
| `render-indirect:74` | feature | `light/material-data` | F0 from the IOR is computed in the GPU record (`MaterialGPU::GetDielectricF0`, render-direct code 3); the concept is `light/reflectance`'s |
| `render-indirect:75` | feature | `light/area-lights` | Sized highlights are that page's (outline); `render-direct:61` |
| `render-indirect:189-193` | feature | `light/measuring-light` | The lighting views, value views, statistics, history under views and the editor's access: the outline gives render-indirect 1.9 to that page; the AO view is read on `indirect/ao` and the GI views on `indirect/gi-cascades` |
| `render-indirect:194-195` | feature | `light/energy` | The white furnace as a test and as a look-dev shot (outline) |
| `render-indirect:196` | feature | `engineering/look-dev` | The list of the area's look-dev shots belongs with the harness; the part's pages use the shots as figure sources |
| `render-indirect:197` | feature | `engineering/test-kinds` | The flicker meter is book.md's "flicker metrics" (`FlickerMetrics.h`); `indirect/ssr` uses it |
| `render-indirect:237` | concept | `light/reflectance` | Radiance, irradiance, solid angle and cosine weighting: the outline gives render-indirect concepts 2 and 3 to that page |
| `render-indirect:241` | concept | `light/reflectance` | The microfacet recap (GGX, Smith, Fresnel, F0, roughness against alpha), as above |
| `render-indirect:259` | concept | `light/energy` | Energy conservation and the white furnace (outline: render-indirect concept 7) |
| `render-indirect:265` | concept | `light/brdf` | Specular aliasing and geometric specular anti-aliasing, with the derivative rule |
| `render-indirect:326` | concept | `light/measuring-light` | Measuring light by numbers (outline) |
| `render-indirect:329` | concept | `gpu/frame-tour` | "Bit for bit when off" as a rule of the whole renderer (book.md, design decisions); the part's pages name it |
| `render-indirect:338` | code | `light/energy` | The BRDF table's shader (outline: render-indirect code 1); the same lines as render-direct code 9 |
| `render-indirect:342-343` | code | `light/energy` | `GetSpecularEnergy` and the furnace test (outline: render-indirect code 5 and 6) |
| `render-indirect:384` | figure | `light/energy` | Single-scattering GGX's energy loss and the compensation (outline: render-indirect figure 6) |
| `render-indirect:417` | figure | `light/measuring-light` | The lighting view statistics pipeline |
| `render-indirect:427` | figure | `light/energy` | The white furnace before and after energy compensation; `render-direct:528` is the same picture |
| `render-indirect:429` | figure | `light/brdf` | Specular anti-aliasing on and off |
| `render-indirect:432` | figure | `light/reflectance` | Dielectric spheres at IOR 1.33, 1.5 and 2.42 (`lookdev.ior`, `Tools/LookDev/Shots.json:86`) show F0 from the IOR |
| `render-indirect:454` | figure | `light/area-lights` | The sun's sized highlight, Clear against Overcast |
| `render-indirect:461` | figure | `light/measuring-light` | The lighting debug views on a sample; the look-dev shots are `lookdev.view.lighting`, `lookdev.view.indirect`, `lookdev.view.luminance` and `lookdev.view.albedo` (`Tools/LookDev/Shots.json:64-68`; R34, D42) |
| `render-indirect:467` | rule | `light/energy` | Light keeps its energy: check shading changes with the furnace |
| `render-indirect:470` | rule | `light/energy` | Diffuse gets what specular leaves (outline: render-indirect rule 2) |
| `render-indirect:472` | rule | `light/brdf` | The derivative rule (`render-direct:588`) |
| `render-indirect:475` | rule | `light/material-data` | IOR 1.5 stays the literal 0.04 in `MaterialData.cpp` (`render-direct:586`) |
| `render-indirect:477` | rule | `light/area-lights` | A light's size widens only its highlight's D (`render-direct:593`) |
| `render-indirect:531-532` | hands-on | `make/lighting` | Lighting with each sky source and the four presets: choosing the source and its preset is `make/lighting`'s (outline, row of `make/reflections`) |
| `render-indirect:533-537` | hands-on | `make/reflections` | AO, a probe and its box, bakes as bounces, times of day and the wet floor are that page's (outline) |
| `render-indirect:538` | hands-on | `make/gi` | A closed room with a window under GI, its views and a wall too thin |
| `render-indirect:539` | hands-on | `make/materials` | The albedo audit with the debug view (outline, row of `make/materials`) |
| `render-indirect:540` | hands-on | `make/commands` | The agent route is all commands; on track G only pages from `make/commands` on may hold steps that only a command can do (style.md §10) |
| `render-indirect:546` | hands-on | `light/energy` | A CPU white furnace and the compensation against `BRDFLut.comp` |
| `render-indirect:548` | hands-on | `light/measuring-light` | A new lighting debug view from end to end |
| `render-indirect:566` | term | `nowhere` | Repeats `render-direct:742` (environment map) |
| `render-indirect:569` | term | `nowhere` | Repeats `assets:702` (mip, mip level, mip chain) |
| `render-indirect:570-571` | term | `light/units-exposure` | Irradiance and radiance as radiometric quantities (book.md: light units); no other inventory has them as terms |
| `render-indirect:572` | term | `basics/math-sphere` | Solid angle (book.md) |
| `render-indirect:573` | term | `nowhere` | Repeats `render-direct:695`, `render-direct:697` and `render-direct:699` (lux, nit, EV100) |
| `render-indirect:574` | term | `nowhere` | Repeats `render-direct:681` (Lambert) |
| `render-indirect:575` | term | `nowhere` | Repeats `render-direct:671` (albedo) |
| `render-indirect:576` | term | `nowhere` | Repeats `render-direct:679` (F0) and `render-direct:680` (IOR) |
| `render-indirect:577` | term | `nowhere` | Repeats `render-direct:678` (Fresnel, Schlick) |
| `render-indirect:578` | term | `light/reflectance` | GGX and alpha: "alpha" has no entry elsewhere, and GGX repeats `render-direct:676`; perceptual roughness is linked to its one entry on `light/materials` (`render-direct:673`; the merge "Perceptual roughness" of `proposals/duplicates.md`) |
| `render-indirect:579` | term | `nowhere` | Repeats `render-direct:677` (Smith visibility) |
| `render-indirect:581` | term | `nowhere` | Repeats `render-direct:683` (BRDF table) |
| `render-indirect:584` | term | `basics/math-probability` | Hammersley is one of the sampling patterns that page is the home of |
| `render-indirect:585` | term | `basics/math-sphere` | The mathematics of spherical harmonics (book.md); `indirect/probes` uses SH-9 |
| `render-indirect:587` | term | `light/energy` | Energy compensation and multiple scattering; "multiple scattering" needs a qualified entry, because `render-direct:749` uses it for the atmosphere |
| `render-indirect:588` | term | `nowhere` | Repeats `render-direct:686` (white furnace test) |
| `render-indirect:589` | term | `nowhere` | Repeats `render-direct:687` and `render-direct:688` (specular aliasing, specular anti-aliasing) |
| `render-indirect:594` | term | `nowhere` | Repeats `render-direct:737` (edge-aware, bilateral blur) |
| `render-indirect:595` | term | `nowhere` | Repeats `render-scene:605` (ordered dither, Bayer matrix) |
| `render-indirect:606` | term | `nowhere` | Repeats `render-direct:702` and `render-image:653` (pre-exposure) |
| `render-indirect:609` | term | `gpu/coordinates` | Depth buffer: Strata's depth conventions (book.md); `gpu/coordinates` keeps it for the depth buffer and links reversed Z, whose home is `basics/math-projection` (the merge "Reversed Z and NDC" of `proposals/duplicates.md`) |
| `render-indirect:611` | term | `basics/math-sphere` | Octahedral encoding (book.md: octahedral maps) |
| `render-indirect:617` | term | `light/clearcoat-transmission` | Premultiplied alpha (book.md) |
| `render-indirect:618` | term | `basics/math-probability` | Interleaved gradient noise is one of that page's patterns (book.md) |
| `render-indirect:619` | term | `nowhere` | Repeats `render-image:700` (history) |
| `render-indirect:620` | term | `nowhere` | Repeats `render-image:702` (motion vector, velocity target) |
| `render-indirect:648` | term | `nowhere` | Repeats `render-image:736` (look-dev) |
| `render-indirect:649` | term | `engineering/test-kinds` | The flicker meter (book.md: flicker metrics) |
| `render-indirect:650` | term | `nowhere` | Repeats `render-direct:755` (sun-to-sky ratio) |
| `render-indirect:687` | open | `nowhere` | A note about files the survey did not read in full; the Fit lines of `indirect/gi-voxels` and `indirect/gi-cascades` carry it to phase B |
| `render-indirect:695` | open | `nowhere` | A note about specs the survey did not read; the Fit lines of the GI pages carry it to phase B |
| `render-indirect:698` | open | `nowhere` | A note on the survey's view of GI batches still landing; the W8 marks and the Fit lines of the GI pages carry it |
| `render-indirect:705` | open | `nowhere` | A note on producing "before" pictures, which `pipelines.md` §5.5 settles (the look-dev baseline sets) |
| `render-indirect:709` | open | `nowhere` | A note about the atmosphere's files the survey did not read; the atmosphere is `render-direct`'s (1.8) and `light/atmosphere`'s |

## Not taken

none

## Questions for the planner

none
