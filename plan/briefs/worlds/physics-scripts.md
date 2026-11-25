# Brief: `worlds/physics-scripts`

| Field | Value |
| --- | --- |
| Title | Worlds meet physics and scripts |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `worlds/streamer`, `physics/scale-streaming`, `scripting/abi-sdk` |
| From | worlds-runtime ch. 6 (the World system, the prepared start, what a world reserves through the streamer, the cook's `MaxBodiesInRadius`, `IWorldStreaming` and the SDK's `World`, prefetch before teleport); capacity, growth and parking are `physics/scale-streaming` |
| Unit | `plan/allocation/worlds.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `worlds/physics-scripts` — Worlds meet physics and scripts

**Covers.** How a running scene drives the streamer, and what a world owes to physics and to scripts. The scene side
comes first: the two components as plain data with documented ranges (`WorldComponent` with its `DistanceScale`;
`StreamingSourceComponent` with radius, layers, priority and view bias), what `DistanceScale` leaves alone (it scales
only the layers' distances: a source with its own radius ignores it; it is read every update, and no graphics preset
sets it), their registration with the World asset's loader, and the "World" scene system with its order (after
Scripting, before Physics and Audio, soft), its profile stage `World.Streaming` registered early for perf logs, and its
place in a game frame, marked on `world/systems`' frame timeline. Then gathering sources: active sources through their
world transforms with -Z as forward, the layer list parsed to a mask with unknown names warned once, and the primary
camera when no source is active; and the idle cost of a scene without a world.

The middle is the coupling with physics, taught from the failure it prevents: a player spawned before the ground's
collision falls through. Bodies arrive with cells, so the cook measures the bodies of every cell and the most any source
can keep loaded anywhere (`MaxBodiesInRadius`, a worst-case bound that again chooses a grid scan or a list), for the
sources it counts (the enabled streaming sources saved in the persistent scene, at least one, with the largest radius
per layer and their layer masks ignored, so that sources a game spawns, sources in cells and script requests get no
room), incrementally by content stamps; the index recommends 1.25 times that, rounded up in integer arithmetic; the
streamer reserves room before it starts loads; and the prepared start loads only the `LoadBeforeStart` layers' cells
around the sources while the scene prepares, raises the physics capacity, advances within the frame's budget and leaves
the cells for the system to adopt. It loads around the sources as the persistent scene was saved, else its primary
camera, before any script runs, so a player that a script spawns or moves in `OnCreate` starts where no start cells were
waited for; Play in the editor waits for nothing and starts with the cells around the editor camera. `WaitForStartCells`
is the blocking form for tools and tests. The last third is the script side: `IWorldStreaming`, a request as a temporary
source at priority 100, the SDK's `World` and `WorldCellRequest` with their five host functions, prefetch before a
teleport on the Open World sample's `Explorer.cpp`, what `IsLoadedAround` promises (the cells are loaded) and what it
does not (a mesh collider's body may still be pending, so a raycast hit is the test of collision; the page says that
this was read in the code, not run), how long a request lasts (only `Release` or the scene stopping lets its cells go;
requests and layer toggles belong to the running scene), the editor's play copy that pins cells with unsaved edits, the
feature test's world, and the rules for scripts: cells unload with their entities' `OnDestroy` in slices, and roaming
objects belong in the persistent scene (the not-done entry: bodies do not move from cell to cell). At the end the reader
can explain why an exported world never drops its player through missing ground, read a cook's numbers, and write a
prefetch.

**Leaves out.**

- Physics capacity, growth, parking and the 1e5 m limit → `physics/scale-streaming`
- The conventions every host function follows → `scripting/host-api`
- A prefetch in a game, step by step → `make/large-worlds`
- The editor's play copy and the pins of edited cells → `editor/worlds`
- Prepared loads and the loader's states in general → `world/sub-scenes`
- The cook as a step of the export → `worlds/export`
- The evaluation that the sources feed → `worlds/streamer`
- The frame timeline with every built-in system, which this page marks → `world/systems`
- The content stamp: what it is built from and what it keeps current → `assets/importing`

**Fit.** `over`: about 7,000 words against L (5,000). The next size is XL (S2); or a split into "The World system: a
world in a running scene" (about 4,200: components, the system, sources, `IWorldStreaming`, the SDK and prefetch) and
"Worlds and physics: the cook, the reservation and the prepared start" (about 4,100), both L.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `worlds-runtime:41-42` | feature | home | `WorldComponent` (`World`, `DistanceScale` 0.1-10; the first active in hierarchy order counts) and `StreamingSourceComponent` (`Enabled`, `Radius`, `Layers`, `Priority` -100 to 100, `ViewBias` 0-1, facing -Z) |
| `worlds-runtime:313` | code | home | `Strata/src/Strata/World/WorldComponents.h:11-28`: components as plain data with documented ranges |
| `new:16` | feature | home | What `DistanceScale` does not do: it scales only the layers' streaming distances, so a source with its own `Radius` ignores it; the World system reads it every update, so a game may change it while it plays; no graphics preset sets it (critic-worlds-runtime-12). Evidence: `Strata/src/Strata/World/WorldStreamer.cpp:413-419` (`GetRadius`); `Strata/src/Strata/World/WorldStreamingSystem.cpp:159-177` (`SyncWorld`, called from `OnUpdate` at `:194-196`); `Strata/src/Strata/World/WorldComponents.h:16-17`; `git grep -n DistanceScale 822a7a46 -- Strata/src/Strata/Renderer Strata/src/Strata/Runtime` finds nothing |
| `worlds-runtime:43` | feature | home | The "World" scene system: after Scripting, before Physics and Audio (soft), Play and Simulate, the stage `World.Streaming` registered at module registration |
| `worlds-runtime:314` | code | home | `Strata/src/Strata/World/WorldRegistration.cpp:31-71`: the loader, the components with ranges and tooltips, the scene system with its order, profile stage and preparation hook |
| `worlds-runtime:357` | figure | home | The worlds overlay of `world/systems`' frame timeline (one figure, no timeline of its own, R31 and D42; critic-worlds-runtime-17): its marks, World.Streaming after the scripts and before physics, and the sub-scene slices drawing from one `SceneWorkBudget`; captured once with that figure from `world/systems`' recipe |
| `scene-ecs:433` | figure | use | `world/systems`' frame timeline, shown again here with the worlds overlay |
| `worlds-runtime:44-45` | feature | home | Source gathering with the layer mask and the camera fallback (`Strata/src/Strata/World/WorldStreamingSystem.cpp:48-71`); a scene without a `WorldComponent` costs one storage check (`WorldStreamingSystem.cpp:31-35`, `159-177`) |
| `worlds-runtime:321` | code | home | `Strata/src/Strata/World/WorldStreamingSystem.cpp:101-138`: `GatherSources`, forward as -Z of the world transform, the primary camera when no source is active |
| `worlds-runtime:261` | concept | home | Coupling streaming with physics: room for bodies, ground before the player, the cook's numbers and the reservation; the mistake of spawning before the ground has collision |
| `worlds-runtime:110` | feature | home | The cook (`world.cook`): measures changed cells on I/O jobs with the session's `WorldCookCache`, computes `MaxBodiesInRadius`, fails on shared entity IDs, warns beyond 20 km and for empty cells, writes the index (one undo step), restarts when the document changed (`StrataEditor/src/Editor/WorldCook.h:21-125`); the sources it counts (critic-worlds-runtime-5): the enabled `StreamingSourceComponent`s saved in the persistent scene, at least one, with the largest of their radii per layer and their layer masks ignored, so that sources a game spawns, sources in cells and script requests are not counted and physics grows while cells load; with the world open it also writes the scene's physics capacity (`StrataEditor/src/Editor/WorldCook.cpp:76-81`, `:311-325`; `WorldCook.h:44`, `:90-96`; `StrataEditor/src/Panels/AssetInspectorPanel.cpp:286`) |
| `worlds-runtime:265` | concept | home | Offline cooking of level metadata: the runtime decides without loading a cell; stamps make it incremental; the mistake of a stale index |
| `worlds-runtime:325` | code | home | `StrataEditor/src/Editor/WorldCook.cpp:336-394`: `ComputeMaxBodiesInRadius`, a conservative bound per layer through the keep radius, grid scan or list, times the sources, plus the persistent scene; the radii and the count of sources are those the cook read from the persistent scene's saved sources (`WorldCook.cpp:311-325`; critic-worlds-runtime-5) |
| `worlds-runtime:312` | code | home | `Strata/src/Strata/World/WorldAsset.cpp:507-511`: 1.25 times, rounded up in integer arithmetic without overflow, capped at the physics limit |
| `worlds-runtime:362` | figure | home | Physics capacity budgeting: cooked bodies per cell, the busiest neighbourhood per layer, summed, times the sources, plus the persistent scene, times 1.25, reserved before loads |
| `worlds-runtime:65` | feature | home | The streamer's reservation with a cooked index: the persistent scene, the cells held and the cells starting, through `IPhysicsCapacity::Reserve` |
| `worlds-runtime:320` | code | home | `Strata/src/Strata/World/WorldStreamer.cpp:576-599`: `ReserveBodies` from the cooked numbers before bodies arrive |
| `worlds-runtime:47-48` | feature | home | The prepared start through the `PrepareLoadedScene` hook (`WorldRegistration.cpp:67-68`), and `WaitForStartCells` for tools and tests (`WorldStreamingSystem.cpp:255-274`) |
| `new:17` | feature | home | Where the prepared start loads (critic-worlds-runtime-6): around the sources as the persistent scene was saved, else its primary camera, before any script runs; so a player that a script spawns, or moves in `OnCreate` to a position restored from a save file, starts in a place whose start cells nobody waited for. Evidence: `Strata/src/Strata/World/WorldStreamingSystem.cpp:304-307` (the sources gathered in `PrepareLoadedScene`), `:126-137` (the primary camera when no source is active); `Strata/src/Strata/Scene/SceneSystem.h:96-100` (the preparation runs before the loaded scene first runs); `Docs/Manual/Worlds.md:69-71` |
| `new:18` | feature | home | Play in the editor waits for no start cells: the play copy starts with the cells the editor has loaded around its camera, and the others stream from their saved documents (critic-worlds-runtime-6). Evidence: `StrataEditor/src/Editor/EditorContext.cpp:1382-1385`; `Docs/Manual/Worlds.md:68-69` |
| `worlds-runtime:323` | code | home | `Strata/src/Strata/World/WorldStreamingSystem.cpp:276-337`: a resumable hook, the prepared state kept on the scene, only `LoadBeforeStart` layers, the capacity raised, true when done |
| `worlds-runtime:359` | figure | home | A world's prepared start: the loading scene plays, the start scene prepares (World loads start cells, Physics builds their bodies, the renderer its proxies), the swap, streaming goes on |
| `worlds-runtime:46` | feature | home | `IWorldStreaming`: `RequestCellsAround`, `ReleaseCells`, `IsLoadedAround`, `SetLayerEnabled`, `IsLayerEnabled`, `GetStats`, `IsStreaming` (`Strata/src/Strata/Scene/SceneServices.h:466-505`) |
| `worlds-runtime:322` | code | home | `Strata/src/Strata/World/WorldStreamingSystem.cpp:194-228`: the update, and a request as a temporary source of priority 100 whose radius 0 means the cells at the point |
| `worlds-runtime:89-90` | feature | home | The SDK's `World` and `WorldCellRequest` (`StrataScriptCore/Include/StrataScript/World.h:14-78`) and the host functions `WorldRequestCellsAround` to `WorldIsLayerEnabled`, misuse reported once through `RequireWorld` (`Strata/src/Strata/Scripting/ScriptHostAPI.cpp:2652-2746`) |
| `new:20` | feature | home | How long a request lasts (critic-worlds-runtime-13): a `WorldCellRequest` is a plain ID, and only `Release` or the scene stopping lets its cells go, not the script or the object going away, so a forgotten request keeps its cells loaded; requests and layer toggles belong to the running scene, so after `Game::LoadScene` or `ReloadScene` every layer starts from `EnabledByDefault` again. Evidence: `StrataScriptCore/Include/StrataScript/World.h:14-36`; `Strata/src/Strata/World/WorldStreamingSystem.cpp:187-192` (`OnRuntimeStop`); `Strata/src/Strata/World/WorldStreamer.h:124-128`, `:207` |
| `worlds-runtime:49` | feature | home | `PinCell` on the system, which the editor's play copy calls for cells with unsaved edits (`Strata/src/Strata/World/WorldStreamingSystem.h:49-51`; the inventory's lines 278-280 do not exist) |
| `worlds-runtime:189` | feature | home | The feature test's world: `StrataTests/FeatureTest/Assets/Worlds/FeatureWorld.stworld` (Ground 32 m and Props 16 m layers of 2 × 2 cells) and `StrataTests/FeatureTest/Scripts/WorldFeatures.cpp`, which requests, toggles and releases |
| `worlds-runtime:436` | rule | home | Cells unloading destroy their entities in slices with `OnDestroy`: scripts that hold entity handles from cells expect them to go |
| `worlds-runtime:438` | rule | home | Roaming objects belong in the persistent scene; references between cells resolve only while both are loaded |
| `new:2` | not-done | home | Bodies that move from one world cell to another: a moving body unloads with the cell it loaded with. Evidence: `Docs/Releases/0.7.0.md:387` (checked again at the pin: it holds) |
| `worlds-runtime:469`, `worlds-runtime:473-477` | hands-on | home | Exercises: a streaming source on the player; prefetch before a teleport, which proves that the cells are loaded, not that the ground collides: `IsLoadedAround` reports loaded cells, a mesh collider's body stays pending until its mesh is in and its shape cooked, and a raycast hit is the test of collision (the island's ground is in the persistent scene, so the raycast of `Explorer.cpp` finds its height; critic-worlds-runtime-10 and the check below; `StrataScriptCore/Include/StrataScript/World.h:38-41`, `:53-59`; `Strata/src/Strata/Physics/PhysicsWorld.h:41-43`; `Samples/OpenWorld/Scripts/Explorer.cpp:229-235`); toggle a layer from gameplay; cook and read the numbers (`world.cook`, `world.info`, a cell moved beyond 20 km), with the page's trace it yourself (D27): a breakpoint in `ComputeMaxBodiesInRadius` while `world.cook` runs shows the radii and the count of sources the cook took from the persistent scene (`StrataEditor/src/Editor/WorldCook.cpp:311-325`) |
| `new:19` | open | home | Check: The pending window of mesh colliders. The claim: `World::IsLoadedAround` reports loaded cells, whose entities exist, while the SDK's comment says that the ground there has collision then; a mesh collider's body stays pending until its mesh data is in and its shape is cooked on a job, so a cell whose ground is a mesh collider may count as loaded before it collides, and a raycast hit is the test of collision. The engine's agents run it as a test or a run; it does not block the brief, and the page says in one sentence that the claim was read in the code, not run (R39; critic-worlds-runtime-10; the SDK's comment is on R34's list for the engine). Evidence: `StrataScriptCore/Include/StrataScript/World.h:38-41`, `:53-59`; `Strata/src/Strata/Physics/PhysicsWorld.h:41-43`, `:129-132`; `Samples/OpenWorld/Scripts/Explorer.cpp:229-235`; `Docs/Manual/Worlds.md:78-85` |
| `worlds-runtime:521`, `worlds-runtime:532-533`, `worlds-runtime:537` | term | home | Distance scale, `LoadBeforeStart`, world cook (the glossary's name, apart from the cooked asset; critic-worlds-runtime-19), `MaxBodiesInRadius` |
| `worlds-runtime:535` | term | use | The content stamp that makes the cook incremental, by name (home `assets/importing`, with `assets:145`; R31 D33) |
| `worlds-runtime:111` | feature | use | `world.cook`, `world.info` and `world.status` as text captures (home `editor/worlds`) |
| `worlds-runtime:398` | figure | use | The JSON of `world.info` and `world.cook` (home `editor/worlds`) |
| `worlds-runtime:427` | rule | use | Physics never leaves a body without collision below its growth limit (home `physics/scale-streaming`) |
| `worlds-runtime:107` | feature | link | The play copy that adopts loaded cells (home `editor/worlds`) |
| `worlds-runtime:158` | feature | link | Cooking stale worlds at export (home `worlds/export`) |
| `physics:79` | feature | use | `IPhysicsCapacity` and `Reserve` |
| `physics:82` | feature | use | Physics' sliced building in its own `PrepareLoadedScene` |
| `physics:285` | concept | use | Bodies in a streaming world, from the physics side |
| `scene-ecs:105` | feature | use | The built-in order of scene systems |
| `scripting:86` | feature | use | The ABI's world-streaming entries as the scripting inventory lists them |
| `scripting:132` | feature | home | The SDK's `World` and `WorldCellRequest` as the scripting inventory lists them (prefetch cells around a point, layers; `StrataScriptCore/Include/StrataScript/World.h`); taught with worlds-runtime:89-90 above (taken from `scripting`) |
| `gamedev:385` | code | use | `Samples/OpenWorld/Scripts/Explorer.cpp` 209-247 as the prefetch example |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The streamer: sources, wanted cells, pins, the total order | `worlds/streamer` | must |
| Physics capacity, the growth limit, `Reserve`, sliced and parallel creation | `physics/scale-streaming` | must |
| The script ABI, the host table and the SDK's classes | `scripting/abi-sdk` | must |
| Scene systems, their order and phases; scene services | `world/systems` | must |
| Prepared loads: `PrepareSystems`, `PrepareLoadedScene`, a scene's prepared state | `world/sub-scenes` | must |
| Registering components and their properties (ranges, tooltips) | `world/reflection` | must |
| World transforms and the primary-camera lookup | `world/scene-graph` | must |
| The columns of a transform matrix: translation and axes | `basics/math-matrices` | must |
| Entity destruction from scripts and `OnDestroy` | `scripting/script-system` | must |
| I/O jobs and the main thread | `core/jobs` | must |
| Host functions: `HostCall`, `ResolveContext`, misuse reported once | `scripting/host-api` | helps |
| How bodies are built from components | `physics/building-bodies` | helps |
| Running a command from a terminal (`world.cook`, `world.info`) | `start/how-to-read` | helps |
| Undo steps of commands (the cook writes the index as one) | `editor/undo` | helps |
| The content stamp: whether a stored result is still current | `assets/importing` | helps |
| The editor's play copy and its pinned cells | `editor/worlds` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `loadbeforestart` | `LoadBeforeStart` | - |
| `distance-scale` | Distance scale | - |
| `maxbodiesinradius` | MaxBodiesInRadius | - |
| `world-cook` | world cook | - |
