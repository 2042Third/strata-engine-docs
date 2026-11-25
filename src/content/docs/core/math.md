---
id: core/math
title: "Strata's math toolkit"
description: "The small set of math types and functions that all of Strata shares: transforms, reversed-Z projections, rotations, boxes, rays and random numbers."
kind: internals
size: M
tracks: [E]
needs: [basics/math-rotations, basics/math-projection, basics/math-geometry, core/conventions]
time: 55
learn:
  - id: projections
    text: compute the depth that Strata's infinite reversed-Z projection gives a point at a distance
  - id: ray-from-ndc
    text: build a ray from a pixel and explain why `Ray::FromNDC` uses the depths 1 and 0.5
  - id: decompose
    text: predict what `DecomposeTransform` returns for a mirrored or a broken matrix
  - id: quaternion-equality
    text: explain why `IsNearlyEqual` compares quaternions by their dot product
  - id: world-compose
    text: explain why the scene composes world matrices in one function
since: 0.3.0
status: final
---

Every part of Strata that moves, aims, draws or picks something needs the same few mathematical tools. The library in
`Strata/src/Strata/Math/` is that shared set: functions that build and split transforms, build projections, turn
angles into rotations and test boxes and rays, plus a random number generator. It is a thin layer over the glm library.
It does not teach the mathematics, which the :term[primers]{id=primer} do, and it does not decide how the camera or the scene works.

## The problem and how engines solve it

The mathematics of vectors, matrices, rotations, projections and intersections is the subject of the primers:
[matrices](../basics/math-matrices.md), [rotations](../basics/math-rotations.md), [projection](../basics/math-projection.md)
and [geometry](../basics/math-geometry.md). An engine has a different problem: many programmers write code that must
agree. They have to agree on an axis convention, on which :term[matrix order]{id=matrix-order} to use, and on the range of the depth. Each
disagreement is a bug that shows only in the picture. Engines solve this with one small library that owns every choice
once, so the rest of the code calls it and never repeats a formula.

## The map

The library is five files over glm. The functions of `Math.h` live in the :term[namespace]{id=namespace} `Strata::Math`; the types `AABB`,
`Frustum`, `Ray` and `Random` live in `Strata`. Nothing in them keeps state except `Random`, whose generator belongs to
each thread, so every function is safe to call from any thread.

```mermaid caption="Every file builds on glm, and the ray and frustum files also build on boxes. The scene code calls the world matrix function and the editor calls the ray function." alt="A diagram. A box for glm points to the transform file, the box file and the random file. The box file points to the frustum file and the ray file. Scene code points to the transform file and editor placement points to the ray file."
flowchart LR
  glm["glm: vectors, matrices, quaternions"]
  math["Math.h: transforms, projections, rotations"]
  aabb["AABB.h: boxes"]
  frustum["Frustum.h: the camera's volume of sight"]
  ray["Ray.h: rays and hit tests"]
  random["Random.h: random numbers"]
  scene["Scene, interpolation and physics"]
  editor["Editor placement"]
  glm --> math
  glm --> aabb
  glm --> random
  aabb --> frustum
  aabb --> ray
  scene --> math
  editor --> ray
```

## The contract

Callers may assume the conventions below, and every function obeys them. Each rule has its reason.

### One set of conventions

The comment at the top of `Math.h` states them once. Coordinates are :term[right-handed]{id=handedness}, +Y is up and the camera looks down
−Z, as in glTF. :term[Clip space]{id=clip-space} follows the Direct3D layout that the graphics library NVRHI offers on every backend: +Y is up in :term[normalized
device coordinates]{id=normalized-device-coordinates} and depth runs from 0 to 1. Strata uses :term[reversed Z]{id=reversed-z}, so the :term[near plane]{id=near-plane} has depth 1 and the :term[far plane]{id=far-plane}
has depth 0. [Coordinates and conventions](../gpu/coordinates.md) is the home of these choices; this page only follows
them.

The mistakes this prevents are old ones. A matrix read by rows instead of columns, a 0-to-1 depth treated like OpenGL's
−1-to-1 depth, and a standard projection used with a reversed depth test each draw a wrong picture without any error.
glm stores matrices by columns, and the library keeps that.

### Transforms

`ComposeTransform` builds the matrix of a translation, a rotation and a scale. `DecomposeTransform` splits a matrix
back into the three. Four cases make it return `false` and leave its outputs untouched. A value is not finite, the last element is near 0, a
column has a length near 0, or the rotation it finds is not finite.
A caller therefore keeps its old values for broken input.

A mirrored matrix, with an odd number of negative scale axes, has no rotation that reproduces it. The function folds the
mirror into X: the scale of X becomes negative and the rotation absorbs the rest. For a scale of (1, −1, 1) it returns
(−1, 1, 1) and a half turn about Z. The rebuilt matrix is the same, but the parts differ from what you put in.

`ComposeWorldTransform(parentWorld, local)` is the product `parentWorld * local` and nothing more. It lives in
`Math.cpp` on purpose: every path of the scene that needs a child's world matrix calls this one compiled copy.

:::why[One function for one product]
A :term[compiler]{id=compiler} may fuse a multiply and an add into one instruction, which rounds once instead of twice. Where the same
product is inlined into different callers, the compiler can fuse it differently in each, and two results that must be
equal differ in the last bit. The scene's cached matrices, the check that computes them again, the drawn transforms
under a parent and the physics write-back all call `ComposeWorldTransform`, so they cannot disagree. The cost is a
:term[function call]{id=function-call} on a hot path. The other cure, forbidding fused instructions in the whole engine, changes all of its arithmetic;
[Flags and portability](../engineering/flags-portability.md) tells the build option that does it.
:::

### Projections

`PerspectiveReverseZ` takes the vertical :term[field of view]{id=field-of-view} in :term[radians]{id=radian}, the aspect ratio and the near and far distances.
`OrthographicReverseZ` takes the six edges of the box it keeps. Both map the near plane to depth 1 and the far plane to 0.
`PerspectiveReverseZInfinite` takes no far distance: its infinite far plane is a far plane at infinity, which depth 0
reaches only in the limit. [Coordinates and conventions](../gpu/coordinates.md) gives the reason and the precision it buys.

For the infinite projection the depth is $near / d$, where $d$ is the distance in front of the camera. With a near
distance of 0.5, a point 4 units away has depth 0.125 and a point 4,000 units away has 0.000125. No distance gives 0, so
nothing is cut off by distance.

### Rotations

Rotations are glm :term[quaternions]{id=quaternion}. `EulerDegreesToQuat` and `QuatToEulerDegrees` convert from and to degrees: pitch about X,
:term[yaw]{id=yaw-angle} about Y and roll about Z. A yaw of 90 degrees turns the forward direction −Z into −X. `GetForwardDirection`,
`GetRightDirection` and `GetUpDirection` rotate −Z, +X and +Y.

`LookRotation(direction, up)` returns the rotation that points −Z along the direction and keeps the up direction near +Y. A zero
direction gives the identity. When you look almost straight along the up hint, the :term[cross product]{id=cross-product} of the two would
collapse, so the function swaps the hint: +Y when the direction is not near vertical, +Z when it is. Looking straight down
therefore gives a rotation whose up direction is +Z.

`IsNearlyEqual` compares numbers, vectors and quaternions within an :term[epsilon]{id=tolerance} of 1e-5 unless you pass another. The
quaternion version takes the absolute value of the :term[dot product]{id=dot-product} and checks that it is near 1. A quaternion and its negative
are one rotation, and comparing their four components one by one would call them different.

### Boxes, rays and random numbers

An `AABB` (:term[axis-aligned bounding box]{id=axis-aligned-bounding-box}) is empty when default-constructed: its minimum is the largest float and its maximum
the lowest, so the first `Expand` sets both. `IsValid` tells an empty box from a real one, and `Contains` and
`Intersects` are closed tests. `Transformed` returns the smallest axis-aligned box around the transformed box, by Arvo's
method: it moves the center and sums the absolute values of the matrix's basis times the extents. A box turned by 45
degrees about Z, from −1 to 1 on each axis, becomes one from −1.414 to 1.414 on X and Y. The result never shrinks back.

A `Ray` holds an origin and a :term[normalized]{id=normalization} direction. The tests return the distance to the first hit or `std::nullopt`.
`IntersectRayAABB` uses slabs, the space between the box's two planes on each axis, and reports 0 for a ray that starts inside. `IntersectRaySphere` reports the exit distance
for a ray inside.

`IntersectRayPlane` takes a plane as normal and distance. `IntersectRayTriangle` is the
Möller and Trumbore test, with an option to skip back faces. [Geometry](../basics/math-geometry.md) teaches the
mathematics. A `Frustum`, the camera's pyramid of sight, is a type of the library too; [Bounds and
culling](../draw/bounds-culling.md) is where it is used.

`Random` keeps one `std::mt19937_64` generator per thread, seeded from `std::random_device`. `Seed` seeds only the calling
thread, so a run that must repeat seeds each thread it uses. `Float` is in [0, 1), `Int` includes both ends and swaps a reversed
pair, and `UnitVector` is uniform on the sphere. The scripts' `Random` is a different class in the software development kit (SDK) for scripts; see
[Recipes](../make/recipes.md).

## A toy version

The job of the toy is the one the editor does when you click: turn a pixel into a ray. Start with real numbers. The
camera is at the origin and looks down −Z. The vertical field of view is 90 degrees, the aspect ratio is 1 and the near
distance is 1.

:::example[A ray from the point (0.5, 0.25)]
The projection gives a point at distance $d$ the depth $1 / d$. Take the pixel at normalized device coordinates (0.5,
0.25). The depth 1 is the near plane, at distance 1. There the point is (0.5, 0.25, −1): with a 90 degree field of view and an aspect ratio of 1, x and y
are the coordinates times the distance.

The depth 0.5 is distance 2, and the point is (1, 0.5, −2). The line through the two is
the ray.

Its direction, from the first point to the second and then divided by its length 1.1456, is
(0.4364, 0.2182, −0.8729). The depth 0 would need distance infinity, which no number holds: that is why a second
point at depth 0.5 is used.
:::

The sketch below does the same with glm alone. It builds the :term[projection matrix]{id=projection-matrix} by hand, as `PerspectiveReverseZInfinite`
does, prints the depth of four distances on the view axis, and then turns the pixel back into points at depths 1 and 0.5. Look at the
last line: at depth 0 the fourth coordinate is 0, and dividing by it would give infinity.

```cpp sketch="core-math-toy.cpp"
// A ray from a pixel through an infinite reversed-Z projection, with glm alone: the depths 1 and 0.5 give two points.
#include <cstdio>
#include <glm/glm.hpp>

namespace
{
	// The matrix of an infinite reversed-Z projection: the depth is near / distance.
	glm::mat4 MakeProjection(float verticalFov, float aspect, float nearClip)
	{
		const float focal = 1.0f / glm::tan(verticalFov * 0.5f);
		glm::mat4 result(0.0f);
		result[0][0] = focal / aspect;
		result[1][1] = focal;
		result[2][3] = -1.0f;
		result[3][2] = nearClip;
		return result;
	}

	glm::vec3 Unproject(const glm::mat4& inverse, const glm::vec2& ndc, float depth)
	{
		const glm::vec4 point = inverse * glm::vec4(ndc, depth, 1.0f);
		return glm::vec3(point) / point.w;
	}
}

int main()
{
	const glm::mat4 projection = MakeProjection(glm::radians(90.0f), 1.0f, 1.0f);

	for (const float distance : { 1.0f, 2.0f, 100.0f, 1.0e6f })
	{
		const glm::vec4 clip = projection * glm::vec4(0.0f, 0.0f, -distance, 1.0f);
		std::printf("distance %9.0f -> depth %.6f\n", distance, clip.z / clip.w);
	}

	const glm::mat4 inverse = glm::inverse(projection);
	const glm::vec2 ndc(0.5f, 0.25f);
	const glm::vec3 origin = Unproject(inverse, ndc, 1.0f);
	const glm::vec3 target = Unproject(inverse, ndc, 0.5f);
	const glm::vec3 direction = glm::normalize(target - origin);
	std::printf("origin    (%.4f, %.4f, %.4f)\n", origin.x, origin.y, origin.z);
	std::printf("target    (%.4f, %.4f, %.4f)\n", target.x, target.y, target.z);
	std::printf("direction (%.4f, %.4f, %.4f)\n", direction.x, direction.y, direction.z);
	std::printf("w at depth 0: %.4f\n", (inverse * glm::vec4(ndc, 0.0f, 1.0f)).w);
}
```

```text output-of="core-math-toy.cpp"
distance         1 -> depth 1.000000
distance         2 -> depth 0.500000
distance       100 -> depth 0.010000
distance   1000000 -> depth 0.000001
origin    (0.5000, 0.2500, -1.0000)
target    (1.0000, 0.5000, -2.0000)
direction (0.4364, 0.2182, -0.8729)
w at depth 0: 0.0000
```

1. **Lines 7–17:** the matrix. Only the near distance appears; the far plane is not in it at all.
2. **Lines 19–23:** the way back. The :term[inverse matrix]{id=inverse-matrix} turns a normalized device point into a point with four coordinates; dividing
   by the fourth coordinate gives the position.
3. **Lines 30–34:** distances 1, 2, 100 and a million give depths 1, 0.5, 0.01 and 0.000001, the formula $near / d$.
4. **Lines 38–40:** the two points of the ray, as in the example. The direction is their difference, normalized.
5. **Line 44:** the fourth coordinate at depth 0 is 0, so no finite point exists there.

The toy ignores the camera's position and orientation. The real code has to put them back, and that is only a matter of
the matrix you invert.

## The real code

The projections are three short functions. Find the one line each of them depends on: the swapped arguments, the row
that divides by distance, and the single near value of the infinite one.

```cpp src="Strata/src/Strata/Math/Math.cpp#L71-L91"
glm::mat4 PerspectiveReverseZ(float verticalFov, float aspectRatio, float nearClip, float farClip)
{
	// A standard [0, 1] depth projection with near and far swapped maps near -> 1 and far -> 0.
	return glm::perspectiveRH_ZO(verticalFov, aspectRatio, farClip, nearClip);
}

glm::mat4 PerspectiveReverseZInfinite(float verticalFov, float aspectRatio, float nearClip)
{
	const float focalLength = 1.0f / glm::tan(verticalFov * 0.5f);
	glm::mat4 result(0.0f);
	result[0][0] = focalLength / aspectRatio;
	result[1][1] = focalLength;
	result[2][3] = -1.0f;
	result[3][2] = nearClip; // depth = near / -z_view
	return result;
}

glm::mat4 OrthographicReverseZ(float left, float right, float bottom, float top, float nearClip, float farClip)
{
	return glm::orthoRH_ZO(left, right, bottom, top, farClip, nearClip);
}
```

1. **Line 74:** a standard zero-to-one projection called with the far distance where the near one goes. That swap is the
   whole of reversed Z.
2. **Line 79:** the focal length, one over the tangent of half the field of view.
3. **Lines 81–82:** X is scaled by the focal length divided by the aspect ratio, so that a wide window does not stretch.
4. **Line 83:** this element makes the fourth coordinate equal to the distance in front of the camera, so the later
   divide is a division by distance.
5. **Line 84:** the depth row holds only the near distance. There is no far distance in this function.

Now the ray. Find the two depths and where the divide happens.

```cpp src="Strata/src/Strata/Math/Ray.cpp#L7-L16"
Ray Ray::FromNDC(const glm::vec2& ndc, const glm::mat4& inverseViewProjection)
{
	// Reversed Z: depth 1 is the near plane. Depth 0.5 is a second point on the same ray that stays
	// finite even with an infinite far plane.
	const glm::vec4 nearPoint = inverseViewProjection * glm::vec4(ndc, 1.0f, 1.0f);
	const glm::vec4 farPoint = inverseViewProjection * glm::vec4(ndc, 0.5f, 1.0f);
	const glm::vec3 origin = glm::vec3(nearPoint) / nearPoint.w;
	const glm::vec3 target = glm::vec3(farPoint) / farPoint.w;
	return Ray(origin, target - origin);
}
```

1. **Line 11:** depth 1, the near plane, run through the inverse of the view-projection matrix.
2. **Line 12:** depth 0.5, a second point on the same line, which stays finite when the far plane is infinite.
3. **Lines 13–14:** each point divides by its own fourth coordinate, as the toy did.
4. **Line 15:** the `Ray` :term[constructor]{id=constructor} normalizes the direction, so the difference of the points needs no care.

The caller chooses the matrix. The editor's placement ray, in `StrataEditor/src/Editor/EditorPlacement.cpp`, inverts the
projection times a :term[view matrix]{id=view-matrix} with the camera's rotation only, then adds the camera position to the ray's origin. The
position is added once and the inverted matrix stays well scaled far from the world's origin.

The :term[decomposition]{id=decomposition-of-a-transform} is the longest function. Find the checks that return early and the one place where the outputs
change.

```cpp src="Strata/src/Strata/Math/Math.cpp#L9-L54"
bool DecomposeTransform(const glm::mat4& transform, glm::vec3& outTranslation, glm::quat& outRotation, glm::vec3& outScale)
{
	// Outputs are only written on success, so callers keep their previous values for degenerate input.
	for (int column = 0; column < 4; column++)
	{
		for (int row = 0; row < 4; row++)
		{
			if (!std::isfinite(transform[column][row]))
				return false;
		}
	}

	glm::mat4 localMatrix(transform);
	if (glm::abs(localMatrix[3][3]) < glm::epsilon<float>())
		return false;

	// Normalize so the homogeneous coordinate is 1. Projective components are ignored.
	if (glm::abs(localMatrix[3][3] - 1.0f) > glm::epsilon<float>())
		localMatrix /= localMatrix[3][3];

	const glm::vec3 translation = glm::vec3(localMatrix[3]);
	glm::vec3 columns[3] = { glm::vec3(localMatrix[0]), glm::vec3(localMatrix[1]), glm::vec3(localMatrix[2]) };
	glm::vec3 scale(glm::length(columns[0]), glm::length(columns[1]), glm::length(columns[2]));
	if (scale.x < glm::epsilon<float>() || scale.y < glm::epsilon<float>() || scale.z < glm::epsilon<float>())
		return false;

	columns[0] /= scale.x;
	columns[1] /= scale.y;
	columns[2] /= scale.z;

	// A left-handed basis means an odd number of negative scale axes; fold the reflection into X.
	if (glm::dot(columns[0], glm::cross(columns[1], columns[2])) < 0.0f)
	{
		scale.x = -scale.x;
		columns[0] = -columns[0];
	}

	const glm::quat rotation = glm::normalize(glm::quat_cast(glm::mat3(columns[0], columns[1], columns[2])));
	if (!std::isfinite(rotation.x) || !std::isfinite(rotation.y) || !std::isfinite(rotation.z) || !std::isfinite(rotation.w))
		return false;

	outTranslation = translation;
	outRotation = rotation;
	outScale = scale;
	return true;
}
```

1. **Lines 12–17:** any value that is not finite fails the whole call at once.
2. **Lines 22–27:** a last element near 0 fails; one that is not 1 divides the matrix by it, so the result stays affine.
3. **Lines 31–33:** the scales are the lengths of the three basis columns; a column near 0 means a squashed matrix.
4. **Lines 39–44:** a negative determinant of the basis means a mirror. Strata puts it in the scale of X.
5. **Lines 50–53:** the outputs change only here, after every check passed.

The toy had no equivalent of the last two functions. `ComposeTransform` scales the columns of the rotation matrix, and
`ComposeWorldTransform` is the one product.

```cpp src="Strata/src/Strata/Math/Math.cpp#L56-L69"
glm::mat4 ComposeTransform(const glm::vec3& translation, const glm::quat& rotation, const glm::vec3& scale)
{
	glm::mat4 result = glm::mat4_cast(rotation);
	result[0] *= scale.x;
	result[1] *= scale.y;
	result[2] *= scale.z;
	result[3] = glm::vec4(translation, 1.0f);
	return result;
}

glm::mat4 ComposeWorldTransform(const glm::mat4& parentWorld, const glm::mat4& local)
{
	return parentWorld * local;
}
```

1. **Lines 58–62:** the rotation matrix, its first three columns scaled, and the translation in the last column.
2. **Line 68:** the whole of `ComposeWorldTransform`: the parent's matrix times the local one, in a function whose
   compiled body every caller runs.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Standard depth with a finite far plane | Most introductory tutorials | Agrees with glm's default and with every OpenGL example | Far surfaces fight for the same depth values |
| The engine's own vector and matrix types | Some large engines | Control of precision and of the layout | Conversions at every library border, and no direct use of glm code |
| Forbid fused multiply-adds everywhere | Builds that need identical numbers | Every product agrees without a special function | Speed in all the engine's arithmetic |
| One shared random generator with a lock | Small programs | One sequence for the whole program | Waiting on the lock, and an order that depends on thread timing |

## How it is tested

The `Math` suite in `StrataTests/src/Math/MathTests.cpp` holds one test case per area. The suite builds and splits
transforms again, including a mirrored matrix and a zero matrix, and it checks Euler conversions and `LookRotation` in four
directions. It projects points through the reversed-Z matrices and checks depth 1 at the near plane and depth near 0 at the far
one, finite or infinite. It also tests boxes, frustum culling with both projections, `Ray::FromNDC` against a projected
point, the four :term[intersection tests]{id=intersection-test} and seeding. Run it with:

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=Math
```

The agreement of world matrices is tested in the scene suites instead: `Scene.Timing.Sweep` compares matrices bit
for bit, and `Scene.Transforms.Sweep` compares each cached matrix with one computed again, within a relative
tolerance of 0.00001.

## Changing it safely

New math goes into `Math.h` in `Strata::Math`, or into a type of its own beside `AABB`, with a test in the `Math` suite.
A function that follows the conventions needs no comment about them; one that cannot follow them says so. Keep every
function free of state and safe for any thread, as the others are.

:::rule[Everything ships with tests]
A change to the library needs a unit test, and a bug fix needs a regression test that fails without the fix. The rule
exists because the library is used by everything: a wrong sign appears far from its cause. [Your first engine change](first-change.md) runs
the tests.
:::

The code adds one rule of its own: compose a world matrix only through `ComposeWorldTransform`. Before a commit, run the `Math` suite and the
`Scene.Timing.Sweep` and `Scene.Transforms.Sweep` suites.

## What went wrong before

When a change left the scene's world matrices composed with a plain product in several inlined copies, two sweeps failed on Linux with GCC
and the `-mfma` option and passed with the MSVC compiler. One cached world matrix differed by a single unit in the last place from
the one computed again, a little above the check's tolerance. The cause was the fused multiply-add: the compiler contracted the same `parent * local` differently
in each inlined copy. The fix was `ComposeWorldTransform`, and the regression tests are the two sweeps named above.

## Summary

- The infinite reversed-Z projection gives the depth near divided by distance and has no far plane.
- `Ray::FromNDC` takes the depths 1 and 0.5, two finite points on one ray.
- `DecomposeTransform` fails on broken matrices without touching its outputs and folds a mirror into the scale of X.
- `IsNearlyEqual` compares quaternions by the dot product, because q and −q are one rotation.
- The scene composes world matrices in one compiled function, so that its paths agree to the last bit.

## Check yourself

1. A point is 4 units in front of an infinite reversed-Z camera whose near distance is 0.5. What depth does it get, and
   what depth does a point 4,000 units away get?

   :::answer{tests="projections"}
   The depth is the near distance divided by the distance: 0.5 / 4 = 0.125, and 0.5 / 4000 = 0.000125. The second is
   small but not 0; the depth reaches 0 only at infinity.
   :::

2. Why does `Ray::FromNDC` use the depths 1 and 0.5, and not 1 and 0?

   :::answer{tests="ray-from-ndc"}
   Depth 0 is the far plane, and for an infinite projection it lies at infinity: the fourth coordinate of the point is 0, and dividing by it gives no number. Depth 0.5 is a finite point on the same line, so the two finite points
   fix the ray.
   :::

3. What do the scale and the rotation of `DecomposeTransform` say for a matrix that mirrors Y only, with no rotation?

   :::answer{tests="decompose"}
   The scale is (−1, 1, 1) and the rotation is a half turn about Z. Together they rebuild the mirror of Y: the half turn
   flips X and Y, and the scale of X flips X back. The parts are not the ones that went in, but the matrix is the same.
   :::

4. Which test says that two quaternions are one rotation? (a) All four components are nearly equal. (b) The absolute dot
   product is nearly 1. (c) The :term[Euler angles]{id=euler-angles} are nearly equal.

   :::answer{tests="quaternion-equality"}
   The answer is (b). Option (a) fails for q and −q, which are the same rotation with four signs flipped. Option (c) can
   fail for rotations near a :term[gimbal lock]{id=gimbal-lock}, where different angles name one rotation.
   :::

5. Two code paths of one build each compute `parent * local` inlined, and their results differ in the last bit. What does
   the scene do, and why does it matter?

   :::answer{tests="world-compose"}
   The scene calls `ComposeWorldTransform` in every path, so every path runs the same compiled product. It matters because the
   scene's checks compare its matrices. A run drawn between poses and one drawn without must agree bit for bit, and
   a cached matrix must match one computed again within a tight tolerance. A different last bit can fail either check.
   :::

## Exercises

1. **Basic.** Trace it yourself: the editor's placement ray. Follow it with a search from the viewport's pointer to
   `Ray::FromNDC`, and say why the camera's position is added only once.

   :::answer[Worked solution]{tests="ray-from-ndc"}
   Search for `MakeViewRay`. The viewport panel calls it in `StrataEditor/src/Panels/ViewportPanel.cpp` and the
   placement command in `StrataEditor/src/Editor/Commands/PlacementCommands.cpp`.

   The function lives in
   `StrataEditor/src/Editor/EditorPlacement.cpp`. It makes a matrix from the camera's rotation only, inverts the product
   of the projection and that matrix, and calls `Ray::FromNDC`. The ray's origin is near 0, so the function adds
   the camera's position afterward, once. A matrix that held the position would be inverted with large numbers in it, which
   wastes float precision far from the origin.
   :::

2. **Medium.** Test a 5 by 4 grid of boxes, each turned 45 degrees about Y, against a camera at (0, 0, 10) with a 60
   degree infinite reversed-Z projection. Its near distance is 0.1 and its aspect ratio 1. Use a box's world box from Arvo's method. Which boxes are visible?

   :::answer[Worked solution]{tests="projections" solution="sketches/core-math-grid.cpp"}
   Use a box test on clip coordinates: a world box is out only when its corners all fail the same plane. The sketch does
   that with glm alone.

   ```cpp sketch="core-math-grid.cpp"
   // A grid of turned boxes against a camera with an infinite reversed-Z projection. Each box gets a world box by Arvo's
   // method; a world box is rejected only when its eight corners all lie outside one clip plane.
   #include <cstdio>
   #include <glm/glm.hpp>
   #include <glm/gtc/matrix_transform.hpp>

   namespace
   {
   	struct Box
   	{
   		glm::vec3 Min, Max;
   	};

   	Box Transformed(const Box& box, const glm::mat4& transform)
   	{
   		const glm::vec3 center = (box.Min + box.Max) * 0.5f;
   		const glm::vec3 extents = (box.Max - box.Min) * 0.5f;
   		const glm::vec3 newCenter = glm::vec3(transform * glm::vec4(center, 1.0f));
   		glm::vec3 newExtents(0.0f);
   		for (int axis = 0; axis < 3; axis++)
   		{
   			newExtents[axis] = glm::abs(transform[0][axis]) * extents.x + glm::abs(transform[1][axis]) * extents.y
   				+ glm::abs(transform[2][axis]) * extents.z;
   		}
   		return { newCenter - newExtents, newCenter + newExtents };
   	}

   	bool IsVisible(const Box& box, const glm::mat4& viewProjection)
   	{
   		// One bit per clip plane. Depth runs from 0 to w, so the planes are x and y against w, z above w (nearer than
   		// the near plane) and z below 0 (beyond the far plane, which an infinite far plane never reaches).
   		int outsideAll = 0b111111;
   		for (int corner = 0; corner < 8; corner++)
   		{
   			const glm::vec3 point((corner & 1) ? box.Max.x : box.Min.x, (corner & 2) ? box.Max.y : box.Min.y,
   				(corner & 4) ? box.Max.z : box.Min.z);
   			const glm::vec4 clip = viewProjection * glm::vec4(point, 1.0f);
   			int outside = 0;
   			if (clip.x > clip.w) outside |= 1;
   			if (clip.x < -clip.w) outside |= 2;
   			if (clip.y > clip.w) outside |= 4;
   			if (clip.y < -clip.w) outside |= 8;
   			if (clip.z > clip.w) outside |= 16;
   			if (clip.z < 0.0f) outside |= 32;
   			outsideAll &= outside;
   		}
   		return outsideAll == 0;
   	}
   }

   int main()
   {
   	const glm::mat4 view = glm::lookAtRH(glm::vec3(0.0f, 0.0f, 10.0f), glm::vec3(0.0f), glm::vec3(0.0f, 1.0f, 0.0f));
   	const float focal = 1.0f / glm::tan(glm::radians(60.0f) * 0.5f);
   	glm::mat4 projection(0.0f);
   	projection[0][0] = focal;
   	projection[1][1] = focal;
   	projection[2][3] = -1.0f;
   	projection[3][2] = 0.1f;

   	const Box unitBox { glm::vec3(-1.0f), glm::vec3(1.0f) };
   	for (const float z : { 20.0f, 0.0f, -50.0f, -1.0e5f })
   	{
   		std::printf("z = %9.0f:", z);
   		for (const float x : { -20.0f, -10.0f, 0.0f, 10.0f, 20.0f })
   		{
   			const glm::mat4 model = glm::rotate(glm::translate(glm::mat4(1.0f), glm::vec3(x, 0.0f, z)), glm::radians(45.0f), glm::vec3(0.0f, 1.0f, 0.0f));
   			std::printf(" %c", IsVisible(Transformed(unitBox, model), projection * view) ? 'X' : '.');
   		}
   		std::printf("\n");
   	}
   }
   ```

   ```text output-of="core-math-grid.cpp"
   z =        20: . . . . .
   z =         0: . . X . .
   z =       -50: X X X X X
   z =   -100000: X X X X X
   ```

   1. **Lines 14–26:** Arvo's method on a plain box type, the same as `AABB::Transformed`.
   2. **Lines 28–48:** six plane tests per corner, ANDed over the eight corners.
   3. **Line 44:** the beyond-the-far test, which an infinite projection never fails.
   4. **Lines 61–71:** the grid, each box turned and moved before the test.

   The row at z = 20 is behind the camera. In the row at z = 0 only the middle box is inside the view. The two rows
   beyond are fully visible, even the one 100,000 units away, because the far plane is infinite. With Strata's types the
   body is `Frustum frustum(projection * view);` and then `frustum.IsAABBVisible(box.Transformed(model))`.
   :::

3. **Hard.** Derive `PerspectiveReverseZInfinite` on paper, with $d$ the distance in front of the camera, and check
   it against the finite projection as the far distance grows.

   :::answer[Worked solution]{tests="projections"}
   The wanted depth is $n / d$, with $n$ the near distance. The fourth clip coordinate must be $d = -z$, so the last row
   of the matrix is (0, 0, −1, 0). The depth clip coordinate must be $n$ times the point's fourth coordinate, so the
   third row is (0, 0, 0, $n$). Dividing gives $n / d$.

   At $d = n$ the depth is 1, and as $d$ grows it falls toward 0,
   which agrees with `MathTests.cpp`, where the test expects 1 at 0.1 and about 0 at 10 million. The X and Y rows are
   the focal length over the aspect ratio, and the focal length.

   For the check, the finite reversed depth is $n (f - d) / (d (f - n))$ for far distance $f$. As $f$ grows, $f - d$ and
   $f - n$ both approach $f$, and the depth approaches $n / d$.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Math/Math.h` and `Math.cpp`: conventions, transforms, projections, rotations.
- `Strata/src/Strata/Math/AABB.h`, `Frustum.h`, `Ray.h` and `Random.h`, with their `.cpp` files.
- `StrataTests/src/Math/MathTests.cpp`: the `Math` suite.
- `StrataEditor/src/Editor/EditorPlacement.cpp`: `MakeViewRay`, the caller of `Ray::FromNDC`.

## Further reading

- Nathan Reed, "Depth Precision Visualized": why reversed Z helps floating-point depth buffers (intermediate).
- Tomas Möller and Ben Trumbore, "Fast, Minimum Storage Ray-Triangle Intersection" (advanced).
- James Arvo, "Transforming Axis-Aligned Bounding Boxes", in Graphics Gems (advanced).
- The glm manual, on its matrix and quaternion functions (beginner).
