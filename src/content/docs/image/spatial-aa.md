---
id: image/spatial-aa
title: "Anti-aliasing in one frame: FXAA and morphological AA"
description: "How Strata removes jagged edges from one finished frame with FXAA and its morphological anti-aliasing, and what neither can fix."
kind: internals
size: L
tracks: [E]
needs: [image/encoding]
time: 80
learn:
  - id: why-jagged
    text: explain why a grid of point samples makes jagged edges and what a pass over one finished frame can and cannot repair
  - id: fxaa-steps
    text: trace FXAA's steps for one pixel and compute its blend offset from the two distances to the ends of its edge
  - id: morph-passes
    text: name the three passes of the morphological anti-aliasing and compute a pixel's blend from the area table
  - id: choose-aa
    text: choose a spatial anti-aliasing method for a scene and say what each method cannot fix
  - id: fallback
    text: trace where the renderer draws FXAA when the morphological resources cannot be made
since: 0.3.0
status: final
---

A game draws a world made of exact lines into a grid of squares, and a line that is not horizontal or vertical comes out as a staircase. Anti-aliasing is the work that hides the steps. This page covers the two ways Strata does that in a single finished frame: fast approximate anti-aliasing (FXAA) and its own morphological anti-aliasing.

Both read the picture after :term[tone mapping]{id=tone-mapping-image}, use no earlier frame, and change only pixels near an edge. Neither adds detail that the frame never had, and neither steadies an edge that crawls from one frame to the next. That is the job of temporal anti-aliasing (TAA), which has its own page: [Temporal anti-aliasing](../image/taa.md).

Look at the end of the ramp's rail over the floor of the Physics Playground in four ways. Each crop is enlarged four times, so every square you see is one pixel of the frame.

::compare{id=aliasing-floor before=off after=fxaa}

::compare{id=aliasing-floor before=morph after=taa}

The first picture has no anti-aliasing: the rail's slanted edges are staircases. The other three trade the steps for soft gradients in different ways, and the rest of the page explains how each one does it. The tiles look alike in all four, because their texture is already filtered.

## The problem and how engines solve it

A :term[renderer]{id=renderer} decides the color of a pixel by asking one question: what does the scene show at the center of this pixel? That is one **point sample** of the scene, as [Sampling, aliasing and filtering](../basics/signals.md) explains. The sample says nothing about the rest of the pixel's square. A pixel half covered by a white wall and half by a dark floor gets the color of whatever lies under its center. The answer is all white or all dark, never half and half.

Three kinds of aliasing follow from that. Geometric aliasing is the staircase along the edge of a triangle. Shading aliasing is a shimmer inside a surface: a sharp highlight or a fine texture pattern that changes faster than the pixel grid can follow. Temporal aliasing appears in motion: a staircase edge that moves by less than a pixel jumps from one step to the next, and a thin wire flickers in and out of view. This page deals with the first kind, and a little with the second.

Engines answer in three ways, and each has a price.

- **Supersampling** draws the frame with more samples per pixel and averages them. With four samples per pixel the edge of the wall above comes out as a mix of four answers, and the result is very good. The cost is also four times: four times the pixels to shade and four times the memory.
- Multi-sample anti-aliasing (MSAA) is the second answer. **MSAA** keeps one shading result per pixel but tests triangle coverage at several points. The edge of a triangle comes out right at a fraction of the cost of supersampling. Its limits are that it smooths only triangle edges, not shading, and that a renderer with many full-screen passes must store every target with several samples.
- A **post pass** works on the finished picture. It searches for edges in the pixels and blends across them. It costs one or a few full-screen passes, works on any content, and sees only pixels, so it cannot know where the true edge ran inside a square.

Strata has neither supersampling nor MSAA. The renderer refuses a target that is not single-sampled, in `Strata/src/Strata/Renderer/SceneRenderer.cpp`, where the format check tests `info.sampleCount != 1`. Strata also keeps its first design decision: a frame is never drawn below native resolution, and its anti-aliasing is TAA and the passes of this page. Nothing here renders above native size either. The quality page, [Quality settings](../image/quality-settings.md), explains the decision.

Post passes come in two families, and Strata has one of each.

The first family is **MLAA**, the morphological anti-aliasing of 2009, and its successor, enhanced subpixel morphological anti-aliasing (SMAA). It studies the staircase. It finds a run of edge pixels, sees how the staircase turns at each end, and works out the straight line the staircase stands for. Then it gives each pixel the share of the neighbor's color that the line leaves it.

The other family is FXAA. It finds the edge direction and walks along the edge to learn how far it runs. Then it moves the sample point across the edge by an amount that depends on the position along it. Both families rely on one assumption: the staircase is a good sign of the line, so the picture alone is enough to rebuild it.

The assumption fails for thin features. A wire thinner than a pixel was never drawn as a line, so no staircase shows it. Post passes also never see what was hidden by the sampling: the shimmer of a distant pattern stays. The sections below show how each method behaves, and the last one lets you choose.

## The map

The anti-aliasing passes live in one file and four :term[shaders]{id=shader}. Tone mapping finishes first, and writes the picture in display values to a 10-bit intermediate target, as [Display encoding and the last pass](../image/encoding.md) explains. One of the two methods reads that target next.

```mermaid caption="Where the two spatial methods run in a frame: after tone mapping, as one pass or as three." alt="A flow chart. Tone mapping writes an intermediate image, and a choice leads either to one FXAA pass or to three passes named edges, weights and blend. Both end in the display image."
flowchart LR
  T["Tone mapping"] --> L["10-bit intermediate"]
  L --> C{"Which method"}
  C -->|FXAA| F["FXAA pass"]
  C -->|Morphological| E["Edges pass"]
  E --> W["Weights pass"]
  W --> B["Blend pass"]
  F --> O["Display image"]
  B --> O
```

The files are these. `Strata/src/Strata/Renderer/SceneRendererPost.cpp` holds `RenderPostDisplay`, which chooses the method and records the passes, and `EnsureMorphologicalResources`, which makes the targets. The shaders are `FXAA.frag.slang`, `MorphologicalEdges.frag.slang`, `MorphologicalWeights.frag.slang` and `MorphologicalBlend.frag.slang` in `Strata/shaders/PostProcess/`. The area table is `Strata/src/Strata/Renderer/MorphologicalAreaTable.inl`, written by `Tools/GenerateAreaTable.py`. All of it runs on the :term[main thread's]{id=main-thread} command recording, and the passes run on the :term[graphics processing unit]{id=gpu} (GPU).

## The contract

A scene chooses its method on the `PostProcessComponent`: **Anti Aliasing** is on by default, and `AntiAliasingMethod` is one of `FXAA`, `TAA` and `Morphological`, with FXAA the default. The player's own quality rows can override the scene. The rules below hold for every caller, and each has its reason.

- The passes read display-encoded values. FXAA was designed for them, and the edge test of the morphological method uses them too, because a difference in display codes follows what the eye sees as an edge.
- The tone mapping writes the 10-bit intermediate with no :term[dither]{id=dither} and no grain. The last pass dithers and adds the grain, once, because a pass that came first would have its noise taken for edges and blended away.
- With TAA on, neither method runs: the frame was resolved over time, and the spatial passes are skipped.
- A pixel far from any edge keeps the tone mapping's value exactly, before the grain. The test of the flat-area case relies on it.
- If the morphological resources cannot be made, the frame is drawn with FXAA and the failure is reported once. A frame is never left without its final pass.
- Single images are the same each time they are taken: the grain's seed is the caller's choice, and the passes themselves hold no history.

:::rule
`AGENTS.md` says that every new renderer pass runs inside a :term[GPU stage]{id=gpu-stage-strata} registered with its module, and that a post effect is off in `AddNeutralPostProcess`. The reasons are measurement and testing: the stage's timer shows what the pass costs, and exact-pixel tests need a frame without effects. [Display encoding and the last pass](../image/encoding.md) gives the order of the chain.
:::

## A toy version

Before the real passes, build the plainest anti-aliasing you can. The toy has a staircase of brightness values in a small grid, finds the edge pixels and moves each one a quarter of the way toward the neighbor across its edge.

:::question
The toy uses loops and functions ([Programming 2](../basics/programming-2.md)) and calls such as `std::abs(` and `std::clamp(` ([Programming 3](../basics/programming-3.md)). Read the numbers it prints; the language details matter less than the idea.
:::

The program makes a grid of 12 by 6 values, 90 for a bright pixel and 10 for a dark one, in the shape of a staircase. It prints the grid, smooths it and prints it again. Notice which pixels change and by how much.

```cpp sketch="image-spatial-aa-toy.cpp"
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdio>

constexpr int c_Width = 12;
constexpr int c_Height = 6;
constexpr float c_Threshold = 0.2f;   // The smallest luma difference that counts as an edge
constexpr float c_BlendWeight = 0.25f; // How far a pixel moves toward the neighbor across its edge

using Image = std::array<std::array<float, c_Width>, c_Height>;

float At(const Image& image, int x, int y)
{
	return image[std::clamp(y, 0, c_Height - 1)][std::clamp(x, 0, c_Width - 1)];
}

Image Smooth(const Image& image)
{
	Image result = image;
	for (int y = 0; y < c_Height; y++)
	{
		for (int x = 0; x < c_Width; x++)
		{
			const float center = At(image, x, y);
			const float neighbors[4] = { At(image, x, y - 1), At(image, x, y + 1), At(image, x - 1, y), At(image, x + 1, y) };
			float across = center;
			for (float neighbor : neighbors)
				if (std::abs(neighbor - center) > std::abs(across - center))
					across = neighbor;
			if (std::abs(across - center) < c_Threshold)
				continue;
			result[y][x] = center + c_BlendWeight * (across - center);
		}
	}
	return result;
}

void Print(const Image& image)
{
	for (const auto& row : image)
	{
		for (float luma : row)
			std::printf("%4ld", std::lround(luma * 100.0f));
		std::printf("\n");
	}
}

int main()
{
	Image image = {};
	for (int y = 0; y < c_Height; y++)
		for (int x = 0; x < c_Width; x++)
			image[y][x] = x < 2 + 2 * y ? 0.9f : 0.1f; // A staircase: bright on the left, 2 pixels more each row
	Print(image);
	std::printf("\n");
	Print(Smooth(image));
	return 0;
}
```

```text output-of="image-spatial-aa-toy.cpp"
  90  90  10  10  10  10  10  10  10  10  10  10
  90  90  90  90  10  10  10  10  10  10  10  10
  90  90  90  90  90  90  10  10  10  10  10  10
  90  90  90  90  90  90  90  90  10  10  10  10
  90  90  90  90  90  90  90  90  90  90  10  10
  90  90  90  90  90  90  90  90  90  90  90  90

  90  70  30  30  10  10  10  10  10  10  10  10
  90  90  70  70  30  30  10  10  10  10  10  10
  90  90  90  90  70  70  30  30  10  10  10  10
  90  90  90  90  90  90  70  70  30  30  10  10
  90  90  90  90  90  90  90  90  70  70  30  30
  90  90  90  90  90  90  90  90  90  90  70  70
```

1. **Line 15:** the clamp keeps a border pixel's missing neighbor inside the grid, so the edge of the picture is no edge.
2. **Lines 27–30:** `across` is the neighbor whose brightness differs most from the center's.
3. **Lines 31–32:** a pixel whose largest difference is below the threshold is flat and stays as it is.
4. **Line 33:** the pixel moves a quarter of the way toward that neighbor.

Every bright pixel that touches a dark one dropped from 90 to 70, and every dark pixel that touches a bright one rose from 10 to 30. The step of 80 between two pixels became a ramp: 90, 70, 30, 10. That is the idea of every post pass.

The toy has two flaws, and the real methods fix both. It gives every edge pixel the same weight, so the first pixel of a long shallow run is treated like the last, and a steep jump like a gentle slope. And it measures brightness with one number per pixel without caring whether the number is a display code or light, which matters when blending (a later section shows how much).

## FXAA, step by step

**FXAA** is one fragment shader that reads the finished picture. Strata's `FXAA.frag.slang` follows the published version 3.11, in its quality path. It has five jobs.

FXAA decides whether the pixel lies near an edge, learns whether the edge runs horizontally or vertically, and finds the edge's two ends. Then it works out how far the pixel lies from the nearer end and moves the sample across the edge by an amount that depends on that distance. The steps are in the next diagram.

```mermaid caption="The steps of FXAA for one pixel. The pixel and its four neighbors give the local contrast. A pixel that passes the test gets its edge direction, the walk along the edge to both ends, the subpixel term, and a final sample moved across the edge." alt="A flow chart of seven boxes. The first reads the luma of the pixel and its four neighbors. The second tests the local contrast and stops if it is low. The next boxes choose the edge direction, walk along the edge for up to twelve steps, compute the offset from the two distances, and take the larger of that and the subpixel term. The last samples the picture at the moved position."
flowchart LR
  A["Luma of the pixel and four neighbors"] --> B{"Contrast high enough"}
  B -->|No| Z["Keep the pixel"]
  B -->|Yes| C["Edge direction from second differences"]
  C --> D["Walk along the edge, up to 12 steps"]
  D --> E["Offset from the two distances"]
  E --> F["Larger of offset and subpixel term"]
  F --> G["Sample the picture at the moved position"]
```

FXAA works on **luma**, a single number for the brightness of a pixel that is built from its encoded red, green and blue. Strata's FXAA weights them 0.299, 0.587 and 0.114, and the weights add up to 1. They apply to display values, not to light, which is what FXAA's authors assumed. Colors with the same luma blend as if they had no edge, so a bright red next to a bright green with equal luma is not smoothed.

Here is a worked example before the code. The numbers are luma values of a gray picture, so the luma is the gray value. The pixel in the middle is bright, and the edge below it runs three pixels to its left and ends one pixel to its right.

:::example
The 3 by 3 block around the pixel has these luma values.

| | West | Middle | East |
| --- | --- | --- | --- |
| Row above | 0.9 | 0.9 | 0.9 |
| The pixel's row | 0.9 | 0.9 | 0.4 |
| Row below | 0.1 | 0.1 | 0.1 |

The largest of the middle and its four neighbors is 0.9 and the smallest is 0.1, so the local contrast is 0.8. The test needs at least the larger of 0.0312 and 0.125 times 0.9, which is 0.1125. The pixel passes.

A second difference adds the values on both sides of a pixel and subtracts the pixel twice: it is large where the values bend across a line. Down the middle column it is 0.9 - 1.8 + 0.1, a size of 0.8, counted twice; the outer columns add 0.8 and 0.2. The sums are 2.6 for a horizontal edge and 1.0 for a vertical one, so the edge runs horizontally. The neighbor above differs from the middle by 0, the one below by 0.8, so the edge lies below the pixel. The local average across it is 0.5 and the walk stops when a sample differs from that by 0.2, a quarter of the larger difference.

Going west, two samples (at 1 and 2 pixels) lie across a boundary between a bright pixel and a dark one, which averages 0.5, so they do not stop the walk. Three pixels to the west, the pixel's row and the row below are both dark, so the sample gives 0.1 and stops the walk. Going east, the first sample, one pixel away, averages 0.4 and 0.1 to 0.25 and stops. The distances are 3 and 1 pixels.

The offset is 0.5 minus the nearer distance divided by the sum, which is 0.5 minus 1 over 4, or 0.25. The nearer end shows the right kind of change, so FXAA uses it. The neighborhood's weighted average is 0.55, which gives a subpixel term of 0.0414, smaller, so the offset stays 0.25. The final sample lies a quarter of a pixel below the middle, and the filter mixes 0.75 of 0.9 and 0.25 of 0.1: the pixel becomes 0.7.
:::

The first test throws away most of the frame. The flat areas of a game picture have almost no contrast, so most pixels leave the shader at once and keep their color. Only the pixels that pass pay for the long walk.

Now the code. The first quote shows the contrast test, the subpixel term, the choice of direction and the side of the edge.

```cpp src="Strata/shaders/PostProcess/FXAA.frag.slang#L67-L101"
float lumaMax = max(lumaM, max(max(lumaN, lumaS), max(lumaW, lumaE)));
float lumaMin = min(lumaM, min(min(lumaN, lumaS), min(lumaW, lumaE)));
float range = lumaMax - lumaMin;
if (range < max(c_EdgeThresholdMin, lumaMax * c_EdgeThreshold))
{
	o_Color = Finish(center);
	return;
}

float lumaNW = Luma(Fetch(uv + float2(-texel.x, -texel.y)));
float lumaNE = Luma(Fetch(uv + float2(texel.x, -texel.y)));
float lumaSW = Luma(Fetch(uv + float2(-texel.x, texel.y)));
float lumaSE = Luma(Fetch(uv + float2(texel.x, texel.y)));

// Sub-pixel aliasing: how far the center is from the average of its neighborhood.
float neighborhood = (2.0 * (lumaN + lumaS + lumaW + lumaE) + lumaNW + lumaNE + lumaSW + lumaSE) / 12.0;
float subpixel = smoothstep(0.0, 1.0, clamp(abs(neighborhood - lumaM) / range, 0.0, 1.0));
float subpixelOffset = subpixel * subpixel * c_Subpixel;

// Edge orientation from the second derivatives across the 3x3 block.
float edgeHorizontal = abs(lumaNW - 2.0 * lumaW + lumaSW) + 2.0 * abs(lumaN - 2.0 * lumaM + lumaS) + abs(lumaNE - 2.0 * lumaE + lumaSE);
float edgeVertical = abs(lumaNW - 2.0 * lumaN + lumaNE) + 2.0 * abs(lumaW - 2.0 * lumaM + lumaE) + abs(lumaSW - 2.0 * lumaS + lumaSE);
bool horizontal = edgeHorizontal >= edgeVertical;

// The side of the edge with the steeper gradient; the search runs along the boundary half a pixel toward it.
float stepLength = horizontal ? texel.y : texel.x;
float luma1 = horizontal ? lumaN : lumaW;
float luma2 = horizontal ? lumaS : lumaE;
float gradient1 = abs(luma1 - lumaM);
float gradient2 = abs(luma2 - lumaM);
bool steeper1 = gradient1 >= gradient2;
float gradientScaled = 0.25 * max(gradient1, gradient2);
float lumaLocalAverage = 0.5 * ((steeper1 ? luma1 : luma2) + lumaM);
if (steeper1)
	stepLength = -stepLength;
```

1. **Line 70:** the contrast must beat an absolute floor and a share of the brightest neighbor, so dark noise stays untouched and bright areas need more contrast.
2. **Line 84:** the subpixel term is the square of a smoothed difference between the center and its blurred neighborhood, times `c_Subpixel`.
3. **Lines 87–89:** the edge's direction comes from second differences; the center row of each block counts twice.
4. **Lines 95–101:** the side of the edge with the steeper gradient is the one the search follows; `stepLength` carries its sign.

The second quote is the walk and the final sample.

```cpp src="Strata/shaders/PostProcess/FXAA.frag.slang#L116-L153"
float2 uv1 = edgeUV - offset;
float2 uv2 = edgeUV + offset;
float lumaEnd1 = Luma(Fetch(uv1)) - lumaLocalAverage;
float lumaEnd2 = Luma(Fetch(uv2)) - lumaLocalAverage;
bool reached1 = abs(lumaEnd1) >= gradientScaled;
bool reached2 = abs(lumaEnd2) >= gradientScaled;
for (int step = 1; step < c_SearchSteps && !(reached1 && reached2); step++)
{
	if (!reached1)
	{
		uv1 -= offset * c_StepSizes[step];
		lumaEnd1 = Luma(Fetch(uv1)) - lumaLocalAverage;
		reached1 = abs(lumaEnd1) >= gradientScaled;
	}
	if (!reached2)
	{
		uv2 += offset * c_StepSizes[step];
		lumaEnd2 = Luma(Fetch(uv2)) - lumaLocalAverage;
		reached2 = abs(lumaEnd2) >= gradientScaled;
	}
}

float distance1 = horizontal ? uv.x - uv1.x : uv.y - uv1.y;
float distance2 = horizontal ? uv2.x - uv.x : uv2.y - uv.y;
bool closer1 = distance1 < distance2;
float edgeOffset = 0.5 - min(distance1, distance2) / (distance1 + distance2);

// Blend only when the luma at the nearer edge end varies the opposite way to the center (a real edge end).
bool centerSmaller = lumaM < lumaLocalAverage;
bool correctVariation = ((closer1 ? lumaEnd1 : lumaEnd2) < 0.0) != centerSmaller;
float finalOffset = max(correctVariation ? edgeOffset : 0.0, subpixelOffset);

float2 finalUV = uv;
if (horizontal)
	finalUV.y += finalOffset * stepLength;
else
	finalUV.x += finalOffset * stepLength;
o_Color = Finish(Fetch(finalUV));
```

1. **Lines 118–121:** the first two samples, one pixel each way, along the boundary half a pixel toward the steep side; each stops when its luma differs enough from the local average.
2. **Lines 122–136:** the loop takes five steps of 1 pixel, then 1.5, four of 2, then 4 and 8 (`c_StepSizes`), 12 samples in all, so long edges are searched far at little cost.
3. **Line 141:** the offset is half a pixel minus the nearer distance as a share of the whole edge length.
4. **Lines 144–146:** the blend applies only when the luma at the nearer end moves away from the center's side; otherwise only the subpixel term acts.

The step sizes widen along the walk, so one lookup covers more distance. A search of 12 samples reaches 26.5 pixels; the worked example needed only three.

The **subpixel blend** is FXAA's smoothing of single-pixel features, such as a wire that crosses one pixel. No walk finds such a feature, because it has no ends. FXAA instead measures how far the pixel lies from the average of its neighbors, squares the measure and multiplies it by `c_Subpixel`. The larger of this term and the edge offset moves the sample.

The constant is 0.25 for a measured reason. At 0.75, the value before release 0.7.0, FXAA removed about a fifth of the fine texture of the Physics Playground's tiled floor at 3840 by 2160, compared with an image without anti-aliasing. At 0.375 it still removed 15 %. The price of 0.25 is that single-pixel aliasing, such as a thin wire, is smoothed less. The pictures below draw a crop of that floor at both values, enlarged four times.

::compare{id=subpixel-pair before=low after=high}

## The morphological anti-aliasing, pass by pass

FXAA moves the sample point. The morphological anti-aliasing of Strata blends colors by an area. It works in three passes with two small targets between them, and no pass reads more than the one before. Strata designed it for itself and takes nothing from the table of the published SMAA; the name comes from the family.

```mermaid caption="The morphological anti-aliasing in three passes. The first marks the edges, the second searches the run of each edge and reads the area table for blend weights, and the third mixes colors in linear light." alt="A flow chart with three boxes in a row and a table below the second. The first box reads the display image and the depth and writes a map of edges. The second reads the map and the area table and writes blend weights. The third reads the display image and the weights and writes the final image."
flowchart LR
  I["Display image and depth"] --> P1["Pass 1: edges"]
  P1 --> M["Edge map"]
  M --> P2["Pass 2: weights"]
  A["Area table"] --> P2
  P2 --> W["Blend weights"]
  W --> P3["Pass 3: blend in linear light"]
  I --> P3
  P3 --> R["Final image"]
```

The first pass makes the edge map. For each pixel it writes two edges: the one to its left and the one above. An edge exists when the luma of the two pixels differs by 0.05 or more. Here the luma weights are 0.2126, 0.7152 and 0.0722, applied to display values; they differ from FXAA's.

The edge is kept only if its difference is at least half the largest difference among the pixel's other neighbors. That is local contrast adaptation. Of two nearby edges, the strong one is the one the eye sees as jagged, and the weak one is a halo of the strong one.

The map has a second source. A jump in depth is an edge even where the colors agree, such as two equal gray walls at different distances. The depth must change between two pixels by more than 5 % of its value and by more than twice the steps beside it. The second condition keeps a slope from counting: on a flat plane the depth changes steadily from pixel to pixel, and only a jump beats twice that step.

:::example
Take a left edge with these luma values: the pixel 0.60, its left neighbor 0.40, so the difference is 0.20, above 0.05. The largest difference among the other neighbors is 0.50. Half of that is 0.25, and 0.20 is below it, so the edge is dropped: a stronger edge lies next to it.

Now take a depth row where the depth falls by 0.002 per pixel along a slope, then drops from 0.300 to 0.250. The jump is 0.05. Five percent of 0.300 is 0.015 and twice the neighboring step is 0.004. Both tests pass, so the pixel has a depth edge, even if its colors match.
:::

The first pass is short. Search for its two tests, luma and depth, and for the lines that clear the edges of the first row and column.

```cpp src="Strata/shaders/PostProcess/MorphologicalEdges.frag.slang#L46-L80"
bool DepthEdge(int2 pixel, int2 step)
{
	float before = Depth(pixel - 2 * step);
	float previous = Depth(pixel - step);
	float center = Depth(pixel);
	float after = Depth(pixel + step);
	float jump = abs(center - previous);
	return jump > u_Parameters.DepthThreshold * max(center, previous) && jump > 2.0 * max(abs(previous - before), abs(after - center));
}

void st_Main()
{
	g_Size = TextureSize(u_Color, 0);
	int2 pixel = int2(st_FragCoord.xy);
	float center = Luma(pixel);
	float left = Luma(pixel - int2(1, 0));
	float top = Luma(pixel - int2(0, 1));
	float2 delta = abs(float2(center - left, center - top));
	float2 edges = step(float2(u_Parameters.Threshold), delta);
	if (edges.x + edges.y > 0.0)
	{
		float right = Luma(pixel + int2(1, 0));
		float bottom = Luma(pixel + int2(0, 1));
		float leftLeft = Luma(pixel - int2(2, 0));
		float topTop = Luma(pixel - int2(0, 2));
		float largest = max(max(max(delta.x, delta.y), max(abs(center - right), abs(center - bottom))), max(abs(left - leftLeft), abs(top - topTop)));
		edges *= step(float2(0.5 * largest), delta);
	}
	edges = max(edges, float2(DepthEdge(pixel, int2(1, 0)) ? 1.0 : 0.0, DepthEdge(pixel, int2(0, 1)) ? 1.0 : 0.0));
	// The image's first column and row have no pixel left of or above them.
	if (pixel.x == 0)
		edges.x = 0.0;
	if (pixel.y == 0)
		edges.y = 0.0;
	o_Edges = edges;
```

1. **Line 53:** the depth test: a jump beyond a share of the depth and beyond twice the neighbors' steps.
2. **Lines 63–64:** the luma differences to the left and top neighbors, compared with the threshold.
3. **Lines 65–73:** the local contrast step, which reads four more neighbors only for pixels that already have an edge.
4. **Lines 76–79:** the first row and column have no pixel on the left or above, so they get no edge.

The second pass finds runs. For a pixel on a horizontal edge, it counts the pixels with the same edge to the left and to the right, up to 32 in each direction. Call these counts $d_1$ and $d_2$.

At each end of the run it examines the crossing edges: does the staircase turn across the edge, onto the pixel's own side, both ways or not at all? That gives one of four codes for each end. A run that continues beyond 32 pixels has no known end, and the code is 0.

The staircase then stands for a line. The line crosses the edge at the middle of the run and sits half a pixel off it at an end where the staircase steps. Steps at the two ends in opposite directions make a Z shape, a straight line through the middle. One step makes an L, a line that leans from the step to the middle.

Two steps in the same direction make a U: a dot or a dash, which blends nothing. A dot is a tiny bump, and the texture of a floor is full of them, so smoothing them would wash out the detail.

The **area table** holds the answer in advance. For each pair of end codes and each pair of distances it stores the share of the pixel that the line puts on the other side of the edge, one share for each side. Strata makes it with `Tools/GenerateAreaTable.py`, which integrates the line exactly, and commits the output. The table is a picture of two 8-bit channels, 132 by 132 texels: four codes times 33 distances (0 to 32) in each direction. The pass finds both shares with one texel read.

:::example
Take a Z run of 5 pixels, with the staircase stepping down at its first end and up at its last. The line goes from -0.5 at the first end through 0 in the middle to +0.5 at the last end. The table gives these shares for the five pixels, from the first to the last: 0.400, 0.200, 0.025 (with 0.025 on the other side), 0.200 and 0.400. The first two pixels lean on the color across the edge on one side, the last two on the other side. The middle pixel gives a little to each.

A U of the same length gives 0 for every pixel. The line the table would draw has no meaning there, so the table holds zeros.
:::

The second pass is one search in two directions and one read. Search for the two loops that count the run and for the line that reads the table.

```cpp src="Strata/shaders/PostProcess/MorphologicalWeights.frag.slang#L42-L60"
g_Size = TextureSize(u_Edges, 0);
int2 pixel = int2(st_FragCoord.xy);
float2 edges = Edges(pixel);
float4 weights = float4(0.0);
if (edges.y > 0.5)
{
	// The top edge: a horizontal run between this row and the one above. A run that goes on beyond the search has no
	// known end there (no crossing).
	int left = 0;
	while (left < c_MaxSearch && Edges(pixel - int2(left + 1, 0)).y > 0.5)
		left++;
	int right = 0;
	while (right < c_MaxSearch && Edges(pixel + int2(right + 1, 0)).y > 0.5)
		right++;
	int2 first = pixel - int2(left, 0);
	int2 last = pixel + int2(right, 0);
	int firstCrossing = left < c_MaxSearch ? Crossing(Edges(first + int2(0, -1)).x > 0.5, Edges(first).x > 0.5) : 0;
	int lastCrossing = right < c_MaxSearch ? Crossing(Edges(last + int2(1, -1)).x > 0.5, Edges(last + int2(1, 0)).x > 0.5) : 0;
	weights.rg = Areas(firstCrossing, lastCrossing, left, right);
```

1. **Line 46:** the top-edge run starts only on a pixel that has a top edge.
2. **Lines 51–55:** two searches walk each way, at most `c_MaxSearch` (32) pixels; the count is the run's length on that side.
3. **Lines 58–59:** the crossing at each end is found in the edge map, and a run that did not end within the search gets code 0.
4. **Line 60:** one texture read gives both shares, which go into the weights target.

The third pass mixes. Each pixel adds the shares of its own top and left edges and the shares that the pixel below and the pixel to its right give it. It then mixes the colors across the edges in linear light. This is the point where display encoding matters.

Take a dark pixel with display value 0.1 and a neighbor of 0.9 with a share of 0.4. Averaging the display values gives 0.42. Converting to light first, mixing and converting back gives 0.60: a gray that is in fact a mix of the light, which is how a real half-covered pixel would look. If the shares sum to more than one (a corner of two runs), they are scaled down to one.

```cpp src="Strata/shaders/PostProcess/MorphologicalBlend.frag.slang#L34-L55"
int2 size = TextureSize(u_Color, 0);
int2 pixel = int2(st_FragCoord.xy);
float3 color = u_Color.Load(int3(pixel, 0)).rgb;
float4 own = u_Weights.Load(int3(pixel, 0));
float up = own.r;
float left = own.b;
float down = pixel.y + 1 < size.y ? u_Weights.Load(int3(pixel + int2(0, 1), 0)).g : 0.0;
float right = pixel.x + 1 < size.x ? u_Weights.Load(int3(pixel + int2(1, 0), 0)).a : 0.0;
float total = up + down + left + right;
if (total > 0.0)
{
	// Shares above a whole pixel (a pixel in a corner of two runs) are scaled down to one.
	float scale = total > 1.0 ? 1.0 / total : 1.0;
	float3 mixed = SRGBToLinear(color) * (1.0 - total * scale);
	mixed += SRGBToLinear(u_Color.Load(int3(max(pixel - int2(0, 1), int2(0)), 0)).rgb) * (up * scale);
	mixed += SRGBToLinear(u_Color.Load(int3(min(pixel + int2(0, 1), size - 1), 0)).rgb) * (down * scale);
	mixed += SRGBToLinear(u_Color.Load(int3(max(pixel - int2(1, 0), int2(0)), 0)).rgb) * (left * scale);
	mixed += SRGBToLinear(u_Color.Load(int3(min(pixel + int2(1, 0), size - 1), 0)).rgb) * (right * scale);
	color = LinearToSRGB(mixed);
}
color = AddFilmGrain(color, uint2(pixel), u_Parameters.FilmGrain, u_Parameters.GrainFrame);
o_Color = float4(DitherToCodes(color, uint2(pixel), u_Parameters.DitherLevels), 1.0);
```

1. **Lines 38–41:** its own `r` and `b` weights, and the `g` of the pixel below and the `a` of the pixel to the right.
2. **Lines 42–46:** a total above one is scaled to one, so a pixel in a corner never takes more than all of the neighbors.
3. **Lines 47–52:** each color is converted to linear light, mixed by its share and converted back.
4. **Lines 54–55:** the grain is added and the result is dithered: this is the last pass, so it does both.

Pixels with no weights keep their value exactly. The method's error grows with the slope. The engine's developer guide measures a 1:7 edge within 0.08 of its true coverage on average and a 1:3 edge within 0.15, against 0.25 and 0.28 with no anti-aliasing. The reason is that the reconstructed line crosses each run at its middle, while the true line crosses anywhere within half a pixel of it.

## Choosing the method and the fallback

`RenderPostDisplay` decides which of the two methods runs and with which targets. The quote shows the decision: TAA comes first, and a morphological request falls back to FXAA when its resources fail.

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

1. **Line 1278:** the anti-aliasing applies unless the image was resolved temporally.
2. **Lines 1279–1282:** the method asked for is Morphological and its resources can be made; if the creation fails, the frame is marked degraded and `EnsureMorphologicalResources` has already reported why.
3. **Line 1283:** FXAA runs when anti-aliasing is on and the morphological method is not the one that runs; this is the fallback.
4. **Lines 1287–1288:** the method that comes last in the chain takes the dither, so the tone mapping dithers only when no method follows.

The resources are made by the first frame that asks for them. The two targets hold two 8-bit channels for the edges and four for the weights, about 50 MB at 3840 by 2160. Other methods make none. The area table does not depend on the picture size, so it stays when the viewport changes and the targets are released.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Supersampling | Film renderers, and games with a render scale above 1 | The best image for every kind of aliasing | Four times the pixels at four samples, and Strata's first design decision on native resolution |
| MSAA | Many forward renderers | Exact triangle edges for little extra work | Every target stored with several samples, and no help with shading aliasing |
| Published SMAA | Games that ship it as a library | A pattern search used in many games | A second table and search to port, and the area table's tuning for texture detail |
| Temporal anti-aliasing alone | Many 3D engines | Steady edges, thin details and shading aliasing | A frame that depends on earlier ones, ghosting, and a blur that needs sharpening |

The table does not say TAA is wrong. Strata has it, and the Basic 3D template chooses it. The spatial methods are for the games that cannot use it: those that must never trail, and the 2D games that want crisp pixels.

## How it is tested

The tests need a GPU and live in `StrataTests/src/Renderer/`. In the suite `GPU.SceneRenderer.PostProcess`, one case checks that FXAA smooths jagged edges and keeps flat areas, on a rotated white quad. The suite `GPU.SceneRenderer.Morphological` has four cases.

- A tilted edge's pixels take the coverage of the line their staircase stands for, at slopes of 1:7, 1:3 and 3. The 1:7 error stays under 0.1, and every slope stays under 0.6 times the error without anti-aliasing.
- Flat areas keep the tone mapping's value exactly, as they do under FXAA.
- Both draw paths of the renderer, the CPU-driven and the GPU-driven, give the same smoothing within one code.
- Other methods make no morphological targets, and the statistic `MorphologicalAntiAliasing` stays false.

Each GPU test ends with `CHECK(gpu.GetNewErrorCount() == 0)`, so a validation error from the new passes fails the test. Run one suite directly with `build/windows/bin/Debug/StrataTests.exe --test-suite=GPU.SceneRenderer.Morphological`, or all of them with `ctest --preset windows-debug -L gpu`.

## Changing it safely

The extension points are few. The constants at the top of `FXAA.frag.slang` (`c_EdgeThreshold`, `c_EdgeThresholdMin`, `c_Subpixel`, `c_SearchSteps`) tune FXAA. The edge thresholds of the morphological method are `c_MorphologicalThreshold` and `c_MorphologicalDepthThreshold` in `Strata/src/Strata/Renderer/PostProcessData.h`. The area table changes only through the script, never by hand.

- Keep the grain after the anti-aliasing. Placed before it, the grain would pass the edge thresholds of FXAA (0.0312) and of the morphological method (0.05), and the passes would blend away about a sixth of its spread.
- Change the generator, not the `.inl`: the file is committed output, and a hand edit disappears on the next run.
- A new pass goes into a GPU stage registered with its module. Keep the pass off in `AddNeutralPostProcess`, so exact-pixel tests keep their meaning.
- A change that alters the picture of the Physics Playground's floor needs the look-dev crops taken again. See [Look-dev harness](../engineering/look-dev.md).
- Run both GPU suites and `GPU.SceneRenderer.GrainAndAberration` before committing.

## Summary

- A grid of point samples turns every slanted edge into a staircase. A pass over one finished frame can only guess the line from the staircase, so it fixes edges and not thin features or crawling.
- FXAA tests local contrast on luma of display values and finds the edge's direction. It walks up to 12 steps along the edge and moves the sample across it by half a pixel minus the nearer distance's share; the subpixel term is 0.25.
- The morphological method has three passes: edges (luma and depth), weights (a run search, crossings and the area table) and a blend in linear light. Z and L runs blend; U runs do not.
- Choose FXAA for the cheapest pass that never trails, the morphological method when texture detail matters, and TAA for steady 3D images; no spatial method steadies motion.
- When the morphological resources cannot be made, `RenderPostDisplay` draws FXAA and marks the frame degraded.

## Check yourself

1. A scene has `AntiAliasingMethod` set to TAA and the player's quality row says FXAA. Which spatial pass can run, and why does the contract say the grain comes last?
   :::answer{tests="why-jagged,choose-aa"}
   The player's row wins, so FXAA runs on the display image. If the grain came first, FXAA's contrast test would read the grain as edges and blend the picture. The grain and the dither come last, in the pass that writes the final image.
   :::
2. FXAA finds a pixel whose walk stops at 2 pixels on one side and 6 on the other. What is the edge offset?
   - A. 0.25
   - B. 0.125
   - C. 0.375
   :::answer{tests="fxaa-steps"}
   A is right. The offset is 0.5 minus the nearer distance over the sum: 0.5 - 2/8 = 0.25. B is one over the sum, 1/8, and C is 0.5 minus that. Neither takes the nearer distance's share of the edge.
   :::
3. In the morphological method, a run has a step up at both ends. How much of the neighbor's color do its pixels take?
   :::answer{tests="morph-passes"}
   None. A run between two steps the same way is a U, which looks like a dot or dash of texture. The table holds zeros for it, so the pixels keep their value.
   :::
4. A thin white wire, half a pixel wide, crosses a dark sky. Which method repairs the breaks in the wire?
   - A. FXAA
   - B. The morphological method
   - C. Neither
   :::answer{tests="choose-aa,why-jagged"}
   C is right. The wire was sampled in some pixels and missed in others, so the picture has dashes and no staircase for a pass to follow. FXAA's subpixel term can soften a single bright pixel a little, but it cannot invent the missing ones. Only more samples, as in TAA, bring them back.
   :::
5. Which line of `RenderPostDisplay` makes FXAA run when the morphological resources fail?
   :::answer{tests="fallback"}
   The line `const bool fxaa = antiAliased && !morphological;` in `Strata/src/Strata/Renderer/SceneRendererPost.cpp`. `morphological` is false when `EnsureMorphologicalResources` returns false, and `morphologicalWanted` stays true, which marks the frame degraded.
   :::

## Exercises

1. **Basic.** Read the sketch of the area of a Z run of 7 pixels below, predict its first and its middle pixel, then run it.
   :::answer[Worked solution]{tests="morph-passes"}
   The line goes from -0.5 to +0.5 across 7 pixels, so it is (x - 3.5) / 7. The first pixel spans 0 to 1 and the line is negative there, so the area below the edge is the integral of the line's size: ((3.5)^2 - (2.5)^2) / 14 = 0.429. The middle pixel spans 3 to 4 and the line crosses zero at 3.5, so it gives 0.018 to each side.

   ```cpp sketch="image-spatial-aa-areas.cpp"
   #include <algorithm>
   #include <cstdio>

   // A Z run of the given length: its line is (x - length / 2) / length, from -0.5 at the first end to +0.5 at the last.
   // The area below the edge (the line is negative) and above it (positive), inside the pixel from x = first to first + 1.
   float Below(int first, float length)
   {
   	const float middle = 0.5f * length;
   	const float low = static_cast<float>(first);
   	const float high = std::min(low + 1.0f, middle);
   	if (high <= low)
   		return 0.0f;
   	return ((middle - low) * (middle - low) - (middle - high) * (middle - high)) / (2.0f * length);
   }

   float Above(int first, float length)
   {
   	const float middle = 0.5f * length;
   	const float low = std::max(static_cast<float>(first), middle);
   	const float high = static_cast<float>(first) + 1.0f;
   	if (high <= low)
   		return 0.0f;
   	return ((high - middle) * (high - middle) - (low - middle) * (low - middle)) / (2.0f * length);
   }

   int main()
   {
   	const int length = 7;
   	for (int pixel = 0; pixel < length; pixel++)
   		std::printf("pixel %d: below %.3f, above %.3f\n", pixel, Below(pixel, static_cast<float>(length)), Above(pixel, static_cast<float>(length)));
   	return 0;
   }
   ```

   ```text output-of="image-spatial-aa-areas.cpp"
   pixel 0: below 0.429, above 0.000
   pixel 1: below 0.286, above 0.000
   pixel 2: below 0.143, above 0.000
   pixel 3: below 0.018, above 0.018
   pixel 4: below 0.000, above 0.143
   pixel 5: below 0.000, above 0.286
   pixel 6: below 0.000, above 0.429
   ```

   1. **Lines 8–13:** the area below the edge inside the pixel: the line is negative only up to the middle of the run.
   2. **Lines 18–23:** the area above the edge, from the middle onward.
   3. **Lines 29–30:** each pixel of the run prints its two shares.
   :::
2. **Medium.** Run the anti-aliasing shoot-out. Capture the Physics Playground's floor with the look-dev harness, with `--aa` set to `off`, `fxaa`, `morph` and `taa`, and compare the crops. Then capture a slow camera pan, for example the shot `tp.live.slow` of the `ThirdPerson` sample, and compare four frames in a row.
   :::answer[Worked solution]{tests="choose-aa"}
   1. Run the harness's `capture` command with `--aa off,fxaa,morph,taa` on the shots you chose, and read the crops it writes.
   2. In the still, FXAA and the morphological method give gradients on the tile edges; the morphological one leaves the dots of the texture alone, and TAA is the smoothest.
   3. In the pan, the edges of the first two methods crawl from frame to frame, because each frame is smoothed alone. TAA stays steady. The rule is that a spatial method cannot fix motion.
   :::
3. **Medium.** Rebuild with FXAA's `c_Subpixel` at 0.75 and then at 0.25, and measure the texture detail of the floor crop against the image without anti-aliasing.
   :::answer[Worked solution]{tests="fxaa-steps"}
   1. Edit `c_Subpixel` in `Strata/shaders/PostProcess/FXAA.frag.slang`, rebuild the shaders and capture the floor with `--aa fxaa`; do it for each value.
   2. Take a detail measure of your own on the crop, such as the mean absolute difference of neighboring pixels' luma, and divide by the measure of the `off` crop.
   3. The guide reports 19 to 22 % of the detail lost at 0.75 and about 13 % at 0.25. Expect the 0.75 build to look softer on the tile pattern.
   :::
4. **Hard.** Trace it yourself. Follow `AntiAliasingMethod` set to `Morphological` from the choice in `RenderPostDisplay` through `EnsureMorphologicalResources` to the three passes and the statistic that reports them. Find the line where a failed creation makes the frame draw FXAA.
   :::answer[Worked solution]{tests="fallback,morph-passes"}
   Open `Strata/src/Strata/Renderer/SceneRendererPost.cpp` and search for `morphologicalWanted`. `RenderPostDisplay` computes `morphological` by calling `EnsureMorphologicalResources`, which returns true at once when the edge target exists, otherwise makes the area table and two targets, reports a failure with "drawing with FXAA" and returns false. When it returns false, `degraded` is set and `const bool fxaa = antiAliased && !morphological;` becomes true. When it succeeds, the code records the edges, weights and blend passes under one marker and sets `m_Stats.MorphologicalAntiAliasing`.
   :::

## Where it lives in Strata

- Shaders: `Strata/shaders/PostProcess/FXAA.frag.slang`, `MorphologicalEdges.frag.slang`, `MorphologicalWeights.frag.slang`, `MorphologicalBlend.frag.slang`.
- Choice and resources: `RenderPostDisplay` and `EnsureMorphologicalResources` in `Strata/src/Strata/Renderer/SceneRendererPost.cpp`.
- Settings: `PostProcessComponent::AntiAliasing` and `AntiAliasingMethod` in `Strata/src/Strata/Renderer/RendererComponents.h`; the `Renderer.Quality` section's `AntiAliasing` row.
- Table: `Tools/GenerateAreaTable.py` writes `Strata/src/Strata/Renderer/MorphologicalAreaTable.inl`.
- Tests: `GPU.SceneRenderer.PostProcess` and `GPU.SceneRenderer.Morphological`.

## Further reading

- Timothy Lottes, "FXAA" (NVIDIA white paper, 2009): the algorithm Strata's shader follows; intermediate.
- Alexander Reshetov, "Morphological Antialiasing" (High Performance Graphics, 2009): the idea of reconstructing lines from staircases; advanced.
- Jorge Jimenez and others, "SMAA: Enhanced Subpixel Morphological Antialiasing" (Eurographics, 2012): the published method Strata's differs from; advanced.
- Tomas Akenine-Moller, Eric Haines and Naty Hoffman, "Real-Time Rendering", the chapter on image-based anti-aliasing; intermediate.
