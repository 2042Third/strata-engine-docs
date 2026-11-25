# Brief: `worlds/grids`

| Field | Value |
| --- | --- |
| Title | Grids, keys and layers |
| Kind | I |
| Size | M |
| Tracks | E |
| Needs | `assets/handles-meta`, `world/serialization`, `worlds/why-streaming` |
| From | worlds-runtime ch. 3 (`WorldData`, validation, grid math, key packing, file layout and derived handles, the index) |
| Unit | `plan/allocation/worlds.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `cell-key` | Cell key | WorldCellKey |
| `grid-origin` | Grid origin | - |
| `index` | Index | - |
| `world-asset` | World asset | .stworld |
