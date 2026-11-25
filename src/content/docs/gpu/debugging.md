---
id: gpu/debugging
title: "Debugging the GPU: validation, frame captures, the error count and debug views"
description: "Find out why a frame looks wrong or a GPU test fails: read validation messages, stop at the call that caused one, capture a frame and switch debug views."
kind: how-to
size: M
tracks: [E]
needs: [gpu/first-triangle, core/debugging]
time: 50
learn:
  - id: read-messages
    text: explain how Strata logs and counts a message of the graphics driver or of NVRHI, and which reports it demotes on purpose
  - id: find-call
    text: find the call that caused a validation error by stopping in the message callback
  - id: read-capture
    text: find a pass of the frame in a capture by its marker, and say why its shaders show no source lines
  - id: pick-tool
    text: choose between validation, a frame capture and a debug view for a frame that looks wrong
  - id: name-views
    text: name what each debug view of the Scene view shows and the page that teaches reading it
since: 0.3.0
status: final
---

A frame can go wrong in three ways, and each has its own tool. This page shows how to tell them apart: you run with validation, read its messages, stop at the call that caused one, capture a frame and switch the Scene view's debug views. Before you start:

- You have a Debug build of the pin with its editor, as `core/first-change` shows.
- A copy of the Showcase sample is open in that editor, as `start/first-game` shows.
- RenderDoc or Nsight Graphics is installed, for the capture step.

## Three faults, three tools

A graphics program can fail in three different ways. Sometimes it asks the :term[graphics processing unit]{id=gpu} (GPU) for something the rules forbid, which is misuse of the application programming interface (API); the :term[validation layer]{id=validation-layer} reports it. Sometimes it asks correctly, but the data is wrong, as when a buffer holds old numbers; a frame capture shows that. Sometimes the data is right and the image still looks wrong: the light is too dark, a texture is too soft. The Scene view's debug views show that.

The order matters. Validation costs nothing to read, so you ask it first. A capture shows what the card received, so you look at it next. A debug view colors the image by one measured quantity, so it answers questions about the look. The figure sums up the choice.

```mermaid caption="Choose the tool from the symptom: errors in the log point to validation, wrong numbers in a pass point to a capture, and a wrong look with correct numbers points to a debug view." alt="A decision diagram. A wrong frame leads to a question about errors in the log: yes leads to validation messages. No leads to a question about the data of a pass: yes leads to a frame capture, and no leads to a debug view."
flowchart TD
    A[Wrong frame] --> B{Errors in the log?}
    B -->|yes| C[Validation messages]
    B -->|no| D{Data of a pass wrong?}
    D -->|yes| E[Frame capture]
    D -->|no| F[Debug view]
```

A **debug view** is a mode of the Scene view that replaces the image with the color of one measured quantity. One example is the level of detail each mesh is drawn at.

## Find the fault

:::::steps

1. Run with validation, and learn when it is on.

   The validation layer is a program that sits between Strata and the driver and checks each call against the rules of :term[Vulkan]{id=vulkan}. Strata's device creation enables it in a Debug build and leaves it off in the other configurations, unless the program says otherwise. In the test program it is on unless the :term[environment variable]{id=environment-variable} `STRATA_TEST_GPU_VALIDATION` is `0`; the performance tests set it to `0`, because checking costs time. `gpu/vulkan-nvrhi` teaches what the layer checks and why Release and :term[Dist]{id=dist} builds do without it.

   **You should see:** in the editor's log, the line that names the device, `Graphics device: ...`, ending in `, validation enabled`.

   **If you do not see it:** the log may warn `Vulkan validation requested but VK_LAYER_KHRONOS_validation is not installed`. Then install the Vulkan software development kit (SDK); until then only :term[NVRHI's]{id=nvrhi} own checks run.

2. Read a message in the log.

   Every message of the layer reaches one :term[callback]{id=callback} in `Strata/src/Platform/Vulkan/VulkanGraphicsDevice.cpp`. The callback sorts it into three cases: an error, a warning or a trace. An error is logged with the prefix `Vulkan:` at error level and adds one to the device's error count. A warning is logged at warning level and does not count. A trace goes to the trace level, the lowest, where it adds detail but never reads as a problem.

   Strata counts errors, and does not only print them, for a reason that suits tests. A test that finishes with a log full of red lines still passes unless something compares the count with zero. The count is the one number a test can check.

   **You should see:** lines such as `Vulkan: Validation Error: ...` followed by the name of the rule, then the objects involved.

   **If you do not see it:** the layer found nothing, which is good. The frame may still be wrong; go to step 7.

3. Recognize the reports Strata lowers on purpose.

   Four reports are no fault of the engine, and Strata lowers their severity instead of failing every run. The first is :term[MoltenVK's]{id=moltenvk} `Blending is enabled for attachment with format` report on macOS: MoltenVK repeats it for every color target whose format Metal cannot blend, such as the prepass's entity identifiers, even when the pipeline does not blend. The second is the layer's report of a descriptor set layout beyond the driver's limits, when the driver's support query under-reports the bindless table; the layer still checks every set. The third is the loader's search for a validation layer it lists but cannot load. The loader reports a missing file as an error, so Strata logs it as a warning, and the instance is created again without the layer.

   The fourth is the loader's account of that search, which it reports as warnings; Strata makes them traces.

   The function that decides is short. Read it once, because the same function tells you what an unknown message will become.

   ```cpp src="Strata/src/Platform/Vulkan/VulkanDebugMessages.cpp#L24-L51"
   VulkanMessageDisposition ClassifyVulkanMessage(const VulkanMessage& message, const VulkanMessageContext& context)
   {
   	if (message.Error)
   	{
   		// The validation layer's report of a descriptor set layout beyond the device's limits that the driver's support
   		// query rejects. Where the query under-reports the bindless table, it says nothing about the table; the layer
   		// still checks every set against the update-after-bind limits.
   		if (context.SupportQueryUnderReportsBindlessTable && Equals(message.IdName, "VUID-vkCreateDescriptorSetLayout-support-09582"))
   			return VulkanMessageDisposition::Trace;
   		// The loader's reports of a validation layer it lists but cannot load (its library's search, "Requested layer ...
   		// failed to load!"): the instance is created again without the layer, which is no error of the device.
   		if (context.CreatingInstanceWithLayers && Equals(message.IdName, "Loader Message"))
   			return VulkanMessageDisposition::Warning;
   		return VulkanMessageDisposition::Error;
   	}
   	if (!message.Warning)
   		return VulkanMessageDisposition::Trace;

   	// The loader reports its search (e.g. missing registry keys for layer manifests) as warnings.
   	if (Equals(message.IdName, "Loader Message"))
   		return VulkanMessageDisposition::Trace;
   	// MoltenVK reports every color attachment whose format Metal cannot blend (the prepass's R32_UINT entity IDs) as
   	// "Blending is enabled ...", whether or not the pipeline blends it, and creates the pipeline without blending. The
   	// engine never blends such a target; doing so would be invalid usage, which the validation layer reports as an error
   	// (VUID-VkGraphicsPipelineCreateInfo-renderPass-06062, -06041 with render passes) where it is loaded.
   	if (Equals(message.IdName, "mvk-warn") && Contains(message.Text, "Blending is enabled for attachment with format"))
   		return VulkanMessageDisposition::Trace;
   	return VulkanMessageDisposition::Warning;
   ```

   1. **Lines 31–32:** the bindless support query is the first exception, and only while the device knows that the query under-reports.
   2. **Lines 35–36:** the loader's error becomes a warning, and only while the instance is created with layers.
   3. **Line 37:** an error that no exception names is counted. This is the default: Strata never hides an error by guessing.
   4. **Lines 43–44:** the loader's search is a trace, not even a warning, because the loader reports missing registry keys on most computers.
   5. **Lines 49–50:** MoltenVK's blending report is a trace, since the engine never blends those targets.

   **You should see:** with these exceptions, a Debug run of the editor on a healthy computer ends with an error count of 0.

   **If you do not see it:** a count above 0 is a real finding. Do not add an exception for it; the exceptions above each name a cause outside the engine.

4. Read NVRHI's own errors.

   NVRHI is the library between Strata and Vulkan. In Debug builds and in tests it wraps the device in its own validation. That validation checks rules that Vulkan cannot know: a draw before any graphics state is set, a binding that the pipeline does not expect, a :term[command list]{id=command-list} used before it is opened. Its messages arrive in a second callback, and the two callbacks add to one error count.

   ```cpp src="Strata/src/Platform/Vulkan/VulkanGraphicsDevice.cpp#L89-L105"
   void message(nvrhi::MessageSeverity severity, const char* messageText) override
   {
   	switch (severity)
   	{
   		case nvrhi::MessageSeverity::Info:
   			ST_CORE_TRACE("NVRHI: {}", messageText);
   			break;
   		case nvrhi::MessageSeverity::Warning:
   			ST_CORE_WARN("NVRHI: {}", messageText);
   			break;
   		case nvrhi::MessageSeverity::Error:
   		case nvrhi::MessageSeverity::Fatal:
   			ST_CORE_ERROR("NVRHI: {}", messageText);
   			ErrorCount.fetch_add(1);
   			break;
   	}
   }
   ```

   1. **Line 91:** NVRHI reports a severity of its own: information, warning, error or fatal.
   2. **Line 94:** information goes to the trace level, so it never reads as a problem.
   3. **Lines 99–102:** an error and a fatal one are logged with the prefix `NVRHI:` and counted, as the Vulkan layer's errors are.

   NVRHI's validation is not part of Dist builds. A Dist device that asks for it logs a warning, `NVRHI validation is not part of Dist builds`, and runs without it.

   **You should see:** the text of the rule that broke, for example `Graphics state is not set before a draw call.`

   **If you do not see it:** the program may be a Release or Dist build, whose device validates nothing by default.

5. Use the error count in a test, and stop where it grows.

   A GPU test creates a `Tests::GPUContext`, as `gpu/first-triangle` shows. The context remembers the count at its start, and `GetNewErrorCount()` returns the current count minus that start. Suppose the shared device had counted 7 errors before your test began, and 9 after it: the test sees 2. A test ends with `CHECK(gpu.GetNewErrorCount() == 0)`, so any error that its own calls cause fails it.

   A failed check says that an error happened, not where. To find the call, set a :term[breakpoint]{id=breakpoint} on the line `ErrorCount.fetch_add(1);` of the NVRHI callback, and one on the line `state->ErrorCount.fetch_add(1);` of the Vulkan callback, line 127. Run the one test case under your :term[debugger]{id=debugger}, as `core/debugging` shows. The program stops inside the callback while the offending call is still on the stack; the :term[call stack]{id=call-stack} window then lists the engine function and the line of your test that made the call.

   **You should see:** the debugger stopped in `message` or `DebugUtilsCallback`, with a frame of your own code a few lines below on the call stack.

   **If you do not see it:** the breakpoint may never fire because validation is off. Check that `STRATA_TEST_GPU_VALIDATION` is not `0` in the debugger's environment.

6. Give resources names and passes markers.

   A capture is only as clear as its names. Strata gives each texture and buffer a `debugName` when it creates it, and prefixes the names of the scene :term[renderer's]{id=renderer} own targets with the renderer's name and a dot, as in `ShadowMap` and `BRDFLut`. The editor makes three scene renderers named `Viewport`, `GameView` and `ViewportCapture`. The renderer also opens a marker with its own name around the whole frame and a marker around each pass: `Shadows`, `Prepass`, `Opaque`, `Transparent`, `TAA` and the others, in the order of `gpu/frame-tour`.

   A marker is a label that the driver records in the command stream, and a capture tool draws it as a folder. NVRHI writes each marker as a Vulkan debug label where the extension for them exists. When you add a pass or a target of your own, name it in the same way, or the capture shows a list without names.

   **You should see:** the target names, each led by the name of its renderer, in the capture's resource list.

   **If you do not see it:** a resource without a name was made by code that left `debugName` empty; fix that code.

7. Capture a frame and find the pass.

   Start the editor from the capture tool, so that the tool loads before the graphics driver does. With RenderDoc, choose the editor's :term[executable]{id=executable}, set the :term[working folder]{id=current-folder} to the folder of the build, and launch. With Nsight Graphics, start a frame :term[debugging]{id=debugging} activity for the same executable. Press the capture key of the tool once the Showcase scene is drawn, then open the capture.

   The event list shows a tree: a folder named `Viewport` for the frame, and inside it folders such as `Shadows`, `Prepass`, `Opaque`. Open `Opaque`, select a draw, and open its texture viewer: the inputs and outputs of that draw are the pictures it read and wrote. Compare the output of `Prepass` with the output of `Opaque` to see where a surface lost its color.

   A capture shows :term[shaders]{id=shader} without source lines. Strata compiles them with :term[slangc]{id=slang} but without its `-g` option, because the output would then depend on the configuration and on the paths of the source folders. The tool shows the compiled instructions, and you match them to the `.slang` file by the names of the :term[entry points]{id=entry-point-gpu}. `CMake/StrataShaders.cmake` explains the choice, and `Docs/Roadmap.md` lists a debug option as not done.

   **You should see:** one folder per pass of `gpu/frame-tour`, in the order the frame runs them.

   **If you do not see it:** if the tree is flat, the driver lacked the debug label extension. Search for `VK_EXT_debug_utils` in the tool's list of extensions.

8. Switch a debug view.

   A capture does not help when the numbers are right and the picture looks wrong. At the top of the Scene view, click the chip with the layers icon, which opens a menu of views. Choose one and the image turns into a measurement. Choose **Lit (no debug view)** to return.

   **You should see:** the image changes color at once; a chip label names the active view, such as `Lighting` or `Voxels`.

   **If you do not see it:** if you switched to a view whose subject is not in the scene, the image looks plain: `Motion` shows nothing on a still scene.

:::::

### The debug views

The menu offers these views. Each row says what the view shows and where to learn to read it. The editor's legend calls its yellow Sulfur; the other colors are green, blue and red.

| View | What it shows | Where to read it |
| --- | --- | --- |
| `streaming` | Entities whose mesh, material or textures are still loading in yellow, failed ones in red, missing meshes as boxes | `draw/asset-requests` |
| `lod` | The level of detail each entity is drawn at, from 0 to 3 or more: green, blue, yellow, red | `draw/lod` |
| `mip` | The mip levels a texture lacks against what the view needs: none green, one blue, two yellow, three or more red | `draw/mip-streaming` |
| `motion` | How far each pixel moved since the previous frame: the hue is the direction, the strength the speed | `draw/motion-vectors` |
| `shadows` | Screen pixels per shadow texel on receivers, and the sun's cascades outlined | `light/sun-shadows-1` |
| `lighting` | Every lit surface white, so that you see the light alone | `light/measuring-light` |
| `ao` | The occlusion that darkens indirect light, white where there is none | `indirect/ao` |
| `indirect` | Only the light of the sky, the probes and reflections | `light/measuring-light` |
| `luminance` | The brightness of the scene in bands of exposure value (EV100) | `light/measuring-light` |
| `albedo` | Base colors, with values below 0.03 marked blue and above 0.85 striped red | `light/measuring-light` |
| `voxels` | The voxel grid that global illumination sees instead of the scene | `indirect/gi-voxels` |
| `specular` | Only the highlights and reflections, without the diffuse light | `light/brdf` |
| `diffuse` | Only the diffuse light, without highlights or reflections | `light/brdf` |
| `clusters` | How many lights each pixel's light cluster lists, one color per power of two, up to a full cluster | `light/many-lights` |
| `culled` | Boxes over what culling omitted: yellow for too small, red for hidden behind other objects | `draw/occlusion` |
| `wireframe` | The edges of the triangles the frame drew, with their count in the legend | `draw/lod` |

Global illumination adds three more views, `gi`, `open` and `probes`, and `indirect/gi-voxels` teaches them with `voxels`. The `culled` view marks no hidden objects on the path where the :term[central processing unit]{id=processor} (CPU) chooses the draws, which has no occlusion culling. A card without support for lines draws no `wireframe`; the legend then says so.

A worked example with the `shadows` view: the sun's shadow map gives each texel a patch of ground. If a texel covers 2 screen pixels, the receiver is yellow; at 4 or more it is red, and the shadow edge is visibly coarse. Green means at most 1 pixel per texel. A coarse shadow in the image together with red in this view says that the cascade is too coarse there, not that the filter is broken.

## Result

You can now sort a wrong frame by cause. An error count above 0 is API misuse, and the message callback finds the call. Wrong numbers in a pass are data, and a capture shows them. A wrong look with right numbers is a debug view's question.

## Variations

**Nsight in place of RenderDoc.** Nsight Graphics shows the same marker tree, because the markers are Vulkan labels and not a feature of one tool. It adds counters for the card, which help when a pass is slow rather than wrong.

**macOS and MoltenVK.** The validation layer may be absent, so only NVRHI's checks and the driver's own run. MoltenVK adds reports of its own; step 3 names the one Strata lowers. A capture on macOS needs a tool that supports the Metal platform; the steps above otherwise hold.

**A failing GPU test in place of the editor.** Run only the test case under a debugger with validation on, and follow steps 4 and 5. The test shares one device with its suite, so a count that grows in one test case may come from an earlier one: `GetNewErrorCount()` counts from the start of this test's context.

**A debug view saved to a file.** A command can capture the viewport with a debug view without the chip. Run this line in a terminal, with the editor open:

```sh
StrataCLI call viewport.capture '{"debugView": "shadows", "path": "shadows.png"}'
```

The command writes `shadows.png` into the project folder; `editor/commands` teaches how to read and run commands.

**A technique switched for one capture.** The same command can draw one picture with a technique of the renderer disabled, to show what the technique adds. Its `renderer` object takes fields of `SceneRendererSpecification` by name. The capture draws through a renderer of its own, so the Scene view, the Game view and the game never change. This line saves the Showcase without specular anti-aliasing:

```sh
StrataCLI call viewport.capture '{"renderer": {"SpecularAntiAliasing": false}, "path": "no-specular-aa.png"}'
```

Compare that picture with one taken without `renderer`. The result's `renderer` repeats the switches the capture used. The table lists the switches named most often and the page that teaches each technique.

| Switch | What changes when it is false or 0 | Where to read it |
| --- | --- | --- |
| `SpecularAntiAliasing` | Highlights no longer widen where the normal changes across a pixel, so they sparkle | `light/brdf` |
| `SpecularEnergyCompensation` | Rough metal loses the light of multiple scattering and looks darker | `light/energy` |
| `DitherOutput` | The 8-bit output shows the bands of smooth gradients | `image/encoding` |
| `GlobalIlluminationBounceGain` | At 0, global illumination bounces light once | `indirect/gi-cascades` |
| `OcclusionCulling` | The GPU draws what lies behind other objects too | `draw/occlusion` |
| `TextureStreaming` | Every texture drawn is loaded whole, at all its levels | `draw/mip-streaming` |
| `HorizonFade` | Reflections that a normal map turns into the surface no longer fade | `indirect/ibl` |

Automatic exposure measures each capture alone. A switch that changes the light also changes the exposure, so compare such pictures with a fixed exposure.

## Summary

- Strata sorts every Vulkan message into error, warning or trace; errors and NVRHI's errors add to one count that a test compares with zero, and four reports are lowered on purpose.
- A breakpoint in the message callbacks stops with the offending call on the stack.
- A capture shows named resources and one marker folder per pass, and its shaders carry no source lines because slangc runs without its debug option.
- Errors point to validation, wrong data to a capture, and a wrong look with right data to a debug view.
- The Scene view's debug views show streaming, detail, mips, motion, shadows, light, the global illumination's voxels, light clusters, culling and triangle edges, and each has a page that teaches reading it. The command `viewport.capture` with `renderer` disables a technique for one picture, to show what it adds.

## Check yourself

1. A test ends with `CHECK(gpu.GetNewErrorCount() == 0)` and the log shows a yellow warning from the layer. Does the check fail?

   :::answer{tests="read-messages"}
   No. A warning is logged and does not count. Only an error of the Vulkan layer or of NVRHI adds to the count.
   :::

2. The shared device had counted 12 errors when your test case began. At its end the count is 12. What does `GetNewErrorCount()` return, and what does that say?

   :::answer{tests="read-messages"}
   The call returns 0, the current count minus the count at the start. Your calls caused no error, even if earlier tests did.
   :::

3. A check fails with the count at 1. Where do you put the breakpoint, and what do you read when it fires?

   :::answer{tests="find-call"}
   On the line `ErrorCount.fetch_add(1);` of the callback that logged the error, `message` for NVRHI or `DebugUtilsCallback` for Vulkan. The call stack lists the engine function and the line of your test below the callback.
   :::

4. You open a capture and the shaders show only instructions. Why, and how do you find the source?

   :::answer{tests="read-capture"}
   Strata compiles shaders without slangc's `-g` option, so a capture has no source lines. Match the entry point's name to the `.slang` file.
   :::

5. A shadow looks coarse and the `shadows` view shows red there. Which tool found the fault, and which page teaches the next step?

   :::answer{tests="pick-tool name-views"}
   A debug view, because the data is right but the look is wrong. `light/sun-shadows-1` teaches how to read it.
   :::

6. The log shows no error, and an object is black. A capture shows its albedo texture is empty at `Opaque`. Which of the three faults is it?

   :::answer{tests="pick-tool"}
   Wrong data: the call was legal, so validation is silent, and the capture shows the content of the texture.
   :::

## Exercises

1. **Basic.** Run the editor, switch the debug view to `mip` and name which color means that a texture lacks three or more levels.

   :::answer{tests="name-views"}
   Red. None lacking is green, one level is blue, two is yellow.
   :::

2. **Medium.** In a scratch copy of the triangle test, break an NVRHI rule on purpose, run the test with validation and find the line that caused the error through the message callback. Use a scratch branch and a Debug build.

   :::answer[Worked solution]{tests="read-messages find-call" solution="tutorials/gpu/debugging/exercise-1.patch"}
   The patch removes `commandList->setGraphicsState(state);` from the test `Triangle rendering follows the engine's clip-space conventions`. Run `StrataTests --test-case="Triangle rendering*"` under your debugger with a breakpoint on `ErrorCount.fetch_add(1);` in the NVRHI callback. It stops with the message `Graphics state is not set before a draw call.` The call stack lists `draw` of NVRHI's validation layer and, below it, the line of the test with `commandList->draw`. The rule broken is that a draw needs a graphics state first. The test then also fails its pixel checks, since nothing was drawn, and `GetNewErrorCount()` is 1.
   :::

3. **Medium.** Use the command of the last variation to save the `albedo` view of the Showcase to a file, and state what the striped red areas mean.

   :::answer{tests="name-views"}
   Replace `"shadows"` by `"albedo"` in the command. Striped red marks base colors above 0.85, which a real surface seldom has; blue marks values below 0.03.
   :::

4. **Hard.** A teammate adds a pass named `Fog`, and in a capture its draws sit loose inside the `Viewport` folder, with no folder of their own. Which lines did the teammate omit, and how do you check the fix?

   :::answer{tests="read-capture"}
   The command list needs a `beginMarker("Fog")` before the pass and an `endMarker()` after it. Capture a frame again and search for a `Fog` folder in the event list.
   :::

## Where it lives in Strata

- `Strata/src/Platform/Vulkan/VulkanGraphicsDevice.cpp`: the Vulkan callback (`DebugUtilsCallback`), the NVRHI callback (`NvrhiMessageCallback`), `GetErrorCount`, and the layer's lookup.
- `Strata/src/Platform/Vulkan/VulkanDebugMessages.cpp`: `ClassifyVulkanMessage`, the lowered reports.
- `Strata/src/Strata/Renderer/GraphicsModule.cpp`: the Debug default of `Validation`.
- `Strata/src/Strata/Renderer/SceneRenderer.cpp`: the frame's marker and one marker per pass.
- `StrataTests/src/Renderer/GPUTestUtils.cpp` and `GPUTestUtils.h`: `Tests::GPUContext`, `GetNewErrorCount`, `STRATA_TEST_GPU_VALIDATION`.
- `CMake/StrataShaders.cmake`: the flags slangc does not get, `-g` among them.
- `StrataEditor/src/Panels/ViewportPanel.cpp` and the command `viewport.capture` in `StrataEditor/src/Editor/EditorViewportCommands.cpp`.
- `StrataEditor/src/Editor/ViewportRenderer.cpp`: `CaptureRendererSwitches`, the switches a capture's `renderer` takes; `StrataEditor/src/Editor/StreamingView.cpp`: the debug views' names and legends.

## Further reading

- [RenderDoc documentation](https://renderdoc.org/docs/): capturing a frame, the event browser and the texture viewer; beginner.
- [Khronos validation layers](https://github.com/KhronosGroup/Vulkan-ValidationLayers): the layer's source and its list of checks; intermediate.
- [NVRHI](https://github.com/NVIDIA-RTX/NVRHI): the library's validation layer and its message callback; intermediate.
