# Brief: `make/scenes-entities`

| Field | Value |
| --- | --- |
| Title | Scenes, entities and components |
| Kind | T |
| Size | M |
| Tracks | G, B |
| Needs | `make/editor-tour` |
| From | gamedev "Scenes, entities and components" (§1.4, concept 4); Coin Run's level: the ground, the walls, the ball and a first coin as entities |
| Unit | `plan/allocation/make-a.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `make/scenes-entities` — Scenes, entities and components

**Covers.** The page builds Coin Run's level and, while doing it, teaches what a scene, an entity and a component are
from the user's side. The idea first, in one paragraph and the figure "an entity is an ID and its components": a scene
is a document of entities; an entity is a thing with a name and an identity and nothing else; what it is and does
comes from the components on it (a Transform for where it is, a Mesh Renderer for what is drawn, a Box Collider for
what it bumps into), and behaviour comes from systems and scripts, not from a class of its own. The common mistake of
looking for an "enemy class" is named, and the inheritance tree is drawn beside the entity as the approach Strata does
not take. Then about ten steps. (1) Select the template's Ground and read its components in the Inspector: Name,
Transform, Mesh Renderer (its Mesh, its Material and Cast Shadows), Box Collider; each property's tooltip gives its unit
and its range, because one description
of every property drives the Inspector, the files, the commands and the scripts. (2) Add a wall with the Hierarchy's
**+ ▸ Cube** (a cube with a matching box collider), rename it with F2, and type its Position and Scale from the page
(the numbers are explained by `make/transforms-units`); drag it once with the Move gizmo (W) to see the numbers change.
(3) Duplicate it with Ctrl+D into four walls, edit their numbers, and drag them onto an empty entity **Walls** (**+ ▸
Empty**) to make them its children. (4) The ball: **+ ▸ Sphere**, named `Ball`. (5) The first coin: **+ ▸ Mesh only ▸
Cylinder** (no collider: the ball must pass through it), flattened and stood up, named `Coin`; a placeholder until
`make/assets` brings the coin's model. (6) **Add Component ▸ Tag** on the coin with the tag `Coin`, which scripts use
later; the component menu (Reset, Copy Values, Paste Values, Remove). (7) Edit several entities at once: select the four
walls and change their height together; mixed values show as "--"; then find them again with the Hierarchy's search
(`Wall`, `t:Coin` for the tag, `c:BoxCollider` for a component; `l:` and `cell:` named for worlds). (8) Click empty
space: with nothing selected the
Inspector shows the scene's settings (the Sky section and the timing are later pages'). (9) Clear the active box of
**Walls**: its children stop drawing and colliding; set it again. (10) Save, then see that a project holds several
scenes: **File ▸ New Scene** makes an empty one (a level or a menu would be one), saved as `Scenes/Test.stscene`, and
**File ▸ Open Scene** goes back to `Main`; the start scene stays `Main`. The built-in meshes are listed (Cube,
Sphere, Plane, Quad, Cylinder, Capsule, Cone, Torus, and the default material), and the Add Component popup's
categories show that the engine's modules register the components a scene can hold; the page writes no count of
them. The exercises (`new:17`) are two editor tasks. At the end the reader can compose an entity from components,
parent entities, edit many at once and switch a group off; the checkpoint holds the walled ground, the ball and the
placeholder coin.

**Leaves out.**

- What the three numbers of a position, a rotation and a scale mean; the gizmos in depth → `make/transforms-units`
- Colliders and bodies; why a collider without a rigid body stands still → `make/physics`
- The ground's material and new materials → `make/materials`
- Reusing the coin → `make/prefabs`
- GameObjects and other engines' names for entities → `start/coming-from`
- Object models compared: inheritance, components, ECS → `world/what-a-world-is`
- The registry, storages and handles inside → `world/ecs`
- Property metadata and registration → `world/reflection`
- How the Inspector is generated → `editor-ui/inspectors`
- Every component and its properties → `reference/components`

**Fit.** `fits`: about 3,550 words against M (3,000). Ten steps at B0's length take most of it, with the idea taught
from zero and its figure, five pictures of the menus, the Hierarchy and the Inspector, and two exercises.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:50-51` | feature | home | The Hierarchy (tree, rename, drag to parent, the "+" menu) and the Inspector (every selected entity at once, Add Component, scene settings with nothing selected) |
| `gamedev:67` | feature | home | The registered components, met by category in the Add Component popup; the count is not typed (see `new:1`) |
| `gamedev:68` | feature | home | One description per property (range, tooltip with unit, category) behind the Inspector, files, commands and scripts |
| `gamedev:69` | feature | home | The built-in meshes and the default material |
| `gamedev:298` | concept | home | Scenes, entities and components from the user's side; the "enemy class" mistake |
| `gamedev:402` | figure | home | An entity as an ID and its components, beside an inheritance tree |
| `gamedev:443` | figure | home | The Hierarchy's "+" menu: meshes with colliders, Mesh only, lights, UI |
| `gamedev:444` | figure | home | The Inspector with the four walls selected (mixed values) and with nothing selected |
| `gamedev:580` | term | home | Transform |
| `gamedev:588` | term | home | Built-in mesh |
| `scene-ecs:597` | hands-on | home | Step 9: the **Walls** parent switched off and on |
| `new:1` | erratum | home | `plan/inventory/gamedev.md:67` and `:272` count 40 registered components; the engine registers 42 (the list of `gamedev:67` holds 42 names), and `component.list` returns 39 of them, leaving out the hidden `ID`, `Relationship` and `Inactive`. The page names the categories and types no count; `process.md`'s table of errata holds the row. Evidence: `StrataTests/Architecture/ComponentSchema.json` at the pin, 42 entries under `Components`; `StrataEditor/src/Editor/Commands/EntityCommands.cpp:619-620` skips the hidden ones, which are the three of `Strata/src/Strata/Scene/ComponentRegistration.cpp:72`, `:90`, `:100` (counted and read at the pin) |
| `scene-ecs:29-30` | feature | use | An entity's lasting identity, and the components every entity is made with |
| `scene-ecs:33` | feature | use | Duplicating with fresh identities (Ctrl+D) |
| `scene-ecs:51-55` | feature | use | The ID, Name, Tag, Inactive and Transform components, as the Inspector shows them |
| `scene-ecs:72` | feature | use | Parenting by drag keeps where the child is in the world |
| `scene-ecs:82` | feature | use | Activity in the hierarchy: a switched-off parent switches off its children |
| `scene-ecs:281` | concept | use | Components as plain data, at the user's level |
| `scene-ecs:311` | concept | use | Activity, at the user's level |
| `scene-ecs:472` | figure | use | The Hierarchy panel |
| `scene-ecs:477-478` | figure | use | The Inspector's sections; the Add Component menu |
| `scene-ecs:483` | figure | use | The Inspector with nothing selected |
| `scene-ecs:611` | term | use | Entity |
| `scene-ecs:613` | term | use | Component |
| `scene-ecs:624` | term | use | Scene |
| `scene-ecs:634` | term | use | Active in hierarchy |
| `editor-ui:144-145` | feature | use | The Hierarchy and the Inspector panels |
| `editor-ui:175` | feature | use | Component sections for what every selected entity has |
| `editor-ui:177` | feature | use | Mixed values across entities |
| `editor-ui:183` | feature | use | The component menu and the Add Component popup |
| `editor-ui:187` | feature | use | Scene settings with nothing selected, named only |
| `editor-ui:239` | feature | use | Delete, Ctrl+D, F2 and the other selection shortcuts |
| `editor-ui:551` | figure | use | The Hierarchy with a group expanded and an entity switched off |
| `editor-ui:555` | figure | use | The Inspector on one entity and on three with mixed values |
| `editor-ui:693` | hands-on | home | Step 7's search of the Hierarchy by name, `t:` and `c:`; `l:` and `cell:` named for `make/large-worlds` |
| `editor-ui:686` | hands-on | home | A small scene built with the Hierarchy and the Inspector: create, rename with F2, reparent by drag, multi-edit; the page's steps on Coin Run's level |
| `new:17` | hands-on | home | Exercises, two editor tasks in `Scenes/Test.stscene`: **Basic.** a table made of a flattened Cube top and four Cube legs under an empty **Table**, switched off and on by its parent's active box; **Medium.** predict which entities the Hierarchy's search `c:BoxCollider` finds in Coin Run's level (the ground and the four walls, not the ball's sphere or the coin's collider-less cylinder), then search to check. Evidence: `StrataEditor/src/Editor/ProjectTemplates.cpp:83-85` (the Ground's box collider); `StrataEditor/src/Panels/SceneHierarchyPanel.cpp:76-79` (Cube with a box collider, Sphere with a sphere collider); `StrataEditor/src/Editor/HierarchyView.cpp:95-100` (the `c:` and `t:` prefixes) |
| `editor-core:74-76` | feature | use | `scene.*`, `entity.*` and `component.*`, the commands of the steps' command tabs |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The panels, selecting and moving the view | `make/editor-tour` | must |
| A position, a rotation and a scale as numbers to type | `make/transforms-units` | helps |
| A scene as a document the engine plays | `start/what-an-engine-is` | helps |

**Starting state.** The end state of `make/editor-tour` (`startsFrom {"tutorial": "make/editor-tour"}`): Coin Run's
fresh Basic 3D project; `make/project-files` changed nothing in it. The page ends with Coin Run's level: the ground,
four walls under **Walls**, the ball and the placeholder coin tagged `Coin`, and the empty `Scenes/Test.stscene` of step
10 (later pages use it as a scratch scene).

**Command-only steps.** none

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `built-in-mesh` | Built-in mesh | - |
| `scene` | scene | - |
| `transform` | transform (use) | transformation |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-make-a-7 | should | stale-item | `make/hud` (steps 3 to 5), `make/project-coin-run` (steps 2 and 3) | After the canvas of step 1, steps 3 to 5 make the texts and the panel with **+ ▸ UI ▸ ...**. The Hierarchy's **+** button (and the Entity menu) always creates at the top level, and a UI element made outside a canvas gets a new canvas of its own, so each step adds another canvas. An element goes into the canvas through the canvas's right-click **Create Child ▸ UI ▸ Text**, which no page names. | Step 3 makes its text with a right-click on the canvas ▸ **Create Child ▸ UI ▸ Text** and says why; steps 4 and 5 and the win and lose panels of `make/project-coin-run` do the same; `make/scenes-entities` names **Create Child** beside the "+" menu in one sentence (about 70 words). | `allocation/make-a.md:1509-1513`, `:1808-1810`; `StrataEditor/src/Panels/SceneHierarchyPanel.cpp:560`, `:929-931`; `StrataEditor/src/EditorLayer.cpp:1582`; `StrataEditor/src/Editor/GameUIPresets.cpp:301-310`; `Docs/Manual/GameUI.md:11-14` |
| critic-make-a-15 | should | stale-item | `make/scenes-entities` (step 2), `make/transforms-units` | The pages call a Transform's first value "Position". The Inspector labels it **Translation**, and the SDK's local calls are `GetTranslation` and `SetTranslation`, beside `GetWorldPosition`. A B0 reader told to "type its Position" finds no such field. | `make/scenes-entities` step 2 says "**Translation**, its position"; `make/transforms-units` teaches the word once where it teaches a position, and its code section names `SetTranslation` for the local position and `SetWorldPosition` for the world one (about 40 words). | `allocation/make-a.md:221`, `:321-322`, `:337-339`; `StrataTests/Architecture/ComponentSchema.json:57`; `Strata/src/Strata/Scene/ComponentRegistration.cpp:84`; `StrataScriptCore/Include/StrataScript/Entity.h:171`, `:177`, `:200` |
| critic-make-a-19 | should | order | `make/scenes-entities`; `make/project-coin-run` (step 5) | Coin Run's camera is framed only on `make/project-coin-run`. Until then the Game view shows Basic 3D's camera, 6 m back and 2 m up, aimed at the centre with a vertical view of 60 degrees. The ground nearest the camera, from about z = 4 to the wall at z = 10, almost a third of the 20 m level, and that wall are out of view, so the ball and coins leave the screen on `make/input` to `make/hud`. | `make/scenes-entities` adds a step after the walls: the Main Camera set high and tilted down over the level (for example Translation (0, 16, 13), Rotation (-55, 0, 0)), checked with the Game camera chip (F8); `make/project-coin-run` step 5 then only adjusts it (about 120 words). | `allocation/make-a.md:221-223`, `:1812`; `StrataEditor/src/Editor/ProjectTemplates.cpp:31`, `:51-55`; `Strata/src/Strata/Scene/Components.h:133`; `StrataEditor/src/Panels/ViewportPanel.cpp:460-461` |
