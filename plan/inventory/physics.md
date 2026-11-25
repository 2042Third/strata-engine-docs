# Inventory: Physics (rigid bodies, colliders, characters, queries, the fixed step)

Surveyed at `main` 822a7a46 of `G:/GameEngineAI`. All paths are relative to that repository. Line numbers are those of
this commit. "DG" is `Docs/DeveloperGuide.md`, "AR" is `Docs/Architecture.md`.

The area in one paragraph: Strata simulates rigid bodies with **box3d** (Erin Catto's 3D engine, MIT, pinned at commit
`efca0c1`, `ThirdPartyNotices.md` line 15) behind its own ECS components. The `Physics` folder holds a scene system
(`PhysicsSystem`) that owns one `PhysicsWorld` per running scene; the world turns entities with `RigidBody` and collider
components into box3d bodies and shapes, steps box3d once per fixed step, writes the moved bodies' poses back to the
entities, and folds box3d's per-shape contact events into per-entity Begin/End events. Character controllers are Strata's
own, written on box3d's "mover" queries (they are not solver bodies). Other modules (scripts, animation, the world
streamer, the editor) reach physics only through scene services declared in `Scene/SceneServices.h`. The fixed timestep,
its accumulator and the interpolation of what fixed steps move live in the Scene module (`Scene.cpp`,
`SceneInterpolation.cpp`), because scripts and animation share the step. There are **no joints, no shape casts (sweeps)
in the public API, no ragdolls, no vehicles** at this commit (release notes list joints and ragdolls as future work).

---

## 1. Features

### 1.1 Components (authoring data)

All in `Strata/src/Strata/Physics/PhysicsComponents.h`, registered in `PhysicsComponents.cpp` `RegisterPhysicsComponents`
(lines 118-185), each with an inspector category "Physics" and a gizmo in `ComponentGizmoGroup::Collider`.

| Feature | What it is | Where | Docs | Release |
| --- | --- | --- | --- | --- |
| `RigidBodyComponent` ("RigidBody") | Body type (Static/Dynamic/Kinematic), mass, linear and angular damping, gravity scale, friction, restitution, `IsTrigger`, `ContinuousCollision`, per-world-axis rotation locks, collision `Layer` (0-31) | `PhysicsComponents.h` 20-42; registration `PhysicsComponents.cpp` 120-134 | AR 354-371 ("Physics") | 0.3.0 (Jolt), box3d since 0.5.0 |
| `BoxColliderComponent` | `HalfExtents`, `Offset` | `PhysicsComponents.h` 44-48 | AR 365-366 | 0.3.0 |
| `SphereColliderComponent` | `Radius`, `Offset` | 50-54 | AR 365 | 0.3.0 |
| `CapsuleColliderComponent` | Y-aligned capsule: `Radius`, `HalfHeight` (of the cylinder), `Offset` | 56-62 | AR 365 | 0.3.0 |
| `MeshColliderComponent` | `Mesh` asset (falls back to the MeshRenderer's mesh), `Convex` (hull) or triangle mesh (static bodies only) | 64-68 | AR 366-369 | 0.3.0; hull reduction 0.5.0 |
| `CharacterControllerComponent` | Upright capsule a script walks: `Height`, `Radius`, `StepHeight`, `MaxSlopeDegrees`, `Layer`, `GravityScale`, `PushStrength` (N), `Enabled` | 70-85; registration `PhysicsComponents.cpp` 167-184 | AR 458-485 ("Character controllers") | 0.3.0 (Jolt's), Strata's own on box3d mover 0.5.0 |
| Collider gizmos | Box, sphere, capsule, mesh and controller wire shapes in the editor, scaled like the bodies | `PhysicsComponents.cpp` 26-114; drawn by `Renderer/SceneGizmos.cpp` 165; viewport toggle `AllColliders` (`viewport.setSettings {allColliders}`, `StrataEditor/src/Editor/EditorViewportCommands.cpp` 124) | none specific | not stated |
| Body composition rule | An entity with a RigidBody is one body made of its own colliders and those of descendants without their own RigidBody; a collider entity with no RigidBody on itself or an ancestor is a static body of its own; events and queries report the owning entity | comment `PhysicsComponents.h` 15-18; `PhysicsWorld.h` 28-39; code `FindBodyOwner` `PhysicsWorld.cpp` 212-226, `CollectMergedEntities` 293-308 | AR 354 ff. | 0.3.0 |

### 1.2 Body types, shapes, materials, mass

| Feature | Where | Docs |
| --- | --- | --- |
| Static, dynamic, kinematic bodies mapped to box3d types | `ToBodyType` `PhysicsWorld.cpp` 178-187 | AR 354 |
| Kinematic bodies follow their entity with a velocity that reaches the target in one step (`b3Body_SetTargetTransform`), stopped at the target | `SyncBody` `PhysicsWorld.cpp` 3398-3410 and 3345-3354 | `PhysicsWorld.h` 52-58 |
| Dynamic bodies moved from outside are teleported, keeping velocity; static bodies moved wake what rests on them | `SyncBody` 3392-3418 | `PhysicsWorld.h` 52-58 |
| Shape building per collider: boxes are shared hulls per size+placement (`BoxHullKey`, `c_MaxSharedBoxHulls` 4096), spheres and capsules are values, convex meshes `b3CreateTransformedHullShape`, triangle meshes `b3CreateMeshShape`, offset triangle meshes become baked compounds | `AddColliderParts` 1857-1976, `CreatePartShape` 2047-2099, `BoxHullKey` 639-668 | AR 364-369 |
| World scale baked into shapes (boxes and meshes exactly incl. mirroring; sphere radius by largest axis; capsule radius by max(|X|,|Z|), half height by |Y|); shear approximated; min extent 1 mm | `PhysicsWorld.h` 35-38; `c_MinColliderExtent` `PhysicsWorld.cpp` 51; code 1860-1918 | AR 364 |
| Material: friction and restitution per body (clamped), one material for every shape of the body | `MakeBodySetup` 1993-2045 | DG "Physics" n/a; Release 0.5.0 lines 75-97 |
| Mass: shapes at density 1 give the distribution, then scaled to the component's mass (`ApplyMass`) | `ApplyMass` 2102-2114; `MakeBodySetup` 2010-2011, 2038 | none |
| Rotation locks on world axes (`motionLocks`) | `MakeBodySetup` 2039-2043 | `PhysicsWorld.h` 39 |
| Continuous collision: every dynamic body swept against static ones (box3d); `ContinuousCollision` makes it a bullet (also against moving bodies) | `MakeBodySetup` 2036-2037; world def `enableContinuous` `PhysicsWorld.cpp` 4695 | Release 0.5.0 "Fast bodies" |
| Triggers: shapes are box3d sensors; sensors see convex shapes and characters only, never triangle meshes; static-static sensor pairs dropped | `MakeBodySetup` 2027-2030; `ProcessStepEvents` 3700-3711 | AR 369-370; Release 0.5.0 line 86 |
| Coordinate limit 1e5 m (box3d single precision, `B3_HUGE`): bodies beyond wait like degenerate transforms | `c_MaxBodyCoordinate` 73, `IsWithinCoordinateRange` 173-176 | AR 431-432 |
| Degenerate transforms, zero-scaled parents: bodies leave the simulation (Suspended) until valid | `SyncBody` 3366-3388; `SuspendUnwritableBody` 4107-4122 | `PhysicsWorld.h` 41-47 |
| Pending bodies: records that cannot build yet keep a `BuildFailure` (NoCollider, InvalidColliders, DegenerateTransform, MissingMesh, WaitingForSlot) and retry when it can succeed | `BuildFailure` 123-132; `SetFailure` 1225 | `PhysicsWorld.h` 41-45 |
| Warnings once per entity and kind (`PhysicsWarning`) | 81-99, `ShouldWarn` 972 | none |

### 1.3 Mesh colliders and cooking

| Feature | Where | Docs |
| --- | --- | --- |
| `PhysicsMeshProvider` interface (non-blocking mesh data source, version, changed meshes) | `PhysicsTypes.h` 268-293 | AR 361-363 |
| `AssetMeshProvider`: default provider from the active asset manager via `MeshGeometryRegistry` (physics never depends on the renderer) | `AssetMeshProvider.h` 17-59, `.cpp` | AR 361-363 |
| `PhysicsMeshShapes`: cooks hulls (64 vertices, fallback 44 because box3d hulls hold at most 128 faces/edges) and BVH meshes on the JobSystem, process-wide cache per data object | `PhysicsMeshShapes.h` 40-83; `.cpp` 73-140 | AR 359-360, 366-367 |
| Mesh wait at start: steps held (nothing moves) until mesh floors exist, at most `MeshWaitTimeout` (10 s) | `HoldForMeshes` `PhysicsWorld.cpp` 3200-3243; `PhysicsTypes.h` 49-51 | `PhysicsWorld.h` 73-78 |
| Mesh hot reload: bodies rebuilt when the provider reports new data | `RefreshMeshBodies` 3115 | `PhysicsWorld.h` 129-133 |

### 1.4 The world and its lifecycle

| Feature | Where | Docs | Release |
| --- | --- | --- | --- |
| `PhysicsSystem` "Physics" scene system (Play and Simulate), soft order after Scripting, profile stage `Scene.Physics` | `PhysicsRegistration.cpp` 12-27; `PhysicsSystem.h` 34-53 | AR 959-976 (system table) | 0.3.0 |
| Lazy world: created at start only if the scene has physics components, else on the first one added | `PhysicsSystem.cpp` 92-124, 568-588 | `PhysicsSystem.h` 36-38 | 0.4.0 |
| 128-world limit of box3d; a scene with no free world plays without physics, one error | `HasFreeWorld` `PhysicsWorld.cpp` 4738; `CreateWorld` `PhysicsSystem.cpp` 574-588 | AR 389-391; Release 0.5.0 358 | 0.5.0 |
| `PhysicsRuntime`: process-wide reference count, box3d assert and log hooks (asserts through Strata's, logs as warnings "box3d: ") | `PhysicsRuntime.h` 8-48, `.cpp` 45-60 | AR 355-357 | 0.5.0 |
| `PhysicsTaskSystem`: box3d's step tasks on Strata's JobSystem; the waiting thread runs an unstarted task itself | `PhysicsTaskSystem.h` 23-69, `.cpp` 14-48 | AR 357-358; DG "Settling and the sweep" (workers) | 0.5.0 |
| Change tracking through EnTT signals (components, reparenting, activity, destruction) into `ChangeList`s, applied in rounds before steps and queries | `ChangeList` 671-713; `ConnectSignals` 3083; `ApplyChanges` 2990; `c_MaxChangeRounds` 69 | `PhysicsWorld.h` 49-51 | 0.3.0 |
| Leaving the simulation: inactive or pending-destroy entities; disable in box3d; static bodies without contacts are **parked** (empty filter mask), disabled 60 steps later, 1,024 a step | `ParkStaticBody` 1530-1542, `DisableParkedBodies` 1560-1584, `RemoveFromSimulation` 1586-1600; `MakeParkedShapeFilter` `PhysicsFilters.h` 33-40 | DG "Leaving the simulation" 2450-2466 | 0.7.0 |
| Capacities and growth: automatic room (next pow2 of 2x bodies, at least 1,024; 2 contacts a body, at least 2,048), creation reserve capped at 2^17 bodies / 2^18 contacts, growth doubles the room, growth limit (default 2^21), FIFO of waiters at the limit, demand remembered per scene lineage | `ResolveCapacities` 4775-4787; `GrowRoom` 2300-2318; constructor 4672-4736; `PhysicsSystem::OnRuntimeStop` 138-156 | AR 391-410; DG "World partition" ("Physics never drops collision", around 2598) | 0.4.0 (growth), 0.5.0 (box3d in-place growth) |
| `EstimateReservedBytes`: memory fitted to box3d's own count (2,120 B a body, 250 a contact, 32 KiB base) | 4789-4793; constants 103-105 | AR 410-411 | not stated |
| `IPhysicsCapacity` service and `Reserve` (the world streamer reserves for cells about to load) | `SceneServices.h` 384-412; `PhysicsWorld::Reserve` 4936; `World/WorldStreamer.cpp` | AR 2778ff (World partition "Reserving physics room") | 0.4.0 |
| Parallel body creation for rounds of >= 256 bodies, deterministic IDs (main thread starts and installs in record order, jobs build parts in chunks of 512) | `RefreshOwnersInParallel` 2611-2697 | AR 411-418 | 0.6.0/0.7.0 (not stated precisely) |
| Static shapes made before the first step skip pair search (`invokeContactCreation`) | `InstallBody` around 2363 | AR 418-420 | not stated |
| Sliced building for loaded scenes (`PhysicsBuildMode::Sliced`, `BuildSlice`, `PrepareLoadedScene`, 8,192 owners a slice, adopted at start) | `PhysicsWorld.h` 22-26, 149-153; `PhysicsWorld.cpp` 4743-4768; `PhysicsSystem.cpp` 544-566 | DG "World partition" (Preparing, ~2594) | 0.6.0 (not stated precisely) |
| Process-default settings for tests and tools | `PhysicsSystem::SetDefaultSettings` | `PhysicsSystem.h` 64-67 | |

### 1.5 The step

| Feature | Where | Docs |
| --- | --- | --- |
| `PhysicsSystem::OnFixedUpdate`: apply changes, sync gravity, layers and Physics.Simulation, `Simulate`, dispatch events | `PhysicsSystem.cpp` 164-177 | AR 429-431 |
| `PhysicsWorld::Simulate`: changes, reserved growth, parked disables, mesh hold, sync entities to bodies, step characters, `CollisionSteps` box3d steps of 4 sub-steps each with forces reapplied, events per box3d step, write-back, pair upkeep, instruments | `PhysicsWorld.cpp` 4973-5078; `c_SolverSubSteps` 77 | AR 421-424 |
| Synchronization before the step: only awake bodies, polled records and descendants of bodies moved without a signal; parallel chunks skip unmoved ones | `SyncEntitiesToBodies` 3430-3527; `SyncBody` 3300-3421 | DG "Physics instruments" (write-back paragraph); AR 437-441 |
| Write-back after the step: bitmap of moved bodies in body order, parallel chunks, parents before children, only translation and rotation written, scale kept, `Scene::MarkTransformsChanged` (no `on_update`) | `MarkMoved` 3628-3640; `WritePose` 4144-4182; `WriteBackDynamicBodies` 4198-4435 | AR 441-454; DG 2399-2408 |
| Forces act during the next fixed step only (queued, re-applied before each box3d step); impulses immediate | `AddPendingForce` 5157; `ApplyPendingForces` 4009; `PhysicsWorld.h` 224-231 | `SceneServices.h` 135-157 |
| Teleport: body and entity at once, wakes neighbours, breaks interpolation | `PhysicsWorld::Teleport` 5302-5355 | DG "Interpolation" (Breaks) |
| Gravity from `SceneSettings::Gravity` (-9.81 Y), changing it wakes every body | `SetGravity` 5092-5100; `Scene/Scene.h` 63 | AR 1060ff |

### 1.6 Contacts and events

| Feature | Where | Docs |
| --- | --- | --- |
| `CollisionEvent` (Begin/End, IsTrigger, A/B entity and UUID, point, normal A->B); every Begin has exactly one End except at stop | `Scene/SceneServices.h` 41-71 | AR 455-470 |
| `ICollisionEventSource`: listeners (AllEntities or WatchedEntities scope), watches counted per entity | `SceneServices.h` 73-105; `PhysicsSystem.cpp` 203-260 | AR 456-462 |
| Pair folding: box3d's per-shape contacts and sensor visits counted into per-entity `TouchingPair`s (begin with first, end with last); rebuilt bodies mark pairs Unconfirmed instead of End+Begin | `TouchingPair` `PhysicsWorld.cpp` 422-443; `CountBegin`/`CountEnd` 3598-3625; `ProcessStepEvents` 3643-3712; `MarkPairsUnconfirmed` 1714 | AR 455-470 |
| Contact interest: only wanted pairs tracked; nobody listening costs nothing; pair seeded from box3d contacts when it becomes wanted | `IsWanted` 3529; `SeedWantedPairs` 3949; `SetTrackAllContacts` 4864 | DG "Physics instruments" ("Contacts nobody tracks cost nothing") |
| Contact point = midway between surfaces over the first manifold; trigger point = centre of AABB intersection | `ReadContactPoint` 3536-3556; `ComputeTriggerPoint` 3558-3569 | AR 466-468 |
| Dispatch on the main thread after the step, snapshot of listeners, listeners may destroy entities | `DispatchCollisionEvents` `PhysicsSystem.cpp` 636-660 | `PhysicsSystem.h` 48-53 |
| Scripts' `OnCollisionEnter/Exit`, `OnTriggerEnter/Exit` via a WatchedEntities listener of `ScriptSystem` | `Scripting/ScriptSystem.cpp` 39-40, 99, 317-335; `StrataScriptCore/Include/StrataScript/Script.h` 89-92 | DG "Gameplay API" (Scripting) |
| O(1) pair add/remove (`IndexInA/B`, `EntityPairs`), `BodyRecord::PairCount` | 1344-1404 | AR 466-470 |

### 1.7 Queries

| Feature | Where | Docs |
| --- | --- | --- |
| `Raycast` (closest), `RaycastAll` (closest per entity, sorted), `OverlapSphere`, `OverlapBox` (deterministic body order); layer mask, ignore entity, includeTriggers; rays starting inside convex colliders do not hit; max distance clamped 1e5 | `PhysicsWorld.h` 254-265; `.cpp` 4436-4580, 5399-5488 | `SceneServices.h` 160-191 |
| Query sees bodies as of the last step or change; changes applied before queries | `PhysicsSystem.h` 41-46; `PhysicsSystem.cpp` 448-478 | `PhysicsSystem.h` 34-53 |
| No shape casts / sweeps in the public API (box3d's `b3World_CastMover` is used only by characters) | grep result: `CharacterControllers.cpp` 373 | none (gap) |

### 1.8 Collision layers

| Feature | Where | Docs | Release |
| --- | --- | --- | --- |
| 32 layers, symmetric matrix, names (`PhysicsLayerSettings`), "both masks must allow" rule | `Scene/PhysicsLayerSettings.h` 15-112 | DG "Collision layers" 1292-1340 | named layers 0.5.0; project-wide 0.6.0 |
| Project section `Scene.CollisionLayers` (`ProjectCollisionLayers`), working copy per scene (`Scene::GetPhysicsLayers`), hand-over `ApplyProjectLayers` | `Scene/ProjectCollisionLayers.h/.cpp`; `Scene.h` 649-665 | DG 1292-1340; AR 371-380 | 0.6.0 |
| box3d filter mapping: category bit = layer, mask = row | query category bit 63 | `PhysicsFilters.h` 1-60 | AR 386-388 |
| Runtime changes (`SetLayerCollisionMasks`, scripts' `Physics::SetLayersCollide`) refilter shapes, wake bodies | `PhysicsWorld.cpp` 5112-5140; `PhysicsSystem.cpp` 279-308 | AR 380-386 |
| Editor: Collision Layers page, `project.setCollisionLayers`, migration from 0.5.0 scenes | `StrataEditor/src/UI/CollisionLayersPage.cpp`; `Editor/EditorProjectSettingsCommands.cpp` 323 | DG 1316-1340 | 0.6.0 |

### 1.9 Character controllers

| Feature | Where | Docs |
| --- | --- | --- |
| `CharacterControllerSet`: capsule moved by box3d mover queries (`b3World_CollideMover`, `b3SolvePlanes`, `b3World_CastMover`) | `CharacterControllers.h` 57-127; `.cpp` 340-374 | AR 458-485 |
| Two-pass move (across, then vertical), step-up, ground snapping, slope limit, ground state | `MoveController` `CharacterControllers.cpp` 557-664; `SlideMove` 406-422; `ShapePlanes` 384-402; `FindGround` 475-519 | AR 465-473 |
| Moving platforms (carried velocity) and leaving them with their motion | `MoveController` 568-575, 650 | AR 466-467 |
| Presence body: kinematic capsule at 90% radius so bodies land on, triggers see and rays hit the character; never recycles | `CreatePresenceBody` 290-309; `MovePresenceBody` 311-320 | AR 461-463; DG "Physics simulation" |
| Pushing: inelastic impulse with effective mass at contact, capped by `PushStrength * dt`, never downward; 70 kg weight on dynamic ground | `PushBodies` 680-736; `c_CharacterMass` 30 | AR 475-479 |
| Parallel deterministic moves, serial writes in controller order | `CharacterControllerSet::Step` 928-999 | `CharacterControllers.h` 70-76 |
| `ICharacterControl` service (Move, Jump, Teleport, AddCharacterMotion for root motion, GetCharacterState) | `SceneServices.h` 193-235; animation's `AnimationSystem::ApplyRootMotion` `Animation/AnimationSystem.cpp` 788-804 | AR 463-466 |
| Character contacts join entity pairs; triggers reach the presence body | `StepCharacters` `PhysicsWorld.cpp` 4065-4105 | AR 481-485 |

### 1.10 Settings, tuning, determinism

| Feature | Where | Docs | Release |
| --- | --- | --- | --- |
| `PhysicsSettings` (capacities, `CollisionSteps`, `MeshWaitTimeout`, `GrowthLimit`, tuning, layer masks) | `PhysicsTypes.h` 39-99 | `PhysicsTypes.h` comments | |
| `Physics.Simulation` project section: `ContactRecycleDistance` (0.05 m), `SleepThreshold` (0.08 m/s), `ContactHertz` (30), `ContactDampingRatio` (10), `ContactPushSpeed` (3 m/s); clamped; applied at the next fixed step | `PhysicsSimulationSettings.h/.cpp`; `PhysicsWorld::SetSimulationTuning` 5620-5651; `PhysicsSystem::SyncSimulationSettings` 310-317 | DG "Physics simulation" 1342-1382 | 0.7.0 |
| Contact recycling (box3d), off for kinematic and presence bodies | `MakeBodySetup` 2025-2034; `CreatePresenceBody` 300 | DG "Contact recycling" 2235-2317 | 0.7.0 |
| Effective contact stiffness ceiling (1/8 of substep rate: 30 Hz at 60 steps/s) | `GetEffectiveContactHertz` 5658-5666 | DG 1361-1365 | 0.7.0 |
| Determinism: same results with any number of threads (ordered records, fixed chunking, integer settling sums, box3d golden hash) | tests `PhysicsSimulationTests.cpp` 821-853, `PhysicsBox3DTests.cpp` 105-121, `PhysicsCharacterTests.cpp` 573; `SettlingSums` `PhysicsWorld.cpp` 591-637 | AR 411-418, 447-454 | 0.5.0 onwards |
| Settle scenes, `physics-settle` helper, `Tools/PhysicsSweep.py` (distances, knobs, workers, pits, playground, report) | `StrataTests/src/Physics/PhysicsScenes.h/.cpp`; `Tools/PhysicsSweep.py` 1-44 | DG "Settling and the sweep" 2409-2448 | 0.7.0 |

### 1.11 The fixed step and interpolation (Scene module, shared with scripts and animation)

| Feature | Where | Docs | Release |
| --- | --- | --- | --- |
| Accumulator loop with `GetMaxFixedSteps`, backlog drop, time dilation (drop steps when steps cost more than they simulate) | `Scene/Scene.cpp` 2239-2329 | AR 1013-1023, 1043-1053 (Time dilation) | time dilation 0.6.0 (`Releases/0.6.0.md` 227) |
| `SceneSettings`: `Gravity`, `FixedTimestep` 1/60, `MaxFixedStepsPerFrame` 8, `PhysicsCapacity` | `Scene/Scene.h` 55-65 | AR 1060-1075 | |
| Project `Scene.Timing`: `FixedRate` (Scene/30/60/120/240), max steps `ceil(rate*2/15)`; `Interpolation` switch | `Scene/ProjectSceneTiming.h/.cpp` 118-123 | DG "Fixed rate" 1384-1440 | wave 8 (0.8.0, unreleased) |
| Interpolation of drawn transforms (Blend/Compose/Exact roles, step alpha, breaks) | `Scene/TransformInterpolation.h` 1-49; `Scene/SceneInterpolation.cpp` 107-116 (`BlendPose`); `Scene.cpp` 2312-2322 (alpha) | DG "Interpolation" 2468-2565 | wave 8 (0.8.0, unreleased) |
| Readers: `Scene::GetFixedTimestep`, `GetMaxFixedSteps`, `GetFixedStepCount`, `GetStepAlpha`, `GetDrawnTransform`, `FindDrawnTransform`, `BreakInterpolation`, `c_MaxInterpolatedSpeed` (400 m/s) | `Scene/Scene.h` 438-528 | DG 1414-1418, 2541-2549 | |
| Script SDK: `OnFixedUpdate`, `Time::GetFixedDeltaTime`, `GetDrawnPosition/Rotation`, `ResetInterpolation`, `Time::GetStepAlpha` | `StrataScript/Script.h` 34-38, 85; `Entity.h` 205-210 | `Docs/Manual/Scripting.md` 157-175 ("Following moving things") | wave 8 |

### 1.12 Diagnostics

| Feature | Where | Docs |
| --- | --- | --- |
| `PhysicsStats` (walked counts plus instruments kept as it steps) | `PhysicsTypes.h` 150-259; `GetStats` `PhysicsWorld.cpp` 5490 | DG "Physics instruments" 2319-2407 |
| `PhysicsLibraryProfile` (box3d stages), `PhysicsLibraryCounters` (islands, contacts, recycled), detailed stats switch | `PhysicsTypes.h` 116-148; `ReadLibraryStep` 4622; `SetDetailedStats` 5680 | DG 2330-2349 |
| `IPhysicsDiagnostics` / `PhysicsStepInfo` (constant time) | `SceneServices.h` 414-458 | DG 2321-2324 |
| Settling instruments (max speed, settling count, resting jitter) | `SettlingSums` 591-637; `WritePose` 4155, 4180 | DG 2361-2366 |
| Contact storage growth counting | `CountContactGrowth` 4658-4667 | DG 2350-2360 |
| Editor: `physics.stats`, `physics.setDetailedStats`, Streaming panel Physics row, `editor.status` `play.running.physics`; runtime perf-log columns | `StrataEditor/src/Editor/EditorWorldCommands.cpp` 1036-1098; `Panels/StreamingPanel.cpp` 516 | DG 2367-2373 |
| Perf tests `Perf.Physics.*` (Boxes10k/30kTracked/70k, Characters1000Step, Create10kBodies, Create100kStaticBodies, Grow65k, Sleeping70k, BallPit2k...) | `StrataTests/src/Perf/PhysicsPerfTests.cpp`; budgets `StrataTests/Perf/Budgets.json` | DG "Physics instruments" table 2386-2396; `Docs/Roadmap.md` 713-760 |

### 1.13 Script API (game developers' surface)

Host functions in `StrataScriptCore/Include/StrataScript/ScriptABI.h`: bodies 400-419 (`GetLinearVelocity` ...
`Teleport`), queries 421-438, characters 546-549 (`CharacterMove/Jump/Teleport/GetState`), layers 599-610
(`PhysicsSetLayersCollide`, `PhysicsGetLayersCollide`, `PhysicsGetLayerIndex`), interpolation 752-753
(`GetDrawnTransform`, `ResetInterpolation`). SDK wrappers: `StrataScript/Physics.h` (`RigidBody` 44-165, `Physics` 168-300,
`RaycastHit` 20-26, `Collision` 29-36) and `StrataScript/CharacterController.h` (`GroundState` 15, `CharacterController`
31-120). Agent-facing guide: `.claude/skills/strata-scripting/SKILL.md` 167-260 ("Physics", "Character controllers",
"Contacts"). Implemented in `Strata/src/Strata/Scripting/ScriptHostAPI.cpp` (13 uses of the physics services).

### 1.14 The Physics Playground sample

`Samples/PhysicsPlayground/`: about 600 bodies in six stations (crate tower and pyramid, 64 dominoes on a serpentine, a pit
of 500 balls of four materials, a goal basket trigger, ghost boxes on a Ghost layer that sinks through balls, a ramp and
ten pins). Scripts: `Playground.cpp` (raycast shooting 237, grab with `SetLinearVelocity` 225-255, `InstantiateMany` pour
258-275, domino impulse 277-286, ghost teleport 300-310, slow motion `Time::SetTimeScale` 325, 358), `GoalBasket.cpp`
(trigger counting, 1-26), `LaunchPad.cpp` (trigger sets velocity, 1-22), `Impact.cpp` (impact sounds from contact normal
and velocities, 40-87), `FlyCamera.cpp`. README lists what each part shows. Regression:
`StrataTests/Editor/PhysicsPlaygroundCommands.json.in` (CTest `StrataEditor.PhysicsPlayground`). Release 0.5.0.

### How completeness was checked

- Every header of `Strata/src/Strata/Physics/` (11 headers, 22 files) read and accounted for above: `AssetMeshProvider`,
  `CharacterControllers`, `PhysicsComponents`, `PhysicsFilters`, `PhysicsMeshShapes`, `PhysicsRegistration`,
  `PhysicsRuntime`, `PhysicsSimulationSettings`, `PhysicsSystem`, `PhysicsTaskSystem`, `PhysicsTypes`, `PhysicsWorld`.
- Every registered component (6, `PhysicsComponents.cpp` 118-185), the one scene system and the one settings section
  (`PhysicsRegistration.cpp`) are listed; the Scene-module sections physics depends on (`Scene.CollisionLayers`,
  `Scene.Timing`) are listed.
- Every scene service physics offers (7: `ICollisionEventSource`, `IBodyMotionQuery`, `IBodyControl`, `IPhysicsQueries`,
  `ICharacterControl`, `IPhysicsCapacity`, `IPhysicsDiagnostics`) is listed, with their consumers (Scripting, Animation,
  World streamer, Runtime, editor).
- Every physics-related host function of `StrataScriptHostAPI` found by grep (bodies, queries, characters, layers,
  interpolation) is listed. Editor commands found by grepping `"physics.` (2) plus `project.setCollisionLayers`.
- Every test suite (`Physics.*`, 17 suites, 22 files, about 250 cases) was listed by name and mapped to features.
- No shaders: physics has none. One tool: `Tools/PhysicsSweep.py`.
- Not checked line by line: the middle of `PhysicsWorld.cpp` (about 2,000 of its 5,695 lines skimmed by function
  name only: rebuild/merge bookkeeping 2120-2290, change rounds 2770-3040, pair seeding 3714-3960).

---

## 2. Concepts to teach (dependency order)

1. **What a physics engine is for in a game.** The problem: objects that fall, collide, stack and are pushed, plus
   questions about space ("what is under the cursor", "is the player on the ground"). Approaches: hand-written gameplay
   collision, third-party engines (PhysX, Havok, Jolt, Bullet, Box2D/box3d), own engine. Strata: a third-party solver
   (box3d) wrapped behind components and services, its own character controller. Newcomers expect physics to "just
   be the transform"; it is a separate simulation that must be kept in sync.
2. **Units, coordinates and float precision.** Meters, kilograms, seconds; gravity -9.81. Single precision degrades far
   from the origin; box3d refuses beyond 1e5 m, Strata's worlds stay within 20 km (DG "World partition" Precision).
   Mistake: building a game in centimeters or at huge coordinates.
3. **Rigid body state and integration.** Position, rotation (quaternion), linear and angular velocity, mass and inertia
   tensor; semi-implicit Euler; forces vs impulses vs setting velocity. Strata: forces act during the next fixed step
   only (`PhysicsWorld.h` 224-225), impulses at once; mass from the component, distribution from the shapes
   (`ApplyMass`). Mistake: calling `AddForce` once from `OnUpdate` and expecting continuous push.
4. **Body types.** Static (infinite mass, never moves by itself), dynamic (simulated), kinematic (moved by game code,
   infinite mass, pushes dynamics). Strata: kinematic bodies follow their transform by target velocity
   (`b3Body_SetTargetTransform`), so riders are carried. Mistake: moving a static body every frame (costly, wakes things),
   or animating a dynamic body's transform (teleports, loses contacts).
5. **Colliders and shapes.** Primitive shapes (sphere, capsule, box), convex hulls, triangle meshes, compounds; why
   triangle meshes are static only (no volume, no mass); hull vertex limits. Strata: box hulls shared, hulls reduced to
   64/44 vertices, mesh colliders cooked on jobs and cached. Mistake: a triangle mesh on a dynamic body; a round mesh as
   convex expecting exact shape.
6. **Composing bodies from an entity hierarchy.** Engines differ (Unity: Rigidbody plus child colliders form a compound;
   Unreal: per-component bodies). Strata takes the Unity-like rule (`PhysicsComponents.h` 15-18). Scale is baked into
   shapes; shear cannot be represented. Mistake: putting a RigidBody on every child; non-uniform scale under a rotated
   parent.
7. **The simulation loop: fixed timestep.** Why a fixed step (stability, determinism, repeatability) vs variable step; the
   accumulator; max steps per frame and the spiral of death; dropping backlog; time dilation. Strata: 1/60 by default,
   project `FixedRate`, `GetMaxFixedSteps` = steps of 2/15 s, time dilation in wall-clock programs. Mistake: multiplying by
   frame delta in `OnFixedUpdate`, counting frames instead of steps.
8. **Collision detection: broad phase and narrow phase.** AABB trees (box3d's dynamic trees), pair finding, contact
   manifolds; why a step costs what is awake. Strata: static shapes before the first step skip pair search; parked
   bodies keep their proxies but collide with nothing.
9. **Constraint solving: contacts as constraints.** Penetration, soft contacts (stiffness in hertz, damping ratio),
   push-out speed, sub-stepping (box3d's 4 substeps of "soft step"), friction and restitution (box3d bounces only above
   1 m/s). Strata exposes hertz, damping and push speed and explains the stiffness ceiling (1/8 of substep rate). Mistake:
   spawning overlapping bodies (pushed apart at 3 m/s); raising `ContactHertz` above 30 and seeing no change.
10. **Continuous collision (tunnelling).** Discrete steps miss thin walls; swept tests (time of impact). box3d sweeps every
    dynamic body against statics; bullets also against moving ones. More collision steps per fixed step as an alternative
    (`CollisionSteps`).
11. **Sleeping and islands.** Islands of touching bodies, sleep threshold and time (0.5 s), waking. Strata's 0.08 m/s
    threshold chosen by a sweep. Mistake: writing transforms of sleeping bodies without a signal (they never notice).
12. **Contact recycling / warm starting / caching.** Reusing last step's contact data; trade-off with stale geometry
    (ghost bumps, ledges). Strata keeps box3d's 5 cm, turns it off for kinematic and character presence bodies.
13. **Collision filtering.** Layers and masks (category/mask bits), groups; queries filtering. Strata: 32 named project
    layers, symmetric matrix, "both must agree" rule, a reserved query category bit so queries see every layer.
14. **Triggers (sensors).** Overlap without response; events only; what sensors can see. Strata: box3d sensors skip
    triangle meshes; static-static pairs dropped.
15. **Contact events.** Begin/End per pair; why per-shape events are folded per entity; why events are delivered after
    the step on the main thread (never from inside the solver); balanced Begin/End; cost of tracking (interest).
16. **Spatial queries.** Raycasts (closest/all), overlaps, shape casts (absent in Strata's API); masks, ignoring self,
    triggers, starting inside a shape. Queries see the last step's state.
17. **Synchronizing physics and the scene graph.** Two copies of the truth; who writes when (before the step: entity to
    body; after: body to entity); dirty signals; hierarchy write-back parents first; only awake bodies cost. Strata's
    transform contract (`MarkModified`, `MarkTransformChanged`). Mistake: writing `TransformComponent` fields directly
    without signalling.
18. **Character controllers.** Why not a dynamic capsule (tips over, bounces, slides on slopes); kinematic "collide and
    slide" with plane solving; steps, slopes, ground snapping, moving platforms, pushing, being landed on. Strata: own
    controller on box3d's mover, two passes, presence body. Mistake: rotating the controller entity expecting a tilted
    capsule; expecting vertical walk velocity with gravity on.
19. **Interpolation of rendering.** Drawing fixed-step poses at a higher frame rate judders; interpolation vs
    extrapolation; the half step of latency; teleports must break it. Strata: state interpolation with Blend/Compose/Exact
    roles; the simulation never reads drawn transforms. Mistake: camera following `GetWorldPosition` instead of the drawn
    position.
20. **Determinism.** Same input same output; floating point order; multithreading without changing results (fixed chunk
    order, integer sums, serial creation). Strata tests it with box3d's golden hash and twin runs with and without
    workers. Mistake: thinking "deterministic" means cross-platform bit-identical gameplay (box3d claims cross-platform
    determinism for its scenario; Strata checks a golden hash).
21. **Scale and memory: capacities and growth.** Preallocated pools vs growth; reserving ahead of streaming; growth
    limits as memory caps. Strata: automatic room, growth doubling, demand remembered per scene.
22. **Bodies in a streaming world.** Building bodies in slices while a scene loads, parallel creation, parking static
    bodies to spread removal cost. Prerequisite: the World partition area.
23. **Tuning by measurement.** Why physics defaults are chosen by sweeps over representative scenes; chaotic systems
    need many layouts (medians). Strata's `PhysicsSweep.py` and the settle scenes. A good "engineering method" chapter.

---

## 3. Code worth showing

| # | File and lines | What it teaches | Reader must know first |
| --- | --- | --- | --- |
| 1 | `Strata/src/Strata/Physics/PhysicsComponents.h` 20-42 | A rigid body as plain data: what fields a game designer sets | ECS components |
| 2 | `PhysicsComponents.h` 70-85 | The character controller's knobs and their units | concept 18 |
| 3 | `Strata/src/Strata/Physics/PhysicsWorld.cpp` 212-226 (`FindBodyOwner`) | The hierarchy rule for which entity owns a body | entity hierarchy |
| 4 | `Strata/src/Strata/Scene/Scene.cpp` 2239-2329 | The fixed-step accumulator, max steps, backlog drop, time dilation, step alpha | game loop basics |
| 5 | `PhysicsSystem.cpp` 158-177 | What one frame and one fixed step of the physics system do | scene systems |
| 6 | `PhysicsWorld.cpp` 4973-5078 (`Simulate`) | The anatomy of a physics step in an engine (central algorithm; long) | 3, 5, 17 |
| 7 | `PhysicsWorld.cpp` 3300-3421 (`SyncBody`) | Entity-to-body sync: static vs kinematic vs dynamic, wake rules, degenerate transforms | concepts 4, 17 |
| 8 | `PhysicsWorld.cpp` 4144-4182 (`WritePose`) | Body-to-entity write-back relative to the parent, keeping authored scale | matrices, decomposition |
| 9 | `PhysicsWorld.cpp` 3628-3640 (`MarkMoved`) plus 4214-4231 | A bitmap that orders moved bodies at cost proportional to what moved | bit operations |
| 10 | `PhysicsWorld.cpp` 1993-2045 (`MakeBodySetup`) | Mapping component data to box3d definitions; sanitizing input; why kinematic bodies do not recycle | 1 |
| 11 | `PhysicsWorld.cpp` 2102-2114 (`ApplyMass`) | Mass vs mass distribution; scaling inertia | inertia tensor |
| 12 | `PhysicsWorld.cpp` 1857-1918 (`AddColliderParts`, box/sphere/capsule part) | Baking scale into shapes; why spheres take the largest axis | 5, 6 |
| 13 | `Strata/src/Strata/Physics/PhysicsFilters.h` 1-60 | Category/mask filtering and the reserved query bit | bit masks |
| 14 | `Strata/src/Strata/Scene/PhysicsLayerSettings.h` 43-67 | Symmetric layer matrix and the "both agree" rule | 13 |
| 15 | `PhysicsWorld.cpp` 3598-3625 (`CountBegin`/`CountEnd`) and 422-443 (`TouchingPair`) | Folding per-shape contacts into per-entity Begin/End | 15 |
| 16 | `PhysicsWorld.cpp` 3643-3712 (`ProcessStepEvents`) | Reading a physics library's event buffers; skipping work nobody wants | 15 |
| 17 | `PhysicsSystem.cpp` 636-660 (`DispatchCollisionEvents`) | Safe event dispatch (snapshot, removed listeners, re-entrancy) | callbacks |
| 18 | `PhysicsWorld.cpp` 4499-4519 (`RayCallback`) and 5399-5417 (`Raycast`) | Ray query callbacks and clipping the ray to closer hits; inside-convex rule | 16 |
| 19 | `PhysicsWorld.cpp` 4535-4576 (`CollectOverlaps`) | Making query results deterministic by sorting by body index | determinism |
| 20 | `CharacterControllers.cpp` 384-422 (`ShapePlanes`, `SlideMove`) | Collide-and-slide with a plane solver; treating steep slopes as walls | vectors, planes |
| 21 | `CharacterControllers.cpp` 557-664 (`MoveController`) | The complete character move: gravity, jump, platforms, step-up, vertical pass, snapping (central algorithm; long) | 20 |
| 22 | `CharacterControllers.cpp` 680-718 (`PushBodies` push part) | Effective mass at a contact point; inelastic push; force cap | 3, cross product |
| 23 | `CharacterControllers.cpp` 928-999 (`CharacterControllerSet::Step`) | Parallel read-only moves then serial writes: determinism with threads | job systems |
| 24 | `PhysicsTaskSystem.cpp` 14-48 | Plugging a library's task callbacks into an engine job system; waiting thread runs the task | job systems |
| 25 | `PhysicsWorld.cpp` 1530-1584 (`ParkStaticBody`, `DisableParkedBodies`) | Amortizing an expensive removal across frames | 13, streaming |
| 26 | `PhysicsWorld.cpp` 4775-4787 (`ResolveCapacities`) and 2300-2318 (`GrowRoom`) | Sizing pools and growing by doubling; remembering demand | memory |
| 27 | `Strata/src/Strata/Scene/SceneInterpolation.cpp` 104-116 (`BlendPose`) | Interpolating poses: lerp translation, nlerp rotation on the shorter arc | quaternions |
| 28 | `StrataTests/src/Physics/PhysicsSimulationTests.cpp` 821-839 | Testing determinism with twin runs and a job system | doctest |
| 29 | `Samples/PhysicsPlayground/Scripts/GoalBasket.cpp` 1-26 and `LaunchPad.cpp` 1-22 | Triggers in game code, the smallest useful scripts | scripting basics |
| 30 | `Samples/PhysicsPlayground/Scripts/Playground.cpp` 225-255 (`UpdateGrab`) | Raycast picking and velocity-driven grabbing | 16 |

---

## 4. Figures

### Diagrams

1. **Layered overview**: Scene systems (Scripting, Animation, World, Physics, Audio) above Scene services above
   `PhysicsSystem` -> `PhysicsWorld` -> box3d world; side boxes `CharacterControllerSet`, `PhysicsMeshShapes` cache,
   `AssetMeshProvider` -> `MeshGeometryRegistry`, `PhysicsTaskSystem` -> JobSystem. Shows who may include whom.
2. **Entity hierarchy to bodies**: a tree of entities (RigidBody, child colliders, a child with its own RigidBody, a lone
   collider) and the bodies and shapes that result (the composition rule).
3. **Frame timeline**: one frame with `OnUpdate` of every system, the fixed loop running 0..N `OnFixedUpdate`s
   (accumulator bar filling and draining), `OnLateUpdate`, render; mark where physics applies changes, steps, dispatches.
4. **Inside a fixed step** (`Simulate`): flow chart ApplyChanges -> GrowRoom -> DisableParked -> HoldForMeshes? ->
   SyncEntitiesToBodies -> StepCharacters -> [CollisionSteps x (ApplyPendingForces -> b3World_Step(4 substeps) ->
   ProcessStepEvents)] -> WriteBack -> pair upkeep -> instruments.
5. **Two copies of the truth**: entity `TransformComponent` vs box3d body pose, with arrows "before the step: signaled or
   awake changes" and "after the step: moved dynamic bodies", annotated with `MarkModified` / `MarkTransformsChanged`.
6. **Contact pair folding**: box3d shape-pair contacts (several per entity pair, sensors) feeding counters of one
   `TouchingPair`; timeline of Begin at first contact, End at last; the Unconfirmed state on rebuild. A small state machine.
7. **Layer filtering bits**: 64-bit category/mask of a shape (bit L, row of matrix, bit 63 query category) and a query's
   filter; the symmetric 32x32 matrix.
8. **Character move**: side view of a capsule: across pass with planes (wall, steep slope as wall), step-up (lift, move,
   drop), vertical pass, snap down; ground states (OnGround, OnSteepGround, NotSupported, InAir) as a state diagram.
9. **Presence body**: character capsule vs 90% presence capsule; who interacts with which (bodies land on presence,
   triggers see presence, queries hit presence, mover collides with world).
10. **Push impulse**: contact normal, lever arm r, effective mass formula 1/(1/m + (r x n) . I^-1 (r x n)).
11. **Interpolation**: timeline of fixed steps T-h, T and frames between; the drawn time T + a - h; Blend/Compose/Exact
    roles on a small hierarchy (body root, camera child, attachment).
12. **Capacity growth**: room over time with bodies arriving (doubling steps), growth limit line, waiters queue; demand
    remembered for the next play.
13. **Parking timeline**: a cell unloading at step S, filters emptied at once, `b3Body_Disable` in slices from S+60.
14. **Body record memory layout**: `BodyRecord` in a `std::map`, `BodySlot` by box3d index, `ShapeSlot`, `RecordSlot`
    by entity index pointing into the map nodes (constant-time lookup both ways).
15. **Parallel write-back**: list moved bodies (main) -> parallel chunks (roots, then parented under non-moving parents)
    -> main thread (deferred, nested, outcomes) -> `MarkTransformsChanged`.
16. **Contact recycling** (optional): two boxes and the recycle distance/angle gates; stale point past an edge.

### Screenshots (physics has no rendering feature; screenshots show behaviour and tools)

1. Physics Playground overview (`Samples/PhysicsPlayground/Screenshots/Overview.png` exists) and the ball pit after a pour
   (`Screenshots/BallPit.png` exists).
2. The editor with collider gizmos: `viewport.setSettings {allColliders: true}` on the Playground (crates, ramp, pit
   walls), and with `allColliders: false` (only the selection's colliders).
3. Inspector of a RigidBody and of a Character Controller component (Rigid Body fields; tooltips).
4. Project Settings > Collision Layers page (named layers, the compact matrix) with the Playground's Ghost/Ball pair kept
   apart.
5. Project Settings > Physics > Simulation page (five fields) and Physics > Timing (FixedRate, Interpolation).
6. The Streaming panel's Physics row with "Count contacts" on ("Step ... ms (box3d ...) - awake ... - recycled ...%").
7. A `physics.stats` JSON answer (terminal screenshot or code block).
8. Before/after sequences (frame grabs via `viewport.capture {atFixedStep}` while paused, `play.step`): the domino run
   falling; the crate tower settling; ghosts sinking through the balls (layers); balls counted by the goal (trigger).
9. Interpolation on/off: a fast-moving body with a following camera at high frame rate (Third-Person sample, Project
   Settings > Timing > Interpolation off vs on); a motion-trail composite shows the judder (the doc cites 29.4 px peak to
   peak at 702 fps).
10. Character controller on stairs and slopes (Third-Person sample or a purpose-built scene): walking up a 0.3 m step and
    stopping at a 0.5 m one; standing on a 40 degree slope vs sliding on 50 degrees.

---

## 5. Rules and pitfalls ("why" boxes)

1. **Signal transform writes** (`MarkModified`, `ComponentAccess`, `Scene::SetWorldTransform`, at least
   `Scene::MarkTransformChanged`). Why: sleeping and static bodies are never polled; a silent write is never seen by
   physics (`PhysicsWorld.h` 52-58; AGENTS "Scene caches and the transform contract").
2. **Use `Teleport` for instant moves.** Why: a transform write moves the body only at the next fixed step, so queries in
   between see the old place; Teleport also breaks interpolation (`PhysicsSystem.h` 41-46; `PhysicsWorld.cpp` 5352).
3. **Apply forces in `OnFixedUpdate`, every step they should act.** Why: forces act during the next fixed step only and
   are cleared (`PhysicsWorld.h` 224-225; `Simulate` 5036-5045).
4. **Read the step via `Scene::GetFixedTimestep`/`GetMaxFixedSteps`, never `SceneSettings`.** Why: the project's
   `FixedRate` overrides the scene (DG "Fixed rate" 1414-1418).
5. **Tools count fixed steps, not frames.** Why: frames are not reproducible; steps are (`Scene::GetFixedStepCount`;
   AGENTS "Editor").
6. **Main thread only.** Why: box3d world slots are not thread-safe, the scene is owned by the main thread; physics
   parallelism is internal and deterministic (`PhysicsWorld.h` 90-92).
7. **Events are delivered after the step, not from inside it.** Why: listeners may destroy entities or call the physics
   API; the solver's state must not change while it runs (`PhysicsSystem.h` 48-53).
8. **Entity destruction from scripts goes through `ScriptSystem::DestroyEntity`/deferred destroy.** Why: physics and
   scripts hold references during the update (AGENTS "Scripting").
9. **Do not spawn bodies overlapping.** Why: box3d pushes overlaps apart at up to 3 m/s (`ContactPushSpeed`), enough to
   throw light bodies over walls (Release 0.5.0 line 90).
10. **Triangle meshes only on static bodies; triggers do not see them.** Why: a mesh has no volume or mass; box3d's
    sensors test convex shapes only (`AddColliderParts` 1945-1949; AR 369-370).
11. **A floor of many tiles bumps at the seams; make it one collider.** Why: inner edges of adjacent boxes catch sliding
    bodies (44 mm at 2 m/s), with or without recycling (DG "Contact recycling" 2281-2296).
12. **`ContactHertz` above the ceiling does nothing.** Why: box3d uses at most 1/8 of its substep rate; 30 Hz at 60
    steps/s (DG 1361-1365).
13. **Kinematic and character presence bodies never recycle contacts.** Why: riders on turning platforms crept 0.70 m in
    4 s with recycling (DG 2244-2247; `MakeBodySetup` 2031-2033).
14. **Stay within 20 km (box3d refuses 1e5 m).** Why: single precision (`c_MaxBodyCoordinate`; AGENTS "Worlds").
15. **Never let a body sit without collision below the growth limit.** Why: a body without collision falls through the
    world; box3d grows in place, only the limit makes bodies wait (AGENTS "Worlds"; DG World partition).
16. **Collision layers are the project's, not the scene's.** Why: a name must mean the same in every scene and prefab;
    scripts change only the running copy (DG 1292-1314).
17. **Physics settings are applied on the main thread.** Why: `IProjectSettings` contract; loaders' worker threads never
    read the provider (DG 1305-1316, 1355-1360).
18. **Follow moving bodies with the drawn transform in `OnLateUpdate`.** Why: the world transform is a step ahead of what
    is drawn; a camera following it judders (DG "Interpolation" 2544-2549).
19. **Move what others ride in `OnFixedUpdate` or as a kinematic body.** Why: carrier and rider must be on the same clock
    (DG 2547-2549).
20. **Compare chaotic results over many layouts.** Why: a pile's time to sleep changes by seconds with a bit's difference
    (DG 2266-2275).
21. **Character controller rotation and scale do not change its capsule.** Why: it is an upright capsule on the entity's
    origin by design (`PhysicsComponents.h` 70-74).
22. **An entity with both RigidBody and CharacterController is the rigid body.** Why: one mover per entity (warning).
23. **Damping differs from Jolt's formula.** Why: box3d multiplies by 1/(1 + d h) per sub-step (Release 0.5.0 93-95).
24. **Restitution needs speed above 1 m/s to bounce.** Why: box3d's restitution threshold (skill `strata-scripting`).
25. **Never dereference box3d IDs without validity checks; shapes resolve through generation-checked slots.** Why: events
    may name shapes that are already gone (`ShapeSlot` `PhysicsWorld.cpp` 550-560).

---

## 6. Hands-on

### For game developers

| Exercise | Difficulty | Proves |
| --- | --- | --- |
| Make a crate fall onto a floor in the editor (RigidBody Dynamic + BoxCollider, floor with a BoxCollider only); press Play | Easy | Body composition, static vs dynamic |
| Build a stack of 10 crates and topple it with a script impulse (`AddImpulseAtPosition`) | Easy | Impulses, sleeping, waking |
| Change friction and restitution of four balls (wood, metal, rubber, ice) and compare | Easy | Materials |
| A trigger zone that counts balls (copy GoalBasket) and a launch pad (copy LaunchPad) | Easy | Triggers, OnTriggerEnter |
| A gun that shoots via `Physics::Raycast` and pushes what it hits | Medium | Queries, layer masks, ignore self |
| A grab tool (as `UpdateGrab`) | Medium | Raycast picking, velocity control |
| A Ghost layer that passes through balls but not walls; toggle at runtime with `Physics::SetLayersCollide` | Medium | Collision layers |
| A player with a CharacterController: walk, jump, stairs, a slope too steep, a moving platform made kinematic | Medium | Character controller API, ground state |
| A follow camera that judders, then fixed with `GetDrawnPosition` in `OnLateUpdate`; toggle Timing > Interpolation | Medium | Fixed step vs frame, interpolation |
| Impact sounds louder for harder hits (as `Impact.cpp`) | Medium | Contact normal and velocities |
| Tune Physics > Simulation's Sleep Threshold and observe a ball pit with `physics.stats` | Medium | Sleeping, diagnostics |
| Write a `.json` command script that pauses, steps to a fixed step and checks an outcome with `until` (as the Playground's regression) | Hard | Determinism, step counting |

### For engine developers

| Exercise | Difficulty | Proves |
| --- | --- | --- |
| Write a doctest that drops a sphere and checks it rests at height r (use `PhysicsTestUtils.h`) | Easy | Test harness, the world API |
| Add `GetLinearVelocity` checks to a test that bodies sleep; read `PhysicsStats::SleepingBodyCount` | Easy | Instruments |
| Trace one fixed step in Tracy (`ST_PROFILE_SCOPE("PhysicsWorld::Simulate - box3d")`) and attribute time to sync, library, write-back | Medium | Step anatomy |
| Implement an `OverlapCapsule` query (world, system, service, host function appended at the end, SDK, test, feature script) | Medium-Hard | Query plumbing, ABI rules, feature test rule |
| Implement a shape cast (`b3World_CastShape`) query `SphereCast` with sorted hits and the same filters | Hard | Sweeps, determinism of results |
| Add a new collider type (cylinder via hull) with gizmo, inspector, scale rule and tests | Hard | Component registration, shape building |
| Expose a hinge or distance joint (box3d joints) as a component: lifetime with bodies, rebuild, serialization | Very hard | The rebuild model, records, events |
| Reproduce the determinism test: run a pile with 0 and 3 workers and diff poses | Medium | Determinism with threads |
| Run `Tools/PhysicsSweep.py knobs` on a local build for one knob and read the report | Medium | Tuning by measurement |
| Make a regression test fail without a fix (e.g. remove `enableContactRecycling = false` for kinematic bodies and watch `Physics.Settling` "Boxes ride a moving and turning kinematic platform") | Medium | Why each rule exists |

---

## 7. Glossary

- **Rigid body**: an object that moves but never deforms; state is pose and velocities.
- **Static body**: a body that never moves by simulation (infinite mass); in Strata also a collider without a rigid body.
- **Dynamic body**: a body the solver moves under forces and contacts.
- **Kinematic body**: a body moved by game code with a velocity; pushes dynamic bodies, is not pushed.
- **Collider / shape**: the geometry of a body used for collision (box, sphere, capsule, hull, mesh).
- **Convex hull**: the smallest convex shape containing a set of points; box3d limits hulls to 128 faces/edges.
- **Triangle mesh collider**: collision against a mesh's triangles; static only, no volume.
- **Compound / baked compound**: several shapes acting as one; box3d's form of an offset triangle mesh.
- **Trigger / sensor**: a shape that reports overlaps without collision response.
- **Presence body**: Strata's kinematic capsule (90% radius) that lets others detect a character controller.
- **Character controller**: a kinematic mover that walks a capsule with collide-and-slide instead of forces.
- **Mover (box3d)**: box3d's query API for character movement (`b3World_CollideMover`, `b3World_CastMover`, `b3SolvePlanes`).
- **Collide and slide**: moving a shape by projecting its motion onto the planes of what it touches.
- **Step height / step up**: the highest ledge a controller walks onto without jumping.
- **Ground snapping**: keeping a controller on the ground while walking down.
- **Ground state**: OnGround, OnSteepGround, NotSupported, InAir.
- **Fixed timestep**: simulation time per step (1/60 s by default), independent of the frame rate.
- **Accumulator**: the remainder of frame time not yet simulated.
- **Spiral of death**: when steps take longer than they simulate and frames fall further behind; capped by max steps.
- **Time dilation**: Strata's choice to drop steps and slow the game when it cannot keep up.
- **Sub-step**: box3d's internal division of a step (4) for its soft-step solver.
- **Collision step**: Strata's `CollisionSteps`, box3d steps per fixed step.
- **Broad phase**: finding candidate pairs with bounding-volume trees.
- **Narrow phase**: computing exact contacts (manifolds) between candidate pairs.
- **AABB**: axis-aligned bounding box.
- **Manifold / contact point**: the points, normal and separations describing a touch.
- **Contact constraint**: the solver's rule keeping touching bodies apart.
- **Soft contact / contact hertz / damping ratio**: a spring-like contact with stiffness frequency and damping.
- **Push speed (contactSpeed)**: the fastest speed at which overlap is resolved.
- **Restitution**: bounciness (0 to 1).
- **Friction**: resistance to sliding.
- **Damping**: velocity loss over time (linear and angular).
- **Gravity scale**: multiplier of the scene's gravity for one body.
- **Inertia tensor**: rotational mass distribution; effective mass at a point.
- **Impulse**: an instant change of momentum; force times time.
- **Continuous collision (CCD) / bullet / tunnelling**: sweeping fast bodies so they do not pass through thin geometry.
- **Island**: a group of bodies connected by contacts, solved and put to sleep together.
- **Sleep threshold**: speed below which a body (with its island) falls asleep after 0.5 s.
- **Contact recycling**: box3d reusing a contact's computed points while bodies barely moved.
- **Ghost collision**: a bump at an internal edge, e.g. between floor tiles.
- **Collision layer / layer matrix**: one of 32 groups and the table of which collide.
- **Category bits / mask bits**: the bit filter box3d checks for every pair and query.
- **Query category**: Strata's bit 63 every shape's mask accepts so queries find all layers.
- **Raycast / RaycastAll / overlap / shape cast (sweep)**: spatial queries; shape casts are not exposed by Strata.
- **Collision event (Begin/End)**: Strata's per-entity-pair notification.
- **Touching pair**: Strata's tracked pair of entities with a contact count.
- **Contact interest / watch**: asking Strata to track an entity's pairs.
- **Write-back**: copying simulated poses to entity transforms after the step.
- **Synchronization (sync)**: bringing bodies in line with changed entity transforms before the step.
- **Signal (on_update)**: EnTT notification that a component changed.
- **Degenerate transform**: a world matrix that cannot be decomposed (e.g. zero scale).
- **Suspended body**: Strata's body out of the simulation until its transform is valid.
- **Parked body**: Strata's static body out of the simulation, colliding with nothing until disabled later.
- **Capacity / room / growth limit / demand**: what a world reserves, its cap, and what it needed beyond its room.
- **Body record / slot**: Strata's per-entity bookkeeping and constant-time lookups by box3d and entity index.
- **Cooking**: precomputing hull or mesh collision data.
- **Mesh provider**: the source of triangle data for mesh colliders.
- **Interpolation (state interpolation)**: drawing between the last two fixed-step poses.
- **Step alpha**: how far between those poses a frame draws.
- **Blend / Compose / Exact**: the three ways an interpolated entity is drawn.
- **Drawn transform**: the matrix renderers draw, as opposed to the simulated world transform.
- **Determinism**: identical results for identical input; Strata's holds for any thread count.
- **Golden hash**: a stored hash of a reference run used to detect behaviour changes.
- **Settle scene / sweep**: Strata's representative test scenes and the tool that measures tuning over them.
- **Job system / worker**: the engine's thread pool; box3d's tasks run on it.

---

## 8. Proposed chapters

1. **Why games need physics** (concept, both, S): the problems, the engines on the market, what Strata chose (box3d) and
   what it does not do (joints, sweeps, ragdolls). Prerequisites: none.
2. **Time in a game: the fixed step** (concept + internals, both, M): accumulator, max steps, dropping, time dilation,
   `Scene.Timing`, `OnFixedUpdate`. Prerequisites: game loop, scene systems.
3. **Rigid bodies and colliders in Strata** (tutorial, game, M): components, body types, the composition rule, scale,
   materials, the Playground's crates and balls; gizmos. Prerequisites: editor basics, entities.
4. **How a rigid body simulation works** (concept, engine, L): integration, mass and inertia, broad/narrow phase,
   contacts as soft constraints, sub-stepping, friction, restitution, CCD, islands and sleep; box3d's choices.
   Prerequisites: vectors, quaternions, chapter 2.
5. **Inside PhysicsWorld: the step** (internals, engine, XL): records and slots, change tracking, sync, write-back,
   determinism with threads, task system, mesh cooking, capacities. Prerequisites: 4, ECS signals, job system,
   transform contract.
6. **Contacts and triggers** (concept + internals + tutorial, both, M): events, pair folding, interest, dispatch rules,
   scripts' callbacks, trigger limits; GoalBasket, LaunchPad, Impact. Prerequisites: 3, scripting basics.
7. **Asking the world: queries** (tutorial + internals, both, S-M): raycasts, overlaps, masks, ignore, determinism of
   results; shooting and grabbing in the Playground; the missing sweep as an exercise. Prerequisites: 3, 8 (layers)
   optionally.
8. **Collision layers** (tutorial + internals, both, S): project table, matrix, filter bits, runtime changes, the Ghost
   layer. Prerequisites: 3, project settings.
9. **Character controllers** (concept + internals + tutorial, both, L): why kinematic, collide and slide, steps, slopes,
   snapping, platforms, pushing, presence body, root motion hook, determinism. Prerequisites: 4, 7.
10. **Smooth motion: interpolation** (concept + internals, both, M): judder, state interpolation, roles, alpha, rules for
    renderers and game code. Prerequisites: 2, transform hierarchy, render scene basics.
11. **Physics at scale and in streaming worlds** (internals, engine, M): capacities and growth, sliced and parallel
    creation, parking, reservation by the streamer, 1e5 m limit. Prerequisites: 5, World partition.
12. **Tuning and measuring physics** (internals + reference, engine, M): Physics.Simulation fields, contact recycling and
    the sweep, sleep threshold, stiffness ceiling, instruments, `physics.stats`, perf tests, `PhysicsSweep.py`.
    Prerequisites: 4, 5.
13. **Physics reference** (reference, both, M): every component property, settings field, service function, script API
    and command with units, ranges and defaults.

---

## 9. Not determined

- Exact release for several internals: parallel body creation, sliced preparation (`PrepareLoadedScene`), shared box
  hulls, `invokeContactCreation` skipping; the documents name waves, not always releases. Interpolation and `FixedRate`
  are wave 8 work, unreleased at this commit (0.7.0 is the latest release note).
- I did not read line by line `PhysicsWorld.cpp` 2120-2290 (merging and rebuild bookkeeping), 2770-3040 (hierarchy
  changes and change rounds), 3714-3960 (checked and seeded pairs), 4300-4435 (rest of the write-back), nor
  `CharacterControllers.cpp` 740-927 (apply-changes and teleport bookkeeping), `AssetMeshProvider.cpp`,
  `PhysicsRuntime.cpp` beyond the hook installation, `PhysicsSimulationSettings.cpp` beyond line 80.
- `Scene/SceneInterpolation.cpp` was read only to its first 130 lines; the capture pass in `Scene.cpp`
  `UpdateWorldTransforms` was not read.
- Test bodies were read only for the determinism and golden-hash cases; other cases are known by name.
- `StrataTests/src/Perf/PhysicsPerfTests.cpp`, `SceneGenerators.cpp`, the budgets' values and
  `StrataTests/Editor/PhysicsPlaygroundCommands.json.in` were not opened.
- The Playground's scene (`Assets/Scenes/Main.stscene`), prefabs and materials were not opened; the station layout comes
  from its README.
- box3d's own internals (solver, soft step, sleep test, CCD) were not read; statements about them come from Strata's
  comments and docs. Whether box3d's restitution threshold is 1 m/s comes from the scripting skill, not from box3d's
  source.
- The editor UI pages (`CollisionLayersPage.cpp`, the generic settings page for Physics.Simulation and Timing, the
  Inspector's Physics section) were not read; their probe keys come from DG.
- There is no Manual page for physics (`Docs/Manual/` has none); the game-facing physics documentation is in the
  `strata-scripting` skill and `Docs/Manual/Scripting.md` "Following moving things" only. The book must write it.
