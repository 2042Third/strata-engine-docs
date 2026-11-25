# Brief: `worlds/why-streaming`

| Field | Value |
| --- | --- |
| Title | Why levels must stream |
| Kind | C |
| Size | M |
| Tracks | E |
| Needs | `world/sub-scenes`, `assets/residency`, `basics/numbers` |
| From | worlds-runtime ch. 1 (the memory problem, the industry's approaches, Strata's choice, float precision and HLOD as open problems); home of the 20 km limit |
| Unit | `plan/allocation/worlds.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `cell-worlds` | Cell (worlds) | - |
| `hlod` | HLOD | - |
| `persistent-scene` | Persistent scene | - |
| `world-worlds` | World (worlds) | - |
