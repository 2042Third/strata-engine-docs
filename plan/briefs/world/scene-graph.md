# Brief: `world/scene-graph`

| Field | Value |
| --- | --- |
| Title | The scene graph: hierarchy, transforms and the transform contract |
| Kind | I |
| Size | XL |
| Tracks | E |
| Needs | `world/ecs`, `basics/math-rotations`, `core/math`, `core/jobs` |
| From | scene-ecs; home of change signals; + the primary-camera lookup (the camera itself is `gpu/coordinates`') |
| Unit | `plan/allocation/world.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `active-in-hierarchy` | Active in hierarchy | - |
| `dirty-flag` | Dirty flag | dirty mark |
| `frontier` | Frontier | - |
| `hierarchy-version` | Hierarchy version | - |
| `patch` | patch | MarkModified, `registry.patch`, `MarkModified` |
| `root-entity` | Root entity | - |
| `sibling-index` | Sibling index | - |
| `transform-contract` | Transform contract | - |
