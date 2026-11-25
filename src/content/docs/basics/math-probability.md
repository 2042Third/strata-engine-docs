---
id: basics/math-probability
title: "Chance: probability, noise, integrals and Monte Carlo"
description: "How a game uses chance: probability, random numbers from a seed, estimating an area with random points, and spreading samples evenly."
kind: primer
size: L
tracks: [B, E]
needs: [basics/math-change, basics/signals]
time: 90
learn:
  - id: probability-rules
    text: compute the probability of a case from equally likely cases, and combine probabilities by adding and multiplying
  - id: mean-spread
    text: compute the expected value, the variance and the standard deviation from a table of values
  - id: seeded-generator
    text: explain how a seed makes a repeatable sequence, and why a remainder of a random number is biased
  - id: monte-carlo
    text: compute an estimate of an integral from random points, dividing each by its density, and predict how the error falls with the count
  - id: sample-patterns
    text: choose between white noise, blue noise, stratified offsets, the Hammersley set, the Vogel disk and Poisson disks
status: final
---

::::test-out

1. A coin of Coin Run is gold with probability 0.25, and each coin is decided on its own. Compute the probability that
   three coins in a row are all gold.

   :::answer{tests="probability-rules"}
   Independent events multiply: 0.25 × 0.25 × 0.25 = 0.015625, about 1.6 in 100.
   :::

2. The four values 2, 4, 4 and 6 are samples. Compute their mean and their standard deviation.

   :::answer{tests="mean-spread"}
   The mean is 16 / 4 = 4. The distances from it are -2, 0, 0 and 2, whose squares 4, 0, 0 and 4 average to 2. The
   standard deviation is the square root of 2, which is 1.41.
   :::

3. Two `Random` objects of the script software development kit (SDK) are both seeded with 7, and each draws three
   numbers. Do the two lists match? What if neither was seeded?

   :::answer{tests="seeded-generator"}
   Yes, they match: a seed starts a fixed rule, so equal seeds give equal sequences. Without a seed every generator
   starts the same way, so the lists match too.
   :::

4. A Monte Carlo estimate from 100 random points is off by about 0.2. How many points make it off by about 0.02?

   :::answer{tests="monte-carlo"}
   The error falls as one over the square root of the count. An error ten times smaller needs a hundred times more
   points: 10,000.
   :::

5. Compute the point with index 6 of the 8-point Hammersley set.

   :::answer{tests="sample-patterns"}
   The first coordinate is 6 / 8 = 0.75. The index 6 is 110 in binary; reversed, 011 read after a point is 0.011 in
   binary: 0.25 + 0.125 = 0.375. The point is (0.75, 0.375).
   :::

::::

## Why you will need this

A game is full of numbers that must look random but must also stay under control. Coin Run places its coins by chance,
and a test needs the same coins every time. A renderer cannot add up all the light that reaches a surface, so it adds
up a few samples chosen by chance and averages them. Chance also hides the stair-steps of banded colors, as film grain.

This page teaches the arithmetic of chance, then the tools Strata builds on it. [Directions and the
sphere](../basics/math-sphere.md) uses densities and Monte Carlo estimates over directions. [Light
energy](../light/energy.md) fills a table by averaging samples. [Sun shadows](../light/sun-shadows-2.md) turn a ring of
samples by a different angle at every pixel. A game maker who wants random numbers in a script finds the recipes in
[Recipes](../make/recipes.md); this page explains what they rest on.

Only the optional Coin Run exercise needs a project. Each sketch is a whole program: save it as `sketch.cpp` and compile it with C++20 in the terminal of [How a C++ program is built](build.md#open-a-terminal-that-finds-a-compiler). On Windows, run `cl /std:c++20 /EHsc sketch.cpp` and then `.\sketch.exe`. On Linux and macOS, run `c++ -std=c++20 sketch.cpp -o sketch` and then `./sketch`. Without a compiler, read each output and its notes.

## A probability counts equally likely cases

Roll one die. Six faces can come up, and none is favoured. The chance of a 6 is 1 case out of 6. The chance of an even
number is 3 cases (2, 4 and 6) out of 6, which is one half.

A **probability** is a number from 0 to 1 that says how likely a case is: 0 never happens, 1 always happens. When the
cases are equally likely, the probability of a group of them is the count of cases in the group divided by the count of
all cases. People also write it as a percentage: 0.5 is 50 %.

Two rules combine probabilities. Two cases are **exclusive** when they cannot both happen, like a 2 and a 5 on one roll.
Their probabilities add: a 2 or a 5 has 1/6 + 1/6 = 2/6. Two events are **independent** when one does not change the
other, like two different dice. The probability that both happen is the product: two sixes have 1/6 × 1/6 = 1/36.

Chance has no memory. After five sixes in a row, the sixth roll still has probability 1/6, because the dice do not
know what came before. One more rule helps. All cases together have probability 1, so "not this" has probability 1
minus "this". The chance of at least one six on two dice is 1 - 5/6 × 5/6 = 11/36.

:::question
What are `#include` and `std::printf`? [Programming from zero, part 3](../basics/programming-3.md) explains them; here, read `std::printf` as "print this text, putting the numbers in".
:::

Now add the faces of two dice. The program counts the 36 equally likely pairs and how many give each sum.

```cpp sketch="basics-math-probability-dice.cpp"
// Counts the 36 ways two dice can fall and prints the chance of each sum.
#include <cstdio>

int main()
{
	int counts[13] = {};
	for (int first = 1; first <= 6; first++)
		for (int second = 1; second <= 6; second++)
			counts[first + second]++;
	for (int sum = 2; sum <= 12; sum++)
		std::printf("sum %2d: %d of 36, chance %.3f\n", sum, counts[sum], counts[sum] / 36.0);
	return 0;
}
```

```text output-of="basics-math-probability-dice.cpp"
sum  2: 1 of 36, chance 0.028
sum  3: 2 of 36, chance 0.056
sum  4: 3 of 36, chance 0.083
sum  5: 4 of 36, chance 0.111
sum  6: 5 of 36, chance 0.139
sum  7: 6 of 36, chance 0.167
sum  8: 5 of 36, chance 0.139
sum  9: 4 of 36, chance 0.111
sum 10: 3 of 36, chance 0.083
sum 11: 2 of 36, chance 0.056
sum 12: 1 of 36, chance 0.028
```

1. **Lines 7–9:** two loops visit every pair, and each pair adds 1 to the count of its sum.
2. **Line 11:** the chance of a sum is its count divided by 36, the number of pairs.

The sum 7 has 6 pairs and the sum 2 has 1. Sums near the middle are likelier because more pairs make them.

::figure{id=dice-sums}

:::example[Seven or eleven]
The sum 7 has probability 6/36, and the sum 11 has 2/36. A roll cannot give both, so the cases are exclusive and you add:
8/36, about 0.22.
:::

Try it: what is the probability of a sum of 2 or 12?

:::answer
Each has 1 pair out of 36, and the cases are exclusive, so the probability is 1/36 + 1/36 = 2/36, about 0.056.
:::

## A random variable has a distribution

A **random variable** is a value that chance decides, such as the sum of two dice or the position of a coin.

Its **probability distribution** is the list of its possible values with the probability of each. The output above is the
distribution of the sum of two dice, and the figure draws it as bars.

A die is the simplest case: every face has probability 1/6. A distribution where every value is equally likely is
**uniform**. Games lean on one uniform distribution above all: a number between 0 and 1 where every part of the range
is as likely as every other part of the same size.

That range holds endless values, so each single value has probability zero. A **probability density** replaces the list
with a curve: the probability that the value falls in a part of the range is the area under the curve over that part. The
whole area is 1. For a uniform number in [0, 1) the curve is a flat line at height 1, which makes a rectangle of
area 1.

Add two such numbers, as Strata's output dither does before it rounds a color. The sum lies between 0 and 2, and its
density is a triangle: it rises from 0 at 0 to a peak of 1 at 1, and falls back to 0 at 2. The triangle is the smooth
cousin of the dice bars, because one cause makes both: the middle can be made in more ways.

::figure{id=triangle-density}

:::example[The chance of a sum between 1 and 1.5]
Between 1 and 1.5 the triangle falls from height 1 to 0.5. Cut that part into a rectangle of height 0.5 and a small
triangle on top. The rectangle has area 0.5 × 0.5 = 0.25, and the triangle has area 0.5 × 0.5 × 0.5 = 0.125. The sum of
two uniform numbers lands in that part with probability 0.375, which is 37.5 % of the time.
:::

Try it: what is the probability that the sum lands between 0 and 1?

:::answer
That part is the left half of the triangle: a right triangle with base 1 and height 1, whose area is 1 × 1 / 2 = 0.5.
:::

## The expected value is the mean, and the spread says how far values stray

Throw a die many times and average the results. The average settles near 3.5, although no face shows 3.5. The **expected
value** of a random variable is that settling point: each value times its probability, added up. For a die, (1 + 2 + 3 +
4 + 5 + 6) / 6 = 3.5. For the sum of two dice it is 7.

The **mean** is the same number computed from samples you actually have: their sum divided by their count. A mean of many
samples lies close to the expected value.

Two sets of samples can share a mean and still differ: 4, 5, 5, 6 and 1, 5, 5, 9 both have mean 5. The **variance**
measures the difference. For each sample, take its distance from the mean, square it, and average the squares.

The **standard deviation** is the square root of the variance, which puts the spread back in the units of the samples.

$$
\sigma^2 = \frac{1}{n} \sum_{i=1}^{n} (x_i - \mu)^2
$$

$x_i$ is sample number $i$, which counts from 1 to $n$, the number of samples. $\mu$ is their mean. $\sum$ is read "the
sum over", here of each squared distance. $\sigma^2$ is the variance, and its square root $\sigma$ is the standard
deviation.

:::example[A pixel's neighborhood]
Strata's temporal anti-aliasing, described in [Temporal anti-aliasing](../image/taa.md), reads the 3 × 3 pixels around a
pixel and measures how much their colors vary. Take the nine values 0.2, 0.4, 0.4, 0.5, 0.5, 0.5, 0.6, 0.6, 0.8.
The sum is 4.5, so the mean is 0.5.

The distances are -0.3, -0.1, -0.1, 0, 0, 0, 0.1, 0.1 and 0.3, and their squares add to 0.22. The variance is 0.22 / 9 =
0.0244, and the standard deviation is 0.156. Strata's shader finds the same number as the mean of the squares minus the
square of the mean. It pulls the old frame's color into a box around the mean that reaches a set number of standard
deviations on each side.
:::

Try it: the samples are 1, 1, 1 and 5. Compute the mean and the standard deviation.

:::answer
The mean is 8 / 4 = 2. The squared distances are 1, 1, 1 and 9, which add to 12, so the variance is 3. The standard
deviation is the square root of 3, about 1.73.
:::

Two facts about spread are used again below. The variance of a sum of independent values is the sum of their variances,
and the variance of the mean of $n$ independent samples is the variance of one sample divided by $n$. The standard deviation of that mean is then divided by $\sqrt{n}$. Check the first
on two dice: one die has variance 2.92, and the distribution above gives 5.83 for the sum, twice as much.

Film grain in Strata's post-processing uses the first fact. A uniform number in [0, 1) has variance 1/12, so the sum of
four independent ones has variance 4/12 = 1/3 and standard deviation 0.577. The shader subtracts the mean, 2, and
multiplies by 1.7320508, the square root of 3. Scaling a value by $k$ scales its standard deviation by $k$, so the
result has standard deviation 1. The grain's strength setting then scales a noise of known size.

## A generator makes a random-looking sequence from a seed

A computer cannot toss a coin: it obeys rules. A **pseudo-random number generator** is a fixed rule that turns a stored
number, its state, into the next number of a sequence that looks random, and then changes the state.

The **seed** is the number that sets the first state. The same seed always gives the same sequence, which is a feature:
a test, a replay or a shared level code needs exactly that.

Strata's script SDK has such a generator, `Random`, which implements the permuted congruential generator (PCG32). **PCG32** is a small, fast pseudo-random number
generator of good statistical quality. A seed gives the same numbers on every platform and compiler. The next lines are
the seeding and the step of the sequence.

```cpp src="StrataScriptCore/Include/StrataScript/Gameplay.h#L32-L48"
void Seed(uint64_t seed)
{
	m_State = 0;
	NextUInt();
	m_State += seed;
	NextUInt();
}

// Uniform over every 32-bit value.
uint32_t NextUInt()
{
	const uint64_t state = m_State;
	m_State = state * c_Multiplier + c_Increment;
	const uint32_t xorShifted = static_cast<uint32_t>(((state >> 18u) ^ state) >> 27u);
	const uint32_t rotation = static_cast<uint32_t>(state >> 59u);
	return (xorShifted >> rotation) | (xorShifted << ((32u - rotation) & 31u));
}
```

1. **Line 34:** the state is a 64-bit :term[integer]{id=integer}, and a seed starts from state 0.
2. **Lines 35–37:** one step, then the seed added, then another step, so that a small seed such as 1 or 2 does not give a similar first number.
3. **Line 44:** the step multiplies the state by a large odd constant and adds another; the product wraps around at 64 bits, which the rule wants.
4. **Lines 45–46:** the output mixes the old state: it shifts the high bits down, combines them with an exclusive or, and takes a rotation amount from the top 5 bits.
5. **Line 47:** the 32-bit value is rotated by that amount, so each call returns a scrambled value, not the state itself.

The calculation uses only integers, so the sequence depends on nothing but the seed. A `Random` made without a seed
starts as if seeded with 0, so every such generator gives the same sequence in every run. Seed from a fixed number for a
test, and from something that varies, such as the time, for variety. The program below uses the same step with large
start states, so that its first outputs are not zero.

```cpp sketch="basics-math-probability-pcg.cpp"
// A PCG32 generator like the SDK's Random, started from three seeds: equal seeds give equal numbers.
#include <cstdint>
#include <cstdio>

struct Pcg32
{
	uint64_t State = 0;

	uint32_t Next()
	{
		const uint64_t old = State;
		State = old * 6364136223846793005ull + 1442695040888963407ull;
		const uint32_t shifted = static_cast<uint32_t>(((old >> 18u) ^ old) >> 27u);
		const uint32_t rotation = static_cast<uint32_t>(old >> 59u);
		return (shifted >> rotation) | (shifted << ((32u - rotation) & 31u));
	}
};

int main()
{
	Pcg32 first{ 0x853c49e6748fea9bull }, second{ 0x853c49e6748fea9bull }, third{ 0x0123456789abcdefull };
	for (int draw = 0; draw < 3; draw++)
		std::printf("%10u %10u %10u\n", first.Next(), second.Next(), third.Next());
	return 0;
}
```

```text output-of="basics-math-probability-pcg.cpp"
 355248013  355248013  610837995
1055580183 1055580183 4242744859
3222338950 3222338950 2398997793
```

1. **Line 21:** the first two generators share a start state, and the third differs.
2. **Lines 22–23:** each draw prints one number from each generator, so equal states give equal columns and different states give unrelated ones.

:::why
Why does Strata ship its own generator, not the standard library's? A game replays a match, shares a level seed or tests
against fixed outcomes, so a seed must give the same numbers on every platform, compiler and SDK version. PCG32 does
that in a few lines of integer arithmetic. The cost is that it is unsafe for secrets such as passwords: never use it for
them.
:::

Raw outputs are whole numbers up to 4,294,967,295. `NextFloat` makes a uniform float in [0, 1): it keeps the top 24 bits
and multiplies by 2 to the power -24. A `float` holds 24 bits of precision, so every result is exact and never reaches 1.
`Chance(p)` returns whether `NextFloat()` is below $p$.

A random number in a range needs more care, because the obvious way is wrong. The obvious way is the remainder: `value
% 6` for a die. Take a generator with only 256 values, 0 to 255. Six does not divide 256: 256 = 42 × 6 + 4, so the
remainders 0 to 3 occur 43 times each and the remainders 4 and 5 only 42 times. The low faces win by 2.4 %.

A 32-bit generator makes the effect tiny for a die. It stays large for a wide range: for 3 billion values the remainders
below 1,294,967,296 occur twice as often as the rest. `Range` of the SDK removes the bias by drawing again.

```cpp src="StrataScriptCore/Include/StrataScript/Gameplay.h#L62-L70"
// Values below the threshold would make the low results more likely than the high ones: draw again.
const uint32_t bound = static_cast<uint32_t>(span);
const uint32_t threshold = static_cast<uint32_t>(0x100000000ull % bound);
for (;;)
{
	const uint32_t value = NextUInt();
	if (value >= threshold)
		return static_cast<int32_t>(static_cast<int64_t>(min) + static_cast<int64_t>(value % bound));
}
```

The lines run inside `Range`, after it has counted the possible results in `span`. For a span of 6, the threshold is the
remainder of 2 to the power 32 divided by 6, which is 4, and the values 0 to 3 are drawn again. The values left, from 4 to
4,294,967,295, number a multiple of 6, so each remainder occurs equally often. A draw is rejected with probability about
one in a billion, so the loop almost never repeats.

A second source of chance has no state: a hash of a position. Strata's output dither and grain draw their noise from
`PixelRandom` in `Strata/shaders/Include/Dither.slang`. It mixes the bits of the pixel's x and y and a stream number, and
keeps the top 24 bits as a uniform number. The same pixel and stream always give the same value, so the dither of a
still frame stays identical, and the shader needs no memory of the last pixel. The grain's stream number grows with the frame's
number, so it changes every frame, as film grain does.

## An integral is an area, and chance can estimate it

[Change over time](../basics/math-change.md) showed that the integral of a function from $a$ to $b$ is the area between
its graph and the axis, and that adding thin strips approaches it. That is all this page needs from integrals. Strips
work for one variable, but the lighting problems of a renderer have many, and the count of strips explodes. Chance does
not suffer from that.

## Monte Carlo integration averages random samples

**Monte Carlo integration** estimates an integral as the size of the range times the average of the function at random
points. A function's average height times the width of the range is the area, and a handful of random heights estimates
the average.

$$
\int_a^b f(x)\,dx \approx (b - a) \cdot \frac{1}{N} \sum_{i=1}^{N} f(x_i)
$$

$f$ is the function, and $x$ is its input. $a$ and $b$ are the ends of the range, and $x_i$ are $N$ points chosen
uniformly in it. $\int$ is read "the integral of", $d$ in $dx$ marks the thin strip of $x$ that is added up, and $\approx$
is read "is about".

:::example[The area under x squared by hand]
Take $f(x) = x^2$ on [0, 1], whose exact area is 1/3. Four random points are 0.1, 0.4, 0.7 and 0.9. The function there
is 0.01, 0.16, 0.49 and 0.81, with mean 0.3675. The range has size 1, so the estimate is 0.3675, close to 0.3333. More
points make it closer.
:::

Try it: estimate the area under $f(x) = x^2$ on [0, 2] from the points 0.25, 0.75, 1.25 and 1.75. The exact area is 2.67.

:::answer
The function values are 0.0625, 0.5625, 1.5625 and 3.0625, with mean 1.3125. The range has size 2, so the estimate is
2.625.
:::

How good is the method? Throw darts at a square of side 1 with a quarter circle of radius 1 drawn in it. The circle's
area is $\pi / 4$. The function is 1 where a dart lands inside and 0 outside, so its average is the share of darts
inside, and four times that share estimates $\pi$.

```cpp sketch="basics-math-probability-darts.cpp"
// Throws random darts at the unit square; the share inside the quarter circle, times 4, estimates pi.
#include <cmath>
#include <cstdio>
#include <random>

int main()
{
	std::mt19937 generator(1);
	std::uniform_real_distribution<double> unit(0.0, 1.0);
	int inside = 0;
	for (int dart = 1; dart <= 1000000; dart++)
	{
		const double x = unit(generator);
		const double y = unit(generator);
		if (x * x + y * y < 1.0)
			inside++;
		if (dart == 100 || dart == 10000 || dart == 1000000)
		{
			const double estimate = 4.0 * inside / dart;
			std::printf("%8d darts: %.4f, error %.4f\n", dart, estimate, std::fabs(estimate - 3.14159265));
		}
	}
	return 0;
}
```

```text output-of="basics-math-probability-darts.cpp"
     100 darts: 3.3200, error 0.1784
   10000 darts: 3.1568, error 0.0152
 1000000 darts: 3.1399, error 0.0017
```

1. **Lines 13–15:** a dart is two uniform numbers, and it is inside when $x^2 + y^2$ is below 1.
2. **Line 19:** four times the share inside estimates $\pi$.

::figure{id=darts}

Each dart counts 1 with probability $p = \pi / 4 = 0.785$, and a value of 0 or 1 has variance $p (1 - p)$, about 0.17, so the estimate of $\pi$ has standard deviation $4 \sqrt{0.17 / N}$,
which is $1.64 / \sqrt{N}$. At 100 darts that is 0.16, at 10,000 it is 0.016, and at a million 0.0016: the output's errors
are of that size.

The error falls as one over the square root of the count: a hundred times more darts give ten times less error. The
method is slow, and its rate does not depend on the number of dimensions. That is why renderers use it for light.

## Importance sampling puts samples where the function is large

Uniform points waste effort where the function is small. **Importance sampling** draws points more often where the function
is large, and divides each sample by its density so that the estimate stays correct.

$$
\int_a^b f(x)\,dx \approx \frac{1}{N} \sum_{i=1}^{N} \frac{f(x_i)}{p(x_i)}
$$

$p$ is the probability density of the points: it is 1 / (b - a) for uniform points, and then the formula is the one
above. $f(x_i) / p(x_i)$ is read "f at the point, divided by the density there".

The example is a function with a :term[cosine]{id=cosine} in it: $f(x) = \cos x \,(1 + \sin x / 2)$ from 0 to $\pi / 2$. Its exact area is
1.25. Choose the density $p(x) = \cos x$, whose area over the range is 1, so it is a valid density. This is a density on
a line; cosine-weighted directions over a hemisphere are the business of [Directions and the
sphere](../basics/math-sphere.md).

To draw from it, take a uniform $u$ in [0, 1) and compute $x = \arcsin u$, the angle whose :term[sine]{id=sine} is $u$. The probability that $x$ is below a value $t$
is the area of $p$ up to $t$, which is $\sin t$, and that is the probability that $u$ is below $\sin t$. Here $f / p = 1 +
\sin x / 2$, which hardly varies. The program measures the spread of single samples both ways.

```cpp sketch="basics-math-probability-importance.cpp"
#include <cmath>
#include <cstdio>
#include <random>
void Report(bool weighted)
{
	const double halfPi = 1.5707963267948966;
	std::mt19937 generator(7);
	double sum = 0.0, squares = 0.0;
	for (int sample = 0; sample < 100000; sample++)
	{
		const double unit = generator() / 4294967296.0;
		const double x = weighted ? std::asin(unit) : halfPi * unit; // Density cos(x), or uniform
		const double f = std::cos(x) * (1.0 + 0.5 * std::sin(x));
		const double value = weighted ? f / std::cos(x) : halfPi * f; // Divide by the density
		sum += value;
		squares += value * value;
	}
	const double mean = sum / 100000;
	std::printf("%s: mean %.4f, spread %.4f\n", weighted ? "importance" : "uniform   ", mean, std::sqrt(squares / 100000 - mean * mean));
}
int main()
{
	Report(false);
	Report(true);
}
```

```text output-of="basics-math-probability-importance.cpp"
uniform   : mean 1.2485, spread 0.5217
importance: mean 1.2503, spread 0.1445
```

1. **Line 12:** the point is uniform, or comes from the cosine density through the inverse :term[sine]{id=sine}.
2. **Line 14:** the weighted sample is divided by the density, here $\cos x$, so the average is still the area.
3. **Line 19:** both means are near 1.25, and the spread of the importance samples is 0.14 against 0.52.

Both estimates have the right mean, but the spread, and so the error of an average, is smaller by a factor of 3.6.
Reaching the same error with uniform points takes 13 times as many. Cosine weighting is a usual choice for light,
because light on a surface is weighted by a cosine. Strata's irradiance pass feeds cosine-shaped directions to each
point of an environment map's irradiance.

A mistake to avoid: omit the division, and the average is a different integral. Here it would be the area of
$f \cdot p$, which is 0.95, not 1.25, and the image would be wrong.

## A low-discrepancy sequence covers the range evenly

Random points clump and leave gaps, and the error of a Monte Carlo estimate partly comes from that. A **low-discrepancy
sequence** is a list of points made to cover the range more evenly than random ones, usually with no randomness at all.

A cheap cure keeps some randomness. **Stratified sampling** cuts the range into equal cells and puts one random point in
each cell. No cell is empty and none holds two.

:::example[Sixteen samples of a ramp]
Estimate the mean of $f(x) = x$ on [0, 1], which is 0.5, from 16 points. A uniform number has standard deviation
0.2887, so random points give an error of about 0.2887 / 4 = 0.072. With one point in each of 16 cells of width 1/16, each
point has a standard deviation of only 0.2887 / 16 = 0.018 inside its cell. The mean of 16 independent such points divides
that by $\sqrt{16}$: 0.0045.
:::

Try it: how many random points does plain sampling need to reach the error 0.0045?

:::answer
The error 0.2887 / $\sqrt{N}$ equals 0.0045 when $\sqrt{N}$ = 64, so $N$ = 4,096 points, against 16 for the stratified set.
:::

The second cure is a rule. The **Hammersley sequence**, or set, of $N$ points gives point $i$ the coordinates ($i / N$, the
bits of $i$ reversed). Reversing means that the bits are read from the other end and placed after the binary point, the
radical inverse of [Numbers in a computer](../basics/numbers.md). The index 6 is 110, and 0.011 in binary is 0.25 + 0.125 =
0.375.

```cpp sketch="basics-math-probability-hammersley.cpp"
// The Hammersley set of 8 points: x counts up, y is the index with its bits reversed.
#include <cstdint>
#include <cstdio>

double Reversed(uint32_t index)
{
	uint32_t bits = 0;
	for (int bit = 0; bit < 32; bit++)
		bits |= ((index >> bit) & 1u) << (31 - bit);
	return bits / 4294967296.0;
}

int main()
{
	for (uint32_t index = 0; index < 8; index++)
		std::printf("index %u: x = %u / 8 = %.3f, y = %.3f\n", index, index, index / 8.0, Reversed(index));
	return 0;
}
```

```text output-of="basics-math-probability-hammersley.cpp"
index 0: x = 0 / 8 = 0.000, y = 0.000
index 1: x = 1 / 8 = 0.125, y = 0.500
index 2: x = 2 / 8 = 0.250, y = 0.250
index 3: x = 3 / 8 = 0.375, y = 0.750
index 4: x = 4 / 8 = 0.500, y = 0.125
index 5: x = 5 / 8 = 0.625, y = 0.625
index 6: x = 6 / 8 = 0.750, y = 0.375
index 7: x = 7 / 8 = 0.875, y = 0.875
```

1. **Lines 8–9:** each of the 32 bits moves to the opposite end, and the result divided by 2 to the power 32 is a fraction below 1.
2. **Line 16:** the first coordinate counts up, and the second jumps between halves: 0, 0.5, 0.25, 0.75 and so on.

The jump is the point. The second coordinate visits the halves, then the quarters, then the eighths, so every prefix of
the sequence is spread over the square.

Strata's shaders compute the pair in one line. They are written in Slang, a shader language close to C++ with a few
differences. `float2` is a pair of floats, `uint` is an unsigned 32-bit integer, `float(...)` converts, and `reversebits`
is a built-in bit reversal. The function `Hammersley` of `Strata/shaders/Include/IBL.slang` takes the index and the
count and returns `float2(float(index) / float(count), float(reversebits(index)) * 2.3283064365386963e-10)`. Its first
value is the index over the count; its second is the index with its 32 bits reversed, times 2.3283064365386963e-10,
which is 1 / 2 to the power 32.

The renderer feeds these points to the cosine sampler for the irradiance of an environment map, and to the sampler that
builds the light table described in [Light energy](../light/energy.md).

::figure{id=hammersley}

## Noise is random values, white or blue

**Noise** is a stream of values that looks random: no pattern, no trend. Sample positions and per-pixel values are
noise.

**White noise** draws each value independently, like the dice. Its points clump and leave holes, and in frequency terms
it has equal strength at every frequency, as [Signals](../basics/signals.md) describes them.

**Blue noise** avoids close neighbors. No two points are very near, but no big hole appears either, which is a mix of
order and chance. Its strength at low frequencies is nearly gone and the rest lies at high frequencies. That is why blue
noise looks finer: an error made of tiny, quickly changing values disappears under any blur or squint, while white
noise leaves patches of every size.

::figure{id=white-blue}

Strata keeps a table of blue noise, 64 × 64 :term[byte]{id=byte} values, made by `Tools/GenerateBlueNoise.py` with the method of void and
cluster. The tool starts from random points, moves a point from its tightest cluster into the largest void until that
move would put it back. It then ranks every cell: the points by taking them out of the tightest clusters, the empty cells
by filling the largest voids.

Each value from 0 to 255 appears exactly 16 times. The sun's shadow filter reads the table by pixel position, repeated
every 64 pixels, and the table does not change from frame to frame.

:::why
Why a table and not a formula? Blue noise has no short formula, but the table costs one read per pixel. A table fixed
in time also means that nothing flickers and that a still image is the same on every run.
:::

## Disk patterns spread taps over a circle

A soft shadow averages taps of the shadow map inside a disk. Where should the taps go?

The **Vogel disk** puts tap $i$ of $N$ on a spiral, at radius $\sqrt{(i + 0.5) / N}$ and at angle $i$ times the golden
angle, 2.39996 :term[radians]{id=radian}, which is 137.5 degrees. The root keeps the density even: each tap owns the same area. The golden
angle never lines taps up in spokes, because no number of turns by it returns to the start. The table lists the four
taps of a disk with $N = 4$; the figure draws $N = 32$.

| Tap | Radius | Angle in degrees | Point |
| --- | --- | --- | --- |
| 0 | 0.354 | 0 | (0.354, 0.000) |
| 1 | 0.612 | 137.5 | (-0.452, 0.414) |
| 2 | 0.791 | 275.0 | (0.069, -0.788) |
| 3 | 0.935 | 52.5 | (0.569, 0.742) |

::figure{id=vogel-spiral}

Strata's sun shadow filter uses this disk in `Strata/shaders/Include/Shadows.slang`. It turns the disk at each pixel by
a blue-noise value, which changes the banding of a fixed pattern into fine grain.

**Poisson disk sampling** is the other way: it picks random points but rejects any that lie closer than a set distance to
a kept one. The result is irregular, like noise, and free of clumps. Strata's local-light shadows use a fixed table of 16
such taps in `Strata/shaders/Include/LocalShadows.slang`, turned at each pixel.

## Interleaved gradient noise costs one line

Blue noise needs a table. **Interleaved gradient noise** (IGN) computes a per-pixel value from the pixel's position alone,
and neighbors get values that differ evenly.

```slang src="Strata/shaders/Include/Common.slang#L41-L46"
// Per-pixel noise in [0, 1) whose neighbors differ evenly (interleaved gradient noise): screen-space reflections' start
// offsets, turned each frame by TemporalParams.z.
float InterleavedGradientNoise(float2 pixel)
{
	return frac(52.9829189 * frac(dot(pixel, float2(0.06711056, 0.00583715))));
}
```

`frac` is the part of a number after its point, `float2` holds a pixel's x and y, and `dot` multiplies two pairs and
adds. The function adds the pixel's x times 0.06711056 to its y times 0.00583715, takes the part after the point,
multiplies it by 52.98 and takes the part after the point again.

For pixels (0, 0) to (3, 0) the value is 0, 0.556, 0.111, 0.667: each step right adds 0.556, wrapping at 1. Each step
down adds 0.309. A slope that wraps is a gradient, and the large constant makes the wrapping fast, so neighbors never
match and the values spread evenly. Strata uses it for the start offset of screen-space reflection rays, shifted by a
value that changes every frame.

## Common mistakes

- **`rand() % n` for a range.** Symptom: low results appear a little more often. Fix: draw again below a threshold, as
  `Range` does.
- **A seed from the clock in a test.** Symptom: a test that passes on some runs and fails on others. Fix: seed from a
  fixed number, and take the seed from the clock only in play.
- **A Monte Carlo estimate not divided by its density.** Symptom: an image that is too dark or too bright in places. Fix:
  divide each sample by the density it was drawn from.
- **White noise where blue noise is wanted.** Symptom: uneven grain or clumped samples. Fix: use a blue-noise table or a
  pattern.
- **A generator seeded again every frame.** Symptom: the same "random" number every frame. Fix: seed once, in `OnCreate`, the function a script runs once when it starts.

## Summary

- Probability counts equally likely cases; add exclusive cases and multiply independent events.
- The expected value is the mean, the variance is the mean of squared distances, and the standard deviation is its square root.
- A seed fixes a generator's sequence, and `Range` draws again to avoid a biased remainder.
- Monte Carlo averages random samples divided by their density, and its error falls as one over the square root of the count.
- Spread samples with stratified offsets, the Hammersley set, Vogel or Poisson disks and blue noise; IGN makes a cheap per-pixel value.

## Check yourself

1. Two independent dice are rolled. Which is the probability that both are even?

   - A. 1/2
   - B. 1/4
   - C. 1/36
   - D. 1/6

   :::answer{tests="probability-rules"}
   B. Each die is even with probability 1/2, and independent events multiply: 1/4. Answer A adds the two instead.
   :::

2. A script calls `Seed(5)` on its generator in `OnUpdate`, which runs every frame, then `NextFloat()`. What does it see over three frames?

   :::answer{tests="seeded-generator"}
   The same number every frame, because the seed starts the sequence again each time. Seed once, in `OnCreate`.
   :::

3. A dart estimate is off by 0.05 with 400 darts. About how far off is it with 1,600?

   :::answer{tests="monte-carlo"}
   Four times the darts halve the error: 0.025.
   :::

4. The offsets of a shadow filter must look like fine grain, not patches. White noise or blue noise?

   :::answer{tests="sample-patterns"}
   Blue noise. Its values at neighboring pixels differ, so the error is fine; white noise leaves patches.
   :::

5. Compute the standard deviation of 3, 5, 5, 7.

   :::answer{tests="mean-spread"}
   The mean is 5, the squared distances are 4, 0, 0 and 4, the variance is 2, and the standard deviation is 1.41.
   :::

## Practice

1. **Basic.** Two dice are rolled. Compute the probability of a sum of at least 10, and of at least one six.

   :::answer[Worked solution]{tests="probability-rules"}
   Sums 10, 11 and 12 have 3 + 2 + 1 = 6 pairs, so the probability is 6/36 = 1/6. At least one six has 1 - 25/36 = 11/36.
   :::

2. **Basic.** For `Range(1, 6)` the threshold is 4. How many of the 2 to the power 32 values does the loop accept, and why does each face then occur equally often?

   :::answer[Worked solution]{tests="seeded-generator"}
   The values 4 to 4,294,967,295 are accepted: 4,294,967,292 of them, which is 6 × 715,827,882. Each remainder from 0 to 5 therefore appears 715,827,882 times.
   :::

3. **Basic.** Compute the value of interleaved gradient noise for pixel (2, 1).

   :::answer[Worked solution]{tests="sample-patterns"}
   The dot is 2 × 0.06711056 + 0.00583715 = 0.14005827. Times 52.9829189 is 7.4207, and the part after the point is 0.42.
   :::

4. **Medium.** Estimate the area under $x^2$ on [0, 1] with importance sampling. The density is $p(x) = 2x$, and the uniform numbers $u$ = 0.25 and 0.64 give the points $x = \sqrt{u}$.

   :::answer[Worked solution]{tests="monte-carlo"}
   The points are 0.5 and 0.8. $f / p = x^2 / 2x = x / 2$ gives 0.25 and 0.4, with mean 0.325, against the exact 0.333.
   :::

5. **Medium.** Find the Vogel point for tap 2 of 4 by hand.

   :::answer[Worked solution]{tests="sample-patterns"}
   The radius is $\sqrt{2.5 / 4}$ = 0.791 and the angle is 2 × 137.5 = 275 degrees. The point is (0.791 cos 275°, 0.791 sin 275°) = (0.069, -0.788).
   :::

6. **Hard.** Optional, on your [Coin Run](../make/project-coin-run.md) or Checkpoint 4 of [Ship the finished game](../make/project-coin-run.md#ship-the-finished-game). Write a new script, `RandomCoin`, for one coin. It places the coin at random from a `Seed` and a `Number` field, and makes it gold with `Chance(0.25)`. Then count the gold coins over 1,000 seeds and compare the count with the expected value.

   :::answer[Worked solution]{tests="seeded-generator monte-carlo" solution="sketches/basics-math-probability-coins.cpp"}
   The script seeds once and draws three numbers, so one `Seed` always gives the same level.

   ```cpp pseudocode
   class RandomCoin : public Script
   {
   public:
   	int32_t Seed = 1;
   	int32_t Number = 0;
   	bool IsGold = false;

   	void OnCreate() override
   	{
   		Random random(static_cast<uint64_t>(Seed) * 1000u + static_cast<uint64_t>(Number));
   		GetTransform().SetWorldPosition(glm::vec3(random.Range(-10.0f, 10.0f), 0.5f, random.Range(-10.0f, 10.0f)));
   		IsGold = random.Chance(0.25f);
   	}
   };
   ```

   1. **Line 10:** one generator per coin, seeded from the level's `Seed` and the coin's `Number`, so a coin never depends on the others.
   2. **Line 11:** two `Range` calls choose the x and z of the position; the height stays 0.5.
   3. **Line 12:** `Chance(0.25)` is true for a quarter of the draws, which makes the coin gold.

   The program below does the counting. It uses a standard generator, since a program of its own cannot use the SDK. With 20 coins per level the expected value is 5,000, and the standard deviation of the count is about 61, so a result within two standard deviations of 5,000 is normal.

   ```cpp sketch="basics-math-probability-coins.cpp"
   // Makes 1,000 levels of 20 coins; each coin is gold with chance 0.25. Counts the gold coins over all seeds.
   #include <cstdio>
   #include <random>

   int main()
   {
   	const int coinsPerLevel = 20;
   	int gold = 0;
   	for (int seed = 1; seed <= 1000; seed++)
   	{
   		std::mt19937 generator(seed);
   		std::uniform_real_distribution<float> unit(0.0f, 1.0f);
   		for (int coin = 0; coin < coinsPerLevel; coin++)
   			if (unit(generator) < 0.25f)
   				gold++;
   	}
   	std::printf("gold coins: %d, expected value %.0f\n", gold, 1000 * coinsPerLevel * 0.25);
   	return 0;
   }
   ```

   ```text output-of="basics-math-probability-coins.cpp"
   gold coins: 5080, expected value 5000
   ```

   1. **Line 9:** each seed is one level.
   2. **Lines 11–12:** the generator starts again from the level's seed, so the level is the same on every run.
   3. **Line 14:** a coin is gold when the uniform number is below 0.25.
   :::

## Where the book uses it

- [Directions and the sphere](../basics/math-sphere.md) uses densities and Monte Carlo estimates to integrate over directions.
- [Reflectance](../light/reflectance.md) uses sampled estimates of light that leaves a surface.
- [Light energy](../light/energy.md) uses Monte Carlo and the Hammersley set to fill its table.
- [Sun shadows](../light/sun-shadows-2.md) uses the Vogel disk turned by blue noise.
- [Indirect light](../indirect/problem.md) uses estimates made from random samples.

## Further reading

- Pharr, Jakob and Humphreys, "Physically Based Rendering", the chapter on Monte Carlo integration; advanced.
- Melissa O'Neill, "PCG: A Family of Better Random Number Generators", the paper behind the generator; intermediate.
- [C++ random number library](https://en.cppreference.com/w/cpp/numeric/random): the standard generators used in this page's programs; intermediate.
