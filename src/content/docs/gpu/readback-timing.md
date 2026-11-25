---
id: gpu/readback-timing
title: "Readback and GPU timing"
description: "How Strata brings pixels and timings back from the graphics card without making a frame wait, and why the answers come two or three frames late."
kind: internals
size: L
tracks: [E]
needs: [gpu/frame-tour, core/profiling]
time: 85
learn:
  - id: poll-readback
    text: explain why Strata polls a readback each frame and what a caller must do while the answer is pending
  - id: trace-timestamps
    text: trace one timestamp from a pass boundary to a GPU stage time in the frame profiler
  - id: compute-interval
    text: compute a pass time from two timestamp ticks, also when the counter wraps
  - id: add-stage
    text: add a GPU stage in frame order and in the five lists that name the stages
since: 0.3.0
status: final
---

The :term[graphics processing unit]{id=gpu} (GPU), also called the graphics card, works on a different schedule from the :term[central processing unit]{id=processor} (CPU) that feeds it. Two kinds of facts are therefore hard to get from it: the pixels it drew, and the time it took to draw them. This page covers the part of Strata that brings both back to the CPU without ever making a frame wait. It covers copying a texture or a buffer into memory the CPU can read, picking one pixel, saving images, and timing every pass of the frame with the GPU's own clock. It does not cover the frame profiler's CPU side ([Measuring the frame](../core/profiling.md)), the picking tool of the Scene view, or the exposure and culling readbacks, which have their own pages.

## The problem and how engines solve it

Here is a case you will meet in your first week. A person clicks in the Scene view, and the editor must tell which entity is under the mouse. The answer exists only on the graphics card: the :term[renderer]{id=renderer} drew an image in which every pixel holds the number of the entity that covers it. The editor needs one pixel of that image. How does one pixel travel from the card to the program?

The path is slow for a reason you have already met in [the tour of a GPU frame](../gpu/frame-tour.md). The CPU does not draw anything. It records commands, hands them over, and moves on. The GPU runs them later, and by default the CPU may be two frames ahead of it. A command to copy a pixel is queued behind everything that was handed over before it.

A **readback** is a copy of data from the GPU's memory to memory the CPU can read. The simplest readback blocks: copy, then wait until the GPU says the copy is done.

Here is what the wait costs. Suppose each frame takes 10 ms on the GPU, and the CPU has handed over frame 100 while the GPU still draws frames 98 and 99. These numbers are invented, but the shape is real. The copy sits behind three frames of work, so the wait lasts about 30 ms. At 60 :term[frames per second]{id=frame-rate} a frame lasts 16.7 ms, so the program misses about two frames: the window freezes for a moment at each click.

Engines solve this in three ways, and each pays a different price.

- **Wait.** Block until the copy finishes. The code is short and the answer arrives in the same frame. The price is the stall above, so only tools and tests accept it.
- **Poll.** Submit the copy, keep drawing, and ask each frame whether it finished. Nothing waits, and the answer arrives a few frames later. The price is code that must cope with an answer that is not there yet.
- **Avoid.** Compute the answer on the CPU so that no copy is needed. This works for a few questions only; "which entity is under this pixel" needs the image the GPU drew.

Strata polls, and keeps the blocking form for tests and tools.

The second problem, timing, has the same shape. Which pass of the frame is slow? The CPU cannot tell by reading its clock while it records a command, because the command has not run yet. The GPU must write the time itself.

A **timestamp query** is a command that makes the GPU write the current value of its clock into a slot of a query pool. The GPU does this when it reaches that point in the :term[command list]{id=command-list}. A **GPU timestamp** is one such written value. Two timestamps around a pass give the pass's time. The values are read back like pixels, so they arrive late in the same way, and the same remedy applies: poll for them.

Timestamps are not the only way to measure the GPU, and Strata does not use the others for its always-on numbers. Vendor tools, such as the capture tools of NVIDIA and AMD that Further reading names, capture one frame and show its draws in detail. They run beside the program, on one vendor's hardware, for one captured frame. Pipeline statistics queries count work, for example how often a :term[shader]{id=shader} ran, not time. Timestamps are cheap and run in every frame on a device that supports them, so the Performance panel can show a moving graph.

## How the pieces fit

Two groups of code share the problem. The first group copies data back: `TextureReadback` for textures, `BufferReadback` for buffers, and `Renderer::ReadTexture`, the blocking form. The second group measures time: a timestamp pool made by the graphics device, the `GPUProfiler` that owns a ring of slots in it, and the `GPUPassTimer` that the renderer's code uses to mark pass boundaries. Everything runs on the :term[main thread]{id=main-thread}, because the readback classes and the profiler touch the device and the scene.

```mermaid caption="Who calls whom. The renderer starts each frame by asking the profiler to close and resolve slots. Passes write timestamps through a pass timer. Resolved times go to the frame profiler. Readbacks are separate objects that a caller polls." alt="A flow diagram. At the top the renderer's frame start calls the GPU profiler. The profiler owns a timestamp pool and sends resolved stage times to the frame profiler. Scene passes use a pass timer that writes into the profiler. On the right a texture readback, made by a caller such as picking, is polled by that caller and can feed an image writer."
flowchart TD
  BF[Renderer begin frame] --> GP[GPU profiler]
  PT[Pass timer in scene passes] --> GP
  GP --> TP[Timestamp pool in the device]
  GP --> FP[Frame profiler]
  PK[Caller such as picking] --> TR[Texture readback]
  TR --> IW[Image writer]
```

The profiler's ring is the heart of the timing half, so here is its life in one picture. The ring has one slot for each frame in flight plus two: with the default of two :term[frames in flight]{id=frames-in-flight}, four slots, each holding 256 timestamps. A slot is free, then open while its frame writes timestamps, then pending while the GPU finishes that frame, then free again once its times are read or dropped.

```mermaid caption="The life of one slot of the ring. A frame opens a free slot, writes its timestamps into it, closes it at the start of the next frame, and the slot waits as pending until the GPU has finished. A pending slot is then read and freed, or dropped and freed when its turn comes too early." alt="A state diagram with three states. A free slot becomes open when a frame starts. An open slot becomes pending when the next frame starts. A pending slot becomes free when the GPU finished and its times were read, or when it was dropped."
stateDiagram-v2
  [*] --> Free
  Free --> Open: a frame starts
  Open --> Pending: the next frame starts
  Pending --> Free: read after the GPU finished
  Pending --> Free: dropped
```

Now follow one frame through the ring with real numbers. Frame 10 opens slot 2 and writes 14 timestamps. At the start of frame 11 the renderer closes slot 2 and marks it with an :term[event query]{id=fence}, a marker the GPU completes after it finishes everything submitted so far.

The GPU is still busy with frame 10 at that moment, so the profiler polls, sees nothing and moves on. The same happens at the start of frame 12. At the start of frame 13 the poll says the work is done, so the profiler reads the 14 timestamps and hands the stage times to the frame profiler, labelled frame 10. The answer came three frames after the pass ran. With a faster GPU it would have come at the start of frame 12, two frames after, which is the meaning of "two to three frames late".

## The contract

The code that uses this part may rely on a few things and must respect a few others. Each rule has its reason.

- **Poll once per frame; never wait.** A frame that waits for the GPU loses the overlap between CPU and GPU, which is the reason for having two frames in flight. The poll costs a few microseconds; the wait costs frames.
- **Expect the answer late.** A readback is ready some frames after you ask, and a timing arrives two to three frames after the pass ran. Code keeps working with "not yet", and checks that what it asked about still exists when the answer comes.
- **A request can be refused.** Creating a readback can fail, for example on a compressed texture. It then returns null and a reason. The caller handles null every time.
- **Timings may be dropped.** A frame whose slot is still in use when its turn returns is dropped, never waited for, and a drop is not an error. A reader of the profiler must accept a frame without GPU times.
- **Never rely on stage ids.** Ids come from the order of registration in one build. Find stages by name.
- **Blocking forms are for tests and tools.** `Renderer::ReadTexture`, `TextureReadback::Wait`, `BufferReadback::Wait` and `SceneRenderer::ResolveGPUStats(true)` block. A shipped frame never calls them.
- **Timed command lists run in the frame that recorded them.** The profiler cannot match a timestamp to a frame otherwise.

:::rule
Strata never blocks a frame on the GPU: readbacks and timestamps are polled once per frame, and only tests and tools may use the blocking forms. The reason is the one in the first section: a wait turns the GPU's queued work into a stall of the whole program. See [the contract above](#the-contract) for the list of blocking forms.
:::

:::rule
Every new GPU pass is timed in a GPU stage, which is registered in frame order and added to the five lists that name the stages. The reason is that the Performance panel, the perf logs and the automation tools read those stages: a pass outside every stage hides its cost. See [changing it safely](#changing-it-safely).
:::

## A toy version

:::question
This sketch uses a :term[struct]{id=struct}, loops, `std::array` and `std::printf`. If any of them is new, the pages [first programs](../basics/programming-1.md), [functions and loops](../basics/programming-2.md) and [classes and calls](../basics/programming-3.md) teach them.
:::

Before the real code, here is the whole idea in a program you can run. It pretends to be a GPU that needs four frames to finish a copy. Each frame it first polls its slots and takes what is ready, then issues a new request into a free slot. It has three slots. If none is free, the request is dropped, not waited for.

```cpp sketch="gpu-readback-timing-toy.cpp"
#include <array>
#include <cstdint>
#include <cstdio>

namespace
{
	constexpr uint32_t c_SlotCount = 3;
	constexpr uint32_t c_GPUFrames = 4; // Frames the pretend GPU needs to finish one copy

	struct Slot
	{
		bool Pending = false;
		uint32_t IssuedFrame = 0;
	};

	bool IsReady(const Slot& slot, uint32_t frame)
	{
		return frame >= slot.IssuedFrame + c_GPUFrames;
	}
}

int main()
{
	std::array<Slot, c_SlotCount> slots;
	uint32_t dropped = 0;
	for (uint32_t frame = 0; frame < 9; frame++)
	{
		// Poll: take what is ready, never wait for what is not.
		for (uint32_t index = 0; index < c_SlotCount; index++)
		{
			if (slots[index].Pending && IsReady(slots[index], frame))
			{
				std::printf("frame %u: slot %u holds the copy of frame %u\n", frame, index, slots[index].IssuedFrame);
				slots[index].Pending = false;
			}
		}

		// Issue: the first free slot, or drop this frame's request.
		bool issued = false;
		for (uint32_t index = 0; index < c_SlotCount && !issued; index++)
		{
			if (!slots[index].Pending)
			{
				slots[index] = { true, frame };
				issued = true;
			}
		}
		if (!issued)
		{
			dropped++;
			std::printf("frame %u: every slot is pending, request dropped\n", frame);
		}
	}
	std::printf("dropped %u\n", dropped);
}
```

```text output-of="gpu-readback-timing-toy.cpp"
frame 3: every slot is pending, request dropped
frame 4: slot 0 holds the copy of frame 0
frame 5: slot 1 holds the copy of frame 1
frame 6: slot 2 holds the copy of frame 2
frame 7: every slot is pending, request dropped
frame 8: slot 0 holds the copy of frame 4
dropped 2
```

1. **Line 8:** the pretend GPU is slower than the ring is deep: it needs four frames, and the ring holds three requests.
2. **Lines 16–19:** a copy is ready when enough frames have passed since it was issued; the real code asks an event query instead.
3. **Lines 28–36:** the poll takes what is ready and never waits for what is not.
4. **Lines 38–47:** the issue step takes the first free slot.
5. **Lines 48–52:** with no free slot the request is dropped and counted, and the frame continues without waiting.

Read the output as a sequence. Frames 0, 1 and 2 fill the three slots, and at frame 3 the request is dropped. At frame 4 the first copy is ready, and its slot takes a new request. When the GPU is slower than the ring is deep, requests are lost in a steady rhythm, and no frame ever waits. The profiler makes the same trade: it prefers a missing number to a late frame.

The toy omits what makes the real code long. The GPU is a real device with an event query to poll, the data is a texture with a format, and every request can be invalid. The real code is the rest of the page.

## The real code

### Copying a texture region: `TextureReadback`

`TextureReadback::Create` is a careful function: it refuses every request it cannot serve, says why, and checks the region in a way that cannot overflow. Look first at the refusals about the texture itself, then at the region.

```cpp src="Strata/src/Strata/Renderer/TextureReadback.cpp#L25-L40"
if (formatInfo.blockSize != 1 || formatInfo.bytesPerBlock == 0 || formatInfo.hasStencil)
	return fail(fmt::format("the format of '{}' cannot be read back", desc.debugName));
if (desc.sampleCount > 1)
	return fail(fmt::format("'{}' is multisampled and cannot be read back", desc.debugName));
if (desc.dimension == nvrhi::TextureDimension::Texture3D || region.MipLevel >= desc.mipLevels || region.ArraySlice >= desc.arraySize)
	return fail(fmt::format("'{}' has no 2D subresource at mip {}, slice {}", desc.debugName, region.MipLevel, region.ArraySlice));

const uint32_t mipWidth = std::max(desc.width >> region.MipLevel, 1u);
const uint32_t mipHeight = std::max(desc.height >> region.MipLevel, 1u);
if (region.X >= mipWidth || region.Y >= mipHeight)
	return fail(fmt::format("the region at ({}, {}) is outside '{}' ({}x{})", region.X, region.Y, desc.debugName, mipWidth, mipHeight));
const uint32_t width = region.Width > 0 ? region.Width : mipWidth - region.X;
const uint32_t height = region.Height > 0 ? region.Height : mipHeight - region.Y;
// Compared as differences: X + Width could overflow.
if (width > mipWidth - region.X || height > mipHeight - region.Y)
	return fail(fmt::format("the region {}x{} at ({}, {}) exceeds '{}' ({}x{})", width, height, region.X, region.Y, desc.debugName, mipWidth, mipHeight));
```

1. **Line 25:** block-compressed formats, depth formats with a second aspect and formats with no :term[byte]{id=byte} size cannot become rows of pixels, so they are refused with the texture's debug name.
2. **Line 27:** a texture with several samples per pixel cannot be copied to plain rows, so it is refused.
3. **Lines 32–33:** a mip level is one of the smaller copies a texture keeps of itself, each half the size of the one before. Its size is the base size shifted right, never below one pixel.
4. **Lines 38–39:** the region is compared as differences, such as `width > mipWidth - region.X`, because the sum `X + Width` of two 32-bit numbers can wrap around to a small value and pass a check it should fail.

Here is the overflow in numbers. A texture is 100 pixels wide and a caller asks for X = 10 and a width of 4,294,967,295. The sum wraps to 9 and a naive check `X + Width <= 100` would accept it. The difference form compares 4,294,967,295 with 90, and refuses. An earlier check, `region.X >= mipWidth`, has already ensured that `mipWidth - region.X` cannot go below zero, so the subtraction itself is safe too.

The second half of `Create` builds the copy: a staging texture, which is a texture in memory the CPU can read, and one command list that copies the region into it.

```cpp src="Strata/src/Strata/Renderer/TextureReadback.cpp#L42-L67"
nvrhi::IDevice* device = Renderer::GetDevice();
nvrhi::TextureDesc stagingDesc;
stagingDesc.width = width;
stagingDesc.height = height;
stagingDesc.format = desc.format;
stagingDesc.debugName = "TextureReadback";
stagingDesc.initialState = nvrhi::ResourceStates::CopyDest;
stagingDesc.keepInitialState = true;
Scope<TextureReadback> readback(new TextureReadback());
readback->m_Staging = device->createStagingTexture(stagingDesc, nvrhi::CpuAccessMode::Read);
readback->m_Query = device->createEventQuery();
nvrhi::CommandListHandle commandList = device->createCommandList();
if (!readback->m_Staging || !readback->m_Query || !commandList)
	return fail(fmt::format("failed to create the staging resources for reading '{}'", desc.debugName));

const nvrhi::TextureSlice source = nvrhi::TextureSlice()
	.setOrigin(region.X, region.Y)
	.setSize(width, height, 1)
	.setMipLevel(region.MipLevel)
	.setArraySlice(region.ArraySlice);
commandList->open();
commandList->copyTexture(readback->m_Staging, nvrhi::TextureSlice(), texture, source);
commandList->close();
device->executeCommandList(commandList);
// The query completes with the last submitted command list, which is the copy.
device->setEventQuery(readback->m_Query, nvrhi::CommandQueue::Graphics);
```

1. **Lines 43–49:** the staging texture has the region's size and the source's format, and its initial state is the copy destination.
2. **Lines 50–52:** the readback object owns its staging texture and its event query. Destroying a readback that is still pending is safe.
3. **Lines 62–65:** one command list opens, copies the region, closes and executes at once. Nothing here waits for it.
4. **Lines 66–67:** the event query is set after the last submitted list, which is the copy, so `IsReady` later means "the copy finished".

`IsReady` is one call: `pollEventQuery`, which returns at once. `GetResult` maps the staging memory, copies the rows out into a `ReadbackImage` with tight rows, top row first, then releases the mapping. The staging texture's rows may be padded, so the copy goes row by row with the pitch the device reports, the length of a staging row in bytes, padding included. `Wait` exists for tests and tools; it calls `waitEventQuery`.

`Renderer::ReadTexture` is the blocking form, five lines of logic: create a readback for one mip level and slice, log the reason on refusal, `Wait`, and `GetResult`. The back-buffer capture of the graphics module uses it, because a capture is a tool's request, not part of a frame the player sees.

### Copying a buffer: `BufferReadback`

`BufferReadback` is the same idea for buffers, with one difference: you use one object again and again. You create it once with a capacity. Each frame, `Record` puts the copy of a byte range into a command list that you already have open, `Submit` marks it after that list has executed, `IsReady` polls, and `Read` takes the bytes. A new `Record` replaces the previous copy. The renderer's counters use this for small results requested every frame, where creating a :term[staging buffer]{id=staging-buffer} per request would be waste.

`Read` returns false while the copy is pending, when the staging memory cannot be mapped, or when the offset lies beyond what was recorded.

### Picking: one pixel, 0 means nothing

Picking is the first customer of `TextureReadback`. The :term[depth prepass]{id=depth-prepass} writes, for every pixel, a number that names the entity covering it into a 32-bit target. `SceneRenderer::ReadEntityIDAsync` reads one pixel of that target; `GetEntityFromID` turns the number into an entity.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L4456-L4482"
Scope<TextureReadback> SceneRenderer::ReadEntityIDAsync(uint32_t x, uint32_t y)
{
	if (!m_HasRenderedFrame || !m_EntityIDTexture || x >= m_ViewportSize.x || y >= m_ViewportSize.y)
		return nullptr;

	TextureReadbackRegion region;
	region.X = x;
	region.Y = y;
	region.Width = 1;
	region.Height = 1;
	std::string error;
	Scope<TextureReadback> readback = TextureReadback::Create(m_EntityIDTexture, region, &error);
	if (!readback)
		m_Errors.Report(fmt::format("reading the entity ID at ({}, {}) failed: {}", x, y, error));
	return readback;
}

Entity SceneRenderer::GetEntityFromID(Scene& scene, uint32_t id)
{
	// The prepass writes the entity handle + 1, so 0 means that nothing was drawn.
	if (id == 0)
		return {};
	const entt::entity handle = static_cast<entt::entity>(id - 1);
	if (!scene.GetRegistry().valid(handle))
		return {};
	return Entity(handle, &scene);
}
```

1. **Line 4458:** with no frame rendered yet, no entity-ID target or a pixel outside the viewport, the answer is a null readback and no error, because these are normal states. A renderer made without the target picks nothing.
2. **Lines 4464–4465:** a region of 1 by 1 pixel, so the copy moves four bytes.
3. **Line 4469:** a refusal of `Create` goes to the renderer's error list with its reason, and the caller gets null.
4. **Lines 4475–4477:** the prepass writes the entity's handle plus one, so the target's cleared value 0 means that nothing was drawn there.
5. **Line 4479:** the answer arrives frames later and the entity may be gone. The handle is checked against the scene before an `Entity` is made.

`GetEntityAt` is the blocking form of the same call: it makes the readback, calls `Wait` and resolves the number. It exists for tests and tools. The Scene view uses the asynchronous form, as [the Scene view page](../editor-ui/scene-view.md) shows.

### Saving and loading images: `ImageWriter` and `ImageReader`

A readback gives pixels in memory. `ImageWriter` turns them into files. `EncodePNG` and `SavePNG` take a `ReadbackImage` in an 8-bit `RGBA` or `BGRA` format, `UNORM` or :term[sRGB]{id=srgb}. They swap the channels of a `BGRA` :term[back buffer]{id=back-buffer}, and by default force the alpha to opaque, which is what a screenshot of the back buffer wants. A format they cannot encode fails with a reason.

For floating-point images there is `EncodeHDR`: it writes a Radiance `.hdr` file from linear floats, in the `RGBE` form with run-length encoding, which the :term[high dynamic range]{id=high-dynamic-range} (HDR) texture importer reads. Negative and non-finite values are written as 0. The probe bake saves its captures this way, as [the page on probes](../indirect/probes.md) explains. `ImageReader::DecodeRGBA8` is the small reverse: it reads engine-written images, such as thumbnails, and refuses any image larger than 4,096 pixels on a side.

### The timestamp pool

All timing rests on `GPUTimestampPool`, made by `GraphicsDevice::CreateTimestampPool`. Its interface has four verbs, and the comments in `GraphicsDevice.h` give the rules.

- `Write` records into a command list the order for the GPU to store its time in timestamp number `index`, once every earlier command of the queue finished.
- `Read` returns the ticks of a range, but only when the GPU has written every one of them. Otherwise it returns false at once. It never waits.
- `Reset` and `ResetCompleted` let timestamps be written again. `ResetCompleted` runs on the host, that is the CPU, with no command list, when the device can reset queries there; that is allowed only after the caller saw the earlier writes complete. Without host resets it falls back to `Reset`, a command list of its own.
- `GetValueMask` tells which bits of a value are valid, because a queue may keep fewer than 64 bits.

The mask matters when the clock wraps around. A difference of two values taken with unsigned arithmetic still gives the right interval if you keep only the valid bits. The profiler does exactly that.

```cpp src="Strata/src/Strata/Renderer/GPUProfiler.cpp#L268-L272"
float GPUProfiler::ToMilliseconds(uint64_t begin, uint64_t end) const
{
	const uint64_t ticks = (end - begin) & m_Pool->GetValueMask();
	return static_cast<float>(static_cast<double>(ticks) * m_PeriodNs * 1.0e-6);
}
```

The function converts one interval to milliseconds: it subtracts, masks, multiplies by the tick period in nanoseconds, and converts nanoseconds to milliseconds. Take a device with 32 valid bits, so the mask is 4,294,967,295, and a period of 1 ns per tick. The begin timestamp reads 4,294,967,000 and the end reads 500, because the counter wrapped. The unsigned difference is huge, but masking it leaves 796 ticks, which is 796 ns or 0.0008 ms. A plain subtraction as signed numbers would give a negative time.

### The profiler's ring

`GPUProfiler` owns the ring. Its :term[constructor]{id=constructor} makes the pool with slots times 256 timestamps, where the slot count is the device's frames in flight plus two. Without timestamp support, or when the pool cannot be made, the profiler is disabled and every call is a no-op. When it works, it tells the frame profiler that GPU times are expected.

`Renderer::BeginFrame` calls `GPUProfiler::BeginFrame`, which does three things in order: it closes the frame's open slot, resolves pending slots, and opens the next slot. Closing sets an event query after the frame's submissions, so a later poll shows whether the GPU finished the frame. A slot that wrote nothing is freed at once and reports an empty frame.

Resolving is where the "never wait" rule is kept, so read it closely.

```cpp src="Strata/src/Strata/Renderer/GPUProfiler.cpp#L200-L237"
void GPUProfiler::ResolvePending()
{
	// Oldest first: the GPU completes the frames in order, so a slot it has not completed ends the search.
	while (true)
	{
		uint32_t oldest = ~0u;
		for (uint32_t index = 0; index < m_Slots.size(); index++)
		{
			const Slot& slot = m_Slots[index];
			if (slot.State == SlotState::Pending && (oldest == ~0u || slot.Serial < m_Slots[oldest].Serial))
				oldest = index;
		}
		if (oldest == ~0u)
			return;
		Slot& slot = m_Slots[oldest];
		// Read once the GPU completed the frame: before that, its reset may not have run yet either.
		if (!IsSlotDone(slot))
			return;
		if (ResolveSlot(slot, oldest))
			continue;
		// The GPU completed the frame's work, yet not every timestamp is readable. MoltenVK makes timestamps readable a
		// little after the work's completion is signaled: the slot waits for the next frame. Still missing then, a command
		// list with timestamps was never executed: its times are incomplete, so the frame goes without them.
		const uint64_t frame = m_Profiler.GetTotalFrameCount();
		if (!slot.Unreadable)
		{
			slot.Unreadable = true;
			slot.UnreadableFrame = frame;
			return;
		}
		if (frame == slot.UnreadableFrame)
			return;
		m_Stats.DroppedFrames++;
		if (slot.ResetCount == m_Profiler.GetResetCount())
			m_Profiler.RecordGPUFrame(slot.ProfilerFrame, {});
		FreeSlot(slot);
	}
}
```

1. **Lines 202–211:** the loop takes the pending slot with the lowest serial number, the oldest frame, because the GPU completes frames in order.
2. **Line 216:** if the oldest slot is not done, the function returns, since every newer one is not done either. This is the poll: a yes or no, never a wait.
3. **Lines 218–219:** a slot whose timestamps can all be read hands its stage times to the frame profiler and the loop continues with the next oldest.
4. **Lines 224–229:** if the GPU is done but a timestamp cannot yet be read, the slot waits one frame. The code names :term[MoltenVK]{id=moltenvk}, the :term[Vulkan]{id=vulkan} layer on macOS, which lets values be read only a little after it signals completion.
5. **Lines 232–235:** still missing after that frame, a command list with timestamps was never executed, so the times are incomplete. The frame is counted as dropped and goes without them.

`ResolveSlot` reads the ticks, converts each recorded interval with the function above, and adds them up per stage. Several intervals of one stage add up, like CPU stages do, and every stage that was timed gets an entry, even one that took no time. The sums go to `FrameProfiler::RecordGPUFrame` for the frame that recorded them, unless the profiler was reset in between.

`OpenSlot` is the other place that decides about waiting. If the slot whose turn has come is still pending, its frame was never read, so the profiler counts a dropped frame. When the GPU has not finished with that slot, this frame goes without timing, because the timestamps may still be written. Otherwise the slot's timestamps are reset on the host, so that the frame's timed command lists may execute in any order. `GPUProfilerStats` counts resolved frames, dropped frames, skipped timestamps beyond 256 in a frame, and the profiler's own CPU time.

### Marking pass boundaries: `GPUPassTimer`

The renderer's code never calls the profiler directly. It uses `GPUPassTimer`, which marks the boundaries between passes of one command list. Passes follow each other, so one timestamp ends a pass and starts the next one. N passes need N + 1 timestamps, and the stages tile the command list without gaps.

```cpp src="Strata/src/Strata/Renderer/GPUProfiler.cpp#L357-L392"
GPUPassTimer::GPUPassTimer(GPUProfiler* profiler, nvrhi::ICommandList* commandList, FrameStageID stage, GPUTimerRecord* record)
	: m_Profiler(profiler && profiler->IsEnabled() ? profiler : nullptr), m_CommandList(commandList), m_Record(record), m_Stage(stage)
{
	if (!m_Profiler)
		return;
	m_Slot = m_Profiler->GetOpenSlot();
	m_Begin = m_Profiler->WriteTimestamp(m_CommandList);
}

void GPUPassTimer::Next(FrameStageID stage)
{
	if (!m_Profiler)
	{
		m_Stage = stage;
		return;
	}
	if (stage == m_Stage)
		return;
	const uint32_t boundary = m_Profiler->WriteTimestamp(m_CommandList);
	// A frame boundary between the two timestamps (the slot changed) leaves the interval out.
	if (m_Profiler->GetOpenSlot() == m_Slot)
		m_Profiler->AddInterval(m_Stage, m_Begin, boundary, m_Record);
	m_Slot = m_Profiler->GetOpenSlot();
	m_Begin = boundary;
	m_Stage = stage;
}

void GPUPassTimer::End()
{
	if (!m_Profiler)
		return;
	const uint32_t end = m_Profiler->WriteTimestamp(m_CommandList);
	if (m_Profiler->GetOpenSlot() == m_Slot)
		m_Profiler->AddInterval(m_Stage, m_Begin, end, m_Record);
	m_Profiler = nullptr;
}
```

1. **Line 358:** with no profiler, or a disabled one, the timer holds a :term[null pointer]{id=null-pointer}, and everything after it does nothing. Code never has to ask whether timing is on.
2. **Lines 362–363:** the constructor remembers the open slot and writes the first timestamp where the first pass starts.
3. **Line 373:** `Next` with the stage the timer already has changes nothing, so a caller may call it unconditionally.
4. **Lines 375–378:** `Next` writes a boundary timestamp. If the open slot is still the same one, the interval from the last timestamp to this one goes to the stage that ended.
5. **Lines 384–391:** `End` writes the last timestamp the same way, then turns the timer off. The :term[destructor]{id=destructor} calls it, so an early return cannot leave the timer open.

The check of the slot is the "only within one slot" rule. A timer that lives across a frame boundary could write its begin into one slot and its end into the next. The two values belong to different frames, so the interval would be meaningless, and the timer omits it.

The scene renderer builds one timer where the frame's first pass starts and calls `Next` at each stage's first pass; for example, `Next(gpuStages.Cull)` before the culling dispatches. Where a stage does not run, for instance when a frame has no atmosphere, nothing calls `Next` for it, and the stage has no entry in that frame.

### A renderer's own times

The frame profiler gets the sums of every user of the profiler, all scene renderers together. A renderer that wants its own numbers passes a `GPUTimerRecord` to its timers, which collects the intervals it timed. `SceneRenderer::GetGPUStats` later gives these times, once all their timestamps are written; the renderer keeps its last six records and reads the newest complete one. `ResolveGPUStats(false)` only polls. `ResolveGPUStats(true)` calls `GPUProfiler::Resolve(true)`, which waits until the device is idle, so it belongs to tests and tools.

### The stages

A **GPU stage** is a named slice of the GPU's frame with a time per frame. In the frame profiler it is a stage of the kind GPU, as CPU stages are of the kind CPU. `RendererGPUStages` holds the ids of seventeen of them. The renderer module registers them, so they exist before anything reads the profiler's list. The table gives the order in which `RendererGPUStages::Get` registers them and the order in which a frame runs them.

| Registered | Stage | Runs in the frame |
| --- | --- | --- |
| 1 | `GPU.Uploads` | the upload queue's batches |
| 2 | `GPU.Setup` | first stage of the scene's command list |
| 3 | `GPU.Aerial` | after `GPU.Cull` |
| 4 | `GPU.Cull` | after `GPU.Setup` |
| 5 to 8 | `GPU.Shadows`, `GPU.Prepass`, `GPU.ScreenShadows`, `GPU.AO` | in this order |
| 9 | `GPU.RadianceCascades` | after `GPU.AO` |
| 10 | `GPU.Reflections` | after `GPU.RadianceCascades` |
| 11 to 14 | `GPU.Opaque`, `GPU.Transparent`, `GPU.TAA`, `GPU.MotionBlur` | `GPU.MotionBlur` runs after `GPU.DepthOfField` |
| 15 | `GPU.DepthOfField` | before `GPU.MotionBlur` |
| 16 and 17 | `GPU.Post`, `GPU.Overlays` | in this order |

Two stages break the rule "registered in frame order". The engine's developer guide names one: `GPU.DepthOfField` was registered after `GPU.MotionBlur` and runs before it. The code has a second: `GPU.Aerial` is registered before `GPU.Cull`, but the scene renderer times it after.

The aerial perspective needs the frame's constants and the atmosphere's tables, so the code starts its stage after the light clusters. The work between culling and that point stays in the stage that was running. Registration order fixes only ids and perf-log columns, so the exceptions cost nothing. A reader who assumes the stages are listed in time order will read two rows wrongly.

Other modules add stages of their own. The game's user interface (UI) module registers `GPU.UI` when it registers. Its pass times its draws with the renderer's timer, then hands the timer back to `GPU.Overlays`. The editor's ImGui layer registers `GPU.ImGui` the first time it draws, which is why games show no such column.

`Present` is not a GPU stage. It is a CPU stage of the frame profiler, which times the display's wait; how the upload queue's batches relate to it is on [the upload queue page](../gpu/upload-queue.md).

::figure{id=gpu-stages-panel}

### Tile-based drivers and why boundaries go where passes end

Some GPUs, such as those of Apple's machines, use a **tile-based renderer**: they split the screen into small tiles, draw everything for one tile in fast on-chip memory, and write the result out once. A driver for such a GPU may write a timestamp recorded inside a render pass only when the pass ends. On macOS, Strata reaches the GPU through MoltenVK, which reads Metal's GPU counters only between Metal's groups of commands, so a timestamp inside a pass that continues is written when that pass ends.

The effect is visible. In the forward pass, `GPU.Transparent` begins inside a pass that `GPU.Opaque` started. On macOS, the boundary timestamp is written at the end of the pass, so the time of `GPU.Transparent` appears in `GPU.Opaque`. Stages that begin where a pass ends, such as shadows, the prepass, the opaque pass and post-processing, are exact everywhere. That is why a new stage's boundary should be put where a pass ends, when it can.

:::example
Frame 10 runs these stages with these invented times: `GPU.Shadows` 1.2 ms, `GPU.Prepass` 0.8 ms, `GPU.Opaque` 4.5 ms and `GPU.Post` 1.0 ms, so a GPU frame of 7.5 ms. On a desktop GPU the profiler reports those four numbers for frame 10 two or three frames later. At 60 frames per second a frame is 16.7 ms, so the GPU has 9.2 ms of idle time. If a new pass of 12 ms were added to `GPU.Post`, the GPU would need 19.5 ms, so the frame would become :term[GPU-bound]{id=gpu-bound}. The panel would show it two or three frames after the change reached the screen.
:::

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Blocking readback in the frame | Strata's own tests, tools and back-buffer captures | Same-frame answers, shorter code | A stall of about the GPU's queued work at every call, as in the 30 ms example |
| One staging resource used again by every request | `BufferReadback`, for the renderer's counters | No creation per request | Only one copy at a time; each new `Record` replaces the last |
| Vendor capture tools | The capture tools of NVIDIA and AMD | Per-draw times and hardware counters | Always-on numbers: the tools run beside the game, for one frame, on one vendor's card |
| Pipeline statistics queries | Vulkan's own query type | Counts of shader runs | Time itself: counts do not say which pass is slow |
| A timestamp per draw | No Strata code; the pool would allow it | Finer detail | The 256-timestamp budget per frame, more CPU cost, and worse accuracy on tile-based drivers |

Further reading names sources for the vendor tools and the query types.

## How it is tested

The readback has its own GPU suite, `GPU.TextureReadback`, in `StrataTests/src/Renderer/GPUTextureReadbackTests.cpp`. Its test cases read regions, mips and array slices without blocking. They check that invalid requests are refused and that pending readbacks may be dropped. One reads the entity under a pixel without waiting for the GPU.

`GPU.Renderer.Timers` in `StrataTests/src/Renderer/GPUTimerTests.cpp` covers the timing half. Its cases write timestamps outside and inside render passes and read them in order.

Others check that stages resolve within the frames in flight, add up and never make a frame wait. A frame whose timestamps were never executed is dropped without waiting. Timed command lists may execute in any order. The first preparation of the back buffer shows as the `Present` stage, outside the :term[work time]{id=work-time}.

`StrataTests/src/Renderer/ImageWriterTests.cpp` checks PNG and HDR encoding, the refusals, and that `ImageReader` decodes what the writer wrote.

The two GPU suites need a graphics card and carry the label `gpu`; the image tests, in the suite `Renderer`, do not. Run them through the shared device, and expect each to end with no new graphics errors:

```sh
ctest --preset windows-debug -L gpu
build/windows/bin/Debug/StrataTests.exe --test-suite=GPU.Renderer.Timers
```

The first command runs every GPU suite, and the second runs one suite directly. A new test for a fixed readback bug should fail without the fix, so run it once before trusting it.

## Changing it safely

To add a GPU stage, add a member to `RendererGPUStages` and register it in `RendererGPUStages::Get` near the stage its pass follows. Call `Next` where the pass begins, and `Next` back to the following stage where it ends. Then update the five lists that name the stages:

- the description of the `editor.perf` command in `StrataEditor/src/Editor/EditorStateCommands.cpp`;
- `StrataTests/src/Editor/EditorProfilerTests.cpp`;
- `StrataTests/src/Runtime/FramePerfLogTests.cpp`;
- the stage table in `Docs/Architecture.md`;
- `.claude/skills/strata-editor-automation/SKILL.md`.

Inserting a stage moves the ids of the later ones. That is harmless, because ids are compared only inside one build and perf-log readers find columns by name.

The rules of the engine's guide that apply, with their reasons:

- Wrap every new pass in a stage, so its cost is visible and never hides inside a neighbour.
- Register a module's stages when the module itself registers, so the perf log's :term[header]{id=header} already has their columns. A stage first registered after the header is written gets no column. A stage that only some programs have, such as `GPU.ImGui`, registers where it is first used.
- Call `End`, or let the timer leave its scope, on every path that closes the command list; an open timer at the end of a frame leaves its last interval unwritten.
- An overlay pass uses the frame's own timer: it moves the timer to its stage before its draws, and back to the earlier stage after them, as the game UI does.
- A change that adds a blocking call to a frame is a defect, even when it measures fast on your machine, because the stall is the GPU's queued work, which varies with the scene.

## Summary

- A readback copies GPU data into a staging resource, and the caller polls an event query once per frame. The answer comes frames later, a request may be refused, and a frame never waits.
- The GPU writes timestamps into a pool. The profiler's ring holds one frame's timestamps in each slot, and resolves them two to three frames later into GPU stages, or drops the frame.
- A pass time is the difference of two ticks, masked to the valid bits so that a wrapped counter still gives the right interval, then multiplied by the tick period.
- A new GPU stage is registered in frame order, timed with `GPUPassTimer::Next`, and listed in the five places that name the stages.

## Check yourself

1. A caller creates a `TextureReadback` in frame 50. In which frames may it call `GetResult` successfully, and what should it do in the frames before?
   - (a) Only in frame 50, because the copy is submitted in that frame.
   - (b) In frame 50 or later; it polls `IsReady` and keeps drawing until it is true.
   - (c) Only after calling `Wait`, because `GetResult` blocks until the copy is done.

   :::answer{tests="poll-readback"}
   Option (b). The copy is queued behind earlier work, so it is usually not done in frame 50: (a) is wrong. `GetResult` never blocks; it returns false while the copy is pending, so (c) is wrong, and `Wait` would stall the frame.
   :::

2. Change the toy so that it has four slots and the GPU needs four frames. How many requests are dropped in frames 0 to 8?

   :::answer{tests="poll-readback"}
   None. Frames 0 to 3 fill the four slots. At frame 4 the first slot is ready and frees before the new request, and the pattern repeats, so every frame finds a free slot. A ring as deep as the GPU's delay never drops a request.
   :::

3. A GPU has 32 valid bits and 1 ns per tick. The begin timestamp is 4,294,967,200 and the end is 100. What is the pass time in nanoseconds?

   :::answer{tests="compute-interval"}
   196 ns. The end minus the begin, taken in unsigned arithmetic and masked to 32 bits, is 100 plus 4,294,967,296 minus 4,294,967,200, which is 196. A subtraction without the mask gives a number near 2 to the power 64 or a negative time.
   :::

4. A pass ran in frame 20 and the frame profiler reports its GPU time while frame 23 is at its start. Which statement is right?
   - (a) The profiler waited three frames for the GPU, which is how timestamps work.
   - (b) The slot was polled at the starts of frames 21 and 22, found pending, and read at frame 23 once the event query said done.
   - (c) The pass ran again in frame 23.

   :::answer{tests="trace-timestamps"}
   Option (b). The profiler never waits: each frame start only asks, and a pending slot stays pending. (a) confuses the delay with a wait, and (c) has no basis; the number is the time of frame 20, labelled with that frame.
   :::

5. You add `GPU.Fog` to the end of `RendererGPUStages::Get`, although its pass runs between `GPU.Opaque` and `GPU.Transparent`. What breaks?
   - (a) Nothing that depends on correctness: only the guide's convention of registering in frame order, which sets the ids and the perf-log columns.
   - (b) The timer, because intervals are matched by registration order.
   - (c) The five lists can be skipped because the stage is last.

   :::answer{tests="add-stage"}
   Option (a). The timer needs only the stage's id, so (b) is wrong. The five lists name every stage, so (c) is wrong. The convention exists so that columns read in frame order.
   :::

## Exercises

1. **Basic.** Add a GPU stage named `GPU.Fog` for a new pass between `GPU.Opaque` and `GPU.Transparent`. Say which files you change and what each change contains.

   :::answer[Worked solution]{tests="add-stage"}
   First, add `FrameStageID Fog` to `RendererGPUStages` in `Strata/src/Strata/Renderer/GPUProfiler.h`, and in `RendererGPUStages::Get` in `GPUProfiler.cpp` register `GPU.Fog` after `GPU.Opaque` and before `GPU.Transparent`. Second, in `Strata/src/Strata/Renderer/SceneRenderer.cpp` call `gpuTimer.Next(gpuStages.Fog)` before the pass; the existing `gpuTimer.Next(gpuStages.Transparent)` after it then ends the fog's interval. Third, name the stage in the five lists: the `editor.perf` description, the profiler test, the perf-log test, the stage table of `Docs/Architecture.md` and the automation skill. Last, run `GPU.Renderer.Timers` and the two test files.
   :::

2. **Medium.** Trace it yourself. On a source build, find where one frame's timestamps reach the profiler, and measure how many frames separate the pass from the report.

   :::answer[Worked solution]{tests="trace-timestamps"}
   Put a breakpoint in `GPUProfiler::ResolvePending` in `Strata/src/Strata/Renderer/GPUProfiler.cpp`. When it stops, the oldest pending slot is the first one found by the loop; step to `ResolveSlot` after `IsSlotDone` returns true. Compare the slot's `ProfilerFrame` with `FrameProfiler::GetTotalFrameCount()`. You should see a difference of two or three frames, and a pending slot that returns early when the GPU is not done.
   :::

3. **Hard.** Write a screenshot tool that never stalls a frame: it accepts a request, ignores a second request while one is pending, polls once per frame, and saves when ready. Show with a program that every frame is drawn.

   :::answer[Worked solution]{tests="poll-readback" solution="sketches/gpu-readback-timing-screenshot.cpp"}
   The tool holds at most one readback. `Request` refuses while one is pending, and `Update` polls without waiting.

   ```cpp sketch="gpu-readback-timing-screenshot.cpp"
   #include <cstdint>
   #include <cstdio>
   #include <optional>

   namespace
   {
   	constexpr uint32_t c_GPUFrames = 3; // Frames the pretend GPU needs to finish one copy

   	struct Readback
   	{
   		uint32_t IssuedFrame = 0;

   		bool IsReady(uint32_t frame) const { return frame >= IssuedFrame + c_GPUFrames; }
   	};

   	// Request starts one readback; Update polls it once per frame and never waits.
   	class ScreenshotTool
   	{
   	public:
   		bool Request(uint32_t frame)
   		{
   			if (m_Pending)
   				return false;
   			m_Pending = Readback { frame };
   			return true;
   		}

   		void Update(uint32_t frame)
   		{
   			if (!m_Pending || !m_Pending->IsReady(frame))
   				return;
   			std::printf("frame %u: saved the screenshot of frame %u\n", frame, m_Pending->IssuedFrame);
   			m_Pending.reset();
   		}
   	private:
   		std::optional<Readback> m_Pending;
   	};
   }

   int main()
   {
   	ScreenshotTool tool;
   	for (uint32_t frame = 0; frame < 8; frame++)
   	{
   		if ((frame == 2 || frame == 3) && !tool.Request(frame))
   			std::printf("frame %u: a screenshot is still pending\n", frame);
   		tool.Update(frame);
   		std::printf("frame %u: drawn\n", frame);
   	}
   }
   ```

   ```text output-of="gpu-readback-timing-screenshot.cpp"
   frame 0: drawn
   frame 1: drawn
   frame 2: drawn
   frame 3: a screenshot is still pending
   frame 3: drawn
   frame 4: drawn
   frame 5: saved the screenshot of frame 2
   frame 5: drawn
   frame 6: drawn
   frame 7: drawn
   ```

   1. **Lines 20–26:** `Request` refuses while one readback is pending, so a second request cannot pile up.
   2. **Lines 28–34:** `Update` asks whether the copy is ready and returns at once when it is not.
   3. **Line 36:** the tool holds at most one pending readback.
   4. **Lines 45–46:** the request at frame 3 is refused and reported.
   5. **Lines 47–48:** the poll comes before the frame's work, and nothing in the loop waits.

   Every frame prints "drawn", so no frame waited; the screenshot of frame 2 is saved at frame 5, three frames later. In Strata, `Update` would call `TextureReadback::IsReady`, then `GetResult`, then `ImageWriter::SavePNG`.
   :::

## Where it lives in Strata

- Readbacks: `Strata/src/Strata/Renderer/TextureReadback.h` and `.cpp`, `BufferReadback.h` and `.cpp`, `Renderer::ReadTexture` in `Renderer.cpp`.
- Picking: `SceneRenderer::ReadEntityIDAsync` and `GetEntityFromID` in `SceneRenderer.cpp`.
- Images: `ImageWriter.h` and `ImageReader.h` in `Strata/src/Strata/Renderer/`.
- Timing: `GPUProfiler.h` and `.cpp` (`GPUProfiler`, `GPUPassTimer`, `RendererGPUStages`), `GPUTimestampPool` in `GraphicsDevice.h`, its Vulkan form in `Strata/src/Platform/Vulkan/VulkanGraphicsDevice.cpp`.
- Tests: `GPU.TextureReadback`, `GPU.Renderer.Timers`, and `StrataTests/src/Renderer/ImageWriterTests.cpp`.
- Command: `editor.perf` summarizes the frame profiler's stages, GPU stages included.

## Further reading

- The Vulkan specification's chapter on queries: timestamp and pipeline statistics queries (advanced).
- NVIDIA's documentation of Nsight Graphics and AMD's documentation of the Radeon GPU Profiler: capture tools for one frame (intermediate).
