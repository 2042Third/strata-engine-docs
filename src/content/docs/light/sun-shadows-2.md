---
id: light/sun-shadows-2
title: "Sun shadows II: the soft shadow of a real sun"
description: "How Strata softens the sun's shadow by the sun's real size, classifies lit and umbra from depth ranges, and gives the same image in every frame."
kind: internals
size: XL
tracks: [E]
needs: [light/sun-shadows-1, basics/signals]
time: 100
learn:
  - id: compute-penumbra
    text: compute the penumbra of a sun at a given separation, and the disk radius in texels that filters it
  - id: explain-ranges
    text: explain how the depth range pyramid decides lit and umbra exactly and never misses a thin caster
  - id: trace-pixel
    text: trace the sun's visibility of one opaque pixel and of one transparent pixel from the shadow map to the forward pass
  - id: no-history
    text: explain why the sun's filter uses fixed noise and an explicit comparison level, and which paths change together
  - id: contact-off
    text: name what contact shadows add, what they ignore, and why no preset enables them
status: final
since: 0.7.0
---

Stand a pencil on a sheet of paper in the sun. Where the pencil touches the paper, its shadow is sharp. Lift the pencil a hand's width, and the shadow grows blurred. The sun is not a point: it is a disk in the sky, and the farther a shadow lies from its caster, the more of that disk the paper sees around the edge.

This page is about the part of Strata that draws that effect for the sun. It softens each shadow edge by the width the sun's real size gives it. It decides, from a small table of depths, which pixels need no filtering at all. It runs once per pixel, writes a mask that the lit pass reads, and gives the same picture in every frame, so a still view looks the same with and without temporal anti-aliasing. It does not choose the cascades (that is [Sun shadows I](../light/sun-shadows-1.md)), draw the shadows of point and spot lights ([local shadows](../light/local-shadows.md)) or shape the sun's highlight ([area lights](../light/area-lights.md)).

## The problem and how engines solve it

A :term[shadow map]{id=shadow-map} stores, for each texel, the depth of the surface nearest the light. A pixel on the ground compares its own depth with the texel it falls on. The answer is one bit: lit or in shadow. The result is a staircase of hard edges that never looks like the sun's shadow.

To see what the edge should look like, put a roof's edge over a flat floor. A point beyond the roof's shadow sees the whole sun. A point deep under the roof sees none, and a point in between sees part of the disk. The region where the sun is fully hidden is the **umbra**. The region where it is partly hidden is the **penumbra**, and light fills the region outside both.

The width of the penumbra depends on one distance you can measure: the one from the blocker to the receiver, the surface the shadow falls on. A blocker that touches the receiver leaves almost no penumbra. A blocker far above it leaves a wide one.

**Contact hardening** is the way a shadow grows sharper toward the point where its caster and its receiver meet.

Engines have used four families of answers.

1. Fixed percentage-closer filtering (:term[PCF]{id=pcf}) compares the receiver with several texels around its own and averages the answers. The window has one size everywhere, so every edge gets the same softness. Shadows at the contact come out too soft, shadows far from it too hard, and a wide window costs many reads.
2. Percentage-closer soft shadows (PCSS) search a region of the shadow map for surfaces that block the light, average their depths, turn the distance to the receiver into a window width and filter with that window. The method dates from 2005. Each pixel pays for a search and a filter, and the result is noisy where the filter takes few taps.
3. Moment-based maps (variance, exponential and moment shadow maps) store functions of depth that blur like a picture, so one blur serves a whole shadow. They need more memory and precision, and they can leak light where two casters overlap.
4. Ray-traced shadows shoot rays toward random points of the sun's disk. The answer is exact in the limit, but it needs an acceleration structure for the scene and a filter that removes the noise of few rays.

A number shows how far a fixed window is off. Take a window of 3 texels of 10 mm: it is 30 mm wide. That matches the sun's penumbra only for a blocker 3.2 m away. At 0.5 m the real penumbra is 4.6 mm, so the window makes it 6.5 times too soft. At 8 m the real penumbra is 74 mm, and the window makes it 2.5 times too hard.

Strata took the second family and added to it. Its **PCSS** filter is sized by the sun's real angular size, so the penumbra is as wide as physics makes it. A table of depth ranges decides lit and umbra exactly before any filter runs, so most pixels pay a few table reads and no filter taps. The noise that turns the filter is fixed per pixel, never per frame, so nothing depends on history. The [Alternatives table](#alternatives-strata-did-not-choose) lists what each other family would give and cost.

## The map

Five programs and one rule set make the sun's soft shadow. The pass that draws the cascades' shadow map ends with a compute pass that builds the depth ranges. After the :term[depth prepass]{id=depth-prepass}, a fullscreen pass runs the filter once for every opaque pixel and writes a mask. Two blur passes then smooth where the mask asks, and the lit pass reads the mask. Transparent surfaces skip the mask and call the same filter themselves.

```mermaid caption="From the shadow map to the lit pass: the ranges, the mask, its blur and the two ways a surface reads the sun's shadow." alt="A flow chart. The shadow map feeds the depth ranges. The depth prepass and the ranges feed the mask. The mask goes through a horizontal and a vertical blur into the lit pass for opaque surfaces. Transparent surfaces call the filter directly."
flowchart LR
  Map["Shadow map layers (GPU.Shadows)"] --> Ranges["ShadowRanges.comp: depth ranges"]
  Ranges --> Mask["ScreenShadows.frag: filter per opaque pixel (GPU.ScreenShadows)"]
  Prepass["Depth prepass: depth and normal"] --> Mask
  Mask --> Contact["ContactShadows.frag (Custom only)"]
  Mask --> BlurH["ScreenShadowsBlur.frag: horizontal"]
  Contact --> BlurH
  BlurH --> BlurV["ScreenShadowsBlur.frag: vertical"]
  BlurV --> Opaque["Forward.frag, opaque: reads SRV 28"]
  Ranges --> Transparent["Forward.frag, transparent: SampleDirectionalShadow"]
```

The :term[main thread]{id=main-thread} records every command of this chain, in `Strata/src/Strata/Renderer/SceneRendererScreenShadows.cpp` and the shadow code of `Strata/src/Strata/Renderer/SceneRenderer.cpp`. The :term[graphics processing unit]{id=gpu} (GPU) runs them. No thread reads a result back, so nothing the main thread decides depends on what the filter found.

The :term[shaders]{id=shader} live in `Strata/shaders/Include/Shadows.slang` (the filter), `Strata/shaders/Scene/ShadowRanges.comp.slang` (the ranges) and `Strata/shaders/Effects/` (the mask, its blur and the contact pass). The whole chain exists only for a frame with a shadowed sun.

## The contract

Code that touches this chain keeps six rules. Each has a reason, and a reader who changes the filter breaks one of them first.

1. The filter is the same in every frame. Its only noise is a 64 by 64 tile of :term[blue noise]{id=blue-noise} indexed by the pixel. A frame counter, or a value that turns each frame, would make a still image flicker, and temporal anti-aliasing would have to repair it with history.
2. The ranges round outward. A cell's nearest depth rounds up and its farthest rounds down. The classification then holds for every texel of the cell, so a caster one texel wide is never missed.
3. Comparisons take an explicit level. The filter returns early, so neighbouring :term[invocations]{id=thread-gpu} of the shader take different branches: the sun is shaded in non-uniform flow. `SampleCmpLevelZero` needs no gradients and costs less.
4. Both paths change together. Opaque pixels read the mask, and transparent pixels call `SampleDirectionalShadow`. If one path changes and the other does not, glass differs from the wall behind it.
5. Contact shadows are Custom only. No preset enables them, because their hits shimmer in motion.
6. Nothing is read back. The sun's filter never uses `TemporalParams.z`, and the mask has no history texture.

:::rule
The sun's filter uses fixed noise and never reads `TemporalParams.z`. Opaque surfaces take the sun's shadow from the screen-space mask and transparent ones from `SampleDirectionalShadow`, so a change to one path needs the same change in the other. The reason is that a still view must not change from frame to frame, and that the two paths must agree. See [temporal anti-aliasing](../image/taa.md) for what history costs.
:::

:::why
Fragment shaders that shade lights in non-uniform flow compare shadow maps with an explicit level (`SampleCmpLevelZero`). The reason is that zero gradients made the evaluation cost 2.2 to 2.4 times as much as an explicit level. See [compute shaders](../gpu/compute.md) for how invocations that run together share work.
:::

## The geometry of a real sun

The sun's disk, seen from Earth, is 0.53 degrees across. Half of that, 0.265 degrees, is its angular radius $a$: the angle between the line to the disk's center and the line to its edge. Strata stores the diameter and the shader works with the radius.

Take a straight edge of a blocker at height $s$ above a flat receiver. A ground point right under the edge sees half the sun. Move toward the shadow and the edge covers more of the disk; move the other way and it covers less. A ray from one edge of the disk that grazes the blocker marks where the sun begins to appear. A ray from the opposite edge marks where it is fully visible.

::figure{id=pcss-geometry}

Each grazing ray leans from the vertical by $a$ at most. Over the height $s$ it moves sideways by $s \tan a$, where $\tan$ is the tangent, the ratio of the sideways distance to the height. Two such rays, one each way, bound the penumbra. Its width is therefore twice that, and a filter that spreads a disk of radius $s \tan a$ around each receiver point reproduces it.

$$
w = 2 \, s \tan a
$$

$w$ is the penumbra's width in metres, $s$ is the separation in metres and $a$ is the sun's angular radius. The shader needs the radius of the filter disk: $r = s \tan a$, half of $w$.

:::example
Take the sun's 0.53 degrees, so $a = 0.265$ degrees and $\tan a = 0.004625$. A roof's edge at 0.5 m gives $w = 2 \times 0.5 \times 0.004625 = 4.6$ mm. At 2 m it gives 18.5 mm, and at 8 m it gives 74 mm. Now widen the sun to 2 degrees, so $a = 1$ degree and $\tan a = 0.017455$: the same three roofs give 17.5 mm, 69.8 mm and 279 mm. The width grows in proportion to the separation and, for small angles, in proportion to the sun's size.

The shadow map's texel size matters too. Take a cascade 40.96 m wide in a 4096 texel map: a texel is 10 mm. The disk's radius in texels is $s \tan a$ over 10 mm. For the 0.53 degree sun the three roofs give 0.23, 0.93 and 3.7 texels. For the 2 degree sun at 2 m the radius is 3.5 texels.
:::

A check at the limits shows that the formula is sound. At $s = 0$ the blocker touches the receiver and the penumbra has no width. At $a = 0$ the sun is a point, the shadow is hard and the filter needs no disk. Both are what the pencil showed.

The measured width of a real edge is often given between the points where a tenth and nine tenths of the sun's light arrive. For a straight edge under a uniform disk that span is $1.374 \, s \tan a$, because the disk's area passes 10 % at $0.687$ of its radius from the center. The tests of the filter measure this span.

## A toy version: PCSS along one line

The toy below shows the idea along a single line of ground. A roof covers all ground left of $x = 0$ at 2 m height. The shadow map holds, per texel of 1 mm, the height of the nearest surface. For a ground point, the toy finds the texels that block the sun, averages their heights, turns that into a disk radius, and filters. It compares three results: a single comparison (hard), the PCSS filter and an exact answer made with 4,000 taps.

A filter along one line cannot spread taps over a disk's area. It spreads them over the disk's width and weights each by the chord of the disk there, which is the same thing.

```cpp sketch="light-sun-shadows-2-toy.cpp"
#include <cmath>
#include <cstdio>

namespace
{
	constexpr double c_TexelSize = 0.001;   // Metres per shadow map texel
	constexpr double c_RoofHeight = 2.0;    // Metres from the roof's edge down to the ground
	constexpr double c_SunRadius = 0.265;   // Degrees: half of the sun's 0.53 degrees across
	constexpr double c_SearchRadius = 0.03; // Metres around the receiver where blockers are searched
	constexpr int c_Taps = 16;
	constexpr double c_Pi = 3.14159265358979323846;

	double TanSunRadius()
	{
		return std::tan(c_SunRadius * c_Pi / 180.0);
	}

	// The shadow map of a roof over everything left of x = 0: the height of the surface nearest the sun, per texel.
	double MapHeight(double x)
	{
		const double centre = (std::floor(x / c_TexelSize) + 0.5) * c_TexelSize;
		return centre < 0.0 ? c_RoofHeight : 0.0;
	}

	// The share of the sun's disk that reaches a ground point: taps spread over the disk's width, each weighted by the chord there.
	double Filter(double x, double radius, int taps)
	{
		double lit = 0.0;
		double total = 0.0;
		for (int tap = 0; tap < taps; tap++)
		{
			const double u = 2.0 * (tap + 0.5) / taps - 1.0;
			const double weight = std::sqrt(1.0 - u * u);
			total += weight;
			if (MapHeight(x + u * radius) <= 0.0)
				lit += weight;
		}
		return lit / total;
	}

	double Hard(double x)
	{
		return MapHeight(x) <= 0.0 ? 1.0 : 0.0;
	}

	// PCSS: find the blockers' mean height, turn it into a disk radius, filter with that disk.
	double Pcss(double x)
	{
		double sum = 0.0;
		int count = 0;
		for (double offset = -c_SearchRadius; offset <= c_SearchRadius; offset += c_TexelSize)
		{
			const double height = MapHeight(x + offset);
			if (height > 0.0)
			{
				sum += height;
				count++;
			}
		}
		if (count == 0)
			return 1.0;
		return Filter(x, sum / count * TanSunRadius(), c_Taps);
	}

	// The metres between the 10 % and the 90 % lit points of a profile.
	double EdgeWidth(double (*profile)(double))
	{
		double low = 0.0;
		double high = 0.0;
		for (double x = -0.05; x < 0.05; x += 0.00005)
		{
			if (low == 0.0 && profile(x) >= 0.1)
				low = x;
			if (high == 0.0 && profile(x) >= 0.9)
				high = x;
		}
		return high - low;
	}

	double Exact(double x)
	{
		return Filter(x, c_RoofHeight * TanSunRadius(), 4000);
	}
}

int main()
{
	std::printf("x (mm)  hard  pcss  exact\n");
	for (int millimetres = -12; millimetres <= 12; millimetres += 3)
	{
		const double x = millimetres * 0.001;
		std::printf("%6d  %4.2f  %4.2f  %5.2f\n", millimetres, Hard(x), Pcss(x), Exact(x));
	}
	std::printf("10-90 %% width: pcss %.1f mm, exact %.1f mm\n", EdgeWidth(Pcss) * 1000.0, EdgeWidth(Exact) * 1000.0);
	std::printf("1.374 s tan(a) = %.1f mm\n", 1.374 * c_RoofHeight * TanSunRadius() * 1000.0);
	return 0;
}
```

```text output-of="light-sun-shadows-2-toy.cpp"
x (mm)  hard  pcss  exact
   -12  0.00  0.00   0.00
    -9  0.00  0.00   0.00
    -6  0.00  0.13   0.12
    -3  0.00  0.27   0.30
     0  1.00  0.50   0.50
     3  1.00  0.73   0.70
     6  1.00  0.87   0.88
     9  1.00  1.00   1.00
    12  1.00  1.00   1.00
10-90 % width: pcss 12.7 mm, exact 12.7 mm
1.374 s tan(a) = 12.7 mm
```

1. **Lines 19–23:** the shadow map, one height per texel of 1 mm.
2. **Lines 32–35:** each tap sits at a place across the disk and counts by the chord of the disk there.
3. **Lines 49–59:** the search averages the heights of the texels that block.
4. **Lines 60–62:** with no blocking texel the point is lit; otherwise the average height times the tangent is the disk's radius.

The three columns agree where it matters. The hard edge jumps from 0 to 1 within 1 mm. The PCSS column rises from 0 to 1 over about 18 mm of ground, the full penumbra, and the exact column matches it. The measured 10 to 90 % width is close to the $1.374 \, s \tan a$ of the last section.

The toy omits what a pixel of a real frame needs. The table lists each gap and the reason the real code closes it.

| The toy | The real code | Why |
| --- | --- | --- |
| One line of ground | A disk in two dimensions | A shadow edge can run in any direction |
| Height as depth | Reversed depth, biases and a receiver plane | Receivers tilt, and a flat comparison shadows a slope with itself |
| A search over every texel | A search over cells of the depth range pyramid | A few table reads replace hundreds of texel reads |
| Taps weighted by the chord | Taps spread evenly over the disk's area | The same average without a weight per tap |
| One filter | A tent below a texel, a disk above, faded between | Narrow edges stay smooth, and no result jumps |
| No noise | A fixed blue-noise turn per pixel | The pattern of the taps is hidden without history |

## The real code: the depth ranges

PCSS filters each pixel with a search and many taps. Most pixels of a scene are fully lit or deep in an umbra, and need neither. A **depth range pyramid** is a table made from the shadow map: each of its cells holds the nearest and the farthest depth of a square of texels. Strata builds it with cells of 4, 8 and 16 texels on a side, right after the cascades' layers are drawn.

Depth in Strata is reversed: the nearest to the light has the largest value. The table stores the largest depth of the square first (its nearest) and the smallest second (its farthest), packed in one 32-bit :term[integer]{id=integer} of 16 bits each. A compute pass makes level 0, and a second variant of the same shader makes each higher level from the four cells below it.

```mermaid caption="The pyramid has three levels. A cell of each level holds the nearest and the farthest depth of the square of texels below it, and a cell of a higher level combines four below." alt="A tree with three rows. The bottom row shows the shadow map's texels. Above it a row of cells of four texels, then a row of cells of eight, then a row of cells of sixteen. Arrows join each cell to the four cells below it."
flowchart BT
  Texels["Shadow map texels"] --> L0["Level 0: cells of 4 x 4 texels"]
  L0 --> L1["Level 1: cells of 8 x 8 texels"]
  L1 --> L2["Level 2: cells of 16 x 16 texels"]
```

The next fence shows the shader's level-0 branch. Note the two values it keeps for each cell, and for the extra lines that round them.

```slang src="Strata/shaders/Scene/ShadowRanges.comp.slang#L47-L70"
#else
float nearestDepth = 0.0;
float farthestDepth = 1.0;
for (int y = 0; y < 4; y++)
{
	for (int x = 0; x < 4; x++)
	{
		float depth = TexelFetch(u_Source, int3(min(int2(texel) * 4 + int2(x, y), last), int(layer)), 0).r;
		nearestDepth = max(nearestDepth, depth);
		farthestDepth = min(farthestDepth, depth);
	}
}
// Rounded outward as UnpackShadowRange (Include/Shadows.slang) reads them back: a product that rounded across a step is
// moved one step further out.
nearestDepth = clamp(nearestDepth, 0.0, 1.0);
farthestDepth = clamp(farthestDepth, 0.0, 1.0);
uint nearest = uint(ceil(nearestDepth * 65535.0));
if (nearest < 65535u && float(nearest) / 65535.0 < nearestDepth)
	nearest++;
uint farthest = uint(floor(farthestDepth * 65535.0));
if (farthest > 0u && float(farthest) / 65535.0 > farthestDepth)
	farthest--;
#endif
o_Destination[int3(texel, layer)] = uint4((nearest << 16u) | farthest, 0u, 0u, 0u);
```

1. **Lines 48–58:** the loop reads 16 depths, keeps the largest and the smallest, and clamps a read past the map's edge to the last texel.
2. **Lines 63–65:** the nearest depth rounds up to a step of 1/65535, and moves one step more if the float division lands below the true depth.
3. **Lines 66–68:** the farthest depth rounds down in the same way. The cell's range now holds every depth in it.
4. **Line 70:** the two integers share one word, the nearest in the high bits.

Rounding outward is the key to what comes next. A range that was too narrow by a :term[rounding error]{id=rounding-error} could say lit where one texel blocks. A range that is too wide can only lead to more filtering, which is always safe. The second variant of the shader, which builds a level from the one below, needs no rounding: the largest nearest and the smallest farthest of four cells are exact.

Counting the memory shows what the table costs. A 4096 texel map has 1024 by 1024 cells at level 0, and each cell is a 4-byte integer, so a layer is 4 MiB. Levels 1 and 2 add a quarter and a sixteenth of that: 5.25 MiB a layer. Five cascades take about 26 MiB. The table belongs to the cascade cache and lives and dies with the shadow map.

## The real code: the filter

`SampleCascadeShadow` in `Strata/shaders/Include/Shadows.slang` gives one cascade's answer for one pixel. It works in six steps, shown in the chart below: find the search region, read the ranges, classify, estimate the penumbra, filter with a tent, and add a disk where the penumbra is wide.

```mermaid caption="The filter's decisions for one pixel: two early exits from the ranges, then a tent for every edge, then a disk only where the penumbra is wider than a texel." alt="A flow chart. Read the cells of the search region. If the nearest depth is behind the receiver, the pixel is lit. If the farthest is in front, it is in umbra. Otherwise estimate the penumbra, filter with four tent taps, and blend in a turned disk of taps where the penumbra is wider than one texel."
flowchart TD
  A["Search region and its cells"] --> B{"Nearest depth behind the receiver?"}
  B -- yes --> L["Lit: return 1"]
  B -- no --> C{"Farthest depth in front of the receiver?"}
  C -- yes --> U["Umbra: return 0"]
  C -- no --> D["Blockers' mean distance gives the penumbra's radius"]
  D --> E["Tent: four taps"]
  E --> F{"Radius over one texel?"}
  F -- no --> R["Visibility from the tent"]
  F -- yes --> G["Disk of 8 to 32 taps, turned per pixel, blended with the tent"]
  G --> R
```

Two details come before the search. The lookup position moves off the surface along its normal by one and a half texels, and the receiver's depth gains a bias of one texel. Both avoid acne, the false self-shadowing of a surface by its own texels. A receiver that tilts away from the light has depths that change across the filter's footprint, so a tap one texel aside sees a surface deeper than the pixel's own. A flat comparison would shadow the slope with itself.

`ReceiverDepthGradient` takes the slope from the normal, and every tap moves its reference depth by the slope's change at its offset. The search distance limits the change, so a plane almost along the light, where the slope grows without bound, cannot move a comparison far.

The first part picks the search region. Its half-width is the penumbra's radius for a blocker at the search distance, which is $5 + 0.3 d$ metres for a receiver at view depth $d$. The region is clamped to 31 texels. The code then takes the coarsest level whose cells keep the region within a few cells, and loops over those cells. Note how each cell updates `nearest` and `farthest`, and how it adds to `blockerSum`.

```slang src="Strata/shaders/Include/Shadows.slang#L171-L207"
float searchTexels = min(u_Frame.ShadowParams.x * searchDistance / worldPerTexel, c_MaxShadowSearchTexels);
float regionTexels = max(searchTexels, 1.5) + 1.0;
int level = regionTexels <= 8.0 ? 0 : (regionTexels <= 16.0 ? 1 : 2);
float cellSize = float(4 << level);
int2 lastLevelCell = TextureSize(u_ShadowRanges, level).xy - 1;
int2 firstCell = clamp(int2(floor((texelPosition - regionTexels) / cellSize)), int2(0), lastLevelCell);
int2 lastCell = clamp(int2(floor((texelPosition + regionTexels) / cellSize)), int2(0), lastLevelCell);

// Every comparison below reads texels inside these cells against a reference within receiverDepth +- spread, and the
// ranges are rounded outward: a region whose nearest depth is at most the lowest reference is lit, one whose farthest is
// beyond the highest is in umbra, exactly. A caster of any thinness inside raises the nearest depth: never missed.
float spread = min(slope * regionTexels, maxCorrection);
float cellSpread = min(slope * cellSize * 0.5, maxCorrection);
float nearest = 0.0;
float farthest = 1.0;
float blockerSum = 0.0;
float blockerWeight = 0.0;
for (int cellY = firstCell.y; cellY <= lastCell.y; cellY++)
{
	for (int cellX = firstCell.x; cellX <= lastCell.x; cellX++)
	{
		float2 range = UnpackShadowRange(u_ShadowRanges.Load(int4(int3(cellX, cellY, cascade), level)).r);
		nearest = max(nearest, range.x);
		farthest = min(farthest, range.y);
		// A cell blocks where its nearest depth is nearer than the receiver plane anywhere over it; its weight is its overlap
		// with the search square, which changes continuously as the receiver moves (no jumps as cells enter the region).
		float2 cellMin = float2(cellX, cellY) * cellSize;
		float cellReference = receiverDepth + clamp(dot(depthPerTexel, cellMin + 0.5 * cellSize - texelPosition), -maxCorrection, maxCorrection) + cellSpread;
		if (range.x > cellReference)
		{
			float2 overlap = clamp(min(cellMin + cellSize, texelPosition + searchTexels) - max(cellMin, texelPosition - searchTexels), 0.0, cellSize) / cellSize;
			float weight = overlap.x * overlap.y;
			blockerSum += weight * (range.x - cellReference);
			blockerWeight += weight;
		}
	}
}
```

1. **Lines 171–177:** the search region in texels picks level 0, 1 or 2, so cells of 4, 8 or 16 texels, and the first and last cell in each direction.
2. **Lines 182–183:** `spread` is how far the receiver's own plane can change its depth over the region. A tilted receiver compares against a range of depths, not one.
3. **Lines 193–194:** the nearest over all cells is the largest of their nearest depths, and the farthest the smallest of theirs.
4. **Lines 197–205:** a cell whose nearest depth lies in front of the receiver is a blocker, weighted by how much of the search square it covers, so the estimate changes smoothly as the receiver moves.

:::example
Take a pixel 20 m from the camera in a cascade of 10 mm texels. The search distance is $5 + 0.3 \times 20 = 11$ m, so the search radius is $0.004625 \times 11 / 0.01 = 5.1$ texels. The region adds one texel for the bilinear footprint: 6.1 texels, at most 8, so the pixel reads level 0, cells of 4 texels. The region is 12.2 texels wide, so the loop reads at most 5 cells in a row, 25 reads at most. Without the table the same region holds about 150 texels, and a full search would read each.

Now widen the sun to 2 degrees. The radius becomes $0.017455 \times 11 / 0.01 = 19.2$ texels and the region 20.2. That is over 16, so the pixel reads level 2, cells of 16 texels, and the loop reads at most 4 cells in a row. The level grows with the region, and the reads stay at 25 or fewer.
:::

The search distance depends on the view depth only, and it is the same in every cascade. A pixel in the band where two cascades blend therefore searches the same distance in both, and the two answers can be mixed without a seam.

The second part uses the ranges. If even the nearest texel of the region lies behind the receiver by more than the spread, nothing blocks, and the pixel is lit. If even the farthest texel lies in front of the receiver by more than the spread, every texel blocks, and the pixel is in umbra. A one-texel pole in the region raises the nearest depth, so the first test cannot pass: the thin caster is never missed. Then the penumbra follows from the mean distance of the blocking cells.

```slang src="Strata/shaders/Include/Shadows.slang#L208-L224"
if (nearest <= receiverDepth - spread)
	return result; // Lit
if (farthest > receiverDepth + spread)
{
	result.Visibility = 0.0; // Umbra
	return result;
}

// The penumbra's half-width from the blockers' mean distance (biased toward wider by at most a cell's depth spread):
// a straight edge under a disk of angular radius a falls from lit to shadow over 2 s tan(a), which filtering with a disk
// of radius s tan(a) reproduces. No blocker weight (a softness of 0, or blockers only beside the search square): none.
float penumbraTexels = 0.0;
if (blockerWeight > 0.0)
{
	float separation = blockerSum / blockerWeight * depthRange;
	penumbraTexels = min(separation * u_Frame.ShadowParams.x / worldPerTexel, searchTexels);
}
```

1. **Lines 208–209:** the early exit for light.
2. **Lines 210–214:** the early exit for umbra.
3. **Lines 222–223:** `separation` is the mean blocker distance in metres. Multiplied by $\tan a$, which is `u_Frame.ShadowParams.x`, and divided by the texel size it is the disk's radius in texels, capped by the search.

The third part filters. Four taps of the hardware's bilinear comparison sit at plus and minus half a texel. Each is already an average of four texels, so together they make a ramp that is flat over one texel and fades over three. It is the **tent filter**, a small fixed blur that makes every edge smooth, narrow or not. Where the radius from the last step exceeds one texel, a disk of taps takes over, turned per pixel.

The disk is a Vogel pattern: tap $i$ of $N$ sits at the distance $r\sqrt{(i + 0.5)/N}$ from the center, and each tap turns by the golden angle, 2.39996 :term[radians]{id=radian} or 137.5 degrees, from the one before. The square root spreads the taps evenly over the disk's area. For $N = 8$ the first tap lies at 0.25 of the radius and the last at 0.97 of it. A fixed blue-noise tile gives the whole pattern a starting turn that depends on the pixel and on nothing else.

```slang src="Strata/shaders/Include/Shadows.slang#L228-L256"
float tent = 0.0;
for (int tap = 0; tap < 4; tap++)
{
	float2 offset = float2((tap & 1) == 0 ? -0.5 : 0.5, (tap & 2) == 0 ? -0.5 : 0.5);
	float reference = receiverDepth + clamp(dot(depthPerTexel, offset), -maxCorrection, maxCorrection);
	tent += 0.25 * CompareShadowMap(cascade, uv + offset * texelSize, reference);
}
float shadowed = tent;

// Wider penumbrae: a Vogel disk (taps at radii sqrt((i + 0.5) / N), turned by the golden angle) turned per pixel by the
// blue-noise tile, faded in from 1 to 2 texels of radius so the result stays continuous.
float diskWeight = clamp(penumbraTexels - 1.0, 0.0, 1.0);
if (diskWeight > 0.0)
{
	int taps = max(int(u_Frame.ShadowBias.z), 1);
	float turn = TWO_PI * BlueNoise(pixel, int2(0));
	float2 direction = float2(cos(turn), sin(turn));
	const float2x2 golden = transpose(float2x2(cos(c_GoldenAngle), sin(c_GoldenAngle), -sin(c_GoldenAngle), cos(c_GoldenAngle)));
	float disk = 0.0;
	for (int tap = 0; tap < taps; tap++)
	{
		float2 offset = penumbraTexels * sqrt((float(tap) + 0.5) / float(taps)) * direction;
		float reference = receiverDepth + clamp(dot(depthPerTexel, offset), -maxCorrection, maxCorrection);
		disk += CompareShadowMap(cascade, uv + offset * texelSize, reference);
		direction = mul(golden, direction);
	}
	shadowed = lerp(tent, disk / float(taps), diskWeight);
}
result.Visibility = 1.0 - shadowed;
```

1. **Lines 228–235:** the tent, with a depth reference that follows the receiver's plane at each tap.
2. **Line 239:** `diskWeight` fades the disk in over one texel of radius, from a radius of 1 to 2 texels, so the result has no jump.
3. **Lines 242–244:** the tap count comes from the quality row, and the starting turn from the blue-noise tile at the pixel.
4. **Lines 247–253:** each tap moves along a growing radius and turns by the golden angle.
5. **Line 254:** the final answer mixes the tent and the disk by `diskWeight`.

Each comparison is made by `CompareShadowMap`, which calls `SampleCmpLevelZero`. The filter returns early, so neighbouring invocations of the shader run different code, and an implicit level, which needs the gradients of neighbours, would be undefined there. The function names level 0 by level, not by zero gradients. The texels and weights are the same, because the map has one level. Measured by the engine's developers, sampling with zero gradients made the evaluation cost 2.2 to 2.4 times as much.

The blue-noise tile is made by `Tools/GenerateBlueNoise.py`, which writes a 64 by 64 tile of values with the void-and-cluster method into `Strata/src/Strata/Renderer/BlueNoise.h`. Every :term[byte]{id=byte} value appears 16 times, and `Strata/shaders/Include/BlueNoise.slang` reads the tile with `Load`, shifted by the pixel and wrapped at 64. Nothing in the read turns with the frame.

The rule of this page follows. A still view with a still sun gives the same image in every frame, with and without temporal anti-aliasing. History is not needed to hide the noise, because the noise is the same each frame, and a fixed grain cannot flicker.

The price is that a pixel's grain stays where it is. The `ShadowFilterQuality` row sets the taps: the four presets take 8, 16, 24 and 32, the cheapest first. On opaque surfaces the blur of the mask, which the next section describes, smooths the grain that few taps leave. In the second pair below, 8 and 32 taps give the same smooth edge without anti-aliasing.

::compare{id=penumbra-poles}

::compare{id=disk-taps}

## The real code: the screen-space mask

The filter is costly, and the lit pass shades each pixel of each overlapping triangle. Running the filter there would pay it again for every covered pixel. Strata runs it once per visible pixel instead. The **screen-space shadow mask** is a texture the size of the frame in which each opaque pixel holds the sun's visibility, found after the depth prepass from its depth and its geometric normal.

The pass `ScreenShadows.frag` reads the depth, rebuilds the position the lit pass would shade, decodes the normal from its octahedral form (a direction stored in two numbers) and calls `EvaluateDirectionalShadow`. It writes two channels of an 8-bit target. Red is the square root of the visibility. Green is a blur radius.

The square root spends the 8 bits where a step would show. With plain bits the smallest visibility above zero is 1/255, or 0.0039, and the step from there to zero is a visible line at the edge of an umbra. With the square root, the code 1 stands for $(1/255)^2 = 0.000015$ and code 2 for 0.00006, so the lowest steps are 260 times smaller. The lit pass squares the red value to undo it.

```slang src="Strata/shaders/Effects/ScreenShadows.frag.slang#L69-L91"
ShadowSample shadow = EvaluateDirectionalShadow(position, normal, viewDepth, pixel);
float blur = 0.0;
bool partlyLit = shadow.Visibility > 0.0 && shadow.Visibility < 1.0;
if (shadow.Cascade >= 0 && (shadow.DiskWeight > 0.0 || partlyLit))
{
	float pixelWorld = 2.0 * (u_Frame.CameraForward.w > 0.5 ? 1.0 : viewDepth) / (u_Frame.Projection[1][1] * u_Frame.ViewportSize.y);
	float worldPerTexel = u_Cascades[shadow.Cascade].Parameters.x;
	if (shadow.DiskWeight > 0.0)
	{
		float radiusPixels = shadow.PenumbraTexels * worldPerTexel / pixelWorld;
		blur = clamp(0.35 * radiusPixels * shadow.DiskWeight, 1.0, c_ScreenShadowMaxBlurPixels);
	}
	// On a receiver the light grazes, the tent's edges show the texels' stair steps (saw teeth) once the stretched texels
	// cover more than c_StairTexelPixels: the edge's partly lit pixels take a radius of a texel's footprint, which the blur
	// keeps on the receiver's plane. (Lit ground often takes the tent too: only edges pay.)
	if (partlyLit && abs(dot(normal, u_Frame.DirectionalLightDirection.xyz)) < c_StairFacing)
	{
		float texelPixels = ReceiverTexelPixels(position, normal, worldPerTexel, pixelWorld);
		if (texelPixels > c_StairTexelPixels)
			blur = max(blur, min(texelPixels, c_StairMaxBlurPixels));
	}
}
o_Mask = float2(sqrt(clamp(shadow.Visibility, 0.0, 1.0)), blur / c_ScreenShadowMaxBlurPixels);
```

1. **Line 69:** the same function that transparent surfaces call, here at the opaque pixel.
2. **Lines 76–80:** where the disk filtered, the radius is 0.35 of the penumbra's half-width in pixels, from 1 to 8 pixels. That takes the disk's grain without widening the penumbra by more than about 6 %.
3. **Lines 84–89:** the stair-step radius, explained below, takes the larger of the two.
4. **Line 91:** the output: the square root of the visibility, and the radius over its maximum of 8 pixels.

:::example
A pixel on the ground 5 m from the camera has a penumbra radius of 3.7 texels in a cascade with 10 mm texels. One pixel covers 3 mm of ground there. The radius is $3.7 \times 10 / 3 = 12.3$ pixels, and the blur gets $0.35 \times 12.3 = 4.3$ pixels. The pass writes $4.3 / 8 = 0.54$ in the green channel, and the blur reads it back as a radius of 4.3 pixels. A pixel in umbra writes a radius of 0 and is left alone.
:::

The mask is blurred where its green channel asks. An **edge-aware blur**, also called a bilateral filter, averages neighbours but weights each by how much it belongs to the same surface, so the average never crosses an edge. Here a neighbour counts by its distance from the pixel's own plane and by how alike its normal is. The blur passes run along one direction at a time, first horizontally and then vertically, from target A to B and back to A.

```mermaid caption="The mask's passes. The filter writes target A, or target B when the contact pass runs, which marches from B into A. Two blur passes then move the result from A to B and back." alt="A flow chart of four boxes in a row. The filter writes target A, the horizontal blur reads A and writes B, the vertical blur reads B and writes A, and the lit pass reads A. A dashed box for contact shadows sits between the filter and the first blur."
flowchart LR
  F["Filter at every opaque pixel"] --> A1["Target A: root of visibility, radius"]
  A1 -.-> C["Contact pass, when asked: B into A"]
  A1 --> H["Blur horizontally: A to B"]
  C -.-> H
  H --> V["Blur vertically: B to A"]
  V --> Lit["Lit pass reads A, SRV 28"]
```

The next fence is the end of the blur shader. Note the three factors of a neighbour's weight, and for the line that undoes the encoding before the average.

```slang src="Strata/shaders/Effects/ScreenShadowsBlur.frag.slang#L88-L99"
	float facing = max(dot(normal, NormalAt(other)), 0.0);
	facing *= facing;
	facing *= facing;
	facing *= facing; // The eighth power
	float weight = exp(-offset * offset / (2.0 * sigma * sigma)) * onPlane * facing;
	if (weight <= 0.0)
		continue;
	float encoded = u_Source.Load(int3(other, 0)).r;
	visibilitySum += weight * encoded * encoded;
	weightSum += weight;
}
o_Mask = float2(sqrt(clamp(visibilitySum / weightSum, 0.0, 1.0)), center.g);
```

1. **Lines 88–91:** the normal weight is the :term[cosine]{id=cosine} between the two normals raised to the eighth power, so a neighbour on another face counts for almost nothing.
2. **Line 92:** the weight is a Gaussian of the tap's offset, times the plane weight `onPlane` (computed above this quote) and the normal weight.
3. **Lines 95–97:** the average runs over visibility, not over its square root, so the encoding does not bias it.
4. **Line 99:** the result returns to the encoding, with the radius passed on.

A pixel whose radius is below half a pixel keeps its value. Its Gaussian has $\sigma = \max(0.5 r, 0.5)$ and at most 8 taps each side. The plane weight uses the tap's distance from the pixel's plane, in proportion to the view distance. A grazing floor keeps its weight. Another surface a percent of the distance away gets none, so no light crosses a silhouette.

A third use of the radius needs care. Where the sun grazes a receiver, at under 30 degrees to its plane, one shadow map texel covers many pixels, and the tent leaves a hard edge showing the texels as saw teeth. The function `ReceiverTexelPixels` in the pass computes how many pixels one texel covers at most, accounting for the light's angle, which can stretch a texel up to 20 times. If the edge is partly lit and that number is above 1.5 pixels, the pixel takes a blur radius of that footprint, at most 4 pixels. Only pixels at edges pay, because lit ground leaves the pass early with no radius.

The drawing below shows such an edge, with texels of 6 by 3 pixels, before and after the blur.

::figure{id=stair-step-blur}

:::why
The mask moves the filter from the lit pass, which shades every covered pixel of every triangle, to one pass over the visible pixels. The price is two targets of two 8-bit channels, about 8 MB at 1920 by 1080, and a pass that needs the depth prepass.

The engine's developers measured the screen shadows stage on a reference machine. At 3840 by 2160 in the High preset of version 0.7.0, which drew contact shadows, it took 0.35 to 0.52 ms. At 1920 by 1080 in the middle preset it took 0.06 to 0.10 ms. The lit pass lost the filter's cost in exchange.
:::

## The real code: contact shadows and transparent receivers

A shadow map cannot show a shadow smaller than a texel. A 5 cm plate lying on a floor, a foot on the ground, the gap under a stone: all lie between texels. **Contact shadows** are a second, screen-space estimate for what the cascades are too coarse to show. For each pixel the sun still reaches, a short march goes toward the sun over the depth of the prepass. If a step ends a little behind a surface the :term[depth buffer]{id=depth-buffer} holds, that surface is between the pixel and the sun, and the pixel is darkened.

Three properties follow from using the depth buffer. It sees every opaque pixel on the screen, whether or not its mesh has `CastShadows` set, because the depth buffer has no such flag. It sees nothing off screen or behind another surface. And its hits depend on where a step lands in a thin shell behind a surface, which is close to chance, so a hit can come and go as the camera moves.

The :term[renderer]{id=renderer} sets the row `ContactShadows` to 0 in all four presets, and a Custom setting may ask for 0 or 4 to 32 steps. The light's `ContactShadowLength` (0 to 2 m, 0.3 by default) is the reach of the march, shortened so that on screen it never reaches farther than a twentieth of the image's height. A light with length 0 disables them for itself.

::compare{id=contact-shadows}

Transparent surfaces, such as glass, are not in the depth prepass, so they have no mask pixel. The transparent variants of the lit shader call the filter per pixel, with no blur and no contact shadows, and the opaque variants read the mask.

```slang src="Strata/shaders/Scene/Forward.frag.slang#L303-L313"
if (u_Frame.ShadowParams.w > 0.0)
{
#ifdef ST_FORWARD_TRANSPARENT
	// Transparent surfaces are not in the prepass: the same filter, per pixel (no blur, no contact shadows).
	float3 geometricNormal = normalize(v_Normal) * (st_FrontFacing ? 1.0 : -1.0);
	shadow = SampleDirectionalShadow(v_RelativePosition, geometricNormal, viewDepth, st_FragCoord.xy);
#else
	float encoded = u_ScreenShadows.Load(int3(int2(st_FragCoord.xy), 0)).r;
	shadow = encoded * encoded;
#endif
}
```

1. **Lines 305–308:** the transparent variants call `SampleDirectionalShadow` with the geometric normal, flipped for a back face.
2. **Lines 310–311:** the opaque variants read the red channel at `SRV 28` and square it.

:::example
Follow one opaque pixel and one sheet of glass over the same ground. The ground pixel is in the prepass, so the mask pass calls `EvaluateDirectionalShadow` once with its depth and normal. The blur may smooth the result, and the lit pass reads the red channel at `SRV 28` and squares it.

The glass is not in the prepass. Its lit variant calls `SampleDirectionalShadow` itself with its position and normal. The visibility it gets may carry the disk's grain, with no blur and no contact march. Both paths use the same filter, so a change to it reaches both.
:::

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Fixed :term[PCF]{id=pcf} window | The usual baseline of shadow mapping | The lowest cost and the simplest code | The same softness at contact and far away, so no contact hardening |
| Variance and exponential shadow maps | Published in 2006 (variance) and 2008 (exponential); see Further reading | A filter once per map, so wide softness at a small cost per pixel | Light leaks, more precision and memory, and a blur that does not follow the sun's size |
| Moment shadow maps | Published in 2015; see Further reading | Fewer leaks than variance maps | Four values per texel and a costlier filter |
| Ray-traced shadows | Hardware ray-tracing interfaces of current graphics cards | Exact penumbras with no map, no bias and no cascades | An acceleration structure for the scene, a noise filter that needs history, and cards that lack the hardware |
| A fixed disk with no search | Simple engines | No blocker search | A penumbra of one width, so shadows far from their casters stay too sharp |

The noise filter row matters most for this page. Strata's rule that nothing depends on the frame excludes a method whose cleanliness depends on history.

## How it is tested

The suites need a GPU and share one device. The filter's suite is `GPU.SceneRenderer.ShadowFilter` in `StrataTests/src/Renderer/GPUSceneShadowFilterTests.cpp`:

- `A 0.53 degree sun's penumbra is as wide as the sun makes it` measures a plate's shadow edge against $2 t_{10} s \tan a$ with $t_{10} = 0.687$ and requires a match within 20 %, then checks a 1 degree sun is 1.89 times as wide.
- `A still frame's shadow does not change with the TAA frame` checks that the image is the same at every history index.
- `A thin caster's shadow is never lost to the search` checks the classification.
- `Narrow penumbrae are smooth and the same at every pixel` checks the tent.
- `The cascades' depth ranges hold every texel's depth` reads back the table and compares it with the map.
- `Contacts recede at most 2.5 texels` bounds the offsets of the receiver and the biases.

`GPU.SceneRenderer.ScreenShadows` checks that opaque surfaces take the mask where it is not blurred and that the blur never crosses a silhouette. It also checks that wide penumbras have no grain without anti-aliasing and that a grazed receiver shows no stair steps.

`GPU.SceneRenderer.ContactShadows` checks the plate, the fade and the absence of grain, and has the test `No preset draws contact shadows`. The metrics `ScreenShadows4KHigh` and `ScreenShadows4KMedium` of the `PerfGPU.Renderer` suite time the screen shadows stage on 100,000 shadowed cubes against budgets.

CTest runs every GPU suite together in one test, `ctest --preset windows-debug -R StrataTests.GPU`; to run the filter's suite alone, start the test program with `--test-suite=GPU.SceneRenderer.ShadowFilter`. The perf tests run in Release or :term[Dist]{id=dist} only.

## Changing it safely

The extension points are small. A new input of the filter goes through `FrameConstants` or the quality row, and a new quality row also needs its four preset values and a traits line. A new pass of the chain joins the screen shadows :term[GPU stage]{id=gpu-stage-strata}.

- Keep the noise fixed. A change that reads `TemporalParams.z` or any counter breaks rule 1, and `A still frame's shadow does not change with the TAA frame` fails.
- Keep both paths. If `SampleCascadeShadow` changes what it returns, run the opaque and transparent paths and compare them.
- Keep the rounding outward in the ranges. A change to how nearest and farthest round makes `A thin caster's shadow is never lost to the search` or `The cascades' depth ranges hold every texel's depth` fail.
- Keep the level explicit. A new comparison inside the filter takes `SampleCmpLevelZero` and never an implicit level.
- When a new input changes how casters are drawn, a version that the shadow caches compare must change, and the two ways of drawing casters must agree. That belongs to [Sun shadows I](../light/sun-shadows-1.md).

Before a commit, run `GPU.SceneRenderer.ShadowFilter`, `.ScreenShadows` and `.ContactShadows`, and the perf tests of the stage if the change can alter its cost.

## What went wrong before

Version 0.7.0's two highest presets drew contact shadows, also under meshes whose Cast Shadows was off. The march's hits fall in a thin shell behind a surface, where whether a step lands is close to chance. The noise that spread them was locked to the screen, so the shadows shimmered when the camera moved. Version 0.8.0 set the row to 0 in all four presets. The test `No preset draws contact shadows` keeps it so, and Custom still allows the march.

The second lesson is one of cost. A first version of the comparisons sampled the shadow array with zero gradients, and the evaluation took 2.2 to 2.4 times as long as with an explicit level. The metrics `ScreenShadows4KHigh` and `ScreenShadows4KMedium` of the `PerfGPU.Renderer` suite exist to catch such a change.

## Summary

- The penumbra of a straight edge under the sun is $2 s \tan a$ wide, and a disk of radius $s \tan a$ reproduces it; Strata finds $s$ from the mean distance of the blocking texels near the pixel.
- The depth range pyramid holds the nearest and farthest depth of cells of 4, 8 and 16 texels, rounded outward, so lit and umbra are decided exactly and a thin caster is never missed.
- Each opaque pixel gets the filter once, into the screen-space mask, which an edge-aware blur smooths; the lit pass reads it at `SRV 28`, and transparent surfaces call the filter themselves.
- The filter uses fixed blue noise, an explicit comparison level and no history, so a still view is the same image with and without temporal anti-aliasing.
- Contact shadows come from the depth prepass, ignore `CastShadows`, shimmer in motion, and are on in no preset.

## Check yourself

1. A roof's edge is 1 m over the ground, the sun is 0.53 degrees across and a shadow map texel is 5 mm. Which filter does the receiver under its penumbra get: the tent alone, or the disk too?

   :::answer{tests="compute-penumbra"}
   The radius is $s \tan a = 1 \times 0.004625 = 4.6$ mm, which is 0.93 texels. `diskWeight` is the radius in texels minus 1, clamped to 0 to 1, so it is 0. The tent alone filters the pixel.
   :::

2. Why is the classification exact, where a plain average of depths over the region would not be?

   - (a) The ranges hold the nearest and farthest depth, rounded outward, so one blocking texel always raises the nearest.
   - (b) The ranges hold the mean depth of each cell.
   - (c) The ranges are blurred before they are read.

   :::answer{tests="explain-ranges"}
   (a) is right. A mean of a cell (b) lets one thin pole vanish among many far texels, and a blur (c) spreads it out of existence. The extremes cannot lose it.
   :::

3. Name the two places where an opaque and a transparent pixel get the sun's visibility, and say what each skips.

   :::answer{tests="trace-pixel"}
   The opaque pixel reads the red channel of the mask at `SRV 28`, which was filtered, blurred and perhaps darkened by contact shadows. The transparent pixel calls `SampleDirectionalShadow`, which skips the blur and the contact march.
   :::

4. A colleague adds a random turn from a frame counter to the :term[Vogel disk]{id=vogel-disk} to hide its grain. Which rule breaks, and what do you see in a still view?

   :::answer{tests="no-history"}
   Rule 1: the filter must be the same in every frame. In a still view the grain changes each frame, so the shadow edge flickers, unless temporal anti-aliasing averages it, and then the image depends on history.
   :::

5. Why is `ContactShadows` 0 in all four presets, and what does a mesh with `CastShadows` off do to them?

   :::answer{tests="contact-off"}
   Their hits shimmer in motion, so no preset draws them. The march reads the depth prepass, which has every opaque pixel, so a mesh with `CastShadows` off still casts a contact shadow.
   :::

## Exercises

1. **Basic.** Write a sketch that packs a 4 by 4 cell's range with outward rounding, unpacks it, checks that it holds every depth and classifies three receivers.

   :::answer[Worked solution]{tests="explain-ranges"}
   The sketch finds the largest and smallest depth, rounds the first up and the second down, and packs them as the shader does.

   ```cpp sketch="light-sun-shadows-2-ranges.cpp"
   #include <array>
   #include <cmath>
   #include <cstdint>
   #include <cstdio>

   namespace
   {
   	struct Range
   	{
   		float Nearest; // Toward the sun: the largest depth, because depth is reversed
   		float Farthest;
   	};

   	// Packs a 4 x 4 cell's range into 16 + 16 bits, rounded outward so the range still holds every depth.
   	uint32_t PackRange(const std::array<float, 16>& depths)
   	{
   		float nearest = 0.0f;
   		float farthest = 1.0f;
   		for (const float depth : depths)
   		{
   			nearest = std::fmax(nearest, depth);
   			farthest = std::fmin(farthest, depth);
   		}
   		uint32_t high = static_cast<uint32_t>(std::ceil(nearest * 65535.0f));
   		if (high < 65535u && static_cast<float>(high) / 65535.0f < nearest)
   			high++;
   		uint32_t low = static_cast<uint32_t>(std::floor(farthest * 65535.0f));
   		if (low > 0u && static_cast<float>(low) / 65535.0f > farthest)
   			low--;
   		return (high << 16) | low;
   	}

   	Range UnpackRange(uint32_t packed)
   	{
   		return { static_cast<float>(packed >> 16) / 65535.0f, static_cast<float>(packed & 0xFFFFu) / 65535.0f };
   	}

   	const char* Classify(const Range& range, float receiver)
   	{
   		if (range.Nearest <= receiver)
   			return "lit";
   		if (range.Farthest > receiver)
   			return "umbra";
   		return "needs the filter";
   	}
   }

   int main()
   {
   	std::array<float, 16> depths;
   	depths.fill(0.30f);
   	depths[5] = 0.9137f; // A pole one texel wide, near the sun
   	depths[10] = 0.1234f; // A hole, far from the sun

   	const uint32_t packed = PackRange(depths);
   	const Range range = UnpackRange(packed);
   	bool holds = true;
   	for (const float depth : depths)
   		holds = holds && depth <= range.Nearest && depth >= range.Farthest;

   	std::printf("packed 0x%08X: nearest %.5f, farthest %.5f, holds every depth: %s\n", packed, range.Nearest, range.Farthest, holds ? "yes" : "no");
   	for (const float receiver : { 0.05f, 0.50f, 0.95f })
   		std::printf("receiver %.2f: %s\n", receiver, Classify(range, receiver));
   	return 0;
   }
   ```

   ```text output-of="light-sun-shadows-2-ranges.cpp"
   packed 0xE9E81F97: nearest 0.91371, farthest 0.12340, holds every depth: yes
   receiver 0.05: umbra
   receiver 0.50: needs the filter
   receiver 0.95: lit
   ```

   1. **Lines 21–22:** the extremes of the 16 depths.
   2. **Lines 24–29:** the rounding, with the one-step correction for float error.
   3. **Line 30:** the two 16-bit halves share a word.

   The pole at 0.9137 raises the nearest, so a receiver at 0.50 needs the filter, and one at 0.95 is lit.
   :::

2. **Medium.** Three poles stand 0.5, 2 and 8 m from a wall. Compute the 10 to 90 % width of each shadow edge on the wall for a sun 0.53 degrees across and for one 2 degrees across, using $1.374 \, s \tan a$.

   :::answer[Worked solution]{tests="compute-penumbra"}
   For 0.53 degrees, $\tan a = 0.004625$, so the widths are $1.374 \times 0.5 \times 0.004625 = 3.2$ mm, 12.7 mm and 50.8 mm. For 2 degrees, $\tan a = 0.017455$ and the widths are 12.0 mm, 48.0 mm and 192 mm. The ratio is 3.77 each time, the ratio of the tangents.
   :::

3. **Hard.** Make a debug overlay that shows the pyramid's first level. Say where you would read the table, how you would unpack it, and what it should show.

   :::answer[Worked solution]{tests="explain-ranges"}
   `SceneRenderer::GetShadowRanges` returns the R32_UINT array, bound as `SRV 32` in the scene's sets. A fullscreen pass reads level 0 of the layer of a chosen cascade with `Load` and calls `UnpackShadowRange` from `Strata/shaders/Include/Shadows.slang`. It shows the gap between nearest and farthest as a grey ramp: black for a flat cell, white for a cell holding a tall caster.

   Hook the pass in beside the shadows debug view (`Strata/src/Strata/Renderer/SceneRendererShadowView.cpp`, enabled by `SceneRenderOptions::ShowShadowView`). Wrap the pass in a :term[GPU stage]{id=gpu-stage-strata}. Cells of 4 texels outline the casters at that resolution and show black on open ground.
   :::

4. **Hard.** Trace it yourself: find where an opaque pixel's sun visibility is written and where the lit pass reads it, and where a transparent pixel gets its own.

   :::answer[Worked solution]{tests="trace-pixel"}
   Search for `ScreenShadows`. `Strata/shaders/Effects/ScreenShadows.frag.slang` writes it in `st_Main`, drawn and blurred by `SceneRenderer::RenderScreenShadows` in `Strata/src/Strata/Renderer/SceneRendererScreenShadows.cpp`. The lit pass reads it at `SRV 28` in `Strata/shaders/Scene/Forward.frag.slang`, lines 310 to 311. A transparent pixel calls `SampleDirectionalShadow` at line 308, defined near the end of `Strata/shaders/Include/Shadows.slang`.
   :::

## Where it lives in Strata

- The filter: `Strata/shaders/Include/Shadows.slang` (`SampleCascadeShadow`, `EvaluateDirectionalShadow`, `SampleDirectionalShadow`, `CompareShadowMap`).
- The ranges: `Strata/shaders/Scene/ShadowRanges.comp.slang`, built in `SceneRenderer::BuildShadowRanges` and read through `SceneRenderer::GetShadowRanges`.
- The mask: `Strata/shaders/Effects/ScreenShadows.frag.slang`, `Strata/shaders/Effects/ScreenShadowsBlur.frag.slang`, `Strata/shaders/Effects/ContactShadows.frag.slang` and `SceneRenderer::RenderScreenShadows`.
- The blue-noise tile: `Tools/GenerateBlueNoise.py` and `Strata/shaders/Include/BlueNoise.slang`.
- Settings: the rows `ShadowFilterQuality` and `ContactShadows` of `RendererQualitySettings`, and `DirectionalLightComponent::ShadowSoftness` (Angular Diameter) and `ContactShadowLength`.
- Tests: `GPU.SceneRenderer.ShadowFilter`, `GPU.SceneRenderer.ScreenShadows`, `GPU.SceneRenderer.ContactShadows`, and the metric `ScreenShadows4KHigh` of the `PerfGPU.Renderer` suite.

## Further reading

- Fernando, "Percentage-closer soft shadows" (NVIDIA, SIGGRAPH 2005 sketch): the method this page builds on (intermediate).
- Donnelly and Lauritzen, "Variance shadow maps" (2006): the filterable map (advanced).
- Peters and Klein, "Moment shadow mapping" (2015): the moment-based family (advanced).
- Annen and others, "Exponential shadow maps" (2008): the exponential family (advanced).
- Pharr, Jakob and Humphreys, "Physically Based Rendering": sampling the sun's disk (advanced).
