---
id: assets/residency
title: "Residency, eviction and pins"
description: "How Strata keeps assets within a memory budget per pool: which asset goes first, what is never dropped, and how an arrival gets room."
kind: internals
size: XL
tracks: [E]
needs: [assets/loading, gpu/resources-lifetimes, basics/trees-graphs]
time: 95
learn:
  - id: budgets-pools
    text: explain why Strata keeps one budget per memory pool and compute the default GPU budgets from the device's budget
  - id: eviction-order
    text: predict which assets the manager drops under a budget, given the order of requests, pins, the grace window and held references
  - id: touch-cost
    text: trace how a request moves an asset's node in a recency order in constant time
  - id: room-first
    text: explain why an arrival makes room and reserves it before it allocates, and why it waits the frames in flight
  - id: keep-rules
    text: choose between a request, a pin and a held reference to keep an asset in memory
since: 0.3.0
status: final
---

A game owns more assets than its memory can hold at once. This page teaches the part of Strata that decides which loaded assets stay and which go. It keeps each pool of memory within a budget by dropping what was requested longest ago. It never drops what is pinned, what was used a moment ago or what the :term[graphics card]{id=gpu} may still read.

**Residency** is the state of being in memory: an asset is resident from the moment it is loaded until the manager drops it. The page does not teach loading itself, which [Loading assets](loading.md) covers. It starts where a load ends and asks how long the result may stay.

## The problem and how engines solve it

Take a game with 400 textures of 8 MB each, which add up to 3,200 MB. A graphics card may have 4,096 MB in all, shared with the frame's targets, the meshes and the :term[operating system]{id=operating-system}. The player walks through one valley at a time and sees about 60 textures there, 480 MB.

Loading everything at the start wastes memory and time. Loading only what the valley needs is the aim, and the hard moment is the change of valley: something must leave so that something else can come.

Three questions follow. How much memory may the game use? What goes when the limit is reached? What must never go? Engines answer each in a few ways, and each answer has a cost.

First, the limit. Memory comes in kinds that run out in different ways. System memory belongs to the :term[central processing unit]{id=processor} (CPU). Video memory belongs to the graphics processing unit (GPU), and a texture and a vertex buffer both live there.

A **memory pool** is a kind of memory with its own limit and its own accounting. Strata has three: system memory, video memory for textures and video memory for buffers.

A **budget** is the most memory something may use. Engines choose among three plans for budgets, and the next table compares them.

| Plan | How it works | Main cost |
| --- | --- | --- |
| No budget | Load what is requested and never drop it | The game runs out of memory on a large level or a small card |
| One budget | A single number for all memory | Video and system memory run out differently, so one number is too tight for one and too loose for the other |
| A budget per pool | Each pool has its own number | More numbers to choose; the defaults must follow the machine |

Second, the choice of what goes. **Eviction** is dropping a loaded asset to free its memory; the asset loads again when something requests it next.

A policy picks which asset to drop. **Least recently used** (LRU) is the policy that drops the asset used longest ago. The others are least frequently used, which drops the asset with the fewest uses, priority classes, where the game labels assets and low classes go first, and explicit unloads, where game code says when. The next table compares them.

| Policy | Picks | Main cost |
| --- | --- | --- |
| LRU | The asset used longest ago | Cannot tell a favorite from an asset used once, long ago |
| Least frequently used | The asset used the fewest times | A once-hot asset stays long after it stopped mattering, and counters must age |
| Priority classes | The lowest class first, then the oldest | Someone must label every asset, and the labels drift |
| Explicit unload | What the game code names | Every level and every script must remember to unload |

A small case shows the weakness of the frequency policy. A boss texture is used 500 times in one fight and never again. A counter says it is the most valuable asset in the pool for the next hour.

LRU forgets it after a few minutes, because its last use is old. LRU has its own weakness: a single sweep over many assets, each used once, pushes out the textures that the scene needs every frame. Strata accepts that weakness and covers it with the protections below.

Third, protection. Whatever the policy, some assets must stay. An asset in use this frame must stay, or the player sees a hole. The graphics card works some frames behind the processor, so memory that a running frame reads must not be freed; [Resource lifetimes](../gpu/resources-lifetimes.md) taught why. Gameplay may also need an asset that no frame draws yet, such as a sound that a script plays when a door opens.

Strata chooses a budget per pool, LRU with protections, and explicit pins for gameplay. LRU is simple to reason about: the rule fits in one sentence, and a test can predict its result. The protections cover what LRU alone gets wrong. The pin covers what only game code knows.

:::why[One policy and a few protections, not priority classes]
Labels need a person to keep them true across hundreds of assets. A wrong label drops something drawn this frame, or keeps garbage for hours. A request is a fact the engine sees for itself: every use of an asset says that it is used now. The cost is that the policy cannot know the future. An asset needed soon but not used lately can go, and the cure is a pin, which this page teaches below.
:::

## The map

Four parts hold the work. The :term[asset manager]{id=asset-manager} owns an entry for every registered asset, with its state, its memory, the frame of its last request and its pin count. Next to the entries it keeps one recency order per pool.

A **recency order** is a list of the resident assets of one pool, sorted from the least recently requested to the most recent. The first node is the next to go.

`AssetResidency` is the file and the set of types that name the pools, the budgets and the pin. The graphics side stands behind `IAssetGraphics`, a small interface that the :term[renderer]{id=renderer} registers as an engine service, so the asset layer includes no graphics code. Last, an `AssetManagerExtension` is a hook through which a higher module joins the manager's update.

```mermaid caption="The manager holds the entries and one recency order per pool. The graphics interface tells it the device budget and the frames in flight. An extension frees partly resident memory before whole assets go." alt="Boxes for the asset manager, its entries, three recency orders, the budgets, the graphics interface and a manager extension, joined by arrows that show who asks whom."
flowchart LR
  G["IAssetGraphics (renderer)"] -->|device budget, frames in flight| B["AssetResidencyBudgets"]
  G -->|frames in flight| M["AssetManagerBase"]
  B --> M
  M --> E["entries: state, usage, last request, pins"]
  M --> O["3 recency orders: Cpu, GpuTextures, GpuBuffers"]
  X["AssetManagerExtension (TextureStreamer)"] -->|ReleaseMemory, OnUpdate| M
  M -->|EvictToFitLocked| O
```

The **device memory budget** is the amount of video memory that the graphics driver says the process may use. Strata reads it from `IAssetGraphics::GetMemoryBudget`, which reports the :term[Vulkan]{id=vulkan} extension `VK_EXT_memory_budget`. The value is 0 while no renderer runs or when the device reports nothing.

The same interface reports `GetFramesInFlight`, the number of frames the card may still work on. Both numbers come from the device, so the same game gets a bigger budget on a bigger card.

Every call here runs on the :term[main thread]{id=main-thread}, except that loads finish on other threads and hand their results back. All of the manager's state sits behind one :term[mutex]{id=mutex}. The functions whose names end in `Locked` assume that the caller holds it, and you will meet that suffix on every function that changes an order.

## The contract

Residency works only if assets and callers keep a few promises. Each promise has a reason, and the reasons are the part to remember.

An asset reports its memory per pool. `GetMemoryUsage` returns how many :term[bytes]{id=byte} the asset holds in system memory, in video memory for textures and in video memory for buffers. The manager reads it once the asset is finalized, and the totals follow it.

`GetFinalizedMemoryUsage` returns what `GetMemoryUsage` will report once the asset is finalized. It matters for a texture, which starts as pixels in system memory and ends as video memory. The manager asks for it before the asset arrives, so that it can free room first.

An asset whose data other objects share, such as a clip whose samples a playing voice reads, overrides `IsDataShared` to say so. Dropping it would free nothing.

:::rule[Report shared data and accurate memory per pool]
Strata's guide asks every :term[asset type]{id=asset-type} to report `IsDataShared` and its memory per pool exactly. A wrong total drops the wrong assets, loads a second copy of shared data or leaves the device over budget. A texture counted in both the CPU pool and the GPU pool is counted twice, which wastes budget.
:::

Callers promise three things. The first is to request what they use every frame. A **request** (also called a touch) marks an asset as used in the current frame. `GetAsset`, `RequestLoad` and `Pin` all count as requests. An asset that is drawn but not requested looks unused, and the manager may drop it.

The second promise is to hold handles, not references, across frames. An :term[asset handle]{id=asset-handle} is a number, and a `Ref` is a :term[shared pointer]{id=shared-pointer} that keeps the object alive. The manager refuses to drop an object that anyone outside it still holds. A `Ref` kept in a component therefore makes that asset stay forever, and the budget no longer works.

:::rule[Hold handles, not Refs, and request every frame]
The guide states this for all asset code. A held `Ref` keeps the asset in memory whatever the pool holds, and a missing request lets an asset that is drawn go. The frame's resolve cache shows the rule applied: it drops every reference when the frame ends, as [Asset requests](../draw/asset-requests.md) teaches.
:::

The third promise is to pin what gameplay must keep, and to release it. A **pin** is a hold on one asset, made by an `AssetPin` object, that keeps the asset resident while the object lives. A pin is the only way to keep an asset whatever its use.

:::caution[Pinning everything is no budget]
Pinned assets never leave, so a pool full of pins can only grow. A game that pins its whole level has the first plan of the problem section again: no budget. Pin the few assets that gameplay needs at a given moment, and release them when the moment ends. [Closures and group loads](references.md) teaches the pins that a loading screen makes.
:::

The manager makes one promise back: it frees no GPU memory that a frame :term[in flight]{id=in-flight} may still use. A dropped texture leaves the manager at once, but its video memory returns only after the :term[frames in flight]{id=frames-in-flight} have passed, and an arrival that needs that memory waits for it.

The same promise explains the first protection of the next list. The **grace window** is the number of frames after a request in which an asset is never dropped. Its length is the frames in flight plus 2, so with a default of 2 frames in flight the window is 4 frames.

The manager never drops an asset that:

- is not in the ready state, or has no loaded object;
- is pinned;
- was requested within the grace window;
- is a :term[memory asset]{id=memory-asset} (made in code, with no file) or a :term[built-in asset]{id=built-in-asset};
- is held outside the manager, which shows as a count of references other than 1;
- reports `IsDataShared`.

Because of these protections, a pool can stay over its budget. The budget is a target that the walk works toward, and what is protected is the floor under it. The Streaming panel shows this case, as a later section shows.

## A toy version

A toy makes the core rule concrete before the engine adds its protections. The program below keeps named things within a byte budget. It holds a list in order of use, oldest first, and a map from name to list node.

A request that hits moves the node to the back with `splice`, which moves the node and copies nothing. A request that misses adds a node at the back and then drops from the front until the total fits.

```cpp sketch="assets-residency-toy.cpp"
#include <cstdint>
#include <cstdio>
#include <iterator>
#include <list>
#include <string>
#include <unordered_map>

namespace
{

	struct Entry
	{
		std::string Name;
		uint64_t Bytes = 0;
	};

	// Keeps named things within a byte budget: the one requested longest ago goes first.
	class LruCache
	{
	public:
		explicit LruCache(uint64_t budget)
			: m_Budget(budget)
		{
		}

		void Request(const std::string& name, uint64_t bytes)
		{
			auto found = m_Lookup.find(name);
			if (found != m_Lookup.end())
			{
				// A hit moves the node to the back of the list; no node is copied.
				m_Order.splice(m_Order.end(), m_Order, found->second);
				return;
			}
			m_Order.push_back(Entry { name, bytes });
			m_Lookup[name] = std::prev(m_Order.end());
			m_Resident += bytes;
			EvictToFit();
		}

		void Print() const
		{
			std::printf("resident %llu of %llu:", static_cast<unsigned long long>(m_Resident), static_cast<unsigned long long>(m_Budget));
			for (const Entry& entry : m_Order)
				std::printf(" %s", entry.Name.c_str());
			std::printf("\n");
		}

	private:
		void EvictToFit()
		{
			// The newest entry stays even when it alone is over the budget.
			while (m_Resident > m_Budget && m_Order.size() > 1)
			{
				const Entry& oldest = m_Order.front();
				std::printf("evict %s (%llu)\n", oldest.Name.c_str(), static_cast<unsigned long long>(oldest.Bytes));
				m_Resident -= oldest.Bytes;
				m_Lookup.erase(oldest.Name);
				m_Order.pop_front();
			}
		}

	private:
		uint64_t m_Budget = 0;
		uint64_t m_Resident = 0;
		std::list<Entry> m_Order; // Least recently requested first
		std::unordered_map<std::string, std::list<Entry>::iterator> m_Lookup;
	};

}

int main()
{
	LruCache cache(10);
	cache.Request("A", 4);
	cache.Request("B", 4);
	cache.Request("A", 4);
	cache.Request("C", 4);
	cache.Print();
	cache.Request("D", 4);
	cache.Print();
	return 0;
}
```

```text output-of="assets-residency-toy.cpp"
evict B (4)
resident 8 of 10: A C
evict A (4)
resident 8 of 10: C D
```

1. **Line 32:** a hit moves the node to the back; the map still points to the same node.
2. **Line 53:** the loop stops when the total fits, and the newest entry stays even when it alone is over the budget.
3. **Line 66:** the list holds the policy: the front is always the asset requested longest ago.

Read the run by hand. The budget is 10. After A and B, 8 bytes are resident. The second request of A moves A behind B, so C pushes the total to 12 and B, the oldest, goes. Then D pushes it to 12 again and A goes.

The list is the policy, and the map makes a hit take :term[constant time]{id=constant-time}.

Three things are missing, and the real code adds them. The toy has one pool, and Strata has three. The toy treats an arrival and a request alike, and Strata stamps only by request. The toy drops any entry, and Strata skips the protected ones and waits for GPU memory. The next section shows each in the order that data flows.

## The real code

The code lives in `Strata/src/Strata/Asset/AssetResidency.cpp` and `Strata/src/Strata/Asset/AssetResidency.h`, and the manager's :term[frame loop]{id=game-loop} in `Strata/src/Strata/Asset/AssetManager.cpp`. Follow one asset from the budget to its eviction.

### Pools and budgets

`AssetResidencyBudgets` holds the numbers. `GpuTextures`, `GpuBuffers` and `Cpu` are the pool budgets, each `c_Unlimited` until set. `FromDeviceBudget` turns the device's number into defaults: GPU textures get 50 % of it and GPU buffers 15 %. The CPU pool stays unlimited, and a device budget of 0 leaves the GPU pools unlimited too.

The next diagram shows how one pool is spent. Resident bytes and bytes reserved for arrivals count against the budget together. Loads still in flight are not yet in the pool, but they are on their way.

```mermaid caption="One pool against its budget. Resident bytes and reserved bytes count together against the budget, and pending loads wait outside the pool. What remains under the budget is the headroom." alt="A bar split into resident, reserved and headroom parts under a line that marks the budget, with pending loads waiting to the right of it."
flowchart LR
  subgraph Pool["GpuTextures pool"]
    R["resident"] --> V["reserved"] --> H["headroom"]
  end
  P["pending loads (in flight)"] -.-> V
  Pool --- L["budget line = 50 % of the device budget"]
```

:::example[Default budgets for an 8 GiB card]
A device reports 8 GiB, which is 8,192 MiB. GPU textures get half: 4,096 MiB. GPU buffers get 15 %: about 1,229 MiB. The CPU pool has no limit.

A game with 3,200 MB of textures on this card fits, and nothing is dropped. On a 4 GiB card the texture budget is 2,048 MiB, the same game does not fit, and the least recently requested textures go as the player moves.
:::

### A request moves a node

Each entry stores `LastRequestedFrame`. The recency orders are `std::map` objects, one per pool, keyed by a `RecencyKey` of the frame and a running sequence number. A map keeps its keys sorted, so the first node is the oldest request and the last node is the newest.

Only resident assets with memory in a pool are in that pool's order. An asset that holds both video memory and system memory is in two orders, and a request moves it in both.

```mermaid caption="Touching an asset extracts its node and inserts it again at the end with a new key. The other nodes do not move, and nothing is searched." alt="Three nodes in a row, oldest on the left. The middle node is lifted out, given a new key and placed at the right end of the row."
flowchart LR
  subgraph Before
    a1["T0 (frame 3)"] --> b1["T1 (frame 4)"] --> c1["T2 (frame 5)"]
  end
  subgraph After
    a2["T0 (frame 3)"] --> c2["T2 (frame 5)"] --> b2["T1 (frame 9)"]
  end
  Before -->|"request T1 in frame 9: extract, new key, insert at end"| After
```

Why a node move and not a search? A renderer requests thousands of assets in each frame.

Finding a key in a tree of every resident asset costs a walk down the tree for each one, a number of steps that grows with the :term[logarithm]{id=logarithm} of the count. Extracting the entry's own node (the entry stored its :term[iterator]{id=iterator}) and inserting it with the end as the hint both take constant time. [Trees and graphs](../basics/trees-graphs.md) taught the cost of those walks. Here the walk is gone.

```cpp src="Strata/src/Strata/Asset/AssetResidency.cpp#L325-L349" symbol="AssetManagerBase::TouchLocked"
void AssetManagerBase::TouchLocked(AssetEntry& entry)
{
	if (entry.LastRequestedFrame == m_FrameIndex)
		return; // Requested in this frame already: its place in the orders is the frame's
	entry.LastRequestedFrame = m_FrameIndex;
	if (!entry.InRecencyOrders)
		return;

	// The latest request goes last: its key is the largest. Extracting the entry's own node and inserting it with the end
	// as hint both take constant time, where searching the order for the key would take a walk down a tree of every
	// resident asset (a renderer requests thousands of assets each frame).
	const RecencyKey key { m_FrameIndex, m_NextRecencySequence++ };
	for (AssetMemoryPool pool : c_AssetMemoryPools)
	{
		if (GetPoolBytes(entry.Usage, pool) == 0)
			continue;
		const size_t index = static_cast<size_t>(pool);
		RecencyOrder& order = m_RecencyOrders[index];
		ST_CORE_ASSERT(entry.RecencyNodes[index]->second == entry.Metadata.Handle, "Asset {} is missing from a recency order",
			entry.Metadata.Handle.ToString());
		auto node = order.extract(entry.RecencyNodes[index]);
		node.key() = key;
		entry.RecencyNodes[index] = order.insert(order.end(), std::move(node));
	}
}
```

1. **Line 327:** a second request in the same frame returns at once, so repeated requests cost almost nothing.
2. **Line 336:** the key joins the frame and a running number, so a later request always sorts after an earlier one, even in the same frame.
3. **Line 345:** `extract` hands over the entry's own node, found without a search.
4. **Line 347:** the node, with its new key, returns with the end as the hint.

An arrival is no request. When a load finishes and the asset is linked, `LinkRecencyLocked` uses the asset's latest request frame as the key. An asset that was requested once, long ago, and whose load took longer than the grace window, may be dropped at once. That is the intended result: nothing wants it.

### Which assets may go

`CanEvictLocked` applies the protections of the contract in one function. The pin, the memory and built-in assets and the shared data are plain checks. The check `entry.Loaded.use_count() == 1` is the test for a held reference: the manager holds one reference, and a second means someone else holds the object.

```cpp src="Strata/src/Strata/Asset/AssetResidency.cpp#L428-L435" symbol="AssetManagerBase::CanEvictLocked"
bool AssetManagerBase::CanEvictLocked(const AssetEntry& entry) const
{
	if (entry.State != AssetState::Ready || !entry.Loaded || entry.IsMemoryAsset || entry.Metadata.IsBuiltin() || entry.PinCount > 0)
		return false;
	// Someone outside the manager still holds the object, or its data: evicting it would free nothing now, and the
	// next request would load a second copy.
	return entry.Loaded.use_count() == 1 && !entry.Loaded->IsDataShared();
}
```

The comment in the code gives the reason for the last check. Dropping an object that someone holds frees nothing now, and the next request would load a second copy beside the first.

Now the walk itself. `EvictToFitLocked` takes a pool and the extra bytes that the caller wants to fit, and it walks that pool's order from the oldest node. It stops when the pool fits, when the order ends, or at the first asset requested within the grace window. Every later asset was requested even more recently, so the walk may stop there instead of reading them all.

```cpp src="Strata/src/Strata/Asset/AssetResidency.cpp#L523-L542" symbol="AssetManagerBase::EvictToFitLocked"
void AssetManagerBase::EvictToFitLocked(AssetMemoryPool pool, uint64_t extraBytes, std::vector<Ref<Asset>>& released)
{
	const uint64_t budget = m_Budgets.GetPoolBudget(pool);
	// The sum cannot overflow: it counts bytes of memory that exists.
	const auto isOverBudget = [&]() { return GetPoolBytes(m_Resident, pool) + extraBytes > budget; };

	// Least recently requested first. The order holds only assets with memory of this pool, so a pool that stays over
	// budget (what is in use exceeds it) costs a look at its own stale assets, not at every stale asset.
	RecencyOrder& order = m_RecencyOrders[static_cast<size_t>(pool)];
	for (auto it = order.begin(); it != order.end() && isOverBudget();)
	{
		AssetEntry& entry = m_Entries.at(it->second);
		++it; // Eviction removes the entry from the orders
		m_EvictionChecks++;
		if (WasRequestedWithinLocked(entry, m_EvictionGraceFrames))
			break; // Every later entry was requested even more recently
		if (CanEvictLocked(entry))
			EvictLocked(entry, released);
	}
}
```

1. **Line 527:** the test adds the extra bytes to the pool's resident bytes, so a caller can ask whether something more would fit.
2. **Line 532:** the walk starts at the oldest node of this pool's order and ends when the pool fits.
3. **Lines 537–538:** the first asset inside the grace window ends the walk, because all later ones are newer.
4. **Lines 539–540:** a protected asset is skipped and the walk continues; any other asset is dropped.

The walk skips a protected asset and continues with the next one. A pool that stays over its budget because a few big assets are protected then costs a look at that pool's own stale assets, not at every stale asset of the engine. `EvictLocked` unloads the entry and gives it a new generation, so a late load result for the old one is discarded. It also announces the change and counts the eviction. The dropped object goes into a list that is cleared after the lock is released, since destroying a large asset takes time.

:::example[Which textures go under a 5 MB budget]
Take a texture pool with a budget of 5 MB, eleven textures of 1 MB each (`T0` to `T10`) and a grace window of 4 frames. The player requests `T0` to `T9`, one per frame, and then nothing arrives for a few frames. The pool holds 10 MB and the walk starts at `T0`. Each drop frees 1 MB, so `T0` to `T4` go and the walk stops with 5 MB resident.

Next the player requests `T5`, which moves to the back of the order, and `T10` arrives. The pool is at 6 MB, so the oldest asset outside the window goes: `T6`, not `T5`. The test `Eviction takes the least recently requested assets first` in the suite `Asset.Residency` checks these results.
:::

### The frame's order of work

The manager's `Update` calls the pieces in a fixed order. It :term[finalizes]{id=finalize} the frame's arrivals, runs the extensions, submits the frame's upload batch and applies a scheduled trim if its frame has come. Last it calls `EvictToBudgets`, which runs `EvictToFitLocked` for each pool with no extra bytes.

Eviction to budgets thus comes after the new arrivals. An arrival that is not in use does not push out an asset that is, because the walk stops at the grace window.

### Trims after a scene switch

A budget drops assets only when a pool is over. After a scene switch the old scene's assets may fit in memory beside the new scene's, and yet they are of no use. A **trim** drops everything not requested lately, whatever the budgets say.

`TrimUnused` does it at once. `ScheduleTrim` delays it by some frames and takes a list of handles to keep.

The delay matters. Right after a switch the new scene has not rendered yet, so nothing has requested what it uses. The :term[runtime]{id=runtime} schedules the trim `c_SceneSwitchTrimFrames` (3) frames ahead, with 3 frames as the age limit, and it passes the assets that the scene's load brought in. Three frames later the new scene has requested what it draws, and the assets of the old scene show as unused.

For example, a game leaves a forest of 900 MB and enters a cave. The cave's load brings in its own assets. At frame 3 after the switch, every forest asset with no request in the last 3 frames goes, though the pool was never over its budget. The trim uses `EvictUnusedLocked`, which walks each order from the oldest node and stops at the first asset requested within the age limit.

### Room before arrival

Without care, an arrival would allocate, find the pool over its budget and only then drop assets. For a moment the process would hold the budget plus the arrival. **Room before arrival** is the rule that an asset in use drops what its finalized size would push over the budget before it allocates anything.

A **reservation** is the memory that the manager counts for an arrival after the arrival made room and before it is published. Without it, two arrivals in one frame would each see the same free space, and both would fit on paper. With it, the second arrival counts the first one's bytes.

```cpp src="Strata/src/Strata/Asset/AssetManager.cpp#L1149-L1157" from="if (!completion.RoomMade && (!applyBudget" to="completion.FinalizeFrame = GetFrameIndex() + m_GpuReleaseFrames;" symbol="AssetManagerBase::ProcessCompletions"
if (!completion.RoomMade && (!applyBudget || !arrivalWaiting || makeRoomEarly))
{
	completion.RoomMade = true;
	const RoomResult room = MakeRoomFor(completion.Handle, incoming);
	completion.Reserved = room.Reserved;
	// An arrival that allocates no GPU memory (a material that made room in the CPU pool) has nothing to wait
	// for.
	if (room.EvictedGpuBytes > 0 && incoming.GetGpu() > 0 && upload)
		completion.FinalizeFrame = GetFrameIndex() + m_GpuReleaseFrames;
```

The loop of arrivals, `ProcessCompletions`, makes room before it finalizes anything, as [Loading assets](loading.md) shows around it. It asks `MakeRoomFor` once per arrival. When the room freed GPU memory and the arrival will allocate GPU memory, it sets a finalize frame: the current frame plus `m_GpuReleaseFrames`, which is the frames in flight plus 1.

```cpp src="Strata/src/Strata/Asset/AssetResidency.cpp#L544-L570" symbol="AssetManagerBase::MakeRoomFor"
AssetManagerBase::RoomResult AssetManagerBase::MakeRoomFor(AssetHandle handle, const AssetMemoryUsage& incoming)
{
	std::vector<Ref<Asset>> released;
	RoomResult room;
	{
		std::scoped_lock<std::mutex> lock(m_Mutex);
		auto it = m_Entries.find(handle);
		// An arrival nobody requested lately is no reason to evict what is in use: it may be the next to go itself.
		if (it == m_Entries.end() || !WasRequestedWithinLocked(it->second, m_EvictionGraceFrames))
			return room;

		// Only the pools the arrival needs: pools over budget for other reasons are Update's business (an arrival must not
		// wait for GPU memory it does not need).
		const uint64_t residentGpuBytes = m_Resident.GetGpu();
		for (AssetMemoryPool pool : c_AssetMemoryPools)
		{
			const uint64_t bytes = GetPoolBytes(incoming, pool);
			if (bytes > 0)
				EvictToFitLocked(pool, bytes + GetPoolBytes(m_Reserved, pool), released);
		}
		room.EvictedGpuBytes = residentGpuBytes - m_Resident.GetGpu();
		room.Reserved = incoming;
		m_Reserved += incoming;
	}
	// The evicted objects are destroyed here, after the lock; their GPU memory follows once no frame in flight can use it.
	return room;
}
```

1. **Line 552:** an arrival that nobody requested lately makes no room; it may be the next to go itself.
2. **Line 557:** the manager notes its resident GPU bytes, to report later how many it dropped.
3. **Line 562:** for each pool in which the arrival has bytes, the walk must fit the arrival plus what is already reserved there.
4. **Lines 564–566:** the result tells the caller how many GPU bytes went, and the arrival's size joins the reserved total.

`MakeRoomFor` takes only the pools that the arrival needs. A pool over budget for other reasons is the business of `Update`, since an arrival must not wait for GPU memory that it does not need. The reservation ends when the arrival is published, or when the arrival turns out to be out of date and is thrown away.

The wait has a reason. The manager drops the object at once, but a frame in flight may still read the texture, and the GPU memory returns only after those frames end. If the new texture allocated at once, the device would hold both for a few frames. So an arrival that needs GPU memory, and made room for it, waits until the frame index reaches its finalize frame.

:::example[A 40 MB arrival under a 100 MB budget]
The texture pool holds 95 MB, with two stale textures of 30 MB and 10 MB. A 40 MB texture arrives, and it was requested a frame ago. The walk asks for 95 + 40 = 135 MB to fit in 100 MB. It drops the 30 MB texture (105 MB still to fit) and then the 10 MB one (95 MB, which fits). The reservation of 40 MB is added.

With 2 frames in flight the arrival may start its upload 3 frames later. In those frames the released video memory comes back, and the card never holds 135 MB at once.
:::

:::why[Make room first, and reserve]
The other order, allocate and then drop, has a peak of the budget plus every arrival that is in flight. On a card that is already near its limit the peak is an out-of-memory error. The cost of the chosen order is latency: an arrival that needs room waits a few frames before it is visible, and the asset it replaces is already gone. The reservation costs a few more numbers to keep and keeps simultaneous arrivals honest.
:::

Arrivals are finalized in order, so those behind a waiting arrival wait for it. They still make room at once, so that arrivals that need room in the same frame wait out their releases together and not one after another. They do this only for as much GPU memory as one frame uploads, `UploadBytesPerFrame`. A comment in the code records that dropping far ahead of what can be uploaded raised the memory peak of the engine's stress test.

### Memory that changes under an asset

A texture can gain or lose levels without a new object, and then its memory changes while its entry stays. `UpdateMemoryUsage` takes the new usage, removes the entry from its orders, fixes the totals and puts it back with the same key. The entry keeps its place, since its latest request decides the order and not its size. Only the pools that it holds memory in may change. [Mip streaming](../draw/mip-streaming.md) teaches why levels come and go.

### Extensions free partial memory first

An `AssetManagerExtension` lets a higher module help the manager. The renderer registers a `TextureStreamer` through `AssetManagerExtensionRegistry`. In `Update`, each extension runs `OnUpdate`, and then `ReleaseExtensionMemory` computes, for each pool, how far it is over its budget.

The manager calls each extension's `ReleaseMemory` with that number. The extension frees detail from textures that it keeps partly resident and reports each change through `UpdateMemoryUsage`. Whole assets go only for what is still over, in `EvictToBudgets` later in the frame.

Why in that order? Dropping the top levels of a large texture costs the player less than the texture vanishing. For example, a pool 60 MB over budget may get 45 MB back from lower levels of many textures, and only 15 MB of whole assets must go. The extension also runs without the manager's lock, so it may record GPU work.

### Pins

An `AssetPin` is a small object that holds a handle, a weak pointer to the manager and a registration number. A weak pointer can reach the manager while it exists but does not keep it alive, and the registration number changes when the asset is registered again. `Pin` finds the entry, adds 1 to its pin count and requests the load, at high priority unless the caller says otherwise. `Unpin` subtracts 1. The pin's :term[destructor]{id=destructor} calls `Reset`, so a pin that goes out of scope releases itself.

```cpp src="Strata/src/Strata/Asset/AssetResidency.cpp#L104-L126" symbol="AssetManagerBase::Pin"
AssetPin AssetManagerBase::Pin(AssetHandle handle, AssetPriority priority)
{
	std::weak_ptr<AssetManagerBase> self = weak_from_this();
	ST_CORE_ASSERT(!self.expired(), "Asset managers must be owned by a Ref to pin assets");
	if (self.expired())
		return {};

	uint64_t registration = 0;
	{
		std::scoped_lock<std::mutex> lock(m_Mutex);
		auto it = m_Entries.find(handle);
		if (it == m_Entries.end())
			return {};
		if (it->second.PinCount++ == 0)
		{
			m_PinnedAssets++;
			UpdateListedLocked(it->second);
		}
		registration = it->second.Registration;
	}
	RequestLoad(handle, priority);
	return AssetPin(std::move(self), handle, registration);
}
```

1. **Line 106:** the pin keeps only a weak pointer to the manager, taken here.
2. **Lines 117–121:** the first pin of an asset counts it among the pinned assets and keeps it listed.
3. **Line 124:** a pin is also a request, so the asset starts to load.
4. **Line 125:** the returned object carries the registration, so a pin of an asset registered again counts for nothing.

The weak pointer means that a pin that lives longer than its manager does nothing, instead of keeping the manager alive. Pins of one asset add up: the asset stays pinned until the last is released. A pinned entry is also kept in the listed set that the Streaming panel reads, so a pinned asset shows even if it is not loaded.

A script's pin is the same object. `Assets::RequestLoad(asset)` in a script module asks the scene's script system, which calls `Pin` once per asset, at normal priority, and stores the result in a map. A second call for the same asset adds no second pin; it only requests the load again, in case the asset was unloaded meanwhile. `Assets::Release(asset)` erases the entry, which destroys the pin, and the end of play clears the map.

So a rarely used sound stays loaded for the whole play session between those two calls, and plays at once when needed. [Sound](../make/sound.md) shows the game maker's side.

### Touching many at once

Most frames repeat the previous frame's requests. The renderer's `AssetResolveCache` records which assets a frame used, and a still frame replays that record through `TouchLoadedAssets`. The function takes handles and a weak pointer to the object expected for each.

Under one lock it first checks everything: each entry must exist, be ready and hold exactly the expected object. Only if all checks pass does it touch them, each as one request. If one check fails the function returns false and touches nothing, and the caller falls back to single requests. The saving is one lock instead of thousands, and the order comes out the same as with single requests.

### Seeing it

`GetResidencyInfo` and `GetResidencySamples` list the resident, loading, failed and pinned assets for the editor. They cost what is listed, not what is registered, because the manager keeps a set of listed entries and updates it when an entry changes state. With tens of thousands of registered assets and a hundred resident, the walk visits about a hundred.

The editor's **Streaming** panel shows the pools against their budgets, the queue, the uploads and the evictions. A table below has one row per listed asset: its memory in each pool, how many frames ago it was requested and its pin count. How that table draws cheaply is the subject of [Instrument panels](../editor-ui/instrument-panels.md).

::figure{id="streaming-evictions"}

The figure shows the panel with the texture budget set to 32 MB in the Showcase. The eviction count grows while the texture pool stays near 32 MB. Eviction works per pool: a pool over its budget loses its least recently requested assets first. Meshes not requested for hundreds of frames therefore stay, because the buffer pool is under its budget.

### Setting the budgets

`SetResidencyBudgets` replaces the budgets, clamps time values that are negative or not finite to 0 and pumps the queue. The editor reaches it through the command `asset.setBudget`, whose fields are in MB (1 MB is 1,048,576 bytes): `gpuTexturesMB`, `gpuBuffersMB`, `cpuMB` and others. The change lasts until the project closes, and it cannot be undone.

The runtime takes `--asset-budget-mb <megabytes>` for the GPU texture budget of a game. How to run a command is the subject of [Commands](../editor/commands.md).

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| One global budget | Small engines and simple frameworks | One number to set | The right size for neither video nor system memory |
| Least frequently used | Some caches in servers and databases | Keeps assets used often over a long time | Counters that must age; a level's old favorites linger |
| Priority classes | Engines whose levels set the importance of assets | A designer can keep key assets without code | Labels that go stale; a person must keep them true |
| Explicit unload by level | Console games with fixed levels | No guess about the future | Every level must list its own loads and unloads |
| Fixed pools sized at start | Consoles with a fixed memory map | No allocation at run time | Wasted space when content differs; a poor fit for open worlds |
| Allocate first, drop after | The simplest managers | Simple code | A peak of the budget plus every arrival |

Strata keeps the most predictable policy and adds a pin where only game code knows the future. Sources for each policy are in Further reading.

## How it is tested

The suite `Asset.Residency` in `StrataTests/src/Asset/AssetResidencyTests.cpp` drives a `FakeAssetManager` with fake assets that declare their memory. It checks that default budgets follow the device, that assets report memory per pool, and that resident memory stays within the budgets plus the pinned and recent assets.

Further tests check that eviction takes the least recently requested first, that touched assets keep their place in the order and that arrivals are placed by their latest request. Others check that pins and the grace window protect, and that built-in and memory assets stay.

Still others check that a scheduled trim keeps what was requested since, that room is made before an arrival is finalized and that an arrival nobody requested makes none.

One test holds a `Ref` and shows that its asset stays until the `Ref` is released. The suite `Asset.PartialResidency` in `StrataTests/src/Asset/AssetPartialResidencyTests.cpp` checks that memory changes of a loaded asset keep the totals and the order exact. Run a suite with the test program's filter:

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=Asset.Residency
```

The command runs the whole suite, and it needs no graphics card. The filter `--test-case="Eviction takes*"` runs one test.

## Changing it safely

An extension point exists for each need. A new asset type reports its memory through `GetMemoryUsage` and `GetFinalizedMemoryUsage`, and through `IsDataShared` where something else may use its data. A module that keeps assets partly resident writes an `AssetManagerExtension` and registers its factory, as the renderer does, and it reports each change with `UpdateMemoryUsage`. A new pool means a new `AssetMemoryPool` value, a recency order and a budget, and it must appear in `c_AssetMemoryPools`.

:::rule[Never free GPU memory that a frame in flight may use]
The guide ties dropping to the frames in flight. If you shorten the grace window or the wait, a frame may read memory that was freed, and the result is corruption or a device error that appears only under load. Release render targets and GPU objects through the deferred release of [Resource lifetimes](../gpu/resources-lifetimes.md).
:::

Keep every way to request an asset at constant cost: a new one goes through `TouchLocked`, never through a search of an order. Hold the lock while you change an entry's usage or its place in an order, and use the `Locked` suffix for functions that need it. Destroy dropped objects after the lock is released.

Test the order with the fake manager. A new regression test must fail without its fix. Before you commit, run the suites `Asset.Residency` and `Asset.PartialResidency` and the GPU suites that touch assets.

## Summary

- A budget per pool lets video and system memory run out separately, and the default GPU budgets are 50 % and 15 % of the device's budget.
- The manager drops the least recently requested assets of a pool over its budget and skips protected ones: pins, the grace window, memory and built-in assets, held objects and shared data.
- A request moves the asset's node to the end of each of its recency orders with `extract` and a hinted insert, in constant time.
- An arrival in use drops and reserves first, then waits the frames in flight plus 1 before it allocates GPU memory.
- A request keeps an asset for a moment, a pin keeps it until released, and a held `Ref` keeps it by accident and defeats the budget.

## Check yourself

1. A pool has a budget of 8 MB and holds `A`, `B`, `C` and `D` of 2 MB each, requested in that order, all older than the grace window. `B` is pinned. A script requests `A`, and then `E` of 2 MB arrives. Which asset does the manager drop?

   :::answer{tests="eviction-order"}
   `C`. After the request the order is `B`, `C`, `D`, `A`, and `E` joins at the end, so the pool holds 10 MB and must lose 2 MB. `B` is first but pinned, so the walk skips it. `C` goes and the pool is at 8 MB, which fits. `A` was requested, so it is no longer next.
   :::

2. A component keeps a `Ref<Texture>` between frames. Which statement is right? (a) The texture goes when its pool is over budget. (b) The texture stays while the `Ref` lives. (c) The texture goes but the `Ref` keeps the old object valid.

   :::answer{tests="eviction-order,keep-rules"}
   Option (b). `CanEvictLocked` sees a second reference on the object and refuses. Option (a) ignores that check. Option (c) describes a drop that the manager never makes, because the next request would then load a second copy beside the held one.
   :::

3. Why does a touch use `extract` and an insert with a hint, and not an erase and an insert by key?

   :::answer{tests="touch-cost"}
   The entry stores the iterator of its own node, so `extract` needs no search. The new key is the largest, so inserting with the end as the hint takes constant time. An erase by key and an insert by key would walk down the tree twice for each of thousands of requests in a frame.
   :::

4. A 40 MB texture arrives and drops 40 MB of GPU textures, with 2 frames in flight. How many frames pass before its upload may begin, and why?

   :::answer{tests="room-first"}
   Three: the frames in flight plus 1. A frame in flight may still read a dropped texture, so its video memory returns only after those frames end. Allocating earlier would make the device hold the old and the new texture together.
   :::

5. A designer wants a rarely used boss texture to be ready the moment the boss appears. Choose between a request in each frame, a pin and a held `Ref`.

   :::answer{tests="keep-rules"}
   A pin. A request in each frame needs a use that does not exist. A held `Ref` keeps the asset by accident and hides the intent. A pin states the intent, shows in the Streaming panel's pin count and ends with `Reset` or when the object is destroyed.
   :::

6. A card reports a device budget of 6 GiB. What are the default budgets of the texture pool and the buffer pool?

   :::answer{tests="budgets-pools"}
   6 GiB is 6,144 MiB. The texture pool gets half, 3,072 MiB, and the buffer pool gets 15 %, about 922 MiB. The CPU pool stays unlimited, because each pool has its own number and system memory does not follow the card.
   :::

## Exercises

1. **Basic.** Extend the toy of this page with a grace window of 1 frame, pins and a check for objects held outside. Use three assets of 4 bytes, a budget of 8, `A` pinned and `B` held through a `shared_ptr`, and print which asset goes in which frame.

   :::answer[Worked solution]{tests="eviction-order,keep-rules" solution="sketches/assets-residency-protect.cpp"}
   The program below adds a request frame, a pin count and a `shared_ptr` to each entry. The walk breaks at the first entry inside the grace window, and it skips an entry that is pinned or has a `use_count` above 1.

   ```cpp sketch="assets-residency-protect.cpp"
   #include <cstdint>
   #include <cstdio>
   #include <iterator>
   #include <list>
   #include <memory>
   #include <string>
   #include <unordered_map>
   #include <utility>

   namespace
   {

   	struct Entry
   	{
   		std::string Name;
   		uint64_t Bytes = 0;
   		uint64_t LastFrame = 0;
   		uint32_t Pins = 0;
   		std::shared_ptr<int> Data = std::make_shared<int>(0);
   	};

   	// The toy cache with Strata's protections: a grace window, pins and objects held outside.
   	class ProtectedCache
   	{
   	public:
   		ProtectedCache(uint64_t budget, uint64_t graceFrames)
   			: m_Budget(budget), m_GraceFrames(graceFrames)
   		{
   		}

   		std::shared_ptr<int> Request(const std::string& name, uint64_t bytes, uint64_t frame)
   		{
   			auto found = m_Lookup.find(name);
   			if (found != m_Lookup.end())
   			{
   				found->second->LastFrame = frame;
   				m_Order.splice(m_Order.end(), m_Order, found->second);
   				return found->second->Data;
   			}
   			Entry entry;
   			entry.Name = name;
   			entry.Bytes = bytes;
   			entry.LastFrame = frame;
   			m_Order.push_back(std::move(entry));
   			m_Lookup[name] = std::prev(m_Order.end());
   			m_Resident += bytes;
   			return m_Order.back().Data;
   		}

   		void Pin(const std::string& name)
   		{
   			m_Lookup.at(name)->Pins++;
   		}

   		void EvictToFit(uint64_t frame)
   		{
   			for (auto it = m_Order.begin(); it != m_Order.end() && m_Resident > m_Budget;)
   			{
   				if (frame - it->LastFrame <= m_GraceFrames)
   					break; // Every later entry was requested even more recently
   				const bool protectedEntry = it->Pins > 0 || it->Data.use_count() > 1;
   				if (protectedEntry)
   				{
   					++it;
   					continue;
   				}
   				std::printf("frame %llu: evict %s\n", static_cast<unsigned long long>(frame), it->Name.c_str());
   				m_Resident -= it->Bytes;
   				m_Lookup.erase(it->Name);
   				it = m_Order.erase(it);
   			}
   		}

   	private:
   		uint64_t m_Budget = 0;
   		uint64_t m_GraceFrames = 0;
   		uint64_t m_Resident = 0;
   		std::list<Entry> m_Order;
   		std::unordered_map<std::string, std::list<Entry>::iterator> m_Lookup;
   	};

   }

   int main()
   {
   	ProtectedCache cache(8, 1);
   	cache.Request("A", 4, 1);
   	std::shared_ptr<int> held = cache.Request("B", 4, 1);
   	cache.Request("C", 4, 1);
   	cache.Pin("A");
   	for (uint64_t frame = 1; frame <= 3; frame++)
   		cache.EvictToFit(frame);
   	return 0;
   }
   ```

   ```text output-of="assets-residency-protect.cpp"
   frame 3: evict C
   ```

   1. **Lines 59–60:** the walk stops at the first entry inside the grace window.
   2. **Line 61:** a pinned entry, or one whose data has more than one owner, is protected.
   3. **Line 65:** a protected entry is skipped and the walk continues.
   4. **Line 88:** the held pointer keeps a second owner of `B` alive.

   In frames 1 and 2 every entry is inside the window and the walk stops at once. In frame 3 it reaches `A`, pinned, then `B`, held by `held`, and then `C`, which goes. Only one asset can leave, and the pool is at 8 bytes, which is the budget.
   :::

2. **Medium.** In the Showcase, watch drops happen. Open the **Streaming** panel, set a tight texture budget with the line below and fly around. Predict which rows leave first and why the pool may stay above 32 MB. Run `{"command": "asset.setBudget", "parameters": {"gpuTexturesMB": 32}}` with the command tools of [Commands](../editor/commands.md).

   :::answer[Worked solution]{tests="budgets-pools,eviction-order"}
   After the command the **Streaming** panel shows the texture pool near 32 MB and the eviction count rising as the camera moves. The rows with the largest **Last used** values, the most frames ago, leave first. The pool may stay above 32 MB when textures are protected: a texture requested within the last frames, a built-in texture or one held outside the manager. The Mip and Streaming views of [Mip streaming](../draw/mip-streaming.md) show the same effect on the scene itself.
   :::

3. **Medium.** Keep a sound loaded from a script. Write the :term[pseudocode]{id=pseudocode} of a script that requests a rarely used clip in `OnCreate` and plays it later, and say what the engine does with it between the two calls.

   :::answer[Worked solution]{tests="keep-rules"}
   The script asks for the clip when it is created, plays it on demand and lets it go when it is destroyed.

   ```pseudocode
   OnCreate:  Assets::RequestLoad(clipHandle)   // one pin per asset
   OnUpdate:  if (doorOpened) play the clip     // loaded, so it plays at once
   OnDestroy: Assets::Release(clipHandle)       // the pin ends
   ```

   Between the calls the scene's script system holds an `AssetPin`, so no budget or trim drops the clip. A second `RequestLoad` adds no second pin and only requests the load again. After `Release` the clip may go again, and the next request loads it again.
   :::

4. **Hard.** Trace it yourself. Under the 32 MB texture budget of the last exercise, find which protection keeps each texture that stays. Set breakpoints in `EvictToFitLocked` and `CanEvictLocked`, and say where the walk stops.

   :::answer[Worked solution]{tests="eviction-order,keep-rules"}
   The functions are `AssetManagerBase::EvictToFitLocked` and `AssetManagerBase::CanEvictLocked` in `Strata/src/Strata/Asset/AssetResidency.cpp`. In the first, a breakpoint on the `break` after `WasRequestedWithinLocked` shows the walk stopping at the grace window. In the second, step through each condition: a pinned entry fails on `PinCount`, a memory or built-in asset on `IsMemoryAsset` or `IsBuiltin`, a held object on `use_count() == 1`, and shared data on `IsDataShared`.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Asset/AssetResidency.h` and `Strata/src/Strata/Asset/AssetResidency.cpp`: pools, budgets, `AssetPin`, recency orders, eviction, trims and `MakeRoomFor`.
- `Strata/src/Strata/Asset/AssetManager.cpp`: `Update`, `ProcessCompletions` and `TouchLoadedAssets`.
- `Strata/src/Strata/Asset/AssetManagerExtension.h` and `Strata/src/Strata/Asset/AssetUploadContext.h`: the extension seam and `IAssetGraphics`.
- Tests: `Asset.Residency` and `Asset.PartialResidency` in `StrataTests/src/Asset/`.
- Commands and options: `asset.setBudget` and `--asset-budget-mb`; the **Streaming** panel in the editor.

## Further reading

- The Linux kernel documentation on page reclaim (intermediate): how an operating system chooses memory pages to drop.
- Megiddo and Modha, "ARC: A Self-Tuning, Low Overhead Replacement Cache" (advanced): a policy that adapts between recency and frequency.
- The Vulkan specification, extension `VK_EXT_memory_budget` (intermediate): what the device budget means.
