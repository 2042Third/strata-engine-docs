# Brief: `draw/render-scene-gpu`

| Field | Value |
| --- | --- |
| Title | The render scene's GPU copy |
| Kind | I |
| Size | M |
| Tracks | E |
| Needs | `draw/batching`, `gpu/upload-queue` |
| From | render-scene "RenderSceneGPU"; the change logs it follows (`RecordInstanceChanges`, `RecordProxyChange`) |
| Unit | `plan/allocation/draw.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `culling-record` | Culling record | GPUProxy |
| `gpu-copy` | GPU copy | RenderSceneGPU |
| `mesh-table` | Mesh table | material table |
| `resident-proxy` | Resident (proxy) | - |
| `upload-budget-draw` | Upload budget (draw) | - |
