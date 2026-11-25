---
id: image/depth-of-field
title: "Depth of field"
description: "How Strata blurs what a lens would not hold in focus: the thin lens's circle of confusion, a five-pass gather, and a composite that stays steady under TAA."
kind: internals
size: L
tracks: [E]
needs: [image/taa, gpu/coordinates]
time: 85
learn:
  - id: coc-compute
    text: compute the circle of confusion of a point from a lens's focal length, f-number and focus distance
  - id: set-lens
    text: set a camera's depth-of-field fields for a shot and predict how wide its blur grows
  - id: gather-cover
    text: explain why each gathered sample counts only when its own circle reaches the pixel, and why the near field has its own pass
  - id: fade
    text: explain why the composite fades the blur in from in-focus depth and what that does under TAA
  - id: trace-lens
    text: trace which programs give the renderer a lens and when the depth of field runs
since: 0.7.0
status: final
---

Depth of field is the softness of everything that lies nearer or farther than the distance a camera is focused on. A real lens makes it without effort. A :term[renderer]{id=renderer} draws every point sharp, so it must invent the blur.

This page covers how Strata does that. Five compute passes read the finished image and the depth, and write an image with the blur that the later passes use. The page also covers the camera fields that set the lens, and the one rule that keeps the effect steady under temporal anti-aliasing. It does not cover the camera component as a whole, motion blur, the players' option that disables the effect, or the effect in a game's look; each has its own page.

## The problem and how engines solve it

Think of a portrait photograph. The face is sharp and the trees behind it are soft patches of color. The photographer did not blur the trees on purpose. A lens can bring light from only one distance to a perfectly sharp point on the sensor, and everything at other distances lands as a small disk.

A camera lens is a piece of glass that bends the light rays from each point of the scene so that they meet again on the sensor. The simplest model of it is the **thin lens**: a single flat plane that bends rays, described by three numbers. The focal length, in mm, is how far behind the lens a very distant point comes into focus. The f-number is the focal length divided by the width of the lens's opening, so f/2 means an opening half as wide as the focal length. The sensor height is the height of the light-catching area, in mm; 24 is a full-frame photographic sensor.

:::example[The far wall by hand]
Take a 50 mm lens at f/2 with the sensor set to show sharp what lies 2 m away. The opening is 50 / 2 = 25 mm wide. A wall so far away that its light arrives in parallel rays comes into focus 50 mm behind the lens. The sensor sits where a point at 2 m is sharp: its distance behind the lens is $50 \cdot 2000 / (2000 - 50)$ = 51.28 mm.

So the rays from the wall have already crossed and are spreading again when they hit the sensor, 1.28 mm past their meeting point. They filled 25 mm of lens and meet 50 mm behind it, so at 1.28 mm past the meeting point the beam is $25 \cdot 1.28 / 50$ = 0.64 mm wide. Each point of the wall is a disk 0.64 mm across.

On a sensor 24 mm tall shown as an image 1,000 pixels tall, that is $0.64 / 24 \cdot 1000$ = 26.7 pixels. A single bright point on the wall becomes a disk 27 pixels wide. A point exactly 2 m away stays a point.
:::

That disk has a name. The **circle of confusion** is the disk a single point of the scene makes on the sensor when it is out of focus, measured by its diameter. Its size is what the renderer needs, because blurring a pixel means spreading its light over a disk of that size.

The example's number was for a point at infinity. The general statement is this formula, which holds for any distance.

$$c = \frac{f^2}{N\,(z_f - f)} \cdot \frac{z - z_f}{z}$$

Here $c$ is the diameter of the disk on the sensor, and $f$ is the focal length. $N$ is the f-number, $z_f$ is the focus distance, and $z$ is the distance of the point, all in mm. The sign of $c$ is negative when $z$ is smaller than $z_f$, a point nearer than the focus. The first fraction depends on the lens and the focus only: it is the disk's size for a point at infinity, 0.64 mm in the example. The second fraction, between -∞ and 1, says how much of that size a point at distance $z$ gets.

Check the limits. At $z = z_f$ the second fraction is 0, so the point is sharp. As $z$ grows without end it tends to 1, so the disk reaches its largest far size. A pixel size follows from the sensor: $c / h \cdot r$ pixels, with $h$ the sensor height and $r$ the image height in pixels.

| Distance of the point | Second fraction | Disk, 50 mm at f/2, focus 2 m, 1,000 rows |
| --- | --- | --- |
| 1 m | -1 | -26.7 pixels |
| 1.5 m | -0.33 | -8.9 pixels |
| 2 m | 0 | 0 pixels |
| 3 m | 0.33 | 8.9 pixels |
| 4 m | 0.5 | 13.4 pixels |
| 10 m | 0.8 | 21.4 pixels |
| very far | 1 | 26.7 pixels |

The curve is uneven. Moving from 2 m to 1 m, a distance of 1 m, blurs by 26.7 pixels. Moving from 2 m to 4 m, which is 2 m, blurs by half as much, so near things blur faster than far things. Strata also limits the disk: no circle of confusion is wider than 2 % of the image height, which is 20 pixels at 1,000 rows. The table's 1 m, 10 m and far rows are cut there.

::figure{id=coc-curve}

A picture has two sides of the focus, and they behave differently. The **near field** is everything nearer than the focus distance, whose points have a negative circle of confusion.

The **far field** is everything farther than the focus distance, whose points have a positive one. A blurred near object is a soft cloud that spreads outward over the things behind it. A blurred far object only softens itself, and it may not reach over something in front.

Engines have four ways to make this on a screen. The first follows real rays: each pixel traces many rays through different points of the lens opening, or the scene is drawn many times from slightly moved cameras and the images averaged. The result is exact, and the cost is many renders or many rays per pixel, so games rarely do it.

The other three work on the finished image and the depth. Each pixel's circle of confusion is computed from its depth, and then the light is moved.

In the second way every pixel is drawn as a small disk of its own size, added onto the image. That is scatter: it is exact about where light goes, but it draws many large disks over each other and needs an order for them.

In the third way every pixel reads its neighbors and decides what it receives. That is gather, and each pixel's work is independent, so it fits a compute :term[shader]{id=shader}. In the fourth way the scene is split into layers by depth, each layer is blurred as a whole, and the layers are joined. It handles edges well, and it costs memory and a rule for the split.

Strata gathers, and adds the pieces that make gathering look right. Gathering has two classic faults.

The first fault is a halo. If a sharp foreground pixel is gathered into the blurred background next to it, a dark or bright fringe appears around the sharp subject. The second is flicker. Temporal anti-aliasing :term[jitters]{id=jitter} the camera, so the depth of the frame moves by up to half a pixel. A pixel on an in-focus silhouette then sees the subject in one frame and the distant background in the next, and its blur switches on and off.

## The map

Five compute passes run in a row, recorded by `SceneRenderer::RenderDepthOfField` into the frame's :term[command list]{id=command-list} on the :term[main thread]{id=main-thread} and run by the :term[graphics processing unit]{id=gpu} (GPU). They read the image that exists when they start, the resolved image of temporal anti-aliasing or the image in :term[high dynamic range]{id=high-dynamic-range} (HDR), and the frame's depth. They write a new image that the motion blur, the exposure and the :term[tone mapping]{id=tone-mapping-image} read in place of the old one.

```mermaid caption="The five passes. The first three work on half-resolution data, the gather writes two images, and the composite joins them with the sharp image at full resolution." alt="A flow with the color image and the depth entering the prepare pass. The prepare pass feeds the tiles pass, which feeds the widening pass, and both the prepare pass and the widening pass feed the gather pass. The gather pass and the color and depth images feed the composite pass, whose output goes to the later post effects."
flowchart LR
	C[color image] --> P[Prepare, half resolution]
	D[depth] --> P
	P --> T[Tiles]
	T --> L[Dilate]
	P --> G[Gather, two fields]
	L --> G
	G --> X[Composite, full resolution]
	C --> X
	D --> X
	X --> N[later post effects]
```

The passes live in `Strata/shaders/PostProcess/DepthOfField*.comp.slang` and share `Strata/shaders/Include/DepthOfField.slang`, which holds the parameters and the circle of confusion. `Strata/src/Strata/Renderer/SceneRendererPost.cpp` records them. `CameraLens` is in `Strata/src/Strata/Renderer/SceneRenderer.h`, and the camera's fields are in `CameraComponent` in `Strata/src/Strata/Scene/Components.h`.

## The contract

What a caller may assume, and what a caller must do, each with its reason.

- A program gives the renderer a lens through `SceneRenderOptions::Lens`; no lens means no depth of field. The reason: the renderer knows nothing of cameras in a scene, and the program that picks the camera also decides what is seen through it.
- The effect runs only for a perspective view, and only when the players' `DepthOfField` row is not Off. Orthographic views have no focal length, and a player may find blur uncomfortable, so the row always wins.
- What is in focus stays exactly as without the effect: a pixel with a circle under one pixel across keeps the sharp image bit for bit. Only the blur of a nearer object may spread over it. The reason is trust: turning the lens on must not soften the subject.
- No circle is wider than 2 % of the image height (`c_DepthOfFieldMaxDiameter`). The reason is cost and look: the gather has a fixed number of samples, so a wider disk would show gaps.
- Pixels the effect changed carry alpha 1 in its output, and the tone mapping does not sharpen them. The reason is that sharpening a blur brings its edges back; the mask is the same one that motion blur writes, taught on the [motion blur page](../image/motion-blur.md).
- The effect reads the resolved image of temporal anti-aliasing, which has no jitter in its color, and the depth of the frame, which has. The composite's rules exist because of that gap.

:::rule[Post effects sit between the resolve and the tone mapping]
The engine's guide says a post effect runs in the post-processing :term[source file]{id=source-file}, after temporal anti-aliasing (:term[TAA]{id=taa}) resolves and before the tone mapping, and adds nothing to the frame's shared constants. The reason is that the blur must work on light, before the curve that turns light into display values, and the shared constants must not grow with each effect. The depth of field takes its parameters as :term[push constants]{id=push-constants} of its own. Its lens comes in through the render options, not through a post-process component. The order of the chain is on the [post-processing page](../image/why-post.md).
:::

## A toy version

Before the real passes, a toy in one dimension. A row of 32 pixels holds a white wall far behind the focus, with a radius of 4 pixels, one dark stripe in the wall, and a black card in focus. The toy gathers each pixel over its own circle in two ways: every neighbor counts, or a neighbor counts only when its own circle reaches back to the pixel. Look at the pixels beside the card.

```cpp sketch="image-depth-of-field-toy.cpp"
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <string>
#include <vector>

namespace
{

	constexpr int c_Width = 32;

	// One pixel of a row: its color (0 is black, 1 is white) and the radius of its circle of confusion, in pixels.
	struct Pixel
	{
		float Color;
		float Radius;
	};

	// A white wall far behind the focus (radius 4) with a thin black stripe, and a black card in focus (radius 0) in front of it.
	std::vector<Pixel> MakeRow()
	{
		std::vector<Pixel> row(c_Width, Pixel{ 1.0f, 4.0f });
		for (int x = 12; x < 16; x++)
			row[x] = Pixel{ 0.0f, 0.0f };
		row[26].Color = 0.0f;
		return row;
	}

	// How much a sample whose circle has `radius` covers a pixel `distance` away: all of it inside, fading over the last pixel.
	float Cover(float radius, float distance)
	{
		return std::clamp(radius - distance + 1.0f, 0.0f, 1.0f);
	}

	// Each pixel gathers its neighbors within its own circle. With `useCover` a neighbor counts only when its own circle reaches back.
	std::vector<float> Gather(const std::vector<Pixel>& row, bool useCover)
	{
		std::vector<float> result(row.size());
		for (int x = 0; x < c_Width; x++)
		{
			const int reach = static_cast<int>(std::ceil(row[x].Radius));
			float sum = row[x].Color;
			float total = 1.0f;
			for (int offset = -reach; offset <= reach; offset++)
			{
				if (offset == 0 || std::abs(offset) > row[x].Radius)
					continue;
				const Pixel& sample = row[std::clamp(x + offset, 0, c_Width - 1)];
				const float weight = useCover ? Cover(sample.Radius, static_cast<float>(std::abs(offset))) : 1.0f;
				sum += sample.Color * weight;
				total += weight;
			}
			result[x] = sum / total;
		}
		return result;
	}

	// One digit per pixel: 0 is black, 9 is white.
	std::string Digits(const std::vector<float>& values)
	{
		std::string text;
		for (float value : values)
			text += static_cast<char>('0' + std::lround(value * 9.0f));
		return text;
	}

}

int main()
{
	const std::vector<Pixel> row = MakeRow();
	std::vector<float> sharp;
	for (const Pixel& pixel : row)
		sharp.push_back(pixel.Color);
	std::printf("sharp      %s\n", Digits(sharp).c_str());
	std::printf("no cover   %s\n", Digits(Gather(row, false)).c_str());
	std::printf("with cover %s\n", Digits(Gather(row, true)).c_str());
	return 0;
}
```

```text output-of="image-depth-of-field-toy.cpp"
sharp      99999999999900009999999999099999
no cover   99999999876500005678998888888889
with cover 99999999999900009999998888888889
```

1. **Line 25:** the stripe is part of the wall, so it shows that the wall's pixels still blur one another.
2. **Line 30:** `Cover` is 1 inside a neighbor's circle and falls to 0 over its last pixel.
3. **Line 49:** with `useCover` a neighbor weighs its cover; without it, every neighbor weighs 1.

The first row is the input, one digit per pixel: 9 is white and 0 is black. In the second row, with no cover rule, the white pixels beside the card take in the dark card and darken: 8, 7, 6, 5. That is the halo, a dark fringe on the blurred side of a sharp object. In the third row, the card's own radius is 0, so its cover of a pixel one step away is 0, and the white wall beside it stays white. The thin stripe in the wall is blurred in both rows to the same gray, because the wall's samples cover one another.

## The real code

The real passes follow the toy's idea and add what a picture needs. A lens comes from a camera, and depth becomes a circle of confusion. The gather runs at half resolution, the near field has its own image, and a composite keeps the focus plane sharp.

### The lens

A program asks for a lens with `CameraLens::FromEntity`. It returns a lens for an entity with a `CameraComponent` whose `DepthOfField` field is on and whose projection is perspective, and nothing otherwise. The camera has five fields for the effect: `DepthOfField` (off by default), `FocusDistance` (10 m), `FocusEntity` (none), `Aperture` (2.8, the f-number) and `SensorHeight` (24 mm). The next quote reads and clamps them, so a bad value in a file cannot make a lens that breaks the passes.

```cpp src="Strata/src/Strata/Renderer/SceneRendererPost.cpp#L261-L267" from="auto finiteOr" to="lens.FocusDistance = std::clamp(finiteOr(component.FocusDistance, 10.0f), 0.1f, 10000.0f);" symbol="CameraLens::FromEntity"
auto finiteOr = [](float value, float fallback) { return std::isfinite(value) ? value : fallback; };
CameraLens lens;
lens.SensorHeight = std::clamp(finiteOr(component.SensorHeight, 24.0f), 4.0f, 100.0f);
lens.FNumber = std::clamp(finiteOr(component.Aperture, 2.8f), 1.0f, 32.0f);
const float fieldOfView = glm::radians(std::clamp(finiteOr(component.PerspectiveFOV, 60.0f), 1.0f, 179.0f));
lens.FocalLength = 0.5f * lens.SensorHeight / std::tan(0.5f * fieldOfView);
lens.FocusDistance = std::clamp(finiteOr(component.FocusDistance, 10.0f), 0.1f, 10000.0f);
```

The :term[field of view]{id=field-of-view} needs no lens field of its own, since the camera already has one. The focal length follows from it and the sensor: half the sensor's height over the tangent of half the field of view. For the Third-Person sample's camera, with a 60 degree field of view and the default sensor, that is $12 / \tan 30°$ = 20.78 mm. A narrow view means a long lens, and a long lens blurs more: at 20 degrees the same sensor gives 68 mm.

When `FocusEntity` names an entity of the scene, the focus distance is measured to that entity along the camera's forward axis, not in a straight line. An entity off to one side is therefore in focus at the same depth as one straight ahead, as the focus plane of a real lens is a plane. The distance is at least the :term[near plane]{id=near-plane}. The position used is the drawn one of this frame, so a moving subject stays in focus.

The circle of confusion in pixels is the formula of the first section, in two functions.

```cpp src="Strata/src/Strata/Renderer/SceneRendererPost.cpp#L287-L292" symbol="CameraLens::GetCircleOfConfusionScale"
float CameraLens::GetCircleOfConfusionScale(float height) const
{
	// f^2 / (N (zf - f)) on the sensor, in millimeters, then in pixels of the image the sensor's height spans.
	const float focus = GetFocusMillimeters(*this);
	return FocalLength * FocalLength / (FNumber * (focus - FocalLength)) / SensorHeight * height;
}
```

The function returns the first fraction of the formula, converted to pixels: mm on the sensor over the sensor's height, times the image's rows. A helper, `GetFocusMillimeters`, holds the focus at 1.1 focal lengths at the nearest. Closer than that the formula would turn infinite, since the lens would have to be at its own focal length from the sensor.

Three numbers show how little a wide view blurs. The Third-Person camera at f/2.8 focused 10 m away gives a disk 0.7 pixels wide at infinity for a 1,080-row image, so a wide view blurs the far background hardly at all. At f/1.4 the same disk is 1.4 pixels, at f/8 it is 0.24. A long lens or a close focus makes the large blurs of photographs.

::figure{id=dof-pair variant=off}

::figure{id=dof-pair variant=on}

::figure{id=dof-pair variant=off crop=far}

::figure{id=dof-pair variant=on crop=far}

::figure{id=aperture-sweep variant=f14}

::figure{id=aperture-sweep variant=f8}

::figure{id=focus-entity}

### Parameters

`RenderDepthOfField` turns the lens into the numbers the shaders need and dispatches the five passes.

```cpp src="Strata/src/Strata/Renderer/SceneRendererPost.cpp#L829-L835" from="RenderData::DepthOfFieldParameters parameters = {};" to="parameters.SampleCount = RenderData::c_DepthOfFieldSamples;" symbol="SceneRenderer::RenderDepthOfField"
RenderData::DepthOfFieldParameters parameters = {};
parameters.FocusDistance = GetFocusMillimeters(lens) * 0.001f;
// The passes work with radii: half the circle of confusion's diameter.
parameters.CoCScale = 0.5f * lens.GetCircleOfConfusionScale(rows);
parameters.MaxCoC = 0.5f * RenderData::c_DepthOfFieldMaxDiameter * rows;
parameters.TileSize = std::max(RenderData::c_DepthOfFieldMinTileSize, static_cast<uint32_t>(std::ceil(parameters.MaxCoC * 0.5f)));
parameters.SampleCount = RenderData::c_DepthOfFieldSamples;
```

The shaders work with radii, so the scale is halved, and the largest radius is half of 2 % of the rows. At 1,080 rows that is 10.8 pixels. The tile size is the larger of 8 and the largest radius in half-resolution pixels, rounded up: 8 at 1,080 rows, 11 at 2,160. A tile is therefore always at least as wide as the largest blur, which the `Dilate` pass relies on.

### Prepare

The first pass makes the half-resolution image, so that the three passes that follow read a quarter as many pixels. Each half-resolution pixel gets the mean color of its 2 by 2 block in the full image. It also gets, in alpha, a circle of confusion in half-resolution pixels. Where one of the four pixels is in the near field with a radius over one pixel, the nearest one's value is kept; otherwise the farthest one's is. The reason: a near silhouette must keep its blur, even if only one pixel of the block is near.

The circle comes from the depth. The depth is turned back into a distance with the inverse projection, the matrix that undoes the camera's projection, which the [coordinates page](../gpu/coordinates.md) covers. The distance gives the second fraction of the formula, and the pass multiplies it by the scale.

```slang src="Strata/shaders/Include/DepthOfField.slang#L25-L36"
// The signed circle of confusion, in full-resolution pixels, of what a pixel shows: negative in front of the focus, the sky
// (nothing drawn, infinitely far) the largest behind it; clamped to MaxCoC either way.
float GetCircleOfConfusion(float2 uv, float depth)
{
	float coc = u_DepthOfField.CoCScale;
	if (depth > 0.0)
	{
		float4 point = mul(u_Frame.InverseProjection, float4(UVToNDC(uv), depth, 1.0));
		float distance = max(-point.z / point.w, 1e-4);
		coc = u_DepthOfField.CoCScale * (1.0 - u_DepthOfField.FocusDistance / distance);
	}
	return clamp(coc, -u_DepthOfField.MaxCoC, u_DepthOfField.MaxCoC);
```

1. **Line 29:** the sky has no depth drawn, so it starts at the largest far circle, the scale itself.
2. **Lines 32–33:** the inverse projection turns the depth back into a distance in meters.
3. **Line 34:** the second fraction of the formula, with the focus distance over the distance.
4. **Line 36:** the circle is clamped both ways to the 2 % limit.

The sky has no depth drawn, so its circle is the largest far one, the scale itself. The last line clamps both ways to the 2 % limit. The function is shared by the prepare and composite passes, so both agree on a pixel's circle to the last bit.

```slang src="Strata/shaders/PostProcess/DepthOfFieldPrepare.comp.slang#L23-L32"
for (int index = 0; index < 4; index++)
{
	int2 pixel = min(2 * texel + int2(index & 1, index >> 1), size - 1);
	color += u_Color.Load(int3(pixel, 0)).rgb;
	float coc = GetCircleOfConfusion((float2(pixel) + 0.5) * u_Frame.ViewportSize.zw, u_Depth.Load(int3(pixel, 0)).r);
	nearest = min(nearest, coc);
	farthest = max(farthest, coc);
}
float coc = nearest < -2.0 * c_DepthOfFieldInFocus ? nearest : farthest;
o_Half[texel] = float4(color * 0.25, 0.5 * coc);
```

1. **Lines 26–27:** each of the four full-resolution pixels adds its color and finds its own circle.
2. **Lines 28–29:** the pass tracks the nearest circle, the most negative one, and the farthest.
3. **Line 31:** a near radius over one pixel wins, so a near silhouette keeps its blur; otherwise the farthest counts.
4. **Line 32:** the mean color goes out, and half the circle, a radius in half-resolution pixels, goes in alpha.

### Tiles and the widening of tiles

The near field's gather must reach far enough. A near pixel's light can land on a pixel whose own depth is far, and that pixel needs to know that a large near blur lies close by. The tiles pass finds, for each tile of the half-resolution image, the largest near and the largest far radius in it. One group of 64 threads handles one tile and reduces its values through group-shared memory, each step halving the active threads behind a barrier, the pattern of the [compute page](../gpu/compute.md).

The `Dilate` pass then takes, for each tile, the largest value of the nine tiles around it. A tile is at least as wide as the largest blur, so a near pixel's blur can reach only into the next tile. The nine tiles therefore hold every near pixel that can touch this one.

### Gather

The gather pass is the heart. It runs at half resolution and writes two images: the pixel's own field and the near field.

The pass uses **scatter-as-gather**: the way of doing a scatter, in which each pixel spreads its light over a disk, by having each pixel read the neighbors whose disks cover it. A neighbor's light is wanted by this pixel only if the neighbor's circle of confusion is large enough to reach it. That condition is the cover the toy used: a weight that is 1 inside the neighbor's circle and falls to 0 over the circle's last pixel.

The samples lie on a :term[Vogel disk]{id=vogel-disk}: forty-eight points whose radius grows as the square root of the index and whose angle advances by the golden angle, 2.4 :term[radians]{id=radian}, from one sample to the next. The [probability page](../basics/math-probability.md) explains why that spreads points evenly. Each pixel turns its pattern by a fixed angle from a :term[hash]{id=hash} of its position. Neighbors then use different patterns, no pattern repeats on screen, and nothing changes from frame to frame.

```slang src="Strata/shaders/PostProcess/DepthOfFieldGather.comp.slang#L27-L32"
float2 VogelSample(uint index, uint count, float rotation)
{
	float radius = sqrt((float(index) + 0.5) / float(count));
	float angle = float(index) * c_GoldenAngle + rotation;
	return radius * float2(cos(angle), sin(angle));
}
```

For sample 0 of 48 the radius is $\sqrt{0.5/48}$ = 0.10, and for sample 47 it is $\sqrt{47.5/48}$ = 0.99, so the samples fill the disk with equal area per sample. At the largest radius of 10.8 pixels, which is 5.4 half-resolution pixels, the disk holds about 92 half-resolution pixels, so the 48 samples visit about half of them.

The pixel's own field comes first. A pixel whose circle is at least half a half-resolution pixel is blurred. It takes the weighted mean of its samples, and a sample counts only when it is on the same side of the focus as the pixel and its own circle covers the pixel. This is the toy's cover rule, and it keeps a sharp foreground from bleeding into the background.

A near pixel is a special case. It keeps what lies behind it: the mean of the samples that are farther than it by more than a pixel. A near object that the blur covers only in part must show the scene through its edge. Deep inside a near object nothing farther is in reach, and the pixel keeps its own blur.

```slang src="Strata/shaders/PostProcess/DepthOfFieldGather.comp.slang#L55-L84"
float rotation = PixelRandom(uint2(texel), 7u) * TWO_PI;

float3 own = center.rgb;
float ownRadius = abs(centerCoC);
if (ownRadius >= c_DepthOfFieldInFocus)
{
	float3 sum = center.rgb;
	float total = 1.0;
	float3 behind = float3(0.0);
	float behindCount = 0.0;
	for (uint index = 0u; index < count; index++)
	{
		float2 offset = VogelSample(index, count, rotation) * ownRadius;
		float4 sampled = FetchHalf(texel, offset, size);
		float distance = length(offset);
		bool sampleNear = sampled.a < -c_DepthOfFieldInFocus;
		if (centerNear && sampled.a > centerCoC + 1.0)
		{
			behind += sampled.rgb;
			behindCount += 1.0;
		}
		if (sampleNear == centerNear)
		{
			float weight = Cover(abs(sampled.a), distance);
			sum += sampled.rgb * weight;
			total += weight;
		}
	}
	own = behindCount > 0.0 ? behind / behindCount : sum / total;
}
```

1. **Line 55:** the angle that turns the pattern comes from the pixel's position only, so nothing varies with time.
2. **Line 59:** only a pixel whose circle is at least half a half-resolution pixel is blurred.
3. **Lines 67–68:** a sample lies on the Vogel disk, scaled by the pixel's own radius.
4. **Lines 71–75:** a near pixel collects the samples that are farther than it, to keep what lies behind.
5. **Lines 76–81:** a sample on the same side of the focus counts, weighed by its cover.

The near field is the second image. Near objects spread over what is behind them, which a pixel cannot learn from its own samples alone. So each pixel looks at the widened tile's largest near radius, and gathers over that radius the samples that are in the near field and at least as near as itself. Each weight is the cover times a share: the area of the disk of the largest radius over the area of the sample's own disk, between 1 and 16. A small near disk gives more of its light to each pixel, because it concentrates the same light into less area.

```slang src="Strata/shaders/PostProcess/DepthOfFieldGather.comp.slang#L86-L108"
float4 near = float4(0.0);
float nearRadius = u_Dilated.Load(int3(texel / int(u_DepthOfField.TileSize), 0)).x;
if (nearRadius >= c_DepthOfFieldInFocus)
{
	float3 sum = float3(0.0);
	float total = 0.0;
	float nearestAllowed = centerNear ? centerCoC + 0.5 : -c_DepthOfFieldInFocus;
	for (uint index = 0u; index < count; index++)
	{
		float2 offset = VogelSample(index, count, rotation) * nearRadius;
		float4 sampled = FetchHalf(texel, offset, size);
		if (sampled.a >= -c_DepthOfFieldInFocus || sampled.a > nearestAllowed)
			continue;
		float share = clamp(nearRadius * nearRadius / (sampled.a * sampled.a), 1.0, c_MaxNearShare);
		float weight = Cover(-sampled.a, length(offset)) * share;
		sum += sampled.rgb * weight;
		total += weight;
	}
	float coverage = clamp(total / float(count), 0.0, 1.0);
	if (total > 0.0)
		near = float4(sum / total * coverage, coverage);
}
o_Near[texel] = near;
```

1. **Line 87:** the radius comes from the widened tile of this pixel, the largest near radius around it.
2. **Lines 97–98:** only near samples at least as near as the pixel count.
3. **Lines 99–100:** the share, between 1 and 16, multiplies the cover to give the weight.
4. **Lines 104–106:** the coverage is the total weight over the sample count, at most 1, and the color is multiplied by it.

The result is premultiplied: the color is multiplied by the coverage, a number from 0 to 1 that says how much of the pixel the near field holds, and the coverage goes in alpha. A blurred foreground then covers half of the edge of what lies behind it and all of its own inside. The composite blends with one multiply and one add, and the premultiplied form stays correct when the near image is read between texels with a bilinear sample.

### Composite

The last pass works at full resolution and joins three things: the sharp image, the gathered own field, and the near field. It also holds the page's most delicate rule.

The depth that decides a pixel's circle is this frame's, jittered by up to half a pixel by temporal anti-aliasing. The color is the resolved image, without jitter. Take a pixel right outside an in-focus silhouette. In one frame the jitter makes its depth the subject's, so it keeps the sharp resolved color; in the next frame its depth is the background's, so it takes the blurred background. The pixel switches between two very different images every frame: that is the flicker of the problem section.

The fix is to fade the blur in with the distance from in-focus depth. A pixel within one pixel of something in focus gets none of the blur, whatever the jitter shows. The blur is half strength two pixels from focus, and full strength from three. A pixel next to the subject's edge always finds the subject in its neighborhood, so it never switches. A pixel two or three away may still switch with the jitter, but between two images of the background only, and by half as much.

:::example[The fade by hand]
A pixel's own circle radius is 6 pixels, so its blur weight before the fade is $\mathrm{smoothstep}(0.5, 1, 6)$, which is 1. That curve is 0 up to a radius of 0.5 and 1 from a radius of 1. The nearest in-focus pixel is two pixels away. The fade is $(2 - 1) / 2$ = 0.5, so the pixel shows half its sharp color and half the own field: $0.5 \cdot \text{sharp} + 0.5 \cdot \text{blurred}$. Three or more pixels away the fade is 1, and one pixel away it is 0.
:::

The pass finds the distance to the nearest in-focus pixel with group-shared memory. Each group of 8 by 8 threads first fills a table of 12 by 12 flags, its tile plus two pixels of margin each way, one flag per pixel that is in focus. A barrier makes the table complete. Then each thread scans the 5 by 5 pixels around itself in the table.

```slang src="Strata/shaders/PostProcess/DepthOfFieldComposite.comp.slang#L36-L45"
void st_Main()
{
	int2 size = TextureSize(u_Color, 0);
	int2 origin = int2(st_WorkGroupID.xy) * 8 - c_FocusReach;
	for (uint index = st_LocalInvocationIndex; index < uint(c_FocusTile * c_FocusTile); index += 64u)
	{
		int2 offset = int2(int(index) % c_FocusTile, int(index) / c_FocusTile);
		s_InFocus[index] = GetRadius(origin + offset, size) < 0.5 ? 1u : 0u;
	}
	GroupMemoryBarrierWithGroupSync();
```

1. **Lines 40–44:** 64 threads fill the table's 144 entries in strides, since the table is 12 by 12.
2. **Line 43:** an entry is 1 when the pixel's circle has a radius under half a pixel.
3. **Line 45:** the barrier makes the table complete before any thread reads it.

Each thread of the group fills several entries of the table in a loop, since 144 entries are more than 64 threads. The comparison with 0.5 is the radius, in pixels, under which a pixel counts as in focus; the reason it is a radius is that the passes work with radii.

```slang src="Strata/shaders/PostProcess/DepthOfFieldComposite.comp.slang#L47-L81"
int2 pixel = int2(st_GlobalInvocationID.xy);
if (any((pixel >= size)))
	return;
float3 color = u_Color.Load(int3(pixel, 0)).rgb;
float2 uv = (float2(pixel) + 0.5) * u_Frame.ViewportSize.zw;
float radius = abs(GetCircleOfConfusion(uv, u_Depth.Load(int3(pixel, 0)).r));
float changed = 0.0;
float blend = smoothstep(0.5, 1.0, radius);
if (blend > 0.0)
{
	// The distance (the larger of x and y) to the nearest in-focus pixel within reach; beyond it, c_FocusReach + 1.
	int focusDistance = c_FocusReach + 1;
	int2 local = int2(st_LocalInvocationID.xy) + c_FocusReach;
	for (int y = -c_FocusReach; y <= c_FocusReach; y++)
	{
		for (int x = -c_FocusReach; x <= c_FocusReach; x++)
		{
			if (s_InFocus[(local.y + y) * c_FocusTile + local.x + x] != 0u)
				focusDistance = min(focusDistance, max(abs(x), abs(y)));
		}
	}
	blend *= clamp(float(focusDistance - 1) / float(c_FocusReach), 0.0, 1.0);
}
if (blend > 0.0)
{
	color = lerp(color, u_Own.SampleLevel(u_LinearClampSampler, uv, 0.0).rgb, blend);
	changed = 1.0;
}
float4 near = u_Near.SampleLevel(u_LinearClampSampler, uv, 0.0);
if (near.a > 0.0)
{
	color = color * (1.0 - near.a) + near.rgb;
	changed = 1.0;
}
o_Composite[pixel] = float4(min(color, float3(c_MaxHDRValue)), changed);
```

1. **Line 54:** the blend starts at a radius of 0.5 and is full at 1.
2. **Lines 58–67:** the scan finds the nearest in-focus pixel in the 5 by 5 around this one.
3. **Line 68:** the fade is 0 at a distance of 1, one half at 2 and 1 from 3.
4. **Lines 72–73:** the own field is blended in, and the pixel is marked as changed.
5. **Lines 75–80:** the near field goes over everything, scaled by what it leaves uncovered.

The :term[smoothstep]{id=smoothstep} makes the blur start at a radius of half a pixel and finish at one pixel, so a pixel whose circle is under a pixel across keeps the sharp image exactly. The scan finds the distance of the nearest in-focus pixel, `focusDistance`, as the larger of the x and y offsets, and the blend is multiplied by the fade. Where the blend is above 0 the pixel takes the blurred own field, read with a bilinear sample because that image has half the pixels. The near field then goes over everything: the color is scaled by what the near field leaves uncovered, and the near color is added. The alpha written is 1 wherever either step changed the pixel, which is the mask that stops the tone mapping's sharpening.

### Where it runs

`RenderFrame` decides whether the passes run at all, in one condition.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L3798-L3805"
if (options.Lens && !camera.Orthographic && m_Specification.Quality.DepthOfField != SceneEffectChoice::Off)
{
	gpuTimer.Next(gpuStages.DepthOfField);
	commandList->beginMarker("DepthOfField");
	if (RenderDepthOfField(commandList, *options.Lens, postSource))
		postSource = PostSource::DepthOfField;
	else
		degraded = true;
```

The effect needs a lens, a perspective camera and a players' row that is not Off. The GPU timer marks the pass with its own stage. When the passes cannot make their resources, they report the failure, the frame is marked degraded, and the picture draws without depth of field.

Two programs give the renderer a lens. The :term[runtime's]{id=runtime} game renderer calls `CameraLens::FromEntity` for the :term[primary camera]{id=primary-camera} each frame. The editor's viewport code does the same in `StrataEditor/src/Editor/ViewportRenderer.cpp` when a view comes from the scene's camera. A view through the editor's own camera has no lens, so it is never blurred.

Depth of field belongs to the lens, not to the moment: every view or capture through a scene camera shows it, whether the game plays or not. Motion blur shows only in live views of a playing game.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Rays through the lens, or many renders of the scene | Film and animation renderers, as in the lens chapter of Physically Based Rendering | Exact blur, with correct hidden surfaces | Many times the frame's cost |
| Scatter: draw each bright pixel as a disk | Production engines, as in the second talk under Further reading | Blur shaped like the lens opening | Many large disks drawn over each other, and an order for them |
| Layers split by depth, each blurred whole | A technique of the literature; Strata does not use it | Good edges between layers | Memory for the layers, and a rule for what each holds |
| A gather at full resolution | Strata, but only at the focus plane, in the composite | A sharper blur everywhere | About four times the gather's work |

## How it is tested

Two suites cover the effect. `Renderer.CameraLens` is a unit suite with no GPU. Its cases check that a camera's lens follows its component, and that the circle of confusion is the formula's. For a 50 mm lens at f/2 focused 2 m away on 1,000 rows they check 26.7 pixels at infinity, half of that at 4 m, and 0 at 2 m. They also check a finite positive value when the focus is closer than the lens can reach.

`GPU.SceneRenderer.DepthOfField` renders scenes on a real device, in the exact test configuration. Its cases include these.

- The focus plane renders bit-identically to depth of field off: a wall in focus gives an image with a maximum difference of 0 against the same render without the lens.
- An edge out of focus blurs over its circle of confusion, a near card's blur spreads over the wall in focus, and blurred pixels are not sharpened.
- Under TAA an in-focus silhouette over a far, out-of-focus wall flickers no more than without the lens. The case renders 16 frames after the history settled and allows a change of 6 codes above the lens-free largest.

Run them with `build/windows/bin/Debug/StrataTests.exe --test-suite=Renderer.CameraLens` and, on a machine with a GPU, `--test-suite=GPU.SceneRenderer.DepthOfField`.

## Changing it safely

The places to extend are the lens, the passes and the parameters. A new lens property starts in `CameraComponent` and `CameraLens::FromEntity`, with a clamp for every value. The function clamps the sensor height, the f-number, the field of view and the focus, so a broken scene file cannot make a lens that divides by zero.

Keep three rules in mind.

- Both sides of the circle of confusion stay one function. The prepare and composite passes both call `GetCircleOfConfusion` from `Include/DepthOfField.slang`; if one gets its own formula, the focus plane stops being bit-identical.
- Anything new that reads this frame's depth beside the jittered color needs the composite's fade. A pass that decides by depth what to do to a pixel flickers at silhouettes under TAA without it.
- A new pass is wrapped in a :term[GPU stage]{id=gpu-stage-strata} registered with its module, and its resources are released when the players' row disables the effect, as the test about quality rows checks.

Before a change is done, run `Renderer.CameraLens` and the `GPU.SceneRenderer.DepthOfField` suite.

## Summary

- The circle of confusion of a point is the first fraction of the formula, set by the lens and the focus, times the second fraction, $(z - z_f) / z$, in pixels of the image.
- The camera's `DepthOfField`, `FocusDistance`, `FocusEntity`, `Aperture` and `SensorHeight` fields become a lens through `CameraLens::FromEntity`, which derives the focal length from the field of view and clamps every value.
- Each gathered sample counts only when its own circle covers the pixel, which stops the halo, and the near field has its own premultiplied image, reached through widened tiles.
- The composite keeps the sharp image within a pixel of focus and fades the blur in over the next two pixels, so the jitter of temporal anti-aliasing cannot make in-focus silhouettes flicker.
- Programs give the renderer a lens, the effect runs only for perspective views and when the players' row allows it, and the editor's own camera never shows it.

## Check yourself

1. A camera has a 60 degree field of view and a 36 mm sensor. What focal length does `CameraLens::FromEntity` compute: 20.8, 31.2, 62.4 or 36 mm?

   :::answer{tests="set-lens"}
   31.2 mm. Half the sensor, 18 mm, over the tangent of 30 degrees, 0.577, gives 31.2. The 20.8 mm answer uses the default 24 mm sensor instead of the 36 mm one. The 62.4 mm answer forgets the half, and 36 mm confuses the focal length with the sensor.
   :::

2. In the composite, a pixel two pixels from in-focus depth has a blur weight of 1 before the fade. What does it show: all blur, half blur, no blur, and why?

   :::answer{tests="fade"}
   Half blur. The fade is $(2 - 1) / 2$ = 0.5. The fade exists so that a pixel beside an in-focus silhouette does not switch between sharp and blurred as the jitter moves the depth. Full blur would flicker at two pixels, and no blur would be right only within one pixel.
   :::

3. In the toy, the card's circle has a radius of 0. A white pixel beside it gathers a sample from the card. How much does that sample weigh with the cover rule, and what happens to the pixel's color?

   :::answer{tests="gather-cover"}
   `Cover(0, 1)` is $\mathrm{clamp}(0 - 1 + 1, 0, 1)$ = 0, so the sample weighs nothing and the pixel stays white. Without the rule the card's black would count in full and give the halo of the second row.
   :::

4. The editor's Scene view shows the scene through the editor's own camera, with a scene camera that has `DepthOfField` on. Is the picture blurred by the lens, and where is that decided?

   :::answer{tests="trace-lens"}
   No. `ResolveViewportView` sets a lens only when the view comes from the scene's camera; the editor camera gives none, and `RenderFrame` needs `options.Lens` to run the passes.
   :::

5. With the lens of the first table (50 mm, f/2, focus 2 m) on 1,000 rows, what is the circle of confusion of a point at 1 m, and what does the renderer use?

   :::answer{tests="coc-compute"}
   The formula gives -26.7 pixels: the sign is negative because the point is nearer than the focus. The renderer clamps it to -20 pixels, which is 2 % of the 1,000 rows.
   :::

## Exercises

1. **Basic.** An 85 mm lens at f/1.8 on a 24 mm sensor is focused 3 m away. On 1,080 rows, what is the circle of confusion of a wall 12 m away, before and after the 2 % limit?

   :::answer[Worked solution]{tests="coc-compute"}
   The first fraction is $85^2 / (1.8 \cdot (3000 - 85))$ = 7225 / 5247 = 1.377 mm. The second is $(12000 - 3000) / 12000$ = 0.75, so the disk on the sensor is 1.033 mm. In pixels that is $1.033 / 24 \cdot 1080$ = 46.5. The limit is $0.02 \cdot 1080$ = 21.6 pixels, so the renderer uses 21.6.
   :::

2. **Medium.** Write a program that prints the circle of confusion, in pixels, with the 2 % limit. Use points at 1, 2, 3, 6, 12 and 100 m, and a 50 mm lens at f/4 focused 3 m away on 1,080 rows.

   :::answer[Worked solution]{tests="coc-compute" solution="sketches/image-depth-of-field-coc-table.cpp"}
   The program keeps the engine's steps: the focus distance in mm is held at 1.1 focal lengths at the least, the scale is the first fraction, and the result is clamped to the limit. In the output no line is clamped, because the lens at f/4 is gentle; try f/1.4 and the far lines hit 21.6.

   ```cpp sketch="image-depth-of-field-coc-table.cpp"
   #include <algorithm>
   #include <cstdio>
   #include <initializer_list>

   namespace
   {

   	struct Lens
   	{
   		float FocalLength;   // Millimeters
   		float FNumber;
   		float SensorHeight;  // Millimeters
   		float FocusDistance; // Meters
   	};

   	// The signed diameter of the circle of confusion, in pixels, of a point `distance` meters away; negative in front of the focus.
   	float GetCircleOfConfusion(const Lens& lens, float distance, float rows)
   	{
   		const float focus = std::max(lens.FocusDistance * 1000.0f, 1.1f * lens.FocalLength);
   		const float scale = lens.FocalLength * lens.FocalLength / (lens.FNumber * (focus - lens.FocalLength));
   		const float millimeters = distance * 1000.0f;
   		const float onSensor = scale * (millimeters - focus) / millimeters;
   		const float pixels = onSensor / lens.SensorHeight * rows;
   		const float limit = 0.02f * rows;
   		return std::clamp(pixels, -limit, limit);
   	}

   }

   int main()
   {
   	const Lens lens = { 50.0f, 4.0f, 24.0f, 3.0f };
   	for (float distance : { 1.0f, 2.0f, 3.0f, 6.0f, 12.0f, 100.0f })
   		std::printf("%6.1f m: %6.1f pixels\n", distance, GetCircleOfConfusion(lens, distance, 1080.0f));
   	return 0;
   }
   ```

   ```text output-of="image-depth-of-field-coc-table.cpp"
      1.0 m:  -19.1 pixels
      2.0 m:   -4.8 pixels
      3.0 m:    0.0 pixels
      6.0 m:    4.8 pixels
     12.0 m:    7.2 pixels
    100.0 m:    9.2 pixels
   ```

   1. **Line 19:** the focus distance is held at 1.1 focal lengths at least, as the engine holds it.
   2. **Lines 20–22:** the scale is the first fraction, and the second fraction turns it into the point's disk.
   3. **Lines 23–25:** the disk becomes pixels, and the 2 % limit clamps it both ways.
   :::

3. **Medium.** A racing game's camera has a 30 degree field of view and follows the car. You want f/2.8 with the focus held on the car, 8 m away. Which fields do you set, and how wide is the blur of a tree at 100 m, on 1,080 rows? Which row of the players' settings removes this blur, and does it remove the motion blur too?

   :::answer[Worked solution]{tests="set-lens,coc-compute"}
   Set `DepthOfField` on, `Aperture` to 2.8 and `FocusEntity` to the car. The focal length is $12 / \tan 15°$ = 44.8 mm. The first fraction is $44.8^2 / (2.8 \cdot (8000 - 44.8))$ = 0.090 mm, the second is $(100 - 8) / 100$ = 0.92, and the disk is 0.083 mm, which is 3.7 pixels. The players' `DepthOfField` row set to Off removes it; the motion blur has its own row and stays.
   :::

4. **Hard.** Trace it yourself. With a search for `Lens =` in the engine and the editor, find every program that gives the renderer a lens, and the conditions under which `RenderFrame` runs the depth of field. Say why a Scene view through the editor camera is never blurred by the lens.

   :::answer[Worked solution]{tests="trace-lens"}
   The search finds `Strata/src/Strata/Runtime/GameRenderer.cpp`, where the runtime sets `options.Lens` from the primary camera, and `StrataEditor/src/Editor/ViewportRenderer.cpp`, where `ResolveViewportView` sets `view.Lens` for a scene camera and `options.Lens = view.Lens` passes it on. `SceneRenderer::RenderFrame` runs the passes when `options.Lens` is set, the camera is not orthographic and the quality row is not Off. The editor camera path never sets `view.Lens`, so it stays empty.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Renderer/SceneRendererPost.cpp`: `CameraLens::FromEntity`, the circle of confusion, `RenderDepthOfField`.
- `Strata/src/Strata/Renderer/SceneRenderer.h`: `CameraLens`; `Strata/src/Strata/Renderer/PostProcessData.h`: the parameters and `c_DepthOfFieldMaxDiameter`.
- `Strata/shaders/PostProcess/DepthOfField*.comp.slang` and `Strata/shaders/Include/DepthOfField.slang`: the five passes.
- `Strata/src/Strata/Scene/Components.h`: the camera's fields; `StrataTests/src/Renderer/GPUSceneDepthOfFieldTests.cpp`: the tests.
- The **Depth of field** section of the **Camera** component in the **Inspector**.

## Further reading

- Matt Pharr, Wenzel Jakob and Greg Humphreys, Physically Based Rendering, the section on the thin lens camera model, at [pbr-book.org](https://pbr-book.org): the lens model with rays (intermediate).
- Jorge Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare", SIGGRAPH 2014: a gather with near and far fields (advanced).
- Guillaume Abadie, "A Life of a Bokeh", SIGGRAPH 2018: a production depth of field with scatter and gather (advanced).
