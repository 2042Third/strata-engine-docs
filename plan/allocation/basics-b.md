# Allocation: basics-b

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

## `basics/math-projection` — Cameras and projection: perspective, homogeneous coordinates and depth

**Covers.** In order: (1) the camera as an entity with a transform, view space (the camera at the origin, looking
along -Z), and the view matrix as the inverse of the camera's world transform; (2) perspective by similar triangles: a
point's place on the image plane is x divided by its distance, so far things look smaller; the field of view and the
aspect ratio, and tan(fov / 2) as the half-height of the picture at a distance of 1 (the mathematics behind the recipe
of `make/gameplay-math`); from a direction to a point on the screen; a cube face as a square view with a 90° field of
view, six of which see every direction; (3) homogeneous coordinates: the projection matrix writes the distance to
divide by into w, its result is clip space, and the perspective divide gives normalized device coordinates (NDC), with
x and y from -1 to 1 and +Y up, then pixels, with row 0 at the top; (4) depth: the near plane and the far plane, the
view frustum that they and the field of view bound (a pyramid with its top cut off), the depth buffer that keeps the
nearest surface for each pixel, and why depth after the divide is not spread evenly over the distance; (5) reversed Z:
the near plane stored at 1 and the far plane at 0, and in one paragraph why this suits floating-point numbers, which are
dense near 0 (the precision plot, Strata's depth precision and the far plane at infinity are named with their page,
`gpu/coordinates`); (6) the orthographic projection, where nothing gets
smaller with distance (shadow maps, side views); (7) going back: from a pixel and its depth to a position in view space
(the inverse projection), and the ray through a pixel, read in the Physics Playground's `GetPointerRay`. The page uses
the conventions of `style.md` §4 (NDC +Y up, depth from 0 to 1, reversed Z, origin at the top left) and says that other
graphics APIs differ, with a link to `reference/notation`.

Figures: similar triangles from the side, the frustum with its six sides, depth after the divide against distance, NDC
to pixels. The common mistakes: a field of view in degrees where radians go, the aspect ratio inverted, a near plane at
0, depth read as a distance, a depth range of -1 to 1 expected. Practice (three to eight exercises, `style.md` §8) ends
with the optional Coin Run item: count the coins the camera sees, by taking each coin's offset from the camera along
the camera's right, up and forward (three dot products) and testing it against tan(fov / 2) and the aspect ratio.
"Where the book uses it" names `gpu/coordinates`, `draw/bounds-culling`, `light/shadow-basics` and `image/taa`.

**Leaves out.**

- Strata's clip space, the viewport flip, the precision plot of reversed Z, depth precision in the engine and the far plane at infinity → `gpu/coordinates`
- `PerspectiveReverseZ`, `PerspectiveReverseZInfinite`, `OrthographicReverseZ` and `Ray::FromNDC` in code → `core/math`
- Planes, and testing spheres and boxes against the frustum's planes → `basics/math-geometry`
- Extracting the frustum's planes from a matrix, and culling → `draw/bounds-culling`
- Jitter and reprojection with the previous frame's matrices → `image/taa`
- Cube shadow maps → `light/local-shadows`
- The camera's lens and field of view, for makers → `make/look`
- Cube maps as a way to store directions → `basics/math-sphere`

**Fit.** `fits`: about 5,900 words against L (5,000). The seven ideas take the most: six from zero at 500 words each,
the upper value for B0, and reversed Z, now the mapping and one paragraph on floats, at 300 (3,300). The four figures
(600), the five common mistakes (600), the pointer-ray excerpt (200), the opening (100) and the fixed parts with the
Test out box, Practice and the Coin Run item (1,100) take the rest.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:26` | concept | home | The view matrix and view space: the camera at the origin, looking along -Z; the view matrix as the inverse of the camera's world transform. General knowledge. |
| `new:27` | concept | home | Perspective by similar triangles: the image plane, the field of view, the aspect ratio, tan(fov / 2); a direction to a point on the screen; a cube face as a 90° square view. Figure: similar triangles. General knowledge. |
| `new:28` | concept | home | Homogeneous coordinates and the projection matrix: clip space, the perspective divide, normalized device coordinates, then pixels. Figure: NDC to pixels. General knowledge. |
| `new:29` | concept | home | Depth: the near plane, the far plane, the view frustum, the depth buffer, depth that is not linear in distance. Figures: the frustum, depth after the divide against distance. General knowledge. |
| `new:30` | concept | home | Reversed Z as mathematics: the near plane at 1 and the far plane at 0, and in one paragraph why it suits floats, which are dense near 0. The precision plot, Strata's depth precision and the far plane at infinity are `gpu/coordinates`' (book.md's row of projection). General knowledge. |
| `new:31` | concept | home | The orthographic projection, which keeps sizes at every distance. General knowledge. |
| `new:32` | concept | home | Going back: the inverse projection from a pixel and its depth to a position, and the ray through a pixel. General knowledge. |
| `new:33` | hands-on | home | Coin Run practice, from `make/project-coin-run`'s end state: count the coins the camera sees from the offset along the camera's right, up and forward and from tan(fov / 2) and the aspect ratio. Evidence: `StrataScriptCore/Include/StrataScript/Entity.h:227-229` (`GetForward`, `GetRight`, `GetUp`), `StrataScriptCore/Include/StrataScript/Game.h:95` (`GetWindowSize`), `Samples/PhysicsPlayground/Scripts/Playground.cpp:200` (the camera's `PerspectiveFOV` in degrees) |
| `foundation:633` | term | home | NDC, after the projection and the divide; one glossary entry with the seed's and `render-core:728` |
| `render-core:728` | term | home | Clip space and NDC as the GPU part's glossary words them: the coordinates after the projection, then after the division by w, x and y from -1 to 1; one glossary entry each with the seed's and `foundation:633`; Strata's convention stays on `gpu/coordinates` |
| `foundation:634` | term | home | Reversed Z, near at 1 and far at 0, for the precision of floats; one glossary entry with the seed's and the four items of the next row |
| `render-core:730`, `editor-core:733`, `render-direct:716`, `render-scene:608` | term | home | Reversed Z as the GPU, editor, lighting and drawing parts word it (depth 1 at the near plane and 0 at the far plane; nearer to the light is larger; the farthest is the smallest value); one glossary entry with `foundation:634` and the seed's; the precision argument stays on `gpu/coordinates` |
| `render-scene:593` | term | home | The frustum as the volume the camera sees, bounded by six planes; homed here, where the seed homes the view frustum, and tested against on `basics/math-geometry` |
| `gamedev:382` | code | use | `Playground::GetPointerRay` (`Samples/PhysicsPlayground/Scripts/Playground.cpp:183-207`): a pixel taken back to a direction from the field of view, the aspect ratio and the camera's axes; its home is `make/gameplay-math` |
| `foundation:370` | code | link | The reversed-Z projections of `Math.cpp` 71-91, which `core/math` walks through |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Matrices, the inverse, 4×4 matrices with w, local and world space | `basics/math-matrices` | must |
| Vectors, the dot product, sine, cosine, the tangent function and radians | `basics/math-vectors` | must |
| Floating-point numbers, whose spacing grows with their size | `basics/numbers` | must |
| A pixel and a frame | `start/what-an-engine-is` | helps |
| The camera entity in the editor | `make/look` | helps |

**Starting state.** The optional Coin Run item of Practice starts from the download of `make/project-coin-run`'s end
state, as the outline's introduction of part `basics` says for every primer after `basics/debugging`: Coin Run as
`make/project-coin-run` finishes it, with the rolling ball, the spinning coins, the HUD, the sounds, winning, losing and
the restart. The page's other examples and exercises run in the playground (`style.md` §8), which is no checkpoint.

## `basics/math-rotations` — Rotations and quaternions

**Covers.** In order: (1) Euler angles: yaw, pitch and roll as turns around the up, the side and the forward axis, the
order in which they apply, and how Strata shows them (degrees in the Inspector; radians in scripts, where
`GetEulerAngles` and `SetEulerAngles` hold pitch, yaw and roll); (2) a direction from yaw and pitch, the two angles of
an orbit camera, named as the spherical coordinates that `basics/math-sphere` measures from the up axis; (3) gimbal lock,
shown with the pitch at 90°, and why blending Euler angles takes strange paths; (4) axis and angle: a rotation as one
axis and the angle to turn around it (`glm::angleAxis`), and the rotation matrix it gives; (5) quaternions: four numbers,
the axis times sin(θ / 2) and cos(θ / 2), why half the angle, unit length and normalizing, the identity; (6) combining
by multiplying: the `Spinner`'s `turn * transform.GetRotation()` applies the turn around the world's axis, the other
order around the entity's own; rotating a direction with `q * v`; the conjugate as the inverse; (7) q and -q, the
double cover: two quaternions for one rotation, and comparing rotations by the absolute value of their dot product, as
Strata's math code does; (8) interpolating rotations: slerp, which blends by a weight from 0 to 1 at an even speed,
nlerp as the cheaper approximation, and the shorter arc (one quaternion negated when the dot product is negative);
(9) converting between Euler angles, axis and angle, matrices and quaternions, with a table of what each is good for;
(10) angular velocity as a vector: its direction the axis and its length the rate in radians per second
(`RigidBody::GetAngularVelocity`), and turning by it in one small step.

Figures: the three Euler turns on a model aeroplane, gimbal lock, the half angle of a quaternion, slerp's arc against
lerp's chord, the shorter and the longer arc. The common mistakes: degrees where radians go, multiplying in the wrong
order, a blend not normalized, blending q with -q (a spin the long way round), quaternions compared number by number.
Practice (three to eight exercises, `style.md` §8) ends with the optional Coin Run item: coins that spin around a tilted
axis with `glm::angleAxis`, and an arrow above the ball that turns smoothly toward the nearest coin with `glm::slerp`
toward `Motion::LookAt`'s rotation. "Where the book uses it" names `world/interpolation`, `animation/blending`,
`physics/dynamics` and `editor-ui/inspectors`.

**Leaves out.**

- Strata's rotation helpers in code (`EulerDegreesToQuat`, `LookRotation`, `IsNearlyEqual`) → `core/math`
- The interpolated transforms drawn between fixed steps → `world/interpolation`
- Blending many rotations, and `AnimationMath::Slerp` with its nlerp fallback → `animation/blending`
- Integrating angular velocity in the physics step → `physics/dynamics`
- Solid angles and spherical coordinates measured from the up axis → `basics/math-sphere`
- Rotations with the Inspector and the gizmo, for makers → `make/transforms-units`
- The Inspector's Euler fields and how an edit keeps the quaternion → `editor-ui/inspectors`
- Dual quaternions → `animation/skinning`

**Fit.** `over`: about 7,700 words against L (5,000). The ten ideas from zero at 500 words each, the upper value for B0
(5,000), the five figures (750), the five common mistakes (600), the `Spinner`'s two lines (150), the opening (100) and
the fixed parts with the Test out box, Practice and the Coin Run item (1,100). A primer is at most L, so the page
splits (S3): `basics/math-rotations`, "Rotations: Euler angles, axis and angle, and gimbal lock" (M, about 3,600: ideas
1 to 4), and after it `basics/math-quaternions`, "Quaternions: combining, normalizing and slerp" (L, about 5,300: ideas
5 to 10, the conversions with them because they end in quaternions).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:34` | concept | home | Euler angles: yaw, pitch and roll, their order; degrees in the Inspector, radians in scripts. Figure: the three turns. General knowledge. |
| `new:35` | concept | home | A direction from yaw and pitch, the two angles of an orbit camera (spherical coordinates measured from the horizon). General knowledge. |
| `new:36` | concept | home | Gimbal lock, and why Euler angles blend badly. Figure: two axes lined up. General knowledge. |
| `new:37` | concept | home | Axis and angle (`glm::angleAxis`), and the rotation matrix of an axis and an angle. General knowledge. |
| `new:38` | concept | home | Quaternions: the axis times sin(θ / 2) and cos(θ / 2), unit length, normalizing, the identity. Figure: the half angle. General knowledge. |
| `new:39` | concept | home | Combining rotations by multiplying, and the order (around the world's axes or the entity's own); rotating a direction (`q * v`); the conjugate as the inverse. General knowledge. |
| `new:40` | concept | home | The double cover: q and -q are one rotation; comparing rotations by the absolute value of their dot product. General knowledge. |
| `new:41` | concept | home | Interpolating rotations: slerp, nlerp, and the shorter arc. Figure: slerp's arc, the shorter and the longer arc. General knowledge. |
| `new:42` | concept | home | Converting between Euler angles, axis and angle, matrices and quaternions; a table of what each is good for. General knowledge. |
| `new:43` | concept | home | Angular velocity as a vector (an axis with a rate in radians per second), and turning by it in a small step. General knowledge. |
| `new:44` | hands-on | home | Coin Run practice, from `make/project-coin-run`'s end state: coins spun around a tilted axis with `glm::angleAxis`, and an arrow that turns toward the nearest coin with `glm::slerp` to `Motion::LookAt`'s rotation. Evidence: `StrataEditor/src/Editor/ScriptProject.cpp:249-250` (`glm::angleAxis` and the turn), `StrataScriptCore/Include/StrataScript/Gameplay.h:229` (`Motion::LookAt`), `StrataScriptCore/Include/StrataScript/Entity.h:184-191` (`SetRotation`, `SetEulerAngles`) |
| `animation:254` | concept | home | Quaternions for rotation: why not Euler angles (gimbal lock, bad blends) or matrices, unit quaternions, the double cover, normalization; Strata's `AnimationMath::Normalize` stays on `animation/skeletons` |
| `animation:536` | term | home | Quaternion; one glossary entry with `foundation:638` and the seed's |
| `animation:537` | term | home | Slerp and nlerp, two entries |
| `scene-ecs:684` | term | home | Nlerp, normalized linear interpolation of quaternions, as the scene part's glossary words it; one glossary entry with `animation:537`'s nlerp; `world/interpolation` links |
| `animation:574` | term | home | Yaw; one glossary entry with the seed's yaw angle |
| `foundation:638` | term | home | Quaternion, q and -q the same rotation |
| `foundation:639` | term | home | Euler angles as pitch, yaw and roll |
| `gamedev:359` | code | use | The `Spinner`'s turn, `StrataEditor/src/Editor/ScriptProject.cpp:249-250`: `glm::angleAxis` and `turn * transform.GetRotation()`; its home is `make/first-script` |
| `foundation:142` | feature | use | Strata's rotations: Euler degrees against quaternions, forward, right and up, and `IsNearlyEqual`, which compares quaternions without their sign |
| `scripting:120` | feature | use | `TransformComponent`'s `GetEulerAngles` and `SetEulerAngles` in radians (pitch, yaw, roll), `GetRotation` and `SetRotation` |
| `scripting:125` | feature | use | `RigidBody::GetAngularVelocity`, an angular velocity as one vector |
| `animation:538` | term | link | The quaternion hemisphere (the shorter arc), defined on `animation/blending` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Matrices, columns as axes, combining transforms in order | `basics/math-matrices` | must |
| The transpose, and the inverse of a rotation as its transpose | `basics/math-bases` | must |
| Vectors, length, normalizing, the dot and cross products | `basics/math-vectors` | must |
| Sine, cosine, radians and `atan2` | `basics/math-vectors` | must |
| A script of the playground with `Log::Info` | `basics/programming-1` | must |
| Rotations with the Inspector and the gizmo | `make/transforms-units` | helps |

**Starting state.** The optional Coin Run item of Practice starts from the download of `make/project-coin-run`'s end
state, as the outline's introduction of part `basics` says for every primer after `basics/debugging`: Coin Run as
`make/project-coin-run` finishes it, with the rolling ball, the spinning coins, the HUD, the sounds, winning, losing and
the restart. The page's other examples and exercises run in the playground (`style.md` §8), which is no checkpoint.

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

## `basics/math-change` — Change over time: rates, accumulation, Euler steps and Newton's laws

**Covers.** Every idea comes first as a table of numbers and a graph, and only then as a formula. In order: (1) a rate
of change from a table: positions written down every second, the change per second, the slope of the graph; (2) the
derivative as the rate at one moment, found from shorter and shorter intervals, then its notation read aloud; (3)
accumulation: from a table of speeds back to the distance, rectangles under the graph, and the integral as the area
under it (named here, used again by `basics/math-probability`); accumulating small steps along a path, as a march
through fog or air adds up light (`light/atmosphere`); (4) velocity and acceleration as vectors: velocity the rate of
change of position, acceleration the rate of change of velocity, gravity as a constant acceleration of 9.81 m/s²
downward; (5) the explicit Euler step: the position moved by the old velocity, then the velocity changed, run by hand
in a table for a falling ball; (6) the semi-implicit Euler step: the velocity first, then the position with the new
velocity, the same table for a spring, the explicit step's energy that grows and the semi-implicit step's that stays;
physics engines step this way, as Strata's does (`physics/dynamics`); (7) the size of the step: the error a larger step
brings, a step so large that the spring explodes, and why games simulate with a fixed step (its home is `core/time`);
(8) Newton's laws: a body keeps its velocity, force equals mass times acceleration, every force has an equal and
opposite one; forces in newtons, mass in kilograms; (9) momentum and impulse: mass times velocity, a hit as a large
force over a short time, an impulse that changes the velocity at once, and the SDK's `AddForce` against `AddImpulse`.

Figures: a position graph with its slope, rectangles under a speed graph, the explicit and the semi-implicit spring, a
step that explodes. The common mistakes: multiplying by `deltaTime` twice or not at all, moving by the old velocity
where the new one was meant, a varying step for physics, a force applied once as if it were an impulse. Practice
(three to eight exercises, `style.md` §8) ends with the optional Coin Run item: the ball's speed computed from its
positions in two fixed steps and logged next to `RigidBody::GetLinearVelocity`, then a jump pad that gives the ball an
upward impulse.
"Where the book uses it" names `core/time`, `physics/dynamics`, `audio/spatial` and `light/atmosphere`.

**Leaves out.**

- Exponential decay and its total over a distance, with exponential smoothing → `basics/math-interpolation`
- Lerp, easing and smoothing → `basics/math-interpolation`
- Integrals over directions and Monte Carlo estimates → `basics/math-probability`
- The fixed step, its accumulator and time scale in Strata → `core/time`
- Torque, inertia and how bodies turn → `physics/dynamics`
- Forces, impulses and velocities for makers → `make/physics`
- The Doppler effect from velocities → `audio/spatial`

**Fit.** `fits`: about 5,100 words against L (5,000). The nine ideas at 400 to 500 words take the most (4,000); the
fixed parts with the Test out box, Practice and the Coin Run item take the rest (1,100).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:56` | concept | home | A rate of change from a table of numbers, and the slope of a graph. Figure: a position graph. General knowledge. |
| `new:57` | concept | home | The derivative as the rate at one moment, from shorter and shorter intervals. General knowledge. |
| `new:58` | concept | home | Accumulation and the integral as the area under a graph; accumulating small steps along a path. Figure: rectangles under a speed graph. General knowledge. |
| `new:59` | concept | home | Velocity and acceleration as vectors; gravity as a constant acceleration. General knowledge. |
| `new:60` | concept | home | The explicit Euler method, run by hand in a table. General knowledge. |
| `new:61` | concept | home | The semi-implicit Euler method, and the energy it keeps where the explicit method adds energy. Figure: the two springs. General knowledge. |
| `new:62` | concept | home | The size of the time step: error, instability, and why simulations take fixed steps. Figure: a step that explodes. General knowledge. |
| `new:63` | concept | home | Newton's laws of motion: force, mass and acceleration; newtons and kilograms. General knowledge. |
| `new:64` | concept | home | Momentum and impulse: a hit as a large force over a short time, an impulse as an instant change of velocity. General knowledge. |
| `new:65` | hands-on | home | Coin Run practice, from `make/project-coin-run`'s end state: the ball's speed from two fixed steps' positions beside `GetLinearVelocity`; a jump pad with an upward impulse. Evidence: `StrataScriptCore/Include/StrataScript/Script.h:85` (`OnFixedUpdate`), `StrataScriptCore/Include/StrataScript/Physics.h:55` (`GetLinearVelocity`) and `:93` (`AddImpulse`) |
| `physics:511` | term | home | Impulse, an instant change of momentum, force times time; one glossary entry with the seed's |
| `scripting:125` | feature | use | The SDK's `RigidBody`: `GetLinearVelocity`, `AddForce` and `AddImpulse` |
| `physics:225` | concept | link | Rigid body state and its semi-implicit Euler step in Strata's physics; its home is `physics/dynamics` |
| `foundation:228` | concept | link | The fixed step and its accumulator; its home is `core/time` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Vectors: adding and scaling them, length | `basics/math-vectors` | must |
| Loops and `std::vector`, for tables of numbers in code | `basics/programming-2` | must |
| A script of the playground: `OnUpdate`, `deltaTime` and `Log::Info` | `basics/programming-1` | must |
| Fixed updates in a script (`OnFixedUpdate`) | `make/script-loop` | helps |
| Decimals and floating-point rounding | `basics/numbers` | helps |
| Rigid bodies, forces and impulses in the editor | `make/physics` | helps |

**Starting state.** The optional Coin Run item of Practice starts from the download of `make/project-coin-run`'s end
state, as the outline's introduction of part `basics` says for every primer after `basics/debugging`: Coin Run as
`make/project-coin-run` finishes it, with the rolling ball, the spinning coins, the HUD, the sounds, winning, losing and
the restart. The page's other examples and exercises run in the playground (`style.md` §8), which is no checkpoint.

## `basics/math-interpolation` — Blending and smoothing: lerp, easing, curves and exponential smoothing

**Covers.** In order: (1) lerp: a + (b - a) × t, its weight t from 0 to 1, the same as a weighted average whose weights
add to 1, for numbers, positions and colors (`glm::mix`); blending two values; (2) inverse lerp, remapping a value from
one range to another, and clamping; (3) smoothstep and easing functions: curves that start or end slowly, their graphs,
and which motion wants which; (4) curves through keys: a keyframe as a time and a value, step and linear interpolation
between keys, and finding the two keys around a time; (5) cubic Hermite curves, shaped by the keys' values and slopes,
and Bezier curves at the use level (control points that pull the curve); (6) bilinear and trilinear interpolation: lerps
along x, then y, then z, between the corners of a square or a cube, as a texture read or a 3D grid of values uses them;
(7) exponential decay: a quantity that loses the same fraction each second or each metre, its curve e^(-kt) with the e
of `basics/numbers`, the half-life and the time constant τ, and the total it adds up to over a distance d,
(1 - e^(-kd)) / k, as light through fog does (exponentials and their integrals); (8) exponential smoothing: moving a
fixed fraction of the remaining way toward a target in each step, why a fixed fraction per frame depends on the frame
rate, and `1 - exp(-k * dt)` (written `1 - exp(-dt / tau)` with the time constant) as the weight that does not, read in
`FollowCamera`'s smoothing line; the SDK's `Motion::SmoothDamp` named as a spring that also keeps a velocity; (9)
geometric series: after n steps that each keep a fraction r of the gap, the gap left is rⁿ, the sum 1 + r + r² + ...
is 1 / (1 - r), and how many frames a smoothed value needs to settle.

Figures: the lerp line, smoothstep with two easing curves, keys joined by step, linear and Hermite curves, bilinear
weights between four corners, decay curves stepped at 30 and at 120 frames per second against the exact curve. The
common mistakes: t outside 0 to 1 without a clamp, a fixed fraction per frame, a Hermite slope not scaled by the time
between its keys, angles lerped across 360°. Practice (three to eight exercises, `style.md` §8) ends with the optional
Coin Run item: a collected coin that rises and shrinks over half a second, its time remapped to 0 to 1 and eased with
smoothstep, and a camera that follows the ball with `1 - exp(-k * deltaTime)`, checked by a loop that simulates one
second at 30 and at 120 steps and logs both results. "Where the book uses it" names `world/interpolation`,
`animation/clips`, `image/taa`, `audio/spatial` and `light/fog`.

**Leaves out.**

- Interpolating rotations: slerp and nlerp → `basics/math-rotations`
- The exponential function and the number e → `basics/numbers`
- Strata's transforms drawn between fixed steps → `world/interpolation`
- glTF's samplers, tangents scaled by the key span, and key reduction → `animation/clips`
- Texture reads as sampling and filtering → `basics/signals`
- Smoothing recipes for a game maker's camera → `make/gameplay-math`
- Fog and how Strata draws it → `light/fog`
- The TAA history blend → `image/taa`
- Color lookup tables read with trilinear interpolation → `image/grading`

**Fit.** `fits`: about 5,400 words against L (5,000). The nine ideas at 400 to 600 words take the most (4,200); the
camera's smoothing line (100) and the fixed parts with the Test out box, Practice and the Coin Run item (1,100) take the
rest.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:66` | concept | home | Linear interpolation and its weight; a weighted average whose weights add to 1; blending numbers, positions and colors (`glm::mix`). Figure: the lerp line. General knowledge. |
| `new:67` | concept | home | Inverse linear interpolation, remapping and clamping. General knowledge. |
| `new:68` | concept | home | Smoothstep and easing functions. Figure: smoothstep and two easing curves. General knowledge. |
| `new:69` | concept | home | Keyframes, and step and linear interpolation between them; finding the two keys around a time. General knowledge. |
| `new:70` | concept | home | Cubic Hermite curves from values and slopes; Bezier curves at the use level. Figure: step, linear and Hermite curves through the same keys. General knowledge. |
| `new:71` | concept | home | Bilinear and trilinear interpolation between the corners of a square and a cube. Figure: the four bilinear weights. General knowledge. |
| `new:72` | concept | home | Exponential decay: the same fraction lost per second or per metre, e^(-kt), the half-life, the time constant, and its total over a distance, (1 - e^(-kd)) / k. General knowledge. |
| `new:73` | concept | home | Exponential smoothing, and frame-rate independence with `1 - exp(-k * dt)`. Figure: decay stepped at 30 and 120 frames per second. General knowledge. |
| `new:74` | concept | home | Geometric series: the gap left after n steps, the sum 1 / (1 - r), the frames a smoothed value needs to settle. General knowledge. |
| `new:75` | hands-on | home | Coin Run practice, from `make/project-coin-run`'s end state: a collected coin that rises and shrinks over half a second (inverse lerp, smoothstep, lerp), a follow camera with `1 - exp(-k * deltaTime)`, and one second simulated at 30 and at 120 steps. Evidence: `StrataScriptCore/Include/StrataScript/Entity.h:177-198` (`SetTranslation`, `SetScale`), `Samples/ThirdPerson/Scripts/FollowCamera.cpp:79` (the smoothing weight) |
| `animation:541` | term | home | Key and keyframe, a time and the value of a channel; one glossary entry with the seed's |
| `audio-input:649` | term | home | Exponential smoothing by `1 - exp(-dt / tau)`; one glossary entry with the seed's |
| `gamedev:378` | code | use | Line 79 of `Samples/ThirdPerson/Scripts/FollowCamera.cpp`, the weight `1 - exp(-FollowSharpness * deltaTime)`; the whole camera is `make/characters-cameras`' |
| `scripting:136` | feature | use | `Motion::SmoothDamp`, a critically damped spring that keeps its velocity between calls |
| `render-image:673` | term | link | Trilinear interpolation as the grading's lookup table reads it, on `image/grading`; the general entry, trilinear interpolation, is this page's at the glossary step (basics-b-q8) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The exponential function and the number e | `basics/numbers` | must |
| Powers and fractions | `basics/numbers` | must |
| Rates, accumulation and the area under a graph | `basics/math-change` | must |
| Vectors: adding and scaling them | `basics/math-vectors` | must |
| A script of the playground: `OnUpdate`, `deltaTime` and `Log::Info` | `basics/programming-1` | must |
| Loops and functions | `basics/programming-2` | must |
| Moving an entity from a script (`SetTranslation`) | `basics/math-vectors` | must |

**Starting state.** The optional Coin Run item of Practice starts from the download of `make/project-coin-run`'s end
state, as the outline's introduction of part `basics` says for every primer after `basics/debugging`: Coin Run as
`make/project-coin-run` finishes it, with the rolling ball, the spinning coins, the HUD, the sounds, winning, losing and
the restart. The page's other examples and exercises run in the playground (`style.md` §8), which is no checkpoint.

## `basics/color` — Color and light for programmers: linear, sRGB and HDR

**Covers.** In order: (1) a color as numbers: red, green and blue color channels from 0 to 1, stored in a file as 0 to
255 each (RGBA8, eight bits per channel, the display colors of a picture or a thumbnail), and alpha as a fourth channel
for opacity; (2) linear color: values in proportion to the amount of light, so that adding two lights adds their values
and averaging works; (3) why pictures are not stored that way: the eye tells more dark shades apart, so 256 levels
spread evenly over the light would band in the shadows; gamma encoding, quantization and banding; (4) the sRGB
transfer function, exactly (the straight piece below 0.0031308 and the 2.4 power above it), decoding and encoding, read
in Strata's `LinearToSRGB` and `SRGBToLinear`; which data is sRGB (photographs, base colors, UI colors) and which is
linear (normal maps, roughness, masks), and why blending and filtering work on linear values; (5) high dynamic range:
scene-linear values with no top limit (the sun is thousands of times brighter than a white wall), which need floating
point; (6) half floats: 16 bits, values up to 65504, about three significant digits, and the subnormal values below
2^-14 that lose precision; (7) luminance: how bright a color looks, the weighted sum 0.2126 R + 0.7152 G + 0.0722 B of
linear Rec. 709 values, read in Strata's `Luminance`, against luma, the same kind of sum on encoded values; (8)
chromaticity: what a color is apart from its brightness, two numbers x and y on the horseshoe diagram of the colors the
eye sees; (9) primaries, white point and gamut: a color space as three primaries, a white (D65, daylight) and a transfer
function; Rec. 709 and sRGB share their primaries and white; colors outside a gamut; (10) the working color space:
Strata lights in scene-linear Rec. 709, and changing from one color space to another is a 3×3 matrix applied to
(r, g, b).

Figures: an 8-bit ramp stored linearly and in sRGB (banding in the first), the sRGB curve, a 50% blend done on linear
and on sRGB values, the chromaticity diagram with the Rec. 709 triangle and D65. The common mistakes: blending or
filtering sRGB values, a normal map marked as sRGB, a luma compared with a luminance, HDR values clamped at 1 too early.
Practice (three to eight exercises, `style.md` §8) ends with the optional Coin Run item: the time bar's color blended
from green to red, once on the sRGB values that UI colors are and once in linear (decode, lerp, encode), with the
luminance of each midpoint logged. "Where the book uses it" names `assets/textures`, `image/why-post`,
`image/tone-mapping`, `image/encoding` and `ui/drawing`.

**Leaves out.**

- Light units: lux, nits and exposure → `light/units-exposure`
- HDR targets, the post chain and pre-exposure in Strata → `image/why-post`
- Tone mapping from scene light to the screen → `image/tone-mapping`
- White balance and color grading → `image/grading`
- Quantizing the final picture, its dither and the 10-bit path → `image/encoding`
- sRGB texture formats and how the GPU decodes them → `assets/textures`
- Floating point and its bits → `basics/numbers`
- Dithering as an idea of signals → `basics/signals`
- Premultiplied alpha → `light/clearcoat-transmission`
- The editor's palette and theme tokens → `editor-ui/design-system`

**Fit.** `over`: about 7,500 words against L (5,000). The ten ideas from zero at 500 words each, the upper value for B0
(5,000), the four figures (600), the four common mistakes (480), the sRGB and `Luminance` excerpts (250), the opening
(100) and the fixed parts with the Test out box, Practice and the Coin Run item (1,100). A primer is at most L, so the
page splits (S3): `basics/color`, "Color for programmers: linear, sRGB and HDR" (L, about 5,900: ideas 1 to 7), and
after it `basics/color-spaces`, "Color spaces: chromaticity, white point, gamut and the working space" (M, about 2,900:
ideas 8 to 10, with the 3×3 matrix).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:76` | concept | home | Color channels from 0 to 1 and from 0 to 255 (RGBA8), and alpha as opacity. General knowledge. |
| `new:77` | concept | home | Linear color: values in proportion to light, which add and average. General knowledge. |
| `new:78` | concept | home | Gamma encoding, quantization and banding: why 8-bit pictures are not linear. Figure: a ramp stored linearly and in sRGB. General knowledge. |
| `new:79` | concept | home | The sRGB transfer function, decoding and encoding; sRGB data against linear data; blending and filtering on linear values. Figures: the sRGB curve, a 50% blend both ways. General knowledge. |
| `new:80` | concept | home | High dynamic range and scene-linear values. General knowledge. |
| `new:81` | concept | home | Half floats: range, precision and subnormals. General knowledge. |
| `new:82` | concept | home | Luminance as a weighted sum of linear Rec. 709 values, against luma on encoded values. General knowledge. |
| `new:83` | concept | home | Chromaticity: x and y, the diagram of visible colors. Figure: the chromaticity diagram. General knowledge. |
| `new:84` | concept | home | Primaries, white point and gamut; a color space; Rec. 709 and sRGB. General knowledge. |
| `new:85` | concept | home | The working color space, Strata's being scene-linear Rec. 709 (the primaries of sRGB), and a change of color space as a 3×3 matrix. Evidence: `Strata/src/Strata/Renderer/PostProcessMath.h:62` ("scene-linear sRGB light"), `Strata/shaders/Include/Exposure.slang:18-21` (luminance weights of linear Rec. 709) |
| `new:86` | hands-on | home | Coin Run practice, from `make/project-coin-run`'s end state: the time bar's color blended from green to red on sRGB values and in linear, with the luminance of both midpoints logged. Evidence: `StrataScriptCore/Include/StrataScript/UI.h:75` (UI colors are display sRGB values) and `:86` (`SetColor`) |
| `assets:712` | term | home | sRGB, the nonlinear encoding of color images, and why filtering happens on linear values; one glossary entry with the seed's |
| `render-image:675` | term | home | The sRGB transfer function, the piecewise 2.4 power; one glossary entry with the seed's transfer function |
| `render-direct:703` | term | home | Half float, RGBA16F and subnormals below 2^-14; one glossary entry with `render-image:638`, `render-core:757` and the seed's |
| `render-image:638` | term | home | Half float: largest value 65504, about three decimal digits |
| `render-core:757` | term | home | Half float (RGBA16F) as the GPU part's glossary words it: the 16-bit floating-point channel format of HDR targets, largest value 65504; one glossary entry with `render-direct:703` and `render-image:638`; `gpu/frame-tour` links |
| `render-image:642` | term | home | Luminance (Y), 0.2126 R + 0.7152 G + 0.0722 B of linear Rec. 709 values, shown with Strata's `Luminance` (`Strata/shaders/Include/Exposure.slang:18-21`) |
| `render-image:670` | term | home | D65, sRGB's white point (6504 K daylight) |
| `render-image:130` | feature | use | Strata's sRGB encoding and decoding, `Strata/shaders/Include/Common.slang:25-39`, read as the formula's code; its home is `image/encoding` |
| `gameui:52` | feature | use | The game UI's colors are display (sRGB) values, the space of the Coin Run item's blend |
| `editor-ui:60` | feature | use | The editor's palette as named sRGB tokens, an example of display colors with alpha |
| `render-image:643` | term | link | Luma as FXAA weighs encoded values, on `image/spatial-aa`; the general entry, luma, is this page's at the glossary step (basics-b-q8) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Bits and 8-bit unsigned integers (0 to 255) | `basics/numbers` | must |
| Floating-point numbers: sign, exponent and fraction; precision | `basics/numbers` | must |
| Powers and exponents | `basics/numbers` | must |
| A 3×3 matrix applied to three numbers | `basics/math-matrices` | must |
| A weighted sum of three numbers as a dot product | `basics/math-vectors` | helps |
| Lerp: blending two values by a weight | `basics/math-interpolation` | helps |
| A pixel | `start/what-an-engine-is` | helps |
| A script of the playground with `Log::Info` | `basics/programming-1` | must |
| A UI element's color set from a script | `make/hud` | helps |

**Starting state.** The optional Coin Run item of Practice starts from the download of `make/project-coin-run`'s end
state, as the outline's introduction of part `basics` says for every primer after `basics/debugging`: Coin Run as
`make/project-coin-run` finishes it, with the rolling ball, the spinning coins, the HUD, the sounds, winning, losing and
the restart. The page's other examples and exercises run in the playground (`style.md` §8), which is no checkpoint.

## `basics/signals` — Sampling, aliasing and filtering

**Covers.** In order: (1) a signal and its samples: the brightness along a row of pixels, the pressure of a sound,
measured at separate places or moments; frequency as repeats per second or per metre, with the sine wave of
`basics/math-vectors`; (2) sampling and the sample rate, and reading between samples again: nearest reads and linear
reads, bilinear in two dimensions (bilinear filtering of a texture), whose mathematics `basics/math-interpolation`
taught; (3) the Nyquist limit and aliasing: a frequency above half the sample rate shows up as a false, lower one (a
wheel that turns backward on film, moiré on a fine fence, stair steps along edges, shimmer as the camera moves), and why
sound is sampled 48,000 times a second; (4) filtering: a weighted average of nearby samples, the filter kernel (box,
tent, Gaussian) whose weights add to 1, and convolution as sliding the kernel along the signal; (5) prefiltering:
filtering before sampling, so that nothing above the limit is left; mips as prefiltered copies of a picture, each half
the size of the one before, and choosing the mip whose texels match the pixel; (6) resampling a picture with a filter:
a box filter against a wider one (Strata's texture cooker makes its mips with a Mitchell filter on linear values); (7)
quantization and dithering: rounding to 256 levels bands, and a small planned offset added first turns the bands into
fine grain; ordered dither with the 4×4 Bayer table, which Strata also uses to fade between two levels of detail; (8)
spatial denoising: averaging each pixel with similar neighbors, with weights that stop at edges.

Figures: a sine sampled above and below the Nyquist limit, a checkered floor drawn with and without mips, one signal
under a box, a tent and a Gaussian kernel, a gradient quantized, dithered with noise and with the Bayer table, the Bayer
table itself. The common mistakes: filtering after sampling, a kernel whose weights do not add to 1, a mip chain built
from sRGB values, a dither that changes every frame where a still picture is wanted. Practice (three to eight
exercises, `style.md` §8) ends with the optional Coin Run item: a coin turned by 350° each frame (not scaled by
`deltaTime`) seems to turn 10° backward each frame, the wagon wheel of aliasing; the reader predicts what 370° and 180°
per frame look like, then tries them. "Where the book uses it" names `assets/textures`, `image/spatial-aa`,
`light/shadow-basics`, `indirect/ao` and `audio/sound-in-a-computer`.

**Leaves out.**

- Mips, texture reads and their filters in Strata → `assets/textures`
- How Strata cooks mips → `assets/texture-cooking`
- Anti-aliasing methods: FXAA, morphological AA and TAA → `image/spatial-aa`
- The final picture's dither → `image/encoding`
- Noise and sampling patterns → `basics/math-probability`
- The LOD cross-fade and its masks → `draw/lod`
- The edge-aware blurs of shadows → `light/sun-shadows-2`
- Sound as samples in Strata's audio → `audio/sound-in-a-computer`
- Lerp and bilinear interpolation as mathematics → `basics/math-interpolation`

**Fit.** `fits`: about 5,100 words against L (5,000). The eight ideas at 400 to 600 words take the most (3,800); the
Bayer excerpt (200) and the fixed parts with the Test out box, Practice and the Coin Run item (1,100) take the rest.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:87` | concept | home | Signals and signal samples; frequency. General knowledge. |
| `new:88` | concept | home | Sampling and the sample rate; nearest, linear and bilinear reads between samples. General knowledge. |
| `new:89` | concept | home | The Nyquist limit and aliasing: false low frequencies, moiré, stair steps, shimmer. Figure: a sine sampled above and below the limit. General knowledge. |
| `new:90` | concept | home | Filtering, filter kernels (box, tent, Gaussian) and convolution. Figure: one signal under three kernels. General knowledge. |
| `new:91` | concept | home | Prefiltering, and mips as prefiltered copies of a picture; choosing a mip. Figure: a floor with and without mips. General knowledge. |
| `new:92` | concept | home | Resampling a picture with a filter: box against wider filters. General knowledge. |
| `new:93` | concept | home | Quantization and dithering; ordered dither with the 4×4 Bayer table. Figure: a gradient quantized, dithered and ordered-dithered. General knowledge. |
| `new:94` | concept | home | Spatial denoising: averaging similar neighbors, weights that stop at edges. General knowledge. |
| `new:95` | hands-on | home | Coin Run practice, from `make/project-coin-run`'s end state: a coin turned by a fixed angle per frame (350°, 370°, 180°) to see aliasing at the frame rate. Evidence: `StrataEditor/src/Editor/ScriptProject.cpp:246-250` (the `Spinner`'s turn in `OnUpdate`) |
| `render-image:691` | term | home | Aliasing: artifacts from undersampling (stair steps, crawling, shimmer); one glossary entry with the seed's |
| `render-scene:605` | term | home | Ordered dither and the Bayer matrix, a fixed 4×4 pattern of thresholds 0 to 15; one glossary entry with the seed's |
| `render-scene:360` | code | use | The Bayer table of `IsLODFadeDrawn`, `Strata/shaders/Include/Scene.slang:155-166`, read as an ordered dither; the fade itself is `draw/lod`'s |
| `assets:155` | feature | use | Strata's texture cooker: mips filtered with a Mitchell filter on linear values |
| `assets:716` | term | link | The Mitchell and the box filter, defined on `assets/texture-cooking` |
| `render-image:677` | term | link | Dither and TPDF, as the final picture's encoding uses them, on `image/encoding`; dither's idea and the seed's entry stay this page's (book.md's row of display encoding; basics-b-q8) |
| `render-direct:737` | term | link | The edge-aware (bilateral) blur, defined on `light/sun-shadows-2` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Sine waves, their amplitude and period | `basics/math-vectors` | must |
| Lerp, weighted averages and bilinear interpolation | `basics/math-interpolation` | must |
| Quantization to 8 bits, banding, linear and sRGB values | `basics/color` | must |
| Powers of two and the base-2 logarithm (the number of mips) | `basics/numbers` | must |
| A pixel and a frame | `start/what-an-engine-is` | helps |
| A script of the playground: `OnUpdate` and `Log::Info` | `basics/programming-1` | must |

**Starting state.** The optional Coin Run item of Practice starts from the download of `make/project-coin-run`'s end
state, as the outline's introduction of part `basics` says for every primer after `basics/debugging`: Coin Run as
`make/project-coin-run` finishes it, with the rolling ball, the spinning coins, the HUD, the sounds, winning, losing and
the restart. The page's other examples and exercises run in the playground (`style.md` §8), which is no checkpoint.

## `basics/math-probability` — Chance: probability, noise, integrals and Monte Carlo

**Covers.** In order: (1) probability: a number from 0 to 1, counted from equally likely cases (a die), the chances of
cases that cannot both happen added, those of independent events multiplied; (2) random variables and probability
distributions: a list of values with their chances, the uniform distribution, and for values on a range the probability
density, whose area over a part of the range is that part's chance; (3) the expected value and the mean, and the spread:
the variance and the standard deviation, computed from a table of samples (the spread that `image/taa` measures); (4)
pseudo-random numbers and seeds: a fixed rule that gives a sequence that looks random, the seed that starts it, read in
the SDK's `Random` (PCG32: the state update, the output's shift and rotation, `NextFloat`, and `Range`, which draws again
instead of using a biased remainder); (5) integrals as areas, recalled from `basics/math-change`; (6) Monte Carlo
integration: the average of a function at random points times the size of the range, with an error that falls as one
over the square root of the number of points, worked by darts in a quarter circle that estimate π; (7) importance
sampling: more samples where the function is large, each divided by its density, with a cosine-shaped density as the
example (cosine weighting); (8) white noise and blue noise: clumps and gaps against an even spread, why blue noise looks
finer, and Strata's 64×64 blue-noise table, made by void and cluster; (9) low-discrepancy sequences: the Hammersley set,
whose second coordinate reverses the bits of the index (Strata's two-line `Hammersley`), and stratified offsets, one
random point in each cell of a grid; (10) disk patterns: the Vogel disk, points on a spiral each turned by the golden
angle, and Poisson disk sampling, random points never closer than a set distance; (11) interleaved gradient noise: a
cheap value per pixel, computed from the pixel's position, whose neighbors differ evenly (Strata's
`InterleavedGradientNoise`).

Figures: a histogram of the sums of two dice, a density with an area shaded, darts in a quarter circle, white against
blue noise, Hammersley points against random points, the Vogel spiral. The common mistakes: `rand() % n` and its bias,
a seed from the clock in a test, a Monte Carlo estimate not divided by the density, white noise where blue noise is
wanted, a generator seeded again every frame. Practice (three to eight exercises, `style.md` §8) ends with the optional
Coin Run item: the coins placed at random with `Random` and a seed, so that one seed always gives the same level, and
`Chance(0.25)` to make some of them gold; the gold coins over 1,000 seeds are counted and compared with the expected
value. "Where the
book uses it" names `make/recipes`, `light/energy`, `light/sun-shadows-2`, `indirect/problem` and `engineering/testing`.

**Leaves out.**

- Random numbers and seeds in a game maker's recipes → `make/recipes`
- Integrals over directions and the hemisphere → `basics/math-sphere`
- Sampling the GGX lobe, and filtered importance sampling → `indirect/ibl`
- The BRDF table and its samples → `light/energy`
- The sun's filter: the Vogel disk turned by fixed blue noise → `light/sun-shadows-2`
- The Poisson taps of local shadows → `light/local-shadows`
- Halton jitter → `image/taa`
- The engine's own `Random` → `core/math`
- How the blue-noise table is generated and checked → `engineering/generated-code`
- Rates and accumulation → `basics/math-change`

**Fit.** `over`: about 8,300 words against L (5,000). Ten ideas from zero at 500 words each, the upper value for B0, and
idea (5), integrals as areas recalled from `basics/math-change`, at 200 (5,200); the six figures (900), the five common
mistakes (600), the PCG32 excerpt (250), the `Hammersley` and noise excerpts (150), the opening (100) and the fixed
parts with the Test out box, Practice and the Coin Run item (1,100). A primer is at most L, so the page splits (S3):
`basics/math-probability`, "Chance: probability, random numbers, integrals and Monte Carlo" (L, about 6,300: ideas 1 to
7 and 9, so that Hammersley and stratified offsets stand beside the estimates they improve), and after it
`basics/noise-patterns`, "Noise patterns: blue noise, the Vogel and Poisson disks and interleaved gradient noise" (M,
about 3,200: ideas 8, 10 and 11).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:96` | concept | home | Probability from equally likely cases; adding exclusive cases, multiplying independent events. Figure: the sums of two dice. General knowledge. |
| `new:97` | concept | home | Random variables, probability distributions, the uniform distribution, probability density. Figure: a density with an area shaded. General knowledge. |
| `new:98` | concept | home | The expected value, the mean, the variance and the standard deviation. General knowledge. |
| `new:99` | concept | home | Pseudo-random number generators and seeds; uniform ranges and the bias of a remainder. General knowledge. |
| `new:100` | concept | use | Integrals as areas, recalled for estimating them: the integral as accumulation is `basics/math-change`'s (its row `new:58`; book.md's row of change over time). General knowledge. |
| `new:101` | concept | home | Monte Carlo integration and its error, one over the square root of the count. Figure: darts in a quarter circle. General knowledge. |
| `new:102` | concept | home | Importance sampling: samples where the function is large, divided by their density; cosine weighting. General knowledge. |
| `new:103` | concept | home | White noise and blue noise. Figure: the two side by side. General knowledge. |
| `new:104` | concept | home | Low-discrepancy sequences: the Hammersley set by bit reversal; stratified offsets. Figure: Hammersley against random points. General knowledge. |
| `new:105` | concept | home | The Vogel disk and the golden angle; Poisson disk sampling. Figure: the Vogel spiral. General knowledge. |
| `new:106` | concept | home | Interleaved gradient noise. General knowledge. |
| `new:107` | code | home | `Strata/shaders/Include/IBL.slang:36-39`: `Hammersley`, the index over the count and the index with its 32 bits reversed (`reversebits`) |
| `new:108` | hands-on | home | Coin Run practice, from `make/project-coin-run`'s end state: coins placed with a seeded `Random`, some made gold by `Chance(0.25)`, counted over 1,000 seeds against the expected value. Evidence: `StrataScriptCore/Include/StrataScript/Gameplay.h:26-38` (the seed) and `:81-104` (`Range`, `Chance`) |
| `scripting:383` | code | home | `StrataScriptCore/Include/StrataScript/Gameplay.h:19-110`: the SDK's `Random`, PCG32 (XSH-RR): `Seed`, `NextUInt`'s state update, shift and rotation, `Range` drawing again below the threshold, `NextFloat`, `Chance` |
| `scripting:600` | term | home | PCG32, a small, fast and statistically good pseudo-random number generator |
| `scripting:343` | concept | use | Two parts of the SDK's determinism helpers, read in `scripting:383`: the seeded PCG32 and the unbiased range by rejection (`StrataScriptCore/Include/StrataScript/Gameplay.h:62-70`, a value below the threshold drawn again); the concept's home is `make/recipes` |
| `render-direct:734` | term | home | Vogel disk, a spiral by the golden angle; one glossary entry with `render-image:721` and the seed's |
| `render-image:721` | term | home | Vogel (golden-angle) disk, an evenly spread spiral |
| `render-direct:735` | term | home | Blue noise, noise without low frequencies; one glossary entry with the seed's |
| `render-indirect:584` | term | home | Hammersley sequence; one glossary entry with the seed's |
| `render-indirect:618` | term | home | Interleaved gradient noise (IGN); one glossary entry with the seed's |
| `render-core:459` | code | use | `InterleavedGradientNoise` in `Strata/shaders/Include/Common.slang:41-46`, read as the formula's code; the excerpt's home is `gpu/shaders` |
| `build-test:227` | feature | use | `Tools/GenerateBlueNoise.py`, which makes the 64×64 blue-noise table by void and cluster |
| `render-direct:123` | feature | link | The sun's soft-shadow filter, a Vogel disk turned by blue noise, on `light/sun-shadows-2` |
| `render-indirect:583` | term | link | Importance sampling and filtered importance sampling, the item's home row on `indirect/ibl`; the glossary step gives "importance sampling" to this page, which teaches it (`new:102`), and "filtered importance sampling" to `indirect/ibl` (R48) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Integrals as accumulation: the area under a graph | `basics/math-change` | must |
| Binary, bits, shifts, masks and the exclusive or | `basics/numbers` | must |
| Unsigned 32-bit and 64-bit integers, and overflow that wraps | `basics/numbers` | must |
| Sampling, frequency and aliasing | `basics/signals` | must |
| Sine, cosine and radians | `basics/math-vectors` | must |
| Loops, functions and `std::vector` | `basics/programming-2` | must |
| A class kept as a member of a script | `basics/programming-3` | helps |
| A script of the playground with `Log::Info` | `basics/programming-1` | must |
| Random numbers in a game maker's recipes | `make/recipes` | helps |

**Starting state.** The optional Coin Run item of Practice starts from the download of `make/project-coin-run`'s end
state, as the outline's introduction of part `basics` says for every primer after `basics/debugging`: Coin Run as
`make/project-coin-run` finishes it, with the rolling ball, the spinning coins, the HUD, the sounds, winning, losing and
the restart. The page's other examples and exercises run in the playground (`style.md` §8), which is no checkpoint.

## `basics/math-sphere` — Directions on a sphere: solid angles, spherical harmonics and octahedral maps

**Covers.** In order: (1) directions as points on the unit sphere, and spherical coordinates: the polar angle from the
up axis and the azimuth around it (the yaw and pitch of `basics/math-rotations`, but measured from up), converted both
ways with sine, cosine, `acos` and `atan2`; (2) storing a value for every direction in a picture: the equirectangular
map with its rows of equal angle, and why it stretches at the poles (Strata's `DirectionToEquirect` guards
`atan2(0, 0)`); (3) cube maps: six square faces, the face chosen by the largest coordinate of the direction, and the
point on that face; (4) octahedral maps: the sphere wrapped in an eight-sided shape and unfolded into one square, and
the octahedral encoding of a unit vector into two numbers, read in Strata's `OctahedralEncode` and `OctahedralDecode`,
which store normals; (5) solid angle: the area a patch of directions covers on the unit sphere, the steradian, 4π for
the whole sphere and 2π for a hemisphere, the solid angle of a cone from its angular radius, 2π (1 - cos α), and of a
small disk such as the sun; (6) integrals over the sphere and the hemisphere: a value times the small solid angle of
each piece, added up, why a piece near the pole is smaller (sin θ), the cosine-weighted integral over a hemisphere that
equals π, the solid angle of one texel of a cube map, and directions drawn with a cosine-weighted density, read in
Strata's `SampleCosineHemisphere` (the Monte Carlo of `basics/math-probability`, on a sphere); (7) basis functions: a few
fixed patterns that, weighted and added, approximate a more complex one, first along a line; (8) spherical harmonics: the
patterns of bands 0, 1 and 2, nine coefficients, projecting a function onto them (the integral of the function times
each pattern) and evaluating it back, why they hold only light that changes slowly with direction, and the ringing that
can make values negative.

Figures: the polar angle and the azimuth on a sphere, an equirectangular map with its stretched poles, a cube map
unfolded, the octahedron unfolded, a cone's solid angle, the nine patterns of spherical harmonics. The common mistakes:
sin θ forgotten in a sum over the sphere, the poles of an equirectangular map, a normal stored as three numbers where
two would do, too few bands for sharp light. Practice (three to eight exercises, `style.md` §8) ends with the optional
Coin Run item: coins spread over a dome above the start, evenly by area, with the cosine of the polar angle drawn
uniformly by `Random`, against polar angles drawn uniformly, which bunch the coins at the top. "Where the book uses
it" names `light/units-exposure`, `light/sky`, `indirect/ibl`, `indirect/probes` and `indirect/gi-cascades`.

**Leaves out.**

- Radiance, irradiance and light units → `light/units-exposure`
- Strata's cube face conventions and its equirectangular captures → `indirect/ibl`
- Strata's probes with nine coefficients, their band factors and clamping → `indirect/probes`
- The GI field's octahedral probes → `indirect/gi-cascades`
- The normal buffer and screen-space reflections → `indirect/ssr`
- The sky's directions and the atmosphere's tables → `light/sky`
- Monte Carlo integration → `basics/math-probability`
- Yaw and pitch → `basics/math-rotations`

**Fit.** `fits`: about 5,200 words against L (5,000). The eight ideas at 300 to 600 words take the most (3,700); the
three short excerpts (450) and the fixed parts with the Test out box, Practice and the Coin Run item (1,100) take the
rest.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:109` | concept | home | The unit sphere of directions; spherical coordinates (polar angle and azimuth) and their conversions. Figure: the two angles. General knowledge. |
| `new:110` | concept | home | Equirectangular maps and their poles. Figure: an equirectangular map. General knowledge. |
| `new:111` | concept | home | Cube maps: six faces, the face from the largest coordinate. Figure: a cube map unfolded. General knowledge. |
| `new:112` | concept | home | Octahedral maps and the octahedral encoding of a unit vector. Figure: the octahedron unfolded. General knowledge. |
| `new:113` | concept | home | Solid angle, the steradian, a hemisphere, the solid angle of a cone from its angular radius. Figure: a cone's solid angle. General knowledge. |
| `new:114` | concept | home | Integrals over the sphere and the hemisphere: sin θ, the cosine-weighted integral equal to π, texel solid angles, cosine-weighted directions. General knowledge. |
| `new:115` | concept | home | Basis functions, first along a line. General knowledge. |
| `new:116` | concept | home | Spherical harmonics: bands 0 to 2, nine coefficients, projecting and evaluating, low frequencies only, ringing. Figure: the nine patterns. General knowledge. |
| `new:117` | code | home | `Strata/shaders/Include/Scene.slang:362-377`: `OctahedralEncode` and `OctahedralDecode`, a unit vector folded onto the octahedron and unfolded into [-1, 1]², and back |
| `new:118` | code | home | `Strata/shaders/Include/IBL.slang:59-65`: `SampleCosineHemisphere`, a cosine-weighted direction from two numbers, sin θ as the square root of one of them, turned into the normal's frame |
| `new:119` | hands-on | home | Coin Run practice, from `make/project-coin-run`'s end state: coins on a dome, evenly by area (the cosine of the polar angle uniform) against bunched (the angle uniform). Evidence: `StrataScriptCore/Include/StrataScript/Gameplay.h:81` (`Range` for floats), `StrataScriptCore/Include/StrataScript/Scene.h:192` (`InstantiateMany` with transforms) |
| `render-indirect:572` | term | home | Solid angle in steradians, 4π for the sphere; one glossary entry with the seed's |
| `render-indirect:585` | term | home | Spherical harmonics, nine coefficients in bands 0 to 2; one glossary entry with the seed's |
| `render-indirect:611` | term | home | Octahedral encoding, a unit vector in two numbers; beside the seed's octahedral map |
| `render-indirect:245` | concept | use | Strata's cube faces and equirectangular mapping, `DirectionToEquirect` (`Strata/shaders/Include/IBL.slang:28-34`) read for the pole; its home is `indirect/ibl` |
| `render-indirect:341` | code | link | The projection onto nine coefficients with texel solid angles, walked through on `indirect/ibl` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Monte Carlo integration and probability densities | `basics/math-probability` | must |
| Integrals as areas | `basics/math-change` | must |
| Sine, cosine, radians and `atan2` | `basics/math-vectors` | must |
| Vectors, length, normalizing and the dot product | `basics/math-vectors` | must |
| Random numbers with a seed (the SDK's `Random`) | `basics/math-probability` | must |
| Yaw and pitch as a direction | `basics/math-rotations` | helps |
| A cube face as a 90° view | `basics/math-projection` | helps |
| A frame of three axes as a matrix's columns, and a direction carried from a normal's frame to the world (tangent space) | `basics/math-bases` | helps |
| A script of the playground with `Log::Info` | `basics/programming-1` | must |

**Starting state.** The optional Coin Run item of Practice starts from the download of `make/project-coin-run`'s end
state, as the outline's introduction of part `basics` says for every primer after `basics/debugging`: Coin Run as
`make/project-coin-run` finishes it, with the rolling ball, the spinning coins, the HUD, the sounds, winning, losing and
the restart. The page's other examples and exercises run in the playground (`style.md` §8), which is no checkpoint.

## Passed on

none

## Not taken

none

## Questions for the planner

none
