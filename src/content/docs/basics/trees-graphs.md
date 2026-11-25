---
id: basics/trees-graphs
title: "Data structures II: trees, heaps, graphs and sorting"
description: "Trees, search trees, heaps, spatial trees, graphs, union-find and sorting, each drawn, computed by hand, written in a few lines of C++ and costed."
kind: primer
size: M
tracks: [B, E]
needs: [basics/data-structures]
time: 60
learn:
  - id: walks
    text: trace a depth-first walk with a stack and a breadth-first walk with a queue over a tree and over a graph
  - id: search-trees
    text: compute how many steps a search in a balanced tree takes and explain how a spatial tree halves the space to search
  - id: heap
    text: trace the push and the pop of a binary heap and choose a priority queue for work that waits by priority
  - id: graphs
    text: find a cycle in a directed graph, name a topological order of a dependency graph and merge sets with union-find
  - id: sorting
    text: compare a sort in O(n log n) with a stable radix sort in O(n)
status: final
---

::::test-out

1. The root R has the children A and B, in this order. A has C and D, D has F, and B has E. Write the order of a depth-first walk that takes the first child first, and of a breadth-first walk.

   :::answer{tests="walks"}
   Depth-first: R A C D F B E. Breadth-first: R A B C D E F.
   :::

2. A heap that gives out the smallest number first is the array [2, 5, 3, 9, 6]. Which number does a pop give, and which comes next?

   :::answer{tests="heap"}
   The pop gives 2. The 6 takes the root's place and swaps with the 3: [3, 5, 6, 9]. The next pop gives 3.
   :::

3. A directed graph has the arrows A to B, B to C, C to D, D to B and A to E. Does it have a cycle?

   :::answer{tests="graphs"}
   Yes: B to C to D to B leads back to its start.
   :::

4. A balanced search tree holds 1,000,000 keys. About how many steps find one key?

   :::answer{tests="search-trees"}
   About 20, because each step halves the keys that remain and 2 to the power 20 is 1,048,576.
   :::

5. Sort 31, 12, 22, 11 by the last digit only, so that numbers with the same last digit keep their order.

   :::answer{tests="sorting"}
   31, 11, 12, 22. This is one pass of a radix sort.
   :::

::::

## Why you will need this

A level is a tree of entities, loading work waits in a queue that serves the urgent jobs first, and engine modules start in an order that respects what each one needs.

[Engine modules](../core/engine-modules.md) puts modules in order with a graph. [Residency](../assets/residency.md) keeps assets in memory with queues by priority. [Collision detection](../physics/collision-detection.md) finds the shapes that can touch with a tree of boxes.

Each idea goes from a drawing to numbers by hand, a few lines of C++ and its cost in big-O. The costs use the logarithms of [Numbers](../basics/numbers.md) and the queues of [Data structures I](../basics/data-structures.md).

## A tree is nodes joined by parent and child links

A level is more than a list of entities: the wall group holds a north and a south wall, and the coin group holds every coin. The figure draws a small level that way.

```mermaid caption="A small level as a tree. The top node is the root, and the nodes without children are the leaves. The wall group with its two walls is one subtree." alt="Seven nodes drawn from the top down. Level has three children: Walls, Coins and Player. Walls has the children North and South, and Coins has the child Gold."
flowchart TD
  Level --> Walls
  Level --> Coins
  Level --> Player
  Walls --> North
  Walls --> South
  Coins --> Gold
```

A **tree** is a set of nodes in which one node, the root, has no parent, and every other node has exactly one parent. The nodes right below a node are its children, and a node without children is a leaf.

A **subtree** is a node together with everything that hangs below it: Walls with North and South is a subtree of three nodes. The depth of a node counts the links from the root to it. Level has depth 0, Walls depth 1 and North depth 2.

Strata keeps the scene hierarchy as a tree. The `RelationshipComponent` of an entity holds its `Parent` and a `std::vector` of `Children` (`Strata/src/Strata/Scene/Components.h`), in the order the editor shows. An entity without a parent is a root, and a script lists the roots with `Scene::GetRootEntities`. A node with a second parent, or one that becomes its own ancestor, breaks the tree, so `Scene::SetParent` returns false when a change would make a cycle (`Strata/src/Strata/Scene/Scene.h`).

## A walk visits every node with a stack or a queue

To use every entity of a level, a program visits each node once. A depth-first walk follows one branch as deep as it goes, then comes back and takes the next. A breadth-first walk visits all nodes of depth 1, then all of depth 2, and so on.

The walks differ only in what holds the nodes still to visit. Depth-first takes the node pushed last, so it needs a stack. Breadth-first takes the node added first, so it needs a queue.

:::example[Both walks of the level by hand]
Depth-first: start the stack with [Level]. Pop Level and push its children backwards: [Player, Coins, Walls]. Pop Walls and push South, then North: [Player, Coins, South, North]. The walk continues with North, South, Coins, Gold and Player, so the order is Level, Walls, North, South, Coins, Gold, Player.

Breadth-first: start the queue with [Level]. Take Level from the front and add its children at the back: [Walls, Coins, Player]. Walls adds North and South, and Coins adds Gold, so the order is Level, Walls, Coins, Player, North, South, Gold.
:::

Try it: which order does a breadth-first walk give for R with the children A and B, where A has the child C?

:::answer
R, A, B, C: A and B have depth 1, so both come before C.
:::

The program keeps the tree as a list of nodes, each with a name and the positions of its children. Look at the stack: the walk takes the last item and pushes the children in reverse.

```cpp sketch="basics-trees-graphs-depth.cpp"
// A depth-first walk of a tree with a stack: go down one branch to its end, then come back.
#include <iostream>
#include <string>
#include <vector>

struct Node
{
	std::string Name;
	std::vector<int> Children; // positions of the children in the list, in order
};

int main()
{
	const std::vector<Node> tree = { { "Level", { 1, 2, 3 } }, { "Walls", { 4, 5 } }, { "Coins", { 6 } }, { "Player", {} }, { "North", {} }, { "South", {} }, { "Gold", {} } };
	std::vector<int> stack = { 0 }; // the root waits first
	while (!stack.empty())
	{
		const Node& node = tree[stack.back()]; // the node pushed last goes first
		stack.pop_back();
		std::cout << node.Name << ' ';
		for (size_t child = node.Children.size(); child > 0; child--) // backwards, so the first child pops first
			stack.push_back(node.Children[child - 1]);
	}
	std::cout << '\n';
}
```

```text output-of="basics-trees-graphs-depth.cpp"
Level Walls North South Coins Gold Player 
```

1. **Lines 18–19:** the last item pushed is taken first, which makes the walk depth-first.
2. **Lines 21–22:** the loop counts down, so the first child ends on top and comes out first.

Each node goes into the container once and comes out once, so a walk costs $O(n)$ for $n$ nodes.

## A search tree keeps its keys in order

A sorted array finds a key with :term[binary search]{id=binary-search} in $O(\log n)$ steps, but an insert shifts every larger item, which costs $O(n)$. A **binary search tree** avoids both costs: each node has at most two children, every key in its left subtree is smaller than its own, and every key in its right subtree is larger.

:::example[Find 60 among seven keys]
Insert 50, 30, 70, 20, 40, 60 and 80 in this order, and the tree looks like the figure. To find 60, compare with the root: 60 is larger than 50, so go right. Compare with 70: 60 is smaller, so go left. The node is 60, after three comparisons.
:::

Try it: how many comparisons find 40?

:::answer
Three: smaller than 50, so left; larger than 30, so right; then the node.
:::

```mermaid caption="A binary search tree of seven keys. Every key to the left of a node is smaller than it, and every key to the right is larger." alt="Node 50 at the top with the children 30 and 70. Node 30 has the children 20 and 40, and node 70 has the children 60 and 80."
flowchart TD
  n50["50"] --> n30["30"]
  n50 --> n70["70"]
  n30 --> n20["20"]
  n30 --> n40["40"]
  n70 --> n60["60"]
  n70 --> n80["80"]
```

A tree of $h$ levels holds at most $2^h - 1$ keys, and each comparison removes one level. A full tree of 1,000,000 keys has about 20 levels, since $2^{20}$ is 1,048,576, so a search, an insert or a removal takes about 20 steps. Reading each left subtree, then the node, then the right subtree gives the keys in order.

The shape depends on the insert order. Insert 1 to 7 in sorted order and each key goes right of the last: the tree becomes a chain, and a search takes 7 steps, which is $O(n)$. A self-balancing tree turns a few links after each insert, which keeps its height within a small multiple of $\log_2 n$.

An **ordered map** is a map built on such a tree: it finds a key in $O(\log n)$ and lists its keys in order, which a :term[hash map]{id=hash-map} cannot do. Each node is its own block of memory, and the repairs change links but never move a node. A reference to an entry stays valid while other entries come and go, which a vector's items cannot promise. The price is one block per node and a pointer to follow at each step. C++ offers it as `std::map`, which [Generic C++](../basics/cpp-generic.md) teaches.

## A heap hands out the smallest item first

A queue serves jobs in the order they came. A loading queue should not: the wall in front of the camera is needed now, and a far room can wait. A **priority queue** gives out the waiting item with the best priority, whatever its arrival time.

A **binary heap** is the usual priority queue: a tree stored in an array, in which every node is no larger than its children, so the smallest item sits at index 0. The node at index $i$ has its children at $2i + 1$ and $2i + 2$ and its parent at $(i - 1) / 2$, rounded down.

```mermaid caption="A heap of six numbers. Each node is no larger than its children, so the smallest number is on top. Read row by row, the nodes give the array 1, 3, 2, 5, 4, 8." alt="Node 1 at the top with the children 3 and 2. Node 3 has the children 5 and 4, and node 2 has the child 8."
flowchart TD
  h0["1"] --> h1["3"]
  h0 --> h2["2"]
  h1 --> h3["5"]
  h1 --> h4["4"]
  h2 --> h5["8"]
```

:::example[Push and pop by hand]
A push puts the new item at the end and lets it rise while it is smaller than its parent. Push 5, 3, 8, 1, 4, 2 into an empty heap. After 5, 3 and 8 the array is [3, 5, 8]. The 1 lands at index 3 under 5, swaps with 5, then with 3: [1, 3, 8, 5]. The 4 stays under 3, and the 2 swaps with 8: [1, 3, 2, 5, 4, 8].

A pop returns the first item, moves the last item to the root and lets it sink, swapping with the smaller child while a child is smaller. The pop returns 1, and the 8 swaps with 2: [2, 3, 8, 5, 4]. The next pop returns 2.
:::

Try it: push 7, 2 and 9 into an empty heap. What is the array?

:::answer
[2, 7, 9]: the 2 swaps with 7, and the 9 stays under 2.
:::

A push or a pop moves along one path of the tree, so each costs $O(\log n)$, and a look at the smallest item costs $O(1)$. The program pops the six numbers of the figure.

```cpp sketch="basics-trees-graphs-heap.cpp"
// Taking the smallest number out of a binary heap kept in a vector.
#include <cstdio>
#include <utility>
#include <vector>

int Pop(std::vector<int>& heap)
{
	const int smallest = heap[0];
	heap[0] = heap.back(); // the last item takes the root's place, then sinks
	heap.pop_back();
	for (size_t i = 0, child = 1; child < heap.size(); i = child, child = 2 * i + 1)
	{
		if (child + 1 < heap.size() && heap[child + 1] < heap[child]) child++; // the smaller child
		if (heap[i] <= heap[child])
			break; // the item is no larger than both children: it stays
		std::swap(heap[i], heap[child]);
	}
	return smallest;
}

int main()
{
	for (std::vector<int> heap = { 1, 3, 2, 5, 4, 8 }; !heap.empty();)
		std::printf("%d\n", Pop(heap));
}
```

```text output-of="basics-trees-graphs-heap.cpp"
1
2
3
4
5
8
```

1. **Lines 9–10:** the last item takes the root's place and sinks from there.
2. **Lines 14–15:** an item no larger than its children is in place, so the loop stops.

Strata's queue of asset loads keeps its requests in an ordered map, not a heap, because requests are raised or cancelled while they wait, and a heap cannot reach one in its middle. The first entry is always the next load. The key of an entry is its priority, then the negative of its score, then the order of the request.

:::question[What are `std::map` and `std::tuple` here?]
`std::map` is the ordered map of this page, and `std::tuple` joins several values into one key. [Generic C++](../basics/cpp-generic.md) teaches both.
:::

The key below sorts the smaller value first. A high priority has a small number, and a larger score must go first, so the key stores the score with its sign flipped.

```cpp src="Strata/src/Strata/Asset/AssetStreamingQueue.h#L117-L121"
// Ascending order is dispatch order: priority (High first), then score (highest first), then request order.
using Key = std::tuple<uint8_t, float, uint64_t>;

static Key MakeKey(AssetPriority priority, float score, uint64_t order) { return Key(static_cast<uint8_t>(priority), -score, order); }
bool CanDispatchLocked() const;
```

The request order breaks ties: the earlier request goes first. [Loading](../assets/loading.md) shows how the queue keeps a burst of requests from filling memory. The open set of the A* path search is a heap too; see artificial intelligence (AI) in [Game AI](../appendix/game-ai.md).

## A spatial tree halves the space to search

A level may hold 10,000 boxes, and testing each costs $O(n)$. A **spatial tree** cuts the space into parts, and each step skips every part that cannot hold the answer. Halving the space at each step gives the $\log n$ of a search tree.

Three shapes are common. A quadtree splits a square into four quarters, and each quarter splits again. An octree does the same with a cube and eight parts. A bounding volume hierarchy groups the objects: each node holds the smallest box around everything below it, and a query that misses the box skips the whole subtree.

:::example[The coin at (11, 3) in a room 16 metres wide]
Four halvings find the cell, 1 m wide, that holds the point (11, 3). The first cell is 8 m wide: x from 8 to 16, y from 0 to 8. The next are 4 m (x 8 to 12, y 0 to 4), 2 m (x 10 to 12, y 2 to 4) and 1 m (x 11 to 12, y 3 to 4). A scan of the 256 cells takes up to 256 looks; the tree takes 4.
:::

Try it: how many halvings reach a cell 1 m wide in a square 64 m wide?

:::answer
Six: 64, 32, 16, 8, 4, 2, 1.
:::

Strata uses the idea twice. The shadow atlas, the large texture that holds the shadows of local lights, hands out its tiles from a quadtree whose free quarters merge again (`Strata/src/Strata/Renderer/ShadowAtlasAllocator.h`). Its physics library, box3d, keeps the boxes of its shapes in bounding volume trees (`Strata/vendor/box3d/src/dynamic_tree.c`), a topic of [Collision detection](../physics/collision-detection.md).

## A graph lets a node have many parents

A material needs textures, and two materials can need the same texture. In a tree, that texture would need two parents. A **graph** is a set of nodes joined by edges, with no rule about how many edges a node has. In a **directed graph**, every edge is an arrow from one node to another.

A **dependency graph** is a directed graph in which an arrow from A to B says that A needs B. Strata records one for assets: the scan in `Strata/src/Strata/Asset/AssetDependencies.h` lists the assets that a scene or a material refers to, and [References](../assets/references.md) uses the lists.

```mermaid caption="A dependency graph of one level. An arrow from one node to another means that the first needs the second. The texture is reached by two paths." alt="Level has arrows to Wall and to Floor. Wall and Floor both have an arrow to Stone, and Stone has an arrow to Image."
flowchart TD
  Level --> Wall
  Level --> Floor
  Wall --> Stone
  Floor --> Stone
  Stone --> Image
```

A walk from Level reaches Stone by two paths. Without a record of the nodes it has seen, the walk visits Stone twice and Image twice. With a list of visited nodes, checked when a node would join the queue, each node appears once. A walk costs $O(V + E)$ for $V$ nodes and $E$ edges.

```cpp sketch="basics-trees-graphs-graph.cpp"
// A breadth-first walk of a graph in which two paths lead to Stone: the visited list stops a second visit.
#include <iostream>
#include <string>
#include <vector>

int main()
{
	const std::vector<std::string> names = { "Level", "Wall", "Floor", "Stone", "Image" };
	const std::vector<std::vector<int>> arrows = { { 1, 2 }, { 3 }, { 3 }, { 4 }, {} }; // Level to Wall and Floor, both to Stone, Stone to Image
	std::vector<bool> visited = { true, false, false, false, false }; // the walk starts at Level
	std::vector<int> queue = { 0 };
	for (size_t head = 0; head < queue.size(); head++) // read at the head, add at the end
	{
		const int node = queue[head];
		std::cout << names[node] << ' ';
		for (int next : arrows[node])
		{
			if (visited[next])
				continue; // reached before by another path
			visited[next] = true;
			queue.push_back(next);
		}
	}
	std::cout << '\n';
}
```

```text output-of="basics-trees-graphs-graph.cpp"
Level Wall Floor Stone Image 
```

1. **Line 12:** the queue keeps a head position that grows, so nothing moves.
2. **Lines 18–21:** a node seen before is skipped, and a new one is marked when it joins the queue.

## A cycle has no first node

A **cycle** is a path of arrows that leads back to its start. If Level needed Wall, Wall needed Stone and Stone needed Level, none of them could come first. To find a cycle, walk depth-first and remember the nodes of the current path: an arrow to a node still on the path closes a cycle.

When a dependency graph has no cycle, its nodes have a **topological order**: a list in which every node comes after the nodes it needs. Image, Stone, Wall, Floor, Level is one for the level above. [Engine modules](../core/engine-modules.md) teaches Kahn's algorithm, the usual way to find it. Strata starts its engine modules in such an order, and when modules wait for each other it names the members of the cycle in the error `engine modules ... depend on each other in a cycle` (`Strata/src/Strata/Core/EngineModule.cpp`).

## Union-find joins sets and asks who belongs together

Some questions ask only whether two things are in the same group, while items join groups one pair at a time and a group never splits. **Union-find** is an array in which each item holds the number of a parent, a group's root holds its own number, and two items belong together when their roots are equal.

:::example[Six items and four joins]
Start with the parents [0, 1, 2, 3, 4, 5]: every item is a root. Join 0 and 1 by pointing the root of 1 at 0: [0, 0, 2, 3, 4, 5]. Join 2 and 3: [0, 0, 2, 2, 4, 5]. Join 1 and 3: the root of 1 is 0, the root of 3 is 2, so 2 points at 0: [0, 0, 0, 2, 4, 5]. Join 4 and 5, and two groups remain: [0, 0, 0, 2, 4, 4].

To find the root of 3, follow 3 to 2 to 0, then point 3 straight at 0: [0, 0, 0, 0, 4, 4]. The change is called path compression, and the next question about 3 takes one step.
:::

Try it: what is the root of 5 after these steps?

:::answer
4: the parent of 5 is 4, and the parent of 4 is 4 itself.
:::

With path compression, and with the shorter tree joined under the taller, a question costs close to :term[constant time]{id=constant-time} on average. A graph walk finds the groups only after it has seen every edge, while union-find answers as the pairs arrive. Strata's physics library uses it: bodies that touch form an island, and when a touch ends, `b3SplitIsland` finds the pieces with a union-find (`Strata/vendor/box3d/src/island.c`).

## Sorting costs n log n unless the keys help

A renderer draws faster when draws that share a material come one after the other, so it sorts them by a key. A sort that compares keys needs about $n \log_2 n$ comparisons. $O(n \log n)$ is read "order n log n".

The count comes from halving: a merge sort splits the list in halves until single items remain, then merges them back. Eight items need 3 levels of 8 items each, about 24 steps. For a million items, $n \log_2 n$ is about 20 million steps, against 500 billion for $n^2 / 2$.

A **stable sort** keeps the order of items with equal keys, such as draws with the same material. A **radix sort** never compares two keys: it sorts by one digit of the key at a time, the lowest digit first, and each pass is stable.

:::example[Eight numbers, three passes]
Sort 170, 45, 75, 90, 802, 24, 2, 66. By the ones digit: 170, 90, 802, 2, 24, 45, 75, 66. By the tens digit, equal digits keeping their order: 802, 2, 24, 45, 66, 170, 75, 90. By the hundreds digit: 2, 24, 45, 66, 75, 90, 170, 802. The second pass shows why stability matters: 170 stays before 75 because the first pass put it there.
:::

Try it: sort 53, 21, 55, 23, 51 by the ones digit, then by the tens digit. What is the list after each pass?

:::answer
After the ones digit: 21, 51, 53, 23, 55. After the tens digit: 21, 23, 51, 53, 55.
:::

A computer takes a :term[byte]{id=byte} as the digit, with 256 values, so a 32-bit key needs four passes. A pass counts the keys of each byte value, turns the counts into the start of each bucket, and copies each key to the next free place there. In the program, `(key >> shift) & 0xFF` selects the byte the pass sorts by. The cost is $O(kn)$ for $k$ bytes per key, which is $O(n)$ when $k$ is fixed. The price is a second array of the same size.

```cpp sketch="basics-trees-graphs-radix.cpp"
// Radix sort of 32-bit keys: four stable passes, one byte of the key each, the lowest byte first.
#include <cstdint>
#include <cstdio>
#include <vector>

void RadixSort(std::vector<uint32_t>& keys)
{
	std::vector<uint32_t> scratch(keys.size());
	for (uint32_t shift = 0; shift < 32; shift += 8)
	{
		uint32_t start[257] = {}; // first the count of each byte value, then where its bucket starts
		for (uint32_t key : keys) start[((key >> shift) & 0xFF) + 1]++;
		for (int bucket = 0; bucket < 256; bucket++) start[bucket + 1] += start[bucket];
		for (uint32_t key : keys) scratch[start[(key >> shift) & 0xFF]++] = key; // in order: equal bytes keep their order
		keys.swap(scratch);
	}
}

int main()
{
	std::vector<uint32_t> keys = { 170, 45, 75, 90, 802, 24, 2, 66, 70000, 300 };
	RadixSort(keys);
	for (uint32_t key : keys) std::printf("%u ", key);
	std::printf("\n");
}
```

```text output-of="basics-trees-graphs-radix.cpp"
2 24 45 66 75 90 170 300 802 70000 
```

1. **Lines 11–13:** the counts of each byte value become the start of each bucket.
2. **Line 14:** the keys are copied in their old order, which makes the pass stable.

Strata sorts the frame's draws this way. `RadixSort` in `Strata/src/Strata/Core/RadixSort.cpp` sorts items by a 64-bit key, stably, one byte per pass, and skips a byte that is equal in every key. Below is the step that copies the items of one pass.

```cpp src="Strata/src/Strata/Core/RadixSort.cpp#L54-L62" from="for (uint32_t& bucket : histogram)" to="(*destination)[histogram[(item.Key >> shift) & 0xFF]++] = item;" symbol="RadixSort"
for (uint32_t& bucket : histogram)
{
	const uint32_t size = bucket;
	bucket = offset;
	offset += size;
}
const uint32_t shift = shifts[pass];
for (const SortItem& item : *source)
	(*destination)[histogram[(item.Key >> shift) & 0xFF]++] = item;
```

Radix sort does not always win: `SortIndices` in the same file sorts lists of fewer than 256 values with `std::sort`, because the passes cost more than they save on a short list.

## Common mistakes

- **A recursive walk of a deep tree.** A function that calls itself uses a little of the call stack at each level. Symptom: a crash on a very deep hierarchy. Fix: keep your own stack in a vector.
- **A graph walk without a visited list.** Symptom: nodes visited many times, and an endless loop when the graph has a cycle. Fix: mark a node when it joins the queue, and skip marked nodes.
- **A search tree that never balances.** Symptom: lookups that slow as keys arrive in sorted order. Fix: use a self-balancing tree, such as an ordered map.

## Summary

- A depth-first walk uses a stack and a breadth-first walk a queue; a graph walk also needs a visited list.
- A balanced search tree finds a key in about $\log_2 n$ steps, in order and with nodes in place; a spatial tree halves the space the same way.
- A binary heap lives in an array, gives out the smallest item in $O(\log n)$ and serves work by priority.
- A graph without a cycle has a topological order, and union-find merges sets.
- A comparison sort costs $O(n \log n)$. A stable radix sort costs $O(n)$ for keys of fixed size.

## Check yourself

1. Does a breadth-first walk keep its nodes in a stack or in a queue?

   :::answer{tests="walks"}
   In a queue: it takes the node added first. A stack gives the depth-first order.
   :::

2. The heap is [1, 4, 2, 9, 5, 3]. Which indices hold the children of index 1, and which index holds the parent of index 5?

   :::answer{tests="heap"}
   The children of index 1 are at 3 and 4. The parent of index 5 is at $(5 - 1) / 2 = 2$.
   :::

3. 1,000 keys arrive in sorted order in a search tree that never balances. How many steps find the last one, and how many in a balanced tree?

   :::answer{tests="search-trees"}
   The tree is a chain, so 1,000 steps. A balanced tree has about 10 levels, since $2^{10}$ is 1,024.
   :::

4. A dependency graph has the arrows Level to Wall, Wall to Stone and Stone to Image. Does adding Image to Level make a cycle?

   :::answer{tests="graphs"}
   Yes: Level, Wall, Stone, Image and back to Level. No topological order exists any more.
   :::

5. Why must each pass of a radix sort be stable?

   :::answer{tests="sorting"}
   A pass sorts only by its own digit, so keys with an equal digit must keep the order the earlier passes gave them.
   :::

## Practice

1. **Basic.** Push 7, 2, 9 and 4 in this order into an empty heap that gives out the smallest number first. Write the array after each push.

   :::answer[Worked solution]{tests="heap"}
   [7]; then 2 rises above 7: [2, 7]; then 9 stays: [2, 7, 9]; then 4 lands at index 3 under 7, swaps with it and stops under 2: [2, 4, 9, 7].
   :::

2. **Hard.** Write a function that tells whether a directed graph has a cycle. Test it on the chain 0 to 1 to 2 to 3, and on the same graph with an arrow from 3 back to 1.

   :::answer[Worked solution]{tests="graphs walks" solution="sketches/basics-trees-graphs-cycle.cpp"}
   Walk depth-first and give each node a state: new, on the current path or done. An arrow to a node on the path is a cycle.

   ```cpp sketch="basics-trees-graphs-cycle.cpp"
   // Finding a cycle in a directed graph: a depth-first walk meets a node that is still on its own path.
   #include <cstdio>
   #include <vector>

   // A node's state is 0 (new), 1 (on the current path) or 2 (done).
   bool HasCycle(const std::vector<std::vector<int>>& arrows, int node, std::vector<int>& state)
   {
   	state[node] = 1;
   	for (int next : arrows[node])
   	{
   		if (state[next] == 1)
   			return true; // an arrow back to the current path closes a loop
   		if (state[next] == 0 && HasCycle(arrows, next, state))
   			return true;
   	}
   	state[node] = 2;
   	return false;
   }

   int main()
   {
   	std::vector<int> first(4), second(4); // all zero: every node is new
   	std::printf("chain: %d\n", HasCycle({ { 1 }, { 2 }, { 3 }, {} }, 0, first));
   	std::printf("loop: %d\n", HasCycle({ { 1 }, { 2 }, { 3 }, { 1 } }, 0, second));
   }
   ```

   ```text output-of="basics-trees-graphs-cycle.cpp"
   chain: 0
   loop: 1
   ```

   1. **Line 8:** a node is on the path while its arrows are walked, and line 16 marks it done.
   2. **Lines 11–12:** an arrow to a node on the path closes a loop.

   The program prints 0 for the chain and 1 for the loop.
   :::

3. **Hard.** Optional, on your Coin Run or Checkpoint 4 of [Ship the finished game](../make/project-coin-run.md#ship-the-finished-game): write a script that walks the level's hierarchy from its roots. Walk it depth-first with a stack and breadth-first with a queue, both kept in a `std::vector`, and log each entity's name with its depth. The `Walls` entity must appear.

   :::answer[Worked solution]{tests="walks"}
   The structure is that of the sketches, with a depth stored beside each entity. The depth-first version, run from `OnCreate`, in :term[pseudocode]{id=pseudocode}:

   ```cpp pseudocode
   struct Visit { Entity Node; int Depth; };

   void OnCreate()
   {
   	std::vector<Visit> stack;
   	for (Entity root : Scene::GetRootEntities())
   		stack.push_back({ root, 0 });
   	while (!stack.empty())
   	{
   		Visit visit = stack.back();
   		stack.pop_back();
   		Log::Info(visit.Depth, " ", visit.Node.GetName());
   		std::vector<Entity> children = visit.Node.GetChildren();
   		for (size_t i = children.size(); i > 0; i--)
   			stack.push_back({ children[i - 1], visit.Depth + 1 });
   	}
   }
   ```

   1. **Lines 6–7:** every root starts on the stack with depth 0.
   2. **Line 15:** a child's depth is its parent's depth plus 1.

   For the breadth-first version, read the visits from a vector at a growing head position.
   :::

## Where the book uses it

- [Engine modules](../core/engine-modules.md) orders modules by a topological order of a dependency graph.
- [Residency](../assets/residency.md) keeps assets in memory by priority, with queues like this page's.
- [Generic C++](../basics/cpp-generic.md) teaches `std::map`, the ordered map.
- [Collision detection](../physics/collision-detection.md) searches boxes with trees that halve the space.

## Further reading

- [cppreference, the map container](https://en.cppreference.com/w/cpp/container/map): the ordered map of C++, with its costs and its promise about references; intermediate.
- [Robert Nystrom, Game Programming Patterns, "Spatial Partition"](https://gameprogrammingpatterns.com/spatial-partition.html): grids, quadtrees and the cost of keeping them current in games; beginner.
- Robert Sedgewick and Kevin Wayne, "Algorithms", fourth edition: trees, heaps, graphs, union-find and sorting with proofs; intermediate.
