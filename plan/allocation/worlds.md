# Allocation: worlds

## `worlds/why-streaming` — Why levels must stream

**Covers.** The page opens on the Open World sample's island, the part's running example: a world of 97 cells in three
64 m layers (Vegetation streams within 192 m, Wildlife within 128 m, Landmarks within 320 m), of which only the cells
near the player are in memory; the Streaming panel's cell map shows them come and go as the player walks. It then asks
what a level costs while it is loaded: its entities, the assets they reference, RAM, VRAM and the work of every frame.
The naive answer, loading the whole level, breaks once a level outgrows memory or its load time. The idea follows in
one diagram: a world is a persistent scene that never unloads, plus cells of layers, each cell a scene of its own that
loads around streaming sources. The approaches table compares the whole level, level switches behind a loading screen,
hand-placed streaming volumes and sublevels, and automatic grid partitioning (Unity's additive scenes, Unreal's level
streaming and World Partition), with their cost, quality, complexity and who uses them. Strata's choice: all three ways
to hold a level exist (a scene switch, sub-scenes, worlds), and a world is a uniform grid per layer whose cells stream
around sources, decided from a cooked index without loading a cell. A `:::why` gives the reason: decisions stay cheap,
deterministic and testable, and the grid needs no hand-placed volumes.

The second half is what the choice cannot do. Floating-point range is taught from the spacing of float32 values (about
2 mm up to 32 km, 4 mm up to 65 km, computed in a chart with 20 km marked) to the jitter of a 100 km map. One sentence
names the answers engines use (origin rebasing, double-precision positions, camera-relative rendering) and links
`draw/mirrors-camera-relative`, which compares them; this page keeps what belongs to the world, Strata's choice: float32
scenes and physics, camera-relative rendering, and a supported extent of 20 km that the `World.Coordinates` tests and
the cook's warning hold the engine to. Then what is not drawn: Strata has no HLOD, so distant cells are absent and fog
and the far plane must match the streaming distances. The not-done paragraph names worlds beyond 20 km, HLOD and origin
rebasing, and links `appendix/not-in-strata`. Common mistakes: thinking that streaming means textures only, and building
a map far beyond 20 km. At the end the reader can say what a world, a persistent scene, a layer and a cell are, why
Strata streams by a grid, and what limits a world's size; the exercises compute the spacing of float32 values in a
sketch and design origin rebasing and HLOD on paper.

**Leaves out.**

- Loading scenes additively, in slices, within the frame's work budget → `world/sub-scenes`
- The World document, the grid arithmetic and the cell keys → `worlds/grids`
- How the streamer decides which cells load and when they unload → `worlds/streamer`
- Building a world in the editor, step by step → `make/large-worlds`
- Editing a streamed world: the edit layer, the cell map, saving cells → `editor/worlds`
- Floating point from zero → `basics/numbers`
- The approaches to precision far from the origin compared (origin rebasing, double positions, camera-relative rendering), and camera-relative rendering in the renderer → `draw/mirrors-camera-relative`
- Physics' own 1e5 m limit on bodies → `physics/scale-streaming`
- Level switches in a shipped game → `worlds/runtime`

**Fit.** `fits`: about 3,600 words against M (3,000). The approaches to holding a level with their table and Strata's
choice, and the precision section with its chart and guards, take the most words; three exercises close the page.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `worlds-runtime:227` | concept | home | What a level is in memory and why it must be bounded; whole level, level switches and seamless streaming; Strata has all three; the mistake that streaming means textures only |
| `worlds-runtime:185` | feature | home | The Open World sample as the part's running example, checked at the pin: `Samples/OpenWorld/Assets/Worlds/Island.stworld` (97 cells; layers Vegetation 192 m and Landmarks 320 m with `LoadBeforeStart`, Wildlife 128 m; a cooked index with `MaxBodiesInRadius` 9161), the source on the player, `Scripts/Explorer.cpp` (prefetch), `Scenes/Loading.stscene` with `Scripts/LoadingScreen.cpp`, the regression `StrataTests/Editor/OpenWorldCommands.json.in` |
| `worlds-runtime:346` | figure | home | World anatomy: the persistent scene with its `WorldComponent`, the World asset (layers, cells, index) and the cell files on disk (`Worlds/Island/<Layer>/<X>_<Z>.stscene`) |
| `worlds-runtime:268` | concept | home | Floating-point range: float32 spacing against distance and the jitter of a 100 km map; the approaches engines use named in one sentence that links `draw/mirrors-camera-relative`, which compares them (critic-worlds-runtime-8); what this page keeps: Strata's choice, what stays float32 (scenes, physics), the 20 km limit with its guards, and the mistake of a 100 km map |
| `worlds-runtime:383` | figure | home | Chart of float32 spacing from 1 km to 100 km with 20 km marked (computed data, dataviz rules) |
| `worlds-runtime:422` | rule | home | Worlds stay within 20 km of the origin (`WorldData::c_SupportedExtent`, `Strata/src/Strata/World/WorldAsset.h:87-89`) |
| `worlds-runtime:118` | feature | home | The precision guard: `World.Coordinates` (`StrataTests/src/World/WorldCoordinatesTests.cpp:81-160`: a world 20 km out streams, its bodies rest and are hit) and the editor's rays 20 km out (`StrataTests/src/Editor/EditorWorldTests.cpp:1416-1450`); the cook warns beyond 20 km |
| `worlds-runtime:272` | concept | home | Nothing is drawn beyond the loaded cells: HLOD and impostors in other engines; match fog and the far plane to the streaming distances |
| `new:1` | not-done | home | Worlds beyond 20 km from the origin, HLOD (distant cells are not drawn) and origin rebasing. Evidence: `Docs/Releases/0.7.0.md:386, 414`; `Docs/Roadmap.md:1693, 1706` (checked again at the pin: it holds) |
| `worlds-runtime:498`, `worlds-runtime:500` | hands-on | home | Exercises: design origin rebasing on paper; sketch HLOD for Strata (where a far version per cell would live and how it swaps) |
| `new:13` | hands-on | home | Exercise (D27), done on the workbench: a sketch prints the spacing of float32 values at 1, 20 and 100 km with `std::nextafter`, checks the chart's points, and finds where the spacing doubles from about 2 mm to about 4 mm (32,768 m), beside the supported extent of 20 km. Evidence: `Strata/src/Strata/World/WorldAsset.h:87-89` (`c_SupportedExtent`: "What float32 positions support at 2-4 mm precision") |
| `worlds-runtime:513`, `worlds-runtime:515-517` | term | home | World, persistent scene, world layer (the glossary's name, apart from the application's layer; critic-worlds-runtime-19), cell |
| `worlds-runtime:547` | term | home | HLOD |
| `worlds-runtime:546` | term | link | Origin rebasing, named in the not-done paragraph in one sentence with a link to its home `draw/mirrors-camera-relative` (the merge "Origin rebasing") |
| `worlds-runtime:237` | concept | use | A cell is a sub-scene, loaded additively (taught on `world/sub-scenes`) |
| `worlds-runtime:241`, `worlds-runtime:247` | concept | use | The uniform grid and its layers, named as Strata's choice in plain words (taught on `worlds/grids`) |
| `worlds-runtime:251` | concept | use | Sources decide what loads, in one sentence (taught on `worlds/streamer`) |
| `worlds-runtime:265` | concept | use | The cooked index lets the streamer decide without loading a cell, in one sentence (taught on `worlds/physics-scripts`) |
| `worlds-runtime:392` | figure | use | The island's cell map as the opening picture (its home is `editor/worlds`) |
| `gamedev:257` | feature | link | The Open World sample as game makers meet it |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Loading scenes: whole, additive and in slices; sub-scenes and the frame's work budget | `world/sub-scenes` | must |
| Residency, pins and eviction: what is loaded costs memory until it is released | `assets/residency` | must |
| Binary, integers, floating point, precision and rounding; powers of two | `basics/numbers` | must |
| Object models: a scene as entities with components | `world/what-a-world-is` | helps |
| Frame time and a hitch (the frame map) | `start/what-an-engine-is` | helps |
| Levels of detail, as the renderer has them for meshes | `draw/lod` | helps |
| Mirrored transforms and camera-relative rendering, with the approaches to precision far from the origin compared | `draw/mirrors-camera-relative` | helps |
| Physics capacity and the 1e5 m limit on bodies | `physics/scale-streaming` | helps |

## `worlds/grids` — Grids, keys and layers

**Covers.** The data a world is made of, and the arithmetic on it. The job: a World asset (`.stworld`) names the
persistent scene, the grid origin, the layers and the cells that have content, and answers "which cell holds this
point" without a search. The problem section teaches uniform grids against quadtrees and hand-placed volumes, sparse
grids where only cells with content exist, and layers of different cell sizes so that terrain can stream far and props
near; the examples are the island's three layers (one cell size, three distances) and the figure's
terrain and props layers of 256 m and 64 m cells. Then the data model in code (`WorldLayer` and `WorldCell`: layers named
by ID so that a rename is cheap), the document with its header and every rule of `Validate`, which refuses untrusted
data with a reason and never asserts, the limits (32 layers, 2^20 cells, 1,000 km of extent, 20 km supported), the cell
files at `<world folder>/<World>/<Layer>/<X>_<Z>.stscene` with handles derived from the world's (so that an undo step
can name a cell before its file exists), the fields of the cooked index (how they are filled is the cook's, on
`worlds/physics-scripts`), the hash maps from packed keys, the memory the asset reports to residency, the references that
let a world load without loading a cell, and the loader's registration.

The arithmetic follows the data: floor division from the grid origin (which no command or panel sets: it changes only
when the `.stworld` is edited by hand, and a new origin moves every cell's square) to cell coordinates (lower edges
inclusive, negative positions floored, NaN and far positions clamped), the 64-bit key with the layer in the top byte and
X and Z offset by 2^27 into 28 bits each, why the packed order is the order of (layer, X, Z) that the streamer sorts by,
and the distance from a point to a cell's square in double, 0 inside. The toy version is `CellAt` and `Pack` in about 40
lines, checked against the `World.Asset` tests; the rule is that entity IDs are unique across cells and the persistent
scene. At the end the reader can compute a cell key by hand, also for negative coordinates, read and validate a
`.stworld` file, and say which cell of a layer a point lies in.

**Leaves out.**

- Deciding which cells load → `worlds/streamer`
- The cook that fills the index, and `MaxBodiesInRadius` → `worlds/physics-scripts`
- Writing cell documents and using derived handles in undo steps → `editor/worlds`
- Sub-asset handles in general → `assets/handles-meta`
- The scene document format of a cell → `world/serialization`
- Closures and closure scopes in general → `assets/references`
- The table of every `.stworld` key → `reference/worlds-runtime`

**Fit.** `over`: about 4,700 words against M (3,000). The next size is L (S2): four excerpts, two concepts, the toy
version, three exercises and the data model's features do not fit M without leaving out what a reader of `.stworld`
files needs.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `worlds-runtime:241` | concept | home | Spatial partitioning by a uniform grid: cells as squares from an origin, floor division, packed keys; quadtrees, volumes and World Partition compared; the mistakes of truncating negatives, of cells as points, of float grid math |
| `worlds-runtime:247` | concept | home | Layers of different granularity: big cells far for terrain, small cells near for props; the mistake of one cell size for everything |
| `worlds-runtime:23` | feature | home | The World document: header `{"Strata":{"Format":"World","Version":1}}` and the `World` object (`Strata/src/Strata/World/WorldAsset.h:73-134`; `WorldAsset.cpp:247-371` and `551-596`) |
| `worlds-runtime:24-25` | feature | home | Layers (cell size 1-65,536 m, distance 0-1,000 km, 1-32 per world, IDs 1-255, names without commas, `EnabledByDefault`, `LoadBeforeStart`) and cells (a scene of its own, never the persistent scene, never shared) |
| `worlds-runtime:308` | code | home | `Strata/src/Strata/World/WorldAsset.h:19-40`: `WorldLayer` and `WorldCell`, IDs against names |
| `worlds-runtime:28-29` | feature | home | Validation in `FromJson` (the `Reader` helper) and `Validate`, and the limits `c_MaxLayers`, `c_MaxCells`, `c_MaxExtent`, `c_SupportedExtent` (`WorldAsset.h:78-89`) |
| `worlds-runtime:311` | code | home | `Strata/src/Strata/World/WorldAsset.cpp:373-431`: the world, layer and cell rules of `Validate`, each failure with its reason |
| `worlds-runtime:26` | feature | home | Cell file layout and derived handles: `DeriveSubAssetHandle(world, "Cell/<layer>/<x>/<z>")` (`StrataEditor/src/Editor/EditorWorld.cpp:179-182`); the editor's use of them is `editor/worlds`' |
| `worlds-runtime:27` | feature | home | The cooked index as data: per cell stamp, entities, bodies, bounds, closure bytes; `MaxBodiesInRadius` and `PersistentBodies` (`WorldAsset.h:42-71`) |
| `worlds-runtime:30-31` | feature | home | `FindCell` and `FindSummary` through hash maps from packed keys; `GetMemoryUsage` counting the maps' nodes for residency budgets (`WorldAsset.cpp:598-613`) |
| `worlds-runtime:32-33` | feature | home | References: the persistent scene and every cell, scenes stopping load closures so that a world loads no cell, an export's closure shipping them all; the loader registered as JSON bytes (`Strata/src/Strata/World/WorldRegistration.cpp:33-38`) |
| `worlds-runtime:34-35` | feature | home | `WorldCellKey` and the grid math `CellAt`, `CellBounds`, `Distance` (`Strata/src/Strata/World/WorldGrid.h:14-49`) |
| `new:14` | feature | home | No command or panel sets a world's grid origin: `world.create` takes none and only `world.info` reports it, so it changes only when someone edits the `.stworld` by hand, and a new origin moves the square of every existing cell; the feature test's world sits at (200, 200) (critic-worlds-runtime-16). Evidence: `StrataEditor/src/Editor/EditorWorldCommands.cpp:577-588` (`world.create`'s parameters), `:1030` (`world.info`); `Strata/src/Strata/World/WorldAsset.cpp:267` (the one write of `GridOrigin` in the engine and the editor, when the document is read); `StrataTests/FeatureTest/Assets/Worlds/FeatureWorld.stworld:57-60` |
| `worlds-runtime:309` | code | home | `Strata/src/Strata/World/WorldGrid.cpp:17-48`: the offset and mask, `ToCellCoordinate` (floor, NaN and far positions clamped), `Pack` and `Unpack` |
| `worlds-runtime:310` | code | home | `Strata/src/Strata/World/WorldGrid.cpp:53-73`: `CellAt`, `CellBounds` and the point-to-square distance in double |
| `worlds-runtime:348` | figure | home | Two layers of different cell sizes over one ground, the grid origin, cell (0, 0), negative coordinates and how `CellAt` floors |
| `worlds-runtime:350` | figure | home | The 64-bit key: 8 bits layer, 28 bits X + 2^27, 28 bits Z + 2^27; sort order equals (layer, X, Z) |
| `worlds-runtime:440` | rule | home | Entity IDs must be unique across cells and the persistent scene: a sub-scene whose IDs exist fails to load, and the cook names shared IDs |
| `worlds-runtime:488` | hands-on | home | The toy version and its exercise: write `CellAt` and `Pack` and check them against `World.Asset`'s grid test |
| `new:15` | hands-on | home | Trace it yourself (D27): a breakpoint in `WorldGrid::CellAt` while the editor moves an entity of an open world shows the floor division and the key of the entity's new cell; a search for `CellAt` then lists its other callers (the streamer's squares around a source, the cell map). Evidence: `Strata/src/Strata/World/WorldGrid.cpp:53-73`; `StrataEditor/src/Editor/EditorWorld.cpp:172-176`; `Strata/src/Strata/World/WorldStreamer.cpp:33-34`; `StrataEditor/src/UI/CellMap.cpp:160` |
| `worlds-runtime:471` | hands-on | home | Exercise: tune layers with `world.setLayers` (larger terrain cells streaming farther, `LoadBeforeStart` on terrain) on a new world, before content is placed: the command refuses to change the cell size of a layer that has cells unless `deleteCells` moves them to the trash (`StrataEditor/src/Editor/EditorWorldCommands.cpp:670-675`, `:745-747`; critic-worlds-runtime-2); given as the complete line to paste with a link to `editor/commands` |
| `worlds-runtime:514`, `worlds-runtime:518-519`, `worlds-runtime:534` | term | home | World asset, cell key, grid origin, index |
| `worlds-runtime:191` | feature | use | The `World.Asset` tests (`StrataTests/src/World/WorldAssetTests.cpp:79-327`) for How it is tested |
| `worlds-runtime:535` | term | use | The content stamp of each cell in the index, by name (home `assets/importing`, with `assets:145`; R31 D33) |
| `worlds-runtime:185` | feature | use | `Island.stworld`'s layers and a few of its cells as the example |
| `worlds-runtime:312` | code | link | The index's recommendation of physics room, shown on `worlds/physics-scripts` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Why levels stream; world, persistent scene, layer and cell | `worlds/why-streaming` | must |
| Asset handles, `.meta` files and sub-assets (derived handles) | `assets/handles-meta` | must |
| Scene documents: the text form | `world/serialization` | must |
| JSON | `basics/data-formats` | must |
| Binary integers, two's complement, shifts and masks; floating point and `double` | `basics/numbers` | must |
| Hash maps and what they cost | `basics/data-structures` | must |
| Untrusted input: validate before use | `assets/robustness` | must |
| Errors returned and logged, never asserted, for bad data | `core/conventions` | must |
| References and closures of assets | `assets/references` | must |
| Vectors and the distance between two points | `basics/math-vectors` | must |
| `std::optional`, `std::span` and `std::string_view` | `basics/cpp-modern` | helps |
| Registries that the composition root opens and that accept registrations (the asset loader registry, which stays open: only the component and settings registries freeze) | `core/layers-registries` | helps |
| What an asset reports to residency budgets | `assets/residency` | helps |
| The content stamp: whether a stored result is still current | `assets/importing` | helps |
| Running a command from a terminal (the exercise's one line) | `start/how-to-read` | helps |

## `worlds/streamer` — The streamer

**Covers.** How `WorldStreamer` decides which cells load, and how it follows them while they load and unload. The job
and the map come first: one main-thread core with two drivers (the World system in Play and Simulate, the editor in
Edit), its inputs (sources, pins, enabled layers, the World asset) and its outputs (sub-scene loads, unloads and
cancellations). The first half is what to load, in the order an evaluation runs. A source as the streamer sees it
(`WorldStreamingSource`: position, forward, radius, layer mask, priority, view bias) and why interest is not only the
camera. The wanted cells per source and enabled layer, found by scanning grid squares or the layer's cell list,
whichever is shorter. The load radius and the keep radius, H = max(CellSize / 2, 0.1 × radius), taught from a player
standing on a border with one threshold, then with two rings; one sentence says what hysteresis is and links
`input/gamepads`, the word's home. The total order (priority descending, view-biased distance ascending, packed key
ascending), view bias as "cells ahead rank as if nearer", `High` priority within half the radius, and at most four loads
at once. Then `Evaluate` walked through, with pins (counted, always wanted first), layer toggles remembered by name
before the world loads, unloads and cancellations first in key order, and the physics reservation it calls before
starting loads (named here, taught on `worlds/physics-scripts`).

The second half is the cells in flight: the five cell states and how they follow the sub-scene states, including a cell
someone else unloads; polling only the cells in flight; failures kept with their error and retried only when the cell's
scene changes, checked only when the asset manager's content version moved; adoption of cells that a prepared start or
a play copy loaded; and the update skeleton, which requests the World asset every update without holding it and
evaluates only when something is dirty or a source moved more than 1 cm. Queries, statistics and `SetReloadCells` close
it. The examples are the `World.Streaming` test that pins nearest first, four at a time and the hysteresis numbers on a
32 m grid, and the island's cells loading ahead of a walking player. The toy version is an evaluation of one source over
one layer in about 60 lines. At the end the reader can predict, for a source and a grid, which cells load, in which
order and when they unload, and can change the streamer without breaking the tests that compare drives.

**Leaves out.**

- Where sources come from: components, the primary camera, script requests → `worlds/physics-scripts`
- The physics room a world reserves, and why → `worlds/physics-scripts`
- How sub-scenes create and destroy their entities in slices → `world/sub-scenes`
- The editor's streamer: the editor camera, pins from selection and unsaved edits → `editor/worlds`
- The cell map and the viewport's cell bounds → `editor/worlds`
- Residency, requests and eviction in general → `assets/residency`

**Fit.** `over`: about 6,600 words against L (5,000). The next size is XL (S2), in two anchored halves, "What to load"
and "Cells in flight": six excerpts (one of them the 150 lines of `Evaluate`), three concepts, four figures and four
exercises are the part's central algorithm, and none of them belongs to another page.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `worlds-runtime:55-56` | feature | home | `WorldStreamer`, the core shared by the World system and the editor (`Strata/src/Strata/World/WorldStreamer.h:84-227`), and `WorldStreamingSource` (`WorldStreamer.h:28-38`) |
| `worlds-runtime:251` | concept | home | Streaming sources and interest management: player, vehicles, cameras, requests; priority, radius, facing; the mistake of streaming around the camera only |
| `worlds-runtime:58` | feature | home | Wanted cells per source and enabled layer in its mask: existing cells within the radius |
| `worlds-runtime:315` | code | home | `Strata/src/Strata/World/WorldStreamer.cpp:31-60`: `GetSquaresAround` and `ForEachCellAround`, grid squares or the layer's cell list, whichever is shorter |
| `worlds-runtime:255` | concept | home | A load radius and a keep radius, so that a cell on a border does not thrash; what hysteresis is, in one sentence that links `input/gamepads`, the term's home (R31 D33, R46); the mistake of one threshold |
| `worlds-runtime:59` | feature | home | H = max(CellSize / 2, 0.1 × radius), kept while within radius + H (`WorldStreamer.cpp:462-475`) |
| `worlds-runtime:433` | rule | home | Hysteresis is not optional: without it a player on a border loads and unloads a cell every frame |
| `worlds-runtime:351` | figure | home | Wanted and keep rings around a source, with the view-bias cone ahead |
| `worlds-runtime:60-61` | feature | home | The load order, `High` within half the radius, `c_MaxConcurrentCellLoads` = 4; view bias as ordering only |
| `worlds-runtime:257` | concept | home | Deterministic, idle-cheap decisions: a pure function of inputs and states, evaluated only on change, ties broken by key, bounded concurrency; the mistakes of iterating an unordered map and of evaluating every frame |
| `worlds-runtime:431` | rule | home | Decisions in a total order, so that drives are identical whatever the thread count |
| `worlds-runtime:62-64` | feature | home | Counted pins wanted at top priority; layer toggles by name, remembered before the world loads; unloads and cancellations first in key order, external unloads followed |
| `worlds-runtime:317` | code | home | `Strata/src/Strata/World/WorldStreamer.cpp:421-574`: `Evaluate`, wanted and keep sets, view bias, pins, unloads first, the sort, at most four loads, the reservation call |
| `worlds-runtime:57` | feature | home | `WorldCellStatus` (Unloaded, Loading, Loaded, Unloading, Failed), `WorldCellState`, `WorldActiveCell` (`WorldStreamer.h:40-69`) |
| `worlds-runtime:353` | figure | home | The cell state machine beside the `SubSceneState` machine, and how the two map |
| `worlds-runtime:67` | feature | home | Only the cells in flight are polled each update; created and destroyed entities counted |
| `worlds-runtime:318` | code | home | `Strata/src/Strata/World/WorldStreamer.cpp:287-366`: `PollCellsInFlight`, a state machine driven by another system's states, someone else unloading included |
| `worlds-runtime:68` | feature | home | Failed cells keep their error and retry only when their scene's source revision changes |
| `worlds-runtime:319` | code | home | `Strata/src/Strata/World/WorldStreamer.cpp:368-390`: `RetryChangedFailures`, compared only when the content version moved |
| `worlds-runtime:69` | feature | home | Adoption of sub-scenes whose source is a cell (a prepared start, a play copy) |
| `worlds-runtime:66` | feature | home | Evaluation only when dirty or a source moved more than `c_SourceEpsilon` (1 cm); `GetLastDecisions` for tests |
| `worlds-runtime:316` | code | home | `Strata/src/Strata/World/WorldStreamer.cpp:228-253`: `Update`, the asset requested every update, cells in flight polled, evaluation only when dirty |
| `worlds-runtime:355` | figure | home | One update as a flowchart: request the asset, poll, refresh, retry failures, dirty or moved, evaluate |
| `worlds-runtime:70` | feature | home | The World asset requested at `High` every update and read with `PeekLoadedAsset`; a `weak_ptr` notices a reloaded asset |
| `worlds-runtime:429` | rule | home | Request the World asset every update, never hold a `Ref` across frames |
| `worlds-runtime:71-72` | feature | home | `IsLoadedAround`, `GetStats` with `StateVersion`, the cell queries; `SetReloadCells` for the editor |
| `worlds-runtime:394` | figure | home | The cell map while playing the island: cells loading ahead of the moving player (view bias) |
| `worlds-runtime:338` | code | home | `StrataTests/src/World/WorldStreamerTests.cpp:169-234`: nearest first, four at a time, the hysteresis numbers, and a still source that costs no evaluation |
| `worlds-runtime:191` | feature | home | The area's tests for How it is tested, with the suites at the pin: `World.Asset`, `World.Streaming` (`WorldStreamerTests.cpp` and `WorldStreamingTests.cpp`; the inventory's "World.Streamer" is no suite), `World.Coordinates`, `Runtime.*`, `Editor.World`, `Editor.WorldCook`, `Editor.Export*`, the drive processes and the `Perf.World.*` tests; each other page of the part uses its own rows |
| `worlds-runtime:490-496` | hands-on | home | Exercises: add a streaming statistic through service, command and perf log; make the concurrency limit a `WorldComponent` property; replace view bias by a cone of priority; measure decisions while changing H, as the page's trace it yourself (D27): a breakpoint in `Evaluate` while a source walks across a cell border shows the keep set holding the cell until the source is past radius + H, then a drive test counts the decisions for another H (`Strata/src/Strata/World/WorldStreamer.cpp:462-475`; `StrataTests/src/World/WorldStreamerTests.cpp:169-234`) |
| `worlds-runtime:520`, `worlds-runtime:522-523`, `worlds-runtime:525-526`, `worlds-runtime:540` | term | home | Streaming distance, streaming source, view bias, wanted cell, cell pin (the glossary's name, apart from the asset pin; critic-worlds-runtime-19), adoption |
| `worlds-runtime:524` | term | link | Hysteresis, said in one sentence beside the keep radius, with a link to its home `input/gamepads`, which is not in this page's Needs closure (R31 D33, R46) |
| `worlds-runtime:34-35` | feature | use | The packed key's order and the point-to-square distance |
| `worlds-runtime:237` | concept | use | Sub-scenes and their states, which cells are |
| `worlds-runtime:65` | feature | link | The reservation `Evaluate` calls before loads (home `worlds/physics-scripts`) |
| `worlds-runtime:113` | feature | link | The cell map that draws the streamer's states (home `editor/worlds`) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Grids, cells, keys and layers; the point-to-square distance | `worlds/grids` | must |
| Deterministic parallel work: results that do not depend on the number of threads | `core/jobs` | must |
| Sub-scenes, their states and unloads in slices | `world/sub-scenes` | must |
| Residency: request what you use every frame, never hold a `Ref` across frames | `assets/residency` | must |
| Hash maps and sets; sorting and what it costs | `basics/trees-graphs` | must |
| Lambdas, `std::sort` with a comparator, the standard containers | `basics/cpp-generic` | must |
| Smart pointers: `Ref`, `Scope` and `std::weak_ptr` | `basics/cpp-memory` | must |
| Vectors: length, normalizing and the dot product | `basics/math-vectors` | must |
| Asset priorities and loads in the background | `assets/loading` | helps |
| Source revisions, reimports and the content version | `assets/importing` | helps |
| Physics capacity and `Reserve` | `physics/scale-streaming` | helps |
| Profiling scopes (`ST_PROFILE_FUNCTION`) | `core/profiling` | helps |
| A unit test case in doctest | `core/first-change` | helps |

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

## `worlds/export` — Shipping a game: the export

**Covers.** How `GameExport` turns the open project into a folder a player can run, without blocking a frame. The
problem: what the editor keeps (sources, imports, a project file, a loaded script module) is not what a game ships, and
engines answer with a build step (Unity's player build, Unreal's cook and pak); Strata's export writes an asset pack, a
manifest, the script module, an icon and a renamed runtime. The map shows the main thread and the I/O job and the state
machine WaitingForImports → CookingWorlds → Packing → Copying → Succeeded, Failed or Cancelled, with the progress in
bytes and the stage text that the Export dialog and `project.exportStatus` show. Then the work in the order data flows.
`Start` checks what it can without reading the project's files and fails without side effects: a project, no Play, the
scene saved or its save in flight, an export directory that is absolute, local, outside the project and free of device
names, a start scene, the runtime and its notices beside the editor, the loaded script module unchanged, the loading
scene, valid settings sections, the title and the icon's source. Four of its decisions are told with them: without a
start scene in the project the open scene is the start scene; the loading scene may not be the start scene; a pruned
pack keeps the loading scene and every asset that the settings sections name, and a section that names an asset the
project lacks fails the export; the manifest's window (1280 by 720, windowed, vsync on) comes from the export's options,
not from a project setting. `Update` waits for background imports and saves, scans the documents whose reference search
had not run on a job, starts the cooks of stale worlds, writes their indexes like import results (no undo step) and
records the physics room each persistent scene needs, then plans the pack once on the main thread (the pack itself is
`assets/packs-export`'s).

The I/O job follows the rule "fail before writing": the icon is decoded and the Windows runtime stamped in memory before
the pack is written, so that a failed export never leaves a new pack beside an old executable; the packed persistent
scene gets the cooked physics capacity; then the script module exactly as loaded, named in the manifest's
`ScriptModule`, with its PDB outside Dist, the icon, the manifest, the executable, the third-party notices and the Linux
desktop entry. The folder it leaves, the commands that drive it, and the not-done paragraph (no exports for another
platform, no macOS app bundle, no signed exports, no crash reports in shipped games) close the page. At the end the
reader can name every file of an exported game and the check that guards it, and can add a check to the state where it
belongs.

**Leaves out.**

- The pack: its format, planning, pruning, `AlwaysInclude`, patches and cooked documents → `assets/packs-export`
- The manifest, the icon, the version resources and the desktop entry → `worlds/game-identity`
- The Export dialog → `editor-ui/launcher-dialogs`
- Exporting a game step by step → `make/export`
- Saves in flight and the `DocumentSaver` → `editor/saving`
- The engine's installed layout and its releases → `engineering/releasing`
- Running the exported game → `worlds/runtime`

**Fit.** `over`: about 4,900 words against M (3,000). The next size is L (S2), the size the page had before the first
size pass: five excerpts of `Start`, `Update` and the I/O job, the up-front checks with four decisions of `Start`, and
two exercises take the most words.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `worlds-runtime:279` | concept | home | Shipping, from project to product: editor data against runtime data; the player build and cook and pak compared; Strata's export; the mistake that assets a script loads by path vanish from a pruned pack |
| `worlds-runtime:155` | feature | home | `GameExport`, the non-blocking state machine with progress in bytes and stage text (`StrataEditor/src/Editor/GameExport.h:65-189`; `GameExport.cpp:165-862`) |
| `worlds-runtime:372` | figure | home | The export's state machine, which thread does what, and where each check happens |
| `worlds-runtime:156` | feature | home | The up-front checks, and `CheckExportDirectory` (`GameExport.h:191-193`); four decisions of `Start` with them (critic-worlds-runtime-14): without a start scene in the project the open scene is the start scene; the loading scene may not be the start scene; a pruned pack keeps the loading scene and every asset that the settings sections name, and the export fails when a section names an asset the project lacks; the manifest's window (1280 by 720, windowed, vsync on) comes from the export's options, not from a project setting (`StrataEditor/src/Editor/GameExport.cpp:187-191`, `:222-227`, `:257-276`, `:314-316`; `GameExport.h:39-41`; `Strata/src/Strata/Project/GameManifest.h:58-61`) |
| `new:3` | code | home | `StrataEditor/src/Editor/GameExport.cpp:165-228`: the first checks of `Start`: no project, playing, unsaved scene, the directory, the start scene, the runtime and its notices, the script module, the loading scene |
| `new:4` | code | home | `StrataEditor/src/Editor/GameExport.cpp:129-163`: `CheckExportDirectory`: network and device paths, relative paths, reserved device names, inside the project, a file |
| `worlds-runtime:157` | feature | home | Waiting and planning: imports and saves polled, pending reference searches scanned on a job, the plan made once on the main thread, the writing on an I/O job |
| `assets:217` | feature | home | The export as the asset inventory lists it: `GameExport` polls `HasPendingImports`, plans, writes the pack on an I/O thread; taught with worlds-runtime:155 and 157 above (taken from `assets`) |
| `new:5` | code | home | `StrataEditor/src/Editor/GameExport.cpp:335-409`: `Update` while waiting: cancellation, imports and saves, the awaited save, the document scan on a job, then cooking or planning |
| `worlds-runtime:158` | feature | home | World cooking at export: stale worlds cooked, indexes written like import results, `RecommendedMaxBodies` passed through `AdjustSceneSettings` |
| `new:6` | code | home | `StrataEditor/src/Editor/GameExport.cpp:491-525`: `FinishCooking`: the index as derived data without an undo step, written only when it changed; the capacity per persistent scene |
| `worlds-runtime:446` | rule | home | Fail before writing: decode the icon and stamp the executable before the pack, so that a failed export never leaves a half-new folder |
| `worlds-runtime:336` | code | home | `StrataEditor/src/Editor/GameExport.cpp:595-650`: the icon first, the Windows stamp before the pack, the packed scene settings adjusted |
| `worlds-runtime:162` | feature | home | The script module exactly as the editor loaded it, its PDB unless Dist or `includeScriptSymbols: false`; a failure when scenes use scripts without a module (`GameExport.cpp:585-593`, `663-675`) |
| `scripting:212` | feature | home | The module and its PDB next to the game, named by its file name in the manifest's `ScriptModule` (`StrataEditor/src/Editor/GameExport.cpp:313`; the field since manifest version 2, `Docs/DeveloperGuide.md:2105-2108`); taught with worlds-runtime:162 above (taken from `scripting`) |
| `worlds-runtime:374` | figure | home | The exported folder: executable, `.stgame`, `.stpak`, the module and its PDB, the 256-pixel PNG, `ThirdPartyNotices.md`, the `.desktop` file on Linux, with arrows to what reads what |
| `worlds-runtime:167` | feature | home | `project.export`, `project.exportStatus`, `project.cancelExport`, `project.setExportSettings`, `project.setGameInfo`, `project.setStartScene`, each as a line to paste with a link to `editor/commands` |
| `new:7` | not-done | home | Exports for another platform, macOS app bundles, signed exports and crash reports in shipped games (the export copies the runtime next to the editor). Evidence: `Docs/Releases/0.7.0.md:411-412`; `StrataEditor/src/Editor/GameExport.h:30`; `Docs/Roadmap.md:1684-1685` (checked again at the pin: it holds) |
| `worlds-runtime:479` | hands-on | home | Exercise: set the identity and icon, choose a loading scene, export, run the executable, find the log and save folders |
| `new:21` | hands-on | home | Trace it yourself (D27): a breakpoint in `GameExport::Update` follows one export from `WaitingForImports` through `CookingWorlds` and `Packing` to `Copying`, and a search for `fail(` in `Start` lists every up-front check with its message, in the order the page gives them. Evidence: `StrataEditor/src/Editor/GameExport.cpp:165-322` (`Start`), `:335-463` (`Update`); `StrataEditor/src/Editor/GameExport.h:65-75` (`GameExportState`) |
| `worlds-runtime:548` | term | home | Export |
| `worlds-runtime:159-161` | feature | use | The asset pack, pruning and patch packs, one paragraph each with links (home `assets/packs-export`) |
| `worlds-runtime:442` | rule | use | Pruning is off by default (home `assets/packs-export`) |
| `worlds-runtime:110` | feature | use | The cook that the export runs (home `worlds/physics-scripts`) |
| `worlds-runtime:163-165` | feature | link | The icon, the version resources and the desktop entry the I/O job writes (home `worlds/game-identity`) |
| `worlds-runtime:168` | feature | use | The Export dialog follows an export an agent started (home `editor-ui/launcher-dialogs`) |
| `worlds-runtime:400` | figure | use | The Export dialog during an export, showing the stage text (home `editor-ui/launcher-dialogs`) |
| `worlds-runtime:169` | feature | link | The installed layout that puts the runtime beside the editor (home `engineering/releasing`) |
| `worlds-runtime:191` | feature | use | `Editor.Export` (`StrataTests/src/Editor/EditorExportTests.cpp:167-864`, `WorldGameExportTests.cpp`) for How it is tested |
| `assets:177`, `assets:179` | feature | use | Pack planning and cooked documents, as the asset inventory lists them |
| `build-test:123` | feature | use | The export chain's CTests |
| `editor-ui:217` | feature | link | The Export Game dialog as the editor-ui inventory lists it |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The cook and the physics room it records | `worlds/physics-scripts` | must |
| Asset packs: format, planning, pruning, `AlwaysInclude`, patches, cooked documents | `assets/packs-export` | must |
| Projects and settings sections, and their validation | `world/projects-settings` | must |
| Files you can trust: paths, atomic writes | `core/files` | must |
| Jobs on I/O threads and what stays on the main thread | `core/jobs` | must |
| Atomics and a mutex shared by two threads | `basics/threads` | must |
| Background imports and when they are done | `assets/importing` | must |
| Reference searches of documents | `assets/references` | helps |
| Saves off the main thread (`DocumentSaver`) and saves in flight | `editor/saving` | helps |
| The editor's core and its context (`EditorContext`) | `editor/program` | helps |
| Building scripts from the editor, and the loaded module | `editor/script-builds` | helps |
| Shared libraries and their debug symbols | `scripting/shared-libraries` | helps |
| Commands are the API (`project.export`) | `editor/commands` | helps |
| Exceptions of third-party code caught at the call site | `core/conventions` | helps |
| Running a command from a terminal | `start/how-to-read` | helps |

## `worlds/game-identity` — A game's identity: the manifest, icons and platform files

**Covers.** What a game is called, how it shows itself on each system, and why the runtime trusts its manifest only so
far. The problem: a game must keep its players' saves when it is renamed, and must look like an application in
Explorer, a Linux desktop's menus and the macOS Dock, while the files beside it may have been changed by anyone. The
manifest comes first: `.stgame` version 5 with its fields (name, title, version, company, copyright, icon, pack, patch
packs, start and loading scenes, script module, window, settings sections), versions 1 to 4 that still load, and
settings carried as stored for the runtime to validate once modules have registered. The plain-file-name rule follows:
every file the manifest names lies next to it, with no paths and no `.` or `..`, so that a manifest cannot point the
runtime at another folder. Then identity: `ProjectGameInfo` and its checks (at most 128 code points without control
characters, a version of up to four parts of at most 65,535), and `GamePresentation`, decided from the manifest alone
before anything starts: the window's title, the log's banner, the application id, and the data directory keyed by the
manifest's `Name`, never its title (its `Saves` and `Logs` folders), so that an update that renames the game keeps the
saves.

Each platform last: the icon made square on transparent pixels and resized in linear light with colors weighted by alpha
to ten sizes, a 256-pixel PNG beside the manifest and a warning for small sources; the Windows version resources and
icon group written into a PE32+ image by engine code without the Win32 API (read and checked before use, never
asserting), and why a signed runtime cannot be stamped, so games are signed after the export; the Linux desktop entry
with escaped values and a quoted `Exec`, which names the export folder's absolute paths (moving or shipping the folder
means editing its `Exec` and `Icon`), which the export writes beside the game but does not install, and whose
`StartupWMClass` is the executable's name, the reason the runtime's application id is the executable's stem; the macOS
Dock icon taken from the window's icon while the game runs. The pictures are the Game page of Project Settings and the
executable's Details tab with its icon. The not-done line says that a script cannot read the game's title or version,
and the exercises rename a game and break a manifest. At the end the reader can read a manifest and say which of its
fields the runtime trusts and how, and can say where an exported game's saves and logs go and why a rename keeps them.

**Leaves out.**

- The order of the export's work and its checks → `worlds/export`
- How the runtime starts from the manifest → `worlds/runtime`
- Settings sections, their versions and validation → `world/projects-settings`
- The players' graphics options file → `image/quality-settings`
- The Game page of Project Settings as a window → `editor-ui/settings-windows`
- Save files as game makers write them → `make/levels-saves`

**Fit.** `over`: about 4,700 words against M (3,000). The next size is L (S2): four excerpts, the manifest's fields
and checks, three platforms' files and two exercises take the most words; moving the icon and the version resources to
`worlds/export` no longer helps, since that page is over at M too.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `worlds-runtime:292` | concept | home | Game identity and platform integration: executable resources on Windows, desktop entries on Linux, the Dock on macOS, save folders keyed by a stable name; the mistake of keying saves on the title |
| `worlds-runtime:146` | feature | home | The `.stgame` manifest version 5 and its fields; versions 1 to 4 still load (`Strata/src/Strata/Project/GameManifest.h:18-79`; `GameManifest.cpp:28-202`) |
| `worlds-runtime:147` | feature | home | Every file the manifest names lies next to it |
| `worlds-runtime:335` | code | home | `Strata/src/Strata/Project/GameManifest.cpp:16-24`: `IsPlainFileName`; with lines 95-114, where the icon, the pack, each patch pack and the module are checked |
| `worlds-runtime:444` | rule | home | The manifest is untrusted input and names only files next to it |
| `worlds-runtime:148` | feature | home | `ProjectGameInfo`: title, company and copyright of at most 128 code points without controls, a version of 1 to 4 parts of at most 65,535, the icon as a texture handle (`Strata/src/Strata/Project/GameInfo.h:13-49`) |
| `worlds-runtime:133` | feature | home | `GamePresentation`: title, banner, data directory, icon file, application id, applied to the window's specification before anything starts (`Strata/src/Strata/Runtime/GamePresentation.h`, `GamePresentation.cpp`) |
| `new:8` | code | home | `Strata/src/Strata/Runtime/GamePresentation.h:12-30`: what the runtime decides from the manifest alone, the data directory keyed by `Name` |
| `worlds-runtime:149` | feature | home | The save and log directory keyed by the manifest's `Name` (`GameManifest.h:38-40`, `GamePresentation.h:18-21`; the inventory's `GamePresentation.h` 224-227 do not exist): saves under `<user data>/<Name>/Saves` (`SaveDirectory::ForGame`, `Strata/src/Strata/Core/SaveFiles.h:39-58`), the log at `<user data>/<Name>/Logs/Game.log` (`StrataRuntime/src/RuntimeApplication.cpp:457-459`) |
| `worlds-runtime:448` | rule | home | Saves are keyed by the manifest's `Name`, never the title: renaming the game keeps its players' saves |
| `worlds-runtime:163` | feature | home | The game icon: the texture's PNG, JPEG, TGA or BMP source (at most 16 MiB and 4,096 pixels) made square, resized to ten sizes, a 256-pixel PNG next to the manifest, a warning for small sources (`StrataEditor/src/Editor/GameIcon.h:10-63`) |
| `new:9` | code | home | `StrataEditor/src/Editor/GameIcon.cpp:34-64`: the square on transparent pixels, and the resize in linear light with colors weighted by alpha so that the border neither darkens nor tints the edges |
| `worlds-runtime:164` | feature | home | `PEResources`: a PE32+ resource section parsed and rewritten without the Win32 API; `StampGame` writes `VS_VERSIONINFO` and the icon group `GLFW_ICON`; signed images and unusual layouts refused (`StrataEditor/src/Editor/PEResources.h:15-102`) |
| `new:10` | code | home | `StrataEditor/src/Editor/PEResources.h:58-72`: `Read` checks every header, section and resource directory before reading and never asserts; `Write` rebuilds the resource section in place and refuses a certificate table |
| `worlds-runtime:459` | rule | home | A signed runtime cannot be stamped: sign the game after exporting it |
| `worlds-runtime:165-166` | feature | home | The Linux desktop entry with escaped values and a quoted `Exec` (`StrataEditor/src/Editor/DesktopEntry.cpp:34-115`); it names the export folder's absolute paths, so moving or shipping the folder means editing its `Exec` and `Icon`; the export writes it beside the game and does not install it; its `StartupWMClass` is the executable's name, which is why the runtime's application id is the executable's stem (`StrataEditor/src/Editor/DesktopEntry.h:11-22`; `StrataEditor/src/Editor/GameExport.cpp:714-723`; `Strata/src/Strata/Runtime/GamePresentation.h:23`; critic-worlds-runtime-7); the macOS Dock icon from the window's icon (`Strata/src/Platform/GLFW/GLFWApplicationIcon*`, to be read when the page is written) |
| `worlds-runtime:407` | figure | home | Project Settings, the Game page: title, version, company, copyright, icon |
| `worlds-runtime:401` | figure | home | The exported folder in the system's file browser, and on Windows the executable's Properties > Details tab and its icon |
| `new:22` | not-done | home | Reading the game's title or version from a script: the SDK has no call that returns them (book.md's entry; appendix-q2). Evidence: `Docs/Releases/0.7.0.md:363`; `git grep -ni title 822a7a46 -- StrataScriptCore` finds only the graphics options' `Title` (`StrataScriptCore/Include/StrataScript/Graphics.h:46`, `:125`; `ScriptABI.h:289`, `:299`), and `git grep -ni gameinfo 822a7a46 -- StrataScriptCore` finds nothing (run again at the pin: it holds) |
| `new:23` | hands-on | home | Exercise (D27), done with the editor and an exported game: change the game's title in Project Settings, export again into the same folder, run it, and find its saves and its log where they were, under the manifest's `Name`; then say what an update that changed `Name` would cost its players. Evidence: `Strata/src/Strata/Runtime/GamePresentation.h:18-21`; `StrataEditor/src/Editor/GameExport.cpp:302` (`Name` is the project's name); `Strata/src/Strata/Core/SaveFiles.h:39-58`; `StrataRuntime/src/RuntimeApplication.cpp:457-459` |
| `new:24` | hands-on | home | Trace it yourself (D27): a search for `IsPlainFileName` finds every field of the manifest it guards; then an exported `.stgame` whose `AssetPack` is edited to `../Other.stpak` is run, and the runtime refuses the manifest with the reason the code gives. Evidence: `Strata/src/Strata/Project/GameManifest.cpp:16-24`, `:95-114` |
| `worlds-runtime:553`, `worlds-runtime:558-560` | term | home | Game manifest, game identity, PE resources, desktop entry |
| `scene-ecs:692-693` | term | home | Game manifest, game identity, as the scene inventory words them (taken from `world`) |
| `worlds-runtime:191` | feature | use | `Editor.Export.GameIcon`, `Editor.Export.ExecutableResources` (`StrataTests/src/Editor/ExecutableResourcesTests.cpp`, not in the inventory) and `Editor.Export.DesktopEntry`; the CTests `StrataRuntime.Identity`, `.Icon`, `.GameIcon`, `.VersionInfo` |
| `scene-ecs:215-216` | feature | home | `ProjectGameInfo` and `GameManifest` as the scene inventory lists them (taken from `world`; taught with worlds-runtime:146 and 148 above) |
| `foundation:130` | feature | use | `SaveFiles` and `SaveDirectory`, which resolve the data directory |
| `editor-ui:228` | feature | link | The Project Settings panel's Game page as the editor-ui inventory lists it |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The export and what its folder holds | `worlds/export` | must |
| JSON; UTF-8, code points and other encodings | `basics/data-formats` | must |
| Linear and sRGB values | `basics/color` | must |
| Untrusted input: validate before use | `assets/robustness` | must |
| Settings sections of a project | `world/projects-settings` | must |
| Paths and files you can trust | `core/files` | must |
| Resampling an image with a filter | `basics/signals` | helps |
| Premultiplied alpha | `light/clearcoat-transmission` | helps |
| Sources and cooked forms of an asset (the icon is made from the texture's source) | `assets/what-is-an-asset` | helps |
| A window's specification: title, icon, application id | `core/windows-events` | helps |
| The save service of a game (`IGameSaves`) as scripts use it | `scripting/host-api` | helps |

## `worlds/runtime` — The runtime

**Covers.** How a shipped game runs without the editor: the same engine under another composition root, with no tooling,
no importers, no hot reload, and a headless mode for servers and CI. The map shows `StrataRuntime`'s `RuntimeLayer` over
`GameRuntime`, `GameRenderer`, `GameWindowService` and `FramePerfLog`, and which of them a headless run leaves out. The
start comes in the order it happens: `CreateApplication` checks the command line before a log, a module or a window
exists (a mistake ends the run with exit code 3 and the usage), finds the manifest next to the executable or takes
`--game`, decides the presentation, and chooses the modules (no Graphics module headless, audio on a null device);
`GetProgramRun` makes runs that end by themselves Console runs, and the Windows build is a GUI program entered at
`mainCRTStartup` with its icon and version resource. A table sets out the three kinds of run and what each gets: a
windowed game runs with time dilation, interpolation and render proxies prepared; runs that end by themselves
(`--frames`, `--seconds`) keep every fixed step, without interpolation or dilation; headless runs are capped at 60
frames a second, have no GPU and refuse `--quality` and `--screenshot`; every game has two background threads. Two
sentences give the failures: a screenshot that shows the missing-camera message or a frame still loading fails the run,
and a failed scene switch is logged while the running scene goes on. `GameRuntime::Create` then brings the game up in an
order where every failure is an error: the manifest, its settings validated, the pack and its patch packs, the script
module in its own `ScriptEngine` (loaded in place, since nothing reloads it, made active before the start scene plays,
and the host's engine restored when the game ends), the save directory, the players' bindings, the graphics options, and
the loading and start scenes' loads.

The middle is scene switching without blocking: the loading scene plays while the start scene loads with
`PrepareSystems`, a switch keeps the running scene playing until the next one is ready, a second request for the scene
that is loading keeps its load, the old scene is released in the background and unused assets are trimmed frames later,
one `SceneWorkBudget` serves the frame's loading work, and the frame is capped at 60 per second while nothing plays. The
per-frame loop follows: update, the start error, the headless crash policy (a crash, logged once and again with its
location once symbolized, disables the scripts for the session: exit code 2 headless, while a windowed game runs on
without its scripts), a quit with the game's own code, the window's requests, and the render; `GameRenderer` draws the
primary camera, a UI-only scene over black, or a "No camera to show" message, and resets exposure and TAA history when
the scene changes, so a window is never black or stale. Window and graphics options apply between frames and only when
they change something; the engine stores only the graphics options (`GraphicsOptions.json`), so window options last for
the session unless the game writes them to a save file, as `make/levels-saves` shows. The last section measures a
shipped game: game time counted in fixed steps from the start, runs that keep every fixed step (`--frames`, `--seconds`)
so that their last frame is the same on every machine, and the perf log, whose row is captured when a frame ends and
written when its GPU times arrive. The not-done paragraph says that an exported game runs no command scripts or
simulated input. An exercise runs a game headless with `--frames 300` and with `--seconds 5` and explains why the first
run's game time and the second run's frame count depend on the machine. At the end the reader can run an exported game
headless with `--frames` and a perf log, read its exit code and its CSV, and add a runtime option.

**Leaves out.**

- `SceneLoader`, prepared loads and slices in general → `world/sub-scenes`
- Players' graphics options and `GameGraphicsService` → `image/quality-settings`
- Keeping a game's display settings in a save file, as a game maker writes it → `make/levels-saves`
- The layer table and "no tooling in games" → `core/layers-registries`
- The editor's play mode and its scene switches → `editor/play-mode`
- Measuring a game as a game maker → `make/performance`
- The renderer's passes → `gpu/frame-tour`
- Script crashes and how they are contained → `scripting/crash-containment`
- Every runtime option and perf-log column in one table → `reference/worlds-runtime`
- The runtime's install rule and the release packages → `engineering/releasing`

**Fit.** `fits`: about 8,200 words against XL (8,000). Nine excerpts and four concepts (a runtime that is not the
editor, scene switches, players' options, measuring a shipped game) take the most words, in anchored sections: the
start, scene switches, the frame and measuring.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `worlds-runtime:284` | concept | home | A runtime that is not the editor: one engine, another composition root, no tooling, no importers, no hot reload, headless runs; the mistake of calling editor-only code from game code |
| `worlds-runtime:378` | figure | home | The runtime's composition, windowed and headless |
| `worlds-runtime:137-139` | feature | home | The `StrataRuntime` executable, its options and exit codes (1, 2, 3, or the game's); the manifest found next to it (`Strata/src/Strata/Project/GameManifest.h:76-78`); its Windows build (`StrataRuntime/CMakeLists.txt:1-42`, `StrataRuntime.rc.in`); the three kinds of run as a table (critic-worlds-runtime-11): headless runs capped at 60 frames a second, without a GPU, refusing `--quality` and `--screenshot`; two background threads in every game; a screenshot that shows the missing-camera message or a frame still loading fails the run, and a failed scene switch is logged while the running scene goes on (`StrataRuntime/src/RuntimeApplication.cpp:39`, `:42`, `:273-312`, `:378-410`, `:473-488`; `Strata/src/Strata/Runtime/GameRuntime.cpp:281`) |
| `worlds-runtime:334` | code | home | `StrataRuntime/src/RuntimeApplication.cpp:378-410`: `CheckOptions`, the command line validated before anything starts; with lines 424-533, `CreateApplication` choosing the modules |
| `worlds-runtime:124-125` | feature | home | `GameRuntime`, the windowless core, and `GameRuntimeOptions` (`Strata/src/Strata/Runtime/GameRuntime.h:30-60`); how `StrataRuntime` sets them for each kind of run, in the page's table (critic-worlds-runtime-11): a windowed game with time dilation, interpolation and render proxies prepared; runs that end by themselves keeping every fixed step, without interpolation or dilation; headless runs without render proxies or interpolation (`StrataRuntime/src/RuntimeApplication.cpp:75-91`) |
| `worlds-runtime:329` | code | home | `Strata/src/Strata/Runtime/GameRuntime.cpp:45-156`: `Create`: manifest, settings, pack, patches, scripts, saves, bindings, graphics, loads; every failure returns an error |
| `worlds-runtime:288` | concept | home | Startup and scene switching: loading screens, progress, preparation before the swap, background release, trimming later; the mistake of a black window while loading |
| `worlds-runtime:126-127` | feature | home | Non-blocking scene loads with `SceneLoader::LoadAsync`, the same scene asked again, `ScheduleTrim`, `ReleaseInBackground`; the loading scene and its restart (`GameRuntime.cpp:178-224`) |
| `worlds-runtime:93` | feature | home | `Scene::RequestSceneLoad`, `RequestQuit` and `Game::GetSceneLoadProgress` honored by the runtime (`GameRuntime.cpp:339-362`) |
| `worlds-runtime:129` | feature | home | 60 frames per second while nothing plays (`c_LoadingFrameRate`, `GameRuntime.h:143-147`) |
| `worlds-runtime:330` | code | home | `Strata/src/Strata/Runtime/GameRuntime.cpp:226-282`: `UpdateSceneLoads`; with lines 296-314, `Update` and one budget per frame |
| `worlds-runtime:333` | code | home | `StrataRuntime/src/RuntimeApplication.cpp:138-198`: the per-frame loop: update, start error, headless crash policy, quit, window requests, render, the run's last frame |
| `worlds-runtime:131` | feature | home | `GameRenderer`: the primary camera, UI over black, the message scene, history reset on a new scene, `RenderEmpty` (`Strata/src/Strata/Runtime/GameRenderer.h:23-90`) |
| `worlds-runtime:332` | code | home | `Strata/src/Strata/Runtime/GameRenderer.cpp:95-152`: never a black or stale window |
| `worlds-runtime:404` | figure | home | The "No camera to show" frame of a scene without a primary camera |
| `worlds-runtime:403` | figure | home | The exported Open World game: its loading scene with the progress bar, then the island; the island's shot may show the Wildlife layer's foxes (the cells of `Samples/OpenWorld/Assets/Worlds/Island/Wildlife/` hold instances of the `Fox` prefab), and when it does its caption names the fox's authors and the license (R32, D18) |
| `worlds-runtime:298` | concept | home | Players' options: window mode, resolution and vsync here, applied between frames; the engine stores only the graphics options (`GraphicsOptions.json`, linked to `image/quality-settings`), so window options last for the session unless the game writes them to a save file (a link to `make/levels-saves`; critic-worlds-runtime-1); the mistake of changing the window mid-frame |
| `worlds-runtime:91` | feature | home | `Game::SetWindowMode`, `SetResolution`, `SetVSync` through `IGameWindow` (`StrataScriptCore/Include/StrataScript/Game.h:75-91`) |
| `worlds-runtime:134` | feature | home | `GameWindowService`: requests stored and applied once per frame after the update; headless runs report what was asked |
| `worlds-runtime:337` | code | home | `Strata/src/Strata/Runtime/GameWindowService.cpp:95-161`: `ApplyRequests`, at a frame boundary and only when something changes |
| `worlds-runtime:449` | rule | home | Window changes apply between frames, and only when they change something |
| `new:25` | erratum | home | Concept 19 of the worlds-runtime inventory (lines 298-300) says that the window mode, resolution and vsync the player chooses are kept in the save directory; the engine keeps only the graphics options, in `GraphicsOptions.json`, and the page states that (process.md's table, kind `inventory`; critic-worlds-runtime-1). Evidence: `Strata/src/Strata/Runtime/GameGraphicsService.h:22-28`; `Strata/src/Strata/Runtime/GameWindowService.h:15-18` (requests applied between frames, no file written); `Samples/ThirdPerson/Scripts/ThirdPerson.cpp:81`, `:97-98` (a game that keeps its display settings saves them itself) |
| `worlds-runtime:295` | concept | home | Measuring a shipped game: per-frame CSV logs, deterministic runs and screenshots; the mistake of comparing runs whose game time depended on the frame rate |
| `worlds-runtime:128` | feature | home | `GetPlayedSeconds` counts fixed steps after the start; `KeepEveryFixedStep` for runs that end by themselves |
| `worlds-runtime:331` | code | home | `Strata/src/Strata/Runtime/GameRuntime.cpp:28-41`: `LimitToFixedSteps`, so that no fixed step is dropped |
| `worlds-runtime:457` | rule | home | Deterministic runs keep every fixed step; normal play follows the wall clock with time dilation |
| `worlds-runtime:136` | feature | home | `FramePerfLog`: the built-in columns and the column groups, captured at frame end and written once GPU times arrive (`Strata/src/Strata/Runtime/FramePerfLog.h:18-155`) |
| `worlds-runtime:130`, `worlds-runtime:132` | feature | home | The runtime's world, physics capacity and step columns (`GameRuntime.cpp:364-432`) and the renderer's columns (`GameRenderer.cpp:178-203`) |
| `new:11` | code | home | `StrataRuntime/src/RuntimeApplication.cpp:200-249`: `StartPerfLog`, one listener that captures a frame when it ends and one that writes its row with the GPU's times; an incomplete log fails the run |
| `worlds-runtime:382` | figure | home | Frame N captured at its end, its row written when its GPU times arrive frames later |
| `worlds-runtime:408` | figure | home | A perf log of an Open World drive with the World and Physics columns plotted (dataviz rules) |
| `new:12` | not-done | home | Automating an exported game: command scripts, simulated input and expectations run in the editor only. Evidence: `Docs/Roadmap.md:1697`; `Docs/Releases/0.7.0.md:414` (checked again at the pin: it holds) |
| `worlds-runtime:481` | hands-on | home | Exercise, one with `foundation:537` below, so that the page holds four exercises (style.md §6.3): measure a run with `--frames 600 --perf-log run.csv --resolution 1280x720` and compare `--quality low` and `ultra` |
| `worlds-runtime:502-506` | hands-on | home | Exercises: add a runtime option to `c_Arguments` and `CheckOptions`; add a perf-log column group and make it write the wrong count; trace a scene switch, as the page's trace it yourself (D27): a breakpoint in `GameRuntime::HandleSceneRequests` catches a script's `Game::LoadScene`, one in `StartScene` shows the swap once the load is ready, and a Tracy capture shows the `Scene.Load` stage on the frames between (`Strata/src/Strata/Runtime/GameRuntime.cpp:339-362`, `:226-282`, `:211-224`, `:296-314`) |
| `gamedev:559` | hands-on | home | The same exercise as router-gamedev words it (`--mute`, with tests of the exit codes), merged with worlds-runtime:502 (taken from `router-gamedev`) |
| `gamedev:388` | code | home | `StrataRuntime/src/RuntimeApplication.cpp:339-354`: `c_Arguments`, every option the runtime understands, which `CheckOptions`, the usage and `reference/worlds-runtime` read; the excerpt's second half, the export's states (`StrataEditor/src/Editor/GameExport.h:65-75`), is shown on `worlds/export` (taken from `router-gamedev`) |
| `worlds-runtime:554-556`, `worlds-runtime:561-562` | term | home | Loading scene, start scene, runtime, perf log, column group |
| `worlds-runtime:557` | term | use | Headless, as `core/first-frame`'s one entry of the word defines it (the merge "Headless"); this page keeps headless runs as a feature (`book.md`'s row of the runtime) |
| `worlds-runtime:135` | feature | use | `GameGraphicsService` as the graphics half of the players' options (home `image/quality-settings`) |
| `worlds-runtime:140` | feature | use | The runtime links no tooling, and `StrataRuntime.NoTooling` reads its linker map (home `core/layers-registries`) |
| `worlds-runtime:161` | feature | use | Patch packs mounted in `Create` (home `assets/packs-export`) |
| `worlds-runtime:146` | feature | use | The manifest's fields the runtime reads (home `worlds/game-identity`) |
| `worlds-runtime:133` | feature | use | `GamePresentation` applied to the window before anything starts (home `worlds/game-identity`) |
| `worlds-runtime:191` | feature | use | `Runtime.Game` (`StrataTests/src/Runtime/GameRuntimeTests.cpp:162-1068`), `Runtime.PerfLog`, `Runtime.FramePerfLog`, `Runtime.GameGraphics`, `GPU.Runtime.GameRenderer` and the `StrataRuntime.*` CTests |
| `render-core:193` | feature | use | `GameRenderer` as the render-core inventory lists it |
| `scripting:198` | feature | home | The exported game's script engine: `GameRuntime` loads the module in place (no hot reload) and makes it active before the start scene plays; a crash disables the scripts for the session, a headless run exits with code 2 (`StrataRuntime/src/RuntimeApplication.cpp:150-159`); taught with worlds-runtime:329 and 333 above (taken from `scripting`) |
| `scripting:685` | open | home | Settled at the pin: `GameRuntime`'s script handling is `Strata/src/Strata/Runtime/GameRuntime.cpp:100-115` (an engine of its own, the module next to the manifest, active before the start scene), `147-154` (the classes counted in the log), `166-168` (the host's engine restored) and `CheckScriptFault` at `316-337` (the crash logged once, its location when symbolized); the page reads it with scripting:198 (taken from `scripting`) |
| `scripting:199` | feature | use | The engine services a host provides |
| `foundation:56` | feature | use | `CommandLine` and `CommandLineOptions` |
| `build-test:123` | feature | use | The runtime option tests |
| `foundation:537` | hands-on | home | Exercise: run `StrataRuntime --game <file> --headless --frames 300` and `--seconds 5`, and explain from `GetPlayedSeconds` and the kept fixed steps why one run's game time and the other's frame count differ across machines (`StrataRuntime/src/RuntimeApplication.cpp:186-197`); it needs an exported game; the second half of the exercise of `worlds-runtime:481` (taken from `core`) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The manifest, `GamePresentation` and the game's identity | `worlds/game-identity` | must |
| Engine modules and engine services (`ApplicationSpecification::Modules`, scoped providers) | `core/engine-modules` | must |
| Console and GUI programs, exit codes, fatal error dialogs | `core/platform` | must |
| From `main` to the first frame: `CreateApplication`, `ApplicationLaunch`, `GetProgramRun`, the specification, `CommandLine` | `core/first-frame` | must |
| Layers and the application's frame (`Layer::OnAttach`, `OnUpdate`) | `core/windows-events` | must |
| The frame loop and its pacing | `core/frame-loop` | must |
| The fixed step, the accumulator and time dilation | `core/time` | must |
| The fixed step's code in `Scene` (`GetMaxFixedSteps`, `GetFixedStepCount`) | `world/systems` | must |
| Loading scenes: `SceneLoader`, prepared loads, `ReleaseInBackground`, the frame's `SceneWorkBudget` | `world/sub-scenes` | must |
| Residency and trimming after a switch | `assets/residency` | must |
| Asset packs and patch packs | `assets/packs-export` | must |
| The script system and a crashed module | `scripting/script-system` | must |
| Players' graphics options (`IGameGraphics`) and presets | `image/quality-settings` | must |
| The frame profiler and its stages | `core/profiling` | must |
| GPU timestamps and stages | `gpu/readback-timing` | must |
| The layer table and no tooling in games | `core/layers-registries` | must |
| Interpolation of fixed steps | `world/interpolation` | helps |
| The renderer's frame | `gpu/frame-tour` | helps |
| Exposure adaptation | `image/exposure` | helps |
| TAA history | `image/taa` | helps |
| Overlay passes: screen-space UI over an empty frame | `gpu/debug-drawing` | helps |
| Swapchains | `gpu/vulkan-nvrhi` | helps |
| Crash containment of scripts | `scripting/crash-containment` | helps |
| Players' bindings | `input/rebinding` | helps |
| The audio engine and its null device | `audio/engine` | helps |
| Text in a scene (`TextComponent`) | `gpu/text` | helps |
| Where a game's saves and log go | `worlds/game-identity` | helps |
| The save service of a game (`IGameSaves`) as scripts use it | `scripting/host-api` | helps |
| Command scripts and simulated input in the editor | `editor/command-scripts` | helps |

## Passed on

| Item | Type | To | Why |
| --- | --- | --- | --- |
| `worlds-runtime:78-83` | feature | `world/sub-scenes` | Sub-scenes, their state machine, `SubSceneComponent`, `SceneWorkBudget`, the slice limits and `PrepareSystems` belong to the home of loading scenes (book.md, one-home table); the worlds pages use them |
| `worlds-runtime:232`, `worlds-runtime:237` | concept | `world/sub-scenes` | Loading without stopping the frame, and additive scenes, are that page's concepts |
| `worlds-runtime:324` | code | `world/sub-scenes` | `Strata/src/Strata/Scene/SceneWorkBudget.cpp:32-59`, the frame budget and its adaptive chunk estimate, is the budget's own code |
| `worlds-runtime:423`, `worlds-runtime:425`, `worlds-runtime:434` | rule | `world/sub-scenes` | Prepared loads for scenes that will run, one budget per frame, sliced unloads: rules of loading scenes; `worlds/physics-scripts` names the world's reason (ground before the player) |
| `worlds-runtime:527-531` | term | `world/sub-scenes` | Sub-scene, `SubSceneComponent`, slice, scene work budget, `PrepareSystems`; a world's prepared start uses them on `worlds/physics-scripts` |
| `worlds-runtime:550` | term | `world/serialization` | Cooked documents: that page is the home of the cooked form |
| `worlds-runtime:92`, `worlds-runtime:135` | feature | `image/quality-settings` | Players' graphics options (`IGameGraphics`, the options file, the SDK's `Graphics`) have their home there; `worlds/runtime` uses the service |
| `worlds-runtime:380` | figure | `image/quality-settings` | The layering of the project's quality, the player's file and `--quality` is that page's subject |
| `worlds-runtime:451` | rule | `image/quality-settings` | Only `GameGraphicsService` touches `GraphicsOptions.json` (render-image:572 states the same rule) |
| `worlds-runtime:565` | term | `image/quality-settings` | Graphics preset |
| `worlds-runtime:99-109`, `worlds-runtime:111-117` | feature | `editor/worlds` | The editor's world: `EditorWorld`, edit settings, pins, dirty marks, cells in undo steps, re-celling, `world.moveEntities`, the two-request save, the play copy, recovery, cell IO, the world commands, `world.create`, the cell map, the Hierarchy strip, the Inspector's cell line, cell bounds and the Asset panel (the outline row of `editor/worlds`) |
| `worlds-runtime:274` | concept | `editor/worlds` | Editing a streamed world |
| `worlds-runtime:326-328` | code | `editor/worlds` | `EnsureCellSubScene` and `Recell`, `SyncPins` and `Update`, `PrepareRuntimeCopy` (`StrataEditor/src/Editor/EditorWorld.cpp`) |
| `worlds-runtime:364-369`, `worlds-runtime:388-392`, `worlds-runtime:395-399` | figure | `editor/worlds` | The editor world, the save sequence, play from the editor, and the editor's screenshots (Hierarchy strip, Cells chip, cell map and its menu, the Inspector line, an unsaved cell, the Asset panel with `world.info`, New > World); the cell map while playing (394) stays on `worlds/streamer` |
| `worlds-runtime:414-420` | rule | `editor/worlds` | Never `Scene::Copy` a whole world; membership only through `Scene::SetSubSceneOf` and `EditorWorld`; only `EditorWorld` writes cells; mark saved only after the World document |
| `worlds-runtime:455` | rule | `editor/worlds` | The cell map and cell bounds rebuild only when `StateVersion` changes: the overlay caching that page holds |
| `worlds-runtime:467` | hands-on | `editor/worlds` | Make your first world: the edit layer and the cell map are the editor's |
| `worlds-runtime:541-545` | term | `editor/worlds` | Re-celling, edit layer, dirty cell, cell map, cell bounds |
| `worlds-runtime:140` | feature | `core/layers-registries` | "No tooling in games" has its home there, with its rules, reasons and tests; `worlds/runtime` uses it |
| `worlds-runtime:453` | rule | `core/layers-registries` | Games link no tooling |
| `worlds-runtime:159-161` | feature | `assets/packs-export` | The asset pack, pruning and patch packs (the outline row of `assets/packs-export`); `worlds/export` uses them |
| `worlds-runtime:376` | figure | `assets/packs-export` | The asset pack's layout |
| `worlds-runtime:442` | rule | `assets/packs-export` | Pruning is off by default, with `Export.AlwaysInclude` |
| `worlds-runtime:483` | hands-on | `assets/packs-export` | Prune safely (assets:626, "Export pruned", is the same exercise) |
| `worlds-runtime:549`, `worlds-runtime:551-552` | term | `assets/packs-export` | Asset pack, pruning, patch pack |
| `worlds-runtime:536` | term | `assets/references` | Closure: that page is the home of references and closures |
| `worlds-runtime:168`, `worlds-runtime:175-176` | feature | `editor-ui/launcher-dialogs` | The Export dialog, the Welcome panel and the project dialogs are that page's (editor-ui §1.11) |
| `worlds-runtime:400`, `worlds-runtime:405-406` | figure | `editor-ui/launcher-dialogs` | The Export dialog, the launcher and the New Project dialog |
| `worlds-runtime:566` | term | `editor-ui/launcher-dialogs` | Launcher |
| `worlds-runtime:169` | feature | `engineering/releasing` | The installed layout is that page's (build-test ch. 13); `worlds/export` links it |
| `worlds-runtime:177-179`, `worlds-runtime:181` | feature | `editor/projects` | Templates, recent projects, samples as copies and the project commands: the launcher's model (book.md, one-home table) |
| `worlds-runtime:567-568` | term | `editor/projects` | Template, sample |
| `worlds-runtime:180` | feature | `editor/thumbnails` | Project pictures are that page's (book.md, one-home table) |
| `worlds-runtime:427` | rule | `physics/scale-streaming` | Physics never leaves a body without collision below its growth limit, and bodies at the limit wait: the growth limit's home; `worlds/physics-scripts` uses it |
| `worlds-runtime:538-539` | term | `physics/scale-streaming` | Physics capacity, growth limit |
| `worlds-runtime:563-564` | term | `core/time` | Time dilation, fixed step: that page is their home |
| `worlds-runtime:524` | term | `input/gamepads` | Hysteresis: one term home, the earlier page that teaches it, beside `audio-input:677` (R31 D33, R46; moves.tsv); `worlds/streamer` keeps the load and keep radii (`worlds-runtime:255`, `:59`) and says the word in one sentence with a link |
| `worlds-runtime:535` | term | `assets/importing` | Content stamp: one glossary entry with `editor-core:736` and `assets:145`, beside cache validity (R31 D33; moves.tsv), where its definition is corrected (R33 D34); `worlds/grids` and `worlds/physics-scripts` use it |
| `worlds-runtime:557` | term | `core/first-frame` | Headless: one entry with `foundation:583` (the merge "Headless"; moves.tsv); `worlds/runtime` keeps headless runs as a feature |
| `worlds-runtime:546` | term | `draw/mirrors-camera-relative` | Origin rebasing: one entry with `render-core:742` (the merge "Origin rebasing"; moves.tsv); `worlds/why-streaming` keeps its not-done line and links |
| `worlds-runtime:610-629` | open | `nowhere` | Surveyor's notes on files read only in part (sub-scene internals, the world save, the cook, the export's `Start` and `Update`, the identity helpers, `FramePerfLog` and `GameGraphicsService`, the pack's internals, packaging, Architecture.md's line estimates, sampled tests): no content; the allocator read at the pin every file the pages quote |
| `worlds-runtime:630` | open | `nowhere` | A note that `ProjectMigration` was not examined; it is editor-core's, on `editor/projects` |
| `worlds-runtime:632` | open | `nowhere` | Settled at the pin: `Samples/OpenWorld/Assets/Worlds/Island.stworld` holds a cooked index (`MaxBodiesInRadius` 9161, `PersistentBodies` 98), and `Island.stscene` saves `MaxBodies` 11452 |

## Not taken

none

## Questions for the planner

none
