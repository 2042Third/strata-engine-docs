# Brief: `assets/residency`

| Field | Value |
| --- | --- |
| Title | Residency, eviction and pins |
| Kind | I |
| Size | XL |
| Tracks | E |
| Needs | `assets/loading`, `gpu/resources-lifetimes`, `basics/trees-graphs` |
| From | assets; home of residency, pins and eviction; room before arrival waits for the frames in flight |
| Unit | `plan/allocation/assets.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `assets/residency` — Residency, eviction and pins

**Covers.** The job: keep assets within a memory budget per pool, dropping what was requested longest ago, and never
what is in use or what the GPU still reads. The problem and how engines solve it: no budget, one budget, or budgets
per pool; LRU, LFU, priority classes or explicit unloads; with a table. The map: `AssetResidency` (budgets, pins, trims,
eviction), the manager's entries and recency orders, `IAssetGraphics` (the device's memory budget and its frames in
flight), and the manager extension seam. The contract: assets report memory per pool (`GetMemoryUsage`,
`GetFinalizedMemoryUsage`, `IsDataShared`). Code requests every frame what it uses, and holds handles, not `Ref`s.
Gameplay pins what it must keep, and releases it. No GPU memory that a frame in flight may use is freed. A toy of about
50 lines keeps an LRU cache within a byte budget (a list and a map); then come Strata's differences: pools, stamps by
request rather than by arrival, protections, room before arrival.

The real code: pools and budgets (figure 466; GPU textures 50% and GPU buffers 15% of the device's budget, CPU
unlimited); `TouchLocked`, where a request moves the asset's node to the end in constant time with `extract` and a
hinted insert (figure 468); `CanEvictLocked`, `EvictLocked` and `EvictToFitLocked` (pins, a grace window of the frames
in flight plus two, memory and built-in assets, objects held outside the manager by `use_count() == 1`, shared data);
trims after a scene switch; `MakeRoomFor` and the waiting arrivals of `ProcessCompletions` (figure 470: evict first,
reserve, wait the frames in flight plus one before allocating GPU memory, and arrivals behind wait together); memory
that changes without a new object (`UpdateMemoryUsage`); manager extensions, which free partly resident memory before
whole assets go; pins (`AssetPin`: RAII, a weak manager, one registration) and scripts' pins (`Assets::RequestLoad` and
`Release`); `TouchLoadedAssets` for still frames; the statistics and the Streaming panel (figure 504); and setting the
budgets (`asset.setBudget`, `--asset-budget-mb`). Then the alternatives, the tests (`Asset.Residency`,
`Asset.PartialResidency`), and changing it safely. Exercises: prove the LRU order with `FakeAssetManager` and show that
a held `Ref` is never evicted; watch evictions in the Showcase under a tight budget (one `asset.setBudget` line to paste,
and a link forward to `editor/commands`); keep a sound loaded from a script; trace it yourself: breakpoints in
`EvictToFitLocked` and `CanEvictLocked` under that budget show which protection keeps each asset that is not evicted.

**Leaves out.**

- Loading, finalization and generations → `assets/loading`
- Closures, group loads and prefetch → `assets/references`
- Keeping only some of a texture's levels resident → `draw/mip-streaming`
- Deferred release of GPU resources in general → `gpu/resources-lifetimes`
- How the Streaming panel draws its table cheaply → `editor-ui/instrument-panels`
- Every budget's default and every statistic, as tables → `reference/assets`
- Asking for sounds early, as a game maker → `make/sound`

**Fit.** `fits`: about 7,830 words against XL (8,000), one page in sections. Four concepts, four excerpts with four
figures, and four exercises take the most words.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `assets:302` | concept | home | Memory budgets and pools |
| `assets:307` | concept | home | LRU eviction with protections; the `Ref` pitfall |
| `assets:313` | concept | home | Pins; pinning everything is no budget at all (group loads are `assets/references`') |
| `assets:335` | concept | home | Room before arrival |
| `assets:56` | feature | home | Manager extensions: `ReleaseMemory` before whole assets are evicted, `OnUpdate`, `AddStats` |
| `assets:69` | feature | home | `TouchLoadedAssets`: many requests under one lock, for still frames |
| `assets:100-110` | feature | home | Pools, budgets, recency orders, eviction to budgets, protections, pins, trims, room before arrival, statistics, script pins, budget controls |
| `assets:189` | feature | home | `UpdateMemoryUsage`: totals follow a texture that gained or dropped levels |
| `assets:417` | code | home | `Strata/src/Strata/Asset/AssetResidency.cpp:325-349`: `TouchLocked`, a constant-time move with `extract` |
| `assets:419` | code | home | `Strata/src/Strata/Asset/AssetResidency.cpp:428-445`: `CanEvictLocked` and `EvictLocked`, with `EvictToFitLocked` at 523-542 |
| `assets:421` | code | home | `Strata/src/Strata/Asset/AssetResidency.cpp:544-570`: `MakeRoomFor` |
| `assets:422` | code | home | `Strata/src/Strata/Asset/AssetResidency.cpp:104-138`: `Pin` and `Unpin`, a weak manager and a registration |
| `assets:466` | figure | home | Memory pools and budgets: resident, reserved, pending, the in-flight window, headroom |
| `assets:468` | figure | home | The recency orders, one `std::map` per pool, and touch as a move to the end |
| `assets:470` | figure | home | Room before arrival, across frames |
| `assets:504` | figure | home | The Streaming panel under a 32 MB texture budget, with evictions |
| `assets:539`, `render-scene:467` | rule | home | Hold `AssetHandle`s across frames, not `Ref`s; request what you use every frame: one rule and one why-box here, since a held `Ref` keeps the asset from eviction (`draw/asset-requests` shows it applied: the resolve cache drops its references when the frame ends) |
| `assets:541` | rule | home | Pin what gameplay must keep; release it |
| `assets:543` | rule | home | Report shared data and accurate memory per pool |
| `assets:561` | rule | home | Never free GPU memory a frame in flight may use |
| `assets:594` | hands-on | home | Prove the LRU order, and the held `Ref` that is never evicted |
| `assets:619` | hands-on | home | Watch streaming in the Showcase: the Streaming panel, then a tight budget (the Mip and Streaming views are named and linked) |
| `assets:624` | hands-on | home | Keep a sound loaded with `Assets::RequestLoad` and `Release` |
| `new:33` | hands-on | home | Trace it yourself (D27): breakpoints in `EvictToFitLocked` and `CanEvictLocked` under a tight texture budget show where the walk stops at the grace window and which protection keeps each asset that is not evicted (a pin, a memory or built-in asset, a `Ref` held outside the manager, shared data). Evidence: `Strata/src/Strata/Asset/AssetResidency.cpp:428-435`, `:523-542` |
| `assets:673-681` | term | home | Residency, memory pool, budget, device memory budget, eviction, LRU, recency order, request (touch), grace window |
| `assets:683-686` | term | home | Pin, trim, room before arrival, reservation |
| `scripting:565` | term | home | `AssetPin`, one glossary entry with `assets:683`: a script's `Assets::RequestLoad` holds one until `Release` |
| `assets:414` | code | use | `ProcessCompletions` 1115-1169: room and the waiting arrivals (home `assets/loading`) |
| `assets:442` | code | use | The script side of pins (home `assets/references`) |
| `assets:58` | feature | use | `IAssetGraphics`: the device's budget and its frames in flight |
| `assets:213` | feature | use | What the Streaming panel shows (its drawing is `editor-ui/instrument-panels`') |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Loading, finalization, publication and generations; the `Asset` base class | `assets/loading` | must |
| Frames in flight | `gpu/how-a-gpu-frame-works` | must |
| Deferred release of GPU resources | `gpu/resources-lifetimes` | must |
| The device's memory and the budget it reports | `gpu/vulkan-nvrhi` | must |
| Shared and weak ownership, `use_count`, RAII and types that only move | `basics/cpp-memory` | must |
| Trees and maps, and the cost of their operations | `basics/trees-graphs` | must |
| `std::map` node handles: `extract` and an insert with a hint | `basics/cpp-generic` | must |
| Mutexes | `basics/threads` | must |
| Loading scenes, and a scene switch | `world/sub-scenes` | helps |
| Reading and running a command line | `start/how-to-read` | helps |
| Commands and the command registry | `editor/commands` | helps |
| A script's callbacks, such as `OnCreate` | `scripting/script-system` | helps |
| Textures kept partly resident | `draw/mip-streaming` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `budget-assets` | Budget (assets) | - |
| `device-memory-budget` | Device memory budget | - |
| `eviction` | Eviction | - |
| `grace-window` | Grace window | - |
| `lru` | LRU | least recently used |
| `memory-pool` | Memory pool | - |
| `pin` | Pin | AssetPin |
| `recency-order` | Recency order | - |
| `request-touch` | Request (touch) | - |
| `reservation` | Reservation | - |
| `residency` | Residency | - |
| `room-before-arrival` | Room before arrival | - |
| `trim` | Trim | - |
