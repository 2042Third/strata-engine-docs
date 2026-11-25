---
id: image/tone-mapping
title: "Tone mapping and the Filmic curve"
description: "How the display pass turns exposed light into display values: the tone curves engines use, Strata's six operators and the Filmic curve it fitted."
kind: internals
size: L
tracks: [E]
needs: [image/exposure]
time: 85
learn:
  - id: choose-curve
    text: choose a tone curve for a scene and defend the choice by what it does to middle gray, to highlights and to hue
  - id: compute-filmic
    text: compute the display value of a gray under the Filmic curve and under the simplest curve from its stops above middle gray
  - id: trace-operator
    text: trace the tone curve setting from the component to the shader's switch
  - id: change-filmic
    text: change the Filmic curve's look or its fit without breaking its targets
  - id: pass-order
    text: explain why contrast comes before the curve, saturation after it, and where the pass clamps its input
since: 0.3.0
status: final
---

After exposure, the :term[renderer]{id=renderer} holds light that runs from nearly 0 to values far above 1, and a display accepts only values from 0 to 1. The **display pass** reads that light, applies a **tone curve** that maps every exposed value into that range, and writes display values. It keeps the mid-tones where an eye expects them and rolls the highlights off toward white. It does not choose the exposure (that is the job of [Camera exposure](../image/exposure.md)), and it leaves the bloom, the grading, the :term[sRGB encoding]{id=srgb-encoding} and the grain to the pages that follow.

::figure{id=tone-curves}

The picture above is the idea of the whole page. The horizontal axis counts stops from :term[middle gray]{id=middle-gray}, so every step to the right doubles the light. The vertical axis is the display value. The curve bends flat at both ends: a **toe** in the shadows, a steep, nearly straight part in the middle and a shoulder in the highlights. Film behaves this way, and the rest of this page is about copying that bend with arithmetic.

## The problem and how engines solve it

Suppose a scene shows a white wall in the shade, a lit wall and a lamp. After exposure they hold 0.18, 0.72 and 24. A display cannot show 24, so the simplest answer clamps every value at 1. The shade and the lit wall stay correct, but the lamp becomes a flat white disk, the same as a wall twice as bright.

Clamping also changes color: a saturated orange light of (4, 1, 0.25) clamps to (1, 1, 0.25), a lemon yellow. The clamp throws away both brightness and hue, and Strata offers it as the operator `None`.

A :term[tone curve]{id=tone-mapping-image} (an operator, in Strata's code) fixes the first loss. It is a function that takes any exposed value and returns a value below 1, rising more slowly the brighter the input. The oldest is the `Reinhard` curve, $y = x / (1 + x)$. Take the three walls: 0.18 becomes 0.1525, 0.72 becomes 0.4186 and 24 becomes 0.96. Nothing clips, and the lamp is still the brightest thing.

The cost is that the whole picture turns flat. Middle gray falls from 0.18 to 0.1525, and the curve's steepness there is only $1 / (1 + x) = 0.85$, measured in stops of output per stop of input. A steepness below 1 means the mid-tones lose contrast, which is why a `Reinhard` image looks gray and washed out.

Each later operator starts from the flaw of the one before.

- A curve from the game industry (the first entry of Further reading) adds a toe and a shoulder as separate parts, so the mid-tones get a steeper section that an artist can tune. Its flaw is that it still works on each channel alone, so it skews hue.
- `ACES` is the film industry's Academy Color Encoding System (ACES), a full pipeline. A published fit of its rendering and display steps (a fraction of two small formulas, and two matrices) is cheap enough for a :term[shader]{id=shader}. The result is high in contrast, but it darkens middle gray (below, a gray of 0.18 shows as 0.1056), and it turns bright saturated colors toward other hues.
- `AgX` squeezes the colors toward gray with a matrix, applies the per-channel curve, and gives the saturation back after it. Bright colors fade to white instead of changing hue. The cost is a flat, low-saturation look that a grade then has to repair.
- `KhronosNeutral` does almost nothing below a peak of 0.76, so a material's :term[base color]{id=albedo} stays correct. Above it, the operator compresses the peak and fades the color toward white. It suits product pictures, and it has no contrast of its own.
- The curve of a racing game (the last entry of Further reading) joins a toe, a straight section and a shoulder, with exact control over where each starts. Strata's Filmic curve shares that idea, with the parts written in stops.

Behind the history stands one question about color. A curve may act on each of the three channels (red, green, blue) alone, or on the :term[luminance]{id=luminance} of the pixel and then scale the three channels together. Both have a cost, and the next two sections measure them.

### Per-channel curves skew hue

A per-channel curve is the film's way: each layer of a film responds with its own S-shape. Take the lantern color (4, 1, 0.25) again and apply `Reinhard` to each channel. The result is (0.8, 0.5, 0.2). Before, red was four times green and sixteen times blue. After, red is only 1.6 times green and four times blue.

A simple hue angle (the angle on the color wheel, red at 0 and yellow at 60 degrees) moves from 12 degrees to 30 degrees: the red lantern turned orange. The bigger channel is compressed more than the others, so the colors drift toward the middle of the wheel and toward white. That drift is **hue skew**: the shift of a color's hue by the tone curve, so that a saturated light does not keep the color that the scene gave it.

Hue skew is not always a defect. Film does it, and the drift toward white is what makes an very bright flame look hot. A game that wants a red light to stay red, or a sky to stay blue, does not want it.

A curve on luminance avoids the skew. The engine computes the pixel's luminance, maps it through the curve, and multiplies all three channels by the same factor, so the ratio between the channels does not change.

The lantern's luminance is $0.2126 \times 4 + 0.7152 \times 1 + 0.0722 \times 0.25 = 1.58$. `Reinhard` maps that to 0.61, so the factor is 0.387 and the color becomes (1.55, 0.39, 0.10). The red channel is above 1: the color left the display's :term[gamut]{id=gamut}, and clipping it brings the skew back. A luminance curve also cannot take a saturated light to white, so a blue lamp of any brightness stays blue.

::figure{id=hue-skew}

### Gamut compression: inset and outset

The third approach keeps the per-channel curve but changes what it receives. A matrix first mixes a little of each channel into its neighbors, so a saturated color moves inward toward gray. This is the **inset**, a matrix that draws the gamut in.

The per-channel curve then acts on colors whose channels are closer together, so it skews them less and takes bright ones to white. A second matrix, the outset, is roughly the inverse of the first and returns the saturation that the inset took away. `AgX` does this, and so does Strata's Filmic curve.

How much does a curve change a hue? Engines measure it in a space where angles follow what an eye sees. Strata's fit uses **ICtCp**, a :term[color space]{id=color-space} built for :term[high dynamic range]{id=high-dynamic-range} (HDR) video, which separates an intensity channel from two :term[color channels]{id=color-channel} so that equal distances look nearly equal. The distance in the color plane gives how vivid a color is, and its angle gives its hue.

## Strata's six operators

The component `PostProcessComponent` holds one `Tonemapper` of the enum `TonemapOperator`. Strata keeps the five classic operators, `None`, `Reinhard`, `ACES`, `AgX` and `KhronosNeutral`, and adds `Filmic`, its own curve, as the default for new components. A scene saved before 0.7.0 keeps the `ACES` curve that was then the default, because files store the curve.

How does a curve change a picture? Below is the same frame with the same exposure under two of them. At the same exposure ACES makes the dusk light on the wall darker and a little redder, because it puts middle gray lower.

::compare{id=lanterns}

The numbers that matter first are middle gray's. Exposure aims a gray of 0.18 at the middle of the range, so a good curve returns about 0.18 for it. The table lists each curve's result (computed by the program in the toy section below, from the shader's formulas) and the :term[sRGB]{id=srgb} code a display receives.

| Curve | Display value of 0.18 | sRGB code |
| --- | --- | --- |
| None | 0.1800 | 118 |
| `Reinhard` | 0.1525 | 109 |
| ACES | 0.1056 | 91 |
| ACES with 0.8 stops more exposure | 0.2250 | 130 |
| `AgX` | 0.2145 | 128 |
| **Khronos Neutral** | 0.1400 | 105 |
| Filmic | 0.1800 | 118 |

The `ACES` curve is the dark one: a scene lit to look normal under Filmic is about three quarters of a stop short under it (0.1056 against 0.18). So the component's tooltip suggests adding about 0.8 stops of exposure. Changing the curve without changing the exposure is a common error.

## The display pass: the map

The display pass is one fragment shader, `Strata/shaders/PostProcess/Tonemap.frag.slang`, which runs once per frame for every pixel of the image that reaches the display. Everything the frame does after the lit scene and the post chain's other passes meets here, in a fixed order. The order is the page's map, and each stage sits where its domain needs it: a stage in the wrong domain gives wrong colors.

```mermaid caption="Inside the display pass. The exposed scene-linear light flows through the lens and grading stages, the curve makes display-linear values, and only the last stages work on encoded codes." alt="A row of boxes. Chromatic aberration, exposing, sharpening, bloom, flare, vignette, white balance and grading, and contrast sit in the scene-linear group. The curve and saturation sit in the display-linear group. Encoding, the color lookup, grain and dither sit in the encoded group."
flowchart LR
  subgraph L["Scene-linear, exposed"]
    A["chromatic aberration"] --> B["ExposeSceneColor"] --> C["TAA sharpening"] --> D["bloom"] --> E["lens flare"] --> F["vignette"] --> G["white balance and grading"] --> H["contrast"]
  end
  subgraph D["Display-linear, 0 to 1"]
    I["the curve"] --> J["saturation"]
  end
  subgraph E2["Encoded"]
    K["sRGB encoding"] --> M["color lookup"] --> N["grain"] --> O["dither"]
  end
  H --> I
  J --> K
```

Read the diagram from left to right. In the first group the values still mean light: twice the number is twice the light, and nothing is capped at 1. In the second the curve has made values that a display can show, still proportional to light. In the third the sRGB transfer function (from [Color](../basics/color.md)) has spaced the values the way the display expects, and the last stages work on those codes.

The stages in the first group are exactly the ones that need light units. Chromatic aberration reads red a little farther from the center and blue a little nearer, and `ExposeSceneColor` multiplies by the exposure. The sharpening that the temporal anti-aliasing (TAA) pass asks for, the bloom, the lens flare and the vignette are all additions or multiplications of light.

White balance and grading change the color before the curve, as a camera does. Later pages teach each: [Grading](../image/grading.md), [Lens effects](../image/lens-effects.md), [TAA](../image/taa.md) and [Encoding](../image/encoding.md). This page takes the stages that decide the look of the curve: the clamp, contrast, the curve and saturation.

### Why the order holds

The order has three consequences that are common mistakes elsewhere.

- The curve runs on light, never on encoded values. An sRGB code is already a bent version of light, so a curve applied to it bends twice, and the mid-tones go wrong.
- Saturation runs after the curve. Saturation scales the distance of a color from its own luminance. Before the curve, its effect would depend on the exposure, and the curve would then compress the boosted channels unequally.
- Contrast runs before the curve, in log space (the space of stops, from [Numbers](../basics/numbers.md)), because it must tilt the picture around middle gray and let the curve see the tilted values.

## The contract

The display pass reads its parameters from `TonemapConstants`, a :term[struct]{id=struct} in `Strata/src/Strata/Renderer/PostProcessData.h` that the :term[central processing unit]{id=processor} (CPU) fills every frame in `RenderPostDisplay`. The parameters grew past the 128 :term[bytes]{id=byte} of push constants that :term[NVRHI]{id=nvrhi} allows (see [Binding](../gpu/binding.md)). So Strata keeps them in a volatile constant buffer: a small buffer that the CPU rewrites each frame, with one version for every frame :term[in flight]{id=in-flight} ([Resources and lifetimes](../gpu/resources-lifetimes.md)). Its size is 176 bytes.

```cpp src="Strata/src/Strata/Renderer/PostProcessData.h#L19-L28"
struct TonemapConstants
{
	float BloomIntensity;       // 0: fraction of the light scattered into the glow; 0 = off
	float BloomScale;           //    normalizes the sum of the bloom levels
	float Saturation;
	float Contrast;             //    around middle gray; 1 = unchanged
	int32_t Operator;           // 16: TonemapOperator
	uint32_t BloomAdditive;     //     1: the bloom holds only light above a threshold and is added instead of mixed
	float InversePreExposure;   //     1 / the pre-exposure the scene color carries (FrameConstants::TemporalParams.y)
	float Sharpening;           //     of the displayed image, on frames the TAA resolved; 0 = off
```

1. **Line 25:** the operator's number sits at byte offset 16, the start of the second four-float block, and the shader reads it as an :term[integer]{id=integer}.
2. **Lines 21-24:** the first four fields, which fill exactly one block of 16 bytes (the saturation and contrast among them).

The struct follows the :term[std140]{id=std140} layout rules, so the shader's declaration and this struct must agree byte for byte. A `static_assert` fixes the total size at 176 and checks the offset of several fields, such as `ColorRows` at 64 and `LensFlare` at 160. The contract has four rules.

- A field is added only at the end, and only in whole blocks of four floats, so every older offset stays where it was. The `static_assert` lines are the proof, and they are updated in the same change as the shader's declaration.
- The operators' numbers are part of what files and scripts rely on. A scene file stores `Tonemapper` as a number, and a script reads and writes that number, so a value never changes, and a new curve is appended after `Filmic`.
- The Filmic constants are generated. The matrices, `c_FilmicContrast` and the toe's width come from `Tools/FitFilmic.py` into two committed files, and nobody edits them by hand.
- The buffer needs no reservation of its own. Each frame that tone-maps has written `FrameConstants` first, so the :term[frames in flight]{id=frames-in-flight} leave room for its versions.

:::caution
The comment above `TonemapConstants` asks for growth by appended blocks of four floats, and the engine's developer guide lets generated constants change only through their generators. A hand edit of the shader's constants passes the build and the fit's check, and only the test that compares the shader's pixels with the CPU twin catches it. A block inserted in the middle shifts every field after it, so the shader reads the wrong bytes and reports no error.
:::

## A toy version

Before the real shader, the idea fits in about forty lines. The program below applies two curves to a gray value that is already exposed. One is `Reinhard`. The other is a toy with a toe below middle gray, a power-shaped shoulder above it and white at 6.5 stops. It prints the display value at every stop from -4 to +7; search for the stop where each curve passes 0.9.

```cpp sketch="image-tone-mapping-toy.cpp"
#include <cmath>
#include <cstdio>

// Two tone curves on a gray value x that the exposure already scaled: Reinhard, and a toy with a toe, a straight part
// and a shoulder in stops from middle gray, the shape of Strata's Filmic curve with simpler numbers.
constexpr float c_MiddleGray = 0.18f;

float Reinhard(float x)
{
	return x / (1.0f + x);
}

float ToyFilmic(float x)
{
	constexpr float c_Slope = 1.4f;      // log-log slope at middle gray
	constexpr float c_WhiteStops = 6.5f; // stops above middle gray where white is reached
	if (x <= 0.0f)
		return 0.0f;
	const float stops = std::log2(x / c_MiddleGray);
	if (stops >= c_WhiteStops)
		return 1.0f;
	if (stops < 0.0f)
		return c_MiddleGray * std::exp2(c_Slope * stops);
	const float power = c_Slope * c_MiddleGray * std::log(2.0f) * c_WhiteStops / (1.0f - c_MiddleGray);
	return c_MiddleGray + (1.0f - c_MiddleGray) * (1.0f - std::pow(1.0f - stops / c_WhiteStops, power));
}

int main()
{
	std::printf("stops   x      Reinhard  ToyFilmic\n");
	for (int stops = -4; stops <= 7; stops += 1)
	{
		const float x = c_MiddleGray * std::exp2(static_cast<float>(stops));
		std::printf("%+3d  %7.4f  %7.4f  %7.4f\n", stops, x, Reinhard(x), ToyFilmic(x));
	}
	return 0;
}
```

```text output-of="image-tone-mapping-toy.cpp"
stops   x      Reinhard  ToyFilmic
 -4   0.0113   0.0111   0.0037
 -3   0.0225   0.0220   0.0098
 -2   0.0450   0.0431   0.0258
 -1   0.0900   0.0826   0.0682
 +0   0.1800   0.1525   0.1800
 +1   0.3600   0.2647   0.3493
 +2   0.7200   0.4186   0.5072
 +3   1.4400   0.5902   0.6520
 +4   2.8800   0.7423   0.7816
 +5   5.7600   0.8521   0.8923
 +6  11.5200   0.9201   0.9765
 +7  23.0400   0.9584   1.0000
```

1. **Line 10:** `Reinhard` is one division.
2. **Line 21:** from the white stops upward the toy returns exactly 1.
3. **Line 23:** below middle gray the toy multiplies 0.18 by two to the power of the slope times the stops, so the shadows fall faster than `Reinhard`'s.
4. **Lines 24-25:** the shoulder's power is chosen so that its slope at middle gray matches the toe's slope.

The output shows the three parts of the plot. Below middle gray the toy curve is lower than `Reinhard` (0.0258 against 0.0431 at -2 stops): the toe deepens the shadows. At 0 stops it returns 0.18, and from there to +3 stops it climbs faster, which is the contrast. After +5 stops its slope falls, and it reaches 1.0 at +7, while `Reinhard` is at 0.958 and still rising.

Strata's Filmic curve has the same three parts with fitted numbers. A second program prints middle gray's value under each curve. It copies the formulas of `Tonemap.frag.slang` for `ACES`, `AgX` and `KhronosNeutral`, and has no code for Filmic, which passes 0.18 straight through because the fit demands it. Search for the value that `ACES` gives.

```cpp sketch="image-tone-mapping-gray.cpp"
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdio>

// Middle gray (0.18, already exposed) under each of Strata's curves, from the formulas of Tonemap.frag.slang: the value
// the curve returns, and its sRGB code. A gray input has equal channels, so one channel stands for all three.
using Vec3 = std::array<float, 3>;
using Mat3 = std::array<Vec3, 3>;

Vec3 Multiply(const Mat3& matrix, const Vec3& v)
{
	Vec3 result{};
	for (int row = 0; row < 3; row++)
		result[row] = matrix[row][0] * v[0] + matrix[row][1] * v[1] + matrix[row][2] * v[2];
	return result;
}

float ACES(float gray)
{
	const Mat3 input = { Vec3{ 0.59719f, 0.35458f, 0.04823f }, Vec3{ 0.07600f, 0.90834f, 0.01566f }, Vec3{ 0.02840f, 0.13383f, 0.83777f } };
	const Mat3 output = { Vec3{ 1.60475f, -0.53108f, -0.07367f }, Vec3{ -0.10208f, 1.10813f, -0.00605f }, Vec3{ -0.00327f, -0.07276f, 1.07602f } };
	Vec3 c = Multiply(input, { gray, gray, gray });
	for (float& v : c)
		v = (v * (v + 0.0245786f) - 0.000090537f) / (v * (0.983729f * v + 0.4329510f) + 0.238081f);
	return Multiply(output, c)[0];
}

float AgX(float gray)
{
	const Mat3 inset = { Vec3{ 0.842479f, 0.078434f, 0.079224f }, Vec3{ 0.042328f, 0.878469f, 0.079166f }, Vec3{ 0.042376f, 0.078434f, 0.879143f } };
	const Mat3 outset = { Vec3{ 1.196879f, -0.098021f, -0.099030f }, Vec3{ -0.052897f, 1.151903f, -0.098961f }, Vec3{ -0.052972f, -0.098043f, 1.151074f } };
	Vec3 c = Multiply(inset, { gray, gray, gray });
	for (float& v : c)
	{
		const float x = std::clamp((std::log2(v) + 12.47393f) / (12.47393f + 4.026069f), 0.0f, 1.0f);
		const float x2 = x * x;
		const float x4 = x2 * x2;
		v = 15.5f * x4 * x2 - 40.14f * x4 * x + 31.96f * x4 - 6.868f * x2 * x + 0.4298f * x2 + 0.1191f * x - 0.00232f;
	}
	return std::pow(std::max(Multiply(outset, c)[1], 0.0f), 2.2f); // the curve's output is gamma 2.2: back to linear
}

float KhronosNeutral(float gray)
{
	const float offset = gray < 0.08f ? gray - 6.25f * gray * gray : 0.04f;
	return gray - offset; // below the compression start (0.76) nothing else changes
}

float Filmic(float gray)
{
	return gray; // the curve returns 0.18 at t = 0 by construction (target T1)
}

float Encode(float linear)
{
	return linear <= 0.0031308f ? 12.92f * linear : 1.055f * std::pow(linear, 1.0f / 2.4f) - 0.055f;
}

int main()
{
	const float gray = 0.18f;
	const float exposed = gray * std::exp2(0.8f);
	const char* names[] = { "None", "Reinhard", "ACES", "ACES +0.8 EV", "AgX", "Khronos Neutral", "Filmic" };
	const float values[] = { gray, gray / (1.0f + gray), ACES(gray), ACES(exposed), AgX(gray), KhronosNeutral(gray), Filmic(gray) };
	for (int index = 0; index < 7; index++)
		std::printf("%-16s %.4f  code %3.0f\n", names[index], values[index], Encode(values[index]) * 255.0f);
	return 0;
}
```

```text output-of="image-tone-mapping-gray.cpp"
None             0.1800  code 118
Reinhard         0.1525  code 109
ACES             0.1056  code  91
ACES +0.8 EV     0.2250  code 130
AgX              0.2145  code 128
Khronos Neutral  0.1400  code 105
Filmic           0.1800  code 118
```

1. **Line 19:** `ACES` is a matrix, a fraction of two small formulas and a second matrix.
2. **Line 29:** `AgX` is an inset, a conversion to stops, a sixth-power formula, an outset and a power of 2.2.
3. **Line 44:** `KhronosNeutral` subtracts a small offset and changes nothing else below its peak of 0.76.
4. **Line 50:** Filmic returns its input: middle gray shows as middle gray is the fit's first target.
5. **Line 63:** the second `ACES` entry adds 0.8 stops, a factor of two to the power 0.8.

## The real code

### The clamp before the curves

The data enters the pass as exposed light, and a curve does arithmetic that can overflow. Some lights are infinite, a division by zero somewhere can make a :term[NaN]{id=nan} (not a number), and a 32-bit float that holds 1e30 squares to infinity. The first stage defends against this.

```cpp src="Strata/shaders/PostProcess/Tonemap.frag.slang#L85-L89"
float3 ExposeSceneColor(float3 color)
{
	color *= u_Exposure[ST_EXPOSURE_MULTIPLIER] * u_Parameters.InversePreExposure;
	return clamp(select(isnan(color), float3(0.0), color), float3(0.0), float3(c_MaxExposedValue));
}
```

`ExposeSceneColor` multiplies the color by the exposure factor (from [Camera exposure](../image/exposure.md)) and by `InversePreExposure`, which divides out the factor that the HDR target stored the light with ([Why images need post-processing](../image/why-post.md)). It replaces NaN with 0 and clamps each channel to the range from 0 to `c_MaxExposedValue`, which is 1e8. At that value every curve is saturated long since, and the products inside them (the sixth-power formula of `AgX`, for example) still fit a float.

### Contrast, the switch and saturation

After the grading, three parts of the pass act on the light.

```cpp src="Strata/shaders/PostProcess/Tonemap.frag.slang#L246-L260"
if (u_Parameters.Contrast != 1.0)
	color = 0.18 * pow(color / 0.18, float3(u_Parameters.Contrast));

switch (u_Parameters.Operator)
{
	case ST_TONEMAP_REINHARD:        color = color / (1.0 + color); break;
	case ST_TONEMAP_ACES:            color = TonemapACES(color); break;
	case ST_TONEMAP_AGX:             color = TonemapAgX(color); break;
	case ST_TONEMAP_KHRONOS_NEUTRAL: color = TonemapKhronosNeutral(color); break;
	case ST_TONEMAP_FILMIC:          color = TonemapFilmic(color, u_Parameters.FilmicToeSlope, u_Parameters.FilmicWhiteStops, u_Parameters.FilmicShoulderPower); break;
	default:                         color = clamp(color, 0.0, 1.0); break;
}

float luminance = dot(color, float3(0.2126, 0.7152, 0.0722));
color = max(lerp(float3(luminance), color, u_Parameters.Saturation), float3(0.0));
```

1. **Lines 246-247:** contrast raises the color divided by 0.18 to the power `Contrast`, then multiplies by 0.18 again. Middle gray returns 0.18 for every power, so it stays fixed, and in stops the whole image tilts about it.
2. **Lines 249-256:** the switch applies one curve. A value the enum does not know falls to `default`, which clamps like `None`.
3. **Lines 259-260:** saturation mixes each channel with the luminance of the :term[display-linear]{id=display-linear} color. It gives 1 for no change, 0 for gray, and 2 for twice as vivid.

Contrast works in log space because a power in light is a straight line in stops: raising to 2 doubles the distance in stops from middle gray. For a gray of 0.36, one stop above, a contrast of 2 gives $0.18 \times (0.36 / 0.18)^2 = 0.72$, two stops above. The :term[graphics processing unit]{id=gpu} (GPU) test of that name renders exactly this.

**Contrast** is the tilt of the picture about middle gray: values above it grow, values below shrink, and middle gray stays.

**Saturation** is how far a color's channels lie from the gray of the same luminance. The code on the CPU side clamps `Contrast` to the range from 0.1 to 4 and saturation to 0 and above, before the values reach the buffer.

### The classic operators

Three of the classic curves are functions of their own, and `Reinhard` is one line of the switch.

```cpp src="Strata/shaders/PostProcess/Tonemap.frag.slang#L122-L171"
float3 TonemapACES(float3 color)
{
	const float3x3 inputMatrix = transpose(float3x3(0.59719, 0.07600, 0.02840, 0.35458, 0.90834, 0.13383, 0.04823, 0.01566, 0.83777));
	const float3x3 outputMatrix = transpose(float3x3(1.60475, -0.10208, -0.00327, -0.53108, 1.10813, -0.07276, -0.07367, -0.00605, 1.07602));
	color = mul(inputMatrix, color);
	float3 a = color * (color + 0.0245786) - 0.000090537;
	float3 b = color * (0.983729 * color + 0.4329510) + 0.238081;
	return clamp(mul(outputMatrix, (a / b)), 0.0, 1.0);
}

// AgX base transform with a polynomial fit of the default contrast curve.
float3 AgXContrast(float3 x)
{
	float3 x2 = x * x;
	float3 x4 = x2 * x2;
	return 15.5 * x4 * x2 - 40.14 * x4 * x + 31.96 * x4 - 6.868 * x2 * x + 0.4298 * x2 + 0.1191 * x - 0.00232;
}

float3 TonemapAgX(float3 color)
{
	const float3x3 inset = transpose(float3x3(0.842479062253094, 0.0423282422610123, 0.0423756549057051, 0.0784335999999992, 0.878468636469772, 0.0784336, 0.0792237451477643, 0.0791661274605434, 0.879142973793104));
	const float3x3 outset = transpose(float3x3(1.19687900512017, -0.0528968517574562, -0.0529716355144438, -0.0980208811401368, 1.15190312990417, -0.0980434501171241, -0.0990297440797205, -0.0989611768448433, 1.15107367264116));
	const float minEV = -12.47393;
	const float maxEV = 4.026069;

	color = mul(inset, max(color, float3(1e-10)));
	color = clamp((log2(color) - minEV) / (maxEV - minEV), 0.0, 1.0);
	color = AgXContrast(color);
	color = mul(outset, color);
	// The curve output is display-encoded (gamma 2.2); return linear values for the shared sRGB encode.
	return pow(max(color, float3(0.0)), float3(2.2));
}

// Khronos PBR Neutral tone mapper (keeps base colors accurate up to the highlights).
float3 TonemapKhronosNeutral(float3 color)
{
	const float startCompression = 0.8 - 0.04;
	const float desaturation = 0.15;
	float x = min(color.r, min(color.g, color.b));
	float offset = x < 0.08 ? x - 6.25 * x * x : 0.04;
	color -= offset;
	float peak = max(color.r, max(color.g, color.b));
	if (peak < startCompression)
		return color;
	float d = 1.0 - startCompression;
	float newPeak = 1.0 - d * d / (peak + d - startCompression);
	color *= newPeak / peak;
	float g = 1.0 - 1.0 / (desaturation * (peak - newPeak) + 1.0);
	return lerp(color, float3(newPeak), g);
}
```

1. **Lines 124-129:** `ACES` is the input matrix, a fraction of two small formulas in the color, and the output matrix: a published fit of the film pipeline's steps.
2. **Lines 147-152:** `AgX` is the inset, a conversion to stops between two fixed limits, the sixth-power formula of line 149, the outset and a power of 2.2 back to linear light.
3. **Lines 158-165:** a small offset is subtracted, and a color whose peak is below 0.76 is returned as it is.
4. **Lines 166-170:** above that peak, the peak goes to a value below 1 and the color fades toward white by an amount that grows with the compression.

### Filmic

**Filmic** is Strata's own tone curve, fitted ahead of time against stated targets by `Tools/FitFilmic.py`. Its code lives in `Strata/shaders/Include/Filmic.slang`, and `FilmicConstants.slang` supplies its constants. It works in stops $t = \log_2(x / 0.18)$ of an exposed value $x$.

The idea first, in words: below middle gray, a toe whose steepness in stops per stop turns from $C_0$ (the contrast at middle gray) to the toe's own slope over about three stops. Above middle gray, a shoulder that is a power curve and reaches 1 with zero slope after a number of stops. Middle gray stays at 0.18.

:::note[The formula]
For $t < 0$: $y = 0.18 \cdot 2^{C_t t + (C_0 - C_t) \tau (e^{t/\tau} - 1)}$. For $0 \le t < T_w$: $y = 0.18 + 0.82 (1 - (1 - t/T_w)^q)$. For $t \ge T_w$: $y = 1$.

$C_0$ is the slope at middle gray, 1.39788. $C_t$ is the toe's slope, $\tau$ is 3 stops, $T_w$ is the stops where white is reached, and $q = C_0 \cdot 0.18 \ln 2 \cdot T_w / 0.82$ makes the shoulder's slope at middle gray equal $C_0$.
:::

The curve of one channel comes first. Search for its three branches: the toe below middle gray, the shoulder above it, and the exact 1 at the white stops.

```cpp src="Strata/shaders/Include/Filmic.slang#L11-L21"
float FilmicCurve(float x, float toeSlope, float whiteStops, float shoulderPower)
{
	if (x <= 0.0)
		return 0.0;
	float t = log2(x / c_FilmicMiddleGray);
	if (t < 0.0)
		return c_FilmicMiddleGray * exp2(toeSlope * t + (c_FilmicContrast - toeSlope) * c_FilmicToeWidth * (exp(t / c_FilmicToeWidth) - 1.0));
	if (t >= whiteStops)
		return 1.0;
	return c_FilmicMiddleGray + (1.0 - c_FilmicMiddleGray) * (1.0 - pow(1.0 - t / whiteStops, shoulderPower));
}
```

1. **Lines 15-17:** below middle gray the :term[exponent]{id=exponent} is the log-log form of the toe. At $t = 0$ it gives 0.18 exactly, and its slope falls from $C_0$ toward $C_t$ as $t$ goes negative.
2. **Lines 18-19:** from $T_w$ stops up the function returns exactly 1, which is why nothing in the highlights can clip afterward.
3. **Line 20:** the shoulder is one power of $1 - t/T_w$, chosen so the slope at $t = 0$ matches the toe's side.

The curve works on a single channel. The operator that calls it works on a color.

```cpp src="Strata/shaders/Include/Filmic.slang#L28-L40"
float3 TonemapFilmic(float3 color, float toeSlope, float whiteStops, float shoulderPower)
{
	float3 inset = mul(c_FilmicInset, max(color, float3(0.0)));
	float largest = max(inset.r, max(inset.g, inset.b));
	if (!(largest > 0.0))
		return float3(0.0);
	float largestCurved = FilmicCurve(largest, toeSlope, whiteStops, shoulderPower);
	float3 perChannel = float3(FilmicCurve(inset.r, toeSlope, whiteStops, shoulderPower), FilmicCurve(inset.g, toeSlope, whiteStops, shoulderPower),
		FilmicCurve(inset.b, toeSlope, whiteStops, shoulderPower));
	float channel = smoothstep(c_FilmicChannelStart, c_FilmicChannelEnd, log2(largest / c_FilmicMiddleGray));
	float3 curved = lerp(inset * (largestCurved / largest), perChannel, channel);
	return clamp(mul(c_FilmicOutset, curved), float3(0.0), float3(1.0));
}
```

1. **Line 30:** the inset matrix first, on the color with negative values removed.
2. **Lines 34-36:** two candidates: the whole color scaled by the factor its largest channel gets from the curve, and each channel through the curve alone.
3. **Line 37:** a smooth step blends them by the stops of the largest channel above middle gray: all of the first at 0 or below, all of the second at 4 or above.
4. **Lines 38-39:** the outset matrix follows, and the result is clamped to the display range.

The two candidates have separate jobs. In the shadows, a per-channel toe with a slope above 1 raises the ratio between channels to that power, and a dark blue sky would deepen to a primary color. Scaling the color as a whole keeps the scene's ratios.

In the highlights the per-channel curve takes bright saturated colors to white without skewing them, since the inset has drawn their channels together. The largest channel is on the curve in both candidates, so a gray pixel gets exactly the curve.

### The CPU twin

Toe and Shoulder, the two settings of `PostProcessComponent`, are not the curve's parameters. The CPU turns them into three numbers each frame, and the shader receives those.

```cpp src="Strata/src/Strata/Renderer/PostProcessMath.cpp#L111-L137"
FilmicCurve MakeFilmicCurve(float toe, float shoulder)
{
	toe = std::clamp(std::isfinite(toe) ? toe : 0.5f, 0.0f, 1.0f);
	shoulder = std::clamp(std::isfinite(shoulder) ? shoulder : 0.5f, 0.0f, 1.0f);
	FilmicCurve curve;
	curve.ToeSlope = FilmicConstants::c_Contrast * (0.85f + 0.5f * toe);
	curve.WhiteStops = 6.5f + 3.0f * (shoulder - 0.5f);
	const float middleGray = FilmicConstants::c_MiddleGray;
	curve.ShoulderPower = FilmicConstants::c_Contrast * middleGray * std::log(2.0f) * curve.WhiteStops / (1.0f - middleGray);
	return curve;
}

float EvaluateFilmicCurve(float x, const FilmicCurve& curve)
{
	const float middleGray = FilmicConstants::c_MiddleGray;
	if (!(x > 0.0f))
		return 0.0f;
	const float t = std::log2(x / middleGray);
	if (t < 0.0f)
	{
		const float toeWidth = FilmicConstants::c_ToeWidth;
		return middleGray * std::exp2(curve.ToeSlope * t + (FilmicConstants::c_Contrast - curve.ToeSlope) * toeWidth * (std::exp(t / toeWidth) - 1.0f));
	}
	if (t >= curve.WhiteStops)
		return 1.0f;
	return middleGray + (1.0f - middleGray) * (1.0f - std::pow(1.0f - t / curve.WhiteStops, curve.ShoulderPower));
}
```

1. **Lines 113-114:** both inputs clamp to the range from 0 to 1, and an infinite or NaN value falls back to the default, 0.5.
2. **Line 116:** the toe slope is $C_0 (0.85 + 0.5 \cdot \text{Toe})$, so at the default it is 1.1 times the contrast.
3. **Line 117:** white is reached at $6.5 + 3 (\text{Shoulder} - 0.5)$ stops: 5 stops at 0, 8 at 1.
4. **Line 119:** the power that gives the shoulder the same slope as the toe at middle gray: the slopes match.
5. **Lines 128-136:** `EvaluateFilmicCurve` is the shader's `FilmicCurve` again, line for line.

A **CPU twin** is the same arithmetic as a shader function, written in C++ in `PostProcessMath` so that a test can run it without a GPU. `EvaluateFilmicCurve` is one. Strata keeps twins of the sRGB encode, the dither's noise, Filmic, white balance, grading and the motion blur's profile there.

A twin has two uses. The unit tests check the curve against its targets with exact numbers. A GPU test renders a frame and compares the pixels with the twin, so a change to the shader that the twin lacks fails.

`FilmicConstants.h` holds the same fitted numbers as `FilmicConstants.slang`, and both come from one generator. The CPU function `ApplyFilmic` mirrors `TonemapFilmic` with the same blend.

A worked example shows the whole curve with numbers.

:::example
Take an exposed gray of 0.72, two stops above middle gray. With Toe and Shoulder at 0.5, $T_w = 6.5$ and $q = 1.3825$. The shoulder gives $0.18 + 0.82 (1 - (1 - 2/6.5)^{1.3825})$. The inner part is $0.6923^{1.3825} = 0.6015$, so $y = 0.18 + 0.82 \times 0.3985 = 0.5068$.

The sRGB encode of 0.5068 is code 189. `Reinhard` gives 0.4186 (code 173) for the same input: the Filmic image is brighter at two stops, and its mid-tones have more contrast.

Now two stops below, $x = 0.045$ and $t = -2$. The toe slope is $C_t = 1.3979 \times 1.1 = 1.5377$. The exponent is $1.5377 \times (-2) + (1.3979 - 1.5377) \times 3 \times (e^{-2/3} - 1) = -3.0753 + 0.2041 = -2.8712$. So $y = 0.18 \times 2^{-2.8712} = 0.0246$, code 43. `Reinhard` returns 0.0431 here: Filmic's shadows are deeper, as the toy showed.
:::

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| `ACES` as the only curve | Film production; many engines offer it | A standard that artists know | Darker mid-tones, hue drift of saturated colors, no Toe or Shoulder |
| A curve on luminance only | Tools that must keep every channel ratio | No hue skew | Saturated lights never reach white; out-of-gamut colors clip |
| A lookup table of the whole look | Grading tools; Strata's color lookup, after the curve | Any look an artist can draw | The table cannot follow exposure, and it costs memory |
| A game-industry curve of toe and shoulder | Many games | Few parameters | No gamut handling, so hue skew returns |
| A per-channel curve without gamut compression | Early engines | One line of arithmetic | Hue skew: red lights turn orange |

The sources of each are in Further reading. Strata keeps the classic operators because they are the choices an artist knows, and a scene file that stores one must keep drawing it.

## How it is tested

The suite `Renderer.PostProcessMath`, in `StrataTests/src/Renderer/PostProcessMathTests.cpp`, runs without a GPU. Its test case `Filmic meets its targets` checks the committed constants against targets T1 to T9 of the fit. Middle gray shows as middle gray, the slope there is $C_0$ within 0.01, and white comes at $T_w$ stops. A value of 0.005 shows at a code from 2 to 4, and ten test colors keep their hue within 10 or 6 degrees. The test case `Filmic's look keeps the curve monotonic and soft` sweeps Toe and Shoulder over a grid and checks that each curve rises and never clips early.

On the GPU, the case `Filmic on the GPU matches its CPU reference` in `StrataTests/src/Renderer/GPUSceneCameraTests.cpp` (suite `GPU.SceneRenderer.Camera`) renders a frame and compares every pixel with `ApplyFilmic`. The case `Contrast is applied around middle gray` in the suite `GPU.SceneRenderer.PostProcess` renders a wall at 0.36 and checks that contrast 2 moves it to 0.72.

Run the unit suite with `build/windows/bin/Debug/StrataTests.exe --test-suite=Renderer.PostProcessMath`. Run the GPU cases through `ctest` with the label `gpu`.

The generator checks the same targets itself.

```sh
python Tools/FitFilmic.py --check
```

The command reads the fitted parameters committed in `FilmicConstants.h`, checks every target and writes nothing. It exits with 1 when a target fails.

The generator has three other modes. The plain run fits and writes both files. `--from-committed` refines the committed numbers as one more start, and `--rewrite` writes the files again from the committed parameters with no fit.

## Changing it safely

The extension points are three. A new operator is appended to `TonemapOperator`, to the property's list in `RendererComponents.cpp`, to the shader's defines and its switch, and to the unit and GPU tests. A new look parameter is appended to `TonemapConstants` in a block of four floats. A new curve target belongs in `Tools/FitFilmic.py`, and the committed files are written again by the script.

Follow the rules.

- Values of `TonemapOperator` never change, because they are stored in scenes and scripts.
- The shader's declaration and the struct change together, and the `static_assert` offsets are updated in the same change.
- Never edit `FilmicConstants.slang` or `FilmicConstants.h`. Run the generator and commit both files, then run `FitFilmic.py --check`.
- Run the Filmic test cases and the GPU test that compares the shader with the twin before you commit.

## What went wrong before

An earlier Filmic applied its curve per channel everywhere, and the toe's slope of about 1.5 raised the ratio of a channel pair to that power. A dark blue sky came out 1.88 times as saturated as the scene's, more than ACES at +1 stop. The fix was the blend: below middle gray the color scales as a whole. Target T9 and the check in `Filmic meets its targets` that shadows keep at most 1.3 times the scene's saturation guard it today.

## Summary

- A tone curve maps exposed light to display values: it keeps middle gray near its place and rolls the highlights off, and the choice of curve decides contrast, brightness and hue.
- Filmic shows 0.18 as 0.18, and at two stops above middle gray it gives 0.5068, where `Reinhard` gives 0.4186.
- The operator travels from `PostProcessComponent::Tonemapper` through `TonemapConstants` byte 16 to the shader's switch, and its values never change.
- Toe and Shoulder become three curve numbers on the CPU, the generated constants are never edited, and `FitFilmic.py --check` guards the targets.
- Contrast works before the curve in log space, saturation after it, and the exposed input is clamped to 1e8.

## Check yourself

1. A scene looks dark and flat under ACES and fine under Filmic with the same exposure. What does the table of middle gray's values say, and what do you change?

   :::answer{tests="choose-curve"}
   ACES shows middle gray at 0.1056, about code 91, while Filmic shows 0.18, code 118. The ACES image is darker by design. Add about 0.8 stops of exposure to ACES, or keep Filmic. Changing saturation or contrast would not move the mid-tones the same way.
   :::

2. Compute what `Reinhard` and the Filmic curve at default look give for an exposed gray of 1.44, three stops above middle gray.

   :::answer{tests="compute-filmic"}
   `Reinhard`: $1.44 / 2.44 = 0.5902$. Filmic: $q = 1.3825$, $1 - 3/6.5 = 0.5385$, and $0.5385^{1.3825} = 0.4249$, so $y = 0.18 + 0.82 \times 0.5751 = 0.6516$. The numbers are close because both curves bend there, but Filmic is brighter.
   :::

3. Which option is correct? The operator number of a saved scene is changed by the next release when a better curve exists.

   - A. The number is changed so the new curve takes its slot.
   - B. The new curve is appended with a new number.
   - C. The scene file is rewritten by the editor.

   :::answer{tests="trace-operator"}
   B. The numbers are part of what files and scripts rely on: a scene that stored 2 means ACES forever. Option A would change the look of every old scene, and option C does not help scripts that hold the number.
   :::

4. A game artist wants her lamp's red to stay red under bright exposure. Which curve change helps, and why?

   :::answer{tests="choose-curve"}
   A curve with a smaller hue skew helps: Filmic's inset and per-channel highlight, or `AgX`. A pure luminance curve keeps the ratio but clips out-of-gamut colors. Plain `Reinhard` per channel turns red toward orange, as the lantern example showed.
   :::

5. Predict what happens to a gray of 0.18 when Contrast is 3 and the curve is Filmic. Then say why saturation does not move it.

   :::answer{tests="pass-order"}
   Contrast gives $0.18 \times (0.18 / 0.18)^3 = 0.18$, so the gray stays at 0.18 and the curve returns 0.18. Saturation mixes with the luminance, which equals the gray itself, so nothing changes. Middle gray is fixed in both.
   :::

6. A teammate fixes a color by editing a number in `FilmicConstants.slang` by hand. Which check fails, and why?

   :::answer{tests="change-filmic"}
   `FitFilmic.py --check` still passes: it reads only the fitted parameters written in `FilmicConstants.h`. The GPU case `Filmic on the GPU matches its CPU reference` fails, because the shader no longer matches the twin, which uses the :term[header]{id=header}. The right change is to the generator's targets, then a fit that writes both files.
   :::

## Exercises

1. **Basic.** Pick a tone curve for a scene of red lamps in a dark corridor and say what each of None, `Reinhard` and Filmic does to the lamps' hue.

   :::answer[Worked solution]{tests="choose-curve"}
   None clamps the red channel and leaves the others, so a lamp turns toward orange or yellow. `Reinhard` compresses the largest channel most, which is the skew from the page's example, and the lamp drifts toward orange. Filmic with its inset takes the lamp to white without much drift. Choose Filmic.
   :::

2. **Medium.** Trace it yourself: where does a `Tonemapper` of `ACES` become the shader's switch case? Name the files and functions.

   :::answer[Worked solution]{tests="trace-operator"}
   The property is registered in `Strata/src/Strata/Renderer/RendererComponents.cpp` near line 486 (the list from `None` to `Filmic`). `SceneRenderer::RenderPostDisplay` in `SceneRendererPost.cpp` copies it into `tonemap.Operator`. The struct puts it at offset 16, and `Tonemap.frag.slang` switches on `u_Parameters.Operator` with the `ST_TONEMAP_*` defines.
   :::

3. **Medium.** Write a self-contained check that the Filmic curve returns middle gray at 0.18, has slope near 1.398 there and reaches 1 at its white stops.

   :::answer[Worked solution]{tests="compute-filmic,change-filmic"}
   The program uses the committed constants and a slope measured by a central difference of one thousandth of a stop. Read each printed line against its target.

   ```cpp sketch="image-tone-mapping-twin.cpp"
   #include <cmath>
   #include <cstdio>

   // A CPU-twin check in miniature: the Filmic curve of one channel with Strata's fitted constants, and the three
   // things a test can compare it with, the middle-gray value, the slope there and the white point.
   constexpr float c_MiddleGray = 0.18f;
   constexpr float c_Contrast = 1.39788385f;
   constexpr float c_ToeWidth = 3.0f;

   float Curve(float x, float toeSlope, float whiteStops, float shoulderPower)
   {
   	if (x <= 0.0f)
   		return 0.0f;
   	const float t = std::log2(x / c_MiddleGray);
   	if (t < 0.0f)
   		return c_MiddleGray * std::exp2(toeSlope * t + (c_Contrast - toeSlope) * c_ToeWidth * (std::exp(t / c_ToeWidth) - 1.0f));
   	if (t >= whiteStops)
   		return 1.0f;
   	return c_MiddleGray + (1.0f - c_MiddleGray) * (1.0f - std::pow(1.0f - t / whiteStops, shoulderPower));
   }

   int main()
   {
   	const float toe = 0.5f;
   	const float shoulder = 0.5f;
   	const float toeSlope = c_Contrast * (0.85f + 0.5f * toe);
   	const float whiteStops = 6.5f + 3.0f * (shoulder - 0.5f);
   	const float power = c_Contrast * c_MiddleGray * std::log(2.0f) * whiteStops / (1.0f - c_MiddleGray);

   	const float step = 1e-3f;
   	const float above = std::log2(Curve(c_MiddleGray * std::exp2(step), toeSlope, whiteStops, power));
   	const float below = std::log2(Curve(c_MiddleGray * std::exp2(-step), toeSlope, whiteStops, power));
   	std::printf("middle gray -> %.5f\n", Curve(c_MiddleGray, toeSlope, whiteStops, power));
   	std::printf("slope at middle gray %.4f (contrast %.4f)\n", (above - below) / (2.0f * step), c_Contrast);
   	std::printf("white at %.1f stops -> %.1f\n", whiteStops, Curve(c_MiddleGray * std::exp2(whiteStops), toeSlope, whiteStops, power));
   	return 0;
   }
   ```

   ```text output-of="image-tone-mapping-twin.cpp"
   middle gray -> 0.18000
   slope at middle gray 1.3975 (contrast 1.3979)
   white at 6.5 stops -> 1.0
   ```

   1. **Lines 26-28:** Toe and Shoulder become the three curve numbers, as `MakeFilmicCurve` does.
   2. **Lines 31-32:** the slope is a central difference of one thousandth of a stop on each side of middle gray.
   3. **Lines 33-35:** the three printed lines are the targets: 0.18, the slope $C_0$ and white at its stops.
   :::

4. **Hard.** Fit Filmic again with a changed target and say which tests move.

   :::answer[Worked solution]{tests="change-filmic"}
   Change one target in `Tools/FitFilmic.py`, such as T4's code range, and run the script. It fits and writes both constants files, or writes nothing and exits with 1 when a target fails. Then run `Renderer.PostProcessMath`: `Filmic meets its targets` moves with T4, and the GPU comparison moves because the pixels change. Run `--check` last.
   :::

## Where it lives in Strata

- `Strata/shaders/PostProcess/Tonemap.frag.slang`: the display pass, `ExposeSceneColor` and the classic operators.
- `Strata/shaders/Include/Filmic.slang` and `FilmicConstants.slang`: the curve, and its generated constants.
- `Strata/src/Strata/Renderer/PostProcessMath.cpp` and `FilmicConstants.h`: the CPU twins and constants.
- `Strata/src/Strata/Renderer/PostProcessData.h`: `TonemapConstants`.
- `Strata/src/Strata/Renderer/SceneRendererPost.cpp`: `RenderPostDisplay`.
- `Tools/FitFilmic.py`: the fit and `--check`.
- Tests: the suites `Renderer.PostProcessMath`, `GPU.SceneRenderer.Camera` and `GPU.SceneRenderer.PostProcess`.

## Further reading

- Reinhard, Stark, Shirley and Ferwerda, "Photographic Tone Reproduction for Digital Images" (2002): the Reinhard curve (intermediate).
- Hable, "Uncharted 2: HDR Lighting" (GDC 2010): a toe and shoulder curve (intermediate).
- Hill, notes on the ACES fit (ACES fitting in shaders) (advanced).
- Sobotka, AgX (a Blender color transform) (advanced).
- The Khronos PBR Neutral tone mapper (<https://github.com/KhronosGroup/ToneMapping>): the specification and a reference shader (intermediate).
- Uchimura, "HDR Theory and Practice" (CEDEC 2017): the Gran Turismo curve (advanced).
