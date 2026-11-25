# Allocation: world

## `world/what-a-world-is` — What a game world is made of

**Covers.** The page starts from what the reader saw in `start/first-game`: the Hierarchy panel lists the things of a
scene and the Inspector shows the parts of one of them (the opening picture). The problem: a game world is many things
(a player, a crate, a light, a camera) that the engine must store, find, update, draw, save and load, every frame. The
naive answer is a class for each kind of thing with a virtual `Update`; the page shows where it breaks (deep
hierarchies, a base class that grows to hold everything, behaviour that cuts across classes, objects scattered in
memory). Then the idea in one diagram: an entity is only an identity, components are plain data attached to it (one of
each type at most), and systems hold the behaviour and run over every entity that has the components they need. The
approaches follow, each introduced by the flaw of the one before: object hierarchies (Unreal's `AActor`), objects that
own components (Unity's GameObject), and the data-oriented ECS in its two storage forms, sparse sets (EnTT) and
archetypes (flecs, Unity DOTS, Bevy), ending in a table of their cost, cache use, flexibility and users. Strata's choice
and its reason: one EnTT registry whose components are plain data, behaviour in scene systems, and a `Scene` class that
wraps the registry with persistent identity, a hierarchy and caches; loops over one component type are cache-friendly,
a scene can hold a million entities, and one description of the data drives files and the editor. What the choice
cannot do: an entity has no methods and no type of its own. The common mistake: thinking an entity "is" an object with
methods. The exercise designs a door that opens when the player comes near in each object model, as short sketches
that the reader runs. At the end the reader can say what an entity, a component, a system and a scene are, and why
Strata stores them as it does.

**Leaves out.**

- How EnTT stores components, handles against UUIDs, the `Entity` class → `world/ecs`
- Parents, children and world transforms → `world/scene-graph`
- Systems, their order and the fixed step in code → `world/systems`
- Making entities in the editor, for game makers → `make/scenes-entities`
- The sparse set as a data structure → `basics/data-structures`

**Fit.** `fits`: about 3,800 words against M (3,000). The naive answer, the idea and the three approaches with their
table take most of it, beside one screenshot, two diagrams and the exercise; the page is 200 words below M's top.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `scene-ecs:271` | concept | home | What a scene is: the problem, object hierarchies, components on objects and the ECS, Strata's choice (EnTT, plain-data components, scene systems, `Scene` wrapping the registry) and the newcomer's error |
| `scene-ecs:472` | figure | home | The Hierarchy panel with a nested tree (a sample's start scene, such as `Samples/ThirdPerson`) and the Inspector of one entity: the opening picture |
| `scene-ecs:611`, `scene-ecs:613`, `scene-ecs:615`, `scene-ecs:624` | term | home | Entity, component, ECS and scene, defined where the idea is first drawn |
| `scene-ecs:281` | concept | link | Components as plain data and tag components, named here and taught in `world/ecs` |
| `scene-ecs:284` | concept | link | Sparse sets against archetypes, named in the table; Strata's storage is `world/ecs`' |
| `new:13` | hands-on | home | The page's exercise (D27), a design exercise done as sketches: a door that opens when the player comes near, written three ways as short C++ sketches run for a few frames (a class hierarchy with a virtual `Update`; a game object that owns components; entities with a door component and a system that runs over them), each with its output; the answer weighs the three and names Strata's form, a plain-data component and a scene system (about 250 words). Evidence: `Strata/src/Strata/Scene/SceneSystem.h:26-30` (a scene system is the runtime part attached to a scene while it plays) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Classes, inheritance and virtual calls | `basics/cpp-classes` | must |
| Caches, and why the order of data in memory matters | `basics/computer` | must |
| Arrays, hash maps and what operations cost | `basics/data-structures` | helps |
| One frame of an engine: input, update, draw | `core/frame-loop` | helps |
| The Hierarchy and Inspector panels, as the first game used them | `start/first-game` | helps |
| What a game engine is, and a survey of engines | `start/what-an-engine-is` | helps |

## `world/ecs` — Entities and components, with EnTT inside

**Covers.** The job: `Scene` stores entities and their components in one EnTT registry (EnTT 3.16) and gives every
entity a persistent UUID; it is main-thread only. The hierarchy, systems and files are later pages'. The problem and the
approaches are one paragraph that links `world/what-a-world-is`. The map is the scene's anatomy: the registry with one
storage per component type, the UUID-to-entity map, the root list, the caches, the systems and services. The toy
version is a sparse set of about 60 lines (emplace, remove by swapping with the last element, contains, iterate) and a
view over two of them; then EnTT's own `swap_and_pop` shows why removing one component moves another, which is why a
`T&` or an `Entity` is never held across an add, a remove, a frame or a copy. Handles against UUIDs: the 32-bit EnTT
handle with a 20-bit index and a version, recycled after destruction, against the `IDComponent`'s UUID, which survives
saving, loading and copies (`GetEntityByUUID`); the `UUID` class quoted whole: a 64-bit random value that is never zero,
because zero is the null, written as 16 hexadecimal digits and hashed with `std::hash` to key the UUID map
(`Strata/src/Strata/Core/UUID.h:13-44`): Strata's choice of 64 bits, not the standard's 128-bit UUIDs, which
`basics/data-formats` teaches. The `Entity` class walked through: a
non-owning handle, its templated component functions, the `static_assert` that refuses `GetComponent` on a tag
component, `MarkModified` named with a link forward; then, after the rule "hold UUIDs, not `Entity`", the other class
named `Strata::Entity`: the script SDK's is a UUID value that scripts keep in fields, whose calls do nothing once the
entity is gone, which is why scripts may store it (`scripting/abi-sdk`; about 100 words). Creating an entity: what
every entity gets and why the hierarchy node comes first; duplicate UUIDs replaced with an error; the limit of
1,048,575 entities and its clean failure. Components as plain data, tag components (`InactiveComponent`) and views (`GetAllEntitiesWith`); the registry's
context, where a module keeps one object per scene (the render scene, the game UI's state). The Scene module's
own components in one table (each taught on its own page), the two types it declares for sibling layers
(`MeshRendererComponent`, `SkinComponent`), and the runtime-only components that are never registered. Then the
alternatives (archetypes, EnTT's groups, objects), the tests (the `Scene` suite), changing it safely, and a "trace it
yourself" exercise: follow one component's storage through a view in a debugger. At the end the reader can create,
find and remove components in engine code and say which identifier survives what.

**Leaves out.**

- Change signals and what `MarkModified` is for → `world/scene-graph`
- Parents, children and the two hierarchy components → `world/scene-graph`
- Copying a whole scene to play it → `world/systems`
- How components are described to files, the editor and commands → `world/reflection`
- Asset handles and `.meta` files → `assets/handles-meta`
- The camera component → `gpu/coordinates`
- Sparse sets as a data structure in general → `basics/data-structures`
- The script SDK's `Entity` and how scripts reach entities → `scripting/abi-sdk`

**Fit.** `fits`: about 4,850 words against L (5,000). The toy sparse set and four excerpts (the short `UUID` class
among them) take a third of the page, and the table of the Scene module's components stays a table.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `scene-ecs:25-27` | feature | home | `Scene` owns one registry, the UUID map, the roots and caches, main thread only; the `Entity` handle and its templated functions; tags cannot be fetched |
| `scene-ecs:29-31` | feature | home | `IDComponent` against the EnTT handle; what entity creation emplaces and in which order; the capacity limit and its error |
| `scene-ecs:51` | feature | home | `IDComponent`'s flags (Hidden, NotRemovable, NoSerialize) and why the serializer writes it as the entity's "ID" |
| `scene-ecs:59-60` | feature | home | `MeshRendererComponent` and `SkinComponent`: types declared in the Scene layer because sibling layers read them, registered by their modules |
| `scene-ecs:62` | feature | home | The runtime-only components (`HierarchyComponent`, `WorldTransformComponent`, `SubSceneComponent`, `UnknownComponentsComponent`): never registered, serialized or shown |
| `scene-ecs:94` | feature | home | `GetAllEntitiesWith` as a registry view |
| `new:12` | feature | home | The registry's context: one object per scene that a module keeps in the registry (`RenderSceneContext`, `GameUISceneContext`), which the context copiers of `world/systems` carry into copies. Evidence: `Strata/src/Strata/Renderer/RenderScene.cpp:100-102`; `Strata/src/Strata/GameUI/GameUIScene.cpp:61-63` |
| `scene-ecs:52-57` | feature | link | The other components of the Scene module, one row each in the table, each linking the page that teaches it |
| `scene-ecs:28` | feature | link | `MarkModified` seen in `Entity.h`; its meaning is `world/scene-graph`'s |
| `scene-ecs:277`, `scene-ecs:281`, `scene-ecs:284` | concept | home | Two kinds of ID; components as plain data and tags; storage as sparse sets and what Strata does with it (whole-storage copies, prototypes' own arrays) |
| `scene-ecs:374` | code | home | `Strata/src/Strata/Scene/Entity.h:12-114`: the handle class; templates, perfect forwarding, `decltype(auto)`, the tag `static_assert`, `MarkModified` |
| `scene-ecs:375` | code | home | `Strata/src/Strata/Scene/Scene.cpp:386-415`: `CreateEntityWithUUID`, what every entity gets and why the hierarchy node comes first |
| `new:1` | code | home | `Strata/vendor/entt/src/entt/entity/sparse_set.hpp:260-276`: EnTT's `swap_and_pop` (quoted as `vendor:entt/src/entt/entity/sparse_set.hpp`), after the toy: removal moves the last element into the hole |
| `assets:377` | code | home | `Strata/src/Strata/Core/UUID.h:13-44`: the `UUID` class whole: a 64-bit random id with zero reserved as the null, its text form, and the `std::hash` that keys the UUID map; `assets/handles-meta` quotes it for asset handles |
| `foundation:154` | feature | home | `UUID` as the foundation survey lists it (64-bit, random, never zero, 16 hexadecimal digits, `std::hash`): taught once with the handles against UUIDs |
| `scene-ecs:417`, `scene-ecs:419`, `scene-ecs:421` | figure | home | The scene's anatomy (the map); sparse-set storage with a swap-remove and a view of two storages; the handle's index and version against the UUID, and what survives saving and copies |
| `scene-ecs:516`, `scene-ecs:518`, `scene-ecs:519` | rule | home | Hold UUIDs, not `Entity` or `T&`, across frames and copies, with the paragraph after the rule: the script SDK's `Entity` wraps the UUID, so scripts may keep it (`StrataScriptCore/Include/StrataScript/Entity.h:26-37` against `Strata/src/Strata/Scene/Entity.h:12-21`); never `GetComponent` a tag; at most 1,048,575 entities |
| `new:29` | hands-on | home | The page's "trace it yourself" exercise (style.md §11; D27), which the Covers names and no inventory lists: a breakpoint in a loop over `GetAllEntitiesWith<TransformComponent, NameComponent>()` is followed into EnTT's view, which walks the dense array of one storage and skips each entity that the other storage lacks; the reader sees the entity's index in the sparse array and its place in the dense one, then removes a component and sees the last element move into the hole (about 250 words). Evidence: `Strata/src/Strata/Scene/Scene.h:679-683`; `Strata/vendor/entt/src/entt/entity/view.hpp:68-76`; `Strata/vendor/entt/src/entt/entity/sparse_set.hpp:260-276` |
| `scene-ecs:614`, `scene-ecs:617-621` | term | home | Tag component, registry (EnTT's meaning), component storage (the qualified entry: EnTT's per-type container, not the computer's storage) and sparse set, view, handle, UUID |
| `foundation:642`, `editor-core:686` | term | home | The foundation and editor surveys' entries for UUID: one glossary entry with `scene-ecs:621`; the editor's names asset handles too, which are UUIDs that name assets, and their own entry is `assets/handles-meta`' |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Object models compared; entity, component and system | `world/what-a-world-is` | must |
| Templates, `static_assert` and the standard containers | `basics/cpp-generic` | must |
| `constexpr`, `if constexpr` and perfect forwarding | `basics/cpp-modern` | helps |
| The sparse set and its cost as a data structure | `basics/data-structures` | must |
| Bits, masks and two numbers packed into one integer | `basics/numbers` | must |
| UUIDs as random identifiers, hexadecimal text | `basics/data-formats` | must |
| `Ref`, `Scope`, asserts and errors returned | `core/conventions` | must |
| The main thread owns the scene | `core/jobs` | helps |
| Caches and memory layout | `basics/computer` | helps |
| Running a debugger on a test | `core/debugging` | helps |

## `world/scene-graph` — The scene graph: hierarchy, transforms and the transform contract

**Covers.** The job: the hierarchy of entities, local and world transforms, and the caches the scene keeps of them
(world matrices, hierarchy order, activity, the name and tag indexes), with the contract every writer follows so that
they stay true. This page carries the full section on the problem: hierarchies in an ECS (a parent pointer only, child
lists, intrusive linked lists, arrays sorted by depth as in Unity DOTS) and world transforms (recompute everything, dirty
flags with propagation, change versions). The map: the two hierarchy components, the transform components, the caches
and their readers (the render scene, physics). Then, in this order:

1. Transforms: `TransformComponent` as translation, quaternion rotation and scale; `GetTransform` composes and
   `SetTransform` decomposes through `Math::DecomposeTransform`, which fails, keeping the old values, only for
   non-finite values, a homogeneous w near zero or a scale axis near zero; it folds a mirror into a negative X scale and
   drops shear without a word, so a keep-world `SetParent`, a `SetWorldTransform` or an `InstantiateMany` whose result is
   sheared succeeds, and the child's world pose loses the shear (about 120 words); `Translation` is local, and the world
   matrix is a separate runtime component.
2. The dual hierarchy: `RelationshipComponent` (UUIDs, the authoritative child order, written to files) mirrored by
   `HierarchyComponent` (handle links to parent, first and last child and siblings, depth, cached sibling index), and why
   two forms; `LinkLast` keeps both in step in constant time.
3. Changing the hierarchy: `SetParent` with its cycle check and "keep the world transform" (the parent's inverse),
   sibling indices renumbered lazily, `PlaceEntities`, `IsDescendantOf`; `CompareHierarchyOrder` as the lowest common
   ancestor found by depth; the hierarchy order cached by version, and the bounded log of hierarchy moves.
4. Signals: EnTT's `on_construct`, `on_update` and `on_destroy`; `MarkModified` is `patch`; how the caches subscribe
   (`ConnectSignals` and its handlers).
5. World transforms, incrementally: dirty marks, the frontier of dirty entities without a dirty ancestor (memoized so
   the total stays linear), the walk level by level that switches to `ParallelFor` once a level has 1,024 independent
   subtrees; exact reads between updates (`GetWorldTransform`, and `FindCurrentWorldTransform` for workers),
   `SetWorldTransform` and its refusal of near-singular parents, `InvalidateAllTransforms`; the change log
   (`GetWorldTransformChanges`, 16,384 entries) and versions.
6. The transform contract: every direct write signals; `MarkTransformChanged` for writes one's own listeners must not
   hear (the physics write-back); values written right after `AddComponent` need no signal; the Debug check that
   recomputes and names the entity, paced by `AmortizedCheck` (each update earns a budget of 512 entities and the check
   runs once the budget covers the scene; it counts calls, never time, and the render scene's validation is paced the
   same way); the counters tests use to prove "no traversal".
7. Activity in the hierarchy: `InactiveComponent`, `ActiveInHierarchy` kept exact at once, `IsActiveInHierarchy`.
   Strata keeps no separate activity version: adding or removing `InactiveComponent`, or reparenting, raises the
   transforms version and logs the entities whose activity changed in `GetWorldTransformChanges` at once, which is how
   the render scene and the game UI read activity changes (about 50 words).
8. Lookups: the name and tag indexes built on first use and kept by signals, hash buckets with swap-remove, answers in
   hierarchy order (`FindEntityByName`, `FindEntitiesByTag`, `HasChildNamed`); the primary camera
   (`GetPrimaryCameraEntity`: the first active Primary camera in hierarchy order; the camera itself is `gpu/coordinates`').

Then the alternatives, the tests (`Scene.Hierarchy`, `Scene.Transforms` and its sweep, the `Perf.Scene.*` budgets),
changing it safely, and what went wrong before: deleting 10,000 of 100,000 roots took 54.6 s before wave 1's cached
hierarchy and batched deletes, and about 45 ms after (`Docs/Roadmap.md:48-50`); the rule "one `DestroyEntities` for
many" rests on that batch, which compacts each sibling list once and changes the hierarchy version once (the call is
`world/systems`'). The exercises: a doctest that moves the root of a three-level tree, first traced with a breakpoint
from `component.set` on the root's Transform to the dirty list (the "trace it yourself" exercise), then counting the
recomputed entities; a contract violation reproduced and fixed; a root moved against a leaf at 100,000 entities; random
trees checked against `CompareHierarchyOrder`. At the end the reader can change a hierarchy and its transforms from
engine code without breaking the caches, and say what a frame of transform updates costs.

**Leaves out.**

- Matrices, TRS, decomposing a matrix and quaternions as mathematics → `basics/math-matrices`, `basics/math-bases`, `basics/math-rotations`
- `ComposeWorldTransform` and its FMA rule → `core/math`
- The camera component, its projection and its fields → `gpu/coordinates`
- Destroying entities while systems update → `world/systems`
- Drawn transforms between fixed steps → `world/interpolation`
- How physics writes simulated poses back → `physics/world-step`
- How the render scene follows the change log → `draw/render-scene`
- The UI contract, which mirrors this one → `ui/contract`
- Sub-scene membership of top-level entities → `world/sub-scenes`
- Moving entities in the editor, for game makers → `make/transforms-units`

**Fit.** `fits`: about 9,650 words against XL (8,000). Eleven excerpts, four figures and four exercises take most of
it; at 350 words below XL's top (10,000) the page has no room, and past it the page splits into "The scene graph:
hierarchy, transforms and activity" (sections 1 to 3 and 7) and "Change signals, the transform cache and the transform
contract" (sections 4 to 6 and 8).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `scene-ecs:28` | feature | home | `MarkModified` is `registry.patch`: EnTT's `on_update`, the engine-wide "I wrote this in place" signal |
| `scene-ecs:52-56` | feature | home | Name and Tag (indexed, so writes signal), Inactive (activity), Transform (TRS, Euler degrees in the Inspector), Relationship (UUID parent and children) |
| `scene-ecs:71-85` | feature | home | The dual hierarchy, `SetParent`, sibling indices and batch moves, hierarchy order and moves, cached world matrices and the parallel walk, `HasDirtyAncestor`, exact reads, `SetWorldTransform`, `MarkTransformChanged`, `InvalidateAllTransforms`, activity, change reports, the Debug self-check, the diagnostic counters; a change of activity raises the transforms version and enters the change log at once, with no activity version of its own (`Scene.h:372-384`, `Scene.cpp:1150-1197`) |
| `scene-ecs:91-93` | feature | home | The name and tag indexes, the lookups, and the lookup of the primary camera |
| `foundation:163` | feature | home | `AmortizedCheck`, which paces the Debug check of the scene's caches by a budget of elements per call (`Strata/src/Strata/Core/AmortizedCheck.h`, `Scene.h:393-400`); the render scene's validation, paced the same way, is named |
| `scene-ecs:289`, `scene-ecs:292`, `scene-ecs:297`, `scene-ecs:302`, `scene-ecs:306`, `scene-ecs:311`, `scene-ecs:313` | concept | home | Signals and "write then signal"; transforms and the scene graph (decomposition fails for zero scale and non-finite values, and loses shear without failing, as section 1 says, not as the inventory's concept 6 has it); hierarchies in an ECS; dirty flags and incremental world transforms; the transform contract; activity; lookups and indexes |
| `scene-ecs:373` | code | home | `Strata/src/Strata/Scene/Components.h:50-81`: the TRS component, the relationship by UUID, the cached world matrix as a separate runtime component |
| `scene-ecs:376` | code | home | `Strata/src/Strata/Scene/SceneHierarchy.h:14-37`: the intrusive doubly linked hierarchy kept in a component |
| `scene-ecs:377` | code | home | `Strata/src/Strata/Scene/Scene.cpp:942-974`: `LinkLast`, the constant-time append that keeps the UUID list and the links in step |
| `scene-ecs:378` | code | home | `Strata/src/Strata/Scene/Scene.cpp:1270-1304`: `SetParent`: cycle check, keep the world transform, depth and activity, the signal last |
| `scene-ecs:379` | code | home | `Strata/src/Strata/Scene/Scene.cpp:1448-1476`: `CompareHierarchyOrder`, the lowest common ancestor by depth |
| `scene-ecs:380` | code | home | `Strata/src/Strata/Scene/Scene.cpp:1597-1752`: `UpdateWorldTransforms` and `WalkWorldTransforms`, the page's central algorithm: frontier, levels, `ParallelFor`, change log, one template per hook |
| `scene-ecs:381` | code | home | `Strata/src/Strata/Scene/Scene.cpp:1530-1562`: `HasDirtyAncestor`, memoized with a pass counter so the total stays linear |
| `scene-ecs:382` | code | home | `Strata/src/Strata/Scene/Scene.cpp:1754-1787`: `GetWorldTransform`, exact between updates with the cache's association |
| `scene-ecs:383` | code | home | `Strata/src/Strata/Scene/Scene.cpp:194-206`: `ConnectSignals`; the page also shows the handlers at `Scene.cpp:2039-2082` |
| `scene-ecs:384` | code | home | `StrataTests/src/Scene/SceneTransformTests.cpp:368-388`: the contract proved by a test: the unsignalled write caught, `MarkTransformChanged` repairs it |
| `scene-ecs:385` | code | home | `Strata/src/Strata/Scene/Scene.cpp:733-791`: the lookup index, hash buckets with swap-remove and a slot per entity |
| `scene-ecs:423`, `scene-ecs:425`, `scene-ecs:426`, `scene-ecs:428` | figure | home | The dual hierarchy drawn twice; local TRS to world and the inverse; dirty propagation walked through; the signal flow from a write to the readers, with the unsignalled write the Debug check catches |
| `scene-ecs:501`, `scene-ecs:505`, `scene-ecs:507`, `scene-ecs:509`, `scene-ecs:512` | rule | home | Signal every direct write; `MarkTransformChanged` when your listeners must not hear it; no signal after `AddComponent`; never edit the hierarchy components; `GetSiblingIndex` and one `DestroyEntities` for many |
| `gameui:514` | rule | home | The game UI survey's form of "values written right after `AddComponent` need no signal" (the construct signal covers them): one rule with `scene-ecs:507`; `ui/contract` says that the UI components follow it and links here |
| `scene-ecs:578`, `scene-ecs:579`, `scene-ecs:584`, `scene-ecs:585` | hands-on | home | The page's exercises: the three-level tree and `GetTransformUpdateCount`; the contract violation; root against leaf at 100,000 entities; random trees against `CompareHierarchyOrder` |
| `new:15` | hands-on | home | The "trace it yourself" exercise (D27), joined to the first exercise (`scene-ecs:578`) so that the page keeps four: a breakpoint follows `component.set` on the root's Transform through `ApplyComponents` and the patch to `OnTransformChanged`, `MarkTransformDirty` and the dirty list that `UpdateWorldTransforms` reads, before the recomputed entities are counted (about 150 words). Evidence: `StrataEditor/src/Editor/Commands/EntityCommands.cpp:721`; `StrataEditor/src/Editor/CommandUtils.cpp:510`, `:596`; `Strata/src/Strata/Scene/Scene.cpp:197`, `:1482-1489`, `:1597`, `:2039-2042` |
| `scene-ecs:622-623`, `scene-ecs:625-627`, `scene-ecs:631-634` | term | home | Signal, patch and `MarkModified`, root entity, sibling index, hierarchy version, dirty flag, frontier, transform contract, active in hierarchy |
| `editor-core:685` | term | home | The editor survey's entry for sibling index (an entity's position among its parent's children): one glossary entry with `scene-ecs:626` |
| `scene-ecs:630` | term | use | Decomposition (of a transform), whose glossary home is `basics/math-bases`: section 1 says what Strata's `DecomposeTransform` does (it fails for zero scale and non-finite values; shear is lost) |
| `scene-ecs:628-629` | term | link | Local and world transform, TRS: their mathematics is `basics/math-matrices`' |
| `new:14` | erratum | home | The scene inventory says that decomposing a matrix fails for shear (`plan/inventory/scene-ecs.md:293`, `:630`; process.md's table of errata, kind `inventory`). `DecomposeTransform` fails only for non-finite values, a homogeneous w near zero and a scale axis near zero; it folds a mirror into a negative X scale and drops a shear without a word, making a quaternion of the normalized columns as they are. Section 1 says what the code does. Evidence: `Strata/src/Strata/Math/Math.cpp:12-33`, `:35-37`, `:39-44`, `:46-48` |
| `scene-ecs:58` | feature | link | `CameraComponent`'s Primary field, read by the lookup; the camera is `gpu/coordinates`' |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Matrices, TRS, composing a parent's and a child's transform, the inverse | `basics/math-matrices` | must |
| Decomposing a matrix into translation, rotation and scale, and why TRS cannot hold shear | `basics/math-bases` | must |
| Quaternions and Euler angles | `basics/math-rotations` | must |
| `ComposeWorldTransform` and Strata's math types | `core/math` | must |
| `ParallelFor`, jobs and deterministic parallel work | `core/jobs` | must |
| Linked lists, trees and hash maps | `basics/trees-graphs` | must |
| Entities, handles, storages and the `Entity` class | `world/ecs` | must |
| Lambdas and callbacks stored in a container | `basics/cpp-generic` | must |
| Debug builds, asserts and what Dist compiles out | `core/conventions` | must |
| Writing and running one doctest case | `core/first-change` | must |
| `DestroyEntities` and its batching, which the rule "one `DestroyEntities` for many" and the story of 54.6 s use | `world/systems` | helps |
| Perf tests and their budgets | `engineering/perf-lab` | helps |

## `world/systems` — Systems, phases and fixed steps

**Covers.** The job: what runs while a scene plays: the scene systems and their order, the runtime frame with its fixed
steps, the time the scene keeps, entity lifetime during updates, and the services through which the systems of
different modules meet. This page carries the full section on how engines order updates (a hard-coded order, priority
numbers, dependency graphs as Bevy's `before` and `after` and Unity's `UpdateBefore`); the fixed step as an idea is one
paragraph that links `core/time`. The map: `SceneSystemRegistry`, the descriptors, a running scene's systems in update
order, the six built-in systems (UI, Scripting, Animation, World, Physics, Audio). Then, in this order:

1. The `SceneSystem` interface and its callbacks; Play against Simulate (physics only) and `RunsInSimulateMode`.
2. Descriptors: hard (`After`, `Before`) and soft (`AfterIfPresent`, `BeforeIfPresent`) constraints, `ProfileStage`,
   the `Calls*` flags, `PrepareLoadedScene` (named; `world/sub-scenes` uses it); `MakeSceneSystemDescriptor<T>` records
   the type for `GetSystem<T>` and detects at compile time which callbacks `T` overrides, so idle frames make only the
   calls they need.
3. The update order: a topological order that follows registration order, built from the back with a max-priority
   queue; why from the back, on the example of a "Wind" system before Physics and an unconstrained "CameraFollow"
   registered between them; cycles described; changes refused while any scene runs; the line the composition root logs
   with the update order and the soft constraints that name absent systems
   (`SceneSystemRegistry::GetAbsentSoftConstraints`), which is how a reader checks where a new system runs (about 60
   words).
4. Starting and stopping: `OnRuntimeStart` resets the clocks, creates the systems in order and starts them in two
   phases; `OnRuntimeStop` stops and destroys them in reverse. A scene that plays is a copy: `Scene::Copy` copies every
   storage whole and in parallel, through a copy function each component's registration supplies, the UUID map and
   caches as they are, connects the signals afterwards and runs the
   modules' context copiers (the render scene); `SceneCopyOptions::SerializedOnly` makes the snapshot that background
   saves write.
5. One runtime frame: `OnUpdateRuntime` in order: sub-scenes, the paused path, `OnUpdate`, the accumulator loop of
   `OnFixedUpdate` capped by `GetMaxFixedSteps` with the backlog dropped, time dilation (catch-up steps stop once they
   took longer than they simulated, `GetDroppedFixedStepCount`), the step alpha named (`world/interpolation`),
   `OnLateUpdate`, destruction flushed, world transforms, the Debug check; the accumulator's behaviour as numbers in a
   test (0.035 s gives three steps and carries 0.005 s); `OnUpdateEditor`.
6. The time the scene keeps: pause, `Step(n)` and `GetFixedStepCount` as the game's own time base, time scale and
   unscaled time; `GetFixedTimestep` and `GetMaxFixedSteps`, where the project's `Scene.Timing` rate wins over
   `SceneSettings`; the fields of `SceneSettings`.
7. Entity lifetime during updates: destroying an entity destroys its subtree, `DestroyEntities` batches, destruction
   during an update waits for its end, and `OnEntityDestroying` tells every system first (descendants first, the entity
   still valid).
8. Scene services: `RegisterService`, `GetService` keyed by the interface's type, one provider each, null when the module
   is absent; the interfaces of `SceneServices.h` listed with their providers (their contents are the modules' pages;
   `PhysicsSystem` registers seven, one more than the header's comment names);
   why: dependency inversion inside the layer table, never `GetSystem` of another module's class.

Then the alternatives, the tests (`Scene.Systems`, `Scene.Services`, `Scene`), changing it safely, and the exercises: a
"Spinner" system that rotates entities in `OnFixedUpdate` with soft constraints, checked for its order and its
`CallsUpdate`, and traced from the accumulator loop back to the dispatch list that `OnRuntimeStart` builds from the
`Calls*` flags (the "trace it yourself" exercise); a scene service offered by a Wind system and consumed by Spinner,
null without Wind; the order built from the front, which makes a test of `SceneSystemTests` fail. At the end the
reader can write and register a scene system, predict where it runs in a frame, and let it talk to another module
without including it.

**Leaves out.**

- The fixed step, the accumulator, the spiral of death and time dilation as ideas → `core/time`
- Topological sort in general (Kahn) → `core/engine-modules`
- The two kinds of registry: those that open and accept and stay open, as the scene systems' does, and the component and settings registries, which then freeze → `core/layers-registries`
- What each built-in system does → `physics/world-step`, `scripting/script-system`, `animation/system`, `audio/scene-system`, `worlds/physics-scripts`, `ui/input`
- Drawing between steps and the step alpha → `world/interpolation`
- `PrepareLoadedScene` and prepared loads → `world/sub-scenes`
- Play and Simulate in the editor, edits while playing → `editor/play-mode`
- Pausing and stepping from the editor and from tools → `editor/stepping`
- The script lifecycle as game code sees it → `make/script-loop`

**Fit.** `over`: about 7,400 words against L (5,000). XL by S2: the estimate is inside XL's range (6,501 to 10,000),
which the outline gives two other internals pages of track E (`world/scene-graph`, `world/reflection`); four exercises
(the Spinner with its trace among them), four excerpts and four figures take most of it.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `scene-ecs:32` | feature | home | Destruction of a subtree, `DestroyEntities` in batches (systems told about every subtree first), destruction deferred during an update |
| `scene-ecs:34-35` | feature | home | `Scene::Copy` for play (storages copied whole in parallel, caches as they are, signals connected after; the `SerializedOnly` snapshot) and `RegisterContextCopier` |
| `scene-ecs:100-114` | feature | home | The interface, Play and Simulate, descriptors and constraints, `MakeSceneSystemDescriptor`, the registry and its order, the built-in order, start and stop, `OnUpdateRuntime`, `OnUpdateEditor`, pause and steps, time scale and unscaled time, time dilation, the project's rate over `SceneSettings`, `SceneSettings`, `OnEntityDestroying` |
| `new:16` | feature | home | The log line of the update order: once the modules are registered, the composition root logs "Scene systems update in the order ..." and, when there are any, "soft constraints naming absent systems: ..." (each as "<system> after <name>" or "<system> before <name>", from `SceneSystemRegistry::GetAbsentSoftConstraints`), which is how a reader checks where a new system runs; `world/tutorial-component`'s check may read it (about 60 words). Evidence: `Strata/src/Strata/Engine/BuiltinModules.cpp:163-173`; `Strata/src/Strata/Scene/SceneSystem.cpp:250-271` |
| `scene-ecs:118` | feature | home | Scene services: the mechanism and the list of interfaces with their providers |
| `new:17` | erratum | home | The comment of `SceneServices.h` names six services that `PhysicsSystem` offers; it registers seven, `IPhysicsDiagnostics` among them (process.md's table of errata, kind `engine`; capstone-q8). The page lists the seven. Evidence: `Strata/src/Strata/Scene/SceneServices.h:28-29`; `Strata/src/Strata/Physics/PhysicsSystem.cpp:61-67`; `Strata/src/Strata/Physics/PhysicsSystem.h:54-55` |
| `scene-ecs:321`, `scene-ecs:326`, `scene-ecs:329` | concept | home | Systems and update order; decoupling modules through services and layers; entity lifetime during iteration |
| `scene-ecs:316` | concept | use | The accumulator as `core/time` teaches it; this page shows Strata's code of it |
| `scene-ecs:386` | code | home | `Strata/src/Strata/Scene/SceneSystem.h:26-138`: the interface, the descriptor, and `MakeSceneSystemDescriptor`'s compile-time detection with `decltype(&T::OnUpdate)` |
| `scene-ecs:387` | code | home | `Strata/src/Strata/Scene/SceneSystem.cpp:67-159`: `ComputeUpdateOrder`, built from the back with a priority queue; hard and soft edges; the cycle report |
| `scene-ecs:388` | code | home | `Strata/src/Strata/Scene/Scene.cpp:2239-2328`: the page's one excerpt of `OnUpdateRuntime` (2199-2335) and its central algorithm, from the fixed timestep through `OnLateUpdate`: the accumulator, the cap, the dropped backlog, time dilation, the capture and the alpha; the rest of the function (sub-scenes, the paused path, destruction flushed, world transforms, the Debug check) is told in section 5's prose |
| `scene-ecs:389` | code | home | `StrataTests/src/Scene/SceneTests.cpp:486-527`: the accumulator's behaviour as numbers, pause and step, the cap |
| `scene-ecs:431`, `scene-ecs:433`, `scene-ecs:438`, `scene-ecs:440` | figure | home | The runtime lifecycle as a state machine; one runtime frame as a timeline with the built-in systems in each phase, the book's one frame timeline (R31, D42), drawn with an overlay for physics (changes applied, steps, dispatch: `physics/world-step`) and one for worlds (the World system and the sub-scene slices on one budget: `worlds/physics-scripts`), the figure and both overlays captured once from this page's recipe; the order graph of the six built-ins with Wind and CameraFollow; the services between modules |
| `scene-ecs:436` | figure | link | The accumulator timeline, drawn on `core/time` |
| `scene-ecs:514`, `scene-ecs:533`, `scene-ecs:535`, `scene-ecs:537`, `scene-ecs:539` | rule | home | Destruction during an update is deferred; declare order with soft constraints toward other modules; build descriptors with `MakeSceneSystemDescriptor`; modules meet through services; read the step through `GetFixedTimestep` |
| `scene-ecs:541` | rule | link | Tools count fixed steps, never frames: the design decision of `core/time` |
| `scene-ecs:581`, `scene-ecs:583`, `scene-ecs:589` | hands-on | home | The Spinner system; the Wind service; the order built from the front |
| `new:18` | hands-on | home | The "trace it yourself" exercise (D27), joined to the Spinner's (`scene-ecs:581`) so that the page keeps four: a breakpoint in the Spinner's `OnFixedUpdate` is followed back through `ForEachSystemCall` in the accumulator loop to `m_FixedUpdateCalls`, which `OnRuntimeStart` fills from the descriptor's `CallsFixedUpdate`, and `MakeSceneSystemDescriptor` sets from what the class overrides; so a system that overrides no `OnUpdate` is never called per frame (about 150 words). Evidence: `Strata/src/Strata/Scene/Scene.cpp:2088`, `:2121-2125`, `:2291`; `Strata/src/Strata/Scene/SceneSystem.h:93`, `:134` |
| `scene-ecs:635-636`, `scene-ecs:644-645` | term | home | Scene system, update phases, hard and soft constraint, scene service |
| `audio-input:651-652` | term | home | The audio survey's entries for scene system and for scene service against engine service: one glossary entry each with this page's; engine service's home is `core/engine-modules` |
| `animation:584` | term | home | The animation survey's entry for scene service: one glossary entry with this page's |
| `scripting:606` | term | home | The scripting survey's entry for scene service: one glossary entry with `scene-ecs:645` |
| `foundation:186` | feature | use | Pause and `Step` with `GetFixedStepCount` as the tools' clock, as the foundation survey lists it |
| `physics:156-157` | feature | home | The accumulator loop (the cap, the dropped backlog, time dilation) and `SceneSettings` as the physics survey lists them: the same code as `scene-ecs:107`, `scene-ecs:111` and `scene-ecs:113`, taught once in sections 5 and 6 |
| `gamedev:367` | code | use | The game makers' survey's form of the same lines (`Scene.cpp:2239-2328`): quoted once, as the excerpt of `scene-ecs:388` |
| `gamedev:563` | hands-on | home | An exercise: `FixedRate` set to 30, 60 and 240, the step alpha logged each frame by the script of `start/first-game` (`Time::GetStepAlpha`), and the step counts read with `play.state` (the line to paste, linked forward to `editor/commands`) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Virtual functions and interfaces | `basics/cpp-classes` | must |
| `decltype`, type traits and `if constexpr` | `basics/cpp-modern` | must |
| The fixed step, the accumulator, the spiral of death, time scale and time dilation | `core/time` | must |
| Topological sort (Kahn) | `core/engine-modules` | must |
| Engine services, against the scene services taught here | `core/engine-modules` | helps |
| The composition root, registries that open and accept (the scene-system registry stays open: a system is refused only while a scene runs), the layer table and dependency inversion | `core/layers-registries` | must |
| Graphs and priority queues | `basics/trees-graphs` | must |
| The frame loop and its update | `core/frame-loop` | must |
| Threads, and why the scene belongs to the main thread | `basics/threads` | helps |
| Entities, storages and views | `world/ecs` | must |
| The world transform update after the steps | `world/scene-graph` | helps |
| The copy functions each component's registration supplies (`ComponentInfo`'s `AssureStorage` and `CopyStorage`), which `Scene::Copy` calls | `world/reflection` | helps |
| Profile stages | `core/profiling` | helps |

## `world/interpolation` — Drawing between fixed steps

**Covers.** The job: draw fixed-step motion between its last two poses, so that it does not judder when the frame rate
is above the step rate, while the simulation never reads what is drawn. This page carries the full section on the
problem: judder shown as numbers (a body stepped at 60 Hz and drawn at 144 Hz), the approaches (interpolate with one step
of latency, extrapolate and overshoot, a variable step and its lost determinism) and a table of their costs; `core/time`'s
paragraph is linked. The map: the interpolated set beside the world transforms; the fixed steps write it, the render
scene reads it. Then, in this order:

1. The switch: `SetInterpolation`, and `IsInterpolating` as the switch and the project's `Scene.Timing.Interpolation`
   and a running scene.
2. The set: parallel arrays by slot (entities, entries, drawn matrices) with a slot map by entity index; the roles
   Blend, Compose and Exact.
3. The capture after the steps: `UpdateWorldTransforms` in its capture pass records every matrix it overwrites, and the
   set is rebuilt in four phases.
4. The step alpha: the drawn time `T + a - h` and the formula `1 - (1 - a/h)/n`, from a timeline.
5. Writes to members of the set outside the steps, and the per-frame rules.
6. The pose blend: lerp of translation and scale, a normalized lerp of the quaternion on the shorter arc, and why not
   `glm::mix` or slerp.
7. Drawn matrices: computed lazily when the render scene syncs; `FindDrawnTransform`, `GetDrawnTransform` (exact at any
   time) and the drawn version.
8. Breaks and clears: teleports (`BreakInterpolation`); pause, a step, a changed step, the project turning it off,
   start and stop; the safety net at 400 m/s (box3d's top speed) that makes an entry Exact; stats and validation.
9. The rules for renderer code (draw drawn transforms, never simulate with them) and for game code (follow moving bodies
   with their drawn positions in `OnLateUpdate`, because a camera that follows the world position makes the body judder
   against it above the step rate; move carriers in fixed steps).
10. What it does not do yet: drawn poses for world-space game UI, gizmos and picking, reflection probes, fog,
    post-process volumes, the sky and the sun; attachments placed outside their animator's hierarchy following its
    drawn pose; a cap on interpolated bodies (the Roadmap's "Interpolation, the rest").

The figure of interpolation off and on (a body's drawn screen position per frame, from a sample at a high frame rate),
the tests (`Scene.Timing` and its sweep, and the capture's cost, `Perf.Scene.InterpolatedStepFrame100k.Ratio` at 2.1
against its 1.5 target, a movable claim: `Docs/Roadmap.md:1702`, `StrataTests/Perf/Budgets.json:270`), changing it
safely, and the exercises: the Spinner of `world/systems` drawn
smoothly, its entities reported as Blend and a child light as Compose; and the "trace it yourself" exercise, which
follows the child light's drawn matrix from `RenderScene::Sync` through `UpdateDrawnTransforms` and
`FindDrawnTransform` to the Compose case of `ComputeDrawnTransform`. At the end the reader can explain the drawn time
and the three roles, and write renderer or game code that reads the right transform.

**Leaves out.**

- The fixed step and the accumulator → `core/time`
- The runtime frame that captures and computes the alpha → `world/systems`
- Lerp and smoothing as mathematics → `basics/math-interpolation`
- Interpolating rotations as mathematics → `basics/math-rotations`
- How the render scene reads drawn transforms → `draw/render-scene`
- Following a body with a camera in a game → `make/characters-cameras`
- Teleporting physics bodies → `physics/world-step`
- The project's switch as a settings section → `world/projects-settings`

**Fit.** `fits`: about 5,900 words against L (5,000). Four excerpts and the lines of `OnUpdateRuntime` that compute the
alpha, the problem section with its table and two exercises take most of it; phase B reads the page again at the move
to v0.8.0 (`process.md`, step 11), because interpolation is new in 0.8.0.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `scene-ecs:130-139` | feature | home | The switch, the set and its roles, the capture pass, the step alpha, per-frame writes, the pose blend, drawn matrices, breaks and clears, the safety net, stats and validation |
| `scene-ecs:357` | concept | home | Why motion judders; interpolate, extrapolate or vary the step; Strata's state interpolation of only what the steps moved; drawn transforms apart from simulated ones; the mistakes |
| `scene-ecs:390` | code | home | `Strata/src/Strata/Scene/SceneInterpolation.cpp:104-116`: `BlendPose`, lerp and nlerp on the shorter arc, why not `glm::mix` or slerp |
| `scene-ecs:391` | code | home | `Strata/src/Strata/Scene/SceneInterpolation.cpp:240-374`: `CaptureInterpolation`, the set built from the capture pass: roles, exits, parent slots, breaks |
| `new:2` | code | home | `Strata/src/Strata/Scene/TransformInterpolation.h:15-38`: the roles and an entry of the set, with each role's rule in its comment |
| `new:3` | code | home | `Strata/src/Strata/Scene/SceneInterpolation.cpp:410-525`: `UpdateDrawnTransforms`, `FindDrawnTransform`, `GetDrawnTransform` and `ComputeDrawnTransform`: drawn matrices made lazily and exact at any time |
| `scene-ecs:388` | code | use | Lines 2313-2321 of `OnUpdateRuntime`: the step alpha computed after the capture |
| `scene-ecs:442`, `scene-ecs:489` | figure | home | The timeline of poses, drawn time and alpha with a body (Blend), its child light (Compose) and a teleported crate (Exact); interpolation off against on as a plotted trace or a strip of frames |
| `scene-ecs:543`, `scene-ecs:546` | rule | home | Renderers draw drawn transforms, simulation never reads them, teleports break; follow moving bodies in `OnLateUpdate` with drawn positions, move carriers in fixed steps |
| `scene-ecs:582` | hands-on | home | The Spinner drawn smoothly: Blend and Compose in `GetInterpolationStats` |
| `new:19` | hands-on | home | The "trace it yourself" exercise (D27): the Spinner's child light followed with a debugger from `RenderScene::Sync`, which makes the drawn matrices first, through the proxy's `FindDrawnTransform` to `ComputeDrawnTransform`, where a Compose entry is its parent's drawn matrix times its own local transform (about 250 words). Evidence: `Strata/src/Strata/Renderer/RenderScene.cpp:316-321`, `:425`; `Strata/src/Strata/Scene/SceneInterpolation.cpp:410`, `:457-463`, `:479-495` |
| `scene-ecs:679-683` | term | home | State interpolation (the qualified entry, against the mathematical interpolation of the seed), step alpha, Blend, Compose and Exact, drawn transform, teleport and break |
| `scene-ecs:684` | term | link | nlerp, used by the pose blend of section 6; taught in `basics/math-rotations` |
| `scene-ecs:759` | open | home | The sample of the off-and-on figure is chosen when its recipe is written (`Samples/ThirdPerson` or `Samples/PhysicsPlayground`; the survey ran nothing) |
| `new:4` | not-done | home | Drawn poses for world-space game UI, editor gizmos and picking, reflection probes, fog and post-process volumes, the sky and the sun; attachments placed outside their animator's hierarchy do not follow its drawn pose; there is no cap on interpolated bodies. Evidence: `Docs/Roadmap.md:1698-1702` |
| `scene-ecs:222` | feature | link | `Scene.Timing`'s `Interpolation` field, taught as a section in `world/projects-settings` |
| `foundation:188` | feature | home | Interpolation as the foundation survey lists it (drawn transforms between the last two step poses, `m_StepAlpha`): the same mechanism as `scene-ecs:130-139`, taught once |
| `scripting:341` | concept | home | The scripting survey's concept: why a follow camera reads the drawn pose in `OnLateUpdate` (`Docs/Manual/Scripting.md:157-175`), taught once in section 9's rule for game code; `make/characters-cameras` uses it |
| `foundation:576`, `scripting:579` | term | home | The foundation survey's entry for interpolation (render) and the scripting survey's for drawn transform: one glossary entry each with `scene-ecs:679` and `scene-ecs:682` |
| `physics:159-161` | feature | home | The physics survey's rows on the same mechanism: the roles, the alpha and breaks; the readers (`GetStepAlpha`, `GetDrawnTransform`, `FindDrawnTransform`, `BreakInterpolation`, `c_MaxInterpolatedSpeed`); and the script SDK's side, named in the rule for game code (`GetDrawnPosition` and `GetDrawnRotation`, `ResetInterpolation`, `Time::GetStepAlpha`; their use home is `make/characters-cameras`) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Lerp, its weight, and blending two values | `basics/math-interpolation` | must |
| Quaternions, slerp and the shorter arc | `basics/math-rotations` | must |
| The fixed step, and interpolation in one paragraph (one step of latency) | `core/time` | must |
| The runtime frame, `OnFixedUpdate` and `OnLateUpdate` | `world/systems` | must |
| World transforms, the dirty walk and its passes | `world/scene-graph` | must |
| Floating-point spacing far from the origin | `basics/numbers` | helps |
| The render scene and its sync | `draw/render-scene` | helps |

## `world/reflection` — Reflection: one registration, many uses

**Covers.** The job: one description of each component type (its properties, its metadata and its type-erased
operations) drives files, the Inspector, commands, undo, scripts, cooking and prefab diffs, with no code generator.
Registries that open and accept, and the component and settings registries that then freeze, are
`core/layers-registries`'; this page covers `ComponentRegistry`'s builder. This page carries the full section on the
problem: C++ has no runtime reflection, and engines use macros with a code generator (Unreal's UHT), external
generators, or registration DSLs (RTTR, EnTT's meta, Hazel's style), compared in a table. The map:
`ComponentRegistry` → `ComponentInfo` → `PropertyInfo`, with the consumers drawn around them. Then, in this order:

1. Properties: `PropertyType` (14 types) and `PropertyValue` (a variant of 10 alternatives); `PropertyInfo` (name,
   display name, tooltip, section, type, flags, range, speed, asset filter, enum values, the type-erased getter and
   setter, the inactive reason that section 6 teaches); `PropertyFlags`; `PropertyOptions` (`Range`,
   `Slider`, `Color`, `WithTooltip`, `c_Unbounded`).
2. The builder: `PropertyBuilderBase` as a CRTP builder, the property's type deduced from the member pointer, `Property`,
   `EnumProperty`, `AssetProperty`, `EntityProperty`, `CustomProperty`, `Section`; `PropertyListBuilder` for structs that
   are not components (materials).
3. `ComponentInfo`: its metadata and about 20 type-erased operations; `Register<T>` fills them with lambdas, with
   `if constexpr` for tag types: the page's central mechanism. `ComponentFlags`; `ComponentInfoBuilder`'s metadata
   (`DisplayName`, `Category`, `Description`, `Flags`, `Requires`, `Extra`, `Gizmo` named, `ExtraReferences`,
   `ExtraBinary`); names compared without case, refusals that return a builder which discards, `Find`, `FindByTypeId`,
   `GetAll` in registration order; registration only while the composition root runs, so workers read the frozen
   registry without locks.
4. A real registration: the camera's, with ranges, tooltips and sections; where the Scene module registers
   (`RegisterSceneModule`: its components, two settings sections and three loaders, called second after Input); what one
   registration gives, shown in the Inspector's sections and in the Add Component menu grouped by category.
5. Validation and leniency: `PropertyInfo::SetValue` by type, enum membership, clamping, finite values, normalized
   quaternions; `IsInRange` refuses for commands; strict reads for commands against lenient reads for files (unknown
   properties and bad values become warnings, values out of range are clamped); `ComponentAccess` sets, then signals.
6. Requirements: `Requires`, and `AddWithRequirements` adding the needed components first with a guard against
   cycles; `Freeze` drops requirements that name nothing; metadata for the UI kept as data. Inactive reasons:
   `SetInactiveReason<T>(property, fn)`, called next to the property's registration while the registry is open, gives
   the property a function of the component that says why the property has no effect now ("" when it has), and refuses
   a closed registry or an unknown component or property; the rule that a property another turns off gets one, on the
   camera's registration; how the Inspector shows a reason is `editor-ui/inspectors`' (about 300 words).
7. Data that is not a property: `Extra` serializers, `ExtraReferences` for entity and asset references inside them
   (script fields), `ComponentValueArray` for components kept outside registries (prototypes), `ComponentObserver`.
8. Values as JSON: canonical JSON with the shortest floats that read back exactly, lenient parsing for agents (vectors as
   objects, Euler angles for quaternions, enums by name or number, UUID forms), the `Append` functions that need no DOM,
   `DescribeProperty` for tools.
9. `ComponentAccess`: the one validated path for reads and writes, used by the serializer, the Inspector, commands, undo
   and scripts. Engine code's typed `Entity::AddComponent` and `GetComponent` write raw, with no range, no validation
   and no `Requires`, so ranges hold only on the paths through reflection; and the newcomer's error: a field added to a
   component without being registered is not saved, not shown and out of reach of commands and scripts, and nothing
   warns (a play copy still copies it, with the whole struct) (about 80 words).

Then the alternatives, the tests (`Reflection`, `Reflection.ComponentSchema`, `Scene.InactiveProperties`), changing it
safely, and the exercise: predict, then run, a camera's `PerspectiveFOV` of 200 sent with `component.set` (refused) and
written into a hand-edited `.stscene` (clamped to 179 when the scene loads), with a trace from `component.set` to
`PropertyInfo::IsInRange`. At the end the reader can register a component with properties, ranges and metadata, and
predict what a file, a command and the Inspector each do with a value out of range.

**Leaves out.**

- Registries that open and accept, the component and settings registries that then freeze, and the composition root → `core/layers-registries`
- How the Inspector draws properties and shows an inactive reason → `editor-ui/inspectors`
- The gizmo shapes a component asks for → `gpu/debug-drawing`
- Binary property values in cooked scenes → `world/serialization`
- How commands check parameters against schemas → `editor/commands`
- Script fields and how scripts reach components → `scripting/abi-sdk`
- Type erasure and CRTP as C++ → `basics/cpp-generic`
- Adding a component from start to end → `world/tutorial-component`

**Fit.** `fits`: about 6,900 words against XL (8,000). Six excerpts, three figures, the problem section with its table
and the section on inactive reasons (about 300 words) take most of it.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `scene-ecs:155` | feature | home | Lenient reads: unknown properties and bad values become warnings, values out of range are clamped |
| `scene-ecs:189-197` | feature | home | `PropertyType` and `PropertyValue`, `PropertyInfo`, `PropertyFlags`, the builders, `PropertyOptions`, `ComponentInfo`, `ComponentFlags`, `ComponentRegistry`'s registration and lookups, `ComponentInfoBuilder` |
| `scene-ecs:199-202` | feature | home | `Requires`, `ComponentValueArray`, `ComponentExtraReferences`, `ComponentObserver` |
| `scene-ecs:204` | feature | home | Canonical JSON of values, lenient parsing for agents, shortest floats, the `Append` functions, `DescribeProperty` |
| `scene-ecs:206` | feature | home | `ComponentAccess`, the single validated read and write path; engine code's typed `Entity::AddComponent` and `GetComponent` bypass it and write raw, with no range, no validation and no `Requires` (`Entity.h:24-35`, `ComponentAccess.h:17-19`, `:38-40`) |
| `scene-ecs:228` | feature | home | `RegisterSceneModule`: components, the two settings sections, the three loaders; called second, after Input |
| `scene-ecs:198` | feature | home | `ComponentRegistry::SetInactiveReason<T>(property, fn)`, called next to the property's registration while the registry is open: the function gets the component and returns why the property has no effect in its current state, or "" when it has; false, with the reason logged, for a closed registry or an unknown component or property (`ComponentRegistry.h:249-258`, `ComponentRegistry.cpp:93-119`); with `scene-ecs:531` and `scene-ecs:654` about 300 words in section 6; how the Inspector shows a reason is `editor-ui/inspectors`' |
| `scene-ecs:203` | feature | link | `ComponentGizmo`, named as a builder call; taught in `gpu/debug-drawing` |
| `scene-ecs:331`, `scene-ecs:338`, `scene-ecs:340` | concept | home | Reflection and Strata's builder DSL, with its newcomer's error: a field added without being registered is not saved, not shown and out of reach of commands and scripts, and nothing warns; validation, ranges and leniency; requirements and metadata for the UI as data, inactive reasons among them |
| `scene-ecs:336` | concept | use | Type erasure, CRTP and `std::variant` as `basics/cpp-generic` and `basics/cpp-modern` teach them |
| `scene-ecs:392` | code | home | `Strata/src/Strata/Reflection/ComponentRegistry.h:382-476`: `Register<T>`, the central mechanism: one template fills about 15 lambdas, `if constexpr` for tags |
| `scene-ecs:393` | code | home | `Strata/src/Strata/Reflection/PropertyBuilder.h:17-65`: the type deduced from a member pointer; the CRTP builder |
| `scene-ecs:394` | code | home | `Strata/src/Strata/Scene/ComponentRegistration.cpp:153-185`: a real registration (the camera's): ranges, tooltips, sections, inactive reasons |
| `scene-ecs:395` | code | home | `Strata/src/Strata/Reflection/Property.cpp:192-286`: `PropertyInfo::SetValue`: by type, enum membership, clamping, finite values, normalized quaternions |
| `scene-ecs:396` | code | home | `Strata/src/Strata/Scene/ComponentAccess.cpp:30-96`: strict against lenient reads; the page also shows `SetProperty`, set then signal, at `ComponentAccess.cpp:117-146` |
| `scene-ecs:397` | code | home | `Strata/src/Strata/Scene/ComponentAccess.cpp:153-192`: `AddWithRequirements`, recursion with a guard against cycles |
| `scene-ecs:444`, `scene-ecs:477`, `scene-ecs:478` | figure | home | The reflection model with its consumers; the Inspector's section headings (a sun or a post-process component); the Add Component menu grouped by category |
| `new:20` | hands-on | home | The page's exercise (D27), predict then run, with its "trace it yourself": a camera's `PerspectiveFOV` (range 1 to 179) set to 200 with `component.set`, which refuses it with the range in the error, against the same value in a hand-edited `.stscene`, which loads clamped to 179 (`SetValue` clamps and succeeds, so the lenient read logs no warning for it); the trace goes from the command's handler through `ApplyComponents` to `PropertyInfo::IsInRange` (about 250 words). Evidence: `Strata/src/Strata/Scene/ComponentRegistration.cpp:156`; `StrataEditor/src/Editor/Commands/EntityCommands.cpp:721`; `StrataEditor/src/Editor/CommandUtils.cpp:580-587`; `Strata/src/Strata/Reflection/Property.cpp:136`, `:233`; `Strata/src/Strata/Scene/ComponentAccess.cpp:67` |
| `scene-ecs:447` | figure | link | The component registry's states (Closed, Open, Frozen), drawn on `core/layers-registries` |
| `scene-ecs:522`, `scene-ecs:524`, `scene-ecs:526`, `scene-ecs:528` | rule | home | Register only while the composition root runs (or through `Extra` options); never rename a registered name; choose ranges that make bad states impossible; data that is not a property describes its references |
| `scene-ecs:531` | rule | home | A property another turns off gets an `InactiveReason`, so that people and agents do not edit a value that does nothing; shown on the camera's registration (`ComponentRegistration.cpp:178-182`) |
| `scene-ecs:649-650`, `scene-ecs:653`, `scene-ecs:655-656`, `scene-ecs:658` | term | home | Reflection, property, component flags, requirement, extra data, canonical JSON |
| `scene-ecs:654` | term | home | Inactive reason: text that says why a property has no effect in the component's current state, defined in section 6 |
| `editor-ui:755-756` | term | home | The editor UI survey's entries for reflection and for `PropertyInfo` and `ComponentInfo`: one glossary entry with `scene-ecs:649`, and one for each of the two types, defined in sections 1 and 3 |
| `scene-ecs:651-652` | term | link | Type erasure and CRTP, defined in `basics/cpp-generic` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Templates, lambdas, `std::function`, type erasure, CRTP and pointers to members | `basics/cpp-generic` | must |
| `std::variant`, `std::visit`, `if constexpr`, `std::optional` and `std::string_view` | `basics/cpp-modern` | must |
| JSON, UTF-8, and numbers written as text | `basics/data-formats` | must |
| Floating point: infinities, NaN and rounding | `basics/numbers` | must |
| Registries that open and accept, the component registry that then freezes; the composition root and module registration | `core/layers-registries` | must |
| Entities, storages and the `Entity` class | `world/ecs` | must |
| Change signals, which `ComponentAccess` emits | `world/scene-graph` | helps |
| Quaternions and Euler angles | `basics/math-rotations` | helps |
| The Inspector and its Add Component menu | `start/first-game` | helps |

## `world/serialization` — Scene documents: text, streams and the cooked form

**Covers.** The job: the forms a scene takes outside memory (the JSON document, read and written as a DOM for snapshots
and small documents and as a stream for scenes, prefabs and models; the cooked binary form STSC) and how each is written
and read safely. It takes as given that an asset is named by an `AssetHandle` and read by a loader, and links forward to
`assets/loading`; loading a scene as an asset is `world/sub-scenes`'. This page carries the full section on the problem:
text against binary, a DOM against streaming, versions, forward compatibility, and bytes that do not change without a
reason, for diffs and hashes. The map: `SceneSerializer`, `SceneDocumentWriter`, `SceneDocumentReader` with its sinks,
`CookedScene`. Then, in this order:

1. What a scene file looks like: the header (`{"Strata":{"Format","Version":1}}`), the name, the settings, the entity
   count and one entity per line, shown on `Samples/OpenWorld/Assets/Scenes/Loading.stscene` against the older layout of
   `Samples/Tetris/Assets/Scenes/Main.stscene`; scene settings, and the collision layers that 0.5.0 documents still hold.
2. The DOM serializer and its three-pass read: IDs and their mapping, entities and components, then the hierarchy linked
   with a union-find: a parent that is invalid, missing or would close a cycle is dropped with a warning, the entity is
   attached at the top level, and the load goes on.
3. Unknown components kept verbatim in `UnknownComponentsComponent`, one warning per name, written back unchanged;
   keeping unknown data as a rule.
4. The streaming writer: each entity's line byte for byte what the DOM would dump; chunks of 4,096 entities serialized
   in parallel while an ordered job writes and hashes the batch before (two batches in flight); references collected;
   SHA-256 and FNV-1a hashes; cancel and progress; subsets by root; why the bytes do not depend on the number of threads.
5. The streaming reader: an event parser feeding an `EntitySink`, keys in any order, the header checked whenever it
   arrives, `MaxEntities`, cancellation and progress (`SceneReadProgress`), and a parallel read of documents of 16,384
   entities or more, by lines or by a structure scan; the sinks: `SceneBuilder` links parents once every entity exists
   (with the DOM read's rules for a bad parent) and signals last, `EntityPrototypeBuilder` builds no scene,
   `EntityColumns` parses into columns on workers.
6. Snapshots and references: `SerializeEntities` and `DeserializeEntities` with fresh UUIDs, `DuplicateEntity`, and
   `RemapEntityReferences` through reflection and `ExtraReferences`, so copies point at the copies.
7. The cooked form, STSC version 1: a 64-byte header with a CRC-32C, aligned sections (strings, scene information, IDs,
   parents, component types, one column per type, unknown components), properties through `PropertyBinary` (strings up
   to 1 MiB), extra data as binary or MessagePack; everything validated before use, the columns decoded in parallel;
   across builds, an unknown property is skipped with a warning, a property whose type changed fails the whole read
   (the JSON form only warns), and a type this build lacks is kept as an unknown component (with section 2's paths,
   about 100 words).

Then the alternatives, the tests (`Scene.Serialization`, `Scene.Documents`, `Scene.CookedScene` with its corruption
tests, `Scene.Robustness`), changing it safely, and the exercises: an `EntitySink` that counts entities per component
type without making a scene; random corruption of a cooked scene's bytes that the reader must refuse; one entity moved in
the editor, the scene saved and the file diffed; and the "trace it yourself" exercise, a hand-written document whose two
entities name each other as parents, loaded and followed from its warning back to the union-find of `LinkParents`. At
the end the reader can read a scene file, say what a build without a module does with it, and write a sink.

**Leaves out.**

- Loading a scene asset, prepared scenes and the hand-over → `world/sub-scenes`
- Instantiating a prototype into a scene → `world/prefabs`
- When the export cooks documents into packs → `assets/packs-export`
- Saves off the main thread in the editor → `editor/saving`
- Untrusted input and checksums in general → `assets/robustness`
- Hashes, checksums (CRC-32C among them), JSON and UTF-8 → `basics/bytes`, `basics/data-formats`
- Atomic writes → `core/files`
- Lenient reads of property values → `world/reflection`

**Fit.** `over`: about 6,550 words against L (5,000). XL by S2: the estimate is at L's top (6,500) and inside XL's
range (6,501 to 10,000); four exercises, four excerpts and five figures take most of it.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `scene-ecs:33` | feature | home | `DuplicateEntity`: a deep copy with fresh UUIDs, inserted after the original, references inside remapped |
| `scene-ecs:153-154` | feature | home | The DOM form and `SceneSerializer`'s functions; the three-pass read with a union-find: a parent that is invalid, missing or would close a cycle is dropped with a warning and the entity attached at the top level, and the load goes on (`SceneSerializer.cpp:509-556`, `EntitySink.cpp:85-135`) |
| `scene-ecs:156-162` | feature | home | Unknown components, the streaming writer, the streaming reader, the sinks, `SceneReadProgress`, the cooked form STSC with its reader's rules across builds (an unknown property skipped with a warning, a changed type failing the whole read, a type this build lacks kept as an unknown component: `CookedScene.cpp:381`, `:447`, `:459-476`), scene settings and the old collision layers in documents |
| `scene-ecs:205` | feature | home | `PropertyBinary`: binary property values for cooked scenes, strings up to 1 MiB |
| `scene-ecs:155` | feature | link | Lenient reads, taught in `world/reflection` |
| `scene-ecs:342`, `scene-ecs:347` | concept | home | Serialization formats and their trade-offs; references between entities and assets in data, remapped on copies |
| `scene-ecs:398` | code | home | `Strata/src/Strata/Scene/SceneSerializer.cpp:73-122`: `RemapEntityReferences`, through reflection and `ExtraReferences` |
| `scene-ecs:399` | code | home | `Strata/src/Strata/Scene/SceneDocumentWriter.h:77-94`: the writer's contract, one entity per line; with the two sample files of section 1 |
| `scene-ecs:400` | code | home | `Strata/src/Strata/Scene/SceneDocumentWriter.cpp:380-507`: `WriteEntities`, two batches: parallel serialization, ordered writing, deterministic bytes |
| `scene-ecs:401` | code | home | `Strata/src/Strata/Scene/EntitySink.cpp:397-470`: `SceneBuilder::Finish`, link once all entities exist and signal last; with the interface at `EntitySink.h:29-50` |
| `scene-ecs:449`, `scene-ecs:451`, `scene-ecs:453`, `scene-ecs:454`, `scene-ecs:493` | figure | home | The document's layout annotated, against the old layout; the streaming read and its parallel path; the write pipeline as a timeline; the cooked file's layout; a diff after one entity moved |
| `scene-ecs:548`, `scene-ecs:550`, `scene-ecs:559` | rule | home | Never a DOM of a whole document; loaders reject truncated or garbage bytes and honour cancellation, and a cooked format change extends the corruption tests; keep unknown data |
| `scene-ecs:586`, `scene-ecs:590`, `scene-ecs:605` | hands-on | home | The counting sink; the corrupted cooked scene; the diff of a saved scene |
| `new:21` | hands-on | home | The "trace it yourself" exercise (D27): a hand-written scene document of two entities that name each other as parents is loaded; the reader predicts the result (both load, the second at the top level, one warning), then follows the warning with a search or a breakpoint back to `LinkParents` in `EntitySink.cpp`, where the union-find finds both ends already connected, and to the DOM reader's third pass, which does the same (about 250 words). Evidence: `Strata/src/Strata/Scene/EntitySink.cpp:85-92`, `:130-135`, `:415`; `Strata/src/Strata/Scene/SceneSerializer.cpp:509-511`, `:556` |
| `scene-ecs:657`, `scene-ecs:659-663`, `scene-ecs:665` | term | home | Unknown component, DOM, streaming or event parser, entity sink, snapshot (the scene's meaning), cooked scene, MessagePack |
| `scene-ecs:664` | term | link | CRC-32C, the checksum of the cooked header, named in section 7; taught in `basics/data-formats` |
| `worlds-runtime:550` | term | home | Cooked documents (scenes, prefabs and models read without parsing JSON): one glossary entry with cooked scene |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| JSON, UTF-8, hashes and checksums | `basics/data-formats` | must |
| Bytes in a binary file: sizes, offsets and alignment | `basics/bytes` | must |
| Files that may be cut short; atomic writes | `core/files` | must |
| Jobs, and results kept in order from parallel work | `core/jobs` | must |
| `ComponentInfo`, `PropertyInfo`, extra data and `ExtraReferences` | `world/reflection` | must |
| The hierarchy, `RelationshipComponent` and change signals | `world/scene-graph` | must |
| Union-find (disjoint sets) | `basics/trees-graphs` | helps |
| An asset is named by an `AssetHandle` and read by a loader | `assets/loading` | helps |
| Input that cannot be trusted | `assets/robustness` | helps |

## `world/prefabs` — Prefabs: the data model

**Covers.** The job: prefabs and models as entity templates: prototypes compiled once, instantiation in slices, linked
instances with per-property overrides, and propagation of a prefab's change. The asset side is taken as given, and
keeping instances exact while editing is `editor/prefab-instances`'. This page carries the full section on the problem:
copy on place with no link, linked instances with overrides (Unity's prefabs, the defaults of Unreal's Blueprints), and
nested prefabs with variants. The map: a `.stprefab` read by `EntityTemplate` into an `EntityPrototype`, instantiated by
`ContinueInstantiation` into linked instance entities, with apply, revert and propagation drawn as arrows. Then, in this
order:

1. `EntityPrototype`: a compiled, immutable hierarchy in hierarchy order, with parent indices, one
   `ComponentValueArray` per type and the list of references between its entities; `Compile`, `FromSnapshot`,
   `Serialize`; immutable, so the loading worker and the main thread share it without locks; its own arrays because
   EnTT's pages of 1,024 waste memory in small prefabs; measured at 17 ms before and 0.3 ms after per 1,000-entity prefab.
2. Instantiation: `BeginInstantiation` and `ContinueInstantiation` in slices: checks first (capacity, collisions of kept
   IDs), then create, link, remap the references, link to the prefab, and signal every component. A slice is the part
   of a long job done in one frame: each call creates at most the entities it is given and returns, and the next frame
   goes on, so that no frame stalls (the frame's shared budget is `world/sub-scenes`').
3. `EntityTemplate` and its two kinds: `Prefab` (`.stprefab`, authored, `CreateFromEntities`, `WriteDocument`) and
   `Model` (imported, read only); `Instantiate`, `InstantiateMany`, `CompareInstance`, `GetSnapshot`; the loaders of
   Scene, Prefab and Model that the Scene module registers.
4. Linked instances: `PrefabInstanceComponent` (the prefab, the entity's template id `PrefabEntityID` in it, the version
   and hash it last took, the overrides); instance roots (a linked entity whose parent is not linked to the same prefab)
   and parts; `PrefabInstances`' operations (`ExtractTemplate`, `MakeTemplate`, `Compare`,
   `Replace` to revert, `ReplaceTemplate` to apply, `Link`, `Unpack`, `StripLinks`), and the versions and hashes they keep
   (the catch-up of outdated instances is `editor/prefab-instances`').
5. Overrides: `PrefabOverride` records (a property, an added component, a removed component, a removed entity; script
   fields as `Script` and `<Class>.<Field>`); `ComputeOverrides` as a diff of the part's JSON against the instance's,
   worked through on an example; `UpdateOverrides`; `Propagate`, which brings a prefab's change to its instances except
   their overrides; `Revert` and `ApplyToPart`. Inside the worked example of the override figure, the rules a reader
   needs to predict a change (about 150 words): entities the instance added are its own; components and entities the
   prefab added are made unless a Removed override says no; those it removed go unless the instance added them, and what
   the instance keeps below a removed entity moves up to the nearest entity that stays, keeping its place in the world;
   reverting a script field that the prefab does not store gives the class default. The root's transform and name are
   the instance's own, never overrides: left out of comparisons, kept by `Replace` and replaced by the prefab's own in
   `MakeTemplate`.
6. What Strata does not do: nested prefabs and prefab variants; a prefab made from linked entities stores no inner links.

Then the alternatives, the tests (`Scene.Prefab`, `Scene.PrefabInstances`, `Scene.PrefabOverrides`), changing it
safely, and the exercise: three instances of one prefab, one untouched, one with an overridden property, one with a
removed component; the reader predicts which values a change applied from a fourth instance reaches, checks it, and
traces `prefab.apply` to `PrefabOverrides::Propagate`. At the end the reader can predict which values a prefab's
change reaches, and instantiate a prototype from engine code without stalling a frame.

**Leaves out.**

- Apply and revert as undo steps; keeping instances exact while editing; outdated instances → `editor/prefab-instances`
- How the glTF importer makes a model → `assets/models-gltf`
- Making and placing prefabs in the editor, for game makers → `make/prefabs`
- The Inspector's prefab bar and override marks → `editor-ui/inspectors`
- Placing a prefab with its ghost → `editor/placement`
- A prefab asset's handle, references and loading → `assets/handles-meta`
- Sub-scenes, which compile a prepared scene into a prototype → `world/sub-scenes`

**Fit.** `fits`: about 4,850 words against L (5,000). Three excerpts, the worked example of the override figure with the
rules of propagation, and the exercise take most of it; the catch-up by versions and hashes is
`editor/prefab-instances`', and section 4 names it only.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `scene-ecs:57` | feature | home | `PrefabInstanceComponent`: its fields, EngineAdded, IDs and hashes as read-only properties, overrides as extra data |
| `scene-ecs:168-170` | feature | home | `EntityPrototype`; instantiation in slices; `EntityTemplate`, `Prefab` and `Model` |
| `scene-ecs:172-175` | feature | home | The three loaders; `PrefabInstances`; per-property overrides and propagation; the root's own transform and name |
| `editor-core:172-173`, `editor-core:179` | feature | home | The editor survey's rows on the same data model: the instance link and the instance root, the root's own transform and name (kept by `Replace`, replaced in `MakeTemplate`), the override API; the same as `scene-ecs:57` and `scene-ecs:173-175`, taught once in sections 4 and 5 |
| `scene-ecs:349` | concept | home | Prefabs: the approaches, Strata's compiled prototype, linked instances, overrides as a JSON diff, propagation, no nested prefabs |
| `scene-ecs:402` | code | home | `Strata/src/Strata/Scene/SceneInstantiation.cpp:95-271`: `ContinueInstantiation`, a prototype copied in slices: checks, create, link, remap, link to the prefab, signal |
| `scene-ecs:403` | code | home | `Strata/src/Strata/Scene/PrefabOverrides.cpp:158-210`: `IsRootOwn` and `CompareComponents`, two JSON component maps diffed into override records |
| `new:22` | feature | home | The rules of propagation and revert, inside the worked example of section 5 (critic-scene-ecs-4; the survey did not read `Propagate` or `Revert`): entities the instance added are its own; components and entities the prefab added are made unless a Removed override says no; those the prefab removed go unless the instance added them, and what the instance keeps below a removed entity moves up to the nearest entity that stays, keeping its place in the world; reverting a script field that the prefab does not store gives the class default (about 150 words). Evidence: `Strata/src/Strata/Scene/PrefabOverrides.h:22-28`, `:106-116`, `:118-122` |
| `new:5` | code | home | `Strata/src/Strata/Scene/EntityPrototype.h:24-50`: the prototype's contract: hierarchy order, one array per type, immutable and shared without locks, `Compile` and `FromSnapshot` |
| `scene-ecs:456`, `scene-ecs:458` | figure | home | The prefab data flow; the override computation as a worked example, the part's JSON beside the instance's and the records between |
| `new:23` | hands-on | home | The page's exercise (D27), predict then run, with its "trace it yourself": three instances of one prefab (one untouched, one that overrides a property, one with a Removed component override), and a change applied from a fourth with `prefab.apply`; the reader predicts which values reach each instance, checks them, and follows the command to `PrefabOverrides::Propagate`, called for every other instance (about 250 words). Evidence: `StrataEditor/src/Editor/EditorPrefabCommands.cpp:436`, `:556`; `Strata/src/Strata/Scene/PrefabOverrides.h:106-116` |
| `scene-ecs:564` | rule | home | The root's transform and name are the instance's own |
| `scene-ecs:566` | rule | link | The bookkeeping rule (`MarkSynced`, `PrefabSync::SetBaseline`, `UpdatePrefabOverrides`), taught in `editor/prefab-instances` |
| `scene-ecs:666-672` | term | home | Prefab, model, prototype, prefab instance (the qualified entry, against `VkInstance`, `InstanceData` and the script instance) and instance root, part, override, apply, revert, unpack and propagate |
| `editor-core:715-720`, `editor-ui:759` | term | home | The editor surveys' entries for prefab, prefab instance and instance root, override, apply, revert and unpack, and propagation: one glossary entry each with `scene-ecs:666`, `scene-ecs:669`, `scene-ecs:671` and `scene-ecs:672` (`editor-core:719`, apply, revert and unpack, is one entry with `scene-ecs:672`); template id (`PrefabEntityID`) is an entry of this page's own |
| `scene-ecs:674` | term | link | Outdated instance, defined in `editor/prefab-instances` |
| `new:6` | not-done | home | Nested prefabs and prefab variants: a prefab made from linked entities stores no inner links. Evidence: `Strata/src/Strata/Scene/PrefabInstances.h:129-130` (`StripLinks`); `StrataEditor/src/Editor/EditorAssetCommands.cpp:1185, 1216` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| JSON values and their comparison | `basics/data-formats` | must |
| Snapshots, sinks and the remapping of references | `world/serialization` | must |
| `ComponentInfo`'s type-erased copies and `ComponentValueArray` | `world/reflection` | must |
| Change signals and the hierarchy | `world/scene-graph` | must |
| Immutable data shared between a worker and the main thread | `core/jobs` | must |
| Deadlines and work time in a frame, which the slices of instantiation respect | `core/frame-loop` | helps |
| Asset handles and loaders | `assets/handles-meta` | helps |

## `world/sub-scenes` — Loading scenes: whole, additive and in slices

**Covers.** The job: loading scenes without stopping the frame (a whole scene for a switch, sub-scenes merged into a
running scene) and letting them go. Residency and pins are taken as given; `assets/residency` follows. This page carries
the full section on the problem: loading the whole level, level switches behind a loading screen, background loads with
a hand-over on the main thread, additive loads (Unity's additive scenes, Unreal's sublevels), and work cut into slices.
The map: `SceneAsset`, `SceneLoader` and its `SceneLoadRequest`, the scene's list of sub-scenes, `SceneWorkBudget`. Then,
in this order:

1. Scene assets are read once: the loader reads the document (text or cooked) into a prepared scene on the loading
   worker, computes its world transforms and estimates its memory there; `TakePreparedScene` hands the scene over
   without a copy and applies the project's collision layers and fixed rate on the main thread, because a worker never
   reads the project's settings (one sentence; the hand-over pattern is taught with the sections on
   `world/projects-settings`); `CreateScene` copies.
   The scene keeps its source asset and a lineage ID that copies share (physics remembers its capacity by it).
2. `SceneLoader::LoadAsync` and the request's states (LoadingScene, LoadingDependencies, Preparing, Ready, Failed,
   Cancelled): who calls `Update`, the dependency closure it pins (pins are `assets/residency`'; how the closure is
   fitted into each pool's budget is `assets/references`'), `RequiredProgress`, `Prepare`,
   `TakeScene` with its second hand-over, `Cancel`.
3. Prepared loads: with `PrepareSystems`, each system's `PrepareLoadedScene` works within the frame's budget while the
   request is Preparing; prepared states, the typed per-scene slots a system fills before the scene runs (physics
   bodies), so that the first frame of a scene builds nothing.
4. Asking the owner: `RequestQuit`, `RequestSceneLoad`, `TakeSceneLoadRequest` and the load progress a game shows; the
   owners that honour them are `worlds/runtime`' and `editor/play-mode`'s.
5. Letting a scene go: `ReleaseInBackground` stops it on the main thread and destroys its entities on a job.
6. Sub-scenes: `LoadSubScene` and `BeginAdditiveLoad`; the states Loading, Instantiating, Loaded, Failed and Unloading;
   the prepared scene compiled into a prototype on a job and instantiated in slices; `SubSceneComponent` on the top-level
   entities; membership (`AdoptSubScene`, `SetSubSceneOf`, `GetSubSceneOf`, `FindSubSceneBySource`, the membership
   version); unloads that deactivate at once and destroy in slices; `FlushSubSceneUnloads`.
7. The frame's work budget: `SceneWorkBudget`'s deadline and entity counts, shared by every loader of the frame;
   `FitChunk` and `RecordChunkCost`, which fit each chunk to the cost per entity measured lately.

The output of `scene.loadStatus` while a sub-scene loads is shown as a text capture, with the line to paste, one
sentence on what it does and a link forward to `editor/commands`. Then the tests (`Scene.SubScenes`, `Scene.Loader`,
`Scene.Streaming`), changing it safely, and the exercise: a doctest that sets `MaxEntitiesInstantiatedPerFrame` to 100,
loads a sub-scene of 1,000 entities and counts the updates until it is Loaded, with a trace from `scene.loadAdditive`
to `AdvanceSubScene`. At the end the reader can load a scene or a sub-scene from engine code without
a hitch and say what each frame of the load does.

**Leaves out.**

- Residency, pins and the dependency closure → `assets/residency`, `assets/references`
- How a scene load fits its closure into each pool's budget, and the members it skips → `assets/references`
- Load progress and loading screens in a game → `make/levels-saves`
- Scene switches in a shipped game → `worlds/runtime`
- Scene switches and scenes opened in the background in the editor → `editor/play-mode`, `editor/projects`
- World cells streamed as sub-scenes → `worlds/streamer`
- The World system's prepared start → `worlds/physics-scripts`
- What physics prepares and remembers for a scene → `physics/scale-streaming`
- The project's values applied at the hand-over → `world/projects-settings`

**Fit.** `fits`: about 5,350 words against L (5,000). Four excerpts, three figures (the text capture of
`scene.loadStatus` among them) and the problem section take most of it.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `scene-ecs:36-40` | feature | home | `ReleaseInBackground`; the memory estimate of a prepared scene; prepared states; the requests to the scene's owner; the source asset and the lineage ID |
| `scene-ecs:145-147` | feature | home | Sub-scenes and their states; membership; `SceneWorkBudget` and the adaptive chunks |
| `scene-ecs:171` | feature | home | `SceneAsset`: read once into a prepared scene; `TakePreparedScene` without a copy; `CreateScene` copies |
| `scene-ecs:181` | feature | home | `SceneLoader::LoadAsync` and the request's states, hooks, `TakeScene`, `Cancel` and progress |
| `scene-ecs:354` | concept | home | Loading on workers into a prepared scene, the hand-over on the main thread, preparation and sub-scenes in slices against a shared budget |
| `new:7` | code | home | `Strata/src/Strata/Scene/Prefab.cpp:347-416`: `SceneAsset::Deserialize` and `TakePreparedScene`: text or cooked, world transforms and the memory estimate on the worker, the project's values applied at the hand-over |
| `new:8` | code | home | `Strata/src/Strata/Scene/SceneLoader.cpp:219-299`: `SceneLoadRequest::Update`, the load's state machine frame by frame |
| `new:9` | code | home | `Strata/src/Strata/Scene/SceneSubScenes.cpp:364-457`: `AdvanceSubScene`: the prototype compiled on a job, then chunks within the budget and the deadline, top-level entities tagged, the cost per entity recorded |
| `scene-ecs:460`, `scene-ecs:462`, `scene-ecs:494` | figure | home | The load's state machine with who calls `Update` and where `TakeScene` applies the project's values; the sub-scene lifecycle; `scene.loadStatus` while a sub-scene loads, as a text capture |
| `scene-ecs:553`, `scene-ecs:555` | rule | home | Never block a frame on a load, load scenes that will run with `PrepareSystems`, draw from the frame's budget; load through `SceneLoader`, let go with `ReleaseInBackground` |
| `new:24` | hands-on | home | The page's exercise (D27), with its "trace it yourself": a doctest that sets the scene's `MaxEntitiesInstantiatedPerFrame` to 100 (the default is 5,000), loads a sub-scene of 1,000 entities and counts the updates until its state is Loaded (the reader predicts the count first, and explains the difference the per-frame deadline can make), then follows `scene.loadAdditive` through `Scene::LoadSubScene` to `AdvanceSubScene`, which spends the budget (about 250 words). Evidence: `Strata/src/Strata/Scene/Scene.h:70`; `StrataEditor/src/Editor/EditorSceneCommands.cpp:458`, `:281`; `Strata/src/Strata/Scene/SceneSubScenes.cpp:65`, `:354`, `:364` |
| `scene-ecs:675-678` | term | home | Prepared scene, sub-scene, work slice (the qualified entry, against the shadow cascade's and the AO's slices) and chunk, work budget |
| `worlds-runtime:78-83` | feature | home | The worlds survey's rows on the same mechanism: sub-scenes and their states, `SubSceneComponent`, `SceneWorkBudget` with its defaults (4 ms a frame, 2 ms of sub-scene work), the slice limits (5,000 entities a frame), `PrepareSystems` |
| `worlds-runtime:232`, `worlds-runtime:237` | concept | home | Loading without stopping the frame (background reads, finalization in slices, adaptive chunks, the mistake of budgeting by count only); additive scenes (Unity's and Unreal's forms, sliced unloads, IDs that must not collide) |
| `worlds-runtime:324` | code | home | `Strata/src/Strata/Scene/SceneWorkBudget.cpp:32-59`: the frame's budget and the adaptive chunk estimate (`ForFrame`, `FitChunk`, `RecordChunkCost`) |
| `worlds-runtime:423`, `worlds-runtime:425`, `worlds-runtime:434` | rule | home | Scenes that will run load with `PrepareSystems`; loading work draws from one budget per frame; unloads deactivate at once and destroy in slices (a world's reasons are named on `worlds/physics-scripts`) |
| `worlds-runtime:527-531` | term | home | Sub-scene, `SubSceneComponent`, slice (the entry work slice), scene work budget, prepared start and `PrepareSystems`: one glossary entry each with this page's own terms |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Prototypes and instantiation in slices | `world/prefabs` | must |
| The document reader, cooked scenes and read progress | `world/serialization` | must |
| Scene systems, `PrepareLoadedScene` and the runtime frame | `world/systems` | must |
| Jobs, and handing results back to the main thread | `core/jobs` | must |
| Clocks, deadlines and work time in a frame | `core/frame-loop` | must |
| The asset manager, load requests and loaders | `assets/loading` | helps |
| Residency and pins | `assets/residency` | helps |
| The project's values the hand-over applies, and the hand-over pattern (section 1 says what this page needs in a sentence) | `world/projects-settings` | helps |
| Reading a command and its JSON | `start/how-to-read` | helps |

## `world/projects-settings` — Projects and settings

**Covers.** The job: what a project is to the engine (the `.stproj` file, its folders and the `.strata/` intermediate
folder), and how settings are registered, stored, validated and handed to scenes. The manifest and the game's identity
are `worlds/game-identity`'s; the project folder for game makers is `make/project-files`'. The problem in one paragraph
(settings as code against settings as registered data; project scope against user scope). Then, in this order:

1. The project file: format 3; the layout (the asset folder, scripts, `.strata/` with `Cache`, `Scripts/Build` and
   `Scripts/Bin`) drawn as a tree; `Create`, with the rule of `Project::IsValidName` beside it (the name becomes the
   project file's name, so it is a valid file name on every platform, and `project.create` refuses other names; about 40
   words); `Load` with its 1 MiB cap, the header and version checks, the sections
   validated against a registry and unknown members kept; the script settings and the module name rule; the active
   project, and `ProjectModule`, which releases it and the asset manager at shutdown.
2. Settings sections: simple sections described by fields (Bool, Int, Float, String, Enum, Asset) and complex sections
   with a schema, a default, a read function and references; the scopes Project and User; versioned values with
   upgrades; one `Validate`; a cap of 512 KiB per value; the process registry, frozen with the components, its id rule
   `<Module>.<Name>`, and local registries for tests.
3. A complete simple section: `Scene.Timing` (`FixedRate` Scene, 30, 60, 120 or 240; `Interpolation`; at most
   `ceil(rate × 2 / 15)` steps per frame), with its description for agents and its `Find` cached by the provider's
   version, and the Project Settings page its fields make (Physics > Timing). The Scene module registers two
   sections, `Scene.CollisionLayers` and `Scene.Timing`, although the comment in `SceneRegistration.h` names one;
   Scene owns them, not Physics, because the layers' type, their parser and every reader of their names are Scene's,
   and the step drives scripts and animation as well as physics, so a build or a game without physics keeps both
   (about 40 words); the other sections are named with the pages that teach them, and the full list is
   `reference/settings`'.
4. `IProjectSettings` and `ProjectSettingsValues`: sections no module claims, and invalid ones, kept verbatim; only
   validated values provided; a version unique in the process; stored entries for undo.
5. The hand-over: scenes built on workers never read the service; the main thread applies the project's values when a
   scene is handed over and after every change; the Inspector with nothing selected shows the scene's fixed step overruled
   by the project.

Then the tests (`Project`, `Project.Settings`, `Core.Settings`), changing it safely, and the exercises: a simple section
`Game.Tuning` with an upgrade to version 2, in a local registry; a complex section that keeps a refused value verbatim;
and the "trace it yourself" exercise, `Scene.Timing`'s `FixedRate` set to 120 with `project.setSettings` while a game
plays, followed to the moment the running scene's `GetFixedTimestep` changes.
At the end the reader can add a settings section and read it correctly from a system.

**Leaves out.**

- The project folder for game makers → `make/project-files`
- The manifest and the game's identity → `worlds/game-identity`
- Export settings and `AlwaysInclude` → `assets/packs-export`
- The collision layers section and the scene's working copy → `physics/collision-layers`
- Settings windows drawn from fields; the Preferences dialog → `editor-ui/settings-windows`
- Creating, opening and migrating projects; undoable project changes → `editor/projects`
- Every section and its fields → `reference/settings`
- Building the script module the project names → `editor/script-builds`

**Fit.** `fits`: about 4,550 words against L (5,000). Three excerpts, four figures and three exercises take most of it.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `scene-ecs:212-213` | feature | home | `Project`: the file, the layout, `Create`, `Load`, `Save`, the cap, unknown members kept, the active project; the script settings and the module name rule |
| `new:25` | feature | home | `Project::IsValidName`, beside `Create` in section 1: the name becomes the project file's name, so it must be a valid file name on every platform: at most 128 bytes, none of the nine characters Windows forbids in file names (angle brackets, colon, double quote, both slashes, vertical bar, question mark, asterisk) or control characters, no space at either end, no trailing dot, no reserved device name such as CON; `Create` refuses other names, and so `project.create` does (about 40 words). Evidence: `Strata/src/Strata/Project/Project.h:83-86`; `Strata/src/Strata/Project/Project.cpp:153-165`, `:178-179`; `StrataEditor/src/Editor/EditorContext.cpp:258` |
| `scene-ecs:217-220` | feature | home | `ProjectModule`; settings sections; `SettingsRegistry`; `IProjectSettings` and `ProjectSettingsValues` |
| `scene-ecs:222-224` | feature | home | `Scene.Timing`, and why Scene, not Physics, owns it and `Scene.CollisionLayers`: a build or a game without physics keeps both (`SceneRegistration.cpp:17-22`); the other sections and where they are taught; the hand-over to scenes |
| `physics:158` | feature | home | `Scene.Timing` as the physics survey lists it: the same section as `scene-ecs:222`, taught once in section 3 |
| `foundation:131` | feature | home | `SettingsRegistry` and `ProjectSettings` as the foundation survey lists them: the same as `scene-ecs:219-220`, taught once in sections 2 and 4 |
| `scene-ecs:214-216` | feature | link | Export settings, the game's information and the manifest, taught in `assets/packs-export` and `worlds/game-identity` |
| `scene-ecs:221` | feature | link | `Scene.CollisionLayers`, the example of a complex section, taught in `physics/collision-layers` |
| `scene-ecs:362` | concept | home | Projects and settings: scopes, sections as registrations, versions and upgrades, unknown data kept, the hand-over, settings carried into exported games |
| `scene-ecs:404` | code | home | `Strata/src/Strata/Scene/ProjectSceneTiming.cpp:45-123`: a complete simple section: fields, default, description for agents, `Find` cached by the provider's version |
| `scene-ecs:405` | code | home | `Strata/src/Strata/Core/SettingsRegistry.h:45-103`: the section model, simple against complex |
| `scene-ecs:407` | code | home | `Strata/src/Strata/Project/Project.cpp:208-324`: `Project::Load`: size cap, header, versions, unknown members kept, sections validated |
| `scene-ecs:464`, `scene-ecs:466`, `scene-ecs:483` | figure | home | The project on disk as a tree, with the exported folder beside it; the settings flow from registration to the scenes; the Inspector with nothing selected, its fixed step rows marked "(project)" at a `FixedRate` of 120 |
| `new:26` | figure | home | Project Settings' Physics > Timing page: Fixed Rate (Scene, 30, 60, 120 or 240) and Interpolation with their descriptions, the page that `Scene.Timing`'s fields make, beside section 3 (critic-physics-18: the Timing page's picture comes here from `physics:374`, whose Simulation page stays on `physics/tuning`). Evidence: `Strata/src/Strata/Scene/ProjectSceneTiming.cpp:44-88`; `Strata/src/Strata/Scene/ProjectSceneTiming.h:25` |
| `scene-ecs:561` | rule | home | Read `IProjectSettings` on the main thread only and cache by version; validate only through `Validate`; never assert on a settings value |
| `scene-ecs:559` | rule | use | Keep unknown data: unclaimed sections and unknown project members are written back as read |
| `scene-ecs:587`, `scene-ecs:588` | hands-on | home | The `Game.Tuning` section with an upgrade; a complex section that keeps a refused value |
| `new:27` | hands-on | home | The "trace it yourself" exercise (D27): `Scene.Timing`'s `FixedRate` set to 120 with `project.setSettings` while a game plays, followed from the command through the project settings step, which applies the change to the edited and the running scene, to `Scene::ApplyProjectTiming`, which reads `ProjectSceneTiming::Find` (cached by the provider's version) and takes the new rate on the main thread (about 250 words). Evidence: `StrataEditor/src/Editor/EditorProjectSettingsCommands.cpp:259`; `StrataEditor/src/Editor/ProjectSettingsAction.cpp:76-78`; `StrataEditor/src/Editor/EditorContext.cpp:552-561`; `Strata/src/Strata/Scene/Scene.cpp:229-242`; `Strata/src/Strata/Scene/ProjectSceneTiming.cpp:90-97` |
| `scene-ecs:685-690` | term | home | Project, intermediate directory, settings section, simple and complex section, project and user scope, hand-over |
| `render-image:733` | term | home | The image survey's entry for a settings section, with `Renderer.Quality` as its example: one glossary entry with this page's |
| `new:10` | erratum | home | The comment of `RegisterSceneModule` names one settings section, the collision layers; the code also registers `Scene.Timing`. The page names both. Evidence: `Strata/src/Strata/Scene/SceneRegistration.h:6-8`; `Strata/src/Strata/Scene/SceneRegistration.cpp:22` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| JSON documents, and versions of a format | `basics/data-formats` | must |
| UTF-8 paths, atomic writes and files capped in size | `core/files` | must |
| Engine services and engine modules | `core/engine-modules` | must |
| Registries that open and accept, the settings registry that then freezes | `core/layers-registries` | must |
| Validation, ranges and leniency | `world/reflection` | must |
| `SceneSettings`, `GetFixedTimestep` and the runtime frame | `world/systems` | must |
| The fixed rate and interpolation as ideas | `core/time` | must |
| Scene assets handed over on the main thread | `world/sub-scenes` | helps |
| Asset handles | `assets/handles-meta` | helps |
| Undo steps | `editor/undo` | helps |

## `world/tutorial-component` — Tutorial: adding a component and a system

**Covers.** What you will make: the WindZone, the first stage of track E's running example: a component that will push
bodies with wind (`capstone/build` adds the forces), declared in the Physics module, registered with ranges, tooltips and
an enum, with a scene system that runs in fixed steps, a serialization round trip and the feature test's minimum. What
you need: the source build of `core/first-change`, the engine's own checklist (the skill `strata-add-component`), and
the time it takes. The step sections, each a stage of the page's patch, which starts from the pin:

1. Declare the data: `WindZoneComponent` in `Physics/PhysicsComponents.h`, each member with a default and a comment with
   its unit (Strength in newtons, Radius in meters, Mode Directional or Spherical); why the module's header and not
   `Scene/Components.h`; no asset property at this stage.
2. Register it: in `RegisterPhysicsComponents`, a stable name, the category Physics, a description written for people
   and agents, `Range` and `WithTooltip`, an `EnumProperty`; why a name is never renamed; build, then open the editor:
   the Add Component menu lists Wind Zone under Physics, and the Inspector clamps a negative radius (the page teaches each
   click it uses beyond `start/first-game`).
3. A system: `WindZoneSystem`, built with `MakeSceneSystemDescriptor`, overriding only `OnFixedUpdate`, registered in
   `RegisterPhysicsModule` beside the Physics system with `BeforeIfPresent = { "Physics" }` and its result checked, its
   place read in the update-order line that the engine logs at startup (`world/systems`); at
   this stage it gathers the active zones and their world transforms from the scene's cache each fixed step, writes no
   transform, and a test reads what it gathered through `GetSystem<T>`; the scene service that serves the zones it
   gathers (for the script SDK's `Wind::GetStrength`) comes on `scripting/tutorial-host-function`, and the forces on
   bodies at `capstone/build` (D38).
4. Test it: a reflection test (the properties and their ranges exist; invalid values are refused), a serialization round
   trip (every value kept; an unknown property warns; a value out of range is clamped), and the system stepped with
   `OnUpdateRuntime` in a real `Scene` (`CallsUpdate` is false; the zones are gathered), in a suite that an existing
   shard runs.
5. The feature test's minimum: an entity of `StrataTests/FeatureTest/Assets/Scenes/Feature.stscene` with every property
   at a value other than its default; the component schema snapshot written again with the test program's
   `--strata-test-helper=write-component-schema`; `ctest -L feature` and the `Architecture.Layering` check passing.

Each section ends with a checkpoint (the patch so far), and its "You should see" is build or test output shown as a
text capture. The exercise: rename the WindZone's registered name and load a scene saved before the change, predicting
first what happens. At the end the reader can add a component and a system to Strata that pass the engine's own checks.

**Leaves out.**

- Forces on bodies, the gizmo, the inactive reason, the script API and the command in one change → `capstone/build`
- Designing the WindZone as a feature: its layers and registries → `capstone/plan`
- What the feature test counts, its runners and how to extend it beyond the minimum → `engineering/feature-test`
- The WindZone's gizmo as an exercise → `gpu/debug-drawing`
- The host function `Wind::GetStrength` → `scripting/tutorial-host-function`
- The `wind.*` commands → `editor/tutorial-command`
- Every preset and option of the build → `engineering/building`

**Fit.** `fits`: about 5,150 words against L (5,000). Five step sections of two to four steps, six quoted hunks, two
pictures of the editor and the exercise.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `scene-ecs:580` | hands-on | home | The tutorial is this exercise: declare, register with ranges and tooltips, round trip, feature test; the inactive reason waits for `capstone/build`, and the WindZone needs no `Requires` |
| `scene-ecs:520` | rule | home | New components live in their module's components header, not in `Scene/Components.h` |
| `gamedev:560` | hands-on | home | The game makers' survey's form of the same exercise: a component with tooltips that give units, and the feature test's coverage |
| `new:11` | code | home | `Strata/src/Strata/Physics/PhysicsRegistration.cpp:12-27`: `RegisterPhysicsModule`, the place the WindZone's registration joins: components, a settings section, the Physics system's descriptor with a soft constraint, a profile stage and a preparation hook |
| `physics:70` | feature | use | The Physics system's registration, beside which the WindZone's system is registered |
| `scene-ecs:392` | code | use | `Register<T>` behind the registration the reader writes |
| `scene-ecs:524`, `scene-ecs:526` | rule | use | Never rename a registered name; choose ranges that make bad states impossible |
| `scene-ecs:533`, `scene-ecs:535` | rule | use | Soft constraints toward another module's system; descriptors made with `MakeSceneSystemDescriptor` |
| `scene-ecs:501` | rule | use | The transform contract: the system reads the cache and writes no transform |
| `scene-ecs:581` | hands-on | use | The Spinner's checks of order and `CallsUpdate`, which the system's test repeats |
| `new:28` | hands-on | home | The page's exercise (style.md §6.3, one to four on a tutorial; R32, D27), predict then run: a scene with a WindZone is saved, the registered name is changed in `RegisterPhysicsComponents`, and the scene is loaded again; the old name is now an unknown component, kept unchanged and written back, with one warning, and the zone has no component the system gathers; the answer ties it to the rule never to rename a registered name (`scene-ecs:524`) (about 250 words). Evidence: `Strata/src/Strata/Scene/SceneSerializer.cpp:504`; `Strata/src/Strata/Scene/EntitySink.cpp:180`; `Strata/src/Strata/Reflection/ComponentRegistry.h:242-246` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Building Strata from source, writing and running one test | `core/first-change` | must |
| A project in the editor, the Hierarchy and the Inspector | `start/first-game` | must |
| Scene systems, descriptors, soft constraints and the runtime frame | `world/systems` | must |
| Registration with ranges, tooltips and enums | `world/reflection` | must |
| Scene documents and the round trip | `world/serialization` | must |
| The world transform cache and the transform contract | `world/scene-graph` | must |
| The layer table, and which module a component belongs to | `core/layers-registries` | must |
| The feature test | `engineering/feature-test` | helps |
| Rigid bodies, which the WindZone will push | `physics/bodies-colliders` | helps |

**Starting state.** The engine at the pin (`822a7a46`), unchanged, with the source build of `core/first-change` (in phase
B the patch runner's build folder `build/docs-patch`); the page's patch starts from the pin and is the first of the
WindZone's chain. For the editor step of section 2, a project made from the Basic 3D template as `start/first-game` made
it.

**Command-only steps.** none

## Passed on

| Item | Type | To | Why |
| --- | --- | --- | --- |
| `scene-ecs:41` | feature | `assets/loading` | `Scene::GetAssetManager` is the path from scene code to the asset manager, which `assets/loading` teaches with the active manager's facade |
| `scene-ecs:58` | feature | `gpu/coordinates` | The camera's home: projection, `GetProjection` and reversed Z, its fields and inactive reasons (`process.md`, the camera note); the lookup of the primary camera stays on `world/scene-graph` |
| `scene-ecs:203` | feature | `gpu/debug-drawing` | The gizmo shapes a component asks the editor to draw belong with gizmos and debug drawing, where the WindZone gets its gizmo |
| `scene-ecs:214` | feature | `assets/packs-export` | `AlwaysInclude` and the loading scene of the export settings are the pack's and the export's (`book.md`, "The export") |
| `scene-ecs:215-216` | feature | `worlds/game-identity` | The game's information and the manifest are the game's identity (`book.md`, "The export") |
| `scene-ecs:221` | feature | `physics/collision-layers` | The project's table of collision layers and the scene's working copy have their home there; `world/projects-settings` names it as a complex section |
| `scene-ecs:235` | feature | `editor/commands` | The commands and panels that sit on scenes, prefabs and projects are the editor's command groups |
| `scene-ecs:316` | concept | `core/time` | The fixed step, the accumulator, the spiral of death and time scale have their home there; `world/systems` shows Strata's code |
| `scene-ecs:336` | concept | `basics/cpp-generic` | Type erasure, CRTP and pointers to members are taught there (its From names this concept) |
| `scene-ecs:406` | code | `physics/collision-layers` | The collision layers' bit masks and symmetric matrix are that page's subject |
| `scene-ecs:436` | figure | `core/time` | The accumulator's timeline draws the concept whose home is `core/time` |
| `scene-ecs:447` | figure | `core/layers-registries` | The component registry's states Closed, Open, Frozen (labelled so by D17) belong with the two kinds of registry taught there |
| `scene-ecs:474` | figure | `editor-ui/inspectors` | The camera's inactive properties drawn disabled with their reasons: the Inspector's subject |
| `scene-ecs:479` | figure | `editor-ui/inspectors` | The prefab bar and the override marks are drawn by the Inspector |
| `scene-ecs:482` | figure | `editor/placement` | The placement ghost is the drop and its preview |
| `scene-ecs:486` | figure | `editor-ui/settings-windows` | The Project Settings window, its generic and custom pages |
| `scene-ecs:488` | figure | `editor-ui/settings-windows` | The Preferences dialog |
| `scene-ecs:541` | rule | `core/time` | "Game time counts fixed steps, never frames" is the design decision whose home is `core/time` (`book.md`) |
| `scene-ecs:557` | rule | `assets/loading` | Goes with `Scene::GetAssetManager` |
| `scene-ecs:566` | rule | `editor/prefab-instances` | Keeping instances exact while editing is that page's (`book.md`, "Prefabs") |
| `scene-ecs:596` | hands-on | `make/transforms-units` | A solar system in the Hierarchy: local against world, for game makers |
| `scene-ecs:597` | hands-on | `make/scenes-entities` | Deactivating a parent in the editor |
| `scene-ecs:598` | hands-on | `make/scripting-scene` | Finding entities by tag from a script and destroying them |
| `scene-ecs:599` | hands-on | `make/prefabs` | Overrides, propagation, revert and unpack in the editor |
| `scene-ecs:600` | hands-on | `make/commands` | `prefab.instantiate` with many instances is a step with no menu or button |
| `scene-ecs:601` | hands-on | `make/characters-cameras` | Fixed rates and interpolation felt in play: the use home of interpolation |
| `scene-ecs:602` | hands-on | `make/characters-cameras` | A camera following a ball with its drawn position in `OnLateUpdate` |
| `scene-ecs:603` | hands-on | `make/physics` | Collision layers named and changed from a script |
| `scene-ecs:604` | hands-on | `make/levels-saves` | An additive load with a progress bar: the use home of additive loads |
| `scene-ecs:628-629` | term | `basics/math-matrices` | Local and world transform, and TRS, are defined with the mathematics |
| `scene-ecs:630` | term | `basics/math-bases` | Decomposition (of a transform) is taught from zero there (R43, R46); the definition corrected (R33, D34): recovering TRS from a matrix, which fails for zero scale and non-finite values, and shear is lost; `world/scene-graph` holds a `use` row and the engine function's behaviour in section 1 |
| `scene-ecs:637-641` | term | `core/time` | Fixed timestep, accumulator, spiral of death, time dilation, time scale and unscaled time |
| `scene-ecs:642` | term | `editor/stepping` | Stepping is the home of pausing and stepping a game |
| `scene-ecs:643` | term | `editor/play-mode` | The home of Play and Simulate |
| `scene-ecs:646` | term | `core/engine-modules` | The home of engine services |
| `scene-ecs:647` | term | `core/layers-registries` | The home of the composition root |
| `scene-ecs:648` | term | `core/map` | "Layer" is one of the four words `core/map` separates |
| `scene-ecs:651-652` | term | `basics/cpp-generic` | Type erasure and CRTP, with the concept passed there |
| `scene-ecs:664` | term | `basics/data-formats` | CRC-32C: one entry with `foundation:643` on the page that teaches checksums (R29, the merge "CRC-32C"); `world/serialization` links |
| `scene-ecs:674` | term | `editor/prefab-instances` | Outdated instances and their catch-up are that page's |
| `scene-ecs:684` | term | `basics/math-rotations` | nlerp: one entry with `animation:537` on the primer that teaches interpolating rotations (R29, the merge "nlerp"); `world/interpolation` links |
| `scene-ecs:691` | term | `physics/collision-layers` | Collision layer and collision matrix (the qualified entry, against the mathematical matrix and the CI matrix) |
| `scene-ecs:692-693` | term | `worlds/game-identity` | Game manifest and game identity |
| `scene-ecs:742` | open | `nowhere` | A surveyor's note on the releases it could not date; the release history is `appendix/history`'s, from the release notes |
| `scene-ecs:745` | open | `nowhere` | A note about files the survey did not read in full; the writers read them |
| `scene-ecs:753` | open | `nowhere` | A note about test bodies the survey did not read |
| `scene-ecs:755` | open | `nowhere` | A note that the editor side is outside the survey; the editor inventories cover it |
| `scene-ecs:758` | open | `nowhere` | A note that the survey did not inspect the feature test project; `engineering/feature-test` covers it |
| `scene-ecs:761` | open | `nowhere` | Repeats the stale comment of `scene-ecs:228`; the erratum is `new:10` of `world/projects-settings` |

## Not taken

none

## Questions for the planner

none
