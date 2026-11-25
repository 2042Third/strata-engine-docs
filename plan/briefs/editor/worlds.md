# Brief: `editor/worlds`

| Field | Value |
| --- | --- |
| Title | Editing a streamed world |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `editor/play-mode`, `editor/recovery`, `worlds/streamer` |
| From | worlds-runtime ch. 7 (`EditorWorld`, pins, dirty marks through the undo observer, re-celling, the two-phase save, the play copy, recovery, the cell map and overlay caching) |
| Unit | `plan/allocation/editor.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `editor/worlds` — Editing a streamed world

**Covers.** The problem: the editor shows only the part of a world around its camera, yet an edit must go into the right
cell's file, undo must know which cell an entity belongs to, a save must write only what changed, and Play must copy
only what is loaded. The naive answers are named with their failure: copy the whole world to play (it does not fit),
keep edits in the persistent scene (cells never change), save every cell (minutes for one moved crate). The idea: an
editor world that streams around the editor camera, marks what each undo step touched, moves edited entities into the
cell at their position within the same step, and saves in two steps. The code in order: `EditorWorld` is attached when
the edited scene is a world's persistent scene and streams with its own `WorldStreamer`; the edit settings (edit layer,
visible layers, radius scale: `world.edit`); the reasons a cell stays loaded (`world.loadCells` pins, the selection,
undo steps that asked for a cell until the next save, dirty and saving cells), merged in `SyncPins`; dirty tracking as
an observer of the undo stack; cells in undo steps (`EntityState::Cell`, `LinkCells`, `CheckCells`, and a step that
touches an unloaded cell fails, asks for the cell through `ISceneCellLoader`, and is retried); re-celling inside
`CommitEdit` (`Recell`, new cells made in memory with derived handles) and its rules: only top-level entities change
cell, and a child belongs to its top-level ancestor's cell, so editing a child moves nothing; an entity moves only
within its own layer; entities of the persistent scene stay there; a move into a cell that exists but is not loaded
leaves the entity in its old cell and loads the cell; `world.moveEntities`, the only way to another layer or to the
persistent scene, refuses children, checks every target before it moves one, and no menu runs it; the save in two
requests to the `DocumentSaver` (the persistent scene and the dirty cells from one snapshot, then the World document
with fresh index entries once their stamps exist; saved only after that); the play copy (`PrepareRuntimeCopy` adopts
fully loaded cells, drops partly loaded ones and pins dirty cells); recovery of a world's cells; cell IO (streamed,
cancellable reads of cell documents); the world commands and the defaults of `world.create`, and what `world.setLayers`
refuses: removing a layer that has cells, or changing a layer's cell size, unless `deleteCells` moves those cells to the
trash (content is never re-gridded), and cells loaded in the open world even with `deleteCells`; a rename moves the
layer's folder, and the whole change is one undo step. Then how a world looks in the editor: the cell map and the
viewport's cell bounds, rebuilt only when the world's state version changes, the Hierarchy's world strip and its search
by layer and cell, the Inspector's cell line, and the Asset panel with New > World. The rules: never `Scene::Copy` a
whole world; cell membership changes only through `Scene::SetSubSceneOf` and `EditorWorld`; only `EditorWorld` writes
cell documents, through the `DocumentSaver`; mark saved only after the World document is written; UI code draws cached
views. The example makes a first world with `world.create` and reads its edit layer and cell map; then, in a copy of
`Samples/OpenWorld`, it drags a crate across a cell border, undoes, redoes, saves, and reads `world.status` before and
after. The trace exercise stops in `Recell` during that drag. What `PrefabSync` does with instances in cells that load
later is stated as read in the code, not run (a check before writing). Afterwards the reader can change how the editor
edits worlds without losing an entity between cells.

**Leaves out.**

- Grids, cell keys and layers → `worlds/grids`
- How the streamer decides what loads → `worlds/streamer`
- The cook and the physics capacity of a world → `worlds/physics-scripts`
- The Streaming panel itself → `editor-ui/instrument-panels`
- Making a world as a game maker → `make/large-worlds`

**Fit.** `over`: about 7,350 words against L (5,000). Counted again from the sections, with the rules of re-celling,
what `world.setLayers` refuses, the Check item and the trace exercise: nineteen features, three excerpts, eleven figures
(eight of them screenshots), five rules and two examples pass L's top; the next size is XL (8,000) (S2).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-core:115` | feature | home | Cells in undo: a step that touches an unloaded cell fails, asks the world for the cell, and is retried |
| `worlds-runtime:274` | concept | home | Editing a streamed world: the problem and Strata's answer; the concept's mistake, editing a child entity whose cell is its top-level ancestor's, taught with the rules of re-celling (`worlds-runtime:104`) |
| `worlds-runtime:99-103`, `worlds-runtime:105-109` | feature | home | `EditorWorld`, edit settings, keep-loaded reasons, dirty tracking, cells in undo steps, `MoveEntities`, the world save, the play copy, recovery, cell IO |
| `worlds-runtime:104` | feature | home | Re-celling (`Recell` inside `CommitEdit`, new cells in memory with derived handles) and its rules (about 150 words): only top-level entities change cell, children follow their top-level ancestor; an entity moves only within its own layer; entities of the persistent scene stay there; only `world.moveEntities` moves an entity to another layer or to the persistent scene, and it refuses children, and no menu runs it; a move into a cell that exists but is not loaded leaves the entity in its old cell and loads the cell. At the pin: `StrataEditor/src/Editor/EditorWorld.cpp:289-296`, `:315-345`, `:347-391` (`:365`, `:378`); `git grep -n "world.moveEntities" -- StrataEditor/src/Panels StrataEditor/src/UI` finds nothing |
| `worlds-runtime:111-112` | feature | home | The world commands and the defaults of `world.create` |
| `new:73` | feature | home | What `world.setLayers` refuses (about 120 words, beside the world commands): removing a layer that has cells, or changing a layer's cell size, unless `deleteCells` moves those cells to the trash, since content is never re-gridded; cells loaded in the open world even with `deleteCells`; a rename moves the layer's cell folder; the whole change is one undo step. Evidence: `StrataEditor/src/Editor/EditorWorldCommands.cpp:670-675`, `:740-747`, `:748-754`, `:784-799` |
| `worlds-runtime:113-117` | feature | home | The cell map, the Hierarchy's world strip and search, the Inspector's cell line, the viewport's cell bounds, the Asset panel and New > World |
| `worlds-runtime:326` | code | home | `StrataEditor/src/Editor/EditorWorld.cpp:275-345`: `EnsureCellSubScene` and `Recell` |
| `worlds-runtime:327` | code | home | `StrataEditor/src/Editor/EditorWorld.cpp:477-535`: `SyncPins` and `Update` |
| `worlds-runtime:328` | code | home | `StrataEditor/src/Editor/EditorWorld.cpp:760-799`: `PrepareRuntimeCopy` |
| `worlds-runtime:364` | figure | home | The editor world |
| `worlds-runtime:366` | figure | home | The world save as a sequence |
| `worlds-runtime:369` | figure | home | Play from the editor |
| `worlds-runtime:388-392` | figure | home | Screenshots of a world in the editor: the Hierarchy's strip, the Cells chip, the cell map; the cell map of the Streaming panel (`worlds-runtime:392`) is one capture set with `editor-ui:579` on `editor-ui/instrument-panels`, made once (R34, D42), and this page's caption says what it teaches: the world's cells as the editor keeps them |
| `worlds-runtime:395-399` | figure | home | Screenshots: the cell map's menu, the Inspector's cell line and search, an unsaved cell, the Asset panel with `world.info`, New > World |
| `worlds-runtime:414-420` | rule | home | Never copy a whole world; membership only through `SetSubSceneOf` and `EditorWorld`; only `EditorWorld` writes cells; saved only after the World document |
| `worlds-runtime:455` | rule | home | UI code draws cached views of the world: the cell map and cell bounds rebuild only on a state version |
| `worlds-runtime:467` | hands-on | home | The example: a first world, its edit layer and its cell map |
| `new:57` | hands-on | home | Trace it yourself (D27): in a copy of `Samples/OpenWorld`, drag a crate across a cell border with a breakpoint in `EditorWorld::Recell`, and name the cell it leaves and the cell it joins within the same undo step. Evidence: `StrataEditor/src/Editor/EditorWorld.cpp:275-345` (`Recell` at `:315`) |
| `new:58` | open | home | Check: `PrefabSync` with cells. The claim: `PrefabSync` catches a prefab's instances up once per prefab and scene, the first time it looks at the prefab, so a cell that streams in after another cell already used the prefab may keep its old instances; cells not loaded since a prefab changed keep them in their files, and an export packs those files as they are. The page states it as read in the code, not run, and the brief is not blocked (R39); after a result, about 100 words. Evidence: `StrataEditor/src/Editor/PrefabSync.cpp:174-181`, `:205-241`; `Docs/Manual/Worlds.md:100` says prefab changes reach a cell's instances when the cell loads in the editor; `git grep -n -i prefab -- StrataTests/src/Editor/EditorWorldTests.cpp` finds nothing |
| `worlds-runtime:540` | term | use | Adoption |
| `worlds-runtime:541-545` | term | home | Re-celling, edit layer, dirty cell, cell map, cell bounds |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The streamer, its sources and pins | `worlds/streamer` | must |
| Grids, cell keys and layers | `worlds/grids` | must |
| Sub-scenes and `Scene::SetSubSceneOf` | `world/sub-scenes` | must |
| Undo observers, `CommitEdit` and `EntityState` | `editor/undo` | must |
| The `DocumentSaver` and save points | `editor/saving` | must |
| The running copy | `editor/play-mode` | must |
| The recovery journal | `editor/recovery` | must |
| Derived handles | `assets/handles-meta` | helps |
| Content stamps of assets | `assets/importing` | helps |
| The trash and undoable file operations | `editor/trash-references` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `cell-bounds` | Cell bounds | - |
| `cell-map` | Cell map | - |
| `dirty-cell` | Dirty cell | - |
| `edit-layer` | Edit layer | - |
| `re-celling` | Re-celling | - |
