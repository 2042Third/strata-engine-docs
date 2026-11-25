# Brief: `physics/world-step`

| Field | Value |
| --- | --- |
| Title | Inside `PhysicsWorld`: one step |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `physics/building-bodies`, `world/interpolation` |
| From | physics ch. 5 (second half); 1.5 (`Simulate`, sync, forces and teleports, the characters' step, events per step, the write-back bitmap, parallel write-back, the task system, determinism) |
| Unit | `plan/allocation/physics.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `physics/world-step` — Inside `PhysicsWorld`: one step

**Covers.** The job: run one fixed step of a world and bring its results back to the scene. `world/systems`' frame
timeline, with the physics overlay, places the work (changes applied in `OnUpdate`, zero or more steps in
`OnFixedUpdate`, events dispatched after each). The problem section is one paragraph that links `physics/dynamics`. The
map: the flow chart inside a fixed step (`ApplyChanges`, growth, parked disables, the mesh hold, sync, the characters'
step, `CollisionSteps` box3d steps of 4 sub-steps with forces applied again before each and events read after each,
write-back, pair upkeep, instruments) and "two copies of the truth" (entity transforms and body poses, who writes which
and when). The idea that every engine with a physics library faces, synchronizing physics and the scene graph, is taught
here: before the step entity to body (only what was signalled or is awake), after it body to entity (only what moved,
parents first). The contract: signal transform writes, because sleeping and static bodies are never polled; `Teleport`
for instant moves; forces in `OnFixedUpdate`, every step they should act. A toy version: a step loop with sync, step and
write-back. The real code in data-flow order: `PhysicsSystem::OnUpdate` and `OnFixedUpdate`; `Simulate`; `SyncBody`
(kinematic bodies reach their target in one step and stop there, dynamic bodies moved from outside are teleported
keeping their velocity, a moved static body wakes what rests on it); the write-back: `MarkMoved`'s bitmap and the
ordered list it gives, so that ordering costs what moved; `WritePose` relative to the parent with the authored scale
kept, in parallel chunks with parents first, and `MarkTransformsChanged` without `on_update`; forces queued and impulses
at once; `Teleport` (body and entity at once, neighbours woken, interpolation broken); gravity from the scene's
settings; `PhysicsTaskSystem`, where the waiting thread runs a task no worker has started. Determinism as the second
idea: the same results with any number of threads (ordered records, fixed chunks, integer settling sums), checked by
twin runs and box3d's golden hash. Last, the script face of bodies: the map of the SDK's physics classes (`RigidBody`,
`Physics`, `RaycastHit`, `Collision`, `CharacterController`, `GroundState`), then velocities, forces, impulses, torque
and `Teleport` from a script, through the host functions and the SDK's `RigidBody` and `Physics` (queries, contacts,
characters and layers show their own functions on their pages); what a script cannot call (`IsSleeping`, `WakeUp`,
`SetGravityScale` and a point's velocity, which the services have and the SDK does not) and what a change of the
RigidBody component's properties through `Entity::SetProperty` costs: a rebuild of the body. Then the alternatives, how
it is tested and changing it safely. Exercises: trace one step in Tracy and give its time to sync, library and
write-back; run a pile with 0 and 3 workers and compare the poses.

**Leaves out.**

- The contact events read after each box3d step → `physics/contacts-triggers`
- The characters' step → `physics/character-controllers`
- Growth and parked disables inside the step → `physics/scale-streaming`
- The scene's fixed-step loop and drawn transforms → `world/systems`, `world/interpolation`
- How the host API works → `scripting/host-api`
- Every script function → `reference/script-api`

**Fit.** `over`: about 6,950 words against L (5,000). Seven excerpts with the write-back, two ideas from zero, four
diagrams and the script face with its map of the SDK's classes pass L's top; XL (8,000) by S2.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `physics:42-43` | feature | home | Kinematic bodies follow their entity by a target velocity reached in one step; dynamic bodies moved from outside are teleported; moved static bodies wake what rests on them |
| `physics:74` | feature | home | `PhysicsTaskSystem`: box3d's step tasks on the job system |
| `physics:89-95` | feature | home | `OnFixedUpdate`, `Simulate`, synchronization before the step, write-back after it, forces and impulses, `Teleport`, gravity |
| `physics:149` | feature | home | Determinism with any number of threads, and its tests |
| `physics:177` | feature | home | The script face of physics: the host functions of bodies, queries, characters, layers and drawn transforms, the SDK's `RigidBody` and `Physics`; bodies are taught here, the rest on their pages |
| `scripting:125` | feature | home | The SDK's `RigidBody`, `Physics`, `RaycastHit` and `Collision`, one entry with their twin `physics:177`: the classes a script holds, named as one map; the bodies' functions are shown here, `Physics`' queries and `RaycastHit` on `physics/queries`, `Collision` on `physics/contacts-triggers` |
| `scripting:126` | feature | home | The SDK's `CharacterController` and `GroundState`, one entry with their twin `physics:177`: named in the same map; their functions are shown on `physics/character-controllers` |
| `new:29` | feature | home | In the script face of bodies (about 60 words): the SDK's `RigidBody` has no `IsSleeping`, `WakeUp`, `SetGravityScale` or point velocity, although the services have them; a script changes body settings (type, mass, friction, layer) through the RigidBody component's properties (`Entity::SetProperty`), and each such change rebuilds the body. Evidence: `StrataScriptCore/Include/StrataScript/Physics.h:38-43`; `StrataScriptCore/Include/StrataScript/ScriptABI.h:400-419`; `Strata/src/Strata/Scene/SceneServices.h:113-157`; `git grep -n -e IsSleeping -e WakeUp -e SetGravityScale -e PointVelocity 822a7a46 -- StrataScriptCore` finds nothing (run at the pin); `StrataTests/src/Physics/PhysicsLifecycleTests.cpp:316` (a property edit rebuilds the body) |
| `physics:267` | concept | home | Synchronizing physics and the scene graph: two copies of the truth, who writes when, signals, parents first, only what is awake costs |
| `physics:279` | concept | home | Determinism: same input, same output, with threads; what box3d's cross-platform claim covers and what Strata checks |
| `physics:300` | code | home | `Strata/src/Strata/Physics/PhysicsSystem.cpp:158-177`: what one frame and one fixed step of the physics system do |
| `physics:301` | code | home | `Strata/src/Strata/Physics/PhysicsWorld.cpp:4973-5078`: `Simulate`, the anatomy of a step (long: walked in parts) |
| `physics:302` | code | home | `Strata/src/Strata/Physics/PhysicsWorld.cpp:3300-3421`: `SyncBody`, static against kinematic against dynamic, wake rules, degenerate transforms |
| `physics:303` | code | home | `Strata/src/Strata/Physics/PhysicsWorld.cpp:4144-4179`: `WritePose`, the pose written relative to the parent, scale kept |
| `physics:304` | code | home | `Strata/src/Strata/Physics/PhysicsWorld.cpp:3627-3637`: `MarkMoved`, with the list it gives at `PhysicsWorld.cpp:4208-4229`; a bitmap whose ordering costs what moved |
| `physics:319` | code | home | `Strata/src/Strata/Physics/PhysicsTaskSystem.cpp:14-49`: a library's task callbacks on an engine's job system; the waiting thread runs the task |
| `physics:323` | code | home | `StrataTests/src/Physics/PhysicsSimulationTests.cpp:821-839`: twin runs, with and without three workers, must be identical |
| `physics:338` | figure | home | The physics overlay of `world/systems`' frame timeline (one figure, no timeline of its own, R31): its three marks, where physics applies changes, steps and dispatches; captured once with that figure from `world/systems`' recipe |
| `scene-ecs:433` | figure | use | `world/systems`' frame timeline (`OnUpdate` of every system, 0 to N fixed steps with the accumulator, `OnLateUpdate`, render), shown again here with the physics overlay |
| `physics:340` | figure | home | Inside a fixed step: the flow chart of `Simulate` |
| `physics:343` | figure | home | Two copies of the truth, with `MarkModified` and `MarkTransformsChanged` |
| `physics:361` | figure | home | Parallel write-back: the main thread lists, jobs write in chunks, the main thread finishes |
| `physics:389` | rule | home | Signal transform writes: sleeping and static bodies are never polled |
| `physics:392` | rule | home | Use `Teleport` for instant moves: a transform write moves the body only at the next step |
| `physics:394` | rule | home | Apply forces in `OnFixedUpdate`, every step they should act |
| `physics:464` | hands-on | home | Exercise (trace it yourself): one fixed step in Tracy, its time split into sync, library and write-back |
| `physics:469` | hands-on | home | Exercise: a pile with 0 and 3 workers, poses compared |
| `physics:498` | term | home | Term: collision step |
| `physics:524-525` | term | home | Terms: write-back, synchronization |
| `physics:539` | term | home | Term: golden hash |
| `physics:311` | code | link | `ProcessStepEvents`, named where `Simulate` reads each box3d step's events; walked on `physics/contacts-triggers` |
| `physics:137` | feature | link | The characters' step inside `Simulate` |
| `scene-ecs:107` | feature | use | The scene's fixed-step loop that calls `OnFixedUpdate` |
| `scene-ecs:80` | feature | use | `MarkTransformsChanged`: dirty without `on_update`, so physics does not hear its own write-back |
| `scene-ecs:137` | feature | use | Breaking interpolation on a teleport |
| `build-test:99` | feature | use | box3d's determinism scenario, the golden hash's source |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The fixed step, the accumulator and time dilation | `core/time` | must |
| The scene's fixed-step loop in code | `world/systems` | must |
| Drawn transforms and breaking interpolation | `world/interpolation` | must |
| Change signals, `MarkTransformChanged` and the transform contract | `world/scene-graph` | must |
| The job system, ordered records and fixed chunks | `core/jobs` | must |
| Bits, masks and counting trailing zeros | `basics/numbers` | must |
| Records, slots and how bodies are built | `physics/building-bodies` | must |
| Integration, contacts and sleep | `physics/dynamics` | must |
| Tracy and profile scopes | `core/profiling` | helps |
| The host API behind the script SDK | `scripting/host-api` | helps |
| Writing and running one doctest case | `core/first-change` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `collision-step` | Collision step | - |
| `golden-hash` | Golden hash | - |
| `synchronization` | Synchronization | sync |
| `write-back` | Write-back | - |
