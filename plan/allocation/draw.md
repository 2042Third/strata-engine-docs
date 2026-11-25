# Allocation: draw

## `draw/entities-to-draws` — From entities to draw calls

**Covers.** The page starts from what the reader sees: the Showcase sample open in the editor, with the Scene view's
**Stats** chip turned on. The overlay counts the visible proxies, the draw calls and instances they became and the
bytes uploaded, and a still frame uploads no instance at all (the writer takes the sample's numbers from a capture at
the pin, never from memory). The page asks what had to happen between the entities and the GPU. First the
naive answer: walk every entity each frame and issue one draw per mesh. It breaks twice: the walk costs time in
proportion to the whole scene, and every draw costs the CPU a driver call and the GPU a change of state. Then the
ideas, in this order. What a draw call is and why its count matters (instancing, merged geometry and indirect draws
named, as answers). Retained against immediate scene representations: a persistent record per drawable entity, kept
current from change signals, against walking the scene each frame, and the GPU scene as the third answer. A table
compares the three and names engines that use each. Strata's choice: retained render proxies in a render scene, culled,
batched into instanced draws, on two paths, the CPU path (the reference and the fallback) and the GPU-driven path (the
default where the device can do it). The two paths must agree pixel for pixel, and parallel work is merged in chunk
order, so the result never depends on the number of threads; this is a design constraint of the whole part.

Two diagrams are the part's map: "entity to pixels" (who owns which data, on which thread) and the frame's extraction
timeline in two lanes, with each stage linked to the page of this part that explains it. The page ends with the frame's
numbers: what each line of the Stats overlay measures and which stage makes it, and the same numbers read as
`renderStats` from `viewport.capture` (the complete command line to paste, one sentence on what it does, a link forward
to `editor/commands`). Common mistakes: thinking the triangle count is the only cost; thinking fewer draw calls is
always faster. At the end the reader can name the stages from an entity to a draw, read the Stats overlay and
`renderStats`, and say which page of the part explains each number.

**Leaves out.**

- The render scene's records and code → `draw/render-scene`
- How the visible set is found → `draw/bounds-culling`
- Sort keys, batches and indirect arguments → `draw/batching`
- The GPU-driven path and its mode switch → `draw/gpu-driven`
- The passes of the frame and what each draws → `gpu/frame-tour`
- Every `renderStats` key and `SceneRendererStats` field in one table → `reference/renderer`
- Making a game draw fast, for game makers → `make/performance`

**Fit.** `fits`: about 3,100 words against M (3,000). Three concepts with the approaches table take the most, then the
two diagrams and the reading of the frame's numbers.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-scene:215` | concept | home | What a draw call is and why its count matters; the answers engines use |
| `render-scene:221` | concept | home | Retained against immediate scene representations, the GPU scene; "cost follows change and view" |
| `render-scene:331` | concept | home | Two paths that must agree, chunked work merged in order: agreement as a design constraint |
| `render-scene:383` | figure | home | The frame's extraction timeline in two lanes, the CPU path and the GPU-driven path |
| `render-scene:388` | figure | home | Entity to pixels: components, signals, proxy, instances, GPU copy, draw list, vertex shader |
| `render-scene:184` | feature | home | The Scene view's Stats overlay (`ViewportToolbar::DrawStatsOverlay`): its lines at `StrataEditor/src/Panels/ViewportToolbar.cpp:117-131`, a few of the values of `SceneRendererStats` (not most of its fields), and what each line counts |
| `render-scene:181` | feature | home | `renderStats` in `viewport.capture` and `editor.state`: the keys grouped by the stage that makes them |
| `render-scene:522` | hands-on | home | Read a frame's statistics: capture a sample and explain each group of `renderStats` |
| `render-scene:123` | feature | link | The `GPUDriven` mode switch, named; its home is `draw/gpu-driven` |
| `render-scene:30` | feature | link | The render proxy, named; its home is `draw/render-scene` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| What a draw command records: a pipeline, bindings, a range of vertices and indices; command submission | `gpu/how-a-gpu-frame-works` | must |
| The passes of the scene renderer's frame, the depth prepass and forward shading | `gpu/frame-tour` | must |
| Entities, components and the scene's registry | `world/ecs` | must |
| Change signals and the transform contract | `world/scene-graph` | must |
| The CPU and the GPU working on different frames | `start/what-an-engine-is` | helps |
| Deterministic parallel work: ordered records, fixed chunks, serial publish | `core/jobs` | helps |
| Reading and running an editor command | `start/how-to-read` | helps |
| Commands are the API (linked forward from the command line the page gives) | `editor/commands` | helps |

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

## `draw/bounds-culling` — Bounding volumes, frustums and the spatial index

**Covers.** The CPU path, taught first. The job: find the proxies the camera can see, exactly and in time that follows
what is visible, and say how large each looks on screen. The page carries the full section "The problem and how engines
solve it": a per-object test of every proxy is linear in the scene, and engines answer with bounding volume
hierarchies, octrees and loose octrees, uniform and loose grids, and hashing, compared in a table. Then the ideas in
order. Bounding volumes and their transforms: spheres, axis-aligned and oriented boxes, and why transforming only the
minimum and maximum corners is wrong under rotation (`AABB::Transformed`). Frustum culling: six planes extracted from the
view-projection matrix, the positive vertex test of a box against a plane, the three answers inside, intersecting and
outside, and why the test is conservative (a box near a corner passes while it is outside). Strata's `Frustum` type does
this: the Gribb and Hartmann extraction for depth from 0 to 1, where the depth-0 plane is the far plane of reversed Z, an
infinite far plane that comes out degenerate and never culls, and the point, sphere and box tests; a two-dimensional
sketch shows the planes and a box's positive vertex. The toy: a brute-force culler over a list of boxes, then a uniform
grid.

The real code: the positive and negative vertex tests (`SpatialIndex.cpp:56-107`); Strata's loose two-level grid, with
cells of 32 units keyed by the box's centre, cell bounds that are the union of their objects, blocks of 8x8x8 cells and
a separate list for objects longer than four cells; queries that take wholly inside blocks and cells whole and test
straddlers one by one, so the result equals a brute-force scan; constant-time edits and the lazy shrink in `Refresh`;
`CullView`, which queries the frustum, computes each visible proxy's screen fraction in parallel chunks and merges the
marks in chunk order, and the prefetch sphere. The index has another reader: the editor's raycast asks it for the boxes
along a ray, a thin prism of six planes, as the broad phase before its exact tests. A section "How big does it look?"
teaches the screen fraction (the projected bounding-sphere diameter over the viewport height, perspective and
orthographic), which level of detail, request priority, size culling and texture streaming all use, and size culling
with the quality row "Smallest drawn size". Why a grid and not a BVH: proxies move every frame, and a cell move costs
less than a refit. How it is tested: `SpatialIndexTests`, with the reader's own test that compares a sphere query with
brute force, and a timing of brute force against the grid; the "trace it yourself" exercise follows two boxes through
the query. The page runs on a camera over a field of boxes. At the end the reader can extract a frustum's planes, test a
box against them, and explain why the grid's answer is exact.

**Leaves out.**

- The mathematics of planes, boxes and intersection tests → `basics/math-geometry`
- The `AABB` type → `core/math`
- The rest of the editor's raycast → `editor/placement`
- Finding the sun's shadow casters → `light/sun-shadows-1`
- The same tests on the GPU → `draw/gpu-driven`
- What is hidden behind other objects → `draw/occlusion`
- Choosing a level of detail from the screen fraction → `draw/lod`

**Fit.** `fits`: about 5,550 words against L (5,000). The full section on spatial structures and three concepts take
the most, then five excerpts (`Frustum.cpp` and `AABB.cpp` quoted here among them) and three exercises.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-scene:243` | concept | home | Spatial acceleration structures, compared; why a loose grid for moving proxies |
| `render-scene:233` | concept | home | Bounding volumes and their transforms; `AABB::Transformed` and the corner mistake |
| `render-scene:238` | concept | home | Frustum culling: plane extraction, the positive vertex test, conservative results |
| `render-scene:248` | concept | home | The screen fraction, the section "How big does it look?" |
| `render-scene:56-60` | feature | home | The loose two-level grid, exact queries, constant-time edits and lazy shrink, `CullView`, size culling |
| `render-scene:98` | feature | home | `LODSelection::GetScreenFraction` for perspective and orthographic cameras |
| `render-scene:347` | code | home | `Strata/src/Strata/Renderer/SpatialIndex.cpp:56-107`: the positive and negative vertex tests; inside, intersecting, outside |
| `render-scene:348` | code | home | `Strata/src/Strata/Renderer/SpatialIndex.cpp:406-438`: the query that takes whole cells and tests straddlers (with `Update`, 303-345) |
| `render-scene:349` | code | home | `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp:249-328`: `CullView` and `MarkVisibleProxies`, chunks merged in order |
| `render-scene:397` | figure | home | The loose grid in two dimensions, a block, the large-object list, a frustum classifying cells |
| `render-scene:524` | hands-on | home | Write a spatial-index test that compares a sphere query with brute force |
| `render-scene:526` | hands-on | home | Brute force against the loose grid on 100,000 random boxes |
| `new:12` | hands-on | home | Exercise ("trace it yourself"): with a breakpoint in `SpatialIndex::Query`, follow two boxes of the page's field from `CullView` through `QueryFrustum` to the visible list: one in a cell wholly inside the frustum, taken with its cell, and one in a straddling cell, tested alone by `Frustum::IsAABBVisible`; the solution names each function and the overlap each test returned. Evidence: `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp:249-256`, `Strata/src/Strata/Renderer/SpatialIndex.cpp:406-444` |
| `render-scene:595-599` | term | home | Positive vertex test; loose grid; spatial index; screen fraction; size culling |
| `render-scene:613` | term | home | Conservative test |
| `foundation:144` | feature | home | `Frustum` (`Strata/src/Strata/Math/Frustum.cpp:12-73`): Gribb and Hartmann extraction for depth 0 to 1, the depth-0 plane as reversed Z's far plane, a degenerate infinite far plane that never culls; point, sphere and box (positive vertex) tests |
| `foundation:425` | figure | home | Its first sketch: the frustum's planes and a box's positive vertex in two dimensions (the second, the ray from NDC, is drawn on `core/math`) |
| `foundation:636` | term | home | Frustum culling, as Strata tests it; the frustum as a volume is `basics/math-geometry`'s (`render-scene:593`) |
| `editor-core:726` | term | home | Spatial index: one glossary entry with `render-scene:597`; the editor's raycast queries the index with a thin prism of planes (`StrataEditor/src/Editor/SceneRaycast.cpp:116-132`). The word "broad phase" is linked to its home, `physics:499` on `physics/collision-detection` (the merge "Broad phase") |
| `render-scene:79` | feature | use | Extraction in chunks of 2,048 proxies, merged in chunk order |
| `render-scene:183` | feature | use | The quality row "Smallest drawn size (pixels)" |
| `foundation:370` | code | use | `Strata/src/Strata/Math/Frustum.cpp:12-35`, with lines 57-73: the Gribb and Hartmann plane extraction for depth 0 to 1 and the positive-vertex box test, quoted here (book.md's row of frustum and box tests); the item's home row, its reversed-Z projections, is on `core/math` |
| `foundation:373` | code | use | `Strata/src/Strata/Math/AABB.cpp:7-25`: `AABB::Transformed` by Arvo's method, the answer to the corner mistake, quoted here (book.md's row of frustum and box tests); the item's home row is on `core/math` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Planes, boxes, frustums and intersection tests as mathematics | `basics/math-geometry` | must |
| View and projection matrices, the frustum | `basics/math-projection` | must |
| Strata's `AABB` type | `core/math` | must |
| The camera and Strata's clip space | `gpu/coordinates` | must |
| Dot products and vector length | `basics/math-vectors` | must |
| The render scene's proxies and their world bounds | `draw/render-scene` | must |
| Deterministic parallel work in fixed chunks | `core/jobs` | must |
| The cost of operations (big-O) | `basics/data-structures` | helps |
| Perf tests run only in Release | `engineering/perf-lab` | helps |

## `draw/asset-requests` — Asking for assets at draw time

**Covers.** The job: ask the asset manager for exactly what the frame draws, at the right priority, without ever
waiting, and let go of every reference when the frame ends. The problem in a short section: content larger than memory,
and a renderer that must never block. Engines request by visibility with priorities, draw fallbacks meanwhile, and
evict by use. Then Strata's answer in the order data flows. Requests follow visibility: an asset in view is High
priority when it covers more than 5% of the viewport's height and Normal below that, Low within the prefetch distance of
100 units, and an off-view shadow caster's only if it is already resident; `ResolveAssets` walks slots in order, takes
the priority from use bits and reads the geometry's place once per frame. The asset resolve cache: one lookup per
distinct handle per frame, resident-only lookups that never start a load, and references released when the frame ends,
so that what left the view becomes evictable, also for idle renderers. Recording and replay: a still frame replays the
previous frame's lookups in one locked call. Fallbacks: an unloaded material draws as the default material, an unloaded
mesh is skipped, and a mesh of unknown bounds is requested as if in view. Last, what the frame publishes for mip
streaming: the materials drawn, with their largest size on screen and their UV pixels, and their loaded textures. How
it is tested: `Renderer.AssetResolveCache`, whose cases check one lookup per handle per frame and the references let go
when the frame ends, a cache that keeps no asset manager alive, resident lookups that never start loads and prefetches
at Low priority, and a later frame's replay of a frame's lookups in one call. The exercise predicts the requests of
three cubes and checks them with a breakpoint in `ResolveAssets`.

The toy is a per-frame memo in front of a slow lookup. The streaming debug view, chosen from the Scene view's debug view
chip or with `viewport.setSettings` and `debugView` set to `streaming`, shows the requests: the page runs on the
OpenWorld sample as it opens, pending entities tinted, failed ones in a second tint and missing meshes as boxes, and two
captures of one view from a corner of the world with the pending count beside each. At the end the reader can predict
the priority of a request from what the camera sees, and say why the cache's references end with the frame (the rule
"hold handles across frames, not `Ref`s" and its why are `assets/residency`'s).

**Leaves out.**

- The asset manager's queue, states and priorities as it loads → `assets/loading`
- Budgets, eviction and pins → `assets/residency`
- How the published textures choose their mip levels → `draw/mip-streaming`
- The mip debug view → `draw/mip-streaming`
- Requests driven by the GPU's feedback → `draw/gpu-driven`
- The proxies that wait for their GPU upload → `draw/render-scene-gpu`
- How debug views are drawn and the list of them → `gpu/debugging`

**Fit.** `fits`: about 3,650 words against M (3,000). Three excerpts and the five features of requests, the cache,
replay, fallbacks and publishing take the most; the rule on `Ref`s is shown applied and its why is linked.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-scene:261` | concept | home | Asset streaming meets rendering: request by visibility, fall back, evict by use |
| `render-scene:68-72` | feature | home | Requests follow visibility, the resolve cache, recording and replay, the default material fallback, what the frame publishes for mip streaming |
| `render-scene:350` | code | home | `Strata/src/Strata/Renderer/AssetResolveCache.cpp:87-133`: one lookup per handle per frame; resident-only lookups never start loads |
| `render-scene:351` | code | home | `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp:701-743`: `ResolveAssets`, slot order, priority from use bits |
| `new:1` | code | home | `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp:745-777`: `ReuseResolvedMaterials`, a still frame replaying the previous frame's lookups in one call |
| `render-scene:436` | figure | home | The streaming debug view while OpenWorld opens: pending tints, missing meshes as boxes |
| `render-scene:438` | figure | home | Request priorities: two captures from a corner of the world with the pending and material counts |
| `render-scene:464` | rule | home | Never resolve assets per entity; go through the proxies and the frame's resolve cache |
| `render-scene:467` | rule | use | Hold `AssetHandle`s across frames, not `Ref`s, shown applied: the resolve cache drops its references when the frame ends; the rule and its why are `assets/residency`'s |
| `render-scene:629-632` | term | home | Request priority; prefetch distance; asset resolve cache; replay |
| `new:13` | hands-on | home | Exercise ("trace it yourself", done in a debugger): three cubes, one filling a fifth of the view, one far and small in view, one out of view within 100 units; predict each mesh's request (High, Normal, a prefetch), then, with a breakpoint in `ResolveAssets`, follow each mesh slot's use bits to the call they make (`Resolve` at High or Normal, `Prefetch`, or `FindResident` for an off-view caster) and check the prediction; the solution names the function and each slot's bits. Evidence: `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp:701-724`; `StrataTests/src/Renderer/AssetResolveCacheTests.cpp:115` (prefetches request at low priority) |
| `assets:214` | feature | home | The Streaming view (pending and failed tints, placeholder boxes), chosen from the debug view chip or with `viewport.setSettings` (`StrataEditor/src/Editor/StreamingView.h:52-133`); its Mip view is read on `draw/mip-streaming` |
| `assets:502` | figure | home | The streaming view right after a large scene opens, then loaded: one figure with `render-scene:436` |
| `render-scene:42` | feature | use | Meshes of unknown bounds requested as if in view |
| `render-scene:98` | feature | use | The screen fraction that decides High against Normal |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Loading without stalling: asset states, requests and their priorities | `assets/loading` | must |
| Residency, eviction by recency and pins | `assets/residency` | must |
| Shared ownership with `Ref` and what keeps an object alive | `basics/cpp-memory` | must |
| The screen fraction | `draw/bounds-culling` | must |
| Mesh and material slots of the render scene | `draw/render-scene` | must |
| A mutex and the cost of a locked call | `basics/threads` | helps |
| The default material and what a material holds | `light/materials` | helps |
| The list of debug views and how they are drawn | `gpu/debugging` | helps |
| Mip levels of a texture | `assets/textures` | helps |

## `draw/batching` — Batching and instancing

**Covers.** The job: turn the visible proxies into as few draws as the pipeline states allow, the same way on every run
and with any number of threads. The problem section is one paragraph that links `draw/entities-to-draws`. The ideas in
order. Instancing and per-instance data: one draw for many copies, a structured buffer of persistent 64-byte instances,
a per-frame draw list of indices that the vertex shader reads as `u_DrawList[SV_VulkanInstanceID]` (which includes the
base instance, unlike `SV_InstanceID`), and materials read by slot from a buffer. Material-free instancing: the
material is not in the batch key, so 1,000 cubes with 1,000 colours draw in one opaque draw; `BatchAcrossMaterials` off
splits them, for comparison. Sort keys and radix sort: the draw's state packed into a 64-bit `SceneDrawKey` (cascade,
alpha mask, mirrored, double-sided, skinned, mesh slot, submesh, level of detail, and the material only when batching
across materials is off), why churning fields stay out of the high bits, and a stable LSD radix sort that skips bytes
equal in every key, with `SortIndices`, its form for lists of 32-bit values, which sorts the slots `ResolveAssets`
walks. Indirect drawing: draw arguments in a GPU buffer, `drawIndexedIndirect` and `multiDrawIndirect`
(the GPU-written count is `draw/gpu-driven`'s). The toy sorts and batches a list of (mesh, material) pairs in 50 lines.

The real code in the order data flows: extraction in chunks of 2,048 proxies on the job system, merged in chunk order;
the heart of `GatherDraws` (the residency check, size culling, the level of detail with its fade's double entry, the
transparent split, the sort item), with one sentence on the residency check: it asks the render scene's GPU copy whether
a proxy's upload arrived (`IsResident`), the vertex shader reads the instances from that copy's buffer, and
`draw/render-scene-gpu` teaches the copy; `SceneDrawKey` with the `static_assert` that its fields tile 64 bits;
`RadixSort`; `BuildBatches`, where runs of equal keys become batches and the draw list gets one entry per instance; the
draw-list entry (instance in 27 bits, the fade code above); transparent submeshes drawn one at a time, back to front,
glass first; uploads of only the changed range of a list; `BuildDrawArguments` at each mesh's place in the geometry
pool, and `DrawBuckets`, where consecutive batches of one `PipelineKey` and vertex arena share one `setGraphicsState`
and one indirect call where the device has `multiDrawIndirect` and `drawIndirectFirstInstance` (the glossary entry of
the three device features and limits is this page's), split at `maxDrawIndirectCount`. Beside the `SceneDrawKey`
excerpt, the key's widths as limits: submeshes past the 65,536th and levels past the 32nd are not drawn and reported,
material slots past 65,536 share keys and merge batches, which stays correct. How it is tested: the opaque draw counts
of `GPURenderSceneTests` and `RadixSortTests`, with the exercises that move the material into the key and build keys
that need one, three and eight passes, and a trace of one cube from its sort item to the call that draws it. The
measured proof of material-free instancing: 10,000 materials draw in one opaque call and 10,000 distinct meshes in 8
draw commands, values the page reads through generated keys. The page runs on 1,000 cubes with 1,000 materials. At the
end the reader can decode a sort key, predict the draws a scene makes, and say why the material is not in the key.

**Leaves out.**

- Pipeline state objects and the `PipelineKey` cache → `gpu/binding`
- The geometry pool, its arenas and compaction → `gpu/geometry-pool`
- Blending and premultiplied alpha → `light/clearcoat-transmission`
- How the level of detail is chosen and faded → `draw/lod`
- Buckets and indirect draws that the GPU fills → `draw/gpu-driven`
- The shadow passes' draws → `light/sun-shadows-1`

**Fit.** `fits`: about 5,650 words against L (5,000). Six excerpts and three concepts take the most, then three
exercises; the measured counts and the key's widths as limits add about 230 words, and `SortIndices` takes one sentence.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-scene:272` | concept | home | Instancing and per-instance data; the draw list; `SV_VulkanInstanceID` against `SV_InstanceID` |
| `render-scene:267` | concept | home | Sorting draws by an integer key; radix sort; what belongs in the high bits |
| `render-scene:282` | concept | home | Indirect drawing: arguments in a GPU buffer, `drawIndexedIndirect`, `multiDrawIndirect` |
| `render-scene:79-88` | feature | home | Parallel extraction, the sort key, radix sort, material-free instancing, batches and the draw list, the draw-list entry, transparent draws, changed-range uploads, indirect arguments per batch, buckets of pipeline state |
| `render-scene:352` | code | home | `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp:961-1047`: the heart of `GatherDraws` |
| `render-scene:353` | code | home | `Strata/src/Strata/Renderer/SceneDrawKey.h:9-43`: packing the key; the fields tile 64 bits |
| `render-scene:354` | code | home | `Strata/src/Strata/Core/RadixSort.cpp:14-67`: stable LSD radix sort that skips equal bytes |
| `render-scene:355` | code | home | `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp:845-869`: `BuildBatches`, runs of equal keys |
| `render-scene:356` | code | home | `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp:1271-1302`: uploading only the changed range of a list |
| `render-scene:357` | code | home | `Strata/src/Strata/Renderer/SceneRenderer.cpp:2042-2134`: indirect arguments at geometry-pool offsets; `DrawBuckets` |
| `render-scene:394` | figure | home | The 64-bit `SceneDrawKey` with its fields tiling the word |
| `render-scene:440` | figure | home | 1,000 cubes in 1,000 colours: one opaque draw; the same image with `BatchAcrossMaterials` off |
| `render-scene:530` | hands-on | home | Move the material into the key and compare the opaque draws on 1,000 materials |
| `render-scene:532` | hands-on | home | Keys that need one, three and eight passes; checking stability |
| `new:14` | hands-on | home | Exercise ("trace it yourself"): one cube of the 1,000 followed with a debugger from its sort item in `GatherDraws` through `RadixSort` and `BuildBatches` to its draw-list entry (`MakeDrawEntry`) and to the `DrawBuckets` call that draws its batch; the solution names each function and the entry's value. Evidence: `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp:845-869`, `:1036-1046`; `Strata/src/Strata/Renderer/SceneRenderer.cpp:2072-2134` |
| `new:23` | feature | home | The measured proof of the part's claims for batching: `PerfGPU.Renderer.Render10kMaterials.OpaqueDrawCalls` (10,000 materials in one opaque call) and `PerfGPU.Renderer.Render10kUniqueMeshes.DrawCommands` (10,000 distinct meshes in 8 draw commands), read through the keys `perf.PerfGPU.Renderer.Render10kMaterials.OpaqueDrawCalls.Measured` and `perf.PerfGPU.Renderer.Render10kUniqueMeshes.DrawCommands.Measured`; the method is `engineering/perf-lab`'s and the full table `reference/performance`'s. Evidence: `StrataTests/Perf/Budgets.json:155`, `:192`; `StrataTests/src/Perf/RendererPerfTests.cpp:325`, `:405-411`, `:499`, `:513-521` |
| `new:28` | rule | home | The sort key's widths are limits: a submesh past the 65,536th or a level past the 32nd is not drawn, and the renderer reports how many instances it skipped; material slots past 65,536 share keys and merge batches, which stays correct; mesh slots are bounded by `Scene::c_MaxEntities`. Evidence: `Strata/src/Strata/Renderer/SceneDrawKey.h:24-29`; `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp:996-1000`, `:1075` |
| `render-scene:575-578` | term | home | Draw list; draw entry; batch; bucket |
| `render-scene:580-583` | term | home | Sort key; radix sort; material-free instancing; indirect draw |
| `render-scene:585` | term | home | `multiDrawIndirect`, `drawIndirectFirstInstance`, `maxDrawIndirectCount`: the CPU path meets all three first (one indirect call per bucket where the device has the first two, split at the third: `Strata/src/Strata/Renderer/SceneRenderer.h:157-163`); `draw/gpu-driven` links it |
| `render-scene:586-587` | term | home | Base instance; `SV_VulkanInstanceID` |
| `render-core:752` | term | home | Draw list (the frame's array of instance indices the vertex shader reads per instance): one glossary entry with `render-scene:575`, feature and term homed here (R31, D33), passed by `gpu` |
| `render-core:753` | term | home | Indirect draw (a draw whose arguments the GPU reads from a buffer): one glossary entry with `render-scene:583`, passed by `gpu` |
| `render-core:586` | rule | home | `SV_VulkanInstanceID`, not `SV_InstanceID`: the draw list is indexed including the base instance; the rule beside the term `render-scene:587`, passed by `gpu` |
| `foundation:161` | feature | home | `RadixSort` and `SortIndices` (`Strata/src/Strata/Core/RadixSort.h`), the foundation inventory's view of `render-scene:81`; `SortIndices` sorts the used mesh and material slots in `ResolveAssets` |
| `foundation:644` | term | home | Radix sort: one glossary entry with `render-scene:581` |
| `render-scene:341` | code | use | The draw-list entry and `MakeDrawEntry`, read again from `draw/render-scene` |
| `render-scene:60` | feature | use | Size culling inside `GatherDraws` |
| `render-scene:89` | feature | link | The pipeline cache by key, at `gpu/binding` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Pipelines, the `PipelineKey` cache, structured buffers and bindless reads | `gpu/binding` | must |
| The geometry pool and its vertex arenas | `gpu/geometry-pool` | must |
| Bits, shifts and masks; packing keys | `basics/numbers` | must |
| Instances and their slots in the render scene | `draw/render-scene` | must |
| Residency of proxies and of meshes at draw time | `draw/asset-requests` | must |
| Deterministic parallel work in fixed chunks | `core/jobs` | must |
| Uploading buffers through staging | `gpu/upload-queue` | must |
| Sorting and the cost of operations | `basics/trees-graphs` | helps |
| Transparency, blending and glass | `light/clearcoat-transmission` | helps |
| Levels of detail and their fade codes | `draw/lod` | helps |
| The instances live in the render scene's GPU copy; a new proxy draws once its upload arrived | `draw/render-scene-gpu` | helps |

## `draw/lod` — Levels of detail

**Covers.** The job: draw fewer triangles where a mesh is small on screen, without popping and with the same level on
both paths. The problem section teaches the approaches: discrete levels chosen by distance, by screen size or by
geometric error (the screen-space error metric that HLOD systems and Nanite use), continuous levels; transitions by
popping, by a dithered cross-fade or by geomorphing. Strata's choice: discrete levels generated at import with their
error (the import side is `assets/models-gltf`'s), and older levels without errors chosen by halving. The toy picks a
level from a fraction and a list of errors in 30 lines.

The real code. The halving rule (level n below `LODThreshold / 2^(n-1)`) and the error rule (the coarsest level whose
projected error spans at most `LODErrorPixels`), and why the arithmetic looks strange: doublings, one multiplication and
no logarithm, so that the CPU and the GPU choose the same level for the same fraction; the rules are pure functions,
which tools call to show the drawn level; the GPU's copy of the rule in `Include/LODSelection.slang`, where `precise`
keeps the one multiplication from being fused or reordered, and the test shader that runs it for 10,000 fractions. The
quality rows "Level of detail error (pixels)" and "Smallest drawn size (pixels)", with their four presets from a
generated table. `LODCriteria`, which a renderer exposes so that tools show the drawn level. The cross-fade: when a view
instance's level changes, both levels draw for 16 frames with complementary masks of the 4x4 ordered dither, and the
prepass and the forward pass discard by the same test, so the `EQUAL` depth test holds; the fade's state machine
(continuing, reversing, restarting) and its fade codes in the draw-list entry. The LOD debug view tints entities by the
level drawn and reports error pixels per level. What Strata does not do here: billboards and impostors. How it is
tested: `LODSelectionTests`, the test shader of `GPU.Renderer.LODSelection`, and `GPU.SceneRenderer.LODFade`, whose
cases cross-fade a changed level through complementary masks on both paths, switch at once on a camera cut, and fade
levels that cover the same pixels at the same depth by the same mask in the forward pass. The exercise drives
`UpdateLODFade` through a target that changes at frame 5 and back at frame 9, and a "trace it yourself" finds the CPU's
and the GPU's choice of a level. The page runs on a field of props with generated levels, seen in the LOD view at the
Low and Ultra presets. At the end the reader can compute the level a fraction selects under both rules and explain why a
fade must discard alike in both passes.

**Leaves out.**

- Generating levels and their errors at import → `assets/models-gltf`
- The screen fraction → `draw/bounds-culling`
- Ordered dither as a signal idea → `basics/signals`
- The depth prepass and the `EQUAL` test → `gpu/frame-tour`
- The presets and players' graphics options → `image/quality-settings`
- The GPU's level choice inside `Cull.comp` → `draw/gpu-driven`
- Distant cells of a world, which are not drawn → `worlds/why-streaming`

**Fit.** `fits`: about 3,700 words against M (3,000). Four figures (two of them screenshots that need a live capture),
two two-part excerpts and the GPU's copy of the rule take the most, then two exercises.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-scene:253` | concept | home | Levels of detail: the approaches to choosing and to transitions; Strata's choice and why CPU and GPU must agree |
| `render-scene:99-104` | feature | home | The halving rule, the error rule, cross-fades, `LODCriteria`, the LOD debug view, the agreement test shader |
| `render-core:226` | feature | home | LOD selection as pure functions, the render-core inventory's view of `render-scene:102` and `render-scene:104`; `precise` keeps the shader's multiplication of the error rule unfused (`Strata/shaders/Include/LODSelection.slang:24-39`) |
| `render-scene:183` | feature | home | The quality rows "Level of detail error (pixels)" and "Smallest drawn size (pixels)" |
| `render-scene:359` | code | home | `Strata/src/Strata/Renderer/LODSelection.cpp:19-87`: the halving rule and the error rule, written so CPU and GPU agree |
| `render-scene:360` | code | home | `Strata/src/Strata/Renderer/LODSelection.cpp:99-159`: the fade state machine and `IsLODFadeDrawn`, with the Bayer mask of `Strata/shaders/Include/Scene.slang:155-166` |
| `render-scene:411` | figure | home | LOD selection by error: levels and their relative errors against the screen fraction; the halving staircase |
| `render-scene:413` | figure | home | The cross-fade: the 4x4 Bayer matrix, the masks at steps 1, 8 and 15, the state machine |
| `render-scene:430` | figure | home | The LOD debug view on a prop field, at the Low and Ultra presets |
| `render-scene:433` | figure | home | A cross-fade mid-transition, zoomed so both levels' dither shows (a live capture) |
| `render-scene:541` | hands-on | home | Simulate a fade with `UpdateLODFade` and check the codes against `LODSelectionTests` |
| `new:15` | hands-on | home | Exercise ("trace it yourself"): with a search, find the two places that choose a submesh's level, `SceneRenderer::SelectLOD` (called by `GatherDraws`) and `ChooseLODFor` (called by `Cull.comp` through `ChooseLOD`), and show that each takes the levels' errors where the submesh has them and halves the fraction otherwise; the solution names the files, functions and lines. Evidence: `Strata/src/Strata/Renderer/SceneRenderer.cpp:2018-2021`, `Strata/src/Strata/Renderer/LODSelection.cpp:72-87`, `Strata/shaders/Include/Culling.slang:200-213` |
| `render-scene:600-604` | term | home | Level of detail; geometric error; relative error; error threshold; LOD cross-fade |
| `render-scene:727` | open | home | Which sample has generated levels with errors to show: the writer checks the samples' import records first |
| `new:2` | not-done | home | No billboards or impostors for distant objects. Evidence: `git grep -niE "billboard\|impostor" 822a7a46 -- Strata/src Strata/shaders` finds nothing |
| `render-scene:84` | feature | use | The fade code above the instance bits of a draw-list entry |
| `render-scene:98` | feature | use | The screen fraction the rules take |
| `render-scene:479` | rule | link | Prepass and forward pass agree to the bit, at `gpu/frame-tour` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The screen fraction | `draw/bounds-culling` | must |
| Batches, the draw list and its entries | `draw/batching` | must |
| The depth prepass, the `EQUAL` test and invariant positions | `gpu/frame-tour` | must |
| Ordered dither | `basics/signals` | must |
| Floating point: which operations are exact; logarithms | `basics/numbers` | must |
| A shader that discards a pixel | `gpu/shaders` | must |
| How levels and their errors are generated at import | `assets/models-gltf` | helps |
| The quality rows and their presets | `image/quality-settings` | helps |
| Choosing a debug view in the Scene view | `gpu/debugging` | helps |

## `draw/mirrors-camera-relative` — Mirrors, normals and camera-relative positions

**Covers.** Two problems that every scene shader meets, and the scene vertex shader that solves both. First, handedness
and mirrored transforms: a negative scale (an odd number of them) makes the determinant negative, reverses the winding
of every triangle on screen and the handedness of the tangent frame; back-face culling then shows the mesh inside out.
The answer is to detect the sign, flip the front face and the bitangent's sign. Strata marks the proxy `Mirrored` when
it is placed, gives mirrored instances their own sort-key bit and GPU bucket bit, draws them with clockwise-front
pipelines (`GetScenePipeline`) and flips the tangent's handedness in `Mesh.vert`, which reads the instance from the
render scene's GPU copy (one sentence: a new proxy draws once its upload arrived; `draw/render-scene-gpu` teaches the
copy). The page explains a tangent frame in one paragraph (normal maps are `light/materials`'). Normals come from the
instance's rows through the cofactor matrix, with no inverse on the CPU: the page recalls in two sentences why the
cofactor works under non-uniform scale, links `basics/math-bases`, which derives it and homes the term, and shows how
the shader builds it from the rows.

Second, floating-point precision far from the origin: a float32 position 100 km out has steps of millimetres, so
vertices jitter. The approaches: origin rebasing (which Strata does not use), double precision on the CPU,
camera-relative rendering, large world coordinates. Strata renders camera-relative in every scene shader: view matrices
are rotation only, the vertex shader subtracts the camera's position from the instance's translation before anything is
added, positions the CPU uploads are subtracted in double, and GPU culling tests camera-relative boxes; the scene's
transforms stay float32, so an entity's origin still moves in steps of about 7.8 mm at 100 km. The two answers meet in
two shader functions, read whole: `TransformPositionRelative`, and `TransformNormal`, whose cofactor normal is negated
for a mirrored instance. The walk ends in the scene vertex shader, `Mesh.vert`, where the two functions are called: the
page quotes only the lines of the relative position, the normal and the mirrored handedness, and of the previous
relative position, and links `gpu/geometry-pool`, which reads the shader from the draw list to the clip position; the
skinning and velocity parts are named for `draw/skinned` and `draw/motion-vectors`. The page runs on an asymmetric
Showcase prop beside its mirror image, and on the scene of `GPU.SceneRenderer.CameraRelative` at the origin and 100 km
out (the "without" picture is a diagram, since no switch turns camera-relative rendering off). The exercise is a
camera-relative audit: draw a debug line 100 km out and check that the renderer uploads it relative to the camera,
subtracted in double, then reproduce `GPU.SceneRenderer.CameraRelative` with the reader's own mesh. At the end the
reader can say what a mirrored instance changes in the pipeline and the shader, and why a new pass must never upload a
world position.

**Leaves out.**

- Floating-point numbers and their spacing → `basics/numbers`
- The 20 km limit of worlds → `worlds/why-streaming`
- The counter-clockwise convention and clip space → `gpu/coordinates`
- Normal maps and tangent space → `light/materials`
- Flipped tangents in the material record → `light/material-data`
- The scene vertex shader read from the draw list to the clip position → `gpu/geometry-pool`
- The skinning and velocity parts of the vertex shader → `draw/skinned`, `draw/motion-vectors`
- Mirroring a prop with a negative scale, for game makers → `make/transforms-units`

**Fit.** `fits`: about 3,650 words against M (3,000). Two concepts and Strata's two answers take the most, then two
excerpts and the quoted lines of the vertex shader; the cofactor's derivation is `basics/math-bases`', recalled here in
two sentences.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-scene:317` | concept | home | Handedness and mirrored transforms; the inside-out mistake |
| `render-scene:321` | concept | home | Precision far from the origin: rebasing, doubles, camera-relative rendering, large world coordinates |
| `render-scene:170-172` | feature | home | Mirrored instances; the normal matrix from the rows; camera-relative space |
| `render-scene:358` | code | home | `Strata/src/Strata/Renderer/SceneRenderer.cpp:2464-2469`: the mirrored winding and double-sided culling in pipeline state |
| `render-scene:370` | code | home | `Strata/shaders/Scene/Mesh.vert.slang:50-56`, with lines 76-81: the relative position, `TransformNormal`, the mirrored handedness and the previous relative position; the rest of the shader is linked (lines 35-60 are quoted on `gpu/geometry-pool`, the merge "Scene vertex shader excerpt") |
| `render-scene:442` | figure | home | A mirrored asymmetric prop beside the original, with correct faces and normal map |
| `render-scene:451` | figure | home | The same scene at the origin and 100 km out; the "without" case drawn as a diagram |
| `render-scene:499` | rule | home | Mirrored instances need clockwise pipelines and flipped tangents |
| `render-scene:501` | rule | home | Positions uploaded to scene shaders are camera-relative, subtracted in double |
| `render-scene:643` | term | home | Mirrored transform |
| `render-scene:645`, `render-scene:647` | term | home | Tangent handedness; camera-relative space |
| `render-core:387` | concept | home | Winding, culling and mirrored transforms: the render-core inventory's form of `render-scene:317` |
| `render-core:391` | concept | home | Precision far from the origin and camera-relative rendering: the render-core inventory's form of `render-scene:321`; scene transforms stay float32, 7.8 mm steps at 100 km |
| `render-core:142` | feature | home | Camera-relative space as the render-core inventory lists it: rotation-only view matrices (`GetRelativeView`), CPU uploads computed in double, `InstanceData` kept in world space, tested at 20 and 100 km |
| `render-direct:68` | feature | home | Mirrored instances as the light inventory lists them: the same feature as `render-scene:170` |
| `render-core:462` | code | home | `Strata/shaders/Include/Scene.slang:238-261`: `TransformPositionRelative`, which subtracts the camera from the instance's translation first, and `TransformNormal`, the cofactor normal negated for mirrored instances |
| `render-core:533` | figure | home | The scene at the origin and 100 km out: one figure with `render-scene:451` |
| `render-core:538` | figure | home | The mirrored asymmetric mesh beside the original: one figure with `render-scene:442` |
| `render-core:598` | rule | home | Front faces are counter-clockwise; mirrored instances use clockwise pipelines and flipped tangents; normals go through `TransformNormal`: the render-core form of `render-scene:499` |
| `render-core:600` | rule | home | Never upload a world position to a scene shader: the render-core form of `render-scene:501` |
| `render-core:648` | hands-on | home | The camera-relative audit: a debug line 100 km out, uploaded relative to the camera and subtracted in double (`Strata/src/Strata/Renderer/SceneRenderer.cpp:4105-4110`), then `GPU.SceneRenderer.CameraRelative` with the reader's own mesh |
| `render-core:738-739`, `render-core:741` | term | home | Mirrored transform; tangent handedness; camera-relative rendering: one glossary entry each with `render-scene:643`, `render-scene:645` and `render-scene:647` |
| `render-core:742` | term | home | Origin rebasing, named among the approaches as one Strata does not use |
| `worlds-runtime:546` | term | home | Origin rebasing as the worlds inventory defines it (shifting the world so the player stays near the origin; not in Strata): one glossary entry with `render-core:742`, passed by `worlds` (the merge "Origin rebasing"); `worlds/why-streaming` keeps its not-done line and links |
| `render-core:839` | open | home | No switch turns camera-relative rendering off, so the "without" half of the 100 km figure is a diagram |
| `render-scene:373` | code | use | `Strata/shaders/Include/Scene.slang:238-261`: `TransformPositionRelative` and `TransformNormal` (the item's home is `draw/gpu-driven`) |
| `render-scene:345` | code | use | Where placement sets the `Mirrored` flag |
| `render-scene:646` | term | use | The cofactor matrix, used for the normal in `TransformNormal` and `Mesh.vert`; the term is taught from zero on `basics/math-bases` (R43, R46) |
| `render-core:740` | term | use | Normal matrix (the render-core inventory's "normal matrix / cofactor matrix"), used where `TransformNormal` carries normals from the instance's rows; its glossary home is `basics/math-bases` (R43, R46) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Floating point and the spacing of floats; double precision | `basics/numbers` | must |
| The determinant and its sign; normals through the cofactor matrix | `basics/math-bases` | must |
| Transforms and their rows | `basics/math-matrices` | must |
| The counter-clockwise convention, clip space and the camera's matrices | `gpu/coordinates` | must |
| Batches, sort keys and the draw list | `draw/batching` | must |
| Vertex shaders and their inputs | `gpu/shaders` | must |
| Cross products | `basics/math-vectors` | must |
| Normal maps and tangent space | `light/materials` | helps |
| Why worlds stay within 20 km | `worlds/why-streaming` | helps |
| The instances live in the render scene's GPU copy; a new proxy draws once its upload arrived | `draw/render-scene-gpu` | helps |

## `draw/render-scene-gpu` — The render scene's GPU copy

**Covers.** The job: keep a copy of the render scene on the GPU, one per render scene and shared by its renderers,
uploading only what changed and never more per frame than the budget allows. The problem section is one paragraph that
links `draw/render-scene`'s concept of versioned readers. The map: the mirror's buffers (instances, palettes, a 64-byte
`GPUProxy` culling record per proxy, light records, the mesh table, material data and flags) and `RenderSceneGPUCache`,
keyed by the render scene's id. The contract: the copy knows only what the change logs say, so every change of
instances or proxies is recorded (the rule `AGENTS.md` states), and the copy is written only through staging. The toy
mirrors an array to a "GPU" array by following a log, in 40 lines.

The real code in the order of an update: `Update` follows the three logs and uploads runs of changed elements through
`GPUUploadQueue::RecordSceneUpload` in its own command list; changes of resident proxies upload at once, destroyed
records are cleared at once, and new proxies upload oldest first within `NewInstanceBytesPerFrame` (16 MiB), at least
one a frame. A proxy is drawn only once it is resident, so code that renders a single picture renders again until no
proxy waits. Buffers grow by copying into larger ones, the old ones released deferred. The asset tables: the mesh table
(a `GeometryHandle` per mesh slot and the skinned-arena bit) and the material data and flags per material slot, rebuilt
only for content and slot changes, with a reverse index from textures to materials. Clones copy their mirror on the GPU
when the source holds exactly the clone's versions; mirrors go with their scene or after 300 unused frames, and a small
released mirror's buffers (1 MiB or less) are adopted by the next one with their buffer version, which is why binding
sets are rebuilt by comparing buffer versions, never mirrors or scene ids. What the scene's life asks of the copy: a
prepared load fills it within 16 MiB a call while the scene is prepared (`PrepareLoadedScene`), and the frame that makes
the copy is never the frame that shows the scene; a renderer keeps its per-scene state (visibility bits, LOD fades,
draw lists, feedback, material resolution) for a clone of the scene it drew last, and resets all of it for any other
scene. A residency diagram closes the walk. How it is tested: `GPU.Renderer.RenderSceneGPU`, whose cases cover the
shared copy, random edits, the budget for new proxies, release and recycling, prepared loads ("A loaded scene's GPU copy
is filled while it is prepared"), the asset tables, clones ("A copied scene's GPU copy is cloned from its source's"),
the write logs and the light records. The exercise lowers the budget and counts the frames until no proxy waits. The
page runs on a scene of 100,000 proxies loading over several frames. At the end the reader can say when a new proxy first
draws and why a recycled mirror does not force new binding sets.

**Leaves out.**

- The change logs the copy follows → `draw/render-scene`
- Staging, the upload queue and its budget → `gpu/upload-queue`
- Deferred release → `gpu/resources-lifetimes`
- The write logs that motion histories read → `draw/motion-vectors`
- What the culling shader reads from the copy → `draw/gpu-driven`
- What a light record and a material record hold → `light/lights`, `light/material-data`

**Fit.** `fits`: about 3,600 words against M (3,000). The mirror's eight features and four rules take the most, then
two excerpts; the GPU halves of prepared loads and clones add about 200 words, and the four rules belong in the contract
and the section on changing it safely rather than in asides of their own.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-scene:110-116` | feature | home | The shared mirror, the log-driven update, the budget for new proxies, growth by GPU copy, the asset tables, clone mirrors, release and recycling |
| `render-scene:73` | feature | home | A new proxy draws only once its record and instances are resident |
| `render-scene:361` | code | home | `Strata/src/Strata/Renderer/RenderSceneGPU.cpp:679-782`: changes of resident proxies now, destroyed ones cleared, new ones within the budget, oldest first |
| `new:3` | code | home | `Strata/src/Strata/Renderer/RenderSceneGPU.cpp:911-939`: `RenderSceneGPUCache::Get`, a clone's mirror copied on the GPU or a recycled mirror's buffers adopted |
| `render-scene:401` | figure | home | The residency state machine: not seen, queued, resident; destroyed, cleared; the budget per frame |
| `render-scene:469` | rule | home | Record every change of instances or proxies in the logs |
| `render-scene:503` | rule | home | Compare buffer versions, never mirrors or scene ids, to know when to rebuild binding sets |
| `render-scene:507` | rule | home | Code that renders a single picture renders again until no proxy waits |
| `render-scene:511` | rule | home | Never `writeBuffer` the scene's GPU copy; go through staging |
| `new:26` | feature | home | The GPU half of a prepared load: `PrepareLoadedScene` fills the GPU copy within `c_PrepareUploadBytes` (16 MiB) a call, only while the frame's loading budget has time, and the frame that makes the copy is not the frame that shows the scene; the test "A loaded scene's GPU copy is filled while it is prepared, so the frame that shows it uploads no proxy". Evidence: `Strata/src/Strata/Renderer/RenderScene.h:172-180`; `Strata/src/Strata/Renderer/RenderScene.cpp:297-315`; `StrataTests/src/Renderer/GPURenderSceneGPUTests.cpp:493`, `:523` |
| `new:27` | feature | home | A renderer's per-scene state at a play start and a scene switch: for a clone of the render scene it drew last it keeps the slots' state, draw lists, feedback, material resolution and visibility history; for any other scene it resets them (visibility bits, LOD fades, draw lists, usage); the test "A copied scene's GPU copy is cloned from its source's: the copy's first frame uploads nothing and draws the same". Evidence: `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp:136-170`; `StrataTests/src/Renderer/GPURenderSceneGPUTests.cpp:703` |
| `new:16` | hands-on | home | Exercise (done, with a "trace it yourself"): in the pattern of the test "New proxies upload within the frame's budget and are drawn once they arrived", set `NewInstanceBytesPerFrame` to a budget of 128 proxies for 1,000 cubes, predict the frames until `DeferredProxies` is 0 and the instances drawn in the first frame, run it, and trace with a breakpoint in `RenderSceneGPU::Update` which proxies the first frame took (the oldest first); the solution is the test and the path. Evidence: `StrataTests/src/Renderer/GPURenderSceneGPUTests.cpp:286-337`; `Strata/src/Strata/Renderer/RenderSceneGPU.cpp:679-782` |
| `render-scene:616-617` | term | home | GPU copy (mirror); resident proxy |
| `render-scene:621-623` | term | home | The new-proxy upload budget (`NewInstanceBytesPerFrame`); culling record (`GPUProxy`); mesh table and material table |
| `render-scene:45` | feature | use | The three change logs the copy follows |
| `render-scene:47` | feature | use | Prepared loads, whose GPU half `new:26` teaches |
| `render-scene:48` | feature | use | Clones at play start, whose mirrors are copied and whose renderer state `new:27` teaches |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Staging and the upload queue | `gpu/upload-queue` | must |
| Resources, lifetimes and deferred release | `gpu/resources-lifetimes` | must |
| Structured buffers and binding sets | `gpu/binding` | must |
| The render scene's change logs and versions | `draw/render-scene` | must |
| Slots, instances and the draw list | `draw/batching` | must |
| `GeometryHandle` and the pool's arenas | `gpu/geometry-pool` | must |
| Bindless textures and the texture table | `gpu/binding` | helps |
| A scene that plays is a copy (`Scene::Copy`) | `world/systems` | helps |

## `draw/gpu-driven` — GPU-driven culling and indirect drawing

**Covers.** The job: cull the render scene and build the frame's draw commands on the GPU, so that the CPU's cost no
longer follows the number of proxies, drawing exactly the pixels the CPU path draws. The problem and how engines solve
it: CPU culling of a million proxies costs milliseconds; keep the scene on the GPU, cull in compute and compact the
survivors into indirect arguments (Haar and Aaltonen, SIGGRAPH 2015; Wihlidal, GDC 2016). Why Strata counts first and
writes second instead of appending with one atomic: deterministic ranges per record and draws per bucket with known
slots. The map: the passes and their buffers as a data-flow diagram. The contract: the GPU path is chosen per renderer
(`GPUDriven` Auto on devices with `drawIndirectFirstInstance`, else Off, and a fallback when shaders or resources cannot
be set up), the switches are code only, thumbnails force the CPU path, and every culling rule has a CPU twin that must
change with it. The toy is a two-pass count-then-write over an array in a compute shader, building on `gpu/compute`'s
prefix sum.

The real code, in the order of a frame: the culling tables in the geometry pool (a `GeometryEntry` per handle, a
`GeometrySubmesh` per submesh, a `GeometryLOD` draw record per level); the culling constants; `Cull.comp`'s `CullProxy`,
one thread per proxy (active and indexed flags, the camera-relative frustum test, size culling, the level of detail per
instance and material, the emit into counts per bucket and LOD record); `Emit` and `EmitViewInstances`, which count and
write through one function; `CullBuild.comp`'s prefix allocation by atomics (a range of the draw list and an indirect
slot per record, overflow, the 64-bit triangle count by carry); `RunGPUCulling`'s sequence count, build, feedback,
write, and why dispatches through one binding set need explicit UAV barriers. Buckets: pipeline state times vertex
arena, with the bit layout of a bucket index and only the buckets a frame can have given dense indices. One sentence
points forward to `light/sun-shadows-1`, which teaches how the sun's casters are culled and drawn into the cascades on
both paths. The indirect modes chosen from the device: `drawIndexedIndirectCount` with a GPU-written count, `NoCount`
with bounded zeroed slots, and `PerDraw`, split at `maxDrawIndirectCount` (MoltenVK runs `NoCount`), shown as a decision
tree. What bounds a bucket's draw slots without a GPU-written count (every MoltenVK device, so every Mac): the LOD
records of the meshes the CPU's marks found in view, and on feedback frames the feedback's count plus a quarter and 16;
draws beyond the bound are counted as overflow and not drawn in that frame, and the CPU walks the view once; with a
GPU-written count the GPU's number is exact. The 128-byte counters read back two to three frames late. The empty render
scene that records no culling (and the rule for resources that matter without proxies). Transparent materials left to
the CPU's sorted pass. Shading that must not depend on draw order, because the GPU places instances in scheduling order
(the derivative rule is `light/brdf`'s). What Strata does not do here: mesh shaders and meshlets. How it is tested:
`GPU.SceneRenderer.GPUDriven`, whose `CompareScenes` helper draws the same scenes on both paths and compares them;
`GPU.SceneRenderer.GPUDrivenFallback`, a renderer whose GPU path cannot be set up drawing through the CPU path and
keeping none of the path's resources; and `GPU.SceneRenderer.IndirectFallback`, draws without a GPU-written count, one
draw per slot, local shadow views a batch at a time and buckets split over several calls, each drawing what the CPU path
draws. CI's hosted runners have no GPU and leave the `gpu` suites out. The cost, measured: the CPU's frame for 100,000
and for 1,000,000 cubes against the GPU's, read through generated keys, so the reader sees the CPU's cost stop following
the number of proxies. The exercises add a per-instance value the right way, port a CPU culling rule to the GPU, and
trace one proxy from `CullProxy` to the indirect call that draws it. The page runs on `CompareScenes`' scenes.

The page's last section is the visibility feedback, which the counting pass writes. Its job: let the GPU, which knows
what it culled and drew, tell the CPU which meshes and materials to request and how large they looked, without the CPU
walking the proxies. The section first teaches feedback loops from the GPU to the CPU in general (texture streaming
feedback, virtual texturing) and their price: latency. The real code: the counting pass marks each touched mesh and
material slot with use bits (view, high, prefetch, shadow), the largest pixel size and the UV pixels, with a read before
the atomic so that most threads skip it, and appends first touches to a list that `CullFeedback.comp` packs; the GPU's
port of the texture streaming measure (`Include/TextureStreaming.slang`). The CPU applies the newest feedback it has
(`ApplyFeedback`) and still walks transparent users, skinned proxies and meshes of unknown bounds. It walks instead in
the first frames, after a camera cut, when the tables changed since the feedback's frame, when the feedback is older
than 8 frames, and once after an overflow (`UsesFeedback`); the test "Without a GPU-written draw count, draws beyond the
slots the feedback foresaw run the CPU's walk once" shows the last of these. The feedback reaches the texture streamer
by no road of its own: the sizes `ApplyFeedback` writes into the material slots are published with the frame's visible
textures, and `ReportView` receives them as it does on the CPU path. A timeline shows a frame writing feedback, its
readback two or three frames later, the requests, the loads and the tables catching up. The section runs on its
exercise: add a mesh in a GPU test and count the frames until it is requested. At the end the reader can follow a proxy
from `Cull.comp` to an indirect draw, name what must change on both paths when a rule changes, say how late a request
driven by feedback comes, and say when the CPU walks instead.

**Leaves out.**

- Compute shaders, thread groups, atomics, prefix sums and UAV barriers → `gpu/compute`
- Culling the local lights' shadow views → `light/local-shadows`
- Culling lights into clusters → `light/many-lights`
- Culling the sun's cascades and their occlusion → `light/sun-shadows-1`
- The second phase against the depth pyramid → `draw/occlusion`
- Skinned buckets and posed bounds → `draw/skinned`
- The derivative rule and shading order in the forward shader → `light/brdf`
- The requests and priorities the feedback replaces → `draw/asset-requests`
- How the published sizes choose mip levels → `draw/mip-streaming`
- Readback without stalling → `gpu/readback-timing`

**Fit.** `fits`: about 6,750 words against XL (8,000). Five excerpts, three diagrams and the GPU path's features take the
most; the visibility feedback, the last section, adds a concept, a two-part excerpt, four features, a timeline and an
exercise in about 1,350 words, as the page has one set of fixed parts.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-scene:287` | concept | home | The GPU scene and GPU-driven culling; count, build and write against one atomic append |
| `render-scene:91` | feature | home | The culling tables in the geometry pool: entries, submeshes, LOD records |
| `render-scene:123-132` | feature | home | The mode switch, `Cull.comp`, count, build and write, buckets, indirect modes with what bounds a bucket's draw slots without a GPU-written count (the CPU's marks, the feedback's count plus a quarter and 16, overflow: `Strata/src/Strata/Renderer/SceneRendererGPUDriven.cpp:79`, `:514-566`, `:1199-1203`), culling constants, GPU counters, the empty render scene, transparent left to the CPU; of order-independent shading only the cause, the GPU appending instances in scheduling order (`Strata/shaders/Scene/Cull.comp.slang:12-15`), with a link to `light/brdf`, which teaches the rule and its reason |
| `render-scene:362` | code | home | `Strata/shaders/Scene/Cull.comp.slang:448-511`: `CullProxy`, from flags to emit |
| `render-scene:363` | code | home | `Strata/shaders/Scene/Cull.comp.slang:195-232`: `EmitViewInstances`, with `Emit` at 58-80 counting and writing through one function |
| `render-scene:364` | code | home | `Strata/shaders/Scene/CullBuild.comp.slang:49-109`: prefix allocation by atomics, overflow, the 64-bit triangle count |
| `render-scene:365` | code | home | `Strata/src/Strata/Renderer/SceneRendererGPUDriven.cpp:923-1026`: count, build, feedback, write; the explicit UAV barriers |
| `render-scene:373` | code | home | `Strata/src/Strata/Renderer/GPUSceneData.h:113-151`: the bit layout of bucket indices, with `GetGPUIndirectPath` at `SceneRendererGPUDriven.cpp:177-194`, and `UsesFeedback` at `SceneRendererGPUDriven.cpp:1619-1628`: every reason the CPU walks instead |
| `render-scene:395` | figure | home | The bucket index's bits: view buckets, shadow buckets per cascade, local view buckets, the dense table |
| `render-scene:405` | figure | home | The GPU-driven passes with their buffers, from the proxies to indirect draws per bucket |
| `render-scene:421` | figure | home | The decision tree from `GPUDriven` and device features to the indirect mode |
| `render-scene:474` | rule | home | Change the CPU rule and the GPU rule together |
| `render-scene:509` | rule | home | A GPU-culling resource that matters without proxies is cleared in the empty-scene branch too |
| `render-scene:513` | rule | home | Explicit UAV barriers between culling dispatches through one binding set |
| `render-scene:534` | hands-on | home | Add a per-instance value as a parallel buffer, log its changes and show both paths agree |
| `render-scene:536` | hands-on | home | Port a CPU culling rule (a maximum draw distance) to `Cull.comp` and extend the comparison test |
| `new:17` | hands-on | home | Exercise ("trace it yourself"): one proxy of `CompareScenes`' scenes followed from `CullProxy` through `Emit`'s count, the slot and draw-list range `CullBuild.comp` gives its record, and the write pass, to the indirect call of `DrawGPUBucket` that draws it, with a GPU debugger's capture or a search of the buffers' names; the solution names each pass, buffer and function. Evidence: `Strata/shaders/Scene/Cull.comp.slang:58-80`, `:448-511`; `Strata/shaders/Scene/CullBuild.comp.slang:49-109`; `Strata/src/Strata/Renderer/SceneRendererGPUDriven.cpp:1195-1226` |
| `new:24` | feature | home | The GPU path's cost, measured: the CPU's frame for 100,000 and 1,000,000 cubes against the GPU's, read through `perf.PerfGPU.Renderer.Render100kCubes.Measured`, `perf.PerfGPU.Renderer.Render1MCubes.Measured`, `perf.PerfGPU.Renderer.Render100kCubesGPU.Measured` and `perf.PerfGPU.Renderer.Render1MCubesGPU.Measured` (the measured renderer leaves `GPUDriven` at Auto); the method is `engineering/perf-lab`'s and the full table `reference/performance`'s. Evidence: `StrataTests/Perf/Budgets.json:152`, `:173-175`; `StrataTests/src/Perf/RendererPerfTests.cpp:325-388`; `StrataTests/src/Perf/RendererPerfUtils.h:37-42` |
| `render-scene:584` | term | home | `drawIndexedIndirectCount` |
| `render-scene:585` | term | link | `multiDrawIndirect`, `drawIndirectFirstInstance`, `maxDrawIndirectCount`, at `draw/batching`, where the CPU path meets them first |
| `render-scene:592` | term | home | LOD record (`GeometryLOD`) |
| `render-scene:615` | term | home | GPU-driven rendering |
| `render-scene:624` | term | home | Counting pass and write pass |
| `render-scene:626` | term | home | Overflow |
| `render-scene:715` | open | home | How it is tested: the writer reads `CompareScenes` (`GPUSceneRendererGPUDrivenTests.cpp:610`) for the scenes both paths draw |
| `render-scene:722` | open | home | The switches are code only (`SceneRendererSpecification`); thumbnails force the CPU path (`SceneRenderer.cpp:248-251`); comparison figures need a harness |
| `render-scene:725` | open | home | The GPU-driven path's device reach as the 0.4.0 and 0.5.0 release notes state it (`Docs/Releases/0.4.0.md:264-269`); CI's hosted runners have no GPU and skip the `gpu` label (`.github/workflows/ci.yml:195-215`) |
| `new:4` | not-done | home | No mesh shaders or meshlets: culling is per proxy and per instance, drawing through the classic pipeline. Evidence: `git grep -niE "meshlet\|mesh ?shader\|EXT_mesh_shader\|taskShader" 822a7a46 -- Strata/src Strata/shaders` finds nothing |
| `render-scene:306` | concept | home | Feedback loops from the GPU to the CPU and their latency |
| `render-scene:148-151` | feature | home | The GPU marks requests, the CPU applies the newest feedback, when the CPU walks instead (with the test of the walk after an overflow, `StrataTests/src/Renderer/GPUSceneFeedbackTests.cpp:329`), the texture streaming port |
| `render-scene:368` | code | home | `Strata/shaders/Scene/Cull.comp.slang:84-100`: a read before the atomic, with `ApplyFeedback` at `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp:344-386` |
| `render-scene:415` | figure | home | The feedback loop as a timeline: frame N, the readback at N+2 or N+3, requests, loads, tables |
| `render-scene:543` | hands-on | home | Count the frames until a new mesh is requested by feedback |
| `render-scene:628` | term | home | Visibility feedback |
| `assets:802` | open | home | Settled at the pin: the feedback changes the streamer's inputs only through `ReportView`. `ApplyFeedback` writes the GPU's pixel sizes and UV pixels into the material slots (`Strata/src/Strata/Renderer/SceneRendererExtraction.cpp:344-386`), `GatherDraws` publishes them as the visible textures (lines 1111-1123), and `ReportTextureUse`, the only caller of `ReportView`, hands them over (`Strata/src/Strata/Renderer/SceneRenderer.cpp:2835-2853`) |
| `render-scene:60` | feature | use | Size culling on both paths |
| `render-scene:99-100` | feature | use | The halving and error rules, which `Cull.comp` repeats |
| `render-scene:172` | feature | use | The camera-relative frustum test |
| `render-scene:110` | feature | use | The GPU copy that `Cull.comp` reads |
| `render-scene:68` | feature | use | The use bits and priorities the feedback carries |
| `render-scene:505` | rule | use | Tests of requests wait for feedback or turn it off |
| `render-scene:477` | rule | link | Shading must not depend on draw order, at `light/brdf` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Compute shaders, thread groups, atomics, prefix sums and UAV barriers | `gpu/compute` | must |
| Readback of GPU data a few frames late | `gpu/readback-timing` | must |
| Device features and limits, and the graphics device's capabilities | `gpu/vulkan-nvrhi` | must |
| The render scene's GPU copy and its records | `draw/render-scene-gpu` | must |
| The CPU path's culling rules and the screen fraction | `draw/bounds-culling` | must |
| Batches, buckets, the draw list and indirect arguments | `draw/batching` | must |
| The level-of-detail rules | `draw/lod` | must |
| Mirrored instances and camera-relative positions | `draw/mirrors-camera-relative` | must |
| Writing a GPU test with the shared `GPUContext` | `gpu/first-triangle` | must |
| Requests by visibility and their priorities | `draw/asset-requests` | must |
| The derivative rule and shading order | `light/brdf` | helps |
| Continuous integration and its machines | `engineering/ci` | helps |
| Texel density and the wanted level | `draw/mip-streaming` | helps |

## `draw/occlusion` — Occlusion culling

**Covers.** The job: leave out what is in the frustum but hidden behind other geometry, without ever hiding something
visible and without drawing anything a frame late. The problem section teaches the approaches: hardware occlusion
queries (and their latency), software-rasterized occluders, reprojecting last frame's depth pyramid, and the two-phase
depth pyramid of Haar and Aaltonen and of Nanite, compared in a table. The idea of a conservative test: drawing too much
only costs time, hiding wrongly is a visible bug. The toy builds a farthest-depth pyramid of a small depth array on the
CPU and tests a rectangle against it.

The real code. The depth pyramid: level 0 half the depth buffer rounded up, every level the farthest depth (the
smallest, with reversed Z) of the 2x2 above it, the last row and column covering what lies past them, one sample of a
minimum sampler per 2x2 where the device has `samplerFilterMinmax` and four loads elsewhere; `GetPyramidFootprint`, the
finest level at which a box's screen rectangle spans at most 2x2 texels; `IsOccluded`, the box's nearest depth against
the pyramid. Two-phase view occlusion: the first phase draws what the view saw last frame into the prepass, a pyramid is
built from that depth, the second phase tests every proxy in the frustum and draws the newly visible ones in the same
frame; the two visibility bits per proxy that alternate by frame parity, cleared on a camera cut, a renderer's first
frame or another render scene. The rules: occlusion stays conservative; anything new that reads the view's depth runs
after the second phase's prepass; tests that count draws render a frame more first or turn occlusion off. Visibility
feedback still marks occluded proxies' assets as in view. What went wrong before: a minimum sampler's coordinates
normalized by the wrong size moved the footprints and hid visible objects (fixed in wave 8). What Strata does not do
here: portals. How it is tested: `GPU.SceneRenderer.Occlusion`, whose cases hide a box behind a wall and draw it in the
frame the wall goes or the camera steps aside, cover a screen rectangle that reaches the last row and column at odd and
even sizes, orthographic views, the cascades' casters and the pause of their culling, a box in plain view below a
window, and the pyramid's texels holding the farthest depth of what they cover. A second exercise cuts the camera in
that test's wall scene and traces where the cut clears the visibility bits. The page runs on a wall in front of many
boxes, with `occludedProxies` and `visibleProxies` before and after the wall is removed, and the exercise computes a
pyramid of a 7x5 depth buffer by hand. At the end the reader can build a pyramid level by hand, find a box's footprint,
and explain why nothing appears a frame late.

**Leaves out.**

- The cascades' occlusion and the shadow cascade cache → `light/sun-shadows-1`
- Reversed Z and depth precision → `gpu/coordinates`
- Mip chains → `assets/textures`
- The depth prepass and the passes that read the final depth → `gpu/frame-tour`
- The counting and write passes this page adds a phase to → `draw/gpu-driven`

**Fit.** `fits`: about 4,050 words against L (5,000). Two multi-part excerpts, three figures and three rules take the
most, with the case of what went wrong before; the page stands about 50 words above L's bottom.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-scene:299` | concept | home | Occlusion culling with a hierarchical depth buffer: the approaches and the conservative test |
| `render-scene:138-140` | feature | home | Two-phase view occlusion, the depth pyramid and its wave 8 fix, the visibility bits |
| `render-scene:366` | code | home | `Strata/shaders/Scene/HZBBuild.comp.slang:41-83`: a conservative farthest-depth pyramid, with `GetPyramidFootprint` (`Strata/shaders/Include/Culling.slang:225-246`) and `IsOccluded` (`Strata/shaders/Scene/Cull.comp.slang:165-191`) |
| `render-scene:367` | code | home | `Strata/src/Strata/Renderer/SceneRendererGPUDriven.cpp:1028-1064`: the two-phase sequence, with `CullSecondPhase` (`Cull.comp.slang:516-547`) and the alternating bits |
| `render-scene:407` | figure | home | Two-phase occlusion over two frames: the bits by parity, phase 1, the pyramid, phase 2 |
| `render-scene:409` | figure | home | The pyramid's levels with odd sizes and the footprint of a box's rectangle; farthest is smallest |
| `render-scene:446` | figure | home | A wall in front of many boxes, with the occluded and visible counts before and after |
| `render-scene:484` | rule | home | Occlusion culling must stay conservative |
| `render-scene:487` | rule | home | Anything new that reads the view's depth runs after the second phase's prepass |
| `render-scene:505` | rule | home | Tests that count draws render a frame more first or turn occlusion off; tests of requests wait for feedback |
| `render-scene:539` | hands-on | home | A pyramid of a 7x5 depth buffer by hand, and the footprint of a rectangle touching the last column |
| `new:18` | hands-on | home | Exercise (done, with a "trace it yourself"): in a copy of the wall scene of `CheckOcclusion`, jump the camera more than 10 units (a camera cut) to a place where the wall still hides the box, and check that the frame after the cut draws the box (no history: `OccludedProxies` is 0) and the next frames leave it out; then find with a search where the cut clears the visibility bits (`m_ResetVisibility` set at the cut, the clear in `RunGPUCulling`); the solution is the test and the path. Evidence: `StrataTests/src/Renderer/GPUSceneOcclusionTests.cpp:74-120`; `Strata/src/Strata/Renderer/SceneRenderer.cpp:3155-3159`; `Strata/src/Strata/Renderer/SceneRendererGPUDriven.cpp:950-955` |
| `render-scene:609-612` | term | home | Occlusion culling; hierarchical Z-buffer (depth pyramid); two-phase occlusion culling; visibility parity |
| `render-scene:614` | term | home | Minimum sampler (`samplerFilterMinmax`) |
| `new:5` | not-done | home | No portals. Evidence: `git grep -ni "portal" 822a7a46 -- Strata/src` finds nothing |
| `render-scene:613` | term | use | The conservative test, met first in frustum culling |
| `render-scene:141` | feature | link | The cascades' occlusion, at `light/sun-shadows-1` |
| `render-scene:142` | feature | link | The shadow cascade cache, at `light/sun-shadows-1` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Reversed Z: near is 1, far is 0 | `gpu/coordinates` | must |
| Mip chains and their sizes | `assets/textures` | must |
| The depth prepass and the passes after it | `gpu/frame-tour` | must |
| Sampling, filtering and samplers | `gpu/how-a-gpu-frame-works` | must |
| The counting and write passes and the culling buckets | `draw/gpu-driven` | must |
| Shadow cascades | `light/sun-shadows-1` | helps |
| Visibility feedback and its latency | `draw/gpu-driven` | helps |

## `draw/mip-streaming` — Mip streaming

**Covers.** The job: keep resident only the mip levels the screen needs, raise them before they are missed and drop
them when nothing needs them, without a frame ever waiting. The problem section teaches the approaches: whole-texture
residency by recency, virtual texturing and sparse residency in tiles, and mip streaming as Unreal and Unity do it.
Strata's choice in the order data flows: a first load reads only a prefix (the header and the resident tail of levels
up to 32x32); views report the textures they drew with their size on screen and UV pixels (published by
`draw/asset-requests`, and by the GPU's port of the measure, `draw/gpu-driven`); the wanted level from texel
density, `floor(log2(size * tiling / UVPixels))`; the least needed give levels to the most needed, reads ranked by
missing levels times coverage; then camera cuts, views that need every level, and the streamer's limits: a view that
jumped (more than 10 units or 45 degrees) has its reads ranked Normal, ahead of what older views asked for; a view
without streaming (the probe bake's `ForBake`, exact-pixel tests) needs every level, keeps it under memory pressure and
counts the texture as pending until it is whole; a texture nobody needed for 60 s is forgotten, at most 8 textures drop
levels per frame, a failed read is tried again after 60 frames, and a texture in view always keeps its tail; range reads
of the loaded asset through the same queue and in-flight budget; raising and dropping levels by a new GPU texture with
the resident levels copied on the GPU, the new ones uploaded and a new bindless slot; the fade-in over 0.25 s, and the
mistake of comparing pixels while fades run (captures and thumbnails turn `FadeTextureLevels` off; tests turn it off or
wait until `TextureTable::GetFadeCount()` is 0); the drop after
30 s unneeded or under budget pressure; memory accounting that follows a texture without replacing it; the switch that
turns partial loads off for tests and baselines. Because a texture's bindless slot changes when its levels change, every
frame resolves the slot and materials keep the stable table index. The mip debug view shows the shortfall in levels
(0, 1, 2, 3 or more) while the reader flies through the Showcase, and a surface at its texture's resident tail beside
the same surface at level 0 shows what a first load holds. What Strata does not do here: mesh streaming, and
virtual texturing with sparse residency. The exercise computes wanted levels by hand, and a "trace it yourself"
follows one texture's raise from `ReportView` to its new bindless slot. At the end the reader can compute
the level a texture wants and say why a cached bindless slot is a bug.

**Leaves out.**

- Mips, color spaces and block compression → `assets/textures`
- The cooked texture's layout, smallest level first → `assets/texture-cooking`
- Budgets, eviction and pins → `assets/residency`
- What is uploaded per frame and when → `assets/uploads`
- Bindless slots and the texture table → `gpu/binding`
- The streaming view and the requests of meshes → `draw/asset-requests`

**Fit.** `fits`: about 4,350 words against L (5,000). The streamer's features in the order data flows take the most,
the camera cuts and limits among them, then four figures and two excerpts.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:6` | not-done | home | No mesh streaming, per level of detail included: only textures load in parts. Evidence: `Strata/src/Strata/Renderer/RendererRegistration.cpp:93`, the only call of `RegisterPrefix` (`git grep -n "RegisterPrefix" 822a7a46 -- Strata/src` finds besides it only its declaration and definition in `Strata/src/Strata/Asset/AssetManager.h:207` and `AssetManager.cpp:127`, and a comment that names it at `AssetManager.h:402`); `Docs/Roadmap.md:1691` |
| `new:7` | not-done | home | No virtual texturing and no sparse residency. Evidence: `git grep -niE "sparseBinding\|sparseResidency" 822a7a46 -- Strata/src` finds nothing |
| `assets:339` | concept | home | Partial residency and mip streaming: whole-texture recency, virtual texturing and sparse tiles, mip streaming; the cached-slot mistake, and the second mistake, comparing pixels while fades run: captures and thumbnails turn `SceneRendererSpecification::FadeTextureLevels` off, tests turn it off or wait until `TextureTable::GetFadeCount()` is 0 (`Strata/src/Strata/Renderer/SceneRenderer.h:200-203`) |
| `assets:187-188` | feature | home | Prefix loads (the 64 KiB head, then the header and the resident tail of levels up to 32x32); range reads of the loaded asset through the same queue and in-flight budget, which fail when the asset changed |
| `assets:190-191` | feature | home | The texture streamer (`ReportView`, the wanted level, raising at once, the drop after 30 s or under pressure, the least needed giving to the most needed, the 0.25 s fade-in, `Hold`, `RequestLevel`); raising and dropping levels by a new GPU texture, resident levels copied on the GPU and a new bindless slot |
| `assets:193` | feature | home | The switch `SetPartialLoads(false)`: whole-texture residency for tests and baselines |
| `assets:206` | feature | home | Bindless slots resolved every frame; material data keeps the stable table index |
| `assets:434` | code | home | `Strata/src/Strata/Asset/AssetManager.cpp:1665-1697`: `ReadPrefix`, the head and what the prefix function asks beyond it, with `GetMipTailByteRange` (`Strata/src/Strata/Renderer/CookedTexture.cpp:230-257`): partial loads |
| `assets:436` | code | home | `Strata/src/Strata/Renderer/TextureStreamer.cpp:28-41`: `ComputeWantedLevel`, with `GetUVPixels` at lines 65-80: the mathematics of mip selection on the CPU |
| `assets:487` | figure | home | The mip streaming loop: reports, wanted level, rank, range read, new texture, copy, upload, slot, fade-in; the drop path |
| `assets:500` | figure | home | The mip debug view of the Showcase while flying, then settled |
| `assets:506` | figure | home | A mip fade-in over two frames |
| `assets:509` | figure | home | A surface at its texture's resident tail (32x32) beside the same surface at level 0 |
| `assets:556` | rule | home | Resolve bindless slots every frame; never cache them |
| `assets:604` | hands-on | home | Wanted levels by hand for a 2048 texture tiled 4 times, checked against `TextureStreamerTests` |
| `new:19` | hands-on | home | Exercise ("trace it yourself"): one texture of the Showcase followed with breakpoints as the camera nears it, from `ReportView` (its wanted level and need) through the range read polled in `OnUpdate` to `Texture::RaiseLevels`, and the frame its bindless slot changes (`Texture::GetBindlessSlot`); the solution names each function and the levels before and after. Evidence: `Strata/src/Strata/Renderer/TextureStreamer.cpp:222-233`, `:523-545`; `Strata/src/Strata/Renderer/Texture.cpp:738`; `Strata/src/Strata/Renderer/Texture.h:134` |
| `new:22` | feature | home | Camera cuts, views that need every level, and the streamer's limits: a view that jumped (more than 10 units or 45 degrees) has its reads ranked Normal, ahead of older views'; a view without streaming (`SceneRendererSpecification::ForBake`, exact-pixel tests) needs every level, keeps it under memory pressure and counts the texture as pending until it is whole; a texture nobody needed for twice the idle drop time (60 s) is forgotten; at most 8 textures drop levels per frame; a failed read is tried again after 60 frames; a texture in view keeps its tail. Evidence: `Strata/src/Strata/Renderer/TextureStreamer.h:30-35`, `:44-48`, `:77-97`, `:102`, `:176`, `:182`, `:188`; `Strata/src/Strata/Renderer/SceneRenderer.h:195-199`; `Strata/src/Strata/Renderer/SceneRenderer.cpp:262-269`; `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp:694-696` |
| `assets:703-709` | term | home | Mip tail; mip streaming; partial load; range read; wanted level; texel density; fade-in |
| `assets:189` | feature | use | Memory accounting that follows a texture without replacing it (homed on `assets/residency`) |
| `assets:192` | feature | use | The first-load estimate, which counts only the head while loads read prefixes (homed on `assets/references`) |
| `assets:214` | feature | use | The mip debug view (the streaming view is `draw/asset-requests`') |
| `render-scene:72` | feature | use | The visible materials and textures each frame publishes |
| `render-scene:151` | feature | use | The GPU's port of the texture streaming measure |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Mip chains and texture formats | `assets/textures` | must |
| The cooked texture's layout and `GetMipByteSize` | `assets/texture-cooking` | must |
| Budgets, eviction and pins | `assets/residency` | must |
| Budgeted uploads and `Texture::UploadLevels` | `assets/uploads` | must |
| Bindless slots and the texture table | `gpu/binding` | must |
| What renderers publish each frame | `draw/asset-requests` | must |
| Visibility feedback | `draw/gpu-driven` | must |
| Logarithms in base 2 | `basics/numbers` | must |
| Loading without stalling: the streaming queue | `assets/loading` | must |

## `draw/skinned` — Skinned meshes in the renderer

**Covers.** The job: draw meshes that a skeleton deforms, culled with bounds that follow the pose, at no cost to
scenes without skins. The page takes the pose's joint matrices as given and links forward to `animation/skinning`, which
explains how they are made. The problem section teaches where skinning runs: on the CPU, in the vertex shader with a
palette, or in a compute pre-pass; dual quaternions are named with a link to `animation/skinning`, which teaches the
deformation model (rigid binding, linear blend skinning, the candy wrapper, dual quaternions) and skins a vertex by
hand. Strata's choice: linear blend skinning of four influences in the vertex shader, palettes computed on the CPU only
for changed poses, on the job system. The toy blends four given palette matrices by their weights into one, as
`BlendJoints` does, in about 20 lines.

The real code. Skin proxies: a proxy whose entity has a `SkinComponent` and whose mesh has a skin binding is posed by
the scene's `ISkinningPoses` service, so the renderer never includes Animation. The palette range per proxy, named with
its product in one sentence (what the product means is `animation/skinning`'s). Posed bounds: the union of each joint's
bind-pose extent through its palette entry, why that union bounds every weighted vertex, plus the reach that animators
which pose only when seen publish, and why culling with bind-pose bounds loses a swung limb or its shadow.
`UpdateSkinnedPoses`, which skips the whole pass when poses, transforms, hierarchy, drawn transforms and layouts are
unchanged, skips unchanged proxies, and recomputes the rest in batches of 16 on the job system. The `ST_SKINNED`
variants of the mesh and shadow vertex shaders, which blend four joints from the joint buffer `t15`, with both passes of
a skinned mesh on the same variant so that the `EQUAL` test holds. Bucketing: `c_InstanceSkinned` and the palette's
first joint in the instance (so `InstanceData` does not grow), the skinned sort-key bit and the GPU geometry class.
`HasSkinProxies`, which gates every skinning check. The visibility report: renderers tell the animators which skin
proxies they saw, and which off-view casters can still shadow the view. The rules: skinning work costs unskinned scenes
nothing; posed bounds, not bind-pose bounds; both passes on the skinned variant. What Strata does not do here: compute
skinning and dual-quaternion skinning. How it is tested: `GPU.Animation`'s skinned cases and the GPU perf test
`PerfGPU.Renderer.Skinned1000` (1,000 skinned characters posed anew every frame), its measured time and budget read
through `perf.PerfGPU.Renderer.Skinned1000.Measured` and `.Budget`, as `reference/performance` lists them; the "trace it
yourself" exercise finds why a still robot costs no palette work. The page runs on the Third-Person sample's robot
mid-dance, a limb outside its bind-pose box still drawn and shadowed, and the exercise poses a two-joint arm and prints
its bounds before and after `Sync`. At the end the reader can say what the renderer computes for a skinned proxy, when,
and why its bounds follow the pose.

**Leaves out.**

- How the joint matrices of a pose are made → `animation/skinning`
- The deformation model (linear blend skinning, the candy wrapper, dual quaternions) and a vertex skinned by hand →
  `animation/skinning`
- Skeletons and joints → `animation/skeletons`
- The animation system that publishes poses → `animation/system`
- Animators that pose only what is seen → `animation/culling`
- Skinned motion vectors → `draw/motion-vectors`
- Animation features Strata lacks → `animation/limits`

**Fit.** `over`: about 4,000 words against M (3,000). Two concepts, two excerpts, eight features, three rules and two
exercises reach M's top. Make it L (5,000) by S2.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-scene:311` | concept | home | Where skinning runs: on the CPU, in the vertex shader, in a compute pre-pass, and Strata's choice; dual quaternions named with a link to `animation/skinning`, which teaches the deformation model and skins a vertex by hand (critic-animation-8); posed bounds; the two mistakes |
| `animation:280` | concept | home | Posed bounds and culling of skinned meshes: why the union of transformed joint boxes bounds every weighted vertex |
| `render-scene:157` | feature | home | Skin proxies posed through `ISkinningPoses` |
| `render-scene:159-164` | feature | home | Posed bounds, recomputing only on change, the skinned variants, skinned bucketing, unskinned scenes pay nothing, visibility reports |
| `animation:152` | feature | home | Change-driven palette updates, the animation inventory's view of `render-scene:160` |
| `animation:157` | feature | home | `HasSkinProxies`, the animation inventory's view of `render-scene:163` |
| `render-scene:369` | code | home | `Strata/src/Strata/Renderer/RenderScene.cpp:1322-1339`: the posed bounds half of `ComputePalette` (the palette half is `animation:358`, on `animation/skinning`) |
| `new:8` | code | home | `Strata/src/Strata/Renderer/RenderScene.cpp:1341-1435`: `UpdateSkinnedPoses`, skipping unchanged poses and recomputing the rest in parallel |
| `render-scene:417` | figure | home | Posed bounds as the union of the joints' boxes transformed by their palette entries (the spaces of the product are `animation:381`, on `animation/skinning`) |
| `render-scene:444` | figure | home | The robot mid-dance with a limb outside its bind-pose box, drawn and shadowed |
| `animation:422` | figure | home | The same picture as `render-scene:444`, from the animation inventory: one figure serves both items |
| `render-scene:493` | rule | home | Anything that adds skinning work must cost unskinned scenes nothing |
| `animation:460` | rule | home | Unskinned scenes pay nothing, the animation inventory's form of `render-scene:493` |
| `render-scene:495` | rule | home | Cull skinned proxies with posed bounds, not bind-pose bounds |
| `animation:458` | rule | home | Prepass and forward pass agree to the bit for skinned meshes: both use the `ST_SKINNED` variant |
| `render-scene:545` | hands-on | home | Pose a two-joint arm out of its bind box and print its bounds before and after `Sync` |
| `new:20` | hands-on | home | Exercise ("trace it yourself"): with a breakpoint in `RenderScene::UpdateSkinnedPoses`, find why the robot costs no palette work in a frame where nothing it depends on changed (the versions of the poses, transforms, hierarchy and drawn transforms compare equal and the function returns), and which version changes first when it dances; `RenderSceneStats::LastSyncPoses` counts the palettes recomputed; the solution names the check and the version. Evidence: `Strata/src/Strata/Renderer/RenderScene.cpp:1341-1355` |
| `animation:202` | feature | use | The perf tests of animation, of which this page names the GPU one: `PerfGPU.Renderer.Skinned1000`, 1,000 skinned characters posed anew every frame, with its measured time and budget through `perf.PerfGPU.Renderer.Skinned1000.Measured` and `.Budget` (`StrataTests/Perf/Budgets.json:172`; `StrataTests/src/Perf/AnimationPerfTests.cpp:214`) |
| `render-scene:640` | term | home | Posed bounds |
| `animation:554` | term | home | Posed bounds, the animation inventory's entry (one glossary entry with `render-scene:640`) |
| `new:9` | not-done | home | No compute skinning and no dual-quaternion skinning: skinning runs per draw in the vertex shader. Evidence: `Docs/Roadmap.md:675`; `git grep -niE "dual.?quat" 822a7a46 -- Strata/src Strata/shaders` finds nothing |
| `animation:150-151` | feature | use | Pose inputs and the palette, homed on `animation/skinning` |
| `animation:154` | feature | use | `BlendJoints` and the skinning functions of `Include/Scene.slang`, homed on `animation/skinning` |
| `animation:156` | feature | use | The visibility report from the animation side, homed on `animation/culling` |
| `render-scene:126` | feature | use | The GPU buckets' geometry classes |
| `render-scene:158` | feature | link | The palette's formula, at `animation/skinning` |
| `render-scene:491` | rule | link | Every skin influence names a joint of the skin, at `animation/skinning` |
| `render-scene:638` | term | link | Palette, at `animation/skinning` |
| `render-scene:642` | term | link | WhenVisible animator, at `animation/culling` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Scene services and `GetService` | `world/systems` | must |
| Shader variants from one source with defines | `gpu/shaders` | must |
| Batches, sort keys and the instance's fields | `draw/batching` | must |
| Bounds and culling on the CPU | `draw/bounds-culling` | must |
| The GPU path's buckets | `draw/gpu-driven` | must |
| Deterministic parallel work on the job system | `core/jobs` | must |
| Transform hierarchies and spaces | `basics/math-matrices` | must |
| Skeletons, joints and poses | `animation/skeletons` | helps |
| How the joint matrices are made; inverse bind matrices | `animation/skinning` | helps |
| Animators that pose only what is seen | `animation/culling` | helps |

## `draw/motion-vectors` — Motion vectors and motion history

**Covers.** The job: give every drawn pixel the screen motion since the renderer's previous frame, for objects that
move, deform or stay still under a moving camera. One sentence says what motion vectors are for (temporal anti-aliasing
and motion blur) and links forward to `image/taa`, which the page does not need. The problem section teaches the
approaches: camera-only reprojection from depth, previous transforms per object, previous skinning. Strata's choice: a
per-renderer motion history of the instance and palette buffers, and velocity variants of the scene vertex shaders. The
toy computes a pixel's motion from two positions and two view-projection matrices.

The real code. The RG16F velocity target, which the prepass writes: unjittered current minus previous position in UV
units. The `ST_VELOCITY` variants of `Mesh.vert`: the instance as the previous frame drew it, used only when it is the
same entity's, posed by its previous palette (`u_PreviousJoints`) when that is the same range, and the unjittered clip
positions of both frames (the part of the vertex shader that `draw/mirrors-camera-relative` left for here). The rule
that motion uses unjittered matrices built in double: a still camera gives exactly zero motion, and jitter never appears
as motion. Where nothing was drawn, the camera's motion alone (`Include/Motion.slang`). The motion history: each
renderer keeps its own copy of the instance and palette buffers as its last frame drew them, never in the shared GPU
copy, because renderers render at different times. The GPU copy's write logs by process-unique write version, and
`RecordMotionCopy`, which copies only what the GPU copy wrote since, with `MotionCopy.comp`, one thread per listed
element. A frame with motion draws both the prepass and the forward pass with the velocity variant, so their depths
agree. The motion debug view colours each pixel by its motion's direction. How it is tested:
`GPU.SceneRenderer.MotionVectors`, whose cases check that the history holds what the renderer's latest frame drew and
copies only what was written since, a still view without motion, moved, skinned and mirrored instances with their own
motion, slots that change hands, cross-fades, two renderers of one scene, the motion view, and an image left
bit-identical on both paths. The exercise moves one cube by a known step and traces what the history copies. The page
runs on the Third-Person sample with the camera panning while the robot runs. At the end the reader can say where a
pixel's previous position comes from, and why the history belongs to the renderer.

**Leaves out.**

- What temporal anti-aliasing does with motion → `image/taa`
- Motion blur → `image/motion-blur`
- The pipeline key's velocity flag in the pipeline cache → `gpu/binding`
- The depth prepass and the `EQUAL` test → `gpu/frame-tour`
- The palettes being compared → `draw/skinned`

**Fit.** `fits`: about 3,700 words against M (3,000). Three excerpts and the seven features of the velocity target, the
variants and the history take the most; the items the image and animation units passed here are the same features seen
from their side and add little.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-scene:326` | concept | home | Motion vectors: camera reprojection, previous transforms, previous skinning; the "previous in the shared copy" mistake |
| `render-image:368` | concept | home | Motion vectors and reprojection as the image part recalls them: camera motion for the sky, unjittered against jittered |
| `render-scene:173-175` | feature | home | Motion vectors, the motion history, velocity in both passes |
| `render-scene:117` | feature | home | The GPU copy's write logs for readers |
| `render-image:171` | feature | home | The velocity target as the post chain reads it: RG16F, unjittered current minus previous UV |
| `render-image:174` | feature | home | The motion debug view (`ShowMotionVectors`, `Overlay/MotionView.frag.slang`) |
| `animation:155` | feature | home | Skinned motion vectors: the previous palettes (`u_PreviousJoints`, t21) |
| `render-image:555` | rule | home | Motion vectors use unjittered matrices built in double |
| `render-image:512` | figure | home | The motion view while the camera turns: one figure with `render-scene:450` |
| `render-image:702-703` | term | home | Motion vector (velocity target); motion history: one glossary entry each with `render-scene:648-649` |
| `new:10` | code | home | `Strata/src/Strata/Renderer/SceneRenderer.cpp:1286-1393`: `RecordMotionCopy`, copying only what the GPU copy wrote since the history's version |
| `new:11` | code | home | `Strata/shaders/Scene/MotionCopy.comp.slang:5-30`: one thread per listed element of the history copy |
| `render-scene:419` | figure | home | The motion history: write versions, per-renderer histories, the copy, the velocity shaders reading both |
| `render-scene:450` | figure | home | The motion debug view while the camera pans and the robot runs |
| `render-scene:497` | rule | home | Never store "previous frame" data in the shared GPU copy |
| `new:21` | hands-on | home | Exercise (done, with a "trace it yourself"): in the pattern of the test "Moved entities, skinned poses and mirrored instances carry their own motion", move one cube by a known step between two frames under a still camera, read the motion back and check its pixels against the step worked out by hand from the two view-projection matrices, and that the still pixels have exactly zero motion; then, with a breakpoint in `RecordMotionCopy`, find which elements the history copies in that frame (the moved cube's instance, listed from the write log); the solution is the test and the path. Evidence: `StrataTests/src/Renderer/GPUSceneMotionTests.cpp:494-528`, `:460`; `Strata/src/Strata/Renderer/SceneRenderer.cpp:1286-1393` |
| `render-scene:648-650` | term | home | Motion vector (velocity target); motion history; write version and write log |
| `render-scene:370` | code | use | The velocity part of `Mesh.vert` (lines 61-81) |
| `render-scene:161` | feature | use | The skinned variants, whose velocity forms blend the previous palette |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Clip space, the view-projection matrix and UVs | `gpu/coordinates` | must |
| The render scene's GPU copy | `draw/render-scene-gpu` | must |
| Palettes and the skinned variants | `draw/skinned` | must |
| The depth prepass and the `EQUAL` test | `gpu/frame-tour` | must |
| Compute dispatches | `gpu/compute` | must |
| Half-float formats | `basics/color` | must |
| The scene vertex shader | `draw/mirrors-camera-relative` | must |
| Temporal anti-aliasing and the jitter | `image/taa` | helps |

## Passed on

| Item | Type | To | Why |
| --- | --- | --- | --- |
| `render-scene:61` | feature | `light/sun-shadows-1` | Sun shadow caster selection (`FindShadowCasters`) is that page's by the one-home table |
| `render-scene:62` | feature | `light/sun-shadows-1` | `CanShadowView` is named with the sun's casters in the one-home table |
| `render-scene:141` | feature | `light/sun-shadows-1` | The outline gives the cascades' occlusion to that page; `draw/occlusion` links it |
| `render-scene:142` | feature | `light/sun-shadows-1` | The shadow cascade cache and its versions are that page's |
| `render-scene:448` | figure | `light/sun-shadows-1` | The cascade cache's figure goes with the cache |
| `render-scene:489` | rule | `light/sun-shadows-1` | The versions the shadow caches compare are taught with the cascade cache |
| `render-scene:652-654` | term | `light/sun-shadows-1` | Shadow caster and cascade, sub-texel caster, shadow cascade cache: that page defines them |
| `render-scene:729` | open | `light/local-shadows` | The culling of local shadow views is that page's by the outline and the one-home table |
| `render-scene:731` | open | `light/many-lights` | The GPU culling of light records is light culling |
| `render-scene:477` | rule | `light/brdf` | The one-home table makes `light/brdf` the home of shading independent of draw order; `draw/gpu-driven` links it |
| `render-scene:89` | feature | `gpu/binding` | The outline gives the `PipelineKey` cache to that page (render-scene 1.4 in its From) |
| `render-scene:92` | feature | `gpu/binding` | Vertex input layouts are part of a pipeline's state |
| `render-scene:579` | term | `gpu/binding` | Pipeline key: defined with the pipeline cache |
| `render-scene:90` | feature | `gpu/geometry-pool` | That page is the home of the geometry pool; `draw/batching` links it |
| `render-scene:278` | concept | `gpu/geometry-pool` | Shared geometry buffers are the geometry pool's idea |
| `render-scene:403` | figure | `gpu/geometry-pool` | The pool's memory map goes with the pool |
| `render-scene:482` | rule | `gpu/geometry-pool` | Reading geometry through the pool every frame is the pool's rule |
| `render-scene:574` | term | `gpu/geometry-pool` | Submeshes are first met with meshes on the GPU |
| `render-scene:588-591` | term | `gpu/geometry-pool` | Geometry pool, arena, `GeometryHandle`, compaction: that page defines them |
| `render-scene:182` | feature | `gpu/debugging` | The list of debug views and their mechanism are that page's; each view is read on its subject's page |
| `render-scene:479` | rule | `gpu/frame-tour` | That page is the home of the depth prepass, `EQUAL` and invariant positions |
| `render-scene:606-607` | term | `gpu/frame-tour` | `EQUAL` depth test and depth prepass: defined with the frame's passes |
| `render-scene:608` | term | `basics/math-projection` | Reversed Z as mathematics: one entry with `foundation:634` there (book.md's row of depth and reversed Z; the merge "Reversed Z and NDC"); `gpu/coordinates` keeps Strata's convention and links |
| `render-scene:644` | term | `gpu/coordinates` | Winding and front faces: that page states the counter-clockwise convention |
| `render-scene:620` | term | `gpu/upload-queue` | Staging buffers are that page's mechanism |
| `render-scene:625` | term | `gpu/compute` | Prefix allocation by atomics is taught with the compute model (render-scene concept 14 in its From) |
| `render-scene:627` | term | `gpu/readback-timing` | Readback is that page's |
| `render-scene:467` | rule | `assets/residency` | One rule with `assets:539` (critic-assets-10): that page keeps the why-box and teaches the `use_count() == 1` check; `draw/asset-requests` keeps a `use` row that shows the rule applied |
| `render-scene:571` | term | `basics/data-structures` | Arrays of structs against structs of arrays are that primer's |
| `render-scene:593-594` | term | `basics/math-geometry` | Frustums and boxes as mathematics are that primer's |
| `render-scene:646` | term | `basics/math-bases` | The cofactor matrix is a word of mathematics taught from zero there with normals through the inverse transpose (R43, R46); `draw/mirrors-camera-relative` holds a `use` row for the cofactor normal in its shaders |
| `render-scene:605` | term | `basics/signals` | Ordered dither is that primer's |
| `render-scene:158` | feature | `animation/skinning` | The palette's formula is "how the joint matrices are made"; `animation:151` is the same feature, homed there |
| `render-scene:491` | rule | `animation/skinning` | `animation:456` is the same rule, homed there with the skin's influences |
| `render-scene:636` | term | `animation/skeletons` | Joints and skeletons are taught there |
| `render-scene:637-639` | term | `animation/skinning` | Inverse bind matrix, palette, linear blend skinning: how joint matrices are made |
| `render-scene:641` | term | `animation/system` | `ISkinningPoses` is taught with the Animation system's scene services |
| `render-scene:642` | term | `animation/culling` | WhenVisible animators are that page's subject |
| `render-scene:550` | hands-on | `make/performance` | A game maker's check of draws and culling; that page takes this inventory's game tutorial |
| `render-scene:553` | hands-on | `make/performance` | The LOD view and the quality presets, for game makers |
| `render-scene:555` | hands-on | `make/performance` | The cost of shadows per object, for game makers |
| `render-scene:557` | hands-on | `make/performance` | The streaming view, for game makers |
| `render-scene:559` | hands-on | `make/transforms-units` | A negative scale mirrors an object and still renders and lights correctly: a game maker meets scale there |
| `render-scene:561` | hands-on | `make/animation` | Setting an animator's culling mode is a game maker's animation step |
| `render-scene:706` | open | `nowhere` | A surveyor's note about the files and line ranges it did not read |
| `render-scene:718` | open | `nowhere` | A surveyor's note that the documents do not date some features; the pages date what section 1's Release column dates |

## Not taken

none

## Questions for the planner

none
