---
id: image/lens-effects
title: "Lens effects: bloom, vignette, flares and fringes"
description: "How Strata adds what a real lens adds around bright light: a glow that keeps its size at every resolution, a darker frame, color fringes and flares."
kind: internals
size: L
tracks: [E]
needs: [image/tone-mapping, basics/signals]
time: 90
learn:
  - id: bloom-reach
    text: compute how many levels a bloom radius uses at an image height, and the weight of the deepest level
  - id: bloom-mix
    text: explain why the Karis average and the choice between a mix and an addition keep bloom steady and keep the image's brightness
  - id: lens-numbers
    text: compute the vignette's darkening, the aberration's shift and a ghost's place for a given view and image size
  - id: trace-sun
    text: trace the sun from the frame's light to the starburst and say why a wall removes it
since: 0.3.0
status: final
---

A camera lens does not keep light where the scene put it. Around bright light it adds a glow, it darkens the corners, it draws red and blue fringes toward the edges, and it throws faint copies of a bright lamp across the frame. Strata adds these four effects after the scene is drawn and before the :term[tone mapping]{id=tone-mapping-image} that turns light into display colors: **bloom**, the vignette, chromatic aberration and lens flares. Each is restrained and off or low by default. Bloom is on at 0.04, the vignette at 0.12, and aberration and flares at 0.

The page teaches how each is made and why, and ends with the passes that run them. It does not teach the [tone mapping](tone-mapping.md) that composes them, [depth of field](depth-of-field.md), [motion blur](motion-blur.md) or how the :term[mips]{id=mip} of a texture are made.

## The problem and how engines solve it

Look at a street lamp at night. A real lens does not focus the lamp to a point: the light of one point lands as a small spot, and the shape of that spot is the lens's *point spread*. The lamp is thousands of times brighter than the wall beside it, so even the faint rim of its spot is brighter than the wall, and you see the lamp glow. To make the whole picture, add up the spot of every point. That sum is a *:term[convolution]{id=convolution}*: each output pixel is a weighted sum of its neighbors, and the weights are the kernel.

Take a row of five pixels with one bright value, 0, 0, 8, 0, 0, and the kernel 1/4, 1/2, 1/4. The row becomes 0, 2, 4, 2, 0. The glow spreads out, and the total stays at 8: a blur moves light and does not add it.

The cost is the problem. A glow 64 pixels wide on each side needs a kernel of 129 by 129, which is 16,641 reads for each pixel. A 1920 by 1080 image has 2,073,600 pixels, so one frame would need about 35 billion reads. Engines use two ways to cut that.

- A blur in two passes, one along the rows and one along the columns, as a Gaussian kernel allows. The reads fall from 129 × 129 to 129 + 129 per pixel, about 535 million for the frame. The cost still grows with the radius.
- A pyramid shrinks the image by half again and again, blurs each small level a little, and adds the levels back together. A level two steps down has one sixteenth of the pixels, and one of its pixels covers four times the width, so a small kernel there reaches far. Each level doubles the reach, and the cost is only the sum of a few small images.

Strata uses the pyramid. Its chain starts at half resolution, so with 13 reads to go down and 9 to come up, a 1080-row frame costs about 15 million reads, against 35 billion for the direct kernel.

The filter that shrinks a level matters. The simplest is the box: the mean of a 2 by 2 block. A small bright thing that moves one pixel can fall in or out of a block and make the glow flicker, which is the aliasing that [Sampling, aliasing and filtering](../basics/signals.md) describes. A wider filter that reads the neighbors too hides the jump. A 2014 talk on the post-processing of a shooter game, named in Further reading, used 13 reads arranged as five overlapping boxes, and Strata uses the same filter.

The return to full size uses a **tent filter**: a small kernel whose weights rise and fall in a triangle, such as 1, 2, 1 along each direction. Its weights sum to 1 after division, so the step keeps the light.

A pyramid has one more weakness. A single pixel a thousand times brighter than its neighbors, such as a glint on wet stone, is a **firefly**. It spreads into a large glow at every level, and the glow flickers as the pixel appears and vanishes between frames.

The remedy is to weight each block by one over one plus its :term[luminance]{id=luminance} before averaging, so a block dominated by one very bright pixel counts for little. That weighting is the **Karis average**.

Two designs decide how bloom meets the image. The classic one keeps only the pixels above a threshold, blurs them and adds the result: the glow adds light, and a pixel that crosses the threshold makes it pop. The other blurs everything and mixes: the output is a share $a$ of the blurred image and $1 - a$ of the sharp one, so no light is created. Strata does both, and the choice is the threshold.

The last problem is size. A kernel of fixed width in pixels covers a smaller share of a larger image: 64 pixels are 5.9 % of 1080 rows and 3 % of 2160. A game that turns the resolution up would see its glow shrink. Strata states the radius as a share of the image's height, and the chain follows it.

## The map

The bloom, the flare and the tone map run in the post-processing part of the frame, after exposure. The shrinking steps run first. The flare reads one level of the chain before the enlarging steps add the deeper levels, and the tone map applies everything last.

```mermaid caption="The order of one frame's lens effects. Exposure comes first, then the bloom's shrinking steps, the flare that reads level 1 of them, the bloom's enlarging steps, and the tone map that reads the aberration, bloom, flare and vignette." alt="A flow from exposure to the bloom's shrinking steps, which feed first the lens flare pass and then the bloom's enlarging steps. The bloom, the flare and the scene color enter the tone map, where the aberration, bloom, flare, vignette, grading and tone curve apply in that order."
flowchart LR
	E[exposure] --> D[bloom downsamples, levels 0 to n]
	D --> F[LensFlare.comp, reads level 1]
	D --> U[bloom upsamples]
	F --> T[Tonemap.frag]
	U --> T
	S[HDR scene color] --> D
	S --> T
	T --> O[aberration, bloom, flare, vignette, grading, curve]
```

Three files hold the effects. `Strata/shaders/PostProcess/Bloom.comp.slang` does all three bloom steps, chosen by a mode. `Strata/shaders/PostProcess/LensFlare.comp.slang` draws the ghosts and the halo at a quarter of the resolution. `Strata/shaders/PostProcess/Tonemap.frag.slang` shifts the colors for the aberration, mixes in the bloom, adds the flare and the starburst, and applies the vignette.

The dispatches and the settings are in `Strata/src/Strata/Renderer/SceneRendererPost.cpp`, and the properties are in `PostProcessComponent` in `Strata/src/Strata/Renderer/RendererComponents.h`. Everything runs on the :term[main thread's]{id=main-thread} :term[command list]{id=command-list} and the :term[graphics processing unit]{id=gpu} (GPU).

The chain is a texture with mip levels. Level 0 is half the viewport's size, each level halves again, and the chain stops when the smaller side would fall under 4 pixels or at 8 levels. A 1080-row frame has a chain of 540 rows at level 0, so it allocates all 8 levels, though the default radius uses 6.

## The contract

- The glow's size is a share of the image's height, never of its width or of a pixel count. The reason is the problem above: a game's resolution must not change how its picture looks.
- The tone map mixes bloom in when the threshold is 0 and adds it when the threshold is above 0. The reason: a mix of an empty bloom would darken everything, and an addition of a full-image bloom would brighten everything.
- A **soft knee** is a threshold that fades in over a range instead of cutting at one value, so a pixel that crosses it does not make the glow jump. The threshold is on the exposed color, after the exposure.
- Non-finite colors and values above 65,000 never enter the chain. The reason: one broken material would spread over the whole screen.
- The vignette acts on :term[scene-linear]{id=scene-linear} light before the grading and the tone curve. The reason: a vignette after the curve is a gray ring and not the fall-off of a lens.
- The flare reads only the bright part of the image. The reason: a flare made of the whole image would be a second blur.
- Every effect has a value that disables it, and the tone map skips the work: a frame without lens flares costs nothing for them.

:::rule
:term[Shaders]{id=shader} writing :term[high dynamic range]{id=high-dynamic-range} targets clamp with `SanitizeHDR`, and post effects run between the temporal anti-aliasing resolve and the tone mapping. The reasons: one non-finite value would spread through the bloom chain over the whole screen, and before the tone curve the light is still scene-linear. See [Why post-processing](why-post.md).
:::

## A toy version

:::question
Does the toy's C++ look unfamiliar? It uses functions and `std::vector` ([Programming 2](../basics/programming-2.md)) and references and calls such as `std::clamp(` ([Programming 3](../basics/programming-3.md)).
:::

The toy makes a 16 by 16 gray image with one bright pixel of 16 and shrinks it three times with the box filter. It adds the levels back with bilinear reads, and prints each level's mean and peak and the glow along the middle row. Look at the peak falling and at the mean staying put.

```cpp sketch="image-lens-effects-toy.cpp"
// A toy bloom: a box-filtered pyramid, down and then up.
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <vector>

struct Image
{
	int Size = 0;
	std::vector<float> Pixels;
};

static Image MakeImage(int size)
{
	return Image{ size, std::vector<float>(static_cast<size_t>(size) * size, 0.0f) };
}

static float At(const Image& image, int x, int y)
{
	x = std::clamp(x, 0, image.Size - 1);
	y = std::clamp(y, 0, image.Size - 1);
	return image.Pixels[y * image.Size + x];
}

// Each pixel of the result is the mean of a 2x2 box of the source: the box filter.
static Image Downsample(const Image& source)
{
	Image result = MakeImage(source.Size / 2);
	for (int y = 0; y < result.Size; y++)
		for (int x = 0; x < result.Size; x++)
			result.Pixels[y * result.Size + x] = 0.25f * (At(source, 2 * x, 2 * y) + At(source, 2 * x + 1, 2 * y) + At(source, 2 * x, 2 * y + 1) + At(source, 2 * x + 1, 2 * y + 1));
	return result;
}

// Bilinear read: x and y count texels, and a texel's center is a whole number.
static float Bilinear(const Image& image, float x, float y)
{
	const int x0 = static_cast<int>(std::floor(x));
	const int y0 = static_cast<int>(std::floor(y));
	const float fx = x - static_cast<float>(x0);
	const float fy = y - static_cast<float>(y0);
	const float top = At(image, x0, y0) * (1.0f - fx) + At(image, x0 + 1, y0) * fx;
	const float bottom = At(image, x0, y0 + 1) * (1.0f - fx) + At(image, x0 + 1, y0 + 1) * fx;
	return top * (1.0f - fy) + bottom * fy;
}

static float Mean(const Image& image)
{
	float sum = 0.0f;
	for (const float pixel : image.Pixels)
		sum += pixel;
	return sum / static_cast<float>(image.Pixels.size());
}

int main()
{
	constexpr int c_Levels = 4;
	std::vector<Image> levels = { MakeImage(16) };
	levels[0].Pixels[8 * 16 + 8] = 16.0f; // one bright pixel
	for (int level = 1; level < c_Levels; level++)
		levels.push_back(Downsample(levels[level - 1]));
	for (int level = 0; level < c_Levels; level++)
		std::printf("level %d: %2dx%-2d mean %.4f peak %.3f\n", level, levels[level].Size, levels[level].Size, Mean(levels[level]), *std::max_element(levels[level].Pixels.begin(), levels[level].Pixels.end()));

	// Upsample: each level adds the smaller glow, read bilinearly, to its own pixels.
	Image glow = levels[c_Levels - 1];
	for (int level = c_Levels - 2; level >= 0; level--)
	{
		Image sum = levels[level];
		for (int y = 0; y < sum.Size; y++)
			for (int x = 0; x < sum.Size; x++)
				sum.Pixels[y * sum.Size + x] += Bilinear(glow, (static_cast<float>(x) + 0.5f) / 2.0f - 0.5f, (static_cast<float>(y) + 0.5f) / 2.0f - 0.5f);
		glow = sum;
	}
	std::printf("glow mean %.4f, divided by %d levels %.4f\n", Mean(glow), c_Levels, Mean(glow) / c_Levels);
	std::printf("row 8 of the glow, divided by %d:", c_Levels);
	for (int x = 0; x < glow.Size; x++)
		std::printf(" %.2f", glow.Pixels[8 * glow.Size + x] / c_Levels);
	std::printf("\n");
	return 0;
}
```

```text output-of="image-lens-effects-toy.cpp"
level 0: 16x16 mean 0.0625 peak 16.000
level 1:  8x8  mean 0.0625 peak 4.000
level 2:  4x4  mean 0.0625 peak 1.000
level 3:  2x2  mean 0.0625 peak 0.250
glow mean 0.2500, divided by 4 levels 0.0625
row 8 of the glow, divided by 4: 0.00 0.00 0.00 0.00 0.01 0.02 0.04 0.26 4.68 0.70 0.33 0.13 0.09 0.06 0.04 0.04
```

1. **Line 31:** the box filter: the mean of four source pixels, which keeps the total light.
2. **Line 59:** the only bright pixel of the whole image.
3. **Line 72:** the half-texel shift puts each read at the center of the pixel it enlarges.
4. **Line 75:** the sum of four levels has four times the mean, so the toy divides by the number of levels.

The peak falls by four at each level, from 16 to 4, 1 and 0.25: the same light covers four times the area. The mean stays at 0.0625, because a box filter moves light and keeps the total. The sum of four levels has four times the mean, so the toy divides by the number of levels. That division is the real code's `BloomScale`.

## The real code, in the order data flows

### The levels and the radius

The settings come first. `GetBloomSpan` turns the radius into the number of levels as a real number, and everything else follows from it.

```cpp src="Strata/src/Strata/Renderer/SceneRendererPost.cpp#L1003-L1007"
const float safeRadius = std::isfinite(radius) ? std::clamp(radius, 0.01f, 0.25f) : 64.0f / 1080.0f;
float span = std::log2(safeRadius * static_cast<float>(std::max(height, 1u)));
if (std::abs(span - std::round(span)) < 1e-4f)
	span = std::round(span);
return std::clamp(span, 1.0f, static_cast<float>(std::max(levels, 1u)));
```

Take the default radius, 64 / 1080 of the height. At 1080 rows the radius is 64 pixels and $\log_2 64 = 6$: the span is 6 and the chain uses 6 levels. At 2160 rows it is 128 pixels, a span of 7, and so 7 levels. At 720 rows it is 42.7 pixels, a span of 5.415, and the code rounds up to 6 levels. The last level then counts 0.415 of its weight, because the deepest level carries only the fraction of it that the span reaches.

A span within 0.0001 of a whole number is that number, so the stored value 0.0592593 does not add a seventh level of near zero weight.

$$\mathrm{span} = \log_2(r \, h)$$

Here $r$ is the radius as a share of the height and $h$ is the image height in pixels. The result is the number of doublings that the glow's reach spans. The code clamps it between 1 and 8, the largest chain. A radius larger than the chain reaches gives a smaller glow than asked for: 8640 rows at the default radius would want 9 and get 8.

Two functions use the span. The first shrinks the image level by level, and the number of levels is the span rounded up. Look at the test of `bloom`: without it the chain still makes two levels, for the flare.

```cpp src="Strata/src/Strata/Renderer/SceneRendererPost.cpp#L1032-L1037"
m_BloomSpan = GetBloomSpan(settings.BloomRadius, m_ViewportSize.y, m_BloomLevels);
const uint32_t levels = bloom ? static_cast<uint32_t>(std::ceil(m_BloomSpan)) : std::min(2u, m_BloomLevels);
DispatchBloom(commandList, settings, prefilterSet, RenderData::c_BloomPrefilter, 0, 1.0f);
for (uint32_t level = 1; level < levels; level++)
	DispatchBloom(commandList, settings, m_BloomDownsampleSets[level], RenderData::c_BloomDownsample, level, 1.0f);
return levels;
```

Level 0 reads the scene color with the threshold, and each deeper level reads the one above it.

The second function adds the levels back, deepest first. Look at the weight of the step that adds the deepest level.

```cpp src="Strata/src/Strata/Renderer/SceneRendererPost.cpp#L1040-L1047"
void SceneRenderer::RenderBloomUpsamples(nvrhi::ICommandList* commandList, const PostProcessComponent& settings, uint32_t levels)
{
	// The deepest level is weighted by the fraction of it the span covers.
	const float deepestWeight = m_BloomSpan - static_cast<float>(levels - 1);
	for (uint32_t level = levels - 1; level-- > 0;)
		DispatchBloom(commandList, settings, m_BloomUpsampleSets[level], RenderData::c_BloomUpsample, level, level + 2 == levels ? deepestWeight : 1.0f);
	m_Stats.BloomLevels = levels;
}
```

Only that step uses the fraction from the span. Every other step weighs 1.

### The 13-tap filter and the threshold

Level 0 applies the threshold and the Karis weights. Deeper levels use the plain weights. The shader reads 13 points around each output pixel and groups them into five boxes. Nine reads, `a` to `i`, form a 3 by 3 grid two texels apart, and four, `j` to `m`, sit one texel from the center along the diagonals. Each box is four reads, and the center box is `j`, `k`, `l` and `m`.

```cpp src="Strata/shaders/PostProcess/Bloom.comp.slang#L64-L77"
	// Five overlapping 2x2 boxes: the center one weighs 0.5, the corner ones 0.125 each.
	float3 boxes[5] = { (j + k + l + m) * 0.25, (a + b + d + e) * 0.25, (b + c + e + f) * 0.25, (d + e + g + h) * 0.25, (e + f + h + i) * 0.25 };
	float weights[5] = { 0.5, 0.125, 0.125, 0.125, 0.125 };

	float3 result = float3(0.0);
	float weightSum = 0.0;
	for (int box = 0; box < 5; box++)
	{
		float weight = karisAverage ? KarisWeight(boxes[box], weights[box]) : weights[box];
		result += boxes[box] * weight;
		weightSum += weight;
	}
	return result / weightSum;
}
```

1. **Line 65:** five overlapping 2 by 2 boxes of the 13 reads; the center box is the four reads nearest the pixel.
2. **Line 66:** the weights, 0.5 for the center and 0.125 for each corner, sum to 1.
3. **Line 72:** the Karis weight divides a box's weight by one plus its luminance, on level 0 only.
4. **Line 76:** dividing by the weight sum keeps the total light.

:::example[A firefly through the five boxes]
Let a corner box hold one pixel of luminance 1000 and three of 1, so its mean is 250.75, and let the other four boxes hold pixels of 1.

The plain weights give $0.5 \cdot 1 + 0.125 \cdot 250.75 + 3 \cdot 0.125 \cdot 1 = 32.2$. With the Karis weights, the hot box counts $0.125 / 251.75 = 0.0005$ instead of 0.125, the others count 0.0625 each and the center 0.25, and the result is 1.28. The firefly has gone from 32 times the surroundings to 1.3 times.
:::

The soft knee is eight lines.

```cpp src="Strata/shaders/PostProcess/Bloom.comp.slang#L92-L99"
if (u_Parameters.Threshold <= 0.0)
	return color;
// Soft knee: a quadratic ramp around the threshold instead of a hard cut.
float brightness = max(color.r, max(color.g, color.b));
float knee = max(u_Parameters.Knee, 1e-5);
float soft = clamp(brightness - u_Parameters.Threshold + knee, 0.0, 2.0 * knee);
soft = soft * soft / (4.0 * knee);
return color * (max(soft, brightness - u_Parameters.Threshold) / max(brightness, 1e-5));
```

With a threshold of 1 the knee is 0.5, and the brightness $b$ of a pixel is its largest channel. A pixel at $b = 0.5$ gives nothing, at 0.75 gives 0.03, at 1 gives 0.125, at 1.5 gives 0.5 and at 2 gives 1. The curve is a :term[quadratic]{id=quadratic-equation} ramp that joins the straight line $b - 1$ without a corner, so a pixel that crosses the threshold fades in. The knee is half the threshold, which `DispatchBloom` sets. Past the knee the glow is the excess above the threshold.

The enlarging step reads the smaller level through the tent filter, in the 3 by 3 block 1, 2, 1 / 2, 4, 2 / 1, 2, 1 divided by 16. It adds the result to the larger level's own pixels, and the deepest level is first multiplied by the fraction from the span.

### The mix in the tone map

The bloom is finished before the tone map. The tone map's constants carry `BloomScale`, which is 1 divided by the span, so the sum of the levels returns to the brightness of one.

```cpp src="Strata/shaders/PostProcess/Tonemap.frag.slang#L194-L205"
if (u_Parameters.BloomIntensity > 0.0)
{
	// The bloom is already exposed. Without a threshold it holds all the light, and a small fraction of it
	// scatters into the glow (energy-conserving mix). With a threshold it holds only the bright excess, which is
	// added on top: mixing would darken everything that does not bloom.
	float3 bloom = u_Bloom.Sample(u_LinearSampler, v_UV).rgb * u_Parameters.BloomScale;
	if (u_Parameters.BloomAdditive != 0u)
		color += bloom * u_Parameters.BloomIntensity;
	else
		color = lerp(color, bloom, u_Parameters.BloomIntensity);
	color = min(color, float3(c_MaxExposedValue));
}
```

1. **Line 199:** the bloom level 0, read bilinearly and scaled by `BloomScale`, which is 1 over the span.
2. **Lines 200–203:** above a threshold of 0 the glow is added; at 0 the color mixes toward the glow by the intensity.
3. **Line 204:** the result stays finite.

At threshold 0 and the default intensity of 0.04, a pixel becomes $0.96 \cdot c + 0.04 \cdot b$, where $c$ is its own color and $b$ the blurred value there. A wall keeps 96 % of itself and gains 4 % of the glow around it. At 0.2 the glow is five times as strong and the wall keeps 80 %. At the default the change is hard to see in a picture; the strong setting shows where the glow goes.

With a threshold above 0 the pass adds, and a wall far from any lamp is unchanged. The code limits the intensity to 1 and the result to a very large finite value.

::figure{id=bloom-intensity variant=off}

::figure{id=bloom-intensity variant=default}

::figure{id=bloom-intensity variant=strong}

::figure{id=bloom-intensity variant=off crop=lantern}

::figure{id=bloom-intensity variant=default crop=lantern}

::figure{id=bloom-intensity variant=strong crop=lantern}

### The vignette

A lens collects less light from the sides of its view, and the fall-off is the **vignette**. The law of a simple lens is the cos^4 law: the light at an angle $\theta$ from the axis falls by $\cos^4 \theta$.

The angle $\theta$ is the **field angle**: the angle between a pixel's ray and the camera's axis.

A pixel's field angle comes from the projection. Its screen position runs from -1 to 1 on each axis, and the tangent of the angle along an axis is the position times the tangent of half the :term[field of view]{id=field-of-view} on that axis. Since $\cos^2 \theta = 1 / (1 + \tan^2 \theta)$, the fall-off needs no :term[cosine]{id=cosine}.

$$m = 1 - v + \frac{v}{(1 + a^2 x^2 + b^2 y^2)^2}$$

Here $m$ is the factor on the light and $v$ is the setting `Vignette`, from 0 to 1. The numbers $x$ and $y$ are the pixel's screen position, and $a$ and $b$ are the tangents of half the view across and up. The squares are read "$a$ times $x$, squared". At $v = 1$ the factor is the full law, and at 0 it is 1.

Take a 60 degree vertical view in a 16:9 image. The tangents are $b = \tan 30° = 0.577$ and $a = 0.577 \cdot 16 / 9 = 1.026$. At a corner, $x = y = 1$ and $1 + 1.053 + 0.333 = 2.387$, so the full law gives $1 / 2.387^2 = 0.176$: 2.5 stops darker.

At the default 0.12 the corner keeps $1 - 0.12 \cdot (1 - 0.176) = 0.90$: 10 % darker. At the middle of the top edge, $x = 0$ and $y = 1$, the factor at 0.12 is 0.95. The center is untouched.

The shader applies the factor to the color. Look at `secantSquared`, which is $1 + \tan^2 \theta$ and is squared at the end.

```cpp src="Strata/shaders/PostProcess/Tonemap.frag.slang#L231-L236"
if (u_Parameters.Vignette > 0.0)
{
	float2 field = UVToNDC(v_UV) * u_Parameters.VignetteTangents;
	float secantSquared = 1.0 + dot(field, field);
	color *= lerp(1.0, 1.0 / (secantSquared * secantSquared), u_Parameters.Vignette);
}
```

The tangents come from `GetVignetteTangents`. Look at the branch for orthographic cameras.

```cpp src="Strata/src/Strata/Renderer/SceneRendererPost.cpp#L1150-L1157"
glm::vec2 SceneRenderer::GetVignetteTangents(const SceneCamera& camera, glm::uvec2 viewportSize)
{
	// Orthographic views have no field angle: they vignette as a 60 degree view of their aspect.
	const float aspect = static_cast<float>(viewportSize.x) / static_cast<float>(std::max(viewportSize.y, 1u));
	if (camera.Orthographic || camera.Projection[0][0] == 0.0f || camera.Projection[1][1] == 0.0f)
		return glm::vec2(aspect, 1.0f) * std::tan(glm::radians(30.0f));
	return glm::vec2(1.0f / std::abs(camera.Projection[0][0]), 1.0f / std::abs(camera.Projection[1][1]));
}
```

The function takes the tangents from the projection: 1 over its first and second diagonal entries. An orthographic camera has no field angle, so it vignettes as a 60 degree view of its aspect.

::figure{id=vignette-sweep variant=none}

::figure{id=vignette-sweep variant=default}

::figure{id=vignette-sweep variant=full}

### Chromatic aberration

A lens bends each color a little differently, so red and blue land at slightly different sizes. **Chromatic aberration (lateral)** is that difference of size. The image of each color is a copy of the others scaled about the center, so the fringes grow toward the corners and vanish at the center.

The tone map reads red a little farther out and blue a little nearer in, and takes green where it is.

```cpp src="Strata/shaders/PostProcess/Tonemap.frag.slang#L180-L185"
if (u_Parameters.ChromaticAberration > 0.0)
{
	float2 offset = v_UV - 0.5;
	source.r = u_SceneColor.Sample(u_LinearSampler, 0.5 + offset * (1.0 + u_Parameters.ChromaticAberration)).r;
	source.b = u_SceneColor.Sample(u_LinearSampler, 0.5 + offset * (1.0 - u_Parameters.ChromaticAberration)).b;
}
```

The scale $k$ is the setting times `c_ChromaticAberrationScale`, which is 0.5 over half the width of a 3840-pixel image, or 0.00026. Red is read at the center plus the offset times $1 + k$. At a corner of a 3840 by 2160 image the offset is 0.5 across, so red moves by $0.5 \cdot 0.00026 \cdot 3840 = 0.5$ pixels, and blue moves the other way. At 1920 pixels across the same setting moves red by 0.25 pixels, since $k$ is a share of the image and not of a pixel. At the center the offset is 0 and nothing moves.

The crops below enlarge a fence near the right edge of a 3840 by 2160 picture five times. The picture is drawn without :term[anti-aliasing]{id=anti-aliasing}, so each edge is one sharp step and the half-pixel shift shows as a colored line.

::figure{id=aberration-corner variant=off crop=edge}

::figure{id=aberration-corner variant=on crop=edge}

### Lens flares

Light also reflects between the glass surfaces of a lens and comes out as faint copies of a bright source. A **lens flare** is the set of those artifacts: ghosts, a halo and, for a bright disk such as the sun, rays called the starburst. A *ghost* is a scaled copy of the bright part of the image on the line through the source and the center, on either side of the center. The *halo* is a ring a little inside the frame, and the starburst comes from the lens's opening.

The flare reads level 1 of the bloom chain, a quarter of the resolution. The bright part of a level is what exceeds 4 in exposed luminance, and its excess is compressed toward 16.

```cpp src="Strata/shaders/PostProcess/LensFlare.comp.slang#L76-L81"
float3 color = SampleSmooth(uv);
float luminance = Luminance(color);
if (!(luminance > c_FlareThreshold))
	return float3(0.0);
float excess = luminance - c_FlareThreshold;
return color * (excess / (1.0 + excess / c_FlareCeiling) / luminance);
```

A pixel with luminance 20 has an excess of 16 and contributes 8: $16 / (1 + 16 / 16)$. A pixel of 5000, which is the sun, contributes 15.9 and cannot exceed 16. Even the sun leaves ghosts as faint as a lamp's. The tone map adds the flare at the setting times `c_LensFlareScale`, 0.02.

The ghosts sit at scales -1.6, -0.7, 0.45 and 1.2. A source at screen position $p$ shows at $0.5 + (0.5 - p) \cdot k$ for each scale $k$. A lamp at $x = 0.8$ on the middle row shows at $x = 0.98$, 0.71, 0.365 and 0.14. Positive scales mirror the lamp to the other side of the center, and negative ones keep its side.

Each ghost has a tint, and the edge fade dims them toward the corners. The halo reads the point 0.45 image heights toward the center and weighs it by how near that point is to the center.

```cpp src="Strata/shaders/PostProcess/LensFlare.comp.slang#L120-L136"
float3 flare = float3(0.0);
float fade = EdgeFade(uv);
for (int ghost = 0; ghost < 4; ghost++)
{
	float2 source = 0.5 + (0.5 - uv) / c_GhostScales[ghost];
	flare += BrightPart(source) * c_GhostTints[ghost] * fade;
}
// The halo gathers from the point c_HaloRadius toward the center, weighted by how near that point is to the center.
float2 towardCenter = (0.5 - uv) * float2(u_Parameters.Aspect, 1.0);
float centerDistance = length(towardCenter);
if (centerDistance > 1e-4)
{
	float2 source = uv + towardCenter / centerDistance * c_HaloRadius / float2(u_Parameters.Aspect, 1.0);
	float sourceDistance = length((source - 0.5) * float2(u_Parameters.Aspect, 1.0));
	flare += BrightPart(source) * c_HaloTint * (1.0 - smoothstep(0.0, 0.35, sourceDistance)) * fade;
}
o_Flare[pixel] = float4(min(flare, float3(c_MaxHDRValue)), SunVisibility());
```

1. **Line 124:** the ghost reads the source that lands here, so it divides by the scale.
2. **Line 125:** each ghost is tinted and fades toward the image's edges.
3. **Line 132:** the halo reads the point 0.45 image heights toward the center.
4. **Line 134:** the halo's weight falls as that point leaves the center.
5. **Line 136:** alpha carries the sun's visibility from the 16 depth taps.

The flare reads level 1 as the shrinking step left it, and not after the enlarging steps. The tent filters of the enlarging steps leave diamond-shaped contours in the glow, and the flare's threshold would cut those out as shapes. The chain therefore runs its first two levels for the flare even when Bloom is off, and the tone map then adds no bloom.

The starburst is the sun's. The frame projects the direction of the directional light to a screen position. The tone map draws six rays there at full resolution, because rays thin near the disk are narrower than the flare's texels. The shape is $|\cos 3\varphi|^{40}$ times a fall-off of $e^{-d / 0.08}$, where $\varphi$ is the angle around the disk and $d$ the distance in image heights. At 3.5 degrees from a ray the first factor is 0.5, so each ray is about 7 degrees wide.

The sun's visibility decides whether the rays show. The shader reads 16 depth taps: 8 at 0.01 image heights from the disk and 8 at half that, offset by 22.5 degrees. A tap that sees the sky, where reversed depth is 0 and the tap is inside the image, counts 1/16. A wall that covers half the disk gives 0.5, and a wall that covers it all gives 0. The ghosts need no such test, because a covered sun gives no bright pixel for them to copy.

::figure{id=flare-sun variant=off}

::figure{id=flare-sun variant=on}

::figure{id=flare-sun variant=off crop=sun}

::figure{id=flare-sun variant=on crop=sun}

::figure{id=flare-sun variant=off crop=ghosts}

::figure{id=flare-sun variant=on crop=ghosts}

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Two-pass Gaussian blur at full resolution | Engines with a fixed, small glow | Exact shape, no pyramid | Cost that grows with the radius; at 64 pixels about 535 million reads for a frame |
| Pyramid with box filters | Many tutorials | Fewer reads | The glow flickers as small bright things move |
| Threshold and add only | Older engines | One path in the tone map | A glow that pops at the threshold, and no energy-conserving mode |
| Radius in pixels | Engines with a fixed kernel | A simpler setting | A glow that shrinks when the resolution rises |
| Flare from a picture at the sun | Games with one fixed sun | Sharp, art-directed ghosts | No ghosts from lamps and reflections, and no ghost of a covered sun |

Sources for these are in Further reading.

## How it is tested

The bloom, the vignette, the aberration and the flares have GPU tests in four suites. They need a GPU, so they carry the label `gpu`, and each ends by checking that the device logged no new error.

- `GPU.SceneRenderer.PostProcess` holds the bloom cases: bloom spreads light around its source, a threshold adds glow without dimming the rest, and bloom keeps working after the image changes size.
- `GPU.SceneRenderer.Camera` holds the radius cases: the glow covers the same share of the image at 1080 and 2160 rows. Half or twice the standard radius halves or doubles the glow, and the default at 1080 rows has the six levels of 0.6.0.
- The same suite holds the vignette cases: the same on both sides, untouched at the center and falling like the law, and an orthographic view that vignettes as a 60 degree one.
- `GPU.SceneRenderer.GrainAndAberration` holds one case for aberration: red and blue separate by half a pixel at the corner of a 3840 by 2160 image and nothing moves at the center.
- `GPU.SceneRenderer.LensFlare` holds three: off, flares change nothing; ghosts mirror a source through the center, with the bloom's level count 0; and the starburst shows only while the sky around the disk is seen.

Run one with `build/windows/bin/Debug/StrataTests.exe --test-suite=GPU.SceneRenderer.LensFlare`, or the whole `gpu` label through `ctest --preset windows-debug`.

## Changing it safely

The extension points are the properties of `PostProcessComponent`, the constants in `Strata/src/Strata/Renderer/PostProcessData.h`, and the three shaders. A new lens effect belongs in the tone map or in a pass of its own between the temporal anti-aliasing resolve and the tone map.

- Keep the radius a share of the height. The reason: a glow that changes with the resolution changes the game's look.
- Keep a value that disables the effect and a branch that skips it. The reason: players turn each effect off, and a disabled effect must cost nothing.
- Change the cap and the numbers of the flare in the shader and in the tests together. The reason: the tests measure the codes the ghosts and the rays add.
- Check before committing: the four suites, then the whole `gpu` label.

## What went wrong before

Before 0.7.0 the vignette was a ring drawn after the tone curve, at a default of 0.2. A ring after the curve darkens display values and cannot be told from a gray frame. It is now the lens's own law on scene-linear light before the grading, with a default of 0.12, and scenes that stored a value keep it under the new model. The tests for symmetry, the center and the law keep it from drifting back.

## Summary

- The span of the bloom's chain is the :term[base 2]{id=binary} :term[logarithm]{id=logarithm} of the radius times the height. The chain has as many levels as the span rounds up to, and the deepest level counts the fraction it reaches.
- The Karis average makes a firefly count little in its block, and a mix at threshold 0 and an addition above it keep the brightness of the rest of the image.
- The vignette scales light by one over the square of one plus the squared tangents. The aberration moves red and blue by a share of the image. Each ghost sits at 0.5 plus 0.5 minus the source's position, times its scale.
- The sun's position goes from the frame's directional light through the flare pass into the tone map, and the starburst shows only when the depth taps see the sky.

## Check yourself

1. A game runs at 1440 rows with the default `BloomRadius`. What span does the chain use?
   - A. 5.5, using 6 levels with the deepest at about half weight
   - B. 6.4, using 7 levels with the deepest at 0.4
   - C. 6.4, using 6 levels
   - D. 7, using 7 levels

   :::answer{tests="bloom-reach"}
   B. The radius is $64 / 1080 \cdot 1440 = 85.3$ pixels and $\log_2 85.3 = 6.415$, so the chain needs 7 levels and the deepest counts 0.415. A takes the logarithm of 44. C forgets that the chain rounds up. D rounds the span instead of weighing the last level.
   :::

2. A frame holds only a wall at luminance 1, and the threshold is 2. Strata adds the empty bloom. What would the wall become if it mixed at an intensity of 0.2 instead?
   - A. 1.0
   - B. 0.8
   - C. 1.2
   - D. 0.2

   :::answer{tests="bloom-mix"}
   B. Nothing exceeds the threshold, so the bloom is empty. A mix keeps $0.8$ of the wall and takes $0.2$ of black, which gives 0.8: the whole image dims. A is what the addition gives. C would brighten, and D takes the mix backward.
   :::

3. A 4K image is 3840 pixels wide and the aberration is 1. How far from green is the red edge at a column 1500 pixels from the center, and what is it at 1920 pixels wide at the same share of the image?
   - A. 0.2 pixels; 0.1 pixels
   - B. 0.39 pixels; 0.2 pixels
   - C. 0.39 pixels; 0.39 pixels
   - D. 1.5 pixels; 1.5 pixels

   :::answer{tests="lens-numbers"}
   B. $k = 0.5 / 1920$ and the shift is $1500 \cdot k = 0.39$ pixels. At half the width, a column at the same share of the image is 750 pixels from the center and moves 0.2 pixels. C ignores that the shift is a share of the image. A and D do not use $k$.
   :::

4. The sun is behind a wall that covers it fully. Which of these still shows?
   - A. The starburst, since the rays come from the light
   - B. The ghosts of the lamps in view
   - C. Both
   - D. Neither

   :::answer{tests="trace-sun"}
   B. The 16 depth taps around the disk see no sky, so the starburst's visibility is 0 and the rays do not show. A bright lamp in view still gives a bright pixel in level 1, and it keeps its ghosts. A covered sun gives no bright pixel for ghosts of its own.
   :::

## Exercises

1. **Basic.** Predict how many levels, and with what weight on the deepest, the default radius uses at 720, 1080, 2160 and 8640 rows. Then run a program and compare.

   :::answer[Worked solution]{tests="bloom-reach" solution="sketches/image-lens-effects-span.cpp"}
   By hand, the radius times the height is 42.7, 64, 128 and 512 pixels, and the logarithms are 5.415, 6, 7 and 9. The chain rounds up to 6, 6, 7 and 9 levels, but it holds at most 8.

   ```cpp sketch="image-lens-effects-span.cpp"
   // How many levels a bloom radius of 64 / 1080 of the image's height uses at four heights.
   #include <algorithm>
   #include <cmath>
   #include <cstdio>
   #include <initializer_list>

   int main()
   {
   	const float radius = 64.0f / 1080.0f;
   	const float maxLevels = 8.0f;
   	for (const int height : { 720, 1080, 2160, 8640 })
   	{
   		float span = std::log2(radius * static_cast<float>(height));
   		if (std::abs(span - std::round(span)) < 1e-4f) // a span within 1e-4 of a whole number is that number
   			span = std::round(span);
   		span = std::clamp(span, 1.0f, maxLevels);
   		const float levels = std::ceil(span);
   		std::printf("%4d rows: span %.3f, %.0f levels, deepest weight %.3f\n", height, span, levels, span - (levels - 1.0f));
   	}
   	return 0;
   }
   ```

   ```text output-of="image-lens-effects-span.cpp"
    720 rows: span 5.415, 6 levels, deepest weight 0.415
   1080 rows: span 6.000, 6 levels, deepest weight 1.000
   2160 rows: span 7.000, 7 levels, deepest weight 1.000
   8640 rows: span 8.000, 8 levels, deepest weight 1.000
   ```

   1. **Line 13:** the span, the base 2 logarithm of the radius in pixels.
   2. **Lines 14–15:** a span within 0.0001 of a whole number is that number.
   3. **Line 16:** the clamp to the largest chain, which is why 8640 rows print 8.

   The program mirrors `GetBloomSpan`. At 8640 rows the span of 9 clamps to 8: the glow is half the size you asked for, and the weight stays at 1.
   :::

2. **Medium.** Run a command to give a sample's Post Process a strong bloom. Capture one view at 1280 by 720 and another at 2560 by 1440, and predict the glow's reach as a share of the image height in both. Measure it, and say why it is the same.

   :::answer[Worked solution]{tests="bloom-mix"}
   First run `entity.find` with `{"component": "PostProcess"}`: it returns the identifiers (IDs) of the entities that hold the component. Then run `component.set` with one of them:

   ```json
   {"entity": "<the ID>", "component": "PostProcess", "values": {"BloomIntensity": 0.2}}
   ```

   Then run `viewport.capture` with `{"width": 1280, "height": 720}` and again with `{"width": 2560, "height": 1440}`. The radius is $0.059 \cdot 720 = 43$ pixels in the first and 85 pixels in the second. In both pictures the glow reaches about 6 % of the height from a lamp: measure the distance where the glow falls to the background. The reach is the same because `BloomRadius` is a share of the height, and the chain gains a level when the height doubles.
   :::

3. **Hard.** Trace the sun yourself from the frame's directional light to the starburst's place in the tone map. Name each function and say what happens to the sun's position on the way, and why the starburst goes when a wall covers the sun.

   :::answer[Worked solution]{tests="trace-sun"}
   In `SceneRenderer::RenderFrame` in `Strata/src/Strata/Renderer/SceneRenderer.cpp`, the frame projects the reversed light direction through the camera's view and projection and writes `sunUV` as x times 0.5 plus 0.5 and 0.5 minus y times 0.5. `SceneRenderer::RenderPostHDR` passes it to `SceneRenderer::RenderLensFlare` in `SceneRendererPost.cpp`, which stores it in `m_StarburstSun`, sets `m_Starburst` to 16 times a white card's luminance, the :term[gray card]{id=gray-card}'s divided by 0.18, and writes it into the flare pass's constants. `SceneRenderer::RenderPostDisplay` copies both into `TonemapConstants`. The flare pass writes the sky's share in alpha, and the tone map multiplies the rays by it, so a wall gives 0.
   :::

## Where it lives in Strata

- Shaders: `Strata/shaders/PostProcess/Bloom.comp.slang`, `Strata/shaders/PostProcess/LensFlare.comp.slang`, `Strata/shaders/PostProcess/Tonemap.frag.slang`.
- Code: `SceneRenderer::GetBloomSpan`, `SceneRenderer::RenderPostHDR`, `SceneRenderer::RenderLensFlare`, `SceneRenderer::GetVignetteTangents` and `SceneRenderer::RenderPostDisplay` in `Strata/src/Strata/Renderer/SceneRendererPost.cpp`; the sun's place in `SceneRenderer::RenderFrame`.
- Constants: `Strata/src/Strata/Renderer/PostProcessData.h`.
- Properties: `PostProcessComponent` in `Strata/src/Strata/Renderer/RendererComponents.h`.
- Tests: the suites `GPU.SceneRenderer.PostProcess`, `GPU.SceneRenderer.Camera`, `GPU.SceneRenderer.LensFlare` and `GPU.SceneRenderer.GrainAndAberration`.
- Commands: `entity.find`, `component.set` and `viewport.capture`.

## Further reading

- Jorge Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare" (SIGGRAPH 2014): the 13-tap filter, the Karis average on the first level and the tent enlarging step; intermediate.
- Matt Pharr, Wenzel Jakob and Greg Humphreys, "Physically Based Rendering": the chapter on camera models, with the cos^4 falloff; advanced.
