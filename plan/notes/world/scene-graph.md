# Notes: `world/scene-graph`

## New terms

None beyond the brief's homed terms (root entity, dirty flag, transform contract, frontier, sibling index, hierarchy
version, signal, patch, active in hierarchy), each defined in bold at its first use.

## Requests

- `subtree` (19 uses): a term for `basics/trees-graphs` (an entity, or node, with everything below it), or a line of
  `tools/data/extra-words.txt`. The page's last lint failure is this word (`word-list`).

## Since

`since: 0.3.0`: the scene graph (cached hierarchy, incremental world transforms, indexes) came with wave 1's
`scene-core` work (`Docs/Roadmap.md`, Status, `scene-core` bullet), which shipped in the first release, 0.3.0
(`Docs/Releases/0.3.0.md`; the inventory `plan/inventory/scene-ecs.md` rows 71-93 give 0.3.0).

## Not verified

- That the **Hierarchy** panel shows entities in the order of `GetEntitiesInHierarchyOrder` (the editor's panel code
  was not read).
- That the game interface keeps "ordered lists" and "rectangles placed in the world" (only that `GameUIScene.cpp` calls
  `GetHierarchyMoves` and `GetWorldTransformChanges` was checked).
- "Physics compares thousands of bodies": that it calls `FindCurrentWorldTransform` from workers was checked
  (`PhysicsWorld.cpp` 3428-3469), not how many.
- The cost of the `Debug` check (0.01 ms per entity, 100 ms a frame for 11,000 entities, about 5 ms an update when
  paced) is the comment in `Scene.h` 389-399, not a measurement of mine.
- 54.6 s and 45 ms are `Docs/Roadmap.md`'s numbers; that the old cost came from one-at-a-time renumbering is the
  page's reading of the present code (`GetSiblingIndex`'s comment), not of the old code.
- The sheared child's numbers (columns, lengths 1.581) were computed by hand, not by running `DecomposeTransform`.
- Exercise 1's chain of calls was read in the code (`EntityCommands.cpp` 721 and 749, `CommandUtils.cpp` 510 and 596,
  `ComponentRegistry.h` 418-422, `Scene.cpp` 197, 2039-2042, 1482-1489), not stepped through in a debugger.
- The doctest filter `--test-suite=Scene.Hierarchy,Scene.Transforms*` was not run.
- Claims about Unreal Engine, Godot and Unity in the alternatives table come from their public documentation as I know
  it, not checked against the linked pages in this session.

## Findings not applied

- The brief's only open finding (`new:14`, decomposition fails only for non-finite values, w near zero and a scale axis
  near zero, folds a mirror into X and drops shear silently) is applied in "From a matrix to local values"; nothing is
  left.
- The toy (`sketches/world-scene-graph-toy.cpp`) is 92 lines, above kind I's 30 to 80: the tree, the dirty list, the
  frontier, the level walk, a silent write and the printed results did not fit in 80 lines of Hazel style.
- No `tutorials/world/scene-graph/exercise-<n>.patch`: exercises 1, 2 and 4 add doctest cases to the engine; their
  answers describe the solution and name the engine's own test that does the same, but no patch was written or run.
- No figure manifest: the brief's four figures (dual hierarchy, composition and its inverse, dirty propagation, signal
  flow with the caught silent write) are Mermaid diagrams on the page, as is the map.
- `names`: the budget metrics are named as "the metric `MoveRoot100k`" of the `Perf.Scene` suite, because the names
  check knows suites and CTest names, not the keys of `StrataTests/Perf/Budgets.json`.

## Clerk

- Admitted: "subtree" (alias subtrees), homed on `basics/trees-graphs` as asked, with this page's wording.

## Track walk E-final-8

WK4: the Basic exercise names the build it needs, the source build of `core/first-change` (the package holds no
source and no debug information), and how to start the editor under the debugger: `StrataEditor` with `--project` and a
copy of a sample, as `core/debugging` "The engine under a debugger" starts `StrataTests` (`--project` is in
`StrataEditor/src/EditorApplication.cpp:70`). The breakpoint is set once the project is open, because loading a scene
calls `Scene::MarkTransformDirty` for each new root (`Scene::FinishLinking`,
`Strata/src/Strata/Scene/Scene.cpp:1243-1251`). The doctest case goes into `StrataTests/src/Scene/SceneTransformTests.cpp`. The chain of
the answer was checked by the walker at the pin. Words were cut in the introduction, in "Changing it safely" (the
`DestroyEntities` clause that "What went wrong before" repeats) and in the exercise to stay within size XL (10,000).
