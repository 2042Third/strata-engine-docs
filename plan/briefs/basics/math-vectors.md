# Brief: `basics/math-vectors`

| Field | Value |
| --- | --- |
| Title | Vectors: length, direction, dot and cross products |
| Kind | P |
| Size | L |
| Tracks | B, E |
| Needs | `basics/programming-2` |
| From | foundation "The math toolkit" (the mathematics: vectors); angles in degrees and radians, sine, cosine and `atan2` |
| Unit | `plan/allocation/basics-b.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `basics/math-vectors` — Vectors: length, direction, dot and cross products

**Covers.** The page teaches vectors from the (x, y) graph that the reader already knows, in a script of the
playground that logs values and moves an entity, so that every formula is first computed by hand and then by `glm`.
In order: (1) a position as coordinates measured from an origin, first on a flat (x, y) graph and then with a third
axis z (which way each axis points in Strata is `basics/math-matrices`' and is only named here); (2) a vector as an
arrow: the step from one position to another (`b - a`), adding steps tip to tail, subtracting, and scaling by a number,
each done per coordinate, first in 2D (a mouse movement as a `glm::vec2`, added and scaled per component) and then in
3D (`glm::vec3`); positions and directions as two uses of the same three numbers, and a velocity as a direction with a
length per second; (3) the Pythagorean theorem, from the right triangle with sides 3, 4 and 5, then in three dimensions,
which gives a vector's length and the distance between two points (`glm::length`, `glm::distance`); (4) unit vectors
and normalizing (`glm::normalize`), and why a zero vector must never be normalized; (5) angles: degrees, which the
reader knows, radians and π (`glm::radians`); (6) the unit circle: cosine and sine as the coordinates of the point at
an angle, the tangent function as their ratio, and sine as a wave between -1 and 1 over time, with its amplitude and its
period (the bobbing coin of `make/script-loop`); (7) `atan2(y, x)`, the angle of a direction in all four quarters of
the circle (`std::atan2`), and why `atan` alone fails; (8) the dot product: the sum of the products of matching
coordinates (a sum of products along a direction), its sign (in front or behind), the angle between two directions from
‖a‖ ‖b‖ cos θ, the part of a vector along an axis (projecting onto an axis) and the part left when that is removed
(projecting onto a plane); (9) the cross product: a vector at a right angle to two others, the right-hand rule, its
length as the area of their parallelogram, why `cross(a, b)` is `-cross(b, a)`, the surface normal of a triangle from
two of its edges, and the lever arm (a push far from a hinge turns more; the word torque is named with its page).

Each idea follows `style.md` §4: the picture, small numbers by hand, the formula read aloud, the `glm` call, a check at
the limits. The common mistakes: degrees passed to `std::sin`, the arguments of `atan2` swapped, normalizing a zero
vector, a dot product of directions that were not normalized read as a cosine, the order of a cross product. Practice
(three to eight exercises, `style.md` §8) ends with the optional Coin Run item: a magnet that pulls the coins within
3 metres toward the ball. "Where the book uses it" names `make/gameplay-math`, `physics/collision-detection`,
`light/reflectance` and `audio/spatial`.

**Leaves out.**

- Which way Strata's axes point, handedness and units → `basics/math-matrices`
- Matrices and transforms → `basics/math-matrices`
- Rotations, Euler angles and quaternions → `basics/math-rotations`
- Velocity as a rate of change, and moving by it step by step → `basics/math-change`
- Frequency, and waves as signals → `basics/signals`
- Rays, planes and intersection tests → `basics/math-geometry`
- Torque, inertia and how bodies turn → `physics/dynamics`
- The recipes a game maker types (distance, facing, turning toward a target) → `make/gameplay-math`
- Why floating-point results are approximate → `basics/numbers`

**Fit.** `fits`: about 5,500 words against L (5,000). The nine ideas from zero at 300 to 700 words each take the most
(4,400); the fixed parts with the Test out box, Practice and the Coin Run item take the rest (1,100).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:1` | concept | home | Positions as coordinates measured from an origin, on the (x, y) graph and then with z; coordinate, origin. Figure: points on the graph. General knowledge. |
| `new:2` | concept | home | Vectors as arrows: the step b - a, adding tip to tail, subtracting, scaling, all per coordinate; 2D vectors (`glm::vec2`, a mouse movement) and 3D vectors (`glm::vec3`); positions against directions; a velocity as a direction with a length. Figure: adding two arrows. General knowledge. |
| `new:3` | concept | home | The Pythagorean theorem in 2D and 3D; a vector's length and the distance between two points (`glm::length`, `glm::distance`). Figure: the 3-4-5 triangle. General knowledge. |
| `new:4` | concept | home | Unit vectors and normalization (`glm::normalize`); the zero vector, which has no direction. General knowledge. |
| `new:5` | concept | home | Angles in degrees and radians, and π (`glm::radians`, `glm::degrees`). General knowledge. |
| `new:6` | concept | home | The unit circle: cosine, sine and the tangent function; sine as a wave between -1 and 1 with an amplitude and a period. Figures: the unit circle, the sine wave. General knowledge. |
| `new:7` | concept | home | `atan2(y, x)`: the angle of a direction in all four quarters, against `atan` of a ratio (`std::atan2`). General knowledge. |
| `new:8` | concept | home | The dot product: a sum of products, its sign, the angle between two directions, the part of a vector along an axis (vector projection) and the part in a plane. Figure: the dot product as a shadow on an axis. General knowledge. |
| `new:9` | concept | home | The cross product: at a right angle to both vectors, the right-hand rule, its length as an area, its order, the surface normal of a triangle from two edges, the lever arm. Figure: the right hand. General knowledge. |
| `new:10` | hands-on | home | Coin Run practice, from `make/project-coin-run`'s end state: a `CoinMagnet` script moves each coin within 3 m toward the ball by the step from coin to ball, its length, `glm::normalize`, a speed and `deltaTime`. Evidence: `StrataScriptCore/Include/StrataScript/Entity.h:200` (`GetWorldPosition`) and `:177-182` (`SetTranslation`); `StrataScriptCore/Include/StrataScript/Scene.h:116` (`FindEntityByName`) |
| `scripting:120` | feature | use | `TransformComponent`'s `GetWorldPosition`, `GetTranslation` and `SetTranslation`, the calls the page's scripts read and move positions with |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Variables, expressions, `if`, and namespaces with `::` (`glm::`) | `basics/programming-1` | must |
| A script of the playground: `OnUpdate`, `deltaTime` and `Log::Info` | `basics/programming-1` | must |
| Functions with parameters and return values, structs | `basics/programming-2` | must |
| References as parameters (`const glm::vec3&`) | `basics/programming-3` | helps |
| Why floating-point numbers are approximate | `basics/numbers` | helps |
| A position and a rotation in the Inspector | `make/transforms-units` | helps |

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
| `atan2` | atan2 | - |
| `coordinate` | coordinate | vector component |
| `cosine` | cosine | - |
| `cross-product` | cross product | - |
| `dot-product` | dot product | - |
| `normalization` | normalization | normalize, normalized, normalizing |
| `origin` | origin | Command origin |
| `pi` | pi | - |
| `pythagorean-theorem` | Pythagorean theorem | - |
| `radian` | radian | - |
| `sine` | sine | - |
| `surface-normal` | surface normal | normal vector |
| `tangent-function` | tangent function | - |
| `unit-circle` | unit circle | - |
| `unit-vector` | unit vector | - |
| `vector` | vector | - |
| `vector-length` | vector length | magnitude, norm |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-basics-b-5 | should | missing-item | new item on `basics/math-vectors`, beside `new:8` | No page of the plan teaches the reflection of a direction about a normal, r = d - 2 (d · n) n. The forward shader, screen-space reflections, the BRDF table and the prefilter all call `reflect`, and pages of `indirect` draw reflected rays. The page already teaches the part of a vector along an axis, which is one step from it. | Idea (8) adds reflection: the part along the normal taken away twice, a ball bouncing off a wall worked by hand, `glm::reflect` in code, and the mistake of a normal that is not unit length. A new concept row, about 150 words; `light/reflectance` and `indirect/ssr` use it. | `allocation/basics-b.md:18-21`, `:58`; `allocation/indirect.md:167`, `:500`, `:555`; `Strata/shaders/Scene/Forward.frag.slang:127`; `Strata/shaders/Include/ScreenReflections.slang:52`; `Strata/shaders/IBL/BRDFLut.comp.slang:36`; `Strata/shaders/IBL/Prefilter.comp.slang:45`; a search for `reflect(` in `allocation/*.md` and `inventory/*.md` finds nothing |
| critic-basics-b-9 | should | missing-item | `new:11` and `new:12` on `basics/math-matrices`; `new:2` on `basics/math-vectors` | The pages log matrices (`basics/math-bases` logs a frame's transpose times the frame), but `Log::Info` prints numbers, text, float vectors, quaternions, entities and asset handles only: a `glm::mat3` or a `glm::uvec2` passed to it does not compile. And glm's default constructors set nothing: `glm::mat4 m;` holds whatever was in memory, not the identity, and so does `glm::vec3 v;`. No row says either. | The first code of `basics/math-matrices` logs a matrix column by column (`Log::Info(m[0], " ", m[1], " ", m[2])`), which also shows that `m[i]` is a column and `m[i][j]` its row j; a common mistake: a matrix declared without a value, with `glm::mat4(1.0f)` as the identity (about 120 words). `basics/math-vectors` adds the same for `glm::vec3(0.0f)` (about 30 words). | `allocation/basics-b.md:126-127`, `:176-179`, `:213`; `StrataScriptCore/Include/StrataScript/Log.h:21-54`; `Strata/vendor/glm/glm/detail/setup.hpp:505-511`, `:864-869`; `Strata/vendor/glm/glm/detail/type_mat4x4.hpp:35`; `Strata/vendor/glm/glm/detail/type_vec3.hpp:107` |
| critic-basics-b-12 | should | thin-home | `new:4` and the common mistakes of `basics/math-vectors` | The mistake "normalizing a zero vector" has no symptom in the rows. At the pin `glm::normalize` of a zero vector gives NaN, the host refuses the transform with "the translation must be finite", the coin stops, and the warning comes once per entity, not every frame. A second glm trap is not listed: `a * b` of two vectors multiplies per coordinate and is not the dot product. | The mistake states Strata's symptom, the message and the fix, a length check before normalizing, which the CoinMagnet item needs (about 60 words). Add the mistake of `a * b` taken for `glm::dot(a, b)` (about 40 words). | `allocation/basics-b.md:26-27`, `:54`, `:60`; `Strata/src/Strata/Scripting/ScriptHostAPI.cpp:246-251`, `:733-744`; `Strata/src/Strata/Scripting/ScriptSystem.cpp:1541-1559`; `Strata/vendor/glm/glm/detail/type_vec3.inl:575-579` |
