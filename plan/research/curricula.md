# How the best engine and graphics teaching material is organised and written

Research for planning "Strata Engine Docs". Every source is cited by URL in section 6 and inline as [S#]. Only ideas
and structures are taken from them, never text. Where a fetch failed or a page did not show something, this file says
so instead of guessing.

Engine facts in this file come from the checkout `G:/GameEngineAI` at `822a7a46`: the module folders under
`Strata/src/Strata/` (Animation, Asset, Audio, Core, Engine, Events, GameUI, ImGui, Input, Math, Network, Physics,
Project, Reflection, Renderer, Runtime, Scene, Scripting, World), the platform folders (GLFW, NoWindow, Posix, Vulkan,
Windows), `AGENTS.md`, and the `##`/`###` headings of `Docs/DeveloperGuide.md` and `Docs/Architecture.md`. The feature
inventory is someone else's job. These facts are here only so the checklist can say where Strata stands on a topic.

Marks used in the checklist:

- **[gap]**: most of the resources studied skip this or only mention it, but learners need it (usually it is where
  their first real bug or first "why is it like this?" comes from).
- **[S]**: Strata has this. The book has to cover both the general topic and Strata's version.
- **[S-none]**: Strata does not have it (as far as the folder and heading survey shows). Cover the general idea briefly
  and say plainly that Strata leaves it out, and why if anyone knows.
- **[S?]**: not settled by this survey. The feature inventory has to decide.

---

## 1. Master topic checklist

The list is the union of the tables of contents of Game Engine Architecture 4e [S1], Real-Time Rendering 4e [S2],
PBR 4e [S3], Lengyel's FGED volumes 1-2 [S4], 3D Math Primer [S5], Real-Time Collision Detection [S6], Game Programming
Patterns [S7], LearnOpenGL [S8], the Vulkan tutorials [S9-S11], the Godot, Unity and Unreal documentation [S19-S22],
Gaffer on Games and Gambetta [S16, S17, S24], Catto's physics talks [S25] and Algorithms for Modern Hardware [S26],
plus what Strata itself needs. Use it to check an outline: every line should map to a chapter, a section or an
appendix entry, or be listed as deliberately left out.

### 1.0 Orientation (before anything else)

- What a game is (a real-time, interactive simulation that is drawn, heard and controlled), and what an engine is
  (the reusable part). The runtime and the tools as two halves. Genres and what each demands of an engine (GEA ch. 1).
- A survey of real engines (Unreal, Unity, Godot, Bevy, in-house engines) and where Strata sits among them. **[gap]**
  Most books survey engines but none says how to pick one or what an engine like Strata is *for*.
- The anatomy of one frame, start to finish, at the level of "these ten things happen, in this order". This is the
  book's spine diagram. **[gap]** GEA has the pieces but spread over many chapters. No one-page frame map exists in
  most resources.
- Runtime architecture as layers (platform, core, resources, scene, systems, gameplay, tools). **[S]** Strata's layer
  table (`StrataTests/Architecture/Layers.json`) and composition root.
- How to read a big C++ codebase: where to start, how to follow one feature from editor click to pixel, how to use
  search, the debugger and the tests as a map. **[gap]** Almost no resource teaches this, and it is exactly what
  readers who want to work on Strata need.
- Getting the code, building it, running the editor, running the tests (submodules, CMake presets, configurations).
  **[S]** **[gap]** Books assume it. Beginners get stuck here first.

### 1.1 Foundations: programming and C++ for engines

- The compile and link model: translation units, headers, include paths, the one-definition rule, static libraries and
  shared libraries, link errors and how to read them. **[gap]**
- Build systems: CMake targets, options, presets, generators, globbing and re-configuring, precompiled headers,
  compiler caches. **[S]**
- C++ the engine uses: values and references, pointers and ownership, RAII, `Ref`/`Scope` (shared and unique
  ownership), move semantics, `enum class`, `constexpr`, templates at the level engine code needs, lambdas, the
  standard containers and their costs, `std::optional`, `std::span`, `std::filesystem`. **[S]**
- Error handling without exceptions: return values, `optional`, result structs, asserts against verifies, what
  "recoverable" means. **[S]** **[gap]** C++ tutorials teach exceptions. Engines mostly don't use them, and nobody
  explains why.
- Undefined behaviour, sanitizers, warnings as errors, portable code (MSVC, GCC, Clang differences, missing
  includes). **[S]** **[gap]**
- Strings and text: UTF-8, code points versus bytes, paths on Windows. **[S]** **[gap]**
- Code style and conventions as communication (Strata's Hazel conventions). **[S]**
- C ABIs, dynamic libraries, symbol visibility, loading code at runtime (needed for scripting and hot reload).
  **[S]** **[gap]**
- Concurrency: threads, data races, mutexes, atomics and memory ordering, lock-free basics, job systems and task
  graphs, the main-thread ownership model. GEA ch. 4. **[S]** (JobSystem, the threading model in Architecture.md.)
- How hardware runs code: caches, cache lines, prefetching, branch prediction, SIMD, data-oriented design, AoS versus
  SoA. GEA 3.4-3.5, [S26]. **[S]**
- Floating point: representation, rounding, precision far from the origin, determinism across machines. **[S]**
  (camera-relative rendering, the 20 km world limit) **[gap]** Most resources skip the consequences for large worlds.
- Hashing, UUIDs, radix sort, serialization formats (JSON, binary streams), atomic file writes. **[S]**
- Version control and working with git, reviewing a diff, writing a commit. **[gap]** (GEA 2.1 covers it briefly.)
- Third-party code: licenses (permissive against copyleft), vendoring, submodules, notices. **[S]** **[gap]**

### 1.2 Mathematics

- Coordinate systems and *conventions*: handedness, up axis, row against column vectors, matrix storage order and
  multiplication order, angle units. **[S]** **[gap]** Every resource picks a convention. Few teach how to recognise
  and translate one, and that is where most transform bugs come from.
- Vectors: arithmetic, length, normalisation, dot product (projection, angle, facing), cross product (normals,
  handedness), the scalar triple product.
- Matrices: multiplication, identity, transpose, determinant, inverse, orthogonal matrices, and what a matrix *does*
  geometrically (the basis-vector view).
- Transforms: translation, rotation, scale, shear, reflection. Composition order, TRS decomposition, hierarchies
  (local and world), transforming normals with the inverse transpose. **[S]** (`TransformNormal`, the transform cache)
- Homogeneous coordinates, points against directions.
- Projections: perspective and orthographic, the view frustum, NDC, depth precision, reversed-Z, infinite far plane,
  oblique clipping. FGED vol. 2 ch. 6. **[S]** (Strata uses reversed-Z, D3D conventions through NVRHI.) **[gap]**
  Reversed-Z and API conventions are rarely taught to beginners.
- Rotations: Euler angles and gimbal lock, axis-angle, quaternions (meaning, multiplication, conversion, slerp and
  nlerp), comparing representations.
- Interpolation: lerp, smoothstep, easing, Hermite, Bézier, Catmull-Rom, splines, continuity. [S5] ch. 13.
- Geometric primitives and tests: rays, lines, planes, spheres, AABB, OBB, capsules, triangles, frustums;
  closest-point and intersection tests. [S6], [S5] appendix A.
- Numerical robustness: epsilons, degenerate cases, why tests that are exact on paper fail in floats. [S6] ch. 11-12.
  **[gap]**
- Calculus for simulation: derivatives as rates, integrals as accumulation, numerical integration (explicit Euler,
  semi-implicit Euler, Verlet, RK). [S5] ch. 11-12, Catto's numerical integration talk [S25].
- Randomness: pseudo-random generators, seeding, distributions, hashing for noise, blue noise. **[S]** (`BlueNoise.h`,
  the script SDK's `Random`)
- Noise and procedural generation: value, Perlin, simplex, fBm. [S12] (Scratchapixel), [S15] (Book of Shaders).
- Probability and Monte Carlo integration, importance sampling, low-discrepancy sequences (needed for GI, AO and
  IBL). [S3] ch. 2. **[gap]** Game books skip it, then the GI chapter has nothing to stand on.
- Signals: sampling, aliasing, Nyquist, reconstruction filters, convolution, mip filtering. **[gap]** This is the
  shared theory under texture filtering, anti-aliasing, TAA, shadow filtering and audio. Usually it is taught five
  times, badly, or not at all.
- Colour maths: linear against gamma-encoded values, sRGB, colour spaces (XYZ, Rec.709, ACES), luminance, white
  balance, chromatic adaptation. FGED vol. 2 ch. 5, [S27]. **[S]** (white balance locus, filmic constants) **[gap]**
- Spherical functions: solid angle, spherical coordinates, spherical harmonics, cube maps, octahedral maps. **[gap]**
- Geometric and Grassmann algebra (FGED vol. 1 ch. 4): optional; mark it as further reading.

### 1.3 Memory

- Stack, heap, static storage. Lifetimes and ownership. Dangling pointers.
- Allocators: linear or arena, stack, pool, free list, ring, range allocators. Fragmentation. Alignment. GEA 6.2.
  **[S]** (`RangeAllocator`, `StagingPool`, the geometry pool)
- Handles instead of pointers: generational indices, UUID handles, why references across save and load are IDs.
  **[S]** (`AssetHandle`, entity IDs) **[gap]**
- Containers and their memory behaviour. Strings and allocation.
- Memory budgets, tracking, leak detection, debug fill patterns, memory stats in game. GEA 2.4, 10.9.
- GPU memory: heaps, residency, budgets, eviction, staging and upload. **[S]** (residency, mip streaming, upload steps)
  **[gap]** Graphics tutorials allocate and never free. Engines live or die by this.
- Deferred release: why GPU resources cannot be freed the moment the CPU is done with them. **[S]**
  (`Renderer::ReleaseDeferred`, `DeferredReleaseQueue`) **[gap]**

### 1.4 The game loop and time

- Loop styles: the basic loop, event-driven loops, callbacks, who owns the loop (GPP "Game Loop" [S7], GEA ch. 8).
- Measuring time: high-resolution clocks, delta time, frame-time spikes.
- Fixed timestep with accumulator, semi-fixed steps, the spiral of death and a maximum step count, interpolating the
  drawn state [S16]. **[S]** (`Scene.Timing`, `GetFixedTimestep`, `GetMaxFixedSteps`, drawn transforms,
  `BreakInterpolation`)
- Timelines: real time, game time, pause, time scale, stepping a paused game by fixed steps. **[S]** (Stepping a paused
  game, `GetFixedStepCount`) **[gap]**
- Frame pacing, vsync, latency (input to photon), frames in flight between CPU and GPU. **[gap]**
- The multi-threaded frame: main thread, job system, render submission, the GPU running a frame behind. **[S]**
- Determinism: what breaks it (floats, order, threads), when games need it (replays, lockstep networking).
- Engine start-up and shut-down order, modules and services. GEA 6.1. **[S]** (`EngineModule`,
  `ApplicationSpecification::Modules`, registries)

### 1.5 Platform and windowing

- Why an engine has a platform layer. Where OS code is allowed to live. **[S]** (`src/Platform/`, `ExternalOwners`)
- Windows, events, resizing, minimising, fullscreen modes, monitors, DPI scaling. **[S]** (GLFW) **[gap]** DPI is
  usually missing.
- Headless runs and running without a window. **[S]** (`NoWindow`)
- GUI against console programs on Windows, how shells wait for them. **[S]** **[gap]**
- File systems: paths, UTF-8 at the boundary, watching files, file locks, atomic writes. **[S]**
- Permissions and private files (tokens, code the engine loads). **[S]** **[gap]**
- Processes, command lines, environment.
- Crashes: signals and structured exceptions, crash containment, symbolising stack traces. **[S]** (`CrashGuard`,
  `Symbolizer`) **[gap]**
- Platform differences: Windows, Linux, macOS through MoltenVK. **[S]**

### 1.6 Input

- Devices: keyboard, mouse, gamepads, touch. GEA ch. 9.
- Polling against events. Edges (pressed, released) against levels (held).
- Keyboard: physical key against character, text input, key repeat. **[S]** (script SDK key repeat) **[gap]** Text
  input and IME are usually missing.
- Mouse: relative motion, capture and cursor modes, sensitivity. **[S]**
- Gamepads: dead zones, response curves, mappings. **[S]**
- Actions and bindings: mapping devices to intents, rebinding, saving bindings, input contexts. **[S]**
  (`InputActions`, project input actions) **[gap]** Tutorials read raw keys. Shipped games never do.
- Input routing: UI first or game first, consumption, focus. **[S]** (UI scene system)
- Simulated input for tests and automation. **[S]** (Simulated input) **[gap]**
- Accessibility: remapping, hold against toggle.

### 1.7 Resources and assets

- Why assets need a pipeline: source files, imported and cooked data, platform formats. GEA 1.6, ch. 7.
- Asset identity: handles (UUIDs) against paths, `.meta` files, moves and renames that keep references. **[S]**
  **[gap]**
- The registry or asset database, the resource manager, reference counting against explicit residency. **[S]**
- Importers: versioning (re-import when output changes), dependencies, determinism, cancellation, background imports.
  **[S]**
- References and dependency graphs: delete checks, pruned exports, prefetching. **[S]**
- Loading asynchronously and never blocking a frame, "not loaded yet" as a normal state. **[S]** **[gap]**
  Tutorials load synchronously at start-up.
- Streaming and residency: requests, pins, priorities, budgets, eviction. **[S]**
- Textures: formats, block compression (BC1-7), mip chains and their sizes, cooking, mip streaming, bindless slots.
  **[S]**
- Meshes: vertex layouts, index buffers, LODs, geometry pools and compaction. **[S]**
- Formats: glTF, images, fonts, audio files, scene documents, packs and archives. **[S]**
- Untrusted input: rejecting truncated or garbage files, crafted fonts, corruption tests. **[S]** **[gap]** Rarely
  taught. Security and robustness of loaders.
- Hot reload of assets, file watching. **[S]**
- Thumbnails and previews (tools side). **[S]**

### 1.8 The scene and entity models

- What a game world is made of: static geometry, dynamic objects, data-driven design (GEA ch. 16-17).
- Object models: deep inheritance, component-based objects, entity-component-system. The trade-offs of each
  (GPP "Component" [S7], GEA 17.2, the Bevy ECS pages [S18]).
- ECS in practice: entities as IDs, component storage, views and iteration, systems, ordering, structural changes
  during iteration. **[S]** (EnTT, scene systems, `MakeSceneSystemDescriptor`)
- Components as plain data, tag components, registering components (serialization, inspector, scripting). **[S]**
- Transform hierarchies, scene graphs, world-transform caches, dirty flags (GPP "Dirty Flag"), the contract for writing
  transforms. **[S]** **[gap]** Why caches need change signals is rarely explained.
- Names, tags, indexes and queries. Object references and world queries (GEA 17.5). **[S]**
- Events and messaging: observers, event queues, immediate against deferred (GPP "Observer", "Event Queue"). **[S]**
- Services and registries (GPP "Service Locator") against singletons. **[S]** (scene services, `GetModules().Find<T>()`)
- Reflection and property metadata: how the inspector, serializer and scripts learn about a component. **[S]**
  (Reflection module) **[gap]**
- Scene documents: serialization, streaming readers and writers, versioning formats, unknown components. **[S]**
- Prefabs: templates, instances, overrides, syncing. **[S]** **[gap]** Few books cover prefabs, yet game makers use
  them every day.
- The scene's life: edit scene against play copy, entering and leaving play mode, switching scenes, releasing a scene
  in the background. **[S]**
- Sub-scenes and composition (bridge to world streaming). **[S]**

### 1.9 Rendering

#### 1.9.1 The GPU and the graphics API

- How a GPU works: massively parallel cores, warps or waves, occupancy, memory bandwidth, why branching costs.
  RTR ch. 3 and 23. **[gap]** For beginners this is usually missing or comes too late.
- The pipeline at a glance: vertices, primitives, rasterization, fragments, output merger. RTR ch. 2.
- Explicit APIs (Vulkan): instance, physical and logical device, queues, command buffers, synchronization (fences,
  semaphores, barriers), memory, descriptors, pipelines, dynamic rendering, swap chains, frames in flight.
  [S9]-[S11]. **[S]**
- Abstraction layers (RHIs): why engines wrap the API, what NVRHI hides and what it does not. **[S]** **[gap]** No
  tutorial teaches the RHI layer that every real engine has.
- Bindless resources. **[S]** (bindless texture table)
- Shaders: languages (HLSL syntax, Slang, GLSL), compilation to SPIR-V, embedding, bindings and registers, push
  constants, permutations and variants. **[S]** (Slang, `strata_add_shaders`, `ST_SKINNED` variants)
- Compute shaders, dispatches, UAV barriers. **[S]**
- Validation layers, debug names, GPU debuggers (RenderDoc), reading a frame capture. **[gap]** LearnOpenGL has one
  debugging chapter. Most resources have none.
- Conventions: NDC, viewport flip, UV origin, depth range, winding and front faces. **[S]** **[gap]**

#### 1.9.2 Drawing a scene

- Cameras: view and projection, FOV, aspect, near and far, culling volumes. **[S]**
- Depth testing, face culling, blending, stencil.
- Visibility: frustum culling, occlusion culling, bounding volumes, spatial indexes, portals (FGED vol. 2 ch. 9,
  RTR ch. 19). **[S]** (`SpatialIndex`, `Cull.comp`)
- The render scene: extraction from the game scene into proxies, change logs, a GPU copy. **[S]** **[gap]** The split
  between game scene and render scene is essential and rarely taught.
- Draw lists, sort keys, state changes, batching, instancing. **[S]**
- GPU-driven rendering: indirect draws, compute culling, feedback. vkguide's GPU-driven chapters [S10]. **[S]**
- Level of detail: discrete LODs, cross-fades, LOD selection. **[S]**
- Rendering architectures: forward, deferred, forward+ and clustered, visibility buffers, the trade-offs (RTR ch. 20).
  **[S?]**
- Frame graphs and render graphs (vkguide "Project Ascendant"). **[S?]**
- Camera-relative rendering and precision. **[S]** **[gap]**
- Uploads and streaming on the GPU side: upload queues, budgets, staging. **[S]**
- Reading GPU data back without stalling. **[S]** (`TextureReadback`)

#### 1.9.3 Materials and shading

- Light and surfaces: radiometry (flux, irradiance, radiance), photometry (lumens, lux, candela), the rendering
  equation, BRDFs. RTR ch. 8-9, [S3] ch. 4, [S27] Ciechanowski. **[S]**
- From Lambert and Phong to physically based shading: microfacets, GGX, Fresnel and F0 from IOR, Smith visibility,
  metal against dielectric, roughness remapping, energy conservation, multiple-scattering compensation [S23] Filament.
  **[S]** (`GetSpecularEnergy`)
- Textures: UVs, sampling, filtering (bilinear, trilinear, anisotropic), mipmaps, wrap modes, texture slots. **[S]**
- Normal maps and tangent space, reconstructing Z, mirrored instances and flipped tangents. **[S]** **[gap]** Mirrored
  geometry is almost never mentioned.
- Clear coat, glass, transmission, transparency, alpha testing and sorting, order-independent transparency. **[S]**
- Material systems and parameters for artists, material instances, never editing loaded materials in place. **[S]**
- Skinned meshes on the GPU. **[S]**
- HDR targets and sanitizing (NaN and Inf). **[S]** **[gap]**

#### 1.9.4 Lights and shadows

- Light types: directional, point, spot, area. Physical light units and exposure. **[S]**
- Light culling: tiles, clusters. **[S?]**
- Shadow maps: depth bias, peter-panning, PCF, PCSS, cascades and cascade layouts, stabilisation, local light atlases,
  caching static shadows, screen-space shadow masks, contact shadows. RTR ch. 7, FGED ch. 8. **[S]**
- Ambient occlusion: SSAO, GTAO, denoising, bent normals. **[S]**
- Image-based lighting, environment maps, reflection probes and their capture and baking. **[S]**
- Screen-space reflections: marching, validation, fade-out, their limits. **[S]**
- Sky and atmosphere: scattering models, sky presets. **[S]**
- Fog: height fog, volumetric fog, froxels. **[S]**

#### 1.9.5 Global illumination

- The problem: indirect light, the rendering equation's recursion. RTR ch. 11, [S3] ch. 13.
- The approaches and their trade-offs: lightmaps, irradiance volumes and probes, voxel cone tracing, signed distance
  fields, screen-space GI, radiance cascades, hardware ray tracing, path tracing as reference. **[gap]** No single
  resource compares them for a learner. RTR covers them as a survey. Tutorials cover one.
- World-space against screen-space, and why Strata traces only the world. **[S]** (voxel clipmap, GI layout; GI is
  experimental)
- Reference renders and validation: white-furnace tests, comparing to a path tracer. [S23]. **[S]** **[gap]**

#### 1.9.6 Temporal effects and post-processing

- Aliasing and anti-aliasing: MSAA, morphological AA (FXAA, SMAA), temporal AA, jitter, motion vectors, history
  rejection, ghosting. **[S]**
- Upscaling (and why Strata does not use TAA upscaling; the look direction). **[S]**
- HDR and tone mapping, filmic curves, exposure and auto-exposure, bloom, depth of field, motion blur, colour grading
  and LUTs, white balance, vignette, film grain, chromatic aberration. RTR ch. 12, Filament's imaging pipeline [S23].
  **[S]**
- A neutral post chain for exact-pixel tests. **[S]** **[gap]**

#### 1.9.7 Everything else drawn

- Text: font files, rasterizing glyphs, atlases, shaping, measuring, SDF text, fonts as untrusted input. **[S]**
  **[gap]**
- Debug drawing, gizmos, overlays. **[S]**
- Terrain: heightfields, materials, LOD. **[S?]** (terrain appears in the render scene headers)
- Particles and VFX. **[S?]** (no particle module found in the folder survey)
- Water. **[S?]** (the showcase has a water stand-in)
- Decals, billboards, impostors. FGED ch. 10. **[S?]**
- Non-photorealistic rendering. RTR ch. 15. **[S-none]**, probably

#### 1.9.8 Making it fast and making it scale

- GPU timing, pass timers, budgets, profiling tools. **[S]** (`GPUPassTimer`)
- Pipeline optimisation: finding the bottleneck (CPU, vertex, fragment, bandwidth). RTR ch. 18.
- Quality settings and scalability: presets, per-platform defaults, players' graphics options. **[S]**
  (`RendererQualitySettings`, `IGameGraphics`) **[gap]** Shipping games need it. Tutorials never have it.

### 1.10 Animation

- Kinds of animation: rigid, per-vertex, morph targets, skeletal. GEA ch. 13.
- Skeletons, joints, bind and rest poses, local and model space, poses as data and not as entities. **[S]**
- Clips: keyframes, sampling, interpolation, compression, events. **[S]**
- Skinning: matrix palettes, linear blend skinning, its artefacts, dual quaternions. **[S]**
- Blending: lerp blends, additive, layers and masks, blend trees. **[S?]**
- State machines and controllers, transitions. **[S]** (`AnimationController`)
- Root motion. **[S]**
- Parallel and deterministic evaluation. **[S]**
- Inverse kinematics, constraints, retargeting, motion matching. GEA 13.11-13.12. **[S?]**
- The animation pipeline: import from glTF, previews. **[S]**

### 1.11 Collision and physics

- Do you need physics? Middleware against your own (GEA 14.1-14.2). Strata uses box3d. **[S]**
- Shapes: spheres, boxes, capsules, convex hulls, meshes, heightfields.
- Broad phase: dynamic BVH, sweep and prune, grids [S6] ch. 6-7, Catto's dynamic BVH talk [S25].
- Narrow phase: SAT, GJK, EPA, contact manifolds [S25].
- Rigid body dynamics: mass, inertia tensor, forces, torque, impulses, integration.
- Constraints and solvers: sequential impulses, warm starting, soft constraints, joints [S25].
- Islands, sleeping, settling. **[S]** (settling and the sweep)
- Continuous collision detection and tunnelling.
- Collision layers and filtering, triggers and sensors, contact events. **[S]**
- Kinematic bodies and character controllers. **[S]** **[gap]** Every game needs a character controller and few books
  build one.
- Scene queries: raycasts, shape casts, overlaps. **[S]**
- Fixed rate, interpolation, determinism. **[S]**
- Performance: contact recycling, body-creation limits, constant-time diagnostics. **[S]**
- Debug visualisation and physics instruments. **[S]**
- Integrating physics with the scene (who owns the transform). **[S]** **[gap]**
- Advanced: ragdolls, vehicles, cloth, destruction, fluids, buoyancy. GEA 14.6. **[S?]**

### 1.12 Audio

- Sound as a signal: waves, frequency, amplitude, decibels, sampling rate, bit depth. GEA 15.1-15.2.
- Digital audio: PCM, decoding, streaming against preloading, mixing, clipping, voices and voice limits. **[S]**
  (`AudioVoice`)
- 3D audio: attenuation, panning, Doppler, listeners, occlusion and reverb. **[S?]** (beyond attenuation and panning)
- Audio engine architecture: the mixer thread, latency, a device abstraction, a null device for tests. **[S]**
  (miniaudio)
- Game-side audio: sources, clips, buses or groups, music, ducking. **[S?]**
- Audio middleware (FMOD, Wwise) for comparison.

### 1.13 Gameplay and scripting

- Game flow: menus, levels, loading, saving, quitting. GEA 17.10. **[S]** (`IGameSaves`, scene loading from scripts)
- Gameplay patterns: Command, State, Type Object, Subclass Sandbox, Update Method, Object Pool, Spatial Partition [S7].
- Updating game objects: phases, ordering, dependencies between objects (GEA 17.6-17.7).
- Scripting: why engines have scripts, the options (embedded VMs like Lua and C#, visual scripting like Blueprints,
  native modules), and their trade-offs. **[S]** (C++ modules behind a C ABI)
- A script ABI: plain C data, versioning by appending, host functions. **[S]** **[gap]**
- Crash containment and hot reload. **[S]** **[gap]**
- Script lifecycle, fields exposed to the editor, attaching scripts, spawning prefabs. **[S]**
- The gameplay API surface: entities, transforms, input, physics, audio, time, random, timers, saves, the window.
  **[S]**
- Cameras for games: follow cameras, third-person cameras and collision, camera shake. **[S?]** (ThirdPerson sample)
  **[gap]** Rarely taught and hard to get right.
- Game AI basics: pathfinding (A*), steering, state machines, behaviour trees, navigation meshes. Red Blob Games
  [S28]. **[S-none]**, probably
- Game design basics for the game-maker track: the core loop, prototyping, scope, game feel, playtesting, levels.
  **[gap]** Engine docs teach the tool but not the craft, yet the brief says some readers never made a game.

### 1.14 User interface

- Immediate-mode against retained-mode UI. **[S]** (ImGui for tools, GameUI for games)
- Layout: rects, anchors, pivots, scaling, resolution independence. **[S]**
- Widgets, styles, themes. **[S]**
- Input, focus, navigation with gamepads, hit testing, world-space UI through a camera ray. **[S]**
- Text in UI, localisation, right-to-left text. **[S?]** (beyond text)
- Rendering UI: batching, atlases, one request per texture per frame. **[S]**
- HUDs, menus, settings screens. Accessibility (scaling, contrast).

### 1.15 Tools and editors

- Why engines have editors. The game world editor (GEA 16.4).
- Editor architecture: a core without UI and a UI on top, panels, views, selection. **[S]**
- Commands and undo/redo, transactions, one undo step per change. GPP "Command". **[S]**
- Inspectors driven by reflection, inactive properties. **[S]**
- Viewports, gizmos, cameras, placement and previews. **[S]**
- Content browser, imports, thumbnails. **[S]**
- Play in editor, edits while playing. **[S]**
- No silent data loss: background saves, autosave, recovery, unsaved-changes checks. **[S]** **[gap]**
- Prefab editing. **[S]**
- Project settings and preferences. **[S]**
- Launcher, templates, samples. **[S]**
- Automation: an editor API (JSON-RPC), a CLI client, an MCP server, AI agents making games through it, the security
  model (loopback, tokens). **[S]** **[gap]** Unique to Strata among the resources studied. It needs its own chapter.
- Exporting games. **[S]**

### 1.16 World streaming

- Large worlds: why one scene does not scale, the coordinate limit, floating origin against camera-relative
  rendering. **[S]**
- World partition: cells, a persistent scene, sub-scenes, loading budgets. GEA 17.3-17.4. **[S]**
- Streaming policies: distance, priorities, prefetch, hysteresis. **[S]**
- Editing streamed worlds. **[S]**
- Physics and streaming. **[S]**
- HLOD and impostors for distant cells. **[S?]**

### 1.17 Networking

- Basics: sockets, UDP against TCP, packets, reliability, bandwidth. Gaffer's networking series [S17].
- Models: peer-to-peer lockstep, client-server, authority [S17], [S24].
- Hiding latency: client-side prediction, reconciliation, entity interpolation, lag compensation [S24].
- Serialization and state replication, snapshots, delta compression, networked physics.
- Security: never trust the client.
- **[S-none]** for multiplayer gameplay. Strata's `Network` module holds only the editor's JSON-RPC (`RpcServer`,
  `RpcClient`, `Socket`, `JsonRpc`). The book should teach multiplayer as general knowledge in one chapter or an
  appendix, say plainly that Strata has none, and use the RPC server as the networking that Strata does have (sockets,
  framing, connection limits, authentication).

### 1.18 Debugging and profiling

- Logging and tracing: levels, background log writing, throttling. **[S]**
- Assertions and verifies. **[S]**
- Debuggers: breakpoints, watches, the call stack, debugging optimised builds, attaching to a running process.
  **[gap]**
- Debug drawing, in-game menus and consoles, console variables, debug cameras, cheats. GEA ch. 10. **[S?]**
  (beyond debug draw)
- CPU profiling: instrumentation (Tracy), sampling profilers, the frame profiler, profile stages. **[S]**
- GPU profiling: timers, captures. **[S]**
- Memory profiling and leak detection.
- Method: measure first, budgets, statistically sound comparisons ([S26] "getting accurate results"). **[S]**
  (`Perf/Budgets.json`, `PerfStability.py`) **[gap]**
- Crash reports, stack symbolisation, script crash locations. **[S]**
- Rendering debug views (lighting, normals, overdraw). **[S]**

### 1.19 Build, test and ship

- Configurations (Debug, Release, Dist), what each turns on or off. **[S]**
- Optional modules and the composition root. **[S]**
- Continuous integration, many compilers and platforms. **[S]**
- Testing an engine: unit tests (doctest), GPU tests on a shared device, exact-pixel tests, end-to-end tests that start
  executables, corruption sweeps, the feature test, perf tests and budgets. **[S]** **[gap]** Engine books almost
  never discuss testing. Godot has one contributor page [S20].
- Packaging and installers, what a release ships. **[S]**
- Exporting a game: runtime, manifest, cooked packs. **[S]**
- Versioning and releases, release notes. **[S]**
- Contributing: the review checklist, commit hygiene, rules for agents. **[S]**

---

## 2. What makes each resource teach well or badly

For each: what works, what does not, and patterns worth adopting (marked **Adopt**). This is judged from tables of
contents, sample chapters and structure pages, not from reading every book cover to cover.

### Game Engine Architecture, 4th edition (Gregory) [S1]

- Works: the breadth is unmatched. It covers everything from version control to motion matching, and its two-volume
  split (foundations and core systems; graphics, motion and sound) is a sound order. Each subsystem chapter starts
  with the problem ("Do you want physics in your game?"), surveys the industry's approaches, then goes into
  architecture. It ends with an honest "what we didn't cover" chapter.
- Weak spots: it is a survey. There is little runnable code and nothing to build, few exercises, and a learner cannot
  check their understanding. Topics sit far apart (the loop in ch. 8, the gameplay update in ch. 17), so the reader
  has to assemble the frame alone.
- **Adopt:** the problem → industry approaches → architecture order for every subsystem chapter. An explicit "what
  this book leaves out" page. Its master structure (tools and fundamentals → support systems → loop → devices →
  debugging → rendering → animation → physics → audio → gameplay) as a check on the book's order.

### Real-Time Rendering, 4th edition [S2]

- Works: dense and authoritative. Every claim points to its source, and it has a huge bibliography. The figures are
  excellent (676 of them, 400+ online). The companion site adds a resource page per chapter, free online chapters and
  corrigenda.
- Weak spots: a reference for people who already know graphics. It has almost no code, no exercises, and teaches
  techniques side by side without a project to try them on.
- **Adopt:** per-chapter "further reading" with live links, kept on the site. Online errata. Figures as the main
  explanation of a technique (a figure for every algorithm). Citation discipline: every non-obvious technique credits
  its paper or talk.

### Physically Based Rendering, 4th edition (pbr-book.org) [S3]

- Works: literate programming. The book *is* the complete program (pbrt). Every fragment of code appears in the text
  and has a name, and there is an index of fragments and of identifiers. Chapters end with Further Reading and
  Exercises. The whole book is free online.
- Weak spots: very long and very demanding. The literate fragment notation is hard for beginners to follow.
- **Adopt:** an index of code identifiers (each engine class or function the book discusses links to every page that
  explains it). Further reading and exercises at the end of every chapter. The idea that the text and the real code
  are one artefact, made workable for Strata by pulling excerpts straight from the source (see section 3).

### Foundations of Game Engine Development (Lengyel) [S4]

- Works: mathematically rigorous and compact. It has code listings in C++ (36 in vol. 1, 82 in vol. 2), exercises in
  every chapter (62 and 52) with solution guides as PDFs, and many numbered equations and figures. It covers topics
  others skip: depth precision, infinite and oblique projections, portal systems, Plücker coordinates.
- Weak spots: dense for beginners, and vol. 3-4 (models and materials, physics) are still planned.
- **Adopt:** exercises with published worked solutions. Treat projection and depth precision as a chapter of their own.

### 3D Math Primer for Graphics and Game Development (gamemath.com) [S5]

- Works: free online. Every operation is given as "the official rule" *and* "the geometric interpretation".
  Conventions get a section of their own. It admits simplifications openly ("helpful lies"). Every chapter has
  exercises, with answers in an appendix. It goes all the way to mechanics and curves.
- **Adopt:** pair every rule with its geometric meaning. A conventions page early on. Label simplifications as such
  and pay them off later. This is the best model for the math part of the book.

### Real-Time Collision Detection (Ericson) [S6]

- Works: two whole chapters on robustness, numerical and geometric, which hardly any other book has. It has an
  optimisation chapter and a design-issues chapter before any algorithm.
- **Adopt:** a "why does this fail in floats" section in every geometry-heavy chapter.

### Game Programming Patterns (Nystrom) [S7]

- Works: a fixed per-chapter template (Intent, Motivation, The Pattern, When to Use It, Keep in Mind, Sample Code,
  Design Decisions, See Also). Motivation is the longest part. The sample code grows in stages, and each stage is
  forced by a flaw in the one before (the Game Loop chapter: bare loop → sleep → variable step → fixed step with lag →
  interpolation). Simple hand-drawn figures with alt text. Margin asides for history and jokes that never interrupt the
  main line. A warm first-person voice with honest hedges ("usually", "more or less"). Free online.
- Weak spots: patterns are teachable alone, so it never shows how they combine in one engine.
- **Adopt:** a recognisable fixed template per chapter type. The flaw-driven code progression. "Design decisions" as a
  closing section that lists the options and when each wins. Asides kept apart from the main text.

### Crafting Interpreters (Nystrom) [S13]

- Works: the model for a web textbook that builds one program from nothing. Every line of the program appears in the
  book. Each snippet names its file and says where it goes ("after this method", "replace this line"), with a nearby
  line repeated as an anchor. Every chapter ends with a program that runs and can be checked. It has numbered
  Challenges and a closing Design Note essay that steps back to discuss trade-offs across languages. Hand-drawn
  illustrations carry small jokes that reinforce the concept. It builds the same language twice (tree-walk, then
  bytecode VM), so the second pass deepens the first rather than repeating it.
- Weak spots: it works because the program is small enough to show in full. Strata is not, so "every line" cannot
  carry over.
- **Adopt:** the anchor convention for excerpts (file, symbol, where it sits). A runnable checkpoint at the end of
  every tutorial. Challenges, plus a Design Note that separates "how Strata does it" from "how else it could be done".
  The two-pass idea: first a toy version a reader can hold in their head, then Strata's production version and why it
  differs.

### LearnOpenGL [S8]

- Works: a famous on-ramp for people with no graphics background. Bold terms on first use, acronyms spelled out once,
  pipeline figures, code built up in numbered stages and explained parameter by parameter. Chapters end with exercises
  linked to solution source files. Full source for every chapter. Review pages at the ends of parts. A closing project
  (Breakout) ties it together. A dedicated debugging chapter. Guest articles extend it (CSM, skeletal animation,
  frustum culling).
- Weak spots: code with global state, OpenGL-specific habits that engines don't follow, and the "engine" never gets
  architecture. Much of what a renderer must handle (streaming, residency, threading) is missing.
- **Adopt:** exercises with linked solutions. A part-ending review page (a glossary of what the part introduced).
  A capstone project per track. A debugging chapter early in the rendering part, not at the end.

### Vulkan Tutorial (vulkan-tutorial.com) and the Khronos Vulkan Tutorial [S9], [S11]

- Works: the Overview chapter maps every step to the first triangle before any code (instance → device → surface and
  swap chain → views → pipeline → commands → loop) and closes with a checklist. It explains API conventions (naming,
  create-info structs, validation layers) before the reader meets them, and says openly where it cheats (positions
  hard-coded in the shader). The Khronos rewrite modernises it (Vulkan 1.4, dynamic rendering, timeline semaphores,
  Slang, C++20, RAII), links every API name to the spec, and ends every chapter with a link to the full code so far.
  It also states prerequisites precisely.
- Weak spots: a very long road of boilerplate before the first payoff. Little on how an engine organises it.
- **Adopt:** a "map of the territory" opening for every big part. A "how to read the code that follows" box before
  the first excerpt of a new subsystem. Being open about shortcuts. API names linked to the reference.

### vkguide.dev [S10]

- Works: it builds an *engine*, not a sample. Libraries remove the boilerplate (a bootstrapper, a memory allocator,
  ImGui) so chapters reach interesting results quickly. It shows a picture of the end result first. It has extra
  chapters on what tutorials skip (asset systems, CVars, multithreading, GPU-driven rendering, frame graphs, a frame
  analysis of a shipped game) and a "from tutorial to engine" series.
- Weak spots: it requires prior OpenGL or DirectX knowledge, explicitly.
- **Adopt:** show the destination first. Spend the reader's attention on concepts, not boilerplate: in Strata's case,
  NVRHI already plays the role vkguide's libraries do, so the book explains raw Vulkan once and then works at the NVRHI
  level. A "frame analysis" chapter that walks through a captured Strata frame pass by pass.

### Scratchapixel [S12]

- Works: hands-on results before theory, stated as policy. The math lessons are a *reference* consulted when a lesson
  needs them, not a gate at the start. It has a foundations track in a strict order plus side tracks (maths, geometry,
  imaging, procedural generation, tooling).
- **Adopt:** math taught "just in time" inside the chapter that needs it, with a math reference appendix to look it up
  later. Avoid a 200-page math wall before the first picture.

### Catlike Coding [S14]

- Works: each tutorial opens with a bullet list of what you'll learn, the prerequisites (previous tutorials by name),
  a level, and the engine version it was made with (and which version it was upgraded to). There are screenshots after
  nearly every meaningful step, often paired with the frame debugger so the reader sees both the result and how it was
  drawn. Code shows only the changed part with "…" for the rest. Short Q&A asides explain a language feature the moment
  it appears ("What does `out` mean?"). Each tutorial links its repository and a PDF and ends with "next tutorial".
  Tutorials are grouped into series that build on one another.
- Weak spots: Unity-specific. Changes are described in prose, without diff markers, so readers can miss a line.
- **Adopt:** the opening strip (learn / prerequisites / level / version). A screenshot per step, paired with a debug
  view or a RenderDoc capture for rendering chapters. Q&A asides for C++ features as they come up, which is exactly how
  to teach C++ "as it goes". Series with prerequisites.

### The Book of Shaders [S15]

- Works: every example is live and editable next to the text. Exercises are phrased as "change this line, then notice
  that…", which pairs action and observation. It plots functions so the reader sees what a formula does. "For your
  toolbox" sections point to tools and libraries.
- Weak spots: limited to fragment shaders, and it is unfinished in places.
- **Adopt:** "predict, change, observe" exercises. Interactive plots of shaping functions (tone curves, falloffs,
  easing) in the browser. A toolbox box per chapter.

### Gaffer on Games [S16], [S17]

- Works: "Fix your timestep" teaches through five versions of a loop. Each version is a reasonable fix for the flaw in
  the one before, and ends with a sentence that reframes the whole idea (the renderer produces time and the simulation
  consumes it). The networking series moves through history (lockstep → client-server → prediction). The voice is a
  patient mentor's.
- Weak spots: no figures at all, so timing ideas that a timeline diagram would make obvious stay abstract.
- **Adopt:** the history-and-flaw progression for design topics. A one-sentence reframe as each chapter's key idea.
  Fix the weakness: a timeline figure for every timing concept.

### Gabriel Gambetta, Fast-Paced Multiplayer [S24]

- Works: four short parts, each solving the problem the previous one leaves open (authoritative server → prediction
  and reconciliation → interpolation → lag compensation), plus a live demo where the reader changes latency and sees
  the effect.
- **Adopt:** a small interactive simulation for any concept about time and latency (fixed steps, interpolation,
  frames in flight, streaming).

### Ciechanowski's articles and Red Blob Games [S27], [S28]

- Works: dozens of interactive figures per article with sliders and dragging. The demo shows an effect *before* the
  term is named, then the term is defined, then the formula. It goes from the simplest case (one light, one matte
  surface) to the full one. Red Blob Games does the same for algorithms (A*, hex grids, noise) and publishes how it
  builds the figures.
- **Adopt:** "see it, name it, write it down" as the order for every new concept. A small, budgeted set of
  interactive figures for the hardest ideas (dot product, projection, the BRDF lobes, cascades, the accumulator,
  quaternion slerp, mip selection). Use them only where they add something a static figure cannot.

### Filament's "Physically Based Rendering in Filament" [S23]

- Works: a notation table before any equation. Every concept goes from physical motivation → the exact equation →
  the real-time approximation and why → the shader code. Parameter sweeps show what each input does (metallic,
  roughness, reflectance). White-furnace and reference comparisons validate the result. It states limitations and
  unfinished parts openly.
- **Adopt:** this is the model for Strata's rendering chapters: motivation → equation → approximation and its cost →
  Strata's Slang code → a sweep figure rendered by the engine → a validation figure (Strata has a white-furnace test
  and debug views). A per-part notation table.

### Ray Tracing in One Weekend [S29]

- Works: an image after nearly every step, so readers compare their output with the book's. Listings name their file,
  and changed lines are highlighted and removed lines marked. It says plainly what is simplified and what isn't optimal.
- **Adopt:** highlight what changed in an excerpt. "Your result should look like Figure N" checkpoints in tutorials.

### Learn WebGPU for C++ [S30]

- Works: links the resulting code at the start and end of every page. It offers two ways in (read everything in order,
  or skip the boilerplate and come back). Code tabs switch every block between two API flavours. Every chapter is
  labelled with its status (up to date, older version, work in progress).
- **Adopt:** per-page status relative to the engine (verified at commit X, or stale). Two ways in for each part.

### The Rust Programming Language [S31]

- Works (from its well-known structure; the fetched page only showed front matter): concept chapters interleaved with
  project chapters (a guessing game early, a command-line tool in the middle, a multithreaded web server at the end),
  so each project uses what the chapters before it taught. Listings are numbered per chapter with file names, code that
  fails to compile is marked with an icon, and the expected output is shown.
- **Adopt:** interleave project chapters in each track. Mark "this code is wrong on purpose" excerpts visibly.

### learncpp.com [S32]

- Works: teaches C++ from zero with no prior experience assumed. Numbered lessons, and every chapter ends with a
  summary and a quiz. Optional chapters are labelled as such (bit manipulation, constexpr functions).
- **Adopt:** a summary-and-quiz page per chapter. Optional sections marked. The book should link learncpp for
  general C++ rather than re-teaching all of C++. It teaches the C++ Strata uses, when Strata uses it.

### Bevy's quick start [S18]

- Works: candid about limits (breaking changes, and a recommendation to use Godot if the reader needs more
  features). A tiny game within the first pages, and ECS deferred until the reader has seen it work.
- **Adopt:** honesty about Strata's maturity and gaps (experimental GI, no networking). Make something before
  explaining the architecture.

### Godot documentation [S19], [S20]

- Works: the front page sends readers in by who they are (never made a game / know games but not Godot / experienced
  / contributor). Getting Started has a design philosophy page and a "learning new features" page that teaches how to
  learn the engine. Contributor docs live separately, with an "engine architecture" section that goes from overview
  diagram → core types → object model → class tree → rendering internals → unit testing. The class reference is
  generated and versioned. First 2D and 3D game tutorials.
- Weak spots: Manual pages mix explanation, how-to and reference. Engine internals are thin compared with user docs.
- **Adopt:** audience tiles on the "Start here" page. A design philosophy chapter. The contributor path (overview →
  core types → object model → subsystems → testing) as the opening of the engine-builder track.

### Unity Manual, Script Reference and Unity Learn [S21]

- Works: a strict three-way split. The Manual explains concepts and workflows, the Script Reference documents the API,
  Unity Learn holds the tutorials. All are versioned. It has a glossary and best-practice guides. The Manual's order
  follows the editor (interface → assets → GameObjects → scenes → cameras → physics → input → UI → animation → audio →
  lighting → rendering → scripting → editor extensions → optimisation → building).
- Weak spots: many separate sites and products, so learners lose the thread between "how" and "why".
- **Adopt:** a generated, versioned reference for components, script API and editor commands (Strata can generate it
  from its registries and command schemas). A glossary. Use the Manual's feature order as a check on the game-maker
  track.

### Unreal Engine documentation [S22]

- Works (only partly fetched; the main page returned 403): the Get Started page splits by audience, including
  "transitioning from Unity" and "from Maya", with comparison pages (Blueprint against C++) and a terminology page.
  The top-level categories follow the creator's tasks (understanding the basics, working with content, building
  virtual worlds, designing visuals, programming, animating, testing and optimising, sharing and releasing).
- **Adopt:** "coming from Unity, Unreal or Godot" pages that map their terms to Strata's. Task-named categories in the
  game-maker track.

### The Diátaxis framework [S33]-[S36]

- Four kinds of documentation, each serving one need: tutorials (learning by doing, led), how-to guides (reaching a
  goal, for someone who already knows the basics), reference (describing the machinery, dry and complete, structured
  like the product), explanation (understanding, the "why", context, alternatives, opinion). Neighbouring kinds blur
  easily, and the worst failure is tutorials and how-tos collapsing into one.
- Tutorial rules: show the destination, give visible results early and often, say what the reader should see, point
  out what to notice, keep explanation to a minimum (link it), stay concrete, ignore alternatives, make it reliable
  (test it with real readers).
- Explanation rules: make connections, give context and history, discuss alternatives, admit opinion, keep it bounded
  (no steps, no reference tables).
- Reference rules: describe only, use standard patterns, mirror the product's structure, give examples.
- **Adopt:** label every page with one kind. A textbook is mostly *explanation* plus *tutorials*. The how-to guides
  and reference are needed for completeness, but must be kept separate. The engine already has a source for the
  reference (registries, command schemas, `DeveloperGuide.md`).

### Teaching Tech Together (Wilson) [S37] and the Google developer style guide [S38]

- Evidence-based teaching: give a simple mental model first, then the facts that attach to it. Address
  misconceptions directly. Working memory holds only a handful of items, so chunk. Experts are blind to what novices
  need, so test material on learners. Use worked examples, then faded examples (each with less help). Use Parsons
  problems (put given lines in order). Label subgoals. Write multiple-choice questions whose wrong answers each expose
  a known misconception. Pair words with images, but do not make the reader split attention between redundant ones.
- Sentence-level style: second person, active voice, conditions before instructions, sentence-case headings, numbered
  lists for steps, code font for code, descriptive link text, alt text, writing for a global audience.
- **Adopt:** both, as the basis of section 4.

### Others worth knowing

- Catto's GDC talks [S25]: a ready-made order for teaching rigid-body physics (sequential impulses → constraints →
  integration → GJK → dynamic BVH → continuous collision). The box3d author's own material, so it fits Strata.
- Algorithms for Modern Hardware [S26]: the best free treatment of caches, SIMD and measurement, with case studies.
  Link it from the performance chapter.
- Handmade Hero [S39] (the fetch redirected and was not followed): a whole game built from scratch with every line
  explained. Its lesson is that watching the reasoning matters as much as the result, and its warning is that 600+
  episodes is too long for most learners.

---

## 3. Recommended chapter templates

Every page carries the same frame, so a reader always knows where they are, plus a body that depends on its kind.
One page has one kind (Diátaxis). Each element below says what it is for.

### 3.0 The frame every page shares

Top strip (from Catlike Coding, Learn WebGPU, the Khronos tutorial):

- **Kind and track badges**: Concept / Internals / Tutorial / How-to / Reference; Game maker / Engine builder /
  Everyone; level (Beginner, Intermediate, Advanced). *For:* letting readers decide in two seconds whether this page is
  for them now.
- **You will learn**: 3-6 bullets, each one a capability ("explain why the loop runs physics in fixed steps"), not a
  topic. *For:* showing the destination and setting up the summary.
- **Before you start**: links to the pages this one depends on, and nothing else. *For:* the promise "nothing is
  assumed that the book has not taught", made checkable. A tool can check that every linked page comes earlier in
  every track that includes this one.
- **Verified against**: the Strata commit and date the page was last checked. *For:* honesty about drift. A page whose
  excerpts no longer match the source shows "stale" (see the excerpt contract below).
- **Time**: rough reading or doing time for tutorials.

Bottom strip:

- **Summary**: the "you will learn" bullets answered in one or two sentences each. *For:* retrieval and review.
- **Check yourself**: 3-5 quick questions (multiple choice with misconception distractors, or predict-the-output),
  answers hidden. *For:* formative assessment; the reader finds gaps before the next chapter builds on them.
- **Exercises**: graded (see section 4.7).
- **Where this lives in Strata**: the files, classes, commands and tests that implement the page's subject, linked to
  the source at the pinned commit. *For:* engine builders who want to go from understanding to code.
- **Further reading**: annotated links (one line each: what it adds and at what level). *For:* readers who want depth,
  without the page itself becoming a survey.
- **Next**: the next page in each track this page belongs to.

**Excerpt contract** (the answer to "real code excerpts" in a book about a moving codebase): every code excerpt is
pulled by a tool from the engine at the pinned commit, by file and symbol (or marked region), never pasted by hand.
The book's CI fails when an excerpt's source is gone or has changed, so a writer updates the page and its "Verified
against" line together. Sketch code (not from Strata) is marked as **Sketch** with a distinct frame and is compiled
by the book's own CI where possible. Screenshots of rendering features are made by the engine (editor automation or
the look-dev harness) from committed scenes and scripts, so they can be retaken when the look changes. A figure whose
scene or commit is stale shows that, just as a page does.

### 3.1 Concept chapter (Diátaxis: explanation; "the problem and the industry's answers")

For general knowledge: the game loop, transforms, PBR, shadows, ECS, asset pipelines. Built on GEA, GPP, Filament and
Ciechanowski.

1. **The problem** (a story or a picture). One concrete situation where the naive approach fails: "the ball falls
   through the floor on a slow laptop". *For:* motivation; a reason to care before any term.
2. **See it**: a figure or interactive demo that shows the effect before it is named. *For:* intuition first.
3. **Name it**: the key terms, each defined once in plain words (they enter the glossary). *For:* shared vocabulary.
4. **The idea**: the mental model in one paragraph and one diagram, then the details. *For:* something for the facts
   to attach to.
5. **The math** (when needed): intuition → small worked numbers → the formula with every symbol named → code →
   a check (limits, units). *For:* making the formula a tool, not a wall.
6. **Approaches the industry uses**: two to five ways to solve it, from the naive one up, each introduced by the flaw
   of the one before (the GPP and Gaffer progression). A comparison table at the end (cost, quality, complexity, who
   uses it). *For:* the trade-offs the brief asks for.
7. **What Strata chose and why**: a short bridge to the internals chapter. *For:* connecting the general to the
   particular without merging them.
8. **Common misconceptions and pitfalls**: what people get wrong, and the symptom each produces. *For:* debugging
   knowledge, and the target of the check-yourself distractors.
9. **Design note** (optional): a short essay on a wider question ("Should the engine own the loop?"). *For:* opinion
   and perspective, clearly separated (Crafting Interpreters' design notes, Diátaxis' explanation).
10. The shared bottom strip.

### 3.2 Engine-internals chapter (explanation + guided code reading; "how Strata does it")

For engine builders: Strata's application loop, the asset manager, the render scene, the script host. Built on
Crafting Interpreters, the Godot engine-architecture section and vkguide's architecture chapters.

1. **The job**: what this part of Strata is responsible for, and what it is explicitly not responsible for. *For:*
   boundaries before code.
2. **Where it sits**: a layer and data-flow diagram showing who calls it, what it calls, what thread it runs on and
   what it owns. *For:* the map before the territory.
3. **The contract**: the rules other code must follow (for example "writes to `TransformComponent` signal the change")
   and why each rule exists. Link to the rule in `AGENTS.md` or `DeveloperGuide.md`. *For:* turning the repo's rules
   into understood rules.
4. **A toy version** (optional, a Sketch of a few dozen lines): the simplest thing that works. *For:* a model small
   enough to hold in your head (the Crafting Interpreters two-pass idea).
5. **The real version, walked through**: annotated excerpts in the order data flows (one request through the
   system, from entry to effect). Each excerpt: file and symbol, what to notice, why it is like this. *For:* reading
   real engine code with a guide beside you.
6. **Why it differs from the toy**: each production concern the toy ignored (threading, budgets, failure, hot
   reload, tests) and the code that handles it. *For:* teaching the engineering, not just the algorithm.
7. **Alternatives Strata did not choose**: what other engines do, and what Strata would gain and lose. *For:*
   judgement, and context for future changes.
8. **How it is tested**: the test suites, what they check and how to run them. *For:* the repo's "everything ships
   with tests" culture, learned by example.
9. **Change it safely**: the extension points (registries, scene systems, settings sections), the checklist for a
   change in this area, and a link to the matching how-to or skill. *For:* moving the reader from reading to
   contributing.
10. **Trace it yourself**: a guided exercise using the debugger or a Tracy capture ("set a breakpoint in X, load the
    Showcase, step until Y"). *For:* active learning on the real code.
11. The shared bottom strip.

### 3.3 Step-by-step tutorial (Diátaxis: tutorial)

For both tracks: "Make your first game", "Write a script that opens a door", "Add a component", "Add a post effect".
Built on Diátaxis, Catlike Coding, Ray Tracing in One Weekend and the Rust book's project chapters.

1. **What you will make**: a screenshot or short clip of the finished result. *For:* the destination.
2. **Starting point**: the exact sample, template or commit to start from, and how to get it. *For:* reliability;
   every reader starts in the same state.
3. **Steps**: numbered sections, each a small goal ("Make the cube fall"). Inside: the action (exact clicks, commands
   or code), then **"You should see"** with a screenshot, then **"If you don't"** for the one or two likely failures.
   *For:* visible results early and often, and a way back when something goes wrong.
4. **Notice**: a one-line pointer to what changed that the reader would otherwise miss ("the inspector added a
   field"). *For:* attention, without explanation.
5. **Why, briefly**: at most two sentences, plus a link to the concept or internals chapter. *For:* keeping
   explanation out of the path (Diátaxis) while still connecting to it.
6. **Checkpoint**: at the end of each section, the full code or project state, downloadable. *For:* catching up and
   comparing.
7. **What you made / What you learned**: the result again, and the skills named. *For:* ending on success.
8. **Make it yours**: 2-4 open extensions with hints. *For:* the bridge from following to doing alone.
9. **Tested**: tutorials are executed by CI. Game-maker tutorials as editor command scripts (Strata already has
   `Editor/<Sample>Commands.json.in`), engine tutorials as patches applied to the pinned commit and built. *For:*
   Diátaxis' "it must work every time", enforced by a machine.

### 3.4 How-to guide (Diátaxis: how-to)

Short and goal-titled ("How to make a trigger volume", "How to profile a frame"). Assumes the basics. Prerequisites →
numbered steps → result → variations → related reference. No teaching. *For:* readers who already learned and now
work. The book needs these for completeness, and many can be distilled from `DeveloperGuide.md` and the skills.

### 3.5 Reference page (Diátaxis: reference)

For components, script API, editor commands, settings sections, shader inputs, command-line options, file formats.

- Same layout for every entry of a kind (name, summary line, fields or parameters with type, default, range and units,
  behaviour, errors, an example, related links). *For:* readers find things where they expect them.
- Structured like the engine (one page per component, per command group, per settings section). *For:* the map
  between docs and code stays obvious.
- **Generated** where the engine has the data (component registry, command JSON Schemas, settings registry, script SDK
  headers), with hand-written notes merged in. A check fails when something registered has no reference entry. Strata's
  feature test already does the same for coverage. *For:* completeness that stays true over time.
- Describe only. Link to explanation and tutorials instead of teaching.

---

## 4. Writing style guide for readers who know nothing yet

### 4.1 Voice

- Talk to the reader as "you". Use "we" only for something reader and book do together in a tutorial ("we add a
  field"). Name the engine as the actor of its own choices: "Strata stores…", not "we store…".
- Warm, direct, plain. A patient colleague explaining at a whiteboard (Nystrom, Fiedler). Humour is allowed in asides
  and captions, sparingly, and never at the reader's expense.
- Never write "simply", "just", "obviously", "easy", "trivial", "of course". If it were obvious the reader would not
  be here. These words tell a struggling reader that they are the problem.
- Be honest about uncertainty and about Strata: "this is experimental", "this is a known weakness", "nobody has
  measured this". Bevy's candour earns trust.
- Present tense, active voice. Conditions before instructions ("To see the cascades, open the Lighting view").

### 4.2 Sentences and paragraphs

- Average 15-20 words, rarely over 30. One idea per sentence and per paragraph. A long sentence is fine when it is a
  list in prose. Split it when it holds two claims.
- Paragraphs of 2-5 sentences. Lead with the point, then support it.
- Prefer concrete nouns and verbs: "the renderer skips meshes that are not loaded yet" over "unloaded assets are
  handled gracefully".
- Write for a global audience: avoid idioms, cultural references the reader needs to know, and wordplay that carries
  meaning.
- Headings in sentence case. Headings say what the section establishes ("Fixed steps make physics repeatable"), or
  name the task in tutorials ("Make the cube fall").

### 4.3 Introducing a term

1. Show the thing first (a figure, an example, a symptom).
2. Give the term in **bold** at the moment it is defined, with a one-sentence plain definition.
3. If a precise or formal definition is needed, give it next, after the plain one.
4. Add it to the glossary, and link later uses back to the definition (automatically, on the first use per page).
5. One name per concept across the whole book, and the same name the code uses (`AssetHandle`, "scene system",
   "render scene"). When the industry uses other names, list them once ("Unity calls this a GameObject, Unreal an
   Actor").
6. Spell out acronyms on first use per chapter (not per book: readers jump around).
7. Never introduce more than three or four new terms in one section. If a section needs more, split it.

### 4.4 Analogies without lying

- Use an analogy to give the shape of an idea, then **state where it stops being true**, in the next sentence or a
  "Where the analogy breaks" note. Example pattern: "a handle is like a coat-check ticket … Unlike a ticket, a handle
  stays valid after the coat is gone, so code must ask whether the asset is loaded."
- Prefer analogies whose failure is harmless. Drop an analogy that leads readers to a wrong prediction about the
  engine.
- Don't stack analogies. One per concept, reused consistently.
- Prefer a real small example over an analogy when one exists (two numbers, a 3×3 grid, one frame on a timeline).

### 4.5 Presenting math

The order, every time (from Ciechanowski, the 3D Math Primer and Filament):

1. **Intuition**: what the quantity means and a picture of it (an arrow, a lobe, a curve). Interactive when it truly
   helps.
2. **A worked example with small numbers**: compute it by hand once ((1, 0) · (0.7, 0.7) = 0.7).
3. **The formula**: typeset, every symbol named underneath in words and units, and conventions stated (which space,
   which handedness, row or column vectors). A per-part notation table (Filament) and a book-wide conventions page
   (3D Math Primer).
4. **The code**: the Strata (or Sketch) code that computes it, with the formula's symbols mapped to the code's
   variable names.
5. **A check**: what happens at the limits (angle 0, roughness 1, distance → 0), the units, a sanity test. Where it
   applies, the engine's own validation (white furnace, debug views).

Further rules:

- Derive only what the reader will use. Put long derivations in an expandable "Where this comes from" box.
- Never put a formula in a figure caption without the text explaining it.
- Use the engine's conventions in all math: reversed-Z depth, D3D NDC (+Y up, top-left origin), counter-clockwise
  front faces. Show the alternative conventions once, in the conventions page, with a translation table.
- Teach the math just in time, inside the chapter that needs it (Scratchapixel). The math appendix is for looking
  things up, and every chapter links its specific entries.

### 4.6 Presenting code

- **What to show:** the smallest excerpt that carries the idea, usually 5-25 lines. Show the shape first (signature,
  struct) and the body after. Never show a page of code at once. Split it, and explain between the pieces.
- **Label every excerpt:** file path and symbol, the commit (implicit through "Verified against"), and whether it is
  Strata, Sketch, or Wrong-on-purpose (a visible marker, as the Rust book does with code that fails).
- **Elide honestly:** replace omitted lines with a comment that says what was removed (`// … error handling, see
  below`). Never edit real code silently to make it prettier. If a simplification is needed, it is a Sketch.
- **Annotate:** numbered callouts in the margin or after the block, at most 5 per excerpt. Each callout says why, not
  what. Highlight changed lines when code grows (Ray Tracing in One Weekend).
- **Teach C++ as it appears:** when an excerpt uses a C++ feature not yet taught (`std::optional`, a lambda capture,
  `constexpr`, move), add a short Q&A aside ("What is `std::optional`?") with a two-line answer and a link to the
  C++ appendix and learncpp (Catlike Coding's asides).
- **Show output:** the log line, the test result, the screenshot the code produces.
- **Follow the engine's code style in Sketch code too** (Hazel naming, tabs, Allman braces), so readers learn one
  style.
- **Shaders:** show the Slang source with the binding registers, and say on the CPU side where each binding is filled.

### 4.7 Exercises and solutions

Use several kinds, graded with a marker (one to three dots, for example), and say which track each exercise is for.

- **Check yourself** (in every chapter): multiple choice whose wrong answers each match a real misconception. The
  answer explains why each option is right or wrong.
- **Predict, then run**: "What will happen if the max step count is 1 and a frame takes 100 ms? Try it in the
  ThirdPerson sample." The answer gives the reasoning and what the reader should have seen.
- **Modify**: change a parameter or line and observe (The Book of Shaders).
- **Parsons problems**: put given lines of a loop or shader in order (isolates understanding from typing).
- **Faded examples**: three similar tasks with less help each time (for example registering three components).
- **Trace the code**: find where something happens in the real codebase, with a debugger or search. The solution
  names the file and function and shows the path.
- **Extend**: add a small feature (a component field, a debug view, a script behaviour). The solution is a patch
  against the pinned commit that CI builds and tests.
- **Design**: open questions with no single answer ("How would you stream a world twice as large?"). The solution is
  a discussion of good answers and their trade-offs, not one answer.

Rules for solutions: hidden by default (collapsible), always present, worked through and not just stated, and in the
book itself (or its companion repository for code), never "left to the reader". Code solutions are tested by CI like
tutorials.

### 4.8 Saying what is simplified

- Mark every simplification in a **Simplified** box that says what is left out, why it is safe for now, and where the
  full story is. Then go back and resolve it in the later chapter, linking back ("Earlier we said X. The full
  picture…").
- Never state something false to make it simpler. Say "for now, assume …" or "in most cases …", not a flat untrue
  rule. Bound claims in time and scope ("in Strata at 822a7a46", "on desktop GPUs").
- Distinguish three things in wording: how it works everywhere ("GPUs …"), how most engines do it ("engines usually
  …"), and what Strata does ("Strata …").
- When Strata itself is simplified compared to the industry (for example no networking, experimental GI), say so in
  the chapter that covers the topic, not only in a roadmap.

### 4.9 Figures and screenshots

- One figure per idea, with a caption that says what to notice, not just what it is ("the far cascade covers four
  times the area at the same resolution, so its texels are larger").
- Use the same visual language throughout: one colour for the camera, one for lights, one for the GPU, consistent
  arrows for data flow, colour-blind-safe palettes, vector (SVG) diagrams, alt text for every image.
- Rendering features: a feature-off/feature-on pair, a debug view, and a parameter sweep (Catlike's frame-debugger
  pairs, Filament's sweeps), all rendered by Strata from committed scenes.
- Tutorials: a screenshot after every step that changes what is on screen.
- Timing and threading concepts: a timeline figure (fixing Gaffer's one weakness).

### 4.10 Accessibility and the web

- Every interactive figure has a static fallback image and a text description.
- Code blocks can be copied, and are not images.
- Pages work without JavaScript except the interactive parts.
- Headings are real headings, so screen readers and the table of contents can navigate.

---

## 5. Reading orders: two audiences and complete beginners in one book

### 5.1 Principles

1. **One home per concept.** Each concept is explained in exactly one place. Other pages link there (with a
   one-sentence reminder) instead of explaining it again. This is what stops two tracks from turning into two books.
2. **Two depths per subsystem, on separate pages:** a *use it* page in the game-maker track (what it does for your
   game, how to drive it from the editor and scripts) and a *how it works* page in the engine-builder track (internals,
   template 3.2). Both link to one shared *concept* page (template 3.1) for the general knowledge. For example physics:
   "Making things move with physics" (game maker), "Collision and rigid bodies" (concept), "Inside Strata's physics
   system" (internals).
3. **Tracks are paths through one book, not separate books.** Every page has track badges. Track pages list their
   chapters in order, and the "Before you start" links of every page are checked against each track's order.
4. **Prerequisites are a graph, not just chapter order.** Publish the graph (a "map" page). Readers can enter
   anywhere and walk back.
5. **Beginners are served by an on-ramp and just-in-time foundations**, not by a prerequisite wall. The C++, math and
   graphics foundations are their own part, but each chapter links into exactly the foundation sections it needs.

### 5.2 Proposed parts

- **Part 0 — Start here.** What an engine is and what you can do with Strata (one page with the frame map). Three
  doors in the style of Godot's tiles: "I want to make a game", "I want to understand or work on the engine", "I have
  never programmed much / never made a game". Installing or building Strata. A 30-minute first game in the editor
  (a tutorial with a visible result in the first 5 minutes). How to read this book (page kinds, badges, excerpt
  labels, conventions). "Coming from Unity, Unreal or Godot" mapping pages.
- **Part I — Foundations.** C++ for engines (only what Strata uses, taught through Strata examples, with learncpp
  for the rest), tools of the trade (compilers, CMake, git, the debugger), how computers run code fast (caches,
  threads), and the math (vectors to quaternions, conventions, interpolation, geometry tests, colour, sampling,
  probability). Each chapter is a standalone unit that later chapters link to.
- **Part II — Making games with Strata** (the game-maker track's core). The editor, projects and scenes, entities and
  components, prefabs, materials and lighting from the artist's side, cameras, scripting in C++ (from "hello" to a
  full gameplay script), input actions, physics for gameplay, audio, game UI, animation for gameplay, saves, worlds for
  game makers, testing your game with command scripts, exporting and shipping. A little game design craft (core loop,
  prototyping, scope, feel, playtesting). Project chapters interleaved: a first game, a mid-size game, a capstone,
  based on the samples (Tetris, PhysicsPlayground, ThirdPerson).
- **Part III — The engine core.** The architecture and layers, application and modules, the frame loop and time,
  platform and windowing, input internals, memory, the job system and threading, logging, asserts and errors,
  settings and project files.
- **Part IV — Data: assets, scenes and worlds.** The asset pipeline, importers, residency and streaming, the scene and
  ECS, transforms and caches, reflection and serialization, scene documents, prefabs, sub-scenes and world partition.
- **Part V — Rendering.** The GPU, Vulkan and NVRHI, shaders in Slang, the render scene and draw path, batching and
  GPU-driven rendering, materials and PBR, textures and mip streaming, lights and exposure, shadows, AO, reflections,
  sky, atmosphere and fog, global illumination, TAA and anti-aliasing, post-processing and the filmic look, text and
  overlays, quality settings, GPU timing and a full frame analysis.
- **Part VI — Motion.** Animation (skeletons to root motion), collision and physics (shapes to character
  controllers), interpolation and fixed rate across both.
- **Part VII — Sound, UI and gameplay internals.** The audio engine, the game UI system, the script ABI, host
  functions, hot reload and crash containment.
- **Part VIII — Tools.** The editor's architecture, commands and undo, no silent data loss, inspectors and
  reflection, the viewport and placement, the automation API and MCP, making games with AI agents.
- **Part IX — Quality and shipping.** Debugging and profiling, testing an engine (all suite kinds), CI, performance
  budgets, packaging and releases, contributing to Strata (review checklist, commit hygiene, the rules and why).
- **Appendices.** Math reference, C++ reference (Q&A asides gathered), glossary, conventions and notation, networking
  for games (general; Strata has none), reference (generated: components, script API, commands, settings, command-line
  options), further reading, index of engine identifiers.

### 5.3 Tracks

- **Game maker** (no engine internals needed): Part 0 → the beginner on-ramp if needed → Part II in order → the
  concept chapters Part II links to (read when curious) → selected how-tos and reference. Part II must never require
  reading an internals chapter.
- **Engine builder:** Part 0 → Part I (skip what you know; each chapter has a "test out" quiz) → Part II chapters 1-4
  (enough to use the editor, since you must use what you build) → Parts III-IX in order, with the concept chapters
  inline. Capstone contributions as tutorials: add a component, add a host function, add an editor command, add a post
  effect, each following the repository's skills and checklists.
- **Complete beginner on-ramp:** "Programming you need" (a short C++ start, linking learncpp), "The math you need for
  your first game" (vectors and transforms only), "What is in a frame", then into the game-maker track. Engine-builder
  beginners continue into Part I afterwards. The on-ramp is a sequence of existing pages from Part I plus three or four
  bridging pages, not a separate copy.
- **Specialist paths** (published as lists): rendering only, physics and animation, tools and automation, "I want to
  ship a game this month".

### 5.4 Keeping it complete

- A coverage table (like Strata's feature test): every engine feature from the inventory maps to its use-it,
  concept, internals and reference pages, or is marked as not applicable. The book's CI checks that every registered
  component, command, settings section and script API name has a reference entry, and the inventory's features have
  a home.
- The checklist in section 1 is the outline audit. Every line maps to a page or is listed as deliberately out of
  scope.

---

## 6. Sources

- [S1] Game Engine Architecture, 4th ed., table of contents — https://www.gameenginebook.com/toc.html
- [S2] Real-Time Rendering, 4th ed., companion site and contents — https://www.realtimerendering.com/
- [S3] Physically Based Rendering, 4th ed., contents — https://pbr-book.org/4ed/contents
- [S4] Foundations of Game Engine Development (Lengyel), official site — https://foundationsofgameenginedev.com/
- [S5] 3D Math Primer for Graphics and Game Development, online edition — https://gamemath.com/book/
- [S6] Real-Time Collision Detection (Ericson), table of contents — https://realtimecollisiondetection.net/books/rtcd/toc/
- [S7] Game Programming Patterns, contents — https://gameprogrammingpatterns.com/contents.html ; Game Loop chapter —
  https://gameprogrammingpatterns.com/game-loop.html
- [S8] LearnOpenGL — https://learnopengl.com/ ; Hello Triangle — https://learnopengl.com/Getting-started/Hello-Triangle
- [S9] Vulkan Tutorial, Overview — https://vulkan-tutorial.com/Overview
- [S10] vkguide — https://vkguide.dev/
- [S11] Khronos Vulkan Tutorial — https://docs.vulkan.org/tutorial/latest/00_Introduction.html
- [S12] Scratchapixel — https://www.scratchapixel.com/index.html
- [S13] Crafting Interpreters, contents — https://craftinginterpreters.com/contents.html ; Scanning chapter —
  https://craftinginterpreters.com/scanning.html
- [S14] Catlike Coding tutorials — https://catlikecoding.com/unity/tutorials/ ; Custom SRP, Custom Render Pipeline —
  https://catlikecoding.com/unity/tutorials/custom-srp/custom-render-pipeline/
- [S15] The Book of Shaders — https://thebookofshaders.com/ ; Shaping functions — https://thebookofshaders.com/05/
- [S16] Gaffer on Games, Fix Your Timestep — https://gafferongames.com/post/fix_your_timestep/
- [S17] Gaffer on Games, What Every Programmer Needs To Know About Game Networking —
  https://gafferongames.com/post/what_every_programmer_needs_to_know_about_game_networking/
- [S18] Bevy quick start — https://bevy.org/learn/quick-start/introduction/
- [S19] Godot documentation — https://docs.godotengine.org/en/stable/index.html ; Getting started introduction —
  https://docs.godotengine.org/en/stable/getting_started/introduction/index.html
- [S20] Godot engine architecture (contributors) — https://docs.godotengine.org/en/stable/engine_details/architecture/index.html
- [S21] Unity Manual — https://docs.unity.com/en-us/engine/current/manual
- [S22] Unreal Engine documentation, Get Started — https://dev.epicgames.com/documentation/en-us/unreal-engine/get-started
  ; documentation home (fetch returned 403; categories confirmed only through search results) —
  https://dev.epicgames.com/documentation/en-us/unreal-engine
- [S23] Physically Based Rendering in Filament — https://google.github.io/filament/main/filament.html
- [S24] Gabriel Gambetta, Fast-Paced Multiplayer — https://www.gabrielgambetta.com/client-server-game-architecture.html
- [S25] Erin Catto (Box2D/box3d), publications — https://box2d.org/publications/
- [S26] Algorithms for Modern Hardware — https://en.algorithmica.org/hpc/
- [S27] Bartosz Ciechanowski, archives — https://ciechanow.ski/archives/ ; Lights and Shadows —
  https://ciechanow.ski/lights-and-shadows/
- [S28] Red Blob Games — https://www.redblobgames.com/
- [S29] Ray Tracing in One Weekend — https://raytracing.github.io/books/RayTracingInOneWeekend.html
- [S30] Learn WebGPU for C++ — https://eliemichel.github.io/LearnWebGPU/
- [S31] The Rust Programming Language — https://doc.rust-lang.org/book/ (only the front matter was fetched; the
  structure described is the book's well-known one and should be checked before it is relied on)
- [S32] learncpp.com — https://www.learncpp.com/
- [S33] Diátaxis — https://diataxis.fr/
- [S34] Diátaxis, the map — https://diataxis.fr/map/
- [S35] Diátaxis, tutorials — https://diataxis.fr/tutorials/
- [S36] Diátaxis, explanation — https://diataxis.fr/explanation/ ; reference — https://diataxis.fr/reference/
- [S37] Teaching Tech Together (Greg Wilson) — https://teachtogether.tech/en/index.html
- [S38] Google developer documentation style guide, highlights — https://developers.google.com/style/highlights
- [S39] Handmade Hero — https://handmadehero.org/ (redirects to https://mollyrocket.com/handmade; not fetched)
