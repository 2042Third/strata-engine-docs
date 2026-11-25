# Brief: `physics/building-bodies`

| Field | Value |
| --- | --- |
| Title | From entities to bodies: records, shapes, mesh colliders |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `physics/dynamics`, `world/systems`, `core/jobs`, `assets/loading` |
| From | physics ch. 5 (first half); 1.2-1.4 (records and slots, `AddColliderParts`, baked scale, shared hulls, `ApplyMass`, mesh cooking and the provider, pending and suspended bodies, change rounds); split from `physics/world-step` |
| Unit | `plan/allocation/physics.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `physics/building-bodies` — From entities to bodies: records, shapes, mesh colliders

**Covers.** The job: turn entities with a `RigidBody` and colliders into box3d bodies and shapes, and keep them in line
with every edit; the step itself is `physics/world-step`'s. The problem and how engines solve it is one paragraph that
links `physics/collision-detection` and `physics/dynamics`. The map: the layered overview (scene systems over scene
services over `PhysicsSystem`, `PhysicsWorld` and the box3d world; beside them `CharacterControllerSet`, the
`PhysicsMeshShapes` cache, `AssetMeshProvider` over the mesh geometry registry, `PhysicsTaskSystem` over the job
system); the "Physics" scene system (Play and Simulate, a soft order after Scripting, the stage `Scene.Physics`); the
world created only when the scene has physics components; box3d's limit of 128 worlds; `PhysicsRuntime`'s reference
count and its assert and log hooks; and the body records with their slots (the memory-layout figure). The contract: main
thread only; box3d IDs are never used without a validity check (shapes resolve through generation-checked slots);
kinematic bodies and the presence bodies of character controllers (the kinematic capsule each controller keeps so that
bodies land on it, `physics/character-controllers`) never recycle contacts. A toy version: a map from entity to body
rebuilt from its components. The real code in the order data flows: EnTT signals into change lists applied in rounds,
what each kind of change rebuilds, and what a rebuild keeps (a dynamic body keeps its motion, its touching pairs stay);
`FindBodyOwner`, the composition rule in code; `AddColliderParts`, which bakes scale into shapes (sphere radius by the
largest axis, capsule by the largest of X and Z, shear approximated, 1 mm minimum), shares box hulls and turns offset
triangle meshes into baked compounds; `MakeBodySetup`, which sanitizes the component's numbers, sets the material and
turns recycling off for kinematic bodies; `ApplyMass`. Mesh colliders: the non-blocking `PhysicsMeshProvider`, the
default `AssetMeshProvider` and the reader the renderer registers for it (every submesh's full-detail triangles, indexed
into the whole vertex list), so that physics reads a mesh without including the renderer; hulls and BVH meshes cooked on
jobs and cached (a hull reduced to 64 vertices, or 44, because box3d's 128 faces and edges hold no round hull of 128
vertices), the hold of the first steps (at most 10 s) until mesh floors exist, hot reload, a collider that keeps its
shape when residency unloads its mesh, and a skinned mesh's collider, which keeps its bind pose. Bodies out of the
simulation: pending bodies with their `BuildFailure`, suspended bodies with degenerate transforms, warnings once per
entity, and leaving the simulation (an inactive entity, or one pending destruction, stops colliding in that update; a
dynamic body keeps its velocities and resumes them when it comes back; its contacts end; parking is
`physics/scale-streaming`'s). Then the alternatives, how it is tested (`PhysicsTestUtils.h` and the hierarchy,
mesh-collider, lifecycle and scale suites) and changing it safely. At the end the reader can follow an entity to its
box3d body and shapes, and say why a body is pending or suspended.

**Leaves out.**

- The step: synchronization before it and write-back after it → `physics/world-step`
- Building bodies in slices and in parallel, capacities and growth → `physics/scale-streaming`
- Collision filters on the shapes → `physics/collision-layers`
- The character controllers' records → `physics/character-controllers`
- The mesh geometry registry on the asset side → `assets/models-gltf`
- Registering components with the engine → `world/reflection`

**Fit.** `fits`: about 6,450 words against L (5,000). Four excerpts with change tracking and what a rebuild keeps take
the most, then the map with its two diagrams and the mesh pipeline; with four exercises it stands 50 words under L's
top.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `physics:44-45` | feature | home | Shape building per collider (shared box hulls, values for spheres and capsules, transformed hulls, mesh shapes, baked compounds) and world scale baked into shapes |
| `physics:47` | feature | home | Mass: the shapes at density 1 give the distribution, scaled to the component's mass |
| `physics:52-54` | feature | home | Suspended bodies (degenerate transforms, zero-scaled parents), pending bodies and their `BuildFailure`, warnings once per entity and kind |
| `physics:60-64` | feature | home | Mesh colliders: the provider, `AssetMeshProvider`, cooking and its cache, the mesh wait at start, hot reload. Why hulls are reduced: box3d's hulls hold at most 128 vertices, faces and edges, and a hull of V vertices made of triangles has 2V - 4 faces and 3V - 6 edges, so a round mesh fails at 128 vertices; Strata cooks at most 64 vertices and, when box3d refuses that, 44, which any hull fits (about 80 words) |
| `render-core:112` | feature | home | The renderer's reader for the mesh geometry registry (`ReadMeshGeometry`, `Strata/src/Strata/Renderer/RendererRegistration.cpp:37-63`, registered at `:106`): a mesh's full-detail triangles for mesh colliders, so that physics never includes the renderer; the registry itself is the asset layer's seam |
| `physics:70-73` | feature | home | The "Physics" scene system, the lazy world, the 128-world limit, `PhysicsRuntime` |
| `physics:75` | feature | home | Change tracking through EnTT signals into change lists, applied in rounds before steps and queries, and what each kind of change rebuilds: a property edit rebuilds the body, a world scale change above 1e-4 (relative) rebuilds its shapes, moving or deactivating a merged collider changes its owner's shape, reparenting rebuilds only the bodies whose colliders change; what a rebuild keeps is `new:20` |
| `new:20` | feature | home | What a rebuild keeps (about 200 words, after change tracking): a dynamic body rebuilt because a property changed keeps moving as before, one that was out of the simulation resumes the motion it had, and its touching pairs stay, because contacts are tracked per pair of entities, so a rebuild sends neither End nor Begin. The joint exercise (`physics:468`) depends on this model. Evidence: `Strata/src/Strata/Physics/PhysicsWorld.cpp:2270-2287` (`GetBuildVelocities`), `:394`, `:51-55` with `:993-1000` (`HasScaleChanged`), `:2765-2769`; `StrataTests/src/Physics/PhysicsLifecycleTests.cpp:316`; `StrataTests/src/Physics/PhysicsHierarchyTests.cpp:151`, `:264`; `StrataTests/src/Physics/PhysicsBox3DBehaviorTests.cpp:297` |
| `new:21` | feature | home | A mesh collider keeps its shape when residency unloads its mesh: physics checks built colliders with `PeekMeshData`, which never loads a mesh again, and the bodies hold the cooked shape until they are rebuilt (one sentence in the mesh-collider section, about 50 words). Evidence: `Strata/src/Strata/Physics/PhysicsTypes.h:280-282`; `Strata/src/Strata/Physics/PhysicsMeshShapes.h:40-45`; `Strata/src/Strata/Physics/AssetMeshProvider.h:19-24`; `StrataTests/src/Physics/PhysicsBox3DBehaviorTests.cpp:594` |
| `physics:298` | code | home | `Strata/src/Strata/Physics/PhysicsWorld.cpp:212-226`: `FindBodyOwner`, the hierarchy rule for which entity owns a body |
| `physics:305` | code | home | `Strata/src/Strata/Physics/PhysicsWorld.cpp:1993-2049`: `MakeBodySetup`, component data to box3d definitions, sanitized; why kinematic bodies do not recycle |
| `physics:306` | code | home | `Strata/src/Strata/Physics/PhysicsWorld.cpp:2100-2112`: `ApplyMass`, mass against mass distribution, inertia scaled |
| `physics:307` | code | home | `Strata/src/Strata/Physics/PhysicsWorld.cpp:1857-1920`: `AddColliderParts`, the box, sphere and capsule parts; scale baked in, spheres by the largest axis |
| `physics:333` | figure | home | The layered overview: systems, services, `PhysicsSystem`, `PhysicsWorld`, box3d and the side boxes; who may include whom |
| `physics:359` | figure | home | Body record memory layout: records in a `std::map`, body, shape and record slots, constant-time lookups both ways |
| `physics:400` | rule | home | Main thread only: box3d's world is not thread-safe; physics parallelism is internal and deterministic |
| `physics:414` | rule | home | Kinematic and character presence bodies never recycle contacts (riders crept 0.70 m in 4 s) |
| `physics:434` | rule | home | Never use box3d IDs without validity checks; shapes resolve through generation-checked slots |
| `physics:462` | hands-on | home | Exercise: a doctest that drops a sphere and checks it rests at its radius (`PhysicsTestUtils.h`) |
| `physics:467-468` | hands-on | home | Exercises: a cylinder collider through a hull (gizmo, inspector, scale rule, tests); a hinge or distance joint as a component (lifetime, rebuild, serialization) |
| `new:14` | hands-on | home | Trace it yourself (D27): breakpoints in `FindBodyOwner` and `MakeBodySetup` while the hierarchy of `physics/bodies-colliders`' exercise (a rigid body with two child colliders, a child with its own rigid body, a lone collider) and a kinematic platform start playing: the entity each collider reports as its owner, and the branch that turns contact recycling off for the kinematic body. Evidence: `Strata/src/Strata/Physics/PhysicsWorld.cpp:212-226`, `:2032-2039` |
| `physics:527-528` | term | home | Terms: degenerate transform, suspended body |
| `physics:531-533` | term | home | Terms: body record, slot, cooking, mesh provider |
| `physics:35` | feature | use | The composition rule, now in code |
| `physics:42-43` | feature | link | How bodies follow moved entities, linked to `physics/world-step` |
| `physics:76` | feature | use | The general rule of leaving the simulation, beside suspended and pending bodies (about 120 words): an inactive entity, or one pending destruction, stops colliding in that update; a dynamic body keeps its velocities (`SaveVelocities`) and resumes them when it comes back, also after a rebuild; its contacts end. Parking, the rest of the item, is taught on `physics/scale-streaming` |
| `physics:80` | feature | link | Parallel creation of large rounds, linked to `physics/scale-streaming` |
| `physics:82` | feature | link | Sliced building for loaded scenes, linked to `physics/scale-streaming` |
| `animation:158` | feature | link | One sentence in the mesh-collider section: a skinned mesh's mesh collider keeps its bind pose (the pose is drawn, not collided), linked to `animation/skinning` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Scene systems, their order and scene services | `world/systems` | must |
| Change signals and the transform contract | `world/scene-graph` | must |
| The job system and deterministic parallel work | `core/jobs` | must |
| Asking for an asset without waiting for it | `assets/loading` | must |
| Decomposing a matrix into translation, rotation and scale | `basics/math-bases` | must |
| Body types, colliders and the composition rule | `physics/bodies-colliders` | must |
| Mass and the inertia tensor | `physics/dynamics` | must |
| Registries and the composition root | `core/layers-registries` | helps |
| Asserts, verifies and errors returned | `core/conventions` | helps |
| Ordered maps and stable references to their nodes | `basics/trees-graphs` | helps |
| The mesh geometry registry (physics reads a mesh's triangles without the renderer) | `assets/models-gltf` | helps |
| Writing and running one doctest case | `core/first-change` | helps |
| A character controller's presence body (glossed in one clause with a link forward) | `physics/character-controllers` | helps |
| Running a debugger on a test or the editor | `core/debugging` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `body-record` | Body record | - |
| `cooking` | Cooking | - |
| `degenerate-transform` | Degenerate transform | - |
| `mesh-provider` | Mesh provider | - |
| `suspended-body` | Suspended body | - |
