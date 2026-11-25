# Brief: `assets/references`

| Field | Value |
| --- | --- |
| Title | References, closures, prefetch and loading screens |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `assets/residency`, `world/serialization` |
| From | assets; home of load progress and prefetch (scene switches are `worlds/runtime`'s) |
| Unit | `plan/allocation/assets.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `assets/references` — References, closures, prefetch and loading screens

**Covers.** The job: know what each asset uses, the same way in the editor and in a game, so that loads, exports,
delete checks and prefetches follow references. The problem and how engines solve it (scan at load time, record at
import time, hand-written manifests) take a short table. The map (figure 485): the scanner (`AssetDependencies`), what
importers record (`ImportResult::References` and `Bounds`), the manager's tables of dependencies and bounds, prefetch,
group requests, and the editor's index of referencers with its searches of the engine's own documents. The contract:
references are recorded at import, or found in a document, and normalized (valid handles, each once, never the asset
itself); a new document type records its references; prefetches never evict and never chain, documents prefetch
nothing, and scenes are never prefetched; a closure has one of two scopes. A toy of about 30 lines walks a small graph
breadth first and reports a group's progress by bytes.

The real code: the scanner streams scenes, prefabs and models through `SceneDocumentReader` and collects every asset
property of every registered component and of script fields, materials' textures, controllers' clips and worlds'
cells; `NormalizeReferences`; `GetDependencyClosure` ("the list itself is the queue"; `All` for packing, `Load` stops at
other scenes); bounds known before a mesh loads, so the renderer can cull and request what is not loaded yet;
dependency prefetch when a read completes, only into headroom (`FitsPrefetchLocked`), with the measured reasons (about
25 MB more peak memory for textures, 60 to 100 MB for scenes, a world's cells held at 12.6 GB instead of 280 MB); group
loads (`AssetGroupRequest` pins its closure, and its progress by stored bytes never goes down); reading stored bytes
without loading; what a first load reads now (`EstimateFirstLoadBytes`) and how a scene load fits its closure into the
budgets with it: per pool, the closure's members load and are pinned with the scene only if all of them fit in the room
beside what is resident, else none of them, and the scene requests them itself once it runs (`GetSkippedAssetCount`), so
a load never pushes a pool past its budget; `RequiredProgress`; the trim after the switch, which spares the load's
assets; the referencer index, and the searches of changed documents after 500 ms of quiet. The script side:
`Assets::RequestLoad`, `Release` and `GetLoadProgress`. Then the alternatives, the tests (`Asset.Dependencies`,
`Asset.Groups`), and changing it safely: a new document type that does not record its references loses its assets from
pruned exports, and its deletes do not warn. Exercises: a loading screen script that shows `Assets::GetLoadProgress` as
a bar, with a link to what limits how fast it fills (`assets/uploads`); trace it yourself: a breakpoint in
`GetDependencyClosureLocked` lists a Showcase scene's closure in order and shows where the `Load` scope stops at
another scene.

**Leaves out.**

- Pins, budgets and eviction → `assets/residency`
- The scene loader and its states → `world/sub-scenes`
- Delete checks and the trash, as the editor runs them → `editor/trash-references`
- What the renderer requests and culls each frame → `draw/asset-requests`
- Prefetch before a teleport in a streamed world → `worlds/physics-scripts`
- Loading screens, as a game maker builds them → `make/levels-saves`
- Graphs and breadth-first search in general → `basics/trees-graphs`

**Fit.** `fits`: about 6,075 words against L (5,000). Three concepts, three excerpts and the features of the dependency
graph take the most words; the two editor-side features (the referencer index and the searches of changed documents)
stay, since L holds them.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `assets:318` | concept | home | Dependency graphs: scan at load, record at import, manifests |
| `assets:324` | concept | home | Prefetching without hurting, with the measured reasons |
| `assets:366` | concept | home | Bounds before load: culling and requesting meshes that are not loaded |
| `assets:116-124` | feature | home | The scanner, importer-recorded references and bounds, normalized references, dependency queries, prefetch, group loads, reading without loading, the referencer index, native documents' references |
| `assets:192` | feature | home | `EstimateFirstLoadBytes` |
| `new:34` | feature | home | How a scene load fits its closure into the budgets, about 200 words, beside `assets:121` and `assets:192`: per pool, the closure's members load and are pinned with the scene only if all of them fit in the room the budget has beside what is resident (counted with `EstimateFirstLoadBytes`); otherwise none of them load, and the scene requests them itself once it runs (`GetSkippedAssetCount`), so a load never pushes a pool past its budget; `RequiredProgress`; the trim after the switch keeps the load's assets. Evidence: `Strata/src/Strata/Scene/SceneLoader.h:31-36`, `:50-63`, `:88-92`; `Strata/src/Strata/Asset/AssetManager.h:473` (`ScheduleTrim` and what it keeps) |
| `assets:424` | code | home | `Strata/src/Strata/Asset/AssetManager.cpp:1450-1473`: the breadth-first closure and the `Load` scope |
| `assets:426` | code | home | `Strata/src/Strata/Asset/AssetManager.cpp:1567-1585`: `FitsPrefetchLocked`, headroom with saturating sums |
| `assets:442` | code | home | `StrataScriptCore/Include/StrataScript/Scene.h:18-62`: the script side, `Assets` |
| `assets:485` | figure | home | The dependency graph, closures and their scopes, prefetch edges |
| `assets:554` | rule | home | Record references for any new document type |
| `assets:559` | rule | home | Prefetches never evict and never chain; documents prefetch nothing |
| `assets:622` | hands-on | home | A loading screen with `Assets::GetLoadProgress`; it links the staging bound (`new:36`) and the budgets a game cannot raise (`new:37`) of `assets/uploads` |
| `new:35` | hands-on | home | Trace it yourself (D27): a breakpoint in `GetDependencyClosureLocked` lists a Showcase scene's closure in order (the list itself is the queue) and shows where the `Load` scope stops at another scene. Evidence: `Strata/src/Strata/Asset/AssetManager.cpp:1450-1473` |
| `assets:651-653` | term | home | Dependency (runtime), dependency closure, closure scope |
| `worlds-runtime:536` | term | home | Closure, as the worlds part words it |
| `assets:687-689` | term | home | Prefetch (of assets), headroom, group load |
| `new:13` | erratum | home | The assets inventory places the scanner at `AssetDependencies.h:349-386`, but the header has 56 lines. Evidence: `Strata/src/Strata/Asset/AssetDependencies.h:30-52` (`Scan`, `ScanDocument`, `ScanEntities`, `ReferenceList`, `ScanEntity`) |
| `assets:313` | concept | use | Pins, which group loads hold (taught in `assets/residency`) |
| `assets:109` | feature | use | Script pins (taught in `assets/residency`) |
| `scene-ecs:181` | feature | use | `SceneLoader`, which pins a scene's closure |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Residency, pins and budgets | `assets/residency` | must |
| Loading, priorities, and the read that completes | `assets/loading` | must |
| Scene documents read as streams: `SceneDocumentReader` and sinks | `world/serialization` | must |
| Asset properties of components, through reflection | `world/reflection` | must |
| Graphs and breadth-first search | `basics/trees-graphs` | must |
| C++ at the level a script calls the SDK | `basics/programming-3` | must |
| What an import records | `assets/importing` | helps |
| Loading scenes and their budget | `world/sub-scenes` | helps |
| Culling meshes the renderer has not loaded | `draw/asset-requests` | helps |
| A script's fields and its update | `scripting/script-system` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `closure-scope` | Closure scope | - |
| `dependency` | Dependency | reference (runtime) |
| `dependency-closure` | Dependency closure | - |
| `group-load` | Group load | `AssetGroupRequest` |
| `headroom` | Headroom | - |
| `prefetch-assets` | Prefetch (assets) | - |
