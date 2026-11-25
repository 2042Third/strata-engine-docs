# Brief: `draw/asset-requests`

| Field | Value |
| --- | --- |
| Title | Asking for assets at draw time |
| Kind | I |
| Size | M |
| Tracks | E |
| Needs | `draw/bounds-culling`, `assets/residency` |
| From | render-scene; request priorities, prefetch, the resolve cache, fallbacks and the streaming view; what renderers publish for `draw/mip-streaming` |
| Unit | `plan/allocation/draw.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `asset-resolve-cache` | Asset resolve cache | - |
| `prefetch-distance` | Prefetch distance | - |
| `replay` | Replay | - |
| `request-priority` | Request priority | - |
