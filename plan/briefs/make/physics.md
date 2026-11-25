# Brief: `make/physics`

| Field | Value |
| --- | --- |
| Title | Physics for game makers |
| Kind | T |
| Size | L |
| Tracks | G, B |
| Needs | `make/input` |
| From | gamedev "Physics for game makers" (§1.11, concept 15); physics (use side) and the use half of physics "Tuning and measuring physics" (`Physics.Simulation`, `physics.stats`, the pile that never sleeps); force, mass, velocity and impulse at the use level (what `AddForce` and an impulse do to the ball); scripting "The gameplay API, part 2": `RigidBody`, `Physics` (raycasts, queries, collision layers), contacts and triggers; Coin Run's ball rolls by a force in `OnFixedUpdate` and its coins are triggers (hands-on G12, balls shot through the cursor, is `make/gameplay-math`'s exercise) |
| Unit | `plan/allocation/make-a.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `make/physics` — Physics for game makers

**Covers.** The page makes Coin Run's ball roll by a force and turns the coins into triggers, and is the use home of
rigid bodies, colliders, triggers, contacts, queries, collision layers and the maker's half of tuning. The ideas from
zero first, each in a paragraph: what a physics engine does for a game (bodies that fall, collide and rest, stepped in
the fixed steps of `make/script-loop`); the body types with the choice figure (a collider alone is a static body,
Dynamic is simulated, Kinematic is moved by code and pushes others, a trigger reports overlaps and pushes nothing);
colliders are shapes, not meshes (Box, Sphere, Capsule, Mesh as convex or, on static bodies only, triangles); force,
mass, velocity and impulse at the use level (a velocity is a speed with a direction; a force changes the velocity a
little every step and less for a heavier body; an impulse changes it at once). The steps. (1) **Add Component ▸
RigidBody** on the ball (Dynamic, Mass 1) and Play from 3 m up: it falls onto the template's ground collider and rests;
the collider gizmos shown. Gravity is the scene's: with nothing selected, the Inspector's scene settings show the
Physics section with its summary ("Gravity 9.81 m/s² · 60 steps/s"), Gravity in m/s² (set there, or with
`scene.setSettings` in the command tab; changing it wakes every body), and a script cannot change it, only a body's
**Gravity Scale** (0 for a body that floats); Max Bodies and Max Contacts stay Auto at 0 and are set only for scenes
that create many bodies while they play. (2) Roll it: `BallControl` stops writing the position; it reads the Move action
in `OnUpdate` and pushes with `GetRigidBody().AddForce` in `OnFixedUpdate`, because forces act during the next step
only; a field for the strength; its speed read back with `GetLinearVelocity` and capped. (3) Tune the ball: friction,
restitution (a bounce needs more than 1 m/s), linear and angular damping so it slows, Continuous Collision named for
fast bodies. (4) A reset key: `Teleport` puts the ball back at the start, never a written transform, which takes effect
only at the next step and slides. (5) The coins as triggers: on the coin prefab a Sphere Collider and a RigidBody,
Kinematic with **Is Trigger** (they spin and bob, so they are moved by code), applied to the prefab; the `Coin` script's
`OnTriggerEnter` checks that the other entity is the ball and collects the coin, which replaces the distance test of
`make/scripting-scene`; triggers never see triangle-mesh colliders, so the coin keeps a sphere; `OnCollisionEnter` and
`OnCollisionExit` for bodies that touch, with the contact's point and normal (`make/sound` uses them). (6) Jump: a
raycast down from the ball with `Physics::Raycast` tells whether it is on the ground, and the Jump action of
`make/input` then gives it an impulse upward with `AddImpulse`, which changes the velocity at once; the press is read in
`OnUpdate`, because fixed updates run zero to N times a frame and a press read in `OnFixedUpdate` is missed or counted
twice (the rule, with `make/script-loop`'s root of it). (7) Collision layers: **File ▸ Project Settings ▸ Collision
Layers**, layers `Ball` and `Coin` named and a `Ghost` wall the ball passes through. The gotcha line of the step: the
wall needs a RigidBody of type Static, because a collider alone is a static body on layer 0 with the default material
(friction 0.5, restitution 0), and a RigidBody with no collider gets no body at all (it does not fall, and the Console
warns). The layers are the project's, not the scene's; a script turns the pair on and off with
`Physics::SetLayersCollide`, and the change holds until the scene ends or the project's table changes (an exercise opens
the gate when every coin is taken). (8) Measure and tune in a scratch scene that is not saved: a pile of balls, the
Streaming panel's Physics section ("awake N of M", the step's time), **Physics ▸ Simulation**'s Sleep Threshold changed
until the pile sleeps; `physics.stats` in the command tab. The gotchas in one list: spawn bodies apart (overlapping
bodies are pushed out at 3 m/s), `Instantiate` with a position gives scale 1, a moving dynamic body is never moved by
writing its transform. What Strata does not do here, each in a sentence or two: joints, ragdolls and vehicles (`new:6`);
height-field and cylinder colliders, where the Hierarchy's Cylinder, Cone and Torus get a convex mesh collider of their
own mesh (`new:30`); cloth, soft bodies, destruction, fluids and buoyancy (`new:31`); stay events and a contact's
impulse or impact speed, so a script reads the bodies' velocities for a hit's strength (`new:32`); rolling resistance
and conveyor belts, so a rolling ball slows only through its damping (`new:33`). The exercises: a toppled stack of ten
crates with `AddImpulseAtPosition`, four balls of wood, metal, rubber and ice, whose pairs mix as box3d does by default
(friction the square root of the two frictions' product, restitution the larger of the two, so an ice ball slides on
wood and a rubber ball bounces on a floor of restitution 0), a trigger that counts balls and a launch pad (as the
Physics Playground's `GoalBasket` and `LaunchPad`), a gun that pushes what its ray hits. At the end the reader can
choose a body, push it the right way, react to triggers, cast rays, filter with layers and read the physics numbers; the
checkpoint has the rolling ball and the trigger coins.

**Leaves out.**

- Rigid bodies and colliders inside → `physics/bodies-colliders`
- How bodies are built from entities → `physics/building-bodies`
- Integration and Newton's laws → `physics/dynamics`, `basics/math-change`
- Collision detection → `physics/collision-detection`
- Collision layers inside → `physics/collision-layers`
- Contacts and triggers inside → `physics/contacts-triggers`
- Queries inside; why there are no shape sweeps → `physics/queries`
- Tuning inside: contact recycling, the solver → `physics/tuning`
- Character controllers → `make/characters-cameras`
- Balls shot through the cursor along a ray from the camera → `make/gameplay-math`
- Impact sounds → `make/sound`
- The index of everything Strata does not have → `appendix/not-in-strata`

**Fit.** `over`: about 7,000 words against L (5,000). A page of track B is at most L, so it splits by S3:
`make/physics`, "Physics for game makers" (the four ideas, steps 1 to 6, the gotchas, the absences, the crates, the four
balls and the trigger counter, about 5,650 words, L), then a how-to after it on tracks G and B, "Queries, collision
layers and tuning physics" (`RaycastAll` and the overlaps, steps 7 and 8, the gun and the ghost gate, about 2,400 words,
M). The new page keeps the use homes of collision layers and tuning on track B, and the Assumes rows that name
`make/physics` for collision layers would name it.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:152` | feature | home | Bodies and colliders: the RigidBody's properties, the four collider shapes, a collider without a body is static |
| `gamedev:153` | feature | home | The script API: velocities, forces, impulses, `Teleport`; `Raycast`, `RaycastAll`, `OverlapSphere`, `OverlapBox` with masks; contact callbacks |
| `gamedev:154` | feature | home | Collision layers: 32 project layers and their matrix; `Physics::SetLayersCollide` |
| `gamedev:155` | feature | home | Simulation tuning: the five fields, live while playing |
| `gamedev:70` | feature | home | Scene settings, step 1's Physics section with nothing selected: its summary, Gravity in m/s² (the scene's, set in the Inspector or with `scene.setSettings`; scripts set only a body's Gravity Scale), Max Bodies and Max Contacts at Auto 0, set only for scenes that create many bodies while they play; the fixed timestep and the steps per frame are used on `make/script-loop`. Evidence: `Strata/src/Strata/Scene/Scene.h:42-66`; `StrataEditor/src/Panels/InspectorPanel.cpp:256-266`, `:322-353`; `StrataEditor/src/Editor/EditorSceneCommands.cpp:569-579`; `git grep -ni gravity 822a7a46 -- StrataScriptCore/Include/StrataScript/ScriptABI.h` finds only the character controller's GravityScale (`:542`) (read at the pin) |
| `gamedev:159` | feature | home | The gotchas: triggers and triangle meshes, overlapping spawns, `Instantiate`'s scale, bounces above 1 m/s |
| `gamedev:328` | concept | home | Rigid-body physics for makers; the mistakes (moving a dynamic body by its transform, triggers on triangle meshes, overlapping spawns) |
| `gamedev:418` | figure | home | The body choices: static, dynamic, kinematic, trigger, character controller; which shapes a trigger sees |
| `gamedev:488` | rule | home | Read presses in `OnUpdate`, apply forces in `OnFixedUpdate`: step 2's Move and step 6's Jump, with the press half of the mistake that `make/script-loop` roots (a press read in `OnFixedUpdate` is missed or counted twice) |
| `gamedev:492` | rule | home | Teleport with `Teleport`, not by writing a transform |
| `gamedev:501` | rule | home | Triggers do not see triangle-mesh colliders |
| `gamedev:502` | rule | home | Spawn bodies apart; `Instantiate` with a position sets scale 1 |
| `gamedev:503` | rule | home | Collision layers are the project's, not the scene's |
| `gamedev:621` | term | home | Rigid body (static, dynamic, kinematic) |
| `gamedev:622` | term | home | Collider (box, sphere, capsule, mesh; convex, triangle) |
| `gamedev:623` | term | home | Trigger |
| `gamedev:624` | term | home | Collision layer, layer matrix, mask |
| `gamedev:625` | term | home | Raycast and overlap |
| `gamedev:626` | term | home | Continuous collision |
| `gamedev:627` | term | home | Sleeping |
| `physics:445` | hands-on | home | Step 1: a body falling onto a floor that has only a collider |
| `physics:446` | hands-on | home | Exercise: ten crates toppled with `AddImpulseAtPosition` |
| `physics:447` | hands-on | home | Exercise: four balls of wood, metal, rubber and ice, predicted with box3d's default mixing of a pair (friction the square root of the product, restitution the larger value; the rule's home is `physics/bodies-colliders`). Evidence: `Strata/vendor/box3d/src/physics_world.c:155-165`, `:341-347`; `git grep -n -e frictionCallback -e restitutionCallback 822a7a46 -- Strata/src` finds nothing, so Strata keeps the defaults (run at the pin) |
| `physics:448` | hands-on | home | Exercise: a trigger that counts balls and a launch pad |
| `physics:449` | hands-on | home | Exercise: a gun that shoots with `Physics::Raycast` and pushes what it hits |
| `physics:451` | hands-on | home | Step 7 and its exercise: a Ghost layer switched at run time, on a wall with a Static RigidBody; the gotcha line: a collider alone is a static body on layer 0 with the default material, and a RigidBody with no collider gets no body and does not fall. Evidence: `Strata/src/Strata/Physics/PhysicsWorld.cpp:1997-2004` (the layer comes only from a RigidBody), `:2009-2010`, `:2017-2018` (the defaults without one), `:2503` (the warning); `Strata/src/Strata/Physics/PhysicsComponents.h:34-35` (friction 0.5, restitution 0) (read at the pin) |
| `physics:455` | hands-on | home | Step 8: the Sleep Threshold tuned on a pile of balls |
| `scene-ecs:603` | hands-on | home | Step 7: collision layers named and changed from a script during play; the change holds until the scene ends or the project's table changes (the scene's working copy against the project's table). Evidence: `Strata/src/Strata/Scene/Scene.h:647-648`, `:660-665` (read at the pin) |
| `new:6` | not-done | home | Joints, ragdolls and vehicles. Evidence: `git grep -n "b3Create.*Joint" 822a7a46 -- Strata/src` finds nothing (run at the pin); `Docs/Roadmap.md:1716-1718` |
| `new:30` | not-done | home | Height-field and cylinder colliders: Box, Sphere, Capsule and Mesh only; the Hierarchy's Cylinder, Cone and Torus get a convex mesh collider of their own mesh, a hull of at most 64 vertices, and the torus's hull fills its hole. Evidence: `Strata/src/Strata/Physics/PhysicsComponents.h:44-68`; `StrataEditor/src/Panels/SceneHierarchyPanel.cpp:65-69`, `:83-88`; `Strata/src/Strata/Physics/PhysicsMeshShapes.h:47-49`, `:57` (read at the pin) |
| `new:31` | not-done | home | Cloth, soft bodies, destruction, fluids and buoyancy. Evidence: `git grep -niE -e cloth -e "soft ?bod" -e fluid -e buoyan -e fractur -e destructible 822a7a46 -- Strata/src` finds nothing (run at the pin; the word "destruction" matches only the destruction of entities and objects) |
| `new:32` | not-done | home | Stay events, and the impulse or impact speed of a contact: contacts begin and end, and a script that needs a hit's strength reads the bodies' velocities. Evidence: `Strata/src/Strata/Scene/SceneServices.h:41-45`; `StrataScriptCore/Include/StrataScript/ScriptABI.h:181-188` (a contact holds the other entity, a point and a normal); `git grep -n enableHitEvents 822a7a46 -- Strata/src` finds nothing (run at the pin); `Samples/PhysicsPlayground/Scripts/Impact.cpp:53-55` |
| `new:33` | not-done | home | Rolling resistance and tangent velocity (conveyor belts) of box3d's surface material: a rolling ball slows only through its damping. Evidence: `git grep -n -e rollingResistance -e tangentVelocity 822a7a46 -- Strata/src` finds nothing (run at the pin); `Strata/vendor/box3d/include/box3d/types.h:417-431` |
| `physics:28-32` | feature | use | The RigidBody and the four collider components, as the Inspector shows them |
| `physics:34-35` | feature | use | The collider gizmos; how a body is made of an entity's colliders |
| `physics:41` | feature | use | Static, dynamic and kinematic bodies |
| `physics:46-50` | feature | use | Friction and restitution, mass, rotation locks, continuous collision, triggers as sensors |
| `physics:93-94` | feature | use | Forces act in the next step, impulses at once; `Teleport` |
| `physics:95` | feature | use | Step 1: gravity from the scene's settings, and a change of it wakes every body |
| `physics:107` | feature | use | The scripts' trigger and collision callbacks |
| `physics:114` | feature | use | `Raycast`, `RaycastAll`, `OverlapSphere`, `OverlapBox` |
| `physics:122-123` | feature | use | Layers, the matrix and the project's section |
| `physics:125-126` | feature | use | Layers changed at run time; the Collision Layers page |
| `physics:146` | feature | use | The `Physics.Simulation` section's fields |
| `physics:172` | feature | use | `physics.stats` and the Streaming panel's Physics row |
| `physics:229` | concept | use | Body types, at the maker's level |
| `physics:233` | concept | use | Colliders and shapes, at the maker's level |
| `physics:255` | concept | use | Sleeping, at the maker's level |
| `physics:261` | concept | use | Triggers, at the maker's level |
| `physics:265` | concept | use | Spatial queries, at the maker's level |
| `physics:369` | figure | use | Collider gizmos shown in the editor |
| `physics:371-372` | figure | use | The RigidBody's Inspector; the Collision Layers page |
| `physics:374-375` | figure | use | The Simulation page; the Streaming panel's Physics row |
| `physics:392` | rule | use | Use `Teleport` for instant moves |
| `physics:394` | rule | use | Apply forces in `OnFixedUpdate`, every step they should act |
| `physics:406` | rule | use | Do not spawn bodies overlapping |
| `physics:408` | rule | use | Triangle meshes only on static bodies; triggers do not see them |
| `physics:433` | rule | use | Restitution needs more than 1 m/s to bounce |
| `scripting:125` | feature | use | The SDK's `RigidBody`, `Physics`, `RaycastHit` and `Collision` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The Move action and reading it in `OnUpdate` | `make/input` | must |
| `OnFixedUpdate` and the fixed step | `make/script-loop` | must |
| Components, colliders on the presets, the prefab and Apply | `make/prefabs` | must |
| Writing transforms and finding entities from a script | `make/scripting-scene` | must |
| Project Settings and its pages | `make/project-files` | must |
| A direction as three numbers, scaled | `make/transforms-units` | must |
| Rates, accumulation and Newton's laws as mathematics | `basics/math-change` | helps |

**Starting state.** The end state of `make/input` (`startsFrom {"tutorial": "make/input"}`): the ball moved by the
Move action through its position, the coins placed by `CoinPlacer`, the Jump action defined. Step 8's pile of balls is
built in the scratch scene `Scenes/Test.stscene` and not saved. The page ends with the ball rolling by a force and
jumping, and the coins collected as triggers.

**Command-only steps.** none

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `continuous-collision` | Continuous collision | - |
| `layer-matrix` | layer matrix | - |
| `mask` | mask | - |
| `sleeping` | Sleeping | - |
| `overlap` | overlap (use) | - |
| `collider` | Collider (use) | - |
| `rigid-body` | Rigid body (use) | - |
| `collision-layer` | Collision layer (use) | - |
| `trigger` | Trigger (use) | - |
| `raycast` | Raycast (use) | RaycastAll, shape cast (sweep) |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-make-a-3 | must | missing-item | `make/scripting-scene`; `make/physics` (step 2) | No page of block A teaches how a script reaches its own entity: `Script::GetEntity()`, with `GetTransform()` (the Spinner's) as its shortcut. Hiding or destroying the coin, and reading its tag, need it. `make/physics` step 2 writes `GetRigidBody().AddForce`, which does not compile in a script: `GetRigidBody` is a member of `Entity`, not of `Script`. The only row that names `GetEntity` is on `reference/script-api`. | `make/scripting-scene` names the two members of `Script` before step 5 and writes `GetEntity().SetActive(false)` and `GetEntity().Destroy()` in step 8 (about 60 words). `make/physics` step 2 writes `GetEntity().GetRigidBody().AddForce(...)`. | `allocation/make-a.md:1065-1067`, `:1098`, `:1268`; `allocation/reference.md:58`; `StrataScriptCore/Include/StrataScript/Script.h:100-101`; `StrataScriptCore/Include/StrataScript/Entity.h:51`, `:59`, `:76` |
| critic-make-a-11 | should | missing-item | `make/physics` (step 4), `new:48` on `make/project-coin-run` | `RigidBody::Teleport` moves the body and keeps its velocities. Step 4's reset key would put the ball back at the start still rolling at its old speed, and the Hard exercise of `new:48` would send it back still moving toward the obstacle. | Step 4 sets the linear and angular velocity to zero after `Teleport` (`SetLinearVelocity`, `SetAngularVelocity`), with the reason in one sentence; the solution of `new:48` does the same (about 40 words). | `allocation/make-a.md:1271-1272`, `:1845`; `StrataScriptCore/Include/StrataScript/Physics.h:61`, `:74`, `:117-132` |
| critic-make-a-12 | should | shape | `make/physics` (step 5), `make/project-coin-run` (step 5, `new:48`) | From `make/scripting-scene` step 4 on, `CoinPlacer` places the coins while the game plays and the five hand-placed instances are gone, so the edited scene holds no coin. Yet `make/physics` step 5 changes the coin prefab through an instance and Apply, `make/project-coin-run` step 5 tunes the coins' bob and spin in the Inspector, and `new:48` overrides a field on one gold coin. None has an instance to work on, and edits of the running copy are gone at Stop. | `make/physics` step 5 drags one coin prefab into the level, adds the collider and the body, applies, and deletes the instance (about 60 words); `make/project-coin-run` step 5 finds the values while playing, then sets them the same way; `new:48`'s coin is a sixth one placed by hand. | `allocation/make-a.md:1057-1058`, `:1130`, `:1273`, `:1812-1813`, `:1845`; `allocation/make-a.md:659` (`new:5`: no prefab edit mode); `StrataEditor/src/Editor/EditorPrefabCommands.cpp:436-442` (Apply writes an instance back, edit mode only) |
| critic-make-a-16 | should | stale-item | `make/lighting` (step 7), `make/physics` (steps 1, 7 and 8), `make/input` (step 4), `make/export` (step 8) | Labels the steps name differ at the pin. The sun's softness is **Angular Diameter** in the Inspector (stored as `ShadowSoftness`); the component is **Rigid Body**; the export's pruning box reads **Leave out unused assets**, not Prune; and Project Settings lists its pages under Physics (Collision Layers, Simulation, Timing), Input (Input Actions) and Rendering (Graphics Quality). | The steps use the pin's labels and paths (**Project Settings ▸ Physics ▸ Collision Layers**); `make/lighting` keeps "the sun's size" as the meaning of Angular Diameter (no words added). | `allocation/make-a.md:718`, `:1261-1262`, `:1280`, `:1148`, `:1707`; `StrataTests/Architecture/ComponentSchema.json:480`, `:2173`; `StrataEditor/src/UI/ExportDialog.cpp:311`; `Strata/src/Strata/Scene/ProjectCollisionLayers.cpp:59-60`; `Strata/src/Strata/Physics/PhysicsSimulationSettings.cpp:55-56`; `Strata/src/Strata/Scene/ProjectSceneTiming.cpp:78-80`; `Strata/src/Strata/Input/InputActionSet.cpp:627-628`; `Strata/src/Strata/Renderer/RendererQuality.cpp:712-713` |
| critic-make-a-26 | could | missing-item | `make/physics` (step 7) | `Physics::SetLayersCollide` takes layer numbers, not the names the reader typed on the Collision Layers page. `Physics::GetLayerIndex("Ghost")` gives the number (-1 for a name the project lacks), and a query's mask is `1u << index`. | Step 7's code calls `GetLayerIndex` for both layers and checks for -1, in one sentence and one line (about 30 words). | `allocation/make-a.md:1284-1286`; `StrataScriptCore/Include/StrataScript/Physics.h:258-280`; `.claude/skills/strata-make-a-game/SKILL.md:290` |
