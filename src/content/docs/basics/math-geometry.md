---
id: basics/math-geometry
title: "Geometry for engines: rays, planes, boxes and intersection tests"
description: "Rays, planes, spheres, boxes and triangles as small functions: where lines meet shapes, which shapes touch, and why floating point needs a tolerance."
kind: primer
size: L
tracks: [B, E]
needs: [basics/math-matrices, basics/math-projection]
time: 85
learn:
  - id: rays-planes
    text: compute the point at a given t on a ray, the signed distance of a point from a plane and where a ray meets a plane
  - id: spheres-boxes
    text: compute whether a point lies in a sphere or a box and whether two spheres or two boxes overlap
  - id: ray-tests
    text: compute where a ray meets a sphere, a box and a triangle, and name the cases that miss
  - id: frustum-separating
    text: find whether a sphere lies outside a frustum, and find an axis that separates two shapes
  - id: robustness
    text: choose a tolerance for a comparison and name the degenerate inputs that a test must handle
status: final
---

::::test-out

1. A plane has the unit normal (0, 1, 0) and the offset -2. The signed distance of a point is its dot product with the
   normal, plus the offset. Compute it for (4, 3, 1) and say which side of the plane the point is on.

   :::answer{tests="rays-planes"}
   The dot product is 3, and 3 + (-2) = 1. The result is positive, so the point is on the side the normal points to.
   :::

2. Do the box from (0, 0, 0) to (2, 2, 2) and the box from (1, 3, 1) to (4, 5, 4) overlap?

   :::answer{tests="spheres-boxes"}
   No. On the y axis the first box ends at 2 and the second starts at 3, so one axis shows a gap.
   :::

3. A ray starts at (0, 0, 0) and runs along (0, 0, 1). A sphere with the center (0, 0, 5) and the radius 1 lies on it.
   At which distance does the ray enter the sphere?

   :::answer{tests="ray-tests"}
   The sphere spans z from 4 to 6 on the ray, so the ray enters at distance 4.
   :::

4. A sphere with the radius 0.5 has its center 0.3 outside one plane of a frustum, a signed distance of -0.3. Is the
   sphere kept or dropped? And with a signed distance of -0.8?

   :::answer{tests="frustum-separating"}
   -0.3 is not below -0.5, so the sphere is kept. -0.8 is below -0.5, so the whole sphere lies outside, and it is
   dropped.
   :::

5. Write one line of C++ that is true when the float `d` equals 2, give or take a rounding error of one part in a
   hundred thousand.

   :::answer{tests="robustness"}
   `glm::abs(d - 2.0f) < 1e-5f`. Writing `d == 2.0f` fails as soon as one operation has rounded `d`.
   :::

::::

## Why you will need this

A game keeps asking what lies where. Which object is under the cursor? What does a shot hit first? Is the coin inside
the ball's reach? Is a tree inside the camera's view?

Each answer is a small test on a few numbers: a shape, a line, a comparison. [Bounds and
culling](../draw/bounds-culling.md) uses them to skip what the camera cannot see. [Collision
detection](../physics/collision-detection.md) uses them to tell whether bodies touch. [Queries](../physics/queries.md)
uses them to answer a ray cast from a script.

Only the optional Coin Run exercise needs a project. Each sketch is a whole program: save it as `sketch.cpp` and compile it in the terminal of [How a C++ program is built](build.md#open-a-terminal-that-finds-a-compiler), with C++20 and the `glm` headers of your Strata folder. On Windows, run `cl /std:c++20 /EHsc /I "<Strata folder>\StrataScriptCore\ThirdParty\glm" sketch.cpp` and then `.\sketch.exe`. On Linux and macOS, run `c++ -std=c++20 -I "<Strata folder>/StrataScriptCore/ThirdParty/glm" sketch.cpp -o sketch` and then `./sketch`. Without a compiler, read each output and its notes.

## A ray is an origin and a direction

A click asks what lies under the cursor. A ball asks how far the ground is
below it. Both follow a line from a start in one direction.

A **ray** is a half line: an origin, where it starts, and a direction, in which it runs without end. The ball stands at
(0, 1, 0) and looks straight down, along (0, -1, 0). Walk 0.25 steps along the direction and you are at (0, 0.75, 0).
Walk 1 step and you reach (0, 0, 0). Walk -1 step and you stand at (0, 2, 0), behind the ball: that point is not on
the ray.

$$
P(t) = o + t\,d
$$

$o$ is the origin, $d$ is the direction and $t$ is the number of steps of $d$ that you walk. $P(t)$ is read "the point
at t", and $t\,d$ is the direction scaled by $t$, as in the vectors page. The ray is every $P(t)$ with $t$ from 0
upward. At $t = 0$ you are on the origin; a negative $t$ lies behind it.

If $d$ is a :term[unit vector]{id=unit-vector}, one step is one unit of length, and $t$ is the distance from the origin. Every test below
keeps its direction at length 1, so the number a test returns is a distance.

:::example[Three points on one ray]
The ray has the origin (1, 4, 0) and the direction (0, 0, 1). At t = 2 the point is (1, 4, 0) + 2 × (0, 0, 1) = (1, 4,
2). At t = 0 it is (1, 4, 0), the origin itself. At t = -3 the formula gives (1, 4, -3), which is behind the origin
and off the ray.
:::

Try it: the ray has the origin (0, 2, 5) and the direction (1, 0, 0). Where is the point at t = 4, and which value of
t puts you at (-1, 2, 5)?

:::answer
At t = 4 the point is (4, 2, 5). The point (-1, 2, 5) needs t = -1, so it lies behind the origin and is not on the
ray.
:::

:::note[In Strata]
`Ray` in `Strata/src/Strata/Math/Ray.h` stores an `Origin` and a `Direction`. Its constructor :term[normalizes]{id=normalization} the
direction, and `GetPoint(distance)` returns the point at that distance. [Strata's math code](../core/math.md) walks
through the rest of the type.
:::

## A plane splits space into two sides

A floor reaches in every direction without end. Every point is above it, below it or on it. The same holds for a wall
or a tilted ramp, however far you look.

A **plane** is a flat surface without edges, given by a unit normal $n$, a vector at a right angle to the surface, and
an offset $w$, a number. A point $p$ lies on the plane when $n \cdot p + w = 0$. Take a floor at height 2. Its normal
points up, (0, 1, 0), and its offset is -2, because $n \cdot p + w$ becomes $y - 2$, which is 0 at height 2.

The same sum tells you more than "on or off". Put (3, 5, 1) in: the :term[dot product]{id=dot-product} is 5, and 5 - 2 = 3. Put (0, 0, 0) in:
0 - 2 = -2. The first point is 3 units above the floor and the second is 2 below.

$$
s = n \cdot p + w
$$

$s$ is the **signed distance** of the point $p$: its distance from the plane, positive on the side the normal points
to, negative on the other side and 0 on the plane. $n \cdot p$ is read "n dot p". The dot product of a point with a
unit vector is how far along that vector the point lies, so $s$ compares that with where the plane is.

::figure{id=plane-side}

To build a plane from a normal $n$ and one point $q$ on it, take $w = -(n \cdot q)$. For the floor, $q = (0, 2, 0)$
and $n \cdot q = 2$, so $w = -2$. The plane lies at the distance $-w$ from the origin, along $n$.

The normal must have length 1. A normal of length 2 doubles every signed distance, and the test says 6 where the point
is 3 away. Normalizing the normal, and dividing the offset by the same length, repairs the plane.

## A ray meets a plane at one value of t

Where does a ray meet the floor? Finding that is the first **intersection test** of this page: a function that tells
whether two shapes touch and, often, where. A point of the ray is on the plane when its signed distance is 0.

Take the ray from (0, 5, 0) along (0.6, -0.8, 0), and the floor at height 2. The origin is 3 above the floor. Each
step of the direction goes 0.8 down, so the ray needs 3 / 0.8 = 3.75 steps. At t = 3.75 the point is (2.25, 2, 0), and
its height is 5 - 0.8 × 3.75 = 2.

$$
t = -\frac{n \cdot o + w}{n \cdot d}
$$

The top, $n \cdot o + w$, is the signed distance of the origin: 3. The bottom, $n \cdot d$, is how much of each step
goes along the normal: -0.8. $-$ before the fraction turns 3 / (-0.8) into the positive 3.75. The formula comes from
putting $P(t)$ into the signed distance and asking for 0.

Two cases give no hit. If $n \cdot d$ is 0, the ray runs parallel to the plane, never gets closer, and the division
fails. If $t$ is negative, the plane lies behind the origin: the line meets it, the ray does not.

::figure{id=ray-meets-plane}

:::question[Why do these programs start with lines I have not seen?]
The `#include` lines bring in `glm`, the vector library of Strata, and calls such as `glm::dot(...)` use it. [Programming
3](../basics/programming-3.md) explains both, and [modern C++](../basics/cpp-modern.md) explains `std::optional`, which
holds a number or nothing.
:::

The function below returns the `t` of the hit, or nothing. Search for the three exits: parallel, behind, and the hit.

```cpp sketch="basics-math-geometry-plane.cpp"
#include <cstdio>
#include <glm/glm.hpp>
#include <optional>

float SignedDistance(const glm::vec4& plane, const glm::vec3& point) { return glm::dot(glm::vec3(plane), point) + plane.w; }

std::optional<float> HitPlane(const glm::vec3& origin, const glm::vec3& direction, const glm::vec4& plane)
{
	const float slope = glm::dot(glm::vec3(plane), direction);
	if (glm::abs(slope) < 1e-8f)
		return std::nullopt; // parallel: the ray never meets the plane
	const float t = -SignedDistance(plane, origin) / slope;
	return t >= 0.0f ? std::optional<float>(t) : std::nullopt; // a negative t lies behind the origin
}

int main()
{
	const glm::vec4 floor(0.0f, 1.0f, 0.0f, -2.0f);
	const glm::vec3 origin(0.0f, 5.0f, 0.0f);
	std::printf("above %g, below %g\n", SignedDistance(floor, glm::vec3(3.0f, 5.0f, 1.0f)), SignedDistance(floor, glm::vec3(0.0f)));
	std::printf("slanted %g, ", HitPlane(origin, glm::vec3(0.6f, -0.8f, 0.0f), floor).value_or(-1.0f));
	std::printf("parallel %g, ", HitPlane(origin, glm::vec3(1.0f, 0.0f, 0.0f), floor).value_or(-1.0f));
	std::printf("behind %g\n", HitPlane(origin, glm::vec3(0.0f, 1.0f, 0.0f), floor).value_or(-1.0f));
}
```

```text output-of="basics-math-geometry-plane.cpp"
above 3, below -2
slanted 3.75, parallel -1, behind -1
```

1. **Line 5:** the signed distance, one dot product and one addition. A plane is a `glm::vec4`, as in Strata: x, y and
   z are the normal and w is the offset.
2. **Lines 10–11:** a slope close to 0 means parallel, so the function returns nothing. `IntersectRayPlane` in
   `Strata/src/Strata/Math/Ray.cpp` uses the same limit, 1e-8, a tolerance that a later section explains.
3. **Line 13:** a negative `t` lies behind the origin and counts as a miss.

The output matches the hand numbers: 3 above, 2 below and 3.75 for the slanted ray. A value of -1 stands for nothing
in the output: the parallel ray and the ray that points up both miss.

## A sphere is a center and a radius

A sphere is every point at a fixed distance, the radius, from a center. A point lies inside when its distance to the
center is at most the radius. For the center (0, 0, 0) and the radius 2, the point (1, 1, 1) is the square root of 3,
about 1.73, away: inside.

A square root costs time, so engines compare squares instead. Distance squared is the dot product of the step with
itself: 1 + 1 + 1 = 3, and 3 ≤ 2 × 2 = 4. Both sides are positive, so the comparison gives the same answer.

Two spheres overlap when their centers are closer than the two radii added. Take the centers (0, 0, 0) and (3, 4, 0)
with the radii 2 and 3. The centers are 5 apart, and 2 + 3 = 5: the spheres touch. A test written with "at most" counts
touching as overlapping.

A **bounding sphere** is a sphere that holds a whole shape: its center is somewhere in the middle of the shape, and
its radius reaches the farthest point. A sphere does not care which way the shape is turned, so a turning object keeps
the same bounding sphere. That makes it a cheap first test.

## A ray meets a sphere by solving for t

Where does a ray enter a sphere? The point $P(t)$ is on the sphere when its distance to the center is the radius. That
gives an equation in $t$ of a well-known kind.

A **quadratic equation** asks for the numbers $t$ that make $a t^2 + b t + c = 0$ true. School algebra gives the answer.

$$
t = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}
$$

$a$, $b$ and $c$ are the three numbers of the equation, and $\sqrt{\;}$ is read "the square root of". $\pm$ is read
"plus or minus": it gives two answers, one with the plus and one with the minus. The part under the root decides how
many answers exist. A negative number has no square root, so no $t$ exists. Zero gives one answer, and a positive
number gives two.

:::derivation
Let $m = o - c_s$ be the step from the sphere's center $c_s$ to the origin, and $r$ the radius. The point is on the
sphere when its squared distance to the center is $r^2$: $(m + t\,d) \cdot (m + t\,d) = r^2$. Multiplying out gives $t^2
(d \cdot d) + 2t(m \cdot d) + m \cdot m - r^2 = 0$. A unit direction has $d \cdot d = 1$, so $a = 1$, $b = 2(m \cdot
d)$ and $c = m \cdot m - r^2$.
:::

The 2 in $b$ cancels against the 2 in the formula. Call $h = m \cdot d$, and the answers become $t = -h \pm \sqrt{h^2 -
c}$, with $c = m \cdot m - r^2$.

Take the sphere with the center (0, 0, 5) and the radius 1, and the ray from (0, 0, 0) along (0, 0, 1). Here $m$ =
(0, 0, -5), so $h = -5$ and $c = 25 - 1 = 24$. The part under the root is 25 - 24 = 1, and the answers are $5 \pm 1$:
4 and 6. The ray enters at z = 4 and leaves at z = 6, as a picture of the sphere says.

Turn the ray to look along (0, 1, 0). Now $h = 0$, and the part under the root is 0 - 24, negative: the ray misses. The
smaller answer is the entry. If it is negative, the origin is inside the sphere, and the larger answer is the way out.
If both are negative, the sphere lies behind.

The function below follows those steps, in the order of its exits.

```cpp sketch="basics-math-geometry-sphere.cpp"
#include <cstdio>
#include <glm/glm.hpp>
#include <optional>

std::optional<float> HitSphere(const glm::vec3& origin, const glm::vec3& direction, const glm::vec3& center, float radius)
{
	const glm::vec3 toOrigin = origin - center; // the direction has length 1, so the quadratic has a = 1
	const float b = glm::dot(toOrigin, direction);
	const float c = glm::dot(toOrigin, toOrigin) - radius * radius;
	const float discriminant = b * b - c;
	if (discriminant < 0.0f)
		return std::nullopt; // the line misses the sphere
	const float root = glm::sqrt(discriminant);
	if (-b + root < 0.0f)
		return std::nullopt; // the sphere lies behind the origin
	return -b - root >= 0.0f ? -b - root : -b + root; // inside the sphere: the way out
}

int main()
{
	const glm::vec3 center(0.0f, 0.0f, 5.0f), zero(0.0f), along(0.0f, 0.0f, 1.0f), up(0.0f, 1.0f, 0.0f);
	std::printf("hit %g, miss %g, ", HitSphere(zero, along, center, 1.0f).value_or(-1.0f), HitSphere(zero, up, center, 1.0f).value_or(-1.0f));
	std::printf("inside %g, ", HitSphere(center, along, center, 1.0f).value_or(-1.0f));
	std::printf("behind %g\n", HitSphere(zero, -along, center, 1.0f).value_or(-1.0f));
}
```

```text output-of="basics-math-geometry-sphere.cpp"
hit 4, miss -1, inside 1, behind -1
```

1. **Lines 8–9:** `b` is the $h$ above, half of the formula's $b$, and `c` is $m \cdot m - r^2$.
2. **Lines 10–12:** a negative number under the root means the whole line misses.
3. **Lines 13–15:** a larger answer below 0 means the sphere is behind the origin.
4. **Line 16:** the entry when it is not negative; from inside, the exit.

The four results are the hand numbers: 4 for the hit, nothing for the miss, 1 from the center out to the surface and
nothing for the sphere behind. `IntersectRaySphere` in `Strata/src/Strata/Math/Ray.cpp` gives the same answers. It
first returns nothing when the origin is outside and the ray points away, before it takes a square root.

## A box needs only two corners

A **bounding box** is a box that holds a whole shape.

The most common kind keeps its faces flat to the three axes: an **axis-aligned bounding box** (AABB). Two corners
describe it: the smallest, with the lowest x, y and z, and the largest. The box from (0, 0, 0) to (2, 2, 2) is a cube of
side 2.

Some engines store the smallest corner and the size instead: the largest corner is the smallest plus the size. Strata's
`AABB` in `Strata/src/Strata/Math/AABB.h` keeps `Min` and `Max`, and computes the size and the center when asked.

A point lies inside when it is between the corners on every axis. (1, 1, 1) is inside the cube above; (3, 1, 1) is not,
because 3 is more than 2. Two boxes overlap when their ranges overlap on every axis, so you test each axis, one at a
time. The box from (1, 1, 1) to (3, 3, 3) overlaps the cube: on x, 0 ≤ 3 and 2 ≥ 1, and the same holds on y and z. The
box from (3, 0, 0) to (4, 2, 2) does not: the cube ends at x = 2, and that box starts at 3.

A box grows to hold a point by moving each corner outward, never inward. The new smallest corner takes the lower of the
old one and the point on each axis, and the largest corner takes the higher. Grow the cube to hold (3, -1, 1): the
corners become (0, -1, 0) and (3, 2, 2).

How does a box start, before it holds anything? Strata starts it empty: `Min` at the largest float and `Max` at the
lowest. The first point you add pulls both corners onto it. A box whose `Min` is above its `Max` holds nothing, and
`IsValid` says so.

A sphere against a box takes one more idea. The point of the box closest to the sphere's center is the center, clamped
into the box on each axis. The sphere touches the box when that closest point lies within the radius.

```cpp sketch="basics-math-geometry-boxes.cpp"
#include <cstdio>
#include <glm/glm.hpp>

struct Box { glm::vec3 Low; glm::vec3 High; };

bool Overlaps(const Box& a, const Box& b) { return glm::all(glm::lessThanEqual(a.Low, b.High)) && glm::all(glm::greaterThanEqual(a.High, b.Low)); }

Box Grow(const Box& box, const glm::vec3& point) { return { glm::min(box.Low, point), glm::max(box.High, point) }; }

bool SphereTouches(const glm::vec3& center, float radius, const Box& box)
{
	const glm::vec3 gap = center - glm::clamp(center, box.Low, box.High); // from the center to the box's closest point
	return glm::dot(gap, gap) <= radius * radius;
}

int main()
{
	const Box a = { glm::vec3(0.0f), glm::vec3(2.0f) };
	const Box grown = Grow(a, glm::vec3(3.0f, -1.0f, 1.0f));
	std::printf("overlap %d, ", Overlaps(a, Box{ glm::vec3(1.0f), glm::vec3(3.0f) }));
	std::printf("apart %d\n", Overlaps(a, Box{ glm::vec3(3.0f, 0.0f, 0.0f), glm::vec3(4.0f, 2.0f, 2.0f) }));
	std::printf("grown low (%g, %g, %g) high (%g, %g, %g)\n", grown.Low.x, grown.Low.y, grown.Low.z, grown.High.x, grown.High.y, grown.High.z);
	std::printf("sphere %d, ", SphereTouches(glm::vec3(2.5f, 1.0f, 1.0f), 0.6f, a));
	std::printf("corner %d\n", SphereTouches(glm::vec3(2.5f, 2.5f, 1.0f), 0.6f, a));
}
```

```text output-of="basics-math-geometry-boxes.cpp"
overlap 1, apart 0
grown low (0, -1, 0) high (3, 2, 2)
sphere 1, corner 0
```

1. **Line 6:** the overlap test, one comparison per axis, written with `glm` functions that compare all three at
   once.
2. **Line 8:** growing takes the lowest and the highest values of each axis.
3. **Lines 10–14:** `glm::clamp` finds the closest point; the gap to it, squared, is compared with the radius squared.

The cube and the box from 1 to 3 overlap, and the cube and the box from 3 to 4 do not. The grown box matches the hand
corners, and the sphere with the radius 0.6 at (2.5, 1, 1) touches the cube. At the corner side (2.5, 2.5, 1) the
closest point is (2, 2, 1), 0.707 away, so it misses.

## Bounding volumes are cheap stand-ins for exact shapes

A character holds thousands of triangles, and testing a ray against all of them for every shot is slow. Test a box or
sphere around it first. If the ray misses that stand-in, it misses the model, and the thousands of tests never run.

Such a stand-in is a **bounding volume**. The exact test runs only when the cheap one says "maybe". The price is that a
stand-in is larger than its shape, so some "maybe" answers turn out to be misses.

A box that turns with its object is an **oriented bounding box** (OBB). It fits a long, tilted object more closely than
an AABB. The AABB of a 2 by 2 square turned by 45 degrees has the side 2.83, so it covers 8 units of area for a shape
that holds 4. Overlap tests of oriented boxes need the separating axes below, so they cost more.

A sphere is the cheapest stand-in and the loosest for long shapes. An AABB needs six numbers and fits many objects. When
an object moves and turns, you build a new AABB for it; [Bounds and culling](../draw/bounds-culling.md) shows how Strata
does that with `AABB::Transformed`.

## A ray meets a box by clipping it between slabs

A **slab** is the space between two parallel planes. A box is the part where three slabs meet, one for each axis: its
x range, its y range and its z range. A point is inside the box exactly when it is inside all three slabs at once.

For each slab, find the two values of $t$ where the ray crosses its planes: the entry and the exit. The ray enters the
box when it has entered every slab, so the box's entry is the latest of the slab entries. It leaves when it leaves
the first slab, so the box's exit is the earliest of the slab exits. The ray hits the box when the entry comes before
the exit.

::figure{id=slab-2d}

Take the 2D box from (2, 1) to (4, 3), and the ray from (0, 0) along (0.8, 0.6). The x slab spans x from 2 to 4, so
$t$ runs from 2 / 0.8 = 2.5 to 4 / 0.8 = 5. The y slab spans y from 1 to 3, so $t$ runs from 1 / 0.6 ≈ 1.67 to 3 /
0.6 = 5. The latest entry is 2.5 and the earliest exit is 5: a hit at t = 2.5, the point (2, 1.5) on the left face.

Move the box up to (2, 4) and (4, 6). The x slab is unchanged, 2.5 to 5. The y slab now spans 4 / 0.6 ≈ 6.67 to 10. The
latest entry, 6.67, comes after the earliest exit, 5: the ray has left the x slab before it enters the y slab, and
misses.

The sketch below is the 2D test, with the entry starting at 0. That start handles two cases: a box behind the ray
leaves an exit below 0, so the entry is larger and the test misses; and an origin inside the box returns 0.

```cpp sketch="basics-math-geometry-slab.cpp"
#include <algorithm>
#include <cstdio>
#include <glm/glm.hpp>
#include <optional>

std::optional<float> HitBox(const glm::vec2& origin, const glm::vec2& direction, const glm::vec2& low, const glm::vec2& high)
{
	float entry = 0.0f, leave = 1e30f;
	for (int axis = 0; axis < 2; axis++)
	{
		const glm::vec2 t = (glm::vec2(low[axis], high[axis]) - origin[axis]) / direction[axis]; // a zero direction gives infinity
		entry = std::max(entry, std::min(t.x, t.y)); // the latest entry into a slab
		leave = std::min(leave, std::max(t.x, t.y)); // the earliest exit from a slab
	}
	return entry <= leave ? std::optional<float>(entry) : std::nullopt;
}

int main()
{
	const glm::vec2 slant(0.8f, 0.6f), low(2.0f, 1.0f), high(4.0f, 3.0f), zero(0.0f), along(1.0f, 0.0f);
	std::printf("hit %g, ", HitBox(zero, slant, low, high).value_or(-1.0f));
	std::printf("miss %g\n", HitBox(zero, slant, low + glm::vec2(0.0f, 3.0f), high + glm::vec2(0.0f, 3.0f)).value_or(-1.0f));
	std::printf("parallel inside %g, ", HitBox(glm::vec2(0.0f, 2.0f), along, low, high).value_or(-1.0f));
	std::printf("parallel outside %g\n", HitBox(glm::vec2(0.0f, 5.0f), along, low, high).value_or(-1.0f));
}
```

```text output-of="basics-math-geometry-slab.cpp"
hit 2.5, miss -1
parallel inside 2, parallel outside -1
```

1. **Line 8:** the entry starts at 0, not at minus infinity, so a hit never lies behind the origin; the exit starts at
   1e30, a stand-in for infinity.
2. **Line 11:** both slab values at once. A direction of 0 divides by 0 and gives infinity, which still works when the
   origin is inside the slab or outside it.
3. **Lines 12–13:** the latest entry and the earliest exit.
4. **Line 15:** a hit when the entry is not after the exit.

The four lines show the hand results, 2.5 and a miss. The ray that runs along x at height 2 passes through the box and
enters at 2. The same ray at height 5 misses, as the box spans heights 1 to 3.

`IntersectRayAABB` in `Strata/src/Strata/Math/Ray.cpp` guards a direction near 0 with a test of its own: the ray
misses unless its origin lies within that slab. It returns 0 for an origin inside the box, and nothing for an empty box.

## A ray meets a triangle in its plane and inside its edges

A shot at a model is a shot at its triangles. A triangle lies in one plane, so the test has two steps: find where the
ray meets that plane, then ask whether the point lies inside the triangle.

The plane comes from the corners $a$, $b$ and $c$: the :term[cross product]{id=cross-product} of the edges $b - a$ and $c - a$ is a normal, and
the plane goes through $a$. Once the ray's $t$ is known, the point is $P(t)$.

Inside means on the inner side of each of the three edges. Walk the corners in order, and for each edge compute the
cross product of the edge with the step from its start to the point. Its dot product with the triangle's normal is
positive when the point is on the inner side, negative when outside. One negative result means outside.

Take the corners (0, 0, 0), (4, 0, 0) and (0, 4, 0), a ray from (1, 1, 5) along (0, 0, -1). The normal is (0, 0, 16),
and the ray meets the plane z = 0 at t = 5, at the point (1, 1, 0). The three cross products point along z, like the normal, with the sizes 4, 8 and 4: a hit. Try (3, 3, 0): the second edge, from (4, 0, 0) to (0, 4, 0), gives -8, against the normal. The point lies beyond the long edge.

```cpp sketch="basics-math-geometry-triangle.cpp"
#include <cstdio>
#include <glm/glm.hpp>
#include <optional>

std::optional<float> HitTriangle(const glm::vec3& origin, const glm::vec3& direction, const glm::vec3 corner[3])
{
	const glm::vec3 normal = glm::cross(corner[1] - corner[0], corner[2] - corner[0]);
	const float slope = glm::dot(normal, direction);
	const float t = glm::dot(normal, corner[0] - origin) / slope;
	if (glm::abs(slope) < 1e-8f || t < 0.0f)
		return std::nullopt; // parallel to the triangle's plane, or the plane lies behind the origin
	const glm::vec3 point = origin + direction * t;
	for (int i = 0; i < 3; i++) // one cross product per edge
		if (glm::dot(glm::cross(corner[(i + 1) % 3] - corner[i], point - corner[i]), normal) < 0.0f)
			return std::nullopt; // the point lies outside this edge
	return t;
}

int main()
{
	const glm::vec3 corner[3] = { glm::vec3(0.0f, 0.0f, 0.0f), glm::vec3(4.0f, 0.0f, 0.0f), glm::vec3(0.0f, 4.0f, 0.0f) };
	const glm::vec3 down(0.0f, 0.0f, -1.0f);
	std::printf("inside %g, ", HitTriangle(glm::vec3(1.0f, 1.0f, 5.0f), down, corner).value_or(-1.0f));
	std::printf("outside %g\n", HitTriangle(glm::vec3(3.0f, 3.0f, 5.0f), down, corner).value_or(-1.0f));
}
```

```text output-of="basics-math-geometry-triangle.cpp"
inside 5, outside -1
```

1. **Lines 7–9:** the plane's normal from the corners, the slope as in the plane test, and `t` for the plane through
   the first corner.
2. **Lines 10–11:** a parallel ray and a plane behind the origin both miss.
3. **Lines 13–15:** one cross product per edge; a negative result stops the test.

The two results are 5 and a miss. `IntersectRayTriangle` in `Strata/src/Strata/Math/Ray.cpp` gets the same answers with a faster one-pass method from
the Further reading. It treats counterclockwise corners as the front, and `cullBackFaces` makes it skip triangles seen
from behind.

## A frustum is six planes, and its test may keep too much

[The frustum](../basics/math-projection.md) is the volume a camera sees. Its six sides are planes: left, right,
bottom, top, near and far. Strata stores them facing inward, so a point inside has a signed distance of 0 or more from
every plane. A point is visible when none of the six distances is negative.

A sphere with the center $p$ and the radius $r$ is wholly outside one plane when its center is more than $r$ beyond
that plane: the signed distance is below $-r$. One such plane drops the sphere. If no plane drops it, the sphere is
kept.

::figure{id=frustum-spheres}

Take a toy frustum of two planes, $x \ge 1$ and $y \ge 1$, with the normals (1, 0, 0) and (0, 1, 0) and the offsets
-1 and -1. A sphere of radius 0.5 at (3, 3, 0) has the distances 2 and 2: inside. At (0.8, 3, 0) the first distance is
-0.2, which is not below -0.5: the sphere crosses the plane and is kept. At (0, 3, 0) it is -1, below -0.5: dropped.

Now try the center (0.6, 0.6, 0). Both distances are -0.4, so neither plane drops the sphere. Yet the corner of the
frustum is at (1, 1, 0), 0.57 from the center, farther than the radius: the sphere touches nothing. The test keeps a
sphere that is outside.

```cpp sketch="basics-math-geometry-frustum.cpp"
#include <cstdio>
#include <glm/glm.hpp>

// A toy frustum of two planes, x >= 1 and y >= 1: inward-facing, so a point inside has a distance of 0 or more.
bool SphereVisible(const glm::vec3& center, float radius, const glm::vec4 planes[2])
{
	for (int i = 0; i < 2; i++)
	{
		if (glm::dot(glm::vec3(planes[i]), center) + planes[i].w < -radius)
			return false; // wholly on the outer side of this plane
	}
	return true; // not proven outside: kept
}

int main()
{
	const glm::vec4 planes[2] = { glm::vec4(1.0f, 0.0f, 0.0f, -1.0f), glm::vec4(0.0f, 1.0f, 0.0f, -1.0f) };
	std::printf("inside %d\n", SphereVisible(glm::vec3(3.0f, 3.0f, 0.0f), 0.5f, planes));
	std::printf("across %d\n", SphereVisible(glm::vec3(0.8f, 3.0f, 0.0f), 0.5f, planes));
	std::printf("outside %d\n", SphereVisible(glm::vec3(0.0f, 3.0f, 0.0f), 0.5f, planes));
	std::printf("near the corner %d\n", SphereVisible(glm::vec3(0.6f, 0.6f, 0.0f), 0.5f, planes));
}
```

```text output-of="basics-math-geometry-frustum.cpp"
inside 1
across 1
outside 0
near the corner 1
```

1. **Line 9:** the sphere test, the signed distance of the center against the negative radius.
2. **Line 12:** a sphere that no plane drops is kept, without a proof that it is inside.

The last 1 is the sphere near the corner: the test keeps something outside.

Keeping too much costs little: the renderer draws an object that the screen then clips. Dropping too much makes visible
objects vanish. So a test of this kind follows one rule: **it may keep something outside, but must never drop
something inside.** The same rule governs a bounding volume in front of an exact test.

A box works like the sphere. For each plane, take the corner of the box that lies farthest along the normal. If even
that corner is outside, the whole box is. [Bounds and culling](../draw/bounds-culling.md) extracts the six planes
from a matrix and covers this "positive vertex" test.

:::note[In Strata]
`Frustum` in `Strata/src/Strata/Math/Frustum.h` holds six inward-facing planes, each divided by the length of its
normal. With an infinite far plane, the :term[far plane]{id=far-plane} becomes one that never drops anything.
:::

## Two shapes do not touch when an axis separates them

Hold a flashlight in front of two shapes and look at their shadows on the wall. If the shadows do not overlap, the
shapes do not touch. A shape is **convex** when a straight line between any two of its points stays inside it: boxes,
spheres and triangles are convex.

A **separating axis** is a direction onto which the shadows of two convex shapes do not overlap. The shadow of a shape
on an axis is the range of the dot products of its corners with the axis: its lowest and highest values. If the two
ranges leave a gap, the shapes are apart. If no axis shows a gap, they touch.

Take a box from (0, 0) to (2, 2), and a triangle with the corners (3, 1.5), (1.5, 3) and (3, 3). On the x axis the box
casts the range 0 to 2 and the triangle 1.5 to 3: they overlap. On the y axis it is the same. Neither axis of the box
shows a gap, yet the shapes are apart.

The triangle's long side from (3, 1.5) to (1.5, 3) has the normal (1, 1). On that axis the box corners give 0, 2, 4
and 2, so the range is 0 to 4. The triangle corners give 4.5, 4.5 and 6, so the range is 4.5 to 6. A gap of 0.5 shows:
the axis (1, 1) separates them.

::figure{id=separating-axis}

Which axes do you try? For two boxes in 2D, the sides of both. In 3D, a triangle and a box need 13 axes to cover every
case. They are the 3 face normals of the box, the normal of the triangle, and the 9 cross products of a box edge
direction with a triangle edge. Stop at the first axis that shows a gap; if all 13 overlap, the shapes touch.

The sketch computes the shadows on three axes for the 2D case.

```cpp sketch="basics-math-geometry-separating.cpp"
#include <algorithm>
#include <cstdio>
#include <glm/glm.hpp>

glm::vec2 Shadow(const glm::vec2 corners[], int count, const glm::vec2& axis) // lowest and highest position on the axis
{
	glm::vec2 range(1e30f, -1e30f);
	for (int i = 0; i < count; i++)
	{
		range.x = std::min(range.x, glm::dot(axis, corners[i]));
		range.y = std::max(range.y, glm::dot(axis, corners[i]));
	}
	return range;
}

int main()
{
	const glm::vec2 box[4] = { glm::vec2(0.0f, 0.0f), glm::vec2(2.0f, 0.0f), glm::vec2(2.0f, 2.0f), glm::vec2(0.0f, 2.0f) };
	const glm::vec2 triangle[3] = { glm::vec2(3.0f, 1.5f), glm::vec2(1.5f, 3.0f), glm::vec2(3.0f, 3.0f) };
	for (const glm::vec2& axis : { glm::vec2(1.0f, 0.0f), glm::vec2(0.0f, 1.0f), glm::vec2(1.0f, 1.0f) })
	{
		const glm::vec2 a = Shadow(box, 4, axis), b = Shadow(triangle, 3, axis);
		std::printf("axis (%g, %g): box %g to %g, triangle %g to %g, %s\n", axis.x, axis.y, a.x, a.y, b.x, b.y, a.y < b.x || b.y < a.x ? "apart" : "overlap");
	}
}
```

```text output-of="basics-math-geometry-separating.cpp"
axis (1, 0): box 0 to 2, triangle 1.5 to 3, overlap
axis (0, 1): box 0 to 2, triangle 1.5 to 3, overlap
axis (1, 1): box 0 to 4, triangle 4.5 to 6, apart
```

1. **Lines 5–14:** the shadow of a list of corners on an axis: the lowest and the highest dot product.
2. **Line 23:** a gap exists when one range ends before the other starts.

The first two axes overlap and the third, (1, 1), is apart, as in the hand numbers. The axis does not need to be a
unit vector for this comparison: both shadows are scaled alike.

## Floating point turns exact tests into near misses

All the tests above are exact on paper. A computer stores floats, which hold about seven digits, and every operation
rounds. Add 0.1 ten times in floats, and the result is not 1.

```cpp sketch="basics-math-geometry-rounding.cpp"
// Rounding: a sum that should be 1, and a hit point that should lie exactly on its plane.
#include <cstdio>
#include <glm/glm.hpp>

int main()
{
	float sum = 0.0f;
	for (int i = 0; i < 10; i++)
		sum += 0.1f;
	std::printf("sum %.9g, equal to 1: %d, close to 1: %d\n", sum, sum == 1.0f, glm::abs(sum - 1.0f) < 1e-5f);

	const glm::vec3 normal = glm::normalize(glm::vec3(1.0f, 2.0f, 2.0f));
	const glm::vec3 origin(0.3f, 7.1f, 0.2f);
	const glm::vec3 direction = glm::normalize(glm::vec3(0.2f, -1.0f, 0.1f));
	const float t = -(glm::dot(normal, origin) - 1.0f) / glm::dot(normal, direction);
	const glm::vec3 hit = origin + direction * t;
	std::printf("distance of the hit point from the plane: %g\n", glm::dot(normal, hit) - 1.0f);
	return 0;
}
```

```text output-of="basics-math-geometry-rounding.cpp"
sum 1.00000012, equal to 1: 0, close to 1: 1
distance of the hit point from the plane: -2.38419e-07
```

1. **Lines 7–10:** ten additions of 0.1 do not make exactly 1: the equality test is false and the test with a
   tolerance is true.
2. **Lines 12–17:** the hit point of a ray on a tilted plane, whose signed distance should be 0.

The sum is 1.00000012, so the test for exact equality fails and a test for "close" passes. The second line is worse.
A point found by walking along a ray to a plane lies 2.4e-7 from the plane, not 0. A test of the kind `distance == 0`
fails on a hit that is right.

A **tolerance**, also called an epsilon, is a small distance within which two numbers count as equal. You write
`glm::abs(a - b) < tolerance`, never `a == b`. The right size depends on the numbers: floats near 1 are spaced about
1.2e-7 apart, near 1,000 about 6e-5 apart, and near 100,000 about 0.008. A tolerance of 1e-5 that works near 1 is
below the spacing near 1,000, so it behaves like `==` there. Scale it to the size of the values, or work in a space
where they stay small.

Too large a tolerance has a cost too. Strata guards a parallel ray with the limit 1e-8 on the slope, and 1e-12 for a box
slab. A ray tilted by less than that counts as parallel, though it would meet the plane very far away. These limits
trade a rare far hit against a division by a tiny number.

Degenerate inputs need their own answers. They are the cases where a formula divides by zero or has no meaning:

- A ray parallel to a plane or a slab: the slope or the direction is 0. Strata returns nothing for a plane and tests
  the origin against the slab. The slab sketch divides by 0 instead, which fails for an origin exactly on a slab plane.
- A box of zero size: its corners are equal. `AABB` stays valid, since `IsValid` uses "at most", and holds a single
  point or a flat sheet.
- A direction of zero length: normalizing divides by 0 and gives :term[NaN]{id=nan}, which fails every comparison, so a guard like
  `< 1e-8` lets it through. Check the length before you make a ray.

## Common mistakes

- **A hit at a negative t taken as a hit.** Symptom: a click "hits" an object behind the camera, or a shot hits the
  wall behind the shooter. Fix: reject every t below 0, as every Strata test does.
- **A plane normal that is not unit length.** Symptom: signed distances too big or too small by the normal's length, so
  a sphere is dropped or kept wrongly. Fix: normalize the normal and divide the offset by the same length.
- **Floats compared with `==`.** Symptom: a hit point that is "not on the plane", or a test that passes on one
  machine and fails on another. Fix: compare with a tolerance sized to the numbers.
- **A box whose minimum is larger than its maximum.** Symptom: the box overlaps nothing, contains nothing, and a ray
  misses it. Fix: build the corners with the lowest and highest value of each axis, or start empty and grow.

## Summary

- A ray is an origin plus t times a direction, with t from 0 upward. A plane has a unit normal and an offset, the signed
  distance of a point is `n · p + w`, and a ray meets the plane at `t = -(n · o + w) / (n · d)` unless it is parallel or
  the plane lies behind.
- A sphere holds a point at a distance of at most the radius, and two spheres overlap when their centers are closer
  than the two radii added. An AABB is a smallest and a largest corner, with one test per axis.
- A ray meets a sphere by solving a quadratic equation, a box by the latest slab entry and the earliest exit, and a
  triangle in its plane and inside its three edges.
- A frustum is six inward planes. A sphere is dropped when a signed distance is below its negative radius, and a test
  may keep what is outside but never drops what is inside. Shapes that do not touch have a separating axis.
- :term[Floating point]{id=floating-point-number} rounds every operation, so compare with a tolerance and handle the degenerate inputs: parallel rays,
  zero size and zero length.

## Check yourself

1. A ray test against a plane returns t = -2. What does the result say?

   - A. The plane is 2 units in front of the ray.
   - B. The plane lies behind the origin, so the ray does not hit it.
   - C. The ray is parallel to the plane.
   - D. The origin lies on the plane.

   :::answer{tests="rays-planes"}
   B. A negative t lies behind the origin. A is the mistake of reading the number as a distance without its sign. C
   gives no t at all, and D gives t = 0.
   :::

2. Spheres A and B have the centers (0, 0, 0) and (3, 4, 0) and the radii 2 and 3. Do they overlap?

   :::answer{tests="spheres-boxes"}
   Yes, they touch. The squared distance is 9 + 16 = 25, and the radii added are 5, whose square is 25. With "at
   most", touching counts as overlapping.
   :::

3. A ray from (0, 0) along (1, 0.5) is tested against the 2D box from (4, 4) to (6, 5). Does it hit?

   :::answer{tests="ray-tests"}
   No. The x slab gives t from 4 to 6, and the y slab gives 8 to 10. The latest entry, 8, is after the earliest exit, 6,
   so the ray leaves the x slab before it enters the y slab.
   :::

4. Which statement about a frustum test for spheres is true?

   - A. It may drop a sphere that is visible.
   - B. It may keep a sphere that is outside.
   - C. It is exact for every sphere.
   - D. It keeps every sphere.

   :::answer{tests="frustum-separating"}
   B. The test drops a sphere only when one plane proves it outside, and some outside spheres, near a corner of the
   frustum, pass all six planes. A would make objects vanish from the picture.
   :::

5. Which inputs can make a ray test divide by zero or produce NaN? (A) a ray parallel to a plane, (B) a box of zero
   size, (C) a ray of direction length 0, (D) a ray that starts inside a sphere.

   :::answer{tests="robustness"}
   A and C. Parallel means a slope of 0 in the division, and a zero direction cannot be normalized. A box of zero size is
   valid, and a ray inside a sphere has a negative smaller answer that the test handles.
   :::

## Practice

1. **Basic.** A plane goes through (0, 3, 0) with the unit normal (0, 1, 0). Give its offset, the signed distance of
   (5, 1, 2), and where a ray from (1, 6, 1) along (0, -1, 0) meets it.

   :::answer[Worked solution]{tests="rays-planes"}
   The offset is -(n · q) = -3. For (5, 1, 2): 1 - 3 = -2, below the plane. For the ray, the origin's distance is 6 - 3 =
   3 and n · d = -1, so t = 3, at the point (1, 3, 1).
   :::

2. **Medium.** A ray starts at (0, 0, 0) along (1, 0, 0). A sphere has the center (6, 1, 0) and the radius 2. Where does
   the ray enter it? What happens with the radius 0.5?

   :::answer[Worked solution]{tests="ray-tests"}
   Here $m$ = (-6, -1, 0), so $h$ = -6 and $c$ = 37 - 4 = 33. The part under the root is 36 - 33 = 3, so t = 6 - 1.73 =
   4.27. With the radius 0.5, $c$ = 36.75 and 36 - 36.75 is negative: the ray misses.
   :::

3. **Medium.** A triangle has the corners (0, 0), (2, 0) and (0, 2) and a box spans (1.5, 1.5) to (3, 3). Find an axis
   that separates them.

   :::answer[Worked solution]{tests="frustum-separating"}
   The axes x and y overlap: both shapes span 0 to 2 against 1.5 to 3. On the axis (1, 1), the triangle gives 0 to 2 and
   the box gives 3 to 6. The gap shows, so the shapes are apart.
   :::

4. **Hard.** Write a function that returns the box that holds a list of points, starting from an empty box. Run it on
   (1, 2, 0), (-1, 5, 2) and (0, 3, -4), and print what it returns for no points.

   :::answer[Worked solution]{tests="spheres-boxes robustness" solution="sketches/basics-math-geometry-enclose.cpp"}
   The empty box has its `Low` above its `High`, so the first point pulls both corners onto itself. With no points the
   box stays empty, and a program can see that `Low` is above `High`.

   ```cpp sketch="basics-math-geometry-enclose.cpp"
   #include <cstdio>
   #include <glm/glm.hpp>

   struct Box { glm::vec3 Low = glm::vec3(1e30f); glm::vec3 High = glm::vec3(-1e30f); }; // empty: Low is above High

   Box Enclose(const glm::vec3 points[], int count)
   {
   	Box box;
   	for (int i = 0; i < count; i++)
   	{
   		box.Low = glm::min(box.Low, points[i]);
   		box.High = glm::max(box.High, points[i]);
   	}
   	return box;
   }

   int main()
   {
   	const glm::vec3 points[3] = { glm::vec3(1.0f, 2.0f, 0.0f), glm::vec3(-1.0f, 5.0f, 2.0f), glm::vec3(0.0f, 3.0f, -4.0f) };
   	const Box box = Enclose(points, 3);
   	std::printf("low (%g, %g, %g), high (%g, %g, %g)\n", box.Low.x, box.Low.y, box.Low.z, box.High.x, box.High.y, box.High.z);
   	std::printf("no points: low.x %g, high.x %g\n", Enclose(points, 0).Low.x, Enclose(points, 0).High.x);
   }
   ```

   ```text output-of="basics-math-geometry-enclose.cpp"
   low (-1, 2, -4), high (1, 5, 2)
   no points: low.x 1e+30, high.x -1e+30
   ```

   1. **Line 4:** an empty box has its `Low` above its `High`.
   2. **Lines 9–13:** each point pulls the corners outward, never inward.
   :::

5. **Hard.** Optional, on your [Coin Run](../make/project-coin-run.md) or Checkpoint 4 of [Ship the finished game](../make/project-coin-run.md#ship-the-finished-game). In the ball's script, `BallControl`, in `OnFixedUpdate`, work out by
   hand whether the ball's bounding sphere touches one coin's box. Then log where a ray straight down from the ball
   meets the ground's plane, next to what `Physics::Raycast` returns.

   :::answer[Worked solution]{tests="rays-planes spheres-boxes"}
   Take the ball's center from `GetWorldPosition()` and its radius as half its width, using `GetWorldScale()`. Clamp
   the center into the coin's box, and compare the squared distance with the radius squared. For the ray, use the
   origin at the ball, the direction (0, -1, 0) and the ground's plane at its height $h$: the offset is $-h$, and $t$ is
   the ball's height minus $h$. The `Physics::Raycast` hit gives `Distance` and `Point`. Pass the ball as `ignore`, so that the ray skips the ball's
   own body; on flat ground the two numbers agree to a tolerance.

   ```pseudocode
   const float t = ballPosition.y - groundHeight;
   Log::Info("plane t ", t, ", Raycast ", hit ? hit->Distance : -1.0f);
   ```

   The first line is the plane test, and the second prints it beside the hit.
   :::

## Where the book uses it

- [Bounds and culling](../draw/bounds-culling.md) tests each object's bounding box or sphere against the six planes of
  the frustum, so the renderer skips what the camera cannot see.
- [Collision detection](../physics/collision-detection.md) uses bounding volumes and separating axes to decide which
  bodies touch.
- [Queries](../physics/queries.md) answers ray casts and shape tests with the same ray, box and sphere tests.
- [Placement](../editor/placement.md) puts content where the cursor's ray meets a surface.
- [Interface input](../ui/input.md) hits elements of the game's user interface (UI) in the world with the camera's ray.

## Further reading

- Christer Ericson, *Real-Time Collision Detection* (Morgan Kaufmann, 2004): chapters 4 and 5 treat bounding volumes
  and the tests of this page, with attention to rounding; advanced.
- Tomas Möller and Ben Trumbore, "Fast, Minimum Storage Ray/Triangle Intersection" (Journal of Graphics Tools, 1997):
  the method behind the triangle test; advanced.
