# Brief: `gpu/vulkan-nvrhi`

| Field | Value |
| --- | --- |
| Title | Vulkan, NVRHI, the graphics device and the Renderer's services |
| Kind | I |
| Size | XL |
| Tracks | E |
| Needs | `basics/cpp-classes`, `basics/numbers`, `gpu/how-a-gpu-frame-works`, `core/layers-registries`, `core/platform` |
| From | render-core; the RHI layer (curricula gap); retitled; + render-core 1.2-1.3 (`GraphicsModule`, back-buffer capture, the `Renderer` hub, samplers, fallback textures) |
| Unit | `plan/allocation/gpu.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `device-lost` | Device lost | - |
| `immediate-command-list` | Immediate command list | - |
| `instance-vkinstance` | Instance (VkInstance) | - |
| `logical-device` | logical device | - |
| `moltenvk` | MoltenVK | - |
| `nvrhi` | NVRHI | - |
| `physical-device` | Physical device | - |
| `rhi` | RHI | - |
| `semaphore` | Semaphore | - |
| `srgb-formats` | sRGB formats | - |
| `surface` | Surface | - |
| `unorm` | UNORM | - |
| `validation-layer` | Validation layer | - |
| `vulkan` | Vulkan | - |
