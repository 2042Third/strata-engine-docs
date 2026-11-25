# Inventory: Animation (skeletons, clips, controllers, events, root motion, skinning)

Surveyed at `main` 822a7a46. Paths are relative to the repository root `G:/GameEngineAI`. Line numbers are of that commit.
"AR" is `Docs/Architecture.md`, "DG" is `Docs/DeveloperGuide.md`. Releases: `Docs/Releases/<version>.md`; waves: `Docs/Roadmap.md`.

Sources read in full: every file of `Strata/src/Strata/Animation/` except the middle of `AnimationPreview.cpp` (lines 330-540,
630-662 skimmed by function names) and `AnimationController.cpp` lines 248-553 (the JSON reader and writer, read by outline);
`Scene/SceneServices.h` (animation part), `Scene/Components.h` (`SkinComponent`); the skinning parts of
`Renderer/RenderScene.cpp`, `Renderer/Mesh.h`, `Renderer/SceneRendererExtraction.cpp`, `shaders/Include/Scene.slang`,
`shaders/Scene/Mesh.vert.slang`; the animation parts of `Asset/GltfImporter.cpp`; the script ABI, SDK and host functions;
`StrataEditor/src/Editor/EditorAnimationCommands.cpp` (registrations); `UI/AnimationAssetViews.h`; the test list and four
tests; the Third-Person sample's controller and scripts; AR "Animation" (2612-2746), DG "Animation" (2196-2225), DG
"Animation commands" (3703-3722), DG "Skinned meshes" (4488-4505), AR "Skinned proxies" (2324-2340), the Roadmap and
release notes where they name animation.

---

## 1. Features

### 1.1 The module and its place

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| Animation module (a layer) | Skeletal animation as a layer above Scene; may include Core, Asset, Reflection, Scene only | `Strata/src/Strata/Animation/`; `StrataTests/Architecture/Layers.json` 63-68 | AR "Animation" 2612-2616; DG "Animation" 2196-2200 | 0.3.0 (wave 3, landed 2026-10-12) |
| Optional module | `STRATA_WITH_ANIMATION` (default ON) leaves the module out of a build; `#if ST_WITH_ANIMATION` guards the importer's skeleton/clip code | `CMakeLists.txt` 30; `Strata/CMakeLists.txt` 28; `Asset/GltfImporter.cpp` 1008, 1601, 1944, 1988-1999 | DG "Optional modules"; Roadmap 711-712 | 0.4.0 |
| Module registration | `RegisterAnimationModule`: components, three asset loaders, the "Animation" scene system (After Scripting, Before Physics, soft; not in Simulate; stage `Scene.Animation`) | `Animation/AnimationRegistration.cpp` 15-42; called from `Engine/BuiltinModules.cpp` 72 | AR 2668-2669; DG 2196-2200 | 0.3.0 |
| Only Engine and AssetPipeline include it | The renderer and the script host reach animation only through scene services | `Layers.json` 117, 123 | DG 2208-2210; AGENTS.md "Animation" | 0.3.0 |

### 1.2 Data types and math

| Feature | What it is | Where | Documented |
| --- | --- | --- | --- |
| `JointPose` | Local TRS of a joint relative to its parent (root joints: to the animator entity), scale applied first | `Animation/AnimationTypes.h` 15-22 | AR 2618-2620 |
| `JointIndex`, `c_NoJoint` | 16-bit joint index, `0xFFFF` reserved for "no parent" | `AnimationTypes.h` 24-26 | `Skeleton.h` 35 |
| `AnimationMath::Normalize` | Unit quaternion, identity for zero or non-finite input | `AnimationTypes.h` 32-39 | (code comment) |
| `AnimationMath::Slerp` | Shorter-arc slerp, nlerp fallback when the arc is short (cos > 0.9995) | `AnimationTypes.h` 43-58 | (code comment) |
| `ToMatrix`, `MultiplyAffine` | TRS to matrix; affine product skipping the fourth row | `AnimationTypes.h` 61-85 | (code comment) |

### 1.3 Assets

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| `Skeleton` asset | Unique joint names, parents in topological order (parents first), rest pose, root motion joint; name index; max 4096 joints | `Animation/Skeleton.h` 17-76; `Skeleton.cpp` 43-94 | AR 2618-2620 | 0.3.0 |
| Skeleton cooked format "STSK" v1 | Header, 44-byte joints, names; `Deserialize` validates counts, order, finiteness, uniqueness, trailing data | `Skeleton.cpp` 12-29, 96-161 | `Skeleton.h` 26-27 | 0.3.0 |
| `ComputeModelTransforms` (forward kinematics) | One pass over joints: model = parent model x local | `Skeleton.cpp` 178-187 | `Skeleton.h` 64-66 | 0.3.0 |
| `AnimationClip` asset | Channels per joint and path (T, R, S), Step/Linear/CubicSpline keys, shared key-time arrays, duration = last key, hold before first/after last key | `Animation/AnimationClip.h` 17-131; `AnimationClip.cpp` 150-229 | AR 2620-2624 | 0.3.0 |
| Clip cooked format "STAC" v1 | Header, name, targets, 20-byte channels, times, values; every count bounded before allocation | `AnimationClip.cpp` 18-42, 317-419 | `AnimationClip.h` 74-75 | 0.3.0 |
| Shared key times | Channels with identical time arrays share one (FNV-1a hash + exact compare) | `AnimationClip.cpp` 114-124, 206-222 | AR 2622 | 0.3.0 |
| Keyframe reduction (`ReduceKeys`) | Importer drops keys interpolation reproduces (tolerance 1e-5, rotations 1e-4 quat distance; window 256; cancellable every 256 keys); cubic splines untouched | `AnimationClip.cpp` 44-50, 231-315 | `AnimationClip.h` 91-97; AR 2633 | 0.3.0 |
| Clip binding by name | `Bind` maps channels to a skeleton's joints once; missing targets skipped; root motion channels recorded | `AnimationClip.cpp` 438-457; `AnimationClipBinding` `AnimationClip.h` 61-66 | AR 2623-2624 | 0.3.0 |
| Sampling | `SampleChannel` (binary search with `upper_bound`, step/lerp/slerp/Hermite), `Sample`, `SampleRootMotionJoint` | `AnimationClip.cpp` 459-558 | `AnimationClip.h` 113-119 | 0.3.0 |
| No clip compression | Keys are raw float32; only reduction and time sharing. Compression is listed as later work ("compressed clips if measured to help") | n/a | Roadmap "Later", wave 9 `animation-runtime-2` | not landed |
| `AnimationController` asset (`.stanimator`) | JSON document: parameters (Float, Bool, Trigger), states (clip or none, speed, loop, events), default state, transitions (from a state or Any State, conditions, exit time, cross-fade duration, CanTransitionToSelf) | `Animation/AnimationController.h` 16-153; `AnimationController.cpp` 144-593 | AR 2624-2626; header comment 95-105 | 0.3.0 |
| Controller validation | Limits (256 params, 1024 states, 4096 transitions, 16 conditions, 256 events/state, speed 100, fade 60 s), name rules, mode/type agreement, events stable-sorted by time | `AnimationController.cpp` 144-221 | `AnimationController.h` 112-122 | 0.3.0 |
| Transitions grouped by source | Counting sort into `m_TransitionOrder` + `m_StateTransitionStart`, any-state list apart | `AnimationController.cpp` 223-245 | `AnimationController.h` 141-152 | 0.3.0 |
| Asset loaders | Skeleton and clip from cooked binary, controller from its JSON source | `AnimationRegistration.cpp` 19-31 | AR 2626 | 0.3.0 |
| Asset types | `AssetType::Skeleton`, `AnimationClip`, `AnimationController` (extension `.stanimator`) | `Asset/AssetTypes.h` 26-28; `AssetTypes.cpp` 52 | | 0.3.0 |

### 1.4 Import (glTF)

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| One skeleton per model | Joints of every skin plus animated nodes plus their ancestors, parents first by iterative walk; duplicate names made unique; root motion joint = topmost joint of any skin; sub-asset "Skeleton" | `Asset/GltfImporter.cpp` 1009-1130 | AR 2627-2629 | 0.3.0 |
| One clip per animation | Sub-asset `Animation/<name>` (or index when the name is not unique), keys reduced, channels on nodes outside the skeleton or duplicates warned and skipped; morph-target weights skipped and reported | `GltfImporter.cpp` 1606-1676 | AR 2629-2630 | 0.3.0 |
| Skinned meshes and skin bindings | `MeshSkinBinding` (skeleton joint per skin joint, inverse bind matrices, per-joint bind bounds, `MaxJointExtent`), skin stream `MeshSkinVertex` (4 x uint16 joints, 4 x uint16 weights summing to 65535) | `Renderer/Mesh.h` 28-56; importer 1144 ff., 1356 | AR "Asset pipeline", `MeshSkinBinding`; AR 2630 | 0.3.0 |
| Entities of the imported model | Root = animator (`AnimatorComponent` with skeleton and first clip); skinned meshes under it with `SkinComponent`; joints with content (rigid mesh, camera, light, foreign child) become entities with `AttachToJointComponent` at the joint's rest pose; plain joints are no entities | `GltfImporter.cpp` 1925-1963, 1988-1995 | AR 2630-2633 | 0.3.0 |
| Import scale baked | Root keeps scale 1; meshes, joints, bind matrices, clips scale | test `GltfSkinImportTests.cpp` 384 | Roadmap 394-397 (`authoring-and-playtest`) | 0.4.0 |
| Importer version | `GltfImporter::GetVersion()` returns 11 (AR 2627 still says "version 9") | `Asset/GltfImporter.h` 39 | AR 2627 (stale) | |

### 1.5 Components

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| `AnimatorComponent` | Skeleton, Controller (none: simple mode), Clip, Speed (negative: backwards, +/-100), Loop, PlayOnStart, ApplyRootMotion, CullingMode | `Animation/AnimationComponents.h` 27-37; registered `AnimationComponents.cpp` 33-45 | AR 2634-2637 | 0.3.0 |
| `Clip` inactive reason | Inspector greys `Clip` while a controller is set (`SetInactiveReason`) | `AnimationComponents.cpp` 16-21, 45 | DG "Inspectors" | |
| `AnimatorCullingMode` | `AlwaysAnimate`, `WhenVisible` | `AnimationComponents.h` 15-21 | AR 2700-2722; DG 2214-2225 | 0.3.0, fixed 0.4.0 review round |
| `SkinComponent {Animator}` | Makes a mesh renderer skinned by the named animator's pose; type lives in `Scene/Components.h` so the renderer can read it; registered by the animation module | `Scene/Components.h` 170-183; `AnimationComponents.cpp` 27-31 | AR 2637-2640 | 0.3.0 |
| `AttachToJointComponent {Animator, Joint}` | Places an entity at a joint of the pose every update | `AnimationComponents.h` 39-46; `AnimationComponents.cpp` 47-52 | AR 2723-2726 | 0.3.0 |

### 1.6 Playback: `AnimatorInstance` (no scene)

| Feature | What it is | Where | Documented |
| --- | --- | --- | --- |
| Simple mode | No controller: plays the component's clip (`c_ClipState`) | `AnimatorInstance.cpp` 187-196, 630-637 | AR 2635 |
| State machine | One current state; after each advance, any-state transitions then the current state's, first that holds and whose exit time was reached fires; one per update | `AnimatorInstance.cpp` 725-763 | AR 2641-2648 |
| Conditions | Greater, Less (float), True, False (bool), Set (trigger); all must hold | `AnimatorInstance.cpp` 426-444 | `AnimationController.h` 23-30 |
| Triggers consumed | The firing transition resets the triggers it tests | `AnimatorInstance.cpp` 446-453 | AR 2644 |
| Exit times | Normalized time incl. loops; looping states with exit < 1 fire once per loop at that point; else once reached | `AnimatorInstance.cpp` 734-745 | AR 2644-2647 |
| `CanTransitionToSelf` | Any-state transitions skip their own target unless set | `AnimatorInstance.cpp` 751-752 | AR 2647 |
| Cross-fades | Up to `c_MaxPlaying` = 4 entries; target weight grows linearly; others keep their proportions; a fifth drops the faintest and renormalizes | `AnimatorInstance.cpp` 247-288, 587-609 | AR 2647-2649 |
| Pose blending | Weighted sums: T and S linear, R normalized weighted sum on one hemisphere | `AnimatorInstance.cpp` 791-823 | AR 2649 |
| Commands | `Play`, `CrossFade`, `PlayClip`; parameters `SetFloat`/`SetBool`/`SetTrigger` by name, refused for wrong type or non-finite | `AnimatorInstance.cpp` 290-424 | `AnimatorInstance.h` 144-159 |
| Waiting for the controller | Commands and parameter values given while the controller loads wait (`m_PendingState`, `m_PendingParameters`) | `AnimatorInstance.cpp` 292-300, 357-387, 618-629 | AR 2651 |
| Reload keeps parameter values | Same name and type keep their value when a new controller object arrives | `AnimatorInstance.cpp` 212-245 | AR 2651-2652 |
| Controller changed under it | Entries naming states that no longer exist restart at the default state | `AnimatorInstance.cpp` 640-650 | |
| Loop accounting | `AdvanceEntry` walks loop boundaries forward and backward, counts crossings (`Playing::Loops`), at most `c_MaxEventLoops` = 4 loops of events per update (the rest skipped arithmetically) | `AnimatorInstance.cpp` 455-585 | AR 2642-2644, 2649-2650 |
| Events | Current state's events (not fading-out states) fire each time the playhead passes them, in order, also across loop boundaries and backwards; an event at time 0 fires at start and per loop | `AnimatorInstance.cpp` 472-503, 541-578 | AR 2649-2650 |
| Rest pose with nothing playing | `Evaluate` with no entries returns `ComputeRestPose` | `AnimatorInstance.cpp` 771-776; `RestPose.cpp` 9-13 | AR 2652, 2735-2737 |
| State without clip | Over at once (normalized 1), shows the rest pose | `AnimatorInstance.cpp` 458-467 | AR 2652 |
| Settings | Speed, Loop, ApplyRootMotion, Transitions (off for previews) | `AnimatorInstance.h` 82-88 | |
| Play revision | Counter changed whenever what plays changes (reach cache key) | `AnimatorInstance.h` 174-176; `.cpp` 173, 251, 596-597 | AR 2712-2714 |

### 1.7 Root motion

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| `RootMotionSetup` | Ancestors' rest transform and rotation of the root motion joint; subtree mask | `AnimatorInstance.h` 23-30; `.cpp` 101-123 | AR 2681-2685 | 0.3.0 |
| Extraction | Horizontal travel and yaw about +Y per update, per pass through the clip, split at loop crossings (whole loops included, up to 64), in the frame the root faced at clip start, weighted by blend | `AnimatorInstance.cpp` 17-97, 652-723 | AR 2681-2685 | 0.3.0 |
| Holding the root | The pose moves the root's subtree back (offset and yaw) so the mesh does not run ahead of the entity | `AnimatorInstance.cpp` 62-74, 826-847 | AR 2685 | 0.3.0 |
| `AnimationSystem::ApplyRootMotion` | The one place that moves the entity: move through world (incl. scale) and parent inverse, turn multiplies rotation, `MarkModified<TransformComponent>` | `AnimationSystem.cpp` 788-827 | AR 2685-2689; DG 2211-2213 | 0.3.0 |
| Root motion through a character controller | `ICharacterControl::AddCharacterMotion` walks the move at the next fixed step (collides, climbs, keeps ground); only the turn is written | `AnimationSystem.cpp` 801-812 | AR 2689-2694 | 0.3.0 integration |

### 1.8 The scene system: `AnimationSystem`

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| Records | One `AnimatorRecord` per `AnimatorComponent`; added on construct signal, flagged on destroy, compacted in one order-keeping pass | `AnimationSystem.h` 193-235; `.cpp` 147-274 | AR 2669-2680 | 0.3.0 |
| Record order | Sorted by entity at start, then insertion order; results and events go out in that order | `AnimationSystem.cpp` 101-122 | AR 2676-2680 | 0.3.0 |
| Activity | Deactivated animators reset; reactivated ones start again with PlayOnStart | `AnimationSystem.cpp` 276-330 | AR 2670-2671 | 0.3.0 |
| Asset sets | Animators with the same (skeleton, controller, clip) share a set: assets requested once per update, bindings and reaches once per skeleton x clip; set held while used; failures logged once per set | `AnimationSystem.h` 156-182; `.cpp` 336-500 | AR 2671-2672 | 0.3.0 |
| Clip played directly | Per-record clip, binding and reach, rebound on skeleton change | `AnimationSystem.cpp` 502-533 | | 0.3.0 |
| Parallel evaluation | `JobSystem::ParallelFor` in batches of 8: classify (None/Waiting/Sync/Step) and step in place; Sync records queued, synced on the main thread in record order, then stepped in a second ParallelFor | `AnimationSystem.cpp` 572-654, 718-786 | AR 2672-2676; DG 2208-2210 | 0.3.0 |
| Determinism | Jobs read the registry and sets, write only their record; a test compares 0, 1 and 7 threads bit for bit | `AnimationSystem.cpp` 601-621; `StrataTests/src/Animation/AnimationSystemTests.cpp` 1036-1096 | DG 2208-2210 | 0.3.0 |
| Publishing | Main thread, record order: pose versions, events queued, root motion last; then attachments, compaction, event dispatch | `AnimationSystem.cpp` 656-716 | AR 2676-2680 | 0.3.0 |
| Idle cost | No records: update returns after resetting stats | `AnimationSystem.cpp` 585-591 | AR 2680 | 0.3.0 |
| Attachments | Local transform so world = animator world x joint pose; skipped when identical and untouched; refuses cycles (entity above its animator) | `AnimationSystem.cpp` 829-888 | AR 2723-2726 | 0.3.0 |
| Event dispatch | Snapshot of listeners; removed listeners not called; names copied | `AnimationSystem.cpp` 890-917, 1093-1113 | AR 2679-2680 | 0.3.0 |
| Stats | `AnimationSystemStats` (advanced, evaluated, culled, waiting, sets, attachments, events, reach updates, paused evaluations) | `AnimationSystem.h` 40-57 | | 0.3.0+ |
| WhenVisible culling | Unseen animators advance but skip `Evaluate`; seen = reported in the previous update; first pose always computed | `AnimationSystem.cpp` 739-755, 757-763 | AR 2700-2706; DG 2214-2225 | 0.3.0 |
| Reach | `AnimationReach::Compute` samples each clip at 15/s (2-48 samples): joint-origin boxes with and without root motion, max scale; union published with the pose; recomputed only when play revision, set reach version, culling mode or root motion change | `AnimatorInstance.h` 36-46; `.cpp` 125-166, 850-865; `AnimationSystem.cpp` 764-786 | AR 2706-2716 | 0.3.0 (reach version caching later) |
| Rigid-part animators pose always | WhenVisible animator with attachments but no skin poses every update | `AnimationSystem.cpp` 744-750 | AR 2723-2726 (bullet) ; DG 2219-2220 | 0.4.0 review round |
| Stale-pose report and paused posing | `ReportVisible` returns whether the drawn pose is older than the time; `OnPausedUpdate` poses those at their time (no advance) | `AnimationSystem.cpp` 935-968 | AR 2716-2722; DG 2220-2225 | 0.4.0 (Roadmap 327-329) |
| Sub-scenes and InstantiateMany | Animators of additive sub-scenes and mass-instantiated prefabs each get their own record | tests `AnimationSystemTests.cpp` 900, 982, 1101 | Roadmap 270-271 | 0.3.0 integration |
| Interpolated characters | Skins posed against the animator's drawn transform; attachments stay on their joint on frames without a step | `RenderScene.cpp` 1297-1300; test `AnimationSystemTests.cpp` 1704 | DG 4490-4492 "Skinned meshes" | wave 8 (interpolation) |

### 1.9 Scene services (the only way in from other modules)

| Feature | What it is | Where | Documented |
| --- | --- | --- | --- |
| `SkeletonPose` | Joints (model space), version, reach, reach scale | `Scene/SceneServices.h` 270-280 | AR 2706-2716 |
| `ISkinningPoses` | `GetPose`, `GetPosesVersion`, `ReportVisible`, `GetRenderTransforms`/`Version` | `SceneServices.h` 289-315 | DG 4493-4505 |
| `IAnimatorControl` | Play, PlayClip, CrossFade, SetFloat, SetBool, SetTrigger, ResetTrigger, SetSpeed, GetCurrentState, GetNormalizedTime, IsInTransition, GetJointTransform, HasAnimator | `SceneServices.h` 317-351; implemented `AnimationSystem.cpp` 974-1087 | DG 2206-2210 |
| `IAnimationEventSource` | Add/remove listeners of `AnimationEventInfo` (animator, id, name, state, time) | `SceneServices.h` 353-376 | AR 2679-2680 |
| Registration | `AnimationSystem` registers the three in its constructor, unregisters in its destructor | `AnimationSystem.cpp` 77-99 | `SceneServices.h` 20-33 |

### 1.10 Skinning in the renderer (the boundary; details belong to the Rendering area)

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| Skin proxies and pose inputs | `EvaluatePose`: animator entity, `GetPose`, animator drawn/world matrix, `AnimatorToProxy` | `Renderer/RenderScene.cpp` 1275-1320 | AR 2324-2327 | 0.3.0 |
| Palette | Per skin joint `AnimatorToProxy * pose[joint] * inverseBind`, 3x4 rows; posed bounds = union of per-joint bind boxes transformed; grown by reach x `MaxJointExtent` | `RenderScene.cpp` 1322-1339 | AR 2327-2335 | 0.3.0 |
| Change-driven palette updates | Skips the whole pass when poses version, transforms, hierarchy, drawn transforms unchanged; per proxy skip on version/binding/placement; parallel in batches; `RecordPaletteChange` | `RenderScene.cpp` 1341-1435 | AR 2335-2340; DG 4493-4500 | 0.3.0 |
| Provider change | Versions are a provider's own: a new provider recomputes every palette | `RenderScene.cpp` 1357-1360, 1390 | AR 2738-2740 | 0.4.0 |
| Linear blend skinning shaders | `ST_SKINNED` variants of `Mesh.vert` and `ShadowMesh.vert` (+ velocity, local shadow); `BlendJoints` (4 influences), `SkinPosition`, `SkinDirection`, `SkinNormal` (cofactor) | `shaders/Include/Scene.slang` 168-236; `shaders/Scene/Mesh.vert.slang` 16-75; `Strata/CMakeLists.txt` 186-191 | DG 4496-4499 | 0.3.0 |
| Skinned motion vectors | Previous palettes (`u_PreviousJoints`, t21) for velocity | `Scene.slang` 195-213; `Mesh.vert.slang` 61-82 | | 0.6.0 |
| Visibility report | Extraction collects animators of visible skin proxies (and shadow casters that can reach the view); reported once each, sorted; `StalePoses` stat | `Renderer/SceneRendererExtraction.cpp` 286-309, 1306-1321 | AR 2700-2705 | 0.3.0 / 0.4.0 |
| Unskinned scenes pay nothing | `RenderScene::HasSkinProxies` gates every per-proxy skin check | `RenderScene.h` 290; `SceneRendererExtraction.cpp` 286, 488, 888, 939, 1166 | DG 4499-4501 | 0.3.0 |
| Bind pose for physics | Mesh colliders use the bind pose; entity-ID buffer shows the pose | | DG 4501-4502 | |

### 1.11 Edit-mode poses: `AnimationPreview`

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| Preview provider | An `ISkinningPoses` for scenes that do not play; requests (state, clip, time) per animator; `Status` Waiting/Posed/Failed | `Animation/AnimationPreview.h` 32-233; `AnimationPreview.cpp` | AR 2730-2746 | 0.3.0 (previews), 0.4.0 (rest poses) |
| Same evaluation as play | `EvaluateAnimator` runs an `AnimatorInstance` with `Transitions = false` | `AnimationPreview.cpp` 39-80 | AR 2733-2735 | |
| Rest poses in edit mode | `RestPoses`: every other animator shows `ComputeRestPose`, one per skeleton, recomputed only on reimport (content changes) | `AnimationPreview.h` 32-42, 163-180; `.cpp` 266-405 | AR 2735-2742 | 0.4.0 |
| `ClipStart` edit pose | First frame of what each animator plays on start; keyed by skeleton, controller, clip, root motion | `AnimationEditPose.h` 8-16; `AnimationPreview.cpp` 266-278 | AR 2742-2746 | 0.4.0 |
| Render transforms | Attachments (and meshes under them) drawn at their joints without writing the scene | `AnimationPreview.h` 121-127; `.cpp` 408-502; `RenderScene.cpp` 432-441, 1502-1506 | DG 4502-4505 | 0.4.0 |
| Signal-driven, idle costs nothing | Animators looked at only on component signals; `AnimationPreviewStats` | `AnimationPreview.h` 44-50; `.cpp` 92-140, 280-316 | AR 2735-2742 | 0.4.0 |
| Posed bounds in editor tools | `SceneBounds::GetPosedMeshBounds` for framing, focus, drop-to-ground, placement | `StrataEditor/src/Editor/SceneBounds.*`, `EditorPlacement.*` | AR (end of Previews bullet) | 0.4.0 |

### 1.12 Scripting

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| 12 host functions | `AnimatorPlay` ... `AnimatorGetJointTransform`, appended to the ABI v1 | `StrataScriptCore/include/StrataScript/ScriptABI.h` 509-534; `Strata/src/Strata/Scripting/ScriptHostAPI.cpp` 1970-2130 | DG "Adding a host function"; Roadmap 237 | 0.3.0 |
| SDK `Animator` | `Entity::GetAnimator()`; methods mirror `IAnimatorControl`; `JointTransform` | `StrataScriptCore/include/StrataScript/Animator.h` 17-142 | skill `strata-scripting` 285-318 | 0.3.0 |
| `Script::OnAnimationEvent(name)` | Callback flag, thunk, dispatch from `ScriptSystem` listener to active scripts on the animator entity | `Script.h` 40-42, 93, 298-304, 361, 462-465, 684; `Scripting/ScriptSystem.cpp` 101, 389-407 | skill `strata-scripting` 92 | 0.3.0 |
| Misuse reporting | `RequireAnimation`/`RequireAnimator`/`ControlAnimator` wrap in `HostCall`, report through `ReportProblem` | `ScriptHostAPI.cpp` 1974-2004 | DG "Scripting" | 0.3.0 |

### 1.13 Editor

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| `animation.createController` | Makes a `.stanimator` from JSON sections | `StrataEditor/src/Editor/EditorAnimationCommands.cpp` 150-183 | DG 3703-3709 | 0.3.0 |
| `animation.setController` | Replaces given sections, one undo step (`AssetEdit::SetControllerData`) | same 185-216 | DG 3705-3707 | 0.3.0 |
| `animation.info` | Model, skeleton, clip, controller, or a live animator's state and parameters (Query) | same 218-284 | DG 3707-3709 | 0.3.0 |
| `animation.preview` | Deferred until the request's pose shows; Session kind; refuses while playing | same 286-383 | DG 3709-3716 | 0.3.0 |
| `viewport.setSettings {editPose}` | `rest` / `clipStart` (Scene view camera chip) | `Editor/EditorViewport.cpp` 53, 132-137, 202-212; `EditorViewportCommands.cpp` 137 | DG 3711-3713 | 0.4.0 |
| Preview chip | Viewport names previews, click stops them (`ViewportPanel::DrawPreviewChip`) | `StrataEditor/src/Panels/ViewportPanel*` | DG 3714-3716 | |
| Asset tab views | Skeleton tree, clip channels, controller as editable tables with condition and event text syntaxes | `StrataEditor/src/UI/AnimationAssetViews.h` 16-72, `.cpp` | DG 3716-3720; AR "Editor" bullet | 0.3.0 |
| Inspector live state | State, `from -> to` during fades, normalized time, parameters | `StrataEditor/src/Panels/InspectorPanel.cpp` 1106-1140 | DG 3720-3722 | 0.3.0 |
| Thumbnails | Thumbnail cache makes a rest-pose preview per scene it renders | `Editor/ThumbnailCache.cpp` | AR end of Previews bullet | 0.4.0 |

### 1.14 Tests and perf

- Unit suites: `StrataTests/src/Animation/AnimationAssetTests.cpp` (11 cases), `AnimatorTests.cpp` (9), `AnimationSystemTests.cpp`
  (27, suites `Animation.*`); renderer `Renderer/RenderSceneSkinTests.cpp` (4), `SkinnedMeshTests.cpp` (5); import
  `Asset/GltfSkinImportTests.cpp` (6); scripting `Scripting/ScriptAnimationTests.cpp` (4); editor `Editor/EditorAnimationTests.cpp` (4).
- GPU: `Renderer/GPUAnimationTests.cpp` (7: CPU-skinned reference in forward, entity-ID and shadow passes; limb outside bind bounds;
  blended skinning; shadow casters reporting animators; reach; textured skin streaming; rest poses on both draw paths).
- Perf (budgets `StrataTests/Perf/Budgets.json` 170-172): `Perf.Animation.Evaluate1000` 0.368 ms measured / 0.553 budget,
  `Perf.Animation.CulledAnimators10k` 0.178 / 0.208, `PerfGPU.Renderer.Skinned1000` 0.755 / 0.957 (`Perf/AnimationPerfTests.cpp` 156-240).
- Feature test: `StrataTests/FeatureTest/Scripts/AnimationFeatures.cpp` (Arm rig: controller states Wave/Swing/Rest, events, attachment,
  root motion, root motion through a character controller), `Assets/Animations/Arm.stanimator`, `Assets/Models/Arm.gltf`;
  GPU feature test `GPUFeatureTests.cpp` 212.
- Test helpers: `StrataTests/src/Animation/AnimationTestUtils.h` (arm skeleton, wave/turn/hold clips, locomotion controller),
  `TestSkinningPoses.h`, `SkinnedArmModel.h`, `SkinnedGltf.h`, `SkinnedMeshTestUtils.h`.

### 1.15 The sample

- `Samples/ThirdPerson` (0.5.0, "Sky Islands"): `Assets/Models/Robot/RobotExpressive.glb` (CC0, Quaternius / Don McCurdy);
  `Assets/Animations/Robot.stanimator` (parameters Speed, Grounded, Jump, Wave, Dance; states Idle, Walk, Run, Jump, Wave, Dance;
  Footstep events in Walk and Run; an any-state Jump with `CanTransitionToSelf`; exit times 0.4 from Jump, 0.92 from Wave);
  `Scripts/ThirdPersonPlayer.cpp` 72-133, 231 (sets Speed and Grounded each frame, triggers Wave, Dance, Jump; the character
  controller moves the body, root motion off); `Scripts/Footsteps.cpp` (OnAnimationEvent plays step sounds);
  `Scripts/MenuRobot.cpp` (menu robot alternating Dance and Wave triggers); `Scenes/MainMenu.stscene` (flag in hand through
  `AttachToJoint`); README lines 15, 26, 32 (morph-target faces not imported).
- Other users: `Samples/OpenWorld` (animated foxes with a controller, skill `strata-make-a-game` 502), Showcase Fox (0.5.0 notes 38).

### 1.16 Not in Strata yet (so the book must not imply it)

Blend trees / 1D-2D blend spaces, layers and masks, additive clips, sync markers (Roadmap 1616-1620: the robot's walk and run are
27% of a cycle apart in their cross-fade), IK, ragdolls, curves, clip compression, morph targets, GPU compute skinning
(skinning runs per draw in the vertex shader; Roadmap 675), a node-graph editor, skeleton overlay in the viewport. Wave 8
tranche 2 plans `animation-graph` (Esoterica-based, `.stanimator` version 2); wave 9 plans `animation-tools` and
`animation-runtime-2` (Roadmap 1616-1620, 1648-1660). None of it is in the tree at 822a7a46.

### How completeness was checked

- Every file of `Strata/src/Strata/Animation/` (21 files: 11 headers, 10 sources) is accounted for above.
- Registered components: Skin, Animator, AttachToJoint (`AnimationComponents.cpp` 27-52): all listed.
- Asset types and loaders: Skeleton, AnimationClip, AnimationController (`AnimationRegistration.cpp` 19-31): all listed.
- Scene systems: one, "Animation" (`AnimationRegistration.cpp` 36-41). Scene services: three, all listed with every method.
- Host functions: the 12 of `ScriptABI.h` 518-534, plus the `OnAnimationEvent` callback; SDK `Animator.h` all methods.
- Editor commands: the four `animation.*` registrations (`EditorAnimationCommands.cpp` 153, 187, 218, 286) and the `editPose` viewport setting.
- Shader entries using `ST_SKINNED`: `Strata/CMakeLists.txt` 186, 188, 189, 191 (MeshSkinned, MeshSkinnedVelocity, ShadowMeshSkinned, LocalShadowMeshSkinned).
- No settings section belongs to the module (grep of the folder for settings registrations found none).
- Test case names (list under 1.14) were compared against the feature list; every test maps to a listed feature.

---

## 2. Concepts to teach (dependency order)

1. **What animation must do in a game.** A character's shape must change every frame: a mesh of thousands of vertices
   cannot be stored per frame. Approaches: vertex animation (per-frame vertex positions or textures; used for crowds and
   cloth bakes), morph targets (blend shapes, faces), rigid hierarchies (robot parts), skeletal animation (a few dozen
   joints drive all vertices). Strata: skeletal animation plus rigid parts on joints; no morph targets (importer skips
   them, `GltfImporter.cpp` 1379, 1639). Newcomers think "animation = moving the entity"; it is mostly deforming a mesh
   in place.
2. **Transforms and hierarchies** (prerequisite from the Scene/Math chapters: TRS, matrices, parent-child, local vs world).
   Here: a joint's local `JointPose` TRS, applied scale-rotation-translation (`AnimationTypes.h` 13-22). Newcomers mix up
   the multiplication order and get "rotate about the world origin" instead of "about the joint".
3. **Quaternions for rotation.** Why not Euler angles (gimbal lock, bad interpolation) or matrices (not interpolatable,
   drift). Unit quaternions, double cover (q and -q are the same rotation), normalization. Strata normalizes on create,
   on load and after every blend (`AnimationMath::Normalize`); identity for degenerate input. Newcomer error: blending
   q and -q and getting a 360-degree spin or a zero quaternion.
4. **Interpolation.** Step, linear (lerp, slerp vs nlerp), cubic Hermite with tangents (glTF's cubic spline: tangents
   scaled by the key span). Strata implements exactly glTF's three samplers (`AnimationClip.cpp` 468-536). Newcomer error:
   forgetting to scale tangents by the span; slerping the long way round.
5. **Skeletons.** Joints, parents, topological order, rest pose (vs bind pose!), forward kinematics into model space.
   Approaches: joint arrays sorted parents-first (Strata, Ozz, Esoterica, most engines) vs. scene-node hierarchies
   (joints as entities, as some engines and many beginners do). Strata: array, parents first, validated
   (`Skeleton.cpp` 65-67), FK in one pass (`Skeleton.cpp` 178-187). Why: cache-friendly, no per-joint entities, one pass.
   Newcomer error: assuming any parent index order works; confusing rest pose (skeleton at rest) with bind pose (the
   pose the mesh was modeled in, stored as inverse bind matrices per skin).
6. **Clips and channels.** Keys per joint per path, shared key times, duration, clamping outside keys, binding clips to
   skeletons by name so clips retarget across skeletons with the same names. Approaches: by index (fast, fragile), by
   name (Strata), with retargeting tables (Unreal, Unity humanoid). Strata binds once per (clip, skeleton) and caches.
   Newcomer error: sampling by name every frame; expecting retargeting between differently-proportioned skeletons.
7. **Sampling cost and storage.** Binary search for the key, per-channel data layout. Approaches to size: keyframe
   reduction (Strata, `ReduceKeys` with tolerances justified in comments 44-50), quantization and curve fitting (ACL,
   Ozz, Unreal), uniform sampling with compression. Strata does reduction only; compression is deferred until measured.
8. **Skinning.** Bind pose, inverse bind matrices, palette (joint model x inverse bind), linear blend skinning with four
   weighted influences, normal transformation (cofactor), candy-wrapper artifact and dual-quaternion skinning as the
   alternative not taken. Strata: LBS in the vertex shader, palettes computed on the CPU per proxy, 16-bit weights summing
   to 65535 (`Mesh.h` 28-36), all four palette entries read even with zero weight (so every influence must name a valid
   joint). Newcomer error: forgetting the inverse bind matrix (mesh explodes), using the inverse-transpose wrong for
   normals, culling skinned meshes with their bind-pose bounds (limbs vanish).
9. **Posed bounds and culling of skinned meshes.** Bind bounds are wrong once posed; Strata unions per-joint bind
   boxes transformed by palette entries (exact bound property: a weighted average of points in boxes lies in their
   union's hull) (`RenderScene.cpp` 1322-1339).
10. **State machines for animation.** States, transitions, conditions on parameters, triggers that are consumed,
    exit times, any-state transitions, priority order. Approaches: Unity Mecanim (Strata's model is close to it:
    parameters, Any State, exit time, triggers), Unreal AnimBP state machines inside graphs, Esoterica/Morpheme graphs.
    Strata: flat state machine, one transition per update, any-state first. Newcomer errors: triggers firing twice,
    any-state transitions re-entering their own target every frame (hence `CanTransitionToSelf` default off), exit time
    semantics with loops.
11. **Blending and cross-fades.** Weighted pose blending (lerp T/S, quaternion weighted sum on one hemisphere then
    normalize), cross-fade weight schedules, interrupted fades (Strata keeps up to four entries and their proportions),
    inertialization as the modern alternative (not used). Phase mismatch: walk-to-run without sync markers makes feet
    slide; the Third-Person robot shows it (Roadmap 1619-1620). Newcomer error: blending matrices instead of TRS.
12. **Time, loops and normalized time.** Playhead, speed (negative plays backward), wrap counting, normalized time with
    loops, large time steps (Strata caps events at 4 loops per update and root motion at 64 loops). Newcomer error:
    `fmod` loses loop count, so exit times and events across boundaries fail.
13. **Animation events (notifies).** Named moments in a state's clip; fired when the playhead passes them, including
    across loops and backwards; Strata authors them per controller state (glTF carries none) and dispatches after poses,
    on the main thread, in record order. Approaches: clip-embedded notifies (Unreal), state events (Strata, Mecanim's
    state behaviours partly). Newcomer error: comparing `time == eventTime` (never exact), firing events of fading-out states.
14. **Root motion.** In-place vs root-motion animation; extracting the root joint's horizontal travel and yaw; the pose
    holds the root back; applying the delta to the entity; through a character controller so it collides. Strata:
    `RootTravel::Append` measures per pass in the clip-start frame; `HoldRoot`; `ApplyRootMotion` the single writer.
    Newcomer errors: double motion (root moves in pose and entity), drift at loop boundaries, vertical root motion fights
    gravity (Strata keeps the vertical part in the pose), ignoring entity scale.
15. **Attachments (sockets).** Placing props at joints. Strata: `AttachToJointComponent`, written each update through the
    transform contract; joints themselves never become entities.
16. **Where animation runs in the frame.** After scripts (which set parameters) and before physics (root motion moved
    before the step); per-frame delta, not fixed step; Play mode only. Prerequisites: scene systems and their ordering,
    fixed steps and interpolation (other chapters).
17. **Parallel, deterministic evaluation.** Data-oriented records, job system `ParallelFor`, per-thread scratch, reading
    shared immutable data, writing only own record, applying side effects in a fixed order on the main thread. Why
    determinism matters (replays, tests, multiplayer). Newcomer error: touching the registry or firing events from
    worker threads; ordering results by thread completion.
18. **Asset sharing and lifetime.** Asset sets keyed by handles; requesting every update; holding while used; reloads
    produce new objects (ids), rebinding; failures logged once. Prerequisite: the asset manager chapter.
19. **Animation LOD/culling.** Update-rate or visibility culling (Unity's Culling Mode, Unreal's URO). Strata:
    `WhenVisible` skips evaluation but keeps time, events, transitions and root motion; reach boxes so a frozen pose is
    still found by a view; stale-pose feedback for captures and paused frames. Newcomer error: culling by the stale pose's
    bounds (character never becomes visible again), stopping gameplay-relevant state when unseen.
20. **Decoupling through services.** Renderer and scripts see `ISkinningPoses`, `IAnimatorControl`, `IAnimationEventSource`
    only; layer rules; providers can be swapped (play system vs edit preview), versions are per provider.
21. **Edit-mode posing.** Why a skinned mesh with no animation system lies on the ground (bind pose vs skeleton rest pose,
    Z_UP and Armature nodes); rest poses shared per skeleton; preview requests that change no scene data; render
    transforms for attachments.
22. **Authoring pipeline.** glTF skins, nodes, samplers; which nodes become joints vs entities; sub-asset keys; handles
    stable across reimports; controller documents as JSON and as editor commands.

---

## 3. Code worth showing

| # | File and lines | What it teaches | Reader must know |
| --- | --- | --- | --- |
| 1 | `Strata/src/Strata/Animation/AnimationTypes.h` 15-22 | `JointPose`: TRS as the unit of animation | vectors, quaternions (concept) |
| 2 | `AnimationTypes.h` 43-58 | Slerp with shortest-arc flip and nlerp fallback | quaternion dot, double cover |
| 3 | `AnimationTypes.h` 61-85 | TRS to matrix; affine multiply skipping the fourth row (a micro-optimization with its why) | column-major glm matrices |
| 4 | `Strata/src/Strata/Animation/Skeleton.cpp` 178-187 | Forward kinematics in one pass thanks to parents-first order | 1, 3 |
| 5 | `Skeleton.cpp` 61-75 | Validation: parents before children, finite poses, normalized rotations | 4 |
| 6 | `Skeleton.cpp` 121-161 | Loading untrusted binary safely: magic, version, bounds before allocation, trailing data | BinaryReader (Core) |
| 7 | `Strata/src/Strata/Animation/AnimationClip.cpp` 459-536 | Key search and the three glTF interpolations, Hermite basis with span-scaled tangents | 2, interpolation concept |
| 8 | `AnimationClip.cpp` 438-457 | Binding by name once; recording root-motion channels | skeleton names |
| 9 | `AnimationClip.cpp` 206-222 | Sharing identical key-time arrays (hash then exact compare) | hashing |
| 10 | `AnimationClip.cpp` 231-315 | Keyframe reduction with windowed re-interpolation and cancellation | 7 |
| 11 | `Strata/src/Strata/Animation/AnimationController.cpp` 223-245 | Counting sort that groups transitions by source state (CSR layout) | arrays, prefix sums |
| 12 | `Strata/src/Strata/Animation/AnimatorInstance.cpp` 247-288 | Starting a cross-fade: saved shares, dropping the faintest of 4, renormalizing | weights summing to 1 |
| 13 | `AnimatorInstance.cpp` 587-609 | Weight schedule of a fade and its end | 12 |
| 14 | `AnimatorInstance.cpp` 455-585 (central, long) | Advancing a playhead with loops in both directions, event windows, loop counting, capping work for huge steps | loops, normalized time |
| 15 | `AnimatorInstance.cpp` 725-763 | The state machine: any-state first, exit-time test per loop, conditions, trigger consumption | 11, 14 |
| 16 | `AnimatorInstance.cpp` 766-848 (central) | Evaluating a pose: single clip, blended clips (hemisphere sign trick), FK, root hold | 4, 7, 12 |
| 17 | `AnimatorInstance.cpp` 17-24, 82-97 | Yaw from a quaternion; accumulating root travel in the clip-start frame | trig, quaternions |
| 18 | `AnimatorInstance.cpp` 652-723 | Root motion split at loop crossings, weighted by blend | 14, 17 |
| 19 | `Strata/src/Strata/Animation/AnimationSystem.cpp` 572-716 (central) | The frame of the system: resolve sets, parallel classify/step, main-thread sync, ordered publish, attachments, events | job system, ECS registry |
| 20 | `AnimationSystem.cpp` 739-755 | Culling decision: seen last update, rigid parts, first pose | 19 |
| 21 | `AnimationSystem.cpp` 788-827 | Applying root motion through world and parent inverse; handing it to a character controller | transform contract |
| 22 | `AnimationSystem.cpp` 829-888 | Attachments: local from pose, skip unchanged writes, cycle guard | hierarchy |
| 23 | `AnimationSystem.cpp` 890-917 and 1093-1113 | Re-entrancy-safe event dispatch (snapshot + removed flag) | callbacks |
| 24 | `Strata/src/Strata/Scene/SceneServices.h` 270-376 | The three service interfaces as the module's public contract | interfaces, virtual functions |
| 25 | `Strata/src/Strata/Renderer/RenderScene.cpp` 1322-1339 | Skinning palette and posed bounds | 8 (skinning concept) |
| 26 | `Strata/shaders/Include/Scene.slang` 168-235 | Linear blend skinning on the GPU; normals by cofactor | shader basics |
| 27 | `Strata/shaders/Scene/Mesh.vert.slang` 35-60 | Where skinning sits in the vertex shader before camera-relative transform | 26 |
| 28 | `Strata/src/Strata/Asset/GltfImporter.cpp` 1012-1123 | Building a skeleton from a glTF node tree: marking ancestors, parents-first walk, unique names, root motion joint | glTF node model |
| 29 | `StrataTests/src/Animation/AnimationSystemTests.cpp` 1036-1096 | A determinism test: same bytes with 0, 1, 7 threads | doctest basics |
| 30 | `Samples/ThirdPerson/Scripts/Footsteps.cpp` 1-44 and `ThirdPersonPlayer.cpp` 129-133 | Game side: driving parameters, reacting to events | the scripting chapter |

The JSON form of a controller is best shown from `Samples/ThirdPerson/Assets/Animations/Robot.stanimator` (whole file, 280
lines; excerpt the Jump any-state transition and the Walk state with its Footstep events).

---

## 4. Figures

### Diagrams

1. **Animation data flow, end to end** (data flow): glTF file -> importer -> Skeleton / AnimationClip sub-assets + model
   entities (Animator root, Skin meshes, AttachToJoint parts) -> `.stanimator` authored -> AnimationSystem (asset sets ->
   AnimatorInstance advance/evaluate -> model-space pose) -> `ISkinningPoses` -> RenderScene palettes -> GPU joint buffer
   t15 -> vertex shader LBS. Side branches: root motion -> TransformComponent or ICharacterControl; events ->
   IAnimationEventSource -> ScriptSystem -> `OnAnimationEvent`.
2. **Skeleton memory layout** (memory): parallel arrays names / parents / rest pose with parents-first indices, an example
   tree drawn next to the array, arrows from child to parent index always pointing left.
3. **Spaces of skinning** (geometry): bind space (mesh as modeled) -> inverse bind -> joint space -> joint model transform
   -> animator (model) space -> AnimatorToProxy -> proxy local -> world. Label each matrix of `ComputePalette`.
4. **Clip storage** (memory): channels table (target, path, interpolation, key count, first time, first value) pointing
   into one shared times array and one values array; two channels sharing a times run; cubic spline triplets (in-tangent,
   value, out-tangent).
5. **Interpolation curves** (plot): step, linear, cubic Hermite through the same keys; slerp vs lerp of quaternion arcs.
6. **Controller state machine** (state machine): the Robot controller (Idle, Walk, Run, Jump, Wave, Dance; Any State ->
   Jump; conditions on edges; exit times marked).
7. **Cross-fade weights timeline** (timeline): three fades interrupting each other, stacked areas of up to four entries,
   the faintest dropped at the fifth, weights summing to 1.
8. **Playhead across loops** (timeline): forward and backward advances crossing the loop boundary, the event windows
   `(from, to]`, `Loops` and normalized time values.
9. **Exit time on a looping state** (timeline): normalized time axis 0..3 with exit 0.4 firing at 0.4, 1.4, 2.4.
10. **Root motion extraction** (geometry, top view): root travel within the clip, the entity moved by the delta, the pose
    held back (`HoldRoot`), a loop boundary split into "to end / whole loops / from start".
11. **AnimationSystem frame** (timeline across threads): main thread resolve sets -> ParallelFor classify+step on N
    workers -> main sync queue in record order -> second ParallelFor -> main publish (versions, events queued, root
    motion) -> attachments -> compact -> dispatch. Mark what each phase may read/write.
12. **Frame order of systems** (timeline): Scripting OnUpdate -> Animation -> Physics fixed steps -> render (RenderScene
    Sync reads poses, extraction reports visible animators back).
13. **WhenVisible feedback loop** (data flow): renderer culls with posed bounds + reach -> ReportVisible -> next update
    evaluates -> new pose version; stale-pose return value -> StalePoses -> capture renders again; paused frame path.
14. **Providers of ISkinningPoses** (component diagram): AnimationPreview (edit scene, thumbnails) vs AnimationSystem (play
    copy); RenderScene recomputes all palettes when the provider changes.
15. **Layer diagram** of the module: Animation above Scene; Renderer and Scripting beside it, talking only through Scene
    services; Engine and AssetPipeline above including it.

### Screenshots (all with the Third-Person sample unless noted)

1. The robot in edit mode with `viewport.setSettings {editPose: "rest"}` and with `"clipStart"` side by side
   (`Samples/ThirdPerson`, Course scene).
2. The same robot as it would look without a poses provider (bind pose lying along an axis): reproduce in a test scene
   with the preview's rest poses off is not reachable from the editor UI; use a GPU test capture or describe it (see
   Not determined).
3. `animation.preview {entity: <robot>, state: "Run", time: 0.3}` with the viewport's preview chip visible.
4. The Inspector of the playing robot: Animator component, live State showing `Walk -> Run` during a fade, normalized
   time, parameters.
5. The Asset tab with `Robot.stanimator` open: parameters, states and transitions tables (condition text like
   `Speed > 4.5`).
6. The Asset tab with the robot's Skeleton (joint tree, root motion joint) and a clip (channels list).
7. The menu robot holding the flag (`Scenes/MainMenu.stscene`, `AttachToJoint`), playing.
8. A posed limb outside its bind bounds still drawn and shadowed (reproduce the setup of `GPUAnimationTests.cpp` 192 in a
   scene, or the robot's Wave raising an arm out of the bind box); pair with a bounds overlay if the editor has one.
9. Feature test arm (`StrataTests/FeatureTest`, "Arm Rig") in the entity-ID view showing the preview pose
   (`GPUFeatureTests.cpp` 212), for the "entity-ID buffer shows the pose" point.
10. A cross-fade mid-way (two clips blended) captured at fixed steps with `play.step` for reproducibility.
11. Open World foxes at a distance with `CullingMode WhenVisible` (optional: to illustrate many animators).

Toggle/isolation means for these: component fields (`Animator.Controller`, `ApplyRootMotion`, `CullingMode`),
`animation.preview`, `viewport.setSettings {editPose}`, `play.step` for deterministic frames, `viewport.capture`
(re-renders while `StalePoses` is not 0).

---

## 5. Rules and pitfalls ("why" boxes)

1. **Poses are not entities.** Never create entities per joint or write joint transforms into the scene. Why: a
   character would add dozens of transform changes per frame to the scene's caches, hierarchy, interpolation and
   serialization; 10,000 animators would swamp the scene (DG 2202-2205; AGENTS.md "Animation").
2. **Only scene services cross the module boundary.** The renderer and script host never include Animation; only Engine
   and AssetPipeline do. Why: the module can be left out of a build, and providers can be swapped (edit preview vs play)
   (DG 2206-2207; `Layers.json` 63-68).
3. **Jobs write only their own record; scene changes happen on the main thread in record order.** Why: bit-identical
   results on any thread count (the determinism test), no data races on the registry (DG 2208-2210).
4. **Root motion moves entities only in `AnimationSystem::ApplyRootMotion`, signaled through the transform contract.**
   Why: one writer means one place to make character controllers, parents, scale and interpolation right; an unsignaled
   write leaves stale world-transform caches (DG 2211-2213; AGENTS.md transform contract).
5. **The root's subtree is held back when root motion applies.** Why: otherwise the motion counts twice, mesh ahead of
   entity (`AnimatorInstance.cpp` 826-847).
6. **WhenVisible keeps time, events, transitions and root motion.** Why: gameplay must not depend on the camera (AR
   2703-2705).
7. **Publish a reach with poses that may be skipped.** Why: culling a frozen pose by its own bounds would never see the
   animator again once its clip carried it elsewhere (AR 2706-2711).
8. **Animators that only move rigid parts pose every update.** Why: no skinned mesh means no renderer can report them
   seen (`AnimationSystem.cpp` 744-750).
9. **Every skin influence must name a joint of the skin, even with zero weight.** Why: the shader reads all four palette
   entries; an out-of-range index reads another instance's matrices (DG 4502-4503).
10. **Prepass and forward pass must agree to the bit for skinned meshes.** Why: the forward pass uses an EQUAL depth test;
    both use the `ST_SKINNED` variant (`Mesh.vert.slang` 5-10; DG 4496-4499).
11. **Unskinned scenes pay nothing.** Why: skinning checks run only when `HasSkinProxies()` (DG 4499-4501).
12. **Pose versions belong to their provider.** Why: the play copy's system and the edit preview count independently;
    trusting versions across a provider change shows the wrong pose (`RenderScene.cpp` 1357-1360).
13. **Skins are posed against the animator's drawn transform.** Why: with fixed-step interpolation the entity is drawn
    between steps; posing against the simulated transform snaps the mesh back (DG 4490-4492).
14. **Loaders reject truncated and garbage bytes.** Why: cooked assets and packs are untrusted input; bound every count by
    the remaining bytes before allocating (`AnimationClip.cpp` 357-361).
15. **Joint names are unique and clips bind by name.** Why: binding by name lets clips play across models with the same
    rig; duplicates would make binding ambiguous (the importer renames, `GltfImporter.cpp` 1088-1095).
16. **Skeleton joints are parents-first.** Why: FK in one pass with no recursion and no sorting per frame
    (`Skeleton.cpp` 65-67).
17. **Script commands never block on loading.** Commands and parameters given while a controller loads wait for it.
    Why: assets load asynchronously (exported games), and scripts set parameters in their first frames
    (`AnimatorInstance.cpp` 292-300, 357-387).
18. **Events are dispatched after all poses, outside the jobs, with listener snapshots.** Why: listeners may destroy
    animators or add listeners; doing it mid-evaluation would invalidate records (`AnimationSystem.cpp` 890-917).
19. **Hold `AssetHandle`s, request every update, never block.** The asset sets do this (AGENTS.md "Asset pipeline";
    `AnimationSystem.cpp` 377-500).
20. **Previews change no scene data.** Attachments are drawn through render transforms, never written (DG 4502-4505).
21. **The animation system is Play-only.** A scene that does not play has no system: without a provider skinned meshes
    show the bind pose; the editor installs a preview (AR 2730-2733).
22. **Bump the importer's version when its output changes.** Skeleton, clip or entity layout changes of the glTF importer
    are output changes (AGENTS.md "Importers").
23. **New host functions are appended, never inserted** (the 12 animator functions were appended to ABI v1)
    (AGENTS.md "Scripting").
24. **Pitfall for game makers: triggers stay set until consumed.** A trigger set in a state with no transition testing it
    fires later when one does; reset it (`ResetTrigger`) if that is unwanted (`SceneServices.h` 333-336).
25. **Pitfall: cross-fading walk to run without phase matching slides the feet.** Strata has no sync markers yet
    (Roadmap 1619-1620).

---

## 6. Hands-on

### Engine developers

| # | Task | Difficulty | Proves |
| --- | --- | --- | --- |
| E1 | Write a doctest that builds a 3-joint skeleton by hand (`Skeleton::Create`), computes model transforms and checks the tip's position; then try a child-before-parent order and read the error | Easy | FK, topological order, validation |
| E2 | Sample a clip with each interpolation at chosen times and compare with hand calculation (start from `AnimationAssetTests.cpp` 317) | Easy | interpolation math, Hermite tangents |
| E3 | Corrupt a cooked clip byte by byte and confirm `Deserialize` never crashes (extend the sweep style of `AnimationAssetTests.cpp` 161) | Medium | safe binary loading |
| E4 | Add a `SampleCount` stat to `AnimationSystemStats` counting channels sampled per update; verify with WhenVisible on and off | Medium | the system's frame and culling |
| E5 | Implement an "exit time on non-looping states with conditions" test matrix in `AnimatorTests.cpp` and predict each firing frame before running | Medium | state machine semantics |
| E6 | Prototype sync markers or a phase-matched cross-fade (start the target at the source's normalized phase) inside `AnimatorInstance::StartState`, measure foot sliding on the robot's Walk->Run | Hard | blending, normalized time, why sync markers exist |
| E7 | Replace the quaternion weighted sum in `Evaluate` by iterated slerp and compare results for 3+ entries; argue which is right | Medium | quaternion blending |
| E8 | Add a `Additive` flag to states (design only, or a spike): what reference pose, where in `Evaluate` | Hard | layered animation design |
| E9 | Break determinism on purpose (push events from a job into a shared vector) and watch the determinism test fail | Medium | why jobs write only their record |
| E10 | Write a CPU skinning reference for one vertex and compare with the palette from `RenderScene::ComputePalette` (as `GPUAnimationTests.cpp` 117 does) | Medium | skinning spaces |
| E11 | Add a new `IAnimatorControl` query (e.g. `GetStateDuration`) end to end: service, system, host function appended, SDK, `Scripting.*` test, feature script | Hard | service boundary, ABI rules, feature test rule |

### Game developers

| # | Task | Difficulty | Proves |
| --- | --- | --- | --- |
| G1 | Import a rigged glTF, instantiate it, see it stand in its rest pose; switch the camera chip to clip start; `animation.info` its clips | Easy | the import result and edit poses |
| G2 | Make a two-state controller (Idle, Walk on `Speed > 0.1`) with `animation.createController`, assign it, drive `Speed` from a script | Easy | parameters and transitions |
| G3 | Add Footstep events to Walk and play a sound in `OnAnimationEvent` (copy the sample's `Footsteps.cpp`) | Easy | events |
| G4 | Add a Jump any-state transition on a trigger, with exit-time transitions back; observe in the Inspector's live state | Medium | triggers, any state, exit time |
| G5 | Attach a sword to a hand with `AttachToJoint`; then do it with `GetJointTransform` in a script and compare | Easy | sockets vs per-frame scripting |
| G6 | Turn on `ApplyRootMotion` on a walking clip with and without a `CharacterController`; walk into a wall | Medium | root motion and collision |
| G7 | Spawn 500 characters, measure with `CullingMode` AlwaysAnimate vs WhenVisible (profiler stage `Scene.Animation`) | Medium | animation culling |
| G8 | Modify the Third-Person robot: add a Crouch state on a bool, edit it in the Asset tab tables, undo it | Medium | controller editing workflow |

---

## 7. Glossary

- **Joint (bone):** a node of a skeleton with a transform relative to its parent.
- **Skeleton (rig):** the joints of a model with their parents and rest pose.
- **Topological order (parents first):** joint array order where every parent index is smaller than its children's.
- **Rest pose:** each joint's local transform when nothing plays (the skeleton's default).
- **Bind pose:** the pose in which a mesh was attached to the skeleton; stored as inverse bind matrices.
- **Inverse bind matrix:** takes a vertex from the mesh's bind space into a joint's space.
- **Local / model space (of a pose):** a joint relative to its parent / relative to the animator entity.
- **Forward kinematics (FK):** computing model-space joint transforms by multiplying down the hierarchy.
- **TRS:** translation, rotation, scale, the decomposed form of a transform.
- **Quaternion:** four numbers representing a rotation; q and -q are the same rotation (double cover).
- **Slerp / nlerp:** spherical linear interpolation / normalized linear interpolation of quaternions.
- **Hemisphere (quaternion):** choosing q or -q so blended rotations agree in sign.
- **Clip (animation):** keyframes of joint channels over time.
- **Channel / path:** one animated property (translation, rotation, scale) of one joint.
- **Key / keyframe:** a time and value of a channel.
- **Step, linear, cubic spline:** glTF's interpolation modes.
- **Tangent (in/out):** slope data of a cubic Hermite key.
- **Keyframe reduction:** removing keys that interpolation of their neighbours reproduces.
- **Clip compression:** quantizing or curve-fitting keys to save memory (not in Strata).
- **Binding (clip to skeleton):** the mapping of a clip's channels to a skeleton's joint indices.
- **Retargeting:** playing a clip on a skeleton of other proportions or names (Strata only matches names).
- **Skinning:** deforming mesh vertices by joint transforms.
- **Linear blend skinning (LBS):** a vertex's position is the weighted sum of its influences' transforms applied to it.
- **Dual quaternion skinning:** an alternative that avoids LBS's volume loss (not used).
- **Influence / weight:** a joint affecting a vertex and how much (four per vertex in Strata).
- **Palette (skinning palette):** per skin joint, the matrix joint-model x inverse-bind (with the animator-to-proxy transform).
- **Skin (glTF) / skin binding:** a mesh's set of joints and inverse bind matrices.
- **Posed bounds:** a skinned mesh's bounding box in its current pose.
- **Reach:** the box of where a clip takes the joints, used to cull animators that skip their poses.
- **Animator:** the entity with an `AnimatorComponent`, owner of a pose.
- **Animation controller (state machine):** states, parameters and transitions deciding what an animator plays.
- **State:** a clip with speed, looping and events.
- **Transition:** a rule to move from one state (or any state) to another.
- **Any State:** a transition source meaning "from whatever state".
- **Condition:** a test of a parameter (Greater, Less, True, False, Set).
- **Parameter (float, bool, trigger):** a named value scripts set and conditions test.
- **Trigger:** a bool consumed (reset) by the transition that fires on it.
- **Exit time:** the source state's normalized time a transition waits for.
- **Normalized time:** time over clip duration, counting loops (1.5 = halfway through the second loop).
- **Playhead:** the current time in a clip.
- **Cross-fade:** blending from one state to another over a duration.
- **Blend weight:** a playing entry's share of the pose.
- **Sync markers / phase matching:** aligning cycles of clips during blends (not in Strata).
- **Inertialization:** blending by decaying the difference to the previous pose (not in Strata).
- **Animation event (notify):** a named moment in a state's clip delivered to scripts.
- **Root motion:** motion of the root joint taken out of the pose and applied to the entity.
- **Root motion joint:** the joint whose motion is extracted (topmost joint of a skin on import).
- **Yaw:** rotation about the vertical (+Y) axis.
- **In-place animation:** clips whose root does not travel; the game moves the entity.
- **Attachment (socket):** an object placed at a joint (`AttachToJointComponent`).
- **Culling mode:** whether an animator poses always or only when seen.
- **Stale pose:** a pose older than its animator's time (skipped while unseen).
- **Asset set:** the shared skeleton, controller and clips of animators with the same handles.
- **Record (animator record):** the system's per-animator state.
- **Edit pose:** what skinned characters show in edit mode (rest pose or clip start).
- **Pose preview:** an editor request to show an animator at a state/clip/time without playing.
- **Render transform:** a world transform a poses provider asks renderers to draw an entity at, without changing the scene.
- **Scene service:** an interface a scene system offers to other modules through the scene.
- **Provider (of poses):** the object implementing `ISkinningPoses` for a scene.
- **Sub-asset:** an asset produced from inside another asset file (e.g. a model's skeleton and clips).
- **`.stanimator`:** Strata's controller document (JSON).
- **STSK / STAC:** the cooked binary formats of skeletons and clips.
- **Morph target (blend shape):** per-vertex offsets blended by weights (not imported by Strata).

---

## 8. Proposed chapters (teaching order)

1. **How characters move: the animation problem** (concept, both, S, 1 screenshot). Rigid vs vertex vs morph vs
   skeletal; what Strata chose; the robot as running example. Prereqs: Transforms and hierarchies.
2. **Rotations that interpolate: quaternions, slerp and TRS** (concept, engine, M, 0). Prereqs: vectors and matrices.
3. **Skeletons and forward kinematics** (internals, engine, M, 1: Asset tab skeleton tree). Prereqs: ch 2, assets.
4. **Clips: keys, interpolation, binding and storage** (internals, engine, L, 1: clip view). Covers sampling, reduction,
   shared times, cooked format, safe loading. Prereqs: ch 3, asset loading/binary formats.
5. **Skinning: from pose to vertices** (internals, engine, L, 3: rest pose, posed limb outside bind bounds, entity-ID).
   Palettes, LBS shader, normals, posed bounds, change-driven uploads; boundary with the Rendering part. Prereqs: ch 3,
   shader basics, render scene.
6. **Importing animated models (glTF)** (internals, both, M, 1). Skeleton building, clips, entities, attachments,
   stable handles, import scale. Prereqs: ch 3-5, asset pipeline/importers.
7. **State machines: controllers, parameters and transitions** (concept + internals, both, L, 3: controller tables,
   Inspector live state, state machine diagram). Prereqs: ch 4.
8. **Blending and cross-fades** (internals, engine, M, 1). Weights, four entries, quaternion blending, phase mismatch.
   Prereqs: ch 7, ch 2.
9. **Time, loops and events** (internals, both, M, 0). AdvanceEntry, normalized time, exit times, events. Prereqs: ch 7.
10. **Root motion** (concept + internals, both, M, 1). Extraction, holding the root, applying, character controllers.
    Prereqs: ch 9, physics character controllers, transform contract.
11. **The Animation system: a frame of many animators, in parallel and deterministic** (internals, engine, L, 0).
    Records, asset sets, job phases, ordered publish, attachments, events, services. Prereqs: job system, scene systems,
    scene services.
12. **Animating only what is seen** (internals, engine, M, 1). WhenVisible, reach, feedback, stale poses, paused frames.
    Prereqs: ch 5, 11, culling.
13. **Animation in the editor: previews, edit poses and commands** (internals + tutorial, both, M, 3). AnimationPreview,
    render transforms, `animation.*`, Asset tab, Inspector. Prereqs: ch 7, editor commands.
14. **Tutorial: an animated character from import to footsteps** (tutorial, game, L, 4). G1-G6 on the robot/a new model.
    Prereqs: scripting chapter, ch 1, 7 (conceptual).
15. **Reference: animation components, controller format, script API and commands** (reference, both, M, 0).
    Prereqs: none (lookup).
16. **Exercises and the road ahead: what Strata does not do yet** (concept, engine, S, 0). Sync markers, blend spaces,
    layers, IK, compression, compute skinning, the planned animation graph. Prereqs: ch 8-12.

---

## 9. Not determined

- Not read line by line: `AnimationController.cpp` 248-553 (JSON read/write; only outlined), `AnimationPreview.cpp` 330-540
  and 630-662, `UI/AnimationAssetViews.cpp` (802 lines), `StrataEditor/src/Editor/EditorAnimationCommands.cpp` 1-149
  (describe helpers), the importer's skin binding code (`GltfImporter.cpp` 1144-1360) and `ReadChannel` (1679 ff.),
  `RenderScene.cpp` outside 1270-1440, GPU-driven `Cull.comp` handling of skinned proxies, the perf test bodies, most test
  bodies, `ThumbnailCache.cpp`, `SceneBounds.cpp`, `ViewportPanel::DrawPreviewChip`, `InspectorPanel.cpp` past line 1140.
- Doc drift found: AR 2627 says "GltfImporter (version 9)"; `GltfImporter.h` 39 returns 11. Which later changes bumped it
  (and whether any concern animation) was not traced.
- Observation for the planner: `AnimationSystem.cpp` 42, 53, 64, 983 reach assets through `AssetManager::GetActive()` /
  `AssetManager::GetAssetType` (static), while AGENTS.md says code working for a scene uses `Scene::GetAssetManager()`;
  `AnimationPreview.cpp` 226 does use the scene's. Whether this is an accepted exception or an oversight is not determined.
- Whether the editor shows bounds overlays or a skeleton/bone gizmo in the viewport: none found by grep in
  `StrataEditor/src` (only the Asset tab's skeleton tree); screenshot 8 may need a test capture instead.
- Screenshot 2 (bind pose without provider) cannot be produced through normal editor use (the editor always installs a
  rest-pose preview); possible only from a test or a custom tool. Not verified.
- Exact release of each WhenVisible refinement (reach versioning, rigid-part posing, stale poses) beyond what the Roadmap
  review round at lines 320-330 and 0.4.0 notes say; the reach cache (`ReachVersion`, `ReachUpdates`) may be later than 0.4.0.
- How skinned proxies go through the GPU-driven path (`Cull.comp`, indirect draws) is the Rendering area's; only the
  boundary was read.
- The Open World sample's fox setup and the Showcase Fox were not opened.
- Wave 8 status of `animation-graph` (tranche 2): no code in the tree at 822a7a46; whether it has started on another
  branch is not determined (worktrees were not read, by rule).
