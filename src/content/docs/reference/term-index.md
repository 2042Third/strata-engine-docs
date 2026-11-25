---
id: reference/term-index
title: "Index of terms and engine identifiers"
description: "An alphabetical index that sends you from a term or an engine name to the page that explains it."
kind: reference
size: XL
tracks: []
needs: []
status: final
---

The index below sends you from a name to the page that explains it. Use it when you meet a word or a name and want to learn where the book teaches it. It gives no definitions: the glossary page holds those. It is also not the map of the reference part, which is the part's own index page.

A row is one name. The first column holds the name, sorted by letter, with terms and engine names in one list. The second column says what kind of name it is. A term is a word the book defines, such as a word of games or of the editor. An identifier is a name that stands in the engine's code, such as a class, a function, a macro or a command, and that a quoted excerpt of the book shows.

The third column holds the page. For a term it is the page where the book defines and teaches the term. When a game maker meets the term mostly in another place, the row adds that page after "Used in". A row that starts with "Same as" is another name for a term: it leads to the same page as the term it names.

For an identifier the third column names the first page whose quoted excerpt shows it, in the order of the book. After "Also in" come the other pages that quote it. Search a name that is not here in the generated tables of the reference part instead: each holds the commands, components, settings or functions of one area.

| Name | Kind | Page |
| --- | --- | --- |
| 10-bit intermediate (R10G10B10A2) | term | [Encoding, dithering and grain](../image/encoding.md) |
| `3D LUT` | term | [White balance, grading and lookup tables](../image/grading.md) |
| 7-bag | term | [Project: Tetris](../make/project-tetris.md) |
| `AABB` | term | Same as axis-aligned bounding box: [Geometry for engines: rays, planes, boxes and intersection tests](../basics/math-geometry.md). |
| Abandoned library/file | term | [Loading, calling and validating modules](../scripting/loading.md) |
| `ABI` | term | [Shared libraries and binary interfaces](../scripting/shared-libraries.md) Used in [Building and shipping script modules](../make/script-builds.md). |
| `ABI version` | term | [`scripting/abi-sdk`](../scripting/abi-sdk.md) |
| absolute path | term | [The tools: the terminal, files and a code editor](../basics/tools.md) |
| abstract class | term | [C++ classes in depth: inheritance, virtual calls and interfaces](../basics/cpp-classes.md) |
| acceleration | term | [Change over time: rates, accumulation, Euler steps and Newton's laws](../basics/math-change.md) |
| accept | term | [`automation/json-rpc`](../automation/json-rpc.md) |
| accumulation | term | [Change over time: rates, accumulation, Euler steps and Newton's laws](../basics/math-change.md) |
| accumulator | term | [Time: delta time, the fixed step and time scale](../core/time.md) Used in [The game loop from a script's side](../make/script-loop.md). |
| Acquire | term | [`gpu/how-a-gpu-frame-works`](../gpu/how-a-gpu-frame-works.md) |
| Action group | term | [Undo and redo](../editor/undo.md) |
| Action map | term | [Input actions](../input/actions.md) |
| active | term | [Dear ImGui from first principles](../editor-ui/imgui.md) |
| Active engine | term | [Loading, calling and validating modules](../scripting/loading.md) |
| Active in hierarchy | term | [The scene graph: hierarchy, transforms and the transform contract](../world/scene-graph.md) |
| active scene | term | [Play mode: the running copy](../editor/play-mode.md) |
| Activity journal | term | [The activity journal and replays](../editor/journal.md) Used in [Automated play-tests](../make/automated-playtests.md). |
| `ActivityPanel::RebuildRows` | identifier | [Instrument panels](../editor-ui/instrument-panels.md) |
| `AddColliderParts` | identifier | [From entities to bodies: records, shapes, mesh colliders](../physics/building-bodies.md) |
| `AddImGuiTextureDisplay` | identifier | [ImGui backends](../editor-ui/imgui-backends.md) |
| additive load | term | [Loading scenes: whole, additive and in slices](../world/sub-scenes.md) |
| additive loads | term | Same as additive load: [Loading scenes: whole, additive and in slices](../world/sub-scenes.md). |
| Adoption | term | [The streamer](../worlds/streamer.md) |
| advance | term | [Text: fonts, shaping and signed distance fields](../gpu/text.md) |
| Aerial perspective | term | [Earth's atmosphere and aerial perspective](../light/atmosphere.md) |
| affine transform | term | [`basics/math-matrices`](../basics/math-matrices.md) |
| affine transformation | term | Same as affine transform: [`basics/math-matrices`](../basics/math-matrices.md). |
| affine transforms | term | Same as affine transform: [`basics/math-matrices`](../basics/math-matrices.md). |
| Agent (appendix) | term | [`appendix/game-ai`](../appendix/game-ai.md) |
| `AI agent` | term | [How the editor makes games with agents](../automation/agents.md) |
| Albedo | term | [Strata's material model](../light/materials.md) |
| algorithm | term | [Data structures I: arrays, lists, hash maps and their cost](../basics/data-structures.md) |
| aliasing | term | [Sampling, aliasing and filtering](../basics/signals.md) |
| alignment | term | [Bytes in files and memory: layouts, byte order and text encodings](../basics/bytes.md) |
| allocator | term | [`basics/cpp-memory`](../basics/cpp-memory.md) |
| Allowlist | term | [Layers, registries and the composition root](../core/layers-registries.md) |
| alpha | term | [How surfaces reflect light: the reflection equation and microfacets](../light/reflectance.md) |
| Alpha weighting | term | [`assets/texture-cooking`](../assets/texture-cooking.md) |
| Alternate signal stack | term | [Crash containment](../scripting/crash-containment.md) |
| always include | term | [Exporting and shipping](../make/export.md) |
| `AlwaysInclude` | term | Same as Pruning: [Asset packs, export and patches](../assets/packs-export.md). |
| Ambient cube | term | [`indirect/gi-cascades`](../indirect/gi-cascades.md) |
| Ambient occlusion | term | [Ambient occlusion without history](../indirect/ao.md) |
| Anchor | term | [Rects, anchors and layout](../ui/layout.md) |
| angular diameter | term | Same as Source radius: [Lights with size: sized highlights and area lights](../light/area-lights.md). |
| angular velocity | term | [Rotations and quaternions](../basics/math-rotations.md) |
| animation controller | term | [Animation for game makers](../make/animation.md) |
| Animation controller (state machine) | term | [State machines](../animation/state-machines.md) |
| Animation event | term | [Animation for game makers](../make/animation.md) |
| Animation event (notify) | term | [Time, loops and events](../animation/time-events.md) |
| `AnimationController::Create` | identifier | [State machines](../animation/state-machines.md) |
| `AnimationPreview::UpdateRenderTransforms` | identifier | [Edit-mode poses and previews](../animation/editor.md) |
| `AnimationReach::Compute` | identifier | [Animating only what is seen](../animation/culling.md) |
| `AnimationSystem::ApplyRootMotion` | identifier | [Root motion](../animation/root-motion.md) |
| `AnimationSystem::DispatchEvents` | identifier | [The Animation system](../animation/system.md) |
| `AnimationSystem::OnPausedUpdate` | identifier | [Animating only what is seen](../animation/culling.md) |
| `AnimationSystem::OnUpdate` | identifier | [The Animation system](../animation/system.md) |
| `AnimationSystem::PlaceAttachments` | identifier | [The Animation system](../animation/system.md) |
| `AnimationSystem::PrepareStep` | identifier | [Animating only what is seen](../animation/culling.md) |
| `AnimationSystem::ReportVisible` | identifier | [Animating only what is seen](../animation/culling.md) |
| `AnimationSystem::StepRecord` | identifier | [Animating only what is seen](../animation/culling.md) |
| Animator | term | [Importing animated models](../animation/importing.md) Used in [Animation for game makers](../make/animation.md). |
| animator record | term | [The Animation system](../animation/system.md) |
| `AnimatorInstance::Advance` | identifier | [State machines](../animation/state-machines.md) Also in [Root motion](../animation/root-motion.md). |
| `AnimatorInstance::ConditionsHold` | identifier | [State machines](../animation/state-machines.md) |
| `AnimatorInstance::Evaluate` | identifier | [Blending and cross-fades](../animation/blending.md) Also in [Root motion](../animation/root-motion.md). |
| `AnimatorInstance::StartState` | identifier | [Blending and cross-fades](../animation/blending.md) |
| `AnimatorInstance::UpdateWeights` | identifier | [Blending and cross-fades](../animation/blending.md) |
| Annotation | term | [Continuous integration](../engineering/ci.md) |
| Anti-aliasing | term | [Graphics quality and options for players](../make/quality.md) |
| Any State | term | [State machines](../animation/state-machines.md) |
| `AO` | term | Same as Ambient occlusion: [Ambient occlusion without history](../indirect/ao.md). |
| `AoS` | term | Same as array of structs: [Data structures I: arrays, lists, hash maps and their cost](../basics/data-structures.md). |
| Append-only | term | [Shared libraries and binary interfaces](../scripting/shared-libraries.md) |
| `AppendCodepoint` | identifier | [Input devices and per-frame state](../input/devices-state.md) |
| Application | term | [From main to the first frame](../core/first-frame.md) |
| application binary interface | term | Same as `ABI`: [Shared libraries and binary interfaces](../scripting/shared-libraries.md). |
| `Application::ExecuteMainThreadQueue` | identifier | [The frame loop](../core/frame-loop.md) |
| `Application::Run` | identifier | [The frame loop](../core/frame-loop.md) |
| `Application::RunFrame` | identifier | [The frame loop](../core/frame-loop.md) |
| `Application::StartModules` | identifier | [Engine modules](../core/engine-modules.md) |
| `ApplyDeadZone` | identifier | [Input actions](../input/actions.md) |
| `ApplyHeightFog` | identifier | [Height fog](../light/fog.md) |
| `ApplyHeightFogToSky` | identifier | [Height fog](../light/fog.md) |
| `ApplyMass` | identifier | [From entities to bodies: records, shapes, mesh colliders](../physics/building-bodies.md) |
| `ApplySimulatedEvent` | identifier | [Simulated input](../input/simulated.md) |
| archetype | term | [What a game world is made of](../world/what-a-world-is.md) |
| archetypes | term | Same as archetype: [What a game world is made of](../world/what-a-world-is.md). |
| Area light | term | [Lights with size: sized highlights and area lights](../light/area-lights.md) |
| Area table | term | [`image/spatial-aa`](../image/spatial-aa.md) |
| arena | term | [`gpu/geometry-pool`](../gpu/geometry-pool.md) |
| array | term | [`basics/programming-2`](../basics/programming-2.md) |
| array index | term | [`basics/programming-2`](../basics/programming-2.md) |
| array of structs | term | [Data structures I: arrays, lists, hash maps and their cost](../basics/data-structures.md) |
| `ASCII` | term | [Bytes in files and memory: layouts, byte order and text encodings](../basics/bytes.md) |
| assert handler | term | [Debugging the engine: debuggers, asserts, the log and crash reports](../core/debugging.md) |
| assertion | term | [Ownership, errors and logging in Strata](../core/conventions.md) |
| assertion handler | term | Same as assert handler: [Debugging the engine: debuggers, asserts, the log and crash reports](../core/debugging.md). |
| asset | term | [What a game engine is: one frame, start to finish](../start/what-an-engine-is.md) Used in [A tour of the editor](../make/editor-tour.md). |
| asset field | term | [Project: a third-person platformer](../make/project-platformer.md) |
| Asset handle | term | [Handles, .meta files and sub-assets](../assets/handles-meta.md) Used in [Bringing in assets](../make/assets.md). |
| Asset manager | term | [What an asset is](../assets/what-is-an-asset.md) |
| Asset pack | term | [Asset packs, export and patches](../assets/packs-export.md) |
| Asset resolve cache | term | [Asking for assets at draw time](../draw/asset-requests.md) |
| Asset scan | term | [Importing: from source files to engine data](../assets/importing.md) |
| Asset set | term | [The Animation system](../animation/system.md) |
| Asset state | term | [Loading without stalling](../assets/loading.md) |
| Asset type | term | [Handles, .meta files and sub-assets](../assets/handles-meta.md) |
| `AssetGroupRequest` | term | Same as Group load: [References, closures, prefetch and loading screens](../assets/references.md). |
| `AssetManagerBase::CanEvictLocked` | identifier | [Residency, eviction and pins](../assets/residency.md) |
| `AssetManagerBase::EvictToFitLocked` | identifier | [Residency, eviction and pins](../assets/residency.md) |
| `AssetManagerBase::FitsPrefetchLocked` | identifier | [References, closures, prefetch and loading screens](../assets/references.md) |
| `AssetManagerBase::GetDependencyClosureLocked` | identifier | [References, closures, prefetch and loading screens](../assets/references.md) |
| `AssetManagerBase::MakeRoomFor` | identifier | [Residency, eviction and pins](../assets/residency.md) |
| `AssetManagerBase::Pin` | identifier | [Residency, eviction and pins](../assets/residency.md) |
| `AssetManagerBase::ProcessCompletions` | identifier | [Residency, eviction and pins](../assets/residency.md) Also in [Budgeted uploads](../assets/uploads.md). |
| `AssetManagerBase::ReloadAsset` | identifier | [Importing: from source files to engine data](../assets/importing.md) |
| `AssetManagerBase::TouchLocked` | identifier | [Residency, eviction and pins](../assets/residency.md) |
| `AssetPack::DecodeBlock` | identifier | [Asset packs, export and patches](../assets/packs-export.md) |
| `AssetPin` | term | Same as Pin: [Residency, eviction and pins](../assets/residency.md). |
| `AssetReferences::Find` | identifier | [The trash and references](../editor/trash-references.md) |
| `AssetResolveCache::LookUp` | identifier | [Asking for assets at draw time](../draw/asset-requests.md) |
| `AssetTrashAction::CheckRedo` | identifier | [The trash and references](../editor/trash-references.md) |
| `AssetUploadContext` | term | Same as Upload context: [Budgeted uploads](../assets/uploads.md). |
| assignment | term | [Programming from zero I: values, variables, expressions and decisions](../basics/programming-1.md) |
| Async-signal-safe | term | [Talking to the operating system](../core/platform.md) |
| Asynchronous logging | term | [Debugging the engine: debuggers, asserts, the log and crash reports](../core/debugging.md) |
| atan2 | term | [Vectors: length, direction, dot and cross products](../basics/math-vectors.md) |
| atomic | term | Same as atomic operation: [Threads, atomics and races](../basics/threads.md). |
| atomic operation | term | [Threads, atomics and races](../basics/threads.md) |
| Atomic rename | term | [Files you can trust](../core/files.md) |
| Atomic write | term | [Files you can trust](../core/files.md) |
| attach to process | term | Same as attaching a debugger: [Finding bugs: a method, the log and the debugger](../basics/debugging.md). |
| attaching a debugger | term | [Finding bugs: a method, the log and the debugger](../basics/debugging.md) |
| Attachment (socket) | term | [The Animation system](../animation/system.md) |
| `AttachToJoint` | term | [Animation for game makers](../make/animation.md) |
| Attenuation | term | [Sound in space](../audio/spatial.md) |
| Attenuation color | term | [Transparency, clear coat and glass](../light/clearcoat-transmission.md) |
| attenuation model | term | [Sound in space](../audio/spatial.md) |
| Attract mode | term | [Levels, loading screens and save files](../make/levels-saves.md) |
| Audio source | term | [Sound](../make/sound.md) |
| Audio thread | term | [Sound inside a computer](../audio/sound-in-a-computer.md) |
| `AudioSystem::ApplyComponent` | identifier | [The Audio scene system](../audio/scene-system.md) |
| `AudioSystem::DropOneShot` | identifier | [The Audio scene system](../audio/scene-system.md) |
| `AudioSystem::OnPausedChanged` | identifier | [The Audio scene system](../audio/scene-system.md) |
| `AudioSystem::ResolveClip` | identifier | [The Audio scene system](../audio/scene-system.md) |
| `AudioSystem::SelectListener` | identifier | [The Audio scene system](../audio/scene-system.md) |
| `AudioSystem::StartOneShot` | identifier | [The Audio scene system](../audio/scene-system.md) |
| `AudioSystem::UpdateMotion` | identifier | [Sound in space](../audio/spatial.md) |
| `AudioSystem::UpdateOneShots` | identifier | [The Audio scene system](../audio/scene-system.md) |
| `AudioSystem::UpdateSources` | identifier | [The Audio scene system](../audio/scene-system.md) |
| `AudioVoice::SetAttenuation` | identifier | [Sound in space](../audio/spatial.md) |
| authoritative server | term | Same as authority: [Networking for games, in general](../appendix/networking.md). |
| authority | term | [Networking for games, in general](../appendix/networking.md) |
| Automation | term | [How the editor makes games with agents](../automation/agents.md) |
| axial dead zone | term | Same as Dead zone: [Gamepads](../input/gamepads.md). |
| axis | term | [`basics/math-matrices`](../basics/math-matrices.md) |
| axis and angle | term | Same as axis-angle: [Rotations and quaternions](../basics/math-rotations.md). |
| axis-aligned bounding box | term | [Geometry for engines: rays, planes, boxes and intersection tests](../basics/math-geometry.md) |
| axis-angle | term | [Rotations and quaternions](../basics/math-rotations.md) |
| azimuth | term | [Directions on a sphere: solid angles, spherical harmonics and octahedral maps](../basics/math-sphere.md) |
| Back buffer | term | [`gpu/how-a-gpu-frame-works`](../gpu/how-a-gpu-frame-works.md) |
| back-face culling | term | Same as Winding order: [`gpu/coordinates`](../gpu/coordinates.md). |
| backlog | term | [Time: delta time, the fixed step and time scale](../core/time.md) |
| Backpressure | term | [Loading without stalling](../assets/loading.md) |
| backtrace | term | Same as stack trace: [Finding bugs: a method, the log and the debugger](../basics/debugging.md). |
| bake | term | [Sky light, ambient occlusion and reflections in your game](../make/reflections.md) |
| baked compound | term | [Rigid bodies and colliders](../physics/bodies-colliders.md) |
| banding | term | [`basics/color`](../basics/color.md) |
| bandwidth | term | [`gpu/how-a-gpu-frame-works`](../gpu/how-a-gpu-frame-works.md) |
| Banner | term | [The widget kit](../editor-ui/widget-kit.md) |
| bare name | term | [Input actions](../input/actions.md) |
| Barrier | term | [Compute shaders: dispatches, thread groups, shared memory and atomics](../gpu/compute.md) |
| base 16 | term | Same as hexadecimal: [Numbers in a computer: binary, integers, floating point and precision](../basics/numbers.md). |
| base 2 | term | Same as binary: [Numbers in a computer: binary, integers, floating point and precision](../basics/numbers.md). |
| base class | term | [`basics/programming-3`](../basics/programming-3.md) |
| base color | term | Same as Albedo: [Strata's material model](../light/materials.md). |
| Base hash | term | [`editor/recovery`](../editor/recovery.md) |
| Base instance | term | [Batching and instancing](../draw/batching.md) |
| Base64 | term | [`basics/data-formats`](../basics/data-formats.md) |
| Baseline (editor) | term | [How prefab instances stay linked](../editor/prefab-instances.md) |
| baseline (gpu) | term | [Text: fonts, shaping and signed distance fields](../gpu/text.md) |
| basis function | term | [Directions on a sphere: solid angles, spherical harmonics and octahedral maps](../basics/math-sphere.md) |
| basis vector | term | [`basics/math-matrices`](../basics/math-matrices.md) |
| Batch (assets) | term | [Budgeted uploads](../assets/uploads.md) |
| Batch (automation) | term | [`automation/json-rpc`](../automation/json-rpc.md) |
| Batch (core) | term | [Threads and the job system](../core/jobs.md) |
| Batch (draw) | term | [Batching and instancing](../draw/batching.md) |
| Batch (editor) | term | [Command scripts and batches](../editor/command-scripts.md) |
| Batch (gpu) | term | [Staging and the upload queue](../gpu/upload-queue.md) |
| Bayer dither | term | Same as ordered dither: [Sampling, aliasing and filtering](../basics/signals.md). |
| Bayer matrix | term | Same as ordered dither: [Sampling, aliasing and filtering](../basics/signals.md). |
| Bedrock | term | Same as Theme: [The design system: theme, fonts, icons](../editor-ui/design-system.md). |
| Beer-Lambert law | term | [Earth's atmosphere and aerial perspective](../light/atmosphere.md) |
| behaviour tree | term | [`appendix/game-ai`](../appendix/game-ai.md) |
| behaviour trees | term | Same as behaviour tree: [`appendix/game-ai`](../appendix/game-ai.md). |
| Bezier curve | term | [Blending and smoothing: lerp, easing, curves and exponential smoothing](../basics/math-interpolation.md) |
| big-O notation | term | [Data structures I: arrays, lists, hash maps and their cost](../basics/data-structures.md) |
| Bilateral filter | term | Same as Edge-aware blur: [`light/sun-shadows-2`](../light/sun-shadows-2.md). |
| bilinear blend | term | Same as bilinear interpolation: [Blending and smoothing: lerp, easing, curves and exponential smoothing](../basics/math-interpolation.md). |
| bilinear interpolation | term | [Blending and smoothing: lerp, easing, curves and exponential smoothing](../basics/math-interpolation.md) |
| binary | term | [Numbers in a computer: binary, integers, floating point and precision](../basics/numbers.md) |
| binary heap | term | [`basics/trees-graphs`](../basics/trees-graphs.md) |
| binary heaps | term | Same as binary heap: [`basics/trees-graphs`](../basics/trees-graphs.md). |
| binary search | term | [Data structures I: arrays, lists, hash maps and their cost](../basics/data-structures.md) |
| binary search tree | term | [`basics/trees-graphs`](../basics/trees-graphs.md) |
| binary search trees | term | Same as binary search tree: [`basics/trees-graphs`](../basics/trees-graphs.md). |
| `bind` | term | [Command scripts and batches](../editor/command-scripts.md) |
| Bind pose | term | [Skinning](../animation/skinning.md) |
| Binding (clip to skeleton) | term | [Clips: sampling motion](../animation/clips.md) |
| Binding capture | term | [Players' bindings inside the engine: the bindings file and capture](../input/rebinding.md) Used in [Menus: buttons, navigation, pause and settings screens](../make/menus.md). |
| Binding layout | term | [Pipelines and binding: layouts, registers and bindless](../gpu/binding.md) |
| binding set | term | [Pipelines and binding: layouts, registers and bindless](../gpu/binding.md) |
| Bindless | term | [Pipelines and binding: layouts, registers and bindless](../gpu/binding.md) |
| Bindless slot | term | Same as Bindless: [Pipelines and binding: layouts, registers and bindless](../gpu/binding.md). |
| Bindless texture | term | Same as Bindless: [Pipelines and binding: layouts, registers and bindless](../gpu/binding.md). |
| `BindlessTextureTable::Allocate` | identifier | [Pipelines and binding: layouts, registers and bindless](../gpu/binding.md) |
| `BindlessTextureTable::BeginFrame` | identifier | [Pipelines and binding: layouts, registers and bindless](../gpu/binding.md) |
| bisect | term | Same as bisection: [Screen-space reflections](../indirect/ssr.md). |
| bisection | term | [Screen-space reflections](../indirect/ssr.md) |
| bisections | term | Same as bisection: [Screen-space reflections](../indirect/ssr.md). |
| bisects | term | Same as bisection: [Screen-space reflections](../indirect/ssr.md). |
| bit | term | [Numbers in a computer: binary, integers, floating point and precision](../basics/numbers.md) |
| bit mask | term | [Numbers in a computer: binary, integers, floating point and precision](../basics/numbers.md) |
| bit shift | term | [Numbers in a computer: binary, integers, floating point and precision](../basics/numbers.md) |
| bitangent | term | [Bases, determinants and normals: orthonormal frames, tangent space, mirrors and the inverse transpose](../basics/math-bases.md) |
| bitangents | term | Same as bitangent: [Bases, determinants and normals: orthonormal frames, tangent space, mirrors and the inverse transpose](../basics/math-bases.md). |
| bitwise operator | term | [Numbers in a computer: binary, integers, floating point and precision](../basics/numbers.md) |
| Blend | term | [Drawing between fixed steps](../world/interpolation.md) |
| Blend weight | term | [Blending and cross-fades](../animation/blending.md) |
| `BlendFog` | identifier | [Height fog](../light/fog.md) |
| Block (pack) | term | [Asset packs, export and patches](../assets/packs-export.md) |
| `Block compression (BC1-BC7)` | term | [`assets/textures`](../assets/textures.md) |
| Bloom | term | [Lens effects: bloom, vignette, flares and fringes](../image/lens-effects.md) |
| blue noise | term | [Chance: probability, noise, integrals and Monte Carlo](../basics/math-probability.md) |
| Body record | term | [From entities to bodies: records, shapes, mesh colliders](../physics/building-bodies.md) |
| boolean | term | [Programming from zero I: values, variables, expressions and decisions](../basics/programming-1.md) |
| bounding box | term | [Geometry for engines: rays, planes, boxes and intersection tests](../basics/math-geometry.md) |
| bounding sphere | term | [Geometry for engines: rays, planes, boxes and intersection tests](../basics/math-geometry.md) |
| bounding volume | term | [Geometry for engines: rays, planes, boxes and intersection tests](../basics/math-geometry.md) |
| bounding volumes | term | Same as bounding volume: [Geometry for engines: rays, planes, boxes and intersection tests](../basics/math-geometry.md). |
| box filter | term | Same as Mitchell filter: [`assets/texture-cooking`](../assets/texture-cooking.md). |
| Box projection (parallax correction) | term | [Reflection probes](../indirect/probes.md) |
| box select | term | Same as Range selection: [Lists that scale](../editor-ui/lists.md). |
| `BoxColliderGizmo` | identifier | [Overlays, debug drawing and gizmos](../gpu/debug-drawing.md) |
| `BRDF` | term | [How surfaces reflect light: the reflection equation and microfacets](../light/reflectance.md) |
| `BRDF lookup table (LUT)` | term | Same as `BRDF table (LUT)`: [`light/energy`](../light/energy.md). |
| `BRDF table (LUT)` | term | [`light/energy`](../light/energy.md) |
| Break the merge | term | [Undo and redo](../editor/undo.md) |
| breakpoint | term | [Finding bugs: a method, the log and the debugger](../basics/debugging.md) |
| Broad phase | term | [Collision detection: shapes, broad phase and narrow phase](../physics/collision-detection.md) |
| `BT.709` | term | Same as Rec. 709: [`basics/color`](../basics/color.md). |
| Bucket | term | [Batching and instancing](../draw/batching.md) |
| Budget (assets) | term | [Residency, eviction and pins](../assets/residency.md) |
| budget (engineering) | term | [Measuring performance honestly: noise, percentiles, budgets and the perf lab](../engineering/perf-lab.md) |
| `BudgetChecker::CheckConfirmed` | identifier | [Measuring performance honestly: noise, percentiles, budgets and the perf lab](../engineering/perf-lab.md) |
| Buffer protocol | term | [`scripting/abi-sdk`](../scripting/abi-sdk.md) |
| bug | term | [Finding bugs: a method, the log and the debugger](../basics/debugging.md) |
| build | term | [Your first game](../start/first-game.md) |
| build configuration | term | [How a C++ program is built: from two files by hand to CMake](../basics/build.md) |
| build diagnostic | term | Same as diagnostic: [Building scripts from the editor: toolchains, CMake, diagnostics](../editor/script-builds.md). |
| build stamp | term | Same as stamp: [Building scripts from the editor: toolchains, CMake, diagnostics](../editor/script-builds.md). |
| build system | term | [How a C++ program is built: from two files by hand to CMake](../basics/build.md) |
| build tools | term | [Installing Strata and the C++ build tools](../start/install.md) |
| Built-in asset | term | [Handles, .meta files and sub-assets](../assets/handles-meta.md) |
| Built-in mesh | term | [Scenes, entities and components](../make/scenes-entities.md) |
| Built-in methods | term | [`automation/rpc-server`](../automation/rpc-server.md) |
| Bus | term | [The audio engine](../audio/engine.md) |
| byte | term | [`basics/computer`](../basics/computer.md) |
| byte order | term | Same as endianness: [Bytes in files and memory: layouts, byte order and text encodings](../basics/bytes.md). |
| Bézier curve | term | Same as Bezier curve: [Blending and smoothing: lerp, easing, curves and exponential smoothing](../basics/math-interpolation.md). |
| C runtime | term | Same as `CRT`: [Shared libraries and binary interfaces](../scripting/shared-libraries.md). |
| C++ build tools | term | Same as build tools: [Installing Strata and the C++ build tools](../start/install.md). |
| C++ concept | term | [Modern C++ as Strata uses it: move semantics, constexpr, optional, variant, span and concepts](../basics/cpp-modern.md) |
| C++ reference | term | [`basics/programming-3`](../basics/programming-3.md) |
| C++ standard library | term | Same as standard library: [Generic C++: templates, lambdas and the standard containers](../basics/cpp-generic.md). |
| C++ template | term | [Generic C++: templates, lambdas and the standard containers](../basics/cpp-generic.md) |
| `Cache (CMake)` | term | [How a C++ program is built: from two files by hand to CMake](../basics/build.md) |
| cache line | term | [`basics/computer`](../basics/computer.md) |
| Cache variable | term | [Building Strata](../engineering/building.md) |
| Call site | term | [Loading, calling and validating modules](../scripting/loading.md) |
| call stack | term | [Finding bugs: a method, the log and the debugger](../basics/debugging.md) |
| callback | term | [Generic C++: templates, lambdas and the standard containers](../basics/cpp-generic.md) Used in [The game loop from a script's side](../make/script-loop.md). |
| Camera cut | term | [Temporal anti-aliasing](../image/taa.md) |
| camera space | term | Same as view space: [Cameras and projection: perspective, homogeneous coordinates and depth](../basics/math-projection.md). |
| Camera-relative rendering | term | [Mirrors, normals and camera-relative positions](../draw/mirrors-camera-relative.md) |
| Camera-relative space | term | Same as Camera-relative rendering: [Mirrors, normals and camera-relative positions](../draw/mirrors-camera-relative.md). |
| Camera-relative transform | term | Same as Camera-relative rendering: [Mirrors, normals and camera-relative positions](../draw/mirrors-camera-relative.md). |
| `CameraComponent::GetProjection` | identifier | [`gpu/coordinates`](../gpu/coordinates.md) |
| `CameraLens::FromEntity` | identifier | [Depth of field](../image/depth-of-field.md) |
| `CameraLens::GetCircleOfConfusionScale` | identifier | [Depth of field](../image/depth-of-field.md) |
| Canary | term | [Measuring performance honestly: noise, percentiles, budgets and the perf lab](../engineering/perf-lab.md) |
| Cancellation flag | term | [Importing: from source files to engine data](../assets/importing.md) |
| Candela | term | [Light by the numbers: radiometric and photometric units](../light/units-exposure.md) Used in [Lighting a scene: sun, sky and exposure](../make/lighting.md). |
| Candidate | term | [Screen-space reflections](../indirect/ssr.md) |
| `Canonical JSON` | term | [Reflection: one registration, many uses](../world/reflection.md) |
| Canvas | term | [`ui/what-game-ui-does`](../ui/what-game-ui-does.md) Used in [`make/hud`](../make/hud.md). |
| Canvas mode (2D) | term | [The Scene view](../editor-ui/scene-view.md) |
| Canvas unit | term | [Rects, anchors and layout](../ui/layout.md) |
| Capacity | term | [Physics at scale and in streaming worlds](../physics/scale-streaming.md) |
| capped | term | [Measuring the frame: the frame profiler, Tracy and the method](../core/profiling.md) |
| Capture (editor) | term | [The editor camera and viewport state](../editor/camera-viewport.md) |
| `CaptureStack` | identifier | [From an address to a file and line](../scripting/symbolization.md) |
| card | term | [The widget kit](../editor-ui/widget-kit.md) |
| Caret | term | [Text and text fields](../ui/text.md) |
| cascade (indirect) | term | [`indirect/gi-cascades`](../indirect/gi-cascades.md) |
| cascade (light) | term | [Sun shadows I: stable cascades](../light/sun-shadows-1.md) |
| Cascade blend band | term | [Sun shadows I: stable cascades](../light/sun-shadows-1.md) |
| Cascaded shadow maps | term | [Sun shadows I: stable cascades](../light/sun-shadows-1.md) |
| Catch-up | term | [How prefab instances stay linked](../editor/prefab-instances.md) |
| Category bits | term | [Collision layers](../physics/collision-layers.md) |
| Catmull-Rom filter | term | [Temporal anti-aliasing](../image/taa.md) |
| `CC-BY` | term | [Bringing in assets](../make/assets.md) |
| `CC0` | term | [Bringing in assets](../make/assets.md) |
| cd | term | Same as Candela: [Light by the numbers: radiometric and photometric units](../light/units-exposure.md). |
| cell (gpu) | term | [Text: fonts, shaping and signed distance fields](../gpu/text.md) |
| Cell (worlds) | term | [Why levels must stream](../worlds/why-streaming.md) |
| Cell bounds | term | [Editing a streamed world](../editor/worlds.md) |
| Cell key | term | [Grids, keys and layers](../worlds/grids.md) |
| Cell map | term | [Editing a streamed world](../editor/worlds.md) |
| central processing unit | term | Same as processor: [`basics/computer`](../basics/computer.md). |
| `CFF` | term | Same as `TrueType`: [Text: fonts, shaping and signed distance fields](../gpu/text.md). |
| Challenge-response | term | [The security model](../automation/security.md) |
| change list | term | Same as Content version: [Loading without stalling](../assets/loading.md). |
| Change log | term | [The render scene: persistent proxies](../draw/render-scene.md) |
| Channel (animation) | term | [Clips: sampling motion](../animation/clips.md) |
| Channel (audio) | term | [Sound inside a computer](../audio/sound-in-a-computer.md) |
| Character controller | term | [Character controllers](../physics/character-controllers.md) Used in [Characters and cameras](../make/characters-cameras.md). |
| character encoding | term | Same as text encoding: [Bytes in files and memory: layouts, byte order and text encodings](../basics/bytes.md). |
| character event | term | Same as Typed text: [How input reaches a game: events, polling, edges and intents](../input/how-input-works.md). |
| `CharacterControllerSet::Step` | identifier | [Character controllers](../physics/character-controllers.md) |
| Checkerboard | term | [Screen-space reflections](../indirect/ssr.md) |
| checksum | term | [`basics/data-formats`](../basics/data-formats.md) |
| Checksum file | term | [Packaging and releasing](../engineering/releasing.md) |
| child class | term | Same as derived class: [`basics/programming-3`](../basics/programming-3.md). |
| child window | term | [Dear ImGui from first principles](../editor-ui/imgui.md) |
| Chip | term | [The widget kit](../editor-ui/widget-kit.md) |
| Chip strip | term | [The widget kit](../editor-ui/widget-kit.md) |
| `ChooseFaultLocation` | identifier | [From an address to a file and line](../scripting/symbolization.md) |
| Chromatic aberration (lateral) | term | [Lens effects: bloom, vignette, flares and fringes](../image/lens-effects.md) |
| chromaticity | term | [`basics/color`](../basics/color.md) |
| chunk | term | [Loading scenes: whole, additive and in slices](../world/sub-scenes.md) |
| `CI` | term | [Continuous integration](../engineering/ci.md) |
| `ci/<name>` | term | Same as `ci/<name>` branch: [Continuous integration](../engineering/ci.md). |
| `ci/<name>` branch | term | [Continuous integration](../engineering/ci.md) |
| Circle of confusion | term | [Depth of field](../image/depth-of-field.md) |
| `CJK` | term | [The design system: theme, fonts, icons](../editor-ui/design-system.md) |
| Claim | term | [Threads and the job system](../core/jobs.md) |
| class | term | [`basics/programming-3`](../basics/programming-3.md) |
| Class descriptor | term | [`scripting/abi-sdk`](../scripting/abi-sdk.md) |
| Clear coat | term | [Transparency, clear coat and glass](../light/clearcoat-transmission.md) |
| client-side prediction | term | [Networking for games, in general](../appendix/networking.md) |
| clip | term | [Animation for game makers](../make/animation.md) |
| Clip (animation) | term | [Clips: sampling motion](../animation/clips.md) |
| Clip compression | term | [Clips: sampling motion](../animation/clips.md) |
| Clip rect | term | [Rects, anchors and layout](../ui/layout.md) |
| Clip rectangle | term | [ImGui backends](../editor-ui/imgui-backends.md) |
| clip space | term | [Cameras and projection: perspective, homogeneous coordinates and depth](../basics/math-projection.md) |
| Clipmap | term | [Global illumination I: a voxel copy of the world](../indirect/gi-voxels.md) |
| Clipping | term | [Sound inside a computer](../audio/sound-in-a-computer.md) |
| clone | term | [Version control with git](../basics/git.md) |
| Clone (render scene) | term | [The render scene: persistent proxies](../draw/render-scene.md) |
| Closed mesh | term | [Global illumination I: a voxel copy of the world](../indirect/gi-voxels.md) |
| Closure scope | term | [References, closures, prefetch and loading screens](../assets/references.md) |
| clustered forward | term | [A frame of the scene renderer, pass by pass](../gpu/frame-tour.md) |
| Clustered shading | term | [Many lights: culling and clustered forward shading](../light/many-lights.md) |
| `CMake` | term | [How a C++ program is built: from two files by hand to CMake](../basics/build.md) |
| cmake -P | term | Same as Script mode: [Inside Strata's CMake](../engineering/cmake.md). |
| `CMake preset` | term | [Installing Strata and the C++ build tools](../start/install.md) |
| `CMake target` | term | Same as `Target (CMake)`: [Inside Strata's CMake](../engineering/cmake.md). |
| `cmake_language(DEFER)` | term | [Inside Strata's CMake](../engineering/cmake.md) |
| `CMakeCache.txt` | term | Same as Cache variable: [Building Strata](../engineering/building.md). |
| Coalescing | term | [Saving without stalling](../editor/saving.md) |
| `CoC` | term | Same as Circle of confusion: [Depth of field](../image/depth-of-field.md). |
| code | term | Same as source code: [How to read this book](../start/how-to-read.md). |
| code editor | term | [The tools: the terminal, files and a code editor](../basics/tools.md) |
| code page | term | Same as `UTF-8`: [Bytes in files and memory: layouts, byte order and text encodings](../basics/bytes.md). |
| code point | term | [Bytes in files and memory: layouts, byte order and text encodings](../basics/bytes.md) |
| code trail | term | Same as trail: [Finding your way in a large codebase](../core/reading-code.md). |
| Codec | term | [Clips, voices and sources](../audio/clips-voices-sources.md) |
| Cofactor matrix | term | [Bases, determinants and normals: orthonormal frames, tangent space, mirrors and the inverse transpose](../basics/math-bases.md) |
| `Coin::OnTriggerEnter` | identifier | [Patterns for game code: state machines, managers and object pools](../make/patterns.md) |
| `CollectOverlaps` | identifier | [Physics queries](../physics/queries.md) |
| Collide and slide | term | [Character controllers](../physics/character-controllers.md) |
| Collider | term | [Rigid bodies and colliders](../physics/bodies-colliders.md) Used in [Physics for game makers](../make/physics.md). |
| Collision event | term | [Contacts and triggers](../physics/contacts-triggers.md) |
| Collision layer | term | [Collision layers](../physics/collision-layers.md) Used in [Physics for game makers](../make/physics.md). |
| Collision step | term | [`physics/world-step`](../physics/world-step.md) |
| color channel | term | [`basics/color`](../basics/color.md) |
| color lookup | term | Same as `3D LUT`: [White balance, grading and lookup tables](../image/grading.md). |
| color space | term | [`basics/color`](../basics/color.md) |
| Color temperature | term | [White balance, grading and lookup tables](../image/grading.md) |
| Column group | term | [The runtime](../worlds/runtime.md) |
| Command | term | [Commands](../editor/commands.md) Used in [Automated play-tests](../make/automated-playtests.md). |
| command buffer | term | Same as Command list: [`gpu/how-a-gpu-frame-works`](../gpu/how-a-gpu-frame-works.md). |
| Command kind | term | [Commands](../editor/commands.md) |
| command line | term | Same as terminal command: [The tools: the terminal, files and a code editor](../basics/tools.md). |
| Command list | term | [`gpu/how-a-gpu-frame-works`](../gpu/how-a-gpu-frame-works.md) |
| Command origin | term | Same as origin: [Vectors: length, direction, dot and cross products](../basics/math-vectors.md). |
| Command registry | term | [Commands](../editor/commands.md) |
| Command runner | term | [Commands that take frames](../editor/deferred-commands.md) |
| Command script | term | [Command scripts and batches](../editor/command-scripts.md) Used in [Automated play-tests](../make/automated-playtests.md). |
| command-line argument | term | [The tools: the terminal, files and a code editor](../basics/tools.md) |
| `CommandJournal::Begin` | identifier | [The activity journal and replays](../editor/journal.md) |
| `CommandJournal::BuildReplayScript` | identifier | [The activity journal and replays](../editor/journal.md) |
| `CommandJournal::NoteEditsOutsideCommands` | identifier | [The activity journal and replays](../editor/journal.md) |
| `CommandUtils::FinishEdit` | identifier | [Commands](../editor/commands.md) Also in [Play mode: the running copy](../editor/play-mode.md). |
| comment | term | [How to read this book](../start/how-to-read.md) |
| commit | term | [Version control with git](../basics/git.md) |
| Committed generator | term | [Generated code: shaders, embedded files, version stamps and committed generators](../engineering/generated-code.md) |
| Compact definition | term | [`automation/mcp`](../automation/mcp.md) |
| `Compaction (defragmentation)` | term | [`gpu/geometry-pool`](../gpu/geometry-pool.md) |
| comparison operator | term | [Programming from zero I: values, variables, expressions and decisions](../basics/programming-1.md) |
| Comparison sampler | term | [Shadow mapping from first principles](../light/shadow-basics.md) |
| compilation | term | Same as compiler: [How a C++ program is built: from two files by hand to CMake](../basics/build.md). |
| `Compile` | identifier | [Input actions](../input/actions.md) |
| compile error | term | [`basics/programming-3`](../basics/programming-3.md) |
| compile time | term | [`basics/programming-3`](../basics/programming-3.md) |
| compiler | term | [How a C++ program is built: from two files by hand to CMake](../basics/build.md) |
| Compiler cache | term | [Compiler flags, compile time and portability](../engineering/flags-portability.md) |
| compiler error | term | Same as compile error: [`basics/programming-3`](../basics/programming-3.md). |
| Compiler launcher | term | [Compiler flags, compile time and portability](../engineering/flags-portability.md) |
| compiling | term | Same as compiler: [How a C++ program is built: from two files by hand to CMake](../basics/build.md). |
| complex section | term | [Projects and settings](../world/projects-settings.md) |
| component | term | [Entities and components, with EnTT inside](../world/ecs.md) |
| Component drawer | term | [Inspectors from reflection](../editor-ui/inspectors.md) |
| Component flags | term | [Reflection: one registration, many uses](../world/reflection.md) |
| `ComponentInfo` | term | [Reflection: one registration, many uses](../world/reflection.md) |
| Compose | term | [Drawing between fixed steps](../world/interpolation.md) |
| `ComposeTransform` | identifier | [`basics/math-matrices`](../basics/math-matrices.md) |
| Composite | term | [Input actions](../input/actions.md) Used in [Input and input actions](../make/input.md). |
| Composition root | term | [Layers, registries and the composition root](../core/layers-registries.md) |
| Compound | term | [Rigid bodies and colliders](../physics/bodies-colliders.md) |
| `ComputeCookedTextureLayout` | identifier | [`assets/texture-cooking`](../assets/texture-cooking.md) |
| `ComputeGameViewFrame` | identifier | [The Game view, shortcuts and who owns the keyboard](../editor-ui/game-view.md) |
| condition | term | [Programming from zero I: values, variables, expressions and decisions](../basics/programming-1.md) |
| condition variable | term | [Threads, atomics and races](../basics/threads.md) |
| Confidence | term | [Screen-space reflections](../indirect/ssr.md) |
| configuration struct | term | [Generic C++: templates, lambdas and the standard containers](../basics/cpp-generic.md) |
| configure step | term | [How a C++ program is built: from two files by hand to CMake](../basics/build.md) |
| Confirmed check | term | [Measuring performance honestly: noise, percentiles, budgets and the perf lab](../engineering/perf-lab.md) |
| conjugate | term | [Rotations and quaternions](../basics/math-rotations.md) |
| Connection reset | term | [`automation/json-rpc`](../automation/json-rpc.md) |
| `ConnectSignals` | identifier | [From entities to bodies: records, shapes, mesh colliders](../physics/building-bodies.md) |
| Conservative test | term | [Bounding volumes, frustums and the spatial index](../draw/bounds-culling.md) |
| Console run | term | [From main to the first frame](../core/first-frame.md) |
| `ConsolePanel::OnUpdate` | identifier | [Instrument panels](../editor-ui/instrument-panels.md) |
| Constant buffer | term | [Resources and lifetimes](../gpu/resources-lifetimes.md) |
| constant time | term | [Data structures I: arrays, lists, hash maps and their cost](../basics/data-structures.md) |
| Constant-time comparison | term | [The security model](../automation/security.md) |
| constexpr | term | [Modern C++ as Strata uses it: move semantics, constexpr, optional, variant, span and concepts](../basics/cpp-modern.md) |
| constructor | term | [`basics/programming-3`](../basics/programming-3.md) |
| Contact constraint | term | [Rigid body dynamics: integration, contacts, solvers, sleep and continuous collision](../physics/dynamics.md) |
| Contact hardening | term | [`light/sun-shadows-2`](../light/sun-shadows-2.md) |
| contact hertz | term | Same as Soft contact: [Rigid body dynamics: integration, contacts, solvers, sleep and continuous collision](../physics/dynamics.md). |
| Contact interest | term | [Contacts and triggers](../physics/contacts-triggers.md) |
| contact point | term | Same as Manifold: [Collision detection: shapes, broad phase and narrow phase](../physics/collision-detection.md). |
| Contact recycling | term | [Collision detection: shapes, broad phase and narrow phase](../physics/collision-detection.md) |
| Contact shadows | term | [`light/sun-shadows-2`](../light/sun-shadows-2.md) |
| container | term | [Generic C++: templates, lambdas and the standard containers](../basics/cpp-generic.md) |
| Containment (cascade selection) | term | [Sun shadows I: stable cascades](../light/sun-shadows-1.md) |
| Content scale | term | [Windows, events and layers](../core/windows-events.md) |
| Content stamp | term | [Importing: from source files to engine data](../assets/importing.md) |
| Content version | term | [Loading without stalling](../assets/loading.md) |
| Context | term | [`scripting/abi-sdk`](../scripting/abi-sdk.md) |
| Context (world) | term | [Entities and components, with EnTT inside](../world/ecs.md) |
| Continuous collision | term | [Physics for game makers](../make/physics.md) |
| `Continuous collision (CCD)` | term | [Rigid body dynamics: integration, contacts, solvers, sleep and continuous collision](../physics/dynamics.md) |
| continuous integration | term | Same as `CI`: [Continuous integration](../engineering/ci.md). |
| contrast | term | [Tone mapping and the Filmic curve](../image/tone-mapping.md) |
| convex | term | [Geometry for engines: rays, planes, boxes and intersection tests](../basics/math-geometry.md) |
| Convex hull | term | [Rigid bodies and colliders](../physics/bodies-colliders.md) |
| convolution | term | [Sampling, aliasing and filtering](../basics/signals.md) |
| convolution kernel | term | Same as filter kernel: [Sampling, aliasing and filtering](../basics/signals.md). |
| Cook | term | [What an asset is](../assets/what-is-an-asset.md) |
| Cooked asset | term | [What an asset is](../assets/what-is-an-asset.md) |
| Cooked documents | term | [Scene documents: text, streams and the cooked form](../world/serialization.md) |
| Cooked scene | term | [Scene documents: text, streams and the cooked form](../world/serialization.md) |
| `CookedScene` | term | Same as Cooked scene: [Scene documents: text, streams and the cooked form](../world/serialization.md). |
| `CookHDRLevels` | identifier | [`assets/texture-cooking`](../assets/texture-cooking.md) |
| `CookHull` | identifier | [From entities to bodies: records, shapes, mesh colliders](../physics/building-bodies.md) |
| Cooking | term | [From entities to bodies: records, shapes, mesh colliders](../physics/building-bodies.md) |
| `CookLevels` | identifier | [`assets/texture-cooking`](../assets/texture-cooking.md) |
| coordinate | term | [Vectors: length, direction, dot and cross products](../basics/math-vectors.md) |
| coordinate space | term | [`basics/math-matrices`](../basics/math-matrices.md) |
| coordinate system | term | Same as coordinate space: [`basics/math-matrices`](../basics/math-matrices.md). |
| copyleft license | term | Same as Permissive: [Third-party code and pinned tools](../engineering/third-party.md). |
| core loop | term | [Planning a small game: the core loop, scope, prototype and playtest](../make/designing-a-game.md) |
| Core toolset | term | [`automation/mcp`](../automation/mcp.md) |
| cos^4 law | term | Same as Vignette: [Lens effects: bloom, vignette, flares and fringes](../image/lens-effects.md). |
| cosine | term | [Vectors: length, direction, dot and cross products](../basics/math-vectors.md) |
| `CountBegin` | identifier | [Contacts and triggers](../physics/contacts-triggers.md) |
| `CountEnd` | identifier | [Contacts and triggers](../physics/contacts-triggers.md) |
| Counting pass | term | [`draw/gpu-driven`](../draw/gpu-driven.md) |
| coverage by construction | term | [The feature test](../engineering/feature-test.md) |
| Coyote time | term | [Characters and cameras](../make/characters-cameras.md) |
| `CPack` | term | [Packaging and releasing](../engineering/releasing.md) |
| `CPU` | term | Same as processor: [`basics/computer`](../basics/computer.md). |
| `CPU cache` | term | [`basics/computer`](../basics/computer.md) |
| `CPU core` | term | Same as processor core: [`basics/computer`](../basics/computer.md). |
| `CPU reference` | term | Same as `CPU twin`: [Tone mapping and the Filmic curve](../image/tone-mapping.md). |
| `CPU twin` | term | [Tone mapping and the Filmic curve](../image/tone-mapping.md) |
| `CPU-bound` | term | [Measuring the frame: the frame profiler, Tracy and the method](../core/profiling.md) |
| crash | term | [Finding bugs: a method, the log and the debugger](../basics/debugging.md) |
| Crash containment | term | [Your first script](../make/first-script.md) |
| `CrashGuard` | term | [Crash containment](../scripting/crash-containment.md) |
| `CRC-32C` | term | [`basics/data-formats`](../basics/data-formats.md) |
| `CreatePresenceBody` | identifier | [Character controllers](../physics/character-controllers.md) |
| cross product | term | [Vectors: length, direction, dot and cross products](../basics/math-vectors.md) |
| Cross-fade | term | [Blending and cross-fades](../animation/blending.md) Used in [Animation for game makers](../make/animation.md). |
| `CRT` | term | [Shared libraries and binary interfaces](../scripting/shared-libraries.md) |
| `CRTP` | term | [Generic C++: templates, lambdas and the standard containers](../basics/cpp-generic.md) |
| cryptographic hash | term | [`basics/data-formats`](../basics/data-formats.md) |
| `CSM` | term | Same as Cascaded shadow maps: [Sun shadows I: stable cascades](../light/sun-shadows-1.md). |
| `CSPRNG` | term | [The security model](../automation/security.md) |
| `CTest` | term | [Inside StrataTests](../engineering/test-program.md) |
| `.cube` | term | Same as `3D LUT`: [White balance, grading and lookup tables](../image/grading.md). |
| cube array | term | [Image-based lighting and the split sum](../indirect/ibl.md) |
| Cube map | term | [Image-based lighting and the split sum](../indirect/ibl.md) |
| Cube shadow (six faces) | term | [Shadows of point and spot lights](../light/local-shadows.md) |
| cubic Hermite curve | term | [Blending and smoothing: lerp, easing, curves and exponential smoothing](../basics/math-interpolation.md) |
| Culling mode | term | [Animating only what is seen](../animation/culling.md) |
| Culling record | term | [`draw/render-scene-gpu`](../draw/render-scene-gpu.md) |
| curiously recurring template pattern | term | Same as `CRTP`: [Generic C++: templates, lambdas and the standard containers](../basics/cpp-generic.md). |
| current folder | term | [The tools: the terminal, files and a code editor](../basics/tools.md) |
| Cursor | term | [Clips, voices and sources](../audio/clips-voices-sources.md) |
| Cursor lock | term | Same as Cursor mode: [The mouse, the cursor and the game view](../input/mouse-cursor.md). |
| Cursor mode | term | [The mouse, the cursor and the game view](../input/mouse-cursor.md) |
| Custom (preset) | term | [Quality settings and players' graphics options](../image/quality-settings.md) |
| cut list | term | [Planning a small game: the core loop, scope, prototype and playtest](../make/designing-a-game.md) |
| cycle | term | [`basics/trees-graphs`](../basics/trees-graphs.md) |
| D65 | term | [`basics/color`](../basics/color.md) |
| `DACL` | term | [Files you can trust](../core/files.md) |
| Damping | term | [Rigid bodies and colliders](../physics/bodies-colliders.md) |
| damping ratio | term | Same as Soft contact: [Rigid body dynamics: integration, contacts, solvers, sleep and continuous collision](../physics/dynamics.md). |
| dangling pointer | term | [`basics/cpp-memory`](../basics/cpp-memory.md) |
| data race | term | [Threads, atomics and races](../basics/threads.md) |
| Data source (miniaudio) | term | [Clips, voices and sources](../audio/clips-voices-sources.md) |
| data structure | term | [Data structures I: arrays, lists, hash maps and their cost](../basics/data-structures.md) |
| data type | term | Same as type: [Programming from zero I: values, variables, expressions and decisions](../basics/programming-1.md). |
| datagram | term | [Networking for games, in general](../appendix/networking.md) |
| datagrams | term | Same as datagram: [Networking for games, in general](../appendix/networking.md). |
| daylight locus | term | [White balance, grading and lookup tables](../image/grading.md) |
| `DayNight::OnUpdate` | identifier | [Sky light, ambient occlusion and reflections in your game](../make/reflections.md) |
| `dB` | term | Same as decibel: [Numbers in a computer: binary, integers, floating point and precision](../basics/numbers.md). |
| `DbgHelp` | term | [From an address to a file and line](../scripting/symbolization.md) |
| Dead probe | term | [`indirect/gi-cascades`](../indirect/gi-cascades.md) |
| Dead zone | term | [Gamepads](../input/gamepads.md) Used in [Input and input actions](../make/input.md). |
| deadlock | term | [Threads, atomics and races](../basics/threads.md) |
| `Dear ImGui` | term | [Dear ImGui from first principles](../editor-ui/imgui.md) |
| Debounce | term | [Hot reload](../scripting/hot-reload.md) |
| debug information | term | [Finding bugs: a method, the log and the debugger](../basics/debugging.md) |
| debug symbols | term | Same as debug information: [Finding bugs: a method, the log and the debugger](../basics/debugging.md). |
| Debug view (editor-ui) | term | [The Scene view](../editor-ui/scene-view.md) |
| Debug view (gpu) | term | [`gpu/debugging`](../gpu/debugging.md) |
| `DebugDraw::AddLine` | identifier | [Overlays, debug drawing and gizmos](../gpu/debug-drawing.md) |
| `DebugDraw::PackColor` | identifier | [Overlays, debug drawing and gizmos](../gpu/debug-drawing.md) |
| debugger | term | [Finding bugs: a method, the log and the debugger](../basics/debugging.md) |
| debugging | term | [Finding bugs: a method, the log and the debugger](../basics/debugging.md) |
| decal | term | [What Strata does not do, and how engines do it](../appendix/not-in-strata.md) |
| decals | term | Same as decal: [What Strata does not do, and how engines do it](../appendix/not-in-strata.md). |
| decibel | term | [Numbers in a computer: binary, integers, floating point and precision](../basics/numbers.md) |
| declaration | term | [`basics/programming-3`](../basics/programming-3.md) |
| decoder | term | Same as Codec: [Clips, voices and sources](../audio/clips-voices-sources.md). |
| Decomposition (of a transform) | term | [Bases, determinants and normals: orthonormal frames, tangent space, mirrors and the inverse transpose](../basics/math-bases.md) |
| deferred | term | [A frame of the scene renderer, pass by pass](../gpu/frame-tour.md) |
| Deferred command | term | [Commands that take frames](../editor/deferred-commands.md) |
| Deferred release | term | [Resources and lifetimes](../gpu/resources-lifetimes.md) |
| definition | term | [How a C++ program is built: from two files by hand to CMake](../basics/build.md) |
| Degenerate transform | term | [From entities to bodies: records, shapes, mesh colliders](../physics/building-bodies.md) |
| delta compression | term | [Networking for games, in general](../appendix/networking.md) |
| delta time | term | [Time: delta time, the fixed step and time scale](../core/time.md) |
| denoising | term | [Sampling, aliasing and filtering](../basics/signals.md) |
| denormal | term | Same as subnormal number: [Numbers in a computer: binary, integers, floating point and precision](../basics/numbers.md). |
| Dependency | term | [References, closures, prefetch and loading screens](../assets/references.md) |
| Dependency (import) | term | [Importing: from source files to engine data](../assets/importing.md) |
| Dependency closure | term | [References, closures, prefetch and loading screens](../assets/references.md) |
| dependency graph | term | [`basics/trees-graphs`](../basics/trees-graphs.md) |
| Dependency inversion | term | [Layers, registries and the composition root](../core/layers-registries.md) |
| depth | term | [Cameras and projection: perspective, homogeneous coordinates and depth](../basics/math-projection.md) |
| depth buffer | term | [Cameras and projection: perspective, homogeneous coordinates and depth](../basics/math-projection.md) |
| Depth prepass | term | [A frame of the scene renderer, pass by pass](../gpu/frame-tour.md) |
| depth pyramid | term | Same as Hierarchical Z-buffer: [Occlusion culling](../draw/occlusion.md). |
| Depth range pyramid | term | [`light/sun-shadows-2`](../light/sun-shadows-2.md) |
| Depth test functions | term | [`gpu/coordinates`](../gpu/coordinates.md) |
| Depth-first order | term | [Rects, anchors and layout](../ui/layout.md) |
| dereference | term | [`basics/cpp-memory`](../basics/cpp-memory.md) |
| derivative | term | [Change over time: rates, accumulation, Euler steps and Newton's laws](../basics/math-change.md) |
| derived class | term | [`basics/programming-3`](../basics/programming-3.md) |
| Derived handle | term | [Handles, .meta files and sub-assets](../assets/handles-meta.md) |
| `DeriveSubAssetHandle` | identifier | [Handles, .meta files and sub-assets](../assets/handles-meta.md) |
| `DescribeScriptBuildFailure` | identifier | [Building scripts from the editor: toolchains, CMake, diagnostics](../editor/script-builds.md) |
| Descriptor | term | [Pipelines and binding: layouts, registers and bindless](../gpu/binding.md) |
| descriptor set | term | [Pipelines and binding: layouts, registers and bindless](../gpu/binding.md) |
| Desktop entry | term | [A game's identity: the manifest, icons and platform files](../worlds/game-identity.md) |
| `DesktopEntry::ToText` | identifier | [A game's identity: the manifest, icons and platform files](../worlds/game-identity.md) |
| destructor | term | [`basics/cpp-memory`](../basics/cpp-memory.md) |
| determinant | term | [Bases, determinants and normals: orthonormal frames, tangent space, mirrors and the inverse transpose](../basics/math-bases.md) |
| determinism | term | [Numbers in a computer: binary, integers, floating point and precision](../basics/numbers.md) |
| Determinism (cross-platform) | term | [Compiler flags, compile time and portability](../engineering/flags-portability.md) |
| deterministic | term | Same as determinism: [Numbers in a computer: binary, integers, floating point and precision](../basics/numbers.md). |
| deterministic lockstep | term | [Networking for games, in general](../appendix/networking.md) |
| device driver | term | Same as driver: [Installing Strata and the C++ build tools](../start/install.md). |
| Device lost | term | [Vulkan, NVRHI, the graphics device and the Renderer's services](../gpu/vulkan-nvrhi.md) |
| Device memory budget | term | [Residency, eviction and pins](../assets/residency.md) |
| diagnostic | term | [Building scripts from the editor: toolchains, CMake, diagnostics](../editor/script-builds.md) |
| dielectric | term | [Strata's material model](../light/materials.md) |
| diff | term | [Version control with git](../basics/git.md) |
| directed graph | term | [`basics/trees-graphs`](../basics/trees-graphs.md) |
| direction tile | term | [`indirect/gi-cascades`](../indirect/gi-cascades.md) |
| Directional albedo (E) | term | [`light/energy`](../light/energy.md) |
| `DirectionToEquirect` | identifier | [Directions on a sphere: solid angles, spherical harmonics and octahedral maps](../basics/math-sphere.md) |
| Dirty cell | term | [Editing a streamed world](../editor/worlds.md) |
| Dirty flag | term | [The scene graph: hierarchy, transforms and the transform contract](../world/scene-graph.md) |
| dirty mark | term | Same as Dirty flag: [The scene graph: hierarchy, transforms and the transform contract](../world/scene-graph.md). |
| `DisableParkedBodies` | identifier | [Physics at scale and in streaming worlds](../physics/scale-streaming.md) |
| Discard | term | [Shaders: Slang, the build and the dialect](../gpu/shaders.md) |
| Discard scope | term | [Saving without stalling](../editor/saving.md) |
| Discarded (recovery) | term | [`editor/recovery`](../editor/recovery.md) |
| `DiscoverEditorEndpoints` | identifier | [Sessions, discovery and launching](../automation/sessions.md) |
| Discovery | term | [Sessions, discovery and launching](../automation/sessions.md) |
| disjoint sets | term | Same as union-find: [`basics/trees-graphs`](../basics/trees-graphs.md). |
| Disocclusion | term | [Temporal anti-aliasing](../image/taa.md) |
| dispatch | term | [Compute shaders: dispatches, thread groups, shared memory and atomics](../gpu/compute.md) |
| Dispatch list | term | [The script system](../scripting/script-system.md) |
| Dispatcher | term | [Windows, events and layers](../core/windows-events.md) |
| Display values | term | [`ui/drawing`](../ui/drawing.md) |
| display-linear | term | [Why images need post-processing, and Strata's post chain](../image/why-post.md) |
| display-referred | term | Same as `LDR`: [Why images need post-processing, and Strata's post chain](../image/why-post.md). |
| Dist | term | [Your first engine change: build from source, change one thing, test it](../core/first-change.md) |
| Distance scale | term | [Worlds meet physics and scripts](../worlds/physics-scripts.md) |
| distribution | term | Same as probability distribution: [Chance: probability, noise, integrals and Monte Carlo](../basics/math-probability.md). |
| Dither | term | [Encoding, dithering and grain](../image/encoding.md) |
| dithering | term | [Sampling, aliasing and filtering](../basics/signals.md) |
| `DLL` | term | Same as shared library: [How a C++ program is built: from two files by hand to CMake](../basics/build.md). |
| dock node | term | Same as Dock space: [Dear ImGui from first principles](../editor-ui/imgui.md). |
| Dock space | term | [Dear ImGui from first principles](../editor-ui/imgui.md) |
| `DockBuilder` | term | [The editor shell: host, layer, docking and panels](../editor-ui/shell.md) |
| doctest | term | [Testing an engine](../engineering/testing.md) |
| Document claim | term | [Saving without stalling](../editor/saving.md) |
| Dolly | term | [The editor camera and viewport state](../editor/camera-viewport.md) |
| `DOM` | term | [Scene documents: text, streams and the cooked form](../world/serialization.md) |
| Domain separation label | term | [The security model](../automation/security.md) |
| Doppler effect | term | [Sound in space](../audio/spatial.md) |
| dot product | term | [Vectors: length, direction, dot and cross products](../basics/math-vectors.md) |
| double cover | term | [Rotations and quaternions](../basics/math-rotations.md) |
| double sun | term | [The sky as a light: sources, sun extraction and presets](../light/sky.md) |
| Down | term | [How input reaches a game: events, polling, edges and intents](../input/how-input-works.md) |
| `DPI` | term | Same as Content scale: [Windows, events and layers](../core/windows-events.md). |
| `DPI scale` | term | [Windows, events and layers](../core/windows-events.md) |
| Draft (editor-ui) | term | [Inspectors from reflection](../editor-ui/inspectors.md) |
| Drag and drop payload | term | [Lists that scale](../editor-ui/lists.md) |
| draw command | term | Same as Draw list: [Batching and instancing](../draw/batching.md). |
| draw data | term | Same as Draw list: [Batching and instancing](../draw/batching.md). |
| Draw entry | term | [Batching and instancing](../draw/batching.md) |
| Draw list | term | [Batching and instancing](../draw/batching.md) |
| Draw run | term | [`ui/drawing`](../ui/drawing.md) |
| `drawIndexedIndirectCount` | term | [`draw/gpu-driven`](../draw/gpu-driven.md) |
| drawn pose | term | [Characters and cameras](../make/characters-cameras.md) |
| drawn transform | term | [Drawing between fixed steps](../world/interpolation.md) |
| `DrawShape` | identifier | [Overlays, debug drawing and gizmos](../gpu/debug-drawing.md) |
| driver | term | [Installing Strata and the C++ build tools](../start/install.md) |
| Dry run | term | [Packaging and releasing](../engineering/releasing.md) |
| Dual quaternion skinning | term | [Skinning](../animation/skinning.md) |
| dynamic allocation | term | [`basics/cpp-memory`](../basics/cpp-memory.md) |
| dynamic array | term | [`basics/programming-2`](../basics/programming-2.md) |
| Dynamic body | term | [Rigid bodies and colliders](../physics/bodies-colliders.md) |
| dynamic library | term | Same as shared library: [How a C++ program is built: from two files by hand to CMake](../basics/build.md). |
| dynamic resolution | term | Same as Render scale: [Quality settings and players' graphics options](../image/quality-settings.md). |
| `Dynamic textures (ImGui 1.92)` | term | [ImGui backends](../editor-ui/imgui-backends.md) |
| dynamic tree | term | [Collision detection: shapes, broad phase and narrow phase](../physics/collision-detection.md) |
| easing | term | Same as easing function: [Blending and smoothing: lerp, easing, curves and exponential smoothing](../basics/math-interpolation.md). |
| easing function | term | [Blending and smoothing: lerp, easing, curves and exponential smoothing](../basics/math-interpolation.md) |
| `ECS (entity-component-system)` | term | [What a game world is made of](../world/what-a-world-is.md) |
| Edge (transition) | term | [How input reaches a game: events, polling, edges and intents](../input/how-input-works.md) |
| Edge-aware blur | term | [`light/sun-shadows-2`](../light/sun-shadows-2.md) |
| Edit layer | term | [Editing a streamed world](../editor/worlds.md) |
| Edit pose | term | [Edit-mode poses and previews](../animation/editor.md) |
| Edited scene | term | [Play mode: the running copy](../editor/play-mode.md) |
| editor | term | [What Strata is and what this book teaches](../start/welcome.md) |
| editor camera | term | [The editor camera and viewport state](../editor/camera-viewport.md) |
| Editor core | term | [`editor/program`](../editor/program.md) |
| Editor host | term | Same as `EditorHost`: [`editor/program`](../editor/program.md). |
| Editor shell | term | [The editor shell: host, layer, docking and panels](../editor-ui/shell.md) |
| Editor view | term | [The editor camera and viewport state](../editor/camera-viewport.md) |
| `EditorAssetManager::PlanAssetPack` | identifier | [Asset packs, export and patches](../assets/packs-export.md) |
| `EditorAssetManager::WriteAssetPack` | identifier | [Asset packs, export and patches](../assets/packs-export.md) |
| `EditorAutomation::Stop` | identifier | [Sessions, discovery and launching](../automation/sessions.md) |
| `EditorCommandRegistry` | term | Same as Command registry: [Commands](../editor/commands.md). |
| `EditorCommandRegistry::CheckParameters` | identifier | [Commands](../editor/commands.md) |
| `EditorCommandRegistry::Execute` | identifier | [Commands](../editor/commands.md) Also in [The activity journal and replays](../editor/journal.md). |
| `EditorCommandRegistry::Run` | identifier | [Commands](../editor/commands.md) |
| `EditorCommandRunner::Update` | identifier | [Commands that take frames](../editor/deferred-commands.md) |
| `EditorConnection::IsPinnedEditor` | identifier | [Sessions, discovery and launching](../automation/sessions.md) |
| `EditorContext` | term | [`editor/program`](../editor/program.md) |
| `EditorContext::BeginOpenScene` | identifier | [Opening projects and scenes: templates, background loads and migration](../editor/projects.md) |
| `EditorContext::CheckSceneEditable` | identifier | [Opening projects and scenes: templates, background loads and migration](../editor/projects.md) |
| `EditorContext::CommitEdit` | identifier | [Undo and redo](../editor/undo.md) |
| `EditorContext::FinishOpenScene` | identifier | [Opening projects and scenes: templates, background loads and migration](../editor/projects.md) |
| `EditorContext::GetPlayBuildReason` | identifier | [Building scripts from the editor: toolchains, CMake, diagnostics](../editor/script-builds.md) |
| `EditorContext::HandleRuntimeRequests` | identifier | [Play mode: the running copy](../editor/play-mode.md) |
| `EditorContext::OpenProjectInternal` | identifier | [Opening projects and scenes: templates, background loads and migration](../editor/projects.md) |
| `EditorContext::Play` | identifier | [Play mode: the running copy](../editor/play-mode.md) |
| `EditorContext::StartRuntime` | identifier | [Play mode: the running copy](../editor/play-mode.md) |
| `EditorContext::Stop` | identifier | [Play mode: the running copy](../editor/play-mode.md) |
| `EditorContext::StopOnScriptFault` | identifier | [Play mode: the running copy](../editor/play-mode.md) |
| `EditorContext::UpdateInputSuspension` | identifier | [Pausing, stepping and exact tests](../editor/stepping.md) |
| `EditorContext::UpdateProjectMigration` | identifier | [Opening projects and scenes: templates, background loads and migration](../editor/projects.md) |
| `EditorContext::UpdateSceneLoad` | identifier | [Opening projects and scenes: templates, background loads and migration](../editor/projects.md) |
| `EditorHost` | term | [`editor/program`](../editor/program.md) |
| `EditorLayer::DrawStatusBar` | identifier | [Status bar, toasts and idle throttling](../editor-ui/status.md) |
| `EditorLayer::HandleShortcuts` | identifier | [The Game view, shortcuts and who owns the keyboard](../editor-ui/game-view.md) |
| `EditorLayer::IsBusy` | identifier | [Status bar, toasts and idle throttling](../editor-ui/status.md) |
| `EditorLayer::OnDetach` | identifier | [Sessions, discovery and launching](../automation/sessions.md) |
| `EditorLayer::OnImGuiRender` | identifier | [Instrument panels](../editor-ui/instrument-panels.md) |
| `EditorLayer::OnUpdate` | identifier | [`editor/program`](../editor/program.md) |
| `EditorLayer::StartPlay` | identifier | [The Game view, shortcuts and who owns the keyboard](../editor-ui/game-view.md) |
| `EditorLayer::StatusPillText` | identifier | [Status bar, toasts and idle throttling](../editor-ui/status.md) |
| `EditorLayer::StopPlay` | identifier | [The Game view, shortcuts and who owns the keyboard](../editor-ui/game-view.md) |
| `EditorLayer::UpdateFrameRate` | identifier | [Status bar, toasts and idle throttling](../editor-ui/status.md) |
| `EditorLayer::UpdateSteppingFrameRate` | identifier | [Pausing, stepping and exact tests](../editor/stepping.md) |
| `EditorNotifications::Post` | identifier | [Status bar, toasts and idle throttling](../editor-ui/status.md) |
| `EditorSession::WriteSessionFiles` | identifier | [Sessions, discovery and launching](../automation/sessions.md) |
| `EditorShell` | term | Same as Editor shell: [The editor shell: host, layer, docking and panels](../editor-ui/shell.md). |
| `EditorViewport::RequestPick` | identifier | [The Scene view](../editor-ui/scene-view.md) |
| `EditorViewport::UpdatePicking` | identifier | [The Scene view](../editor-ui/scene-view.md) |
| Edits outside commands | term | [The activity journal and replays](../editor/journal.md) |
| Ellipsis | term | [Text and text fields](../ui/text.md) |
| em | term | [Text: fonts, shaping and signed distance fields](../gpu/text.md) |
| Embedded shader registry | term | [Generated code: shaders, embedded files, version stamps and committed generators](../engineering/generated-code.md) |
| encoded | term | [Why images need post-processing, and Strata's post chain](../image/why-post.md) |
| End-to-end test | term | [Testing an engine](../engineering/testing.md) |
| endianness | term | [Bytes in files and memory: layouts, byte order and text encodings](../basics/bytes.md) |
| endpoint | term | Same as Endpoints: [`assets/texture-cooking`](../assets/texture-cooking.md). |
| Endpoints | term | [`assets/texture-cooking`](../assets/texture-cooking.md) |
| Energy compensation | term | [`light/energy`](../light/energy.md) |
| engine | term | Same as game engine: [What a game engine is: one frame, start to finish](../start/what-an-engine-is.md). |
| Engine module | term | [Engine modules](../core/engine-modules.md) |
| `Engine module registration (Register<Module>Module)` | term | [How Strata is put together: programs, libraries, modules and layers](../core/map.md) |
| engine release | term | [How to read this book](../start/how-to-read.md) |
| engine service | term | Same as Scene service: [Systems, phases and fixed steps](../world/systems.md). |
| Engine-native asset | term | [What an asset is](../assets/what-is-an-asset.md) |
| `EngineModule` | term | Same as Engine module: [Engine modules](../core/engine-modules.md). |
| `EngineModuleRegistry::Create` | identifier | [Engine modules](../core/engine-modules.md) |
| entity | term | [Entities and components, with EnTT inside](../world/ecs.md) |
| `Entity ID buffer` | term | [A frame of the scene renderer, pass by pass](../gpu/frame-tour.md) |
| entity interpolation | term | [Networking for games, in general](../appendix/networking.md) |
| Entity sink | term | [Scene documents: text, streams and the cooked form](../world/serialization.md) |
| `entity-ID buffer` | term | Same as Picking: [The Scene view](../editor-ui/scene-view.md). |
| `Entity::GetProperty` | identifier | [`scripting/host-api`](../scripting/host-api.md) |
| `EntityPrototype` | term | Same as Prototype: [Prefabs: the data model](../world/prefabs.md). |
| `EntityState` | term | [Undo and redo](../editor/undo.md) |
| entry card | term | [The widget kit](../editor-ui/widget-kit.md) |
| Entry point (gpu) | term | [Shaders: Slang, the build and the dialect](../gpu/shaders.md) |
| Entry point (scripting) | term | [Shared libraries and binary interfaces](../scripting/shared-libraries.md) |
| entt signal | term | Same as signal: [Sampling, aliasing and filtering](../basics/signals.md). |
| enum class | term | Same as scoped enumeration: [Programming from zero I: values, variables, expressions and decisions](../basics/programming-1.md). |
| Environment map | term | Same as `Environment map (equirectangular HDR)`: [The sky as a light: sources, sun extraction and presets](../light/sky.md). |
| `Environment map (equirectangular HDR)` | term | [The sky as a light: sources, sun extraction and presets](../light/sky.md) |
| environment variable | term | [The tools: the terminal, files and a code editor](../basics/tools.md) |
| ephemeral port | term | [`automation/json-rpc`](../automation/json-rpc.md) |
| epoch | term | [Pre-exposure](../image/pre-exposure.md) |
| epsilon | term | Same as tolerance: [Geometry for engines: rays, planes, boxes and intersection tests](../basics/math-geometry.md). |
| `EQUAL depth test` | term | Same as Depth prepass: [A frame of the scene renderer, pass by pass](../gpu/frame-tour.md). |
| Equirectangular | term | [Image-based lighting and the split sum](../indirect/ibl.md) |
| equirectangular map | term | [Directions on a sphere: solid angles, spherical harmonics and octahedral maps](../basics/math-sphere.md) |
| Error threshold | term | [Levels of detail](../draw/lod.md) |
| `ErrorThrottle::Report` | identifier | [Ownership, errors and logging in Strata](../core/conventions.md) |
| Euler angles | term | [Rotations and quaternions](../basics/math-rotations.md) |
| Euler's number | term | [Numbers in a computer: binary, integers, floating point and precision](../basics/numbers.md) |
| `EV` | term | Same as Exposure: [Exposure: camera, eye and meter](../image/exposure.md). |
| `EV stop` | term | Same as exposure stop: [Numbers in a computer: binary, integers, floating point and precision](../basics/numbers.md). |
| `EV100` | term | [Exposure: camera, eye and meter](../image/exposure.md) |
| `Evaluate` | identifier | [Input actions](../input/actions.md) |
| `EvaluateAnimator` | identifier | [Edit-mode poses and previews](../animation/editor.md) |
| Event | term | [Windows, events and layers](../core/windows-events.md) |
| Event (input) | term | [How input reaches a game: events, polling, edges and intents](../input/how-input-works.md) |
| event parser | term | Same as Streaming parser: [Scene documents: text, streams and the cooked form](../world/serialization.md). |
| event query | term | Same as Fence: [`gpu/how-a-gpu-frame-works`](../gpu/how-a-gpu-frame-works.md). |
| Event target | term | [`ui/input`](../ui/input.md) Used in [Menus: buttons, navigation, pause and settings screens](../make/menus.md). |
| Eviction | term | [Residency, eviction and pins](../assets/residency.md) |
| Exact | term | [Drawing between fixed steps](../world/interpolation.md) |
| `EXCLUDE_FROM_ALL` | term | [Inside Strata's CMake](../engineering/cmake.md) |
| Exclusive (cases) | term | [Chance: probability, noise, integrals and Monte Carlo](../basics/math-probability.md) |
| executable | term | [How a C++ program is built: from two files by hand to CMake](../basics/build.md) |
| executable file | term | Same as executable: [How a C++ program is built: from two files by hand to CMake](../basics/build.md). |
| exit code | term | [The tools: the terminal, files and a code editor](../basics/tools.md) |
| exit status | term | Same as exit code: [The tools: the terminal, files and a code editor](../basics/tools.md). |
| Exit time | term | [Time, loops and events](../animation/time-events.md) |
| `expect` | term | [Command scripts and batches](../editor/command-scripts.md) |
| expectation | term | Same as expected value: [Chance: probability, noise, integrals and Monte Carlo](../basics/math-probability.md). |
| expected value | term | [Chance: probability, noise, integrals and Monte Carlo](../basics/math-probability.md) |
| explicit Euler method | term | [Change over time: rates, accumulation, Euler steps and Newton's laws](../basics/math-change.md) |
| `Explorer::UpdateTeleport` | identifier | [Worlds meet physics and scripts](../worlds/physics-scripts.md) |
| exponent | term | [Numbers in a computer: binary, integers, floating point and precision](../basics/numbers.md) |
| exponential decay | term | [Blending and smoothing: lerp, easing, curves and exponential smoothing](../basics/math-interpolation.md) |
| Exponential depth slices | term | [Many lights: culling and clustered forward shading](../light/many-lights.md) |
| exponential function | term | [Numbers in a computer: binary, integers, floating point and precision](../basics/numbers.md) |
| exponential smoothing | term | [Blending and smoothing: lerp, easing, curves and exponential smoothing](../basics/math-interpolation.md) |
| export | term | [What a game engine is: one frame, start to finish](../start/what-an-engine-is.md) Used in [Exporting and shipping](../make/export.md). |
| Exposure | term | [Exposure: camera, eye and meter](../image/exposure.md) |
| `Exposure (EV)` | term | [Lighting a scene: sun, sky and exposure](../make/lighting.md) |
| Exposure compensation | term | [Exposure: camera, eye and meter](../image/exposure.md) |
| Exposure key | term | [Exposure: camera, eye and meter](../image/exposure.md) |
| exposure stop | term | [Numbers in a computer: binary, integers, floating point and precision](../basics/numbers.md) |
| expression | term | [Programming from zero I: values, variables, expressions and decisions](../basics/programming-1.md) |
| External editor | term | [Your first script](../make/first-script.md) |
| Extinction | term | [Earth's atmosphere and aerial perspective](../light/atmosphere.md) |
| Extra data | term | [Reflection: one registration, many uses](../world/reflection.md) |
| extrapolate | term | Same as extrapolation: [Drawing between fixed steps](../world/interpolation.md). |
| extrapolated | term | Same as extrapolation: [Drawing between fixed steps](../world/interpolation.md). |
| extrapolates | term | Same as extrapolation: [Drawing between fixed steps](../world/interpolation.md). |
| extrapolating | term | Same as extrapolation: [Drawing between fixed steps](../world/interpolation.md). |
| extrapolation | term | [Drawing between fixed steps](../world/interpolation.md) |
| eye space | term | Same as view space: [Cameras and projection: perspective, homogeneous coordinates and depth](../basics/math-projection.md). |
| f-number | term | Same as Thin lens: [Depth of field](../image/depth-of-field.md). |
| F0 | term | [How surfaces reflect light: the reflection equation and microfacets](../light/reflectance.md) |
| Fade-in | term | [Mip streaming](../draw/mip-streaming.md) |
| `Failed` | term | [Commands](../editor/commands.md) |
| `Fake CMake` | term | [Inside StrataTests](../engineering/test-program.md) |
| fake editor | term | Same as `Fake CMake`: [Inside StrataTests](../engineering/test-program.md). |
| fallback glyph | term | [The design system: theme, fonts, icons](../editor-ui/design-system.md) |
| fallback hierarchy | term | Same as fallback stack: [Where indirect light meets the surface: inputs, gathers and fallbacks](../indirect/seam.md). |
| fallback stack | term | [Where indirect light meets the surface: inputs, gathers and fallbacks](../indirect/seam.md) |
| far clip plane | term | Same as far plane: [Cameras and projection: perspective, homogeneous coordinates and depth](../basics/math-projection.md). |
| far field | term | [Depth of field](../image/depth-of-field.md) |
| far plane | term | [Cameras and projection: perspective, homogeneous coordinates and depth](../basics/math-projection.md) |
| fat box | term | [Collision detection: shapes, broad phase and narrow phase](../physics/collision-detection.md) |
| fattened box | term | Same as fat box: [Collision detection: shapes, broad phase and narrow phase](../physics/collision-detection.md). |
| Fault | term | [Crash containment](../scripting/crash-containment.md) |
| Feature test | term | [The feature test](../engineering/feature-test.md) |
| Fence | term | [`gpu/how-a-gpu-frame-works`](../gpu/how-a-gpu-frame-works.md) |
| Fence (basics) | term | [Threads, atomics and races](../basics/threads.md) |
| fiber | term | [Threads and the job system](../core/jobs.md) |
| Field | term | [Your first script](../make/first-script.md) |
| Field angle | term | [Lens effects: bloom, vignette, flares and fringes](../image/lens-effects.md) |
| field of view | term | [Cameras and projection: perspective, homogeneous coordinates and depth](../basics/math-projection.md) |
| Field override | term | [The script system](../scripting/script-system.md) |
| `FIFO` | term | Same as queue: [Data structures I: arrays, lists, hash maps and their cost](../basics/data-structures.md). |
| `FIFO present mode` | term | [The frame loop](../core/frame-loop.md) |
| `FIFO present modes` | term | Same as `FIFO present mode`: [The frame loop](../core/frame-loop.md). |
| file | term | [The tools: the terminal, files and a code editor](../basics/tools.md) |
| file format | term | [Bytes in files and memory: layouts, byte order and text encodings](../basics/bytes.md) |
| File lock | term | [Files you can trust](../core/files.md) |
| file mode 0700 | term | [Files you can trust](../core/files.md) |
| file path | term | Same as path: [The tools: the terminal, files and a code editor](../basics/tools.md). |
| File watcher | term | [Importing: from source files to engine data](../assets/importing.md) |
| Filled image | term | [`ui/drawing`](../ui/drawing.md) |
| Film grain | term | [Encoding, dithering and grain](../image/encoding.md) |
| Filmic (Strata) | term | [Tone mapping and the Filmic curve](../image/tone-mapping.md) |
| filter kernel | term | [Sampling, aliasing and filtering](../basics/signals.md) |
| filtered importance sampling | term | [Image-based lighting and the split sum](../indirect/ibl.md) |
| filtering | term | [Sampling, aliasing and filtering](../basics/signals.md) |
| Finalize | term | [Loading without stalling](../assets/loading.md) |
| `FindBodyOwner` | identifier | [From entities to bodies: records, shapes, mesh colliders](../physics/building-bodies.md) |
| `FindElfFunction` | identifier | [From an address to a file and line](../scripting/symbolization.md) |
| Firefly | term | [Lens effects: bloom, vignette, flares and fringes](../image/lens-effects.md) |
| first instance | term | [Batching and instancing](../draw/batching.md) |
| First-use order | term | [Asset packs, export and patches](../assets/packs-export.md) |
| Fit content | term | [Rects, anchors and layout](../ui/layout.md) |
| `FitSubset` | identifier | [`assets/texture-cooking`](../assets/texture-cooking.md) |
| fixed step | term | [Time: delta time, the fixed step and time scale](../core/time.md) Used in [The game loop from a script's side](../make/script-loop.md). |
| Fixed update | term | [The game loop from a script's side](../make/script-loop.md) |
| `Fixture (CTest)` | term | [Inside StrataTests](../engineering/test-program.md) |
| `FK` | term | Same as Forward kinematics: [Skeletons and forward kinematics](../animation/skeletons.md). |
| flaky | term | Same as flaky test: [Testing an engine](../engineering/testing.md). |
| flaky test | term | [Testing an engine](../engineering/testing.md) |
| flaky tests | term | Same as flaky test: [Testing an engine](../engineering/testing.md). |
| Flicker meter | term | [`engineering/test-kinds`](../engineering/test-kinds.md) |
| floating point | term | Same as floating-point number: [Numbers in a computer: binary, integers, floating point and precision](../basics/numbers.md). |
| floating-point number | term | [Numbers in a computer: binary, integers, floating point and precision](../basics/numbers.md) |
| floor | term | [The render scene: persistent proxies](../draw/render-scene.md) |
| fly | term | [The editor camera and viewport state](../editor/camera-viewport.md) |
| `FMA` | term | Same as Precompiled header: [Compiler flags, compile time and portability](../engineering/flags-portability.md). |
| `FMA contraction` | term | [Compiler flags, compile time and portability](../engineering/flags-portability.md) |
| `FNV-1a` | term | [`basics/data-formats`](../basics/data-formats.md) |
| focal length | term | Same as Thin lens: [Depth of field](../image/depth-of-field.md). |
| Focus | term | [`ui/what-game-ui-does`](../ui/what-game-ui-does.md) |
| focused | term | [Dear ImGui from first principles](../editor-ui/imgui.md) |
| folder | term | [The tools: the terminal, files and a code editor](../basics/tools.md) |
| Font | term | [Text: fonts, shaping and signed distance fields](../gpu/text.md) |
| Font atlas | term | Same as Glyph atlas: [Text: fonts, shaping and signed distance fields](../gpu/text.md). |
| `FontScaleDpi` | term | [`editor-ui/ui-scale`](../editor-ui/ui-scale.md) |
| for loop | term | [`basics/programming-2`](../basics/programming-2.md) |
| force | term | [Change over time: rates, accumulation, Euler steps and Newton's laws](../basics/math-change.md) |
| format header | term | [`basics/data-formats`](../basics/data-formats.md) |
| Forward | term | [A frame of the scene renderer, pass by pass](../gpu/frame-tour.md) |
| Forward (-Z) | term | [Positions, rotations and units](../make/transforms-units.md) |
| Forward declaration | term | [Compiler flags, compile time and portability](../engineering/flags-portability.md) |
| forward Euler | term | Same as explicit Euler method: [Change over time: rates, accumulation, Euler steps and Newton's laws](../basics/math-change.md). |
| Forward kinematics | term | [Skeletons and forward kinematics](../animation/skeletons.md) |
| forwarding reference | term | [Modern C++ as Strata uses it: move semantics, constexpr, optional, variant, span and concepts](../basics/cpp-modern.md) |
| forwarding references | term | Same as forwarding reference: [Modern C++ as Strata uses it: move semantics, constexpr, optional, variant, span and concepts](../basics/cpp-modern.md). |
| `FOV` | term | Same as field of view: [Cameras and projection: perspective, homogeneous coordinates and depth](../basics/math-projection.md). |
| `FPS` | term | Same as frame rate: [The frame loop](../core/frame-loop.md). |
| frame | term | [The frame loop](../core/frame-loop.md) |
| Frame (audio) | term | [Sound inside a computer](../audio/sound-in-a-computer.md) |
| frame loop | term | Same as game loop: [What a game engine is: one frame, start to finish](../start/what-an-engine-is.md). |
| frame pacing | term | [The frame loop](../core/frame-loop.md) |
| frame rate | term | [The frame loop](../core/frame-loop.md) |
| frame rate cap | term | Same as frame-rate cap: [The frame loop](../core/frame-loop.md). |
| Frame stage | term | [Measuring the frame: the frame profiler, Tracy and the method](../core/profiling.md) |
| frame time | term | [What a game engine is: one frame, start to finish](../start/what-an-engine-is.md) |
| Frame work time | term | Same as Work time: [The frame loop](../core/frame-loop.md). |
| frame-rate cap | term | [The frame loop](../core/frame-loop.md) |
| frame-rate independence | term | [Blending and smoothing: lerp, easing, curves and exponential smoothing](../basics/math-interpolation.md) |
| framebuffer | term | [Windows, events and layers](../core/windows-events.md) |
| framebuffers | term | Same as framebuffer: [Windows, events and layers](../core/windows-events.md). |
| `FrameProfiler::BeginStage` | identifier | [Measuring the frame: the frame profiler, Tracy and the method](../core/profiling.md) |
| `FrameProfiler::ClassifyFrameBound` | identifier | [Measuring the frame: the frame profiler, Tracy and the method](../core/profiling.md) |
| `FrameProfiler::ComputeStatsInPlace` | identifier | [Measuring the frame: the frame profiler, Tracy and the method](../core/profiling.md) |
| `FrameProfiler::EndStage` | identifier | [Measuring the frame: the frame profiler, Tracy and the method](../core/profiling.md) |
| Frames in flight | term | [`gpu/how-a-gpu-frame-works`](../gpu/how-a-gpu-frame-works.md) |
| frames per second | term | Same as frame rate: [The frame loop](../core/frame-loop.md). |
| Framing (automation) | term | [`automation/json-rpc`](../automation/json-rpc.md) |
| Framing (editor) | term | [The editor camera and viewport state](../editor/camera-viewport.md) |
| free list | term | [Data structures I: arrays, lists, hash maps and their cost](../basics/data-structures.md) |
| free lists | term | Same as free list: [Data structures I: arrays, lists, hash maps and their cost](../basics/data-structures.md). |
| Freeze | term | [Layers, registries and the composition root](../core/layers-registries.md) |
| frequency | term | [Sampling, aliasing and filtering](../basics/signals.md) |
| Fresnel | term | [How surfaces reflect light: the reflection equation and microfacets](../light/reflectance.md) |
| Fresnel (Schlick) | term | Same as Fresnel: [How surfaces reflect light: the reflection equation and microfacets](../light/reflectance.md). |
| Friction | term | [Rigid bodies and colliders](../physics/bodies-colliders.md) |
| front face | term | Same as Winding order: [`gpu/coordinates`](../gpu/coordinates.md). |
| Frontier | term | [The scene graph: hierarchy, transforms and the transform contract](../world/scene-graph.md) |
| froxel | term | [Many lights: culling and clustered forward shading](../light/many-lights.md) |
| Frozen struct | term | [`scripting/abi-sdk`](../scripting/abi-sdk.md) |
| frustum | term | Same as view frustum: [Cameras and projection: perspective, homogeneous coordinates and depth](../basics/math-projection.md). |
| frustum culling | term | [Bounding volumes, frustums and the spatial index](../draw/bounds-culling.md) |
| full path | term | Same as absolute path: [The tools: the terminal, files and a code editor](../basics/tools.md). |
| Fullscreen triangle | term | [`gpu/coordinates`](../gpu/coordinates.md) |
| function | term | [`basics/programming-2`](../basics/programming-2.md) |
| function argument | term | [`basics/programming-2`](../basics/programming-2.md) |
| function call | term | [`basics/programming-2`](../basics/programming-2.md) |
| function object | term | [Generic C++: templates, lambdas and the standard containers](../basics/cpp-generic.md) |
| function pointer | term | [Generic C++: templates, lambdas and the standard containers](../basics/cpp-generic.md) |
| function pointers | term | Same as function pointer: [Generic C++: templates, lambdas and the standard containers](../basics/cpp-generic.md). |
| fused multiply-add | term | Same as Precompiled header: [Compiler flags, compile time and portability](../engineering/flags-portability.md). |
| Fuzz run | term | [Inside StrataTests](../engineering/test-program.md) |
| `FXAA` | term | [`image/spatial-aa`](../image/spatial-aa.md) |
| Gain | term | [Sound inside a computer](../audio/sound-in-a-computer.md) |
| Game camera (pilot) | term | [The Scene view](../editor-ui/scene-view.md) |
| game engine | term | [What a game engine is: one frame, start to finish](../start/what-an-engine-is.md) |
| Game identity | term | [A game's identity: the manifest, icons and platform files](../worlds/game-identity.md) Used in [Exporting and shipping](../make/export.md). |
| game logic | term | [What Strata is and what this book teaches](../start/welcome.md) |
| game loop | term | [What a game engine is: one frame, start to finish](../start/what-an-engine-is.md) |
| Game manifest | term | [A game's identity: the manifest, icons and platform files](../worlds/game-identity.md) |
| game project | term | Same as project: [Your first game](../start/first-game.md). |
| Game shell | term | [Play mode: the running copy](../editor/play-mode.md) |
| Game view | term | [Play mode: the running copy](../editor/play-mode.md) |
| `GameManifest::FromJson` | identifier | [A game's identity: the manifest, icons and platform files](../worlds/game-identity.md) |
| Gamepad mapping | term | [Gamepads](../input/gamepads.md) |
| `GamePresentation::Make` | identifier | [A game's identity: the manifest, icons and platform files](../worlds/game-identity.md) |
| `GameUIScene::ComputeClips` | identifier | [Rects, anchors and layout](../ui/layout.md) |
| `GameUIScene::ComputeScale` | identifier | [Rects, anchors and layout](../ui/layout.md) |
| `GameUIScene::EnsureLayout` | identifier | [`ui/contract`](../ui/contract.md) |
| `GameUIScene::GameUIScene` | identifier | [`ui/contract`](../ui/contract.md) |
| `GameUIScene::GetContentSize` | identifier | [Rects, anchors and layout](../ui/layout.md) |
| `GameUIScene::GetPreferredSize` | identifier | [Rects, anchors and layout](../ui/layout.md) |
| `GameUIScene::LayOutAxis` | identifier | [Rects, anchors and layout](../ui/layout.md) |
| `GameUIScene::LayOutSubtree` | identifier | [Rects, anchors and layout](../ui/layout.md) |
| `GameUIScene::OnTextChanged` | identifier | [`ui/contract`](../ui/contract.md) |
| `GameUIScene::PlaceGroupChildren` | identifier | [Rects, anchors and layout](../ui/layout.md) |
| `GameUIScene::RebuildCanvas` | identifier | [Rects, anchors and layout](../ui/layout.md) |
| `GameUIScene::UpdateLayout` | identifier | [`ui/contract`](../ui/contract.md) |
| `GameUIScene::Validate` | identifier | [`ui/contract`](../ui/contract.md) |
| `GameViewPanel::UpdateGameInput` | identifier | [The Game view, shortcuts and who owns the keyboard](../editor-ui/game-view.md) |
| gamma | term | Same as gamma encoding: [`basics/color`](../basics/color.md). |
| gamma encoding | term | [`basics/color`](../basics/color.md) |
| gamut | term | [`basics/color`](../basics/color.md) |
| Generation (assets) | term | [Loading without stalling](../assets/loading.md) |
| Generation (editor) | term | [Undo and redo](../editor/undo.md) |
| `Generator (CMake)` | term | [Building Strata](../engineering/building.md) |
| Generator expression | term | [Inside Strata's CMake](../engineering/cmake.md) |
| Generic tools | term | [`automation/mcp`](../automation/mcp.md) |
| geometric series | term | [Blending and smoothing: lerp, easing, curves and exponential smoothing](../basics/math-interpolation.md) |
| Geometry pool | term | [`gpu/geometry-pool`](../gpu/geometry-pool.md) |
| `GeometryHandle` | term | [`gpu/geometry-pool`](../gpu/geometry-pool.md) |
| `GeometryLOD` | term | Same as `LOD record`: [`draw/gpu-driven`](../draw/gpu-driven.md). |
| `GeometryPool::Allocate` | identifier | [`gpu/geometry-pool`](../gpu/geometry-pool.md) |
| `GeometryPool::CompactArenas` | identifier | [`gpu/geometry-pool`](../gpu/geometry-pool.md) |
| Gesture | term | [`ui/input`](../ui/input.md) |
| `GetBuildVelocities` | identifier | [From entities to bodies: records, shapes, mesh colliders](../physics/building-bodies.md) |
| `GetEditorArguments` | identifier | [Sessions, discovery and launching](../automation/sessions.md) |
| `GetFogInscattering` | identifier | [Height fog](../light/fog.md) |
| `GetFogOpticalDepth` | identifier | [Height fog](../light/fog.md) |
| `GetMipByteSize` | identifier | [`assets/texture-cooking`](../assets/texture-cooking.md) |
| `GGX` | term | [How surfaces reflect light: the reflection equation and microfacets](../light/reflectance.md) |
| Ghost collision | term | [Collision detection: shapes, broad phase and narrow phase](../physics/collision-detection.md) |
| Ghosting | term | [Temporal anti-aliasing](../image/taa.md) |
| `GI` | term | Same as Global illumination: [The indirect-light problem](../indirect/problem.md). |
| gimbal lock | term | [Rotations and quaternions](../basics/math-rotations.md) |
| git | term | [Version control with git](../basics/git.md) |
| git branch | term | [Version control with git](../basics/git.md) |
| `GitHub Actions workflow` | term | Same as workflow: [Continuous integration](../engineering/ci.md). |
| Gizmo (editor-ui) | term | [The Scene view](../editor-ui/scene-view.md) |
| Gizmo (gpu) | term | [Overlays, debug drawing and gizmos](../gpu/debug-drawing.md) |
| Gizmo (start) | term | [Your first game](../start/first-game.md) |
| `GLFW` | term | [Windows, events and layers](../core/windows-events.md) |
| `GLFWWindow::PollGamepads` | identifier | [Gamepads](../input/gamepads.md) |
| `GLFWWindow::SetCursorMode` | identifier | [The mouse, the cursor and the game view](../input/mouse-cursor.md) |
| glob | term | [`basics/data-formats`](../basics/data-formats.md) |
| `GLOB_RECURSE CONFIGURE_DEPENDS` | term | [Inside Strata's CMake](../engineering/cmake.md) |
| Global illumination | term | [The indirect-light problem](../indirect/problem.md) |
| globs | term | Same as glob: [`basics/data-formats`](../basics/data-formats.md). |
| `GLSL` | term | [Shaders: Slang, the build and the dialect](../gpu/shaders.md) |
| glyph | term | [Text: fonts, shaping and signed distance fields](../gpu/text.md) |
| Glyph atlas | term | [Text: fonts, shaping and signed distance fields](../gpu/text.md) |
| goal-oriented action planning | term | [`appendix/game-ai`](../appendix/game-ai.md) |
| `GOAP` | term | Same as goal-oriented action planning: [`appendix/game-ai`](../appendix/game-ai.md). |
| Golden hash | term | [`physics/world-step`](../physics/world-step.md) |
| Golden-ratio turn | term | [Temporal anti-aliasing](../image/taa.md) |
| `GPOS` | term | [Text: fonts, shaping and signed distance fields](../gpu/text.md) |
| `GPU` | term | [Installing Strata and the C++ build tools](../start/install.md) |
| `GPU copy` | term | [`draw/render-scene-gpu`](../draw/render-scene-gpu.md) |
| `GPU scene` | term | [From entities to draw calls](../draw/entities-to-draws.md) |
| `GPU stage` | term | Same as `GPU stage (Strata)`: [`gpu/readback-timing`](../gpu/readback-timing.md). |
| `GPU stage (Strata)` | term | [`gpu/readback-timing`](../gpu/readback-timing.md) |
| `GPU timestamp` | term | Same as Timestamp query: [`gpu/readback-timing`](../gpu/readback-timing.md). |
| `GPU-bound` | term | [Measuring the frame: the frame profiler, Tracy and the method](../core/profiling.md) |
| `GPU-driven rendering` | term | [`draw/gpu-driven`](../draw/gpu-driven.md) |
| `GPUContext::GPUContext` | identifier | [`engineering/test-kinds`](../engineering/test-kinds.md) |
| `GPUProxy` | term | Same as Culling record: [`draw/render-scene-gpu`](../draw/render-scene-gpu.md). |
| `GPUUploadQueue::CollectCompleted` | identifier | [Staging and the upload queue](../gpu/upload-queue.md) |
| `GPUUploadQueue::PlanStep` | identifier | [Staging and the upload queue](../gpu/upload-queue.md) |
| `GPUUploadQueue::RunCopies` | identifier | [Staging and the upload queue](../gpu/upload-queue.md) |
| `GPUUploadQueue::SubmitBatch` | identifier | [Staging and the upload queue](../gpu/upload-queue.md) |
| grace period | term | Same as Graceful stop: [`automation/rpc-server`](../automation/rpc-server.md). |
| Grace window | term | [Residency, eviction and pins](../assets/residency.md) |
| Graceful stop | term | [`automation/rpc-server`](../automation/rpc-server.md) |
| granule | term | [Staging and the upload queue](../gpu/upload-queue.md) |
| `Graphics API` | term | [`gpu/how-a-gpu-frame-works`](../gpu/how-a-gpu-frame-works.md) |
| graphics card | term | Same as `GPU`: [Installing Strata and the C++ build tools](../start/install.md). |
| Graphics options | term | [Quality settings and players' graphics options](../image/quality-settings.md) |
| Graphics preset | term | [Quality settings and players' graphics options](../image/quality-settings.md) |
| graphics processing unit | term | Same as `GPU`: [Installing Strata and the C++ build tools](../start/install.md). |
| Graphics Quality preset | term | [Graphics quality and options for players](../make/quality.md) |
| Gravity scale | term | [Rigid bodies and colliders](../physics/bodies-colliders.md) |
| Gray card | term | [Exposure: camera, eye and meter](../image/exposure.md) |
| grey box | term | [Planning a small game: the core loop, scope, prototype and playtest](../make/designing-a-game.md) |
| Grid origin | term | [Grids, keys and layers](../worlds/grids.md) |
| Ground snapping | term | [Character controllers](../physics/character-controllers.md) |
| Ground state | term | [Character controllers](../physics/character-controllers.md) |
| group barrier | term | [Compute shaders: dispatches, thread groups, shared memory and atomics](../gpu/compute.md) |
| Group load | term | [References, closures, prefetch and loading screens](../assets/references.md) |
| `GrowRoom` | identifier | [Physics at scale and in streaming worlds](../physics/scale-streaming.md) |
| growth limit | term | Same as Capacity: [Physics at scale and in streaming worlds](../physics/scale-streaming.md). |
| guard band | term | [Shadows of point and spot lights](../light/local-shadows.md) |
| `GUID` | term | Same as `UUID`: [`basics/data-formats`](../basics/data-formats.md). |
| Half axis | term | [Gamepads](../input/gamepads.md) |
| half precision | term | Same as half-float: [`basics/color`](../basics/color.md). |
| Half-close | term | [`automation/json-rpc`](../automation/json-rpc.md) |
| half-float | term | [`basics/color`](../basics/color.md) |
| half-life | term | [Blending and smoothing: lerp, easing, curves and exponential smoothing](../basics/math-interpolation.md) |
| half-lives | term | Same as half-life: [Blending and smoothing: lerp, easing, curves and exponential smoothing](../basics/math-interpolation.md). |
| Half-open rect | term | [`ui/input`](../ui/input.md) |
| Half-texel remap | term | [White balance, grading and lookup tables](../image/grading.md) |
| Halton sequence | term | [Temporal anti-aliasing](../image/taa.md) |
| Hammersley sequence | term | [Chance: probability, noise, integrals and Monte Carlo](../basics/math-probability.md) |
| Hammersley set | term | Same as Hammersley sequence: [Chance: probability, noise, integrals and Monte Carlo](../basics/math-probability.md). |
| Hand-over | term | [Projects and settings](../world/projects-settings.md) |
| handedness | term | [`basics/math-matrices`](../basics/math-matrices.md) |
| `Handle (EnTT)` | term | [Entities and components, with EnTT inside](../world/ecs.md) |
| Handled flag | term | [Windows, events and layers](../core/windows-events.md) |
| Hard | term | [Systems, phases and fixed steps](../world/systems.md) |
| hardware thread | term | [`basics/computer`](../basics/computer.md) |
| hardware threads | term | Same as hardware thread: [`basics/computer`](../basics/computer.md). |
| hash | term | [Data structures I: arrays, lists, hash maps and their cost](../basics/data-structures.md) |
| `Hash (SHA-256)` | term | [`basics/data-formats`](../basics/data-formats.md) |
| hash function | term | [Data structures I: arrays, lists, hash maps and their cost](../basics/data-structures.md) |
| hash map | term | [Data structures I: arrays, lists, hash maps and their cost](../basics/data-structures.md) |
| hash table | term | Same as hash map: [Data structures I: arrays, lists, hash maps and their cost](../basics/data-structures.md). |
| hash value | term | Same as hash: [Data structures I: arrays, lists, hash maps and their cost](../basics/data-structures.md). |
| `HDR` | term | Same as high dynamic range: [`basics/color`](../basics/color.md). |
| `HDR (RGBA16F)` | term | [`assets/textures`](../assets/textures.md) |
| `HDR image` | term | [Why images need post-processing, and Strata's post chain](../image/why-post.md) |
| head-of-line blocking | term | [Networking for games, in general](../appendix/networking.md) |
| header | term | [Bytes in files and memory: layouts, byte order and text encodings](../basics/bytes.md) |
| header file | term | [`basics/programming-3`](../basics/programming-3.md) |
| Headless | term | [From main to the first frame](../core/first-frame.md) Used in [Exporting and shipping](../make/export.md). |
| Headroom | term | [References, closures, prefetch and loading screens](../assets/references.md) |
| heap | term | [`basics/computer`](../basics/computer.md) |
| heap allocation | term | Same as dynamic allocation: [`basics/cpp-memory`](../basics/cpp-memory.md). |
| Height fog | term | [Height fog](../light/fog.md) |
| Helper mode | term | [Inside StrataTests](../engineering/test-program.md) |
| hemisphere | term | [Directions on a sphere: solid angles, spherical harmonics and octahedral maps](../basics/math-sphere.md) |
| Hemisphere (quaternion) | term | [Blending and cross-fades](../animation/blending.md) |
| Henyey-Greenstein | term | [Earth's atmosphere and aerial perspective](../light/atmosphere.md) |
| Hermite curve | term | Same as cubic Hermite curve: [Blending and smoothing: lerp, easing, curves and exponential smoothing](../basics/math-interpolation.md). |
| hex | term | Same as hexadecimal: [Numbers in a computer: binary, integers, floating point and precision](../basics/numbers.md). |
| hexadecimal | term | [Numbers in a computer: binary, integers, floating point and precision](../basics/numbers.md) |
| Hi-Z march | term | [Screen-space reflections](../indirect/ssr.md) |
| Hierarchical Z-buffer | term | [Occlusion culling](../draw/occlusion.md) |
| Hierarchy version | term | [The scene graph: hierarchy, transforms and the transform contract](../world/scene-graph.md) |
| high dynamic range | term | [`basics/color`](../basics/color.md) |
| Histogram | term | [Exposure: camera, eye and meter](../image/exposure.md) |
| History | term | [Temporal anti-aliasing](../image/taa.md) |
| Hit test | term | [`ui/input`](../ui/input.md) |
| hitch | term | [What a game engine is: one frame, start to finish](../start/what-an-engine-is.md) |
| `HLOD` | term | [Why levels must stream](../worlds/why-streaming.md) |
| `HLSL` | term | [Shaders: Slang, the build and the dialect](../gpu/shaders.md) |
| `HMAC (automation)` | term | [The security model](../automation/security.md) |
| `HMAC (basics)` | term | [`basics/data-formats`](../basics/data-formats.md) |
| Hold (editor) | term | [Pausing, stepping and exact tests](../editor/stepping.md) |
| `HoldRoot` | identifier | [Root motion](../animation/root-motion.md) |
| homogeneous coordinates | term | [Cameras and projection: perspective, homogeneous coordinates and depth](../basics/math-projection.md) |
| Hook | term | [Engine modules](../core/engine-modules.md) |
| horizon angle | term | [Ambient occlusion without history](../indirect/ao.md) |
| Horizon fade | term | [Image-based lighting and the split sum](../indirect/ibl.md) |
| Host | term | [`scripting/abi-sdk`](../scripting/abi-sdk.md) |
| Host function | term | [`scripting/host-api`](../scripting/host-api.md) |
| `HostCall` | identifier | [`scripting/host-api`](../scripting/host-api.md) |
| `HostInstantiate` | identifier | [`scripting/host-api`](../scripting/host-api.md) |
| `HostSetTimeScale` | identifier | [`scripting/host-api`](../scripting/host-api.md) |
| `HostWriteSaveFile` | identifier | [`scripting/host-api`](../scripting/host-api.md) |
| hot reload | term | [Your first script](../make/first-script.md) |
| Hovered | term | [Dear ImGui from first principles](../editor-ui/imgui.md) |
| `HRTF` | term | [Sound in space](../audio/spatial.md) |
| Hue skew | term | [Tone mapping and the Filmic curve](../image/tone-mapping.md) |
| Hysteresis | term | [Gamepads](../input/gamepads.md) |
| Hysteresis (H) | term | Same as Hysteresis: [Gamepads](../input/gamepads.md). |
| Hysteresis (stick) | term | Same as Hysteresis: [Gamepads](../input/gamepads.md). |
| `HZB` | term | Same as Hierarchical Z-buffer: [Occlusion culling](../draw/occlusion.md). |
| `IBL` | term | Same as Image-based lighting: [Image-based lighting and the split sum](../indirect/ibl.md). |
| Icon font | term | [The design system: theme, fonts, icons](../editor-ui/design-system.md) |
| `ICtCp` | term | [Tone mapping and the Filmic curve](../image/tone-mapping.md) |
| `ID` | term | [Dear ImGui from first principles](../editor-ui/imgui.md) |
| `ID stack` | term | Same as `ID`: [Dear ImGui from first principles](../editor-ui/imgui.md). |
| `IDE` | term | Same as integrated development environment: [Building and shipping script modules](../make/script-builds.md). |
| Identity (rotation) | term | [Rotations and quaternions](../basics/math-rotations.md) |
| identity matrix | term | [`basics/math-matrices`](../basics/math-matrices.md) |
| identity quaternion | term | Same as Identity (rotation): [Rotations and quaternions](../basics/math-rotations.md). |
| `IDEs` | term | Same as integrated development environment: [Building and shipping script modules](../make/script-builds.md). |
| Idle throttling | term | [Status bar, toasts and idle throttling](../editor-ui/status.md) |
| Idle timeout | term | [Sessions, discovery and launching](../automation/sessions.md) |
| if statement | term | [Programming from zero I: values, variables, expressions and decisions](../basics/programming-1.md) |
| `IGN` | term | Same as interleaved gradient noise: [Chance: probability, noise, integrals and Monte Carlo](../basics/math-probability.md). |
| image plane | term | [Cameras and projection: perspective, homogeneous coordinates and depth](../basics/math-projection.md) |
| Image-based lighting | term | [Image-based lighting and the split sum](../indirect/ibl.md) |
| `IME` | term | [How input reaches a game: events, polling, edges and intents](../input/how-input-works.md) |
| `IMGUI` | term | Same as `Immediate-mode GUI`: [`ui/what-game-ui-does`](../ui/what-game-ui-does.md). |
| `ImGui context` | term | [Dear ImGui from first principles](../editor-ui/imgui.md) |
| imgui.ini | term | [Dear ImGui from first principles](../editor-ui/imgui.md) |
| `ImGuiHarness::ClickItem` | identifier | [`editor-ui/ui-testing`](../editor-ui/ui-testing.md) |
| `ImGuiLayer::ApplyStyle` | identifier | [`editor-ui/ui-scale`](../editor-ui/ui-scale.md) |
| `ImGuiLayer::GetUIScale` | identifier | [`editor-ui/ui-scale`](../editor-ui/ui-scale.md) |
| `ImGuiLayer::OnEvent` | identifier | [ImGui backends](../editor-ui/imgui-backends.md) |
| `ImGuiLayer::ToUIScale` | identifier | [`editor-ui/ui-scale`](../editor-ui/ui-scale.md) |
| `ImGuiListClipper` | term | [Lists that scale](../editor-ui/lists.md) |
| `ImGuiModule::OnRenderUI` | identifier | [Dear ImGui from first principles](../editor-ui/imgui.md) Also in [ImGui backends](../editor-ui/imgui-backends.md). |
| `ImGuiPlatform::NewFrame` | identifier | [`editor-ui/ui-scale`](../editor-ui/ui-scale.md) |
| `ImGuiPlatform::OnKey` | identifier | [ImGui backends](../editor-ui/imgui-backends.md) |
| `ImGuiPlatform::UpdateCursorShape` | identifier | [ImGui backends](../editor-ui/imgui-backends.md) |
| `ImGuiRenderer::AcquireFrameBuffers` | identifier | [ImGui backends](../editor-ui/imgui-backends.md) |
| `ImGuiRenderer::Render` | identifier | [ImGui backends](../editor-ui/imgui-backends.md) |
| `ImGuiRenderer::UpdateTexture` | identifier | [ImGui backends](../editor-ui/imgui-backends.md) |
| `ImGuiTextureDisplay` | term | [ImGui backends](../editor-ui/imgui-backends.md) |
| `ImGuizmo` | term | [The Scene view](../editor-ui/scene-view.md) |
| Immediate command list | term | [Vulkan, NVRHI, the graphics device and the Renderer's services](../gpu/vulkan-nvrhi.md) |
| immediate representation | term | [From entities to draw calls](../draw/entities-to-draws.md) |
| `Immediate-mode GUI` | term | [`ui/what-game-ui-does`](../ui/what-game-ui-does.md) |
| `Impact::OnCollisionEnter` | identifier | [Sound](../make/sound.md) |
| Import | term | [What an asset is](../assets/what-is-an-asset.md) Used in [Bringing in assets](../make/assets.md). |
| Import cache | term | [Importing: from source files to engine data](../assets/importing.md) |
| Import memory admission | term | [Importing: from source files to engine data](../assets/importing.md) |
| Import record | term | [Importing: from source files to engine data](../assets/importing.md) |
| Import record store | term | [Importing: from source files to engine data](../assets/importing.md) |
| Import settings | term | [Importing: from source files to engine data](../assets/importing.md) Used in [Bringing in assets](../make/assets.md). |
| Importance sampling | term | [Chance: probability, noise, integrals and Monte Carlo](../basics/math-probability.md) |
| importer | term | [What an asset is](../assets/what-is-an-asset.md) |
| Importer version | term | [Importing: from source files to engine data](../assets/importing.md) |
| impulse | term | [Change over time: rates, accumulation, Euler steps and Newton's laws](../basics/math-change.md) |
| In flight | term | [Loading without stalling](../assets/loading.md) |
| In-place animation | term | [Root motion](../animation/root-motion.md) |
| In-scattering | term | [Earth's atmosphere and aerial perspective](../light/atmosphere.md) |
| Inactive reason | term | [Reflection: one registration, many uses](../world/reflection.md) |
| include directive | term | [`basics/programming-3`](../basics/programming-3.md) |
| incomplete type | term | [Modern C++ as Strata uses it: move semantics, constexpr, optional, variant, span and concepts](../basics/cpp-modern.md) |
| Index | term | [Grids, keys and layers](../worlds/grids.md) |
| Indirect draw | term | [Batching and instancing](../draw/batching.md) |
| Indirect light | term | [The indirect-light problem](../indirect/problem.md) |
| Inertia tensor | term | [Rigid body dynamics: integration, contacts, solvers, sleep and continuous collision](../physics/dynamics.md) |
| Inertialization | term | [Blending and cross-fades](../animation/blending.md) |
| Inf | term | Same as `NaN`: [Numbers in a computer: binary, integers, floating point and precision](../basics/numbers.md). |
| Infinite far plane | term | [`gpu/coordinates`](../gpu/coordinates.md) |
| Influence | term | [Skinning](../animation/skinning.md) |
| inheritance | term | [`basics/programming-3`](../basics/programming-3.md) |
| inline frame | term | [From an address to a file and line](../scripting/symbolization.md) |
| Inlining | term | [From an address to a file and line](../scripting/symbolization.md) |
| Inner/outer cone angle | term | [Lights: the sun, points and spots](../light/lights.md) |
| Input action | term | [Input actions](../input/actions.md) Used in [Input and input actions](../make/input.md). |
| Input frame | term | [Input devices and per-frame state](../input/devices-state.md) |
| Input layout | term | [Pipelines and binding: layouts, registers and bindless](../gpu/binding.md) |
| Input sequence | term | [Pausing, stepping and exact tests](../editor/stepping.md) Used in [Automated play-tests](../make/automated-playtests.md). |
| `Input::BeginFrame` | identifier | [Input devices and per-frame state](../input/devices-state.md) Also in [Simulated input](../input/simulated.md). |
| `Input::GetGamepadAxis` | identifier | [Gamepads](../input/gamepads.md) |
| `Input::GetGamepadStick` | identifier | [Gamepads](../input/gamepads.md) |
| `Input::GetUncapturedTypedText` | identifier | [Input devices and per-frame state](../input/devices-state.md) |
| `Input::ProcessGamepad` | identifier | [Gamepads](../input/gamepads.md) |
| `Input::ReleaseAllSimulated` | identifier | [Simulated input](../input/simulated.md) |
| `InputActions::LoadBindings` | identifier | [Players' bindings inside the engine: the bindings file and capture](../input/rebinding.md) |
| `InputActions::SimulateAction` | identifier | [Input actions](../input/actions.md) |
| `InputActions::Update` | identifier | [Input actions](../input/actions.md) |
| `InputBinding::FitsKind` | identifier | [Input actions](../input/actions.md) |
| `InputBinding::Parse` | identifier | [Input actions](../input/actions.md) |
| `InputSequence::Update` | identifier | [Pausing, stepping and exact tests](../editor/stepping.md) |
| Inset | term | [Tone mapping and the Filmic curve](../image/tone-mapping.md) |
| Install tree | term | [Packaging and releasing](../engineering/releasing.md) |
| Installation marker | term | [Packaging and releasing](../engineering/releasing.md) |
| `InstallBody` | identifier | [Physics at scale and in streaming worlds](../physics/scale-streaming.md) |
| Instance (draw) | term | [The render scene: persistent proxies](../draw/render-scene.md) |
| Instance (scripting) | term | [The script system](../scripting/script-system.md) |
| `Instance (VkInstance)` | term | [Vulkan, NVRHI, the graphics device and the Renderer's services](../gpu/vulkan-nvrhi.md) |
| instance root | term | [Prefabs: the data model](../world/prefabs.md) |
| `InstanceData` | term | Same as Instance (draw): [The render scene: persistent proxies](../draw/render-scene.md). |
| Instancing | term | [`ui/drawing`](../ui/drawing.md) |
| Instruction set extension | term | [Compiler flags, compile time and portability](../engineering/flags-portability.md) |
| integer | term | [Numbers in a computer: binary, integers, floating point and precision](../basics/numbers.md) |
| integer overflow | term | [Numbers in a computer: binary, integers, floating point and precision](../basics/numbers.md) |
| integral | term | [Change over time: rates, accumulation, Euler steps and Newton's laws](../basics/math-change.md) |
| integrated development environment | term | [Building and shipping script modules](../make/script-builds.md) |
| integration | term | Same as numerical integration: [Change over time: rates, accumulation, Euler steps and Newton's laws](../basics/math-change.md). |
| interest management | term | [Networking for games, in general](../appendix/networking.md) |
| interface | term | [C++ classes in depth: inheritance, virtual calls and interfaces](../basics/cpp-classes.md) |
| `Interface library (CMake)` | term | [Inside Strata's CMake](../engineering/cmake.md) |
| Interleaved | term | [Sound inside a computer](../audio/sound-in-a-computer.md) |
| Interleaved A/B | term | [Measuring performance honestly: noise, percentiles, budgets and the perf lab](../engineering/perf-lab.md) |
| interleaved gradient noise | term | [Chance: probability, noise, integrals and Monte Carlo](../basics/math-probability.md) |
| Interpolant | term | [`gpu/how-a-gpu-frame-works`](../gpu/how-a-gpu-frame-works.md) |
| interpolate | term | Same as interpolation: [Drawing between fixed steps](../world/interpolation.md). |
| interpolated | term | Same as interpolation: [Drawing between fixed steps](../world/interpolation.md). |
| interpolated set | term | [Drawing between fixed steps](../world/interpolation.md) |
| interpolates | term | Same as interpolation: [Drawing between fixed steps](../world/interpolation.md). |
| interpolating | term | Same as interpolation: [Drawing between fixed steps](../world/interpolation.md). |
| interpolation | term | [Drawing between fixed steps](../world/interpolation.md) Used in [Characters and cameras](../make/characters-cameras.md). |
| Interpolation (render) | term | Same as interpolation: [Drawing between fixed steps](../world/interpolation.md). |
| Interposition | term | [Shared libraries and binary interfaces](../scripting/shared-libraries.md) |
| intersection test | term | [Geometry for engines: rays, planes, boxes and intersection tests](../basics/math-geometry.md) |
| interval | term | [`indirect/gi-cascades`](../indirect/gi-cascades.md) |
| `InvalidParameters` | term | [Commands](../editor/commands.md) |
| Invariant (position) | term | Same as Invariant position: [A frame of the scene renderer, pass by pass](../gpu/frame-tour.md). |
| Invariant position | term | [A frame of the scene renderer, pass by pass](../gpu/frame-tour.md) |
| Inverse bind matrix | term | [Skinning](../animation/skinning.md) |
| inverse lerp | term | Same as inverse linear interpolation: [Blending and smoothing: lerp, easing, curves and exponential smoothing](../basics/math-interpolation.md). |
| inverse linear interpolation | term | [Blending and smoothing: lerp, easing, curves and exponential smoothing](../basics/math-interpolation.md) |
| inverse matrix | term | [`basics/math-matrices`](../basics/math-matrices.md) |
| `InvisibleButton` | term | [The widget kit](../editor-ui/widget-kit.md) |
| invocation | term | Same as Thread (gpu): [Compute shaders: dispatches, thread groups, shared memory and atomics](../gpu/compute.md). |
| `IOR` | term | [How surfaces reflect light: the reflection equation and microfacets](../light/reflectance.md) |
| Irradiance | term | [Light by the numbers: radiometric and photometric units](../light/units-exposure.md) |
| Irradiance field | term | [`indirect/gi-cascades`](../indirect/gi-cascades.md) |
| `ISkinningPoses` | term | [The Animation system](../animation/system.md) |
| Island | term | [Rigid body dynamics: integration, contacts, solvers, sleep and continuous collision](../physics/dynamics.md) |
| `IsMergedTransition` | identifier | [Simulated input](../input/simulated.md) |
| `IsPlainFileName` | identifier | [A game's identity: the manifest, icons and platform files](../worlds/game-identity.md) |
| `IsStructural` | identifier | [`editor/recovery`](../editor/recovery.md) |
| Item | term | [Dear ImGui from first principles](../editor-ui/imgui.md) |
| Item probe | term | [The widget kit](../editor-ui/widget-kit.md) |
| iterator | term | [Generic C++: templates, lambdas and the standard containers](../basics/cpp-generic.md) |
| `JavaScript Object Notation` | term | Same as `JSON`: [`basics/data-formats`](../basics/data-formats.md). |
| Jitter | term | [Temporal anti-aliasing](../image/taa.md) |
| Jitter (networking) | term | [Networking for games, in general](../appendix/networking.md) |
| `Jitter (TAA)` | term | [Temporal anti-aliasing](../image/taa.md) |
| job | term | [Threads, atomics and races](../basics/threads.md) |
| job handle | term | [Threads and the job system](../core/jobs.md) |
| Join | term | [`indirect/gi-cascades`](../indirect/gi-cascades.md) |
| joint | term | [Animation for game makers](../make/animation.md) |
| Joint (bone) | term | [Skeletons and forward kinematics](../animation/skeletons.md) |
| Journal (feature test) | term | [The feature test](../engineering/feature-test.md) |
| `JSON` | term | [`basics/data-formats`](../basics/data-formats.md) |
| `JSON array` | term | [`basics/data-formats`](../basics/data-formats.md) |
| `JSON object` | term | [`basics/data-formats`](../basics/data-formats.md) |
| `JSON pointer` | term | [Command scripts and batches](../editor/command-scripts.md) |
| `JSON Schema` | term | [Commands](../editor/commands.md) |
| `JSON-RPC 2.0` | term | [`automation/json-rpc`](../automation/json-rpc.md) |
| judder | term | [Drawing between fixed steps](../world/interpolation.md) |
| Kahn's algorithm | term | [Engine modules](../core/engine-modules.md) |
| Karis average | term | [Lens effects: bloom, vignette, flares and fringes](../image/lens-effects.md) |
| kelvin | term | Same as Color temperature: [White balance, grading and lookup tables](../image/grading.md). |
| Kerning | term | [Text: fonts, shaping and signed distance fields](../gpu/text.md) |
| Key (editor) | term | [Thumbnails](../editor/thumbnails.md) |
| Key code | term | [How input reaches a game: events, polling, edges and intents](../input/how-input-works.md) |
| Key repeat | term | [How input reaches a game: events, polling, edges and intents](../input/how-input-works.md) |
| keyboard capture | term | Same as Pointer capture: [Input devices and per-frame state](../input/devices-state.md). |
| keyframe | term | [Blending and smoothing: lerp, easing, curves and exponential smoothing](../basics/math-interpolation.md) |
| Keyframe reduction | term | [Clips: sampling motion](../animation/clips.md) |
| kick | term | [Project: Tetris](../make/project-tetris.md) |
| Kinematic body | term | [Rigid bodies and colliders](../physics/bodies-colliders.md) |
| `Label (CTest)` | term | [Inside StrataTests](../engineering/test-program.md) |
| lag compensation | term | [Networking for games, in general](../appendix/networking.md) |
| lambda | term | [Generic C++: templates, lambdas and the standard containers](../basics/cpp-generic.md) |
| lambda capture | term | [Generic C++: templates, lambdas and the standard containers](../basics/cpp-generic.md) |
| lambda expression | term | Same as lambda: [Generic C++: templates, lambdas and the standard containers](../basics/cpp-generic.md). |
| Lambert | term | [How surfaces reflect light: the reflection equation and microfacets](../light/reflectance.md) |
| Lambert diffuse | term | Same as Lambert: [How surfaces reflect light: the reflection equation and microfacets](../light/reflectance.md). |
| Latency | term | [Sound inside a computer](../audio/sound-in-a-computer.md) |
| Latency (networking) | term | [Networking for games, in general](../appendix/networking.md) |
| latitude-longitude map | term | Same as equirectangular map: [Directions on a sphere: solid angles, spherical harmonics and octahedral maps](../basics/math-sphere.md). |
| `LaunchEditor` | identifier | [Sessions, discovery and launching](../automation/sessions.md) |
| Launcher | term | [Launcher and dialogs](../editor-ui/launcher-dialogs.md) |
| Layer (application) | term | [How Strata is put together: programs, libraries, modules and layers](../core/map.md) |
| Layer (architecture) | term | Same as Layer (application): [How Strata is put together: programs, libraries, modules and layers](../core/map.md). |
| Layer (Strata) | term | Same as Layer (application): [How Strata is put together: programs, libraries, modules and layers](../core/map.md). |
| layer matrix | term | [Physics for game makers](../make/physics.md) |
| Layer table | term | [Layers, registries and the composition root](../core/layers-registries.md) |
| layering test | term | Same as Layer table: [Layers, registries and the composition root](../core/layers-registries.md). |
| `Layers.json` | term | Same as Layer table: [Layers, registries and the composition root](../core/layers-registries.md). |
| Layout (cached) | term | [`ui/contract`](../ui/contract.md) |
| Layout group | term | [Rects, anchors and layout](../ui/layout.md) |
| `LBS` | term | Same as Linear blend skinning: [Skinning](../animation/skinning.md). |
| `LDR` | term | [Why images need post-processing, and Strata's post chain](../image/why-post.md) |
| Lead-in | term | [`indirect/gi-cascades`](../indirect/gi-cascades.md) |
| least recently used | term | Same as `LRU`: [Residency, eviction and pins](../assets/residency.md). |
| left-handed | term | Same as handedness: [`basics/math-matrices`](../basics/math-matrices.md). |
| Lens flare | term | [Lens effects: bloom, vignette, flares and fringes](../image/lens-effects.md) |
| lerp | term | Same as linear interpolation: [Blending and smoothing: lerp, easing, curves and exponential smoothing](../basics/math-interpolation.md). |
| Letterboxing | term | [The Game view, shortcuts and who owns the keyboard](../editor-ui/game-view.md) |
| Level of detail | term | [Levels of detail](../draw/lod.md) |
| library | term | [How a C++ program is built: from two files by hand to CMake](../basics/build.md) |
| lifetime | term | [`basics/cpp-memory`](../basics/cpp-memory.md) |
| Light culling | term | [Many lights: culling and clustered forward shading](../light/many-lights.md) |
| Light injection | term | [`indirect/gi-cascades`](../indirect/gi-cascades.md) |
| Light record | term | [Lights: the sun, points and spots](../light/lights.md) |
| light space | term | [Shadow mapping from first principles](../light/shadow-basics.md) |
| Light/dark adaptation | term | [Exposure: camera, eye and meter](../image/exposure.md) |
| lightmap | term | [What Strata does not do, and how engines do it](../appendix/not-in-strata.md) |
| lightmaps | term | Same as lightmap: [What Strata does not do, and how engines do it](../appendix/not-in-strata.md). |
| line coverage | term | [The feature test](../engineering/feature-test.md) |
| line of sight | term | [`appendix/game-ai`](../appendix/game-ai.md) |
| Linear blend skinning | term | [Skinning](../animation/skinning.md) |
| linear color | term | [`basics/color`](../basics/color.md) |
| Linear data | term | [`assets/textures`](../assets/textures.md) |
| linear interpolation | term | [Blending and smoothing: lerp, easing, curves and exponential smoothing](../basics/math-interpolation.md) |
| Link closure | term | [Inside Strata's CMake](../engineering/cmake.md) |
| link error | term | [How a C++ program is built: from two files by hand to CMake](../basics/build.md) |
| linked list | term | [Data structures I: arrays, lists, hash maps and their cost](../basics/data-structures.md) |
| linker | term | [How a C++ program is built: from two files by hand to CMake](../basics/build.md) |
| linker error | term | Same as link error: [How a C++ program is built: from two files by hand to CMake](../basics/build.md). |
| Linker map | term | [Inside Strata's CMake](../engineering/cmake.md) |
| linking | term | Same as linker: [How a C++ program is built: from two files by hand to CMake](../basics/build.md). |
| Listener (audio) | term | [Sound in space](../audio/spatial.md) |
| Listener (automation) | term | [`automation/json-rpc`](../automation/json-rpc.md) |
| listener (make) | term | [Sound](../make/sound.md) |
| `ListsEveryHostFunction` | identifier | [`scripting/host-api`](../scripting/host-api.md) |
| live line | term | [Inspectors from reflection](../editor-ui/inspectors.md) |
| live lines | term | Same as live line: [Inspectors from reflection](../editor-ui/inspectors.md). |
| lm | term | Same as Lumen: [Light by the numbers: radiometric and photometric units](../light/units-exposure.md). |
| load factor | term | [Data structures I: arrays, lists, hash maps and their cost](../basics/data-structures.md) |
| Load mode | term | [Clips, voices and sources](../audio/clips-voices-sources.md) |
| `LoadBeforeStart` | term | [Worlds meet physics and scripts](../worlds/physics-scripts.md) |
| Loader | term | [Loading without stalling](../assets/loading.md) |
| Loading scene | term | [The runtime](../worlds/runtime.md) Used in [Exporting and shipping](../make/export.md). |
| `LoadingScreen::OnUpdate` | identifier | [Levels, loading screens and save files](../make/levels-saves.md) |
| Lobe widening | term | [Lights with size: sized highlights and area lights](../light/area-lights.md) |
| Local | term | [Skeletons and forward kinematics](../animation/skeletons.md) |
| local avoidance | term | [`appendix/game-ai`](../appendix/game-ai.md) |
| local position | term | [Positions, rotations and units](../make/transforms-units.md) |
| local space | term | [`basics/math-matrices`](../basics/math-matrices.md) |
| Local transform | term | [`basics/math-matrices`](../basics/math-matrices.md) |
| local variable | term | [`basics/programming-2`](../basics/programming-2.md) |
| lock | term | [Threads, atomics and races](../basics/threads.md) |
| lock-free | term | [Threads, atomics and races](../basics/threads.md) |
| lockstep | term | Same as deterministic lockstep: [Networking for games, in general](../appendix/networking.md). |
| `LOD` | term | Same as Level of detail: [Levels of detail](../draw/lod.md). |
| `LOD cross-fade` | term | [Levels of detail](../draw/lod.md) |
| `LOD error` | term | [Levels of detail](../draw/lod.md) |
| `LOD record` | term | [`draw/gpu-driven`](../draw/gpu-driven.md) |
| log | term | [Installing Strata and the C++ build tools](../start/install.md) |
| log level | term | [Ownership, errors and logging in Strata](../core/conventions.md) |
| log levels | term | Same as log level: [Ownership, errors and logging in Strata](../core/conventions.md). |
| logarithm | term | [Numbers in a computer: binary, integers, floating point and precision](../basics/numbers.md) |
| logger | term | [Ownership, errors and logging in Strata](../core/conventions.md) |
| loggers | term | Same as logger: [Ownership, errors and logging in Strata](../core/conventions.md). |
| logical device | term | [Vulkan, NVRHI, the graphics device and the Renderer's services](../gpu/vulkan-nvrhi.md) |
| logical operator | term | [Programming from zero I: values, variables, expressions and decisions](../basics/programming-1.md) |
| Look-dev | term | [The look-dev harness](../engineering/look-dev.md) |
| Look-dev harness | term | [The look-dev harness](../engineering/look-dev.md) |
| loop | term | [`basics/programming-2`](../basics/programming-2.md) |
| Loopback | term | [`automation/json-rpc`](../automation/json-rpc.md) |
| Loose grid | term | [Bounding volumes, frustums and the spatial index](../draw/bounds-culling.md) |
| low-discrepancy sequence | term | [Chance: probability, noise, integrals and Monte Carlo](../basics/math-probability.md) |
| `LRU` | term | [Residency, eviction and pins](../assets/residency.md) |
| `LRU eviction` | term | [Text: fonts, shaping and signed distance fields](../gpu/text.md) |
| `LTC` | term | [Lights with size: sized highlights and area lights](../light/area-lights.md) |
| Luma | term | [`image/spatial-aa`](../image/spatial-aa.md) |
| Lumen | term | [Light by the numbers: radiometric and photometric units](../light/units-exposure.md) |
| luminance | term | [`basics/color`](../basics/color.md) |
| Luminance (Y) | term | [`basics/color`](../basics/color.md) |
| `LUT` | term | [Earth's atmosphere and aerial perspective](../light/atmosphere.md) |
| Lux | term | [Light by the numbers: radiometric and photometric units](../light/units-exposure.md) Used in [Lighting a scene: sun, sky and exposure](../make/lighting.md). |
| lx | term | Same as Lux: [Light by the numbers: radiometric and photometric units](../light/units-exposure.md). |
| machine code | term | [`basics/computer`](../basics/computer.md) |
| machine instruction | term | [`basics/computer`](../basics/computer.md) |
| macro | term | [Modern C++ as Strata uses it: move semantics, constexpr, optional, variant, span and concepts](../basics/cpp-modern.md) |
| magic number | term | [Bytes in files and memory: layouts, byte order and text encodings](../basics/bytes.md) |
| magic numbers | term | Same as magic number: [Bytes in files and memory: layouts, byte order and text encodings](../basics/bytes.md). |
| magnitude | term | Same as vector length: [Vectors: length, direction, dot and cross products](../basics/math-vectors.md). |
| `main` | identifier | [How Strata is put together: programs, libraries, modules and layers](../core/map.md) Also in [`automation/mcp`](../automation/mcp.md). |
| main loop | term | Same as game loop: [What a game engine is: one frame, start to finish](../start/what-an-engine-is.md). |
| main memory | term | Same as memory: [`basics/computer`](../basics/computer.md). |
| main thread | term | [Threads, atomics and races](../basics/threads.md) |
| Main-thread queue | term | [The frame loop](../core/frame-loop.md) |
| `MakeBodySetup` | identifier | [From entities to bodies: records, shapes, mesh colliders](../physics/building-bodies.md) |
| `MakeScriptCMakeLists` | identifier | [Building and shipping script modules](../make/script-builds.md) |
| `MakeToolResult` | identifier | [`automation/mcp`](../automation/mcp.md) |
| Manifest | term | [Exporting and shipping](../make/export.md) |
| Manifold | term | [Collision detection: shapes, broad phase and narrow phase](../physics/collision-detection.md) |
| mantissa | term | Same as significand: [Numbers in a computer: binary, integers, floating point and precision](../basics/numbers.md). |
| map | term | [Input and input actions](../make/input.md) |
| Margin | term | [Rects, anchors and layout](../ui/layout.md) |
| `MarkModified` | term | Same as patch: [The scene graph: hierarchy, transforms and the transform contract](../world/scene-graph.md). |
| `MarkModified` | term | Same as patch: [The scene graph: hierarchy, transforms and the transform contract](../world/scene-graph.md). |
| mask | term | [Physics for game makers](../make/physics.md) |
| mask bits | term | Same as Category bits: [Collision layers](../physics/collision-layers.md). |
| mass | term | [Change over time: rates, accumulation, Euler steps and Newton's laws](../basics/math-change.md) |
| Material | term | [Materials](../make/materials.md) |
| material table | term | Same as Mesh table: [`draw/render-scene-gpu`](../draw/render-scene-gpu.md). |
| Material-free instancing | term | [Batching and instancing](../draw/batching.md) |
| `Material::FromJson` | identifier | [From a material file to the shader: the material record and its textures](../light/material-data.md) |
| `MaterialGPU::Build` | identifier | [From a material file to the shader: the material record and its textures](../light/material-data.md) |
| `MaterialGPU::GetAbsorption` | identifier | [From a material file to the shader: the material record and its textures](../light/material-data.md) |
| `MaterialGPU::GetDielectricF0` | identifier | [From a material file to the shader: the material record and its textures](../light/material-data.md) |
| matrix | term | [`basics/math-matrices`](../basics/math-matrices.md) |
| matrix multiplication | term | [`basics/math-matrices`](../basics/math-matrices.md) |
| matrix order | term | [`basics/math-matrices`](../basics/math-matrices.md) |
| max distance | term | [Sound in space](../audio/spatial.md) |
| `MaxBodiesInRadius` | term | [Worlds meet physics and scripts](../worlds/physics-scripts.md) |
| `MayDefer` | term | [Commands that take frames](../editor/deferred-commands.md) |
| `MCP` | term | [`automation/mcp`](../automation/mcp.md) |
| `MCP client` | term | [`automation/mcp`](../automation/mcp.md) |
| `McpServer::HandleToolsCall` | identifier | [`automation/mcp`](../automation/mcp.md) |
| `McpToolsets::FirstSentence` | identifier | [`automation/mcp`](../automation/mcp.md) |
| `McpToolsets::GetGroupToolset` | identifier | [`automation/mcp`](../automation/mcp.md) |
| Measure | term | [Rects, anchors and layout](../ui/layout.md) |
| `Measure` | identifier | [Measuring performance honestly: noise, percentiles, budgets and the perf lab](../engineering/perf-lab.md) |
| `MeasurePanel` | identifier | [`editor-ui/ui-testing`](../editor-ui/ui-testing.md) |
| Median | term | [Measuring the frame: the frame profiler, Tracy and the method](../core/profiling.md) |
| member | term | [`basics/programming-2`](../basics/programming-2.md) |
| member function | term | [`basics/programming-3`](../basics/programming-3.md) |
| Memento | term | [Undo and redo](../editor/undo.md) |
| memory | term | [`basics/computer`](../basics/computer.md) |
| memory address | term | [`basics/computer`](../basics/computer.md) |
| Memory asset | term | [Loading without stalling](../assets/loading.md) |
| memory bandwidth | term | Same as bandwidth: [`gpu/how-a-gpu-frame-works`](../gpu/how-a-gpu-frame-works.md). |
| memory fence | term | Same as Fence (basics): [Threads, atomics and races](../basics/threads.md). |
| memory leak | term | [`basics/cpp-memory`](../basics/cpp-memory.md) |
| memory order | term | [Threads, atomics and races](../basics/threads.md) |
| memory ordering | term | Same as memory order: [Threads, atomics and races](../basics/threads.md). |
| Memory pool | term | [Residency, eviction and pins](../assets/residency.md) |
| Merge (basics) | term | [Version control with git](../basics/git.md) |
| Merge (editor) | term | [Undo and redo](../editor/undo.md) |
| Merge (indirect) | term | [`indirect/gi-cascades`](../indirect/gi-cascades.md) |
| merge conflict | term | [Version control with git](../basics/git.md) |
| merge conflicts | term | Same as merge conflict: [Version control with git](../basics/git.md). |
| merge key | term | Same as Merge (editor): [Undo and redo](../editor/undo.md). |
| Merge mode | term | [The design system: theme, fonts, icons](../editor-ui/design-system.md) |
| mesh collider | term | [Project: a third-person platformer](../make/project-platformer.md) |
| Mesh layout | term | [The render scene: persistent proxies](../draw/render-scene.md) |
| Mesh provider | term | [From entities to bodies: records, shapes, mesh colliders](../physics/building-bodies.md) |
| Mesh table | term | [`draw/render-scene-gpu`](../draw/render-scene-gpu.md) |
| `MessagePack` | term | [Scene documents: text, streams and the cooked form](../world/serialization.md) |
| `.meta` file | term | [Handles, .meta files and sub-assets](../assets/handles-meta.md) |
| Metallic | term | [Strata's material model](../light/materials.md) |
| Metering | term | [Exposure: camera, eye and meter](../image/exposure.md) |
| method | term | Same as member function: [`basics/programming-3`](../basics/programming-3.md). |
| Metric | term | [Measuring performance honestly: noise, percentiles, budgets and the perf lab](../engineering/perf-lab.md) |
| Microfacet | term | [How surfaces reflect light: the reflection equation and microfacets](../light/reflectance.md) |
| Middle gray | term | [Exposure: camera, eye and meter](../image/exposure.md) |
| Mie scattering | term | [Earth's atmosphere and aerial perspective](../light/atmosphere.md) |
| Min distance | term | [Sound in space](../audio/spatial.md) |
| Min/max sampler | term | [Occlusion culling](../draw/occlusion.md) |
| Mip | term | [`assets/textures`](../assets/textures.md) |
| Mip chain | term | [`assets/textures`](../assets/textures.md) |
| mip level | term | Same as Mip: [`assets/textures`](../assets/textures.md). |
| Mip streaming | term | [Mip streaming](../draw/mip-streaming.md) |
| Mip tail | term | [Mip streaming](../draw/mip-streaming.md) |
| mired | term | Same as Color temperature: [White balance, grading and lookup tables](../image/grading.md). |
| Mirrored transform | term | [Mirrors, normals and camera-relative positions](../draw/mirrors-camera-relative.md) |
| miss rule | term | [`indirect/gi-cascades`](../indirect/gi-cascades.md) |
| Mitchell filter | term | [`assets/texture-cooking`](../assets/texture-cooking.md) |
| Mixed value | term | [Inspectors from reflection](../editor-ui/inspectors.md) |
| Mixer | term | [Sound inside a computer](../audio/sound-in-a-computer.md) |
| Mixing period | term | [Sound inside a computer](../audio/sound-in-a-computer.md) |
| `MLAA` | term | [`image/spatial-aa`](../image/spatial-aa.md) |
| modal | term | [Dear ImGui from first principles](../editor-ui/imgui.md) |
| Model | term | [Prefabs: the data model](../world/prefabs.md) |
| Model Context Protocol | term | Same as `MCP`: [`automation/mcp`](../automation/mcp.md). |
| model space (of a pose) | term | [Skeletons and forward kinematics](../animation/skeletons.md) |
| `modes (BC7)` | term | Same as Endpoints: [`assets/texture-cooking`](../assets/texture-cooking.md). |
| Module description | term | [`scripting/abi-sdk`](../scripting/abi-sdk.md) |
| module library | term | Same as static library: [How a C++ program is built: from two files by hand to CMake](../basics/build.md). |
| moire | term | Same as moiré: [Sampling, aliasing and filtering](../basics/signals.md). |
| moiré | term | [Sampling, aliasing and filtering](../basics/signals.md) |
| `MoltenVK` | term | [Vulkan, NVRHI, the graphics device and the Renderer's services](../gpu/vulkan-nvrhi.md) |
| momentum | term | [Change over time: rates, accumulation, Euler steps and Newton's laws](../basics/math-change.md) |
| Monte Carlo integration | term | [Chance: probability, noise, integrals and Monte Carlo](../basics/math-probability.md) |
| Morph target (blend shape) | term | [The animation problem](../animation/problem.md) |
| `morphological AA` | term | Same as `MLAA`: [`image/spatial-aa`](../image/spatial-aa.md). |
| Morton order | term | [Numbers in a computer: binary, integers, floating point and precision](../basics/numbers.md) |
| Motion history | term | [Motion vectors and motion history](../draw/motion-vectors.md) |
| Motion vector | term | [Motion vectors and motion history](../draw/motion-vectors.md) |
| Motion vectors | term | Same as Motion vector: [Motion vectors and motion history](../draw/motion-vectors.md). |
| Mouse delta | term | [The mouse, the cursor and the game view](../input/mouse-cursor.md) |
| move semantics | term | [Modern C++ as Strata uses it: move semantics, constexpr, optional, variant, span and concepts](../basics/cpp-modern.md) |
| `MoveController` | identifier | [Character controllers](../physics/character-controllers.md) |
| Mover (box3d) | term | [Character controllers](../physics/character-controllers.md) |
| `MSAA` | term | [`image/spatial-aa`](../image/spatial-aa.md) |
| `Multi-bounce AO` | term | [Ambient occlusion without history](../indirect/ao.md) |
| Multi-config generator | term | [Building Strata](../engineering/building.md) |
| `Multi-select (BeginMultiSelect)` | term | [Lists that scale](../editor-ui/lists.md) |
| multiple scattering | term | [Earth's atmosphere and aerial perspective](../light/atmosphere.md) |
| mutex | term | [Threads, atomics and races](../basics/threads.md) |
| Mutual authentication | term | [The security model](../automation/security.md) |
| mutual exclusion | term | Same as mutex: [Threads, atomics and races](../basics/threads.md). |
| mutually exclusive | term | Same as Exclusive (cases): [Chance: probability, noise, integrals and Monte Carlo](../basics/math-probability.md). |
| `Nagle's algorithm` | term | [`automation/json-rpc`](../automation/json-rpc.md) |
| namespace | term | [Programming from zero I: values, variables, expressions and decisions](../basics/programming-1.md) |
| `NaN` | term | [Numbers in a computer: binary, integers, floating point and precision](../basics/numbers.md) |
| Narrow phase | term | [Collision detection: shapes, broad phase and narrow phase](../physics/collision-detection.md) |
| `NAT` | term | Same as `NAT traversal`: [Networking for games, in general](../appendix/networking.md). |
| `NAT traversal` | term | [Networking for games, in general](../appendix/networking.md) |
| Nav cursor | term | [Dear ImGui from first principles](../editor-ui/imgui.md) |
| nav mesh | term | Same as navigation mesh: [`appendix/game-ai`](../appendix/game-ai.md). |
| navigation mesh | term | [`appendix/game-ai`](../appendix/game-ai.md) |
| navigation meshes | term | Same as navigation mesh: [`appendix/game-ai`](../appendix/game-ai.md). |
| navmesh | term | Same as navigation mesh: [`appendix/game-ai`](../appendix/game-ai.md). |
| `NDC` | term | Same as normalized device coordinates: [Cameras and projection: perspective, homogeneous coordinates and depth](../basics/math-projection.md). |
| near clip plane | term | Same as near plane: [Cameras and projection: perspective, homogeneous coordinates and depth](../basics/math-projection.md). |
| Near field | term | [Depth of field](../image/depth-of-field.md) |
| near plane | term | [Cameras and projection: perspective, homogeneous coordinates and depth](../basics/math-projection.md) |
| nearest rank | term | Same as Median: [Measuring the frame: the frame profiler, Tracy and the method](../core/profiling.md). |
| neighbor max | term | Same as Tile max: [Motion blur](../image/motion-blur.md). |
| Neighborhood clamp | term | [Temporal anti-aliasing](../image/taa.md) |
| Network thread | term | [`automation/rpc-server`](../automation/rpc-server.md) |
| Newton's laws | term | Same as Newton's laws of motion: [Change over time: rates, accumulation, Euler steps and Newton's laws](../basics/math-change.md). |
| Newton's laws of motion | term | [Change over time: rates, accumulation, Euler steps and Newton's laws](../basics/math-change.md) |
| nfd | term | [The widget kit](../editor-ui/widget-kit.md) |
| Nine-slice | term | [`ui/drawing`](../ui/drawing.md) |
| Nine-slice (sliced image) | term | [`make/hud`](../make/hud.md) |
| Nit | term | [Light by the numbers: radiometric and photometric units](../light/units-exposure.md) |
| nits | term | Same as Lux: [Light by the numbers: radiometric and photometric units](../light/units-exposure.md). |
| nlerp | term | [Rotations and quaternions](../basics/math-rotations.md) |
| no-gpu | term | [Sessions, discovery and launching](../automation/sessions.md) |
| No-op step | term | [Undo and redo](../editor/undo.md) |
| node | term | [Data structures I: arrays, lists, hash maps and their cost](../basics/data-structures.md) |
| Node graph | term | [The audio engine](../audio/engine.md) |
| node handle | term | [Generic C++: templates, lambdas and the standard containers](../basics/cpp-generic.md) |
| node handles | term | Same as node handle: [Generic C++: templates, lambdas and the standard containers](../basics/cpp-generic.md). |
| noise | term | [Chance: probability, noise, integrals and Monte Carlo](../basics/math-probability.md) |
| Noise modulation | term | [Encoding, dithering and grain](../image/encoding.md) |
| Non-blocking I/O | term | [`automation/json-rpc`](../automation/json-rpc.md) |
| Nonce | term | [The security model](../automation/security.md) |
| norm | term | Same as vector length: [Vectors: length, direction, dot and cross products](../basics/math-vectors.md). |
| Normal bias | term | [`indirect/gi-cascades`](../indirect/gi-cascades.md) |
| Normal map | term | [`assets/textures`](../assets/textures.md) |
| Normal matrix | term | [Bases, determinants and normals: orthonormal frames, tangent space, mirrors and the inverse transpose](../basics/math-bases.md) |
| normal offset | term | [Shadow mapping from first principles](../light/shadow-basics.md) |
| normal vector | term | Same as surface normal: [Vectors: length, direction, dot and cross products](../basics/math-vectors.md). |
| normalization | term | [Vectors: length, direction, dot and cross products](../basics/math-vectors.md) |
| normalize | term | Same as normalization: [Vectors: length, direction, dot and cross products](../basics/math-vectors.md). |
| normalized | term | Same as normalization: [Vectors: length, direction, dot and cross products](../basics/math-vectors.md). |
| normalized device coordinates | term | [Cameras and projection: perspective, homogeneous coordinates and depth](../basics/math-projection.md) |
| Normalized time | term | [Time, loops and events](../animation/time-events.md) |
| normalizing | term | Same as normalization: [Vectors: length, direction, dot and cross products](../basics/math-vectors.md). |
| notification | term | Same as Toast: [Status bar, toasts and idle throttling](../editor-ui/status.md). |
| Notification group | term | [Status bar, toasts and idle throttling](../editor-ui/status.md) |
| notifications/progress | term | Same as Progress token: [`automation/mcp`](../automation/mcp.md). |
| notifier | term | Same as Self-pipe trick: [`automation/rpc-server`](../automation/rpc-server.md). |
| `NotifyCommandOutcome` | identifier | [Status bar, toasts and idle throttling](../editor-ui/status.md) |
| Null device | term | [The audio engine](../audio/engine.md) |
| null pointer | term | [`basics/programming-3`](../basics/programming-3.md) |
| numerical integration | term | [Change over time: rates, accumulation, Euler steps and Newton's laws](../basics/math-change.md) |
| `NVRHI` | term | [Vulkan, NVRHI, the graphics device and the Renderer's services](../gpu/vulkan-nvrhi.md) |
| Nyquist frequency | term | Same as Nyquist limit: [Sampling, aliasing and filtering](../basics/signals.md). |
| Nyquist limit | term | [Sampling, aliasing and filtering](../basics/signals.md) |
| `OBB` | term | Same as oriented bounding box: [Geometry for engines: rays, planes, boxes and intersection tests](../basics/math-geometry.md). |
| object | term | [`basics/programming-3`](../basics/programming-3.md) |
| object file | term | [How a C++ program is built: from two files by hand to CMake](../basics/build.md) |
| object lifetime | term | Same as lifetime: [`basics/cpp-memory`](../basics/cpp-memory.md). |
| object pool | term | [Patterns for game code: state machines, managers and object pools](../make/patterns.md) |
| object pools | term | Same as object pool: [Patterns for game code: state machines, managers and object pools](../make/patterns.md). |
| obscurance | term | [Ambient occlusion without history](../indirect/ao.md) |
| Occlusion culling | term | [Occlusion culling](../draw/occlusion.md) |
| occupancy | term | [`indirect/gi-cascades`](../indirect/gi-cascades.md) |
| Octahedral encoding | term | [Directions on a sphere: solid angles, spherical harmonics and octahedral maps](../basics/math-sphere.md) |
| octahedral map | term | [Directions on a sphere: solid angles, spherical harmonics and octahedral maps](../basics/math-sphere.md) |
| octahedral mapping | term | Same as octahedral map: [Directions on a sphere: solid angles, spherical harmonics and octahedral maps](../basics/math-sphere.md). |
| `ODR` | term | [`scripting/abi-sdk`](../scripting/abi-sdk.md) |
| off by one | term | Same as off-by-one mistake: [`basics/programming-2`](../basics/programming-2.md). |
| off-by-one mistake | term | [`basics/programming-2`](../basics/programming-2.md) |
| Offset allocator | term | Same as Range allocator: [`gpu/geometry-pool`](../gpu/geometry-pool.md). |
| one-definition rule | term | Same as `ODR`: [`scripting/abi-sdk`](../scripting/abi-sdk.md). |
| one-paragraph design | term | [Planning a small game: the core loop, scope, prototype and playtest](../make/designing-a-game.md) |
| One-shot | term | [The audio engine](../audio/engine.md) Used in [Sound](../make/sound.md). |
| Open share | term | [`indirect/gi-cascades`](../indirect/gi-cascades.md) |
| operating system | term | [Installing Strata and the C++ build tools](../start/install.md) |
| operator | term | [Programming from zero I: values, variables, expressions and decisions](../basics/programming-1.md) |
| operator overloading | term | [C++ classes in depth: inheritance, virtual calls and interfaces](../basics/cpp-classes.md) |
| optical depth | term | [Earth's atmosphere and aerial perspective](../light/atmosphere.md) |
| optimization | term | [How a C++ program is built: from two files by hand to CMake](../basics/build.md) |
| optimize | term | Same as optimization: [How a C++ program is built: from two files by hand to CMake](../basics/build.md). |
| optimized | term | Same as optimization: [How a C++ program is built: from two files by hand to CMake](../basics/build.md). |
| optimizes | term | Same as optimization: [How a C++ program is built: from two files by hand to CMake](../basics/build.md). |
| optimizing | term | Same as optimization: [How a C++ program is built: from two files by hand to CMake](../basics/build.md). |
| optional value | term | [`basics/programming-3`](../basics/programming-3.md) |
| orbit | term | [The editor camera and viewport state](../editor/camera-viewport.md) |
| Orbit camera | term | [The editor camera and viewport state](../editor/camera-viewport.md) |
| ordered dither | term | [Sampling, aliasing and filtering](../basics/signals.md) |
| Ordered dither (4x4 Bayer order) | term | Same as ordered dither: [Sampling, aliasing and filtering](../basics/signals.md). |
| ordered float | term | [Many lights: culling and clustered forward shading](../light/many-lights.md) |
| ordered map | term | [`basics/trees-graphs`](../basics/trees-graphs.md) |
| ordered maps | term | Same as ordered map: [`basics/trees-graphs`](../basics/trees-graphs.md). |
| oriented bounding box | term | [Geometry for engines: rays, planes, boxes and intersection tests](../basics/math-geometry.md) |
| origin | term | [Vectors: length, direction, dot and cross products](../basics/math-vectors.md) |
| Origin rebasing | term | [Mirrors, normals and camera-relative positions](../draw/mirrors-camera-relative.md) |
| orthographic projection | term | [Cameras and projection: perspective, homogeneous coordinates and depth](../basics/math-projection.md) |
| orthonormal basis | term | [Bases, determinants and normals: orthonormal frames, tangent space, mirrors and the inverse transpose](../basics/math-bases.md) |
| orthonormal frame | term | Same as orthonormal basis: [Bases, determinants and normals: orthonormal frames, tangent space, mirrors and the inverse transpose](../basics/math-bases.md). |
| `OS` | term | Same as operating system: [Installing Strata and the C++ build tools](../start/install.md). |
| `OTTO` | term | Same as `TrueType`: [Text: fonts, shaping and signed distance fields](../gpu/text.md). |
| Outdated | term | [How prefab instances stay linked](../editor/prefab-instances.md) |
| Outdated instance | term | [How prefab instances stay linked](../editor/prefab-instances.md) Used in [Prefabs](../make/prefabs.md). |
| `Outpost::RequestCaptures` | identifier | [Sky light, ambient occlusion and reflections in your game](../make/reflections.md) |
| `Outpost::SetProbes` | identifier | [Sky light, ambient occlusion and reflections in your game](../make/reflections.md) |
| `Outpost::SwitchProbes` | identifier | [Sky light, ambient occlusion and reflections in your game](../make/reflections.md) |
| Output device | term | [The audio engine](../audio/engine.md) |
| outset (gamut compression) | term | Same as Inset: [Tone mapping and the Filmic curve](../image/tone-mapping.md). |
| overflow | term | Same as integer overflow: [Numbers in a computer: binary, integers, floating point and precision](../basics/numbers.md). |
| overlap | term | [`indirect/gi-cascades`](../indirect/gi-cascades.md) Used in [Physics for game makers](../make/physics.md). |
| Overlay (core) | term | [Windows, events and layers](../core/windows-events.md) |
| Overlay (gpu) | term | [Overlays, debug drawing and gizmos](../gpu/debug-drawing.md) |
| Overlay pass | term | [Overlays, debug drawing and gizmos](../gpu/debug-drawing.md) |
| Override (prefab) | term | Same as Prefab (world): [Prefabs: the data model](../world/prefabs.md). |
| ownership | term | [`basics/cpp-memory`](../basics/cpp-memory.md) |
| Ozone absorption | term | [Earth's atmosphere and aerial perspective](../light/atmosphere.md) |
| p-bits | term | Same as Endpoints: [`assets/texture-cooking`](../assets/texture-cooking.md). |
| p95 | term | Same as Median: [Measuring the frame: the frame profiler, Tracy and the method](../core/profiling.md). |
| pack | term | [Exporting and shipping](../make/export.md) |
| packet loss | term | [Networking for games, in general](../appendix/networking.md) |
| padding | term | [Bytes in files and memory: layouts, byte order and text encodings](../basics/bytes.md) |
| page | term | [Text: fonts, shaping and signed distance fields](../gpu/text.md) |
| pan | term | [The editor camera and viewport state](../editor/camera-viewport.md) |
| Pancaking | term | [Shadow mapping from first principles](../light/shadow-basics.md) |
| Panel | term | [The editor shell: host, layer, docking and panels](../editor-ui/shell.md) |
| panel registry | term | Same as Panel: [The editor shell: host, layer, docking and panels](../editor-ui/shell.md). |
| Panning | term | [Sound in space](../audio/spatial.md) |
| `ParallelFor` | term | [Threads and the job system](../core/jobs.md) |
| parallelism | term | [Threads, atomics and races](../basics/threads.md) |
| parameter | term | [`basics/programming-2`](../basics/programming-2.md) Used in [Animation for game makers](../make/animation.md). |
| parent class | term | Same as base class: [`basics/programming-3`](../basics/programming-3.md). |
| Parked body | term | [Physics at scale and in streaming worlds](../physics/scale-streaming.md) |
| `ParkStaticBody` | identifier | [Physics at scale and in streaming worlds](../physics/scale-streaming.md) |
| parser | term | [`basics/data-formats`](../basics/data-formats.md) |
| parsers | term | Same as parser: [`basics/data-formats`](../basics/data-formats.md). |
| Part (of a prefab) | term | [Prefabs: the data model](../world/prefabs.md) |
| Part version | term | [How prefab instances stay linked](../editor/prefab-instances.md) |
| Partial load | term | [Mip streaming](../draw/mip-streaming.md) |
| partially bound | term | Same as Update-after-bind: [Pipelines and binding: layouts, registers and bindless](../gpu/binding.md). |
| patch | term | [The scene graph: hierarchy, transforms and the transform contract](../world/scene-graph.md) |
| Patch (basics) | term | [Version control with git](../basics/git.md) |
| Patch pack | term | [Asset packs, export and patches](../assets/packs-export.md) |
| path | term | [The tools: the terminal, files and a code editor](../basics/tools.md) |
| `PauseMenu::OnUpdate` | identifier | [Patterns for game code: state machines, managers and object pools](../make/patterns.md) |
| `PBR` | term | [Materials](../make/materials.md) |
| `PCF` | term | [Shadow mapping from first principles](../light/shadow-basics.md) |
| `PCG32` | term | [Chance: probability, noise, integrals and Monte Carlo](../basics/math-probability.md) |
| pch | term | Same as Precompiled header: [Compiler flags, compile time and portability](../engineering/flags-portability.md). |
| `PCM` | term | [Sound inside a computer](../audio/sound-in-a-computer.md) |
| `PCSS` | term | [`light/sun-shadows-2`](../light/sun-shadows-2.md) |
| `PDB` | term | [From an address to a file and line](../scripting/symbolization.md) |
| `PE resources` | term | [A game's identity: the manifest, icons and platform files](../worlds/game-identity.md) |
| pending | term | [`indirect/gi-cascades`](../indirect/gi-cascades.md) |
| penumbra | term | Same as Umbra: [`light/sun-shadows-2`](../light/sun-shadows-2.md). |
| Per-user cache | term | [Third-party code and pinned tools](../engineering/third-party.md) |
| Percentile window | term | [Exposure: camera, eye and meter](../image/exposure.md) |
| Perceptual roughness | term | [Strata's material model](../light/materials.md) |
| Perf lab | term | [Measuring performance honestly: noise, percentiles, budgets and the perf lab](../engineering/perf-lab.md) |
| Perf log | term | [The runtime](../worlds/runtime.md) |
| Permissive | term | [Third-party code and pinned tools](../engineering/third-party.md) |
| Persistent scene | term | [Why levels must stream](../worlds/why-streaming.md) |
| perspective divide | term | [Cameras and projection: perspective, homogeneous coordinates and depth](../basics/math-projection.md) |
| perspective division | term | Same as perspective divide: [Cameras and projection: perspective, homogeneous coordinates and depth](../basics/math-projection.md). |
| perspective projection | term | [Cameras and projection: perspective, homogeneous coordinates and depth](../basics/math-projection.md) |
| peter-panning | term | [Shadow mapping from first principles](../light/shadow-basics.md) |
| Phase function | term | [Earth's atmosphere and aerial perspective](../light/atmosphere.md) |
| phase matching | term | Same as Sync markers: [Blending and cross-fades](../animation/blending.md). |
| Physical atmosphere | term | [Earth's atmosphere and aerial perspective](../light/atmosphere.md) |
| Physical device | term | [Vulkan, NVRHI, the graphics device and the Renderer's services](../gpu/vulkan-nvrhi.md) |
| Physics capacity | term | Same as Capacity: [Physics at scale and in streaming worlds](../physics/scale-streaming.md). |
| `PhysicsSystem::DispatchCollisionEvents` | identifier | [Contacts and triggers](../physics/contacts-triggers.md) |
| `PhysicsWorld::GetEffectiveContactHertz` | identifier | [Rigid body dynamics: integration, contacts, solvers, sleep and continuous collision](../physics/dynamics.md) Also in [Tuning and measuring](../physics/tuning.md). |
| `PhysicsWorld::Raycast` | identifier | [Physics queries](../physics/queries.md) |
| `PhysicsWorld::ResolveCapacities` | identifier | [Physics at scale and in streaming worlds](../physics/scale-streaming.md) |
| `PhysicsWorld::SetLayerCollisionMasks` | identifier | [Collision layers](../physics/collision-layers.md) |
| pi | term | [Vectors: length, direction, dot and cross products](../basics/math-vectors.md) |
| Picking | term | [The Scene view](../editor-ui/scene-view.md) |
| Pill | term | [The widget kit](../editor-ui/widget-kit.md) |
| Pin | term | [Residency, eviction and pins](../assets/residency.md) |
| ping-pong | term | [Temporal anti-aliasing](../image/taa.md) |
| Pinning | term | [Sessions, discovery and launching](../automation/sessions.md) |
| pipe | term | [The tools: the terminal, files and a code editor](../basics/tools.md) |
| `Pipeline (PSO)` | term | [Pipelines and binding: layouts, registers and bindless](../gpu/binding.md) |
| Pipeline key | term | [Pipelines and binding: layouts, registers and bindless](../gpu/binding.md) |
| `PipelineKey` | term | Same as Pipeline key: [Pipelines and binding: layouts, registers and bindless](../gpu/binding.md). |
| Pitch | term | [Clips, voices and sources](../audio/clips-voices-sources.md) |
| pitch angle | term | [Rotations and quaternions](../basics/math-rotations.md) |
| Pivot (editor) | term | [The editor camera and viewport state](../editor/camera-viewport.md) |
| Pivot (ui) | term | [Rects, anchors and layout](../ui/layout.md) |
| pixel | term | [What a game engine is: one frame, start to finish](../start/what-an-engine-is.md) |
| Pixel snapping | term | [`ui/drawing`](../ui/drawing.md) |
| pixels | term | [`editor-ui/ui-scale`](../editor-ui/ui-scale.md) |
| pixels per texel | term | Same as Texel density (light): [Sun shadows I: stable cascades](../light/sun-shadows-1.md). |
| Placeholder | term | [Text and text fields](../ui/text.md) |
| Placeholder bounds | term | [The render scene: persistent proxies](../draw/render-scene.md) |
| Placement ghost | term | [Placing content](../editor/placement.md) |
| Planckian locus | term | [White balance, grading and lookup tables](../image/grading.md) |
| plane | term | [Geometry for engines: rays, planes, boxes and intersection tests](../basics/math-geometry.md) |
| Play | term | [Play mode: the running copy](../editor/play-mode.md) Used in [Playing, testing and debugging](../make/play-test-debug.md). |
| Play mode | term | [Play mode: the running copy](../editor/play-mode.md) |
| play revision | term | [Animating only what is seen](../animation/culling.md) |
| play testing | term | Same as playtest: [Planning a small game: the core loop, scope, prototype and playtest](../make/designing-a-game.md). |
| Players' bindings | term | [Players' bindings inside the engine: the bindings file and capture](../input/rebinding.md) |
| Players' rows | term | [Quality settings and players' graphics options](../image/quality-settings.md) |
| `Playground::GetPointerRay` | identifier | [The math of moving things: vectors, directions, angles and smoothing](../make/gameplay-math.md) Also in [Cameras and projection: perspective, homogeneous coordinates and depth](../basics/math-projection.md). |
| `Playground::UpdateGrab` | identifier | [Physics queries](../physics/queries.md) |
| Playhead | term | [Time, loops and events](../animation/time-events.md) |
| playtest | term | [Planning a small game: the core loop, scope, prototype and playtest](../make/designing-a-game.md) |
| pointer | term | [`basics/programming-3`](../basics/programming-3.md) |
| Pointer capture | term | [Input devices and per-frame state](../input/devices-state.md) |
| pointer to a member | term | [Generic C++: templates, lambdas and the standard containers](../basics/cpp-generic.md) |
| Points | term | [`editor-ui/ui-scale`](../editor-ui/ui-scale.md) |
| Poisson disk sampling | term | [Chance: probability, noise, integrals and Monte Carlo](../basics/math-probability.md) |
| polar angle | term | [Directions on a sphere: solid angles, spherical harmonics and octahedral maps](../basics/math-sphere.md) |
| poll | term | [`automation/json-rpc`](../automation/json-rpc.md) |
| Poll function | term | [Commands that take frames](../editor/deferred-commands.md) |
| `PollCommandResult` | identifier | [Commands that take frames](../editor/deferred-commands.md) |
| Polling | term | [How input reaches a game: events, polling, edges and intents](../input/how-input-works.md) |
| Polling input | term | Same as Polling: [How input reaches a game: events, polling, edges and intents](../input/how-input-works.md). |
| polymorphism | term | [C++ classes in depth: inheritance, virtual calls and interfaces](../basics/cpp-classes.md) |
| `PopulateBasic3D` | identifier | [Opening projects and scenes: templates, background loads and migration](../editor/projects.md) |
| Popup | term | [Dear ImGui from first principles](../editor-ui/imgui.md) |
| Port | term | [`automation/json-rpc`](../automation/json-rpc.md) |
| Pose preview | term | [Edit-mode poses and previews](../animation/editor.md) |
| Posed bounds | term | [Skinned meshes in the renderer](../draw/skinned.md) |
| Positive vertex test | term | [Bounding volumes, frustums and the spatial index](../draw/bounds-culling.md) |
| post pass | term | [`image/spatial-aa`](../image/spatial-aa.md) |
| Post source | term | [Why images need post-processing, and Strata's post chain](../image/why-post.md) |
| `PostProcessMath::GetMotionBlurProfile` | identifier | [Motion blur](../image/motion-blur.md) |
| power | term | [Numbers in a computer: binary, integers, floating point and precision](../basics/numbers.md) |
| `power (CDL)` | term | Same as Slope: [White balance, grading and lookup tables](../image/grading.md). |
| `Power throttling (EcoQoS)` | term | [Talking to the operating system](../core/platform.md) |
| pre-commit review checklist | term | [The review checklist and the way a change lands](../engineering/contributing.md) |
| Pre-exposure | term | [Pre-exposure](../image/pre-exposure.md) |
| Pre-release suffix | term | [Packaging and releasing](../engineering/releasing.md) |
| precision | term | [Numbers in a computer: binary, integers, floating point and precision](../basics/numbers.md) |
| Precompiled header | term | [Compiler flags, compile time and portability](../engineering/flags-portability.md) |
| Prefab (make) | term | [Prefabs](../make/prefabs.md) |
| Prefab (world) | term | [Prefabs: the data model](../world/prefabs.md) |
| `PrefabEntityID` | term | Same as Prefab (world): [Prefabs: the data model](../world/prefabs.md). |
| preferences | term | [Opening projects and scenes: templates, background loads and migration](../editor/projects.md) |
| Preferred size | term | [Rects, anchors and layout](../ui/layout.md) |
| Prefetch (assets) | term | [References, closures, prefetch and loading screens](../assets/references.md) |
| Prefetch (make) | term | [Large worlds](../make/large-worlds.md) |
| Prefetch (scripting) | term | [The script system](../scripting/script-system.md) |
| Prefetch distance | term | [Asking for assets at draw time](../draw/asset-requests.md) |
| Prefiltered environment | term | [Image-based lighting and the split sum](../indirect/ibl.md) |
| prefiltering | term | [Sampling, aliasing and filtering](../basics/signals.md) |
| prefix | term | Same as Partial load: [Mip streaming](../draw/mip-streaming.md). |
| Prefix allocation | term | [Compute shaders: dispatches, thread groups, shared memory and atomics](../gpu/compute.md) |
| prefix sum | term | [Data structures I: arrays, lists, hash maps and their cost](../basics/data-structures.md) |
| prefix sums | term | Same as prefix sum: [Data structures I: arrays, lists, hash maps and their cost](../basics/data-structures.md). |
| Premultiplied alpha | term | [Transparency, clear coat and glass](../light/clearcoat-transmission.md) |
| Prepared scene | term | [Loading scenes: whole, additive and in slices](../world/sub-scenes.md) |
| Prepared start | term | [Loading scenes: whole, additive and in slices](../world/sub-scenes.md) |
| `PrepareSystems` | term | Same as Prepared start: [Loading scenes: whole, additive and in slices](../world/sub-scenes.md). |
| Prepass | term | [Screen-space reflections](../indirect/ssr.md) |
| preprocessor | term | [Modern C++ as Strata uses it: move semantics, constexpr, optional, variant, span and concepts](../basics/cpp-modern.md) |
| prerequisite | term | [How to read this book](../start/how-to-read.md) |
| Presence | term | [The activity journal and replays](../editor/journal.md) |
| Presence body | term | [Character controllers](../physics/character-controllers.md) |
| present | term | [`gpu/how-a-gpu-frame-works`](../gpu/how-a-gpu-frame-works.md) |
| Present mode | term | [`gpu/how-a-gpu-frame-works`](../gpu/how-a-gpu-frame-works.md) |
| Preset | term | [Building Strata](../engineering/building.md) |
| Pressed | term | [How input reaches a game: events, polling, edges and intents](../input/how-input-works.md) |
| Preview lighting | term | [Lights: the sun, points and spots](../light/lights.md) Used in [Lighting a scene: sun, sky and exposure](../make/lighting.md). |
| Primary camera | term | [`gpu/coordinates`](../gpu/coordinates.md) |
| Primary selection | term | [Lists that scale](../editor-ui/lists.md) |
| primer | term | [How to read this book](../start/how-to-read.md) |
| Priority | term | [Loading without stalling](../assets/loading.md) |
| Priority (jobs) | term | [Threads and the job system](../core/jobs.md) |
| priority queue | term | [`basics/trees-graphs`](../basics/trees-graphs.md) |
| priority queues | term | Same as priority queue: [`basics/trees-graphs`](../basics/trees-graphs.md). |
| Private copy | term | [Loading, calling and validating modules](../scripting/loading.md) |
| Private Use Area | term | [The design system: theme, fonts, icons](../editor-ui/design-system.md) |
| `PRNG` | term | Same as pseudo-random number generator: [Chance: probability, noise, integrals and Monte Carlo](../basics/math-probability.md). |
| probability | term | [Chance: probability, noise, integrals and Monte Carlo](../basics/math-probability.md) |
| probability density | term | [Chance: probability, noise, integrals and Monte Carlo](../basics/math-probability.md) |
| probability density function | term | Same as probability density: [Chance: probability, noise, integrals and Monte Carlo](../basics/math-probability.md). |
| probability distribution | term | [Chance: probability, noise, integrals and Monte Carlo](../basics/math-probability.md) |
| Probe | term | [`indirect/gi-cascades`](../indirect/gi-cascades.md) |
| Probe priority | term | [Reflection probes](../indirect/probes.md) |
| Problems panel | term | [Your first script](../make/first-script.md) |
| `ProblemsPanel::OnImGuiRender` | identifier | [Instrument panels](../editor-ui/instrument-panels.md) |
| `ProblemsPanel::OnUpdate` | identifier | [Instrument panels](../editor-ui/instrument-panels.md) |
| `ProblemsPanel::Rebuild` | identifier | [Instrument panels](../editor-ui/instrument-panels.md) |
| Procedural sky | term | [The sky as a light: sources, sun extraction and presets](../light/sky.md) |
| process | term | [`basics/computer`](../basics/computer.md) |
| Process start time | term | [The security model](../automation/security.md) |
| processor | term | [`basics/computer`](../basics/computer.md) |
| processor cache | term | Same as `CPU cache`: [`basics/computer`](../basics/computer.md). |
| processor core | term | [`basics/computer`](../basics/computer.md) |
| processor instruction | term | Same as machine instruction: [`basics/computer`](../basics/computer.md). |
| `ProcessStepEvents` | identifier | [Contacts and triggers](../physics/contacts-triggers.md) |
| Profiler (instrumenting vs sampling) | term | [Measuring the frame: the frame profiler, Tracy and the method](../core/profiling.md) |
| program | term | [`basics/computer`](../basics/computer.md) |
| programming language | term | [How to read this book](../start/how-to-read.md) |
| Progress token | term | [`automation/mcp`](../automation/mcp.md) |
| project | term | [Your first game](../start/first-game.md) |
| project migration | term | [Opening projects and scenes: templates, background loads and migration](../editor/projects.md) |
| Project pointer | term | [The security model](../automation/security.md) |
| Project scope | term | [Projects and settings](../world/projects-settings.md) |
| Projecting (basis functions) | term | [Directions on a sphere: solid angles, spherical harmonics and octahedral maps](../basics/math-sphere.md) |
| projection | term | [Cameras and projection: perspective, homogeneous coordinates and depth](../basics/math-projection.md) |
| projection matrix | term | [Cameras and projection: perspective, homogeneous coordinates and depth](../basics/math-projection.md) |
| projection onto basis functions | term | Same as Projecting (basis functions): [Directions on a sphere: solid angles, spherical harmonics and octahedral maps](../basics/math-sphere.md). |
| `ProjectThumbnail::Update` | identifier | [Thumbnails](../editor/thumbnails.md) |
| Propagate | term | [Prefabs: the data model](../world/prefabs.md) |
| Propagation | term | Same as Prefab (world): [Prefabs: the data model](../world/prefabs.md). |
| Property | term | [Reflection: one registration, many uses](../world/reflection.md) |
| property drawer | term | [Inspectors from reflection](../editor-ui/inspectors.md) |
| Property table | term | [Inspectors from reflection](../editor-ui/inspectors.md) |
| `PropertyInfo` | term | Same as Reflection: [Reflection: one registration, many uses](../world/reflection.md). |
| Prototype | term | [Prefabs: the data model](../world/prefabs.md) |
| Prototype (make) | term | [Planning a small game: the core loop, scope, prototype and playtest](../make/designing-a-game.md) |
| Provider (of poses) | term | [The Animation system](../animation/system.md) |
| provisional | term | [Measuring performance honestly: noise, percentiles, budgets and the perf lab](../engineering/perf-lab.md) |
| pruned export | term | [Exporting and shipping](../make/export.md) |
| Pruning | term | [Asset packs, export and patches](../assets/packs-export.md) |
| pseudo-random number generator | term | [Chance: probability, noise, integrals and Monte Carlo](../basics/math-probability.md) |
| pseudocode | term | [How to read this book](../start/how-to-read.md) |
| `PUA` | term | Same as Private Use Area: [The design system: theme, fonts, icons](../editor-ui/design-system.md). |
| Publish (assets) | term | [Loading without stalling](../assets/loading.md) |
| Publish (editor) | term | [Saving without stalling](../editor/saving.md) |
| pull model | term | [Sound inside a computer](../audio/sound-in-a-computer.md) |
| Punctual light | term | [Lights: the sun, points and spots](../light/lights.md) |
| pure virtual function | term | [C++ classes in depth: inheritance, virtual calls and interfaces](../basics/cpp-classes.md) |
| Push constants | term | [Pipelines and binding: layouts, registers and bindless](../gpu/binding.md) |
| `Push speed (contactSpeed)` | term | [Rigid body dynamics: integration, contacts, solvers, sleep and continuous collision](../physics/dynamics.md) |
| `PushBodies` | identifier | [Character controllers](../physics/character-controllers.md) |
| Pythagorean theorem | term | [Vectors: length, direction, dot and cross products](../basics/math-vectors.md) |
| Quad | term | [`ui/drawing`](../ui/drawing.md) |
| quadratic | term | Same as quadratic equation: [Geometry for engines: rays, planes, boxes and intersection tests](../basics/math-geometry.md). |
| quadratic equation | term | [Geometry for engines: rays, planes, boxes and intersection tests](../basics/math-geometry.md) |
| quadratic equations | term | Same as quadratic equation: [Geometry for engines: rays, planes, boxes and intersection tests](../basics/math-geometry.md). |
| Quadtree allocator | term | [Shadows of point and spot lights](../light/local-shadows.md) |
| Qualified name | term | [Input actions](../input/actions.md) |
| Quality preset | term | [Quality settings and players' graphics options](../image/quality-settings.md) |
| quantization | term | [`basics/color`](../basics/color.md) |
| quaternion | term | [Rotations and quaternions](../basics/math-rotations.md) Used in [Positions, rotations and units](../make/transforms-units.md). |
| quaternion conjugate | term | Same as conjugate: [Rotations and quaternions](../basics/math-rotations.md). |
| Query category | term | [Collision layers](../physics/collision-layers.md) |
| queue | term | [Data structures I: arrays, lists, hash maps and their cost](../basics/data-structures.md) |
| queue family | term | [`gpu/how-a-gpu-frame-works`](../gpu/how-a-gpu-frame-works.md) |
| Queue ownership transfer | term | [Staging and the upload queue](../gpu/upload-queue.md) |
| race | term | Same as race condition: [Threads, atomics and races](../basics/threads.md). |
| race condition | term | [Threads, atomics and races](../basics/threads.md) |
| Racily clean | term | [Importing: from source files to engine data](../assets/importing.md) |
| radial dead zone | term | Same as Dead zone: [Gamepads](../input/gamepads.md). |
| radian | term | [Vectors: length, direction, dot and cross products](../basics/math-vectors.md) |
| Radiance | term | [Light by the numbers: radiometric and photometric units](../light/units-exposure.md) |
| Radiance cascades | term | [`indirect/gi-cascades`](../indirect/gi-cascades.md) |
| radical inverse | term | [Temporal anti-aliasing](../image/taa.md) |
| Radiosity | term | [The indirect-light problem](../indirect/problem.md) |
| Radix sort | term | Same as `Radix sort (LSD)`: [Batching and instancing](../draw/batching.md). |
| `Radix sort (LSD)` | term | [Batching and instancing](../draw/batching.md) |
| `RadixSort` | identifier | [`basics/trees-graphs`](../basics/trees-graphs.md) |
| ragdoll | term | [What Strata's animation does not do yet](../animation/limits.md) |
| `RAII` | term | [`basics/cpp-memory`](../basics/cpp-memory.md) |
| `RAM` | term | Same as memory: [`basics/computer`](../basics/computer.md). |
| random number generator | term | Same as pseudo-random number generator: [Chance: probability, noise, integrals and Monte Carlo](../basics/math-probability.md). |
| random variable | term | [Chance: probability, noise, integrals and Monte Carlo](../basics/math-probability.md) |
| Range (light) | term | [Lights: the sun, points and spots](../light/lights.md) |
| Range allocator | term | [`gpu/geometry-pool`](../gpu/geometry-pool.md) |
| Range read | term | [Mip streaming](../draw/mip-streaming.md) |
| Range selection | term | [Lists that scale](../editor-ui/lists.md) |
| rasterization | term | [`gpu/how-a-gpu-frame-works`](../gpu/how-a-gpu-frame-works.md) |
| rasterize | term | Same as rasterization: [`gpu/how-a-gpu-frame-works`](../gpu/how-a-gpu-frame-works.md). |
| rasterized | term | Same as rasterization: [`gpu/how-a-gpu-frame-works`](../gpu/how-a-gpu-frame-works.md). |
| rasterizer | term | Same as rasterization: [`gpu/how-a-gpu-frame-works`](../gpu/how-a-gpu-frame-works.md). |
| rasterizes | term | Same as rasterization: [`gpu/how-a-gpu-frame-works`](../gpu/how-a-gpu-frame-works.md). |
| rasterizing | term | Same as rasterization: [`gpu/how-a-gpu-frame-works`](../gpu/how-a-gpu-frame-works.md). |
| Ratchet | term | [Measuring performance honestly: noise, percentiles, budgets and the perf lab](../engineering/perf-lab.md) |
| rate | term | Same as rate of change: [Change over time: rates, accumulation, Euler steps and Newton's laws](../basics/math-change.md). |
| rate of change | term | [Change over time: rates, accumulation, Euler steps and Newton's laws](../basics/math-change.md) |
| Ratio estimator | term | [Screen-space reflections](../indirect/ssr.md) |
| ray | term | [Geometry for engines: rays, planes, boxes and intersection tests](../basics/math-geometry.md) |
| `RayCallback` | identifier | [Physics queries](../physics/queries.md) |
| Raycast | term | [Physics queries](../physics/queries.md) Used in [Physics for game makers](../make/physics.md). |
| Raycast target | term | [`ui/input`](../ui/input.md) |
| `RaycastAll` | term | Same as Raycast: [Physics queries](../physics/queries.md). |
| Rayleigh | term | [Earth's atmosphere and aerial perspective](../light/atmosphere.md) |
| rc | term | Same as release candidate: [Packaging and releasing](../engineering/releasing.md). |
| Re-celling | term | [Editing a streamed world](../editor/worlds.md) |
| Reach | term | [Animating only what is seen](../animation/culling.md) |
| Reactive mask | term | [Temporal anti-aliasing](../image/taa.md) |
| `ReadActionState` | identifier | [Input actions](../input/actions.md) |
| Readback | term | [`gpu/readback-timing`](../gpu/readback-timing.md) |
| `ReadImportDependency` | identifier | [Importing: from source files to engine data](../assets/importing.md) |
| reading track | term | [How to read this book](../start/how-to-read.md) |
| rebind | term | Same as Rebinding: [Menus: buttons, navigation, pause and settings screens](../make/menus.md). |
| Rebinding | term | [Menus: buttons, navigation, pause and settings screens](../make/menus.md) |
| rebinds | term | Same as Rebinding: [Menus: buttons, navigation, pause and settings screens](../make/menus.md). |
| Rec. 709 | term | [`basics/color`](../basics/color.md) |
| Recency order | term | [Residency, eviction and pins](../assets/residency.md) |
| recent list | term | Same as recent projects: [Opening projects and scenes: templates, background loads and migration](../editor/projects.md). |
| recent projects | term | [Opening projects and scenes: templates, background loads and migration](../editor/projects.md) |
| Recorded bounds | term | [The render scene: persistent proxies](../draw/render-scene.md) |
| recoverable failure | term | [Ownership, errors and logging in Strata](../core/conventions.md) |
| recoverable failures | term | Same as recoverable failure: [Ownership, errors and logging in Strata](../core/conventions.md). |
| Recovery journal | term | [`editor/recovery`](../editor/recovery.md) Used in [Projects, saving, undo and recovery](../make/project-files.md). |
| Redo branch | term | [Undo and redo](../editor/undo.md) |
| `$ref` | term | [Command scripts and batches](../editor/command-scripts.md) Used in [Input and input actions](../make/input.md). |
| reference (runtime) | term | Same as Dependency: [References, closures, prefetch and loading screens](../assets/references.md). |
| Reference machine | term | [Measuring performance honestly: noise, percentiles, budgets and the perf lab](../engineering/perf-lab.md) |
| Reference resolution | term | [Rects, anchors and layout](../ui/layout.md) Used in [`make/hud`](../make/hud.md). |
| Referencer | term | [The trash and references](../editor/trash-references.md) |
| Referencers | term | Same as Referencer: [The trash and references](../editor/trash-references.md). |
| reflectance | term | [How surfaces reflect light: the reflection equation and microfacets](../light/reflectance.md) |
| Reflection | term | [Reflection: one registration, many uses](../world/reflection.md) |
| Reflection attack | term | [The security model](../automation/security.md) |
| Reflection probe | term | [Reflection probes](../indirect/probes.md) Used in [Sky light, ambient occlusion and reflections in your game](../make/reflections.md). |
| `RefreshOwner` | identifier | [From entities to bodies: records, shapes, mesh colliders](../physics/building-bodies.md) |
| regex | term | Same as regular expression: [`basics/data-formats`](../basics/data-formats.md). |
| register | term | [`basics/computer`](../basics/computer.md) |
| Register and space | term | [Pipelines and binding: layouts, registers and bindless](../gpu/binding.md) |
| `RegisterAssetPipeline` | identifier | [What an asset is](../assets/what-is-an-asset.md) |
| `RegisterAudioModule` | identifier | [The Audio scene system](../audio/scene-system.md) |
| `RegisterGameUIRenderer` | identifier | [Overlays, debug drawing and gizmos](../gpu/debug-drawing.md) |
| `RegisterRendererModule` | identifier | [What an asset is](../assets/what-is-an-asset.md) |
| `RegisterScriptingModule` | identifier | [The script system](../scripting/script-system.md) |
| `RegisterWorldModule` | identifier | [Worlds meet physics and scripts](../worlds/physics-scripts.md) |
| Registry | term | [Layers, registries and the composition root](../core/layers-registries.md) |
| Registry (world) | term | [Entities and components, with EnTT inside](../world/ecs.md) |
| `registry.patch` | term | Same as patch: [The scene graph: hierarchy, transforms and the transform contract](../world/scene-graph.md). |
| regular expression | term | [`basics/data-formats`](../basics/data-formats.md) |
| regular expressions | term | Same as regular expression: [`basics/data-formats`](../basics/data-formats.md). |
| Relative error | term | [Levels of detail](../draw/lod.md) |
| relay server | term | [Networking for games, in general](../appendix/networking.md) |
| release candidate | term | [Packaging and releasing](../engineering/releasing.md) |
| Released | term | [How input reaches a game: events, polling, edges and intents](../input/how-input-works.md) |
| Relevance | term | [Many lights: culling and clustered forward shading](../light/many-lights.md) |
| relocation | term | [`indirect/gi-cascades`](../indirect/gi-cascades.md) |
| remapping | term | [Blending and smoothing: lerp, easing, curves and exponential smoothing](../basics/math-interpolation.md) |
| Render proxy | term | [The render scene: persistent proxies](../draw/render-scene.md) |
| Render scale | term | [Quality settings and players' graphics options](../image/quality-settings.md) |
| Render scene | term | [The render scene: persistent proxies](../draw/render-scene.md) |
| Render target | term | [The Scene view](../editor-ui/scene-view.md) |
| render to texture | term | Same as Render target: [The Scene view](../editor-ui/scene-view.md). |
| Render transform | term | [Edit-mode poses and previews](../animation/editor.md) |
| renderer | term | [What a game engine is: one frame, start to finish](../start/what-an-engine-is.md) |
| Renderer.Quality | term | Same as Settings section (world): [Projects and settings](../world/projects-settings.md). |
| `Renderer::PrepareBackBuffer` | identifier | [Staging and the upload queue](../gpu/upload-queue.md) |
| `RendererGPUStages::Get` | identifier | [Tutorial: adding a post effect](../image/tutorial-post-effect.md) |
| rendering | term | Same as renderer: [What a game engine is: one frame, start to finish](../start/what-an-engine-is.md). |
| `RenderScene` | term | Same as Render scene: [The render scene: persistent proxies](../draw/render-scene.md). |
| `RenderScene::ComputePalette` | identifier | [Skinned meshes in the renderer](../draw/skinned.md) Also in [Skinning](../animation/skinning.md). |
| `RenderScene::EvaluatePose` | identifier | [Skinning](../animation/skinning.md) |
| `RenderScene::PrepareLoadedScene` | identifier | [`draw/render-scene-gpu`](../draw/render-scene-gpu.md) |
| `RenderScene::UpdateSkinnedPoses` | identifier | [Skinned meshes in the renderer](../draw/skinned.md) |
| `RenderSceneGPU` | term | Same as `GPU copy`: [`draw/render-scene-gpu`](../draw/render-scene-gpu.md). |
| `RenderSceneGPUCache::Get` | identifier | [`draw/render-scene-gpu`](../draw/render-scene-gpu.md) |
| Replay | term | [Asking for assets at draw time](../draw/asset-requests.md) Used in [Automated play-tests](../make/automated-playtests.md). |
| Replay attack | term | [The security model](../automation/security.md) |
| Replay script | term | [The activity journal and replays](../editor/journal.md) |
| repo | term | Same as repository: [Version control with git](../basics/git.md). |
| `ReportCallFailure` | identifier | [`automation/mcp`](../automation/mcp.md) |
| `ReportProblem` | term | [`scripting/host-api`](../scripting/host-api.md) |
| repository | term | [Version control with git](../basics/git.md) |
| Reprojection | term | [Temporal anti-aliasing](../image/taa.md) |
| Request (touch) | term | [Residency, eviction and pins](../assets/residency.md) |
| Request priority | term | [Asking for assets at draw time](../draw/asset-requests.md) |
| Requests in flight | term | [`automation/rpc-server`](../automation/rpc-server.md) |
| Requirement | term | [Reflection: one registration, many uses](../world/reflection.md) |
| requires clause | term | [Modern C++ as Strata uses it: move semantics, constexpr, optional, variant, span and concepts](../basics/cpp-modern.md) |
| Resampling | term | [Clips, voices and sources](../audio/clips-voices-sources.md) |
| Resampling blur | term | [Temporal anti-aliasing](../image/taa.md) |
| Rescaling | term | [Gamepads](../input/gamepads.md) |
| Reservation | term | [Residency, eviction and pins](../assets/residency.md) |
| Residency | term | [Residency, eviction and pins](../assets/residency.md) |
| Resident (proxy) | term | [`draw/render-scene-gpu`](../draw/render-scene-gpu.md) |
| `Resize` | identifier | [A game's identity: the manifest, icons and platform files](../worlds/game-identity.md) |
| `Resolve` | identifier | [From an address to a file and line](../scripting/symbolization.md) |
| `ResolveContext` | identifier | [`scripting/host-api`](../scripting/host-api.md) |
| `ResolveInlinedCalls` | identifier | [From an address to a file and line](../scripting/symbolization.md) |
| `ResolveShape` | identifier | [From entities to bodies: records, shapes, mesh colliders](../physics/building-bodies.md) |
| resource acquisition is initialization | term | Same as `RAII`: [`basics/cpp-memory`](../basics/cpp-memory.md). |
| Resource lock | term | [Inside StrataTests](../engineering/test-program.md) |
| resource state | term | Same as Barrier: [Compute shaders: dispatches, thread groups, shared memory and atomics](../gpu/compute.md). |
| Responder | term | [`automation/rpc-server`](../automation/rpc-server.md) |
| Rest pose | term | [Skeletons and forward kinematics](../animation/skeletons.md) |
| Restitution | term | [Rigid bodies and colliders](../physics/bodies-colliders.md) |
| retained representation | term | [From entities to draw calls](../draw/entities-to-draws.md) |
| `Retained-mode GUI` | term | [`ui/what-game-ui-does`](../ui/what-game-ui-does.md) |
| Retargeting | term | [Clips: sampling motion](../animation/clips.md) |
| return value | term | [`basics/programming-2`](../basics/programming-2.md) |
| reverse Z | term | Same as reversed Z: [Cameras and projection: perspective, homogeneous coordinates and depth](../basics/math-projection.md). |
| reversed Z | term | [Cameras and projection: perspective, homogeneous coordinates and depth](../basics/math-projection.md) |
| Reversed-Z | term | Same as reversed Z: [Cameras and projection: perspective, homogeneous coordinates and depth](../basics/math-projection.md). |
| Revert | term | [Prefabs: the data model](../world/prefabs.md) Used in [Prefabs](../make/prefabs.md). |
| review checklist | term | Same as pre-commit review checklist: [The review checklist and the way a change lands](../engineering/contributing.md). |
| `RGB9E5` | term | [Global illumination I: a voxel copy of the world](../indirect/gi-voxels.md) |
| `RHI` | term | [Vulkan, NVRHI, the graphics device and the Renderer's services](../gpu/vulkan-nvrhi.md) |
| right-handed | term | Same as handedness: [`basics/math-matrices`](../basics/math-matrices.md). |
| Rigid body | term | [Rigid bodies and colliders](../physics/bodies-colliders.md) Used in [Physics for game makers](../make/physics.md). |
| Ring buffer | term | [Data structures I: arrays, lists, hash maps and their cost](../basics/data-structures.md) |
| ringing | term | [Directions on a sphere: solid angles, spherical harmonics and octahedral maps](../basics/math-sphere.md) |
| `RMS` | term | [Testing sound without speakers](../audio/testing.md) |
| roll angle | term | [Rotations and quaternions](../basics/math-rotations.md) |
| Rollback | term | [Undo and redo](../editor/undo.md) |
| Rollback (networking) | term | [Networking for games, in general](../appendix/networking.md) |
| rollback network code | term | Same as Rollback (networking): [Networking for games, in general](../appendix/networking.md). |
| Rolloff | term | [Sound in space](../audio/spatial.md) |
| Room before arrival | term | [Residency, eviction and pins](../assets/residency.md) |
| Root canvas | term | [Rects, anchors and layout](../ui/layout.md) |
| Root entity | term | [The scene graph: hierarchy, transforms and the transform contract](../world/scene-graph.md) |
| Root motion | term | [Root motion](../animation/root-motion.md) Used in [Animation for game makers](../make/animation.md). |
| Root motion joint | term | [Root motion](../animation/root-motion.md) |
| `RootTravel::Append` | identifier | [Root motion](../animation/root-motion.md) |
| rotation | term | [`basics/math-matrices`](../basics/math-matrices.md) |
| rotation box | term | [Project: Tetris](../make/project-tetris.md) |
| round-off error | term | Same as rounding error: [Numbers in a computer: binary, integers, floating point and precision](../basics/numbers.md). |
| round-trip time | term | Same as Latency (networking): [Networking for games, in general](../appendix/networking.md). |
| rounding error | term | [Numbers in a computer: binary, integers, floating point and precision](../basics/numbers.md) |
| Row traits | term | [Quality settings and players' graphics options](../image/quality-settings.md) |
| `RPC` | term | [`automation/json-rpc`](../automation/json-rpc.md) |
| `RpcResponder` | term | Same as Responder: [`automation/rpc-server`](../automation/rpc-server.md). |
| `RUN_SERIAL` | term | [Inside StrataTests](../engineering/test-program.md) |
| `RunMcpServer` | identifier | [`automation/mcp`](../automation/mcp.md) |
| `Runner (GitHub Actions)` | term | [Continuous integration](../engineering/ci.md) |
| Running copy | term | [Play mode: the running copy](../editor/play-mode.md) |
| `RUNPATH` | term | [Shared libraries and binary interfaces](../scripting/shared-libraries.md) |
| runtime | term | [What a game engine is: one frame, start to finish](../start/what-an-engine-is.md) |
| `RuntimeAssetManager::AddPack` | identifier | [Asset packs, export and patches](../assets/packs-export.md) |
| Safe area | term | [Rects, anchors and layout](../ui/layout.md) |
| Sample (audio) | term | [Sound inside a computer](../audio/sound-in-a-computer.md) |
| Sample (editor) | term | [Opening projects and scenes: templates, background loads and migration](../editor/projects.md) |
| Sample (start) | term | [Your first game](../start/first-game.md) |
| sample rate | term | [Sampling, aliasing and filtering](../basics/signals.md) |
| Sample-and-hold blur | term | [Motion blur](../image/motion-blur.md) |
| `SampleCosineHemisphere` | identifier | [Directions on a sphere: solid angles, spherical harmonics and octahedral maps](../basics/math-sphere.md) |
| `samplerFilterMinmax` | term | Same as Min/max sampler: [Occlusion culling](../draw/occlusion.md). |
| sampling | term | [Sampling, aliasing and filtering](../basics/signals.md) |
| sampling rate | term | Same as sample rate: [Sampling, aliasing and filtering](../basics/signals.md). |
| `SanitizeHDR` | term | [`light/brdf`](../light/brdf.md) |
| Saturation | term | [Tone mapping and the Filmic curve](../image/tone-mapping.md) |
| Save file | term | [Levels, loading screens and save files](../make/levels-saves.md) |
| Save point | term | [Undo and redo](../editor/undo.md) |
| scale | term | [`basics/math-matrices`](../basics/math-matrices.md) |
| Scale (s) | term | [Rects, anchors and layout](../ui/layout.md) |
| scale mode | term | [`make/hud`](../make/hud.md) |
| Scancode | term | [How input reaches a game: events, polling, edges and intents](../input/how-input-works.md) |
| `ScanEntityInto` | identifier | [References, closures, prefetch and loading screens](../assets/references.md) |
| Scatter-as-gather | term | [Depth of field](../image/depth-of-field.md) |
| scene | term | [Scenes, entities and components](../make/scenes-entities.md) |
| Scene edit transaction | term | [Undo and redo](../editor/undo.md) |
| Scene service | term | [Systems, phases and fixed steps](../world/systems.md) |
| Scene system | term | [Systems, phases and fixed steps](../world/systems.md) |
| Scene view | term | [The Scene view](../editor-ui/scene-view.md) |
| Scene work budget | term | [Loading scenes: whole, additive and in slices](../world/sub-scenes.md) |
| Scene-color copy | term | [Transparency, clear coat and glass](../light/clearcoat-transmission.md) |
| scene-linear | term | [`basics/color`](../basics/color.md) |
| `Scene::ApplyProjectLayers` | identifier | [Collision layers](../physics/collision-layers.md) |
| `Scene::BeginSubSceneUnload` | identifier | [Loading scenes: whole, additive and in slices](../world/sub-scenes.md) |
| `Scene::CompareHierarchyOrder` | identifier | [The scene graph: hierarchy, transforms and the transform contract](../world/scene-graph.md) |
| `Scene::ConnectSignals` | identifier | [The scene graph: hierarchy, transforms and the transform contract](../world/scene-graph.md) |
| `Scene::CreateEntityWithUUID` | identifier | [Entities and components, with EnTT inside](../world/ecs.md) |
| `Scene::GetMaxFixedSteps` | identifier | [Time: delta time, the fixed step and time scale](../core/time.md) |
| `Scene::GetPrimaryCameraEntity` | identifier | [The scene graph: hierarchy, transforms and the transform contract](../world/scene-graph.md) |
| `Scene::GetWorldTransform` | identifier | [The scene graph: hierarchy, transforms and the transform contract](../world/scene-graph.md) |
| `Scene::HasDirtyAncestor` | identifier | [The scene graph: hierarchy, transforms and the transform contract](../world/scene-graph.md) |
| `Scene::LinkLast` | identifier | [The scene graph: hierarchy, transforms and the transform contract](../world/scene-graph.md) |
| `Scene::ReleaseInBackground` | identifier | [Loading scenes: whole, additive and in slices](../world/sub-scenes.md) |
| `Scene::RemoveLookupValue` | identifier | [Data structures I: arrays, lists, hash maps and their cost](../basics/data-structures.md) Also in [The scene graph: hierarchy, transforms and the transform contract](../world/scene-graph.md). |
| `Scene::SetParent` | identifier | [The scene graph: hierarchy, transforms and the transform contract](../world/scene-graph.md) |
| `Scene::SetPaused` | identifier | [Pausing, stepping and exact tests](../editor/stepping.md) |
| `Scene::SetWorldTransform` | identifier | [`basics/math-matrices`](../basics/math-matrices.md) |
| `SceneAsset::Deserialize` | identifier | [Loading scenes: whole, additive and in slices](../world/sub-scenes.md) |
| `SceneAsset::TakePreparedScene` | identifier | [Loading scenes: whole, additive and in slices](../world/sub-scenes.md) |
| `SceneDrawBatch` | term | Same as Batch (draw): [Batching and instancing](../draw/batching.md). |
| `SceneDrawKey` | term | Same as Sort key: [Batching and instancing](../draw/batching.md). |
| `SceneEdit::ApplyEntities` | identifier | [Undo and redo](../editor/undo.md) |
| `SceneEditAction::MergeWith` | identifier | [Undo and redo](../editor/undo.md) |
| `SceneEditTransaction::TakeAction` | identifier | [Undo and redo](../editor/undo.md) |
| `SceneHierarchyPanel::DrawRow` | identifier | [Dear ImGui from first principles](../editor-ui/imgui.md) |
| `SceneLoadRequest::Update` | identifier | [Loading scenes: whole, additive and in slices](../world/sub-scenes.md) |
| `SceneOverlayRegistry::Register` | identifier | [Overlays, debug drawing and gizmos](../gpu/debug-drawing.md) |
| `SceneRecovery::OnApplied` | identifier | [`editor/recovery`](../editor/recovery.md) |
| `SceneRecovery::Update` | identifier | [`editor/recovery`](../editor/recovery.md) |
| `SceneRecovery::Write` | identifier | [`editor/recovery`](../editor/recovery.md) |
| `SceneRenderer::BuildDrawArguments` | identifier | [`gpu/geometry-pool`](../gpu/geometry-pool.md) |
| `SceneRenderer::DrawDebugLines` | identifier | [Overlays, debug drawing and gizmos](../gpu/debug-drawing.md) |
| `SceneRenderer::FilterEnvironmentStep` | identifier | [Image-based lighting and the split sum](../indirect/ibl.md) |
| `SceneRenderer::MarkVisibleProxies` | identifier | [Asking for assets at draw time](../draw/asset-requests.md) |
| `SceneRenderer::RenderDepthOfField` | identifier | [Depth of field](../image/depth-of-field.md) |
| `SceneRenderer::RenderFrame` | identifier | [A frame of the scene renderer, pass by pass](../gpu/frame-tour.md) |
| `SceneRenderer::RenderMotionBlur` | identifier | [Motion blur](../image/motion-blur.md) |
| `SceneRenderer::RenderOverlays` | identifier | [Overlays, debug drawing and gizmos](../gpu/debug-drawing.md) |
| `SceneRenderer::ReportVisibleAnimators` | identifier | [Animating only what is seen](../animation/culling.md) |
| `SceneRenderer::ResolveAssets` | identifier | [Asking for assets at draw time](../draw/asset-requests.md) |
| `SceneRenderer::ResolveLightingViewStats` | identifier | [Measuring light: the debug views and their statistics](../light/measuring-light.md) |
| `SceneRenderer::ResolveMaterials` | identifier | [Asking for assets at draw time](../draw/asset-requests.md) |
| `SceneRenderer::ReuseResolvedMaterials` | identifier | [Asking for assets at draw time](../draw/asset-requests.md) |
| `SceneRenderer::SetHeightFog` | identifier | [Height fog](../light/fog.md) |
| `SceneWorkBudget` | term | Same as Work budget: [Loading scenes: whole, additive and in slices](../world/sub-scenes.md). |
| scheduling quantum | term | [Talking to the operating system](../core/platform.md) |
| Schlick approximation | term | [How surfaces reflect light: the reflection equation and microfacets](../light/reflectance.md) |
| scope | term | [Programming from zero I: values, variables, expressions and decisions](../basics/programming-1.md) |
| Scope (make) | term | [Planning a small game: the core loop, scope, prototype and playtest](../make/designing-a-game.md) |
| scoped enum | term | Same as scoped enumeration: [Programming from zero I: values, variables, expressions and decisions](../basics/programming-1.md). |
| scoped enumeration | term | [Programming from zero I: values, variables, expressions and decisions](../basics/programming-1.md) |
| Screen fraction | term | [Bounding volumes, frustums and the spatial index](../draw/bounds-culling.md) |
| Screen space | term | [`ui/what-game-ui-does`](../ui/what-game-ui-does.md) |
| Screen view | term | [Overlays, debug drawing and gizmos](../gpu/debug-drawing.md) |
| Screen-space reflections | term | [Screen-space reflections](../indirect/ssr.md) |
| Screen-space shadow mask | term | [`light/sun-shadows-2`](../light/sun-shadows-2.md) |
| script | term | [Your first game](../start/first-game.md) |
| script class | term | [Your first script](../make/first-script.md) |
| script field | term | [Your first script](../make/first-script.md) |
| Script mode | term | [Inside Strata's CMake](../engineering/cmake.md) |
| script module | term | [Your first script](../make/first-script.md) |
| `ScriptBuilder::Begin` | identifier | [Building scripts from the editor: toolchains, CMake, diagnostics](../editor/script-builds.md) |
| `ScriptBuilder::StartProcess` | identifier | [Building scripts from the editor: toolchains, CMake, diagnostics](../editor/script-builds.md) |
| `ScriptBuilder::Update` | identifier | [Building scripts from the editor: toolchains, CMake, diagnostics](../editor/script-builds.md) |
| `ScriptBuildSettings::Detect` | identifier | [Building scripts from the editor: toolchains, CMake, diagnostics](../editor/script-builds.md) |
| `ScriptEngine::LoadInternal` | identifier | [Hot reload](../scripting/hot-reload.md) |
| `ScriptEngine::SetHotReloadEnabled` | identifier | [Hot reload](../scripting/hot-reload.md) |
| `ScriptEngine::StartWatching` | identifier | [Hot reload](../scripting/hot-reload.md) |
| `ScriptEngine::Update` | identifier | [Hot reload](../scripting/hot-reload.md) |
| `ScriptModule::RecordFault` | identifier | [From an address to a file and line](../scripting/symbolization.md) |
| `ScriptSystem::BeginModuleReload` | identifier | [Hot reload](../scripting/hot-reload.md) |
| `ScriptSystem::DeliverContact` | identifier | [The script system](../scripting/script-system.md) |
| `ScriptSystem::DestroyEntity` | identifier | [The script system](../scripting/script-system.md) |
| `ScriptSystem::EndModuleReload` | identifier | [Hot reload](../scripting/hot-reload.md) |
| `ScriptSystem::GetAssetLoadProgress` | identifier | [References, closures, prefetch and loading screens](../assets/references.md) |
| `ScriptSystem::OnAnimationEvent` | identifier | [The script system](../scripting/script-system.md) |
| `ScriptSystem::OnCollision` | identifier | [Contacts and triggers](../physics/contacts-triggers.md) |
| `ScriptSystem::ReportProblem` | identifier | [`scripting/host-api`](../scripting/host-api.md) |
| `ScriptSystem::RunCallbacks` | identifier | [The script system](../scripting/script-system.md) |
| `ScriptSystem::RunPendingReloads` | identifier | [Hot reload](../scripting/hot-reload.md) |
| `ScriptSystem::SyncPoint` | identifier | [The script system](../scripting/script-system.md) |
| `SDF` | term | Same as Signed distance field: [Text: fonts, shaping and signed distance fields](../gpu/text.md). |
| `SDK` | term | [`scripting/abi-sdk`](../scripting/abi-sdk.md) Used in [Your first script](../make/first-script.md). |
| seam | term | [Talking to the operating system](../core/platform.md) |
| Section (property) | term | [Inspectors from reflection](../editor-ui/inspectors.md) |
| section header | term | [The widget kit](../editor-ui/widget-kit.md) |
| seed | term | [Chance: probability, noise, integrals and Monte Carlo](../basics/math-probability.md) Used in [Building blocks and recipes](../make/recipes.md). |
| `SEH` | term | [Crash containment](../scripting/crash-containment.md) |
| Selectable | term | [`ui/input`](../ui/input.md) |
| selection anchor | term | [Text and text fields](../ui/text.md) |
| Selection user data | term | [Lists that scale](../editor-ui/lists.md) |
| self time | term | [Measuring the frame: the frame profiler, Tracy and the method](../core/profiling.md) |
| Self-pipe trick | term | [`automation/rpc-server`](../automation/rpc-server.md) |
| self-time | term | Same as self time: [Measuring the frame: the frame profiler, Tracy and the method](../core/profiling.md). |
| semantic color | term | Same as Token: [The design system: theme, fonts, icons](../editor-ui/design-system.md). |
| Semaphore | term | [Vulkan, NVRHI, the graphics device and the Renderer's services](../gpu/vulkan-nvrhi.md) |
| semi-implicit Euler method | term | [Change over time: rates, accumulation, Euler steps and Newton's laws](../basics/math-change.md) |
| sensor height | term | Same as Thin lens: [Depth of field](../image/depth-of-field.md). |
| separating axis | term | [Geometry for engines: rays, planes, boxes and intersection tests](../basics/math-geometry.md) |
| separating axis test | term | [Collision detection: shapes, broad phase and narrow phase](../physics/collision-detection.md) |
| Sequence lock | term | [Threads and the job system](../core/jobs.md) |
| sequence number | term | [Debugging the engine: debuggers, asserts, the log and crash reports](../core/debugging.md) |
| sequence numbers | term | Same as sequence number: [Debugging the engine: debuggers, asserts, the log and crash reports](../core/debugging.md). |
| Serial | term | [Undo and redo](../editor/undo.md) |
| serialization | term | [Bytes in files and memory: layouts, byte order and text encodings](../basics/bytes.md) |
| server | term | [`automation/mcp`](../automation/mcp.md) |
| server reconciliation | term | [Networking for games, in general](../appendix/networking.md) |
| Service | term | [Engine modules](../core/engine-modules.md) |
| Service locator | term | [Engine modules](../core/engine-modules.md) |
| Session file | term | [The security model](../automation/security.md) |
| Session results | term | [Commands](../editor/commands.md) |
| session token | term | [The security model](../automation/security.md) |
| `SetBaseSizes` | identifier | [`editor-ui/ui-scale`](../editor-ui/ui-scale.md) |
| `SetJitteredDepthBias` | identifier | [Overlays, debug drawing and gizmos](../gpu/debug-drawing.md) |
| `SetPropertyWithUndo` | identifier | [Undo and redo](../editor/undo.md) |
| settings browser | term | Same as Settings section (editor-ui): [Settings windows from schemas](../editor-ui/settings-windows.md). |
| Settings handler | term | [The editor shell: host, layer, docking and panels](../editor-ui/shell.md) |
| settings page | term | Same as Settings section (editor-ui): [Settings windows from schemas](../editor-ui/settings-windows.md). |
| Settings section (editor-ui) | term | [Settings windows from schemas](../editor-ui/settings-windows.md) |
| Settings section (world) | term | [Projects and settings](../world/projects-settings.md) |
| Settle frames | term | [Temporal anti-aliasing](../image/taa.md) |
| Settle scene | term | [Tuning and measuring](../physics/tuning.md) |
| Settled | term | [`indirect/gi-cascades`](../indirect/gi-cascades.md) |
| `SH` | term | Same as spherical harmonics: [Directions on a sphere: solid angles, spherical harmonics and octahedral maps](../basics/math-sphere.md). |
| `SHA-256` | term | [`basics/data-formats`](../basics/data-formats.md) |
| `SHA-256 pin` | term | [Third-party code and pinned tools](../engineering/third-party.md) |
| shader | term | [What a game engine is: one frame, start to finish](../start/what-an-engine-is.md) |
| `ShaderLibrary::Get` | identifier | [Shaders: Slang, the build and the dialect](../gpu/shaders.md) |
| Shadow acne | term | [Shadow mapping from first principles](../light/shadow-basics.md) |
| Shadow atlas | term | [Shadows of point and spot lights](../light/local-shadows.md) |
| Shadow cascade cache | term | [Sun shadows I: stable cascades](../light/sun-shadows-1.md) |
| Shadow caster | term | [Sun shadows I: stable cascades](../light/sun-shadows-1.md) |
| Shadow map | term | [Shadow mapping from first principles](../light/shadow-basics.md) |
| shape cast (sweep) | term | Same as Raycast: [Physics queries](../physics/queries.md). |
| `ShapePlanes` | identifier | [Character controllers](../physics/character-controllers.md) |
| Shard | term | [Inside StrataTests](../engineering/test-program.md) |
| shared library | term | [How a C++ program is built: from two files by hand to CMake](../basics/build.md) |
| shared memory | term | [Compute shaders: dispatches, thread groups, shared memory and atomics](../gpu/compute.md) |
| shared pointer | term | [`basics/cpp-memory`](../basics/cpp-memory.md) |
| `Sharpening (TAA)` | term | [Temporal anti-aliasing](../image/taa.md) |
| shell | term | [The tools: the terminal, files and a code editor](../basics/tools.md) |
| shell command | term | Same as terminal command: [The tools: the terminal, files and a code editor](../basics/tools.md). |
| Shortcut routing | term | [The Game view, shortcuts and who owns the keyboard](../editor-ui/game-view.md) |
| Shutter angle | term | [Motion blur](../image/motion-blur.md) |
| Sibling index | term | [The scene graph: hierarchy, transforms and the transform contract](../world/scene-graph.md) |
| sidecar | term | Same as `.meta` file: [Handles, .meta files and sub-assets](../assets/handles-meta.md). |
| signal | term | [Sampling, aliasing and filtering](../basics/signals.md) |
| Signal (on_update) | term | Same as signal: [Sampling, aliasing and filtering](../basics/signals.md). |
| signal sample | term | [Sampling, aliasing and filtering](../basics/signals.md) |
| Signed difference image | term | [The look-dev harness](../engineering/look-dev.md) |
| signed distance | term | [Geometry for engines: rays, planes, boxes and intersection tests](../basics/math-geometry.md) |
| Signed distance field | term | [Text: fonts, shaping and signed distance fields](../gpu/text.md) |
| significand | term | [Numbers in a computer: binary, integers, floating point and precision](../basics/numbers.md) |
| `SIGPIPE` | term | [`automation/json-rpc`](../automation/json-rpc.md) |
| `sigsetjmp`/`siglongjmp` | term | [Crash containment](../scripting/crash-containment.md) |
| `SIMD` | term | [`basics/computer`](../basics/computer.md) |
| Simple | term | [Projects and settings](../world/projects-settings.md) |
| simple mode | term | [State machines](../animation/state-machines.md) |
| simplex | term | [Collision detection: shapes, broad phase and narrow phase](../physics/collision-detection.md) |
| Simulate | term | [Play mode: the running copy](../editor/play-mode.md) |
| Simulate mode | term | [Play mode: the running copy](../editor/play-mode.md) |
| Simulated input | term | [Simulated input](../input/simulated.md) Used in [Automated play-tests](../make/automated-playtests.md). |
| sine | term | [Vectors: length, direction, dot and cross products](../basics/math-vectors.md) |
| Single | term | [Earth's atmosphere and aerial perspective](../light/atmosphere.md) |
| single instruction, multiple data | term | Same as `SIMD`: [`basics/computer`](../basics/computer.md). |
| sink | term | [Ownership, errors and logging in Strata](../core/conventions.md) |
| Size culling | term | [Bounding volumes, frustums and the spatial index](../draw/bounds-culling.md) |
| Skeleton | term | [Animation for game makers](../make/animation.md) |
| Skeleton (rig) | term | [Skeletons and forward kinematics](../animation/skeletons.md) |
| `Skeleton::ComputeModelTransforms` | identifier | [Skeletons and forward kinematics](../animation/skeletons.md) |
| `Skeleton::Deserialize` | identifier | [Skeletons and forward kinematics](../animation/skeletons.md) |
| skin | term | [Animation for game makers](../make/animation.md) |
| `Skin (glTF)` | term | [Skinning](../animation/skinning.md) |
| skin binding | term | Same as `Skin (glTF)`: [Skinning](../animation/skinning.md). |
| Skinning | term | [Skinning](../animation/skinning.md) |
| skinning palette | term | [Skinning](../animation/skinning.md) |
| sky preset | term | [The sky as a light: sources, sun extraction and presets](../light/sky.md) |
| slab | term | [Geometry for engines: rays, planes, boxes and intersection tests](../basics/math-geometry.md) |
| Slang | term | [Shaders: Slang, the build and the dialect](../gpu/shaders.md) |
| slangc | term | Same as Slang: [Shaders: Slang, the build and the dialect](../gpu/shaders.md). |
| Sleep threshold | term | [Rigid body dynamics: integration, contacts, solvers, sleep and continuous collision](../physics/dynamics.md) |
| Sleeping | term | [Physics for game makers](../make/physics.md) |
| slerp | term | [Rotations and quaternions](../basics/math-rotations.md) |
| Slice (indirect) | term | [Ambient occlusion without history](../indirect/ao.md) |
| slice (light) | term | [Sun shadows I: stable cascades](../light/sun-shadows-1.md) |
| Slice (world) | term | [Loading scenes: whole, additive and in slices](../world/sub-scenes.md) |
| slicing | term | [C++ classes in depth: inheritance, virtual calls and interfaces](../basics/cpp-classes.md) |
| `SlideMove` | identifier | [Character controllers](../physics/character-controllers.md) |
| Slope | term | [White balance, grading and lookup tables](../image/grading.md) |
| Slot | term | [The render scene: persistent proxies](../draw/render-scene.md) |
| `SMAA` | term | Same as `MLAA`: [`image/spatial-aa`](../image/spatial-aa.md). |
| smart pointer | term | [`basics/cpp-memory`](../basics/cpp-memory.md) |
| Smith visibility (height-correlated) | term | [How surfaces reflect light: the reflection equation and microfacets](../light/reflectance.md) |
| Smoke test | term | [Testing an engine](../engineering/testing.md) |
| smoothstep | term | [Blending and smoothing: lerp, easing, curves and exponential smoothing](../basics/math-interpolation.md) |
| Snapping (editor) | term | [Placing content](../editor/placement.md) |
| Snapping (editor-ui) | term | [The Scene view](../editor-ui/scene-view.md) |
| snapshot (editor) | term | [Undo and redo](../editor/undo.md) |
| Snapshot (networking) | term | [Networking for games, in general](../appendix/networking.md) |
| Snapshot (save) | term | [Saving without stalling](../editor/saving.md) |
| Snapshot (world) | term | [Scene documents: text, streams and the cooked form](../world/serialization.md) |
| `SoA` | term | Same as struct of arrays: [Data structures I: arrays, lists, hash maps and their cost](../basics/data-structures.md). |
| Socket | term | [`automation/json-rpc`](../automation/json-rpc.md) |
| soft constraint | term | [Systems, phases and fixed steps](../world/systems.md) |
| Soft contact | term | [Rigid body dynamics: integration, contacts, solvers, sleep and continuous collision](../physics/dynamics.md) |
| Soft knee | term | [Lens effects: bloom, vignette, flares and fringes](../image/lens-effects.md) |
| Softness | term | [`ui/drawing`](../ui/drawing.md) |
| solid angle | term | [Directions on a sphere: solid angles, spherical harmonics and octahedral maps](../basics/math-sphere.md) |
| Sort key | term | [Batching and instancing](../draw/batching.md) |
| Sort order | term | [Rects, anchors and layout](../ui/layout.md) |
| Source | term | [Clips, voices and sources](../audio/clips-voices-sources.md) |
| source asset | term | Same as source file: [`basics/programming-3`](../basics/programming-3.md). |
| source code | term | [How to read this book](../start/how-to-read.md) |
| source control | term | Same as version control: [Version control with git](../basics/git.md). |
| source file | term | [`basics/programming-3`](../basics/programming-3.md) |
| Source radius | term | [Lights with size: sized highlights and area lights](../light/area-lights.md) |
| source record | term | [The Audio scene system](../audio/scene-system.md) |
| Source revision | term | [Loading without stalling](../assets/loading.md) |
| source scan | term | [`editor-ui/ui-testing`](../editor-ui/ui-testing.md) |
| source scans | term | Same as source scan: [`editor-ui/ui-testing`](../editor-ui/ui-testing.md). |
| span | term | [Modern C++ as Strata uses it: move semantics, constexpr, optional, variant, span and concepts](../basics/cpp-modern.md) |
| sparse set | term | [Data structures I: arrays, lists, hash maps and their cost](../basics/data-structures.md) |
| spatial denoising | term | Same as denoising: [Sampling, aliasing and filtering](../basics/signals.md). |
| Spatial index | term | [Bounding volumes, frustums and the spatial index](../draw/bounds-culling.md) |
| Spatial navigation | term | [`ui/input`](../ui/input.md) |
| spatial tree | term | [`basics/trees-graphs`](../basics/trees-graphs.md) |
| spatial trees | term | Same as spatial tree: [`basics/trees-graphs`](../basics/trees-graphs.md). |
| `SpatialHigh` | term | Same as Checkerboard: [Screen-space reflections](../indirect/ssr.md). |
| `SpatialIndex` | term | Same as Spatial index: [Bounding volumes, frustums and the spatial index](../draw/bounds-culling.md). |
| Spatialization | term | [Sound in space](../audio/spatial.md) |
| spec | term | [Capstone I: designing a feature the way Strata does](../capstone/plan.md) |
| specs | term | Same as spec: [Capstone I: designing a feature the way Strata does](../capstone/plan.md). |
| Specular aliasing | term | [`light/brdf`](../light/brdf.md) |
| Specular anti-aliasing (geometric) | term | [`light/brdf`](../light/brdf.md) |
| Specular occlusion (Lagarde) | term | [Ambient occlusion without history](../indirect/ao.md) |
| specular power | term | [Strata's material model](../light/materials.md) |
| spherical coordinates | term | [Directions on a sphere: solid angles, spherical harmonics and octahedral maps](../basics/math-sphere.md) |
| spherical harmonics | term | [Directions on a sphere: solid angles, spherical harmonics and octahedral maps](../basics/math-sphere.md) |
| spherical linear interpolation | term | Same as slerp: [Rotations and quaternions](../basics/math-rotations.md). |
| `SPIR-V` | term | [Shaders: Slang, the build and the dialect](../gpu/shaders.md) |
| Spiral of death | term | [Time: delta time, the fixed step and time scale](../core/time.md) |
| spirv-val | term | [Continuous integration](../engineering/ci.md) |
| Split | term | [Sun shadows I: stable cascades](../light/sun-shadows-1.md) |
| Split sum | term | Same as Split-sum approximation: [Image-based lighting and the split sum](../indirect/ibl.md). |
| Split-sum approximation | term | [Image-based lighting and the split sum](../indirect/ibl.md) |
| `sRGB` | term | [`basics/color`](../basics/color.md) |
| `sRGB encoding` | term | [Why images need post-processing, and Strata's post chain](../image/why-post.md) |
| `sRGB formats` | term | [Vulkan, NVRHI, the graphics device and the Renderer's services](../gpu/vulkan-nvrhi.md) |
| `sRGB transfer function` | term | [`basics/color`](../basics/color.md) |
| `SSR` | term | Same as Screen-space reflections: [Screen-space reflections](../indirect/ssr.md). |
| `ST_CORE_ASSERT` | term | [Ownership, errors and logging in Strata](../core/conventions.md) |
| `ST_CORE_VERIFY` | term | [Ownership, errors and logging in Strata](../core/conventions.md) |
| `st_Main` | identifier | [`gpu/coordinates`](../gpu/coordinates.md) |
| Stable cascades | term | [Sun shadows I: stable cascades](../light/sun-shadows-1.md) |
| stable hash | term | [`basics/data-formats`](../basics/data-formats.md) |
| stable sort | term | [`basics/trees-graphs`](../basics/trees-graphs.md) |
| stable sorts | term | Same as stable sort: [`basics/trees-graphs`](../basics/trees-graphs.md). |
| `STAC` | term | Same as `STSK`: [Skeletons and forward kinematics](../animation/skeletons.md). |
| stack | term | [`basics/computer`](../basics/computer.md) |
| stack frame | term | [Finding bugs: a method, the log and the debugger](../basics/debugging.md) |
| Stack guarantee | term | [Crash containment](../scripting/crash-containment.md) |
| stack trace | term | [Finding bugs: a method, the log and the debugger](../basics/debugging.md) |
| staged file | term | Same as Atomic write: [Files you can trust](../core/files.md). |
| staging area | term | [Version control with git](../basics/git.md) |
| Staging buffer | term | [Staging and the upload queue](../gpu/upload-queue.md) |
| Staging pool | term | [Staging and the upload queue](../gpu/upload-queue.md) |
| Stale pose | term | [Animating only what is seen](../animation/culling.md) |
| Stale session | term | [The security model](../automation/security.md) |
| Stall timeout | term | [`automation/rpc-server`](../automation/rpc-server.md) |
| stamp | term | [Building scripts from the editor: toolchains, CMake, diagnostics](../editor/script-builds.md) |
| standard deviation | term | [Chance: probability, noise, integrals and Monte Carlo](../basics/math-probability.md) |
| standard error | term | [The tools: the terminal, files and a code editor](../basics/tools.md) |
| standard input | term | [The tools: the terminal, files and a code editor](../basics/tools.md) |
| standard library | term | [Generic C++: templates, lambdas and the standard containers](../basics/cpp-generic.md) |
| standard output | term | [The tools: the terminal, files and a code editor](../basics/tools.md) |
| standard-layout type | term | [Bytes in files and memory: layouts, byte order and text encodings](../basics/bytes.md) |
| `.stanimator` | term | [State machines](../animation/state-machines.md) |
| starburst | term | Same as Lens flare: [Lens effects: bloom, vignette, flares and fringes](../image/lens-effects.md). |
| Start scene | term | [The runtime](../worlds/runtime.md) Used in [Exporting and shipping](../make/export.md). |
| `StartPlayAfterBuild` | identifier | [Building scripts from the editor: toolchains, CMake, diagnostics](../editor/script-builds.md) |
| State | term | [State machines](../animation/state-machines.md) Used in [Animation for game makers](../make/animation.md). |
| state interpolation | term | Same as interpolation: [Drawing between fixed steps](../world/interpolation.md). |
| state machine | term | [Patterns for game code: state machines, managers and object pools](../make/patterns.md) |
| state machines | term | Same as state machine: [Patterns for game code: state machines, managers and object pools](../make/patterns.md). |
| statement | term | [Programming from zero I: values, variables, expressions and decisions](../basics/programming-1.md) |
| Static body | term | [Rigid bodies and colliders](../physics/bodies-colliders.md) |
| static initialization | term | [How a C++ program is built: from two files by hand to CMake](../basics/build.md) |
| static library | term | [How a C++ program is built: from two files by hand to CMake](../basics/build.md) |
| static member function | term | [`basics/programming-2`](../basics/programming-2.md) |
| Status provider | term | [Commands](../editor/commands.md) |
| stb_truetype | term | [Text: fonts, shaping and signed distance fields](../gpu/text.md) |
| std140 | term | [Pipelines and binding: layouts, registers and bindless](../gpu/binding.md) |
| std430 | term | Same as std140: [Pipelines and binding: layouts, registers and bindless](../gpu/binding.md). |
| `std::array` | term | Same as array: [`basics/programming-2`](../basics/programming-2.md). |
| `std::span` | term | Same as span: [Modern C++ as Strata uses it: move semantics, constexpr, optional, variant, span and concepts](../basics/cpp-modern.md). |
| `std::string` | term | Same as string: [`basics/programming-2`](../basics/programming-2.md). |
| `std::vector` | term | Same as dynamic array: [`basics/programming-2`](../basics/programming-2.md). |
| stderr | term | Same as standard error: [The tools: the terminal, files and a code editor](../basics/tools.md). |
| stdin | term | Same as standard input: [The tools: the terminal, files and a code editor](../basics/tools.md). |
| stdio | term | [The tools: the terminal, files and a code editor](../basics/tools.md) |
| stdout | term | Same as standard output: [The tools: the terminal, files and a code editor](../basics/tools.md). |
| steering behaviour | term | [`appendix/game-ai`](../appendix/game-ai.md) |
| steering behaviours | term | Same as steering behaviour: [`appendix/game-ai`](../appendix/game-ai.md). |
| step | term | [Staging and the upload queue](../gpu/upload-queue.md) |
| step alpha | term | [Drawing between fixed steps](../world/interpolation.md) Used in [Characters and cameras](../make/characters-cameras.md). |
| Step height | term | [Character controllers](../physics/character-controllers.md) |
| step into | term | Same as stepping through code: [Finding bugs: a method, the log and the debugger](../basics/debugging.md). |
| step out | term | Same as stepping through code: [Finding bugs: a method, the log and the debugger](../basics/debugging.md). |
| step over | term | Same as stepping through code: [Finding bugs: a method, the log and the debugger](../basics/debugging.md). |
| step up | term | Same as Step height: [Character controllers](../physics/character-controllers.md). |
| Stepping | term | [Pausing, stepping and exact tests](../editor/stepping.md) |
| stepping through code | term | [Finding bugs: a method, the log and the debugger](../basics/debugging.md) |
| steradian | term | [Directions on a sphere: solid angles, spherical harmonics and octahedral maps](../basics/math-sphere.md) |
| .stgame | term | Same as Manifest: [Exporting and shipping](../make/export.md). |
| storage | term | [`basics/computer`](../basics/computer.md) |
| storage image | term | Same as `UAV`: [Compute shaders: dispatches, thread groups, shared memory and atomics](../gpu/compute.md). |
| Storage scale | term | [Earth's atmosphere and aerial perspective](../light/atmosphere.md) |
| Stored form | term | [What an asset is](../assets/what-is-an-asset.md) |
| .stpak | term | Same as Asset pack: [Asset packs, export and patches](../assets/packs-export.md). |
| stpch.h | term | Same as Precompiled header: [Compiler flags, compile time and portability](../engineering/flags-portability.md). |
| `StrataCLI` | term | [`automation/mcp`](../automation/mcp.md) |
| `StrataEditorCore` | term | Same as Editor core: [`editor/program`](../editor/program.md). |
| `StrataRuntime` | term | Same as runtime: [What a game engine is: one frame, start to finish](../start/what-an-engine-is.md). |
| stratified | term | Same as stratified sampling: [Chance: probability, noise, integrals and Monte Carlo](../basics/math-probability.md). |
| stratified offsets | term | Same as stratified sampling: [Chance: probability, noise, integrals and Monte Carlo](../basics/math-probability.md). |
| stratified sampling | term | [Chance: probability, noise, integrals and Monte Carlo](../basics/math-probability.md) |
| Streaming distance | term | [The streamer](../worlds/streamer.md) |
| Streaming parser | term | [Scene documents: text, streams and the cooked form](../world/serialization.md) |
| Streaming queue | term | [Loading without stalling](../assets/loading.md) |
| Streaming source | term | [The streamer](../worlds/streamer.md) |
| `StreamingPanel::StartTableBuild` | identifier | [Instrument panels](../editor-ui/instrument-panels.md) |
| `StreamingPanel::UpdateTable` | identifier | [Instrument panels](../editor-ui/instrument-panels.md) |
| string | term | [`basics/programming-2`](../basics/programming-2.md) |
| string view | term | [Modern C++ as Strata uses it: move semantics, constexpr, optional, variant, span and concepts](../basics/cpp-modern.md) |
| struct | term | [`basics/programming-2`](../basics/programming-2.md) |
| struct of arrays | term | [Data structures I: arrays, lists, hash maps and their cost](../basics/data-structures.md) |
| `StructSize` | term | [`scripting/abi-sdk`](../scripting/abi-sdk.md) |
| Structural step | term | [`editor/recovery`](../editor/recovery.md) |
| Structure of arrays | term | [Data structures I: arrays, lists, hash maps and their cost](../basics/data-structures.md) |
| structured binding | term | [Modern C++ as Strata uses it: move semantics, constexpr, optional, variant, span and concepts](../basics/cpp-modern.md) |
| structured bindings | term | Same as structured binding: [Modern C++ as Strata uses it: move semantics, constexpr, optional, variant, span and concepts](../basics/cpp-modern.md). |
| Structured buffer | term | [Compute shaders: dispatches, thread groups, shared memory and atomics](../gpu/compute.md) |
| structured exception handling | term | Same as `SEH`: [Crash containment](../scripting/crash-containment.md). |
| `structuredContent` | term | [`automation/mcp`](../automation/mcp.md) |
| `STSK` | term | [Skeletons and forward kinematics](../animation/skeletons.md) |
| `STTX` | term | [`assets/texture-cooking`](../assets/texture-cooking.md) |
| .stworld | term | Same as World asset: [Grids, keys and layers](../worlds/grids.md). |
| Style | term | [Dear ImGui from first principles](../editor-ui/imgui.md) |
| style color | term | Same as Style: [Dear ImGui from first principles](../editor-ui/imgui.md). |
| style var | term | Same as Style: [Dear ImGui from first principles](../editor-ui/imgui.md). |
| Sub-asset | term | [Handles, .meta files and sub-assets](../assets/handles-meta.md) Used in [Bringing in assets](../make/assets.md). |
| Sub-scene | term | [Loading scenes: whole, additive and in slices](../world/sub-scenes.md) Used in [Levels, loading screens and save files](../make/levels-saves.md). |
| sub-scenes | term | Same as Sub-scene: [Loading scenes: whole, additive and in slices](../world/sub-scenes.md). |
| Sub-step | term | [Rigid body dynamics: integration, contacts, solvers, sleep and continuous collision](../physics/dynamics.md) |
| Sub-texel caster | term | [Sun shadows I: stable cascades](../light/sun-shadows-1.md) |
| subclass | term | Same as derived class: [`basics/programming-3`](../basics/programming-3.md). |
| Submesh | term | [`gpu/geometry-pool`](../gpu/geometry-pool.md) |
| submodule | term | [Installing Strata and the C++ build tools](../start/install.md) |
| Submodule (git) | term | [Third-party code and pinned tools](../engineering/third-party.md) |
| subnormal | term | Same as subnormal number: [Numbers in a computer: binary, integers, floating point and precision](../basics/numbers.md). |
| subnormal number | term | [Numbers in a computer: binary, integers, floating point and precision](../basics/numbers.md) |
| subnormal numbers | term | Same as subnormal number: [Numbers in a computer: binary, integers, floating point and precision](../basics/numbers.md). |
| subnormals | term | Same as subnormal number: [Numbers in a computer: binary, integers, floating point and precision](../basics/numbers.md). |
| Subpixel blend | term | [`image/spatial-aa`](../image/spatial-aa.md) |
| `SubSceneComponent` | term | [Loading scenes: whole, additive and in slices](../world/sub-scenes.md) |
| subtree | term | [`basics/trees-graphs`](../basics/trees-graphs.md) |
| Subtree range | term | [Rects, anchors and layout](../ui/layout.md) |
| subtrees | term | Same as subtree: [`basics/trees-graphs`](../basics/trees-graphs.md). |
| `Summarize` | identifier | [Measuring performance honestly: noise, percentiles, budgets and the perf lab](../engineering/perf-lab.md) |
| Sun-to-sky ratio | term | [Light by the numbers: radiometric and photometric units](../light/units-exposure.md) |
| `Supersampling (SSAA)` | term | [`image/spatial-aa`](../image/spatial-aa.md) |
| Support function | term | [Placing content](../editor/placement.md) |
| support point | term | [Collision detection: shapes, broad phase and narrow phase](../physics/collision-detection.md) |
| Suppression (capture) | term | [Players' bindings inside the engine: the bindings file and capture](../input/rebinding.md) |
| Surface | term | [Vulkan, NVRHI, the graphics device and the Renderer's services](../gpu/vulkan-nvrhi.md) |
| surface normal | term | [Vectors: length, direction, dot and cross products](../basics/math-vectors.md) |
| surface target | term | Same as Prepass: [Screen-space reflections](../indirect/ssr.md). |
| Surrogate | term | [Input devices and per-frame state](../input/devices-state.md) |
| Suspended body | term | [From entities to bodies: records, shapes, mesh colliders](../physics/building-bodies.md) |
| Suspended input frames | term | [Input devices and per-frame state](../input/devices-state.md) |
| `SV_VulkanInstanceID` | term | [Batching and instancing](../draw/batching.md) |
| swap and pop | term | Same as swap-remove: [Data structures I: arrays, lists, hash maps and their cost](../basics/data-structures.md). |
| swap-remove | term | [Data structures I: arrays, lists, hash maps and their cost](../basics/data-structures.md) |
| Swapchain | term | [`gpu/how-a-gpu-frame-works`](../gpu/how-a-gpu-frame-works.md) |
| Sweep | term | [Inside StrataTests](../engineering/test-program.md) |
| sweep and prune | term | [Collision detection: shapes, broad phase and narrow phase](../physics/collision-detection.md) |
| `.Sweep` suite | term | Same as Sweep: [Inside StrataTests](../engineering/test-program.md). |
| sweep-and-prune | term | Same as sweep and prune: [Collision detection: shapes, broad phase and narrow phase](../physics/collision-detection.md). |
| switch statement | term | [Programming from zero I: values, variables, expressions and decisions](../basics/programming-1.md) |
| symbol | term | [How a C++ program is built: from two files by hand to CMake](../basics/build.md) |
| Symbolization | term | [From an address to a file and line](../scripting/symbolization.md) |
| symplectic Euler | term | Same as semi-implicit Euler method: [Change over time: rates, accumulation, Euler steps and Newton's laws](../basics/math-change.md). |
| sync | term | Same as Synchronization: [`physics/world-step`](../physics/world-step.md). |
| Sync markers | term | [Blending and cross-fades](../animation/blending.md) |
| Sync point | term | [The script system](../scripting/script-system.md) |
| synced hash | term | [How prefab instances stay linked](../editor/prefab-instances.md) |
| Synchronization | term | [`physics/world-step`](../physics/world-step.md) |
| `SYSTEM include` | term | [Compiler flags, compile time and portability](../engineering/flags-portability.md) |
| `TAA` | term | [Temporal anti-aliasing](../image/taa.md) |
| `TAA history` | term | Same as History: [Temporal anti-aliasing](../image/taa.md). |
| tab bar | term | Same as Dock space: [Dear ImGui from first principles](../editor-ui/imgui.md). |
| Tag (git) | term | [Version control with git](../basics/git.md) |
| Tag component | term | [Entities and components, with EnTT inside](../world/ecs.md) |
| Tangent | term | [Clips: sampling motion](../animation/clips.md) |
| tangent frame | term | Same as tangent space: [Bases, determinants and normals: orthonormal frames, tangent space, mirrors and the inverse transpose](../basics/math-bases.md). |
| tangent function | term | [Vectors: length, direction, dot and cross products](../basics/math-vectors.md) |
| Tangent handedness | term | [Mirrors, normals and camera-relative positions](../draw/mirrors-camera-relative.md) |
| tangent space | term | [Bases, determinants and normals: orthonormal frames, tangent space, mirrors and the inverse transpose](../basics/math-bases.md) |
| target | term | [Measuring performance honestly: noise, percentiles, budgets and the perf lab](../engineering/perf-lab.md) |
| `Target (CMake)` | term | [Inside Strata's CMake](../engineering/cmake.md) |
| task graph | term | [Threads and the job system](../core/jobs.md) |
| task graphs | term | Same as task graph: [Threads and the job system](../core/jobs.md). |
| tau | term | Same as time constant: [Blending and smoothing: lerp, easing, curves and exponential smoothing](../basics/math-interpolation.md). |
| `TCP` | term | [`automation/json-rpc`](../automation/json-rpc.md) |
| Teleport | term | [Drawing between fixed steps](../world/interpolation.md) |
| Teleport (audio) | term | [Sound in space](../audio/spatial.md) |
| Template | term | [Opening projects and scenes: templates, background loads and migration](../editor/projects.md) |
| template argument | term | [`basics/programming-3`](../basics/programming-3.md) |
| Template id | term | Same as Prefab (world): [Prefabs: the data model](../world/prefabs.md). |
| temporal upscaling | term | Same as Render scale: [Quality settings and players' graphics options](../image/quality-settings.md). |
| Tent filter (image) | term | [Lens effects: bloom, vignette, flares and fringes](../image/lens-effects.md) |
| Tent filter (light) | term | [`light/sun-shadows-2`](../light/sun-shadows-2.md) |
| Tent kernel | term | [Ambient occlusion without history](../indirect/ao.md) |
| terminal | term | [The tools: the terminal, files and a code editor](../basics/tools.md) |
| terminal command | term | [The tools: the terminal, files and a code editor](../basics/tools.md) |
| `Tests::WaitUntil` | identifier | [Testing an engine](../engineering/testing.md) |
| `TetrisBoard::ShowCell` | identifier | [Patterns for game code: state machines, managers and object pools](../make/patterns.md) |
| Texel density (draw) | term | [Mip streaming](../draw/mip-streaming.md) |
| Texel density (light) | term | [Sun shadows I: stable cascades](../light/sun-shadows-1.md) |
| Texel snapping | term | [Sun shadows I: stable cascades](../light/sun-shadows-1.md) |
| Text buffer protocol | term | Same as Buffer protocol: [`scripting/abi-sdk`](../scripting/abi-sdk.md). |
| text character | term | [Bytes in files and memory: layouts, byte order and text encodings](../basics/bytes.md) |
| text encoding | term | [Bytes in files and memory: layouts, byte order and text encodings](../basics/bytes.md) |
| Text shaping | term | [Text: fonts, shaping and signed distance fields](../gpu/text.md) |
| text string | term | Same as string: [`basics/programming-2`](../basics/programming-2.md). |
| texture coordinates | term | [`gpu/coordinates`](../gpu/coordinates.md) |
| Texture table (Strata) | term | [Pipelines and binding: layouts, registers and bindless](../gpu/binding.md) |
| Texture table index | term | Same as Texture table (Strata): [Pipelines and binding: layouts, registers and bindless](../gpu/binding.md). |
| `Texture::FinalizeOnMainThread` | identifier | [Budgeted uploads](../assets/uploads.md) |
| `Texture::UploadLevels` | identifier | [Budgeted uploads](../assets/uploads.md) |
| `TextureImporter::ChooseFormat` | identifier | [`assets/texture-cooking`](../assets/texture-cooking.md) |
| `TextureImporter::Decode` | identifier | [`assets/texture-cooking`](../assets/texture-cooking.md) |
| Theme | term | [The design system: theme, fonts, icons](../editor-ui/design-system.md) |
| Thickness tolerance | term | [Screen-space reflections](../indirect/ssr.md) |
| Thin lens | term | [Depth of field](../image/depth-of-field.md) |
| `ThirdPerson::GetSettings` | identifier | [Levels, loading screens and save files](../make/levels-saves.md) |
| thread | term | [Threads, atomics and races](../basics/threads.md) |
| Thread (gpu) | term | [Compute shaders: dispatches, thread groups, shared memory and atomics](../gpu/compute.md) |
| thread group | term | [Compute shaders: dispatches, thread groups, shared memory and atomics](../gpu/compute.md) |
| thread pool | term | [Threads, atomics and races](../basics/threads.md) |
| Thread priority | term | [Talking to the operating system](../core/platform.md) |
| Thread-local | term | [Threads, atomics and races](../basics/threads.md) |
| Threat model | term | [The security model](../automation/security.md) |
| Thumbnail cache | term | [Thumbnails](../editor/thumbnails.md) |
| thumbnail key | term | Same as Key (editor): [Thumbnails](../editor/thumbnails.md). |
| `ThumbnailCache::ComputeKey` | identifier | [Thumbnails](../editor/thumbnails.md) |
| `ThumbnailCache::StartQueued` | identifier | [Thumbnails](../editor/thumbnails.md) |
| `ThumbnailCache::StartTextureJob` | identifier | [Thumbnails](../editor/thumbnails.md) |
| `ThumbnailCache::UpdateSceneJob` | identifier | [Thumbnails](../editor/thumbnails.md) |
| Thunk | term | [`scripting/abi-sdk`](../scripting/abi-sdk.md) |
| Tick (networking) | term | [Networking for games, in general](../appendix/networking.md) |
| tick rate | term | Same as Tick (networking): [Networking for games, in general](../appendix/networking.md). |
| Ticket (upload) | term | [Staging and the upload queue](../gpu/upload-queue.md) |
| tile | term | [Shadows of point and spot lights](../light/local-shadows.md) |
| Tile max | term | [Motion blur](../image/motion-blur.md) |
| Tile-based renderer | term | [`gpu/readback-timing`](../gpu/readback-timing.md) |
| time constant | term | [Blending and smoothing: lerp, easing, curves and exponential smoothing](../basics/math-interpolation.md) |
| time dilation | term | [Time: delta time, the fixed step and time scale](../core/time.md) Used in [The game loop from a script's side](../make/script-loop.md). |
| Time scale | term | [Time: delta time, the fixed step and time scale](../core/time.md) Used in [The game loop from a script's side](../make/script-loop.md). |
| time step | term | [Change over time: rates, accumulation, Euler steps and Newton's laws](../basics/math-change.md) |
| Timestamp query | term | [`gpu/readback-timing`](../gpu/readback-timing.md) |
| timestep | term | Same as time step: [Change over time: rates, accumulation, Euler steps and Newton's laws](../basics/math-change.md). |
| Tint | term | [White balance, grading and lookup tables](../image/grading.md) |
| Toast | term | [Status bar, toasts and idle throttling](../editor-ui/status.md) |
| `ToCellCoordinate` | identifier | [Grids, keys and layers](../worlds/grids.md) |
| `TOCTOU` | term | [Files you can trust](../core/files.md) |
| Toe | term | [Tone mapping and the Filmic curve](../image/tone-mapping.md) |
| Toggle group | term | [Menus: buttons, navigation, pause and settings screens](../make/menus.md) |
| Token | term | [The design system: theme, fonts, icons](../editor-ui/design-system.md) |
| Token bucket | term | [Building blocks and recipes](../make/recipes.md) |
| `Tokens (LLM)` | term | [How the editor makes games with agents](../automation/agents.md) |
| tolerance | term | [Geometry for engines: rays, planes, boxes and intersection tests](../basics/math-geometry.md) |
| tone curve | term | Same as tone mapping (image): [Why images need post-processing, and Strata's post chain](../image/why-post.md). |
| tone mapping (image) | term | [Why images need post-processing, and Strata's post chain](../image/why-post.md) |
| Tone mapping (make) | term | [The camera's image](../make/look.md) |
| Tool | term | [How the editor makes games with agents](../automation/agents.md) |
| toolchain | term | Same as build tools: [Installing Strata and the C++ build tools](../start/install.md). |
| Tooling layer | term | [Layers, registries and the composition root](../core/layers-registries.md) |
| `tools/list_changed` | term | [`automation/mcp`](../automation/mcp.md) |
| Toolset | term | [`automation/mcp`](../automation/mcp.md) |
| Topological order (basics) | term | [`basics/trees-graphs`](../basics/trees-graphs.md) |
| Topological order (parents first) | term | [Skeletons and forward kinematics](../animation/skeletons.md) |
| Topological sort | term | [Engine modules](../core/engine-modules.md) |
| Toroidal addressing | term | [Global illumination I: a voxel copy of the world](../indirect/gi-voxels.md) |
| Touching pair | term | [Contacts and triggers](../physics/contacts-triggers.md) |
| `TPDF` | term | [Encoding, dithering and grain](../image/encoding.md) |
| Tracy | term | [Measuring the frame: the frame profiler, Tracy and the method](../core/profiling.md) |
| trail | term | [Finding your way in a large codebase](../core/reading-code.md) |
| transfer function | term | [`basics/color`](../basics/color.md) |
| Transfer queue | term | [Staging and the upload queue](../gpu/upload-queue.md) |
| transform | term | [`basics/math-matrices`](../basics/math-matrices.md) Used in [Scenes, entities and components](../make/scenes-entities.md). |
| Transform contract | term | [The scene graph: hierarchy, transforms and the transform contract](../world/scene-graph.md) |
| transform hierarchy | term | [`basics/math-matrices`](../basics/math-matrices.md) |
| transformation | term | Same as transform: [`basics/math-matrices`](../basics/math-matrices.md). |
| Transition (animation) | term | [State machines](../animation/state-machines.md) |
| transition (make) | term | [Animation for game makers](../make/animation.md) |
| Transition (ui) | term | [`ui/input`](../ui/input.md) |
| translation | term | [`basics/math-matrices`](../basics/math-matrices.md) |
| translation unit | term | [How a C++ program is built: from two files by hand to CMake](../basics/build.md) |
| Transmission | term | [Transparency, clear coat and glass](../light/clearcoat-transmission.md) |
| Transmittance (indirect) | term | [`indirect/gi-cascades`](../indirect/gi-cascades.md) |
| transmittance (light) | term | [Earth's atmosphere and aerial perspective](../light/atmosphere.md) |
| transpose | term | [Bases, determinants and normals: orthonormal frames, tangent space, mirrors and the inverse transpose](../basics/math-bases.md) |
| transposed matrix | term | Same as transpose: [Bases, determinants and normals: orthonormal frames, tangent space, mirrors and the inverse transpose](../basics/math-bases.md). |
| Trash | term | [The trash and references](../editor/trash-references.md) |
| tree | term | [`basics/trees-graphs`](../basics/trees-graphs.md) |
| Triangle mesh collider | term | [Rigid bodies and colliders](../physics/bodies-colliders.md) |
| `Triangle-box overlap (Akenine-Moller)` | term | [Global illumination I: a voxel copy of the world](../indirect/gi-voxels.md) |
| triangle-mesh collider | term | Same as mesh collider: [Project: a third-person platformer](../make/project-platformer.md). |
| triangular dither | term | Same as `TPDF`: [Encoding, dithering and grain](../image/encoding.md). |
| Trigger | term | [Contacts and triggers](../physics/contacts-triggers.md) Used in [Physics for game makers](../make/physics.md). |
| trigger parameter | term | [Animation for game makers](../make/animation.md) |
| Trilinear interpolation | term | [White balance, grading and lookup tables](../image/grading.md) |
| Trim | term | [Residency, eviction and pins](../assets/residency.md) |
| Trowbridge-Reitz | term | Same as `GGX`: [How surfaces reflect light: the reflection equation and microfacets](../light/reflectance.md). |
| `TRS` | term | [`basics/math-matrices`](../basics/math-matrices.md) |
| `TrueType` | term | [Text: fonts, shaping and signed distance fields](../gpu/text.md) |
| truncate | term | Same as Ellipsis: [Text and text fields](../ui/text.md). |
| tutorial checkpoint | term | [How to read this book](../start/how-to-read.md) |
| two's complement | term | [Numbers in a computer: binary, integers, floating point and precision](../basics/numbers.md) |
| Two-phase occlusion culling | term | [Occlusion culling](../draw/occlusion.md) |
| Two-sided voxel | term | [Global illumination I: a voxel copy of the world](../indirect/gi-voxels.md) |
| type | term | [Programming from zero I: values, variables, expressions and decisions](../basics/programming-1.md) |
| type argument | term | [Generic C++: templates, lambdas and the standard containers](../basics/cpp-generic.md) |
| type arguments | term | Same as type argument: [Generic C++: templates, lambdas and the standard containers](../basics/cpp-generic.md). |
| type erasure | term | [Generic C++: templates, lambdas and the standard containers](../basics/cpp-generic.md) |
| Type scale | term | [The design system: theme, fonts, icons](../editor-ui/design-system.md) |
| type trait | term | [Modern C++ as Strata uses it: move semantics, constexpr, optional, variant, span and concepts](../basics/cpp-modern.md) |
| type traits | term | Same as type trait: [Modern C++ as Strata uses it: move semantics, constexpr, optional, variant, span and concepts](../basics/cpp-modern.md). |
| Typed text | term | [How input reaches a game: events, polling, edges and intents](../input/how-input-works.md) |
| `UAV` | term | [Compute shaders: dispatches, thread groups, shared memory and atomics](../gpu/compute.md) |
| `UB` | term | Same as undefined behavior: [`basics/cpp-memory`](../basics/cpp-memory.md). |
| `UI actions` | term | Same as `UI map`: [Input actions](../input/actions.md). |
| `UI contract` | term | [`ui/contract`](../ui/contract.md) |
| `UI element` | term | [`ui/what-game-ui-does`](../ui/what-game-ui-does.md) |
| `UI harness` | term | [`editor-ui/ui-testing`](../editor-ui/ui-testing.md) |
| `UI map` | term | [Input actions](../input/actions.md) |
| `UI scale` | term | [`editor-ui/ui-scale`](../editor-ui/ui-scale.md) |
| `UI::DrawNotifications` | identifier | [Status bar, toasts and idle throttling](../editor-ui/status.md) |
| `UIActionState::Update` | identifier | [Input actions](../input/actions.md) |
| Umbra | term | [`light/sun-shadows-2`](../light/sun-shadows-2.md) |
| undefined behavior | term | [`basics/cpp-memory`](../basics/cpp-memory.md) |
| Underrun | term | [Sound inside a computer](../audio/sound-in-a-computer.md) |
| Undo merge | term | [Undo and redo](../editor/undo.md) |
| Undo stack | term | [Undo and redo](../editor/undo.md) |
| Undo step | term | [Undo and redo](../editor/undo.md) |
| `UndoStack::IsModified` | identifier | [Undo and redo](../editor/undo.md) |
| `UndoStack::MarkSaved` | identifier | [Undo and redo](../editor/undo.md) |
| `UndoStack::Push` | identifier | [Undo and redo](../editor/undo.md) |
| `UndoStack::Undo` | identifier | [Undo and redo](../editor/undo.md) |
| Unicode | term | [Bytes in files and memory: layouts, byte order and text encodings](../basics/bytes.md) |
| Uniform (distribution) | term | [Chance: probability, noise, integrals and Monte Carlo](../basics/math-probability.md) |
| Uniform branch | term | [`gpu/how-a-gpu-frame-works`](../gpu/how-a-gpu-frame-works.md) |
| uniform distribution | term | Same as Uniform (distribution): [Chance: probability, noise, integrals and Monte Carlo](../basics/math-probability.md). |
| Uniform grid | term | [`ui/input`](../ui/input.md) |
| Uniform grid (physics) | term | [Collision detection: shapes, broad phase and narrow phase](../physics/collision-detection.md) |
| union-find | term | [`basics/trees-graphs`](../basics/trees-graphs.md) |
| unique pointer | term | [`basics/cpp-memory`](../basics/cpp-memory.md) |
| unit circle | term | [Vectors: length, direction, dot and cross products](../basics/math-vectors.md) |
| unit sphere | term | [Directions on a sphere: solid angles, spherical harmonics and octahedral maps](../basics/math-sphere.md) |
| unit vector | term | [Vectors: length, direction, dot and cross products](../basics/math-vectors.md) |
| `UnitCirclePoint` | identifier | [Overlays, debug drawing and gizmos](../gpu/debug-drawing.md) |
| universally unique identifier | term | Same as `UUID`: [`basics/data-formats`](../basics/data-formats.md). |
| Unknown component | term | [Scene documents: text, streams and the cooked form](../world/serialization.md) |
| `UNORM` | term | [Vulkan, NVRHI, the graphics device and the Renderer's services](../gpu/vulkan-nvrhi.md) |
| Unpack | term | [Prefabs: the data model](../world/prefabs.md) Used in [Prefabs](../make/prefabs.md). |
| unscaled time | term | [Time: delta time, the fixed step and time scale](../core/time.md) Used in [Timers, time scale and events between scripts](../make/timers-events.md). |
| unsigned integer | term | [Numbers in a computer: binary, integers, floating point and precision](../basics/numbers.md) |
| `until` | term | [Command scripts and batches](../editor/command-scripts.md) |
| untrusted file | term | Same as untrusted input: [Corruption, crash safety and cancellation](../assets/robustness.md). |
| untrusted input | term | [Corruption, crash safety and cancellation](../assets/robustness.md) |
| Unwritten settings | term | [Saving without stalling](../editor/saving.md) |
| up axis | term | [`basics/math-matrices`](../basics/math-matrices.md) |
| update method | term | [Patterns for game code: state machines, managers and object pools](../make/patterns.md) |
| Update order | term | [The script system](../scripting/script-system.md) |
| Update phases | term | [Systems, phases and fixed steps](../world/systems.md) |
| Update-after-bind | term | [Pipelines and binding: layouts, registers and bindless](../gpu/binding.md) |
| Upload | term | [Budgeted uploads](../assets/uploads.md) |
| upload batch | term | Same as Batch (gpu): [Staging and the upload queue](../gpu/upload-queue.md). |
| Upload budget (draw) | term | [`draw/render-scene-gpu`](../draw/render-scene-gpu.md) |
| Upload budget (gpu) | term | [Staging and the upload queue](../gpu/upload-queue.md) |
| Upload context | term | [Budgeted uploads](../assets/uploads.md) |
| Upload step | term | [Budgeted uploads](../assets/uploads.md) |
| usage requirements | term | [Inside Strata's CMake](../engineering/cmake.md) |
| user data | term | Same as user pointer: [Generic C++: templates, lambdas and the standard containers](../basics/cpp-generic.md). |
| user data folder | term | [The tools: the terminal, files and a code editor](../basics/tools.md) |
| user pointer | term | [Generic C++: templates, lambdas and the standard containers](../basics/cpp-generic.md) |
| user scope | term | [Projects and settings](../world/projects-settings.md) |
| `UTF-16` | term | Same as `UTF-8`: [Bytes in files and memory: layouts, byte order and text encodings](../basics/bytes.md). |
| `UTF-8` | term | [Bytes in files and memory: layouts, byte order and text encodings](../basics/bytes.md) |
| `UTF-8 continuation byte` | term | [Bytes in files and memory: layouts, byte order and text encodings](../basics/bytes.md) |
| `utility AI` | term | [`appendix/game-ai`](../appendix/game-ai.md) |
| `UUID` | term | [`basics/data-formats`](../basics/data-formats.md) |
| `UV` | term | Same as texture coordinates: [`gpu/coordinates`](../gpu/coordinates.md). |
| `UV coordinates` | term | Same as texture coordinates: [`gpu/coordinates`](../gpu/coordinates.md). |
| `UVPixels` | term | Same as Texel density (draw): [Mip streaming](../draw/mip-streaming.md). |
| V-sync | term | Same as vsync: [The frame loop](../core/frame-loop.md). |
| validated crossing | term | [Screen-space reflections](../indirect/ssr.md) |
| Validation | term | [`ui/contract`](../ui/contract.md) |
| Validation layer | term | [Vulkan, NVRHI, the graphics device and the Renderer's services](../gpu/vulkan-nvrhi.md) |
| validity | term | [`indirect/gi-cascades`](../indirect/gi-cascades.md) |
| value | term | [Programming from zero I: values, variables, expressions and decisions](../basics/programming-1.md) |
| variable | term | [Programming from zero I: values, variables, expressions and decisions](../basics/programming-1.md) |
| variance | term | [Chance: probability, noise, integrals and Monte Carlo](../basics/math-probability.md) |
| variance clipping | term | [Temporal anti-aliasing](../image/taa.md) |
| Variant (basics) | term | [Modern C++ as Strata uses it: move semantics, constexpr, optional, variant, span and concepts](../basics/cpp-modern.md) |
| Variant (shader) | term | [Shaders: Slang, the build and the dialect](../gpu/shaders.md) |
| vector | term | [Vectors: length, direction, dot and cross products](../basics/math-vectors.md) |
| vector component | term | Same as coordinate: [Vectors: length, direction, dot and cross products](../basics/math-vectors.md). |
| vector length | term | [Vectors: length, direction, dot and cross products](../basics/math-vectors.md) |
| velocity | term | [Change over time: rates, accumulation, Euler steps and Newton's laws](../basics/math-change.md) |
| velocity target | term | Same as Motion vector: [Motion vectors and motion history](../draw/motion-vectors.md). |
| Vendoring | term | [Third-party code and pinned tools](../engineering/third-party.md) |
| Version | term | [The render scene: persistent proxies](../draw/render-scene.md) |
| version control | term | [Version control with git](../basics/git.md) |
| vertex pulling | term | Same as Instancing: [`ui/drawing`](../ui/drawing.md). |
| vertical slice | term | [Planning a small game: the core loop, scope, prototype and playtest](../make/designing-a-game.md) |
| vertical synchronization | term | Same as vsync: [The frame loop](../core/frame-loop.md). |
| View | term | [Entities and components, with EnTT inside](../world/ecs.md) |
| view bias (indirect) | term | [`indirect/gi-cascades`](../indirect/gi-cascades.md) |
| View bias (worlds) | term | [The streamer](../worlds/streamer.md) |
| view frustum | term | [Cameras and projection: perspective, homogeneous coordinates and depth](../basics/math-projection.md) |
| view matrix | term | [Cameras and projection: perspective, homogeneous coordinates and depth](../basics/math-projection.md) |
| view space | term | [Cameras and projection: perspective, homogeneous coordinates and depth](../basics/math-projection.md) |
| viewport | term | Same as Scene view: [The Scene view](../editor-ui/scene-view.md). |
| Viewport (input) | term | [The mouse, the cursor and the game view](../input/mouse-cursor.md) |
| Viewport capture | term | [Automated play-tests](../make/automated-playtests.md) |
| Viewport flip | term | [`gpu/coordinates`](../gpu/coordinates.md) |
| `ViewportPanel::DrawDebugViewLegend` | identifier | [The Scene view](../editor-ui/scene-view.md) |
| `ViewportPanel::GetWindowOptions` | identifier | [The Scene view](../editor-ui/scene-view.md) |
| `ViewportPanel::HandleShortcuts` | identifier | [The Game view, shortcuts and who owns the keyboard](../editor-ui/game-view.md) |
| `ViewportPanel::OnImGuiRender` | identifier | [The Scene view](../editor-ui/scene-view.md) |
| `ViewportPanel::UpdateCamera` | identifier | [The Scene view](../editor-ui/scene-view.md) |
| Vignette | term | [Lens effects: bloom, vignette, flares and fringes](../image/lens-effects.md) |
| virtual device | term | Same as Simulated input: [Simulated input](../input/simulated.md). |
| virtual function | term | [C++ classes in depth: inheritance, virtual calls and interfaces](../basics/cpp-classes.md) |
| virtual table | term | [C++ classes in depth: inheritance, virtual calls and interfaces](../basics/cpp-classes.md) |
| virtual tables | term | Same as virtual table: [C++ classes in depth: inheritance, virtual calls and interfaces](../basics/cpp-classes.md). |
| Virtualization | term | [Lists that scale](../editor-ui/lists.md) |
| Visibility feedback | term | [`draw/gpu-driven`](../draw/gpu-driven.md) |
| Visibility parity | term | [Occlusion culling](../draw/occlusion.md) |
| visual scripting | term | [What Strata is and what this book teaches](../start/welcome.md) |
| Visual state | term | [`ui/input`](../ui/input.md) |
| Vogel disk | term | [Chance: probability, noise, integrals and Monte Carlo](../basics/math-probability.md) |
| Vogel spiral | term | Same as Vogel disk: [Chance: probability, noise, integrals and Monte Carlo](../basics/math-probability.md). |
| Voice | term | [Sound inside a computer](../audio/sound-in-a-computer.md) |
| Voice stealing | term | [The audio engine](../audio/engine.md) |
| volatile constant buffer | term | [Resources and lifetimes](../gpu/resources-lifetimes.md) |
| Voxel | term | [Global illumination I: a voxel copy of the world](../indirect/gi-voxels.md) |
| voxel guard | term | [`indirect/gi-cascades`](../indirect/gi-cascades.md) |
| voxelization | term | [Global illumination I: a voxel copy of the world](../indirect/gi-voxels.md) |
| vsync | term | [The frame loop](../core/frame-loop.md) |
| vtable | term | Same as virtual table: [C++ classes in depth: inheritance, virtual calls and interfaces](../basics/cpp-classes.md). |
| Vulkan | term | [Vulkan, NVRHI, the graphics device and the Renderer's services](../gpu/vulkan-nvrhi.md) |
| `VulkanGraphicsDevice::BeginFrame` | identifier | [`gpu/how-a-gpu-frame-works`](../gpu/how-a-gpu-frame-works.md) |
| `WaitForEditorProject` | identifier | [Sessions, discovery and launching](../automation/sessions.md) |
| `WaitsForAssets` | term | [Commands that take frames](../editor/deferred-commands.md) |
| Wanted cell | term | [The streamer](../worlds/streamer.md) |
| Wanted level | term | [Mip streaming](../draw/mip-streaming.md) |
| Watchdog | term | [Crash containment](../scripting/crash-containment.md) |
| Waveform (preview) | term | [Inspectors from reflection](../editor-ui/inspectors.md) |
| `WhenVisible animator` | term | Same as Culling mode: [Animating only what is seen](../animation/culling.md). |
| while loop | term | [`basics/programming-2`](../basics/programming-2.md) |
| White balance | term | [White balance, grading and lookup tables](../image/grading.md) |
| White furnace test | term | [`light/energy`](../light/energy.md) |
| white noise | term | [Chance: probability, noise, integrals and Monte Carlo](../basics/math-probability.md) |
| white point | term | [`basics/color`](../basics/color.md) |
| Widget kit | term | [The widget kit](../editor-ui/widget-kit.md) |
| Winding | term | [`gpu/coordinates`](../gpu/coordinates.md) |
| Winding order | term | [`gpu/coordinates`](../gpu/coordinates.md) |
| Window | term | [Dear ImGui from first principles](../editor-ui/imgui.md) |
| Window backend | term | [Windows, events and layers](../core/windows-events.md) |
| Work budget | term | [Loading scenes: whole, additive and in slices](../world/sub-scenes.md) |
| work stealing | term | [Threads and the job system](../core/jobs.md) |
| Work time | term | [The frame loop](../core/frame-loop.md) |
| workflow | term | [Continuous integration](../engineering/ci.md) |
| workflows | term | Same as workflow: [Continuous integration](../engineering/ci.md). |
| workgroup | term | Same as thread group: [Compute shaders: dispatches, thread groups, shared memory and atomics](../gpu/compute.md). |
| working color space | term | [`basics/color`](../basics/color.md) |
| working folder | term | Same as current folder: [The tools: the terminal, files and a code editor](../basics/tools.md). |
| worktree | term | [Version control with git](../basics/git.md) |
| worktrees | term | Same as worktree: [Version control with git](../basics/git.md). |
| World (editor-ui) | term | [The Scene view](../editor-ui/scene-view.md) |
| World (worlds) | term | [Why levels must stream](../worlds/why-streaming.md) |
| World asset | term | [Grids, keys and layers](../worlds/grids.md) |
| world cook | term | [Worlds meet physics and scripts](../worlds/physics-scripts.md) |
| World position | term | [Positions, rotations and units](../make/transforms-units.md) |
| world space | term | [`basics/math-matrices`](../basics/math-matrices.md) |
| world space (render mode) | term | Same as Screen space: [`ui/what-game-ui-does`](../ui/what-game-ui-does.md). |
| world transform | term | [`basics/math-matrices`](../basics/math-matrices.md) |
| `WorldAsset::FindCell` | identifier | [Grids, keys and layers](../worlds/grids.md) |
| `WorldCellKey` | term | Same as Cell key: [Grids, keys and layers](../worlds/grids.md). |
| `WorldCellKey::Pack` | identifier | [Grids, keys and layers](../worlds/grids.md) |
| `WorldCook::ComputeMaxBodiesInRadius` | identifier | [Worlds meet physics and scripts](../worlds/physics-scripts.md) |
| `WorldData::Validate` | identifier | [Grids, keys and layers](../worlds/grids.md) |
| `WorldGrid::Distance` | identifier | [Grids, keys and layers](../worlds/grids.md) |
| `WorldIndex::GetRecommendedMaxBodies` | identifier | [Worlds meet physics and scripts](../worlds/physics-scripts.md) |
| `WorldStreamer::ReserveBodies` | identifier | [Worlds meet physics and scripts](../worlds/physics-scripts.md) |
| `WorldStreamingSystem::GatherSources` | identifier | [Worlds meet physics and scripts](../worlds/physics-scripts.md) |
| `WorldStreamingSystem::OnUpdate` | identifier | [Worlds meet physics and scripts](../worlds/physics-scripts.md) |
| `WorldStreamingSystem::PrepareLoadedScene` | identifier | [Worlds meet physics and scripts](../worlds/physics-scripts.md) |
| `WorldStreamingSystem::RequestCellsAround` | identifier | [Worlds meet physics and scripts](../worlds/physics-scripts.md) |
| write log | term | Same as Write version: [Motion vectors and motion history](../draw/motion-vectors.md). |
| write pass | term | Same as Counting pass: [`draw/gpu-driven`](../draw/gpu-driven.md). |
| Write version | term | [Motion vectors and motion history](../draw/motion-vectors.md) |
| write-ahead ordering | term | [Corruption, crash safety and cancellation](../assets/robustness.md) |
| Write-back | term | [`physics/world-step`](../physics/world-step.md) |
| `WriteFileAtomically` | identifier | [Generated code: shaders, embedded files, version stamps and committed generators](../engineering/generated-code.md) |
| X-macro | term | [`scripting/host-api`](../scripting/host-api.md) |
| yaw | term | Same as yaw angle: [Rotations and quaternions](../basics/math-rotations.md). |
| yaw angle | term | [Rotations and quaternions](../basics/math-rotations.md) |
| `YCoCg` | term | [Temporal anti-aliasing](../image/taa.md) |
| z-buffer | term | Same as depth buffer: [Cameras and projection: perspective, homogeneous coordinates and depth](../basics/math-projection.md). |
| Z-order | term | Same as Morton order: [Numbers in a computer: binary, integers, floating point and precision](../basics/numbers.md). |
| zstd | term | [Asset packs, export and patches](../assets/packs-export.md) |

## Where it lives in Strata

- `src/content/glossary.json`: the book's file of terms, with the home page of each, the source of every term row.
- The quoted excerpts of the book's pages: each names the function, class or type it shows, and that name is the source of every identifier row.
- `Strata/src/Strata/Scene/Scene.cpp`: one of the engine files whose functions the excerpts quote, and so one source of identifier rows.
