# Brief: `core/math`

| Field | Value |
| --- | --- |
| Title | Strata's math toolkit |
| Kind | I |
| Size | M |
| Tracks | E |
| Needs | `basics/math-rotations`, `basics/math-projection`, `basics/math-geometry`, `core/conventions` |
| From | foundation "The math toolkit" (the code, §1.8): `PerspectiveReverseZ*`, `Ray::FromNDC`, `ComposeWorldTransform` and its FMA rule; culling is `draw/bounds-culling`'s, the conventions are `gpu/coordinates`' |
| Unit | `plan/allocation/core.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `core/math` — Strata's math toolkit

**Covers.** The job: the small set of math types and functions that every part of the engine shares, the conventions
they follow and the rule they enforce. The mathematics is the primers'; this page is Strata's code, and its problem
section is one paragraph that links the primers. The map: `Math/Math.h`, `AABB`, `Frustum`, `Ray` and `Random` over glm.
The contract: the conventions stated once in `Math.h` (right-handed, +Y up, −Z forward as in glTF; NDC with +Y up and
depth from 0 to 1, reversed), in one paragraph, since their home is `gpu/coordinates`; transforms (`DecomposeTransform`,
which refuses matrices that are not finite or are degenerate and folds a reflection into X; `ComposeTransform`;
`ComposeWorldTransform`, one compiled multiply, so that fused multiply-adds cannot make the scene's paths disagree, with
its rule); projections (`PerspectiveReverseZ` by swapping near and far, `PerspectiveReverseZInfinite` with depth = near
/ −z, whose infinite far plane is said in one sentence and linked to `gpu/coordinates`, the term's home,
`OrthographicReverseZ`); rotations (Euler degrees to and from quaternions, the forward, right and up directions,
`LookRotation` with its fallback for up, and `IsNearlyEqual`, which knows that q and −q are one rotation); `AABB` (empty
by default, expand, contains, intersects, `Transformed` by Arvo's method); `Ray` (`FromNDC`, which works with an
infinite reversed-Z projection because it takes depths 1 and 0.5; tests against boxes by slabs, spheres, planes, and
triangles by Möller and Trumbore); `Random` (a `mt19937_64` per thread, seeded from `random_device`, with `Seed` for
repeatable runs; the scripts' `Random` is the SDK's own). The mistakes the choices prevent: row against column major,
quaternions compared by their components, a depth from 0 to 1 treated like OpenGL's from −1 to 1, and FMA making one
product two. The toy is a ray from the mouse through an infinite reversed-Z projection, in 30 lines; the real code is
the projections, `Ray::FromNDC`, the decomposition and `ComposeWorldTransform` (the code of `AABB::Transformed` is
quoted on `draw/bounds-culling`, which book.md gives the box tests). The page's example: a ray from a pixel into the
scene, as picking and the camera's ray build it. The exercises: a frustum test of a grid of boxes with `Frustum` and
`AABB::Transformed`; `PerspectiveReverseZInfinite` derived on paper and checked against `MathTests.cpp`; a trace of the
editor's placement ray from the view to `Ray::FromNDC`. At the end the reader can use the toolkit's types, build a ray
from a pixel and say why world matrices are composed in one place.

**Leaves out.**

- Vectors, matrices and transforms as mathematics → `basics/math-matrices`
- Decomposing a matrix into translation, rotation and scale, as mathematics → `basics/math-bases`
- Projection and reversed Z as mathematics → `basics/math-projection`
- Strata's clip space, depth conventions and precision, the camera → `gpu/coordinates`
- Frustum planes, the positive vertex and culling → `draw/bounds-culling`
- FMA contraction and determinism across compilers → `engineering/flags-portability`
- The scripts' `Random` and `Motion` → `make/recipes`
- The transform contract and the scene's world matrices → `world/scene-graph`

**Fit.** `fits`: about 3,550 words against M (3,000). The contract of the toolkit's types (transforms, projections,
rotations, `AABB`, `Ray` and `Random`) and its quotes take the most; three exercises follow.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `foundation:325` | concept | home | Math for engines as Strata chose it: glTF's axes, reversed Z with an infinite far plane; the mistakes (row and column major, quaternions compared by components, a 0-to-1 depth taken for OpenGL's, FMA); the mathematics itself is the primers' |
| `foundation:140` | feature | home | Transforms: `DecomposeTransform`, `ComposeTransform` and `ComposeWorldTransform` |
| `foundation:141` | feature | home | Projections: `PerspectiveReverseZ`, `PerspectiveReverseZInfinite` and `OrthographicReverseZ` |
| `foundation:142` | feature | home | Rotations: Euler degrees and quaternions, forward, right and up, `LookRotation`, `IsNearlyEqual` |
| `foundation:143` | feature | home | `AABB`, the type and its operations; how `Transformed` serves culling is `draw/bounds-culling`'s |
| `foundation:145` | feature | home | `Ray`: `FromNDC` and the intersection tests |
| `foundation:146` | feature | home | `Random`: one generator per thread, seeded, with `Seed` for repeatable runs |
| `foundation:370` | code | home | `Strata/src/Strata/Math/Math.cpp:71-91`: the reversed-Z projections (near and far swapped; the infinite far plane); the item's second half, `Frustum.cpp`'s plane extraction and positive-vertex test, is quoted on `draw/bounds-culling` |
| `foundation:373` | code | home | `Strata/src/Strata/Math/Ray.cpp:7-16`: the ray from NDC with reversed Z; also `Math/Math.cpp` 9-54 (decomposition with the reflection folded into X); `Math/AABB.cpp` 7-25 (Arvo's box) is not quoted here: `draw/bounds-culling` uses it (book.md gives it the box tests; draw-q3, D43); the item's pieces about modules are used by `core/engine-modules` |
| `foundation:502` | rule | home | Compose world matrices only through `Math::ComposeWorldTransform` |
| `foundation:530` | hands-on | home | A frustum test of a grid of boxes with `Frustum` and `AABB::Transformed` under an infinite reversed-Z projection |
| `foundation:531` | hands-on | home | `PerspectiveReverseZInfinite` derived on paper and checked against `MathTests.cpp` 79-93 |
| `new:35` | hands-on | home | Trace it yourself: the editor's placement ray followed with a search or the debugger from the camera's rotation-only view to `Ray::FromNDC` and back to world space, and why the camera's position is added only once. Evidence: `StrataEditor/src/Editor/EditorPlacement.cpp:97-104`; `Strata/src/Strata/Math/Ray.cpp:7-16` |
| `foundation:635` | term | link | Infinite far plane, said in one sentence where `PerspectiveReverseZInfinite` is shown; its entry is `gpu/coordinates`' (R31, D33) |
| `foundation:139` | feature | use | The conventions comment of `Math.h`, in one paragraph; their home is `gpu/coordinates` |
| `foundation:144` | feature | use | `Frustum`, named as a type of the toolkit; its home is `draw/bounds-culling` |
| `foundation:425` | figure | use | Its second sketch, the ray from NDC through the near plane and depth 0.5, drawn here; the frustum half is `draw/bounds-culling`'s |
| `foundation:424`, `foundation:426` | figure | link | Reversed Z's depth precision and the coordinate conventions, drawn on `gpu/coordinates` |
| `foundation:632`, `foundation:633`, `foundation:634`, `foundation:636`, `foundation:637`, `foundation:638`, `foundation:639`, `foundation:640`, `foundation:641` | term | link | The terms the page uses, whose entries are the primers' and the later pages' |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Vectors, matrices, TRS, spaces and matrix order | `basics/math-matrices` | must |
| Quaternions and Euler angles | `basics/math-rotations` | must |
| Projection, homogeneous coordinates, NDC and reversed Z | `basics/math-projection` | must |
| Rays, planes, boxes and intersection tests | `basics/math-geometry` | must |
| Floating-point rounding | `basics/numbers` | must |
| The code style | `core/conventions` | must |
| `glm` | `basics/math-vectors` | helps |
| Strata's clip space and the infinite far plane | `gpu/coordinates` | helps |
| FMA contraction across compilers | `engineering/flags-portability` | helps |
| Random numbers and seeds | `basics/math-probability` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

None: the glossary homes no term on this page.
