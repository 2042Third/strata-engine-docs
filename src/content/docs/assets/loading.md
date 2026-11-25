---
id: assets/loading
title: "Loading without stalling"
description: "How Strata turns a handle into a loaded object while no frame waits: a queue, reads, decoding, generations and one publication point."
kind: internals
size: XL
tracks: [E]
needs: [assets/handles-meta, core/jobs]
time: 140
learn:
  - id: poll-contract
    text: explain what GetAsset returns in each state and why game code polls and never waits
  - id: trace-load
    text: trace a load through its stages and name the thread that runs each one
  - id: predict-order
    text: predict the order in which the streaming queue dispatches a list of requests
  - id: compute-backpressure
    text: compute how many loads the queue dispatches under its limit on bytes and reads
  - id: generations
    text: explain how generations discard stale completions and why a failed load stays failed
since: 0.3.0
status: final
---

A game needs thousands of assets, and each one must travel from a file to an object that the frame can use. The :term[asset manager]{id=asset-manager} does this travel: it takes a handle, finds the stored :term[bytes]{id=byte}, decodes them into an object, makes the object ready for drawing or playing, and hands it out. Its main promise is that no frame ever waits for it. It also survives a reload, a cancel, an eviction or a failure that arrives while a load is under way. It does not decide which assets are wanted, how much memory they may fill, or how the :term[graphics card]{id=gpu} receives them; other pages teach those.

## The problem and how engines solve it

Take a texture of 40 MB. A disk that reads 200 MB per second needs 200 ms for the bytes, and decoding adds about 30 ms. A frame at 60 :term[frames per second]{id=frame-rate} lasts 16.7 ms, so a program that waits for this texture loses about 14 frames. The player sees the picture freeze for almost a quarter of a second. One such texture is bad; a scene with hundreds of them could not be played.

### Three ways to wait for a file

The first way is to **block**. The game calls `Load`, the call returns when the object exists, and a loading screen hides the wait. The code is simple, because every call returns a finished object. The cost is that nothing may load while the game plays. An open world cannot stop the game each time the player walks toward a hill, and an editor cannot freeze when you click a file.

The second way is a **callback**. The game calls `Load(handle, callback)` and the call returns at once. A thread of the engine reads and decodes, and then calls the callback with the object. Frames continue.

The cost moves into the callback. It runs on another thread, so it may touch the scene while the :term[main thread]{id=main-thread} touches it too. If the engine posts it to the main thread instead, the callback still holds references to objects that may be gone when it runs. A load that is cancelled, reloaded or replaced still calls back, and every caller must handle that.

The third way is to **poll**. The game asks `GetAsset(handle)` every frame. The answer is the object if it is ready, and "not yet" (a :term[null pointer]{id=null-pointer}) if it is not. The first ask also starts the load.

No code runs on another thread on the caller's behalf, because the caller only reads an answer. Strata uses this third way. It costs a question per use per frame, and every place that uses an asset must handle null.

### A worked example in frames

Walk the 40 MB texture through the polling way. On frame 0 a mesh :term[renderer]{id=renderer} asks for it and gets null, and the manager queues the read. Frames 1 to 11 the renderer asks again, gets null, and draws with a fallback texture. Around frame 12 the read ends, and a worker decodes for about 2 frames.

On frame 14 the main thread finds the finished object, spends part of its budget of a few milliseconds to prepare it for the graphics card, and the next ask returns the texture. In all this time no frame took longer than usual.

### Two costs a fast reader must also pay

Reading in the background brings its own problem. Suppose a scene requests 1,000 textures of 40 MB in one frame. If the engine starts them all, it holds 40 GB of half-read and half-decoded data before the first finishes, and memory runs out. The answer is **backpressure**: refusing or slowing new work while too much is already pending. Strata applies it to bytes, not to a count of loads, because one load may be 4 KB and another 400 MB.

The second problem is change. While a load runs, the asset may be reloaded because its file changed, unloaded because memory ran short, or cancelled because the scene closed. When the load finishes, its result may be wrong for the world it arrives in. Every step that touches an asset must be able to tell that the result is out of date. The page returns to this with a counter called a generation.

## The map

Figure 1 follows one load in time. Each lane is a thread or a pool from the page on [the job system](../core/jobs.md). The load starts on the main thread, reads on an I/O thread, decodes on a worker, and ends on the main thread.

```mermaid caption="One load in time. The main thread asks and later finalizes, an I/O thread reads, and a worker decodes. A list of completions carries the result back to the main thread." alt="A sequence diagram with four lanes: the main thread, the waiting list, an I/O thread and a worker. The main thread asks for a load, and the waiting list dispatches it to the I/O thread. The I/O thread reads and queues the decoding. The worker decodes and leaves a completion, and the main thread later finalizes and publishes."
sequenceDiagram
    participant M as Main thread
    participant Q as Streaming queue
    participant I as I/O thread
    participant W as Worker
    M->>Q: GetAsset asks, RequestLoad queues
    Q->>I: Pump dispatches the read
    I->>I: ReadAssetData reads the stored bytes
    I->>W: Submit the decoding
    W->>W: the loader decodes the bytes
    W-->>M: PushCompletion leaves the result
    M->>M: Update finalizes and publishes
```

Figure 2 shows who owns what. `AssetManagerBase` owns a table of **entries**, one for each registered handle. An entry holds the asset's description (type, path and stored size), the loaded object, the state, the error text, the generation and more, all guarded by one :term[mutex]{id=mutex}. Two :term[subclasses]{id=derived-class} supply the bytes: `EditorAssetManager` reads project files and imports them, and `RuntimeAssetManager` reads an asset pack. Each overrides `ReadAssetData`.

```mermaid caption="The parts of a load. The manager's entries feed a queue, the queue feeds the I/O pool, the loader registry serves the workers, and a list of completions returns to the main thread." alt="A flow diagram from code that needs an asset, through the manager and its entries, the streaming queue, the I/O pool and the workers, to a list of completions that the main thread reads."
flowchart LR
    Caller["Code that needs an asset"] -->|GetAsset| Manager["AssetManagerBase and its entries"]
    Manager -->|RequestLoad| Queue["Streaming queue"]
    Queue -->|Pump| IO["I/O pool: reads bytes"]
    Source["EditorAssetManager or RuntimeAssetManager"] -.->|ReadAssetData| IO
    IO --> Workers["Worker pool: decodes"]
    Registry["Loader registry"] -.-> Workers
    Workers --> Done["Completion list in a shared LoadState"]
    Done -->|Update| Main["Main thread: finalize and publish"]
    Main --> Manager
```

A **loader** is a function, registered for one :term[asset type]{id=asset-type}, that turns the stored bytes of an asset into an `Asset` object. It runs on a worker and touches no engine state. The module that owns a type registers its loader at start-up; the page below shows the renderer's.

The **streaming queue** is the manager's list of waiting loads. It decides the order in which loads start, and how many may run at once. It knows nothing about files or decoding: it calls a function that the manager gives it, and the manager tells it when a read and a whole load have ended.

An **asset state** is the stage an asset is in: one of `Unloaded`, `Loading`, `Ready` and `Failed`. `Unloaded` means nothing is loaded and nothing is requested, and `Loading` means queued, read, decoded or waiting to be finalized. `Ready` means an object is loaded, and `Failed` means the last load ended with an error. Every entry has exactly one state.

To **finalize** an asset is to complete it on the main thread, after the worker decoded it. A texture or a mesh creates its graphics-card resources there, because only the main thread submits graphics work. The page on [uploads](uploads.md) teaches the budget that the finalize step works within.

## The contract

The manager's callers can rely on these rules, and must obey the ones that bind them. Each rule has its reason.

1. **`GetAsset` never blocks.** It returns the loaded object, or the previous object while a reload runs, or null. It marks the asset as used this frame and asks for the load when one is needed. The reason is the example above: a call that waited would put the disk's speed into the frame.
2. **Code handles "not loaded yet" every frame.** It draws a fallback or skips the work, and asks again next frame. It polls and never waits. The reason is that the answer changes without any callback: the object appears between two frames.
3. **Typed calls return null for a wrong type.** `GetAsset<T>(handle)` returns null for an invalid handle, for an asset that is not loaded, and for an asset of another type. The caller cannot get a texture object where it asked for a mesh.
4. **`PeekLoadedAsset` asks without requesting.** It starts no load and does not count as a use, so tools that watch streaming do not change it. Code that draws or plays an asset uses `GetAsset`, because only a request keeps the asset alive and loading.
5. **`LoadAssetSync` is for tools, tests and loading screens.** It waits on the main thread, and it never runs from a finalize function, because the completions it would wait for are the ones the finalize function is in the middle of handling. It logs an error and returns null there.
6. **Loaders run on workers.** They touch no engine state, may take the bytes over, and check `IsCancelled` when their work is long.
7. **Every load ends in exactly one completion.** The finalize step and publication happen on the main thread, and only there does an asset become `Ready` or `Failed`.

:::rule[Never block a frame on an asset]
The engine's `AGENTS.md` forbids blocking a frame on an asset: code must cope, in every frame, with an asset that has not loaded yet. The reason is rule 1: a wait puts file speed into a frame, and no budget can bound it. Code holds `AssetHandle` values across frames, not `Ref` objects, and asks again each frame.
:::

:::rule[Reach assets through the scene's manager]
Code that serves a scene gets its assets from `Scene::GetAssetManager()`, and calls no static function of `AssetManager`. At the pin the call returns the active manager, but the comment of `Scene::GetAssetManager` says per-scene managers are planned and would then change this one function and not the code that calls it.
:::

The first `GetAsset` of an asset is a request, and a request has a **priority**: a level and a score. The level is one of three: `High` for what is needed now (visible, or blocking gameplay), `Normal`, and `Low` for a prefetch, a load asked for before anything uses the asset. Within a level, a higher score goes first; a renderer may use how large the asset appears on screen. Asking again at a higher level or score raises a waiting request, and nothing ever lowers one.

A load is **in flight** from the moment the queue dispatches it until the manager has finalized or discarded it. It counts its bytes in flight the whole time, also while it waits for the main thread. A load that has been read and decoded still holds memory.

A **memory asset** is an asset that exists only in memory: built in, or made at run time, with no :term[stored form]{id=stored-form}. The manager finalizes it when you add it, it is `Ready` at once, and it is never dropped for memory, unloaded, reloaded or replaced.

To **publish** an asset is to make a finalized object the entry's loaded object and set the state to `Ready`, so that the next `GetAsset` returns it. Publication is the only way an object leaves the manager's private lists and reaches callers.

## A toy version

A toy manager makes the rules easier to see, because it shows four ways in which a simple one fails. It has a waiting list, one worker, a list of completions that the frame polls, and a generation counter. To keep the output the same on every run, the worker's steps run on the main thread, in turn; the real worker is a thread. The toy runs each scenario twice: with every guard off (the naive manager), and with every guard on.

:::question
The toy uses classes and containers. If they are new, read [the page on classes in C++](../basics/programming-3.md) and [the generic C++ page](../basics/cpp-generic.md) first.
:::

The program below keeps the four guards in a `Guards` :term[struct]{id=struct}. Search for the places where a guard changes a decision: `GetAsset` (is a request allowed), `StepWorker` (does a failure still complete), `Update` (is a completion still wanted) and `CanDispatch` (are the bytes too many).

```cpp sketch="assets-loading-toy.cpp"
// A toy asset manager: a waiting list, one worker, a completion list that the frame polls, and a generation counter.
// The worker's steps run on the main thread, in turn, so that the output is the same on every run.
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <deque>
#include <map>

namespace
{

	enum class State { Unloaded, Loading, Ready, Failed };

	const char* ToString(State state)
	{
		switch (state)
		{
			case State::Unloaded: return "Unloaded";
			case State::Loading:  return "Loading";
			case State::Ready:    return "Ready";
			case State::Failed:   return "Failed";
		}
		return "?";
	}

	struct Guards
	{
		bool CheckGeneration = true;     // Discard a completion whose load is no longer wanted
		bool OnlyWhenUnloaded = true;    // Start a load only from the Unloaded state
		bool CatchFailures = true;       // A load that fails still ends in a completion
		uint64_t MaxInFlightBytes = 128; // Megabytes; 0 means no limit
	};

	struct Entry
	{
		State Current = State::Unloaded;
		uint64_t Generation = 1;
		uint64_t Megabytes = 0;
		bool Broken = false;
	};

	struct Job { int Handle; uint64_t Generation; uint64_t Megabytes; bool Broken; };
	struct Completion { Job Source; bool Ok; };

	class ToyManager
	{
	public:
		explicit ToyManager(Guards guards)
			: m_Guards(guards)
		{
		}

		void Add(int handle, uint64_t megabytes, bool broken) { m_Entries[handle] = Entry { State::Unloaded, 1, megabytes, broken }; }

		bool GetAsset(int handle)
		{
			Entry& entry = m_Entries[handle];
			if (entry.Current == State::Ready)
				return true;
			if (!m_Guards.OnlyWhenUnloaded || entry.Current == State::Unloaded)
			{
				entry.Current = State::Loading;
				m_Waiting.push_back(Job { handle, entry.Generation, entry.Megabytes, entry.Broken });
				m_LoadsStarted++;
				Pump();
			}
			return false;
		}

		void Unload(int handle)
		{
			Entry& entry = m_Entries[handle];
			entry.Current = State::Unloaded;
			entry.Generation++;
		}

		void StepWorker()
		{
			if (m_Dispatched.empty())
				return;
			const Job job = m_Dispatched.front();
			m_Dispatched.pop_front();
			if (job.Broken && !m_Guards.CatchFailures)
				return; // The exception ended the job: no completion, and its bytes never leave the flight
			m_Completions.push_back(Completion { job, !job.Broken });
		}

		void Update()
		{
			while (!m_Completions.empty())
			{
				const Completion completion = m_Completions.front();
				m_Completions.pop_front();
				m_InFlightBytes -= completion.Source.Megabytes;
				m_InFlightLoads--;
				Entry& entry = m_Entries[completion.Source.Handle];
				if (m_Guards.CheckGeneration && entry.Generation != completion.Source.Generation)
					continue;
				entry.Current = completion.Ok ? State::Ready : State::Failed;
			}
			Pump();
		}

		State GetState(int handle) { return m_Entries[handle].Current; }
		uint64_t GetInFlightBytes() const { return m_InFlightBytes; }
		uint64_t GetPeakBytes() const { return m_PeakBytes; }
		uint32_t GetLoadsStarted() const { return m_LoadsStarted; }

	private:
		bool CanDispatch() const
		{
			return m_Guards.MaxInFlightBytes == 0 || m_InFlightLoads == 0 || m_InFlightBytes < m_Guards.MaxInFlightBytes;
		}

		void Pump()
		{
			while (!m_Waiting.empty() && CanDispatch())
			{
				m_InFlightBytes += m_Waiting.front().Megabytes;
				m_InFlightLoads++;
				m_PeakBytes = std::max(m_PeakBytes, m_InFlightBytes);
				m_Dispatched.push_back(m_Waiting.front());
				m_Waiting.pop_front();
			}
		}

		Guards m_Guards;
		std::map<int, Entry> m_Entries;
		std::deque<Job> m_Waiting;
		std::deque<Job> m_Dispatched;
		std::deque<Completion> m_Completions;
		uint64_t m_InFlightBytes = 0;
		uint64_t m_PeakBytes = 0;
		uint32_t m_InFlightLoads = 0;
		uint32_t m_LoadsStarted = 0;
	};

	void RunScenarios(const char* name, Guards guards)
	{
		std::printf("%s\n", name);

		ToyManager unloaded(guards);
		unloaded.Add(1, 10, false);
		unloaded.GetAsset(1);
		unloaded.Unload(1);
		unloaded.StepWorker();
		unloaded.Update();
		std::printf("  unloaded while loading: %s\n", ToString(unloaded.GetState(1)));

		ToyManager broken(guards);
		broken.Add(2, 10, true);
		broken.GetAsset(2);
		broken.StepWorker();
		broken.Update();
		std::printf("  broken file: %s, %llu MB in flight\n", ToString(broken.GetState(2)), static_cast<unsigned long long>(broken.GetInFlightBytes()));

		ToyManager asked(guards);
		asked.Add(3, 10, false);
		for (int system = 0; system < 3; system++)
			asked.GetAsset(3);
		std::printf("  three systems ask in one frame, loads started: %u\n", asked.GetLoadsStarted());

		ToyManager burst(guards);
		for (int handle = 10; handle < 20; handle++)
		{
			burst.Add(handle, 40, false);
			burst.GetAsset(handle);
		}
		std::printf("  ten 40 MB assets at once: %llu MB in flight at most\n", static_cast<unsigned long long>(burst.GetPeakBytes()));
	}

}

int main()
{
	RunScenarios("naive manager", Guards { false, false, false, 0 });
	RunScenarios("guarded manager", Guards {});
	return 0;
}
```

```text output-of="assets-loading-toy.cpp"
naive manager
  unloaded while loading: Ready
  broken file: Loading, 10 MB in flight
  three systems ask in one frame, loads started: 3
  ten 40 MB assets at once: 400 MB in flight at most
guarded manager
  unloaded while loading: Unloaded
  broken file: Failed, 0 MB in flight
  three systems ask in one frame, loads started: 1
  ten 40 MB assets at once: 160 MB in flight at most
```

1. **Lines 26-31:** the four guards, one for each failure the scenarios show.
2. **Lines 60-66:** `GetAsset` starts a load only from `Unloaded`; the naive one starts a load at every call that finds the asset not ready.
3. **Lines 83-85:** a failing job still pushes a completion; the naive worker returns early, and the entry never leaves `Loading`.
4. **Lines 97-98:** the completion handler compares generations and discards a result whose generation is old.
5. **Lines 110-113:** the dispatch check: with a limit, the toy dispatches while the bytes in flight are below it, and one load always runs.

Read the output as four lessons. The naive manager resurrects an asset: the player unloaded it while its load ran, and the old completion made it `Ready` again, with its memory held. It loses a failure: a broken file leaves the asset in `Loading` for ever and keeps 10 MB in flight, so the queue never gets that room back.

The naive manager also starts three loads when three systems ask in one frame, and it holds 400 MB in flight when ten assets arrive together. The guarded manager keeps 160 MB at most. Its fourth load starts at 120 MB in flight, which is below the limit of 128, and the fifth waits.

## The real code, in the order a load flows

The real manager has the same four guards and several more, because real loads also read files, prefetch, stream partially, wait for imports and finalize within budgets. The sections below follow one load and name each difference from the toy.

### Asking: `GetAsset` and `RequestLoad`

`GetAsset` is the function every caller uses. Search for what it does under the manager's lock and what it does after releasing it.

```cpp src="Strata/src/Strata/Asset/AssetManager.cpp#L330-L349"
Ref<Asset> AssetManagerBase::GetAsset(AssetHandle handle, AssetPriority priority)
{
	Ref<Asset> current;
	bool requestLoad = false;
	{
		std::scoped_lock<std::mutex> lock(m_Mutex);
		m_GetAssetCalls++;
		auto it = m_Entries.find(handle);
		if (it == m_Entries.end())
			return nullptr;
		TouchLocked(it->second);
		current = it->second.Loaded; // Also the previous version while a reload is in progress
		// A load that is still queued is raised to this priority, and the dependencies of an asset that was read while it
		// was only prefetched are prefetched now (RequestLoad).
		requestLoad = it->second.State == AssetState::Unloaded || it->second.State == AssetState::Loading || it->second.DependenciesDeferred;
	}
	if (requestLoad)
		RequestLoad(handle, priority);
	return current;
}
```

1. **Lines 337-339:** an unknown handle returns null without any state change.
2. **Line 341:** the object returned is `Loaded`, which still holds the previous version while a reload runs.
3. **Line 344:** a request is made when the asset is `Unloaded` or `Loading`, so that a queued load is raised to this priority, or when its dependencies still wait for a request.
4. **Lines 346-348:** the manager's lock is released before `RequestLoad`, because the queue's lock must never be taken inside it.

The toy had no lock order. In the real manager two locks exist, the manager's and the queue's, and `RequestLoad` shows how they stay apart.

```cpp src="Strata/src/Strata/Asset/AssetManager.cpp#L440-L484"
void AssetManagerBase::RequestLoad(AssetHandle handle, AssetPriority priority, float score)
{
	bool newRequest = false;
	bool loading = false;
	bool prefetchDependencies = false;
	uint64_t generation = 0;
	uint64_t loadBytes = 0;
	bool partial = false;
	{
		std::scoped_lock<std::mutex> lock(m_Mutex);
		auto it = m_Entries.find(handle);
		if (it == m_Entries.end() || it->second.IsMemoryAsset)
			return;
		AssetEntry& entry = it->second;
		TouchLocked(entry);
		// Requested now: its own dependencies are prefetched when it is read, or now if it was read while it was only
		// prefetched (see PrefetchDependencies).
		entry.PrefetchOnly = false;
		const bool deferred = std::exchange(entry.DependenciesDeferred, false);
		if (entry.State == AssetState::Unloaded)
		{
			SetStateLocked(entry, AssetState::Loading);
			entry.Error.clear();
			newRequest = true;
		}
		loading = entry.State == AssetState::Loading;
		prefetchDependencies = deferred && !newRequest && entry.State != AssetState::Failed;
		generation = entry.Generation;
		loadBytes = GetLoadBytesLocked(entry);
		partial = IsPartialLoadLocked(entry);
	}

	// The queue's lock is taken without the manager's: pumping dispatches, which takes the manager's lock.
	if (newRequest)
	{
		m_Queue.Enqueue(handle, priority, score, loadBytes, generation, partial);
		m_Queue.Pump();
	}
	else if (loading && m_Queue.Raise(handle, priority, score))
	{
		m_Queue.Pump();
	}
	if (prefetchDependencies)
		PrefetchDependencies(handle, priority);
}
```

1. **Lines 451-452:** an unknown handle, or a memory asset, is ignored; a memory asset has nothing to load.
2. **Lines 459-464:** only an `Unloaded` entry becomes `Loading`, and its old error text is cleared. This is the toy's second guard.
3. **Lines 467-469:** the generation and the load's size are read under the lock, so that the queue gets values that belong together.
4. **Lines 472-477:** the queue is called with only its own lock held; `Pump` may dispatch, and dispatching takes the manager's lock.
5. **Lines 478-481:** a load that is already `Loading` is raised and not queued twice.

### The queue: order and bounds

The queue keeps its waiting requests in a `std::map`, which visits its elements in key order, so the first element is always the next load to dispatch. The key is a `std::tuple` of three values.

```cpp src="Strata/src/Strata/Asset/AssetStreamingQueue.h#L116-L120"
private:
	// Ascending order is dispatch order: priority (High first), then score (highest first), then request order.
	using Key = std::tuple<uint8_t, float, uint64_t>;

	static Key MakeKey(AssetPriority priority, float score, uint64_t order) { return Key(static_cast<uint8_t>(priority), -score, order); }
```

The priority level is the first value, with `High` as 0, so a smaller number goes first. The score is stored with its sign flipped, so a higher score gives a smaller key and goes first within its level. The request order is the third value, a counter that grows with every new request, so equal requests go in the order they came. A request that is raised keeps its old order: it was first queued when it was queued. A score that is not a number counts as 0, so a bad value cannot break the order.

:::example[The order of six requests]
Six requests arrive in this order, each with a level and a score: Tree (`Low`, 0), Rock (`Normal`, 2), Door (`Normal`, 2), Sky (`High`, 0), Grass (`Normal`, 7) and Bush (`Normal`, -1). Their keys are (2, 0, 0), (1, -2, 1), (1, -2, 2), (0, 0, 3), (1, -7, 4) and (1, 1, 5). Sorted, the order is Sky, Grass, Rock, Door, Bush and Tree. Grass beats Rock and Door, because -7 is below -2; Rock beats Door, because its request order 1 is below 2.
:::

Dispatch is bounded by two limits. The manager sets them at every `Update` from its budgets. The bytes in flight stay below `128 MiB` by default, which is 128 times 1,048,576 bytes. The reads still running stay below twice the number of I/O threads, and the job system has 2 I/O threads by default, so 4 reads. The next quote holds both checks and the loop that applies them.

```cpp src="Strata/src/Strata/Asset/AssetStreamingQueue.cpp#L148-L207"
bool AssetStreamingQueue::CanDispatchLocked() const
{
	if (m_Closed || m_Waiting.empty())
		return false;
	// With nothing in flight one load always starts, however large: an asset above the limit must still load.
	if (m_InFlightLoads == 0)
		return true;
	return m_InFlightBytes < m_Limits.MaxInFlightBytes && m_OutstandingReads < std::max(1u, m_Limits.MaxOutstandingReads);
}

void AssetStreamingQueue::Pump()
{
	std::unique_lock<std::mutex> lock(m_Mutex);
	// Another pump is running (maybe further up this thread's stack, inside the dispatch function): it checks the
	// limits again under the lock after each dispatch, so it sees whatever made this pump necessary.
	if (m_Pumping)
		return;
	m_Pumping = true;
	while (CanDispatchLocked())
	{
		const AssetStreamingRequest request = m_Waiting.begin()->second;
		EraseLocked(m_Waiting.begin());
		m_InFlightLoads++;
		if (request.RangeId != 0)
			m_InFlightRanges++;
		m_OutstandingReads++;
		m_InFlightBytes += request.Bytes;
		m_InFlightBytesHighWater = std::max(m_InFlightBytesHighWater, m_InFlightBytes);
		m_Dispatched++;

		lock.unlock();
		// The dispatch function reports its own failures by returning false; an exception (allocation failure while
		// starting a job) must not leave the queue pumping forever.
		bool dispatched = false;
		try
		{
			dispatched = m_Dispatch(request);
		}
		catch (const std::exception& exception)
		{
			ST_CORE_ERROR("Starting the load of asset {} failed: {}", request.Handle.ToString(), exception.what());
		}
		catch (...)
		{
			ST_CORE_ERROR("Starting the load of asset {} failed with an unknown exception", request.Handle.ToString());
		}
		lock.lock();

		if (!dispatched)
		{
			m_InFlightLoads--;
			if (request.RangeId != 0)
				m_InFlightRanges--;
			m_OutstandingReads--;
			m_InFlightBytes -= request.Bytes;
			m_Dispatched--;
		}
	}
	m_Pumping = false;
}
```

1. **Lines 153-155:** with nothing in flight one load always starts, however large; otherwise both limits must hold, checked before the dispatch, so the bytes in flight reach the limit plus one asset.
2. **Lines 163-164:** a pump that is called while another one runs returns at once; the running one checks the limits again after each dispatch. This is why `Pump` never recurses, also when the dispatch function finishes a load before it returns.
3. **Lines 168-176:** the best request moves from the waiting map to the flight, and the counters change under the lock.
4. **Lines 178-194:** the dispatch function runs without the lock, and an exception inside it is logged and not allowed to leave the pump stuck.
5. **Lines 196-204:** a dispatch that returns false is undone: the load never started, so it leaves the flight.

:::why[A bound on bytes, not on count]
The queue limits bytes in flight and the reads that run, and never the count of waiting requests. A count of 8 loads is harmless for small meshes and fatal for eight 400 MB textures. The size of each load comes from the asset's stored size, or 1 MB when it is unknown. The cost of the choice is that the byte figure is an estimate: the decoded object may be larger than the stored form, and the limit does not count it.
:::

Figure 3 gives the decision. The one-load rule is the first test, and the two limits come after it.

```mermaid caption="The dispatch decision. A load always starts when none is in flight, and otherwise both the byte limit and the read limit must allow it." alt="A flow diagram of the dispatch decision. A request is sent at once if no load is in flight. Otherwise the bytes in flight and the running reads must both be below their limits, or the queue waits."
flowchart TD
    A["Waiting requests, best key first"] --> B{"Is any load in flight?"}
    B -->|no| G["Dispatch the best request"]
    B -->|yes| C{"Bytes in flight below the limit?"}
    C -->|no| W["Wait until a load finishes"]
    C -->|yes| D{"Running reads below the read limit?"}
    D -->|no| W
    D -->|yes| G
    G --> A
```

### Reading and decoding: `RunLoad`

`DispatchLoad` is the function the queue calls. It checks that the request still applies: an entry that is gone, has another generation, or is no longer `Loading` makes it return false, and the queue forgets the request. It then submits `RunLoad` to the I/O pool with `JobSystem::SubmitIO`, and the asset's priority becomes the job's priority. The manager counts the load in a shared `LoadState` first, and a submission that fails ends in a failed completion.

One more check comes before that. In the editor, the first import of an asset may still run, and there is nothing to read until it ends. The editor's manager answers `IsAwaitingImport` for such an asset. `DispatchLoad` marks the entry as waiting, returns false so that the load leaves the flight, and the entry stays `Loading`.

When the import is applied, `ResumeLoadsAwaitingImport` gives the entry a new generation and requests it again at the priority it had. The page on [importing](importing.md) teaches the import itself; the :term[runtime's]{id=runtime} manager never waits for one.

`RunLoad` has one rule above the others: every path ends in exactly one `PushCompletion`, also when code inside throws. Search for how the function keeps that rule, and for the place where the read ends and the decoding starts.

```cpp src="Strata/src/Strata/Asset/AssetManager.cpp#L583-L628"
void AssetManagerBase::RunLoad(const AssetMetadata& metadata, const AssetStreamingRequest& request)
{
	// Every path ends in exactly one PushCompletion, also when code inside throws (bad_alloc on huge assets, third-party
	// code), so in-flight counts always drain; the queue hears of the read's end exactly once before that.
	Ref<LoadState> loadState = m_LoadState;
	Completion completion { metadata.Handle, request.Generation, nullptr, {}, request.Bytes };
	bool readReported = false;
	auto finishRead = [this, &readReported]()
	{
		if (!readReported)
			m_Queue.OnReadFinished();
		readReported = true;
	};

	try
	{
		// A load cancelled after it was dispatched never reads, and one cancelled while it read is never decoded: its
		// completion is discarded when it is handled (its generation is stale).
		if (!IsLoadCurrent(metadata.Handle, request.Generation))
		{
			finishRead();
			PushCompletion(loadState, std::move(completion));
			return;
		}

		auto data = CreateRef<std::vector<uint8_t>>();
		std::string error;
		uint64_t storedSize = 0; // Of the whole stored form, when only a prefix was read
		const bool read = request.Partial ? ReadPrefix(metadata, *data, storedSize, &error) : ReadAssetData(metadata, *data, &error);
		// The asset will arrive: what it references starts loading now, alongside its decoding and finalization. Queued
		// before the read leaves its slot, so the pump that follows weighs the dependencies against what waits already.
		const bool current = read && IsLoadCurrent(metadata.Handle, request.Generation);
		if (current)
			PrefetchDependencies(metadata.Handle, request.Priority);
		finishRead();
		if (!read)
		{
			completion.Error = error.empty() ? std::string("Failed to read asset data") : error;
			PushCompletion(loadState, std::move(completion));
			return;
		}
		if (!current)
		{
			PushCompletion(loadState, std::move(completion));
			return;
		}
```

1. **Lines 587-595:** the completion is made first, and `finishRead` tells the queue that the read ended, at most once, whichever path runs.
2. **Lines 601-606:** a load that was cancelled after dispatch never reads; it pushes its completion at once, and the main thread discards it.
3. **Line 611:** the bytes come from the manager's own `ReadAssetData`, or from `ReadPrefix` when only the head of the stored form is wanted.
4. **Lines 614-617:** if the load is still wanted, its dependencies are prefetched now, alongside its decoding; the read frees its slot before the next dispatch weighs them.
5. **Lines 618-627:** a failed read, or a read that is out of date, pushes its completion and returns.

The second half moves to the worker pool. The read held an I/O thread; the decoding runs on a worker and does not.

```cpp src="Strata/src/Strata/Asset/AssetManager.cpp#L630-L671"
if (storedSize > 0)
	m_PartialLoads.fetch_add(1, std::memory_order_relaxed);
// The job asks the manager whether the load is still wanted: the manager outlives it, since it waits for every load in
// flight before it goes (WaitForInFlightLoads, which sets Closing first so that the job gives up instead of finishing).
JobSystem::Submit([manager = this, loadState, metadata, data, storedSize, completion]() mutable
{
	try
	{
		const AssetLoadFunction* loader = AssetLoaderRegistry::Find(metadata.Type);
		if (!loader)
		{
			completion.Error = fmt::format("No loader for asset type {}", AssetTypeToString(metadata.Type));
		}
		else
		{
			// The bytes are not needed after decoding: the loader may take them over.
			AssetLoadData loadData(*data, storedSize);
			loadData.SetCancelCheck([manager, &loadState, handle = metadata.Handle, generation = completion.Generation]()
			{
				return loadState->Closing.load(std::memory_order_relaxed) || !manager->IsLoadCurrent(handle, generation);
			});
			completion.LoadedAsset = (*loader)(metadata, loadData, &completion.Error);
			if (completion.LoadedAsset)
				completion.LoadedAsset->Handle = metadata.Handle;
			else if (completion.Error.empty())
				completion.Error = "Loader returned no asset";
		}
	}
	catch (const std::exception& exception)
	{
		completion.LoadedAsset = nullptr;
		completion.Error = fmt::format("Loading failed: {}", exception.what());
	}
	catch (...)
	{
		completion.LoadedAsset = nullptr;
		completion.Error = "Loading failed with an unknown exception";
	}
	data.reset(); // The stored bytes are not needed any more; finalization may wait for frames
	PushCompletion(loadState, std::move(completion));
}, ToJobPriority(request.Priority));
return;
```

1. **Lines 634-637:** the decoding is a second job, on the worker pool; the shared `LoadState` and the bytes are captured by value, so they stay alive after the manager's call returns.
2. **Lines 638-642:** the loader registry gives the function for the asset's type, and a missing loader is an error text, not a crash.
3. **Lines 646-651:** the loader gets the bytes in an `AssetLoadData` with a cancel check that asks whether the manager closes or the generation changed.
4. **Lines 658-667:** an exception becomes a failed load with an error text, and a loader that returns nothing is a failure too.
5. **Lines 668-669:** the stored bytes are released before the completion is pushed, because the finalize step may wait several frames.

`PushCompletion` lowers the in-flight count first and then appends the completion under the same lock, so a thread that waits for the count never hangs even if the append runs out of memory. The :term[destructor]{id=destructor} of the manager waits for every load in flight; it first sets a closing flag, so that the cancel check makes loaders stop.

### The loader registry and the renderer's loaders

The registry keeps one `AssetLoadFunction` for each asset type. A function receives the asset's description, an `AssetLoadData` holding the bytes, and a place for an error text. Registering a type again replaces its loader, and only at start-up. The registry is closed until `Engine::RegisterBuiltinModules` opens it, and a use before that fails a check. Each module registers the types it owns; the renderer registers textures, meshes, materials, fonts and colour lookups.

`AssetLoadData` gives the loader its bytes in two ways. A loader that wants a span reads it. A loader whose asset keeps the bytes calls `TakeBytes`, which moves the vector out and leaves the load data empty, instead of copying a large asset a second time. If the data was handed over read-only, `TakeBytes` copies. The test `Loaders take the stored bytes over when they are handed over, and copy them otherwise` checks both.

```cpp src="Strata/src/Strata/Renderer/RendererRegistration.cpp#L85-L118"
AssetLoaderRegistry::Register(AssetType::Texture, [](const AssetMetadata&, AssetLoadData& data, std::string* outError) -> Ref<Asset>
{
	const uint64_t storedSize = data.GetStoredSize();
	Ref<Texture> texture = Texture::Deserialize(data.TakeBytes(), storedSize, outError);
	if (texture && IsBlockCompressedFormat(texture->GetSpecification().Format) && !Texture::IsBlockCompressionSupported())
		return texture->Decompress(outError);
	return texture;
});
AssetLoaderRegistry::RegisterPrefix(AssetType::Texture, [](std::span<const uint8_t> head, uint64_t storedSize)
{
	return Texture::GetLoadPrefixSize(head, storedSize);
});
AssetManagerExtensionRegistry::Register([](AssetManagerBase& manager) -> Scope<AssetManagerExtension>
{
	return CreateScope<TextureStreamer>(manager);
});
AssetLoaderRegistry::Register(AssetType::Mesh, [](const AssetMetadata&, std::span<const uint8_t> data, std::string* outError) -> Ref<Asset>
{
	return Mesh::Deserialize(data, outError);
});
// Modules that collide with meshes (physics) read their triangles without knowing the renderer's Mesh.
MeshGeometryRegistry::Register(AssetType::Mesh, ReadMeshGeometry);
AssetLoaderRegistry::Register(AssetType::Material, [](const AssetMetadata&, std::span<const uint8_t> data, std::string* outError) -> Ref<Asset>
{
	return Material::Deserialize(data, outError);
});
AssetLoaderRegistry::Register(AssetType::Font, [](const AssetMetadata&, AssetLoadData& data, std::string* outError) -> Ref<Asset>
{
	return Font::Create(data.TakeBytes(), outError);
});
AssetLoaderRegistry::Register(AssetType::ColorLookup, [](const AssetMetadata&, std::span<const uint8_t> data, std::string* outError) -> Ref<Asset>
{
	return ColorLookup::Deserialize(data, outError);
});
```

1. **Lines 88-90:** the texture loader takes the bytes over; when the graphics device cannot sample a block-compressed format, the decoding of that format also runs here, on the loading worker.
2. **Lines 93-96:** a prefix function lets a first load of a texture read only its :term[header]{id=header} and its small mip levels; the texture streamer reads the finer ones later.
3. **Lines 101-104:** the mesh loader takes a span and copies what it needs, because the mesh keeps its own data.
4. **Lines 111-114:** a font keeps its file bytes, so its loader takes them over as well.

### Completions: stale ones discarded, good ones published

Back on the main thread, `Update` runs once per frame. It advances the frame number, refreshes the queue's limits, pumps the queue, and calls `ProcessCompletions` with the frame's budgets. The function swaps the shared list of completions into a local one under the lock, and handles them in order. A guard stops it from running again if a finalize :term[function calls]{id=function-call} it.

```cpp src="Strata/src/Strata/Asset/AssetManager.cpp#L1088-L1113"
while (!completions.empty())
{
	// The frame's first finalization always proceeds, so an asset larger than the budget still loads.
	if (applyBudget && processed > 0 && (uploadedBytes >= budgets.UploadBytesPerFrame || std::chrono::steady_clock::now() >= deadline))
		break;

	Completion& completion = completions.front();
	bool current = false;
	bool prefetched = false; // Requested by nobody yet: its finalization requests nothing (prefetches do not chain)
	{
		std::scoped_lock<std::mutex> lock(m_Mutex);
		auto it = m_Entries.find(completion.Handle);
		current = it != m_Entries.end() && it->second.Generation == completion.Generation;
		prefetched = current && it->second.PrefetchOnly;
		if (!current)
			m_Reserved -= completion.Reserved;
	}
	if (!current)
	{
		// Unregistered, unloaded, cancelled or reloaded since the request (also while its upload was under way):
		// discard. The load leaves the flight; the queue may dispatch the next one.
		processed++;
		m_Queue.OnLoadFinished(completion.InFlightBytes);
		completions.pop_front();
		continue;
	}
```

1. **Line 1091:** with a budget, the loop stops when the frame's bytes or time are used, but only after the first completion, so an asset larger than the budget still arrives.
2. **Lines 1098-1103:** the entry's generation is compared with the completion's; a different number also releases the memory reserved for it.
3. **Lines 1105-1112:** a stale completion is discarded, and `OnLoadFinished` takes its bytes out of the flight, so the queue dispatches the next load.

The lines between these two parts make room for an arrival in memory and wait for the graphics card, and the pages on [residency](residency.md) and [uploads](uploads.md) show them. The last part is what every arrival ends with.

```cpp src="Strata/src/Strata/Asset/AssetManager.cpp#L1219-L1246"
	// The load leaves the flight once it is handled, whatever becomes of it; the queue may dispatch the next one.
	m_Queue.OnLoadFinished(completion.InFlightBytes);
	Completion handled = std::move(completion);
	completions.pop_front();

	std::scoped_lock<std::mutex> lock(m_Mutex);
	m_Reserved -= handled.Reserved; // Counted as resident from now on, or not at all
	auto it = m_Entries.find(handled.Handle);
	if (it == m_Entries.end() || it->second.Generation != handled.Generation)
		continue;

	AssetEntry& entry = it->second;
	if (handled.LoadedAsset)
	{
		released.push_back(SetLoadedLocked(entry, handled.LoadedAsset));
		SetStateLocked(entry, AssetState::Ready);
		entry.Error.clear();
		PublishContentChange(handled.Handle);
	}
	else
	{
		SetStateLocked(entry, AssetState::Failed);
		entry.Error = handled.Error;
		ST_CORE_ERROR("Failed to load asset '{}' ({}): {}", entry.Metadata.Path.empty() ? entry.Metadata.Name : entry.Metadata.Path,
			entry.Metadata.Handle.ToString(), handled.Error);
	}
	m_TotalLoadsCompleted++;
}
```

1. **Line 1220:** the load leaves the flight once it is handled, whatever becomes of it.
2. **Lines 1226-1228:** the generation is checked a second time under the lock, because the finalize step ran without it and may have lasted frames.
3. **Lines 1231-1237:** publication: the object becomes the entry's, the state `Ready`, the error text is cleared, and a content change is published.
4. **Lines 1238-1244:** a failure sets `Failed`, keeps the error text and logs it with the asset's path and handle.

### Generations and the state machine

A **generation** is a number on each entry, taken from one counter of the manager, that grows whenever its current load stops being the one that counts. Reloads, unloads, cancels, replacements and loads that resume after an import all grow it. Each request carries the generation it was made under. A step that holds a request compares it with the entry's, and a different number means "out of date: drop it". The queue, `DispatchLoad`, `RunLoad`, the cancel check and both parts of `ProcessCompletions` all compare, so no step has to know why a result is stale.

Figure 4 shows the states and what moves an entry between them.

```mermaid caption="The four states of an asset. A request starts a load, a published arrival makes the asset ready, a failure keeps it failed, and a reload, an unload or an eviction returns it to unloaded." alt="A state diagram with four states. A request moves unloaded to loading, and loading ends as ready or failed. Cancel, unload, eviction and reload lead back to unloaded."
stateDiagram-v2
    [*] --> Unloaded
    Unloaded --> Loading: request
    Loading --> Ready: arrival published
    Loading --> Failed: read, decode or finalize failed
    Loading --> Unloaded: cancelled or unloaded
    Ready --> Unloaded: unload, eviction or reload
    Failed --> Unloaded: reload or unload
```

Three functions bump the generation. `ReloadAsset` keeps serving the old object while the new one loads, and the next quote shows how.

```cpp src="Strata/src/Strata/Asset/AssetManager.cpp#L739-L763"
void AssetManagerBase::ReloadAsset(AssetHandle handle)
{
	bool wasRequested = false;
	{
		std::scoped_lock<std::mutex> lock(m_Mutex);
		auto it = m_Entries.find(handle);
		if (it == m_Entries.end() || it->second.IsMemoryAsset)
			return;

		AssetEntry& entry = it->second;
		wasRequested = entry.State != AssetState::Unloaded;
		AbandonLoadLocked(entry); // A queued load of the old version is replaced by the new request
		// Keep serving the old object until the new one is ready, so users never see the asset disappear.
		SetStateLocked(entry, AssetState::Unloaded);
		entry.Generation = m_NextGeneration++;
		entry.SourceRevision = NextSourceRevision();
		// Without a loaded object the change is published now: unless the asset is requested, no arrival will tell caches
		// that keep data derived from it (evicted meshes' render layouts) that its source changed.
		if (!entry.Loaded)
			PublishContentChange(handle);
	}

	if (wasRequested)
		RequestLoad(handle, AssetPriority::High);
}
```

1. **Lines 749-750:** a queued or running load of the old version is abandoned, so the new request replaces it.
2. **Lines 752-754:** the state becomes `Unloaded` but `Loaded` stays, so `GetAsset` continues returning the old object; the generation and the source revision change.
3. **Lines 757-758:** an asset with no object publishes its content change at once, because no arrival will tell the caches.
4. **Lines 761-762:** only an asset that was requested is requested again, at `High`.

Eviction drops an asset because memory ran short, and a pinned asset is one that code has marked to stay loaded; the page on [residency](residency.md) teaches both. `UnloadAsset` drops the object, abandons the load and bumps the generation; it unloads pinned assets too, because pins only protect from eviction. `CancelLoad` abandons a load that has not finished and returns false for a pinned asset; an asset that was being reloaded returns to `Ready` with its old object, and any other goes to `Unloaded`. Memory assets can be neither unloaded nor reloaded.

A failed load stays failed. `RequestLoad` starts a load only from `Unloaded`, and `GetAsset` asks for a load only in `Unloaded` and `Loading`. So for a `Failed` asset, `GetAsset` returns null every frame and starts nothing, and the manager does not try again by itself. The error text is kept: `GetAssetError` returns it, and the command `asset.info` shows it as `loadError`. Only `ReloadAsset` or `UnloadAsset` make the entry `Unloaded` again; registering the handle again keeps its state, and only an entry removed with `UnregisterAsset` starts fresh when it is registered later.

In the editor a changed :term[source file]{id=source-file} or a re-import calls `ReloadAsset`. In a game only `RuntimeAssetManager::Mount` calls it, for the assets that a newly mounted pack replaces, so a broken asset of the game's pack stays broken until the program ends.

:::why[A failure that is not tried again]
Trying again every frame would read a broken file 60 times per second, log an error each time, and hide the one fact worth knowing. A failure is a fact about the file, and the file changes only when the editor changes it or a game mounts a pack over it. The cost is that a failure caused by a short fault, such as a drive that was busy, also stays. In a shipped game the pack is read-only, so that case is rare.
:::

Every asset type derives from `Asset`, and its few :term[virtual functions]{id=virtual-function} are the contract between the manager and a type.

```cpp src="Strata/src/Strata/Asset/Asset.h#L161-L193"
// Base class of every asset. Assets are shared (Ref<Asset>) and identified by their handle; code holds handles
// and asks the asset manager for the current object, which allows hot reload and streaming to replace objects.
class Asset
{
public:
	virtual ~Asset() = default;

	virtual AssetType GetType() const = 0;

	// Called on the main thread once the asset has been loaded, before it becomes Ready. GPU assets create their
	// GPU resources here and report what they uploaded (AssetFinalizeContext::UploadedBytes); assets referencing others
	// may request them from the context's manager. Must not block on other loads (no LoadAssetSync). Large uploads may
	// be split over several calls within the context's budget (Pending); a call with an unlimited budget finishes.
	virtual AssetFinalizeResult FinalizeOnMainThread(const AssetFinalizeContext&) { return AssetFinalizeResult::Done; }

	// Approximate memory held by the asset, per pool. Asset managers read it once the asset is finalized (for
	// residency budgets, upload budgets and statistics), so it must describe the asset's state from then on.
	virtual AssetMemoryUsage GetMemoryUsage() const { return {}; }
	// What GetMemoryUsage will report once the asset is finalized, asked before finalizing: managers make room for it in
	// their budgets first, so its memory is allocated after what it replaces was freed. Assets whose finalization moves
	// data between pools (CPU pixels to a GPU texture) override it.
	virtual AssetMemoryUsage GetFinalizedMemoryUsage() const { return GetMemoryUsage(); }

	// Whether objects outside the asset share its data, so that dropping the asset would free nothing (a playing
	// voice holds an audio clip's samples). Residency management keeps such assets resident.
	virtual bool IsDataShared() const { return false; }

	// For assets that can be partly resident (textures streaming their mip levels): how much of it is. False for the
	// others. Any thread.
	virtual bool GetDetailLevels(AssetDetailLevels&) const { return false; }

	AssetHandle Handle = UUID::Null();
};
```

1. **Line 168:** the type, which the typed `GetAsset<T>` calls compare.
2. **Line 174:** `FinalizeOnMainThread` runs on the main thread before the asset becomes `Ready`; the default does nothing and returns `Done`. It must not block on another load.
3. **Lines 178-182:** the memory an asset holds, per pool, and what it will hold once finalized, so that the manager makes room first.
4. **Line 186:** an asset whose data others share is never dropped for memory, since dropping it would free nothing.
5. **Line 192:** the handle the manager writes when it loads the object.

### The manager's other entry points

**Source revisions.** A **source revision** is a number from one process-wide counter that names the version of an asset's source. It changes when the asset is registered, at every `ReloadAsset`, and when a memory asset is added again. `GetSourceRevisions` returns two: `Current`, and `Loaded`, the revision the loaded object was read from. A cache that keeps data derived from an asset, even while the asset is dropped from memory, compares them to learn that its data is out of date.

A **content version** is a counter of the manager that grows whenever an asset object is published, replaced or dropped. `GetContentChanges(since, handles)` appends the handles that changed after a version, which is a change list for caches. The manager remembers the latest 4,096 changes; when a cache asks for an older version, the call returns false and the cache checks everything again. A separate version of the asset table changes when assets are registered, removed or moved, so caches of names and paths can check cheaply whether to refresh.

**Synchronous loads and the waiting helpers.** `LoadAssetSync` is the function the contract named for tools. It requests the load at `High` and then handles completions itself until the entry is `Ready`, `Failed` or `Unloaded`.

```cpp src="Strata/src/Strata/Asset/AssetManager.cpp#L388-L424"
Ref<Asset> AssetManagerBase::LoadAssetSync(AssetHandle handle)
{
	if (m_ProcessingCompletions)
	{
		// The completions this would wait for are being finalized by the caller: waiting would never end.
		ST_CORE_ERROR("LoadAssetSync called while finalizing assets (from Asset::FinalizeOnMainThread); request the load instead");
		return nullptr;
	}

	RequestLoad(handle, AssetPriority::High);
	while (true)
	{
		{
			std::scoped_lock<std::mutex> lock(m_Mutex);
			auto it = m_Entries.find(handle);
			if (it == m_Entries.end() || it->second.State == AssetState::Failed)
				return nullptr;
			if (it->second.State == AssetState::Ready)
				return it->second.Loaded;
			if (it->second.State == AssetState::Unloaded)
				return nullptr;
			if (it->second.AwaitingImport)
			{
				// Its import is applied between frames (the subclass's Update), which waiting here would never reach.
				ST_CORE_WARN("'{}' is still importing: it cannot be loaded synchronously yet", it->second.Metadata.Path.empty() ? handle.ToString()
					: it->second.Metadata.Path);
				return nullptr;
			}
		}

		if (ProcessCompletions(false) == 0)
		{
			std::unique_lock<std::mutex> lock(m_LoadState->Mutex);
			m_LoadState->Condition.wait_for(lock, std::chrono::milliseconds(1), [this]() { return !m_LoadState->Completions.empty(); });
		}
	}
}
```

1. **Lines 390-395:** inside a finalize function it refuses, logs an error and returns null: the completions it would wait for are the ones being handled.
2. **Lines 403-408:** unknown, `Failed` and `Unloaded` end the wait with null, and `Ready` returns the object.
3. **Lines 409-415:** an entry that waits for its first import ends the call with a warning, because the import is applied between frames and the loop would never see it.
4. **Lines 418-422:** the loop processes completions without a budget, and sleeps up to 1 ms on a :term[condition variable]{id=condition-variable} when there are none.

`WaitForPendingLoads(timeout)` does the same for the whole manager: it finalizes loads until none is queued, in flight or waiting, or until the timeout (30 seconds by default) passes, and returns whether the manager is idle. `HasPendingLoads` asks without waiting. Both belong on the main thread, and neither belongs in per-frame game code. A test uses them to wait for the 64 loads of its pack; a loading screen would call one while it draws progress.

**Replacing a loaded object.** `ReplaceLoadedAsset` makes a ready object the asset's at once, so an edit shows in the same frame. The editor publishes a material this way while the value is dragged, and after saving it.

```cpp src="Strata/src/Strata/Asset/AssetManager.cpp#L801-L831"
// Finalized like an arrival without a budget, in a batch of its own (main thread only, and no other batch is open: the
// finalization of completions is not running).
asset->Handle = handle;
AssetUploadContext* upload = GetUploadContext();
if (upload)
	upload->Begin();
uint64_t uploadedBytes = 0;
AssetFinalizeContext context { upload, this };
context.UploadedBytes = &uploadedBytes;
const AssetFinalizeResult result = asset->FinalizeOnMainThread(context);
if (upload)
	upload->Submit();
if (result != AssetFinalizeResult::Done)
	return fail("The asset could not be finalized");

Ref<Asset> released; // Released after the lock: destroying assets may be slow
std::scoped_lock<std::mutex> lock(m_Mutex);
m_FrameUploadedBytes += uploadedBytes;
auto it = m_Entries.find(handle);
if (it == m_Entries.end())
	return fail(fmt::format("Asset {} was unregistered while it was finalized", handle.ToString()));
AssetEntry& entry = it->second;
if (AbandonLoadLocked(entry))
	m_Cancellations++;
released = SetLoadedLocked(entry, asset);
SetStateLocked(entry, AssetState::Ready);
entry.Error.clear();
entry.Generation = m_NextGeneration++; // A load still in flight is discarded when it completes
TouchLocked(entry);
PublishContentChange(handle);
return true;
```

1. **Lines 803-812:** the object is finalized here without a budget, in a batch of its own; the function is meant for small documents.
2. **Lines 813-814:** an object that does not finalize changes nothing.
3. **Lines 823-825:** a load in flight is abandoned and the object is set as `Loaded`.
4. **Lines 826-830:** the state is `Ready`, the generation changes so that a load still in flight is discarded when it completes, and a content change is published.

The function refuses an unknown handle, a memory asset, an object of another type, and a call from a finalize function. `AddMemoryAsset` works like it for new entries: the object is finalized in the call, the entry is `Ready` with a new source revision, and the path index learns its path.

**The active manager.** The project sets one active manager, `AssetManager::SetActive`, and the static functions of `AssetManager` (`GetAsset<T>`, `PeekLoadedAsset<T>`, `LoadAssetSync<T>`, `GetAssetState`) forward to it, and return null without one. `Scene::GetAssetManager()` returns that manager at the pin. Engine code that works for a scene calls the scene's function, so that the manager is something the code was handed and not something it finds.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Blocking loads behind a loading screen | Unity's resource loading that blocks the caller; many games load a level this way | Code that always gets a finished object, and no states to handle | Streaming: the world could not grow while the player plays, and the editor would freeze on a click |
| Background loads with a callback | Unreal Engine's asynchronous asset loading takes a delegate that runs when the load ends | Code that runs at the moment the asset arrives, with no per-frame question | One more thread-safety rule for every callback, and cancel and reload cases in every caller |
| Futures that complete on arrival | Application code built on `std::future` | Code that reads top to bottom, as if it waited | A promise per load, a wait that is hard to bound, and no natural place for the previous object during a reload |
| A fixed count of concurrent loads | Simple loaders with a :term[thread pool]{id=thread-pool} of N | Less to build: no sizes to estimate | A 400 MB asset counts like a 4 KB one, so memory has no bound or the pipeline idles |
| A priority heap with a decrease-key operation | Textbook :term[priority queues]{id=priority-queue} | Cheaper raises for very long queues | Simplicity: the :term[ordered map]{id=ordered-map} gives the best element, a raise and a cancel with a plain erase and insert |

Godot's `ResourceLoader` offers threaded loading that the caller polls with a status call, which is close to Strata's way. The sources are in Further reading.

## How it is tested

Two suites hold the rules. `Asset.StreamingQueue` (file `StrataTests/src/Asset/StreamingQueueTests.cpp`) tests the queue alone, with a recording dispatch function. One test queues six requests of mixed levels and scores, one of them a score that is not a number, and checks the dispatch order `3, 6, 4, 2, 5, 1`.

Others check that a raise never lowers a request and that cancelled requests never dispatch. More check that a repeated request replaces a waiting one unless it is of a later generation, and that the bytes in flight stay below the limit plus one asset. A test with 200 latched reads of 8 MB and a limit of 64 MB checks the bound under load. The test `The queue is thread-safe` hammers the queue from several threads.

The `Asset` suite (file `StrataTests/src/Asset/AssetTests.cpp`) tests the manager. `Assets load asynchronously on the job system` requests 64 assets at three priorities, checks that every `GetAsset` returns null at once, waits, and checks that all are `Ready`; it destroys the manager with loads in flight. `Reloading keeps serving the old object until the new one is ready` and `Replacing a loaded asset publishes the new object at once` test the generation rules. The content-version tests check the counters and the change list. Run them directly with doctest filters.

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=Asset.StreamingQueue
```

The command runs the queue's suite only, in a Debug build made with the steps of [your first change](../core/first-change.md). The test `A Low request raised to High overtakes 50 queued Normal requests` is a good one to read first. It closes a gate so that reads wait, raises one request with `GetAsset` at `High`, and checks that it is read before the 50 queued ahead of it.

## Changing it safely

The extension points are the loader registry and the two functions a manager subclass supplies. A new asset type registers a loader in its module, and a new place for bytes overrides `ReadAssetData`. The queue and the completion path are not extension points; each line there guards a failure.

- Never block in code that runs every frame. Use `GetAsset`, handle null, and hold handles across frames. The engine's `AGENTS.md` states the rule, and the contract above gives its reason.
- Keep every path of `RunLoad` ending in exactly one `PushCompletion` and at most one `OnReadFinished`. A path that adds a second, or none, breaks the counts of loads in flight, and the queue stalls or dispatches too much.
- Compare the generation at every step that holds a request across a gap in time. A new step that skips the comparison writes a stale result into a live entry.
- Never call `LoadAssetSync` or `ReplaceLoadedAsset` from `FinalizeOnMainThread`, and never let a loader touch engine state: it runs on a worker.
- Keep the one-load-always rule in `CanDispatchLocked`: without it, an asset above the byte limit never loads.
- A loader of a large document asks `AssetLoadData::IsCancelled` as it goes, and returns no asset when it is true.

Run the `Asset` and `Asset.StreamingQueue` suites before a commit, and the stress tests of the asset layer when you change dispatch or completion. A change that alters the order of locks needs a run under a thread checker as well, because a :term[deadlock]{id=deadlock} between the manager's lock and the queue's lock shows only under load.

## Summary

- `GetAsset` never blocks: it returns the loaded object, the previous object during a reload, or null, stamps the request and asks for the load. Code polls every frame and never waits; `LoadAssetSync` is for tools, tests and loading screens.
- A load flows from the main thread through the streaming queue to an I/O thread that reads and a worker that decodes. A completion list carries it back to the main thread, which finalizes and publishes.
- The queue orders requests by level, score and request order. It dispatches while the bytes in flight stay under `128 MiB` and the reads under two per I/O thread, and one load always runs.
- A generation on each entry makes every step discard a result that is out of date; every load ends in exactly one completion, also when its code throws.
- A failed load stays `Failed` with its error text, and `GetAsset` returns null every frame without trying again, until `ReloadAsset` or `UnloadAsset` makes it `Unloaded`.

## Check yourself

1. An asset is `Ready` and `ReloadAsset` has run a moment ago. What does `GetAsset` return until the new version is published? (a) null, because the state is `Unloaded` (b) the previous object, because `Loaded` is kept (c) it blocks until the new object exists.

   :::answer{tests="poll-contract"}
   Option (b) is right. The state is `Unloaded` and the load is requested again, but the entry's `Loaded` is not cleared, and `GetAsset` returns it. Option (a) confuses the state with the object. Option (c) breaks the rule that `GetAsset` never blocks.
   :::

2. A load of a texture starts from a call to `GetAsset` in the frame. Which thread runs each of these: the queue's dispatch decision, the read of the file, the loader, the finalize step?

   :::answer{tests="trace-load"}
   The first dispatch decision is made by `Pump` on the thread that called `GetAsset`, the main thread; a later one runs on whichever thread ends a read or a load. The read runs on an I/O thread, the loader on a worker, and the finalize step on the main thread inside `Update`.
   :::

3. Three requests wait: A (`High`, score 1, order 0), B (`High`, score 5, order 1) and C (`Normal`, score 9, order 2). In which order does the queue dispatch them?

   :::answer{tests="predict-order"}
   The order is B, A, C. Level comes first, so C is last despite its score. Within `High`, the score 5 of B beats the score 1 of A, so the order of requests matters only for equal scores.
   :::

4. Three loads of 60 MB wait, and a fourth of 70 MB. The limit on bytes is 128 MiB and nothing is in flight. How many loads does one `Pump` dispatch, and how many bytes are in flight then? Take 1 MiB as 1 MB.

   :::answer{tests="compute-backpressure"}
   The first load starts because none is in flight (60 MB). The second starts because 60 is below 128 (120 MB). The third starts because 120 is below 128 (180 MB). The fourth waits, since 180 is not below 128. So 3 loads and 180 MB, assuming the read limit allows 3 reads.
   :::

5. A load under generation 4 is in flight when the asset is unloaded and requested again. What happens when the first load's completion reaches `ProcessCompletions`, and what state does the entry have then?

   :::answer{tests="generations"}
   The unload gave the entry a new number from the manager's counter, which only grows, so it is larger than 4 and the old completion's 4 does not match. The completion is discarded, `OnLoadFinished` takes its bytes from the flight, and the entry stays `Loading` until the new load's completion arrives.
   :::

## Exercises

1. **Basic.** Six requests arrive in this order: A (`Low`, 0), B (`Normal`, 0), C (`High`, 3), D (`Normal`, 4), E (`High`, 3), F (`Normal`, 0). Write the dispatch order and say which pair is ordered by request order.

   :::answer[Worked solution]{tests="predict-order"}
   The keys are A (2, 0, 0), B (1, 0, 1), C (0, -3, 2), D (1, -4, 3), E (0, -3, 4) and F (1, 0, 5). Sorted: C, E, D, B, F, A. C and E have equal levels and scores, so request order puts C first; B and F tie the same way.
   :::

2. **Medium.** Trace it yourself. Put breakpoints in `AssetManagerBase::RequestLoad`, `AssetManagerBase::RunLoad`, the loader of a texture in `RendererRegistration.cpp`, and `AssetManagerBase::ProcessCompletions`. Run a Debug editor and open a texture. For each stop, note the thread in the debugger's threads window, and say which stage it is.

   :::answer[Worked solution]{tests="trace-load"}
   `RequestLoad` in `Strata/src/Strata/Asset/AssetManager.cpp` stops on the main thread, which queues the load and pumps. `RunLoad` stops on an I/O thread, where `ReadAssetData` reads. The texture loader in `Strata/src/Strata/Renderer/RendererRegistration.cpp` stops on a worker, started by `JobSystem::Submit` from `RunLoad`. `ProcessCompletions` stops on the main thread inside `Update`, where the finalize step and publication happen. If the queue was full, `RunLoad` for the asset may start later, from a `Pump` that an I/O thread called after its read.
   :::

3. **Medium.** Write a complete program with the queue's key: a `std::map` from a `std::tuple` of priority, score with its sign flipped and request order to a request. Add the six requests below, raise Rock to level 0 with score 0, and print the dispatch order. Compare with the example in the real code.

   :::answer[Worked solution]{tests="predict-order" solution="sketches/assets-loading-order.cpp"}
   The key sorts by level, then by the score with its sign flipped, then by order. A raise erases the entry and inserts it under the new key with its old order, so Rock sorts before Sky.

   ```cpp sketch="assets-loading-order.cpp"
   // The streaming queue's order: a map keyed by priority, negated score and request order. Raising a waiting request
   // erases it and inserts it again under a better key, with its old request order.
   #include <cstdint>
   #include <cstdio>
   #include <map>
   #include <string>
   #include <tuple>

   namespace
   {

   	using Key = std::tuple<uint8_t, float, uint64_t>;

   	struct Request
   	{
   		std::string Name;
   		uint8_t Priority;
   		float Score;
   		uint64_t Order;
   	};

   	Key MakeKey(const Request& request)
   	{
   		return Key(request.Priority, -request.Score, request.Order);
   	}

   	class Queue
   	{
   	public:
   		void Enqueue(const std::string& name, uint8_t priority, float score)
   		{
   			const Request request { name, priority, score, m_NextOrder++ };
   			m_Waiting.emplace(MakeKey(request), request);
   		}

   		void Raise(const std::string& name, uint8_t priority, float score)
   		{
   			for (auto it = m_Waiting.begin(); it != m_Waiting.end(); ++it)
   			{
   				if (it->second.Name != name)
   					continue;
   				Request request = it->second;
   				const bool better = priority < request.Priority || (priority == request.Priority && score > request.Score);
   				if (!better)
   					return;
   				request.Priority = priority;
   				request.Score = score;
   				m_Waiting.erase(it);
   				m_Waiting.emplace(MakeKey(request), request);
   				return;
   			}
   		}

   		void PrintDispatchOrder() const
   		{
   			for (const auto& [key, request] : m_Waiting)
   				std::printf("%s ", request.Name.c_str());
   			std::printf("\n");
   		}

   	private:
   		std::map<Key, Request> m_Waiting;
   		uint64_t m_NextOrder = 0;
   	};

   }

   int main()
   {
   	Queue queue;
   	queue.Enqueue("Tree", 2, 0.0f);
   	queue.Enqueue("Rock", 1, 2.0f);
   	queue.Enqueue("Door", 1, 2.0f);
   	queue.Enqueue("Sky", 0, 0.0f);
   	queue.Enqueue("Grass", 1, 7.0f);
   	queue.Enqueue("Bush", 1, -1.0f);
   	queue.Raise("Rock", 0, 0.0f);
   	queue.PrintDispatchOrder();
   	return 0;
   }
   ```

   ```text output-of="assets-loading-order.cpp"
   Rock Sky Grass Door Bush Tree 
   ```

   1. **Line 24:** the key flips the sign of the score, so that a higher score gives a smaller key.
   2. **Lines 43-50:** a raise changes the level or score only when the request improves, and keeps its order.
   :::

4. **Hard.** The byte limit is 128 MiB, and the read limit never binds. Five assets of 50 MB wait, then one of 300 MB; nothing finalizes in the frame. How many loads are in flight after the pumps? Then the three in flight finalize in one `Update`: which loads start, in what order, and how many bytes are in flight at the end?

   :::answer[Worked solution]{tests="compute-backpressure"}
   The first load starts (50 MB), the second (100) and the third (150). The fourth stops, because 150 is not below 128. So 3 loads are in flight, with two small ones and the large one waiting.

   Each load that finalizes calls `OnLoadFinished`, which pumps. The first finish leaves 100, below 128, so the fourth starts (150). The second finish leaves 100 again, so the fifth starts (150). The third leaves 100, so the 300 MB load starts. Then 400 MB are in flight: 100 below the limit, plus the largest asset.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Asset/AssetManager.h` and `AssetManager.cpp`: `AssetManagerBase` (`GetAsset`, `RequestLoad`, `DispatchLoad`, `RunLoad`, `PushCompletion`, `ProcessCompletions`, `Update`, `LoadAssetSync`, `ReloadAsset`, `UnloadAsset`, `CancelLoad`, `ReplaceLoadedAsset`, `AddMemoryAsset`, `WaitForPendingLoads`), `AssetLoadData`, `AssetLoaderRegistry`, `AssetSourceRevisions` and the facade `AssetManager`.
- `Strata/src/Strata/Asset/AssetStreamingQueue.h` and `AssetStreamingQueue.cpp`: `AssetStreamingQueue`, `AssetStreamingLimits`, `AssetStreamingRequest`.
- `Strata/src/Strata/Asset/Asset.h`: `Asset`, `AssetState`, `AssetPriority`, `AssetFinalizeResult`.
- `Strata/src/Strata/Asset/EditorAssetManager.h` and `RuntimeAssetManager.h`: the two managers that supply the bytes.
- `Strata/src/Strata/Renderer/RendererRegistration.cpp`: the renderer's loaders.
- `Strata/src/Strata/Scene/Scene.h`: `Scene::GetAssetManager`.
- `StrataTests/src/Asset/StreamingQueueTests.cpp` and `AssetTests.cpp`: the suites `Asset.StreamingQueue` and `Asset`.
- The command `asset.info` shows an asset's state and `loadError`.

## Further reading

- Robert Nystrom, "Game Programming Patterns", the chapters on the game loop and on object pools: why a loop never waits, and how to bound memory; beginner.
- Jason Gregory, "Game Engine Architecture", the section on resource management and asynchronous file I/O: how engines order and bound background loads; intermediate.
- The Unity manual, on loading resources and scenes in blocking and asynchronous ways: one engine's blocking and asynchronous calls; beginner.
- The Unreal Engine documentation, on asynchronous asset loading with the streamable manager: callbacks and handles in a large engine; intermediate.
- The Godot documentation, on `ResourceLoader` and background loading: polling a status, close to Strata's approach; beginner.
