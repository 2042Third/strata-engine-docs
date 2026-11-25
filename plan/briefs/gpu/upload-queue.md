# Brief: `gpu/upload-queue`

| Field | Value |
| --- | --- |
| Title | Staging and the upload queue |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `gpu/resources-lifetimes` |
| From | render-core; the mechanism: `PlanStep`, `StagingPool`, the transfer queue, `PrepareBackBuffer` (what assets queue and when is `assets/uploads`') |
| Unit | `plan/allocation/gpu.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `gpu/upload-queue` — Staging and the upload queue

**Covers.** The job: move bytes from the CPU into GPU memory at a bounded cost per frame, and let the frame wait for
the display only after the uploads were sent. The problem (GPU-local memory is not writable by the CPU; a large upload
stalls a frame) and the approaches (staging rings, copy queues, budgets per frame). The map is the upload path's data
flow. The contract: staging is released after the copies that read it are recorded, and those command lists execute
before `SubmitBatch` or the next `BeginFrame`; a ticket is complete once the GPU ran every copy recorded before it;
nothing renders into the back buffer before `Renderer::PrepareBackBuffer`. The toy is a staging ring with one fence per
frame.

The real code: `StagingPool`'s design note (powers of two from 64 KiB, reuse after the batch's fence, idle staging up to
16 MiB, all of it released after 120 idle frames); how staging is written: write-combined memory (the CPU's writes are
gathered into bursts, and reading it back is slow), so a step that writes 512 KiB or more into reused staging spreads
its copies over the job workers in pieces of 256 KiB, while new staging is written by the main thread alone, because
its first writes fault pages in one at a time (the measurements of the code's comment); `PlanStep`, which sizes a step
to the bytes
and time left in the frame at the measured speed, rounds to granules and lets the frame's first step always make
progress; the queue's batches, tickets, scene-data uploads in steps of 16 MiB, copies of levels on the GPU and
statistics; the transfer queue, off because it measured no faster and used more memory, and the ownership transfers it
would need; `RendererUploadContext` and `IAssetGraphics`, so the asset layer never includes NVRHI. Last, the frame's
start: `Renderer::BeginFrame` rolls staging and the queue (its order is `gpu/vulkan-nvrhi`'s, used here), and
`PrepareBackBuffer` triggers the device's acquire wait and clears the back buffer black; the wait is the `Present` stage
of the frame profiler, a CPU stage outside the work time and no GPU stage, which `core/profiling` lists. Alternatives,
tests (`GPU.UploadQueue`, the asset upload tests) and changing safely close the page; the exercise traces one texture's
upload step by step.

**Leaves out.**

- What the assets queue and when: steps of `c_AssetUploadStepBytes`, finalize contexts → `assets/uploads`
- The device's acquire, its deferred wait and present → `gpu/vulkan-nvrhi`
- Residency budgets → `assets/residency`
- Mip streaming's uploads → `draw/mip-streaming`
- The render scene's GPU copy and its uploads → `draw/render-scene-gpu`

**Fit.** `fits`: about 4,500 words against L (5,000). The real code's three excerpts with how staging is written, the
transfer queue, the layer seam and the display wait with its `Present` stage take the most words.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-core:341` | concept | home | Uploads, staging memory and budgets; the mistakes of `writeBuffer` with big data every frame and of blocking a frame on a load |
| `render-core:84`, `render-core:85`, `render-core:86`, `render-core:87`, `render-core:88` | feature | home | `GPUUploadQueue`; `PlanStep`; transfer queue uploads, off; `StagingPool`; `RendererUploadContext` and `IAssetGraphics` |
| `render-core:45` | feature | home | Queue ownership transfers and copies from buffers into textures |
| `assets:200`, `assets:202`, `assets:203` | feature | home | Step planning, the staging pool and the optional transfer queue as the asset inventory lists them: the same mechanism as `render-core:85`, `:87` and `:86`, with its details (a tenth of the budget kept in reserve, `c_MaxPendingBytes` of 256 MiB, finalizations that return `AwaitingGPU`) |
| `assets:205` | feature | home | The back buffer's late wait, the same subject as `render-core:65` |
| `render-core:65` | feature | home | `Renderer::PrepareBackBuffer`: the first call of a frame on the back buffer, the `Present` stage, the black clear |
| `render-core:214` | feature | home | The `Present` stage, beside `render-core:65`: the display wait in `PrepareBackBuffer`, counted as a built-in CPU stage of the frame profiler (`ST_PROFILE_STAGE("Present")`) outside the work time, and no GPU stage (R31; moved from `gpu/readback-timing`) |
| `new:37` | feature | home | How staging is written: write-combined memory, named in plain words; a step that writes 512 KiB or more into reused staging spreads its copies over the job workers in pieces of 256 KiB (4 MiB took 0.4 to 1.2 ms on one thread of the reference machine, 0.15 to 0.3 ms spread); new staging is written by the main thread alone, because its first writes fault its pages in one at a time (spread, 4 MiB took 2.5 to 4.3 ms) (about 150 words). Evidence: `Strata/src/Strata/Renderer/GPUUploadQueue.cpp:31-37, 506-535`; `Strata/src/Strata/Renderer/GPUUploadQueue.h:224-227` |
| `render-core:455` | code | home | `Strata/src/Strata/Renderer/GPUUploadQueue.cpp:228-277`: `PlanStep`, budgeted by measured speed, deadline share and granules |
| `render-core:456` | code | home | `Strata/src/Strata/Renderer/StagingPool.h:16-32`: the design note, as a "design note" box |
| `render-core:452` | code | home | `Strata/src/Strata/Renderer/Renderer.cpp:289-310`: `PrepareBackBuffer`: the `Present` stage, the device's acquire wait, the black clear; `Renderer::BeginFrame`'s order before it (lines 267-282) is `gpu/vulkan-nvrhi`'s |
| `render-core:494` | figure | home | The upload path from asset bytes to a complete ticket |
| `render-core:543` | figure | home | The black frame `PrepareBackBuffer` guarantees when nothing draws (optional) |
| `render-core:565` | rule | home | Call `Renderer::PrepareBackBuffer()` before rendering into the back buffer |
| `render-core:567` | rule | home | Command lists that copy from released staging execute before `SubmitBatch` or the next `BeginFrame` |
| `render-core:690`, `render-core:743`, `render-core:744`, `render-core:746` | term | home | Transfer queue; staging buffer; upload budget, step and granule; ticket |
| `render-scene:620` | term | home | Staging buffer, as the drawing part words it; one entry with `render-core:743` |
| `assets:694`, `assets:697` | term | home | Staging pool; queue ownership transfer |
| `render-core:34` | feature | use | The device's deferred acquire wait, which `PrepareBackBuffer` triggers |
| `render-core:320` | concept | link | Where the display wait is placed, taught on the device's page |
| `render-core:64` | feature | use | `Renderer::BeginFrame`, as the frame start of staging and the queue |
| `new:38` | hands-on | home | Exercise ("trace it yourself"): one large texture's upload on the source build: a breakpoint in `GPUUploadQueue::PlanStep` while the texture loads, the step's bytes, the measured speed and the time left read on each call, and the frame its ticket completes in. Evidence: `Strata/src/Strata/Renderer/GPUUploadQueue.cpp:228-277` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Resources, lifetimes and event queries | `gpu/resources-lifetimes` | must |
| GPU resources in NVRHI: staging buffers and their CPU access | `gpu/vulkan-nvrhi` | must |
| The device's frame: acquire, the deferred acquire wait, present | `gpu/vulkan-nvrhi` | must |
| Queues and queue families | `gpu/how-a-gpu-frame-works` | must |
| The layer table and why the asset layer may not include the renderer | `core/layers-registries` | must |
| Engine services | `core/engine-modules` | helps |
| What an asset is | `assets/what-is-an-asset` | helps |
| Powers of two | `basics/numbers` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `granule` | granule | - |
| `queue-ownership-transfer` | Queue ownership transfer | - |
| `staging-buffer` | Staging buffer | - |
| `staging-pool` | Staging pool | - |
| `step` | step | - |
| `ticket-upload` | Ticket (upload) | - |
| `transfer-queue` | Transfer queue | - |
| `upload-budget-gpu` | Upload budget (gpu) | - |
