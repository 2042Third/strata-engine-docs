# Notes: `basics/data-structures`

## New terms

The page bolds the 16 terms the brief lists (data structure, algorithm, big-O notation, constant time, binary search,
linked list, node, queue, ring buffer, hash function, hash, hash map, sparse set, array of structs, struct of arrays,
structure of arrays) and four more whose home is this page. Proposed, for the glossary:

- **swap-remove**: removes an array item in constant time by copying the last item into its place and shrinking the array
  by one. Home: this page. Aliases: swap and pop.
- **free list**: a list of the unused slot indices of an array, from which the next new item takes its slot. Home: this
  page.
- **prefix sum**: a running total of a list of counts, giving the place where each group starts in one shared array. Home:
  this page.
- **load factor**: the number of items of a hash map divided by its number of buckets. Home: this page.

Not bolded, explained in the text: slot, handle, bucket, collision, chaining, capacity, probe, stack (the data structure),
double-ended queue.

## Requests

- Figures: none requested. The page has three Mermaid diagrams (doubly linked list, hash buckets, sparse set) and no
  figure manifest.
- Sketches: twelve files `sketches/basics-data-structures-*.cpp` (steps, growth, bsearch, slots, links, ring, hashmap,
  prefix, layouts, sparse; soa-remove and coinrun for the Practice). All compile with the sketch check; outputs are filled.
- Words: none beyond the lists; "Mia" is written as code.
- Further reading cites cppreference, "Game Programming Patterns" and "Introduction to Algorithms" without links.

## Not verified

- That `std::vector` libraries other than the one that compiled the sketches grow by 1.5 (the text says "some standard
  libraries"); general knowledge, not checked at the pin.
- That `std::hash` is not promised to give the same number across libraries or versions: standard-library behavior, not
  checked at the pin.
- That `std::deque` adds and removes at both ends in constant time: standard-library behavior.
- That Strata's job queue is first in, first out: `JobSystem.h` names a queue of waiting jobs and priorities; the page says
  only "a queue of jobs waiting for a worker thread" and links `core/jobs`.
- "About a billion simple steps per second": a rough figure for a processor, not measured on the reference machine.
- Links to pages that may not exist yet at the time of writing: `basics/trees-graphs`, `basics/cpp-generic`,
  `basics/cpp-memory`, `basics/data-formats`, `basics/computer`, `basics/numbers`, `core/jobs`, `make/project-coin-run`.
- The Practice item 6 is a standalone sketch with standard containers; how the reader's Coin Run script would hold the
  names is not stated.

## Findings not applied

- critic-basics-a-21: applied. The page has a "Common mistakes" section with an index kept across a swap-remove, a hash
  map's order relied on, a reference kept across growth, and a standard hash stored in a file.
- From the brief's Covers: job queues are only named, with a link to `core/jobs` (the brief's "Leaves out"); least recently
  used eviction, stable hashes and Strata's own sparse sets are left to their homes.
- `scene-ecs:284` is used as the reason for the sparse set (EnTT's `basic_sparse_set` at the pin); `scene-ecs:376` and
  `:385` appear as the hierarchy quote (`SceneHierarchy.h`) and the lookup index (`Scene.h`, `Scene.cpp`).
- The brief's size note said about 5,250 words; the page has about 6,380, inside L (4,001 to 6,500).

## Clerk

- Admitted: swap-remove (alias swap and pop), free list, prefix sum, load factor.
