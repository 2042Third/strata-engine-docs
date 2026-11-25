# Inventory: what gets drawn (render scene, batching, culling, GPU-driven path, LOD, skinned meshes)

Area key: `render-scene`. Surveyed at `main` 822a7a46. Paths are relative to the repository root `G:/GameEngineAI`. Line
numbers are at that commit. "AM" is `Docs/Architecture.md`, "DG" is `Docs/DeveloperGuide.md`.

The question this area answers: given a scene of entities, which triangles reach the GPU this frame, from which buffers,
in how many draw calls, and at which level of detail, and how the engine keeps that cost tied to *what is visible and what
changed* rather than to the size of the scene. Strata answers it twice: on the CPU (the reference and the fallback) and on
the GPU (the default where the device can do it). The two paths must agree pixel for pixel, and the tests check that they do.

Where this area ends:
- Lighting, the shadow filters, cascade layout and the post chain belong to other areas. This area covers only *which
  casters are drawn into the shadow maps* and how the shadow draws are culled and cached.
- Asset loading, residency budgets and mip streaming belong to the asset area. This area covers the point where the
  renderer *asks* for assets (priorities, the resolve cache, visibility feedback) and reports what it drew.
- Interpolated (drawn) transforms belong to the scene/timing area. This area covers how the render scene reads them.

---

## 1. Features

Each entry: what it is, where it lives, which document describes it, and the release it arrived in where the documents say.
Releases: 0.3.0 holds waves 1-3, 0.4.0 wave 4, 0.5.0 wave 5, 0.6.0 wave 6, 0.7.0 wave 7. The roadmap's `render-scene` item
is wave 2 (Docs/Roadmap.md:1137) and `gpu-driven-rendering` is wave 4 (Docs/Roadmap.md:1236-1247).

### 1.1 The render scene (CPU side)

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| Render proxy | The renderer's own record of each entity that has a `MeshRendererComponent`, kept in structure-of-arrays form: 3x4 world matrix, local and world bounds, mesh handle and slot, override material and slot, flags, entity ID, instance range | `Strata/src/Strata/Renderer/RenderScene.h:73-565` (members 469-487), `RenderScene.cpp` | AM "Render scene" 2248-2269; DG "Render scene" 4159-4186 | 0.3.0 |
| One render scene per scene | Stored in the EnTT registry's context, created on first use, shared by every renderer of that scene (viewport, capture, thumbnails) | `RenderScene::Get/Find` `RenderScene.cpp:92-117`, `RenderSceneContext` | AM 2251 | 0.3.0 |
| Proxy flags | `Active`, `CastShadows`, `Mirrored`, `Indexed`, `MeshBounds`, `Skin`, `Skinned` | `RenderScene.h:34-49`; mirrored in `shaders/Include/Culling.slang:11-17` | AM 2249-2250 | 0.3.0 (Skin flags with animation, 0.3.0) |
| Signal-driven sync | Listeners on `on_construct/on_update/on_destroy` of `MeshRendererComponent` and `SkinComponent` queue the entity once; `Sync` reads the queue, then the scene's world-transform change log | `ConnectListeners` `RenderScene.cpp:130-140`; `QueuePending/DropPending` 209-236; `Sync` 316-401 | AM 2252-2261; AGENTS.md "Scene caches and the transform contract" | 0.3.0 |
| Full refresh fallback | When the scene's transform log no longer reaches back, every proxy is compared | `FullRefresh` `RenderScene.cpp:403-416`; `RenderSceneStats::FullRefreshes` | AM 2254 | 0.3.0 |
| Drawn transforms | Proxies are placed where the scene draws the entity (pose provider's render transform, then the interpolated transform, then the world matrix) | `GetDrawnTransform` `RenderScene.cpp:418-428`; interpolated set re-walked in `Sync` 362-378 | DG "Render scene" 4155-4158; DG "Interpolation" 2468 | not stated |
| Render transforms | A pose provider that may not write the scene (the editor's pose preview) can list entities drawn elsewhere (attachments at joints) | `UpdateRenderTransforms` `RenderScene.cpp:430-461`; `ISkinningPoses::GetRenderTransforms` in `Scene/SceneServices.h` | AM 2355-2359 | not stated (0.4.0 "authoring that behaves as shown", Releases/0.4.0.md:83) |
| Proxy placement | Bounds from transform and mesh layout; mirrored when the determinant is negative; zero-scale or non-finite transforms are not drawable; spatial index membership | `UpdateProxyPlacement` `RenderScene.cpp:647-711` | AM 2248-2250 | 0.3.0 |
| Dense mesh and material slots | Each distinct mesh/material in use gets a small integer slot shared by its users; slots freed with the last user; `GetSlotsVersion` changes when slots are taken or let go | `AcquireMesh/ReleaseMesh/AcquireMaterial/ReleaseMaterial` `RenderScene.cpp:713-835`; `MeshEntry`, `MaterialEntry` `RenderScene.h:314-375` | AM 2360 | 0.3.0 |
| Material users | Find the proxies that may draw a set of material slots (by override, and through their meshes' submesh materials) without walking every proxy | `CollectMaterialUsers` `RenderScene.cpp:897-915` | AM 2496 | not stated |
| Mesh layouts | Bounds, submeshes and submesh materials learned from the loaded mesh, kept through eviction, forgotten when the source is reimported while unloaded | `SetMeshLayout` 916, `UpdateMeshLayouts` 962, `CheckMeshLayout` 1019, `ForgetMeshLayout` 1063 (`RenderScene.cpp`) | AM 2299-2311 | 0.3.0 (revisions later; not stated) |
| Recorded bounds before load | Bounds the asset database recorded (import records, a pack's bounds table) place a mesh before it ever loads | `RenderScene::ResolveUnloadedBounds` `RenderScene.cpp:264-269` | AM 2312-2316 | not stated |
| Unknown bounds are visible | A mesh with no layout and no recorded bounds gets placeholder bounds (unit box around the entity) and is requested as if in view while any user is active | `GetPlaceholderBounds` 270; `GetMeshesWithoutBounds`; `SceneRenderer::MarkMeshesWithoutBounds` `SceneRendererExtraction.cpp:330-342` | AM 2316-2323 | not stated |
| Instance data | One 64-byte `InstanceData` (3x4 world rows, material slot, entity ID, flags, skin palette) per submesh of each proxy, in one persistent array | `RenderData::InstanceData` `SceneRenderData.h:187-199`; `RebuildInstances/WriteInstances/AllocateInstances` `RenderScene.cpp:1079-1166` | AM 2360-2366; DG "Batching" 4215-4219 | 0.3.0 |
| Instance limit | At most 2^27 instances (what a draw-list entry can name); proxies beyond get none, logged once | `c_MaxRenderInstances` `SceneRenderData.h:206-208`; `SetInstanceLimit` `RenderScene.cpp:1156` | DG 4220-4221 | not stated |
| Three change logs | Bounded (65,536) version-stamped logs of instance, proxy and palette changes that readers (the GPU copy, shadow cache) follow; overflow means "read everything" | `RecordInstanceChanges/RecordProxyChange/GetProxyChanges/GetInstanceChanges` `RenderScene.cpp:1168-1239`; palettes 1462-1489 | AM 2362-2365; DG "Render scene" 4187-4202 | 0.4.0 (proxy log with the GPU copy) |
| Debug validation | Debug builds rebuild the proxies from the scene and compare after syncs (every sync up to 1,024 proxies, amortized above) to catch unsignaled writes | `Validate` `RenderScene.cpp:1491-`; `c_ValidatedProxiesPerSync`, `AmortizedCheck` `RenderScene.h:182-192`; `Sync` 386-399 | AM 2256-2259 | not stated |
| Prepared loads | A loaded scene builds its proxies in chunks of 2,048 within the frame's `SceneWorkBudget` before it is shown, then fills its GPU copy within 16 MiB a frame | `RenderScene::Prepare`, `PrepareLoadedScene` `RenderScene.cpp:280-315`, `RenderScene.h:164-180` | AM 2261-2269, 2379-2386 | not stated |
| Clones at play start | `Scene::Copy` clones the render scene member by member (large arrays in parallel) so the play copy's first frame builds no proxy; renderer state carries over | `CopyIntoScene` `RenderScene.cpp:142-180`; `SceneRenderer::PrepareExtraction` `SceneRendererExtraction.cpp:136-204` | AM 2282-2298 | 0.4.0 (Roadmap.md:425) |
| Point and spot light records | Lights are render-scene records too, with their own change log and GPU buffer | `Renderer/RenderLights.h`, `RenderScene::GetLights` | AM 2270-2281; DG "Lights, shadows and HDR" 4508 | 0.4.0 (GPU light culling) |
| Statistics | `RenderSceneStats` (proxies, indexed, instance slots, meshes, materials, updates, mirrored, skin, posed, palette joints, clone time) | `RenderScene.h:51-71` | AM 2589-2595 | 0.3.0+ |

### 1.2 Spatial index and CPU culling

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| Loose two-level grid | 32-unit cells keyed by the box center, cell bounds = union of their objects, 8x8x8 blocks of cells, objects longer than 4 cells in a separate list | `Renderer/SpatialIndex.h` (all), `SpatialIndex.cpp` | AM "Render scene" 2408-2412 | 0.3.0 |
| Exact queries | Frustum, convex planes and sphere; blocks/cells wholly inside are taken whole, straddling ones tested per object with the brute-force test | `SpatialIndex::Query` `SpatialIndex.cpp:406-438`; `IntersectsPlanes/ClassifyPlanes/ClassifySphere` 56-107 | AM 2410-2411 | 0.3.0 |
| Constant-time edits, lazy shrink | `Update` grows bounds at once; `Refresh` (every `Sync`) tightens stale cells and blocks | `Update` 303-345, `Refresh` 371-404 | AM 2412 | 0.3.0 |
| View frustum culling (CPU) | `CullView`: `QueryFrustum`, screen fraction per visible proxy (parallel chunks), request marks; prefetch sphere | `SceneRendererExtraction.cpp:249-328` | AM 2223-2224 | 0.3.0 |
| Screen-size culling | Proxies below `MinProjectedPixels` (quality row, 0.5 px at Medium) are not drawn, on both paths | `GatherDraws` 973-977; `Cull.comp` 482-489; `RendererQuality.h:140-143` | DG "GPU-driven path" 4264-4266; Manual/Graphics.md:22 | 0.4.0 |
| Shadow caster search | Cascade boxes queried with `QueryPlanes` (a job per cascade), exact light-space test in parallel chunks, sub-texel casters left out | `FindShadowCasters` `SceneRendererExtraction.cpp:418-613`, `GetCascadeMask` 614 | AM 2227-2230; DG 4531-4534 | 0.4.0 (parallel, sub-texel) |
| Off-view casters for animators | `CanShadowView` decides whether an off-view skinned caster's shadow can fall into the view, so its animator keeps animating | `SceneRendererExtraction.cpp:636-678` | AM 2348-2352 | not stated |

### 1.3 Requests, the resolve cache and residency at draw time

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| Requests follow visibility | In view: High priority above 5% of viewport height, Normal below; within 100 units: Low (prefetch); off-view shadow casters only if resident | Use bits `c_UseView/High/Prefetch/Shadow` `SceneRendererExtraction.cpp:41-48`; `ResolveAssets` 701-743; spec fields `HighPriorityScreenFraction`, `PrefetchDistance` `SceneRenderer.h:182-189` | AM 2413-2418; DG 4162-4164 | 0.3.0 |
| Asset resolve cache | One asset-manager lookup per distinct handle per frame; references released when the frame ends; the manager held only during the frame | `Renderer/AssetResolveCache.h/.cpp` (`LookUp` 98-130) | AM 2418-2424; DG 4164-4166 | 0.3.0 |
| Recording and replay | A still frame replays the previous frame's lookups in one locked call (`TouchLoadedAssets`) | `AssetResolveCache::BeginRecording/EndRecording/Replay`; `SceneRenderer::ReuseResolvedMaterials` `SceneRendererExtraction.cpp:745-777`, `ResolveMaterials` 779-843 | AM 2433-2451; DG 4166-4170 | not stated (perf numbers in AM 2449-2451) |
| Default material fallback | Unloaded materials draw as the default material; unloaded meshes are skipped | `ResolveMaterials` 821-835 | DG "Streaming and uploads" 6057-6059 | 0.3.0 |
| Visible materials and textures published | Each frame publishes materials drawn with their largest pixel size and UV pixels, and their loaded textures, for mip streaming | `GetVisibleMaterials/GetVisibleTextures`; `GatherDraws` 1111-1123 | AM 2590-2592 | 0.3.0 |
| Drawn only when resident | A new proxy is drawn only once its GPU record and instances are uploaded | `RenderSceneGPU::IsResident`; checked in `GatherDraws` 968 | DG 4190-4194 | 0.4.0 |

### 1.4 Batching and draw submission (CPU path)

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| Parallel extraction | Draws gathered in chunks of 2,048 proxies on the job system, merged in chunk order (thread-count independent) | `ExtractionChunk` `SceneRenderer.h:1221-1239`; `ForEachChunk` `SceneRendererExtraction.cpp:113-127`; `GatherDraws` 929-1124 | AM 2580-2581; DG 4214-4215 | 0.3.0 |
| 64-bit sort key | Cascade (3 bits), alpha mask, mirrored, double-sided, skinned, mesh slot (20), submesh (16), LOD (5), material (16, only when not batching across materials) | `Renderer/SceneDrawKey.h` | AM 2581-2582 | 0.3.0 |
| Byte-skipping radix sort | Stable LSD radix sort that skips bytes equal in every key | `Core/RadixSort.h`, `Core/RadixSort.cpp:14-67` | AM 2582-2583 | 0.3.0 (byte skip later, Roadmap.md:172) |
| Material-free instancing | Material is not in the batch key; shaders read `u_Materials[instance.MaterialIndex]`; `BatchAcrossMaterials` off splits by material for comparison | `SceneRendererSpecification::BatchAcrossMaterials` `SceneRenderer.h:190-194`; `GatherDraws` 1028 | AM 2584-2586; DG 4212-4214 | 0.3.0 |
| Batches and draw list | `BuildBatches` decodes runs of equal keys into `SceneDrawBatch`es; the draw list holds one entry per drawn instance | `SceneRendererExtraction.cpp:845-869`; `SceneDrawBatch` `SceneRenderer.h:791-806` | DG 4216-4218 | 0.3.0 |
| Draw-list entry | Instance index in the low 27 bits, LOD fade code above | `MakeDrawEntry` `SceneRenderData.h:201-216` | DG 4220-4221 | 0.4.0 (fade code) |
| Transparent draws | One draw each, back to front; glass (transmissive) first, unblended, writing depth | `TransparentDraw` `SceneRenderer.h:1134-1147`; sort in `GatherDraws` 1078-1106 | AM 2586-2587; DG "Clear coat and glass" 6083-6090 | 0.3.0 (glass 0.6.0) |
| Changed-range uploads | Draw lists and indirect arguments upload only the range between the first and last changed entry | `UploadChangedRange` `SceneRendererExtraction.cpp:1271-1302`; `UploadSceneData` 1323-1331 | AM 2589-2590 | 0.3.0 |
| Indirect arguments per batch | `BuildDrawArguments` writes `DrawIndexedIndirectArguments` at each mesh's place in the geometry pool | `SceneRenderer.cpp:2042-2070` | AM 2235 | 0.4.0 |
| Buckets of pipeline state | Consecutive batches of one `PipelineKey` and vertex arena share one `setGraphicsState`, drawn with one `drawIndexedIndirect` (or per batch without `multiDrawIndirect`); split at `maxDrawIndirectCount` | `DrawBuckets` `SceneRenderer.cpp:2072-`; `PipelineKey` `SceneRenderer.h:1107-1119`; `IndirectDrawMode` 104-110 | DG "Batching" 4244-4251 | 0.4.0 |
| Pipeline cache by key | `GetScenePipeline` builds and caches a pipeline per key (pass, double-sided, mirrored, skinned, velocity, surface) | `SceneRenderer.cpp:2424-` | DG 4244 | 0.3.0+ |
| Geometry pool | All meshes in shared buffers: Static arena (12 B positions + 36 B attributes), Skinned arena (+16 B skin stream), one 32-bit index arena; stable `GeometryHandle`, offsets move under compaction; growth by GPU copy | `Renderer/GeometryPool.h/.cpp`; `Core/RangeAllocator` | DG "Batching" 4228-4243 | 0.4.0 (Releases/0.4.0.md:45) |
| Culling tables in the pool | Per handle a `GeometryEntry`, per submesh a `GeometrySubmesh`, per level a `GeometryLOD` draw record | `GPUSceneData.h:33-67`; `GeometryPool::SetLayout/RecordTableUploads` | DG 4240-4243 | 0.4.0 |
| Vertex layouts | Each scene vertex shader reads exactly the attributes of its layout (Mesh, SkinnedMesh, Shadow, SkinnedShadow) | `Renderer/SceneVertexLayouts.h` | (code comment only) | not stated |

### 1.5 Levels of detail

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| Screen fraction | Projected bounding-sphere diameter over viewport height (perspective and orthographic) | `LODSelection::GetScreenFraction` `LODSelection.cpp:10-17`; GPU copy `Include/Culling.slang:215-223` | DG "Overlays" 6168-6175 | 0.3.0 |
| Halving rule | Levels without errors: LOD n below `LODThreshold / 2^(n-1)`; exact doublings so CPU and GPU agree | `SelectLOD` `LODSelection.cpp:19-34`; `Include/LODSelection.slang:4-21` | DG 6170-6172 | 0.3.0 |
| Error rule | Generated levels carry `MeshLOD::Error`; the coarsest level whose projected error is at most `LODErrorPixels` (quality row: 2/1/1/0.5 px) is drawn | `SelectLODByError` `LODSelection.cpp:60-87`; `Include/LODSelection.slang:23-38`; `RendererQuality.h:137-139`; `MeshUtils::GenerateLODs` | DG 6170-6175; Manual/Graphics.md:21 | 0.4.0 |
| LOD cross-fades | When a view instance's level changes, both levels draw for 16 frames with complementary 4x4 ordered-dither masks; prepass and forward discard by the same test so EQUAL depth holds | `UpdateLODFade` `LODSelection.cpp:99-145`, `IsLODFadeDrawn` 153-159; shader copies `Include/LODSelection.slang:40-91`, `Include/Scene.slang:155-166`; `DepthPrepass.frag.slang:73`, `Forward.frag.slang:452`; `LODFadeState` `GPUSceneData.h:69-78` | DG "Batching" 4220-4227 | 0.4.0 (Releases/0.4.0.md:47-48) |
| LOD criteria | `LODCriteria` (threshold, error threshold, viewport height) a renderer exposes so tools show the drawn level | `SceneRenderer.h:119-125`; `LODSelection.h` | DG 6168-6169 | 0.4.0 |
| Editor LOD debug view | Tints entities by the level drawn and reports error pixels per level | `StrataEditor/src/Editor/StreamingView.cpp:283-316` (`BuildLOD`); `viewport.setSettings {debugView:"lod"}` (`EditorViewportCommands.cpp:1131-1135`) | Releases/0.3.0.md:31 | 0.3.0 |
| GPU/CPU LOD agreement test shader | `Debug/LODSelection.comp` runs the shader's selection for 10,000 fractions | `Strata/shaders/Debug/LODSelection.comp.slang`; test `GPU.Renderer.LODSelection` | DG 6173-6174 | 0.4.0 |

### 1.6 The render scene's GPU copy (RenderSceneGPU)

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| Shared mirror | Instances, palettes, a 64-byte `GPUProxy` culling record per proxy, light records, mesh table, material data and flags; one per render scene, shared by its renderers, keyed by id | `Renderer/RenderSceneGPU.h:48-363`; `RenderSceneGPUCache` 300-363; `GPUProxy` `GPUSceneData.h:13-31` | AM 2367-2393; DG 4187-4208 | 0.4.0 |
| Log-driven update | Follows the three change logs; uploads runs of changed elements through staging (`GPUUploadQueue::RecordSceneUpload`) in its own command list executed at once | `RenderSceneGPU::Update` `RenderSceneGPU.cpp:604-895` | AM 2370-2373 | 0.4.0 |
| Residency budget for new proxies | New proxies upload oldest first within `NewInstanceBytesPerFrame` (16 MiB), at least one per frame; destroyed records cleared at once | `Update` 737-782; spec `SceneRenderer.h:208-211`; stats `DeferredInstanceBytes`, `DeferredProxies` | AM 2373-2378 | 0.4.0 |
| Growth by GPU copy | Buffers grow by copying into larger ones; old ones released deferred | `EnsureCapacity` `RenderSceneGPU.cpp:202-277` | AM 2378-2379 | 0.4.0 |
| Asset tables | Mesh table (GeometryHandle per mesh slot, skinned-arena bit) and material data/flags per material slot, built only for content changes and slot changes; reverse index texture -> materials | `UpdateAssetTables/BuildMeshEntry/BuildMaterial` `RenderSceneGPU.cpp:412-603` | AM 2394-2407; DG 4203-4208 | 0.4.0 |
| Clone mirror | A clone's mirror is copied on the GPU when the source holds exactly the clone's versions | `CreateClone`, `HoldsVersions` `RenderSceneGPU.cpp:70-118`; `RenderSceneGPUCache::Get` 911-940 | AM 2290-2296 | 0.4.0 |
| Release and recycle | Mirrors go with their scene or after 300 unused frames; a small released mirror's buffers (<= 1 MiB) are adopted by the next mirror with their buffer version | `RenderSceneGPUCache::BeginFrame/Release/ReleaseRecycled`; `AdoptBuffers/TakeBuffers` | AM 2386-2393; DG 4194-4197 | 0.7.0 (Roadmap.md:1512, wave 7) |
| Write logs for readers | Instance and palette write ranges by process-unique write version (for motion histories) | `GetInstanceWrites/GetPaletteWrites`, `WriteLog` `RenderSceneGPU.h:181-246` | DG "Motion vectors and TAA" 4366-4370 | 0.6.0 |

### 1.7 The GPU-driven path

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| Mode switch | `GPUDriven` Auto (devices with `drawIndirectFirstInstance`) or Off; fallback when shaders or resources cannot be set up | `GPUDrivenMode` `SceneRenderer.h:112-117`, spec 151-156; `IsGPUDriven` `SceneRendererGPUDriven.cpp:164-168`; `CreateCullResources/ReleaseCullResources` 196-335 | AM 2452-2457; DG "GPU-driven path" 4255-4263 | 0.4.0 |
| Cull.comp | One thread per proxy: active/indexed, frustum (camera-relative), screen size, per instance material and LOD, emit into (bucket, LOD record) counts; `ST_CULL_SHADOW` variant (`Scene/CullShadow.comp`) for cascades and local shadow views | `Strata/shaders/Scene/Cull.comp.slang` (627 lines); `Strata/CMakeLists.txt:96,192` | AM 2457-2462 | 0.4.0 (local shadow views 0.6.0) |
| Count / build / write | Counting pass, `CullBuild.comp` gives each record a draw-list range and an indirect draw slot, writing pass places instances | `RunGPUCulling` `SceneRendererGPUDriven.cpp:923-1015`; `Scene/CullBuild.comp.slang` | AM 2465-2467 | 0.4.0 |
| Buckets | Pipeline state x vertex arena: mirrored, double-sided, geometry (Static, Skinned arena bind pose, posed), second-phase bit; shadows add alpha-mask and cascade; local views last; only buckets the frame can have get dense indices | `MakeViewBucket/MakeShadowBucket/MakeLocalShadowBucket` `GPUSceneData.h:113-151`; `PrepareGPUCulling` `SceneRendererGPUDriven.cpp:514-759` | AM 2462-2465; DG 4327-4332 | 0.4.0 |
| Indirect modes | `drawIndexedIndirectCount` (GPU-written count), `NoCount` (bounded slots, zeroed), `PerDraw`; split at `maxDrawIndirectCount`; MoltenVK runs NoCount | `GetGPUIndirectPath` 177-194; `DrawGPUBucket` 1195-1226; `DrawGPUView` 1228-1259 | AM 2467-2473; DG 4258-4260 | 0.4.0 |
| Culling constants | `CullConstants` (planes, camera, LOD params, view params, light view, occlusion params, cascade boxes, counts, parity, fades, cache mask) | `GPUSceneData.h:171-222`; filled at `SceneRendererGPUDriven.cpp:705-758` | AM 2457 | 0.4.0 |
| GPU counters | 128-byte `CullCounters` read back 2-3 frames late into `SceneRendererGPUStats`; `AddGPUCounts` merges for display | `GPUSceneData.h:224-256`; `RecordCullReadback/ResolveCullCounters` `SceneRendererGPUDriven.cpp:1152-1194,1550-1618`; `SceneRenderer.h:740-789` | AM 2473-2474; DG 4272-4276 | 0.4.0 |
| Empty render scene skip | A render scene that never had a proxy records no culling, pyramid or feedback; only clears of counters and caster depths | `RunGPUCulling` 927-940; `SceneRendererStats::GPUCulled` | AM 2477-2482; DG 4277-4283 | 0.7.0 (Roadmap.md:1472) |
| Transparent stays on CPU | The GPU leaves transparent materials' instances to the CPU's sorted pass | `Cull.comp` 202; `RenderSceneGPU::GetTransparentMaterialSlots` | AM 2455-2456 | 0.4.0 |
| Order-independent shading rule | Shading must not depend on draw order or the order of a record's instances (GPU order is scheduling order) | `Cull.comp.slang:12-15`; receiver plane bias in `Include/Shadows.slang` | AM 2474-2477; DG 4264-4271 | 0.4.0 |

### 1.8 Occlusion culling

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| Two-phase view occlusion | Phase 1 draws what was visible last frame into the prepass; a depth pyramid of that; phase 2 tests every proxy in the frustum and draws newly visible ones the same frame | `RunOcclusionPhase` `SceneRendererGPUDriven.cpp:1028-1064`; `CullSecondPhase` `Cull.comp.slang:516-547`; `IsOccluded` 165-191; spec `OcclusionCulling` `SceneRenderer.h:220-228` | AM 2508-2527; DG 4291-4302 | 0.4.0 (Releases/0.4.0.md:41-42) |
| Depth pyramid (HZB) | Level 0 half the depth buffer (rounded up), each level the farthest (smallest, reversed-Z) of 2x2, last row/column covers what lies past it; min sampler where available, else 4 loads | `Scene/HZBBuild.comp.slang`; `GetPyramidLevelSize` `SceneRendererGPUDriven.cpp:64-70`; `GetPyramidFootprint` `Include/Culling.slang:225-246`; spec `MinimumSamplerPyramids` | AM 2511-2517 (wave 8 fix 2516-2517) | 0.4.0 (fix wave 8) |
| Visibility bits | Two bits per proxy alternating by frame parity (and per cascade), cleared on camera cut, first frame or another scene | `c_VisibilityCascadeShift` `GPUSceneData.h:166-169`; `m_VisibilityParity` | AM 2523-2525 | 0.4.0 |
| Cascade occlusion | Each cascade culled in two phases against a pyramid of its own first-phase shadow map (quarter size, `HZBBuildArray.comp`); runs only while it pays (>= 1/16 hidden, else probes every 16 frames) | `RunShadowOcclusionPhase` `SceneRendererGPUDriven.cpp:1112-1150`; `CullShadowSecondPhase` `Cull.comp.slang:552-588`; `IsOccludedInCascade` 292-312; constants 40-53 | AM 2528-2548; DG 4303-4310 | not stated |
| Shadow cascade cache | A cascade's layer is redrawn only when something reaching it changed (camera, light, casters via the proxy log, tables/pool/texture versions) | `PrepareShadowCache/CommitShadowCache` `SceneRendererGPUDriven.cpp:1293-1381`; spec `CacheShadowCascades` | AM 2564-2579; DG 4311-4317 | 0.4.0 (Releases/0.4.0.md:49-50) |

### 1.9 Visibility feedback

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| GPU marks requests | The counting pass marks each touched mesh/material slot with use bits (view, high, prefetch, shadow), largest pixel size and UV pixels; first touch appends to a list; `CullFeedback.comp` packs records | `MarkMeshFeedback/MarkMaterialFeedback/MarkProxyMaterials` `Cull.comp.slang:82-161`; `Scene/CullFeedback.comp.slang`; `FeedbackRecord` `GPUSceneData.h:93-111` | AM 2483-2494 | 0.4.0 |
| CPU applies the newest feedback | `ApplyFeedback` marks slots and sizes; the CPU still walks transparent users, skinned proxies and meshes of unknown bounds | `SceneRendererExtraction.cpp:344-386` | AM 2494-2498; DG 4284-4290 | 0.4.0 |
| When the CPU walks instead | First frames, after a camera cut, tables changed since the feedback's frame, feedback older than 8 frames, once after an overflow | `UsesFeedback` `SceneRendererGPUDriven.cpp:1619-1628`; `c_MaxFeedbackAge` 82 | AM 2498-2503 | 0.4.0 |
| Texture streaming port | `Include/TextureStreaming.slang` ports `TextureStreamingPolicy::GetWorldPixels/GetUVPixels` | `Strata/shaders/Include/TextureStreaming.slang` | AM 2490-2491 | 0.4.0 |

### 1.10 Skinned meshes in the renderer

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| Skin proxies | A proxy whose entity has `SkinComponent` and whose mesh has a `MeshSkinBinding` is posed by the scene's `ISkinningPoses` service (renderer never includes Animation) | `SkinComponent` `Scene/Components.h:171-182`; `ISkinningPoses` `Scene/SceneServices.h:289-`; `EvaluatePose` `RenderScene.cpp:1275-1320` | AM 2324-2354; DG "Skinned meshes" 4488-4504 | 0.3.0 (Releases/0.3.0.md:63) |
| Palettes | Per joint `inverse(proxy world) * animator world * joint model * inverse bind`, 3x4, in a palette range per proxy | `ComputePalette` `RenderScene.cpp:1322-1339`; `GetPalette` | AM 2326-2328 | 0.3.0 |
| Posed bounds | Union of each joint's bind-pose extent through its palette entry, plus `SkeletonPose::Reach` for WhenVisible animators | `ComputePalette` 1324-1338; `MeshSkinBinding::JointBounds/MaxJointExtent` `Mesh.h:44-56` | AM 2328-2335 | 0.4.0 (reach later; not stated) |
| Recompute only on change, in parallel | Skipped when poses, transforms, hierarchy, drawn transforms and layouts are unchanged; batches of 16 on the job system | `UpdateSkinnedPoses` `RenderScene.cpp:1341-1435` | AM 2335-2339 | 0.4.0 |
| Skinned variants | `ST_SKINNED` variants of `Mesh.vert` and `ShadowMesh.vert` (and local shadow) blend four influences from the joint buffer `t15` | `Strata/CMakeLists.txt:186-191`; `BlendJoints` `Include/Scene.slang:168-236`; `Mesh.vert.slang:35-48` | AM 2339-2345 | 0.3.0 |
| Skinned bucketing | `c_InstanceSkinned` + `SkinPalette` in the instance (no growth), skinned sort-key bit, GPU geometry class `c_CullGeometrySkinned` | `SceneRenderData.h:29-30,195-197`; `SceneDrawKey::c_SkinnedShift`; `GPUSceneData.h:120-122` | AM 2339-2342 | 0.3.0 / 0.4.0 |
| Unskinned scenes pay nothing | `HasSkinProxies` gates every skinning check | `RenderScene.h:289-290`; used in `GatherDraws` 939 | AM 2352; DG 4499-4500 | 0.3.0 |
| Visibility reports | Renderers report animators of skin proxies in view (and of off-view casters) so WhenVisible animators know | `ReportVisibleAnimators` `SceneRendererExtraction.cpp:1306-1321`; `ISkinningPoses::ReportVisible` | AM 2347-2352 | 0.4.0 |

### 1.11 Mirrored instances, camera-relative positions and motion vectors

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| Mirrored instances | Negative-determinant transforms get `c_InstanceMirrored`, clockwise-front pipelines and flipped tangent handedness; their own sort-key bit and GPU bucket bit | `UpdateProxyPlacement` 657-658; `GetScenePipeline` `SceneRenderer.cpp:2464-2465`; `Mesh.vert.slang:52-55`; `TransformNormal` `Include/Scene.slang:251-261` | DG "Lights, shadows and HDR" 4545-4547 | 0.3.0 |
| Normal matrix from rows | Shaders derive the normal transform as the cofactor matrix of the 3x3, no inverse on the CPU | `TransformNormal` `Include/Scene.slang:251-261`; `SkinNormal` 227-235 | DG 4218-4219 | 0.3.0 |
| Camera-relative space | Rotation-only view matrices; vertex shaders subtract the camera position from the instance translation first; GPU culling tests relative boxes | `TransformPositionRelative` `Include/Scene.slang:238-244`; `Cull.comp.slang:477-481`; `PrepareGPUCulling` 707-713 | AM 2549-2555; DG "Camera-relative space" 4334-4347 | 0.4.0 |
| Motion vectors | RG16F velocity target; `ST_VELOCITY` vertex variants compare this frame's instance and palette with the renderer's previous ones | `Mesh.vert.slang:57-81`; `GetClipMotion` `Include/Scene.slang:145-149`; `Include/Motion.slang` | DG "Motion vectors and TAA" 4354-4381 | 0.6.0 (Releases/0.6.0.md:37-44) |
| Motion history | Per-renderer copy of the instance and palette buffers as its last frame drew them; `MotionCopy.comp` copies only what the GPU copy wrote since (write logs) | `SceneRenderer::RecordMotionCopy` `SceneRenderer.cpp:1286-`; `Scene/MotionCopy.comp.slang`; `GetPreviousInstanceBuffer/GetPreviousPaletteBuffer` | DG 4361-4372 | 0.6.0 |
| Velocity in both passes | A frame with motion uses the velocity module in prepass and forward pass so EQUAL depth holds | `PipelineKey::Velocity` `SceneRenderer.h:1113-1115` | DG 4376-4378 | 0.6.0 |

### 1.12 User-visible surfaces

| Surface | What it shows | Where |
| --- | --- | --- |
| `renderStats` in `viewport.capture` / `editor.state` | gpuDriven, gpuCulled, gpuCounts, feedbackRequests, drawCommands, draws, opaqueDraws, shadowDraws, instances, shadowCasters, triangles, visibleProxies, occludedProxies, occludedCasters, cachedCascades, culledProxies, instancesPerLod, materials, pendingAssets, extractMs, sortMs, proxyUpdates, instanceBytesUploaded, deferredInstanceBytes, sizeCulledProxies, geometryPool, sceneMirrorMB | `StrataEditor/src/Editor/EditorStateCommands.cpp:228-292` |
| Viewport debug views | `lod` (tint by drawn level, error px), `streaming` (pending/failed), `mip`, `motion` | `StrataEditor/src/Editor/StreamingView.cpp:35-60,151-316`; `EditorViewportCommands.cpp:1095-1140` |
| Quality rows | "Level of detail error (pixels)" 2/1/1/0.5; "Smallest drawn size (pixels)" 1/0.5/0.5/0.25 | `Docs/Manual/Graphics.md:21-22`; `RendererQuality.h:137-143` |
| Viewport stats overlay | Most `SceneRendererStats` fields | AM 2594-2595 |

### How completeness was checked

- Every header of `Strata/src/Strata/Renderer` in scope was opened: `RenderScene.h`, `RenderSceneGPU.h`, `SpatialIndex.h`,
  `AssetResolveCache.h`, `SceneDrawKey.h`, `GPUSceneData.h`, `SceneRenderData.h` (the instance/draw parts), `LODSelection.h`,
  `GeometryPool.h`, `Mesh.h` (skin and LOD parts), `SceneVertexLayouts.h`, `SceneRenderer.h` (specification, stats,
  batches, private extraction types). Every public member of `RenderScene` and `RenderSceneGPU` is accounted for above.
- Every `SceneRenderer::` function in `SceneRendererExtraction.cpp` (24) and `SceneRendererGPUDriven.cpp` (38) was listed
  with `grep` and mapped to a feature; the frame order was read in `SceneRenderer::Render` (`SceneRenderer.cpp:2921-2958,
  3155-3240`).
- Every shader entry of the area registered in `strata_add_shaders` (`Strata/CMakeLists.txt:80-201`) is listed: `Scene/Mesh.vert`
  (+`MeshSkinned`, `MeshVelocity`, `MeshSkinnedVelocity`), `Scene/ShadowMesh.vert` (+`ShadowMeshSkinned`, `LocalShadowMesh`,
  `LocalShadowMeshSkinned`), `Scene/DepthPrepass.frag` (its six variants matter here only for the fade discard and
  velocity), `Scene/Cull.comp` (+`CullShadow`), `Scene/CullBuild.comp`, `Scene/CullFeedback.comp`, `Scene/HZBBuild.comp`
  (+`HZBBuildArray`), `Scene/MotionCopy.comp`, `Debug/LODSelection.comp`; includes `Include/Culling.slang`,
  `Include/LODSelection.slang`, `Include/Scene.slang`, `Include/Motion.slang`, `Include/TextureStreaming.slang`,
  `Include/OrderedFloat.slang` (caster depths).
- Components the area reads: `MeshRendererComponent` and `SkinComponent` (`Scene/Components.h:158-182`). The area
  registers no editor command, settings section, asset type or host function of its own; its user-visible knobs are the
  `Renderer.Quality` rows above and `SceneRendererSpecification` (code only).
- Every bullet of AM "Render scene" (2209-2610) and of DG "Render scene", "Batching", "GPU-driven path", "Camera-relative
  space", "Skinned meshes", the motion part of "Motion vectors and TAA" and "Streaming and uploads" maps to a row.
- The test files of the area (section 6 and section 9) were listed with their `TEST_CASE` names.

---

## 2. Concepts to teach

In dependency order. Each concept: the problem, what engines generally do, what Strata does and why, and the usual mistake.

1. **What a draw call is and why its count matters.** Problem: the GPU draws triangles only when the CPU records a command
   naming a vertex/index range, a pipeline and bindings; each command costs CPU time in the driver and state changes cost
   GPU time. Approaches: one draw per object (simple, does not scale), instancing, merging static geometry, indirect draws.
   Strata: instanced batches per (pipeline state, mesh, submesh, LOD), buckets per pipeline state drawn by one indirect
   call. Newcomer mistake: thinking triangle count is the only cost; or thinking fewer draw calls always means faster.

2. **Retained vs immediate scene representation for rendering.** Problem: walking the ECS every frame to find drawable
   things costs O(scene). Approaches: immediate extraction every frame (Unity's older built-in pipeline style),
   retained render proxies (Unreal's `FPrimitiveSceneProxy`), a GPU scene. Strata: retained proxies in SoA form, updated
   only from component signals and the transform change log (AM 2211; `RenderScene.h:73-113`). Why: "cost follows change
   and view" (Roadmap.md:18). Mistake: writing a component field without signaling, so the proxy is stale (the Debug
   `Validate` exists to catch it).

3. **Structure of arrays and stable indices.** Problem: hot loops touch a few fields of many objects. Approach: SoA with
   free lists so indices are stable and reusable. Strata: `m_Entities`, `m_Flags`, `m_WorldBounds`... (`RenderScene.h:469-486`),
   free proxy and instance ranges by length (`m_FreeInstanceRanges`). Mistake: assuming a proxy index or instance slot
   keeps its entity forever (the motion history and LOD fade state check `EntityID` because slots change hands).

4. **Bounding volumes and their transforms.** Problem: testing every triangle is impossible; test a box. Approaches:
   spheres, AABBs, OBBs; transforming an AABB conservatively. Strata: local AABB transformed to a world AABB
   (`AABB::Transformed`), spheres from the box for screen size. Mistake: transforming only the min/max corners, which is
   wrong under rotation.

5. **Frustum culling.** Problem: draw only what can be on screen. Approach: six planes from the view-projection matrix;
   the "positive vertex" test of a box against each plane. Strata: `IntersectsPlanes` (`SpatialIndex.cpp:56-71`), the same
   test on the GPU (`Include/Culling.slang:248-264`). Mistake: forgetting the test is conservative (boxes near corners
   pass while outside) and expecting exact results.

6. **Spatial acceleration structures.** Problem: even a per-object frustum test is O(n). Approaches: BVH, octree, loose
   octree, uniform/loose grids, hashing. Strata: a loose two-level grid with blocks (AM 2408-2412) whose edits cost constant
   time and whose results equal a brute-force scan. Why: proxies move every frame; a BVH refit or rebuild costs more than
   a cell move. Mistake: believing a hierarchy gives approximate results; this one is exact by construction.

7. **Screen-space size: the projected fraction.** Problem: decide detail and importance by how big something looks.
   Approach: projected sphere diameter over viewport height. Strata: `GetScreenFraction` (`LODSelection.cpp:10-17`), used
   for LOD, request priority, size culling and texture streaming. Mistake: using world distance instead (a huge object far
   away is still large on screen).

8. **Levels of detail.** Problem: distant meshes waste triangles and alias. Approaches: discrete LODs by distance or
   screen size, by geometric error (screen-space error metric, as Nanite/HLOD systems do), continuous LOD; transitions by
   popping, dithered cross-fade, geomorphing. Strata: discrete levels generated with their error (meshoptimizer's
   simplifier, `MeshUtils::GenerateLODs`, `c_MaxLODError` 0.02), chosen so the error stays under `LODErrorPixels`;
   legacy levels by halving; 16-frame complementary 4x4 dither cross-fade. Why the strange arithmetic (doublings, one
   multiplication, `precise`): the CPU and GPU must choose the same level for the same fraction (`LODSelection.cpp:22-25`).
   Mistakes: comparing `log2` results across CPU and GPU; fading in only one of the prepass/forward passes (breaks EQUAL).

9. **Asset streaming meets rendering.** Problem: content larger than memory; the renderer must never wait. Approach:
   request by visibility with priorities, draw fallbacks meanwhile, LRU eviction stamped by use. Strata: High/Normal/Low
   by screen fraction and prefetch distance, one lookup per asset per frame through `AssetResolveCache`, references
   released at frame end so what leaves the view becomes evictable (AM 2413-2432). Mistake: holding `Ref<Mesh>` across
   frames (pins memory), or resolving per entity (thousands of locked lookups).

10. **Sorting draws: sort keys and radix sort.** Problem: group draws by state cheaply and deterministically. Approach:
    pack the state into an integer key, sort once (Christer Ericson's "order your graphics draw calls around"). Strata:
    64-bit `SceneDrawKey`, stable LSD radix sort that skips constant bytes. Mistake: putting high-churn fields in the high
    bits, or including the material in the key (Strata's instancing is material-free).

11. **Instancing and per-instance data.** Problem: one draw for many copies with different transforms and materials.
    Approaches: per-instance vertex streams; a structured buffer indexed by instance id; "draw list" indirection. Strata:
    persistent 64-byte `InstanceData`, a per-frame draw list of indices, `u_DrawList[SV_VulkanInstanceID]` (which includes
    the base instance), materials by slot from a buffer. Mistake: using `SV_InstanceID` (excludes base instance) or growing
    `InstanceData` (every pass reads it; additions go in parallel buffers).

12. **Shared geometry buffers.** Problem: binding a vertex buffer per mesh forces a draw per mesh. Approach: one big
    vertex/index buffer per vertex format with suballocation (a "mega buffer"). Strata: `GeometryPool` with Static and
    Skinned arenas, offsets in draw arguments, compaction moves geometry. Mistake: caching a mesh's offsets across frames.

13. **Indirect drawing.** Problem: the CPU must know draw parameters to record them. Approach: draw arguments in a GPU
    buffer (`DrawIndexedIndirect`), `multiDrawIndirect` for many, `DrawIndirectCount` for a GPU-written count. Strata:
    all three, chosen by device capability, split at `maxDrawIndirectCount` (`GetGPUIndirectPath`). Mistake: assuming every
    device has `drawIndirectCount` (MoltenVK does not).

14. **The GPU scene and GPU-driven culling.** Problem: CPU culling of a million proxies costs milliseconds. Approach
    (Wihlidal "Optimizing the Graphics Pipeline with Compute", GDC 2016; Haar & Aaltonen "GPU-Driven Rendering Pipelines",
    SIGGRAPH 2015): keep the scene on the GPU, cull in compute, compact into indirect arguments. Strata: `RenderSceneGPU`
    updated from change logs; `Cull.comp` count pass, `CullBuild.comp` prefix allocation per (bucket, LOD record), write
    pass. Why two passes rather than one atomic append: deterministic ranges per record and draws per bucket with known
    slots. Mistake: changing a culling rule on one path only; letting shading depend on instance order.

15. **Change logs and versioned mirrors.** Problem: keep a GPU copy in sync without re-uploading everything; several
    readers at different times. Approach: dirty flags, or version-stamped logs with a floor ("you are too far behind, read
    all"). Strata: three bounded logs with versions, coalesced proxy entries, write logs on the GPU side. Mistake: changing
    instances without `RecordInstanceChanges`/`RecordProxyChange` (the GPU path draws stale data the CPU path does not).

16. **Occlusion culling with a hierarchical depth buffer.** Problem: much of what is in the frustum is hidden. Approaches:
    hardware occlusion queries (latency), software rasterized occluders (Frostbite, Intel's MaskedOcclusionCulling), HZB
    reprojection, two-phase HZB (Haar & Aaltonen 2015, Nanite). Strata: two-phase in the same frame (nothing appears a
    frame late), farthest-depth pyramid with conservative edges, also per shadow cascade, running only while it pays.
    Mistakes: building the pyramid with the wrong UV normalization (the wave 8 bug, AM 2516-2517); a non-conservative test
    (something hidden wrongly is a visible bug, something drawn needlessly is only cost).

17. **Feedback loops from GPU to CPU.** Problem: the GPU knows what is visible; the CPU decides what to load. Approach:
    GPU writes feedback buffers read back a few frames later (texture streaming feedback, virtual texturing). Strata: use
    bits and sizes per mesh/material slot, read back 2-3 frames late; CPU walks instead when feedback cannot know.
    Mistake: tests that expect requests in the frame a scene changed.

18. **Skinning on the GPU.** Problem: animated characters deform per vertex. Approaches: CPU skinning, vertex-shader
    linear blend skinning with a palette, compute pre-skinning, dual quaternions. Strata: vertex-shader LBS with four
    influences, palettes computed on the CPU per changed pose (job system), posed bounds from per-joint bind extents.
    Mistakes: culling with bind-pose bounds (a swung limb disappears or loses its shadow); influences naming joints outside
    the skin (shaders read all four).

19. **Handedness and mirrored transforms.** Problem: a negative scale flips triangle winding and tangent frames.
    Approach: detect the determinant's sign, flip front-face winding and bitangent sign. Strata: `Mirrored` flag, separate
    pipelines and buckets. Mistake: back-face culling a mirrored mesh inside-out.

20. **Floating-point precision far from the origin.** Problem: float32 world positions lose millimeters at kilometers.
    Approaches: origin rebasing, camera-relative rendering, double precision on the CPU. Strata: camera-relative space in
    every scene shader (rotation-only view matrices, subtraction in double on the CPU for uploads). Mistake: building a
    new pass with absolute positions.

21. **Motion vectors.** Problem: TAA and motion blur need where each pixel was last frame. Approaches: camera-only
    reprojection from depth; per-object previous transforms; previous skinning. Strata: per-renderer motion history of
    instance and palette buffers, copied incrementally; velocity variants in both prepass and forward pass. Mistake:
    storing "previous" in the shared GPU copy (renderers render at different times).

22. **Determinism and agreement as a design constraint.** Problem: two implementations of the same rule drift.
    Strata's answer: chunked parallel work merged in chunk order, slot-ordered requests, CPU/GPU twins checked
    pixel-for-pixel by `GPU.SceneRenderer.GPUDriven`. Mistake: "fixing" a rule in `SceneRendererExtraction.cpp` only.

---

## 3. Code worth showing

| # | File and lines | What it teaches | Reader must know first |
| --- | --- | --- | --- |
| 1 | `Strata/src/Strata/Renderer/SceneRenderData.h:160-216` | `AffineTransform` (3 rows), the 64-byte `InstanceData`, the draw-list entry with its fade code | Matrices, structs, bit shifts |
| 2 | `Strata/src/Strata/Renderer/RenderScene.h:73-113` | The class comment: the whole design of the render scene in prose (signals, layouts, unknown bounds, skinning, logs) | Concepts 2-3 |
| 3 | `Strata/src/Strata/Renderer/RenderScene.cpp:130-140, 188-236` | Listening to EnTT signals and a de-duplicating pending queue (index map with swap-remove) | EnTT basics (another area) |
| 4 | `Strata/src/Strata/Renderer/RenderScene.cpp:316-401` | `Sync`: pending entities, then transform change log or full refresh, interpolated set, lights, layouts, poses, index refresh, Debug validation | 2, 3 and the scene's transform log |
| 5 | `Strata/src/Strata/Renderer/RenderScene.cpp:647-711` | `UpdateProxyPlacement`: determinant for mirroring, bounds choice (posed / layout / recorded / placeholder), drawable rule, index membership | 4 |
| 6 | `Strata/src/Strata/Renderer/RenderScene.cpp:1106-1132, 1168-1239` | Writing instances only where bytes differ; the bounded versioned change logs and their floors | 3, 15 |
| 7 | `Strata/src/Strata/Renderer/SpatialIndex.cpp:56-107` | The positive/negative vertex tests; classify Inside/Intersecting/Outside | 4, 5 |
| 8 | `Strata/src/Strata/Renderer/SpatialIndex.cpp:303-345, 406-438` | Loose grid: constant-time update, query that takes whole cells and tests straddlers | 6 |
| 9 | `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp:249-328` | `CullView`/`MarkVisibleProxies`: query, per-chunk marks merged in order, request priorities by screen fraction | 5-7, 9, job system |
| 10 | `Strata/src/Strata/Renderer/AssetResolveCache.cpp:87-130` | One lookup per handle per frame; resident lookups never start loads | 9 |
| 11 | `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp:701-743` | `ResolveAssets`: slot order, priority from use bits, geometry place read once per frame | 9, 12 |
| 12 | `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp:961-1047` | The heart of `GatherDraws`: residency check, size culling, LOD choice, transparent split, sort item and LOD fade double entry | 8, 10, 11 |
| 13 | `Strata/src/Strata/Renderer/SceneDrawKey.h:9-43` | Packing a sort key, the `static_assert` that the fields tile 64 bits | Bit fields |
| 14 | `Strata/src/Strata/Core/RadixSort.cpp:14-67` | Stable LSD radix sort that skips bytes equal in every key | 10 |
| 15 | `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp:845-869` | `BuildBatches`: runs of equal keys become batches | 13-14 |
| 16 | `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp:1271-1302` | Uploading only the changed range of a list (mismatch from both ends), swap as double buffer | Buffers |
| 17 | `Strata/src/Strata/Renderer/SceneRenderer.cpp:2042-2111` | Indirect arguments at geometry-pool offsets; bucketing consecutive batches by pipeline key and arena | 12, 13 |
| 18 | `Strata/src/Strata/Renderer/SceneRenderer.cpp:2464-2469` | Mirrored winding and double-sided culling in pipeline state | 19 |
| 19 | `Strata/src/Strata/Renderer/LODSelection.cpp:19-34, 60-87` | Halving rule and error rule, written so CPU and GPU agree | 7, 8 |
| 20 | `Strata/src/Strata/Renderer/LODSelection.cpp:99-159` with `Strata/shaders/Include/Scene.slang:155-166` | The LOD fade state machine and the complementary Bayer masks | 8 |
| 21 | `Strata/src/Strata/Renderer/RenderSceneGPU.cpp:679-782` | GPU mirror update: changes of resident proxies now, destroyed cleared, new ones within a byte budget oldest first | 15 |
| 22 | `Strata/shaders/Scene/Cull.comp.slang:448-511` | `CullProxy`: flags, drawable check, prefetch feedback, camera-relative frustum, size cull, feedback, visibility bit, emit | 14, 20, HLSL basics |
| 23 | `Strata/shaders/Scene/Cull.comp.slang:58-80, 195-232` | `Emit` (count vs write via the same function) and `EmitViewInstances` (material, LOD, bucket, fade) | 22 |
| 24 | `Strata/shaders/Scene/CullBuild.comp.slang:49-110` | Prefix allocation by atomics: a range of the draw list and an indirect slot per record, overflow handling, 64-bit triangle count by carry | 13, 14, atomics |
| 25 | `Strata/src/Strata/Renderer/SceneRendererGPUDriven.cpp:923-1026` | The pass sequence count -> build -> feedback -> write, and why explicit UAV barriers are needed through one binding set | 14 |
| 26 | `Strata/shaders/Scene/HZBBuild.comp.slang:36-80` with `Strata/shaders/Include/Culling.slang:225-246` and `Strata/shaders/Scene/Cull.comp.slang:165-191` | Building a conservative farthest-depth pyramid (odd sizes, min sampler) and testing a box's screen rectangle against it | 16, reversed-Z |
| 27 | `Strata/src/Strata/Renderer/SceneRendererGPUDriven.cpp:1028-1064` and `Cull.comp.slang:516-547` | The two-phase occlusion sequence and the alternating visibility bits | 26 |
| 28 | `Strata/shaders/Scene/Cull.comp.slang:84-100` and `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp:344-386` | Feedback with read-before-atomic and first-touch lists; the CPU side that applies it | 17 |
| 29 | `Strata/src/Strata/Renderer/RenderScene.cpp:1322-1339` and `Strata/shaders/Include/Scene.slang:178-193` | Palette formula and posed bounds; blending four joints in the vertex shader | 18 |
| 30 | `Strata/shaders/Scene/Mesh.vert.slang:35-82` | The whole scene vertex shader: draw list, skinning, camera-relative position, normal and mirrored tangent, fade code, previous-frame position for motion | 11, 18-21 |
| (test) | `StrataTests/src/Renderer/RenderSceneTests.cpp:384-435` | A test that reads like a specification: 100,000 cubes, a still sync updates nothing, one move updates one instance, an unsignaled write fails `Validate` | 2, 15 |

Also useful, shorter: `Strata/src/Strata/Renderer/GPUSceneData.h:113-151` (bucket index bit layout), `SceneRendererGPUDriven.cpp:177-194`
(choosing the indirect path from device capabilities), `SceneRendererGPUDriven.cpp:1619-1628` (`UsesFeedback`: every
reason the CPU walks instead), `Strata/shaders/Include/Scene.slang:238-261` (camera-relative position and cofactor normal).

---

## 4. Figures

### Diagrams

1. **The frame's extraction timeline** (data flow + timeline): `RenderScene::Sync` -> `AssetResolveCache::BeginFrame` ->
   `RenderSceneGPU::Update` -> `CullView` or `ApplyFeedback` -> `FindShadowCasters` -> `ResolveAssets` -> `GatherDraws`/
   `GatherShadowDraws` -> `BuildDrawArguments` -> `PrepareGPUCulling` -> `UploadSceneData` -> `RunGPUCulling` -> prepass
   phase 1 -> `RunOcclusionPhase` -> forward -> `ReleaseFrameAssets`. Two lanes: CPU path and GPU-driven path. Source: AM
   2216-2246, `SceneRenderer.cpp:2921-3240`.
2. **Entity to pixels**: ECS components -> signals -> render proxy (SoA) -> instances -> GPU copy -> draw list -> vertex
   shader. Shows which object owns which data and on which thread.
3. **Structure of arrays of proxies** (memory layout): one column per array of `RenderScene.h:469-486`, proxy index as row,
   free list; contrast with an array of structs.
4. **`InstanceData` 64-byte layout and draw-list entry bits** (memory layout): 48 B rows, 4x4 B fields; 27-bit instance,
   5-bit fade code (codes 1-15 incoming, 17-31 outgoing).
5. **`SceneDrawKey` 64-bit layout** (bit diagram) with the fields tiling the word.
6. **GPU bucket index layout** (bit diagram): view bucket bits 0-4, shadow buckets per cascade, local view buckets; dense
   index table.
7. **Loose grid spatial index** (2D illustration): cells keyed by box centers, loose cell bounds overlapping neighbors, a
   block, the large-object list, and a frustum classifying blocks/cells as Inside/Intersecting/Outside.
8. **Change logs and versions** (timeline): versions increasing, a reader's version, the floor, overflow -> "read all";
   coalescing of a proxy changed twice between reads.
9. **RenderSceneGPU residency state machine**: not seen -> queued (record of zeros) -> resident; destroyed -> cleared;
   budget per frame.
10. **Geometry pool memory map**: Static arena (positions, attributes), Skinned arena (+skin stream), index arena; a mesh's
    `GeometryHandle` -> entry -> submeshes -> LOD records; compaction moving a range.
11. **GPU-driven passes** (data flow): proxies buffer -> Cull.comp count -> counts[(bucket, LOD record)] -> CullBuild.comp
    -> offsets, arguments, bucket counts -> Cull.comp write -> draw list -> indirect draws per bucket. With buffer names.
12. **Two-phase occlusion culling** (timeline over two frames): visibility bits by parity, phase 1 draws last frame's
    visible, HZB, phase 2 tests the rest, writes this frame's bits.
13. **Depth pyramid construction and footprint**: levels with odd sizes, last row/column covering the remainder, a box's
    screen rectangle mapped to the finest level spanning at most 2x2 texels; reversed-Z "farthest = smallest".
14. **LOD selection by error**: a mesh with levels and their relative errors, screen fraction axis, threshold line; the
    halving rule as a staircase.
15. **LOD cross-fade**: the 4x4 Bayer matrix, the mask at steps 1, 8, 15 for the incoming and the complement for the
    outgoing level; the state machine (continuing, reverse, restart).
16. **Visibility feedback loop** (timeline): frame N culls and writes feedback -> readback at N+2/N+3 -> CPU requests ->
    loads -> tables change -> CPU walks until feedback catches up.
17. **Skinning palette** (math diagram): spaces (bind, joint, animator, proxy local, world) and the product
    `inverse(proxy) * animator * joint * inverseBind`; posed bounds as union of transformed joint boxes.
18. **Motion history** (data flow): shared GPU copy writes with write versions -> per-renderer history buffers ->
    `MotionCopy.comp` copies written ranges -> `ST_VELOCITY` vertex shaders read both.
19. **CPU path vs GPU-driven path decision tree**: `GPUDriven` Auto/Off, device features (`drawIndirectFirstInstance`,
    `multiDrawIndirect`, `drawIndirectCount`, `maxDrawIndirectCount`), `IndirectMode`, empty render scene.

### Screenshots (what each must show, and how to isolate it)

Note: `GPUDriven`, `OcclusionCulling`, `VisibilityFeedback`, `FadeLevelsOfDetail` and `BatchAcrossMaterials` are
`SceneRendererSpecification` fields, not exposed in the editor UI or commands (found only in code and tests). Screenshots
that compare them need a small harness renderer or a test helper (see section 9).

1. **LOD debug view** on a scene with generated LODs (OpenWorld island vegetation or a Showcase prop field): Scene view,
   `viewport.setSettings {debugView: "lod"}`; legend "LOD n (x px)". Pair with Graphics Quality Low vs Ultra (error 2 vs 0.5
   px) to show levels moving.
2. **LOD cross-fade mid-transition**: a close-up captured during a fade (dolly the camera across a threshold, capture with
   `viewport.capture {live}`), zoomed so the 4x4 dither pattern of both levels is visible. Single captures turn fades off,
   so it must be a live capture.
3. **Streaming debug view** while a large scene loads (OpenWorld on open): `debugView: "streaming"`, pending entities in
   Sulfur, missing meshes as boxes, showing requests follow the view.
4. **Request priorities**: two captures of the stress world/OpenWorld from a corner (Perf "stress world seen from an empty
   corner") with `renderStats.pendingAssets` and `materials` overlaid; optional.
5. **Material-free instancing**: 1,000 cubes with 1,000 distinct material colors, `renderStats.opaqueDraws` = 1; contrast
   with `BatchAcrossMaterials` off (harness) showing 1,000 draws for the same image.
6. **Mirrored instance**: a mesh with scale x = -1 next to the original, correct outward faces and lighting (normal map),
   e.g. an asymmetric prop from Showcase.
7. **Skinned character with swung limb**: ThirdPerson's robot mid-animation (Dance) with its shadow, showing the limb
   outside the bind-pose box is drawn and casts its shadow; optionally debug bounds lines.
8. **Occlusion culling**: a wall in front of many boxes; picture plus `renderStats.occludedProxies` and `visibleProxies`
   before/after the wall is removed; and a debug-line overlay of hidden boxes if the book builds one (not in the engine).
9. **Shadow cascade caching**: a still view with `renderStats.cachedCascades` = cascade count, then a moving object
   redrawing only the cascades it reaches (numbers, not an image difference).
10. **Motion debug view**: `debugView: "motion"` while the camera pans and a character runs (ThirdPerson), hue = direction.
11. **Camera-relative precision**: the same small scene placed at the origin and 100 km out (the scene used by
    `GPU.SceneRenderer.CameraRelative`), rendered with and without relative positions; the "without" image needs a
    modified build or a simulated float32 reprojection, so it may be a diagram instead.
12. **Placeholder/unknown bounds**: a terrain whose origin is out of view yet loads and appears (test scenario
    `GPURenderSceneTests.cpp:586`), as a before/after pair.

---

## 5. Rules and pitfalls (the "why" boxes)

1. **Signal every write to `MeshRendererComponent` and transforms** (`MarkModified`, `registry.patch`, `ComponentAccess`).
   Why: the render scene only reads signaled entities and the transform log; an unsignaled write leaves a stale proxy
   that the GPU draws. Debug validation catches it a few syncs later (AGENTS.md "Scene caches"; AM 2252-2259).
2. **Never resolve assets per entity in renderer code; go through proxies and the frame's `AssetResolveCache`.** Why:
   thousands of locked lookups per frame, and references that outlive the frame pin memory (DG 4185-4186; AGENTS.md
   "Rendering").
3. **Hold `AssetHandle`s across frames, not `Ref`s.** Why: the cache drops every reference at frame end so evicting what
   left the view works, also for idle renderers (AM 2421-2424).
4. **Record every change of instances or proxies in the logs** (`RecordInstanceChanges`, `RecordProxyChange`). Why: the GPU
   copy and the shadow cache know only what the logs say; the CPU path would look right while the GPU path draws stale
   data (DG 4198-4200).
5. **`InstanceData` stays 64 bytes; per-instance additions go to parallel buffers.** Why: every pass reads it per instance;
   growth costs bandwidth everywhere (`LODFadeState` is the model, DG 4200-4202).
6. **Change the CPU rule and the GPU rule together** (frustum, size, cascades, sub-texel, materials, LOD,
   feedback marks, texture streaming measures). Why: two implementations of one decision; tests compare pixels and counts
   (DG 4264-4267, 4286-4288).
7. **Shading must not depend on draw order or instance order.** Why: GPU culling places instances in scheduling order;
   screen-space derivatives only of the primitive's own interpolants, before `discard` (DG 4267-4271; Cull.comp:12-15).
8. **The prepass and forward pass must produce bit-identical positions.** Why: the forward pass uses an `EQUAL` depth test;
   so both use the same vertex module (velocity variant in both, skinned variant in both), the position is decorated
   invariant, and LOD fades discard by the same mask in both (`Mesh.vert.slang:4-10`, DG 4376-4378, 4223-4226).
9. **Read mesh geometry through the pool every frame.** Why: compaction moves it between frames; growth recreates buffers
   (DG 4232-4235).
10. **Occlusion culling must stay conservative.** Why: drawing too much costs time, hiding wrongly is a visible bug; the
    pyramid's sizes are mip sizes, last row/column cover the remainder, footprints clamp (DG 4295-4302). The wave 8 bug:
    a minimum sampler's UVs normalized by the wrong size hid visible objects (AM 2516-2517).
11. **Anything new that reads the view's depth runs after the second phase's prepass.** Why: phase 2 adds newly visible
    objects to the depth (DG 4295-4296).
12. **A new input of how casters are drawn changes a version the shadow caches compare.** Why: a still camera keeps showing
    the old shadow otherwise (DG 4311-4315; AGENTS.md "Rendering").
13. **Every skin influence names a joint of the skin, even with zero weight.** Why: the shader reads all four palette
    entries; an out-of-range index reads another proxy's joints (DG 4501-4502; `Mesh::CreateSkinned` refuses).
14. **Anything that adds skinning work must cost unskinned scenes nothing** (`HasSkinProxies`). Why: most scenes have no
    skins (DG 4499-4500).
15. **Cull skinned proxies with posed bounds, not bind-pose bounds.** Why: a swung limb would be culled or lose its shadow
    (AM 2328-2331).
16. **Never store "previous frame" data in the shared GPU copy.** Why: its renderers render at different times; each
    renderer keeps its own motion history (DG 4361-4364).
17. **Mirrored instances need clockwise pipelines and flipped tangents.** Why: a negative determinant reverses winding and
    handedness (DG 4545-4547).
18. **Positions uploaded to scene shaders are camera-relative, subtracted in double.** Why: float32 precision far from the
    origin (DG 4339-4345).
19. **Compare buffer versions, never mirrors or scene ids, to know when to rebuild binding sets.** Why: a recycled mirror's
    buffers are the same objects under the same version (DG 4194-4197).
20. **Tests that count draws render a frame more first, or turn occlusion off; tests of requests wait for feedback or turn
    it off.** Why: two-phase draws and 2-3 frame feedback latency (DG 4289-4294).
21. **Code that renders a single picture renders again until no proxy waits** (`DeferredProxies`). Why: new proxies upload
    within a per-frame budget (DG 4191-4194).
22. **A new GPU-culling resource that matters without proxies is cleared in the empty-scene branch too.** Why: empty render
    scenes record no culling passes (DG 4281-4283).
23. **Never `writeBuffer` the scene's GPU copy; go through staging** (`GPUUploadQueue::RecordSceneUpload`). Why: uploads are
    budgeted and fenced (DG 4189-4190, 6057-6069).
24. **Explicit UAV barriers between culling dispatches through one binding set.** Why: NVRHI inserts barriers only when
    binding sets change (`CullBarrier` `SceneRendererGPUDriven.cpp:1017-1026`; AGENTS.md "NVRHI pitfalls").

---

## 6. Hands-on

### For engine developers

1. **Read a frame's statistics** (easy). Run a sample in the editor, call `viewport.capture` and explain every field of
   `renderStats` listed in section 1.12. Proves: the reader can map stats to pipeline stages.
2. **Write a spatial-index test** (easy). Add a doctest case to `StrataTests/src/Renderer/SpatialIndexTests.cpp` that
   inserts boxes on a line, queries a sphere, and checks the result equals brute force. Proves: understanding of exactness.
3. **Brute force vs loose grid** (medium). Implement a brute-force `QueryFrustum` in a scratch test and time both on
   100,000 random boxes (perf tests only in Release). Proves: the purpose of acceleration structures.
4. **Trace a signal** (medium). Change a mesh renderer's material in a test without `MarkModified`, observe `Validate`
   failing (pattern of `RenderSceneTests.cpp:426-434`), then fix. Proves: the transform/component contract.
5. **Change the sort key** (medium). Move the material into the batch key (as `BatchAcrossMaterials` off does) and compare
   `OpaqueDrawCalls` on 1,000 materials (`GPURenderSceneTests.cpp:120`). Proves: material-free instancing.
6. **Radix sort exercise** (medium). Explain why `RadixSort` skips bytes, construct keys that need 1, 3 and 8 passes, and
   check stability with a test like `Core/RadixSortTests.cpp`. Proves: sort keys and LSD radix.
7. **Add a per-instance value the right way** (hard). Add a per-instance tint as a parallel buffer (as `LODFadeState`),
   not in `InstanceData`; record changes in the logs and show both paths agree. Proves: rules 4-6.
8. **Port a CPU culling rule to the GPU** (hard). Add a hypothetical "max draw distance" to `SceneRendererSpecification`,
   implement it in `GatherDraws` and `Cull.comp`, extend `GPU.SceneRenderer.GPUDriven`'s comparison. Proves: twin rules,
   constants upload, test discipline.
9. **Occlusion pyramid on paper** (medium). For a 7x5 depth buffer, compute levels by hand following `HZBBuild.comp`, then
   compute `GetPyramidFootprint` for a rectangle touching the last column. Proves: conservative pyramids.
10. **LOD fade simulation** (easy-medium). Call `LODSelection::UpdateLODFade` in a loop with a target that changes at frame
    5 and back at frame 9; print codes; check with `LODSelectionTests.cpp:216-272`. Proves: the fade state machine.
11. **Feedback latency experiment** (medium). In a GPU test, add a mesh and count frames until `FeedbackRequests` requests
    it (model on `GPUSceneFeedbackTests.cpp:247`). Proves: GPU-to-CPU feedback latency.
12. **Skinned bounds** (medium). Pose a two-joint arm out of its bind box (`GPUAnimationTests.cpp:192`) and print
    `GetLocalBounds` before/after `Sync`. Proves: posed bounds.

### For game developers

1. **Is my scene drawing efficiently?** (easy). Open the Showcase, check `renderStats.opaqueDraws`, `instances`,
   `triangles`, `visibleProxies`, `occludedProxies`; move behind a building and watch `occludedProxies` rise. Proves: what
   culling does for them.
2. **Use the LOD view** (easy). Import a glTF model, place 200 copies receding into the distance, turn on the LOD debug
   view, change Graphics Quality from Low to Ultra. Proves: LOD selection by screen error and the quality row.
3. **Mesh renderer settings** (easy). Toggle `CastShadows` on a dense prop field and read `shadowCasters`/`shadowDraws`.
   Proves: per-object shadow cost.
4. **Watch streaming** (easy). Open OpenWorld with the streaming view; fly the camera and watch requests follow the view
   and the 100-unit prefetch. Proves: visibility-driven loading.
5. **Mirroring safely** (easy). Mirror a prop with negative scale and check it renders and lights correctly. Proves:
   mirrored instances are supported.
6. **Skinned character culling** (medium). In a ThirdPerson copy, set the robot's animator culling to WhenVisible
   (Animation area) and look away; observe `StalePoses` and the pose catching up. Proves: renderers report visibility to
   animators.

---

## 7. Glossary

- **Render proxy**: the renderer's record of one mesh-rendering entity (transform, bounds, mesh, material, flags).
- **Render scene** (`RenderScene`): all proxies of one scene plus instances, slots, palettes, spatial index and logs.
- **Structure of arrays (SoA)**: one array per field instead of one array of structs.
- **Slot (mesh slot, material slot)**: small dense integer standing for a distinct asset handle the scene uses.
- **Instance (`InstanceData`)**: one drawn submesh of a proxy: 64 bytes on the GPU.
- **Submesh**: a part of a mesh with its own index range and material.
- **Draw list**: per-frame array of instance indices (plus fade codes) that a draw's instances read through.
- **Draw entry**: one draw-list element: instance in 27 bits, LOD fade code above.
- **Batch** (`SceneDrawBatch`): one instanced draw: a submesh at one LOD with one pipeline state.
- **Bucket**: consecutive batches (CPU) or a GPU draw group sharing pipeline state and vertex arena, drawn by one indirect call.
- **Pipeline key** (`PipelineKey`): pass, double-sided, mirrored, skinned, velocity, surface: what selects a pipeline.
- **Sort key** (`SceneDrawKey`): 64-bit integer encoding a draw's state for sorting.
- **Radix sort (LSD)**: integer sort by digits from least significant, stable, linear time.
- **Material-free instancing**: instances of one mesh share a draw whatever their materials.
- **Indirect draw**: a draw whose parameters are read from a GPU buffer.
- **`drawIndexedIndirectCount`**: indirect multi-draw whose draw count is also read from a GPU buffer.
- **`multiDrawIndirect`, `drawIndirectFirstInstance`, `maxDrawIndirectCount`**: Vulkan device features/limits that decide the paths.
- **Base instance / first instance**: offset added to the instance index; Strata uses it as the draw-list start.
- **`SV_VulkanInstanceID`**: instance index including the base instance (unlike `SV_InstanceID`).
- **Geometry pool**: shared vertex and index buffers holding every mesh.
- **Arena (Static, Skinned)**: a vertex buffer set of one vertex format in the pool.
- **`GeometryHandle`**: stable id of a mesh's place in the pool; offsets may move.
- **Compaction (defragmentation)**: moving allocations together to recover scattered free space.
- **LOD record (`GeometryLOD`)**: one level of one submesh: a draw record GPU culling counts instances per.
- **Frustum**: the pyramid-shaped volume the camera sees, bounded by six planes.
- **AABB**: axis-aligned bounding box.
- **Positive vertex test**: the box corner farthest along a plane normal decides if the box is wholly behind it.
- **Loose grid**: grid where objects live in the cell of their center and cell bounds expand to cover them.
- **Spatial index** (`SpatialIndex`): Strata's loose two-level grid of proxy bounds.
- **Screen fraction**: projected bounding-sphere diameter divided by viewport height.
- **Size culling**: not drawing objects smaller than `MinProjectedPixels`.
- **Level of detail (LOD)**: simplified versions of a mesh drawn when it is small on screen.
- **Geometric error (LOD error)**: how far a simplified level deviates from full detail, in mesh units (`MeshLOD::Error`).
- **Relative error**: LOD error divided by the mesh bounds' radius.
- **Error threshold**: largest screen fraction x relative error allowed for the configured error pixels.
- **LOD cross-fade**: drawing old and new level with complementary dither masks over 16 frames.
- **Ordered dither / Bayer matrix**: a fixed 4x4 pattern of thresholds 0-15 used for the fade masks.
- **EQUAL depth test**: forward pass draws only where depth equals the prepass's, so it shades each pixel once.
- **Depth prepass**: drawing depth (and IDs, normals, velocity) before shading.
- **Reversed-Z**: depth 1 at the near plane, 0 at the far plane; "farthest" is the smallest value.
- **Occlusion culling**: not drawing what is hidden behind other geometry.
- **Hierarchical Z-buffer (HZB) / depth pyramid**: mip chain of depth keeping the farthest depth per texel.
- **Two-phase occlusion culling**: draw last frame's visible set, build HZB, test the rest, draw newly visible.
- **Visibility parity**: which of two alternating bits holds last frame's visibility.
- **Conservative test**: may report visible what is hidden, never the reverse.
- **Min/max sampler (`samplerFilterMinmax`)**: sampler returning the minimum of the filtered texels.
- **GPU-driven rendering**: the GPU culls and builds its own draw commands.
- **GPU copy / mirror** (`RenderSceneGPU`): the render scene's buffers on the GPU, shared by its renderers.
- **Resident (proxy)**: its record and instances are uploaded; only resident proxies draw.
- **Change log**: version-stamped list of changed indices that readers follow.
- **Version / floor**: monotonically increasing counter; the oldest version a log still covers.
- **Staging buffer**: CPU-writable buffer copied into GPU buffers.
- **Upload budget**: bytes a frame may upload for new proxies (`NewInstanceBytesPerFrame`).
- **Culling record (`GPUProxy`)**: 64-byte per-proxy record GPU culling reads.
- **Mesh table / material table**: per-slot GPU tables of loaded meshes and materials.
- **Counting pass / write pass**: Cull.comp's two modes.
- **Prefix allocation**: giving each group a contiguous range by atomically adding its count to a running offset.
- **Overflow**: instances that found no room in the draw list or slots (counted, not drawn).
- **Readback**: copying GPU data to CPU memory, read frames later without stalling.
- **Visibility feedback**: GPU culling's record of which mesh/material slots were used how, read back to drive requests.
- **Request priority (High, Normal, Low)**: the order the asset manager loads in.
- **Prefetch distance**: radius around the camera whose assets are requested at Low priority.
- **Asset resolve cache**: per-renderer, per-frame memo of asset lookups.
- **Replay**: redoing a previous frame's lookups in one call.
- **Placeholder bounds**: unit box around an entity whose mesh bounds are unknown.
- **Mesh layout**: bounds, submeshes and submesh materials learned from a loaded mesh.
- **Recorded bounds**: bounds the asset database stored at import or pack time.
- **Skin, joint, skeleton**: bones (joints) of an animated character; the mesh is bound to them.
- **Inverse bind matrix**: takes a vertex from mesh (bind) space into a joint's space.
- **Palette**: per-joint skinning matrices of one posed proxy.
- **Linear blend skinning**: each vertex is a weighted average of up to four joints' transforms.
- **Posed bounds**: bounds computed from the pose rather than the bind pose.
- **`ISkinningPoses`**: scene service that publishes poses to the renderer.
- **WhenVisible animator**: an animator that only evaluates poses while seen.
- **Mirrored transform**: one with negative determinant (an odd number of negative scales).
- **Winding / front face**: whether a triangle's vertices appear clockwise or counter-clockwise on screen.
- **Tangent handedness**: sign telling which way the bitangent points.
- **Cofactor matrix**: matrix proportional to the inverse transpose, used to transform normals without inverting.
- **Camera-relative space**: world space translated so the camera is at the origin.
- **Motion vector / velocity target**: per-pixel screen motion since the previous frame.
- **Motion history**: a renderer's copy of instances and palettes as its previous frame drew them.
- **Write version / write log**: GPU copy's record of ranges it wrote, for history copies.
- **Clone (render scene)**: the copy of a render scene made when play starts.
- **Shadow caster / cascade**: an object drawn into a shadow map; one of the sun's nested shadow maps.
- **Sub-texel caster**: caster smaller than a texel of its cascade, left out.
- **Shadow cascade cache**: keeping a cascade's layer while nothing reaching it changed.

---

## 8. Proposed chapters

1. **"What gets drawn: from entities to draw calls"** - concept, both audiences, M. Purpose: the reader can describe the
   problem (draw calls, CPU cost, the frame's extraction stages) and the overall flow from ECS to the GPU, and knows that
   Strata has two paths. Prereqs: ECS basics, GPU pipeline basics. Screenshots: 1 (a capture with `renderStats`).
2. **"The render scene: persistent proxies"** - internals, engine, L. Purpose: explain proxies, SoA, signals and sync,
   slots, instances, unknown and recorded bounds, validation, clones and prepared loads. Prereqs: ch. 1, EnTT signals,
   the transform contract. Screenshots: 1 (placeholder/unknown bounds pair).
3. **"Finding what is in view: bounding volumes, frustums and the spatial index"** - concept + internals, engine, M.
   Purpose: implement and reason about frustum tests and the loose grid; know why results are exact. Prereqs: ch. 2,
   vectors and planes. Screenshots: 0.
4. **"Asking for assets at draw time"** - internals, both, M. Purpose: request priorities, prefetch, the resolve cache and
   replay, fallbacks, drawn-only-when-resident, what renderers publish for mip streaming. Prereqs: ch. 3, asset
   residency (asset area). Screenshots: 1-2 (streaming view).
5. **"Batching and instancing"** - internals, engine, L. Purpose: sort keys, radix sort, material-free instancing,
   draw lists, transparent sorting, changed-range uploads, the geometry pool, indirect arguments and buckets, pipeline
   keys. Prereqs: ch. 4, buffers and pipelines. Screenshots: 1 (one draw for 1,000 materials).
6. **"Levels of detail"** - concept + internals, both, M. Purpose: screen fraction, halving and error rules, CPU/GPU
   agreement, cross-fades with dither masks, the quality row and the LOD view. Prereqs: ch. 5 (draw entries), depth
   prepass basics. Screenshots: 2.
7. **"Mirrors, normals and camera-relative positions"** - concept + internals, engine, S. Purpose: mirrored transforms,
   cofactor normals, camera-relative space, the scene vertex shader end to end. Prereqs: ch. 5, matrices. Screenshots: 1-2.
8. **"The scene on the GPU: RenderSceneGPU"** - internals, engine, M. Purpose: change logs, the mirror's buffers and
   tables, residency budget, growth, clones and recycling. Prereqs: ch. 2, 5, staging uploads. Screenshots: 0.
9. **"GPU-driven culling and indirect drawing"** - internals, engine, XL. Purpose: Cull.comp, buckets, count-build-write,
   indirect modes and device limits, counters and readback, empty scenes, the order-independence rule, CPU/GPU twin
   tests. Prereqs: ch. 6, 8, compute shaders and atomics. Screenshots: 1 (stats).
10. **"Occlusion culling"** - internals, engine, L. Purpose: HZB construction, conservative footprints, two-phase view
    culling, cascades' occlusion and "runs while it pays", the shadow cascade cache. Prereqs: ch. 9, reversed-Z, shadow
    cascades (shadows area). Screenshots: 1-2.
11. **"Visibility feedback"** - internals, engine, M. Purpose: GPU marks, packing, latency, when the CPU walks instead,
    texture streaming's port. Prereqs: ch. 4, 9. Screenshots: 0.
12. **"Skinned meshes in the renderer"** - internals, both, M. Purpose: skin proxies, palettes, posed bounds, parallel
    recompute, skinned variants and buckets, visibility reports to animators. Prereqs: ch. 5, 9; animation basics
    (animation area). Screenshots: 1.
13. **"Motion vectors and the motion history"** - internals, engine, M. Purpose: velocity variants, per-renderer history,
    write logs and `MotionCopy.comp`, why both passes use the velocity module. Prereqs: ch. 8, 12; TAA concept (post area).
    Screenshots: 1.
14. **"Tutorial: making a big scene draw fast"** - tutorial, game, M. Purpose: a game developer builds a scene of
    thousands of props, reads `renderStats`, uses the LOD and streaming views, shadows on/off, quality presets. Prereqs:
    editor basics, ch. 1 (light). Screenshots: 3.
15. **"Reference: render scene switches and statistics"** - reference, both, S. Purpose: every `SceneRendererSpecification`
    field of this area, every stat and `renderStats` key with its meaning. Prereqs: none. Screenshots: 0.

---

## 9. Not determined

- **Not read in full**: `Strata/src/Strata/Renderer/SceneRenderer.cpp` (4,267 lines) beyond the Render orchestration
  (2781-2975, 3155-3245), `BuildDrawArguments`/`DrawBuckets` (2042-2120) and `GetScenePipeline` (2424-2484);
  `SceneRendererExtraction.cpp` lines 388-700 (cascade layout, `FindShadowCasters`, `CanShadowView`, texture resolution)
  and 1126-1255 (`GatherShadowDraws`) were only skimmed by function boundaries; `SceneRendererGPUDriven.cpp` 196-513,
  761-922, 1066-1194, 1273-1618 (resources, light culling, shadow pyramids, shadow cache, local shadows, counters) were
  located but not read line by line; `RenderSceneGPU.cpp` 1-171, 202-603 and 897-1035; `RenderScene.cpp` 713-1078
  (slots, layouts) and `Validate` (1491-1674); `GeometryPool.cpp` (638 lines) and `Core/RangeAllocator`; `Mesh.cpp`;
  `RenderLights.h/.cpp`; `Include/TextureStreaming.slang`, `Include/OrderedFloat.slang`; `ShadowMesh.vert.slang`;
  `Forward.frag.slang` beyond the fade discard; `CullFeedback.comp` past line 25.
- **Tests**: test names were listed; bodies read only for `RenderSceneTests.cpp:384-435` and the head of
  `GPUSceneRendererGPUDrivenTests.cpp:672-684`. `GPUSceneRendererGPUDrivenTests.cpp`'s `CompareScenes` helper (before
  line 670) defines the comparison scenes and is worth reading for the GPU-driven chapter.
- **Releases** not stated by the documents: cascade occlusion culling, materials taken over by still frames, prepared
  loads (`PrepareLoadedScene`), placeholder/recorded bounds, render transforms, posed-bounds reach. Release notes of
  0.4.0 mention "hidden behind other objects" for the view and cascades in one sentence, which does not settle when the
  cascades' occlusion arrived.
- **No UI or command switch** was found for `GPUDriven`, `OcclusionCulling`, `VisibilityFeedback`, `FadeLevelsOfDetail`,
  `BatchAcrossMaterials` or `IndirectMode` (grep of `StrataEditor/src`, `StrataRuntime`, `Strata/src`): comparison
  screenshots need a harness or a test build. Thumbnails force the CPU path (`SceneRenderer.cpp:248-251`).
- **Device reach**: Releases/0.4.0.md:267-269 and 0.5.0.md:281-283 say the GPU-driven path had not yet run on Windows/Linux
  CI machines (no GPU); which GPUs the book's screenshots will come from is not determined.
- **Which sample shows LOD best**: whether OpenWorld or Showcase props have generated LODs with errors was not checked in
  their asset metadata.
- **Local light shadow views' culling** (`CullLocalShadowViews`, `RunLocalShadowCulling`) is in this area's code but
  likely taught in the shadows area; split to be decided by the planner.
- **Light records' GPU culling** (`LightCull.comp`, `LightCompact.comp`) lives in the render scene but is lighting; not
  inventoried here beyond the record itself.
