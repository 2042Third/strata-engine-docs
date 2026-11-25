---
id: reference/renderer
title: "Passes, bindings, switches, statistics, debug views, quality rows, device requirements"
description: "The renderer's lists in one place: GPU stages, scene bindings, switches, statistics, debug views, quality rows, fallbacks, device needs and rules."
kind: reference
size: L
tracks: []
needs: [gpu/frame-tour]
status: final
---

This page holds the facts about the :term[renderer]{id=renderer} that the engine can list: the names, slots, defaults and limits that a person finds while reading or changing renderer code. The pages about the :term[graphics processing unit]{id=gpu} (GPU) start with [the tour of a frame](../gpu/frame-tour.md); those about drawing, light, the image and indirect light teach the ideas and give the reasons. They do not keep their own copies of these lists, so a number or a name that you find on this page is the one to trust.

Most tables are generated from the engine's source, and a line above each one says where it comes from. The other tables are written by hand from the code, and each of those says so above it. A reader who wants the order of the passes and the reason for it starts with [the tour of a frame](../gpu/frame-tour.md) and comes back here for the names.

## GPU stages

A **GPU stage** is a named slice of the frame's GPU time. The profiler times each stage with timestamps and reports it as a column of the :term[runtime's]{id=runtime} performance log and a row of `editor.perf`. The engine registers :value{key="gpuStages.count"} stages. The first table lists the names by :term[source file]{id=source-file}, with the call that registers each; the renderer's stages keep frame order there, after the stages of the game's and the editor's interfaces. [GPU timing](../gpu/readback-timing.md) teaches how the times come back to the program and why they arrive a few frames late.

::include{file="gpu-stages.md"}

The next table is written by hand from the comments of `Strata/src/Strata/Renderer/GPUProfiler.cpp`, `Strata/src/Strata/Renderer/RendererQuality.cpp` and the perf command's description in `StrataEditor/src/Editor/EditorStateCommands.cpp`. Each row names what the stage times, the quality rows whose traits name the stage, and the page that teaches the pass. A stage whose quality column says none is one that no quality row names.

| Stage | What it times | Quality rows | Teaching page |
| --- | --- | --- | --- |
| `GPU.Uploads` | Copies of asset data and geometry into GPU memory | none | [Upload queue](../gpu/upload-queue.md) |
| `GPU.Setup` | Per-frame preparation, including the sky and environment updates | none | [Tour of a frame](../gpu/frame-tour.md) |
| `GPU.Aerial` | The atmosphere's aerial perspective volume | none | [Atmosphere](../light/atmosphere.md) |
| `GPU.Cull` | Culling of the render scene on the GPU | none | [GPU-driven drawing](../draw/gpu-driven.md) |
| `GPU.Shadows` | The sun's cascades, the tiles of point, spot and rect lights, and the depth ranges of the rect lights' tiles | `ShadowResolution`, `ShadowCascades`, `LocalShadowAtlasSize`, `LocalShadowMaxTile`, `MaxShadowedLocalLights`, `LocalShadowViewsPerFrame` | [Sun shadows](../light/sun-shadows-1.md), [local shadows](../light/local-shadows.md) |
| `GPU.Prepass` | The depth prepass | none | [Tour of a frame](../gpu/frame-tour.md) |
| `GPU.ScreenShadows` | The screen-space shadow masks of the sun and of the rect lights | `ShadowFilterQuality`, `ContactShadows` | [Sun shadows, part two](../light/sun-shadows-2.md) |
| `GPU.AO` | Ambient occlusion | `AmbientOcclusionQuality` | [Ambient occlusion](../indirect/ao.md) |
| `GPU.RadianceCascades` | Global illumination: voxels and light | `GlobalIllumination` | [Voxels for global illumination](../indirect/gi-voxels.md) |
| `GPU.Reflections` | Reflection probe conversions and screen-space reflections | `Reflections`, `ReflectionProbeResolution` | [Reflections](../indirect/ssr.md) |
| `GPU.Opaque` | The opaque forward pass, with the sky | `LODErrorPixels`, `MinProjectedPixels` | [Levels of detail](../draw/lod.md) |
| `GPU.Transparent` | Transparent surfaces | none | [Tour of a frame](../gpu/frame-tour.md) |
| `GPU.TAA` | Motion history and temporal anti-aliasing | `AntiAliasing` | [Temporal anti-aliasing](../image/taa.md) |
| `GPU.MotionBlur` | Motion blur | `MotionBlurQuality`, `MotionBlur` | [Motion blur](../image/motion-blur.md) |
| `GPU.DepthOfField` | Depth of field | `DepthOfField` | [Depth of field](../image/depth-of-field.md) |
| `GPU.Post` | The pass that writes the display image: tone mapping, grain, fringes | `FilmGrain`, `ChromaticAberration`, `AntiAliasing` | [Tone mapping](../image/tone-mapping.md) |
| `GPU.Overlays` | Overlays and debug views over the image | none | [Debug drawing](../gpu/debug-drawing.md) |
| `GPU.UI` | The game's interface | none | [Text and interface drawing](../gpu/text.md) |
| `GPU.ImGui` | The editor's interface | none | [ImGui](../editor-ui/imgui.md) |

## Scene bindings

A **scene binding layout** is the one list of slots that every scene pass shares: the frame's constants, the buffers and textures a pass may read, and the samplers. A slot is a register such as `t3`. The letter says the kind, and the number says the slot. The kinds are `b` :term[constant buffer]{id=constant-buffer}, `t` :term[shader]{id=shader} resource view (a buffer or texture that a shader reads), `s` sampler and `u` unordered access view (one that a shader writes). [Binding layouts](../gpu/binding.md) teaches how a layout becomes registers and how the bindless texture table sits beside it in a second set (`space1`).

The tables below are written by hand from `SceneRenderer::CreateResources` in `Strata/src/Strata/Renderer/SceneRenderer.cpp` and from the declarations of `Strata/shaders/Include/Scene.slang` and the files it includes. The layout holds no unordered access views. Slot 61 is the next free one. A new scene resource takes it, and a frame in which its pass does not run binds a dummy in its place.

| Slot | What it holds |
| --- | --- |
| `b0` | The frame's constants (`FrameConstants`): matrices, camera, time, light and exposure parameters |
| `b3` | The global illumination field's constants |
| `t0` | The instances (`InstanceData`, 64 :term[bytes]{id=byte} each) |
| `t1` | The materials |
| `t2` | The lights |
| `t3`, `t4`, `t5`, `t6` | Irradiance map, prefiltered environment map, bidirectional reflectance distribution function (BRDF) lookup table, environment map |
| `t7` | The sun's shadow cascades (a texture array) |
| `t8` | The atlas of point and spot light shadows |
| `t9`, `t10` | The reflection probes' cube array and their records |
| `t11` | Ambient occlusion |
| `t12` | The light indices of each cluster |
| `t13` | The shadowed point and spot lights |
| `t14` | The draw list |
| `t15` | Joint matrices, read by the skinned vertex shaders only |
| `t16` | The :term[texture table]{id=texture-table-strata}: material data names textures by its indices |
| `t17` | The shadow cascades' fitted data |
| `t18` | Screen-space reflections |
| `t19` | The copy of the scene's color that glass reads |
| `t20`, `t21` | The previous frame's instances and joint matrices, for motion vectors |
| `t27` | The atmosphere's sky-view table |
| `t28` | The sun's screen-space shadow mask |
| `t29` | The aerial perspective volume |
| `t32` | The cascades' depth ranges |
| `t33` | The blue-noise tile |
| `t35` | The global illumination field |
| `t37`, `t38`, `t39`, `t40` | The probes' validity and the voxel levels 0 to 2 |
| `t54` | The probes' depth moments |
| `t55` | The probes' ambient cubes |
| `t56` | The rect lights' lookup table (`Renderer::GetAreaLightTable`) |
| `t57` | The lights' faces, entry for entry beside the lights of `t2` |
| `t58` | The depth ranges of the point, spot and rect light shadow atlas |
| `t59` | The rect lights' screen-space shadow masks |
| `t60` | The rect lights' back faces: a second atlas of the same tiles |
| `s0` to `s5` | The six material samplers: two filters times three wrap modes |
| `s8` | Linear filtering, clamped edges |
| `s9` | The shadow comparison sampler |
| `s10` | Point filtering, clamped edges |

Slots 22 to 26 belong to the compute layouts of temporal anti-aliasing and screen-space reflections, never to the scene layout. Slots 30, 31, 34 and 36 are assigned in the slot list of `Scene.slang` to the irradiance volume and to fog, and the layout does not bind them at this commit. Slots 41 to 53 belong to the light passes of global illumination, which read the field too.

:term[Push constants]{id=push-constants} share the `b` registers with the constant buffers. A pipeline that pairs the scene layout with push constants gives them a register that no constant buffer of its other layouts uses. The sun's cascade passes, for example, push one 32-bit value at register 1, because register 0 holds the frame's constants. [The shader dialect](../gpu/shaders.md) gives the rule and its reason.

## Switches

A **switch** here is a field of `SceneRendererSpecification`, the :term[struct]{id=struct} that a program completes when it creates a renderer. The first table below lists those fields with their types, defaults and the engine's own comments. The same file also declares `SceneRendererStats`, the counters of a frame, so the second half of the table is the list of statistics that the [statistics section](#statistics) explains. The pages of [lights](../light/many-lights.md), [drawing](../draw/gpu-driven.md) and [the image chain](../image/quality-settings.md) each name the switches they tune and link here for the rest.

::include{file="renderer.md"}

Five switches have no menu entry and no project setting: `GPUDriven`, `OcclusionCulling`, `VisibilityFeedback`, `FadeLevelsOfDetail` and `BatchAcrossMaterials`. The programs leave them at the defaults in the table, and only code that creates a renderer, or the `renderer` parameter of `viewport.capture` for one picture, changes them. They exist so that tests can compare two paths of the same frame, and so that a contributor can turn one path off while hunting a bug. A person who wants to change what the renderer costs uses the [quality rows](#quality-rows) instead, because those are the settings a project stores.

Other switches, such as `SpecularEnergyCompensation`, `HorizonFade`, `SpatialReflectionResolve` and `FXAASubpixel`, also change only in the editor's captures, through the same parameter. They show what one technique adds, and every other renderer keeps them at the defaults.

## Statistics

A **statistic** is a counter or a measure that a renderer records for each frame it draws. `SceneRendererStats` holds them as fields, and the editor reports a selection of them as the `renderStats` object of `viewport.capture` and `editor.perf`. The engine reports :value{key="renderStats.count"} keys at this commit. A row of the next table gives a key, the field it comes from and a description. A nested key (`cascades.near`) lives inside its parent object, and the table of the previous section lists the fields themselves.

::include{file="render-stats.md"}

Three rules read every row. A name that ends in `Ms` is a time in milliseconds, and a name that ends in `Bytes` is a size in bytes. Any other name that holds a number counts things, such as draw calls, instances or lights. The table below is written by hand from the field names and gives the page that teaches each family. Fields from `PreExposure` on belong to the image chain, and each page of [the image chain](../image/exposure.md) names only its own.

| Family | Typical fields | Teaching page |
| --- | --- | --- |
| Draw and culling counts | `DrawCalls`, `Instances`, `Triangles`, `CulledInstances`, `OccludedProxies` | [Bounds and culling](../draw/bounds-culling.md), [occlusion](../draw/occlusion.md) |
| Batching and GPU-driven counts | `GPUDriven`, `GPUCulled`, `DrawCommands`, `FeedbackRequests` | [Batching](../draw/batching.md), [GPU-driven drawing](../draw/gpu-driven.md) |
| Render scene upload counts | `InstanceBytesUploaded`, `ProxyUpdates`, `DeferredProxies`, `ExtractMs`, `SortMs` | [The render scene](../draw/render-scene.md) |
| Asset requests | `PendingAssets`, `RequestsByVisibility`, `PrefetchRequests` | [Asset requests](../draw/asset-requests.md) |
| Skinning | `SkinnedInstances`, `StalePoses`, `PaletteBytesUploaded` | [Skinned meshes](../draw/skinned.md) |
| Lights | `Lights`, `AreaLights`, `CulledLights`, `DroppedLights` | [Many lights](../light/many-lights.md) |
| Shadows | `ShadowCasters`, `CachedCascadeMask`, `LocalShadowRequested`, `LocalShadowLights`, `AreaShadowMasks` | [Sun shadows](../light/sun-shadows-1.md), [local shadows](../light/local-shadows.md) |
| Sky and fog | `Atmosphere`, `AerialPerspective`, `HeightFog`, `SunTransmittance` | [Atmosphere](../light/atmosphere.md), [fog](../light/fog.md) |
| Indirect light | `ReflectionProbes`, `ScreenSpaceReflections`, `GlobalIllumination`, `GIVoxelizedTriangles` | [Probes](../indirect/probes.md), [global illumination](../indirect/gi-voxels.md) |
| Ambient occlusion | `AmbientOcclusionSamples` | [Ambient occlusion](../indirect/ao.md) |
| Motion and anti-aliasing | `MotionHistory`, `TemporalFrames`, `HistoryResets`, `Jitter` | [Motion vectors](../draw/motion-vectors.md), [temporal anti-aliasing](../image/taa.md) |
| Image chain | `PreExposure`, `MotionBlurred`, `DepthOfField`, `BloomLevels`, `Dithered` | [Exposure](../image/exposure.md), [tone mapping](../image/tone-mapping.md) |
| Text and overlays | `Texts`, `TextGlyphs`, `DebugLines`, `Overlays` | [Text](../gpu/text.md), [debug drawing](../gpu/debug-drawing.md) |

## Debug views

A **debug view** replaces the lit image with a picture of one quantity, such as the level of detail or the ambient occlusion. `viewport.capture` takes a `debugView` parameter, and the editor's viewport has the same choice. The engine offers :value{key="debugViews.count"} values. The generated table lists the value names, and the sentence above it in its file explains the extra data that some views return. [Measuring light](../light/measuring-light.md) and [debugging the GPU](../gpu/debugging.md) teach how to read each picture.

::include{file="debug-views.md"}

The table below is written by hand from the same source and from the lighting view constants of `Strata/shaders/Include/Scene.slang`. It says what each value shows and where to learn it.

| Value | What it shows | Teaching page |
| --- | --- | --- |
| `none` | The normal image | none |
| `streaming` | Entities tinted by the state of their assets: pending, failed, or a missing mesh drawn as a box | [Mip streaming](../draw/mip-streaming.md) |
| `lod` | The level of detail each mesh draws | [Levels of detail](../draw/lod.md) |
| `mip` | The mip levels that the textures lack | [Mip streaming](../draw/mip-streaming.md) |
| `motion` | The motion of each pixel since the previous frame of the capture | [Motion vectors](../draw/motion-vectors.md) |
| `shadows` | Screen pixels per shadow texel, and the outlines of the cascades | [Sun shadows, part two](../light/sun-shadows-2.md) |
| `lighting` | Lighting on white surfaces, without emission | [Measuring light](../light/measuring-light.md) |
| `ao` | The occlusion of indirect light | [Ambient occlusion](../indirect/ao.md) |
| `indirect` | Indirect light only | [Measuring light](../light/measuring-light.md) |
| `luminance` | The lit image in bands of exposure value | [Units and exposure](../light/units-exposure.md) |
| `albedo` | Base colors, with values outside the physical range marked | [Materials](../light/materials.md) |
| `voxels` | The voxels of global illumination | [Voxels for global illumination](../indirect/gi-voxels.md) |
| `gi` | The diffuse light that global illumination adds, on white | [Cascades of global illumination](../indirect/gi-cascades.md) |
| `open` | The share of the sky that a surface sees through the world | [Cascades of global illumination](../indirect/gi-cascades.md) |
| `probes` | The probes of global illumination | [Voxels for global illumination](../indirect/gi-voxels.md) |
| `specular` | Only the highlights and reflections, without emission or fog | [The forward shader](../light/brdf.md) |
| `diffuse` | Only the diffuse light, without emission or fog | [The forward shader](../light/brdf.md) |
| `clusters` | How many lights each pixel's cluster lists, in bands of powers of two | [Many lights](../light/many-lights.md) |
| `culled` | Boxes over the mesh renderers in view that culling omitted: too small, or hidden | [Occlusion culling](../draw/occlusion.md) |
| `wireframe` | The edges of every triangle drawn, over the image; omitted where the device cannot draw lines | [Debugging the GPU](../gpu/debugging.md) |

## Quality rows

A **quality row** is one costly knob of the renderer, such as the sun's shadow resolution. Each row is a field of `RendererQualitySettings` and of the `Renderer.Quality` settings section. The four presets (`Low`, `Medium`, `High` and `Ultra`) give every row a value, and the preset Custom keeps the values that a project or a player chose. [Quality settings](../image/quality-settings.md) teaches the design: rows change only cost, never a scene's look, and the players' rows may disable what a scene uses, never enable more.

The generated table gives each row's value in the four presets and the description of the settings schema, then the fields that no preset sets. Quote a value in prose only through `:value{key="quality.<field>.<preset>"}`, because the presets are tuned from release to release. High is the default.

::include{file="quality.md"}

The table below is written by hand from the `c_RowTraits` list and the section schema of `Strata/src/Strata/Renderer/RendererQuality.cpp`. A **players' row** is a row that the presets leave alone: it is comfort or preference, not cost, and the game's graphics options read it under every preset. The last column is the range that Custom accepts. Where the engine corrects a value, it clamps a number into the range and replaces an unknown choice with the Medium preset's value or `Scene`.

| Row | Players' row | GPU stage | Memory counted | Custom accepts |
| --- | --- | --- | --- | --- |
| `ShadowResolution` | no | `GPU.Shadows` | cascades | `Auto`, `AutoFine`, `1024`, `2048`, `4096`, `8192` |
| `ShadowCascades` | no | `GPU.Shadows` | with the resolution | `1` to `5` |
| `LocalShadowAtlasSize` | no | `GPU.Shadows` | the atlas, and with a shadowed rect light its back faces and depth ranges | `1024`, `2048`, `4096`, `8192` |
| `LocalShadowMaxTile` | no | `GPU.Shadows` | none | `256`, `512`, `1024`, `2048` |
| `MaxShadowedLocalLights` | no | `GPU.Shadows` | with the atlas | `0` to `4096` |
| `LocalShadowViewsPerFrame` | no | `GPU.Shadows` | none | `1` to `1024` |
| `LODErrorPixels` | no | `GPU.Opaque` | none | `0` to `8` |
| `MinProjectedPixels` | no | `GPU.Opaque` | none | `0` to `8` |
| `ShadowFilterQuality` | no | `GPU.ScreenShadows` | none | `8`, `16`, `24`, `32` |
| `ContactShadows` | no | `GPU.ScreenShadows` | none | `0`, or `4` to `32` steps (`1` to `3` count as `4`) |
| `AmbientOcclusionQuality` | no | `GPU.AO` | none | `Low`, `Medium`, `High`, `Ultra` |
| `EnvironmentResolution` | no | none: the sky is filtered only when it changes | the sky's map | `256`, `512` |
| `Reflections` | no | `GPU.Reflections` | the traced targets | `Off`, `Checkerboard`, `Spatial`, `SpatialHigh` |
| `MotionBlurQuality` | no | `GPU.MotionBlur` | the blur's targets | `Off`, `Samples8`, `Samples12`, `Samples16` |
| `ReflectionProbeResolution` | no | `GPU.Reflections` | the probes' cubes | `128`, `256` |
| `GlobalIllumination` | no | `GPU.RadianceCascades` | the field and voxels | `Off`, `Low`, `High` |
| `AntiAliasing` | yes | the chosen method's own: `GPU.TAA` or `GPU.Post` | none | `Scene`, `Off`, `FXAA`, `Morphological`, `TAA` |
| `MotionBlur` | yes | `GPU.MotionBlur` | counted with the samples | `Scene`, `Off` |
| `DepthOfField` | yes | `GPU.DepthOfField` | none | `Scene`, `Off` |
| `FilmGrain` | yes | `GPU.Post` | none | `Scene`, `Off` |
| `ChromaticAberration` | yes | `GPU.Post` | none | `Scene`, `Off` |

## Fallback textures and common samplers

While a real texture streams in, the renderer binds a one-texel stand-in, so that a pass never waits and never reads nothing. The **Renderer** class creates the stand-ins and four samplers once, when it starts, in `Strata/src/Strata/Renderer/Renderer.cpp`. The scene passes bind their own samplers too (the table of bindings above). The stand-ins appear in the next table, and [the device and the renderer's services](../gpu/vulkan-nvrhi.md) teaches the class that owns them.

| Accessor | What it is | Used for |
| --- | --- | --- |
| `GetWhiteTexture` | One white texel, 8 bits per channel | The reserved white slot of the bindless table, and the sun's shadow mask of frames without it (fully lit) |
| `GetBlackTexture` | One opaque black texel | The sky-view table, the glass copy and the reflections texture of frames without them |
| `GetFlatNormalTexture` | One texel of exactly (0.5, 0.5, 1, 1) in half floats | The neutral normal that points straight out of a surface |
| `GetBlackCubeTexture` | A black cube map | The environment and irradiance maps of a scene that has none |
| `GetBlackCubeArrayTexture` | A cube array holding one black cube | The reflection probes of a scene that has none |
| `GetBlueNoiseTexture` | A 64 by 64 tile of one 8-bit channel | Per-pixel values that filters index by the screen pixel |
| `GetBlack3DTexture` | A 1 by 1 by 1 black 3D texture | The aerial perspective volume in frames without it |
| `GetZero3DUintTexture` | A 1 by 1 by 1 texture of the 32-bit :term[unsigned integer]{id=unsigned-integer} 0 | The probes' depth moments in frames without global illumination |

The flat normal is stored in half floats because 8 bits cannot hold 0.5: the nearest value, 128 out of 255, tilted a surface by 0.3 degrees. One more texture is no stand-in: `GetAreaLightTable` holds the rect lights' lookup tables, layers of 64 by 64 texels of four 32-bit floats. The class writes it before the first frame and never changes it. The samplers are the other half of the class.

| Accessor | Filtering | Edges |
| --- | --- | --- |
| `GetLinearClampSampler` | Linear | Clamped |
| `GetLinearWrapSampler` | Linear | Repeating |
| `GetPointClampSampler` | Nearest texel | Clamped |
| `GetAnisotropicWrapSampler` | Linear, `maxAnisotropy` of 16 | Repeating |

## Device requirements

A **device requirement** is a capability that the graphics device must have before the engine uses it. The device selection in `Strata/src/Platform/Vulkan/VulkanGraphicsDevice.cpp` rejects a device that lacks any of the required ones and logs the reason. If no device remains, startup fails with an error that lists the main requirements, and the log lines before it give each skipped device's reason. The first table below is the required set, and it is written by hand from that file. [The device and NVRHI](../gpu/vulkan-nvrhi.md) teaches what a device, a queue and a feature are.

| Requirement | Detail |
| --- | --- |
| :term[Vulkan]{id=vulkan} version | 1.2 or later, for the instance and the adapter |
| Dynamic rendering | Core in Vulkan 1.3; on 1.2 the extension and its feature |
| Synchronization 2 | Core in Vulkan 1.3; on 1.2 the extension and its feature |
| :term[Semaphores]{id=semaphore} | The `timelineSemaphore` feature |
| :term[Descriptor]{id=descriptor} indexing | Runtime arrays, :term[partially bound]{id=update-after-bind} arrays, non-uniform indexing of sampled images, and update after bind with updates of unused slots while pending |
| Sampler feature | `samplerAnisotropy` |
| Cube map arrays | `imageCubeArray`, because the one scene layout holds the probes' cube array |
| A :term[queue family]{id=queue-family} | Graphics and compute together, and presentation unless the device runs headless |
| The :term[swapchain]{id=swapchain} extension | Unless the device runs headless |

When several devices qualify, the engine scores them: one point for each `MiB` of device-local memory, plus a million for a discrete GPU or a hundred thousand for an integrated one. The highest score wins.

The swapchain is chosen after the device. The surface format is `B8G8R8A8_UNORM`, or `R8G8B8A8_UNORM` if that is absent, with the `SRGB_NONLINEAR` :term[color space]{id=color-space}, because the engine writes display-encoded values itself, and a surface that offers neither makes the swapchain fail. The :term[present mode]{id=present-mode} is FIFO (:term[vertical synchronization]{id=vsync}) when the player asks for it. Without vertical synchronization the engine takes `MAILBOX`, then `IMMEDIATE`, and falls back to FIFO, which every device supports. The image count is one more than the larger of the surface's minimum and the :term[frames in flight]{id=frames-in-flight}, clamped to the surface's maximum.

The capabilities below are not required. `GraphicsDeviceInfo`, in `Strata/src/Strata/Renderer/GraphicsDevice.h`, records them and the renderer switches paths by them, never by the :term[operating system]{id=operating-system}.

| Field | Meaning |
| --- | --- |
| `SupportsBCCompression` | Block-compressed textures |
| `SupportsWireframe` | Drawing triangles as outlines |
| `SupportsExtendedStorageFormats` | :term[Storage images]{id=uav} of formats such as 16-bit float and 8-bit single channel |
| `SupportsTimestamps` | The graphics queue writes timestamps, so GPU stages have times |
| `TimestampPeriodNs` | Nanoseconds per timestamp tick |
| `SupportsMultiDrawIndirect` | Several draws per indirect call |
| `SupportsDrawIndirectFirstInstance` | Indirect arguments that set the first instance |
| `SupportsDrawIndirectCount` | Draw counts that the GPU writes |
| `MaxDrawIndirectCount` | The most draws one indirect call may issue (1 without multi-draw) |
| `SupportsSamplerMinMax` | Samplers that return the minimum or maximum of the texels they filter |
| `MaxTextureDimension2D` | The longest side of a 2D texture or render target |
| `MaxBindlessTextures` | Slots of the bindless texture table, at most 32,768, fewer where the device's limits allow fewer |
| `IsDiscreteGPU`, `DedicatedVideoMemory` | The kind of device and its device-local memory |
| `ValidationEnabled` | Whether the Vulkan :term[validation layer]{id=validation-layer} is active |

## The renderer's rules

The renderer follows a set of rules whose breaking produces bugs that tests rarely catch. This table is written by hand from the rendering rules of `AGENTS.md` at the pin and from the engine's inventory of renderer rules, and it is checked again when the pin moves. A row says the rule in a line and links the page that gives the reason. The rules of a topic share one page, so a link may serve several rows.

### Core and conventions

| Rule | Reason and page |
| --- | --- |
| Take no address of an NVRHI handle | [The device and NVRHI](../gpu/vulkan-nvrhi.md) |
| Dispatches through one binding set that read each other's writes need explicit barriers | [Binding layouts](../gpu/binding.md) |
| Drop render targets through `Renderer::ReleaseDeferred` | [Lifetimes of GPU resources](../gpu/resources-lifetimes.md) |
| Call `Renderer::PrepareBackBuffer()` before drawing into the :term[back buffer]{id=back-buffer} | [The device and NVRHI](../gpu/vulkan-nvrhi.md) |
| Copies from released staging memory execute before the batch is submitted | [Upload queue](../gpu/upload-queue.md) |
| Never block a frame on an asset or on the GPU; poll readbacks | [Readback and timing](../gpu/readback-timing.md) |
| Write bindless slots only at allocation; resolve slots every frame | [Binding layouts](../gpu/binding.md) |
| Read mesh geometry through the pool every frame | [Geometry pool](../gpu/geometry-pool.md) |
| Time every new pass in a GPU stage, in frame order | [Readback and timing](../gpu/readback-timing.md) |
| A new scene resource takes the next free slot of the slot list | [Binding layouts](../gpu/binding.md) |
| Fullscreen pass coordinates flip: row 0 is the top | [Coordinates](../gpu/coordinates.md) |
| Depth is reversed: near is 1, far is 0 | [Coordinates](../gpu/coordinates.md) |
| Front faces wind counterclockwise | [Coordinates](../gpu/coordinates.md) |
| Gate on device features, never on the operating system | [The device and NVRHI](../gpu/vulkan-nvrhi.md) |
| Font files are untrusted input; measure text by shaping, never by drawing | [Text](../gpu/text.md) |
| GPU tests share one device and end with no new errors | [Debugging the GPU](../gpu/debugging.md) |

### Shaders

| Rule | Reason and page |
| --- | --- |
| List every shader entry in the build; configure again after adding one | [Shaders](../gpu/shaders.md) |
| Write Slang in the style of `HLSL`: no generics, no target switches outside the common include | [Shaders](../gpu/shaders.md) |
| Use `mul` only with a matrix | [Shaders](../gpu/shaders.md) |
| Compare vectors through `all` and `any`; matrix :term[constructors]{id=constructor} take rows | [Shaders](../gpu/shaders.md) |
| Sample with an explicit level in compute | [Shaders](../gpu/shaders.md) |
| Give every storage image a format | [Shaders](../gpu/shaders.md) |
| Take derivatives before the first `discard` | [Shaders](../gpu/shaders.md) |
| A push constant never shares a register with another layout's constant buffer | [Binding layouts](../gpu/binding.md) |
| Clamp every write to a :term[high dynamic range]{id=high-dynamic-range} (HDR) target with `SanitizeHDR` | [Tone mapping](../image/tone-mapping.md) |
| Normal maps read two channels; the third is rebuilt | [Materials](../light/material-data.md) |

### Drawing a scene

| Rule | Reason and page |
| --- | --- |
| Signal every write to a transform or mesh renderer | [The render scene](../draw/render-scene.md) |
| Never resolve assets per entity; use the proxies and the frame's cache | [Asset requests](../draw/asset-requests.md) |
| Hold asset handles across frames, never references | [Asset requests](../draw/asset-requests.md) |
| Log every change of instances or proxies | [The render scene](../draw/render-scene.md) |
| Keep `InstanceData` at 64 bytes; add parallel buffers | [The render scene](../draw/render-scene.md) |
| Change the rule of the :term[central processing unit]{id=processor} (CPU) path and the rule of the GPU path together | [GPU-driven drawing](../draw/gpu-driven.md) |
| Shading must not depend on draw order | [GPU-driven drawing](../draw/gpu-driven.md) |
| The prepass and the forward pass produce identical positions | [Tour of a frame](../gpu/frame-tour.md) |
| Occlusion culling stays conservative | [Occlusion culling](../draw/occlusion.md) |
| Anything new that changes how casters are drawn bumps a version that the shadow caches compare | [Sun shadows](../light/sun-shadows-1.md) |
| Skinning work costs scenes without skinned meshes nothing | [Skinned meshes](../draw/skinned.md) |
| Mirrored instances use clockwise pipelines and flipped tangents | [Mirrors and camera-relative space](../draw/mirrors-camera-relative.md) |
| Upload positions relative to the camera, subtracted in double | [Mirrors and camera-relative space](../draw/mirrors-camera-relative.md) |
| Previous-frame data lives in each renderer, never in the shared copy | [Motion vectors](../draw/motion-vectors.md) |

### Direct light and shadows

| Rule | Reason and page |
| --- | --- |
| Every intensity has a unit, and no hidden factor changes it | [Units and exposure](../light/units-exposure.md) |
| HDR writers multiply by the pre-exposure; readers divide it out | [Pre-exposure](../image/pre-exposure.md) |
| Light keeps its energy; check with the white furnace and the debug views | [Energy conservation](../light/energy.md) |
| The flat normal is exactly flat; the reflectance at index 1.5 stays 0.04 | [Reflectance](../light/reflectance.md) |
| A light's size widens only its highlight | [Lights](../light/lights.md) |
| Cascade layouts come only from the view; nothing is read back | [Sun shadows](../light/sun-shadows-1.md) |
| The sun's shadow reaches opaque and transparent surfaces by two paths: change both | [Sun shadows, part two](../light/sun-shadows-2.md) |
| The sun's filters use fixed noise, never the frame's | [Sun shadows, part two](../light/sun-shadows-2.md) |
| Point and spot shadows never blink: importance, hysteresis, fades by time, old tiles until new ones are drawn, fixed noise | [Local shadows](../light/local-shadows.md) |
| Rect lights are light records with faces; change their shading function, its include and its GPU test together | [Lights](../light/lights.md) |
| A mesh that shows a rect light's face carries a marker; reflections, probe captures and rect light shadows omit it | [Lights](../light/lights.md) |
| Only one directional light shines; fog is not a volume | [Fog](../light/fog.md) |

### Image chain

| Rule | Reason and page |
| --- | --- |
| Pre-exposure is a power of two, divided out exactly | [Pre-exposure](../image/pre-exposure.md) |
| Read the exposure back only by polling, never by waiting | [Exposure](../image/exposure.md) |
| Post effects take push constants or their own buffers, not new frame constants | [Why post-processing](../image/why-post.md) |
| A post effect runs between the temporal resolve and tone mapping, and is off in the neutral setup | [Why post-processing](../image/why-post.md) |
| Neutral settings render bit for bit unchanged | [Grading](../image/grading.md) |
| Dither once, in the last pass; the dither is static | [Encoding](../image/encoding.md) |
| Jitter only the frame's copy of the camera | [Temporal anti-aliasing](../image/taa.md) |
| History belongs to the renderer and is counted in frames | [Temporal anti-aliasing](../image/taa.md) |
| Single images settle or turn temporal anti-aliasing off | [Temporal anti-aliasing](../image/taa.md) |
| Quality rows change cost, never a scene's look | [Quality settings](../image/quality-settings.md) |
| Never render below the output's resolution | [Quality settings](../image/quality-settings.md) |
| Never change the numbers of enum values that files store; append new ones | [Quality settings](../image/quality-settings.md) |

### Indirect light

| Rule | Reason and page |
| --- | --- |
| Diffuse gets what specular leaves | [Energy conservation](../light/energy.md) |
| Ambient occlusion darkens indirect light only, with no history | [Ambient occlusion](../indirect/ao.md) |
| Screen-space reflections keep only validated crossings and fade only where rays leave the screen | [Reflections](../indirect/ssr.md) |
| Checkerboard reflections need temporal anti-aliasing | [Reflections](../indirect/ssr.md) |
| The editor bakes reflection probes; the running game never does | [Probes](../indirect/probes.md) |
| A feature that is off costs nothing and leaves the image bit for bit unchanged | [Image-based lighting](../indirect/ibl.md) |
| Global illumination traces world data, never the screen | [Voxels for global illumination](../indirect/gi-voxels.md) |
| Its constants live in their own buffer, not in the frame's | [Voxels for global illumination](../indirect/gi-voxels.md) |
| Moving objects stay out of the voxels for a time; worlds stay within the supported extent | [Limits of global illumination](../indirect/gi-limits.md) |

## Where it lives in Strata

- `Strata/src/Strata/Renderer/SceneRenderer.h`: `SceneRendererSpecification` and `SceneRendererStats`.
- `Strata/src/Strata/Renderer/SceneRenderer.cpp`: `SceneRenderer::CreateResources`, which builds the scene binding layout.
- `Strata/shaders/Include/Scene.slang`: the slot list and the lighting view constants.
- `Strata/src/Strata/Renderer/GPUProfiler.cpp`: the registration of the GPU stages.
- `Strata/src/Strata/Renderer/RendererQuality.cpp`: the rows, the presets, the traits and the section schema.
- `Strata/src/Strata/Renderer/Renderer.cpp`: the fallback textures and the common samplers.
- `Strata/src/Platform/Vulkan/VulkanGraphicsDevice.cpp`: the device selection and the swapchain.
- `Strata/src/Strata/Renderer/GraphicsDevice.h`: `GraphicsDeviceInfo`.
- `StrataEditor/src/Editor/EditorStateCommands.cpp`: `editor.perf` and the `renderStats` object.
- `StrataEditor/src/Editor/EditorViewportCommands.cpp`: `viewport.capture` and its `debugView` parameter.
- `tools/reference.py`: the generator of the included tables.
