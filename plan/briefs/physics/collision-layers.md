# Brief: `physics/collision-layers`

| Field | Value |
| --- | --- |
| Title | Collision layers |
| Kind | I |
| Size | M |
| Tracks | E |
| Needs | `physics/building-bodies`, `world/projects-settings` |
| From | physics ch. 8; 1.8 (the project's table, the matrix, filter bits, runtime changes through the scene's working copy, the Ghost layer) |
| Unit | `plan/allocation/physics.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `physics/collision-layers` — Collision layers

**Covers.** The job: decide which bodies may collide, and which bodies a query sees. The problem and how engines solve
it, taught here in full because no concept page holds it: groups of objects that must not collide (the Playground's
ghost boxes sink through the balls but land on the floor), and the approaches engines use (per-pair ignore lists,
groups, category and mask bits, named layers with a matrix), with their costs. The map: the project's section
`Scene.CollisionLayers`, the scene's working copy, the world's masks and each shape's filter. The contract: layers are
the project's, so a layer's name means the same in every scene and prefab, and a script changes only the running copy;
settings reach the world on the main thread, when a scene is handed over or a setting changes. A toy version: 32-bit
masks with a set and a test. The real code: `PhysicsLayerSettings` (32 names and 32 masks of 32 bits, every pair
colliding by default, a symmetric matrix, and the rule that both masks must allow a pair; its stored form, the named
layers by index and the `NoCollisions` pairs, which is the value of a complex section); the project section and
`Scene::ApplyProjectLayers`; `PhysicsFilters.h`, which maps
a layer to box3d's category bit and its matrix row to the mask, reserves bit 63 as the query category so that queries
see every layer, and gives parked bodies an empty filter; changes while the game runs (`SetLayerCollisionMasks`, the
SDK's `Physics::SetLayersCollide`), which refilter shapes and wake bodies. The editor's side: the Collision Layers page
of Project Settings, `project.setCollisionLayers` and the migration of 0.5.0 scenes. The figure of the filter bits and
the 32 × 32 matrix, and the picture of the page with the Playground's Ball and Ghost pair kept apart. Then the
alternatives, how it is tested and changing it safely. At the end the reader can set up a Ghost layer and predict, for
any pair of layers, whether they collide and whether a query sees them.

**Leaves out.**

- How a settings section is registered, versioned and handed over → `world/projects-settings`
- The Collision Layers page's drawing → `editor-ui/settings-windows`
- Layer masks in raycasts and overlaps → `physics/queries`
- Using layers in a game → `make/physics`

**Fit.** `over`: about 4,500 words against M (3,000). The full problem section, three excerpts from the table's data to
the shapes' filters, the editor's side and two figures pass M's top; L (5,000) by S2.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `physics:122-126` | feature | home | 32 named layers and the symmetric matrix; the project section and the scene's working copy; the box3d filter mapping; changes at run time; the editor's page, the command and the migration from 0.5.0 |
| `physics:259` | concept | home | Collision filtering: layers and masks, category and mask bits, groups, filtering queries; Strata's "both must agree" rule and its reserved query bit |
| `physics:308` | code | home | `Strata/src/Strata/Physics/PhysicsFilters.h:1-60`: category and mask filtering, the reserved query bit, the parked filter |
| `physics:309` | code | home | `Strata/src/Strata/Scene/PhysicsLayerSettings.h:43-67`: `SetCollide` and `DoCollide`, a symmetric matrix and the "both agree" rule |
| `scene-ecs:406` | code | home | `Strata/src/Strata/Scene/PhysicsLayerSettings.h:24-40`: the table's data, 32 names and 32 masks of 32 bits, every pair colliding by default; with the stored form at `PhysicsLayerSettings.h:102-111`, a complex section's value (named layers by index, the `NoCollisions` pairs). Shown with `physics:309` as one walk |
| `scene-ecs:221` | feature | home | The section `Scene.CollisionLayers`: a complex section whose value is the table, and the scene's working copy made by `Scene::ApplyProjectLayers` |
| `scene-ecs:691` | term | home | Terms: collision layer and matrix, as the scene inventory defines them (the same entry as `physics:517`) |
| `physics:347` | figure | home | Layer filtering bits: a shape's 64-bit category and mask, the query's filter, the symmetric 32 × 32 matrix |
| `physics:372` | figure | home | Project Settings, the Collision Layers page, with the Playground's Ghost and Ball pair kept apart |
| `physics:419` | rule | home | Collision layers are the project's, not the scene's; scripts change only the running copy |
| `physics:421` | rule | home | Physics settings are applied on the main thread (the hand-over of `IProjectSettings`); `physics/tuning` applies the same rule to `Physics.Simulation` |
| `physics:517-519` | term | home | Terms: collision layer, layer matrix, category bits, mask bits, query category |
| `new:15` | hands-on | home | Exercises (D27): from a RigidBody's `Layer` to box3d's filter, followed with a search: `MakeBodySetup` passes the layer to `PhysicsFilters::MakeShapeFilter`, which sets the category bit and a mask that holds bit 63, and `MakeQueryFilter` asks for that bit (trace). A doctest: a ball on layer 1 dropped on a box with a Static RigidBody on layer 2, after `PhysicsSystem::SetLayersCollide(1, 2, false)`: the ball falls through, a raycast down still hits the box, and one with the mask `~ST_BIT(2)` does not (done). Evidence: `Strata/src/Strata/Physics/PhysicsWorld.cpp:1997-2008`; `Strata/src/Strata/Physics/PhysicsFilters.h:18-60`; `StrataTests/src/Physics/PhysicsBox3DBehaviorTests.cpp:201-218`; `StrataTests/src/Physics/PhysicsLayerTests.cpp:202` |
| `new:7` | erratum | home | `Samples/PhysicsPlayground/README.md:16` calls the Ghost and Ball rule "the scene's layer matrix" in "Scene settings", and `:52` says the layers were set with `scene.setSettings`. At the pin the layers are the project's: `Samples/PhysicsPlayground/PhysicsPlayground.stproj:25-39` holds `Scene.CollisionLayers` (Ball 1, Ghost 2, the pair in `NoCollisions`), and `scene.setSettings` refuses collision layers since 0.6.0. Evidence: `StrataEditor/src/Editor/EditorSceneCommands.cpp:568`, `:599-600` (read again at the pin, as process.md's table of errata cites them) |
| `physics:377` | figure | use | The frames of the ghosts sinking through the balls |
| `physics:76` | feature | link | The parked filter, linked to `physics/scale-streaming` |
| `scene-ecs:224` | feature | use | The hand-over pattern: scenes built on workers never read the service |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Bits, bit masks and bitwise operators | `basics/numbers` | must |
| Settings sections, `IProjectSettings` and the hand-over to scenes | `world/projects-settings` | must |
| Records and shapes of a body | `physics/building-bodies` | must |
| The pairs the broad phase finds | `physics/collision-detection` | helps |
| Settings windows built from schemas | `editor-ui/settings-windows` | helps |
| Running an editor command | `editor/commands` | helps |
| Writing and running one doctest case | `core/first-change` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `category-bits` | Category bits | mask bits |
| `collision-layer` | Collision layer | - |
| `query-category` | Query category | - |
