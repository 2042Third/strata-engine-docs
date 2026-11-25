# Brief: `assets/loading`

| Field | Value |
| --- | --- |
| Title | Loading without stalling |
| Kind | I |
| Size | XL |
| Tracks | E |
| Needs | `assets/handles-meta`, `core/jobs` |
| From | assets |
| Unit | `plan/allocation/assets.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `assets/loading` — Loading without stalling

**Covers.** The job: turn a handle into a loaded object while no frame ever waits, and while loads are reloaded,
cancelled, evicted or failed under it. This page carries the part's full section on the problem: blocking loads behind
a loading screen, loads in the background that call back, loads in the background that code polls; Strata polls. The
map (figure 461): `AssetManagerBase` and its entries; the streaming queue; the I/O pool that reads and the workers that
decode; the completion queue behind a shared `LoadState`; `Update` on the main thread; the loader registry; the two
managers that supply the bytes. The contract: `GetAsset` never blocks. It returns the loaded object, the previous one
during a reload, or null; it stamps the request and asks for the load. Code handles "not loaded yet" every frame and
polls, never waits. Typed accessors return null for a wrong type. `LoadAssetSync` is for tools, tests and loading
screens, and never runs from a finalizer. Loaders run on workers, may take the bytes over, and check `IsCancelled`.
Every load ends in exactly one completion, and finalization and publication happen on the main thread. A toy of about
60 lines (a queue, one worker, a completion list polled each frame, a generation counter) shows four ways a simple
loader goes wrong, which Strata guards against.

The real code, in the order a load flows: `GetAsset` and `RequestLoad`; the queue (figure 464: keys of priority,
negative score and request order in a `std::map`; a repeat raises and never lowers; dispatch while the bytes in flight
stay under 128 MiB and the reads under two per I/O thread; one load always runs; `Pump` never recurses); `RunLoad`
(read on the I/O pool, dependencies prefetched when the read completes, decoding on a worker, exceptions turned into
failed loads); the loader registry and the renderer's loaders (`TakeBytes`); `ProcessCompletions`, shown in parts
(stale completions discarded by their generation; publication; the room it makes is `assets/residency`'s and the budget
it hands to finalizers `assets/uploads`'); generations and the state machine (figure 458), where a failed load stays
Failed with its error (`GetAssetError`, `loadError` of `asset.info`) and `GetAsset` returns null every frame without
trying again, until `ReloadAsset`, `UnloadAsset` or a new registration makes it Unloaded (in a game nothing does); the
`Asset` base class. Then the manager's other entry points: peeking without requesting, synchronous loads, replacing a
loaded object (a material while its value is dragged), memory assets, source revisions and content versions for caches,
the active manager and `Scene::GetAssetManager`, loads waiting for a first import, cancelling and unloading, and the
waiting helpers. Then the alternatives, the tests (`Asset`, `Asset.StreamingQueue`), and changing it safely. Exercises:
trace a load with breakpoints and note which thread runs each stage; predict the queue's dispatch order for a list of
requests.

**Leaves out.**

- Memory budgets, eviction and pins → `assets/residency`
- Dependencies, closures and prefetch rules → `assets/references`
- The upload budget a finalizer works within → `assets/uploads`
- Partial loads and range reads of textures → `draw/mip-streaming`
- What the renderer requests each frame, and the resolve cache → `draw/asset-requests`
- Loading whole scenes in slices → `world/sub-scenes`
- The job system's pools → `core/jobs`

**Fit.** `fits`: about 7,995 words against XL (8,000), one page in sections. Six excerpts (two of them long), three
concepts and the manager's other entry points take the most words.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `assets:286` | concept | home | Asynchronous loading and the main-thread rule, with the approaches |
| `assets:292` | concept | home | Generations: stale completions are discarded at every step |
| `assets:297` | concept | home | Priority queues and backpressure: a bound on bytes, not on count |
| `assets:41-42` | feature | home | Asset states and priorities; the `Asset` base class |
| `assets:54` | feature | home | The loader registry, filled by the module that owns each type |
| `assets:65-68` | feature | home | `AssetManagerBase`, typed accessors, `GetAsset` never blocks, `PeekLoadedAsset` |
| `assets:70-72` | feature | home | `LoadAssetSync`, `ReplaceLoadedAsset`, memory assets |
| `assets:74-77` | feature | home | Generations, source revisions, content and metadata versions, the active manager facade |
| `assets:80` | feature | home | A load waits in Loading while the asset's first import runs |
| `scene-ecs:41` | feature | home | `Scene::GetAssetManager()`, the path from scene code to assets, taught with the active manager's facade |
| `assets:86-90` | feature | home | The streaming queue, reads on I/O and decoding on workers, `AssetLoadData`, the completion queue, main-thread finalization |
| `assets:92-94` | feature | home | Cancellation, exception containment, waiting helpers |
| `new:32` | feature | home | A failed load stays failed, about 100 words: `RequestLoad` starts a load only from Unloaded, so `GetAsset` returns null for a Failed asset every frame and never tries again; the error is kept (`GetAssetError`, `loadError` of `asset.info`); only `ReloadAsset` (in the editor, a changed source or a re-import), `UnloadAsset` or a new registration make it Unloaded again, and in a game nothing does. Evidence: `Strata/src/Strata/Asset/AssetManager.cpp:459-463`, `:1238-1243`, `:718-763`; `Strata/src/Strata/Asset/AssetManager.h:354`, `:358-369`; `StrataEditor/src/Editor/EditorAssetCommands.cpp:690` |
| `assets:382` | code | home | `Strata/src/Strata/Asset/Asset.h:161-193`: the `Asset` base class, the contract of every type |
| `assets:386` | code | home | `Strata/src/Strata/Renderer/RendererRegistration.cpp:81-118`: the renderer's loaders, `TakeBytes` and the BC fallback |
| `assets:406` | code | home | `Strata/src/Strata/Asset/AssetManager.cpp:330-349`: `GetAsset`, with `RequestLoad` at 440-484 |
| `assets:408` | code | home | `Strata/src/Strata/Asset/AssetStreamingQueue.cpp:148-207`: `CanDispatchLocked` and `Pump`, with the key at `AssetStreamingQueue.h:117-120` |
| `assets:411` | code | home | `Strata/src/Strata/Asset/AssetManager.cpp:583-684`: `RunLoad`, exactly one completion on every path |
| `assets:414` | code | home | `Strata/src/Strata/Asset/AssetManager.cpp:1040-1274`: `ProcessCompletions`, shown in parts: 1088-1113 (stale completions) and 1219-1246 (publication); 1115-1169 is quoted by `assets/residency`, 1171-1217 by `assets/uploads` |
| `assets:458` | figure | home | The asset state machine, with the generation bumps and the ways out of Failed (`ReloadAsset`, `UnloadAsset`, a new registration) |
| `assets:461` | figure | home | The three-stage load timeline: main thread, I/O thread, worker |
| `assets:464` | figure | home | The queue's ordering and its backpressure |
| `assets:537` | rule | home | `GetAsset` never blocks; handle "not loaded yet" every frame |
| `assets:568` | rule | home | Polling, not waiting |
| `scene-ecs:557` | rule | home | Code that works for a scene reaches assets through `Scene::GetAssetManager()` |
| `assets:577` | hands-on | home | Trace a load and the thread of each stage |
| `assets:597` | hands-on | home | The streaming queue puzzle |
| `assets:657` | term | home | Memory asset |
| `assets:661-671` | term | home | Loader, finalize, publish, asset state, priority and score, streaming queue, in flight, backpressure, generation, source revision, content version |
| `automation:739` | term | home | Backpressure, one glossary entry with `assets:668`, taught from zero here: refusing or slowing new work while too much is pending; the automation server's form of it is `automation/rpc-server`'s |
| `assets:73` | feature | use | `ReloadAsset` serves the old version (taught in `assets/importing`) |
| `assets:91` | feature | use | The finalize contract (taught in `assets/uploads`) |
| `assets:120` | feature | use | Dependencies prefetched when a read completes (taught in `assets/references`) |
| `assets:164` | feature | use | The BC decode in the texture loader |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| What an asset, a source file and a stored form are | `assets/what-is-an-asset` | must |
| Handles and asset metadata | `assets/handles-meta` | must |
| The job system's pools (`Submit`, `SubmitIO`) and the main thread's role | `core/jobs` | must |
| The frame loop: an update once per frame | `core/frame-loop` | must |
| Mutexes, locks taken one at a time, atomics | `basics/threads` | must |
| `std::map` ordering, tuples, lambdas and `std::function` | `basics/cpp-generic` | must |
| Shared ownership (`Ref`) | `basics/cpp-memory` | must |
| `std::span` and `std::optional` | `basics/cpp-modern` | must |
| Virtual functions and interfaces | `basics/cpp-classes` | must |
| Exceptions caught where third-party code throws | `core/conventions` | must |
| Priority queues and the cost of their operations | `basics/trees-graphs` | helps |
| Imports in the background | `assets/importing` | helps |
| Breakpoints and threads in a debugger | `core/debugging` | helps |
| The finalize results `Pending` and `AwaitingGPU` | `assets/uploads` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `asset-state` | Asset state | - |
| `backpressure` | Backpressure | - |
| `content-version` | Content version | change list |
| `finalize` | Finalize | - |
| `generation-assets` | Generation (assets) | - |
| `in-flight` | In flight | - |
| `loader` | Loader | - |
| `memory-asset` | Memory asset | - |
| `priority` | Priority | - |
| `publish-assets` | Publish (assets) | - |
| `source-revision` | Source revision | - |
| `streaming-queue` | Streaming queue | - |
