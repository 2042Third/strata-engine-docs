# Brief: `gpu/readback-timing`

| Field | Value |
| --- | --- |
| Title | Readback and GPU timing |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `gpu/frame-tour`, `core/profiling` |
| From | render-core; home of GPU timestamps and stages (`core/profiling` shows them); the one-pixel readback that picking uses |
| Unit | `plan/allocation/gpu.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `gpu/readback-timing` — Readback and GPU timing

**Covers.** The job: bring GPU data back to the CPU, and measure the GPU's time per pass, without ever making a frame
wait. The problem and the approaches: readback through staging memory, polled; timestamp queries, vendor tools and
pipeline statistics. The map is the profiler's ring of slots. The contract: readbacks and timestamps are polled once a
frame; results arrive two to three frames late and are dropped rather than waited for; `Renderer::ReadTexture` and
`ResolveGPUStats(true)` block and are for tests and tools only. The toy is a ring of readback slots in about 40 lines.

The real code: `TextureReadback` (each refusal with its reason, an overflow-safe region check, a staging texture and an
event query); `BufferReadback`; picking, a one-pixel read of the entity-ID target where 0 means nothing was drawn;
`ImageWriter` (PNG, and Radiance `.hdr` files from linear floats, which the probe bake saves, linked to
`indirect/probes`) and `ImageReader`; the timestamp pool (reset on the host, reads that never wait, a mask for wrapping);
`GPUProfiler` (frames in flight + 2 slots of 256 timestamps); `GPUPassTimer` (one timestamp per boundary, intervals only
within one slot); the 17 stages of `RendererGPUStages`, with `GPU.UI` and `GPU.ImGui` added by others; a renderer's own
GPU times; that `Present` is no GPU stage (a CPU stage of the frame profiler, linked to `gpu/upload-queue`); tile-based
drivers, and why stage boundaries go where passes end.
The registration order is stated as the code has it, with both of its exceptions. The Performance panel's GPU stages
for a Showcase frame are the figure. Alternatives, tests (`GPU.TextureReadback`, the timer tests), changing safely
(a new stage and the five lists that name the stages), and three exercises: trace one frame's timestamps to the
profiler; add a GPU stage; write a screenshot tool that never stalls.

**Leaves out.**

- The frame profiler, CPU stages, percentiles and Tracy → `core/profiling`
- Picking in the Scene view and gizmos → `editor-ui/scene-view`
- The Performance panel's drawing → `editor-ui/instrument-panels`
- Exposure's readback and its epochs → `image/pre-exposure`
- The culling counters read back on the GPU path → `draw/gpu-driven`
- Perf budgets and measuring on the reference machine → `engineering/perf-lab`

**Fit.** `fits`: about 5,400 words against L (5,000). Two concepts, three excerpts, ten features and three exercises
take the most words; the page needs no split.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-core:418` | concept | home | Readback through staging, polled; the mistake of blocking in a frame |
| `render-core:420` | concept | home | GPU timing with timestamps; always-on stages, late results, dropped frames; the mistake of waiting for timestamps or expecting stable ids |
| `render-core:66` | feature | home | `Renderer::ReadTexture`, the blocking readback of tests, tools and screenshots |
| `render-core:201`, `render-core:202`, `render-core:203`, `render-core:204` | feature | home | `TextureReadback`; `BufferReadback`; picking; `ImageWriter` (PNG, and Radiance `.hdr` files, RGBE and run-length encoded, from linear floats, which the probe bake saves and the HDR importer reads: one clause linking `indirect/probes`, about 40 words; `Strata/src/Strata/Renderer/ImageWriter.h:13-22`) and `ImageReader` |
| `render-core:44` | feature | home | The GPU timestamp pool |
| `render-core:210`, `render-core:211`, `render-core:212`, `render-core:213` | feature | home | `GPUProfiler`; `GPUPassTimer`; `RendererGPUStages`; a renderer's GPU times |
| `render-core:214` | feature | link | The `Present` stage, homed on `gpu/upload-queue`: the page says that Present is no GPU stage (R31) |
| `render-core:471` | code | home | `Strata/src/Strata/Renderer/TextureReadback.cpp:7-74`: a careful API: every refusal with a reason, the overflow-safe check, staging and an event query |
| `render-core:470` | code | home | `Strata/src/Strata/Renderer/GPUProfiler.cpp:357-394`: `GPUPassTimer`: one timestamp per boundary, intervals only within a slot |
| `new:17` | code | home | `Strata/src/Strata/Renderer/SceneRenderer.cpp:4239-4265`: `ReadEntityIDAsync` and `GetEntityFromID`: a one-pixel readback, and the prepass writing the entity + 1 |
| `new:18` | erratum | home | `Docs/DeveloperGuide.md:6235-6237` says `RendererGPUStages::Get` registers in frame order with one exception (depth of field after motion blur); `GPU.Aerial` is a second: registered before `GPU.Cull`, timed after it. Evidence: `Strata/src/Strata/Renderer/GPUProfiler.cpp:52-53`; `Strata/src/Strata/Renderer/SceneRenderer.cpp:3360, 3381` |
| `render-core:511` | figure | home | The profiler's ring: open, pending and free slots, timestamps per slot, resolved two to three frames later |
| `render-core:540` | figure | home | The Performance panel (or `editor.perf`) with the GPU stages of a Showcase frame |
| `render-core:569` | rule | home | Never block a frame on the GPU: poll readbacks and timestamps |
| `render-core:609` | rule | home | Time every new pass in a GPU stage, registered in frame order and in the five lists |
| `render-core:643`, `render-core:646` | hands-on | home | Add a GPU stage; a non-blocking screenshot tool |
| `new:48` | hands-on | home | Exercise ("trace it yourself"): one frame's timestamps to the profiler on the source build: a breakpoint in `GPUProfiler::ResolvePending`, the oldest pending slot read once the GPU completed it, and the frame it belongs to compared with the frame now recorded (two to three frames apart). Evidence: `Strata/src/Strata/Renderer/GPUProfiler.cpp:200-237` |
| `render-core:758`, `render-core:759`, `render-core:760`, `render-core:761` | term | home | Readback; timestamp query; GPU stage; tile-based renderer |
| `editor-core:737`, `render-image:654`, `render-scene:627` | term | home | Readback, as other parts word it; one entry with `render-core:758` |
| `build-test:669` | term | home | Readback, as the build's glossary words it (GPU results copied to the CPU to check them); one entry with `render-core:758` |
| `render-direct:758` | term | home | GPU stage; one entry with `render-core:760` |
| `foundation:610` | term | home | GPU timestamp; one entry with `render-core:759` |
| `render-core:773` | term | link | Picking, taught with the Scene view |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The frame's passes and their stages | `gpu/frame-tour` | must |
| Measuring the frame: the frame profiler and its stages | `core/profiling` | must |
| Event queries and deferred release | `gpu/resources-lifetimes` | must |
| Staging memory | `gpu/upload-queue` | must |
| GPU resources in NVRHI: staging textures and buffers read by the CPU | `gpu/vulkan-nvrhi` | must |
| Integer overflow | `basics/numbers` | helps |
| Picking in the Scene view | `editor-ui/scene-view` | helps |
| The Performance panel | `editor-ui/instrument-panels` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `gpu-stage-strata` | GPU stage (Strata) | GPU stage |
| `readback` | Readback | - |
| `tile-based-renderer` | Tile-based renderer | - |
| `timestamp-query` | Timestamp query | GPU timestamp |
