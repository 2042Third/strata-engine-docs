# Brief: `draw/render-scene`

| Field | Value |
| --- | --- |
| Title | The render scene: persistent proxies |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `world/interpolation`, `world/sub-scenes`, `core/jobs` |
| From | render-scene; home of the render scene's records and change logs, the lights' records included (what a light record holds is `light/lights`') |
| Unit | `plan/allocation/draw.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `draw/render-scene` — The render scene: persistent proxies

**Covers.** The job: the renderer's own, persistent record of every entity of one scene that has a
`MeshRendererComponent`, kept current from change signals, and the change logs its readers follow. Culling and drawing
are not its job. The problem section is one paragraph that links `draw/entities-to-draws`. The map: one `RenderScene`
per scene, made on first use in the registry's context and shared by every renderer of that scene (viewport, capture,
thumbnails); main thread only. The contract: code that writes `MeshRendererComponent` fields or transforms signals the
change (the `AGENTS.md` rule, from the transform contract), and readers follow the logs by version. The toy is a proxy
store of about 60 lines: a dense array per field, a free list and a queue of dirty entities.

The real code, in the order data flows. The class comment (`RenderScene.h:73-112`) is read first, as the whole design
in prose. Proxies in structure-of-arrays form with stable indices and free ranges (why slots change hands, and why the
motion history and the fade state check the entity ID); the proxy flags. Listening to EnTT's signals into a
de-duplicating pending queue, then `Sync`: the pending entities, the scene's world-transform change log or the full
refresh when the log no longer reaches back, the interpolated set (proxies are placed at drawn transforms), render
transforms from a pose provider, layouts, poses, the index refresh and Debug validation. `UpdateProxyPlacement`: the
determinant's sign marks a mirrored proxy (`draw/mirrors-camera-relative` teaches what follows), zero or non-finite
transforms are not drawable, and the bounds come from the pose, the mesh layout, the bounds the asset database recorded,
or placeholder bounds around the entity, which make the mesh requested as if in view (a terrain whose origin is out of
view still loads). Mesh layouts learned from loaded meshes and kept through eviction, while the mesh's source is the one
the layout was learned from: a mesh reimported while it was not loaded loses its layout, so that its new bounds are not
culled with the old ones, and a render scene that was not rendered for a while catches up through the asset manager's
content version. Dense mesh and material slots and
the material users. Instances: one 64-byte `InstanceData` per submesh in one persistent array, written only where the
bytes differ, at most 2^27 of them, and the rule that `InstanceData` stays 64 bytes. The three bounded change logs with
versions and floors (overflow means "read everything"). Then what the scene's life asks of it: prepared loads that
build proxies in chunks within the frame's `SceneWorkBudget`, clones at play start copied member by member (the GPU
halves of both are `draw/render-scene-gpu`'s), and the light records, which are render-scene records with their own log
(what a light record holds is `light/lights`'). What the scene's life costs, as the perf tests measure it: a play start
on 1,000,000 rendered cubes and the interpolated frames of 32,768 moving cubes, whose budgets are provisional. The
statistics close the walk. How it is tested: `RenderSceneTests`, whose 100,000-cube case reads like a specification, and
the exercise that writes a field without signaling and watches `Validate` fail. The page runs on that 100,000-cube scene.
At the end the reader can say what a proxy holds, why an unsignaled write is a bug, and how a reader of the logs knows
what changed.

**Leaves out.**

- What a light record holds and how lights are chosen → `light/lights`
- The GPU copy that follows the logs → `draw/render-scene-gpu`
- The GPU halves of prepared loads and clones, and the renderer's state at a play start and a scene switch →
  `draw/render-scene-gpu`
- Culling the proxies with the spatial index → `draw/bounds-culling`
- Palettes and posed bounds of skinned proxies → `draw/skinned`
- What a mirrored proxy changes in the pipelines and shaders → `draw/mirrors-camera-relative`
- How drawn transforms are computed → `world/interpolation`
- The transform contract and change signals themselves → `world/scene-graph`
- The running copy that play mode makes → `editor/play-mode`

**Fit.** `fits`: about 5,500 words against L (5,000). Seven excerpts and four diagrams take the most, then the
twenty-one features walked in the order data flows; the scene's life as the perf tests measure it adds about 150 words.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-scene:30-34` | feature | home | The render proxy, one render scene per scene, the proxy flags, signal-driven sync, the full refresh |
| `render-scene:35-36` | feature | home | Proxies placed at drawn transforms; render transforms from a pose provider that may not write the scene |
| `render-scene:37-42` | feature | home | Proxy placement, dense slots, material users, mesh layouts (kept through eviction while the source is unchanged, lost when the mesh is reimported while not loaded, caught up through the asset manager's content version: `Strata/src/Strata/Renderer/RenderScene.h:83-89`), recorded bounds, unknown bounds made visible |
| `render-scene:43-46` | feature | home | Instance data, the instance limit, the three change logs, Debug validation |
| `render-scene:47-50` | feature | home | Prepared loads (the proxies built in chunks), clones at play start (the render scene copied member by member), the light records, `RenderSceneStats`; the GPU halves of loads and clones are `new:26` and `new:27` on `draw/render-scene-gpu` |
| `render-scene:228` | concept | home | Structure of arrays with stable indices and free ranges; slots that change hands |
| `render-scene:294` | concept | home | Change logs and versioned readers: dirty flags against logs with a floor |
| `render-scene:342` | code | home | `Strata/src/Strata/Renderer/RenderScene.h:73-112`: the class comment, the whole design in prose |
| `render-scene:343` | code | home | `Strata/src/Strata/Renderer/RenderScene.cpp:188-236`: the signal handlers and the de-duplicating pending queue (with `ConnectListeners` at 130-140) |
| `render-scene:344` | code | home | `Strata/src/Strata/Renderer/RenderScene.cpp:316-401`: `Sync`, from pending entities to Debug validation |
| `render-scene:345` | code | home | `Strata/src/Strata/Renderer/RenderScene.cpp:647-711`: `UpdateProxyPlacement`, the determinant, the drawable rule, the choice of bounds |
| `render-scene:341` | code | home | `Strata/src/Strata/Renderer/SceneRenderData.h:160-216`: `AffineTransform`, the 64-byte `InstanceData` and the draw-list entry (the entry is read again on `draw/batching`) |
| `render-scene:346` | code | home | `Strata/src/Strata/Renderer/RenderScene.cpp:1168-1239`: the bounded, versioned change logs and their floors (with `WriteInstances` at 1106-1132, writing only where bytes differ) |
| `render-scene:371` | code | home | `StrataTests/src/Renderer/RenderSceneTests.cpp:384-435`: 100,000 cubes, a still sync updates nothing, one move updates one instance |
| `render-scene:390` | figure | home | The proxies' arrays as columns, the proxy index as the row, the free list; an array of structs beside it |
| `render-scene:392` | figure | home | The 64-byte `InstanceData` and the bits of the draw-list entry |
| `render-scene:399` | figure | home | Change logs and versions: a reader's version, the floor, overflow, a proxy changed twice between reads |
| `render-scene:454` | figure | home | Placeholder bounds: a mesh whose origin is out of view still loads and appears, before and after |
| `render-scene:461` | rule | home | Signal every write to `MeshRendererComponent` and transforms |
| `render-scene:472` | rule | home | `InstanceData` stays 64 bytes; per-instance additions go to parallel buffers |
| `render-scene:528` | hands-on | home | Trace a signal: an unsignaled write fails `Validate`, then the fix |
| `render-scene:569-570` | term | home | Render proxy; render scene |
| `render-scene:572-573` | term | home | Slot; instance (`InstanceData`) |
| `render-core:751` | term | home | Instance and `InstanceData` (one placement of a mesh, its 64-byte GPU record): one glossary entry with `render-scene:573`, passed by `gpu` |
| `render-scene:618-619` | term | home | Change log; version and floor |
| `render-scene:633-635` | term | home | Placeholder bounds; mesh layout; recorded bounds |
| `render-scene:651` | term | home | Clone of a render scene |
| `new:25` | feature | home | The scene's life measured: `PerfGPU.Renderer.PlayStartRender1MCubes` (a play start on 1,000,000 rendered cubes clones their render scene and its GPU copy) and `PerfGPU.Renderer.InterpolatedFrame32k` with its `.StepRatio` (32,768 moving cubes cost a step frame's proxy work in every interpolated frame). Both budgets are provisional, so no `perf.<name>` key exists (R41): the page states the targets the file gives (5.0 ms; a ratio of 1.15) and says that the budgets are provisional. Evidence: `StrataTests/Perf/Budgets.json:176`, `:273-274`; `StrataTests/src/Perf/RendererPerfTests.cpp:415`, `:462` |
| `scene-ecs:59` | feature | use | `MeshRendererComponent`, the input the render scene reads |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Arrays of structs against structs of arrays | `basics/data-structures` | must |
| Change signals and the transform contract; the scene's world-transform change reports | `world/scene-graph` | must |
| Entities, components and EnTT's storage | `world/ecs` | must |
| Drawn transforms and Strata's interpolated set | `world/interpolation` | must |
| Prepared loads and the frame's `SceneWorkBudget` | `world/sub-scenes` | must |
| Asset handles | `assets/handles-meta` | must |
| Axis-aligned boxes | `basics/math-geometry` | must |
| Deterministic parallel work in fixed chunks | `core/jobs` | must |
| Meshes and submeshes on the GPU | `gpu/geometry-pool` | helps |
| The determinant of a matrix and its sign | `basics/math-bases` | helps |
| Scene services such as `ISkinningPoses` | `world/systems` | helps |
| Asserts and Debug builds in engine code | `core/conventions` | helps |
| Materials as assets that describe a surface | `light/materials` | helps |
| Bounds recorded at import | `assets/importing` | helps |
| A scene that plays is a copy (`Scene::Copy`) | `world/systems` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `change-log` | Change log | - |
| `clone-render-scene` | Clone (render scene) | - |
| `floor` | floor | - |
| `instance-draw` | Instance (draw) | InstanceData |
| `mesh-layout` | Mesh layout | - |
| `placeholder-bounds` | Placeholder bounds | - |
| `recorded-bounds` | Recorded bounds | - |
| `render-proxy` | Render proxy | - |
| `render-scene` | Render scene | RenderScene |
| `slot` | Slot | - |
| `version` | Version | - |
