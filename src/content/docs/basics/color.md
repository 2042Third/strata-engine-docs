---
id: basics/color
title: "Color and light for programmers: linear, sRGB and HDR"
description: "How a game stores and mixes color: values in proportion to light, the sRGB curve, HDR and half floats, luminance, gamut and the working color space."
kind: primer
size: L
tracks: [B, E]
needs: [basics/numbers, basics/math-matrices]
time: 80
learn:
  - id: srgb-convert
    text: compute the sRGB encoding and decoding of a channel value, and a blend of two colors done on linear values
  - id: encoded-vs-linear
    text: explain why pictures store encoded values while lighting, blending and filtering work on linear values
  - id: hdr-half
    text: name the range and the precision of a half float and explain why scene light needs floating point
  - id: luminance
    text: compute the luminance of a linear color and tell it from the luma of encoded values
  - id: color-space
    text: explain chromaticity, gamut, white point and the working color space, and a change of space as a 3×3 matrix
status: final
---

::::test-out

1. A gray in an sRGB picture is stored as 0.5. Does it send more or less than half the light of white, and about how much?

   :::answer{tests="srgb-convert"}
   Less. Decoding 0.5 gives $((0.5 + 0.055) / 1.055)^{2.4}$, which is about 0.21: one fifth of the light of white.
   :::

2. You blend a black pixel and a white pixel half and half. On a picture that stores sRGB values, is the stored value that shows the true mix of their light 0.5 or about 0.74?

   :::answer{tests="encoded-vs-linear srgb-convert"}
   About 0.74. Half the light of white is the linear value 0.5, and encoding it gives $1.055 \times 0.5^{1/2.4} - 0.055$, which is 0.735. The stored value 0.5 would show only a fifth of the light.
   :::

3. Compute the luminance of the linear color (1, 0.5, 0) with the weights 0.2126, 0.7152 and 0.0722.

   :::answer{tests="luminance"}
   $0.2126 \times 1 + 0.7152 \times 0.5 + 0.0722 \times 0 = 0.2126 + 0.3576 = 0.5702$.
   :::

4. What does a half float store when you give it 70000, and what when you give it 2049?

   :::answer{tests="hdr-half"}
   The largest half float is 65504, so 70000 overflows to infinity. Between 2048 and 4096 the values are 2 apart, so 2049 lies halfway between 2048 and 2050 and is stored as 2048.
   :::

5. The first column of a matrix that changes color space is (0.63, 0.07, 0.02). What does the matrix give for the color (0.5, 0, 0)?

   :::answer{tests="color-space"}
   The color (0.5, 0, 0) has only a red part, so the result is half of the first column: (0.315, 0.035, 0.01). The green and blue parts are 0 and add nothing.
   :::

::::

## Why you will need this

Every picture in a game is a grid of numbers. The numbers mean light only if you know how they were made. A color picked in a paint tool, a lamp in a scene and a pixel on a screen use different scales, and mixing them without care gives muddy shadows, dark blurs and flat fires.

Other pages rely on this one. [Textures](../assets/textures.md) tells which images hold colors and which hold data. [Why post-processing exists](../image/why-post.md) and [Tone mapping](../image/tone-mapping.md) squeeze the light of a scene into a picture that a screen can show. [Encoding the final picture](../image/encoding.md) writes that picture into :term[bytes]{id=byte}. [Drawing the game user interface (UI)](../ui/drawing.md) uses display colors.

The page goes from one color as three numbers to the color space Strata lights in. Each idea starts with a small example worked by hand, then gives the formula and the code. The sketches are small C++ programs; their output is real. You can follow every step by hand.

This page needs no project and no download. Each sketch is a whole program: save it as `sketch.cpp` and compile it in the terminal of [How a C++ program is built](build.md#open-a-terminal-that-finds-a-compiler), with C++20 and the `glm` headers of your Strata folder. On Windows, run `cl /std:c++20 /EHsc /I "<Strata folder>\StrataScriptCore\ThirdParty\glm" sketch.cpp` and then `.\sketch.exe`. On Linux and macOS, run `c++ -std=c++20 -I "<Strata folder>/StrataScriptCore/ThirdParty/glm" sketch.cpp -o sketch` and then `./sketch`. Without a compiler, read each output and its notes.

## A color is three numbers and an alpha

A screen is a grid of pixels, and each pixel mixes a red, a green and a blue light. A **color channel** is one of the three numbers, the amount of one of these lights, from 0 for none to 1 for full strength. The color (1, 0, 0) is red, (1, 1, 1) is white, (0, 0, 0) is black and (1, 0.5, 0) is orange.

Files and thumbnails keep each channel in one byte, a whole number from 0 to 255, as [Numbers](numbers.md) explains. The pixel then has four bytes: red, green, blue and alpha. Alpha is a fourth channel that says how solid the pixel is: 0 is fully transparent and 1, or 255 as a byte, is fully opaque. This layout of red, green, blue and alpha in eight bits each (RGBA8) is the usual form of a picture file. To convert, multiply by 255 and round to the nearest whole number.

:::example[Orange as four bytes]
Take the color (1, 0.5, 0) with an alpha of 1. The channel values 1, 0.5, 0 and 1 become 255, 127.5, 0 and 255. A byte has no fraction, so 127.5 rounds to 128 and the pixel is (255, 128, 0, 255).

Reading it back gives 128 / 255, which is 0.502. The byte lost at most 1 / 510, about 0.002, to rounding.
:::

Try it: compute the four bytes of the color (0.2, 0.6, 1, 0.5).

:::answer
$0.2 \times 255 = 51$, $0.6 \times 255 = 153$, $1 \times 255 = 255$ and $0.5 \times 255 = 127.5$, which rounds to 128. The pixel is (51, 153, 255, 128).
:::

You meet the same four numbers in Strata in three places. The Inspector draws a color property as fields for **R**, **G**, **B** and **A** and a small square of the color that opens a picker. A script reads the color of a UI element with `GetColor`, four numbers from 0 to 1. The editor's own palette is a set of named sRGB colors, used with an alpha.

## Linear color is in proportion to light

Light adds up. Two equal lamps light a wall twice as much as one. A **linear color** is a color whose channel values are in proportion to the amount of light: doubling the light doubles the value, and adding two lights adds their values.

Averaging works the same way. A blur, a smooth blend and the shrinking of a picture all average pixels. The average of the numbers is the light that a camera far away would collect from both pixels, but only when the numbers are in proportion to light.

:::example[Two lamps and two pixels]
One lamp lights a wall with 0.2 units of light and a second lamp adds 0.3. Together they give 0.2 + 0.3 = 0.5 units.

Now blur two neighboring pixels that carry 0.2 and 0.6 units. Their average is (0.2 + 0.6) / 2 = 0.4, the light you collect from the pair.
:::

Try it: three pixels carry 0.1, 0.1 and 0.4 units of light. What does a blur over all three give?

:::answer
$(0.1 + 0.1 + 0.4) / 3 = 0.2$ units of light.
:::

A renderer does all its sums of light on linear values: lights add, light bounces multiply by the color of a surface, and a blur averages. The question for the rest of the page is why the numbers in a picture file are often not linear.

## Eight bits spread evenly would band in the shadows

The eye judges a change of brightness against the brightness that is already there. A step of 0.004 units on a wall of 0.01 units is a change of 40 %, which you see. The same step on a wall of 0.8 units is 0.5 %, which you do not. Dark shades therefore need finer steps than bright ones.

**Quantization** is the rounding of a value to one of a limited list of levels. One byte holds 256 levels, so every channel of a picture is rounded to one of them.

**Banding** is the visible stripes that appear in a smooth gradient when neighboring levels differ too much to look like one shade.

:::example[Counting the levels of the shadows]
Store light in proportion to its amount, with the code 255 as the light of white. The codes 0, 1 and 2 mean the light 0, 0.0039 and 0.0078. Only three levels lie below 1 % of the light of white, and going from code 1 to code 2 doubles the light.

Near white, going from code 200 to code 201 changes the light by 0.5 %. The levels are fine where the eye does not need them and too coarse where it does.
:::

The cure is to give the dark values more codes. **Gamma encoding** stores a power of the light, a curve that lifts dark values, instead of the light itself: the code is about the light raised to the power 1 / 2.2.

A **transfer function** is the rule that converts between the amount of light and the stored value. Displays also turn a stored value back into light with a curve close to a power of 2.2, so a picture made this way shows the right light.

::figure{id=ramp-banding}

The next section gives the exact rule that computers use.

## The sRGB transfer function converts both ways

**sRGB** is the standard for color on ordinary displays and in pictures: three primary lights, a white and one curve.

The **sRGB transfer function** is that curve. It has a straight piece for the darkest values and a power for the rest.

Take a linear value $c$ and its stored value $s$. For $c$ up to 0.0031308 the encoding is a straight line:

$$s = 12.92\,c$$

Here $c$ is the linear value and $s$ the stored value, both from 0 to 1. Above 0.0031308 the encoding is a power:

$$s = 1.055\,c^{1/2.4} - 0.055$$

Read $c^{1/2.4}$ as the 2.4th root of $c$. To decode, use a straight line for $s$ up to 0.04045:

$$c = s / 12.92$$

Here $/$ is a division. Above 0.04045 the decoding is the reverse power:

$$c = \left(\frac{s + 0.055}{1.055}\right)^{2.4}$$

Raising to the power 2.4 undoes the 2.4th root. The straight piece keeps the curve from being infinitely steep at 0, where a power curve would turn a tiny change of dark light into a large change of the stored value.

Check the limits. The value 0 gives 0 and the value 1 gives $1.055 - 0.055 = 1$, so black and white stay. The two pieces meet where $12.92 \times 0.0031308 = 0.04045$, which is why the decoding switches there.

Strata writes the same two formulas in its shaders, in the Slang language. A shader runs on the :term[graphics card]{id=gpu}.

Three things differ from C++ with `glm`. The type `float3` is a vector of three floats like `glm::vec3`. The functions `max` and `pow` work on each channel. The call `select(test, a, b)` takes `a` in each channel where the test holds and `b` elsewhere.

```slang src="Strata/shaders/Include/Common.slang#L25-L39"
// sRGB transfer functions (IEC 61966-2-1).
float3 LinearToSRGB(float3 color)
{
	color = max(color, float3(0.0));
	float3 low = color * 12.92;
	float3 high = 1.055 * pow(color, float3(1.0 / 2.4)) - 0.055;
	return select((color <= float3(0.0031308)), low, high);
}

float3 SRGBToLinear(float3 color)
{
	float3 low = color / 12.92;
	float3 high = pow((color + 0.055) / 1.055, float3(2.4));
	return select((color <= float3(0.04045)), low, high);
}
```

1. **Line 28:** a negative light has no stored value, so the encoding first clamps it to 0.
2. **Lines 29–31:** both pieces are computed for every channel, and `select` keeps the straight piece where the value is at most 0.0031308.
3. **Lines 36–38:** the decoding mirrors it with the limit 0.04045.

:::example[Middle gray, light 0.18]
Light 0.18 is above 0.0031308, so use the power. $0.18^{1/2.4}$ is 0.4894, times 1.055 is 0.5163, minus 0.055 is 0.4613. The sketch carries more digits and shows 0.4614. As a byte this is 118, close to the middle of 0 to 255 although the light is under a fifth of white. A value of 0.001 is below the limit, so the straight piece gives $12.92 \times 0.001 = 0.01292$, byte 3.

Now blend black (0) and white (1) in half. On stored values the average is 0.5, which decodes to the light 0.214. In light the average is 0.5, which is stored as 0.7354, byte 187.5, which rounds to 188.
:::

::figure{id=blend-both-ways}

:::question[Why do the programs start with lines I have not seen?]
Each program starts with `#include` lines and calls functions such as `std::pow(`; [Programming 3](programming-3.md) explains both. [Memory](cpp-memory.md) explains the `*` in `const char* name`.
:::

The sketch below does all of this with `std::pow`. Run the numbers against your hand work.

```cpp sketch="basics-color-srgb.cpp"
// The sRGB transfer function, and a 50 % blend of black and white done on each kind of value.
#include <cmath>
#include <cstdio>

float Encode(float linear)
{
	return linear <= 0.0031308f ? linear * 12.92f : 1.055f * std::pow(linear, 1.0f / 2.4f) - 0.055f;
}

float Decode(float encoded)
{
	return encoded <= 0.04045f ? encoded / 12.92f : std::pow((encoded + 0.055f) / 1.055f, 2.4f);
}

int main()
{
	std::printf("light 0.18 is stored as %.4f, byte %.0f\n", Encode(0.18f), Encode(0.18f) * 255.0f);
	std::printf("light 0.001 is stored as %.5f, byte %.1f\n", Encode(0.001f), Encode(0.001f) * 255.0f);
	std::printf("black and white averaged on sRGB values: light %.4f\n", Decode(0.5f));
	std::printf("black and white averaged as light: stored %.4f, byte %.1f\n", Encode(0.5f), Encode(0.5f) * 255.0f);
	return 0;
}
```

```text output-of="basics-color-srgb.cpp"
light 0.18 is stored as 0.4614, byte 118
light 0.001 is stored as 0.01292, byte 3.3
black and white averaged on sRGB values: light 0.2140
black and white averaged as light: stored 0.7354, byte 187.5
```

1. **Lines 5–8:** `Encode` is the encoding formula: the straight piece for small values, the power for the rest.
2. **Lines 10–13:** `Decode` is its inverse.
3. **Lines 19–20:** the average of the stored values, decoded to light, against the average of light, encoded.

The program prints the middle gray, the dark value and both blends. The last two lines are the point: a blend on stored values gives a dark mix, a blend on light gives a bright one.

The second sketch counts the codes that describe the shadows. It shows what the curve buys.

```cpp sketch="basics-color-bands.cpp"
// How many of the 256 codes of a byte describe the shadows, up to 1 % of the light of white.
#include <cmath>
#include <cstdio>

float Decode(float encoded)
{
	return encoded <= 0.04045f ? encoded / 12.92f : std::pow((encoded + 0.055f) / 1.055f, 2.4f);
}

int main()
{
	int linearCodes = 0;
	int srgbCodes = 0;
	for (int code = 0; code < 256; code++)
	{
		const float value = static_cast<float>(code) / 255.0f;
		linearCodes += value <= 0.01f ? 1 : 0;       // the code means light in proportion
		srgbCodes += Decode(value) <= 0.01f ? 1 : 0; // the code means an sRGB value
	}
	std::printf("linear: %d codes, sRGB: %d codes\n", linearCodes, srgbCodes);
	return 0;
}
```

```text output-of="basics-color-bands.cpp"
linear: 3 codes, sRGB: 26 codes
```

1. **Lines 14–19:** the loop visits each of the 256 codes and turns it into the value it stands for.
2. **Lines 17–18:** each line counts the codes whose light is at most 1 % of white, once with the code read as light and once read as an sRGB value.

The loop visits each of the 256 codes. A linear picture spends 3 codes on light up to 1 % of white and an sRGB picture spends 26, so the gradient bands far less.

::figure{id=srgb-curve}

Try it: decode the stored value 0.02. Is it above or below 0.04045?

:::answer
The value is below, so the straight piece applies: $0.02 / 12.92 = 0.00155$ units of light.
:::

## Color data is sRGB, other data is linear

Not every image holds colors. Photographs, painted base color maps and UI colors are meant to be seen, so they are stored as sRGB. A normal map, a roughness map and a mask hold numbers that mean something else, such as a direction, a roughness of 0.5 or a mask of 1. Such numbers are **linear data**: stored as they are, never decoded.

Strata's texture importer names the difference in `TextureUsage`. Usage `Color` is sRGB (base color, the color of emitted light, UI), `NormalMap` and `Data` (roughness, metallic, occlusion, masks) are linear, and `HDR` is a floating-point texture, used for environment maps. A normal map marked as `Color` would be decoded as if it were light, and every direction in it would tilt.

The rule has a second half. Sums of light, blends and filtering must work on linear values, because only linear values add up. A graphics card can decode an sRGB texture before it filters it, which [Textures](../assets/textures.md) explains.

The numbers you type into Strata's properties are of two kinds too, and the Inspector draws both with the same widget and shows the stored numbers.

| Field | Kind |
| --- | --- |
| `MaterialProperties::BaseColor` and `EmissiveColor` | linear |
| Light `Color` (directional, point, spot) | linear |
| `HeightFogComponent::Color` | linear |
| `UIImageComponent` and `UITextComponent` colors, `TextComponent::Color` | display (sRGB) |
| `CameraComponent::ClearColor` | sRGB-encoded |

Strata's comment on the property kinds `Color3` and `Color4` calls every color linear, which is wrong for the last two rows. Only some help texts in the Inspector say which kind a field is.

:::caution
Typing a color you picked in a paint tool into a linear field gives a paler, lighter surface. Take the sRGB color (0.8, 0.2, 0.2). Its linear value is (0.604, 0.033, 0.033). Typed as it is, (0.8, 0.2, 0.2) gives the green and blue channels six times more light, so the red looks washed out. glTF files keep their base color factors as linear values, and the import setting **Base Color Factors Are sRGB** repairs files from exporters that wrote sRGB.
:::

## High dynamic range has no top limit

A byte stops at 1. The world does not. A white wall in the sun and the sun itself differ by a factor of thousands. A lit sign or a monitor is many times brighter than a white sheet of paper in a room.

Strata's material help texts put a monitor at about 200 nits and a lit sign at about 1,000, where a nit is a unit of the light a surface sends out. [Light units](../light/units-exposure.md) explains it.

**High dynamic range (HDR)** values are values with no upper limit at 1: a color can be 10, or 5,000, times white.

**Scene-linear** values are linear values that stand for the light of the scene, not for what a display will show. A renderer lights in scene-linear values and only at the end squeezes them into the 0 to 1 of the screen.

:::example[A sun and a wall]
Say a white wall in the shade carries 1 unit of light and a patch of sun on it carries 20. Clamped to 1, both turn white and the picture cannot tell them apart. A blur or a glow over the sun now has too little light to spread: a clamped sun glows like a white wall.

An 8-bit byte cannot hold 20, and it cannot hold 0.00001 either. Scene-linear values need floating point, which [Numbers](numbers.md) explains: a sign, an exponent and a fraction, so that the steps grow with the value.
:::

Thirty-two bits per channel would do. A frame of 1920 × 1080 pixels has 2,073,600 pixels. With four 32-bit channels each pixel takes 16 bytes and the frame takes 33.2 million bytes; with four 16-bit channels it takes 16.6 million bytes. The renderer reads and writes such frames many times, so the smaller size matters.

## A half float keeps three digits in 16 bits

A **half-float**, also called half precision, is a 16-bit floating-point number: 1 sign bit, 5 exponent bits and 10 fraction bits. Strata's high dynamic range (HDR) render target uses it as a format of four half floats per pixel: red, green, blue and alpha as 16-bit floating-point numbers (RGBA16F).

Its limits follow from the bits. The largest value is 65504. Below it, 11 significant bits are kept (10 stored and one implied), so the step between neighbors is 1 / 1024 of the value at most: about three decimal digits. Below $2^{-14}$, about 0.000061, the numbers are :term[subnormal]{id=subnormal-number}: the exponent stops falling and the step stays $2^{-24}$, about 0.00000006, so the precision drops as the value shrinks.

| Range of the value | Step between half floats |
| --- | --- |
| 1 to 2 | 0.000977 |
| 2048 to 4096 | 2 |
| 32768 to 65504 | 32 |
| below 0.000061 | 0.00000006 |

:::example[What 16 bits keep]
The value 2049 lies between the steps 2048 and 2050 and rounds to 2048. The value 3000.7 becomes 3000, an error of 0.7. The value 0.1 becomes 0.099975586. The value 0.00001 is subnormal and becomes 0.0000100136, which is 0.14 % off.
:::

The sketch rounds a float to 11 significant bits. The call `std::frexp` splits a number into a fraction of at least 0.5 and a power of two, and `std::ldexp` scales by a power of two. Watch which inputs change and which do not.

```cpp sketch="basics-color-half.cpp"
// What a half float keeps: a float rounded to 11 significant bits, with its range and its subnormal values.
#include <cmath>
#include <cstdio>

float RoundToHalf(float value)
{
	const float size = std::fabs(value);
	if (size >= 65520.0f) // halfway to the next step after 65504, which a half float does not have
		return value < 0.0f ? -INFINITY : INFINITY;
	if (size < 1.0f / 16384.0f) // below 2^-14 the step stays 2^-24, so fewer bits are kept
		return std::nearbyint(value * 16777216.0f) / 16777216.0f;
	int exponent = 0;
	std::frexp(value, &exponent); // value = m * 2^exponent with m from 0.5 up to 1
	const float scale = std::ldexp(1.0f, 11 - exponent); // 11 bits of m are kept
	return std::nearbyint(value * scale) / scale;
}

int main()
{
	const float values[] = { 1.0009766f, 1.0001f, 2049.0f, 3000.7f, 0.1f, 65504.0f, 70000.0f, 0.00006f, 0.00001f, 1e-8f };
	for (const float value : values)
		std::printf("%-10g is stored as %.8g\n", value, RoundToHalf(value));
	return 0;
}
```

```text output-of="basics-color-half.cpp"
1.00098    is stored as 1.0009766
1.0001     is stored as 1
2049       is stored as 2048
3000.7     is stored as 3000
0.1        is stored as 0.099975586
65504      is stored as 65504
70000      is stored as inf
6e-05      is stored as 6.0021877e-05
1e-05      is stored as 1.001358e-05
1e-08      is stored as 0
```

1. **Lines 8–9:** from 65520 on, a half float has no value to round to, so the result is infinity.
2. **Lines 10–11:** a subnormal value is rounded to a multiple of $2^{-24}$.
3. **Lines 12–15:** a normal value keeps 11 bits, so the step depends on its power of two.

A value that overflows is a bug in a picture: infinity or a number that is not a number spreads through every blur that touches it. Strata's shader function `SanitizeHDR` therefore clamps negative light and not-a-number to 0 and everything above 65000 to 65000, before a color goes into an HDR target. The renderer also multiplies its light by a power of two, the pre-exposure, so that dark and bright scenes both sit in the range where half floats are fine; [Why post-processing exists](../image/why-post.md) tells the rest.

Try it: what does a half float store for 6000.2? Between which two steps does it lie?

:::answer
The values between 4096 and 8192 are 4 apart. 6000.2 lies between 6000 and 6004, closer to 6000, so the half float stores 6000.
:::

## Luminance is how bright a color looks

Green looks brighter than blue at the same amount of light. **Luminance** is the measure of how bright a color looks, a single number for a color of three. The eye reacts most to green, a little to red and very little to blue, so the number is a weighted sum of the channels.

**Luminance (Y)** is the luminance of a linear color in the primary lights of sRGB, called Rec. 709 colors (a later section names them), which is $Y = 0.2126\,r + 0.7152\,g + 0.0722\,b$. Here $r$, $g$ and $b$ are the linear channels and $Y$ is the luminance, in the same units as the channels. Read it as a :term[dot product]{id=dot-product} of the color with the weights (0.2126, 0.7152, 0.0722), which add up to 1, so white (1, 1, 1) has the luminance 1.

Strata computes it exactly so, in the file that meters the exposure of the image.

```slang src="Strata/shaders/Include/Exposure.slang#L14-L21"
#define ST_HISTOGRAM_BINS     256u
#define ST_HISTOGRAM_MIN_LOG2 -12.0
#define ST_HISTOGRAM_MAX_LOG2 16.0

float Luminance(float3 color)
{
	return dot(color, float3(0.2126, 0.7152, 0.0722));
}
```

The three `#define` lines above it size the table of luminances the exposure meter counts. The function takes a `float3` and returns the dot product of the color with the weights. The sum is only right on linear values, which is what the pipeline holds at that point.

**Luma** is a sum of the same kind taken on encoded values. The pass of Strata that smooths jagged edges weighs display-encoded values with the weights 0.299, 0.587 and 0.114, because its algorithm asks for that. A luma and a luminance are different numbers, and comparing them is a mistake.

:::example[One color, two numbers]
The stored color (0.5, 0.5, 0) decodes to the linear color (0.214, 0.214, 0). Its luminance is $0.2126 \times 0.214 + 0.7152 \times 0.214 = 0.199$.

The luma of the stored values is $0.299 \times 0.5 + 0.587 \times 0.5 = 0.443$. The two numbers differ by a factor of more than two, because the first measures light and the second measures stored values.
:::

Try it: compute the luminance of the linear color (0.8, 0.4, 0.1).

:::answer
$0.2126 \times 0.8 + 0.7152 \times 0.4 + 0.0722 \times 0.1 = 0.1701 + 0.2861 + 0.0072 = 0.4634$.
:::

## Chromaticity is a color without its brightness

Two colors can differ in brightness only: a dim red and a bright red are the same red. **Chromaticity** is what a color is apart from its brightness, written as two numbers $x$ and $y$.

To get there, a color standard of 1931 describes any color the eye can see with three numbers $X$, $Y$ and $Z$, called $XYZ$, where $Y$ is the luminance. A linear Rec. 709 color becomes $XYZ$ through a 3×3 matrix, whose three rows are these sums:

- $X = 0.4124\,r + 0.3576\,g + 0.1805\,b$
- $Y = 0.2126\,r + 0.7152\,g + 0.0722\,b$
- $Z = 0.0193\,r + 0.1192\,g + 0.9505\,b$

Here $r$, $g$ and $b$ are the linear channels and $X$, $Y$ and $Z$ the results. Each result is the dot product of one row of the matrix with $(r, g, b)$; the second row is the luminance. The chromaticity drops the brightness by dividing by the sum:

$$x = \frac{X}{X + Y + Z}, \qquad y = \frac{Y}{X + Y + Z}$$

The numbers $x$ and $y$ are the two chromaticity coordinates. Doubling a color doubles $X$, $Y$ and $Z$ and the sum, so $x$ and $y$ stay.

:::example[The chromaticity of red and of white]
Pure linear red (1, 0, 0) is the first column: $X = 0.4124$, $Y = 0.2126$, $Z = 0.0193$. The sum is 0.6443, so $x = 0.6401$ and $y = 0.3300$.

White (1, 1, 1) adds the three columns: $X = 0.9505$, $Y = 1$, $Z = 1.089$. The sum is 3.0395, so $x = 0.3127$ and $y = 0.3290$.
:::

Try it: pure linear green (0, 1, 0) is the second column (0.3576, 0.7152, 0.1192). Compute its $x$ and $y$.

:::answer
The sum is 1.192, so $x = 0.3576 / 1.192 = 0.3$ and $y = 0.7152 / 1.192 = 0.6$.
:::

The sketch repeats the calculation for five colors, white and double white among them. Look at the last two lines.

```cpp sketch="basics-color-chromaticity.cpp"
// Chromaticity: linear Rec. 709 color to XYZ with the matrix of its primaries, then x and y.
#include <cstdio>
#include <glm/glm.hpp>

void Print(const char* name, const glm::dvec3& rgb)
{
	// glm builds a matrix column by column: these are the columns for red, green and blue.
	const glm::dmat3 toXYZ(0.4124, 0.2126, 0.0193, 0.3576, 0.7152, 0.1192, 0.1805, 0.0722, 0.9505);
	const glm::dvec3 xyz = toXYZ * rgb;
	const double sum = xyz.x + xyz.y + xyz.z;
	std::printf("%-6s Y %.4f  x %.4f  y %.4f\n", name, xyz.y, xyz.x / sum, xyz.y / sum);
}

int main()
{
	Print("red", glm::dvec3(1.0, 0.0, 0.0));
	Print("green", glm::dvec3(0.0, 1.0, 0.0));
	Print("blue", glm::dvec3(0.0, 0.0, 1.0));
	Print("white", glm::dvec3(1.0, 1.0, 1.0));
	Print("white2", glm::dvec3(2.0, 2.0, 2.0));
	return 0;
}
```

```text output-of="basics-color-chromaticity.cpp"
red    Y 0.2126  x 0.6401  y 0.3300
green  Y 0.7152  x 0.3000  y 0.6000
blue   Y 0.0722  x 0.1500  y 0.0600
white  Y 1.0000  x 0.3127  y 0.3290
white2 Y 2.0000  x 0.3127  y 0.3290
```

1. **Line 8:** `glm` fills a matrix column by column, so the first three numbers are the column of red.
2. **Lines 9–11:** the color becomes $XYZ$, the three numbers are summed, and each of $x$ and $y$ is a share of the sum.
3. **Lines 19–20:** white and twice white have the same chromaticity and differ only in luminance.

Plot every color the eye can see by its $x$ and $y$ and you get a shape with a round top and a straight bottom edge. Its curved edge holds the pure colors of single wavelengths, from violet through green to red, and a straight edge closes it with the purples. White sits near the middle.

::figure{id=chromaticity-diagram}

## A color space is primaries, a white and a curve

A **color space** is a rule for what three numbers mean: three primaries, a white point and a transfer function. The primaries are the chromaticities of the pure red, green and blue of the space.

A **white point** is the chromaticity that the color (1, 1, 1) has.

**D65** is the standard white of daylight, at a temperature of about 6504 kelvin, with $x = 0.3127$ and $y = 0.3290$: the white that the sketch above printed.

The **gamut** of a color space is the set of colors it can write with channels from 0 to 1. On that diagram it is the triangle between the three primaries, because any mix of three lights lies inside the triangle they span. A color outside the triangle needs a negative channel. A saturated green of a wide-gamut space is such a color in a smaller space.

:::example[A green that a smaller gamut cannot hold]
The Rec. 2020 standard for television beyond high definition has primaries farther apart than those of sRGB. Its pure green (0, 1, 0) is, in the numbers of sRGB's primaries, (−0.5876, 1.1329, −0.1006), found with the matrix that the next section builds. Two channels are negative: no light of sRGB's primaries makes that color.
:::

Try it: a conversion gives (1.2, 0.4, −0.05). Is the color inside the gamut of the target space?

:::answer
No. The blue channel is negative, so the color lies outside the triangle. The red channel of 1.2 is not outside: it only means more light than white, which HDR allows.
:::

## The working color space is where the lighting runs

**BT.709**, written Rec. 709 in this book, is the standard for high-definition television. Its primaries are (0.64, 0.33), (0.30, 0.60) and (0.15, 0.06), and its white point is D65. The sRGB standard uses the same primaries and the same white and adds its transfer function, so a linear color in Rec. 709 primaries and a linear color in sRGB are the same numbers.

The **working color space** is the color space a program computes in. Strata lights in scene-linear Rec. 709: the primaries of sRGB, the white D65 and no transfer function, because all lighting sums need linear values. The renderer's own comment calls it scene-linear sRGB light, and its code builds the matrices between linear sRGB and $XYZ$ from the primaries and the white written above.

:::why
Pictures, base colors and the UI of a game are sRGB, and the glTF format keeps its colors in the same primaries. A working space with these primaries needs no matrix at the edges: a texture is decoded and used. The cost is the gamut. A color that has a negative channel in this space cannot be held: the renderer clamps negative light to 0, so a wide-gamut source loses its most saturated colors when it enters.
:::

Changing from one color space to another is a 3×3 matrix applied to the linear color $(r, g, b)$, as [Matrices](math-matrices.md) explains. The matrix is built in two steps. The matrix of the source space takes the color to $XYZ$, and the inverse of the matrix of the target space brings it from $XYZ$ into the target. Each space's matrix comes from its three primaries and its white, so that (1, 1, 1) lands on the white.

The change works on linear values. Decode an sRGB picture first, apply the matrix, then encode in the transfer function of the target.

The sketch builds both matrices as the renderer does, with `glm::inverse` for the inverse, and applies the change to the Rec. 2020 green of the last section. It is the program that printed the numbers there.

```cpp sketch="basics-color-spaces.cpp"
// A color space as a matrix: built from three primaries and a white, then one change of space.
#include <cstdio>
#include <glm/glm.hpp>

glm::dvec3 ToXYZ(const glm::dvec2& xy)
{
	return glm::dvec3(xy.x / xy.y, 1.0, (1.0 - xy.x - xy.y) / xy.y);
}

glm::dmat3 RGBToXYZ(const glm::dvec2 primaries[3], const glm::dvec2& white)
{
	const glm::dmat3 columns(ToXYZ(primaries[0]), ToXYZ(primaries[1]), ToXYZ(primaries[2]));
	const glm::dvec3 scale = glm::inverse(columns) * ToXYZ(white); // makes (1, 1, 1) the white
	return columns * glm::dmat3(scale.x, 0.0, 0.0, 0.0, scale.y, 0.0, 0.0, 0.0, scale.z);
}

int main()
{
	const glm::dvec2 d65(0.3127, 0.3290);
	const glm::dvec2 rec709[3] = { { 0.64, 0.33 }, { 0.30, 0.60 }, { 0.15, 0.06 } };
	const glm::dvec2 rec2020[3] = { { 0.708, 0.292 }, { 0.170, 0.797 }, { 0.131, 0.046 } };
	const glm::dmat3 change = glm::inverse(RGBToXYZ(rec709, d65)) * RGBToXYZ(rec2020, d65);
	const glm::dvec3 green = change * glm::dvec3(0.0, 1.0, 0.0);
	std::printf("pure Rec. 2020 green in Rec. 709: (%.4f, %.4f, %.4f)\n", green.x, green.y, green.z);
}
```

```text output-of="basics-color-spaces.cpp"
pure Rec. 2020 green in Rec. 709: (-0.5876, 1.1329, -0.1006)
```

1. **Lines 5–8:** a chromaticity becomes an $XYZ$ color at luminance 1, from $X = x / y$ and $Z = (1 - x - y) / y$.
2. **Lines 12–14:** the white's $XYZ$ is divided by the primaries' columns to get three scales, so that (1, 1, 1) is the white.
3. **Line 22:** the change is the inverse of the Rec. 709 matrix times the Rec. 2020 matrix.

## Common mistakes

- **Blending or filtering encoded values.** The symptom is a dark seam where two colors meet, a blur that darkens bright shapes, or a smaller picture that looks darker. The fix is to decode, blend or filter, then encode, or to let the graphics card decode the texture.
- **Marking a normal map as sRGB.** The symptom is lighting that looks tilted or uneven, because the stored directions were decoded like colors. The fix is the usage `NormalMap` for a normal map and `Data` for roughness, metallic, occlusion and masks.
- **Comparing a luma with a luminance.** The symptom is a threshold that works on one image and fails on another, or a brightness that is off by a factor of two. The fix is to compute both on the same kind of value, linear for luminance.
- **Clamping HDR values at 1 too early.** The symptom is a sun that looks like a white wall, a glow that never appears and a flat sky. The fix is to keep scene-linear values until the tone mapping and to clamp only the final picture.
- **Typing sRGB numbers into a linear field.** The symptom is a pale or too bright material or light. The fix is to decode the color first, or to use the field that is documented as display color.
- **Encoding twice or not at all.** The symptom is a picture that is too light, with washed-out colors, or too dark. The fix is to track which kind of value each buffer holds, and to apply the curve once, at the picture's edge.

## Summary

- Compute the sRGB encoding and decoding of a channel value: the straight piece up to 0.0031308 (encoding) or 0.04045 (decoding), the 2.4 power above; for a blend, decode, mix, encode.
- Pictures store encoded values because 256 even steps of light would band in the shadows; lighting, blending and filtering add light and so need linear values.
- A half float holds values up to 65504 with about three digits, and loses precision below $2^{-14}$; scene-linear HDR light has no top limit and needs floating point.
- Luminance is $0.2126\,r + 0.7152\,g + 0.0722\,b$ on linear Rec. 709 values; a luma uses encoded values and is a different number.
- A color space is primaries, a white point and a transfer function; Strata lights in scene-linear Rec. 709, and a change of space is a 3×3 matrix on linear values.

## Check yourself

1. Which of these hold linear numbers in Strata? (a) The Base Color factor of a material. (b) The color of a UI text. (c) A normal map. (d) The clear color of a camera.

   :::answer{tests="encoded-vs-linear"}
   (a) and (c). The material's color factor is linear and a normal map is linear data. The UI text color and the camera's clear color are display (sRGB) values.
   :::

2. A blur averages two pixels that store the sRGB values 0.2 and 0.8. The stored average is 0.5. What stored value shows the true average of their light?

   :::answer{tests="srgb-convert encoded-vs-linear"}
   Decode both: 0.2 gives 0.0331 and 0.8 gives 0.6038. Their average is 0.3185, which encodes to about 0.60. The naive 0.5 shows too little light.
   :::

3. A code compares the luma of a pixel in a picture with the luminance of a light and finds them 2.2 times apart. Is the code wrong, and why?

   :::answer{tests="luminance"}
   The comparison is wrong. A luma is a weighted sum of encoded values and a luminance a weighted sum of linear values, so the two numbers do not measure the same thing. Compute both from linear values or both from encoded ones.
   :::

4. Which is true of a half float? (a) It stores 100000. (b) It stores 4097 exactly. (c) It stores 0.5 exactly. (d) Its precision is the same at every size.

   :::answer{tests="hdr-half"}
   Only (c). The largest value is 65504, so (a) fails. Between 4096 and 8192 the step is 4, so (b) fails. The value 0.5 is a power of two and exact. The step grows with the value, so (d) fails.
   :::

5. Two colors have the same chromaticity but one has four times the luminance. What is the relation of their linear channels?

   :::answer{tests="color-space"}
   The channels of the brighter color are four times those of the other. Scaling a color scales $X$, $Y$, $Z$ and their sum alike, so $x$ and $y$ stay the same.
   :::

## Practice

1. **Basic.** Encode the linear value 0.5 into sRGB by hand and give it as a byte. Then decode the byte 64.

   :::answer[Worked solution]{tests="srgb-convert"}
   0.5 is above 0.0031308: $1.055 \times 0.5^{1/2.4} - 0.055 = 1.055 \times 0.7491 - 0.055 = 0.7354$, which is byte $0.7354 \times 255 = 187.5$, rounded to 188. For the byte 64, $s = 64 / 255 = 0.251$, above 0.04045, so $c = ((0.251 + 0.055) / 1.055)^{2.4} = 0.290^{2.4} = 0.0513$.
   :::

2. **Basic.** Compute the luminance of the linear colors (0, 0, 1), (0, 1, 0) and (1, 1, 1). Which of the pure colors looks brightest?

   :::answer[Worked solution]{tests="luminance"}
   The weights give 0.0722, 0.7152 and 1. Pure green looks brightest among the pure colors, almost ten times brighter than pure blue.
   :::

3. **Medium.** An HDR target holds the value 4100.3 in a half float. Which value does it keep, and what is the relative error?

   :::answer[Worked solution]{tests="hdr-half"}
   Between 4096 and 8192 the step is 4, so the neighbors are 4100 and 4104, and 4100.3 is closer to 4100. The error is 0.3, which is $0.3 / 4100.3 = 0.007$ %, far below a visible change.
   :::

4. **Medium.** A texture of 1024 × 1024 pixels is stored as RGBA8 and as RGBA16F, without mip levels. How many bytes does each take, and how many more does the second need?

   :::answer[Worked solution]{tests="hdr-half"}
   The texture has 1,048,576 pixels. RGBA8 takes 4 bytes a pixel, 4,194,304 bytes; RGBA16F takes 8 bytes, 8,388,608 bytes. The second needs 4,194,304 bytes more: twice as much.
   :::

5. **Medium.** The $XYZ$ of the linear color (0, 0, 1) is (0.1805, 0.0722, 0.9505). Compute its chromaticity $x$ and $y$.

   :::answer[Worked solution]{tests="color-space"}
   The sum is 1.2032. So $x = 0.1805 / 1.2032 = 0.15$ and $y = 0.0722 / 1.2032 = 0.06$: the blue primary of Rec. 709.
   :::

6. **Hard.** Coin Run's time bar, from [the page on heads-up displays](../make/hud.md), could change color from green to red as time runs out. The color is a UI color, so its numbers are display (sRGB) values. In a program of your own, blend (0, 1, 0) to (1, 0, 0) halfway once on the stored values and once in linear light, and print the luminance of both middle colors.

   :::answer[Worked solution]{tests="srgb-convert luminance encoded-vs-linear" solution="sketches/basics-color-time-bar.cpp"}
   A UI color is display sRGB. The blend in linear light is decode, mix, encode. The sketch does both and weighs each result with the luminance weights after decoding.

   ```cpp sketch="basics-color-time-bar.cpp"
   // The time bar's color from green to red: blended on sRGB values, then in linear light.
   #include <cstdio>
   #include <glm/glm.hpp>

   glm::vec3 Decode(const glm::vec3& encoded)
   {
   	return glm::mix(encoded / 12.92f, glm::pow((encoded + 0.055f) / 1.055f, glm::vec3(2.4f)), glm::greaterThan(encoded, glm::vec3(0.04045f)));
   }

   glm::vec3 Encode(const glm::vec3& linear)
   {
   	return glm::mix(linear * 12.92f, 1.055f * glm::pow(linear, glm::vec3(1.0f / 2.4f)) - 0.055f, glm::greaterThan(linear, glm::vec3(0.0031308f)));
   }

   int main()
   {
   	const glm::vec3 green(0.0f, 1.0f, 0.0f);
   	const glm::vec3 red(1.0f, 0.0f, 0.0f);
   	const glm::vec3 weights(0.2126f, 0.7152f, 0.0722f);
   	const glm::vec3 onSRGB = glm::mix(green, red, 0.5f);
   	const glm::vec3 inLinear = Encode(glm::mix(Decode(green), Decode(red), 0.5f));
   	std::printf("sRGB blend (%.4f, %.4f, %.4f): luminance %.4f\n", onSRGB.r, onSRGB.g, onSRGB.b, glm::dot(Decode(onSRGB), weights));
   	std::printf("linear blend (%.4f, %.4f, %.4f): luminance %.4f\n", inLinear.r, inLinear.g, inLinear.b, glm::dot(Decode(inLinear), weights));
   	return 0;
   }
   ```

   ```text output-of="basics-color-time-bar.cpp"
   sRGB blend (0.5000, 0.5000, 0.0000): luminance 0.1986
   linear blend (0.7354, 0.7354, 0.0000): luminance 0.4639
   ```

   1. **Lines 5–13:** `Decode` and `Encode` apply the two formulas to three channels at once; `glm::mix` with a test takes the straight piece where the test holds.
   2. **Lines 20–21:** the first blend mixes stored values, the second decodes, mixes and encodes.
   3. **Lines 22–23:** each result is decoded to light before the luminance weights apply.

   The sRGB blend (0.5, 0.5, 0) has the luminance 0.1986. The linear blend is (0.7354, 0.7354, 0) and has 0.4639. Which looks right for a time bar is your choice: the linear blend is the one that mixes light correctly, and its middle is brighter.

   In the game's script, the update function computes the middle color with these functions and sets the bar's color. The line that logs the luminance uses `Log::Info`.

   ```cpp pseudocode
   const glm::vec3 linear = glm::mix(Decode(green), Decode(red), t);
   GetEntity().GetUI().SetColor(glm::vec4(Encode(linear), 1.0f));
   Log::Info("middle luminance ", glm::dot(linear, glm::vec3(0.2126f, 0.7152f, 0.0722f)));
   ```

   Here `t` goes from 0 to 1 as the time runs out. `SetColor` takes display (sRGB) values, so the blend is encoded before it is set.
   :::

## Where the book uses it

- [Textures](../assets/textures.md) sorts images into color and data, and explains how the graphics card decodes sRGB.
- [Why post-processing exists](../image/why-post.md) uses scene-linear values, half-float targets and luminance.
- [Tone mapping](../image/tone-mapping.md) turns scene-linear light of any size into the 0 to 1 of a display.
- [Encoding the final picture](../image/encoding.md) applies the sRGB curve and rounds the result to bytes.
- [Drawing the game UI](../ui/drawing.md) draws the UI colors, which are display values.

## Further reading

- IEC 61966-2-1:1999, the sRGB standard: the exact curve and primaries; advanced.
- Charles Poynton, "Digital Video and HD": gamma, luma and color spaces for programmers; intermediate.
- The glTF 2.0 specification, the section on materials: which color numbers are linear and which are sRGB; intermediate.
