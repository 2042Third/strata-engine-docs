# Brief: `physics/scale-streaming`

| Field | Value |
| --- | --- |
| Title | Physics at scale and in streaming worlds |
| Kind | I |
| Size | M |
| Tracks | E |
| Needs | `physics/world-step`, `world/sub-scenes` |
| From | physics ch. 11; 1.4 (capacities and growth, `Reserve`, sliced and parallel creation, parking, the 1e5 m limit); what a world reserves and `MaxBodiesInRadius` are `worlds/physics-scripts`' |
| Unit | `plan/allocation/physics.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `physics/scale-streaming` — Physics at scale and in streaming worlds

**Covers.** The job: keep physics fast and never unsafe when bodies number in the hundreds of thousands and arrive or
leave with streamed parts of a world. The problem and how engines solve it, taught here in full: capacities and memory
(pools sized in advance against growth, reserving ahead of what streams in, a growth limit as a cap on memory) and
bodies in a streaming world (building them in slices while a scene loads, creating many in parallel, and spreading the
cost of removal). The map: `IPhysicsCapacity` and `Reserve` (which the world streamer calls for cells about to load),
the loaded scene's prepared world, growth inside the step, parked bodies. The contract: never let a body sit without
collision below the growth limit (box3d grows in place; only at the limit do bodies wait, in order, in a queue that no
step polls); stay within 20 km of the origin, because box3d refuses coordinates beyond 1e5 m. A toy version: a pool that
doubles up to a cap, with a queue of waiters. The real code: `ResolveCapacities` and `GrowRoom` (automatic room at the
next power of two of twice the bodies, at least 1,024; two contacts a body; the reserve at creation capped; growth that
doubles up to the limit; the demand remembered for the scene's next world), and beside them a scene's own capacity,
`SceneSettings::PhysicsCapacity` (`MaxBodies` and `MaxContactConstraints`, 0 for automatic, at most 2^21 and 2^19, set
with `scene.setSettings {physicsCapacity}`, winning over the defaults; `maxBodyPairs` ignored since 0.5.0);
`EstimateReservedBytes`, fitted to box3d's own counts; parallel creation for rounds of 256 bodies or more with IDs that
do not depend on the threads; static shapes made before the first step that skip the pair search; sliced building for
loaded scenes (8,192 owners a slice, adopted when the scene starts); parking (`ParkStaticBody`, `DisableParkedBodies`:
an empty filter at once, `b3Body_Disable` 60 steps later, at most 1,024 a step); bodies beyond 1e5 m that wait like
degenerate ones. The figures of capacity growth and of the parking timeline. What Strata does not do: bodies farther
than 1e5 m. Then the alternatives, how it is tested (the capacity and prepare suites, and the perf tests that create
100,000 static bodies and grow to 65,536) and changing it safely. At the end the reader can size a world for a streamed
level and explain why removing a cell's bodies is spread over steps.

**Leaves out.**

- What a world reserves through the streamer, the cook's `MaxBodiesInRadius`, prefetch before a teleport →
  `worlds/physics-scripts`
- Loading scenes in slices in general → `world/sub-scenes`
- Why worlds stay within 20 km → `worlds/why-streaming`
- Measuring the cost of creation with the perf tests → `physics/tuning`

**Fit.** `over`: about 4,800 words against M (3,000). Two ideas from zero, two excerpts with the scene's own capacity,
eight features and two figures pass M's top; L (5,000) by S2.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `physics:51` | feature | home | The coordinate limit of 1e5 m: bodies beyond it wait like degenerate transforms |
| `physics:76-82` | feature | home | Parking, the bulk of `physics:76` (static bodies without contacts get an empty filter at once and are disabled 60 steps later, 1,024 a step; the general rule of leaving the simulation is used on `physics/building-bodies`); capacities and growth; `EstimateReservedBytes`; `IPhysicsCapacity` and `Reserve`; parallel creation; static shapes that skip the pair search; sliced building |
| `physics:283-285` | concept | home | Scale and memory: capacities and growth; bodies in a streaming world |
| `new:26` | feature | home | A scene's own physics capacity, one paragraph beside `ResolveCapacities` (about 100 words): `SceneSettings::PhysicsCapacity` (`PhysicsCapacitySettings`) with `MaxBodies` and `MaxContactConstraints`; 0 means automatic; the limits are 2^21 and 2^19; `scene.setSettings {physicsCapacity}` sets them, and they win over the defaults; `maxBodyPairs` has been read and ignored since 0.5.0, with a warning. Evidence: `Strata/src/Strata/Scene/Scene.h:42-59`, `:66`; `Strata/src/Strata/Physics/PhysicsSystem.cpp:528-537`; `StrataEditor/src/Editor/EditorSceneCommands.cpp:62-92`, `:587` |
| `physics:320` | code | home | `Strata/src/Strata/Physics/PhysicsWorld.cpp:1530-1582`: `ParkStaticBody` and `DisableParkedBodies`, an expensive removal spread across steps |
| `physics:321` | code | home | `Strata/src/Strata/Physics/PhysicsWorld.cpp:4775-4787`: `ResolveCapacities`, with `GrowRoom` at `PhysicsWorld.cpp:2300-2316`; sizing pools, growing by doubling, remembering demand |
| `physics:356-358` | figure | home | Capacity growth (room over time, the growth limit, the waiters, demand for the next play); the parking timeline (filters emptied at step S, disables in slices from S + 60) |
| `physics:416-417` | rule | home | Stay within 20 km (box3d refuses 1e5 m); never let a body sit without collision below the growth limit |
| `worlds-runtime:427` | rule | home | The same rule as the worlds inventory states it: no body without collision below the growth limit, and bodies at the limit wait in a queue that no step polls; reserving from the cook's counts is `worlds/physics-scripts`' |
| `physics:529-530` | term | home | Terms: parked body, capacity, room, growth limit, demand |
| `worlds-runtime:538-539` | term | home | Terms: physics capacity, growth limit, as the worlds inventory defines them (the same entries as `physics:530`) |
| `new:6` | not-done | home | Bodies farther than 1e5 m from the origin: they wait. Evidence: `Strata/src/Strata/Physics/PhysicsWorld.cpp:71-73` (`c_MaxBodyCoordinate`) |
| `new:19` | hands-on | home | Exercises (D27): a doctest after the test `At its growth limit a full world keeps bodies waiting`: a scene whose `PhysicsCapacity.MaxBodies` is 1,024, a `PhysicsSettings::GrowthLimit` of 2,048 set through `ScopedPhysicsSettings`, and 3,000 boxes; after the first step, `PhysicsStats`' `GrowthCount`, `BodyOverflowCount` and `PendingBodyCount` predicted and read; then 1,000 boxes destroyed, and the waiting ones built in the order they started waiting (done). Breakpoints in `ParkStaticBody` and `DisableParkedBodies` while an entity holding 2,000 static boxes is deactivated and stays inactive: the step their filters empty, then, 60 steps later, box3d's disables, at most 1,024 a step (trace). Evidence: `StrataTests/src/Physics/PhysicsCapacityTests.cpp:232-262`, `:459`; `Strata/src/Strata/Physics/PhysicsTypes.h:53-54`, `:157`, `:169`, `:200`; `StrataTests/src/Physics/PhysicsTestUtils.h:206-218`; `Strata/src/Strata/Physics/PhysicsWorld.cpp:64-65`, `:1530-1582` |
| `physics:171` | feature | link | Contact storage growth counting, read on `physics/tuning` |
| `scene-ecs:38` | feature | use | Prepared states: the slot a loaded scene's physics world waits in |
| `worlds-runtime:65` | feature | link | The world streamer's physics reservation |
| `worlds-runtime:325` | code | link | The cook's `ComputeMaxBodiesInRadius` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Loading scenes in slices: `PrepareLoadedScene`, prepared states and the frame's `SceneWorkBudget` | `world/sub-scenes` | must |
| Floating-point precision far from the origin; powers of two | `basics/numbers` | must |
| Queues | `basics/data-structures` | must |
| The job system and deterministic parallel work | `core/jobs` | must |
| One step and its order | `physics/world-step` | must |
| Records, slots and change rounds | `physics/building-bodies` | must |
| The broad phase's trees and the pair search | `physics/collision-detection` | must |
| The world streamer and its cells | `worlds/streamer` | helps |
| Writing and running one doctest case | `core/first-change` | helps |
| Running a debugger on a test or the editor | `core/debugging` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `capacity` | Capacity | growth limit, Physics capacity |
| `parked-body` | Parked body | - |
