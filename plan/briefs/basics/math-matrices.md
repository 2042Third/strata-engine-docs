# Brief: `basics/math-matrices`

| Field | Value |
| --- | --- |
| Title | Matrices and transforms: TRS, hierarchies, spaces and conventions |
| Kind | P |
| Size | L |
| Tracks | B, E |
| Needs | `basics/math-vectors`, `basics/numbers` |
| From | foundation "The math toolkit" (the mathematics: matrices); translation, rotation and scale, hierarchies, spaces, the inverse; home of axes, handedness, units and matrix order; bases, the determinant and normals are `basics/math-bases`' |
| Unit | `plan/allocation/basics-b.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `basics/math-matrices` — Matrices and transforms: TRS, hierarchies, spaces and conventions

**Covers.** The page opens with its own Test out box: five questions on this page's ideas alone. In order: (1) a
matrix as a grid of numbers, and a matrix times a vector as one dot product per row, first 2×2 on the (x, y) graph;
(2) what a matrix does: its columns are where the axes go (basis vectors), which gives a scale and a rotation by an
angle in 2D from cosine and sine, then their 3×3 forms, and the identity matrix; (3) combining transforms: the matrix
product (each number of the result a dot product of a row and a column), and why the order matters, shown with "turn,
then move" against "move, then turn"; (4) translation needs a fourth number: 4×4 matrices, w = 1 for a position and
w = 0 for a direction, so that a direction is changed only by the linear part (linear transforms of directions),
affine transforms, the translation in the last column and the axes in the other three (the columns of a transform
matrix); (5) TRS: scale first, then rotation, then translation, as T · R · S; (6) spaces: local space and world space,
the transform hierarchy, a child's world matrix as its parent's world matrix times its local one, so that moving a
parent moves its children; (7) the inverse: the matrix that undoes another, the inverse of a product in the reverse
order, a child's local transform from world ones (`inverse(parentWorld) * world`), `glm::inverse`, and the matrix that
has none; (8) conventions: column vectors on the right and the matrix order they set (P · V · M), glm's column-major
storage, right-handed axes (the right-hand rule of the cross product), +Y up, -Z forward and units in metres, as
Strata's math code states them, and how to recognize another engine's convention. A 3×3 matrix is also what turns one
set of three numbers into another, such as a color in one color space into another (`basics/color`) or a body's
inertia (`physics/dynamics`). Bases, the determinant, normals and decomposing a matrix are taught on the next primer,
`basics/math-bases`.

Figures: the axes moved by a 2×2 matrix, turn-then-move against move-then-turn, a parent and its child, the right hand
with Strata's axes. The common mistakes: the multiplication order reversed, rows read as columns. Practice (three to
eight exercises, `style.md` §8) ends with the optional Coin Run item: a ring of coins made children of a turning empty
entity; the reader predicts one coin's world position by hand and checks it against `GetWorldPosition` in the log.
"Where the book uses it" names `world/scene-graph`, `gpu/coordinates` and `animation/skeletons`.

**Leaves out.**

- Rotations as Euler angles and quaternions → `basics/math-rotations`
- Bases and tangent space, the determinant, the inverse transpose and decomposing a matrix → `basics/math-bases`
- Projection matrices and the division by w → `basics/math-projection`
- Strata's clip space, NDC and depth conventions → `gpu/coordinates`
- Strata's transform code (`ComposeWorldTransform`) and its FMA rule → `core/math`
- The scene's cached world transforms and the transform contract → `world/scene-graph`
- Inverse bind matrices and skinning → `animation/skinning`
- The inertia tensor → `physics/dynamics`
- Positions, rotations and hierarchies in the Inspector, for makers → `make/transforms-units`

**Fit.** `fits`: about 6,000 words against L (5,000). The eight ideas from zero at 500 words each, the upper value for
B0 (4,000), and the four figures (600) take the most; the two common mistakes (240), the opening (100) and the fixed
parts with the Test out box, Practice and the Coin Run item (1,100) take the rest.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:11` | concept | home | A matrix as a grid; a matrix times a vector as one dot product per row; 2×2 first. General knowledge. |
| `new:12` | concept | home | The columns of a matrix are where the axes go (basis vectors): scale and rotation in 2D from cosine and sine, their 3×3 forms, the identity matrix. Figure: the axes moved by a 2×2 matrix. General knowledge. |
| `new:13` | concept | home | Matrix multiplication combines transforms, and the order matters (turn then move against move then turn). Figure: the two orders. General knowledge. |
| `new:14` | concept | home | 4×4 matrices and w: 1 for a position, 0 for a direction; affine transforms; translation in the last column, the axes in the others. General knowledge. |
| `new:15` | concept | home | TRS: scale, then rotation, then translation (T · R · S). General knowledge. |
| `new:16` | concept | home | Coordinate spaces: local space, world space and the transform hierarchy; world = parent's world × local. Figure: a parent and its child. General knowledge. |
| `new:17` | concept | home | The inverse matrix: undoing a transform, the inverse of a product in reverse order, a local transform from world ones, the matrix without an inverse (`glm::inverse`). General knowledge. |
| `new:23` | concept | home | Conventions: column vectors and matrix order (P · V · M), column-major storage in glm, handedness and the right-hand rule, the up axis +Y, forward -Z, units in metres; recognizing another engine's convention. Figure: the right hand with Strata's axes. General knowledge. |
| `new:25` | hands-on | home | Coin Run practice, from `make/project-coin-run`'s end state: six coins as children of an empty entity that a `Spinner` turns; the world position of one coin predicted by hand (the parent's rotation times the local position, plus the parent's position) and checked in the log. Evidence: `StrataScriptCore/Include/StrataScript/Entity.h:55` (`SetParent`), `:200` (`GetWorldPosition`); `StrataEditor/src/Editor/ScriptProject.cpp:240-251` (the `Spinner`) |
| `scene-ecs:628` | term | home | Local transform and world transform, defined with the transform hierarchy |
| `scene-ecs:629` | term | home | TRS with the rotation as a quaternion; one glossary entry with `foundation:640` and `animation:535` |
| `foundation:640` | term | home | TRS; one glossary entry with the seed's |
| `animation:535` | term | home | TRS as the decomposed form of a transform; one glossary entry with the seed's |
| `foundation:139` | feature | use | Strata's conventions as `Strata/src/Strata/Math/Math.h:9-11` states them: right-handed, +Y up, -Z forward; the clip-space half is `gpu/coordinates`' |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Vectors, length, normalizing, the dot and cross products | `basics/math-vectors` | must |
| Sine, cosine and radians | `basics/math-vectors` | must |
| Functions with parameters and return values, structs | `basics/programming-2` | must |
| A script of the playground with `Log::Info` | `basics/programming-1` | must |
| Floating-point rounding | `basics/numbers` | helps |
| Positions, rotations, scales and parents in the Inspector | `make/transforms-units` | helps |

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
| `axis` | axis | - |
| `basis-vector` | basis vector | - |
| `coordinate-space` | coordinate space | coordinate system |
| `handedness` | handedness | right-handed, left-handed |
| `identity-matrix` | identity matrix | - |
| `inverse-matrix` | inverse matrix | - |
| `local-space` | local space | - |
| `local-transform` | Local transform | - |
| `matrix` | matrix | - |
| `matrix-multiplication` | matrix multiplication | - |
| `matrix-order` | matrix order | - |
| `rotation` | rotation | - |
| `scale` | scale | - |
| `transform` | transform | transformation |
| `transform-hierarchy` | transform hierarchy | - |
| `translation` | translation | - |
| `trs` | TRS | - |
| `up-axis` | up axis | - |
| `world-space` | world space | - |
| `world-transform` | world transform | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-basics-b-3 | should | shape | the Practice of all twelve pages | Each page's Practice is named only by its optional Coin Run item. No row holds the other two to seven exercises (style.md asks three to eight), nor the exercise that runs code in the playground, which track E needs and which an optional item for track B cannot be. basics-a gives each primer a row "Practice before the Coin Run item" and counts the fixed parts at 1,300 to 1,450 words; basics-b counts them at 1,100. R32 D27 asked every unit to add the missing exercises as items. | Each page gets a hands-on row for its Practice, from easy to hard, run in the playground's script and read in the Console, at least one of them run and logged (about 250 words a page, D27's measure). The Fit lines count the fixed parts again. `basics/math-matrices` (6,000), `basics/math-projection` (5,900) and `basics/math-geometry` (5,800) then reach the top of L and go to the second size pass by S5. | `allocation/basics-b.md:28`, `:101-103`, `:175`, `:253`, `:330`, `:417`, `:496`, `:570`, `:652`, `:743`, `:825`, `:925`; Fit lines `:44`, `:118`, `:269`, `:435`; `allocation/basics-a.md:192`, `:211`, `:266`, `:285`; `style.md:584`, `:598-606`; `critique/rulings-7.md:206`; `outline-1.md:242` |
| critic-basics-b-9 | should | missing-item | `new:11` and `new:12` on `basics/math-matrices`; `new:2` on `basics/math-vectors` | The pages log matrices (`basics/math-bases` logs a frame's transpose times the frame), but `Log::Info` prints numbers, text, float vectors, quaternions, entities and asset handles only: a `glm::mat3` or a `glm::uvec2` passed to it does not compile. And glm's default constructors set nothing: `glm::mat4 m;` holds whatever was in memory, not the identity, and so does `glm::vec3 v;`. No row says either. | The first code of `basics/math-matrices` logs a matrix column by column (`Log::Info(m[0], " ", m[1], " ", m[2])`), which also shows that `m[i]` is a column and `m[i][j]` its row j; a common mistake: a matrix declared without a value, with `glm::mat4(1.0f)` as the identity (about 120 words). `basics/math-vectors` adds the same for `glm::vec3(0.0f)` (about 30 words). | `allocation/basics-b.md:126-127`, `:176-179`, `:213`; `StrataScriptCore/Include/StrataScript/Log.h:21-54`; `Strata/vendor/glm/glm/detail/setup.hpp:505-511`, `:864-869`; `Strata/vendor/glm/glm/detail/type_mat4x4.hpp:35`; `Strata/vendor/glm/glm/detail/type_vec3.hpp:107` |
| critic-basics-b-10 | should | missing-item | `new:15` on `basics/math-matrices` | The page teaches T · R · S, but no row says how a script builds it. glm's `translate`, `rotate` and `scale` each multiply the matrix they are given on the right, so the code reads inside out: `glm::scale(glm::translate(glm::mat4(1.0f), p), s)` is T · S, as the Physics Playground writes it. The SDK's headers bring these functions, and `Scene::InstantiateMany` is the SDK call that takes such matrices. | Idea (5) adds TRS in code (`glm::translate`, `glm::mat4_cast` of the rotation, `glm::scale`) and the rule that each builder multiplies on the right, with `glm::rotate` in radians (about 120 words); a new `code` row with `Samples/PhysicsPlayground/Scripts/Playground.cpp:262-274`. | `allocation/basics-b.md:89`, `:130`; `Strata/vendor/glm/glm/ext/matrix_transform.inl:10-15`; `Strata/vendor/glm/glm/gtc/quaternion.hpp:18`; `Samples/PhysicsPlayground/Scripts/Playground.cpp:262-274`; `.claude/skills/strata-scripting/SKILL.md:411-414`; `StrataScriptCore/Include/StrataScript/Scene.h:192` |
| critic-basics-b-14 | could | missing-item | `new:17` and `new:25` on `basics/math-matrices` | `Entity::SetParent` keeps the world transform by default: the child's new local transform is the parent's inverse times its world transform, which is idea (7) at work. With `false` the child keeps its local numbers and moves. The Coin Run item makes coins children of an empty entity, and the reader's prediction depends on which form ran. | Idea (7) ends with `SetParent` and its second parameter as the engine's use of the inverse, and the item says which form it uses (about 50 words). | `allocation/basics-b.md:91-92`, `:132`, `:134`; `StrataScriptCore/Include/StrataScript/Entity.h:55` |
| critic-basics-b-15 | could | order | `new:119` on `basics/math-sphere` | The Coin Run item places the coins with `Scene::InstantiateMany`, which takes a list of matrices. No page on track B teaches it before: `make/scripting-scene` sends it to `make/performance`, on track G. | The item places each coin with `Scene::Instantiate` and a position, as `make/scripting-scene` teaches; or it builds the matrices with the TRS of `basics/math-matrices` and says what `InstantiateMany` does in two sentences (about 30 words). | `allocation/basics-b.md:959`; `allocation/make-a.md:1074`, `:1080`; `StrataScriptCore/Include/StrataScript/Scene.h:164`, `:188-192` |
| critic-basics-b-19 | could | missing-item | `new:23` and `foundation:139` on `basics/math-matrices` | The page is the home of axes and handedness, and it quotes `Math.h:9-11`, which says "-Z forward (glTF)". It does not say that a glTF model faces +Z, so a model needs a half turn to look along Strata's forward. Tracks G and B learn this on `make/transforms-units`; track E meets it only on the optional `start/coming-from`. | Idea (8) adds one sentence: imported models face +Z, while cameras, lights and `GetForward` look along -Z; `Math.h`'s "(glTF)" is read as glTF's axes and cameras (about 40 words). | `allocation/basics-b.md:93-95`, `:133`, `:139`; `Strata/src/Strata/Math/Math.h:9-11`; `allocation/make-a.md:324`, `:362`; `allocation/make-c.md:322`; `allocation/start.md:457`; `outline-1.md:266` |
