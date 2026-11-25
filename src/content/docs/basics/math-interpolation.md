---
id: basics/math-interpolation
title: "Blending and smoothing: lerp, easing, curves and exponential smoothing"
description: "Blend two values, ease a motion, read curves through keys, and smooth a value toward a target at any frame rate."
kind: primer
size: L
tracks: [B, E]
needs: [basics/math-change, basics/numbers]
time: 90
learn:
  - id: lerp-remap
    text: compute a lerp, an inverse lerp and a remapping, with the weight clamped
  - id: easing-curves
    text: choose an easing function for a motion and compute smoothstep by hand
  - id: keys-grids
    text: compute a value between keys by step, linear and Hermite interpolation, and between four corners by bilinear interpolation
  - id: exp-decay
    text: compute an exponential decay, its half-life, its time constant and its total over a distance
  - id: smoothing
    text: explain why a fixed fraction per frame depends on the frame rate, write the weight that does not, and compute the frames a smoothed value needs to settle
status: final
---

::::test-out

1. The ball stands at (0, 1, 0) and a coin at (4, 1, 8). Compute the point 25 % of the way from the ball to the coin.

   :::answer{tests="lerp-remap"}
   Blend each coordinate: 0 + 4 × 0.25 = 1, 1 + 0 × 0.25 = 1 and 0 + 8 × 0.25 = 2. The point is (1, 1, 2), which `glm::mix(ball, coin, 0.25f)` returns.
   :::

2. By hand, compute smoothstep for the weight 0.25 with the formula 3t² − 2t³. Is the result above or below 0.25, and what does that say about the start of the motion?

   :::answer{tests="easing-curves"}
   3 × 0.0625 − 2 × 0.015625 = 0.1875 − 0.03125 = 0.15625. The result is below 0.25, so the motion starts more slowly than a straight lerp.
   :::

3. A square has the corner values 0 (bottom left), 8 (bottom right), 4 (top left) and 12 (top right). Compute the bilinear value halfway across and a quarter of the way up.

   :::answer{tests="keys-grids"}
   Halfway across the bottom edge is 4, and across the top edge 8. A quarter of the way up from 4 to 8 is 4 + (8 − 4) × 0.25 = 5.
   :::

4. A value follows $v = 100 \, e^{-2t}$ with $t$ in seconds. Compute it at t = 0.5 s, and the time constant.

   :::answer{tests="exp-decay"}
   At 0.5 s the exponent is -1, so v = 100 × 0.368 = 36.8. The time constant is 1 / 2 = 0.5 s: the time the value needs to fall to 36.8 % of its start.
   :::

5. A camera closes 20 % of the gap to the ball in every frame and feels right at 30 frames per second. What happens at 120 frames per second, and which weight fixes it for a rate of 4 per second?

   :::answer{tests="smoothing"}
   The game runs four times as many frames each second, so the camera closes the gap much sooner and feels sharper. The weight `1.0f - std::exp(-4.0f * deltaTime)` gives the same result at every frame rate.
   :::

::::

## Why you will need this

A game seldom jumps from one value to another. A door swings open, a coin rises when you collect it, a camera trails the ball and a sound fades with distance. Each is a value that moves between two others, and your work is to choose the path it takes.

[Drawing between fixed steps](../world/interpolation.md) draws a body between two physics steps with a blend from this page. [Clips](../animation/clips.md) store an animation as values at chosen times and read between them. [Temporal anti-aliasing](../image/taa.md) mixes each new image with the old one. [Height fog](../light/fog.md) dims light with an exponential.

Each idea goes from numbers by hand to the formula and then to C++.

:::question[Why do the programs start with lines I have not seen?]
Each program starts with `#include` lines that bring in the library `glm`, and a call such as `glm::mix(...)` runs one of its functions. [Programming 3](../basics/programming-3.md) explains both; read them as "use the library" and "call its function".
:::

Only the optional Coin Run exercise needs a project. Each sketch is a whole program: save it as `sketch.cpp` and compile it in the terminal of [How a C++ program is built](build.md#open-a-terminal-that-finds-a-compiler), with C++20 and the `glm` headers of your Strata folder. On Windows, run `cl /std:c++20 /EHsc /I "<Strata folder>\StrataScriptCore\ThirdParty\glm" sketch.cpp` and then `.\sketch.exe`. On Linux and macOS, run `c++ -std=c++20 -I "<Strata folder>/StrataScriptCore/ThirdParty/glm" sketch.cpp -o sketch` and then `./sketch`. Without a compiler, read each output and its notes.

## A lerp walks a fraction of the way from one value to another

A coin hangs 10 units above the floor and must rise to 30. Halfway through the rise it should be at 20, and a quarter of the way through at 15. Each answer is the start plus a share of the distance.

**Linear interpolation**, short lerp, finds the value a chosen fraction of the way from a start $a$ to an end $b$:

$$\operatorname{lerp}(a, b, t) = a + (b - a) \, t$$

Here $a$ is the start value and $b$ the end value, in the same unit. The weight $t$ is a number from 0 to 1 without a unit. Read the formula as: start at $a$, then add $t$ times the gap $b - a$.

Check the limits. At $t = 0$ the second term vanishes and the result is $a$. At $t = 1$ the result is $a + (b - a) = b$. For 10 to 30, the weight 0.25 gives 10 + 20 × 0.25 = 15 and the weight 0.5 gives 20.

The same number is a weighted average of the two ends, with the weights $1 - t$ and $t$. Expand $(1 - t) \, a + t \, b$ and you get $a + t \, (b - a)$ again. Because the two weights add up to 1, the result never leaves the range between $a$ and $b$, as long as $t$ stays between 0 and 1.

A position is a list of numbers, so a lerp of two positions blends each coordinate with the same weight. The point moves along the straight line between them. A color is three numbers too, for red, green and blue, and blends the same way. The C++ library `glm` does all coordinates in one call, `glm::mix(a, b, t)`, and C++20 adds a lerp function for single numbers to its standard library. Whether a blend of two colors looks right depends on the space their numbers live in, which [Color](../basics/color.md) explains.

::figure{id=lerp-line}

:::example[A coin's path, blended by hand and by glm]
The program writes the formula as a function, runs it for three weights, checks the weighted average, and blends a position and a color. Look at the weight 1.5, which lies beyond the end.

```cpp sketch="basics-math-interpolation-lerp.cpp"
// Linear interpolation of a number, a position and a color, by hand and with glm::mix.
#include <cstdio>
#include <glm/glm.hpp>

float Lerp(float a, float b, float t)
{
	return a + (b - a) * t;
}

int main()
{
	std::printf("10 to 30 at t = 0.25: %g\n", Lerp(10.0f, 30.0f, 0.25f));
	std::printf("t = 0: %g, t = 1: %g, t = 1.5: %g\n", Lerp(10.0f, 30.0f, 0.0f), Lerp(10.0f, 30.0f, 1.0f), Lerp(10.0f, 30.0f, 1.5f));
	std::printf("weighted average: %g\n", 0.75f * 10.0f + 0.25f * 30.0f);
	const glm::vec3 start(0.0f, 1.0f, 0.0f);
	const glm::vec3 coin(4.0f, 1.0f, 8.0f);
	const glm::vec3 point = glm::mix(start, coin, 0.25f); // one call blends all three coordinates
	std::printf("a quarter of the way: (%g, %g, %g)\n", point.x, point.y, point.z);
	const glm::vec3 red(1.0f, 0.0f, 0.0f);
	const glm::vec3 blue(0.0f, 0.0f, 1.0f);
	const glm::vec3 purple = glm::mix(red, blue, 0.5f);
	std::printf("half red, half blue: (%g, %g, %g)\n", purple.x, purple.y, purple.z);
	return 0;
}
```

```text output-of="basics-math-interpolation-lerp.cpp"
10 to 30 at t = 0.25: 15
t = 0: 10, t = 1: 30, t = 1.5: 40
weighted average: 15
a quarter of the way: (1, 1, 2)
half red, half blue: (0.5, 0, 0.5)
```

1. **Line 7:** the formula, written as in the text.
2. **Line 13:** a weight of 1.5 gives 40, past the end at 30: outside 0 to 1, the line continues in both directions.
3. **Line 14:** the weighted average with the weights 0.75 and 0.25 equals the lerp.
4. **Line 17:** one `glm::mix` blends all three coordinates with one weight.

:::

Try it: a door turns from 0 to 90 degrees. Compute its angle at the weight 0.4.

:::answer
0 + (90 − 0) × 0.4 = 36 degrees.
:::

## Inverse lerp finds the weight, and remapping moves it to another range

Often you hold the value and need the weight. A health bar shows health from 10 to 30, and the health is 25. How far along is it?

**Inverse linear interpolation**, short inverse lerp, answers: which weight $t$ puts the value $v$ between $a$ and $b$? Solve $v = a + (b - a) \, t$ for $t$:

$$t = \frac{v - a}{b - a}$$

Here $v$ is the value, and $a$ and $b$ are the ends, all in one unit. The fraction reads as "how much of the gap has the value covered". For health 25 in the range 10 to 30 it is (25 − 10) / (30 − 10) = 0.75. When $a$ equals $b$ the gap is zero and the division fails, so code that takes the ends from data checks for it.

**Remapping** moves a value from one range to another: an inverse lerp in the old range gives the weight, and a lerp in the new range uses it. The health 25 from the range 10 to 30 onto a bar of 0 to 200 pixels has the weight 0.75, so the bar is 0 + 200 × 0.75 = 150 pixels wide.

A value outside its range gives a weight outside 0 to 1. Health 35 gives (35 − 10) / 20 = 1.25, and a bar 250 pixels wide. To clamp is to limit a number to a lowest and a highest value, so `glm::clamp(t, 0.0f, 1.0f)` returns 0 for any smaller weight and 1 for any larger one. Clamp the weight when the ends are real limits, and skip it only when going past them is what you want.

:::example[A health bar from a health value]
The program defines an inverse lerp and a remap, and prints the weight of 25, the width in pixels, and the weight of 35 before and after the clamp.

```cpp sketch="basics-math-interpolation-remap.cpp"
// Inverse lerp, remapping and clamping.
#include <cstdio>
#include <glm/glm.hpp>

float InverseLerp(float a, float b, float value)
{
	return (value - a) / (b - a);
}

float Remap(float value, float inA, float inB, float outA, float outB)
{
	return glm::mix(outA, outB, InverseLerp(inA, inB, value));
}

int main()
{
	std::printf("weight of 25 in 10 to 30: %g\n", InverseLerp(10.0f, 30.0f, 25.0f));
	std::printf("25 from 10..30 to 0..200: %g\n", Remap(25.0f, 10.0f, 30.0f, 0.0f, 200.0f));
	const float weight = InverseLerp(10.0f, 30.0f, 35.0f);
	std::printf("weight of 35: %g, clamped: %g\n", weight, glm::clamp(weight, 0.0f, 1.0f));
	return 0;
}
```

```text output-of="basics-math-interpolation-remap.cpp"
weight of 25 in 10 to 30: 0.75
25 from 10..30 to 0..200: 150
weight of 35: 1.25, clamped: 1
```

1. **Line 7:** the inverse lerp is the division from the formula above.
2. **Line 12:** a remap is an inverse lerp in the old range, then a `glm::mix` in the new one.
3. **Lines 19–20:** the weight 1.25 before the clamp would draw a bar wider than its frame; the clamp holds it at 1.

:::

Try it: loudness is 1 at a distance of 5 m and 0 at 25 m. Remap the distance 15 m to a loudness.

:::answer
The weight is (15 − 5) / (25 − 5) = 0.5, so the loudness is 1 + (0 − 1) × 0.5 = 0.5.
:::

## Angles wrap around, so blend the shortest difference

A lerp assumes that the number line runs straight. An angle does not: 350 degrees and 10 degrees are 20 degrees apart, but a lerp from 350 to 10 walks 340 degrees the long way round, through 180. The yaw of a camera or a character, its turn to the left or right, would spin almost a full turn instead of nudging.

The fix is to blend the difference, taken the short way. `std::remainder(target - angle, 360.0f)` returns that difference as a number from -180 to 180: for 10 − 350 = -340 it returns 20. Add part of it to the angle, or limit it to the most the object may turn in this frame. The player in `Samples/ThirdPerson/Scripts/ThirdPersonPlayer.cpp` turns toward its walking direction with these lines.

```cpp pseudocode
const float difference = std::remainder(target - yaw, 360.0f); // the short way, -180 to 180
const float maxTurn = TurnSpeed * deltaTime;                   // degrees allowed in this frame
yaw += std::clamp(difference, -maxTurn, maxTurn);
```

The first line finds the short way and its sign. The second turns a speed in degrees per second into a limit for one frame. The third moves the yaw by the difference, never by more than the limit. Rotations stored as quaternions blend with other functions, which [Rotations and quaternions](../basics/math-rotations.md) explains.

## An easing function bends the weight so a motion starts or ends slowly

A lerp moves at one constant speed. It starts at full speed and stops dead, as a robot does, and a door, a menu or a falling crate rarely moves like that. Speed is the slope of the graph of position over time, as [Change over time](../basics/math-change.md) shows: a constant speed is a straight line.

An **easing function** takes a weight from 0 to 1 and returns another weight from 0 to 1 with a different pace. You pass the new weight to the lerp. Three easing functions cover most uses:

| Function | Formula | Speed at the start | Speed at the end |
| --- | --- | --- | --- |
| Ease in | $t^2$ | zero | fast |
| Ease out | $1 - (1 - t)^2$ | fast | zero |
| Smoothstep | $3t^2 - 2t^3$ | zero | zero |

The third has a name of its own. **Smoothstep** is the easing function $3t^2 - 2t^3$: its graph leaves 0 flat and arrives at 1 flat. Its speed is $6t - 6t^2$, which is zero at both ends and 1.5 at the middle. In `glm`, `glm::smoothstep(a, b, x)` takes the ends and the value and does the inverse lerp for you.

::figure{id=easing-curves}

:::example[A door that opens in 2 seconds]
A door turns from 0 to 90 degrees, and the weight is the time divided by 2 s. At 0.5 s the weight is 0.25. A straight lerp gives 22.5 degrees. Ease in gives 0.0625 × 90 = 5.6, ease out gives 0.4375 × 90 = 39.4, and smoothstep gives 0.15625 × 90 = 14.1.
:::

Try it: compute smoothstep at the weight 0.75, and compare it with 1 minus smoothstep at 0.25.

:::answer
3 × 0.5625 − 2 × 0.421875 = 1.6875 − 0.84375 = 0.84375. The other value is 1 − 0.15625 = 0.84375: the two values mirror each other around the middle.
:::

Choose by what the motion does at its ends. Ease in suits a body that leaves rest and gathers speed, such as a falling crate. Ease out suits one that arrives and settles, such as a menu that slides in. Smoothstep suits a move from one resting place to another, such as a door or a fade between two states. Keep the straight lerp for what really moves at a constant speed, such as the second hand of a clock.

## Keyframes give a value at chosen times

Some motions have stages: a platform rises for 2 s, waits for 1 s and sinks for 2 s. One lerp cannot describe it. A **keyframe**, or key, is a time and the value a property has at that time, and a list of keys sorted by time describes the whole motion.

Take four keys, written (time, height): (0 s, 0 m), (2 s, 4 m), (3 s, 4 m) and (5 s, 0 m). To read the height at 4 s, find the two keys around that time: the last key at or before it, 3 s, and the next, 5 s. The weight is an inverse lerp of the time: (4 − 3) / (5 − 3) = 0.5. The height is a lerp of the two key values with that weight: 4 + (0 − 4) × 0.5 = 2 m. A segment between two keys is a remapping from time to value.

What happens between two keys is a choice. Step interpolation holds the earlier key's value until the next key arrives, then jumps: it suits a switch, such as visible or hidden. Linear interpolation blends with a lerp, so the value moves at one speed in each segment and turns a corner at each key. Before the first key and after the last, the value stays at that key's value.

The code below finds the segment and blends. Look at the loop: it moves to the next segment while the next key's time has already passed.

```cpp pseudocode
// keys are sorted by time, and there are at least two
size_t i = 0;
while (i + 2 < keys.size() && keys[i + 1].Time <= time)
	i++;
const float s = glm::clamp((time - keys[i].Time) / (keys[i + 1].Time - keys[i].Time), 0.0f, 1.0f);
const float value = glm::mix(keys[i].Value, keys[i + 1].Value, s);
```

The loop stops at the last segment, and the clamp keeps a time outside the keys at the first or last value. With the four keys above and the time 2.5 s, the loop moves to segment 1 and stops, because the key at 3 s lies ahead. A long list of keys is searched with a binary search instead, as [Data structures](../basics/data-structures.md) describes.

Try it: with the same four keys, what height do step and linear interpolation give at 1 s?

:::answer
Step holds the key at 0 s, so the height is 0 m. Linear has the weight (1 − 0) / (2 − 0) = 0.5 and gives 2 m.
:::

## A Hermite curve takes its shape from the keys' values and slopes

Linear segments turn a corner at each key: the speed changes at once. A **cubic Hermite curve** removes the corner. Between two keys it is a smooth curve fixed by four numbers: the value $p_0$ and slope $m_0$ at the first key, and the value $p_1$ and slope $m_1$ at the second. The slope is the rate of change, in units of value per second, as in [Change over time](../basics/math-change.md). The curve leaves the first key at the slope $m_0$ and arrives at the second at $m_1$.

$$v(s) = h_{00}(s) \, p_0 + h_{10}(s) \, \Delta t \, m_0 + h_{01}(s) \, p_1 + h_{11}(s) \, \Delta t \, m_1$$

Here $s$ is the position in the segment, from 0 at the first key to 1 at the second, found by the inverse lerp of the time. $\Delta t$ is the time between the keys, in seconds. The four blend weights are $h_{00}$, $h_{10}$, $h_{01}$ and $h_{11}$, each a cubic formula in $s$:

- $h_{00} = 2s^3 - 3s^2 + 1$ is 1 at $s = 0$ and 0 at $s = 1$: it carries the first value.
- $h_{01} = 3s^2 - 2s^3$ is the reverse: it carries the second value.
- $h_{10} = s^3 - 2s^2 + s$ and $h_{11} = s^3 - s^2$ are 0 at both ends and carry the slopes.

The slope is multiplied by $\Delta t$ because $s$ runs from 0 to 1 over $\Delta t$ seconds. A slope in units per second must become units per unit of $s$. Forget the factor and the curve is wrong whenever the keys are not exactly 1 s apart.

:::example[Two keys with a slope of 1 at the start]
The first key is at 0 s with value 0 and slope 1 per second, and the second at 2 s with value 1 and slope 0. The program prints the value of each kind of interpolation at 1 s and at 1.5 s.

```cpp sketch="basics-math-interpolation-keys.cpp"
// One segment between two keys, read by step, linear and Hermite interpolation.
#include <cstdio>
#include <glm/glm.hpp>
struct Key
{
	float Time, Value;
	float Slope; // value change per second, read by Hermite only
};
float Hermite(const Key& a, const Key& b, float s) // s: 0 at key a, 1 at key b
{
	const float span = b.Time - a.Time;
	const float s2 = s * s, s3 = s2 * s;
	return (2 * s3 - 3 * s2 + 1) * a.Value + (s3 - 2 * s2 + s) * span * a.Slope + (3 * s2 - 2 * s3) * b.Value + (s3 - s2) * span * b.Slope;
}
int main()
{
	const Key a{0.0f, 0.0f, 1.0f};
	const Key b{2.0f, 1.0f, 0.0f};
	for (const float time : {1.0f, 1.5f})
	{
		const float s = (time - a.Time) / (b.Time - a.Time);
		std::printf("t = %g s: step %g, linear %g, Hermite %g\n", time, a.Value, glm::mix(a.Value, b.Value, s), Hermite(a, b, s));
	}
	return 0;
}
```

```text output-of="basics-math-interpolation-keys.cpp"
t = 1 s: step 0, linear 0.5, Hermite 0.75
t = 1.5 s: step 0, linear 0.75, Hermite 0.9375
```

1. **Line 9:** the function takes the position $s$ in the segment, not the time.
2. **Line 11:** the span of the segment scales both slopes.
3. **Line 13:** the four weights multiply the two values and the two scaled slopes.
4. **Line 22:** the same position feeds the linear blend and the Hermite curve; step holds the first value.

:::

At the middle, $s = 0.5$, the weights are 0.5, 0.125, 0.5 and -0.125. The Hermite value is 0.5 × 0 + 0.125 × 2 × 1 + 0.5 × 1 − 0.125 × 2 × 0 = 0.75, above the linear 0.5 because the start slope is steep.

::figure{id=keys-curves}

With both slopes zero and the values 0 and 1, the Hermite curve is $3s^2 - 2s^3$: smoothstep. A smoothstep is the Hermite curve between two resting keys.

A **Bezier curve** is the other common way to shape a segment. It uses four control points $P_0$ to $P_3$: the curve starts at $P_0$ and ends at $P_3$, and the two points between pull it toward them without lying on it.

$$B(s) = (1 - s)^3 P_0 + 3 (1 - s)^2 s \, P_1 + 3 (1 - s) s^2 P_2 + s^3 P_3$$

In this formula $s$ again runs from 0 to 1, $B$ is the point of the curve at $s$, and each $P$ is a value or a position. Control points 0, 0, 1 and 1 give $3s^2 - 2s^3$ once more. The pull of $P_1$ and $P_2$ thus plays the part of a slope: the first slope is three times the gap from $P_0$ to $P_1$, divided by $\Delta t$.

Try it: keys at 0 s (value 0, slope 0) and at 2 s (value 1, slope 0.5 per second). Compute the Hermite value at 1 s.

:::answer
At $s = 0.5$: 0.5 × 1 + (−0.125) × 2 × 0.5 = 0.5 − 0.125 = 0.375. The slope at the end is shallow, so the curve stays below the straight line, which gives 0.5.
:::

## Bilinear and trilinear interpolation blend the corners of a square and a cube

A grid stores a value at each corner: the height of a terrain, the brightness of a texture's pixel. A point between four corners needs a value too. **Bilinear interpolation** gets it with lerps in two directions: first along x on the bottom and top edges, then along y between the two results.

Take corner values 0 and 4 on the bottom edge, and 2 and 6 on the top edge. The point lies 0.25 of the way across and 0.5 of the way up. Along the bottom edge: 0 + 4 × 0.25 = 1. Along the top edge: 2 + 4 × 0.25 = 3. Between them at 0.5: 1 + (3 − 1) × 0.5 = 2.

The four corners carry the weights $(1-u)(1-v)$, $u(1-v)$, $(1-u)v$ and $uv$ for the weights $u$ across and $v$ up. They add up to 1, so the result is a weighted average of the corners. Each weight is the area of the rectangle opposite its corner.

::figure{id=bilinear-weights}

**Trilinear interpolation** adds one more direction for the eight corners of a cube: bilinear interpolation on the front and back squares, then a lerp between the two results along the depth. A :term[graphics processing unit]{id=gpu} (GPU) uses the bilinear form when a texture is read between pixels, and [Sampling, aliasing and filtering](../basics/signals.md) explains that. A table of colors laid out as a cube, as in [White balance, grading and lookup tables](../image/grading.md), is read with the trilinear form.

:::example[Four corners and then two squares]
The program computes the four weights at the point above, then the bilinear value on a front square and on a back square, and blends those with a depth weight of 0.5.

```cpp sketch="basics-math-interpolation-bilinear.cpp"
// Bilinear interpolation between four corners, and trilinear between two squares.
#include <cstdio>
#include <glm/glm.hpp>

float Bilinear(float c00, float c10, float c01, float c11, float u, float v)
{
	const float bottom = glm::mix(c00, c10, u); // along x on the bottom edge
	const float top = glm::mix(c01, c11, u);    // along x on the top edge
	return glm::mix(bottom, top, v);            // then along y between them
}

int main()
{
	const float u = 0.25f;
	const float v = 0.5f;
	std::printf("weights: %g %g %g %g\n", (1 - u) * (1 - v), u * (1 - v), (1 - u) * v, u * v);
	const float front = Bilinear(0.0f, 4.0f, 2.0f, 6.0f, u, v);
	const float back = Bilinear(10.0f, 14.0f, 12.0f, 16.0f, u, v);
	std::printf("bilinear %g and %g, trilinear at w = 0.5: %g\n", front, back, glm::mix(front, back, 0.5f));
	return 0;
}
```

```text output-of="basics-math-interpolation-bilinear.cpp"
weights: 0.375 0.125 0.375 0.125
bilinear 2 and 12, trilinear at w = 0.5: 7
```

1. **Lines 7–9:** two lerps along x, then one along y.
2. **Line 16:** the four weights add up to 1.
3. **Line 19:** the last `glm::mix` is the depth step that makes the blend trilinear.

:::

Try it: the corners of a square hold 10 and 20 on the bottom edge and 30 and 50 on the top edge. Compute the value at the middle.

:::answer
The bottom edge at 0.5 gives 15 and the top edge gives 40. Halfway between them is 27.5. The average of the four corners gives the same.
:::

## Exponential decay loses the same fraction in each equal step

A sound fades, light dims in fog, a camera closes on a ball. Each loses a share of what is left, not the same amount. **Exponential decay** is a quantity that loses the same fraction in each equal step of time or distance. Halve a value every second and you get 100, 50, 25, 12.5 and so on.

With the number $e$ of [Numbers in a computer](../basics/numbers.md), the value at time $t$ is

$$v(t) = v_0 \, e^{-kt}$$

where $v_0$ is the start, $k$ is the decay rate in 1/s (or 1/m for a distance) and $e^{-kt}$ reads "e to the power minus k times t". The factor $e^{-k}$ is the share kept in each second. A larger $k$ means a faster fall.

Two numbers describe the speed. The **time constant** $\tau$ is $1 / k$: after $\tau$ the value is $e^{-1}$ = 36.8 % of the start. After 3 $\tau$ about 5 % is left, and after 5 $\tau$ under 1 %.

The **half-life** is the time to lose half, $\ln 2 / k$, which is about 0.693 times $\tau$.

:::example[A decay with k = 2 per second]
With $v_0 = 100$ and $k = 2$ per second: $\tau = 0.5$ s and the half-life is 0.347 s. The value at 0.5 s is 100 × $e^{-1}$ = 36.8, at 1 s it is 100 × $e^{-2}$ = 13.5, and at 1.5 s it is 100 × $e^{-3}$ = 4.98.
:::

Try it: a light loses half of its brightness every 2 m of fog. Compute $k$.

:::answer
The half-life is 2 m, so $k = 0.693 / 2 = 0.347$ per metre.
:::

The same curve describes light in fog over a distance $d$. Light that crosses $d$ metres keeps the share $e^{-kd}$ of its brightness. Fog also adds light of its own: a thin layer at each distance sends a little light toward the eye, and that light has to cross the fog in front of it. The total of the added light is the area under the graph of $e^{-kx}$ from 0 to $d$, as accumulation in [Change over time](../basics/math-change.md) defined it:

$$A(d) = \frac{1 - e^{-kd}}{k}$$

Here $A$ is the total for a layer that adds one unit of light per metre, $d$ is the distance in metres and $k$ is the rate in 1/m. At $d = 0$ the total is 0. For a long distance $e^{-kd}$ vanishes and the total approaches $1 / k$: far fog stops adding light.

Check the formula with $k = 0.5$ per metre and $d = 4$ m. Then $e^{-2} = 0.135$ and $A = (1 - 0.135) / 0.5 = 1.73$.

To see that this is plausible, cut the distance into four slices. Four slices of 1 m, each as tall as the graph at its left edge, add 1 + 0.607 + 0.368 + 0.223 = 2.20, too much. Slices as tall as the graph at their right edge add 1.33, too little. The exact value lies between. [Height fog](../light/fog.md) draws fog in Strata.

## A fixed fraction per frame depends on the frame rate

A camera must follow a ball that moves. The shortest code moves the camera a fixed fraction of the remaining gap in each frame, for example `camera += (ball - camera) * 0.2f`. That is **exponential smoothing**: each frame is a lerp from the current value toward the target, so the gap shrinks by the same factor in every step, like the decay above.

By hand, with the target 1, start 0 and the fraction 0.2: the gap is 0.8 after one frame, 0.64 after two, 0.512 after three. After $n$ frames it is $0.8^n$. The smoothing looks natural, because a camera that is far away moves fast and one that is near slows.

The trouble is that the fraction counts frames, not seconds. At 30 frames per second, three frames last 0.1 s and the gap is 0.512. At 120 frames per second, 0.1 s is 12 frames, and the gap is $0.8^{12}$ = 0.069. In the same time the faster machine leaves a gap seven times smaller, so the camera feels sharp there and loose on a slow machine.

The property you want has a name. **Frame-rate independence** means that the result after a given time is the same at every frame rate. The program below tunes a fixed weight for 30 frames per second, then runs it at 120.

```cpp sketch="basics-math-interpolation-smoothing.cpp"
// Chasing a target for one second at 30 and at 120 frames per second, with two kinds of weight.
#include <cmath>
#include <cstdio>

float GapAfterOneSecond(int framesPerSecond, bool exponential)
{
	const float k = 2.0f; // per second
	const float deltaTime = 1.0f / framesPerSecond;
	float value = 0.0f; // the target is 1
	for (int frame = 0; frame < framesPerSecond; frame++)
	{
		const float weight = exponential ? 1.0f - std::exp(-k * deltaTime) : 0.0645f; // 0.0645 suits 30 frames per second
		value += (1.0f - value) * weight;
	}
	return 1.0f - value;
}

int main()
{
	std::printf("fixed fraction: gap %.4f at 30 fps, %.4f at 120 fps\n", GapAfterOneSecond(30, false), GapAfterOneSecond(120, false));
	std::printf("1 - exp(-k dt): gap %.4f at 30 fps, %.4f at 120 fps\n", GapAfterOneSecond(30, true), GapAfterOneSecond(120, true));
	return 0;
}
```

```text output-of="basics-math-interpolation-smoothing.cpp"
fixed fraction: gap 0.1353 at 30 fps, 0.0003 at 120 fps
1 - exp(-k dt): gap 0.1353 at 30 fps, 0.1353 at 120 fps
```

1. **Line 12:** the fixed weight 0.0645 is right at 30 frames per second only; the other branch is derived below.
2. **Line 13:** each frame closes a share `weight` of the remaining gap.

The first output line shows the problem: a gap of 0.1353 at 30 frames per second becomes 0.0003 at 120. The second line shows the cure, a gap of 0.1353 at both rates.

::figure{id=decay-stepped}

## An exponential weight gives the same result at every frame rate

The cure comes from asking what a frame must do. In the smooth world the gap follows the decay $e^{-kt}$, so after one frame of $\Delta t$ seconds it must be multiplied by $e^{-k \, \Delta t}$. A lerp with the weight $w$ multiplies the gap by $1 - w$. Equate the two and solve:

$$w = 1 - e^{-k \, \Delta t}$$

Here $w$ is the weight for one frame, $k$ is the rate in 1/s and $\Delta t$ is the frame's delta time in seconds. In terms of the time constant it reads $w = 1 - e^{-\Delta t / \tau}$. After $n$ frames the gap is $(e^{-k \, \Delta t})^n = e^{-k \, n \, \Delta t}$, and $n \, \Delta t$ is the time that has passed, so the frame rate has vanished from the result.

For $k = 2$ the weight is 1 − $e^{-2/30}$ = 0.0645 at 30 frames per second, the number the sketch tuned, and 1 − $e^{-2/120}$ = 0.0165 at 120. One second later, both leave the gap $e^{-2}$ = 0.1353.

The weight is also always between 0 and 1. The simpler `gap * k * deltaTime` is nearly equal for small frames, but a stall of 0.6 s with $k = 4$ makes $k \, \Delta t = 2.4$, and the camera flies past the ball. The exponential weight tends to 1 in a long frame and lands on the target.

The follow camera in `Samples/ThirdPerson/Scripts/FollowCamera.cpp` reads this way. Search for the weight in the last line of the quote.

```cpp src="Samples/ThirdPerson/Scripts/FollowCamera.cpp#L73-L79"
// Where the player is drawn this frame: between its last two physics steps while the game interpolates.
const glm::vec3 pivot = Target.GetTransform().GetDrawnPosition() + glm::vec3(0.0f, PivotHeight, 0.0f);
// A respawn or a teleport moves the camera at once; walking is followed smoothly.
if (glm::length(pivot - m_Pivot) > 8.0f)
	m_Pivot = pivot;
else
	m_Pivot = glm::mix(m_Pivot, pivot, 1.0f - std::exp(-FollowSharpness * deltaTime));
```

The weight on the last line is `1.0f - std::exp(-FollowSharpness * deltaTime)`, with `FollowSharpness` set to 14 per second in the same file. Its time constant is $\tau = 1/14$ = 71 ms, so the pivot closes 95 % of a gap in 3 $\tau$, about 0.21 s, at any frame rate.

A pivot more than 8 m from its target, after the player returns to the start for example, jumps at once. The target is the player's drawn position, read in `OnLateUpdate`. The player moves in fixed physics steps, and the game draws it between two of them, as [Drawing between fixed steps](../world/interpolation.md) explains. A camera that read the simulated position would follow the steps and move in jerks.

Exponential smoothing starts at full speed in the first frame after the target moves. The script software development kit (SDK) also has `Motion::SmoothDamp(current, target, velocity, smoothTime, deltaTime)` in `StrataScriptCore/Include/StrataScript/Gameplay.h`, a spring that keeps a `velocity` between calls. It pulls toward the target, is damped so that it never passes the target, and reaches the target in about `smoothTime` seconds. Because it keeps the velocity, its speed rises gradually, and a delta time of 0 or less changes nothing.

## A geometric series tells how many frames a smoothed value needs to settle

Each frame keeps the share $r = e^{-k \, \Delta t}$ of the gap, which is $1 - w$. A **geometric series** is a sum in which each term is the one before it times the same number $r$: $1 + r + r^2 + \dots$. The gap after $n$ frames is $r^n$, the term of the series after $n$ multiplications.

With $r = 0.8$ the gaps are 0.8, 0.64, 0.512, and after 10 frames 0.107. To ask when the gap falls below 1 %, solve $r^n \le 0.01$ with logarithms, which [Numbers in a computer](../basics/numbers.md) introduced:

$$n \ge \frac{\ln 0.01}{\ln r}$$

Here $\ln$ is the natural logarithm and $n$ counts frames. For $r = 0.8$ it is −4.605 / −0.2231 = 20.6, so 21 frames. In seconds the time is $n \, \Delta t = 4.605 / k$, which is 4.6 time constants whatever the frame rate. For the follow camera, $k = 14$ gives 0.33 s: 20 frames at 60 per second, 40 at 120.

The sum of the series has a closed form for $0 < r < 1$:

$$1 + r + r^2 + \dots = \frac{1}{1 - r}$$

Here the dots mean the terms continue without end. To see why, call the sum $S$: then $S = 1 + r \, S$, so $S \, (1 - r) = 1$. With $r = 0.5$ the sum is 2: 1 + 0.5 + 0.25 + 0.125 and so on approach 2.

The series answers a question about the camera. In frame $i$ it moves the share $w$ of what is left, $w \, r^i$ of the original gap. All the moves add up to $w / (1 - r) = w / w = 1$: the whole gap, never more.

## Common mistakes

- **A weight outside 0 to 1 without a clamp.** The symptom is a bar wider than its frame, or a door that swings past open. Clamp the weight, or choose an easing function that stays in range. Leave the weight free only when passing the end is the goal.
- **A fixed fraction per frame.** The symptom is a camera that feels sharper on a fast machine than on a slow one. Use `1 - exp(-k * deltaTime)` as the weight.
- **A Hermite slope not scaled by the time between keys.** The symptom is a curve that bulges or flattens when the keys are not 1 s apart. Multiply each slope by $\Delta t$ before the blend.
- **Angles lerped across 360 degrees.** The symptom is a yaw that spins the long way round from 350 to 10 degrees. Lerp the difference from `std::remainder`, or limit it to a turn rate.

## Summary

- A lerp, $a + (b - a) \, t$, is a weighted average; an inverse lerp finds a value's weight, a remapping moves it between ranges and a clamp limits it.
- An easing function bends the weight: ease in starts slowly, ease out ends slowly, and smoothstep, $3t^2 - 2t^3$, does both.
- Between keys, step holds a value, linear lerps it and a Hermite curve follows values and slopes; across a square or a cube, lerps along each direction in turn blend the corners.
- Exponential decay, $v_0 \, e^{-kt}$, loses the same fraction in each equal step: its time constant is $1 / k$, its half-life $\ln 2 / k$ and its total over a distance $(1 - e^{-kd}) / k$.
- A fixed fraction per frame depends on the frame rate; the weight $1 - e^{-k \, \Delta t}$ does not, and the geometric series $r^n$ gives the frames to settle.

## Check yourself

1. A camera smooths with $k = 6$ per second at 60 frames per second. Which weight does it use per frame?

   - (a) 0.1
   - (b) 0.0952
   - (c) 0.9048
   - (d) 6

   :::answer{tests="smoothing"}
   (b): the weight is $1 - e^{-6/60} = 1 - e^{-0.1} = 0.0952$. Choice (a) is $k \, \Delta t$, close for a short frame but not exact. Choice (c) is the share of the gap that stays, $e^{-0.1}$, and (d) ignores the frame's length.
   :::

2. Remap 7 from the range 0 to 10 onto the range 100 to 200, and do the same for 12, with the weight clamped.

   :::answer{tests="lerp-remap"}
   The weight of 7 is 0.7, so the value is 100 + 100 × 0.7 = 170. The weight of 12 is 1.2, clamped to 1, so the value is 200.
   :::

3. A menu panel slides in and must stop gently at its place. Which easing suits it?

   - (a) ease in
   - (b) ease out
   - (c) a straight lerp

   :::answer{tests="easing-curves"}
   (b): ease out has zero speed at the end, so the panel arrives and settles. Ease in does the opposite, it ends at full speed, and a straight lerp stops dead.
   :::

4. Keys at (0 s, 1), (4 s, 5) and (6 s, 3). Compute the step value and the linear value at 5 s.

   :::answer{tests="keys-grids"}
   The segment is the one from 4 s to 6 s. Step holds the earlier key, so the value is 5. Linear has the weight 0.5 and gives 5 + (3 − 5) × 0.5 = 4.
   :::

5. A sound loses half its loudness every 2 s. Compute $k$ and the time constant.

   :::answer{tests="exp-decay"}
   $k = 0.693 / 2 = 0.347$ per second, and $\tau = 1 / k = 2.88$ s.
   :::

## Practice

1. **Basic.** A sound is full at 5 m and silent at 25 m. By hand, remap a distance of 12 m and one of 30 m to a loudness from 1 down to 0, with clamping.

   :::answer[Worked solution]{tests="lerp-remap"}
   For 12 m the weight is (12 − 5) / 20 = 0.35, so the loudness is 1 − 0.35 = 0.65. For 30 m the weight is 1.25, which the clamp makes 1, so the loudness is 0.
   :::

2. **Basic.** A door turns from 0 to 90 degrees in 2 s with smoothstep. Compute the angle at 0.5 s and at 1.5 s.

   :::answer[Worked solution]{tests="easing-curves"}
   At 0.5 s the weight is 0.25 and smoothstep gives 0.15625, so the angle is 14.06 degrees. At 1.5 s the weight is 0.75 and smoothstep gives 0.84375, so the angle is 75.94 degrees. The two mirror each other: 14.06 + 75.94 = 90.
   :::

3. **Medium.** A yaw is 350 degrees and the target is 10. The turn speed is 90 degrees per second and the frame lasts 0.1 s. Compute the new yaw with the lines of the angle section.

   :::answer[Worked solution]{tests="lerp-remap"}
   The difference is `std::remainder(10 - 350, 360)` = 20. The limit is 90 × 0.1 = 9, so the clamp gives 9 and the yaw becomes 359. The camera turns the short way, through 0.
   :::

4. **Medium.** Show that a Bezier curve with the control values 0, 0, 1 and 1 gives smoothstep at $s = 0.25$.

   :::answer[Worked solution]{tests="easing-curves keys-grids"}
   The terms with 0 vanish, so $B = 3 (1 - s) s^2 + s^3$. At 0.25: 3 × 0.75 × 0.0625 + 0.015625 = 0.140625 + 0.015625 = 0.15625. Smoothstep at 0.25 is 0.15625, the same.
   :::

5. **Medium.** Fog has $k = 0.2$ per metre. Compute the share of light left after 10 m, the distance at which half is left, and the total $A(10)$.

   :::answer[Worked solution]{tests="exp-decay"}
   The share is $e^{-2}$ = 0.135. Half is left at $0.693 / 0.2$ = 3.47 m. The total is $(1 - 0.135) / 0.2$ = 4.32, below the limit of $1 / k$ = 5.
   :::

6. **Hard.** A camera smooths with $k = 14$ per second. Compute the frames to settle within 1 % at 30, 60 and 120 frames per second, and the time each takes.

   :::answer[Worked solution]{tests="smoothing"}
   The settle time is 4.605 / 14 = 0.329 s. At 30 frames per second that is 9.87, so 10 frames, at 60 it is 19.7 so 20 frames, and at 120 it is 39.4 so 40 frames. Each takes about 0.33 s: the time is the same and only the count of frames changes.
   :::

7. **Hard.** Optional, on your [Coin Run](../make/project-coin-run.md) or Checkpoint 4 of [Ship the finished game](../make/project-coin-run.md#ship-the-finished-game). Make a collected coin rise from 1 m to 2.5 m and shrink to nothing over 0.5 s, with its time turned into a weight from 0 to 1 and eased with smoothstep. Make the camera follow the ball with the weight `1 - exp(-k * deltaTime)`, and check it with a loop that runs one second at 30 and at 120 steps.

   :::answer[Worked solution]{tests="lerp-remap easing-curves smoothing" solution="sketches/basics-math-interpolation-coin.cpp"}
   The program holds both effects as plain functions and runs the check loop.

   ```cpp sketch="basics-math-interpolation-coin.cpp"
   // Coin Run's two effects as plain functions: the collected coin's pop and the follow camera's step.
   #include <cmath>
   #include <cstdio>
   #include <glm/glm.hpp>

   float PopHeight(float age) // the coin rises from 1 m to 2.5 m in half a second
   {
   	const float t = glm::clamp(age / 0.5f, 0.0f, 1.0f); // inverse lerp, clamped
   	return glm::mix(1.0f, 2.5f, glm::smoothstep(0.0f, 1.0f, t));
   }

   float FollowOneSecond(int steps)
   {
   	float camera = 0.0f;
   	for (int step = 0; step < steps; step++)
   		camera = glm::mix(camera, 10.0f, 1.0f - std::exp(-3.0f * (1.0f / steps))); // k = 3 per second
   	return camera;
   }

   int main()
   {
   	std::printf("height at 0, 0.25, 0.5 s: %g %g %g\n", PopHeight(0.0f), PopHeight(0.25f), PopHeight(0.5f));
   	std::printf("camera after 1 s: %.3f at 30 steps, %.3f at 120 steps\n", FollowOneSecond(30), FollowOneSecond(120));
   	return 0;
   }
   ```

   ```text output-of="basics-math-interpolation-coin.cpp"
   height at 0, 0.25, 0.5 s: 1 1.75 2.5
   camera after 1 s: 9.502 at 30 steps, 9.502 at 120 steps
   ```

   1. **Line 8:** the clamped inverse lerp turns the age into a weight.
   2. **Line 9:** smoothstep eases the weight, and a lerp makes the height.
   3. **Line 16:** the follow step, with the exponential weight.

   Both loops end at 9.502: the frame rate does not change the result. In the game, a `CoinPop` script on a coin keeps its age and sets the position and the scale from the two lerps.

   ```cpp pseudocode
   void OnUpdate(float deltaTime) override
   {
   	m_Age += deltaTime;
   	const float t = glm::clamp(m_Age / 0.5f, 0.0f, 1.0f);
   	const float eased = glm::smoothstep(0.0f, 1.0f, t);
   	TransformComponent transform = GetTransform();
   	transform.SetTranslation(glm::vec3(m_Start.x, glm::mix(1.0f, 2.5f, eased), m_Start.z));
   	transform.SetScale(glm::vec3(glm::mix(1.0f, 0.0f, eased)));
   }
   ```

   The camera script follows the ball in `OnLateUpdate`, not `OnUpdate`, and reads the ball's `GetDrawnPosition()`. The ball moves in fixed physics steps, and the game draws it between two of them ([Drawing between fixed steps](../world/interpolation.md)).

   ```cpp pseudocode
   void OnLateUpdate(float deltaTime) override
   {
   	const glm::vec3 goal = Target.GetTransform().GetDrawnPosition() + glm::vec3(0.0f, Height, Back);
   	TransformComponent transform = GetTransform();
   	transform.SetWorldPosition(glm::mix(transform.GetWorldPosition(), goal, 1.0f - std::exp(-Sharpness * deltaTime)));
   }
   ```

   The coin script keeps `m_Age` and `m_Start`, the position at creation, and your own code that collects the coin sets `m_Age` to 0. The camera script names `Target`, `Height`, `Back` and `Sharpness` with `ST_SCRIPT_FIELD`, as the camera of the sample does, and 4 is a first value for `Sharpness`.
   :::

## Where the book uses it

- [Drawing between fixed steps](../world/interpolation.md) draws a body between its last two physics poses with a lerp, whose weight is the share of the step that has passed.
- [Clips](../animation/clips.md) store an animation as keys and read values between them by step, linear and cubic interpolation.
- [Temporal anti-aliasing](../image/taa.md) mixes each new image with the history by a weight, as exponential smoothing does.
- [Sound in space](../audio/spatial.md) offers a linear fall of loudness between a near and a far distance, a remapping with a clamp, beside the default inverse fall.
- [Height fog](../light/fog.md) dims light by an exponential of the distance and adds the light of the fog itself.

## Further reading

- [cppreference, the lerp function](https://en.cppreference.com/w/cpp/numeric/lerp): the C++20 lerp for single numbers, with its guarantees at 0 and 1; intermediate.
- [cppreference, the remainder function](https://en.cppreference.com/w/cpp/numeric/math/remainder): the function that returns the short difference of two angles; intermediate.
- [Unity, Mathf.SmoothDamp](https://docs.unity3d.com/ScriptReference/Mathf.SmoothDamp.html): the same idea as the SDK's spring, in another engine's scripting API; intermediate.
- Freya Holmér, "Lerp smoothing is broken": a talk about the fixed fraction per frame and its cure; intermediate.
- Inigo Quilez, "Useful little functions": a catalogue of easing and shaping functions with graphs; advanced.
