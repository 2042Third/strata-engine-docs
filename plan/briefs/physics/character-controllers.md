# Brief: `physics/character-controllers`

| Field | Value |
| --- | --- |
| Title | Character controllers |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `physics/world-step`, `physics/queries` |
| From | physics ch. 9; 1.9 (why kinematic, collide and slide, steps, slopes, snapping, platforms, pushing, the presence body, the root-motion hook, determinism) |
| Unit | `plan/allocation/physics.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `character-controller` | Character controller | - |
| `collide-and-slide` | Collide and slide | - |
| `ground-snapping` | Ground snapping | - |
| `ground-state` | Ground state | - |
| `mover-box3d` | Mover (box3d) | - |
| `presence-body` | Presence body | - |
| `step-height` | Step height | step up |
