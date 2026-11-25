# Brief: `world/systems`

| Field | Value |
| --- | --- |
| Title | Systems, phases and fixed steps |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `world/ecs`, `basics/threads`, `core/time`, `core/engine-modules`, `core/layers-registries` |
| From | scene-ecs; `Scene` update code; the code of the fixed step, the accumulator and time dilation (the concept is `core/time`'s) |
| Unit | `plan/allocation/world.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `hard` | Hard | - |
| `scene-service` | Scene service | engine service |
| `scene-system` | Scene system | - |
| `soft-constraint` | soft constraint | - |
| `update-phases` | Update phases | - |
