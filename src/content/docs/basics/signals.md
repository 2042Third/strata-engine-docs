---
id: basics/signals
title: "Sampling, aliasing and filtering"
description: "Why a picture or a sound measured at separate points can show false detail, and how filters, mips, dithering and denoising keep it honest."
kind: primer
size: L
tracks: [B, E]
needs: [basics/math-interpolation, basics/color]
time: 75
learn:
  - id: aliasing
    text: compute the false frequency that a signal above half the sample rate appears as
  - id: filtering
    text: compute a weighted average of samples under a kernel whose weights add to 1
  - id: prefiltering
    text: choose the mip level whose texels match a pixel and explain why a picture is filtered before it is sampled
  - id: dithering
    text: predict which pixels of a flat area an ordered dither rounds up
  - id: denoising
    text: explain how weights that stop at edges keep a blur from smearing two surfaces together
status: final
---

::::test-out

1. A game samples a sound 100 times a second, and a pure tone of 70 Hz goes in. At which frequency does the tone
   appear in the samples?

   :::answer{tests="aliasing"}
   Half the sample rate is 50 Hz, and 70 Hz lies above it, so the tone is false. It appears at the distance to the
   nearest multiple of the rate: |70 - 100| = 30 Hz.
   :::

2. Blur the middle of the row 8, 8, 0 with the weights 1, 2, 1, each divided by 4. What is the new middle value, and
   what must the weights add to?

   :::answer{tests="filtering"}
   (8 × 1 + 8 × 2 + 0 × 1) / 4 = 24 / 4 = 6. The weights must add to 1, here 1/4 + 2/4 + 1/4, or the blur makes the
   picture lighter or darker.
   :::

3. A texture 256 texels wide covers 64 pixels of the screen. Counting the full size as level 0, which mip level has about
   one texel for each pixel, and how wide is it?

   :::answer{tests="prefiltering"}
   Each pixel spans 256 / 64 = 4 texels. Each level halves the width, so level 2 is the one: 256 / 4 = 64 texels wide.
   :::

4. A display shows whole numbers. A flat area has the value 7.5. Before rounding down, a 4 by 4 block adds the 16
   thresholds 0.03, 0.09, 0.16 and so on up to 0.97, spread evenly. How many of the 16 pixels show 8?

   :::answer{tests="dithering"}
   A pixel shows 8 when 7.5 plus its threshold reaches 8, so the threshold must be at least 0.5. Half of the 16
   thresholds are, so 8 pixels show 8 and 8 show 7. The block averages 7.5.
   :::

5. A pixel has the value 0.6. Its left neighbor has 0.8 on the same surface, and its right neighbor has 0.2 on another
   surface. The weights are 1 for the pixel and the left neighbor and 0 for the right one. What is the average?

   :::answer{tests="denoising"}
   (0.6 + 0.8) / 2 = 0.7. The weight 0 keeps the other surface out; a plain average of all three would give 0.53.
   :::

::::

## Why you will need this

A picture on a screen and a sound from a speaker have one thing in common: both are lists of numbers measured at separate
places or moments. A game must make them, change them and show them, and most visible bugs sit in the gaps between the
numbers. A fence that crawls with strange patterns, a coin that seems to turn backward, a sky with visible bands and a
shadow that looks like sand are all the same few ideas.

You will do four things with this page. You will compute what a too-fast signal turns into, filter a row of numbers by
hand, choose the right mip level and round a flat area so that it keeps its average.

Other pages build on it. [Textures](../assets/textures.md) uses mips and filtered reads to keep far surfaces calm.
[Spatial anti-aliasing](../image/spatial-aa.md) removes stair steps along edges. [Sound in a computer](../audio/sound-in-a-computer.md)
explains why a sound has 48,000 samples a second. [Ambient occlusion](../indirect/ao.md) cleans up a noisy result with the
last idea here.

Only the optional Coin Run exercise needs a project. Each sketch is a whole program: save it as `sketch.cpp` and compile it with C++20 in the terminal of [How a C++ program is built](build.md#open-a-terminal-that-finds-a-compiler). On Windows, run `cl /std:c++20 /EHsc sketch.cpp` and then `.\sketch.exe`. On Linux and macOS, run `c++ -std=c++20 sketch.cpp -o sketch` and then `./sketch`. Without a compiler, read each output and its notes.

## A signal is a quantity measured at separate places

Take a screenshot of a striped wall and read the brightness of one row of pixels from left to right: 20, 20, 220, 220,
20, 20, 220, 220. Drawn as a graph, the numbers rise and fall in a wave. A **signal** is a quantity that changes along a
line: here the brightness along a row, and in a sound the pressure of the air along time. A microphone cannot write down
the whole curve, so it measures the pressure again and again, a few thousand times a second.

Each number you wrote down is a **signal sample**: the value of the signal at one place or one moment. The row of pixels
is a list of samples of the brightness that the camera saw. Everything between two samples was never measured, and that
fact causes the rest of this page.

The stripes repeat every 4 pixels. A signal that repeats has a **frequency**: how many repeats fit in one unit of time
or distance. These stripes repeat 1 / 4 = 0.25 times per pixel. A tone of 440 Hz (hertz, repeats per second) repeats 440
times a second, so one repeat lasts 1000 / 440 = 2.3 ms.

The sine wave of [vectors](../basics/math-vectors.md) is the pure case. A sine of frequency $f$ is $\sin(2\pi f t)$, which
reads "the sine of two pi times f times t". Its period, the length of one repeat, is $1/f$. Any signal you meet is a sum of
such waves, and sharp detail needs high frequencies: broad shapes and low rumbles are low, thin stripes and whistles are
high.

:::example[A fence in pixels]
A fence has a post every 0.5 m, and the camera shows 20 pixels for each metre. The fence repeats 1 / 0.5 = 2 times per
metre. That is 2 / 20 = 0.1 repeats per pixel, or one repeat each 10 pixels. The camera takes 20 samples per metre, the
fence is 2 per metre, and the rest of the page asks when that is enough.
:::

Try it: a tone repeats 250 times a second. How long is one repeat?

:::answer
The period is 1 / 250 s = 0.004 s, which is 4 ms.
:::

## Sampling measures at regular steps, and reading between samples is a guess

**Sampling** is measuring a signal at regular steps along its line.

The **sample rate** is how many samples you take in each unit: 48,000 a second for a sound, or 20 a metre for the fence
above. Between two samples you know nothing, yet a game often needs a value there. It scales a picture, or it draws a
texture on a surface whose pixels do not line up with the texture's. Then it guesses from the neighbors.

The first guess is a nearest read: take the closest sample. It is cheap and gives coarse results, because the value
jumps halfway between two samples. The second is a linear read: blend the two neighbors by distance, the lerp of
[interpolation](../basics/math-interpolation.md). The value then changes smoothly.

In two dimensions a read uses the four samples around the point. It blends along x in the top pair, blends along x in the
bottom pair, and blends those two results along y. A texture read that does this is **bilinear filtering**; the lerp
mathematics are the interpolation page's.

:::example[One linear read and one read in two dimensions]
The samples at positions 0, 1, 2 and 3 are 10, 30, 20 and 60. Read at 1.25. The nearest sample is at 1, so the nearest
read gives 30. The linear read blends 30 and 20 by 0.25: 30 × 0.75 + 20 × 0.25 = 27.5.

Now four pixels of a texture hold 0 and 100 on the top row and 100 and 200 below. Read at 0.25 across and 0.5 down. The
top pair gives 25, the bottom pair gives 125, and half of the way between them is 75.
:::

Try it: with the same four samples, read at 2.75 with both methods.

:::answer
The nearest sample is at 3, so the nearest read gives 60. The linear read blends 20 and 60 by 0.75: 20 × 0.25 + 60 ×
0.75 = 50.
:::

A linear read is only a straight-line guess. It cannot bring back detail that the sampling lost, and the next section
shows how much can be lost.

## Above half the sample rate, a fast signal appears as a slow one

:::question
The sketches use `#include`, :term[function calls]{id=function-call} such as `std::sin(` and references, which [Programming 3](../basics/programming-3.md) teaches. You can read only their output and the numbered notes.
:::

Sample a sine of 1 Hz and one of 9 Hz at 10 samples a second. The sketch prints the first five samples of each.

```cpp sketch="basics-signals-alias.cpp"
// Samples a 1 Hz and a 9 Hz sine at 10 samples a second: the 9 Hz samples are the 1 Hz ones turned upside down.
#include <cmath>
#include <cstdio>
#include <numbers>

int main()
{
	const double sampleRate = 10.0;
	const double twoPi = 2.0 * std::numbers::pi;
	for (int n = 0; n <= 4; n++)
	{
		const double t = n / sampleRate;
		std::printf("n = %d   1 Hz: %6.3f   9 Hz: %6.3f\n", n, std::sin(twoPi * 1.0 * t), std::sin(twoPi * 9.0 * t));
	}
}
```

```text output-of="basics-signals-alias.cpp"
n = 0   1 Hz:  0.000   9 Hz:  0.000
n = 1   1 Hz:  0.588   9 Hz: -0.588
n = 2   1 Hz:  0.951   9 Hz: -0.951
n = 3   1 Hz:  0.951   9 Hz: -0.951
n = 4   1 Hz:  0.588   9 Hz: -0.588
```

1. **Line 12:** the moment of sample `n` is `n` divided by the rate, 0.1 s apart.
2. **Line 13:** the two sines differ only in the frequency, 1 and 9.

The 9 Hz samples are the 1 Hz samples turned upside down. Between two samples the 9 Hz wave runs 324° of its 360°, which
looks like a small step of 36° backward. The samples cannot tell the two waves apart, so the reader of the numbers sees
a slow wave that does not exist.

The largest frequency that samples can hold is the **Nyquist limit**, half the sample rate: 5 Hz here.

A signal above it comes out as **aliasing**: a false, lower frequency. Read aloud as "the absolute value of f minus n
times f s", the false frequency is
$$f_\text{false} = |f - n f_s|$$

Here $f_\text{false}$ is the false frequency, $f$ the real frequency and $f_s$ the sample rate, all in Hz. The number $n$ is the whole number that makes the
result smallest. Check the limits: below half the rate $n$ is 0 and nothing changes; at a frequency equal to the rate,
$n$ is 1 and the result is 0, a constant. For 9 Hz at a rate of 10 the result is |9 - 10| = 1 Hz.

::figure{id=aliasing-sine}

The same effect has many faces. A film camera takes 24 pictures a second, which is the sample rate. A wheel with a spoke
every 30° looks the same after every 30°, so its pattern repeats each 30°. If it turns 25° between two pictures, the nearest
spoke is 5° behind where the old one was, and the wheel appears to turn backward by 5° a picture.

A fine fence seen from far away does the same in space. The camera has 20 pixels a metre, so its limit is 10 repeats per
metre. A fence with a post each 0.08 m repeats 12.5 times a metre and appears as |12.5 - 20| = 7.5 repeats a metre: wide,
false stripes called **moiré**. Moving the camera slides the false stripes much faster than the real fence, which the eye
sees as shimmer.

A sharp edge between a dark and a bright area holds frequencies without an upper bound. Some of them always lie above the
limit, so every edge drawn with one sample per pixel has stair steps. The limit also explains why sound uses 48,000 samples a second:
people hear up to about 20,000 Hz, and the limit of 24,000 Hz lies above it.

:::example[A wheel and a fence]
A wheel has 12 spokes, one each 30°, and turns 25° a picture. The pattern repeats each 30°, so a turn of 25° looks like
25 - 30 = -5°: 5° backward. At 24 pictures a second, the wheel spins forward 600° a second yet appears to run backward
120° a second.

A fence with a post every 0.25 m seen with 20 pixels a metre repeats 4 times a metre, far below the limit of 10, and the
posts show true.
:::

Try it: a sound of 30,000 Hz is sampled at 48,000 samples a second. Which frequency do the samples hold?

:::answer
The limit is 24,000 Hz, so 30,000 Hz is above it. The nearest multiple of the rate is 48,000, and |30,000 - 48,000| =
18,000 Hz. The samples hold an 18,000 Hz tone that nobody played.
:::

## Filtering averages nearby samples with weights

If detail above the limit causes false patterns, the cure is to remove that detail before it is measured. The tool is
**filtering**: replacing each sample with a weighted average of the samples near it. A weighted average multiplies each
neighbor by a weight, adds the products and divides by the weights' sum.

The row of weights is the **filter kernel**.

Three kernels appear everywhere. A box gives every neighbor the same weight, such as 1/3, 1/3, 1/3. A tent gives the
center the most and falls off in a straight line, such as 1/4, 2/4, 1/4. A Gaussian has a bell shape: its weights follow
$e^{-x^2 / 2\sigma^2}$ at distance $x$, where $e$ is the number 2.718 and $\sigma$ sets the bell's width, and $(1, 4, 6, 4, 1) / 16$ is a close five-weight version.

The weights must add to 1. Then a flat area keeps its value and the picture keeps its brightness. Weights adding to 2
double the brightness, and weights adding to 0.8 darken the picture by a fifth.

:::example[One spike under three kernels]
Take the row 0, 0, 0, 16, 0, 0, 0. The new value at each place is the sum of the neighbors times the weights. A box of
three gives 16 / 3 = 5.33 at the spike and at its two neighbors. A tent gives 4, 8, 4, and the bell gives 1, 4, 6, 4,

1. Each result adds to 16, the total of the spike.

:::

Sliding a kernel along the signal and doing this sum at every place is **convolution**. The sketch does it for the three
kernels.

```cpp sketch="basics-signals-kernel.cpp"
// Slides a box, a tent and a bell kernel along a spike of height 16: each result keeps the total of 16.
#include <cstdio>
#include <vector>

int main()
{
	const std::vector<double> spike = { 0, 0, 0, 16, 0, 0, 0 };
	const std::vector<double> kernels[3] = { { 1.0 / 3, 1.0 / 3, 1.0 / 3 }, { 0.25, 0.5, 0.25 }, { 0.0625, 0.25, 0.375, 0.25, 0.0625 } };
	for (const std::vector<double>& kernel : kernels)
	{
		const int radius = static_cast<int>(kernel.size()) / 2;
		for (int i = 0; i < 7; i++)
		{
			double sum = 0.0;
			for (int k = -radius; k <= radius; k++)
				if (i + k >= 0 && i + k < 7)
					sum += spike[i + k] * kernel[k + radius];
			std::printf("%.2f%c", sum, i < 6 ? ' ' : '\n');
		}
	}
}
```

```text output-of="basics-signals-kernel.cpp"
0.00 0.00 5.33 5.33 5.33 0.00 0.00
0.00 0.00 4.00 8.00 4.00 0.00 0.00
0.00 1.00 4.00 6.00 4.00 1.00 0.00
```

1. **Line 8:** the three kernels, each with weights adding to 1.
2. **Lines 9–11:** one kernel at a time; the radius is how many neighbors it reaches on each side.
3. **Lines 13–16:** for every place, the sum of the neighbors times their weights; places outside the row count as 0.

::figure{id=kernels-three}

A wider kernel removes more detail and costs more taps, the reads of one sample for each weight. For a picture the kernel has rows and columns. A bell or box
filter can run as a row pass and then a column pass, so a kernel 5 wide costs 10 reads instead of 25.

Try it: apply the weights 1, 2, 1 divided by 4 to the row 0, 0, 8, 8, 8 at the second, third and fourth places.

:::answer
Second: (0 + 0 + 8) / 4 = 2. Third: (0 + 16 + 8) / 4 = 6. Fourth: (8 + 16 + 8) / 4 = 8. The sharp step from 0 to 8
became a ramp of 0, 2, 6, 8.
:::

## Prefiltering filters before sampling, and mips do it for pictures

Filtering after sampling is too late: once a fast signal appears as a slow one, no filter can tell them apart. The filter
must come first. **Prefiltering** is filtering a signal before it is sampled, so that nothing above the limit is left.
Sound hardware does it with an electronic filter in front of the converter.

A picture on a surface has the same problem. Suppose a far floor shows a row of texels, the pixels of a texture, that
alternate 0 and 255. The camera samples one texel in 4, always texel 0, 4, 8 and so on, which are all 0, so the floor is
black. Move the camera by one texel and every sample is 255: the floor flashes white. The true average is 127.5.

The cure is to store the picture already filtered. A mip is a copy of a texture at half the width and half the height,
each of its texels the average of a 2 by 2 block of the copy before. The copies together are the mip chain, and level 0 is
the original. For the alternating row, level 1 holds 127.5 everywhere, so any reading is right and nothing flashes.

The :term[graphics card]{id=gpu} chooses the level by how many texels one pixel spans. With 4 texels to a pixel, the level is the
base-2 :term[logarithm]{id=logarithm} of 4, which is 2. A level between two whole numbers blends two neighbors. Strata's cooker
(`Strata/src/Strata/Asset/TextureCooker.cpp`) builds the chain once, when the image is imported, filtering each level
from the one before.

::figure{id=floor-mips}

The chain costs memory: the extra levels add 1/4 + 1/16 + ... of the original, a third. A texture of 1,024 by 1,024 has
11 levels, down to a single texel. The count is 1 plus the base-2 logarithm of the larger side, which Strata computes in
`CalculateMipCount` of `Strata/src/Strata/Renderer/Texture.cpp`.

:::example[Choosing a mip]
A texture is 2,048 texels wide. A wall covers 256 pixels across. One pixel spans 2,048 / 256 = 8 texels, and the
base-2 logarithm of 8 is 3. Level 3 is 2,048 / 8 = 256 texels wide: one texel for each pixel.
:::

Try it: a 512-texel texture covers 128 pixels. Which level, and how wide is it?

:::answer
One pixel spans 512 / 128 = 4 texels, so the level is 2, and it is 512 / 4 = 128 texels wide.
:::

## Resampling a picture with a filter

Making a mip is shrinking a picture, and shrinking is filtering with a kernel. The simplest kernel for halving is the box:
each new pixel is the average of the 2 by 2 pixels it covers. It is cheap, but it treats a feature by where it falls.

:::example[A thin line, halved by a box and by a wider kernel]
Halve the row 0, 0, 0, 100, 0, 0, 0, 0 to 4 pixels. A box averages pairs and gives 0, 50, 0, 0. Move the line one pixel
to the right and it gives 0, 0, 50, 0: a shift of half a new pixel made the line jump a whole pixel.

A wider kernel, the tent with weights 1/8, 3/8, 3/8 and 1/8 over four old pixels, gives 0, 37.5, 12.5, 0 for the first row
and 0, 12.5, 37.5, 0 for the second. The line moves smoothly. The price is four reads for each new pixel instead of two.
:::

Strata's cooker uses a wider kernel, the Mitchell filter, for the mips of ordinary images. Its weights reach farther
than the tent's and have a small negative part, which keeps edges crisper than a tent. The weights still add to 1. The
cooker halves each level from the one before, as `Halve` shows in the file named above.

The values it averages matter. A color stored as an :term[sRGB]{id=srgb} :term[byte]{id=byte} is not proportional to light. The average of black and
white light is 0.5 in linear values, and an sRGB byte for 0.5 is about 188, not the 128 you get by averaging the bytes.
So the cooker filters in linear values (`STBIR_TYPE_UINT8_SRGB` makes the library convert) and converts back.

Images with a :term[high dynamic range]{id=high-dynamic-range} hold linear values already, and the cooker halves those with a box filter. The cooker's own page,
[texture cooking](../assets/texture-cooking.md), has the rest.

:::why
A box would cost less, but a thin line would jump between pixels as a texture moves. The Mitchell filter costs more reads for each new pixel, and the sRGB conversion costs a step for each texel. Both are paid once, when the image is imported, so the running game pays nothing.
:::

Try it: what does an average of two sRGB bytes, 0 and 255, give, and what should it give for equal amounts of light?

:::answer
The bytes give (0 + 255) / 2 = 127.5, about 128. Equal amounts of black and white light give 0.5 in linear values, which an
sRGB byte stores as about 188. So 128 is too dark, and a mip chain built from bytes makes far surfaces darker.
:::

## Dithering rounds with a planned offset

A screen stores each :term[color channel]{id=color-channel} in 256 levels. A screen rounds a smooth value to the nearest level. A smooth
sky from 100 to 110 across 1,920 pixels becomes 11 flat stripes: nine of 192 pixels and a half stripe of 96 at each end. The eye sees the steps between them: bands.

**Dithering** adds a small planned offset before rounding, so that the :term[rounding errors]{id=rounding-error} spread out and the bands turn into fine
grain that averages to the right value. With a flat value of 100.25, plain rounding gives 100 everywhere, losing the 0.25.
A threshold between 0 and 1 added first gives 101 when the sum reaches 101, and 25 % of the pixels need a threshold of at
least 0.75.

A random threshold per pixel works, but it clumps and, when drawn again every frame, makes the grain boil on a still
picture. **Ordered dither** uses a fixed pattern instead: the 4 by 4 Bayer matrix, a table of the numbers 0 to 15 so
that nearby pixels hold far-apart numbers. The pixel at column x and row y uses the entry `x % 4` columns across and `y % 4` rows down, where `%` is the remainder after division.

| | x = 0 | x = 1 | x = 2 | x = 3 |
| --- | --- | --- | --- | --- |
| y = 0 | 0 | 8 | 2 | 10 |
| y = 1 | 12 | 4 | 14 | 6 |
| y = 2 | 3 | 11 | 1 | 9 |
| y = 3 | 15 | 7 | 13 | 5 |

The threshold of an entry $n$ is $(n + 0.5) / 16$, which spans 0.03 to 0.97 evenly. A value of 100.25 reaches 101 where the
threshold is at least 0.75, that is where $n \ge 12$. That is four entries, so four of 16 pixels show 101 and the block
averages 100.25. The pattern never changes, so a still picture stays still.

```cpp sketch="basics-signals-bayer.cpp"
// Dithers the flat value 100.25 over one 4 by 4 block with the Bayer table and prints the rounded values.
#include <cmath>
#include <iostream>

int main()
{
	const int bayer[16] = { 0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5 };
	const double value = 100.25;
	int raised = 0;
	for (int y = 0; y < 4; y++)
	{
		for (int x = 0; x < 4; x++)
		{
			const double threshold = (bayer[y * 4 + x] + 0.5) / 16.0;
			const int shown = static_cast<int>(std::floor(value + threshold));
			raised += shown - 100;
			std::cout << shown << (x < 3 ? ' ' : '\n');
		}
	}
	std::cout << raised << " of 16 pixels show 101\n";
}
```

```text output-of="basics-signals-bayer.cpp"
100 100 100 100
101 100 101 100
100 100 100 100
101 100 101 100
4 of 16 pixels show 101
```

1. **Line 7:** the Bayer table, row by row.
2. **Line 14:** the threshold of the pixel, from its table entry.
3. **Line 15:** rounding down after adding the threshold gives 100 or 101.

::figure{id=dither-gradients}

Strata uses the same table for something else: it fades between two levels of detail of a mesh, drawing the new level on
some pixels and the old one on the others. The shader reads the table like this.

Slang, the shader language, looks like C++ with types for the graphics processing unit (GPU). The type `uint` is an :term[unsigned integer]{id=unsigned-integer}, `uint2` holds two of them, and `fragCoord` is the position in
pixels of the pixel being drawn. A literal such as `3u` is an unsigned number, and `& 3u` keeps the two lowest bits, which
is the remainder after division by 4.

```slang src="Strata/shaders/Include/Scene.slang#L171-L182"
// Whether a draw with this cross-fade code covers the pixel (LODSelection::IsLODFadeDrawn): the level fading in (codes 1-15)
// where the 4x4 ordered dither threshold is below the code, the level fading out (the code plus 16) on the other pixels.
// The depth prepass and the forward pass test the same, so the EQUAL depth test holds.
bool IsLODFadeDrawn(uint code, float2 fragCoord)
{
	if (code == 0u)
		return true;
	const uint bayer[16] = { 0u, 8u, 2u, 10u, 12u, 4u, 14u, 6u, 3u, 11u, 1u, 9u, 15u, 7u, 13u, 5u };
	uint2 pixel = uint2(fragCoord) & 3u;
	uint threshold = bayer[pixel.y * 4u + pixel.x];
	return code < ST_LOD_FADE_OUTGOING_CODE ? threshold < code : threshold >= code - ST_LOD_FADE_OUTGOING_CODE;
}
```

1. **Line 174:** the function answers whether this pixel is drawn for the level of detail and its fade `code`.
2. **Line 178:** the Bayer table of this page, as 16 unsigned numbers in one row.
3. **Line 179:** the pixel's position, cut to its two lowest bits in each direction, so 0 to 3.
4. **Line 180:** the threshold: row `pixel.y` of 4 entries, column `pixel.x`.
5. **Line 181:** the level fading in draws where the threshold is below the code, and the level fading out draws on the other pixels.

:::why
The fade is drawn by two passes, which must cover the same pixels. A table that depends only on the pixel's position gives that without more work, where a random choice would need a seed shared by both passes. The cost is a regular pattern that a close look can see.
:::

The final picture's own dither is the topic of [encoding](../image/encoding.md), and the fade of
[levels of detail](../draw/lod.md).

Try it: with the same table, dither the value 5.375. How many of the 16 pixels show 6?

:::answer
The value reaches 6 where the threshold is at least 0.625, that is where $n + 0.5 \ge 10$, so $n \ge 10$. The entries 10
to 15 are six, so six of 16 pixels show 6, and the block averages 5 + 6 / 16 = 5.375.
:::

## Denoising averages similar neighbors

Some effects measure little and guess the rest. Ambient occlusion, which says how much the nearby geometry blocks the soft
light at a point, is measured from a few samples around each pixel, so its result is noisy. **Denoising** removes the noise by
averaging each pixel with its neighbors in the same picture. Doing so with the neighbors of one frame, not of earlier
frames, is **spatial denoising**.

A plain blur is wrong at an edge. Take the five pixels 0.9, 0.7, 0.8 | 0.2, 0.1, where the bar is the edge between a near
wall and a far one, with depths 5, 5, 5 | 9, 9. A box average at the middle pixel gives (0.9 + 0.7 + 0.8 + 0.2 + 0.1) / 5
= 0.54, dragged down by the far wall.

The fix is to weigh each neighbor by how much it looks like the middle pixel. A neighbor with another depth gets a
weight near 0 and drops out, and the average stays on one surface. Weights that fall to 0 at an edge are what makes a blur
edge-aware; the same idea is the bilateral blur of [sun shadows](../light/sun-shadows-2.md).

Strata's ambient occlusion does this in `Strata/shaders/Effects/AODenoise.comp.slang`. The excerpt below has a vector type
`float4` of four numbers, `int2` of two :term[integers]{id=integer}, and `exp`, the :term[exponential function]{id=exponential-function}. Each of the 5 taps gets a tent weight
(0.5, 1, 1, 1, 0.5), a weight from depth and a weight from the angle between normals. The occlusion pass turns its samples by a fixed pattern of 16 rotations, one for each pixel of a 4 by 4 block. The tent weights make the 5 by 5 average count each rotation exactly once.

```slang src="Strata/shaders/Effects/AODenoise.comp.slang#L74-L89"
float depthScale = -c_DepthSharpness / centerNormalDepth.w;
float sum = 0.0;
float weightSum = 0.0;
for (int offset = -2; offset <= 2; offset++)
{
	int2 tap = center + step * offset;
	float4 normalDepth = s_NormalDepth[TileIndex(tap.x, tap.y)];
	if (normalDepth.w <= 0.0)
		continue;
	float weight = TentWeight(offset) * exp(depthScale * abs(normalDepth.w - centerNormalDepth.w))
		* NormalWeight(normalDepth.xyz, centerNormalDepth.xyz);
	float value = alongRows ? s_Occlusion[TileIndex(tap.x, tap.y)] : s_ResolvedRows[tap.y * c_Resolved + tap.x - 2];
	sum += value * weight;
	weightSum += weight;
}
return sum / weightSum; // The center weighs 1
```

1. **Line 74:** how fast the depth weight falls: 50 divided by the center's depth.
2. **Lines 77–82:** the loop over the five taps, which skips pixels that hold no surface.
3. **Lines 83–84:** a tap's weight is its tent weight times its depth weight times its normal weight.
4. **Lines 86–87:** the weighted values and the weights add up apart from each other.
5. **Line 89:** dividing by the weights' sum makes the weights add to 1.

:::example[The depth weight at an edge]
The depth weight is $e^{-50 d}$, where $d$ is the depth difference divided by the center's depth. A neighbor on the same
wall with a 1 % difference has $d = 0.01$ and a weight of $e^{-0.5} = 0.61$. A neighbor across the edge, 9 against 5, has
$d = 0.8$ and a weight of $e^{-40}$, about 4 × 10⁻¹⁸, which is 0 for all purposes.
:::

Try it: a center pixel of value 0.5 has two neighbors at the same depth, both weight 1, with values 0.7 and 0.3. Give the
average with the center's weight 1.

:::answer
(0.5 + 0.7 + 0.3) / 3 = 0.5. The weights are all 1, so this is a plain average of three values.
:::

Doing a 5 by 5 average in one pass would read 25 pixels. The shader runs a row of 5 and then a column of 5, 10 reads, and
weighs each tap against the pixel it is gathered for. Temporal denoising, which averages over earlier frames, is a
different technique that this page does not cover.

## Common mistakes

- **Filtering after sampling.** Symptom: a blur that leaves shimmer, because the false pattern is already in the numbers.
  Fix: filter before sampling, as mips do.
- **A kernel whose weights do not add to 1.** Symptom: a blurred picture that is lighter or darker than the original.
  Fix: divide by the sum of the weights.
- **A mip chain built from sRGB values.** Symptom: far surfaces darker than the same surface near. Fix: average in linear
  values and convert back, as the cooker does.
- **A dither that changes every frame.** Symptom: grain that boils on a picture that should be still. Fix: use a fixed
  pattern, such as the Bayer matrix.
- **Taking a smooth read for a filter.** Symptom: a linear read of a texture that still shimmers when far away. Fix: a
  read between samples is a guess; only a filter before sampling removes detail that is too fine.

## Summary

- A false frequency appears for any signal above half the sample rate; it is the distance to the nearest multiple of the
  rate, and an edge, a fence or a wheel can show it.
- Filtering replaces each sample with a weighted average; the kernel's weights add to 1, and sliding it along the signal is
  convolution.
- Filtering must come before sampling, so a texture keeps mips, each level a half-size average of the one before, and the
  graphics card reads the level whose texels match one pixel.
- Dithering adds a planned offset before rounding; the 4 by 4 Bayer table is a fixed pattern that keeps still pictures
  still.
- Denoising averages similar neighbors, with weights that fall to 0 across an edge.

## Check yourself

1. A signal has 30 samples a metre. Which pattern is below the Nyquist limit? (a) 20 repeats a metre (b) 14 repeats a
   metre (c) 15 repeats a metre (d) 40 repeats a metre

   :::answer{tests="aliasing"}
   (b). The limit is 15 repeats a metre, and only 14 lies below it. (c) is exactly at the limit, (a) and (d) are above it
   and appear as 10 and 10 repeats a metre.
   :::

2. The kernel 1, 2, 1 divided by 4 is slid along 4, 4, 12, 4, 4. What is the value at the 12?

   :::answer{tests="filtering"}
   (4 × 1 + 12 × 2 + 4 × 1) / 4 = 32 / 4 = 8. A wrong answer of 32 comes from forgetting the division, which leaves
   weights adding to 4.
   :::

3. A texture is 1,024 texels wide and shows on 128 pixels. Which level? (a) 0 (b) 3 (c) 8 (d) 128

   :::answer{tests="prefiltering"}
   (b). One pixel spans 1,024 / 128 = 8 texels, and the base-2 logarithm of 8 is 3. (c) is the texel count, not the level.
   :::

4. Why is the Bayer table better than a new random threshold each frame for a still picture?

   :::answer{tests="dithering"}
   The Bayer pattern depends only on the pixel's position, so a still picture gets the same result every frame. Random
   thresholds change each frame, and the grain boils.
   :::

5. A far pixel's neighbor lies on a different surface but has a similar value. Should an edge-aware blur keep its weight?

   :::answer{tests="denoising"}
   Depth and normal decide, not the value alone: a different surface gets a weight near 0 even if the value is close,
   because the blur must not smear two surfaces together.
   :::

## Practice

1. **Basic.** A sound is sampled at 44,100 samples a second. Give its Nyquist limit and the false frequency of a 30,000 Hz
   tone.

   :::answer[Worked solution]{tests="aliasing"}
   The limit is 44,100 / 2 = 22,050 Hz. The tone is above it, and |30,000 - 44,100| = 14,100 Hz, the false frequency.
   :::

2. **Basic.** Apply the weights 1, 2, 1 divided by 4 to the row 0, 8, 0, 8, 0 at its second, third and fourth places.

   :::answer[Worked solution]{tests="filtering"}
   Second: (0 + 16 + 0) / 4 = 4. Third: (8 + 0 + 8) / 4 = 4. Fourth: (0 + 16 + 0) / 4 = 4. The flickering row becomes a
   flat 4, the average, as a filter before sampling should make it.
   :::

3. **Medium.** A 2,048 by 1,024 texture has a mip chain. How many levels are there, and what do level 3 and the last level
   measure?

   :::answer[Worked solution]{tests="prefiltering"}
   The larger side is 2,048, which is 2 to the power 11, so there are 11 + 1 = 12 levels. Level 3 is 256 by 128. The last
   level is 1 by 1, because the smaller side stops at 1 after 10 halvings while the larger one needs 11.
   :::

4. **Medium.** Dither the flat value 5.375 over a 4 by 4 block with the Bayer table, and name the positions that show 6.

   :::answer[Worked solution]{tests="dithering"}
   A pixel shows 6 when $n \ge 10$. In the table these are 14 at (2, 1), 11 at (1, 2), 15 at (0, 3), 13 at (2, 3), 12 at
   (0, 1) and 10 at (3, 0). Six pixels in all, spread over the block.
   :::

5. **Hard.** A center pixel of 0.5 has a neighbor of 0.7 with weight 1 and a neighbor of 0.1 with a relative depth difference
   of 0.05. Weigh the second with $e^{-50 d}$ and average with the center's weight 1.

   :::answer[Worked solution]{tests="denoising"}
   The weight is $e^{-2.5} = 0.082$. The sum is 0.5 + 0.7 + 0.1 × 0.082 = 1.2082, and the weights add to 1 + 1 + 0.082 =
   2.082. The average is 1.2082 / 2.082 = 0.58. The far neighbor barely moves the result.
   :::

6. **Hard.** Optional, on your [Coin Run](../make/project-coin-run.md) or Checkpoint 4 of [Ship the finished game](../make/project-coin-run.md#ship-the-finished-game). Make a script turn the coin by a fixed angle each frame, not an angle scaled by
   `deltaTime`. Predict what 350°, 370° and 180° a frame look like, then try them.

   :::answer[Worked solution]{tests="aliasing" solution="sketches/basics-signals-coin.cpp"}
   The coins turn with `Coin`, in `Scripts/Coin.cpp`. Like `Spinner`, the example script the editor
   writes into a new script project, it turns by an angle per second times `deltaTime`; replace that product by the fixed angle.

   ```cpp pseudocode
   void OnUpdate(float deltaTime)
   {
   	const float degreesPerFrame = 350.0f; // try 370.0f and 180.0f
   	// turn the coin around the Y axis by degreesPerFrame
   }
   ```

   The coin repeats every 360°, so a turn of 350° looks like -10°: 10° backward each frame. 370° looks like 10° forward.
   Half a turn, 180°, is exactly the limit, and the coin flips between two views with no visible direction.

   ```cpp sketch="basics-signals-coin.cpp"
   // Practice 6: the turn a viewer sees when a coin turns by a fixed angle every frame.
   #include <cmath>
   #include <iostream>

   int main()
   {
   	const double angles[] = { 350.0, 370.0, 180.0, 90.0 };
   	for (const double angle : angles)
   		std::cout << angle << " degrees a frame looks like " << std::remainder(angle, 360.0) << " degrees\n";
   }
   ```

   ```text output-of="basics-signals-coin.cpp"
   350 degrees a frame looks like -10 degrees
   370 degrees a frame looks like 10 degrees
   180 degrees a frame looks like 180 degrees
   90 degrees a frame looks like 90 degrees
   ```

   1. **Line 7:** the angles to try.
   2. **Line 9:** the remainder after division by 360° is the turn the eye sees, between -180° and 180°.
   :::

## Where the book uses it

- [Textures](../assets/textures.md) reads mips and filtered texels, which the prefiltering section explains.
- [Spatial anti-aliasing](../image/spatial-aa.md) fights the stair steps and shimmer of edges that are sampled too coarsely.
- [Shadow basics](../light/shadow-basics.md) filters shadow edges with kernels like these.
- [Ambient occlusion](../indirect/ao.md) removes its noise with the weighted average of the denoising section.
- [Sound in a computer](../audio/sound-in-a-computer.md) uses the sample rate and the Nyquist limit.

## Further reading

- Mitchell and Netravali, "Reconstruction Filters in Computer Graphics" (SIGGRAPH 1988): the family that holds the
  Mitchell filter; advanced.
- Matt Pharr, Wenzel Jakob and Greg Humphreys, "Physically Based Rendering", chapter on sampling and reconstruction: a
  full treatment of aliasing and filters in rendering; advanced.
- Julius O. Smith, "Mathematics of the Discrete Fourier Transform": sampling and aliasing for sound; intermediate.
