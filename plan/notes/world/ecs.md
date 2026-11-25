# Notes: `world/ecs`

## New terms

- **registry**: EnTT's container of entity numbers and component storages (`entt::registry`). Home: `world/ecs`.
  Aliases: registries. (Defined in bold under "A map of the code"; the brief's table does not list it, the inventory
  does: `scene-ecs:614`.)
- **context**: a place inside a registry that keeps one object per type for the whole registry; a module keeps its
  per-scene state there (`RenderSceneContext`, `GameUISceneContext`). Home: `world/ecs`.

The page also defines the glossary's own entries homed here: entity, component, handle (EnTT), tag component, view.
"Sparse set" is used as homed in `basics/data-structures` (markterms marks it); the page defines no storage term.

## Requests

- Hosts for Further reading, both cited without a link: `gameprogrammingpatterns.com` (Robert Nystrom, "Game
  Programming Patterns", chapter "Component") and `skypjack.github.io` (Michele Caini's blog series about the design
  of EnTT). `github.com` is already allowed and carries the one link.
- `tools/data/names.txt`: nothing; the names in Further reading are not read.
- The page uses no word beyond the lists; every word-list finding of the first rounds was reworded.

## Since

`since: 0.3.0`: the scene, its registry, `Entity`, `IDComponent` and the entity limit came with wave 1's `scene-core`
work in the first release (`plan/inventory/scene-ecs.md`, rows 25-31 give 0.3.0).

## Not verified

- The EnTT wiki address in Further reading (`github.com/skypjack/entt/wiki/Crash-Course:-entity-component-system`) was
  not fetched.
- The alternatives table: the Unity Entities package keeping one table per set of components, EnTT groups, and
  inheritance-based engines come from the projects' public documentation as I know it, not checked in this session.
- "EnTT does not promise that addresses stay put when components are added": the code shows pages of 1,024 elements
  (`ENTT_PACKED_PAGE`), so growth does not move elements in this version; the page states the cautious form (the
  promise is EnTT's documentation's, not read here).
- That the context's objects are destroyed with the scene: followed from `Scope` in the context structs, not from
  EnTT's destructor code.
- The collision chance near one in 1.8 x 10^19 per pair is 1 / 2^64 computed by hand.
- That a handle's version wraps after 4,095 uses of one slot was read from `entity_traits::next`
  (`entity.hpp`) and reproduced in the sketch of exercise 3, a program that does not use EnTT; nothing ran EnTT itself.
- That `Scene::Copy` keeps the source's EnTT handles is the comment of `Scene.h` (`Scene::Copy`), not a test.
- The Hierarchy node as the reason for the creation order: the comment says the signals rely on it, and
  `MarkTransformDirty` returns when the node is missing (`Scene.cpp` 1482-1489); no test removes the node.
- Exercise 2's chain (`Scene::GetAllEntitiesWith`, `view_iterator`, `seek_next`, `valid`, `unchecked_refresh`) was
  read in the code, not stepped through in a debugger. The doctest filters in "How it is tested" were not run.
- The names of the tests in "How it is tested" were read in `SceneTests.cpp` and `HierarchyTests.cpp`; they were not run.

## Findings not applied

- The brief names no open findings.
- The toy (`sketches/world-ecs-toy.cpp`) has 91 lines, above kind I's 30 to 80 and the brief's about 60: the three
  arrays, the removal, the view, a print helper and the printed steps did not fit in 80 lines of Hazel style.
- No figure manifest: the scene's anatomy and the swap-removal are Mermaid diagrams on the page; the handle's index and
  version against the UUID is the example and a table ("what survives what") instead of a picture.
- `scene-ecs:284` (`EntityPrototype` keeps values in its own per-type arrays because EnTT's pages of 1,024 waste
  memory for small prefabs) is not on the page: the pin's `EntityPrototype.h` has no comment saying so.
- No "What went wrong before" section: the history has no bug of this subject with a regression test.
- No `tutorials/world/ecs/exercise-<n>.patch`: the card asks for one only after `core/first-change` and the hard
  exercise is a standalone sketch.
- The title is the brief's ("Entities and components, with EnTT inside"), not the task text's "Entities, components and
  systems", because the card ties `title` to the brief's row.

## Clerk

- Admitted: "Registry (world)" and "Context (world)", homed here; the glossary's "Registry" (`core/layers-registries`)
  and "Context" (`scripting/abi-sdk`) are other meanings.
- `tools/external-hosts.txt`: `gameprogrammingpatterns.com` and `skypjack.github.io` added (front pages fetched: the
  book's site and Michele Caini's blog about EnTT).
