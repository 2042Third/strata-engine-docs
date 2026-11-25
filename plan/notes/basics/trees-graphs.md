# Notes: `basics/trees-graphs`

## New terms

- binary search tree: a tree in which each node has at most two children, the keys of its left subtree are smaller than its own and those of its right subtree larger; home `basics/trees-graphs`.
- ordered map: a map built on a balanced search tree that finds a key in O(log n), lists its keys in order and never moves its nodes; home `basics/trees-graphs`.
- priority queue: a queue that gives out the waiting item with the best priority, whatever its arrival time; home `basics/trees-graphs`.
- binary heap: a tree stored in an array in which every node is no larger than its children, so the smallest item sits at index 0; home `basics/trees-graphs`; aliases: heap.
- spatial tree: a tree that cuts space into parts so that a search skips every part that cannot hold the answer; home `basics/trees-graphs`; aliases: spatial trees.
- graph: a set of nodes joined by edges, with no rule about how many edges a node has; home `basics/trees-graphs`.
- cycle: a path of arrows in a directed graph that leads back to its start; home `basics/trees-graphs`; aliases: cycles.
- topological order: a list of the nodes of a dependency graph in which every node comes after the nodes it needs; home `basics/trees-graphs`, taught by `core/engine-modules`.
- union-find: an array in which each item holds the number of a parent, so that two items are in one group when their roots are equal; home `basics/trees-graphs`; aliases: disjoint sets.
- stable sort: a sort that keeps the order of items with equal keys; home `basics/trees-graphs`.
- radix sort: a sort by one digit or byte of the key at a time, lowest first, each pass stable; home `basics/trees-graphs`.

The glossary's own four terms (tree, subtree, directed graph, dependency graph) are defined in bold on the page.

## Requests

- Words for `tools/data/extra-words.txt`: octree (the three spatial trees named in the brief).
- Names for `tools/data/names.txt`: Kahn (Kahn's algorithm, named only to point to `core/engine-modules`).
- The sidebar lists of tracks B and E (`site.json`) do not hold `basics/trees-graphs` yet (`pages` O5, front matter `tracks: [B, E]` as the brief says); the planner adds it.
- Host for the last Further reading entry (Sedgewick and Wayne, "Algorithms"): cited without a link; algs4.cs.princeton.edu would carry it.

## Not verified

- Nothing about Strata on the page is unverified at the pin. The general statements (a self-balancing tree keeps a height within a small multiple of log n, `std::map` keeps references valid, path compression costs close to constant time) are general knowledge, not engine facts.
- No picture is drawn: the four figures are Mermaid diagrams, so there is no figures file.

## Findings not applied

- critic-basics-a-21 is applied (Common mistakes: a recursive walk of a deep tree, a graph walk without a visited list, a search tree that never balances), except that the depth at which a deep recursive walk overflows the stack is not given, because it depends on the platform and the frame size.
- A* is not taught, only named as a use of a heap: the brief leaves it to `appendix/game-ai`.
- The Coin Run item is the last Practice exercise (optional, pseudocode with the depth-first walk; the breadth-first change is described). It is not a tutorial, so no tutorial file exists.
- The brief's wording "reference graphs and closures of assets" and "bounding volume trees in physics" are only linked (`assets/references`, `physics/collision-detection`), as its Leaves out says.

## Clerk

- Admitted: binary search tree, ordered map, priority queue, binary heap (alias "heap" left out: the heap of `basics/computer` holds it), spatial tree, cycle, Topological order (basics) (the glossary's topological order is homed on `animation/skeletons`), union-find (alias disjoint sets), stable sort.
- Refused: radix sort: an alias of "Radix sort (LSD)" (`draw/batching`); the planner's.
- `extra-words.txt`: "octree" (the page uses it without a bold definition; a term would need one). `names.txt`: "Kahn".
- Left for the planner: `algs4.cs.princeton.edu` is admitted (front page fetched: Sedgewick and Wayne's Algorithms) though no link is written yet; the sidebar: see the clerk's report.
- Not admitted, because the page check would then fail and the page is the writer's: graph (its paragraph would define 2 terms with directed graph (term-paragraph)). The part's reviewer splits the paragraph or section or bolds the term; the next clerk admits it then.
