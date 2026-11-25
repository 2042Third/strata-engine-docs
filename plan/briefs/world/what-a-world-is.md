# Brief: `world/what-a-world-is`

| Field | Value |
| --- | --- |
| Title | What a game world is made of |
| Kind | C |
| Size | M |
| Tracks | E |
| Needs | `basics/computer`, `basics/cpp-classes`, `basics/data-structures`, `core/frame-loop` |
| From | scene-ecs; object models compared (inheritance, components, ECS) |
| Unit | `plan/allocation/world.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `world/what-a-world-is` — What a game world is made of

**Covers.** The page starts from what the reader saw in `start/first-game`: the Hierarchy panel lists the things of a
scene and the Inspector shows the parts of one of them (the opening picture). The problem: a game world is many things
(a player, a crate, a light, a camera) that the engine must store, find, update, draw, save and load, every frame. The
naive answer is a class for each kind of thing with a virtual `Update`; the page shows where it breaks (deep
hierarchies, a base class that grows to hold everything, behaviour that cuts across classes, objects scattered in
memory). Then the idea in one diagram: an entity is only an identity, components are plain data attached to it (one of
each type at most), and systems hold the behaviour and run over every entity that has the components they need. The
approaches follow, each introduced by the flaw of the one before: object hierarchies (Unreal's `AActor`), objects that
own components (Unity's GameObject), and the data-oriented ECS in its two storage forms, sparse sets (EnTT) and
archetypes (flecs, Unity DOTS, Bevy), ending in a table of their cost, cache use, flexibility and users. Strata's choice
and its reason: one EnTT registry whose components are plain data, behaviour in scene systems, and a `Scene` class that
wraps the registry with persistent identity, a hierarchy and caches; loops over one component type are cache-friendly,
a scene can hold a million entities, and one description of the data drives files and the editor. What the choice
cannot do: an entity has no methods and no type of its own. The common mistake: thinking an entity "is" an object with
methods. The exercise designs a door that opens when the player comes near in each object model, as short sketches
that the reader runs. At the end the reader can say what an entity, a component, a system and a scene are, and why
Strata stores them as it does.

**Leaves out.**

- How EnTT stores components, handles against UUIDs, the `Entity` class → `world/ecs`
- Parents, children and world transforms → `world/scene-graph`
- Systems, their order and the fixed step in code → `world/systems`
- Making entities in the editor, for game makers → `make/scenes-entities`
- The sparse set as a data structure → `basics/data-structures`

**Fit.** `fits`: about 3,800 words against M (3,000). The naive answer, the idea and the three approaches with their
table take most of it, beside one screenshot, two diagrams and the exercise; the page is 200 words below M's top.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `scene-ecs:271` | concept | home | What a scene is: the problem, object hierarchies, components on objects and the ECS, Strata's choice (EnTT, plain-data components, scene systems, `Scene` wrapping the registry) and the newcomer's error |
| `scene-ecs:472` | figure | home | The Hierarchy panel with a nested tree (a sample's start scene, such as `Samples/ThirdPerson`) and the Inspector of one entity: the opening picture |
| `scene-ecs:611`, `scene-ecs:613`, `scene-ecs:615`, `scene-ecs:624` | term | home | Entity, component, ECS and scene, defined where the idea is first drawn |
| `scene-ecs:281` | concept | link | Components as plain data and tag components, named here and taught in `world/ecs` |
| `scene-ecs:284` | concept | link | Sparse sets against archetypes, named in the table; Strata's storage is `world/ecs`' |
| `new:13` | hands-on | home | The page's exercise (D27), a design exercise done as sketches: a door that opens when the player comes near, written three ways as short C++ sketches run for a few frames (a class hierarchy with a virtual `Update`; a game object that owns components; entities with a door component and a system that runs over them), each with its output; the answer weighs the three and names Strata's form, a plain-data component and a scene system (about 250 words). Evidence: `Strata/src/Strata/Scene/SceneSystem.h:26-30` (a scene system is the runtime part attached to a scene while it plays) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Classes, inheritance and virtual calls | `basics/cpp-classes` | must |
| Caches, and why the order of data in memory matters | `basics/computer` | must |
| Arrays, hash maps and what operations cost | `basics/data-structures` | helps |
| One frame of an engine: input, update, draw | `core/frame-loop` | helps |
| The Hierarchy and Inspector panels, as the first game used them | `start/first-game` | helps |
| What a game engine is, and a survey of engines | `start/what-an-engine-is` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `ecs-entity-component-system` | ECS (entity-component-system) | - |
