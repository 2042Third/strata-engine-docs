---
id: gpu/resources-lifetimes
title: "Resources and lifetimes"
description: "How Strata keeps every graphics resource alive while the graphics card may still use it, and in the right state, without waiting in a frame."
kind: internals
size: L
tracks: [E]
needs: [gpu/vulkan-nvrhi, gpu/compute, gpu/first-triangle]
time: 80
learn:
  - id: tracked-barriers
    text: explain when NVRHI places a barrier by itself and when a pass must place one
  - id: clear-exception
    text: explain why a render target that a frame only cleared needs a deferred release
  - id: queue-trace
    text: trace a released resource through pending, completed and destroyed
  - id: destroy-budget
    text: compute how many frames a destruction budget needs to free a set of textures
  - id: version-pacing
    text: compute when the owner of a volatile constant buffer must wait for the graphics card
since: 0.3.0
status: final
---

Your game window changes size. The :term[renderer]{id=renderer} must drop every image it drew into and make new ones of the new size. But the :term[graphics processing unit]{id=gpu} (GPU) runs behind the processor: when your code asks to drop an image, the GPU may still be drawing into it. This page covers the code that keeps each resource alive until the GPU is done with it, puts it in the right state for each use, and never makes a frame wait for either. It does not cover how data reaches the GPU or how memory for geometry is sliced: those are other pages.

## The problem and how engines solve it

A frame is not finished when your code stops recording it. The central processing unit (CPU) records commands, submits them, and moves on to the next frame, while the GPU works through the queue some milliseconds behind. At 60 :term[frames per second]{id=frame-rate} a frame lasts 16.7 ms, and the GPU may be one to three frames late. Two problems follow from that gap.

The first problem is lifetime. Suppose frame 41 draws into an image called `Depth`, and you submit it. You then change the window's size, and your code drops `Depth` and makes a bigger one. If the driver frees the memory of `Depth` at once, frame 41 writes into memory that no longer belongs to it. The best case is an error message from the :term[validation layer]{id=validation-layer}; the worst is a lost device.

The second problem is state. A GPU keeps images in different layouts, and its caches hold data that other units of the chip cannot see yet. An image you draw into must change its layout before a :term[shader]{id=shader} reads it, and the change must wait for the writes to finish. The command that does this is a barrier: it makes earlier work on a resource finish, so that its data is visible to later work. It may also change the layout of the resource.

The label that graphics software gives a layout is the resource state: `RenderTarget`, `ShaderResource`, `UnorderedAccess` and so on.

Take a worked case. A pass draws the scene into `HDR`. The next pass, tone mapping, reads `HDR` as a texture. Between them a barrier changes `HDR` from the render target state to the shader resource state.

Omit it and tone mapping may read stale data, or read it in a layout the hardware cannot sample. Add one that nothing needs and the GPU waits for no reason. A frame holds dozens of such transitions. A missing one appears as flicker on one vendor's card and not on another's.

### Three ways to handle states

Engines meet the state problem in one of three ways. The first is to write every barrier by hand. This costs the least at run time and the most in programmer time, because every pass must know which state its inputs were left in by whoever ran before it.

The second is to track states in the library. The library remembers the state of each resource as commands are recorded, and when a pass uses a resource in a new way it inserts the barrier. :term[NVRHI]{id=nvrhi}, the library Strata renders through, does this. The price is that the library sees only what you tell it: it guesses wrong in the corner cases below, and you place a barrier yourself there.

The third is a render graph. Each pass declares what it reads and writes, the engine sorts the passes, and the graph computes all barriers (and the lifetime of temporary images) before any command is recorded. It finds the best barriers and can share memory between temporary images, but it asks the whole renderer to be written in that shape. Strata has no render graph: its passes are plain functions that record into a :term[command list]{id=command-list}, and NVRHI tracks the states.

### Three ways to handle lifetimes

Reference counting is the base. NVRHI resources are objects with a count: each handle you hold adds one, and the resource is destroyed when the last handle goes. A command list that you record also holds a handle to what it uses, until the GPU finishes that list. So most resources need no extra care.

For what the list does not hold, engines keep a release queue. The oldest approach is by frame: put the resource in the bucket of the current frame, and free the bucket when the frame is a fixed number of frames old. It is simple, but it assumes the :term[frame loop]{id=game-loop} advances, and it frees too late when the GPU is fast and too early when the GPU falls behind.

The other approach is to fence the release. When a resource is released, the queue asks the GPU to raise a flag after the last work submitted so far. The queue frees the resource once the flag is up. This costs one flag per batch and works with any submission pattern.

Strata does this, and the flag is an :term[event query]{id=fence}: an object that the GPU sets when all earlier work on a queue is complete, which the CPU asks about without waiting. Every lifetime system in Strata uses this one signal. You poll it: ask, and if the answer is no, continue and ask again next frame. Waiting for it inside a frame makes the CPU idle until the GPU catches up, which appears as a hitch.

The rest of the page covers how Strata does the fenced queue, called **deferred release**: holding a resource until the GPU has finished the work submitted before the release, and only then destroying it. Staging memory for uploads has its own fences, covered in [the upload queue](upload-queue.md).

## The map

The diagram follows one released image. Everything on it runs on the :term[main thread]{id=main-thread}. Only the :term[event query]{id=fence} is set by the GPU.

```mermaid caption="A released resource waits in a pending batch until the graphics card finishes the work submitted before it, moves to the completed list, and is destroyed within a time budget in a later frame." alt="A flow from dropped handles, through a release call that makes a batch and an event query, to pending batches, completed resources and destruction."
flowchart LR
  A["Owner drops handles"] --> B["Release: batch plus event query"]
  B --> C["Pending batches, oldest first"]
  G["GPU sets the query after earlier work"] -.-> C
  C -->|"poll says done"| D["Completed list"]
  D -->|"each frame, within 0.25 ms"| E["Destroyed"]
```

Four files own the pieces. `Strata/src/Strata/Renderer/DeferredReleaseQueue.h` and `Strata/src/Strata/Renderer/DeferredReleaseQueue.cpp` hold the queue. `Strata/src/Strata/Renderer/Renderer.cpp` owns the one queue of the program, reached through `Renderer::ReleaseDeferred`, and drains it once per frame in `Renderer::BeginFrame`. `Strata/src/Strata/Renderer/SceneRenderer.cpp` is the main caller: it drops its render targets through the queue, and it paces its own volatile constant buffer with event queries. Automatic barriers belong to NVRHI, in the NVRHI :term[submodule]{id=submodule} under `Strata/vendor`, so no Strata file holds them.

## The contract

The first rules say what you can count on. NVRHI counts references, so a handle you copy keeps the resource alive. A command list keeps alive what it references until the GPU completes the list. NVRHI tracks the state of each resource while you record, and it places the barrier when a binding set changes: that is, when a pass binds a texture it last saw in another state. You rarely write a barrier.

The same contract has holes, and Strata's seven rules mark them. Each has a reason.

1. **Never take the address of a handle.** Writing `&m_Pipeline` calls `RefCountPtr::operator&`, which releases the reference and returns the address of the raw pointer. Assign through that address and the object has no owner and dangles.
2. **Place barriers by hand in a chain of writes through one binding set.** NVRHI places barriers when the binding set changes, not between two dispatches through the same set. If dispatch two reads what dispatch one wrote, call `setBufferState` or `setTextureState` with `UnorderedAccess`, then `commitBarriers()`. The compute model is in [Compute shaders](compute.md).
3. **Hand render targets to `Renderer::ReleaseDeferred`.** NVRHI's :term[Vulkan]{id=vulkan} backend keeps no reference to what a clear or a resolve writes. If a frame in flight only cleared a target, the owner frees memory that the GPU still writes.
4. **Budget destruction.** Destroying a texture costs the driver about 0.1 ms. Strata frees at most 0.25 ms worth of completed resources in a frame, or twenty thumbnails dropped in one frame stall it for 2.1 to 2.3 ms.
5. **Move a compute-written texture out of its undefined layout whole.** A texture that compute passes write level by level, in the frame it was made, first gets `setTextureState` on `AllSubresources` with `UnorderedAccess`, and `commitBarriers()`. Per-level barriers can land after levels were written, which on one NVIDIA card lost the data.
6. **Make a list non-immediate if it may open while another list is open.** With one immediate list open, the validation layer of NVRHI rejects the opening of another. Recording into the list that did not open does nothing. Create such lists with `setEnableImmediateExecution(false)`.
7. **Expect a fixed count of versions in a volatile constant buffer.** The owner of one that renders back to back must pace its writes. It must also poll its event query after waiting on it.

A **constant buffer** is a small block of read-only values that every thread of a draw's shaders can read, such as the camera matrices; [Binding resources](binding.md) covers it.

A **volatile constant buffer** is a constant buffer that NVRHI rewrites by keeping several versions. Every write goes to a fresh version, and the GPU may read an older one until it finishes the command list that wrote that version. The reason for versions is that the CPU writes the buffer every frame while the GPU may still read last frame's values.

:::rule[Drop render targets through the deferred release]
`AGENTS.md` lists the traps of NVRHI among its architecture rules: never take a handle's address, place barriers by hand for chains of writes through one binding set, and drop render targets through `Renderer::ReleaseDeferred`. The reason is rule 3 above: a validation error on a good day, a lost device on a bad one. The barrier rule is explained in [Compute shaders](compute.md).
:::

### What the clears exception means

Rule 3 is the surprising one, so look at it in a frame. A view in which nothing is drawn still has an image of entity identifiers, one number per pixel. That image is only cleared: one `clearTextureUInt` and no draw. The command list that did the clear holds no reference that NVRHI's Vulkan backend counts. When the owner drops its last handle, the texture is destroyed, though the GPU has not run the clear yet.

The same happens to a depth image that is only cleared, and to the source of a resolve. Rule 3 is therefore not about every resource: it is about every resource that a submitted list may use without NVRHI knowing. The safe habit is to hand over every render target.

## A toy version

The toy models the idea with a pretend GPU that counts frames. The queue stores each released batch with a fence, the number of frames submitted when it was released. It moves a batch to the completed list once the GPU has finished that many frames, and destroys completed resources oldest first until a budget of 250 microseconds is spent, at 100 microseconds each. The class uses :term[constructors]{id=constructor}, `std::deque` and `std::move`: read the question first.

:::question
Not sure what a class, a pointer or `std::move` means? Read [C++ classes](../basics/cpp-classes.md) and [modern C++](../basics/cpp-modern.md) first.
:::

The program submits three frames, releases eight textures, then runs six more frames in which the GPU finishes one frame each. Search for the frame where the first destruction happens, and for how many fall in each frame.

```cpp sketch="gpu-resources-lifetimes-toy.cpp"
#include <algorithm>
#include <cstdio>
#include <deque>
#include <string>
#include <utility>
#include <vector>

// A pretend GPU: it counts the frames it was given and the frames it finished.
struct FakeGpu
{
	int Submitted = 0;
	int Finished = 0;

	void SubmitFrame() { Submitted++; }
	void Finish(int frames) { Finished = std::min(Finished + frames, Submitted); }
	bool HasReached(int fence) const { return Finished >= fence; }
};

class DeletionQueue
{
public:
	explicit DeletionQueue(const FakeGpu& gpu)
		: m_Gpu(gpu)
	{
	}

	// The fence is the number of frames submitted so far: every frame that may use the resources is below it.
	void Release(std::vector<std::string> names)
	{
		m_Pending.push_back({ std::move(names), m_Gpu.Submitted });
	}

	// Destroys completed resources, oldest first, until the budget is spent. Returns how many it destroyed.
	int Collect(int budgetMicroseconds)
	{
		while (!m_Pending.empty() && m_Gpu.HasReached(m_Pending.front().Fence))
		{
			for (std::string& name : m_Pending.front().Names)
				m_Completed.push_back(std::move(name));
			m_Pending.pop_front();
		}

		int spent = 0;
		int destroyed = 0;
		while (!m_Completed.empty())
		{
			m_Completed.pop_front();
			destroyed++;
			spent += 100; // A texture costs about 100 microseconds to destroy.
			if (spent >= budgetMicroseconds)
				break;
		}
		return destroyed;
	}

	size_t GetHeldCount() const
	{
		size_t held = m_Completed.size();
		for (const Batch& batch : m_Pending)
			held += batch.Names.size();
		return held;
	}

private:
	struct Batch
	{
		std::vector<std::string> Names;
		int Fence;
	};

	const FakeGpu& m_Gpu;
	std::deque<Batch> m_Pending;
	std::deque<std::string> m_Completed;
};

int main()
{
	FakeGpu gpu;
	DeletionQueue queue(gpu);

	for (int frame = 0; frame < 3; frame++)
		gpu.SubmitFrame();
	queue.Release({ "t0", "t1", "t2", "t3", "t4", "t5", "t6", "t7" });

	for (int round = 1; round <= 6; round++)
	{
		gpu.SubmitFrame();
		gpu.Finish(1);
		const int destroyed = queue.Collect(250);
		std::printf("frame %d: gpu finished %d of %d, destroyed %d, held %zu\n", round, gpu.Finished, gpu.Submitted, destroyed, queue.GetHeldCount());
	}
	return 0;
}
```

```text output-of="gpu-resources-lifetimes-toy.cpp"
frame 1: gpu finished 1 of 4, destroyed 0, held 8
frame 2: gpu finished 2 of 5, destroyed 0, held 8
frame 3: gpu finished 3 of 6, destroyed 3, held 5
frame 4: gpu finished 4 of 7, destroyed 3, held 2
frame 5: gpu finished 5 of 8, destroyed 2, held 0
frame 6: gpu finished 6 of 9, destroyed 0, held 0
```

1. **Lines 27–30:** the fence is the count of frames submitted at the moment of release.
2. **Lines 36–41:** a batch becomes completed only when the GPU has reached its fence, and batches leave in order.
3. **Lines 45–52:** the budget loop: destroy one, add its cost, stop once the budget is spent.

Nothing is destroyed until the GPU has finished frame 3, the last frame that could use the textures: the fence is 3, and the first collection that sees `Finished` at 3 runs in round 3. Then the budget decides. Each destruction adds 100, and the loop stops after the one that reaches 250, so a round destroys three. Eight textures take three rounds. The held count falls by the destroyed count, never faster, and the queue never asked the GPU anything it had to wait for.

:::example[Twenty thumbnails]
A thumbnail cache lets go of 20 thumbnails in one frame, each a texture. Destroying one costs about 0.1 ms, so freeing them all at once is 20 times 0.1 ms, that is 2.0 ms; the engine measured 2.1 to 2.3 ms. At 60 frames per second a frame has 16.7 ms, so that single frame spends about 13 percent of itself on destruction.

With the 0.25 ms budget, a frame destroys resources one at a time and stops after the destruction that reaches the budget: 0.1, 0.2, 0.3 ms. That is three per frame, 0.3 ms at most. Twenty textures take 7 frames: six frames of three, then one of two. A hundred would take 34 frames and cost the same 0.3 ms in each. The editor spends a little every frame instead of a lot once.
:::

## The real code

The real queue differs from the toy in four ways. It fences with event queries instead of a frame counter. It keeps every query it creates to use again. It works without frames, because tools and tests render without a frame loop. And it measures its budget with a clock, not a count.

Start with its design comment, which holds the contract in words.

```cpp src="Strata/src/Strata/Renderer/DeferredReleaseQueue.h#L16-L30"
// Keeps GPU resources alive until the GPU has finished the work submitted before they were released, without waiting
// for it. NVRHI keeps what a command list references alive until the list completes, but its Vulkan backend does not
// reference the textures of clears (clearTextureFloat, clearTextureUInt, clearDepthStencilTexture) and resolves: a
// render target that a submitted command list only cleared (the entity IDs of a view in which nothing is drawn) would
// be destroyed, and its memory freed, while the GPU still writes it. That is a validation error, and freed memory
// in use can lose the device. Owners that drop render targets while their frames may be in flight (SceneRenderer when
// it is resized) hand them over here instead, through Renderer::ReleaseDeferred.
//
// Completion is tracked with event queries on the graphics queue, where everything renders, so releases do not
// depend on frames advancing (tools and tests render without them). Main thread only.
//
// Dropping the last reference destroys the resource, which costs the driver about 0.1 ms for a texture: a frame that
// dropped every completed resource at once held the editor 2.1-2.3 ms for the 20 thumbnails a cache let go of, and
// would hold it for tens of milliseconds for hundreds. Frames destroy within a time budget (Collect's), the rest in the
// frames after.
```

1. **Lines 16–17:** the job: hold resources until the GPU has finished what was submitted before the release.
2. **Lines 18–21:** the clears exception, with the example of an entity image of a view in which nothing is drawn.
3. **Lines 24–25:** the queue tracks completion with event queries on the graphics queue, so it does not need frames.
4. **Lines 27–30:** why destruction is budgeted: the numbers of the thumbnail case.

`Release` takes a list of handles. It runs in the order below, and the first part has no match in the toy.

```cpp src="Strata/src/Strata/Renderer/DeferredReleaseQueue.cpp#L14-L24"
void DeferredReleaseQueue::Release(std::vector<nvrhi::ResourceHandle> resources)
{
	std::erase_if(resources, [](const nvrhi::ResourceHandle& resource) { return !resource; });
	if (resources.empty())
		return;

	// As many resources as the caller hands over, the oldest done on the GPU, are destroyed now: the queue stays bounded
	// by the GPU's progress when no frames run, and a release costs what dropping its own resources at once would.
	TakeCompleted();
	for (size_t index = 0; index < resources.size() && !m_Completed.empty(); index++)
		m_Completed.pop_front();
```

1. **Line 16:** empty handles are dropped first, so a release of nothing leaves no batch.
2. **Lines 20–24:** a release destroys as many completed resources as it takes over, oldest first, so a program that never runs a frame still stays bounded by the GPU's progress.

The `for` loop on line 23 costs about what dropping the new resources at once would have cost, so a caller never pays more than it handed over. The queue gets a query from `m_IdleQueries`, a pool of finished ones, or creates one, then does the key step.

```cpp src="Strata/src/Strata/Renderer/DeferredReleaseQueue.cpp#L36-L48"
	if (!completion)
	{
		// Completion cannot be observed without a query: wait for the GPU instead, then drop the resources.
		ST_CORE_ERROR("DeferredReleaseQueue: failed to create an event query; waiting for the GPU to release {} resources", resources.size());
		m_Device->waitForIdle();
		return;
	}
	// The query completes with the last command list executed so far, after every one that may use the resources.
	m_Device->resetEventQuery(completion);
	m_Device->setEventQuery(completion, nvrhi::CommandQueue::Graphics);
	m_PendingCount += resources.size();
	m_Pending.push_back(Batch { std::move(resources), std::move(completion) });
}
```

1. **Lines 36–42:** if the device cannot create a query, the queue cannot tell when the GPU is done. It logs an error, waits for the GPU to go idle, and drops the resources by returning. This is the one wait in the file, and it is a failure path.
2. **Lines 43–45:** `resetEventQuery` clears a recycled query, and `setEventQuery` places it after the last command list executed so far. That is why the caller must hand resources over after executing the lists that use them.
3. **Line 47:** the batch joins the back of `m_Pending`, with its query.

`Collect` runs once a frame, from `Renderer::BeginFrame`, with `c_FrameDestroyBudget`, 250 microseconds. It first moves finished batches to `m_Completed` through `TakeCompleted`, then destroys.

```cpp src="Strata/src/Strata/Renderer/DeferredReleaseQueue.cpp#L50-L76"
void DeferredReleaseQueue::Collect(std::optional<std::chrono::nanoseconds> budget)
{
	TakeCompleted();

	// Dropping the queue's reference destroys what nothing else holds.
	const auto start = std::chrono::steady_clock::now();
	while (!m_Completed.empty())
	{
		m_Completed.pop_front();
		if (budget && std::chrono::steady_clock::now() - start >= *budget)
			break;
	}
}

void DeferredReleaseQueue::TakeCompleted()
{
	// Queries complete in submission order, so the first pending batch decides whether any later one can be done.
	while (!m_Pending.empty() && m_Device->pollEventQuery(m_Pending.front().Completion))
	{
		Batch batch = std::move(m_Pending.front());
		m_Pending.pop_front();
		m_PendingCount -= batch.Resources.size();
		for (nvrhi::ResourceHandle& resource : batch.Resources)
			m_Completed.push_back(std::move(resource));
		m_IdleQueries.push_back(std::move(batch.Completion));
	}
}
```

1. **Line 52:** it never waits: `TakeCompleted` only polls.
2. **Lines 56–61:** a destruction is a `pop_front`, which drops the queue's reference. The budget check comes after it, so every call destroys at least one resource and the queue always drains, even with a budget of zero.
3. **Lines 66–67:** queries complete in submission order, so when the oldest batch is not done, no later one can be, and the loop stops at the first no.
4. **Lines 69–74:** a finished batch moves its resources to `m_Completed` in order, and its query returns to the pool for the next release.

The toy and the real queue agree on the order of events: fence at release, poll, move, destroy with a budget. The differences are all about being safe in places where the toy's pretend GPU hides the problem. For instance, `GetPendingCount()` counts what the GPU may still use plus what waits to be destroyed, and tests rely on it.

### How the renderer uses it

`SceneRenderer` is the main caller. When its viewport changes, `SetViewportSize` calls `ReleaseRenderTargets`, directly or through `CreateRenderTargets`. This function collects every handle into one list and drops the owner's reference as it goes.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L2305-L2320"
void SceneRenderer::ReleaseRenderTargets()
{
	// Submitted frames may still use the targets. NVRHI keeps alive what their command lists reference, but not the
	// textures they only cleared (in a view where nothing is drawn, the entity IDs are only cleared): the deferred
	// release keeps everything until the GPU is done with it.
	std::vector<nvrhi::ResourceHandle> released;
	auto release = [&released](auto& handle)
	{
		if (handle)
			released.emplace_back(handle.Get());
		handle = nullptr;
	};
	release(m_DepthTexture);
	release(m_NormalTexture);
	release(m_EntityIDTexture);
	ReleaseGlobalIllumination(released);
```

1. **Lines 2307–2309:** the comment is the clears exception, applied: the entity identifiers of a view where nothing is drawn are only cleared.
2. **Lines 2311–2316:** the :term[lambda]{id=lambda} copies the handle into `released`, then sets the member to `nullptr`. The queue holds the only reference once the function returns.
3. **Lines 2317–2320:** the first three targets, then a helper for the global illumination targets; many more follow, including frame buffer objects, which reference textures.

Frame buffer objects, binding sets and the shadow atlas go the same way. The last line of the function, line 2400, is `Renderer::ReleaseDeferred(std::move(released))`. That call is where `Release` runs: the batch is stamped with an event query after the last command list the renderer has executed, which includes any frame that still draws into the targets. A few frames later, `Collect` destroys them.

### Pacing the volatile constant buffer

The other lifetime in `SceneRenderer` is the version of its volatile `FrameConstants` buffer. `c_FrameConstantVersions` is 16, and a frame writes it at most `c_MaxFrameConstantWrites` times, which is 2: the frame's constants, and under temporal anti-aliasing the overlays' copy without jitter. A write that finds no free version is an NVRHI error.

A program's frame loop keeps the CPU from running far ahead (`GraphicsDevice::BeginFrame`). A test or tool that renders back to back has no such loop, so the renderer paces itself. `ExecuteFrame` runs the list, then sets one event query after it and records how many writes the frame made.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L1542-L1562"
void SceneRenderer::ExecuteFrame(nvrhi::ICommandList* commandList)
{
	m_Device->executeCommandList(commandList);
	if (m_FrameConstantWrites == 0)
		return;
	nvrhi::EventQueryHandle done;
	if (!m_FreeFrameConstantQueries.empty())
	{
		done = std::move(m_FreeFrameConstantQueries.back());
		m_FreeFrameConstantQueries.pop_back();
		m_Device->resetEventQuery(done);
	}
	else
	{
		done = m_Device->createEventQuery();
	}
	m_Device->setEventQuery(done, nvrhi::CommandQueue::Graphics);
	m_SubmittedFrameConstants.push_back({ std::move(done), m_FrameConstantWrites });
	m_SubmittedFrameConstantWrites += m_FrameConstantWrites;
	m_FrameConstantWrites = 0;
}
```

1. **Line 1544:** the list executes first, so the query lands after the writes.
2. **Lines 1545–1546:** a frame that wrote nothing has no versions to release and gets no query.
3. **Lines 1558–1560:** the query is placed on the graphics queue and stored with the frame's write count, which the total of outstanding writes adds up.

Before the next frame writes, `ReserveFrameConstantVersions` frees the versions of finished frames, and waits only if the coming writes could find none free.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L1515-L1533"
void SceneRenderer::ReserveFrameConstantVersions()
{
	ST_PROFILE_FUNCTION();
	// Frames the GPU finished release their versions; while the frame could still need more than are free, the renderer
	// waits for its oldest frame (only callers that outrun the GPU by about 8 frames get there).
	while (!m_SubmittedFrameConstants.empty() && m_Device->pollEventQuery(m_SubmittedFrameConstants.front().Done))
		ReleaseOldestFrameConstants();
	while (!m_SubmittedFrameConstants.empty() && m_SubmittedFrameConstantWrites + c_MaxFrameConstantWrites > c_FrameConstantVersions)
	{
		// The poll after the wait matters: NVRHI's Vulkan wait leaves behind the queue's completion value that the buffer's
		// versions are checked against, and a poll brings it up to date.
		nvrhi::IEventQuery* oldest = m_SubmittedFrameConstants.front().Done;
		m_Device->waitEventQuery(oldest);
		m_Device->pollEventQuery(oldest);
		ReleaseOldestFrameConstants();
	}
	m_FrameConstantWrites = 0;
	m_TonemapConstantsWritten = false;
}
```

1. **Lines 1520–1521:** polling frees every finished frame's versions without waiting.
2. **Lines 1522–1523:** the wait happens only if the outstanding writes plus a full frame's maximum would exceed 16.
3. **Lines 1527–1528:** the wait is followed by a poll. NVRHI's Vulkan wait leaves the queue's completion value stale, and the versions are checked against that value, so a poll updates it.

:::example[When does the renderer wait?]
Each frame writes 2 times. The renderer waits when outstanding writes plus 2 would exceed 16, that is, with 15 or more outstanding. After seven submitted frames 14 writes are outstanding, and 14 plus 2 is 16, which does not exceed 16, so no wait. After the eighth frame, 16 are outstanding, and the next reserve waits for the oldest frame. A caller must therefore run ahead of the GPU by about 8 frames before it waits at all.

If a frame wrote once, the same rule waits at 15 submitted frames. A frame loop that allows three :term[frames in flight]{id=frames-in-flight} never gets near it. This one place is where the renderer waits in a frame, and it is a safety net, not the normal path.
:::

Note the tension with the rule "never wait in a frame". The deferred queue never waits except on a failed query. The constants pacing waits, but only when the alternative is an error and only for callers that skip the frame loop. The design keeps the wait out of the path that real programs run.

## Barriers in practice

The state rules do not live in one file; they appear where a pass touches a resource. Two cases carry the contract. Rule 2 applies to a pass that dispatches twice through one binding set. If the second dispatch reads what the first wrote, the pass must call `setBufferState` or `setTextureState` with `UnorderedAccess`, then `commitBarriers()`, between them. NVRHI places its automatic barrier only when the binding set changes.

For rule 5, `SceneRenderer::CreateEnvironmentTexture` makes one state call after it creates the texture, shown here with the engine's own comment.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L751-L759"
nvrhi::TextureHandle texture = m_Device->createTexture(desc);
ST_CORE_VERIFY(texture, "SceneRenderer: failed to create the {} cubemap", name);
// The new texture leaves its undefined layout whole, before any level is written. Left to the passes, each level would
// leave it in a barrier of its own that waits for nothing (there is nothing to wait for in a new texture), recorded
// between the writes of the other levels; on the RTX 5090 (driver 617.42) such a barrier could land after levels
// already written and lose them: the atmosphere's first environment kept a black prefiltered map (its levels 0 to 3)
// whenever the long multiple-scattering pass ran before it in the frame, so mirrors and rough metals reflected
// nothing until the sun moved.
commandList->setTextureState(texture, nvrhi::AllSubresources, nvrhi::ResourceStates::UnorderedAccess);
```

The comment above it says why: a barrier per level waited for nothing in a new texture and could be recorded between the writes of other levels. On one NVIDIA card it landed after levels already written, and a prefiltered map came out black. The cure is to take the texture out of its undefined layout once, whole, before any level is written, so that no later barrier has to. The line is the "whole texture first" rule in a single call.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Hand-written barriers | Applications written directly on Vulkan | The cheapest barriers, and no tracking cost per command | Every pass must know the state its inputs were left in; a missing barrier shows on one vendor only |
| Render graph | Some large commercial engines (see Further reading) | Barriers computed once for the whole frame, and :term[shared memory]{id=shared-memory} for temporary images | A rewrite of all passes into declared reads and writes; harder passes that tools add |
| Release queue by frame number | Many engines | No query objects, and a single counter | Needs a frame loop; tools and tests that render without frames would not free anything |
| Wait for idle before destroying | Strata itself, on the failure path of the queue | No queue at all | A stall of the whole GPU in the middle of the editor at every size change |
| Reference counting only | Code that trusts the library | No release call | The clears exception: freed memory in use |

The sources of the first three rows are in Further reading. The fourth row is what the queue does when it cannot create a query, which shows its price: a hitch.

## How it is tested

The suite `GPU.Renderer.DeferredRelease` in `StrataTests/src/Renderer/GPUDeferredReleaseTests.cpp` has five tests. Each starts from the shared device (`Tests::GPUContext`) and ends with a check that no new validation errors appeared.

- Released resources stay alive until the GPU has finished: a cleared texture is released, the queue shows one pending, and after `WaitForIdle` and `Collect` none.
- Releases are collected in order, also without frames: each release destroys as many completed resources as it takes over, so the counts stay at two pending and one completed over four rounds.
- A collection within a budget destroys the completed resources over several calls: with a budget of zero nanoseconds, one reference drops per call, and the test checks which textures lost theirs by their counts.
- A frame destroys within its budget: 512 objects that each take 20 microseconds to destroy are released, and one frame frees at most the budget divided by 20 microseconds plus one.
- The renderer drops releases the frame after the GPU finishes them.

The pacing has one test in `StrataTests/src/Renderer/GPUSceneRendererTests.cpp`, in the suite `GPU.SceneRenderer`: 48 frames rendered back to back at 2048 by 2048 with ambient occlusion, bloom, reflections and temporal anti-aliasing, then a check of zero errors. Without the pacing, NVRHI reports an error for each write that finds no version. CTest runs every GPU suite as one test, `StrataTests.GPU`: run it with `ctest --preset windows-debug -R StrataTests.GPU`, or one suite with `StrataTests.exe --test-suite=GPU.Renderer.DeferredRelease`. They need a GPU and carry the label `gpu`.

## Changing it safely

A new owner of render targets calls `Renderer::ReleaseDeferred` with everything that references the old targets: images, frame buffer objects and binding sets. Hand the resources over after executing the command lists that use them, because the query is set after the last list executed so far.

Three habits keep changes safe. Do not wait for the GPU in a frame: poll event queries, and where a wait is the lesser evil, as in the constants pacing, poll again after it. Do not add a destroy path that bypasses the budget, because the 20-thumbnail stall comes back. And when you add a pass that writes a texture through compute in the frame it was made, place the whole-texture barrier first. Before you merge, run the suite above plus `GPU.SceneRenderer*` with the validation layer, and check that the count of new errors stays at zero.

The reasons sit in the rules: render targets through `ReleaseDeferred` (the clears exception), budgeted destruction (0.1 ms per texture), explicit barriers for same-set chains (NVRHI sees binding set changes only).

## What went wrong before

Before the budget, the queue destroyed everything whose work had completed in one call. A thumbnail cache let go of 20 thumbnails in one frame, and that frame took 2.1 to 2.3 ms longer, visible as a hitch in the editor. The fix added `c_FrameDestroyBudget` and made `Collect` stop when the budget is spent. The regression test is the fourth test above: with textures that take a fixed time to destroy, one frame frees only what the budget holds.

## Summary

- NVRHI places a barrier when a binding set changes; you place one for a chain of writes through one set and for a compute-written texture's first layout change.
- A command list keeps alive what it references, but not textures it only cleared or resolved, so render targets go to `Renderer::ReleaseDeferred`.
- A released resource waits in a batch fenced by an event query, moves to the completed list in order, and is destroyed within 0.25 ms per frame.
- The budget bounds a frame's destruction: 20 textures at 0.1 ms each take 7 frames at 3 per frame.
- A volatile constant buffer has 16 versions; the renderer waits for the oldest frame only when the next frame's writes might find none, and polls after the wait.

## Check yourself

1. A submitted frame only clears the entity identifier image of a view in which nothing is drawn, and the owner then sets its handle to `nullptr`. What goes wrong? (a) Nothing: the list keeps the image alive; (b) the image may be freed while the GPU still clears it; (c) the next frame draws black; (d) the count goes below zero.

   :::answer{tests="clear-exception"}
   (b). NVRHI's Vulkan backend does not reference textures that a list only clears, so the last handle's destruction frees memory in use. (a) is the mistake the page warns about: the list keeps alive only what it references that way. (c) and (d) are not what happens: the harm is a validation error or a lost device.
   :::

2. Eight textures are released while 3 frames are submitted, at 0.1 ms per destruction and a 0.25 ms budget. The GPU has finished 3 frames. How many does the first collection destroy, and how many frames in all does the queue need?

   :::answer{tests="destroy-budget,queue-trace"}
   Three, because the loop stops after the destruction that reaches 0.25 ms (0.1, 0.2, 0.3). It needs 3 frames: 3, 3 and 2. The fence of 3 is reached once the GPU has finished frame 3, so the first collection with that state destroys. The toy's output shows the same.
   :::

3. A renderer writes its volatile buffer 3 times per frame and the buffer has 16 versions. After how many submitted frames does the check "outstanding plus 3 exceeds 16" first hold?

   :::answer{tests="version-pacing"}
   After 5 frames: 15 outstanding, and 15 plus 3 is 18, more than 16. After 4 frames it is 12 plus 3, which is 15, so no wait yet.
   :::

4. Two compute dispatches use one binding set; the second reads what the first wrote through the same texture. Who places the barrier, and why?

   :::answer{tests="tracked-barriers"}
   The pass places it, with `setTextureState` for `UnorderedAccess` and `commitBarriers()`. NVRHI places automatic barriers when the binding set changes, and here it does not, so it sees nothing to do.
   :::

5. In `Collect`, why does the destruction loop check the budget after `pop_front` and not before?

   :::answer{tests="destroy-budget"}
   So each call destroys at least one resource. If the check came first, a budget that is already spent would destroy none and the queue would never drain.
   :::

## Exercises

1. **Basic.** A cache lets go of 50 textures at once. Using the page's numbers (0.1 ms each, 0.25 ms budget), how many frames does the queue need, and what is the most one frame spends?

   :::answer[Worked solution]{tests="destroy-budget"}
   A frame destroys 3 (0.1, 0.2, 0.3 ms, stopping after the one that reaches 0.25). Fifty divided by 3 is 16 full frames (48) and a last frame of 2, so 17 frames. The most one frame spends is 0.3 ms. Without the budget, the same frame would spend 5 ms.
   :::

2. **Medium.** In a scratch build, write a GPU test that creates a 64 by 64 render target, only clears it in a command list, executes the list without waiting, then drops the handle with `nullptr`. Write a second version that hands the handle to `Renderer::ReleaseDeferred`. Predict the count of new validation errors in each.

   :::answer[Worked solution]{tests="clear-exception"}
   Model the test on `GPU.Renderer.DeferredRelease` in `StrataTests/src/Renderer/GPUDeferredReleaseTests.cpp`: create the texture with the render target flag, record `clearTextureUInt`, execute, then drop it. With `nullptr` the image is destroyed while the clear may still run, so expect a validation error from the layer, as the engine's own comment says. A fast GPU may finish first and hide it, so repeat the loop. With `ReleaseDeferred` the queue holds the reference until the event query completes, and `gpu.GetNewErrorCount()` stays at zero. Do not commit the first version.
   :::

3. **Medium.** Trace it yourself: find where one render target of `SceneRenderer` is destroyed after the window changes size.

   :::answer[Worked solution]{tests="queue-trace"}
   Start at `SceneRenderer::SetViewportSize` in `Strata/src/Strata/Renderer/SceneRenderer.cpp`, which calls `CreateRenderTargets` and so `ReleaseRenderTargets`. That function ends with `Renderer::ReleaseDeferred` (line 2400), defined in `Strata/src/Strata/Renderer/Renderer.cpp`, which calls `DeferredReleaseQueue::Release` in `DeferredReleaseQueue.cpp`. The destruction itself is the `pop_front` in `DeferredReleaseQueue::Collect`, reached from `Renderer::BeginFrame`, frames later. A breakpoint in `Release` and one in `Collect` shows the gap.
   :::

4. **Hard.** The engine's `Release` also destroys as many completed resources as it takes over. Take the toy, remove `Collect` from its use, and add that rule. Run a tool that releases two resources after each of 8 frames and print the held count.

   :::answer[Worked solution]{tests="queue-trace,destroy-budget" solution="sketches/gpu-resources-lifetimes-bounded.cpp"}
   `Release` first moves completed batches to the completed list, then pops as many as the new batch holds. The GPU finishes one frame per step, so the batch of the previous step is complete and the pop removes exactly its two names. The program below runs the tool and prints the held count.

   ```cpp sketch="gpu-resources-lifetimes-bounded.cpp"
   #include <algorithm>
   #include <cstdio>
   #include <deque>
   #include <string>
   #include <utility>
   #include <vector>

   struct FakeGpu
   {
   	int Submitted = 0;
   	int Finished = 0;

   	void SubmitFrame() { Submitted++; }
   	void Finish(int frames) { Finished = std::min(Finished + frames, Submitted); }
   	bool HasReached(int fence) const { return Finished >= fence; }
   };

   class DeletionQueue
   {
   public:
   	explicit DeletionQueue(const FakeGpu& gpu)
   		: m_Gpu(gpu)
   	{
   	}

   	// Like the engine's queue, a release also destroys as many completed resources as it takes over.
   	void Release(std::vector<std::string> names)
   	{
   		MoveCompleted();
   		for (size_t index = 0; index < names.size() && !m_Completed.empty(); index++)
   			m_Completed.pop_front();
   		m_Pending.push_back({ std::move(names), m_Gpu.Submitted });
   	}

   	size_t GetHeldCount() const
   	{
   		size_t held = m_Completed.size();
   		for (const Batch& batch : m_Pending)
   			held += batch.Names.size();
   		return held;
   	}

   private:
   	struct Batch
   	{
   		std::vector<std::string> Names;
   		int Fence;
   	};

   	void MoveCompleted()
   	{
   		while (!m_Pending.empty() && m_Gpu.HasReached(m_Pending.front().Fence))
   		{
   			for (std::string& name : m_Pending.front().Names)
   				m_Completed.push_back(std::move(name));
   			m_Pending.pop_front();
   		}
   	}

   	const FakeGpu& m_Gpu;
   	std::deque<Batch> m_Pending;
   	std::deque<std::string> m_Completed;
   };

   int main()
   {
   	FakeGpu gpu;
   	DeletionQueue queue(gpu);

   	// A tool that renders without a frame loop: it releases two resources after every submitted frame and never calls Collect.
   	for (int step = 1; step <= 8; step++)
   	{
   		gpu.SubmitFrame();
   		gpu.Finish(1);
   		queue.Release({ "a", "b" });
   		std::printf("step %d: held %zu\n", step, queue.GetHeldCount());
   	}
   	return 0;
   }
   ```

   ```text output-of="gpu-resources-lifetimes-bounded.cpp"
   step 1: held 2
   step 2: held 2
   step 3: held 2
   step 4: held 2
   step 5: held 2
   step 6: held 2
   step 7: held 2
   step 8: held 2
   ```

   1. **Line 26:** the comment names the rule that the toy lacked.
   2. **Lines 29–31:** the release moves completed batches, then destroys as many names as the new batch holds.

   The held count stays at 2. Without the pop loop it would grow by 2 each step, to 16.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Renderer/DeferredReleaseQueue.h` and `Strata/src/Strata/Renderer/DeferredReleaseQueue.cpp`: the queue, `c_FrameDestroyBudget`, `GetPendingCount`.
- `Strata/src/Strata/Renderer/Renderer.cpp`: `Renderer::ReleaseDeferred`, `Renderer::GetDeferredReleases`, and the per-frame `Collect` in `Renderer::BeginFrame`.
- `Strata/src/Strata/Renderer/SceneRenderer.cpp`: `ReleaseRenderTargets`, `ReserveFrameConstantVersions`, `ExecuteFrame`, `CreateEnvironmentTexture`.
- `Strata/src/Strata/Renderer/SceneRenderer.h`: `c_FrameConstantVersions` and `c_MaxFrameConstantWrites`.
- `StrataTests/src/Renderer/GPUDeferredReleaseTests.cpp`: the suite `GPU.Renderer.DeferredRelease`.

## Further reading

- Yuriy O'Donnell, "FrameGraph: Extensible Rendering Architecture in Frostbite" (GDC 2017): the render graph idea; intermediate.
- The Vulkan specification, the chapters on synchronization and on object lifetime: what a barrier guarantees and when destruction is valid; advanced.
- The NVRHI repository readme and its header `nvrhi.h`: resource states, command lists and event queries; intermediate.
