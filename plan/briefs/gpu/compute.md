# Brief: `gpu/compute`

| Field | Value |
| --- | --- |
| Title | Compute shaders: dispatches, thread groups, shared memory and atomics |
| Kind | C |
| Size | M |
| Tracks | E |
| Needs | `gpu/shaders` |
| From | new; render-core concepts 9, 13; render-scene concept 14 (prefix allocation); toy: a histogram and a prefix sum; home of the compute model and of UAV barriers, which draw, light, image and indirect use |
| Unit | `plan/allocation/gpu.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `gpu/compute` — Compute shaders: dispatches, thread groups, shared memory and atomics

**Covers.** The problem as a reader meets it: count the brightness of a million pixels into 256 bins, every frame. The
naive answer (one thread per pixel adding to one counter in memory) and where it breaks (every thread waits for the
same address). The idea: a dispatch of thread groups, each thread with its group and global IDs (`numthreads`,
`SV_DispatchThreadID`, `SV_GroupThreadID`); memory shared by a group and the barrier that waits for the whole group;
atomic operations; the resources a shader writes (UAVs: read-write structured buffers and storage images); the barrier
between two dispatches when one reads what the other wrote; a dispatch whose group counts a shader wrote (an indirect
dispatch, which the GI uses). The second pattern is a prefix sum, and how it gives each
item its own output range in an order that does not depend on timing, where an atomic append would not. The toy is the
histogram in about 40 lines, then the scan. The approaches table compares a CPU loop, fragment-shader tricks, compute
with global atomics, compute with shared memory, and multi-pass scans.

Strata's choice: compute pipelines are made by `SceneRenderer::CreateComputePipeline`, written in the same dialect as
other shaders; compute reads textures with `SampleLevel` or `Load`, never `Sample`; every storage image states its
format; a group's shared memory stays within 32 KiB, the limit of MoltenVK. Two real shaders are named for the reader to
open later: the exposure histogram (`image/exposure`) and the culling's prefix allocation (`draw/gpu-driven`). What the
choice cannot do: Strata uses no wave operations and runs compute on the graphics queue, with no asynchronous compute.
The exercise reads the real histogram's dispatch: its group counts from the view's size, and the barrier placed before
the exposure pass reads the bins. At the end the reader can write a small compute shader, size its dispatch and say
where a barrier is needed.

**Leaves out.**

- How NVRHI tracks resource states and places barriers, and the pitfalls of one binding set → `gpu/resources-lifetimes`
- Registers, binding layouts and push constants of compute pipelines → `gpu/binding`
- The exposure histogram as exposure metering → `image/exposure`
- GPU culling and its two-pass allocation → `draw/gpu-driven`
- Light culling in compute → `light/many-lights`
- Threads, atomics and memory order on the CPU → `basics/threads`

**Fit.** `over`: about 4,150 words against M (3,000). Five ideas taught from zero, the scan, the real histogram and the
exercise pass M's top; the page takes L by S2 (4,150 is inside L's range), which also leaves room for a figure of thread
groups over an image.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:5` | concept | home | The compute model: dispatches, thread groups, group and global IDs, shared memory, group barriers, atomics, writes to UAVs and the barrier between dispatches; the outline makes this page its home. General knowledge. |
| `new:6` | concept | home | Two GPU patterns, the page's toys: a histogram with shared-memory atomics, and a prefix sum that allocates output ranges deterministically. General knowledge. |
| `new:7` | not-done | home | No asynchronous compute and no wave (subgroup) operations: compute runs on the graphics queue, although the device fetches a compute queue. Evidence: `git grep -n "CommandQueue::Compute" 822a7a46 -- Strata/src` finds nothing; `git grep -nE "Wave[A-Z][a-z]*\(" 822a7a46 -- Strata/shaders` finds nothing; the compute queue is fetched at `Strata/src/Platform/Vulkan/VulkanGraphicsDevice.cpp:939-940` (run again at the pin) |
| `render-core:96` | feature | home | `SceneRenderer::CreateComputePipeline(shader, layout)`, as Strata's way to make a compute pipeline |
| `render-core:582` | rule | home | `SampleLevel` or `Load` in compute: `Sample` needs compute derivatives, a capability devices need not have |
| `render-core:584` | rule | home | Every storage image states its format (`[vk::image_format]`), because Unknown needs a capability the checks reject |
| `render-core:46` | feature | use | MoltenVK's 32 KiB of compute shared memory, the limit a group's shared memory stays within (about 30 words; `Docs/DeveloperGuide.md:298`) |
| `render-core:702` | term | home | Barrier and resource state, met first here as the barrier between a write and a read |
| `render-core:709`, `render-core:710` | term | home | Structured buffer; UAV and storage image |
| `render-scene:625` | term | home | Prefix allocation, taught with the scan |
| `render-core:329` | concept | link | Resource states and barriers in NVRHI, linked forward |
| `render-core:350` | concept | use | Stages and entry points, applied to the compute stage |
| `render-scene:287` | concept | link | The culling's two-pass prefix allocation, as the second real example |
| `render-image:400` | code | use | `Strata/shaders/PostProcess/Histogram.comp.slang`, the real histogram (16x16 groups, group-shared bins, two `InterlockedAdd`s), shown short after the toy |
| `new:32` | hands-on | home | Exercise (predict, then run): from the real histogram's dispatch, compute its group counts for a 1920x1080 view and say why the explicit barrier is needed before the exposure pass reads the bins (NVRHI places barriers only when binding sets change), then check the counts with a breakpoint at the dispatch on the source build. Evidence: `Strata/src/Strata/Renderer/SceneRendererPost.cpp:962-972` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Threads, races and atomics in general | `basics/threads` | must |
| GPU resources in NVRHI: descs, uses, UAVs, CPU access | `gpu/vulkan-nvrhi` | must |
| Shaders, entry points and the dialect | `gpu/shaders` | must |
| How a GPU works: lanes, waves, occupancy | `gpu/how-a-gpu-frame-works` | must |
| Arrays and their cost | `basics/data-structures` | helps |
| Luminance as one number per pixel | `basics/color` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `barrier` | Barrier | resource state |
| `prefix-allocation` | Prefix allocation | - |
| `structured-buffer` | Structured buffer | - |
| `uav` | UAV | storage image |
