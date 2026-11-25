# Outline 2: Scenes and the ECS, The GPU and the renderer's core, Assets, Drawing a scene

Columns as in [outline-1.md](outline-1.md).

## Part 4 — Scenes and the ECS (`world`)

Tracks: E

Needs of the part: `start/first-game`, `basics/computer`, `basics/data-structures`, `basics/cpp-classes`, `basics/cpp-generic`, `basics/cpp-modern`, `basics/data-formats`, `basics/math-rotations`, `basics/math-interpolation`, `basics/threads`, `core/first-change`, `core/conventions`, `core/frame-loop`, `core/time`, `core/engine-modules`, `core/layers-registries`, `core/jobs`, `core/files`, `core/math`

| id | Title | Kind | Size | Tracks | Needs | From |
| --- | --- | --- | --- | --- | --- | --- |
| `world/what-a-world-is` | What a game world is made of | C | M | E | `basics/computer`, `basics/cpp-classes`, `basics/data-structures`, `core/frame-loop` | scene-ecs; object models compared (inheritance, components, ECS) |
| `world/ecs` | Entities and components, with EnTT inside | I | L | E | `world/what-a-world-is`, `basics/cpp-generic`, `core/conventions` | scene-ecs; a toy sparse set first; home of handles instead of pointers and of UUIDs (`assets/handles-meta` covers asset handles only) |
| `world/scene-graph` | The scene graph: hierarchy, transforms and the transform contract | I | XL | E | `world/ecs`, `basics/math-rotations`, `core/math`, `core/jobs` | scene-ecs; home of change signals; + the primary-camera lookup (the camera itself is `gpu/coordinates`') |
| `world/systems` | Systems, phases and fixed steps | I | L | E | `world/ecs`, `basics/threads`, `core/time`, `core/engine-modules`, `core/layers-registries` | scene-ecs; `Scene` update code; the code of the fixed step, the accumulator and time dilation (the concept is `core/time`'s) |
| `world/interpolation` | Drawing between fixed steps | I | L | E | `world/scene-graph`, `world/systems`, `basics/math-interpolation` | scene-ecs "Interpolating fixed steps"; physics "Interpolating fixed steps"; M→L; home of interpolation (`core/time` names it in one paragraph); + what it does not do yet (`Docs/Roadmap.md`, "Interpolation, the rest") |
| `world/reflection` | Reflection: one registration, many uses | I | XL | E | `world/ecs`, `basics/cpp-modern`, `basics/data-formats`, `core/layers-registries` | scene-ecs; `ComponentRegistry`'s builder (registries that open, accept and freeze are `core/layers-registries`') |
| `world/serialization` | Scene documents: text, streams and the cooked form | I | L | E | `world/scene-graph`, `world/reflection`, `core/files` | scene-ecs §1.9 (the DOM serializer, the three-pass read, leniency, unknown components, the parallel streaming writer and its deterministic bytes, the event-parser reader, sinks, the cooked form STSC and its validation); retitled, the formats only; takes as given that an asset is named by an `AssetHandle` and read by a loader, and links forward to `assets/loading` |
| `world/prefabs` | Prefabs: the data model | I | L | E | `world/serialization` | scene-ecs "Prefabs"; the data model, overrides and propagation (`EntityPrototype`, instantiation, `PrefabInstances`, `PrefabOverrides`); prefabs and models as entity templates, the asset side taken as given; keeping them exact while editing is `editor/prefab-instances`' |
| `world/sub-scenes` | Loading scenes: whole, additive and in slices | I | L | E | `world/prefabs`, `world/systems` | scene-ecs §1.8, §1.11, `SceneAsset` (§1.10); worlds-runtime "Sub-scenes and the frame budget"; `SceneLoader` and its states, `PrepareSystems` and `PrepareLoadedScene`, prepared states, the hand-over, `RequestSceneLoad`, `ReleaseInBackground`, `SceneWorkBudget`; retitled, M→L; home of loading scenes (a shipped game's scene switches are `worlds/runtime`', the editor's `editor/play-mode`'s); residency and pins taken as given (`assets/residency` follows) |
| `world/projects-settings` | Projects and settings | I | L | E | `world/systems`, `world/reflection`, `core/files` | scene-ecs; settings sections, their versions and validation, `IProjectSettings`, the hand-over to scenes (timing, collision layers); the manifest and the game's identity are `worlds/game-identity`'s; `make/project-files` teaches the project folder to game makers |
| `world/tutorial-component` | Tutorial: adding a component and a system | T | L | E | `core/first-change`, `start/first-game`, `world/systems`, `world/serialization` | scene-ecs; skill `strata-add-component`; creates the WindZone component, track E's running example that the capstone completes; at this stage the WindZone has no asset property (the skill's example has a `Sound` property, which the feature test would need a resolving asset with its `.meta` for, and assets come in a later part); a later stage (`capstone/build`) may add one; ends with a serialization round trip and the feature test's minimum (`engineering/feature-test` has the rest); moved to the end of the part (the skill needs serialization) |

## Part 5 — The GPU and the renderer's core (`gpu`)

Tracks: E

Needs of the part: `basics/numbers`, `basics/cpp-classes`, `basics/build`, `basics/bytes`, `basics/math-projection`, `basics/color`, `basics/signals`, `basics/threads`, `core/first-change`, `core/frame-loop`, `core/layers-registries`, `core/platform`, `core/profiling`, `core/debugging`, `core/math`, `world/scene-graph`, `world/tutorial-component`

| id | Title | Kind | Size | Tracks | Needs | From |
| --- | --- | --- | --- | --- | --- | --- |
| `gpu/how-a-gpu-frame-works` | How a GPU works and draws a frame | C | L | E | `basics/threads`, `basics/math-projection`, `basics/color`, `basics/signals`, `core/frame-loop` | render-core; retitled; + the hardware: waves, occupancy, bandwidth, branches (curricula 1.9.1 [gap]); + the pipeline at a glance, textures, sampling and filtering, buffers, command submission and frames in flight; rasterization takes pixels as samples (aliasing in general is `basics/signals`') |
| `gpu/vulkan-nvrhi` | Vulkan, NVRHI, the graphics device and the Renderer's services | I | XL | E | `basics/cpp-classes`, `basics/numbers`, `gpu/how-a-gpu-frame-works`, `core/layers-registries`, `core/platform` | render-core; the RHI layer (curricula gap); retitled; + render-core 1.2-1.3 (`GraphicsModule`, back-buffer capture, the `Renderer` hub, samplers, fallback textures) |
| `gpu/shaders` | Shaders: Slang, the build and the dialect | I | L | E | `gpu/vulkan-nvrhi`, `basics/build`, `core/first-change` | render-core; writing and registering a shader, the dialect and its checks (the CMake custom commands and the generated registry are `engineering/generated-code`'s) |
| `gpu/compute` | Compute shaders: dispatches, thread groups, shared memory and atomics | C | M | E | `gpu/shaders` | new; render-core concepts 9, 13; render-scene concept 14 (prefix allocation); toy: a histogram and a prefix sum; home of the compute model and of UAV barriers, which draw, light, image and indirect use |
| `gpu/coordinates` | Coordinate systems and the camera: clip space, reversed depth, UVs | C | M | E | `basics/math-projection`, `basics/numbers`, `core/math`, `world/scene-graph`, `gpu/how-a-gpu-frame-works` | render-core; retitled; + `CameraComponent` (scene-ecs §1.2: projection, `GetProjection`); home of the camera and of Strata's depth conventions and precision (the math is `basics/math-projection`'s, the code `core/math`'s, the depth-of-field fields `image/depth-of-field`'s); states the counter-clockwise convention only (mirroring and camera-relative space are `draw/mirrors-camera-relative`'s) |
| `gpu/first-triangle` | Tutorial: your first triangle in Strata | T | L | E | `core/first-change`, `gpu/shaders`, `gpu/coordinates` | render-core; home of writing a GPU test (the shared `GPUContext`, the error count, pixel readback); moved after `gpu/coordinates` (it uses shaders and clip space) |
| `gpu/debugging` | Debugging the GPU: validation, frame captures, the error count and debug views | H | M | E | `gpu/first-triangle`, `core/debugging` | new; render-core concept 4 and hands-on 12 (a frame in RenderDoc or Nsight); the validation layer, debug names and markers, `GetNewErrorCount`, the editor's debug views (`debugView`) and the page that reads each; curricula 1.9.1 [gap] |
| `gpu/resources-lifetimes` | Resources and lifetimes | I | L | E | `gpu/vulkan-nvrhi`, `gpu/compute`, `gpu/first-triangle` | render-core; deferred release; states and barriers in NVRHI (the compute model is `gpu/compute`'s) |
| `gpu/upload-queue` | Staging and the upload queue | I | L | E | `gpu/resources-lifetimes` | render-core; the mechanism: `PlanStep`, `StagingPool`, the transfer queue, `PrepareBackBuffer` (what assets queue and when is `assets/uploads`') |
| `gpu/binding` | Pipelines and binding: layouts, registers and bindless | I | L | E | `gpu/shaders`, `gpu/resources-lifetimes` | render-core; retitled; + pipeline state objects and the `PipelineKey` cache (render-core 1.6, concept 18; render-scene 1.4) |
| `gpu/geometry-pool` | Meshes on the GPU and the geometry pool | I | M | E | `gpu/upload-queue`, `gpu/binding` | render-core; home of the geometry pool (`draw/batching` links) |
| `gpu/frame-tour` | A frame of the scene renderer, pass by pass | I | XL | E | `gpu/coordinates`, `gpu/binding`, `gpu/geometry-pool` | render-core; the map every rendering page links back to; the renderer's half of the frame map; home of forward, deferred and visibility buffers, the depth prepass, `EQUAL` and invariant positions, and of the rule that a feature turned off is invisible bit for bit and costs nothing · W8r (the list of passes and the statistics they report) |
| `gpu/readback-timing` | Readback and GPU timing | I | L | E | `gpu/frame-tour`, `core/profiling` | render-core; home of GPU timestamps and stages (`core/profiling` shows them); the one-pixel readback that picking uses |
| `gpu/debug-drawing` | Overlays, debug drawing and gizmos | I | L | E | `gpu/frame-tour`, `world/tutorial-component` | render-core; home of overlay passes (`SceneOverlayRegistry`); its exercise gives WindZone a gizmo |
| `gpu/text` | Text: fonts, shaping and signed distance fields | I | L | E | `gpu/debug-drawing`, `basics/bytes` | render-core; gameui "Text in the UI" (the rendering half); home of fonts, `ShapeText` layout, the atlas and signed distance fields, and of font validation (`FontValidation`; untrusted input in general is `assets/robustness`') |

## Part 6 — Assets (`assets`)

Tracks: E

Needs of the part: `basics/numbers`, `basics/trees-graphs`, `basics/data-formats`, `basics/color`, `basics/signals`, `core/layers-registries`, `core/jobs`, `core/files`, `world/ecs`, `world/reflection`, `world/serialization`, `world/prefabs`, `world/tutorial-component`, `gpu/how-a-gpu-frame-works`, `gpu/resources-lifetimes`, `gpu/upload-queue`, `gpu/geometry-pool`

| id | Title | Kind | Size | Tracks | Needs | From |
| --- | --- | --- | --- | --- | --- | --- |
| `assets/what-is-an-asset` | What an asset is | C | M | E | `basics/data-formats`, `core/layers-registries`, `world/ecs` | assets; sources and cooked forms, the editor's side and the game's side, the pipeline at a glance (registries and seams) |
| `assets/handles-meta` | Handles, `.meta` files and sub-assets | I | L | E | `core/files`, `assets/what-is-an-asset` | assets; asset handles only (handles and UUIDs in general are `world/ecs`') |
| `assets/importing` | Importing: from source files to engine data | I | XL | E | `assets/handles-meta`, `world/reflection`, `core/jobs`, `core/files` | assets; import records, cache validity, dependencies, settings as properties, background imports, cancellation, hot reload of assets |
| `assets/textures` | Textures for the GPU: mips, color spaces, block compression | C | M | E | `basics/color`, `basics/signals`, `gpu/how-a-gpu-frame-works` | assets ch. 4 (the general problem and the formats); L→M |
| `assets/texture-cooking` | Cooking textures: Strata's importer, mips and BC7 encoder | I | L | E | `assets/importing`, `assets/textures`, `basics/numbers` | assets §1.8 (the texture importer, defaults from name tokens, `ChooseFormat`, the Mitchell cooker, `BC7Encoder.cpp`, the `HDRSun` setting, STTX v2, `GetMipByteSize`, the BC decode fallback), excerpts 12-15, rules 4, 14, 15; new by split from `assets/textures` (the importer, the cooker and the encoder are internals); what `HDRSun` does is `light/sky`'s |
| `assets/models-gltf` | Models and the glTF importer | I | L | E | `assets/texture-cooking`, `gpu/geometry-pool`, `world/prefabs` | assets |
| `assets/loading` | Loading without stalling | I | XL | E | `assets/handles-meta`, `core/jobs` | assets |
| `assets/residency` | Residency, eviction and pins | I | XL | E | `assets/loading`, `gpu/resources-lifetimes`, `basics/trees-graphs` | assets; home of residency, pins and eviction; room before arrival waits for the frames in flight |
| `assets/references` | References, closures, prefetch and loading screens | I | L | E | `assets/residency`, `world/serialization` | assets; home of load progress and prefetch (scene switches are `worlds/runtime`'s) |
| `assets/uploads` | Budgeted uploads | I | L | E | `assets/residency`, `assets/texture-cooking`, `gpu/upload-queue` | assets "Budgeted uploads and staging": what is queued and when (steps of `c_AssetUploadStepBytes`, the first step of a frame, `AssetFinalizeContext` and `AssetFinalizeResult`, `Texture::UploadLevels`, one batch per `Update`); the mechanism is `gpu/upload-queue`'s |
| `assets/packs-export` | Asset packs, export and patches | I | L | E | `assets/references` | assets; the pack: format, planning, pruning, `AlwaysInclude`, patches, cooked documents and when the export cooks them (the export as a whole is `worlds/export`'s) |
| `assets/robustness` | Corruption, crash safety and cancellation | C | L | E | `assets/importing`, `assets/packs-export` | assets; I→C; home of untrusted input (validate before use, checksums, bounded sizes) and of write-ahead ordering; corruption sweeps and fuzzing are `engineering/test-program`'s |
| `assets/extending` | Tutorial: adding an asset type | T | L | E | `assets/uploads`, `assets/robustness`, `world/tutorial-component` | assets "Extending the pipeline" |

## Part 7 — Drawing a scene (`draw`)

Tracks: E

Needs of the part: `basics/numbers`, `basics/math-geometry`, `core/jobs`, `core/math`, `world/scene-graph`, `world/interpolation`, `world/sub-scenes`, `gpu/compute`, `gpu/coordinates`, `gpu/upload-queue`, `gpu/binding`, `gpu/geometry-pool`, `gpu/frame-tour`, `gpu/readback-timing`, `assets/texture-cooking`, `assets/residency`, `assets/uploads`

| id | Title | Kind | Size | Tracks | Needs | From |
| --- | --- | --- | --- | --- | --- | --- |
| `draw/entities-to-draws` | From entities to draw calls | C | M | E | `gpu/frame-tour`, `world/scene-graph` | render-scene; the CPU path and the GPU-driven path at a glance |
| `draw/render-scene` | The render scene: persistent proxies | I | L | E | `world/interpolation`, `world/sub-scenes`, `core/jobs` | render-scene; home of the render scene's records and change logs, the lights' records included (what a light record holds is `light/lights`') |
| `draw/bounds-culling` | Bounding volumes, frustums and the spatial index | I | L | E | `draw/render-scene`, `basics/math-geometry`, `core/math` | render-scene; the CPU path, taught first; home of frustum and box tests (plane extraction, the positive vertex, `AABB::Transformed`) and of the screen fraction (`GetScreenFraction`, a section "How big does it look?"); sun shadow casters are `light/sun-shadows-1`'s |
| `draw/asset-requests` | Asking for assets at draw time | I | M | E | `draw/bounds-culling`, `assets/residency` | render-scene; request priorities, prefetch, the resolve cache, fallbacks and the streaming view; what renderers publish for `draw/mip-streaming` |
| `draw/batching` | Batching and instancing | I | L | E | `draw/asset-requests`, `gpu/geometry-pool`, `gpu/binding` | render-scene; sort keys and radix sort; the transparent pass's back-to-front order (blending is `light/clearcoat-transmission`'s) |
| `draw/lod` | Levels of detail | I | M | E | `draw/batching` | render-scene; the lod view |
| `draw/mirrors-camera-relative` | Mirrors, normals and camera-relative positions | I | M | E | `draw/batching`, `basics/numbers`, `gpu/coordinates` | render-scene; home of mirrored transforms and of camera-relative rendering (float precision is `basics/numbers`', the 20 km limit `worlds/why-streaming`'s) |
| `draw/render-scene-gpu` | The render scene's GPU copy | I | M | E | `draw/batching`, `gpu/upload-queue` | render-scene "RenderSceneGPU"; the change logs it follows (`RecordInstanceChanges`, `RecordProxyChange`) |
| `draw/gpu-driven` | GPU-driven culling and indirect drawing | I | XL | E | `draw/lod`, `draw/mirrors-camera-relative`, `draw/render-scene-gpu`, `gpu/compute`, `gpu/readback-timing` | render-scene; thumbnails force the CPU path; local shadow views' culling is `light/local-shadows`'; its last section is the visibility feedback, which the counting pass writes (merged from `draw/visibility-feedback`) |
| `draw/occlusion` | Occlusion culling | I | L | E | `draw/gpu-driven`, `gpu/coordinates` | render-scene; the cascades' occlusion and the shadow cascade cache are `light/sun-shadows-1`'s, linked forward |
| `draw/mip-streaming` | Mip streaming | I | L | E | `draw/asset-requests`, `draw/gpu-driven`, `assets/texture-cooking`, `assets/uploads`, `gpu/binding` | assets "Mip streaming"; moved from `assets/mip-streaming` (it reads the views the render scene reports); home of mip streaming: partial loads, range reads, wanted levels, raising and dropping, fades, bindless slots resolved every frame, the mip view |
| `draw/skinned` | Skinned meshes in the renderer | I | M | E | `draw/gpu-driven` | render-scene; takes a list of joint matrices per mesh as given and links forward to `animation/skinning`; home of posed bounds |
| `draw/motion-vectors` | Motion vectors and motion history | I | M | E | `draw/render-scene-gpu`, `draw/skinned` | render-scene; says in one sentence what motion vectors are for and links forward to `image/taa`, without needing it; the motion view |
