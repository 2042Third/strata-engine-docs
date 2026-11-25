# Brief: `make/large-worlds`

| Field | Value |
| --- | --- |
| Title | Large worlds |
| Kind | T |
| Size | L |
| Tracks | G |
| Needs | `make/levels-saves` |
| From | gamedev "Large worlds" (§1.16, concept 22; hands-on G13); worlds-runtime "Building a World in the Editor"; scripting "The gameplay API, part 3": `World`, `WorldCellRequest` (prefetch before a teleport); the Play check in the editor and, for the exported game, "A world that waits for its ground" (kept here, not in `make/export`: `make/export` comes before any world on track G, and `make/export` says it in one sentence with a link here) |
| Unit | `plan/allocation/make-b2.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `make/large-worlds` — Large worlds

**Covers.** The tutorial turns a small level into a streamed world, on the page's own example: a project whose player is
Coin Run's rolling ball and whose props are a few nature prefabs (the starting checkpoint). The idea comes first, in a
maker's words: a large level cannot stay loaded whole (memory, and the wait to load it), so a world keeps a persistent
scene that never unloads (the player, cameras, lights, the sky, managers, screen UI) and splits the rest into layers of
square cells, each layer with its own cell size and streaming distance; streaming sources decide which cells load (the
diagram of cells around a source, and a prefetch before a teleport). Then the sections, each ending in a checkpoint.
Make the world: **New ▸ World** in the Content Browser writes a World asset and its persistent scene and opens it; the
Asset panel lists its four layers (Terrain, Buildings, Props and Gameplay, 64 m cells streaming four cells away; Terrain
loads before a game starts). Fill its cells: the Hierarchy's world strip and its edit layer (Persistent for the player,
the camera and the managers; Terrain for the ground's plane tiles; Props for the level's content), the prefabs dragged
in, the Inspector naming an entity's cell ("Cell: Props (3, -1)"), an entity moved across a border changing cell in the
same undo step, and the Hierarchy's search `l:Props`; a gotcha: choose the edit layer before creating, because a new
entity goes into that layer's cell and a moved one stays in its own layer, and children belong to their top-level
parent's cell. See the cells: the viewport's **Cells** chip (loading, loaded, unloading), the cell map in **View ▸
Streaming** (unsaved cells, pins, sources; **Load and pin**); flying away and back; Save writes only what changed, and a
prefab changed later reaches a cell's instances only when the cell loads in the editor, so cells that use it are loaded
and saved before an export (the page says that this was read in the code, not run). The player as the streaming source:
the ball in the persistent scene with a Streaming Source component (Radius, Layers, Priority); Play, and the cell map
follows it; roaming things belong in the persistent scene, because a body unloads with the cell it loaded with; keep the
player saved there with its source, because the exported game loads the start cells around the saved sources before any
script runs, so a player that a script spawns or moves (to a position from a save file) needs a prefetch first, while
Play in the editor starts from the cells the editor has loaded. **Cook** in the Asset panel, and what its numbers and
warnings say, with a gotcha: the physics room it reserves counts only the enabled streaming sources saved in the
persistent scene (at least one, the largest radius per layer), so sources a game spawns later are not counted. A
teleport: a script asks for the cells around a far marker with `World::RequestCellsAround`, waits for
`World::IsLoadedAround` and for a raycast to find the ground, then teleports the ball and releases the request (the Open
World's `Explorer` code, quoted); without the prefetch the ball falls through ground that is not there yet. Why the
raycast, in one sentence: `IsLoadedAround` says the cells are loaded, and a mesh collider in them may still wait for its
shape, so a hit is the test of collision (read in the code, not run). A layer switched off from a script with
`World::SetLayerEnabled`; a forgotten `WorldCellRequest` keeps its cells loaded until `Release` or the scene stops, and
requests and layer toggles belong to the running scene. The exported world: the export with the loading scene of
`make/levels-saves`, run, waiting for the Terrain layer's cells and their collision before the ball drops ("a world that
waits for its ground"). The limits and what Strata does not do: worlds within 20 km of the origin (positions are kept to
about 2 mm there) and no origin rebasing; distant cells are not drawn, with no simplified far versions (match fog and
the camera's far plane to the streaming distances); no terrain system (the samples' terrains are meshes made by tools);
a moving body cannot pass from one cell to another. A last look at the Open World sample's island. The exercise moves a
plain scene 50 km from the origin: it still draws without shaking, which is why the limit is about the precision of
positions, not the renderer. At the end the reader can build, play, cook and export a streamed world and move a player
across it safely.

**Leaves out.**

- Why levels stream, and floating-point precision far from the origin → `worlds/why-streaming`
- The World document, its grid and the streamer's rules → `worlds/grids`, `worlds/streamer`
- What a world reserves in physics, and prefetching as the engine does it → `worlds/physics-scripts`
- How the editor keeps cells, saves and play copies → `editor/worlds`
- Changing a world's layers (cell size, distance, Load Before Start), a step with no menu or button → `make/commands`
- Loading scenes and scene switches → `make/levels-saves`
- Exporting in general → `make/export`
- Measuring a world's streaming in the exported game → `make/performance`

**Fit.** `fits`: about 4,600 words against L (5,000): the idea with its diagram, seven step sections of about 18 steps
with their gotchas, one excerpt of 39 lines, the limits with the four not-done entries in one paragraph, and the
exercise take the most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:210` | feature | home | Worlds for makers: New ▸ World, layers (cell size, streaming distance, Load Before Start), the edit layer strip, entities re-celled by moving, the Cells chip, the cell map (load and pin), Save of changed cells, Cook, Play from loaded cells, `StreamingSource`, the scripts' `World` calls, the limits |
| `gamedev:344` | concept | home | Large worlds: why stream, cells, layers, sources, prefetch before a teleport, precision; the mistake of a player in a cell |
| `gamedev:385` | code | home | `Samples/OpenWorld/Scripts/Explorer.cpp:209-247`: the prefetch before a teleport, the wait for the cells and a raycast to the ground, the teleport and the request released |
| `gamedev:428` | figure | home | World streaming: the persistent scene and layers of cells around a source with their radii; the teleport's prefetch |
| `gamedev:457` | figure | home | World editing in the Open World copy: the Hierarchy's strip with the edit layer, the Cells chip, the cell map in the Streaming panel; a capture that shows a fox names the fox's authors and license in its caption (`appendix/credits` holds the full entry) |
| `gamedev:514` | rule | home | Keep worlds within 20 km; roaming things in the persistent scene |
| `gamedev:515` | rule | home | Prefetch cells before a teleport |
| `gamedev:546` | hands-on | home | G13: a small world, props in a layer, a streaming source on the player, a teleport with prefetch (New ▸ World in place of `world.create`) |
| `gamedev:649` | term | home | World, persistent scene, layer, cell, streaming source, edit layer, cook |
| `gamedev:650` | term | home | Prefetch |
| `render-core:670` | hands-on | home | Exercise: a plain scene 50 km from the origin draws as well as at the origin; what still loses precision there |
| `new:2` | not-done | home | Terrain: a terrain system, sculpting and painting; the samples' terrains are meshes made by `Tools/GenerateIslandTerrain.py` and `Tools/GenerateShowcaseTerrain.py`. Evidence: `git grep -ni terrain 822a7a46 -- Strata/src` finds only comments (`Strata/src/Strata/Renderer/Mesh.cpp:447`, `RenderScene.h:94`, `SceneRenderData.h:695`, `SpatialIndex.h:20`, `Strata/src/Strata/World/WorldAsset.h:19`); `Docs/Roadmap.md:1694-1695` |
| `new:3` | not-done | home | Bodies that move from one world cell to another: a moving body unloads with the cell it loaded with. Evidence: `Docs/Releases/0.7.0.md:387-388`; `Docs/Manual/Worlds.md:97-98` |
| `new:8` | open | home | Check: `PrefabSync` with cells. Prefab changes reach a cell's instances when the cell loads in the editor; cells not loaded since the change keep their old instances in their files, and an export packs those files as they are. `PrefabSync` catches a prefab's instances up once per prefab and scene, the first time it looks, so a cell that loads after another cell used the prefab may not catch up; no test covers cells. Until the engine's agents run the check, the page tells the reader to load and save the cells that use a changed prefab, and says that this was read, not run. Evidence: `Docs/Manual/Worlds.md:100`; `StrataEditor/src/Editor/PrefabSync.cpp:174-181`, `:205-241`; `git grep -n -i prefab 822a7a46 -- StrataTests/src/Editor/EditorWorldTests.cpp` finds nothing |
| `new:9` | open | home | Check: The pending window of mesh colliders. `World::IsLoadedAround` reports loaded cells, whose entities exist, and the SDK's comment says that the ground there has collision then; a mesh collider's body stays pending until its mesh data is in and its shape is cooked on a job, so a cell whose ground is a mesh collider may count as loaded before it collides. The teleport waits for a raycast hit, which is the test of collision, and the page says that this was read, not run (the island's ground is in the persistent scene, so the sample's raycast finds the ground's height). Evidence: `StrataScriptCore/Include/StrataScript/World.h:38-41`; `Strata/src/Strata/Physics/PhysicsWorld.h:41-43`, `:129-132`; `Samples/OpenWorld/Scripts/Explorer.cpp:229-233` |
| `new:4` | not-done | home | Worlds beyond 20 km from the origin, HLOD (distant cells are not drawn) and origin rebasing. Evidence: `Docs/Releases/0.7.0.md:386, 414`; `Docs/Roadmap.md:1693, 1706` |
| `worlds-runtime:24-25`, `worlds-runtime:29` | feature | use | Layers, cells and the limits (`c_SupportedExtent` 20 km) |
| `worlds-runtime:41-42` | feature | use | The World and Streaming Source components |
| `worlds-runtime:47-48` | feature | use | The exported game's prepared start, which waits for the start cells around the sources saved in the persistent scene before any script runs; Play in the editor starts from the cells the editor has loaded (`Strata/src/Strata/World/WorldStreamingSystem.cpp:276-310`; `StrataEditor/src/Editor/EditorContext.cpp:1382-1385`; `Docs/Manual/Worlds.md:68-71`) |
| `worlds-runtime:89` | feature | use | The SDK's `World` and `WorldCellRequest`: a request holds its cells until `Release` or the scene stops, and requests and layer toggles belong to the running scene (`StrataScriptCore/Include/StrataScript/World.h:14-36`; `Strata/src/Strata/World/WorldStreamingSystem.cpp:187-191`; home `worlds/physics-scripts`) |
| `worlds-runtime:104` | feature | use | Re-celling as a maker meets it: a new top-level entity goes into the edit layer's cell, a moved entity changes cell within its own layer, children belong to their top-level parent's cell (`StrataEditor/src/Editor/EditorWorld.cpp:315-345`; home `editor/worlds`) |
| `worlds-runtime:105-106`, `worlds-runtime:110`, `worlds-runtime:112-117` | feature | use | Moving entities between cells, the world's save, the cook (which counts only the enabled streaming sources saved in the persistent scene, at least one: `StrataEditor/src/Editor/WorldCook.cpp:76-81`, `:313-325`), the defaults of a new world, the cell map, the Hierarchy's strip and search, the Inspector's cell line, the Cells chip, the Asset panel and New ▸ World (home `editor/worlds`) |
| `worlds-runtime:185` | feature | use | The Open World sample as the last look |
| `worlds-runtime:227`, `worlds-runtime:251`, `worlds-runtime:268`, `worlds-runtime:272` | concept | use | Why a level must be bounded, streaming sources, floating-point range, no HLOD |
| `worlds-runtime:388`, `worlds-runtime:390`, `worlds-runtime:392`, `worlds-runtime:394`, `worlds-runtime:396`, `worlds-runtime:399` | figure | use | The Open World in the editor with the strip, the Cells chip, the cell map (editing and playing), the Inspector's cell line, New ▸ World; a capture that shows a fox names the fox's authors and license in its caption |
| `worlds-runtime:403` | figure | use | The exported Open World: its loading scene, then the island; a capture that shows a fox names the fox's authors and license in its caption |
| `worlds-runtime:422`, `worlds-runtime:438` | rule | use | Worlds stay within 20 km; roaming objects belong in the persistent scene |
| `worlds-runtime:467`, `worlds-runtime:469`, `worlds-runtime:473`, `worlds-runtime:475`, `worlds-runtime:477` | hands-on | use | A first world, a source on the player, prefetch before a teleport, a layer toggled from gameplay, cook and read the numbers |
| `worlds-runtime:513-517`, `worlds-runtime:522`, `worlds-runtime:532`, `worlds-runtime:542`, `worlds-runtime:544` | term | link | World, World asset, persistent scene, layer, cell, streaming source, `LoadBeforeStart`, edit layer, cell map |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Prefabs, and placing them by dragging into the Scene view | `make/prefabs` | must |
| Position and scale in meters | `make/transforms-units` | must |
| The start scene and the loading scene | `make/levels-saves` | must |
| Exporting the game and running it | `make/export` | must |
| Finding an entity by name and reading its transform in a script | `make/scripting-scene` | must |
| A raycast and teleporting a body | `make/physics` | must |
| `std::optional` (the raycast's hit) | `basics/programming-3` | must |
| Input actions read by a script | `make/input` | must |
| Undo | `make/project-files` | helps |
| A UI image used as a fade | `make/hud` | helps |
| Height fog and the camera's far plane | `make/look` | helps |

**Starting state.** The book's start checkpoint of the tutorial file, downloadable: a new project from the Basic 3D
template holding a player prefab (Coin Run's ball with its `Move` action, its rolling script and a camera that follows
it), three nature prop prefabs from Kenney's Nature Kit (CC0, credited in the checkpoint's `CREDITS.md`), a loading
scene as `make/levels-saves` built it, and a `Teleport` script with its key unbound. No world yet.

**Command-only steps.** none

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `prefetch-make` | Prefetch (make) | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-make-b2-2 | must | shape | `make/commands` (Starting state; `animation:185`, `animation:190`, `worlds-runtime:111`, `render-indirect:540`) | The page starts from Coin Run's end checkpoint: a rolling ball and coins. That project has no skinned model with clips, no world, no reflection probe and no global illumination, so the steps `animation.createController`, `animation.preview`, `world.setLayers`, `lighting.bakeProbes` and the GI capture have nothing to act on. | The Starting state names the project each section opens, each a download of the book (the end checkpoints are planned already; the last two are states of those pages' steps, which the book adds as downloads): Coin Run's end for the scatter, the batch and the store-page captures; the end checkpoint of `make/animation` (its robot and clips) for the controller and the preview; the end checkpoint of `make/large-worlds` for `world.setLayers`; the courtyard of `make/reflections` with its probe, and the room of `make/gi` with Global Illumination on, for the bake and the GI view. About 60 words. | `allocation/make-b2.md:800-807`, `:869-870`, `:875-876`; `outline-1.md:196` (Coin Run as a rolling ball); pin: `StrataEditor/src/Editor/EditorAnimationCommands.cpp:153-157` (each state plays an animation clip); `StrataEditor/src/Editor/EditorWorldCommands.cpp:670-673` (a world's layer list); `StrataEditor/src/Editor/EditorLightingCommands.cpp:872-883` (the scene's probes) |
| critic-make-b2-4 | must | missing-item | `make/large-worlds` (Make the world; the player as the streaming source; `gamedev:210`, `worlds-runtime:112-117`) | **New ▸ World** writes a persistent scene filled from the Basic 3D template: a Primary Main Camera with an audio listener, the Sun, the Sky, a 20 m Ground with its collider at height 0, and a Post Process. The starting checkpoint's player prefab brings its own follow camera. The first Primary camera in hierarchy order draws the game, so Play shows the template's fixed view, and ground tiles laid at height 0 overlap the template's Ground. | After New ▸ World, one step deletes the template's Main Camera and its Ground (or keeps the Ground as the start pad and lays the tiles around it), with one sentence why: the first Primary camera in the Hierarchy draws the game, and two surfaces at one height flicker. About 70 words. Read in the code, not run. | `allocation/make-b2.md:467-470`, `:566-569`; pin: `StrataEditor/src/Panels/ContentBrowserPanel.cpp:363-371` (New ▸ World runs `world.create`); `StrataEditor/src/Editor/EditorWorldCommands.cpp:636-639` (`ProjectTemplates::Populate(ProjectTemplates::c_Basic3D, persistent)`); `StrataEditor/src/Editor/ProjectTemplates.cpp:51-55`, `:77-86`; `Strata/src/Strata/Scene/Scene.cpp:867-881` (the first Primary camera in hierarchy order) |
| critic-make-b2-14 | should | missing-item | `make/large-worlds` (the teleport; `gamedev:385`, `gamedev:515`) | The quoted teleport moves the explorer's character controller or, while flying, writes its transform. The page's player is Coin Run's ball, a dynamic body, which `make/physics` teaches to move only with `RigidBody::Teleport`, because a written transform moves the body at the next fixed step. `Teleport` keeps the body's velocities, so the ball arrives rolling as fast as it left. | After the excerpt, the page's own line for the ball: `GetEntity().GetRigidBody().Teleport(...)` with its velocity set to zero, and one sentence on why it differs from the sample's. About 60 words. | `allocation/make-b2.md:485-487`, `:522`, `:566-569`; `allocation/make-a.md:1272`, `:1339`; pin: `Samples/OpenWorld/Scripts/Explorer.cpp:236-239`; `StrataScriptCore/Include/StrataScript/Physics.h:61-65`, `:117-132`; `StrataScriptCore/Include/StrataScript/Entity.h:76` |
