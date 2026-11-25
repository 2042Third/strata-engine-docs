---
id: reference/scene
title: "Scene, reflection and settings: types, flags, formats, limits"
description: "The Scene and Entity API, the flags of reflection, the settings field types, the limits and the file formats of scenes, prefabs, cooked scenes and projects."
kind: reference
size: M
tracks: []
needs: [basics/programming-3]
status: final
---

This page holds the facts of three things that every Strata program uses: the scene that holds entities, the reflection that describes their components, and the settings that describe a project. Use it when you meet a name in code, a flag in a component's registration or a number in an error message, and want the exact meaning. Each table has a short introduction that names the page teaching its subject, and a note after a table says what it omits.

Read a declaration as C++ writes it: the type that a function returns comes first, then its name, then the parameters between round brackets. A `const` after the round brackets promises that the call changes nothing in the scene. A name that starts with `c_` is a constant, and a name that starts with `m_` is a private member, which a caller never uses. A value of an enum that carries a bit, such as `ST_BIT(2)`, is a flag: you combine flags with `|` and test them with `&`, so one number holds several of them. [Classes and references](../basics/programming-3.md) teaches the C++ that these declarations use.

## The Scene API

A **scene** here means the `Scene` class: the world of entities that owns the EnTT registry (the table of components), the hierarchy and, while the game plays, the systems that run. Every `Scene` function must run on the main thread. [Entities and components](../world/ecs.md) teaches what an entity is, [The scene graph](../world/scene-graph.md) teaches the hierarchy and the transform contract, and [Systems](../world/systems.md) teaches the phases. The groups below follow the header `Strata/src/Strata/Scene/Scene.h`; the meaning column repeats the comment of each member.

The table is written by hand from the header in this version, in the order of its groups. Private members and the members of `SceneSettings` are not listed.

### Entities

Creating and destroying entities. A prototype (`EntityPrototype`) is a ready-made list of entities and their components, compiled from a prefab, a model or a scene document, which `Instantiate` and its two steps copy into the scene. A scene holds at most `Scene::c_MaxEntities` live entities (see the limits below); past it, creation logs an error and returns an invalid `Entity`.

| Member | Declaration | Meaning |
| --- | --- | --- |
| `Scene::c_MaxEntities` | `static constexpr size_t c_MaxEntities` | Most live entities of one registry |
| `Scene::CreateEntity` | `Entity CreateEntity(const std::string& name = std::string())` | Creates an entity with a new identifier at the top level |
| `Scene::CreateEntityWithUUID` | `Entity CreateEntityWithUUID(UUID uuid, const std::string& name = std::string())` | Creates one with the identifier you give, as a loader does |
| `Scene::CreateChildEntity` | `Entity CreateChildEntity(Entity parent, const std::string& name = std::string())` | Creates an entity below a parent |
| `Scene::DestroyEntity` | `void DestroyEntity(Entity entity)` | Destroys the entity and its descendants; while the scene updates, the end of the frame does it |
| `Scene::DestroyEntities` | `void DestroyEntities(std::span<const Entity> entities)` | Destroys many subtrees in one pass, so removing many siblings stays linear |
| `Scene::IsPendingDestroy` | `bool IsPendingDestroy(Entity entity) const` | True while a destruction waits for the end of the update |
| `Scene::GetPendingDestroys` | `const std::vector<UUID>& GetPendingDestroys() const` | The entities whose destruction waits |
| `Scene::DuplicateEntity` | `Entity DuplicateEntity(Entity entity)` | Deep copy with fresh identifiers, inserted after the original; references inside the copy point at the copies |
| `Scene::Copy` | `static Ref<Scene> Copy(const Ref<Scene>& source)` | Deep copy that keeps every identifier; play mode runs on such a copy |
| `Scene::Copy` | `static Ref<Scene> Copy(const Ref<Scene>& source, const SceneCopyOptions& options)` | The same with options; `SerializedOnly` makes the snapshot of a background save, which is read, never played |
| `Scene::RegisterContextCopier` | `static bool RegisterContextCopier(SceneContextCopier copier)` | Lets a module copy the data it keeps for a scene into each copy |
| `Scene::ReleaseInBackground` | `static void ReleaseInBackground(Ref<Scene> scene)` | Stops a scene on the main thread and destroys its entities on a background job |
| `Scene::BeginInstantiation` | `bool BeginInstantiation(const Ref<EntityPrototype>& prototype, const InstantiationOptions& options, PrototypeInstantiation& outInstantiation, std::string* outError = nullptr)` | Checks a prototype and gives its entities their identifiers; fails without creating anything |
| `Scene::ContinueInstantiation` | `size_t ContinueInstantiation(PrototypeInstantiation& instantiation, size_t maxEntities, std::string* outError = nullptr, const TransformComponent* rootTransform = nullptr)` | Creates the next entities of a prototype, at most `maxEntities` |
| `Scene::Instantiate` | `std::vector<Entity> Instantiate(const Ref<EntityPrototype>& prototype, const InstantiationOptions& options, std::string* outError = nullptr)` | Both steps in one call: all top-level entities, or none and an error |
| `Scene::GetEntityCount` | `size_t GetEntityCount() const` | Entities of the scene |
| `Scene::GetRegistryEntityCount` | `size_t GetRegistryEntityCount() const` | Live entities of the registry, also those made directly through `GetRegistry()` |
| `Scene::EstimateMemoryUsage` | `uint64_t EstimateMemoryUsage() const` | About the memory the entities take; costs a pass, so not for every frame |

### Lookups

Finding an entity, and reaching the registry. The name and tag lookups use an index built on the first call and kept current by the components' signals.

| Member | Declaration | Meaning |
| --- | --- | --- |
| `Scene::GetEntityByUUID` | `Entity GetEntityByUUID(UUID uuid) const` | The entity, or an invalid one when none has that identifier |
| `Scene::FindEntityByName` | `Entity FindEntityByName(std::string_view name) const` | The first entity in hierarchy order with the name |
| `Scene::FindEntitiesByTag` | `std::vector<Entity> FindEntitiesByTag(std::string_view tag) const` | Every entity with the tag, in hierarchy order |
| `Scene::HasChildNamed` | `bool HasChildNamed(Entity parent, std::string_view name, Entity except) const` | Whether another child of the parent has the name |
| `Scene::GetPrimaryCameraEntity` | `Entity GetPrimaryCameraEntity()` | The first active entity whose camera is the primary one |
| `Scene::GetRegistry` | `entt::registry& GetRegistry()` | The EnTT registry; writes to it follow the transform contract |
| `Scene::GetAllEntitiesWith` | `auto GetAllEntitiesWith()` | A registry view of the entities that have the listed components |

### Hierarchy

The hierarchy is a tree of entities in hierarchy order: parents before children, siblings in their list order. Changes go through these functions, never through the relationship components.

| Member | Declaration | Meaning |
| --- | --- | --- |
| `Scene::GetRootEntities` | `const std::vector<UUID>& GetRootEntities() const` | The top-level entities in order |
| `Scene::GetHierarchyVersion` | `uint64_t GetHierarchyVersion() const` | Changes whenever the order may have changed, so results can be cached |
| `Scene::GetHierarchyMoves` | `bool GetHierarchyMoves(uint64_t sinceVersion, std::vector<entt::entity>& outEntities) const` | The entities that moved since a version; false when the log no longer reaches that far |
| `Scene::GetEntitiesInHierarchyOrder` | `std::vector<Entity> GetEntitiesInHierarchyOrder() const` | Every entity, depth first, computed once per version |
| `Scene::SetParent` | `bool SetParent(Entity child, Entity parent, bool keepWorldTransform = true)` | Re-parents; false when it would make a cycle |
| `Scene::SetSiblingIndex` | `bool SetSiblingIndex(Entity entity, size_t index)` | Moves an entity among its siblings |
| `Scene::GetSiblingIndex` | `size_t GetSiblingIndex(Entity entity) const` | Its position among its siblings |
| `Scene::PlaceEntities` | `bool PlaceEntities(std::span<const EntityPlacement> placements)` | Moves many entities at once; world transforms are not kept |
| `Scene::IsDescendantOf` | `bool IsDescendantOf(Entity entity, Entity ancestor) const` | Whether the ancestor lies above the entity |
| `Scene::CountSubtree` | `size_t CountSubtree(Entity entity) const` | The entity and its descendants; linear in the subtree |
| `Scene::CompareHierarchyOrder` | `int CompareHierarchyOrder(Entity a, Entity b) const` | Negative when a comes first, positive when b does, 0 for the same entity |
| `Scene::GetDepth` | `uint32_t GetDepth(Entity entity) const` | Depth in the tree; roots have 0 |
| `Scene::c_MaxHierarchyMoves` | `static constexpr size_t c_MaxHierarchyMoves` | Moves the log remembers (see the limits) |

### Transforms

The scene caches world transforms and computes again only the subtrees below entities whose transform changed. Code that writes a transform field must signal it: that rule is the transform contract. A fixed step is a slice of simulation time of constant length. A drawn transform is where a renderer draws an entity: while the scene interpolates, the point between the poses of the last two fixed steps. [Interpolation](../world/interpolation.md) teaches it.

| Member | Declaration | Meaning |
| --- | --- | --- |
| `Scene::UpdateWorldTransforms` | `void UpdateWorldTransforms()` | Brings the cached world matrices up to date; returns at once without changes |
| `Scene::GetWorldTransform` | `glm::mat4 GetWorldTransform(Entity entity) const` | The world matrix right now, cached or computed |
| `Scene::FindCurrentWorldTransform` | `const glm::mat4* FindCurrentWorldTransform(entt::entity handle) const` | The cached matrix if current, else null; safe for worker threads that only read |
| `Scene::SetWorldTransform` | `bool SetWorldTransform(Entity entity, const glm::mat4& worldTransform)` | Sets the local transform so that the world one matches; false when no local transform can |
| `Scene::MarkTransformChanged` | `void MarkTransformChanged(Entity entity)` | Records a write without the update signal, as physics does when it writes poses back |
| `Scene::MarkTransformsChanged` | `void MarkTransformsChanged(std::span<const entt::entity> entities)` | The same for many entities |
| `Scene::InvalidateAllTransforms` | `void InvalidateAllTransforms()` | Marks every world transform stale |
| `Scene::IsActiveInHierarchy` | `bool IsActiveInHierarchy(Entity entity) const` | Constant time, never stale |
| `Scene::GetTransformsVersion` | `uint64_t GetTransformsVersion() const` | Changes whenever a cached world transform changes |
| `Scene::GetWorldTransformChanges` | `bool GetWorldTransformChanges(uint64_t sinceVersion, std::vector<entt::entity>& outEntities) const` | The entities that changed since a version; false past the log (see the limits) |
| `Scene::ValidateWorldTransforms` | `bool ValidateWorldTransforms(std::string* outError = nullptr) const` | Compares every cache with a full pass over the hierarchy |
| `Scene::ValidateHierarchy` | `bool ValidateHierarchy(std::string* outError = nullptr) const` | Checks links, depths, indexes and the sub-scene membership |
| `Scene::SetInterpolation` | `void SetInterpolation(bool enabled)` | The program's switch for drawing between fixed steps; off by default |
| `Scene::IsInterpolating` | `bool IsInterpolating() const` | In effect: the switch, the project's setting and a running scene |
| `Scene::GetStepAlpha` | `float GetStepAlpha() const` | How far between the two poses this frame draws, from 0 to 1 |
| `Scene::GetDrawnTransform` | `glm::mat4 GetDrawnTransform(Entity entity) const` | Where the entity is drawn this frame |
| `Scene::FindDrawnTransform` | `const glm::mat4* FindDrawnTransform(entt::entity handle) const` | The drawn matrix of an entity of the interpolated set, else null |
| `Scene::UpdateDrawnTransforms` | `void UpdateDrawnTransforms()` | Brings world and drawn matrices up to date |
| `Scene::BreakInterpolation` | `void BreakInterpolation(Entity entity)` | Draws the entity where it is: a teleport |

### Systems and services

A system is code that the scene runs every frame while it plays; a service is an interface that one system offers so that other code never includes its module. [Systems](../world/systems.md) teaches both. The six built-in systems are in the table after this one.

| Member | Declaration | Meaning |
| --- | --- | --- |
| `Scene::GetSystem` | `T* GetSystem() const` | The running system of exactly class T, or null |
| `Scene::GetRunningSceneCount` | `static uint32_t GetRunningSceneCount()` | Scenes between start and stop in this process |
| `Scene::RegisterService` | `bool RegisterService(T& service)` | A system offers interface T; a second provider logs an error and returns false |
| `Scene::UnregisterService` | `void UnregisterService(T& service)` | Withdraws it |
| `Scene::GetService` | `T* GetService() const` | The provider of interface T, or null |
| `Scene::SetPreparedState` | `T& SetPreparedState(Scope<T> state)` | Keeps what a system prepared for a loaded scene |
| `Scene::GetPreparedState` | `T* GetPreparedState() const` | Reads it without taking it |
| `Scene::TakePreparedState` | `Scope<T> TakePreparedState()` | Takes it when the scene starts |
| `Scene::GetAssetManager` | `AssetManagerBase* GetAssetManager() const` | The manager the scene's assets come from, or null; code that works for a scene goes through it |

### The runtime and time

The scene runs in a mode (play or simulate) between `OnRuntimeStart` and `OnRuntimeStop`. Simulate mode is the editor's physics run: of the built-in systems, only `Physics` and `World` run in it. [Time](../core/time.md) and [Systems](../world/systems.md) teach the loop.

| Member | Declaration | Meaning |
| --- | --- | --- |
| `Scene::OnRuntimeStart` | `void OnRuntimeStart(SceneRuntimeMode mode = SceneRuntimeMode::Play)` | Starts the run |
| `Scene::OnRuntimeStop` | `void OnRuntimeStop()` | Stops it; drops steps that did not run |
| `Scene::OnUpdateRuntime` | `void OnUpdateRuntime(Timestep timestep, SceneWorkBudget* budget = nullptr)` | One frame of a running scene |
| `Scene::OnUpdateEditor` | `void OnUpdateEditor(Timestep timestep, SceneWorkBudget* budget = nullptr)` | One frame of an edited scene |
| `Scene::IsRunning` | `bool IsRunning() const` | Between start and stop |
| `Scene::GetRuntimeMode` | `SceneRuntimeMode GetRuntimeMode() const` | Play or simulate |
| `Scene::IsUpdating` | `bool IsUpdating() const` | During an update, when destruction is deferred |
| `Scene::SetPaused` | `void SetPaused(bool paused)` | Stops the running systems and tells them; starting resets it |
| `Scene::Step` | `void Step(uint32_t frames = 1)` | While paused, lets the next updates each run exactly one fixed step |
| `Scene::GetStepFrames` | `uint32_t GetStepFrames() const` | Steps asked for that have not run |
| `Scene::GetFixedStepCount` | `uint64_t GetFixedStepCount() const` | Fixed steps since the start: the game's own time base |
| `Scene::GetFixedTimestep` | `float GetFixedTimestep() const` | Seconds of one step: the project's rate when it sets one |
| `Scene::GetMaxFixedSteps` | `uint32_t GetMaxFixedSteps() const` | Most steps one update runs before it drops the backlog |
| `Scene::GetProjectFixedRate` | `uint32_t GetProjectFixedRate() const` | Steps per second the project imposes; 0 means the scene's own |
| `Scene::GetTime` | `double GetTime() const` | Simulation seconds since the start |
| `Scene::GetFrameIndex` | `uint64_t GetFrameIndex() const` | Runtime updates since the start |
| `Scene::GetTimeScale` | `float GetTimeScale() const` | The factor that slows or stops game time |
| `Scene::SetTimeScale` | `void SetTimeScale(float timeScale)` | Sets it; negative values become 0 |
| `Scene::GetUnscaledDeltaTime` | `float GetUnscaledDeltaTime() const` | The latest timestep before the time scale |
| `Scene::GetUnscaledTime` | `double GetUnscaledTime() const` | Their sum since the start |
| `Scene::SetTimeDilation` | `void SetTimeDilation(bool enabled)` | A run that falls behind real time slows instead of catching up |
| `Scene::IsTimeDilated` | `bool IsTimeDilated() const` | Whether it is on |
| `Scene::GetDroppedFixedStepCount` | `uint64_t GetDroppedFixedStepCount() const` | Steps whose time was dropped |
| `Scene::GetSettings` | `SceneSettings& GetSettings()` | Gravity, the fixed step and the per-frame loading counts; read the step through `GetFixedTimestep` |
| `Scene::GetName` | `const std::string& GetName() const` | The scene's name |
| `Scene::GetSourceAsset` | `AssetHandle GetSourceAsset() const` | The scene asset it came from, or null; copies keep it |
| `Scene::GetLineageID` | `UUID GetLineageID() const` | Recognizes a scene from one play session to the next |
| `Scene::GetPhysicsLayers` | `PhysicsLayerSettings& GetPhysicsLayers()` | The working copy of the project's collision layers; not saved |
| `Scene::ApplyProjectLayers` | `bool ApplyProjectLayers()` | Makes the project's table the working copy |
| `Scene::ApplyProjectTiming` | `bool ApplyProjectTiming()` | Takes the project's fixed rate and interpolation |

### Sub-scenes

A sub-scene is a scene loaded into another one, next to what it holds. [Sub-scenes](../world/sub-scenes.md) teaches loading and unloading. Loading work shares one budget per frame: the counts in `SceneSettings` and `Scene::c_MaxSubSceneMillisecondsPerFrame`.

| Member | Declaration | Meaning |
| --- | --- | --- |
| `Scene::LoadSubScene` | `SubSceneID LoadSubScene(AssetHandle scene, const SubSceneOptions& options = {}, std::string* outError = nullptr)` | Starts loading a scene asset into this scene; 0 and an error when no load can start |
| `Scene::BeginAdditiveLoad` | `SubSceneID BeginAdditiveLoad(Ref<Scene> prepared, std::string* outError = nullptr)` | Adds the entities of a prepared scene without loading |
| `Scene::UnloadSubScene` | `bool UnloadSubScene(SubSceneID id)` | Makes its roots inactive at once and destroys the rest in slices |
| `Scene::FlushSubSceneUnloads` | `void FlushSubSceneUnloads()` | Finishes the unloads now, for tools and tests |
| `Scene::IsSubSceneLoaded` | `bool IsSubSceneLoaded(SubSceneID id) const` | Whether every entity exists |
| `Scene::GetSubSceneStatus` | `const SubSceneStatus* GetSubSceneStatus(SubSceneID id) const` | The state, or null for an unknown identifier |
| `Scene::GetSubScenes` | `std::vector<SubSceneStatus> GetSubScenes() const` | Every sub-scene not yet unloaded, in load order |
| `Scene::GetSubSceneRoots` | `std::vector<Entity> GetSubSceneRoots(SubSceneID id) const` | Its top-level entities |
| `Scene::AdoptSubScene` | `SubSceneID AdoptSubScene(AssetHandle source, std::span<const Entity> roots, std::string* outError = nullptr)` | Registers existing top-level entities as a loaded sub-scene |
| `Scene::SetSubSceneOf` | `bool SetSubSceneOf(Entity root, SubSceneID id)` | Moves a top-level entity into a sub-scene, or out with 0 |
| `Scene::GetSubSceneOf` | `SubSceneID GetSubSceneOf(Entity entity) const` | The sub-scene of its top-level ancestor, 0 for none |
| `Scene::GetSubSceneMembershipVersion` | `uint64_t GetSubSceneMembershipVersion() const` | Changes when a top-level entity joins or leaves one |
| `Scene::FindSubSceneBySource` | `SubSceneID FindSubSceneBySource(AssetHandle source) const` | The latest sub-scene loaded from an asset |
| `Scene::HasPendingSubScenes` | `bool HasPendingSubScenes() const` | Whether one still loads, creates or unloads |
| `Scene::UpdateSubScenes` | `void UpdateSubScenes(SceneWorkBudget& budget)` | Advances loads and unloads within the frame's budget; the editor and runtime updates call it first |

### Requests to the scene's owner

Gameplay code asks whoever runs the scene (the runtime or the editor's play mode) to end the game or switch scenes. The owner honors the request after the update in which it was made; quitting wins over a scene load, and a later request replaces an earlier one.

| Member | Declaration | Meaning |
| --- | --- | --- |
| `Scene::RequestQuit` | `void RequestQuit(int32_t exitCode)` | Asks to end the game with an exit code |
| `Scene::GetQuitRequest` | `std::optional<int32_t> GetQuitRequest() const` | The pending quit request |
| `Scene::RequestSceneLoad` | `void RequestSceneLoad(UUID sceneAsset)` | Asks for another scene; the null handle restarts this one |
| `Scene::GetSceneLoadRequest` | `std::optional<UUID> GetSceneLoadRequest() const` | The pending request |
| `Scene::TakeSceneLoadRequest` | `std::optional<UUID> TakeSceneLoadRequest()` | Reads and clears it, so an owner that cannot load does not try again every frame |
| `Scene::SetSceneLoadProgress` | `void SetSceneLoadProgress(std::optional<float> progress)` | The owner reports its progress from 0 to 1 |
| `Scene::GetSceneLoadProgress` | `std::optional<float> GetSceneLoadProgress() const` | Nothing while no such load runs |

## The Entity API

An `Entity` is a small handle: an EnTT entity and the scene that holds it. You copy it freely, and it owns nothing. The handle of a destroyed entity answers false from `IsValid()`. Every component function lives here and forwards to the registry.

The table is written by hand from `Strata/src/Strata/Scene/Entity.h`. A tag component is an empty :term[struct]{id=struct} with no data: use `HasComponent` and `AddComponent` with it, never `GetComponent`, which a `static_assert` refuses.

| Member | Declaration | Meaning |
| --- | --- | --- |
| `Entity::AddComponent` | `decltype(auto) AddComponent(Args&&... args)` | Adds a component and returns it; asserts when the entity has it |
| `Entity::AddOrReplaceComponent` | `decltype(auto) AddOrReplaceComponent(Args&&... args)` | Adds it, or replaces the old value |
| `Entity::GetComponent` | `T& GetComponent()` | The component; asserts when absent, and refuses tag components |
| `Entity::TryGetComponent` | `T* TryGetComponent()` | The component, or null when absent or the entity invalid |
| `Entity::HasComponent` | `bool HasComponent() const` | True only for a valid entity that has T |
| `Entity::HasAnyComponent` | `bool HasAnyComponent() const` | True when it has at least one of the listed types |
| `Entity::RemoveComponent` | `void RemoveComponent()` | Removes it; asserts when absent |
| `Entity::MarkModified` | `void MarkModified()` | Tells the systems, through the on_update signal, that a component changed in place |
| `Entity::GetUUID` | `UUID GetUUID() const` | The identifier from the entity's identity component |
| `Entity::GetName` | `const std::string& GetName() const` | Its name |
| `Entity::GetTransform` | `TransformComponent& GetTransform()` | The local transform; a write needs `MarkModified<TransformComponent>()` after it |
| `Entity::GetParent` | `Entity GetParent() const` | Its parent, or an invalid entity |
| `Entity::GetChildren` | `std::vector<Entity> GetChildren() const` | Its children in order |
| `Entity::IsActive` | `bool IsActive() const` | False when the entity itself has the inactive component |
| `Entity::SetActive` | `void SetActive(bool active)` | Adds or removes it |
| `Entity::IsValid` | `bool IsValid() const` | Whether the scene still holds the entity |
| `Entity::GetHandle` | `entt::entity GetHandle() const` | The EnTT identifier |
| `Entity::GetScene` | `Scene* GetScene() const` | The scene |

Two entities are equal when both the EnTT identifier and the scene agree.

## The systems the engine registers

A system descriptor says when a system runs and in which order. `Hard` constraints name systems that must exist, and `soft` constraints apply only when the named system is part of the build, so the engine runs without that module. The table is written by hand from the six registrations (`ScriptingRegistration.cpp`, `AnimationRegistration.cpp`, `PhysicsRegistration.cpp`, `WorldRegistration.cpp`, `AudioRegistration.cpp`, `GameUIRegistration.cpp`) and from `Strata/src/Strata/Scene/SceneSystem.h`. [Systems](../world/systems.md) teaches why the order is what it is. Registration order decides what no constraint settles.

| System | Runs in simulate mode | Runs after (soft) | Runs before (soft) | Profile stage | Prepares loaded scenes |
| --- | --- | --- | --- | --- | --- |
| `Scripting` | No | None | None | `Scene.Scripts` | No |
| `UI` | No | None | `Scripting` | `Scene.UI` | No |
| `Animation` | No | `Scripting` | `Physics` | `Scene.Animation` | No |
| `World` | Yes | `Scripting` | `Physics`, `Audio` | `World.Streaming` | Yes |
| `Physics` | Yes | `Scripting` | None | `Scene.Physics` | Yes |
| `Audio` | No | `Scripting`, `Animation`, `Physics` | None | `Scene.Audio` | No |

A system takes part only in the per-frame phases whose callbacks its class overrides: update, fixed update, late update and paused update. No built-in system sets a hard constraint.

## Reflection: flags and types

Reflection is the description of each component and property that one registration gives, and that the file writer, the inspector, the automation commands, undo and script access all read. [Reflection](../world/reflection.md) teaches why. The enums below are in `Strata/src/Strata/Reflection/ComponentRegistry.h` and `Strata/src/Strata/Reflection/Property.h`. [Components](../reference/components.md) lists every registered component and property with these values completed.

A flag enum is a set of bits, each named. The table of values is written by hand from the two headers, one row per value with the header's comment.

### `ComponentFlags`

The flags of a component type. `None` is 0.

| Value | Bit | Meaning |
| --- | --- | --- |
| `Hidden` | 0 | Internal: not shown in the inspector or the add-component menus |
| `NotRemovable` | 1 | Present on every entity, for example the transform |
| `NoCopy` | 2 | Not copied when the scene is copied to enter play mode |
| `NoSerialize` | 3 | Not written as a component: the scene writer stores it itself, for example the identifier and the parent |
| `EngineAdded` | 4 | Added only by the engine, for example prefab links: visible, and a user can remove it, but never added by users or tools |

### `PropertyType`

The type of a property. Every authored component field is described by one of these values.

| Value | Stored as | Meaning |
| --- | --- | --- |
| `Bool` | `bool` | A true or false value |
| `Int` | `int32_t` | A whole number |
| `UInt` | `uint32_t` | A whole number from 0 |
| `Float` | `float` | A real number |
| `Vec2` | `glm::vec2` | Two floats |
| `Vec3` | `glm::vec3` | Three floats |
| `Vec4` | `glm::vec4` | Four floats |
| `Quat` | `glm::quat` | A rotation; edited as Euler angles in degrees |
| `Color3` | `glm::vec3` | Linear red, green and blue |
| `Color4` | `glm::vec4` | Linear red, green, blue and alpha |
| `String` | `std::string` | Text |
| `Enum` | `int32_t` | A value with named options |
| `Asset` | `UUID` | An asset handle |
| `Entity` | `UUID` | A reference to an entity by identifier |

### `PropertyFlags`

The flags of one property. `None` is 0.

| Value | Bit | Meaning |
| --- | --- | --- |
| `ReadOnly` | 0 | Visible, but you cannot change it through the inspector, automation or scripts |
| `Hidden` | 1 | Not shown in the inspector, still written to files |
| `Transient` | 2 | Not written to files: runtime state |
| `MultiLine` | 3 | A string edited in a multi-line text box |
| `Slider` | 4 | A number edited with a slider between its minimum and maximum |
| `PowerOfTwoLimit` | 5 | An unsigned limit chosen among the powers of two up to the maximum, where 0 means no limit |
| `PhysicsLayer` | 6 | An unsigned index of a physics layer, chosen by its name from the project's collision layers |

## Settings: field types and scopes

A settings section is a named group of project or user values that the engine validates, describes and stores. Its identifier has the form `<Module>.<Name>`, such as `Scene.CollisionLayers`. [Projects and settings](../world/projects-settings.md) teaches sections, validation and versions, and [Settings](../reference/settings.md) lists every section and field. The enums below are in `Strata/src/Strata/Core/SettingsRegistry.h`; the tables are written by hand from it.

A simple section lists its fields and the registry validates a value against them. Each field has one of these types:

| `SettingsFieldType` | Meaning | Limits the field states |
| --- | --- | --- |
| `Bool` | True or false | None |
| `Int` | A whole number | `Min` to `Max`, inclusive |
| `Float` | A number | `Min` to `Max`, inclusive; `DragSpeed` sets the step of a drag |
| `String` | UTF-8 text | At most `MaxLength` bytes |
| `Enum` | One of the listed options | The names in `Options` |
| `Asset` | An asset handle, 16 hexadecimal digits, or null for none | The asset type named in `AssetType` |

A section lives in one of two places:

| `SettingsScope` | Where the value is kept |
| --- | --- |
| `Project` | In the project file, and in the manifest of the games it exports |
| `User` | In the user's preferences file, which is the editor's |

Validation checks a value in this order. First its size against `SettingsSection::c_MaxValueBytes`, in compact JSON. Then its version, from 1 to the section's `Version`, where a newer one is refused. Last the fields or the section's own `Read` function.

A section identifier is two names, each of letters and digits from the English alphabet that start with an upper-case letter. The whole identifier has at most `SettingsRegistry::c_MaxIdSize` bytes.

## Limits

A limit is a number that the engine checks and refuses to exceed. The generated table below lists the constants of scenes and worlds that a tool reads from the source: the value, the expression the source writes it with, the comment and where it is declared. A reader who meets a count in an error message finds the constant here. Rows for physics capacities and world sizes belong to [Physics reference](../reference/physics.md) and to the worlds reference; they stay in this table because one tool makes it.

The unit of a size is the byte, and a KiB is 1,024 bytes. [Bytes](../basics/bytes.md) teaches the units.

::include{file="limits.md"}

The next table holds the limits of files and settings that the generated one lacks. It is written by hand from the declarations named in its last column. The 512 KiB cap on a section's value is in the generated table: it is a member of `SettingsSection`, not of `SettingsRegistry`.

| Constant | Value | What it bounds | Checked in |
| --- | --- | --- | --- |
| `SettingsRegistry::c_MaxIdSize` | 64 bytes | A section identifier, in all | `SettingsRegistry::IsValidSectionId` |
| `Project::c_MaxFileBytes` | 1 MiB | A project file, read or written | `Project::Load` and `Project::Save` |
| `Project::c_MaxScriptModuleNameSize` | 64 | A script module name | `Project::IsValidScriptModuleName` |
| `c_MaxBinaryStringBytes` | 1 MiB | A string in a binary property value | `PropertyBinary.cpp`, both directions |
| `CookedSceneFormat::c_MaxBlobBytes` | 16 MiB | One block of MessagePack bytes (a compact binary form of JSON) of an unknown component or a JSON extra | `CookedScene.cpp`, both directions |

Three facts that the constants imply. A cooked scene also refuses a header that declares more than `Scene::c_MaxEntities` entities. The sub-scene time limit is a ceiling for one update, not a promise, and each update also stops at its entity counts. The transform log forgets all but the latest `Scene::c_MaxTransformChanges` changes, so `GetWorldTransformChanges` answers false for a version older than that and the caller rebuilds its cache whole.

## File formats

A document is a file that a loader reads. A scene, a prefab and a model share one text layout; a cooked scene is the same content as bytes; a project file is a smaller JSON document. This table is written by hand from the headers and sources named in it. Every JSON document begins with a header, `{"Strata": {"Format": "<kind>", "Version": <n>}}`, and a reader refuses a version of zero or above the one it supports. [Scene documents](../world/serialization.md) teaches the layouts, how they are read as streams and why a writer puts one entity on each line, and [Projects and settings](../world/projects-settings.md) teaches the project file.

| Format | Header and version | Version constant | Reader and writer | Taught by |
| --- | --- | --- | --- | --- |
| Scene, `.stscene` | `Format` is `Scene`, `Version` 1; then `Scene` with `Name`, `Settings`, `EntityCount`, `Entities` | `SceneSerializer::c_FormatVersion` | `SceneDocumentReader`, `SceneDocumentWriter` | [Scene documents](../world/serialization.md) |
| Prefab, `.stprefab` | `Format` is `Prefab`, `Version` 1; then `Prefab` with `EntityCount`, `Entities` | `Prefab::c_FormatVersion` | `SceneDocumentReader`, `SceneDocumentWriter::WritePrototype` | [Scene documents](../world/serialization.md) |
| Model, no file extension of its own | `Format` is `Model`, `Version` 1; then `Model` with `EntityCount`, `Entities` | `Model::c_FormatVersion` | `SceneDocumentReader`, `SceneDocumentWriter::WritePrototype` | [Scene documents](../world/serialization.md) |
| Cooked scene | Magic `STSC`, version 1, a 64-byte header | `CookedSceneFormat::c_Version` | `CookedSceneReader`, `CookedSceneWriter` | [Scene documents](../world/serialization.md) |
| Project, `.stproj` | `Format` is `Project`, `Version` 3 | `Project::c_FormatVersion` | `Project::Load`, `Project::Save` | [Projects and settings](../world/projects-settings.md) |

The cooked scene is little endian. Its header holds, in order, the magic, the version, flags (none exist, so a reader refuses a file with any), the header's size and the kind of document. Then come the counts of entities, component types and strings, the bytes of the strings, and where the section table is with its count of sections. The last fields are a cyclic redundancy check (CRC-32C) of the table and one of the header, which the writer computes with the header's own field zero.

Sections are 16-byte aligned, each with its own CRC-32C in the table, and a reader checks every checksum before it decodes anything.

A reader of another build maps component types and properties by name.

The project file still reads its older versions: a version 1 file has no `Scripts` object and takes the default script settings, and versions 1 and 2 have no `Settings`. The file's `Project` object holds the project's name, asset folder, start scene, script settings, export settings and game information; its `Settings` object holds one entry per section, each with its `Version` and `Value`. Project members that a later version added are written back as read.

:::note
When a document is read, components and properties that this build does not know are kept, not dropped. A scene from a newer engine, or one that uses a module the build lacks, keeps those components word for word as JSON in the entity's unknown-components record, and the writer puts them back. Loading and saving never loses them, and the cooked form keeps them in its own section.
:::

## Where it lives in Strata

- `Strata/src/Strata/Scene/Scene.h`: the `Scene` class, `SceneSettings`, `PhysicsCapacitySettings` and the scene limits.
- `Strata/src/Strata/Scene/Entity.h`: the `Entity` handle and its component functions.
- `Strata/src/Strata/Scene/SceneSystem.h`: the system descriptor that the system table reads.
- `Strata/src/Strata/Reflection/ComponentRegistry.h`: `ComponentFlags`.
- `Strata/src/Strata/Reflection/Property.h`: `PropertyType`, `PropertyFlags` and `PropertyInfo`.
- `Strata/src/Strata/Reflection/PropertyBinary.h`: `c_MaxBinaryStringBytes`.
- `Strata/src/Strata/Core/SettingsRegistry.h`: `SettingsScope`, `SettingsFieldType`, `SettingsField`, `SettingsSection` and the id and value limits.
- `Strata/src/Strata/Project/Project.h`: the project file's format version and its limits.
- `Strata/src/Strata/Scene/SceneDocumentWriter.h`: the writer of scene, prefab and model documents.
- `Strata/src/Strata/Scene/SceneDocumentReader.h`: the streaming reader and its entity limit.
- `Strata/src/Strata/Scene/CookedScene.h`: the cooked scene's header, sections and `c_MaxBlobBytes`.
- `Strata/src/Strata/Scene/UnknownComponents.h`: the record that keeps components the build does not know.
- `tools/reference-limits.json`: the list of constants that the generated limits table parses.
