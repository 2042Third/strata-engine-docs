# Brief: `basics/math-geometry`

| Field | Value |
| --- | --- |
| Title | Geometry for engines: rays, planes, boxes and intersection tests |
| Kind | P |
| Size | L |
| Tracks | B, E |
| Needs | `basics/math-matrices`, `basics/math-projection` |
| From | new; rays, planes, boxes, frustums, intersection tests and their robustness in floating point (Ericson, *Real-Time Collision Detection*) |
| Unit | `plan/allocation/basics-b.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `basics/math-geometry` — Geometry for engines: rays, planes, boxes and intersection tests

**Covers.** Each shape and test is written as a small function in a script and run on numbers the reader checks by
hand. In order: (1) rays: an origin plus t times a direction, t from 0 upward, and the point at a given t; (2) planes: a
normal and a distance from the origin, the signed distance of a point (a dot product), which side of the plane a point
is on; (3) where a ray meets a plane, and the ray that never does (parallel to it); (4) spheres: a center and a radius,
a point inside, two spheres that overlap, bounding spheres; a ray against a sphere through the quadratic formula,
taught from zero; (5) boxes: the axis-aligned bounding box (AABB) as a smallest and a largest corner, or as a minimum
and a size, whether it holds a point, whether two overlap (one test per axis), growing a box to hold a shape; the
oriented bounding box; bounding volumes as cheap stand-ins that a test tries first; (6) a ray against a box: the slab
test; (7) a ray against a triangle: the triangle's plane, then whether the point lies inside (one cross product per
edge); (8) the view frustum of `basics/math-projection` as six planes, and a sphere or a box tested against them, with
the rule that such a test may keep something outside but must never drop something inside; (9) separating axes: two
convex shapes do not touch when some axis separates their shadows, and a triangle against a box as the worked case;
(10) robustness: tolerances, the degenerate cases (a ray parallel to a plane, a box of zero size, a direction of zero
length), and why tests that are exact on paper fail in floating point. Strata's own types (`Ray`, `AABB`, `Frustum`)
are named as the code that `core/math` walks through.

Figures: a ray meeting a plane, the slab test in 2D, a separating axis between two boxes, a frustum with a sphere inside,
one outside and one across a side. The common mistakes: a hit at negative t taken, a plane normal that is not unit
length, floats compared with `==`, a box whose minimum is larger than its maximum. Practice (three to eight exercises,
`style.md` §8) ends with the optional Coin Run item: collect a coin by testing the ball's bounding sphere against the
coin's box by hand, and log where a ray straight down from the ball meets the ground's plane, next to what
`Physics::Raycast` returns.
"Where the book uses it" names `draw/bounds-culling`, `physics/collision-detection`, `physics/queries`,
`editor/placement` and `ui/input`.

**Leaves out.**

- The frustum's shape and where it comes from → `basics/math-projection`
- Extracting the frustum's planes, the positive vertex and `AABB::Transformed` → `draw/bounds-culling`
- Strata's `Ray`, `AABB` and `Frustum` code → `core/math`
- Broad phase, narrow phase and contacts in the physics engine → `physics/collision-detection`
- Raycasts and shape queries in a game → `physics/queries`
- Placing content where the cursor's ray hits → `editor/placement`
- Hitting world-space UI with the camera's ray → `ui/input`
- Voxelizing triangles for global illumination → `indirect/gi-voxels`

**Fit.** `fits`: about 5,800 words against L (5,000). The ten ideas at 400 to 600 words take the most (4,700); the
fixed parts with the Test out box, Practice and the Coin Run item take the rest (1,100).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:45` | concept | home | Rays: an origin plus t times a direction, t from 0 upward. General knowledge. |
| `new:46` | concept | home | Planes: a normal and a distance; the signed distance of a point; which side a point is on. Figure: a point above a plane. General knowledge. |
| `new:47` | concept | home | Where a ray meets a plane, and the parallel ray that never does. Figure: a ray meeting a plane. General knowledge. |
| `new:48` | concept | home | Spheres and bounding spheres: a point inside, two spheres overlapping, a ray against a sphere through the quadratic formula. General knowledge. |
| `new:49` | concept | home | Boxes: the AABB as a minimum and a maximum (or a minimum and a size), holding a point, overlapping per axis, growing to enclose; the oriented bounding box; bounding volumes as stand-ins. General knowledge. |
| `new:50` | concept | home | A ray against a box: the slab test. Figure: the slab test in 2D. General knowledge. |
| `new:51` | concept | home | A ray against a triangle: the plane, then one cross product per edge. General knowledge. |
| `new:52` | concept | home | The frustum as six planes; spheres and boxes against them, a test that may keep what is outside but never drops what is inside. Figure: three spheres and a frustum. General knowledge. |
| `new:53` | concept | home | Separating axes: convex shapes that do not touch; a triangle against a box. Figure: an axis between two boxes. General knowledge. |
| `new:54` | concept | home | Robustness: tolerances, degenerate cases, why exact tests fail in floating point. General knowledge. |
| `new:55` | hands-on | home | Coin Run practice, from `make/project-coin-run`'s end state: the ball's bounding sphere against a coin's box, by hand; a ray down from the ball against the ground's plane, logged beside `Physics::Raycast`'s hit. Evidence: `StrataScriptCore/Include/StrataScript/Entity.h:200-202` (world position and scale), `StrataScriptCore/Include/StrataScript/Physics.h:175` (`Physics::Raycast`) |
| `foundation:637` | term | home | AABB; one glossary entry with `render-scene:594` and the seed's |
| `render-scene:594` | term | home | AABB, as the drawing part's glossary words it; one glossary entry |
| `foundation:143` | feature | link | Strata's `AABB`, empty by default, with expand, contains and intersects; its home is `core/math` |
| `foundation:144` | feature | link | Strata's `Frustum` and its point, sphere and box tests; its home is `core/math` |
| `foundation:145` | feature | link | Strata's `Ray` with its tests against boxes (slabs), spheres, planes and triangles; its home is `core/math` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Vectors, length, normalizing, the dot and cross products | `basics/math-vectors` | must |
| Matrices, transforms and spaces (a box carried by a transform) | `basics/math-matrices` | must |
| The view frustum: what a camera sees between its near and far planes | `basics/math-projection` | must |
| Floating-point rounding and precision | `basics/numbers` | must |
| Functions with parameters and return values, structs | `basics/programming-2` | must |
| `std::optional` for a hit that may not exist | `basics/programming-3` | helps |

**Starting state.** The optional Coin Run item of Practice starts from the download of `make/project-coin-run`'s end
state, as the outline's introduction of part `basics` says for every primer after `basics/debugging`: Coin Run as
`make/project-coin-run` finishes it, with the rolling ball, the spinning coins, the HUD, the sounds, winning, losing and
the restart. The page's other examples and exercises run in the playground (`style.md` §8), which is no checkpoint.

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `axis-aligned-bounding-box` | axis-aligned bounding box | AABB |
| `bounding-box` | bounding box | - |
| `bounding-sphere` | bounding sphere | - |
| `intersection-test` | intersection test | - |
| `oriented-bounding-box` | oriented bounding box | OBB |
| `plane` | plane | - |
| `ray` | ray | - |
| `tolerance` | tolerance | epsilon |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-basics-b-3 | should | shape | the Practice of all twelve pages | Each page's Practice is named only by its optional Coin Run item. No row holds the other two to seven exercises (style.md asks three to eight), nor the exercise that runs code in the playground, which track E needs and which an optional item for track B cannot be. basics-a gives each primer a row "Practice before the Coin Run item" and counts the fixed parts at 1,300 to 1,450 words; basics-b counts them at 1,100. R32 D27 asked every unit to add the missing exercises as items. | Each page gets a hands-on row for its Practice, from easy to hard, run in the playground's script and read in the Console, at least one of them run and logged (about 250 words a page, D27's measure). The Fit lines count the fixed parts again. `basics/math-matrices` (6,000), `basics/math-projection` (5,900) and `basics/math-geometry` (5,800) then reach the top of L and go to the second size pass by S5. | `allocation/basics-b.md:28`, `:101-103`, `:175`, `:253`, `:330`, `:417`, `:496`, `:570`, `:652`, `:743`, `:825`, `:925`; Fit lines `:44`, `:118`, `:269`, `:435`; `allocation/basics-a.md:192`, `:211`, `:266`, `:285`; `style.md:584`, `:598-606`; `critique/rulings-7.md:206`; `outline-1.md:242` |
