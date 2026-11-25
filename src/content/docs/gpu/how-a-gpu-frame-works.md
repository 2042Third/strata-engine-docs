---
id: gpu/how-a-gpu-frame-works
title: "How a GPU works and draws a frame"
description: "What a graphics card is, why a program gives it commands that run later, how a triangle becomes pixels, and how frames reach the screen."
kind: concept
size: L
tracks: [E]
needs: [basics/threads, basics/math-projection, basics/color, basics/signals, core/frame-loop]
time: 60
learn:
  - id: deferred-commands
    text: explain why a draw call does not draw at once and who keeps track of the work
  - id: pipeline-stages
    text: name the stages of the graphics pipeline in order and say what each reads and writes
  - id: wave-cost
    text: compute what a branch that splits a wave costs and what limits the speed of a shader
  - id: frame-timeline
    text: predict when each frame is recorded and drawn with two frames in flight
  - id: vsync-choice
    text: choose a present mode and say what vsync costs and what it buys
since: 0.3.0
status: final
---

::figure{id=showcase-viewport}

Open the editor with the Showcase sample, hold the right mouse button over the Scene view and drag to turn its
camera from the distant horizon it starts on. Press **W** to fly forward until you see terrain, props, shadows and a
sky. That
image is one **frame**, and the editor makes a new one about every 16 ms. Between two of them, your program has done
something to roughly two million pixels, many times over. The question of this page is what the :term[graphics card]{id=gpu} did in
those 16 ms, and why your program never sees it happen.

You will meet the answer in four steps. First you learn what a graphics card is built for. Then you learn why a
program talks to it through recorded commands. Then you follow a triangle through the pipeline that turns it into
colored pixels. At the end you learn how finished images reach the screen, and why Strata keeps two frames in
flight.

## A graphics card runs one small program over millions of pieces of data

Consider the naive way to draw the image: a loop visits each of the 2,073,600 pixels of a 1920 by 1080 window, works out its color and stores it. At 60 :term[frames per second]{id=frame-rate} the loop must finish 124,416,000 pixels every second,
and each pixel needs many steps: find what is there, light it, mix colors. A fast core of a :term[central processing unit]{id=processor} (CPU) does a few billion simple
steps each second, so it has about 30 steps per pixel. Real scenes need hundreds.

The :term[CPU]{id=processor} is built to run one thing fast. It has a few large cores that guess ahead, run steps in a new order and keep a big cache. A cache is the fast memory close to a core, which you met in [How a computer runs a program](../basics/computer.md). That design
suits a game's logic, which branches a lot and touches memory in unpredictable ways. Drawing pixels is different:
the same steps run for millions of pixels, and no pixel needs the result of another.

A **graphics processing unit** (GPU) is a processor built for that second kind of work. It has thousands of simple lanes that run the same small program over many pieces of data at once, with memory of its own.

A lane is far slower than
a :term[CPU core]{id=processor-core} and cannot guess ahead. Yet 5,000 lanes that each do a small share beat a few fast cores when the work
divides evenly. The small program has a name: a **shader** is a program that runs on the GPU, once for each piece of data
it is given. Its name stays from the first programs, which only shaded surfaces.

Two facts about the card shape everything that follows. The card has its own memory, so the data a shader reads
must first be copied there, and that copy takes time. The card also runs on its own clock, apart from the CPU: both
chips work at the same time, much as two threads do, except that they do not share a program or a stack.

## A draw call records a request; it does not draw

Imagine the program asks the card to draw a mesh and then waits until the card answers. The CPU would idle while
the card works, and the card would idle while the CPU prepares the next request. Each chip would spend half of its
time doing nothing. A better design lets the CPU write down many requests in a list and hand the list over, so that
the card works through them while the CPU writes the next list.

Every modern program works that way. An application programming interface (API) is a set of calls a program makes to use a service. A **graphics API** is the one that gives the GPU its orders. Vulkan, Direct3D 12 and Metal are graphics APIs; so are the older OpenGL and Direct3D 11.

A call such as "draw this
mesh" is a **draw call**. It does not draw. It appends one entry to a **command list**, a recorded sequence of GPU
commands that runs later. Vulkan calls it a command buffer. When the list is complete, the program submits it
to a queue, and the driver and the card run it whenever they have time.

A queue takes submitted lists and starts them in order. A card has several kinds of queue for different work: a
**queue family** is a group of queues that can do the same kinds of command, such as drawing, general computing or
copying. The graphics queue is the one the frame uses, and it does the drawing in this page.

Someone must keep track of what the GPU has not finished. A list that has been submitted may still read a buffer
or a texture; if the CPU rewrites or frees it, the card reads garbage or crashes. APIs differ in who watches.

An **immediate API**, such as OpenGL or Direct3D 11, hides the problem. The driver tracks what each command uses,
copies data when the program rewrites something in use, and inserts the waits that keep the order correct. The
program is simpler, but the driver does work the program cannot see or plan, and its costs appear as uneven :term[frame times]{id=frame-time}.

An **explicit API**, such as Vulkan, Direct3D 12 or Metal, hands the work to the program. The program records lists
itself, tells the card where one pass must finish before the next starts, and decides when memory may be used again.
That is more code and more ways to make mistakes. It allows the engine to plan the work, record lists on several
threads and know exactly what is in use.

Strata uses Vulkan through NVRHI, a library that wraps the explicit API in friendlier objects while still leaving the
duties of ordering and lifetime to Strata. [The Vulkan and NVRHI page](vulkan-nvrhi.md) shows how Strata opens the
device. The rest of this page treats the card as an explicit-API program sees it.

## The idea: a frame is a pipeline of stages fed by lists

The mental model has three parts. The CPU records command lists. The card runs them through a fixed order of stages, called
the **graphics pipeline**, that turns the scene's triangles into pixels. And a small set of images, the swap chain,
carries the results to the display. The next sections take the parts in that order.

```mermaid caption="The graphics pipeline from the mesh to the target. Round boxes are programs you write; square boxes are fixed hardware stages; each arrow names what travels between them." alt="A diagram of the graphics pipeline from left to right. A vertex buffer feeds the vertex shader, a program run once per vertex. Its output goes to the rasterization stage, which finds the pixels a triangle covers. The rasterization stage passes blended values to the fragment shader, a program run once per covered pixel. The fragment shader output goes to the depth test and then to blending, which write into the render target."
flowchart LR
	vb["Vertex buffer: positions, normals, texture coordinates"] --> vs(["Vertex shader: once per vertex"])
	vs -->|"clip position, interpolants"| rast["Rasterization: which pixels does the triangle cover"]
	rast -->|"blended values per pixel"| fs(["Fragment shader: once per covered pixel"])
	tex["Textures and buffers"] -.->|"read"| fs
	fs -->|"color, depth"| dt["Depth test"]
	dt --> bl["Blending"]
	bl --> rt["Render target"]
	rt -.->|"read the old depth and color"| dt
```

Read the diagram from left to right. Data flows through the stages and each stage reads only what the one before it
wrote, plus the textures and buffers the program binds. The dotted arrow shows the one loop: the depth test and
blending read what the target already holds before they write.

## A triangle becomes pixels in six steps

The sections here follow one triangle. Each corner is a **vertex**, and it carries data: a position, a
direction the surface faces and a pair of texture coordinates. A mesh is a long list of triangles that share corners. The
vertex data sits in a buffer, which is a block of GPU memory the program fills before drawing.

### Vertex shading moves corners into view

The **vertex shader** runs once for each vertex. Its job is to place the corner on the screen: it multiplies the
position by the model, view and projection matrices of [Projection](../basics/math-projection.md) and writes a
clip-space position. It also passes along any other values the later stages need. Because each vertex is
independent, the card can run thousands of them at the same time.

### Rasterization turns a triangle into pixel samples

After the vertex stage, the hardware knows where each corner lands on the screen. **Rasterization** is the stage that
finds which pixels a triangle covers. For each pixel it asks one question: is the center of this pixel inside the
triangle? The answer is yes or no, and nothing in between.

Rasterization is the sampling of [Signals](../basics/signals.md): a pixel takes one sample of the triangle at one point. A triangle edge that cuts a pixel in half gives it the whole pixel or none of it. Edges then show stairs, the :term[aliasing]{id=aliasing} you studied there. Strata hides most of them in later stages, as the
[frame tour](frame-tour.md) shows.

### Interpolants carry values across the triangle

A vertex output that varies across the triangle is an **interpolant**: a value written at each vertex and blended
by the rasterization stage into a value for each covered pixel. The blend uses the pixel's weights toward the three corners,
which add up to 1.

Here is a worked example. A pixel center lies at weights 0.5, 0.25 and 0.25 toward corners A, B and C. The vertex
shader wrote a brightness of 1.0 at A, 0.0 at B and 0.4 at C. The pixel receives 0.5 × 1.0 + 0.25 × 0.0 +
0.25 × 0.4, which is 0.6. A pixel exactly at corner A receives weights 1, 0 and 0, so it gets 1.0, and a pixel on the edge
between B and C gets a mix of 0.0 and 0.4 only.

### Fragment shading colors each pixel, in groups of four

The **fragment shader** runs once for each covered pixel and returns its color. It also reads textures, which the next section
covers. The hardware does not run pixels alone: it runs them in **quads**, blocks of 2 by 2 neighbors, even at the
edge of a triangle where some of the four are outside it. Those outside pixels run too and their results are
thrown away.

The waste has a purpose. In a quad each pixel can compare its interpolant with its three neighbors, which gives the rate at which a
value changes from one pixel to the next: a derivative. Suppose a texture coordinate reads 0.500 at one pixel and
0.502 at its right neighbor. The change is 0.002 per pixel.

On a texture 1024 texels wide, a texel is one cell of the
image; one pixel step then moves across 0.002 × 1024 = 2.05 texels. The card keeps smaller copies of the texture, each half as wide as the one before.
It reads the copy where one pixel step moves about one texel: here the copy half as wide, because log₂ of 2.05 is about 1. That copy is a **mip level**, taught in
[Textures](../assets/textures.md).

### The depth test keeps the nearest surface

Two triangles can cover the same pixel, and the program does not draw them in distance order. A **depth buffer**
holds, for each pixel, the depth of the nearest surface drawn so far. When a new fragment arrives, the **depth test**
compares its depth with the stored one and keeps the new fragment only if it is nearer. Depth ranges and their
direction in Strata are the subject of [Coordinates](coordinates.md); here you need only that the test discards what
is hidden.

### Blending mixes the fragment into the target

The surviving fragment is written to a **render target**, an image the card draws into. For an opaque surface, the
new color replaces the old. For glass, **blending** mixes them: the result is new × alpha + old × (1 − alpha).

With an alpha of 0.25, a red fragment (1, 0, 0) over a blue target (0, 0, 1) gives (0.25, 0, 0.75). Blending must read
the old value, so it costs memory traffic as well as arithmetic. It also depends on order, and that is why
transparent surfaces are sorted.

The table lists, for each stage of the figure, what it reads and what it writes.

```text
Pipeline stage        Reads                          Writes
Vertex shader         one vertex of the buffer       clip position, interpolants
Rasterization stage   three clip positions           covered pixels, weights
Fragment shader       interpolants, textures         color, depth
Depth test            new depth, stored depth        pass or discard, new depth
Blending              new color, stored color        the mixed color
```

The table shows one row for each stage of the figure. If you can say the row from memory, you can name the stages
in order and tell what each reads and writes.

:::note[The colors in the pipeline]
The mixing above is correct only on linear values. Colors stored as sRGB must be converted first, a rule from
[Color](../basics/color.md) that the card's texture units and render targets can apply for you.
:::

## Textures and sampling feed the fragment shader

A **texture** is an image stored in GPU memory, in a layout the card reads fast. A buffer is the plain counterpart:
:term[bytes]{id=byte} the shader reads in any order, such as the corners of a mesh or a list of lights. Textures are for data that has
neighbors, such as images, because the hardware knows how to read them as images.

Reading a texture is **sampling**. The shader gives a coordinate from 0 to 1 and the hardware answers with a color. A
**sampler** is the setting that says how: how to turn a coordinate between texels into a color, and what to do beyond the edge. The
choices form a ladder from cheap to costly, and each step cures a flaw of the one below.

**Point** filtering reads the nearest texel. It is fast, but a texture magnified past its size shows square cells. **Bilinear** filtering reads the four nearest texels and blends them by distance.

Take four texels with values
10 and 30 on the top row and 50 and 90 on the bottom row. A sample 0.75 of the way across and halfway down gets a top blend of 10 × 0.25 + 30 × 0.75 = 25. Its bottom blend is 50 × 0.25 + 90 × 0.75 = 80. The final value is 25 × 0.5 + 80 × 0.5 = 52.5.

Bilinear filtering still fails on a texture seen from far away, where one pixel covers many texels and the four it reads
are an arbitrary few. That is the aliasing of [Signals](../basics/signals.md) again. **Trilinear** filtering reads
two neighboring mip levels, chosen by the derivative above, and blends them. **Anisotropic** filtering also handles
a floor seen at a glancing angle, where a pixel covers a long thin strip of texels, by taking several samples
along the strip. Each step reads more memory.

## The hardware sets the cost of every stage

The pipeline says what happens; the hardware says what it costs. Four ideas explain most of a GPU's behavior.

### Waves run their lanes together

The card groups lanes into **waves**: a wave is a group of lanes, often 32 or 64, that execute the same instruction at
the same moment on different data. A quad of four pixels lives inside a wave. The hardware names vary (vendors also say warp), and the size depends on the card.

### Branches that split a wave run both sides

Suppose the shader has an :term[if statement]{id=if-statement}. When all 32 lanes of a wave take the same side, the branch costs only that side:
a **uniform branch**, one that every lane takes the same way. When 16 lanes take one side and 16 the other, the
wave runs the first side with half the lanes switched off, then the second side with the other half off. If each
side costs 10 instructions, a uniform branch costs 10 and a branch that splits costs 20. Neighboring pixels usually
agree, so most branches are cheap; a branch that depends on noise is not.

### Occupancy hides waiting

Reading memory takes hundreds of cycles. The card does not wait: when a wave asks for memory, the core switches to
another wave that is ready. **Occupancy** is how many waves a core holds at once.

Each wave needs its own registers,
the small fast storage of a lane. If a core has 65,536 registers and a shader needs 128 per lane, a wave of 32 lanes uses 4,096, so
16 waves fit. A shader that needs 64 per lane allows 32 waves, which hides more waiting. These numbers are
typical, not the same on every card.

### Bandwidth limits what moves

**Bandwidth** is how many bytes per second the memory can move. A 1920 by 1080 target that stores 8 bytes per pixel
holds 2,073,600 × 8 = 16.6 MB. Blending reads and writes it, so each layer costs 33.2 MB. Ten layers at 60 frames per
second move about 332 MB × 60 = 19.9 GB per second.

Suppose the card offers 400 GB per second: that is 5 % of it, from
one effect. A frame has hundreds of such passes, and that is why engines fight for every byte.

## Frames in flight keep both processors busy

Now put the hardware and the lists together over time. The CPU records frame 1 while the GPU draws frame 0. A
**frame in flight** is a frame the CPU has begun that the GPU has not finished, so **frames in flight** is the number
of such frames at one moment. Strata allows two.

Why a limit? Suppose the CPU were free to run ahead. It would record frame 5 while the card still draws frame 2,
the frames would pile up, and the image on screen would show input from a long time ago. Also, each frame in flight
owns buffers the card still reads, and every extra frame needs another set. A small limit bounds both the delay and the memory.

The CPU needs a way to learn that the card is done. A **fence** is a signal from the GPU to the CPU that all the
work up to a point is finished; NVRHI calls it an event query, and Strata waits on it. The program places a fence after the
frame's last list. Before it starts a new frame, it checks the oldest fence.

```mermaid caption="Two frames in flight. The CPU records frames 0 and 1 at once, then frame 2 waits until the GPU has finished frame 0; the acquire and present points mark where a frame meets the display." alt="A schedule with two rows, CPU and GPU. The CPU records frame 0, then frame 1, then waits for the fence of frame 0, then records frame 2. The GPU draws frame 0 after it is recorded, then frame 1, then frame 2. Each frame ends with a present, and each frame begins with an acquire of an image."
flowchart LR
	subgraph CPU
		direction LR
		r0["Record frame 0"] --> r1["Record frame 1"] --> w2["Wait: fence of frame 0"] --> r2["Record frame 2"]
	end
	subgraph GPU
		direction LR
		d0["Draw frame 0, present"] --> d1["Draw frame 1, present"] --> d2["Draw frame 2, present"]
	end
	r0 --> d0
	r1 --> d1
	d0 -.->|"fence signals"| w2
	r2 --> d2
```

:::example[Frames in flight with numbers]
Say the CPU needs 4 ms to record a frame and the GPU needs 10 ms to draw it, with two frames in flight. The CPU
records frame 0 from 0 to 4 ms; the GPU draws it from 4 to 14. The CPU records frame 1 from 4 to 8, and the GPU
draws it from 14 to 24.

Frame 2 cannot start at 8: two frames are outstanding. The CPU waits for the fence of frame 0
at 14 ms, records frame 2 from 14 to 18, and the GPU draws it from 24 to 34. Frame 3 waits for the fence of frame 1 at
24 ms.

From then on a new frame finishes every 10 ms: the GPU sets the pace, and the CPU waits about 6 ms of each. Frame 3
is recorded at 24 ms and drawn by 44 ms, so 20 ms pass between the start of the recording and the finished image.
With one frame in flight, the CPU would wait for each frame: 4 ms of recording and 10 ms of drawing give 14 ms per
frame, and the GPU would idle 4 ms of them.
:::

The rule has a second half that explains the third mistake below: the card reads a frame's buffers until its fence
signals. The CPU may rewrite the data of the frame whose fence has signaled, not the one still in flight.

## The swap chain hands finished images to the display

A display shows an image by reading it from memory, line by line, about 60 times a second. If the card wrote into
that image while the display read it, the top of the screen would show the old frame and the bottom the new one:
a visible seam called tearing. The fix is to draw somewhere else, and show the result only when it is complete.

A **swapchain** is a ring of images that belong to a window; the program draws into one while the display shows another.

The image the frame draws into is the **back buffer**; the others wait or are on show.

When the frame starts, the program asks the swapchain for a free image: **acquire** is that request, and it may wait if every image is busy.

When the frame has finished drawing, the program hands the image back to be shown: to **present** is that hand-over.

## Present modes trade delay against tearing

The display shows a new image only at its refresh, every 16.7 ms on a 60 Hz screen. What happens to an image that
finishes between two refreshes is the choice of the **present mode**, the rule that says when a presented image reaches the screen and what happens to those that wait. Vulkan names three common modes: first in, first out (FIFO), `MAILBOX` and `IMMEDIATE`.

| Mode | What happens | Tearing | Delay | Cost |
| --- | --- | --- | --- | --- |
| `FIFO` | Images wait in a queue; one is shown at each refresh | None | Highest: up to the queue length | The program waits when the queue is full; the card idles |
| `MAILBOX` | One image waits; a newer one replaces it | None | Lowest without tearing | Drawn frames can be thrown away unseen |
| `IMMEDIATE` | The image is shown at once, mid-refresh | Yes | Lowest | Tearing, and the program draws as fast as it can |

**Vsync** is the common name for `FIFO`: the program waits for the display, so frames are shown whole and in step with
the refresh. Vsync buys clean images and a card that does not work harder than the screen needs. It costs delay and rhythm.

Say the card needs 20 ms to draw a frame on a 60 Hz screen. The images finish at 20, 40, 60, 80, 100 and 120 ms
and appear at the next refreshes, 33.3, 50, 66.7, 83.3, 100 and 133.3 ms. The gaps are four of 16.7 ms and one of
33.3 ms, so you see 50 frames per second with an uneven rhythm. `IMMEDIATE` would show every image at once, torn but
with the least delay.

## Strata asks for two frames in flight and `FIFO`

Strata requires Vulkan 1.2. Its graphics device allows two frames in flight by default (the field
`MaxFramesInFlight` of `GraphicsDeviceSpecification`), and a window starts with :term[vsync]{id=vsync} on. With vsync on the device
asks for `FIFO`, which every Vulkan device must support. With vsync off it prefers `MAILBOX`, falls back to `IMMEDIATE` when
the screen lacks `MAILBOX`, and otherwise keeps `FIFO`. The next quote is the whole choice.

```cpp src="Strata/src/Platform/Vulkan/VulkanGraphicsDevice.cpp#L1157-L1168"
VkPresentModeKHR presentMode = VK_PRESENT_MODE_FIFO_KHR; // Always supported
if (!m_VSync)
{
	if (supportsMode(VK_PRESENT_MODE_MAILBOX_KHR))
		presentMode = VK_PRESENT_MODE_MAILBOX_KHR;
	else if (supportsMode(VK_PRESENT_MODE_IMMEDIATE_KHR))
		presentMode = VK_PRESENT_MODE_IMMEDIATE_KHR;
}

uint32_t imageCount = std::max(capabilities.minImageCount + 1, m_Specification.MaxFramesInFlight + 1);
if (capabilities.maxImageCount > 0)
	imageCount = std::min(imageCount, capabilities.maxImageCount);
```

1. **Line 1157:** The device starts from `FIFO`, because every Vulkan device supports it.
2. **Lines 1158–1164:** Only with vsync off does it prefer `MAILBOX`, then `IMMEDIATE`; with neither, it keeps `FIFO`.
3. **Lines 1166–1168:** The image count is the larger of the driver's minimum plus one and the frames in flight plus one, kept below the driver's maximum.

The wait for the oldest frame is the first thing `BeginFrame` does, before the program asks for an image to draw into.

```cpp src="Strata/src/Platform/Vulkan/VulkanGraphicsDevice.cpp#L1444-L1452" from="// Frame pacing" to="m_EventQueryPool.push_back(query);" symbol="VulkanGraphicsDevice::BeginFrame"
// Frame pacing: wait until the GPU has finished the frame that last used this slot.
try
{
	while (m_FramesInFlight.size() >= m_Specification.MaxFramesInFlight)
	{
		nvrhi::EventQueryHandle query = m_FramesInFlight.front();
		m_FramesInFlight.pop();
		m_NvrhiDevice->waitEventQuery(query);
		m_EventQueryPool.push_back(query);
```

The loop runs while the number of outstanding frames has reached the limit. Each pass takes the oldest fence, waits until the GPU has passed it and gives the fence back to a pool. The first two frames find the queue short and never wait.

:::why[Why two frames in flight, and why more images than frames?]
Two is the smallest number that keeps both processors busy: one frame being drawn, one being recorded. A third
would hide an occasional slow frame, but it adds a frame of delay between input and image and another set of buffers,
and a bigger memory bill. For a game that must feel responsive, the delay costs more than the protection against slow frames gains.

The image count of the swap chain is a different number. The display holds one image, and a presented image may wait
in the queue, so the swap chain needs more images than frames in flight. Strata asks for the larger of the driver's
minimum plus one and the frames in flight plus one. A driver may also give more, so the number of images is never the
number of frames in flight; only the fence limits the CPU's lead.
:::

The fence is placed at the end of `EndFrame`, right after the frame is presented. The wait is the first step of the next
`BeginFrame`: the loop frees one entry while two are outstanding. [The Vulkan and NVRHI page](vulkan-nvrhi.md)
describes how the acquire is ordered after that wait. The :term[frame loop]{id=game-loop} paces the CPU's side with a sleep that caps the frame rate; [The frame loop](../core/frame-loop.md) teaches it.

## What Strata's choice cannot do

Vulkan 1.2 as a minimum excludes cards and drivers older than it; Strata rejects them at startup with a message
instead of running badly. The pacing allows a lead of two frames at most, so a long CPU frame cannot be hidden by
a longer queue. With vsync on, the delay of `FIFO` is accepted; a game that needs the lowest delay must disable vsync and accept tearing, or the lost frames of `MAILBOX`. What the engine omits on purpose is listed in
[What Strata does not do](../appendix/not-in-strata.md).

## Common mistakes

- **Believing that a draw call draws now.** Symptom: timing a draw call on the CPU shows microseconds, and the
  conclusion is that drawing is free, yet the frame is slow. Fix: the call recorded one command; the cost lands on the
  GPU later, so measure GPU time with the profiler.
- **Counting the swap chain images as frames in flight.** Symptom: a developer sees three images and expects a lead
  of three frames, or raises one number and expects the other to follow. Fix: the images belong to the display's queue
  and the fence limits the CPU; they are chosen apart.
- **Rewriting what the GPU still reads.** Symptom: flickering or wrong geometry that appears only when the GPU is
  busy and vanishes when you slow it with a debugger. Fix: give each frame in flight its own copy, or wait on its fence.
- **Treating a branch as free.** Symptom: a shader with a noisy if costs about both sides added up, not the one side you
  expected. Fix: make the condition uniform over neighbors, or compute both sides without a branch.
- **Reading vsync as a speed switch.** Symptom: disabling it raises the frame counter but the picture tears. Fix: a
  higher counter is not a faster game; judge the delay and the tearing you accept.

## Summary

- A draw call appends a command to a list that runs later; an explicit API leaves the tracking of what the GPU still
  uses to the program, an immediate API to the driver.
- The pipeline runs vertex shader, rasterization stage, fragment shader, depth test and blending; each reads the one before's
  output, and the fragment shader also reads textures.
- A branch that splits a wave costs both sides; occupancy hides memory waits; bandwidth limits what each pass moves.
- With two frames in flight the CPU records frame N + 1 while the GPU draws frame N, and a fence makes the CPU wait for
  the oldest frame.
- `FIFO` shows whole images at the refresh and delays them; `MAILBOX` and `IMMEDIATE` lower the delay, at the cost of dropped
  frames or tearing.

## Check yourself

1. A program calls a draw function and then measures 8 microseconds on the CPU. Which statement is right?
   (a) The card drew the mesh in 8 microseconds. (b) The call recorded a command; the card runs it later. (c) The
   driver always runs the draw at once in an explicit API.

   :::answer{tests="deferred-commands"}
   Option (b) is right. A draw call appends an entry to a command list and returns. Option (a) mistakes the cost of
   recording for the cost of drawing. Option (c) is wrong for both kinds: even an immediate API queues the work, and an
   explicit API leaves the timing and the tracking to the program.
   :::

2. Put in order: blending, rasterization stage, vertex shader, depth test, fragment shader. Name what the rasterization stage hands to
   the fragment shader.

   :::answer{tests="pipeline-stages"}
   The order is vertex shader, rasterization stage, fragment shader, depth test, blending. The rasterization stage hands over the
   covered pixels with their interpolants: the vertex outputs blended by each pixel's weights.
   :::

3. A wave has 32 lanes. Twelve take the first side of a branch, which costs 8 instructions, and twenty take the second
   side, which costs 14. How many instructions does the wave spend, and how many if all lanes took the second side?

   :::answer{tests="wave-cost"}
   The wave runs both sides because the lanes split: 8 + 14 = 22 instructions. If every lane took the second side, the
   branch would be uniform and cost 14. Occupancy would not change either number; it only hides memory waits.
   :::

4. The CPU needs 3 ms to record a frame, the GPU 8 ms to draw it, and two frames are in flight. When does the CPU
   begin recording frame 2?

   :::answer{tests="frame-timeline"}
   Frame 0 is recorded from 0 to 3 ms and drawn from 3 to 11 ms. Frame 1 is recorded from 3 to 6 ms. Frame 2 waits for the
   fence of frame 0, so it begins at 11 ms. The CPU idles from 6 to 11 ms.
   :::

5. Your game draws in 12 ms and the screen refreshes every 16.7 ms. With vsync on, how many frames per second do you
   see, and what do you gain over `IMMEDIATE`?

   :::answer{tests="vsync-choice"}
   Each frame is ready before the next refresh, so `FIFO` shows one frame per refresh: 60 frames per second. You gain
   whole images without tearing and a card that rests part of each refresh. You pay with a little delay, because images
   wait for the refresh. `IMMEDIATE` would show them sooner, torn.
   :::

## Exercises

1. **Basic.** Predict how many frames the CPU records before it first waits for the GPU, with two frames in flight.
   Then run the sketch to check.

   :::answer[Worked solution]{tests="frame-timeline" solution="sketches/gpu-how-a-gpu-frame-works-pacing.cpp"}
   The wait happens when two frames are outstanding. Frame 0 starts with none, frame 1 with one, so both are recorded
   without a wait; frame 2 starts with two and waits for frame 0. The answer is two. The sketch models the queue of
   fences with a `std::queue` and prints it.

   ```cpp sketch="gpu-how-a-gpu-frame-works-pacing.cpp"
   #include <cstddef>
   #include <cstdio>
   #include <queue>

   int main()
   {
   	const std::size_t maxFramesInFlight = 2;
   	std::queue<int> outstanding;

   	for (int frame = 0; frame < 5; frame++)
   	{
   		// The GPU finishes frames in order, so waiting frees the oldest one.
   		while (outstanding.size() >= maxFramesInFlight)
   		{
   			std::printf("frame %d: waits for frame %d\n", frame, outstanding.front());
   			outstanding.pop();
   		}
   		std::printf("frame %d: the CPU records it\n", frame);
   		outstanding.push(frame);
   	}
   	return 0;
   }
   ```

   ```text output-of="gpu-how-a-gpu-frame-works-pacing.cpp"
   frame 0: the CPU records it
   frame 1: the CPU records it
   frame 2: waits for frame 0
   frame 2: the CPU records it
   frame 3: waits for frame 1
   frame 3: the CPU records it
   frame 4: waits for frame 2
   frame 4: the CPU records it
   ```

   1. **Line 7:** The limit is two, as in Strata's default.
   2. **Lines 13–17:** While two frames are outstanding, the CPU waits for the oldest and removes it from the queue.
   3. **Line 19:** After recording, the frame joins the queue, as its fence joins Strata's.

   On a source build, add a log line at the wait in `VulkanGraphicsDevice::BeginFrame` to see the same order. The
   Strata queue holds fences, and the sketch holds numbers.
   :::

2. **Medium.** Using the schedule example (CPU 4 ms, GPU 10 ms), change the limit to three frames in flight. When does
   the CPU first wait, and does the frame rate change?

   :::answer[Worked solution]{tests="frame-timeline"}
   The CPU records frames 0, 1 and 2 at 0 to 4, 4 to 8 and 8 to 12 ms. The GPU draws them from 4 to 14, 14 to 24 and 24
   to 34. Frame 3 waits for the fence of frame 0 at 14 ms. The GPU still finishes a frame every 10 ms, so the frame
   rate stays the same, while frame 3 now finishes later after its recording began: it starts at 14 ms and ends at 44.
   That is 30 ms against 20 ms: the extra frame bought delay, not speed.
   :::

3. **Hard.** A designer asks for 2 frames in flight and 2 swap chain images, under `FIFO`. Explain what can go wrong,
   and why Strata takes more images.

   :::answer[Worked solution]{tests="vsync-choice"}
   The display holds one image, so one image remains for drawing. A frame that finished must wait for the next refresh
   before its image is free, so the CPU's acquire waits for the display even though the GPU has space for work. The
   pipeline stalls in step with the refresh and the card idles. With a third image the card can draw the next frame while one
   image is shown and one waits. Strata asks for at least the frames in flight plus one, and never fewer than the
   driver's minimum plus one.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Renderer/GraphicsDevice.h`: the `GraphicsDeviceSpecification` :term[struct]{id=struct} (its field
  `MaxFramesInFlight`, default 2) and the `GraphicsDevice` interface with `BeginFrame`, `EndFrame`, `SetVSync`,
  `IsVSync` and `GetMaxFramesInFlight`.
- `Strata/src/Platform/Vulkan/VulkanGraphicsDevice.cpp`: `VulkanGraphicsDevice::BeginFrame` (the wait and the acquire),
  `VulkanGraphicsDevice::EndFrame` (the present and the fence) and the choice of present mode and image count.
- `Strata/src/Strata/Renderer/GraphicsModule.cpp`: the module that passes the window's vsync setting to the device.

## Further reading

- The Vulkan specification, chapter on presentation (registry.khronos.org/vulkan): the present modes and the swap chain, advanced. [Vulkan specification](https://registry.khronos.org/vulkan/)
- Vulkan Tutorial, the chapters on frames in flight and the swap chain: a worked program with two frames in flight, intermediate.
- Fabian Giesen, "A trip through the Graphics Pipeline 2011": each pipeline stage as hardware does it, advanced.
- Tomas Akenine-Moller and others, Real-Time Rendering: the pipeline, textures and filtering, intermediate.
