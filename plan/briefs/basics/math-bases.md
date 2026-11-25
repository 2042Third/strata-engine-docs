# Brief: `basics/math-bases`

| Field | Value |
| --- | --- |
| Title | Bases, determinants and normals: orthonormal frames, tangent space, mirrors and the inverse transpose |
| Kind | P |
| Size | M |
| Tracks | B, E |
| Needs | `basics/math-matrices` |
| From | new by split of `basics/math-matrices`, which could not hold both lessons at a primer's size; foundation "The math toolkit" (the mathematics: bases); the transpose and orthonormal bases (`Motion::LookAt`), changing basis and tangent space (`TangentBasis`), the determinant and its sign as a mirror, normals through the inverse transpose and the cofactor matrix, decomposing a matrix into translation, rotation and scale and when it fails |
| Unit | `plan/allocation/basics-b.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `basics/math-bases` — Bases, determinants and normals: orthonormal frames, tangent space, mirrors and the inverse transpose

**Covers.** The page opens with its own Test out box: five questions on this page's ideas alone. In order: (1) the
transpose and orthonormal bases: the transpose turns rows into columns; three columns of length 1 at right angles to
each other are an orthonormal basis; for a rotation the inverse is the transpose; `Motion::LookAt` builds the three
axes of a rotation with two cross products and puts them in a matrix's columns; (2) changing basis: three vectors such
as a surface's tangent, bitangent and normal as a space of their own (tangent space), with directions taken from it to
world space and back, read in Strata's `TangentBasis`; (3) the determinant: how much a transform scales areas and
volumes, its sign as a mirror (a negative determinant turns the winding of faces), zero as a transform that flattens
and has no inverse, and how it is computed from the rows; (4) normals through the inverse transpose: why a non-uniform
scale bends normals, the fix (the normal matrix, the inverse transpose of the 3×3 part), and the cofactor matrix, whose
columns are cross products of the other columns, the determinant times the inverse transpose, which needs no division
and turns a normal around under a mirror; (5) decomposing a matrix into translation, rotation and scale: TRS cannot
hold a shear, a mirror becomes a negative scale on one axis that must be chosen, and a zero scale leaves no rotation to
find. Every idea starts from the matrices of `basics/math-matrices`: the columns as where the axes go, the product and
the inverse.

Figure: a normal bent by a squashing scale. The common mistakes: normals transformed by the model matrix under a
non-uniform scale, inverting a matrix whose determinant is zero. Practice (three to eight exercises, `style.md` §8)
ends with the optional Coin Run item: a frame that faces a coin from the ball, built by hand with two cross products
as `Motion::LookAt` builds it and shown by three markers one metre along its axes; the log shows that the frame is
orthonormal (its transpose times it is the identity, its determinant 1), carries a point from the frame's coordinates
to the world and back with the transpose, and shows the determinant turn to -1 when two axes are swapped. "Where the
book uses it" names `draw/mirrors-camera-relative`, `light/materials`, `physics/building-bodies` and
`animation/skinning`.

**Leaves out.**

- Rotations as Euler angles and quaternions, and a rotation matrix turned into a quaternion → `basics/math-rotations`
- Normal maps and tangent space in Strata's materials → `light/materials`
- Mirrored instances, the normal matrix in shaders and camera-relative space → `draw/mirrors-camera-relative`
- The receiver-plane depth bias from the inverse transpose of the light's projection → `light/shadow-basics`
- Normals of skinned vertices through the cofactor → `animation/skinning`
- Strata's `DecomposeTransform`, which folds a mirror into the x scale and loses a shear → `core/math`, `world/scene-graph`
- World scale baked into collision shapes, and bodies whose transforms are degenerate → `physics/building-bodies`

**Fit.** `over`: about 4,400 words against M (3,000). The five ideas from zero at 500 words each, the upper value for
B0 (2,500), the `TangentBasis` excerpt (300), the figure of the bent normal (150), the two common mistakes (240), the
opening (100) and the fixed parts with the Test out box, Practice and the Coin Run item (1,100); the normal matrix, the
cofactor matrix, decomposition and the erratum stand inside ideas (4) and (5) and add no section. At or over M's top,
so the next size is L (5,000), by S2.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:18` | concept | home | The transpose and orthonormal bases: the inverse of a rotation is its transpose; a basis built from two cross products. General knowledge. |
| `new:19` | concept | home | Changing basis: tangent, bitangent and normal as tangent space, and directions taken from it to world space and back. General knowledge. |
| `new:20` | concept | home | The determinant: the factor of areas and volumes, its sign as a mirror that turns the winding of faces, zero as flattening; computed from the rows. General knowledge. |
| `new:21` | concept | home | Normals through the inverse transpose (the normal matrix), and the cofactor matrix built from cross products of the columns, the determinant times the inverse transpose. Taught from zero here, so the page is the glossary home of the normal matrix and the cofactor matrix (R43, R46). Figure: a normal bent by a squashing scale. General knowledge. |
| `render-scene:646` | term | home | Cofactor matrix: the matrix whose columns are cross products of pairs of columns, the determinant times the inverse transpose, which carries normals without a division and turns them around under a mirror; homed here, where it is taught from zero (R43), and used on `draw/mirrors-camera-relative` |
| `render-core:740` | term | home | Normal matrix: the matrix that carries normals under a non-uniform scale, the inverse transpose of the 3×3 part; an entry of its own beside the cofactor matrix's (`render-scene:646`), which this inventory names with it and which is one way to build it (R46) |
| `new:22` | concept | home | Decomposing a matrix into translation, rotation and scale: TRS cannot hold a shear, a mirror becomes a negative scale on one chosen axis, and a zero scale leaves no rotation to find. Taught from zero here, so the page is the glossary home of decomposition (R43). General knowledge. |
| `scene-ecs:630` | term | home | Decomposition (of a transform): recovering translation, rotation and scale from a matrix; one glossary entry (R46). Its definition is corrected (critic-scene-ecs-1): TRS cannot hold a shear, and Strata's `DecomposeTransform` fails for zero scale and non-finite values while a shear is lost; what the function does is `world/scene-graph`'s |
| `new:121` | erratum | home | `plan/inventory/scene-ecs.md:293` and `:630` say that decomposing a matrix fails for shear (process.md's table of errata). The page states the mathematics, that TRS cannot hold a shear, and never that the engine's function fails for it. Evidence: `Strata/src/Strata/Math/Math.cpp:12-33` and `:46-48` (it fails only for non-finite values, a homogeneous w near zero and a scale axis near zero), `:39-44` (a mirror folded into a negative X scale), `:35-37` and `:46` (a quaternion made of the normalized columns as they are, so a shear is dropped without a word) |
| `new:24` | code | home | `Strata/shaders/Include/IBL.slang:41-48`: `TangentBasis`, a tangent frame from two cross products, put in a matrix whose constructor takes rows and is transposed, so that the three vectors end up as columns |
| `new:120` | hands-on | home | Coin Run practice, from `make/project-coin-run`'s end state: a frame that faces a coin from the ball, built by hand with two cross products (right, up and back) as `Motion::LookAt` builds it, shown by three markers one metre along its axes; the dot products of its axes, their lengths, its transpose times it and its determinant logged; a point carried from the frame's coordinates to the world and back with the transpose; the determinant -1 once two axes are swapped. Evidence: `StrataScriptCore/Include/StrataScript/Gameplay.h:229-248` (`Motion::LookAt`), `StrataScriptCore/Include/StrataScript/Entity.h:200` (`GetWorldPosition`) and `:177-182` (`SetTranslation`), `StrataScriptCore/Include/StrataScript/Scene.h:116` (`FindEntityByName`), `StrataScriptCore/Include/StrataScript/Entity.h:6` (`glm/glm.hpp`, which declares `glm::mat3`, `glm::transpose` and `glm::determinant`) |
| `scripting:136` | feature | use | `Motion::LookAt` (`StrataScriptCore/Include/StrataScript/Gameplay.h:229-248`): right and up from two cross products, and the matrix whose columns are right, up and back |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Matrices: a matrix times a vector, the columns as where the axes go, the product and its order, 4×4 matrices with w, local and world space, the inverse, column-major storage in glm | `basics/math-matrices` | must |
| Vectors, length, normalizing, the dot and cross products, a triangle's normal from two of its edges | `basics/math-vectors` | must |
| Functions with parameters and return values, structs | `basics/programming-2` | must |
| A script of the playground with `Log::Info` | `basics/programming-1` | must |
| Floating-point rounding: lengths that are almost 1, a determinant that is almost 0 | `basics/numbers` | helps |

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
| `cofactor-matrix` | Cofactor matrix | - |
| `decomposition-of-a-transform` | Decomposition (of a transform) | - |
| `normal-matrix` | Normal matrix | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-basics-b-4 | should | order | `new:24` (`basics/math-bases`); `render-image:130`, `render-image:642` (`basics/color`); `render-scene:360` (`basics/signals`); `new:107`, `render-core:459` (`basics/math-probability`); `new:117`, `new:118`, `render-indirect:245` (`basics/math-sphere`) | Five pages quote Strata's shaders, which are written in Slang. No page before them teaches how to read Slang: `gpu/shaders` does, after part `basics` on track E and never on track B. No Assumes row names it, and style.md has a rule for Python fences but none for shader fences. The quotes rest on what differs from C++ and glm: `float3`, `float3x3` whose constructor takes rows (the point of `TangentBasis`), `mul`, swizzles such as `.yx`, `frac`, `select`, `reversebits`. | The first shader quote of each of the five pages is introduced by two or three sentences on what in it differs from C++ and glm, and each shader quote is followed by its explanation line by line, as R31 asks of Python (about 60 words a page). See forPlanner for a rule in style.md §9.1. | `allocation/basics-b.md:212`, `:697`, `:699`, `:779`, `:868`, `:878`, `:957-958`, `:963`; `allocation/gpu.md:189`, `:238`; `style.md:634-636`, `:679`; `tracks.md:208`; `Strata/shaders/Include/IBL.slang:41-48`; `Strata/shaders/Include/Common.slang:25-39`; `Strata/shaders/Include/Scene.slang:362-377` |
| critic-basics-b-9 | should | missing-item | `new:11` and `new:12` on `basics/math-matrices`; `new:2` on `basics/math-vectors` | The pages log matrices (`basics/math-bases` logs a frame's transpose times the frame), but `Log::Info` prints numbers, text, float vectors, quaternions, entities and asset handles only: a `glm::mat3` or a `glm::uvec2` passed to it does not compile. And glm's default constructors set nothing: `glm::mat4 m;` holds whatever was in memory, not the identity, and so does `glm::vec3 v;`. No row says either. | The first code of `basics/math-matrices` logs a matrix column by column (`Log::Info(m[0], " ", m[1], " ", m[2])`), which also shows that `m[i]` is a column and `m[i][j]` its row j; a common mistake: a matrix declared without a value, with `glm::mat4(1.0f)` as the identity (about 120 words). `basics/math-vectors` adds the same for `glm::vec3(0.0f)` (about 30 words). | `allocation/basics-b.md:126-127`, `:176-179`, `:213`; `StrataScriptCore/Include/StrataScript/Log.h:21-54`; `Strata/vendor/glm/glm/detail/setup.hpp:505-511`, `:864-869`; `Strata/vendor/glm/glm/detail/type_mat4x4.hpp:35`; `Strata/vendor/glm/glm/detail/type_vec3.hpp:107` |
