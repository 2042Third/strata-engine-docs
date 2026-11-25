# Brief: `worlds/streamer`

| Field | Value |
| --- | --- |
| Title | The streamer |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `worlds/grids`, `core/jobs` |
| From | worlds-runtime ch. 5 (sources, wanted and keep sets, hysteresis, view bias, total order, concurrency, failures, adoption, idle cost, determinism tests) |
| Unit | `plan/allocation/worlds.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `adoption` | Adoption | - |
| `streaming-distance` | Streaming distance | - |
| `streaming-source` | Streaming source | - |
| `view-bias-worlds` | View bias (worlds) | - |
| `wanted-cell` | Wanted cell | - |
