# Notes: `basics/math-geometry`

## New terms

- **signed distance**: the distance of a point from a plane, positive on the side the plane's normal points to,
  negative on the other side and 0 on the plane. Home: `basics/math-geometry`. Aliases: none.
- **quadratic equation**: an equation of the form a t squared plus b t plus c equal to 0, solved by the quadratic
  formula. Home: `basics/math-geometry`. Aliases: quadratic.
- **bounding volume**: a simple shape, a sphere or a box, that holds a complex one and stands in for it in a cheap first
  test. Home: `basics/math-geometry`. Aliases: none.
- **slab**: the space between two parallel planes; a box is where three slabs meet. Home: `basics/math-geometry`.
  Aliases: slabs.
- **convex**: a shape is convex when a straight line between any two of its points stays inside it. Home:
  `basics/math-geometry`. Aliases: none.
- **separating axis**: a direction onto which the shadows of two convex shapes do not overlap, which proves that they
  do not touch. Home: `basics/math-geometry`. Aliases: none.

The page also defines the glossary's entries of its brief in bold: ray, plane, intersection test, bounding sphere,
bounding box, axis-aligned bounding box (AABB), oriented bounding box (OBB), tolerance (epsilon).

## Requests

- `tools/data/extra-words.txt`: "quadratic" (the term proposed above; its word-list finding is left until the term
  exists).
- Figures: five diagram requests in `src/content/figures/basics/math-geometry.json` (a point above and below a plane, a
  ray meeting a plane, the slab test in 2D, three spheres against a frustum, a separating axis between a box and a
  triangle). None is drawn yet.
- No external host is linked: Ericson's book and the Moller and Trumbore paper are cited without a link in Further
  reading.

## Not verified

- Coin Run's details: the ball's width and scale, the ground's height and whether the end state of
  `make/project-coin-run` has a script on the ball that can log in `OnFixedUpdate`. Practice 5 says only what
  `Entity.h` and `Physics.h` of `StrataScriptCore` show (`GetWorldPosition`, `GetWorldScale`, `Physics::Raycast` with
  `ignore`, `RaycastHit::Distance` and `Point`).
- The spacing of floats near 1, 1,000 and 100,000 (about 1.2e-7, 6e-5 and 0.008) is computed from the 24-bit
  significand, not taken from the engine.
- That a zero direction gives NaN in `Ray`'s constructor and then passes the guards (`< 1e-8`) of the tests: read from
  `Ray.h` and `Ray.cpp` and from `glm::normalize`, not run.
- The sketches' output was produced by compiling and running them here (`-Wall -Wextra -Werror`, glm of the pin).

## Findings not applied

- `critic-basics-b-3` (the Practice's other exercises, one run in code): applied. The Practice has five exercises: three
  by hand, one code exercise with a sketch solution (`basics-math-geometry-enclose.cpp`) and the optional Coin Run
  item, which is pseudocode.
- The brief's figure "an axis between two boxes" is drawn as an axis between a box and a triangle, the worked case of
  the section; two boxes are described in words.
- The brief's "the oriented bounding box" has no hand-run test of its own: its overlap test is the separating-axis
  test of the next sections, and the page says so.

## Clerk

- Admitted: signed distance, quadratic equation (alias quadratic), bounding volume, slab, convex, separating axis.

## Track walk E-final-4

Each sketch of the page compiled with `cl /std:c++20 /EHsc` (Visual Studio 2026, 19.50) and with g++ 15 `-std=c++20`, glm from the 0.8.0 package's `StrataScriptCore/ThirdParty/glm`; both printed the same output (`docs-work/walkfix-E4/cl/`, 2026-11-24). The exact Windows line of the page was run in PowerShell in a Visual Studio developer environment (`cmdtest/`).

In Checkpoint 4 of `make/project-coin-run` the ball's script is `BallControl`, which has an `OnFixedUpdate`.
