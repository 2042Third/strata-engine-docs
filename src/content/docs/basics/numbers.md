---
id: basics/numbers
title: "Numbers in a computer: binary, integers, floating point and precision"
description: "How a computer stores whole numbers and fractions in bits, why a float loses precision far from zero, and what powers, logarithms and exp are."
kind: primer
size: L
tracks: [B, E]
needs: [basics/computer, basics/programming-1]
time: 90
learn:
  - id: binary-hex
    text: compute a number between binary, decimal and hexadecimal, and name what a bit and a byte are
  - id: integers
    text: choose an integer type by its range and predict an overflow and a division with a negative number
  - id: bit-masks
    text: write masks that set, clear and test a bit, and shifts that pack two numbers into one integer
  - id: floating-point
    text: explain how a float stores a number, why the gap between floats grows and why 0.1 + 0.2 is not 0.3
  - id: logarithms
    text: compute powers of two, logarithms, exposure stops, decibels and a decay with the exponential function
status: final
---

::::test-out

1. Write 13 in binary, and write 0xFF in decimal.

   :::answer{tests="binary-hex"}
   13 is 8 + 4 + 1, so its binary form is 1101. 0xFF is F × 16 + F = 15 × 16 + 15 = 255.
   :::

2. A `uint8_t` holds 250, and the program adds 10 and stores the result back. What does it hold? What does `-9 / 2`
   give in C++?

   :::answer{tests="integers"}
   The type holds 4: 260 is 4 more than the 256 values the type has, so the count wraps around. `-9 / 2` gives -4, because
   the division drops the fraction toward zero: -4.5 becomes -4.
   :::

3. The variable `flags` holds `0b0101`. Write one line that sets bit 1, and give the value afterwards.

   :::answer{tests="bit-masks"}
   `flags |= 1u << 1;` sets the bit. Bit 1 is the second place from the right, worth 2, so the value is `0b0111`, which is 7.
   :::

4. In `double`, is `0.1 + 0.2 == 0.3` true or false? How do you compare the two numbers instead?

   :::answer{tests="floating-point"}
   False: neither 0.1 nor 0.2 has an exact binary form, and their sum lands on a neighbour of the double 0.3. Compare
   the distance with a small limit: `std::abs(sum - 0.3) < 1e-9`.
   :::

5. A texture is 1,024 pixels wide. How many times can you halve it before it is 1 pixel wide?

   :::answer{tests="logarithms"}
   10 times. This is the base-2 logarithm of 1,024, because 2 multiplied by itself 10 times is 1,024.
   :::

::::

## Why you will need this

Everything in a game is a number: the coins you collect, the seconds on the clock, the position of the ball, the red
of a pixel. Each number lives in a fixed number of bits, grouped in :term[bytes]{id=byte}, and the choice of that size decides what the game can say.
A clock that looks right for a minute can drift after five hours, and a flag stored in one bit can be tested in a
single instruction.

Other pages build on this one. [Bytes](../basics/bytes.md) reads numbers out of files. [Color](../basics/color.md)
stores light in 8 and 16 bits. [Interpolation](../basics/math-interpolation.md) smooths motion with the exponential
function. [Temporal anti-aliasing](../image/taa.md) uses the digits-backwards numbers of this page, and
[Entities and components](../world/ecs.md) packs two numbers into one.

The page goes from the smallest idea, one switch, up to the numbers of a physical scene. Each idea has a small example by hand first, and the code comes after it. The questions and exercises at the end let you test yourself.

## A computer counts with two digits

You count in tens, and each place of a number is worth ten times the place to its right. In 305, the 3 stands for
3 × 100, the 0 for no tens and the 5 for 5 ones.

A computer's memory is a long row of switches that are on or off. A **bit** is one such switch: a digit that is 0 or 1.
[The computer](../basics/computer.md) shows memory as numbered bytes, and a byte is eight bits.

Counting with only the digits 0 and 1 is **binary**, also called base 2. The rule is the one of your tens: each place is worth twice the place to its right.

| Place worth | 8 | 4 | 2 | 1 | Number |
| --- | --- | --- | --- | --- | --- |
| Zero | 0 | 0 | 0 | 0 | 0 |
| One | 0 | 0 | 0 | 1 | 1 |
| Two | 0 | 0 | 1 | 0 | 2 |
| Three | 0 | 0 | 1 | 1 | 3 |
| Five | 0 | 1 | 0 | 1 | 5 |
| Eight | 1 | 0 | 0 | 0 | 8 |
| Fifteen | 1 | 1 | 1 | 1 | 15 |

To count, add 1 and carry: 0111 plus 1 is 1000, as 999 plus 1 is 1000 in tens. A **power** multiplies a number by
itself several times: $2^8$, read "two to the power eight", is eight 2s multiplied, which is 256. Eight bits give $2^8$
different patterns, and their numbers run from 0 to 255.

:::example[13 written in binary]
Take the largest place worth at most the number, subtract it, and repeat with what is left. The places are 1, 2, 4, 8,
16 and so on. The largest at most 13 is 8, and 13 - 8 = 5. The largest at most 5 is 4, and 5 - 4 = 1. The last is 1.

So 13 = 8 + 4 + 1, and the places 8, 4, 2, 1 hold 1, 1, 0, 1. The binary form is 1101. To check it, add the places that
hold a 1: 8 + 4 + 0 + 1 = 13.
:::

Try it: write 100 in binary.

:::answer
The largest place at most 100 is 64, and 100 - 64 = 36. Then 32 fits, and 36 - 32 = 4, and the last is 4. The places
64, 32 and 4 hold a 1: 1100100.
:::

A power also has a name for its small raised number. In $2^8$ the 8 is the **exponent**: how many times the base 2 is
multiplied. A group of $n$ bits holds $2^n$ patterns, from 0 to $2^n - 1$.

## Hexadecimal writes four bits with one digit

Binary is long: 255 is 11111111. **Hexadecimal**, or hex, is base 16 and writes four bits with one digit, because
16 is $2^4$. It needs sixteen digits, so after 0 to 9 it uses the letters A to F for 10 to 15. A hex number carries
the prefix `0x`, which tells a reader and the compiler which base follows.

| Binary | 0000 | 0001 | 1001 | 1010 | 1100 | 1111 |
| --- | --- | --- | --- | --- | --- | --- |
| Hex | 0 | 1 | 9 | A | C | F |
| Decimal | 0 | 1 | 9 | 10 | 12 | 15 |

:::example[0xC8 in decimal and in binary]
The places of a hex number are worth 1, 16, 256 and so on. In `0xC8`, C is 12 and 8 is 8, so the value is
12 × 16 + 8 = 200. Each digit also stands for four bits: C is 1100 and 8 is 1000, so 200 is 11001000.
:::

Try it: what are the decimal and the binary form of `0x2F`?

:::answer
2 × 16 + 15 = 47. The digit 2 is 0010 and F is 1111, so the bits are 00101111.
:::

Hex appears wherever bit patterns matter. A color such as `#FF8000` is three bytes: red `FF` (255), green `80` (128)
and blue `00` (0). :term[Memory addresses]{id=memory-address} and hash values are also written in hex, since two hex digits are exactly one byte.

Other bases work alike. Base 3 uses the digits 0, 1 and 2, and its places are worth 1, 3, 9, 27. There is one more trick with them.

Write a whole number in base $b$, then reverse its digits and put them behind a point. The number 3 is
11 in base 2, and reversed behind the point it is 0.11, which is 1/2 + 1/4 = 0.75. In base 3 the number 3 is 10, and
reversed it is 0.01, which is 1/9, or 0.111.

:::question[What are the lines of the program that I have not seen?]
The sketches use loops, functions and `return`, taught in [Programming 2](../basics/programming-2.md), and `#include`,
`std::cout` and calls such as `std::bit_cast(`, taught in [Programming 3](../basics/programming-3.md). Read each as a
shape and use the printed output to see what it does.
:::

This reversal is the **radical inverse**: the numbers 1, 2, 3, ... map to points of the range between 0 and 1 that
spread out evenly and never repeat. The sketch below computes it for the numbers 1 to 4 in base 2 and base 3.
Strata's `SceneRenderer::GetTemporalJitter` has the same loop. It turns the numbers 1 to 8 into small shifts of the
camera's image, which [temporal anti-aliasing](../image/taa.md) needs.

```cpp sketch="basics-numbers-radical.cpp"
// The digits of 1, 2, 3 and 4 written backwards behind the point, in base 2 and in base 3.
#include <cstdint>
#include <iostream>

float RadicalInverse(uint32_t index, uint32_t base)
{
	float result = 0.0f;
	float scale = 1.0f / static_cast<float>(base);
	for (; index > 0; index /= base)
	{
		result += static_cast<float>(index % base) * scale;
		scale /= static_cast<float>(base);
	}
	return result;
}

int main()
{
	for (uint32_t index = 1; index <= 4; index++)
		std::cout << index << ": " << RadicalInverse(index, 2) << " " << RadicalInverse(index, 3) << '\n';
	return 0;
}
```

```text output-of="basics-numbers-radical.cpp"
1: 0.5 0.333333
2: 0.25 0.666667
3: 0.75 0.111111
4: 0.125 0.444444
```

1. **Line 5:** `index` is the number whose digits are reversed, and `base` is 2 or 3.
2. **Lines 9–11:** the loop takes the last digit of `index` with `index % base` and drops it with `index /= base`.
3. **Line 12:** a digit gets the place value `scale`: one half, then one quarter, then one eighth, and so on.

The output matches the hand work: the number 3 gives 0.75 in base 2 and 0.111111 in base 3.

## Integers have a fixed size, so they have a fixed range

An **integer** is a whole number: positive, negative or zero. A computer cannot store an integer of any length, so
C++ names the types by their bits. `uint8_t` is an unsigned type of 8 bits and `int32_t` a signed type of 32 bits. The
name `int` alone is usually 32 bits, but the standard does not promise it, so code that needs a size uses these names.

An **unsigned integer** has no sign: all its bits count, and its range starts at 0. A signed integer spends one bit on the sign.

| Type | Bits | Smallest | Largest |
| --- | --- | --- | --- |
| `uint8_t` | 8 | 0 | 255 |
| `int8_t` | 8 | -128 | 127 |
| `uint16_t` | 16 | 0 | 65,535 |
| `int16_t` | 16 | -32,768 | 32,767 |
| `uint32_t` | 32 | 0 | 4,294,967,295 |
| `int32_t` | 32 | -2,147,483,648 | 2,147,483,647 |
| `uint64_t` | 64 | 0 | 18,446,744,073,709,551,615 |
| `int64_t` | 64 | -9,223,372,036,854,775,808 | 9,223,372,036,854,775,807 |

In code, `std::numeric_limits<int32_t>::max()` gives the largest value of a type, so you need not remember the table.
Sound shows why the sizes matter: a 16-bit sample is an `int16_t`, so a loud sound is a number up to 32,767 and a
quiet one is near 0. Strata's `AudioEngine` hands out the mix as 32-bit floats instead, the type of a later section.

Negative numbers need a code. The common one is **two's complement**: the top bit of an $n$-bit number counts as
$-2^{n-1}$ instead of $+2^{n-1}$. In 8 bits, 11111111 is -128 + 127 = -1, 10000000 is -128, and 01111111 is 127. To change the sign of a number, flip every bit and add 1: 5 is 00000101, so -5 is 11111010 + 1 = 11111011.

:::why
Computers use two's complement because one adding circuit then serves signed and unsigned numbers alike, and the
number zero has a single form. The cost is a range with one more negative number than positive ones.
:::

When a result lies beyond the range, **integer overflow** happens. An unsigned type wraps around: it keeps the
remainder after division by the number of values. A signed overflow is not allowed. The C++ standard calls it undefined
behavior, which [C++ memory](../basics/cpp-memory.md) explains, so never write code that relies on it.

:::example[A health counter wraps]
A `uint8_t` health of 200 takes a bonus of 100. The sum 300 is 44 more than the 256 values of the type, so the result
is 44. In the other direction, 0 minus 1 in a `uint8_t` is 255.
:::

Try it: a `uint8_t` holds 3, and the program subtracts 5. What does it hold?

:::answer
The result 3 - 5 = -2 is below the range, and the wrap adds 256: the type holds 254.
:::

## Integer division drops the fraction toward zero

In C++, `7 / 2` is 3: when both numbers are integers, the result is an integer and the fraction is dropped. The
remainder is `7 % 2`, which is 1. The two always agree: `(a / b) * b + a % b` is `a`.

With a negative dividend, the fraction is dropped toward zero, not downward: `-7 / 2` is -3, and `-7 % 2` is -1,
so the remainder takes the sign of the left number. Many tasks want the floor, the next whole number below. Dividing
-7 by 2 gives -3.5, whose floor is -4. A cell grid shows why it matters: with cells 10 m wide, a point at x = -5 m lies
in cell -1, but `-5 / 10` is 0, the cell of x = +5 m. Cell 0 would be twice as wide as the others.

Strata's global illumination code needs the floor for positions on its grid, which can be negative, so it has its own `FloorDivide`.

```cpp src="Strata/src/Strata/Renderer/GlobalIlluminationLayout.cpp#L17-L21"
int64_t FloorDivide(int64_t value, int64_t divisor)
{
	const int64_t quotient = value / divisor;
	return (value % divisor != 0 && (value < 0) != (divisor < 0)) ? quotient - 1 : quotient;
}
```

The function divides, then subtracts 1 when the remainder is not zero and the two numbers have different signs. The
world grid gets the same result with `std::floor` on a double: `ToCellCoordinate` in
`Strata/src/Strata/World/WorldGrid.cpp` floors the offset divided by the cell size.

The other common need is the round-up rule: how many boxes of size $b$ hold $a$ items? The expression `(a + b - 1) / b`
gives it. Ten items in boxes of 4 need `(10 + 3) / 4`, which is 3, and eight items need `(8 + 3) / 4`, which is 2. Both
rules hold only for a non-negative $a$ and a positive $b$: for a negative $a$, use a floor division first.

## A mask picks bits, and a shift moves them

A **bitwise operator** works on every bit place of its numbers at the same time, and it never carries from one place to
the next. `&` (and) gives 1 where both bits are 1, `|` (or) where at least one is, `^` (exclusive or) where exactly one is, and `~` flips every bit.

| Expression | In bits | Result |
| --- | --- | --- |
| `0b1100 & 0b1010` | 1100 and 1010 | `0b1000` |
| `0b1100 \| 0b1010` | 1100 or 1010 | `0b1110` |
| `0b1100 ^ 0b1010` | 1100 and 1010 differ | `0b0110` |
| `~0b00001100` (8 bits) | flip 00001100 | `0b11110011` |

A **bit mask** is a number whose 1 bits mark the places you care about. Four forms cover most needs, with `value` and
`mask` as unsigned numbers: `value & mask` keeps only the marked bits, `value |= mask` sets them, `value &= ~mask`
clears them, and `(value & mask) != 0` tests whether any is set. A number that uses its bits as separate yes-or-no
settings is a set of **bit flags**.

Strata keeps one for each of its 32 collision layers. `CollisionMasks[i]` holds one bit per layer, set when layer `i`
collides with that layer. The function below sets or clears a pair, and the mask `1u << layerA` is built by a shift,
which the next part explains.

```cpp src="Strata/src/Strata/Scene/PhysicsLayerSettings.h#L43-L59"
void SetCollide(uint32_t layerA, uint32_t layerB, bool collide)
{
	if (layerA >= c_PhysicsLayerCount || layerB >= c_PhysicsLayerCount)
		return;
	const uint32_t bitA = 1u << layerA;
	const uint32_t bitB = 1u << layerB;
	if (collide)
	{
		CollisionMasks[layerA] |= bitB;
		CollisionMasks[layerB] |= bitA;
	}
	else
	{
		CollisionMasks[layerA] &= ~bitB;
		CollisionMasks[layerB] &= ~bitA;
	}
}
```

1. **Lines 47–48:** each layer's bit is a 1 moved to the place of the layer number.
2. **Lines 51–52:** `|=` sets the bit of one layer in the mask of the other, so the pair collides both ways.
3. **Lines 56–57:** `&= ~` clears it: `~` turns the one-bit mask into one that has every bit but that one.

A **bit shift** moves all the bits of a number. `x << n` moves them $n$ places up and fills with zeros, which multiplies
by $2^n$: `5 << 2` is 20. `x >> n` moves them down and drops the lowest,
which divides by $2^n$ and rounds down: `100 >> 3` is 12. A shift count at or beyond the number of bits is undefined, and `1u << 5` is 32.

Shifts also count halvings. A texture of 1,024 pixels has a chain of smaller copies, each half the size of the one before,
and Strata counts the copies like this:

```cpp src="Strata/src/Strata/Renderer/Texture.cpp#L856-L866"
uint32_t CalculateMipCount(uint32_t width, uint32_t height)
{
	uint32_t levels = 1;
	uint32_t size = std::max(width, height);
	while (size > 1)
	{
		size >>= 1;
		levels++;
	}
	return levels;
}
```

1. **Line 859:** the number to halve is the longer side.
2. **Lines 860–864:** each round halves `size` with `>>= 1` and counts a level, until the size is 1.
3. **Line 865:** a size of 1024 gives 10 halvings and so 11 levels.

Shifts and masks also pack two numbers into one integer. Strata's entity handle is 32 bits wide: the low 20 bits hold
an index and the high 12 bits a version, which the entity system raises when an index is used again. An old handle then differs from a new one. [Entities and components](../world/ecs.md) shows it at work.

:::example[Pack an index of 5 and a version of 3]
Shift the version up by 20 places, which gives 3 × 1,048,576 = 3,145,728, and add the index with `|`: the handle is
3,145,733. To take the index out, keep the low 20 bits with the mask `0xFFFFF`, which is twenty 1 bits: 5. To take the
version out, shift down by 20 places: 3.
:::

The sketch below does the same in code, and also finds the number of zero bits below the lowest 1 bit with
`std::countr_zero`: the number 40 is 101000, so there are 3. A word of 64 bits can then be walked bit by bit: the
expression `bits &= bits - 1` clears the lowest 1 (101000 minus 1 is 100111, and `&` leaves 100000). Strata's physics
code visits the moved bodies of a frame this way in `Strata/src/Strata/Physics/PhysicsWorld.cpp`.

```cpp sketch="basics-numbers-pack.cpp"
// Two numbers packed into one 32-bit integer and taken out again, and the zeros below the lowest set bit.
#include <bit>
#include <cstdint>
#include <iostream>

int main()
{
	const uint32_t index = 5;
	const uint32_t version = 3;
	const uint32_t handle = (version << 20) | index;
	std::cout << "handle: " << handle << '\n';
	std::cout << "index: " << (handle & 0xFFFFF) << '\n';
	std::cout << "version: " << (handle >> 20) << '\n';
	std::cout << "trailing zeros of 40: " << std::countr_zero(40u) << '\n';
	return 0;
}
```

```text output-of="basics-numbers-pack.cpp"
handle: 3145733
index: 5
version: 3
trailing zeros of 40: 3
```

1. **Line 10:** the version moves up 20 places, and `|` adds the index in the empty low places.
2. **Line 12:** the mask `0xFFFFF` keeps the low 20 bits: the index.
3. **Line 13:** the shift `>> 20` drops the low 20 bits and leaves the version.
4. **Line 14:** `std::countr_zero(40u)` counts the zeros below the lowest 1 of 101000.

The handle prints as 3145733, and the two numbers come back out. One more use of shifts is **Morton order**:
mixing the bits of two numbers. For x = 5 (101) and y = 3 (011), take the bits of y and x in turn from the top:
0 1, then 1 0, then 1 1. The result is 011011, which is 27. Points that are close in a grid usually get close Morton numbers,
so a list sorted by them keeps neighbours near each other.

## A float stores a sign, an exponent and a significand

Whole numbers do not hold 0.15625 or a distance of a billion metres. Scientists write a big or small number as digits
times a power of ten: $6.02 \times 10^{23}$. A **floating-point number**, in short a float, does the same in base 2: a sign, a
power of two that moves the point, and the digits. The formats come from the standard 754 of the Institute of Electrical and Electronics Engineers (IEEE).

A `float` has 32 bits: 1 for the sign, 8 for the exponent and 23 for the **significand**, the digits after the leading
one. A `double` has 64 bits: 1, 11 and 52. For a float, the value is

$$v = (-1)^s \times \left(1 + \frac{m}{2^{23}}\right) \times 2^{e-127}$$

$v$ is the value. $s$ is the sign bit, 0 or 1, so $(-1)^s$ is 1 for a positive number and -1 for a negative one. $m$ is
the 23 bits of the significand read as a whole number, and the fraction $m / 2^{23}$ lies from 0 up to a value below 1.
$e$ is the 8 bits of the exponent read as a whole number; subtracting 127 lets the power be negative. The leading 1 in
$1 + m / 2^{23}$ is not stored.

::figure{id=float-bits}

:::example[0.15625 as bits]
Write 0.15625 as 5/32, which is 101 divided by 100000 in binary: 0.00101. Move the point so one 1 stands before it:
$1.01 \times 2^{-3}$. The sign is 0, and the exponent field is -3 + 127 = 124, which is 01111100. The significand field holds the
digits behind the point, 01, followed by zeros. Joined, the 32 bits are 0 01111100 01000000000000000000000, which is
`0x3E200000` in hex.
:::

The sketch reads the bits of three floats with `std::bit_cast`, which copies a value's bits into another type, and
prints them in three groups.

```cpp sketch="basics-numbers-floatbits.cpp"
// The 32 bits of three floats, split into the sign, the exponent field and the significand field.
#include <bit>
#include <bitset>
#include <cstdint>
#include <iostream>
#include <string>

int main()
{
	const float values[] = { 0.15625f, 1.0f, -2.5f };
	for (const float value : values)
	{
		const std::bitset<32> bits(std::bit_cast<uint32_t>(value));
		const std::string text = bits.to_string();
		std::cout << value << ": " << text.substr(0, 1) << " " << text.substr(1, 8) << " " << text.substr(9) << '\n';
	}
	return 0;
}
```

```text output-of="basics-numbers-floatbits.cpp"
0.15625: 0 01111100 01000000000000000000000
1: 0 01111111 00000000000000000000000
-2.5: 1 10000000 01000000000000000000000
```

1. **Line 13:** `std::bit_cast` copies the float's 32 bits into an integer, and `std::bitset` prints them.
2. **Line 15:** the string is cut into 1, 8 and 23 characters: the sign, the exponent field and the significand field.

The first line matches the hand work. The number 1 has the exponent field 01111111, which is 127, so its power is
$2^0$. The number -2.5 is $-1.25 \times 2^{1}$: the sign is 1 and the exponent field is 10000000.

## The gap between floats grows with the number

The significand has 23 bits whatever the exponent is, so each doubling, such as 1 to 2 or 16,384 to 32,768, holds the
same number of floats: $2^{23}$, about 8.4 million. A wider range holds the same count, so the floats lie further apart.
The **precision** of a type is how finely it tells neighbours apart, and for floats it is relative: about 7 decimal
digits for a `float` and about 15 for a `double`.

The gap between a float and the next one is

$$g = 2^{k-23}$$

where $g$ is the gap in the unit of the number, and $k$ is the exponent of the largest power of two at or below the
number. For a `double` the 23 becomes 52. If one unit is one metre, the gaps are:

| Distance | Float gap | Double gap |
| --- | --- | --- |
| 1 m | 0.00000012 m | 0.00000000000000022 m |
| 1,000 m (1 km) | 0.000061 m (0.06 mm) | 0.00000000000011 m |
| 20,000 m (20 km) | 0.00195 m (about 2 mm) | 0.0000000000036 m |
| 16,777,216 m | 2 m | 0.0000000037 m |

::figure{id=float-gaps}

At 16,777,216, which is $2^{24}$, a `float` can no longer hold every whole number: the gap is 2, so 16,777,217 does not
exist. A model at 20 km from the origin can move only in steps of 2 mm in a `float`, and a shaking mesh is the visible
sign. Strata therefore subtracts the camera's position in `double` before it sends positions to the :term[graphics card]{id=gpu}, a
topic of [Camera-relative rendering](../draw/mirrors-camera-relative.md).

Time has the same problem. A game that counts seconds in a `float` loses precision as the count grows. The `Time` class of scripts gives the delta time as a `float`, which is small and precise. It gives the seconds since the scene started as a `double`: `Time::GetDeltaTime()` and `Time::GetElapsedTime()` have those types.

:::example[A float clock after hours]
Coin Run's clock adds one frame, 1/60 s or 0.016667 s, each frame. At 16,384 s, 4.55 hours in, the gap is 0.00195 s, and
the frame is 8.53 gaps. The sum rounds to 9 gaps, 0.017578 s: the clock runs 5.5 % fast. At 32,768 s, 9.1 hours in, the
gap is 0.0039 s, the frame is 4.27 gaps, the sum adds 4 gaps, 0.015625 s, and the clock runs 6.3 % slow.

At 524,288 s, about 146 hours in, the gap is 0.0625 s. The frame is less than half a gap, so the sum rounds back to the
same number: the clock stops. A `double` has a gap of about 0.0000000001 s there, and no game will see it.
:::

Try it: at 1,000 s, is the gap of a float larger than 0.1 ms (0.0001 s)?

:::answer
The number 1,000 lies from 512 to 1,024, so $k = 9$ and the gap is $2^{-14}$, 0.000061 s, which is smaller than
0.0001 s. The gap is 0.061 ms.
:::

## Most decimal fractions have no exact binary form

The decimal 0.1 is one tenth. In binary it is 0.000110011001100..., a pattern that repeats forever, as 1/3 does in
decimal. A float keeps only 24 significant bits, so it stores the nearest float and the stored value is not 0.1. The
difference between the true result and the stored one is a **rounding error**.

Some results are exact. These are whole numbers up to $2^{24}$ in a `float` and up to $2^{53}$ in a `double`, and any sum or product whose true result is a float. Halving and doubling only change the exponent, so they are exact too. The result of one operation is
always the float nearest to the true result.

The result of 0.1 + 0.2 is the clearest case. The stored 0.1 is slightly above one tenth, the stored 0.2 slightly above
a fifth, and their sum rounds to a float that is not the nearest one to 0.3. The sketch prints every digit.

```cpp sketch="basics-numbers-sum.cpp"
// Why 0.1 + 0.2 is not 0.3: every digit of the sum, and a comparison with a tolerance.
#include <cmath>
#include <iomanip>
#include <iostream>

int main()
{
	const double sum = 0.1 + 0.2;
	std::cout << std::setprecision(17) << std::boolalpha;
	std::cout << "0.1 + 0.2 = " << sum << '\n';
	std::cout << "equal to 0.3: " << (sum == 0.3) << '\n';
	std::cout << "difference: " << std::abs(sum - 0.3) << '\n';
	std::cout << "within 1e-9: " << (std::abs(sum - 0.3) < 1e-9) << '\n';
	return 0;
}
```

```text output-of="basics-numbers-sum.cpp"
0.1 + 0.2 = 0.30000000000000004
equal to 0.3: false
difference: 5.5511151231257827e-17
within 1e-9: true
```

1. **Line 8:** the sum is computed in `double`.
2. **Line 9:** `std::setprecision(17)` writes 17 digits, and `std::boolalpha` writes `true` and `false`.
3. **Line 13:** the tolerance test accepts a distance below 1e-9.

The difference is about $5.6 \times 10^{-17}$, far below any size a game can see, but `==` asks for equality of every bit, so it
says false. Compare with a **tolerance**, a small distance that counts as equal: `std::abs(a - b) < limit`. Choose
the limit from the numbers: 1e-9 suits sums near 1 in a `double`, and `float` needs a much larger one, about 1e-6.

Scripts log numbers with `Log::Info`, which writes six significant digits, so it shows the double sum as 0.3 and hides
the error. To see every digit, put the number in a string with `std::ostringstream` and `std::setprecision`: 9 digits
for a `float` and 17 for a `double` identify the float exactly. Then log the string.

Rounding also happens when you store a float in fewer bits on purpose. A color channel in the range 0 to 1 stored in 8
bits becomes the whole number `round(x * 255)`. The value 0.5 gives 127.5, which rounds to 128, and reading it back
gives 128 / 255 = 0.50196. The error is at most half a step, 1/510, or about 0.002. The name of this step is **quantizing**.

## Some floats are not numbers

A float has patterns that are not finite numbers. Dividing 1.0f by 0.0f gives positive **infinity**, written `inf`,
and a result above the largest float, about $3.4 \times 10^{38}$, becomes infinity too. A calculation without an answer, such as
0 / 0 or infinity minus infinity, gives **NaN**, "not a number". A NaN is not equal to anything, itself included, so
`x == x` is false for it and `x != x` is true. It also spreads: a NaN plus 1 is a NaN, and one NaN in a sum makes the
whole sum a NaN.

Test for them with `std::isnan(x)` and `std::isfinite(x)`, never with `==`. Strata guards its pictures this way. A shader function, `SanitizeHDR`, turns a NaN into 0 and clamps a value to 65,000. One bad pixel then cannot turn black or spread through the post-processing. The texture cooker also replaces NaN and infinity with 0 in the high-dynamic-range (HDR) images it imports.

Near zero, the floats also change. The smallest float of the usual form is about $1.2 \times 10^{-38}$. Below it come
**subnormal numbers**: the leading 1 is dropped, the gap stays at about $1.4 \times 10^{-45}$, and values fade to zero in
steps rather than jumping from $1.2 \times 10^{-38}$ to 0.

A **half float** has 16 bits: 1 for the sign, 5 for the exponent and 10 for the significand. Its largest value is
65,504, it holds whole numbers exactly only up to 2,048, and it keeps about 3 decimal digits. Strata stores
HDR colors in half floats, so numbers above 65,504 become infinity there, which is why `SanitizeHDR`
stops at 65,000. [Color](../basics/color.md) explains why that range suffices for light.

## The same inputs give the same bits

**Determinism** means that the same inputs give the same results, bit for bit. A float operation is exact in this sense:
one machine adding two given floats always gives the same sum. Two runs can still differ in the last bit when the order
of the steps differs. Adding floats in another grouping can change the result. In `double`,
(0.1 + 0.2) + 0.3 is 0.6000000000000001, and 0.1 + (0.2 + 0.3) is 0.6.

An order changes when several threads add their parts of a sum and combine them as they finish, or when a compiler
fuses a multiply and an add into one step that rounds once. The second case belongs to
[Flags and portability](../engineering/flags-portability.md). Strata promises that its physics results do not depend on
the number of threads, as `Docs/Architecture.md` says, and [Jobs](../core/jobs.md) shows how.

## Powers of two give sizes, and logarithms ask for the exponent

You met $2^n$ with bits, and its values double with each step: $2^{10}$ is 1,024, $2^{20}$ is 1,048,576 and $2^{30}$ is 1,073,741,824. Sizes follow them. A KiB is $2^{10}$ bytes, a MiB is $2^{20}$ bytes and a GiB is $2^{30}$ bytes. A kB is 1,000 bytes, a MB 1,000,000 and a GB 1,000,000,000, so a "256 GB" drive is a little smaller than 256 GiB. A data rate uses the decimal prefixes: a graphics card with 500 GB/s moves 500,000,000,000 bytes each second, which is about 8.3 GB in one frame at 60 frames per second.

One more sum has powers in it: 1 + 1/2 + 1/4 + 1/8 + ... never reaches 2 but comes as close as you like. It is a
geometric series, and [Interpolation](../basics/math-interpolation.md) teaches it with its sum.

The **logarithm** asks for the exponent backwards: $\log_b x$ is the exponent $y$ with $b^y = x$. In base 2,
$\log_2 1024 = 10$, because $2^{10} = 1024$. It counts the halvings of the mip example: a side of 1,024 pixels halves 10
times, and the chain has 11 levels. In base 10, $\log_{10} 1000 = 3$ counts the zeros. The logarithm of a product is the
sum of the logarithms:

$$\log_b(xy) = \log_b x + \log_b y$$

Here $b$ is the base, and $x$ and $y$ are positive numbers. As a check, 8 × 16 is $2^3 \times 2^4 = 2^7 = 128$, and
the exponents add: 3 + 4 = 7. C++ calls them `std::log2` and `std::log10`.

A logarithm also measures ratios, which people feel as steps of equal size, as pitch or brightness. An **exposure stop**, also called an exposure value (EV) stop, is a factor of two in light. Raising the exposure by one stop doubles the light, and by 3 stops
gives 8 times. A ratio $r$ of two lights is $\log_2 r$ stops: a sky 1,024 times brighter than a room is 10 stops
apart. [Lighting](../make/lighting.md) shows the editor's exposure.

A **decibel** (dB) states a ratio of two powers as ten times its base-10 logarithm.

$$\text{dB} = 10 \log_{10} \frac{P_2}{P_1}$$

$P_1$ and $P_2$ are two powers, such as the power of two sounds. A ratio of 10 is 10 dB, 100 is 20 dB,
and 2 is about 3 dB. For amplitudes, such as the height of a wave, the factor is 20, because power grows with the
square of the amplitude.

## The exponential function repeats one factor

An **exponential function** changes by the same factor in each equal step. Halve a value every second and you get 100,
50, 25, 12.5, and so on.

The standard base for it is **Euler's number**, $e$, about 2.71828. Its rate of change at any
moment equals its own value. Written with $e$, a decay is

$$v(t) = v_0 \, e^{-kt}$$

where $v$ is the value at the time $t$ in seconds, $v_0$ is the starting value, $k$ is the decay rate per second, and
`std::exp(x)` computes $e^x$. A minus sign makes the value fall, and $k$ is larger when it falls faster.

:::example[A decay with k = 2]
With $v_0 = 100$ and $k = 2$ per second, the value at $t = 0$ is 100. At $t = 0.5$ it is $100 \, e^{-1} = 36.8$, and
at $t = 1$ it is $100 \, e^{-2} = 13.5$. Each half second multiplies the value by $e^{-1}$, which is 0.368: the
same factor in each equal step.
:::

Try it: which $k$ halves the value every second?

:::answer
After one second the factor is $e^{-k}$, and it must be 1/2. The natural logarithm, `std::log`, undoes $e^x$: the natural logarithm of 1/2 is -0.693, so $-k = -0.693$ and $k = 0.693$.
:::

The inverse of $e^x$ is the natural logarithm, `std::log`. [Interpolation](../basics/math-interpolation.md) turns the
factor $1 - e^{-k \, \Delta t}$ into smooth motion.

## Common mistakes

- **Comparing floats with `==`.** Symptom: a test that fails for sums that look equal. Fix: compare the distance with a
  tolerance, and test NaN with `std::isnan`.
- **A float far from zero.** Symptom: a clock that runs fast or stops after hours, or a mesh that shakes 20 km from
  the origin. Fix: keep time in a `double`, and keep numbers small by measuring from a near origin.
- **Division with a negative dividend.** Symptom: a cell or index that is one too big at -0.5. Fix: use a floor
  division, and apply `(a + b - 1) / b` only to a non-negative `a`.
- **Relying on signed overflow.** Symptom: a program that works in a Debug build and fails in a Release build. Fix: use an
  unsigned type or a wider one, and check the range before the addition.
- **Logging a byte.** `Log::Info` writes a value with `<<`, so a `uint8_t` of 65 appears as the letter "A", and a 200
  as a symbol you cannot read. Fix: log `int(value)` or `+value`.
- **Trusting six digits.** Symptom: the log shows 0.3 and 1, and a test still fails. Fix: write 9 or 17 digits with
  `std::setprecision` into a string and log that.
- **A shift of 1 instead of 1u.** Symptom: a flag of bit 31 that is negative. Fix: write `1u << n`, and keep the shift
  below the bit count of the type.

## Summary

- A bit is 0 or 1, a byte is eight bits, and binary places are worth 1, 2, 4, 8, and so on. One hex digit is four
  bits, and `0x` marks a hex number.
- Integer types have a fixed size and range. Signed ones use two's complement, unsigned ones wrap around on overflow,
  and `/` drops the fraction toward zero, so a negative dividend needs a floor division.
- Masks with `&`, `|`, `^` and `~` test, set and clear bits, and shifts multiply and divide by powers of two and pack
  two numbers into one integer.
- A float is a sign, an exponent and a significand. Its gap is $2^{k-23}$, so it grows with the number, most decimal
  fractions are rounded, and NaN and infinity are values to guard against.
- A logarithm is an exponent asked for backwards: stops count factors of two, decibels count tens, and a decay by the
  same factor each step is $e^{-kt}$.

## Check yourself

1. What is `0x3A` in decimal? (a) 40 (b) 58 (c) 13 (d) 310

   :::answer{tests="binary-hex"}
   (b) 58: 3 × 16 + 10. (a) gives the first place a worth of 10 instead of 16, (c) adds the digits, and (d) writes 3 and 10 side by side.
   :::

2. Which range does an `int16_t` hold? (a) 0 to 65,535 (b) -32,768 to 32,767 (c) -32,767 to 32,768 (d) -65,535 to 65,535

   :::answer{tests="integers"}
   (b). Two's complement has one more negative number than positive ones. (a) is `uint16_t`, and (c) puts the extra
   number on the wrong side.
   :::

3. What do `0x2C & 0x0F`, `0x2C | 0x0F` and `1u << 5` give?

   :::answer{tests="bit-masks"}
   `0x2C` is 00101100 and `0x0F` is 00001111. `&` keeps 00001100, which is 12 (`0x0C`). `|` gives 00101111, which is 47
   (`0x2F`). `1u << 5` is 32.
   :::

4. A `float` holds 5,000. Which is the gap to the next float? (a) 0.0000001 (b) 0.00049 (c) 0.5 (d) 1

   :::answer{tests="floating-point"}
   (b). The number lies from 4,096 to 8,192, so $k = 12$ and the gap is $2^{12-23} = 2^{-11} = 0.00049$. (a) is the gap
   at 1, and (c) and (d) are far too big.
   :::

5. A variable `x` is NaN. What do `x == x`, `x != x` and `x + 1.0f` give?

   :::answer{tests="floating-point"}
   `false`, `true` and NaN. A NaN is not equal to anything, itself included, and an operation with it gives a NaN.
   :::

6. How many stops lie between two lights, one 16 times brighter than the other, and what is $80\,e^{-0.5 t}$ at
   $t = 2$?

   :::answer{tests="logarithms"}
   The ratio 16 is $2^4$, so there are 4 stops. At $t = 2$ the exponent is -1, and $80 \, e^{-1} = 29.4$.
   :::

## Practice

1. **Basic.** Write 13 in binary and `0xFF` in decimal by hand, then log both from a script and compare.

   :::answer[Worked solution]{tests="binary-hex"}
   By hand, 13 is 8 + 4 + 1 = 1101, and 0xFF is 15 × 16 + 15 = 255. In the playground ([The playground is a script of your own](programming-1.md#the-playground-is-a-script-of-your-own)), log `13` and `0xFF` from `int` variables: an `int` prints in decimal, so the Console shows 13 and 255. A binary literal such as `0b1101` checks your first answer, because the Console then shows 13.
   :::

2. **Basic.** Predict, then run: a `uint16_t` of 65,535 plus one stored back, and the results of `-7 / 2` and
   `-7 % 2` in `int`.

   :::answer[Worked solution]{tests="integers" solution="sketches/basics-numbers-overflow.cpp"}
   The counter wraps to 0, because 65,536 is exactly the number of values the type has, and the remainder is 0. The division drops the
   fraction toward zero: -3, with the remainder -1. The floor of -3.5 is -4.

   ```cpp sketch="basics-numbers-overflow.cpp"
   // Practice 2: a 16-bit counter that wraps, and division with positive and negative dividends.
   #include <cmath>
   #include <cstdint>
   #include <iostream>

   int main()
   {
   	uint16_t counter = 65535;
   	counter = static_cast<uint16_t>(counter + 1);
   	std::cout << "65535 + 1 in 16 bits: " << counter << '\n';
   	std::cout << "7 / 2 = " << 7 / 2 << '\n';
   	std::cout << "-7 / 2 = " << -7 / 2 << '\n';
   	std::cout << "-7 % 2 = " << -7 % 2 << '\n';
   	std::cout << "floor of -7 / 2.0 = " << std::floor(-7 / 2.0) << '\n';
   	return 0;
   }
   ```

   ```text output-of="basics-numbers-overflow.cpp"
   65535 + 1 in 16 bits: 0
   7 / 2 = 3
   -7 / 2 = -3
   -7 % 2 = -1
   floor of -7 / 2.0 = -4
   ```

   1. **Line 9:** the sum 65,536 is an `int`, and storing it back in 16 bits keeps the remainder, 0.
   2. **Lines 12–13:** a negative dividend gives -3 and the remainder -1.
   3. **Line 14:** `std::floor` of -3.5 gives -4.

   :::

3. **Medium.** A `uint32_t` holds `0b0101`. Set bit 3, test it, clear it and test it again. Predict each value.

   :::answer[Worked solution]{tests="bit-masks"}
   Bit 3 is worth 8. The line `flags |= 1u << 3;` sets it and gives 5 + 8 = 13, and `(flags & (1u << 3)) != 0` is then true. The line `flags &= ~(1u << 3);` clears it and returns to 5, and the test is false.
   :::

4. **Medium.** Add 0.1f ten times into a `float` and compare the sum with 1.0f, once with `==` and once with a
   tolerance. Predict first, then log every digit with `std::ostringstream` and `std::setprecision`.

   :::answer[Worked solution]{tests="floating-point" solution="sketches/basics-numbers-tolerance.cpp"}
   The `==` test is false, because 0.1f is slightly off and the ten errors add up. The tolerance of 1e-6 accepts the
   sum. In a script, `Log` shows six digits, so write the digits into a string first.

   ```cpp sketch="basics-numbers-tolerance.cpp"
   // Practice 4: ten additions of 0.1f against 1.0f, with every digit, without and with a tolerance.
   #include <cmath>
   #include <iomanip>
   #include <iostream>

   int main()
   {
   	float sum = 0.0f;
   	for (int count = 0; count < 10; count++)
   		sum += 0.1f;
   	std::cout << std::setprecision(9) << std::boolalpha;
   	std::cout << "sum: " << sum << '\n';
   	std::cout << "equal to 1: " << (sum == 1.0f) << '\n';
   	std::cout << "within 1e-6: " << (std::abs(sum - 1.0f) < 1e-6f) << '\n';
   	return 0;
   }
   ```

   ```text output-of="basics-numbers-tolerance.cpp"
   sum: 1.00000012
   equal to 1: false
   within 1e-6: true
   ```

   1. **Lines 9–10:** ten additions of the float nearest to 0.1.
   2. **Line 11:** nine digits identify a `float`.
   3. **Line 14:** the tolerance accepts a distance below 1e-6.

   The playground's script writes the digits into a string first and then logs the string. Add `#include <iomanip>` and `#include <sstream>` at the top of the script:

   ```cpp pseudocode
   std::ostringstream stream;
   stream << std::setprecision(9) << sum;
   Log::Info(stream.str());
   ```

   The log then shows all nine digits of the sum.

   :::

5. **Hard.** With `std::nextafter`, find the gap between a float and its neighbour at 1, 1,000 and 20,000. Log the
   difference, not the neighbour, and compare it with the table.

   :::answer[Worked solution]{tests="floating-point" solution="sketches/basics-numbers-gaps.cpp"}
   The neighbour itself prints as 1 at six digits, so the difference is the number worth logging. The gaps are $2^{-23}$,
   $2^{-14}$ and $2^{-9}$, as the table says.

   ```cpp sketch="basics-numbers-gaps.cpp"
   // Practice 5: the gap from a float to the next float, at 1, 1000 and 20000.
   #include <cmath>
   #include <iomanip>
   #include <iostream>

   int main()
   {
   	const float values[] = { 1.0f, 1000.0f, 20000.0f };
   	std::cout << std::setprecision(9);
   	for (const float value : values)
   		std::cout << value << ": " << std::nextafter(value, 1.0e9f) - value << '\n';
   	return 0;
   }
   ```

   ```text output-of="basics-numbers-gaps.cpp"
   1: 1.1920929e-07
   1000: 6.10351562e-05
   20000: 0.001953125
   ```

   1. **Line 11:** `std::nextafter(value, 1.0e9f)` is the next float above `value`, and subtracting `value` leaves the gap.

   :::

6. **Hard.** Optional, starting from the end of Coin Run, your own or Checkpoint 4 of [Ship the finished game](../make/project-coin-run.md#ship-the-finished-game): its on-screen display shows a clock, which starts from the field `TimeLimit` of `CoinRunGame` on `Game`. Start the clock at 600,000 s and
   find after how long one frame's time no longer changes it. Then start at 20,000 s and watch the drift. Predict
   each from the table, and then keep the clock in a `double`.

   :::answer[Worked solution]{tests="floating-point" solution="sketches/basics-numbers-timer.cpp"}
   At 600,000 s the gap is 0.0625 s, so a frame of 0.0167 s adds nothing. At 20,000 s the gap is 0.00195 s, and a frame
   adds 9 gaps, 0.0176 s, so the clock runs 5.5 % fast. A `double` adds the frame exactly enough at both starts.

   ```cpp sketch="basics-numbers-timer.cpp"
   // Practice 6: one frame of 1/60 s added to a float timer and to a double timer, far from the start.
   #include <iomanip>
   #include <iostream>

   int main()
   {
   	const float frame = 1.0f / 60.0f;
   	const float starts[] = { 20000.0f, 600000.0f };
   	std::cout << std::setprecision(9);
   	for (const float start : starts)
   	{
   		float asFloat = start;
   		double asDouble = start;
   		asFloat += frame;
   		asDouble += frame;
   		std::cout << start << ": float adds " << asFloat - start << ", double adds " << asDouble - start << '\n';
   	}
   	return 0;
   }
   ```

   ```text output-of="basics-numbers-timer.cpp"
   20000: float adds 0.017578125, double adds 0.0166666675
   600000: float adds 0, double adds 0.0166666675
   ```

   1. **Lines 12–15:** the same start goes into a `float` and into a `double`, and each adds the frame.
   2. **Line 16:** the program prints how much each type changed.

   :::

## Where the book uses it

- [Bytes](../basics/bytes.md) reads integers and floats from files, and uses the sizes and masks of this page.
- [Color](../basics/color.md) stores light in 8 bits and in half floats, and rounds to fit, as shown above.
- [Interpolation](../basics/math-interpolation.md) uses the exponential function to smooth a value.
- [Temporal anti-aliasing](../image/taa.md) uses the radical inverse in bases 2 and 3 for its camera shifts.
- [Entities and components](../world/ecs.md) packs an index and a version into one handle.
- [Jobs](../core/jobs.md) keeps the results of parallel work the same for any thread count.

## Further reading

- [learncpp.com, "Introduction to fundamental data types"](https://www.learncpp.com/cpp-tutorial/introduction-to-fundamental-data-types/):
  the integer and floating-point types of C++ with their ranges; beginner.
- [learncpp.com, "Bitwise operators"](https://www.learncpp.com/cpp-tutorial/bitwise-operators/): shifts, masks and
  flags with worked examples; beginner.
- [cppreference, `std::numeric_limits`](https://en.cppreference.com/w/cpp/types/numeric_limits): the limits of every
  numeric type; intermediate.
- [Gaffer On Games, "Floating Point Determinism"](https://gafferongames.com/post/floating_point_determinism/): why
  two machines can differ in the last bit; advanced.
- David Goldberg, "What Every Computer Scientist Should Know About Floating-Point Arithmetic": the standard paper on
  rounding and IEEE 754; advanced.
