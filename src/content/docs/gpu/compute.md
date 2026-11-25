---
id: gpu/compute
title: "Compute shaders: dispatches, thread groups, shared memory and atomics"
description: "How a graphics processing unit counts and sorts data without drawing: dispatches, thread groups, shared memory, atomics and barriers."
kind: concept
size: M
tracks: [E]
needs: [gpu/shaders]
time: 45
learn:
  - id: dispatch-size
    text: compute the group counts of a dispatch that covers an image
  - id: shared-histogram
    text: explain why a group counts into shared memory before it adds to global memory
  - id: barrier-place
    text: find where a barrier is needed between a write and a read
  - id: scan-ranges
    text: compute the output ranges that a prefix sum gives to counted items
since: 0.3.0
status: final
---

Your game shows a bright desert and then a dark cave. To show detail in both, the engine must know how bright the picture is. A good way is a histogram: 256 boxes, each counting the pixels of one brightness. A 1920 by 1080 picture has 2,073,600 pixels, and the count must be ready every frame, about every 16.7 ms.

A :term[graphics processing unit]{id=gpu} (GPU) can do this work, because it runs thousands of small programs at once. But the obvious way to write the count is slow, and the reasons teach most of what this page covers. This page starts with that slow way, builds a fast one, and then uses the same tools for a second problem: giving each item of a list its own place in an output array.

## Counting into one address makes every thread wait

Here is the obvious plan. Start one **thread**, a single copy of your small program, for each pixel. Each thread reads its pixel, finds the box for its brightness, and adds one to that box in memory.

Two threads that add to the same box at the same moment cause a problem. Each reads the old count, adds one, and writes the result. If both read 7, both write 8, and one pixel is lost. That failure is a race, the one that threads on the :term[central processing unit]{id=processor} (CPU) also have ([Threads](../basics/threads.md)).

The fix is an :term[atomic operation]{id=atomic-operation}. An **atomic operation** reads, changes and writes a memory cell as one step that no other thread can split. With atomics the count is right: two threads that both add one to a box holding 7 leave 9.

The cost is waiting. A desert is mostly one brightness, so most of the 2,073,600 threads want the same few boxes. The memory system lets one atomic at a time work on one address. The others queue, and the GPU, which relies on thousands of threads running together, runs them one after another.

:::question
What if each thread had its own copy of the boxes? That works, but 2 million copies of 256 counters take 2 GB of memory, and adding them up is as slow as the original problem.
:::

The better plan counts in small groups first. Each group of threads counts its own pixels into a private histogram, and only then adds that histogram to the shared one. The rest of the page builds this plan from its parts.

## A dispatch starts thread groups with numbered threads

A **dispatch** is one command that asks the GPU to run a compute :term[shader]{id=shader} many times. A compute shader has no triangles and no output picture: it reads and writes memory, and nothing else. Its entry point, from [shaders](shaders.md), is its `main` function.

The threads of a dispatch come in teams. A **thread group** is a fixed number of threads that run together on one part of the GPU and can share fast memory. The shader states the size of its group with `numthreads`, and the dispatch states how many groups to start.

Both have three directions, x, y and z, which suits images: a group is a tile of pixels. The Strata histogram uses `[numthreads(16, 16, 1)]`, a tile of 16 by 16 threads, so 256 threads per group.

:::example[Covering a 1920 by 1080 view]
One group covers 16 by 16 pixels. Across, 1920 / 16 = 120 groups fit exactly. Down, 1080 / 16 = 67.5, so 67 groups leave the last 8 rows uncovered. You need 68 groups.

The dispatch is 120 by 68 by 1 groups, which is 8,160 groups of 256 threads, or 2,088,960 threads. The picture has 2,073,600 pixels, so 15,360 threads have no pixel: they are the 8 rows past the bottom edge, 8 times 1920 wide. Those threads must check their pixel number and do nothing.
:::

The general rule is the group count: round up the division, $(\text{size} + \text{group} - 1) / \text{group}$, with whole-number division that drops the fraction. For 1080 and 16, $(1080 + 15) / 16$ is 1095 / 16, which is 68. For a size that divides evenly, such as 1920, it gives 120, no extra group.

Each thread learns who it is from built-in values. In Strata's dialect, from the shader page, these are system values with these names:

| Value | Meaning | In the 1920 by 1080 example |
| --- | --- | --- |
| `SV_GroupID` | Which group, in the dispatch | 0 to 119 across, 0 to 67 down |
| `SV_GroupThreadID` | Which thread, inside its group | 0 to 15 in each direction |
| `SV_DispatchThreadID` | Which thread, in the whole dispatch | group times 16 plus group thread |
| `SV_GroupIndex` | The group thread identifier flattened to one number | 0 to 255 |

A thread in group (3, 5), at group thread (2, 7), has dispatch thread ID (3 times 16 + 2, 5 times 16 + 7) = (50, 87). That is the pixel it handles. The flat index is $7 \times 16 + 2 = 114$.

```mermaid caption="A dispatch covers an image with tiles. Each tile is one thread group, and the last row of tiles reaches past the bottom edge." alt="A grid of square tiles laid over an image. The tiles in the bottom row extend below the image edge, and an arrow marks one tile as thread group three, five."
flowchart TB
    D["Dispatch: 120 by 68 groups"] --> G1["Group 0, 0: 16 by 16 threads"]
    D --> G2["Group 3, 5: 16 by 16 threads"]
    D --> G3["Group 119, 67: partly past the edge"]
    G2 --> T["Thread 2, 7 handles pixel 50, 87"]
```

The GPU is free to run the groups in any order, on any part of the chip, at the same time or not. A shader may therefore never rely on one group having finished before another starts. Threads inside one group, in contrast, can cooperate, as the next section shows.

## Shared memory lets a group count in private

**Shared memory** is a small, fast block of memory that all threads of one thread group read and write, and that no other group can see. It lives on the chip, close to the threads, and it vanishes when the group ends. In :term[Slang]{id=slang} you declare it with `groupshared`.

Shared memory is the tool for the histogram. Each group keeps its own 256 boxes in shared memory. Its threads add to those boxes with atomics. Threads of one group collide only with each other, and the memory is fast, so the waiting is short.

There is one trap. A thread must not read the box counts before every thread has finished adding. A **group barrier** makes every thread of the group wait until all of them reach the same line, and it makes their shared-memory writes visible. Slang calls it `GroupMemoryBarrierWithGroupSync`. It works only inside a group: no command makes different groups wait for each other within a dispatch.

The plan, as :term[pseudocode]{id=pseudocode} for one group:

```pseudocode
groupshared uint bins[256];

[numthreads(16, 16, 1)]
void main(uint3 pixelID : SV_DispatchThreadID, uint index : SV_GroupIndex)
{
    bins[index] = 0;                      // thread i clears box i
    GroupMemoryBarrierWithGroupSync();    // all boxes are zero now

    if (pixelID is inside the image)
        InterlockedAdd(bins[boxOf(pixelID)], 1);
    GroupMemoryBarrierWithGroupSync();    // all adds are done

    InterlockedAdd(globalBins[index], bins[index]);   // thread i publishes box i
}
```

1. **Line 6:** thread `index` clears box `index`, so 256 threads clear 256 boxes without a loop.
2. **Line 7:** no thread may add before all boxes are zero.
3. **Line 10:** the atomic add happens in shared memory.
4. **Line 11:** every add must finish before a box is read.
5. **Line 13:** one global atomic per box, not per pixel.

Read it in three steps. First, the 256 threads clear the 256 boxes, one each: this is why the group has exactly as many threads as the histogram has boxes. Second, every thread adds its pixel. Third, each thread adds one finished box to the global histogram.

Count the savings. Without shared memory, 2,073,600 atomics hit 256 global addresses. With it, each group publishes only its boxes that are not zero. In a desert, a tile of 256 pixels falls into a few boxes, so each of the 8,160 groups sends a few global adds, not 256. The many collisions of similar pixels happen in fast shared memory instead.

Shared memory is limited. Strata keeps a group's shared memory within 32 KiB, the limit of :term[MoltenVK]{id=moltenvk}, the layer that runs :term[Vulkan]{id=vulkan} on Apple computers, so the same shader runs everywhere. The histogram's 256 boxes of 4 :term[bytes]{id=byte} each use 1 KiB, far below it. Check the limit by hand: 32 KiB is 32,768 bytes, enough for 8,192 four-byte numbers per group.

## Shaders write to storage resources

Until now the shader has written to `groupshared` memory and to `globalBins`. A shader writes global memory through special resources, the unordered access views (UAV). A **UAV** is a resource a shader may write in arbitrary places, in any order; a UAV that holds an image is also called a storage image. A plain `Texture2D`, in contrast, is a resource a shader only reads.

A **structured buffer** is an :term[array of structs]{id=array-of-structs}, indexed by number, that a shader reads or, when its name starts with `RW`, also writes. The histogram uses `RWStructuredBuffer<uint>`, an array of 256 unsigned numbers, as its UAV. A `RWTexture2D` is the image form.

Strata states two rules for compute shaders, because some devices lack features that others have:

- A compute shader reads a texture with `Load` (by pixel number) or `SampleLevel` (with an explicit detail level), never `Sample`. `Sample` needs the change of the coordinate between neighbor threads, called derivatives, and compute shaders need not have them on every device.
- A storage image states its format, as in `[vk::image_format("r16f")]` on the ambient-occlusion shaders. A stated format lets the shader compile for devices that cannot write an image of unknown format.

## A barrier orders one dispatch before the next

The group barrier works inside one dispatch. A second kind of ordering is needed between two dispatches: the exposure step reads the histogram boxes that the histogram step wrote. If the GPU started the second dispatch while the first still ran, it would read half-finished counts.

A **barrier**, also called a resource state change, is a command that tells the GPU a resource changes use, and that earlier writes must finish before later reads begin. Between two dispatches that use one buffer as a UAV, the barrier says: all writes of the first dispatch are complete and visible before the second dispatch starts.

Forgetting it gives a bug that comes and goes: on a fast GPU, the first dispatch may finish in time, and the picture looks right on your machine and wrong on another. :term[Validation layers]{id=validation-layer} catch some cases, but not all.

How :term[NVRHI]{id=nvrhi}, the graphics layer Strata uses, tracks states and places barriers is in [resource lifetimes](resources-lifetimes.md). Here it matters that you decide where the barrier goes: write it wherever a dispatch reads what an earlier dispatch wrote.

## A scan gives every item its own output range

The second pattern solves a different problem. A culling shader looks at 10,000 objects and keeps some. Each kept object writes a few draw records, a different number each. Where in one output array does each object write?

The naive answer is an atomic counter: each object adds its record count to a shared counter and takes the old value as its start. The ranges never overlap. But the order of the objects depends on which thread reached the counter first, so two frames of the same scene can place the objects in different orders.

A **prefix sum** (or scan) turns a list of counts into the running totals before each item. An exclusive scan of $c_0, c_1, c_2, \ldots$ gives start $s_0 = 0$, $s_1 = c_0$, $s_2 = c_0 + c_1$, and so on. Item $i$ writes its records from $s_i$ to $s_i + c_i - 1$. The result depends only on the counts, not on timing, so it is the same in every run.

:::example[Four boxes, ranges from counts]
Counts per box are 2, 3, 3, 4. Exclusive scan: the starts are 0, 2, 5, 8, and the total is 12. Box 2 owns slots 5, 6 and 7. Every box can write at once, without any atomics, because no two ranges share a slot.
:::

**Prefix allocation** gives each item or group a block of slots of an output array, so that all can write at once without overlapping. The atomic running offset is the simplest form. The scan is the form with a fixed order, and a scan itself runs in several dispatches: groups scan their own pieces, the group totals are scanned, and the totals are added back.

## Engines count on the GPU in five ways

Each approach below fixes a flaw of the one before.

| Approach | Cost | Quality | Complexity | Used by |
| --- | --- | --- | --- | --- |
| CPU loop over read-back pixels | Slow: a copy to the CPU and a loop over 2 million pixels | Exact | Low | Early engines and tools |
| Fragment-shader tricks (draw each pixel as a point into a box) | Heavy on the fixed-function blend unit | Exact, but with many draw limits | Medium | Engines without compute |
| Compute with global atomics | Slow when many pixels share a box | Exact | Low | First compute ports |
| Compute with shared memory | Fast: collisions stay inside groups | Exact | Medium | Most engines' exposure passes |
| Multi-pass scans | Several dispatches and barriers | Exact and ordered | High | Culling and sorting passes |

Sources for each row are in Further reading.

## Strata uses compute where the data is on the GPU

:::why[Why not use wave operations or a second queue?]
A wave operation lets the threads of one hardware wave share values without shared memory. Strata's shaders use none, so one code path runs on every Vulkan device, including MoltenVK. The cost: a few passes may do more memory traffic than the best hand-tuned version.
:::

Strata makes a compute pipeline with `SceneRenderer::CreateComputePipeline(shader, layout)`. It takes the name of a compute shader and a binding layout, and it stops with an error when the shader is missing. The shaders are written in the same dialect as the others, and the compute stage is one more entry point: see [shaders](shaders.md). Registers and layouts are in [binding](binding.md).

The real histogram, `Strata/shaders/PostProcess/Histogram.comp.slang`, is the toy at full size. Its entry point `main`, below the quote, copies the system values into names that start with `st_`: `st_LocalInvocationIndex` is the `SV_GroupIndex`, and `st_GlobalInvocationID` is the `SV_DispatchThreadID`. Search for the three phases and the two atomics.

```slang src="Strata/shaders/PostProcess/Histogram.comp.slang#L52-L71"
groupshared uint s_Bins[ST_HISTOGRAM_BINS];

void st_Main()
{
	s_Bins[st_LocalInvocationIndex] = 0u;
	GroupMemoryBarrierWithGroupSync();

	int2 pixel = int2(st_GlobalInvocationID.xy);
	int2 size = TextureSize(u_SceneColor, 0);
	if (all((pixel < size)))
	{
		uint bin = LuminanceToHistogramBin(Luminance(u_SceneColor.Load(int3(pixel, 0)).rgb) * u_Parameters.InversePreExposure);
		InterlockedAdd(s_Bins[bin], MeteringWeight(pixel, size));
	}
	GroupMemoryBarrierWithGroupSync();

	uint count = s_Bins[st_LocalInvocationIndex];
	if (count > 0u)
		InterlockedAdd(u_Histogram[st_LocalInvocationIndex], count);
}
```

1. **Line 56:** the same clearing step, one box per thread.
2. **Line 57:** the group barrier after the clearing.
3. **Line 64:** the add into shared memory, weighted by the pixel's metering weight.
4. **Line 66:** the group barrier before the boxes are read.
5. **Line 70:** the add into the global buffer, skipped when the count is zero.

Compare it with the toy. The shared box array has `ST_HISTOGRAM_BINS` entries, 256, and the group is 16 by 16, so each thread clears and publishes one box. The weight added for a pixel is 1, or in center-weighted metering from 4 at the edges to 16 at the center: that is the subject of [exposure](../image/exposure.md).

Now the CPU side. The next quote clears the buffer, dispatches the histogram, and then the exposure.

```cpp src="Strata/src/Strata/Renderer/SceneRendererPost.cpp#L962-L976"
commandList->clearBufferUInt(m_HistogramBuffer, 0);
nvrhi::ComputeState state;
state.pipeline = m_HistogramPipeline;
state.bindings = { bindingSet };
commandList->setComputeState(state);
commandList->setPushConstants(&parameters, sizeof(parameters));
commandList->dispatch((m_ViewportSize.x + 15) / 16, (m_ViewportSize.y + 15) / 16, 1);

// NVRHI places barriers only when the binding sets change: the histogram must be complete before it is read.
commandList->setBufferState(m_HistogramBuffer, nvrhi::ResourceStates::UnorderedAccess);
commandList->commitBarriers();
state.pipeline = m_ExposurePipeline;
commandList->setComputeState(state);
commandList->setPushConstants(&parameters, sizeof(parameters));
commandList->dispatch(1, 1, 1);
```

1. **Line 962:** the shader only adds, so the buffer starts at zero.
2. **Line 968:** the histogram dispatch, 120 by 68 groups for a 1920 by 1080 view.
3. **Lines 971–972:** the explicit barrier before the next dispatch reads the boxes.
4. **Line 976:** one group runs the exposure step.

The group counts are the rounding rule from earlier: `(width + 15) / 16` across and the same for height. The buffer is cleared first, because the shader only adds. The source asks for an explicit barrier on the buffer between the two dispatches. Its comment says that NVRHI places barriers only when binding sets change, and both dispatches use one set.

Two more real uses are worth opening later. The culling in `Strata/shaders/Scene/CullBuild.comp.slang` allocates each draw list's range with `InterlockedAdd` on a running counter: prefix allocation, as in [GPU-driven drawing](../draw/gpu-driven.md). The global illumination code starts a pass with `dispatchIndirect`. Its group count comes from a buffer that an earlier shader wrote, so the CPU never learns how many large triangles there were.

## What compute in Strata cannot do

Strata uses no wave (subgroup) operations in its shaders, so it never shares a value between lanes of a wave without shared memory. It also runs every compute dispatch on the graphics queue. The device fetches a compute queue, but no code submits to it, so compute work cannot overlap graphics work on a queue of its own. The [not in Strata](../appendix/not-in-strata.md) page lists these absences.

A group has no way to wait for another group in the same dispatch. An algorithm that needs this, such as a scan over a long list, needs several dispatches with barriers between them.

## Common mistakes

- **Rounding down the group count.** Symptom: the last rows or columns of the image stay undone, as a stripe. Fix: round up, and make threads past the edge do nothing.
- **Reading shared memory before the barrier.** Symptom: counts that differ by a few from frame to frame. Fix: put a group barrier between the last write and the first read.
- **Using a group barrier for two groups.** Symptom: the same wrong counts. Fix: end the dispatch, and place a barrier before the next one.
- **Using `Sample` in compute.** Symptom: a :term[compile error]{id=compile-error} or a missing capability on some devices. Fix: use `SampleLevel` or `Load`.
- **Forgetting to clear an adding buffer.** Symptom: counts that grow every frame. Fix: clear it before the dispatch, as the exposure code does.

## Summary

- A dispatch of $(\text{size} + \text{group} - 1) / \text{group}$ groups per axis covers an image, and the threads past the edge do nothing.
- A group counts into shared memory first, so collisions stay inside the fast group, and only finished counts reach global memory.
- A barrier is needed wherever a dispatch reads what an earlier dispatch wrote; a group barrier covers only one group.
- A :term[prefix sum]{id=prefix-sum} turns counts into start offsets, so each item has its own output range in an order that never depends on timing.

## Check yourself

1. A view is 1280 by 720, and the group is 16 by 16. How many groups does the dispatch start, and how many threads lie outside the image?

   :::answer{tests="dispatch-size"}
   1280 / 16 = 80 and 720 / 16 = 45, both exact. So 80 by 45 = 3,600 groups, and no thread lies outside the image.
   :::

2. Why does each group add its box to the global histogram once, instead of every pixel adding to the global histogram?
   - A. Global memory cannot hold atomics.
   - B. Shared memory is faster and holds the collisions inside the group.
   - C. Groups must run in order.

   :::answer{tests="shared-histogram"}
   B. Global memory does support atomics (A is wrong): the cost is the queue at one address. Groups run in any order (C is wrong). B moves the collisions into fast memory.
   :::

3. Dispatch A writes a buffer, and dispatch B reads it. Where does the barrier go, and what happens without one?

   :::answer{tests="barrier-place"}
   Between the two dispatches, on the buffer. Without it, B may start before A finishes and read old or partial values, sometimes only on some devices.
   :::

4. The counts of four groups are 5, 0, 2, 4. Give each start offset and the total.

   :::answer{tests="scan-ranges"}
   The starts are 0, 5, 5, 7 and the total is 11. The second group owns no slot, and the third owns slots 5 and 6.
   :::

## Exercises

1. **Basic.** Run the sketch below, then change `c_GroupSize` to 6. Predict the line for group 1 first.

   :::answer[Worked solution]{tests="shared-histogram,scan-ranges" solution="sketches/gpu-compute-histogram.cpp"}
   The sketch emulates a dispatch: each group fills its own array, then adds to the global one, and a scan gives starts.

   ```cpp sketch="gpu-compute-histogram.cpp"
   #include <array>
   #include <cstdio>
   #include <vector>

   // A CPU emulation of one dispatch: every "group" owns its own small histogram (the shared memory), fills it,
   // and only then adds it to the global histogram (the buffer every group shares).
   constexpr int c_BinCount = 4;
   constexpr int c_GroupSize = 4;

   int main()
   {
   	// Twelve pixels, each already reduced to a bin number from 0 to 3.
   	const std::vector<int> pixels = { 0, 1, 1, 3, 2, 2, 2, 0, 3, 3, 3, 1 };
   	const int groupCount = (static_cast<int>(pixels.size()) + c_GroupSize - 1) / c_GroupSize;

   	std::array<int, c_BinCount> global = {};
   	for (int group = 0; group < groupCount; group++)
   	{
   		std::array<int, c_BinCount> shared = {};
   		for (int thread = 0; thread < c_GroupSize; thread++)
   		{
   			const int pixel = group * c_GroupSize + thread;
   			if (pixel < static_cast<int>(pixels.size()))
   				shared[pixels[pixel]]++;
   		}
   		for (int bin = 0; bin < c_BinCount; bin++)
   			global[bin] += shared[bin];
   		std::printf("group %d: %d %d %d %d\n", group, shared[0], shared[1], shared[2], shared[3]);
   	}
   	std::printf("global:  %d %d %d %d\n", global[0], global[1], global[2], global[3]);

   	// Exclusive prefix sum: the start of each bin's output range.
   	int running = 0;
   	for (int bin = 0; bin < c_BinCount; bin++)
   	{
   		std::printf("bin %d starts at %d\n", bin, running);
   		running += global[bin];
   	}
   	return 0;
   }
   ```

   ```text output-of="gpu-compute-histogram.cpp"
   group 0: 1 2 0 1
   group 1: 1 0 3 0
   group 2: 0 1 0 3
   global:  2 3 3 4
   bin 0 starts at 0
   bin 1 starts at 2
   bin 2 starts at 5
   bin 3 starts at 8
   ```

   1. **Line 14:** the group count rounds up, as in the 1920 by 1080 example.
   2. **Line 19:** each group has its own array, the stand-in for shared memory.
   3. **Line 23:** a thread past the end of the data does nothing.
   4. **Line 27:** each group adds its finished boxes to the global ones, once.
   5. **Lines 33–37:** the scan: each start is the sum of the counts before it.

   With a size of 6, there are two groups. Group 1 holds pixels 6 to 11, which are 2, 0, 3, 3, 3, 1, so its line is `group 1: 1 1 1 3`. The global totals stay 2 3 3 4: the answer does not depend on the group size.
   :::

2. **Medium.** For a 1920 by 1080 view, compute the histogram dispatch's group counts, then say why the exposure dispatch needs an explicit barrier.

   :::answer[Worked solution]{tests="dispatch-size,barrier-place"}
   In `SceneRendererPost.cpp`, the dispatch is `(m_ViewportSize.x + 15) / 16` by `(m_ViewportSize.y + 15) / 16` by 1: 120 by 68. The two dispatches share one binding set, and NVRHI places barriers only when binding sets change, so the code sets the buffer state and commits the barrier before the exposure dispatch reads the boxes.
   :::

## Where it lives in Strata

- `SceneRenderer::CreateComputePipeline` in `Strata/src/Strata/Renderer/SceneRenderer.cpp` makes every compute pipeline.
- `Strata/shaders/PostProcess/Histogram.comp.slang` and `Strata/shaders/PostProcess/Exposure.comp.slang` are the histogram and the exposure steps.
- `Strata/src/Strata/Renderer/SceneRendererPost.cpp` records their dispatches and the barrier.
- `Strata/shaders/Scene/CullBuild.comp.slang` allocates ranges; `Strata/src/Strata/Renderer/SceneRendererGlobalIllumination.cpp` has the indirect dispatch.

## Further reading

- Microsoft, "HLSL Shader Model 5 compute shaders and groupshared memory": the model for `numthreads` and `groupshared` (intermediate).
- NVIDIA, "Parallel Prefix Sum (Scan) with CUDA", GPU Gems 3, chapter 39: how scans work on a GPU (advanced).
- Khronos, "Vulkan specification: compute and synchronization" (advanced).
