---
id: basics/math-change
title: "Change over time: rates, accumulation, Euler steps and Newton's laws"
description: "How a game moves things: rates and accumulation from tables of numbers, the Euler step, the size of the step, and Newton's laws with impulses."
kind: primer
size: L
tracks: [B, E]
needs: [basics/math-vectors]
time: 90
learn:
  - id: rate-slope
    text: compute a rate of change from a table of positions and read it as the slope of a graph
  - id: accumulate
    text: compute a distance from a table of speeds with rectangles and explain the integral as an area
  - id: euler-steps
    text: compute explicit and semi-implicit Euler steps by hand and explain why the second keeps a spring's energy
  - id: step-size
    text: explain why a larger step brings more error, why it can make a simulation explode and why physics takes a fixed step
  - id: newton-impulse
    text: compute accelerations and velocity changes from force, mass and impulse, and choose AddForce or AddImpulse
status: final
---

::::test-out

1. A cart stands at 0 m, 2 m, 6 m and 12 m at the times 0 s, 1 s, 2 s and 3 s. Compute its speed in each of the three seconds.

   :::answer{tests="rate-slope"}
   Each speed is the change of position divided by the change of time: 2 m/s, 4 m/s and 6 m/s. The cart gets faster, so the graph of its position bends upward.
   :::

2. A ball moves at 3 m/s for 2 s, then at 5 m/s for 1 s. How far does it travel?

   :::answer{tests="accumulate"}
   The two rectangles under the speed graph are 3 × 2 = 6 m and 5 × 1 = 5 m, so the ball travels 11 m.
   :::

3. A ball at a height of 5 m moves at -2 m/s with an acceleration of -10 m/s². Compute its height and velocity after one step of 0.1 s with the explicit Euler method.

   :::answer{tests="euler-steps"}
   The position moves by the old velocity: 5 + (-2) × 0.1 = 4.8 m. The velocity changes next: -2 + (-10) × 0.1 = -3 m/s. The semi-implicit method would use the new velocity and give 5 - 0.3 = 4.7 m.
   :::

4. A simulation runs a spring with a step of 0.01 s and looks right. Another run uses a step of 3 s and the spring flies away. Why?

   :::answer{tests="step-size"}
   Each step trusts the force at its start for its whole length. When the step is long compared with the spring's swing, the errors grow from step to step instead of shrinking.
   :::

5. A 2 kg ball at rest gets an impulse of 6 newton seconds. What is its speed right after?

   :::answer{tests="newton-impulse"}
   The velocity changes by the impulse divided by the mass: 6 / 2 = 3 m/s. A force would need time to do the same.
   :::

::::

## Why you will need this

Every moving thing in a game follows one rule: the position changes by the speed times the time. A falling ball, a jumping character and a sliding crate all obey it. To write such code you need to know what a speed is, how a game adds it up, and what goes wrong when one step is long.

[Time](../core/time.md) uses these ideas to say why a game measures the time of every frame. [Rigid body dynamics](../physics/dynamics.md) uses them to explain how Strata's physics moves a body. [Sound in space](../audio/spatial.md) uses velocities for the Doppler effect, and [Earth's atmosphere and aerial perspective](../light/atmosphere.md) adds up small pieces along a path.

Each idea starts with a table of numbers and a picture, and only then becomes a formula. You run the steps by hand, so you can predict what the computer does.

Only the optional Coin Run exercise needs a project. Each sketch is a whole program: save it as `sketch.cpp` and compile it with C++20 in the terminal of [How a C++ program is built](build.md#open-a-terminal-that-finds-a-compiler). On Windows, run `cl /std:c++20 /EHsc sketch.cpp` and then `.\sketch.exe`. On Linux and macOS, run `c++ -std=c++20 sketch.cpp -o sketch` and then `./sketch`. Without a compiler, read each output and its notes.

## A rate of change is how much per second

A cart rolls along a rail. You note its position in metres every second and write the numbers down.

| Time (s) | 0 | 1 | 2 | 3 | 4 |
| --- | --- | --- | --- | --- | --- |
| Position (m) | 0 | 1 | 4 | 9 | 16 |

The cart moved 1 m in the first second, 3 m in the second, 5 m in the third and 7 m in the fourth. The **rate of change** of a quantity is how much it changes in each unit of time. Here the rate of the position is the speed, in metres per second, and it grows.

::figure{id=position-slope}

On the graph, time runs across and position runs up. Between two points, the rise divided by the run is the slope: the change of position divided by the change of time. The slope is the rate. A steep part of the graph is a fast part of the motion, and a flat part is a rest.

:::example[The cart's speed in each second]
Take the second between 2 s and 3 s. The position goes from 4 m to 9 m, a rise of 5 m in a run of 1 s. The rate is 5 m / 1 s = 5 m/s. The fourth second gives (16 - 9) / 1 = 7 m/s.
:::

Try it: a drone is at 10 m, 10 m, 12 m and 18 m at 0 s, 1 s, 2 s and 3 s. What are its speeds, and in which second is the graph steepest?

:::answer
The speeds are 0, 2 and 6 m/s. The last second is the steepest: the drone got faster.
:::

A table gives the average rate over a whole second. The cart does not keep one speed during that second, so the next section asks for the rate at a single moment.

## The derivative is the rate at one moment

At 2 s the speed of the cart is neither the 3 m/s of the second before nor the 5 m/s of the second after. To find the speed at exactly 2 s, shrink the interval that starts there and compute the rate over each.

| Interval | Rise | Run | Rate |
| --- | --- | --- | --- |
| 2 s to 3 s | 9 - 4 = 5 m | 1 s | 5 m/s |
| 2 s to 2.5 s | 6.25 - 4 = 2.25 m | 0.5 s | 4.5 m/s |
| 2 s to 2.1 s | 4.41 - 4 = 0.41 m | 0.1 s | 4.1 m/s |
| 2 s to 2.01 s | 4.0401 - 4 = 0.0401 m | 0.01 s | 4.01 m/s |

The rates close in on 4 m/s. The **derivative** of a quantity is the rate that these shrinking intervals approach: the slope of the graph at one point. The derivative of the cart's position at 2 s is 4 m/s. The same method gives 2 × t at any time t, so the speed is 6 m/s at 3 s.

Mathematics writes the derivative of the position with a fraction.

$$ v = \frac{dx}{dt} $$

Read it aloud as "v equals d x over d t". Here $v$ is the velocity in metres per second, $x$ is the position in metres, and $t$ is the time in seconds. The letter $d$ stands for "a tiny change of", so $dx$ is a tiny change of position and $dt$ is the tiny change of time that goes with it. The fraction is an ordinary division of two changes so small that the slope no longer depends on their size.

A computer never reaches "nothing". It takes a small interval, such as the length of one frame, and divides. That is enough for a game.

Try it: the position is $x = t^2$ again. Compute the rate between 3 s and 3.1 s, and guess the derivative at 3 s.

:::answer
The position is 9 m at 3 s and 9.61 m at 3.1 s. The rate is 0.61 / 0.1 = 6.1 m/s, so the derivative at 3 s is 6 m/s, as the rule 2 × t says.
:::

## Accumulation adds small pieces into a total

Now turn the question around. You know the speed at each moment and you want the distance. The speed table of the same cart reads as follows.

| Time (s) | 0 | 1 | 2 | 3 | 4 |
| --- | --- | --- | --- | --- | --- |
| Speed (m/s) | 0 | 2 | 4 | 6 | 8 |

During one second, a speed times a time is a distance. For the first second, take the speed at its start, 0 m/s, and get 0 m. The next three seconds give 2 m, 4 m and 6 m. **Accumulation** is the adding up of many small pieces into a total, and here the total is 0 + 2 + 4 + 6 = 12 m.

::figure{id=speed-rectangles}

Each piece is a rectangle under the speed graph: its width is the time and its height is the speed. The sum of the rectangles is a distance, and also an area. The sum of 12 m is too small, because the speed grew during every second and each rectangle used the speed at its start. The speeds at the end of each second give 2 + 4 + 6 + 8 = 20 m, which is too large. The position table says that the true distance is 16 m.

Narrower rectangles close the gap, and the next program shows how.

:::question[Why do the programs start with lines I have not seen?]
Each program starts with `#include` lines that bring in a library, and calls functions such as `std::printf(...)`, whose `std::` names the library. [Programming 3](../basics/programming-3.md) explains both; here, read them as "use the library" and "call its function".
:::

The program below sums rectangles of the speed 2 × t between 0 s and 4 s, as many as you ask for. Look at how the total changes as the count grows.

```cpp sketch="basics-math-change-area.cpp"
// Rectangles under the speed graph v = 2 t between 0 s and 4 s: narrower rectangles come closer to the area, 16 m.
#include <cstdio>

float SumOfRectangles(int count)
{
	const float width = 4.0f / static_cast<float>(count);
	float sum = 0.0f;
	for (int i = 0; i < count; i++)
	{
		const float time = static_cast<float>(i) * width;
		sum += 2.0f * time * width; // the speed at the start of the rectangle times its width
	}
	return sum;
}

int main()
{
	for (int count = 4; count <= 1024; count *= 4)
		std::printf("%d rectangles: %g m\n", count, SumOfRectangles(count));
	return 0;
}
```

```text output-of="basics-math-change-area.cpp"
4 rectangles: 12 m
16 rectangles: 15 m
64 rectangles: 15.75 m
256 rectangles: 15.9375 m
1024 rectangles: 15.9844 m
```

1. **Line 6:** the width of every rectangle is the 4 seconds divided by the count.
2. **Line 11:** the speed at the start of the rectangle times its width is one piece.
3. **Line 18:** four times as many rectangles each time: 4, 16, 64, 256 and 1024.

The totals come closer to 16 m, and the gap halves when the width halves. The **integral** of the speed is the value that the sums approach as the rectangles become narrower and narrower: the area under the graph. Mathematics writes it with a stretched S, for "sum".

$$ x = \int_0^4 v \, dt $$

Read it aloud as "x equals the integral from 0 to 4 of v with respect to t". Here $x$ is the distance in metres, and $v$ is the speed in metres per second at each moment. The symbol $dt$ is the tiny width of one rectangle, in seconds, and the numbers 0 and 4 are the start and the end of the time that is added up. For $v = 2t$ the area is a triangle with the base 4 s and the height 8 m/s, so the integral is 4 × 8 / 2 = 16 m.

A path through fog adds up in the same way. Say the density of the fog, the amount of fog per metre, is 0.2, 0.4, 0.6 and 0.8 at the start of each metre of a 4 m path. Each piece is the density times the length, 1 m, so the total is 0.2 + 0.4 + 0.6 + 0.8 = 2.0. A program that marches along a ray in small steps and adds a little at each step does this sum, and [Earth's atmosphere and aerial perspective](../light/atmosphere.md) uses it for air. [Chance](../basics/math-probability.md) uses the same area for averages.

Try it: a car drives at 10 m/s for 3 s, then at 20 m/s for 2 s. How far does it drive?

:::answer
The area is two rectangles: 10 × 3 = 30 m and 20 × 2 = 40 m. The car drives 70 m.
:::

## Velocity and acceleration are vectors

In a game things move in three directions, so a speed needs a direction. [Vectors](../basics/math-vectors.md) supplies the tool: an arrow of three numbers. The **velocity** of a body is the rate of change of its position, as a vector. Its length is the speed.

A ball moves from the position (2, 5, 0) to (2.5, 4.8, 0) in 0.1 s. The step is (0.5, -0.2, 0) m, and dividing each number by 0.1 s gives the velocity (5, -2, 0) m/s. The speed is the length of that vector, the square root of 25 + 4, about 5.39 m/s.

Velocity changes too. The **acceleration** of a body is the rate of change of its velocity, as a vector, in metres per second per second (m/s²). If the ball has the velocity (5, -2.981, 0) m/s 0.1 s later, the change is (0, -0.981, 0) m/s, and the acceleration is (0, -0.981, 0) / 0.1 = (0, -9.81, 0) m/s².

That acceleration is gravity near the ground of the Earth: every falling body gains 9.81 m/s of downward speed in each second, whatever its mass. In Strata the +Y axis points up, and a new scene has the gravity (0, -9.81, 0), as the `Gravity` setting in `Strata/src/Strata/Scene/Scene.h` says.

Accumulation connects the three. The velocity of a falling ball is the accumulated acceleration: after t seconds it is -9.81 × t. The height changes by the accumulated velocity. The triangle under that line has the base t and the height 9.81 × t, so its area is half of t × 9.81 × t. A ball released at the height $y_0$ is at $y_0$ - 4.905 × t² after t seconds.

:::example[A ball dropped from a tower]
After 3 s the velocity is -9.81 × 3 = -29.43 m/s. The ball has fallen 4.905 × 3² = 44.145 m, which is the area of the triangle under the velocity line.
:::

Try it: how long does the ball take to fall its first 5 m, and how fast does it move then?

:::answer
The fall is 4.905 × t² = 5, so t² is about 1.019 and t is about 1.01 s. The velocity then is about -9.9 m/s.
:::

## The explicit Euler step moves by the old velocity

A game does not know the formula of a motion. A thrown ball meets a wall, a player pushes a crate, and no triangle gives the answer. So a game moves bodies in small steps, from the present state to the next. **Numerical integration** is computing a motion by accumulating it in steps.

The **time step** is the length of one such step in seconds, written $h$ below. The simplest method uses what you already know: the position changes by the velocity times the time step, and the velocity changes by the acceleration times the time step.

```pseudocode
position = position + velocity * h
velocity = velocity + acceleration * h
```

The **explicit Euler method**, also called forward Euler, runs these two lines in this order: the position moves by the old velocity, and only then does the velocity change. Everything on the right of each line is a value from the start of the step.

Here is the falling ball from a height of 10 m, with a step of 0.5 s. The program prints the method's table beside the exact height, 10 - 4.905 × t².

```cpp sketch="basics-math-change-fall.cpp"
// A ball falls from 10 m with the explicit Euler step: the position moves by the old velocity, then the velocity changes.
#include <cstdio>

int main()
{
	const float gravity = -9.81f;
	const float step = 0.5f;
	float height = 10.0f;
	float velocity = 0.0f;
	for (int i = 0; i <= 4; i++)
	{
		const float time = static_cast<float>(i) * step;
		const float exact = 10.0f + 0.5f * gravity * time * time;
		std::printf("t = %.1f s: height %.3f m, velocity %.3f m/s, exact height %.3f m\n", time, height, velocity, exact);
		height += velocity * step;  // first the position, with the old velocity
		velocity += gravity * step; // then the velocity
	}
	return 0;
}
```

```text output-of="basics-math-change-fall.cpp"
t = 0.0 s: height 10.000 m, velocity 0.000 m/s, exact height 10.000 m
t = 0.5 s: height 10.000 m, velocity -4.905 m/s, exact height 8.774 m
t = 1.0 s: height 7.547 m, velocity -9.810 m/s, exact height 5.095 m
t = 1.5 s: height 2.642 m, velocity -14.715 m/s, exact height -1.036 m
t = 2.0 s: height -4.715 m, velocity -19.620 m/s, exact height -9.620 m
```

1. **Line 13:** the exact height from the triangle of the last section.
2. **Line 15:** first the position, with the old velocity.
3. **Line 16:** then the velocity; its new value reaches the position only in the next step.

Look at the second row. At 0.5 s the ball has not moved, because the old velocity was 0. At 2 s the method says -4.715 m and the exact height is -9.62 m. The ball falls too slowly, since every step uses a velocity that is already out of date.

## The semi-implicit Euler step moves by the new velocity

Swap the two lines and the result changes. The **semi-implicit Euler method**, also called symplectic Euler, changes the velocity first and then moves the position with the new velocity.

```pseudocode
velocity = velocity + acceleration * h
position = position + velocity * h
```

For a falling ball the difference is small: the explicit method ends too high, and the semi-implicit method ends too low by the same amount. A spring shows a difference that matters. Hang a ball on a spring that pulls toward 0 with the acceleration -x, pull it to x = 1 and let go. A spring without friction swings back and forth forever, and its energy stays the same. That energy is half the velocity squared plus half the position squared, here 0.5 at the start.

With a step of 0.5 s, the program below runs both methods side by side and prints the energy of each.

```cpp sketch="basics-math-change-spring.cpp"
// A spring that pulls with an acceleration of -x, started at x = 1: the energy 0.5 v² + 0.5 x² should stay at 0.5.
#include <cstdio>

int main()
{
	const float step = 0.5f;
	float explicitX = 1.0f, explicitV = 0.0f;
	float semiX = 1.0f, semiV = 0.0f;
	for (int i = 1; i <= 20; i++)
	{
		const float oldX = explicitX;
		explicitX += explicitV * step; // explicit: the position with the old velocity ...
		explicitV += -oldX * step;     // ... the velocity with the old position
		semiV += -semiX * step;        // semi-implicit: the velocity first ...
		semiX += semiV * step;         // ... the position with the new velocity
		if (i <= 4 || i == 20)
			std::printf("step %2d: explicit x %7.3f energy %6.3f | semi-implicit x %6.3f energy %5.3f\n", i, explicitX,
				0.5f * explicitV * explicitV + 0.5f * explicitX * explicitX, semiX, 0.5f * semiV * semiV + 0.5f * semiX * semiX);
	}
	return 0;
}
```

```text output-of="basics-math-change-spring.cpp"
step  1: explicit x   1.000 energy  0.625 | semi-implicit x  0.750 energy 0.406
step  2: explicit x   0.750 energy  0.781 | semi-implicit x  0.312 energy 0.432
step  3: explicit x   0.250 energy  0.977 | semi-implicit x -0.203 energy 0.552
step  4: explicit x  -0.438 energy  1.221 | semi-implicit x -0.668 energy 0.655
step 20: explicit x  -9.206 energy 43.368 | semi-implicit x -0.613 energy 0.400
```

1. **Lines 11–13:** explicit; the acceleration comes from the old position, kept in `oldX` before the position moves.
2. **Lines 14–15:** semi-implicit; the new velocity moves the position.
3. **Line 16:** a row for each of the first four steps and the last, to compare the energies.

The energy of the explicit method grows in every step, from 0.5 to 0.625, 0.781 and 0.977, and after 20 steps, 10 s of simulated time, it is 43.4. The spring swings wider and wider with nobody pushing it. The energy of the semi-implicit method moves up and down but stays near 0.5: over thousands of steps it stays between about 0.4 and 0.67.

::figure{id=two-springs}

The reason lies in how each step uses its information. The explicit step computes both changes from the old state, and the combination always pushes outward: for this spring it multiplies the energy by 1.25 in every step. The semi-implicit step lets the position see the velocity that the force has already changed, which closes the loop of position and velocity instead of letting it spiral out.

Physics engines integrate this way, and so does Strata's. The library under Strata's physics states that it uses semi-implicit Euler (`Strata/vendor/box3d/docs/faq.md`), and [Rigid body dynamics](../physics/dynamics.md) shows where it runs. The price is accuracy: the method is only first order, which the next section measures.

:::why[Why Strata's physics prefers the semi-implicit step]
Games run for hours, and a ball that gains energy in every step shoots out of the world. The semi-implicit method costs the same as the explicit one, two lines and no extra work, and it never adds energy to a spring. A more accurate method needs several force evaluations per step, which a scene with thousands of bodies cannot afford.
:::

Try it: do one semi-implicit step by hand for the spring with h = 0.5 from x = 1 and v = 0, and check the first row of the program's table.

:::answer
The velocity changes first: 0 + (-1) × 0.5 = -0.5. The position moves with the new velocity: 1 + (-0.5) × 0.5 = 0.75. The energy is 0.5 × 0.25 + 0.5 × 0.5625 = 0.406, as the first row says.
:::

## The size of the step decides the error, and a large step explodes

Both methods approximate, and the step size decides how well. The next program runs one second of free fall from 10 m with the semi-implicit method and compares the result with the exact 5.095 m.

```cpp sketch="basics-math-change-error.cpp"
// One second of free fall from 10 m with the semi-implicit step: the error shrinks in proportion to the step.
#include <cstdio>

float FallError(float step)
{
	float height = 10.0f, velocity = 0.0f;
	const int count = static_cast<int>(1.0f / step + 0.5f);
	for (int i = 0; i < count; i++)
	{
		velocity += -9.81f * step;
		height += velocity * step;
	}
	return height - (10.0f - 4.905f); // the exact height after 1 s is 10 - 4.905 t² = 5.095 m
}

int main()
{
	for (float step = 0.5f; step > 0.01f; step *= 0.2f)
		std::printf("step %.2f s: error after 1 s %.3f m\n", step, FallError(step));
	return 0;
}
```

```text output-of="basics-math-change-error.cpp"
step 0.50 s: error after 1 s -2.453 m
step 0.10 s: error after 1 s -0.491 m
step 0.02 s: error after 1 s -0.098 m
```

1. **Line 13:** the exact height after 1 s, from the formula of the last sections.

The error is -2.453 m for a step of 0.5 s, -0.491 m for 0.1 s and -0.098 m for 0.02 s. A step five times smaller gives an error five times smaller, so the error is in proportion to the step. For falling it equals half the gravity times the step times the time, 0.5 × 9.81 × h × t.

A slowly growing error is the good case. The spring shows the bad one: a step that is too long makes the method unstable. The program below runs 20 semi-implicit steps with four sizes and prints the largest distance from the middle that the ball reaches.

```cpp sketch="basics-math-change-explode.cpp"
// The semi-implicit step on the spring from before, with larger and larger steps: past a step of 2 s it explodes.
#include <cmath>
#include <cstdio>
#include <vector>

float LargestPosition(float step)
{
	float position = 1.0f, velocity = 0.0f, largest = 1.0f;
	for (int i = 0; i < 20; i++)
	{
		velocity += -position * step;
		position += velocity * step;
		largest = std::fmax(largest, std::fabs(position));
	}
	return largest;
}

int main()
{
	for (float step : std::vector<float>{ 0.5f, 1.0f, 1.9f, 2.1f })
		std::printf("step %.1f s: largest |x| in 20 steps %g\n", step, LargestPosition(step));
	return 0;
}
```

```text output-of="basics-math-change-explode.cpp"
step 0.5 s: largest |x| in 20 steps 1.0322
step 1.0 s: largest |x| in 20 steps 1
step 1.9 s: largest |x| in 20 steps 3.2021
step 2.1 s: largest |x| in 20 steps 632673
```

1. **Line 11:** the velocity from the old position, in the semi-implicit order.
2. **Line 13:** the largest distance so far; the starting distance is 1.

Steps of 0.5 s and 1 s keep the ball near 1, and 1.9 s lets it reach 3.2. With 2.1 s the ball reaches 632,673 after 20 steps: the simulation explodes. For this spring the limit is a step of 2 s, about a third of its swing of 6.3 s. A stiffer spring swings faster and needs shorter steps, and a stiff contact between two bodies behaves like a very stiff spring.

::figure{id=exploding-step}

Strata lowers the danger in two ways. Its physics library works in four smaller steps inside each step (`c_SolverSubSteps` in `Strata/src/Strata/Physics/PhysicsWorld.cpp`), and the step itself has a fixed length. The scene's `FixedTimestep` setting is 1/60 s by default, and `MaxFixedStepsPerFrame` limits one frame to 8 steps (`Strata/src/Strata/Scene/Scene.h`).

Why fixed? The error depends on the step. The next program makes a jump that leaves the ground at 5 m/s, where the exact peak is 1.274 m, and runs it with three steps.

```cpp sketch="basics-math-change-jump.cpp"
// A jump that leaves the ground at 5 m/s, simulated with different step sizes; the exact peak is 1.274 m.
#include <cstdio>

float JumpPeak(float step)
{
	float height = 0.0f, velocity = 5.0f, peak = 0.0f;
	while (velocity > 0.0f)
	{
		velocity += -9.81f * step;
		height += velocity * step;
		peak = height > peak ? height : peak;
	}
	return peak;
}

int main()
{
	for (int rate = 30; rate <= 120; rate *= 2)
		std::printf("step 1/%d s: jump peak %.3f m\n", rate, JumpPeak(1.0f / static_cast<float>(rate)));
	return 0;
}
```

```text output-of="basics-math-change-jump.cpp"
step 1/30 s: jump peak 1.192 m
step 1/60 s: jump peak 1.233 m
step 1/120 s: jump peak 1.253 m
```

1. **Line 7:** the loop ends when the velocity turns downward.
2. **Line 11:** the peak is the largest height seen.

A player whose machine draws a frame every 1/30 s jumps to 1.192 m, and one at 1/120 s jumps to 1.253 m. With a fixed step every machine gives the same jump, and a recorded input replays the same way. The price is that a slow frame runs several steps and a very slow one drops some. [Time](../core/time.md) explains the accumulator that does this.

Try it: the jump at 1/60 s is 0.041 m too low. About how far off is the jump at 1/120 s?

:::answer
Half as far, about 0.02 m. The program shows 1.253 m, which is 0.021 m below 1.274 m.
:::

## Newton's laws connect force, mass and acceleration

What makes the acceleration in the Euler step? **Newton's laws of motion** answer with three rules. The first says that a body keeps its velocity, at rest or in motion, until a force acts on it. The second says how a force changes the velocity. The third says that forces come in pairs.

A **force** is a push or a pull on a body, a vector measured in newtons.

The **mass** of a body is how much it resists a change of velocity, in kilograms. The second law ties force, mass and acceleration together.

$$ F = m \, a $$

Read it aloud as "force equals mass times acceleration". Here $F$ is the sum of all the forces on the body, in newtons, $m$ is the mass in kilograms, and $a$ is the acceleration in metres per second squared. One newton is the force that gives a 1 kg body an acceleration of 1 m/s². A heavier body needs a larger force for the same acceleration, so the acceleration is the force divided by the mass.

:::example[A push on a ball]
A 2 kg ball at rest is pushed with 6 newtons along +X. Its acceleration is 6 / 2 = 3 m/s². With a step of 0.5 s, the semi-implicit method gives the velocity 3 × 0.5 = 1.5 m/s and then the position 1.5 × 0.5 = 0.75 m.
:::

Gravity is a force too: the weight of a body is $m × 9.81$ newtons downward. Divide by the mass and the acceleration is 9.81 m/s² for any body, which is why a heavy and a light ball fall together.

The first law explains why a ball on a table slows: something pushes against it, and on a table that something is friction. In empty space the ball would roll on forever. In Strata a body also loses a little speed through damping, since the `RigidBody` component's `LinearDamping` property is 0.05 by default.

The third law says that when body A pushes body B, B pushes A with a force of the same size in the opposite direction. A 1 kg ball hits a 3 kg ball: the forces are equal, so the light ball changes its velocity three times as much. New bodies have a `Mass` of 1 kg by default.

Try it: a 4 kg crate gets a net force of 12 newtons. What are its acceleration and its velocity after 2 s, starting at rest?

:::answer
The acceleration is 12 / 4 = 3 m/s². The velocity is the acceleration accumulated for 2 s: 3 × 2 = 6 m/s.
:::

## Momentum and impulse describe a hit

A kick lasts 0.01 s, and nobody knows its force at each instant. What matters is the total push. The **momentum** of a body is its mass times its velocity, in kilogram metres per second.

$$ p = m \, v $$

Read it aloud as "p equals m times v". Here $p$ is the momentum, $m$ is the mass in kilograms and $v$ is the velocity in metres per second. A force changes momentum: acting for a time, it adds its size times the time. The **impulse** of a force is that product, in newton seconds, and it equals the change of momentum.

$$ J = F \, \Delta t = m \, \Delta v $$

Read it aloud as "J equals F times delta t, which equals m times delta v". Here $J$ is the impulse, $F$ is the force in newtons, and $\Delta t$ is the time in seconds that the force acts. The symbol $\Delta v$ is the change of velocity in metres per second, so $\Delta v = J / m$.

:::example[A kick of 0.01 s]
A kick of 500 newtons lasts 0.01 s on a ball of 0.5 kg. The impulse is 500 × 0.01 = 5 newton seconds, and the velocity changes by 5 / 0.5 = 10 m/s. A kick of 0.005 s with 1000 newtons has the same impulse and gives the same change.
:::

A large force over a short time and a small force over a long time can have the same impulse, and the change of velocity depends only on the impulse. A game seldom knows how long a hit lasts, so it states the impulse and changes the velocity at once.

The software development kit (SDK) of the scripts has both ways, on the `RigidBody` of an entity (`StrataScriptCore/Include/StrataScript/Physics.h`). `AddImpulse` changes the velocity at once. `AddForce` acts during the next fixed step only, so a force that should act for a second needs a call in every `OnFixedUpdate`. A force applied once adds its size times one step, here 1/60 s, to the momentum. A force of 600 newtons on a 1 kg body changes the velocity by 10 m/s; an impulse of 10 newton seconds does so for any step.

A jump pad gives the ball an impulse upward. For a 1 kg ball with the impulse (0, 7, 0), the velocity changes at once by 7 m/s and the ball rises about 7² / (2 × 9.81) = 2.5 m. [Physics for game makers](../make/physics.md) shows the same calls from the editor side.

Try it: you give a 0.5 kg ball the velocity 8 m/s upward. What impulse is that, and what force over one fixed step of 1/60 s gives the same?

:::answer
The impulse is 0.5 × 8 = 4 newton seconds. A force over one step of 1/60 s needs 4 × 60 = 240 newtons.
:::

## Common mistakes

- **Multiplying by `deltaTime` twice, or not at all.** Symptom: a body that moves far too slowly, or at a speed that changes with the frame rate. A velocity is already per second, so the position moves by the velocity times the step once, and the velocity changes by the acceleration times the step once. Fix: count the factors of the step in each line.
- **Moving by the old velocity where the new one was meant.** Symptom: a spring that swings wider and wider, or a ball that lags a step. Fix: change the velocity first, then move the position with the new velocity.
- **A varying step for physics.** Symptom: a jump that is higher on one machine than on another, or a simulation that explodes after a slow frame. Fix: run physics in `OnFixedUpdate` with its fixed step, and use the frame's `deltaTime` only for what the player sees.
- **A force applied once as if it were an impulse.** Symptom: a jump pad that barely moves the ball, or one whose jump changes with the step. A call of `AddForce` lasts one step only. Fix: use `AddImpulse` for a hit or a jump, and `AddForce` in every `OnFixedUpdate` for a push that lasts.
- **The mass forgotten in an impulse.** Symptom: a heavy crate that jumps as high as a light one, or the reverse. The change of velocity is the impulse divided by the mass. Fix: give the impulse as the mass times the change of velocity you want.

## Summary

- A rate of change is the change of a quantity divided by the time, the slope of its graph; the derivative is the rate at one moment, found from shorter and shorter intervals.
- Accumulation adds small pieces into a total: rectangles of speed times time give a distance, and the integral is the area under the graph that narrower rectangles approach.
- The explicit Euler method moves the position by the old velocity and then changes the velocity. The semi-implicit method changes the velocity first and moves by the new one, which keeps a spring's energy where the explicit method adds energy.
- The error of a step is in proportion to its size, a step beyond the limit makes a simulation explode, and a fixed step gives every machine the same result.
- Force equals mass times acceleration, in newtons and kilograms; an impulse is force times time and changes the velocity at once, and `AddImpulse` does this where `AddForce` acts for one fixed step.

## Check yourself

1. The positions of a cart at 0 s, 2 s and 4 s are 0 m, 6 m and 22 m. What is its average speed between 2 s and 4 s? (a) 4 m/s (b) 8 m/s (c) 11 m/s (d) 16 m/s

   :::answer{tests="rate-slope"}
   (b) 8 m/s: the rise is 22 - 6 = 16 m over a run of 2 s. (a) divides by 4 s, the whole time, (c) divides the last position by 2 s, and (d) forgets the division.
   :::

2. A speed graph is a straight line from 0 m/s at 0 s to 6 m/s at 3 s. How far does the body travel, and is the sum of rectangles that use the start of each second too large or too small?

   :::answer{tests="accumulate"}
   The area of the triangle is 3 × 6 / 2 = 9 m. The rectangles that use the speed at the start of each second give 0 + 2 + 4 = 6 m, which is too small, because the speed grows during each second.
   :::

3. Predict the first two rows of the spring table for the explicit method with h = 1, starting at x = 1, v = 0 and the acceleration -x. What does the semi-implicit method give for the position in the first row?

   :::answer{tests="euler-steps"}
   Explicit, row 1: x = 1 + 0 × 1 = 1 and v = 0 - 1 = -1. Row 2: x = 1 + (-1) = 0 and v = -1 - 1 × 1 = -2. Semi-implicit, row 1: v = -1 first, then x = 1 + (-1) × 1 = 0.
   :::

4. A game uses the `deltaTime` of each frame as the physics step. On a computer that suddenly draws a frame of 2.5 s the ball vanishes. Which two facts of this page explain it?

   :::answer{tests="step-size"}
   The error grows with the step, and past a limit that depends on how stiff the contacts are, the method explodes. A fixed step, with a limit on the steps per frame, avoids both.
   :::

5. A 3 kg ball moves at 2 m/s. You want it to move at 5 m/s in the same direction at once. Which call and which value? (a) `AddForce` of 9 (b) `AddImpulse` of 9 (c) `AddImpulse` of 3 (d) `AddForce` of 3

   :::answer{tests="newton-impulse"}
   (b): the change of velocity is 3 m/s, and the impulse is 3 × 3 = 9 newton seconds. (a) is a force for one step, so it adds only 9 / 60 newton seconds; (c) forgets the mass of 3 kg.
   :::

## Practice

1. **Basic.** A drone is at 0 m, 5 m, 15 m and 30 m at 0 s, 1 s, 2 s and 3 s. Compute its speed in each second and say what the graph of its position looks like.

   :::answer[Worked solution]{tests="rate-slope"}
   The speeds are 5, 10 and 15 m/s. They grow by 5 m/s each second, so the graph bends upward, steeper with every second, as for the cart.
   :::

2. **Medium.** Throw a ball up at 6 m/s from the height 0, with gravity -10 m/s² and the step 0.2 s. Run three explicit steps by hand and then three semi-implicit steps, and write the height and the velocity after each.

   :::answer[Worked solution]{tests="euler-steps accumulate"}
   Explicit: the heights are 1.2, 2.0 and 2.4 m, with the velocities 4, 2 and 0 m/s. Semi-implicit: the velocities are the same, but the heights use the new velocity: 0.8, 1.2 and 1.2 m. The exact peak is 1.8 m, which the explicit method ends above and the semi-implicit method below.
   :::

3. **Medium.** A 4 kg crate gets a net force of 20 newtons for 3 s, starting at rest. What are its acceleration, final velocity and momentum? What impulse gives the same final velocity at once?

   :::answer[Worked solution]{tests="newton-impulse"}
   The acceleration is 20 / 4 = 5 m/s² and the velocity after 3 s is 15 m/s. The momentum is 4 × 15 = 60 kg m/s. The impulse is the same 60 newton seconds, the force 20 times 3 s.
   :::

4. **Hard.** In a program of your own, push a 2 kg crate with 6 newtons for one second in 60 semi-implicit steps and print the velocity and the distance. Then print the velocity that an impulse of 6 newton seconds gives at once.

   :::answer[Worked solution]{tests="newton-impulse euler-steps" solution="sketches/basics-math-change-crate.cpp"}
   The acceleration is the force divided by the mass, 3 m/s², and every step adds 3 / 60 to the velocity.

   ```cpp sketch="basics-math-change-crate.cpp"
   // A 2 kg crate at rest is pushed with 6 N for one second at 60 steps per second, then another is given the same impulse.
   #include <cstdio>

   int main()
   {
   	const float mass = 2.0f;
   	const float step = 1.0f / 60.0f;
   	float velocity = 0.0f, position = 0.0f;
   	for (int i = 0; i < 60; i++)
   	{
   		velocity += (6.0f / mass) * step; // force over mass is the acceleration
   		position += velocity * step;
   	}
   	std::printf("pushed for 1 s: velocity %.3f m/s, moved %.3f m\n", velocity, position);

   	const float impulse = 6.0f * 1.0f;           // force times time, in newton seconds
   	std::printf("impulse of %g N s: velocity %.3f m/s at once\n", impulse, impulse / mass);
   	return 0;
   }
   ```

   ```text output-of="basics-math-change-crate.cpp"
   pushed for 1 s: velocity 3.000 m/s, moved 1.525 m
   impulse of 6 N s: velocity 3.000 m/s at once
   ```

   1. **Line 11:** the force over the mass is the acceleration, and the step is the only factor of time.
   2. **Line 12:** the new velocity moves the position, as in the semi-implicit method.
   3. **Line 16:** an impulse changes the velocity by the impulse over the mass, with no steps.

   The crate reaches 3 m/s either way. The exact distance of the push is 1.5 m; the steps give 1.525 m, an error that a smaller step shrinks.
   :::

5. **Hard.** Optional, on your [Coin Run](../make/project-coin-run.md) or Checkpoint 4 of [Ship the finished game](../make/project-coin-run.md#ship-the-finished-game): in a new script on the ball, compute the speed from the positions of two fixed steps and log it beside `GetLinearVelocity`. Then make a jump pad that gives the ball an upward impulse.

   :::answer[Worked solution]{tests="newton-impulse rate-slope"}
   The script keeps the position of the last fixed step. In every `OnFixedUpdate` the speed is the length of the change of position divided by the fixed step.

   ```cpp pseudocode
   class BallSpeed : public Script
   {
   public:
   	void OnCreate() override { m_Last = GetTransform().GetWorldPosition(); }

   	void OnFixedUpdate(float fixedDeltaTime) override
   	{
   		const glm::vec3 now = GetTransform().GetWorldPosition();
   		const float fromPositions = glm::length(now - m_Last) / fixedDeltaTime;
   		const float fromBody = glm::length(GetEntity().GetRigidBody().GetLinearVelocity());
   		Log::Info("speed from positions ", fromPositions, " m/s, from the body ", fromBody, " m/s");
   		m_Last = now;
   	}

   private:
   	glm::vec3 m_Last = glm::vec3(0.0f);
   };
   ```

   1. **Line 9:** the rate of change of the position over one fixed step is the speed.
   2. **Line 10:** the body's own velocity, the value to compare with.

   The two numbers should be close while the ball rolls freely, and can differ right after a collision. The jump pad is a second script, added to a pad whose `RigidBody` has `IsTrigger` enabled, so the ball passes through it and the script hears of the overlap.

   ```cpp pseudocode
   class JumpPad : public Script
   {
   public:
   	void OnTriggerEnter(const Collision& collision) override
   	{
   		collision.Other.GetRigidBody().AddImpulse(glm::vec3(0.0f, 6.0f, 0.0f));
   	}
   };
   ```

   The impulse of 6 newton seconds gives a ball of 1 kg the velocity 6 m/s upward at once, and the ball rises about 1.8 m. Try other values until the jump suits the level.
   :::

## Where the book uses it

- [Time](../core/time.md) uses the time step and the error it causes to explain the fixed step and its accumulator.
- [Rigid body dynamics](../physics/dynamics.md) uses the semi-implicit step, forces and impulses to explain how a body moves.
- [Sound in space](../audio/spatial.md) uses velocities, the rate of change of distance, for the Doppler effect.
- [Earth's atmosphere and aerial perspective](../light/atmosphere.md) uses accumulation along a path for the light that crosses air.

## Further reading

- [Gaffer on Games, "Integration Basics"](https://gafferongames.com/post/integration_basics/): explicit and semi-implicit Euler for a game's physics, with code; beginner.
- [Gaffer on Games, "Fix Your Timestep!"](https://gafferongames.com/post/fix_your_timestep/): why the step is fixed and how a game stays in step with real time; intermediate.
- 3Blue1Brown, "Essence of calculus" (video series): derivatives and integrals drawn as pictures before any formula; beginner.
- Box3D documentation in `Strata/vendor/box3d/docs/`: the physics library's own notes on its integrator and its limits; advanced.
