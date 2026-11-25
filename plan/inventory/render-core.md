# Inventory: Renderer foundations (render-core)

Area key: `render-core`. Commit surveyed: `822a7a46` (main). Scope: the GPU and how Strata talks to it (NVRHI on
Vulkan), the device and swap chain, the process-wide `Renderer` services, command lists, uploads and staging, deferred
release, pipelines and binding layouts, bindless textures, textures and meshes as GPU resources, the geometry pool, the
frame of `SceneRenderer` pass by pass, the coordinate conventions, shaders (Slang sources, the build, the dialect),
readback, GPU timing, overlays, text and fonts.

Abbreviations used below: **DG** = `Docs/DeveloperGuide.md`, **ARCH** = `Docs/Architecture.md`, **AG** = `AGENTS.md`,
**RM** = `Docs/Roadmap.md`. "R/" = `Strata/src/Strata/Renderer/`, "PV/" = `Strata/src/Platform/Vulkan/`, "SH/" =
`Strata/shaders/`, "T/" = `StrataTests/src/`. Line numbers are at `822a7a46`.

Release mapping (from RM "Status" and `Docs/Releases/`): 0.3.0 holds waves 1-3 (first public release: NVRHI/Vulkan
device, bindless table, SDF text, budgeted upload queue and staging from wave 3's `mip-streaming`); 0.4.0 holds wave 4
(`gpu-driven-rendering`: GPU timers, geometry pool, camera-relative rendering, GPU culling; `game-ui`: `FontFace`,
`ShapeText`, shared atlases); 0.5.0 wave 5; 0.6.0 wave 6 (`render-quality`); 0.7.0 wave 7 (quality presets, sun
screen-space shadows); wave 8 is in progress, unreleased (0.8.0): the conversion of every shader from GLSL/glslang to
HLSL-syntax Slang. Where a document gives no release, the entry says "release not stated".

---

## 1. Features

### 1.1 The graphics device and presentation (Vulkan through NVRHI)

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| `GraphicsDevice` interface | Abstract device: owns the NVRHI device, swapchain, frames in flight, timestamps, queue transfers, error count, device-lost flag. No Vulkan header leaks out of it. | R/GraphicsDevice.h:128-199 | ARCH "Engine modules" Renderer paragraph (l.297); DG "Platform seams" (l.1086, table row "Graphics, present") | 0.3.0 (wave 1-3) |
| `GraphicsDeviceSpecification` | Name, validation on/off, headless, presentation window, `MaxFramesInFlight` (default 2, clamped 1-4), adapter index (-1 = best). | R/GraphicsDevice.h:17-30; PV/VulkanGraphicsDevice.cpp:269-283 | ARCH l.297 ("frames in flight, 2 by default") | release not stated |
| `GraphicsDeviceInfo` | Capabilities queried at start: BC compression, wireframe, extended storage formats, max 2D texture, bindless slots, timestamps + period, multi-draw indirect, first-instance, draw-count, max draw-indirect count, min/max samplers. | R/GraphicsDevice.h:32-65; filled in PV/VulkanGraphicsDevice.cpp:757-790 | DG "Batching" (l.4210, `MaxDrawIndirectCount`); DG "macOS and MoltenVK" (l.288) | grown per wave |
| `VulkanGraphicsDevice` | The only implementation: loads the Vulkan loader, creates instance (validation layer when asked and loadable), selects a physical device, creates the logical device and queues, wraps it in NVRHI (`nvrhi::vulkan::createDevice`), optionally NVRHI's validation layer (never in Dist). | PV/VulkanGraphicsDevice.cpp:266-472 (class), 486 `CreateInstance`, 614 `SelectPhysicalDevice`, 803 `CreateLogicalDevice`, 948-990 NVRHI creation | DG "Architecture rules"; ARCH l.297 | 0.3.0 |
| Device selection and requirements | Rejects GPUs below Vulkan 1.2, without swapchain (unless headless), dynamic rendering, synchronization2, timeline semaphores, descriptor indexing features, anisotropy, `imageCubeArray`, or a graphics+compute queue that can present; scores discrete (+1,000,000), integrated (+100,000) plus MiB of device-local memory; finds dedicated compute and transfer families. | PV/VulkanGraphicsDevice.cpp:614-801 (requirements 657-713, score 744-750) | Releases/0.3.0.md l.111 (Vulkan 1.2 driver required); DG "macOS and MoltenVK" | 0.3.0 |
| Swapchain | UNORM back buffer (B8G8R8A8 or R8G8B8A8, sRGB nonlinear colour space; the engine encodes sRGB itself), FIFO with vsync, else MAILBOX or IMMEDIATE, image count max(minImageCount + 1, frames in flight + 1), recreated on resize/out-of-date/suboptimal, none while minimized. | PV/VulkanGraphicsDevice.cpp:1032-1306 (format 1130-1150, present mode 1152-1164, count 1166) | ARCH "Application and frame loop" l.812-820 (vsync, FIFO, log line naming modes) | 0.3.0 |
| Deferred acquire wait | `BeginFrame` acquires the image but the GPU waits for it only at `PrepareBackBuffer` (an ALL_COMMANDS semaphore wait), so uploads and offscreen work never queue behind the display. | PV/VulkanGraphicsDevice.cpp:1438-1555 (`SubmitPendingAcquireWait` 1515-1528) | DG "Streaming and uploads" (l.6055); ARCH frame table l.778-803 | 0.4.0 (RM l.420: "the display's wait at the back buffer's first use counted as Present") |
| Frame pacing | A queue of event queries, one per submitted frame; `BeginFrame` waits for the oldest while `MaxFramesInFlight` are outstanding. | PV/VulkanGraphicsDevice.cpp:1444-1458, 1585-1601 | DG "Architecture rules" (NVRHI pitfalls, volatile buffers, l.958-983) | 0.3.0 |
| Present | Signals a present semaphore via an empty command list (NVRHI attaches queued signals to the next submission), `vkQueuePresentKHR`, `runGarbageCollection`, frame index++. | PV/VulkanGraphicsDevice.cpp:1557-1605 | ARCH l.781 | 0.3.0 |
| Device lost | `vk::SystemError` and `VK_ERROR_DEVICE_LOST` set `IsDeviceLost`; `GraphicsModule` then returns `EngineFrameAction::Close`. | PV/VulkanGraphicsDevice.cpp:1430-1436; R/GraphicsModule.cpp:72-74 | ARCH l.778, l.830 | release not stated |
| `VulkanPresentation` seam | What a window system gives the device: instance extensions, per-queue-family present support, surface creation; implemented by `Platform/GLFW`. A window that cannot present yields an offscreen device (`CanPresent` false). | PV/VulkanPresentation.h:16-29; PV/VulkanGraphicsDevice.cpp:272-282 | DG "Platform seams" l.1097-1103 | release not stated |
| `VulkanLoader` | Loads the platform's Vulkan loader once; same `vkGetInstanceProcAddr` for GLFW; install advice per OS for error messages. | PV/VulkanLoader.h, .cpp | DG "Platform seams"; T/Renderer/GraphicsDeviceTests.cpp:12 | release not stated |
| Bindless table sizing | Queries `vkGetDescriptorSetLayoutSupport`; halves the table down to 1,024 slots if refused, except on MoltenVK which under-reports. | PV/VulkanGraphicsDevice.cpp:992-1030; PV/VulkanBindlessSupport.h/.cpp | DG "macOS and MoltenVK" l.300-306 | 0.4.x-0.6 (release not stated) |
| Validation message classification | Debug-utils messages become errors (counted), warnings or trace; known false reports (MoltenVK blending report, the bindless support query, the loader's layer search) are demoted. | PV/VulkanDebugMessages.h/.cpp; PV/VulkanGraphicsDevice.cpp:108-133 | DG "macOS and MoltenVK"; DG "GPU tests" (l.431) | release not stated |
| NVRHI message callback | NVRHI's own errors are logged and counted into `GetErrorCount` (tests require zero). | PV/VulkanGraphicsDevice.cpp:86-106 | DG "GPU tests" | 0.3.0 |
| Memory budget | `VK_EXT_memory_budget` per device-local heap (or the heap size without it). | PV/VulkanGraphicsDevice.cpp:303-327 | ARCH "Streaming and residency" (other area) | release not stated |
| GPU timestamp pool | `GPUTimestampPool`: `Reset`, host `ResetCompleted` (vkResetQueryPool), `Write`, non-waiting `Read`, value mask for wrap. | R/GraphicsDevice.h:67-95; PV/VulkanGraphicsDevice.cpp:152-264 | DG "GPU timing" (l.6230) | 0.4.0 |
| Queue ownership transfer | `RecordQueueTransfer` (release on transfer queue, acquire on graphics) and `RecordBufferToTextureCopies` (copies from buffers, which NVRHI only does from staging textures). | R/GraphicsDevice.h:177-190; PV/VulkanGraphicsDevice.cpp:1335-1428 | DG "Streaming and uploads" | 0.3.0 (wave 3) |
| MoltenVK specifics | Missing features gated on device features, tight limits, bindless quirk, debug-build slowness. | (cross-cutting) | DG "macOS and MoltenVK" l.288-314 | release not stated |

### 1.2 The Graphics engine module and the frame

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| `GraphicsModule` | The `EngineModule` named "Graphics": creates the device (swapchain only with a window), `Renderer::Init`, begins frames (vsync, wait, `Renderer::BeginFrame`), presents, back-buffer captures, shuts both down last. Validation on by default in Debug only. | R/GraphicsModule.h:20-67; R/GraphicsModule.cpp:26-128 | ARCH "Application and frame loop" table l.737, frame list l.786-803 | wave 5-6 (engine modules), release not stated |
| Back-buffer capture | `RequestBackBufferCapture`: thread-safe, read with `Renderer::ReadTexture` at the end of the next frame, empty image when there is none. | R/GraphicsModule.cpp:100-128 | ARCH l.737, l.752-756 | release not stated |
| Programs' module lists | Editor (windowed, headless offscreen, `--no-gpu`), runtime (windowed, headless without Graphics). | (programs) | ARCH l.744-751 | release not stated |
| Frame order | Main-thread queue, input, events, `OnBeginFrame` (Graphics), layers' update, `OnRenderUI` (ImGui + `PrepareBackBuffer`), `OnEndFrame` (reverse: present). | Core/Application.cpp (other area) | ARCH l.786-803 | release not stated |

### 1.3 Process-wide renderer services (`Renderer`)

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| `Renderer` static service hub | Device, `ShaderLibrary`, samplers, fallback textures, `BindlessTextureTable`, `TextureTable`, `StagingPool`, `GPUUploadQueue`, `RendererUploadContext`, `DeferredReleaseQueue`, `GPUProfiler`, `GeometryPool`, `RenderSceneGPUCache`; destruction order encoded in `RendererData`. | R/Renderer.h:45-118; R/Renderer.cpp:17-168 | ARCH l.297-306 | 0.3.0, grown |
| Common samplers | Linear clamp, linear wrap, anisotropic (16x) wrap, point clamp. | R/Renderer.cpp:92-101, 312-315 | (none specific) | 0.3.0 |
| Fallback textures | 1x1 white, black, flat normal (exact half floats, with the reason), black cube, black cube array, 64x64 blue noise, black 3D, zero R32_UINT 3D. | R/Renderer.cpp:52-131 | DG "Scene renderer and lighting" (fallbacks implied); comment at R/Renderer.cpp:107-111 | grown per wave |
| `Renderer::BeginFrame` | Profiler, geometry pool, scene GPU cache, bindless and texture table recycling, staging, upload queue roll, deferred releases within budget. | R/Renderer.cpp:267-282 | DG "Streaming and uploads" | 0.3.0, grown |
| `Renderer::PrepareBackBuffer` | First call of a frame: triggers the device's acquire wait (timed as the `Present` stage) and clears the back buffer black. | R/Renderer.cpp:289-310 | AG "Rendering" (first bullet); DG "Streaming and uploads" | 0.4.0 |
| `Renderer::ReadTexture` | Blocking readback of one subresource (tests, tools, screenshots). | R/Renderer.cpp:325-342 | DG "Readback, the game renderer and tests" (l.6214) | 0.3.0 |
| Frame number | `GetFrameNumber`: frames begun, how renderers tell whether they rendered last frame. | R/Renderer.cpp:284-287 | (none) | release not stated |

### 1.4 Command lists, synchronisation and lifetime

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| NVRHI command lists | Recorded with `open`/`close`, executed with `executeCommandList`; immediate by default; non-immediate lists for those that may open while another is open (upload batch's transfer list, geometry pool growth). | used everywhere; rule in DG | DG "Architecture rules" NVRHI pitfalls (l.958-983) | 0.3.0 |
| Automatic and explicit barriers | NVRHI tracks resource states and places barriers when binding sets change; same-set UAV read-after-write needs `setBufferState`/`setTextureState(UnorderedAccess)` + `commitBarriers()`; whole-texture first transition for compute-written levels. | e.g. `SceneRenderer::CreateEnvironmentMaps` (R/SceneRenderer.cpp:727) | DG l.958-972 | 0.3.0 + later fixes |
| `DeferredReleaseQueue` | Holds resources until an event query set at release completes, then destroys them within 0.25 ms per frame (`c_FrameDestroyBudget`), oldest first; also frees as many as each release hands over, so it works without frames. | R/DeferredReleaseQueue.h:16-73; .cpp:14-76 | DG l.966-970; ARCH l.301-306 | release not stated (render target release fix) |
| `Renderer::ReleaseDeferred` | The entry point; used when `SceneRenderer` is resized or freed. | R/Renderer.cpp:261-265; R/SceneRenderer.cpp:2214-2343 | AG "NVRHI pitfalls"; DG l.966 | as above |
| Volatile constant buffer pacing | `SceneRenderer::ReserveFrameConstantVersions`: an event query per submitted frame; waits for the oldest only if the next frame's writes (`c_MaxFrameConstantWrites`) would find no free version; poll after wait (NVRHI Vulkan quirk). | R/SceneRenderer.cpp:1457-1512 | DG l.976-983 | release not stated |
| Event queries | `createEventQuery`/`setEventQuery`/`pollEventQuery`: the engine's universal "has the GPU got here?" primitive (deferred release, staging, uploads, readback, profiler, bindless recycling by frame). | many | DG "Streaming and uploads" | 0.3.0 |

### 1.5 Uploads and staging

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| `GPUUploadQueue` | Every asset upload: textures in runs of rows or stacked small levels, meshes in buffer ranges, through staging; batches with tickets (`GetTicket`, `IsComplete`, `WaitForTicket`); scene-data uploads (`RecordSceneUpload`, 16 MiB staging steps); GPU-side level copies; per-frame statistics; optional transfer queue. | R/GPUUploadQueue.h:94-273; .cpp (646 lines) | DG "Streaming and uploads" l.6055-6070; ARCH "Streaming and residency" (l.1832) | 0.3.0 (wave 3 `mip-streaming`) |
| `PlanStep` | Sizes a step to bytes and time left in the frame and before the deadline at the measured speed, rounded to granules, at least one granule for the frame's first step; accounts for staging creation cost. | R/GPUUploadQueue.cpp:228-277 | DG "Streaming and uploads"; AG "Asset pipeline" (`c_AssetUploadStepBytes`) | 0.3.0, refined later |
| Transfer queue uploads (off by default) | Uploads the managers may wait for run on a dedicated transfer queue with ownership transfers; off because it measured no faster and used more memory. | R/Renderer.h:33-41; R/GPUUploadQueue.h:45-50, 125-131, 186-190 | DG "Streaming and uploads"; RM wave 3 | 0.3.0 |
| `StagingPool` | CPU-writable buffers in powers of two (from 64 KiB), reused once the GPU ran their copies (`FenceReleased` per batch, `BeginFrame` per frame), idle up to 16 MiB, all released after 120 idle frames, pending capped at 256 MiB, budgeted with `HasRoomFor`. | R/StagingPool.h:11-141 | DG "Streaming and uploads"; ARCH l.301 | 0.3.0 |
| `RendererUploadContext` and `IAssetGraphics` | The asset layer's upload batches are the queue's batches, reached through an engine service so the asset layer never includes NVRHI. | R/RendererUploadContext.h; R/RendererRegistration.cpp:60-63 | ARCH "Layers" l.611-617 | 0.3.0 (wave 3: "Remove NVRHI from the asset layer") |

### 1.6 Pipelines, binding layouts and bindless textures

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| Scene pipelines by key | `PipelineKey {Pass, DoubleSided, Mirrored, Skinned, Velocity, Surface}` -> cached `IGraphicsPipeline`; vertex shader picked by pass and key, input layout by vertex shader, pixel shader by pass, culling and winding, reversed-Z depth function per pass, shadow depth bias, transparent blending into alpha-as-transmittance. | R/SceneRenderer.cpp:2424-2527; R/SceneRenderer.h:1094-1119 | AG "Renderer conventions"; DG "Batching" (l.4246, buckets by `PipelineKey`) | 0.3.0, grown |
| Fullscreen pipelines | Cached per framebuffer info; shared fullscreen triangle vertex shader. | R/SceneRenderer.cpp:2529-2556; SH/PostProcess/Fullscreen.vert.slang | AG "Renderer conventions" (fullscreen UVs) | 0.3.0 |
| Compute pipelines | `SceneRenderer::CreateComputePipeline(shader, layout)`. | R/SceneRenderer.cpp:226 | (none) | 0.3.0 |
| Scene binding layout | One layout shared by scene passes: volatile CB 0 (`FrameConstants`), SRVs 0-21, 27-29, 32-40, 54..., samplers 0-5, 8-10; documented slot ledger in `Include/Scene.slang`; a pass that does not run binds a dummy. | R/SceneRenderer.cpp:357-404; SH/Include/Scene.slang:7-16 | DG "GPU timing" (l.6246-6250, slot assignment rule) | grown per wave |
| Push constants | `[[vk::push_constant]] ConstantBuffer<T>`, slot only in C++ `BindingLayoutItem::PushConstants`; must not collide with another layout's CB slot (shadow push layout). | R/SceneRenderer.cpp:406+ (`m_ShadowPushLayout`) | AG "Shaders"; DG "Shaders" item 3 (l.3891-3895) | wave 8 (Slang) form |
| Scene vertex layouts | Four input layouts, each exactly what its vertex shaders read; pipeline layout chosen by vertex shader name; a test checks every scene vertex shader reads exactly its layout's locations. | R/SceneVertexLayouts.h:23-89; R/SceneRenderer.cpp:341-353 | DG "Shaders" item 6 (l.3918-3925) | release not stated |
| `BindlessTextureTable` | One update-after-bind descriptor array of sampled 2D textures (up to 32,768 slots, grows from 1,024 by doubling); reserved slots 0-2 (white, black, flat normal); slot recycled only `framesInFlight + 1` frames after release; replacing a texture = new slot. | R/BindlessTextureTable.h:14-79; .cpp:7-108 | ARCH l.300; DG "macOS and MoltenVK" | 0.3.0 |
| `TextureTable` | Stable per-texture index -> packed entry (bindless slot 0-23, sampler 24-30, grayscale bit 31) plus a minimum LOD for fade-in; material data stores indices, so streaming changes no material. | R/TextureTable.h:11-137 | DG "Render scene" (l.4204-4208); AG "Asset pipeline" (bindless slots resolved every frame) | 0.4.0 (RM l.422: "a stable texture table") |
| Bindless in shaders | `Texture2D<float4> u_Textures[] : register(t0, space1)`, read with `NonUniformResourceIndex`; entries via `u_TextureTable` (t16) through `SampleMaterialTexture`. | SH/Include/Scene.slang:338-345; SH/Include/MaterialTextures.slang | DG "Shaders" item 2 | 0.3.0 |

### 1.7 Textures and meshes as GPU resources; the geometry pool

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| `Texture` asset (GPU side) | CPU mip chain + GPU texture + bindless slot + table index; `FinalizeOnMainThread` uploads smallest level first in planned steps; partial residency (mip tail) and level changes by swapping textures (streaming belongs to the streaming area). | R/Texture.h (274 lines) | DG "Textures" (l.1756), "Mip streaming" (l.1827) | 0.3.0 |
| Block-compression support flag | Device without BC sampling: loaders decode on workers. | R/Renderer.cpp:165-166; R/RendererRegistration.cpp:70-77 | DG "Textures" | 0.3.0 |
| `Mesh` asset (GPU side) | Positions (stream 0, 12 B), attributes (stream 1, 36 B: normal, tangent with sign, UV), skin stream (16 B); submeshes with LODs (`MeshLOD::Error`); CCW front faces; uploads through the queue into the pool; CPU keeps positions and indices for physics. | R/Mesh.h:14-160 | DG "Batching" (geometry pool bullet, l.4229-4241); ARCH l.344-348 | 0.3.0; cooked v3 in 0.4.0 |
| `GeometryPool` | Shared buffers: Static and Skinned vertex arenas (positions, attributes, skin), one 32-bit index arena; `RangeAllocator` offsets; stable `GeometryHandle`; deferred frees; growth by GPU copy; compaction within 8 MiB/frame above 25% scattered free space; GPU-culling tables (entries, submeshes, LODs). | R/GeometryPool.h:17-289; .cpp (638 lines) | DG "Batching" l.4229-4245 | 0.4.0 (RM l.1239, Releases/0.4.0.md l.45) |
| `MeshGeometryRegistry` reader | The renderer registers how to read a `Mesh`'s full-detail triangles so physics never includes the renderer. | R/RendererRegistration.cpp:31-56, 87-88 | ARCH l.357-362 | release not stated |
| `MeshFactory` | Procedural primitives (cube, sphere, plane, quad, cylinder, capsule, cone, torus), CCW, registered as built-in assets. | R/MeshFactory.h; R/RendererRegistration.cpp:120-129 | ARCH l.348 | 0.3.0 |

### 1.8 Shaders: sources, build, embedding, dialect

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| Shader source tree | `SH/` folders: `Include/` (39 include files), `Scene/` (16), `PostProcess/` (20), `Effects/` (10), `IBL/` (12), `GI/` (12), `Overlay/` (10), `Debug/` (5), `GameUI/` (3), `ImGui.*`. | SH/ | DG "Shaders" item 1 (l.3862-3866) | wave 8 (Slang); before: GLSL |
| Shader entry list | `strata_add_shaders(Strata_Renderer ...)`: 89 registered stage files plus 25 VARIANTS (same source, extra defines), 114 entries; `INVARIANT_POSITION Scene/Mesh.vert`. | Strata/CMakeLists.txt:79-205 | AG "Shaders"; DG "Shaders" item 4 | wave 8 |
| Build pipeline | slangc -> `<name>.raw.spv` (SPIRV-Tools validated) -> `StrataShaderTool` (checks, invariant decoration) -> `<name>.spv` + `<name>.h`; generated `EmbeddedShaderRegistry.cpp`; `ShaderEntries.txt` manifest; every entry depends on every include. | CMake/StrataShaders.cmake:1-226; CMake/StrataShaderTool/ | DG "Shaders" item 4 (l.3897-3911) | wave 8 |
| slangc flags | `-target spirv -profile spirv_1_5 -matrix-layout-column-major -fvk-{t,s,b,u}-shift 0/128/256/384 -default-image-format-unknown -warnings-disable 39001,41012` (+ warnings as errors); each flag's reason, and the flags not passed. | CMake/StrataShaders.cmake:64-85 | DG "Shaders" item 4 | wave 8 |
| Slang pin | Slang 2026.20 archives by SHA-256, per-user cache, `STRATA_SLANG_ROOT` offline. | CMake/StrataSlang.cmake | DG "Shaders" item 5 (l.3912-3924); AG "Working with third-party code" | wave 8 |
| `StrataShaderTool` | Host tool (standard library only): SPIR-V framing checks, `Invariant` decoration of `SV_Position`, header writer (8 words per line). | CMake/StrataShaderTool/*.cpp | DG "Shaders" item 4; T/Renderer/ShaderToolTests.cpp | wave 8 (invariant patch) |
| `EmbeddedShaders` / `ShaderLibrary` | Registry lookup by registered name; stage from suffix (.vert/.frag/.comp/.geom); entry `main`; thread-safe cache; `SetUnavailable` for fallback tests. | R/EmbeddedShaders.h; R/ShaderLibrary.h/.cpp | ARCH l.298-300 | 0.3.0 (embedded since then) |
| `Include/Common.slang` | Register convention comment, constants, `NDCToUV`/`UVToNDC`, sRGB transfer, interleaved gradient noise, `SanitizeHDR`, GLSL-conversion globals `st_*`, `TextureSize`/`TexelFetch` helpers, `UnsignedMultiplyExtended`, `PackHalf2x16`/`UnpackHalf2x16` (the only `__target_switch`/`spirv_asm`). | SH/Include/Common.slang:1-217 | DG "Shaders" items 1-2 | wave 8 |
| `Include/Scene.slang` | Scene layout ledger, material/instance/light flags, `FrameConstants`, `InstanceData`, draw list, LOD fade test, skinning, `TransformPositionRelative`, `TransformNormal`, `MaterialData`, `LightData`, samplers, IBL, bindless, texture table, cascades, octahedral normals. | SH/Include/Scene.slang:1-379 | DG "Batching", "Camera-relative space", "GPU timing" | 0.3.0, grown |
| Dialect rules | `mul` only with a matrix, `all()/any()`, row constructors, `select` order, `Interlocked*` out params, `SampleLevel`/`Load` in compute, `[vk::image_format]`, `NonUniformResourceIndex`, `SV_VulkanVertexID/InstanceID`, `precise`, no generics/modules/interfaces, stage inputs as parameters, derivatives before discard. | (rules) | DG "Shaders" item 2 (l.3867-3889); AG "Shaders" | wave 8 |
| Shader checks | `Architecture.Shaders` (sources), `Renderer.ShaderModules` (SPIR-V 1.5, entry `main`, capabilities allow-list, invariant positions, no double-bound slots, vertex inputs match layouts), `Renderer.ShaderTool`, `GPU.Renderer` (validation accepts every module), CI `StrataShaders.TargetHLSL`, Linux `spirv-val`, macOS Metal conversion with known failures. | T/Architecture/ShaderSourceTests.cpp:276+; T/Renderer/ShaderModuleTests.cpp:242-371; T/Renderer/ShaderToolTests.cpp; T/Renderer/GPURendererTests.cpp:445 | DG "Shaders" item 6 (l.3918-3938) | wave 8 |
| Conversion-slip diagnosis | Look-dev capture + signed compare against 0.7.0's set. | Tools/LookDev.py | DG "Shaders" item 7 (l.3939-3946); DG "Look-dev harness" (l.666) | wave 8 |
| Other targets | `slangc -target hlsl` succeeds for every entry; what a D3D target would still need. | (CI) | DG "Shaders" item 8 (l.3947-3952) | wave 8 |

### 1.9 Coordinate conventions

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| D3D-style clip space via NVRHI | NDC +Y up, framebuffer row 0 at top, depth [0, 1]; NVRHI flips the Vulkan viewport (so `-fvk-invert-y` is not passed). | SH/Include/Common.slang:13-23; CMake/StrataShaders.cmake:76-77 | AG "Renderer conventions"; Math/Math.h:8-10 | 0.3.0 |
| Reversed-Z | Near -> depth 1, far/infinity -> 0; `PerspectiveReverseZ` (swap near/far), `PerspectiveReverseZInfinite`, `OrthographicReverseZ`; depth cleared to 0; depth tests `GreaterOrEqual`; sky drawn at depth 0. | Strata/src/Strata/Math/Math.h:23-28; Math/Math.cpp:70-91; R/SceneRenderer.cpp:2470-2512, 3415-3420, 3505-3512 | AG "Renderer conventions" | 0.3.0 |
| Fullscreen UVs | `uv = (ndc.x*0.5+0.5, 0.5-ndc.y*0.5)`; the fullscreen triangle from `SV_VulkanVertexID`. | SH/Include/Common.slang:15-23; SH/PostProcess/Fullscreen.vert.slang:8-13 | AG "Renderer conventions" | 0.3.0 |
| Front faces CCW (glTF) | Pipelines `setFrontCounterClockwise(!Mirrored)`; mirrored instances (negative determinant) get clockwise pipelines and flipped tangent handedness. | R/SceneRenderer.cpp:2462-2467; SH/Scene/Mesh.vert.slang:53-56; SH/Include/Scene.slang:251-260 | AG "Rendering" (mirrored); DG "Lights, shadows and HDR" l.4544-4547 | 0.3.0 / mirrored later |
| Right-handed, +Y up, -Z forward | Engine-wide math convention. | Math/Math.h:8-10 | (Math area) | 0.3.0 |
| Camera-relative space | Rotation-only view matrices (`GetRelativeView`), vertex shader subtracts camera from instance translation first, CPU uploads positions relative to the camera computed in double; `InstanceData` stays world space; tested at 20 and 100 km. | R/SceneRenderer.cpp:2830-2833, 3096-3100; SH/Include/Scene.slang:238-245; T/Renderer/GPUSceneCameraRelativeTests.cpp:74-115 | DG "Camera-relative space" (l.4334-4347); ARCH l.2549-2555; AG "Rendering" | 0.4.0 |
| Matrices column-major | glm's bytes: `-matrix-layout-column-major`; `floatNxN(...)` takes rows; `mul(M, v)`. | CMake/StrataShaders.cmake:66, 81 | DG "Shaders" item 2, 4 | wave 8 |
| GPU struct layouts | std140 for constant buffers, std430 for structured buffers, mirrored by C++ structs with `static_assert`ed sizes (`FrameConstants` 8x64+27x16, `InstanceData` 64, `MaterialData` 144, `LightData` 64...). | R/SceneRenderData.h:113-259; R/GPUSceneData.h | DG "Shaders" item 3; SH/Include/Scene.slang:4-5 | 0.3.0 |

### 1.10 The frame of `SceneRenderer` (pass order)

`SceneRenderer::Render` -> `RenderFrame` (R/SceneRenderer.cpp:2901-3735). The order below is the code's; the bracket
names the GPU stage the pass is timed in (`RendererGPUStages`, R/GPUProfiler.h:13-37). Features of passes beyond the
foundations (lighting, shadows, AO, reflections, GI, post-processing, TAA) belong to other areas; the foundations
chapter must teach the order and the plumbing.

| # | Step | Where (R/SceneRenderer.cpp unless noted) | Stage |
| --- | --- | --- | --- |
| 0 | Resolve GPU stats of earlier frames; validate viewport, targets, target framebuffer | 2903-2919 | CPU |
| 1 | `RenderScene::Sync` and extraction prep (`Render.Extract` CPU stage) | 2921-2941 | CPU |
| 2 | Render scene's GPU mirror update (`RenderSceneGPU::Update`) | 2944-2959 | (own list) |
| 3 | Lights collected, assets resolved (`ResolveAssets`), local shadow data, draw arguments built (`BuildDrawArguments`), frame constants filled (relative view, jittered projection) | 2960-3284 (e.g. 3096-3100, 3203-3220) | CPU |
| 4 | `ReserveFrameConstantVersions`, open command list, `GPUPassTimer` starts | 3283-3289 | GPU.Setup |
| 5 | Motion history growth, environment (IBL / procedural sky / atmosphere tables), height fog, aerial perspective setup, texture table uploads, geometry tables | 3290-3358 | GPU.Setup |
| 6 | GPU culling (`RunGPUCulling`) on the GPU-driven path | 3360-3363 | GPU.Cull |
| 7 | Light culling (GPU) and light clusters | 3365-3378 | GPU.Cull |
| 8 | Aerial perspective volume (atmosphere skies) | 3380-3386 | GPU.Aerial |
| 9 | Sun cascades (fit, draw, ranges) and local light shadows | 3388-3413 | GPU.Shadows |
| 10 | Clears (depth to 0, normals, entity IDs), depth/normal/entity-ID prepass (two phases on the GPU path, with cull readback) | 3415-3443 | GPU.Prepass |
| 11 | Sun screen-space shadow mask | 3445-3450 | GPU.ScreenShadows |
| 12 | Ambient occlusion (GTAO + denoise) | 3454-3459 | GPU.AO |
| 13 | Global illumination voxelization (when wanted) | 3461-3477 | GPU.RadianceCascades |
| 14 | Reflection probes' conversions and screen-space reflection trace | 3479-3487 | GPU.Reflections |
| 15 | Opaque forward pass (EQUAL depth test) | 3489-3495 | GPU.Opaque |
| 16 | Sky (fullscreen triangle at depth 0, `GreaterOrEqual`) | 3497-3522 | GPU.Opaque |
| 17 | Scene colour copy (glass, next frame's spatial reflections) then transparent pass (glass first, then blended back to front) | 3524-3541 | GPU.Transparent |
| 18 | Motion history copy and TAA resolve | 3543-3566 | GPU.TAA |
| 19 | Depth of field | ~3588-3597 | GPU.DepthOfField |
| 20 | Motion blur | ~3598-3606 | GPU.MotionBlur |
| 21 | Exposure, bloom, lens flares (`RenderPostHDR`), colour lookup, tone mapping + FXAA/SMAA-style morphological AA (`RenderPostDisplay`) | 3608-3680; R/SceneRendererPost.cpp | GPU.Post |
| 22 | Overlays: GI debug views, lighting view, entity tints, motion view, grid, outline, debug lines, text, overlay passes (game UI); copy into an external target | 3682-3730; `RenderOverlays` 4006-4222 | GPU.Overlays (GPU.UI inside) |
| 23 | Close and execute (`ExecuteFrame` sets the constants' event query) | 3732-3733; 1484-1504 | - |

Related renderer-level features: `SceneRenderer` API (output, HDR, depth, normal, entity-ID, AO and many debug textures),
`SetViewportSize` (validates against `MaxTextureDimension2D`, releases through `ReleaseDeferred`), `SetQuality`,
`GetStats`/`GetGPUStats`/`ResolveGPUStats`, `ResetExposureAdaptation`, `ResetHistory`, temporal jitter (Halton 2,3, 8
phases), output target rules (non-sRGB UNORM, same size; R/SceneRenderer.h:837-848), output texture created lazily, the
`SceneRenderOptions` editor knobs (`PreviewEnvironment`, `DrawScreenSpaceText`, overlays) - R/SceneRenderer.h:816-1046;
DG "Scene renderer and lighting" (l.3955-4007); ARCH l.307-331.

File split of the frame: `SceneRenderer.cpp` (frame and shared), `SceneRendererPost.cpp`, `...AmbientOcclusion.cpp`,
`...LightingView.cpp`, `...Glass.cpp`, `...ScreenShadows.cpp`, `...ShadowView.cpp`, `...ScreenReflections.cpp`,
`...ReflectionProbes.cpp`, `...Atmosphere.cpp`, `...LocalShadows.cpp`, `...Extraction.cpp`, `...GPUDriven.cpp`,
`...GlobalIllumination.cpp` - members all declared in `SceneRenderer.h` (2,853 lines) grouped by file comment
(DG l.3981-3992).

`GameRenderer` (Strata/src/Strata/Runtime/) draws a game into the back buffer at the project's quality without an
entity-ID buffer (DG l.6220-6224) - runtime area, mentioned here because it is the simplest real caller of
`SceneRenderer::Render(scene, camera, backBufferFramebuffer)`.

### 1.11 Readback

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| `TextureReadback` | Non-blocking region copy into a staging texture + event query; `IsReady` polled once per frame; refuses BC, depth-stencil, MSAA, 3D, out-of-range regions (overflow-safe check). | R/TextureReadback.h; .cpp:7-74 | DG "Readback..." (l.6216-6219); AG "Rendering" | 0.3.0 |
| `BufferReadback` | Reusable buffer range readback (Record, Submit, IsReady, Read). | R/BufferReadback.h | (used by culling counters, exposure) | 0.4.0 (release not stated) |
| Picking | `ReadEntityIDAsync(x, y)` -> R32_UINT pixel -> `GetEntityFromID`; `GetEntityAt` blocking; renderers with `EntityIDs` off pick nothing. | R/SceneRenderer.h:965-978; R/SceneRenderer.cpp:4224-4266 | DG l.6218-6219 | 0.3.0 |
| `ImageWriter` / `ImageReader` | PNG encode of readback images (8-bit RGBA/BGRA, UNORM/sRGB), small image decode. | R/ImageWriter.h, R/ImageReader.h | ARCH l.350-351 | 0.3.0 |

### 1.12 GPU timing

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| `GPUProfiler` | Ring of `MaxFramesInFlight + 2` slots of 256 timestamps; host resets; resolves completed slots 2-3 frames late into `FrameProfiler::RecordGPUFrame`; drops instead of waiting. | R/GPUProfiler.h:63-160; .cpp | DG "GPU timing" (l.6230-6259); ARCH "Frame profiler" (l.860, GPU stages ~l.903-945) | 0.4.0 |
| `GPUPassTimer` | One timestamp per pass boundary: constructor (first pass), `Next(stage)`, `End()`/destructor; intervals added only within one slot. | R/GPUProfiler.h:162-205; .cpp:352-394 | DG "GPU timing" | 0.4.0 |
| `RendererGPUStages` | 17 stages registered in frame order (Uploads, Setup, Aerial, Cull, Shadows, Prepass, ScreenShadows, AO, RadianceCascades, Reflections, Opaque, Transparent, TAA, MotionBlur, DepthOfField, Post, Overlays) + GPU.UI by GameUI, GPU.ImGui at first use. | R/GPUProfiler.h:13-37; R/RendererRegistration.cpp:64-65 | DG l.6236-6252; ARCH stage table | 0.4.0, stages added per wave |
| `GPUTimerRecord` / `GetGPUStats` | A renderer's own GPU times; `ResolveGPUStats(true)` for tests. | R/GPUProfiler.h:46-58; R/SceneRenderer.h:1028-1033 | DG l.6255-6256 | 0.4.0 |
| Present stage | The back buffer's first preparation is timed as `Present`, outside the work time. | R/Renderer.cpp:296-298 | ARCH Frame profiler table row `Present`; T/Renderer/GPUTimerTests.cpp:466 | 0.4.0 |

### 1.13 Overlays and debug drawing

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| Overlay set | After post-processing, exact display colours into the output texture: entity tints, motion view, grid, selection outline (entity IDs, or a selection mask with TAA), debug lines (tested/on top), text, overlay passes; jitter-free constants with TAA and a one-pixel depth bias for scene-placed overlays. | R/SceneRenderer.cpp:3752-4222; SH/Overlay/*.slang | DG "Overlays" (l.6141-6175) | 0.3.0, grown |
| `DebugDraw` | Immediate-mode line lists (two depth modes; boxes, spheres, circles from tables, arrows, cones, capsules, frustums), packed sRGB colours. | R/DebugDraw.h/.cpp | DG "Overlays" | 0.3.0 |
| `DrawSceneGizmos` | Gizmos of lights, cameras, colliders (through `ComponentInfoBuilder::Gizmo`), view-culled, icons below a pixel size. | R/SceneGizmos.h/.cpp | DG "Overlays" | 0.3.0, view-culling later |
| `ISceneOverlayPass` / `SceneOverlayRegistry` / `SceneOverlayFrame` | How a higher module (GameUI) draws over every renderer's image without the renderer naming it; frame data (camera-relative view-projection, jitter flag, command list, atlases, GPU timer). | R/SceneOverlay.h:15-136 | DG "Overlays"; AG "Game UI" (renderer reaches the UI only through `SceneOverlayRegistry`) | 0.4.0 |
| `SceneScreenView` | Where the game's screen lies in the image (editor 2D canvas zoom/pan). | R/SceneOverlay.h:15-33 | DG "Game UI" (other area) | 0.4.0 |
| `SetJitteredDepthBias` | Depth bias for overlays against jittered depth. | R/SceneOverlay.h:79-86 | DG "Overlays" | 0.7.0? (TAA), release not stated |
| LOD selection as pure functions | `LODSelection` so tools show the drawn LOD; CPU/GPU agreement with `precise`. | R/LODSelection.h/.cpp; SH/Include/LODSelection.slang | DG "Overlays" LOD bullet (l.6168-6175) | 0.4.0 |

### 1.14 Text and fonts

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| `Font` asset | TrueType (`.ttf`, first font of `.ttc`), validated at create; default Roboto Medium embedded (`strata_embed_file`). | R/Font.h; Strata/CMakeLists.txt:207-208 | DG "Text and fonts" (l.6177-6212) | 0.3.0 |
| Font validation | `ValidateTrueTypeFont`: every table stb_truetype reads, glyph outlines, composites (depth 8, 256 components), limits (64 MiB, 16M points), kerning disabled when unbounded, CFF rejected, cmap format-4 search fix. | R/FontValidation.h:9-71; .cpp (789 lines) | DG "Text and fonts" bullet 4; AG "Rendering" (font files untrusted) | 0.3.x-0.4 (release not stated) |
| `FontFace` | Glyph metrics without rasterizing: code point -> glyph, advance, kerning, vertical metrics, plane bounds, distance-field size and cost; caches bounded at 4,096. | R/FontFace.h | DG "Text and fonts" bullet 2 | 0.4.0 (game-ui) |
| `ShapeText` / `LayoutText` / `MeasureCaretStops` / `DecodeUTF8` | Layout: alignment, wrap after spaces/hyphens and inside long words, line spacing, vertical alignment, truncation with ellipsis (U+2026 or "..."); UTF-8 decoding with U+FFFD. | R/TextLayout.h/.cpp | DG "Text and fonts" bullet 2 | 0.3.0 (LayoutText), 0.4.0 (ShapeText) |
| `FontAtlas` | SDF atlas per font: 512x512 pages of 42-texel cells in a texture array, up to 8 pages, LRU eviction never of this frame's glyphs, dirty-row uploads in bands of 64 rows, per-frame raster budget, reduced resolution for costly glyphs. | R/FontAtlas.h/.cpp | DG "Text and fonts" bullet 4 | 0.3.0, bounded later |
| `FontAtlasCache` | One atlas per font per renderer, shared by text and the game UI, one raster budget lent between passes, unused atlases dropped at frame start. | R/FontAtlasCache.h/.cpp | DG "Text and fonts" bullet 3 | 0.4.0 |
| `TextRenderer` | Draws `TextComponent`s: world-space (entity XY plane, depth-tested) and screen-space (HUD over everything); `c_FrameRasterBudget = {32 glyphs, 512 Ki cost}`. | R/TextRenderer.h/.cpp; SH/Overlay/Text.vert/.frag.slang; SH/Include/SDFText.slang | DG "Text and fonts" bullet 1 | 0.3.0 |
| SDF coverage in the shader | `SDFCoverage`: smoothstep over ~one screen pixel via `fwidth`, before the discard. | SH/Include/SDFText.slang:9-15; SH/Overlay/Text.frag.slang:17-26 | DG "Lights, shadows and HDR" (derivatives before discard) | 0.3.0 |

### 1.15 Module registration and data plumbing owned by the renderer

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| `RegisterRendererModule` | Components, `IAssetGraphics` service, GPU stages, render-scene copier, `Renderer.Quality` settings section, loaders (Texture with prefix loads, Mesh, Material, Font, ColorLookup), `TextureStreamer` extension, mesh geometry reader, built-in assets (default material, 8 primitives). | R/RendererRegistration.cpp:58-130 | ARCH "Composition root and registries" (l.619-714, row l.638) | wave 1 (module-foundation) |
| Registered asset types (this area) | Texture, Mesh, Font (Material, ColorLookup belong to the materials/post areas). | R/RendererRegistration.cpp:70-117 | DG "Adding an asset type" (l.1801) | 0.3.0 |
| Registered components (this area) | `TextComponent` (text); `MeshRendererComponent` (registered by the renderer, used by physics/animation). Lights, sky, post-process, fog etc. belong to other areas. | R/RendererComponents.h/.cpp | ARCH l.266-272 | 0.3.0 |

### 1.16 Headers of R/ that belong to other areas (accounted for, not inventoried here)

Render scene, culling and batching (`RenderScene`, `RenderSceneGPU`, `SpatialIndex`, `AssetResolveCache`,
`SceneDrawKey`, `GPUSceneData.h` beyond the geometry tables, `SceneRendererExtraction.cpp`, `SceneRendererGPUDriven.cpp`,
`RenderLights`); lighting and shadows (`ShadowCascades`, `ShadowView`, `ShadowAtlasAllocator`, `SceneRendererScreenShadows`,
`...LocalShadows`, `...ShadowView`, `...LightingView`, `BlueNoise.h`); materials (`Material`, `MaterialData`); sky and
atmosphere (`Atmosphere`, `SkyPresets`, `SceneRendererAtmosphere`); post-processing (`PostProcessData`, `PostProcessMath`,
`FilmicConstants.h`, `WhiteBalanceLocus.inl`, `MorphologicalAreaTable.inl`, `ColorLookup`, `SceneRendererPost`);
AO (`AmbientOcclusionFit.h`, `SceneRendererAmbientOcclusion`); reflections (`SceneRendererReflectionProbes`,
`...ScreenReflections`, `...Glass`); GI (`GlobalIlluminationLayout`, `VoxelClipmap`, `SceneRendererGlobalIllumination`);
quality (`RendererQuality`); texture streaming and cooking (`TextureStreamer`, `CookedTexture`, `TextureFormat`,
`BlockCompression`, `BC7Format`). `LODSelection` is shared with the render-scene area.

### How completeness was checked

- Every file of `Strata/src/Strata/Renderer/` (127 files, listed with `ls`) is either inventoried above (1.1-1.15) or
  assigned to another area in 1.16.
- Every file of `Strata/src/Platform/Vulkan/` (8 files) is inventoried in 1.1.
- Every shader folder of `Strata/shaders/` is named in 1.8; the entry count (89 + 25 variants = 114) was counted from
  `strata_add_shaders` in `Strata/CMakeLists.txt`. Individual post, lighting, GI and reflection shaders are left to
  their areas; this area owns `Include/Common.slang`, `Include/Scene.slang` (plumbing parts), `Include/SDFText.slang`,
  `Scene/Mesh.vert`, `PostProcess/Fullscreen.vert`, `PostProcess/Copy.frag`, `Debug/ColorTriangle.*`, `Overlay/*`,
  `ImGui.*` (with the ImGui area).
- Every `RendererGPUStages` member is listed in 1.12; every step of `RenderFrame` that opens a GPU stage is in 1.10.
- Registered items: asset loaders and built-in assets from `RegisterRendererModule` (1.15); no editor command and no
  host function belongs to this area (the viewport capture and `editor.perf` commands, which expose its data, belong to
  the editor/automation area). Settings section `Renderer.Quality` belongs to the quality area.
- DG headings under "Rendering" read in full for this area: Shaders, Scene renderer and lighting, Render scene,
  Batching, GPU-driven path (first bullet), Camera-relative space, Streaming and uploads, Overlays, Text and fonts,
  Readback, GPU timing; plus Architecture rules (NVRHI pitfalls), Platform seams, macOS and MoltenVK, GPU tests.

---

## 2. Concepts to teach (dependency order)

Each entry: the problem, the approaches engines use, what Strata does and why, and the newcomer's usual mistake.

1. **What a GPU is and why an engine talks to it through commands.** Problem: the CPU and GPU are separate processors
   with separate memory running asynchronously. Approaches: immediate-mode APIs (OpenGL, D3D11) hide the asynchrony;
   explicit APIs (Vulkan, D3D12, Metal) make the program record command buffers and synchronise itself. Strata: Vulkan
   1.2 (explicit), so it must manage lifetimes and synchronisation. Mistake: thinking `draw()` draws now.

2. **Graphics APIs and abstraction layers (RHI).** Problem: Vulkan is verbose and platform APIs differ. Approaches:
   write per-API backends (Unreal RHI, bgfx, The Forge), use a third-party RHI (NVRHI, Diligent, wgpu), or a single API
   plus translation (MoltenVK). Strata: NVRHI on Vulkan only, with MoltenVK on macOS; Vulkan headers allowed only in
   `Platform/Vulkan` (layer rule `ExternalOwners`). Why: one backend to maintain, NVRHI gives state tracking and resource
   lifetimes, the Slang/HLSL choice keeps a D3D route open (DG "Shaders" intro, item 8). Mistake: assuming NVRHI makes
   Vulkan "safe" (see NVRHI pitfalls).

3. **Instance, physical device, logical device, queues.** Problem: a machine may have several GPUs with different
   features. Approaches: pick by score; require a feature floor. Strata: Vulkan 1.2 floor with dynamic rendering,
   synchronization2, timeline semaphores, descriptor indexing, anisotropy, cube arrays; discrete preferred; optional
   dedicated transfer/compute families. Why each feature is required is stated in the code (PV/VulkanGraphicsDevice.cpp
   659-713). Mistake: gating on the OS ("on Mac do X") instead of device features (DG "macOS and MoltenVK").

4. **Validation layers and error counting.** Problem: explicit APIs do not check misuse at run time. Approaches: debug
   layers in development. Strata: Khronos layer plus NVRHI's validation in Debug; every error is counted and every GPU
   test ends with `GetNewErrorCount() == 0`; known false positives are classified, not hidden. Mistake: ignoring
   warnings because "it renders".

5. **The swap chain, presentation and vsync.** Problem: showing images without tearing while the display scans out.
   Approaches: FIFO (vsync), MAILBOX (triple buffering), IMMEDIATE (tearing). Strata: FIFO with vsync, else MAILBOX or
   IMMEDIATE; UNORM back buffer because the engine sRGB-encodes itself; recreation on resize/out-of-date. Mistake:
   assuming the swapchain image count equals frames in flight.

6. **Frames in flight and CPU/GPU pacing.** Problem: the CPU must not overwrite what the GPU still reads, but should not
   wait each frame either. Approaches: N frames in flight with fences; ring buffers per frame. Strata: 2 frames in
   flight by default, an event query per frame (`BeginFrame` waits for the oldest). Callers that render back to back
   (tests, tools) do not pace through frames, hence the volatile-constant pacing in `SceneRenderer`. Mistake: freeing or
   rewriting a resource right after submitting work that uses it.

7. **Acquire, render, present, and the "display wait" placement.** Problem: waiting for the swapchain image early
   blocks unrelated work. Strata's distinctive choice: acquire in `BeginFrame` but submit the semaphore wait only at
   `PrepareBackBuffer`, so uploads and offscreen renders run first; counted as the `Present` stage. Mistake: rendering
   into the back buffer without calling `PrepareBackBuffer` (rule in AG "Rendering").

8. **Command lists, recording vs execution, immediate lists.** NVRHI's `open/close/executeCommandList`; immediate lists
   and the rule that a list which may open while another is open must be non-immediate. Mistake: opening two immediate
   lists (NVRHI validation refuses; timing it crashes).

9. **Resource states and barriers.** Problem: GPU caches and layouts require transitions between uses. Approaches:
   manual barriers (Vulkan/D3D12), automatic tracking (NVRHI, render graphs). Strata: NVRHI automatic barriers, plus
   explicit `setTextureState/commitBarriers` for same-binding-set UAV chains and for textures whose levels compute
   writes in the frame they were made. Mistake: two dispatches through one binding set reading each other's writes
   without a barrier.

10. **GPU resource lifetime: reference counting and deferred destruction.** Problem: destroying memory the GPU still
    reads corrupts or loses the device. Approaches: frame-delayed deletion queues, fence-tracked garbage collection.
    Strata: NVRHI references what command lists use, but not textures of clears and resolves, so render targets go
    through `DeferredReleaseQueue` (event-query tracked, time-budgeted destruction, 0.1 ms per texture). Mistake: `x =
    nullptr` on a render target in a resize.

11. **CPU-to-GPU uploads: staging memory and budgets.** Problem: GPU-local memory is not CPU-writable; large uploads
    stall frames. Approaches: staging rings, copy queues, per-frame budgets. Strata: `StagingPool` (power-of-two buffers,
    fenced reuse, bounded idle), `GPUUploadQueue` with time/byte planning (`PlanStep`), optional transfer queue (off by
    measurement). Mistake: `writeBuffer` of big data every frame; blocking a frame on a load.

12. **Event queries/fences as the universal "done" signal.** All lifetime systems (deferred release, staging, uploads,
    readback, profiler) poll event queries and never wait in a frame. Mistake: waiting on the GPU in a frame
    (`Renderer::ReadTexture` in game code).

13. **Shaders: stages, entry points, inputs and outputs.** Vertex, fragment (pixel), compute; interpolants; system
    values (`SV_Position`, `SV_VulkanVertexID`). Strata: every entry is `main`, stage from the registered name's suffix.
    Mistake: confusing `SV_InstanceID` (excludes base instance) with `SV_VulkanInstanceID`.

14. **Shading languages and offline compilation.** Approaches: GLSL->SPIR-V, HLSL via DXC, Slang, runtime compilation vs
    build time. Strata: HLSL-syntax Slang compiled at build time by a pinned slangc to SPIR-V 1.5, post-processed and
    embedded as C arrays; no runtime compilation, same bytes in every configuration. Why: portability (HLSL), no shader
    compiler in shipped games, reproducibility. Mistake: adding a shader file without listing it in
    `strata_add_shaders` and re-running configure.

15. **HLSL vs GLSL semantic traps.** `mul` order and the vector-vector `mul` dot product, `*` componentwise, row-wise
    constructors, `select` vs `mix`, vector comparisons, `Sample` in compute. Strata's real bug: a `mul` of two vectors
    collapsed a shadow filter and passed every GPU test (DG item 7). Mistake: trusting "it compiles".

16. **Resource binding models: descriptor sets, binding layouts, registers, push constants.** Approaches: slot-based
    (D3D11), descriptor sets/tables (Vulkan/D3D12), bindless. Strata: HLSL registers shifted to NVRHI's Vulkan ranges
    (t+0, s+128, b+256, u+384), `spaceS` = set S, one shared scene layout with a slot ledger, push constants in C++
    only. Mistake: a push-constant slot equal to another layout's constant buffer slot.

17. **Bindless textures.** Problem: rebinding textures per material breaks batching. Approaches: texture arrays, bindless
    descriptor indexing, virtual texturing. Strata: one update-after-bind array of up to 32,768 slots, slots written
    only at allocation, recycled after frames in flight; plus a stable `TextureTable` indirection so streaming does not
    rewrite materials. Mistake: overwriting a slot a frame in flight may sample (never done; replace = new slot).

18. **Pipeline state objects.** All fixed-function state (raster, depth, blend, input layout, shaders, framebuffer
    formats) baked into one object. Strata: `PipelineKey` cache; vertex input layout chosen by the vertex shader.
    Mistake: an input attribute no shader reads (validation warning; tests check).

19. **Coordinate systems and clip space.** World (right-handed, +Y up, -Z forward), view, clip, NDC, framebuffer;
    Vulkan's native +Y-down vs D3D's +Y-up; NVRHI's viewport flip makes Strata D3D-like. Mistake: using GLSL's UV
    formula for fullscreen passes, flipping images.

20. **Depth buffers and reversed-Z.** Problem: float depth precision is wasted near the far plane with standard
    mapping. Approaches: standard Z, reversed-Z with float depth, infinite far plane, logarithmic depth. Strata:
    reversed-Z everywhere (near 1, far 0), infinite variant available; clear to 0, `GreaterOrEqual`. Mistake: clearing
    depth to 1 or using `Less`.

21. **Triangle winding, culling and mirrored transforms.** CCW front faces (glTF); negative-determinant transforms flip
    winding and tangent handedness. Strata: separate clockwise pipelines for mirrored instances and a flipped handedness
    in `Mesh.vert`. Mistake: negative scale making objects inside-out.

22. **Floating-point precision far from the origin; camera-relative rendering.** Problem: float32 has ~7 digits, so at
    100 km vertex positions jitter. Approaches: origin rebasing, double-precision transforms on CPU, camera-relative
    rendering, large world coordinates (UE5). Strata: camera-relative shaders, rotation-only view, CPU subtracts in
    double; scene transforms stay float32 (7.8 mm quantisation at 100 km). Mistake: uploading a world position to a
    shader.

23. **Vertex data layout: streams and shared geometry.** Problem: per-mesh buffers mean per-mesh binds and draw calls.
    Approaches: interleaved vs separate streams, mega-buffers, mesh pools. Strata: positions separate (depth-only passes
    fetch 12 B), attributes 36 B, skin 16 B; one geometry pool with stable handles, compaction and growth by GPU copies.
    Mistake: caching a mesh's offsets across frames (compaction moves them).

24. **Instancing, draw lists and indirect draws (foundation level).** Instance buffer of 64-byte records, a per-frame
    draw list indexed by `SV_VulkanInstanceID`, buckets per pipeline drawn by `drawIndexedIndirect`. The GPU-driven
    details belong to the render-scene area; the foundations chapter needs the shape.

25. **GPU struct layout rules (std140/std430) and CPU mirrors.** Strata mirrors every GPU struct in C++ with size
    `static_assert`s and column-major glm bytes. Mistake: adding a `vec3` and shifting every following field.

26. **Multi-pass frame architecture: forward with depth prepass.** Problem: overdraw and the need for depth/normals
    early (SSAO, SSR, shadows mask). Approaches: forward, forward+ (clustered), deferred, visibility buffer. Strata:
    clustered forward with a depth/normal/entity-ID prepass and an `EQUAL` opaque pass; needs bit-identical positions
    (invariant position decoration). Mistake: changing the prepass vertex math without the forward pass.

27. **HDR rendering and the display transform (foundation level).** Linear HDR RGBA16F target, `SanitizeHDR`,
    pre-exposure, tone mapping into sRGB-encoded UNORM. Details in the post-processing area; foundations must explain why
    the back buffer is UNORM and the engine encodes.

28. **Readback.** GPU->CPU copies through staging, polled. Mistake: blocking readback in a frame.

29. **GPU timing with timestamps.** Approaches: timestamp queries, vendor tools (Nsight, RGP), pipeline statistics.
    Strata: always-on stages tiling each command list, results 2-3 frames late, dropped rather than waited for; tile
    based drivers may write timestamps at pass end. Mistake: waiting for timestamps, or inserting a stage and expecting
    ids to be stable.

30. **Text rendering: fonts, shaping, glyph atlases, signed distance fields.** Approaches: bitmap atlases per size, SDF /
    MSDF atlases, vector rendering (Slug), HarfBuzz shaping. Strata: single-channel SDF at 32 texels per em, on-demand
    atlases with LRU and raster budgets, simple shaping (advance + kerning, wrap, ellipsis; no complex scripts),
    measuring separated from rasterizing. Mistake: measuring text by rasterizing it.

31. **Untrusted input in the renderer: font files.** stb_truetype does no bounds checks; Strata validates every read
    and bounds time. Mistake: calling a new stb_truetype function without extending the validator.

32. **Overlays and editor visualisation.** Grid, outline from entity IDs, debug lines, gizmos, overlay passes from
    higher modules via a registry (dependency inversion). Mistake: renderer code including the GameUI module.

---

## 3. Code worth showing

| # | File and lines | What it teaches | Reader must know first |
| --- | --- | --- | --- |
| 1 | SH/Debug/ColorTriangle.vert.slang:1-35 with T/Renderer/GPURendererTests.cpp:131-172 | The smallest complete GPU program: a triangle without vertex buffers, a pipeline, a command list, a readback, and the clip-space convention proved by pixels (NDC +Y up = top half). | Concepts 1, 8, 13, 19 |
| 2 | R/GraphicsDevice.h:128-199 | An RHI-facing interface: what a device must offer (swapchain, frames, back buffer, timestamps, transfers, errors). | Concept 2 |
| 3 | PV/VulkanGraphicsDevice.cpp:657-713 | Feature requirements with a reason per feature; rejection logging. | Concept 3 |
| 4 | PV/VulkanGraphicsDevice.cpp:744-750 | Adapter scoring (discrete > integrated, memory as tiebreak). | Concept 3 |
| 5 | PV/VulkanGraphicsDevice.cpp:1129-1170 | Swapchain format (UNORM, engine encodes), present mode by vsync, image count. | Concept 5 |
| 6 | PV/VulkanGraphicsDevice.cpp:1438-1513 | `BeginFrame`: frame pacing by event queries, minimized window, swapchain recreation, acquire with retry, deferred wait. | Concepts 5-7 |
| 7 | PV/VulkanGraphicsDevice.cpp:1515-1605 | `SubmitPendingAcquireWait`, `PrepareBackBuffer`, `EndFrame` (present semaphore through an empty submission). | Concept 7 |
| 8 | PV/VulkanGraphicsDevice.cpp:946-990 | Wrapping a raw Vulkan device into NVRHI, validation wrapper, Dist exclusion, exceptions caught at the call site. | Concepts 2, 4 |
| 9 | R/GraphicsModule.cpp:26-77 | An engine module that owns the GPU: device + swapchain + `Renderer::Init`, failure advice, frame begin returns Skip/Close. | Concept 6; engine modules (Core area) |
| 10 | R/Renderer.cpp:84-168 | Service hub initialisation: samplers, fallback textures in one command list, bindless reserved slots, order of subsystems. Includes the flat-normal half-float story (107-111). | Concepts 8, 17 |
| 11 | R/Renderer.cpp:267-310 | What every frame begins with, and `PrepareBackBuffer` (Present stage, black clear). | Concepts 6, 7 |
| 12 | R/DeferredReleaseQueue.h:16-30 and .cpp:14-76 | The central lifetime algorithm: batches fenced by event queries, completion in order, budgeted destruction, progress without frames. | Concepts 10, 12 |
| 13 | R/BindlessTextureTable.cpp:23-108 | Growing a partially-bound descriptor table, slot allocation and recycling after `framesInFlight + 1` frames. | Concepts 6, 17 |
| 14 | R/GPUUploadQueue.cpp:228-277 | `PlanStep`: budgeted uploads sized by measured throughput, deadline share, granules, "every frame makes progress". (Long; the second central algorithm.) | Concept 11 |
| 15 | R/StagingPool.h:11-30 | Design comment of a staging pool (why fence per batch, why idle staging must not exceed the budget). Text, not code: a "design note" box. | Concept 11 |
| 16 | R/ShaderLibrary.cpp:47-88 and R/EmbeddedShaders.h | Shader lookup of embedded SPIR-V, stage from name, caching. | Concept 14 |
| 17 | CMake/StrataShaders.cmake:64-85 and 165-218 | slangc flags with reasons; two custom commands per entry; generated registry. | Concepts 14, 16 |
| 18 | SH/Include/Common.slang:4-57 | Register convention, `NDCToUV`, sRGB, `SanitizeHDR`. | Concepts 16, 19, 27 |
| 19 | SH/Include/Common.slang:194-215 | The only `__target_switch`/`spirv_asm`: why `PackHalf2x16` is wrapped (Float16 capability). | Concept 15 |
| 20 | SH/Include/Scene.slang:53-133 | `FrameConstants` and `InstanceData` as the CPU/GPU contract (std140/std430, comments as documentation). Pair with R/SceneRenderData.h:113, 189-199. | Concept 25 |
| 21 | SH/Include/Scene.slang:238-260 | `TransformPositionRelative` and `TransformNormal` (cofactor normal matrix, mirrored sign). | Concepts 21, 22 |
| 22 | SH/Scene/Mesh.vert.slang:35-60, 85-137 | The scene vertex shader: draw list -> instance -> camera-relative position -> clip; tangent handedness; the converted `st_Main` + entry wrapper pattern. | Concepts 13, 22, 24 |
| 23 | SH/PostProcess/Fullscreen.vert.slang:8-13 | Fullscreen triangle from the vertex index (exercise: derive the three vertices). | Concept 19 |
| 24 | Strata/src/Strata/Math/Math.cpp:70-91 | Reversed-Z projections: swap near/far in a [0,1] projection, the infinite form by hand. | Concept 20 |
| 25 | R/SceneRenderer.cpp:2424-2527 | Building a pipeline from a key: shader choice, input layout by shader, winding, culling, reversed-Z depth per pass, shadow bias, transmittance blending. | Concepts 18, 20, 21, 26 |
| 26 | R/SceneRenderer.cpp:2901-3735 (excerpted: 3283-3289, 3360-3420, 3489-3541) | The frame as a sequence of timed passes; markers; `gpuTimer.Next(stage)`. Show as a trimmed outline, not whole. | Concept 26 |
| 27 | R/SceneRenderer.cpp:2247-2275 (`ReleaseRenderTargets`) | Real use of deferred release on resize, with the comment on clears. | Concept 10 |
| 28 | R/SceneRenderer.cpp:1457-1504 | Pacing volatile constant buffer versions with event queries; the poll-after-wait quirk. | Concepts 6, 12 |
| 29 | R/GPUProfiler.cpp:357-394 | `GPUPassTimer`: one timestamp per boundary, intervals only within one slot. | Concept 29 |
| 30 | R/TextureReadback.cpp:7-74 | A careful API: every refusal with a reason, overflow-safe region check, staging + event query. | Concept 28 |
| 31 | R/SceneVertexLayouts.h:23-89 | `constexpr` tables tying shaders to input layouts (and the test that checks them). | Concept 18 |
| 32 | SH/Include/SDFText.slang:4-15 + SH/Overlay/Text.frag.slang:17-26 | SDF coverage with `fwidth`, derivative before discard. | Concept 30 |
| 33 | R/FontValidation.h:58-71 (comment) and an excerpt of FontValidation.cpp | Defensive parsing of untrusted binary input. | Concept 31 |

(33 rows: the planner can drop the weakest; 12, 14, 22, 25 and 26 are the must-haves.)

---

## 4. Figures

### Diagrams

1. **Layer and ownership map**: Application -> GraphicsModule -> GraphicsDevice (interface) -> VulkanGraphicsDevice
   (Platform/Vulkan) -> NVRHI -> Vulkan -> driver/MoltenVK; `Renderer` services beside; `VulkanPresentation` from
   Platform/GLFW. Shows which folders may include which headers.
2. **CPU/GPU timeline with two frames in flight**: CPU records frame N+1 while GPU executes N; event query per frame;
   `BeginFrame` wait point; acquire at `BeginFrame`, semaphore wait at `PrepareBackBuffer`, present at `EndFrame`; uploads
   submitted before the back buffer wait.
3. **Swapchain state machine**: none (minimized) -> created -> acquired -> prepared -> presented; out-of-date/suboptimal
   -> recreate; surface lost -> rebuild next frame; device lost -> close.
4. **Resource lifetime / deferred release**: handles -> Release (batch + event query) -> pending -> completed -> destroyed
   within 0.25 ms per frame; contrast with NVRHI's command-list references (and the clears exception).
5. **Upload path data flow**: asset bytes -> `PlanStep` -> `StagingPool` buffer (mapped write) -> copy command (graphics or
   transfer queue) -> texture/geometry pool -> ticket complete -> asset Ready; staging fenced and reused.
6. **Register/binding mapping**: HLSL `tN/sN/bN/uN, spaceS` -> Vulkan binding N + 0/128/256/384, set S; set 0 scene layout,
   set 1 bindless table; push constants.
7. **Bindless indirection**: material data (texture table index) -> `TextureTable` entry (slot | sampler | grayscale,
   MinLod) -> bindless slot -> `Texture2D u_Textures[]`; streaming swaps slots without touching materials.
8. **Geometry pool memory layout**: Static arena (positions buffer, attributes buffer), Skinned arena (+ skin buffer),
   index arena; `GeometryHandle` -> `GeometryAllocation` table; free ranges, compaction moving a mesh.
9. **Shader build pipeline**: `.slang` + includes -> slangc (flags) -> `.raw.spv` -> StrataShaderTool -> `.spv` + `.h` ->
   EmbeddedShaderRegistry.cpp -> `ShaderLibrary::Get` -> `nvrhi::IShader`; plus the variants fan-out (one source, many
   defines) and CI checks.
10. **Coordinate spaces chain**: object -> world (instance rows) -> camera-relative world -> view (rotation only) -> clip
    (reversed-Z, jitter) -> NDC (+Y up) -> framebuffer (row 0 top) and UVs.
11. **Reversed-Z precision plot**: depth value vs distance for standard and reversed float depth (a chart, could be
    computed from the projection formulas).
12. **The frame's pass graph**: the 23 steps of 1.10 as a vertical timeline coloured by GPU stage, with the render targets
    each pass reads and writes (depth, normals, entity IDs, HDR, AO, shadow mask, LDR, output).
13. **GPU profiler ring**: `MaxFramesInFlight + 2` slots, open/pending/free, timestamps per slot, resolution 2-3 frames
    later.
14. **Font pipeline**: font bytes -> `ValidateTrueTypeFont` -> `Font` -> `FontFace` (metrics) -> `ShapeText` -> `FontAtlas`
    (cells in pages, LRU) -> `Resolve` -> quads -> Text shaders (SDF coverage).
15. **Overlay order**: post-processed image -> tints -> motion view -> grid -> outline -> debug lines -> world text ->
    world canvases -> screen text -> screen canvases -> copy to target.

### Screenshots

Taking them: `viewport.capture {camera, position, target, overlays, debugView, quality, path}` through StrataCLI
(DG "View commands" l.3627-3640), on the `Showcase` sample (`Samples/Showcase`) or a new project from a template.
Foundation screenshots are mostly not of shading features:

1. **The editor viewport with Showcase** at default settings: "what the frame produces". Overlays on.
2. **The same view's intermediate targets** (depth (reversed-Z: near bright), normals, entity IDs false-coloured, HDR before
   tone mapping, output). Not exposed by `viewport.capture` debug views; would need a test-style tool reading
   `GetDepthTexture()`/`GetNormalTexture()`/`GetEntityIDTexture()` via `Renderer::ReadTexture` (see "Not determined").
3. **Overlays isolated**: grid on, selection outline on one entity, debug lines (gizmos of lights/cameras/colliders);
   `viewport.capture {overlays: true}` vs `false`.
4. **Entity tints / streaming debug view** (`debugView: "streaming"`), **LOD view** (`"lod"`) and **mip view** (`"mip"`)
   as examples of overlay-based debug views.
5. **Motion view** (`debugView: "motion"`) to illustrate the per-pixel motion overlay.
6. **Camera-relative rendering**: the same small scene at the origin and at 100 km (the test's checker ground and sphere);
   ideally a third image with camera-relative rendering conceptually off (not switchable in the engine; would have to be
   simulated or shown from an older build - see "Not determined").
7. **Text**: world-space text on a wall and screen-space HUD text (e.g. the Tetris sample's HUD); a close-up of an SDF
   glyph magnified to show crisp edges; the atlas page texture (`FontAtlas::GetPagePixels`) as an image.
8. **Mirrored instance**: an asymmetric mesh with scale (-1, 1, 1) beside the original, showing correct winding and
   normal map.
9. **Editor Performance panel / `editor.perf` output** with the GPU stages (GPU.Setup ... GPU.Overlays) for a Showcase
   frame.
10. **Validation-layer error example**: a log line "Vulkan: ..." counted as an error (text capture, not a render).
11. **The black frame**: what `PrepareBackBuffer`'s clear guarantees when nothing draws (trivial, optional).

---

## 5. Rules and pitfalls (the "why" boxes)

1. **Never take the address of an NVRHI handle (`&m_Pipeline`)**: `RefCountPtr::operator&` releases the reference and
   returns the raw pointer's address; assigning through it leaves a dangling object. (DG l.958-960; AG.)
2. **Same-binding-set UAV chains need explicit barriers**: NVRHI places barriers only when binding sets change.
   (DG l.960-963.)
3. **Drop render targets through `Renderer::ReleaseDeferred`**: NVRHI's Vulkan backend does not reference textures of
   clears and resolves; a target that an in-flight frame only cleared would be freed while the GPU writes it
   (validation error, possibly device loss). (R/DeferredReleaseQueue.h:16-22.)
4. **Destroying a texture costs ~0.1 ms**: destruction is budgeted per frame (0.25 ms) or 20 thumbnails cost 2.1-2.3 ms
   in one frame. (R/DeferredReleaseQueue.h:27-30.)
5. **Leave a compute-written texture's undefined layout whole first** (`setTextureState(AllSubresources, UnorderedAccess)`
   + `commitBarriers()`): per-level barriers could land after levels were written on NVIDIA and lose them. (DG l.971-975.)
6. **A list that may open while another is open must be non-immediate**: NVRHI validation refuses a second immediate
   list; recording into the unopened list does nothing; timing it crashes. (DG l.975-979.)
7. **Volatile constant buffers have a fixed number of versions**: callers that render back to back must pace their
   writes; poll after `waitEventQuery` because NVRHI's Vulkan wait leaves the completion value stale. (DG l.979-983;
   R/SceneRenderer.cpp:1462-1472.)
8. **Call `Renderer::PrepareBackBuffer()` before rendering into the back buffer**: the GPU waits for the display only from
   there, so earlier work never queues behind it; it also defines the image (black). (AG "Rendering"; R/Renderer.h:87-91.)
9. **Command lists that copy from released staging must execute before `SubmitBatch`/next `BeginFrame`**: staging is
   fenced then and would be reused while a copy still reads it. (AG "Rendering"; R/StagingPool.h:29-30.)
10. **Never block a frame on an asset or the GPU**: skip or fall back; poll readbacks and timestamps. `ReadTexture` and
    `ResolveGPUStats(true)` are for tests and tools. (AG "Rendering"; DG "Readback", "GPU timing".)
11. **Bindless slots are written only at allocation and recycled after frames in flight**: update-after-bind descriptors
    must not change while frames in flight can access them; replacing a texture means a new slot. Resolve slots every
    frame (mip streaming changes them). (R/BindlessTextureTable.h:17-20; AG "Asset pipeline".)
12. **Read mesh geometry through the pool every frame**: compaction moves it, growth replaces buffers; compare buffer
    versions to remake binding sets. (DG "Batching" l.4229-4241.)
13. **Every shader entry is listed in `strata_add_shaders`; re-run configure**: there is no runtime discovery.
    (AG "Shaders".)
14. **`mul` only with a matrix**: `mul(v, w)` is a dot product and `M * N` componentwise; both compile silently. A real
    regression collapsed the local shadows' filter and passed every GPU test. (DG item 2, item 7.)
15. **Vector comparisons through `all()`/`any()`; matrix constructors take rows; `select` reverses `mix`'s order.**
    (DG item 2.)
16. **`SampleLevel` or `Load` in compute**: `Sample` needs compute derivatives, a capability devices need not have.
    (DG item 2; ShaderModules hint.)
17. **Every storage image states its format**: unstated ones become Unknown, which needs a capability the checks reject.
    (CMake/StrataShaders.cmake:68-69.)
18. **`SV_VulkanInstanceID`, not `SV_InstanceID`**: the draw list is indexed including the base instance. (DG item 2.)
19. **Derivatives before the first `discard`**: a discarded lane leaves its quad's derivatives undefined (Mesa drops the
    lane, MoltenVK keeps it). (DG "Lights, shadows and HDR" l.4549-4554; `Architecture.Shaders` checks.)
20. **Push-constant slot must not equal another layout's CB slot**: both share the `b` registers. (AG "Shaders".)
21. **`__target_switch`/`spirv_asm` only in `Include/Common.slang`, no generics/modules/interfaces**: keeps the HLSL
    route to other compilers open. (DG item 2, item 8.)
22. **The prepass and forward pass must produce bit-identical positions**: the opaque pass uses an `EQUAL` depth test;
    `Scene/Mesh.vert` positions are decorated `Invariant` by the shader tool because Slang cannot say `invariant`.
    (SH/Scene/Mesh.vert.slang:5-10, 32-33.)
23. **A scene vertex shader reads exactly its input layout**: the validation layer only warns on unused attributes and GPU
    suites count errors; a new vertex shader gets a `c_SceneVertexEntries` line. (R/SceneVertexLayouts.h:23-25.)
24. **Reversed-Z: clear depth to 0, test `GreaterOrEqual`, sky at depth 0.** (R/SceneRenderer.cpp:2470-2472, 3416, 3509.)
25. **Front faces are CCW; mirrored instances use clockwise pipelines and flip tangent handedness; normals via
    `TransformNormal`.** (AG "Rendering"; SH/Include/Scene.slang:251-260.)
26. **Never upload a world position to a scene shader**: subtract the camera in double on the CPU; `InstanceData` stays
    world space and 64 bytes. (DG "Camera-relative space".)
27. **Fullscreen UVs `(ndc.x*0.5+0.5, 0.5-ndc.y*0.5)`**: NVRHI's flip makes row 0 the top. (AG "Renderer conventions".)
28. **HDR writers clamp with `SanitizeHDR`**: Inf/NaN in a half-float target turn black or spread through post. (AG.)
29. **A target framebuffer must be the viewport's size and non-sRGB UNORM**: the renderer never rescales and writes
    sRGB-encoded values itself. (R/SceneRenderer.h:837-848; DG l.3972-3975.)
30. **Gate on device features, never on the OS.** (DG "macOS and MoltenVK".)
31. **GPU tests share one device (`Tests::GPUContext`) and end with zero new errors**: repeated `VkInstance` creation
    under load crashed drivers. (DG "GPU tests"; AG "Testing".)
32. **Time every new pass in a GPU stage and register the stage in frame order** (and in the five lists that name them);
    stage boundaries that matter go where passes end (tile-based drivers). (DG "GPU timing".)
33. **A new scene resource takes the next free slot in the `Include/Scene.slang` ledger; a pass that does not run binds a
    dummy.** (DG l.6246-6250.)
34. **Font files are untrusted: extend `FontValidation` (with crafted-font tests) before calling another stb_truetype
    function; bound time as well as reads.** (AG "Rendering"; DG "Text and fonts".)
35. **Measure text with `ShapeText`, never by rasterizing; passes share the renderer's `FontAtlasCache`.** (AG.)
36. **The renderer reaches higher modules only through registries** (`SceneOverlayRegistry`, component gizmos), never by
    including them. (AG "Game UI", "Layers".)
37. **Exceptions from NVRHI/vulkan.hpp are caught at the call site** (`vk::SystemError` around device creation and frame
    waits): engine code does not throw. (PV/VulkanGraphicsDevice.cpp:964-972, 1446-1458.)

---

## 6. Hands-on

### For engine developers

1. **Read the triangle test** (easy): run `StrataTests --test-case="Triangle rendering follows*"`, then change
   `ColorTriangle.vert`'s positions to cover the bottom half and make the test's expectation fail, then fix it. Proves:
   NDC orientation, the shader-to-test cycle, shaders need a rebuild (not a configure for an edit).
2. **Add a new debug shader entry** (easy-medium): a `Debug/Checker.frag` fullscreen pass; add to
   `strata_add_shaders`, re-run configure, load through `ShaderLibrary`, draw with `PostProcess/Fullscreen.vert` into an
   offscreen target and check pixels in a new `GPU.*` test ending with `GetNewErrorCount() == 0`. Proves: the build,
   registry, pipelines, fullscreen UVs, test rules.
3. **Break and observe a dialect trap** (medium): in a scratch branch replace a `mul(M, v)` with `mul(v, w)` in a copy of
   a shader, observe it compiles; write a pixel test that catches it. Proves: why the rules exist.
4. **Derive the fullscreen triangle** (exercise, easy): from `Fullscreen.vert.slang:10`, compute the three NDC vertices
   and UVs by hand; explain why one triangle beats two.
5. **Reversed-Z precision experiment** (medium, CPU-only): with `Math::PerspectiveReverseZ` and the standard projection,
   compute float32 depth for distances 0.1 m-10 km and plot the step between representable depths. Proves concept 20.
6. **Deferred release experiment** (medium): write a GPU test that creates a render target, only clears it in a command
   list, drops it with `nullptr` vs `ReleaseDeferred`, and observe the validation error count (in a scratch build
   only). Proves rule 3. (Model: T/Renderer/GPUDeferredReleaseTests.cpp:80.)
7. **Add a GPU stage** (medium): time a new no-op pass between two existing stages with `GPUPassTimer::Next`, register
   it in `RendererGPUStages` in frame order, update the five lists, check with `editor.perf`. Proves the GPU timing
   rules.
8. **Write a non-blocking screenshot tool** (medium): use `TextureReadback` polled each frame and `ImageWriter` to save
   `SceneRenderer::GetOutputTexture()` without stalling. Proves readback and event-query polling.
9. **Camera-relative audit** (medium-hard): add a debug line at a world position 100 km out and check it is uploaded
   relative (study `DrawDebugLines` and `SceneOverlayFrame`), then reproduce the CameraRelative test with your own
   mesh. Proves concept 22.
10. **Font validation exercise** (hard): craft a font with a `loca` entry pointing past `glyf` and check
    `ValidateTrueTypeFont` rejects it; read `FontTests.cpp:430` first. Proves defensive parsing.
11. **Geometry pool compaction** (hard): write a test that allocates and frees meshes to fragment the Static arena, calls
    `Compact`, and verifies a rendered frame is identical (model: T/Renderer/GPUGeometryPoolTests.cpp:468). Proves
    "read the pool every frame".
12. **Map a frame in RenderDoc or Nsight** (medium, outside the engine's tests): capture the editor and match markers
    (`beginMarker("Shadows")`, ...) to the pass table of 1.10. Proves the frame order. (Tool availability not checked.)

### For game developers

1. **Choose vsync and see the cost** (easy): toggle vsync (window/project setting) and read `editor.perf` frame times;
   explain FIFO vs MAILBOX in a sentence.
2. **Debug draw from a script or C++ layer** (easy-medium): draw a path with `DebugDraw::Line`/`Arrow` each frame (where
   a game can reach `DebugDraw` - see "Not determined"), show it with and without depth test.
3. **World and screen text** (easy): add `TextComponent`s (world on a sign, screen HUD), change font asset, alignment and
   size; observe text appearing with the default font while a font loads.
4. **Capture screenshots for a store page** (easy): `viewport.capture` with path, quality and overlays off.
5. **Mirroring safely** (easy): flip a prop with negative scale and confirm it renders correctly (front faces, normal
   maps), then compare with a hand-made mirrored mesh.
6. **Big worlds** (medium): place a scene 50 km from the origin and walk around; compare with the same scene at the
   origin. Explains why the engine is fine with this and what still quantises (entity origins at 7.8 mm per 100 km).
7. **Read the GPU stages of your game** (medium): run `StrataRuntime --perf-log` (or the editor's Performance panel) and
   identify which stage dominates; relate it to the scene's features.

---

## 7. Glossary

- **GPU**: a processor of many parallel lanes, with its own memory, that runs shaders on commands sent by the CPU.
- **Graphics API**: the interface a program uses to command the GPU (Vulkan, Direct3D 12, Metal, OpenGL).
- **Vulkan**: Khronos's explicit, cross-platform graphics and compute API; Strata requires 1.2.
- **MoltenVK**: a Vulkan implementation on top of Apple's Metal; how Strata runs on macOS.
- **NVRHI**: NVIDIA's Rendering Hardware Interface library: one C++ API over Vulkan/D3D with state tracking and
  reference-counted resources.
- **RHI**: Rendering Hardware Interface, an engine's abstraction over graphics APIs.
- **Instance (VkInstance)**: the program's connection to the Vulkan loader and its layers.
- **Physical device / logical device**: a GPU as enumerated / the program's opened handle on it with chosen features.
- **Queue / queue family**: where command buffers are submitted; families differ in capabilities (graphics, compute,
  transfer).
- **Transfer queue**: a queue for copies only, which can run beside rendering.
- **Validation layer**: a debug layer that checks API usage and reports errors.
- **Swapchain**: the ring of images shown on a window surface.
- **Surface**: the window system's presentable target for Vulkan.
- **Present mode**: how images reach the display: FIFO (vsync), MAILBOX (latest wins), IMMEDIATE (may tear).
- **Back buffer**: the swapchain image the frame draws into.
- **Acquire / present**: taking the next swapchain image / handing a finished one to the display.
- **Semaphore**: GPU-GPU ordering primitive between submissions (acquire -> render -> present).
- **Fence / event query**: a GPU->CPU "work up to here is done" signal; NVRHI's event query is what Strata polls.
- **Frames in flight**: how many frames the CPU may record ahead of the GPU (2 by default).
- **Command list / command buffer**: a recorded sequence of GPU commands, executed later.
- **Immediate command list**: NVRHI's default kind, of which only one may be open at a time.
- **Barrier / resource state**: a transition telling the GPU a resource changes use (render target -> shader read).
- **Descriptor / descriptor set**: a GPU-side reference to a resource / a group of them bound together.
- **Binding layout / binding set**: NVRHI's names for a descriptor set layout / a filled descriptor set.
- **Register (tN, sN, bN, uN) and space**: HLSL's binding slots for textures/read-only buffers, samplers, constant
  buffers, UAVs; space = descriptor set.
- **Push constants**: a small block of data written directly into the command list.
- **Constant buffer / volatile constant buffer**: small uniform data; NVRHI's volatile kind has versions per write.
- **Structured buffer**: an array of structs a shader reads (or writes, RW) by index.
- **UAV / storage image**: a resource a shader writes in arbitrary places.
- **std140 / std430**: GLSL/Vulkan layout rules for uniform and storage buffers (alignment, padding).
- **Bindless**: one big descriptor array indexed by an integer from data, instead of binding textures per draw.
- **Update-after-bind / partially bound**: descriptor-indexing features that let a large table be written while in use
  (for unused slots) and contain empty slots.
- **Texture table (Strata)**: stable per-texture index -> packed bindless slot, sampler and min-LOD entry.
- **Pipeline (PSO)**: an object holding shaders and fixed-function state for draws or dispatches.
- **Input layout**: how vertex buffer bytes map to vertex shader inputs.
- **Shader**: a GPU program; vertex (per vertex), fragment/pixel (per covered pixel sample), compute (general).
- **Entry point**: the function a shader stage starts at (`main` in Strata).
- **SPIR-V**: Vulkan's binary shader intermediate language.
- **Slang / slangc**: a shading language and compiler accepting HLSL syntax; Strata's shader compiler (pinned 2026.20).
- **HLSL / GLSL**: Microsoft's and Khronos's shading languages; Strata's sources are HLSL-syntax.
- **Variant (shader)**: the same source compiled with different preprocessor defines (`ST_SKINNED`, `ST_VELOCITY`).
- **Invariant position**: a guarantee that identical position computations give identical results across shaders.
- **Interpolant**: a vertex output interpolated across the triangle for the fragment shader.
- **Derivative (ddx/ddy/fwidth)**: rate of change of a value between neighbouring pixels in a 2x2 quad.
- **Discard / clip**: ending a fragment so it writes nothing.
- **Clip space / NDC**: post-projection homogeneous coordinates / after division by w, x and y in [-1, 1].
- **Viewport flip**: NVRHI's negative-height viewport that makes Vulkan's NDC +Y point up like D3D's.
- **Reversed-Z**: depth mapping with near = 1 and far = 0 for better float precision.
- **Infinite far plane**: a projection whose far plane is at infinity (depth 0).
- **Depth test functions**: Less/Greater/Equal comparisons; Strata uses GreaterOrEqual and Equal.
- **Depth prepass**: drawing depth (and normals, IDs) first so later passes shade only visible surfaces.
- **Forward / deferred / clustered forward**: shading while rasterizing / from a G-buffer / forward with lights binned into
  view-space clusters.
- **Winding order / front face / back-face culling**: vertex order deciding which side faces the camera / skipping
  triangles seen from behind.
- **Mirrored transform**: a transform with negative determinant, which reverses winding.
- **Tangent handedness**: the sign that orients the bitangent of a tangent frame (MikkTSpace).
- **Normal matrix / cofactor matrix**: what transforms normals correctly under non-uniform scale.
- **Camera-relative rendering**: shading in world space translated so the camera is at the origin.
- **Origin rebasing**: moving the world's origin to the player instead (not used by Strata).
- **Staging buffer**: CPU-writable memory used as the source of copies into GPU-local resources.
- **Upload budget / step / granule**: the bytes and time a frame may spend uploading / one recorded copy / the smallest
  useful piece (a row of blocks).
- **Ticket (upload)**: an id complete once the GPU ran every copy recorded before it.
- **Deferred release**: holding resources until the GPU is done, then destroying them.
- **Geometry pool / arena**: shared vertex and index buffers holding every mesh / one buffer set within it.
- **Range allocator**: hands out and frees offset ranges in a buffer.
- **Compaction (defragmentation)**: moving allocations together to recover contiguous free space.
- **Instance / InstanceData**: one placement of a mesh / its 64-byte GPU record.
- **Draw list**: the frame's array of instance indices the vertex shader reads per instance.
- **Indirect draw**: a draw whose arguments the GPU reads from a buffer.
- **HDR / tone mapping / sRGB encoding**: high-dynamic-range linear light / mapping it to displayable range / the
  display's nonlinear encoding.
- **UNORM / sRGB formats**: 8-bit formats read as [0, 1] / with hardware sRGB conversion.
- **RGBA16F / half float**: 16-bit floating-point channel format of HDR targets (max 65504).
- **Readback**: copying GPU data to the CPU.
- **Timestamp query**: a GPU-written clock value used to time passes.
- **GPU stage (Strata)**: a named interval of the frame's GPU work in the frame profiler.
- **Tile-based renderer**: GPUs (Apple, mobile) that render per screen tile; timestamps may land at pass ends.
- **Font / glyph / code point**: a typeface file / one drawable shape / a Unicode character number.
- **TrueType / CFF / OTTO**: outline formats; Strata accepts TrueType outlines and rejects CFF.
- **stb_truetype**: the single-header font rasterizer Strata uses (no bounds checking).
- **Kerning / GPOS**: spacing adjustment between glyph pairs / OpenType's positioning table.
- **Text shaping**: turning text into positioned glyphs (Strata: advances, kerning, wrapping; no complex scripts).
- **Signed distance field (SDF)**: an image storing the distance to the glyph outline, sharp when scaled.
- **Glyph atlas / page / cell**: texture(s) holding rasterized glyphs / one array layer / a fixed-size slot.
- **LRU eviction**: removing the least recently used entries when full.
- **Overlay**: something drawn over the finished image (grid, outline, lines, text, UI).
- **Gizmo**: an editor shape showing a light, camera or collider.
- **Entity ID buffer**: a render target storing which entity covers each pixel, for picking and outlines.
- **Picking**: finding the object under the mouse.
- **Jitter (TAA)**: a sub-pixel offset of the projection each frame for temporal anti-aliasing.
- **Device lost**: an unrecoverable GPU failure (driver reset, removal).

---

## 8. Proposed chapters (teaching order)

1. **"How a GPU frame works"** - concept, both audiences, prereq: none (basic C++). Purpose: explain CPU/GPU
   asynchrony, command buffers, frames, double buffering, presentation, with Strata's frame list as the running example.
   Size M, 2 screenshots (editor viewport, perf panel), diagrams 2 and 3.
2. **"Talking to the GPU: Vulkan, NVRHI and the GraphicsDevice"** - internals, engine, prereq: ch. 1, C++ interfaces.
   Purpose: read `GraphicsDevice`, device selection, swapchain, acquire/present placement, validation, MoltenVK.
   Size L, 0 screenshots, diagrams 1, 3.
3. **"Your first triangle in Strata"** - tutorial, engine, prereq: ch. 2. Purpose: build a pipeline, record a command list,
   read pixels back, write a GPU test; the clip-space convention by experiment. Size M, 1 screenshot (test image).
4. **"Shaders in Strata: Slang, the build and the dialect"** - internals + reference, engine, prereq: ch. 3, basic linear
   algebra. Purpose: write and register a shader, know every dialect rule and its reason, the checks that guard them.
   Size L, 0 screenshots, diagram 9.
5. **"Coordinate systems: from object to pixel"** - concept, both, prereq: ch. 3 and the math chapter (matrices,
   transforms). Purpose: spaces, NDC, viewport flip, UVs, reversed-Z, winding and mirroring, camera-relative rendering.
   Size L, 3 screenshots (mirrored prop, 100 km comparison, depth visual), diagrams 10, 11.
6. **"Resources and their lifetimes"** - internals, engine, prereq: ch. 2. Purpose: buffers, textures, states and
   barriers, the NVRHI pitfalls, frames in flight and deferred release, volatile constant pacing. Size M, diagram 4.
7. **"Getting data onto the GPU: staging and the upload queue"** - internals, engine, prereq: ch. 6. Purpose: staging pool,
   budgeted steps (`PlanStep`), tickets, transfer queue trade-off. Size M, diagram 5. (The streaming policy itself is
   in the asset-streaming area's chapter.)
8. **"Binding resources: layouts, registers and bindless textures"** - internals, engine, prereq: ch. 4, 6. Purpose:
   register mapping, the scene layout ledger, push constants, the bindless table and the texture table. Size M,
   diagrams 6, 7.
9. **"Meshes on the GPU: vertex streams and the geometry pool"** - internals, engine, prereq: ch. 7, 8. Purpose: stream
   layout, pipelines' input layouts, the pool's allocation, growth, compaction and its rules. Size M, diagram 8.
10. **"A frame of the scene renderer, pass by pass"** - internals, both (game developers read the overview), prereq:
    ch. 5, 8, 9. Purpose: the 23 steps, the render targets, the prepass/EQUAL design, where each feature chapter plugs
    in, pipelines by key. Size XL, 4 screenshots (intermediate targets, final), diagram 12. This is the hub chapter
    the lighting/shadow/post/GI chapters link back to.
11. **"Reading back and measuring: readback and GPU timing"** - internals + tutorial, engine, prereq: ch. 10. Purpose:
    non-blocking readback, picking, timestamps, stages and how to add one. Size M, 1 screenshot (perf panel),
    diagram 13.
12. **"Drawing over the image: overlays, debug drawing and gizmos"** - internals + tutorial, both, prereq: ch. 10.
    Purpose: overlay order, entity-ID outline, debug lines, gizmo registration, overlay passes via registry. Size M,
    3 screenshots, diagram 15.
13. **"Text: fonts, shaping and signed distance fields"** - concept + internals + tutorial, both, prereq: ch. 10 (and
    ch. 12). Purpose: font validation (security), FontFace/ShapeText, the SDF atlas and its budgets, TextComponent use.
    Size L, 3 screenshots, diagram 14.
14. **"Renderer reference: services, conventions and rules"** - reference, engine, prereq: ch. 2-13. Purpose: the
    `Renderer` services, fallback textures, samplers, every rule of section 5 in one place. Size S.

---

## 9. Not determined

- **Not read in full**: `SceneRenderer.cpp` beyond the parts cited (`RenderFrame` was outlined by grep and read at its
  key ranges; `CreateResources` read to l.404, `CreateSceneBindingSets` not read), `SceneRenderer.h` beyond l.60-130 and
  l.816-1119; `GPUUploadQueue.cpp` beyond `PlanStep`; `GeometryPool.cpp` (only the header); `StagingPool.cpp`,
  `TextureTable.cpp`, `GPUProfiler.cpp` beyond `GPUPassTimer`; `TextRenderer.cpp`, `FontAtlas.cpp`, `TextLayout.cpp`,
  `FontFace.cpp`, `FontValidation.cpp` (headers only); `DebugDraw.cpp`, `SceneGizmos.cpp`; `VulkanGraphicsDevice.cpp`
  `CreateInstance` (486-612), `CreateLogicalDevice` beyond l.930, `RecordQueueTransfer`/`RecordBufferToTextureCopies`
  bodies, `VulkanLoader.cpp`, `VulkanDebugMessages.cpp`; `CMake/StrataSlang.cmake`; `CMake/StrataShaderTool/*.cpp`;
  `Include/Scene.slang` was read whole, other includes only by name.
- **Tests**: test case names of the core suites were listed; bodies were read only for the triangle and camera-relative
  tests. `GPUSceneRendererTests.cpp`, `GPUAssetUploadTests.cpp`, `GPURenderSceneGPUTests.cpp` not opened.
- **ImGui renderer** (`Strata/src/Strata/ImGui/ImGuiRenderer`, NVRHI backend) is outside the Renderer folder and was not
  read; it is a good second "real" NVRHI example and should be assigned to the editor-UI or this area by the planner.
- **Intermediate render targets as screenshots**: no `viewport.capture` debug view shows raw depth, normals or entity IDs;
  whether an existing tool (look-dev harness `Tools/LookDev.py`) can export them was not checked.
- **Camera-relative "off" comparison**: the engine has no switch to disable camera-relative rendering; a before/after
  image would need an old build (pre-0.4.0) or a synthetic illustration.
- **Whether games can reach `DebugDraw` from scripts**: no host function for debug drawing was searched for; the SDK
  may not expose it (check the scripting area's inventory).
- **Exact release of several features** (deferred release queue, font validation, bindless sizing, `BufferReadback`,
  `SetJitteredDepthBias`) is not stated in the documents read; release notes 0.5.0-0.7.0 were not read in full.
- **RenderDoc/Nsight usage**: whether the documents describe capturing frames with external GPU debuggers was not
  checked (markers exist in `RenderFrame`).
- **Curiosity found, not verified as a problem**: `PostProcess/Fullscreen.vert.slang` and `Overlay/Text.frag.slang` include
  `Include/Common.slang` twice (harmless under its include guard; a by-product of the GLSL conversion).
