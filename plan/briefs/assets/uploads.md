# Brief: `assets/uploads`

| Field | Value |
| --- | --- |
| Title | Budgeted uploads |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `assets/residency`, `assets/texture-cooking`, `gpu/upload-queue` |
| From | assets "Budgeted uploads and staging": what is queued and when (steps of `c_AssetUploadStepBytes`, the first step of a frame, `AssetFinalizeContext` and `AssetFinalizeResult`, `Texture::UploadLevels`, one batch per `Update`); the mechanism is `gpu/upload-queue`'s |
| Unit | `plan/allocation/assets.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `assets/uploads` — Budgeted uploads

**Covers.** The job: get the bytes of finalized assets to the GPU in steps that fit the frame's byte and time budgets,
so that a 90 MB texture never stalls a frame and every frame makes progress. The problem takes one paragraph (upload
rings, copy queues, caps per frame) that links `gpu/upload-queue`, which owns the mechanism: `PlanStep`, the staging
pool, the transfer queue and `PrepareBackBuffer`. The map: the asset layer's side (`AssetFinalizeContext`,
`AssetFinalizeResult`, `c_AssetUploadStepBytes`, `AssetUploadContext`, `IAssetGraphics`) and the renderer's
(`RendererUploadContext`, `GPUUploadQueue`, `Texture`). The contract: a finalizer records into the context and never
into a graphics API, which the asset layer does not include; steps are at most 4 MiB, sized to what is left of the
bytes, of the milliseconds and of the time to the deadline; the frame's first step goes whatever the byte and time
budgets say, but every step through staging, the first too, waits while the staging in flight leaves it no room (the
first within `StagingBytes`, later ones within `GetStagingRoom`); bytes are reported; `Pending` continues in a later
frame, `AwaitingGPU` when the copies run on the transfer queue; and the manager opens one batch per update and submits
it before rendering. The staging bound sets the throughput: with the default 32 MiB, sustained uploads reach about
28 MiB a frame, and about half the budget when frames come faster than the copies, unless the 16 MiB and 4 ms of a
frame stop them first; the code advises raising all three for a loading screen, which a game cannot do (no script
function and no settings section sets them). A toy of about 40 lines uploads in steps, in the shape of the tests'
`SteppedAsset`.

The real code: the contract in `Asset.h` (the step size, the results, the context and its staging room); the seam in
`AssetUploadContext.h`; the finalize part of `ProcessCompletions` (the budgets each finalizer gets; `Pending` keeps its
place in line; `AwaitingGPU` steps aside); `Texture::FinalizeOnMainThread` (the GPU texture made, the levels uploaded,
the CPU copy freed within the deadline before publication, the bindless slot and the texture-table index allocated at
publication); and `UploadLevels` (small levels stacked in one staging buffer, large ones in power-of-two runs of block
rows). Figure 489 places the steps within a frame: 4 ms of finalization, 2 ms of upload steps with a tenth kept in
reserve. Then the alternatives, the tests (`Asset.Finalize`), and changing it safely (the layering test refuses NVRHI and
Vulkan headers in `Asset/`). Exercises: drive the finalize contract without a GPU and show that no frame uploads more
than its budget; trace it yourself: a breakpoint in `Texture::FinalizeOnMainThread` while a large texture arrives shows
the frames its upload takes and the bytes each call reports.

**Leaves out.**

- `PlanStep`, the staging pool, fences, the transfer queue and `PrepareBackBuffer` → `gpu/upload-queue`
- Bindless slots that change when a texture's levels change → `draw/mip-streaming`
- How meshes reach the geometry pool → `gpu/geometry-pool`
- Room before arrival, which can hold an arrival back → `assets/residency`

**Fit.** `fits`: about 4,665 words against L (5,000). Four excerpts and the contract's many fields, with the staging
bound, take the most words.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `assets:329` | concept | home | Budgeted GPU uploads and staging memory, from the asset side |
| `assets:58` | feature | home | The upload seam: `AssetUploadContext` and the `IAssetGraphics` engine service |
| `assets:91` | feature | home | The finalize contract: `AssetFinalizeContext` and `AssetFinalizeResult` |
| `assets:199` | feature | home | Steps of at most `c_AssetUploadStepBytes`; the frame's first step goes whatever the byte and time budgets say, within the staging bound |
| `assets:201` | feature | home | Texture uploads: levels stacked or in runs of rows, the CPU copy freed before publication |
| `assets:204` | feature | home | One batch per update, submitted before rendering |
| `render-core:108` | feature | home | The `Texture` asset's GPU side: its finalization uploads in planned steps (its level changes are `draw/mip-streaming`'s) |
| `assets:440` | code | home | `Strata/src/Strata/Renderer/Texture.cpp:584-676`: `UploadLevels` |
| `new:14` | code | home | `Strata/src/Strata/Asset/Asset.h:43-119`: `c_AssetUploadStepBytes`, `AssetFinalizeResult` and `AssetFinalizeContext` with its staging room |
| `new:15` | code | home | `Strata/src/Strata/Asset/AssetUploadContext.h:10-47`: the upload context and `IAssetGraphics`, the seam without a graphics API |
| `new:16` | code | home | `Strata/src/Strata/Renderer/Texture.cpp:464-537`: `Texture::FinalizeOnMainThread`, from upload to publication |
| `new:36` | concept | home | The staging bound and the throughput it gives, about 120 words: a step through staging waits while the staging in flight leaves it no room (the frame's first within `StagingBytes`, later ones within `GetStagingRoom`, one step less); with the default 32 MiB, sustained uploads reach about 28 MiB a frame, about half the budget when frames come faster than the copies, unless `UploadBytesPerFrame` (16 MiB) or `FinalizeMsPerFrame` (4 ms) stop them first. Evidence: `Strata/src/Strata/Asset/Asset.h:72-78`; `Strata/src/Strata/Asset/AssetResidency.h:47-64` |
| `new:37` | not-done | home | A game cannot raise its streaming budgets for a loading screen: no script function and no settings section sets the upload, finalization and staging budgets, and the runtime's `--asset-budget-mb` sets only the GPU texture budget. Evidence: `Strata/src/Strata/Asset/AssetResidency.h:56-64` (raise all three for a loading screen); `git grep -ln -e UploadBytesPerFrame -e FinalizeMsPerFrame 822a7a46 -- Strata/src StrataEditor/src StrataRuntime/src StrataScriptCore` finds only the asset manager's files and the editor's (`StrataEditor/src/Editor/EditorStreamingCommands.cpp`, `StrataEditor/src/Panels/StreamingPanel.cpp`); `StrataRuntime/src/RuntimeApplication.cpp:56`, `:94-95` |
| `new:38` | hands-on | home | Trace it yourself (D27): a breakpoint in `Texture::FinalizeOnMainThread` while a large texture arrives shows the frames its upload takes, the bytes each call reports and where it ends `Pending`. Evidence: `Strata/src/Strata/Renderer/Texture.cpp:464-537` |
| `assets:489` | figure | home | Upload steps planned within a frame |
| `assets:545` | rule | home | Upload in steps of at most `c_AssetUploadStepBytes` within the context's budget; report bytes |
| `assets:565` | rule | home | The asset layer includes no graphics API |
| `assets:591` | hands-on | home | Drive the finalize contract without a GPU |
| `assets:690-691` | term | home | Upload, upload step |
| `assets:698-699` | term | home | Upload context, batch (of uploads) |
| `assets:414` | code | use | `ProcessCompletions` 1171-1217: the finalize part (home `assets/loading`) |
| `assets:206` | feature | use | Bindless slots resolved every frame (taught in `draw/mip-streaming`) |
| `render-core:85` | feature | use | `PlanStep` |
| `render-core:87` | feature | use | `StagingPool` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Staging, the upload queue, `PlanStep`, fences and the transfer queue | `gpu/upload-queue` | must |
| Resources, their states and deferred release | `gpu/resources-lifetimes` | must |
| Bindless slots and the texture table | `gpu/binding` | must |
| The CPU and the GPU working on different frames | `gpu/how-a-gpu-frame-works` | must |
| Finalization and publication on the main thread | `assets/loading` | must |
| Room before arrival, and the frame's budgets | `assets/residency` | must |
| Cooked textures, their levels and block rows | `assets/texture-cooking` | must |
| Engine services | `core/engine-modules` | must |
| The layer table and its test | `core/layers-registries` | must |
| Mip streaming, which changes bindless slots | `draw/mip-streaming` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `batch-assets` | Batch (assets) | - |
| `upload` | Upload | - |
| `upload-context` | Upload context | AssetUploadContext |
| `upload-step` | Upload step | - |
