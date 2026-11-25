# Brief: `gpu/resources-lifetimes`

| Field | Value |
| --- | --- |
| Title | Resources and lifetimes |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `gpu/vulkan-nvrhi`, `gpu/compute`, `gpu/first-triangle` |
| From | render-core; deferred release; states and barriers in NVRHI (the compute model is `gpu/compute`'s) |
| Unit | `plan/allocation/gpu.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `gpu/resources-lifetimes` — Resources and lifetimes

**Covers.** The job: keep every GPU resource alive while the GPU may still use it, and in the right state for each
use, without waiting in a frame. The problem and the approaches: manual barriers or automatic tracking (NVRHI, render
graphs); frame-delayed deletion queues or fence-tracked collection. The map is the lifetime diagram. The contract:
NVRHI counts references, and a command list keeps alive what it references, but not the textures it only cleared or
resolved; states are tracked and barriers placed when binding sets change. Event queries are the one "has the GPU got
here?" signal of every lifetime system, polled and never waited for in a frame. The toy is a deletion queue fenced per
frame in about 40 lines.

The real code follows the data: `DeferredReleaseQueue` (batches fenced by event queries, completed in order, destroyed
within 0.25 ms a frame because one texture costs about 0.1 ms, progress without frames); its use when the renderer drops
its targets (`ReleaseRenderTargets`, with the comment on clears); volatile constant buffers, whose versions are paced by
an event query per submitted frame and the poll after the wait. The NVRHI pitfalls are rules with their reasons: never
take a handle's address; chains of UAV writes through one binding set need explicit barriers; a texture whose levels
compute writes is moved out of its undefined layout whole; a list that may open while another is open is not immediate;
volatile buffers have a fixed number of versions. Alternatives, tests (`GPU.Renderer.DeferredRelease` and the
frame-constant
tests), changing safely, and what went wrong before (20 thumbnails freed in one frame cost 2.1 to 2.3 ms). The exercise
drops a cleared target with `nullptr` and with `ReleaseDeferred` and counts the validation errors; a second traces one
render target from `ReleaseRenderTargets` to its destruction. The glossary entry here is the volatile constant buffer;
the plain constant buffer is said in one sentence and linked to `gpu/binding`.

**Leaves out.**

- The compute model and what a UAV barrier is → `gpu/compute`
- Staging memory and its fences → `gpu/upload-queue`
- Freed geometry ranges in the pool → `gpu/geometry-pool`
- Constant buffers as bindings and `FrameConstants` → `gpu/binding`
- Residency and eviction of assets → `assets/residency`

**Fit.** `fits`: about 5,450 words against L (5,000). Three concepts, three excerpts and seven rules with their reasons
take the most words, then the two exercises.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-core:329` | concept | home | Resource states and barriers: manual or tracked; NVRHI's automatic barriers and the explicit ones |
| `render-core:335` | concept | home | Reference counting and deferred destruction; the clears exception; the mistake `x = nullptr` in a resize |
| `render-core:346` | concept | home | Event queries as the universal "done" signal; the mistake of waiting on the GPU in a frame |
| `render-core:74`, `render-core:75`, `render-core:76`, `render-core:77`, `render-core:78` | feature | home | Automatic and explicit barriers; `DeferredReleaseQueue`; `Renderer::ReleaseDeferred`; volatile constant buffer pacing; event queries |
| `render-core:453` | code | home | `Strata/src/Strata/Renderer/DeferredReleaseQueue.cpp:14-76`: batches fenced by event queries, in order, within the frame's budget, with the design comment `Strata/src/Strata/Renderer/DeferredReleaseQueue.h:16-30` |
| `render-core:468` | code | home | `Strata/src/Strata/Renderer/SceneRenderer.cpp:2247-2262`: `ReleaseRenderTargets`' comment on clears and its release list, which ends in `Renderer::ReleaseDeferred` at line 2340 |
| `render-core:469` | code | home | `Strata/src/Strata/Renderer/SceneRenderer.cpp:1457-1504`: versions of volatile constants paced by event queries; the poll after the wait |
| `render-core:492` | figure | home | Resource lifetime: release, pending, completed, destroyed within 0.25 ms a frame; NVRHI's references and the clears exception |
| `render-core:549`, `render-core:551`, `render-core:553`, `render-core:556` | rule | home | A handle's address; same-set UAV chains; render targets through `ReleaseDeferred`; destruction costs about 0.1 ms |
| `render-core:558`, `render-core:560`, `render-core:562` | rule | home | A compute-written texture's layout whole first; non-immediate lists; volatile buffers' versions |
| `render-core:640` | hands-on | home | The deferred release experiment |
| `new:36` | hands-on | home | Exercise ("trace it yourself"): one render target from `SceneRenderer::ReleaseRenderTargets` to its destruction: resize the Scene view on the source build, break in `DeferredReleaseQueue::Release` and `Collect`, and see the batch destroyed only once its event query completed, frames later. Evidence: `Strata/src/Strata/Renderer/SceneRenderer.cpp:2247, 2340`; `Strata/src/Strata/Renderer/DeferredReleaseQueue.cpp:14, 50` |
| `render-core:708` | term | home | Volatile constant buffer, its own glossary entry (R33 D34, critic-render-core-16); the plain constant buffer is `gpu/binding`'s entry (`new:41`) |
| `render-core:747` | term | home | Deferred release |
| `render-core:702` | term | use | Barrier and resource state |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| NVRHI's device, command lists and immediate lists | `gpu/vulkan-nvrhi` | must |
| GPU resources in NVRHI: descs, initial states, render targets | `gpu/vulkan-nvrhi` | must |
| Compute shaders, UAVs and the barrier between dispatches | `gpu/compute` | must |
| Writing a GPU test and its error count | `gpu/first-triangle` | must |
| Frames in flight and fences | `gpu/how-a-gpu-frame-works` | must |
| Smart pointers, reference counting and RAII | `basics/cpp-memory` | must |
| Queues as a data structure | `basics/data-structures` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `constant-buffer` | Constant buffer | - |
| `deferred-release` | Deferred release | - |
| `volatile-constant-buffer` | volatile constant buffer | - |
