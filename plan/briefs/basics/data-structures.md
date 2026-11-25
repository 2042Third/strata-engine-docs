# Brief: `basics/data-structures`

| Field | Value |
| --- | --- |
| Title | Data structures I: arrays, lists, hash maps and their cost |
| Kind | P |
| Size | L |
| Tracks | B, E |
| Needs | `basics/programming-3`, `basics/numbers` |
| From | new; arrays, linked lists, stacks, queues and ring buffers, hash maps and their cost (big-O, with the logarithms of `basics/numbers`); binary search, swap-remove and free lists, prefix sums; arrays of structs against structs of arrays; the engine's cases: sparse sets (scene-ecs concept 4; code 4, 5, 13) and hash buckets, job queues; trees, heaps, graphs and sorting are `basics/trees-graphs`' |
| Unit | `plan/allocation/basics-a.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `basics/data-structures` — Data structures I: arrays, lists, hash maps and their cost

**Covers.** Every structure is drawn first, then written in a few lines of C++ with arrays, structs and loops, and its
cost counted. The cost of operations: counting steps, big-O (O(1), O(log n) with the logarithms of `basics/numbers`,
O(n), O(n log n), O(n²)), constant time, and why a cost on paper meets the cache of `basics/computer`. Arrays: side by
side in memory, an index in constant time, inserting in the middle in O(n), a dynamic array that grows by doubling,
arrays and their cost as the base of everything after. Binary search on a sorted array. Removing from an array by
swapping with the last element; free lists of slots, and indices that stay valid with a version that catches a stale
one. Linked lists, single and double, with pointers or with indices, and lists kept inside the items themselves (as
Strata's hierarchy keeps its links in a component, `world/scene-graph`); their cost against arrays. Stacks (last in,
first out; the word's second meaning beside the stack of memory). Queues (first in, first out), double-ended queues,
and ring buffers of fixed size that overwrite the oldest entry (the log's buffer and the profiler's frames). Hash maps
and hash sets: a hash function turns a key into a number (stable hashes are `basics/data-formats`'), buckets,
collisions, the load factor and growing; a cache as a hash map from a key to a result already computed; hash maps and
what they cost. Prefix sums and arrays of indices that point into one shared array. Arrays of structs against structs
of arrays, with the cache. Sparse sets: a packed array and an array of positions, adding, removing by a swap and
finding in constant time, walking the packed data; the sparse set and its cost (Strata's storage is `world/ecs`'). The
Test out box asks for the cost of an operation in big-O, the array left after a swap-remove, and the bucket a key lands
in. The Practice draws, writes and costs small cases of these structures and ends with the optional item on the
reader's Coin Run: keep the collected coins' names in a `std::vector` and in a hash set, remove with a swap, and count
the steps of each.

**Leaves out.**

- Trees, heaps, graphs and sorting → `basics/trees-graphs`
- The standard library's containers and algorithms as C++ → `basics/cpp-generic`
- Strata's sparse sets and entity storage → `world/ecs`
- Strata's hierarchy as linked lists and its lookup index → `world/scene-graph`
- Job queues → `core/jobs`
- Least recently used eviction → `assets/residency`
- Stable hashes, checksums and cryptographic hashes → `basics/data-formats`

**Fit.** `fits`: about 5,250 words against L (5,000). Eleven structures and ideas, each drawn, written in a few lines
of C++ and costed from zero (about 4,150), and the primer's fixed parts with the Test out box, the Practice and the
Coin Run item (about 1,100); hash maps and sparse sets take the most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:101` | concept | home | The cost of operations: counting steps, big-O, constant time. General knowledge. |
| `new:102` | concept | home | Arrays and dynamic arrays: an index in constant time, inserting in O(n), growth by doubling. General knowledge. |
| `new:103` | concept | home | Binary search and what it costs. General knowledge. |
| `new:104` | concept | home | Removing by a swap with the last element; free lists of slots; indices with a version. General knowledge. |
| `new:105` | concept | home | Linked lists with pointers or indices, and lists kept inside the items; their cost. General knowledge. |
| `new:106` | concept | home | Stacks, the data structure: last in, first out. General knowledge. |
| `new:107` | concept | home | Queues, double-ended queues and ring buffers of fixed size. General knowledge. |
| `new:108` | concept | home | Hash functions, hash maps and hash sets: buckets, collisions, load factor, growth; a cache as a hash map. General knowledge. |
| `new:109` | concept | home | Prefix sums and arrays of indices into one shared array. General knowledge. |
| `new:110` | concept | home | Arrays of structs against structs of arrays, with the cache. General knowledge. |
| `new:111` | concept | home | Sparse sets: packed array, positions, add, swap-remove and find in constant time. General knowledge. |
| `new:118` | hands-on | home | Optional practice on Coin Run: the collected coins in a vector and in a hash set, a swap-remove, the steps counted. General knowledge. |
| `foundation:614` | term | home | Ring buffer, in general; Strata's `LogBuffer` and the profiler's frames are its examples |
| `render-scene:571` | term | home | Structure of arrays, against an array of structs |
| `scene-ecs:284` | concept | use | Sparse sets as the storage `world/ecs` teaches, named as the reason for the structure |
| `scene-ecs:376` | code | use | `SceneHierarchy.h`, the links kept in a component, named as the example of a list inside its items |
| `scene-ecs:385` | code | use | The scene's lookup index, hash buckets with a swap-remove, named as an example |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Arrays, `std::vector`, loops, functions and structs | `basics/programming-2` | must |
| Pointers at the use level, and template arguments | `basics/programming-3` | must |
| Logarithms in base 2 | `basics/numbers` | must |
| Caches, and why the order of data in memory matters | `basics/computer` | must |

**Starting state.** The end state of `make/project-coin-run`, downloaded on track E, from which the optional Coin Run
item of the Practice starts.

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `algorithm` | algorithm | - |
| `array-of-structs` | array of structs | AoS |
| `big-o-notation` | big-O notation | - |
| `binary-search` | binary search | - |
| `constant-time` | constant time | - |
| `data-structure` | data structure | - |
| `hash` | hash | hash value |
| `hash-function` | hash function | - |
| `hash-map` | hash map | hash table |
| `linked-list` | linked list | - |
| `node` | node | - |
| `queue` | queue | FIFO |
| `ring-buffer` | Ring buffer | - |
| `sparse-set` | sparse set | - |
| `struct-of-arrays` | struct of arrays | SoA |
| `structure-of-arrays` | Structure of arrays | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-basics-a-21 | should | shape | `basics/computer`, `basics/tools`, `basics/git`, `basics/data-structures`, `basics/trees-graphs`, `basics/bytes`, `basics/data-formats` | A primer has a "Common mistakes" section: each mistake, its symptom and its fix. These seven pages list none: no Covers, row or Fit line of theirs names a mistake, while the other eleven pages of the unit do. | Each page's Covers names three or four mistakes with their symptoms (about 250 words a page). For example: tools, a path with a space not quoted, a program run from the wrong folder, Ctrl+C taken for copy; git, a commit without `git add`, conflict markers left in a file, build output committed (the editor's `.gitignore` keeps `.strata/` out); data-structures, an index kept across a swap-remove, a hash map's order relied on; trees-graphs, a recursive walk of a deep tree that overflows the stack, a graph walk without a visited set; bytes, a length read from a file and used unbounded, UTF-8 cut by bytes; data-formats, a float written with too few digits, `std::hash` stored in a file, a trailing comma in JSON; computer, memory taken for storage, more cores taken for a faster single task. | `style.md:476`; `allocation/basics-a.md:5-46`, `:82-120`, `:459-485`, `:607-639`, `:677-701`, `:1088-1114`, `:1152-1186`; `Strata/src/Strata/Project/Project.cpp:198-199` |
