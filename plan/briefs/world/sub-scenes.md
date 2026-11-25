# Brief: `world/sub-scenes`

| Field | Value |
| --- | --- |
| Title | Loading scenes: whole, additive and in slices |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `world/prefabs`, `world/systems` |
| From | scene-ecs §1.8, §1.11, `SceneAsset` (§1.10); worlds-runtime "Sub-scenes and the frame budget"; `SceneLoader` and its states, `PrepareSystems` and `PrepareLoadedScene`, prepared states, the hand-over, `RequestSceneLoad`, `ReleaseInBackground`, `SceneWorkBudget`; retitled, M→L; home of loading scenes (a shipped game's scene switches are `worlds/runtime`', the editor's `editor/play-mode`'s); residency and pins taken as given (`assets/residency` follows) |
| Unit | `plan/allocation/world.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `subscenecomponent` | `SubSceneComponent` | - |
| `additive-load` | additive load | - |
| `chunk` | chunk | - |
| `prepared-scene` | Prepared scene | - |
| `prepared-start` | Prepared start | `PrepareSystems` |
| `scene-work-budget` | Scene work budget | - |
| `slice-world` | Slice (world) | - |
| `sub-scene` | Sub-scene | - |
| `sub-scene-additive-load` | Sub-scene (additive load) | - |
| `work-budget` | Work budget | SceneWorkBudget |
