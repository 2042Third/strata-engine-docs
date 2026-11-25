# Outline 3: Light and materials, The image, Indirect light, Physics, Animation, Audio, Input

Columns as in [outline-1.md](outline-1.md).

**Figures of parts 8 to 10.** Every page of these parts takes its figures from its inventory's "Screenshots" and "Diagrams"
lists (render-direct §4, render-indirect §4, render-image §4). A page that teaches a visible effect has figures rendered
by the engine: the effect off and on where it has a switch, its debug view where one exists, and a sweep of its main
setting. A page or feature without a switch gets a diagram or a lab instead. The part brief lists which page gets
which figures. `image/pre-exposure` is exempt: it changes no image by design and uses render-image's diagrams 3 and 4.
`indirect/ao`, `indirect/probes` and `indirect/gi-cascades` compare their figures with the reference image of the path
tracer sketch in `indirect/problem`.

## Part 8 — Light and materials (`light`)

Tracks: E

Needs of the part: `basics/numbers`, `basics/math-vectors`, `basics/math-bases`, `basics/math-projection`, `basics/color`, `basics/signals`, `basics/math-probability`, `basics/math-sphere`, `world/interpolation`, `gpu/compute`, `gpu/coordinates`, `gpu/binding`, `gpu/frame-tour`, `gpu/readback-timing`, `gpu/debug-drawing`, `assets/textures`, `assets/texture-cooking`, `assets/loading`, `draw/render-scene`, `draw/bounds-culling`, `draw/batching`, `draw/gpu-driven`, `draw/occlusion`

| id | Title | Kind | Size | Tracks | Needs | From |
| --- | --- | --- | --- | --- | --- | --- |
| `light/units-exposure` | Light by the numbers: radiometric and photometric units | C | L | E | `gpu/frame-tour`, `basics/numbers`, `basics/color`, `basics/math-sphere` | render-direct ch. 1; 1.5 (radiometry; lumen, candela, lux and nit conversions; the spot rule; the sun-to-sky ratio; the reference table; one paragraph on why the HDR target needs a pre-exposure); one sentence that 0.8.0's rectangle lights have units of their own, which `light/area-lights` gives (a movable claim, read again at the pin move to v0.8.0); home of "light in real units" |
| `light/materials` | Strata's material model | C | L | E | `assets/textures`, `basics/math-bases`, `light/units-exposure` | render-direct ch. 2 (the model, the maps, alpha modes, emission in nits, plausible albedos, IOR as a field, normal maps and tangent space as a concept) |
| `light/reflectance` | How surfaces reflect light: the reflection equation and microfacets | C | L | E | `light/materials`, `basics/math-vectors`, `basics/math-probability`, `basics/math-sphere` | new; the theory the BRDF code needs first: render-direct concepts 6-7, render-indirect concepts 2-3 (radiance and irradiance in use, the reflection equation, Lambert, microfacets with D, G and F derived, Fresnel and F0 from IOR) |
| `light/material-data` | From a material file to the shader: the material record and its textures | I | L | E | `light/materials`, `gpu/binding`, `assets/loading` | new; the GPU half of render-direct ch. 2, which a concept page cannot hold: 1.1 (GPU rows), code #2-#5, figure 5, rules 7-9 and 14 (`MaterialGPU::Build`, the 144-byte `MaterialData`, the texture table, the XY normal decode) |
| `light/brdf` | The forward shader and the BRDF in code | I | L | E | `light/reflectance`, `light/material-data`, `basics/signals` | render-direct ch. 3; 1.2 (GGX, Smith, Schlick, Lambert, minimum roughness, the six variants, the EQUAL test, `[earlydepthstencil]`, the derivative rule, specular anti-aliasing, `SanitizeHDR`), code #6, #7, #10, #19, figure 20, rules 6, 10, 29 |
| `light/energy` | Keeping the energy: directional albedo, the BRDF table and the white furnace | I | M | E | `light/brdf`, `gpu/compute` | render-indirect ch. 3 (was `indirect/energy`); render-direct concept 9, code #8, #9 (`BRDFLut.comp.slang`); render-indirect concept 7, code #1, #5, #6, rule 2; the furnace tests of `GPUSceneLightingTests.cpp` and the shot `lookdev.furnace`; render-direct figure 4, render-indirect figure 6 |
| `light/measuring-light` | Measuring light: the debug views and their statistics | I | M | E | `light/brdf`, `gpu/readback-timing`, `gpu/debug-drawing` | render-direct ch. 14, 1.10 and render-indirect ch. 12, 1.9 (was `indirect/measuring-light`, a how-to): the lighting, luminance, albedo and indirect views, their statistics, the sun-to-sky ratio; the shadows view is `light/sun-shadows-1`'s, the AO view `indirect/ao`'s, the GI views `indirect/gi-cascades`' |
| `light/lights` | Lights: the sun, points and spots | I | L | E | `light/brdf`, `draw/render-scene`, `world/interpolation` | render-direct ch. 4; 1.3 (the components, falloff, the cone, one sun, what a light record holds, `LightData`, spot bounds, drawn transforms, preview lighting) · W8r (light components and records) |
| `light/many-lights` | Many lights: culling and clustered forward shading | I | L | E | `light/lights`, `gpu/compute`, `draw/bounds-culling`, `draw/gpu-driven` | render-direct ch. 5; 1.4 (the CPU and GPU paths, clusters, overflow bisection, the forward loop, stats); tiled against clustered shading (forward against deferred is `gpu/frame-tour`'s) · W8r (the forward light loop) |
| `light/area-lights` | Lights with size: sized highlights and area lights | I | L | E | `light/many-lights`, `light/energy` | render-direct concept 12, 1.13; sized highlights (`GetSourceLobeAlpha2`, `GetLobeAlpha`, `RenderData::GetSunLobeAlpha2`); new: 0.8.0's rectangle lights (LTC shading, light surfaces, editor and script support; disk lights if stage 5 lands), the units of their intensity and how they convert to the quantities of `light/units-exposure`, and the clear coat under them; their soft shadows are `light/local-shadows`' · W8 |
| `light/shadow-basics` | Shadow mapping from first principles | C | L | E | `light/lights`, `gpu/coordinates`, `basics/math-projection` | render-direct ch. 6 (rendering and sampling a shadow map, reversed-Z comparisons, acne and the four biases, pancaking, alpha-masked casters) |
| `light/sun-shadows-1` | Sun shadows I: stable cascades | I | XL | E | `light/shadow-basics`, `draw/gpu-driven`, `draw/occlusion` | render-direct ch. 7; 1.6 (the stable layout, the fifth cascade, the GPU depth fit, containment, blend bands, stats); + sun caster selection (`FindShadowCasters`, `CanShadowView`), the cascade cache and its versions, cascade occlusion (`draw/occlusion` links here for it); + the shadows view |
| `light/sun-shadows-2` | Sun shadows II: the soft shadow of a real sun | I | XL | E | `light/sun-shadows-1`, `basics/signals` | render-direct ch. 8; 1.6 (PCSS at physical width, the depth-range classification, the tent and the Vogel disk with fixed blue noise, the screen-space mask and stair blur, contact shadows, transparent receivers, why nothing depends on the frame) |
| `light/local-shadows` | Shadows of point and spot lights | I | L | E | `light/sun-shadows-1`, `light/many-lights`, `light/area-lights` | render-direct ch. 9; 1.7 (the atlas, quadtree tiles, cube faces, guard bands, view caches, the redraw budget, fades); local shadow casters and culling (`FindLocalShadowCasters`); + the soft shadows of 0.8.0's rectangle lights · W8 |
| `light/sky` | The sky as a light: sources, sun extraction and presets | I | M | E | `light/lights`, `assets/texture-cooking` | render-direct ch. 10; 1.8 (source rows: the three sky sources, the procedural sky, environment maps, Extract and Remove Sun, presets with `groundIlluminance`, the sun-to-sky ratio), concept 19 |
| `light/atmosphere` | Earth's atmosphere and aerial perspective | I | L | E | `light/sky`, `gpu/compute` | new; split from `light/sky`, which held two chapters: render-direct 1.8 (atmosphere rows), 1.9 (aerial perspective), concept 20; home of participating media (extinction, transmittance, phase functions) |
| `light/fog` | Height fog | I | M | E | `light/atmosphere` | render-direct ch. 11; 1.9 (the closed-form integral, its lighting, the sky at infinity, `c_MinHeightFalloff`, what a fog without volume cannot do) |
| `light/clearcoat-transmission` | Transparency, clear coat and glass | I | L | E | `light/energy`, `draw/batching` | render-direct ch. 12; 1.1 (clear coat, glass, the scene-color copy); home of transparency, blending and premultiplied alpha, and of the scene-color copies; the coat under rectangle lights is `light/area-lights`' |

## Part 9 — The image (`image`)

Tracks: E

Needs of the part: `basics/numbers`, `basics/math-projection`, `basics/signals`, `core/first-change`, `world/projects-settings`, `gpu/compute`, `gpu/coordinates`, `gpu/first-triangle`, `gpu/frame-tour`, `gpu/readback-timing`, `assets/importing`, `draw/motion-vectors`, `light/brdf`, `light/measuring-light`, `light/sun-shadows-2`

| id | Title | Kind | Size | Tracks | Needs | From |
| --- | --- | --- | --- | --- | --- | --- |
| `image/why-post` | Why images need post-processing, and Strata's post chain | C | M | E | `gpu/frame-tour`, `light/brdf` | render-image ch. 1; 1.1 whole (the HDR target, the chain's order, `PostSource`, the fullscreen pass, the CPU twins in `PostProcessMath`); code #1, and a few lines of code #2, which `image/tutorial-post-effect` walks whole; code #3 (`SanitizeHDR`) is `light/brdf`'s |
| `image/exposure` | Exposure: camera, eye and meter | I | L | E | `gpu/compute`, `gpu/coordinates`, `light/measuring-light`, `image/why-post` | render-image ch. 2; 1.2 (the camera exposure and EV100, histogram metering, percentiles, center weighting, adaptation, the key, the debug views) |
| `image/pre-exposure` | Pre-exposure | I | M | E | `image/exposure`, `basics/numbers`, `gpu/readback-timing` | render-image ch. 3; 1.2 (power-of-two scaling, asynchronous readbacks, epochs, settling, the TAA rescale); render-direct code #36 (`ChoosePreExposure`); the mechanism of "light in real units" |
| `image/tone-mapping` | Tone mapping and the Filmic curve | I | L | E | `image/exposure` | render-image ch. 4; 1.3 (tone curves, hue skew, the five classic operators, Filmic's form and its fit, Toe and Shoulder, contrast and saturation) |
| `image/grading` | White balance, grading and lookup tables | I | L | E | `image/tone-mapping`, `assets/importing` | render-image ch. 5; 1.4 (chromaticity, the white locus, CAT02, ASC-CDL, `.cube` lookup tables and the `ColorLookup` asset) |
| `image/encoding` | Encoding, dithering and grain | I | L | E | `image/grading`, `basics/signals` | render-image ch. 6; 1.5 (sRGB encoding, banding, TPDF dither, film grain, the 10-bit intermediate); a forward sentence on FXAA and grain |
| `image/lens-effects` | Lens effects: bloom, vignette, flares and fringes | I | L | E | `image/tone-mapping`, `basics/signals` | render-image ch. 7; 1.6 (the bloom pyramid, the Karis average, radius independence, the cos^4 vignette, ghosts, halo and starburst, chromatic aberration) |
| `image/spatial-aa` | Anti-aliasing in one frame: FXAA and morphological AA | I | L | E | `image/encoding` | render-image ch. 8; 1.8 (FXAA's algorithm, Strata's morphological AA and its area table) |
| `image/taa` | Temporal anti-aliasing | I | XL | E | `image/spatial-aa`, `draw/motion-vectors`, `basics/math-projection` | render-image ch. 9; 1.8 (jitter on the frame's camera copy, history, reprojection, Catmull-Rom, clamping and clipping, the reactive mask, sharpening, settling); home of "nothing needs history to look right" |
| `image/motion-blur` | Motion blur | I | M | E | `image/taa` | render-image ch. 10 (first half); 1.7 (tile max, neighbor max, the gather, the CPU profile model, shutter-angle and cut rules), concept 16, diagram 19; split from `image/motion-blur-dof` |
| `image/depth-of-field` | Depth of field | I | L | E | `image/taa`, `gpu/coordinates` | render-image ch. 10 (second half); 1.7 (the five shaders, thin-lens CoC, `CameraLens::FromEntity`, the camera's fields), concept 17, diagram 20; split from `image/motion-blur-dof` |
| `image/quality-settings` | Quality settings and players' graphics options | I | L | E | `image/taa`, `light/sun-shadows-2`, `world/projects-settings` | render-image ch. 11; 1.9 (cost against look, rows and presets, traits, Custom, the section, `IGameGraphics`, the options file, the script SDK, why no render scale); home of "never below native resolution" · W8r (the quality rows and their presets) |
| `image/tutorial-post-effect` | Tutorial: adding a post effect | T | L | E | `image/taa`, `gpu/first-triangle`, `core/first-change` | render-image ch. 13 (push constants, `PostSource`, the neutral helper, the GPU stage, GPU tests, a feature-test value) |

## Part 10 — Indirect light (`indirect`)

Tracks: E

Needs of the part: `basics/math-geometry`, `basics/signals`, `basics/math-sphere`, `gpu/compute`, `gpu/geometry-pool`, `assets/residency`, `draw/render-scene`, `draw/mip-streaming`, `light/brdf`, `light/energy`, `light/measuring-light`, `light/sky`, `light/atmosphere`, `light/clearcoat-transmission`, `image/pre-exposure`, `image/taa`

| id | Title | Kind | Size | Tracks | Needs | From |
| --- | --- | --- | --- | --- | --- | --- |
| `indirect/problem` | The indirect-light problem | C | M | E | `light/brdf`, `light/sky` | render-indirect ch. 1; the rendering equation (extending `light/reflectance`'s reflection equation), what each technique approximates, the families engines use; a Monte Carlo path tracer sketch of the Cornell box as the reference image; home of "GI traces world data, never the screen" |
| `indirect/ibl` | Image-based lighting and the split sum | I | L | E | `light/energy`, `light/sky`, `basics/math-sphere`, `gpu/compute` | render-indirect ch. 2; 1.1 (the sky's sources as cube maps, the filter chain, filtered importance sampling, the budget, shared environments, constant ambient, the atmosphere cube); the split sum's prefiltered half, reusing `light/energy`'s table; home of the horizon fade |
| `indirect/seam` | Where indirect light meets the surface: inputs, gathers and fallbacks | I | M | E | `indirect/ibl` | new; the indirect light's join in the forward shader had no page: render-indirect 1.3 (`IndirectInputs`, the four forms, the gathers, compose, the coat's image light), code #8-#10, #30, concept 15 (the fallback stack) |
| `indirect/ao` | Ambient occlusion without history | I | L | E | `indirect/seam`, `gpu/compute`, `basics/signals` | render-indirect ch. 4; 1.4, 1.5 (GTAO, the fixed pattern and denoiser, the radius clamp, thin occluders, the multi-bounce fit, specular occlusion); the AO view |
| `indirect/probes` | Reflection probes | I | XL | E | `indirect/seam`, `image/pre-exposure`, `assets/residency`, `basics/math-geometry`, `draw/mip-streaming` | render-indirect ch. 5; 1.6 (box projection, blending, the probe cache and conversions, the bake and its pre-exposure, times of day) |
| `indirect/ssr` | Screen-space reflections | I | XL | E | `indirect/probes`, `image/taa`, `light/clearcoat-transmission`, `indirect/ao` | render-indirect ch. 7; 1.7 (screen-space rays, the Checkerboard and Spatial traces, validation, the resolve, fallbacks and limits; Checkerboard's use of the TAA history as the exception to "nothing needs history") |
| `indirect/gi-voxels` | Global illumination I: a voxel copy of the world | I | L | E | `indirect/seam`, `gpu/compute`, `gpu/geometry-pool`, `draw/render-scene`, `indirect/problem` | render-indirect ch. 9; 1.8 (the voxel clipmap, voxelizing the geometry pool's static submeshes, fill, finalize, budgets and anchors) · W8 |
| `indirect/gi-cascades` | Global illumination II: radiance cascades and the irradiance field | I | XL | E | `indirect/gi-voxels`, `indirect/ao`, `light/measuring-light`, `basics/math-sphere`, `light/atmosphere` | render-indirect ch. 10; 1.8 (injection, the cascades, merge, field reduce, the forward gather, multi-bounce and settling, what is experimental); + the GI debug views and their statistics · W8 |
| `indirect/gi-limits` | Global illumination III: moving objects, limits and what comes next | C | M | E | `indirect/gi-cascades` | new; what Strata's GI does not do (local lights, moving and skinned objects: render-indirect 1.8) and how other engines do it; home of "a feature that is off is invisible bit for bit" for GI · W8 |

## Part 11 — Physics (`physics`)

Tracks: E

Needs of the part: `basics/trees-graphs`, `basics/math-vectors`, `basics/math-rotations`, `basics/math-geometry`, `basics/math-change`, `core/time`, `core/jobs`, `core/profiling`, `world/scene-graph`, `world/systems`, `world/interpolation`, `world/sub-scenes`, `world/projects-settings`, `assets/loading`

| id | Title | Kind | Size | Tracks | Needs | From |
| --- | --- | --- | --- | --- | --- | --- |
| `physics/why` | Why games need physics | C | S | E | - | physics ch. 1 (the problems, the engines on the market, why box3d, what Strata does not do) |
| `physics/bodies-colliders` | Rigid bodies and colliders | C | M | E | `world/scene-graph`, `basics/math-vectors` | physics ch. 3 (the concepts; its hands-on is `make/physics`'); 1.1, 1.2; concepts 4-6 |
| `physics/collision-detection` | Collision detection: shapes, broad phase and narrow phase | C | L | E | `physics/bodies-colliders`, `basics/math-geometry`, `basics/trees-graphs` | physics ch. 4 (first half), concept 8: AABB trees, pair finding, GJK, contact manifolds (Catto's BVH and GJK talks, Ericson); split from `physics/how-simulation-works` |
| `physics/dynamics` | Rigid body dynamics: integration, contacts, solvers, sleep and continuous collision | C | L | E | `physics/collision-detection`, `core/time`, `basics/math-change`, `basics/math-rotations` | physics ch. 4 (second half), concepts 3, 9-12: integration, mass and inertia, contacts as soft constraints, sub-stepping, friction, restitution, continuous collision, islands and sleep, box3d's choices; a toy solver first; split from `physics/how-simulation-works` |
| `physics/building-bodies` | From entities to bodies: records, shapes, mesh colliders | I | L | E | `physics/dynamics`, `world/systems`, `core/jobs`, `assets/loading` | physics ch. 5 (first half); 1.2-1.4 (records and slots, `AddColliderParts`, baked scale, shared hulls, `ApplyMass`, mesh cooking and the provider, pending and suspended bodies, change rounds); split from `physics/world-step` |
| `physics/world-step` | Inside `PhysicsWorld`: one step | I | L | E | `physics/building-bodies`, `world/interpolation` | physics ch. 5 (second half); 1.5 (`Simulate`, sync, forces and teleports, the characters' step, events per step, the write-back bitmap, parallel write-back, the task system, determinism) |
| `physics/collision-layers` | Collision layers | I | M | E | `physics/building-bodies`, `world/projects-settings` | physics ch. 8; 1.8 (the project's table, the matrix, filter bits, runtime changes through the scene's working copy, the Ghost layer) |
| `physics/contacts-triggers` | Contacts and triggers | I | L | E | `physics/world-step`, `physics/collision-layers` | physics ch. 6; 1.6 (events, pair folding, interest, dispatch rules, trigger limits); home of contacts and triggers reaching scripts |
| `physics/queries` | Physics queries | I | M | E | `physics/collision-layers` | physics ch. 7; 1.7 (raycasts, overlaps, masks, ignored bodies, deterministic results; no shape sweep in the API) |
| `physics/character-controllers` | Character controllers | I | L | E | `physics/world-step`, `physics/queries` | physics ch. 9; 1.9 (why kinematic, collide and slide, steps, slopes, snapping, platforms, pushing, the presence body, the root-motion hook, determinism) |
| `physics/scale-streaming` | Physics at scale and in streaming worlds | I | M | E | `physics/world-step`, `world/sub-scenes` | physics ch. 11; 1.4 (capacities and growth, `Reserve`, sliced and parallel creation, parking, the 1e5 m limit); what a world reserves and `MaxBodiesInRadius` are `worlds/physics-scripts`' |
| `physics/tuning` | Tuning and measuring | H | M | E | `physics/world-step`, `core/profiling` | physics ch. 12; 1.10, 1.12, the solver side only (`Physics.Simulation`, contact recycling, the sleep threshold, the stiffness ceiling, `physics.stats`, perf tests, `PhysicsSweep.py`); the game maker's half is `make/physics`' |

## Part 12 — Animation (`animation`)

Tracks: E

Needs of the part: `basics/math-rotations`, `basics/math-interpolation`, `core/jobs`, `world/scene-graph`, `world/systems`, `assets/importing`, `assets/models-gltf`, `assets/loading`, `assets/residency`, `draw/bounds-culling`, `draw/gpu-driven`, `draw/skinned`, `physics/character-controllers`

| id | Title | Kind | Size | Tracks | Needs | From |
| --- | --- | --- | --- | --- | --- | --- |
| `animation/problem` | The animation problem | C | S | E | `world/scene-graph` | animation ch. 1 (rigid, vertex, morph and skeletal animation; what Strata chose; the Third-Person sample's robot as the running example) |
| `animation/skeletons` | Skeletons and forward kinematics | I | M | E | `basics/math-rotations`, `assets/importing` | animation ch. 3; 1.2, 1.3 (the skeleton asset) |
| `animation/clips` | Clips: sampling motion | I | L | E | `animation/skeletons`, `assets/loading`, `basics/math-interpolation` | animation ch. 4; 1.3 (sampling with the three glTF interpolations, keyframe reduction, shared key times, the STAC cooked format, safe loading) |
| `animation/skinning` | Skinning | C | L | E | `animation/skeletons`, `draw/skinned` | animation ch. 5 (joint palettes, linear blend skinning, normals: how the joint matrices that `draw/skinned` takes as given are made) |
| `animation/importing` | Importing animated models | I | M | E | `animation/clips`, `animation/skinning`, `assets/models-gltf` | animation ch. 6; 1.4 (skeleton building, clips, entities, attachments, stable handles, import scale) |
| `animation/state-machines` | State machines | I | L | E | `animation/clips` | animation ch. 7; 1.3 (the controller asset), 1.6 (parameters, states and transitions) |
| `animation/blending` | Blending and cross-fades | I | M | E | `animation/state-machines` | animation ch. 8; 1.6 (weights, the four entries, quaternion blending, phase mismatch) |
| `animation/time-events` | Time, loops and events | I | M | E | `animation/state-machines` | animation ch. 9; 1.6 (`AdvanceEntry`, normalized time, exit times, events) |
| `animation/root-motion` | Root motion | I | M | E | `animation/time-events`, `physics/character-controllers`, `animation/blending` | animation ch. 10; 1.7 (extraction, holding the root, applying it, the character controller's hook) |
| `animation/system` | The Animation system | I | L | E | `animation/blending`, `animation/root-motion`, `world/systems`, `core/jobs`, `assets/residency` | animation ch. 11; 1.8, 1.9 (records, asset sets, job phases, the ordered publish, attachments, events, the scene services `ISkinningPoses`, `IAnimatorControl`, `IAnimationEventSource`) |
| `animation/culling` | Animating only what is seen | I | M | E | `animation/system`, `animation/skinning`, `draw/bounds-culling`, `draw/gpu-driven` | animation ch. 12; 1.8 (`WhenVisible`, reach, the renderer's visibility report, stale poses, paused frames) |
| `animation/editor` | Edit-mode poses and previews | I | M | E | `animation/system`, `animation/skinning` | animation ch. 13 (the internals half); 1.11, concept 21 (`AnimationPreview`, rest poses shared per skeleton, the `ClipStart` edit pose, render transforms for attachments, the idle cost); the how-to half is `make/animation`'s |
| `animation/limits` | What Strata's animation does not do yet | C | S | E | `animation/system` | animation ch. 16; 1.16 (blend trees, layers, sync markers, IK, morph targets, clip compression, compute skinning) and how other engines provide them |

## Part 13 — Audio (`audio`)

Tracks: E

Needs of the part: `basics/numbers`, `basics/math-vectors`, `basics/signals`, `basics/threads`, `core/first-change`, `core/frame-loop`, `core/engine-modules`, `world/systems`, `assets/importing`, `assets/loading`, `physics/bodies-colliders`

| id | Title | Kind | Size | Tracks | Needs | From |
| --- | --- | --- | --- | --- | --- | --- |
| `audio/sound-in-a-computer` | Sound inside a computer | C | M | E | `basics/numbers`, `basics/signals` | audio-input ch. 1; concepts A1-A2, A12 (samples, frames, channels, formats, gain and decibels, the pull model) |
| `audio/engine` | The audio engine | I | L | E | `basics/threads`, `core/frame-loop`, `core/engine-modules`, `audio/sound-in-a-computer` | audio-input ch. 2; 1.1 (`AudioEngine`, miniaudio, the null-device fallback, master volume, the real-time rules and the sequence lock, the engine module) |
| `audio/clips-voices-sources` | Clips, voices and sources | I | L | E | `audio/engine`, `assets/importing`, `assets/loading` | audio-input ch. 3; 1.2, 1.3 (load modes and safe decoding, the STAU cooked format and the importer, the custom miniaudio data source, destruction order with a real-time reader, lock-free parameters, `AudioSource` and its two races) |
| `audio/spatial` | Sound in space | I | M | E | `audio/clips-voices-sources`, `basics/math-vectors` | audio-input ch. 4; concepts A7-A8 (panning, attenuation models, minimum and maximum distance, rolloff, Doppler and velocity estimation) |
| `audio/scene-system` | The Audio scene system | I | L | E | `audio/spatial`, `world/systems`, `physics/bodies-colliders` | audio-input ch. 5; 1.4 (records, diffing without signals, asynchronous clips, listener choice, the up-vector policy, scene pause, one-shots with a 0.25 s deadline, services, inspection) |
| `audio/testing` | Testing sound without speakers | I | S | E | `audio/scene-system`, `core/first-change` | audio-input ch. 7 (the null device, RMS tests, settle frames, `audio.state` for agents) |

## Part 14 — Input (`input`)

Tracks: E

Needs of the part: `basics/bytes`, `basics/math-vectors`, `core/frame-loop`, `core/time`, `core/windows-events`, `world/projects-settings`

| id | Title | Kind | Size | Tracks | Needs | From |
| --- | --- | --- | --- | --- | --- | --- |
| `input/how-input-works` | How input reaches a game: events, polling, edges and intents | C | M | E | `core/frame-loop`, `core/windows-events` | new; the input part had no concept page: audio-input concepts B1, B2, B5-B7 (where input comes from, events against polling, edges, text is not keys, focus and capture, actions instead of keys in Unity, Unreal and Godot) |
| `input/devices-state` | Input devices and per-frame state | I | L | E | `core/time`, `basics/bytes`, `input/how-input-works` | audio-input ch. 8; 1.6, 1.7 (codes and names, the GLFW feed, edges, input frames and suspension, the enabled flag, typed text, captures, raw reads) |
| `input/mouse-cursor` | The mouse, the cursor and the game view | I | M | E | `input/devices-state` | audio-input ch. 9 (coordinate spaces, the render resolution, cursor modes in the game and the editor); Shift+F1, which frees a cursor the game locked, is editor code (`StrataEditor/src/Panels/GameViewPanel.cpp`) and `editor-ui/game-view`'s |
| `input/gamepads` | Gamepads | I | M | E | `input/devices-state`, `basics/math-vectors` | audio-input ch. 10 (mapping databases, conventions, axial and radial dead zones, hysteresis, several pads) |
| `input/actions` | Input actions | I | XL | E | `input/mouse-cursor`, `input/gamepads`, `world/projects-settings` | audio-input ch. 11; 1.9 (the model, the grammar, the section, compilation, evaluation, map enables, live edits, UI actions and menu repeat, performance); home of UI actions and menu key repeat |
| `input/rebinding` | Players' bindings inside the engine: the bindings file and capture | I | M | E | `input/actions` | audio-input ch. 12 (the code side) and 1.9 (players' bindings, binding capture in `InputActions`); the rebinding screen and binding capture's use side are `make/menus`' |
| `input/simulated` | Simulated input | I | M | E | `input/mouse-cursor`, `input/gamepads` | audio-input ch. 13 (the engine half); 1.8 (the virtual devices, the merge rules, release and clear, determinism); holds in fixed steps, `input.sequence` and `input.click` are `editor/stepping`'s |
