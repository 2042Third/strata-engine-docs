# Brief: `basics/trees-graphs`

| Field | Value |
| --- | --- |
| Title | Data structures II: trees, heaps, graphs and sorting |
| Kind | P |
| Size | M |
| Tracks | B, E |
| Needs | `basics/data-structures` |
| From | new by split of `basics/data-structures`, which could not hold both lessons at a primer's size; trees and ordered maps whose nodes stay put, depth-first and breadth-first walks, binary heaps as priority queues, spatial trees as halving the space to search, graphs (directed graphs, dependency graphs, walks, cycles; their topological sort is `core/engine-modules`', foundation concept 10), union-find, sorting and radix sort; the engine's cases: dependency graphs, spatial trees, reference graphs, queues of loading work by priority |
| Unit | `plan/allocation/basics-a.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `basics/trees-graphs` — Data structures II: trees, heaps, graphs and sorting

**Covers.** The page goes on from `basics/data-structures` the same way: every structure is drawn first, then written
in a few lines of C++ with arrays, structs and loops, and its cost counted. Trees: root, parent and children; binary
search trees and ordered maps that keep their keys in order, whose nodes do not move, so references to them stay
valid; trees, their costs and big-O; depth-first walks with a stack and breadth-first walks with a queue. Binary heaps
as priority queues (a queue of loading work by priority, the open set of A*). Spatial trees (bounding volume
hierarchies, quadtrees and octrees) as the idea of halving the space to search. Graphs: nodes and edges, directed
graphs, dependency graphs, walking a graph breadth-first and depth-first, cycles; the topological order is named, and
Kahn's algorithm is `core/engine-modules`'. Union-find (disjoint sets) in one worked example. Sorting: what O(n log n)
means, stable sorts, and radix sort by the bytes of a key in O(n). The Test out box asks for the orders in which a
depth-first and a breadth-first walk visit a small tree, the item a heap gives out next, and whether a small graph has
a cycle. The Practice draws, writes and costs small cases of these structures and ends with the optional item on the
reader's Coin Run: walk the level's hierarchy from its roots, depth-first and breadth-first, and log each entity's name
with its depth.

**Leaves out.**

- `std::map`, `std::set` and `std::sort` as C++ → `basics/cpp-generic`
- Topological sort (Kahn) → `core/engine-modules`
- Reference graphs and closures of assets → `assets/references`
- Bounding volume trees in physics → `physics/collision-detection`
- A* and other searches for game AI → `appendix/game-ai`

**Fit.** `fits`: about 3,800 words against M (3,000). Seven ideas, each drawn, written in a few lines of C++ and costed
from zero (about 2,700), and the primer's fixed parts with the Test out box, the Practice and the Coin Run item (about
1,100); trees with their walks, graphs and sorting take the most, and the page stands about 200 words under M's top.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:112` | concept | home | Trees, binary search trees and ordered maps whose nodes stay put; depth-first and breadth-first walks. General knowledge. |
| `new:113` | concept | home | Binary heaps as priority queues. General knowledge. |
| `new:114` | concept | home | Spatial trees as halving the space to search. General knowledge. |
| `new:115` | concept | home | Graphs, directed and dependency graphs, walks, cycles, a topological order named. General knowledge. |
| `new:116` | concept | home | Union-find (disjoint sets). General knowledge. |
| `new:117` | concept | home | Sorting: O(n log n), stable sorts, radix sort by bytes in O(n). General knowledge. |
| `new:207` | hands-on | home | Optional practice on Coin Run: the level's hierarchy walked from `Scene::GetRootEntities` through `Entity::GetChildren`, depth-first with a stack and breadth-first with a queue (both kept in a `std::vector`), each name logged with its depth, the `Walls` parent among them. Evidence: `StrataScriptCore/Include/StrataScript/Scene.h:134`, `StrataScriptCore/Include/StrataScript/Entity.h:53-56` |
| `foundation:332` | concept | use | The radix sort of the utilities, taught here as a sort (the item's home is `basics/data-formats`) |
| `foundation:256` | concept | link | Topological sorting and Kahn's algorithm, linked to `core/engine-modules` |
| `assets:297` | concept | link | Priority queues of loading work, linked to `assets/loading` |
| `assets:318` | concept | link | Dependency graphs of assets, linked to `assets/references` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Arrays, stacks, queues, hash maps, and the cost of an operation in big-O | `basics/data-structures` | must |
| Loops, functions, structs and `std::vector` | `basics/programming-2` | must |
| Pointers at the use level | `basics/programming-3` | must |
| Logarithms in base 2; bytes, shifts and masks, for radix sort | `basics/numbers` | must |
| Parents and children in the Hierarchy, as Coin Run's `Walls` holds the walls | `make/scenes-entities` | helps |

**Starting state.** The end state of `make/project-coin-run`, downloaded on track E, from which the optional Coin Run
item of the Practice starts.

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `dependency-graph` | dependency graph | - |
| `directed-graph` | directed graph | - |
| `subtree` | subtree | subtrees |
| `tree` | tree | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-basics-a-21 | should | shape | `basics/computer`, `basics/tools`, `basics/git`, `basics/data-structures`, `basics/trees-graphs`, `basics/bytes`, `basics/data-formats` | A primer has a "Common mistakes" section: each mistake, its symptom and its fix. These seven pages list none: no Covers, row or Fit line of theirs names a mistake, while the other eleven pages of the unit do. | Each page's Covers names three or four mistakes with their symptoms (about 250 words a page). For example: tools, a path with a space not quoted, a program run from the wrong folder, Ctrl+C taken for copy; git, a commit without `git add`, conflict markers left in a file, build output committed (the editor's `.gitignore` keeps `.strata/` out); data-structures, an index kept across a swap-remove, a hash map's order relied on; trees-graphs, a recursive walk of a deep tree that overflows the stack, a graph walk without a visited set; bytes, a length read from a file and used unbounded, UTF-8 cut by bytes; data-formats, a float written with too few digits, `std::hash` stored in a file, a trailing comma in JSON; computer, memory taken for storage, more cores taken for a faster single task. | `style.md:476`; `allocation/basics-a.md:5-46`, `:82-120`, `:459-485`, `:607-639`, `:677-701`, `:1088-1114`, `:1152-1186`; `Strata/src/Strata/Project/Project.cpp:198-199` |
