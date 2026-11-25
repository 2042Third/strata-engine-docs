# Inventory: Making a game with Strata (the game developer's whole journey)

Surveyed at `main` 822a7a46 (2026-11-10) of `G:/GameEngineAI`. Paths are relative to the repository root. "DG" is
`Docs/DeveloperGuide.md`, "Arch" is `Docs/Architecture.md`, "Manual/X" is `Docs/Manual/X.md`; `L123` is a line number at
this commit. Releases: 0.3.0 (first, waves 1-3), 0.4.0, 0.5.0, 0.6.0, 0.7.0 (latest release); "wave 8" means on `main`
after 0.7.0 with no release notes yet (it becomes 0.8.0).

This area is the *user's side* of the whole engine. Most systems it touches (renderer, physics, animation, UI, worlds,
asset pipeline, scripting ABI, editor commands) have their own inventories; this one maps what a game maker sees and does,
where it lives in code, and how the five samples teach it. Cross-references to other areas are marked "(see area: X)".

---

## 1. Features

### 1.1 Getting Strata and starting it

| Feature | What it is | Where it lives | Documented | Release |
| --- | --- | --- | --- | --- |
| Release archives | One folder per platform (Windows x64, Linux x64 Ubuntu 24.04+, macOS 14+ arm64) with `StrataEditor`, `StrataRuntime`, `StrataCLI`, `Samples/`, `StrataScriptCore/`, `Docs/Manual/`, `Skills/`, `StrataInstall.json`, `ThirdPartyNotices.md` | `CMake/StrataPackaging.cmake`; the README shipped is `Docs/Releases/PackageReadme.md` | PackageReadme "What is in this folder" L10; README.md "Download" | 0.3.0 |
| Requirements and first start | Vulkan 1.2 GPU with `imageCubeArray`; unsigned executables (Windows Unblock/SmartScreen, macOS `xattr -dr com.apple.quarantine`); MoltenVK on macOS; Linux package list | PackageReadme "Requirements" L26, "First start" L63 | same; each release's "Requirements"/"First start" | 0.3.0; cube arrays 0.6.0 |
| Script toolchain discovery | A downloaded editor finds VS 2022 17.10+/2026 C++ tools + CMake (Windows), g++/clang++ + Ninja/Make + CMake 3.25 (Linux), Xcode CLT + CMake (macOS) at the first build and names what is missing | `StrataEditor/src/Editor/ScriptToolchain.h/.cpp`; `script.status` -> `toolchain` | Manual/Scripting "Where builds happen" L208; PackageReadme L50 | 0.3.0 |
| Logs | Editor log `<user data>/Strata/Logs/StrataEditor.log`, game log `<user data>/<Game>/Logs/Game.log` | `Strata/Core/Log`, `Platform` | PackageReadme "When something goes wrong" L132 | 0.3.0 |
| GUI-subsystem programs | Editor and games open no console; PowerShell waits only when output is piped (`| Write-Output`) | `Application::GetProgramRun`, `ReportFatalError` | README "Making a game"; AGENTS "Windows subsystem" | 0.3.0 |

### 1.2 The launcher, projects, templates, samples

| Feature | What it is | Where it lives | Documented | Release |
| --- | --- | --- | --- | --- |
| Launcher | What the editor shows with no project: hero band, New Project, Open Project, template cards, sample cards with pictures, recent projects as cards (search, context menu), "Connect an AI agent" card with the exact `claude mcp add strata -- "<StrataCLI>" mcp` line, footer (version, GPU, startup time, About) | `StrataEditor/src/Panels/WelcomePanel.h/.cpp` (header comment L1-10), `Editor/RecentProjects`, `Editor/ProjectThumbnail` | DG "Launcher" L3508, "Templates and recent projects" L3483 | 0.3.0; redesigned in later waves |
| Continue without a project | Editor without project; File > Show Launcher returns | `EditorLayer.cpp` | tests `EditorLauncherTests.cpp` L452, L470 | — |
| Templates | `empty` (no scene) and `basic3d` ("Basic 3D": Main Camera primary + AudioListener at (0,2,6), Sun 120,000 lux 40 degrees up at azimuth 20 with 0.53 degree soft shadows, Sky with physical atmosphere (Clear preset), 20x20 Ground plane with `Materials/Ground.stmat` (dark stone, roughness 0.9) and a 1 m thick static box collider whose top is y = 0, Post Process with Filmic, auto exposure +0.25, TAA); saved as `Scenes/Main.stscene`, set as start scene | `StrataEditor/src/Editor/ProjectTemplates.h/.cpp` (`PopulateBasic3D` L49-95) | DG "Templates and recent projects" L3483; skill make-a-game §2 L42 | 0.3.0 (procedural sky); atmosphere + real sun 0.7.0 |
| Project creation | `project.create {directory, name, template}` writes `<Name>.stproj`, `Assets/`, `.gitignore` for `.strata/`, `Scripts/` with `CMakeLists.txt` and example `Spinner.cpp` | `EditorContext`, `Editor/ScriptProject.cpp` (`MakeScriptCMakeLists` L207, `MakeExampleScript` L224, `CreateScriptProjectFiles` L383) | skill make-a-game §2; skill scripting "The workflow" L660 | 0.3.0 |
| Project file | `.stproj`: `Project` (AssetDirectory, Export {AlwaysInclude, LoadingScene}, Game {Title, Version, Company, Copyright, Icon}, Name, Scripts {ModuleName, SourceDirectory}, StartScene) and `Settings` sections (e.g. `Input.Actions`) | `Strata/src/Strata/Project/Project.h`, `GameInfo.h`; example `Samples/ThirdPerson/ThirdPerson.stproj` | Manual/Settings L1-130; DG "Project settings" L1146 | format v3 in 0.6.0 |
| Samples, Open Sample | `Samples.json` index (Directory, Name, Description, Picture, optional `"Budget": "Showcase"`); samples are always opened as *copies* without `.strata`; the picture becomes the copy's thumbnail | `StrataEditor/src/Editor/ProjectSamples.h/.cpp`; `Samples/Samples.json`; `project.samples`, `project.openSample {sample, directory}` | DG "Samples" L6451; ProjectSamples.h L11-48 | Tetris 0.3.0; three more 0.5.0; Showcase wave 8 |
| Recent projects | Cards, read on an I/O thread, missing ones hidden; `editor.recentProjects`, `editor.removeRecentProject` | `Editor/RecentProjects.h` | DG L3483 | 0.3.0 |
| Project migration | 0.5.0 projects: per-scene collision layers become the project's, file saved as v3; preferences copied from `EditorSettings.json` | `Editor/ProjectMigration.h` | Manual/Settings L118, L152; 0.6.0 "Upgrading" | 0.6.0 |

### 1.3 The editor's windows

| Feature | What it is | Where it lives | Documented | Release |
| --- | --- | --- | --- | --- |
| Panel set | Registered built-ins: Scene (viewport), Game, Hierarchy, Inspector, Asset, Console, Problems, Content Browser, Welcome (launcher), Streaming, Performance, Activity, Project Settings | `EditorLayer::RegisterBuiltinPanels` `StrataEditor/src/EditorLayer.cpp` L337-365; `UI/EditorPanelRegistry.h` | Arch "Editor" L3217; README "Editor" | 0.3.0; Game view 0.4.0; Project Settings 0.6.0 |
| Menus | File (New/Open Project, Open Recent, Open Sample, Close Project, Show Launcher, New/Open/Save/Save As Scene, Recover Unsaved Changes, Set as Start Scene, Export Game, Project Settings, Preferences, Exit), Edit (Cut, Copy, Paste, Duplicate, Rename, Delete, Drop to Ground, Select All, Undo/Redo), View (panels, Reset Layout), Entity, Scripts (Build Scripts Ctrl+B, Reload Scripts, Create Script Build, New Script, Open Scripts Folder, External Editor, Show Problems), Help (About) | `StrataEditor/src/EditorLayer.cpp`, `UI/EditorActions.cpp` | README "Making a game"; Manual/Scripting | 0.3.0+ |
| Bedrock look | Basalt/Limestone/Ochre theme, Inter + JetBrains Mono + Lucide icons, scale-aware | `UI/Theme`, `UI/EditorFonts`, `UI/Icons.h` | Roadmap "Pillars" L8; DG "Editor UI rules" | 0.3.0 |
| Status bar pills | Build state ("Building", "Build failed", "Scripts unused"), assets, connected agents, frame time; each leads to the panel that explains | `EditorLayer::StatusPillText` | DG "Shortcuts and editor status" L3346 (text at L2810ff) | 0.3.0 |
| Toasts / notifications | Build failures, script crashes ("Show Problems") | `Editor/EditorNotifications.h`, `UI/Notifications.h` | Manual/Scripting L66, L183 | 0.3.0 |
| Scene view (viewport) | Editor camera (orbit Alt+LMB, pan MMB, fly RMB+WASD/QE, F frame), gizmos, snap (toolbar, Ctrl inverts), chips: Game camera (F8), Game UI, 2D, Cells, Camera chip (rest pose / first frame), quality chip, preview lighting, debug views | `Panels/ViewportPanel`, `Panels/ViewportToolbar`, `Editor/EditorViewport.h`, `Editor/EditorCamera.h`, `Editor/ViewportRenderer.h` | Manual/GameView "The Scene view and the Game view" L7; DG "Viewport panel" L3568, "View commands" L3610 | 0.3.0; chips over waves |
| Game view | Primary camera + HUD without overlays; resolution menu (Free, 16:9, 16:10, 4:3, 21:9, 1920x1080, 1280x720, custom, Game's request); notice when no primary camera; UI over black for a camera-less canvas scene | `Panels/GameViewPanel`, `Editor/EditorGameWindow.h` | Manual/GameView L7-35 | 0.4.0 |
| Hierarchy | Tree with multi-select, drag-drop parenting, rename, filters/search (`l:Props`, `cell:3,-1`), "+" menu presets (Empty; Cube, Sphere, Plane, Cylinder, Capsule, Cone, Torus *with matching colliders* or "Mesh only"; Camera; Directional/Point/Spot/Sky Light; Post Process; 3D Text; Audio Source; UI presets) | `Panels/SceneHierarchyPanel.cpp` (`GetMeshPresets` L72, `GetPresets` L101, `CreatePreset` L129 which runs `entity.create`), `Editor/HierarchyView.h`, `Editor/GameUIPresets.h` | Manual/GameUI "Make a menu" L9; DG "Hierarchy, Content Browser and thumbnails" L3260 | 0.3.0; colliders on presets 0.4.0 |
| Inspector | Edits every selected entity at once; Add Component by category; scene settings when nothing is selected (Sky section: Add Procedural Sky, Add Height Fog, Extract Sun, Bake Reflection Probes); prefab bar; inactive properties greyed with reason; "requires" notices | `Panels/InspectorPanel`, `UI/ComponentDrawers`, `UI/PropertyWidgets` | DG "Inspectors" L3282; Manual/Lighting "The sky" L72 | 0.3.0 |
| Asset tab | Selected asset: import settings, material editor, audio waveform and playback, animation controller tables, world layers, Cook button | `Panels/AssetInspectorPanel`, `UI/MaterialEditor`, `UI/AnimationAssetViews`, `Editor/AudioPreview` | DG "Materials" L3692, "Animation commands" L3703 | 0.3.0 |
| Content Browser | Folder tree, grid/list, thumbnails, filters, drag-drop, New > (World, Script...), Scripts root listing source files with the classes they register | `Panels/ContentBrowserPanel`, `Editor/AssetBrowserView`, `UI/ScriptBrowser`, `Editor/ThumbnailCache` | Manual/Scripting "Create a script" L9 (Scripts root); Arch "Content Browser" (Editor section) | 0.3.0; Scripts root later |
| Console, Problems | Log with clickable file:line; Problems lists build diagnostics and script crashes with stack, double-click opens the line | `Panels/ConsolePanel`, `Panels/ProblemsPanel` | Manual/Scripting "When the build fails" L66, "When a script crashes" L183 | 0.3.0 |
| Activity panel | Every command with who ran it (person, agent, script); exports a session as a replayable command script | `Panels/ActivityPanel`, `Editor/CommandJournal.h` | Arch "Activity journal", "Replays" (Editor section); skill make-a-game §7 L404 | 0.3.0 |
| Streaming, Performance panels | Budgets, loads, uploads, world cell map, physics; per-stage CPU/GPU frame timings with pause | `Panels/StreamingPanel`, `Panels/PerformancePanel`, `UI/CellMap` | Manual/Worlds "The cell map" L45 | 0.3.0; cell map 0.4.0 |
| Undo/redo for everything | One undo step per successful command; project settings undoable; asset deletes to trash restored by undo | `Editor/UndoStack.h`, `Editor/SceneEdit.h` | DG "Undo" L2972 | 0.3.0 |
| Autosave and crash recovery | Unsaved changes journaled a few seconds after edits; File > Recover Unsaved Changes; `scene.recoveryStatus`, `scene.recover` | `Editor/SceneRecovery.h`, `UI/RecoveryDialog` | DG "Autosave and recovery" L2948 | 0.3.0 |
| Background saves | Scene snapshot written off the main thread; quit waits | `Editor/DocumentSaver.h` | DG "No silent data loss" L2911 | 0.4.0 |
| Placement and drop ghost | Drag a prefab/model/mesh into the Scene view: box ghost resting on the surface under the pointer with label ("Crate on 'Ground'"), Escape cancels, Snap; material dropped on a mesh tints it; End drops selection to ground | `Editor/EditorPlacement.h`, `Editor/PlacementPreview.h`, `Editor/SceneRaycast.h`; `asset.place`, `scene.raycast`, `entity.dropToGround` | Manual/Prefabs "Place instances" L15; DG "Placing content" L3525 | drop-to-ground 0.3.0; ghost, `asset.place` wave 8 |
| Preferences | External Editor (detected VS Code/Visual Studio/CLion; `{file}` `{line}` `{column}` `{directory}` placeholders; no shell; `STRATA_EXTERNAL_EDITOR` override), Interface scale, Frame Rate (idle after, idle rates, active cap) | `Editor/EditorPreferences.h`, `Editor/ExternalEditor.h`, `Editor/EditorFrameRate.h`, `UI/PreferencesDialog` | Manual/Settings "Preferences" L132; Manual/Scripting "Your code editor" L74 | 0.6.0; frame rate wave 8 |

### 1.4 Scenes, entities and components (the maker's view)

| Feature | What it is | Where it lives | Documented | Release |
| --- | --- | --- | --- | --- |
| Registered components (40) | Scene: ID, Name, Transform, Relationship, Tag, Inactive, PrefabInstance, Camera; Renderer: MeshRenderer, Text, DirectionalLight, PointLight, SpotLight, SkyLight, PostProcess, HeightFog, ReflectionProbe; Physics: RigidBody, BoxCollider, SphereCollider, CapsuleCollider, MeshCollider, CharacterController; Audio: AudioSource, AudioListener; Animation: Animator, Skin, AttachToJoint; Scripting: Script; GameUI: UICanvas, UIRect, UIImage, UIText, UISelectable, UIButton, UIToggle, UISlider, UILayout, UIInputField, UIMask; World: World, StreamingSource | `ComponentRegistry::Register<...>` in `Strata/src/Strata/{Scene/ComponentRegistration.cpp, Renderer/RendererComponents.cpp, Physics/PhysicsComponents.cpp, Audio/AudioComponents.cpp, Animation/AnimationComponents.cpp, Scripting/ScriptingComponents.cpp, GameUI/GameUIComponents.cpp, World/WorldRegistration.cpp}` | skill add-component §1-2; `component.list` | various |
| Reflection-driven editing | Every property has range, tooltip with units, category; the Inspector, files, commands and scripts all go through it | `Strata/Reflection/PropertyOptions.h`, `ComponentRegistry` | skill add-component §2 | 0.3.0 |
| Built-in meshes | `Builtin/Cube`, `Sphere`, `Plane`, `Quad`, `Cylinder`, `Capsule`, `Cone`, `Torus`; `Builtin/DefaultMaterial` | `Strata/Asset/BuiltinAssets.h`, `MeshFactory` | skill make-a-game §3 L81 | 0.3.0 |
| Scene settings | Fixed timestep, max steps per frame, `MaxEntitiesInstantiatedPerFrame` (5000), physics capacity; greyed when the project's FixedRate rules | `Scene`, `scene.setSettings` | Manual/Settings "Timing" L53 | 0.3.0 |
| Conventions a maker must know | -Z forward for cameras/lights/`GetForward()`, glTF models face +Z, Euler degrees `[pitch, yaw, roll]` in commands but radians in `SetEulerAngles`, meters, y up | skill make-a-game §3 L98, §5 L291; scripting cheat sheet L118 | — | — |

### 1.5 Assets: importing models, textures, sounds, fonts

| Feature | What it is | Where it lives | Documented | Release |
| --- | --- | --- | --- | --- |
| Drop-to-import, `asset.import` | Drop files on the window or `asset.import {file|directories, directory}`; background import; a `.gltf` brings its `.bin` and images | `Editor/EditorAssetCommands.cpp`, `EditorAssetManager` (see area: asset pipeline) | README "Making a game"; skill make-a-game §3 L75 | 0.3.0 |
| Formats | glTF 2.0 (meshopt, skins, animations, KHR clearcoat/transmission/volume/ior), PNG/JPEG/TGA/BMP/PSD/GIF/HDR, WAV/MP3/FLAC/Ogg, TrueType | importers in `Strata/src/Strata/AssetPipeline/` | README "Features"; 0.3.0 notes L34 | 0.3.0; KHR materials 0.6.0 |
| Asset types | Scene `.stscene`, Prefab `.stprefab`, Model, Mesh, Material `.stmat`, Texture, AudioClip, Font, Skeleton, AnimationClip, AnimationController `.stanimator`, World `.stworld`, ColorLookup `.cube` | `Strata/src/Strata/Asset/AssetTypes.h` L14-31 | — | ColorLookup 0.7.0 |
| `.meta` sidecars, handles | Each asset file's stable UUID; never edit by hand | `EditorAssetManager` | AGENTS "Asset pipeline" | 0.3.0 |
| Import settings a maker uses | Model `Scale` (centimeter models: 0.01), `BaseColorFactorsAreSRGB` (Kenney exporter habit), texture usage by name tokens (`_normal`, `_rough`), `RemoveSun` for HDR skies; material warnings with a `fix` | `asset.setImportSettings`, `asset.info` (`bounds` in meters) | skill make-a-game §3 L92-101; OpenWorld README "an import setting"; 0.7.0 "One more import" | Scale 0.4.0 to instances; RemoveSun 0.6.0; sRGB factors 0.7.0 |
| Asset deletes and references | `asset.delete` to project trash, refused while used (`asset.findReferences`), undo restores | `Editor/AssetFileAction.h`, `AssetReferences.h` | DG "Asset files are never lost" L2840 | 0.3.0 |
| Downloaded assets policy | CC0 or CC-BY 4.0 only; untrusted downloads in their own directory; `CREDITS.md` table; `ThirdPartyNotices.md` | `StrataTests/src/Samples/SampleContent*` (`Samples.Content`) | skill make-a-game "Downloaded assets" L103; DG "Samples" L6451 | 0.5.0 |

### 1.6 Materials

| Feature | What it is | Where it lives | Documented | Release |
| --- | --- | --- | --- | --- |
| Material documents | `material.create {path, properties}`, `material.get`, `material.set`; properties BaseColor, Metallic, Roughness, Emissive*, AlphaMode (Opaque/Mask/Blend), AlphaCutoff, DoubleSided, Unlit, maps, UVTiling/Offset, Clearcoat(+Roughness), Transmission, IOR, Thickness, AttenuationColor/Distance | `Strata/src/Strata/Renderer/Material.h`, `UI/MaterialEditor`, `Editor/AssetEdit.h` (see area: rendering materials) | skill make-a-game §3 L66-74; DG "Materials" L3692 | 0.3.0; clear coat and glass 0.6.0 |
| Material guidance for makers | Water/wet 1.33 IOR roughness 0.02-0.06; glass 1.5; painted scans roughness 0.15-0.45; base colors above 0.85 look plastic | skill make-a-game §3, §5 L300 | — | 0.7.0 |

### 1.7 Prefabs

| Feature | What it is | Where it lives | Documented | Release |
| --- | --- | --- | --- | --- |
| Prefab create/instantiate | Drag entities to the Content Browser or Create Prefab; drop instances; `prefab.instantiate {prefab, instances: [...]}` for many | `Editor/EditorPrefabCommands.cpp`, `Editor/PrefabSync.h`, `Scene/PrefabInstances.h` | Manual/Prefabs L1-31 | 0.3.0; `instances` 0.4.0 |
| Overrides, apply, revert, unpack, outdated | Per-property overrides marked bold with an accent bar; Apply to Prefab / Revert per property, component or instance; outdated instances; models offer Revert only | same | Manual/Prefabs "Overrides" L33, "Change the prefab" L47, "Revert and unpack" L59; DG "Prefab instances" L2854 | 0.4.0 |
| Models as prefabs | Imported glTF places as a linked hierarchy | `AssetType::Model` | Manual/Prefabs L1-7 | 0.3.0 |

### 1.8 Lighting, cameras, the camera's image, graphics quality (maker's controls)

(Details of how each is rendered: see area: rendering. What the maker turns on and off:)

| Feature | Maker's control | Documented | Release |
| --- | --- | --- | --- |
| Light units | DirectionalLight lux, Point/Spot candela, sky and emission nits; Source Radius for highlights | Manual/Lighting "Lights and their units" L8 | units 0.6.0; source radius wave 8 |
| Sky sources | Procedural, Environment Map (+Rotation, Extract Sun, Remove Sun), Atmosphere (Density, Haze, Ground Albedo, Aerial Perspective + Scale) | Manual/Lighting "The sky" L72 | procedural 0.3.0; atmosphere 0.6.0; aerial perspective 0.7.0 |
| Sky presets | `lighting.applySkyPreset {preset: Clear|Hazy|Overcast|GoldenHour, sunAzimuth, sunElevation}` | Manual/Lighting "Sun and sky presets" L279 | 0.7.0 |
| Height fog | Add Height Fog; Density, Base Height, Falloff, Color From Sky | Manual/Lighting "Height fog" L106 | 0.6.0 |
| Shadows | Sun cascades, Cascade Blend, Shadow Distance, Shadow Softness; point/spot Cast Shadows (16 in view) | Manual/Lighting "Shadows" L115 | 0.3.0; local shadows 0.6.0; real sun 0.7.0 |
| Reflection probes | ReflectionProbe box, Bake (`lighting.bakeProbes`), Box Projection, time-of-day probe sets | Manual/Lighting "Reflection probes" L189, "Times of day with baked probes" L219 | 0.6.0 |
| SSR | Post Process Screen Space Reflections | Manual/Lighting L229 | 0.6.0 |
| Ambient occlusion, GI (experimental) | AO radius, multi-bounce; Post Process Global Illumination (High/Ultra only) | Manual/Lighting L306, L320 | AO 0.3.0; GI wave 8 |
| Debug views | lighting, AO, indirect, luminance (EV), albedo, shadows, motion, gi | Manual/Lighting "Debug views" L361 | 0.7.0 |
| Exposure and camera image | Post Process: Exposure, Auto Exposure (Min/Max EV, metering, speeds, key), tone curve (Filmic default, ACES), color, LUTs, bloom, vignette, motion blur, depth of field (Camera lens), grain, chromatic aberration, lens flares | Manual/Camera L1-200 (Recipes L185) | 0.3.0 basics; most 0.7.0 |
| Anti-aliasing | FXAA, TAA (Sharp/Original/Custom), Morphological | Manual/AntiAliasing L1-180 | FXAA 0.3.0; TAA 0.6.0; Morphological 0.7.0 |
| Graphics Quality | Project page with Low/Medium/High/Ultra/Custom; memory and GPU cost per row; Players' choices; Scene-view quality chip; `--quality` | Manual/Graphics L1-125; Manual/Settings L81 | 0.7.0 |
| Preview lighting | A scene with no light shows preview lighting in editor captures (`previewLighting: true`) but the game is unlit | skill make-a-game §5 L308; tests `EditorLauncherTests.cpp` L602, L619 | 0.3.0 |

### 1.9 Scripts (C++ game logic)

| Feature | What it is | Where it lives | Documented | Release |
| --- | --- | --- | --- | --- |
| Script module | Every `.cpp/.h` under `Scripts/` compiled into one shared library through the `StrataScriptCore` CMake package (`strata_add_script_module`) | `StrataScriptCore/CMake/StrataScriptModule.cmake`, `StrataScriptCoreConfig.cmake`; generated `Scripts/CMakeLists.txt` (`ScriptProject.cpp` L207-222) | Manual/Scripting L1-8; skill scripting "Building outside the editor" L738 | 0.3.0 |
| Script class and fields | `class X : public Script`, `ST_SCRIPT_CLASS(X) { ST_SCRIPT_FIELD(...); }`; field types bool, int32_t, float, vec2/3/4, quat, string, Entity, AssetHandle | `StrataScriptCore/Include/StrataScript/Script.h` (class L70-110, macros L842-865) | Manual/Scripting "Create a script" L9; skill scripting "A script class" L20 | 0.3.0 |
| Lifecycle callbacks (15) | OnCreate, OnUpdate, OnFixedUpdate, OnLateUpdate, OnDestroy, OnReload, OnCollisionEnter/Exit, OnTriggerEnter/Exit, OnAnimationEvent, OnUIClick, OnUIValueChanged, OnUIFocusChanged, OnUISubmit; only overridden ones are called (`CallbackFlag`, `Overrides*` detection) | `Script.h` L30-97, L348-400 | skill scripting "Lifecycle" L79 | 0.3.0; UI callbacks 0.4.0 |
| SDK namespaces | `Entity`, `TransformComponent`, `Scene`, `Assets`, `Input` (keys, mouse, gamepads, cursor, actions, binding capture), `Time`, `Physics`, `RigidBody`, `Collision`, `CharacterController`, `AudioSource`, `Audio`, `Animator`, `UIElement`/`UI`, `Game` (quit, scenes, window, saves), `Graphics`, `World`, `Log`, `Random`, `Timer`, `KeyRepeat`, `Motion` | headers `StrataScriptCore/Include/StrataScript/{Entity,Scene,Input,Time,Physics,CharacterController,Audio,Animator,UI,Game,Graphics,World,Log,Gameplay,Value}.h` (5,255 lines total) | skill scripting "API cheat sheet" L103, "Gameplay API" L165-646 | 0.3.0; actions 0.6.0; Graphics 0.7.0; drawn poses wave 8 |
| Generic component access | `GetProperty<T>/SetProperty(component, property, value)` for every registered component by its Inspector names | `Entity.h` L355-396 | skill scripting L106 | 0.3.0 |
| New Script | Scripts > New Script... (class-name dialog with validation), `script.create {class, fields, template, path}`; validation refuses SDK names and existing types | `Editor/ScriptProject.h` (`ValidateNewScriptClass`, `MakeScriptSource`), `UI/ScriptDialogs` | Manual/Scripting L9-52 | 0.3.0 |
| Build, Play builds first | Ctrl+B / `script.build` (CMake configure on first run and after file adds/removes); Play builds changed sources first ("Building to play"); `play.start {build:false}` | `Editor/ScriptBuild.h/.cpp`, `EditorContext::StartPlayBuild` (`EditorContext.cpp` L2347) | Manual/Scripting "Attach it and play" L55; skill scripting L678 | 0.3.0 |
| Attach and fields | Add Component > Script, pick class; fields per entity with reset; `script.add`, `script.setField`, `script.get` (live values while playing) | `Editor/ScriptEdit.h`, `EditorScriptCommands.cpp` | skill scripting L696-704 | 0.3.0 |
| Hot reload | Rebuild while playing: instances recreated, fields kept by name and type, `OnReload` instead of `OnCreate`; module runs from a private copy | `ScriptEngine` (see area: scripting) | Manual/Scripting "Hot reload" L177 | 0.3.0 |
| Crash containment | Access violations, div by zero, stack overflow, escaped exceptions (Windows also abort) disable the module and stop play; report with file:line from PDB on Windows, function+offset elsewhere; exceptions disable one instance | `ScriptModule` CrashGuard (see area: scripting) | Manual/Scripting "When a script crashes" L183; skill scripting "Rules" L648 | 0.3.0 |
| Code editor and IDE | External editor; `Scripts/CMakePresets.json` "strata" preset for VS/VS Code/clangd; IDE builds hot-reload too | `Editor/ExternalEditor.h`, `ScriptBuild` presets | Manual/Scripting "Your code editor" L74, "IntelliSense" L94 | 0.3.0 |
| Debugger attach | Attach to StrataEditor; PDB in `.strata/Scripts/Bin` | — | Manual/Scripting L200 | 0.3.0 |
| Long-path fallback | MSBuild path > ~133 characters builds in `<user data>/Strata/Builds/<hash>` | `ScriptBuild` | Manual/Scripting L208 | 0.6.0 or 0.7.0 (not stated) |
| Script ABI | C ABI, version 1; 165 host functions at this commit (155 at 0.6.0, 162 at 0.7.0), appended only | `StrataScriptCore/Include/StrataScript/ScriptABI.h` (host table L312-756, `ST_SCRIPT_ABI_VERSION` L33), `Host.h` | AGENTS "Scripting"; 0.6.0/0.7.0 "Upgrading" | 0.3.0 |

### 1.10 Input and input actions

| Feature | What it is | Where it lives | Documented | Release |
| --- | --- | --- | --- | --- |
| Device input | Keys, mouse buttons/position/delta/scroll, typed text, gamepads 0-3 (sticks with round dead zone, triggers, Xbox layout), cursor modes Normal/Hidden/Locked; only while the Game view has focus; Shift+F1 frees cursor | `Input.h`, `Strata/src/Strata/Input/` | skill scripting L127-136, "Gamepads and the cursor" L435; Manual/GameView "Input and the mouse" L36 | 0.3.0 |
| Input actions | Project's maps (Gameplay, Vehicle...) of Button/Axis/Vector2 actions with bindings (`Key/Space`, `Gamepad/LeftStick`, `Gamepad/LeftX+`, `1D:`, `2D:` composites), dead zones; reserved map `UI` (Submit, Cancel, Up, Down, Left, Right) | `Strata/src/Strata/Input/InputActionSet.h` (grammar L61-96), `InputActions.cpp` (`ApplyDeadZone` L443, evaluation L452-560); page `UI/InputActionsPage`, `UI/BindingCapture` | Manual/Settings "Input Actions" L67; Manual/Scripting "Input actions and rebinding" L109; DG "Input actions" L1442 | 0.6.0 |
| Player rebinding | `GetActionBindings`, `SetActionBindings`, `ResetActionBindings`, `SaveBindings`, `BeginBindingCapture`/`PollBindingCapture`/`CancelBindingCapture`; saved per player; "In play" and Reset Player Bindings in the page | `InputActions`, `inputActions.resetPlayerBindings` | Manual/Scripting L119-134 | 0.6.0 |
| KeyRepeat | SDK helper firing on press, after a delay, then at an interval | `Gameplay.h` L181-219 | skill scripting L550 | 0.3.0 |

### 1.11 Physics and characters (maker's view)

| Feature | What it is | Where documented | Release |
| --- | --- | --- | --- |
| Bodies and colliders | RigidBody Static/Dynamic/Kinematic, mass, friction, restitution, damping, GravityScale, LockRotation, ContinuousCollision, IsTrigger, Layer; Box/Sphere/Capsule/Mesh (convex or triangle on static) colliders; a collider without a RigidBody is static | skill scripting "Physics" L167; templates' ground; presets with colliders | Jolt 0.3.0, box3d 0.5.0 |
| Script API | velocities, forces, impulses, torque, Teleport; Raycast/RaycastAll/OverlapSphere/OverlapBox with layer masks; contacts callbacks | skill scripting L173-226, "Contacts" L252 | 0.3.0 |
| Collision layers | 32 project layers and matrix; `Physics::SetLayersCollide` per scene; `project.setCollisionLayers` | Manual/Settings "Collision Layers" L31 | per scene 0.3.0; project 0.6.0 |
| Simulation tuning | Contact recycle distance, sleep threshold, stiffness, damping, push speed; live while playing | Manual/Settings "Simulation" L37 | 0.7.0 |
| Timing | FixedRate (Scene/30/60/120/240), Interpolation (draw between last two steps) | Manual/Settings "Timing" L53; Manual/Scripting "Following moving things" L157 | wave 8 |
| Character controller | Capsule (Height, Radius, StepHeight, MaxSlopeDegrees, PushStrength, GravityScale, Layer); Move/Jump/Teleport/IsGrounded/GroundState/Velocity | skill scripting "Character controllers" L228 | 0.3.0; Strata's own on box3d mover 0.5.0 |
| Time dilation | When steps cannot keep up the game slows instead of spiralling | DG "Play mode and scene switches" L3091; `Scene.cpp` L2269-2310 | 0.3.0 |
| Gotchas | Triggers never see triangle-mesh colliders; overlapping spawns pushed apart at 3 m/s; `Instantiate` with a translation sets scale 1; bounce only above 1 m/s | skill scripting L91, L215-223; 0.5.0 "What changes with box3d" L75 | 0.5.0 |

(Internals: see area: physics.)

### 1.12 Animation (maker's view)

| Feature | What it is | Documented | Release |
| --- | --- | --- | --- |
| Import skinned glTF | Model root becomes Animator playing the first clip; `animation.info` lists clips | skill make-a-game §3 L83 | 0.3.0 |
| Animation controllers `.stanimator` | Parameters (Float, Bool, Trigger), states with clip/loop/speed/events, transitions (AnyState, conditions Greater/Set..., Duration, ExitTime); `animation.createController`, `animation.setController`, `animation.preview`; Asset tab tables | `Samples/ThirdPerson/Assets/Animations/Robot.stanimator`; skill scripting "Animation" L285 | 0.3.0 |
| Script API | SetFloat/SetBool/SetTrigger, Play/CrossFade, GetCurrentState, GetNormalizedTime, GetJointTransform, `OnAnimationEvent` | `Animator.h` | 0.3.0 |
| AttachToJoint, root motion, culling mode | Object in a hand; ApplyRootMotion with CharacterController; WhenVisible | skill scripting L314-320 | 0.3.0 |
| Rest pose while editing / first frame | Camera chip | Manual/GameView L23 | 0.4.0 |
| Not imported | Morph targets (ThirdPerson README: face stays neutral) | ThirdPerson README | — |

(Internals: see area: animation. Wave 8 tranche 2 "animation-graph" is planned, not in this commit's user docs.)

### 1.13 Audio (maker's view)

`AudioSource` (clip, volume, pitch, loop, 3D) + `AudioListener` (or the camera); scripts `AudioSource::Play/Pause/Stop/Seek`,
`Audio::PlayOneShot`, `PlayOneShotAt`, `SetMasterVolume`; clips must be requested early (dropped if not loaded within
0.25 s); Asset tab waveform preview; `audio.state` command. Files: `StrataScriptCore/Include/StrataScript/Audio.h`,
`Strata/src/Strata/Audio/`. Docs: skill scripting "Audio" L272; AGENTS "Audio". Release 0.3.0. (See area: audio.)

### 1.14 Game UI and menus (maker's view)

Canvases (Screen/World space, Scale With Screen + reference resolution, Sort Order, Receives Input, First Selected), rects
(anchors, pivots, presets), Image (color, texture, rounded, border, sliced, filled), Text (font, size, wrap, overflow,
outline), Selectable states, Button, Toggle (groups), Slider, Input Field, Layout groups, Mask; Hierarchy "+ > UI"
presets; viewport Game UI and 2D chips; script callbacks and `GetUI()` setters; keyboard/gamepad navigation through the
`UI` action map; pause menus at time scale 0; main-menu scene with no camera; `ui.create`, `ui.layout`, `ui.hitTest`,
`input.click`. Files: `Strata/src/Strata/GameUI/`, `Editor/GameUIPresets.h`, `Editor/UIRectEdit.h`,
`Panels/CanvasModeView`, `UI/UIRectDrawer.cpp`, SDK `UI.h`. Docs: Manual/GameUI L1-130; skill scripting "Game UI" L322.
Release 0.4.0 (masks and world space later in 0.4.x/0.5; Manual does not date them). (See area: gameui.)

### 1.15 Game flow: scenes, loading, saves, window, graphics options

| Feature | What it is | Where it lives | Documented | Release |
| --- | --- | --- | --- | --- |
| Scene switch | `Game::LoadScene(handle or path)`, `ReloadScene`, `GetSceneLoadProgress`; background load, swap between frames; scene named in a field is an asset reference (pruned exports keep it) | SDK `Game.h`; `Scene::RequestSceneLoad`; `SceneLoader` | skill scripting "Game flow" L380; DG "Play mode and scene switches" L3091 | 0.3.0 |
| Quit | `Game::Quit(code)`: exported game exits with code; editor stops play | `Scene::RequestQuit`, `EditorContext::HandleRuntimeRequests` (`EditorContext.cpp` L1432) | same | 0.3.0 |
| Additive sub-scenes, many instances | `Scene::LoadAdditive`, `SubScene::Unload`, `Assets::GetLoadProgress`, `Scene::InstantiateMany` | SDK `Scene.h` | skill scripting "Streaming" L394 | 0.3.0 |
| Module state across scene loads | Namespace-scope state in the module survives `LoadScene` (attract mode, settings cache) | `Samples/ThirdPerson/Scripts/ThirdPerson.h` L1-6 | ThirdPerson README | 0.5.0 sample |
| Start scene, loading scene | File > Set as Start Scene / `project.setStartScene`; `project.setExportSettings {loadingScene}` plays while start scene loads | `Project`, `GameManifest::LoadingScene` | Manual/Settings "Game" L18; skill make-a-game §8 L474 | 0.3.0 |
| Save files | `Game::WriteSaveFile`, `ReadSaveText`, `ListSaveFiles`, `DeleteSaveFile`; names 1-64 safe ASCII; editor `<project>/.strata/Saves`, game `<user data>/<Game>/Saves`; synchronous (save at quiet moments) | SDK `Game.h`; engine service `IGameSaves` | skill scripting "The window and save files" L517 | 0.3.0 |
| Window | `Game::SetWindowMode` (Windowed/Fullscreen/Borderless), `SetResolution`, `SetVSync`, `GetWindowSize`; editor records requests (Game view "Game's request") | SDK `Game.h`; `Runtime/GameWindowService.h`; `Editor/EditorGameWindow.h` | same; Manual/GameView "Resolution" L28 | 0.3.0 |
| Graphics options for players | `Graphics::SetPreset/Set/Get/Reset/Save/Options/FindOption`; `GraphicsOptions.json`; `graphics.resetPlayerOptions` | SDK `Graphics.h`; `Runtime/GameGraphicsService.h` | Manual/Graphics "Players' options" L95; Manual/Scripting "Graphics options" L136 | 0.7.0 |
| Game identity | Title, Version, Company, Copyright, Icon; Windows PE stamping, macOS Dock icon, Linux `.desktop` | `Project/GameInfo.h`, `Editor/GameIcon.h`, `Editor/PEResources.h`, `Editor/DesktopEntry.h`; `project.setGameInfo` | Manual/Settings "Game" L18; DG "Exporting games" L3009 | 0.6.0 |

### 1.16 Worlds (maker's view)

New > World, layers (cell size, streaming distance, Load Before Start), edit layer strip in Hierarchy, cell crossing
moves entity, Cells chip, cell map (load and pin), Save writes only changed cells, Cook, Play from loaded cells,
`StreamingSource`, scripts `World::RequestCellsAround/IsLoadedAround/SetLayerEnabled/IsLayerEnabled`; limits (20 km,
no far LODs, roaming bodies belong in persistent scene). Files: `Strata/src/Strata/World/`, `Editor/EditorWorld.h`,
`Editor/WorldCook.h`, `Editor/WorldCellIO.h`, `Editor/CellBoundsOverlay.h`, `UI/CellMap`, SDK `World.h`; commands
`world.create/edit/info/status/loadCells/moveEntities/setLayers/cook`. Docs: Manual/Worlds L1-100; skill make-a-game §5
L360. Release 0.4.0. (See area: worlds-runtime.)

### 1.17 Playing and testing

| Feature | What it is | Where it lives | Documented | Release |
| --- | --- | --- | --- | --- |
| Play / Simulate / Stop / Pause / Step | Play runs a *copy* of the edited scene (stop restores), Simulate runs physics only, Step one fixed update; toolbar takes the play color | `EditorContext::Play`/`StartRuntime`/`Stop` (`EditorContext.cpp` L1340-1430); `Editor/Commands/PlayCommands.cpp` | Manual/GameView L1-46 | 0.3.0 |
| Edits while playing | Scene view picks and moves the running copy; project settings changes apply live and persist | `EditorContext` | DG "Edits while playing and value ranges" L3451; Manual/Settings L123 | 0.3.0 |
| Simulated input | `input.key/mouseButton/mouseMove/scroll/click/type/gamepadButton/gamepadAxis/action/releaseAll/state`; durations in fixed steps | `Editor/SimulatedInput.h`, `EditorInputCommands.cpp` | skill make-a-game §6 L369; Manual/GameView "Testing with an agent" L47 | 0.3.0; fixed-step durations 0.4.0; `input.action` 0.6.0 |
| Deterministic sequences | `input.sequence {steps, events, observe}`; `play.step` answers after steps ran; `play.start {paused}` | `Editor/InputSequence.h` | skill make-a-game §6 L386-401 | 0.4.0 |
| Viewport capture | `viewport.capture {camera, width, height, position/target, debugView, quality, live, atFixedStep, frames, path}`; waits for assets; `pendingAssets` | `EditorViewportCommands.cpp` | skill make-a-game §6 L381 | 0.3.0; options 0.6.0/0.7.0 |
| Command scripts and expectations | `StrataEditor --commands f.json --quit-after-commands`; steps with `expect` (equals/min/max), `until {steps|seconds}`, `bind` + `$ref`; exit code 1 on failure | `Editor/EditorCommandRunner.h` (`EditorCommandScript`) | skill make-a-game §7 L404-449; DG "Deferred commands and command scripts" L3176 | 0.3.0; `until` 0.5.0 |
| Session replay | `editor.activity.export {path, since}` writes the session as a command script with bindings | `Editor/CommandJournal.h` | skill make-a-game §7 L438 | 0.3.0 |
| Sample regressions | One command script per sample, run by CTest through `SampleProject.cmake` (copy, play, export full and pruned, run headless, fail on unlisted warnings) | `StrataTests/Editor/{Tetris,ThirdPerson,OpenWorld,PhysicsPlayground,Showcase}Commands.json.in`, `StrataTests/Editor/SampleProject.cmake` L1-20 | DG "Samples" L6451 | 0.3.0 Tetris; others 0.5.0; Showcase wave 8 |
| Observability | `editor.status` (`errors`, `saving`, sections), `log.read`, `script.status`, `component.get`, `entity.get {world}`, `physics.stats`, `animation.info {entity}` | various command files | skill make-a-game §1 L37 | 0.3.0+ |

### 1.18 Exporting and the runtime

| Feature | What it is | Where it lives | Documented | Release |
| --- | --- | --- | --- | --- |
| Export | File > Export Game... / `project.export {directory, prune}`: background, states WaitingForImports, CookingWorlds, Packing, Copying, Succeeded/Failed/Cancelled; writes `<Game>[.exe]` (renamed runtime), `.stgame` manifest (v5), `.stpak` pack ordered by first use, script module (+PDB outside Dist), `<Game>.png`, `.desktop` on Linux; `project.exportStatus`, `project.cancelExport` | `StrataEditor/src/Editor/GameExport.h` (options L21-41, result L42-55, states L56-66, class comment L67-78), `GameExport.cpp`; `UI/ExportDialog` | DG "Exporting games" L3009; Arch "Export and the runtime" L4072; skill make-a-game §8 L451 | 0.3.0; identity 0.6.0 |
| Pruned export, alwaysInclude | Only what scenes reference, plus `Export.AlwaysInclude` paths and folders (assets scripts find by path) | `EditorAssetManager::PlanAssetPack`; Project Settings > Export | Manual/Settings "Export" L28; skill make-a-game §8 L472 | 0.3.0 |
| Export refusals | Unsaved/unbuilt/changed module, output inside project, build running | `GameExport::Start` | skill scripting L725; EditorExportTests L723 | 0.3.0 |
| Runtime options | `--game`, `--headless` (60 fps, no GPU), `--windowed`, `--resolution WxH`, `--frames N`, `--seconds N`, `--screenshot f.png`, `--asset-budget-mb`, `--perf-log f.csv`, `--save-directory`, `--quality`, `--help`; exit code 1 cannot start, 2 scripts crashed headless | `StrataRuntime/src/RuntimeApplication.cpp` (`c_Arguments` L339-353, exit codes L35) | README "Making a game"; PackageReadme L82 | 0.3.0; `--seconds`, `--quality` 0.7.0 |
| GameRuntime | Opens pack, loads module (no hot reload), plays loading scene while start scene loads, disables scripts after a crash, project settings as `IProjectSettings`, graphics as `IGameGraphics` | `Strata/src/Strata/Runtime/GameRuntime.h` L62-84 | Arch "Export and the runtime" L4072 | 0.3.0 |

### 1.19 AI agents as game makers

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| Commands are the API | 153 registered commands in 26 groups (animation 4, asset 14, audio 1, camera 3, component 5, edit 3, editor 12, entity 11, graphics 1, input 12, inputActions 3, lighting 3, log 1, material 3, physics 2, play 6, prefab 7, preferences 3, project 18, scene 13, script 13, selection 2, ui 3, viewport 3, world 8) each with JSON Schema and description | `registry.Register({...})` across `StrataEditor/src/Editor/*Commands.cpp`, `Editor/Commands/*.cpp`, `EditorLayer.cpp` | DG "Command conventions" L2881; skill strata-editor-automation (84 KB) | 0.3.0 (124 at 0.4.0) |
| StrataCLI and MCP | `StrataCLI launch --headless/--no-gpu`, `list`, `call cmd @p.json`; `StrataCLI mcp` toolsets (`core` <= 32 tools; `scene`, `ui`, `world`, `settings`...), `strata_describe`, `strata_toolsets`, `strata_call` | `StrataCLI/` | skill make-a-game §1 L17-40; PackageReadme "Connect an AI agent" L117 | 0.3.0; toolsets 0.4.0 |
| Skills shipped | `Skills/` in archive: editor automation, scripting, make-a-game | `.claude/skills/` | PackageReadme L127 | 0.3.0 |

### 1.20 The five samples

| Sample | Teaches | Scenes / key assets | Scripts (lines) | Regression |
| --- | --- | --- | --- | --- |
| **Tetris** (0.3.0; HUD as UI canvas 0.4.0) | Pure scripting: rules in a plain C++ class tested without the engine, a `Script` that feeds input/time and draws; entities created once and shown/hidden; KeyRepeat; seeded 7-bag; HUD texts; one-shot sounds generated as WAV; Escape quits | `Assets/Scenes/Main.stscene`, `Materials/` (piece colors), `Sounds/` | `TetrisGame.h` (108), `TetrisGame.cpp`, `TetrisBoard.cpp` (~420); 829 total | `TetrisCommands.json.in` (44 lines): exact score 209 after a 26-step `input.sequence`, game over, restart, `ui.layout` at two resolutions |
| **Third-Person Adventure "Sky Islands"** (0.5.0; input actions, probes, extracted sun 0.6.0; graphics row 0.7.0) | Character controller with camera-relative movement, coyote time, checkpoints, respawn; follow camera with orbit, zoom, raycast arm, `GetDrawnPosition`; skinned robot + controller (Idle/Walk/Run/Jump/Wave/Dance, Footstep events); triggers as prefabs (Coin, JumpPad, Goal); pushable crate; course of 35 Platformer Kit blocks with mesh colliders on a 4 m grid; three scenes (MainMenu, Course, Loading); main menu, settings (volume, sensitivity, invert, fullscreen, vsync, Graphics row), credits in a UIMask, pause at time scale 0; save files; attract mode in module state; AttachToJoint flag; HDR sky with extracted sun; lantern point-light shadows; four baked probes | `Animations/Robot.stanimator`, `Prefabs/Coin`, `JumpPad`, `Prefabs/Course/`, `Scenes/{MainMenu,Course,Loading}.stscene`, `UI/` (Kenney UI Pack), `Environment/*.hdr` | `ThirdPersonPlayer.cpp` (263), `FollowCamera.cpp` (124), `ThirdPerson.cpp/.h`, `MainMenu.cpp`, `SettingsMenu.cpp`, `PauseMenu.cpp`, `CourseState.cpp`, `Coin.cpp`, `JumpPad.cpp`, `Goal.cpp`, `Pushable.cpp`, `Footsteps.cpp`, `MenuRobot.cpp`, `LoadingScreen.cpp`; 1,720 total | `ThirdPersonCommands.json.in` (99 lines) |
| **Physics Playground** (0.5.0; clear coat/glass 0.6.0) | ~600 bodies from prefabs placed with `prefab.instantiate {instances}`; materials by restitution/friction/mass; trigger counting (GoalBasket), launch pad, impact sounds with a token-bucket voice budget; Ghost layer passing through Ball layer; shoot through the cursor (camera FOV ray), grab (velocity toward a point), pour 100 balls with `InstantiateMany`; slow motion toggle; reset by reloading the scene; hot reload keeping fields; AutoDemo in export; fly camera | `Prefabs/`, `Materials/` (ambientCG), `Scenes/Main.stscene`, `Sounds/Impacts/`, `UI/` | `Playground.cpp` (401), `Playground.h`, `Impact.cpp` (87), `FlyCamera.cpp`, `GoalBasket.cpp`, `LaunchPad.cpp`; 734 total | `PhysicsPlaygroundCommands.json.in` (59 lines; paused waits with `until`) |
| **Open World** (0.5.0; atmosphere, fog, shadows 0.6.0; aerial perspective, sRGB factors 0.7.0) | World of three layers in 64 m cells (Vegetation 192 m, Wildlife 128 m, Landmarks 320 m) + persistent scene with 97 terrain tiles (static mesh colliders, Terrain layer); 20,000 props of 26 one-entity prefabs drawn GPU-driven; streaming source on player; teleport with prefetch + raycast wait; foxes with controller in streamed cells; day/night under atmosphere, moon, campfires at dusk; HUD clock, pause with day-length slider; loading scene with progress bar | `Worlds/Island.stworld`, `Worlds/Island/{Vegetation,Wildlife,Landmarks}/`, `Prefabs/Nature/`, `Prefabs/Fox.stprefab`, `Terrain/` | `Explorer.cpp` (348), `DayNight.h/.cpp`, `Wander.cpp`, `IslandHud.cpp`, `LoadingScreen.cpp`; 655 total | `OpenWorldCommands.json.in` (47 lines), `OpenWorldRenderCommands.json` |
| **High Desert Outpost (Showcase)** (wave 8) | The graphics reference scene: scans + generated terrain/props (`Tools/GenerateShowcaseTerrain.py`, `GenerateShowcaseProps.py`), three times of day as stations (`Stations.h`) each with two baked probes switched with a 1 s hold; camera tour over marker entities (`TourPath.h`), first-person walk on rays, flight, photo mode (time, exposure, FOV, focus, f-number, quality, AA from `Graphics::Options()`); flicker of fire/lanterns; loading scene; generated command scripts (materials, tune, prefabs, layout, controls, dress, bake, pictures) | `Assets/Scans/` (12 Poly Haven models), `Textures/` (10 sets), `Generated/{Terrain,Props}/`, `Prefabs/` (Bus, OilTank, FuelTank, Hut, FirePit, Lantern), `Scenes/Outpost.stscene`, `Lighting/Outpost/` | `Outpost.cpp` (372), `Outpost.h` (184), `OutpostTour.cpp`, `OutpostWalk.cpp`, `OutpostPhoto.cpp`, `Flicker.cpp/.h`, `LoadingScreen.cpp`, `Stations.h`, `TourPath.h`; 1,406 total | `ShowcaseCommands.json.in` (66 lines), `ShowcaseRenderCommands.json`; `StrataTools.ShowcaseTerrain/Props` selftests |

Sample rules (all samples): README with feature-to-file table, controls, how it was made, credits; `CREDITS.md`
`| Files | Source | Author | License | Attribution | Changes |`; `Picture.png` 480x270 from `.strata/Thumbnail.png`;
<= 3 screenshots in 3 MB (showcase 6 in 8 MB); 25 MB source assets (showcase 80 MB); game identity with
`Assets/Icon.png`. Checked by `Samples.Content` (`StrataTests/src/Samples/SampleContentTests.cpp` L79-227). DG "Samples"
L6451, "The showcase" L6493.

### How completeness was checked

- Every panel registered in `EditorLayer::RegisterBuiltinPanels` (13) is listed in 1.3.
- Every menu item extracted from `EditorLayer.cpp`/`UI/EditorActions.cpp` (`BeginMenu`/`MenuItem`) is in 1.3.
- Every editor command registered (grep of `Register({ "<group>.<action>"` over `StrataEditor/src`: 154 registrations,
  153 unique names) is counted by group in 1.19 and the ones a maker uses are named in their feature rows.
- Every component registered with `ComponentRegistry::Register<...>` (40, eight files) is in 1.4.
- Every asset type of `AssetType` (13) is in 1.5.
- The five project settings sections with ids (`Input.Actions`, `Scene.CollisionLayers`, `Scene.Timing`,
  `Renderer.Quality`, `Physics.Simulation`) and the project file's own Game/Export fields are in 1.2, 1.10, 1.11, 1.8, 1.15.
- Every SDK header of `StrataScriptCore/Include/StrataScript/` (19) is named in 1.9.
- Every runtime option of `c_Arguments` (12) is in 1.18.
- Every sample's script files are listed in 1.20 with line counts from `wc -l`.
- Every Manual file (10) and the headings of each are cited somewhere.
Not checked line by line: each component's individual properties (belong to the module areas), each command's schema.

---

## 2. Concepts to teach (dependency order)

1. **What a game is to a computer: a loop.** Problem: a game must react to input and redraw many times a second.
   Approaches: fixed loop, variable delta, fixed simulation + variable rendering. Strata: variable frame for `OnUpdate`,
   fixed steps (default 60/s, project FixedRate 30-240) for physics and `OnFixedUpdate`, accumulator with a cap of 2/15 s
   and time dilation (`Scene.cpp` L2239-2330). Newcomer error: moving things with constant per-frame amounts (frame-rate
   dependent); reading `IsKeyPressed` in `OnFixedUpdate` (misses or repeats presses, skill scripting L133).
2. **Engine vs game vs editor vs runtime.** The engine is a library; the editor is a program for making; the runtime
   plays exported games; your game is data (scenes, assets) plus a script module. Strata keeps game code out of the
   engine behind a C ABI. Error: expecting to edit engine files to make a game.
3. **Projects and files.** A project folder: `.stproj`, `Assets/`, `Scripts/`, `.strata/` cache (gitignored).
   Approaches: one binary project blob vs text files per asset; Strata: JSON documents + `.meta` handles, edited only
   through the editor. Error: editing `.stscene`/`.meta` by hand; moving files in the file manager (breaks references
   unless the editor does it).
4. **Scenes, entities, components (ECS from the user side).** Approaches: deep class hierarchies (GameObject subclasses)
   vs composition. Strata: EnTT entities with registered components; behaviour lives in systems and scripts. Error: looking
   for an "Enemy class" instead of composing components plus a script.
5. **Transforms and hierarchy.** Local vs world, parent-child, units (meters), axes (y up, -Z forward, glTF +Z), Euler vs
   quaternions, degrees in commands vs radians in `SetEulerAngles`. Error: model walks backwards; rotating by adding Euler
   angles to a quaternion.
6. **Assets and import.** Source files vs imported/cooked data; stable handles; background import; import settings
   (scale, color space). Error: centimeter models 100x too big; sRGB factors; treating a normal map as color.
7. **Prefabs and instances.** Reuse with overrides; apply/revert; outdated instances. Approaches: copy-paste, prefab with
   nested overrides (Unity), blueprints (Unreal). Strata: per-property overrides, root transform/name never an override.
   Error: editing every copy by hand; expecting moving the root to count as an override.
8. **Materials and physically based shading (user level).** Base color, metallic, roughness, normal maps, emission,
   alpha modes, clear coat, transmission, IOR. Error: base colors near white (look plastic); metallic on painted metal.
9. **Light, units and exposure.** Real units (lux, cd, nits), exposure in EV like a camera, auto exposure, tone mapping;
   why small and real values both work if consistent. Strata: real units since 0.6.0, pre-exposure, Filmic default,
   presets. Error: everything washed out (auto exposure on a dark scene); dark game because editor preview lighting lied.
10. **The camera's image and quality.** Post-processing chain; anti-aliasing kinds; quality presets as cost knobs;
    Strata never renders below native resolution (Manual/Graphics "Why there is no render scale" L120). Error: expecting
    a render-scale slider; using TAA on pixel art.
11. **Scripts in C++.** Classes, inheritance and virtual functions (needed for `override`), public data members as
    fields, headers vs sources, one `ST_SCRIPT_CLASS` per class in a `.cpp`, default constructors without side effects,
    building with CMake, the shared library (module), compile errors and the Problems panel. Error: initializing in the
    constructor (runs once with no entity when the module loads to read defaults); putting `ST_SCRIPT_CLASS` in a header.
12. **Script lifecycle and ordering.** OnCreate after all existing scripts constructed; update order parents first;
    destruction at end of frame; inactive entities get nothing. Error: caching `T*` from `GetScript<T>()` across frames.
13. **Hot reload and state.** Fields survive, members do not; `OnReload`. Error: creating entities again in `OnReload`
    (duplicates; Tetris `FindCells` pattern).
14. **Input: devices vs actions.** Why actions (rebinding, gamepad+keyboard in one), kinds, composites, dead zones,
    press vs held, focus in the editor. Error: hardcoding keys; ignoring dead zones; mouse look via an action (mouse
    motion is no binding).
15. **Rigid-body physics for makers.** Static/dynamic/kinematic, colliders vs meshes, mass, friction, restitution,
    sleeping, layers and masks, triggers, raycasts, continuous collision. Error: moving a dynamic body by writing its
    transform; triggers against triangle meshes; spawning overlapping bodies.
16. **Characters.** Why a kinematic capsule controller rather than a rigid body (no tipping, steps, slopes); move vs
    jump; ground state; coyote time; camera-relative movement; facing. Error: both RigidBody and CharacterController.
17. **Cameras that follow.** Smoothing independent of frame rate (`1 - exp(-k dt)`), interpolation and drawn poses,
    `OnLateUpdate`, collision-aware arms. Error: following `GetWorldPosition()` causes judder above step rate.
18. **Animation for makers.** Skeletons, clips, state machines, parameters vs triggers, cross-fades, events, root
    motion, attachments. Error: setting trigger every frame; feet sliding without root motion.
19. **Audio.** Sources, listener, 3D attenuation, one-shots, loading before use, voice budgets. Error: one-shot dropped
    because the clip was not requested in `OnCreate`.
20. **UI.** Canvas scaling, anchors and pivots, layout groups, nine-slice, event routing (EventTarget), focus
    navigation, unscaled time for pause menus. Error: HUD built with screen-space `Text` (does not scale); alignment
    default Center cuts text.
21. **Game flow and persistence.** Scenes as levels/menus, loading screens, passing state (fields or module state),
    save files and their location, settings menus, window modes. Error: expecting entities to survive `LoadScene`.
22. **Large worlds.** Why stream (memory), cells, layers, sources, prefetch before teleport, precision limits.
    Error: player in a cell (unloads with it).
23. **Testing a game.** Determinism (seeds, fixed steps), observability (log lines, fields), automated play-tests,
    regression scripts. Strata: command scripts with `expect`/`until`, `input.sequence`. Error: timing-dependent asserts.
24. **Shipping.** What an export contains, pruning and assets loaded by path, identity, platform quirks (unsigned
    executables, Unblock, quarantine), checking the exported game headless. Error: pruned export missing assets
    `Assets::Find` loads.
25. **Licenses of assets.** CC0, CC-BY attribution, unclear licenses out. Error: shipping assets with unclear license.

---

## 3. Code worth showing

| # | File and lines | What it teaches | Reader must know |
| --- | --- | --- | --- |
| 1 | `StrataEditor/src/Editor/ScriptProject.cpp` L224-257 (the generated `Spinner` example) | The smallest complete script: class, field, `OnUpdate(deltaTime)`, quaternion turn, registration | C++ class basics |
| 2 | `Docs/Manual/Scripting.md` L14-40 (New Script template `DoorOpener`) | What New Script writes; comments on when each callback runs | 1 |
| 3 | `StrataScriptCore/Include/StrataScript/Script.h` L30-110 | The base class and its contract (lifecycle, hot reload, contacts, UI callbacks in one comment) | virtual functions |
| 4 | `Script.h` L348-376 and L842-865 | How the SDK detects which callbacks you override at compile time and how `ST_SCRIPT_CLASS` registers a class with a static registrar (static initialization, macros, `__COUNTER__`) | templates intro, macros |
| 5 | `StrataScriptCore/Include/StrataScript/Entity.h` L358-396 and `Host.h` L19-24, L105-111 | How `SetProperty` crosses the C ABI as a table of function pointers; graceful degradation when an engine lacks a function | pointers, C vs C++ |
| 6 | `StrataEditor/src/Editor/ScriptProject.cpp` L207-222 | The game's `CMakeLists.txt`: a script module is a CMake target from a package | what a build is |
| 7 | `StrataEditor/src/Editor/ProjectTemplates.cpp` L31-95 | What "Basic 3D" really is: five entities, real sun, ground collider top at y = 0, Filmic + TAA, with *why* in comments | entities/components |
| 8 | `StrataEditor/src/Panels/SceneHierarchyPanel.cpp` L72-91 and L129-150 | Presets are JSON component sets; the UI creates through the `entity.create` command (the same API agents use) | JSON |
| 9 | `Strata/src/Strata/Scene/Scene.cpp` L2239-2330 | **Central algorithm**: the fixed-timestep accumulator with max steps, time dilation, dropped backlog and interpolation alpha | concept 1 |
| 10 | `StrataEditor/src/Editor/EditorContext.cpp` L1362-1430 | Play mode is a copy (`Scene::Copy`), what is reset at start (simulated input, bindings, graphics options), what stop restores | 9 |
| 11 | `Strata/src/Strata/Input/InputActionSet.h` L61-96 | Binding text grammar (Key/, Gamepad/, 1D:, 2D:) and kinds | concept 14 |
| 12 | `Strata/src/Strata/Input/InputActions.cpp` L441-450 and L513-531 | Radial dead zone with rescale; 2D composite normalized so diagonals are length 1 | vectors, length |
| 13 | `StrataScriptCore/Include/StrataScript/Gameplay.h` L181-219 | `KeyRepeat`: a tiny state machine for held keys | 12 |
| 14 | `Samples/Tetris/Scripts/TetrisGame.h` L8-106 | Separating rules from the engine (testable, deterministic, seeded 7-bag) | classes, arrays |
| 15 | `Samples/Tetris/Scripts/TetrisBoard.cpp` L60-104, L109-150 | Script lifecycle in practice (request assets, create cells, `OnReload` finds them again), gravity as an accumulator | 9, 13 |
| 16 | `Samples/Tetris/Scripts/TetrisBoard.cpp` L282-369 | "Touch only what changed": cached shown state, `SetActive`, `SetProperty("MeshRenderer","Material")`, HUD texts | 15 |
| 17 | `StrataTests/Editor/TetrisCommands.json.in` L1-25 | A regression play-test: `expect`, `script.setField` to remove timing, `input.sequence` producing an exact score | JSON, determinism |
| 18 | `.claude/skills/strata-make-a-game/SKILL.md` L158-189 | The minimal first-person controller (actions, mouse look, yaw/pitch split between body and camera) | 14, 16 |
| 19 | `Samples/ThirdPerson/Scripts/ThirdPersonPlayer.cpp` L54-137 | A real character: camera-relative input, turn rate with `std::remainder`, coyote time, animator parameters, fall respawn | 16, 18 |
| 20 | `Samples/ThirdPerson/Scripts/FollowCamera.cpp` L43-101 | Orbit camera, exponential smoothing, `GetDrawnPosition`, raycast-shortened arm that snaps in and eases out | 17 |
| 21 | `Samples/ThirdPerson/Scripts/ThirdPerson.h` L1-63 + `ThirdPerson.cpp` L67-77 | State that survives scene loads in module scope; settings in a save file read once | 21 |
| 22 | `Samples/ThirdPerson/Scripts/SettingsMenu.cpp` L26-38 | Toggle groups: ignore the 0 events; `Graphics::SetPreset` + `Save` | 20 |
| 23 | `Samples/ThirdPerson/Assets/Animations/Robot.stanimator` (parameters, Walk/Run states with Footstep events, first transitions) | A state machine as data | 18 |
| 24 | `Samples/PhysicsPlayground/Scripts/Playground.cpp` L183-207 | Turning a mouse position into a world ray from FOV and aspect | trigonometry (tan), camera basis |
| 25 | `Playground.cpp` L223-275 | Grabbing with velocity control (a P-controller with a speed cap) and spawning 100 balls in one `InstantiateMany` call with seeded jitter | 15, 24 |
| 26 | `Samples/PhysicsPlayground/Scripts/Impact.cpp` L13-61 | Token-bucket budget for sounds; impact strength from relative velocity along the normal | 19 |
| 27 | `Samples/OpenWorld/Scripts/Explorer.cpp` L209-247 | Prefetch cells, wait, raycast for ground, teleport, release the request | 22 |
| 28 | `Samples/OpenWorld/Scripts/DayNight.h` L16-72 | Driving lights from a script: sun angle from hour, stepping to keep shadow caches, moon at night, campfires by tag | 9, transforms |
| 29 | `Samples/Showcase/Scripts/Stations.h` L38-42 + `Outpost.cpp` L205-293 | Data-driven times of day; switching baked probes with an overlap so reflections never fall to the sky | 28, probes |
| 30 | `StrataRuntime/src/RuntimeApplication.cpp` L339-353 and `StrataEditor/src/Editor/GameExport.h` L56-78 | What a shipped game understands on its command line; the export as a staged background job | 24 |

---

## 4. Figures

### Diagrams

1. **The maker's journey map**: install -> launcher -> project (template) -> scene building -> assets -> scripts ->
   play/test -> export -> exported folder; each box names the editor panel and the command family.
2. **Project folder anatomy**: `Game.stproj`, `Assets/` (with `.meta` beside each file), `Scripts/` (CMakeLists,
   CMakePresets, sources), `.strata/` (Scripts/Build, Scripts/Bin, Saves, Thumbnail.png, cache), `.gitignore`.
3. **Editor layout**: the default docking with each panel labelled (Scene/Game tabs, Hierarchy, Inspector, Asset, Content
   Browser, Console/Problems) and the toolbar (Play, Pause, Step, Simulate, Build, Export) and status pills.
4. **Entity = ID + components**: an entity "Player" with Transform, CharacterController, Script(ThirdPersonPlayer) and a
   child "Robot" with Animator and Skin; versus an inheritance tree (the approach Strata does not take).
5. **Coordinate conventions**: y up, -Z forward for cameras/lights, glTF +Z, yaw/pitch/roll; Euler degrees in commands.
6. **Frame timeline (central)**: one frame with OnUIClick..., OnUpdate, 0..N fixed steps (physics, OnFixedUpdate,
   contacts), OnLateUpdate, animation, render; with accumulator bars for 30, 60, 144 Hz displays; drawn pose between the
   last two steps (alpha).
7. **Play mode copy**: Edit scene -> `Scene::Copy` -> runtime scene; Stop discards; edits while playing go to the copy;
   project settings changes persist.
8. **Script module boundary**: game `.cpp` -> CMake -> shared library -> C ABI table (host functions, class descriptors)
   -> engine; hot reload swaps copies; crash guard catches faults.
9. **Script lifecycle state machine**: constructed -> fields applied -> OnCreate -> (OnUpdate/OnFixedUpdate/OnLateUpdate
   loop) -> OnDestroy; hot reload branch: destructor -> new instance -> fields carried -> OnReload; crash -> faulted.
10. **Input actions pipeline**: devices -> bindings (control, 1D, 2D) -> per-action max -> dead zone -> Down/Pressed/
    Released/Value -> scripts; player bindings file overriding project bindings; UI map to navigation.
11. **Prefab override model**: prefab asset -> instances; instance values vs prefab values per property; apply/revert
    arrows; outdated instance.
12. **Physics body choices**: decision tree static/dynamic/kinematic/trigger/character controller; collider shapes and
    which a trigger sees.
13. **Character controller and follow camera**: capsule with feet at origin, step height, slope limit; camera pivot,
    arm, raycast shortening; camera-relative movement vectors.
14. **Animation state machine of the robot** (from `Robot.stanimator`): Idle <-> Walk <-> Run on Speed thresholds,
    AnyState -> Jump on trigger, Wave/Dance triggers, Footstep event times.
15. **UI anchoring**: anchors/pivot/position/size for a corner score, a stretched bar, a centered panel at 1280x720 vs
    2560x1440 (numbers from `TetrisCommands.json.in` `ui.layout` expectations: [70,70,131.68,42.19] vs doubled).
16. **UI event routing**: widget -> its scripts -> EventTarget scripts; before OnUpdate.
17. **Scene flow of Sky Islands**: MainMenu (attract after 10 s) -> Loading -> Course -> Pause; module state arrow.
18. **World streaming**: persistent scene + layers of cells around a streaming source with radii; teleport prefetch.
19. **Export pipeline**: states WaitingForImports -> CookingWorlds -> Packing -> Copying -> Succeeded; output folder
    contents; pruned vs full pack.
20. **Testing loop**: write script -> build -> play -> simulated input -> observe (log/fields/capture) -> regression
    script (expect/until/bind) -> CTest.
21. **Agent path**: Claude Code -> MCP (`StrataCLI mcp`) -> JSON-RPC loopback with token -> editor commands (same as UI).

### Screenshots

Editor (Scene view of a basic3d project unless said otherwise; take at 100% and 1920x1080):
1. Launcher with templates, samples (five pictures) and agent card.
2. New Project dialog with Basic 3D chosen; Open Sample dialog.
3. The fresh Basic 3D scene in the editor (default layout).
4. Scene view vs Game view side by side during Play (drag tab beside); F8 Game camera chip.
5. Game view resolution menu; "no primary camera" notice.
6. Hierarchy "+" menu (meshes with colliders, lights, UI submenu).
7. Inspector with two entities selected (multi-edit) and with nothing selected (scene settings, Sky section).
8. Content Browser grid with thumbnails; Scripts root with classes.
9. Drop ghost with label "Crate on 'Ground'" and a dimmed ghost over empty space.
10. Prefab bar and overridden properties (bold + accent bar), Overrides menu.
11. Material editor in the Asset tab; normal-map warning with Fix.
12. New Script dialog; the generated file open in VS Code.
13. Problems panel with a build error; crash toast and the crash with stack.
14. Project Settings: Game page (title, version, icon), Input Actions page (Gameplay map, binding capture), Collision
    Layers grid, Physics Simulation, Timing, Graphics Quality table.
15. Preferences: External Editor page with detected editors.
16. Export dialog with progress; exported folder in Explorer showing the icon.
17. Activity panel listing commands by person and agent.
18. Viewport 2D canvas mode for Tetris HUD; Game UI chip on.
19. World editing: Hierarchy strip with edit layer, Cells chip, cell map in Streaming panel (OpenWorld copy).
20. Animation controller tables in the Asset tab (Robot.stanimator); `animation.preview` pose.

Lighting/look for makers (cross-check with rendering area; isolate by the named switch):
21. Basic 3D under each sky preset: `lighting.applySkyPreset {preset: Clear|Hazy|Overcast|GoldenHour}`.
22. Exposure: same scene Auto Exposure on/off; "washed out gray" failure (auto exposure on a dark scene) and fix.
23. Preview lighting: a scene with no lights in an editor capture vs the Game view (black).
24. Debug views `luminance` and `albedo` on ThirdPerson course (`viewport.capture {debugView}`).
25. TAA vs FXAA on a thin-detail scene (Post Process `AntiAliasingMethod`); TAA on pixel-art-like Tetris (softening).
26. Graphics Quality Low vs High on the Showcase Shot 2 (`--quality low` / `project.setSettings Renderer.Quality`).

Samples (existing `Samples/*/Screenshots/` and `Picture.png` can be reused; new ones listed):
27. Tetris playing with HUD and ghost piece; game over panel.
28. Sky Islands: main menu, settings menu (Graphics row), course with coin and jump pad (existing `Screenshots/Course.png`,
    `JumpPad.png`), pause menu.
29. Physics Playground: overview, ball pit after a pour (existing), grab in action, slow motion.
30. Open World: tour (existing `Tour.png`), forest (`Forest.png`), night with campfires, teleport fade.
31. Showcase: the six tour shots (existing Screenshots), photo mode panel.
32. Exported game running windowed with its title in the window bar.

---

## 5. Rules and pitfalls ("why" boxes)

1. **Never edit `.stscene`, `.stmat`, `.stproj`, `.meta` by hand; move/rename/delete through the editor.** Handles and
   references are indexed by the editor; hand edits break references and bypass undo (skill make-a-game L11; AGENTS
   "Asset pipeline").
2. **Initialize in `OnCreate`, not the constructor.** The module constructs each class once without an entity to read
   defaults (skill scripting L74; `Script.h` L66-69).
3. **Only public members registered with `ST_SCRIPT_FIELD` survive hot reload.** Everything else starts over; re-find
   entities in `OnReload` instead of creating more (Manual/Scripting "Hot reload" L177; Tetris `OnReload`).
4. **Read presses in `OnUpdate`, apply forces in `OnFixedUpdate`.** Fixed updates run 0..N times per frame (skill
   scripting L133; `AddForce` acts only in the next step L177).
5. **Follow moving bodies with `GetDrawnPosition()` in `OnLateUpdate`.** Otherwise judder above the step rate
   (Manual/Scripting L157-175).
6. **Teleport with `Teleport`, not by writing a transform** (writes take effect next step; far moves without
   `ResetInterpolation` slide visibly) (skill scripting L224, L145).
7. **Request assets early; `Instantiate` never waits.** A null entity comes back for an unloaded prefab; a one-shot whose
   clip takes > 0.25 s is dropped (skill scripting L122, L282). Reason: no frame ever blocks on disk (AGENTS rendering).
8. **Never keep `GetScript<T>()` pointers across frames; store `Entity` and check `IsValid()`** (skill scripting L651).
9. **Never block or start threads in scripts.** The engine is main-thread; an infinite loop freezes the editor (L650-658).
10. **Read controls as input actions.** Players can rebind; one action covers keyboard and gamepads (Manual/Scripting
    L109). Mouse motion is not an action (skill make-a-game L130).
11. **One of RigidBody or CharacterController, never both** (the entity becomes a rigid body with a warning) (L250).
12. **Triggers do not see triangle-mesh colliders** (box3d sensors see convex shapes only) (L91; 0.5.0 notes).
13. **Spawn bodies apart; `Instantiate` with a translation sets scale 1** unless passed (L221-223).
14. **Collision layers are the project's, not the scene's** (since 0.6.0); `SetLayersCollide` lasts until the next scene.
15. **Entities do not survive `Game::LoadScene`.** Pass state through fields of the next scene, save files or module
    state (skill scripting L387; ThirdPerson.h).
16. **A scene with no light is unlit in the game even though editor captures show preview lighting** (skill
    make-a-game L308).
17. **Automatic exposure brightens dark scenes to gray**; real daylight needs Max EV 16 (Manual/Lighting L61-70).
18. **Do not build HUDs from screen-space `Text`; use a UI canvas** (does not scale with the screen) (L355).
19. **UIText alignment defaults to Center** (HUD text cut at the left edge) (Pitfalls table L525).
20. **Pruned exports drop assets loaded by path; list them in Export > Always Include** (Manual/Settings L28).
21. **Export refuses while a build runs, the module changed since load, or scripts are unbuilt** (skill scripting L725).
22. **Unsaved scene blocks `scene.open`/`project.*`/quit unless forced** (no silent data loss) (skill make-a-game L272).
23. **Keep worlds within 20 km; roaming things in the persistent scene** (float precision; cells unload) (Manual/Worlds L91).
24. **Prefetch cells before a teleport** or the player falls through missing ground (Manual/Worlds "Scripts" L73).
25. **Deterministic play-tests: seeds, fixed-step input durations, `input.sequence`, paused `until` waits** (skill
    make-a-game L386-436). Reason: calls take ~0.1 s and steps per frame vary by machine.
26. **No render scale, ever** (Manual/Graphics L120; Roadmap "Later"): quality presets lower costs, not resolution.
27. **Asset licenses: CC0 or CC-BY only, credited** (skill make-a-game L103; `Samples.Content`).
28. **In a toggle group act only on value 1** (SettingsMenu.cpp L28-33).
29. **Windows path length**: deep project folders build elsewhere; extremely deep ones are refused (Manual/Scripting L208).
30. **Rebuilding the engine while an editor runs fails** (locked executable) (skill make-a-game L31) - engine developers.
31. **`ST_SCRIPT_CLASS` once per class, in a `.cpp`, never in a header** (duplicate registration) (skill scripting L70).
32. **Shared libraries a module links must sit next to it / RUNPATH; `$ORIGIN` fails under hot reload** (L761-763).

---

## 6. Hands-on

### For game developers (progression ends with a finished small game, then a larger one)

| # | Exercise | Difficulty | Proves |
| --- | --- | --- | --- |
| G1 | Install, open the launcher, open a copy of Tetris, Play it, read its README | 1/5 | Can install and run samples |
| G2 | New Project (Basic 3D); add a Cube from "+", move/rotate/scale with gizmos, Play, Stop (see it restored) | 1/5 | Editor navigation, play copy |
| G3 | Add a dynamic RigidBody to the cube, drop it on the ground; make a ramp; change friction/restitution | 1/5 | Bodies and colliders |
| G4 | Import a glTF model and a texture; fix the model's scale with `asset.info` bounds; make a material with the texture | 2/5 | Assets and materials |
| G5 | Turn the cube into a prefab, place five, override one's color, apply another's change | 2/5 | Prefabs |
| G6 | Attach `Spinner`; change `DegreesPerSecond`; edit code during Play and watch hot reload | 2/5 | Scripts, fields, hot reload |
| G7 | Light the scene with each sky preset; break exposure (auto off at -15), fix it; add a lantern point light with shadows | 2/5 | Lighting units, exposure |
| G8 | **Small finished game: "Coin Run"** (from Basic 3D): input actions Move/Jump, player with CharacterController and first-person script (skill make-a-game L158), coins as trigger prefabs with a spin script, HUD canvas (coins, timer), coin sound, win panel, restart with `Game::ReloadScene`, title/icon, export, run the exported game | 3/5 | The whole journey once |
| G9 | Second game: **Tetris from scratch** guided by `Samples/Tetris` (rules class, board script, KeyRepeat, HUD, sounds, pause, game over), then a command-script regression that checks an exact score | 3/5 | Pure gameplay programming, determinism, testing |
| G10 | Add a main menu scene (canvas, no camera), settings menu with volume slider and Graphics row, pause menu at time scale 0, save the best score | 3/5 | UI, game flow, saves |
| G11 | **Larger game: a third-person platformer** (Sky Islands-lite): skinned character + controller made with `animation.createController`, follow camera with raycast arm, jump pads, checkpoints, moving platform in `OnFixedUpdate`, footstep events, menus, loading scene, pruned export | 4/5 | Characters, animation, cameras, multi-scene game |
| G12 | Physics toy: shoot balls through the cursor (port `GetPointerRay`), a goal trigger that counts, a Ghost collision layer, impact sounds with a budget | 3/5 | Raycasts, layers, contacts, audio budget |
| G13 | Make a small world: `world.create`, place props into a layer, streaming source on the player, teleport with prefetch | 4/5 | Worlds |
| G14 | Rebindable controls menu: list bindings, capture a new key, save, reset | 3/5 | Input action rebinding |
| G15 | Let an agent build a level: connect Claude Code via MCP, ask it to place props with `asset.place`, inspect the Activity panel, export the session as a command script and replay it on a fresh copy | 3/5 | Agent workflow, replay |
| G16 | Day/night script driving the sun under the atmosphere, campfires by tag (port `DayNight.h`) | 3/5 | Scripted lighting |

### For engine developers (changing the engine from the game maker's side)

| # | Exercise | Difficulty | Proves |
| --- | --- | --- | --- |
| E1 | Read `PopulateBasic3D`; add a third template "basic2d" (orthographic camera, FXAA, no sky) with a `EditorTemplateTests.cpp` case and launcher card | 3/5 | Templates, commands, tests |
| E2 | Add a Hierarchy preset (e.g. "Trigger Box": BoxCollider + RigidBody IsTrigger) that goes through `entity.create`; test it | 2/5 | UI calls commands |
| E3 | Add an SDK helper in `Gameplay.h` (e.g. a `Cooldown` class) used only inside a script module, covered by the feature test | 3/5 | SDK rules, feature test |
| E4 | Add a host function (e.g. `Game::GetLanguage`) appended to `StrataScriptHostAPI` and `ST_SCRIPT_HOST_FUNCTIONS`, with `ST_SCRIPT_DETAIL_HOST_WITH` check, a `Scripting.*` test and feature script | 4/5 | ABI append-only rules |
| E5 | Add a runtime option to `c_Arguments` (e.g. `--mute`) with tests | 3/5 | Runtime, command-line options |
| E6 | Add a new component the maker can use (skill add-component), with Inspector tooltip units and feature-test coverage | 4/5 | Registration path end to end |
| E7 | Trace `Game::LoadScene` from the SDK to `EditorContext::HandleRuntimeRequests` and `GameRuntime`; write a diagram | 3/5 | Play mode/scene switch internals |
| E8 | Extend a sample's command script with a new `expect` for a feature you added; run the CTest | 2/5 | Sample regressions |
| E9 | Measure the fixed-step loop: set FixedRate 30/60/240, read `Time::GetStepAlpha` and `play.state` counts | 2/5 | Timing internals |

---

## 7. Glossary

- **Engine**: the library that runs games (rendering, physics, audio, scenes); Strata's is `Strata/`.
- **Editor**: `StrataEditor`, the program in which games are made.
- **Runtime**: `StrataRuntime`, the player of exported games, copied and renamed per game.
- **Launcher**: the editor's start page when no project is open.
- **Project**: a folder with `<Name>.stproj`, `Assets/`, `Scripts/`, `.strata/`.
- **Template**: what a new project starts with (`empty`, `basic3d`).
- **Sample**: a finished game shipped to learn from, always opened as a copy.
- **Scene**: a document of entities (`.stscene`); a level, a menu, a loading screen.
- **Start scene / loading scene**: the scene an exported game starts with / plays while it loads.
- **Entity**: a thing in a scene, identified by a UUID, made of components.
- **Component**: a block of data on an entity (Transform, MeshRenderer, RigidBody...).
- **Transform**: position, rotation (quaternion), scale, relative to the parent.
- **World position / local position**: position in the scene / relative to the parent.
- **Quaternion**: a four-number rotation without gimbal lock; Euler angles are pitch/yaw/roll.
- **Forward (-Z)**: the direction cameras, lights and `GetForward()` look along.
- **Asset**: a file the game uses (model, texture, sound, material, prefab, scene).
- **Asset handle**: the stable UUID of an asset, kept in its `.meta` file.
- **Import / import settings**: converting a source file into engine data / options of that conversion (Scale, RemoveSun).
- **Sub-asset**: a mesh, material or texture inside an imported model.
- **Built-in mesh**: `Builtin/Cube` and the other primitive shapes.
- **Material**: how a surface looks (base color, metallic, roughness, maps...).
- **PBR**: physically based rendering, shading from physical quantities.
- **Prefab / instance / override**: a saved group of entities / a placed linked copy / a value an instance keeps.
- **Apply / Revert / Unpack**: write an override into the prefab / take the prefab's value / end the link.
- **Outdated instance**: an instance changed since it last took its prefab's values.
- **Gizmo**: the handles to move, rotate and scale in the Scene view.
- **Scene view / Game view**: the editor's camera with overlays / what the player sees.
- **Play / Simulate / Pause / Step**: run the game on a copy / physics only / freeze / one fixed update.
- **Preview lighting**: the editor's stand-in light for scenes with none; the game has none.
- **Lux, candela, nits**: units of illuminance (sun), luminous intensity (lamps), luminance (sky, emission).
- **Exposure (EV)**: how bright the image is rendered, in camera stops; auto exposure adapts it.
- **Tone mapping (Filmic, ACES)**: compressing HDR brightness for the screen.
- **Anti-aliasing (FXAA, TAA, Morphological)**: smoothing stair-stepped edges.
- **Graphics Quality preset**: Low/Medium/High/Ultra/Custom costs of shadows, AO, reflections...
- **Reflection probe / bake**: a box that captures surroundings for reflections / rendering that capture in the editor.
- **Script / script class / script module**: game logic class / its registered C++ type / the shared library built from `Scripts/`.
- **SDK**: `StrataScriptCore`, the headers scripts include.
- **ABI**: the C-level binary interface between module and engine; versioned, append-only.
- **Host function**: an engine function the SDK calls through the ABI table.
- **Field**: a public script member registered with `ST_SCRIPT_FIELD`, shown in the Inspector and saved.
- **Hot reload**: replacing the module while the game plays, keeping fields.
- **Crash containment**: catching a script crash so the editor/game survives.
- **CMake, toolchain, preset**: the build system, the compiler set it uses, a saved IDE configuration.
- **External editor**: the code editor that opens script files.
- **Problems panel**: list of build diagnostics and crashes.
- **Frame / delta time**: one loop iteration / the seconds it covered.
- **Fixed step / fixed timestep**: a simulation tick of constant length (default 1/60 s).
- **Accumulator**: leftover time not yet simulated.
- **Time scale**: multiplier of game time (0 pauses).
- **Unscaled time**: time that runs on at time scale 0.
- **Interpolation / drawn pose / step alpha**: drawing between the last two physics poses / that pose / how far between.
- **Time dilation**: slowing the game when steps cannot keep up.
- **Rigid body (static, dynamic, kinematic)**: never moves / simulated / moved by code and pushes others.
- **Collider (box, sphere, capsule, mesh; convex, triangle)**: the shape used for collisions.
- **Trigger**: a collider that reports overlaps without pushing.
- **Collision layer / layer matrix / mask**: a body's group / which groups collide / which a query sees.
- **Raycast / overlap**: finding what a ray hits / what lies in a shape.
- **Continuous collision**: sweeping fast bodies so they do not tunnel.
- **Sleeping**: a resting body excluded from simulation until woken.
- **Character controller**: a capsule moved by code that walks, climbs steps and slopes.
- **Coyote time**: a short grace period to jump after leaving a ledge.
- **Skeleton, joint, clip, skin**: bone hierarchy, one bone, an animation, the mesh bound to bones.
- **Animator / animation controller / state / transition / parameter / trigger parameter**: the component that plays / the `.stanimator` state machine / a clip-playing node / a rule to change state / a value scripts set / a one-shot flag consumed by a transition.
- **Cross-fade**: blending from one animation to another.
- **Animation event**: a named time in a state's clip that reaches scripts.
- **Root motion**: moving the entity by the clip's own travel.
- **AttachToJoint**: a component that keeps an entity on a joint.
- **Audio source / listener / one-shot**: a sound emitter / the ears / a fire-and-forget sound.
- **Canvas (screen space, world space)**: the root of a UI over the screen / placed in the world.
- **Reference resolution / scale mode**: the size the UI is laid out for / how it scales.
- **Rect, anchor, pivot**: an element's box / where it attaches to its parent / its own reference point.
- **Nine-slice (sliced image)**: an image whose corners keep size while it stretches.
- **Layout group, mask**: automatic placement of children / clipping to a rect.
- **Selectable, focus, navigation**: a clickable widget / which one the keyboard drives / moving between them.
- **Event target**: the entity whose scripts receive a widget's events.
- **Toggle group**: toggles of which only one is on.
- **Input action / map / binding / composite / dead zone**: a named control / a set of actions / a control that drives it / several keys making one axis or vector / stick movement ignored near the center.
- **Rebinding / binding capture**: players choosing controls / listening for the next control pressed.
- **Save file**: a named file a game writes in the player's data folder.
- **Sub-scene (additive load)**: a scene loaded beside the running one.
- **World, persistent scene, layer, cell, streaming source, edit layer, cook**: a level larger than memory / its never-unloaded scene / a kind of content with its own grid / a square of a layer's grid / what decides which cells load / where new entities go / measuring cells for export.
- **Prefetch**: asking for cells before they are needed.
- **Export / pruned export / always include**: writing a playable folder / packing only what scenes use / assets kept anyway.
- **Manifest (`.stgame`) / pack (`.stpak`)**: the game's description / its compressed assets.
- **Headless**: running without a window or GPU.
- **Game identity**: title, version, company, copyright, icon.
- **Command / command script / expect / until / bind**: an editor operation with a JSON schema / a JSON list of commands / a check on a result / repeat until it holds / name a result for later steps.
- **Simulated input / input sequence**: keys and clicks sent by commands / a timeline of them in fixed steps.
- **Viewport capture**: a PNG of a view taken by command.
- **Activity journal / replay**: the list of every command run / turning it into a command script.
- **Recovery journal**: unsaved changes kept for after a crash.
- **MCP, toolset**: the Model Context Protocol agents use / a group of commands offered as tools.
- **Attract mode**: a demo the game plays by itself when idle.
- **7-bag**: shuffling all seven Tetris pieces before dealing them again.
- **Seed**: the start value of a random sequence; same seed, same game.
- **Token bucket**: a budget that refills over time (sound voices).
- **CC0 / CC-BY**: public-domain dedication / license requiring attribution.

---

## 8. Proposed chapters (teaching order)

See the structured summary for the machine-readable list. In words:

Part A, getting started: (1) What it takes to make a game; (2) Installing Strata; (3) The launcher and your first
project; (4) A tour of the editor.
Part B, building a scene: (5) Scenes, entities and components; (6) Positions, rotations and units; (7) Bringing in
assets; (8) Materials; (9) Prefabs; (10) Lighting a scene; (11) The camera's image and graphics quality.
Part C, making it play: (12) C++ for game scripts (just enough); (13) Your first script; (14) The game loop from a
script's side; (15) Input and input actions; (16) Physics for game makers; (17) Characters and cameras; (18) Animation
for game makers; (19) Sound; (20) Menus and HUDs; (21) Levels, loading, saves and settings; (22) Large worlds.
Part D, finishing: (23) Playing, testing and debugging; (24) Automated play-tests and AI agents; (25) Exporting and
shipping.
Part E, projects: (26) Tutorial: Coin Run (the first finished game); (27) Tutorial: Tetris; (28) Tutorial: a
third-person platformer; (29) Studying the samples (Physics Playground, Open World, Showcase).
Part F, reference and internals: (30) How the editor makes games (internals for engine developers); (31) Reference:
components, commands, SDK, runtime options, project file.

---

## 9. Not determined

- **Not read in full**: the 84 KB `strata-editor-automation` skill (headings only), the full Lighting, Camera and
  AntiAliasing manuals (headings and first sections), Release notes' "Known issues" sections, Roadmap waves 1-7 bodies,
  DG sections other than Samples, Exporting games, Play mode (headings only for others), Arch Editor section (bullets
  only), most sample scripts beyond the excerpts (MainMenu, PauseMenu, CourseState, Coin, JumpPad, Goal, Pushable,
  Footsteps, MenuRobot, Wander, IslandHud, FlyCamera, GoalBasket, LaunchPad, OutpostTour/Walk/Photo, Flicker,
  LoadingScreen bodies), every command's schema, every component property, the feature test project.
- **Stale documents found**: `README.md` says 0.6.0 is the latest release (0.7.0 exists); `Docs/Releases/PackageReadme.md`
  lists four samples (no Showcase), and its `Docs/Manual/` row names nine guides, leaving out `Graphics.md`. The chapter authors should check against the release that the book targets.
- **Release dates of some features** are not stated: long-path build fallback, UIMask/world-space canvases (Manual
  undated), the Scripts root of the Content Browser, Morphological AA (0.7.0 per its notes), Hierarchy search tokens.
- **Wave 8 status**: the Showcase, Scene.Timing/interpolation, drop ghost/`asset.place`, editor frame rate preferences,
  Source Radius and experimental GI are on `main`; whether all ship in 0.8.0, and the animation-graph slice (tranche 2),
  could not be determined from the documents.
- **No editor run**: no screenshot was taken; menu layout and exact UI labels come from source strings, not from seeing
  the editor. The `Entity` menu's items were not extracted (built dynamically).
- **Host function count**: 165 counted by pattern in `ScriptABI.h` L312-756; the exact number should be confirmed with
  the feature test's SDK reader.
- **Audio and physics component properties**, UI component property lists and animation transition fields are in other
  areas' inventories and were not enumerated here.
