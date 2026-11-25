# Brief: `world/ecs`

| Field | Value |
| --- | --- |
| Title | Entities and components, with EnTT inside |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `world/what-a-world-is`, `basics/cpp-generic`, `core/conventions` |
| From | scene-ecs; a toy sparse set first; home of handles instead of pointers and of UUIDs (`assets/handles-meta` covers asset handles only) |
| Unit | `plan/allocation/world.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `world/ecs` — Entities and components, with EnTT inside

**Covers.** The job: `Scene` stores entities and their components in one EnTT registry (EnTT 3.16) and gives every
entity a persistent UUID; it is main-thread only. The hierarchy, systems and files are later pages'. The problem and the
approaches are one paragraph that links `world/what-a-world-is`. The map is the scene's anatomy: the registry with one
storage per component type, the UUID-to-entity map, the root list, the caches, the systems and services. The toy
version is a sparse set of about 60 lines (emplace, remove by swapping with the last element, contains, iterate) and a
view over two of them; then EnTT's own `swap_and_pop` shows why removing one component moves another, which is why a
`T&` or an `Entity` is never held across an add, a remove, a frame or a copy. Handles against UUIDs: the 32-bit EnTT
handle with a 20-bit index and a version, recycled after destruction, against the `IDComponent`'s UUID, which survives
saving, loading and copies (`GetEntityByUUID`); the `UUID` class quoted whole: a 64-bit random value that is never zero,
because zero is the null, written as 16 hexadecimal digits and hashed with `std::hash` to key the UUID map
(`Strata/src/Strata/Core/UUID.h:13-44`): Strata's choice of 64 bits, not the standard's 128-bit UUIDs, which
`basics/data-formats` teaches. The `Entity` class walked through: a
non-owning handle, its templated component functions, the `static_assert` that refuses `GetComponent` on a tag
component, `MarkModified` named with a link forward; then, after the rule "hold UUIDs, not `Entity`", the other class
named `Strata::Entity`: the script SDK's is a UUID value that scripts keep in fields, whose calls do nothing once the
entity is gone, which is why scripts may store it (`scripting/abi-sdk`; about 100 words). Creating an entity: what
every entity gets and why the hierarchy node comes first; duplicate UUIDs replaced with an error; the limit of
1,048,575 entities and its clean failure. Components as plain data, tag components (`InactiveComponent`) and views (`GetAllEntitiesWith`); the registry's
context, where a module keeps one object per scene (the render scene, the game UI's state). The Scene module's
own components in one table (each taught on its own page), the two types it declares for sibling layers
(`MeshRendererComponent`, `SkinComponent`), and the runtime-only components that are never registered. Then the
alternatives (archetypes, EnTT's groups, objects), the tests (the `Scene` suite), changing it safely, and a "trace it
yourself" exercise: follow one component's storage through a view in a debugger. At the end the reader can create,
find and remove components in engine code and say which identifier survives what.

**Leaves out.**

- Change signals and what `MarkModified` is for → `world/scene-graph`
- Parents, children and the two hierarchy components → `world/scene-graph`
- Copying a whole scene to play it → `world/systems`
- How components are described to files, the editor and commands → `world/reflection`
- Asset handles and `.meta` files → `assets/handles-meta`
- The camera component → `gpu/coordinates`
- Sparse sets as a data structure in general → `basics/data-structures`
- The script SDK's `Entity` and how scripts reach entities → `scripting/abi-sdk`

**Fit.** `fits`: about 4,850 words against L (5,000). The toy sparse set and four excerpts (the short `UUID` class
among them) take a third of the page, and the table of the Scene module's components stays a table.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `scene-ecs:25-27` | feature | home | `Scene` owns one registry, the UUID map, the roots and caches, main thread only; the `Entity` handle and its templated functions; tags cannot be fetched |
| `scene-ecs:29-31` | feature | home | `IDComponent` against the EnTT handle; what entity creation emplaces and in which order; the capacity limit and its error |
| `scene-ecs:51` | feature | home | `IDComponent`'s flags (Hidden, NotRemovable, NoSerialize) and why the serializer writes it as the entity's "ID" |
| `scene-ecs:59-60` | feature | home | `MeshRendererComponent` and `SkinComponent`: types declared in the Scene layer because sibling layers read them, registered by their modules |
| `scene-ecs:62` | feature | home | The runtime-only components (`HierarchyComponent`, `WorldTransformComponent`, `SubSceneComponent`, `UnknownComponentsComponent`): never registered, serialized or shown |
| `scene-ecs:94` | feature | home | `GetAllEntitiesWith` as a registry view |
| `new:12` | feature | home | The registry's context: one object per scene that a module keeps in the registry (`RenderSceneContext`, `GameUISceneContext`), which the context copiers of `world/systems` carry into copies. Evidence: `Strata/src/Strata/Renderer/RenderScene.cpp:100-102`; `Strata/src/Strata/GameUI/GameUIScene.cpp:61-63` |
| `scene-ecs:52-57` | feature | link | The other components of the Scene module, one row each in the table, each linking the page that teaches it |
| `scene-ecs:28` | feature | link | `MarkModified` seen in `Entity.h`; its meaning is `world/scene-graph`'s |
| `scene-ecs:277`, `scene-ecs:281`, `scene-ecs:284` | concept | home | Two kinds of ID; components as plain data and tags; storage as sparse sets and what Strata does with it (whole-storage copies, prototypes' own arrays) |
| `scene-ecs:374` | code | home | `Strata/src/Strata/Scene/Entity.h:12-114`: the handle class; templates, perfect forwarding, `decltype(auto)`, the tag `static_assert`, `MarkModified` |
| `scene-ecs:375` | code | home | `Strata/src/Strata/Scene/Scene.cpp:386-415`: `CreateEntityWithUUID`, what every entity gets and why the hierarchy node comes first |
| `new:1` | code | home | `Strata/vendor/entt/src/entt/entity/sparse_set.hpp:260-276`: EnTT's `swap_and_pop` (quoted as `vendor:entt/src/entt/entity/sparse_set.hpp`), after the toy: removal moves the last element into the hole |
| `assets:377` | code | home | `Strata/src/Strata/Core/UUID.h:13-44`: the `UUID` class whole: a 64-bit random id with zero reserved as the null, its text form, and the `std::hash` that keys the UUID map; `assets/handles-meta` quotes it for asset handles |
| `foundation:154` | feature | home | `UUID` as the foundation survey lists it (64-bit, random, never zero, 16 hexadecimal digits, `std::hash`): taught once with the handles against UUIDs |
| `scene-ecs:417`, `scene-ecs:419`, `scene-ecs:421` | figure | home | The scene's anatomy (the map); sparse-set storage with a swap-remove and a view of two storages; the handle's index and version against the UUID, and what survives saving and copies |
| `scene-ecs:516`, `scene-ecs:518`, `scene-ecs:519` | rule | home | Hold UUIDs, not `Entity` or `T&`, across frames and copies, with the paragraph after the rule: the script SDK's `Entity` wraps the UUID, so scripts may keep it (`StrataScriptCore/Include/StrataScript/Entity.h:26-37` against `Strata/src/Strata/Scene/Entity.h:12-21`); never `GetComponent` a tag; at most 1,048,575 entities |
| `new:29` | hands-on | home | The page's "trace it yourself" exercise (style.md §11; D27), which the Covers names and no inventory lists: a breakpoint in a loop over `GetAllEntitiesWith<TransformComponent, NameComponent>()` is followed into EnTT's view, which walks the dense array of one storage and skips each entity that the other storage lacks; the reader sees the entity's index in the sparse array and its place in the dense one, then removes a component and sees the last element move into the hole (about 250 words). Evidence: `Strata/src/Strata/Scene/Scene.h:679-683`; `Strata/vendor/entt/src/entt/entity/view.hpp:68-76`; `Strata/vendor/entt/src/entt/entity/sparse_set.hpp:260-276` |
| `scene-ecs:614`, `scene-ecs:617-621` | term | home | Tag component, registry (EnTT's meaning), component storage (the qualified entry: EnTT's per-type container, not the computer's storage) and sparse set, view, handle, UUID |
| `foundation:642`, `editor-core:686` | term | home | The foundation and editor surveys' entries for UUID: one glossary entry with `scene-ecs:621`; the editor's names asset handles too, which are UUIDs that name assets, and their own entry is `assets/handles-meta`' |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Object models compared; entity, component and system | `world/what-a-world-is` | must |
| Templates, `static_assert` and the standard containers | `basics/cpp-generic` | must |
| `constexpr`, `if constexpr` and perfect forwarding | `basics/cpp-modern` | helps |
| The sparse set and its cost as a data structure | `basics/data-structures` | must |
| Bits, masks and two numbers packed into one integer | `basics/numbers` | must |
| UUIDs as random identifiers, hexadecimal text | `basics/data-formats` | must |
| `Ref`, `Scope`, asserts and errors returned | `core/conventions` | must |
| The main thread owns the scene | `core/jobs` | helps |
| Caches and memory layout | `basics/computer` | helps |
| Running a debugger on a test | `core/debugging` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `component` | component | - |
| `context-world` | Context (world) | - |
| `entity` | entity | - |
| `handle-entt` | Handle (EnTT) | - |
| `registry-world` | Registry (world) | - |
| `tag-component` | Tag component | - |
| `view` | View | - |
