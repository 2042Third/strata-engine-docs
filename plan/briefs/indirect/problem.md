# Brief: `indirect/problem`

| Field | Value |
| --- | --- |
| Title | The indirect-light problem |
| Kind | C |
| Size | M |
| Tracks | E |
| Needs | `light/brdf`, `light/sky` |
| From | render-indirect ch. 1; the rendering equation (extending `light/reflectance`'s reflection equation), what each technique approximates, the families engines use; a Monte Carlo path tracer sketch of the Cornell box as the reference image; home of "GI traces world data, never the screen" |
| Unit | `plan/allocation/indirect.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `global-illumination` | Global illumination | GI |
| `indirect-light` | Indirect light | - |
| `radiosity` | Radiosity | - |
