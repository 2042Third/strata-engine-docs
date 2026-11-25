# Brief: `gpu/how-a-gpu-frame-works`

| Field | Value |
| --- | --- |
| Title | How a GPU works and draws a frame |
| Kind | C |
| Size | L |
| Tracks | E |
| Needs | `basics/threads`, `basics/math-projection`, `basics/color`, `basics/signals`, `core/frame-loop` |
| From | render-core; retitled; + the hardware: waves, occupancy, bandwidth, branches (curricula 1.9.1 [gap]); + the pipeline at a glance, textures, sampling and filtering, buffers, command submission and frames in flight; rasterization takes pixels as samples (aliasing in general is `basics/signals`') |
| Unit | `plan/allocation/gpu.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `gpu/how-a-gpu-frame-works` — How a GPU works and draws a frame

**Covers.** The page opens on the editor's viewport with the Showcase sample: one frame, drawn about every 16 ms, and
the question what the GPU did to make it. It teaches, in this order: what a GPU is (many simple lanes with their own
memory, running one program over many pieces of data); why a program talks to it through commands that run later, and
how immediate APIs (OpenGL, Direct3D 11) and explicit APIs (Vulkan, Direct3D 12, Metal) differ in who keeps track of
that; the graphics pipeline at a glance (vertices, the vertex shader, rasterization that takes each pixel as a sample,
interpolants, the fragment shader run on quads of 2x2 pixels, which gives the derivatives that pick a mip level, the
depth test, blending into a target); textures, buffers, sampling and filtering;
the hardware that sets the cost of all this (waves, occupancy, bandwidth, branches that diverge inside a wave); queues
and command lists; frames in flight, with a timeline of two frames and the fence that keeps the CPU at most two frames
ahead of the GPU; the swap chain, the back buffer, acquire and present, vsync and the three present modes.

Strata's choices close the concept: Vulkan 1.2, two frames in flight, FIFO when vsync is on, and why the image count of
the swap chain is not the number of frames in flight. The running example is Strata's own frame, named step by step
without code. At the end the reader can explain why a draw call does not draw at once, read a CPU and GPU timeline, and
say what vsync costs and what it buys. The exercise predicts how many frames the CPU records before it first waits for
the GPU, then checks it on the source build at the frame-pacing wait.

**Leaves out.**

- How Strata opens the device, the swap chain's code and where the acquire wait is submitted → `gpu/vulkan-nvrhi`
- Shader stages, entry points and Strata's shading language → `gpu/shaders`
- Compute shaders, thread groups and shared memory → `gpu/compute`
- Clip space, depth conventions and reversed Z in Strata → `gpu/coordinates`
- Mip levels, color spaces and block compression of textures → `assets/textures`
- Aliasing and filtering as signal theory → `basics/signals`
- The passes of Strata's frame, one by one → `gpu/frame-tour`
- The HDR target and why the back buffer is UNORM → `gpu/frame-tour`
- Frame pacing on the CPU side (the frame pacer, frame-rate caps) → `core/frame-loop`

**Fit.** `fits`: about 4,950 words against L (5,000). Eight short concepts for a reader with no graphics, three figures
and Strata's choices take the most words; the HDR display transform stays with `gpu/frame-tour`.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-core:286` | concept | home | What a GPU is and why an engine talks to it through commands; immediate and explicit APIs; the mistake "`draw()` draws now" |
| `render-core:309` | concept | home | The swap chain, presentation and vsync: FIFO, MAILBOX, IMMEDIATE; Strata's choice in one paragraph; the mistake of equating the image count with frames in flight |
| `render-core:314` | concept | home | Frames in flight and CPU and GPU pacing: two by default, a fence per frame; the mistake of rewriting what the GPU still reads |
| `new:1` | concept | home | The graphics pipeline at a glance: vertex shading, rasterization (pixels as samples), interpolation, fragment shading, the depth test, blending; the outline's From column asks for it. General knowledge. |
| `new:2` | concept | home | Textures, buffers, sampling and filtering at a glance: texels, point, bilinear, trilinear and anisotropic filtering, mips named only. General knowledge. |
| `new:3` | concept | home | The GPU's hardware: waves, occupancy, memory bandwidth, branches that diverge; curricula 1.9.1 marks it a gap. General knowledge. |
| `new:4` | figure | home | A diagram of the graphics pipeline from vertices to the target, with what each stage reads and writes. General knowledge. |
| `render-core:487` | figure | home | The CPU and GPU timeline with two frames in flight; the wait in `BeginFrame` named, the acquire and present points marked, their details linked to `gpu/vulkan-nvrhi` |
| `render-core:524` | figure | home | The opening picture: the editor's viewport with Showcase at default settings, "what the frame produces" |
| `render-core:679`, `render-core:680` | term | home | GPU; graphics API |
| `render-core:688` | term | home | Queue and queue family |
| `render-core:692` | term | home | Swapchain |
| `render-core:694`, `render-core:695`, `render-core:696` | term | home | Present mode; back buffer; acquire and present |
| `foundation:581` | term | home | Present, as the core part words it; one entry with `render-core:696` (the term; the `Present` stage of the frame profiler is `gpu/upload-queue`'s) |
| `render-core:698`, `render-core:699`, `render-core:700` | term | home | Fence and event query; frames in flight; command list |
| `editor-ui:788` | term | home | Frames in flight, as the editor's UI words it; one entry with `render-core:699` |
| `editor-ui:787` | term | home | Event query, as the editor's UI words it: NVRHI's fence, the one Strata polls; one entry with `render-core:698`, which this page defines. `gpu/resources-lifetimes` uses it as the "done" signal of every lifetime (`render-core:346`) |
| `render-core:718` | term | home | Shader (vertex, fragment, compute), as the pipeline names them |
| `render-core:725` | term | home | Interpolant |
| `render-image:727` | term | home | Uniform branch, beside the branch that diverges inside a wave |
| `new:25` | hands-on | home | Exercise (predict, then run): predict how many frames the CPU records before it first waits for the GPU, then check it on the source build with a log line at the frame-pacing wait of `VulkanGraphicsDevice::BeginFrame` (two frames in flight by default). Evidence: `Strata/src/Platform/Vulkan/VulkanGraphicsDevice.cpp:1444-1453`; `Strata/src/Strata/Renderer/GraphicsDevice.h:28` |
| `render-core:35` | feature | link | Strata's frame pacing, in one sentence: `BeginFrame` waits for the oldest frame while two are outstanding |
| `foundation:234` | concept | link | Frame pacing and vsync on the CPU side, one sentence and a link |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| How a computer runs a program: CPU, memory, caches | `basics/computer` | must |
| Threads in general, and that two processors work at the same time | `basics/threads` | must |
| Sampling, aliasing and filtering | `basics/signals` | must |
| The frame loop: one frame after another on the main thread | `core/frame-loop` | must |
| The frame map for people: frame time in milliseconds, the CPU preparing one frame while the GPU draws the one before | `start/what-an-engine-is` | helps |
| Projection: view and projection matrices, depth | `basics/math-projection` | helps |
| Color: linear and sRGB values | `basics/color` | helps |
| Bytes and their sizes (bandwidth in GB/s) | `basics/numbers` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `acquire` | Acquire | - |
| `back-buffer` | Back buffer | - |
| `command-list` | Command list | command buffer |
| `fence` | Fence | event query |
| `frames-in-flight` | Frames in flight | - |
| `graphics-api` | Graphics API | - |
| `interpolant` | Interpolant | - |
| `present` | present | - |
| `present-mode` | Present mode | - |
| `queue-family` | queue family | - |
| `swapchain` | Swapchain | - |
| `uniform-branch` | Uniform branch | - |
