# Allocation: physics

## `physics/why` — Why games need physics

**Covers.** The page opens on the part's running example, the Physics Playground sample: a crate tower, a domino run,
a pit of 500 balls, a goal that counts what falls into it and ghost boxes that sink through the balls (its two
screenshots). From it the reader meets the problem: things that fall, collide, stack and are pushed, and questions
about space ("what is under the cursor", "is the player on the ground"). The naive answer is collision written by hand
in game code (move, test for overlap, push back), and the page shows where it breaks: stacks, many objects, fast
objects. The idea: a physics engine is a second simulation beside the scene, stepped in fixed steps, that must be kept
in step with the scene's transforms. The approaches engines use come next: hand-written gameplay collision, a
third-party engine (PhysX, Havok, Jolt, Bullet, Box2D and box3d) or an engine's own solver, with a table of their
cost, quality, licence and users (sources in Further reading). Strata's choice and its reason: box3d (MIT, pinned in
`ThirdPartyNotices.md`) behind Strata's own components and scene services, with Strata's own character controller on
box3d's mover queries; box3d replaced Jolt in 0.5.0 (`Docs/Releases/0.5.0.md:30, 64-66, 75-100`). What Strata does not
do here: joints, ragdolls and vehicles; cloth, soft bodies, destruction, fluids and buoyancy. The common mistake: to
think the physics body is the transform. At the end the reader can say what box3d does and what Strata adds around
it, and which page of the part answers which question.

**Leaves out.**

- How a body and its colliders are set up → `physics/bodies-colliders`
- How a solver moves bodies and resolves contacts → `physics/dynamics`
- The fixed step and the accumulator → `core/time`
- Making a game with physics in the editor → `make/physics`
- Every property with its default and range → `reference/components`
- The units of every property and settings field → `reference/physics`

**Fit.** `over`: about 2,750 words against S (1,500). The concept shape's eight sections, from the Playground's opening
to the table of six engines, with the two exercises of D27, pass S's top; M (3,000) by S2.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `physics:217` | concept | home | What a physics engine is for in a game; the approaches (hand-written, third-party, own); Strata's choice of box3d behind components and services, with its own character controller; the mistake "physics is the transform" |
| `physics:187` | feature | home | The Physics Playground sample: six stations, about 600 bodies, its scripts and its regression; the part's running example, whose stations later pages take up |
| `physics:367` | figure | home | `Samples/PhysicsPlayground/Screenshots/Overview.png` and `BallPit.png` (both exist at the pin) as the page's opening |
| `new:1` | not-done | home | Joints, ragdolls and vehicles: Strata has none; the Roadmap lists them on box3d's joints. Evidence: `git grep -nE "b3Create[A-Za-z]*Joint" 822a7a46 -- Strata/src` finds nothing (run at the pin); `Docs/Roadmap.md:1716-1718` |
| `new:2` | not-done | home | Cloth, soft bodies, destruction, fluids and buoyancy. Evidence: `git grep -niE "cloth\|soft ?bod\|fluid\|buoyan\|fractur\|destructible" 822a7a46 -- Strata/src` finds nothing (run at the pin); the word "destruction" matches only the destruction of entities and objects |
| `new:10` | hands-on | home | Exercises (D27): in a copy of the Physics Playground, one crate lifted 3 m in the Scene view and played: it falls; its Rigid Body type set to Static and played again: it hangs in the air; its Box Collider removed: a ball shot at it with a left click passes through it. What is drawn is the MeshRenderer, what collides is the collider, and only a dynamic body falls (done, editor task). For three games (a stacking puzzle, a top-down shooter whose bullets are rays, a card game), which needs bodies, which needs only queries and which needs no physics engine, and why (design). Evidence: `Samples/PhysicsPlayground/Assets/Prefabs/Crate.stprefab:2` (a BoxCollider, a MeshRenderer and a Dynamic RigidBody on one entity); `Samples/PhysicsPlayground/README.md:35` (left click shoots a ball); `Strata/src/Strata/Physics/PhysicsComponents.h:15-18` |
| `physics:116` | feature | link | No shape sweeps in the API, named in the list of absences and linked to its page |
| `physics:51` | feature | link | The 1e5 m coordinate limit, named in one sentence |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| What a game engine is, and one frame from start to finish | `start/what-an-engine-is` | must |
| Entities and components | `world/what-a-world-is` | helps |
| The fixed step | `core/time` | helps |
| Opening a copy of a sample and pressing Play | `start/first-game` | helps |
| A velocity as a direction with a length | `basics/math-vectors` | helps |
| Third-party libraries in Strata and their licences | `engineering/third-party` | helps |

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

## `physics/collision-detection` — Collision detection: shapes, broad phase and narrow phase

**Covers.** The problem as the reader meets it: the ball pit's 500 balls make 124,750 pairs, and testing every pair
exactly each step is too slow; the exact test must also say where and how deeply two shapes touch. The naive answer,
every pair with the exact test, and its cost in big-O. The idea: two phases, a cheap broad phase on bounding boxes that
finds candidate pairs, and an exact narrow phase that computes contacts. The broad phase's approaches, each introduced
by the flaw of the one before: a uniform grid, sweep and prune, and dynamic trees of axis-aligned boxes (fattened boxes,
what a step costs when most bodies sleep), with a table of costs. The narrow phase: the separating axis test for boxes,
GJK on convex shapes (support functions and the simplex), penetration depth, and contact manifolds (points, normal and
separation; why a box resting on a box has four points). Caching between steps: contact recycling reuses a contact's
points while the bodies barely moved (box3d's 5 cm), and its price, stale points past an edge (the recycling figure);
ghost collisions at the inner edges of a floor of tiles, and the fix, one collider. Strata's choice: box3d's trees and
manifolds, which Strata does not replace; parked bodies keep their tree entries but collide with nothing (linked). The
writer checks every statement about box3d's own trees and manifolds in `Strata/vendor/box3d` at the pin, because the
inventory did not read them (`physics:596`). Sources: Ericson, *Real-Time Collision Detection*, and Erin Catto's talks
on dynamic trees and GJK. At the end the reader can explain what a pair search costs, read a contact's point and
normal, and say why a box sliding over a tiled floor bumps.

**Leaves out.**

- Solving contacts once found → `physics/dynamics`
- Continuous collision and time of impact → `physics/dynamics`
- Filtering pairs by layer → `physics/collision-layers`
- The recycle distance as a setting, and measuring it → `physics/tuning`
- Rays and overlaps against the same trees → `physics/queries`
- The mathematics of rays, planes and boxes → `basics/math-geometry`

**Fit.** `fits`: about 5,100 words against L (5,000). The narrow phase (the separating axis test, GJK, penetration
depth and manifolds) and the broad phase's three approaches take the most; contact recycling and ghost collisions
follow.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `physics:245` | concept | home | Broad phase and narrow phase: trees of boxes, pair finding, manifolds; why a step costs what is awake |
| `physics:257` | concept | home | Contact recycling as caching between steps, and its trade-off with stale geometry (ghost bumps, ledges); the setting itself is `physics/tuning`'s |
| `physics:363` | figure | home | Contact recycling: two boxes, the recycle distance and angle gates, a stale point past an edge |
| `physics:410` | rule | home | A floor of many tiles bumps at the seams (44 mm at 2 m/s, with or without recycling): make it one collider |
| `physics:499-500` | term | home | Terms: broad phase, narrow phase |
| `physics:502` | term | home | Terms: manifold, contact point |
| `physics:515-516` | term | home | Terms: contact recycling, ghost collision |
| `new:12` | hands-on | home | Exercises (D27): in `Strata/vendor/box3d/src`, where the broad phase finds new pairs (`b3UpdateBroadPhasePairs`) and where a contact is recycled instead of collided again (its distance and angle gates against the recycle tolerance), found by a search and named with their lines (trace). A doctest of a frictionless box pushed at 2 m/s along a lane of 1 m static tiles and along one collider of the lane's length, its highest centre recorded every step: it rises at the tiles' seams and not on the single collider (done; the settle scenes' seam probe in small). Evidence: `Strata/vendor/box3d/src/broad_phase.c:649`; `Strata/vendor/box3d/src/physics_world.c:651-681`, `:725`; `StrataTests/src/Physics/PhysicsScenes.cpp:81-85` (`CreateTileLane`), `:290-352` (`CreateSeamProbe`) |
| `physics:81` | feature | link | Static shapes made before the first step skip the pair search, named and linked to `physics/scale-streaming` |
| `physics:76` | feature | link | Parked bodies keep their tree entries with an empty filter, linked to `physics/scale-streaming` |
| `physics:147` | feature | link | The recycle distance as a project setting, off for kinematic and presence bodies |
| `physics:62` | feature | link | Hull limits (64 vertices, 44 when box3d's 128 faces and edges do not fit) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Rays, planes, boxes and intersection tests | `basics/math-geometry` | must |
| Axis-aligned bounding boxes | `basics/math-geometry` | must |
| Trees, their costs and big-O | `basics/trees-graphs` | must |
| Dot and cross products; projecting onto an axis | `basics/math-vectors` | must |
| Bodies, colliders and their shapes | `physics/bodies-colliders` | must |
| Rounding in floating-point geometric tests | `basics/numbers` | helps |
| Writing and running one doctest case | `core/first-change` | helps |

## `physics/dynamics` — Rigid body dynamics: integration, contacts, solvers, sleep and continuous collision

**Covers.** The problem as the reader meets it: the Playground's crate tower settling and its domino run falling,
captured at exact fixed steps, and the question what one step must do so that bodies fall, touch, stop and rest. The
naive answer: move each body by its velocity, then push overlaps apart; it jitters, gains energy and lets stacks sink. A
toy solver comes first (a sketch: one body on a floor, semi-implicit Euler and an impulse at the contact). Then the
ideas in teaching order. Rigid body state and integration: position, rotation as a quaternion, linear and angular
velocity, the velocity of a point of the body (v + ω × r, which impact sounds, pushes and contacts use), mass and the
inertia tensor, semi-implicit Euler, and forces against impulses against setting a velocity (in Strata a force acts
during the next fixed step only, an impulse at once; the mass is the component's, its distribution comes from the
shapes). Contacts as constraints: penetration, impulses that keep bodies apart, soft contacts with a stiffness in hertz
and a damping ratio, a capped push-out speed, friction, and restitution, which box3d applies only above 1 m/s (a pair's
friction and restitution combined by the mixing rule of `physics/bodies-colliders`). Sub-stepping: box3d's soft step
with 4 sub-steps per step, and why the contact stiffness has a ceiling of an eighth of the sub-step rate. Continuous
collision: tunnelling through thin walls, swept tests and the time of impact; box3d sweeps every dynamic body against
static ones, `ContinuousCollision` makes a bullet, and more collision steps per fixed step are the other remedy. Islands
and sleep: islands of touching bodies, the sleep threshold (Strata's 0.08 m/s) held for 0.5 s, waking, and why a pile's
time to sleep is chaotic. The approaches engines use (penalty forces, sequential impulses, position-based methods,
box3d's soft step) in a table with sources. Strata's choice: box3d's solver, tuned through the project's
`Physics.Simulation` section; what changed from Jolt (damping as `1 / (1 + d h)` per sub-step). How such defaults are
chosen, the concept of tuning by measurement: sweeps over representative scenes, and medians over many layouts because a
pile is chaotic (the steps are `physics/tuning`'s). Common mistakes: spawning bodies that overlap, `ContactHertz` above
30, `AddForce` once in `OnUpdate`, expecting slow bodies to bounce. At the end the reader can predict whether a body
tunnels, bounces or sleeps, and say what each field of `Physics.Simulation` changes in the solver.

**Leaves out.**

- How Strata maps components to box3d bodies → `physics/building-bodies`
- One step in Strata's code → `physics/world-step`
- Changing the solver's settings and measuring them → `physics/tuning`
- The fixed step and the accumulator → `core/time`
- Joints → `physics/why`

**Fit.** `fits`: about 5,400 words against L (5,000). Rigid body state and integration and contacts as soft constraints
take the most, then continuous collision and sleep; the toy solver and the sequence of pictures open the page.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `physics:225` | concept | home | Rigid body state and integration: semi-implicit Euler, mass and inertia, forces, impulses and velocities; the mistake of one `AddForce` in `OnUpdate` |
| `physics:248` | concept | home | Contacts as soft constraints: stiffness in hertz, damping ratio, push-out speed, sub-steps, friction and restitution; the stiffness ceiling explained |
| `physics:252` | concept | home | Continuous collision: tunnelling, swept tests, bullets, more collision steps as the alternative |
| `physics:255` | concept | home | Islands and sleep: the threshold, the 0.5 s, waking, the mistake of writing sleeping bodies' transforms without a signal |
| `physics:287` | concept | home | Tuning by measurement: why the solver's defaults are chosen by sweeps over representative scenes, and why a chaotic system (a pile that settles) is compared over many layouts by medians, not by one run; Strata's settle scenes and `Tools/PhysicsSweep.py` named, the steps on `physics/tuning` |
| `physics:49` | feature | home | Continuous collision in Strata: every dynamic body swept against static ones (`enableContinuous`), `ContinuousCollision` for bullets |
| `physics:377` | figure | home | Sequences of frames at exact fixed steps: the crate tower settling and the domino run; its ghost and goal frames are used by `physics/collision-layers` and `physics/contacts-triggers` |
| `physics:406` | rule | home | Do not spawn bodies overlapping: box3d pushes overlaps apart at up to 3 m/s |
| `physics:432` | rule | home | Damping differs from Jolt's formula |
| `physics:433` | rule | home | Restitution needs speed above 1 m/s: box3d's default `restitutionThreshold` (`Strata/vendor/box3d/src/types.c:18`), which Strata does not change (no `restitutionThreshold` in `Strata/src`) |
| `physics:497` | term | home | Term: sub-step |
| `physics:503-505` | term | home | Terms: contact constraint, soft contact, contact hertz, damping ratio, push speed |
| `physics:510` | term | home | Term: inertia tensor (and effective mass, which `physics/character-controllers` uses) |
| `physics:512-514` | term | home | Terms: continuous collision, CCD, bullet, tunnelling, island, sleep threshold |
| `new:13` | hands-on | home | Exercises (D27): the test `Bullets do not tunnel through thin kinematic walls` made one's own: a sphere of radius 0.1 m at 240 m/s fired at a wall 0.1 m thick that is static, then kinematic, then kinematic with `ContinuousCollision` on the sphere; for each, predict whether it stops in front of the wall, then run (done). A sphere of restitution 1 dropped on `CreateGround` from 2 cm and from 1 m (the ground's restitution 0 combines with 1 as the larger): the first meets the floor at about 0.63 m/s, below box3d's threshold of 1 m/s, and does not bounce; the second does (done). Evidence: `StrataTests/src/Physics/PhysicsSimulationTests.cpp:344-368`; `Strata/src/Strata/Physics/PhysicsWorld.cpp:2041-2042` (a bullet), `:4694` (`enableContinuous`); `Strata/vendor/box3d/src/types.c:18` (`restitutionThreshold`); `StrataTests/src/Physics/PhysicsTestUtils.h:71-75` (`CreateGround`) |
| `physics:93` | feature | use | Forces act during the next fixed step only, impulses at once: the rule as the solver sees it |
| `physics:148` | feature | use | The stiffness ceiling (30 Hz at 60 steps/s) as a consequence of sub-steps; the setting is `physics/tuning`'s |
| `physics:146` | feature | link | The `Physics.Simulation` section, named with each knob it explains |
| `physics:47` | feature | link | `ApplyMass`: the component's mass with the shapes' distribution |
| `new:27` | concept | use | The mixing rule of a pair's materials, named in one sentence where friction and restitution enter the contact |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Rates, accumulation, explicit and semi-implicit Euler steps; Newton's laws, momentum and impulse | `basics/math-change` | must |
| Quaternions, and angular velocity as an axis with a rate | `basics/math-rotations` | must |
| Matrices (the inertia tensor is a 3×3 matrix) | `basics/math-matrices` | must |
| Cross products: torque and the lever arm | `basics/math-vectors` | must |
| The fixed step and why it is fixed | `core/time` | must |
| Contacts, manifolds and the broad phase | `physics/collision-detection` | must |
| Body types, materials and mass | `physics/bodies-colliders` | must |
| Determinism as bit-identical results | `basics/numbers` | helps |
| Writing and running one doctest case | `core/first-change` | helps |

## `physics/building-bodies` — From entities to bodies: records, shapes, mesh colliders

**Covers.** The job: turn entities with a `RigidBody` and colliders into box3d bodies and shapes, and keep them in line
with every edit; the step itself is `physics/world-step`'s. The problem and how engines solve it is one paragraph that
links `physics/collision-detection` and `physics/dynamics`. The map: the layered overview (scene systems over scene
services over `PhysicsSystem`, `PhysicsWorld` and the box3d world; beside them `CharacterControllerSet`, the
`PhysicsMeshShapes` cache, `AssetMeshProvider` over the mesh geometry registry, `PhysicsTaskSystem` over the job
system); the "Physics" scene system (Play and Simulate, a soft order after Scripting, the stage `Scene.Physics`); the
world created only when the scene has physics components; box3d's limit of 128 worlds; `PhysicsRuntime`'s reference
count and its assert and log hooks; and the body records with their slots (the memory-layout figure). The contract: main
thread only; box3d IDs are never used without a validity check (shapes resolve through generation-checked slots);
kinematic bodies and the presence bodies of character controllers (the kinematic capsule each controller keeps so that
bodies land on it, `physics/character-controllers`) never recycle contacts. A toy version: a map from entity to body
rebuilt from its components. The real code in the order data flows: EnTT signals into change lists applied in rounds,
what each kind of change rebuilds, and what a rebuild keeps (a dynamic body keeps its motion, its touching pairs stay);
`FindBodyOwner`, the composition rule in code; `AddColliderParts`, which bakes scale into shapes (sphere radius by the
largest axis, capsule by the largest of X and Z, shear approximated, 1 mm minimum), shares box hulls and turns offset
triangle meshes into baked compounds; `MakeBodySetup`, which sanitizes the component's numbers, sets the material and
turns recycling off for kinematic bodies; `ApplyMass`. Mesh colliders: the non-blocking `PhysicsMeshProvider`, the
default `AssetMeshProvider` and the reader the renderer registers for it (every submesh's full-detail triangles, indexed
into the whole vertex list), so that physics reads a mesh without including the renderer; hulls and BVH meshes cooked on
jobs and cached (a hull reduced to 64 vertices, or 44, because box3d's 128 faces and edges hold no round hull of 128
vertices), the hold of the first steps (at most 10 s) until mesh floors exist, hot reload, a collider that keeps its
shape when residency unloads its mesh, and a skinned mesh's collider, which keeps its bind pose. Bodies out of the
simulation: pending bodies with their `BuildFailure`, suspended bodies with degenerate transforms, warnings once per
entity, and leaving the simulation (an inactive entity, or one pending destruction, stops colliding in that update; a
dynamic body keeps its velocities and resumes them when it comes back; its contacts end; parking is
`physics/scale-streaming`'s). Then the alternatives, how it is tested (`PhysicsTestUtils.h` and the hierarchy,
mesh-collider, lifecycle and scale suites) and changing it safely. At the end the reader can follow an entity to its
box3d body and shapes, and say why a body is pending or suspended.

**Leaves out.**

- The step: synchronization before it and write-back after it → `physics/world-step`
- Building bodies in slices and in parallel, capacities and growth → `physics/scale-streaming`
- Collision filters on the shapes → `physics/collision-layers`
- The character controllers' records → `physics/character-controllers`
- The mesh geometry registry on the asset side → `assets/models-gltf`
- Registering components with the engine → `world/reflection`

**Fit.** `fits`: about 6,450 words against L (5,000). Four excerpts with change tracking and what a rebuild keeps take
the most, then the map with its two diagrams and the mesh pipeline; with four exercises it stands 50 words under L's
top.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `physics:44-45` | feature | home | Shape building per collider (shared box hulls, values for spheres and capsules, transformed hulls, mesh shapes, baked compounds) and world scale baked into shapes |
| `physics:47` | feature | home | Mass: the shapes at density 1 give the distribution, scaled to the component's mass |
| `physics:52-54` | feature | home | Suspended bodies (degenerate transforms, zero-scaled parents), pending bodies and their `BuildFailure`, warnings once per entity and kind |
| `physics:60-64` | feature | home | Mesh colliders: the provider, `AssetMeshProvider`, cooking and its cache, the mesh wait at start, hot reload. Why hulls are reduced: box3d's hulls hold at most 128 vertices, faces and edges, and a hull of V vertices made of triangles has 2V - 4 faces and 3V - 6 edges, so a round mesh fails at 128 vertices; Strata cooks at most 64 vertices and, when box3d refuses that, 44, which any hull fits (about 80 words) |
| `render-core:112` | feature | home | The renderer's reader for the mesh geometry registry (`ReadMeshGeometry`, `Strata/src/Strata/Renderer/RendererRegistration.cpp:37-63`, registered at `:106`): a mesh's full-detail triangles for mesh colliders, so that physics never includes the renderer; the registry itself is the asset layer's seam |
| `physics:70-73` | feature | home | The "Physics" scene system, the lazy world, the 128-world limit, `PhysicsRuntime` |
| `physics:75` | feature | home | Change tracking through EnTT signals into change lists, applied in rounds before steps and queries, and what each kind of change rebuilds: a property edit rebuilds the body, a world scale change above 1e-4 (relative) rebuilds its shapes, moving or deactivating a merged collider changes its owner's shape, reparenting rebuilds only the bodies whose colliders change; what a rebuild keeps is `new:20` |
| `new:20` | feature | home | What a rebuild keeps (about 200 words, after change tracking): a dynamic body rebuilt because a property changed keeps moving as before, one that was out of the simulation resumes the motion it had, and its touching pairs stay, because contacts are tracked per pair of entities, so a rebuild sends neither End nor Begin. The joint exercise (`physics:468`) depends on this model. Evidence: `Strata/src/Strata/Physics/PhysicsWorld.cpp:2270-2287` (`GetBuildVelocities`), `:394`, `:51-55` with `:993-1000` (`HasScaleChanged`), `:2765-2769`; `StrataTests/src/Physics/PhysicsLifecycleTests.cpp:316`; `StrataTests/src/Physics/PhysicsHierarchyTests.cpp:151`, `:264`; `StrataTests/src/Physics/PhysicsBox3DBehaviorTests.cpp:297` |
| `new:21` | feature | home | A mesh collider keeps its shape when residency unloads its mesh: physics checks built colliders with `PeekMeshData`, which never loads a mesh again, and the bodies hold the cooked shape until they are rebuilt (one sentence in the mesh-collider section, about 50 words). Evidence: `Strata/src/Strata/Physics/PhysicsTypes.h:280-282`; `Strata/src/Strata/Physics/PhysicsMeshShapes.h:40-45`; `Strata/src/Strata/Physics/AssetMeshProvider.h:19-24`; `StrataTests/src/Physics/PhysicsBox3DBehaviorTests.cpp:594` |
| `physics:298` | code | home | `Strata/src/Strata/Physics/PhysicsWorld.cpp:212-226`: `FindBodyOwner`, the hierarchy rule for which entity owns a body |
| `physics:305` | code | home | `Strata/src/Strata/Physics/PhysicsWorld.cpp:1993-2049`: `MakeBodySetup`, component data to box3d definitions, sanitized; why kinematic bodies do not recycle |
| `physics:306` | code | home | `Strata/src/Strata/Physics/PhysicsWorld.cpp:2100-2112`: `ApplyMass`, mass against mass distribution, inertia scaled |
| `physics:307` | code | home | `Strata/src/Strata/Physics/PhysicsWorld.cpp:1857-1920`: `AddColliderParts`, the box, sphere and capsule parts; scale baked in, spheres by the largest axis |
| `physics:333` | figure | home | The layered overview: systems, services, `PhysicsSystem`, `PhysicsWorld`, box3d and the side boxes; who may include whom |
| `physics:359` | figure | home | Body record memory layout: records in a `std::map`, body, shape and record slots, constant-time lookups both ways |
| `physics:400` | rule | home | Main thread only: box3d's world is not thread-safe; physics parallelism is internal and deterministic |
| `physics:414` | rule | home | Kinematic and character presence bodies never recycle contacts (riders crept 0.70 m in 4 s) |
| `physics:434` | rule | home | Never use box3d IDs without validity checks; shapes resolve through generation-checked slots |
| `physics:462` | hands-on | home | Exercise: a doctest that drops a sphere and checks it rests at its radius (`PhysicsTestUtils.h`) |
| `physics:467-468` | hands-on | home | Exercises: a cylinder collider through a hull (gizmo, inspector, scale rule, tests); a hinge or distance joint as a component (lifetime, rebuild, serialization) |
| `new:14` | hands-on | home | Trace it yourself (D27): breakpoints in `FindBodyOwner` and `MakeBodySetup` while the hierarchy of `physics/bodies-colliders`' exercise (a rigid body with two child colliders, a child with its own rigid body, a lone collider) and a kinematic platform start playing: the entity each collider reports as its owner, and the branch that turns contact recycling off for the kinematic body. Evidence: `Strata/src/Strata/Physics/PhysicsWorld.cpp:212-226`, `:2032-2039` |
| `physics:527-528` | term | home | Terms: degenerate transform, suspended body |
| `physics:531-533` | term | home | Terms: body record, slot, cooking, mesh provider |
| `physics:35` | feature | use | The composition rule, now in code |
| `physics:42-43` | feature | link | How bodies follow moved entities, linked to `physics/world-step` |
| `physics:76` | feature | use | The general rule of leaving the simulation, beside suspended and pending bodies (about 120 words): an inactive entity, or one pending destruction, stops colliding in that update; a dynamic body keeps its velocities (`SaveVelocities`) and resumes them when it comes back, also after a rebuild; its contacts end. Parking, the rest of the item, is taught on `physics/scale-streaming` |
| `physics:80` | feature | link | Parallel creation of large rounds, linked to `physics/scale-streaming` |
| `physics:82` | feature | link | Sliced building for loaded scenes, linked to `physics/scale-streaming` |
| `animation:158` | feature | link | One sentence in the mesh-collider section: a skinned mesh's mesh collider keeps its bind pose (the pose is drawn, not collided), linked to `animation/skinning` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Scene systems, their order and scene services | `world/systems` | must |
| Change signals and the transform contract | `world/scene-graph` | must |
| The job system and deterministic parallel work | `core/jobs` | must |
| Asking for an asset without waiting for it | `assets/loading` | must |
| Decomposing a matrix into translation, rotation and scale | `basics/math-bases` | must |
| Body types, colliders and the composition rule | `physics/bodies-colliders` | must |
| Mass and the inertia tensor | `physics/dynamics` | must |
| Registries and the composition root | `core/layers-registries` | helps |
| Asserts, verifies and errors returned | `core/conventions` | helps |
| Ordered maps and stable references to their nodes | `basics/trees-graphs` | helps |
| The mesh geometry registry (physics reads a mesh's triangles without the renderer) | `assets/models-gltf` | helps |
| Writing and running one doctest case | `core/first-change` | helps |
| A character controller's presence body (glossed in one clause with a link forward) | `physics/character-controllers` | helps |
| Running a debugger on a test or the editor | `core/debugging` | helps |

## `physics/world-step` — Inside `PhysicsWorld`: one step

**Covers.** The job: run one fixed step of a world and bring its results back to the scene. `world/systems`' frame
timeline, with the physics overlay, places the work (changes applied in `OnUpdate`, zero or more steps in
`OnFixedUpdate`, events dispatched after each). The problem section is one paragraph that links `physics/dynamics`. The
map: the flow chart inside a fixed step (`ApplyChanges`, growth, parked disables, the mesh hold, sync, the characters'
step, `CollisionSteps` box3d steps of 4 sub-steps with forces applied again before each and events read after each,
write-back, pair upkeep, instruments) and "two copies of the truth" (entity transforms and body poses, who writes which
and when). The idea that every engine with a physics library faces, synchronizing physics and the scene graph, is taught
here: before the step entity to body (only what was signalled or is awake), after it body to entity (only what moved,
parents first). The contract: signal transform writes, because sleeping and static bodies are never polled; `Teleport`
for instant moves; forces in `OnFixedUpdate`, every step they should act. A toy version: a step loop with sync, step and
write-back. The real code in data-flow order: `PhysicsSystem::OnUpdate` and `OnFixedUpdate`; `Simulate`; `SyncBody`
(kinematic bodies reach their target in one step and stop there, dynamic bodies moved from outside are teleported
keeping their velocity, a moved static body wakes what rests on it); the write-back: `MarkMoved`'s bitmap and the
ordered list it gives, so that ordering costs what moved; `WritePose` relative to the parent with the authored scale
kept, in parallel chunks with parents first, and `MarkTransformsChanged` without `on_update`; forces queued and impulses
at once; `Teleport` (body and entity at once, neighbours woken, interpolation broken); gravity from the scene's
settings; `PhysicsTaskSystem`, where the waiting thread runs a task no worker has started. Determinism as the second
idea: the same results with any number of threads (ordered records, fixed chunks, integer settling sums), checked by
twin runs and box3d's golden hash. Last, the script face of bodies: the map of the SDK's physics classes (`RigidBody`,
`Physics`, `RaycastHit`, `Collision`, `CharacterController`, `GroundState`), then velocities, forces, impulses, torque
and `Teleport` from a script, through the host functions and the SDK's `RigidBody` and `Physics` (queries, contacts,
characters and layers show their own functions on their pages); what a script cannot call (`IsSleeping`, `WakeUp`,
`SetGravityScale` and a point's velocity, which the services have and the SDK does not) and what a change of the
RigidBody component's properties through `Entity::SetProperty` costs: a rebuild of the body. Then the alternatives, how
it is tested and changing it safely. Exercises: trace one step in Tracy and give its time to sync, library and
write-back; run a pile with 0 and 3 workers and compare the poses.

**Leaves out.**

- The contact events read after each box3d step → `physics/contacts-triggers`
- The characters' step → `physics/character-controllers`
- Growth and parked disables inside the step → `physics/scale-streaming`
- The scene's fixed-step loop and drawn transforms → `world/systems`, `world/interpolation`
- How the host API works → `scripting/host-api`
- Every script function → `reference/script-api`

**Fit.** `over`: about 6,950 words against L (5,000). Seven excerpts with the write-back, two ideas from zero, four
diagrams and the script face with its map of the SDK's classes pass L's top; XL (8,000) by S2.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `physics:42-43` | feature | home | Kinematic bodies follow their entity by a target velocity reached in one step; dynamic bodies moved from outside are teleported; moved static bodies wake what rests on them |
| `physics:74` | feature | home | `PhysicsTaskSystem`: box3d's step tasks on the job system |
| `physics:89-95` | feature | home | `OnFixedUpdate`, `Simulate`, synchronization before the step, write-back after it, forces and impulses, `Teleport`, gravity |
| `physics:149` | feature | home | Determinism with any number of threads, and its tests |
| `physics:177` | feature | home | The script face of physics: the host functions of bodies, queries, characters, layers and drawn transforms, the SDK's `RigidBody` and `Physics`; bodies are taught here, the rest on their pages |
| `scripting:125` | feature | home | The SDK's `RigidBody`, `Physics`, `RaycastHit` and `Collision`, one entry with their twin `physics:177`: the classes a script holds, named as one map; the bodies' functions are shown here, `Physics`' queries and `RaycastHit` on `physics/queries`, `Collision` on `physics/contacts-triggers` |
| `scripting:126` | feature | home | The SDK's `CharacterController` and `GroundState`, one entry with their twin `physics:177`: named in the same map; their functions are shown on `physics/character-controllers` |
| `new:29` | feature | home | In the script face of bodies (about 60 words): the SDK's `RigidBody` has no `IsSleeping`, `WakeUp`, `SetGravityScale` or point velocity, although the services have them; a script changes body settings (type, mass, friction, layer) through the RigidBody component's properties (`Entity::SetProperty`), and each such change rebuilds the body. Evidence: `StrataScriptCore/Include/StrataScript/Physics.h:38-43`; `StrataScriptCore/Include/StrataScript/ScriptABI.h:400-419`; `Strata/src/Strata/Scene/SceneServices.h:113-157`; `git grep -n -e IsSleeping -e WakeUp -e SetGravityScale -e PointVelocity 822a7a46 -- StrataScriptCore` finds nothing (run at the pin); `StrataTests/src/Physics/PhysicsLifecycleTests.cpp:316` (a property edit rebuilds the body) |
| `physics:267` | concept | home | Synchronizing physics and the scene graph: two copies of the truth, who writes when, signals, parents first, only what is awake costs |
| `physics:279` | concept | home | Determinism: same input, same output, with threads; what box3d's cross-platform claim covers and what Strata checks |
| `physics:300` | code | home | `Strata/src/Strata/Physics/PhysicsSystem.cpp:158-177`: what one frame and one fixed step of the physics system do |
| `physics:301` | code | home | `Strata/src/Strata/Physics/PhysicsWorld.cpp:4973-5078`: `Simulate`, the anatomy of a step (long: walked in parts) |
| `physics:302` | code | home | `Strata/src/Strata/Physics/PhysicsWorld.cpp:3300-3421`: `SyncBody`, static against kinematic against dynamic, wake rules, degenerate transforms |
| `physics:303` | code | home | `Strata/src/Strata/Physics/PhysicsWorld.cpp:4144-4179`: `WritePose`, the pose written relative to the parent, scale kept |
| `physics:304` | code | home | `Strata/src/Strata/Physics/PhysicsWorld.cpp:3627-3637`: `MarkMoved`, with the list it gives at `PhysicsWorld.cpp:4208-4229`; a bitmap whose ordering costs what moved |
| `physics:319` | code | home | `Strata/src/Strata/Physics/PhysicsTaskSystem.cpp:14-49`: a library's task callbacks on an engine's job system; the waiting thread runs the task |
| `physics:323` | code | home | `StrataTests/src/Physics/PhysicsSimulationTests.cpp:821-839`: twin runs, with and without three workers, must be identical |
| `physics:338` | figure | home | The physics overlay of `world/systems`' frame timeline (one figure, no timeline of its own, R31): its three marks, where physics applies changes, steps and dispatches; captured once with that figure from `world/systems`' recipe |
| `scene-ecs:433` | figure | use | `world/systems`' frame timeline (`OnUpdate` of every system, 0 to N fixed steps with the accumulator, `OnLateUpdate`, render), shown again here with the physics overlay |
| `physics:340` | figure | home | Inside a fixed step: the flow chart of `Simulate` |
| `physics:343` | figure | home | Two copies of the truth, with `MarkModified` and `MarkTransformsChanged` |
| `physics:361` | figure | home | Parallel write-back: the main thread lists, jobs write in chunks, the main thread finishes |
| `physics:389` | rule | home | Signal transform writes: sleeping and static bodies are never polled |
| `physics:392` | rule | home | Use `Teleport` for instant moves: a transform write moves the body only at the next step |
| `physics:394` | rule | home | Apply forces in `OnFixedUpdate`, every step they should act |
| `physics:464` | hands-on | home | Exercise (trace it yourself): one fixed step in Tracy, its time split into sync, library and write-back |
| `physics:469` | hands-on | home | Exercise: a pile with 0 and 3 workers, poses compared |
| `physics:498` | term | home | Term: collision step |
| `physics:524-525` | term | home | Terms: write-back, synchronization |
| `physics:539` | term | home | Term: golden hash |
| `physics:311` | code | link | `ProcessStepEvents`, named where `Simulate` reads each box3d step's events; walked on `physics/contacts-triggers` |
| `physics:137` | feature | link | The characters' step inside `Simulate` |
| `scene-ecs:107` | feature | use | The scene's fixed-step loop that calls `OnFixedUpdate` |
| `scene-ecs:80` | feature | use | `MarkTransformsChanged`: dirty without `on_update`, so physics does not hear its own write-back |
| `scene-ecs:137` | feature | use | Breaking interpolation on a teleport |
| `build-test:99` | feature | use | box3d's determinism scenario, the golden hash's source |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The fixed step, the accumulator and time dilation | `core/time` | must |
| The scene's fixed-step loop in code | `world/systems` | must |
| Drawn transforms and breaking interpolation | `world/interpolation` | must |
| Change signals, `MarkTransformChanged` and the transform contract | `world/scene-graph` | must |
| The job system, ordered records and fixed chunks | `core/jobs` | must |
| Bits, masks and counting trailing zeros | `basics/numbers` | must |
| Records, slots and how bodies are built | `physics/building-bodies` | must |
| Integration, contacts and sleep | `physics/dynamics` | must |
| Tracy and profile scopes | `core/profiling` | helps |
| The host API behind the script SDK | `scripting/host-api` | helps |
| Writing and running one doctest case | `core/first-change` | helps |

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

## `physics/contacts-triggers` — Contacts and triggers

**Covers.** The job: tell game code when two entities start and stop touching, and when something enters or leaves a
trigger. The problem and how engines solve it, taught here in full: triggers as sensors (overlap without a response,
events only, what a sensor can see) and contact events (Begin and End per pair, why a library's per-shape events are
folded per entity, why events are delivered after the step and never from inside the solver, why every Begin has exactly
one End, what tracking costs), on the Playground's goal basket that counts balls and its impact sounds. The map: box3d's
contact and sensor events, `ProcessStepEvents`, the touching pairs, `CollisionEvent`s, the dispatch on the main thread
and the listeners, among them the script system's. The contract: events come after the step, on the main thread, and
listeners may destroy entities or call the physics API. A toy version: counting contacts per entity pair. The real code:
`TouchingPair` with `CountBegin` and `CountEnd` (a pair begins with its first contact and ends with its last; a rebuilt
body marks its pairs Unconfirmed instead of an End and a Begin; constant-time removal); reading box3d's event buffers in
`ProcessStepEvents` (static-static sensor pairs dropped, nothing tracked that nobody wants); contact interest and
watches (nobody listening costs nothing); the contact point midway between the surfaces and the trigger point at the
centre of the boxes' overlap; `ICollisionEventSource` with its two scopes; `DispatchCollisionEvents` over a snapshot of
the listeners; and the scripts' side, `OnCollisionEnter`, `OnCollisionExit`, `OnTriggerEnter` and `OnTriggerExit` with
the SDK's `Collision`, in the Playground's `GoalBasket` and `LaunchPad`. What Strata does not do: triggers that see
triangle-mesh colliders; stay events, and the impulse or impact speed of a contact (a script reads the bodies'
velocities, as `Impact.cpp` does). The pair-folding figure (a small state machine), then the alternatives, how it is
tested and changing it safely. At the end the reader can write a trigger script and explain why its Enter and Exit
always come in pairs.

**Leaves out.**

- How the script system calls a script's callbacks → `scripting/script-system`
- The contacts of character controllers → `physics/character-controllers`
- Impact sounds that are louder for harder hits → `make/sound`
- Triggers in a game, for game makers → `make/physics`

**Fit.** `fits`: about 5,100 words against L (5,000). The problem section taught in full (sensors and per-entity
contact events) and four excerpts, from the pair folding to the Playground's trigger scripts, take the most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `physics:50` | feature | home | Triggers are box3d sensors: they see convex shapes and characters, never triangle meshes; static-static sensor pairs are dropped |
| `physics:101-108` | feature | home | `CollisionEvent`; `ICollisionEventSource`; pair folding; contact interest; contact and trigger points; dispatch after the step; the scripts' callbacks; constant-time pair upkeep |
| `physics:261-263` | concept | home | Triggers (sensors) and contact events |
| `physics:310` | code | home | `Strata/src/Strata/Physics/PhysicsWorld.cpp:3598-3625`: `CountBegin` and `CountEnd`, with `TouchingPair` at `PhysicsWorld.cpp:422-443`; per-shape contacts folded into per-entity Begin and End |
| `physics:311` | code | home | `Strata/src/Strata/Physics/PhysicsWorld.cpp:3643-3710`: `ProcessStepEvents`, reading a library's event buffers and skipping work nobody wants |
| `physics:312` | code | home | `Strata/src/Strata/Physics/PhysicsSystem.cpp:636-660`: `DispatchCollisionEvents`, a snapshot of the listeners, removed listeners, re-entrancy |
| `physics:324` | code | home | `Samples/PhysicsPlayground/Scripts/GoalBasket.cpp:1-26`, with `Samples/PhysicsPlayground/Scripts/LaunchPad.cpp:1-22`: triggers in game code, the smallest useful scripts |
| `physics:345` | figure | home | Contact pair folding: shape contacts feeding one touching pair, Begin at the first, End at the last, Unconfirmed on rebuild |
| `physics:402` | rule | home | Events are delivered after the step, not from inside it |
| `physics:485` | term | home | Terms: trigger, sensor |
| `scripting:618` | term | home | Term: trigger, as the scripting inventory defines it (the same entry as `physics:485`) |
| `physics:521-523` | term | home | Terms: collision event, touching pair, contact interest, watch |
| `new:16` | hands-on | home | Exercises (D27): breakpoints in `CountBegin` and `CountEnd` while a body of two box colliders lands on the ground: two shape contacts, one touching pair, one Begin (trace). A doctest with `Tests::CollisionRecorder`: a ball dropped through a static trigger counts one Begin and one End, and a second ball destroyed while it is inside the trigger still ends its pair, so every Begin has its End (done). Evidence: `Strata/src/Strata/Physics/PhysicsWorld.cpp:3598-3625`; `StrataTests/src/Physics/PhysicsBox3DBehaviorTests.cpp:275`; `StrataTests/src/Physics/PhysicsTestUtils.h:95-112`; `StrataTests/src/Physics/PhysicsEventTests.cpp:14`, `:104`; `Strata/src/Strata/Scene/SceneServices.h:47-48` |
| `new:4` | not-done | home | Triggers that see triangle-mesh colliders (box3d's sensors test convex shapes only); the Roadmap lists them. Evidence: `Docs/Releases/0.7.0.md:399`; `Docs/Roadmap.md:1719-1720` |
| `new:9` | not-done | home | Stay events, and the impulse or impact speed of a contact: events are only Begin and End, so scripts get Enter and Exit and no "stay" callback, and a contact carries the other entity, a point and a normal but no impulse, because box3d's hit events are not used; game code that needs a hit's strength reads the bodies' velocities, as the Playground's `Impact.cpp` does (about 80 words; a reader who knows Unity expects `OnCollisionStay` and the contact's impulse). Evidence: `Strata/src/Strata/Scene/SceneServices.h:41-45`; `StrataScriptCore/Include/StrataScript/Script.h:89-92`; `StrataScriptCore/Include/StrataScript/ScriptABI.h:181-188`; `git grep -n enableHitEvents 822a7a46 -- Strata/src` finds nothing (run at the pin); `Samples/PhysicsPlayground/Scripts/Impact.cpp:53-55` |
| `physics:139` | feature | link | Character contacts that join entity pairs, and triggers that reach the presence body |
| `physics:377` | figure | use | The frames of the balls counted by the goal |
| `scripting:382` | code | link | The script system's contact delivery, walked on `scripting/script-system` |
| `scripting:125` | feature | use | The SDK's `Collision`, which the four contact callbacks receive (the other entity, the point, the normal) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| One step: sync, box3d steps and write-back | `physics/world-step` | must |
| Collision layers and filters | `physics/collision-layers` | must |
| Callbacks stored as `std::function` | `basics/cpp-generic` | must |
| A script class and `override` | `basics/programming-3` | must |
| Scene services | `world/systems` | must |
| Hash maps, and removing from an array by swapping with the last element | `basics/data-structures` | must |
| UUIDs as the identities of entities | `world/ecs` | helps |
| How the script system delivers callbacks | `scripting/script-system` | helps |
| Writing and running one doctest case | `core/first-change` | helps |
| Running a debugger on a test or the editor | `core/debugging` | helps |

## `physics/queries` — Physics queries

**Covers.** The job: answer questions about space without moving anything. The problem and how engines solve it,
taught here in full: raycasts (the closest hit or all hits), overlaps, shape casts; layer masks, ignoring oneself,
triggers or not, a ray that starts inside a shape; and the question of when a query sees the world (Strata's: as of the
last step or change, with pending changes applied first). The example is the Playground: shooting a ball through the
cursor and the grab tool. The map: the SDK's `Physics::Raycast`, its host function, `IPhysicsQueries`, `PhysicsSystem`
and `PhysicsWorld`, down to box3d's ray cast and overlap tests. The contract: results in a deterministic order, the
world as of the last step, distances clamped to 1e5 m. A toy version: a ray against a list of spheres. The real code:
`RayCallback` and `Raycast` (a callback that clips the ray to closer hits, so the closest wins; rays that start inside a
convex collider do not hit it); `RaycastAll`, the closest hit per entity sorted by distance; `CollectOverlaps`, results
sorted by body index; the grab tool (`UpdateGrab`: a raycast picks a body, a capped velocity pulls it). What Strata
does not do: shape sweeps in the API (box3d's mover cast is used only inside the character controller). Then the
alternatives, how it is tested, and changing it safely: adding a query end to end, with the host function appended at
the end and the feature test extended (the exercises `OverlapCapsule` and `SphereCast`). At the end the reader can
choose the query for a gameplay question and say what it returns and in which order.

**Leaves out.**

- A camera's ray through the cursor → `make/gameplay-math`, `core/math`
- The ground probes inside the character controller → `physics/character-controllers`
- Adding a host function, step by step → `scripting/tutorial-host-function`
- Picking in the editor's Scene view → `editor-ui/scene-view`

**Fit.** `over`: about 4,200 words against M (3,000). The problem section taught in full, three excerpts with the grab
tool and three exercises (two of them extend the API) pass M's top; L (5,000) by S2.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `physics:114-116` | feature | home | `Raycast`, `RaycastAll`, `OverlapSphere`, `OverlapBox` with masks, ignored entity and triggers; the world as of the last step; no shape casts in the public API |
| `physics:265` | concept | home | Spatial queries: closest and all, overlaps, shape casts, masks, ignoring self, triggers, starting inside a shape |
| `physics:313` | code | home | `Strata/src/Strata/Physics/PhysicsWorld.cpp:4499-4519`: `RayCallback`, with `Raycast` at `PhysicsWorld.cpp:5399-5417`; clipping the ray to closer hits, the inside-convex rule |
| `physics:314` | code | home | `Strata/src/Strata/Physics/PhysicsWorld.cpp:4535-4571`: `CollectOverlaps`, results made deterministic by body index |
| `physics:325` | code | home | `Samples/PhysicsPlayground/Scripts/Playground.cpp:223-255`: `UpdateGrab`, raycast picking and grabbing by velocity |
| `physics:465-466` | hands-on | home | Exercises: an `OverlapCapsule` query through every layer (world, system, service, host function at the end, SDK, test, feature script); a `SphereCast` with sorted hits and the same filters |
| `new:17` | hands-on | home | Trace it yourself (D27): a breakpoint in `RayCallback` while a ray is cast through three boxes in a row (a copy of the test `Raycast reports the closest hit`): `Raycast`'s callback returns the hit's fraction, which clips the ray, so later calls come only for closer hits; `RaycastAll`'s returns 1 and never clips; a ray that starts inside a box passes out of it without a hit. Evidence: `Strata/src/Strata/Physics/PhysicsWorld.cpp:4499-4519`, `:5399-5417`; `StrataTests/src/Physics/PhysicsQueryTests.cpp:13` |
| `physics:520` | term | home | Terms: raycast, `RaycastAll`, overlap, shape cast, sweep |
| `editor-core:725` | term | home | Term: raycast, as the editor inventory defines it (finding what a ray from the camera hits), one entry with `physics:520`; `editor/placement` teaches the editor's own ray against the scene under its own name and links this entry |
| `new:5` | not-done | home | Shape sweeps in the API: queries cast rays, and a sweep is used only inside the character controller. Evidence: `git grep -n "b3World_Cast" 822a7a46 -- Strata/src` finds `b3World_CastRay` (`Strata/src/Strata/Physics/PhysicsWorld.cpp:5413, 5435`; the controller's ground ray, `Strata/src/Strata/Physics/CharacterControllers.cpp:436`) and `b3World_CastMover` only at `CharacterControllers.cpp:373` |
| `physics:177`, `scripting:125` | feature | use | The query host functions, the SDK's `Physics` queries and `RaycastHit` |
| `physics:124` | feature | use | The query category bit that lets a query see every layer |
| `scripting:73` | feature | link | The query functions of the C ABI |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Rays and ray-shape intersection | `basics/math-geometry` | must |
| The broad phase's trees | `physics/collision-detection` | must |
| Layer masks and the query category bit | `physics/collision-layers` | must |
| `std::optional` | `basics/cpp-modern` | must |
| `std::vector` and sorting a list | `basics/cpp-generic` | must |
| A camera's ray from the cursor (`Ray::FromNDC`) | `core/math` | helps |
| Determinism as bit-identical results | `basics/numbers` | helps |
| Appending a host function | `scripting/host-api` | helps |
| The feature test | `engineering/feature-test` | helps |
| Running a debugger on a test or the editor | `core/debugging` | helps |

## `physics/character-controllers` — Character controllers

**Covers.** The job: walk an upright capsule that game code steers, through a world of bodies. The problem and how
engines solve it, taught here in full: why a player is not a dynamic capsule (it tips over, bounces and slides down
slopes), the kinematic answer of collide and slide with a plane solver, and what a walker needs beyond it (steps,
slopes, ground snapping, moving platforms, pushing what it walks into, being landed on), with the approaches engines use
and their costs. The example is a scene built for the page, which is also the figure's source: a 0.3 m and a 0.5 m step,
a 40° and a 50° slope, as `Physics.Character`'s tests build them (the Third-Person sample has one slope and no stairs).
The map: the scene service `ICharacterControl` (move, jump, teleport, root motion, state), `CharacterControllerSet` and
box3d's mover queries (`b3World_CollideMover`, `b3SolvePlanes`, `b3World_CastMover`), and the presence body. The
contract: the entity's rotation and scale do not change the capsule; an entity with both a `RigidBody` and a controller
is simulated as the rigid body; what others ride moves in `OnFixedUpdate` or as a kinematic body, so that carrier and
rider share the clock; presence bodies never recycle contacts; an entity moved from outside (a script writing its
transform, the editor) teleports its controller there at the next step; controllers collide with other controllers'
presence bodies, so characters block each other; a controller never collides with its own entity's bodies or with
triggers, which reach it through its presence body. A toy version: collide and slide of a circle against lines in two
dimensions. The real code: the component's knobs and units; `ShapePlanes` and `SlideMove` (steep slopes become walls);
`MoveController`, the whole move (gravity, the jump, the carried velocity of a platform and leaving it with its motion,
the pass across, the step up, the vertical pass, snapping down, the ground state); `PushBodies` (an inelastic impulse
with the effective mass at the contact point, capped by `PushStrength` times the step, never downward, and a 70 kg
weight on dynamic ground); the presence body, a kinematic capsule at 90 % of the radius that bodies land on, triggers
see and rays hit; the characters' contacts joining the entity pairs; `CharacterControllerSet::Step`, moves in parallel
that read only, then writes in controller order. The root-motion hook (`AddCharacterMotion`) is named and linked
forward. Four figures: the character move with its ground states, the presence body, the push impulse, and the picture
of stairs and slopes. Then the alternatives, how it is tested and changing it safely. At the end the reader can predict
what a controller does at a 0.3 m step and a 0.5 m step, on a 40° and a 50° slope, and on a turning platform.

**Leaves out.**

- Root motion from animation clips → `animation/root-motion`
- Making a player character and a follow camera in a game → `make/characters-cameras`
- Drawn transforms for the camera that follows a character → `world/interpolation`
- The input actions a player script reads → `input/actions`

**Fit.** `fits`: about 5,950 words against L (5,000). Five excerpts, with `MoveController` walked in parts, and the full
problem section take the most, then the four figures.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `physics:33` | feature | home | `CharacterControllerComponent`: height, radius, step height, slope limit, layer, gravity scale, push strength, enabled |
| `physics:132-139` | feature | home | `CharacterControllerSet` on box3d's mover; the two-pass move, step-up, snapping, slope limit and ground state; platforms; the presence body; pushing; parallel moves and serial writes; `ICharacterControl`; character contacts and triggers |
| `physics:271` | concept | home | Character controllers: why kinematic, collide and slide, steps, slopes, snapping, platforms, pushing, being landed on; the mistakes of a rotated controller and of a vertical walk velocity with gravity on |
| `physics:297` | code | home | `Strata/src/Strata/Physics/PhysicsComponents.h:70-85`: the controller's knobs and their units |
| `physics:315` | code | home | `Strata/src/Strata/Physics/CharacterControllers.cpp:384-422`: `ShapePlanes` and `SlideMove`, collide and slide with a plane solver, steep slopes as walls |
| `physics:316` | code | home | `Strata/src/Strata/Physics/CharacterControllers.cpp:557-664`: `MoveController`, the complete move (long: walked in parts) |
| `physics:317` | code | home | `Strata/src/Strata/Physics/CharacterControllers.cpp:680-716`: `PushBodies`' push, the effective mass at a contact point, an inelastic push, the force cap |
| `physics:318` | code | home | `Strata/src/Strata/Physics/CharacterControllers.cpp:928-999`: `CharacterControllerSet::Step`, read-only moves in parallel, then writes in order |
| `physics:349-353` | figure | home | The character move (across pass with planes, step up, vertical pass, snap; the ground states as a state diagram); the presence body and who meets which capsule; the push impulse with its effective-mass formula |
| `physics:382` | figure | home | A controller on stairs and slopes: up a 0.3 m step, stopped by a 0.5 m one; standing on 40°, sliding on 50°; captured from a scene built for it, because the Third-Person sample has one slope and no stairs (`Samples/ThirdPerson/Assets/Scenes/Course.stscene` holds one entity named "Slope" and none of stairs; `Samples/ThirdPerson/README.md:15-20`) |
| `physics:425` | rule | home | Move what others ride in `OnFixedUpdate` or as a kinematic body |
| `physics:429-431` | rule | home | A controller's rotation and scale do not change its capsule; an entity with both a `RigidBody` and a controller is the rigid body |
| `new:23` | feature | home | An entity moved from outside (a script writing its transform, the editor) teleports its controller there at the next step: a world position that differs from where the controller put it by more than 1e-4 of its magnitude (at least 1e-4 m) counts as such a move (in the contract, about 40 words). Evidence: `Strata/src/Strata/Physics/CharacterControllers.h:75-76`; `Strata/src/Strata/Physics/CharacterControllers.cpp:42-44` (`c_ExternalMoveTolerance`), `:75`; `Docs/Architecture.md:480-481` |
| `new:24` | feature | home | Controllers collide with other controllers' presence bodies, so characters block each other (in the map, beside the presence body, about 40 words). Evidence: `Strata/src/Strata/Physics/CharacterControllers.h:63-65` |
| `new:25` | feature | home | A controller never collides with its own entity's bodies or with triggers; triggers reach it through its presence body (`OnTriggerEnter` and `OnTriggerExit`), about 40 words. Evidence: `Strata/src/Strata/Physics/CharacterControllers.h:63-65`; `Docs/Architecture.md:482-484`; `StrataTests/src/Physics/PhysicsCharacterTests.cpp:400` |
| `physics:486-492` | term | home | Terms: presence body, character controller, mover, collide and slide, step height, step up, ground snapping, ground state |
| `new:18` | hands-on | home | Exercises (D27): the figure's scene built in a doctest the way `Physics.Character`'s step and slope tests build theirs (a 0.3 m and a 0.5 m step, a 40° and a 50° ramp): with the default `StepHeight` of 0.35 m and `MaxSlopeDegrees` of 45°, predict what the controller does at each, then run and read its height and ground state (done). Breakpoints in `PushBodies` while a controller walks into a crate: the effective mass at the contact point, and the cap of `PushStrength` times the step (trace). Evidence: `StrataTests/src/Physics/PhysicsCharacterTests.cpp:104`, `:127`, `:287`; `Strata/src/Strata/Physics/PhysicsComponents.h:79-80`; `Strata/src/Strata/Physics/CharacterControllers.cpp:680-716` |
| `physics:414` | rule | use | Presence bodies never recycle contacts |
| `physics:371` | figure | use | The Inspector of a Character Controller |
| `physics:177`, `scripting:126` | feature | use | The character host functions and the SDK's `CharacterController` and `GroundState` |
| `animation:111` | feature | link | Root motion through a character controller, linked forward to `animation/root-motion` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Projecting a vector onto a plane; dot and cross products | `basics/math-vectors` | must |
| Planes and their normals | `basics/math-geometry` | must |
| Kinematic bodies | `physics/bodies-colliders` | must |
| Impulses and the effective mass at a point | `physics/dynamics` | must |
| One step and the write-back | `physics/world-step` | must |
| Queries and casts against the world | `physics/queries` | must |
| The job system and serial publishing | `core/jobs` | must |
| Drawn transforms of moving entities | `world/interpolation` | must |
| Root motion | `animation/root-motion` | helps |
| Writing and running one doctest case | `core/first-change` | helps |
| Running a debugger on a test or the editor | `core/debugging` | helps |

## `physics/scale-streaming` — Physics at scale and in streaming worlds

**Covers.** The job: keep physics fast and never unsafe when bodies number in the hundreds of thousands and arrive or
leave with streamed parts of a world. The problem and how engines solve it, taught here in full: capacities and memory
(pools sized in advance against growth, reserving ahead of what streams in, a growth limit as a cap on memory) and
bodies in a streaming world (building them in slices while a scene loads, creating many in parallel, and spreading the
cost of removal). The map: `IPhysicsCapacity` and `Reserve` (which the world streamer calls for cells about to load),
the loaded scene's prepared world, growth inside the step, parked bodies. The contract: never let a body sit without
collision below the growth limit (box3d grows in place; only at the limit do bodies wait, in order, in a queue that no
step polls); stay within 20 km of the origin, because box3d refuses coordinates beyond 1e5 m. A toy version: a pool that
doubles up to a cap, with a queue of waiters. The real code: `ResolveCapacities` and `GrowRoom` (automatic room at the
next power of two of twice the bodies, at least 1,024; two contacts a body; the reserve at creation capped; growth that
doubles up to the limit; the demand remembered for the scene's next world), and beside them a scene's own capacity,
`SceneSettings::PhysicsCapacity` (`MaxBodies` and `MaxContactConstraints`, 0 for automatic, at most 2^21 and 2^19, set
with `scene.setSettings {physicsCapacity}`, winning over the defaults; `maxBodyPairs` ignored since 0.5.0);
`EstimateReservedBytes`, fitted to box3d's own counts; parallel creation for rounds of 256 bodies or more with IDs that
do not depend on the threads; static shapes made before the first step that skip the pair search; sliced building for
loaded scenes (8,192 owners a slice, adopted when the scene starts); parking (`ParkStaticBody`, `DisableParkedBodies`:
an empty filter at once, `b3Body_Disable` 60 steps later, at most 1,024 a step); bodies beyond 1e5 m that wait like
degenerate ones. The figures of capacity growth and of the parking timeline. What Strata does not do: bodies farther
than 1e5 m. Then the alternatives, how it is tested (the capacity and prepare suites, and the perf tests that create
100,000 static bodies and grow to 65,536) and changing it safely. At the end the reader can size a world for a streamed
level and explain why removing a cell's bodies is spread over steps.

**Leaves out.**

- What a world reserves through the streamer, the cook's `MaxBodiesInRadius`, prefetch before a teleport →
  `worlds/physics-scripts`
- Loading scenes in slices in general → `world/sub-scenes`
- Why worlds stay within 20 km → `worlds/why-streaming`
- Measuring the cost of creation with the perf tests → `physics/tuning`

**Fit.** `over`: about 4,800 words against M (3,000). Two ideas from zero, two excerpts with the scene's own capacity,
eight features and two figures pass M's top; L (5,000) by S2.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `physics:51` | feature | home | The coordinate limit of 1e5 m: bodies beyond it wait like degenerate transforms |
| `physics:76-82` | feature | home | Parking, the bulk of `physics:76` (static bodies without contacts get an empty filter at once and are disabled 60 steps later, 1,024 a step; the general rule of leaving the simulation is used on `physics/building-bodies`); capacities and growth; `EstimateReservedBytes`; `IPhysicsCapacity` and `Reserve`; parallel creation; static shapes that skip the pair search; sliced building |
| `physics:283-285` | concept | home | Scale and memory: capacities and growth; bodies in a streaming world |
| `new:26` | feature | home | A scene's own physics capacity, one paragraph beside `ResolveCapacities` (about 100 words): `SceneSettings::PhysicsCapacity` (`PhysicsCapacitySettings`) with `MaxBodies` and `MaxContactConstraints`; 0 means automatic; the limits are 2^21 and 2^19; `scene.setSettings {physicsCapacity}` sets them, and they win over the defaults; `maxBodyPairs` has been read and ignored since 0.5.0, with a warning. Evidence: `Strata/src/Strata/Scene/Scene.h:42-59`, `:66`; `Strata/src/Strata/Physics/PhysicsSystem.cpp:528-537`; `StrataEditor/src/Editor/EditorSceneCommands.cpp:62-92`, `:587` |
| `physics:320` | code | home | `Strata/src/Strata/Physics/PhysicsWorld.cpp:1530-1582`: `ParkStaticBody` and `DisableParkedBodies`, an expensive removal spread across steps |
| `physics:321` | code | home | `Strata/src/Strata/Physics/PhysicsWorld.cpp:4775-4787`: `ResolveCapacities`, with `GrowRoom` at `PhysicsWorld.cpp:2300-2316`; sizing pools, growing by doubling, remembering demand |
| `physics:356-358` | figure | home | Capacity growth (room over time, the growth limit, the waiters, demand for the next play); the parking timeline (filters emptied at step S, disables in slices from S + 60) |
| `physics:416-417` | rule | home | Stay within 20 km (box3d refuses 1e5 m); never let a body sit without collision below the growth limit |
| `worlds-runtime:427` | rule | home | The same rule as the worlds inventory states it: no body without collision below the growth limit, and bodies at the limit wait in a queue that no step polls; reserving from the cook's counts is `worlds/physics-scripts`' |
| `physics:529-530` | term | home | Terms: parked body, capacity, room, growth limit, demand |
| `worlds-runtime:538-539` | term | home | Terms: physics capacity, growth limit, as the worlds inventory defines them (the same entries as `physics:530`) |
| `new:6` | not-done | home | Bodies farther than 1e5 m from the origin: they wait. Evidence: `Strata/src/Strata/Physics/PhysicsWorld.cpp:71-73` (`c_MaxBodyCoordinate`) |
| `new:19` | hands-on | home | Exercises (D27): a doctest after the test `At its growth limit a full world keeps bodies waiting`: a scene whose `PhysicsCapacity.MaxBodies` is 1,024, a `PhysicsSettings::GrowthLimit` of 2,048 set through `ScopedPhysicsSettings`, and 3,000 boxes; after the first step, `PhysicsStats`' `GrowthCount`, `BodyOverflowCount` and `PendingBodyCount` predicted and read; then 1,000 boxes destroyed, and the waiting ones built in the order they started waiting (done). Breakpoints in `ParkStaticBody` and `DisableParkedBodies` while an entity holding 2,000 static boxes is deactivated and stays inactive: the step their filters empty, then, 60 steps later, box3d's disables, at most 1,024 a step (trace). Evidence: `StrataTests/src/Physics/PhysicsCapacityTests.cpp:232-262`, `:459`; `Strata/src/Strata/Physics/PhysicsTypes.h:53-54`, `:157`, `:169`, `:200`; `StrataTests/src/Physics/PhysicsTestUtils.h:206-218`; `Strata/src/Strata/Physics/PhysicsWorld.cpp:64-65`, `:1530-1582` |
| `physics:171` | feature | link | Contact storage growth counting, read on `physics/tuning` |
| `scene-ecs:38` | feature | use | Prepared states: the slot a loaded scene's physics world waits in |
| `worlds-runtime:65` | feature | link | The world streamer's physics reservation |
| `worlds-runtime:325` | code | link | The cook's `ComputeMaxBodiesInRadius` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Loading scenes in slices: `PrepareLoadedScene`, prepared states and the frame's `SceneWorkBudget` | `world/sub-scenes` | must |
| Floating-point precision far from the origin; powers of two | `basics/numbers` | must |
| Queues | `basics/data-structures` | must |
| The job system and deterministic parallel work | `core/jobs` | must |
| One step and its order | `physics/world-step` | must |
| Records, slots and change rounds | `physics/building-bodies` | must |
| The broad phase's trees and the pair search | `physics/collision-detection` | must |
| The world streamer and its cells | `worlds/streamer` | helps |
| Writing and running one doctest case | `core/first-change` | helps |
| Running a debugger on a test or the editor | `core/debugging` | helps |

## `physics/tuning` — Tuning and measuring

**Covers.** A how-to: measure a physics scene and change its tuning with numbers, on a copy of the Physics Playground.
The goal and what must be true first (a copy of the sample; for the perf tests and the sweep, a source build in
Release). The numbered steps: play the Playground and read the Streaming panel's Physics row (capacity, growth, the
step's time and box3d's share); turn on Count contacts for the detailed statistics; read the whole `physics.stats`
answer; change a field of Project Settings > Physics > Simulation (`ContactRecycleDistance` 0.05 m, `SleepThreshold`
0.08 m/s, `ContactHertz` 30, `ContactDampingRatio` 10, `ContactPushSpeed` 3 m/s; clamped, applied at the next fixed
step) and see the numbers move; run the physics perf tests in Release against their budgets; run
`Tools/PhysicsSweep.py` (distances, knobs, workers, ball pits over many layouts, the Playground) on the settle scenes;
read its report. A table of the instruments and what each counts (`PhysicsStats`, box3d's stage profile and counters,
`IPhysicsDiagnostics`' constant-time step info, the settling instruments, contact storage growth). The result, then the
variations: a ball pit that never sleeps, `ContactHertz` above its ceiling, contact recycling off for a kinematic
platform (the regression exercise), chaotic piles compared over many layouts by their medians, and settings that only
code sets: `PhysicsSettings`' `CollisionSteps` for very fast bodies (clamped to 1 to 64) and the process defaults of
tests and tools (no project setting holds them: `Strata/src/Strata/Physics/PhysicsTypes.h:48`,
`Strata/src/Strata/Physics/PhysicsWorld.cpp:756`). Each why is at most two sentences and links `physics/dynamics` or
`physics/collision-detection`. At the end the reader can change a solver setting and show with numbers what it did.

**Leaves out.**

- What each setting does inside the solver → `physics/dynamics`, `physics/collision-detection`
- The game maker's half: `Physics.Simulation`, `physics.stats`, a pile that never sleeps → `make/physics`
- The perf lab's method: noise, budgets, the reference machine → `engineering/perf-lab`
- Every perf budget → `reference/performance`
- The Streaming panel's drawing → `editor-ui/instrument-panels`
- The picture of Project Settings' Timing page (FixedRate, Interpolation) → `world/projects-settings`

**Fit.** `fits`: about 3,950 words against M (3,000). Seven steps with three pictures take the most, then the
instruments' table and six variations; it stands 50 words under M's top, and the theory stays on the concept pages.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `physics:83` | feature | home | Process-default settings for tests and tools (`PhysicsSystem::SetDefaultSettings`), below the project's section |
| `physics:145-148` | feature | home | `PhysicsSettings`; the `Physics.Simulation` section with its defaults and clamps; contact recycling off for kinematic and presence bodies; the stiffness ceiling |
| `physics:150` | feature | home | The settle scenes, the `physics-settle` helper and `Tools/PhysicsSweep.py` |
| `build-test:225` | feature | home | `Tools/PhysicsSweep.py` as the build inventory lists it: the tool that sweeps physics tuning over the settle scenes and the Physics Playground, run in steps 6 and 7 |
| `physics:167-173` | feature | home | `PhysicsStats`, box3d's profile and counters with the detailed switch, `IPhysicsDiagnostics`, settling instruments, contact growth, the editor's commands and Streaming row, the perf tests |
| `physics:287` | concept | use | Tuning by measurement, as steps: representative scenes, many layouts, medians; the why in two sentences that link `physics/dynamics`, which teaches the concept |
| `physics:374-376` | figure | home | Project Settings' Physics > Simulation page (of `physics:374`, the Simulation page only: the Timing page, FixedRate and Interpolation, is pictured on `world/projects-settings`, where `Scene.Timing` is homed); the Streaming panel's Physics row with Count contacts on; a `physics.stats` answer as a text capture |
| `physics:412` | rule | home | `ContactHertz` above the ceiling does nothing |
| `physics:427` | rule | home | Compare chaotic results over many layouts |
| `physics:463` | hands-on | home | Exercise: a test that bodies fall asleep, with `GetLinearVelocity` and `PhysicsStats::SleepingBodyCount` |
| `physics:470-471` | hands-on | home | Exercises: `Tools/PhysicsSweep.py knobs` for one knob and its report; make `Physics.Settling`'s turning-platform case fail by turning recycling back on for kinematic bodies |
| `physics:540` | term | home | Terms: settle scene, sweep |
| `physics:257` | concept | use | Contact recycling, as the recycle distance changes it |
| `physics:255` | concept | use | Sleep, as the threshold changes it |
| `physics:248` | concept | use | Soft contacts, as the hertz, damping and push speed change them |
| `editor-core:91` | feature | link | The `world.*` and `physics.*` command group |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The measuring method: percentiles, self time, Tracy | `core/profiling` | must |
| What each `Physics.Simulation` field changes in the solver | `physics/dynamics` | must |
| Contact recycling and ghost collisions | `physics/collision-detection` | must |
| One step and where its instruments count | `physics/world-step` | must |
| Settings sections of a project | `world/projects-settings` | must |
| Running a program with arguments in a terminal | `basics/tools` | must |
| A source build in Release, and running tests with CTest | `core/first-change` | must |
| Running an editor command from its line | `start/how-to-read` | helps |
| Opening a copy of a sample | `start/first-game` | helps |
| Perf budgets and the reference machine | `engineering/perf-lab` | helps |
| The Streaming panel | `editor-ui/instrument-panels` | helps |

**Starting state.** A copy of the Physics Playground that the launcher made (Open Sample > Physics Playground), open
in the editor of the pin's build, with no change to its settings. Steps 5 to 7 also need the Release source build of
`core/first-change` (perf tests run in Release and Dist only), its `StrataTests` binary for the sweep, and Python 3.
The page starts from no checkpoint of a tutorial.

**Command-only steps.**

- Reading the whole `physics.stats` answer: no menu or button shows it (the Streaming panel shows a summary, and its
  Count contacts check box runs `physics.setDetailedStats`). Track E reaches this page before `editor/commands`, so the
  step gives the complete line to paste, one sentence on what it does and a link forward to `editor/commands`
  (`critique/rulings-4.md`, R11).

## Passed on

| Item | Type | To | Why |
| --- | --- | --- | --- |
| `physics:156-157` | feature | `world/systems` | The accumulator loop, backlog drop, time dilation and `SceneSettings` are the Scene's update code; book.md gives the code of the fixed step to `world/systems` |
| `physics:158` | feature | `world/projects-settings` | `Scene.Timing` is a settings section of the Scene module, handed over to scenes (that page's From names timing) |
| `physics:159-161` | feature | `world/interpolation` | Interpolated drawn transforms, their readers and the script SDK's drawn poses: book.md, "Interpolation of fixed steps" |
| `physics:241` | concept | `nowhere` | Repeats `scene-ecs:316` (the fixed step against a variable one, the accumulator, the spiral of death), whose home is `core/time` |
| `physics:275` | concept | `nowhere` | Repeats `scene-ecs:357` (interpolation of fixed-step motion) |
| `physics:299` | code | `nowhere` | Repeats `scene-ecs:388`: the same function of `Scene.cpp`, the fixed-step accumulator |
| `physics:322` | code | `nowhere` | Repeats `scene-ecs:390`: `BlendPose`, the same lines |
| `physics:354` | figure | `nowhere` | Repeats `scene-ecs:442`, the interpolation timeline with its roles |
| `physics:379` | figure | `nowhere` | Repeats `scene-ecs:489`, interpolation on and off |
| `physics:396` | rule | `nowhere` | Repeats `scene-ecs:539` (read the fixed step through `Scene::GetFixedTimestep`) |
| `physics:398` | rule | `nowhere` | Repeats `scene-ecs:541` (tools count fixed steps, not frames) |
| `physics:404` | rule | `nowhere` | Repeats `scripting:464` (entity destruction goes through `ScriptSystem::DestroyEntity`) |
| `physics:423` | rule | `nowhere` | Repeats `scene-ecs:546` (follow moving bodies with drawn positions in `OnLateUpdate`) |
| `physics:445-449` | hands-on | `make/physics` | Game makers' exercises: a falling crate, a toppled stack, four ball materials, a counting trigger and a launch pad, a raycast gun; `make/physics` is the use home of bodies, triggers and queries |
| `physics:450` | hands-on | `make/recipes` | The grab tool is a recipe from the Playground's scripts |
| `physics:451` | hands-on | `make/physics` | A Ghost layer toggled with `Physics::SetLayersCollide`: the use home of collision layers |
| `physics:452-453` | hands-on | `make/characters-cameras` | A player with a controller, and a follow camera fixed with `GetDrawnPosition`: the use home of both |
| `physics:454` | hands-on | `make/sound` | Impact sounds louder for harder hits |
| `physics:455` | hands-on | `make/physics` | Sleep Threshold and `physics.stats` on a ball pit: the game maker's half of tuning |
| `physics:456` | hands-on | `make/automated-playtests` | A command script that pauses, steps and checks with `until` |
| `physics:493-496` | term | `nowhere` | Repeat `foundation:572-575` (fixed timestep, accumulator, spiral of death, time dilation) |
| `physics:501` | term | `nowhere` | Repeats `foundation:637` (AABB) |
| `physics:511` | term | `basics/math-change` | Impulse is a term of Newton's laws; the glossary seed gives it that home |
| `physics:526` | term | `nowhere` | Repeats `scene-ecs:622` (EnTT's signals) |
| `physics:534-537` | term | `nowhere` | Repeat `scene-ecs:679-682` (state interpolation, step alpha, Blend, Compose and Exact, drawn transform) |
| `physics:538` | term | `basics/numbers` | The glossary seed's home of determinism; the promise that results do not depend on the number of threads is `core/jobs`' design decision, which `physics/world-step` uses |
| `physics:541` | term | `nowhere` | Repeats `foundation:592` (worker) and `foundation:590` (thread pool) |
| `physics:582` | open | `nowhere` | A note on release dates; each writer finds `since` from the tags (`process.md`, "What a writer is given") |
| `physics:585-599` | open | `nowhere` | Notes on what the survey did not read; the writers read those files at the pin |
| `physics:601` | open | `nowhere` | A note that no Manual page covers physics; the game makers' pages are `make/physics` and `make/characters-cameras` |

## Not taken

none

## Questions for the planner

none
