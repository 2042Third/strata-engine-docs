# Inventory: Scenes, entities and components; reflection; projects and settings

Surveyed at `main` 822a7a46. Scope: `Strata/src/Strata/Scene` (27 headers, 23 sources, 15,816 lines),
`Strata/src/Strata/Reflection` (7 headers, 5 sources, 2,199 lines), `Strata/src/Strata/Project` (4 headers, 4 sources,
1,101 lines), plus the two Core files the settings system lives in (`Core/SettingsRegistry.{h,cpp}`,
`Core/ProjectSettings.{h,cpp}`) because the area's "settings sections" cannot be taught without them. All paths below are
relative to `G:/GameEngineAI`; `S/` abbreviates `Strata/src/Strata/`. Line numbers are at 822a7a46.

Abbreviations for documents: **AR** = `Docs/Architecture.md`, **DG** = `Docs/DeveloperGuide.md`, **AG** = `AGENTS.md`,
**MS** = `Docs/Manual/Settings.md`, **MP** = `Docs/Manual/Prefabs.md`, **SK** = `.claude/skills/strata-add-component/SKILL.md`,
**RM** = `Docs/Roadmap.md`, **RN x** = `Docs/Releases/x.md`.

Release mapping used below (from RM "Status"): waves 1-3 → 0.3.0, wave 4 → 0.4.0, wave 5 → 0.5.0, wave 6 → 0.6.0, wave 7
→ 0.7.0, wave 8 → not released yet (landed on `main` after 0.7.0). Where no document dates a feature, the line says
"release not stated".

---

## 1. Features

### 1.1 The entity-component store (EnTT) and entities

| Feature | Where | Documented | Release |
| --- | --- | --- | --- |
| `Scene` owns one `entt::registry` (EnTT 3.16, `Strata/vendor/entt`), a UUID→entity dense map, the root list and the caches; all functions main-thread only | `S/Scene/Scene.h` 91-105 (class comment), 852-856 (members) | AR "Engine modules" (Scene paragraph, l.261-282) | 0.3.0 (wave 1 `scene-core`) |
| `Entity`: a non-owning handle (`entt::entity` + `Scene*`), copyable; `IsValid` checks the registry; templated `AddComponent`/`GetComponent`/`TryGetComponent`/`HasComponent`/`HasAnyComponent`/`RemoveComponent`/`AddOrReplaceComponent` | `S/Scene/Entity.h` 12-114 | AR l.261-263 | 0.3.0 |
| Tag components (empty structs) cannot be fetched: `GetComponent` `static_assert`s `!std::is_empty_v<T>` | `Entity.h` 37-51 | AG "Code style" (tag components) | release not stated |
| `Entity::MarkModified<T>()` = `registry.patch<T>`: emits EnTT `on_update`, the engine-wide "I wrote this in place" signal | `Entity.h` 84-90 | DG "Architecture rules" (transform contract, l.1058-1085) | 0.3.0 |
| Entity identity: `IDComponent` (64-bit `UUID`, never reused) separate from the EnTT handle (index+version, reused) | `S/Scene/Components.h` 28-31; `Scene::GetEntityByUUID` (`Scene.cpp` 679) | AR l.261 | 0.3.0 |
| Entity creation with core components: hierarchy node first, then ID, Name ("Entity" if empty), Transform, Relationship, WorldTransform; root-appended; duplicate UUIDs replaced with a fresh one plus an error | `Scene::CreateEntityWithUUID`, `Scene.cpp` 386-415; `CreateChildEntity` 423-429 | AR "Scene caches" (Capacity) | 0.3.0 |
| Capacity limit `Scene::c_MaxEntities` = 2^20−1 (EnTT's 20-bit index): creating more logs an error and returns an invalid Entity; deserialization/instantiation refuse up front | `Scene.h` 139-145; `Scene.cpp` 388-392; `SceneInstantiation.cpp` 141-143 | AR "Scene caches" (Capacity); DG l.1084 | release not stated |
| Destruction of an entity destroys its subtree; `DestroyEntities` batches (systems told about every subtree first, sibling lists compacted once); during an update destruction is deferred to the end of the frame | `Scene.h` 148-157; `Scene.cpp` 431-660 (`DestroyEntities`, `DestroyRoots`, `RemoveNestedRoots`, `NotifyEntitiesDestroying`, `DestroySubtrees`, `FlushPendingDestroys`) | AR "Scene runtime lifecycle" (bullet after timeline), "Scene caches" (Batches) | 0.3.0 |
| `DuplicateEntity`: deep copy with fresh UUIDs, inserted after the original, internal entity references remapped | `Scene.h` 159-161; `Scene.cpp` 659-677; `SceneSerializer.cpp` 73-128 (`RemapEntityReferences`) | — (header only) | 0.3.0 |
| `Scene::Copy` (play mode): same EnTT identifiers, every storage copied whole in parallel (`ComponentInfo::AssureStorage`/`CopyStorage`), UUID map and caches copied as-is, signals connected afterwards, module context copiers run; `SceneCopyOptions::SerializedOnly` snapshot for background saves | `Scene.h` 81-89, 114-127; `Scene.cpp` 253-379 | AR "Scene runtime lifecycle" (`Scene::Copy` bullet, l.1041-1055 of the file), "Scene documents" (Snapshots) | 0.3.0; storage-whole copy measured 43 ms/1M |
| `Scene::RegisterContextCopier`: modules copy registry-context data (render scene) into copies; only while the composition root runs | `Scene.h` 121-127; `Scene.cpp` 140-175 | DG "Architecture rules" (Module registration) | release not stated |
| `Scene::ReleaseInBackground`: stop on the main thread, destroy entities on a background job | `Scene.h` 128-133; `Scene.cpp` 177-192 | AR "Scene runtime lifecycle" (scene loads bullet); AG "Editor" | release not stated |
| `Scene::EstimateMemoryUsage` (asset accounting) | `Scene.h` 284-287; `Scene.cpp` 687-731 | — | release not stated |
| Prepared states: typed per-scene slots a system fills before the scene runs (physics bodies) | `Scene.h` 568-595, 969-980 | AR "Scene runtime lifecycle" (scene loads bullet) | release not stated |
| Requests to the owner: `RequestQuit`, `RequestSceneLoad`, `TakeSceneLoadRequest`, `Set/GetSceneLoadProgress` | `Scene.h` 614-627; `Scene.cpp` 2371-2380 | AR "Scene runtime lifecycle" | 0.3.0 |
| Source asset and lineage ID (`GetSourceAsset`, `GetLineageID`) | `Scene.h` 635-643 | AR "Scene runtime lifecycle" (last bullet) | release not stated |
| `Scene::GetAssetManager()`: the only sanctioned path from scene code to assets | `Scene.h` 601-608; `Scene.cpp` 2177-2180 | DG "Architecture rules" (Assets); AG "Architecture rules" | release not stated |

### 1.2 The Scene module's own components

All registered in `S/Scene/ComponentRegistration.cpp` (`RegisterSceneComponents`, 64-187), declared in
`S/Scene/Components.h`. The engine registers 42 components in all (`StrataTests/Architecture/ComponentSchema.json`); the
other 34 belong to other areas (Renderer, Physics, Audio, Animation, Scripting, World, GameUI).

| Component (registered name) | Data | Flags / notes | Lines |
| --- | --- | --- | --- |
| `IDComponent` ("ID") | `UUID ID` | Hidden, NotRemovable, NoSerialize (the serializer writes it as the entity's "ID"); property ReadOnly | Components.h 28-31; reg. 70-73 |
| `NameComponent` ("Name") | `std::string Name` | NotRemovable; indexed by the name lookup (writes must signal) | 33-36; 75-78 |
| `TagComponent` ("Tag") | `std::string Tag` | Gameplay label; indexed | 38-42; 93-96 |
| `InactiveComponent` ("Inactive") | none (tag) | Hidden; presence deactivates entity and descendants | 44-48; 98-101 |
| `TransformComponent` ("Transform") | `Translation`, `Rotation` (quat), `Scale`; `GetTransform()` composes TRS, `SetTransform(mat4)` decomposes (false if impossible) | NotRemovable; rotation edited as Euler degrees | 50-67; 80-86 |
| `RelationshipComponent` ("Relationship") | `UUID Parent`, `std::vector<UUID> Children` (authoritative child order) | Hidden, NotRemovable, NoSerialize (written as "Parent") | 69-74; 88-91 |
| `PrefabInstanceComponent` ("PrefabInstance") | `Prefab`, `PrefabEntityID`, `PrefabVersion`, `SyncedHash`, `Overrides` | EngineAdded; IDs/hashes as read-only custom string properties; overrides via `.Extra` | 83-118; 103-147 |
| `CameraComponent` ("Camera") | projection, FOV, near/far, ortho size, Primary, ClearColor, depth of field (FocusDistance, FocusEntity, Aperture, SensorHeight) | Category Rendering; section "Depth of field"; 11 inactive reasons | 124-156; 153-185; `Components.cpp` (`GetProjection`, reversed-Z) |
| `MeshRendererComponent` (type only) | Mesh, Material, CastShadows | declared here because physics and animation read it; registered by the Renderer | 158-165 |
| `SkinComponent` (type only) | `UUID Animator` | declared here so the renderer can read it; registered by Animation | 171-182 |

Unregistered runtime-only components (never serialized, copied by `Scene::Copy` by hand, never shown):
`HierarchyComponent` (`S/Scene/SceneHierarchy.h` 14-37), `WorldTransformComponent` (`Components.h` 76-81),
`SubSceneComponent` (`S/Scene/SubScene.h` 20-24), `UnknownComponentsComponent` (`S/Scene/UnknownComponents.h` 13-26).
Documented: AR "Engine modules" l.261-274; DG "Architecture rules" (Module registration) l.1013-1021; SK §1.

### 1.3 Hierarchy and world transforms

| Feature | Where | Documented | Release |
| --- | --- | --- | --- |
| Dual hierarchy: `RelationshipComponent` (UUIDs, serialized, authoritative order) mirrored by `HierarchyComponent` (EnTT handle links: parent, first/last child, prev/next sibling, depth, child count, cached sibling index, dirty flags) | `SceneHierarchy.h` 14-37; `Scene.cpp` 942-1104 (`LinkLast`, `LinkAt`, `Unlink`, `RebuildChildList`) | AR "Scene caches" (table row 1) | 0.3.0 (wave 1 `scene-core`) |
| `SetParent(child, parent, keepWorldTransform)`: refuses cycles, keeps world pose by default, emits the child's Relationship `on_update` | `Scene.h` 309-313; `Scene.cpp` 1270-1304 | AR "Scene caches"; header | 0.3.0 |
| `SetSiblingIndex`, `GetSiblingIndex` (lazy renumbering per sibling list), `PlaceEntities` (batch move for undo), `IsDescendantOf`, `CountSubtree`, `GetDepth` | `Scene.h` 314-345; `Scene.cpp` 1105-1125, 1254-1446 | AR "Scene caches" (Sibling positions, Batches) | 0.3.0 |
| `CompareHierarchyOrder(a, b)`: depth-equalize, climb to common parent, compare sibling indices | `Scene.cpp` 1448-1476 | header `Scene.h` 340-343 | 0.3.0 |
| `GetEntitiesInHierarchyOrder` cached per hierarchy version; `GetHierarchyVersion`; `GetHierarchyMoves(since)` bounded log (`c_MaxHierarchyMoves` 4096) | `Scene.h` 289-303; `Scene.cpp` 883-930 | AR "Scene caches" (Hierarchy moves) | 0.3.0 |
| Cached world matrices (`WorldTransformComponent::Matrix`), recomputed by `UpdateWorldTransforms` only below dirty entities, level by level, in parallel once a level has ≥1,024 independent subtrees (`c_ParallelTransformWidth`, `Scene.cpp` 33) | `Scene.h` 347-350; `Scene.cpp` 1482-1752 | AR "Scene caches" (Dirty transforms) | 0.3.0 |
| `HasDirtyAncestor` memoized per update pass (linear total) | `Scene.cpp` 1530-1562 | AR "Scene caches" (Dirty transforms) | 0.3.0 |
| `GetWorldTransform` exact at any time (cache or top-down recomputation that matches the cache bit for bit); `FindCurrentWorldTransform` read-only for worker threads | `Scene.cpp` 1754-1787, 1506-1522 | header 351-357 | 0.3.0 |
| `SetWorldTransform`: inverse of parent world (refuses near-singular parents, `c_MinInvertibleDeterminant` 1e-12), decompose, `patch` | `Scene.cpp` 1789-1817 | header 358-361 | 0.3.0 |
| `MarkTransformChanged` / `MarkTransformsChanged`: mark dirty without `on_update` (physics write-back) | `Scene.cpp` 1491-1504 | DG "Architecture rules" (transform contract) | 0.3.0 |
| `InvalidateAllTransforms` | `Scene.cpp` 1524-1528 | header | release not stated |
| Activity in hierarchy: `WorldTransformComponent::ActiveInHierarchy` kept exact at once on Inactive add/remove and reparent; `IsActiveInHierarchy` O(1); `Entity::SetActive` | `Scene.cpp` 1150-1197 (`RefreshSubtreeActivity`), 1199-1241 (`DeactivateEntities`), 2044-2058 | AR "Scene caches" (Activity row) | 0.3.0 |
| Change reports: `GetTransformsVersion`, `GetWorldTransformChanges(since)` (`c_MaxTransformChanges` 16384, returns false after overflow) | `Scene.h` 376-384; `Scene.cpp` 1564-1590 | AR "Scene caches" (Change reports) | 0.3.0 |
| Debug self-check: `ValidateWorldTransforms`, `ValidateHierarchy`, amortized via `AmortizedCheck` (every update ≤512 entities, every few above) | `Scene.h` 386-401; `Scene.cpp` 1829-2037 | AR "Scene runtime lifecycle" (Debug bullet); DG l.1071-1081 | 0.3.0 |
| Diagnostic counters (transform updates, parallel updates, hierarchy order builds, lookup visits, index builds) used by tests to prove "no traversal" | `Scene.h` 403-411 | AR "Scene caches" (last bullet) | 0.3.0 |

### 1.4 Lookups

| Feature | Where | Documented |
| --- | --- | --- |
| Name and tag indices: built on first lookup, kept by Name/Tag signals, hash buckets with swap-remove (constant-time removal), lookups compare strings and order by hierarchy | `Scene.h` 685-700; `Scene.cpp` 733-865, 2060-2082 | AR "Scene caches" (Name and tag row) |
| `FindEntityByName`, `FindEntitiesByTag`, `HasChildNamed` (cheaper of children/name bucket) | `Scene.h` 271-280 | same |
| `GetPrimaryCameraEntity`: view over `CameraComponent`, first active Primary in hierarchy order | `Scene.cpp` 867-881 | AR "Scene caches" (Primary camera) |
| `GetAllEntitiesWith<...>()` = `registry.view` | `Scene.h` 679-683 | — |

### 1.5 Scene systems, runtime lifecycle and time

| Feature | Where | Documented | Release |
| --- | --- | --- | --- |
| `SceneSystem` interface: `OnRuntimeStart`, `OnRuntimeStarted`, `OnRuntimeStop`, `OnUpdate`, `OnFixedUpdate`, `OnLateUpdate`, `OnPausedChanged`, `OnPausedUpdate`, `OnEntityDestroying` | `S/Scene/SceneSystem.h` 26-62 | AR "Scene runtime lifecycle" | 0.3.0 |
| `SceneRuntimeMode::Play` vs `Simulate` (physics only); `RunsInSimulateMode` | `SceneSystem.h` 20-24, 67 | AR same, table | 0.3.0 |
| `SceneSystemDescriptor` with hard (`After`/`Before`) and soft (`AfterIfPresent`/`BeforeIfPresent`) order constraints, `ProfileStage`, `Calls*` flags, `PrepareLoadedScene` hook | `SceneSystem.h` 64-102 | AR same ("Update order", "Per-frame calls", "Profiling") | 0.3.0 (wave 1 `module-foundation`); `PrepareLoadedScene` later, release not stated |
| `MakeSceneSystemDescriptor<T>`: records the type for `Scene::GetSystem<T>` and detects at compile time which callbacks `T` overrides (`decltype(&T::OnUpdate)` comparison) | `SceneSystem.h` 104-138 | AR "Per-frame calls"; DG Module registration | release not stated |
| `SceneSystemRegistry`: Register/Unregister/GetAll; update order = topological order that follows registration order, built from the back with a max-priority queue; cycle description; refuses changes while any scene runs | `SceneSystem.h` 140-162; `S/Scene/SceneSystem.cpp` 11-274 (`ComputeUpdateOrder` 77-~170, `DescribeCycle` 36-66) | AR "Update order" | 0.3.0 |
| Built-in update order: UI, Scripting, Animation, World, Physics, Audio (registered by their modules) | AR table l.965-972 of the file; test `SceneSystemTests.cpp` 151 | AR "Scene runtime lifecycle" table | — |
| `OnRuntimeStart`/`OnRuntimeStop`: reset clocks, create systems in update order, two-phase start, reverse-order stop and destruction | `Scene.cpp` 2088-2170 | AR timeline block | 0.3.0 |
| `OnUpdateRuntime`: sub-scenes first; paused path; `OnUpdate` → fixed-step accumulator loop (`OnFixedUpdate` ×N, at most `GetMaxFixedSteps`, backlog dropped) → `OnLateUpdate` → flush destruction → world transforms → debug cache check | `Scene.cpp` 2199-2335 (loop 2267-2309) | AR timeline; DG "Fixed rate" | 0.3.0; time dilation and interpolation later |
| `OnUpdateEditor`: sub-scenes + world transforms only | `Scene.cpp` 2355-2369 | AR | 0.3.0 |
| Pause, `Step(n)`, `GetStepFrames`, `GetFixedStepCount` (the game's own time base) | `Scene.h` 427-438; `Scene.cpp` 2337-2353 | DG "Stepping a paused game" | release not stated |
| Time scale, unscaled time (`GetUnscaledDeltaTime`, `GetUnscaledTime`), `GetTime`, `GetFrameIndex` | `Scene.h` 455-463 | RN 0.5.0 (unscaled time for pause menus) | 0.5.0 (unscaled) |
| Time dilation: catch-up steps stop once they took longer in wall time than they simulated; `GetDroppedFixedStepCount` | `Scene.h` 465-475; `Scene.cpp` 2272-2304 | AR "Time dilation" bullet | release not stated |
| `GetFixedTimestep`/`GetMaxFixedSteps`: project rate wins over `SceneSettings` | `Scene.h` 439-453; `Scene.cpp` 244-251 | DG "Fixed rate" | wave 8 (unreleased) |
| `SceneSettings` (gravity, fixed step, max steps, physics capacity, sub-scene entity budgets) | `Scene.h` 42-79 | AR "Scene runtime lifecycle" (`SceneSettings` bullet) | 0.3.0; capacity 0.5.0 |
| Entity-destruction notification `OnEntityDestroying` (descendants first, entity still valid) | `SceneSystem.h` 58-61; `Scene.cpp` 569-592 | AR bullet after timeline | 0.3.0 |

### 1.6 Scene services (how systems of different modules talk)

`Scene::RegisterService<T>`/`UnregisterService<T>`/`GetService<T>` (`Scene.h` 546-566; `Scene.cpp` 2182-2197): one
provider per interface, keyed by `entt::type_id<T>().hash()`. Interfaces in `S/Scene/SceneServices.h` (594 lines):
`ICollisionEventSource` (87), `IBodyMotionQuery` (113), `IBodyControl` (137), `IPhysicsQueries` (175), `ICharacterControl`
(217), `IAudioPlayback` (242), `ISkinningPoses` (293), `IAnimatorControl` (321), `IAnimationEventSource` (369),
`IPhysicsCapacity` (401), `IPhysicsDiagnostics` (446), `IWorldStreaming` (485), `IUIEvents` (538), `IUIControl` (552), and
the engine service `IAudioOutput` (584). Documented AR "Scene services" (table of providers and consumers). The *contents*
of each service belong to other areas (physics, audio, animation, world, UI); this area owns the mechanism.

### 1.7 Interpolation of fixed-step motion (wave 8, unreleased)

| Feature | Where | Documented |
| --- | --- | --- |
| Switch `SetInterpolation`, `IsInterpolating` (switch ∧ project's `Scene.Timing.Interpolation` ∧ running) | `Scene.h` 477-491; `SceneInterpolation.cpp` 165-172 | DG "Interpolation" (l.2468-2566) |
| The interpolated set: parallel arrays by slot (entities, `InterpolatedEntry`, drawn matrices) and a slot map by entity index; roles Blend / Compose / Exact | `S/Scene/TransformInterpolation.h` 13-48; `Scene.h` 927-947 | DG "Interpolation" (The set) |
| Capture pass after the steps (`UpdateWorldTransforms(TransformPass::Capture)` records every matrix it overwrites) and set rebuild in 4 phases | `SceneInterpolation.cpp` 240-374 | same |
| Step alpha `1 - (1 - a/h)/n` | `Scene.cpp` 2313-2321; `Scene.h` 492-495 | DG (The alpha) |
| Per-frame rules for writes to set members outside the steps | `SceneInterpolation.cpp` 196-238 | DG (Per-frame writes) |
| Pose blend: lerp translation and scale, normalized lerp of quaternion on the shorter arc | `SceneInterpolation.cpp` 104-116 | DG (The set) |
| Drawn matrices computed lazily (`UpdateDrawnTransforms`, called by `RenderScene::Sync`), `FindDrawnTransform`, `GetDrawnTransform` (exact at any time), `GetDrawnTransformsVersion` | `SceneInterpolation.cpp` 410-525 | DG (Drawn matrices; Rule for renderer code) |
| Breaks (`BreakInterpolation`, teleports), clears (pause, step, timestep change, project turning it off, start/stop) | `SceneInterpolation.cpp` 376-408, 527-575 | DG (Breaks, Clears) |
| Safety net: `c_MaxInterpolatedSpeed` 400 m/s (box3d's max speed) → Exact | `Scene.h` 526-528 | DG (Exact when in doubt) |
| Stats and validation (`GetInterpolationStats`, `ValidateInterpolation`) | `SceneInterpolation.cpp` 577-631 | header |

### 1.8 Sub-scenes (additive loads) and the frame's work budget

| Feature | Where | Documented | Release |
| --- | --- | --- | --- |
| `LoadSubScene(asset, options)`, `BeginAdditiveLoad(prepared)`, `UnloadSubScene`, `FlushSubSceneUnloads`, states Loading/Instantiating/Loaded/Failed/Unloading, `SubSceneStatus` with progress | `Scene.h` 188-268; `S/Scene/SubScene.h`; `S/Scene/SubSceneLoad.h`; `S/Scene/SceneSubScenes.cpp` | AR "Scene runtime lifecycle" (Additive scenes bullet) | 0.3.0 (load slices); unload in slices 0.7.0 (RN 0.7.0 l.227) |
| Membership: `AdoptSubScene`, `SetSubSceneOf`, `GetSubSceneOf`, `FindSubSceneBySource`, `GetSubSceneMembershipVersion` | `Scene.h` 236-258; `SceneSubScenes.cpp` 518-620 | AR same | release not stated (world partition, 0.4.0) |
| `SceneWorkBudget`: per-frame deadline + entity counts shared by all loaders; `FitChunk`, `RecordChunkCost` adaptive chunk sizing | `S/Scene/SceneWorkBudget.h`, `.cpp` | AR same | release not stated |

### 1.9 Scene documents: serialization, streaming writer and reader, cooked form

| Feature | Where | Documented | Release |
| --- | --- | --- | --- |
| `SceneSerializer`: DOM form `{"Strata":{"Format","Version":1},"Scene":{...}}`; `Serialize`, `Deserialize`, `SerializeEntities`/`DeserializeEntities` (snapshots with fresh UUIDs and remapping), settings read/write, `SaveToFile`/`LoadFromFile`, `GetDeserializeCount` | `S/Scene/SceneSerializer.h` 39-92; `.cpp` 1-631 | AR "Scene documents" | 0.3.0 |
| Three-pass entity read: IDs+mapping, entities+components, hierarchy linking with union-find cycle refusal | `SceneSerializer.cpp` 390-~600 | AR "Scene documents" (SceneBuilder bullet) | 0.3.0 |
| Lenient reads: unknown properties and bad values become warnings, not failures; out-of-range values clamped | `ComponentAccess.cpp` 30-96 (strict=false path) | SK §4 | 0.3.0 |
| Unknown components kept verbatim (`UnknownComponentsComponent`), one warning per name, written back unchanged | `UnknownComponents.h`; `SceneSerializer.cpp` 466-492; `SceneDocumentWriter.cpp` 224-~290 | AR "Composition root and registries" (last bullet) | 0.3.0 (wave 1) |
| `SceneDocumentWriter`: one entity per line, byte-identical to `JsonUtils::Dump` of the DOM entity, parallel chunk serialization (4096 entities) with an ordered writer job, references collected, SHA-256 and FNV-1a hashes, cancel and progress, subsets by root, `LeaveOut` | `S/Scene/SceneDocumentWriter.h` 77-209; `.cpp` 1-603 (pipeline 400-509) | AR "Scene documents" (Writer) | 0.4.0 (RN 0.4.0 l.61-64) |
| `SceneDocumentReader`: event-parser stream to an `EntitySink`, any key order, header validated whenever it arrives, `MaxEntities`, cancellation, progress; parallel read of ≥16,384-entity documents by lines or a structure scan | `S/Scene/SceneDocumentReader.h`; `.cpp` 1-969 (`DocumentHandler` 143, `FindEntityLines` 515, `StructureScanner` 561, `Read` 787) | AR "Scene documents" (Reader, Parallel read) | 0.4.0 |
| Sinks: `EntitySink` interface; `SceneBuilder` (into a scene); `EntityPrototypeBuilder` (into a prototype, no scene); `EntityColumns`/`PreparedEntities` (columnar parse on workers) | `S/Scene/EntitySink.h` 29-201; `.cpp` 1-624 (`LinkParents` union-find 92-~140, `SceneBuilder::Finish` 397-470) | AR same | 0.4.0 |
| `SceneReadProgress` (thread-safe per-asset read progress) | `S/Scene/SceneReadProgress.h`, `.cpp` | AR "Scene runtime lifecycle" (scene loads bullet) | release not stated |
| Cooked scenes "STSC" v1: 64-byte header + CRC-32C, 16-byte aligned sections (strings, scene info, IDs, parents, component types, one column per type, unknown components), properties via `PropertyBinary`, extra data binary or MessagePack; validated before use; parallel column decode | `S/Scene/CookedScene.h` 22-158; `.cpp` 1-947 | AR "Scene documents" (Cooked scenes) | 0.4.0 (RN 0.4.0 l.64-65) |
| Scene settings and stored 0.5.0 collision layers in documents | `SceneSerializer.cpp` 133-235 | DG "Collision layers" (Stored tables) | 0.6.0 moved layers out |

### 1.10 Prefabs, models and scene assets as data

| Feature | Where | Documented | Release |
| --- | --- | --- | --- |
| `EntityPrototype`: a compiled, immutable entity hierarchy (hierarchy-order arrays of IDs, parent indices, per-type `ComponentValueArray`s, entity-reference list); `Compile(scene)`, `FromSnapshot`, `Serialize` | `S/Scene/EntityPrototype.h` 24-118; `.cpp` 1-257 (`FindReferences` 127-158) | AR "Scene runtime lifecycle" (Compiled prefabs) | release not stated (measured 17 ms → 0.3 ms per 1,000-entity prefab) |
| Instantiation: `BeginInstantiation`/`ContinueInstantiation` (slices, skipped orphans, KeepIDs collision checks, references remapped, prefab links, on_update for every component)/`Instantiate` | `Scene.h` 163-186; `S/Scene/SceneInstantiation.cpp` 41-293 (core 95-271) | AR same | 0.3.0 |
| `EntityTemplate` (asset base) with `Instantiate`, `InstantiateMany`, `CompareInstance`, `GetSnapshot`; `Prefab` (`.stprefab`, authored, `CreateFromEntities`, `WriteDocument`); `Model` (imported, read-only) | `S/Scene/Prefab.h` 19-121; `Prefab.cpp` 79-345 | AR same; MP | 0.3.0 |
| `SceneAsset`: the loader reads the document into a *prepared scene* once; `TakePreparedScene` hands it over without a copy; `CreateScene` copies | `Prefab.h` 123-168; `Prefab.cpp` 347-434 | AR "Scene assets are read once" | release not stated |
| Loaders for Scene, Prefab, Model registered by the Scene module | `S/Scene/SceneRegistration.cpp` 24-40 | AR "Composition root and registries" | 0.3.0 |
| Prefab instances: instance roots, `ExtractTemplate`, `MakeTemplate`, `Compare`, `Replace` (revert), `ReplaceTemplate` (apply), `Link`, `Unpack`, `StripLinks`, version/hash bookkeeping (`GetPartVersion`, `GetContentHash`, `MarkSynced`, `IsOutdated`, `IsUnchangedSinceSync`, `PartVersionCache`) | `S/Scene/PrefabInstances.h` 20-133; `.cpp` 1-618 | AR "Editor" → "Prefab instances" (l.3753-3800); DG "Prefab instances" (l.2854-2880); MP | 0.3.0 (linked instances); version/hash catch-up 0.4.0 |
| Per-property overrides: `PrefabOverride {Entity, Component, Property, Kind}` (Property, AddedComponent, RemovedComponent, RemovedEntity; scripts as `Script`/`<Class>.<Field>`), `ComputeOverrides` (JSON diff), `UpdateOverrides` (incremental), `Propagate` (prefab change reaches instances except overrides), `Revert`, `ApplyToPart`, caches | `S/Scene/PrefabOverrides.h` 22-127; `.cpp` 1-1026 (`CompareComponents` 165-210, `ComputeOverrides` 390-417, `Propagate` 550-~860) | AR same; DG same; MP "Overrides" | 0.4.0 (RN 0.4.0 l.72-75) |
| The root's transform and name are the instance's own, never overrides | `PrefabOverrides.cpp` 160-163 (`IsRootOwn`) | MP "Place instances"; AR | 0.3.0 |

### 1.11 Scene loading

| Feature | Where | Documented | Release |
| --- | --- | --- | --- |
| `SceneLoader::LoadAsync` → `SceneLoadRequest` (states LoadingScene, LoadingDependencies, Preparing, Ready, Failed, Cancelled; pins its dependency closure; residency-aware; `Prepare` and `PrepareSystems` hooks; `TakeScene`, `Cancel`, `GetProgress`) | `S/Scene/SceneLoader.h` 17-307; `.cpp` 1-342 | AR "Scene loads never stop the frame" | 0.3.0 (background loads); cancel 0.4.0 |

The residency and closure parts of loading are the asset area's; this area owns the state machine and the hand-over.

### 1.12 Reflection

| Feature | Where | Documented | Release |
| --- | --- | --- | --- |
| `PropertyType` (14 types: Bool, Int, UInt, Float, Vec2-4, Quat, Color3/4, String, Enum, Asset, Entity) and `PropertyValue` variant (10 alternatives) | `S/Reflection/Property.h` 22-48; `Property.cpp` 11-102 | AR "Engine modules" (Reflection paragraph, l.250-259) | 0.3.0 |
| `PropertyInfo`: name, display name, tooltip, section, type, flags, range, speed, asset filter, enum values, type-erased getter/setter, inactive reason; `SetValue` validates/clamps; `IsInRange` for commands | `Property.h` 72-112; `Property.cpp` 136-~314 | same | 0.3.0; sections 0.7.0; inactive reasons by 0.4.0 |
| `PropertyFlags` (ReadOnly, Hidden, Transient, MultiLine, Slider, PowerOfTwoLimit, PhysicsLayer) | `Property.h` 50-61 | SK §2 | release not stated per flag |
| `PropertyBuilderBase<T, Derived>` (CRTP): `Property` (type deduced from the member pointer), `EnumProperty`, `AssetProperty`, `EntityProperty`, `CustomProperty`, `Section`; `PropertyListBuilder` for non-component structs (materials) | `S/Reflection/PropertyBuilder.h` 17-145; `.cpp` | SK §2; DG "Inspectors" (Sections) | 0.3.0 |
| `PropertyOptions` helpers: `Range`, `Slider`, `Color`, `WithTooltip`, `c_Unbounded` | `S/Reflection/PropertyOptions.h` | SK §2 | release not stated |
| `ComponentInfo`: metadata + ~20 type-erased operations (`Has`, `Get`, `Add`, `Remove`, `MarkModified`, `Copy`, `AssureStorage`, `CopyStorage`, `CreateValueArray`, `EmplaceCopy`, `Observe`, `SerializeExtra`/`DeserializeExtra`, `ExtraReferences`, `SerializeExtraBinary`/`DeserializeExtraBinary`, `Gizmo`, `Requires`) | `S/Reflection/ComponentRegistry.h` 154-213 | AR "Composition root and registries" | 0.3.0 (grew over waves) |
| `ComponentFlags` (Hidden, NotRemovable, NoCopy, NoSerialize, EngineAdded) | `ComponentRegistry.h` 24-33 | SK §2 | release not stated |
| `ComponentRegistry` lifecycle Closed→Open→Frozen; `Register<T>(name)` fills the type-erased lambdas; refusals return a builder that discards; case-insensitive names; `Find<T>`, `Find(name)`, `FindByTypeId`, `GetAll` (registration order) | `ComponentRegistry.h` 218-262, 382-476; `ComponentRegistry.cpp` 1-183 | AR "Component lifecycle" | 0.3.0 (wave 1) |
| `ComponentInfoBuilder<T>`: `DisplayName`, `Category`, `Description`, `Flags`, `Requires`, `Extra`, `Gizmo`, `ExtraReferences`, `ExtraBinary` | `ComponentRegistry.h` 286-380 | SK §2 | release not stated |
| `ComponentRegistry::SetInactiveReason<T>(property, fn)` | `ComponentRegistry.h` 249-258; `.cpp` 93-119 | DG "Inspectors"; SK §2; AG "Editor" | by 0.4.0 (RM wave 4 mentions UI inactive reasons) |
| `Requires`: dependent components added first by `ComponentAccess::AddComponent`; `Freeze` drops bad requirements | `ComponentRegistry.h` 202-205, 324-329; `.cpp` 61-81; `ComponentAccess.cpp` 153-206 | AR "Component lifecycle" | release not stated (game UI, 0.4.0) |
| `ComponentValueArray` / `TypedComponentValueArray<T>`: components kept outside registries (prototypes) | `ComponentRegistry.h` 45-127 | AR "Compiled prefabs" | release not stated |
| `ComponentExtraReferences` (Visit, Set, Equals, VisitJson): entity/asset references inside non-property data (script fields) | `ComponentRegistry.h` 129-151 | AR "Extra data and its references" | release not stated |
| `ComponentObserver` + `Observe`: generic listeners of a type's signals | `ComponentRegistry.h` 35-43, 465-473 | header | release not stated |
| `ComponentGizmo`: shapes a component asks the editor to draw (Box, Sphere, Capsule, MeshBounds) | `S/Reflection/ComponentGizmo.h` | header | release not stated |
| Canonical JSON of values (`PropertyValueToJson`), lenient parsing for agents (`PropertyValueFromJson`: vectors as objects, Euler for quats, enum by name or int, UUID forms), `FloatToJson` shortest round-trip, `AppendFloatJson`/`AppendPropertyValueJson` (no DOM), `DescribeProperty` for tools | `S/Reflection/PropertyJson.h` 13-41; `.cpp` 1-519 | AR "Scene documents" (Writer) | 0.3.0; Append* 0.4.0 |
| Binary property values for cooked scenes (`WritePropertyValue`, `ReadPropertyValue`, `c_MaxBinaryStringBytes` 1 MiB) | `S/Reflection/PropertyBinary.h`, `.cpp` | AR "Cooked scenes" | 0.4.0 |
| `ComponentAccess` (in Scene): the single validated read/write path used by serializer, inspector, commands, undo, scripts | `S/Scene/ComponentAccess.h` 17-45; `.cpp` 1-253 | AR Reflection paragraph | 0.3.0 |

### 1.13 Projects and settings

| Feature | Where | Documented | Release |
| --- | --- | --- | --- |
| `Project`: `.stproj` (format v3), layout (asset dir, scripts, `.strata/` intermediate with Cache, Scripts/Build, Scripts/Bin), `Create`, `Load` (validates sections with a registry), `Save`, `MakeFileText`, 1 MiB cap, unknown members kept, active project | `S/Project/Project.h` 20-141; `Project.cpp` 1-491 (`Load` 208-324) | AR "Engine modules" (Project paragraph l.513-520); DG "Project settings" (The project file) | 0.3.0; v3 file 0.6.0 |
| `ProjectScriptSettings`, `MakeScriptModuleName`, `IsValidScriptModuleName` | `Project.h` 22-30, 120-124; `Project.cpp` 446-479 | DG "Building and loading scripts" (scripting area) | 0.3.0 |
| `ProjectExportSettings` (`AlwaysInclude`, `LoadingScene`) | `Project.h` 32-40 | DG "Exporting games" | release not stated |
| `ProjectGameInfo` (title, version, company, copyright, icon; validation, version parsing) | `S/Project/GameInfo.h`, `.cpp` | DG "Project settings" (The project file); MS "Game" | 0.6.0 (RN 0.6.0 l.101-107) |
| `GameManifest` (`.stgame` v5: name, identity, packs, start/loading scene, script module, window, settings kept unvalidated) | `S/Project/GameManifest.h` 21-79; `.cpp` | AR Project paragraph; DG "Project settings" (Exported games) | v5 0.6.0 |
| `ProjectModule` (`EngineModule` that releases the active project and asset manager at shutdown) | `S/Project/ProjectModule.h`, `.cpp` | AR "Engine modules" | release not stated |
| Settings sections: `SettingsSection` (simple: `Fields`; complex: `Schema`, `MakeDefault`, `Read`, `References`), `SettingsField` (Bool, Int, Float, String, Enum, Asset), scopes Project/User, versioned values with upgrade, single `Validate`, 512 KiB value cap | `S/Core/SettingsRegistry.h` 25-103; `.cpp` 1-387 | DG "Project settings" (l.1146-1244) | 0.6.0 |
| `SettingsRegistry` (process registry, frozen with components; local registries for tests); id rule `<Module>.<Name>` | `SettingsRegistry.h` 109-137 | same | 0.6.0 |
| `IProjectSettings` engine service + `ProjectSettingsValues` (keeps unclaimed/invalid sections verbatim, provides only validated ones, process-unique version, stored entries for undo) | `S/Core/ProjectSettings.h` 24-98 | same ("Reading", "The project file") | 0.6.0 |
| Section `Scene.CollisionLayers` (complex; `PhysicsLayerSettings` 32 named layers + symmetric collision matrix; working copy per scene via `Scene::ApplyProjectLayers`) | `S/Scene/PhysicsLayerSettings.h` 17-112; `ProjectCollisionLayers.h` 13-40; `.cpp`; `Scene.cpp` 208-227 | DG "Collision layers" (l.1292-1341); MS | 0.6.0 |
| Section `Scene.Timing` (simple: `FixedRate` enum Scene/30/60/120/240, `Interpolation` bool), `GetMaxSteps` = ceil(rate·2/15) | `ProjectSceneTiming.h` 14-49; `.cpp` 45-123; `Scene.cpp` 229-242 | DG "Fixed rate" (l.1384-1441); MS "Timing" | wave 8 (unreleased) |
| Other project sections registered by other areas (for the full list): `Input.Actions`, `Renderer.Quality`, `Physics.Simulation`; user sections `Editor.Interface`, `Editor.ExternalEditor`, `Editor.FrameRate` | `S/Input/InputActionSet.h` 132; `S/Renderer/RendererQuality.h` 188; `S/Physics/PhysicsSimulationSettings.h` 20; `StrataEditor/src/Editor/EditorInterface.h` 16, `ExternalEditor.h` 54, `EditorFrameRate.h` 19 | DG "Project settings", "Preferences" | 0.6.0/0.7.0/wave 8 |
| Hand-over pattern: scenes built on workers never read the service; the main thread applies project values when a scene is handed over (`TakePreparedScene`, `TakeScene`, editor adoption, every settings change) | `Scene.h` 660-674 | DG "Collision layers" (Hand-over), "Fixed rate" (Hand-over) | 0.6.0 |

### 1.14 Registration of the Scene module

`RegisterSceneModule` (`S/Scene/SceneRegistration.cpp` 14-41) registers the components, the two settings sections and
the three loaders; the composition root `Engine::RegisterBuiltinModules` (`S/Engine/BuiltinModules.cpp` 61-76 table, 134-160
open/freeze) calls it second, after Input. Note: the header comment in `SceneRegistration.h` (lines 6-9) names only
`Scene.CollisionLayers`, while the code also registers `Scene.Timing` (stale comment).

### 1.15 User-visible surfaces that sit on this area (owned by the editor area, listed so the book covers them)

Editor commands: `entity.create/delete/duplicate/copy/paste/rename/setActive/setParent/find/get/dropToGround`,
`component.list/add/remove/get/set`, `scene.new/open/save/saveAs/info/hierarchy/setSettings/loadAdditive/unloadAdditive/
loadStatus/recover/recoveryStatus`, `prefab.create/instantiate/status/apply/revert/unpack/select`,
`project.create/open/openSample/close/save/info/settings/setSettings/setCollisionLayers/setStartScene/
setExportSettings/setGameInfo/export...`, `selection.get/set`, `play.step` (counts `GetFixedStepCount`). Panels: Hierarchy,
Inspector (generic property widgets from reflection, sections, inactive reasons, prefab bar and override marks, scene
settings with nothing selected), Project Settings panel (generic pages for simple sections, custom pages for complex),
Preferences dialog. Sources: `StrataEditor/src/Editor/EditorSceneCommands.cpp`, `EditorPrefabCommands.cpp`,
`EditorProjectSettingsCommands.cpp`, `Editor/PrefabSync.*`, `Editor/ProjectSettingsAction.*`, `Editor/ProjectMigration.*`,
`UI/SettingsPages.*`, `UI/PropertyWidgets.h`, `Panels/InspectorPanel`. Scripts reach entities and components through the
script host (Scripting area).

### How completeness was checked

- Every header of `S/Scene` (27), `S/Reflection` (7) and `S/Project` (4) was read whole and has rows above; the five
  source-only files (`SceneInstantiation.cpp`, `SceneInterpolation.cpp`, `SceneSubScenes.cpp`, `Components.cpp`,
  `ComponentRegistration.cpp`) are covered by their features.
- Every component the Scene module registers (8) and the two types it declares for others (2) are listed (§1.2), checked
  against `RegisterSceneComponents` and `StrataTests/Architecture/ComponentSchema.json` (42 components total).
- Both settings sections the Scene module registers (`Scene.CollisionLayers`, `Scene.Timing`) and every other section id
  in `Strata/src` and `StrataEditor/src` were found by grepping `c_SectionId`/`c_SettingsSection` (§1.13).
- Three asset loaders (Scene, Prefab, Model) from `SceneRegistration.cpp`; no shaders, no host functions in this area
  (scripts' entity API is the Scripting area's; scene services' contents are the other modules').
- Every scene service interface in `SceneServices.h` (15) listed by grepping `class I`.
- Test suites cross-checked: `Scene`, `Scene.Hierarchy`, `Scene.Transforms(.Sweep)`, `Scene.Systems`, `Scene.Services`,
  `Scene.Timing(.Sweep)`, `Scene.SubScenes`, `Scene.Loader`, `Scene.Streaming`, `Scene.Serialization`,
  `Scene.Documents`, `Scene.CookedScene`, `Scene.Prefab`, `Scene.PrefabInstances`, `Scene.PrefabOverrides`,
  `Scene.Robustness`, `Scene.InactiveProperties`, `Reflection`, `Reflection.ComponentSchema`, `Reflection.PropertyBinary`,
  `Project`, `Project.Settings`, `Project.GameManifest`, `Core.Settings` (files under `StrataTests/src/Scene`, `Reflection`,
  `Project`, `Core/SettingsRegistryTests.cpp`; 213 test cases). Perf budgets `Perf.Scene.*` (17 entries in
  `StrataTests/Perf/Budgets.json`).

---

## 2. Concepts to teach (dependency order)

1. **What a scene is.** The problem: a game world is many things (a player, a crate, a light, a camera) that the engine
   must store, find, update, draw, save and load. *Approaches:* object hierarchies with virtual `Update` (classic
   OOP: Unreal's `AActor`, early Unity `MonoBehaviour`), component-based objects (Unity GameObject + components), and
   data-oriented ECS (EnTT, flecs, Unity DOTS, Bevy). *Strata:* an ECS registry (EnTT) whose components are plain data and
   whose behaviour lives in scene systems; a `Scene` class wraps the registry with identity, hierarchy and caches.
   *Newcomer error:* thinking an entity "is" an object with methods; in Strata it is an ID with data attached.
2. **Entities as IDs; two kinds of ID.** EnTT handles (index + version, recycled, fast) versus persistent UUIDs (stable
   across save/load, play copies, network, prefabs). *Strata:* `IDComponent` UUID + `m_EntityMap` dense map; `Entity`
   wraps the handle. *Error:* storing `entt::entity` or `Entity` in saved data or across scene copies; storing a `Ref` or
   pointer to a component (EnTT storages move).
3. **Components as plain data; tag components.** Structs with defaults, no engine pointers; empty "tag" structs carry
   presence only (`InactiveComponent`). *Error:* `GetComponent` on a tag (compile error by design); runtime handles in
   serialized fields (SK §1 rule).
4. **Storage layout: sparse sets.** EnTT keeps one packed array per component type plus a sparse index; iteration over a
   view is cache-friendly; adding/removing is O(1) but moves elements. *Strata uses* the layout implicitly and explicitly
   (`Scene::Copy` copies storages whole and in parallel; `EntityPrototype` keeps values in its own per-type arrays because
   EnTT pages of 1,024 waste memory for small prefabs). *Error:* holding a `T&` across an `emplace`/`remove` of the same
   type.
5. **Signals (observer pattern) and the "write then signal" model.** EnTT `on_construct`/`on_update`/`on_destroy`.
   Systems and caches react to changes instead of polling. In-place writes are invisible until `patch` (`MarkModified`).
   *Error:* writing a field and expecting systems to notice.
6. **Transforms and the scene graph.** Local TRS, composition to world matrices (`parent * local`), quaternions, why
   decomposition can fail (shear, zero scale), reparenting with "keep world transform" (needs the parent's inverse). The
   book's math chapter must precede this. *Strata:* TRS components, cached world matrices, `SetWorldTransform`.
   *Error:* thinking `Translation` is a world position; putting non-uniform scale under rotation and expecting a clean
   decomposition.
7. **Hierarchies in an ECS.** Approaches: parent pointer only, child lists, intrusive linked lists, sorted arrays by depth
   (Unity DOTS `Parent`/`Child`), flattened arrays. *Strata:* a serialized UUID form (`RelationshipComponent`, the
   authoritative child order) mirrored by handle links (`HierarchyComponent`, intrusive doubly linked siblings,
   first/last child for O(1) append, depth, lazily renumbered sibling indices). *Why:* hot paths walk handles without UUID
   lookups; the file keeps stable IDs. *Error:* editing `RelationshipComponent::Children` directly (the links go stale).
8. **Dirty flags and incremental world transforms.** Approaches: recompute everything every frame; dirty flags with
   propagation; change versions. *Strata:* dirty list, "dirty without dirty ancestor" frontier (memoized), level-by-level
   then parallel walk; clean frames cost nothing (`Perf.Scene.CleanTransformUpdate1M`). *Why:* million-entity scenes
   (wave 1 `scene-core`). *Error:* forgetting that a parent's move recomputes the whole subtree.
9. **The transform contract (cache coherence).** Any cache needs every writer to cooperate; Strata enforces it with a
   Debug-only full recomputation (`ValidateWorldTransforms` names the entity), amortized for large scenes. Two signalling
   paths: `on_update` (listeners hear it) and `MarkTransformChanged` (they do not: physics write-back avoids feedback).
   *Error:* direct writes from scripts or systems without a signal; signalling with `patch` from the physics write-back
   (feedback loop).
10. **Activity.** Inactive flags inherited through the hierarchy, kept exact at once. *Error:* checking only
    `HasComponent<InactiveComponent>` instead of `IsActiveInHierarchy`.
11. **Lookups and indices.** Naive scans vs indices maintained by signals; hash buckets with swap-remove; ordering by
    hierarchy. *Error:* calling `FindEntityByName` every frame expecting it to be free when names change constantly (it
    is cheap, but ordering many matches costs).
12. **Game loop time: variable vs fixed step.** The accumulator ("Fix Your Timestep", Glenn Fiedler), spiral of death,
    max steps per frame, dropping backlog, time scale, unscaled time, pause and single-stepping. *Strata:* `OnUpdate` →
    `OnFixedUpdate`×N → `OnLateUpdate`, cap 8 (or 2/15 s at a project rate), optional time dilation for wall-clock owners,
    `GetFixedStepCount` as the deterministic time base for tools. *Error:* reading the step from `SceneSettings`
    (`GetFixedTimestep` is authoritative); counting frames instead of fixed steps in tests.
13. **Systems and update order.** Approaches: hard-coded order, priority numbers, dependency graphs (Bevy's
    `before/after`, Unity's `UpdateBefore`). *Strata:* named constraints, hard vs soft (soft for other modules so builds
    without them work), deterministic topological order that follows registration order (built from the back), refused
    cycles. Systems call only the phases they override (compile-time detection). *Error:* assuming registration order
    alone decides; using a hard constraint toward another module's system.
14. **Decoupling modules: services and layers.** Systems never include each other; they meet through interfaces in the
    lower Scene layer (`GetService<T>`, null when absent). This is dependency inversion. *Error:* `GetSystem<PhysicsSystem>`
    from scripting code (layering violation).
15. **Entity lifetime during iteration.** Deferred destruction while updating, `OnEntityDestroying` before the entity
    goes, batched destruction. *Error:* destroying entities inside a view loop; caching `Entity` handles after destroy.
16. **Reflection.** C++ has no runtime reflection; engines use macros + code generators (Unreal UHT), external
    generators, or registration DSLs (RTTR, EnTT meta, Hazel-style). *Strata:* an explicit builder DSL with member
    pointers and type-erased lambdas (`ComponentRegistry::Register<T>`), deduced property types, frozen registry. *Why:*
    one description drives files, inspector, commands, undo, scripts, cooking; no code generator. *Error:* adding a field
    without registering it (it is silently not saved); renaming a registered name (breaks files).
17. **Type erasure and templates.** `std::function`, `void*` + `static_cast`, CRTP builders, `if constexpr` for tag
    types, `std::variant` for values. Prerequisite C++ for 16.
18. **Validation, ranges and leniency.** Strict (commands) vs lenient (files) reads; clamp vs refuse
    (`SetValue` clamps, `IsInRange` refuses for commands); canonical JSON vs forgiving input for agents.
19. **Inactive reasons and requirements.** UI metadata as data: a property that another turns off says why; components
    that need others get them added first.
20. **Serialization formats.** Text (JSON) vs binary; DOM vs streaming; versioning; forward compatibility (unknown
    properties and unknown components kept verbatim); determinism of bytes (sorted keys, shortest floats) for diffs and
    hashes. *Strata:* one entity per line, parallel serialization with ordered output, event parser with sinks, cooked
    binary for shipping with checksums. *Error:* building a DOM of a huge document; trusting file bytes (cooked reader
    validates everything first).
21. **References between entities and assets in data.** UUID references, remapping on copy/duplicate/instantiate,
    references inside opaque data (`ExtraReferences`). *Error:* forgetting to remap, so copies point at the originals.
22. **Prefabs.** Approaches: copy-on-place (no link), linked instances with overrides (Unity prefabs, Unreal blueprints'
    defaults), nested prefabs. *Strata:* compiled prototype for fast instantiation; linked instances with per-property
    override lists, JSON diff against the prefab's "part", propagation except overrides, version/hash catch-up for scenes
    that were closed; the root's transform and name belong to the instance; no nested prefab editing yet (0.3.0 notes
    "no prefab edit mode"). *Error:* expecting moving the root to count as an override.
23. **Asynchronous loading and time-slicing.** Load on workers into a *prepared* scene, hand over on the main thread,
    prepare in budgeted slices, sub-scenes created and destroyed in slices against a shared per-frame budget with
    adaptive chunk sizes. *Error:* blocking a frame on a load; creating 100,000 entities in one frame.
24. **Interpolation of fixed-step motion.** Why motion judders when frame rate > step rate; approaches: interpolate
    (one step of latency), extrapolate (overshoot), variable-step physics (non-deterministic). *Strata:* state
    interpolation of only what the steps moved, roles Blend/Compose/Exact, drawn transforms separate from simulated ones.
    *Error:* following a body with a camera using its world position instead of its drawn position; moving a carrier in
    `OnUpdate` while its rider moves in fixed steps.
25. **Projects and settings.** What a project is (file + folders + intermediate cache), project vs user scope, settings as
    registered sections (open/closed principle: a new setting is one registration), versioned values and upgrades,
    keeping unknown data, main-thread hand-over to scenes, undoable project changes, carrying settings into exported games.
    *Error:* reading `IProjectSettings` on a worker; assuming a missing section is an error (its default applies).

---

## 3. Code worth showing

| # | File and lines | What it teaches | Reader must know first |
| --- | --- | --- | --- |
| 1 | `S/Scene/Components.h` 50-81 | TRS component, local vs world, relationship by UUID, cached world as separate runtime component | structs, vectors, quaternions (intro) |
| 2 | `S/Scene/Entity.h` 12-114 | A handle class over EnTT: templates, perfect forwarding, `decltype(auto)`, tag `static_assert`, `MarkModified` | templates basics, EnTT registry idea |
| 3 | `S/Scene/Scene.cpp` 386-415 (`CreateEntityWithUUID`) | What every entity gets, order of emplacement and why the hierarchy node comes first | 1, 2 |
| 4 | `S/Scene/SceneHierarchy.h` 14-37 | Intrusive doubly linked hierarchy in components; cached per-update scratch | linked lists |
| 5 | `S/Scene/Scene.cpp` 942-974 (`LinkLast`) | O(1) append keeping UUID list and handle links in step | 4 |
| 6 | `S/Scene/Scene.cpp` 1270-1304 (`SetParent`) | Cycle check, keep-world-transform, depth/activity refresh, signal last | 5, matrix inverse |
| 7 | `S/Scene/Scene.cpp` 1448-1476 (`CompareHierarchyOrder`) | Classic LCA-by-depth algorithm | 4 |
| 8 | `S/Scene/Scene.cpp` 1597-1636 + 1638-1752 (`UpdateWorldTransforms`, `WalkWorldTransforms`) — **central algorithm** | Dirty frontier, level-by-level walk, switch to `ParallelFor`, change log, template-per-hook to avoid per-entity branches | 6, jobs/threads basics |
| 9 | `S/Scene/Scene.cpp` 1530-1562 (`HasDirtyAncestor`) | Memoization with a pass counter to keep the total linear | 8 |
| 10 | `S/Scene/Scene.cpp` 1754-1787 (`GetWorldTransform`) | Exact answer between updates, same association as the cache | 8 |
| 11 | `S/Scene/Scene.cpp` 194-206 (`ConnectSignals`) + 2039-2082 (handlers) | How caches subscribe to EnTT signals | signals concept |
| 12 | `StrataTests/src/Scene/SceneTransformTests.cpp` 368-388 | The transform contract proved by a test: unsignalled write caught, `MarkTransformChanged` repairs | 8, 11 |
| 13 | `S/Scene/Scene.cpp` 733-791 (lookup index) | Hash buckets with swap-remove and per-entity slots | hash maps |
| 14 | `S/Scene/SceneSystem.h` 26-62, 104-138 | System interface; compile-time override detection with `decltype(&T::OnUpdate)` | virtual functions, type traits |
| 15 | `S/Scene/SceneSystem.cpp` 67-~170 (`ComputeUpdateOrder`) | Topological sort with a priority queue built from the back; hard vs soft edges; cycle reporting | graphs, topological sort |
| 16 | `S/Scene/Scene.cpp` 2199-2335 (`OnUpdateRuntime`), esp. 2263-2322 — **central algorithm** | Fixed-step accumulator, max steps, backlog drop, time dilation, step alpha | game loop chapter |
| 17 | `StrataTests/src/Scene/SceneTests.cpp` 486-527 | The accumulator's behaviour as numbers (0.035 s → 3 steps, carry 0.005, pause/step, cap) | 16 |
| 18 | `S/Scene/SceneInterpolation.cpp` 104-116 (`BlendPose`) | Lerp + nlerp on the shorter arc, why not `glm::mix`/slerp | quaternions |
| 19 | `S/Scene/SceneInterpolation.cpp` 240-374 (`CaptureInterpolation`) | Building the set from a capture pass, roles, exits logged, parent slots, breaks | 16, 8 |
| 20 | `S/Reflection/ComponentRegistry.h` 382-476 (`Register<T>`) — **central mechanism** | Type erasure: one template fills ~15 lambdas; `if constexpr` for tags | lambdas, `std::function`, `void*` |
| 21 | `S/Reflection/PropertyBuilder.h` 17-65 | Type deduction from member pointers; CRTP fluent builder | pointers to members, CRTP |
| 22 | `S/Scene/ComponentRegistration.cpp` 153-185 | A real registration: ranges, tooltips, sections, inactive reasons | 20, 21 |
| 23 | `S/Reflection/Property.cpp` 192-~280 (`PropertyInfo::SetValue`) | Validation by type, enum membership, clamping, finiteness, quat normalization | `std::variant`, `std::visit` |
| 24 | `S/Scene/ComponentAccess.cpp` 30-96 and 117-146 | Strict vs lenient deserialization; set-then-signal | 20, 23 |
| 25 | `S/Scene/ComponentAccess.cpp` 153-192 (`AddWithRequirements`) | Recursive requirement resolution with cycle guard | recursion |
| 26 | `S/Scene/SceneSerializer.cpp` 73-128 (`RemapEntityReferences`) | Generic reference remapping through reflection and `ExtraReferences` | 20 |
| 27 | `S/Scene/SceneDocumentWriter.h` 77-94 + a sample file: `Samples/OpenWorld/Assets/Scenes/Loading.stscene` (new layout) vs `Samples/Tetris/Assets/Scenes/Main.stscene` (old tab-indented, sorted keys) | What a scene file looks like, why one entity per line | JSON |
| 28 | `S/Scene/SceneDocumentWriter.cpp` 400-509 | Two-batch pipeline: parallel serialize, ordered write, deterministic bytes | jobs |
| 29 | `S/Scene/EntitySink.h` 29-50 + `EntitySink.cpp` 397-470 (`SceneBuilder::Finish`) | Streaming visitor; link after all entities exist; signal last | 27 |
| 30 | `S/Scene/SceneInstantiation.cpp` 95-271 (`ContinueInstantiation`) | Prototype copy in slices: checks first, create, link, remap, link to prefab, signal | 20, 26 |
| 31 | `S/Scene/PrefabOverrides.cpp` 160-210 (`IsRootOwn`, `CompareComponents`) | Diff of two JSON component maps into override records | JSON, prefabs concept |
| 32 | `S/Scene/ProjectSceneTiming.cpp` 45-123 | A complete simple settings section: fields, default, description for agents, cached `Find` keyed by provider version | settings concept |
| 33 | `S/Core/SettingsRegistry.h` 45-103 | The section model (simple vs complex) | 32 |
| 34 | `S/Scene/PhysicsLayerSettings.h` 24-112 | Bit masks, symmetric matrix, a complex section's value | bit operations |
| 35 | `S/Project/Project.cpp` 208-324 (`Project::Load`) | Defensive file loading: size cap, header check, versions, keep unknown members, validate sections | JSON, error handling |

(35 candidates; the planner can pick 10-30. The bold central ones are 8, 16, 20.)

---

## 4. Figures

### Diagrams

1. **Scene anatomy** (data structure): `Scene` → `entt::registry` (storages per component type) + `m_EntityMap`
   (UUID→handle) + root list + caches (dirty list, change logs, name/tag index, hierarchy order) + systems + services.
2. **Sparse-set storage** (memory layout): sparse array indexed by entity index → dense array of entities → parallel
   packed component array; show add/remove (swap with last) and a view intersecting two storages.
3. **Entity handle vs UUID** (diagram): 32-bit `entt::entity` split into 20-bit index and version; UUID 64-bit; which
   survives save/load/copy.
4. **Dual hierarchy** (memory layout): a small tree drawn twice: `RelationshipComponent` (UUID parent + child vector) and
   `HierarchyComponent` (Parent/FirstChild/LastChild/Prev/Next arrows, Depth, SiblingIndex).
5. **Transform composition** (math): local TRS → matrix; world = parent world × local; inverse for `SetWorldTransform`.
6. **Dirty propagation** (algorithm walk-through): a tree with three marked entities, one under another; frontier
   selection; level-by-level walk; switch to parallel at 1,024 subtrees; change log entries with versions.
7. **Signal flow** (data flow): writer → `patch`/`MarkTransformChanged` → `OnTransformChanged` → dirty list →
   `UpdateWorldTransforms` → `WorldTransformComponent` → change log → readers (render scene, physics). Contrast with the
   unsignalled write that the Debug check catches.
8. **Runtime lifecycle** (state machine): Not running → `OnRuntimeStart` (create systems, Start, Started) → Running
   (paused/unpaused/stepping substates) → `OnRuntimeStop` (reverse stop, destroy) → Not running.
9. **One runtime frame** (timeline): UpdateSubScenes → UpdateWorldTransforms → OnUpdate (all systems) → [interpolating:
   settle] → OnFixedUpdate × N (accumulator bar) → [capture] → step alpha → OnLateUpdate → flush destroys →
   UpdateWorldTransforms → Debug check. Annotate which built-in systems take part in each phase.
10. **Accumulator timeline** (timeline): wall-clock frames of uneven length over a ruler of fixed steps; steps run per
    frame; remainder carried; backlog drop at the cap; time dilation case.
11. **System order graph** (graph): the six built-ins with soft edges; a user "Wind" before Physics and an unconstrained
    "CameraFollow" registered between them, showing why the order is built from the back.
12. **Services** (component diagram): Scripting/Audio/Animation/UI/Physics/World modules, all depending on the Scene layer's
    interfaces, never on each other; null when a module is absent.
13. **Interpolation** (timeline + roles): poses at T−nh and T, drawn time T+a−h, alpha; a body (Blend) with a child light
    (Compose) and a teleported crate (Exact).
14. **Reflection model** (class diagram): `ComponentRegistry` → `ComponentInfo` (metadata + type-erased ops) →
    `PropertyInfo` (getter/setter, range, flags, inactive reason); consumers around it: serializer, inspector, commands,
    undo, scripts, cooker, prefab diff.
15. **Registration lifecycle** (state machine): Closed → Open (modules register in table order, then asset pipeline,
    then Extra) → Frozen; what fails in each state.
16. **Scene document layout** (annotated file): header, Name, Settings, EntityCount, one entity per line; old layout
    comparison.
17. **Streaming read** (data flow): text → event parser → `DocumentHandler` → sink (`SceneBuilder` / `EntityPrototypeBuilder`
    / reference scanner); parallel path: line split → chunk jobs → `EntityColumns` → in-order hand-off.
18. **Write pipeline** (timeline): two batches; batch k serialized in parallel while batch k−1 is written and hashed.
19. **Cooked scene file** (memory layout): 64-byte header fields, section table, aligned sections, a column (dense flag or
    indices, then per-property value runs).
20. **Prefab data flow** (data flow): `.stprefab` → `EntityTemplate::Read` → `EntityPrototype` → `ContinueInstantiation` →
    linked instance entities (`PrefabInstanceComponent`); apply/revert/propagate arrows; overrides list on the root.
21. **Override computation** (worked example): prefab part JSON vs instance template JSON side by side, the resulting
    `PrefabOverride` records.
22. **Scene load state machine**: LoadingScene → LoadingDependencies → Preparing → Ready / Failed / Cancelled; who calls
    `Update`, where `TakeScene` and `ApplyProjectLayers/Timing` happen.
23. **Sub-scene lifecycle** (state machine): Loading → Instantiating (slices) → Loaded → Unloading (slices) → gone;
    Failed; membership via top-level `SubSceneComponent`.
24. **Project on disk** (tree): `<Name>.stproj`, `Assets/` (with `.meta` files), `Scripts/`, `.strata/Cache`,
    `.strata/Scripts/Build`, `.strata/Scripts/Bin`, `.strata/Saves`; and the exported game folder with `.stgame`.
25. **Settings flow** (data flow): module registers section → process registry frozen → `.stproj` "Settings" →
    `ProjectSettingsValues::Validate` → `IProjectSettings` provider (editor/runtime) → module `Find()` cached by version →
    main-thread hand-over to scenes; export → manifest → `GameRuntime` validates.

### Screenshots (editor; this area has no rendering feature of its own)

1. **Hierarchy panel** with a nested tree (e.g. `Samples/ThirdPerson` start scene) and the same entities' Inspector,
   showing Name, Transform, Tag; to pair with diagram 4.
2. **Inspector of a Camera** with Projection = Orthographic: the perspective fields drawn disabled with the inactive
   reason tooltip ("The camera's projection is Orthographic"); and Depth Of Field off greying Aperture etc. Toggle via
   `component.set {component: "Camera", property: "Projection", value: "Orthographic"}`.
3. **Inspector sections**: a Directional Light or Post Process with section headings (any sample with a sun).
4. **Add Component menu** grouped by category (shows `Category` metadata).
5. **Inspector of a prefab instance**: prefab bar (Select, Open, Overrides menu) and an overridden property (bold label,
   accent bar); `Samples/OpenWorld` has prefabs (`Assets/Prefabs/Fox.stprefab`, `Nature/*.stprefab`). Make an override
   with `component.set` on an instance entity, show `prefab.status` output beside it.
6. **Prefab placement ghost** while dragging a prefab into the Scene view (MP "Place instances").
7. **Inspector with nothing selected**: scene settings (gravity, fixed step, physics capacity, sub-scene budgets,
   collision layers count, Graphics Quality link); with `Scene.Timing` FixedRate = 120 the Fixed Timestep rows inactive
   with "(project)".
8. **Project Settings panel**: the page list; the **Timing** page (generic page of a simple section); the **Collision
   Layers** page (custom page of a complex section).
9. **Preferences dialog** (user-scope sections) for the contrast project vs user.
10. **Interpolation, on vs off**: not well served by stills. Propose a short capture or a plotted trace: `Samples/ThirdPerson`
    at a high frame rate with `Scene.Timing.Interpolation` on vs off (`project.setSettings {section: "Scene.Timing", value:
    {FixedRate: "Scene", Interpolation: false}}`), plotting the robot's drawn screen position per frame (the 29.4 px
    sawtooth vs ≤0.37 px quoted in RM wave 8). A motion-blurred still or a strip of consecutive frames could stand in.
11. **Scene file in a text editor/diff view**: one entity per line diff after moving one entity.
12. **Streaming panel / status** while a sub-scene or world cell loads (`scene.loadStatus` output) if the World chapter
    does not already show it.

---

## 5. Rules and pitfalls ("why" boxes)

1. **Signal every direct write to `TransformComponent`, `NameComponent`, `TagComponent` (and in other areas
   `MeshRendererComponent`, light fields).** Why: the scene caches world matrices, names and tags and only learns of
   changes through signals; an unsignalled write leaves a stale cache that the renderer and physics read. Debug builds
   recompute and assert, naming the entity (DG "Architecture rules"; `Scene.h` 97-104).
2. **Use `MarkTransformChanged` (not `patch`) when your own listeners must not hear the write.** Why: physics writing
   simulated poses back would otherwise treat its own output as user edits and teleport bodies (`Scene.h` 362-366).
3. **Values written right after `AddComponent` need no signal.** Why: entities created since the last update are read
   anyway (DG l.1065-1066). Prevents over-signalling cargo cult.
4. **Never edit `RelationshipComponent` or `HierarchyComponent`; go through `Scene` (`SetParent`, `PlaceEntities`,
   `DestroyEntities`).** Why: the two hierarchy forms must stay in step with depths, sibling indices, activity, sub-scene
   membership and the hierarchy version (AG "Architecture rules").
5. **Read sibling positions with `GetSiblingIndex`, never by searching the child list; destroy many entities in one
   `DestroyEntities`.** Why: linear vs quadratic (deleting 10,000 of 100,000 roots: 45 ms vs 54.6 s, RM wave 1).
6. **Destruction during an update is deferred.** Why: handles stay valid for the frame, scripts get `OnDestroy` with the
   entity complete; destroying in the middle of a system's iteration would invalidate storages.
7. **Do not hold `Entity` or `T&` across frames or across copies; hold UUIDs.** Why: handles are recycled; play mode runs
   on a `Scene::Copy`; EnTT storages move elements on add/remove.
8. **Never `GetComponent` a tag component.** Why: empty types have no storage; compile-time `static_assert`.
9. **A scene holds at most 1,048,575 entities.** Why: EnTT's 20-bit index; creation fails cleanly rather than corrupting.
10. **New components live in their module (`<Module>/<Module>Components.h`), not in `Scene/Components.h`.** Why: layering;
    Scene holds only its own and types sibling layers must read (DG Module registration).
11. **Register components only while the composition root runs (or via `ModuleRegistrationOptions::Extra`).** Why: the
    registry freezes so that worker threads read it without locks (AR "Component lifecycle").
12. **Never rename a registered component or property name.** Why: names are the file format and the automation API
    (SK §2).
13. **Choose ranges so invalid states are impossible.** Why: ranges are enforced on every path (files clamp, commands
    refuse), so one registration protects inspector, commands, scripts and loads (SK §2).
14. **Data that is not a property must describe its references (`ExtraReferences`).** Why: copies, prefab instances and
    asset scans find references only through reflection; otherwise duplicates point at the originals and exports drop
    assets (AR "Extra data and its references").
15. **A property another turns off gets an `InactiveReason`.** Why: people and agents otherwise edit values that do
    nothing (AG "Editor"; DG "Inspectors").
16. **Systems declare order; toward another module's system use soft constraints.** Why: builds without that module must
    still register and run; registration order alone is fragile (AR "Update order").
17. **Build descriptors with `MakeSceneSystemDescriptor<T>` and declare overrides public.** Why: `GetSystem<T>` finds it
    and idle frames call only overridden phases (nine calls for all built-ins).
18. **Modules meet through scene services, never `GetSystem` of a class from another module.** Why: the layer table
    forbids the include; services return null when a module is absent (AR "Scene services").
19. **Read the fixed step via `Scene::GetFixedTimestep`/`GetMaxFixedSteps`, never `GetSettings()`.** Why: the project's
    `Scene.Timing` rate overrides the scene's value (DG "Fixed rate").
20. **Tools count game time in fixed steps (`GetFixedStepCount`), never frames.** Why: frames depend on the machine;
    steps are deterministic (AG "Editor"; DG "Stepping a paused game").
21. **Renderers draw `FindDrawnTransform`/`GetDrawnTransform`; simulation never reads them; teleports call
    `BreakInterpolation`.** Why: drawn and simulated poses differ by up to a step; reading drawn poses in gameplay would
    feed latency back into the simulation; a teleport blended would streak (DG "Interpolation").
22. **Follow moving bodies in `OnLateUpdate` with drawn positions; move carriers in fixed steps.** Why: otherwise judder
    or riders lagging their platforms (DG "Interpolation", Rule for game code).
23. **Never build a DOM of a whole scene document; write with `SceneDocumentWriter`, read with `SceneDocumentReader`.**
    Why: a million entities as a DOM costs gigabytes; streaming holds one entity (AG "Asset pipeline").
24. **Loaders reject truncated or garbage bytes without crashing and honour cancellation; a cooked format change extends
    the corruption tests.** Why: files are untrusted input; cancelled loads must end within milliseconds (AG "Asset
    pipeline").
25. **Never block a frame on a scene load; scenes that will run load with `PrepareSystems`; loading work draws from the
    frame's `SceneWorkBudget`.** Why: frame pacing; the first frame of a scene must build nothing (AG "Worlds").
26. **Scenes load through `SceneLoader` (never `LoadAssetSync`) and are let go with `ReleaseInBackground`.** Why:
    destroying a million entities takes tens of ms (AG "Editor").
27. **Code that works for a scene reaches assets through `Scene::GetAssetManager()`.** Why: per-scene asset managers can
    replace the active one later without changing callers (DG "Architecture rules").
28. **Keep unknown data.** Why: a build without a module, or an older engine, must not destroy what it does not
    understand (unknown components, unclaimed settings sections, unknown project members are written back as read).
29. **Settings: read `IProjectSettings` on the main thread only and cache by `GetVersion`; validate only through
    `SettingsSection::Validate`; never assert on settings values.** Why: values come from files and agents; providers
    change when projects open and close (DG "Project settings").
30. **Prefab root transform and name are the instance's own.** Why: placing and naming instances must not count as
    modifications that block prefab propagation (MP; AR "Prefab instances").
31. **Code that writes a prefab or gives instances its values keeps the bookkeeping exact (`MarkSynced`,
    `PrefabSync::SetBaseline`, `UpdatePrefabOverrides`).** Why: otherwise changes are propagated twice or instances are
    wrongly marked outdated (AG "Editor").

---

## 6. Hands-on

### For engine developers

| Exercise | Difficulty | Proves |
| --- | --- | --- |
| Write a doctest that builds a 3-level tree, moves the root, and checks with `GetTransformUpdateCount` that only that subtree was recomputed; then a second update recomputes nothing | Easy | dirty propagation and the diagnostics |
| Reproduce the transform contract violation: write `Translation` without a signal, show `ValidateWorldTransforms` fails and names the entity; fix with `MarkModified` | Easy | the contract and the Debug check |
| Add a new component in a module (tutorial following SK): declare, register with ranges, tooltip, a `Section`, an inactive reason and a `Requires`; round-trip it through `SceneSerializer`; add it to the feature test scene | Medium | reflection end to end, feature test rule |
| Write a `SceneSystem` "Spinner" that rotates entities with a `SpinComponent` in `OnFixedUpdate`, registered with `AfterIfPresent = {"Scripting"}`, `BeforeIfPresent = {"Physics"}`; verify `GetAll()` order and that only `OnFixedUpdate` is called (`CallsUpdate == false`) | Medium | systems, ordering, override detection, signalling writes |
| Have Spinner's entities be drawn smoothly: run with `SetInterpolation(true)` and check `GetInterpolationStats` reports them as Blend; add a child light and see it as Compose | Medium | interpolation roles |
| Implement a scene service `IWindQuery` offered by a Wind system and consumed by Spinner, showing null when Wind is unregistered | Medium | services, decoupling |
| Measure: create 100,000 entities, time `UpdateWorldTransforms` after moving one root vs one leaf (cf. `Perf.Scene.MoveRoot100k`, `MoveLeaf100k`) | Medium | cost model, parallel walk |
| Extend `CompareHierarchyOrder` test coverage: random trees vs `GetEntitiesInHierarchyOrder` ranks (a mini sweep) | Medium | LCA algorithm, sweep testing |
| Write an `EntitySink` that counts entities per component type while streaming a scene document, without creating a scene | Medium-hard | streaming reader, sink pattern |
| Add a simple settings section `Game.Tuning` in a test-local `SettingsRegistry` with an Int field and a version-2 upgrade; validate stored values of version 1, 2 and 3 | Medium | sections, versioning, validation |
| Add a field to a section's `Read` upgrade path in a complex section and check `ProjectSettingsValues` keeps a refused value verbatim | Hard | keep-unknown principle |
| Explain (written exercise) why `ComputeUpdateOrder` builds from the back, using the Wind/CameraFollow example, then break it by building from the front and watch `SceneSystemTests` "A system moves ahead..." fail | Hard | topological sort trade-offs |
| Corrupt a cooked scene's bytes at random offsets and confirm `CookedSceneReader::Read` refuses them (cf. `CookedSceneTests.cpp`) | Hard | defensive binary formats |

### For game developers (editor and scripts)

| Exercise | Difficulty | Proves |
| --- | --- | --- |
| Build a solar system: Sun → Earth → Moon with the Hierarchy panel; rotate Sun and watch children follow; reparent the Moon with and without keeping world position | Easy | hierarchy and local vs world |
| Deactivate a parent and observe children stop rendering; reactivate | Easy | activity inheritance |
| Find entities by tag from a script (`FindEntitiesByTag("Enemy")`) and destroy them; observe deferred destruction | Easy | tags, lifetimes |
| Make a prefab from a group, place five instances, override one light intensity on one instance, change the prefab, observe propagation except the override; Revert; Unpack | Easy-Medium | prefab linking and overrides |
| Use `prefab.instantiate {instances: [...]}` through StrataCLI to scatter 200 crates in one undo step | Medium | automation, InstantiateMany |
| Set Project Settings > Timing to 30 and 120 with Interpolation on/off; play the Physics Playground and describe what changes (contact softness, smoothness, latency) | Medium | fixed step and interpolation trade-offs |
| Script a camera that follows a physics ball with `GetDrawnPosition` in `OnLateUpdate`, then with the world position in `OnUpdate`; compare judder | Medium | drawn vs simulated transforms |
| Name collision layers and make "Ghost" pass through "Player"; change it from a script during play and see it reset on the next scene | Medium | project settings vs scene working copy |
| Load a level section additively with the SDK's `SubScene` and show its progress on a UI bar; unload it | Medium | sub-scenes |
| Inspect a `.stscene` file in a text editor, move one entity in the editor, save, diff | Easy | the document format |

---

## 7. Glossary

- **Entity**: an identifier in a scene to which components are attached; in Strata an `entt::entity` handle wrapped by
  `Entity`, plus a persistent UUID.
- **Component**: a plain struct of data attached to an entity; one of each type at most.
- **Tag component**: an empty struct whose presence is the information (`InactiveComponent`).
- **ECS (entity-component-system)**: architecture separating identity (entities), data (components) and behaviour
  (systems).
- **Registry**: EnTT's container of entities and component storages (`entt::registry`).
- **Storage / sparse set**: EnTT's per-type container: sparse index + packed entity array + packed component array.
- **View**: an iterable over entities that have a given set of components.
- **Handle (EnTT)**: 32-bit value of index and version; recycled after destruction.
- **UUID**: 64-bit random identifier that persists across save/load and copies (`Core/UUID.h`).
- **Signal (on_construct / on_update / on_destroy)**: EnTT callbacks fired when a component is added, patched, removed.
- **patch / MarkModified**: emitting `on_update` after writing a component in place.
- **Scene**: Strata's world of entities: registry, hierarchy, caches, and while running its systems.
- **Root entity**: an entity without a parent.
- **Sibling index**: an entity's position among its parent's children.
- **Hierarchy version**: a counter that changes whenever hierarchy order may have changed; cache key.
- **Local transform / world transform**: TRS relative to the parent / composed up to the root.
- **TRS**: translation, rotation (quaternion), scale.
- **Decomposition**: recovering TRS from a matrix; fails for shear or zero scale.
- **Dirty flag**: a mark that a cached value is stale.
- **Frontier**: the dirty entities without a dirty ancestor, from which recomputation starts.
- **Transform contract**: Strata's rule that direct transform writes must be signalled.
- **Active in hierarchy**: active and every ancestor active.
- **Scene system**: an object that runs while a scene plays (physics, scripts, audio...).
- **Update phases**: `OnUpdate` (per frame), `OnFixedUpdate` (per fixed step), `OnLateUpdate` (after steps).
- **Fixed timestep**: the constant simulated duration of one physics/script step (1/60 s by default).
- **Accumulator**: leftover frame time not yet simulated in fixed steps.
- **Spiral of death**: frames getting longer because each must simulate more catch-up steps.
- **Time dilation**: Strata's option to run the simulation slower than real time instead of catching up.
- **Time scale / unscaled time**: multiplier on simulated time / time that ignores it (menus).
- **Stepping**: running exactly one fixed step per frame while paused.
- **Simulate mode**: editor mode running physics only.
- **Hard / soft constraint**: an order requirement that needs / does not need the named system to be registered.
- **Scene service**: an interface a running system offers to others through the scene.
- **Engine service**: a process-wide interface (`EngineServices`), e.g. `IProjectSettings`.
- **Composition root**: the one function that registers every module (`Engine::RegisterBuiltinModules`).
- **Layer (architecture)**: a library group with allowed include directions (`Layers.json`).
- **Reflection**: runtime description of types and their fields.
- **Property**: a reflected field of a component (type, range, flags, getter/setter).
- **Type erasure**: hiding a concrete type behind `void*` and function objects.
- **CRTP**: curiously recurring template pattern; base class templated on the derived class (fluent builders).
- **Component flags**: Hidden, NotRemovable, NoCopy, NoSerialize, EngineAdded.
- **Inactive reason**: text explaining why a property has no effect in the component's current state.
- **Requirement (`Requires`)**: a component that must be added before another.
- **Extra data**: component data serialized by the component itself (script fields).
- **Unknown component**: a component in a file whose name this build does not register; kept verbatim.
- **Canonical JSON**: the exact form values are written in (sorted keys, shortest floats).
- **DOM**: an in-memory tree of a whole parsed document.
- **Streaming parser / event parser**: reads a document as events without building the whole tree.
- **Entity sink**: the receiver of a streamed document's entities (`EntitySink`).
- **Snapshot**: `{"Entities": [...]}` of some entity hierarchies (clipboard, undo, prefabs).
- **Cooked scene**: the checksummed binary form exported games load ("STSC").
- **CRC-32C**: a checksum used to detect corruption.
- **MessagePack**: a compact binary encoding of JSON values.
- **Prefab**: an authored, reusable entity hierarchy asset (`.stprefab`).
- **Model**: an imported (glTF) entity hierarchy asset, read-only.
- **Prototype (`EntityPrototype`)**: a compiled, immutable hierarchy ready for fast copying.
- **Instance / instance root**: entities made from a prefab / the topmost linked entity of an instance.
- **Part (of a prefab)**: the sub-hierarchy below one template root.
- **Override**: a value an instance keeps differently from its prefab.
- **Apply / Revert / Unpack / Propagate**: write instance into prefab / take prefab's values / break the link / push a
  prefab change to instances.
- **Outdated instance**: modified since it last took its prefab's values while the prefab changed.
- **Prepared scene**: a scene a loader built on a worker, handed over once.
- **Sub-scene (additive load)**: a scene asset loaded into another scene next to its entities.
- **Slice / chunk**: a bounded portion of work done per frame / between clock checks.
- **Work budget (`SceneWorkBudget`)**: the frame's deadline and entity counts for loading work.
- **Interpolation (state interpolation)**: drawing between the last two simulated poses.
- **Step alpha**: the fraction between those poses drawn this frame.
- **Blend / Compose / Exact**: interpolation roles (own motion blended / parent's drawn × local / drawn as is).
- **Drawn transform**: where an entity is drawn this frame, possibly differing from its world transform.
- **Teleport / break**: a jump that must not be interpolated.
- **nlerp**: normalized linear interpolation of quaternions.
- **Project**: a game's folder with `.stproj`, assets, scripts and `.strata/` cache.
- **Intermediate directory**: `.strata/`, never committed.
- **Settings section**: a registered group of settings with an id `<Module>.<Name>`, scope and version.
- **Simple / complex section**: defined by fields / by schema, default and read function.
- **Project scope / user scope**: stored in the project (shipped) / in the user's preferences.
- **Hand-over**: applying project values to a scene on the main thread when it becomes live.
- **Collision layer / matrix**: one of 32 named groups / which pairs collide.
- **Game manifest**: `.stgame` file describing an exported game.
- **Game identity**: title, version, company, copyright, icon.

---

## 8. Proposed chapters (teaching order)

1. **What a game world is made of** — concept, both audiences, S. Purpose: explain scenes, entities, components and
   systems vs object hierarchies; Strata's choice. Prereqs: none. Screenshots: Hierarchy + Inspector (1).
2. **Entities and components in Strata (EnTT inside)** — internals, engine, M. Purpose: registry, sparse sets, handles vs
   UUIDs, `Entity` API, tag components, signals, `CreateEntity`, destruction rules, capacity. Prereqs: ch.1, C++
   templates intro. Screenshots: 0.
3. **The scene graph: hierarchy and transforms** — concept+internals, both, L. Purpose: local/world TRS, the dual
   hierarchy, reparenting, activity, ordering, the incremental world transform update and the transform contract, scene
   caches and lookups. Prereqs: ch.2, math chapter (vectors, matrices, quaternions). Screenshots: 1 (solar system tree).
4. **The game loop inside a scene: systems, phases and fixed steps** — internals, engine (game devs read the first
   half), L. Purpose: runtime lifecycle, Play/Simulate, the accumulator, pause/step/time scale/dilation, system
   descriptors and order, deferred destruction, scene services. Prereqs: ch.2, threading basics, application frame loop
   chapter. Screenshots: 0.
5. **Smooth motion: interpolating fixed steps** — concept+internals, both, M. Purpose: why judder happens, the
   interpolated set, roles, alpha, rules for renderers and game code, project switch. Prereqs: ch.3, ch.4.
   Screenshots/figure: 1 (trace or frame strip).
6. **Reflection: describing components once** — internals, engine, L. Purpose: why reflection, the builder DSL, type
   erasure, properties and validation, flags, sections, inactive reasons, requirements, extra data and references,
   JSON and binary value forms, `ComponentAccess`. Prereqs: ch.2, C++ lambdas/`std::function`/`std::variant`, CRTP
   (taught inline). Screenshots: 3 (camera inactive, sections, Add Component).
7. **Tutorial: adding a component and a system** — tutorial, engine, M. Purpose: follow SK end to end (WindZone or
   Spinner) including tests and feature test. Prereqs: ch.4, ch.6. Screenshots: 1 (new component in Inspector).
8. **Saving and loading scenes** — internals, engine, L. Purpose: document format, versioning and leniency, unknown
   components, streaming writer and reader, sinks, parallel read, cooked binary form, scene assets read once, async loads
   and the load state machine, `ReleaseInBackground`. Prereqs: ch.3, ch.6, asset pipeline basics (handles, loaders),
   job system. Screenshots: 1 (file diff).
9. **Prefabs** — concept+tutorial (game devs) and internals (engine), both, L. Purpose: prototypes and fast
   instantiation, instances, overrides, apply/revert/propagate, catch-up by version/hash, models. Prereqs: ch.6, ch.8.
   Screenshots: 2-3 (prefab bar, overrides, placement ghost).
10. **Streaming parts of a scene: sub-scenes and the frame budget** — internals, engine (short game-dev section), M.
    Purpose: additive loads, slices, membership, unloading, `SceneWorkBudget`. Prereqs: ch.8, ch.9. Screenshots: 0-1.
    (May merge into the World partition chapter of another area.)
11. **Projects and settings** — concept+internals, both, M. Purpose: project layout and file, game identity, manifest,
    settings sections (simple/complex, scopes, versions, validation, keeping unknown), `IProjectSettings`, hand-over to
    scenes (collision layers, timing), undoable project changes, export. Prereqs: ch.4 (fixed step), ch.6 (validation
    ideas). Screenshots: 3 (Project Settings Timing page, Collision Layers page, Preferences).
12. **Reference: scene, reflection and settings APIs** — reference, engine, M. Purpose: tables of Scene/Entity APIs,
    component flags, property types and flags, settings field types, file formats, limits and constants. Prereqs: the
    above. Screenshots: 0.

---

## 9. Not determined

- Exact release in which several features arrived (inactive reasons for the camera, `Requires`, `PrepareLoadedScene`,
  prepared states, `SceneWorkBudget`, `EntityPrototype`, time dilation, `ReleaseInBackground`): the documents describe
  the current state; RM gives waves for some only. I mapped what RN/RM state and marked the rest "release not stated".
- I did not read in full: `SceneDocumentReader.cpp` (969 lines; read its structure and AR's description), `CookedScene.cpp`
  (947; header and AR only), `PrefabOverrides.cpp` beyond `CompareComponents`/`ComputeOverrides` (`Propagate` 550-~860,
  `Revert`, `ApplyToPart` not read), `PrefabInstances.cpp` bodies, `SceneSubScenes.cpp` bodies, `SceneLoader.cpp`,
  `EntityPrototype::Compile`, `SceneSerializer.cpp` after line 520 (union-find tail, file I/O), `Property.cpp` after 280,
  `PropertyJson.cpp`, `PropertyBinary.cpp`, `Core/SettingsRegistry.cpp`, `Core/ProjectSettings.cpp`,
  `ProjectCollisionLayers.cpp`, `PhysicsLayerSettings.cpp`, `GameManifest.cpp`, `GameInfo.cpp`, `Project.cpp` outside
  `Load`, `SceneSystem.cpp` after line 140, `Scene.cpp`'s `PlaceEntities`, `ValidateHierarchy`, `DeactivateEntities`.
  The line ranges I give for unread function ends ("~") are approximate.
- Tests: read case lists of all suites and a few cases in full; did not read `SceneDocumentTests`, `SerializationTests`,
  `PrefabOverridesTests`, `SceneStreamingTests`, `RobustnessTests`, `SceneLoaderTests` bodies.
- The editor-side implementation of commands, Inspector, Hierarchy view, undo (`SceneEditTransaction`), `PrefabSync`,
  `ProjectMigration` and settings pages is outside this scope; I listed only their names. The script SDK's entity and
  component API (how scripts read components through reflection) belongs to the Scripting area and was not read.
- The feature test project's coverage of this area (`StrataTests/FeatureTest/`) was not inspected.
- Whether the samples have scenes that best demonstrate interpolation for a screenshot or trace (I propose ThirdPerson and
  PhysicsPlayground from DG/RM mentions; not verified by running anything, as required).
- Stale comment found: `S/Scene/SceneRegistration.h` 6-9 omits `Scene.Timing`, which `SceneRegistration.cpp` 22
  registers.
