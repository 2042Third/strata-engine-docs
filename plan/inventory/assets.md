# Inventory: the asset pipeline (handles, importing, cooking, packs, residency, streaming)

Key: `assets`. Surveyed at `main` 822a7a46 (2026-11-10). All paths are relative to the engine repository
(`G:/GameEngineAI`). Line numbers are those of that commit. "AR" is `Docs/Architecture.md`, "DG" is
`Docs/DeveloperGuide.md`.

What the area is, in one paragraph for the planner: everything between "a file somebody dropped into `Assets/`" and
"bytes on the GPU that a shader samples". In the editor, files get a stable 64-bit handle in a `.meta` sidecar, are
imported on background threads into a cooked "stored form" cached per handle, and their references and bounds are
recorded. An export plans a pack ordered by first use and writes it as zstd-compressed, checksummed 256 KiB blocks. At
runtime (editor and game alike) one base class, `AssetManagerBase`, loads assets asynchronously through a
prioritized, byte-bounded queue (I/O thread read, worker decode, main-thread finalize), keeps memory within per-pool
budgets by least-recently-requested eviction, finalizes GPU uploads in time- and byte-budgeted steps, prefetches
dependencies only into headroom, and lets the renderer's texture streamer keep textures partly resident (mip
streaming). The asset layer itself knows no graphics API.

Size of the area: `Strata/src/Strata/Asset/` holds 46 files, 20,653 lines (the largest: `EditorAssetManager.cpp`
5,109, `GltfImporter.cpp` 2,273, `AssetManager.cpp` 2,070, `BC7Encoder.cpp` 1,435). The streaming and upload half
lives in `Strata/src/Strata/Renderer/` (`Texture.*`, `CookedTexture.*`, `TextureStreamer.*`, `GPUUploadQueue.*`,
`StagingPool.*`, `RendererUploadContext.*`, `TextureFormat.*`, `BlockCompression.*`, `BC7Format.h`, about 5,300 lines).
Tests: `StrataTests/src/Asset/` (23 files, 12,042 lines) plus GPU and streaming tests in `StrataTests/src/Renderer/`.

Releases: the release notes start at 0.3.0 (waves 1-3). The roadmap (`Docs/Roadmap.md`, "Status" and "Waves") dates the
large reworks: `asset-residency` wave 1, `texture-cook-v2`, `pack-v2` and `import-cancel` wave 2, `mip-streaming` wave
3 (all in 0.3.0); `world-io` (import record store, background scans, import memory admission, cooked scenes in packs)
wave 4 (0.4.0); `RemoveSun` and the glTF material extensions wave 6 (0.6.0); color lookups and
`BaseColorFactorsAreSRGB` 0.7.0. Where a feature below says "release: not stated", the documents do not date it; it
existed by 0.3.0 unless noted.

---

## 1. Features

### 1.1 Identity: handles, types, metadata, sidecars

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| Asset handle | `using AssetHandle = UUID`: a random non-zero 64-bit id, text form 16 upper-case hex digits; assets are referenced by handle, never by path | `Asset/AssetTypes.h:12`, `Core/UUID.h` | DG "Asset files" (1638); AGENTS.md "Assets" | not stated |
| Asset types | `enum class AssetType : uint16_t` with 13 types (Scene, Prefab, Model, Mesh, Material, Texture, AudioClip, Font, Skeleton, AnimationClip, AnimationController, World, ColorLookup); values are stored in packs and records, so append only | `Asset/AssetTypes.h:14-31`, names `AssetTypes.cpp:6-43` | AR "Importers and stored forms" (1632) | ColorLookup 0.7.0; others not stated |
| Native extensions | `.stscene .stprefab .stmat .stanimator .stworld`: types the engine writes itself, stored as their JSON source | `GetNativeAssetExtension`, `AssetTypes.cpp:45-55` | DG "Engine-native assets, sub-assets and built-in assets" (1715) | not stated |
| Asset states and priorities | `AssetState` Unloaded / Loading / Ready / Failed; `AssetPriority` High / Normal / Low (prefetch) | `Asset/Asset.h:18-31` | AR "Loading" (1654) | not stated |
| Asset base class | `Asset`: `GetType`, `FinalizeOnMainThread`, `GetMemoryUsage`, `GetFinalizedMemoryUsage`, `IsDataShared`, `GetDetailLevels`, public `Handle` | `Asset/Asset.h:161-193` | DG "Adding an asset type" (1801) | not stated |
| Asset metadata | `AssetMetadata`: handle, type, relative `/` path, parent and sub-asset key (sub-assets), display name, `StoredSize` (bytes a load reads) | `Asset/Asset.h:195-211` | AR "Accounting" (1837) | not stated |
| `.meta` sidecars | `<file>.meta`, JSON `{Strata:{Format:"AssetMeta",Version:1}, Handle, Type, ImportSettings}`; committed with the file; an invalid one is reported and never overwritten (it may hold a merge conflict) | `Asset/AssetRegistration.h:283-304`, `ReadAssetMeta`/`WriteAssetMeta` `AssetRegistration.cpp:64-108`; sample `Samples/Showcase/Assets/Generated/Props/WeatheredSteel_arm.png.meta` | DG "Asset files" (1638) | not stated |
| Sub-assets | Assets an import produces inside another (a model's meshes, materials, textures, skeleton, clips), keyed `"Mesh/0"`, `"Material/2"`, `"Texture/<image>/<usage>/<sampler>"`, `"Skeleton"`, `"Animation/<name>"` | `ImportedSubAsset` `AssetImporter.h:22-32`; keys described `GltfImporter.h:262-282` | DG (1715) | not stated |
| Derived sub-asset handles | `DeriveSubAssetHandle(parent, key)` = `Hash::Combine(FNV1a(key), parent)`, moved out of 0-255: stable across re-imports and machines | `AssetImporter.cpp:264-271` | DG (1715) | not stated |
| Built-in assets | Handles 1-255 reserved; Cube, Sphere, Plane, Quad, Cylinder, Capsule, Cone, Torus meshes (1-8) and DefaultMaterial (0x10), memory assets in every manager; their objects come from factories the renderer module registers; packs cannot replace them | `Asset/BuiltinAssets.h:26-52`, `BuiltinAssets.cpp:15-25,60-120`, factories `Renderer/RendererRegistration.cpp:118-130`, refusal `RuntimeAssetManager.cpp:78-82` | AR "Built-in assets" (1675); DG (1715) | not stated |
| Duplicate `.meta` handles | Files copied with their `.meta` share a handle: the file the records store names keeps it, else the shortest path ("Name - Copy"), the others get new ones | `FindDuplicateHandles` `AssetRegistration.h:319-330`, `.cpp:148` | AR "Importing" (1471), "Import records" (1495) | not stated |

### 1.2 Registries and module seams (how the asset layer stays at the bottom)

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| Loader registry | `AssetLoaderRegistry::Register(type, AssetLoadFunction)`: the module that owns a type registers its loader (stored bytes to `Ref<Asset>`, on a worker); `RegisterPrefix` for partial loads; used before `BeginRegistration` fails `ST_CORE_VERIFY` | `AssetManager.h:192-209`, `.cpp:105-140`. Registrations: Renderer (Texture, Mesh, Material, Font, ColorLookup) `Renderer/RendererRegistration.cpp:85-118`; Scene (Prefab, Model, Scene) `Scene/SceneRegistration.cpp:26-40`; Audio (AudioClip) `Audio/AudioRegistration.cpp:36`; Animation (Skeleton, AnimationClip, AnimationController) `Animation/AnimationRegistration.cpp:20-30`; World `World/WorldRegistration.cpp:34` | AR "Importers and stored forms" (1632); DG "Adding an asset type" (1801) | wave 1 (`module-foundation`), 0.3.0 |
| Importer registry | `AssetImporterRegistry` by extension (case-insensitive, later registrations win); opened only by `RegisterAssetPipeline`, which tools pass as `ModuleRegistrationOptions::AssetPipeline`: shipped games contain no importer | `AssetImporter.h:175-190`, `AssetImporter.cpp:225-262`, `AssetImporters.cpp:159-177` | DG "Importers" (1660) | 0.3.0 |
| Manager extensions | `AssetManagerExtension` (`RefinesPartialAssets`, `OnUpdate`, `ReleaseMemory`, `AddStats`) made per manager from factories in `AssetManagerExtensionRegistry`; the renderer registers `TextureStreamer` | `Asset/AssetManagerExtension.h`, `RendererRegistration.cpp:97-100` | AR "Mip streaming / Manager extensions" (1998 ff.) | wave 3, 0.3.0 |
| Mesh geometry registry | `MeshGeometryRegistry`: physics reads a mesh's positions and triangle list without knowing the renderer's `Mesh` | `Asset/MeshGeometry.h`, `.cpp`; reader `RendererRegistration.cpp:36-62` | not described in the asset sections | not stated |
| The upload seam | `AssetUploadContext` (`Begin`, `Submit`, `EndFrame`) and the `IAssetGraphics` engine service (upload context, frames in flight, device memory budget): finalizers record uploads without the asset layer including NVRHI or Vulkan | `Asset/AssetUploadContext.h:16-49`; renderer side `Renderer/RendererUploadContext.*`; registered `RendererRegistration.cpp:72` | AR "The upload seam" (2095) | wave 3 ("Remove NVRHI from the asset layer"), 0.3.0 |
| Layering | Layer `Asset` (runtime: registry, loading, packs; may include Core only; no `nvrhi/`, `vulkan/`) and Tooling layer `AssetPipeline` (importers, cooker, BC7, HDRSun, editor manager, scanner, pack writer, records) | `StrataTests/Architecture/Layers.json:26-32,113-118` | AGENTS.md "Layers" | wave 1 |

### 1.3 The asset managers

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| `AssetManagerBase` | Registry plus asynchronous loading plus residency; subclasses supply bytes (`ReadAssetData`, `ReadAssetRange`, `IsAwaitingImport`); owned by a `Ref` (pins hold it weakly); thread-safe, finalization on the main thread | `Asset/AssetManager.h:281-878`, `AssetManager.cpp`, `AssetResidency.cpp` | AR "Loading" (1654), "Streaming and residency" (1832) | wave 1 rework |
| Typed accessors | `GetAsset<T>`, `PeekLoadedAsset<T>`, `LoadAssetSync<T>`: null for an invalid handle, unloaded asset or wrong type (`CastAsset` checks `T::GetStaticType()`) | `AssetManager.h:336-352,579-586` | AR "Loading" | not stated |
| `GetAsset` never blocks | Returns the loaded object (or the previous version during a reload) or null, stamps the request, and requests the load | `AssetManager.cpp:330-349` | AR "Loading" (1654); DG "Residency" (1784) | not stated |
| `PeekLoadedAsset` | The loaded object without requesting or counting as used: for debug views that must observe streaming without changing it | `AssetManager.h:327-331`, `.cpp:381` | AR "Streaming"; `StrataEditor/src/Editor/StreamingView.h:125-133` | not stated |
| `TouchLoadedAssets` | Batch "request" of many already-loaded assets under one lock, validated by weak pointers: the renderer's `AssetResolveCache::Replay` for still frames | `AssetManager.h:320-326`, `.cpp:351-379` | AR "Requests and pins" (1852) | not stated |
| `LoadAssetSync` | Blocking load for tools, tests and loading screens, unbudgeted; never from a finalizer | `AssetManager.h:332-335`, `.cpp:388-424` | AR "Loading" | not stated |
| `ReplaceLoadedAsset` | Publishes an in-memory object for a registered asset at once (an edited material while its value is dragged) | `AssetManager.h:372-377`, `.cpp:774-832` | AR "Loading" | not stated |
| Memory assets | `AddMemoryAsset`: assets that exist only in memory (built-ins, runtime-made); never evicted, never unloaded | `AssetManager.h:379-380`, `.cpp:834-871` | AR "Built-in assets" | not stated |
| Hot reload | `ReloadAsset`: re-reads a loaded asset; the previous version keeps serving until the new one is Ready; in-flight loads of the old version are discarded by generation | `AssetManager.h:365-369`, `.cpp:739-763` | AR "Importing" (1471) | not stated |
| Generations | Every (re)registration, reload, unload, eviction and cancel takes a new manager-wide generation; completions and range reads of another generation are discarded | `AssetEntry::Generation` `AssetManager.h:632-635`; checks `AssetManager.cpp:493-495, 576-581, 1101-1117` | AR "Loading" | not stated |
| Source revisions | `GetSourceRevisions`: `Current` changes on registration and every `ReloadAsset` (never on loads or evictions), `Loaded` is the revision the object came from; unique per process; lets caches tell an eviction from a reimport | `AssetManager.h:100-111,370-371`, `.cpp:765-772` | AR "Streaming" (1667); DG "Residency" (1784) | not stated |
| Content and metadata versions | `GetContentVersion`, `GetContentChanges(since)` (the last `c_MaxContentChanges` = 4096 handles) and `GetMetadataVersion`: caches revalidate only what changed | `AssetManager.h:493-507`, `.cpp:1330-1349` | AR "Streaming" (1667) | not stated |
| Active manager facade | `AssetManager::SetActive/GetActive` and static typed accessors; new code that works for a scene uses `Scene::GetAssetManager()` instead | `AssetManager.h:880-917` | AGENTS.md "Assets" | not stated |
| `EditorAssetManager` | The editor's manager: every file under `Assets/` with a known importer is an asset; imports to `<project>/.strata/Cache`; watches files; moves, trash, folders, referencers, pack planning and writing | `Asset/EditorAssetManager.h:188-731`, `.cpp` | AR "Asset pipeline" (1446-1716); DG "Asset pipeline" (1636) | reworked waves 2-4 |
| `RuntimeAssetManager` | Shipped games' manager: assets come from mounted packs; dependencies and bounds from pack tables; `Mount` stacks patch packs (later entries replace earlier ones by handle and reload what they replace) | `Asset/RuntimeAssetManager.h`, `.cpp:13-138` | AR "Mounts" (1714); DG "Asset packs" (1725) | patch packs wave 2, 0.3.0 |
| Awaiting import | `IsAwaitingImport` / `ResumeLoadsAwaitingImport`: a load of an asset whose first import is still running waits in `Loading` instead of failing | `AssetManager.h:594-600`, `.cpp:486-574`; `EditorAssetManager.cpp:3267` | AR "Importing" (1471); DG "Importers" (1660) | wave 4, 0.4.0 |

### 1.4 The loading pipeline

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| Streaming queue | `AssetStreamingQueue`: waiting requests keyed by (priority, -score, request order) in a `std::map`; a repeat raises, never lowers; dispatch while bytes in flight < `MaxInFlightBytes` (128 MiB) and outstanding reads < limit (two per I/O thread); one load always runs when none does; unknown sizes count 1 MiB; `Pump` never recurses | `Asset/AssetStreamingQueue.h:65-148`, `.cpp` (`CanDispatchLocked` 148-156, `Pump` 158-207) | AR "Streaming queue" (1876) | wave 1, 0.3.0 |
| Read on I/O, decode on workers | `DispatchLoad` submits `RunLoad` to `JobSystem::SubmitIO`; the read then submits the decode to `JobSystem::Submit`; both at the request's priority | `AssetManager.cpp:486-546, 583-684` | AR "Loading" (1654); AR "Threading model" (1381) | not stated |
| `AssetLoadData` | What a loader gets: bytes as a span, `TakeBytes` to take them over without a copy (textures, fonts), `IsPartial`/`GetStoredSize` for prefix loads, `IsCancelled` for long decodes | `AssetManager.h:126-179` | AR "Loading"; DG "Adding an asset type" | take-over wave 1 |
| Completion queue and `LoadState` | Jobs push completions into a queue shared through a `Ref<LoadState>`, so a job finishing late never touches a destroyed manager; every path ends in exactly one `PushCompletion` (also on exceptions) | `AssetManager.cpp:184-216, 686-700` | not described as such | not stated |
| Main-thread finalization | `Update` (once per frame) finalizes completions in order within the frame's upload and time budgets (`ProcessCompletions(true)`), then runs extensions, a scheduled trim, eviction and staging release | `AssetManager.cpp:963-1038, 1040-1274` | AR "Loading", "Room before arrival" (1884) | wave 1, 0.3.0 |
| Finalize contract | `AssetFinalizeContext` (upload context, byte, time and staging budgets, deadline, `Prefetched`, `MayWait`, `FirstOfFrame`) and `AssetFinalizeResult` Done / Pending / Failed / AwaitingGPU | `Asset/Asset.h:43-119` | AR "Bounded uploads" (1897); DG "Adding an asset type" | wave 1; AwaitingGPU wave 3 |
| Cancellation | `CancelLoad` (queued requests removed, running ones discarded), `UnloadAsset`; loaders of large documents poll `AssetLoadData::IsCancelled` | `AssetManager.h:358-364`, `.cpp:702-737` | AR "Streaming queue"; DG "Adding an asset type" | wave 1 |
| Exception containment | Loader and read exceptions (bad_alloc, third-party code) become failed loads with a message | `AssetManager.cpp:530-546, 636-683`, `AssetStreamingQueue.cpp:174-188` | not described | not stated |
| Waiting helpers | `WaitForPendingLoads(timeout)`, `HasPendingLoads` (range reads ignored) | `AssetManager.h:389-392`, `.cpp:1303-1328` | AR "Mip streaming / Range reads" | not stated |

### 1.5 Residency (memory budgets, eviction, pins)

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| Memory pools | `AssetMemoryUsage {Cpu, GpuTextures, GpuBuffers}`, `AssetMemoryPool`; each asset reports per pool; the manager keeps totals | `Asset/Asset.h:121-149`, `AssetResidency.h:15-25` | AR "Accounting" (1837) | wave 1, 0.3.0 |
| Budgets | `AssetResidencyBudgets`: GPU textures 50% and GPU buffers 15% of the device's memory budget (VK_EXT_memory_budget), CPU unlimited, 128 MiB in flight, 16 MiB and 4 ms of finalization per frame with 2 ms of upload steps, 32 MiB of staging | `AssetResidency.h:27-71`, `AssetResidency.cpp:31-50` | AR "Budgets" (1846); DG "Residency" (1784) | wave 1; staging and upload ms wave 3 |
| LRU recency orders | One `std::map<RecencyKey{frame, sequence}, handle>` per pool holding only evictable resident assets with memory in that pool; a request moves its node to the end in constant time (`extract` + hinted `insert`); arrivals placed by their latest request | `AssetManager.h:615-625,647-651,831-836`; `AssetResidency.cpp:325-393` | AR "Requests and pins" (1852) | not stated |
| Eviction to budgets | After finalization, per pool over budget, least recently requested first, stopping at the grace window | `EvictToBudgets`/`EvictToFitLocked` `AssetResidency.cpp:512-542` | AR "Eviction" (1862) | wave 1 |
| Eviction protections | Pinned, requested within the grace window (frames in flight + 2), memory and built-in assets, objects referenced outside the manager (`use_count() == 1`), `IsDataShared` (a playing voice) | `CanEvictLocked` `AssetResidency.cpp:428-435`; grace `AssetManager.cpp:197-212` | AR "Eviction"; DG "Residency" | wave 1 |
| Pins | `AssetPin` (RAII, movable, weak manager, counts add up, scoped to one registration); `Pin` also requests the load at High | `AssetResidency.h:95-120`, `AssetResidency.cpp:52-140` | AR "Requests and pins" | wave 1 |
| Trims | `TrimUnused(frames)` evicts what was not requested lately whatever the budgets; `ScheduleTrim(delay, frames, keep)` after a scene switch (`AssetResidency::c_SceneSwitchTrimFrames` = 3), sparing what the new scene's load brought in | `AssetManager.h:465-473`, `AssetResidency.cpp:175-191, 447-467`, `AssetResidency.h:87-93` | AR "Eviction"; DG "Residency" | not stated |
| Room before arrival | `MakeRoomFor`: an arrival in use evicts what its finalized size would push over budget in the pools it needs, reserves its memory until published; with a renderer, waits until the evicted GPU memory is released (frames in flight + 1); arrivals behind a waiting one make room together up to a frame's upload budget | `AssetResidency.cpp:544-571`; `AssetManager.cpp:1121-1172` | AR "Room before arrival" (1884) | wave 1-3 |
| Statistics | `AssetManagerStats` (counts per state, pool totals and budgets, queue, in flight with high water, uploads and finalization ms last frame and max over 120 frames, evictions and eviction checks, cancellations, staging releases, prefetches, partial loads, range reads, mip `Detail`); `GetResidencyInfo`/`GetResidencySamples` cost what is listed (`m_Listed`, `ValidateResidencyIndex`) | `AssetManager.h:31-98, 479-510`; `AssetResidency.cpp:193-320`; `.cpp:1357-1407` | AR "Statistics" (2139) | wave 1 + later |
| Script pins | `Assets::RequestLoad` keeps an asset loaded while the scene plays, `Release` ends it, `GetLoadProgress` loads and reports a closure; host side `ScriptSystem::RequestAsset` | `StrataScriptCore/Include/StrataScript/Scene.h:17-61` | AR "Requests and pins"; DG "Residency" | wave 1 (Release later) |
| Budget controls | `SetResidencyBudgets`; editor `asset.setBudget`, runtime `--asset-budget-mb`, `GameRuntimeOptions::AssetBudgets` | `AssetResidency.cpp:147-167`; `StrataEditor/src/Editor/EditorStreamingCommands.cpp` | AR "Budgets"; DG "Asset streaming commands" (3372) | wave 1 |

### 1.6 Dependencies, references, bounds and group loads

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| Reference scanner | `AssetDependencies::Scan/ScanDocument/ScanEntity/ScanEntities`: scenes, prefabs and models stream through `SceneDocumentReader` and collect every asset property of every registered component (via `ComponentRegistry`) and script fields (`ExtraReferences.VisitJson`); materials their texture maps; controllers their clips; worlds their cells | `Asset/AssetDependencies.h:349-386`, `.cpp:30-235` (`ScanEntityInto` 62-84) | AR "References and bounds" (1590); DG "References and bounds" (1737) | wave 2 (`pack-v2`), 0.3.0 |
| Importer-recorded references and bounds | `ImportResult::References`/`Bounds` and per sub-asset (a glTF mesh's default materials; mesh local bounds) | `AssetImporter.h:22-56` | AR (1590) | wave 2 |
| Normalized references | `NormalizeReferences`: valid handles, each once, never the asset itself; `SetAssetReferences` stores them | `AssetManager.h:546-549,577`, `.cpp:1409-1441` | DG (1737) | wave 2 |
| Dependency queries | `GetDependencies`, `GetDependencyClosure` (breadth first; `AssetClosureScope::All` for packing, `Load` stops at other scenes), `GetBounds` (known before the mesh loads; used to cull unloaded meshes) | `AssetManager.h:516-545`, `.cpp:1443-1495` | AR "References and bounds", "Group loads" (2129) | wave 2 |
| Dependency prefetch | When a requested asset's read completes, its direct dependencies are queued at its priority with score -1 (`c_DependencyPrefetchScore`); only into headroom beside resident + reserved + on-its-way + one in-flight window; unfit arrivals dropped unfinalized; prefetches do not chain; scenes, prefabs and models prefetch nothing; scenes are never prefetched | `AssetManager.cpp:1497-1608`; `AssetManager.h:516-538` | AR "Dependency prefetch" (2107); DG (1737) | wave 2, tightened later |
| Group loads | `RequestLoadWithDependencies`, `RequestLoadGroup`, `AssetGroupRequest` (pins members; `Progress` by stored bytes, never decreasing; `IsComplete`, `HasFailed`, `Cancel`); `IsLoadedWithDependencies` | `AssetManager.h:231-279, 551-560`, `.cpp:1610-1642, 1974-2040` | AR "Group loads" (2129) | wave 2 |
| Reading without loading | `ReadStoredRange`, `ReadStoredData` (blocking; packs decode only covered blocks) | `AssetManager.h:562-567`, `.cpp:1644-1663, 1934-1972` | AR "Group loads" | wave 2 |
| Referencers index | `EditorAssetManager::GetReferencers` (inverse index kept on the main thread); deletes refuse while something uses the asset | `EditorAssetManager.h:425-428, 654-657, 706-709`; editor `Editor/AssetReferences.*` | AR "Folders, the trash and who uses an asset" (1608); DG "Asset files are never lost" (2840) | wave 3 |
| Native documents' references | Engine documents get records of their own (`"Native": true`, per content); changed documents are searched on an I/O job after 500 ms of quiet (`c_ReferenceSearchDelay`), one search per document; saves pass references they already have | `EditorAssetManager.h:437-454, 564-574, 636-648`; `.cpp:2587-2832` | AR "Searches of what documents reference" (1512) | wave 4 |

### 1.7 Importing in the editor

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| Scan | `BeginScan` returns at once: a job walks `Assets/`, prepares each file in batches of 256 (reads `.meta`, picks importer, checks cached import, finds document references), removes unused cache files; `Update` inserts in slices of about 1 ms (clock read every 64 entries); phases Walking / Registering / Applying; `Scan` is the blocking form | `EditorAssetManager.h:214-233`, `.cpp:1375-1500, 1601-1952`; `AssetRegistration.h:233-281` | AR "Importing" (1471); DG "Importers" (1660) | wave 4, 0.4.0 |
| Import cache | `<project>/.strata/Cache/<HANDLE>.bin` per asset and sub-asset; derived data, never committed, safe to delete | `GetCachePath` `EditorAssetManager.cpp:705-708` | DG "Importers" (1660) | not stated |
| Import record store | One append-only file `.strata/Cache/ImportRecords.log`: header line, then lines `<crc32c 8 hex> <compact JSON>`; latest record and path per handle win; torn last line skipped and cut; compacted from memory when dead > live and file > 1 MiB; migrates the older per-asset `.import` files and `AssetIndex.json` | `Asset/ImportRecordStore.h:85-163`, `.cpp` (`FormatLine` 271-274, `Load` 281) | AR "Import records" (1495) | wave 4, 0.4.0 |
| Cache validity | A cached import is current when record version (2), importer `GetVersion`, settings hash and success match, the source is unchanged (size and time, else content hash), and every recorded dependency is unchanged; times too recent to trust are recorded as 0 ("racily clean", as git does) | `LoadCurrentImport` `EditorAssetManager.cpp:1959-2060`; `IsFileCurrent`, `GetRecordableTime` `.cpp:162-193`; `c_ImportRecordVersion` `.cpp:41` | DG "Importers" (1660) | not stated |
| Running an import | `RunImport`: snapshot source state, build `ImportContext`, call the importer, scan references, stage cache files under `.staged<n>` names, then rename them and set the record together under the exclusive file lock, only if not cancelled | `EditorAssetManager.cpp:2062-2236` | AR "Cancelling imports" (1545) | wave 2 + 4 |
| Confined reads | `ReadImportSource`, `ReadImportDependency` (inside the asset directory, symlinks resolved, recorded as a dependency even when missing), `ReadEstimateBytes` | `AssetImporter.h:195-209`, `.cpp:273-343` | DG "Importers" (1660) | not stated |
| Import settings | Importer `GetDefaultSettings` merged with the `.meta`'s `ImportSettings`; `GetSettingsProperties` built with `ImportSettingsBuilder` (Bool, UInt, Float, Enum, `PowerOfTwoLimit`, tooltips); `NormalizeImportSettings` validates (refuses out-of-range, never clamps); `GetInactiveReason` greys a setting out | `AssetImporter.h:104-173`, `.cpp:57-222` | AR "Import settings" (1626); DG "Importers" | wave 2 (`editor-authoring`) |
| Background imports and hot reload | `FileWatcher` reports changes; `Update` re-registers and queues background re-imports, applies finished ones through `ReloadAsset`; `SetImportSettingsInBackground`, `ReimportAssetInBackground`, `IsImportPending`; blocking `SetImportSettings`, `ReimportAsset` for tools | `EditorAssetManager.h:253-304`, `.cpp:2357-2549, 2848-3016, 3164-3338` | AR "Importing", "Import records" | waves 2-4 |
| Import cancellation | Each import is a `BackgroundJob` with an atomic flag (`ImportContext::Cancel`); moves, deletes, re-imports, new settings, `Close` cancel; queued jobs never start, running ones stop at their next check and store nothing; jobs share only `BackgroundWork` | `EditorAssetManager.h:488-503, 593-602`, `.cpp:621-1000` | AR "Cancelling imports" (1545); DG "Importers" | wave 2 (`import-cancel`), 0.3.0 |
| Import memory admission | Imports start only while their estimates fit a budget (a quarter of physical memory, 1-4 GiB): `EstimateImportMemory` from the source head (textures: 20 bytes per pixel from the header; glTF: buffers twice plus images; default 4x size); one over budget runs alone; waiting imports hold no thread | `AssetImporter.h:129-134`, `EditorAssetManager.h:235-245`, `.cpp:714-860`; `TextureImporter.h:97-108`; `GltfImporter.h:303-308` | AR "Import memory admission" (1570); DG "Importers" | wave 4, 0.4.0 |
| External import | `ImportExternal`: copy files/folders on an I/O job (with the files a model names, `FindExternalFiles`), prepare off-thread, import in the background, roll back failed items unless `KeepOnFailure`, `CancelExternalImport`; `ImportExternalFile` blocking | `EditorAssetManager.h:59-136, 306-328`, `.cpp:3340-3751` | AR "Importing external files" (1520) | wave 4 |
| File operations | `MoveAsset`, `MoveFolder`, `DeleteAsset` (tools), `MoveToTrash`/`RestoreFromTrash` (`<project>/.strata/Trash/<UTC time>`, `Trashed.json`), `PurgeTrash` (30 days), `CreateFolder`, `RemoveEmptyFolder`; handles survive | `EditorAssetManager.h:366-402`, `.cpp:4091 ff.` | AR "Folders, the trash..." (1608); DG "Asset files", "Asset files are never lost" | trash wave 3, 0.3.0 |
| Folder index and browsing | `GetFolders`, `HasFolder`, `GetAssetsInFolder`, `GetAssetsBelowFolder`, `ListAssets`, `GetChangeVersion` | `EditorAssetManager.h:404-423` | AR (1608); DG "Asset files" | wave 3-4 |
| Native document writes | `CreateNativeAsset`, `SaveNativeAsset`, `ReserveNativeAsset`, `ClaimDocumentWrite` + `DocumentWriteClaim::Commit` (background saves), `PublishWrittenDocument` | `EditorAssetManager.h:329-365, 733-781`, `.cpp:3753-4072` | DG "No silent data loss" (Editor section) | wave 4 (`world-io`) |
| Unobserved import failures | `TakeImportFailures` (latest 64), shown to the person by the editor | `EditorAssetManager.h:168-176, 300-304` | AR "Importing" | wave 3 |
| Content stamp | `GetContentStamp`: a session-independent fingerprint for on-disk caches such as thumbnails | `EditorAssetManager.h:273-277`, `.cpp:3133` | not in the asset sections | not stated |
| Shared file lock | Background reads hold a shared lock and saves/moves an exclusive one (Windows cannot move a file another handle has open) | `BackgroundWork::FileMutex`, `EditorAssetManager.cpp:621 ff.` | AR "References and bounds" (1590) | wave 4 |

### 1.8 Importers and stored forms

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| Native importer | `.stscene .stprefab .stmat .stanimator .stworld`: validates the JSON with the type's loader and stores the source (`StoresSourceDirectly`) | `AssetImporters.cpp:35-80` | AR table (1632); DG (1715) | not stated |
| Texture importer | PNG, JPEG, TGA, BMP, PSD, GIF, HDR; settings Usage, Compression, Quality, GenerateMips, Filter, Wrap, MaxSize, FlipVertically, FlipGreen, RemoveSun; defaults guessed from file-name tokens; version 5 | `Asset/TextureImporter.h:18-125`, `.cpp` (`GetNameTokens` 254, `GetDefaults` 312, `Decode` 480, `ChooseFormat` 641-666) | AR "Texture cooking" (1718-1830); DG "Textures" (1756) | cook v2 wave 2; FlipGreen v5; RemoveSun 0.6.0 |
| Format choice | Color BC7SRGB (Fast + opaque: BC1SRGB), normal maps BC5, one-channel data BC4 (Grayscale flag), other data BC7, HDR RGBA16F; Uncompressed: RGBA8(SRGB)/R8 | `TextureImporter::ChooseFormat` `TextureImporter.cpp:641-666` | AR "Import" (1738) | wave 2 |
| Texture cooker | Mitchell-filtered mips (sRGB in linear space, alpha-weighted, edges by wrap mode, normal maps renormalized), HDR box filter and half-float clamp, two levels held at a time, encoding in parallel (`ParallelFor`) | `Asset/TextureCooker.h`, `.cpp` (`CookLevels` 275-309, `CookHDRLevels` 311-348) | AR "Mips", "Encoding" (1768-1777) | wave 2 |
| BC7 encoder | Strata's own, from the format's definition (`Renderer/BC7Format.h`): principal-axis endpoints, p-bits, least-squares refits, mode screening; High (all modes) vs Fast (modes 6 and 5) | `Asset/BC7Encoder.h`, `.cpp` | AR "BC7" (1778) | wave 2 |
| HDR sun finder | `HDRSun::Find`/`Remove`: locate the sun in an equirectangular sky, measure its illuminance, paint it out (`RemoveSun`) | `Asset/HDRSun.h`, `.cpp` | DG "Textures" (1756) | 0.6.0 |
| glTF importer | `.gltf`/`.glb` (cgltf, meshoptimizer): entity template + Mesh (LODs with errors, skins), Material (PBR + clear coat, transmission, volume, IOR), Texture, Skeleton, AnimationClip sub-assets; `Scale` baked into content; `FindExternalFiles`; version 11 | `Asset/GltfImporter.h:262-309`, `.cpp` | AR table and Scale note (1632-1652); DG "Importers" (1660) | v10 0.6.0; v11 0.7.0 |
| Audio importer | `.wav .mp3 .flac .ogg` validated by opening as streamed; stored as `STAU` header + encoded file; `LoadMode` Decompressed/Streamed (default by 1 MiB threshold) | `AssetImporters.cpp:82-137` | AR table (1632) | not stated |
| Font importer | `.ttf .otf` stored as-is after `Font::Create` validates (fonts are untrusted input) | `AssetImporters.cpp:140-155` | AR table | not stated |
| Color lookup importer | `.cube` 3D LUTs parsed, resampled to `Size` 17/33/65/File, stored as `STLU` | `Asset/ColorLookupImporter.h` | AR table; DG "Post-processing" | 0.7.0 |
| Cooked texture `STTX` v2 | 40-byte header, mip table, name, then levels smallest first, each 16-byte aligned: the mip tail is one contiguous range after the header; `ParseCookedTexture` validates; v1 still read | `Renderer/CookedTexture.h:17-137`, `.cpp` (`GetMipTailByteRange` 230-257, `ComputeCookedTextureLayout` 339-360) | AR "Cooked form" (1801) | wave 2 |
| Block sizes | `GetMipByteSize` rounds to whole 4x4 blocks; the size every count uses | `Renderer/TextureFormat.cpp:53-65` | AR "Formats" (1722); DG "Textures" | wave 2 |
| BC decode fallback | On devices without BC support the loader decodes blocks on the worker (`Texture::Decompress`, `Renderer/BlockCompression`) | `RendererRegistration.cpp:85-92` | AR "Loading on devices without BC support" (1816) | wave 2 |
| Grayscale and normal conventions | Grayscale bit in texture slots samples `(r,r,r,1)`; normal maps read X, Y and reconstruct Z | `RenderData::c_TextureSlotGrayscale`, `Forward.frag` | AR "Shading" (1828); DG "Material texture slots" (6120) | wave 2 |
| Material texture usage warnings | A texture whose Usage disagrees with its material slot is reported with the `asset.setImportSettings` fix | `Editor/AssetEdit::FindTextureUsageMismatches` | AR "Import" (1738) | not stated |

### 1.9 Asset packs and export

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| Pack format v2 | `.stpak`: 64-byte header ("STPK", counts, tables offset, two CRC-32C), entries from 4 KiB boundaries cut into 256 KiB blocks (zstd, or stored when compression saves under 1/8), tables at the end (88-byte entries, strings, 24-byte blocks, dependencies) | `Asset/AssetPack.h:66-260` | AR "Packs" (1677); DG "Asset packs" (1725) | wave 2, 0.3.0 |
| Validation on open | Header and tables checksummed and checked completely (codecs, ranges, overlapping or non-consecutive blocks, block counts per size, known types, unique handles, finite bounds); totals bounded by the file size (`GetMaxNameBytes`: 16 name bytes per file byte + 1 MiB) | `AssetPack.cpp:179-435` | AR "Packs" | wave 2 |
| Range reads | `ReadRange` decodes only covered blocks; consecutive blocks merged into 2 MiB chunks, three read ahead into lent buffers (at most six kept); stored blocks read straight into the destination; helper jobs decompress while the reader reads on, never running unrelated jobs | `AssetPack.cpp:445-680` (`BlockDecoding` 70-152, `DecodeBlock` 681-744) | AR "Packs" (1677) | wave 2 + later tuning |
| Version 1 compatibility | Header, raw blobs, entry table; read whole; still loads and can still be written | `AssetPackFormat::HeaderV1` `AssetPack.h:245-256` | AR "Packs" | wave 2 |
| Pack writer | `AssetPackWriter::Write`: one pass, temp file renamed into place, blocks compressed in parallel batches of 64, progress, cancel, level 9; zstd's compressor linked only here | `Asset/AssetPackWriter.h`, `.cpp:420-499` | AR "Packs" | wave 2 |
| Pack planning | `PlanAssetPack`: first-use order (start scene's closure breadth first, other scenes' closures, rest by path); `Prune` with `AlwaysInclude`; plan is a snapshot written on an I/O thread | `EditorAssetManager.h:138-157, 456-478`, `.cpp:4202-4360` | AR "Pack layout" (1704) | wave 2 |
| Pack consistency check | `WriteAssetPack` rescans documents and fails if one now references what the plan did not record | `EditorAssetManager.cpp:4292-4345` | AR "Pack layout" | wave 2 |
| Cooking documents for packs | `CookForPack`: scenes, prefabs and models written as `CookedScene` binary (no JSON parse at load), `AdjustSceneSettings` hook | `Asset/AssetPackCook.h`, `.cpp` | DG "Asset files" (1638); AR "Scene documents" (1292) | wave 4, 0.4.0 |
| Patch packs | The game manifest's `PatchPacks` mount after the game's pack | `Project/GameManifest.cpp:41,101-110`; `RuntimeAssetManager::Mount` | AR "Mounts" (1714) | wave 2 |
| Content hash | `AssetPack::HashContent`: FNV-1a per block combined | `AssetPack.h:132-133`, `.cpp:171-177` | AR "Packs" | wave 2 |

### 1.10 Partial residency and mip streaming

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| Prefix loads | A type with a prefix function loads only the head (64 KiB, `c_AssetPrefixHeadBytes`) plus what the function asks for; textures ask for header + resident tail (levels up to 32x32, `Texture::c_ResidentTailDimension`) | `AssetManager.h:181-190, 399-414`; `ReadPrefix` `.cpp:1665-1697`; `Texture::GetLoadPrefixSize` `Renderer/Texture.cpp:396-406`; `GetCookedTexturePrefixSize` `CookedTexture.cpp:323-337` | AR "Partial loads" (1998 ff.); DG "Mip streaming" (1827) | wave 3, 0.3.0 |
| Range reads of loaded assets | `RequestRange`/`PollRange`/`RaiseRange`/`CancelRange` through the same queue and in-flight budget; fail when the asset changed | `AssetManager.h:424-435`, `.cpp:1706-1932` | AR "Range reads" | wave 3 |
| Memory changes without replacement | `UpdateMemoryUsage`: pool totals and recency orders follow a texture that gained or dropped levels | `AssetResidency.cpp:469-489` | AR "Memory changes" | wave 3 |
| Texture streamer | `TextureStreamer` (an `AssetManagerExtension`): views report drawn textures (`ReportView`); wanted level `floor(log2(size * tiling / UVPixels))`; raise at once, drop after 30 s unneeded or under budget pressure; least-needed give levels to most-needed; fade-in 0.25 s; `Hold`, `RequestLevel` | `Renderer/TextureStreamer.h`, `.cpp` (`ComputeWantedLevel` 28-41, `GetUVPixels` 65-80, `RankRaise` 82-88, `OnUpdate` 456-731, `ReleaseMemory` 733-749) | AR "Mip streaming" (1998-2093); DG "Mip streaming" (1827) | wave 3; 30 s idle drop 0.4.0 |
| Raising and dropping levels | `Texture::RaiseLevels`, `DropLevels`, `ContinueLevelChange`: a new GPU texture, resident levels copied on the GPU, new ones uploaded, new bindless slot | `Renderer/Texture.cpp:738-842` | AR "Raising", "Dropping" | wave 3 |
| First-load estimate | `EstimateFirstLoadBytes`: what a load starting now reads (used by `SceneLoader` to fit a scene's closure) | `AssetManager.h:410-414`, `.cpp:268-272` | DG "References and bounds" (1737) | wave 3 |
| Switch | `SetPartialLoads(false)`: whole-texture residency (tests, baselines) | `AssetManager.h:402-409` | DG "Mip streaming" | wave 3 |

### 1.11 GPU uploads

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| Step budget | Steps of at most `c_AssetUploadStepBytes` (4 MiB), sized to bytes, time and deadline left; the frame's first step always goes (one granule at least) | `Asset/Asset.h:43-119` | AR "Bounded uploads" (1897); AGENTS.md "Asset pipeline" | wave 1; time sizing wave 3 |
| Step planning | `GPUUploadQueue::PlanStep`: bytes from measured speed (`BytesPerMs`), a tenth kept in reserve, staging creation time counted (`StagingCreateMs`, `ColdBytesPerMs`) | `Renderer/GPUUploadQueue.cpp:228-277` | AR "Bounded uploads" | wave 3 |
| Texture uploads | `Texture::FinalizeOnMainThread` + `UploadLevels`: small levels stacked in one staging buffer, large levels in power-of-two runs of block rows; CPU copy freed (timed) before publishing; bindless slot and texture-table index allocated at publish | `Renderer/Texture.cpp:464-537, 584-676` | AR "Uploads" (1823), "Bounded uploads" | wave 3 |
| Staging pool | CPU-writable buffers in powers of two from 64 KiB, reused once fenced copies ran; within `StagingBytes`; idle kept up to 16 MiB, all returned after 120 frames idle; `c_MaxPendingBytes` 256 MiB | `Renderer/StagingPool.h`, `.cpp` | AR "Staging" (1965); DG "Streaming and uploads" (6055) | wave 3 |
| Transfer queue (optional) | Uploads on a dedicated transfer queue with queue-ownership transfers; finalizations return `AwaitingGPU`; off by default | `GPUUploadQueue::SetTransferQueue/ChooseQueue/ReleaseToGraphics/AcquireOnGraphics` | AR "The transfer queue" (1943) | wave 3 |
| One batch per update | The manager opens one upload batch per `Update` (finalizations and extension work) and submits it before rendering | `AssetManager.cpp:977-1026`; `RendererUploadContext` | AR "The upload seam" (2095) | wave 3 |
| Back buffer wait late | `Renderer::PrepareBackBuffer`: the GPU waits for the display only before the first back-buffer work, so uploads do not queue behind it | Renderer | AR "Bounded uploads"; DG "Streaming and uploads" (6055) | not stated |
| Per-frame slot resolution | Bindless slots change when levels change: resolve `Texture::GetBindlessSlot` every frame; material data uses the stable `GetTableIndex` | `Renderer/TextureTable.h` | DG "Mip streaming" (1827), "Material texture slots" (6120) | wave 3 |

### 1.12 Tools and user-facing surface

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| Asset commands | `asset.list`, `asset.info`, `asset.import`, `asset.reimport`, `asset.setImportSettings`, `asset.move`, `asset.moveFolder`, `asset.createFolder`, `asset.delete`, `asset.deleteFolder`, `asset.findReferences`, `asset.place`, `asset.stats`, `asset.setBudget` | `StrataEditor/src/Editor/EditorAssetCommands.cpp`, `EditorStreamingCommands.cpp` | DG "Asset streaming commands" (3372), "Asset files are never lost" (2840) | 0.3.0 onward |
| Streaming panel | Pools, queue, uploads, prefetches, mip streaming; sortable table of resident/loading/failed/pinned assets with a Mip column (resident / wanted) | `StrataEditor/src/Panels/StreamingPanel.*` | DG (3372) | wave 2 (`streaming-observatory`) |
| Debug views | Scene view "Streaming" (pending/failed tints, placeholder boxes) and "Mip" (shortfall of mip levels: 0, 1, 2, 3+) views; `viewport.setSettings {debugView: "streaming"|"mip"}` | `StrataEditor/src/Editor/StreamingView.h:52-133` | 0.3.0 release notes | 0.3.0 |
| Content Browser and Asset Inspector | Drop files to import; import settings drawn from `GetSettingsProperties` with inactive reasons | `Panels/ContentBrowserPanel.cpp`, `Panels/AssetInspectorPanel.cpp` | AR "Importing external files", "Import settings" | 0.3.0 onward |
| Thumbnails | Read the cooked header and mip tail by byte range, without loading the texture | `StrataEditor/src/Editor/ThumbnailCache.*` | AR "Cooked form" (1801) | not stated |
| Export | `GameExport` polls `HasPendingImports`, plans, writes the pack on an I/O thread | `StrataEditor/src/Editor/GameExport.*` | AR "Export and the runtime" (4072); DG "Exporting games" (3009) | wave 2 |
| Feature test | Fails when a registered asset type has no asset in `StrataTests/FeatureTest/Assets` | `StrataTests/src/FeatureTest/FeatureTests.cpp:51-110` | AGENTS.md "Testing" | not stated |

### How completeness was checked

- Every one of the 46 files in `Strata/src/Strata/Asset/` is accounted for above: the 23 headers (`Asset`,
  `AssetDependencies`, `AssetImporter`, `AssetManager`, `AssetManagerExtension`, `AssetPack`, `AssetPackCook`,
  `AssetPackWriter`, `AssetRegistration`, `AssetResidency`, `AssetStreamingQueue`, `AssetTypes`,
  `AssetUploadContext`, `BC7Encoder`, `BuiltinAssets`, `ColorLookupImporter`, `EditorAssetManager`, `GltfImporter`,
  `HDRSun`, `ImportRecordStore`, `MeshGeometry`, `RuntimeAssetManager`, `TextureCooker`, `TextureImporter`) and their
  sources, plus `AssetImporters.cpp` (no header). All public members of the headers were read.
- Every `AssetType` value (13) has a loader registration found by grep (`AssetLoaderRegistry::Register(` across
  `Strata/src`: Renderer 5, Scene 3, Audio 1, Animation 3, World 1) and an importer or a sub-asset origin (Mesh,
  Skeleton, AnimationClip come only from glTF; Model from glTF; the native five from `NativeAssetImporter`).
- Every importer registered in `RegisterAssetPipeline` (`AssetImporters.cpp:159-177`) is listed (native x5, Texture,
  glTF, AudioClip, Font, ColorLookup), with its `GetVersion`.
- The one prefix registration and the one manager extension (`RendererRegistration.cpp:93-100`) are listed.
- Every `asset.*` command name found in `StrataEditor/src` (14) is listed.
- The doc sections named in the scope were read in full: AR 1446-2208, DG 1636-1858, 2840-2853, 3372-3392, 6055-6070,
  6120-6140. Their bullets are mapped above.
- Not exhaustively checked: every private helper of `EditorAssetManager.cpp` and `GltfImporter.cpp` (read by function
  list and the central functions only).

---

## 2. Concepts to teach (dependency order)

Each concept: the problem, the approaches engines use, Strata's choice and why, and the usual newcomer mistake.

1. **What an asset is, and source versus runtime form.** Problem: artists produce files in interchange formats (PNG,
   glTF, WAV) that are slow to parse and not what the GPU wants. Approaches: load sources directly at runtime (simple,
   slow, big); convert ahead of time ("cook") into engine formats (Unreal's cooked packages, Unity's Library folder,
   Godot's `.import`). Strata: an importer turns a source into a "stored form" (cooked bytes or, for its own JSON
   documents, the source itself); the editor caches it per handle; games read only stored forms from packs.
   Mistake: thinking the PNG is what ships, or editing cache files.

2. **Identity by handle, not by path.** Problem: renames and moves break path references; two files with the same name.
   Approaches: paths (fragile), GUIDs in sidecars (Unity `.meta`), GUIDs inside the asset (Unreal), content hashes.
   Strata: random 64-bit UUID in a committed `.meta`; sub-assets derive theirs from parent + key deterministically;
   built-ins reserve 1-255. Why: references in scenes stay valid through moves; deterministic sub-handles survive
   re-imports and other machines. Mistakes: moving files without their `.meta` in a file manager (handle lost);
   copying a file with its `.meta` (duplicate handle, resolved by `FindDuplicateHandles`); committing without `.meta`.

3. **Asset types and the registry pattern.** Problem: the asset layer must load meshes and textures without depending
   on the renderer. Approaches: one big switch in the asset system; plug-in registries. Strata: modules register
   loaders, importers, built-in factories, mesh readers and manager extensions into registries opened by the
   composition root; the asset layer includes only Core. Teaches dependency inversion. Mistake: including renderer
   headers from `Asset/` (the layering test refuses it).

4. **Importers, settings and versions (an incremental build system).** Problem: re-importing everything at every start
   is too slow; stale imports are wrong. Approaches: timestamps (make), content hashes (Bazel), import records.
   Strata: a record per asset of importer version, settings hash, source size/time/hash and every dependency file read;
   "racily clean" times recorded as unknown. Why: cheap check on the common path, content compare only when times
   change. Mistake: changing an importer's output without bumping `GetVersion()` (everyone keeps stale caches);
   reading a sibling file directly instead of `ReadImportDependency` (its changes are never noticed).

5. **Texture data for GPUs: mips, color spaces and block compression.** Problem: textures dominate memory and bandwidth;
   minification aliases; sRGB must be filtered in linear space; alpha is coverage; normal maps are vectors.
   Approaches: uncompressed RGBA8, DXT/BC families, ASTC/ETC on mobile, runtime transcoding (Basis). Strata: BC7 for
   color and multi-channel data, BC5 for normals (X, Y; Z reconstructed), BC4 for gray, BC1 at Fast, RGBA16F for HDR;
   Mitchell mips; its own BC7 encoder. Teaches 4x4 blocks, endpoints and indices, why data channels need BC7 (BC1's
   line through RGB space couples channels). Mistakes: computing sizes from bytes per pixel (use `GetMipByteSize`);
   importing a normal map as Color; DirectX vs OpenGL green convention (`FlipGreen`).

6. **File layout for streaming (smallest level first).** Problem: to show something quickly, you want the tiny levels
   first, readable in one contiguous read. Approaches: largest-first (DDS), separate files per mip, tail-first layouts.
   Strata: `STTX` v2 stores levels smallest first, so the mip tail is one range after the header. Mistake: assuming
   level 0 is first in the file.

7. **Asynchronous loading and the main-thread rule.** Problem: disk reads and decoding stall frames; GPU resource
   creation and engine state belong to one thread. Approaches: blocking loads behind loading screens; async with
   callbacks; async with polling. Strata: three stages (I/O pool read, worker decode, main-thread finalize in
   `Update`), `GetAsset` returns null until Ready, code handles "not loaded yet" every frame, no callbacks into engine
   state from workers. Mistakes: calling `LoadAssetSync` in game code; caching a null; expecting a callback.

8. **Futures without futures: generations.** Problem: a load finishes after the asset was reloaded, unloaded or
   cancelled. Approaches: cancellation tokens, versioned requests. Strata: every state change takes a new
   generation from a never-repeating counter; stale completions are discarded at every step. Mistake: publishing
   whatever a job returns.

9. **Priority queues and backpressure.** Problem: a burst of requests fills memory with decoded data the main thread
   has not taken. Approaches: unbounded thread pools, fixed concurrency, byte budgets. Strata: an ordered map keyed by
   (priority, -score, order), raise-never-lower, bytes-in-flight and outstanding-read caps, "one always runs". Teaches
   why a bound on bytes, not on count. Mistake: lowering priorities, or starving one huge asset.

10. **Memory budgets and pools.** Problem: VRAM and RAM run out differently. Approaches: no budget (load everything),
    a single budget, per-pool budgets from the device. Strata: three pools; GPU budgets from VK_EXT_memory_budget
    (50% textures, 15% buffers); `GetFinalizedMemoryUsage` predicts the size after upload. Mistake: counting a texture
    twice (CPU copy and GPU copy) or forgetting block rounding.

11. **LRU eviction with protections.** Problem: what to drop when over budget. Approaches: LRU, LFU, priority classes,
    explicit unload. Strata: per-pool LRU by "request" stamps (requests, not arrivals, mark use), grace window for
    frames the GPU still uses, pins, refcount check (`use_count()==1`), `IsDataShared`. Teaches O(1) touch with
    `std::map::extract`. Mistakes: holding `Ref<T>` across frames (the asset can never be evicted and the budget is
    defeated); not requesting every frame (it gets evicted while drawn).

12. **Pins and group loads (loading screens).** Problem: gameplay needs some assets kept regardless of view; a loading
    screen needs a progress bar. Strata: RAII `AssetPin`; `AssetGroupRequest` pins a breadth-first closure and reports
    progress by bytes. Scripts: `Assets::RequestLoad/Release/GetLoadProgress`. Mistake: pinning everything (that is no
    budget at all).

13. **Dependency graphs.** Problem: a material needs textures; a scene needs meshes; exports must ship what is used.
    Approaches: scan at load time, record at import time, manual manifests. Strata: recorded at import (scanner over
    registered components' asset properties and script fields), carried in pack tables, answered the same in editor
    and game; closures with scopes (`Load` stops at scenes). Mistake: a new document type that references assets
    without recording them (pruned exports miss them, deletes do not warn).

14. **Prefetching without hurting.** Problem: loading dependencies after their owner doubles latency; loading them
    eagerly blows memory. Strata: prefetch direct dependencies of non-document assets only into budget headroom,
    never evict for a prefetch, drop unfit arrivals, no chaining. Measured reasons are in the docs (25-100 MB peaks).
    Mistake: thinking prefetch should follow the whole closure.

15. **Budgeted GPU uploads and staging memory.** Problem: uploading a 90 MB texture in one frame stalls it; staging
    buffers cost memory the driver keeps committed. Approaches: upload rings, copy queues, per-frame byte caps.
    Strata: steps sized by measured speed to a time and byte budget, staging pool with fences and a cap, first step of
    a frame always goes, optional transfer queue. Teaches CPU/GPU timelines and fences. Mistake: one unbounded upload
    in `FinalizeOnMainThread`; waiting on a fence instead of polling.

16. **Room before arrival.** Problem: evicting after allocating means peak = budget + arrivals; GPU memory of evicted
    textures is still in use by frames in flight. Strata: evict first, reserve, wait frames-in-flight + 1 before
    allocating GPU memory, batch waits. Mistake: freeing GPU memory the GPU is still reading.

17. **Partial residency and mip streaming.** Problem: content size exceeds memory; the screen needs only some detail.
    Approaches: whole-texture LRU, virtual texturing / sparse residency (tiles), mip streaming (Unreal, Unity "mipmap
    streaming"). Strata: first loads hold the 32x32 tail; the streamer computes wanted levels from texel density at
    the nearest point (`UVPixels`), raises via range reads into new textures, drops after 30 s or under pressure,
    fades in over 0.25 s. Mistakes: caching a bindless slot; comparing pixels while fades run.

18. **Distribution formats: packs.** Problem: thousands of small files are slow; need compression, integrity,
    random access, patches. Approaches: zip/pak (Unreal .pak/IoStore), Unity bundles, custom archives. Strata:
    block-compressed (256 KiB zstd blocks, stored when gain < 1/8), CRC-32C per block, tables at the end, entries
    ordered by first use, patch packs override by handle. Mistake: compressing already-compressed BC data (costs
    reads, saves 7%).

19. **Untrusted input and corruption.** Problem: files on disk can be truncated or hostile. Strata: every loader
    rejects garbage without crashing; packs validated fully on open, every block checksummed before decoding, sizes
    bounded by file size; sweep tests flip every byte. Mistake: trusting a size field to allocate.

20. **Crash-safe bookkeeping.** Problem: a crash mid-write must not corrupt the project. Strata: append-only records
    with per-line checksums, cache files renamed into place before their record, atomic file writers, staged names.
    Teaches write-ahead ordering.

21. **Cancellation and editor responsiveness.** Problem: closing a project while 17 imports run took 5-12 s. Strata:
    cancel flags checked per block, jobs that share only `BackgroundWork`, nothing waits. Mistake: joining threads on
    close.

22. **Hot reload.** Problem: artists change a file and want to see it. Strata: file watcher, background re-import,
    previous version served until the new one is ready, revisions tell caches it changed.

23. **Bounds before load and culling unloaded meshes** (bridge to the render scene): recorded bounds let the renderer
    cull and request what is visible before it is loaded.

---

## 3. Code worth showing

Small, real, self-contained excerpts at 822a7a46. "Needs" is what the reader must know first.

1. `Strata/src/Strata/Asset/AssetTypes.h:10-31` - the handle alias and the type enum with its "append only" note.
   Teaches: identity by handle; why enum values are part of a file format. Needs: enums, `uint64_t`.
2. `Strata/src/Strata/Core/UUID.h` (whole class, about 25 lines) - a 64-bit id with a reserved null. Needs: classes.
3. A `.meta` file: `Samples/Showcase/Assets/Generated/Props/WeatheredSteel_arm.png.meta` (19 lines). Teaches the
   sidecar and import settings. Needs: JSON.
4. `Strata/src/Strata/Asset/AssetImporter.cpp:264-271` - `DeriveSubAssetHandle`. Teaches deterministic ids by hashing,
   avoiding reserved ranges. Needs: hashing.
5. `Strata/src/Strata/Asset/Asset.h:161-193` - the `Asset` base class. Teaches the contract every asset type meets
   (finalize, memory per pool, shared data, detail levels). Needs: virtual functions, `shared_ptr`.
6. `Strata/src/Strata/Asset/AssetImporters.cpp:35-80` - `NativeAssetImporter`. Teaches the importer interface at its
   simplest (validate with the loader, store as-is). Needs: excerpt 5, interfaces.
7. `Strata/src/Strata/Renderer/RendererRegistration.cpp:81-118` - how the renderer registers the Texture loader (with
   `TakeBytes` and BC fallback), the prefix function and the texture streamer. Teaches registries and dependency
   inversion. Needs: lambdas, `std::function`.
8. `Strata/src/Strata/Asset/AssetImporter.cpp:312-343` - `ReadImportDependency`. Teaches sandboxed reads and recording
   dependencies (also missing ones). Needs: `std::filesystem`.
9. `Strata/src/Strata/Asset/EditorAssetManager.cpp:162-193` - `GetRecordableTime` and `IsFileCurrent`. Teaches
   incremental-build change detection and the racy-timestamp problem. Needs: file times and hashes.
10. `Strata/src/Strata/Asset/EditorAssetManager.cpp:1959-1985` (head of `LoadCurrentImport`) - what makes a cached
    import current. Needs: excerpt 9.
11. `Strata/src/Strata/Asset/EditorAssetManager.cpp:2176-2236` - staging cache files, publishing them and the record
    together under the exclusive lock after a last cancellation check. Teaches crash- and race-safe publication.
    Needs: mutexes, rename atomicity.
12. `Strata/src/Strata/Asset/TextureImporter.cpp:641-666` - `ChooseFormat`. Teaches the BC family choice with the
    comment explaining data channels. Needs: concept 5.
13. `Strata/src/Strata/Asset/TextureCooker.cpp:275-309` - `CookLevels`: encode, then filter the next level, holding two
    levels. Needs: mips.
14. `Strata/src/Strata/Renderer/TextureFormat.cpp:53-65` - `GetMipByteSize`: rounding to 4x4 blocks. Needs: integer
    division rounding up.
15. `Strata/src/Strata/Renderer/CookedTexture.cpp:339-360` - `ComputeCookedTextureLayout`: levels written smallest
    first, aligned. With `CookedTexture.h:17-31` (the format comment). Teaches streaming-friendly layout.
16. `Strata/src/Strata/Asset/AssetManager.cpp:330-349` and `440-484` - `GetAsset` and `RequestLoad`: never block,
    stamp, queue or raise; locks taken one at a time. Needs: mutexes, `scoped_lock`.
17. `Strata/src/Strata/Asset/AssetStreamingQueue.h:119-120` with `AssetStreamingQueue.cpp:148-207` - the key
    `(priority, -score, order)`, `CanDispatchLocked` and the non-recursive `Pump` (lock dropped around dispatch).
    Central algorithm. Needs: `std::map` ordering, tuples.
18. `Strata/src/Strata/Asset/AssetManager.cpp:583-684` - `RunLoad`: read on I/O, prefetch, hand off to a worker,
    loader with a cancel check, exactly one completion on every path. Central algorithm (long). Needs: excerpts 16-17,
    job systems, exceptions at boundaries.
19. `Strata/src/Strata/Asset/AssetManager.cpp:1040-1274` - `ProcessCompletions`: room before arrival, waiting arrivals,
    budgets, Pending/AwaitingGPU, publishing. The central main-thread algorithm (long; show in parts: 1088-1120
    discard stale, 1121-1172 room and waiting, 1174-1222 finalize with budget, 1224-1250 publish).
20. `Strata/src/Strata/Asset/AssetResidency.cpp:325-349` - `TouchLocked`: O(1) LRU move with `extract` and a hinted
    insert. Needs: `std::map` nodes.
21. `Strata/src/Strata/Asset/AssetResidency.cpp:428-445` and `523-542` - `CanEvictLocked`, `EvictLocked`,
    `EvictToFitLocked`. Teaches eviction rules (the `use_count() == 1` check is a good "why" box). Needs: excerpt 20.
22. `Strata/src/Strata/Asset/AssetResidency.cpp:544-571` - `MakeRoomFor`. Needs: excerpt 21.
23. `Strata/src/Strata/Asset/AssetResidency.cpp:104-138` - `Pin`/`Unpin` with weak manager and registration. Teaches
    RAII handles to shared state. Needs: `weak_ptr`.
24. `Strata/src/Strata/Asset/AssetManager.cpp:1450-1473` - breadth-first closure ("the list itself is the queue") with
    the `Load` scope stopping at scenes. Needs: graphs, BFS.
25. `Strata/src/Strata/Asset/AssetManager.cpp:1567-1585` - `FitsPrefetchLocked`: headroom arithmetic with saturation.
    Needs: excerpt 10's budgets.
26. `Strata/src/Strata/Asset/AssetPack.h:66-89` (format comment) and `177-216` (`Header`, `EntryRecord` with
    `static_assert` sizes). Teaches binary file formats. Needs: structs, alignment.
27. `Strata/src/Strata/Asset/AssetPack.cpp:271-292` and `386-414` - checksums and the entry/block consistency checks of
    `Load`. Teaches validating untrusted input. Needs: CRC.
28. `Strata/src/Strata/Asset/AssetPack.cpp:681-744` - `DecodeBlock`: checksum, stored vs zstd, partial blocks.
    Needs: excerpt 26.
29. `Strata/src/Strata/Asset/AssetManager.cpp:1665-1697` - `ReadPrefix` with `Renderer/CookedTexture.cpp:230-257`
    (`GetMipTailByteRange`). Teaches partial loads. Needs: excerpt 15.
30. `Strata/src/Strata/Renderer/TextureStreamer.cpp:28-41` and `65-80` - `ComputeWantedLevel` and `GetUVPixels`: the
    math of mip selection on the CPU. Needs: log2, texel density.
31. `Strata/src/Strata/Renderer/GPUUploadQueue.cpp:228-277` - `PlanStep`: sizing a step to bytes and time with a
    reserve and staging creation cost. Needs: concept 15.
32. `Strata/src/Strata/Renderer/Texture.cpp:584-676` - `UploadLevels`: stacking small levels, runs of block rows,
    power-of-two staging. Needs: excerpts 14, 31.
33. `StrataScriptCore/Include/StrataScript/Scene.h:17-61` - the script-side `Assets` API. For game developers. Needs:
    nothing engine-side.
34. `StrataTests/src/Asset/AssetPackTests.cpp:1008-1030` - the "any single changed byte" sweep. Teaches testing
    parsers of untrusted input.

---

## 4. Figures

Diagrams:

1. **The whole pipeline, editor and game** (data flow): `Assets/<file>` + `.meta` -> importer -> `.strata/Cache/<handle>.bin`
   + `ImportRecords.log` -> (export) plan -> `.stpak` (+ patches) -> `RuntimeAssetManager`; both managers feed the same
   `AssetManagerBase` load pipeline. AR 1450-1466 has an ASCII version to redraw.
2. **Handle derivation and the `.meta` sidecar** (structure): a file, its `.meta`, the cache file named by the handle,
   sub-assets with derived handles, built-ins 1-255.
3. **Asset state machine** (state machine): Unloaded -> Loading (queued / awaiting import / dispatched reading /
   decoding / waiting finalize / finalizing Pending / AwaitingGPU) -> Ready / Failed; Ready -> Unloaded (evict,
   unload); Ready -> Ready (reload serves old until new); generation bump arrows.
4. **The three-stage load timeline** (timeline, three lanes: main thread, I/O thread, worker): `GetAsset` returns null
   frames 1..n, read, decode, completion queue, finalize over two frames (Pending), publish; prefetch of dependencies
   branching at "read complete".
5. **Streaming queue ordering and backpressure** (data structure): the map keyed (priority, -score, order), the
   in-flight bytes gauge vs 128 MiB, outstanding reads, "one always runs".
6. **Memory pools and budgets** (bar chart style): Cpu / GpuTextures / GpuBuffers with resident, reserved, pending,
   in-flight window, budget lines; where prefetches may go (headroom).
7. **LRU recency orders** (data structure): three `std::map`s keyed by (frame, sequence), an asset in two of them,
   `RecencyNodes` iterators, touch = move to end; eviction walks from the front and stops at the grace window.
8. **Room before arrival** (timeline across frames): arrival needs 20 MB, evicts, waits frames-in-flight + 1 for GPU
   release, then uploads; arrivals behind it share the wait.
9. **Import pipeline in the editor** (flow + threads): scan job phases (walk, prepare batches of 256, apply slices),
   background import job (admission, import, stage, publish under lock), main-thread `ApplyImportOutcome`.
10. **Cache validity decision tree**: record version, importer version, settings hash, success, source size/time/hash,
    dependencies -> current / re-import.
11. **Cooked texture layout** (memory layout): `STTX` header, mip table, name, padding, then levels smallest first,
    the resident tail (<= 32x32) as the first-load prefix, the 128x128 tail range, later level ranges read by range.
12. **BC block anatomy** (memory layout): a 4x4 block, BC1 (two endpoints + 2-bit indices), BC7 (mode bits,
    partitions, endpoints, p-bits, indices); why data channels fail in BC1 (colors on one line).
13. **Pack file layout** (memory layout): 64-byte header, entries at 4 KiB boundaries split into 256 KiB blocks
    (zstd or stored), tables at the end (entries, strings, blocks, dependencies) with what points where; first-use
    order shown as a scene's closure laid out front to back.
14. **Pack read path** (flow): range -> covered blocks -> chunks of up to 2 MiB -> read ahead three -> helpers decode;
    stored blocks read in place.
15. **Dependency graph and closures** (graph): scene -> prefabs -> meshes -> materials -> textures; another scene named by
    a script; `All` vs `Load` scope; prefetch edges vs request edges.
16. **Mip streaming loop** (cycle): view reports -> wanted level -> rank -> range read -> new GPU texture -> copy
    resident levels -> upload new -> swap slot -> fade in; drop path under pressure or after 30 s idle.
17. **Upload step planning** (timeline within a frame): 4 ms finalize budget, 2 ms upload budget with 10% reserve,
    steps sized by measured bytes/ms, first step exempt, staging room.
18. **The layer seam** (dependency diagram): Asset layer (Core only) with `AssetUploadContext`/`IAssetGraphics`
    interfaces implemented by the Renderer; AssetPipeline as tooling above.

Screenshots (all from the editor; the Showcase or ThirdPerson samples, or the stress project tests write):

1. **Content Browser with an import running** and a texture's Asset Inspector showing import settings (Usage, Quality,
   MaxSize, an inactive `FlipGreen` with its reason). Open any sample, select a `.png`.
2. **The same texture at Usage Color vs NormalMap vs Data**, or High vs Fast (BC7 vs BC1) zoomed, to show compression
   artifacts. Isolate with `asset.setImportSettings {Quality: "Fast"}`; capture with `viewport.capture` at a close-up.
3. **Mip debug view** of the Showcase while flying: `viewport.setSettings {debugView: "mip"}`; colors 0/1/2/3+ levels
   short; then the same after settling (all green).
4. **Streaming debug view** right after opening a large scene: `debugView: "streaming"`, pending tints and placeholder
   boxes; then after loading.
5. **Streaming panel** with pools, budgets, the queue and the asset table's Mip column ("4 / 2"), with a tight budget
   set via `asset.setBudget {gpuTexturesMB: 32}` so evictions show.
6. **Mip fade-in** (two frames 0.1 s apart, or a short sequence): a texture raising levels near the camera. Turn off
   with `SceneRendererSpecification::FadeTextureLevels` (tests) or compare a still after `TextureTable::GetFadeCount()`
   is 0.
7. **A texture at its resident tail (32x32) vs level 0** on the same surface: tiny budget (`asset.setBudget
   {gpuTexturesMB: 8}`) vs default.
8. **HDR sky with and without RemoveSun** (an `.hdr` sky's `RemoveSun` setting, plus `lighting.extractSun`).
9. **Export dialog** with pruning and AlwaysInclude, and the resulting `.stpak` size in the log.
10. **Delete refused**: `asset.delete` on a used material, the error listing `referencedBy`; then the trash restore via undo.
11. **Status bar assets pill** and `editor.status` assets section (text capture is enough).

---

## 5. Rules and pitfalls (the book's "why" boxes)

1. **Reference assets by handle, never by path at runtime.** Paths change with moves; handles survive. Scripts may find
   by path (`Assets::Find`), which is why exports need `AlwaysInclude` for such assets.
2. **Move, rename and delete through the editor (or move the `.meta` along).** The handle lives in the `.meta`; a file
   manager move loses it and breaks every reference. Deletes go to the trash so undo can restore the handle.
3. **Never overwrite an invalid `.meta`.** It may hold a merge conflict; writing a new handle would silently break
   references.
4. **Bump `GetVersion()` whenever an importer's output changes** (textures: `TextureImporter` and `GltfImporter`).
   Otherwise every project keeps stale caches that look current. An estimate change bumps nothing (it changes no
   output). Adding a key to defaults re-imports everything once (settings hash).
5. **Importers read other files only through `ReadImportDependency`.** It confines reads to the asset directory
   (symlinks resolved) and records the dependency, so a changed image re-imports its model.
6. **Long importers check `ImportContext::IsCancelled` every few milliseconds.** Otherwise closing a project or moving
   a file waits seconds (the 5.6-12 s it once took).
7. **Nothing in the editor waits for a background import; nothing touches files on the main thread.** Frames must
   stay short; jobs prepare, `Update` only inserts (tests check with `FileSystem::GetThreadOperationCount`).
8. **Cache files are renamed into place before their record is set, under the exclusive lock, and only while the import
   is still wanted.** A record never names a missing file; a cancelled import never publishes after a move.
9. **`GetAsset` never blocks; handle "not loaded yet" every frame.** Blocking loads freeze frames; `LoadAssetSync` is
   for tools, tests and loading screens, never from a finalizer.
10. **Hold handles across frames, not `Ref`s, and request what you use every frame.** A held `Ref` makes the asset
    unevictable (`use_count() == 1` check) and defeats the budget; not requesting lets it be evicted while drawn.
11. **Pin what gameplay must keep; release it.** Pins are the only way to keep an asset regardless of use; too many is no
    budget.
12. **Report shared data (`IsDataShared`) and accurate memory per pool (`GetMemoryUsage`, `GetFinalizedMemoryUsage`).**
    Wrong numbers mean wrong eviction, double copies or over-budget devices.
13. **Upload in steps of at most `c_AssetUploadStepBytes` within the context's budget; report bytes.** One unbounded
    upload stalls a frame (a BC7 step once cost 2 ms alone).
14. **Texture sizes come from `GetMipByteSize`, never bytes per pixel.** Blocks are 4x4: a 2x2 BC7 level takes one whole
    16-byte block, not the 4 bytes its 1 byte per texel suggests; the off-by-blocks error breaks validation, staging
    and residency counts alike.
15. **Read cooked textures through `ParseCookedTexture`.** It validates every offset and size; raw parsing invites
    out-of-bounds reads on corrupt data.
16. **Every loader rejects truncated or garbage bytes without crashing; pack and cooked-scene format changes extend the
    corruption tests.** Files are untrusted input (`AssetPackTests.cpp`, `CookedSceneTests.cpp`).
17. **Record references for any new document type** (`AssetDependencies::Scan` or `ImportResult::References`, each valid
    handle once, never itself). Pruned exports, delete checks and prefetches know references only from records.
18. **Resolve bindless slots every frame; never cache them.** Mip streaming replaces a texture's GPU texture and slot.
19. **Stream scene documents; never build a DOM of a whole document.** A million entities' DOM takes gigabytes and
    blocks cancellation (`SceneDocumentReader` with an `EntitySink`).
20. **Prefetches never evict and never chain; documents prefetch nothing; scenes are never prefetched.** Measured: a
    scene's eager prefetch raised peaks 60-100 MB; a World's cells held 12.6 GB instead of 280 MB.
21. **Never free GPU memory a frame in flight may use.** Evicted textures stay frames-in-flight + 1; arrivals wait for
    that release before allocating.
22. **Do not compress what does not compress.** BC data shrinks about 7% under zstd but costs a buffer and a
    decompression; blocks that save under 1/8 are stored and read in place.
23. **The asset layer includes no graphics API.** Record uploads into `AssetUploadContext`; the layering test refuses
    NVRHI/Vulkan headers in `Asset/`.
24. **Built-in handles are reserved.** Packs cannot replace 1-255; sub-asset derivation skips them.
25. **Polling, not waiting.** Fences, range reads and queries are polled per frame; `Renderer::ReadTexture`-style
    blocking is for tests and tools.

---

## 6. Hands-on

For engine developers:

1. **Trace a load** (easy). Put breakpoints or logs in `GetAsset`, `RunLoad`, the decode lambda and
   `ProcessCompletions`; load the Tetris sample and note which thread runs each. Proves: the three-stage model.
2. **Read a `.meta` and a cache record** (easy). Open a sample, find a texture's `.meta`, find its line in
   `.strata/Cache/ImportRecords.log` and its `<HANDLE>.bin`; change a setting and watch a new line appear. Proves:
   identity and cache validity.
3. **Write a cooked-texture inspector** (medium). A small test or tool that calls `ParseCookedTexture` on a cache file
   and prints format, levels, offsets; verify smallest-first layout and the 32x32 tail size. Proves: `STTX` v2 and
   `GetMipByteSize`.
4. **Add a toy asset type** (medium-hard): a "TextAsset" (`.sttxt`, stored as-is) with a loader registered from a test
   module, `GetMemoryUsage` reporting its bytes, a round-trip test and a corrupt-bytes test; add it to the feature test
   assets. Proves: the registry pattern and the "Adding an asset type" checklist (DG 1801).
5. **Add an importer setting** (medium): a boolean to `ColorLookupImporter` via `ImportSettingsBuilder`, with
   `GetInactiveReason`, and bump `GetVersion()`. Verify `asset.setImportSettings` validates it. Proves: settings and
   versioning.
6. **Drive the finalize contract without a GPU** (medium): copy the pattern of `StrataTests/src/Asset/AssetFinalizeTests.cpp`
   (`FakeUploadContext`, `SteppedAsset`) to write an asset that uploads 10 MiB in steps; assert no frame exceeds
   `UploadBytesPerFrame`. Proves: budgets and `Pending`.
7. **Prove LRU order** (medium): with `FakeAssetManager` (`StrataTests/src/Asset/AssetTestUtils.h:133`) and
   `FakeSizedAsset`, set a CPU budget, request assets in a pattern, and predict which are evicted; then hold a `Ref`
   and show it is never evicted. Proves: eviction rules and the `Ref` pitfall.
8. **Streaming queue puzzle** (easy-medium): given a list of requests with priorities, scores and sizes and a 64 MiB
   limit, predict dispatch order; check with a unit test like `StreamingQueueTests.cpp:46`. Proves: queue keys and
   backpressure.
9. **Corrupt a pack** (medium): build a pack in a test with `AssetPackWriter`, flip bytes, confirm `AssetPack::Open`/
   `ReadRange` fail with messages (pattern of `AssetPackTests.cpp:768,1008`). Proves: validation and checksums.
10. **Measure compression** (medium): write a pack of BC7 data and of JSON, read `AssetPackWriteStats`
    (`CompressedBlocks` vs `Blocks`) and explain `c_MinCompressionSaving`. Proves: the stored-block decision.
11. **Wanted level by hand** (easy, math): compute `ComputeWantedLevel` for a 2048 texture tiled 4 times at
    `UVPixels` 300, 1000, 8000; compare with `TextureStreamerTests.cpp:22`. Proves: mip selection math.
12. **Extension stub** (hard): write an `AssetManagerExtension` that only counts `OnUpdate` calls and adds a stat;
    register it in a test. Proves: the extension seam.
13. **Extend the BC7 encoder tests** (hard, optional): measure PSNR of High vs Fast on a gradient with
    `BC7Encoder::EncodeBlock` and the decoder. Proves: block compression understanding.

For game developers:

1. **Import a model and textures** (easy): drag a glTF with its textures into the Content Browser (or `asset.import`);
   inspect sub-assets; place it (`asset.place`). Proves: importing and sub-assets.
2. **Fix a normal map** (easy): import a DirectX-convention normal map named `*_nor_dx_*`, observe `FlipGreen` defaults;
   import one with a bad name, see the material editor's usage warning and apply its fix. Proves: import settings.
3. **Fast vs High** (easy): switch a large albedo to `Quality: Fast`, compare look, stored size (asset.info) and import
   time. Proves: compression trade-offs.
4. **Watch streaming** (easy): open the Showcase, turn on the Mip and Streaming debug views, fly around, open the
   Streaming panel. Then `asset.setBudget {gpuTexturesMB: 32}` and watch evictions. Proves: residency is real and
   visible.
5. **Loading screen** (medium): a script that calls `Assets::GetLoadProgress(levelHandle)` each frame to show a bar,
   then `Game` loads the scene; `Release` after. Proves: group loads and pins.
6. **Keep a sound loaded** (easy): `Assets::RequestLoad` a rarely used clip in `OnCreate`, play it later instantly,
   `Release` at the end. Proves: pins.
7. **Export pruned** (medium): export with pruning; find that an asset only found by `Assets::Find(path)` is missing;
   add it to `Export.AlwaysInclude`. Proves: references and packs.
8. **Safe delete and restore** (easy): try deleting a used material, read the `referencedBy` list, delete anyway with
   force, undo. Proves: the trash and references.
9. **Patch pack** (medium-hard): export, change a texture, build a second pack with only it, list it in the manifest's
   `PatchPacks`, run the game. Proves: mounts by handle.

---

## 7. Glossary

- **Asset**: a piece of content the engine loads by handle (texture, mesh, scene...); in code, a subclass of `Asset`.
- **Asset handle**: a 64-bit random id (`UUID`) naming an asset forever; 0 is null.
- **Asset type**: which kind of asset (`AssetType`), stored as a number in files.
- **Source file / source asset**: the file in `Assets/` an asset comes from.
- **Stored form**: the bytes a loader reads: the cooked data, or the source itself for JSON documents and fonts.
- **Import / importer**: converting a source into its stored form; the class that does it for some extensions.
- **Cook / cooked**: the engine-ready, often binary form an import produces (`STTX`, `STAU`, cooked meshes, `CookedScene`).
- **`.meta` file / sidecar**: the JSON next to each asset file holding its handle and import settings.
- **Import settings**: per-asset options of its importer (Usage, MaxSize, Scale...).
- **Importer version**: a number an importer bumps when its output changes, invalidating caches.
- **Import cache**: `<project>/.strata/Cache/<HANDLE>.bin`, the stored forms of imported assets (derived, not committed).
- **Import record**: what the editor remembers of an asset's last import (versions, hashes, dependencies, references).
- **Import record store**: the append-only `ImportRecords.log` holding all records.
- **Dependency (import)**: another file an import read, whose change re-imports the asset.
- **Dependency / reference (runtime)**: another asset an asset uses (a material's textures).
- **Dependency closure**: an asset with everything it references, transitively.
- **Closure scope**: `All` (ship everything) or `Load` (stop at other scenes).
- **Sub-asset**: an asset produced inside another's import (a model's meshes), with a key like `Mesh/0`.
- **Derived handle**: a sub-asset's handle computed from parent handle and key.
- **Built-in asset**: an engine-provided asset with handle 1-255 (cube mesh, default material).
- **Memory asset**: an asset created in memory, not loaded from storage; never evicted.
- **Engine-native asset**: a JSON document type the engine writes (`.stscene`, `.stprefab`, `.stmat`, `.stanimator`, `.stworld`).
- **Asset manager**: the object that registers, loads and keeps assets (`AssetManagerBase`, editor and runtime subclasses).
- **Registry**: a table modules fill at startup (loaders, importers, extensions) so lower layers need not know them.
- **Loader**: a function turning stored bytes into an asset object on a worker thread.
- **Finalize**: the main-thread step after decoding: create GPU resources, then publish.
- **Publish**: make a finalized object the asset's loaded object (state Ready).
- **Asset state**: Unloaded, Loading, Ready, Failed.
- **Priority / score**: a load's class (High, Normal, Low) and its order within the class.
- **Streaming queue**: the ordered waiting list of loads and range reads with in-flight limits.
- **In flight**: dispatched and not yet finalized or discarded.
- **Backpressure**: refusing to start more work while too much is pending.
- **Generation**: a counter value that identifies one version of a request; stale ones are discarded.
- **Source revision**: a number that changes when an asset's source changes (not when it is evicted).
- **Content version / change list**: counters and handles that tell caches what loaded objects changed.
- **Hot reload**: re-loading an asset whose file changed while the program runs.
- **Residency**: whether (and how much of) an asset is in memory.
- **Memory pool**: Cpu, GpuTextures or GpuBuffers, each with its own budget.
- **Budget**: the most memory (or bytes, or milliseconds) something may use.
- **Device memory budget**: what the GPU driver says the process may use (VK_EXT_memory_budget).
- **Eviction**: dropping a loaded asset to free memory; it loads again on next request.
- **LRU (least recently used)**: evict what was used longest ago first.
- **Recency order**: Strata's per-pool LRU list (a `std::map` keyed by frame and sequence).
- **Request (touch)**: marking an asset as used this frame (`GetAsset`, `RequestLoad`, `Pin`).
- **Grace window**: frames after a request during which an asset is never evicted (frames in flight + 2).
- **Frames in flight**: how many frames the GPU may still be working on while the CPU prepares the next.
- **Pin (`AssetPin`)**: an RAII object that keeps an asset resident while it lives.
- **Trim**: evicting everything not requested recently, e.g. after a scene switch.
- **Room before arrival**: evicting for an incoming asset before it allocates.
- **Reservation**: memory counted for an arrival that made room but is not published yet.
- **Prefetch**: loading something before it is requested; here, an asset's direct dependencies into headroom only.
- **Headroom**: budget left beside what is resident, reserved and on its way.
- **Group load / `AssetGroupRequest`**: loading and pinning a set (a closure) with progress.
- **Upload**: copying data from CPU memory into GPU resources.
- **Upload step**: one budgeted piece of an upload (at most 4 MiB).
- **Granule**: the smallest step unit (a row of blocks, or 64 KiB).
- **Staging buffer**: CPU-writable GPU-visible memory data passes through on its way to a GPU resource.
- **Staging pool**: reusable staging buffers, recycled once the GPU has run the copies.
- **Fence / event query**: a GPU marker the CPU polls to know work completed.
- **Transfer queue**: a separate GPU queue for copies, running beside rendering.
- **Queue ownership transfer**: the release/acquire pair that hands a resource from one GPU queue family to another.
- **Upload context (`AssetUploadContext`)**: the interface finalizers record uploads into; the renderer implements it.
- **Batch**: the uploads recorded during one manager update, submitted together.
- **Bindless slot**: an index into a big descriptor array shaders use to find a texture.
- **Texture table index**: a stable per-texture index materials store; its entry points at the current bindless slot.
- **Mip / mip level / mip chain**: successively halved versions of a texture; level 0 is the largest.
- **Mip tail**: the small levels at the end of the chain (here, up to 32x32 resident, 128x128 as a range).
- **Mip streaming**: keeping only the levels the screen needs resident.
- **Partial load / prefix**: a first load reading only the start of the stored form (header + tail).
- **Range read**: reading a byte range of a loaded asset's stored form later.
- **Wanted level**: the finest level a view needs for a texture.
- **Texel density / `UVPixels`**: how many screen pixels a unit of texture coordinates spans where drawn.
- **Fade-in**: blending newly arrived mip levels in over 0.25 s.
- **Block compression (BC1-BC7)**: GPU texture formats that store 4x4 texel blocks in 8 or 16 bytes.
- **Endpoints / indices / partitions / p-bits / modes (BC7)**: the parts of a BC7 block encoding.
- **sRGB**: the nonlinear color encoding of color images; filtering must happen in linear space.
- **Linear data**: textures holding numbers (roughness, metallic), not colors.
- **Normal map**: a texture of surface direction vectors; stored as X and Y with Z reconstructed.
- **HDR (RGBA16F)**: floating-point textures for light values above 1 (skies).
- **Mitchell filter / box filter**: resampling filters used to build mips.
- **Alpha weighting**: filtering color weighted by alpha so transparent texels do not bleed.
- **`STTX`**: Strata's cooked texture format (version 2: levels smallest first).
- **Asset pack (`.stpak`)**: the single file a shipped game reads its assets from.
- **Block (pack)**: a 256 KiB piece of an entry, compressed with zstd or stored.
- **zstd**: a fast general-purpose compressor.
- **CRC-32C**: a checksum detecting corruption of each block, header and tables.
- **FNV-1a**: a simple fast hash (content hashes, sub-asset keys).
- **First-use order**: laying out a pack so loading the start scene reads front to back.
- **Pruning / `AlwaysInclude`**: shipping only what scenes reference, plus named extras.
- **Patch pack / mount**: an extra pack whose entries replace earlier ones by handle.
- **Cooked scene (`CookedScene`)**: binary scene documents in packs, loaded without parsing JSON.
- **Import memory admission**: starting imports only while their estimated memory fits a budget.
- **Cancellation flag**: an atomic bool importers and loaders check to stop early.
- **Racily clean**: a file whose modification time is too recent to prove it has not changed again.
- **Atomic write / staged file**: writing to a temporary name and renaming into place so readers never see half a file.
- **File watcher**: the OS-backed service reporting changed files for hot reload.
- **Referencers**: the assets that use a given asset (the inverse of references).
- **Trash**: `<project>/.strata/Trash`, where editor deletes go so undo can restore handles.
- **Layer / layering test**: the rule table saying which engine folders may include which.
- **Composition root**: the one place (`Engine::RegisterBuiltinModules`) that registers all modules.
- **Engine service**: an interface a module registers for others to find (`IAssetGraphics`).

---

## 8. Proposed chapters (teaching order)

1. **What is an asset? From files to game content** - concept, both audiences, M. Prerequisites: none. Purpose: explain
   sources vs stored forms, why engines cook, the editor/game split, and Strata's whole pipeline at a glance (figure 1).
   Screenshots: 1.
2. **Names that never break: handles, `.meta` files and sub-assets** - concept + tutorial, both, M. Prerequisites: 1.
   Purpose: reader can explain handle identity, read a `.meta`, move/copy files safely, explain derived and built-in
   handles. Screenshots: 1.
3. **Importing in Strata: importers, settings and the cache** - concept + internals, both (engine-heavy second half), L.
   Prerequisites: 2; threads basics (from the jobs/threading chapter). Purpose: explain the import record, cache
   validity, dependencies, settings properties, background imports, cancellation, admission, hot reload. Screenshots: 1.
4. **Textures for the GPU: mips, color spaces and block compression** - concept + internals, both, L. Prerequisites:
   3; basic graphics (texture sampling) from the rendering primer. Purpose: reader can choose Usage/Quality, explain BC
   formats, the cooker, the BC7 encoder's idea, `STTX` v2 layout and `GetMipByteSize`. Screenshots: 2-3.
5. **Models: what the glTF importer makes** - internals + reference, both, M. Prerequisites: 3, 4; meshes from the
   rendering chapters. Purpose: sub-asset keys, LODs, skins, animations, materials, Scale baking, external files.
   (Coordinate with the animation and mesh chapters.) Screenshots: 1.
6. **Loading without stalling: the asset manager's pipeline** - internals, engine, L. Prerequisites: 1-2; mutexes, job
   system. Purpose: reader can trace `GetAsset` to publish, explain the streaming queue, generations, `AssetLoadData`,
   finalization and the upload seam; write a loader. Screenshots: 0.
7. **Living within a budget: residency, eviction and pins** - concept + internals, both (game devs: the first and last
   sections), L. Prerequisites: 6. Purpose: explain pools, budgets, LRU orders, protections, room before arrival,
   trims, pins and scripts' requests; avoid the `Ref` pitfall. Screenshots: 2 (Streaming panel, tight budget).
8. **What uses what: references, closures, prefetch and loading screens** - concept + tutorial, both, M. Prerequisites:
   7. Purpose: recorded references, closures and scopes, prefetch rules, group loads, `Assets::GetLoadProgress`
   tutorial. Screenshots: 1 (delete refused).
9. **Getting bytes to the GPU: budgeted uploads and staging** - internals, engine, M. Prerequisites: 6, 7; GPU command
   submission basics (rendering primer). Purpose: steps, `PlanStep`, staging pool and fences, transfer queue, one
   batch per update. Screenshots: 0 (diagrams 8, 17).
10. **Mip streaming: texture memory that follows the screen** - concept + internals, both (engine-heavy), L.
    Prerequisites: 4, 7, 9; the render scene chapter for view reports. Purpose: partial loads, range reads, wanted
    levels, raise/drop, fades, slot resolution; debug views. Screenshots: 3-4.
11. **Shipping: asset packs, export and patches** - concept + internals + tutorial, both, L. Prerequisites: 8; file
    formats basics. Purpose: pack format, validation, range reads, writer, planning and pruning, cooked scenes, mounts,
    patch tutorial. Screenshots: 1.
12. **Trusting nothing: corruption, crash safety and cancellation** - concept, engine, S-M. Prerequisites: 3, 11.
    Purpose: why loaders validate, checksums, sweep tests, append-only records, staged publication; a "testing
    parsers" exercise. Screenshots: 0.
13. **Extending the pipeline: adding an asset type, an importer setting or a manager extension** - tutorial, engine, M.
    Prerequisites: 6-11. Purpose: the full checklist (DG "Adding an asset type") as a worked example with tests and
    the feature test. Screenshots: 0.
14. **Reference: asset commands, budgets and statistics** - reference, both, S. Prerequisites: 7. Purpose: `asset.*`
    commands, `asset.stats` fields, budget defaults, runtime flags, Streaming panel columns. Screenshots: 1.

---

## 9. Not determined

- Not read in full: `GltfImporter.cpp` (2,273 lines; read by function list and its header), `BC7Encoder.cpp` beyond
  its header and function list, `EditorAssetManager.cpp` beyond the functions cited (scan preparation, file changes,
  external import and moves were read by outline only), `AssetPack.cpp`'s `ReadBlocks`/`BlockDecoding` beyond the
  first lines, `AssetPackWriter.cpp` and `AssetPackCook.cpp` bodies, `ColorLookupImporter.cpp`, `HDRSun.cpp`,
  `ImportRecordStore.cpp` beyond checksums and `FormatLine`, `TextureStreamer::OnUpdate` (456-731), `GPUUploadQueue`
  beyond `PlanStep`, `StagingPool.cpp`, `RendererUploadContext.cpp`, `Texture::ContinueLevelChange`.
- Not read: the cooked mesh format (`Renderer/Mesh` serialization, "cooked meshes version 3"), `AudioClipAsset`'s
  `STAU` layout, `ColorLookup`'s `STLU` layout, `CookedScene` (belongs to the scene area), `SceneLoader` (how a scene
  load picks a budget-fitting closure), `AssetResolveCache` and `AssetMeshProvider` (renderer area), `ThumbnailCache`,
  `GameExport`, the Streaming panel and Asset Inspector UI code.
- Release dates: the docs date workstreams by wave; per-feature release for small items (most of 1.3 and 1.4) is not
  stated. Whether anything of the area predates 0.3.0 as a release is not determinable (no earlier release notes).
- Exact pixel-level screenshots: not taken (no editor or GPU runs allowed); the screenshot list says how to isolate each.
- Whether GPU visibility feedback (wave 4, "asset requests and mip streaming driven by the GPU's visibility
  feedback") changes the streamer's inputs beyond `ReportView`: belongs to the render scene / GPU-driven area and was
  not traced.
- The Manual (`Docs/Manual/`) has no chapter on assets, importing or export; the user-facing story had to be assembled
  from the commands, the release notes and the skill files (not read: `.claude/skills/strata-editor-automation`,
  `strata-make-a-game`).
