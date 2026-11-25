---
id: gpu/upload-queue
title: "Staging and the upload queue"
description: "How Strata moves bytes from the processor into graphics memory at a bounded cost per frame, and why the frame waits for the display only after its uploads."
kind: internals
size: L
tracks: [E]
needs: [gpu/resources-lifetimes]
time: 70
learn:
  - id: staging-need
    text: explain why a texture reaches graphics memory through a staging buffer and in budgeted steps
  - id: step-size
    text: compute the bytes of an upload step from the time left, the measured speed and the granule
  - id: staging-reuse
    text: explain when a staging buffer may be written again and which rule keeps that safe
  - id: back-buffer
    text: explain what PrepareBackBuffer does and why its Present stage is a wait, not work
  - id: trace-plan
    text: trace one large texture's upload through the calls of PlanStep
since: 0.3.0
status: final
---

A game loads a large texture while the player walks through a door. The pixels sit in the :term[main memory]{id=memory} of the computer, and the :term[graphics processing unit]{id=gpu} (GPU) must read them from its own fast memory. Something has to copy the :term[bytes]{id=byte} across, and it must do so without making the frame late.

This page covers the part of Strata that does that copying: the upload queue and the pool of staging memory behind it. It decides how many bytes move in each frame, writes them into memory both sides can reach, orders the copies, and tells the assets when their data has arrived. It also makes sure that the frame waits for the display only after these uploads were sent. It does not decide which assets to load or when; that belongs to [the asset upload pages](../assets/uploads.md).

## The problem and how engines solve it

The memory of a GPU comes in kinds. Device-local memory is the fastest for the GPU to read, and the :term[central processing unit]{id=processor} (CPU) cannot write to it. Memory that the CPU can write is a different block, which the GPU reads more slowly. So a texture the GPU samples must first be written by the CPU into one block, then copied by the GPU into the other. The first block is the **staging buffer**: memory that the CPU can write, which serves as the source of copies into device-local resources.

Take a texture of 4,096 by 4,096 texels with four bytes each, a size that appears in real games. That is 16,777,216 texels times 4 bytes, or 67,108,864 bytes (64 MiB). A modern processor writes memory at billions of bytes per second, and Strata starts by assuming 4 million bytes per millisecond. At that speed the writing alone takes 67,108,864 / 4,000,000, about 16.8 ms.

A frame at 60 :term[frames per second]{id=frame-rate} lasts 16.7 ms. One call that writes the whole texture makes one frame twice as long, and the player sees a pause.

The cost is real even when the data is small. Every call that makes a new staging buffer asks the graphics driver for memory, and the driver may take from a fraction of a millisecond to a millisecond to answer. A game that makes a new buffer for every small upload pays that price again and again. The mistake has a name in practice: pushing big data through :term[NVRHI's]{id=nvrhi} `writeBuffer` every frame, which takes its staging outside the pool and outside any budget.

The second common mistake is a frame that waits for a load to finish before it continues. Both turn a loading cost into a visible hitch.

Engines answer with three ideas, which this page builds in order.

- **Use staging memory again.** A ring or a pool of buffers is made once and written again, so the driver is asked rarely. The danger is writing a buffer while the GPU still reads it, so each buffer needs a signal that tells when the GPU is done.
- **Copy beside the frame.** Many GPUs have a second queue only for copies. Uploads there run while the graphics queue draws.
- **Spend a budget per frame.** The engine splits a large upload into pieces and copies only as many in a frame as its time and byte limits allow. An **upload budget** is that limit: the bytes, the milliseconds and the staging bytes that one frame may spend on uploads.

Strata uses the first and third ideas and has the second built, but off. The sections below show why.

## The map: from asset bytes to a complete ticket

Three objects share the work, and all of them belong to the :term[main thread]{id=main-thread}. The asset managers decide what to upload and hand each call its budget. `GPUUploadQueue` plans each piece, writes it into staging, records the copy and tracks completion. `StagingPool` owns the staging buffers and knows when each may be written again. A fourth piece, `RendererUploadContext`, joins the asset layer to the queue.

```mermaid caption="The path of one upload. The managers plan a step, and the queue writes it into staging and records the copy. The batch goes to the GPU, and a fence tells when staging and ticket are done." alt="A flow of boxes from left to right. Asset bytes enter a planned step. The step is written into staging memory, a copy is recorded, and the staging is released. The batch is then sent to the graphics processing unit with a fence. When the fence completes, the staging becomes idle and the ticket is complete."
flowchart LR
    A[Asset bytes on the CPU] --> B[Plan a step<br/>bytes and time left]
    B --> C[Write the step into staging]
    C --> D[Record the copy<br/>release the staging]
    D --> E[Send the batch to the GPU<br/>set a fence]
    E --> F[Fence done:<br/>staging idle, ticket complete]
    F -.-> B
```

Follow the arrows with one texture. The manager calls the queue with a wish: say, the rest of a 64 MiB level. The queue answers with a **step**: one bounded piece of an upload, planned so that the bytes and time fit what is left of the frame. The queue takes a staging buffer from the pool, writes the step into it, and records a copy from the buffer into the texture. Then it gives the buffer back to the pool.

Many steps from one frame travel together in a **batch**, which the queue sends to the GPU in one submission and closes with a fence, an :term[event query]{id=fence} that the CPU can poll. A batch also gets a number.

That number is the **ticket**: it names the uploads recorded so far, and it is complete once the GPU has run every copy recorded before it. An asset that needs its last step holds the ticket and asks `IsComplete` in later frames. It never waits for it inside a frame.

Files in `Strata/src/Strata/Renderer/` hold the parts: `GPUUploadQueue.h` and `GPUUploadQueue.cpp` the queue, `StagingPool.h` and `StagingPool.cpp` the pool, `RendererUploadContext.h` the join to the asset layer, and `Renderer.cpp` the frame start and `PrepareBackBuffer`.

## The contract

Callers of the queue and the pool may assume four things, and must do three.

- A step never exceeds the bytes and time its call was given, except for the first step of the frame. That step gets at least one granule, the smallest piece an upload may be cut into (defined below). Reason: the budget bounds the cost of a frame, and a frame that uploads nothing can never finish a load.
- Staging is returned to the pool after the copies that read it are recorded. The pool then holds it until the GPU has run those copies. Reason: writing a buffer that the GPU still reads corrupts the texture.
- A ticket is complete once the GPU has run every copy recorded before it. Completion is polled and never waited for in a frame.
- Nothing renders into the :term[back buffer]{id=back-buffer} before `Renderer::PrepareBackBuffer` ran in that frame. Reason: the first work on the image may wait for the display.

The duties follow. The :term[command lists]{id=command-list} that copy from released staging must be executed before `SubmitBatch` closes the batch or the next `BeginFrame` starts. A step that finds no room in staging must wait for a later frame, not block. All of the queue and the pool run on the main thread only.

:::rule
Copy commands that read released staging must run before `SubmitBatch` or the next `BeginFrame`. Rendering into the back buffer starts with a call of `Renderer::PrepareBackBuffer()`. The first rule keeps a fence from covering copies that were never sent, and the second keeps the display wait out of the :term[work time]{id=work-time}. See [resources and lifetimes](resources-lifetimes.md) for the event queries these rules lean on.
:::

## A toy version: a ring with one fence per frame

The smallest working design is a ring of staging slots with one fence per frame. A frame takes a free slot, copies into it and marks it with its frame number. A slot becomes free again when the GPU has finished that frame.

:::question
Which C++ is new here? The toy uses classes, `std::vector`, loops and function calls; they are taught on [programming 3](../basics/programming-3.md) and [programming 2](../basics/programming-2.md).
:::

The sketch below simulates a GPU that finishes each frame three frames after the CPU recorded it. A ring of two slots copies 4 MiB per frame until 20 MiB are done. Look at the frames where no slot is free: the program prints that nothing was copied and tries again, as the real queue does.

```cpp sketch="gpu-upload-queue-toy.cpp"
#include <cstdint>
#include <cstdio>
#include <vector>

// A ring of staging slots. A slot is free again once the GPU finished the frame whose copies read it.
struct Slot
{
	int64_t FenceFrame = -1; // The frame whose copies read the slot
	bool InFlight = false;
};

class StagingRing
{
public:
	explicit StagingRing(size_t slotCount)
		: m_Slots(slotCount)
	{
	}

	// Polled once per frame: frees every slot whose frame the GPU has finished.
	void BeginFrame(int64_t completedFrame)
	{
		for (Slot& slot : m_Slots)
			if (slot.InFlight && slot.FenceFrame <= completedFrame)
				slot.InFlight = false;
	}

	// Takes a free slot for this frame's copy, or fails: the caller waits for a later frame instead of blocking.
	bool Acquire(int64_t frame)
	{
		for (Slot& slot : m_Slots)
		{
			if (!slot.InFlight)
			{
				slot.InFlight = true;
				slot.FenceFrame = frame;
				return true;
			}
		}
		return false;
	}

private:
	std::vector<Slot> m_Slots;
};

int main()
{
	constexpr uint64_t c_SlotBytes = 4ull << 20;
	constexpr int64_t c_GPULag = 3; // The GPU finishes a frame this many frames after the CPU recorded it
	StagingRing ring(2);
	uint64_t remaining = 20ull << 20;

	for (int64_t frame = 0; remaining > 0; frame++)
	{
		ring.BeginFrame(frame - c_GPULag);
		const uint64_t step = remaining < c_SlotBytes ? remaining : c_SlotBytes;
		if (ring.Acquire(frame))
		{
			remaining -= step;
			std::printf("frame %lld: copied %llu KiB, %llu KiB left\n", static_cast<long long>(frame),
				static_cast<unsigned long long>(step >> 10), static_cast<unsigned long long>(remaining >> 10));
		}
		else
		{
			std::printf("frame %lld: no free slot, nothing copied\n", static_cast<long long>(frame));
		}
	}
	return 0;
}
```

```text output-of="gpu-upload-queue-toy.cpp"
frame 0: copied 4096 KiB, 16384 KiB left
frame 1: copied 4096 KiB, 12288 KiB left
frame 2: no free slot, nothing copied
frame 3: copied 4096 KiB, 8192 KiB left
frame 4: copied 4096 KiB, 4096 KiB left
frame 5: no free slot, nothing copied
frame 6: copied 4096 KiB, 0 KiB left
```

1. **Line 8:** the frame whose copies read the slot, which is the fence: one number per frame.
2. **Lines 21–25:** the poll at the start of a frame frees every slot whose frame the GPU finished.
3. **Lines 29–40:** acquiring never blocks; with no free slot it returns false, and the caller tries again in a later frame.
4. **Line 50:** the simulated GPU lag, in frames.
5. **Line 56:** the newest frame the GPU has finished is the current frame minus the lag.

The output shows the whole idea. Frames 0 and 1 take both slots. Frame 2 finds none free, because the GPU has not finished frame 0 yet, so the upload waits and the frame still runs. Frame 3 sees frame 0 completed and takes its slot again. The upload took seven frames, and no frame blocked.

Strata's pool differs in three ways. Its buffers have different sizes, so it keeps them by size; its fence covers a batch, not a frame; and its steps are sized by time, which the toy ignores.

## The real code

### Staging buffers: sizes, release and idle limits

The **staging pool** is the `StagingPool` object that hands out staging buffers and takes them back to be written again once the GPU has run the copies that read them. Its design note in `StagingPool.h` states the rules; here they are with their reasons.

Buffers come in powers of two from 64 KiB. A request for 100,000 bytes gets a buffer of 131,072 bytes, and one for 70,000 bytes gets the same buffer. Uploads of similar size therefore share buffers, at the price of unused space: the exercises show a waste of up to nearly half.

A released buffer cannot be written again at once. The pool holds it until an event query tells that the GPU has run the copies. The asset managers set that query as soon as they have executed the frame's uploads, through `SubmitBatch`, and the GPU runs a frame's uploads ahead of the frame's rendering. So when the GPU keeps pace, a buffer released in one frame is free to write in the next. A query set only at the next `BeginFrame` would also wait for the frame's rendering, which delays the buffer by two frames and halves what the budget can move per frame.

Memory must not grow with the biggest burst ever seen. The pool keeps idle buffers up to 16 MiB. When nothing was acquired for 120 frames, it frees all of them. A steady stream of uploads therefore allocates nothing, and a quiet game gives its staging back.

Budgeted uploads also bound the whole pool. They wait while the buffers in flight leave no room, and `AcquireBuffer` frees idle buffers of other sizes before it makes one that would put the pool over its limit. The driver keeps the memory of freed buffers for a while, so the process pays for the high-water mark of staging; idle staging must not come on top of the budget. Uploads that ignore the budget, such as loads that block, are bounded another way.

The pool keeps at most 256 MiB of released staging that waits for the GPU. It frees the rest when the GPU is done.

### Writing staging memory

Staging memory is write-combined: the CPU gathers its writes into bursts, which makes writing fast and reading it back slow. The queue never reads it. Where the writing happens matters, because the main thread waits for the step either way.

A step that writes 512 KiB or more into staging the pool already had spreads its copies over the worker threads of the job system in pieces of 256 KiB. On the reference machine, the computer on which Strata measures its budgets, 4 MiB took 0.4 to 1.2 ms on one thread and 0.15 to 0.3 ms spread.

New staging is written by the main thread alone. The system gives each of its pages, blocks of a few KiB, real memory only at the first write. It handles those page faults one at a time, and spread over workers the same 4 MiB took 2.5 to 4.3 ms. So the code asks `RunCopies` to spread only when `created` is false.

```cpp src="Strata/src/Strata/Renderer/GPUUploadQueue.cpp#L519-L539" symbol="GPUUploadQueue::RunCopies"
void GPUUploadQueue::RunCopies(bool spread)
{
	if (!spread || m_CopyBytes < c_ParallelCopyBytes || m_Copies.size() < 2)
	{
		for (const CopyRun& copy : m_Copies)
			std::memcpy(copy.Destination, copy.Source, copy.Bytes);
	}
	else
	{
		// Batches of about a piece's bytes (runs of short rows go together).
		const size_t averageBytes = std::max<size_t>(m_CopyBytes / m_Copies.size(), 1);
		const uint32_t runsPerBatch = static_cast<uint32_t>(std::max<size_t>(c_CopyPieceBytes / averageBytes, 1));
		JobSystem::ParallelFor(static_cast<uint32_t>(m_Copies.size()), runsPerBatch, [this](uint32_t begin, uint32_t end)
		{
			for (uint32_t index = begin; index < end; index++)
				std::memcpy(m_Copies[index].Destination, m_Copies[index].Source, m_Copies[index].Bytes);
		});
	}
	m_Copies.clear();
	m_CopyBytes = 0;
}
```

1. **Line 521:** small steps, staging newly created, or a single run stay on the calling thread.
2. **Lines 529–530:** the runs go to workers in batches of about one piece, and runs of short rows go together.
3. **Line 531:** the parallel loop returns only when every run is written, because the main thread needs the step done.
4. **Lines 537–538:** the lists are cleared for the next step.

### Planning a step

The queue sizes each step to what is left of the frame. A **granule** is the smallest piece into which a step may cut an upload: a row of blocks of a texture, or a small level. Cutting between granules never splits a row.

:::example[Planning one call by hand]
Suppose a frame may spend 2 ms on uploads, with no deadline, and the pool holds idle staging of every size the call needs. The measured speed is the starting 4 million bytes per millisecond. The call wants 64 MiB with granules of 64 KiB (65,536 bytes).

The queue keeps a tenth of the frame's time in reserve for steps that run slower than planned, so 0.2 ms goes unused and 1.8 ms remain. At the speed, 1.8 times 4,000,000 is 7,200,000 bytes, but no step exceeds 4 MiB, which is 4,194,304 bytes, about a millisecond of writing. The first step is 4,194,304 bytes and costs about 1.05 ms.

The second step has 2 - 1.05 - 0.2, about 0.75 ms left. That buys 3,005,600 bytes, and rounding down to whole granules gives 45 times 65,536, or 2,949,120 bytes. It costs about 0.74 ms. A third step finds about 0.015 ms and plans zero bytes, so the call stops. Only the first step of a frame is exempt: it takes one granule even when no time is left.

Each frame therefore moves 7,143,424 bytes, and the 64 MiB texture needs ten frames, about 167 ms at 60 frames per second, with no frame over its budget. The single write of 16.8 ms becomes ten frames of about 1.8 ms.
:::

The code below does the same arithmetic. Search for the three limits (bytes, time and deadline), the rounding to granules and the second plan for fresh staging.

```cpp src="Strata/src/Strata/Renderer/GPUUploadQueue.cpp#L228-L277" symbol="GPUUploadQueue::PlanStep"
uint64_t GPUUploadQueue::PlanStep(const AssetFinalizeContext& context, uint64_t callBytes, float callMs, uint64_t wantedBytes, uint64_t granuleBytes) const
{
	if (wantedBytes == 0)
		return 0;
	const uint64_t granule = std::clamp<uint64_t>(granuleBytes, 1, wantedBytes);
	uint64_t limit = std::min(wantedBytes, c_MaxStepBytes);
	limit = std::min(limit, context.UploadBudget > callBytes ? context.UploadBudget - callBytes : 0);

	// What is left of the call's upload time less the frame's reserve, and of the time until the deadline less its share, at
	// the speed of the latest steps.
	double milliseconds = std::numeric_limits<double>::infinity();
	if (std::isfinite(context.UploadMsBudget))
	{
		const float frameBudget = std::isfinite(context.UploadMsFrameBudget) ? context.UploadMsFrameBudget : context.UploadMsBudget;
		const double reserve = (1.0 - c_PlannedTimeShare) * static_cast<double>(std::max(frameBudget, 0.0f));
		milliseconds = static_cast<double>(context.UploadMsBudget) - static_cast<double>(callMs) - reserve;
	}
	if (context.Deadline != std::chrono::steady_clock::time_point::max())
	{
		const auto now = std::chrono::steady_clock::now();
		const double untilDeadline = context.Deadline > now ? std::chrono::duration<double, std::milli>(context.Deadline - now).count() : 0.0;
		milliseconds = std::min(milliseconds, untilDeadline * c_PlannedTimeShare);
	}
	const bool framesFirst = IsFramesFirstStep(context, callBytes);
	const auto finish = [&](uint64_t bytes)
	{
		if (bytes >= wantedBytes)
			return wantedBytes; // All of it fits
		bytes -= bytes % granule;
		if (bytes == 0 && framesFirst)
			bytes = granule; // Every frame makes progress
		return bytes;
	};
	if (!std::isfinite(milliseconds))
		return finish(limit);

	const auto byTime = [&](double available, float bytesPerMs)
	{
		const double bytes = std::max(0.0, available) * static_cast<double>(bytesPerMs);
		return bytes < static_cast<double>(limit) ? static_cast<uint64_t>(bytes) : limit;
	};
	const uint64_t step = finish(byTime(milliseconds, m_Stats.BytesPerMs));
	// The staging the step would take (callers take what is wanted when it all fits, else a power of two of bytes): where
	// the pool has none idle, the step creates it first and then writes fresh memory. The creation takes at most half the
	// time left, so such steps still make progress (and staging of their size comes about) where creating staging is slow.
	if (step == 0 || m_Staging.HasIdleBuffer(step >= wantedBytes ? wantedBytes : std::bit_floor(step)))
		return step;
	const double creationMs = std::min(static_cast<double>(m_Stats.StagingCreateMs), milliseconds * 0.5);
	return finish(byTime(milliseconds - creationMs, m_Stats.ColdBytesPerMs));
}
```

1. **Lines 233–234:** the byte limits: what is wanted, 4 MiB, and what is left of the call's bytes.
2. **Lines 242–243:** the time left is the call's time less the reserve, a tenth of the frame's time.
3. **Lines 256–258:** the step rounds down to whole granules, and the frame's first step takes one granule at least.
4. **Line 269:** the bytes the time buys, at the measured speed.
5. **Lines 273–276:** where the pool has no idle staging of the step's size, the step must create it, so the code subtracts that time and plans with the slower speed of fresh memory.

Two more points differ from the hand example. A load may also carry a deadline, the moment by which its work should end. That gives a second limit: nine tenths of the time until it, so a planned step never counts the last tenth. And creating staging costs at most half of the time left, so such steps still make progress, and staging of their size comes into being even where creating it is slow.

:::why[Why steps keep a reserve]
A step's speed strays from the measured average by a tenth and more, because the frame's other work takes memory speed and fresh pages fault. Steps planned to fill the budget to its end went over it as often as not: frames that filled their 2 ms took up to 2.18 ms. The reserve is a share of the frame's time, not of what is left, because steps that each used a share of what was left still added up to the budget's end. The price is a little unused time in every frame.
:::

### One texture step, in order

The speed in the plan is not fixed. `UploadTexture` is the call that makes a step real, and it ends by measuring itself.

1. `UploadTexture` lays out the regions one after the other in one staging buffer, each at a multiple of 16 bytes, and adds up the size.
2. The call acquires that much staging from the pool, within the context's staging budget, and maps it. When no staging can be had, it records nothing and says so.
3. The call collects one write per region, runs them (`RunCopies`, above) and releases the mapping.
4. The call records the copies from the buffer into the texture, and keeps the texture alive until the batch has completed.
5. The call releases the staging to the pool for its queue, and adds the step's bytes and time to the call's totals and to the frame's statistics.

The last part of step 5 closes the loop. Each step's bytes, divided by its writing time without the acquire, are mixed into the measured speed with a weight of 0.2 against 0.8 for the old value. Steps under 16 KiB or 0.01 ms say nothing about speed and are ignored. The queue keeps two speeds, one for staging the pool had and one for staging made for the step, so the plan for each case uses the right one.

### Batches, tickets and scene data

Steps are recorded into the command lists of the open batch. `SubmitBatch` closes them, executes them, fences the staging they released and sets one event query per queue. The submission waits in a queue of its own with its ticket and the textures its copies wrote. NVRHI's command lists do not keep the destinations of copies from buffers alive, so the batch does.

```cpp src="Strata/src/Strata/Renderer/GPUUploadQueue.cpp#L185-L189" from="m_GraphicsList->close();" to="m_Staging.FenceReleased(nvrhi::CommandQueue::Graphics);" symbol="GPUUploadQueue::SubmitBatch"
m_GraphicsList->close();
m_Device->executeCommandList(m_GraphicsList);
// The staging these uploads copy from becomes reusable as soon as the GPU has run them, usually by the next frame's
// finalization: the GPU runs them ahead of the frame's rendering.
m_Staging.FenceReleased(nvrhi::CommandQueue::Graphics);
```

The order matters. `FenceReleased` comes only after `executeCommandList`, so its query is set behind the copies. Called earlier, it could complete before the copies ran, and the pool would hand out staging the GPU still reads. That is the rule of the contract, in code.

Tickets complete in order. `CollectCompleted` polls the oldest submission first, and a ticket is complete when it is at most the newest completed one. Nothing blocks, except `WaitForTicket`, which exists for loads that must finish at once.

```cpp src="Strata/src/Strata/Renderer/GPUUploadQueue.cpp#L602-L615" symbol="GPUUploadQueue::CollectCompleted"
void GPUUploadQueue::CollectCompleted()
{
	while (!m_Submissions.empty())
	{
		Submission& submission = m_Submissions.front();
		if (!m_Device->pollEventQuery(submission.Graphics) || (submission.Transfer && !m_Device->pollEventQuery(submission.Transfer)))
			break;
		m_CompletedTicket = submission.Ticket;
		m_IdleQueries.push_back(std::move(submission.Graphics));
		if (submission.Transfer)
			m_IdleQueries.push_back(std::move(submission.Transfer));
		m_Submissions.pop_front();
	}
}
```

1. **Line 604:** the loop starts with the oldest submission.
2. **Lines 606–608:** both queries are polled, never waited for, and the loop stops at the first batch that is not done.
3. **Line 609:** the ticket becomes the completed one; submissions finish in order, so every older ticket is complete too.
4. **Lines 610–613:** the finished queries are kept to be used again and the submission leaves the queue.

Two other uses of the queue appear in its statistics. The render scenes' own data, such as instances and joints, goes through `RecordSceneUpload` in steps of at most 16 MiB of staging, outside the asset budget, because every frame's drawing reads it. And `CopyTextureLevels` copies mip levels from one texture into another on the GPU, with no staging at all. The queue counts bytes, time and steps for the frame and the previous frame, the measured speeds, and the number of batches, so tests and the profiler can read them.

### The transfer queue

Many GPUs have a **transfer queue**: a hardware queue meant for copies, which runs beside the graphics queue. The queue can send the uploads that managers may wait for there, so copying overlaps drawing. Strata builds this, behind `SetTransferQueue`, and leaves it off.

The reason is a measurement. On the reference machine the exported stress game did not load faster with it: every texture was resident from frame 10 or 11 with it and from frame 10 without, in five runs each. It also held more memory meanwhile, a peak of 595 to 622 MB against 582 to 595 MB. Each upload is handed over to the graphics queue a frame after its last copy, so its data lives that much longer.

A **queue ownership transfer** is the :term[Vulkan]{id=vulkan} rule that a resource written by one :term[queue family]{id=queue-family} belongs to it until that family releases it and the other acquires it, and Strata's hand-over follows it. `ReleaseToGraphics` records the release after the last copy and returns a ticket. When that ticket is complete, `AcquireOnGraphics` records the acquire on the graphics queue, which may then use the texture. While it waits, an asset that finishes loading answers `AwaitingGPU`. The batch also gives NVRHI's tracking back the resources' states before its list closes, because the transfer queue cannot make the transitions into :term[shader]{id=shader} states.

### Copies into textures, and the layer seam

NVRHI makes copies from buffers into textures only from staging textures, which would rarely be used again. So `GraphicsDevice::RecordBufferToTextureCopies` records such copies for the queue. The destination levels become copy destinations first through the state tracking; the sources stay copy sources, and regions in staging start at multiples of 16 bytes so that every texel block size divides the offset.

The asset layer must not include NVRHI or the renderer: the [layer table](../core/layers-registries.md) forbids it. Two classes cross the seam. `AssetUploadContext` is an interface of the asset layer that begins and submits batches, and `RendererUploadContext` implements it with the queue's batches; its `EndFrame` also frees idle staging when uploads stopped for 120 manager updates. `IAssetGraphics` is an engine service that the renderer module registers, and the managers ask it for the context, the :term[frames in flight]{id=frames-in-flight} and the memory budget. With no renderer, it returns none, and GPU assets keep their data on the CPU.

### The frame's start and `PrepareBackBuffer`

`Renderer::BeginFrame` rolls staging and the queue forward: it tells the pool the new frame index, which makes finished staging idle and fences what was released, and it lets the queue collect completed batches. The order of its calls belongs to [the device page](vulkan-nvrhi.md).

Then comes the first work on the back buffer. On some drivers the image is handed out only at its first use, so the first work on it waits for the display. Strata does not want that wait to stand before the uploads, so `PrepareBackBuffer` is called late. The first code that renders into the back buffer calls it, or the end of the frame when nothing drew. It runs once per frame and clears the image black, so a frame that draws nothing still shows a defined picture.

```cpp src="Strata/src/Strata/Renderer/Renderer.cpp#L310-L331" symbol="Renderer::PrepareBackBuffer"
nvrhi::ITexture* Renderer::PrepareBackBuffer()
{
	if (!s_Data)
		return nullptr;
	if (s_Data->BackBufferPrepared)
		return s_Data->Device->GetBackBuffer();
	s_Data->BackBufferPrepared = true;
	// The first work on the image waits for the display where the driver hands the image out only at its first use
	// (MoltenVK waits for its drawable in the submission below): a wait, not work, like presenting.
	ST_PROFILE_STAGE("Present");
	if (!s_Data->Device->PrepareBackBuffer())
		return nullptr;
	nvrhi::ITexture* backBuffer = s_Data->Device->GetBackBuffer();
	if (backBuffer)
	{
		s_Data->FrameCommandList->open();
		s_Data->FrameCommandList->clearTextureFloat(backBuffer, nvrhi::AllSubresources, nvrhi::Color(0.0f, 0.0f, 0.0f, 1.0f));
		s_Data->FrameCommandList->close();
		s_Data->Device->GetDevice()->executeCommandList(s_Data->FrameCommandList);
	}
	return backBuffer;
}
```

1. **Lines 314–316:** only the first call of a frame does the work; later calls return the image.
2. **Line 319:** the wait is timed as the `Present` stage.
3. **Line 320:** the device's acquire wait, where the driver needs it.
4. **Lines 325–328:** the image is cleared black and the command list runs at once.

The wait is timed as the `Present` stage of the frame profiler. It is a CPU stage outside the work time and not a GPU stage, because the CPU waits and the GPU does nothing for it; [the profiling page](../core/profiling.md) lists the stages. The sending of the uploads comes earlier in the frame, so the wait costs them nothing.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| A new staging buffer for every upload | Simple renderers and small tools | No pool to maintain | Driver allocation on every upload, and memory that follows no bound |
| Ring of slots with one fence per frame (the toy) | Renderers with fixed-size uploads | Simpler code and no sizing by power of two | Wasted room for large steps, and a slot is free again only after a whole frame |
| NVRHI's `writeBuffer` for all data | Code that uploads small, changing data | Almost no upload code | No budget, no pool and a stall on big data |
| Transfer queue always on | Engines on hardware with a dedicated copy engine | Copies that overlap drawing | Memory and a one-frame hand-over for no measured gain here |
| Byte budget per frame, without timing | Engines with fixed frame costs | A simpler planner | A budget that fits one machine and misses the others |

## How it is tested

The suites `GPU.UploadQueue` and `GPU.Assets.Uploads` carry the `gpu` label: they need a graphics device. `GPU.UploadQueue` checks that uploads run on the graphics queue unless the transfer queue was asked for. It checks that a batch that records nothing submits nothing, and that no frame passes its byte budget on either queue. It also checks that a 90 MB texture spreads over frames and is ready only once its last level is complete. Its test of `PlanStep` checks that steps follow the bytes and time left and that a frame's first step takes one granule at least.

`GPU.Assets.Uploads` checks the pool. Staging must come back once the GPU has run the copies fenced with it, and buffers must come in powers of two with one of a size kept. New staging must first free idle staging so the pool stays within its limit, and textures must upload smallest level first in runs of rows. Run a suite directly with `build/windows/bin/Debug/StrataTests.exe --test-suite=GPU.UploadQueue`, or all GPU tests with `ctest --preset windows-debug -L gpu`. Each GPU test ends by checking that the device logged no new error.

## Changing it safely

Extension points are few. A new kind of upload calls `PlanStep` for its size, `UploadBuffer` or `UploadTexture` for its copy, and keeps its ticket; it never calls the pool directly. A new user of staging that skips the queue must still release the staging after recording its copies and execute those command lists before the next fence.

Rules to keep, with reasons:

- Scene data goes through `RecordSceneUpload`, never `writeBuffer`: the pool and its limits stay the only source of staging.
- Never block a frame on a load. Check `IsComplete` and skip or use a fallback.
- Hold ticket numbers, not buffers. A buffer released to the pool is no longer yours.
- Call `Renderer::PrepareBackBuffer()` before rendering into the back buffer, so the display wait is counted as `Present`, not as work.
- A change to the planner needs a check of the budget tests: a step that runs over its budget appears as a long frame, not as a failure.

Before a commit, run `GPU.UploadQueue` and `GPU.Assets.Uploads`, and the perf tests when the change can alter what a frame spends.

## Summary

- A texture reaches device-local memory through a staging buffer, and the copy is split into budgeted steps so no frame stalls.
- A step is the smallest of the wanted bytes, 4 MiB, the bytes left and what the time left buys at the measured speed, rounded down to granules. The first step of a frame always gets one granule.
- Staging is released after its copies are recorded, held until a fence behind the executed copies completes, and then written again; the rule is to execute those lists before `SubmitBatch` or the next `BeginFrame`.
- `PrepareBackBuffer` runs once per frame, waits for the display where the driver needs it, clears the image black, and its wait is the CPU stage `Present`.
- To trace an upload, watch `PlanStep` calls in a frame and the frame in which its ticket completes.

## Check yourself

1. Why does a game not write the pixels of a texture directly into the memory the GPU samples from?
   - A. The GPU cannot read main memory at all.
   - B. The CPU cannot write to device-local memory, so a staging buffer and a copy are needed.
   - C. Staging buffers make textures smaller.

   :::answer{tests="staging-need"}
   B. The GPU can read memory that the CPU writes (A is wrong) but more slowly, and staging does not change the texture's size (C is wrong). The fast copy goes through a buffer the CPU can write.
   :::

2. A call may spend 1 ms and has spent 0.4 ms, and the frame budget is 1 ms. The speed is 4,000,000 bytes per millisecond and the granule is 64 KiB. The pool has idle staging of the right size. How many bytes may the next step take, at most? Ignore the byte limits.

   :::answer{tests="step-size"}
   Time left is 1 - 0.4 - 0.1 = 0.5 ms, which buys 2,000,000 bytes. Whole granules of 65,536 bytes: 30 granules is 1,966,080 bytes, and 31 would be 2,031,616, over the time. The step is 1,966,080 bytes.
   :::

3. Staging is released, and its copy command list is executed after the fence is set. What goes wrong, and which rule is broken?

   :::answer{tests="staging-reuse"}
   The fence can complete before the copies ran, so the pool may hand out the buffer and the CPU writes over it while the GPU still reads it. The rule: execute the command lists that copy from released staging before `SubmitBatch` or the next `BeginFrame`.
   :::

4. Where does the time of the display wait appear, and why is it not GPU time?
   - A. As a GPU stage, because the GPU finishes the frame.
   - B. As the CPU stage `Present`, outside the work time, because the CPU waits and the GPU does nothing for it.
   - C. Inside the upload statistics.

   :::answer{tests="back-buffer"}
   B. The wait happens in `PrepareBackBuffer` on the CPU. No GPU pass runs for it (A is wrong), and uploads count only their own steps (C is wrong).
   :::

5. In the toy, the ring has three slots and the GPU lag is three frames. In which frames does a copy happen for a 20 MiB texture?

   :::answer{tests="staging-reuse"}
   Frames 0 to 4. Frames 0 to 2 take the three slots. Frame 3 sees frame 0 completed and takes its slot again, and frame 4 takes the second. Five steps of 4 MiB finish the 20 MiB, and no frame waits.
   :::

6. A trace of a 64 MiB load shows `PlanStep` returning 4,194,304 on the first call of a frame and 2,949,120 on the second. What do the two values tell you about the frame's budget?

   :::answer{tests="trace-plan"}
   The first step hit the 4 MiB limit, so time was plentiful. The second was cut by the time left, which means the frame's upload time is nearly spent: the call stops after it or at the next call.
   :::

## Exercises

1. **Basic.** A call may spend 0.8 ms and has spent nothing, no deadline applies, the frame budget is 0.8 ms and the granule is 64 KiB. The speed is 4 million bytes per millisecond, and 2 million for fresh staging, which costs 0.5 ms to create. The call wants 64 MiB. Compute the step when idle staging of its size exists, and when none does.

   :::answer[Worked solution]{tests="step-size"}
   The reserve is 0.08 ms, so 0.72 ms remain. With idle staging: 0.72 times 4,000,000 is 2,880,000 bytes, rounded down to granules, 43 times 65,536 is 2,818,048 bytes. Without it, the step is 2,818,048 and rounds down to a 2 MiB buffer, which the pool lacks. Creation takes the smaller of 0.5 and half of 0.72, so 0.36 ms. That leaves 0.36 ms at 2,000,000 bytes per millisecond, or 720,000 bytes, and 10 granules is 655,360 bytes.
   :::

2. **Medium.** Write a function that gives the staging buffer size for a request, from 64 KiB in powers of two, and print the share of the buffer left unused for a request of 20,000,000 bytes.

   :::answer[Worked solution]{tests="staging-need" solution="sketches/gpu-upload-queue-sizes.cpp"}
   The size is the larger of the smallest size and the next power of two at or above the request.

   ```cpp sketch="gpu-upload-queue-sizes.cpp"
   #include <algorithm>
   #include <bit>
   #include <cstdint>
   #include <cstdio>

   // Staging buffers come in powers of two, from a smallest size on, so buffers of similar uploads are reused.
   constexpr uint64_t c_MinBufferBytes = 64ull << 10;

   uint64_t GetBufferByteSize(uint64_t bytes)
   {
   	return std::max(c_MinBufferBytes, std::bit_ceil(bytes));
   }

   int main()
   {
   	const uint64_t requests[] = { 1, 65536, 65537, 100000, 4194304, 20000000 };
   	for (const uint64_t bytes : requests)
   	{
   		const uint64_t size = GetBufferByteSize(bytes);
   		const double waste = 100.0 * static_cast<double>(size - bytes) / static_cast<double>(size);
   		std::printf("%llu bytes -> buffer of %llu bytes, %.1f %% unused\n", static_cast<unsigned long long>(bytes),
   			static_cast<unsigned long long>(size), waste);
   	}
   	return 0;
   }
   ```

   ```text output-of="gpu-upload-queue-sizes.cpp"
   1 bytes -> buffer of 65536 bytes, 100.0 % unused
   65536 bytes -> buffer of 65536 bytes, 0.0 % unused
   65537 bytes -> buffer of 131072 bytes, 50.0 % unused
   100000 bytes -> buffer of 131072 bytes, 23.7 % unused
   4194304 bytes -> buffer of 4194304 bytes, 0.0 % unused
   20000000 bytes -> buffer of 33554432 bytes, 40.4 % unused
   ```

   1. **Line 11:** the next power of two at or above the request, but never below the smallest size.
   2. **Line 16:** the last request is the one of the exercise.
   3. **Line 20:** the unused share is the buffer's size less the request, over the buffer's size.
   :::

3. **Hard.** Trace it yourself: find, with a debugger, how one large texture uploads on a build of the engine. Set a breakpoint in `PlanStep`, load the texture, and note on each call the step's bytes, the measured speed and the time left. Name the frame in which its ticket completes.

   :::answer[Worked solution]{tests="trace-plan"}
   Break in `GPUUploadQueue::PlanStep` in `Strata/src/Strata/Renderer/GPUUploadQueue.cpp`. Read `callBytes`, `callMs` and `m_Stats.BytesPerMs` on each stop and the returned step. Early frames show steps of 4 MiB, shrinking in a frame's later calls. Set a watch on `m_CompletedTicket` in `CollectCompleted`: the frame where it reaches the ticket of the last step is the frame the texture is ready.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Renderer/GPUUploadQueue.h` and `GPUUploadQueue.cpp`: `PlanStep`, `SubmitBatch`, tickets, `RunCopies`.
- `Strata/src/Strata/Renderer/StagingPool.h` and `StagingPool.cpp`: the pool, `c_MaxIdleBytes`, `c_IdleReleaseFrames`.
- `Strata/src/Strata/Renderer/RendererUploadContext.h`: `RendererUploadContext` and `RendererAssetGraphics`.
- `Strata/src/Strata/Asset/AssetUploadContext.h`: `AssetUploadContext` and `IAssetGraphics`.
- `Strata/src/Strata/Renderer/Renderer.cpp`: `Renderer::BeginFrame` and `Renderer::PrepareBackBuffer`.
- Tests: `StrataTests/src/Renderer/GPUUploadQueueTests.cpp` and `GPUAssetUploadTests.cpp`.
- Setting: `RendererSpecification::TransferQueueUploads`, off by default.

## Further reading

- The Vulkan specification, chapter on resource sharing between queue families (registry.khronos.org): the rules of ownership transfer; advanced.
- Documentation of NVRHI in its repository (github.com): staging resources and command lists; intermediate.
