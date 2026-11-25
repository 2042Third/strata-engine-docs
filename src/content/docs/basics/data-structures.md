---
id: basics/data-structures
title: "Data structures I: arrays, lists, hash maps and their cost"
description: "Learn how to arrange items in memory with arrays, linked lists, queues, hash maps and sparse sets, and how to count what each choice costs."
kind: primer
size: L
tracks: [B, E]
needs: [basics/programming-3, basics/numbers]
time: 90
learn:
  - id: cost
    text: compute the steps of a search, an insert and a removal, and name each cost in big-O notation
  - id: arrays
    text: trace an array through insert, swap-remove, growth by doubling, a free list and binary search
  - id: links
    text: draw a linked list, a stack, a queue and a ring buffer, and trace their operations
  - id: hashing
    text: compute the bucket of a key and trace a lookup through a collision
  - id: layouts
    text: choose between an array of structs, a struct of arrays and a sparse set for an access pattern
status: final
---

::::test-out

1. A list holds 2,000 names in no order. You compare them one by one with `Mia`. What is the largest number of
   comparisons one search needs, and what is that cost in big-O notation?

   :::answer{tests="cost"}
   2,000, because `Mia` may stand last or may be missing. The cost is O(n), where n is the number of names.
   :::

2. The array `[7, 3, 9, 4, 8]` loses the element at index 1 by a swap-remove: the last element moves into the gap, then
   the array shrinks by one. Write the array that is left.

   :::answer{tests="arrays"}
   `[7, 8, 9, 4]`. The 8 moves to index 1, and the old last place disappears.
   :::

3. A hash map has 8 buckets, and the hash of a key is 37. Which bucket does the key land in?

   :::answer{tests="hashing"}
   Bucket 5. Divide the hash by the bucket count and keep the remainder: 37 % 8 = 5, because 8 × 4 = 32.
   :::

4. A ring buffer holds 4 numbers. You write 1, 2, 3, 4, 5, 6 in that order. Which numbers does it hold, oldest first?

   :::answer{tests="links"}
   3, 4, 5, 6. The fifth write replaces the oldest value, 1, and the sixth replaces 2.
   :::

5. A struct of 32 bytes sits in an array of 1,000. A loop reads one 4-byte field of every struct. How many bytes of
   memory does the loop sweep, and how many would a separate array of that field hold?

   :::answer{tests="layouts"}
   The loop sweeps 1,000 × 32 = 32,000 bytes. An array of only that field holds 1,000 × 4 = 4,000 bytes, eight times
   less.
   :::

::::

## Why you will need this

A game keeps thousands of things: entities, coins, sounds, log lines and assets. Where the program puts them in memory
decides how fast it finds, adds and removes them. A frame lasts 16.7 ms at 60 frames per second, so a slow choice makes a
frame late.

This page teaches the ordinary ways to arrange items and how to count what each costs. [Trees and
graphs](../basics/trees-graphs.md) builds on them. The [scene graph](../world/scene-graph.md) keeps its links as a linked
list, and the [entity-component system](../world/ecs.md) stores components in sparse sets. At the end you try the choices
on your Coin Run game.

## Every arrangement has a price you can count

Coin Run keeps the names of the coins the player collected. A script asks: "Did the player take `Coin7`?" Where do you
keep the names, and how many steps does the question take?

A **data structure** is a way to arrange data in memory, together with the operations that work on it.

An **algorithm** is a fixed list of steps that solves a problem. The question above is answered by the algorithm "compare
each name in turn", which runs on one data structure, the list of names.

Count the steps by hand. The program below searches eight names for `Gus` and adds 1 to `steps` at each comparison.

```cpp sketch="basics-data-structures-steps.cpp"
// Counts the comparisons of a linear search through a list of names.
#include <iostream>
#include <string>
#include <vector>

int main()
{
	const std::vector<std::string> names = { "Ada", "Bo", "Cy", "Di", "Eve", "Fay", "Gus", "Hal" };
	const std::string wanted = "Gus";

	int steps = 0;
	for (size_t index = 0; index < names.size(); index++)
	{
		steps++; // one comparison
		if (names[index] == wanted)
		{
			std::cout << "found at index " << index << " after " << steps << " steps\n";
			return 0;
		}
	}
	std::cout << "not found after " << steps << " steps\n";
	return 0;
}
```

```text output-of="basics-data-structures-steps.cpp"
found at index 6 after 7 steps
```

1. **Line 11:** `steps` starts at 0 and counts every comparison; the count is the cost.
2. **Lines 15–19:** the search stops at the first match, so the cost depends on where the name stands.

`Gus` stands at index 6, the seventh place, so the search takes 7 steps. With 8 names, the best case is 1 step, the
worst case is 8 and the average is about 4. With 1,000 names the worst case is 1,000. The steps grow in step with the
number of names, and that number is the one thing that matters.

**Big-O notation** writes down how the number of steps grows with the size of the input, called n, keeping only the
fastest-growing part and dropping constant factors. A search that takes 3n + 7 steps is written O(n), read "O of n". The
notation hides the 3 and the 7 on purpose: for a large n they matter little next to the growth itself.

An operation that takes the same number of steps whatever n is, such as reading one array element by its index, runs in
**constant time**, written O(1).

The table lists the costs you meet most, with the steps each takes at three sizes. The logarithm is in base 2, as in
[Numbers](../basics/numbers.md): log n is how many times you halve n to reach 1.

| Cost | n = 10 | n = 1,000 | n = 1,000,000 |
| --- | --- | --- | --- |
| O(1) | 1 | 1 | 1 |
| O(log n) | about 3 | about 10 | about 20 |
| O(n) | 10 | 1,000 | 1,000,000 |
| O(n log n) | about 33 | about 10,000 | about 20,000,000 |
| O(n²) | 100 | 1,000,000 | 1,000,000,000,000 |

A processor does very roughly a billion simple steps per second, so about 17 million fit into one 16.7 ms frame. An O(n²)
algorithm needs a million steps on 1,000 items, which is cheap, and a trillion on a million items, about a quarter of an
hour.

Cost on paper meets the machine at one point. Big-O treats every step as equal. A processor keeps a cache, a small and fast memory beside it. A step that reads memory
already held in the cache is far cheaper than one that waits for main memory, as [Computer](../basics/computer.md)
explains.

Items side by side in memory share :term[cache lines]{id=cache-line}, so a scan of an array is often fast. Read big-O as the first
question, and measure for the second.

:::example[Counting a worst case]
Coin Run has 64 coins, and a script scans the collected names for `Coin41` once per frame.

The worst case is a miss, which compares all 64 names: 64 steps, or 3,840 comparisons per second at 60 frames per second.
That is little work. Now 10,000 enemies each scan 10,000 names in one frame: 10,000 × 10,000 = 100,000,000 steps. The
class O(n²) now costs far more than the 16.7 ms the frame has.
:::

Try it: how many steps does a linear search need, at most, among 250,000 names, and what is the cost in big-O?

:::answer
At most 250,000 steps, when the name is last or missing. The cost is O(n).
:::

## Arrays keep items side by side

An array holds items of one type in one block of memory, one after another. Item number i lives at the address of the
start plus i times the size of one item. A `std::vector<int>` of 4-byte numbers that starts at address 1000 keeps item 3
at 1000 + 3 × 4 = 1012. The computer does one multiplication and one addition, whatever n is. Reading or writing an
element by index is therefore O(1).

Inserting in the middle is different. To insert 25 at index 2 of `[10, 20, 30, 40]`, the items at indices 2 and 3 each move
one place right, and then 25 goes into the gap. The result is `[10, 20, 25, 30, 40]` after two moves. Inserting at the
front moves all n items, which is the worst case. The cost is O(n), and removing from the middle costs the same.

An array has a fixed size, but `std::vector` grows. A :term[dynamic array]{id=dynamic-array} keeps a block with spare room, called its capacity. An
append that fits costs one write. An append that does not fit allocates a block twice as large, copies every item and
drops the old block.

The copying looks expensive, but it is rare. Start with capacity 1 and append 8 items. The appends that find the block
full copy 1, then 2, then 4 items: 7 copies in all, for 8 appends. In general, doubling keeps the copies of n appends
below 2n. Spread over many appends, each one costs a constant number of steps: O(1) on average, with occasional spikes.

The program appends 20 numbers to a `std::vector` and prints its capacity whenever it changes.

```cpp sketch="basics-data-structures-growth.cpp"
// Prints the capacity of a std::vector each time it grows during 20 appends.
#include <iostream>
#include <vector>

int main()
{
	std::vector<int> values;
	size_t lastCapacity = values.capacity();
	for (int value = 1; value <= 20; value++)
	{
		values.push_back(value);
		if (values.capacity() != lastCapacity)
		{
			lastCapacity = values.capacity();
			std::cout << "size " << values.size() << ": capacity " << lastCapacity << '\n';
		}
	}
	return 0;
}
```

```text output-of="basics-data-structures-growth.cpp"
size 1: capacity 1
size 2: capacity 2
size 3: capacity 4
size 5: capacity 8
size 9: capacity 16
size 17: capacity 32
```

1. **Line 8:** `capacity()` is the room the block has; `size()` is the number of items inside.
2. **Lines 12–16:** the capacity changes only at an append that found the block full.

Each line shows one growth: the old items moved into a larger block. Some standard libraries multiply the capacity by 1.5
instead of 2. The reasoning stays the same.

Growth has a price. The items move to a new block, so a reference or a pointer (the address of an item) that you kept from before the
growth points into freed memory. An index stays valid, so an index is the safer thing to keep.

### Binary search

Searching an array in no order costs O(n). A sorted array allows far better. **Binary search** looks at the middle item,
learns which half can hold the wanted value, and throws the other half away, until one candidate is left.

The program searches nine sorted numbers for 63 and prints each probe, that is, each item it looks at.

```cpp sketch="basics-data-structures-bsearch.cpp"
// Binary search in a sorted array, printing each probe.
#include <iostream>
#include <vector>

int main()
{
	const std::vector<int> sorted = { 3, 8, 15, 21, 34, 42, 57, 63, 79 };
	const int wanted = 63;
	int low = 0;
	int high = static_cast<int>(sorted.size()) - 1;
	while (low <= high)
	{
		const int middle = (low + high) / 2;
		std::cout << "probe index " << middle << ": " << sorted[middle] << '\n';
		if (sorted[middle] == wanted)
			return 0;
		if (sorted[middle] < wanted)
			low = middle + 1;
		else
			high = middle - 1;
	}
	std::cout << "not found\n";
	return 0;
}
```

```text output-of="basics-data-structures-bsearch.cpp"
probe index 4: 34
probe index 6: 57
probe index 7: 63
```

1. **Lines 9–10:** `low` and `high` mark the part of the array that can still hold the value.
2. **Lines 13–20:** each probe compares the middle item and moves one mark past it, so the part halves.

The first probe reads index 4, the number 34. That is smaller than 63, so the left half and index 4 are gone. The next
probe reads index 6, the number 57: smaller again. The last probe reads index 7 and finds 63 after 3 probes, against 8
comparisons for a linear search.

Each probe halves the candidates, so n items need at most about log n probes: 10 for 1,000
items and 20 for a million. The cost is O(log n).

The price is the order. A sorted array must stay sorted, so inserting in the middle costs O(n) moves, and sorting an array
costs O(n log n) with the methods of [Trees and graphs](../basics/trees-graphs.md). Binary search pays off when you
search often and change rarely.

## Removing by a swap and handing out slots again

Removing item i from the middle of an array shifts every later item left: O(n). If the order of the items does not
matter, a **swap-remove** does the removal in O(1): copy the last item into the gap, then shrink the array by one.

Take `[A, B, C, D, E]` and remove C at index 2. E, the last item, moves into index 2, and the array shrinks to
`[A, B, E, D]`. One write and one shrink replace two shifts, and the cost does not grow with n.

Two things change. The
order of the items changes, and E now lives at index 2 instead of index 4. Any index you kept for E is wrong.

:::example[Swap-remove by hand]
The array `[4, 8, 15, 16, 23, 42]` loses the 8 at index 1.

The last item, 42, moves into index 1, and the array shrinks to `[4, 42, 15, 16, 23]`. Remove the 4 at index 0 next: 23
moves into index 0, and the result is `[23, 42, 15, 16]`. After two removals the numbers stand in no order, but each
removal took one write.
:::

Try it: from `[1, 2, 3, 4]` swap-remove index 3, then index 0. What is left?

:::answer
Removing index 3 removes the last item, which moves nowhere, and leaves `[1, 2, 3]`. Removing index 0 moves 3 into the gap
and leaves `[3, 2]`.
:::

Code that stores indices must repair the moved item's index. A cleaner design gives every item a stable name that never
changes while its place may. Many engines hand out slots: a slot is a place in an array, and a handle, a small :term[struct]{id=struct}, names it. When
an item dies, its slot joins a **free list**, a list of unused slot indices, often kept as a stack: the most recent free
slot is the next one handed out.

Handing a slot out again creates a danger. A handle to the dead item still names the slot, and the slot now holds a
different item. The cure is a version number. A slot stores its version, and a handle stores the version the slot had when
the handle was made. Destroying the item adds 1 to the slot's version, so a stale handle no longer matches, and the
program finds the mistake instead of reading the wrong item.

The program creates a handle to slot 2, destroys the slot, hands it out again and checks both handles. It prints 1 for true and 0 for false.

```cpp sketch="basics-data-structures-slots.cpp"
// A free list reuses slot 2; a version number catches a handle to the destroyed slot.
#include <cstdint>
#include <iostream>
#include <vector>

struct Handle { uint32_t Index; uint32_t Version; };

int main()
{
	std::vector<uint32_t> versions = { 0, 0, 0 }; // three slots, all at version 0
	std::vector<uint32_t> freeSlots;              // unused slot indices, used as a stack
	const Handle first = { 2, versions[2] };

	versions[2]++;          // destroy slot 2: its version changes ...
	freeSlots.push_back(2); // ... and its index joins the free list

	const uint32_t reused = freeSlots.back(); // create: take an index from the free list
	freeSlots.pop_back();
	const Handle second = { reused, versions[reused] };
	std::cout << "same slot: " << (first.Index == second.Index) << '\n';
	std::cout << "first valid: " << (versions[first.Index] == first.Version) << '\n';
	std::cout << "second valid: " << (versions[second.Index] == second.Version) << '\n';
	return 0;
}
```

```text output-of="basics-data-structures-slots.cpp"
same slot: 1
first valid: 0
second valid: 1
```

1. **Lines 10–11:** `versions` holds the current version of each slot, and `freeSlots` is the free list.
2. **Lines 14–15:** destroying slot 2 raises its version and puts its index on the free list.
3. **Lines 17–19:** a new item takes index 2 from the free list, with the slot's new version, 1.
4. **Lines 20–22:** the old handle still carries version 0, so it fails the check, and the new handle passes.

Strata uses both ideas. Its render scene, the renderer's copy of the scene, keeps one proxy, a record of what to draw, for each drawn entity in
vectors and keeps the free slots in `m_FreeProxies`. `CreateProxy` takes the last free slot with `back()` and
`pop_back()`, or appends a new slot when none is free, in `Strata/src/Strata/Renderer/RenderScene.cpp`. Entity numbers
carry a version as well: EnTT, the library that stores the scene's components, packs a 20-bit index and a 12-bit version
into one 32-bit number. `Scene::c_MaxEntities` in `Strata/src/Strata/Scene/Scene.h` follows from the 20 bits.

## Linked lists link items instead of lining them up

An array makes inserting in the middle expensive because the items must stay side by side. A **linked list** drops that
rule: its items point to each other, and they may lie anywhere in memory.

Each item of a linked list is a **node**: a small record with a value and a link to the next node.

```mermaid caption="A doubly linked list of three nodes: each node holds a value and two links, and a missing link ends the list." alt="Three boxes in a row hold the values 10, 20 and 30. Arrows point from each box to the next, and back arrows point from each box to the previous one. The first box has no previous link, and the last has no next link."
flowchart LR
    A["10"] -->|next| B["20"]
    B -->|next| C["30"]
    C -->|prev| B
    B -->|prev| A
```

A singly linked list has one link per node, the next. A doubly linked list has two, next and previous, so you can walk it
in both directions and cut out a node you hold without searching for its neighbor. The links may be pointers, the
addresses of other nodes, or indices into an array of nodes. Indices survive the growth of the array.

The program keeps three nodes in a vector, with `-1` for "no node", and inserts a fourth between the first two.

```cpp sketch="basics-data-structures-links.cpp"
// A doubly linked list kept in an array: links are indices, and -1 means "none".
#include <iostream>
#include <vector>

struct Node
{
	int Value = 0;
	int Next = -1;
	int Prev = -1;
};

int main()
{
	std::vector<Node> nodes = { { 10, 1, -1 }, { 20, 2, 0 }, { 30, -1, 1 } }; // 10, 20, 30
	nodes.push_back({ 15, 1, 0 }); // node 3 joins between node 0 and node 1 ...
	nodes[0].Next = 3;             // ... once its two neighbors point at it
	nodes[1].Prev = 3;

	for (int index = 0; index != -1; index = nodes[index].Next)
		std::cout << nodes[index].Value << ' ';
	std::cout << '\n';
	return 0;
}
```

```text output-of="basics-data-structures-links.cpp"
10 15 20 30 
```

1. **Line 14:** each node names its neighbors by index: node 0 holds 10, with next 1 and no previous.
2. **Lines 15–17:** the new node 3 sits in memory after the others and joins the list when two links change.
3. **Lines 19–20:** the walk follows `Next` from node 0 until it meets -1, so the values come out in list order, not memory
   order.

The insert changed two links and moved no item, whatever the length of the list: O(1). The price comes elsewhere. To
reach the 100th node you follow 100 links, so reading by position costs O(n). The nodes are scattered, so each step may
miss the cache. An array wins at reading and scanning, a linked list at inserting and removing where you already stand.

A list can live inside the items it links. Instead of separate nodes, each item carries its own links. Strata's scene does
this for its hierarchy. The struct below sits next to every entity.

```cpp src="Strata/src/Strata/Scene/SceneHierarchy.h#L13-L21"
// Not registered with ComponentRegistry (like WorldTransformComponent): never serialized, copied or shown.
struct HierarchyComponent
{
	entt::entity Parent = entt::null;      // entt::null for root entities
	entt::entity FirstChild = entt::null;
	entt::entity LastChild = entt::null;   // Appending a child is O(1)
	entt::entity NextSibling = entt::null; // Siblings in child order (roots: in root order)
	entt::entity PrevSibling = entt::null;
	uint32_t Depth = 0;                    // Roots have depth 0
```

Each entity names its parent, its first and last child, and its previous and next sibling. `LastChild` lets the scene
append a child in O(1): it links the new entity after `LastChild` without walking the list. Removing an entity repairs its
two neighbors, which also takes constant time. Learning a child's position means counting from the first child, so the scene caches each child's
`SiblingIndex` for its hot paths. The [scene graph](../world/scene-graph.md) page shows how the scene keeps these links
in step.

## Stacks, queues and ring buffers

A stack lets you add and remove at one end only, so the last item in is the first item out. Think of plates in a
cupboard. With a vector, `push_back` adds on top and `pop_back` removes from the top, both in O(1) on average. An undo
history is a stack: the newest change is the first to undo. The free list above works as a stack too.

The word has a second meaning in programming: the stack of memory, where each running function keeps its :term[local variables]{id=local-variable}.
That stack also works last in, first out, but it is a different thing.

A **queue** is first in, first out (FIFO): you add at the back and remove at the front, like people waiting in line. A
queue of jobs waiting for a worker thread, a helper that runs work beside the main program, is the usual example, and [Jobs](../core/jobs.md) shows Strata's.

A vector is a poor queue: removing the front shifts all other items, which costs O(n). Two cures exist. You can keep a
`head` index that moves right instead of shifting. Or you can use a double-ended queue, `std::deque`, which adds and
removes at both ends in O(1).

A queue sometimes needs a limit. A log keeps only the last 4,096 lines, and a profiler keeps only the last 600 frames. A
**ring buffer** is a queue of fixed size in one array that, once full, replaces its oldest entry. Two numbers run the
ring: the place of the next write, and the count of filled places. After the last place, the next write returns to place
0, which the remainder of a division does: `(next + 1) % size`.

The program writes 1 to 6 into a ring of four and then prints the entries from oldest to newest.

```cpp sketch="basics-data-structures-ring.cpp"
// A ring buffer of four numbers: the fifth write overwrites the oldest value.
#include <iostream>
#include <vector>

int main()
{
	std::vector<int> slots(4, 0);
	size_t next = 0;  // where the next value goes
	size_t count = 0; // how many slots hold a value
	for (int value = 1; value <= 6; value++)
	{
		slots[next] = value;
		next = (next + 1) % slots.size(); // after the last slot, return to slot 0
		if (count < slots.size())
			count++;
	}

	// Once the buffer is full, the oldest value sits where the next one would go.
	const size_t oldest = count == slots.size() ? next : 0;
	for (size_t offset = 0; offset < count; offset++)
		std::cout << slots[(oldest + offset) % slots.size()] << ' ';
	std::cout << '\n';
	return 0;
}
```

```text output-of="basics-data-structures-ring.cpp"
3 4 5 6 
```

1. **Lines 12–13:** the write goes to `next`, which then advances and wraps around to 0 after the last place.
2. **Lines 18–21:** once the ring is full, the oldest entry sits at `next`, and the loop reads one full round from there.

Trace the ring by hand. After writes 1 to 4 the slots hold `[1, 2, 3, 4]`, and `next` is back at 0. Write 5 goes to slot
0, giving `[5, 2, 3, 4]`. Write 6 goes to slot 1, giving `[5, 6, 3, 4]`, and `next` is 2.

The oldest value, 3, sits at
index 2, so reading from index 2 around the ring gives 3, 4, 5, 6. The memory never grows, and each write costs O(1).

Try it: a ring of 4 receives 10, 20, 30, 40, 50. Which slot does 50 use, and which value does it replace?

:::answer
Slot 0, which held 10, because the fifth write wraps around to the first place.
:::

Strata uses the idea twice. The frame profiler keeps `Capacity` frames, 600 by default, in an array and advances with
`m_NextRecord = (m_NextRecord + 1) % m_Capacity`, in `Strata/src/Strata/Core/FrameProfiler.cpp`. At 60 frames per
second, 600 frames cover 10 seconds. The log keeps its entries in a `LogBuffer`. It acts as a ring buffer but stores the entries in a
`std::deque`: when the buffer is full, `Push` drops the oldest entry from the front, then adds the new one at the back.

## Hash maps find a key without a search

Suppose the scene holds 100,000 entities and a script asks for the one named `Player`. Scanning every name is O(n). A
sorted array allows a binary search but costs O(n) for each insert. A hash map answers in about one step and keeps
inserts cheap.

A **hash function** turns a key, such as a name, into a number.

That number is the key's **hash**, and the same key must always give the same hash.

A **hash map**, also called a hash table, keeps its items in an array of buckets. The bucket number is the hash divided by the bucket count, keeping the
remainder.

Take a toy hash function: add the character codes of the letters. A computer stores each letter as a number, its code: `a`
is 97, `n` is 110 and `t` is 116. The hash of `ant` is 97 + 110 + 116 = 323. With 8 buckets the key lands in bucket
323 % 8 = 3, because 8 × 40 = 320. Finding `ant` costs one hash and one bucket, however many keys the map holds.

Two keys can share a bucket. The word `tan` has the same letters, so its hash is also 323. Two keys in one bucket are a
collision. The usual fix is chaining: each bucket holds a small list, and a lookup compares the wanted key with each entry
in its bucket. The program places four names into 8 buckets.

```cpp sketch="basics-data-structures-hashmap.cpp"
// A hash map's buckets: eight lists, and the sum of the letter codes as the hash function.
#include <iostream>
#include <string>
#include <vector>

size_t HashName(const std::string& name)
{
	size_t sum = 0;
	for (char letter : name)
		sum += static_cast<unsigned char>(letter);
	return sum;
}
int main()
{
	std::vector<std::vector<std::string>> buckets(8);
	for (const std::string name : { "ant", "bee", "tan", "cat" })
		buckets[HashName(name) % buckets.size()].push_back(name);
	for (size_t index = 0; index < buckets.size(); index++)
	{
		std::cout << "bucket " << index << ":";
		for (const std::string& name : buckets[index])
			std::cout << ' ' << name;
		std::cout << '\n';
	}
}
```

```text output-of="basics-data-structures-hashmap.cpp"
bucket 0: cat
bucket 1:
bucket 2:
bucket 3: ant tan
bucket 4: bee
bucket 5:
bucket 6:
bucket 7:
```

1. **Lines 6–12:** the hash function adds the letter codes of the name.
2. **Lines 16–17:** a name goes into the bucket its hash selects, behind any earlier entries.

```mermaid caption="Four keys in eight buckets: ant and tan collide in bucket 3, and a lookup of tan compares two entries." alt="A row of buckets numbered 0 to 7. Bucket 0 holds cat, bucket 3 holds ant followed by tan, bucket 4 holds bee, and the other buckets are empty."
flowchart LR
    B0["bucket 0"] --> C["cat"]
    B3["bucket 3"] --> A["ant"] --> T["tan"]
    B4["bucket 4"] --> E["bee"]
```

To find `tan`, the map hashes it to 323 and takes bucket 3. It compares `tan` with `ant`, which differs, and then with `tan`,
which matches: 2 comparisons.

The lookup stays cheap only while the buckets stay short. The **load factor** is the number of items divided by the number
of buckets. At 4 items in 8 buckets it is 0.5, so a typical bucket holds fewer than one item.

When the load factor passes
a limit, often 1, the map grows. It allocates twice the buckets and puts every key into its new bucket, because the
bucket number depends on the bucket count. That step costs O(n) but is rare, so an insert stays O(1) on average, as with
the dynamic array.

The worst case is O(n), when every key lands in one bucket. A good hash function spreads keys evenly, and the average cost
is O(1).

Two limits follow from the design. First, a hash map has no useful order: the order of its entries depends on
the hash function and on the bucket count, and it changes when the map grows. Second, the hash of a standard library, such
as `std::hash`, is good for one running program only. Never store it in a file or send it to another program, because
another library may compute other numbers. [Data formats](../basics/data-formats.md) explains hashes that stay stable.

A hash set keeps only keys, without values. It answers "is this key in the set?" in O(1), the question of the Coin Run
script at the start of this page.

:::question[What are `std::unordered_map` and `std::unordered_set`?]
Both are the standard library's: a hash map and a hash set. [Generic C++](../basics/cpp-generic.md) teaches the template
form `std::unordered_map<Key, Value>`; read it as "a hash map from a `Key` to a `Value`".
:::

A hash map is also the simplest cache. A cache stores a result already worked out, keyed by what the work needed. The next
request for that key reads the stored result instead of working it out again. The price is memory, and the duty to drop an
entry when its input changes.

Strata uses hash maps twice. The renderer keeps `m_MeshSlotsByHandle`, a `std::unordered_map` from an asset handle, the id of an asset, to the
small number that stands for the mesh. The scene's lookup index finds an entity by its name or tag. Its buckets are
vectors of entities, found by the hash of the name:

```cpp src="Strata/src/Strata/Scene/Scene.h#L695-L700"
struct LookupIndex
{
	bool Built = false;
	std::unordered_map<uint64_t, std::vector<entt::entity>> Buckets;
	std::vector<LookupSlot> Slots;
};
```

Different names can share one hash, so a lookup compares the real strings inside the bucket, and the scene's comment says
so. The index also keeps, for each entity, the key and the entity's position in its bucket. Removal then needs no search:
it is a swap-remove inside the bucket.

:::question[What are `->` and the `&` in the quote below?]
The arrow `->` reaches a member through a pointer, and `&` after a type makes a reference; [Memory in C++](../basics/cpp-memory.md) teaches both. Read `bucket->second` as "the entities of this bucket".
:::

The five lines below fetch the bucket's entities, copy the last one over the removed entity's place, record its new
position and shrink the bucket.

```cpp src="Strata/src/Strata/Scene/Scene.cpp#L782-L786" from="std::vector<entt::entity>& entities = bucket->second;" to="entities.pop_back();" symbol="Scene::RemoveLookupValue"
std::vector<entt::entity>& entities = bucket->second;
const entt::entity moved = entities.back();
entities[slot.Position] = moved;
index.Slots[static_cast<size_t>(entt::to_entity(moved))].Position = slot.Position;
entities.pop_back();
```

Nothing is searched or shifted: one write and one shrink remove the entity. The engine's comment in `Scene.h` says the
removal costs the same for a name that a million entities share.

## Prefix sums and shared arrays

Sometimes many small lists share one big array. A **prefix sum** is a running total: it turns the lengths of the lists into
the place where each list starts. Take four groups with 3, 0, 2 and 4 items. Their starts are 0, then 0 + 3 = 3, then
3 + 0 = 3, then 3 + 2 = 5, and the total is 5 + 4 = 9. Group 2 lives in places 3 and 4 of the shared array, and group 3
lives in places 5 to 8.

```cpp sketch="basics-data-structures-prefix.cpp"
// Prefix sums: where each group's items start in one shared array.
#include <iostream>
#include <vector>

int main()
{
	const std::vector<int> counts = { 3, 0, 2, 4 }; // items in groups 0, 1, 2 and 3
	std::vector<int> starts(counts.size() + 1, 0);
	for (size_t group = 0; group < counts.size(); group++)
		starts[group + 1] = starts[group] + counts[group];

	for (size_t group = 0; group < counts.size(); group++)
		std::cout << "group " << group << " starts at " << starts[group] << " and has " << counts[group] << '\n';
	std::cout << "total " << starts.back() << '\n';
	return 0;
}
```

```text output-of="basics-data-structures-prefix.cpp"
group 0 starts at 0 and has 3
group 1 starts at 3 and has 0
group 2 starts at 3 and has 2
group 3 starts at 5 and has 4
total 9
```

1. **Lines 9–10:** each start is the previous start plus the previous count.
2. **Lines 12–13:** the output lists a start and a count for each group; an empty group has a start but no items.

One array holds all the items, and each group owns a start and a count, two small numbers instead of its own array. A prefix
sum also answers a range question in O(1): the items of groups 1 to 3 number `starts[4]` minus `starts[1]`, 9 − 3 = 6.

Strata's render scene does this for instances. Each proxy stores `m_FirstInstances` and `m_InstanceCounts`: where its
instances start in one shared array, and how many it has. Creating or freeing a proxy takes or returns a range of that
array.

## Arrays of structs and structs of arrays

An **array of structs** (AoS) is the layout you have used so far: one array whose items are structs, each struct holding
all the fields of one thing.

A **struct of arrays** (SoA) turns it around: one array for each field, and a struct holds the arrays. The index i names
the same thing in every array.

Take a particle with a 12-byte position, a 12-byte velocity, a 4-byte life and a 4-byte color: 32 :term[bytes]{id=byte}. A loop that
lowers the life of 1,000 particles reads one 4-byte field per particle. In an array of structs, the fields of one particle
lie side by side, so the processor loads whole neighborhoods of 32 bytes to use 4 of them. The loop sweeps 32,000 bytes.

In
a struct of arrays, the lives lie in one array of 4,000 bytes, and every loaded byte gets used. Eight times fewer bytes
mean fewer cache misses.

```cpp sketch="basics-data-structures-layouts.cpp"
// The bytes an update of one field sweeps in an array of structs and in a struct of arrays.
#include <iostream>
#include <vector>

struct Particle
{
	float Position[3];
	float Velocity[3];
	float Life;
	unsigned Color;
};

int main()
{
	const size_t count = 1000;
	std::vector<Particle> particles(count);
	std::vector<float> lives(count);
	for (Particle& particle : particles)
		particle.Life -= 0.016f; // touches one field of each 32-byte struct
	for (float& life : lives)
		life -= 0.016f; // touches a packed array of that field alone

	std::cout << "array of structs, bytes swept: " << particles.size() * sizeof(Particle) << '\n';
	std::cout << "struct of arrays, bytes swept: " << lives.size() * sizeof(float) << '\n';
}
```

```text output-of="basics-data-structures-layouts.cpp"
array of structs, bytes swept: 32000
struct of arrays, bytes swept: 4000
```

1. **Lines 18–19:** the first loop reads and writes one field in every 32-byte struct.
2. **Lines 20–21:** the second loop does the same work on a packed array of that field.

The struct of arrays costs something. A loop that needs all fields of one particle now touches several arrays. Adding or
removing an item must change every array, so a swap-remove has to run on each one, in step. And the code is longer. As a
guide: use a struct of arrays where a hot loop reads a few fields of very many items, and an array of structs where code
handles whole items.

Strata's renderer calls the layout a **structure of arrays** and uses it for the render scene's proxies, which a draw loop
visits every frame. `RenderScene.h` declares `m_Entities`, `m_Flags`, `m_Transforms`, `m_WorldBounds` and a dozen more
vectors of the same length under the comment "Proxies (structure of arrays)". A pass that tests only bounds reads only
`m_WorldBounds`.

## Sparse sets keep ids and data together

An entity-component system stores one component, a `Transform` for example, for some of the entities. Entity numbers are
spread over a range, say 0 to 1,000,000, but only a few entities have the component. An array with one place per possible
number wastes memory. A list of the entities that have it makes "does entity 700,000 have a `Transform`?" cost O(n).

A **sparse set** answers in O(1) with two arrays. The packed array holds the members side by side. The sparse array has one
place per possible number and records where in the packed array the number sits. Add 5, 2 and 9, in that order:

- `packed` is `[5, 2, 9]`.
- `sparse[5]` is 0, `sparse[2]` is 1 and `sparse[9]` is 2. The other places of `sparse` hold anything.

To ask whether 5 is a member, read `sparse[5]`, which is 0, and check that `packed[0]` is 5. The check matters because the
other places of `sparse` hold anything, and a stale place may still point into `packed`. The test costs two reads.

```mermaid caption="A sparse set after adding 5, 2 and 9: the sparse array points to places in the packed array, which holds the members side by side." alt="Two rows. The packed row holds 5, 2 and 9 in places 0, 1 and 2. The sparse row has places numbered 0 to 9. Arrows run from place 5 to packed place 0, from place 2 to packed place 1, and from place 9 to packed place 2."
flowchart TB
    subgraph packed
        P0["0: 5"]
        P1["1: 2"]
        P2["2: 9"]
    end
    S2["sparse 2"] --> P1
    S5["sparse 5"] --> P0
    S9["sparse 9"] --> P2
```

Removing 5 uses a swap-remove on the packed array. The last member, 9, moves into packed place 0, and `sparse[9]` becomes
0. The packed array shrinks to `[9, 2]`. Asking about 5 now finds `packed[0]` is 9, not 5, so the answer is no.

```cpp sketch="basics-data-structures-sparse.cpp"
// A sparse set: packed holds the members side by side, sparse maps a number to its place in packed.
#include <iostream>
#include <vector>

int main()
{
	std::vector<size_t> packed;
	std::vector<size_t> sparse(16, 0); // the numbers 0 to 15 are possible
	for (size_t id : { 5, 2, 9 })
	{
		sparse[id] = packed.size(); // add: record the place ...
		packed.push_back(id);       // ... and append the member
	}

	const size_t gone = 5;                // remove 5: the last member fills its place
	packed[sparse[gone]] = packed.back();
	sparse[packed.back()] = sparse[gone];
	packed.pop_back();

	for (size_t id : packed)
		std::cout << id << ' ';
	std::cout << "| has 5: " << (sparse[5] < packed.size() && packed[sparse[5]] == 5);
	std::cout << ", has 2: " << (sparse[2] < packed.size() && packed[sparse[2]] == 2) << '\n';
}
```

```text output-of="basics-data-structures-sparse.cpp"
9 2 | has 5: 0, has 2: 1
```

1. **Lines 7–8:** the two arrays; the sparse array has a place for each of the 16 possible numbers.
2. **Lines 11–12:** an add records the place first, then appends the member.
3. **Lines 15–18:** a remove copies the last member into the gap and fixes that member's sparse place: the same swap-remove as before.
4. **Lines 22–23:** a member test reads the sparse place, then checks the packed array: two reads, whatever n is.

Adding, removing and finding all take O(1). The members lie side by side, so a loop over the packed array scans dense
memory, and a component can ride along in a parallel array in the same order. The costs: the sparse array has a place for
every possible number, so it needs memory for the whole range. Removal moves another member, so the order of the packed
array changes, and an index into it is not stable. EnTT keeps the sparse array in pages of 4,096 places, which
`ENTT_SPARSE_PAGE` sets, so it allocates only the pages that hold a member.

Strata's scene stores each component type in one of these. EnTT's `basic_sparse_set` has a `packed` vector of entities and
a paged `sparse` array, and a component type that can move is erased with `swap_and_pop`. [The entity-component
system](../world/ecs.md) builds on this layout. The render scene's `m_ProxyByEntityIndex` is also a sparse array: it maps
an entity's index to the proxy's place, with `c_InvalidIndex` for "none".

Try it: from `packed` `[7, 12]` add 20, then remove 7. What is `packed`, and what is `sparse[20]`?

:::answer
After the add, `packed` is `[7, 12, 20]` and `sparse[20]` is 2. Removing 7 moves 20 into place 0 and sets `sparse[20]` to
0, so `packed` is `[20, 12]`.
:::

## Common mistakes

- **An index kept across a swap-remove.** Symptom: a script reads the wrong item after another item died. The kept index
  now names the item that moved into the gap. Fix: keep a handle with a version, or find the item again after a removal.
- **A reference kept across a growth.** Symptom: a crash or garbage values after an append. The array moved to a new block,
  and the old address points to freed memory. Fix: keep an index, or finish with the reference before you append.
- **A hash map's order relied on.** Symptom: a list comes out in another order on another machine or after another insert.
  The order depends on the hash function and the bucket count. Fix: copy the keys into a vector and sort them.
- **A standard hash stored in a file.** Symptom: a file written by one build finds nothing when another build reads it.
  `std::hash` is not promised to give the same number in another library. Fix: store the key itself, or use a specified
  hash, as [Data formats](../basics/data-formats.md) teaches.

## Summary

- Count an operation's steps as a function of n and write the growth in big-O notation: O(1) is constant, O(log n)
  halves, O(n) scans and O(n²) multiplies; cost on paper meets the cache.
- An array reads by index in O(1) and inserts in O(n). It grows by doubling. Binary search needs a sorted array and O(log n)
  probes. A swap-remove costs O(1), and a free list with versions makes slots safe to hand out again.
- A linked list inserts in O(1) and reads by position in O(n). A stack is last in, first out, a queue is first in, first
  out, and a ring buffer replaces its oldest entry.
- A hash function turns a key into a bucket. Collisions share a bucket, the map grows at a load factor limit, and the average
  lookup costs O(1).
- An array of structs suits whole items, a struct of arrays suits hot loops on few fields, and a sparse set stores sparse
  ids with O(1) add, remove and find.

## Check yourself

1. Inserting an item at the front of an array of n items costs: A O(1), B O(log n), C O(n), D O(n²)?

   :::answer{tests="cost"}
   C. Every one of the n items moves one place right. A is the cost of a swap-remove or of reading by index, and B is the
   cost of binary search.
   :::

2. Slot 3 holds a coin, and a handle `(3, 0)` names it. The coin is destroyed, which makes the slot's version 1, and a new
   coin takes slot 3. Does the old handle still pass the check, and what does the new coin's handle hold?

   :::answer{tests="arrays"}
   The old handle fails: its version 0 differs from the slot's version 1. The new handle holds `(3, 1)`.
   :::

3. A ring buffer has 5 places and is full. Its oldest entry is at place 3. Where does the next write go, and what is lost?

   :::answer{tests="links"}
   The write goes to place 3, and the oldest entry is lost. In a full ring, the next place to write holds the oldest entry.
   :::

4. A hash function adds letter codes, and `ant` and `tan` both give 323. In a map of 8 buckets, what do the two keys share,
   and how many comparisons does a lookup of `tan` need if `ant` came first?

   :::answer{tests="hashing"}
   Both keys land in bucket 3, since 323 % 8 = 3: a collision. A lookup of `tan` compares with `ant` first, then with
   `tan`: 2 comparisons.
   :::

5. A renderer visits 100,000 proxies per frame and tests only their bounds. Which layout suits it, and why?

   :::answer{tests="layouts"}
   A struct of arrays: the bounds lie in one packed array, so the loop reads only the bytes it uses. In an array of structs,
   every proxy's other fields would load with the bounds and mostly go to waste.
   :::

## Practice

1. **Basic.** Give the big-O cost of four operations: reading `items[40]`, searching n names in no order, a binary search in
   n sorted numbers, and inserting at index 0 of n items.

   :::answer[Worked solution]{tests="cost"}
   Reading by index: O(1). Searching in no order: O(n). Binary search: O(log n). Inserting at the front: O(n), since all
   items move.
   :::

2. **Basic.** Trace `[10, 20, 30, 40, 50]` through these steps: swap-remove index 0, append 60, swap-remove index 2. Write the
   array after each step.

   :::answer[Worked solution]{tests="arrays"}
   After the first step, 50 moves to index 0: `[50, 20, 30, 40]`. After the append: `[50, 20, 30, 40, 60]`. After the
   third step, 60 moves into index 2: `[50, 20, 60, 40]`.
   :::

3. **Medium.** Use the letter-sum hash and 5 buckets. Place `act`, `cat`, `dog` and `ant` in that order. Give each bucket, the
   load factor, and the comparisons a lookup of `cat` needs. The codes are `a` 97, `c` 99, `d` 100, `g` 103, `n` 110,
   `o` 111 and `t` 116.

   :::answer[Worked solution]{tests="hashing"}
   The sums are `act` 312, `cat` 312, `dog` 314 and `ant` 323. With 5 buckets: 312 % 5 = 2, 314 % 5 = 4, 323 % 5 = 3. So bucket 2
   holds `act` then `cat`, bucket 3 holds `ant`, and bucket 4 holds `dog`. The load factor is 4 / 5 = 0.8. A lookup of
   `cat` compares with `act`, then with `cat`: 2 comparisons.
   :::

4. **Medium.** Choose a structure for each of four needs and say why. The needs are an undo history, the last 100 chat lines, a
   search by name among 50,000 assets, and damage events handled in the order they happened.

   :::answer[Worked solution]{tests="links,layouts"}
   Undo history: a stack, since the newest action is undone first. The last 100 chat lines: a ring buffer, since the
   oldest line is replaced. The search by name: a hash map from the name to the asset, an O(1) lookup in place of a scan of
   50,000 names. Damage events: a queue, which serves them first in, first out.
   :::

5. **Hard.** Write `RemoveCoin(Coins&, size_t index)` for a struct of two vectors, `Names` and `Values`, that removes one coin in
   O(1) and keeps both arrays in step. Start from `{ "a", "b", "c", "d" }` and `{ 1, 5, 10, 25 }`, remove index 1 and print the
   rest.

   :::answer[Worked solution]{tests="arrays,layouts" solution="sketches/basics-data-structures-soa-remove.cpp"}
   Each array moves its last element into the gap and then shrinks, so the pair at one index still belongs together.

   ```cpp sketch="basics-data-structures-soa-remove.cpp"
   // A struct of arrays with a swap-remove: every array moves its last element into the gap.
   #include <iostream>
   #include <string>
   #include <vector>

   struct Coins { std::vector<std::string> Names; std::vector<int> Values; };

   void RemoveCoin(Coins& coins, size_t index)
   {
   	coins.Names[index] = coins.Names.back();
   	coins.Values[index] = coins.Values.back();
   	coins.Names.pop_back();
   	coins.Values.pop_back();
   }

   int main()
   {
   	Coins coins = { { "a", "b", "c", "d" }, { 1, 5, 10, 25 } };
   	RemoveCoin(coins, 1);
   	for (size_t index = 0; index < coins.Names.size(); index++)
   		std::cout << coins.Names[index] << '=' << coins.Values[index] << ' ';
   	std::cout << '\n';
   	return 0;
   }
   ```

   ```text output-of="basics-data-structures-soa-remove.cpp"
   a=1 d=25 c=10 
   ```

   1. **Lines 10–11:** both arrays copy their last element into the gap.
   2. **Lines 12–13:** both arrays shrink, so the arrays stay the same length.
   3. **Line 19:** the call removes index 1, the coin `b`.

   The coin `d=25` now lives at index 1. A kept index for it would be wrong.
   :::

6. **Hard.** Optional, on Coin Run: your project from [Coin Run](../make/project-coin-run.md), or Checkpoint 4 at the end of [Ship the finished game](../make/project-coin-run.md#ship-the-finished-game), opened with **File ▸ Open Project...**. Keep the collected coins' names
   in a `std::vector` and in a hash set. Remove `Coin3` from both, using a swap-remove for the vector, and count the steps of each.

   :::answer[Worked solution]{tests="cost,hashing" solution="sketches/basics-data-structures-coinrun.cpp"}
   The vector search compares names until `Coin3` matches, 3 comparisons here, and the swap-remove adds one write: O(n) for
   the search and O(1) for the removal. The set erase hashes the name and works in one bucket: O(1) on average. The
   vector's order changed, because `Coin6` moved into the gap, and the set has no order.

   ```cpp sketch="basics-data-structures-coinrun.cpp"
   // Coin Run: collected coin names in a vector (linear search, swap-remove) and in a hash set.
   #include <iostream>
   #include <string>
   #include <unordered_set>
   #include <vector>

   int main()
   {
   	std::vector<std::string> collected = { "Coin1", "Coin2", "Coin3", "Coin4", "Coin5", "Coin6" };
   	std::unordered_set<std::string> collectedSet(collected.begin(), collected.end());

   	size_t index = 0;
   	while (collected[index] != "Coin3")
   		index++; // one comparison per step: index + 1 in all (Coin3 is known to be there)
   	collected[index] = collected.back(); // swap-remove: one write
   	collected.pop_back();
   	const size_t erased = collectedSet.erase("Coin3"); // one hash, one bucket

   	std::cout << "vector: " << index + 1 << " comparisons, " << collected.size() << " left\n";
   	std::cout << "set: " << erased << " erased, " << collectedSet.size() << " left\n";
   	return 0;
   }
   ```

   ```text output-of="basics-data-structures-coinrun.cpp"
   vector: 3 comparisons, 5 left
   set: 1 erased, 5 left
   ```

   1. **Lines 13–14:** the loop compares one name per step, so `index + 1` comparisons find `Coin3`.
   2. **Lines 15–16:** the swap-remove copies the last name over `Coin3` and shrinks the vector.
   3. **Line 17:** the set erases by hash: no search through the other names.
   :::

## Where the book uses it

- [Trees and graphs](../basics/trees-graphs.md) builds trees, heaps and graphs from the arrays, links and indices of this page.
- [The scene graph](../world/scene-graph.md) keeps its parent and child links as a linked list inside a component.
- [The entity-component system](../world/ecs.md) stores components in sparse sets, which this page builds by hand.
- [Generic C++](../basics/cpp-generic.md) teaches the standard library containers that implement these structures.

## Further reading

- cppreference, "Containers library": every standard container with the cost of each operation; intermediate.
- Robert Nystrom, "Game Programming Patterns", chapter "Data Locality": why the order of data in memory decides speed in a
  game; beginner.
- Thomas Cormen and others, "Introduction to Algorithms": the full treatment of costs, hash tables and amortized analysis;
  advanced.
