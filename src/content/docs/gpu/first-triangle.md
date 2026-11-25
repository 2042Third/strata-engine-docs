---
id: gpu/first-triangle
title: "Tutorial: your first triangle in Strata"
description: "Run, read and break the engine's triangle test, then add a shader of your own and prove its pixels with a new GPU test."
kind: tutorial
size: L
tracks: [E]
needs: [core/first-change, gpu/shaders, gpu/coordinates]
time: 120
learn:
  - id: run-test
    text: run one GPU test case on its own and read the summary of its run
  - id: trace-draw
    text: trace a GPU test from its shader through the draw to the pixels it reads back
  - id: predict-pixels
    text: predict which pixels of a rendered image a triangle in normalized device coordinates covers
  - id: add-shader
    text: add a shader to the registry and name the edits that need a new configure step
  - id: write-test
    text: write a GPU test that shares the device, reads pixels back and ends with the error count
since: 0.3.0
status: final
---

## What you will make

You will run the engine's smallest test of the engine that uses the :term[graphics processing unit]{id=gpu} (GPU). The test draws one triangle and checks two pixels of the result. Then you
break it on purpose, add a :term[shader]{id=shader} of your own and write the test that proves its pixels.

::figure{id=result}

## What you need

- The source build of [your first engine change](../core/first-change.md): the engine at the book's commit in your own
  build folder, configured with the preset of your system and built in `Debug`. The test program `StrataTests` must
  exist in `build/<preset>/bin/Debug/`.
- A terminal, as in that tutorial, and a computer whose GPU has a :term[Vulkan]{id=vulkan} 1.2 driver. The test
  program draws without a window, but it needs a real device. Without one, the first step stops at the first check.
- No project, sample or editor. You change three files of the engine: a shader, the list of shaders and a test file.
- Time: about two hours. Each build after the first compiles little, but a shader change compiles the shader and links
  the test program again.
- Every file you write is in the patch of this page, and each section says which part of it you are adding. The patch
  applies to the engine at the book's commit.

:::files[The files you read and change]

- `GameEngine/` your clone
  - `Strata/shaders/Debug/`
    - **ColorTriangle.vert.slang**, **ColorTriangle.frag.slang**: the triangle's two shaders; you read them
    - **Checker.frag.slang**: your shader
  - `Strata/CMakeLists.txt`: the list of registered shaders; you add one line
  - `StrataTests/src/Renderer/`
    - **GPURendererTests.cpp**: the triangle test; you read it, and add your test beside it
    - **GPUTestUtils.h**, **GPUTestUtils.cpp**: the shared device; you read them

:::

## Run the triangle test

A GPU test is a doctest test case that draws with the real graphics device. You first run the existing one, to know
what a passing run looks like before you change anything. The suite is named `GPU.Renderer`, and the test case is
named "Triangle rendering follows the engine's clip-space conventions".

:::::steps

1. Run only this test case. The filter `--test-case` takes the name of a test case, and `*` stands for any characters,
   so one short start of the name is enough.

   ::::tabs{sync=os}
   :::tab[Windows]

   ```powershell
   build\windows\bin\Debug\StrataTests.exe --test-case="Triangle rendering follows*"
   ```

   PowerShell waits for a console program, so the output appears before the next prompt.

   :::
   :::tab[Linux]

   ```sh
   ./build/linux/bin/Debug/StrataTests --test-case="Triangle rendering follows*"
   ```

   The leading `./` runs a program from the :term[current folder]{id=current-folder}.

   :::
   :::tab[macOS]

   ```sh
   ./build/macos/bin/Debug/StrataTests --test-case="Triangle rendering follows*"
   ```

   :::
   ::::

   **You should see:** the output ends with three lines that start with `[doctest]`. The first counts
   the test cases, `1 | 1 passed`, and then the number of test cases the filter skipped. The second counts the checks:
   this test has 7, so it reads `7 | 7 passed | 0 failed`. The third reads `Status: SUCCESS!`.

   **If you do not see it:** when the run stops at `REQUIRE( gpu.IsValid() )`, the program found no usable Vulkan
   device. Install a current graphics driver and try again. When doctest counts 0 test cases, the filter matched no
   name: copy the name from the test file.

2. Run the whole suite, to know how long a GPU test takes and that its neighbours pass.

   ::::tabs{sync=os}
   :::tab[Windows]

   ```powershell
   build\windows\bin\Debug\StrataTests.exe --test-suite=GPU.Renderer
   ```

   The filter `--test-suite` runs every test case of the suites whose name matches.

   :::
   :::tab[Linux]

   ```sh
   ./build/linux/bin/Debug/StrataTests --test-suite=GPU.Renderer
   ```

   A name with `*` matches several suites, as `GPU*` does.

   :::
   :::tab[macOS]

   ```sh
   ./build/macos/bin/Debug/StrataTests --test-suite=GPU.Renderer
   ```

   :::
   ::::

   The suite holds several test cases of the renderer.

   **You should see:** `Status: SUCCESS!` again, with all test cases passed. The first GPU test of the run is the
   slowest, because it creates the device; the rest use it again.

   **If you do not see it:** a failing neighbour has nothing to do with your work yet. Note its name, and compare it
   with a run on the unchanged book commit before you continue.

:::::

The run printed no word about triangles, but a failed pixel check would have named the pixel. The test passes only
when a triangle was drawn to the place the engine's conventions say. The next section reads the test, so that the
numbers of the passing line mean something.

## Read what the test does

The test has three parts: a shader that holds one triangle, a draw that renders it, and two checks on the pixels. You
read them in that order. The shader comes first, because everything else exists to show its result.

:::why[A triangle without a vertex buffer]
A vertex buffer is memory that holds the corners of a mesh, and a pipeline reads it through a layout that describes
each field. Keeping the corners in the shader removes that layout, the buffer and the upload from the smallest test:
only the shader, the pipeline and the target remain. The cost is that the shape changes only by editing the shader and
compiling again, which is what a test of a convention wants and what a model never wants. The engine's fullscreen
passes use the same trick, as you see later on this page.
:::

The shader you read next puts two corners at the middle of the image and one at the top, so the triangle should stand on the
middle line like a tent. Work it out with numbers first. The target has 64 pixels in each direction. The conversion from
:term[clip space]{id=clip-space} to pixels, for a target of $64$ pixels with row 0 at the top, is

$$x_{pix} = 64 \cdot (0.5 \cdot x + 0.5), \qquad y_{pix} = 64 \cdot (0.5 - 0.5 \cdot y)$$

$x$ and $y$ are the clip-space coordinates and run from -1 to 1. $x_{pix}$ and $y_{pix}$ are the position in pixels,
counted from the left edge and from the top edge. Put in the three corners: $(-1, 0)$ becomes $(0, 32)$, $(1, 0)$
becomes $(64, 32)$ and $(0, 1)$ becomes $(32, 0)$. The triangle has its base on the row 32 and its tip at the top
of the image. The pixel $(32, 16)$ lies inside it, and the pixel $(32, 48)$ lies below the base, outside it.

The check at the limits agrees. A corner with $y = 1$ gives $y_{pix} = 64 \cdot 0 = 0$, the top row, and $y = -1$ gives
64, the bottom edge. This is the rule of [clip space and coordinates](coordinates.md): +Y is up in clip space, and row 0 is
the top of the image.

:::::steps

1. Open `Strata/shaders/Debug/ColorTriangle.vert.slang` and read the data of the triangle.

   ```slang src="Strata/shaders/Debug/ColorTriangle.vert.slang#L6-L15"
   static float3 v_Color;

   static const float2 c_Positions[3] = { float2(-1.0, 0.0), float2(1.0, 0.0), float2(0.0, 1.0) };
   static const float3 c_Colors[3] = { float3(1.0, 0.0, 0.0), float3(1.0, 0.0, 0.0), float3(1.0, 0.0, 0.0) };

   void st_Main()
   {
   	v_Color = c_Colors[st_VertexIndex];
   	st_Position = float4(c_Positions[st_VertexIndex], 0.5, 1.0);
   }
   ```

   1. **Line 8:** three positions in clip space, one for each corner: left, right and top of the middle line of the
      image. The `float2` values are x and y.
   2. **Line 9:** one color for each corner. All three are red, so every pixel of the triangle is red.
   3. **Line 13:** the vertex shader picks the color of its own vertex by the number of the vertex.
   4. **Line 14:** the position leaves as four numbers. The depth is 0.5, and the last number, `w`, is 1.0 so that the
      coordinates stay as they are.

   **You should see:** the shader has no input from a buffer. Its three corners are constants of the program.

   **If you do not see it:** the file you opened is `ColorTriangle.frag.slang`, whose body only copies a color to the
   output.

2. Read the rest of the file, the part that connects `st_Main` to the pipeline.

   ```slang src="Strata/shaders/Debug/ColorTriangle.vert.slang#L17-L35"
   // --- Entry point ---
   struct ST_Input
   {
   };
   struct ST_Output
   {
   	[[vk::location(0)]] float3 v_Color : TEXCOORD0;
   	float4 st_Position : SV_Position;
   };
   ST_Output main(ST_Input input, int vertexIndex : SV_VulkanVertexID, int instanceIndex : SV_VulkanInstanceID)
   {
   	st_VertexIndex = vertexIndex;
   	st_InstanceIndex = instanceIndex;
   	st_Main();
   	ST_Output output;
   	output.v_Color = v_Color;
   	output.st_Position = st_Position;
   	return output;
   }
   ```

   1. **Line 26:** `main` is the entry of the shader. Its input `SV_VulkanVertexID` is the number of the vertex that
      the draw call is processing: 0, 1 or 2.
   2. **Line 28:** the engine's shaders keep that number in a global of their own, `st_VertexIndex`, which `st_Main`
      reads on line 13.
   3. **Line 30:** the body of the shader runs here.
   4. **Line 33:** the position goes out in `SV_Position`, the output the GPU reads to find which pixels the
      triangle covers.

   **You should see:** `ST_Input` is empty. No vertex buffer feeds this shader.

   **If you do not see it:** when the file looks different, you are not at the commit of the book. Compare `git log -1`
   with the commit the first tutorial gave.

3. Read how the test makes its target and pipeline. The test file is
   `StrataTests/src/Renderer/GPURendererTests.cpp`.

   ```cpp src="StrataTests/src/Renderer/GPURendererTests.cpp#L131-L148"
   TEST_CASE("Triangle rendering follows the engine's clip-space conventions")
   {
   	Tests::GPUContext gpu;
   	REQUIRE(gpu.IsValid());
   	nvrhi::IDevice* device = gpu.GetNvrhiDevice();

   	constexpr uint32_t size = 64;
   	nvrhi::TextureHandle target = CreateRenderTarget(device, size, size, nvrhi::Format::RGBA8_UNORM);
   	nvrhi::FramebufferHandle framebuffer = device->createFramebuffer(nvrhi::FramebufferDesc().addColorAttachment(target));

   	nvrhi::GraphicsPipelineDesc pipelineDesc;
   	pipelineDesc.VS = Renderer::GetShaderLibrary().Get("Debug/ColorTriangle.vert");
   	pipelineDesc.PS = Renderer::GetShaderLibrary().Get("Debug/ColorTriangle.frag");
   	pipelineDesc.primType = nvrhi::PrimitiveType::TriangleList;
   	pipelineDesc.renderState.rasterState.setCullNone();
   	pipelineDesc.renderState.depthStencilState.setDepthTestEnable(false).setDepthWriteEnable(false);
   	nvrhi::GraphicsPipelineHandle pipeline = device->createGraphicsPipeline(pipelineDesc, framebuffer->getFramebufferInfo());
   	REQUIRE(pipeline);
   ```

   1. **Lines 133–135:** the test takes the shared device. `GPUContext` is the helper of the next steps.
   2. **Line 138:** a render target of 64 by 64 pixels, with four 8-bit channels (`RGBA8_UNORM`): the image the
      triangle is drawn into.
   3. **Lines 142–143:** the shaders come from the engine's `ShaderLibrary`, by the names registered in
      `Strata/CMakeLists.txt`.
   4. **Lines 145–146:** no culling and no depth test, so nothing but the corners of the triangle decides what is drawn.
   5. **Line 148:** `createGraphicsPipeline` builds the pipeline for this target, and `REQUIRE` stops the test when
      that fails.

   **You should see:** nothing in the pipeline mentions a vertex buffer or a layout of inputs.

   **If you do not see it:** line numbers that differ by a few mean another commit; read by the names instead.

4. Read the commands the test records, and the readback.

   ```cpp src="StrataTests/src/Renderer/GPURendererTests.cpp#L150-L160"
   nvrhi::CommandListHandle commandList = device->createCommandList();
   commandList->open();
   commandList->clearTextureFloat(target, nvrhi::AllSubresources, nvrhi::Color(0.0f, 0.0f, 1.0f, 1.0f));
   nvrhi::GraphicsState state;
   state.pipeline = pipeline;
   state.framebuffer = framebuffer;
   state.viewport.addViewportAndScissorRect(nvrhi::Viewport(static_cast<float>(size), static_cast<float>(size)));
   commandList->setGraphicsState(state);
   commandList->draw(nvrhi::DrawArguments().setVertexCount(3));
   commandList->close();
   device->executeCommandList(commandList);
   ```

   1. **Line 152:** the clear fills the whole target with blue, the color the test calls its background.
   2. **Line 156:** the viewport and the scissor rectangle cover the whole 64 by 64 target.
   3. **Line 158:** `draw` with a vertex count of 3: the vertex shader runs three times, with the vertex numbers 0, 1 and 2.
   4. **Line 160:** the commands go to the graphics queue. They run later, on the GPU.

   **You should see:** the test records into a :term[command list]{id=command-list} and submits it once, as every frame of the engine does.

   **If you do not see it:** none of these lines draws by itself. A draw is a command in a list, and the list runs when it
   is executed.

5. Read the last part: the readback, the two pixels and the error count.

   ```cpp src="StrataTests/src/Renderer/GPURendererTests.cpp#L162-L172"
   	ReadbackImage image;
   	REQUIRE(Renderer::ReadTexture(target, image));
   	REQUIRE(image.Width == size);

   	// The triangle spans NDC y in [0, 1]: with +Y up that is the TOP half of the image (row 0 = top).
   	const glm::u8vec4 top = Tests::GetPixelRGBA8(image, size / 2, size / 4);
   	const glm::u8vec4 bottom = Tests::GetPixelRGBA8(image, size / 2, size * 3 / 4);
   	CHECK(top == glm::u8vec4(255, 0, 0, 255));
   	CHECK(bottom == glm::u8vec4(0, 0, 255, 255));
   	CHECK(gpu.GetNewErrorCount() == 0);
   }
   ```

   1. **Line 163:** `Renderer::ReadTexture` copies the target to the :term[central processing unit]{id=processor} (CPU) and waits until the copy is done. It
      blocks, so only tests and tools may call it.
   2. **Lines 167–168:** the two pixels. `size / 4` is row 16, the middle of the upper half, and `size * 3 / 4` is row 48.
   3. **Lines 169–170:** the upper pixel must be red and the lower pixel the blue of the clear. The four numbers are
      red, green, blue and alpha, each from 0 to 255.
   4. **Line 171:** no validation error was reported since the test began.

   **You should see:** two pixel checks and one error check, 3 of the 7 checks of the run. The other 4 are the
   `REQUIRE` lines.

   **If you do not see it:** when `GetPixelRGBA8` is unknown to you, it reads the 4 :term[bytes]{id=byte} of one pixel from the image
   data, row by row.

:::::

The test is the whole life of a GPU program in one function, and the next picture shows its order. A shader, a
pipeline, a recorded draw, a wait and a check follow one another.

```mermaid caption="The test builds a pipeline from two shaders, records one draw into a command list, waits for the GPU, reads the pixels back and checks them." alt="Six boxes in a row, joined by arrows: shaders, pipeline, command list with clear and draw, GPU executes, readback of the target, pixel and error checks."
flowchart LR
  A[Shaders] --> B[Pipeline]
  B --> C[Command list: clear, draw]
  C --> D[GPU executes]
  D --> E[ReadTexture]
  E --> F[Pixel and error checks]
```

Lines 133 and 171 use `GPUContext`, the helper every GPU test starts with. A GPU test never creates a graphics
device of its own. It makes a `GPUContext`, which gives the test the one device that the whole test program shares.
Here is its :term[constructor]{id=constructor}.

```cpp src="StrataTests/src/Renderer/GPUTestUtils.cpp#L29-L50"
GPUContext::GPUContext()
{
	SharedGPU& shared = GetSharedGPU();
	if (!shared.Initialized)
	{
		shared.Initialized = true;
		GraphicsDeviceSpecification specification;
		specification.ApplicationName = "StrataTests";
		specification.Headless = true;
		// Validation layers multiply the CPU cost of every GPU call, so the perf tests measure without them: their
		// CTest (StrataTests.PerfGPU) sets STRATA_TEST_GPU_VALIDATION=0. Everything else validates.
		const std::optional<std::string> validation = Platform::GetEnvVar("STRATA_TEST_GPU_VALIDATION");
		specification.EnableValidation = !validation || *validation != "0";
		shared.Device = GraphicsDevice::Create(specification);
		if (shared.Device && !Renderer::Init(*shared.Device))
			shared.Device.reset();
	}

	m_Device = shared.Device.get();
	if (m_Device)
		m_InitialErrorCount = m_Device->GetErrorCount();
}
```

1. **Lines 32–34:** the first test that makes a context creates the device. Every later test finds it ready.
2. **Lines 40–41:** validation is on, unless the :term[environment variable]{id=environment-variable} `STRATA_TEST_GPU_VALIDATION` is exactly `0`. The
   perf tests set it to `0`, because validation multiplies the cost of every GPU call.
3. **Lines 42–44:** the device is headless, with no window, and `Renderer::Init` makes the renderer's own resources.
   When either fails, the context is invalid, and the test's first `REQUIRE` says so.
4. **Lines 47–49:** the context remembers the number of errors the device had reported so far. `GetNewErrorCount`
   subtracts it, so each test sees only its own errors.

The :term[destructor]{id=destructor} waits until the GPU is idle and releases what the renderer deferred, so each test starts from a quiet
device. One more member matters later: `ExecuteAndWait` executes a command list, waits for it and recycles its command
buffer. Tests that submit many lists use it, because a list that is never recycled makes a new command pool at each
`open()`. The triangle test submits one list and reads the result with `ReadTexture`, which waits by itself.

:::rule[GPU tests share one device]
Every GPU test makes a `GPUContext`, never a device of its own, and ends with
`CHECK(gpu.GetNewErrorCount() == 0)`. The test program creates its Vulkan device once, as a game does. Creating and
destroying instances again and again is no use that the engine has, and the :term[header]{id=header} `GPUTestUtils.h` says that some
drivers and overlay layers handle that churn poorly. The cost is shared state: a test that damages the device harms the
next one, so the context drains the device when a test ends. [The kinds of tests](../engineering/test-kinds.md)
describes the GPU suites.
:::

:::question[Why does the error count matter if the pixels are right?]
A :term[validation layer]{id=validation-layer} reports misuse of Vulkan that a driver may still accept: a wrong resource state, a missing barrier. The pixels can look right on your machine and be wrong on another. The count turns such a report into a failed check.
:::

## Break the convention on purpose

A test that cannot fail proves nothing. You prove that this one can by moving the triangle to the lower half, which
breaks the convention the test guards. This is the same habit as the broken `ToUpper` of
[your first engine change](../core/first-change.md).

:::::steps

1. Move the triangle. In `Strata/shaders/Debug/ColorTriangle.vert.slang`, change the third position of `c_Positions` on
   line 8 from `float2(0.0, 1.0)` to `float2(0.0, -1.0)`. Its base stays on the middle line, and its tip moves to the
   bottom of the image.

   Then make the test show its pixels. In `GPURendererTests.cpp`, after the line that defines `bottom`, add the two
   lines `INFO("top pixel ", int(top.r), " ", int(top.g), " ", int(top.b));` and
   `INFO("bottom pixel ", int(bottom.r), " ", int(bottom.g), " ", int(bottom.b));`. Doctest prints an `INFO` message
   with a check that fails.

   **You should see:** two edited files and no build yet. `git diff` shows the three changed lines.

   **If you do not see it:** when the edit sits in `ColorTriangle.frag.slang`, undo it: only the vertex shader holds
   the positions.

2. Build the test program and run the test case again. A shader is compiled by the build, so a changed shader needs
   only the build, not the :term[configure step]{id=configure-step}, because the list of shaders did not change.

   ::::tabs{sync=os}
   :::tab[Windows]

   ```powershell
   cmake --build build/windows --config Debug --target StrataTests --parallel
   build\windows\bin\Debug\StrataTests.exe --test-case="Triangle rendering follows*"
   ```

   The build step compiles the changed shader first and then links the test program.

   :::
   :::tab[Linux]

   ```sh
   cmake --build build/linux --config Debug --target StrataTests --parallel
   ./build/linux/bin/Debug/StrataTests --test-case="Triangle rendering follows*"
   ```

   Ninja prints one line for each step it runs.

   :::
   :::tab[macOS]

   ```sh
   cmake --build build/macos --config Debug --target StrataTests --parallel
   ./build/macos/bin/Debug/StrataTests --test-case="Triangle rendering follows*"
   ```

   :::
   ::::

   **You should see:** predict it first. The tip is now at the bottom, so the pixel $(32, 16)$ lies outside the triangle and
   keeps the blue of the clear, while the pixel $(32, 48)$ lies inside it and is red. Both pixel checks fail. Doctest
   names the file and the line of each one, writes `is NOT correct!` and prints the context: `top pixel 0 0 255` and
   `bottom pixel 255 0 0`. The summary counts `7 | 5 passed | 2 failed` checks and ends with `Status: FAILURE!`.

   **If you do not see it:** when the run still passes, the build did not take your edit: read the end of the build output
   for the shader. When nothing builds, check the new corner for a missing bracket.

3. Restore both files with :term[git]{id=git}, and run the test case once more.

   ```sh
   git restore Strata/shaders/Debug/ColorTriangle.vert.slang StrataTests/src/Renderer/GPURendererTests.cpp
   ```

   Build and run as in the last step.

   **You should see:** `Status: SUCCESS!` again with 7 checks passed.

   **If you do not see it:** `git status` lists the files that still differ from the commit. Restore each of them.

:::::

The failure shows what the test protects. A change to the clip-space convention, for example a viewport that flips the
image or a shader that moves the corners, turns two numbers of a pixel into other numbers, and the test names which.
That is the strength of a pixel test: it checks the result a person would see, not the code that makes it.

## Add a shader of your own

A fullscreen pass draws one triangle that covers the whole target, and its fragment shader decides each pixel. You write
such a fragment shader: a checkerboard that also shows which way the vertical axis of the :term[texture coordinates]{id=texture-coordinates} runs. The
engine already has the vertex shader for it, `PostProcess/Fullscreen.vert`, and its shader draws with a vertex count of 3
like the triangle you read earlier.

The :term[fullscreen triangle's]{id=fullscreen-triangle} corners are $(-1, -1)$, $(3, -1)$ and $(-1, 3)$ in clip space. The target shows only the
square from $-1$ to $1$, and the triangle covers all of it. The vertex shader also passes on the texture coordinates
$uv = (0.5 \cdot x + 0.5, \; 0.5 - 0.5 \cdot y)$, the rule of [clip space and coordinates](coordinates.md). $u$ grows to the right and $v$
grows downwards, from 0 at the top edge to 1 at the bottom edge. The checker uses $uv$ in two ways.

The first use is the cell. Multiply $uv$ by 8 and drop the fraction: the pixel $(12, 4)$ has $uv = (0.1953, 0.0703)$ at its center, which times 8 is
$(1.5625, 0.5625)$, so it lies in the cell $(1, 0)$. A cell whose column and row add up to an even number is red, and the
cell $(1, 0)$ adds up to 1, so it is not. The second use is the half: when $v$ is below 0.5, the pixel is in the upper half
of the image, and the shader adds green.

:::::steps

1. Create the file `Checker.frag.slang` in `Strata/shaders/Debug/` with the shader below. The :term[Slang]{id=slang} language you write here reads like
   :term[HLSL]{id=hlsl}, and the engine's shaders start from `Include/Common.slang`.

   ```diff src="book:tutorials/gpu/first-triangle.patch#hunk-1"
   +#include "Include/Common.slang"
   +
   +// Diagnostic shader used by GPU tests: a checkerboard of 8 x 8 cells over the whole target. Red marks the cells whose
   +// column and row add up to an even number; green marks the upper half of the target, which shows the direction of V.
   +
   +static float2 v_UV;
   +static float4 o_Color;
   +
   +void st_Main()
   +{
   +	uint2 cell = uint2(v_UV * 8.0);
   +	float red = ((cell.x + cell.y) & 1u) == 0u ? 1.0 : 0.0;
   +	float green = v_UV.y < 0.5 ? 1.0 : 0.0;
   +	o_Color = float4(red, green, 0.0, 1.0);
   +}
   +
   +// --- Entry point ---
   +struct ST_Input
   +{
   +	[[vk::location(0)]] float2 v_UV : TEXCOORD0;
   +};
   +struct ST_Output
   +{
   +	[[vk::location(0)]] float4 o_Color : SV_Target0;
   +};
   +ST_Output main(ST_Input input, float4 fragCoord : SV_Position, bool frontFacing : SV_IsFrontFace)
   +{
   +	st_FragCoord = fragCoord;
   +	st_FrontFacing = frontFacing;
   +	v_UV = input.v_UV;
   +	st_Main();
   +	ST_Output output;
   +	output.o_Color = o_Color;
   +	return output;
   +}
   ```

   1. **Line 11:** `uv * 8.0` scales the coordinates to 0 up to 8, and the conversion to `uint2` drops the fraction, so
      `cell` holds the column and the row of the cell.
   2. **Line 12:** the cell is red when its column and row add up to an even number: the last bit of the sum is 0.
   3. **Line 13:** green is 1 in the upper half, where $v$ is below 0.5.
   4. **Line 14:** the color of the pixel; blue is 0 and alpha is 1.
   5. **Line 30:** the entry takes the `v_UV` that the pixel gets from the vertex shader, as `ColorTriangle.frag` takes its color.

   **You should see:** a new file with the same entry as `ColorTriangle.frag.slang`, and a body of four lines.

   **If you do not see it:** a shader that fails to compile stops the build with the message of the Slang compiler. Read
   the line it names, in the next build.

2. Register the shader. The build compiles only the shaders named in `strata_add_shaders`, in `Strata/CMakeLists.txt`.
   Add one line after `Debug/ColorTriangle.frag`.

   ```diff src="book:tutorials/gpu/first-triangle.patch#hunk-2"
    		ImGui.frag
    		Debug/ColorTriangle.vert
    		Debug/ColorTriangle.frag
   +		Debug/Checker.frag
    		Scene/Mesh.vert
    		Scene/DepthPrepass.frag
    		Scene/Forward.frag
   ```

   The name is the path under `Strata/shaders` without `.slang`, and its ending, `.frag`, tells the library the stage.

   **You should see:** the new line has two tabs, like its neighbours.

   **If you do not see it:** a name with a different spelling is compiled by nothing: the test of the next section then
   fails, and the log names the shader.

3. Run the configure step again, then build. The list of shaders is written into `CMakeLists.txt`, and :term[CMake]{id=cmake} reads that
   file at the configure step only, so a new entry needs it. Editing a shader that is already listed, as in the last
   section, does not.

   ::::tabs{sync=os}
   :::tab[Windows]

   ```powershell
   cmake --preset windows
   cmake --build build/windows --config Debug --target StrataTests --parallel
   ```

   The configure step reads `CMakeLists.txt` again, and with it the list of shaders.

   :::
   :::tab[Linux]

   ```sh
   cmake --preset linux
   cmake --build build/linux --config Debug --target StrataTests --parallel
   ```

   The preset `linux` builds with Ninja, as in the first tutorial.

   :::
   :::tab[macOS]

   ```sh
   cmake --preset macos
   cmake --build build/macos --config Debug --target StrataTests --parallel
   ```

   :::
   ::::

   **You should see:** the build compiles `Checker.frag` with the Slang compiler and links the test program again.

   **If you do not see it:** when the build reports an error in the shader, the message names the file and the line. A
   typing mistake in a type name, such as `uint2`, is the usual cause.

:::::

The engine finds the shader by name at run time: `Renderer::GetShaderLibrary().Get("Debug/Checker.frag")` returns the
compiled shader of the embedded registry, and it logs an error and returns null when the name is not registered. The next
section calls it from a test.

## Draw it and test it

The shader exists, but nothing proves that it does what you meant. You write the test. It draws the checker into a
64 by 64 target with the fullscreen vertex shader, reads the image back and checks five pixels.

The pixel values follow from the shader, and you work them out before the test runs. Cells are 8 pixels wide. The pixel
$(4, 4)$ lies in the cell $(0, 0)$: even, so red is 1, and it is in the upper half, so green is 1. The color is yellow,
$(255, 255, 0, 255)$. The pixel $(12, 4)$ lies in the cell $(1, 0)$: odd, so red is 0, with green 1.

The lower half has no green. The pixel $(4, 52)$ is in the cell $(0, 6)$: even, so it is red. The pixel $(12, 52)$ is in
the cell $(1, 6)$: odd, so it is black. The pixel $(60, 60)$ lies in the cell $(7, 7)$: even, so red again.

::figure{id=checker}

:::::steps

1. Add the test case at the end of the suite `GPU.Renderer`, after the triangle test, in `GPURendererTests.cpp`.
   Copy the lines that start with `+`.

   ```diff src="book:tutorials/gpu/first-triangle.patch#hunk-3"
    		CHECK(gpu.GetNewErrorCount() == 0);
    	}
    
   +	TEST_CASE("Checker shader draws its cells over the whole target, with V running down")
   +	{
   +		Tests::GPUContext gpu;
   +		REQUIRE(gpu.IsValid());
   +		nvrhi::IDevice* device = gpu.GetNvrhiDevice();
   +
   +		constexpr uint32_t size = 64;
   +		nvrhi::TextureHandle target = CreateRenderTarget(device, size, size, nvrhi::Format::RGBA8_UNORM);
   +		nvrhi::FramebufferHandle framebuffer = device->createFramebuffer(nvrhi::FramebufferDesc().addColorAttachment(target));
   +
   +		nvrhi::GraphicsPipelineDesc pipelineDesc;
   +		pipelineDesc.VS = Renderer::GetShaderLibrary().Get("PostProcess/Fullscreen.vert");
   +		pipelineDesc.PS = Renderer::GetShaderLibrary().Get("Debug/Checker.frag");
   +		REQUIRE(pipelineDesc.VS != nullptr);
   +		REQUIRE(pipelineDesc.PS != nullptr);
   +		pipelineDesc.primType = nvrhi::PrimitiveType::TriangleList;
   +		pipelineDesc.renderState.rasterState.setCullNone();
   +		pipelineDesc.renderState.depthStencilState.setDepthTestEnable(false).setDepthWriteEnable(false);
   +		nvrhi::GraphicsPipelineHandle pipeline = device->createGraphicsPipeline(pipelineDesc, framebuffer->getFramebufferInfo());
   +		REQUIRE(pipeline);
   +
   +		// The clear is blue, a color the shader never writes: a pixel the fullscreen triangle misses stays blue.
   +		nvrhi::CommandListHandle commandList = device->createCommandList();
   +		commandList->open();
   +		commandList->clearTextureFloat(target, nvrhi::AllSubresources, nvrhi::Color(0.0f, 0.0f, 1.0f, 1.0f));
   +		nvrhi::GraphicsState state;
   +		state.pipeline = pipeline;
   +		state.framebuffer = framebuffer;
   +		state.viewport.addViewportAndScissorRect(nvrhi::Viewport(static_cast<float>(size), static_cast<float>(size)));
   +		commandList->setGraphicsState(state);
   +		commandList->draw(nvrhi::DrawArguments().setVertexCount(3));
   +		commandList->close();
   +		device->executeCommandList(commandList);
   +
   +		ReadbackImage image;
   +		REQUIRE(Renderer::ReadTexture(target, image));
   +		REQUIRE(image.Width == size);
   +
   +		// 8 x 8 cells of 8 pixels. Row 0 is the top of the image, so V grows downwards and green marks rows 0 to 3.
   +		CHECK(Tests::GetPixelRGBA8(image, 4, 4) == glm::u8vec4(255, 255, 0, 255));
   +		CHECK(Tests::GetPixelRGBA8(image, 12, 4) == glm::u8vec4(0, 255, 0, 255));
   +		CHECK(Tests::GetPixelRGBA8(image, 4, 52) == glm::u8vec4(255, 0, 0, 255));
   +		CHECK(Tests::GetPixelRGBA8(image, 12, 52) == glm::u8vec4(0, 0, 0, 255));
   +		CHECK(Tests::GetPixelRGBA8(image, 60, 60) == glm::u8vec4(255, 0, 0, 255));
   +		CHECK(gpu.GetNewErrorCount() == 0);
   +	}
   +
    	TEST_CASE("ImGui renders into an offscreen target")
    	{
    		Tests::GPUContext gpu;
   ```

   1. **Lines 15–16:** the vertex shader is the engine's fullscreen one and the pixel shader is yours.
   2. **Lines 17–18:** a name that is not registered would give a null shader. These `REQUIRE` lines stop the test with a
      clear reason before the pipeline sees it.
   3. **Line 28:** the clear color, blue, is one your shader never writes. A pixel that the triangle missed stays blue.
   4. **Lines 43–47:** five pixels, each worked out above. Row 0 is the top, so the green of the upper half is proof
      that $v$ grows downwards.
   5. **Line 48:** the error count, last, as in the triangle test.

   **You should see:** two test cases of the suite that draw a triangle, yours and the engine's; they differ in two
   lines and in the checks.

   **If you do not see it:** a test outside `TEST_SUITE("GPU.Renderer")` belongs to no `GPU` suite, so the CTest run of
   the GPU suites skips it. The new case stands inside the suite's braces, before the test of ImGui.

2. Build and run the new test case with its own filter.

   ::::tabs{sync=os}
   :::tab[Windows]

   ```powershell
   cmake --build build/windows --config Debug --target StrataTests --parallel
   build\windows\bin\Debug\StrataTests.exe --test-case="Checker shader*"
   ```

   The quotes keep the space of the name together.

   :::
   :::tab[Linux]

   ```sh
   cmake --build build/linux --config Debug --target StrataTests --parallel
   ./build/linux/bin/Debug/StrataTests --test-case="Checker shader*"
   ```

   The `*` at the end of the filter matches the rest of the name.

   :::
   :::tab[macOS]

   ```sh
   cmake --build build/macos --config Debug --target StrataTests --parallel
   ./build/macos/bin/Debug/StrataTests --test-case="Checker shader*"
   ```

   :::
   ::::

   **You should see:** one test case passed and `Status: SUCCESS!`. The run counts 12 checks: 6 `REQUIRE` lines, 5
   pixels and the error count.

   **If you do not see it:** when the log says that `Debug/Checker.frag` is not part of the embedded shaders,
   the entry is missing in `Strata/CMakeLists.txt` or the configure step did not run. Fix the list, configure
   and build again.

3. Show that the test can fail. In `Checker.frag.slang`, change `v_UV.y < 0.5` to `v_UV.y > 0.5`, build and run the
   same filter.

   **You should see:** predict first. The green moves to the lower half. The pixels $(4, 4)$ and $(12, 4)$ lose their
   green, and the pixels $(4, 52)$ and $(12, 52)$ gain it. All five pixel checks fail, because even the pixel $(60, 60)$ now lies in the green half, and the error count
   passes. Restore the line and run the test again to see it pass.

   **If you do not see it:** when all checks still pass, you edited the wrong copy of the shader. The build compiles the
   one in `Strata/shaders/Debug`.

4. Run all the GPU tests with the CTest preset of your system. The label `gpu` selects them.

   ::::tabs{sync=os}
   :::tab[Windows]

   ```powershell
   ctest --preset windows-debug -L gpu
   ```

   The preset `windows-debug` names the Debug configuration, so no `--config` is needed.

   :::
   :::tab[Linux]

   ```sh
   ctest --preset linux-debug -L gpu
   ```

   The preset `linux-debug` does the same on Linux.

   :::
   :::tab[macOS]

   ```sh
   ctest --preset macos-debug -L gpu
   ```

   :::
   ::::

   **You should see:** the tests with the label `gpu` pass, among them `StrataTests.GPU`, the run of every suite whose
   name starts with `GPU`. Your test case runs there, with the others, on one shared device.

   **If you do not see it:** a failure in a suite you did not touch is a finding for that suite. Run it alone with
   `--test-suite=` and the name from the CTest output.

:::::

Your change is complete: a shader, one line of the shader list and a test. The tests of the next pages build on the
same pieces. When a pass has a more complex setup, read [reading validation messages and capturing a frame](debugging.md); when pixels have to come back during a
frame without a stall, read [readback timing](readback-timing.md).

## Summary

- You ran one GPU test case with a doctest filter and read the three lines of its summary: test cases, checks and the
  status.
- You traced the test from a shader with three constant corners, through a pipeline, a recorded draw and a blocking
  readback, to two pixels and the error count.
- You predicted the pixels of a triangle from the clip-space convention: +Y is up, row 0 is the top, so the upper half
  holds the triangle's tip.
- You added a shader: the file under `Strata/shaders`, a line in `strata_add_shaders`, a new configure step because the
  list changed, and a build. An edit inside a listed shader needs only the build.
- You wrote a GPU test with `GPUContext`, five pixel checks and the error count, and you made it fail on purpose.

## Check yourself

1. A triangle has the clip-space corners $(-1, -1)$, $(1, -1)$ and $(0, 0)$. In the 64 by 64 target of the test, is the
   pixel $(32, 48)$ red or blue?

   :::answer{tests="predict-pixels"}
   Red. The corners become the pixels $(0, 64)$, $(64, 64)$ and $(32, 32)$: the base lies on the bottom edge and the
   tip is at the middle of the image. The pixel $(32, 48)$ has its center at $(32.5, 48.5)$. At the row 48.5 the triangle
   reaches 16.5 pixels to each side of the column 32, so the center is inside.
   :::

2. You run `StrataTests --test-case="Checker*"` and doctest reports 0 test cases. Name two causes.

   :::answer{tests="run-test"}
   The filter matches the start of a name, with `*` for any characters, and no test case begins with that text: the
   name is spelled wrongly. Another cause is the program: an old build of `StrataTests` does not hold the test, because
   the build step was skipped.
   :::

3. In the triangle test, which call makes the CPU wait for the GPU, and why may a game not use it in a frame?

   :::answer{tests="trace-draw"}
   `Renderer::ReadTexture` creates a readback and waits for it. In a frame, that wait would stall the :term[frame loop]{id=game-loop} for as
   long as the GPU needs to finish its work. So the engine reads data back without waiting and polls each frame.
   Tests and tools may block, because nothing else runs in them.
   :::

4. You add `Edge.frag.slang` to `Strata/shaders/Debug/` and build, but the test logs that the shader is not part of the
   engine's embedded shaders. What is missing, and what do you run?

   :::answer{tests="add-shader"}
   The line `Debug/Edge.frag` is missing in `strata_add_shaders`, in `Strata/CMakeLists.txt`. Add it, run the configure
   step again with `cmake --preset <preset>`, and build. A file that no entry names is not compiled and not embedded.
   :::

5. A colleague writes a GPU test that creates its own Vulkan device, checks a pixel and never reads the error count.
   Name two things wrong with it.

   :::answer{tests="write-test"}
   The test must use `GPUContext`, the one device of the run: a device for each test costs time, and drivers handle that
   pattern poorly. It must also end with `CHECK(gpu.GetNewErrorCount() == 0)`. Validation errors do not fail a test by
   themselves, and a right pixel can hide misuse that another driver rejects.
   :::

## Exercises

1. **Basic.** Change the checker to 4 by 4 cells: use `v_UV * 4.0` in the shader. Predict the colors of the pixels
   $(12, 4)$, $(20, 4)$, $(12, 52)$ and $(20, 52)$, then change the checks of the test and run it.

   Hint: a cell is now 16 pixels wide, and the rows 0 and 1 are the upper half.

   :::answer{tests="predict-pixels write-test"}
   The pixel $(12, 4)$ is in the cell $(0, 0)$, even and upper: yellow, $(255, 255, 0, 255)$. The pixel $(20, 4)$ is in
   the cell $(1, 0)$: odd and upper, so green, $(0, 255, 0, 255)$. The pixel $(12, 52)$ is in the cell $(0, 3)$: odd and
   lower, so black, $(0, 0, 0, 255)$. The pixel $(20, 52)$ is in the cell $(1, 3)$: even and lower, so red,
   $(255, 0, 0, 255)$. Of the old checks, those of $(12, 4)$ and $(4, 52)$ then fail, as they should, because those pixels changed
   color.
   :::

2. **Hard.** The engine's rule for Slang says that `mul` takes a matrix and that a matrix constructor takes rows. Test
   the rule. Write a shader `Debug/ChannelRotate.frag` that sends pure red through the matrix with the rows $(0, 1, 0)$,
   $(0, 0, 1)$ and $(1, 0, 0)$, as `mul(rotation, color)`. Swap the two arguments, build and see that it compiles.

   Then write the pixel test that catches the swap. Show that it fails for the swapped shader and passes for the right one.

   Hint: compute both products by hand.

   The engine has a second way to test a shader function: a small diagnostic
   compute shader runs the function of an include for many inputs and writes the results to a buffer. The test reads the
   buffer back and compares it with the C++ twin of the function. `Debug/BlueNoise.comp` does this for the blue-noise
   tile, and `Debug/LODSelection.comp` and `Debug/ShadowViewStats.comp` for the choice of a level of detail (see
   [levels of detail](../draw/lod.md)) and the statistics of a shadow view. The technique fits a function that other
   shaders call. A pixel test fits a whole shader.

   :::answer{tests="trace-draw write-test add-shader" solution="tutorials/gpu/first-triangle/exercise-2.patch"}
   With `mul(rotation, color)` the vector is a column: each output is a row dotted with the color, so red $(1, 0, 0)$
   becomes $(0, 0, 1)$, blue. With the arguments swapped, `mul(color, rotation)` reads the vector as a row and uses the
   columns of the matrix: red becomes $(0, 1, 0)$, green. Both forms compile, because both multiply a vector and a
   matrix, so only a pixel shows the difference.

   The worked solution is the patch of this exercise. It applies on top of the page's change, the checker, and adds
   `ChannelRotate.frag`, its line in the shader list, and a test case that draws it with the fullscreen vertex shader. The test expects the pixel
   $(32, 32)$ to be $(0, 0, 255, 255)$ and the error count to be 0. With the arguments swapped, the same test reports a
   green pixel instead of the blue one.
   :::

## Where it lives in Strata

- `Strata/shaders/Debug/ColorTriangle.vert.slang` and `ColorTriangle.frag.slang`: the triangle of the first test.
- `Strata/shaders/PostProcess/Fullscreen.vert.slang`: the fullscreen triangle, drawn with a vertex count of 3.
- `Strata/shaders/Include/Common.slang`: `NDCToUV` and the globals of the :term[entry points]{id=entry-point-gpu}.
- `Strata/CMakeLists.txt`: `strata_add_shaders`, the list of registered shaders.
- `Strata/src/Strata/Renderer/ShaderLibrary.cpp`: `ShaderLibrary::Get`, the lookup by name.
- `Strata/src/Strata/Renderer/Renderer.cpp`: `Renderer::ReadTexture`, the blocking readback.
- `StrataTests/src/Renderer/GPUTestUtils.h` and `GPUTestUtils.cpp`: `GPUContext`.
- `StrataTests/src/Renderer/GPURendererTests.cpp`: the suite `GPU.Renderer` and the triangle test.

## Further reading

- [NVRHI on GitHub](https://github.com/NVIDIA-RTX/NVRHI): the library behind `nvrhi::IDevice`, with the command list and
  the pipeline description. Intermediate.
- [doctest, "Command line"](https://github.com/doctest/doctest/blob/master/doc/markdown/commandline.md): the filters
  `--test-case` and `--test-suite`. Beginner.
- [The Vulkan specification, on registry.khronos.org](https://registry.khronos.org/vulkan/specs/1.3/html/vkspec.html): the
  chapter on the viewport transform and the fragment operations. Advanced.
- [Microsoft's page of the HLSL function `mul`](https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-mul): how
  the order of the arguments decides what a vector is. Intermediate.
