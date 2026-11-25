# Allocation: appendix

## `appendix/not-in-strata` — What Strata does not do, and how engines do it

**Covers.** The problem as a reader meets it: someone who has used another engine looks for particles, a navigation
mesh or multiplayer, finds no menu for it, and cannot tell whether Strata lacks the feature or hides it. The naive
answers are to guess from memory or to read a missing menu as a missing feature; both mislead, and the book states no
absence without its evidence at the pin. The idea: an engine is a set of choices of scope, and each absence is one of
three things: a decision with a reason (Strata never renders below native resolution), work the engine's own documents
plan (quoted, never dated or promised, `style.md` §13), or work left to game code and engine changes. The approaches
engines take to scope (build it in, ship middleware beside the engine, load plugins at run time, leave it to game code),
in one short table with sources. Strata's choice: modules chosen at compile time with `ST_WITH_*`, game code in script
modules, and no engine plugins loaded at run time (two rows of the first area, `new:9` and `new:10`, state it).

Then the index, one section per area in the order of `book.md`'s table: assets, core and platform; scenes, prefabs and
editing; rendering; physics; animation; audio; input; scripting; game UI; editor, export and automation; gameplay;
building, testing and the GPU; and the entries checked when the W8 pages are written. Each entry is one row: what
Strata does not have, the page that states it (linked), and the evidence. After each area's rows comes the general
technique behind its absences, grouped (for rendering: particles, trails, decals, billboards, terrain and water; MSAA,
HDR output, post volumes and toon shading; ray tracing, lightmaps, run-time probes and transparency; mesh shaders,
render graphs, portals and virtual shadow maps; a second view, skies with clouds, light cookies and IES profiles, and
material parameters per entity; for building and testing: asynchronous compute, shader debug information, unity
builds and package managers, measured coverage, fuzzers and sanitizers, signed releases), one paragraph per group
with a source in Further reading. The page does not repeat a subsystem page's paragraph: it gives the technique across
the area, and the subsystem page says what Strata offers instead.

A last section reads the release's own lists: "Known issues" and "Not in this release" of `Docs/Releases/0.8.0.md` at
the tag. At the pin the newest are 0.7.0's (`Docs/Releases/0.7.0.md:308-416`) and the draft of 0.8.0's notes that each
landing of wave 8 adds to (`Docs/Plans/Wave8/ReleaseNotes.md`, "Known issues" at 369-504, which has no "Not in this
release" yet). Each line is mapped to a row of the index, or named as a limit of a feature Strata has (stated on that
feature's page), or sent to the planner when no row holds it. The writer also checks that every line of the curricula
checklist marked "S-none" or "S?" (`research/curricula.md` §1) is a row here or a feature with a home page (light
culling, for example, is `light/many-lights`'). Common mistakes: stating an absence from memory; reading a cap of a
feature as an absence; repeating a plan of the Roadmap as a promise; taking a known issue of an older release as true
at the pin (0.7.0's line on the fixed timestep is half out of date: the project's `Scene.Timing` now sets a fixed
rate). The writer runs every entry's evidence again at the tag (`book.md`, "What Strata does not do", rule 6). The
exercises: a command script that lists the components and commands and shows that none is one of three absent
features, two rows' searches run at the pin with the matches that are not the feature named, and a design exercise
that places particles under Strata's choice of scope. At the end the reader knows, for any feature, whether Strata has
it, where the book says so, and what technique would fill the gap.

**Leaves out.**

- Each absence's own paragraph, with what Strata offers instead → `animation/limits`, `indirect/gi-limits`, `physics/why`, `gpu/frame-tour`
- Networking for games in general → `appendix/networking`
- Game AI in general → `appendix/game-ai`
- What each release added → `appendix/history`
- Caps and limits of the features Strata has (counts, sizes, ranges) → `reference/renderer`, `reference/physics`, `reference/worlds-runtime`

**Fit.** `over`: about 6,850 words against L (5,000). The 116 index rows take about 1,900 words (their absences and
pages, counted from `book.md`'s table), the general techniques about 3,400 in seventeen groups of about 200 (one per
area, five for rendering), the introduction, the approaches table, the release lists and the mistakes about 700, the
exercises 250, and the fixed parts 600. At or over L's top, the page takes the next size, XL (8,000), which its kind
allows (S2, S5); phase B looks at the size again when the 0.8.0 notes add or remove rows.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:1` | not-done | link | Assets, core and platform: OBJ and FBX import (models are glTF only); stated on `make/assets`, `assets/models-gltf`. Evidence: `Strata/src/Strata/Asset/AssetImporters.cpp:159-177`; `Docs/Releases/0.7.0.md:414-415` |
| `new:2` | not-done | link | Assets, core and platform: BC6H compression (HDR textures are stored as RGBA16F); stated on `assets/texture-cooking`. Evidence: `Docs/Releases/0.7.0.md:403`; `Docs/Roadmap.md:1714` |
| `new:3` | not-done | link | Assets, core and platform: EXR import (the texture importer reads `.png`, `.jpg`, `.jpeg`, `.tga`, `.bmp`, `.psd`, `.gif` and `.hdr`); stated on `assets/texture-cooking`. Evidence: `Strata/src/Strata/Asset/TextureImporter.cpp:348`; `Docs/Roadmap.md:949` |
| `new:4` | not-done | link | Assets, core and platform: Mesh streaming, per level of detail included (only textures load in parts); stated on `draw/mip-streaming`. Evidence: `Strata/src/Strata/Renderer/RendererRegistration.cpp:93`, the only `RegisterPrefix`; `Docs/Roadmap.md:1691` |
| `new:5` | not-done | link | Assets, core and platform: Virtual texturing and sparse residency; stated on `draw/mip-streaming`. Evidence: no `sparseBinding` in `Strata/src` |
| `new:6` | not-done | link | Assets, core and platform: Shaders as assets and material graphs (shaders are compiled at build time and embedded); stated on `make/materials`, `light/materials`. Evidence: `Strata/src/Strata/Asset/AssetTypes.h:14-31`, no shader type; `strata_add_shaders` in `Strata/CMakeLists.txt` |
| `new:7` | not-done | link | Assets, core and platform: Mobile, console and web targets; stated on `core/platform`. Evidence: `Strata/src/Strata/Core/PlatformDetection.h:5-22`, an `#error` for every other target |
| `new:8` | not-done | link | Assets, core and platform: Work stealing, fibers and a frame task graph; stated on `core/jobs`. Evidence: `Docs/Roadmap.md:1704-1705`; `git grep -ni fiber 822a7a46 -- Strata/src` finds nothing |
| `new:148` | not-done | link | Assets, core and platform: A failure exit code after an exception leaves the frame loop (the program logs a critical line, ends in order and exits with 0 unless a layer set another code); stated on `core/frame-loop`. Evidence: `Strata/src/Strata/Core/Application.cpp:243-253`; `Strata/src/Strata/Engine/EntryPoint.h:35-36`; `git grep -n "Unhandled exception" 822a7a46 -- StrataTests` finds nothing |
| `new:9` | not-done | link | Assets, core and platform: Engine plugins loaded at run time (modules are chosen at compile time with `ST_WITH_*`; only script modules load at run time); stated on `core/layers-registries`. Evidence: the compile-time module table `Strata/src/Strata/Engine/BuiltinModules.cpp:62-76`; `git grep -lw DynamicLibrary 822a7a46 -- Strata/src` finds it used only for script modules (`Strata/src/Strata/Scripting/ScriptModule.cpp`, `ScriptEngine.cpp`, the module's file name in `Strata/src/Strata/Project/Project.cpp`) and for the Vulkan loader (`Strata/src/Platform/Vulkan/VulkanLoader.cpp`), besides its own files |
| `new:10` | not-done | link | Assets, core and platform: A build without scripting (physics, audio and animation can be left out); stated on `core/layers-registries`. Evidence: `Docs/Releases/0.7.0.md:404` |
| `new:149` | not-done | link | Assets, core and platform: A crash handler or crash dumps for the engine's own crashes (only guarded script calls are contained; a crash in engine code ends the process, and the log keeps every warning and error but loses the info and trace lines still queued); stated on `core/debugging`. Evidence: `git grep -n -e MiniDumpWriteDump -e SetUnhandledExceptionFilter -e set_terminate 822a7a46 -- Strata/src StrataEditor/src StrataRuntime/src` finds nothing; `Strata/src/Platform/Posix/PosixCrashGuard.cpp:92-109` (outside a guarded call a signal goes where it would have gone without the guard); `Strata/src/Strata/Core/BackgroundLogSink.h:29-32` |
| `new:150` | not-done | link | Assets, core and platform: Raising the streaming budgets of a game for a loading screen (no script function and no settings section sets the upload, finalization and staging budgets; the runtime's `--asset-budget-mb` sets only the GPU texture budget); stated on `assets/uploads`, `make/levels-saves`. Evidence: `Strata/src/Strata/Asset/AssetResidency.h:56-64` (raise all three for a loading screen); `git grep -ln -e UploadBytesPerFrame -e FinalizeMsPerFrame 822a7a46 -- Strata/src StrataEditor/src StrataRuntime/src StrataScriptCore` finds only the asset manager's files and the editor's (`StrataEditor/src/Editor/EditorStreamingCommands.cpp`, `StrataEditor/src/Panels/StreamingPanel.cpp`); `StrataRuntime/src/RuntimeApplication.cpp:56, 94-95` |
| `new:11` | not-done | link | Scenes, prefabs and editing: Nested prefabs and prefab variants (a prefab made from linked entities stores no inner links); stated on `make/prefabs`, `world/prefabs`. Evidence: `Strata/src/Strata/Scene/PrefabInstances.h:129-130` (`StripLinks`); `StrataEditor/src/Editor/EditorAssetCommands.cpp:1185, 1216` |
| `new:12` | not-done | link | Scenes, prefabs and editing: A prefab edit mode (a prefab changes through an instance and Apply); stated on `make/prefabs`. Evidence: `Docs/Releases/0.7.0.md:380` |
| `new:13` | not-done | link | Scenes, prefabs and editing: Drawn (interpolated) poses for world-space game UI, editor gizmos and picking, reflection probes, fog, post-processing, the sky and the sun; stated on `world/interpolation`. Evidence: `Docs/Roadmap.md:1698-1702` |
| `new:14` | not-done | link | Scenes, prefabs and editing: Editing several scenes at once (the editor edits one scene and a world's loaded cells; `scene.loadAdditive` works in play mode only); stated on `editor/play-mode`, `make/levels-saves`. Evidence: `StrataEditor/src/Editor/EditorSceneCommands.cpp:458-460` |
| `new:15` | not-done | link | Rendering: Particles, trails and decals; stated on `gpu/frame-tour`, `make/look`. Evidence: `git grep -niE "particle\|decal" 822a7a46 -- Strata/src Strata/shaders` finds nothing; `git grep -niwE "trails?"` there finds only the anti-aliasing tooltips of `Strata/src/Strata/Renderer/RendererComponents.cpp:508, 519, 523`; `Docs/Roadmap.md:1690` |
| `new:16` | not-done | link | Rendering: Terrain: a terrain system, sculpting and painting (the samples' terrains are meshes made by `Tools/GenerateIslandTerrain.py` and `Tools/GenerateShowcaseTerrain.py`); stated on `make/large-worlds`. Evidence: "terrain" only in comments of `Strata/src`; `Docs/Roadmap.md:1694` |
| `new:17` | not-done | link | Rendering: Water as an engine feature (water is a material with IOR 1.33); stated on `light/clearcoat-transmission`. Evidence: `Strata/src/Strata/Renderer/Material.h:59` |
| `new:18` | not-done | link | Rendering: MSAA and supersampling (a render scale above 1); stated on `image/spatial-aa`, `make/quality`. Evidence: `Strata/src/Strata/Renderer/SceneRenderer.cpp:2767` refuses targets with `sampleCount != 1`; `Docs/Roadmap.md:944, 1670, 1672`; `Docs/Releases/0.7.0.md:409, 411` |
| `new:19` | not-done | link | Rendering: Rendering below native resolution, dynamic resolution, temporal upscalers: left out by decision (the first design decision); stated on `image/quality-settings`. Evidence: `Docs/Roadmap.md:1642-1643` |
| `new:20` | not-done | link | Rendering: HDR display output (HDR10, scRGB): the swap chain is sRGB only; stated on `image/encoding`, `make/quality`. Evidence: `Strata/src/Platform/Vulkan/VulkanGraphicsDevice.cpp:1131-1136` |
| `new:21` | not-done | link | Rendering: Post-process volumes (the first active `PostProcessComponent` applies, with no shape and no blending); stated on `image/why-post`, `make/look`. Evidence: `Strata/src/Strata/Renderer/SceneRenderer.cpp:1447-1455` |
| `new:22` | not-done | link | Rendering: Non-photorealistic shading (toon, cel, ink outlines on objects): there is one physically based material model; the only outlines are the editor's selection outline and the outlines of text; stated on `light/materials`. Evidence: `git grep -niE "toon\|cel[ -]shad\|hatching" 822a7a46 -- Strata/src Strata/shaders` finds nothing; `Strata/shaders/Overlay/Outline.frag.slang:5` is the selection outline over the finished image; the other matches of "outline" in `Strata/shaders` are the selection outline's mask (`Scene/DepthPrepass.frag.slang`) and the outlines of glyphs (`GameUI/UIQuad.frag.slang`, `Include/SDFText.slang`, `Overlay/Text.frag.slang`) |
| `new:23` | not-done | link | Rendering: Hardware ray tracing; stated on `indirect/problem`. Evidence: `git grep -niE "accelerationstructure\|RayQuery<\|ray_query\|raytracing\|TraceRay\|VK_KHR_ray" 822a7a46 -- Strata/src Strata/shaders` finds nothing (the word `RayQuery` alone matches only physics, `struct RayQuery` of `Strata/src/Strata/Physics/PhysicsWorld.cpp` and its use in `CharacterControllers.cpp`) |
| `new:24` | not-done | link | Rendering: Mesh shaders and meshlets; stated on `draw/gpu-driven`. Evidence: no match in `Strata/src` or `Strata/shaders` |
| `new:25` | not-done | link | Rendering: A render graph or frame graph (`SceneRenderer::RenderFrame` orders the passes by hand); stated on `gpu/frame-tour`. Evidence: no `RenderGraph` or `FrameGraph` in `Strata/src`; `Strata/src/Strata/Renderer/SceneRenderer.cpp:2901` |
| `new:26` | not-done | link | Rendering: Portals; stated on `draw/occlusion`. Evidence: no match in `Strata/src` |
| `new:27` | not-done | link | Rendering: A second shadowed directional light; virtual shadow maps; stated on `light/sun-shadows-1`. Evidence: `Docs/Roadmap.md:949-950, 1670` |
| `new:28` | not-done | link | Rendering: Lightmaps and baked global illumination (reflection probes are the only bake); stated on `indirect/problem`. Evidence: no `Lightmap` in `Strata/src` or `Strata/shaders` |
| `new:29` | not-done | link | Rendering: Reflection probes captured while the game runs; stated on `indirect/probes`. Evidence: `Docs/Roadmap.md:943, 947`; `Docs/Releases/0.7.0.md:410-411` |
| `new:30` | not-done | link | Rendering: Reflections of and through transparent surfaces; glass behind glass; stated on `indirect/ssr`, `light/clearcoat-transmission`. Evidence: `Docs/Roadmap.md:939-942, 947-948` |
| `new:31` | not-done | link | Rendering: Subsurface scattering, sheen, anisotropy, iridescence, specular maps and thickness maps; stated on `light/materials`. Evidence: no `Subsurface` in `Strata/src` or `Strata/shaders`; `Docs/Roadmap.md:949` |
| `new:32` | not-done | link | Rendering: Order-independent transparency (glass shows only what was drawn before it); stated on `light/clearcoat-transmission`. Evidence: no match in `Strata/src` or `Strata/shaders`; `Docs/Roadmap.md:939-940` |
| `new:33` | not-done | link | Rendering: Volumetric fog, light shafts and fog volumes (height fog has no volume); stated on `light/fog`, `make/look`. Evidence: `Strata/src/Strata/Renderer/RendererComponents.h:126-129`; `Strata/shaders/Include/Scene.slang:13-14` (SRVs 34 and 36 reserved); `Docs/Roadmap.md:948` |
| `new:34` | not-done | link | Rendering: Billboards and impostors; stated on `draw/lod`. Evidence: no match in `Strata/src` or `Strata/shaders` |
| `new:35` | not-done | link | Rendering: Complex-script text shaping, and fonts with CFF outlines; stated on `gpu/text`. Evidence: `Strata/src/Strata/Renderer/FontValidation.cpp:131-132`; render-core inventory, concept 30 |
| `new:36` | not-done | link | Rendering: Compute skinning and dual-quaternion skinning (skinning runs per draw in the vertex shader); stated on `draw/skinned`, `animation/limits`. Evidence: `Docs/Roadmap.md:675`; no "dual quaternion" in `Strata/src` or `Strata/shaders` |
| `new:37` | not-done | link | Rendering: Debug drawing from scripts; stated on `gpu/debug-drawing`, `make/play-test-debug`. Evidence: no such function in `StrataScriptCore/Include/StrataScript/` |
| `new:151` | not-done | link | Rendering: A second view: split-screen, picture-in-picture, a camera that renders into a texture for a mirror or a minimap (a game is drawn from one camera, the first active entity whose Camera is Primary); stated on `gpu/frame-tour`, `make/characters-cameras`. Evidence: `Strata/src/Strata/Scene/Scene.cpp:867-879`; `Strata/src/Strata/Runtime/GameRenderer.cpp:114-126`; `git grep -niE "split-?screen\|render-?to-?texture\|picture-in-picture\|RenderTexture" 822a7a46 -- Strata/src StrataScriptCore Docs` finds nothing |
| `new:152` | not-done | link | Rendering: Clouds, stars and a moon (the atmosphere's haze is clear aerosol; the Overcast preset is a nearly uniform procedural sky); stated on `light/sky`, `make/lighting`. Evidence: `Strata/src/Strata/Renderer/SkyPresets.cpp:35-37`; `git grep -niwE "moon\|stars\|starfield\|clouds?" 822a7a46 -- Strata/src Strata/shaders` finds only that comment, a tooltip's full-moon illuminance (`Strata/src/Strata/Renderer/RendererComponents.cpp:289`) and two comments on cloud placeholder files (`Strata/src/Platform/Windows/WindowsFileSecurity.h:28`, `Strata/src/Strata/Core/Platform.h:104`) |
| `new:153` | not-done | link | Rendering: Light cookies, IES profiles, light linking and lighting channels (every light lights every surface in its range); stated on `light/lights`, `make/lamps`. Evidence: `git grep -niE "cookie\|light ?channel\|light ?layer\|light ?mask\|light ?link" 822a7a46 -- Strata/src Strata/shaders` finds only the DLL-directory cookie of `Strata/src/Platform/Windows/WindowsDynamicLibrary.cpp:21-36` and the socket notifier's cookie of `Strata/src/Platform/Windows/WindowsSocket.cpp`; `git grep -nw IES 822a7a46 -- Strata/src Strata/shaders` finds nothing |
| `new:154` | not-done | link | Rendering: Material parameters per entity, such as a tint or a hit flash, and material changes from scripts (a loaded material never changes; a game gives `MeshRenderer.Material` another asset); stated on `light/materials`, `make/materials`. Evidence: `Strata/src/Strata/Renderer/Material.h:87-90`; `git grep -ni material 822a7a46 -- StrataScriptCore/Include/StrataScript/ScriptABI.h` finds nothing; `Samples/Tetris/Scripts/TetrisBoard.cpp:365` |
| `new:155` | not-done | link | Rendering: A gizmo for reflection probes (the Scene view draws no box for a probe's Extents); stated on `make/reflections`, `indirect/probes`. Evidence: `Strata/src/Strata/Renderer/SceneGizmos.cpp:224-345` draws lights and cameras; `git grep -n "\.Gizmo(" 822a7a46 -- Strata/src StrataEditor/src` finds only the colliders and the character controller (`Strata/src/Strata/Physics/PhysicsComponents.cpp:143-184`) and the call that draws them (`Strata/src/Strata/Renderer/SceneGizmos.cpp:176`) |
| `new:156` | not-done | link | Rendering: Cube-map texture assets (skies and probe captures are equirectangular HDR textures, made into cubes at run time); stated on `indirect/ibl`, `make/reflections`. Evidence: `Strata/src/Strata/Asset/AssetTypes.h:14-31`, no cube texture type (its `.cube` files are color lookups); `Docs/Roadmap.md:947` |
| `new:38` | not-done | link | Physics: Joints, ragdolls and vehicles; stated on `physics/why`, `make/physics`. Evidence: no `b3Create*Joint` in `Strata/src`; `Docs/Roadmap.md:1716-1718` |
| `new:39` | not-done | link | Physics: Shape sweeps in the API (queries cast rays; a sweep is used only inside the character controller); stated on `physics/queries`. Evidence: `Strata/src/Strata/Physics/PhysicsWorld.cpp:5413, 5435` (`b3World_CastRay`); `Strata/src/Strata/Physics/CharacterControllers.cpp:373` (`b3World_CastMover`) |
| `new:40` | not-done | link | Physics: Height-field and cylinder colliders (Box, Sphere, Capsule and Mesh only; the Hierarchy's Cylinder, Cone and Torus get a convex mesh collider of their own mesh, a hull of at most 64 vertices, and the torus's hull fills its hole); stated on `physics/bodies-colliders`, `make/physics`. Evidence: `Strata/src/Strata/Physics/PhysicsComponents.h:44-68`; `StrataEditor/src/Panels/SceneHierarchyPanel.cpp:65-69, 83-88`; `Strata/src/Strata/Physics/PhysicsMeshShapes.h:48-49, 57` |
| `new:41` | not-done | link | Physics: Cloth, soft bodies, destruction, fluids and buoyancy; stated on `physics/why`, `make/physics`. Evidence: `git grep -niE "cloth\|soft ?bod\|fluid\|buoyan\|fractur\|destructible" 822a7a46 -- Strata/src` finds nothing (the word "destruction" matches only the destruction of entities and objects) |
| `new:42` | not-done | link | Physics: Bodies farther than 1e5 m from the origin (they wait); stated on `physics/scale-streaming`. Evidence: `Strata/src/Strata/Physics/PhysicsWorld.cpp:73` (`c_MaxBodyCoordinate`) |
| `new:43` | not-done | link | Physics: Triggers that see triangle-mesh colliders; stated on `physics/contacts-triggers`. Evidence: `Docs/Releases/0.7.0.md:399`; `Docs/Roadmap.md:1719-1720` |
| `new:44` | not-done | link | Physics: Bodies that move from one world cell to another (a moving body unloads with the cell it loaded with); stated on `worlds/physics-scripts`, `make/large-worlds`. Evidence: `Docs/Releases/0.7.0.md:387` |
| `new:157` | not-done | link | Physics: Stay events, and the impulse or impact speed of a contact (contacts begin and end; a script that needs a hit's strength reads the bodies' velocities); stated on `physics/contacts-triggers`, `make/physics`, `make/sound`. Evidence: `Strata/src/Strata/Scene/SceneServices.h:41-45`; `StrataScriptCore/Include/StrataScript/ScriptABI.h:181-186`; `git grep -n enableHitEvents 822a7a46 -- Strata/src` finds nothing; `Samples/PhysicsPlayground/Scripts/Impact.cpp:53-55` |
| `new:158` | not-done | link | Physics: Rolling resistance and tangent velocity (conveyor belts) of box3d's surface material (a rolling ball slows only through its damping); stated on `physics/bodies-colliders`, `make/physics`. Evidence: `git grep -n -e rollingResistance -e tangentVelocity 822a7a46 -- Strata/src` finds nothing; `Strata/vendor/box3d/include/box3d/types.h:417-431` |
| `new:45` | not-done | link | Animation: Blend trees, animation layers, IK, morph targets, clip compression; stated on `animation/limits`, `make/animation`. Evidence: `git grep -nilE "blend ?tree\|inverse kinematics\|morph\|compress" 822a7a46 -- Strata/src/Strata/Animation` finds nothing; `Strata/src/Strata/Asset/GltfImporter.cpp:1031` (weight channels skipped); `Docs/Roadmap.md:1649-1652` |
| `new:46` | not-done | link | Animation: Additive clips, sync markers, float curves, inertialization, motion matching; stated on `animation/limits`. Evidence: `git grep -nilE "additive\|sync ?marker\|float curve\|inertiali\|motion ?match" 822a7a46 -- Strata/src/Strata/Animation` finds nothing; `Docs/Roadmap.md:1647-1651` |
| `new:47` | not-done | link | Animation: Retargeting beyond matching joint names (clips bind to skeletons by name); stated on `animation/limits`. Evidence: `Strata/src/Strata/Animation/AnimationClip.h:38` |
| `new:48` | not-done | link | Animation: A skeleton overlay in the viewport; stated on `animation/limits`. Evidence: `git grep -nilE "joint" 822a7a46 -- StrataEditor/src Strata/src/Strata/Renderer Strata/shaders` finds the Asset tab's joint and channel views, the animation commands, the editor's bounds code, the `AttachToJoint` entity icon and the skinning code, and other words (`JoinTypeNames` in `StrataEditor/src/Editor/EditorUICommands.cpp`, "disjoint" in `Strata/src/Strata/Renderer/GlobalIlluminationLayout.h` and `.cpp`); nothing draws joints in a view |
| `new:49` | not-done | link | Audio: Buses, effects, reverb and HRTF (a voice sets only its own output volume); stated on `audio/engine`, `make/sound`. Evidence: no `ma_sound_group`, reverb, HRTF or filter node in `Strata/src/Strata/Audio`; `Strata/src/Strata/Audio/AudioVoice.cpp:308` |
| `new:50` | not-done | link | Audio: Occlusion and reverb zones; stated on `audio/spatial`, `make/sound`. Evidence: no match in `Strata/src/Strata/Audio` |
| `new:51` | not-done | link | Audio: Virtual voices and voice priorities; stated on `audio/clips-voices-sources`, `make/sound`. Evidence: no match in `Strata/src/Strata/Audio` |
| `new:52` | not-done | link | Audio: Streaming from disk or packs (a streamed clip decodes encoded bytes held in memory); stated on `audio/clips-voices-sources`, `make/sound`. Evidence: `Strata/src/Strata/Audio/AudioClip.h:45-52`; `Docs/Roadmap.md:1712` |
| `new:53` | not-done | link | Audio: A choice of attenuation model per component (components always use Inverse); stated on `audio/spatial`. Evidence: `Strata/src/Strata/Audio/AudioComponents.h:11-22`, no model field |
| `new:54` | not-done | link | Audio: Listeners per world; stated on `audio/scene-system`, `make/sound`. Evidence: `Docs/Roadmap.md:1707` |
| `new:55` | not-done | link | Audio: Music systems and ducking; stated on `make/sound`. Evidence: no match in `Strata/src/Strata/Audio` |
| `new:56` | not-done | link | Input: Touch input; stated on `input/how-input-works`, `make/input`. Evidence: no touch code in `Strata/src/Strata/Input` or `Strata/src/Platform/GLFW` |
| `new:57` | not-done | link | Input: Input-method composition in game UI: committed text arrives, but the text being composed and the candidate window are not shown. The editor's ImGui text fields take composed text and, on Windows, place the candidate list; stated on `ui/text`, `editor-ui/imgui-backends`. Evidence: `Strata/src/Strata/Input/Input.h:148`; GLFW 3.4 has no preedit API (`Strata/vendor/glfw/include/GLFW/glfw3.h`); `Strata/src/Strata/ImGui/ImGuiPlatform.h:25-26` |
| `new:58` | not-done | link | Input: Action modifiers, chords, processors and interactions; mouse motion and scroll as action sources (they stay on the raw API); stated on `input/actions`, `make/input`. Evidence: `Docs/DeveloperGuide.md:1464-1465`; `Docs/Releases/0.7.0.md:361, 412`; `Strata/src/Strata/Input/InputActionSet.cpp:102` refuses every binding but `Key/`, `Mouse/<button>`, `Gamepad/`, `1D:` and `2D:` |
| `new:59` | not-done | link | Input: Force feedback; stated on `input/gamepads`, `make/input`. Evidence: no rumble, vibration or haptic code in `Strata/src` or `StrataScriptCore` |
| `new:60` | not-done | link | Input: Devices assigned to players for local multiplayer (gamepad bindings read every gamepad); stated on `input/gamepads`, `make/input`. Evidence: `Docs/DeveloperGuide.md:1460`; `Docs/Releases/0.7.0.md:412`; `Docs/Roadmap.md:1707` |
| `new:159` | not-done | link | Input: Key names that follow the player's keyboard layout (a game shows a key's name by its US position; only the editor's shortcuts follow the layout); stated on `input/rebinding`, `make/menus`. Evidence: `Docs/Releases/0.7.0.md:361-362`; `git grep -n GetLayoutKey 822a7a46 -- Strata/src StrataScriptCore` finds only the window's own code and the ImGui platform's (`Strata/src/Strata/ImGui/ImGuiPlatform.cpp:180` and a comment of its header) |
| `new:160` | not-done | link | Input: Controllers missing from GLFW's gamepad database, more than four gamepads, and gamepad mappings that a game adds (an unmapped controller reads as not connected and keeps its slot); stated on `input/gamepads`, `make/input`. Evidence: `Strata/src/Platform/GLFW/GLFWWindow.cpp:416-442`; `Strata/src/Strata/Input/GamepadCodes.h:42` (`c_MaxGamepads = 4`); `git grep -n glfwUpdateGamepadMappings 822a7a46 -- Strata/src StrataEditor/src StrataRuntime/src` finds nothing |
| `new:61` | not-done | link | Scripting: Visual scripting (game logic is C++ script classes); stated on `start/welcome`, `scripting/why-scripts`. Evidence: no node or graph scripting in `Strata/src` or `StrataEditor/src`; `AGENTS.md`, "Scripting" |
| `new:62` | not-done | link | Scripting: Script languages other than C++; stated on `scripting/why-scripts`. Evidence: no `lua_`, `mono_` or CoreCLR code in the engine |
| `new:63` | not-done | link | Scripting: Calls into scripts from other threads; stated on `scripting/abi-sdk`. Evidence: `StrataScriptCore/Include/StrataScript/ScriptABI.h:25-26` |
| `new:64` | not-done | link | Scripting: Script modules linked statically; stated on `scripting/loading`. Evidence: `Docs/Roadmap.md:1709` |
| `new:161` | not-done | link | Scripting: Script field types beyond the ten (no `std::vector`, array, enum, `double`, `int64_t` or struct: such a field fails to compile with "Unsupported script field type"); stated on `make/script-fields`. Evidence: `StrataScriptCore/Include/StrataScript/Script.h:133-137, 785-786` |
| `new:162` | not-done | link | Scripting: Callbacks when an entity is activated or deactivated (no `OnEnable` or `OnDisable`; `OnCreate` is the only start); stated on `make/script-loop`. Evidence: `StrataScriptCore/Include/StrataScript/Script.h:83-97`, the 15 callbacks |
| `new:163` | not-done | link | Scripting: Coroutines (nothing waits inside a callback; timers and state machines do that work); stated on `make/timers-events`. Evidence: `git grep -n -i -e coroutine -e co_await 822a7a46 -- Strata/src StrataScriptCore` finds nothing |
| `new:164` | not-done | link | Scripting: Debug information in script modules that a Release or Dist editor builds with GCC or Clang: only MSVC builds get it in every configuration, and the editor builds scripts in its own configuration, whose Release and Dist flags hold no `-g` (read from the build files, not run); stated on `basics/debugging`, `make/play-test-debug`. Evidence: `StrataScriptCore/CMake/StrataScriptModule.cmake:110-133`; `StrataScriptCore/CMake/StrataScriptCoreConfig.cmake:37-52`; `StrataEditor/src/Editor/ScriptBuild.cpp:402` |
| `new:165` | not-done | link | Scripting: Reading the game's title or version from a script; stated on `worlds/game-identity`, `make/export`. Evidence: `Docs/Releases/0.7.0.md:363`; `git grep -niE "title\|gameinfo" 822a7a46 -- StrataScriptCore` finds only the graphics options' `Title` (`StrataScriptCore/Include/StrataScript/Graphics.h:46, 125`; `ScriptABI.h:289, 299`) |
| `new:65` | not-done | link | Game UI: Scroll views, drop-downs, rich text and multi-line input fields (a mask clips a scrolling list; input fields are one line); stated on `ui/what-game-ui-does`, `make/menus`. Evidence: `Strata/src/Strata/GameUI/GameUIComponents.cpp:211-397`; `Strata/src/Strata/GameUI/GameUIComponents.h:255-260, 272-273` |
| `new:66` | not-done | link | Game UI: Localization and right-to-left text; stated on `ui/text`, `make/menus`. Evidence: `Docs/Releases/0.7.0.md:415`; `Docs/Roadmap.md:1713`; no localization code in `Strata/src` |
| `new:67` | not-done | link | Game UI: Lit world-space UI; game clicks on world-space canvases that respect geometry in front; stated on `ui/drawing`, `ui/input`. Evidence: `Docs/Releases/0.7.0.md:389-390` |
| `new:68` | not-done | link | Editor, export and automation: Panels torn out into windows of their own (one main viewport); stated on `editor-ui/shell`. Evidence: `Strata/src/Strata/ImGui/ImGuiPlatform.h:21`; `Docs/Roadmap.md:1715` |
| `new:69` | not-done | link | Editor, export and automation: Editor extensions written by a game project (only the editor registers panels); stated on `editor-ui/shell`. Evidence: `StrataEditor/src/EditorLayer.cpp:350` |
| `new:70` | not-done | link | Editor, export and automation: A place in the editor's UI to type and run any command (the Activity panel re-runs only commands the journal recorded); stated on `make/commands`. Evidence: `EditorLayer::DrawMenuBar`, `StrataEditor/src/EditorLayer.cpp:1449-1627`; `StrataEditor/src/Panels/ActivityPanel.cpp:372-397` |
| `new:71` | not-done | link | Editor, export and automation: Creating an animation controller from the UI (only the command `animation.createController`); stated on `make/animation`. Evidence: `StrataEditor/src/Editor/EditorAnimationCommands.cpp:153`; `StrataEditor/src/Panels/ContentBrowserPanel.cpp:566-580` |
| `new:72` | not-done | link | Editor, export and automation: Setting a player's graphics options by command (only `graphics.resetPlayerOptions`); stated on `make/quality`. Evidence: `StrataEditor/src/Editor/EditorGraphicsCommands.cpp:16` |
| `new:73` | not-done | link | Editor, export and automation: Automating an exported game (command scripts, simulated input and expectations run in the editor only); stated on `make/automated-playtests`, `worlds/runtime`. Evidence: `Docs/Roadmap.md:1697`; `Docs/Releases/0.7.0.md:414` |
| `new:74` | not-done | link | Editor, export and automation: Exports for another platform, macOS app bundles, signed exports, crash reports in shipped games (the export copies the runtime next to the editor); stated on `make/export`, `worlds/export`. Evidence: `Docs/Releases/0.7.0.md:411-412`; `StrataEditor/src/Editor/GameExport.h:30`; `Docs/Roadmap.md:1684-1685` |
| `new:75` | not-done | link | Editor, export and automation: In-game consoles and console variables; stated on `make/play-test-debug`. Evidence: no match in `Strata/src`, `StrataRuntime/src` or `StrataScriptCore` |
| `new:166` | not-done | link | Editor, export and automation: MCP resources, prompts and logging, a transport other than the standard streams, and cancellation (the MCP server offers tools only, and nothing cancels a command once it is sent: the editor finishes it, as it does after the CLI's exit code 4); stated on `automation/mcp`, `make/with-an-agent`. Evidence: `StrataCLI/src/CLI/McpServer.cpp:367-372` (every notification but `notifications/initialized` is dropped), `:379-397`, `:420` (the `tools` capability alone); `StrataCLI/src/CLI/CliApplication.cpp:358-359` (standard input and output); `StrataCLI/src/CLI/CliApplication.h:24` (exit code 4: the command may still be running in the editor); `git grep -n -i "notifications/cancel" 822a7a46 -- StrataCLI Strata/src/Strata/Network` finds nothing |
| `new:167` | not-done | link | Editor, export and automation: Rebinding the editor's shortcuts (the chords are written in the code); stated on `editor-ui/game-view`, `make/editor-tour`. Evidence: `StrataEditor/src/EditorLayer.cpp:951-985`; `StrataEditor/src/Editor/EditorPreferences.cpp:69-74` (three preference sections: the external editor, the interface and the frame rate); `Docs/Roadmap.md:993` |
| `new:168` | not-done | link | Editor, export and automation: Editor themes other than the one it has; stated on `editor-ui/design-system`. Evidence: `StrataEditor/src/Editor/EditorPreferences.cpp:69-74`; `Docs/Roadmap.md:993` |
| `new:169` | not-done | link | Editor, export and automation: A tool that writes patch packs (the export writes none; a patch is a pack written from code and named in the manifest's `PatchPacks` by hand); stated on `assets/packs-export`, `make/export`. Evidence: `git grep -n PatchPacks 822a7a46 -- StrataEditor StrataCLI Tools` finds nothing; `Strata/src/Strata/Project/GameManifest.h:26, 53` |
| `new:76` | not-done | link | Editor, export and automation: Worlds beyond 20 km from the origin, HLOD (distant cells are not drawn), origin rebasing; stated on `worlds/why-streaming`, `make/large-worlds`. Evidence: `Docs/Releases/0.7.0.md:386, 414`; `Docs/Roadmap.md:1693, 1706` |
| `new:77` | not-done | link | Gameplay: Gameplay networking (network code exists for editor automation only, in the Tooling layer `Network`, which games never link); stated on `appendix/networking`, `automation/json-rpc`. Evidence: `StrataTests/Architecture/Layers.json:99-102` |
| `new:78` | not-done | link | Gameplay: Game AI: steering, pathfinding, navigation meshes, behaviour trees (left to scripts); stated on `appendix/game-ai`, `make/patterns`. Evidence: no match in `Strata/src` or `StrataScriptCore` |
| `new:170` | not-done | link | Gameplay: A sequencer or timeline for cutscenes (camera moves and cuts are scripted, as the Showcase's camera tour is); stated on `make/characters-cameras`. Evidence: `Samples/Showcase/Scripts/TourPath.h:3-6`; `git grep -niE "sequencer\|cutscene\|cinematic" 822a7a46 -- Strata/src StrataEditor/src StrataScriptCore Docs/Roadmap.md` finds only the editor's input sequences (`IsInputSequenceRunning`, `DescribeSequenceResult`) |
| `new:171` | not-done | link | Building, testing and the GPU: Asynchronous compute and wave (subgroup) operations (compute runs on the graphics queue, although the device fetches a compute queue); stated on `gpu/compute`. Evidence: `git grep -n "CommandQueue::Compute" 822a7a46 -- Strata/src` and `git grep -nE "Wave[A-Z][a-z]*\(" 822a7a46 -- Strata/shaders` find nothing; the compute queue is fetched at `Strata/src/Platform/Vulkan/VulkanGraphicsDevice.cpp:939-940` |
| `new:172` | not-done | link | Building, testing and the GPU: Debug information in shaders (slangc runs without `-g`, so a frame capture shows shaders without their source); stated on `gpu/debugging`. Evidence: `CMake/StrataShaders.cmake:77-79`; `Docs/Roadmap.md:1090` |
| `new:173` | not-done | link | Building, testing and the GPU: A choice of GPU (no program sets the device's adapter index, so the device's score picks: a discrete GPU first, then the most memory; the log names each GPU it skips, with the reason); stated on `gpu/vulkan-nvrhi`. Evidence: `Strata/src/Strata/Renderer/GraphicsDevice.h:29`; `Strata/src/Platform/Vulkan/VulkanGraphicsDevice.cpp:632, 637-640, 744-750`; `git grep -n AdapterIndex 822a7a46 -- Strata/src StrataEditor/src StrataRuntime/src StrataTests/src` finds only these two files |
| `new:174` | not-done | link | Building, testing and the GPU: Command lists recorded on several threads (the main thread records and submits every command list; the renderer's jobs do CPU work only); stated on `gpu/vulkan-nvrhi`. Evidence: `Docs/Architecture.md:1383-1384`; `git grep -n -e ParallelFor -e "JobSystem::Submit" 822a7a46 -- Strata/src/Strata/Renderer` finds only staging copies (`GPUUploadQueue.cpp:531`), poses (`RenderScene.cpp:1409`), extraction (`SceneRendererExtraction.cpp:117`) and caster queries (`SceneRendererExtraction.cpp:538`, `SceneRendererLocalShadows.cpp:578`) |
| `new:175` | not-done | link | Building, testing and the GPU: A check at startup for the processor's AVX2 (the release builds compile every engine object for AVX2, so an older processor stops at an illegal instruction without a message); stated on `engineering/flags-portability`, `make/export`. Evidence: `CMake/StrataCompilerOptions.cmake:30`, `:50-51`, `:61-62`; the only processor check in `Strata/src` is `Strata/src/Strata/Core/Hash.cpp:109-119` (SSE 4.2, for CRC32) |
| `new:176` | not-done | link | Building, testing and the GPU: Unity builds (every source compiles as its own translation unit); stated on `engineering/flags-portability`. Evidence: `git grep -niE "UNITY_BUILD" 822a7a46 -- CMakeLists.txt CMake Strata/CMakeLists.txt StrataTests/CMakeLists.txt StrataEditor/CMakeLists.txt` finds nothing |
| `new:177` | not-done | link | Building, testing and the GPU: A package manager such as vcpkg or Conan (dependencies are pinned submodules wrapped by one CMake file); stated on `engineering/third-party`. Evidence: `git ls-tree -r --name-only 822a7a46 \| grep -iE "vcpkg\|conanfile"` finds nothing; `Strata/vendor/CMakeLists.txt:3-7` |
| `new:178` | not-done | link | Building, testing and the GPU: Measured line coverage (the feature test's coverage by construction stands in its place); stated on `engineering/testing`. Evidence: `git grep -niE "\-\-coverage\|llvm-cov\|gcov\|OpenCppCoverage\|fprofile-instr" 822a7a46 -- CMakeLists.txt CMake StrataTests/CMakeLists.txt .github Tools` finds nothing |
| `new:179` | not-done | link | Building, testing and the GPU: A coverage-guided fuzzer such as libFuzzer or AFL (the sweeps test fixed, seeded offsets); stated on `engineering/test-program`. Evidence: `git grep -niE "libfuzzer\|LLVMFuzzerTestOneInput\|fsanitize=fuzzer" 822a7a46 -- Strata/src StrataTests CMake CMakeLists.txt .github` finds nothing |
| `new:180` | not-done | link | Building, testing and the GPU: Sanitizer builds (AddressSanitizer, UndefinedBehaviorSanitizer); stated on `engineering/ci`. Evidence: `git grep -niE "fsanitize" 822a7a46 -- CMakeLists.txt CMake StrataTests/CMakeLists.txt .github CMakePresets.json` finds nothing; `.github/scripts/annotate_failures.py:40` only recognizes the word "Sanitizer" in a log |
| `new:181` | not-done | link | Building, testing and the GPU: A format check (neither CI nor a test runs clang-format, so `.clang-format` and `.editorconfig` act only in editors that read them); stated on `engineering/ci`. Evidence: `git grep -n -i "clang-format" 822a7a46 -- . ":!Strata/vendor" ":!Docs/Plans"` finds only `AGENTS.md:144` |
| `new:182` | not-done | link | Building, testing and the GPU: Signed or notarized release archives, and installers (CPack writes a ZIP on Windows and a TGZ elsewhere); stated on `engineering/releasing`. Evidence: `git grep -niE "signtool\|codesign\|notari" 822a7a46 -- .github CMake CMakeLists.txt` finds nothing; `CMake/StrataPackaging.cmake:95-99` |
| `new:79` | not-done | link | W8 pages: Disk-shaped area lights (0.8.0 brings rectangle lights; disk lights only if their stage lands); stated on `light/area-lights`. Evidence: no `AreaLight`, rectangle-light or LTC code in `Strata/src` or `Strata/shaders` |
| `new:80` | not-done | link | W8 pages: Diffuse light and soft shadows from the size of point and spot lights (a light's size widens only its highlight); stated on `light/area-lights`, `light/local-shadows`. Evidence: `Docs/Roadmap.md:946-947, 1660`; `AGENTS.md:407-408`; `Docs/Releases/0.7.0.md:409-410` |
| `new:81` | not-done | link | W8 pages: Global illumination from local lights and from moving or skinned objects; specular light from global illumination (the field changes only the diffuse indirect light), the open share in specular occlusion, an Ultra level, textured albedo per voxel, hardware ray queries for global illumination, nested probe-field levels, and denser probes near surfaces; stated on `indirect/gi-limits`, `make/gi`. Evidence: `Docs/Plans/Wave8/specs/radiance-cascades-world.md:896-917` ("Below the cut", items 1 to 6 and 8; item 7, probe relocation, is at the pin: `Docs/DeveloperGuide.md:5090`); `Docs/DeveloperGuide.md:4960-4961, 5164, 5271`; render-indirect inventory §1.8 |
| `new:82` | not-done | home | The release's own list of what it does not hold ("Not in this release"), mapped to the index rows: 0.8.0's at the tag, 0.7.0's at the pin (the wave 8 draft has no such section yet). Evidence: `Docs/Releases/0.7.0.md:406-416`; `git ls-tree --name-only 822a7a46 Docs/Releases/` lists `0.3.0.md` to `0.7.0.md` and `PackageReadme.md`, no `0.8.0.md`; the draft's headings are `Docs/Plans/Wave8/ReleaseNotes.md:8, 308, 325, 369` |
| `new:83` | not-done | home | The release's "Known issues", read for absences: a line that is an absence maps to a row, a limit of a feature goes to its page, and a line no longer true at the pin is dropped. Evidence: `Docs/Releases/0.7.0.md:308-404` and the wave 8 draft's `Docs/Plans/Wave8/ReleaseNotes.md:369-504` (its line on drawn poses, `:461-463`, matches the index row of `world/interpolation`); 0.7.0's line "The fixed timestep and gravity remain settings of each scene" (`:364`) is half out of date at the pin, where the project's `Scene.Timing` section has a `FixedRate` that overrides every scene's step (`Strata/src/Strata/Scene/SceneRegistration.cpp:22`, `Strata/src/Strata/Scene/ProjectSceneTiming.h:11, 36`); its line on endless loops (`:401-402`) still holds, because the script watchdog only reports a long call (`Strata/src/Strata/Scripting/ScriptWatchdog.h:16-18`) |
| `animation:223` | feature | link | The animation inventory's list of what is not in Strata yet, homed on `animation/limits` |
| `animation:52` | feature | link | No clip compression, stated on `animation/limits` |
| `editor-core:184` | feature | link | No prefab edit mode, stated on `make/prefabs` |
| `physics:116` | feature | link | No shape casts in the public API, stated on `physics/queries` |
| `render-direct:217` | feature | link | Area lights at the pin, a W8 entry stated on `light/area-lights` |
| `render-image:260` | feature | link | No render scale, the first design decision, stated on `image/quality-settings` |
| `gamedev:518` | rule | link | "No render scale, ever" in the game maker's words, on `make/quality` |
| `worlds-runtime:272` | concept | link | No HLOD yet, stated on `worlds/why-streaming` |
| `worlds-runtime:546-547` | term | link | Origin rebasing and HLOD, defined by their owners and named in the index |
| `audio-input:621` | term | link | Bus or group, named in the audio rows |
| `audio-input:642` | term | link | HRTF, named in the audio rows |
| `new:188` | hands-on | home | The page's exercises (D27). Done, as a command script with `expect` steps: `component.list` and `editor.commands` show that no component or command is a particle system, a navigation mesh or a network session, as the index says; then two rows' searches run in the engine's clone at the pin (particles and trails; toon shading), and the reader names each match that is not the absent feature (the anti-aliasing tooltips' "trails", the selection outline). Design: a game needs particles; the reader weighs the four approaches to scope (build it in, middleware beside the engine, a plugin loaded at run time, game code) under Strata's choice (modules chosen at compile time, only script modules loaded at run time) and says what each costs (about 250 words). Evidence: `StrataEditor/src/Editor/Commands/EntityCommands.cpp:613` (`component.list`); `StrataEditor/src/Editor/EditorCommands.cpp:66` (`editor.commands`); `StrataEditor/src/Editor/EditorCommandRunner.cpp:444` (a step's `expect`); `Strata/src/Strata/Renderer/RendererComponents.cpp:508, 519, 523`; `Strata/shaders/Overlay/Outline.frag.slang:5`; `Strata/src/Strata/Engine/BuiltinModules.cpp:62-76` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| What an engine is made of: programs, libraries, modules and layers | `core/map` | helps |
| Layers, registries and the composition root; modules chosen at compile time | `core/layers-registries` | helps |
| Game code as script modules outside the engine | `scripting/why-scripts` | helps |
| The scene renderer's frame, pass by pass | `gpu/frame-tour` | helps |
| What a release holds and how its notes are made | `engineering/releasing` | helps |
| Reading a search command such as `git grep` (the evidence of an entry) | `basics/git` | helps |
| Command scripts and their `expect` steps (the exercise) | `editor/command-scripts` | helps |

## `appendix/networking` — Networking for games, in general

**Covers.** The page runs on one small example: two players on two machines push one ball across a field, on a
simulation of 60 steps a second. The problem as the reader meets it: the second player's push arrives tens to
hundreds of milliseconds late, some packets arrive twice, out of order or never, and both screens must still show one
game. The naive answer is to send every object's position over TCP every frame; it breaks on four things in turn: input
feels late, one lost packet holds back every later one (head-of-line blocking), the bytes grow with the objects and the
frame rate, and a player's machine can send any position it likes. The idea: one simulation has the authority, the
others predict and correct, and time, more than bytes, is the hard part.

Transport first: datagrams (UDP) against streams (TCP), a reliability layer of sequence numbers and acknowledgements
for the few messages that need it, and why games build their own; the stream, the framing and the bounds on a peer
come from `automation/json-rpc` and are not taught again. The approaches, each introduced by the flaw of the one
before: deterministic lockstep (send only inputs; every machine must compute the same steps bit for bit; strategy
games), rollback (predict the remote inputs, and rewind and replay the steps when the real ones arrive; fighting
games), client-server with snapshots and entity interpolation (remote objects drawn one or two snapshots in the past),
client-side prediction with server reconciliation (the local player runs ahead and is corrected), and lag compensation
(the server rewinds its hit tests to what the shooter saw). A table compares them: bandwidth, the latency they hide,
resistance to cheating, how hard they are, and who uses them, with sources (Gaffer on Games [S17] and Gambetta [S24]
of `research/curricula.md`). Then bandwidth: quantization of floats, deltas against the last snapshot the other side
acknowledged, and interest management. Then topologies: dedicated server, listen server, peer to peer, relays and NAT
traversal. Security: never trust the client, and bound everything a peer controls (the editor's server is the book's
worked case).

Strata's choice: no gameplay networking. Its sockets, framing and JSON-RPC are the Tooling layer `Network`, which
serves the editor's automation only and which games never link; the SDK and the runtime hold no socket. What a game or
an engine change would build on is already there: game time in fixed steps (the tick), parallel physics that gives the
same result with any number of threads (bit-identical results across machines are box3d's claim for its own scenario,
which Strata checks with a golden hash, not a promise of the engine), inputs as data (input actions; simulated input
queued per fixed step), drawn transforms between the last two fixed poses (the same idea as entity interpolation, one
step behind), and scene documents. What it would have to add: a transport, snapshots and their deltas, a way to rewind
state for rollback or lag compensation, and devices assigned to players. Common mistakes: TCP for fast-changing state;
sending every frame instead of every tick; trusting results that a client computed; counting frames instead of ticks;
assuming floating-point results agree across compilers and processors. The exercises: a sketch that draws the ball
one snapshot interval behind, with one snapshot lost, and prints the error; and a design exercise that names the model
for three games and what Strata would have to add for each. At the end the reader can name the model a given game
needs, say what it costs, and say what Strata would have to gain to run it.

**Leaves out.**

- Sockets, ports, non-blocking reads, framing and JSON-RPC as Strata implements them → `automation/json-rpc`
- The editor's RPC server: its network thread, limits and backpressure → `automation/rpc-server`
- The handshake, the session token and HMAC → `automation/security`
- The fixed step, the accumulator and time dilation → `core/time`
- Drawing between two fixed steps → `world/interpolation`
- Floating-point determinism across compilers (FMA contraction) → `engineering/flags-portability`
- Devices per player for local multiplayer (an absence) → `input/gamepads`

**Fit.** `fits`: about 5,550 words against L (5,000). Five approaches with their table take 1,700 words, Strata's
choice with what a game would build on 750, the problem and the naive answer 600, bandwidth and topologies 600,
transport 500, mistakes 300, security 250, the two exercises 250, and the fixed parts 600; three timelines carry the
approaches.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:77` | not-done | home | Gameplay networking: network code exists for editor automation only, in the Tooling layer `Network`, which games never link; how engines do it is the page itself. Evidence: `StrataTests/Architecture/Layers.json:99-102` (the layer `Network`, `"Tooling": true`, `Strata/Network/**` and the OS socket files); `git grep -nE "Socket\|Network" 822a7a46 -- StrataScriptCore StrataRuntime` finds nothing |
| `automation:47` | feature | use | The Network layer's place: Tooling, may include only Core, links `ws2_32` on Windows |
| `worlds-runtime:140` | feature | use | Games link no tooling: the runtime links no editor, asset pipeline or network layer |
| `automation:284` | concept | use | Processes, sockets and ports; TCP on loopback, the starting point for datagrams against streams |
| `automation:298` | concept | use | A stream has no message boundaries: framing, against the packets of a game protocol |
| `automation:310` | concept | link | Remote procedure calls and JSON-RPC 2.0, the opposite of state replication |
| `automation:350` | concept | use | Limits and backpressure: what one slow or hostile peer may cost |
| `automation:363` | concept | use | The editor's threat model, as the worked case of "never trust the peer"; a game adds cheating players |
| `automation:615` | rule | use | The network thread never touches engine state: a game's network thread would hand messages to the main thread the same way |
| `automation:622` | rule | use | Bound everything a peer controls |
| `automation:481` | code | link | The network thread's iteration, read on `automation/rpc-server` |
| `foundation:228` | concept | use | The fixed step and its accumulator, as the tick a networked simulation counts |
| `physics:279` | concept | use | Determinism: the same results with any number of threads; what box3d's cross-platform claim covers, which lockstep would rest on |
| `physics:149` | feature | link | The determinism tests of physics |
| `build-test:301` | concept | use | Instruction sets and floating-point determinism across machines |
| `scene-ecs:357` | concept | use | Drawing between two fixed poses, the same idea as entity interpolation |
| `audio-input:357` | concept | use | Simulated input queued per fixed step: inputs as data, the basis of lockstep and replays |
| `scripting:343` | concept | use | Seeded random numbers in game code, which lockstep needs on every machine |
| `new:60` | not-done | link | Devices assigned to players for local multiplayer, stated on `input/gamepads` and `make/input` |
| `new:84` | figure | home | A timeline of deterministic lockstep beside rollback: inputs sent, steps waited for, steps rewound and replayed. General knowledge. |
| `new:85` | figure | home | A timeline of client-server with client-side prediction and server reconciliation, the corrections drawn as jumps. General knowledge. |
| `new:86` | figure | home | Snapshot interpolation: the remote ball drawn between the two newest snapshots, one interval behind. General knowledge. |
| `new:87` | figure | home | Strata's layers as a diagram, `Network` among the Tooling layers beside the stack, games linking none of them. Evidence: `StrataTests/Architecture/Layers.json:99-102` |
| `new:88` | term | home | UDP and datagram. General knowledge. |
| `new:89` | term | home | Latency and round-trip time. General knowledge. |
| `new:90` | term | home | Packet loss and jitter. General knowledge. |
| `new:91` | term | home | Tick and tick rate. General knowledge. |
| `new:92` | term | home | Authority; authoritative server. General knowledge. |
| `new:93` | term | home | Deterministic lockstep. General knowledge. |
| `new:94` | term | home | Rollback (rollback netcode). General knowledge. |
| `new:95` | term | home | Snapshot (networking): the state a server sends each tick, a third meaning beside the two of `book.md`'s rule 6. General knowledge. |
| `new:96` | term | home | Entity interpolation. General knowledge. |
| `new:97` | term | home | Client-side prediction. General knowledge. |
| `new:98` | term | home | Server reconciliation. General knowledge. |
| `new:99` | term | home | Lag compensation. General knowledge. |
| `new:100` | term | home | Delta compression and quantization. General knowledge. |
| `new:101` | term | home | Interest management (relevancy). General knowledge. |
| `new:102` | term | home | NAT traversal and relay server. General knowledge. |
| `new:189` | hands-on | home | The page's exercises (D27). Done, a sketch with its output: a C++ sketch of about 40 lines in which a server steps the ball at 60 ticks a second and sends its position every third tick, one snapshot is lost, and the client draws the ball one snapshot interval behind by interpolating between the two newest snapshots; the output lists, frame by frame, the drawn position beside the true one, and the reader explains the error after the lost snapshot. Design: for a strategy game, a fighting game and a shooter, the reader names the model each needs (lockstep, rollback, client-server with prediction and lag compensation), what it costs, and what Strata would have to add for it (a transport, snapshots and their deltas, a way to rewind state, devices assigned to players) (about 250 words). General knowledge. |
| `automation:716-717` | term | link | Socket and TCP, defined on `automation/json-rpc` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Sockets, ports, TCP, non-blocking reads, framing and JSON-RPC | `automation/json-rpc` | must |
| The fixed step, the accumulator and game time counted in fixed steps | `core/time` | must |
| Vectors: positions and velocities, adding and scaling them | `basics/math-vectors` | must |
| Binary, integers, floating point and precision (quantizing a float into fewer bits) | `basics/numbers` | must |
| Threads and the main-thread rule | `basics/threads` | helps |
| Deterministic parallel work: ordered records, fixed chunks | `core/jobs` | helps |
| Drawing between fixed steps | `world/interpolation` | helps |
| Determinism of the physics step | `physics/world-step` | helps |
| FMA contraction and floating-point determinism across compilers | `engineering/flags-portability` | helps |
| Scene documents and their serialization | `world/serialization` | helps |
| Input actions | `input/actions` | helps |
| Hashes, MACs and the threat model of the editor's server | `automation/security` | helps |

## `appendix/game-ai` — Game AI in general: steering, pathfinding, navigation meshes and behaviour trees

**Covers.** The problem as the reader meets it: an animal in a forest should look alive, and a guard should reach the
player around a wall. The naive answers are to move straight at the target, or to pick a new random action every
frame; the first walks into walls and the second jitters. The idea: three layers on top of the senses. Deciding (what
to do now), finding a way (which way to go), and moving (how to get there), with rays and overlap tests as the senses
(can I see the player, is there ground). Deciding: finite state machines and their hierarchical form, behaviour trees
(sequences, selectors, conditions and a tick from the root), utility scoring, and goal-oriented action planning; a
table of their cost per agent, authoring effort, how they are debugged and who uses them, with sources (Red Blob Games
[S28] and the State chapter of Nystrom's *Game Programming Patterns* [S7] in `research/curricula.md`). Moving: steering
behaviours (seek, flee, arrive, wander, separation, and obstacle avoidance with rays), each as a desired velocity.
Finding a way: the level as a graph; breadth-first search, Dijkstra's algorithm and A* with a heuristic, worked by hand
on a grid of six by six cells; navigation meshes built from the walkable geometry, with path smoothing by string
pulling and local avoidance between agents.

Strata's choice: no AI module (the evidence), so game AI is script code. The SDK gives a script what it needs to build
it: `Physics::Raycast`, `RaycastAll`, `OverlapSphere` and `OverlapBox` with layer masks, the character controller's
moves, `Random` with seeds, `Timer`, the animator's `CrossFade`, and entities found by name. The one example is the Open
World sample's fox, `Samples/OpenWorld/Scripts/Wander.cpp`, in two excerpts: `Choose` and `SetState`, a state machine of
three states (Survey, Walk, Run) with a timer each, a seeded random target around the fox's home, and the animator's
state cross-faded to match; and `OnUpdate`, which waits while no ground is under the fox, seeks the target at walking or
running speed, turns the fox to face its way with `atan2`, and stands it on the terrain with a ray down to the Terrain
layer. The fox has no body (its prefab holds an Animator and a Script): it writes its own transform each frame and asks
physics only for the ground. Then how it would grow: arrive instead of a hard stop, a grid A* in a script, rays to step
around rocks. What Strata cannot do here: no navigation mesh to bake, no path queries, no shape sweeps in the API, and
no debug drawing from scripts, so a path cannot be drawn in the view. Common mistakes: deciding every frame, searching
a path every frame for every agent, a heuristic that overestimates (A* then misses the shortest path), and moving a
physics body by writing its transform instead of through its body or controller. The file's first comment says that
the target stays inside the fox's own world cell; the code picks a spot within `Range` of home and tests no cell, and
most foxes stand closer than `Range` to an edge of their cell, so the page says what the code does and does not repeat
the comment (an erratum of the engine). The exercises: A* in a sketch on the page's grid, run with three heuristics, and
a guard written as a state machine and as a behaviour tree. At the end the reader can choose a decision model and a
path search for a game, and write a first one in a script.

**Leaves out.**

- State machines, managers and object pools for game code → `make/patterns`
- The animator's state machine and cross-fades → `animation/state-machines`, `animation/blending`
- Raycasts, overlaps and their layer masks → `physics/queries`, `physics/collision-layers`
- Collide-and-slide movement of characters → `physics/character-controllers`
- Random numbers and seeds → `basics/math-probability`, `make/recipes`
- Graphs, queues and their cost → `basics/trees-graphs`

**Fit.** `fits`: about 4,750 words against L (5,000). The problem, the naive answer and the idea take 650 words, four
decision models with their table 900, path search with a worked A* and navigation meshes 750, the fox's two excerpts
500, steering 400, Strata's choice and what the SDK offers 350, the limits, the erratum of `Wander.cpp`'s first comment
and the mistakes 350, the two exercises 250, and the fixed parts 600; the four figures go with their sections.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:78` | not-done | home | Game AI (steering, pathfinding, navigation meshes, behaviour trees) is left to scripts. Evidence: `git grep -niE "pathfind\|path ?finding\|nav ?mesh\|navigation mesh\|behaviou?r ?tree\|steering\|blackboard\|utility ai\|goap" 822a7a46 -- Strata/src StrataScriptCore` finds nothing; `git grep -niwE "astar\|a-star\|dijkstra" 822a7a46 -- Strata/src StrataScriptCore` finds nothing; the word "navigation" alone matches only the game UI's keyboard and gamepad navigation (`Strata/src/Strata/GameUI/GameUIComponents.cpp`) |
| `new:103` | code | home | `Samples/OpenWorld/Scripts/Wander.cpp:68-87`: `Choose` and `SetState`, a three-state machine (Survey, Walk, Run) with a timer per state, a seeded random target around home, and a cross-fade of the animator per state |
| `new:104` | code | home | `Samples/OpenWorld/Scripts/Wander.cpp:36-66`: `OnUpdate`, waiting for ground, seeking the target, facing it with `atan2` and standing on the terrain by a ray down to the Terrain layer |
| `new:105` | figure | home | The three layers of game AI (decide, find a way, move) over the senses, as a diagram. General knowledge. |
| `new:106` | figure | home | A guard's behaviour as a state machine beside the same behaviour as a behaviour tree. General knowledge. |
| `new:107` | figure | home | A* on a six-by-six grid with a wall, step by step: the open set, the costs and the path found. General knowledge. |
| `new:108` | figure | home | The fox's three states and their timers, drawn from the code. Evidence: `Samples/OpenWorld/Scripts/Wander.cpp:68-87` |
| `new:109` | term | home | Behaviour tree (sequence, selector, condition, tick). General knowledge. |
| `new:110` | term | home | Steering behaviour (seek, flee, arrive, wander, separation). General knowledge. |
| `new:111` | term | home | A* search and its heuristic (admissible heuristic). General knowledge. |
| `new:112` | term | home | Navigation mesh (navmesh). General knowledge. |
| `new:113` | term | home | Utility AI. General knowledge. |
| `new:114` | term | home | Goal-oriented action planning (GOAP). General knowledge. |
| `new:115` | term | home | Line of sight, as an AI's sense. General knowledge. |
| `new:116` | term | home | Local avoidance. General knowledge. |
| `new:187` | erratum | home | The first comment of `Wander.cpp` says that a fox's target stays inside its own world cell, so that it never walks into a cell that is not loaded; `Choose` picks a spot 0.3 to 1 times `Range` (22 m) from the fox's home and tests no cell, and 27 of the 30 foxes stand within 22 m of an edge of their 64 m Wildlife cell. The page states what the code does and does not repeat the comment (process.md's table of errata, kind `engine`). Evidence: `Samples/OpenWorld/Scripts/Wander.cpp:1-2`, `:20`, `:68-77`; `Samples/OpenWorld/Assets/Worlds/Island.stworld:2649` (the Wildlife layer's `CellSize` of 64); the translations of the 30 foxes in `Samples/OpenWorld/Assets/Worlds/Island/Wildlife/*.stscene`, the only scenes that use the script |
| `new:190` | hands-on | home | The page's exercises (D27). Done, a sketch with its output: A* on the page's six-by-six grid with its wall, in a C++ sketch whose open set is a priority queue; it prints the path, its length and the number of cells taken from the open set, and the reader predicts, then runs, the same search with no heuristic (Dijkstra's algorithm) and with one that overestimates, and explains the differences in the counts and the paths. Design: a guard that patrols, chases a player it sees and goes back, written as a state machine and as a behaviour tree; the reader says which a Strata script would hold more simply, and where each would put the fox's timers (about 250 words). General knowledge. |
| `new:37` | not-done | link | No debug drawing from scripts, stated on `gpu/debug-drawing` |
| `physics:114` | feature | use | `Raycast`, `RaycastAll`, `OverlapSphere` and `OverlapBox`: the senses a script's AI uses |
| `physics:116` | feature | link | No shape casts in the public API, so a wide agent cannot sweep its shape |
| `physics:132` | feature | link | Character controllers, for agents that must collide while they move |
| `scripting:125` | feature | use | The SDK's `Physics` and `RaycastHit`, as the fox calls them |
| `scripting:133` | feature | use | The SDK's `Random` with seeds |
| `scripting:134` | feature | use | The SDK's `Timer` |
| `animation:85` | feature | link | The animator's own state machine, which the fox's states drive with `CrossFade` |
| `animation:283` | concept | link | State machines for animation, a sibling of decision state machines |
| `gamedev:257` | feature | use | The Open World sample: foxes with an animation controller in streamed cells |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Graphs, queues and a priority queue, and the cost of their operations (A* keeps its open set in a priority queue) | `basics/trees-graphs` | must |
| Rays, planes and intersection tests | `basics/math-geometry` | must |
| Vectors: length, direction, normalizing, `atan2` | `basics/math-vectors` | must |
| A rotation from an axis and an angle (`glm::angleAxis`) | `basics/math-rotations` | helps |
| Random numbers and seeds | `basics/math-probability` | helps |
| Script classes, their callbacks (`OnCreate`, `OnUpdate`) and fields | `scripting/script-system` | helps |
| Physics queries and their layer masks | `physics/queries` | helps |
| Collision layers | `physics/collision-layers` | helps |
| Character controllers | `physics/character-controllers` | helps |
| Animation state machines and cross-fades | `animation/state-machines` | helps |
| State machines for game code | `make/patterns` | helps |
| World cells that stream in and out | `worlds/why-streaming` | helps |
| The standard containers (`std::priority_queue`, the exercise's sketch) | `basics/cpp-generic` | helps |

## `appendix/math-cheatsheet` — Math cheat sheet

**Covers.** One paragraph on how to read the page: it teaches nothing; each line names the primer that teaches it, and
a reader who meets a symbol here for the first time follows that link. Then two tables. The first is how to read the
symbols: each symbol that a page of the book uses (Σ, ∫, ∂, ∇, ·, ×, ‖v‖, |x|, θ and φ, ω, π, e and exp, log, √, ∈, ≈,
≤, ∞, the hat of a unit vector, the transpose and the inverse of a matrix, the conjugate of a quaternion, and big-O), with
how it is read aloud, what it does, one example with small numbers, and the page that teaches it. The second holds the
formulas, grouped by primer in the order of `basics`: numbers (powers and logarithms, EV stops and decibels, e and the
exponential, the spacing of floating-point numbers), data structures (the costs in big-O), vectors (length, normalizing,
the dot product and the angle, the cross product, `atan2`), matrices (TRS, composing transforms, the inverse of a rigid
transform), bases (the transpose of an orthonormal basis as its inverse, changing basis, the determinant and its sign as
a mirror, normals through the inverse transpose, decomposing a matrix into translation, rotation and scale), projection
(the perspective divide, reversed depth), rotations (axis and angle to a quaternion, rotating a vector, slerp),
geometry (a ray against a plane, a sphere and a box; the distance of a point to a plane), change (the explicit and the
semi-implicit Euler step, F = m a, impulse), interpolation (lerp, inverse lerp and remapping, smoothstep, exponential
smoothing with 1 - exp(-k dt)), color (the sRGB transfer function, luminance), signals (the Nyquist rate, box and tent
filters), probability (expected value, the Monte Carlo estimate with a density), and the sphere (the solid angle of a
sphere, spherical coordinates, the first bands of spherical harmonics, the octahedral map). Each formula has one line
of meaning, its units, and the page that derives it; no derivation is repeated.
Strata's own conventions (axes, handedness, units, matrix order, depth and color spaces) and the rendering parts'
symbols are `reference/notation`'s: the page links it once. The symbol table is checked against the notation tables
of the parts (`style.md` §4), so every symbol a page introduces is listed here with its teacher.

**Leaves out.**

- Teaching each symbol and formula → `basics/numbers`, `basics/math-vectors`, `basics/math-matrices`, `basics/math-bases`, `basics/math-change`, `basics/math-probability`
- Strata's conventions and the rendering parts' symbols → `reference/notation`
- Strata's math types and functions (`AABB`, `Frustum`, `Ray`, the projections) → `core/math`

**Fit.** `fits`: about 430 words against M (3,000). That is the prose: the paragraph on how to read the page and one
line for each of the 14 groups; the page's size comes from its two tables, written by hand (R36): about 30 symbols (700
words) and about 65 formulas in 14 groups (1,850).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:117` | concept | link | How to read the symbols: each operator symbol with how it is read, what it does and the page that teaches it (`style.md` §4 asks for this table). General knowledge. |
| `new:118` | concept | link | Numbers: powers, logarithms, EV stops, decibels, e and the exponential, the spacing of floats; taught on `basics/numbers`. General knowledge. |
| `new:119` | concept | link | The costs of data structures in big-O; taught on `basics/data-structures`. General knowledge. |
| `new:120` | concept | link | Vectors: length, normalizing, dot and cross products, `atan2`; taught on `basics/math-vectors`. General knowledge. |
| `new:121` | concept | link | Matrices: TRS, composing transforms, the inverse of a rigid transform; taught on `basics/math-matrices`. General knowledge. |
| `new:186` | concept | link | Bases: the transpose and orthonormal bases, changing basis and tangent space, the determinant and its sign as a mirror, normals through the inverse transpose and the cofactor matrix, decomposing a matrix into translation, rotation and scale; taught on `basics/math-bases`. General knowledge. |
| `new:122` | concept | link | Projection: the perspective divide, homogeneous coordinates, reversed depth; taught on `basics/math-projection`. General knowledge. |
| `new:123` | concept | link | Rotations: axis and angle, quaternions, rotating a vector, slerp; taught on `basics/math-rotations`. General knowledge. |
| `new:124` | concept | link | Geometry: rays against planes, spheres and boxes, point-plane distance; taught on `basics/math-geometry`. General knowledge. |
| `new:125` | concept | link | Change: rates, accumulation, Euler steps, Newton's second law and impulse; taught on `basics/math-change`. General knowledge. |
| `new:126` | concept | link | Interpolation: lerp, inverse lerp, remap, smoothstep, exponential smoothing; taught on `basics/math-interpolation`. General knowledge. |
| `new:127` | concept | link | Color: the sRGB transfer function, luminance; taught on `basics/color`. General knowledge. |
| `new:128` | concept | link | Signals: sampling, the Nyquist rate, filters; taught on `basics/signals`. General knowledge. |
| `new:129` | concept | link | Probability: expected value, densities, the Monte Carlo estimate; taught on `basics/math-probability`. General knowledge. |
| `new:130` | concept | link | The sphere: solid angle, spherical coordinates, spherical harmonics, octahedral maps; taught on `basics/math-sphere`. General knowledge. |
| `foundation:325` | concept | link | Math for engines as Strata chose it (glTF's axes, reversed Z with an infinite far plane), homed on `core/math` |
| `foundation:139` | feature | link | The conventions comment of `Math.h`, which `reference/notation` collects |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Binary, integers, floating point; powers, logarithms and the exponential function | `basics/numbers` | helps |
| Data structures and what they cost | `basics/data-structures` | helps |
| Vectors: length, direction, dot and cross products; angles in degrees and radians | `basics/math-vectors` | helps |
| Matrices, transforms, hierarchies and spaces | `basics/math-matrices` | helps |
| Bases, the determinant and normals: orthonormal frames, tangent space, mirrors and the inverse transpose | `basics/math-bases` | helps |
| Projection: view and projection matrices, homogeneous coordinates, depth | `basics/math-projection` | helps |
| Rotations: Euler angles, axis and angle, quaternions, slerp | `basics/math-rotations` | helps |
| Rays, planes, boxes and intersection tests | `basics/math-geometry` | helps |
| Change over time: rates, accumulation, Euler steps, Newton's laws | `basics/math-change` | helps |
| Blending and smoothing: lerp, easing, exponential smoothing | `basics/math-interpolation` | helps |
| Color: linear and sRGB values | `basics/color` | helps |
| Sampling, aliasing and filtering | `basics/signals` | helps |
| Probability, random numbers, integrals and Monte Carlo | `basics/math-probability` | helps |
| Solid angles, spherical coordinates, spherical harmonics, octahedral maps | `basics/math-sphere` | helps |

## `appendix/history` — Which release brought what

**Covers.** One paragraph on how to read it: versions follow the engine's development waves (0.3.0, the first release,
held waves 1 to 3; each later minor version holds one wave) and patch versions carry fixes; the book targets 0.8.0, and
at the pin the programs still report 0.7.0, which is not a mistake (one sentence, as `style.md` §13 asks). Then one
section per release, oldest first: 0.3.0 (waves 1 to 3, the last completed on 2026-10-12), 0.4.0 (wave 4, completed on
2026-10-19), 0.5.0 (wave 5, completed on 2026-10-20, the release that moved physics from Jolt to box3d), 0.6.0 (wave 6,
completed on 2026-10-23), 0.7.0 (wave 7, integrated on 2026-10-28) and 0.8.0 (wave 8). Each section gives the date and
the wave, a table of what the release brought by area (editor, worlds, rendering, game UI, physics, audio and
animation, scripting, exported games, AI agents, instruments and scale, as the release notes group them), each row
linking the page that teaches the feature, and the upgrade notes that changed projects (in 0.6.0 the collision layers
became the project's, migrated once from 0.5.0's scenes). The rows come from each release's "What's new" (for 0.3.0,
"What you can do with it"), "What changes with box3d" and "Upgrading from" sections, and from the Roadmap's Status
paragraph of each wave. The 0.8.0 section is drafted at the pin from `Docs/Plans/Wave8/ReleaseNotes.md` and rewritten
from `Docs/Releases/0.8.0.md` at the tag; its rows agree with the pages' `since: 0.8.0` front matter, so the table and
the "New in 0.8.0" labels name the same features. The build and tests, which the release notes group under no area of
their own, get a row in each release that the Roadmap's Status dates them in (the perf lab in wave 1, the CI jobs and
shards of wave 4, the look-dev harness of wave 7, Slang in wave 8). Features the documents do not date (the surveyors
list them, below) are named as not dated, never guessed. The page states no plan: what the Roadmap lists for later is quoted on
`appendix/not-in-strata` and the subsystem pages.

**Leaves out.**

- What each feature does and how it works → `reference/term-index`
- What the engine's documents plan for later → `appendix/not-in-strata`
- How a release is built, packaged and published → `engineering/releasing`

**Fit.** `fits`: about 1,200 words against M (3,000). That is the prose: a paragraph per release with its date, wave
and upgrade notes (750), the undated features (250) and the paragraph on versions and the pre-release pin (200); the
page's size comes from its tables, written by hand from the release notes (R36): six release tables of about 12 rows
each (1,300 words) and the build and test rows (150), whose 0.8.0 section phase B rewrites from the notes at the tag.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `audio-input:755` | open | home | The dating of audio and input: audio, basic input, gamepads and simulated input in 0.3.0; `input.sequence`, `input.click` and UI navigation in 0.4.0; simulated input at time scale 0 in 0.5.0; input actions and rebinding in 0.6.0; the players' bindings in the user data folder of shipped games in 0.7.0; finer dating stated as not traced |
| `gamedev:699` | open | home | Features whose release the documents do not state (the long-path build fallback, `UIMask` and world-space canvases, the Scripts root of the Content Browser, the Hierarchy's search tokens); morphological anti-aliasing is 0.7.0's by its notes |
| `gamedev:701` | open | home | Wave 8's status at the pin: the Showcase, `Scene.Timing` and interpolation, the drop ghost and `asset.place`, the editor's frame-rate preferences, Source Radius and experimental global illumination are on main; what 0.8.0 ships is read from its notes at the tag |
| `new:131` | feature | home | 0.3.0, the first release: waves 1 to 3, completed on 2026-10-12. Evidence: `Docs/Releases/0.3.0.md:3-6`, "What you can do with it" at `:24-107`; `Docs/Roadmap.md:36, 66, 202` (the Status paragraphs of waves 1, 2 and 3) |
| `new:132` | feature | home | 0.4.0: wave 4, completed on 2026-10-19. Evidence: `Docs/Releases/0.4.0.md:3-6`, "What's new in 0.4.0" at `:27-95`; `Docs/Roadmap.md:360` |
| `new:133` | feature | home | 0.5.0: wave 5, completed on 2026-10-20; physics on box3d instead of Jolt. Evidence: `Docs/Releases/0.5.0.md:3-6`, "What's new in 0.5.0" at `:28-73`, "What changes with box3d" at `:75-103`; `Docs/Roadmap.md:460, 488` |
| `new:134` | feature | home | 0.6.0: wave 6, completed on 2026-10-23, and the upgrade from 0.5.0. Evidence: `Docs/Releases/0.6.0.md:3-7`, "What's new in 0.6.0" at `:30-115`, "Upgrading from 0.5.0" at `:117-151`; `Docs/Roadmap.md:511, 1334` (collision layers for the whole project, migrated once from 0.5.0's scenes) |
| `new:135` | feature | home | 0.7.0: wave 7, integrated on 2026-10-28, and the upgrade from 0.6.0. Evidence: `Docs/Releases/0.7.0.md:3-7`, "What's new in 0.7.0" at `:31-95`, "Upgrading from 0.6.0" at `:97-130`; `Docs/Roadmap.md:574` |
| `new:136` | feature | home | 0.8.0: wave 8, from the draft notes at the pin and the release notes at the tag. Evidence: `Docs/Roadmap.md:609` ("Wave 8 in progress"); `Docs/Plans/Wave8/ReleaseNotes.md:1-6` (written into `Docs/Releases/0.8.0.md` at the release), "What's new" at `:8-307`, "Defaults that change" at `:308-324`, "Upgrading from 0.7.0" at `:325-368` |
| `new:137` | feature | home | Versions follow the waves, and patch versions carry fixes. Evidence: `Docs/Releases/0.3.0.md:5-6`; `Docs/Releases/0.7.0.md:6-7` |
| `new:138` | feature | home | At the pin the programs report 0.7.0 while the book targets 0.8.0: a pre-release build reports the previous release. Evidence: `CMakeLists.txt:4` (`VERSION 0.7.0`); `Strata/src/Strata/Core/Version.h.in:17` (`c_EngineVersion`) |
| `gamedev:254-258` | feature | use | The samples and the release each arrived in (Tetris 0.3.0; Third-Person, Physics Playground and Open World 0.5.0; the Showcase in wave 8) |
| `physics:126` | feature | use | The collision layers' migration from 0.5.0's scenes, an upgrade note of 0.6.0 |
| `animation:645` | open | use | What the documents do not date in animation (the refinements of `WhenVisible`) |
| `assets:799` | open | use | What the documents do not date in the asset pipeline |
| `automation:841` | open | use | The automation area already exists in 0.3.0; the RPC core came in waves 1 and 2, before any release file |
| `build-test:765` | open | home | The dating of the build and tests: the perf lab in wave 1; release 0.3.0 with the Dist CI job, the perf lock, the CI-compiler lint and the CI status tool in wave 4's step 0; layer libraries, optional modules, precompiled headers, the Core shards, the fuzz run, the compiler cache and the Windows Debug CI job in 0.4.0; the look-dev harness in 0.7.0; Slang and the build without GLFW in wave 8, not yet released at the pin; the rest stated as not dated |
| `editor-core:800` | open | use | What the documents do not date in the editor's core |
| `editor-ui:874` | open | home | The release of arrival of the editor's interface features: what the documents date (idle throttling, the launcher, multi-edit, the Activity, Streaming, Performance and Problems panels, CJK fonts in 0.3.0; the Game view and others later) and what they leave undated, stated as such |
| `foundation:696` | open | use | What the documents do not date in the foundation |
| `gameui:740` | open | use | The game UI's history inside 0.4.0 to 0.7.0 |
| `physics:582` | open | use | What the documents do not date in physics |
| `render-core:843` | open | use | What the documents do not date in the renderer's core |
| `render-direct:824` | open | use | The release of the shadows' horizon fade, not stated |
| `render-image:804` | open | use | The image features whose release is partly inferred (bloom, tone mapping, grading, FXAA) |
| `render-scene:718` | open | use | What the documents do not date in drawing a scene |
| `scene-ecs:742` | open | use | What the documents do not date in scenes and the ECS |
| `scripting:687` | open | use | The wave in which physics bodies, queries, audio and game flow joined the script API, not stated |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The engine's programs, libraries, modules and layers | `core/map` | helps |
| How a release is packaged and published | `engineering/releasing` | helps |
| Layers, registries and modules chosen at compile time (the areas the tables group by) | `core/layers-registries` | helps |

## `appendix/further-reading` — Further reading

**Covers.** One paragraph on how to read it: each source has one line on what it gives and its level (beginner,
intermediate, advanced), as every page's own Further reading does (`style.md` §6.3). Then three parts. First, the
engine's own documents, for readers who want the source of truth after the book: `AGENTS.md`, `Docs/Architecture.md`,
`Docs/DeveloperGuide.md`, `Docs/Roadmap.md`, the release notes in `Docs/Releases/`, the guides of `Docs/Manual/`
(anti-aliasing, the camera, game UI, the Game view, graphics, lighting, prefabs, scripting, settings and worlds) and the
skills in `.claude/skills/`, which teach agents (and anyone) to build the engine, add a component, write scripts, drive
the editor and make a game; each with whom it serves and the book's pages it backs. Second, the books and sites that
serve the whole field, from `research/curricula.md` §6 and its judgements in §2 (Game Engine Architecture, Real-Time
Rendering, Physically Based Rendering, Foundations of Game Engine Development, 3D Math Primer, Real-Time Collision
Detection, Game Programming Patterns, learncpp.com, LearnOpenGL and the Vulkan tutorials, Gaffer on Games, Gambetta,
Red Blob Games, Catto's publications, Filament's notes, Ciechanowski's articles), each with its level and the parts it
serves; sources the research could not fetch are marked as the research marks them. Third, one section per part in
the book's order, collected from every page's `## Further reading` and merged, so a source appears once under its part
with the pages that cite it. The third part is generated from the pages in phase B by `tools/reference.py render`
(`pipelines.md` §7.1, the route "further reading"); the page states no claim of its own.

**Leaves out.**

- Credits and licenses of what the book shows or quotes → `appendix/credits`
- The meaning of the terms the sources use → `reference/glossary`

**Fit.** `fits`: about 800 words against M (3,000). That is the prose written by hand: the paragraph on top (100) and
the lines of the first two parts, the engine's documents (350) and the books and sites of the field (350); the page's
size comes from the third part, about 120 sources of the parts at one line each (2,100 words), generated by
`tools/reference.py render` in phase B, whose count is known only when the pages are written.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:139` | feature | home | The engine's own documents as further reading: `AGENTS.md`, `Docs/Architecture.md`, `Docs/DeveloperGuide.md`, `Docs/Roadmap.md`, `Docs/Releases/`, `Docs/Manual/` and the skills. Evidence: `git ls-tree --name-only 822a7a46 Docs/Manual/` lists `AntiAliasing.md`, `Camera.md`, `GameUI.md`, `GameView.md`, `Graphics.md`, `Lighting.md`, `Prefabs.md`, `Scripting.md`, `Settings.md` and `Worlds.md`; `git ls-tree --name-only 822a7a46 .claude/skills/` lists `strata-add-component`, `strata-build-test`, `strata-editor-automation`, `strata-make-a-game` and `strata-scripting` |
| `new:140` | feature | home | The books and sites of the whole field, each with its level and the parts it serves (`research/curricula.md` §2 and §6, S1 to S39). General knowledge. |
| `new:141` | feature | home | One section per part, collected from every page's `## Further reading` (`style.md` §6.3) by `tools/reference.py render` in phase B (`pipelines.md` §7.1, the route "further reading") and merged, each source with the pages that cite it. General knowledge. |
| `automation:223-225` | feature | use | The two skills for agents and the package readme's "Connect an AI agent", as reading for agents and game makers |

**Assumes.**

none

## `appendix/credits` — Credits and licenses

**Covers.** One paragraph on how to read it: what the book shows or quotes that others made, where it comes from and
under which license. Then the tables. The libraries of `ThirdPartyNotices.md`, with version, license and whether games
ship them; a page may quote a library's source (`vendor:<lib>`) only when the library is listed there and named here
with its license (`pipelines.md` §3.2). The fonts the pictures show: the editor's Inter and JetBrains Mono (SIL Open
Font License 1.1) and Lucide's icons (ISC, the icons derived from Feather also MIT), and Roboto Medium (Apache 2.0), the
default font of text in every game. Code that Strata derived from other projects (radiance-cascades-lab, MIT, in the
shaders of global illumination), whose notice travels with any excerpt of those files. The sample assets that figures
show, by sample and pack, from each sample's `CREDITS.md`: almost all are CC0; the Open World's fox carries CC BY 4.0
parts (rigging, animation and glTF conversion), so every figure that shows the fox gives its attribution in its caption
or beside it, and this page lists those figures and holds the fox's full entry, with the two copyright lines that the
engine's own credit leaves out (an erratum of the engine) and the link to the Khronos commit. The book's own assets:
the files of `tutorials/assets/` (with their `CREDITS.md`) and the textures of the labs, each CC0 or CC-BY. And the
engine itself: every excerpt and every picture of the book comes from the owner's engine at the pin, and of the
engine's own terms the page says only what its repository says there. Last, the book's own terms: the statement
"Copyright © 2026 2042Third. All rights reserved.", with "Except where otherwise noted" and its two exceptions, and the
first exception, the permission for the book's code, in the reader's words (a reader may put the book's code and
project files into their own games and ship them, also commercially, but may not publish them as a collection, a
course or a book). The page holds no license text of its own: it links the site's `license.txt` and
`third-party-notices.txt`.

**Leaves out.**

- How Strata pins, wraps and upgrades its libraries, and the rule for code from other projects → `engineering/third-party`
- Choosing assets with licenses a game may use → `make/assets`
- A game's own credits screen and notices file → `make/export`, `worlds/export`
- The books and articles the book's ideas come from → `appendix/further-reading`

**Fit.** `fits`: about 780 words against S (1,500). That is the prose: the paragraph on how to read the page with the
tables' introductions (600), the book's statement with the permission for its code (120) and the fox's full entry (60);
the page's size comes from its tables, written by hand from `ThirdPartyNotices.md` and the samples' `CREDITS.md` (R36):
twenty libraries, four fonts, one derived project, about nine sample packs and the figures that need an attribution.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:142` | feature | home | The libraries: name, version, license and whether games ship them; the list a `vendor:` quote must be in. Evidence: `ThirdPartyNotices.md:8-29` |
| `new:143` | feature | home | The fonts in the pictures: Inter and JetBrains Mono (OFL 1.1) and Lucide (ISC; Feather's icons MIT) in the editor; Roboto Medium (Apache 2.0) in every game. Evidence: `ThirdPartyNotices.md:31-43`; `StrataEditor/Resources/Fonts/` holds `Inter-OFL.txt`, `JetBrainsMono-OFL.txt` and `Lucide-LICENSE.txt` |
| `new:144` | feature | home | Code derived from other projects: radiance-cascades-lab (MIT) in the shaders of global illumination, its notice with any excerpt of them. Evidence: `ThirdPartyNotices.md:45-79` |
| `new:145` | feature | home | The sample assets in figures, by sample and pack, and the attribution the fox's CC BY 4.0 parts require beside every figure that shows it; the fox's full entry is `new:185`, not the engine's shorter credit. Evidence: `ThirdPartyNotices.md:81-96`; `Samples/OpenWorld/CREDITS.md:3-5, 11` |
| `new:185` | erratum | home | The fox's full credit, which the engine's credit leaves out: the model's notes at Khronos commit `edc7c9e67c639d230715049ee31f9a96a6babbbe` (`Models/Fox`) hold "© 2014, tomkranis." (rigging and animation, CC BY 4.0) and "© 2017, @AsoboStudio and @scurest." (conversion to glTF, CC BY 4.0) beside PixelMannen's model (CC0 1.0). The page copies the entry with the link to that commit, and every caption of a fox names its authors and license (process.md's table of errata, kind `engine`; `critique/rulings-6.md`, R22), about 60 words. Evidence: `Samples/OpenWorld/CREDITS.md:11` and `ThirdPartyNotices.md:92` name the authors and licenses but no copyright line; `git grep -n tomkranis 822a7a46` finds only those two lines, `Samples/OpenWorld/README.md:63`, the in-game credits of `Samples/OpenWorld/Assets/Worlds/Island.stscene:144` and the binary `Fox.glb`; at the Khronos commit the two lines stand in the "Legal" section of `Models/Fox/README.md`, and as owner and year in its `metadata.json` |
| `new:146` | feature | home | The book's own assets: `tutorials/assets/` with its `CREDITS.md`, and the labs' committed textures, CC0 or CC-BY (`pipelines.md` §5 and §6). General knowledge. |
| `new:147` | feature | home | The engine itself as the source of every excerpt and picture; the repository holds no license file at its root, so the page names the repository and its owner and says only what the repository says of its terms. Evidence: `git ls-tree --name-only 822a7a46` lists no `LICENSE` file (its entries are `.clang-format` to `Tools`, with `ThirdPartyNotices.md` and `README.md`) |
| `new:183` | feature | home | The book's statement, stated once: "Copyright © 2026 2042Third. All rights reserved.", then "Except where otherwise noted" and its two exceptions, the book's code (`new:184`) and third-party material, which keeps its own terms; the holder and the year are `site.json`'s `copyright.holder` and `copyright.year`, and the page links `<base>/license.txt` and `<base>/third-party-notices.txt` (`critique/rulings-6.md`, R20 and R22). General knowledge. |
| `new:184` | feature | home | The permission for the book's code, in the reader's words: the code and project files the book gives (the listings written for the book, the tutorial files, the command scripts, the lab files, the worked solutions and the checkpoint projects) may go into the reader's own programs and games and ship with them, also commercially, without asking and without naming the book; they may not be published as a collection of examples, a course or a book; the text, the pictures, the diagrams and the site are for reading and for printing for one's own use. Excerpts of the engine stay the engine's, and third-party files keep their own terms (`critique/rulings-6.md`, R21), about 120 words with `new:183`. General knowledge. |
| `build-test:96` | feature | use | `ThirdPartyNotices.md`: libraries, fonts, derived code and sample packs |
| `build-test:98` | feature | use | The rule for code from other projects: permissive only, copyleft for ideas only, a notice row and the license text |
| `gamedev:260` | feature | use | Every sample's README credits its assets and its `CREDITS.md` lists every file |
| `gamedev:519` | rule | use | Asset licenses: CC0 or CC-BY only, credited |
| `editor-ui:50` | feature | use | The editor embeds its fonts and `ThirdPartyNotices.md` |
| `animation:212` | feature | use | The Third-Person robot (CC0), the most pictured asset of the book's animation part |
| `build-test:639` | term | link | Permissive and copyleft licenses, defined on `engineering/third-party` |
| `gamedev:665` | term | link | CC0 and CC-BY, defined on `make/assets` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Submodules, the vendor folder and pinned libraries | `engineering/third-party` | helps |
| Permissive and copyleft licenses, and notices | `engineering/third-party` | helps |
| Asset licenses (CC0 and CC-BY) as a game maker meets them | `make/assets` | helps |
| A game's credits and notices when it ships | `make/export` | helps |

## Passed on

none

## Not taken

none

## Questions for the planner

none
