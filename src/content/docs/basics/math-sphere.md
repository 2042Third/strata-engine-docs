---
id: basics/math-sphere
title: "Directions on a sphere: solid angles, spherical harmonics and octahedral maps"
description: "How a game stores and adds up a value for every direction: spherical coordinates, solid angles, three picture layouts for the sphere, and spherical harmonics."
kind: primer
size: L
tracks: [B, E]
needs: [basics/math-probability]
time: 80
learn:
  - id: coordinates
    text: compute the polar angle and the azimuth of a direction, and the direction of a given pair of angles
  - id: maps
    text: find where a direction lands in an equirectangular map, a cube map and an octahedral map
  - id: solid-angle
    text: compute the solid angle of a cone, a hemisphere and a small disk
  - id: sphere-integral
    text: explain why a sum over the sphere weights each piece by sin θ, and draw cosine-weighted directions
  - id: spherical-harmonics
    text: compute the first coefficients of a light and evaluate them back, and explain ringing
status: final
---

::::test-out

1. A direction is (0, -0.6, 0.8), with +Y up. Compute its polar angle and its azimuth.

   :::answer{tests="coordinates"}
   The polar angle is acos(-0.6) = 126.9°, below the horizon because y is negative. The azimuth is atan2(0.8, 0) = 90°.
   :::

2. Which face of a cube map holds the direction (-0.2, 0.3, -0.9), and which pair of numbers places it on that face?

   :::answer{tests="maps"}
   The largest coordinate is z, with size 0.9, and it is negative: the -Z face. Divide the other two by 0.9 to get
   (-0.22, 0.33).
   :::

3. A lamp lights a cone of directions with an angular radius of 60°. Compute its solid angle.

   :::answer{tests="solid-angle"}
   2π (1 - cos 60°) = 2π × 0.5 = π, about 3.14 steradians: a quarter of the whole sphere, 4π.
   :::

4. A light has the value 3 in every direction. Compute its integral over the whole sphere.

   :::answer{tests="sphere-integral"}
   The value times the solid angle of the sphere: 3 × 4π = 12π, about 37.7.
   :::

5. How many numbers do bands 0 to 2 of the spherical harmonics need for one colour channel, and how many for red, green
   and blue?

   :::answer{tests="spherical-harmonics"}
   Band 0 has 1 pattern, band 1 has 3 and band 2 has 5, so 9 numbers. Three channels need 27.
   :::

::::

## Why you will need this

A game keeps many things that depend on a direction: the sky seen from a point, the light that reaches a surface, the way
a surface faces. Each needs a rule that turns a direction into a place in memory, and a way to add up what arrives from
all directions.

[Units and exposure](../light/units-exposure.md) measures light per solid angle, and [the sky](../light/sky.md) works
with the directions of the sun. [Image-based lighting](../indirect/ibl.md) stores the sky in a cube map, and
[reflection probes](../indirect/probes.md) project what they see onto nine spherical harmonics per colour. [Global
illumination cascades](../indirect/gi-cascades.md) store the rays of a probe in an octahedral square.

Only the optional Coin Run exercise needs a project. Each sketch is a whole program: save it as `sketch.cpp` and compile it in the terminal of [How a C++ program is built](build.md#open-a-terminal-that-finds-a-compiler), with C++20 and the `glm` headers of your Strata folder. On Windows, run `cl /std:c++20 /EHsc /I "<Strata folder>\StrataScriptCore\ThirdParty\glm" sketch.cpp` and then `.\sketch.exe`. On Linux and macOS, run `c++ -std=c++20 -I "<Strata folder>/StrataScriptCore/ThirdParty/glm" sketch.cpp -o sketch` and then `./sketch`. Without a compiler, read each output and its notes.

## A direction is a point on the unit sphere

A direction in a game is a vector of length 1: the way a light shines, a surface faces or a camera looks. Collect every
such vector and you get the **unit sphere**, the set of all points at distance 1 from the origin. Each direction is one
point of it, and each point is one direction.

The vector has three numbers, but its length ties them together: $x^2 + y^2 + z^2 = 1$. Two numbers are free and the
third follows. Two angles are enough, as when you point at a star and say how high it stands and which way round.

**Spherical coordinates** name a direction by two angles instead of three numbers. Strata's world has +Y up, so the first
angle counts from +Y.

The **polar angle** is the angle between the direction and the :term[up axis]{id=up-axis}: 0° for straight up, 90° for level with the
horizon and 180° for straight down.

The **azimuth** is the angle around the up axis, measured from +X toward +Z.

[Yaw and pitch](../basics/math-rotations.md) are the same two turns, with one change: pitch counts up from the horizon,
so the polar angle is 90° minus the pitch.

::figure{id=polar-azimuth}

To turn the angles into a direction, use the polar angle for the height and the azimuth for the place on the circle at
that height:

$$
d = (\sin\theta \cos\varphi,\ \cos\theta,\ \sin\theta \sin\varphi)
$$

$d$ is the direction, $\theta$ is the polar angle and $\varphi$ is the azimuth, both in :term[radians]{id=radian}. The height is
$\cos\theta$: 1 at the top, 0 on the horizon and -1 at the bottom. The circle at that height has the radius
$\sin\theta$, and $\cos\varphi$ and $\sin\varphi$ place the point on it along X and along Z.

The way back uses the inverse functions:

$$
\theta = \operatorname{acos}(d_y), \qquad \varphi = \operatorname{atan2}(d_z, d_x)
$$

$d_x$, $d_y$ and $d_z$ are the three numbers of the direction. `acos` is the inverse of the :term[cosine]{id=cosine}, and its input must lie
between -1 and 1. `atan2(z, x)` gives the angle of the point (x, z), from -180° to 180°. Unlike the inverse tangent of z
divided by x, it reads both signs and so finds the right quarter of the circle.

:::example[From a direction to two angles and back]
Take $d$ = (0.5, 0.5, 0.7071). Its length is √(0.25 + 0.25 + 0.5) = 1. The polar angle is acos(0.5) = 60°, and the
azimuth is atan2(0.7071, 0.5) = 54.7°.

Now return. sin 60° = 0.866, cos 54.7° = 0.577 and sin 54.7° = 0.816, so the direction is (0.866 × 0.577, 0.5, 0.866 ×
0.816) = (0.5, 0.5, 0.707), the start.
:::

Check the limits. Straight up is (0, 1, 0), with the polar angle 0. There x and z are both 0, so `atan2(0, 0)` has no
answer: at the poles the azimuth means nothing, because every azimuth gives the same point. Code that reads the azimuth
must handle that case.

Try it: the direction is (-0.6, 0.8, 0). Compute its polar angle and azimuth.

:::answer
The polar angle is acos(0.8) = 36.9°. The azimuth is atan2(0, -0.6) = 180°, because the direction points along -X.
:::

## An equirectangular map stretches the poles

A picture holds one value per pixel, and a sky holds one value per direction. The oldest way to connect them is to lay
the two angles flat: the azimuth gives the column and the polar angle gives the row.

The result is an **equirectangular map**: a picture whose columns step evenly in azimuth and whose rows step evenly in
polar angle. It is twice as wide as it is tall, because the azimuth covers 360° and the polar angle only 180°.

::figure{id=equirect-map}

Both coordinates of the picture run from 0 to 1. The column is the azimuth divided by 2π, shifted by one half so that it
is never negative, and the row is the polar angle divided by π.

:::example[The pixel of a direction]
The map is 1024 pixels wide and 512 high. The direction (0.5, 0.5, 0.7071) has the azimuth 54.7° and the polar angle
60°. The column is 54.7 / 360 + 0.5 = 0.652, and the row is 60 / 180 = 0.333.

Multiply by the size: 0.652 × 1024 = 667.7 and 0.333 × 512 = 170.7. Drop the fractions: the pixel is column 667, row
170, counted from 0 at the left and the top.
:::

Try it: which pixel of the same map holds the direction (0, 0, -1)?

:::answer
The azimuth is atan2(-1, 0) = -90°, so the column is -90 / 360 + 0.5 = 0.25, which is 256. The polar angle is 90°, so
the row is 0.5, which is 256. The pixel is (256, 256).
:::

The layout has a cost. A row at polar angle $\theta$ is a circle of radius $\sin\theta$, but the picture gives every row
the same 1024 pixels. At 60° the circle is 0.866 times as long as at the horizon, so its pixels are stretched 1.15
times. At 10° the stretch is 5.8 times. In the top row the whole circle shrinks to one point, and all 1024 pixels show
the same direction.

Strata reads such maps with `DirectionToEquirect`. Its shaders are written in Slang, whose form is close to C++ and
`glm`. A `float2` or `float3` is a vector of two or three numbers like `glm::vec2`, `.x` and `.xy` take components, and
`a ? b : c` works as in C++. The function turns a direction into the pair (column, row), each from 0 to

1. Look at the condition inside the line that makes `u`.

```slang src="Strata/shaders/Include/IBL.slang#L26-L34" symbol="DirectionToEquirect"
// Equirectangular (latitude-longitude) coordinates of a direction: u around +Y starting at -X, v from +Y (top row)
// to -Y (bottom row).
float2 DirectionToEquirect(float3 direction)
{
	// atan(0, 0) is undefined: straight up or down, where every column is the same direction, the middle one is read.
	float u = (direction.x != 0.0 || direction.z != 0.0 ? atan2(direction.z, direction.x) : 0.0) / TWO_PI + 0.5;
	float v = acos(clamp(direction.y, -1.0, 1.0)) / PI;
	return float2(u, v);
}
```

The line of `u` is the column: `atan2(direction.z, direction.x)` divided by `TWO_PI` and shifted by 0.5, so -180° gives
0 and 180° gives 1. The condition before it is the pole check from above: when x and z are both 0, the function uses 0
instead of calling `atan2(0, 0)`, which lands on the middle column. The line of `v` is the row: `acos` of the height,
clamped to the range -1 to 1, divided by `PI`. The clamp matters because rounding can leave a :term[unit vector]{id=unit-vector} with a height
of 1.0000001, and `acos` has no answer there.

## A cube map picks a face by the largest coordinate

A cube map avoids the poles by using six square pictures, one for each face of a cube around the origin. A direction
points through exactly one face. The direction (0, 1, 0) leaves through the top, and (0.3, 0.2, 0.9) leaves
through the +Z face.

To find the face, take the coordinate with the largest size. Its axis names the face, and its sign names the side.
Strata keeps the faces in the order +X, -X, +Y, -Y, +Z, -Z. To find the place on the face, scale the direction until the
largest coordinate is exactly 1 or -1. The other two numbers then lie between -1 and 1.

::figure{id=cube-map}

:::example[Face and place]
Take the direction (-0.2, 0.3, -0.9). The coordinate with the largest size is z, 0.9, and it is negative, so the face is
-Z. Divide by 0.9: the direction becomes (-0.222, 0.333, -1), and the place on the face is (-0.222, 0.333).

A face of 128 pixels turns each number into a pixel with (a + 1) / 2 × 128. That gives 49.8 and 85.3, so the pixel is
(49, 85) in the face's own picture.
:::

Two details need care. When two coordinates tie, such as (0.7, 0, 0.7), either face is right, because both give the same
point on the shared edge. And which way each face's picture runs is a convention that differs between graphics
interfaces: [Image-based lighting](../indirect/ibl.md) gives Strata's.

A face is what a camera sees with a field of view of 90°, as in [Cameras and projection](../basics/math-projection.md).
The cost is that pixels are not equal: those in a face's corners cover less of the sphere than those in its middle. The
section on integrals measures by how much.

## An octahedral map unfolds the sphere into one square

A cube map needs six pictures. An **octahedral map** needs one: a square picture of the whole sphere, made by wrapping
the sphere in an octahedron, a solid of eight triangles, and unfolding that into a square.

Picture two pyramids glued base to base. Their corners lie on the six axes at distance 1 from the centre, and every point
of their surface satisfies $|x| + |y| + |z| = 1$. Three steps take a direction onto the square:

1. Divide the direction by $|x| + |y| + |z|$. That slides the point along its line until it touches the octahedron.
2. Look at the half with z at least 0 from above. It is a diamond, and its points keep their x and y as their place in
   the square.
3. Cut the other half into its four triangles and fold them outward over the corners of the square.

::figure{id=octahedral-unfolded}

**Octahedral encoding** stores a unit vector as the two numbers of its place in an octahedral map. A normal has three
numbers, but its length is fixed, so two suffice.

:::example[A vector below the horizon]
Take n = (-0.2, 0.4, -0.8944). The sum of the sizes is 0.2 + 0.4 + 0.8944 = 1.4944, so the point on the octahedron is
(-0.1338, 0.2677, -0.5985). Its z is negative: the point lies in the half that folds.

Fold it: swap x and y, take 1 minus their sizes, and give the results the signs of the original x and y. The pair is
((1 - 0.2677) × -1, (1 - 0.1338) × 1) = (-0.7323, 0.8662).
:::

To reverse it, rebuild z as 1 - |x| - |y| = -0.5985. That is below 0, so the point was folded: move x and y back toward
0 by that amount, and divide by the length 0.6692 to get n = (-0.2, 0.4, -0.8944).

The functions below are Strata's. Read them with these Slang notes: `n /= s` divides all three numbers, `n.xy` is the
first two components and `n.yx` the same two swapped, and `float2(a, b)` builds a pair. Look at the line that tests the
sign of z.

```slang src="Strata/shaders/Include/Scene.slang#L380-L395"
// Octahedral encoding of unit vectors into [-1, 1]^2 (normal G-buffer).
float2 OctahedralEncode(float3 n)
{
	n /= abs(n.x) + abs(n.y) + abs(n.z);
	float2 encoded = n.z >= 0.0 ? n.xy : (1.0 - abs(n.yx)) * float2(n.x >= 0.0 ? 1.0 : -1.0, n.y >= 0.0 ? 1.0 : -1.0);
	return encoded;
}

float3 OctahedralDecode(float2 encoded)
{
	float3 n = float3(encoded, 1.0 - abs(encoded.x) - abs(encoded.y));
	float t = max(-n.z, 0.0);
	n.x += n.x >= 0.0 ? -t : t;
	n.y += n.y >= 0.0 ? -t : t;
	return normalize(n);
}
```

1. **Line 383:** the division by the sum of the sizes puts the vector on the octahedron.
2. **Line 384:** the upper half keeps `n.xy`. The lower half folds with `1.0 - abs(n.yx)`, then takes the signs of x and
   y.
3. **Lines 390–391:** the reverse rebuilds z from the octahedron's rule. `t` is how far below 0 that z fell, which is how
   far the point was folded.
4. **Lines 392–393:** each of x and y moves toward 0 by `t`, which undoes the fold.
5. **Line 394:** the point is on the octahedron, not on the sphere, so `normalize` restores the length 1.

Strata uses the pair for normals. The depth prepass writes each pixel's normal, in view space, with `OctahedralEncode`
into a target of the format `RG16_FLOAT`, two 16-bit :term[floating-point numbers]{id=floating-point-number}, set in
`Strata/src/Strata/Renderer/SceneRenderer.cpp`. Three such numbers would take half again as much memory. Passes such as
[screen-space reflections](../indirect/ssr.md) read the pair back with `OctahedralDecode`.

The map has no pole where pixels pile up, and its pixels differ by a factor of about 5 in the solid angle they cover, as
in a cube face. It has costs of its own. Never average two stored pairs near a fold: reverse both first. And the point
(0, 0, -1) appears at all four corners, so one direction has several places. The rays of a probe in [Global illumination
cascades](../indirect/gi-cascades.md) use the same layout.

Try it: reverse the pair (0.5, 0.25).

:::answer
z = 1 - 0.5 - 0.25 = 0.25, which is not below 0, so nothing was folded. The vector (0.5, 0.25, 0.25) has the length
0.612, so n = (0.816, 0.408, 0.408).
:::

## A solid angle measures a patch of directions

On a flat page, an angle in radians is the length of arc that it cuts from a circle of radius 1. On the sphere the
matching measure is an area. The **solid angle** of a set of directions is the area they cut from the unit sphere.

Its unit is the **steradian**. The unit sphere has the area 4π, about 12.57, so the whole sphere is 4π steradians.

A **hemisphere** is the half of the sphere on one side of a plane through its centre, such as all directions above a
surface. It is 2π steradians.

A patch of area $A$ at distance $r$, facing the centre, has the solid angle $A / r^2$, because a sphere of radius $r$ has
$r^2$ times the area of the unit one. A panel of 2 m by 2 m, 10 m away and facing you, covers 4 / 100 = 0.04 steradians.
At 20 m it covers 0.01: doubling the distance cuts the solid angle to a quarter. Light follows the same inverse square.

The shape you meet most is the cone: all directions within an angle $\alpha$ of an axis. It cuts a cap from the unit
sphere.

::figure{id=cone-solid-angle}

$$
\Omega = 2\pi\,(1 - \cos\alpha)
$$

$\Omega$ is the solid angle in steradians, $\alpha$ is the angular radius of the cone, the angle between its axis and its
edge, and $\pi$ is about 3.14159. The factor $(1 - \cos\alpha)$ is the height of the cap, and the next section derives
the formula.

Check the limits. At $\alpha$ = 0 the cone is one direction, and $\Omega$ = 0. At 90° the cone is a hemisphere: 2π × 1 =
2π. At 180° it is the whole sphere: 2π × 2 = 4π. For a small angle, $(1 - \cos\alpha)$ is close to $\alpha^2 / 2$, so
$\Omega$ is close to $\pi\alpha^2$, the area of a flat disk of radius $\alpha$.

:::example[A cone and the sun]
A cone with an angular radius of 60° has 2π (1 - 0.5) = π = 3.14 steradians, a quarter of the sphere.

The sun is about 0.53° across, so its angular radius is 0.2665°, which is 0.00465 radians. A flat disk of that radius
has π × 0.00465² = 6.8 × 10⁻⁵ steradians, one 185,000th of the sphere.
:::

## An integral over the sphere weights each piece by its size

The goal is to add up a value that depends on direction, such as the light from every direction. Cut the sphere into
small pieces, multiply the value of each piece by its solid angle, and add. That sum is the integral over the sphere: the
area under a curve of [Rates of change](../basics/math-change.md), moved onto a sphere.

Cut along the angles, with rows of the polar step $\Delta\theta$ and columns of the azimuth step $\Delta\varphi$. A piece
at polar angle $\theta$ is $\Delta\theta$ high, from top to bottom. Along its row it is $\sin\theta\,\Delta\varphi$ wide,
because the row is a circle of radius $\sin\theta$. The area of the piece is the product:

$$
d\omega = \sin\theta \, d\theta \, d\varphi
$$

$d\omega$ is the solid angle of a very small piece, and $d\theta$ and $d\varphi$ are the small steps of the two angles.
The weight $\sin\theta$ is 1 on the horizon and 0 at the poles, where the rows shrink to points. Without it, a sum over
equal steps counts a piece at the pole as large as one on the horizon.

:::example[Four rows, with and without the weight]
Cut the sphere into 4 rows of 45°. The middles of the rows are at 22.5°, 67.5°, 112.5° and 157.5°, with sin θ = 0.383,
0.924, 0.924 and 0.383. Each row spans the full 2π of azimuth, so the area is 2π × (π / 4) × (0.383 + 0.924 + 0.924 +
0.383) = 12.90. The true area is 4π = 12.57, so the sum is 2.6 % too high.

Without the weight, every row counts as 2π × π / 4, and the sum is 2π² = 19.74, which is 57 % too high.
:::

Practice 2 runs the same sum as a program. With 64 rows the weighted sum reaches 12.568, while the flat sum stays at
19.74 however many rows it uses.

:::question[What do `#include`, `std::` and `&` mean in the practice programs?]
Each `#include` brings in a library, `std::sin(x)` calls the library's function `sin`, and `&` in `const glm::vec3& n`
passes the vector without a copy. [Programming 3](../basics/programming-3.md) explains all three.
:::

The same weight gives the cone formula. A cone of angular radius $\alpha$ covers the polar angles from 0 to $\alpha$ and
the whole azimuth, so its solid angle is 2π times the sum of $\sin\theta\,d\theta$ from 0 to $\alpha$. That sum is the
height of the cap, $(1 - \cos\alpha)$.

A surface receives light weighted by the cosine of the angle to its normal, because light that arrives at a slant
spreads over more surface ([Units and exposure](../light/units-exposure.md) explains why). With the normal as the pole,
the integral of that weight over the hemisphere is:

$$
\int_{\text{hemisphere}} \cos\theta \, d\omega = 2\pi \int_0^{\pi/2} \cos\theta \sin\theta \, d\theta = 2\pi \cdot \tfrac{1}{2} = \pi
$$

The symbols are those of the last display, and $\int$ reads "the sum of". The inner sum is the area under the curve cos θ
sin θ, which is ½ sin 2θ, from 0 to π/2: a bump of height ½ and width π/2, so its area is ½. The result π is why a
uniform light of strength 1 above a surface adds up to π, and why diffuse shading divides by π.

### Drawing directions with a cosine density

The Monte Carlo method of [Probability and Monte Carlo](../basics/math-probability.md) estimates an integral from random
samples: the average of $f / p$, the value divided by the density of the draw. On the sphere the density is per
steradian, and for a uniform draw over a hemisphere it is 1 / 2π. When the value has the factor cos θ, a draw with that
factor in its density is better:

$$
p(\omega) = \frac{\cos\theta}{\pi}
$$

$p$ is the density and $\omega$ a direction. The density adds up to π / π = 1 over the hemisphere, as every density must.
Each sample has the cosine in both $f$ and $p$, so it cancels, and the estimate is less noisy where the light is smooth.

To draw from it, take two uniform numbers $\xi_1$ and $\xi_2$ in [0, 1). The azimuth is uniform: $\varphi$ = 2π $\xi_1$.
The share of directions within the angle $\theta$ of the normal is $\sin^2\theta$ (the sum above, up to $\theta$, divided
by π), so set $\sin^2\theta = \xi_2$. Then $\sin\theta = \sqrt{\xi_2}$ and $\cos\theta = \sqrt{1 - \xi_2}$.

For example, $\xi$ = (0.25, 0.75) gives the azimuth 90°, the cosine √0.25 = 0.5 and the :term[sine]{id=sine} √0.75 = 0.866, so the polar
angle is 60°. Half of all draws fall within 45° of the normal, since sin² 45° = 0.5. A uniform draw would put only 29 %
there.

Strata's `SampleCosineHemisphere` does exactly this. Its frame is the normal's: `TangentBasis(normal)` makes three
perpendicular axes, the tangent, the `bitangent` and the normal, as the columns of a matrix ([Bases and
frames](../basics/math-bases.md)). The function `mul` multiplies a matrix by a vector, so the last line carries the local
direction, with the normal as its third number, to the world. Look at how the square roots match the formulas above.

```slang src="Strata/shaders/Include/IBL.slang#L59-L65" symbol="SampleCosineHemisphere"
float3 SampleCosineHemisphere(float2 xi, float3 normal)
{
	float phi = TWO_PI * xi.x;
	float cosTheta = sqrt(1.0 - xi.y);
	float sinTheta = sqrt(xi.y);
	return mul(TangentBasis(normal), float3(sinTheta * cos(phi), sinTheta * sin(phi), cosTheta));
}
```

`xi` holds the two numbers. The first line makes the azimuth `phi` from `xi.x`, and the next two give the cosine and the
sine of the polar angle from `xi.y`. The last line builds the local direction and turns it into a world direction. The
irradiance pass in `Strata/shaders/IBL/Irradiance.comp.slang` calls it with a spread-out list of number pairs, not random
ones, to average the sky around each normal.

### The solid angle of a pixel of a cube map

The pixels of a cube map differ in size, and a sum over them needs their solid angles. Put a face at distance 1, with
points (s, t, 1) for s and t from -1 to 1. A pixel there has the area $h^2$, where $h$ is its width. Its distance to the
centre is $r = \sqrt{1 + s^2 + t^2}$, and it faces the centre at a slant with the cosine $1 / r$. A patch of area $A$,
distance $r$ and slant cosine $c$ has the solid angle $A c / r^2$, so the pixel has $h^2 / r^3$.

For a face of 64 pixels, $h$ = 2 / 64. In the middle $r$ = 1 and the pixel covers 0.00098 steradians. In the corner $r$ is
√3 = 1.73, so the pixel covers 0.00019: 5.2 times less. All 6 × 64² pixels add up to 12.567, which is 4π to four digits.
[Reflection probes](../indirect/probes.md) use these weights, in `Strata/shaders/IBL/ProbeIrradiance.comp.slang`, when
they project a cube map onto spherical harmonics.

## Basis functions add fixed patterns to approximate a shape

Often the full value for every direction is too much to keep. A **basis function** is one of a small, fixed set of
patterns that, each multiplied by a weight and all added, approximate a shape. A recipe of a few weights takes the place
of the whole shape.

Start on a line, from -1 to 1. Three patterns will do: a flat level $b_0$ = 0.7071, a ramp $b_1$ = 1.2247 x, and a bowl
$b_2$ = 1.5811 × (3x² - 1) / 2. Each is scaled so that its square, summed over the line, gives 1, and any two different
ones multiplied and summed give 0: they do not overlap.

To find the weight of one pattern, multiply the shape by that pattern and sum over the line. The other patterns in the
shape drop out, and its own part stays:

$$
c_i = \int_{-1}^{1} f(x)\, b_i(x)\, dx
$$

$f$ is the shape, $b_i$ is the pattern with the number $i$, and $c_i$ is its weight. Finding the weights is
**projecting** the shape onto the patterns. Adding the weighted patterns, $c_0 b_0 + c_1 b_1 + c_2 b_2$, evaluates the
approximation.

:::example[Approximating (1 + x)²]
For $f$ = (1 + x)² the sums give $c_0$ = 1.886, $c_1$ = 1.633 and $c_2$ = 0.422. With only the first two patterns, the
approximation is 1.886 × 0.7071 + 1.633 × 1.2247 x = 1.333 + 2x, the best straight line.

At x = 0 it gives 1.33 for the true 1, and at x = -1 it gives -0.67 for the true 0: the approximation is negative where
the shape never is. The third pattern adds 0.422 × 1.5811 × (3x² - 1) / 2 = x² - 0.333, and the sum is exactly 1 + 2x +
x².
:::

Try it: evaluate 1.333 + 2x at x = 0.5, and compare it with (1 + 0.5)².

:::answer
The line gives 1.333 + 1 = 2.333, and the true value is 2.25. The error is 0.083, about 4 %.
:::

## Spherical harmonics are basis functions for the sphere

**Spherical harmonics** (SH) are the standard basis functions of the sphere: patterns of direction in groups called
bands, which do not overlap, like the three patterns on the line. Band $l$ holds $2l + 1$ patterns, each a formula in x,
y and z. Bands 0, 1 and 2 hold 1, 3 and 5, so bands 0 to 2 give nine.

Band 0 is a constant: the average level. Band 1 leans toward one axis, with a positive side and a negative side. Band 2
has products of two coordinates, with two positive and two negative regions. A higher band changes sign faster.

::figure{id=sh-patterns}

Strata's nine patterns come from `ProbeSHBasis` in `Strata/shaders/Include/SphericalHarmonics.slang`. The order is a
convention, and the table gives Strata's:

| Number | Band | Pattern of the direction (x, y, z) |
| --- | --- | --- |
| 0 | 0 | 0.282095 |
| 1 | 1 | 0.488603 y |
| 2 | 1 | 0.488603 z |
| 3 | 1 | 0.488603 x |
| 4 | 2 | 1.092548 x y |
| 5 | 2 | 1.092548 y z |
| 6 | 2 | 0.315392 (3 z² - 1) |
| 7 | 2 | 1.092548 x z |
| 8 | 2 | 0.546274 (x² - y²) |

The constants scale each pattern so that its square, summed over the sphere, gives 1. Check two. For pattern 0,
0.282095² × 4π = 1. For pattern 1, 0.488603² times the sum of y² over the sphere, 4π / 3, gives 1.

Projection and evaluation read as on the line, with the sum weighted by solid angle:

$$
c_i = \int_{\text{sphere}} L(\omega)\, Y_i(\omega)\, d\omega, \qquad \tilde{L}(\omega) = \sum_{i=0}^{8} c_i\, Y_i(\omega)
$$

$L$ is the light as a function of direction, $Y_i$ is the pattern with the number $i$, and $c_i$ is its coefficient: the
weight of that pattern. $\tilde{L}$ is the approximation, and $\sum$ reads "the sum over". Nine coefficients per colour
channel replace the whole function.

:::example[A sky with a sharp horizon]
Let $L$ be 1 for every direction above the horizon (y > 0) and 0 below it. For $c_0$ the sum covers the upper hemisphere
only: 0.282095 × 2π = 1.7725. For $c_1$, pattern 1 is 0.488603 y, and the sum of y over the upper hemisphere is π, the
cosine sum of the last section, so $c_1$ = 0.488603 × π = 1.5350.

By symmetry the other seven coefficients are 0: each of those patterns has equal positive and negative parts over the
upper hemisphere. The evaluation is 1.7725 × 0.282095 + 1.5350 × 0.488603 y = 0.5 + 0.75 y.
:::

Practice 4 confirms these numbers with a program.

Now compare 0.5 + 0.75 y with the true sky. At the top, y = 1, it gives 1.25 for the true 1. At y = -1 it gives -0.25
for the true 0.

That rise above the true value on one side of an edge and fall below it on the other, as when a cut-off series swings
beside a sharp edge, is **ringing**. Here it makes light negative below y = -2 / 3, which no real light is. Strata's
[reflection probes](../indirect/probes.md) raise a negative result to 0 in `EvaluateProbeIrradiance`.

The patterns of band $l$ change sign about $l$ times around the sphere, so nine patterns can show only light that changes
slowly with direction. A sky that fades from bright above to dark below is a good fit. The sun, at 6.8 × 10⁻⁵
steradians, is not: the best nine-number fit spreads it over half the sphere and swings elsewhere. What a surface
receives fits better, because the cosine weight blurs the light. More bands sharpen the fit, at 16 numbers per channel
for bands 0 to 3 and 25 for bands 0 to 4.

Try it: evaluate 0.5 + 0.75 y for y = 0.5 and for y = -0.5.

:::answer
The values are 0.875 and 0.125. The true light is 1 above the horizon and 0 below, so both are off by 0.125.
:::

## Common mistakes

- **The weight sin θ omitted from a sum over the sphere.** Symptom: a total that is too large, 57 % in the example above.
  Fix: multiply each piece of a grid of rows and columns by its solid angle, $\sin\theta\,\Delta\theta\,\Delta\varphi$.
- **The poles of an equirectangular map read as ordinary rows.** Symptom: a streak at the top and bottom, or no number
  at all from `atan2(0, 0)` or from `acos` of a value a little above 1. Fix: guard the azimuth at the poles and clamp the
  input of `acos`.
- **Too few bands for sharp light.** Symptom: a sun or a bright window that smears over the whole sky, with negative
  light on the far side. Fix: keep sharp light out of the spherical harmonics, or use more bands.

## Summary

- A direction is a point on the unit sphere. The polar angle and the azimuth name it, and sine, cosine, `acos` and
  `atan2` convert both ways. At the poles the azimuth has no value.
- An equirectangular map crowds its pixels at the poles, and a cube map picks its face by the largest coordinate. An
  octahedral map folds the sphere into one square, and octahedral encoding stores a unit vector in two numbers.
- A solid angle is an area on the unit sphere, in steradians: 4π for the sphere, 2π for a hemisphere and 2π (1 - cos α)
  for a cone of angular radius α.
- A sum over the sphere weights each piece by sin θ. The cosine-weighted sum over a hemisphere is π, and a cosine density
  draws directions with cos θ = √(1 - ξ).
- Spherical harmonics of bands 0 to 2 are nine patterns. Their coefficients are sums of the light times each pattern,
  and adding them back evaluates the light. They fit slow changes, and a sharp edge makes the sum ring.

## Check yourself

1. A direction has the polar angle 90° and the azimuth -90°. Which direction is it? (a) (0, 0, -1) (b) (0, 0, 1)
   (c) (0, -1, 0) (d) (-1, 0, 0)

   :::answer{tests="coordinates"}
   (a). The direction is (sin 90° cos(-90°), cos 90°, sin 90° sin(-90°)) = (0, 0, -1). (b) has the azimuth +90°, (c)
   has the polar angle 180° and (d) has the azimuth 180°.
   :::

2. In an equirectangular map of 512 by 256 pixels, a direction lies on the horizon. Which row holds it? (a) 0 (b) 128
   (c) 256 (d) it depends on the azimuth

   :::answer{tests="maps"}
   (b). The horizon is the polar angle 90°, so the row is 0.5 × 256 = 128, for every azimuth. (a) is the top row, the
   pole, (c) lies past the bottom edge, and (d) mixes up the row with the column.
   :::

3. Which is larger: the solid angle of a cone of angular radius 45°, or a quarter of a hemisphere?

   :::answer{tests="solid-angle"}
   The cone: 2π (1 - cos 45°) = 1.84 steradians, against 2π / 4 = 1.57. The cone widens in two directions at once, so it
   takes more than a quarter.
   :::

4. A program estimates the area of the sphere with 100 rows of 2π × π / 100 each, and gets 19.74. Which mistake gives
   this? (a) too few rows (b) the weight sin θ is missing (c) degrees instead of radians (d) the azimuth has the wrong
   range

   :::answer{tests="sphere-integral"}
   (b). Without the weight the sum is 2π² = 19.74 for any number of rows, so (a) is not the cause. (c) and (d) would
   change the result in other ways.
   :::

5. A sky fades smoothly from bright above to dim at the horizon. Which fit holds it best? (a) bands 0 to 2 (b) none: the
   bands cannot hold a gradient (c) bands 0 to 2, but only with the sun in the sky

   :::answer{tests="spherical-harmonics"}
   (a). A smooth fade is the kind of light that the low bands hold, and band 1 is the gradient pattern. (b) is not true,
   and (c) adds a condition that is not needed.
   :::

## Practice

1. **Basic.** In an equirectangular map of 2048 by 1024 pixels, which pixel holds the direction (0.6, 0, 0.8)? Which cube
   face holds it? Compute the solid angle of a cone of angular radius 45° as a share of the whole sphere.

   :::answer[Worked solution]{tests="maps coordinates solid-angle"}
   The azimuth is atan2(0.8, 0.6) = 53.1°, so the column is 53.1 / 360 + 0.5 = 0.648, which is 1326. The polar angle is
   90°, so the row is 512. The cube face is +Z, the largest coordinate. The cone has 2π (1 - 0.7071) = 1.84 steradians,
   which is 14.6 % of the sphere's 12.57.
   :::

2. **Medium.** Write a program that sums the area of the sphere in 4, 16 and 64 rows, once with the weight sin θ and once
   without. Say what each sum approaches.

   :::answer[Worked solution]{tests="sphere-integral" solution="sketches/basics-math-sphere-rows.cpp"}
   Each row is a ring of length 2π sin θ, and its height is the step of the polar angle.

   ```cpp sketch="basics-math-sphere-rows.cpp"
   // The area of the unit sphere as a sum of rows, with and without the sin(theta) of each row.
   #include <cmath>
   #include <cstdio>
   #include <initializer_list>
   #include <numbers>

   int main()
   {
   	const float pi = std::numbers::pi_v<float>;
   	for (int rows : { 4, 16, 64 })
   	{
   		const float step = pi / static_cast<float>(rows);
   		float flat = 0.0f;
   		float weighted = 0.0f;
   		for (int row = 0; row < rows; row++)
   		{
   			const float polar = (static_cast<float>(row) + 0.5f) * step; // the middle of the row
   			flat += 2.0f * pi * step; // every row counted as if it had the same size
   			weighted += 2.0f * pi * std::sin(polar) * step; // a ring of circumference 2 pi sin(theta)
   		}
   		std::printf("%2d rows: without sin %.3f, with sin %.3f, exact %.3f\n", rows, flat, weighted, 4.0f * pi);
   	}
   	return 0;
   }
   ```

   ```text output-of="basics-math-sphere-rows.cpp"
    4 rows: without sin 19.739, with sin 12.895, exact 12.566
   16 rows: without sin 19.739, with sin 12.587, exact 12.566
   64 rows: without sin 19.739, with sin 12.568, exact 12.566
   ```

   1. **Line 18:** the flat sum counts each row as the same size.
   2. **Line 19:** the weighted sum multiplies by the sine at the row's middle.

   The weighted sum approaches 4π = 12.566. The flat sum stays at 2π² = 19.739, however many rows it uses.
   :::

3. **Medium.** Write `Encode` and `Decode` for the octahedral encoding in C++. Test them on (-0.2, 0.4, -0.8944), and
   say which half of the sphere folds.

   :::answer[Worked solution]{tests="maps" solution="sketches/basics-math-sphere-octa.cpp"}
   The program ports the two shader functions: `Encode` divides by the sum of the sizes and folds the half with z below
   0, and `Decode` reverses it.

   ```cpp sketch="basics-math-sphere-octa.cpp"
   // The octahedral encoding of a unit vector into two numbers, and the way back: the shader's functions in C++.
   #include <cstdio>
   #include <glm/glm.hpp>

   glm::vec2 Encode(glm::vec3 n)
   {
   	n /= glm::abs(n.x) + glm::abs(n.y) + glm::abs(n.z); // onto the octahedron |x| + |y| + |z| = 1
   	return n.z >= 0.0f ? glm::vec2(n) : (1.0f - glm::abs(glm::vec2(n.y, n.x))) * glm::vec2(n.x >= 0.0f ? 1.0f : -1.0f, n.y >= 0.0f ? 1.0f : -1.0f);
   }

   glm::vec3 Decode(glm::vec2 e)
   {
   	glm::vec3 n(e.x, e.y, 1.0f - glm::abs(e.x) - glm::abs(e.y));
   	const float t = glm::max(-n.z, 0.0f); // how far a point of the lower half was folded out
   	n.x += n.x >= 0.0f ? -t : t;
   	n.y += n.y >= 0.0f ? -t : t;
   	return glm::normalize(n);
   }

   int main()
   {
   	const glm::vec2 e = Encode({ -0.2f, 0.4f, -0.8944f });
   	const glm::vec3 n = Decode(e);
   	std::printf("(%.4f, %.4f) -> (%.4f, %.4f, %.4f)\n", e.x, e.y, n.x, n.y, n.z);
   }
   ```

   ```text output-of="basics-math-sphere-octa.cpp"
   (-0.7323, 0.8662) -> (-0.2000, 0.4000, -0.8944)
   ```

   1. **Lines 7–8:** the vector goes onto the octahedron, and the half with z at least 0 keeps x and y.
   2. **Lines 13–16:** z is rebuilt, and x and y move back by `t` where the fold moved them.
   3. **Lines 22–23:** the encoded pair is reversed again in the same program.

   The round trip returns the input to four digits. The half with z below 0 folds: its pair (-0.7323, 0.8662) lies in a
   corner triangle of the square.
   :::

4. **Hard.** Project the light that is 1 above the horizon and 0 below onto the nine harmonics by summing over a grid of
   directions, and find the direction below which the evaluated light is negative.

   :::answer[Worked solution]{tests="spherical-harmonics sphere-integral" solution="sketches/basics-math-sphere-project.cpp"}
   Sum each cell's light times pattern times solid angle, with the weight sin θ in the solid angle.

   ```cpp sketch="basics-math-sphere-project.cpp"
   // Projects a light that is 1 above the horizon and 0 below onto the nine spherical harmonics.
   #include <array>
   #include <cmath>
   #include <cstdio>
   #include <glm/glm.hpp>

   std::array<float, 9> Basis(const glm::vec3& n) { return { 0.282095f, 0.488603f * n.y, 0.488603f * n.z, 0.488603f * n.x, 1.092548f * n.x * n.y, 1.092548f * n.y * n.z, 0.315392f * (3.0f * n.z * n.z - 1.0f), 1.092548f * n.x * n.z, 0.546274f * (n.x * n.x - n.y * n.y) }; }

   int main()
   {
   	const float pi = 3.14159265f;
   	std::array<float, 9> c = {};
   	for (int cell = 0; cell < 128 * 256; cell++) // 128 rows of polar angle, 256 columns of azimuth
   	{
   		const float polar = (static_cast<float>(cell / 256) + 0.5f) / 128.0f * pi, azimuth = (static_cast<float>(cell % 256) + 0.5f) / 256.0f * 2.0f * pi;
   		const glm::vec3 n(std::sin(polar) * std::cos(azimuth), std::cos(polar), std::sin(polar) * std::sin(azimuth));
   		const float weight = (n.y > 0.0f ? 1.0f : 0.0f) * std::sin(polar) * (pi / 128.0f) * (2.0f * pi / 256.0f); // light times solid angle
   		for (int i = 0; i < 9; i++)
   			c[i] += weight * Basis(n)[i];
   	}
   	for (int i = 0; i < 9; i++)
   		std::printf("c%d = %.4f\n", i, c[i]);
   }
   ```

   ```text output-of="basics-math-sphere-project.cpp"
   c0 = 1.7725
   c1 = 1.5350
   c2 = -0.0000
   c3 = 0.0000
   c4 = 0.0000
   c5 = 0.0000
   c6 = -0.0000
   c7 = 0.0000
   c8 = -0.0001
   ```

   1. **Line 7:** the nine patterns of the table, in Strata's order.
   2. **Lines 15–17:** the direction of the cell, and its weight: the light, the sine of the polar angle and the two
      steps.
   3. **Line 19:** each coefficient adds the weight times its pattern.

   Only c0 and c1 survive, so the evaluated light is 0.5 + 0.75 y. It is negative for y below -2 / 3, which is a polar
   angle above 131.8°.
   :::

5. **Hard.** Optional, on your [Coin Run](../make/project-coin-run.md) or Checkpoint 4 of [Ship the finished game](../make/project-coin-run.md#ship-the-finished-game): spread the coins over a dome above the start, evenly by area. Draw the cosine of
   the polar angle uniformly with `Random`, and compare it with a polar angle drawn uniformly. Count how many of 10000
   coins land within 20° of the top of a dome that reaches 80°.

   :::answer[Worked solution]{tests="sphere-integral" solution="sketches/basics-math-sphere-dome.cpp"}
   The area of a cap grows with the height $(1 - \cos\theta)$, so the cosine is the number to draw uniformly. In
   `CoinPlacer`, which already waits for the coin prefab, the loop for one coin reads as below, with `Random` from the
   script library.

   ```cpp pseudocode
   float cosTheta = random.Range(std::cos(maxPolar), 1.0f); // uniform in the cosine
   float sinTheta = std::sqrt(1.0f - cosTheta * cosTheta);
   float azimuth = random.Range(0.0f, 2.0f * pi);
   glm::vec3 direction(sinTheta * std::cos(azimuth), cosTheta, sinTheta * std::sin(azimuth));
   Scene::Instantiate(coinPrefab, start + radius * direction);
   ```

   A separate program counts the coins of both draws.

   ```cpp sketch="basics-math-sphere-dome.cpp"
   // Coins on a dome: a uniform polar angle bunches them at the top; a uniform cosine of it spreads them by area.
   #include <cmath>
   #include <cstdio>
   #include <numbers>
   #include <random>

   int main()
   {
   	const float pi = std::numbers::pi_v<float>;
   	const float maxPolar = 80.0f * pi / 180.0f;
   	const float nearTop = 20.0f * pi / 180.0f;
   	std::mt19937 random(11);
   	std::uniform_real_distribution<float> unit(0.0f, 1.0f);
   	int bunched = 0;
   	int spread = 0;
   	for (int coin = 0; coin < 10000; coin++)
   	{
   		const float uniformAngle = unit(random) * maxPolar;
   		const float cosine = 1.0f - unit(random) * (1.0f - std::cos(maxPolar)); // uniform between cos(max) and 1
   		bunched += uniformAngle < nearTop ? 1 : 0;
   		spread += std::acos(cosine) < nearTop ? 1 : 0;
   	}
   	std::printf("within 20 degrees of the top, of 10000 coins: angle uniform %d, cosine uniform %d\n", bunched, spread);
   	return 0;
   }
   ```

   ```text output-of="basics-math-sphere-dome.cpp"
   within 20 degrees of the top, of 10000 coins: angle uniform 2500, cosine uniform 730
   ```

   1. **Lines 18–19:** the first draw takes the angle uniformly, and the second takes the cosine uniformly between cos 80°
      and 1.
   2. **Lines 20–21:** each count adds the coins with a polar angle below 20°.

   The area share of the cap is (1 - cos 20°) / (1 - cos 80°) = 7.3 %, so 730 coins. The uniform angle gives 20 / 80 =
   25 %, so 2500 coins: the coins bunch at the top.
   :::

## Where the book uses it

- [Units and exposure](../light/units-exposure.md) measures light per solid angle and uses the cosine sum π.
- [The sky](../light/sky.md) uses spherical coordinates for the directions of the sun.
- [Image-based lighting](../indirect/ibl.md) stores a sky in a cube map and averages it with cosine-weighted directions.
- [Reflection probes](../indirect/probes.md) project a cube map onto nine coefficients per colour channel, weighting
  each pixel by its solid angle.
- [Global illumination cascades](../indirect/gi-cascades.md) store the rays of each probe in an octahedral tile.

## Further reading

- Robin Green, "Spherical Harmonic Lighting: The Gritty Details": the projection and evaluation of spherical harmonics
  for games, step by step; intermediate.
- Peter-Pike Sloan, "Stupid Spherical Harmonics (SH) Tricks": the ringing of low bands and how engines reduce it;
  advanced.
- Zina Cigolle and others, "A Survey of Efficient Representations for Independent Unit Vectors": octahedral and other
  encodings of normals, compared; intermediate.
- Matt Pharr, Wenzel Jakob and Greg Humphreys, "Physically Based Rendering", the chapters on sampling and on spherical
  geometry: solid angles, integrals over the sphere and cosine-weighted directions; intermediate.
