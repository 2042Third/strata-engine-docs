---
id: basics/math-rotations
title: "Rotations and quaternions"
description: "Describe how a thing faces with Euler angles, an axis and an angle, or a quaternion; combine turns by multiplying, and blend two rotations with slerp."
kind: primer
size: L
tracks: [B, E]
needs: [basics/math-bases]
time: 90
learn:
  - id: euler-order
    text: explain how yaw, pitch and roll build a rotation in Strata's order, and why Euler angles lock and blend badly
  - id: axis-angle
    text: compute the quaternion of an axis and an angle, and explain why it holds half the angle
  - id: combine
    text: predict the result of multiplying two quaternions in either order, of rotating a direction with one, and of comparing two
  - id: slerp
    text: choose slerp or nlerp to blend two rotations, and take the shorter arc
  - id: angular-velocity
    text: compute the small turn that an angular velocity makes in one step
status: final
---

::::test-out

1. Strata applies the pitch around the X axis first, then the yaw around Y, then the roll around Z. Which direction does the forward direction (0, 0, -1) face after a pitch of 90 degrees and nothing else?

   :::answer{tests="euler-order"}
   The pitch turns around X, so the z value moves into y: the result is (0, 1, 0), straight up.
   :::

2. Compute the four numbers (w, x, y, z) of the quaternion for a turn of 180 degrees around the Y axis.

   :::answer{tests="axis-angle"}
   A quaternion holds the cosine and the sine of half the angle. Half of 180 degrees is 90 degrees, so w is 0 and the axis (0, 1, 0) is multiplied by 1: (0, 0, 1, 0).
   :::

3. A script holds `turn` and `rotation`. Which product turns the entity around its parent's axes: `turn * rotation` or `rotation * turn`?

   :::answer{tests="combine"}
   `turn * rotation`. The left factor acts last and turns around the fixed axes; `rotation * turn` turns around the entity's own axes.
   :::

4. The dot product of two quaternions is -0.9. What do you do before you blend them, and what happens if you do not?

   :::answer{tests="slerp"}
   Change the sign of one of them, because both signs are the same rotation. Without that, the blend takes the longer arc and turns the long way round.
   :::

5. A body turns with the angular velocity (0, 0, 3) radians per second. Name the axis and the rate, and compute the angle it turns in 0.1 s.

   :::answer{tests="angular-velocity"}
   The axis is Z and the rate is 3 radians per second. In 0.1 s it turns 3 × 0.1 = 0.3 radians, about 17.2 degrees.
   :::

::::

## Why you will need this

A game turns things all the time. A coin spins, a camera looks where the mouse moves, an arrow follows a target, a door swings. A position is three numbers that you add. A rotation is harder: it can be written in four ways, and each way is good at one job and poor at another.

This page teaches the four ways and when to use each. [Transforms and units](../make/transforms-units.md) places things with the Inspector's angles. [Interpolation](../world/interpolation.md) blends two poses to draw a frame between fixed steps. [Blending animations](../animation/blending.md) mixes the rotations of a skeleton. [Dynamics](../physics/dynamics.md) turns bodies by their angular velocity.

:::question[Why do the programs start with lines I have not seen?]
Each program starts with `#include` lines that bring in `glm`, and calls functions such as `glm::angleAxis(...)`, whose `glm::` names the library. [Programming 3](../basics/programming-3.md) explains both; here, read them as "use the library" and "call its function".
:::

## Euler angles name three turns around three axes

Hold a toy aeroplane. Turn its nose to the left or the right, and you change its **yaw angle**: the angle of the turn around the vertical axis.

Tip its nose up or down, and you change its **pitch angle**: the angle of the turn around the axis that runs from wing to wing.

Tilt it from wing to wing, as a pilot does when banking into a curve, and you change its **roll angle**: the angle of the turn around the axis that runs from tail to nose.

Together the three angles are **Euler angles**: a rotation written as three angles, one around each axis, applied in a fixed order. Strata's axes are those of [Matrices](../basics/math-matrices.md): +X to the right, +Y up and -Z forward. So the yaw turns around Y, the pitch around X and the roll around Z, the line along the nose. A positive angle follows the right-hand rule of the :term[cross product]{id=cross-product}: the thumb points along the axis and the fingers curl the way the turn goes. A positive yaw turns the nose to the left, a positive pitch tips it upward and a positive roll lowers the left wing.

::figure{id=three-turns}

The order matters, because two turns give a different result when you swap them. The section on multiplying quaternions shows numbers.

Strata builds a rotation from Euler angles as `glm` does. The pitch turns first, then the yaw, then the roll, and every turn goes around the fixed axes of the parent, not around the axes the nose now points along. With no roll, as for a camera or a character, that equals the story of the toy: yaw first, then pitch around the nose's new side axis. With a roll the two differ. After a yaw, Strata's roll still turns around the fixed Z axis, which is no longer the line along the nose, so it does not bank the aeroplane.

The Inspector shows the three angles in degrees, in its fields **X**, **Y** and **Z**: X is the pitch, Y the yaw and Z the roll. A script reads and writes them in :term[radians]{id=radian}: `GetEulerAngles` and `SetEulerAngles` of a transform hold the pitch, the yaw and the roll, in that order. Convert with `glm::radians` and `glm::degrees`, as [Vectors](../basics/math-vectors.md) showed.

## Yaw and pitch give a direction

Many things need only a direction: where a camera looks, where a gun aims. Two angles are enough for a direction, because a roll turns the thing around its own nose and leaves the nose where it was. The forward direction starts as (0, 0, -1). The pitch first lifts it to (0, sin pitch, -cos pitch), a point on the :term[unit circle]{id=unit-circle} in the plane of y and z. The yaw then turns that around Y.

$$
d = (-\cos\phi\,\sin\theta,\;\; \sin\phi,\;\; -\cos\phi\,\cos\theta)
$$

$d$ is the unit direction. $\theta$ is the yaw and $\phi$ is the pitch, both in radians. The three numbers read "minus :term[cosine]{id=cosine} of the pitch times :term[sine]{id=sine} of the yaw" for x, "sine of the pitch" for y and "minus cosine of the pitch times cosine of the yaw" for z. At the limits it behaves: with both angles 0 it gives (0, 0, -1), the forward direction; a pitch of 90 degrees gives (0, 1, 0), straight up, whatever the yaw.

:::example[A camera yawed 30 degrees and pitched 45 degrees]
The cosine of 45 degrees is 0.7071 and its sine is 0.7071; the sine of 30 degrees is 0.5 and its cosine is 0.866. So x is -0.7071 × 0.5 = -0.354, y is 0.707 and z is -0.7071 × 0.866 = -0.612. The squares add up to 0.125 + 0.5 + 0.375 = 1, so the result is a :term[unit vector]{id=unit-vector}, as a direction should be. The camera faces to the left, upward and forward.
:::

Try it: a camera has the yaw 90 degrees and the pitch 0. Which way does it face?

:::answer
x is -cos 0 × sin 90° = -1, y is 0 and z is -cos 0 × cos 90° = 0: (-1, 0, 0), to the left, along -X.
:::

An **orbit camera**, one that circles a target, keeps only these two angles and a distance. It sits at the target minus the direction times the distance, and it faces the target. The `FollowCamera` of `Samples/ThirdPerson/Scripts/FollowCamera.cpp` keeps a `Yaw`, a `Pitch` and a `Distance`, and clamps the pitch between a minimum and a maximum. The same two angles name a point on a sphere around the target, as the two angles of a place on a globe do. [Directions on a sphere](../basics/math-sphere.md) measures the second angle from the :term[up axis]{id=up-axis} instead of from the horizon, so that angle is 90 degrees minus the pitch.

The other way round, the yaw of a direction comes from `atan2`: yaw = atan2(-x, -z). `ThirdPersonPlayer` in `Samples/ThirdPerson/Scripts/ThirdPersonPlayer.cpp` turns toward the way it walks with exactly that call. For the direction (-1, 0, -1), `atan2(1, 1)` gives 45 degrees.

## Gimbal lock loses a turn, and Euler angles blend badly

The name comes from gimbals, the nested rings that hold a compass level. When the pitch is 90 degrees, the nose of a plane points straight up. The roll axis along the nose then lies along the vertical axis, which is also the yaw's axis. Two of the three angles turn around the same line, and nothing turns around the third. That is **gimbal lock**: a state of Euler angles in which two axes line up, so two angles make the same turn and a direction of turning disappears.

::figure{id=gimbal-lock}

In Strata's order the middle turn is the yaw, so the lock comes at a yaw of 90 degrees. There the yaw swings the X axis, which the pitch turns around, onto the -Z axis, which the roll turns around. A pitch and a roll then undo or repeat each other: only the roll minus the pitch matters.

:::example[Two triples, one rotation]
The sketch builds the rotation of (30, 90, 30) degrees and that of (0, 90, 0), and prints the absolute value of the :term[dot product]{id=dot-product} of the two quaternions: 1 means the same rotation. It also reads a yaw of 120 degrees back as Euler angles.

```cpp sketch="basics-math-rotations-euler.cpp"
// Euler angles read back, and a gimbal lock: two triples of angles that make one rotation.
#include <cstdio>
#include <glm/glm.hpp>
#include <glm/gtc/quaternion.hpp>

int main()
{
	const glm::quat yawed(glm::radians(glm::vec3(0.0f, 120.0f, 0.0f))); // pitch, yaw, roll, in degrees
	const glm::vec3 back = glm::degrees(glm::eulerAngles(yawed));
	std::printf("yaw 120 reads back as (%.1f, %.1f, %.1f)\n", back.x, back.y, back.z);

	const glm::quat a(glm::radians(glm::vec3(30.0f, 90.0f, 30.0f)));
	const glm::quat b(glm::radians(glm::vec3(0.0f, 90.0f, 0.0f)));
	std::printf("|dot| of (30, 90, 30) and (0, 90, 0): %.4f\n", glm::abs(glm::dot(a, b)));
	return 0;
}
```

```text output-of="basics-math-rotations-euler.cpp"
yaw 120 reads back as (180.0, 60.0, 180.0)
|dot| of (30, 90, 30) and (0, 90, 0): 1.0000
```

1. **Line 8:** `glm::quat` builds a rotation from three angles in radians: pitch, yaw, roll.
2. **Line 9:** `glm::eulerAngles` is the way back: it reads the three angles of a rotation.
3. **Lines 12–14:** the pitch 30 and the roll 30 cancel at a yaw of 90, so the two rotations are the same.

:::

Try it: what does `GetEulerAngles` give for an entity with the yaw 100 degrees, 0 elsewhere?

:::answer
(180, 80, 180) degrees. The yaw is read through an inverse sine, which gives only -90 to 90 degrees, so Strata's `GetEulerAngles` returns another triple of the same rotation.
:::

The second line of the output shows the other trouble. The way back from a rotation to angles gives the yaw only between -90 and 90 degrees. A yaw of 120 degrees reads back as (180, 60, 180): the same rotation, other angles. A script that turns an entity by reading the yaw, adding a little and writing it back climbs to 90 degrees and stalls there. Past 90, each step turns it backward: at a yaw of 120 it reads 60 and writes 61, which is the same rotation as a yaw of 119.

The fix is to keep the yaw and the pitch in fields of your own and build the rotation from them each frame, as `FollowCamera` and `ThirdPersonPlayer` do. The Inspector keeps the angles you type for the same reason, so that a drag past 90 degrees does not jump.

Blending suffers too. Blend by taking a weighted average of each angle, and a yaw from 10 to 350 degrees passes 180 halfway. The plane spins nearly all the way round instead of turning 20 degrees the short way. With three angles at once, the in-between rotations also move along paths that no one chose. A better way to describe a rotation has no lock and blends along the shortest turn.

## An axis and an angle name any rotation

Every rotation in 3D, however it was made, equals one turn around one axis. **Axis-angle** is that description: a unit vector for the axis and the angle to turn by, in radians, following the right-hand rule. `glm::angleAxis(angle, axis)` makes a quaternion from it. The axis must have length 1: glm does not :term[normalize]{id=normalization} it for you, so call `glm::normalize` on a tilted axis such as (0.3, 1, 0).

For a turn of $\theta$ radians around Y, the rotation matrix has three columns that say where the axes go, as [Matrices](../basics/math-matrices.md) taught. The X axis lands at (cos θ, 0, -sin θ), the Y axis stays at (0, 1, 0) and the Z axis lands at (sin θ, 0, cos θ). For θ = 0 every axis stays in place. For a quarter turn, 90 degrees, the columns are (0, 0, -1), (0, 1, 0) and (1, 0, 0): X goes to -Z and Z goes to X.

A turn around a tilted axis fills the matrix with products of the axis's numbers, the cosine and the sine; `glm::mat3_cast` computes it from a quaternion. The columns stay at right angles and keep their length, so the inverse of this matrix is the matrix with its rows and columns swapped, as [Bases](../basics/math-bases.md) showed.

Try it: where does the X axis land after a 90-degree turn around Z?

:::answer
Around Z, X turns toward Y: (0, 1, 0). The matrix's first column is (cos 90°, sin 90°, 0).
:::

## A quaternion stores the axis and the half angle

Axis and angle show a turn at a glance but are awkward to combine. A **quaternion** is a rotation written as four numbers: the cosine of half the angle, and the axis multiplied by the sine of half the angle.

$$
w = \cos\frac{\theta}{2}, \qquad (x, y, z) = \sin\frac{\theta}{2}\,(a_x, a_y, a_z)
$$

$w$ is the first number, $x$, $y$ and $z$ the others, and $\theta$ is the angle in radians. $a_x$, $a_y$ and $a_z$ are the coordinates of the unit axis. The formula reads "w is the cosine of half the angle".

:::example[Three quaternions around the Y axis]
A quarter turn, 90 degrees, has half angle 45 degrees: w = 0.7071 and y = 0.7071, so the quaternion is (0.7071, 0, 0.7071, 0). A half turn has half angle 90 degrees: (0, 0, 1, 0). No turn at all has the half angle 0: (1, 0, 0, 0), the **identity**, the rotation that changes nothing. Squares check the length: 0.7071² + 0.7071² = 1.
:::

Try it: write the quaternion of 60 degrees around Z.

:::answer
The half angle is 30 degrees: w = cos 30° = 0.866 and z = sin 30° = 0.5, so (0.866, 0, 0, 0.5).
:::

Because cos² + sin² = 1 and the axis has length 1, the four numbers of a turn always have length 1. A quaternion of length 1 is a unit quaternion, and only those are rotations. Each multiplication adds a little :term[rounding error]{id=rounding-error} to the length, so code that multiplies many times calls `glm::normalize` now and then. A script need not worry about the rotation it sets, because Strata normalizes it. Strata refuses a rotation that is not finite or has length zero, and reports "the rotation must be a finite, non-zero quaternion".

::figure{id=half-angle}

Why half the angle? To turn a direction $v$, the quaternion $q$ takes the sandwich $q\,v\,q^{*}$, where $q^{*}$ is its conjugate, defined below. The turn acts once from each side, so each side carries half of the angle. Take a full turn of 360 degrees: its half angle is 180 degrees and its quaternion is (-1, 0, 0, 0). A full turn leaves every direction in place, yet its quaternion is not the identity, as the section on two quaternions for each rotation explains.

The same four numbers appear in three orders. The constructor `glm::quat(w, x, y, z)` takes w first, so the identity is `glm::quat(1, 0, 0, 0)`. The members of a `glm::quat` are stored x, y, z, w, and `Log::Info` prints `quat(x, y, z, w)`. A script field of a quaternion type is set by `[x, y, z, w]` or by Euler degrees `[pitch, yaw, roll]`.

| Where | Order | The identity |
| --- | --- | --- |
| The constructor `glm::quat(w, x, y, z)` | w, x, y, z | `glm::quat(1, 0, 0, 0)` |
| The members, and what `Log::Info` prints | x, y, z, w | `quat(0, 0, 0, 1)` |
| A script field set by a command | `[x, y, z, w]` | `[0, 0, 0, 1]` |

## Multiplying quaternions combines turns

Two turns in a row are one quaternion product, and the product reads right to left, as matrices do: in `a * b` the turn `b` acts first and `a` acts last. For two turns around the same axis the angles add, so the half angles add too. The product of $(\cos a, \sin a\,n)$ and $(\cos b, \sin b\,n)$ is $(\cos(a + b), \sin(a + b)\,n)$, with $a$ and $b$ the half angles and $n$ the axis. Two quarter turns around Y give w = 0.7071² - 0.7071² = 0 and y = 2 × 0.7071 × 0.7071 = 1: (0, 0, 1, 0), the half turn.

:::question[What are `override` and the class around this line?]
The line belongs to a class that extends `Script`; [Classes](../basics/cpp-classes.md) explains `override` and the class around it. Here, read it as the function that runs every frame.
:::

The product of turns around different axes depends on the order. [First script](../make/first-script.md) wrote the `Spinner` that relies on it. The editor generates it for a new script project, and its heart is two lines.

```cpp src="StrataEditor/src/Editor/ScriptProject.cpp#L246-L251"
void OnUpdate(float deltaTime) override
{
	TransformComponent transform = GetTransform();
	const glm::quat turn = glm::angleAxis(glm::radians(DegreesPerSecond * deltaTime), glm::vec3(0.0f, 1.0f, 0.0f));
	transform.SetRotation(turn * transform.GetRotation());
}
```

The `turn` is a small turn around Y, made from `DegreesPerSecond` and the frame's `deltaTime`. The last line multiplies it on the left of the current rotation, so the turn acts after the rotation, around the fixed axes of the parent. `GetRotation` is the local rotation, relative to the parent, so those axes are the world's only when the entity has no rotated parent. Multiply on the right instead, `rotation * turn`, and the turn acts first, around the entity's own axes.

:::example[Yaw and pitch in both orders]
The sketch turns the forward direction by a yaw and a pitch of 90 degrees, in both orders, and then undoes a yaw with its conjugate. Compare the first two lines of the output.

```cpp sketch="basics-math-rotations-compose.cpp"
// Combining two turns: the order decides which axes they turn around.
#include <cstdio>
#include <glm/glm.hpp>
#include <glm/gtc/quaternion.hpp>

void Print(const glm::vec3& v)
{
	const glm::vec3 shown = glm::round(v * 100.0f) / 100.0f + 0.0f; // two places, and no -0
	std::printf("(%g, %g, %g)\n", shown.x, shown.y, shown.z);
}

int main()
{
	const glm::quat yaw = glm::angleAxis(glm::radians(90.0f), glm::vec3(0.0f, 1.0f, 0.0f));
	const glm::quat pitch = glm::angleAxis(glm::radians(90.0f), glm::vec3(1.0f, 0.0f, 0.0f));
	const glm::vec3 forward(0.0f, 0.0f, -1.0f);
	std::printf("yaw * pitch turns forward to ");
	Print(yaw * pitch * forward);
	std::printf("pitch * yaw turns forward to ");
	Print(pitch * yaw * forward);
	std::printf("the conjugate of yaw undoes it: ");
	Print(glm::conjugate(yaw) * (yaw * forward));
	return 0;
}
```

```text output-of="basics-math-rotations-compose.cpp"
yaw * pitch turns forward to (0, 1, 0)
pitch * yaw turns forward to (-1, 0, 0)
the conjugate of yaw undoes it: (0, 0, -1)
```

1. **Lines 14–15:** `glm::angleAxis` makes the two quarter turns; the axes (0, 1, 0) and (1, 0, 0) have length 1.
2. **Lines 17–20:** the same two quaternions in the two orders. `yaw * pitch` lifts the nose first and then turns around the vertical, which leaves a nose that points up; `pitch * yaw` turns the nose to the left first, and the pitch around X cannot move it.
3. **Lines 21–22:** the conjugate turns the direction back.

:::

Writing `rotation * direction` turns a direction by a rotation: `glm` computes the sandwich. Strata's own `GetForward` is the world rotation times (0, 0, -1). The **conjugate** of a quaternion keeps w and flips the signs of x, y and z. It is the same axis with the opposite angle, because sin(-θ / 2) = -sin(θ / 2), so for a unit quaternion it is the inverse: `glm::conjugate(q) * q` is the identity, and `glm::inverse` gives the same.

Try it: what does `glm::conjugate(yaw) * yaw` give, with `yaw` any unit quaternion?

:::answer
The identity, (1, 0, 0, 0): the conjugate turns by the negative angle around the same axis, and the two turns add up to none.
:::

## Two quaternions name every rotation

The full turn above has the quaternion (-1, 0, 0, 0), and the identity is (1, 0, 0, 0). Both leave every direction in place. In general a turn of θ + 360 degrees equals a turn of θ, and the half angle moves by 180 degrees, which flips the sign of both the cosine and the sine. So $q$ and $-q$ are one rotation. The word for this is **double cover**: each rotation has exactly two quaternions, and the unit quaternions cover the rotations twice.

Never compare rotations number by number, because $q$ and $-q$ differ in all four. Compare the absolute value of the dot product instead. For two unit quaternions the dot product is the cosine of half the angle between the rotations: 1 for equal ones, and -1 for $q$ against $-q$. The absolute value is 1 in both cases. Strata's `Math::IsNearlyEqual` for two `glm::quat` values in `Strata/src/Strata/Math/Math.h` checks that the absolute value of the dot product lies within a small limit of 1, and [Math](../core/math.md) lists its siblings.

:::example[Equal or not?]
The quaternions (0.7071, 0, 0.7071, 0) and (-0.7071, 0, -0.7071, 0) have the dot product -0.5 - 0.5 = -1, with the absolute value 1: the same quarter turn. The quaternions (0, 0, 1, 0) and (0.7071, 0, 0.7071, 0) have the dot product 0.7071. That is far from 1, so the rotations differ, by 2 × 45 = 90 degrees, because the angle whose cosine is 0.7071 is 45 degrees.
:::

Try it: do (1, 0, 0, 0) and (0, 0, 0, 1) give the same rotation?

:::answer
No. The dot product is 0, far from 1 or -1. The second is a half turn around Z.
:::

## Slerp blends two rotations at an even speed

A game blends rotations when an arrow turns toward a target or a camera eases into a new view. Unit quaternions are points on a sphere in four dimensions, and a blend with the weight $t$, from 0 to 1, should stay on that sphere and move at an even speed. **Slerp**, short for spherical linear interpolation, does that: it walks the arc between the two quaternions, covering an equal part of the angle for an equal step of $t$.

$$
\mathrm{slerp}(a, b, t) = \frac{\sin((1 - t)\,\Omega)}{\sin\Omega}\,a + \frac{\sin(t\,\Omega)}{\sin\Omega}\,b
$$

$a$ and $b$ are the unit quaternions, $t$ is the weight and $\Omega$ is the angle between them on the sphere, $\arccos(a \cdot b)$. At $t = 0$ the formula gives $a$ and at $t = 1$ it gives $b$. Slerp needs sines and cosines for each blend. **Nlerp**, normalized linear interpolation, is the cheaper form: it walks the straight chord between the two points, a weighted average of the four numbers, and divides by the length to return to the sphere.

::figure{id=slerp-arc}

Nlerp stays on the same path but not at an even speed: it moves a little slower near the ends. Both agree exactly at $t = 0$, $t = 0.5$ and $t = 1$. Between, the gap grows with the angle: for a quarter turn the weight 0.25 gives 22.5 degrees by slerp and 21.6 degrees by nlerp; for 160 degrees it gives 40 degrees against 34.5. For small turns, such as one frame's, nlerp is as good as slerp and costs less.

The double cover shapes the blend too. Two arcs on the sphere join $a$ to the rotation $b$, because $-b$ is the same rotation. One arc is the short way and the other the long way. The dot product says which: a positive value means the short arc leads to $b$, and a negative one means it leads to $-b$. So change the sign of one quaternion when the dot product is negative.

Animation code calls this choice the quaternion hemisphere, as [Blending animations](../animation/blending.md) explains.

::figure{id=short-arc}

:::example[From 10 degrees to 350 degrees around Y]
The sketch blends the yaw 10 degrees with the yaw 350 degrees. The dot product of the quaternions is negative, because 350 degrees has the half angle 175 degrees and a negative w. The first block shows slerp against nlerp for a quarter turn.

```cpp sketch="basics-math-rotations-slerp.cpp"
// Blending two rotations: slerp, nlerp and the shorter arc.
#include <cstdio>
#include <glm/glm.hpp>
#include <glm/gtc/quaternion.hpp>

float Degrees(const glm::quat& q)
{
	return glm::degrees(glm::angle(q)); // the angle of the turn the quaternion makes
}

int main()
{
	const glm::quat start(1.0f, 0.0f, 0.0f, 0.0f); // the identity: w comes first
	const glm::quat end = glm::angleAxis(glm::radians(90.0f), glm::vec3(0.0f, 1.0f, 0.0f));
	std::printf("slerp, a quarter of the way: %.1f degrees\n", Degrees(glm::slerp(start, end, 0.25f)));
	std::printf("nlerp, a quarter of the way: %.1f degrees\n", Degrees(glm::normalize(start * 0.75f + end * 0.25f)));

	const glm::quat from = glm::angleAxis(glm::radians(10.0f), glm::vec3(0.0f, 1.0f, 0.0f));
	const glm::quat to = glm::angleAxis(glm::radians(350.0f), glm::vec3(0.0f, 1.0f, 0.0f));
	std::printf("dot of 10 and 350 degrees: %.3f\n", glm::dot(from, to));
	std::printf("slerp halfway: %.1f degrees\n", Degrees(glm::slerp(from, to, 0.5f)));
	std::printf("mix halfway: %.1f degrees\n", Degrees(glm::mix(from, to, 0.5f)));
	return 0;
}
```

```text output-of="basics-math-rotations-slerp.cpp"
slerp, a quarter of the way: 22.5 degrees
nlerp, a quarter of the way: 21.6 degrees
dot of 10 and 350 degrees: -0.985
slerp halfway: 0.0 degrees
mix halfway: 180.0 degrees
```

1. **Line 8:** `glm::angle` returns the turn of a quaternion in radians, and `glm::degrees` converts it.
2. **Line 16:** nlerp by hand: the weighted sum of the four numbers, then `glm::normalize`.
3. **Lines 21–22:** `glm::slerp` changes the sign of one quaternion when the dot product is negative and goes the short way, so halfway is no turn at all; `glm::mix` does not and halfway is 180 degrees.

:::

Try it: the yaws 100 and 260 degrees have the dot product cos 80° = 0.174. Which way does `glm::slerp` go, and where is the middle?

:::answer
The dot product is positive, so slerp keeps both and takes the arc of 160 degrees; halfway is at 100 + 80 = 180 degrees.
:::

## Each form is good at one job

The four forms convert into each other. The table says what each is good for and which `glm` call converts it.

| Form | Numbers | Good for | Poor at | Conversions in `glm` |
| --- | --- | --- | --- | --- |
| Euler angles | 3 angles | Typing and reading, the Inspector's fields, a camera's yaw and pitch | Lock, blends, a read-back that changes the angles | `glm::quat(euler)` builds a quaternion, `glm::eulerAngles(q)` reads back |
| Axis and angle | A unit axis and an angle | Making one turn, such as a spin, and measuring how large a turn is | Combining and blending | `glm::angleAxis(angle, axis)`, and `glm::angle(q)` reads the angle |
| Matrix | 9 numbers | Turning many points, joining with scale and translation, sending to the :term[graphics processing unit]{id=gpu} (GPU) | Blending; rounding error makes the columns drift apart | `glm::mat3_cast(q)`, and `glm::quat_cast(matrix)` |
| Quaternion | 4 numbers | Storing, combining, blending and comparing | Reading by eye; two signs for one rotation | |

:::why[Why Strata stores a quaternion]
`TransformComponent::Rotation` in `Strata/src/Strata/Scene/Components.h` is a `glm::quat`. Four numbers are the fewest that combine by one product, blend without a lock and stay unit length with a division. The price is that a person cannot read four numbers at a glance: the Inspector converts to degrees every time it draws, and it keeps the typed angles so that its fields do not jump. Code that compares rotations must handle the two signs.
:::

## An angular velocity is an axis with a rate

A spinning body needs a speed of turning, and a speed of turning needs an axis. The **angular velocity** is one vector for both: its direction is the axis, by the right-hand rule, and its length is the rate in radians per second. `RigidBody::GetAngularVelocity` in a script returns it as radians per second around each world axis, and zero when the entity has no body.

$$
\Delta\theta = |\omega|\,\Delta t, \qquad q_{\text{step}} = \mathrm{angleAxis}\!\left(\Delta\theta,\; \frac{\omega}{|\omega|}\right)
$$

$\omega$ is the angular velocity, in radians per second, and $|\omega|$ its length, the rate. $\Delta t$ is the time of the step in seconds and $\Delta\theta$ the angle the body turns in it, in radians. $q_{\text{step}}$ is the quaternion of that small turn. The new rotation is the step times the old one: $q_{\text{step}}\,q$, the same left-hand product as the `Spinner`, because the axes are the world's. When $|\omega|$ is 0 there is no axis, so skip the step.

:::example[Two radians per second for 16 ms]
The angular velocity (0, 2, 0) turns around Y at 2 radians per second, 114.6 degrees per second. A frame of 0.016 s turns 2 × 0.016 = 0.032 radians, 1.83 degrees. After three frames the rotation is 5.5 degrees about Y.
:::

Try it: the angular velocity is (3, 4, 0) and the step is 0.01 s. Name the rate and the angle.

:::answer
The rate is the length, √(9 + 16) = 5 radians per second, so the angle is 5 × 0.01 = 0.05 radians, about 2.9 degrees, around the axis (0.6, 0.8, 0).
:::

## Common mistakes

- **Degrees where radians go.** Symptom: `glm::angleAxis(90.0f, ...)` turns 116.6 degrees, because 90 radians is more than fourteen turns. Fix: convert with `glm::radians`; only the Inspector speaks degrees.
- **The wrong order of a product.** Symptom: a spinning coin turns around its own tilted axis, not around the vertical. Fix: `turn * rotation` for the parent's axes, `rotation * turn` for the entity's own.
- **A blend that is not normalized.** Symptom: none in the entity, because Strata normalizes the rotation a script sets; the error appears in your own math, such as `q * v` stretching a direction. Fix: `glm::normalize` after each blend. A zero quaternion is refused with "the rotation must be a finite, non-zero quaternion".
- **A blend between q and -q.** Symptom: the arrow turns the long way round, up to 340 degrees. Fix: change the sign of one quaternion when the dot product is negative, or call `glm::slerp`, which does it for you; `glm::mix` does not.
- **Quaternions compared number by number.** Symptom: two equal rotations count as different. Fix: compare the absolute value of the dot product with 1.
- **Angles read back, changed and written again.** Symptom: a turn that stalls at a yaw of 90 degrees or runs backward. Fix: keep the yaw and the pitch in fields and build the rotation from them.

## Summary

- Yaw, pitch and roll are three turns, around Y, X and Z in Strata. Strata applies them in the order pitch, yaw, roll around fixed axes; Euler angles lock when the middle one reaches 90 degrees, read back only in part of their range, and blend badly.
- An axis and an angle name any rotation. A quaternion stores them as w = cos(θ / 2) and (x, y, z) = axis × sin(θ / 2), with length 1 and the identity (1, 0, 0, 0).
- `a * b` applies `b` first; `turn * rotation` turns around the parent's axes and `rotation * turn` around the entity's own. `q * v` rotates a direction and the conjugate undoes a turn.
- q and -q are one rotation, so compare with the absolute value of the dot product. Slerp blends along the arc at an even speed, nlerp along the chord and then normalized; change the sign of one quaternion when the dot product is negative to take the shorter arc.
- An angular velocity is an axis with a rate in radians per second; one small step is `glm::angleAxis(rate * deltaTime, axis)` multiplied on the left.

## Check yourself

1. A script reads `GetEulerAngles` of an entity at a yaw of 120 degrees. Which triple of degrees does it get? (a) (0, 120, 0) (b) (180, 60, 180) (c) (0, 60, 0) (d) (0, -120, 0)

   :::answer{tests="euler-order"}
   (b). The yaw reads back through an inverse sine, so only -90 to 90 degrees is possible; the same rotation has the pitch 180, the yaw 60 and the roll 180. (a) is what the script wrote, (c) halves the yaw and (d) turns the other way.
   :::

2. Which quaternion (w, x, y, z) is a turn of 90 degrees around Z? (a) (1, 0, 0, 1) (b) (0.7071, 0, 0, 0.7071) (c) (0, 0, 0, 1) (d) (0.7071, 0, 0.7071, 0)

   :::answer{tests="axis-angle"}
   (b): half the angle is 45 degrees, and the axis (0, 0, 1) is multiplied by the sine. (a) does not have length 1, (c) is a half turn and (d) turns around Y.
   :::

3. An object lies tilted by `rotation`. Which line spins it around the world's vertical axis? (a) `rotation = turn * rotation;` (b) `rotation = rotation * turn;` (c) `rotation = turn + rotation;`

   :::answer{tests="combine"}
   (a): the left factor acts last around the fixed axes. (b) spins around the object's own axis; (c) adds the numbers of two quaternions and gives no rotation at all.
   :::

4. Two unit quaternions have the dot product -1. What are they? (a) opposite rotations (b) the same rotation (c) a half turn apart (d) not unit length

   :::answer{tests="combine"}
   (b). A dot product of -1 means q and -q, which turn every direction the same way. A half turn apart would give a dot product of 0.
   :::

5. Which is true of nlerp against slerp for a turn of 160 degrees at the weight 0.25? (a) nlerp gives more of the turn (b) nlerp gives less of the turn (c) they are equal

   :::answer{tests="slerp"}
   (b). Slerp gives 40 degrees, nlerp 34.5 degrees: nlerp moves slower near the ends and agrees with slerp only at 0, 0.5 and 1.
   :::

6. An angular velocity of (0, 0, 0) reaches the formula for the step. What do you do?

   :::answer{tests="angular-velocity"}
   Skip the step. The axis ω / |ω| divides by 0 and has no direction; a body that does not turn needs no step.
   :::

## Practice

1. **Basic.** A camera has the yaw 180 degrees and the pitch -30 degrees. Compute its forward direction and say which way it looks.

   :::answer[Worked solution]{tests="euler-order"}
   x is -cos(-30°) × sin 180° = 0, y is sin(-30°) = -0.5 and z is -cos(-30°) × cos 180° = 0.866: (0, -0.5, 0.866). The camera faces backward along +Z and downward.
   :::

2. **Basic.** Write the quaternion of 60 degrees around Z and the first column of its rotation matrix.

   :::answer[Worked solution]{tests="axis-angle"}
   The quaternion is (cos 30°, 0, 0, sin 30°) = (0.866, 0, 0, 0.5). The first column is where X goes: (cos 60°, sin 60°, 0) = (0.5, 0.866, 0).
   :::

3. **Medium.** An object has `rotation` = a quarter turn around X. Where does its own up axis (0, 1, 0) end after `turn * rotation` and after `rotation * turn`, with `turn` a quarter turn around Y?

   :::answer[Worked solution]{tests="combine"}
   The rotation lifts up to (0, 0, 1). `turn * rotation` then turns that around Y, to (1, 0, 0). `rotation * turn` turns around Y first, which leaves (0, 1, 0), and then lifts it to (0, 0, 1): the turn around the object's own axis does not move it.
   :::

4. **Medium.** Compute the quaternion of 120 degrees around (1, 1, 1), check its length, and say where the X axis goes.

   :::answer[Worked solution]{tests="axis-angle"}
   The unit axis is (1, 1, 1) / √3, the half angle is 60 degrees, so each of x, y and z is 0.866 / 1.732 = 0.5 and w = cos 60° = 0.5. The length is √(4 × 0.25) = 1. The turn cycles the axes, X to Y: (0, 1, 0).
   :::

5. **Medium.** An arrow faces the yaw 100 degrees and must face the yaw 270 degrees. Compute the dot product of the two quaternions, say whether to change the sign of one, and give the yaw halfway by the shorter arc.

   :::answer[Worked solution]{tests="slerp"}
   The half angles are 50 and 135 degrees. The dot product is cos 50° cos 135° + sin 50° sin 135° = cos 85° = 0.087. It is positive, so neither quaternion changes sign, and the shorter arc is 170 degrees long. Halfway is at 100 + 85 = 185 degrees.
   :::

6. **Hard.** In a program of your own, write `Spin`, which takes a rotation, an angular velocity and a time and returns the rotation after that time. Run it for 60 steps of 1/60 s with the angular velocity (0, π, 0) and print the angle.

   :::answer[Worked solution]{tests="angular-velocity" solution="sketches/basics-math-rotations-spin.cpp"}
   The length of the angular velocity is the rate and the vector divided by it is the axis.

   ```cpp sketch="basics-math-rotations-spin.cpp"
   // An angular velocity turns a rotation in small steps: an axis, a rate and a time.
   #include <cstdio>
   #include <glm/glm.hpp>
   #include <glm/gtc/constants.hpp>
   #include <glm/gtc/quaternion.hpp>

   glm::quat Spin(const glm::quat& rotation, const glm::vec3& angularVelocity, float deltaTime)
   {
   	const float rate = glm::length(angularVelocity); // radians per second
   	if (rate < 1e-6f)
   		return rotation; // no axis to turn around
   	const glm::quat step = glm::angleAxis(rate * deltaTime, angularVelocity / rate);
   	return glm::normalize(step * rotation); // a turn around world axes goes on the left
   }

   int main()
   {
   	glm::quat rotation(1.0f, 0.0f, 0.0f, 0.0f);
   	const glm::vec3 angularVelocity(0.0f, glm::pi<float>(), 0.0f); // half a turn per second around Y
   	for (int frame = 0; frame < 60; frame++)
   		rotation = Spin(rotation, angularVelocity, 1.0f / 60.0f);
   	std::printf("after 1 s: %.1f degrees\n", glm::degrees(glm::angle(rotation)));
   	return 0;
   }
   ```

   ```text output-of="basics-math-rotations-spin.cpp"
   after 1 s: 180.0 degrees
   ```

   1. **Lines 9–11:** the rate is the length; a zero vector has no axis, so the rotation stays.
   2. **Line 12:** the step is the turn of one frame around the unit axis.
   3. **Line 13:** the step stands on the left, around the world's axes, and `glm::normalize` removes the rounding error.
   :::

7. **Hard.** Optional, on Coin Run: your project from [Coin Run](../make/project-coin-run.md), or Checkpoint 4 at the end of [Ship the finished game](../make/project-coin-run.md#ship-the-finished-game), opened with **File ▸ Open Project...**. Make the coins spin around a tilted axis with `glm::angleAxis`. Add an arrow above the ball that turns smoothly toward the nearest coin: blend with `glm::slerp` toward `Motion::LookAt`'s rotation.

   :::answer[Worked solution]{tests="axis-angle slerp"}
   In the coin's script, replace the axis (0, 1, 0) of the `Spinner` by a tilted axis of length 1.

   ```cpp pseudocode
   const glm::vec3 axis = glm::normalize(glm::vec3(0.3f, 1.0f, 0.0f));
   const glm::quat turn = glm::angleAxis(glm::radians(DegreesPerSecond * deltaTime), axis);
   transform.SetRotation(turn * transform.GetRotation());
   ```

   The arrow's script first finds the position `target` of the nearest coin, by comparing the distances from the arrow to each coin with `glm::length`, as [Vectors](../basics/math-vectors.md) taught. Then it blends from its rotation toward the wanted one by a part of the way each frame.

   ```cpp pseudocode
   const glm::quat wanted = Motion::LookAt(transform.GetWorldPosition(), target);
   const glm::quat current = transform.GetWorldRotation();
   const float weight = glm::min(1.0f, TurnSpeed * deltaTime);
   transform.SetWorldRotation(glm::slerp(current, wanted, weight));
   ```

   `Motion::LookAt` returns the rotation that turns the forward direction, -Z, toward the target. A weight of `TurnSpeed * deltaTime` moves a part of the remaining turn each frame, so the arrow eases in; `glm::slerp` takes the shorter arc itself.
   :::

## Where the book uses it

- [Interpolation](../world/interpolation.md) blends the last two poses of fixed-step motion, with nlerp and slerp for the rotations.
- [Blending animations](../animation/blending.md) mixes the rotations of many bones, and relies on the shorter arc and on normalizing.
- [Dynamics](../physics/dynamics.md) turns a body by its angular velocity, one small step at a time.
- [Inspectors](../editor-ui/inspectors.md) shows a rotation as Euler angles and keeps the typed ones, because of the read-back range.

## Further reading

- [The glm manual](https://github.com/g-truc/glm/blob/master/manual.md): the quaternion types and functions this page calls; intermediate.
- [3Blue1Brown, "Essence of linear algebra"](https://www.3blue1brown.com/topics/linear-algebra): the pictures of matrices that the axis-angle matrix builds on; beginner.
- Grant Sanderson and Ben Eater, "Visualizing quaternions", an interactive explorable at eater.net/quaternions: the four numbers and the half angle as moving pictures; intermediate.
