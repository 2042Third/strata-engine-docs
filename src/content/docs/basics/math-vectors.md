---
id: basics/math-vectors
title: "Vectors: length, direction, dot and cross products"
description: "Positions and steps as lists of numbers: add and scale them, measure lengths and angles, and use the dot and cross products."
kind: primer
size: L
tracks: [B, E]
needs: [basics/programming-2]
time: 90
learn:
  - id: vector-steps
    text: compute the step between two positions and add, subtract and scale vectors one number at a time
  - id: length-direction
    text: compute a vector's length, the distance between two points and a unit vector, and explain why a zero vector has no direction
  - id: angles
    text: compute the cosine, the sine and the atan2 angle of a direction, with angles in radians
  - id: dot-product
    text: compute a dot product and use it to tell in front from behind, find an angle, project and reflect
  - id: cross-product
    text: compute a cross product and predict which way it points with the right-hand rule
status: final
---

::::test-out

1. The ball stands at (2, 1, 0) and a coin at (5, 5, 0). Compute the step from the ball to the coin and its length.

   :::answer{tests="vector-steps length-direction"}
   The step is the coin minus the ball, one number at a time: (3, 4, 0). Its length is the square root of 9 + 16 + 0 =
   25, which is 5.
   :::

2. Write one line of C++ that gives `std::sin` of an angle of 30 degrees.

   :::answer{tests="angles"}
   `std::sin(glm::radians(30.0f))`, which is 0.5. `std::sin(30.0f)` reads 30 in another unit of angle and gives about
   -0.988.
   :::

3. By hand, compute `glm::dot` of (1, 2, 3) and (4, -5, 6). Is the angle between the two arrows less or more than 90
   degrees?

   :::answer{tests="dot-product"}
   1 × 4 + 2 × (-5) + 3 × 6 = 4 - 10 + 18 = 12. The result is positive, so the angle is less than 90 degrees.
   :::

4. By hand, compute `glm::cross` of (1, 0, 0) and (0, 0, 1).

   :::answer{tests="cross-product"}
   (0 × 1 - 0 × 0, 0 × 0 - 1 × 1, 1 × 0 - 0 × 0) = (0, -1, 0).
   :::

5. A coin and the ball stand at the same point. What does `glm::normalize(ball - coin)` give, and what should the code
   do instead?

   :::answer{tests="length-direction"}
   The step is (0, 0, 0), which has no direction, and `glm::normalize` returns values that are not numbers. The code
   measures the length first and moves the coin only when the length is greater than a small limit.
   :::

::::

## Why you will need this

A game keeps asking where things are. Is the coin close enough to collect? Is the player in front of the guard or
behind? How does a ball bounce off a wall? Each answer is a small calculation on a few numbers, and the pages listed
at the end use them.

Each idea goes from a picture and numbers by hand to the formula and to C++ with `glm`, the library of mathematics that
Strata and its scripts use.

:::question[What are the programs' first lines, and how do I run them?]
The `#include` lines bring in `glm`, and `glm::` in `glm::length(...)` names the library: [Programming
3](../basics/programming-3.md) explains both. You need not run a program: its output stands below it. To run one, put
the lines inside `main` into `OnCreate` of the `Playground` script of [Programming 1](../basics/programming-1.md), with
`Log::Info` in place of `std::printf`.
:::

## A position is a list of numbers measured from an origin

You know the flat graph from school: two lines that cross at a right angle. Each line is an **axis**: a line with a
direction, along which you measure distance. The left-to-right axis is called x, the bottom-to-top one y.

The point where the axes cross is the **origin**: the place every measurement starts from, where both numbers are zero.
To say where a point is, you count how far it lies along x and then along y. Point A in the figure is 1 along x and 2
up y, written (1, 2). Point C lies 3 to the left of the origin, so its first number is negative: (-3, 1).

::figure{id=points-on-graph}

Each of those numbers is a **coordinate**: the distance of a point from the origin along one axis. The order matters:
(1, 2) and (2, 1) are two different points, because the first number is always x.

A game world needs a third axis, z, at a right angle to both x and y, like the edge where two walls of a room meet. A
point in 3D is three coordinates, (x, y, z): a coin at (4, 0, 6) lies 4 along x, 0 along y and 6 along z. Which way
each axis points in Strata is the subject of [Matrices](../basics/math-matrices.md). Here any choice works, because
every calculation treats the three axes alike. One unit of a Strata scene is one metre.

:::example[A position in the Inspector]
Select an entity in the editor, and its **Transform** shows three numbers beside **Translation**: its x, y and z
coordinates. (0, 1, -3) puts the entity 1 unit up y and 3 units along z the negative way.
:::

Try it: a point lies 2 to the left of the origin, 5 up and 1 along z. Write its coordinates.

:::answer
(-2, 5, 1). Left of the origin is the negative direction of x.
:::

## A vector is a step from one position to another

The ball stands at A = (1, 0, 2) and a coin at B = (4, 0, 6). To walk from the ball to the coin, you move 3 along x, 0
along y and 4 along z. That step is itself three numbers, (3, 0, 4), and you found it by taking A's coordinates from
B's, one at a time: (4 - 1, 0 - 0, 6 - 2).

A **vector** is a list of numbers that describes a step: how far to move along each axis. You draw it as an arrow. The
arrow has a direction and a length, but no fixed place: the step (3, 0, 4) is the same step wherever it starts.

$$
b - a = (b_x - a_x,\; b_y - a_y,\; b_z - a_z)
$$

$a$ is the start position and $b$ the end position. $a_x$, $a_y$ and $a_z$ are the three coordinates of $a$, read "a x",
"a y" and "a z"; $b_x$, $b_y$ and $b_z$ are those of $b$. The formula is read "b minus a". The order matters: a - b =
(-3, 0, -4) is the step back from the coin to the ball.

### Adding, subtracting and scaling

Steps add up. Walk the step (3, 1), then walk (1, 2) from where you stopped, and you stand at (4, 3) from where you
began. Adding two vectors adds their matching coordinates. In the picture, the second arrow's tail sits on the first
arrow's tip, and the sum goes from the first tail to the last tip.

::figure{id=adding-arrows}

Subtracting goes the other way: a - b is the step that, added to b, gives a. Scaling multiplies every coordinate by one
plain number. Half the step (3, 0, 4) is (1.5, 0, 2), the same direction and half as long. A negative number turns the
arrow around: -1 × (3, 0, 4) = (-3, 0, -4). Scaling by 0 gives (0, 0, 0), the **zero vector**: the step that goes
nowhere.

### Positions and directions are the same three numbers

A position and a step are both three numbers, so code stores both in one type. A position plus a step is a new
position, and a position minus a position is a step. A position plus a position means nothing: the result depends on
where the origin happens to be.

A velocity is a direction with a length per second. A ball with the velocity (2, 0, 0) moves 2 units along x each
second, so in a frame of 0.5 seconds it moves 0.5 × (2, 0, 0) = (1, 0, 0). [Change over
time](../basics/math-change.md) builds movement on that idea.

:::example[The step from the ball to a coin, computed by glm]
`glm::vec3` is the type of a 3D vector: three `float` values called `x`, `y` and `z`. The program takes the step from
the ball to the coin, adds it back, halves it, and adds a `glm::vec2`, a 2D vector, to itself. Watch the `-`, `+` and
`*` signs: `glm` does each one coordinate at a time.

```cpp sketch="basics-math-vectors-steps.cpp"
// Steps between positions: subtract, add and scale, one coordinate at a time.
#include <cstdio>
#include <glm/glm.hpp>

int main()
{
	const glm::vec3 start(1.0f, 0.0f, 2.0f); // where the ball is
	const glm::vec3 coin(4.0f, 0.0f, 6.0f);  // where a coin is
	const glm::vec3 step = coin - start;     // the arrow from the ball to the coin
	const glm::vec3 back = start + step;     // the step added to the start lands on the coin
	const glm::vec3 half = step * 0.5f;      // half the step: the same direction, half as long
	std::printf("step (%g, %g, %g)\n", step.x, step.y, step.z);
	std::printf("start + step (%g, %g, %g)\n", back.x, back.y, back.z);
	std::printf("half (%g, %g, %g)\n", half.x, half.y, half.z);

	const glm::vec2 mouse(12.0f, -5.0f); // a mouse movement, in pixels
	const glm::vec2 twice = mouse + mouse;
	std::printf("mouse + mouse (%g, %g)\n", twice.x, twice.y);
	return 0;
}
```

```text output-of="basics-math-vectors-steps.cpp"
step (3, 0, 4)
start + step (4, 0, 6)
half (1.5, 0, 2)
mouse + mouse (24, -10)
```

1. **Lines 7–9:** a position and a step use the same type; only the names say which is which.
2. **Line 10:** the ball plus the step lands on the coin, so subtracting and adding undo each other.
3. **Lines 16–17:** a mouse movement is a 2D vector of pixels, which a script reads with `Input::GetMouseDelta()`.

:::

In the playground, `Log::Info` prints a vector in brackets: the line below writes (3, 0, 4) to the **Console**.

```cpp pseudocode
Log::Info("step ", glm::vec3(4.0f, 0.0f, 6.0f) - glm::vec3(1.0f, 0.0f, 2.0f));
```

A script reads the **Translation** of its entity with `GetTransform().GetTranslation()` and moves the entity with
`GetTransform().SetTranslation(...)`, both with a `glm::vec3`.

Try it: the ball is at (2, 0, -1). Compute the step to a coin at (-1, 0, 3), then twice that step.

:::answer
The step is (-1 - 2, 0 - 0, 3 - (-1)) = (-3, 0, 4). Twice the step is (-6, 0, 8).
:::

## The length of a vector comes from the Pythagorean theorem

How far is the coin from the ball, when the step is (3, 0, 4)? Not 3 + 4 = 7: that is the walk along x and then along
z, around the corner. The straight line is shorter.

Draw the step flat, ignoring y: 3 along one axis, 4 along the other. The two moves and the straight line form a
triangle with a right angle in its corner. The **Pythagorean theorem** says that in such a triangle, the square of the
long side equals the squares of the two short sides added together.

::figure{id=three-four-five}

:::example[The 3-4-5 triangle by hand]
The short sides are 3 and 4, whose squares are 9 and 16. They add up to 25. The long side is the number whose square is
25, the square root of 25: 5. The coin is 5 units from the ball.
:::

The theorem works in 3D too: add the squares of all three coordinates and take the square root. The **vector length**
is the distance from an arrow's tail to its tip, computed that way.

$$
\|v\| = \sqrt{v_x^2 + v_y^2 + v_z^2}
$$

$v$ is any vector, and $v_x$, $v_y$ and $v_z$ are its coordinates. $\|v\|$, read "the length of v", is its length in
the units of its coordinates, and $\sqrt{\;}$ is read "the square root of". For the step (1, 2, 2), the length is the
square root of 1 + 4 + 4 = 9, which is 3.

The distance between two points is the length of the step between them. In `glm`, `glm::length(v)` gives a vector's
length and `glm::distance(a, b)` the distance between two positions. A check at the limits: a length is never
negative, because squares are never negative, and it is zero only for the zero vector.

Try it: compute the distance between (1, 1, 1) and (3, 4, 7).

:::answer
The step is (2, 3, 6). Its length is the square root of 4 + 9 + 36 = 49, which is 7.
:::

## A unit vector keeps only the direction

A coin should fly toward the ball at 4 units per second, wherever the ball is. The step from the coin to the ball points
the right way, but its length is the distance, which changes every frame. You want the same direction with the length
1.

A **unit vector** is a vector whose length is 1.

**Normalization** is turning a vector into the unit vector of the same direction, by dividing every coordinate by the
vector's length.

:::example[The unit vector of (3, 0, 4)]
The length is 5. Divide each coordinate by 5: (0.6, 0, 0.8). Check: 0.36 + 0 + 0.64 = 1, whose square root is 1.
:::

To move at a speed, scale the unit vector by the speed and by the frame's time. At 4 units per second and a frame of
0.125 seconds, the coin moves (0.6, 0, 0.8) × 4 × 0.125 = (0.3, 0, 0.4), a step 0.5 units long.

The program below computes the lengths of the earlier examples, then a unit vector with `glm::normalize`. Its last line
asks what `glm::normalize` makes of the zero vector.

```cpp sketch="basics-math-vectors-length.cpp"
// Lengths, distances and unit vectors, computed by glm.
#include <cmath>
#include <cstdio>
#include <glm/glm.hpp>

int main()
{
	const glm::vec2 flat(3.0f, 4.0f);
	std::printf("length of (3, 4): %g\n", glm::length(flat));

	const glm::vec3 a(1.0f, 0.0f, 2.0f);
	const glm::vec3 b(4.0f, 0.0f, 6.0f);
	std::printf("distance from a to b: %g\n", glm::distance(a, b));
	std::printf("length of (1, 2, 2): %g\n", glm::length(glm::vec3(1.0f, 2.0f, 2.0f)));

	const glm::vec3 direction = glm::normalize(b - a);
	std::printf("unit vector (%g, %g, %g), length %g\n", direction.x, direction.y, direction.z, glm::length(direction));

	const glm::vec3 nothing = glm::normalize(glm::vec3(0.0f));
	std::printf("normalize of zero is a number: %s\n", std::isnan(nothing.x) ? "no" : "yes");
	return 0;
}
```

```text output-of="basics-math-vectors-length.cpp"
length of (3, 4): 5
distance from a to b: 5
length of (1, 2, 2): 3
unit vector (0.6, 0, 0.8), length 1
normalize of zero is a number: no
```

1. **Line 13:** `glm::distance(a, b)` gives the same 5 as the length of the step from a to b.
2. **Line 16:** `glm::normalize` divides by the length, so the result has the length 1.
3. **Lines 19–20:** the zero vector has the length 0, and dividing by 0 gives values that are not numbers, which
   `std::isnan` detects.

### Never normalize the zero vector

The zero vector has no direction: it is the step that goes nowhere. Dividing its 0 by its length of 0 gives a special
value called "not a number", printed `nan`. Any arithmetic with `nan` gives `nan` again, so one bad step spreads into
everything computed from it.

A coin that has reached the ball, or an enemy on its target, meets the zero vector. The fix is to measure
the length first and to divide only when it is greater than a small limit, such as 0.001.

## Angles are measured in degrees or radians

A direction on a flat graph can also be described by an angle: how far you turn from the x axis. You know degrees: a
full turn is 360 degrees, a right angle 90.

C++ functions use another unit. A **radian** is the angle you turn while you walk one radius along the edge of a
circle. On a circle of radius 1, the distance you walk along the edge from the x axis is the angle in that unit.

**Pi**, written π, is the length of a circle's edge divided by its width across, about 3.14159. The edge of a circle
of radius 1 is therefore 2π long, and a full turn is 2π radians, about 6.283.

$$
\text{radians} = \text{degrees} \times \frac{\pi}{180}
$$

$\frac{\pi}{180}$, read "pi over 180", is the size of one degree in radians, about 0.01745. The other way, multiply by 180
over π.

:::example[Degrees into radians]
180 degrees is π radians, about 3.1416, and 90 degrees is π / 2. 60 degrees × 0.01745 = 1.0472 radians. One radian
is 180 / π, about 57.3 degrees.
:::

`glm::radians(60.0f)` gives 1.0472, and `glm::degrees(1.0472f)` gives 60 back. Keep the angles that people read, in
the Inspector or a log, in degrees, and convert them right before you call a function.

:::caution[C++ functions take radians]
`std::sin`, `std::cos` and `std::atan2` work in radians. `std::sin(90.0f)` reads 90 radians and gives about 0.894,
not 1. Nothing warns you: the number is wrong, and the motion looks strange.
:::

Try it: how many radians is 45 degrees? How many degrees is 2 radians?

:::answer
45 × π / 180 = π / 4, about 0.785 radians. 2 × 180 / π is about 114.6 degrees.
:::

## The unit circle turns an angle into a direction

The **unit circle** is the circle of radius 1 around the origin, so every point on it is a unit vector. Turn from the x
axis by an angle, toward the y axis, and walk out to the circle. Where do you stop?

::figure{id=unit-circle}

The **cosine** of an angle is the x coordinate of the point on the unit circle at that angle, written cos θ, where the
Greek letter θ names the angle.

The **sine** of the angle is the y coordinate of the same point, written sin θ.

:::example[The point at 60 degrees]
60 degrees is 1.0472 radians. Its cosine is 0.5 and its sine about 0.866, so the point is (0.5, 0.866). It lies on the
circle: 0.25 + 0.75 = 1.
:::

Every point of the unit circle passes the same check, because its distance from the origin is 1:

$$
\cos^2\theta + \sin^2\theta = 1
$$

$\theta$ is any angle, and $\cos^2\theta$ is read "cos squared of the angle", the cosine times itself. The formula is
the Pythagorean theorem for the triangle under the point.

At the limits, four quarter turns give points you can draw at once: (1, 0) at 0 degrees, (0, 1) at 90, (-1, 0) at 180
and (0, -1) at 270. Cosine and sine never leave the range from -1 to 1. For a point at the distance r instead of 1,
scale: (r cos θ, r sin θ).

The **tangent function** gives the sine of an angle divided by its cosine, tan θ = sin θ / cos θ. In the picture, it is
the slope of the line from the origin to the point: how far up for each unit across. At 90 degrees the cosine is 0, so
the division has no answer.

## Sine over time makes a wave

Feed the sine a time instead of an angle, and the result rises and falls between -1 and 1 forever. The bobbing coin of
[The script loop](../make/script-loop.md) adds such a sine to its middle height.

::figure{id=sine-wave}

The **amplitude** is how far the wave reaches above and below its middle line. The period is the time one full wave
takes. The sine repeats every 2π radians, so a wave that repeats every T seconds feeds the sine 2π × t / T.

$$
y = y_0 + A \sin\left(\frac{2\pi\, t}{T}\right)
$$

$y$ is the height, in units, and $y_0$ the middle height. $A$ is the amplitude, in units. $t$ is the time and $T$ the
period, both in seconds.

:::example[A bobbing coin]
The middle height is 1, the amplitude 0.25 and the period 2 seconds. At t = 0 the sine is 0, so the coin is at 1. At
t = 0.5 s the angle is 2π × 0.5 / 2 = π / 2, whose sine is 1: the coin is at its top, 1.25. At t = 1.5 s it is at its
bottom, 0.75, and at t = 2 s the next wave starts.
:::

At the limits, an amplitude of 0 keeps the coin still. Waves as sound are the subject of [Signals](../basics/signals.md).

## Atan2 turns a direction back into an angle

A game often needs the way back from a direction to an angle: the enemy knows the step to the player, (x, y), and wants
the angle to turn to.

Since tan θ = y / x, the function `std::atan`, which turns the ratio y / x back into an angle, looks right. But the
ratio loses information. The steps (1, 1) and (-1, -1) both give the ratio 1, yet one points up and right and the other down and
left. For x = 0 the division has no answer at all.

**Atan2** is the function that gives the angle of a direction from its two coordinates, taken apart. In C++ it is
`std::atan2(y, x)`, which returns radians from -π to π: positive when y is positive. Mind the order of the arguments: y
first, then x, as in the ratio y / x.

:::example[One angle in each quarter]
The program asks both functions for the angle of a direction in each quarter of the circle, in degrees. Compare the
second and third lines of its output.

```cpp sketch="basics-math-vectors-angles.cpp"
// Degrees to radians, the point on the unit circle at an angle, and the angle of a direction back.
#include <cmath>
#include <cstdio>
#include <glm/glm.hpp>

int main()
{
	const float angle = glm::radians(60.0f);
	std::printf("60 degrees is %.4f radians\n", angle);
	std::printf("cos %.4f, sin %.4f\n", std::cos(angle), std::sin(angle));

	const float x[4] = { 1.0f, -1.0f, -1.0f, 1.0f };
	const float y[4] = { 1.0f, 1.0f, -1.0f, -1.0f };
	for (int i = 0; i < 4; i++)
	{
		const float withAtan2 = glm::degrees(std::atan2(y[i], x[i]));
		const float withAtan = glm::degrees(std::atan(y[i] / x[i]));
		std::printf("(%g, %g): atan2 %g, atan %g\n", x[i], y[i], withAtan2, withAtan);
	}
	return 0;
}
```

```text output-of="basics-math-vectors-angles.cpp"
60 degrees is 1.0472 radians
cos 0.5000, sin 0.8660
(1, 1): atan2 45, atan 45
(-1, 1): atan2 135, atan -45
(-1, -1): atan2 -135, atan 45
(1, -1): atan2 -45, atan -45
```

1. **Lines 8–10:** 60 degrees becomes 1.0472 radians before `std::cos` and `std::sin` see it.
2. **Line 16:** `std::atan2` gets y and x apart and gives 135 and -135 degrees for the two left quarters.
3. **Line 17:** `std::atan` gets only the ratio, so the left quarters come out as -45 and 45 degrees, the wrong way.

:::

At the limits: (0, 1) gives 90 degrees, (0, -1) gives -90 and (-1, 0) gives 180. `std::atan2(0, 0)` returns 0 without
failing, but that 0 means nothing, because the zero vector has no direction.

Try it: what does `glm::degrees(std::atan2(-2.0f, 0.0f))` give?

:::answer
-90. The direction (0, -2) points straight down the y axis, a quarter turn the negative way.
:::

## The dot product measures how much two arrows agree

A guard faces along z, the direction (0, 0, 1), and a coin lies at the step (2, 0, 5) from the guard. Is the coin in
front or behind?

The **dot product** of two vectors is the number you get when you multiply their matching coordinates and add the
products. It is written a · b and read "a dot b".

$$
a \cdot b = a_x b_x + a_y b_y + a_z b_z
$$

$a$ and $b$ are any two vectors, and the result is one plain number. For the guard, (0, 0, 1) · (2, 0, 5) = 0 × 2 + 0 ×
0 + 1 × 5 = 5. For a coin at (2, 0, -5) it is -5.

### The sign says in front or behind

Positive: the two arrows point more or less the same way, the angle between them is less than 90 degrees, and the coin
is in front. Zero: they stand at a right angle. Negative: they point more or less opposite ways, and the coin is behind.

The same number gives the angle. The dot product equals the two lengths multiplied together and by the cosine of the
angle between the arrows:

$$
a \cdot b = \|a\| \, \|b\| \cos\theta
$$

$\theta$ is the angle between the arrows, and the cosine has the same signs: positive below 90 degrees, 0 at 90
and negative above. For two unit vectors both lengths are 1, so the dot product is the cosine of
the angle, and `std::acos`, the angle whose cosine is a number, gives the angle.

:::example[The angle between two directions]
Take a = (1, 0, 0) and b = (1, 1, 0). The length of b is the square root of 2, about 1.414, so its unit vector is
(0.7071, 0.7071, 0). The dot product of a with it is 0.7071, and the angle whose cosine is 0.7071 is 45 degrees.
:::

### The part of a vector along an axis

Put a light straight above a unit axis u, and a vector v casts a shadow on the axis. The dot product v · u is the
length of that shadow, and (v · u) u, read "v dot u, times u", is the shadow as a vector. The **projection** of
v onto u is that shadow: the part of v that lies along the axis.

::figure{id=dot-shadow}

What is left, v - (v · u) u, stands at a right angle to the axis. If u is the up direction of a floor, the leftover is
the part of v that lies in the floor's plane. A character that slides along a slope instead of sinking into it keeps
that part of its velocity.

:::example[Splitting a velocity]
A ball moves with the velocity (3, 2, 0), and the floor's up direction is (0, 1, 0). The dot product is 2, so the part
along up is (0, 2, 0) and the part in the floor is (3, 2, 0) - (0, 2, 0) = (3, 0, 0).
:::

### Bouncing off a surface

The **surface normal** is the unit vector at a right angle to a surface, on its outer side. A ball that
hits a wall keeps the part of its velocity along the wall and turns around the part along the normal. Take that part
away twice, once to cancel it and once more to send it back. The reflection of a direction d about a normal n is
d - 2 (d · n) n, read "d minus twice d dot n, times n".

:::example[A ball against a wall]
The ball flies along (4, 0, 3) toward a wall whose normal is (-1, 0, 0). The dot product is -4, so twice the part along
the normal is 2 × (-4) × (-1, 0, 0) = (8, 0, 0). The reflection is (4, 0, 3) - (8, 0, 0) = (-4, 0, 3): x has turned
around, z is unchanged.
:::

`glm::reflect(d, n)` computes the same formula, and Strata's drawing code uses the same one for shiny surfaces. The
normal must be a unit vector: with a normal of length 2, the part taken away is four times too large.

The program below does this section's examples with `glm::dot` and `glm::reflect`.

```cpp sketch="basics-math-vectors-dot.cpp"
// The dot product: in front or behind, the angle between two directions, a projection and a bounce.
#include <cmath>
#include <cstdio>
#include <glm/glm.hpp>

int main()
{
	const glm::vec3 facing(0.0f, 0.0f, 1.0f);
	std::printf("coin ahead: %g, coin behind: %g\n", glm::dot(facing, glm::vec3(2.0f, 0.0f, 5.0f)), glm::dot(facing, glm::vec3(2.0f, 0.0f, -5.0f)));

	const glm::vec3 a = glm::normalize(glm::vec3(1.0f, 0.0f, 0.0f));
	const glm::vec3 b = glm::normalize(glm::vec3(1.0f, 1.0f, 0.0f));
	std::printf("angle between: %g degrees\n", glm::degrees(std::acos(glm::dot(a, b))));

	const glm::vec3 velocity(3.0f, 2.0f, 0.0f);
	const glm::vec3 up(0.0f, 1.0f, 0.0f);
	const glm::vec3 along = glm::dot(velocity, up) * up; // the part of the velocity along the up axis
	const glm::vec3 flat = velocity - along;             // the part left in the floor's plane
	std::printf("along (%g, %g, %g), flat (%g, %g, %g)\n", along.x, along.y, along.z, flat.x, flat.y, flat.z);

	const glm::vec3 wall(-1.0f, 0.0f, 0.0f); // the wall's normal, pointing back into the room
	const glm::vec3 bounced = glm::reflect(glm::vec3(4.0f, 0.0f, 3.0f), wall);
	std::printf("bounced (%g, %g, %g)\n", bounced.x, bounced.y, bounced.z);
	return 0;
}
```

```text output-of="basics-math-vectors-dot.cpp"
coin ahead: 5, coin behind: -5
angle between: 45 degrees
along (0, 2, 0), flat (3, 0, 0)
bounced (-4, 0, 3)
```

1. **Line 9:** the coin ahead gives 5 and the coin behind -5; only the sign matters for "in front".
2. **Lines 11–13:** both directions become unit vectors before the dot product is read as a cosine.
3. **Lines 17–18:** the part along up and the part in the floor add up to the velocity again.
4. **Line 22:** `glm::reflect` gives the bounce, (-4, 0, 3).

A check at the limits: the dot product of a vector with itself is its squared length. `std::acos` accepts only numbers
from -1 to 1, and rounding can give 1.0000001, so limit the value first with `glm::clamp(value, -1.0f, 1.0f)`.

Try it: is a coin at the step (-3, 0, 1) in front of a guard who faces (0, 0, 1)?

:::answer
The dot product is 0 × (-3) + 0 × 0 + 1 × 1 = 1, which is positive: the coin is in front, though far to the side.
:::

## The cross product gives the arrow at a right angle to two others

Two arrows that point different ways lie in one flat plane, like two pencils on a table. Which way a triangle of a model
faces is the direction straight out of such a plane.

The **cross product** of two vectors is a third vector that stands at a right angle to both. It is written a × b and
read "a cross b".

$$
a \times b = (a_y b_z - a_z b_y,\; a_z b_x - a_x b_z,\; a_x b_y - a_y b_x)
$$

$a$ and $b$ are the two vectors, and the result is a vector. To remember it: the x coordinate uses y and z, the y
coordinate uses z and x, the z coordinate uses x and y.

:::example[The cross product of the x and y axes]
a = (1, 0, 0) and b = (0, 1, 0). The x coordinate is 0 × 0 - 0 × 1 = 0. The y coordinate is 0 × 0 - 1 × 0 = 0. The
z coordinate is 1 × 1 - 0 × 0 = 1. The result is (0, 0, 1): the z axis, at a right angle to both.
:::

### Which way it points, and how long it is

Two directions stand at a right angle to a plane, one out of each side. The **right-hand rule** tells which one the
formula picks: point the first finger of your right hand along a and the middle finger along b, and your thumb points
along a × b.

::figure{id=right-hand}

Swap the order and the thumb turns around: b × a = -(a × b). In the example, (0, 1, 0) × (1, 0, 0) = (0, 0, -1).

The length of a × b is the area of the slanted rectangle the two arrows span from one point. It equals the two lengths
multiplied together and by the sine of the angle between them. At the limits, two arrows along one line span no area
and give the zero vector; two arrows at a right angle give the largest area.

### The normal of a triangle

A model is drawn from small triangles, and lighting needs to know which way each one faces. The cross product of two
edges from one corner, p1 - p0 and p2 - p0, stands at a right angle to the triangle. As a unit vector, it is the
triangle's surface normal. Half its length is the triangle's area, because the triangle is half the slanted rectangle.

:::example[A triangle in the plane of x and y]
The corners are p0 = (0, 0, 0), p1 = (4, 0, 0) and p2 = (0, 3, 0), so the edges are (4, 0, 0) and (0, 3, 0). Their
cross product is (0 × 0 - 0 × 3, 0 × 0 - 4 × 0, 4 × 3 - 0 × 0) = (0, 0, 12). The normal is (0, 0, 1), and the area is
12 / 2 = 6, which matches a right triangle with sides 4 and 3.
:::

The order of the corners decides the side. The corners in the order p0, p2, p1 give (0, 0, -12) and a normal that
points the other way. The program below checks this section's examples with `glm::cross`.

```cpp sketch="basics-math-vectors-cross.cpp"
// The cross product: a right angle to both, its order, and the normal and area of a triangle.
#include <cstdio>
#include <glm/glm.hpp>

int main()
{
	const glm::vec3 x(1.0f, 0.0f, 0.0f);
	const glm::vec3 y(0.0f, 1.0f, 0.0f);
	const glm::vec3 xy = glm::cross(x, y);
	const glm::vec3 yx = glm::cross(y, x);
	std::printf("cross(x, y) (%g, %g, %g), cross(y, x) (%g, %g, %g)\n", xy.x, xy.y, xy.z, yx.x, yx.y, yx.z);

	const glm::vec3 p0(0.0f, 0.0f, 0.0f);
	const glm::vec3 p1(4.0f, 0.0f, 0.0f);
	const glm::vec3 p2(0.0f, 3.0f, 0.0f);
	const glm::vec3 edges = glm::cross(p1 - p0, p2 - p0);
	const glm::vec3 normal = glm::normalize(edges);
	std::printf("cross of the edges (%g, %g, %g), normal (%g, %g, %g)\n", edges.x, edges.y, edges.z, normal.x, normal.y, normal.z);
	std::printf("triangle area %g\n", glm::length(edges) / 2.0f);
	return 0;
}
```

```text output-of="basics-math-vectors-cross.cpp"
cross(x, y) (0, 0, 1), cross(y, x) (0, 0, -1)
cross of the edges (0, 0, 12), normal (0, 0, 1)
triangle area 6
```

1. **Lines 9–10:** the same two axes in two orders give opposite results.
2. **Line 16:** the cross product of two edges from one corner.
3. **Line 19:** half its length is the triangle's area.

### The lever arm

Push a door near its hinge and it barely moves; push at the handle, far from the hinge, and it swings. The **lever
arm** is the step from the point a body turns around to the point where the push acts. The cross product of the lever
arm and the push says how hard the push turns the body, and around which line. This turning effect is called torque,
and [Dynamics](../physics/dynamics.md) explains it.

Try it: compute (0, 2, 0) × (0, 0, 3). Which way does the result point?

:::answer
(2 × 3 - 0 × 0, 0 × 0 - 0 × 3, 0 × 0 - 2 × 0) = (6, 0, 0): straight along the x axis. Its length, 6, is the area of the
2 by 3 rectangle the two arrows span.
:::

## Common mistakes

- **Degrees passed to `std::sin`.** Symptom: a wave that looks random. Fix: convert with `glm::radians`.
- **The arguments of `std::atan2` swapped.** Symptom: a character that faces the wrong way for some directions. Fix: y
  first, then x.
- **The zero vector normalized.** Symptom: the new position is `nan`. Strata refuses to write it, with a warning that
  "the translation must be finite", and the entity stops moving. The warning comes once, so read the **Console** from
  its first line. Fix: check the length before you divide by it.
- **A dot product of vectors that are not unit vectors read as a cosine.** Symptom: `std::acos` returns `nan`, or
  wrong angles. Fix: make both unit vectors first.
- **The order of a cross product.** Symptom: a normal that points into a surface. Fix: swap the arguments, and check
  with the right-hand rule.
- **`a * b` taken for the dot product.** Symptom: a vector where you expected one number. `glm` multiplies two vectors
  one coordinate at a time: (1, 2, 3) * (4, 5, 6) is (4, 10, 18). Fix: call `glm::dot(a, b)`.
- **A vector declared without a value.** Symptom: an entity that jumps to a strange place. `glm::vec3 v;` holds
  whatever was in memory, not zeros. Fix: write `glm::vec3 v(0.0f);`.

## Summary

- A position is three coordinates measured from an origin; a vector is a step between positions, b - a, and vectors
  add, subtract and scale one coordinate at a time.
- A vector's length is the square root of its squared coordinates added together, and a distance is the length of a
  step. A unit vector has the length 1; the zero vector has no direction.
- Angles in C++ are radians, degrees × π / 180. The point at an angle on the unit circle is (cos θ, sin θ), and
  `std::atan2(y, x)` gives the angle of a direction in all four quarters.
- The dot product adds the products of matching coordinates: its sign tells in front from behind, for unit vectors it
  is the cosine of the angle, and it gives projections and reflections.
- The cross product stands at a right angle to two vectors, points as the right-hand rule says, changes sign when the
  order changes, and has the area of their slanted rectangle as its length.

## Check yourself

1. What is the length of (2, 3, 6)? (a) 11 (b) 7 (c) 49 (d) the square root of 11

   :::answer{tests="length-direction"}
   (b) 7, the square root of 4 + 9 + 36 = 49. (a) adds the coordinates without squares, (c) forgets the square root,
   and (d) takes the root of the plain sum.
   :::

2. Predict the output of `glm::degrees(std::atan2(0.0f, -2.0f))` and of `glm::degrees(std::atan(0.0f / -2.0f))`.

   :::answer{tests="angles"}
   180, and -0, a zero with a sign that equals 0. The direction (-2, 0) is half a turn, which only `std::atan2` sees;
   the ratio is 0, whose angle is 0.
   :::

3. Two vectors that are not zero have a dot product of 0. What do you know? (a) they point the same way (b) they stand
   at a right angle (c) they point opposite ways (d) one of them is a unit vector

   :::answer{tests="dot-product"}
   (b). The same direction gives a positive dot product and opposite ones a negative one; a vector's length cannot make
   it zero.
   :::

4. The cross product a × b is (0, 0, 12). What is b × a?

   :::answer{tests="cross-product"}
   (0, 0, -12): the same length, the opposite direction.
   :::

5. Compute 2 × (1, -2, 0) + (0, 4, 1).

   :::answer{tests="vector-steps"}
   2 × (1, -2, 0) = (2, -4, 0), and adding (0, 4, 1) gives (2, 0, 1).
   :::

6. What does `glm::vec3(1.0f, 2.0f, 3.0f) * glm::vec3(4.0f, 5.0f, 6.0f)` give? (a) 32 (b) (4, 10, 18) (c) (5, 7, 9)

   :::answer{tests="dot-product"}
   (b): `*` multiplies matching coordinates and keeps them apart. (a) is the dot product, from `glm::dot`; (c) is the
   sum.
   :::

## Practice

1. **Basic.** By hand, compute the distance between (1, 2, 3) and (4, 6, 15), and the unit vector of the step from the
   first point to the second.

   :::answer[Worked solution]{tests="vector-steps length-direction"}
   The step is (3, 4, 12). Its squares add up to 9 + 16 + 144 = 169, whose square root is 13: the distance. The unit
   vector is (3 / 13, 4 / 13, 12 / 13), about (0.231, 0.308, 0.923).
   :::

2. **Medium.** The bobbing coin has the middle height 1, the amplitude 0.25 and the period 2 seconds. Write its height
   at the time `t` in C++, and compute it at t = 0.25 s.

   :::answer[Worked solution]{tests="angles"}
   `1.0f + 0.25f * std::sin(2.0f * glm::pi<float>() * t / 2.0f)`. At t = 0.25 s the angle is π / 4, whose sine is
   about 0.7071, so the height is about 1.177.
   :::

3. **Medium.** A ball falls onto a floor whose normal is (0, 1, 0), with the velocity (2, -3, 1). Split the velocity
   into the part along the normal and the part in the floor, then compute the bounced velocity.

   :::answer[Worked solution]{tests="dot-product"}
   The dot product with the normal is -3: the part along it is (0, -3, 0), the part in the floor (2, 0, 1). The bounce
   is (2, -3, 1) - 2 × (-3) × (0, 1, 0) = (2, 3, 1).
   :::

4. **Medium.** A triangle has the corners p0 = (0, 0, 0), p1 = (0, 0, 2) and p2 = (2, 0, 0). Compute the cross product
   of p1 - p0 and p2 - p0, the normal and the area. Which way would the normal point with p1 and p2 swapped?

   :::answer[Worked solution]{tests="cross-product"}
   The edges are (0, 0, 2) and (2, 0, 0). Their cross product is (0 × 0 - 2 × 0, 2 × 2 - 0 × 0, 0 × 0 - 0 × 2),
   which is (0, 4, 0). The normal is (0, 1, 0), straight up, and the area is 2. Swapped, the normal points down.
   :::

5. **Hard.** In the `Playground` script, write a function `MagnetStep` above the class. It takes a coin's position, the
   ball's position, a reach, a speed and the frame's time, and returns the coin's new position. A coin within the reach
   moves toward the ball at the speed, never past it; any other coin stays. In `OnCreate`, log five frames of 0.125 s
   for a coin at (2, 0.5, 0), the ball at (0, 0.5, 0), a reach of 3 and a speed of 4.

   :::answer[Worked solution]{tests="vector-steps length-direction" solution="sketches/basics-math-vectors-magnet.cpp"}
   The step from the coin to the ball gives the distance and, as a unit vector, the direction. The program below prints
   with `std::printf` what `Log::Info` writes in the playground.

   ```cpp sketch="basics-math-vectors-magnet.cpp"
   // The magnet's step for one frame: a coin within reach moves toward the ball at a fixed speed.
   #include <cstdio>
   #include <glm/glm.hpp>

   glm::vec3 MagnetStep(const glm::vec3& coin, const glm::vec3& ball, float reach, float speed, float deltaTime)
   {
   	const glm::vec3 toBall = ball - coin;
   	const float distance = glm::length(toBall);
   	if (distance > reach || distance < 0.001f) // out of reach, or already on the ball: no direction to move in
   		return coin;
   	return coin + glm::normalize(toBall) * glm::min(speed * deltaTime, distance); // never step past the ball
   }

   int main()
   {
   	const glm::vec3 ball(0.0f, 0.5f, 0.0f);
   	glm::vec3 coin(2.0f, 0.5f, 0.0f);
   	for (int frame = 1; frame <= 5; frame++)
   	{
   		coin = MagnetStep(coin, ball, 3.0f, 4.0f, 0.125f);
   		std::printf("frame %d: coin at (%g, %g, %g)\n", frame, coin.x, coin.y, coin.z);
   	}
   	std::printf("a coin 5 m away stays at x = %g\n", MagnetStep(glm::vec3(5.0f, 0.5f, 0.0f), ball, 3.0f, 4.0f, 0.125f).x);
   	return 0;
   }
   ```

   ```text output-of="basics-math-vectors-magnet.cpp"
   frame 1: coin at (1.5, 0.5, 0)
   frame 2: coin at (1, 0.5, 0)
   frame 3: coin at (0.5, 0.5, 0)
   frame 4: coin at (0, 0.5, 0)
   frame 5: coin at (0, 0.5, 0)
   a coin 5 m away stays at x = 5
   ```

   1. **Line 9:** the reach and the zero length are checked before any division.
   2. **Line 11:** the unit vector times the move gives a step of exactly that length, 0.5 per frame here. `glm::min`
      keeps the last move from carrying the coin past the ball, so it stops on frame 4.
   :::

6. **Hard.** Optional, in your Coin Run or the last checkpoint of [Coin Run](../make/project-coin-run.md): write a
   `CoinMagnet` script that pulls every coin within 3 m toward the ball `Ball`, and play. `CoinPlacer` copies
   `Prefabs/Coin.stprefab` at play, so add the script to a copy dragged into the scene, apply it to the prefab and
   delete the copy.

   :::answer[Worked solution]{tests="length-direction"}
   `Scene::FindEntityByName` finds the
   ball by the name in the `BallName` field; type your ball's name there in the Inspector if it is not `Ball`. The
   script reads and writes [world positions](../make/transforms-units.md), so it works for a coin with a parent too.
   The book's checks build only programs that stand alone, so the listings are marked as
   :term[pseudocode]{id=pseudocode}. Yet they are the whole class, and build as they stand in `Scripts/CoinMagnet.cpp`
   below `MagnetStep` of the previous exercise.

   ```cpp pseudocode
   class CoinMagnet : public Script
   {
   public:
   	std::string BallName = "Ball";
   	float Reach = 3.0f;
   	float Speed = 4.0f;

   	void OnUpdate(float deltaTime) override
   	{
   		const Entity ball = Scene::FindEntityByName(BallName);
   		if (!ball)
   			return;
   		TransformComponent transform = GetTransform();
   		const glm::vec3 ballPosition = ball.GetTransform().GetWorldPosition();
   		transform.SetWorldPosition(MagnetStep(transform.GetWorldPosition(), ballPosition, Reach, Speed, deltaTime));
   	}
   };
   ```

   1. **Lines 10–12:** without an entity of that name, the entity is not valid, and the script waits.
   2. **Line 15:** the new position comes from `MagnetStep`, whose length check keeps out the zero vector.

   Below the class, the registration names the fields, which then appear in the Inspector.

   ```cpp pseudocode
   ST_SCRIPT_CLASS(CoinMagnet)
   {
   	ST_SCRIPT_FIELD(BallName);
   	ST_SCRIPT_FIELD(Reach);
   	ST_SCRIPT_FIELD(Speed);
   }
   ```

   Coin Run's `Coin` sets only the height, so the two scripts share the position. A coin script that writes the whole
   position calls `MagnetStep` itself instead.
   :::

## Where the book uses it

- [Gameplay math](../make/gameplay-math.md): is it close, is it in front, turn toward it.
- [Collision detection](../physics/collision-detection.md): lengths, dot products and normals tell whether shapes touch.
- [Reflectance](../light/reflectance.md): light from dot products and the reflected view direction.
- [Spatial audio](../audio/spatial.md): the distance to a sound and the directions the listener faces.

## Further reading

- [The glm manual](https://github.com/g-truc/glm/blob/master/manual.md): the functions this page calls; intermediate.
- [3Blue1Brown, "Essence of linear algebra"](https://www.3blue1brown.com/topics/linear-algebra): videos that draw
  vectors and both products as moving pictures; beginner.
