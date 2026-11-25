---
id: assets/uploads
title: "Budgeted uploads"
description: "How Strata sends the bytes of finished assets to the graphics card in steps that fit each frame's byte and time budgets, so no large texture stalls a frame."
kind: internals
size: L
tracks: [E]
needs: [assets/residency, assets/texture-cooking, gpu/upload-queue]
time: 80
learn:
  - id: step-budget
    text: compute how many frames the upload of a large texture takes from the frame's byte and time budgets
  - id: finalize-contract
    text: explain what a finalizer may do in one call and what Done, Pending, Failed and AwaitingGPU tell the manager
  - id: staging-bound
    text: compute the upload rate that the staging bound allows and name the budget that limits it first
  - id: no-graphics-api
    text: explain why the asset layer records uploads into an upload context and never into a graphics API
  - id: trace-finalize
    text: trace the finalize calls of a large texture across frames and read the bytes each one reports
since: 0.3.0
status: final
---

A game loads a texture of 90 MB while the player walks down a corridor. The :term[bytes]{id=byte} have been read and decoded by now, and one thing is left: they must reach the memory of the :term[graphics card]{id=gpu}. This page covers the asset layer's half of that work. It makes sure that the copy happens in small steps, that every step fits what is left of the frame's budgets, and that every frame still moves the load forward.

The page does not cover how a step is written into staging memory or how the copies are ordered and tracked: that is the mechanism of [the upload queue](../gpu/upload-queue.md). It also does not decide whether an arrival may come in at all, which is the business of [residency](residency.md).

## The problem and how engines solve it

Take the texture above: 90 MiB is 94,371,840 bytes. The upload queue starts from a guess of 4 million bytes per millisecond, so writing all of it takes about 23.6 ms. A frame at 60 :term[frames per second]{id=frame-rate} lasts 16.7 ms, so one call that uploads the whole texture makes that frame 141 % as long as it should be, and the player sees a pause.

An engine can avoid the pause with a ring of :term[staging buffers]{id=staging-buffer}, a copy queue beside the graphics queue, or a cap on the bytes each frame. Each answer has a cost, and [the upload queue](../gpu/upload-queue.md) weighs them: it explains why a texture goes through staging memory and what a fence is.

The question of this page comes one level up. Who decides how much of a texture goes in this frame, and how does a texture of any kind say so without knowing the graphics library? Strata answers with a budget that travels with each call. A contract lets the asset's :term[finalize]{id=finalize} function stop halfway and continue in a later frame.

## The map: two sides of one seam

Two layers share the work, and a small interface sits between them. The asset layer knows what to upload and how much of the frame is left. The :term[renderer]{id=renderer} knows how to write staging memory and record copies. The asset layer must not include a graphics :term[header]{id=header}, so the renderer plugs itself in from the other side.

```mermaid caption="The asset manager opens a batch, calls each asset's finalize function with a context of budgets, and submits the batch. The texture records into the renderer's context behind the seam." alt="A flow of boxes. The asset manager calls an asset's finalize function with a finalize context. The function records into an upload context, an interface of the asset layer. The renderer's upload context implements it and feeds the upload queue. A batch goes to the graphics card when the manager submits it."
flowchart LR
    M["AssetManagerBase::Update"] -->|"Begin batch"| U["AssetUploadContext (interface)"]
    M -->|"AssetFinalizeContext: budgets"| T["Texture::FinalizeOnMainThread"]
    T -->|"records steps"| U
    U --- R["RendererUploadContext"]
    R --> Q["GPUUploadQueue"]
    Q --> S["StagingPool"]
    M -->|"Submit batch"| U
    I["IAssetGraphics service"] -.->|"hands out"| M
```

On the asset side five names matter. `AssetFinalizeContext` is what an asset's finalize function is given: the budgets of the call. `AssetFinalizeResult` is what it gives back. `c_AssetUploadStepBytes` is the largest step an asset may take. `AssetUploadContext` and `IAssetGraphics` are the seam, in `Strata/src/Strata/Asset/AssetUploadContext.h`, with the contract itself in `Strata/src/Strata/Asset/Asset.h`.

On the renderer's side `RendererUploadContext` implements the seam and records into `GPUUploadQueue`, and `Texture` is the asset that uses both. All of it runs on the :term[main thread]{id=main-thread}. The vocabulary below stays close to the code.

An **upload** is the copy of an asset's bytes from main memory into the graphics card's memory.

An **upload step** is one piece of an upload: a call records at most `c_AssetUploadStepBytes` bytes into the queue, and a large asset takes many steps over many frames.

The **upload context** is the object that an asset's finalize function records its steps into, `AssetUploadContext` in the code: an interface of the asset layer that the renderer implements.

A **batch** (of uploads) is everything that the finalize calls of one manager update record. The manager opens it before them and submits it after them, and the contract below says why.

## The contract

Every asset has a function `FinalizeOnMainThread`, which turns its decoded data into something the graphics card can use. The manager calls it on the main thread with an `AssetFinalizeContext`, and the asset answers with an `AssetFinalizeResult`. The rules follow, each with its reason.

- **Record into the context, never into a graphics library.** The field `Upload` holds the upload context, or null when there is no graphics device, and then assets for the graphics processing unit (GPU) keep their data on the :term[central processing unit]{id=processor} (CPU). Reason: the asset layer includes no graphics application programming interface (API), so a test can stand in for the renderer.
- **Take steps of at most `c_AssetUploadStepBytes`, which is 4 MiB.** A step copies about a millisecond of memory at most. Reason: one step is the longest the main thread is held, so a frame that runs late runs late by a step and not by a texture.
- **Size each step to what is left.** The bytes left of `UploadBudget`, the milliseconds left of `UploadMsBudget` and the time until `Deadline` all bound a step, at the speed of the latest steps. `UploadMsBudget` comes from the frame's upload time, `UploadMsPerFrame` (2 ms by default), less a tenth the planner keeps in reserve for slow steps, and `Deadline` ends the frame's finalize time, `FinalizeMsPerFrame` (4 ms). A step is a whole number of :term[granules]{id=granule}, whole block rows of about 64 KiB or one row where a row is larger, and a call takes no step once not even one fits. Reason: a frame that obeys its budget needs steps that end close to it.
- **Make progress in the frame's first step.** When `FirstOfFrame` is true and nothing was uploaded yet in the frame, the first step goes whatever the byte and time budgets say, one granule at least. Reason: a budget smaller than a granule must not freeze a load, and a texture larger than any budget must still arrive.
- **Report the bytes.** The call adds what it uploaded to `*UploadedBytes`, and its time to `*UploadMs`. Reason: the next call of the frame is given what is left, and the statistics show what the frame spent.
- **Answer with the right result.** `Done` means the asset can be published. `Pending` means the budget ran out and the asset continues in the next call. `Failed` means it cannot be made.
- **Wait for the card only when allowed.** `AwaitingGPU` means that every copy is recorded, but on a queue that the graphics card runs beside the frame's work. The asset continues once the card has finished, and the arrivals behind it continue meanwhile. Only a context with `MayWait` allows this answer.

The manager keeps three promises in return. It opens one batch per update, so that all the frame's finalize calls record together. It submits that batch before anything renders, so that what was recorded reaches the card ahead of the draw calls that use it.

The manager sets `FirstOfFrame` for the frame's first call and for no other. It also keeps a `Pending` asset first in line, so that arrivals finish in order.

:::rule
The asset layer includes no :term[graphics API]{id=graphics-api}: finalize functions record into `AssetUploadContext`, and the :term[layering test]{id=layer-table} refuses `nvrhi/` and `vulkan/` headers under `Strata/src/Strata/Asset/`. The reason is a test that drives the whole contract with a fake context, and a game's asset code that never depends on the backend. See [layers and registries](../core/layers-registries.md) for the layer table.
:::

### The staging bound

Staging memory is the extra block that uploads pass through, and its size bounds the rate of the whole system. `StagingBytes` is the most that uploads may keep :term[in flight]{id=in-flight}, 32 MiB by default. A step through staging waits while the staging already in flight leaves it no room. The first step of a frame is allowed up to all of `StagingBytes`. Later steps are allowed up to `GetStagingRoom()`, which is `StagingBytes` less one step, so 28 MiB with the default.

The reason for the lower limit is the next frame. Its first step must find room even when the card has not finished the copies of this frame, so the later steps of this frame leave one step of room for it. The cost is that the bound, and not only the byte budget, can limit a frame.

:::why
A step of at most 4 MiB is about a millisecond of memory copying. The main thread cannot stop a step once it began, so the step size is the longest delay that one finalize call adds to a frame. Smaller steps would cost more calls and more staging buffers; larger ones would bring back the pause that the steps are there to remove.
:::

Staging is free again once the card has run the copies that read it. When the card runs a frame's copies before the next frame's finalize calls, every frame finds its staging free, and sustained uploads reach 28 MiB a frame. When frames come faster than the copies, about half of that arrives.

With the defaults, though, `UploadBytesPerFrame` (16 MiB), `UploadMsPerFrame` (2 ms) and `FinalizeMsPerFrame` (4 ms) stop the work first, so the staging bound limits only a setup that raises those. The header of `Strata/src/Strata/Asset/AssetResidency.h` says to raise them together with `StagingBytes` for a loading screen.

A game cannot do that. No script function and no settings section sets these budgets, and the :term[runtime]{id=runtime} option `--asset-budget-mb` sets only the budget for graphics textures. Only the editor sets them, through its command `asset.setBudget`.

## A worked frame

:::example[A 90 MiB texture, frame by frame]
Suppose the frame may upload 16 MiB and spend 2 ms on upload steps (the defaults), and the queue measures 5 MiB per millisecond. The texture has 90 MiB left, and the granule is 64 KiB. This is the first call of the frame, and the pool holds idle staging of every size needed.

The queue keeps a tenth of the frame's 2 ms in reserve, which is 0.2 ms, so the first step may use 2 - 0.2 = 1.8 ms. That buys 9 MiB, but a step is at most 4 MiB. Step one is 4 MiB and costs 4 / 5 = 0.8 ms.

Step two sees 2 - 0.8 - 0.2 = 1.0 ms, which buys 5 MiB, so it takes 4 MiB again and the call has now used 1.6 ms. Step three sees 2 - 1.6 - 0.2 = 0.2 ms, which buys exactly 1 MiB, a whole number of granules. Step four sees nothing and returns zero bytes.

The call reports 9 MiB and ends `Pending`. The same happens in the next frames, so 90 / 9 is 10 frames, or about 167 ms at 60 :term[frames per second]{id=frame-rate}. No frame spends more than 2 ms of upload steps, where one call of 90 MiB would need 18 ms. The byte budget of 16 MiB was never the limit here: the time was. The staging bound was not either, because 9 MiB per frame is far below 28.
:::

The real speed differs from machine to machine and from step to step. The queue starts from 4 million bytes per millisecond and corrects its figure with what it measures, so the plan changes while the load runs.

## A toy version

The toy below has no graphics at all. An asset uploads in equal steps, a manager gives each call what is left of a frame's budget, and an asset that runs out of budget stays first in line. Its shape follows `SteppedAsset` in the test file `StrataTests/src/Asset/AssetFinalizeTests.cpp`. Three assets of three 1 MiB steps wait for a frame budget of 2 MiB, and the program prints how many MiB each frame uploads.

```cpp sketch="assets-uploads-toy.cpp"
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <vector>

constexpr uint64_t c_MiB = 1ull << 20;

enum class Result
{
	Done,
	Pending
};

// What one call may do: the bytes left of the frame's budget, and whether the call is the frame's first.
struct Context
{
	uint64_t UploadBudget = 0;
	bool FirstOfFrame = false;
	uint64_t* UploadedBytes = nullptr;
};

// An asset that uploads in equal steps. It never records into a graphics API: it only says how many bytes it moved.
class SteppedAsset
{
public:
	SteppedAsset(uint32_t steps, uint64_t stepBytes)
		: m_Steps(steps), m_StepBytes(stepBytes)
	{
	}

	Result Finalize(const Context& context)
	{
		uint64_t uploaded = 0;
		while (m_Done < m_Steps)
		{
			// Only the frame's first step ignores the budget, so every frame makes progress.
			const bool framesFirst = context.FirstOfFrame && uploaded == 0;
			if (!framesFirst && uploaded + m_StepBytes > context.UploadBudget)
				break;
			uploaded += m_StepBytes;
			m_Done++;
		}
		*context.UploadedBytes += uploaded;
		return m_Done < m_Steps ? Result::Pending : Result::Done;
	}

private:
	uint32_t m_Steps;
	uint64_t m_StepBytes;
	uint32_t m_Done = 0;
};

int main()
{
	std::vector<SteppedAsset> queue(3, SteppedAsset(3, c_MiB));
	const uint64_t frameBudget = 2 * c_MiB;
	size_t next = 0;
	for (int frame = 1; next < queue.size(); frame++)
	{
		uint64_t uploaded = 0;
		bool first = true;
		while (next < queue.size())
		{
			if (!first && uploaded >= frameBudget)
				break;
			const Context context { frameBudget - std::min(uploaded, frameBudget), first, &uploaded };
			const Result result = queue[next].Finalize(context);
			first = false;
			if (result == Result::Pending)
				break; // Keeps its place in line
			next++;
		}
		std::printf("frame %d: %llu MiB\n", frame, static_cast<unsigned long long>(uploaded / c_MiB));
	}
	return 0;
}
```

```text output-of="assets-uploads-toy.cpp"
frame 1: 2 MiB
frame 2: 2 MiB
frame 3: 2 MiB
frame 4: 2 MiB
frame 5: 1 MiB
```

1. **Lines 37–38:** only the frame's first step ignores the budget, so every frame makes progress; every other step must fit what is left.
2. **Line 44:** the asset answers `Pending` while steps remain and `Done` after the last one.
3. **Lines 64–66:** the manager stops once the frame's bytes are used, and hands each call only what is left.
4. **Lines 69–70:** a `Pending` asset breaks the loop and keeps its place in line.

Nine MiB arrive at 2 MiB per frame, so a fifth frame holds the last one. No frame exceeds its budget, because every step is 1 MiB and the budget is a whole number of steps.

Look at what the loop does with `Pending`: it breaks, so the asset that ran out of budget is the first to be called again in the next frame, ahead of the others. The toy lacks the time budget, the staging bound and the batch. Like the real texture, it lets only the frame's first step ignore the budget.

## The real code, in the order the data flows

### The seam

The asset layer sees the renderer only through two types. The first is the upload context, with its three functions. The second is `IAssetGraphics`, an engine service that hands out the context of the running renderer.

```cpp src="Strata/src/Strata/Asset/AssetUploadContext.h#L16-L29"
class AssetUploadContext
{
public:
	virtual ~AssetUploadContext() = default;

	// Opens a batch: the finalizations until Submit record into it. A batch opened while one is open (a memory asset
	// added by code a finalization runs) joins it: the outermost Submit submits.
	virtual void Begin() = 0;
	// Submits what the batch recorded (nothing when it recorded nothing).
	virtual void Submit() = 0;
	// Once per manager update, after its finalizations: lets the context return memory it no longer needs (idle staging).
	// Returns whether it returned staging memory that had become idle (AssetManagerStats::StagingReleases).
	virtual bool EndFrame(uint64_t uploadedBytes) = 0;
};
```

1. **Line 16:** the class is an interface of the asset layer, so a test can implement it without a graphics device.
2. **Lines 21–23:** `Begin` opens a batch, and a second `Begin` while one is open joins it, so code that adds an asset in the middle of a finalize call does not break the batch.
3. **Line 25:** `Submit` sends what was recorded, and a batch that recorded nothing sends nothing.
4. **Line 28:** `EndFrame` takes the frame's uploaded bytes and lets the context return idle staging memory once per update.

### The manager's finalize loop

`ProcessCompletions` takes the arrivals that finished reading and decoding and :term[finalizes]{id=finalize} them in order. The quote starts where the manager has chosen an arrival. Watch how the frame's budgets turn into the fields of one context, and what the manager does with each result.

```cpp src="Strata/src/Strata/Asset/AssetManager.cpp#L1171-L1215" from="// Finalization runs without holding the lock" to="completion.LoadedAsset = nullptr;" symbol="AssetManagerBase::ProcessCompletions"
// Finalization runs without holding the lock: it may request dependent assets (e.g. a material's textures). With
// the budget, it gets what is left of the frame's: a large upload continues in the next frame (Pending).
processed++;
if (completion.LoadedAsset)
{
	AssetFinalizeContext context { upload, this };
	context.Prefetched = prefetched;
	if (applyBudget)
	{
		context.UploadBudget = budgets.UploadBytesPerFrame - std::min(uploadedBytes, budgets.UploadBytesPerFrame);
		context.UploadMsBudget = std::max(0.0f, budgets.UploadMsPerFrame - uploadMs);
		context.UploadMsFrameBudget = budgets.UploadMsPerFrame;
		context.Deadline = deadline;
		context.StagingBytes = budgets.StagingBytes;
	}
	context.UploadedBytes = &uploadedBytes;
	context.UploadMs = &uploadMs;
	context.MayWait = applyBudget;
	context.FirstOfFrame = finalizations == 0;
	finalizations++;
	AssetFinalizeResult result = completion.LoadedAsset->FinalizeOnMainThread(context);
	// Without a budget an asset has to finish in its call, but what it needs may not happen in the open batch: a mesh
	// whose geometry needs the geometry pool to grow after the batch wrote into the pool waits for the next batch
	// (GeometryPool::Allocate). It gets that batch at once: what the open one recorded is submitted, and the asset
	// is finalized again in a new one.
	if (result == AssetFinalizeResult::Pending && !applyBudget && upload)
	{
		upload->Submit();
		upload->Begin();
		result = completion.LoadedAsset->FinalizeOnMainThread(context);
	}
	if (result == AssetFinalizeResult::Pending && applyBudget)
		break; // Stays in line
	if (result == AssetFinalizeResult::AwaitingGPU && applyBudget)
	{
		awaitingGpu.push_back(std::move(completion));
		completions.pop_front();
		continue;
	}
	if (result != AssetFinalizeResult::Done)
	{
		// Without a budget an asset has to finish: one that still asks for more in a batch of its own is broken.
		completion.Error = result == AssetFinalizeResult::Failed ? "Failed to create GPU resources"
			: "Finalization did not finish without an upload budget";
		completion.LoadedAsset = nullptr;
```

1. **Lines 1180–1184:** with a budget, the call gets what is left of the frame: bytes, milliseconds, the whole frame's milliseconds for the reserve, the deadline and the staging bound.
2. **Line 1189:** only the frame's first call is marked `FirstOfFrame`, because the manager counts the calls made so far.
3. **Lines 1196–1200:** a call without a budget that ends `Pending` gets one more call in a new batch, which is the geometry pool's case.
4. **Lines 1202–1203:** with a budget, `Pending` breaks the loop, so the asset keeps its place in line for the next frame.
5. **Lines 1204–1209:** `AwaitingGPU` moves the arrival to a separate queue, and the arrivals behind it continue.

### The texture's finalize function

A texture goes from its decoded levels to a published asset in several calls. The first call makes the graphics texture and sets its upload position, and every call continues the upload from that position. Only a complete upload reaches the publication in the second half below.

```cpp src="Strata/src/Strata/Renderer/Texture.cpp#L466-L498" from="RendererUploadContext* upload = RendererUploadContext::From" to="return progress;" symbol="Texture::FinalizeOnMainThread"
RendererUploadContext* upload = RendererUploadContext::From(context.Upload);
if (!upload || !upload->GetQueue().IsBatchOpen() || m_BindlessSlot != BindlessTextureTable::c_InvalidSlot)
	return AssetFinalizeResult::Done; // No renderer (tools, tests): CPU data only; or finalized before

// Past the deadline only the frame's first finalization works (AssetFinalizeContext::FirstOfFrame); creating the GPU
// texture is work too.
if (!context.FirstOfFrame && std::chrono::steady_clock::now() >= context.Deadline)
	return AssetFinalizeResult::Pending;

if (!m_UploadTexture)
{
	// Loaders decode block-compressed data for such devices (IsBlockCompressionSupported); textures created from
	// blocks in memory cannot be shown on them.
	if (IsBlockCompressedFormat(m_Specification.Format) && !Renderer::GetGraphicsDevice().GetInfo().SupportsBCCompression)
	{
		ST_CORE_ERROR("Texture '{}' is {}, which the graphics device cannot sample", m_Specification.DebugName,
			TextureFormatToString(m_Specification.Format));
		return AssetFinalizeResult::Failed;
	}
	// The levels the cooked data held: all of them, or a partial load's mip tail.
	m_UploadTexture = CreateGPUTexture(m_LoadedLevel);
	if (!m_UploadTexture)
		return AssetFinalizeResult::Failed;
	m_UploadPosition = UploadPosition { m_LoadedLevel, m_MipCount - m_LoadedLevel, 0 };
	m_UploadQueue = upload->GetQueue().ChooseQueue(context);
}

uint64_t uploaded = 0;
const AssetFinalizeResult progress = ContinueUpload(upload->GetQueue(), context, m_UploadTexture, m_UploadPosition, uploaded);
if (progress == AssetFinalizeResult::Failed)
	m_UploadTexture = nullptr;
if (progress != AssetFinalizeResult::Done)
	return progress;
```

1. **Line 467:** with no renderer, no open batch or a published texture the call returns `Done` at once: tools and tests keep CPU data.
2. **Lines 472–473:** past the deadline only the frame's first call works, even creating the graphics texture.
3. **Lines 479–484:** a device that cannot sample block-compressed data fails the texture with a logged error.
4. **Lines 489–490:** the position records the first level, the levels left and the next row, which is all the state a later call needs.
5. **Lines 494–498:** `ContinueUpload` reports its progress, and only `Done` falls through to publication.

The second half runs once every level is uploaded. Search for where the CPU copy goes, why that can wait for a later call, and which two table entries are made before the texture is published.

```cpp src="Strata/src/Strata/Renderer/Texture.cpp#L500-L529" from="// The chain is uploaded;" to="std::vector<uint8_t>().swap(m_Cooked);" symbol="Texture::FinalizeOnMainThread"
// The chain is uploaded; the CPU copy goes before the texture is published. Freeing a large one takes time like a
// step: when it would end after the deadline it is the next call's work (the frame's first call that took no step
// does it anyway).
const uint64_t cpuCopyBytes = GetCPUCopyBytes();
if (!(context.FirstOfFrame && uploaded == 0) && cpuCopyBytes >= c_TimedReleaseBytes)
{
	const auto now = std::chrono::steady_clock::now();
	const auto predicted = std::chrono::duration_cast<std::chrono::steady_clock::duration>(
		std::chrono::duration<float, std::milli>(static_cast<float>(cpuCopyBytes) / s_ReleaseBytesPerMs));
	if (now >= context.Deadline || context.Deadline - now < predicted)
		return AssetFinalizeResult::Pending;
}

const uint32_t slot = Renderer::GetBindlessTextures().Allocate(m_UploadTexture);
if (slot == BindlessTextureTable::c_InvalidSlot)
{
	m_UploadTexture = nullptr;
	return AssetFinalizeResult::Failed; // Table full (logged by the table)
}
m_BindlessSlot = slot;
m_TableIndex = Renderer::GetTextureTable().Allocate(GetTableEntry());
m_GPUTexture = std::move(m_UploadTexture);
m_ResidentLevel.store(m_LoadedLevel, std::memory_order_release);
m_ResidentBytes.store(GetLevelBytes(m_LoadedLevel, m_MipCount), std::memory_order_release);

// The GPU copy is authoritative from now on; streaming re-reads cooked data when it needs pixels again.
const auto releaseStart = std::chrono::steady_clock::now();
m_Mips.clear();
m_Mips.shrink_to_fit();
std::vector<uint8_t>().swap(m_Cooked);
```

1. **Lines 503–511:** a CPU copy of 1 MiB or more takes time to free, so the call predicts that time from the speed of earlier releases and ends `Pending` when the deadline comes first.
2. **Lines 513–518:** the bindless slot is made only now, and a full table fails the texture.
3. **Line 520:** the texture-table entry is made at publication too.
4. **Lines 521–523:** the finished texture replaces the upload texture, and the resident level and bytes are stored for readers on other threads.
5. **Lines 525–529:** the CPU copies of the levels and of the cooked data are released.

### The levels

`UploadLevels` does the planning for one call. Its loop runs from the smallest level to the largest, so the first half sizes a step and the second chooses what goes into it.

```cpp src="Strata/src/Strata/Renderer/Texture.cpp#L586-L618" from="m_UploadStarted = true;" to="const uint64_t limit = queue.PlanStep(" symbol="Texture::UploadLevels"
m_UploadStarted = true;
const TextureFormat format = m_Specification.Format;
const TextureFormatInfo info = GetTextureFormatInfo(format);
const auto levelWidth = [this](uint32_t level) { return std::max(1u, m_Width >> level); };
const auto levelHeight = [this](uint32_t level) { return std::max(1u, m_Height >> level); };
const auto levelRegion = [&](uint32_t level, uint32_t firstRow, uint32_t rows)
{
	const uint64_t rowBytes = GetBlockRowByteSize(format, levelWidth(level));
	return GPUTextureRegion { level - position.FirstLevel, levelWidth(level), levelHeight(level), firstRow, rows,
		GetMipData(level).data() + static_cast<size_t>(firstRow / info.BlockHeight) * rowBytes };
};
// Levels of textures made from pixels hold their own data: it goes once the level is uploaded.
const auto releaseLevel = [this](uint32_t level)
{
	if (level < m_Mips.size())
		std::vector<uint8_t>().swap(m_Mips[level].Data);
};

uint64_t& callBytes = outBytes;
callBytes = 0;
float callMs = 0.0f;
std::vector<GPUTextureRegion> regions;
while (position.Remaining > 0)
{
	const uint32_t level = position.FirstLevel + position.Remaining - 1;
	const uint64_t rowBytes = GetBlockRowByteSize(format, levelWidth(level));
	const uint32_t levelBlockRows = AlignUp(levelHeight(level), info.BlockHeight) / info.BlockHeight;
	const uint64_t remainingBytes = static_cast<uint64_t>(levelBlockRows - position.NextRow / info.BlockHeight) * rowBytes
		+ GetLevelBytes(position.FirstLevel, level);
	const bool framesFirst = GPUUploadQueue::IsFramesFirstStep(context, callBytes);
	// A step is a row of blocks at least, and not much less than GPUUploadQueue::c_MinStepBytes where the level has more.
	const uint64_t granule = std::max(rowBytes, std::min(GPUUploadQueue::c_MinStepBytes, remainingBytes) / rowBytes * rowBytes);
	const uint64_t limit = queue.PlanStep(context, callBytes, callMs, remainingBytes, granule);
```

1. **Lines 589–596:** a level's size halves with each level but stays at 1, and a region points into the cooked data at the first block row of the run.
2. **Lines 597–602:** a texture made from pixels frees a level's memory once that level is uploaded.
3. **Lines 610–614:** the loop starts at the smallest level left, and the bytes still to upload include the rest of this level.
4. **Lines 616–617:** the granule is one row of blocks, or whole rows that add up to about 64 KiB.
5. **Line 618:** `PlanStep` sizes the step from the budgets; the next line returns `Partial` when it answers zero.

The second half stacks small levels into one staging buffer, or cuts a large level into runs of rows. Watch which of the two branches runs, and where the call stops when staging has no room.

```cpp src="Strata/src/Strata/Renderer/Texture.cpp#L622-L672" from="// Whole levels stacked" to="position.NextRow = 0;" symbol="Texture::UploadLevels"
// Whole levels stacked in one staging buffer while their bytes fit the step and their staging buffer (a power of two
// of bytes) is a step at most; a level that does not fit alone goes up in runs of rows, a power of two of block rows
// (whole staging buffers for levels of powers of two).
regions.clear();
uint32_t stacked = 0;
uint64_t stackedBytes = 0;
if (position.NextRow == 0)
{
	for (uint32_t candidate = level + 1; candidate-- > position.FirstLevel;)
	{
		const uint64_t candidateBytes = GetLevelBytes(candidate, candidate + 1);
		regions.push_back(levelRegion(candidate, 0, levelHeight(candidate)));
		if (stackedBytes + candidateBytes > limit || GPUUploadQueue::GetStagingBytes(format, regions) > GPUUploadQueue::c_MaxStepBytes)
		{
			regions.pop_back();
			break;
		}
		stackedBytes += candidateBytes;
		stacked++;
	}
}
if (stacked == 0)
{
	const uint32_t remainingBlockRows = levelBlockRows - position.NextRow / info.BlockHeight;
	const uint64_t fitting = std::max<uint64_t>(1, limit / rowBytes);
	const uint32_t blockRows = static_cast<uint32_t>(std::min<uint64_t>(remainingBlockRows, std::bit_floor(fitting)));
	const uint32_t rows = std::min(levelHeight(level) - position.NextRow, blockRows * info.BlockHeight);
	regions.push_back(levelRegion(level, position.NextRow, rows));
}

if (!queue.HasStagingRoom(context, GPUUploadQueue::GetStagingBytes(format, regions), framesFirst))
	return UploadProgress::Partial;
const GPUUploadStep step = queue.UploadTexture(context, texture, format, regions, m_UploadQueue);
if (!step.Recorded)
	return UploadProgress::Failed;
callBytes += step.Bytes;
callMs += step.Milliseconds;

if (stacked > 0)
{
	for (uint32_t index = 0; index < stacked; index++)
		releaseLevel(level - index);
	position.Remaining -= stacked;
	continue;
}
position.NextRow += regions.front().Rows;
if (position.NextRow >= levelHeight(level))
{
	releaseLevel(level);
	position.Remaining--;
	position.NextRow = 0;
```

1. **Lines 630–634:** small levels are stacked into one staging buffer while their bytes fit the step and the buffer stays within 4 MiB.
2. **Lines 645–649:** a level that does not fit goes in runs of rows, and the run is a power of two of block rows.
3. **Lines 652–653:** a step without staging room ends the call `Partial`, and the next call tries again.
4. **Lines 654–658:** the queue records the copy, and its bytes and milliseconds are added to the call's totals.
5. **Lines 660–672:** the position moves on by the stacked levels, or by the rows of the run.

A level of 4,096 by 4,096 texels in a format of 16 bytes per block of 4 by 4 texels has 1,024 block rows of 16,384 bytes, which is 16 MiB. With a step limit of 4 MiB, `limit / rowBytes` is 256 rows, a power of two, so four runs of 256 block rows (1,024 texel rows) cover it. With a limit of 3 MiB the division gives 192 and `std::bit_floor` lowers it to 128, so a run takes only 2 MiB. The power of two keeps staging buffers of few sizes, so that the pool finds one to use again.

### The differences from the toy

The toy asks one question per step, whether the budget fits. The real code asks four: the bytes, the time, the deadline and the staging room. It also records into a queue instead of counting, and it publishes only when everything is uploaded. The toy has no `FirstOfFrame` flag that the manager counts, no `AwaitingGPU`, and no second call after a rebuilt batch for the one case where a call without a budget ends `Pending`. Each addition answers a failure the toy cannot meet: a step that runs past the time, a texture that stalls the frame, or an asset that must wait for the card.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| One call uploads the whole asset | Small engines and tools | The simplest asset code | A stall of the length of the largest texture |
| A fixed cap of bytes per frame, no time | Many engines' streaming systems | A rule that is simple to explain | Steps that run past the time when the machine is slow |
| A worker thread records the uploads | Engines with a render thread | The main thread never pays for a copy | Locks and a second owner of every texture |
| Copies only on a :term[transfer queue]{id=transfer-queue} | Engines with an async copy path | Uploads fully beside the frame's work | A new answer for every device that lacks the queue |
| The graphics device handed to every asset | Early versions of many engines | No seam to maintain | An asset layer that cannot be tested without a device |

Strata keeps the budget in the call and lets the asset stop and continue. It pays with one more result in every finalize function: each asset must keep its own position between calls. For the places where each technique is described, see the further reading below.

## How it is tested

The suite `Asset.Finalize` in `StrataTests/src/Asset/AssetFinalizeTests.cpp` drives the contract with a fake upload context and no graphics device. One test checks that finalize calls record into the manager's context, that the manager opens one batch per update, and that the frames stay within the byte budget. It gives three assets of three steps of 1 MB a budget of 2 MB, and the frames upload 2, 2, 2, 2 and 1 MB.

Another test checks that past the deadline only the frame's first step goes: one step per frame and no second call. A third checks that an asset `AwaitingGPU` lets the arrivals behind it continue. Two more cover loads without a budget, each in a batch of its own, and a load that the open batch cannot take.

A separate suite, `Architecture.Layering`, checks the include rule of the layer table. Run the first suite directly with the line below, or all tests with `ctest`.

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=Asset.Finalize
```

The command runs only that suite and prints each failed check with the values it saw.

## Changing it safely

Adding an :term[asset type]{id=asset-type} that uploads in steps follows the contract above. Record into the context, size steps with the queue's planner, report the bytes, keep your position in the object, and answer `Pending` when the budget ends. The extension points are `Asset::FinalizeOnMainThread` and the planner `GPUUploadQueue::PlanStep`, which the texture and the mesh both call.

- **Never include a graphics header in `Strata/src/Strata/Asset/`.** The layering test fails the build, and the fix is an interface below the asset layer, not an entry in the allow list.
- **Report every byte.** An asset that uploads and does not add the bytes to `*UploadedBytes` lets the frame spend its budget twice, because the next call sees a budget that is too large.
- **Keep `Pending` for budget reasons.** Without a budget, a call may end `Pending` only when the open batch cannot take what it needs. One that ends `Pending` again in a batch of its own is broken, and the manager fails the load with an error.
- **Raise the importer's version when the uploaded bytes change.** A change to what a texture uploads is a change of the importer's output, which [texture cooking](texture-cooking.md) teaches, and the version number must change with it.
- **Check the staging figures when you change a budget.** Raising one budget without the others changes nothing while another limit binds first.

Before a commit run `Asset.Finalize`, `Architecture.Layering` and the GPU suites of the renderer, which use the real queue.

## Summary

- A step is at most 4 MiB and fits the bytes, the milliseconds and the time to the deadline that remain. The frame's first step always goes, so a 90 MiB texture arrives in about ten frames.
- An asset's finalize function records into the upload context and reports its bytes. Its answer, `Done`, `Pending`, `Failed` or `AwaitingGPU`, tells the manager whether to publish, continue, stop or move on.
- The staging bound limits the rate to about 28 MiB a frame, but with the defaults the 16 MiB, 2 ms and 4 ms budgets stop the work first, and a game cannot raise them.
- The asset layer includes no graphics API, so a fake context can drive the whole contract.
- To trace an upload, break in `Texture::FinalizeOnMainThread` and read the bytes each call reports.

## Check yourself

1. The frame may spend 2 ms on steps, the speed is 4 MiB per millisecond, and the first step of the call has taken 1 ms. The reserve is a tenth of the frame's time. How many MiB may the next step take at most, ignoring the byte budget and the granule?

   :::answer{tests="step-budget"}
   The time left is 2 - 1 - 0.2 = 0.8 ms, which buys 0.8 times 4 = 3.2 MiB. The limit of 4 MiB does not bind, so the time does. The granule would round the figure down to a whole number of 64 KiB.
   :::

2. A texture's call returns `Pending` in the middle of a frame. What does the manager do with it?
   - A. It discards the texture and loads it again.
   - B. It stops calling finalize functions for the frame, and the texture keeps its place in line for the next one.
   - C. It moves the texture behind the other arrivals.

   :::answer{tests="finalize-contract"}
   B. A is wrong because the texture keeps the levels it already uploaded. C is wrong because arrivals finish in order, so a stalled texture would otherwise be overtaken by smaller ones forever.
   :::

3. The staging bound is 32 MiB, one step is 4 MiB, and the byte budget is 40 MiB with the time not limiting. Which rate can the uploads reach at most in a frame?

   :::answer{tests="staging-bound"}
   The first step may use all 32 MiB and later steps use room of 28 MiB, so sustained uploads reach about 28 MiB a frame when the card runs each frame's copies in time. The 40 MiB budget would allow more. With the default budgets, the 16 MiB budget or the 2 ms of upload time binds first, so the figure would be 16 MiB at most.
   :::

4. Why does `Texture` treat the context as the renderer's own type, `RendererUploadContext`, and not use the interface alone?
   - A. The interface has no `Begin`.
   - B. The renderer's assets know the renderer's queue, which the asset layer's interface rightly does not show.
   - C. The asset layer includes :term[NVRHI]{id=nvrhi}.

   :::answer{tests="no-graphics-api"}
   B. The seam hides the queue from the asset layer, while the texture lives in the renderer and may know it. A is wrong because the interface has `Begin`. C is wrong because the asset layer includes no graphics header, which the layering test enforces.
   :::

5. A trace of a large texture shows a call that reports 0 bytes and ends `Pending`, in a frame that is not the first. What does it mean?

   :::answer{tests="trace-finalize"}
   The budget or the deadline left no room for a step, or the staging was still in flight. Only the frame's first step ignores the budget, so a later call may take nothing, and the next frame's first call continues.
   :::

6. Change the toy's frame budget to 3 MiB. How many frames does it print, and how many MiB does each upload?

   :::answer{tests="finalize-contract"}
   Three frames of 3 MiB. The first asset takes steps of 1 MiB while the sum stays within 3 MiB, so it finishes alone in a frame, and the loop stops because the frame's bytes reached the budget. Each of the three assets then fills one frame.
   :::

## Exercises

1. **Basic.** The frame may upload 16 MiB and spend 2 ms, the speed is 4 MiB per millisecond, and a texture has 24 MiB left. Compute the bytes of the first call's steps and the number of frames.

   :::answer[Worked solution]{tests="step-budget"}
   Step one takes 4 MiB (the limit) in 1 ms. Step two sees 2 - 1 - 0.2 = 0.8 ms, which buys 3.2 MiB, rounded to 3.1875 MiB at 64 KiB granules; it takes 0.8 ms. Step three sees nothing. The call uploads about 7.19 MiB, so 24 MiB take four frames, the last with a shorter call.
   :::

2. **Medium.** Run the finalize contract without a GPU: two assets of four 3 MiB steps, with frame budgets of 1, 2, 4, 8 and 16 MiB. Print the frames needed and the largest frame, and say when a frame exceeds its budget.

   :::answer[Worked solution]{tests="finalize-contract,step-budget" solution="sketches/assets-uploads-sweep.cpp"}
   The program is the toy with a sweep over budgets. A frame goes over its budget only when the budget is smaller than one step, because the frame's first step ignores it.

   ```cpp sketch="assets-uploads-sweep.cpp"
   #include <algorithm>
   #include <cstdint>
   #include <cstdio>
   #include <vector>

   constexpr uint64_t c_MiB = 1ull << 20;

   // The finalize contract without a GPU: a finalizer sees the bytes left of the frame and reports what it uploaded.
   struct Context
   {
   	uint64_t UploadBudget = 0;
   	bool FirstOfFrame = false;
   };

   class SteppedAsset
   {
   public:
   	SteppedAsset(uint32_t steps, uint64_t stepBytes)
   		: m_Steps(steps), m_StepBytes(stepBytes)
   	{
   	}

   	// Returns the bytes uploaded; Done tells whether the asset is complete.
   	uint64_t Finalize(const Context& context, bool& done)
   	{
   		uint64_t uploaded = 0;
   		while (m_Done < m_Steps)
   		{
   			const bool framesFirst = context.FirstOfFrame && uploaded == 0;
   			if (!framesFirst && uploaded + m_StepBytes > context.UploadBudget)
   				break;
   			uploaded += m_StepBytes;
   			m_Done++;
   		}
   		done = m_Done == m_Steps;
   		return uploaded;
   	}

   private:
   	uint32_t m_Steps;
   	uint64_t m_StepBytes;
   	uint32_t m_Done = 0;
   };

   int main()
   {
   	const uint64_t budgets[] = { 1 * c_MiB, 2 * c_MiB, 4 * c_MiB, 8 * c_MiB, 16 * c_MiB };
   	for (const uint64_t budget : budgets)
   	{
   		std::vector<SteppedAsset> queue(2, SteppedAsset(4, 3 * c_MiB));
   		size_t next = 0;
   		int frames = 0;
   		uint64_t largest = 0;
   		while (next < queue.size())
   		{
   			uint64_t uploaded = 0;
   			bool first = true;
   			while (next < queue.size() && (first || uploaded < budget))
   			{
   				bool done = false;
   				uploaded += queue[next].Finalize(Context { budget - std::min(uploaded, budget), first }, done);
   				first = false;
   				if (!done)
   					break;
   				next++;
   			}
   			largest = std::max(largest, uploaded);
   			frames++;
   		}
   		std::printf("budget %2llu MiB: %d frames, largest frame %2llu MiB%s\n", static_cast<unsigned long long>(budget / c_MiB), frames,
   			static_cast<unsigned long long>(largest / c_MiB), largest > budget ? " (over: the first step)" : "");
   	}
   	return 0;
   }
   ```

   ```text output-of="assets-uploads-sweep.cpp"
   budget  1 MiB: 8 frames, largest frame  3 MiB (over: the first step)
   budget  2 MiB: 8 frames, largest frame  3 MiB (over: the first step)
   budget  4 MiB: 8 frames, largest frame  3 MiB
   budget  8 MiB: 4 frames, largest frame  6 MiB
   budget 16 MiB: 2 frames, largest frame 15 MiB
   ```

   1. **Lines 29–30:** the same rule as the toy: the frame's first step ignores the budget.
   2. **Line 58:** a call is made while the frame's bytes are below the budget, or for the frame's first call.
   3. **Line 67:** the largest frame is kept, so the program can compare it with the budget.

   The budgets of 1 and 2 MiB print the mark for a frame over its budget, and the others do not.
   :::

3. **Hard.** Trace it yourself: find where a texture's finalize call ends `Pending` because the deadline has passed, and where it ends `Pending` because the copy of the CPU data would end after the deadline.

   :::answer[Worked solution]{tests="trace-finalize"}
   Both are in `Texture::FinalizeOnMainThread` in `Strata/src/Strata/Renderer/Texture.cpp`. The first is the early check of `FirstOfFrame` against `context.Deadline`, before the GPU texture is made. The second is after the upload, where the predicted time to free the CPU copy is compared with the time until the deadline. Put a breakpoint on each return and load a large texture: the first fires for later calls of a frame, the second for a call that finished its upload.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Asset/Asset.h`: `c_AssetUploadStepBytes`, `AssetFinalizeResult`, `AssetFinalizeContext`
- `Strata/src/Strata/Asset/AssetUploadContext.h`: `AssetUploadContext`, `IAssetGraphics`
- `Strata/src/Strata/Asset/AssetManager.cpp`: `AssetManagerBase::ProcessCompletions`, `AssetManagerBase::Update`
- `Strata/src/Strata/Asset/AssetResidency.h`: `UploadBytesPerFrame`, `UploadMsPerFrame`, `FinalizeMsPerFrame`, `StagingBytes`
- `Strata/src/Strata/Renderer/Texture.cpp`: `Texture::FinalizeOnMainThread`, `Texture::UploadLevels`
- `StrataTests/src/Asset/AssetFinalizeTests.cpp`: the suite `Asset.Finalize`

## Further reading

- NVIDIA developer blog on uploading resources in Vulkan: staging buffers and transfer queues (intermediate)
- The Vulkan specification chapter on queues and synchronization (advanced)
