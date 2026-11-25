---
id: basics/math-projection
title: "Cameras and projection: perspective, homogeneous coordinates and depth"
description: "How a game turns 3D positions into pixels: the view matrix, perspective, clip space, the divide, depth, reversed Z, and the way back."
kind: primer
size: L
tracks: [B, E]
needs: [basics/math-matrices]
time: 90
learn:
  - id: view-space
    text: compute the position of a world point in view space from the camera's transform
  - id: perspective
    text: compute where a point lands on the image plane from its distance and the field of view
  - id: clip-ndc
    text: trace a point through clip space, the perspective divide and normalized device coordinates to a pixel
  - id: depth
    text: explain why depth is not spread evenly over distance and what reversed Z and the orthographic projection change
  - id: unproject
    text: find the ray through a pixel and the position that a pixel and its depth stand for
status: final
---

::::test-out

1. A camera stands at the origin and looks along -Z. A point lies 4 units ahead and 2 units up. Where does it land on an
   image plane 1 unit in front of the camera?

   :::answer{tests="perspective"}
   Divide by the distance: 2 / 4 = 0.5 up, and 0 / 4 = 0 across. The point lands at (0, 0.5) on the plane.
   :::

2. A camera stands at (0, 0, 5) in the world and has no rotation. Where is the world origin in view space?

   :::answer{tests="view-space"}
   At (0, 0, -5): the view matrix undoes the camera's move, so it subtracts (0, 0, 5). The origin is 5 units ahead,
   along -Z.
   :::

3. A projection leaves a point at the clip coordinates (3, 1.5, 0.5, 6). The window is 800 pixels wide and 400 tall.
   Compute the normalized device coordinates and the pixel.

   :::answer{tests="clip-ndc"}
   Divide every number by w = 6: (0.5, 0.25, 0.083). The pixel column is (0.5 × 0.5 + 0.5) × 800 = 600, and the row is
   (0.5 - 0.25 × 0.5) × 400 = 150, counted from the top.
   :::

4. With reversed Z, which depth does a point on the near plane get, and which one a point on the far plane?

   :::answer{tests="depth"}
   The near plane gets 1 and the far plane gets 0.
   :::

5. The cursor stands at the exact middle of the window. Which direction, in view space, has the ray through it?

   :::answer{tests="unproject"}
   Straight ahead, (0, 0, -1): the middle of the window is (0, 0) in normalized device coordinates, so the ray has no
   sideways or upward part.
   :::

::::

## Why you will need this

A game world has three dimensions and a screen has two. Something must decide which pixel shows which point of the
world. That decision is the camera's, and its mathematics fits on a few pages.

[Coordinates and conventions](../gpu/coordinates.md) states Strata's choices for clip space and depth in full.
[Bounds and culling](../draw/bounds-culling.md) skips what lies outside the camera's pyramid of sight.
[Shadow basics](../light/shadow-basics.md) draws the scene from a light, which needs the orthographic kind of camera.
[Temporal anti-aliasing](../image/taa.md) moves the projection by a fraction of a pixel on each frame.

Each idea goes from a picture and small numbers by hand to the formula and to C++. The programs use `glm`, the
mathematics library that Strata and its scripts use.

:::question[Why do the programs start with lines I have not seen?]
Each program starts with `#include` lines that bring in `glm`, and calls functions such as `glm::inverse(...)`, whose
`glm::` names the library. [Programming 3](../basics/programming-3.md) explains both; here, read them as "use the
library" and "call its function".
:::

## The view matrix puts the camera at the origin

In the editor a camera is an entity with a **Camera** component. Like every entity it has a transform: a position and a
rotation in the world. Drawing needs the opposite view of things: every position measured from the camera.

**View space** is the :term[coordinate system]{id=coordinate-space} whose origin is the camera, with +X to its right, +Y up and -Z straight ahead.
Strata's world uses the same axes, so a camera with no rotation has view space and :term[world space]{id=world-space} aligned.

The **view matrix** is the matrix that turns a world position into a view-space position. It is the inverse of the
camera's :term[world transform]{id=world-transform}. The camera's own matrix carries view space into the world: it places the camera. The way back,
from the world into view space, is the :term[inverse matrix]{id=inverse-matrix}.

:::example[A camera that moved]
The camera stands at (2, 1, 5) and has no rotation. Its world transform adds (2, 1, 5), so the view matrix subtracts
it. The world point (5, 2, 1) becomes (3, 1, -4) in view space: 3 to the right, 1 up and 4 ahead.
:::

Rotation works the same way, with the inverse of a rotation, the turn the other way. Turn the camera a quarter turn to
the left, so that it looks along -X. The world point (-4, 0, 0) is then straight ahead, and the view matrix maps it to
(0, 0, -4). At the limits, a camera at the origin with no rotation has the identity as its view matrix.

Strata builds its view matrix as `glm::inverse` of the camera entity's translation times its rotation, in
`Strata/src/Strata/Renderer/SceneRenderer.cpp`. It leaves the scale out, so scaling the camera entity never stretches
the picture.

Try it: the camera stands at (0, 2, 3) with no rotation. Where is the world point (1, 2, -1) in view space?

:::answer
Subtract the camera's position: (1 - 0, 2 - 2, -1 - 3) = (1, 0, -4). The point is 1 to the right, level with the
camera and 4 ahead.
:::

## Perspective divides by the distance

Look along a straight road: the far telegraph poles look smaller than the near ones, though they are all as tall. A
camera draws the same way. Hold an imaginary window, flat and 1 unit in front of you, and mark where each line of sight
to a point crosses it.

That window is the **image plane**: the flat surface, at distance 1 in front of the camera and at a right angle to its
view direction, on which every point is drawn. In view space it is the plane z = -1.

::figure{id=similar-triangles}

The picture shows the camera and the plane from the side. The point lies at the distance d = 4 and the height y = 1.
The line of sight reaches the plane at a height y' that we want. Two triangles share the corner at the camera: a small
one up to the plane, and a large one up to the point. They have the same angles, so one is a scaled copy of the other,
and its sides keep the same ratio.

The large triangle is 4 times longer, so it is 4 times taller:

$$
y' = \frac{y}{d}, \qquad x' = \frac{x}{d}
$$

$x$ and $y$ are the point's coordinates in view space, in metres. $d$ is its distance in front of the camera, which is
$-z$, because the camera looks along -Z. $x'$ and $y'$ are the place on the image plane. The formulas read "x divided by
d" and "y divided by d". For the point (3, 1, -4), d = 4 gives (0.75, 0.25).

A **projection** is a rule that turns a position in space into a position in a flat picture.

The one found above is the
**perspective projection**: the projection that divides by the distance, so that far things look smaller. Twice the
distance halves the size: the point (3, 1, -8) lands at (0.375, 0.125).

At the limits, a point at d = 0 would need a division by zero, and a point behind the camera has a negative d, which
flips the picture upside down and left to right. So a renderer must discard points on the camera's plane and behind it.
The next sections come back to this.

### The field of view and the aspect ratio set how much the plane holds

The plane is infinite, but a screen shows a rectangle of it. The **field of view** (FOV) is the angle between the top
and the bottom edge of what the camera sees. In Strata it is the vertical angle, written in degrees. A wide angle shows
more and makes everything smaller, like a wide lens; a narrow angle zooms in.

Cut the picture in half, along the view direction, and a right-angled triangle remains. Its angle at the camera is half
the field of view, its side along the view direction has length 1, and its other side is the plane's half-height. The
:term[tangent function]{id=tangent-function} of an angle is the opposite side divided by the adjacent one, so the plane's half-height is tan(FOV / 2).

The width follows from the **aspect ratio**, the width of the picture divided by its height: a window of 1920 by 1080
pixels has 1920 / 1080 = 1.78. At the distance d, the visible half-height and half-width are:

$$
h = d \tan\left(\frac{\theta}{2}\right), \qquad w = a\,h
$$

$\theta$ is the vertical field of view, in :term[radians]{id=radian} when a program computes it. $a$ is the aspect ratio, a plain number.
$h$ and $w$ are the half-height and half-width of what the camera sees at the distance $d$, in metres. The formulas read
"d times the tangent of half the angle" and "a times h".

:::example[What a 60 degree camera sees]
tan(30 degrees) is 0.577. At 10 metres the half-height is 5.77 metres, so the camera sees a strip 11.5 metres tall. With
the aspect ratio 1.78 the half-width is 10.3 metres. A coin 8 metres above the camera's line at that distance is
outside the picture; one 5 metres above is inside.
:::

At the limits, a field of view near 180 degrees makes tan(FOV / 2) grow without bound, and one near 0 shows
almost nothing of the world. Strata keeps the **Camera**'s field of view between 1 and 179 degrees when it builds the projection.

### From a direction to a point on the screen

A direction in view space is a vector (x, y, z) with z below 0. Divide by the distance d = -z to put it on the image
plane. Then divide by the half-width and the half-height of the plane, and both numbers fall between -1 and 1 when the
direction lies inside the picture.

:::example[A direction on a 60 degree camera]
The direction is (1, 0.5, -2), the aspect ratio 1.78. The distance is 2, so the plane position is (0.5, 0.25). The
half-height is 0.577 and the half-width 1.03. The screen position is (0.5 / 1.03, 0.25 / 0.577) = (0.49, 0.43): in the
right half and in the upper half of the picture.
:::

### A cube face is a camera with a 90 degree view

Take an aspect ratio of 1 and a field of view of 90 degrees. Then tan(45 degrees) = 1, and the image plane reaches from
-1 to 1 in both directions. Six such cameras, one looking along each of +X, -X, +Y, -Y, +Z and -Z, cover every direction
without a gap: each is a pyramid, and six pyramids fill the sides of a cube. [Local light shadows](../light/local-shadows.md)
use six views like this to draw the shadows around a point light.

## Homogeneous coordinates let a matrix divide

A matrix can only add multiples of the coordinates, and dividing by d is not that. The next trick moves the division to
the end. The matrix computes d and stores it in a fourth number, and a later step divides by it.

**Homogeneous coordinates** write a position with four numbers, (x, y, z, w), that stand for the position (x / w,
y / w, z / w). A usual position has w = 1, as in the 4×4 matrices of the last page. But (6, 2, -8, 2) is the same
position as (3, 1, -4, 1), because dividing by 2 gives (3, 1, -4).

The **projection matrix** is the 4×4 matrix that turns a view-space position into homogeneous coordinates with the
distance in w. Here is the one for a field of view of 90 degrees, an aspect ratio of 2, a near distance of 1 and a far
distance of 100. It uses Strata's reversed depth of a later section. Its rows, written on paper, are (0.5, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1/99, 100/99) and (0, 0, -1, 0).
Each row gives one result number as a :term[dot product]{id=dot-product} with (x, y, z, 1).

The first row multiplies x by $1 / (a \tan(\theta / 2))$, here 0.5, and the second multiplies y by $1 / \tan(\theta / 2)$,
here 1. The third row builds the depth, which a later section explains. The last row copies -z into w: that is the
distance. Multiplying the point (3, 1, -4, 1) gives (1.5, 1, 0.9697, 4).

The **clip space** is the space of these results: the coordinates after the projection matrix and before the divide. A
:term[graphics card]{id=gpu} tests every point there. A point is inside the picture when x and y lie between -w and w, and z between 0
and w. This test needs no division, and it also removes the points with a w of 0 or less, the ones behind the camera.

The program below does the whole chain for the point of the example, from the world to a pixel. This section needs only
its first lines. It names the camera's world matrix, takes its inverse as the view matrix, and builds the projection
with the near and far distances swapped, which a later section explains.

```cpp sketch="basics-math-projection-pipeline.cpp"
// A world point through the view matrix, the projection, the divide and the pixel grid.
#include <cstdio>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>

int main()
{
	const glm::mat4 cameraWorld = glm::translate(glm::mat4(1.0f), glm::vec3(2.0f, 1.0f, 5.0f));
	const glm::mat4 view = glm::inverse(cameraWorld);
	// Near and far swapped: the near plane stores 1, the far plane 0.
	const glm::mat4 projection = glm::perspectiveRH_ZO(glm::radians(90.0f), 2.0f, 100.0f, 1.0f);

	const glm::vec4 world(5.0f, 2.0f, 1.0f, 1.0f);
	const glm::vec4 inView = view * world;
	const glm::vec4 clip = projection * inView;
	const glm::vec3 ndc = glm::vec3(clip) / clip.w;
	const float pixelX = (ndc.x * 0.5f + 0.5f) * 800.0f;
	const float pixelY = (0.5f - ndc.y * 0.5f) * 400.0f;

	std::printf("view  (%g, %g, %g)\n", inView.x, inView.y, inView.z);
	std::printf("clip  (%g, %g, %.4f, %g)\n", clip.x, clip.y, clip.z, clip.w);
	std::printf("ndc   (%g, %g, %.4f)\n", ndc.x, ndc.y, ndc.z);
	std::printf("pixel (%g, %g)\n", pixelX, pixelY);
	return 0;
}
```

```text output-of="basics-math-projection-pipeline.cpp"
view  (3, 1, -4)
clip  (1.5, 1, 0.9697, 4)
ndc   (0.375, 0.25, 0.2424)
pixel (550, 150)
```

1. **Line 9:** the view matrix is the inverse of the camera's world transform.
2. **Line 11:** the projection matrix of the example, a vertical field of view of 90 degrees and an aspect ratio of 2.
3. **Lines 15–16:** the clip coordinates keep the distance in w, and the divide by w gives the next step's numbers.

## The perspective divide leads to pixels

The **perspective divide** divides the x, y and z of the clip coordinates by w.

The result is a position in
**normalized device coordinates** (NDC): x and y from -1 to 1 with +Y up, and the depth z from 0 to 1. Everything that
the camera sees fits into that box, whatever the field of view and the window are.

For the clip coordinates (1.5, 1, 0.9697, 4) the divide gives (0.375, 0.25, 0.2424). The point is a little right of the
middle and a little above it, and its depth is 0.2424.

```mermaid caption="A point passes through five spaces: the world, the camera's view space, clip space, normalized device coordinates and the pixels of the window." alt="Five boxes joined by arrows from left to right. The world goes to view space through the view matrix, to clip space through the projection matrix, to normalized device coordinates through the divide by w, and to pixels through the viewport."
flowchart LR
    World -->|view matrix| View[View space]
    View -->|projection matrix| Clip[Clip space]
    Clip -->|divide by w| NDC[NDC]
    NDC -->|viewport| Pixels
```

The last step maps NDC to the window. The picture is stored in rows of pixels with row 0 at the top, so the vertical
direction turns around. For a window of W pixels across and H down:

$$
p_x = \left(\frac{x}{2} + \frac{1}{2}\right) W, \qquad p_y = \left(\frac{1}{2} - \frac{y}{2}\right) H
$$

$x$ and $y$ are the NDC coordinates. $p_x$ is the pixel's column, counted from the left, and $p_y$ its row, counted from
the top. $W$ and $H$ are the width and height of the window in pixels. The point (0.375, 0.25) in a window of 800 by 400
lands at the column 550 and the row 150.

::figure{id=ndc-to-pixels}

At the limits, NDC (-1, 1) is the top-left corner, pixel (0, 0), and NDC (1, -1) is the bottom-right corner, pixel
(800, 400). The middle of NDC, (0, 0), is the middle of the window.

:::note[Other graphics libraries differ]
Strata puts +Y up in NDC, depth from 0 to 1 and the origin of the window at the top left. Other graphics interfaces
choose differently: OpenGL, for one, stores depth from -1 to 1. A formula from another book may need a change before it
fits here. [Notation](../reference/notation.md) lists the choices, and [Coordinates and conventions](../gpu/coordinates.md)
shows how Strata's renderer arranges its own.
:::

Try it: in a window of 1280 by 720 pixels, which pixel shows NDC (-0.5, 0.5)?

:::answer
Column (-0.5 × 0.5 + 0.5) × 1280 = 0.25 × 1280 = 320. Row (0.5 - 0.5 × 0.5) × 720 = 0.25 × 720 = 180. The point is in the
upper left quarter of the window.
:::

## The near and far planes bound the view frustum

Not every point is drawn. The sides of the picture cut off what lies to the left, right, above and below. Two more cuts
limit the distance.

The **near plane** is the flat surface at the smallest distance the camera draws.

The **far plane** is the one at the greatest distance. Points closer than the near plane or farther than the far plane are skipped. The near plane keeps the divide
away from 0. The far plane gives the depth numbers a finite range to spread over.

The **view frustum** is the volume the camera sees, bounded by six planes: the left, right, top and bottom sides from
the field of view and the aspect ratio, and the near and far planes. It is a pyramid with its top cut off.

::figure{id=view-frustum}

:::example[The default camera's frustum]
A new **Camera** component has a vertical field of view of 60 degrees, a near plane at 0.1 and a far plane at 1000, all
in metres. At the near plane the picture is 0.115 metres tall; at the far plane it is 1155 metres tall, because tan(30
degrees) × 1000 × 2 = 1155.
:::

The names above are the fields `PerspectiveFOV`, `PerspectiveNear` and `PerspectiveFar` of the **Camera** component.
Strata keeps the near distance above 0.0001 and the far one above the near one when it builds the projection, in
`Strata/src/Strata/Scene/Components.cpp`.

A renderer uses the frustum for speed too: an object that lies fully outside it cannot appear, so it is not drawn.
[Planes](../basics/math-geometry.md) shows how to test a shape against a plane, and
[Bounds and culling](../draw/bounds-culling.md) applies it to whole scenes.

## The depth buffer keeps the nearest surface

Two surfaces can lie on the same line of sight, such as a wall behind a coin. Both land on the same pixel, and only the
nearer one may show.

**Depth** is the number that the projection stores for a point to tell nearer from farther: the z of its NDC, from 0
to 1.

The **depth buffer** is a grid with one depth per pixel of the picture. When a surface is drawn, its depth at each
pixel is compared with the stored one, and the nearer surface wins and replaces the old value. The order in which
surfaces are drawn then does not matter.

Depth is not the distance. The third row of the projection matrix gives z, and w holds the distance d. So after the
divide the depth has the form A + B / d, and its graph is a curve, not a line. Write n for the near distance and f for the far distance. The standard mapping
(the near plane at 0, the far plane at 1) is:

$$
\text{depth} = \frac{f\,(d - n)}{d\,(f - n)}
$$

$d$ is the distance in front of the camera, $n$ the near distance and $f$ the far distance, all in metres. The result is
a plain number. At d = n it is 0, and at d = f it is 1. In between the program below prints it for n = 1 and f = 100.

```cpp sketch="basics-math-projection-depth.cpp"
// The depth that a standard and a reversed projection store for the same distances.
#include <cstdio>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>

float DepthAt(const glm::mat4& projection, float distance)
{
	const glm::vec4 clip = projection * glm::vec4(0.0f, 0.0f, -distance, 1.0f);
	return clip.z / clip.w;
}

int main()
{
	const float fov = glm::radians(60.0f);
	const glm::mat4 standard = glm::perspectiveRH_ZO(fov, 1.0f, 1.0f, 100.0f);
	const glm::mat4 reversed = glm::perspectiveRH_ZO(fov, 1.0f, 100.0f, 1.0f);

	const float distances[] = { 1.0f, 2.0f, 5.0f, 10.0f, 50.0f, 100.0f };
	for (const float distance : distances)
		std::printf("distance %5.1f: standard %.4f, reversed %.4f\n", distance, DepthAt(standard, distance),
			DepthAt(reversed, distance));
	return 0;
}
```

```text output-of="basics-math-projection-depth.cpp"
distance   1.0: standard 0.0000, reversed 1.0000
distance   2.0: standard 0.5051, reversed 0.4949
distance   5.0: standard 0.8081, reversed 0.1919
distance  10.0: standard 0.9091, reversed 0.0909
distance  50.0: standard 0.9899, reversed 0.0101
distance 100.0: standard 1.0000, reversed 0.0000
```

1. **Line 15:** the standard projection with the near distance 1 and the far distance 100.
2. **Line 16:** the same call with the two distances swapped, which a later section explains.
3. **Lines 8–9:** a point at each distance on the view direction, divided by its w.

::figure{id=depth-curve}

Read the standard column. Half of the whole depth range is used up at a distance of 2, only one unit past the near
plane, and 99 % of it is gone at 50. The 50 metres between 50 and 100 share the last 1 %.

The costs are real. Surfaces far away get few different depth values, so two surfaces that are close together can store
the same number and flicker, as the renderer cannot tell which is nearer. The remedy is to move the near plane out as
far as the game allows: 0.1 metre in place of 0.001 gives much more of the range to the far places.

## Reversed Z stores the near plane at 1

**Reversed Z** swaps the roles: the near plane stores depth 1 and the far plane stores depth 0. The mapping is the
standard one with the near and far distances exchanged. Strata's `Math::PerspectiveReverseZ` is exactly that: a call of
`glm::perspectiveRH_ZO` with the far distance where the near one goes, in `Strata/src/Strata/Math/Math.cpp`.

For every distance the reversed depth is 1 minus the standard one. With n = 1 and f = 100 the reversed column of the
last program reads 1, 0.49, 0.19, 0.09, 0.01 and 0. A surface that is nearer has the larger number, so the depth buffer
keeps the larger value of two.

The reason is the floating-point numbers of [Numbers](../basics/numbers.md), whose spacing grows with their size. Near
0 they are very dense and near 1 they are far apart. The curve squeezes the far places toward one end of the range.
The standard mapping squeezes them toward 1, where the numbers are sparse. Reversed Z squeezes them toward 0, where the
numbers are dense, and the two effects cancel.

:::caution[glm in a script gives the other order]
Scripts build with `GLM_FORCE_DEPTH_ZERO_TO_ONE`, so `glm::perspective` there puts depth 0 at the near plane and 1 at
the far plane, which is not what the renderer uses. A script that needs Strata's order swaps the near and far arguments
itself.
:::

This page stays with the mathematics. [Coordinates and conventions](../gpu/coordinates.md) shows the precision of the
depth in numbers and tells what Strata does with a far plane at infinity, and [Math](../core/math.md) walks through the
engine's projection functions.

## The orthographic projection keeps sizes

The **orthographic projection** is the projection that does not divide by the distance: it keeps w at 1 and only
scales x and y, so an object has the same size at every distance. The volume it sees is a box and not a pyramid.

The box's half-height comes from one number, the vertical size of the picture. A **Camera** with an `OrthographicSize`
of 10 and the aspect ratio 2 sees 10 metres up and down in total and 20 across, so the half-height is 5 and the
half-width 10. The point (3, 1, -4) lands at the NDC (3 / 10, 1 / 5) = (0.3, 0.2), and so does (3, 1, -40).

Its depth is a straight line of the distance, with no bend. Use it where size must not depend on distance: the
shadow of the sun, whose rays are parallel, a side view, or a flat 2D game. At the limits, a box of zero size would
divide by zero, so Strata keeps the size above 0.0001.

:::note[Where the numbers live in Strata]
`Projection` of the **Camera** chooses perspective or orthographic. `PerspectiveFOV` is the vertical field of view in
degrees, 60 by default, with `PerspectiveNear` 0.1 and `PerspectiveFar` 1000. `OrthographicSize` is the vertical extent
in metres, 10 by default. A script reads one with `GetProperty<float>("Camera", "PerspectiveFOV")`, and the value comes
in degrees.
:::

## A pixel leads back to a position and a ray

A player clicks at a pixel. Which thing in the world did the click hit? The question runs the chain backward: from a
pixel to a line in the world.

Start with the NDC, from the pixel: x = 2 p_x / W - 1 and y = 1 - 2 p_y / H, the formulas of the last section solved
for x and y. If the depth is also known, multiply the NDC and a 1 by the inverse of the projection matrix. The result
has the distance in w, so the divide comes last. Multiplying that by the inverse of the view matrix then gives the world position.

The program below takes the pixel (550, 150) with the depth 0.2424 from the first example, and finds the view-space
position again.

```cpp sketch="basics-math-projection-unproject.cpp"
// From a pixel and its depth back to a position in view space, and the direction of the ray through the pixel.
#include <cstdio>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>

int main()
{
	const glm::mat4 projection = glm::perspectiveRH_ZO(glm::radians(90.0f), 2.0f, 100.0f, 1.0f);
	const glm::mat4 inverseProjection = glm::inverse(projection);

	const float pixelX = 550.0f, pixelY = 150.0f, depth = 0.2424f;
	const glm::vec4 ndc(pixelX / 800.0f * 2.0f - 1.0f, 1.0f - pixelY / 400.0f * 2.0f, depth, 1.0f);
	const glm::vec4 back = inverseProjection * ndc;
	const glm::vec3 position = glm::vec3(back) / back.w;
	std::printf("position (%.2f, %.2f, %.2f)\n", position.x, position.y, position.z);

	// The ray needs no depth: x and y at the image plane, one unit in front of the camera.
	const float halfHeight = glm::tan(glm::radians(90.0f) * 0.5f);
	const glm::vec3 direction = glm::normalize(glm::vec3(ndc.x * halfHeight * 2.0f, ndc.y * halfHeight, -1.0f));
	std::printf("direction (%.3f, %.3f, %.3f)\n", direction.x, direction.y, direction.z);
	return 0;
}
```

```text output-of="basics-math-projection-unproject.cpp"
position (3.00, 1.00, -4.00)
direction (0.588, 0.196, -0.784)
```

1. **Line 9:** the inverse of the projection matrix undoes the projection.
2. **Lines 12–14:** the NDC and the depth go in, and the divide by w comes after the multiplication.
3. **Lines 17–19:** the ray needs no depth, only the place on the image plane one unit in front of the camera.

The position is (3, 1, -4) again, and that is the point the first example started with. A pixel alone has no depth, so
it names a whole line of points, all of which draw to it.

That line is the **ray** through the pixel. It starts at the
camera. With x and y in NDC, its direction in view space is (x × tan(FOV / 2) × a, y × tan(FOV / 2), -1). The
Physics Playground sample builds that ray to aim a shot at the mouse. Here is the center of the function:

```cpp src="Samples/PhysicsPlayground/Scripts/Playground.cpp#L193-L205" from="const glm::uvec2 window = Game::GetWindowSize();" to="outDirection = glm::normalize(forward + right * x + up * y);" symbol="Playground::GetPointerRay"
const glm::uvec2 window = Game::GetWindowSize();
const glm::vec2 mouse = Input::GetMousePosition();
if (window.x == 0 || window.y == 0 || mouse.x < 0.0f || mouse.y < 0.0f)
{
	outDirection = forward;
	return true;
}
// The cursor's place on the camera's image plane (vertical field of view in degrees).
const float fov = glm::radians(camera.GetProperty<float>("Camera", "PerspectiveFOV").value_or(45.0f));
const float aspect = static_cast<float>(window.x) / static_cast<float>(window.y);
const float x = (2.0f * mouse.x / static_cast<float>(window.x) - 1.0f) * std::tan(fov * 0.5f) * aspect;
const float y = (1.0f - 2.0f * mouse.y / static_cast<float>(window.y)) * std::tan(fov * 0.5f);
outDirection = glm::normalize(forward + right * x + up * y);
```

1. **Line 193:** the size of the window in pixels, which is 0 while it is unknown.
2. **Lines 195–199:** with no size or no cursor position, the ray points straight ahead.
3. **Line 201:** the field of view comes from the camera's property in degrees and turns into radians.
4. **Line 202:** the aspect ratio divides in floats; whole numbers would give 1 for 1920 by 1080.
5. **Lines 203–205:** NDC times tan(FOV / 2), times the aspect ratio for x, goes along the camera's right and up axes,
   and the sum with the forward axis is the world direction.

At the limits, the middle of the window gives x = y = 0, so the ray is the camera's forward axis. A cursor at the top
edge gives y = 1, and the ray rises by tan(FOV / 2) for each unit forward, the slope of the frustum's top side.

## Common mistakes

- **A field of view in degrees where radians go.** Symptom: a picture that is far too wide or flipped, because `glm`
  takes radians and 60 is read as 60 radians. Fix: call `glm::radians` first. The **Camera** field itself is in degrees.
- **The aspect ratio inverted.** Symptom: the picture is stretched, tall things look wide. Fix: width divided by height,
  1.78 for a wide screen. In a script, divide in floats: `size.x / size.y` with whole numbers gives 1 for 1920 by 1080,
  and the size is 0 while it is unknown.
- **A near plane at 0.** Symptom: the depth is the same everywhere, and the picture flickers or vanishes. With n = 0 the
  formula has no range to spread. Fix: choose a small positive near distance. Strata keeps it above 0.0001.
- **Depth read as a distance.** Symptom: a fog or an effect that works only near the camera. Depth is the curve
  A + B / d, not d. Fix: turn it back into a distance with the projection's numbers before you use it as a length.
- **A depth range of -1 to 1 expected.** Symptom: code from another source, written for OpenGL, gives wrong shadows or
  hides everything. Strata's depth runs from 0 to 1 and is reversed. Fix: check the convention of every formula you copy.
- **Clip coordinates used as NDC.** Symptom: points that lie far off the screen when they should be in it. The divide
  by w is missing. Fix: divide x, y and z by w before the pixel step.
- **The y axis not flipped.** Symptom: the picture is upside down. NDC has +Y up and pixel rows count downward. Fix: use
  0.5 - y × 0.5 for the row.

## Summary

- The view matrix is the inverse of the camera's world transform: it moves the world so that the camera sits at the
  origin and looks along -Z.
- Perspective divides x and y by the distance, so far things look smaller; the image plane's half-height at distance 1 is
  tan(FOV / 2), and the width follows from the aspect ratio.
- The projection matrix writes the distance into w to give clip space. The perspective divide gives NDC, with x and y
  from -1 to 1, +Y up, and a depth from 0 to 1. A flip of y gives the pixel, with row 0 at the top.
- Depth is not spread evenly: the curve spends most of its range near the camera. Reversed Z stores the near plane at 1
  and the far plane at 0, which suits floats. The orthographic projection keeps sizes and keeps depth linear.
- In the other direction, the inverse projection and the divide turn a pixel with its depth into a position, and a pixel alone gives
  a ray from the camera.

## Check yourself

1. A script calls `glm::perspective(60.0f, aspect, near, far)` with the field of view straight from the **Camera**. What
   is wrong? (a) nothing, `glm` takes degrees (b) `glm` takes radians, so 60 means 60 radians (c) the aspect ratio must
   come last (d) `glm` has no perspective function

   :::answer{tests="perspective"}
   (b). `glm` works in radians, so the call should read `glm::radians(60.0f)`. (a) mistakes the function for the
   **Camera** field, (c) moves the arguments around, and (d) is not true.
   :::

2. The camera has the near distance 1 and the far distance 100, and Strata's reversed Z. Which depth does a surface at a
   distance of 10 get: about 0.09, 0.5 or 0.9?

   :::answer{tests="depth"}
   About 0.09. The standard depth at 10 is 0.909, and the reversed one is 1 minus that. The far part of the scene is
   squeezed toward 0.
   :::

3. A point has the clip coordinates (2, 1, 0.5, 4). Is it inside the picture, and what are its NDC?

   :::answer{tests="clip-ndc"}
   Inside: x and y lie between -4 and 4, and z between 0 and 4. The NDC are (2 / 4, 1 / 4, 0.5 / 4) = (0.5, 0.25, 0.125).
   :::

4. The camera is at (0, 0, 8) and looks along -Z. The point (0, 0, 2) is in the world. What is its view-space position,
   and what is the distance d?

   :::answer{tests="view-space"}
   The view matrix subtracts (0, 0, 8), so the position is (0, 0, -6). The camera looks along -Z, so the point is 6
   units ahead and d = 6.
   :::

5. A window is 800 by 400 pixels and the field of view is 90 degrees. Which direction, in view space, has the ray
   through the pixel (600, 100)?

   :::answer{tests="unproject"}
   The NDC are x = 2 × 600 / 800 - 1 = 0.5 and y = 1 - 2 × 100 / 400 = 0.5. With tan(45 degrees) = 1 and the aspect
   ratio 2, the direction is (0.5 × 2, 0.5, -1) = (1, 0.5, -1), before it is made a :term[unit vector]{id=unit-vector}.
   :::

## Practice

1. **Basic.** The camera has a field of view of 90 degrees and an aspect ratio of 2. Compute the half-height and the
   half-width that it sees at a distance of 10 metres, and say whether a point 6 metres above the camera's line at that
   distance is inside the picture.

   :::answer[Worked solution]{tests="perspective"}
   tan(45 degrees) = 1, so the half-height is 10 × 1 = 10 metres and the half-width is 2 × 10 = 20 metres. A point 6
   metres up is inside, because 6 is less than 10.
   :::

2. **Medium.** For the projection of this page (90 degrees, aspect ratio 2, near 1, far 100, with reversed Z), take the
   view-space point (-2, -0.5, -2). Compute its clip coordinates, its NDC and its pixel in a window of 800 by 400.

   :::answer[Worked solution]{tests="clip-ndc"}
   The distance is 2. The clip coordinates are (0.5 × -2, -0.5, (-2 + 100) / 99, 2) = (-1, -0.5, 0.9899, 2). The divide
   gives the NDC (-0.5, -0.25, 0.4949). The column is (-0.5 × 0.5 + 0.5) × 800 = 200 and the row is
   (0.5 + 0.25 × 0.5) × 400 = 250.
   :::

3. **Medium.** With reversed Z, a near distance of 0.1 and a far distance of 1000, compute the depth at the distances 1
   and 10. How much of the 0 to 1 range does a surface 10 metres away get?

   :::answer[Worked solution]{tests="depth"}
   Reversed depth is 1 minus the standard depth, which equals n (f - d) / (d (f - n)). At d = 1 it is 0.1 × 999 / 999.9 = 0.0999. At d = 10 it is 0.1 × 990 /
   (10 × 999.9) = 0.0099. A surface 10 metres away stores about 1 % of the range, so almost all the numbers go to the
   first metre; floats are dense near 0, which is why this still works.
   :::

4. **Medium.** In a window of 800 by 400 pixels, with a field of view of 60 degrees, find the view-space ray through the
   pixel (200, 300). Give its direction before :term[normalizing]{id=normalization}.

   :::answer[Worked solution]{tests="unproject"}
   The NDC are x = 2 × 200 / 800 - 1 = -0.5 and y = 1 - 2 × 300 / 400 = -0.5. With tan(30 degrees) = 0.577 and the aspect
   ratio 2, the direction is (-0.5 × 0.577 × 2, -0.5 × 0.577, -1) = (-0.577, -0.289, -1): left of the middle and below it.
   :::

5. **Hard.** An orthographic camera has an `OrthographicSize` of 20 and the aspect ratio 16 / 9. Compute the NDC of the
   view-space point (6, -4, -50) and say what happens to it when the distance grows to 500.

   :::answer[Worked solution]{tests="depth"}
   The half-height is 10 and the half-width is 10 × 16 / 9 = 17.78. The NDC are (6 / 17.78, -4 / 10) = (0.34, -0.4). At
   a distance of 500 they stay the same: an orthographic projection does not divide by the distance, so only the depth
   changes, in a straight line.
   :::

6. **Hard.** The optional Coin Run item: count the coins the camera sees. A camera at (0, 1, 10) looks along -Z with a
   field of view of 60 degrees in a window of 1600 by 900 pixels. Take each coin's offset from the camera, measure it
   along the camera's right, up and forward axes with three :term[dot products]{id=dot-product}, and test it against tan(FOV / 2) and the
   aspect ratio. Write a program for the six coins (0, 1, 5), (6, 1, 5), (2, 2, 0), (0, 1, 15), (-3, 4, 2) and (0, 9, 6),
   and print the count.

   :::answer[Worked solution]{tests="view-space perspective" solution="sketches/basics-math-projection-coins.cpp"}
   The forward dot product gives the depth of a coin in view space; it must be above 0. At that depth the picture's
   half-height is depth × tan(FOV / 2), and its half-width is that times the aspect ratio, so the up and right dot
   products must stay inside them.

   ```cpp sketch="basics-math-projection-coins.cpp"
   // Counts the coins that a camera sees, from each coin's offset along the camera's axes.
   #include <cmath>
   #include <cstdio>
   #include <vector>
   #include <glm/glm.hpp>

   bool IsSeen(const glm::vec3& offset, const glm::vec3& right, const glm::vec3& up, const glm::vec3& forward, float tanHalf, float aspect)
   {
   	const float depth = glm::dot(offset, forward);
   	const float halfHeight = depth * tanHalf;
   	return depth > 0.0f && std::abs(glm::dot(offset, up)) <= halfHeight && std::abs(glm::dot(offset, right)) <= halfHeight * aspect;
   }

   int main()
   {
   	const glm::vec3 camera(0.0f, 1.0f, 10.0f);
   	const float aspect = 1600.0f / 900.0f; // In floats: 1600 / 900 with integers gives 1.
   	const float tanHalf = std::tan(glm::radians(60.0f) * 0.5f);
   	const std::vector<glm::vec3> coins = { { 0, 1, 5 }, { 6, 1, 5 }, { 2, 2, 0 }, { 0, 1, 15 }, { -3, 4, 2 }, { 0, 9, 6 } };
   	int seen = 0;
   	for (const glm::vec3& coin : coins)
   		if (IsSeen(coin - camera, { 1, 0, 0 }, { 0, 1, 0 }, { 0, 0, -1 }, tanHalf, aspect))
   			seen++;
   	std::printf("%d of %zu coins are in view\n", seen, coins.size());
   }
   ```

   ```text output-of="basics-math-projection-coins.cpp"
   3 of 6 coins are in view
   ```

   1. **Line 7:** the three axes and the two numbers of the camera go in, with the coin's offset.
   2. **Lines 9–11:** the forward part is the depth, and the up and right parts are tested against the half-height and
      the half-width at that depth.
   3. **Line 17:** the aspect ratio is made in floats, because whole numbers would give 1.

   Three coins are in view. (6, 1, 5) is too far to the side, (0, 1, 15) is behind the camera and (0, 9, 6) is too high.
   In a Coin Run script, the axes come from `GetForward`, `GetRight` and `GetUp` of the camera's transform. The window size
   comes from `Game::GetWindowSize` and the field of view from the **Camera** property, as `GetPointerRay` reads them.
   Treat a window size of 0 as unknown and skip the count.
   :::

## Where the book uses it

- [Coordinates and conventions](../gpu/coordinates.md) states Strata's clip space, its flip of the viewport and the
  depth precision of reversed Z.
- [Bounds and culling](../draw/bounds-culling.md) extracts the frustum's six planes from the matrices and tests objects
  against them.
- [Shadow basics](../light/shadow-basics.md) draws the scene from the light with the orthographic projection.
- [Temporal anti-aliasing](../image/taa.md) shifts the projection by a fraction of a pixel and projects again with the last
  frame's matrices.

## Further reading

- 3Blue1Brown, "Essence of linear algebra": videos that draw matrices and the inverse as moving pictures; beginner.
- Eric Lengyel, "Foundations of Game Engine Development, Volume 2: Rendering": the chapter on projections, with
  homogeneous coordinates and depth; intermediate.
- Khronos Group, "OpenGL Specification", the chapter on coordinate transformations: how another interface maps depth
  from -1 to 1; advanced.
