# Inventory: Big worlds and shipping (world partition, cell streaming, the runtime, exporting a game)

Surveyed at `main` 822a7a46 of G:/GameEngineAI. Paths are relative to the repository root. Line numbers are those of
that commit. "Arch" is `Docs/Architecture.md`, "DevGuide" is `Docs/DeveloperGuide.md`, "Manual" is
`Docs/Manual/Worlds.md`, "Readme" is `Docs/Releases/PackageReadme.md`.

Release history as the release notes state it: export and the runtime, the launcher, templates and recent projects
arrived in **0.3.0** (waves 1-3; `Docs/Releases/0.3.0.md` lines 28, 45, 80-88); **world partition** in **0.4.0** (wave 4;
`0.4.0.md` lines 29-40, 124-133, 305-314), together with cooked binary scenes in packs; the **Open World** sample and
picture cards for samples in **0.5.0** (`0.5.0.md` lines 33-55); the **game's identity** (title, version, company,
copyright, icon), Windows version resources, the Linux desktop entry and manifest version 5 (settings sections) in
**0.6.0** (`0.6.0.md` lines 28, 85-107, 149); the **graphics options of players**, `--quality` and `--seconds` in
**0.7.0** (`0.7.0.md` lines 29-46, 93, 233).

---

## 1. Features

### 1.1 The World asset and its grid (`Strata/src/Strata/World/`)

| Feature | What it is | Where | Documented |
| --- | --- | --- | --- |
| World document `.stworld` | JSON document with header `{"Strata":{"Format":"World","Version":1}}` and a `World` object: name, persistent scene handle, grid origin (X, Z in double), layers, cells, optional cooked index | `World/WorldAsset.h` 73-134 (`WorldData`, `WorldAsset`); `WorldAsset.cpp` 247-371 (`FromJson`), 460-505 (`ToJson`), 551-596 (`WorldAsset::FromJson`, `Deserialize`, `ToDocument`) | Arch "World partition" 2747 (JSON example 2755-2767) |
| Layers | A grid of square cells of one size (`CellSize` 1-65,536 m) that streams within one distance (`StreamingDistance` 0-1,000 km); 1-32 per world; ID 1-255 unique; unique names without commas/control chars; `EnabledByDefault`, `LoadBeforeStart` | `WorldAsset.h` 19-29 (`WorldLayer`) | Arch 2769-2775; Manual "What a world is" |
| Cells | A (layer, X, Z) square that has content: a scene asset of its own (never the persistent scene, never shared) | `WorldAsset.h` 31-40 (`WorldCell`) | Arch 2776-2780 |
| Cell file layout and derived handles | Cell documents at `<world folder>/<WorldName>/<LayerName>/<X>_<Z>.stscene`; handle `DeriveSubAssetHandle(world, "Cell/<layerID>/<X>/<Z>")` so an undo step can name a cell before its file exists | `StrataEditor/src/Editor/EditorWorld.cpp` 179-182 (`DeriveCellScene`) | Arch 2778-2780; DevGuide "World partition" 2567 |
| Cooked index | Per cell: content stamp, entities, physics bodies, bounds, closure bytes; world: `MaxBodiesInRadius`, `PersistentBodies`; `GetRecommendedMaxBodies` = ceil(1.25 x MaxBodiesInRadius) capped at the physics limit | `WorldAsset.h` 42-71 (`WorldCellSummary`, `WorldIndex`); `WorldAsset.cpp` 507-511 | Arch 2781-2783 |
| Validation | Type checks in `FromJson` (with a `Reader` helper class, `WorldAsset.cpp` 34-200), every rule in `Validate` (373-458): extent 1,000 km, layer rules, duplicate keys, duplicate cell scenes, cell scene = persistent scene, index version, bounds | `WorldAsset.cpp` 34-458 | Arch 2784-2786 |
| Limits | `c_MaxLayers` 32, `c_MaxCells` 2^20, `c_MaxExtent` 1,000 km, `c_SupportedExtent` 20 km (float32 precision) | `WorldAsset.h` 78-89 | Arch "Coordinates and what is not loaded" (~2918-2924); Manual "Limits" |
| Fast lookups | `FindCell`, `FindSummary` through hash maps from packed keys | `WorldAsset.h` 126-133; `WorldAsset.cpp` 533-549, 615-629 | Arch 2785 |
| Memory accounting | `GetMemoryUsage` estimates hash-map nodes too (residency budgets) | `WorldAsset.cpp` 598-613 | - |
| References | `AssetDependencies::Scan` lists persistent scene + every cell; scenes stop load closures (`AssetClosureScope::Load`) so loading a world loads no cell; an export's closure (`All`) ships them all | `Strata/src/Strata/Asset/AssetDependencies*` (not read in detail) | Arch 2787-2789 |
| Loader registration | World loader registered as JSON bytes -> `WorldAsset::Deserialize` | `World/WorldRegistration.cpp` 33-38 | Arch 2747 |
| Cell keys | `WorldCellKey {Layer, X, Z}` packed into 64 bits (layer in the top byte, X and Z offset by 2^27 into 28 bits each); order of packed = order of (Layer, X, Z) | `World/WorldGrid.h` 14-29; `WorldGrid.cpp` 18-19, 34-49 | Arch 2791-2795 |
| Grid math | `CellAt` (floor division from the grid origin, lower edges inclusive, NaN and far positions clamp), `CellBounds`, `Distance` point-to-square on the XZ plane (0 inside), all in double | `WorldGrid.h` 31-49; `WorldGrid.cpp` 21-30, 54-74 | Arch 2791-2795 |

### 1.2 Components and the World scene system

| Feature | What it is | Where | Documented |
| --- | --- | --- | --- |
| `WorldComponent` | Makes a scene a world's persistent scene: `World` (asset), `DistanceScale` 0.1-10 (quality knob); first active in hierarchy order counts | `World/WorldComponents.h` 13-18; registered `WorldRegistration.cpp` 39-44 | Arch "Components" ~2826; Manual |
| `StreamingSourceComponent` | A point cells stream around: `Enabled`, `Radius` (0 = each layer's distance), `Layers` (comma-separated names), `Priority` -100..100, `ViewBias` 0-1; facing -Z; without any, the primary camera streams | `WorldComponents.h` 21-28; `WorldRegistration.cpp` 45-55 | Arch ~2826-2832 |
| "World" scene system | `WorldStreamingSystem`: After Scripting, Before Physics and Audio (soft), runs in Play and Simulate, profile stage `World.Streaming` registered at module registration so perf logs have its column | `WorldRegistration.cpp` 57-70; `World/WorldStreamingSystem.h/.cpp` | Arch "The World system" ~2834-2842 |
| Source gathering | Active enabled sources through world transforms; layer list parsed into a 32-bit mask; unknown names warned once; primary camera fallback | `WorldStreamingSystem.cpp` 48-71 (`ParseLayerMask`), 101-138 (`GatherSources`) | Arch ~2836 |
| Idle cost | A scene with no `WorldComponent` costs one storage-empty check per update | `WorldStreamingSystem.cpp` 31-35, 159-177 (`SyncWorld`) | DevGuide 2620-2622 |
| `IWorldStreaming` service | `RequestCellsAround` (temporary source of priority 100, radius 0 = cells at the point), `ReleaseCells`, `IsLoadedAround`, `SetLayerEnabled`/`IsLayerEnabled`, `GetStats`, `IsStreaming` | `Strata/src/Strata/Scene/SceneServices.h` 464-505; `WorldStreamingSystem.cpp` 214-253 | Arch ~2838-2842 |
| Prepared start | `PrepareLoadedScene` hook: loads only the `LoadBeforeStart` layers' cells around the sources while the scene is `Preparing`, raises `PhysicsCapacity.MaxBodies` to the index's recommendation, advances sub-scenes within the frame budget, then hands the cells over (adoption) | `WorldStreamingSystem.cpp` 23-29, 276-337; descriptor hook `WorldRegistration.cpp` 67 | Arch "A world's start" ~2844-2857; DevGuide 2592-2598 |
| `WaitForStartCells` | Blocking helper for tools and tests that start without preparation | `WorldStreamingSystem.cpp` 255-274 | Arch ~2856 |
| `PinCell` on the system | The editor's play copy pins cells with unsaved edits for the session | `WorldStreamingSystem.h` 278-280; caller `StrataEditor/src/Editor/EditorContext.cpp` 1385, 1400-1405 | Arch ~2904-2910 |

### 1.3 The streaming core (`WorldStreamer`)

| Feature | What it is | Where | Documented |
| --- | --- | --- | --- |
| `WorldStreamer` | Main-thread core shared by the World system (Play/Simulate) and the editor (Edit); streams cells as sub-scenes | `World/WorldStreamer.h` 84-227; `WorldStreamer.cpp` | Arch "Streaming" 2797-2824 |
| Source description | `WorldStreamingSource`: position, forward, radius, layer mask, priority, view bias | `WorldStreamer.h` 28-38 | Arch 2799-2802 |
| Cell states | `Unloaded, Loading, Loaded, Unloading, Failed` and `WorldCellState`, `WorldActiveCell` | `WorldStreamer.h` 40-69; `WorldStreamer.cpp` 69-80 | Arch 2820-2824 |
| Wanted cells | Per source x enabled layer in its mask: existing cells within radius; visits grid squares through the hash map or the layer's cell list, whichever is shorter | `WorldStreamer.cpp` 19-60 (`GetSquaresAround`, `ForEachCellAround`), 449-483 | Arch 2804-2807 |
| Hysteresis | Keep while within radius + H, H = max(CellSize/2, 0.1 x radius) | `WorldStreamer.cpp` 462-475 | Arch 2808-2810 |
| Load ordering | Total order: priority desc, view-biased distance asc, packed key asc; `High` asset priority within half the radius, else `Normal`; at most `c_MaxConcurrentCellLoads` = 4 | `WorldStreamer.cpp` 476-480, 539-573, 601-632 | Arch 2811-2814 |
| View bias | Cells ahead of a source rank as if `ViewBias x radius x cos(angle)` nearer (ordering only) | `WorldStreamer.cpp` 452-455, 476-480 | Arch 2812 |
| Pins | Counted pins: every `PinCell` needs an `UnpinCell`; pinned cells are wanted at top priority | `WorldStreamer.cpp` 161-188, 484-491 | Arch 2802 |
| Layer toggles | By name, remembered before the world loads (`m_LayerOverrides`), applied on load | `WorldStreamer.cpp` 122-159, 255-285 | Arch 2802 |
| Unloads and cancellation | Cells left behind, of disabled layers or gone from the world unload first in key order; a Loading cell is cancelled through `Scene::UnloadSubScene`; external unloads are followed | `WorldStreamer.cpp` 497-537, 634-646 | Arch 2808-2810 |
| Physics reservation | With a cooked index, before starting loads, reserve bodies for persistent + all held + starting cells via `IPhysicsCapacity::Reserve` | `WorldStreamer.cpp` 576-599 | Arch 2815-2817 |
| Idle/determinism | Evaluates only when dirty (pins, layers, world, scale, finished loads) or a source moved > 1 cm (`c_SourceEpsilon`); decisions depend only on inputs and states (`GetLastDecisions`) | `WorldStreamer.cpp` 228-253, 392-406 | Arch 2818-2822 |
| Polling in flight | Only `m_InFlight` cells are polled each update; counts created/destroyed entities | `WorldStreamer.cpp` 287-366 | Arch 2820 |
| Failures | Failed cells keep their error and retry only when their scene's source revision changes (a reimport), checked only when the asset manager's content version moved | `WorldStreamer.cpp` 334-345, 368-390 | Arch 2822-2823 |
| Adoption | Takes over existing sub-scenes whose source is a cell (prepared start, play copy) | `WorldStreamer.cpp` 190-226 | Arch 2824-2826 |
| World asset never held | `GetAsset` every update at `High` priority (residency), `PeekLoadedAsset` for reads; `weak_ptr` to detect a reloaded asset | `WorldStreamer.cpp` 109-113, 239-246, 255-285 | Arch 2799-2801; AGENTS "Assets" rule |
| Queries | `IsLoadedAround`, `GetStats` (`WorldStreamingStats` incl. `StateVersion`), `GetCellStates`, `GetCellState`, `GetActiveCells`, `GetCellSubScene`, `GetCellStatus` | `WorldStreamer.cpp` 663-782; `SceneServices.h` 464-483 | Arch 2826-2830 |
| `SetReloadCells` | Editor reads cells as their files are now (`SubSceneOptions::Reload`) | `WorldStreamer.h` 117-118 | Arch "The editor's world" |

### 1.4 Sub-scenes and the frame's loading budget (shared with the Scene area)

| Feature | What it is | Where | Documented |
| --- | --- | --- | --- |
| Sub-scenes (additive loads) | `Scene::LoadSubScene`, `BeginAdditiveLoad`, `UnloadSubScene`, `AdoptSubScene`, `SetSubSceneOf`, `GetSubSceneOf`, `FindSubSceneBySource`, `UpdateSubScenes`, `FlushSubSceneUnloads`, `GetSubSceneMembershipVersion` | `Scene/Scene.h` 195-268; `Scene/SubScene.h` (whole, 69 lines); `Scene/SubSceneLoad.h`; `Scene/SceneSubScenes.cpp` (630 lines) | Arch "Additive scenes" bullet at 1152 |
| Sub-scene state machine | `Loading -> Instantiating -> Loaded`, `Failed`, `Unloading` (inactive at once, destroyed in slices, children before parents) | `SubScene.h` 26-33 | Arch 1152 |
| `SubSceneComponent` | Runtime-only tag on top-level entities naming their sub-scene; never serialized or registered | `SubScene.h` 17-24 | DevGuide 2578-2579 |
| `SceneWorkBudget` | Per-frame budget of loading work: deadline (default 4 ms), entities to create/destroy, sub-scene ms cap (2 ms); `FitChunk` and `RecordChunkCost` adapt chunk sizes to measured cost per entity | `Scene/SceneWorkBudget.h` 12-47; `SceneWorkBudget.cpp` 32-59; chunk use `SceneSubScenes.cpp` 20-45 | DevGuide 2592-2598 |
| Slice limits | `SceneSettings::MaxEntitiesInstantiatedPerFrame`/`MaxEntitiesDestroyedPerFrame` (5,000), `Scene::c_MaxSubSceneMillisecondsPerFrame` = 2 | `Scene.h` 61-77, 195 | DevGuide 2596-2598 |
| `SceneLoadOptions::PrepareSystems` | Scenes that will run run each system's `PrepareLoadedScene` while `Preparing` | `Scene/SceneLoader.h` 21, 40-47, 119 | DevGuide 2592-2595 |

### 1.5 Scripting surface

| Feature | What it is | Where | Documented |
| --- | --- | --- | --- |
| SDK `World` class | `World::RequestCellsAround`, `IsLoadedAround`, `SetLayerEnabled`, `IsLayerEnabled`; `WorldCellRequest::Release` | `StrataScriptCore/Include/StrataScript/World.h` 14-78 | Manual "Scripts"; 0.4.0 notes |
| Host functions | `WorldRequestCellsAround`, `WorldReleaseCells`, `WorldIsLoadedAround`, `WorldSetLayerEnabled`, `WorldIsLayerEnabled` (each wraps `HostCall`, resolves the context, `RequireWorld` reports misuse once) | `Strata/src/Strata/Scripting/ScriptHostAPI.cpp` 2652-~2760; table 3569-3573 | Arch "Scripting"; AGENTS "Scripting" rules |
| Game window from scripts | `Game::SetWindowMode`, `SetResolution`, `SetVSync` (-> `IGameWindow`) | `StrataScriptCore/Include/StrataScript/Game.h` 19, 75-91 | Arch "Export and the runtime" |
| Graphics options from scripts | `Graphics::Options/Get/Set/SetPreset/Reset/Save` (-> `IGameGraphics`) | `StrataScriptCore/Include/StrataScript/Graphics.h` 110-232 | DevGuide "Players' options" (bullet at 4123 area of Arch; DevGuide "Quality settings") |
| Scene loads from scripts | `Scene::RequestSceneLoad`, `RequestQuit`, `Game::GetSceneLoadProgress` honored by `GameRuntime` | `Strata/src/Strata/Runtime/GameRuntime.cpp` 339-362 | Arch "Export and the runtime" |

### 1.6 The editor's world (`StrataEditor/src/Editor/`)

| Feature | What it is | Where | Documented |
| --- | --- | --- | --- |
| `EditorWorld` | Attached when the edited scene is a world's persistent scene; streams around the editor camera with a `WorldStreamer` | `EditorWorld.h` 57-241; `EditorWorld.cpp` 61-93, 505-535; attach in `EditorContext.cpp` 712 | Arch "The editor's world" ~2878-2916; DevGuide 2574-2591 |
| Edit settings | Edit layer ("Persistent" default), visible layers, radius scale (`world.edit`) | `EditorWorld.h` 87-94; `.cpp` 95-138 | Arch ~2910-2913 |
| Keep-loaded reasons | `world.loadCells` pins, selection pins, undo-requested pins (until next save), dirty and saving cells, all merged in `SyncPins` | `EditorWorld.cpp` 477-503, 505-528 | Arch ~2884-2889 |
| Dirty tracking as an undo observer | Marks cells and the persistent scene touched by each step; settings changes; snapshot steps dirty everything loaded | `EditorWorld.cpp` 427-475 (`MarkCellDirty`, `MarkStates`, `OnApplied`) | Arch ~2889-2893 |
| Cells in undo steps | `EntityState::Cell`, `SceneEdit::LinkCells`, `SceneEdit::CheckCells`, `ISceneCellLoader` (`DescribeCell`, `RequestCell`) | `Editor/SceneEdit.h` 41, 81-94; `EditorWorld.cpp` 415-425 | Arch ~2893-2899 |
| Re-celling | `Recell` moves edited top-level entities into the cell at their position within the same undo step; created entities go into the edit layer's cell; new cells made in memory with derived handles (`AdoptSubScene`) | `EditorWorld.cpp` 275-313 (`EnsureCellSubScene`), 315-345 (`Recell`); caller `EditorContext.cpp` 1887 | Arch ~2910-2916 |
| `MoveEntities` | `world.moveEntities`: validate all targets first, then move | `EditorWorld.cpp` 347-391 | Arch ~2917 |
| World save | Two `DocumentSaver` requests: (1) persistent scene and dirty cells from one `SerializedOnly` snapshot with per-document roots, new cells reserved; (2) the World document with fresh index entries once stamps exist | `EditorWorld.h` 29-55, 144-164; `EditorWorld.cpp` 537-758 | Arch ~2899-2909; DevGuide 2579-2588 |
| Play copy | `PrepareRuntimeCopy`: adopts fully loaded cells as sub-scenes of the copy, removes partially loaded ones, returns dirty cells to pin | `EditorWorld.cpp` 760-799; `EditorContext.cpp` 1382-1405 | Arch ~2904-2910; DevGuide 2574-2577 |
| Recovery | `CollectCells`, `PrepareRecoveredCells` for `scene.recover` of a world | `EditorWorld.h` 126-142; `EditorWorld.cpp` 184-273 | Arch ~2895-2899 |
| Cell IO | Streamed cancellable reads of cell documents, summaries from memory, `CreateDocument` (meta first, chosen handle) | `WorldCellIO.h` (61 lines), `WorldCellIO.cpp` | Arch "The cook" |
| The cook (`world.cook`) | Measures changed cells on I/O jobs (content stamps, session `WorldCookCache`), computes `MaxBodiesInRadius`, fails on shared entity IDs, warns beyond 20 km and for empty cells; writes the index and optionally the physics capacity (one undo step); restarts if the World document changed meanwhile | `WorldCook.h` 21-125; `WorldCook.cpp` 40, 92-334, 336-396 | Arch "The cook" ~2859-2876 |
| World commands | `world.cook`, `world.create`, `world.setLayers`, `world.status`, `world.edit`, `world.loadCells`, `world.moveEntities`, `world.info` (plus `physics.stats`, `physics.setDetailedStats` in the same file) | `EditorWorldCommands.cpp` 445, 577, 670, 814, 830, 888, 951, 988, 1036, 1076 | Arch ~2913-2920 |
| `world.create` defaults | Four layers Terrain, Buildings, Props, Gameplay of `cellSize` (default 64 m), distance = 4 cells, first loads before start; persistent scene with basic3d content and a "World" entity | `EditorWorldCommands.cpp` 577-668 | Manual "Create a world" |
| Cell map | Streaming panel's World section: cells as squares colored by state, dirty outlines, pins, sources with radius circles; pan/zoom; context menu Load and pin / Unpin / Show | `StrataEditor/src/UI/CellMap.h/.cpp`; `Panels/StreamingPanel.h` 63-101, 157-180 | Arch "The cell map" ~2926-2938; Manual "The cell map" |
| Hierarchy world strip and search | World name, loaded/unsaved counts, edit layer combo, map button; search `l:<layer>`, `l:persistent`, `cell:<x>,<z>` | `Panels/SceneHierarchyPanel.h` 38, 77-110 | Arch "A world in the Hierarchy and the Inspector" ~2940-2952 |
| Inspector cell line | "Cell: Props (3, -1)" / "Persistent scene" | `Panels/InspectorPanel.cpp` (not read in detail) | Arch ~2945 |
| Viewport cell bounds | Debug lines of active cells around the camera, colored by state, rebuilt only on `StateVersion` change (`viewport.setSettings {cellBounds}`, "Cells" chip) | `Editor/CellBoundsOverlay.h/.cpp`; `EditorViewport.h` 129-130; `ViewportRenderer.h` 164-179; `EditorViewportCommands.cpp` 138, 1157 | Arch ~2948-2952 |
| Asset panel / Content Browser | New > World; the Asset panel shows layers and a Cook button | `Panels/AssetInspectorPanel.*`, `Panels/ContentBrowserPanel.*` (not read in detail) | Manual "Create a world", "Save and cook" |
| Precision guard | `World.Coordinates` tests at 20 km; cook warning | `StrataTests/src/World/WorldCoordinatesTests.cpp` 81-160; `EditorWorldTests.cpp` 1416-1450 | DevGuide 2589-2591 |

### 1.7 The runtime (`Strata/src/Strata/Runtime/`, `StrataRuntime/`)

| Feature | What it is | Where | Documented |
| --- | --- | --- | --- |
| `GameRuntime` | Windowless core that runs an exported game: manifest, settings validation and provider, `RuntimeAssetManager` on the pack (+ patch packs), script module in its own `ScriptEngine` (no hot reload), saves, input bindings, graphics options, loading scene + start scene loads, scene switches, quits, script crash handling | `Runtime/GameRuntime.h` 30-204; `GameRuntime.cpp` 45-362 | Arch "Export and the runtime" 4072 (para at ~4152-4172) |
| Runtime options | `AssetBudgets`, `TimeDilation`, `Interpolation`, `KeepEveryFixedStep`, `SaveFilesDirectory`, `PrepareRenderScenes`, `Settings`, `Quality` | `GameRuntime.h` 30-60 | Arch ~4128-4140 |
| Non-blocking scene loads | `SceneLoader::LoadAsync`; the running scene plays until the next one is ready; same-scene requests keep the load; switches release old assets later (`ScheduleTrim`) and destroy the old scene in the background | `GameRuntime.cpp` 178-224, 226-282 | Arch ~4160-4168 |
| Loading scene | Plays while the start scene loads; restart handling | `GameRuntime.cpp` 131-144, 201-209, 233-248, 352-357 | Arch ~4157-4160 |
| Fixed-step accounting | `GetPlayedSeconds` counts only fixed steps after the start; `LimitToFixedSteps` for deterministic runs | `GameRuntime.cpp` 28-41, 296-314; `GameRuntime.h` 101-107 | Arch ~4126-4131 |
| Frame-rate cap while loading | 60 fps while nothing plays (`c_LoadingFrameRate`) | `GameRuntime.h` 143-147 | Arch (runtime para) |
| Perf log columns of the runtime | World streaming, physics capacity and step diagnostics columns | `GameRuntime.cpp` 364-432 | Arch ~4140-4150 |
| `GameRenderer` | Renders the scene from its primary camera into the back buffer; UI-only scenes over black; a "No camera to show" message scene otherwise; resets exposure/TAA history on scene change; follows the graphics options by version; `RenderEmpty` | `Runtime/GameRenderer.h` 23-90; `GameRenderer.cpp` 23-176 | Arch ~4160-4162; GameUI area |
| Render perf columns | `DrawCalls`, `Instances`, `Triangles`, `VisibleProxies`, `OccludedProxies`, `InstanceUploadMB`, `LocalShadowLights`, `LocalShadowViewsDrawn` | `GameRenderer.cpp` 178-203 | Arch ~4146-4149 |
| `GamePresentation` | Title, banner, data directory name (keyed by manifest Name), icon path, AppId; applied to the window spec before anything starts | `Runtime/GamePresentation.h/.cpp` (32 + 32 lines) | DevGuide "Exporting games" 3026-3036 |
| `GameWindowService` | `IGameWindow`: requests stored, applied once per frame after update; idempotent; headless reflects requests | `Runtime/GameWindowService.h/.cpp` | Arch ~4110-4115 |
| `GameGraphicsService` | `IGameGraphics`: project quality + player's `GraphicsOptions.json` + `--quality`; version-pulled, no per-frame work; only it touches the file | `Runtime/GameGraphicsService.h` 22-96; `.cpp` 184-658 | DevGuide "Quality settings", "Players' options"; AGENTS "Scripting" |
| `FramePerfLog` | CSV per frame: built-in columns (stages, job threads, asset streaming, upload queue, device memory, private memory, GPU) + column groups; capture at frame end, write once GPU times arrive | `Runtime/FramePerfLog.h` 18-155; `FramePerfLog.cpp` (296 lines) | Arch ~4131-4152 |
| `StrataRuntime` executable | `RuntimeLayer`, `RuntimeApplication`, `CreateApplication`, `GetProgramRun`; options `--game --headless --windowed --resolution --frames --seconds --screenshot --asset-budget-mb --perf-log --save-directory --quality --help`; exit codes 1 / 2 / game's | `StrataRuntime/src/RuntimeApplication.cpp` 35-533 | Arch ~4103-4131; Readme "First start" |
| Manifest discovery | `<exe stem>.stgame` next to it, else the only `.stgame` there | `Project/GameManifest.h` 76-78 | Arch ~4103 |
| Windows packaging of the runtime | GUI subsystem with `mainCRTStartup`, manifest, StrataMark icon and version resource (`StrataRuntime.rc.in`), linker map for `StrataRuntime.NoTooling`, `ThirdPartyNotices.md` copied post-build | `StrataRuntime/CMakeLists.txt` 1-42; `StrataRuntime.rc.in` | AGENTS "Windows subsystem"; DevGuide "Windows subsystem" |
| No tooling in games | The runtime links no editor/asset-pipeline/network layers | `StrataTests/Architecture/Layers.json` 93-97 (Runtime layer); comment `RuntimeApplication.cpp` 525-526 | 0.4.0 notes line 91 |

### 1.8 The game manifest and identity (`Strata/src/Strata/Project/`)

| Feature | What it is | Where | Documented |
| --- | --- | --- | --- |
| `.stgame` manifest v5 | Name, Title, Version, Company, Copyright, Icon, AssetPack, PatchPacks (<=256), StartScene, LoadingScene, ScriptModule, Window {Width, Height, Fullscreen, VSync}, Settings sections; versions 1-4 still load | `Project/GameManifest.h` 18-79; `GameManifest.cpp` 28-202 | Arch table ~4097; DevGuide 3009-3036 |
| Plain-file-name rule | Every file the manifest names must be next to it (no paths, no `.`/`..`) | `GameManifest.cpp` 16-24, 95-114 | (comment only) |
| `ProjectGameInfo` | Title/Company/Copyright <=128 code points, no controls; version 1-4 parts <= 65535; icon is a texture handle | `Project/GameInfo.h` 13-49; `GameInfo.cpp` | DevGuide "Project settings" 1146 |
| Save/log directory identity | Directory keyed by manifest `Name`, not title, so renames keep saves | `GameManifest.h` 38-40; `GamePresentation.h` 224-227 | DevGuide 3026-3029 |

### 1.9 Exporting (`StrataEditor/src/Editor/GameExport.*` and helpers)

| Feature | What it is | Where | Documented |
| --- | --- | --- | --- |
| `GameExport` | Non-blocking export state machine `WaitingForImports -> CookingWorlds -> Packing -> Copying -> Succeeded/Failed/Cancelled`; progress in bytes and stage text | `GameExport.h` 12-174; `GameExport.cpp` 165-862 | Arch "Export and the runtime" 4074-4094 |
| Up-front checks | Saved stopped scene (or its save in flight), start scene, no running script build, loaded module unchanged, AlwaysInclude entries, usable directory (`CheckExportDirectory`: absolute, local, outside the project, no device names, no UNC) | `GameExport.cpp` 115-130 (directory), 165-322 (`Start`); `GameExport.h` 176-178 | Arch 4074-4081 |
| Waiting and planning | Polls imports and saves, scans pending document references on a job, plans once on the main thread (`PlanAssetPack`), writes on an I/O job | `GameExport.cpp` 335-462, 527-756 | Arch 4081-4089 |
| World cooking at export | Cooks stale worlds, writes fresh indexes like import results; passes `RecommendedMaxBodies` through `AssetPackWriteOptions::AdjustSceneSettings` | `GameExport.cpp` 464-525, 640-650 | Arch "A world's start" and "The cook" |
| Asset pack | `<Game>.stpak`: every project asset (or pruned to scene closures + `Export.AlwaysInclude`), ordered by first use from the start scene, scenes/prefabs/models cooked binary (`CookDocuments`), 256 KiB zstd blocks at 4 KiB boundaries, CRC-32C | `Strata/src/Strata/Asset/EditorAssetManager.h` 138-157, 456-475; `Asset/AssetPack.h` 19-80; `AssetPackWriter.*`, `AssetPackCook.*` | Arch table ~4095; Asset area |
| Pruning | Off by default because scripts can load assets by path; `excludedAssets` listed | `GameExport.h` 27-29; `EditorAssetManager.h` 145-150 | DevGuide 3011-3014 |
| Patch packs | Mounted over the main pack in order (`RuntimeAssetManager::Mount`); a missing one stops the game | `GameRuntime.cpp` 73-84; `Asset/RuntimeAssetManager.h` 30 | Arch ~4154-4155 |
| Script module | The editor's loaded module exactly as loaded (digest), PDB unless Dist or `includeScriptSymbols: false`; export fails if scenes use scripts without a module | `GameExport.cpp` 46-68, 585-593, 663-673 | Arch table; DevGuide 3011 |
| Game icon | Texture's source PNG/JPEG/TGA/BMP (<=16 MiB, <=4096 px) made square, resized in linear light with premultiplied alpha to 10 sizes; 256-px PNG next to the manifest; small sources upscaled with a warning | `GameIcon.h` 10-63; `GameIcon.cpp` (165 lines) | DevGuide 3021-3032 |
| Windows version resources | `PEResources`: parse and rewrite a PE32+ resource section without the Win32 API; `StampGame` writes VS_VERSIONINFO and icon group `GLFW_ICON`; refuses signed images and unusual layouts | `PEResources.h` 15-100; `PEResources.cpp` (1188 lines); used `GameExport.cpp` 609-633 | DevGuide 3054-3090 |
| Linux desktop entry | `<Game>.desktop` with escaped values and quoted Exec | `DesktopEntry.h/.cpp`; `GameExport.cpp` 714-732 | DevGuide 3037-3046 |
| macOS Dock icon | Window icon becomes `NSApplication` icon while running | `Strata/src/Platform/GLFW/GLFWApplicationIcon*` (not read) | DevGuide 3047-3053 |
| Export commands | `project.export`, `project.exportStatus`, `project.cancelExport`, `project.setExportSettings {alwaysInclude, loadingScene}`, `project.setGameInfo`, `project.setStartScene` | `EditorAssetCommands.cpp` 457 and neighbours | DevGuide 3009-3024 |
| Export dialog | File > Export Game..., toolbar Export, progress bar, loading-scene choice, identity summary, follows exports started by agents | `StrataEditor/src/UI/ExportDialog.h/.cpp` | Arch 4089-4094; DevGuide 3020 |
| Installed layout | `cmake --install`/`cpack` lay out editor, runtime, CLI side by side (export copies the runtime from beside the editor) | `CMake/StrataPackaging.cmake` (not read) | Arch "The installed layout" ~4176-4198; DevGuide "Packages" 339 |

### 1.10 Launcher, templates, samples, recent projects

| Feature | What it is | Where | Documented |
| --- | --- | --- | --- |
| Launcher | `WelcomePanel` drawn instead of the dock space while no project is open: New Project, Open Project, Open Sample, recent-project cards with pictures, search, "Connect an AI agent" line, footer | `StrataEditor/src/Panels/WelcomePanel.h/.cpp` (895 lines); `UI/EditorPanelRegistry.h` 50 | DevGuide "Launcher" 3508 |
| Project dialogs | New Project (template cards, name, location), Open Sample (destination); location remembered in imgui.ini, default `<home>/StrataProjects` | `UI/ProjectDialogs.h` 17-125 | DevGuide 3508-3515 |
| Templates | `empty` and `basic3d` (camera with listener, Sun, Sky, Ground with `Materials/Ground.stmat` and box collider, Post Process) | `Editor/ProjectTemplates.h/.cpp` 23, 104-120 | DevGuide "Templates and recent projects" 3483 |
| Recent projects | JSON list in user data, shared by editors, <=12, `STRATA_RECENT_PROJECTS` override, read-only for scripted runs, checked on an I/O thread | `Editor/RecentProjects.h/.cpp` | DevGuide 3490-3498 |
| Samples | `Samples.json` index next to the executable; copies opened without `.strata`; optional `Picture` | `Editor/ProjectSamples.h/.cpp` | DevGuide 3498-3507; AGENTS "Samples" |
| Project thumbnails | After each scene save, 480x270 picture rendered at 1440x810 from the primary camera once streaming/TAA settles | `Editor/ProjectThumbnail.h/.cpp` | DevGuide 3512-3515 |
| Commands | `project.create {template}`, `project.templates`, `project.samples`, `project.openSample`, `project.open`, `project.close`, `editor.recentProjects`, `editor.removeRecentProject`, `scene.new {template}` | various `Editor/*Commands.cpp` | DevGuide 3483-3507 |

### 1.11 Samples and tests that exercise the area

- **Open World sample** (`Samples/OpenWorld/`): `Worlds/Island.stworld` with three 64 m layers (Vegetation 192 m,
  Wildlife 128 m, Landmarks 320 m), streaming source on the player, prefetch before teleport (`Scripts/Explorer.cpp`),
  loading scene with progress bar (`Scenes/Loading.stscene`, `Scripts/LoadingScreen.cpp`), regression
  `StrataTests/Editor/OpenWorldCommands.json.in`. `Samples/OpenWorld/README.md` explains how an agent made it.
- **Feature test world**: `StrataTests/FeatureTest/Assets/Worlds/FeatureWorld.stworld` with Ground and Props layers of
  2 x 2 cells.
- Unit tests: `World.Asset` (`StrataTests/src/World/WorldAssetTests.cpp` 79-327), `World.Streamer`
  (`WorldStreamerTests.cpp` 169-491), `World.Streaming` (`WorldStreamingTests.cpp` 91-339), `World.Coordinates`,
  `Runtime.Game` (`StrataTests/src/Runtime/GameRuntimeTests.cpp` 162-1068), `Runtime.PerfLog`/`Runtime.FramePerfLog`
  (`FramePerfLogTests.cpp`), `GameGraphicsTests.cpp`, `GPUGameRendererTests.cpp`, `Editor.World`
  (`StrataTests/src/Editor/EditorWorldTests.cpp` 76-1450), `Editor.WorldCook` (`WorldCookTests.cpp`), `Editor.Export`
  and `Editor.Export.GameIcon` (`EditorExportTests.cpp` 167-864), `WorldGameExportTests.cpp`, `DesktopEntryTests.cpp`,
  `TestPEImage.h`, `EditorLauncherTests.cpp`, `EditorTemplateTests.cpp`, `RecentProjectsTests.cpp`,
  `ProjectSamplesTests.cpp`. Perf/drive: `World/WorldDriveProcess.*`, `World/WorldDriveGame.*`,
  `Editor/EditorWorldPerfTests.cpp`, `WorldGamePerfTests.cpp`; test world generators `World/WorldTestUtils.*`,
  `Editor/WorldProjectUtils.h`. CTests named in DevGuide 2599-2619 and 3020-3024: `StrataRuntime.World`,
  `StrataRuntime.Smoke`, `StrataRuntime.Identity`, `StrataRuntime.Icon`, `StrataRuntime.GameIcon`,
  `StrataRuntime.VersionInfo`, `StrataRuntime.NoTooling`, `StrataEditor.Export`, `StrataEditor.Tetris`,
  `StrataEditor.OpenWorld`, `GPU.World`, `Perf.World.*`, `PerfGPU.World.CellDriveMaxFrame`.

### How completeness was checked

- Every header of `Strata/src/Strata/World/` (WorldAsset, WorldComponents, WorldGrid, WorldRegistration,
  WorldStreamer, WorldStreamingSystem) and `Strata/src/Strata/Runtime/` (FramePerfLog, GameGraphicsService,
  GamePresentation, GameRenderer, GameRuntime, GameWindowService) was read whole and every public type and function is
  in a row above; `StrataRuntime/src/RuntimeApplication.cpp` (its only source) was read whole.
- The world module registers exactly one asset loader (World), two components (World, StreamingSource) and one scene
  system ("World"): `WorldRegistration.cpp` 31-71. All are listed.
- Host functions: the five `World*` entries of `ST_SCRIPT_HOST_FUNCTIONS` (`ScriptHostAPI.cpp` 3569-3573) are listed;
  window and graphics host functions belong to Scripting/Rendering areas and are only referenced.
- Editor commands: every `registry.Register` of `EditorWorldCommands.cpp` (10) and the project/export/launcher command
  names (grep of `StrataEditor/src/Editor/*.cpp`) are listed.
- Editor files of the area: EditorWorld, WorldCellIO, WorldCook, CellBoundsOverlay, CellMap, GameExport, GameIcon,
  PEResources, DesktopEntry, ProjectTemplates, RecentProjects, ProjectSamples, ProjectThumbnail, ExportDialog,
  ProjectDialogs, WelcomePanel are all named. `StreamingView.h` was checked and belongs to asset streaming debug views,
  not to worlds. `EditorStreamingCommands.cpp` holds `asset.stats`/`asset.setBudget` (residency area).
- There are no shaders in this area. Tools: `Tools/GenerateIslandTerrain.py` (Open World) is referenced, not read.

---

## 2. Concepts to teach (dependency order)

1. **What "a level" is in memory, and why it must be bounded.** A scene is a set of entities plus the assets they
   reference; everything loaded costs RAM, VRAM and per-frame work. Approaches: load the whole level (small games),
   level switches with loading screens, seamless streaming. Strata: all three exist (scene switches through
   `GameRuntime::LoadScene`, worlds for streaming). Newcomer error: thinking "streaming" only means textures; here it
   means whole entities.
2. **Loading without stopping the frame.** Background I/O and decoding on worker threads, main-thread finalization
   in time slices. Strata: `SceneLoader::LoadAsync`, `SceneWorkBudget` (4 ms/frame by default, 2 ms of entity work),
   adaptive chunk sizes (`FitChunk`, `RecordChunkCost` raise the per-entity estimate at once, lower it halfway).
   Newcomer error: blocking on a load "just this once" (a hitch), or budgeting by entity count only (entities cost
   differently on cold caches; the code measures).
3. **Additive scenes (sub-scenes).** Loading a scene into another, tagging its top-level entities, unloading by
   deactivating at once and destroying in slices. Industry: Unity additive scenes, Unreal level streaming / sublevels.
   Strata: `Scene::LoadSubScene`, `SubSceneComponent`, `SubSceneState`. Newcomer error: destroying a big batch in
   one frame (the reason unloads are sliced); assuming IDs can collide freely (a sub-scene whose IDs exist fails).
4. **Spatial partitioning by a uniform grid.** Cells as squares from an origin; integer cell coordinates by floor
   division; packing a key into 64 bits for hashing and a total order. Alternatives: quadtrees, hand-placed streaming
   volumes (older Unreal), Unreal 5 World Partition (grid per runtime cell size, data layers), Unity's custom solutions.
   Strata: per-layer uniform grids, sparse (only cells with content exist), hash map from packed keys. Newcomer
   errors: truncation instead of floor for negative coordinates, cells as points instead of squares (distance to the
   square, not the center), float precision in the grid math (Strata uses double).
5. **Layers of different granularity.** Big terrain cells far out, small prop cells near. Strata: up to 32 layers,
   each with its own cell size and distance; layers can be toggled at runtime and named by sources. Unreal analogue:
   runtime grids and data layers. Newcomer error: one cell size for everything (either terrain pops or props waste
   memory).
6. **Streaming sources and interest management.** What decides what loads: the player, vehicles, cameras, explicit
   requests. Priority, per-source radius, facing (view bias). Strata: `StreamingSourceComponent`, primary camera
   fallback, script requests at priority 100, pins in the editor. Newcomer error: streaming around the camera only
   (in third-person or teleport cases the camera is not where gameplay needs collision).
7. **Hysteresis.** Load radius vs keep radius so an object on a border does not thrash. Strata: H = max(CellSize/2,
   0.1 x radius). Newcomer error: one threshold for load and unload (flicker, repeated I/O).
8. **Deterministic, idle-cheap decision making.** A streamer as a pure function of inputs and states, evaluated only
   when something changed; total order with tie-breaks by key; bounded concurrency (4 loads). Why: reproducible tests
   across thread counts, no per-frame cost for a still world. Newcomer error: iterating an unordered map to decide
   (order differs run to run), re-evaluating every frame.
9. **Coupling streaming with physics.** Bodies appear with cells; physics storage must have room; a body without
   collision makes things fall through. Strata: a cook measures bodies per cell and the worst case any source can
   keep loaded (`MaxBodiesInRadius`), reserves before loads (`IPhysicsCapacity::Reserve`), and the start waits for the
   ground (`LoadBeforeStart`). Newcomer error: spawning the player before the ground's collision exists.
10. **Offline "cooking" of level metadata.** Precomputing per-cell numbers so the runtime decides without loading
    cells; incremental by content stamps. Strata: `world.cook`, `WorldCookCache`, stamps, restart if the source
    changed. Newcomer error: a stale index (Strata keeps stamps and `world.info` reports stale cells).
11. **Floating-point range.** float32 has 24 bits of mantissa: precision ~2 mm at 20 km, 4 mm to 65 km. Approaches:
    origin rebasing (Unity users, many engines), double-precision world positions (Unreal 5 LWC), camera-relative
    rendering. Strata: float32 scenes and physics, camera-relative rendering, supported extent 20 km, rebasing is
    "later work". Newcomer error: building a 100 km map and seeing jitter.
12. **No HLOD yet.** What distant content looks like when it is not loaded; HLOD/impostors in other engines. Strata:
    nothing is drawn; match fog and far plane to streaming distances. Teach as a trade-off and a future exercise.
13. **Editing a streamed world.** The editor shows only part of the world; edits must go into the right cell file;
    undo must know cell membership; saves write only what changed. Strata: `EditorWorld`, re-celling by position,
    dirty marks, pins keep edited cells loaded, two-request save (cells first, world index second because stamps exist
    only after the write). Newcomer error: copying the whole world to play (Strata copies only what the editor has
    loaded); editing a child entity whose cell is the top-level ancestor's.
14. **Shipping: from project to product.** Editor data vs runtime data: imported/cooked assets packed into an
    archive, a manifest, an executable. Approaches: Unity's player build, Unreal's cook + pak. Strata: export writes
    `.stpak` (ordered by first use, zstd blocks), `.stgame` manifest, script module, icon, renamed runtime. Newcomer
    error: assets loaded by path from scripts disappear when pruning (hence `Export.AlwaysInclude`, pruning off by
    default).
15. **A runtime that is not the editor.** Same engine, different composition root: no tooling, no importers, no
    hot reload, headless mode for servers/CI. Strata: `StrataRuntime`, `GameRuntime` independent of windowing,
    `Layers.json` forbids tooling, `StrataRuntime.NoTooling` reads the linker map. Newcomer error: calling editor-only
    code from game code.
16. **Startup and scene switching UX.** Loading screens, progress, preparation before the swap frame, background
    destruction of the old scene, trimming unused assets later. Strata: loading scene, `PrepareSystems`,
    `ReleaseInBackground`, `ScheduleTrim`. Newcomer error: a black window while loading (Strata paces to 60 fps and
    renders black or the loading scene).
17. **Game identity and platform integration.** Executable resources on Windows, desktop entries on Linux, Dock icon
    on macOS; save directories keyed by a stable name. Strata: `GamePresentation`, `PEResources`, `DesktopEntry`.
    Newcomer error: keying saves on the display title (a rename loses saves).
18. **Measuring a shipped game.** Per-frame CSV logs for CI and performance work; deterministic runs (`--frames`,
    `--seconds` keep every fixed step) and screenshots. Strata: `FramePerfLog` with column groups, rows written only
    when GPU times arrive. Newcomer error: comparing runs whose game time depended on the machine's frame rate.
19. **Players' options.** Window mode, resolution, vsync and graphics presets the player chooses, applied between
    frames, persisted in the save directory. Strata: `GameWindowService`, `GameGraphicsService`. Newcomer error:
    changing the window mid-frame (swapchain invalidated).

---

## 3. Code worth showing

| # | File and lines | What it teaches | Reader must know |
| --- | --- | --- | --- |
| 1 | `Strata/src/Strata/World/WorldAsset.h` 19-40 | The data model: a layer and a cell, ID vs name | Structs, asset handles (UUID) |
| 2 | `Strata/src/Strata/World/WorldGrid.cpp` 16-49 | Floor division to cell coordinates, clamping NaN/far positions, packing a key into 64 bits with offsets and masks | Integer bit operations, two's complement |
| 3 | `WorldGrid.cpp` 54-74 | Cell square and point-to-square distance in double | Vectors, distance |
| 4 | `WorldAsset.cpp` 373-430 (first half of `Validate`) | Validating untrusted documents with reasons, never asserting | Error handling without exceptions |
| 5 | `WorldAsset.cpp` 507-511 | Rounding up 1.25x in integer math without overflow | Integer division |
| 6 | `Strata/src/Strata/World/WorldComponents.h` 13-28 | Components as plain data with documented ranges | ECS components |
| 7 | `Strata/src/Strata/World/WorldRegistration.cpp` 31-70 | Module registration: loader, components with property ranges, a scene system with ordering constraints and a profile stage | Registries, scene systems |
| 8 | `Strata/src/Strata/World/WorldStreamer.cpp` 31-60 | Choosing between scanning grid squares and the cell list, whichever is cheaper | Hash maps, Big-O |
| 9 | `WorldStreamer.cpp` 228-253 | The update skeleton: request the asset every frame, poll in-flight, re-evaluate only when dirty | Asset residency, dirty flags |
| 10 | `WorldStreamer.cpp` 421-574 (`Evaluate`) | The central algorithm: wanted/keep sets with hysteresis, view bias, pins, unload-first, total order, bounded concurrency | 4-9, sorting comparators |
| 11 | `WorldStreamer.cpp` 287-366 (`PollCellsInFlight`) | A state machine driven by another system's states (sub-scenes), including someone else unloading | Sub-scene states |
| 12 | `WorldStreamer.cpp` 368-390 | Retrying failures only when the input changed (source revisions, content version) | Asset reimport |
| 13 | `WorldStreamer.cpp` 576-599 (`ReserveBodies`) | Reserving physics room from cooked numbers before bodies arrive | Physics capacity |
| 14 | `Strata/src/Strata/World/WorldStreamingSystem.cpp` 101-138 | Gathering sources from components, forward = -Z of the world transform, camera fallback | Transforms, matrices' columns |
| 15 | `WorldStreamingSystem.cpp` 194-228 | A scene system's update and a request as a temporary source | Scene services |
| 16 | `WorldStreamingSystem.cpp` 276-337 (`PrepareLoadedScene`) | A resumable preparation hook: prepared state kept on the scene, only LoadBeforeStart layers, capacity raise, returns true when done | Coroutine-like polling, SceneLoader states |
| 17 | `Strata/src/Strata/Scene/SceneWorkBudget.cpp` 32-59 | Frame budgets and the adaptive chunk-size estimate | Time measurement, steady_clock |
| 18 | `StrataEditor/src/Editor/WorldCook.cpp` 336-396 (`ComputeMaxBodiesInRadius`) | A conservative worst-case bound over a grid, again choosing grid scan vs list | 8, 10 |
| 19 | `StrataEditor/src/Editor/EditorWorld.cpp` 275-345 (`EnsureCellSubScene`, `Recell`) | Re-celling edited entities by position within one undo step; cells made in memory with deterministic handles | Undo transactions, sub-scenes |
| 20 | `EditorWorld.cpp` 477-535 (`SyncPins`, `Update`) | Merging keep-loaded reasons into counted pins; caching a lookup by version keys | Set diff, version counters |
| 21 | `EditorWorld.cpp` 760-799 (`PrepareRuntimeCopy`) | Why play copies only what is loaded, and adopts it | Scene::Copy |
| 22 | `Strata/src/Strata/Runtime/GameRuntime.cpp` 45-156 (`Create`) | Bringing up a game: manifest, settings, pack, patches, scripts, saves, bindings, graphics, loads; every failure returns an error | Engine services, RAII order |
| 23 | `GameRuntime.cpp` 226-282 and 296-314 | Non-blocking scene switching and one budget per frame; counting game time in fixed steps | Fixed timestep |
| 24 | `GameRuntime.cpp` 28-41 | Limiting a timestep so no fixed step is dropped (determinism for checks) | Fixed-step accumulator |
| 25 | `Strata/src/Strata/Runtime/GameRenderer.cpp` 95-152 | Never show a black or stale window: camera, UI-only and message paths; history reset on scene change | Renderer basics, TAA history |
| 26 | `StrataRuntime/src/RuntimeApplication.cpp` 138-198 | The per-frame loop of a shipped game: update, start error, headless crash policy, quit, window requests, render, last-frame logic | Application/Layer model |
| 27 | `RuntimeApplication.cpp` 378-410 and 424-533 | Validating a command line before anything starts; choosing modules (headless: no Graphics module, null audio device) | Command-line parsing |
| 28 | `Strata/src/Strata/Project/GameManifest.cpp` 16-24 and 95-114 | Treating a manifest as untrusted: files must lie next to it | Path handling, security |
| 29 | `StrataEditor/src/Editor/GameExport.cpp` 595-650 | Ordering an export so failures happen before writes (icon decode, PE stamp before the pack), adjusting packed scene settings | Lambdas, job threads |
| 30 | `Strata/src/Strata/Runtime/GameWindowService.cpp` 95-~160 | Deferring window changes to a frame boundary and making requests idempotent | Swapchains (conceptually) |
| Test | `StrataTests/src/World/WorldStreamerTests.cpp` 169-234 | A test that pins down nearest-first, four at a time, hysteresis numbers and idle cost | doctest |

---

## 4. Figures

Diagrams:

1. **World anatomy**: persistent scene (player, sky, managers, `WorldComponent`) + World asset (layers, cells, index)
   + cell scene files on disk (`Worlds/Island/Props/3_-1.stscene`). Data-structure diagram.
2. **Layer grids overlaid**: two layers of different cell sizes over the same ground (terrain 256 m, props 64 m), the
   grid origin, cell (0,0), negative coordinates; how `CellAt` floors.
3. **Key packing**: 64-bit layout, 8 bits layer | 28 bits X+2^27 | 28 bits Z+2^27; sort order equals (Layer, X, Z).
4. **Wanted / keep rings**: a source with radius R and keep radius R+H; cells inside R wanted, between R and R+H
   kept if loaded, beyond unloaded; the view-bias cone ahead. Spatial diagram.
5. **Cell state machine**: Unloaded -> Loading -> Loaded -> Unloading -> (gone); Loading -> Failed (retry on source
   revision change); Loading -> Unloading (cancel). Also the underlying `SubSceneState` machine and how the two map.
6. **One streamer update (flowchart)**: GetAsset -> PollCellsInFlight -> RefreshWorld -> RetryChangedFailures ->
   dirty or moved? -> Evaluate (gather candidates, unloads in key order, sort, start up to 4, ReserveBodies).
7. **Frame timeline of a game frame**: Input, Assets.Update, Scene.Load (budget), scripts, World.Streaming, Physics,
   Audio, rendering; sub-scene slices drawing from the same `SceneWorkBudget`.
8. **Prepared world start timeline**: manifest load -> loading scene plays -> start scene `Loading` -> `Preparing`
   (World hook loads LoadBeforeStart cells; Physics hook builds bodies; renderer builds proxies) -> `Ready` -> swap ->
   streaming continues; old scene destroyed in background; trim after N frames.
9. **Physics capacity budgeting**: cooked per-cell bodies, MaxBodiesInRadius computation (worst cell neighbourhood
   per layer, summed, times sources, plus persistent), x1.25, Reserve before loads.
10. **Editor world**: editor camera source, pins from four reasons, dirty marks from undo steps, re-celling on commit;
    a gizmo drag across a border moving an entity's membership.
11. **World save sequence diagram**: BeginSave (snapshot, plan per document, reserve new cells) -> DocumentSaver
    request 1 (cells, persistent) -> FinishSave (stamps, closure bytes) -> request 2 (World document) ->
    FinishIndexSave -> MarkSaved.
12. **Play from the editor**: Scene::Copy of edited scene (persistent + loaded cells) -> PrepareRuntimeCopy adopts
    loaded cells, drops partial ones -> game's World system adopts -> dirty cells pinned -> other cells stream from
    saved files.
13. **Export pipeline state machine**: WaitingForImports -> CookingWorlds -> Packing -> Copying -> Succeeded/Failed/
    Cancelled, with which thread does what (main vs I/O job) and where checks happen.
14. **Exported game folder**: `<Game>.exe`, `<Game>.stgame`, `<Game>.stpak`, script module (+PDB), `<Game>.png`,
    `ThirdPartyNotices.md`, `<Game>.desktop` (Linux); arrows to what reads what.
15. **Asset pack layout**: header, entries at 4 KiB boundaries cut into 256 KiB zstd blocks, tables at the end;
    first-use ordering (start scene closure breadth first).
16. **Runtime composition**: `StrataRuntime` (RuntimeLayer) -> `GameRuntime` (assets, scripts, saves, settings,
    graphics service) + `GameRenderer` + `GameWindowService` + `FramePerfLog`; headless vs windowed modules.
17. **Graphics option layering**: project's `Renderer.Quality` < player's `GraphicsOptions.json` < `--quality`,
    with versions pulled by `GameRenderer`.
18. **Perf log row timing**: frame N captured at frame end, row written when GPU times of N arrive frames later.
19. **Float precision chart**: spacing of float32 vs distance (1 km ... 100 km) with 20 km marked (use the dataviz
    skill's rules; data is computable).

Screenshots (none of this area is a rendering feature, but the editor tooling and the result must be shown):

1. Open World sample in the editor, Hierarchy world strip visible (edit layer combo, loaded/unsaved counts).
   Open via launcher Open Sample > Open World.
2. Viewport with the **Cells** chip on (`viewport.setSettings {cellBounds: true}`): loading (Sulfur), loaded (Ochre),
   unloading (gray) squares around the camera; pair with the chip off.
3. Streaming panel's World section with the **cell map** (View > Streaming), one layer selected, sources' circles;
   a second shot with all layers overlaid; a third with a hovered cell tooltip.
4. Cell map while playing (the game's streamer), showing cells loading ahead of the moving player (view bias).
5. The cell map's context menu (Load and pin / Unpin / Show in Content Browser) and a pinned cell.
6. Inspector header "Cell: Vegetation (x, z)" of a selected tree; Hierarchy search `l:Vegetation` and `cell:3,-1`.
7. An unsaved cell outlined in the warning color in the cell map after moving an entity.
8. The Asset panel of a World asset (layers table, Cook button) and the `world.info` / `world.cook` JSON output.
9. Content Browser New > World menu.
10. Export dialog before, during (strata-band progress bar, stage text) and after (Open Folder).
11. The exported folder in the OS file browser, and on Windows the executable's Properties > Details tab (version
    info) and its icon.
12. The exported Open World game running: its loading scene with the progress bar, then the world.
13. The runtime's "No camera to show" message frame (a scene without a primary camera).
14. Launcher (WelcomePanel): template cards, sample cards with pictures, recent projects, "Connect an AI agent".
15. New Project dialog with the basic3d template; the resulting basic3d scene.
16. Project Settings > Game page (title, version, company, copyright, icon).
17. A perf log CSV opened in a spreadsheet with the World* and Physics* columns plotted over an Open World drive.

---

## 5. Rules and pitfalls ("why" boxes)

1. **Never `Scene::Copy` a whole world.** The edited scene is the persistent scene plus loaded cells; play copies
   only that. A full copy would load every cell (memory, time) and defeats streaming. (AGENTS "Worlds"; DevGuide 2574)
2. **Cell membership changes only through `Scene::SetSubSceneOf` and `EditorWorld`.** Undo steps record membership
   (`EntityState::Cell`); editing `SubSceneComponent` directly would leave the undo history and the save plan wrong.
3. **Only `EditorWorld` writes cell documents, through the `DocumentSaver`.** Saves never serialize on the main thread
   and must be ordered (cells before the World document, whose index needs their stamps).
4. **Mark saved only after the World document is written.** A world that does not list a new cell leaves that cell's
   entities out of the game: an "unsaved" state must survive a failed index write.
5. **Worlds stay within 20 km of the origin.** float32 precision ~2 mm there; beyond, physics and rendering jitter.
6. **Scenes that will run load with `SceneLoadOptions::PrepareSystems`.** Otherwise the swap frame builds bodies and
   proxies all at once (a hitch) and the player can fall through ground that has no collision yet.
7. **Loading work draws from the frame's `SceneWorkBudget`.** Several loaders share one frame; separate budgets would
   add up beyond the frame time.
8. **Physics never leaves a body without collision below its growth limit; bodies at the limit wait, never polled.**
   Reserving from the cook's counts avoids growth during play.
9. **Request the World asset every update, never hold a `Ref` across frames.** Residency follows requests; a held
   reference hides use from the eviction logic and prevents reloads being noticed (the `weak_ptr` pattern).
10. **Decisions in a total order.** Hash-map iteration order is not stable; sorting by (priority, distance, key) keeps
    drives identical whatever the thread count, which the tests compare.
11. **Hysteresis is not optional.** Without it a player standing on a border loads and unloads a cell every frame.
12. **Unloads are sliced and deactivate at once.** Entities leave rendering, scripts and physics in the frame the
    unload starts, but destruction spreads over frames: a cell of 25,000 entities would stall a frame otherwise.
13. **Script code never runs while engine state it could invalidate is in use.** Cells unloading call `OnDestroy`
    in slices through `DestroyEntities`; scripts holding entity handles from cells must expect them to go.
14. **Roaming objects belong in the persistent scene.** Moving bodies unload with the cell they loaded with (Manual
    "Limits"); references between cells resolve only while both are loaded.
15. **Entity IDs must be unique across cells and the persistent scene.** A sub-scene whose IDs exist fails to load;
    the cook names shared IDs.
16. **Pruning is off by default.** Scripts can load assets by path, which no reference scan sees; prune only with
    `Export.AlwaysInclude` listing those.
17. **The manifest is untrusted input; it names only files next to it.** A manifest cannot point the runtime to other
    folders.
18. **Fail before writing.** The export checks what it can up front, decodes the icon and stamps the executable before
    writing the pack, so a failed export never leaves a half-new folder next to an old executable.
19. **Saves are keyed by the manifest's Name, never the title.** Renaming the game keeps players' saves.
20. **Window changes apply between frames, and only when they change something.** Mid-frame changes would invalidate
    the swapchain; idempotence lets games apply options every frame.
21. **Only `GameGraphicsService` touches `GraphicsOptions.json`.** One owner of a player's file avoids conflicting
    writes and keeps validation in one place.
22. **Games link no tooling.** Importers and the editor are absent from the runtime (layer table, `NoTooling` test):
    shipped games must read cooked packs only.
23. **Never block a frame on an asset in UI code; draw cached views.** The cell map and cell bounds rebuild only when
    `StateVersion` changes.
24. **Deterministic test runs keep every fixed step.** `--frames`/`--seconds` runs must show the same game time on
    every machine; normal play follows the wall clock with time dilation.
25. **A signed runtime cannot be stamped.** Sign the game after exporting it (PE layout rules).

---

## 6. Hands-on

Game developers:

1. **Make your first world** (easy). `world.create` / New > World; add props on the Props edit layer; watch cells
   stream in the cell map while flying. Proves: persistent scene vs cells, edit layer, streaming around the camera.
2. **Put a streaming source on the player** (easy). Add `StreamingSourceComponent`, change Radius, Layers, Priority;
   observe the cell map during Play. Proves: sources, layer masks, camera fallback.
3. **Tune layers** (medium). Use `world.setLayers` to give terrain larger cells and a longer distance than props; set
   `LoadBeforeStart` on terrain; export and see the game wait for the ground. Proves: layer granularity, start cells.
4. **Prefetch before a teleport** (medium). Script with `World::RequestCellsAround`/`IsLoadedAround`/`Release`
   (as `Samples/OpenWorld/Scripts/Explorer.cpp`). Proves: script-side streaming control and collision readiness.
5. **Toggle a layer from gameplay** (easy). `World::SetLayerEnabled("Props", false)` behind a key. Proves: runtime
   layers.
6. **Cook and read the numbers** (easy). `world.cook`, `world.info`; read MaxBodiesInRadius and warnings; move a cell
   beyond 20 km to see the warning. Proves: what the index is for.
7. **Export and ship** (easy). Set the game's identity and icon, choose a loading scene, export, run the executable,
   find the log and save directories. Proves: the export folder and identity.
8. **Measure a run** (medium). `<Game> --frames 600 --perf-log run.csv --resolution 1280x720`; chart WorldCellsLoaded,
   PhysicsBodies and WorkMs; compare `--quality low` and `ultra`. Proves: profiling a shipped build.
9. **Prune safely** (medium). Export with prune; load an asset by path in a script, see it fail, add it to
   `Export.AlwaysInclude`. Proves: why pruning is off by default.

Engine developers:

1. **Write `CellAt` and `Pack` yourself** (easy) and check them against `World.Asset`'s grid test. Proves: grid math,
   negative coordinates, bit packing.
2. **Add a streaming statistic** (medium): e.g. the number of cancelled loads in `WorldStreamingStats`, shown by
   `world.status` and a perf-log column. Proves: following stats through service, command and log; feature test rule.
3. **Make the concurrency limit a property** (medium): a `WorldComponent` field instead of `c_MaxConcurrentCellLoads`,
   with registration ranges, inspector, serialization and the feature test. Proves: the component checklist.
4. **Replace view bias by a cone of priority** (hard): rank cells inside a source's view frustum higher; keep the
   total order and deterministic tests passing. Proves: the evaluation algorithm and its invariants.
5. **Distance-based hysteresis experiment** (medium): change H and measure decision counts in a drive test like
   `WorldStreamerTests.cpp` 169-213. Proves: understanding thrash.
6. **Design origin rebasing on paper** (hard, essay): what in scenes, physics, rendering and the editor must shift,
   given camera-relative rendering exists. Proves: the precision concept and the engine's coupling.
7. **Sketch HLOD for Strata** (hard, design): where a simplified far representation per cell would live (asset, cook,
   renderer proxy), how it is swapped with hysteresis. Proves: the "not loaded" problem.
8. **Add a runtime command-line option** (easy/medium): e.g. `--start-scene <handle>` for testing; add it to
   `c_Arguments`, `CheckOptions`, usage; test exit codes. Proves: runtime startup flow.
9. **Add a perf-log column group** (easy): a group in `RuntimeApplication::StartPerfLog` with one column; make it write
   the wrong count and see the log fail. Proves: `FramePerfColumnGroup` contract.
10. **Trace a scene switch** (medium): put Tracy zones around `UpdateSceneLoads` and observe `Scene.Load`, background
    release and trim. Proves: non-blocking switching.

---

## 7. Glossary

- **World**: a level split into cells that stream; a persistent scene plus a World asset.
- **World asset (`.stworld`)**: JSON document listing layers, cells and the cooked index.
- **Persistent scene**: the always-loaded scene of a world; holds its `WorldComponent`.
- **Layer**: a grid of cells of one size and one streaming distance (terrain, props...).
- **Cell**: a square of a layer's grid that has content, stored as its own scene file.
- **Cell key (`WorldCellKey`)**: (layer ID, X, Z), packable into 64 bits.
- **Grid origin**: X and Z of the corner of cell (0, 0) of every layer.
- **Streaming distance**: the radius within which a layer's cells load around a source.
- **Distance scale**: per-world multiplier of every layer's distance (quality knob).
- **Streaming source**: a point (player, camera, request) cells load around.
- **View bias**: share of the radius by which cells ahead of a source rank nearer.
- **Hysteresis (H)**: extra keep distance so cells near the edge do not flicker in and out.
- **Wanted cell**: a cell within some source's radius, or pinned.
- **Pin**: a counted reason to keep a cell loaded regardless of sources.
- **Sub-scene / additive load**: a scene loaded into another; a loaded cell is one.
- **`SubSceneComponent`**: runtime-only tag naming the sub-scene of a top-level entity.
- **Slice**: the part of a job done in one frame (entities created/destroyed per update).
- **Scene work budget**: the per-frame time and entity allowance for loading work.
- **Prepared start / `PrepareSystems`**: running systems' preparation hooks before a loaded scene is swapped in.
- **`LoadBeforeStart`**: layer flag: a game waits for these cells (and their collision) before starting.
- **Cook (world cook)**: offline measurement of cells written as the world's index.
- **Index**: per-cell stamps, entity/body counts, bounds, closure bytes, plus MaxBodiesInRadius.
- **Content stamp**: identifier of a document's content, used to know if a cell changed since the cook.
- **Closure (dependency closure)**: an asset and everything it references transitively.
- **MaxBodiesInRadius**: the most physics bodies the sources could keep loaded anywhere.
- **Physics capacity**: the room a physics world reserves for bodies and contacts.
- **Growth limit**: the capacity up to which the physics library grows while bodies are created.
- **Adoption**: taking over already-loaded sub-scenes as cells (prepared start, play copy).
- **Re-celling**: moving an edited entity into the cell its new position lies in.
- **Edit layer**: the layer new top-level entities go into in the editor ("Persistent" by default).
- **Dirty cell**: a cell changed since it was saved.
- **Cell map**: the editor's 2D view of a world's cells and sources.
- **Cell bounds**: viewport overlay outlining active cells.
- **Origin rebasing**: shifting the world so the player stays near (0,0,0) for precision (not in Strata yet).
- **HLOD**: hierarchical level of detail: simplified stand-ins for far content (not in Strata yet).
- **Export**: turning a project into a playable game folder.
- **Asset pack (`.stpak`)**: one file with every shipped asset in stored form, compressed in blocks.
- **Cooked documents**: scenes/prefabs/models in a binary form that loads without JSON parsing.
- **Pruning**: packing only what scenes (and `Export.AlwaysInclude`) use.
- **Patch pack**: a pack mounted over the main one, replacing entries with the same handles.
- **Game manifest (`.stgame`)**: JSON describing an exported game: identity, files, start scene, window, settings.
- **Loading scene**: a scene the runtime plays while the start scene loads.
- **Start scene**: the first scene the game plays.
- **Runtime (`StrataRuntime`)**: the player executable, copied and renamed for each game.
- **Headless**: running without window or GPU (servers, CI).
- **Game identity**: title, version, company, copyright and icon an exported game shows.
- **PE resources**: version info and icons inside a Windows executable.
- **Desktop entry**: Linux `.desktop` file that lists an application in menus.
- **Perf log**: CSV with one row of measurements per frame.
- **Column group**: extra perf-log columns a program adds.
- **Time dilation**: slowing the game instead of catching up when fixed steps cannot keep up.
- **Fixed step**: a simulation step of constant duration; game time is counted in them.
- **Graphics preset**: Low/Medium/High/Ultra/Custom quality bundle; players may override.
- **Launcher**: the editor's start screen when no project is open.
- **Template**: what a new project or scene starts with (`empty`, `basic3d`).
- **Sample**: a finished project shipped with the editor, opened as a copy.

---

## 8. Proposed chapters

1. **Big Worlds: Why Levels Must Stream** (concept, both, M): the memory problem, approaches in the industry
   (whole level, level switches, streaming, World Partition), Strata's choice; float precision and HLOD as open
   problems. Prereqs: scenes and entities, assets and residency.
2. **Building a World in the Editor** (tutorial, game, L, 8 screenshots): create, layers, edit layer, cell map, cell
   bounds, sources, cook, play, export with Load Before Start; Open World sample tour. Prereqs: editor basics,
   components.
3. **Grids, Keys and Layers** (internals, engine, M): `WorldData`, validation, grid math, key packing, file layout and
   derived handles, the index. Prereqs: C++ structs, bit operations, JSON documents.
4. **Sub-scenes and the Frame Budget** (internals, engine, M): additive loads, state machine, slicing, `SceneWorkBudget`
   and adaptive chunks, prepared loads. Prereqs: scene loading, job system. (Coordinate with the Scene area, which
   may own sub-scenes; this chapter can be a focused recap if they do.)
5. **The Streamer: Deciding What Loads** (internals, engine, L): sources, wanted/keep sets, hysteresis, view bias,
   total order, concurrency, failures, adoption, idle cost, determinism tests. Prereqs: 3, 4.
6. **Worlds Meet Physics and Scripts** (internals, both, M): the World system, prepared start, capacity reservation
   and the cook's MaxBodiesInRadius, `IWorldStreaming` and the script SDK, prefetch-before-teleport. Prereqs: 5,
   physics basics, scripting ABI.
7. **Editing a Streamed World** (internals, engine, L): `EditorWorld`, pins, dirty marks through the undo observer,
   re-celling, two-phase save, play copy, recovery, cell map and overlay caching. Prereqs: 5, editor commands and undo,
   document saver.
8. **Shipping a Game: the Export** (tutorial + internals, both, L, 4 screenshots): what an export holds, the export
   state machine, pack planning and pruning, world cooking at export, icon, PE resources, desktop entry, checks before
   writes. Prereqs: asset packs (Asset area), project settings.
9. **The Runtime: a Game Without the Editor** (internals, engine, L): `StrataRuntime` startup, options and exit codes,
   `GameRuntime` (scene loads, loading scene, fixed-step accounting, crash policy), `GameRenderer` fallbacks, window and
   graphics services, headless mode, no tooling. Prereqs: application/layer model, scenes, renderer overview.
10. **Measuring Shipped Games** (tutorial + reference, both, S, 1 screenshot): perf log columns and groups, deterministic
    runs, screenshots, reading the CSV. Prereqs: 9, profiling basics.
11. **The Launcher, Templates and Samples** (tutorial, game, S, 3 screenshots): starting projects, templates' content,
    samples as copies, recent projects, thumbnails. Prereqs: none beyond installing Strata.
12. **Reference: World and Runtime Formats and Commands** (reference, both, M): `.stworld`, `.stgame` v1-v5,
    `GraphicsOptions.json`, `world.*` and `project.*` command list, runtime command line, perf-log columns.

---

## 9. Not determined

- `Scene/SceneSubScenes.cpp` (630 lines) and `SceneLoader.cpp` were read only in outline; the sub-scene slicing
  internals, `FindSubScene`'s binary search and `EntityPrototype` compilation are better covered by the Scene area.
- `EditorWorld::BeginSave`/`FinishSave` (537-758) were read only at the start; their per-document item construction
  is known from the header and Architecture.md.
- `WorldCook.cpp` read only around `ComputeMaxBodiesInRadius` and `Finish`; `WorldCellIO.cpp`, `CellBoundsOverlay.cpp`,
  `UI/CellMap.cpp`, `Panels/StreamingPanel.cpp`, `Panels/SceneHierarchyPanel.cpp` (world strip),
  `Panels/AssetInspectorPanel.cpp` (world view, Cook button), `Panels/ContentBrowserPanel.cpp` (New > World) and
  `Panels/WelcomePanel.cpp` were not read beyond headers/greps.
- `GameExport::Start` (165-322) and `Update` (335-462) were read through their comments only.
- `PEResources.cpp`, `GameIcon.cpp`, `DesktopEntry.cpp`, `ProjectTemplates.cpp`, `RecentProjects.cpp`,
  `ProjectSamples.cpp`, `ProjectThumbnail.cpp`, `ProjectMigration.*` were read through headers only.
- `FramePerfLog.cpp` and `GameGraphicsService.cpp` internals were outlined only (the options-layering logic is long);
  the GraphicsOptions/Quality material probably belongs with the Rendering-quality area.
- `AssetPack*`, `RuntimeAssetManager` and `AssetDependencies` (closure scopes) are referenced from headers; their
  internals belong to the Asset area.
- `CMake/StrataPackaging.cmake`, `.github/workflows/release.yml`, `StrataRuntime.rc.in` and the macOS
  `GLFWApplicationIcon` were not read.
- The exact Architecture.md line numbers of subsections inside "World partition" (marked "~") are estimates from the
  section start (2747); headings inside it are bold paragraphs, not Markdown headings.
- The test bodies were sampled (one streamer test read whole); expected numbers in other tests were not checked.
- `ProjectMigration` was found in the editor folder but its relation to a game's life (opening older projects) was not
  examined.
- Whether `Samples/OpenWorld` currently exports with a cooked index committed (its `Island.stworld` content) was not
  checked.
