# Brief: `physics/dynamics`

| Field | Value |
| --- | --- |
| Title | Rigid body dynamics: integration, contacts, solvers, sleep and continuous collision |
| Kind | C |
| Size | L |
| Tracks | E |
| Needs | `physics/collision-detection`, `core/time`, `basics/math-change`, `basics/math-rotations` |
| From | physics ch. 4 (second half), concepts 3, 9-12: integration, mass and inertia, contacts as soft constraints, sub-stepping, friction, restitution, continuous collision, islands and sleep, box3d's choices; a toy solver first; split from `physics/how-simulation-works` |
| Unit | `plan/allocation/physics.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `contact-constraint` | Contact constraint | - |
| `continuous-collision-ccd` | Continuous collision (CCD) | - |
| `inertia-tensor` | Inertia tensor | - |
| `island` | Island | - |
| `push-speed-contactspeed` | Push speed (contactSpeed) | - |
| `sleep-threshold` | Sleep threshold | - |
| `soft-contact` | Soft contact | contact hertz, damping ratio |
| `sub-step` | Sub-step | - |
