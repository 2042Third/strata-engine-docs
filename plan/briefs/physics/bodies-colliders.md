# Brief: `physics/bodies-colliders`

| Field | Value |
| --- | --- |
| Title | Rigid bodies and colliders |
| Kind | C |
| Size | M |
| Tracks | E |
| Needs | `world/scene-graph`, `basics/math-vectors` |
| From | physics ch. 3 (the concepts; its hands-on is `make/physics`'); 1.1, 1.2; concepts 4-6 |
| Unit | `plan/allocation/physics.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `physics/bodies-colliders` — Rigid bodies and colliders

**Covers.** The problem as the reader meets it: in the editor, the Playground's crate is a mesh you see, but physics
needs a body and a shape; the collider gizmos make the shapes visible (the viewport's All Colliders on and off). The
naive answer is to collide the rendered mesh itself, and it breaks on cost and on meshes that have no volume. The idea:
a rigid body (a pose, velocities and a mass) made of one or more simple colliders. Then, in teaching order: units
(metres, kilograms, seconds, gravity of -9.81 m/s² on Y, and one paragraph on why precision falls far from the origin,
linking `physics/scale-streaming`); the three body types (static, dynamic, kinematic) and what goes wrong when one is
moved like another; the collider shapes (box, sphere, capsule, convex hull, triangle mesh; why a triangle mesh is static
only; why a round mesh made convex is not exactly round); the material of a body (friction and restitution, one material
for every shape of the body; how two touching bodies' materials combine, box3d's rule that Strata keeps: friction as the
square root of the product, restitution as the larger value, with one worked pair; damping and gravity scale) and
rotation locks on world axes; composing one body from an entity hierarchy, with the approaches of engines compared (a
rigid body with child colliders as one compound, or a body per component) and Strata's rule: an entity with a
`RigidBody` is one body made of its own colliders and those of descendants without their own, a lone collider is a
static body, events and queries report the owner, and scale is baked into the shapes; when the parent's body moves, a
dynamic descendant with its own `RigidBody` keeps its own world pose, while kinematic and static descendants follow the
parent (the nested write-back of `physics/world-step` shows how). A rule box says what a body needs: a `RigidBody`
without a collider gets no body and does not fall (the log warns), and a lone collider is a static body with the default
material on layer 0, so a wall that needs another layer or material takes a Static `RigidBody`. The components are shown
as plain data (`RigidBodyComponent`) beside their Inspector. What Strata cannot do: no height-field and no cylinder
colliders (the Create menu's Cylinder, Cone and Torus collide as convex hulls of their meshes, and the torus's hull
fills its hole); no rolling resistance and no tangent velocity of box3d's surface material. Common mistakes: a
`RigidBody` on every child, a triangle mesh on a dynamic body, a static body moved every frame, a dynamic body moved by
writing its transform, non-uniform scale under a rotated parent (a shear, which a shape cannot represent: it takes the
decomposed scale). At the end the reader can choose the body type and colliders for an object and predict which bodies a
hierarchy gives.

**Leaves out.**

- Making bodies and colliders in a game, step by step → `make/physics`
- How shapes are built from the components (scale baking, shared hulls, cooking) → `physics/building-bodies`
- How mass, inertia and forces move a body → `physics/dynamics`
- Triggers → `physics/contacts-triggers`
- Collision layers → `physics/collision-layers`
- The character controller component → `physics/character-controllers`
- The full property tables, every property with its default and range → `reference/components`
- The units of every property → `reference/physics`

**Fit.** `over`: about 4,850 words against M (3,000). Four ideas from zero, the composition rule with its diagram, the
material's mixing rule, the rule box, the component's excerpt and two pictures of the editor pass M's top; L (5,000) by
S2.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `physics:28-32` | feature | home | `RigidBodyComponent` and the box, sphere, capsule and mesh colliders: every field, its unit and default; a mesh collider falls back to the MeshRenderer's mesh |
| `physics:34` | feature | home | The collider gizmos and the viewport's All Colliders toggle, as what makes shapes visible |
| `physics:35` | feature | home | The body composition rule (the code of it is `physics/building-bodies`') |
| `physics:41` | feature | home | Static, dynamic and kinematic bodies and the box3d types they map to |
| `physics:46` | feature | home | Friction and restitution per body, one material for all its shapes |
| `new:27` | concept | home | How the materials of two touching bodies combine (about 120 words, in the material paragraph): box3d's default callbacks, which Strata keeps, take friction as the square root of the product and restitution as the larger value; one worked pair: an ice ball (friction 0.05) on a wood floor (0.5) slides with about 0.16, and a rubber ball (restitution 0.8) on a floor of restitution 0 bounces with 0.8. `make/physics` uses it in the four-balls exercise; `physics/dynamics` names it where friction and restitution enter the contact. Evidence: `Strata/vendor/box3d/src/physics_world.c:155-165`, `:341-352`; `git grep -ni -e frictioncallback -e restitutioncallback 822a7a46 -- Strata/src` finds nothing (run at the pin) |
| `new:28` | rule | home | What a body needs, a rule box (about 120 words): a RigidBody with no collider gets no body, does not fall, and the log warns once ("has a Rigid Body but no collider; it is not simulated"); a collider with no RigidBody on itself or an ancestor is a static body with the default material (friction 0.5, restitution 0) on layer 0; so a wall or floor that needs another layer or material needs a Static RigidBody, as `make/physics`' Ghost wall does. Evidence: `Strata/src/Strata/Physics/PhysicsWorld.cpp:2499-2503` (the warning), `:2009-2010` and `:2017-2018` (the defaults without a RigidBody), `:1997-2004` (the layer comes only from a RigidBody); `Strata/src/Strata/Physics/PhysicsComponents.h:34-35`, `:41` |
| `physics:48` | feature | home | Rotation locks on world axes |
| `physics:222` | concept | home | Units (m, kg, s), gravity -9.81 and float precision far from the origin; the mistake of building in centimetres or at huge coordinates |
| `physics:229-237` | concept | home | Body types; colliders and shapes; composing bodies from an entity hierarchy, with their mistakes, among them non-uniform scale under a rotated parent (shear cannot be represented, the shape takes the decomposed scale; about 40 words) |
| `new:22` | feature | home | Nested bodies, one paragraph of the composition rule (about 80 words): when the parent's body moves, a dynamic descendant with its own `RigidBody` keeps its own world pose, and kinematic and static descendants follow the parent; the figure's "child with its own rigid body" does the first. Evidence: `Strata/src/Strata/Physics/PhysicsWorld.h:63-64`; `Strata/src/Strata/Physics/PhysicsWorld.cpp:4394`; `StrataTests/src/Physics/PhysicsHierarchyTests.cpp:422` |
| `physics:296` | code | home | `Strata/src/Strata/Physics/PhysicsComponents.h:20-42`: a rigid body as plain data, the fields a designer sets |
| `physics:336` | figure | home | Entity hierarchy to bodies: a tree with a rigid body, child colliders, a child with its own rigid body and a lone collider, and the bodies that result |
| `physics:369` | figure | home | The Playground with All Colliders on and off |
| `physics:371` | figure | home | The Inspector of a Rigid Body (and of a Character Controller, which `physics/character-controllers` uses) |
| `physics:408` | rule | home | Triangle meshes only on static bodies; triggers do not see them |
| `physics:477-484` | term | home | Terms, each its own glossary entry: rigid body, static body, dynamic body, kinematic body, collider, shape, convex hull, triangle mesh collider, compound, baked compound. Kinematic body, corrected from the inventory's "moved by game code with a velocity": a body that game code moves through its transform (or `Teleport`); Strata gives it the velocity that reaches the target in one step; it pushes dynamic bodies and is not pushed, and refuses velocities, forces and impulses |
| `physics:506-509` | term | home | Terms: restitution, friction, damping, gravity scale |
| `new:3` | not-done | home | Height-field and cylinder colliders: Strata has box, sphere, capsule and mesh colliders only. The Hierarchy's Create menu gives Cylinder, Cone and Torus a convex mesh collider of their own mesh, a hull of at most 64 vertices, so a cylinder that collides is a hull, and the torus's hull fills its hole; the page's example of a round mesh made convex. Evidence: `Strata/src/Strata/Physics/PhysicsComponents.h:44-68`; `StrataEditor/src/Panels/SceneHierarchyPanel.cpp:65-69, 83-88`; `Strata/src/Strata/Physics/PhysicsMeshShapes.h:48-49, 57` |
| `new:8` | not-done | home | Rolling resistance and tangent velocity (conveyor belts) of box3d's surface material: Strata sets only friction and restitution, so a rolling ball slows only through its damping; said beside the material (about 40 words). Evidence: `git grep -n -e rollingResistance -e tangentVelocity 822a7a46 -- Strata/src` finds nothing (run at the pin); `Strata/vendor/box3d/include/box3d/types.h:417-431` (the fields of `b3SurfaceMaterial`) |
| `new:11` | hands-on | home | Exercises (D27): a doctest with `PhysicsTestUtils.h`: an entity with a RigidBody and two child box colliders, a third child with a RigidBody of its own, and a lone box collider beside them; the bodies predicted on paper by the composition rule, then checked with `PhysicsStats`' `BodyCount`, `StaticBodyCount` and `DynamicBodyCount` after one step (done). In the editor, a box of friction 0.1 on a ramp of friction 0.9 that has a Static RigidBody (so that it keeps its own material): predicted with the mixing rule, √(0.1 × 0.9) = 0.3 against tan 15° ≈ 0.27 and tan 20° ≈ 0.36, it holds at 15° and slides at 20°; then played to check (done, editor task). Evidence: `StrataTests/src/Physics/PhysicsTestUtils.h:63-92`; `Strata/src/Strata/Physics/PhysicsTypes.h:152-154`; `StrataTests/src/Physics/PhysicsHierarchyTests.cpp:148` (a test that counts the static bodies of a hierarchy); `Strata/vendor/box3d/src/physics_world.c:155-159` |
| `physics:45` | feature | link | Scale baked into shapes, named with the composition rule; the rules per shape are `physics/building-bodies`' |
| `physics:49` | feature | link | The `ContinuousCollision` field, linked to `physics/dynamics` |
| `physics:50` | feature | link | The `IsTrigger` field, linked to `physics/contacts-triggers` |
| `physics:33` | feature | link | The character controller as the other kind of mover |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Positions and directions as vectors; length | `basics/math-vectors` | must |
| Entities, the hierarchy, local and world transforms | `world/scene-graph` | must |
| Mass, force and velocity (Newton's laws) | `basics/math-change` | must |
| Components as plain data registered with the engine | `world/reflection` | helps |
| Rotations stored as quaternions | `basics/math-rotations` | helps |
| Floating-point precision that falls with distance | `basics/numbers` | helps |
| Boxes, spheres and bounding volumes | `basics/math-geometry` | helps |
| A mesh as vertices and triangles | `gpu/geometry-pool` | helps |
| Asset handles (a mesh collider names a mesh asset) | `assets/handles-meta` | helps |
| Gizmos drawn over the scene | `gpu/debug-drawing` | helps |
| Writing and running one doctest case | `core/first-change` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `baked-compound` | baked compound | - |
| `collider` | Collider | - |
| `compound` | Compound | - |
| `convex-hull` | Convex hull | - |
| `damping` | Damping | - |
| `dynamic-body` | Dynamic body | - |
| `friction` | Friction | - |
| `gravity-scale` | Gravity scale | - |
| `kinematic-body` | Kinematic body | - |
| `restitution` | Restitution | - |
| `rigid-body` | Rigid body | - |
| `static-body` | Static body | - |
| `triangle-mesh-collider` | Triangle mesh collider | - |
