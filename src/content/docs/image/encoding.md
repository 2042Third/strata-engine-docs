---
id: image/encoding
title: "Encoding, dithering and grain"
description: "How Strata turns display-linear light into the codes a target stores with no bands, and adds dither and film grain once, in the last pass."
kind: internals
size: L
tracks: [E]
needs: [image/grading, basics/signals]
time: 70
learn:
  - id: codes
    text: explain how Strata turns display-linear values into the codes a target stores, and why 256 codes leave bands in a dark gradient
  - id: dither-math
    text: compute the mean error and the noise power of rounding, a rectangular dither and a triangular dither for a value between two codes
  - id: last-pass
    text: explain why the dither and the film grain go once into the last pass that writes the display image, in the encoded domain
  - id: trace-pass
    text: trace which pass dithers for each anti-aliasing setting
  - id: run-tests
    text: predict what the two dither test cases of the renderer check, and say which check a rectangular dither would fail
since: 0.3.0
status: final
---

Look at a dark sky at dusk on a screen. The light changes very slowly from the horizon upward, and a good picture shows a smooth fade. A picture made with too few codes shows steps instead: wide bands, each one flat, with a visible edge between neighbors.

::compare{id=banding-pair}

The first picture of the pair stores the sky in 8 bits and rounds every pixel to the nearest code. The second adds a small planned noise before the rounding, and the bands are gone. The noise is there, but it is smaller than what an eye resolves at the viewing distance, and it breaks up the edges that the eye finds at once.

The command `viewport.capture` can switch the noise off for one picture with its :term[renderer]{id=renderer} switch `DitherOutput`, and the pair above was taken with it. In the first picture, the blue of the sky climbs from code 28 at the top to 57 at the ridge, in flat bands of 16 to 40 rows, the widest at the top. Each band is one code brighter than the one above it. One code of a dark blue is a small step, so look closely, or raise the screen's brightness.

This page is about the last step of the image: the one that turns the values the :term[renderer]{id=renderer} computed into the **codes** the target stores. The step has one job and three duties. It encodes :term[display-linear]{id=display-linear} light with the :term[sRGB]{id=srgb} curve, it rounds to the target's codes without bands, and it adds noise once only. It does not choose the picture's look: the exposure, the :term[tone curve]{id=tone-mapping-image} and the grade ([Grading](grading.md)) have finished before it starts. It does not blend edges either: the passes that do so are the subject of [Spatial anti-aliasing](spatial-aa.md), and this page shows only where they meet the encoding.

## The problem and how engines solve it

The tone mapping hands the last step display-linear values: numbers proportional to the light the screen will emit. A target does not store light in proportion. [Color](../basics/color.md) teaches the sRGB transfer function, which Strata writes in `Strata/shaders/Include/Common.slang` as the function below. It multiplies a dark value by 12.92 and bends a brighter one with a power of 1 / 2.4, so that codes at equal distances look like equal steps to an eye.

```slang src="Strata/shaders/Include/Common.slang#L26-L32"
float3 LinearToSRGB(float3 color)
{
	color = max(color, float3(0.0));
	float3 low = color * 12.92;
	float3 high = 1.055 * pow(color, float3(1.0 / 2.4)) - 0.055;
	return select((color <= float3(0.0031308)), low, high);
}
```

The function first clamps negative values to 0. Below 0.0031308 the curve is a straight line; above it, the power curve takes over. A C++ twin, `PostProcessMath::LinearToSRGB`, does the same arithmetic on the :term[central processing unit]{id=processor} (CPU), so that tests can compute what the :term[graphics processing unit]{id=gpu} (GPU) must show.

The curve helps the dark end, but 256 codes remain 256 codes. The next program takes the dark sky from the opening: the light rises from 0.002 to 0.004 of white across 1,920 columns. It rounds each column's encoded value to the nearest code and counts the columns per code.

```cpp sketch="image-encoding-bands.cpp"
// The 8-bit codes of a dark sky gradient: how many columns share each code, and the light each code means.
#include <cmath>
#include <cstdio>

float LinearToSRGB(float linear)
{
	return linear <= 0.0031308f ? linear * 12.92f : 1.055f * std::pow(linear, 1.0f / 2.4f) - 0.055f;
}

float SRGBToLinear(float encoded)
{
	return encoded <= 0.04045f ? encoded / 12.92f : std::pow((encoded + 0.055f) / 1.055f, 2.4f);
}

int main()
{
	constexpr int c_Width = 1920;
	int columns[256] = {};
	for (int x = 0; x < c_Width; x++)
	{
		// The light rises from 0.002 to 0.004 of white across the picture.
		const float linear = 0.002f + 0.002f * static_cast<float>(x) / static_cast<float>(c_Width - 1);
		const int code = static_cast<int>(std::lround(LinearToSRGB(linear) * 255.0f));
		columns[code]++;
	}
	for (int code = 0; code < 256; code++)
	{
		if (columns[code] > 0)
			std::printf("code %3d: %4d columns, light %.5f\n", code, columns[code], SRGBToLinear(static_cast<float>(code) / 255.0f));
	}
	return 0;
}
```

```text output-of="image-encoding-bands.cpp"
code   7:  266 columns, light 0.00212
code   8:  291 columns, light 0.00243
code   9:  291 columns, light 0.00273
code  10:  293 columns, light 0.00304
code  11:  308 columns, light 0.00335
code  12:  325 columns, light 0.00368
code  13:  146 columns, light 0.00402
```

1. **Line 7:** the encode is the engine's curve, the straight line below 0.0031308 and the power above it.
2. **Line 22:** the light rises in a straight line from 0.002 to 0.004 of white across the 1,920 columns.
3. **Line 23:** `lround` rounds the encoded value to the nearest of the 256 codes, which is all that an 8-bit target can store.
4. **Line 24:** a counter for each code collects the columns that share it.
5. **Line 29:** the decode shows the light that each code means, so the step between neighbors is visible in light.

The gradient spans only seven codes. Each code but the last holds 266 to 325 columns, so the eye sees seven flat bands with an edge between each pair. The step between neighbors is small in light, 0.0003 of white, but the eye compares neighbors at an edge and finds even that. A picture of a night sky, a fog bank or a dark wall lit by a lamp has long slow gradients, and they all show this.

Three families of answers exist. The first is more bits: store the values in 10 or 16 bits, so that the steps are four or more times smaller. Displays and common image files hold 8 bits per channel, so the last step cannot avoid the 8 bits, and the answer only moves the problem. The second hides the steps with noise, and the third avoids them by keeping every earlier stage at a high precision, which Strata does with its float targets. The page is about what remains: the last rounding to 8 bits.

A **dither** is a small planned noise added to a value before it is rounded to a code, so that the :term[rounding error]{id=rounding-error} becomes a fine grain in place of a band. [Signals](../basics/signals.md) shows the idea with a fixed table of thresholds, the ordered dither. Strata uses noise from a :term[hash]{id=hash} instead, and the design has three choices.

The first choice is the noise's shape. Add a random number from 0 to 1 before flooring a value, and the mean of the stored codes equals the value. A value of 26.3 becomes 27 in three pixels of ten and 26 in seven. That is **rectangular** noise, because its :term[probability density function]{id=probability-density} is flat: every amount from 0 to 1 is equally likely.

The flaw of rectangular noise is how much noise a pixel gets. A value at exactly 26.0 always stores 26, with no noise, while a value at 26.5 gets the most. So the grain's strength changes with the value, and a slow gradient shows the grain breathing as the value crosses codes. That effect is **noise modulation**: noise whose strength depends on the signal that it is added to.

For a value $f$ codes above a whole code, the rectangular dither stores the code above with chance $f$, so its noise power is $f (1 - f)$ codes squared. The table gives three cases by hand, beside the rounding error and the noise power of the sum of two noises that the next paragraph builds.

| Value in codes | Rounding: mean error | Rectangular: noise power | Sum of two: noise power |
| --- | --- | --- | --- |
| 26.0 | 0 | 0 | 1/4 |
| 26.3 | -0.3 | 0.21 | 1/4 |
| 26.5 | +0.5 | 1/4 | 1/4 |

A fix is a **triangular probability density function** (TPDF). **TPDF** noise is the sum of two independent rectangular noises, minus 1; it spans from -1 to 1 and is likelier near 0. Its mean is 0 and its variance is 1/6. With it the rounding error has the same power at every value, 1/4 of a code squared.

By hand: the stored code is $q$ and the value $v$, the error $q - v$ has a mean of 0 and the same variance for 26.0, 26.3 and 26.5. The toy version below measures this.

The second choice is whether the noise moves. Temporal noise changes every frame, so that the eye averages many frames and sees a clean gradient, but it needs a moving picture, and a screenshot of a still scene differs between runs. Static noise depends only on the pixel's position: a still picture is the same every frame, and a capture is the same every time. Strata chooses static noise. The grain below is the opposite, on purpose.

The last choice is where to put the extra bits. When a later pass has to read the picture, such as the pass that finds edges, the picture is first stored with more than 8 bits per channel. A **10-bit intermediate** is a target with 10 bits for each :term[color channel]{id=color-channel}, so 1,024 codes in place of 256, which holds an image between the tone mapping and a following pass. Strata names it `c_LDRFormat`, and its format is R10G10B10A2_UNORM, which packs three 10-bit channels and a 2-bit alpha into 32 bits.

## The map

Everything on this page happens on the GPU, in the last pass or passes of the frame. The CPU's part is small: it chooses the number of levels for the target and one frame number, and it writes both into a :term[constant buffer]{id=constant-buffer} on the :term[main thread]{id=main-thread}.

```mermaid caption="Which pass writes the display image. With no spatial anti-aliasing, or with temporal anti-aliasing, the tone mapping adds grain and dither. With fast approximate anti-aliasing or the morphological pass, the tone mapping writes the 10-bit image bare and the next pass adds both." alt="A tree. The post chain feeds the tone mapping. If no spatial anti-aliasing follows, the tone mapping adds grain and dither and writes the display image. If one follows, the tone mapping writes the 10-bit image without grain or dither, and the fast approximate or morphological pass reads it, blends, adds grain and dither and writes the display image."
flowchart TD
	Post["Post chain: exposure, bloom, flare"] --> Tone["Tone mapping: curve, grade, sRGB encode"]
	Tone -->|no spatial AA, or TAA| Direct["Grain, dither: display image"]
	Tone -->|FXAA or morphological AA| Ten["10-bit image, bare"]
	Ten --> AA["AA pass: blend, grain, dither: display image"]
```

Two passes of spatial anti-aliasing may follow the tone mapping: fast approximate anti-aliasing (FXAA) and a morphological pass. Temporal anti-aliasing (TAA) works earlier in the chain and needs no pass after the tone mapping.

Five files hold the pieces:

- `Strata/shaders/Include/Common.slang` has the sRGB curve.
- `Strata/shaders/Include/Dither.slang` has the hash and the dither, and `Strata/shaders/Include/Grain.slang` the grain.
- `Strata/src/Strata/Renderer/PostProcessMath.cpp` has the :term[CPU twins]{id=cpu-twin} of all three.
- `Strata/src/Strata/Renderer/SceneRendererPost.cpp` decides in `RenderPostDisplay` which pass does what.

Three :term[shaders]{id=shader} call the dither: `Strata/shaders/PostProcess/Tonemap.frag.slang`, `Strata/shaders/PostProcess/FXAA.frag.slang` and `Strata/shaders/PostProcess/MorphologicalBlend.frag.slang`.

## The contract

A caller of this step, and the author of a new post pass, can rely on these rules. Each has its reason.

- **The display image is encoded and dithered exactly once.** A second dither on top of the first would add noise power twice and show as grain; and a dither that is blended by a later pass is blurred. So only the last pass that writes the display image dithers.
- **The dither works on encoded values.** The codes the target stores are encoded, and the steps that the eye sees are encoded steps. A dither added in linear light would be far too strong in the shadows and too weak in the lights.
- **The dither is static.** It is a function of the pixel and a stream number, and it has no frame index. A still frame and a capture are the same every time, and nothing has to accumulate.
- **Black and white stay exact.** A pixel at 0 stores code 0 and a pixel at 1 stores the top code, whatever the noise, so black bars and pure white stay clean.
- **The mean stays.** Over many pixels, the stored codes average to the value that was asked for, so the dither does not brighten or darken the picture.
- **The grain comes right before the dither, in the same pass.** The grain belongs to the display image, and a blend after it would take the differences between neighbors for edges.
- **A level count of 0 means no dither.** The levels come from the target's format. A format that the code does not know keeps its own rounding.

The renderer's switch `DitherOutput` is a field of `SceneRendererSpecification`, true by default. It exists for the exact-pixel tests: `ExactSpecification` disables it, so that a test compares codes without noise. The editor's `viewport.capture` command can switch it for one picture, as one of its renderer switches, which is how the pair at the top of this page was taken.

Strata writes sRGB output only. `Strata/src/Platform/Vulkan/VulkanGraphicsDevice.cpp` picks a :term[back buffer]{id=back-buffer} from the formats that the surface offers in the sRGB non-linear :term[color space]{id=color-space}, and prefers `VK_FORMAT_B8G8R8A8_UNORM`, then `VK_FORMAT_R8G8B8A8_UNORM`. There is no :term[high dynamic range]{id=high-dynamic-range} output at the pin, so the codes end at 255 or 1023, and this page's rounding is the whole story of the last step. [Vulkan and NVRHI](../gpu/vulkan-nvrhi.md) teaches the swap chain.

## A toy version

The toy compares three ways to store one value in whole codes: plain rounding, a rectangular dither and a TPDF dither. For each of three values it stores the value in 200,000 pixels and measures the mean error and the noise power, which is the variance of the stored codes. Look at how the numbers change as the value moves from 26.0 to 26.5.

```cpp sketch="image-encoding-toy.cpp"
// Three ways to store a value in whole codes: rounding, a rectangular dither and a triangular dither.
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <initializer_list>

uint32_t MixBits(uint32_t x)
{
	x ^= x >> 16u;
	x *= 0x7FEB352Du;
	x ^= x >> 15u;
	x *= 0x846CA68Bu;
	x ^= x >> 16u;
	return x;
}

// A value in [0, 1) that depends only on the pixel and the stream: the same pixel always gets the same noise.
float PixelRandom(uint32_t pixel, uint32_t stream)
{
	return static_cast<float>(MixBits(pixel ^ MixBits(stream)) >> 8u) / 16777216.0f;
}

int main()
{
	constexpr uint32_t c_Pixels = 200000;
	for (const float value : { 26.0f, 26.3f, 26.5f })
	{
		double sums[3] = {};
		double squares[3] = {};
		for (uint32_t pixel = 0; pixel < c_Pixels; pixel++)
		{
			const float u0 = PixelRandom(pixel, 0);
			const float u1 = PixelRandom(pixel, 1);
			const float rounded = std::floor(value + 0.5f);
			const float rectangular = std::floor(value + u0);
			const float triangular = std::floor(value + (u0 + u1 - 1.0f) + 0.5f);
			const float stored[3] = { rounded, rectangular, triangular };
			for (int method = 0; method < 3; method++)
			{
				const double error = static_cast<double>(stored[method] - value);
				sums[method] += error;
				squares[method] += error * error;
			}
		}
		std::printf("value %.1f\n", static_cast<double>(value));
		const char* names[3] = { "round", "rectangular", "triangular" };
		for (int method = 0; method < 3; method++)
		{
			const double mean = sums[method] / c_Pixels;
			const double power = squares[method] / c_Pixels;
			std::printf("  %-11s mean error %+.3f, noise power %.3f\n", names[method], mean, power - mean * mean);
		}
	}
	return 0;
}
```

```text output-of="image-encoding-toy.cpp"
value 26.0
  round       mean error +0.000, noise power 0.000
  rectangular mean error +0.000, noise power 0.000
  triangular  mean error -0.001, noise power 0.251
value 26.3
  round       mean error -0.300, noise power 0.000
  rectangular mean error +0.000, noise power 0.210
  triangular  mean error -0.000, noise power 0.249
value 26.5
  round       mean error +0.500, noise power 0.000
  rectangular mean error -0.001, noise power 0.250
  triangular  mean error -0.001, noise power 0.250
```

1. **Line 18:** the noise is a hash of the pixel and a stream number, so a pixel always gets the same values.
2. **Line 25:** 200,000 pixels give each average enough samples to settle.
3. **Lines 34–36:** the three ways to store the value: rounding, a rectangular dither with one random number, and a TPDF dither with two.
4. **Line 42:** the squares collect the noise power.
5. **Line 51:** the noise power is the variance of the error: the mean of the squares minus the square of the mean.

Rounding has a mean error of 0 only when the value sits on a code; at 26.3 it is wrong by 0.3 in every pixel, and nothing breaks the band. The rectangular dither has a mean error near 0 at every value, but its noise power is 0 at 26.0, 0.210 at 26.3 and 0.250 at 26.5: the noise modulation, in numbers. The TPDF dither has the same power, about 0.25, at all three. The result is why the engine pays for the second random number.

The toy omits three things that the real code adds. It dithers one channel, and the engine does three, with independent streams. It has no exact black and white. And it never meets a target other than 8 bits.

## The real code

The real code follows the data. The pixel's hash comes first, then the dither, then the grain, then the choice of the levels and of the pass.

### The hash

The dither needs a random-looking number for each pixel, the same every time. `MixBits` is a 32-bit :term[integer]{id=integer} mixing function: it mixes the bits of a number so that a small change in the input changes about half of the output bits. `PixelRandom` hashes the pixel's two coordinates and a stream number, and keeps the top 24 bits as a fraction in [0, 1). Search for the nesting in the second function, which makes each stream independent.

```slang src="Strata/shaders/Include/Dither.slang#L10-L25"
uint MixBits(uint x)
{
	x ^= x >> 16u;
	x *= 0xA3B195E5u;
	x ^= x >> 15u;
	x *= 0x6C8E9CF7u;
	x ^= x >> 16u;
	return x;
}

// A uniform value in [0, 1) for a pixel and a stream (independent streams per use): the top 24 bits of the hash.
float PixelRandom(uint2 pixel, uint stream)
{
	uint bits = MixBits(pixel.x ^ MixBits(pixel.y ^ MixBits(stream)));
	return float(bits >> 8u) * (1.0 / 16777216.0);
}
```

1. **Line 12:** a right shift by 16 moves the top bits into the bottom ones, so that every input bit reaches the low bits.
2. **Line 13:** a multiplication by an odd constant spreads each bit upward through the word; the constants were chosen once and are fixed.
3. **Line 23:** the pixel's x is mixed with the hash of y, which is mixed with the hash of the stream, so two streams of one pixel have no pattern in common.
4. **Line 24:** only the top 24 bits are kept, because a float holds 24 bits of fraction exactly, and the division maps them to [0, 1).

### The dither

`DitherToCodes` takes an encoded color, the pixel and the number of levels. For a target of 255 levels, the result is a value of the form q / 255, with q a whole code. The function works channel by channel and uses streams 0 to 5, two for each channel, so the three channels do not share noise.

```slang src="Strata/shaders/Include/Dither.slang#L36-L51"
float3 DitherToCodes(float3 encoded, uint2 pixel, float levels)
{
	if (levels <= 0.0)
		return encoded;
	float3 result;
	for (int channel = 0; channel < 3; channel++)
	{
		float v = clamp(encoded[channel] * levels, 0.0, levels);
		v = v < c_DitherEndSnap ? 0.0 : (v > levels - c_DitherEndSnap ? levels : v);
		float u0 = PixelRandom(pixel, uint(2 * channel));
		float u1 = PixelRandom(pixel, uint(2 * channel + 1));
		float q = (v >= 0.5 && v <= levels - 0.5) ? floor(v + (u0 + u1 - 1.0) + 0.5) : floor(v + u0);
		result[channel] = q / levels;
	}
	return result;
}
```

1. **Line 38:** zero levels mean no :term[quantization]{id=quantization} at all, and the color passes unchanged.
2. **Line 43:** the value moves into codes: with 255 levels, 0.1 becomes 25.5.
3. **Line 44:** a value within 1/256 of a code of black or white is snapped to it, because the encode of 1.0 may end a few units in the last place below 1.
4. **Line 47:** in the middle, the TPDF noise `u0 + u1 - 1.0` is added before the rounding; within half a code of the ends, only the rectangular `floor(v + u0)` is used.
5. **Line 48:** q is divided by the levels, and a unit-normalized target stores q again.

Take the value 26.3 in codes. A pixel with `u0` 0.8 and `u1` 0.5 has noise 0.3, so q is floor(26.3 + 0.3 + 0.5), which is 27. A pixel with `u0` 0.1 and `u1` 0.2 has noise -0.7, and q is floor(26.3 - 0.7 + 0.5), which is 26. Over many pixels the 27s and 26s average to 26.3, as the toy showed.

The ends need a different rule, and the reason is the mean. Near code 0, a value of 0.3 plus a noise of -0.8 would want a code of -1, which does not exist; clamping it to 0 would make the mean too high. So within half a code of an end, the shader uses the rectangular noise, whose result cannot leave the range. Its mean is still right, and the noise power is smaller there, which is invisible. At exactly black or white, the snap makes the result exact.

### The grain

**Film grain** is a noise that changes every frame, is strongest in the mid-tones and has a bell-shaped spread, so that a picture looks like a photograph on film. It is a choice of look, off by default (`FilmGrain` 0 in `PostProcessComponent`), and players can disable it through the quality row `FilmGrain`.

```slang src="Strata/shaders/Include/Grain.slang#L17-L25"
float3 AddFilmGrain(float3 encoded, uint2 pixel, float strength, uint frame)
{
	if (!(strength > 0.0))
		return encoded;
	uint salt = 8u + 4u * frame;
	float noise = (PixelRandom(pixel, salt) + PixelRandom(pixel, salt + 1u) + PixelRandom(pixel, salt + 2u) + PixelRandom(pixel, salt + 3u) - 2.0) * 1.7320508;
	float encodedLuminance = clamp(dot(encoded, float3(0.2126, 0.7152, 0.0722)), 0.0, 1.0);
	return clamp(encoded + strength * c_FilmGrainAmplitude * sqrt(4.0 * encodedLuminance * (1.0 - encodedLuminance)) * noise, 0.0, 1.0);
}
```

1. **Line 19:** a strength of 0 returns the color unchanged, and the test is written so that a not-a-number value also does.
2. **Line 21:** the stream starts at 8, past the dither's six, and moves by four for each frame, so every frame has new noise.
3. **Line 22:** the sum of four uniform numbers minus 2 has a variance of 1/3, and the factor 1.7320508 (the square root of 3) brings it to 1: a bell-shaped noise of unit spread.
4. **Line 23:** the encoded :term[luminance]{id=luminance} is the weighted sum of red, green and blue with the usual weights.
5. **Line 24:** the weight is the square root of 4 Y (1 - Y): 1 at a luminance of 0.5, 0.6 at 0.1 and 0 at black and white. The same noise goes to all three channels.

The amplitude, `c_FilmGrainAmplitude`, is 0.04 of the encoded range at a `FilmGrain` of 1, which is 0.04 times 255, about 10 codes of spread in the mid-tones. A look of 0.3 gives about 3 codes. Because the noise has a mean of 0 before the clamp, the grain adds texture without moving the picture's brightness. A test checks it: on a mid-gray wall, the mean change of the pixels stays within 0.1 code.

::compare{id=grain-sweep}

The sequence of a frame sets the seed. Unless the caller sets `GrainSeed` in the render options, the renderer uses its frame count, so every frame has new grain. Captures and thumbnails set the seed to 0, so that a picture taken again is the same, and a still stays :term[deterministic]{id=determinism}.

### The levels

The step works for any target for which the code knows how many codes a channel has. `GetDitherLevels` maps the format of the output to a level count: 255 for the 8-bit unsigned :term[normalized]{id=normalization} (:term[UNORM]{id=unorm}) formats and 1023 for the 10-bit one. Every other format, for example the 16-bit ones, gets 0, and its own rounding stays.

```cpp src="Strata/src/Strata/Renderer/SceneRendererPost.cpp#L60-L75"
float GetDitherLevels(nvrhi::Format format)
{
	switch (format)
	{
		case nvrhi::Format::R8_UNORM:
		case nvrhi::Format::RG8_UNORM:
		case nvrhi::Format::RGBA8_UNORM:
		case nvrhi::Format::BGRA8_UNORM:
		case nvrhi::Format::BGRX8_UNORM:
			return 255.0f;
		case nvrhi::Format::R10G10B10A2_UNORM:
			return 1023.0f;
		default:
			return 0.0f;
	}
}
```

1. **Lines 64–69:** the one-, two- and four-channel 8-bit formats, and the one without alpha, all have 256 codes.
2. **Lines 70–71:** the 10-bit packed format has 1,024 codes.
3. **Lines 72–73:** any other format returns 0, so the shader skips the dither.

### Which pass is last

`RenderPostDisplay` writes the tone mapping's constants and then chooses the passes. The thing to find in the next quote is the order of three decisions: whether spatial anti-aliasing runs, where the tone mapping writes, and who gets the levels and the grain.

```cpp src="Strata/src/Strata/Renderer/SceneRendererPost.cpp#L1278-L1294"
const bool antiAliased = postProcess.AntiAliasing && !resolved;
const bool morphologicalWanted = antiAliased && postProcess.AntiAliasingMethod == AntiAliasingMode::Morphological;
const bool morphological = morphologicalWanted && EnsureMorphologicalResources(commandList);
if (morphologicalWanted && !morphological)
	degraded = true; // Drawn with FXAA; EnsureMorphologicalResources reported why
const bool fxaa = antiAliased && !morphological;
nvrhi::IFramebuffer* tonemapTarget = fxaa || morphological ? m_LDRFramebuffer.Get() : output;
// The last pass that writes the display image dithers it, once: FXAA's or the morphological blend when one follows (the
// tone mapping's 10-bit image stays undithered), else the tone mapping.
const float outputLevels = m_Specification.DitherOutput ? GetDitherLevels(output->getFramebufferInfo().colorFormats[0]) : 0.0f;
tonemap.DitherLevels = fxaa || morphological ? 0.0f : outputLevels;
// The grain too goes into the display image last (before the dither): in the tone mapping's 10-bit image, FXAA and the
// morphological edges would take its differences between neighbors for edges and blend it away.
const float grain = tonemap.FilmGrain;
if (fxaa || morphological)
	tonemap.FilmGrain = 0.0f;
m_Stats.Dithered = outputLevels > 0.0f;
```

1. **Line 1278:** spatial anti-aliasing runs only when the image was not resolved by temporal anti-aliasing, which has already blended the picture over time.
2. **Lines 1280–1283:** when the morphological pass is wanted but its resources cannot be made, the frame falls back to FXAA and reports the loss.
3. **Line 1284:** with a following pass, the tone mapping writes the 10-bit intermediate and not the display image.
4. **Line 1287:** the levels come from the output's format, and are 0 when `DitherOutput` is off.
5. **Lines 1288–1293:** the tone mapping gets the levels and the grain only when no pass follows; otherwise both go to the pass that does follow.

Here is the trace for four settings. With anti-aliasing off, or with temporal anti-aliasing, `fxaa` and `morphological` are false, so the tone mapping dithers and adds the grain, and its target is the output. With FXAA, the tone mapping writes the 10-bit image with `DitherLevels` 0 and a grain of 0, and the FXAA shader calls `AddFilmGrain`, then `DitherToCodes`, on the blended color. With the morphological pass, the edges and weights passes run first, and the blend does the same. The 10-bit step is a quarter of an 8-bit one, so storing the bare image there loses less than the final dither adds.

This rule is also why FXAA and the grain agree: a test, `Film grain is as strong under FXAA and the morphological anti-aliasing as without anti-aliasing`, measures the spread with each method and finds it within 3 % of the spread without anti-aliasing. [Spatial anti-aliasing](spatial-aa.md) teaches the two passes.

:::example[One frame, three pixels]
A frame has FXAA on and `FilmGrain` 0.3 on an 8-bit output. A pixel in a dark corner has an encoded luminance of 0.02 after the blend. The weight is the square root of 4 × 0.02 × 0.98, which is 0.28, so the grain's spread there is 0.3 × 0.04 × 0.28 × 255, about 0.86 codes. A pixel at 0.5 has a weight of 1 and a spread of 3.06 codes. A pixel of pure black has a weight of 0, and its snap in the dither gives code 0 exactly.

Each of the three pixels is then dithered with its own pair of numbers from `PixelRandom`, so even two neighbors with the same value store different codes. The tone mapping had written all three into the 10-bit image bare, and the FXAA pass added both. Had the tone mapping added the grain, the pass would have read the differences between neighbor pixels as edges and blended them down, and `FilmGrain` 0.3 would show weaker under FXAA than with no anti-aliasing.
:::

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Plain rounding, no dither | Simple renderers and tests | No noise and the cheapest last pass | Bands in every dark gradient |
| Rectangular noise | Many simple shaders | One random number a channel instead of two | Noise that swells and fades with the value |
| Ordered dither (a Bayer table) | Older games and printers | No hash, a regular pattern that is cheap to read | A visible grid in smooth areas |
| Temporal noise (a new pattern each frame) | Engines that average frames | Fewer visible patterns when the picture moves | Different stills on every run, and noise a temporal pass could blur |
| Error carrying: each pixel passes its rounding error to its neighbors | Tools that reduce the colors of an image | The best use of each code | A pass that visits pixels in order, which a GPU cannot do in parallel |
| A high dynamic range display output | Engines with high dynamic range displays | More codes and brighter lights | A second output path, which Strata lacks at the pin |

Sources for the claims about other programs are listed in Further reading.

## How it is tested

The CPU twin lives in the suite `Renderer.PostProcessMath`, which runs without a GPU. `The dither noise is triangular and uncorrelated` measures the noise's :term[histogram]{id=histogram} against the triangle and checks that the channels, and neighbors, have a correlation below 0.03. `Dithering keeps black, white and the mean` checks that black and white stay exact for 255 and 1023 levels and that levels of 0 change nothing. It also checks that the mean of the stored codes equals the value, within 0.01, at several fractions.

The suite `GPU.SceneRenderer.Camera` checks the whole step on a real device. `Dithering keeps a gradient's mean and breaks up its bands` renders a ramp that spans about four codes, and cuts it in bands of 32 columns. With the dither, no band's mean is wrong by more than 0.1 code; without, the error is above 0.2, because rounding steps the bands.

`DitherOutput false quantizes without noise` renders flat fields with anti-aliasing off, FXAA and TAA. It checks that a field has one code with the switch off and at least two with it on, and that black and white are exact either way. `The dither on the GPU is its CPU twin` compares the GPU's codes with `PostProcessMath::DitherToCodes`. `GPU.SceneRenderer.GrainAndAberration` has the grain cases.

Run the CPU cases with `build/windows/bin/Debug/StrataTests.exe --test-case="Dithering keeps black, white and the mean"`, and the GPU ones with `build/windows/bin/Debug/StrataTests.exe --test-suite=GPU.SceneRenderer.Camera`. They need a Vulkan device; CTest runs all GPU suites together as `StrataTests.GPU`. [Test kinds](../engineering/test-kinds.md) explains the exact-pixel tests, and [Your first change](../core/first-change.md) shows how to build and run one case.

## Changing it safely

The extension points are few. A new target format with its own levels is one more case of `GetDitherLevels`. A new pass that writes the display image takes over the duties of the last pass. It gets the levels and the grain from `RenderPostDisplay`, the tone mapping gets 0 for both, and the new shader calls `AddFilmGrain` and then `DitherToCodes`. A new noise takes streams that neither the dither (0 to 5) nor the grain (8 and up) uses.

The rules that apply, with their reasons:

- Change the shader and its CPU twin together, and keep both in the same integer arithmetic, since a test requires them to store the same code in all but one pixel of 1,000.
- Keep the dither static. A frame index in it would make captures differ and force the tests to accept noise.
- Never dither in a pass that another pass reads; the 10-bit image stays bare, so that the blend does not average the noise away.
- A change to the hash or to its constants changes every capture. The statistics in `Renderer.PostProcessMath` must still pass, and the look-dev pictures are taken again.

Before a commit, run `Renderer.PostProcessMath`, `GPU.SceneRenderer.Camera` and `GPU.SceneRenderer.GrainAndAberration`.

## Summary

- The last step encodes display-linear light with the sRGB curve and rounds to the target's codes; 256 codes leave a dark gradient in flat bands of 266 to 325 columns in the example.
- A rectangular dither keeps the mean but its noise power is f (1 - f) for a fraction f, so it swells and fades; a TPDF dither has the power 1/4 at every value.
- Strata's dither is TPDF, static and a hash of the pixel, exact at black and white; the levels come from the target's format.
- The dither and the grain go once, into the last pass that writes the display image: the tone mapping, or the FXAA or morphological pass, which read a bare 10-bit image.
- The tests compare the shader with its CPU twin, check the mean and the bands, and check that the switch turns the noise off.

## Check yourself

1. A value of 40.5 codes is stored by a rectangular dither and by a TPDF dither. Which statement is right? (a) Both have the same noise power, 1/4 (b) The rectangular has power 1/4 and the TPDF 1/6 (c) The rectangular has power 0 (d) Neither keeps the mean

   :::answer{tests="dither-math"}
   (a). At a fraction of 0.5 the rectangular noise power is 0.5 × 0.5 = 1/4, and the TPDF noise is 1/4 at every value. (b) mixes up the TPDF noise's own variance, 1/6, with the error's power. (c) holds at an exact code only. (d) is wrong: both keep the mean.
   :::

2. Why does Strata not add the film grain in the tone mapping when FXAA follows?

   :::answer{tests="last-pass"}
   FXAA searches for edges where neighbors differ. The grain makes neighbors differ, so FXAA would read it as edges and blend it away, and a given strength would show softer under FXAA than with no anti-aliasing.
   :::

3. The dither is hashed from the pixel and a stream, with no frame number. A game shows a still scene. What does the player see, and what would a frame number change?

   :::answer{tests="codes"}
   The dither pattern is the same every frame, so the picture is still. With a frame number the pattern would change each frame and a still scene would shimmer. The grain does use a frame number, on purpose, because film grain moves.
   :::

4. A frame has TAA on. Which shader dithers?

   :::answer{tests="trace-pass"}
   The tone mapping shader. TAA resolves the image before it, so `antiAliased` is false, no spatial pass follows, and the tone mapping writes the output with the levels and the grain.
   :::

5. A rectangular dither replaces the TPDF dither. Which check of `Dithering keeps a gradient's mean and breaks up its bands` could change, and why?

   :::answer{tests="run-tests"}
   The mean stays, so the band checks of that GPU case would still pass. The case that fails is `The dither noise is triangular and uncorrelated` in `Renderer.PostProcessMath`: it compares the histogram of `PostProcessMath::TriangularNoise` in steps of 0.1 with the triangle, and a flat histogram misses it by more than 0.03.
   :::

## Exercises

1. **Basic.** A gradient has the encoded value 100.5 codes in one pixel. By hand, give the stored code with plain rounding, and the two stored codes the engine's dither can give with noise -0.4 and 0.4.

   :::answer[Worked solution]{tests="dither-math"}
   Rounding gives floor(100.5 + 0.5) = 101. With noise -0.4 the code is floor(100.5 - 0.4 + 0.5), which is floor(100.6) = 100. With noise 0.4 it is floor(101.4) = 101. Half of the pixels store 100 and half 101 on average, so the mean is 100.5.
   :::

2. **Medium.** Predict, then run: for the dark gradient of this page, which band error do you expect with and without the dither, in blocks of 32 columns? Then run the case `Dithering keeps a gradient's mean and breaks up its bands` of `GPU.SceneRenderer.Camera`, and say which check a rectangular dither would fail.

   :::answer[Worked solution]{tests="run-tests"}
   Without the dither each band's mean is the rounded code, which can be off by up to half a code, so expect a large error. With the TPDF dither the mean of 512 pixels has a spread of about 0.5 / 22, so about 0.02 to 0.06. The sketch below measures it. In the engine's cases the checks are `error < 0.1f` with the dither and `error > 0.2f` without. A rectangular dither keeps the mean, so it passes those, but the case `The dither noise is triangular and uncorrelated` in `Renderer.PostProcessMath` compares the noise's histogram with the triangle within 0.03 and fails.

   ```cpp sketch="image-encoding-ramp.cpp"
   // The largest error of a band's mean code in a dark gradient, when the gradient is rounded and when it is dithered.
   #include <algorithm>
   #include <cmath>
   #include <cstdint>
   #include <cstdio>

   uint32_t MixBits(uint32_t x)
   {
   	x ^= x >> 16u;
   	x *= 0x7FEB352Du;
   	x ^= x >> 15u;
   	x *= 0x846CA68Bu;
   	x ^= x >> 16u;
   	return x;
   }

   float PixelRandom(uint32_t pixel, uint32_t stream)
   {
   	return static_cast<float>(MixBits(pixel ^ MixBits(stream)) >> 8u) / 16777216.0f;
   }

   float LinearToSRGB(float linear)
   {
   	return linear <= 0.0031308f ? linear * 12.92f : 1.055f * std::pow(linear, 1.0f / 2.4f) - 0.055f;
   }

   int main()
   {
   	constexpr uint32_t c_Width = 1920;
   	constexpr uint32_t c_Rows = 16;
   	constexpr uint32_t c_Block = 32;
   	double largestRounded = 0.0;
   	double largestDithered = 0.0;
   	for (uint32_t start = 0; start < c_Width; start += c_Block)
   	{
   		double exactSum = 0.0;
   		double roundedSum = 0.0;
   		double ditheredSum = 0.0;
   		for (uint32_t y = 0; y < c_Rows; y++)
   		{
   			for (uint32_t x = start; x < start + c_Block; x++)
   			{
   				const float linear = 0.002f + 0.002f * static_cast<float>(x) / static_cast<float>(c_Width - 1);
   				const float value = LinearToSRGB(linear) * 255.0f;
   				const uint32_t pixel = y * c_Width + x;
   				const float noise = PixelRandom(pixel, 0) + PixelRandom(pixel, 1) - 1.0f;
   				exactSum += static_cast<double>(value);
   				roundedSum += static_cast<double>(std::floor(value + 0.5f));
   				ditheredSum += static_cast<double>(std::floor(value + noise + 0.5f));
   			}
   		}
   		const double count = static_cast<double>(c_Rows * c_Block);
   		largestRounded = std::max(largestRounded, std::abs(roundedSum - exactSum) / count);
   		largestDithered = std::max(largestDithered, std::abs(ditheredSum - exactSum) / count);
   	}
   	std::printf("largest band error in codes: rounded %.3f, dithered %.3f\n", largestRounded, largestDithered);
   	return 0;
   }
   ```

   ```text output-of="image-encoding-ramp.cpp"
   largest band error in codes: rounded 0.422, dithered 0.062
   ```

   1. **Line 31:** each band is 32 columns wide, as in the engine's test, and the sketch uses 16 rows of it.
   2. **Line 45:** the pixel number mixes the row and the column, so the rows get different noise.
   3. **Line 46:** the TPDF noise is the two random numbers minus 1.
   4. **Line 53:** the error of a band is the distance of its mean from the exact mean; the sketch keeps the largest.
   :::

3. **Hard.** Trace it yourself: for anti-aliasing off, FXAA, the morphological pass and TAA, find the one pass that dithers, and say what `RenderPostDisplay` passes as `DitherLevels` to each pass.

   :::answer[Worked solution]{tests="trace-pass"}
   Search for `DitherToCodes` in `Strata/shaders`: it is called in `Strata/shaders/PostProcess/Tonemap.frag.slang`, `Strata/shaders/PostProcess/FXAA.frag.slang` and, through `AddFilmGrain` followed by the dither, in `Strata/shaders/PostProcess/MorphologicalBlend.frag.slang`. In `RenderPostDisplay` in `Strata/src/Strata/Renderer/SceneRendererPost.cpp`, `tonemap.DitherLevels` is 0 when `fxaa` or `morphological` is true, and `outputLevels` otherwise. The FXAA and the morphological parameters get `outputLevels`. So: off and TAA dither in the tone mapping; FXAA in the FXAA pass; the morphological setting in the blend pass.
   :::

## Where it lives in Strata

- Shaders: `Strata/shaders/Include/Common.slang` (the sRGB curve), `Strata/shaders/Include/Dither.slang`, `Strata/shaders/Include/Grain.slang`, and the three passes in `Strata/shaders/PostProcess/`.
- CPU: `Strata/src/Strata/Renderer/PostProcessMath.cpp` (the twins), `Strata/src/Strata/Renderer/SceneRendererPost.cpp` (`RenderPostDisplay`, `GetDitherLevels`), `Strata/src/Strata/Renderer/SceneRenderer.h` (`DitherOutput`, `GrainSeed`, `c_LDRFormat`).
- Tests: `Renderer.PostProcessMath`, `GPU.SceneRenderer.Camera`, `GPU.SceneRenderer.GrainAndAberration`.
- Settings: `FilmGrain` of `PostProcessComponent` and the quality row `FilmGrain`.

## Further reading

- Gjøl and Svendsen, "The Rendering of INSIDE" (GDC 2016): a game that dithers its final image with TPDF noise (intermediate).
- Wannamaker, Lipshitz, Vanderkooy and Wright, "A theory of nonsubtractive dither" (IEEE Transactions on Signal Processing, 2000): why the TPDF noise makes the error power constant (advanced).
