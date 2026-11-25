# Allocation: gpu

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

## `gpu/vulkan-nvrhi` — Vulkan, NVRHI, the graphics device and the Renderer's services

**Covers.** The job: how Strata opens a GPU, keeps it busy frame after frame and offers every renderer the same
services. The problem and the approaches (one backend per API, a third-party RHI, one API with a translation layer),
and Strata's choice: NVRHI over Vulkan only, MoltenVK on macOS, Vulkan headers only in `Platform/Vulkan`. The map:
`Application` → `GraphicsModule` → `GraphicsDevice` → `VulkanGraphicsDevice` → NVRHI → Vulkan → the driver or MoltenVK,
with `Renderer` beside it and `VulkanPresentation` from `Platform/GLFW`. Then the device, in the order it is made:
instance, physical and logical device, queues and their families; the `GraphicsDevice` interface as the contract; the
loader, the instance with the validation layer when asked, and what validation is (what the layer checks and why an
explicit API needs it, why it is off outside Debug, how each message is classified and every error counted, NVRHI's own
errors among them); device selection with its requirements (each with its reason) and its score, and that no program
chooses the GPU; wrapping the device into NVRHI with `vk::SystemError` caught, Dist without NVRHI's validation; MoltenVK
and the rule to gate on device features. The swap chain: a UNORM format because the engine encodes sRGB itself, the
present mode from vsync, the image count, recreation, no swap chain while minimized. The device's frame: pacing by event
queries, acquire with retry, the acquire wait submitted only at the back buffer's first use, present through an empty
submission, device loss. NVRHI's command lists: open, close, execute, and immediate lists, all recorded on the main
thread. Beside them, GPU resources in NVRHI: textures, buffers and staging resources made from a desc (size, format,
mips, array layers, dimension), their uses (shader resource, render target, depth, UAV), CPU access (none for device
memory, Write for upload staging, Read for readback), the initial state kept, debug names, subresources, framebuffers
and a draw's graphics state, quoted from `SceneRenderer::CreateRenderTarget` and the staging pool's desc.

The second section is the Renderer's side: the Graphics engine module (which programs run it, validation on in Debug,
start failure advice, `Skip` and `Close`, back-buffer captures), the `Renderer` hub (its services in their destruction
order, the four samplers, the fallback textures with the flat normal's exact half floats, `Renderer::BeginFrame`'s order,
the frame number) and `RegisterRendererModule`. The toy is a 60-line device wrapper; the real code follows it. Tests,
alternatives and changing it safely close the page; the exercise traces the device's choice of GPU on the reader's
machine.

**Leaves out.**

- Turning on validation, reading its messages and the error count → `gpu/debugging`
- `Renderer::PrepareBackBuffer` and why uploads run before the display wait → `gpu/upload-queue`
- Resource lifetimes, deferred release and the NVRHI pitfalls → `gpu/resources-lifetimes`
- The bindless table, its sizing and binding layouts → `gpu/binding`
- GPU timestamps and the timestamp pool → `gpu/readback-timing`
- Queue ownership transfers for the transfer queue → `gpu/upload-queue`
- Engine modules in general, their order and their failures → `core/engine-modules`
- The layer table and `ExternalOwners` → `core/layers-registries`
- The `Renderer.Quality` section and its rows → `image/quality-settings`

**Fit.** `fits`: about 9,200 words against XL (8,000). Ten code excerpts, the device's frame and the GPU resources of
NVRHI take the most words; in its two sections, the device and the Renderer's services, the page has about 800 words of
room below XL's top.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-core:291` | concept | home | Graphics APIs and RHIs: per-API backends, a third-party RHI, one API plus translation; why NVRHI on Vulkan; the mistake "NVRHI makes Vulkan safe" |
| `render-core:298` | concept | home | Instance, physical device, logical device, queues: the feature floor, the score, dedicated compute and transfer families |
| `render-core:304` | concept | home | Validation layers and error counting: what the layer checks and why explicit APIs need it, the Khronos layer and NVRHI's validation in Debug, why both are off in the other builds, every error counted and known false reports classified, not hidden; the mistake of ignoring warnings because "it renders" (moved from `gpu/debugging`, R31 D25; about 250 words) |
| `render-core:41` | feature | home | How messages are classified: errors counted, warnings logged, known false reports demoted (MoltenVK's blending report, the bindless support query, the loader's layer search); `book.md`'s row gives how errors are counted to this page |
| `render-core:42` | feature | home | NVRHI's errors logged and counted into the error count that tests require to be zero |
| `render-core:320` | concept | home | Acquire, render, present, and where the display wait is placed (the device's side; the Renderer's call is `gpu/upload-queue`'s) |
| `render-core:325` | concept | home | Command lists: recording against execution, NVRHI's `open`, `close`, `executeCommandList`, immediate lists |
| `new:26` | concept | home | GPU resources in NVRHI, beside command lists: a texture, buffer or staging resource made from a desc (size, format, mips, array layers, dimension); its uses (shader resource, render target, depth, UAV); CPU access (none for device memory, Write for upload staging, Read for readback); the initial state kept with `keepInitialState`; debug names; subresources; framebuffers; a draw's graphics state (pipeline, framebuffer, viewport, bindings). The pages after it assume it (about 700 words with `new:27`). Evidence: `Strata/src/Strata/Renderer/SceneRenderer.cpp:213-224`; `Strata/src/Strata/Renderer/StagingPool.cpp:52-60`; `Strata/src/Strata/Renderer/TextureReadback.cpp:51`; `Strata/src/Strata/Renderer/BufferReadback.cpp:17`; `StrataTests/src/Renderer/GPURendererTests.cpp:137-160` |
| `new:27` | code | home | `Strata/src/Strata/Renderer/SceneRenderer.cpp:213-224`: `SceneRenderer::CreateRenderTarget`, a texture desc with its use, initial state and debug name, shown with the staging buffer's desc of `Strata/src/Strata/Renderer/StagingPool.cpp:52-60` (CPU access Write, kept in `CopySource`) |
| `render-core:28`, `render-core:29`, `render-core:30` | feature | home | The `GraphicsDevice` interface, its specification (frames in flight 1 to 4, default 2) and the capabilities it queries |
| `render-core:31`, `render-core:32` | feature | home | `VulkanGraphicsDevice` and device selection: requirements and score |
| `new:28` | not-done | home | No choice of GPU: no program sets the device's adapter index, so the device's score picks (a discrete GPU first, then the most memory), and the log names each GPU it skips, with the reason (about 60 words). Evidence: `Strata/src/Strata/Renderer/GraphicsDevice.h:29`; `Strata/src/Platform/Vulkan/VulkanGraphicsDevice.cpp:632, 637-640, 744-750`; `git grep -n AdapterIndex 822a7a46 -- Strata/src StrataEditor/src StrataRuntime/src StrataTests/src` finds only these two files (run again at the pin) |
| `render-core:33`, `render-core:34`, `render-core:35`, `render-core:36`, `render-core:37` | feature | home | The swap chain, the deferred acquire wait, frame pacing, present, device lost |
| `render-core:38`, `render-core:39` | feature | home | The `VulkanPresentation` seam and `VulkanLoader` |
| `foundation:84` | feature | home | The same seam seen from the window's side: `Platform/GLFW` gives presentation, so the renderer never includes GLFW |
| `foundation:70` | feature | home | Where the device is made, from `GraphicsModule::OnInit` to `CreateLogicalDevice`: the same path as `render-core:52` and `render-core:31` |
| `render-core:43` | feature | home | The memory budget per device-local heap (what `assets/residency` reads) |
| `render-core:46` | feature | home | MoltenVK's specifics, as the reason for gating on device features |
| `render-core:52`, `render-core:53`, `render-core:54` | feature | home | `GraphicsModule`, back-buffer capture, which programs run the module (editor windowed, headless or `--no-gpu`; runtime without Graphics when headless) |
| `render-core:61`, `render-core:62`, `render-core:63`, `render-core:64`, `render-core:67` | feature | home | The `Renderer` hub, samplers, fallback textures, `Renderer::BeginFrame`'s order described or quoted from `Strata/src/Strata/Renderer/Renderer.cpp:267-282` (`gpu/upload-queue` uses it and quotes only `PrepareBackBuffer`), the frame number |
| `render-core:73` | feature | home | NVRHI command lists, immediate by default; non-immediate lists named, their rule linked to `gpu/resources-lifetimes` |
| `new:29` | not-done | home | No command lists recorded on several threads: the main thread records and submits every command list, and the renderer's jobs do CPU work only (extraction, the cascades' and local shadows' caster queries, poses, staging copies); one sentence in the command-list section, linking `core/jobs` (about 80 words). Evidence: `Docs/Architecture.md:1383-1384`; `git grep -n -e ParallelFor -e "JobSystem::Submit" 822a7a46 -- Strata/src/Strata/Renderer` finds only `GPUUploadQueue.cpp:531`, `RenderScene.cpp:1409`, `SceneRendererExtraction.cpp:117, 538` and `SceneRendererLocalShadows.cpp:578` (run again at the pin) |
| `render-core:245`, `render-core:246`, `render-core:247` | feature | home | `RegisterRendererModule`, the asset types Texture, Mesh and Font, and the components it registers (`TextComponent`, `MeshRendererComponent`) |
| `render-core:443` | code | home | `Strata/src/Strata/Renderer/GraphicsDevice.h:128-199`: what a device must offer, with no Vulkan header in sight |
| `render-core:444` | code | home | `Strata/src/Platform/Vulkan/VulkanGraphicsDevice.cpp:659-713`: the required features, each with its reason, and the rejection log |
| `render-core:445` | code | home | `Strata/src/Platform/Vulkan/VulkanGraphicsDevice.cpp:745-749`: the adapter score (discrete, integrated, memory as the tiebreak) |
| `render-core:449` | code | home | `Strata/src/Platform/Vulkan/VulkanGraphicsDevice.cpp:948-990`: NVRHI wraps the device; exceptions caught at the call site; no NVRHI validation in Dist |
| `render-core:446` | code | home | `Strata/src/Platform/Vulkan/VulkanGraphicsDevice.cpp:1130-1168`: the UNORM format, the present mode by vsync, the image count |
| `render-core:447` | code | home | `Strata/src/Platform/Vulkan/VulkanGraphicsDevice.cpp:1438-1513`: `BeginFrame`: pacing by event queries, minimized windows, recreation, acquire with retry |
| `render-core:448` | code | home | `Strata/src/Platform/Vulkan/VulkanGraphicsDevice.cpp:1515-1605`: `SubmitPendingAcquireWait` with ALL_COMMANDS, the device's `PrepareBackBuffer`, `EndFrame` presenting through an empty submission |
| `render-core:450` | code | home | `Strata/src/Strata/Renderer/GraphicsModule.cpp:26-77`: an engine module that owns the GPU: device, swap chain, `Renderer::Init`, failure advice, `Skip` and `Close` |
| `render-core:451` | code | home | `Strata/src/Strata/Renderer/Renderer.cpp:84-168`: the hub's start: samplers, fallback textures in one command list, the flat normal's half floats (107-111), reserved bindless slots, the order of subsystems |
| `render-core:484` | figure | home | The layer and ownership map, with the folders that may include Vulkan headers |
| `render-core:490` | figure | home | The swap chain's state machine: none while minimized, created, acquired, prepared, presented, recreated, device lost |
| `render-core:606` | rule | home | Gate on device features, never on the OS |
| `render-core:618` | rule | home | Exceptions from NVRHI and vulkan.hpp are caught at the call site |
| `render-core:681`, `render-core:682`, `render-core:683`, `render-core:685` | term | home | Vulkan; MoltenVK; NVRHI; RHI |
| `build-test:647` | term | home | MoltenVK, as the build's glossary words it; one entry with `render-core:682` |
| `editor-ui:791` | term | home | NVRHI, as the editor's UI words it; one entry with `render-core:683` |
| `render-core:686`, `render-core:687` | term | home | Instance; physical and logical device |
| `render-core:691` | term | home | Validation layer, defined with `render-core:304` (moved from `gpu/debugging`, R43) |
| `build-test:668` | term | home | Validation layer, as the build's glossary words it; one entry with `render-core:691` (moved from `gpu/debugging` with it) |
| `render-core:693`, `render-core:697` | term | home | Surface; semaphore |
| `render-core:701` | term | home | Immediate command list |
| `render-core:756` | term | home | UNORM and sRGB formats, with the swap chain's choice |
| `render-core:775` | term | home | Device lost |
| `new:30` | hands-on | home | Exercise ("trace it yourself"): the device's choice of GPU on the reader's machine: a breakpoint in the selection loop of `VulkanGraphicsDevice`, each GPU's score read, and the log's "skipped" lines matched to the requirement each GPU failed. Evidence: `Strata/src/Platform/Vulkan/VulkanGraphicsDevice.cpp:628-640, 744-750` |
| `foundation:65` | feature | use | The `EngineModule` interface the Graphics module implements |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| How a GPU works and draws a frame: commands, queues, frames in flight, the swap chain | `gpu/how-a-gpu-frame-works` | must |
| Engine services and engine modules (`OnBeginFrame`, `OnEndFrame`, start failures) | `core/engine-modules` | must |
| The layer table and `ExternalOwners` | `core/layers-registries` | must |
| Talking to the operating system: seams per platform, console and GUI programs | `core/platform` | must |
| C++ interfaces and virtual calls | `basics/cpp-classes` | must |
| Smart pointers and reference counting | `basics/cpp-memory` | must |
| Floating point, half floats and their exact values | `basics/numbers` | helps |
| Errors, asserts and logging in engine code (`ST_CORE_VERIFY`, errors returned) | `core/conventions` | helps |
| The frame loop | `core/frame-loop` | helps |

## `gpu/shaders` — Shaders: Slang, the build and the dialect

**Covers.** The job: how a shader goes from a `.slang` file to a shader object at run time, and the rules that keep its
source portable. The problem and the approaches (GLSL to SPIR-V, HLSL through DXC, Slang; compiled while the game runs
or when the engine is built), then Strata's choice and its reasons: HLSL-syntax Slang, compiled at build time by a
pinned slangc to SPIR-V 1.5, checked, and embedded in the program as arrays, so no game ships a compiler and every
configuration runs the same bytes. The map is the build's diagram, from the source and its includes to
`ShaderLibrary::Get`. Then, in the order a writer meets them: stages, entry points, inputs, outputs and system values
(every entry is `main`, the stage comes from the registered name's suffix, the converted shaders fill `st_*` globals in
an entry wrapper); the source tree; registering a shader in `strata_add_shaders`, variants, and why configure runs again;
the slangc flags with their reasons (register shifts, column-major matrices, stated image formats, two warnings
switched off) and the flags not passed; `Include/Common.slang` and its one `__target_switch`.

The dialect comes next, each rule with the bug it prevents: `mul` only with a matrix, comparisons through `all()` and
`any()`, matrix constructors that take rows, `select`'s order, `SV_VulkanInstanceID`, derivatives before the first
`discard`, nothing target-specific outside `Common.slang`. The real case is told here: a `mul` of two vectors collapsed
a shadow filter and passed every GPU test. Then the checks that guard the dialect (`Architecture.Shaders`,
`Renderer.ShaderModules`, `Renderer.ShaderTool`, the GPU suite, CI's HLSL target, `spirv-val`, the Metal conversion),
how a conversion slip is found with the look-dev compare, and what a Direct3D target would still need. The toy is a
fullscreen gradient shader with its one CMake line; loading it is the last excerpt. The exercise traces a registered
name to the bytes `ShaderLibrary` returns.

**Leaves out.**

- The CMake custom commands, StrataShaderTool's SPIR-V patch and the generated registry → `engineering/generated-code`
- Slang's pinned download and its cache → `engineering/third-party`
- The CI's shader steps → `engineering/ci`
- Registers, binding layouts and push constants → `gpu/binding`
- Compute shaders, `SampleLevel` in compute and storage image formats → `gpu/compute`
- The invariant position decoration and why the prepass needs it → `gpu/frame-tour`
- `SanitizeHDR`, which the first pass that writes HDR values calls → `light/brdf`
- The look-dev harness itself → `engineering/look-dev`
- Writing a pixel test that catches a dialect slip → `gpu/first-triangle`

**Fit.** `fits`: about 5,950 words against L (5,000). The dialect with its real bug, four excerpts and the checks that
guard the dialect take the most words; the build's internals stay with `engineering/generated-code`.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-core:354` | concept | home | Shading languages and offline compilation; why build time and embedding; the mistake of adding a file without listing it |
| `render-core:350` | concept | home | Stages, entry points, inputs and outputs, system values; `main` and the suffix; the `SV_InstanceID` mistake named, its rule linked to `draw/batching` |
| `render-core:360` | concept | home | HLSL against GLSL: `mul`, `*`, row constructors, `select` against `mix`, vector comparisons, `Sample` in compute; the real bug |
| `render-core:119`, `render-core:120` | feature | home | The shader source tree, its file counts given by a generated value, never typed (40 files in `Include/` at the pin, `GeometryTables.slang` among them; the inventory's 39 is a slip); the entry list in `strata_add_shaders` with variants and `INVARIANT_POSITION` |
| `render-core:122` | feature | home | slangc's flags and the reason for each, and the flags not passed |
| `render-core:125`, `render-core:126` | feature | home | `EmbeddedShaders` and `ShaderLibrary`; `Include/Common.slang` |
| `render-core:128`, `render-core:129` | feature | home | The dialect's rules; the checks that guard them |
| `render-core:130`, `render-core:131` | feature | home | Finding a conversion slip with a signed compare against 0.7.0's look-dev set; what other targets would need |
| `render-core:143` | feature | home | Column-major matrices: glm's bytes, `floatNxN(...)` takes rows, `mul(M, v)` |
| `render-core:457` | code | home | `Strata/src/Strata/Renderer/ShaderLibrary.cpp:47-87`: lookup by registered name, the stage from the suffix, the thread-safe cache (with `Strata/src/Strata/Renderer/EmbeddedShaders.h`) |
| `render-core:458` | code | home | `CMake/StrataShaders.cmake:64-86`: the flags with their reasons; the custom commands later in the file are `engineering/generated-code`'s |
| `render-core:459` | code | home | `Strata/shaders/Include/Common.slang:4-46`: the register convention, `NDCToUV`, the sRGB transfer; `SanitizeHDR`, the next lines of the file (48-57), is named in one sentence with a link to `light/brdf`, its home |
| `render-core:460` | code | home | `Strata/shaders/Include/Common.slang:194-215`: the only `__target_switch` and `spirv_asm`, and why `PackHalf2x16` is wrapped |
| `render-core:502` | figure | home | The shader build: source and includes, slangc, `.raw.spv`, StrataShaderTool, `.spv` and `.h`, the registry, `ShaderLibrary::Get`; the variants' fan-out |
| `render-core:576` | rule | home | Every shader entry is listed in `strata_add_shaders`; re-run configure |
| `render-core:578`, `render-core:580` | rule | home | `mul` only with a matrix; comparisons, constructors and `select` |
| `render-core:587` | rule | home | Derivatives before the first `discard` |
| `render-core:590` | rule | home | `__target_switch` and `spirv_asm` only in `Include/Common.slang`; no generics, modules or interfaces |
| `render-core:719`, `render-core:720`, `render-core:721`, `render-core:722`, `render-core:723` | term | home | Entry point; SPIR-V; Slang and slangc; HLSL and GLSL; shader variant |
| `render-core:726`, `render-core:727` | term | home | Derivative; discard |
| `render-core:121`, `render-core:124` | feature | link | The build's custom commands and StrataShaderTool, one sentence each |
| `render-core:123` | feature | link | The Slang pin, one sentence |
| `render-core:603` | rule | link | `SanitizeHDR` appears in `Common.slang`; its rule is taught where the first HDR writer calls it |
| `build-test:78` | feature | home | The same flags, from the build's side: the same subject as `render-core:122` and its excerpt `render-core:458`, taught once with them |
| `build-test:80` | feature | home | `EmbeddedShaders::GetAll` and `Find`, the run-time lookup in the embedded registry, taught with `ShaderLibrary` (`render-core:125`) |
| `build-test:171` | feature | home | `StrataShaders.TargetHLSL`: `slangc -target hlsl` over every entry, with no label so every CI job that runs the tests runs it; one of the dialect's checks (`render-core:129`) and a first step of what a Direct3D target would need (`render-core:131`) |
| `build-test:185` | feature | home | `Architecture.Shaders` (derivatives before the first `discard`, Slang only, HLSL syntax), one of the checks that guard the dialect (`render-core:129`) |
| `build-test:480` | rule | home | "Shaders are listed, not globbed", from the build's side: the same rule as `render-core:576`, taught once with it |
| `build-test:644`, `build-test:645` | term | home | Slang and slangc; SPIR-V, as the build's glossary words them; one entry each with `render-core:721` and `render-core:720`; SPIR-V's word layout is linked to `engineering/generated-code` |
| `new:31` | hands-on | home | Exercise ("trace it yourself"): `PostProcess/Fullscreen.vert` from its line in `strata_add_shaders` to the bytes `ShaderLibrary::Get` returns: a breakpoint in `Get`, the step into `EmbeddedShaders::Find`, the stage read from the name's suffix, and the generated header found in the reader's own build directory. Evidence: `Strata/CMakeLists.txt:136`; `Strata/src/Strata/Renderer/ShaderLibrary.cpp:29, 47, 60` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| How a C++ program is built: compiling, linking, CMake, configure and build | `basics/build` | must |
| The short source build and one test case | `core/first-change` | must |
| The pipeline at a glance: vertex and fragment shaders, interpolants | `gpu/how-a-gpu-frame-works` | must |
| NVRHI's device and shader objects | `gpu/vulkan-nvrhi` | must |
| Matrices and matrix order | `basics/math-matrices` | must |
| Floating point and half floats | `basics/numbers` | helps |
| The sRGB transfer function | `basics/color` | helps |
| The look-dev harness (captures and signed compares) | `engineering/look-dev` | helps |

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

## `gpu/coordinates` — Coordinate systems and the camera: clip space, reversed depth, UVs

**Covers.** The problem as a reader meets it: a cube placed in the editor lands on some pixels at some depth; which
ones, and what happens when a textbook's OpenGL formulas are used (an image upside down, far surfaces that fight). The
idea is the chain of spaces in one figure: object, world (right-handed, +Y up, −Z forward), camera, clip, NDC,
framebuffer and UVs, and the way back from a pixel and its depth to a position through the inverse projection.
Strata's conventions follow, each with its reason (the words clip space, NDC and reversed Z are taught on
`basics/math-projection` and linked): Direct3D-style NDC through NVRHI's viewport flip
(+Y up, row 0 at the top, depth from 0 to 1), and why slangc is not asked to flip; fullscreen UVs and the fullscreen
triangle made from the vertex index; depth and reversed Z, with the precision argument shown as a plot computed from the
projection formulas, depth cleared to 0, tests with `GreaterOrEqual`, the sky at depth 0 and the infinite far plane;
front faces counter-clockwise as glTF has them, with mirrored instances named and linked forward.

The camera closes the concept: `CameraComponent`'s projection, field of view, near and far planes, orthographic size,
Primary and clear color, and `GetProjection`, which builds the reversed-Z matrices and guards bad values; then
`SceneCamera`, what every renderer is given (view, projection in Strata's clip space, position, near, far, the field of
view used for levels of detail, orthographic, clear color, `FromEntity`), kept apart from the lens because it is the
shadow cascades' cache key, and why a clear color shows changed: it is linearized into the HDR image, so exposure and
tone mapping apply to it. The approaches
table compares standard depth, reversed Z with float depth, the infinite far plane and logarithmic depth. What Strata's
choice cannot do here, and two exercises: derive the fullscreen triangle by hand, and measure the float depth step from
0.1 m to 10 km for both mappings.

**Leaves out.**

- The mathematics of projection and homogeneous coordinates → `basics/math-projection`
- The code of `PerspectiveReverseZ*` and `Ray::FromNDC` → `core/math`
- Mirrored transforms, clockwise pipelines and flipped tangents → `draw/mirrors-camera-relative`
- Camera-relative rendering and float precision far from the origin → `draw/mirrors-camera-relative`
- The lookup of the primary camera → `world/scene-graph`
- The camera's depth-of-field fields → `image/depth-of-field`
- The projection's jitter for TAA → `image/taa`
- The editor camera and its viewport → `editor/camera-viewport`

**Fit.** `over`: about 4,750 words against M (3,000). Six conventions with the precision plot, the camera with
`SceneCamera` and the two exercises pass M's top; the page takes L by S2 (4,750 is inside L's range), and the fullscreen
triangle stays here.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-core:378` | concept | home | Coordinate systems and clip space; Vulkan's +Y down against Direct3D's +Y up; the mistake of GLSL's UV formula |
| `render-core:382` | concept | home | Depth buffers and reversed Z; the approaches; the mistake of clearing to 1 or testing `Less` |
| `render-core:137`, `render-core:138`, `render-core:139` | feature | home | Direct3D-style clip space through NVRHI; reversed Z in Strata; fullscreen UVs |
| `render-core:140` | feature | home | Front faces counter-clockwise (glTF); `setFrontCounterClockwise(!Mirrored)` named, mirroring linked |
| `render-core:141` | feature | home | Right-handed, +Y up, −Z forward |
| `foundation:139` | feature | home | The same conventions as the math code states them (`Math/Math.h`), with Direct3D-style clip space and reversed Z |
| `render-core:464` | code | home | `Strata/shaders/PostProcess/Fullscreen.vert.slang:8-13`: one triangle from the vertex index; the exercise derives its three vertices |
| `new:8` | code | home | `Strata/src/Strata/Scene/Components.cpp:7-24`: `CameraComponent::GetProjection`: the aspect ratio, near and far guarded, `PerspectiveReverseZ` and `OrthographicReverseZ` |
| `render-core:505` | figure | home | The chain of spaces, from object to framebuffer and UVs |
| `foundation:426` | figure | home | The conventions' figure (axes, NDC, depth, the framebuffer's origin), drawn as the start and end of the chain above |
| `render-core:507` | figure | home | The reversed-Z precision plot, computed from the projection formulas |
| `render-core:597` | rule | home | Reversed Z: clear depth to 0, test `GreaterOrEqual`, the sky at depth 0 |
| `render-core:602` | rule | home | Fullscreen UVs `(ndc.x * 0.5 + 0.5, 0.5 - ndc.y * 0.5)` |
| `render-core:636`, `render-core:638` | hands-on | home | Derive the fullscreen triangle; the reversed-Z precision experiment (CPU only) |
| `render-core:729`, `render-core:731`, `render-core:732` | term | home | Viewport flip; infinite far plane; depth test functions |
| `foundation:635` | term | home | Infinite far plane, as the core part words it; one entry with `render-core:731` (R31 D33) |
| `render-core:728`, `render-core:730` | term | link | Clip space and NDC; reversed Z: homed on `basics/math-projection` (the mathematics); this page keeps Strata's convention and the precision argument |
| `render-image:724` | term | home | Fullscreen triangle: one oversize triangle that covers the viewport, made from the vertex index (`render-core:464`); "post source" (`render-image:723`) stays with `image/why-post` |
| `render-core:736` | term | home | Winding order, front face and back-face culling |
| `render-scene:644` | term | home | Winding and front face, as the drawing part words it |
| `editor-core:695` | term | home | Primary camera |
| `render-indirect:609` | term | home | Depth buffer, as the indirect part words it; reversed Z in it linked to `basics/math-projection` |
| `editor-core:733`, `render-direct:716`, `render-scene:608` | term | link | Reversed Z, as other parts' glossaries word it; one entry with `render-core:730` on `basics/math-projection` |
| `scene-ecs:58` | feature | home | `CameraComponent`: projection, field of view, near and far, orthographic size, Primary, clear color and `GetProjection`; its inactive reasons named; the depth-of-field fields and the primary-camera lookup linked |
| `new:33` | feature | home | `SceneCamera`, what every renderer is given (`Render(scene, camera, ...)`): view, projection in Strata's clip space, position, near, far, a vertical field of view for levels of detail, orthographic, clear color, and `FromEntity`; it stays apart from `CameraLens` because its whole value is the shadow cascades' cache key. The clear color rule: it is linearized into the HDR image, pre-exposed, so exposure and tone mapping change it (about 150 words). Evidence: `Strata/src/Strata/Renderer/SceneRenderer.h:62-81, 83-84, 851`; `Strata/src/Strata/Renderer/SceneRenderer.cpp:187-211, 3423-3425` |
| `scene-ecs:474` | figure | use | The Inspector of a Camera, beside the fields it shows |
| `foundation:424` | figure | home | The same precision plot, drawn once with `render-core:507` |
| `foundation:632` | term | home | Right-handed coordinates, +Y up, −Z forward |
| `foundation:370` | code | link | The reversed-Z projections in `Math.cpp`, quoted by `core/math` |
| `render-core:387` | concept | link | Winding and mirrored transforms, linked forward |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Projection: view and projection matrices, homogeneous coordinates, frustums, depth and reversed Z (the mathematics) | `basics/math-projection` | must |
| Matrices, transforms and spaces; axes and handedness | `basics/math-matrices` | must |
| Floating point and its precision | `basics/numbers` | must |
| Strata's math code: `PerspectiveReverseZ*` | `core/math` | must |
| The pipeline at a glance: rasterization, the depth test, the framebuffer | `gpu/how-a-gpu-frame-works` | must |
| Components and the transform | `world/scene-graph` | helps |
| A vertex shader and its system values (`SV_VulkanVertexID`) | `gpu/shaders` | helps |

## `gpu/first-triangle` — Tutorial: your first triangle in Strata

**Covers.** What you will make: a GPU test that draws one triangle without a vertex buffer, reads its pixels back and
proves Strata's clip-space convention; then a shader of your own, registered, drawn and tested. What you need: the
source build of `core/first-change`, a terminal, about two hours. The step sections, each ending in a checkpoint of the
patch: "Run the triangle test" (`StrataTests --test-case="Triangle rendering follows*"`, the passing line as a text
capture); "Read what the test does" (the shader's three positions and `SV_VulkanVertexID`, a 64x64 target, a pipeline,
a command list, the clear, `draw` of three vertices, `Renderer::ReadTexture`, the two pixels, the error count; the
shared `GPUContext` and why a run has one device); "Break the convention on purpose" (move the triangle to the bottom
half, build, watch the expectation fail with its pixel values, restore it; a shader edit needs a build, not a
configure); "Add a shader of your own" (`Debug/Checker.frag`, its line in `strata_add_shaders`, configure again,
`ShaderLibrary::Get`); "Draw it and test it" (with `PostProcess/Fullscreen.vert` into an offscreen target, pixels checked
in a new `GPU.*` test that ends with `CHECK(gpu.GetNewErrorCount() == 0)`).

This page is the home of writing a GPU test: one shared device, validation on unless `STRATA_TEST_GPU_VALIDATION` is
`0`, the error count at the end, pixels read back with the blocking call that only tests and tools may use. The
exercise, with a worked solution, breaks a `mul` in a copy of a shader, sees that it compiles, and writes the pixel test
that catches it. A hint after it names the engine's second technique: a shader function tested against its C++ twin by a
small diagnostic compute shader (`Debug/BlueNoise.comp`, `Debug/LODSelection.comp`, `Debug/ShadowViewStats.comp`).

**Leaves out.**

- The GPU suites → `engineering/test-kinds`
- Exact-pixel specifications (`ExactSpecification`) and `AddNeutralPostProcess` → `image/tutorial-post-effect`
- Reading validation messages and capturing a frame → `gpu/debugging`
- Pipeline state objects and binding layouts in full → `gpu/binding`
- Non-blocking readback in a frame → `gpu/readback-timing`
- Writing a test from zero with doctest → `core/first-change`

**Fit.** `fits`: about 4,100 words against L (5,000). Five sections of one to three steps, four excerpts quoted from the
patch and the exercise with its solution and hint take the most words.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-core:442` | code | home | `Strata/shaders/Debug/ColorTriangle.vert.slang:1-35`, with its test `StrataTests/src/Renderer/GPURendererTests.cpp:131-172`: the smallest complete GPU program, and the convention proved by two pixels |
| `new:9` | code | home | `StrataTests/src/Renderer/GPUTestUtils.h:16-48`: `GPUContext`: one device per run, validation unless the variable is `0`, `GetNewErrorCount`, `ExecuteAndWait` |
| `new:10` | figure | home | The test's 64x64 image as a diagram: the top half red, the bottom half the blue clear, the two pixels the test reads marked. Evidence: `StrataTests/src/Renderer/GPURendererTests.cpp:137, 152, 167-170` |
| `render-core:607` | rule | home | GPU tests share one device and end with zero new errors: repeated `VkInstance` creation crashed drivers under load |
| `render-core:627` | hands-on | home | Read the triangle test, move the triangle to the bottom half, watch the test fail |
| `render-core:630` | hands-on | home | Add a debug shader entry, draw it with the fullscreen vertex shader, test its pixels |
| `render-core:634` | hands-on | home | Break and observe a dialect trap, as the exercise |
| `render-core:66` | feature | use | `Renderer::ReadTexture`, the blocking readback for tests |
| `render-core:120`, `render-core:125` | feature | use | Registering the new entry; loading it through `ShaderLibrary` |
| `render-core:139` | feature | use | Fullscreen UVs, for the checker |
| `build-test:125` | feature | home | The GPU test context from the test program's side: one headless device per process, validation unless `STRATA_TEST_GPU_VALIDATION` is `0`, `GetNewErrorCount`, `ExecuteAndWait`, `ShutdownShared`; the same subject as `new:9`, taught once with it |
| `build-test:512` | rule | home | Never create a graphics device in a test, and end GPU tests with the error check, as the test program states it: the same rule as `render-core:607`, taught once with it |
| `new:34` | feature | home | A hint after the exercise: shader functions are tested against their C++ twins by small diagnostic compute shaders that run an include's function and write the results to a buffer the test reads back (`Debug/BlueNoise.comp`, `Debug/LODSelection.comp`, `Debug/ShadowViewStats.comp`; the LOD case is `draw/lod`'s) (about 120 words). Evidence: `Strata/shaders/Debug/BlueNoise.comp.slang:5-6`; `Strata/CMakeLists.txt:103-105`; `StrataTests/src/Renderer/GPUBlueNoiseTests.cpp:35` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The short source build, one test case and running `StrataTests` | `core/first-change` | must |
| The terminal: a program with arguments, environment variables | `basics/tools` | must |
| Shaders, registering an entry, re-running configure | `gpu/shaders` | must |
| Clip space, NDC with +Y up, fullscreen UVs | `gpu/coordinates` | must |
| NVRHI's device, command lists and immediate lists | `gpu/vulkan-nvrhi` | must |
| GPU resources in NVRHI: a render target, a framebuffer and a draw's graphics state | `gpu/vulkan-nvrhi` | must |
| Pipeline state objects | `gpu/binding` | helps |
| Readback in a frame, polled | `gpu/readback-timing` | helps |

**Starting state.** The source build of `core/first-change`: the engine at the pin in the reader's own build directory,
configured with the platform's preset and built in Debug, so `StrataTests` exists and validation is on. No project and
no editor are used. The tutorial's patch starts from the pin; each section's checkpoint is the patch up to that section.

**Command-only steps.** none

## `gpu/debugging` — Debugging the GPU: validation, frame captures, the error count and debug views

**Covers.** The goal: find out why a frame looks wrong or why a GPU test fails, with the GPU's own tools. What must be
true first: a Debug build of the pin, a copy of the Showcase sample open in its editor, RenderDoc or Nsight Graphics
installed. The steps: run with validation (on in Debug builds, off in the others, on in tests unless
`STRATA_TEST_GPU_VALIDATION` is `0`); read a validation message in the log and its severity, with two sentences on why
it is counted and a link to `gpu/vulkan-nvrhi`, which teaches what the layer checks and how messages are classified;
recognize the reports Strata demotes on purpose (MoltenVK's blending report, the bindless support query, the loader's
search for a missing layer) and NVRHI's own errors; use the error count in a test and stop in the message callback to
find the call that caused it; give resources names and passes markers; capture a frame with RenderDoc and find the
markers of `gpu/frame-tour`'s passes, knowing that shaders carry no source-level debug information; switch the Scene
view's debug view and go to the page that reads it.

The page holds the table of debug views (streaming, lod, mip, motion, shadows, lighting, ao, indirect, luminance,
albedo, voxels), each with what it shows in one line and the page that teaches reading it. The result: the reader can
tell API misuse (validation), wrong data (a capture) and a wrong look (a debug view) apart. Variations: Nsight in place
of RenderDoc; macOS and MoltenVK; a failing GPU test instead of the editor; a debug view saved to a file with
`viewport.capture`, given as the complete line to paste with a link forward to `editor/commands`. The exercise breaks an
NVRHI rule on purpose in a scratch copy of the triangle test and finds the line through the message callback.

**Leaves out.**

- What the validation layer checks, why it is off outside Debug and how errors are counted → `gpu/vulkan-nvrhi`
- What each lighting view measures and its statistics → `light/measuring-light`
- Reading the streaming, lod, mip and motion views → `draw/asset-requests`
- How overlays draw the tints and views over the image → `gpu/debug-drawing`
- The frame's passes the markers name → `gpu/frame-tour`
- Debugger setup per OS and asserts → `core/debugging`
- The GPU suites and their error checks → `engineering/test-kinds`

**Fit.** `fits`: about 2,900 words against M (3,000). Seven steps without theory, the table of debug views, four
variations and the exercise take the most words.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-core:304` | concept | link | Validation layers and error counting, in the two sentences a how-to allows, with a link to `gpu/vulkan-nvrhi`, its home |
| `render-core:41` | feature | use | Reading a classified message in the log: an error counted, a warning logged, the demoted reports recognized |
| `render-core:42` | feature | use | NVRHI's errors in the log and in the error count a test checks |
| `new:11` | feature | home | Debug names on resources and markers around passes, which a frame capture shows. Evidence: `Strata/src/Strata/Renderer/Renderer.cpp:63, 119` (`desc.debugName`); `Strata/src/Strata/Renderer/SceneRenderer.cpp:3286` (the renderer's name as the frame's marker) and `:3361-3723` (a marker per pass) |
| `new:12` | not-done | home | No shader debug information: slangc runs without `-g`, so a frame capture shows shaders without their source. Evidence: `CMake/StrataShaders.cmake:77-79`; `Docs/Roadmap.md:1090` (read again at the pin) |
| `render-core:542` | figure | home | A validation error in the log, counted as an error (a text capture) |
| `render-core:656` | hands-on | home | Capture the editor in RenderDoc or Nsight and match the markers to the passes |
| `render-core:845` | open | home | Settled: the engine's documents describe no capture tool (the Roadmap names RenderDoc once, `Docs/Roadmap.md:1090`); the markers exist, so the capture steps are checked on the GPU in phase B |
| `render-core:691`, `build-test:668` | term | link | Validation layer, homed on `gpu/vulkan-nvrhi` with `render-core:304` |
| `render-core:52` | feature | use | Validation on by default in Debug builds only |
| `render-scene:182` | feature | home | The viewport's debug views as a list, and their mechanism: the lod, streaming, mip and motion tints and views; each view is read on its subject's page |
| `render-direct:757` | term | home | Debug view (lighting, AO, indirect, luminance, albedo, shadows), beside the list of views it names; `light/measuring-light` links (about 30 words) |
| `editor-ui:198` | feature | use | The Scene view's chips, the debug view among them |
| `render-direct:177`, `render-direct:178` | feature | link | The shadows view; the lighting views |
| `render-indirect:180` | feature | link | The GI's views (voxels) |
| `render-image:174` | feature | link | The motion view |
| `assets:214` | feature | link | The streaming and mip views |
| `new:35` | hands-on | home | Exercise (modify): in a scratch copy of the triangle test, break one NVRHI rule on purpose, run it with validation, stop in the message callback and follow the call stack to the line that caused the error; the worked solution is a patch that names the rule broken. Evidence: `Strata/src/Platform/Vulkan/VulkanGraphicsDevice.cpp:86-106, 110-134`; `StrataTests/src/Renderer/GPURendererTests.cpp:131-172` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Writing a GPU test and its error count | `gpu/first-triangle` | must |
| Debugging the engine: a debugger attached, breakpoints, the log | `core/debugging` | must |
| Opening a sample's copy in the editor and its Scene view | `start/first-game` | must |
| The frame's passes, for the markers | `gpu/frame-tour` | helps |
| How to read and run a command | `start/how-to-read` | helps |

**Starting state.** A Debug build of the pin made as `core/first-change` shows, with its editor; a copy of the Showcase
sample made from the launcher and opened, as `start/first-game` shows; RenderDoc or Nsight Graphics installed for the
capture step. No change to the engine.

**Command-only steps.** none

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

## `gpu/binding` — Pipelines and binding: layouts, registers and bindless

**Covers.** The job: tell the GPU which resources a draw or a dispatch reads and writes, and fix the rest of its state
in one object made ahead of time. The problem and the approaches to binding: slots (Direct3D 11), descriptor sets and
tables (Vulkan, Direct3D 12), bindless. The map is the register figure: HLSL's `tN`, `sN`, `bN`, `uN` and `spaceS` become
Vulkan bindings N + 0, 128, 256 and 384 in set S; set 0 holds the scene layout, set 1 the bindless table; push
constants sit beside them. The contract, each rule with its reason: a new scene resource takes the next free slot of
the ledger in `Include/Scene.slang` and a pass that does not run binds a dummy; a push constant's slot never equals
another layout's constant buffer slot; a scene vertex shader reads exactly its input layout; a new binding counts against
MoltenVK's limits of 31 storage buffers and 16 samplers per stage, of which the scene set already uses 12 and 9 (GPU
culling's layout 23 storage buffers). A constant buffer, the glossary's entry here, is a buffer of constants bound at a
`b` register; the volatile kind is `gpu/resources-lifetimes`' entry, linked. The layout of GPU structs:
std140 for constant buffers, std430 for structured buffers, mirrored by C++ structs whose sizes are checked
(`FrameConstants` and `InstanceData` as the CPU and GPU contract). The toy binds one texture and one constant buffer for
a fullscreen pass in about 50 lines.

Pipeline state objects: everything fixed in one object; the scene's `PipelineKey` (pass, double-sided, mirrored,
skinned, velocity, surface) and its cache, where the vertex shader is chosen by pass and key, the input layout by the
vertex shader, culling and winding, the reversed-Z depth test per pass, the shadow bias and the blending of
transparents; fullscreen pipelines cached per framebuffer; one scene binding layout shared by the passes; when pipelines
are made and what that costs (a scene pipeline on the first frame that draws its key, searched in each renderer's own
cache, with NVRHI's one in-memory pipeline cache never saved, so a new key in a running game compiles inside the frame;
compute pipelines made with the renderer's resources, a missing shader there stopping the program). Bindless last:
the problem (binding textures per material breaks batching), the approaches (texture arrays, descriptor indexing,
virtual texturing), `BindlessTextureTable` (one update-after-bind array that grows from 1,024 slots by doubling up to
32,768, three reserved slots, a slot reused only frames-in-flight + 1 frames after release, a replaced texture taking a
new slot, and what a full table does), the table's size as the device allows it, the `TextureTable` indirection that
lets streaming change slots without touching a material, and bindless reads in shaders. Alternatives, tests and
changing safely close the page; the exercise traces a texture to its bindless slot.

**Leaves out.**

- Batching, sort keys and buckets of pipeline state → `draw/batching`
- The material record and its texture table entries → `light/material-data`
- Mip streaming, which changes bindless slots every frame → `draw/mip-streaming`
- Mirrored pipelines and flipped tangents → `draw/mirrors-camera-relative`
- Skinned variants of the scene shaders → `draw/skinned`
- Resource states and constant buffer versions → `gpu/resources-lifetimes`

**Fit.** `fits`: about 6,250 words against L (5,000). Four concepts, four excerpts, when pipelines are made and the
bindless table take the most words; at 250 words below L's top the page can take nothing more.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-core:364` | concept | home | Binding models, registers shifted to NVRHI's Vulkan ranges, one shared layout with a ledger, push constants in C++ only |
| `render-core:374` | concept | home | Pipeline state objects; the `PipelineKey` cache; the mistake of an input attribute no shader reads |
| `render-core:406` | concept | home | GPU struct layout rules and their C++ mirrors; the mistake of a `vec3` that shifts every later field |
| `render-core:369` | concept | home | Bindless textures and the stable texture table; the mistake of overwriting a slot a frame in flight may sample |
| `render-core:94`, `render-core:95` | feature | home | Scene pipelines by key; fullscreen pipelines |
| `new:39` | feature | home | When pipelines are made, and the cost: `GetScenePipeline` makes a scene pipeline the first time a frame draws its key, while draws are recorded, after searching the renderer's own vector of keys; each `SceneRenderer` keeps its own cache; NVRHI adds one empty in-memory `VkPipelineCache` per device, never saved, so a new key in a running game compiles inside the frame; compute pipelines are made with the renderer's resources, and a missing shader there stops the program (`ST_CORE_VERIFY`) (about 150 words). Evidence: `Strata/src/Strata/Renderer/SceneRenderer.cpp:226-232, 2091, 2424-2430, 2523-2525`; `Strata/src/Strata/Renderer/SceneRenderer.h:2445`; `Strata/vendor/NVRHI/src/vulkan/vulkan-device.cpp:245-248`; `git grep -ni pipelinecache 822a7a46 -- Strata/src` finds nothing |
| `render-core:46` | feature | use | MoltenVK's limits in the contract: 31 storage buffers and 16 samplers per stage; the scene set uses 12 storage buffers and 9 samplers, GPU culling's layout 23 storage buffers, and a new binding counts against these (about 100 words; `Docs/DeveloperGuide.md:298-301`) |
| `render-core:97`, `render-core:98`, `render-core:99` | feature | home | The scene binding layout; push constants; the four scene vertex layouts |
| `render-core:127` | feature | home | `Include/Scene.slang` as the layout ledger and the structs shared with C++ |
| `render-core:144` | feature | home | std140 and std430, mirrored by C++ structs with checked sizes |
| `render-core:100`, `render-core:101`, `render-core:102` | feature | home | `BindlessTextureTable`; `TextureTable`; bindless reads in shaders |
| `new:40` | feature | home | A full bindless table: `Allocate` returns an invalid slot and the table logs it; a texture being finalized then fails to load, and a streaming swap keeps the levels it has (one sentence, about 60 words). Evidence: `Strata/src/Strata/Renderer/BindlessTextureTable.h:38-39`; `Strata/src/Strata/Renderer/Texture.cpp:513-518, 826-829` |
| `render-core:40` | feature | home | The bindless table's size: the support query, halving to 1,024, the MoltenVK exception |
| `render-core:461` | code | home | `Strata/shaders/Include/Scene.slang:53-133`: `FrameConstants` and `InstanceData` as the CPU and GPU contract, paired with `Strata/src/Strata/Renderer/SceneRenderData.h:113, 189-199` |
| `render-core:466` | code | home | `Strata/src/Strata/Renderer/SceneRenderer.cpp:2424-2527`: a pipeline from a key: shaders, input layout, winding, culling, depth test per pass, shadow bias, transmittance blending |
| `render-core:472` | code | home | `Strata/src/Strata/Renderer/SceneVertexLayouts.h:23-89`: `constexpr` tables that tie vertex shaders to their input layouts |
| `render-core:454` | code | home | `Strata/src/Strata/Renderer/BindlessTextureTable.cpp:23-108`: growing a partially bound table; allocating slots and recycling them after `framesInFlight + 1` frames |
| `render-core:496`, `render-core:498` | figure | home | Registers to bindings; the bindless indirection from material to slot |
| `render-core:571` | rule | home | Bindless slots are written only at allocation and recycled after frames in flight; resolve slots every frame |
| `render-core:589` | rule | home | A push constant's slot must not equal another layout's constant buffer slot |
| `render-core:595` | rule | home | A scene vertex shader reads exactly its input layout; a new one gets its line in the table |
| `render-core:611` | rule | home | A new scene resource takes the next free slot of the ledger; a pass that does not run binds a dummy |
| `render-core:703`, `render-core:704`, `render-core:705`, `render-core:707` | term | home | Descriptor and descriptor set; binding layout and binding set; register and space; push constants |
| `render-core:711`, `render-core:712`, `render-core:713`, `render-core:715` | term | home | std140 and std430; bindless; update-after-bind and partially bound; texture table |
| `editor-ui:786`, `editor-ui:789` | term | home | Binding set; push constants, as the editor's UI words them; one entry each with `render-core:704` and `render-core:707` |
| `render-core:716`, `render-core:717` | term | home | Pipeline (PSO); input layout |
| `new:41` | term | home | Constant buffer: a buffer of constants a shader reads at a `b` register, `FrameConstants` at `b0` the scene's; its own glossary entry, apart from the volatile constant buffer, which is `render-core:708` on `gpu/resources-lifetimes` (R33 D34, critic-render-core-16). Evidence: `Strata/shaders/Include/Scene.slang:121`; `Strata/src/Strata/Renderer/SceneRenderer.cpp:359` |
| `render-core:63` | feature | use | The fallback textures a pass binds as its dummy |
| `render-core:708` | term | use | Volatile constant buffer, the kind the scene layout binds at `b0`; its entry is on `gpu/resources-lifetimes` |
| `render-scene:89` | feature | home | The pipeline cache by key, with the same subject as `render-core:94` |
| `render-scene:92` | feature | home | The scene vertex layouts, with the same subject as `render-core:99` |
| `render-scene:579` | term | home | Pipeline key |
| `render-image:725` | term | home | Push constants, as the image part words them; one entry with `render-core:707`; the volatile constant buffer the item also names is linked to `gpu/resources-lifetimes` (duplicates.md, "Volatile constant buffer") |
| `render-image:726` | term | home | std140, as the image part words it; one entry with `render-core:711` |
| `new:42` | hands-on | home | Exercise ("trace it yourself"): a material's base color texture to its bindless slot on the source build: a breakpoint in `BindlessTextureTable::Allocate` when the texture finalizes, the slot read, then the same slot found in the material's texture table entry; a second run after mip streaming swaps the texture shows the new slot. Evidence: `Strata/src/Strata/Renderer/BindlessTextureTable.cpp:39-60`; `Strata/src/Strata/Renderer/Texture.cpp:513-519, 823-829` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Shaders, the register convention of `Common.slang` | `gpu/shaders` | must |
| Resources, states, constant buffers and their versions | `gpu/resources-lifetimes` | must |
| Structured buffers and UAVs | `gpu/compute` | must |
| Reversed Z and the counter-clockwise front face | `gpu/coordinates` | must |
| Frames in flight | `gpu/how-a-gpu-frame-works` | must |
| Bytes, alignment and padding | `basics/bytes` | must |
| Mip streaming, which changes slots | `draw/mip-streaming` | helps |
| Mirrored instances | `draw/mirrors-camera-relative` | helps |
| Skinned meshes in the renderer | `draw/skinned` | helps |

## `gpu/geometry-pool` — Meshes on the GPU and the geometry pool

**Covers.** The job: hold every mesh's vertices and indices in a few shared buffers, so that draws of different meshes
share their state, and let the pool move geometry without the meshes knowing. The problem (a buffer per mesh means a
bind and often a draw per mesh) and the approaches (interleaved or separate streams, a buffer per mesh, one large
buffer per vertex format, pools with suballocation). The map is the pool's memory figure: the Static and Skinned arenas,
the index arena, handles, the allocation table, free ranges and a compaction moving a mesh. A mesh on the GPU: 12-byte
positions in their own stream (depth-only passes fetch nothing else), 36-byte attributes (normal, tangent with its
sign, UV), a 16-byte skin stream, submeshes with levels of detail, counter-clockwise faces, uploads through the queue
into the pool, and the positions and indices the CPU keeps for physics; `MeshFactory`'s primitives as built-in assets.
The contract: a stable `GeometryHandle`; ranges that move, so geometry is read through the pool every frame and binding
sets are made again when a buffer version changes; frees that wait for the GPU. The limits: each stream's buffer is at
most 2 GiB (about 59.6 million vertices per vertex arena, 536 million indices in all), ranges are rounded to 16
vertices and 64 indices, the pool starts at 65,536 static vertices, 4,096 skinned vertices and 262,144 indices and
doubles, a mesh that does not fit waits for the next frame's growth, and a mesh larger than one buffer fails with an
error.

The toy is a range allocator with free lists and coalescing in about 60 lines. The real code is the pool's design
comment, then compaction: moves planned within 8 MiB a frame when more than a quarter of an arena's free space is
scattered, copies on the GPU through a scratch buffer, the owner table updated, growth by copying into larger buffers.
Last, how a draw finds its mesh and its instance at the foundation level: indirect draw arguments at the mesh's place in
the pool, a 64-byte `InstanceData` per instance, the frame's draw list read with `SV_VulkanInstanceID`, all shown in the
scene vertex shader; instancing, the instance, the draw list and the indirect draw are each said in one sentence and
linked to their homes on `draw/batching` and `draw/render-scene`. Alternatives, tests (`GPU.Renderer.GeometryPool`),
changing safely; the exercise fragments the Static arena, compacts it and checks that a rendered frame is the same, and
a second traces one mesh to its range and back after a compaction.

**Leaves out.**

- Instancing, the draw list, indirect draws, the `SV_VulkanInstanceID` rule, sort keys, batches and buckets → `draw/batching`
- The instance and `InstanceData` as the render scene holds them → `draw/render-scene`
- The culling tables in the pool and GPU-driven drawing → `draw/gpu-driven`
- Levels of detail and how one is chosen → `draw/lod`
- Camera-relative positions in the vertex shader → `draw/mirrors-camera-relative`
- Skinning in the vertex shader → `draw/skinned`
- The glTF importer and cooked meshes → `assets/models-gltf`
- Mesh colliders that read the CPU's triangles → `physics/building-bodies`

**Fit.** `over`: about 5,050 words against M (3,000). Two concepts, three excerpts, the toy, the pool's limits and two
exercises pass M's top; the page takes L by S2 (5,050 is inside L's range).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-core:397` | concept | home | Vertex data layout: separate streams and shared geometry; the mistake of caching a mesh's offsets across frames |
| `render-core:402` | concept | home | Instancing, draw lists and indirect draws at the foundation level: the shape `gpu/frame-tour` needs; instancing is used here first on track E and defined in one sentence with a link to `draw/batching`, its home (ui-q5); the details are `draw/batching`'s |
| `render-core:110`, `render-core:111`, `render-core:113` | feature | home | The `Mesh` asset's GPU side; `GeometryPool`; `MeshFactory` |
| `new:13` | code | home | `Strata/src/Strata/Renderer/GeometryPool.h:62-72`: the pool's design: arenas, stable handles, frees after the GPU, growth and compaction in `BeginFrame` |
| `new:14` | code | home | `Strata/src/Strata/Renderer/GeometryPool.cpp:435-503`: `CompactArenas`: planned moves, GPU copies through the scratch buffer, the owners updated |
| `render-core:463` | code | home | `Strata/shaders/Scene/Mesh.vert.slang:35-60`, with its entry wrapper at lines 85-137: draw list, instance, position, clip; the tangent's handedness named |
| `render-core:500` | figure | home | The geometry pool's memory layout |
| `render-core:574` | rule | home | Read mesh geometry through the pool every frame |
| `render-core:586` | rule | link | `SV_VulkanInstanceID`, not `SV_InstanceID`, named where the vertex shader reads the draw list; the rule's home is `draw/batching` (R31 D33) |
| `new:43` | feature | home | The pool's limits and failure path: each stream's buffer at most 2 GiB (about 59.6 million vertices per vertex arena of 36-byte attributes, 536 million indices in all); ranges rounded to 16 vertices and 64 indices; start sizes of 65,536 static vertices, 4,096 skinned vertices and 262,144 indices, doubled on growth; a mesh that does not fit returns `Retry` and uploads after the next frame's growth; a mesh larger than one buffer fails with an error (about 120 words). Evidence: `Strata/src/Strata/Renderer/GeometryPool.h:77-94, 97-102`; `Strata/src/Strata/Renderer/GeometryPool.cpp:154-158, 546-572`; `Strata/src/Strata/Renderer/Mesh.cpp:351-358` |
| `render-core:653` | hands-on | home | Fragment, compact, compare a frame |
| `new:44` | hands-on | home | Exercise ("trace it yourself"): one mesh to its range: a breakpoint in `GeometryPool::Allocate` when a model loads on the source build, its handle and offsets read, then the same handle's new offsets found after `CompactArenas` moved it. Evidence: `Strata/src/Strata/Renderer/Mesh.cpp:351`; `Strata/src/Strata/Renderer/GeometryPool.cpp:151, 435-503` |
| `render-core:748`, `render-core:749`, `render-core:750` | term | home | Geometry pool and arena; range allocator; compaction |
| `render-core:751`, `render-core:752`, `render-core:753` | term | link | Instance and `InstanceData`; draw list; indirect draw: each said in one sentence, linked to its home (`draw/render-scene` for the instance, `draw/batching` for the other two; R31 D33) |
| `foundation:162` | feature | home | `RangeAllocator`: size-class free lists, coalescing and bounded compaction planning; the pool is its only user at the pin, and the toy is a small one |
| `foundation:645` | term | home | Offset (range) allocator; one entry with `render-core:749` |
| `render-scene:90` | feature | home | The geometry pool as the drawing part lists it, with the same subject as `render-core:111` |
| `render-scene:278` | concept | home | Shared geometry buffers, the same idea as `render-core:397` |
| `render-scene:403` | figure | home | The pool's memory map, drawn once with `render-core:500` |
| `render-scene:482` | rule | home | Read mesh geometry through the pool every frame, the same rule as `render-core:574` |
| `render-scene:574` | term | home | Submesh, met first with meshes on the GPU |
| `render-scene:588-591` | term | home | Geometry pool; arena (Static, Skinned); `GeometryHandle`; compaction |
| `render-scene:91` | feature | link | The culling tables in the pool (`Include/GeometryTables.slang`, as culling and the voxelizer read them), taught with GPU-driven drawing |
| `render-scene:370` | code | link | The same vertex shader from another angle: `draw/mirrors-camera-relative` quotes its lines 50-56 and 76-81 (the relative position, the normal, the mirrored handedness, the previous position), and this page's excerpt `render-core:463` holds lines 35-60 (duplicates.md, "Scene vertex shader excerpt") |
| `render-core:142` | feature | link | Camera-relative positions in the vertex shader |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Staging, the upload queue and tickets | `gpu/upload-queue` | must |
| Pipelines and input layouts | `gpu/binding` | must |
| Deferred release and event queries | `gpu/resources-lifetimes` | must |
| Data structures: arrays, free lists, hash maps | `basics/data-structures` | must |
| Levels of detail | `draw/lod` | helps |
| Camera-relative positions | `draw/mirrors-camera-relative` | helps |
| Batching and instancing | `draw/batching` | helps |

## `gpu/frame-tour` — A frame of the scene renderer, pass by pass

**Covers.** The job: what `SceneRenderer::Render` does with a scene and a camera, pass by pass, as the map every
rendering page links back to. The problem and the approaches: forward, forward with clustered lights, deferred with a
G-buffer, visibility buffers, with a table of their costs; Strata's choice, clustered forward with a depth, normal and
entity-ID prepass and an opaque pass that tests depth for equality, and why that needs positions identical to the bit
(the invariant decoration). The engine's documents give no reason for forward over deferred, so the page presents the
choice as a trade-off and names no motive. The map: the passes as a vertical timeline by GPU stage, with the targets
each one reads and
writes, and how the frame's code is split over files. The contract: the `SceneRenderer` API (output, HDR, depth, normal
and entity-ID textures; `SetViewportSize`, checked and released through `ReleaseDeferred`; `SetQuality`; stats; history
and exposure resets), the target framebuffer's rules (the viewport's size, non-sRGB UNORM), `SceneRenderOptions`, the
callers with `GameRenderer` as the simplest, the `SceneCamera` each caller passes (taught on `gpu/coordinates`), and the
rule that a feature switched off is invisible bit for bit and costs nothing (no target made, no stage timed, a dummy
bound). The toy is a frame of prepass, forward pass and one post pass in about 70 lines.

The real frame is walked in order as a trimmed outline: the targets checked; `RenderScene::Sync` and extraction; the
GPU mirror; lights, resolved assets, draw arguments and frame constants with the relative view and the jittered
projection; the command list and its timer; setup; GPU culling; light culling and clusters; aerial perspective; shadows;
clears and the prepass; the sun's screen-space shadow mask; ambient occlusion; GI voxels; reflections; the opaque pass;
the sky; the scene color copy and the transparents; TAA; depth of field; motion blur; exposure, bloom, flares, color
lookup, tone mapping and anti-aliasing; overlays; close and execute. Each step names the page that teaches its feature
and the stage it is timed in; the light passes are timed in the stage before them, as the code has it, not as the
inventories say. The HDR target and the display transform are taught here at the foundation level, with the
intermediate targets as figures (the words HDR, tone mapping, sRGB encoding and half float each said in one sentence and
linked to their homes). A section "Looking inside a frame" matches a capture's markers to the steps. What Strata does
not do here (particles, trails and decals; a render graph; a second view: split-screen, picture-in-picture or a camera
that renders into a texture), alternatives, tests and changing it safely (a new pass: its stage, its slot, its dummy,
invisible when off) close the page; the exercise traces one pass from its marker to its stage and its switch.

**Leaves out.**

- The lights a pass shades with → `light/lights`
- The sun's shadows and the screen-space mask → `light/sun-shadows-1`
- Ambient occlusion → `indirect/ao`
- Screen-space reflections → `indirect/ssr`
- Global illumination's voxels → `indirect/gi-voxels`
- The post chain and its passes → `image/why-post`
- The render scene, extraction and draws → `draw/render-scene`
- GPU culling and the two-phase prepass → `draw/gpu-driven`
- Tiled against clustered light culling → `light/many-lights`
- GPU timestamps and stages → `gpu/readback-timing`
- Overlays in detail → `gpu/debug-drawing`
- Jitter on the frame's camera copy → `image/taa`
- `SanitizeHDR` and the half-float range → `light/brdf`
- The renderer's switches and statistics as tables → `reference/renderer`

**Fit.** `fits`: about 7,500 words against XL (8,000). Twenty-four steps at about 80 words each, the outline from three
ranges, the forward and deferred comparison and the HDR target take the most words. W8r: phase B must read again the
list of passes (local light shadows, area lights, the GI's later stages) and the statistics they report, and the page's
entries of "What Strata does not do": particles, trails and decals; a render graph or frame graph; a second view.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-core:409` | concept | home | Forward with a depth prepass, against forward+, deferred and visibility buffers; `EQUAL` and identical positions; the mistake of changing the prepass's vertex math alone |
| `render-core:414` | concept | home | HDR rendering and the display transform at the foundation level: the RGBA16F target, tone mapping into UNORM, why the engine encodes sRGB itself |
| `render-indirect:329` | concept | home | The rule of the renderer: a feature that is off is invisible bit for bit and costs nothing (`book.md`'s design decision), checked by tests; the mistake of a uniform branch that changes the default path's rounding. Its places at the pin: `AGENTS.md:393, 399-401, 405-406`; `Docs/DeveloperGuide.md:4968, 5404, 5762` |
| `render-direct:822` | open | home | Settled: the documents give no reason for forward over deferred (no match for "deferred shading", "G-buffer" or "forward rendering" in `Docs/DeveloperGuide.md`, `Docs/Architecture.md`, `Docs/Roadmap.md` and `AGENTS.md`); the page states the trade-off without a motive |
| `render-core:155-178` | feature | home | The 24 steps of `RenderFrame` in the code's order, each with its stage; the light passes are timed in the stage before them (`GPU.Cull` on the GPU-driven path, `GPU.Setup` otherwise: `SceneRenderer.cpp:3360-3378`), not always `GPU.Cull` as the inventory's table says |
| `render-core:180` | feature | home | The `SceneRenderer` API, `SetViewportSize`, `SetQuality`, stats, resets, temporal jitter named, output target rules, `SceneRenderOptions` |
| `render-core:187` | feature | home | The frame's code split over the `SceneRenderer*.cpp` files |
| `render-core:193` | feature | home | `GameRenderer` as the simplest caller of `SceneRenderer::Render` |
| `render-core:467` | code | home | `Strata/src/Strata/Renderer/SceneRenderer.cpp:2901-3735`: the frame as timed passes, shown as a trimmed outline from lines 3283-3289, 3360-3420 and 3489-3541 |
| `render-core:509` | figure | home | The pass graph: the steps as a timeline colored by stage, with the targets read and written |
| `render-core:525` | figure | home | The intermediate targets of one view: depth, normals, entity IDs, HDR before tone mapping, output |
| `render-core:837` | open | home | No debug view shows raw depth, normals or entity IDs: figure 525 waits for a capture addition (`pipelines.md` §11) and shows a diagram until it ships |
| `render-core:592` | rule | home | The prepass and the forward pass produce identical positions; `Mesh.vert` is decorated `Invariant` by the shader tool |
| `render-core:604` | rule | home | A target framebuffer has the viewport's size and a non-sRGB UNORM format |
| `render-core:724`, `render-core:733`, `render-core:734` | term | home | Invariant position; depth prepass; forward and deferred, with clustered shading linked to its one entry on `light/many-lights` (`render-direct:712`) |
| `render-core:772` | term | home | Entity ID buffer |
| `render-core:754`, `render-core:757` | term | link | HDR, tone mapping and sRGB encoding (homed on `image/why-post`, tone mapping on `image/tone-mapping`); RGBA16F and half float (homed on `basics/color`): each said in one sentence with a link |
| `render-scene:606`, `render-scene:607` | term | home | `EQUAL` depth test; depth prepass (one entry with `render-core:733`) |
| `build-test:648` | term | home | Invariant position, as the build's glossary words it (what the prepass's `EQUAL` test needs); one entry with `render-core:724` |
| `render-scene:479` | rule | home | The prepass and the forward pass produce identical positions, the same rule as `render-core:592`, with LOD fades in both passes |
| `render-direct:204` | feature | home | The stages in frame order as the lighting part lists them, merged into the steps; the same slip as the inventory's step 7 (the light passes are in `GPU.Setup` on the CPU path) |
| `new:15` | not-done | home | No particles, trails or decals. Evidence: `git grep -niE -e particle -e decal 822a7a46 -- Strata/src Strata/shaders` finds nothing; `git grep -niwE "trails?"` there finds only the anti-aliasing tooltips of `Strata/src/Strata/Renderer/RendererComponents.cpp:508, 519, 523`; `Docs/Roadmap.md:1690` (run again at the pin) |
| `new:16` | not-done | home | No render graph or frame graph: `RenderFrame` orders the passes by hand. Evidence: `git grep -n -e RenderGraph -e FrameGraph 822a7a46 -- Strata/src` finds nothing; `Strata/src/Strata/Renderer/SceneRenderer.cpp:2901` (run again at the pin) |
| `new:45` | not-done | home | No second view: no split-screen, no picture-in-picture, no camera that renders into a texture for a mirror or a minimap; a game is drawn from one camera, the first active entity whose Camera is Primary in hierarchy order (`make/characters-cameras` tells makers how to switch). Evidence: `Strata/src/Strata/Scene/Scene.cpp:867-879`; `Strata/src/Strata/Runtime/GameRenderer.cpp:114-126`; `git grep -niE -e "split-?screen" -e "render-?to-?texture" -e "picture-in-picture" -e "RenderTexture" 822a7a46 -- Strata/src StrataScriptCore Docs` finds nothing (run again at the pin) |
| `new:46` | erratum | home | `plan/inventory/render-core.md:162` and `plan/inventory/render-direct.md:205` time light culling and the light clusters in `GPU.Cull` (process.md's table, kind `inventory`): `GPU.Cull` starts only on GPU-driven frames, and light culling and the clusters are recorded after it, so they are timed in `GPU.Cull` on GPU-driven frames and in `GPU.Setup` on frames of the CPU path. Evidence: `Strata/src/Strata/Renderer/SceneRenderer.cpp:3289, 3343, 3360, 3365-3377` |
| `new:47` | hands-on | home | Exercise ("trace it yourself"): one pass from its marker to its stage and its switch: find the marker `Aerial` in `RenderFrame`, the stage its time goes to (`gpuTimer.Next`), the switch that skips it (`m_AerialFrame`) and the page that teaches the feature, then render a scene without the atmosphere on the source build, with a breakpoint there, and see the step skipped. Evidence: `Strata/src/Strata/Renderer/SceneRenderer.cpp:3379-3382`; `Strata/src/Strata/Renderer/SceneRendererAtmosphere.cpp:370` |
| `new:33` | feature | use | `SceneCamera`, as the API contract's camera that every caller passes |
| `render-core:656` | hands-on | use | A capture's markers matched to the steps, in "Looking inside a frame" |
| `render-core:94` | feature | use | Pipelines by key, as each pass picks its pipeline |
| `render-core:212` | feature | link | The GPU stages the steps are timed in |
| `render-core:774` | term | link | Jitter, named in the frame constants |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Clip space, reversed Z and the camera | `gpu/coordinates` | must |
| Pipelines by key, binding layouts and the ledger | `gpu/binding` | must |
| Meshes in the pool, instances and the draw list | `gpu/geometry-pool` | must |
| Compute shaders and dispatches | `gpu/compute` | must |
| Resources and deferred release | `gpu/resources-lifetimes` | must |
| Color: linear and sRGB values, the half-float range | `basics/color` | must |
| GPU stages | `gpu/readback-timing` | helps |
| The render scene's proxies | `draw/render-scene` | helps |
| Lights and shadows as features | `light/lights` | helps |
| The post chain | `image/why-post` | helps |

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

## `gpu/debug-drawing` — Overlays, debug drawing and gizmos

**Covers.** The job: draw over the finished image what helps people see the scene (the grid, the selection outline,
tints, debug lines, gizmos, text and the game's UI) in exact display colors, and let modules above the renderer add
passes the renderer never names. The problem and the approaches: immediate-mode debug lines, retained gizmos, overlay
passes found through a registry (dependency inversion). The map is the overlay order. The contract: overlays are drawn
after post-processing into the output; overlays placed in the scene use constants without jitter and a one-pixel depth
bias under TAA; tints and the outline need the entity-ID buffer; the renderer reaches higher modules only through
registries. The toy is a recorder of line lists and its draw in about 40 lines.

The real code: `DebugDraw` (immediate shapes in two depth modes, circles from tables, packed sRGB colors);
`RenderOverlays` in its order (the views and tints first, the grid, lines uploaded relative to the camera in double,
the world text, the world canvases, the outline, the lines on top, the HUD); `DrawSceneGizmos` (lights, cameras and
colliders through `ComponentInfoBuilder::Gizmo` and its `ComponentGizmo` shapes: box, sphere, capsule, mesh bounds;
culled to the view, icons below a pixel size); `ISceneOverlayPass`,
`SceneOverlayRegistry` and `SceneOverlayFrame`; `SceneScreenView` for the editor's 2D canvas (the struct and the term
"screen view" are taught here; `editor-ui/scene-view` says how canvas mode drives it); `SetJitteredDepthBias`.
The figures show the overlays off and on, and the tints with the streaming view. What Strata does not do: debug drawing
from scripts. Alternatives, tests (`Renderer.DebugDraw`, the overlay GPU tests), changing safely. The exercise starts
from `world/tutorial-component`'s end state and gives the WindZone its gizmo, a sphere of its radius; its solution patch
is the WindZone chain's gizmo, from which `scripting/tutorial-host-function` starts (R41), and `capstone/build` adds
only the arrow. A second draws a path with `DebugDraw` from C++, depth-tested and on top; a third traces a gizmo from
its registration to its lines.

**Leaves out.**

- Picking and the transform gizmo the person drags → `editor-ui/scene-view`
- The game UI's quads, runs and shaders → `ui/drawing`
- Text, fonts and the glyph atlas → `gpu/text`
- What each debug view shows and the page that reads it → `gpu/debugging`
- TAA's jitter → `image/taa`
- LOD selection shared by tools and the renderer → `draw/lod`

**Fit.** `fits`: about 4,900 words against L (5,000). Seven features with three excerpts, two figures and three
exercises, the WindZone chain's gizmo among them, take the most words.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-core:433` | concept | home | Overlays and editor visualisation; overlay passes from higher modules through a registry; the mistake of renderer code including GameUI |
| `render-core:220`, `render-core:221`, `render-core:222` | feature | home | The overlay set; `DebugDraw`; `DrawSceneGizmos` |
| `render-core:223`, `render-core:224`, `render-core:225` | feature | home | `ISceneOverlayPass`, `SceneOverlayRegistry` and `SceneOverlayFrame`; `SceneScreenView`, the struct taught here (critic-gameui-18); `SetJitteredDepthBias` |
| `gameui:685` | term | home | Screen view, beside `SceneScreenView`, which this page teaches; the glossary entry follows the teaching page (critic-gameui-18; passed by `ui`) |
| `new:19` | code | home | `Strata/src/Strata/Renderer/DebugDraw.h:29-62`: the immediate shapes, the depth modes, packed colors |
| `new:20` | code | home | `Strata/src/Strata/Renderer/SceneRenderer.cpp:4055-4126`: the overlays' order, the entity-ID check, debug lines made relative to the camera in double |
| `new:21` | code | home | `Strata/src/Strata/Renderer/SceneOverlay.h:92-136`: `ISceneOverlayPass` and `SceneOverlayRegistry`: modules register factories, each renderer makes one pass per factory |
| `new:22` | not-done | home | No debug drawing from scripts. Evidence: no such function in `StrataScriptCore/Include/StrataScript/` (`git grep -niE -e debugdraw -e drawline 822a7a46 -- StrataScriptCore` finds nothing, run again at the pin) |
| `render-core:515` | figure | home | The overlay order |
| `render-core:528` | figure | home | Overlays isolated: the grid, an outline, gizmos; overlays on and off |
| `render-core:530` | figure | home | Entity tints with the streaming view, as an overlay-based view |
| `render-core:616` | rule | home | The renderer reaches higher modules only through registries |
| `render-core:663` | hands-on | home | Debug drawing from C++, with and without the depth test; scripts cannot |
| `render-core:841` | open | home | Settled: games cannot reach `DebugDraw` from scripts (`new:22`) |
| `render-core:770`, `render-core:771` | term | home | Overlay; gizmo |
| `scene-ecs:203` | feature | home | `ComponentGizmo`: the shapes a component asks the editor to draw (Box, Sphere, Capsule, MeshBounds), which the WindZone's gizmo uses |
| `new:49` | hands-on | home | Exercise (extend), the WindZone chain's gizmo: from `world/tutorial-component`'s end state, the WindZone gets its gizmo through `ComponentInfoBuilder::Gizmo`, a sphere of its radius (`ComponentGizmoShape::Kind::Sphere`), drawn in the one gizmo group the pin has, `Collider`; the solution is the patch `exercise-<n>.patch` of this page's tutorial file, a patch of the chain, from which `scripting/tutorial-host-function` starts (`startsFrom` with the exercise, R41; critic-book-27), and `capstone/build` adds only the arrow of a Directional zone. Evidence: `Strata/src/Strata/Reflection/ComponentRegistry.h:340-341`; `Strata/src/Strata/Reflection/ComponentGizmo.h:16-20, 23-38`; `Strata/src/Strata/Renderer/SceneGizmos.cpp:122-145` |
| `new:50` | hands-on | home | Exercise ("trace it yourself"): one component gizmo from its registration to its lines: with colliders shown and a Box Collider in view on the source build, a breakpoint in `DrawSceneGizmos`, the step into `BoxColliderGizmo`, registered with `.Gizmo(ComponentGizmoGroup::Collider, ...)`, which fills a `ComponentGizmoShape`, and `DrawShape` turning the shape into `DebugDraw` lines. Evidence: `Strata/src/Strata/Renderer/SceneGizmos.cpp:122, 165-176, 215`; `Strata/src/Strata/Physics/PhysicsComponents.cpp:143` |
| `gameui:342` | concept | home | Overlay passes and dependency inversion, as the game UI meets them; the same idea as `render-core:433` |
| `gameui:660` | term | home | Overlay pass |
| `render-core:177` | feature | use | The frame's overlay step |
| `render-core:226` | feature | link | LOD selection as pure functions, which tools show |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The frame's passes and its overlay step | `gpu/frame-tour` | must |
| Adding a component and its system (the WindZone) | `world/tutorial-component` | must |
| Reflection: one registration, `ComponentInfoBuilder` | `world/reflection` | must |
| The composition root, registries and dependency inversion | `core/layers-registries` | must |
| Camera-relative positions subtracted in double | `draw/mirrors-camera-relative` | helps |
| TAA's jitter | `image/taa` | helps |
| The Scene view and its chips | `editor-ui/scene-view` | helps |
| The game UI's overlay pass | `ui/drawing` | helps |

## `gpu/text` — Text: fonts, shaping and signed distance fields

**Covers.** The job: turn a font file and a UTF-8 string into glyphs that stay sharp at any size, without trusting the
file and without stalling a frame. The problem and the approaches: bitmap atlases per size, SDF and MSDF atlases, vector
rendering, shaping libraries; Strata's choice: single-channel signed distance fields at 32 texels per em, atlases filled
on demand with LRU eviction and raster budgets, simple shaping (advances, kerning, wrapping, ellipsis), and measuring
kept apart from rasterizing. The map is the font pipeline, from bytes to quads. The contract: font files are untrusted
input (extend `FontValidation`, with crafted-font tests, before calling another stb_truetype function; bound time as
well as reads); text is measured with `ShapeText`, never by rasterizing; passes share the renderer's `FontAtlasCache`.
The toy computes a glyph's distance field from a bitmap by brute force, then shapes one line by advances.

The real code: the `Font` asset (TrueType, the first font of a collection, Roboto Medium embedded as the default);
validation (every table stb_truetype reads, outlines and composites bounded, kerning switched off when unbounded, CFF
rejected, the cmap format 4 search corrected); `FontFace` (metrics without rasterizing, caches bounded at 4,096);
`ShapeText`, `LayoutText`, `MeasureCaretStops` and `DecodeUTF8`; `FontAtlas` (512x512 pages of 42-texel cells, up to 8
pages, LRU that never evicts this frame's glyphs, uploads in bands of 64 rows, cheaper resolution for costly glyphs);
`FontAtlasCache`, shared with the game UI; `TextRenderer` (`TextComponent` on the entity's XY plane, depth-tested, or on
the screen over everything; 32 glyphs and 512 Ki of cost a frame); the shader's coverage, a smoothstep over about one
screen pixel from `fwidth`, taken before the discard. Figures: world and screen text, a magnified glyph, an atlas page.
What Strata does not do: complex scripts and CFF fonts. Alternatives, tests (font, atlas, layout and text GPU suites),
changing safely; the exercise crafts a font whose `loca` points past `glyf`, and a second traces one glyph from
`ShapeText` to its atlas cell. Code point is said in one sentence and linked to `basics/bytes`, its home.

**Leaves out.**

- How rects, sizes and overflow modes drive `ShapeText` in game UI, and text fields → `ui/text`
- Drawing the game UI's glyph quads → `ui/drawing`
- `TextComponent` for game makers: signs and HUD text → `make/hud`
- The editor's fonts, which use ImGui's own atlas → `editor-ui/design-system`
- Untrusted input in general: checksums and bounded sizes → `assets/robustness`
- Localization and right-to-left text → `ui/text`

**Fit.** `fits`: about 5,600 words against L (5,000). Eight features with three excerpts, the validation contract and
two exercises take the most words.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-core:425` | concept | home | Fonts, shaping, glyph atlases and SDFs; Strata's choices; the mistake of measuring text by rasterizing it |
| `render-core:430` | concept | home | Untrusted input in the renderer: font files and stb_truetype, which checks no bounds |
| `render-core:232-239` | feature | home | `Font`; font validation; `FontFace`; `ShapeText` and its siblings; `FontAtlas`; `FontAtlasCache`; `TextRenderer`; SDF coverage in the shader |
| `new:23` | code | home | `Strata/src/Strata/Renderer/TextLayout.h:50-112`: `TextShapeOptions`, `ShapedText` and `ShapeText`: layout from metrics alone |
| `render-core:474` | code | home | `Strata/src/Strata/Renderer/FontValidation.h:63-72`: what is verified before stb_truetype reads a byte, with the CFF refusal at `Strata/src/Strata/Renderer/FontValidation.cpp:131-132` |
| `render-core:473` | code | home | `Strata/shaders/Include/SDFText.slang:4-15`, with `Strata/shaders/Overlay/Text.frag.slang:17-26`: coverage from `fwidth`, the derivative before the discard |
| `new:24` | not-done | home | No complex-script shaping and no fonts with CFF outlines: shaping is advances, kerning and line breaks. Evidence: `Strata/src/Strata/Renderer/FontValidation.cpp:131-132`; `Strata/src/Strata/Renderer/TextLayout.h:109-112`; render-core inventory, concept 30 |
| `render-core:513` | figure | home | The font pipeline |
| `render-core:536` | figure | home | World and screen text; a magnified SDF glyph; an atlas page from `FontAtlas::GetPagePixels` |
| `render-core:613` | rule | home | Font files are untrusted: extend `FontValidation` first; bound time as well as reads |
| `render-core:615` | rule | home | Measure with `ShapeText`; passes share the `FontAtlasCache` |
| `render-core:651` | hands-on | home | The font validation exercise |
| `new:51` | hands-on | home | Exercise ("trace it yourself"): one glyph from `ShapeText` to its atlas cell on the source build: a sign whose text holds a glyph not yet in the atlas, a breakpoint in `FontAtlas::Rasterize`, the cells allocated and the page it lands in, and the frame its rows upload in. Evidence: `Strata/src/Strata/Renderer/FontAtlas.cpp:81, 103-116, 147, 342`; `Strata/src/Strata/Renderer/TextLayout.h:109-112` |
| `render-core:762-769` | term | home | Font and glyph (code point, which the item also names, is linked to `basics/bytes`, its home: duplicates.md, "Code point"); TrueType, CFF and OTTO; stb_truetype; kerning and GPOS; text shaping; SDF; glyph atlas, page and cell; LRU eviction |
| `render-core:247` | feature | use | `TextComponent`, which the renderer registers |
| `gameui:303` | concept | home | Shaping against rasterizing and distance-field fonts, the same subject as `render-core:425`; `ui/text` and `ui/drawing` use it |
| `gameui:645` | term | home | Glyph, advance, kerning, baseline and em; one entry with `render-core:762` and `render-core:765` |
| `editor-ui:716` | term | home | Font atlas, as the editor's UI words it; one entry with `render-core:768`; the editor's own atlas is ImGui's, which `editor-ui/design-system` says |
| `gameui:115` | feature | link | The game UI shaping its texts from font metrics |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Overlays and their order | `gpu/debug-drawing` | must |
| Bytes, text encodings and UTF-8 | `basics/bytes` | must |
| Derivatives and discard in shaders | `gpu/shaders` | must |
| Texture arrays and binding sets | `gpu/binding` | must |
| Hash maps and caches | `basics/data-structures` | must |
| Budgeted uploads | `gpu/upload-queue` | helps |
| Untrusted input in general | `assets/robustness` | helps |
| Text in game UI | `ui/text` | helps |

## Passed on

| Item | Type | To | Why |
| --- | --- | --- | --- |
| `render-core:55` | feature | `core/frame-loop` | The frame's order lives in `Application` (other area); the page of the frame loop teaches it, with Graphics' place in it |
| `render-core:108` | feature | `assets/uploads` | The `Texture` asset's GPU side: `FinalizeOnMainThread` uploads the smallest level first in planned steps, which is what assets queue and when |
| `render-core:109` | feature | `assets/texture-cooking` | Devices without BC sampling get levels decoded on workers: the BC decode fallback of that page |
| `render-core:112` | feature | `physics/building-bodies` | The renderer registers how to read a mesh's triangles so physics never includes it: mesh colliders read it |
| `render-core:121`, `render-core:124` | feature | `engineering/generated-code` | The custom commands, StrataShaderTool's patch and the generated registry are that page's by `book.md` |
| `render-core:123` | feature | `engineering/third-party` | Slang's pinned download is that page's by `book.md` |
| `render-core:142` | feature | `draw/mirrors-camera-relative` | Camera-relative space is that page's by `book.md` |
| `render-core:226` | feature | `draw/lod` | LOD selection as pure functions, and the CPU and GPU agreeing, belong with levels of detail |
| `render-core:387`, `render-core:391` | concept | `draw/mirrors-camera-relative` | Winding and mirrored transforms; float precision far away and camera-relative rendering: that page's by `book.md` |
| `render-core:462` | code | `draw/mirrors-camera-relative` | `TransformPositionRelative` and `TransformNormal` (`Strata/shaders/Include/Scene.slang:238-260`) teach that page's two subjects |
| `render-core:465` | code | `nowhere` | Repeats `foundation:370`: the same lines of `Math.cpp`, whose home is `core/math` |
| `render-core:532` | figure | `nowhere` | Repeats `render-scene:450` (and `render-image:512`): the motion view, read on `draw/motion-vectors` |
| `render-core:533`, `render-core:538` | figure | `draw/mirrors-camera-relative` | The 100 km comparison and the mirrored instance show that page's subjects |
| `render-core:598`, `render-core:600` | rule | `draw/mirrors-camera-relative` | Mirrored pipelines and flipped tangents; never a world position in a scene shader |
| `render-core:603` | rule | `light/brdf` | `SanitizeHDR` is taught where the first pass that writes HDR values calls it (`book.md`) |
| `render-core:648` | hands-on | `draw/mirrors-camera-relative` | The camera-relative audit |
| `render-core:668` | hands-on | `nowhere` | Repeats `render-scene:559` (mirroring a prop safely), whose home is `make/transforms-units` (R31 D40) |
| `render-core:661` | hands-on | `make/performance` | Vsync and its cost: games set vsync from a script (`Game::SetVSync`, the settings screen of `make/menus`) and the editor keeps its own in play mode (`StrataEditor/src/Editor/EditorGameWindow.cpp:65-71`), so reading the cost is a variation of measuring a game |
| `render-core:665` | hands-on | `make/hud` | World and screen text with `TextComponent`: that page is its use home |
| `render-core:667` | hands-on | `make/commands` | Screenshots for a store page need `viewport.capture`: the editor has no screenshot menu |
| `render-core:670` | hands-on | `make/large-worlds` | A scene 50 km from the origin, for game makers |
| `render-core:672` | hands-on | `make/performance` | The GPU stages of a game with `--perf-log` or the Performance panel |
| `render-core:738`, `render-core:739`, `render-core:741`, `render-core:742` | term | `draw/mirrors-camera-relative` | Mirrored transform, tangent handedness, camera-relative rendering and origin rebasing are defined with mirroring and camera-relative space |
| `render-core:740` | term | `basics/math-bases` | Normal matrix and cofactor matrix are words of mathematics, taught from zero on that page; `draw/mirrors-camera-relative` holds a `use` row (R43, R46) |
| `render-core:751` | term | `draw/render-scene` | Instance and `InstanceData` are defined beside `render-scene:573` (R31 D33); `gpu/geometry-pool` links |
| `render-core:752`, `render-core:753` | term | `draw/batching` | Draw list and indirect draw are defined beside `render-scene:575` and `:583` (R31 D33: draw list, feature and term, on `draw/batching`); `gpu/geometry-pool` links |
| `render-core:586` | rule | `draw/batching` | `SV_VulkanInstanceID`, not `SV_InstanceID`, beside its twin `render-scene:587` (R31 D33); `gpu/geometry-pool` and `gpu/shaders` link |
| `render-core:728`, `render-core:730` | term | `basics/math-projection` | Clip space and NDC, and reversed Z, are the mathematics' words, beside `foundation:633` and `:634` (duplicates.md, "Reversed Z and NDC"); `gpu/coordinates` keeps Strata's convention and the precision argument, and links |
| `render-core:757` | term | `basics/color` | RGBA16F and half float, one entry with `render-direct:703` and `render-image:638` (duplicates.md, "Half float"); `gpu/frame-tour` links |
| `render-core:754` | term | `image/why-post` | HDR, tone mapping and sRGB encoding, one entry with `render-image:634` and `:636`, tone mapping linked to `image/tone-mapping` (duplicates.md, "HDR, tone mapping, sRGB encoding"); `gpu/frame-tour` links |
| `render-core:773` | term | `editor-ui/scene-view` | Picking's home is the Scene view by `book.md`; `gpu/readback-timing` teaches the one-pixel readback |
| `render-core:774` | term | `image/taa` | Jitter's home is the TAA page by `book.md` |
| `render-core:825`, `render-core:833` | open | `nowhere` | The surveyor's notes of files and tests not read in full |
| `render-core:835` | open | `nowhere` | The ImGui renderer is inventoried by the editor's UI (`editor-ui:40`, code `editor-ui:434` to `:437`) |
| `render-core:839` | open | `draw/mirrors-camera-relative` | Camera-relative rendering has no switch: that page's 100 km figure needs a diagram or an older build |
| `render-core:843` | open | `nowhere` | Release notes not read in full; `appendix/history` reads `Docs/Releases` itself |
| `render-core:847` | open | `nowhere` | A harmless double include of `Include/Common.slang`, left from the conversion; no page needs it |

## Not taken

none

## Questions for the planner

none
