# Brief: `physics/collision-detection`

| Field | Value |
| --- | --- |
| Title | Collision detection: shapes, broad phase and narrow phase |
| Kind | C |
| Size | L |
| Tracks | E |
| Needs | `physics/bodies-colliders`, `basics/math-geometry`, `basics/trees-graphs` |
| From | physics ch. 4 (first half), concept 8: AABB trees, pair finding, GJK, contact manifolds (Catto's BVH and GJK talks, Ericson); split from `physics/how-simulation-works` |
| Unit | `plan/allocation/physics.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `broad-phase` | Broad phase | - |
| `contact-recycling` | Contact recycling | - |
| `ghost-collision` | Ghost collision | - |
| `manifold` | Manifold | contact point |
| `narrow-phase` | Narrow phase | - |
