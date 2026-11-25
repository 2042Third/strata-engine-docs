---
id: light/sun-shadows-1
title: "Sun shadows I: stable cascades"
description: "How Strata covers a view with the sun's shadow maps: fine near the camera, with texels that stay put when the camera moves, and how casters reach them."
kind: internals
size: XL
tracks: [E]
needs: [light/shadow-basics, draw/gpu-driven, draw/occlusion]
time: 100
learn:
  - id: compute-layout
    text: compute the splits, the sphere radius and the texel size of a cascade layout by hand
  - id: explain-stability
    text: explain why lens-only spheres and snapped squares keep shadow texels still while the camera turns and moves
  - id: trace-caster
    text: trace one caster into a cascade's draws on the CPU path and on a GPU-driven frame
  - id: read-shadows-view
    text: find what the shadows debug view and the cascade statistics say about a scene
since: 0.3.0
status: final
---

The sun lights a whole scene, from the grass at your feet to a hill a kilometer away, and its shadows must look sharp wherever you look. One set of **cascaded shadow maps** (CSM) solves this by drawing several :term[shadow maps]{id=shadow-map} of the same sun, each covering a different range of distances from the camera. This page covers the part of Strata that lays those maps out, chooses which objects each map draws and decides which map shades each pixel. Most of the work runs on the :term[graphics processing unit]{id=gpu} (GPU), and the rest on the :term[main thread]{id=main-thread}. The page does not cover the soft filter, the screen-space mask or contact shadows, which the [second page on sun shadows](../light/sun-shadows-2.md) teaches, nor the shadows of point and spot lights.

## The problem and how engines solve it

A shadow map is a picture of the scene seen from the light, and each of its pixels, a texel, stores one depth. A texel has a fixed size in the world. A pixel on your screen has another size, and the two sizes decide how a shadow looks: when one texel covers several screen pixels, the shadow edge shows coarse steps.

Take one sun shadow map of 2048 by 2048 texels that must cover a square of 100 m around the camera. One texel is 100 m divided by 2048, or 4.9 cm. On a screen 1080 rows tall with a 60 degree view, a pixel at 5 m spans 2 × 5 × 0.577 / 1080, or 5.3 mm, with 0.577 the tangent of 30 degrees. A texel is then 9 pixels wide, and every shadow edge near the camera shows steps nine pixels long. A map 4 times larger each way would still leave 2 pixels per texel, at 16 times the memory.

The sun needs fine texels close to the camera, where you see detail, and a long reach, where you see only outlines. The remedy is to draw several maps, each covering more distance with the same number of texels. Each of these maps is a **cascade**: a shadow map of the sun that serves one range of the view.

A **slice** is the part of the view between two distances from the camera that one cascade serves. A cascade near the camera serves a slice a few meters deep, so its texels are small. A cascade far away serves a slice dozens of meters deep, and its texels are large, but the screen shows distant shadows small as well.

A **split** is the view distance where one slice ends and the next begins. A layout of four cascades has four splits, and the last one is the shadow distance, the farthest distance that casts visible shadows.

The measure of success is the **texel density** of a pixel, also called pixels per texel: how many screen pixels a shadow texel spans at that pixel. A value near 1 is as sharp as the screen can show, and 4 or more is visibly coarse. A good layout keeps the density about equal from the nearest slice to the farthest, and the cascades exist to do that.

Engines have tried several ways to reach this goal, and the table compares them.

| Technique | Who uses it | What it costs and gains |
| --- | --- | --- |
| One map for the whole view | Small scenes, early engines | Cheapest; the density is far too coarse near the camera |
| Parallel-split maps: a map for each slice of the :term[view frustum]{id=view-frustum}, fitted to the slice's corners | The standard of most engines since about 2006 | Fine near the camera; the fit follows the camera's turn, so texels move and edges flicker |
| Maps fitted to the receivers (sample-distribution shadow maps) | Research and some games, from 2011 | Tight maps, because a depth :term[readback]{id=readback} shows which depths are in view; the readback arrives frames late and the fit changes with the view |
| Stable cascades, from Valient's 2008 talk | Games that need steady shadows | Spheres and snapping keep texels still; some texels cover parts of the sphere outside the view |
| Virtual shadow maps | Unreal Engine 5 | A huge virtual map with pages made on demand: the finest shadows, with heavy machinery and a large :term[memory pool]{id=memory-pool} |

Strata uses the fourth row. The key fact is that a shadow edge may only move by whole texels. A fitted map moves when the camera turns, because the box around the slice changes. Every texel center then lands in a new place on the shadow edge, and the edge crawls or flickers while nothing in the scene moved.

Three mistakes produce that flicker, and the rest of the page is a defense against each. The first is to size a cascade by the receivers it sees, so that a turn changes the size. The second is to place the square without snapping, so that a step of the camera changes the texel grid. The third is to snap in single precision far from the origin, where a float has too few bits to hold a texel.

:::analogy
A shadow map is a sheet of graph paper laid over the ground. If you slide the sheet by half a square, every line you drew on it now falls across the middle of the squares and looks different. If you slide it only by whole squares, every line falls on the same squares as before.

**Where it breaks:** a real shadow map also has a depth range and a size in texels, and neither of them stays still by sliding alone; the sphere rule below keeps the size fixed.
:::

::figure{id=stable-cascades}

Strata's answer, the stable cascade layout, is defined with the code below. Two pictures show its main idea.

:::elsewhere
Valient (2008, "Stable rendering of cascaded shadow maps") describes the sphere and the snapping used here. Lauritzen and others (2011, "Sample distribution shadow maps") fit each map to the depths a readback finds. Epic's documentation of Unreal Engine 5 describes virtual shadow maps. Strata 0.7.0 used the fitting idea, and the section "What went wrong before" tells why it left it.
:::

## The map

The sun's maps live in one depth texture with an array layer for each cascade. The renderer makes it in the first frame that has a shadowed sun and keeps it when the window changes size. A viewport of zero size, as in a capture renderer between pictures, releases it with the cascades' :term[depth pyramids]{id=hierarchical-z-buffer} and cache. A thumbnail draws one cascade.

Memory is the main cost. Each texel stores a 32-bit depth, so one layer of 8192 by 8192 texels takes 256 MiB, and five layers take 1.25 GiB. The graphics quality tables in [Quality settings](../image/quality-settings.md) list the estimate for every row. A card may refuse the allocation, and the renderer then halves the size each way, down to 1024, until a map fits. Every reader uses the size that fit, and the renderer reports the fallback once, not every frame.

The files and the threads that own the work follow, in the order the data flows.

```mermaid caption="How a frame's cascades are made and used: the layout and the caster search run on the main thread, the fit and the draws on the GPU." alt="Boxes in order: the layout, the squares, the caster search or the GPU culling, the depth fit, the draws into the layers, then the shaders that select a cascade."
flowchart TD
	A["LayOutShadowCascades: GetLayout from the lens, splits and spheres (main thread)"] --> B["FindShadowCasters: GetSquare snaps each square (main thread)"]
	B --> C["CPU path: caster search, GatherShadowDraws"]
	B --> D["GPU-driven path: CullShadow.comp, CullCascades"]
	C --> E["CascadeFit.comp writes u_Cascades"]
	D --> E
	E --> F["Draws into the layers of the D32 array (cached layers skipped)"]
	F --> G["Shaders: SelectShadowCascade, CascadeBlendWeight"]
```

The layout is arithmetic in `Strata/src/Strata/Renderer/ShadowCascades.cpp`, and `SceneRenderer` feeds it. The caster search, which runs on the :term[central processing unit]{id=processor} (CPU) on one path, is in `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp`. The culling is in `Strata/shaders/Scene/Cull.comp.slang`, the depth fit in `Strata/shaders/Scene/CascadeFit.comp.slang` and the selection in `Strata/shaders/Include/Shadows.slang`.

:::caution
The Manual's table of cascades per preset lists four cascades at **High** and **Ultra**, and says four 8192 texel cascades take 1 GiB. The code gives five cascades at both, and five layers of 8192 texels take 1.25 GiB. This page takes the code's numbers.
:::

## The contract

Code that touches the cascades follows six rules. Each has a reason, and a broken rule shows as a visible flaw, not as a crash, so the tests below matter.

- The frame's view alone decides the layout. The lens, the camera position, the light direction and the settings go in. Nothing from the last frame and nothing from the :term[GPU]{id=gpu} comes back. The reason is the first-frame promise: a turned camera shows its final shadows at once.
- Layouts come only from `ShadowCascades::GetLayout`, and squares only from `ShadowCascades::GetSquare`. A second place that cuts slices would drift from the first, and the :term[CPU]{id=processor} path, the GPU path and the debug view must agree to the pixel.
- Snapping runs in double precision, in absolute :term[light space]{id=light-space}. A float far from the origin has too few bits to hold a texel, and the grid would drift; [Numbers and precision](../basics/numbers.md) shows why.
- :term[Shaders]{id=shader} select a cascade only with `SelectShadowCascade`, never by depth alone. The section on containment below gives the reason.
- Cascade projections live in `u_Cascades`, which `CascadeFit.comp` writes, and never return to `FrameConstants`. Every shadow reader then reads one buffer, so the two paths cannot disagree about a cascade's depth range.
- Whatever changes how a caster is drawn must also change a version that the shadow caches compare. The section on the cache gives the reason.

:::rule[One function selects, one function lays out]
Every selection of a cascade goes through `SelectShadowCascade`, every layout through `GetLayout`, and snapping happens in double precision in absolute light space. The reason is one source of truth for the slices that the shading, the debug view and the culling share. The [second page on sun shadows](../light/sun-shadows-2.md) shows the filter that reads the same selection.
:::

## A toy version

The toy lays out four cascades for one lens: a 60 degree view, 16:9, a shadow distance of 80 m, a map of 2048 texels and a screen 1080 rows tall. For each cascade it computes the split, the radius of the sphere around the slice and the texel size, and then the texel density at the split. It omits snapping, the fifth cascade, the clamp of the shadow distance and the filter.

Read `GetSplit` first, then `GetSphereRadius`, then `main`, which chains them as the real `GetLayout` does.

```cpp sketch="light-sun-shadows-1-toy.cpp"
// A toy cascade layout: the splits, the sphere around each slice and the texel size, for one lens.
#include <algorithm>
#include <cmath>
#include <cstdio>

constexpr int c_CascadeCount = 4;
constexpr float c_SplitStart = 1.5f;
constexpr float c_MaxFirstSplit = 7.5f;
constexpr float c_ShadowDistance = 80.0f;
constexpr float c_Distribution = 0.9f;
constexpr float c_Blend = 0.1f;
constexpr int c_MapSize = 2048;
constexpr int c_MarginTexels = 68; // Twice the filter's reach of 33 texels plus one snapping texel
constexpr int c_ScreenRows = 1080;

float GetSplit(int index)
{
	if (index + 1 >= c_CascadeCount)
		return c_ShadowDistance;
	const float fraction = static_cast<float>(index + 1) / static_cast<float>(c_CascadeCount);
	const float logarithmic = c_SplitStart * std::pow(c_ShadowDistance / c_SplitStart, fraction);
	const float uniform = c_SplitStart + (c_ShadowDistance - c_SplitStart) * fraction;
	const float split = c_Distribution * logarithmic + (1.0f - c_Distribution) * uniform;
	return index == 0 ? std::min(split, c_MaxFirstSplit) : split;
}

// The radius of the smallest sphere around the slice [sliceNear, sliceFar] of a 60 degree, 16:9 view.
float GetSphereRadius(float sliceNear, float sliceFar)
{
	const float tanHalf = std::tan(0.5f * 3.14159265f / 3.0f);
	const float reach = tanHalf * std::sqrt(1.0f + (16.0f / 9.0f) * (16.0f / 9.0f));
	const float nearHalf = reach * sliceNear;
	const float farHalf = reach * sliceFar;
	// The sphere's center on the view axis, equally far from the near and far corners, or at the far end.
	float center = (sliceFar * sliceFar - sliceNear * sliceNear + farHalf * farHalf - nearHalf * nearHalf) / (2.0f * (sliceFar - sliceNear));
	center = std::clamp(center, sliceNear, sliceFar);
	const float extent = std::max(std::hypot(center - sliceNear, nearHalf), std::hypot(sliceFar - center, farHalf));
	return std::ceil(extent * 16.0f) / 16.0f;
}

int main()
{
	const float tanHalf = std::tan(0.5f * 3.14159265f / 3.0f);
	float sliceNear = 0.1f;
	float previousSplit = 0.0f;
	for (int cascade = 0; cascade < c_CascadeCount; cascade++)
	{
		const float split = GetSplit(cascade);
		const float radius = GetSphereRadius(sliceNear, split);
		const float texel = 2.0f * radius / static_cast<float>(c_MapSize - c_MarginTexels);
		const float pixel = 2.0f * split * tanHalf / static_cast<float>(c_ScreenRows);
		std::printf("cascade %d: %6.2f to %5.2f m, radius %6.3f m, texel %5.2f mm, %.2f pixels per texel\n", cascade, sliceNear, split, radius, texel * 1000.0f, texel / pixel);
		sliceNear = std::max(split - c_Blend * (split - previousSplit), 0.1f);
		previousSplit = split;
	}
	return 0;
}
```

```text output-of="light-sun-shadows-1-toy.cpp"
cascade 0:   0.10 to  5.76 m, radius  6.812 m, texel  6.88 mm, 1.12 pixels per texel
cascade 1:   5.18 to 13.93 m, radius 16.438 m, texel 16.60 mm, 1.11 pixels per texel
cascade 2:  13.12 to 32.68 m, radius 38.500 m, texel 38.89 mm, 1.11 pixels per texel
cascade 3:  30.81 to 80.00 m, radius 94.250 m, texel 95.20 mm, 1.11 pixels per texel
```

1. **Lines 21–24:** the split blends a logarithmic and a uniform series by the distribution, and the first cascade ends at most at 7.5 m.
2. **Lines 35–36:** the sphere's center is where the near and far corners are equally far, or at the far end when that point lies beyond it.
3. **Line 50:** the texel is the sphere's diameter divided by the map's size less the 68 texels of margin.
4. **Line 53:** the next slice starts where the previous cascade's blend band begins.

The first cascade covers the view from 0.1 m to 5.76 m with texels of 6.9 mm, and the last covers 30.8 m to 80 m with texels of 95.2 mm. The last column is the point. Every cascade holds about 1.1 pixels per texel at its far end, so the layout spends its texels evenly over the screen. The sections below build each line of the toy back into the real code and add what the toy omits.

Change the constants and run the toy again to feel the layout. A distribution of 0 gives equal slices, and the first cascade then grows. A longer shadow distance makes every texel coarser, because the same 2048 texels cover more.

## The real code: layout and selection

### Splits

**Stable cascades** are a cascade layout whose sizes depend on the camera's lens alone and whose squares move only by whole texels of a fixed grid. Strata adds one rule that Valient's talk did not need: nothing is read back from the :term[graphics processing unit]{id=gpu} (GPU), so the first frame after a turn already shows the final shadows.

The real code takes its splits from a fixed distance of 1.5 m, not from the near clip of the camera. The reason is a lens that changes. A near clip of 1 cm against one of 10 cm would halve the first split if the splits began at the clip, and every slice would shift. With a fixed start, another near clip moves no split.

Between 1.5 m and the shadow distance, each split blends two series. A logarithmic series makes each slice a fixed ratio longer than the previous one, which matches how the screen shrinks things with distance. A uniform series makes all slices equally long. The light's `CascadeDistribution` is the logarithmic share, 0.9 by default: at 0 the slices are equal, and at 1 the series is purely logarithmic. For four cascades at 80 m the splits are 5.76, 13.93 and 32.68 m, and the last cascade ends at 80 m.

```cpp src="Strata/src/Strata/Renderer/ShadowCascades.cpp#L56-L71"
float GetSplit(const ShadowCascadeView& view, uint32_t index)
{
	const uint32_t count = std::clamp(view.CascadeCount, 1u, RenderData::c_MaxCascades);
	if (index + 1 >= count)
		return view.ShadowDistance;
	// From a fixed distance rather than the near clip, which would move every split with the camera's lens (a near clip of
	// 1 cm against one of 10 cm halves the first split).
	const float rangeNear = std::min(std::max(c_SplitStart, view.Near), 0.5f * view.ShadowDistance);
	const uint32_t nearCascades = count > c_SharedCascades ? count - c_SharedCascades : 0;
	if (index < nearCascades)
		return std::min(rangeNear, GetRadiusLimit(view, c_MaxNearRadius));
	const float distribution = std::isfinite(view.Distribution) ? std::clamp(view.Distribution, 0.0f, 1.0f) : 0.9f;
	const uint32_t shared = index - nearCascades;
	const float split = GetSplit(rangeNear, view.ShadowDistance, distribution, shared, count - nearCascades);
	return shared == 0 ? std::min(split, c_MaxFirstSplit) : split;
}
```

1. **Line 63:** the range starts at the larger of 1.5 m and the near clip, and at most half the shadow distance.
2. **Line 66:** a cascade before the shared series is the near cascade, which ends at 1.5 m or where its sphere reaches the radius limit.
3. **Line 70:** the first split of the shared series never ends beyond 7.5 m.

That cap, `c_MaxFirstSplit`, matters for long shadow distances. Without it, a shadow distance of 200 m puts the first split at 9.7 m. The shadows nearest the camera then have coarse texels, and curved surfaces under a low sun show them as stripes. With the cap the splits at 200 m are 7.5, 25.66 and 68.01 m.

The fifth cascade, at **High** and **Ultra**, is not part of the blend. It covers the view from the near clip to 1.5 m, or to a nearer distance where its sphere would pass a radius of 2 m (`c_MaxNearRadius`). At 8192 texels it reaches texels of about 0.5 mm for what lies within arm's reach. `GetRadiusLimit` finds the distance with a search that halves the range 64 times at most, and it uses the lens alone, so a turn never moves it.

### Spheres

A cascade covers the smallest sphere around its slice, the part of the view frustum between two distances, which has eight corners. The smallest sphere around it has its center on the view axis, where the nearest and farthest corners are equally far. If that point lies beyond the slice, as it does for wide views, the center sits at the far end. At 60 degrees and 16:9 the sphere sits at the far end, and its radius is the far corner's distance from the axis. That distance is 0.577 × the square root of 1 + (16/9) × (16/9), or 1.178 times the split.

```cpp src="Strata/src/Strata/Renderer/ShadowCascades.cpp#L73-L102"
void GetSliceSphere(const ShadowCascadeView& view, float sliceNear, float sliceFar, glm::vec3& center, float& radius)
{
	// The slice is the hull of its eight corners, symmetric about the view axis, so its smallest sphere is centered on the
	// axis where the nearest and farthest corners are equally far, or at the far end where they cannot be (wide views):
	// its size depends on the slice and the lens alone, never on where the camera looks.
	const double a = static_cast<double>(sliceNear);
	const double b = std::max(static_cast<double>(sliceFar), a);
	double nearHalf2 = 0.0; // The squared half-diagonal of the slice's near and far ends
	double farHalf2 = 0.0;
	if (view.Orthographic)
	{
		const double halfHeight = 0.5 * static_cast<double>(view.OrthographicHeight);
		const double halfWidth = halfHeight * static_cast<double>(view.Aspect);
		nearHalf2 = halfHeight * halfHeight + halfWidth * halfWidth;
		farHalf2 = nearHalf2;
	}
	else
	{
		const double tanY = static_cast<double>(view.TanHalfFOV);
		const double reach2 = tanY * tanY * (1.0 + static_cast<double>(view.Aspect) * static_cast<double>(view.Aspect));
		nearHalf2 = reach2 * a * a;
		farHalf2 = reach2 * b * b;
	}
	double z = a;
	if (b > a)
		z = std::clamp((b * b - a * a + farHalf2 - nearHalf2) / (2.0 * (b - a)), a, b);
	const double extent = std::max(std::sqrt((z - a) * (z - a) + nearHalf2), std::sqrt((b - z) * (b - z) + farHalf2));
	center = view.CameraRotation * glm::vec3(0.0f, 0.0f, -static_cast<float>(z));
	radius = static_cast<float>(std::ceil(extent * 16.0) / 16.0);
}
```

1. **Line 98:** the center along the axis is found from the two corner distances, then clamped to the slice.
2. **Line 100:** only here does the camera's turn enter, and only to place the center, never to size it.
3. **Line 101:** the radius rounds up to 1/16 m, so the same lens gives bit-equal sizes in every frame.

Look at what the function reads: the slice, the tangent of half the :term[field of view]{id=field-of-view} and the aspect ratio. A turned camera changes none of them, so every sphere keeps its radius and every texel keeps its size.

Stability has a price. The far face of a slice at 60 degrees and 16:9 is 2.05 times its distance wide and 1.15 times tall, an area of 2.37 times the square of the distance. The square around its sphere is 2.36 times the distance on a side, an area of 5.55. Less than half of the texels near the far end therefore lie inside the view, and the rest wait for the camera to turn.

### Squares, snapping and the filter's margin

The map is a square, and the sphere must fit inside it with room to spare. The square covers the sphere, the reach of the soft filter on each side (33 texels, `c_FilterReachTexels`) and one texel for snapping. The usable part of the map is the map's size less 68 texels, so one texel is the sphere's diameter divided by that number. For the first cascade of a 2048 map the sphere has a radius of 6.8125 m, so the texel is 13.625 m divided by 1980, or 6.9 mm.

```cpp src="Strata/src/Strata/Renderer/ShadowCascades.cpp#L104-L128"
ShadowCascadeLayout GetLayout(const ShadowCascadeView& view)
{
	ShadowCascadeLayout layout;
	const uint32_t count = std::clamp(view.CascadeCount, 1u, RenderData::c_MaxCascades);
	// The square covers the sphere and, beyond it, the filter's reach and the texel the snapping may move it by.
	constexpr uint32_t margin = 2 * (c_FilterReachTexels + 1);
	const double usableTexels = static_cast<double>(std::max(view.MapSize, 2 * margin) - margin);
	const float blend = std::isfinite(view.CascadeBlend) ? std::clamp(view.CascadeBlend, 0.0f, 1.0f) : 0.0f;
	float sliceNear = view.Near;
	float previousSplit = 0.0f;
	for (uint32_t cascade = 0; cascade < count; cascade++)
	{
		// Each cascade blends into the next over the last CascadeBlend of its slice before its split (the first one's measured
		// from the camera, at 0: Include/Shadows.slang, CascadeBlendWeight), so the next slice starts at that band.
		const float split = std::max(GetSplit(view, cascade), sliceNear);
		ShadowCascadeSlice& slice = layout.Cascades[cascade];
		slice.SliceNear = sliceNear;
		slice.SliceFar = split;
		GetSliceSphere(view, sliceNear, split, slice.SphereCenter, slice.Radius);
		slice.WorldPerTexel = 2.0 * static_cast<double>(slice.Radius) / usableTexels;
		sliceNear = std::max(split - blend * (split - previousSplit), view.Near);
		previousSplit = split;
	}
	layout.CascadeCount = count;
	return layout;
```

1. **Line 109:** the margin is twice the filter's reach plus one texel on each side.
2. **Line 123:** the world size of a texel follows from the radius and the usable texels.
3. **Line 124:** the next slice starts where this cascade's blend band begins, so its sphere covers the band.

Each cascade fades into the next over the last `CascadeBlend` of its slice, which is a tenth by default. The next slice therefore starts at the beginning of that band, and its sphere must cover the band too.

The center of the square follows the camera, and `GetSquare` fixes it to a grid. The function finds the sphere's center in the light's coordinates, divides by the texel size, rounds down and multiplies back.

```cpp src="Strata/src/Strata/Renderer/ShadowCascades.cpp#L131-L141"
ShadowCascadeSquare GetSquare(const ShadowCascadeSlice& slice, const glm::dvec3& cameraLight, const glm::dmat3& lightRotation, uint32_t mapSize)
{
	// In absolute light space and double precision, so the texel grid stays put however far the camera is from the origin.
	const glm::dvec3 sphere = cameraLight + lightRotation * glm::dvec3(slice.SphereCenter);
	const double texel = slice.WorldPerTexel;
	ShadowCascadeSquare square;
	square.Center = texel > 0.0 ? glm::floor(glm::dvec2(sphere) / texel) * texel : glm::dvec2(sphere);
	square.HalfSide = 0.5 * texel * static_cast<double>(mapSize);
	square.SphereZ = sphere.z;
	return square;
}
```

1. **Line 134:** the camera's position and the sphere's center are added in double precision, in absolute light space.
2. **Line 137:** the rounding down is the snapping: the center lands on a corner of the texel grid.
3. **Line 138:** half the side is half a texel size times the map's size, so the map's texels are exactly the grid's.

**Texel snapping** is that rounding. The square's center moves only in steps of whole texels, so a texel of the map always covers the same patch of world however far the camera has moved. The work runs in `double` because a float far from the origin cannot hold a step of 7 mm. The second sketch, in an exercise below, shows the effect on one shadow edge.

### Selection by containment

The layout makes the cascades, and the shaders must pick one for each pixel. A simple rule picks the first cascade whose split lies beyond the pixel's view depth. That rule fails at the edges of a square. The :term[normal offset]{id=normal-offset} of the shadow lookup moves the sample sideways, and the filter reads up to 33 texels around it, so a pixel near a square's edge would read outside the map.

**Containment** is the rule Strata uses. Start at the first cascade whose split lies beyond the pixel's depth, and take the first one whose square holds the position at least 33 texels inside and whose depth range holds it. The last cascade holds up to its edge. Each square covers its sphere by that margin, so its own cascade holds every point of a slice. The test changes the outcome only for a point that the normal offset pushed toward the edge.

::figure{id=containment}

Blending is the same idea in the other direction. A **cascade blend band** is the last part of a cascade's slice, in which its shadow mixes into the next cascade's so that no seam shows. The weight is 0 before the band and 1 at the split, and it is 0 where the next cascade does not hold the point.

```slang src="Strata/shaders/Include/Shadows.slang#L46-L92"
bool ShadowCascadeHolds(int cascade, float3 relativePosition, float margin)
{
	float4 lightClip = mul(u_Cascades[cascade].ViewProjection, float4(relativePosition, 1.0));
	float3 lightPosition = lightClip.xyz / lightClip.w;
	float2 uv = NDCToUV(lightPosition.xy);
	return all((uv >= float2(margin))) && all((uv <= float2(1.0 - margin))) && lightPosition.z >= 0.0 && lightPosition.z <= 1.0;
}

bool ShadowCascadeHolds(int cascade, float3 relativePosition)
{
	bool last = cascade + 1 >= int(u_Frame.ShadowParams.w);
	return ShadowCascadeHolds(cascade, relativePosition, last ? 0.0 : c_ShadowCascadeMarginTexels * u_Frame.ShadowParams.y);
}

// The cascade that shades a camera-relative position at a view depth, by containment: from the first cascade whose split lies
// beyond the depth, the first one that holds the position (ShadowCascadeHolds); -1 when none does. Each cascade's square covers
// its slice's sphere by the filter's reach (SceneRenderer::FindShadowCasters), so a point of the view is held by the cascade of
// its slice; containment also keeps a position the normal offset or the jitter moved off it from reading outside its square.
// Every shader that selects a cascade calls this; none selects by depth alone.
int SelectShadowCascade(float viewDepth, float3 relativePosition)
{
	int cascadeCount = int(u_Frame.ShadowParams.w);
	for (int cascade = 0; cascade < cascadeCount; cascade++)
	{
		if (viewDepth < GetCascadeSplit(cascade) && ShadowCascadeHolds(cascade, relativePosition))
			return cascade;
	}
	return -1;
}

// How far a pixel is into the band where its cascade hands over to the next one (the last one fades out): 0 before the
// band, 1 at the split. The band is the last ShadowParams.z of the cascade's depth range, from the previous split (the
// first cascade's from the camera, at 0), as ShadowCascades::GetLayout lays it out: the next cascade's slice starts at the
// band, so its square covers it; where the next cascade does not hold a position (moved off it by the normal offset), the
// cascade does not blend into it (0).
float CascadeBlendWeight(int cascade, float viewDepth, float3 relativePosition)
{
	float split = GetCascadeSplit(cascade);
	float previousSplit = cascade > 0 ? GetCascadeSplit(cascade - 1) : 0.0;
	float band = u_Frame.ShadowParams.z * (split - previousSplit);
	if (!(band > 0.0))
		return 0.0;
	float weight = clamp((viewDepth - (split - band)) / band, 0.0, 1.0);
	if (weight > 0.0 && cascade + 1 < int(u_Frame.ShadowParams.w) && !ShadowCascadeHolds(cascade + 1, relativePosition))
		return 0.0;
	return weight;
}
```

1. **Line 51:** the test is the square in :term[uv]{id=texture-coordinates}, shrunk by a margin, and the depth range.
2. **Line 70:** a cascade is chosen only if its split lies beyond the depth and it holds the position.
3. **Line 85:** the band is a share of the slice's depth range, counted from the previous split.
4. **Line 89:** a cascade does not blend into the next one where that one does not hold the position.

One constant matters most: the margin of 33 texels. The test, the layout's margin and the filter's reach are one number in three places. If the filter reached further than the margin, the shader would read texels outside the square and show a line at the edge.

## The real code: depth and casters

### The depth fit

A cascade also needs a depth range, the span along the light's direction that its map stores. Strata fits each range on the GPU. The range spans from the far side of the slice's sphere to the nearest caster toward the light, at least the sphere's near side and at most a set distance beyond it. The depth's precision then goes where the casters are, and none is spent on empty sky between the sun and the scene.

A caster farther toward the light than `c_MaxShadowCasterDistance` (100 km) would stretch the range uselessly. The vertex shader flattens such casters onto the :term[near plane]{id=near-plane}, a technique called pancaking that [Shadow basics](../light/shadow-basics.md) explains. `CascadeFit.comp` writes the projections into `u_Cascades`, one thread for each cascade.

```slang src="Strata/shaders/Scene/CascadeFit.comp.slang#L35-L72"
void st_Main()
{
	uint cascade = st_LocalInvocationIndex;
	if (cascade >= u_Fit.CascadeCount)
		return;
	float4 box = u_Fit.Boxes[cascade];
	float4 depths = u_Fit.Depths[cascade];
	float casterNearZ = depths.y;
	if (u_Fit.CasterDepthsFromGPU != 0u)
	{
		uint encoded = u_CasterDepths[cascade];
		if (encoded != 0u)
			casterNearZ = max(casterNearZ, DecodeOrderedFloat(encoded));
	}
	else
	{
		casterNearZ = max(casterNearZ, depths.w);
	}
	float nearZ = clamp(casterNearZ, depths.y, depths.y + u_Fit.MaxCasterDistance);
	float nearPlane = -nearZ;
	float farPlane = -depths.x;

	// glm::orthoRH_ZO with the planes swapped (reversed-Z: the near plane at depth 1).
	float zNear = farPlane;
	float zFar = nearPlane;
	float4x4 projection = float4x4(1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0);
	projection[0][0] = 2.0 / (box.z - box.x);
	projection[1][1] = 2.0 / (box.w - box.y);
	projection[2][2] = -1.0 / (zFar - zNear);
	projection[0][3] = -(box.z + box.x) / (box.z - box.x);
	projection[1][3] = -(box.w + box.y) / (box.w - box.y);
	projection[2][3] = -zNear / (zFar - zNear);
	u_Cascades[cascade].ViewProjection = mul(projection, u_Fit.LightView);
	// z: 0 (the penumbra's search distance follows the receiver's view distance alike in every cascade: Include/Shadows.slang,
	// ShadowSearchDistance); w: the near plane's light view z, for the cascades' occlusion culling (Cull.comp's
	// IsOccludedInCascade).
	u_Cascades[cascade].Parameters = float4(depths.z, farPlane - nearPlane, 0.0, nearZ);
}
```

1. **Lines 43–51:** the nearest caster comes from the GPU's culling or from what the CPU found, never from a readback.
2. **Line 53:** the near plane is clamped between the sphere's near side and the limit beyond it.
3. **Line 67:** the projection is orthographic with reversed depth, and it joins the light's view.
4. **Line 71:** the parameters carry the texel size and the near plane for the cascade's :term[occlusion culling]{id=occlusion-culling}.

Both paths fit here. The CPU path hands the shader the nearest casters it found, and the GPU-driven path's culling writes the nearest depth of each cascade into a buffer in the same frame.

The fit is the reason the maps need no readback. Nothing waits for an answer that arrives frames later, because the culling that finds the casters also finds their depths.

### Which casters, on both paths

A **shadow caster** is an object that a cascade's map draws because its shadow can fall inside that cascade's square. The rule for one caster is the same on both paths. The caster's bounds in light space must overlap the square, must not lie beyond the cascade's far side and must span at least one texel.

A **sub-texel caster** is a caster whose light-space extent, the larger of its width and height, is under one texel of a cascade. That cascade omits it, because such a caster only flickers in and out of single texels. A bolt 5 cm wide is 7 texels in the first cascade of the toy, which has 6.9 mm texels, and under one texel in the last one, which has 95 mm texels. The statistic `SubTexelCasters` counts the casters dropped.

On the CPU path, `FindShadowCasters` asks the :term[spatial index]{id=spatial-index} for candidates with one job for each cascade, and merges the lists in cascade order. The exact test then runs in parallel chunks that merge in chunk order. The casters, the assets they need and the animators they report never depend on how the threads ran; [Threads and the job system](../core/jobs.md) shows how such a merge stays :term[deterministic]{id=determinism}. `GetCascadeMask` sets one bit for each cascade a caster reaches. `GatherShadowDraws` batches the casters by a :term[sort key]{id=sort-key} that holds the cascade in three bits.

`CanShadowView` serves the animators. A skinned mesh that is off screen may still throw a shadow into the view, so its animator must keep running. The function sweeps the caster's box along the light and asks whether the sweep reaches the receivers inside the view.

On a GPU-driven frame the search moves into the culling. `CullShadow.comp` is `Cull.comp` built with its shadow switch, and [GPU-driven draw](../draw/gpu-driven.md) keeps the general story. `GetCasterCascades` does the CPU's test on the GPU for each proxy.

```slang src="Strata/shaders/Scene/Cull.comp.slang#L240-L273"
uint GetCasterCascades(GPUProxy proxy, bool countSubTexel, out float3 lightMin, out float3 lightMax)
{
	CullInstance first = u_CullInstances[proxy.FirstInstance];
	float4x4 world = transpose(transpose(float4x4(first.WorldRows[0], first.WorldRows[1], first.WorldRows[2], float4(0.0, 0.0, 0.0, 1.0))));
	world[0][3] -= u_Cull.CameraPosition.x;
	world[1][3] -= u_Cull.CameraPosition.y;
	world[2][3] -= u_Cull.CameraPosition.z;
	float4x4 lightWorld = mul(u_Cull.LightView, world);
	float3 localCenter = (proxy.LocalMin + proxy.LocalMax) * 0.5;
	float3 localExtents = (proxy.LocalMax - proxy.LocalMin) * 0.5;
	float3 lightCenter = (mul(lightWorld, float4(localCenter, 1.0))).xyz;
	float3x3 basis = ((float3x3)(lightWorld));
	float3 lightExtents = float3(abs(basis[0][0]) * localExtents.x + abs(basis[0][1]) * localExtents.y + abs(basis[0][2]) * localExtents.z,
		abs(basis[1][0]) * localExtents.x + abs(basis[1][1]) * localExtents.y + abs(basis[1][2]) * localExtents.z,
		abs(basis[2][0]) * localExtents.x + abs(basis[2][1]) * localExtents.y + abs(basis[2][2]) * localExtents.z);
	lightMin = lightCenter - lightExtents;
	lightMax = lightCenter + lightExtents;
	float extent = max(lightMax.x - lightMin.x, lightMax.y - lightMin.y);
	uint cascadeMask = 0u;
	for (uint cascade = 0u; cascade < u_Cull.CascadeCount; cascade++)
	{
		float4 box = u_Cull.CascadeBoxes[cascade];
		float4 parameters = u_Cull.CascadeParameters[cascade];
		if (lightMax.x < box.x || lightMin.x > box.z || lightMax.y < box.y || lightMin.y > box.w || lightMax.z < parameters.x)
			continue;
		if (extent < parameters.y)
		{
			if (countSubTexel)
				Count(ST_COUNTER_SUB_TEXEL_CASTERS);
			continue;
		}
		cascadeMask |= 1u << cascade;
	}
	return cascadeMask;
```

1. **Line 257:** the extent is the larger side of the caster's box in light space.
2. **Line 263:** the caster must overlap the cascade's box and not lie beyond its far side.
3. **Line 265:** a caster smaller than the texel is counted and omitted from that cascade.

`CullCascades` calls it, widens each cascade's depth range for the fit, keeps the cascade mask under occlusion culling and emits the draws into each cascade's shadow buckets.

```slang src="Strata/shaders/Scene/Cull.comp.slang#L408-L443"
void CullCascades(uint proxyIndex, GPUProxy proxy, bool meshDrawable, GeometryEntry entry, float fraction, uint geometry, uint mirrored, bool feedback)
{
	float3 lightMin;
	float3 lightMax;
	uint cascadeMask = GetCasterCascades(proxy, true, lightMin, lightMax);
	if (cascadeMask == 0u)
		return;
	if (feedback)
	{
		// Casters are kept resident, not requested (as FindShadowCasters marks them).
		MarkMeshFeedback(proxy.MeshSlot, ST_FEEDBACK_SHADOW, 0.0);
		MarkProxyMaterials(proxy, ST_FEEDBACK_SHADOW, false, 0.0, entry);
	}
	if (!meshDrawable)
		return;
	if (IsCounting())
	{
		// Every drawn caster extends the depth range of its cascades toward the light (Scene/CascadeFit.comp), in both phases'
		// cascades: the projections are known before the first phase draws.
		uint nearZ = EncodeOrderedFloat(lightMax.z);
		for (uint cascade = 0u; cascade < u_Cull.CascadeCount; cascade++)
		{
			if ((cascadeMask & (1u << cascade)) != 0u && u_CasterDepths[cascade] < nearZ)
				InterlockedMax(u_CasterDepths[cascade], nearZ);
		}
	}
	// Occlusion culled: the first phase draws into each cascade what it held in the previous frame; the second the other
	// casters it finds visible against the first phase's depth (CullShadowSecondPhase). Frames that draw the cascades whole
	// record what they drew as the next frame's history (the culling pauses while it does not pay). Cascades that keep their
	// layer from the previous frame get no draws.
	if (u_Cull.ShadowOcclusion != 0u)
		cascadeMask &= GetCascadeVisibility(u_Visibility[proxyIndex], u_Cull.VisibilityParity);
	else if (IsCounting())
		SetCascadeVisibility(proxyIndex, cascadeMask);
	EmitShadowInstances(proxy, entry, fraction, geometry, mirrored, cascadeMask & ~u_Cull.CachedCascades, 0u);
}
```

1. **Line 412:** the mask of cascades the caster reaches comes from the function above.
2. **Line 431:** every drawn caster raises its cascades' nearest depth for the fit, with an atomic maximum.
3. **Line 438:** under occlusion culling, a cascade draws only casters its visibility bits keep.
4. **Line 442:** cascades whose layers are cached get no draws.

On frames that use :term[visibility feedback]{id=visibility-feedback}, `FindShadowCasters` only places the cascades and tests skinned proxies out of view for their animators. The GPU finds the casters.

### The cascade cache and cascade occlusion

A cascade's map holds the same picture while nothing it shows changes. The **shadow cascade cache** keeps a cascade's layer from one frame to the next and draws it again only when something that reaches it changed. It runs only on GPU-driven frames. The CPU path, which runs when `GPUDriven` is off, on devices without `drawIndirectFirstInstance` and for thumbnails, draws every cascade in every frame.

Each cascade has a key made of the camera, the viewport, the light's view, the cascade's box, the cascade count, the map size and the levels of detail. The cache also compares the :term[render scene's]{id=render-scene} identity and the versions of the :term[GPU copy's]{id=gpu-copy} tables, the :term[geometry pool]{id=geometry-pool} and the :term[texture table]{id=texture-table-strata}, the last one while materials are alpha-masked. The render scene's :term[change log]{id=change-log} names the proxies that changed, and the cascades their old and new bounds reach become dirty. If the log has overflowed, every cascade is dirty.

A moving camera changes the keys, because the squares moved, so every layer is drawn again. A still camera keeps them. The keys hold the camera without the jitter of temporal anti-aliasing, which goes into the frame's constants, so the jitter alone draws no layer again. `DrawGPUShadows` clears and draws only the dirty layers, and `CullCascades` emits no draws for the others.

Suppose a ball rolls through cascade 2 on a still camera. Its old and new bounds reach only that cascade, so the other layers stay valid and the frame draws one layer. A statistic shows it: `renderStats.cachedCascades` reads the cascade count minus one.

Cascades also use occlusion culling, which [Occlusion culling](../draw/occlusion.md) leaves for this page. The first phase draws what each cascade held the frame before. A depth pyramid of that cascade's own shadow map, at a quarter of its size, shows what the first phase covered, and the second phase draws the casters that stand in front of it. A caster that lies, everywhere it covers the map, behind the pyramid's farthest depth is hidden.

The culling runs only while it pays, which means at least one caster in sixteen is hidden. Otherwise it probes again every 16 frames.

## Reading the result

### Statistics and the shadows view

The renderer records each slice's near end, split and texel size in `SceneRendererStats::Cascades`. The editor's `editor.perf` and every `viewport.capture` result show them as `renderStats.cascades`.

The shadows debug view is the value `shadows` of the `debugView` setting. For every pixel the scene drew, it rebuilds the position from the depth and selects the cascade as the shading does. It then divides the cascade's texel size by the world size of a screen pixel at that distance. Green marks a density of 1 or less, yellow 2 and red 4 or more. White lines are cascade edges, hatching marks the blend bands, and a gray veil marks surfaces that no cascade covers.

Beside the picture the view keeps statistics for each cascade: the median density, the 10th and 90th percentiles and the share of pixels at 4 or more. They come back two or three frames late, and `viewport.capture` waits for them. A median of 1.1 in cascade 0 says the nearest slice is as fine as the screen. A red floor in the middle distance says the slice that holds it is too coarse there.

A change shows in the statistics before it shows to the eye. Raise `ShadowDistance` from 80 m to 160 m, and every split moves out, every texel grows and the medians rise. Lower it, and the same texels cover less, so the medians fall.

The figures below show the shadows view down the Third Person course at Medium quality, then its legend at Medium and at High. Every surface is green at both qualities, so the change shows only in the legend. High adds a cascade nearest the camera, and the farther slices keep their far ends with texels half as large, so their medians fall to about half.

::figure{id=shadows-view-medium-high variant=medium}

::figure{id=shadows-view-medium-high variant=medium crop=legend}

::figure{id=shadows-view-medium-high variant=high crop=legend}

The knobs that change the picture are few. `ShadowDistance` moves the last split, `CascadeDistribution` moves the splits between, and `CascadeBlend` widens the bands. The figure below shows the view at the sun's distribution of 0.9. A higher distribution moves the white edges toward the camera, and a lower one moves them away.

::figure{id=cascade-distribution-sweep}

### The quality rows

Two rows of the quality settings decide the cost: `ShadowResolution`, the texels each way of every cascade, and `ShadowCascades`, the number of layers. The quality tables list their values for every preset, with the estimate of the memory in [Quality settings](../image/quality-settings.md). **High** chooses its resolution by the viewport's height, and a custom quality may change either row.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Fit each cascade to the receivers by a depth readback | Research, some games | Tight squares, so finer texels at the same size | A readback that arrives frames late, texels that move with every turn, shadows that sharpen after a stop |
| Fit to the slice's corners without snapping | Many engines | Squares a few percent smaller than spheres | A size that changes when the camera turns, and flicker |
| Virtual shadow maps | Unreal Engine 5 | Sharp shadows at every distance, one design | A pool of pages, a feedback pass and far more machinery |
| More cascades or larger maps only | Any engine | Simplicity | Memory and time without limit: five layers of 8192 already take 1.25 GiB |
| A second shadowed directional light, such as a moon | Games with two light sources | Night scenes with a lit moon | A second set of cascades, memory and time |

Strata does not offer virtual shadow maps or a second shadowed directional light, and its plans for the future list both as not done. A scene has one shadowed sun, so a moon that casts shadows is not possible yet, and a view that needs sharp shadows at every distance must raise the quality rows instead.

## How it is tested

The layout alone is tested without a GPU in the suite `Renderer.ShadowCascades`, in `StrataTests/src/Renderer/ShadowCascadesTests.cpp`. One case checks that the splits follow the shadow distance and the distribution from a fixed start, never the near clip. Another checks that a fifth cascade sits before the four and keeps their texels. Further cases check that a turning camera keeps every slice, sphere and texel size. The last two check that a sphere is the smallest around its slice and holds all of it, and that squares cover their spheres and move in whole texels.

The suite `GPU.SceneRenderer.ShadowCascades` renders. One case checks that a turned camera's first frame shows the shadows of a fresh renderer at that view. Another checks that a slow sideways step moves the shadows without shimmer. A third checks that every receiver has its shadow in the first frame after a turn or a change.

The remaining cases check that a still camera keeps its cascades and cached layers. They also check that both paths lay out alike and stay pixel-equal, and that a ball shot from the camera leaves the shadows of the boxes where they are.

Run both on the Windows debug build with doctest filters. The GPU suite needs a graphics card.

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=Renderer.ShadowCascades
build/windows/bin/Debug/StrataTests.exe --test-suite=GPU.SceneRenderer.ShadowCascades
```

The first command runs in a second and needs no device. The second renders real frames, and a failure there names the case that broke, such as the first frame after a turn.

## Changing it safely

The extension points are few. A sixth cascade is not one of them. The limit of five stands in the shader's constants and in the visibility bits, which keep five cascades for each of two frames; the three bits of the sort key would hold eight. A cascade beyond the limit would draw into the layer of another.

The extension points that remain follow. The slices change in `GetSplit` and `GetLayout`, the squares in `GetSquare`, the test of a caster in `GetCascadeMask` and `GetCasterCascades`, and the depth fit in `CascadeFit.comp`. Whatever you change, keep the CPU path and the GPU path equal: the case that compares them to the pixel is the first to run.

Three rules of the engine's guide apply. What is drawn and requested is decided by two codes, the CPU path and `Cull.comp`, so a change goes into both, and shading must not depend on the draw order. Cascade layouts come only from `GetLayout`, and a selection comes only from `SelectShadowCascade`. A new input of how casters are drawn must change a version that the caches compare.

:::rule[A new input changes a version]
A cascade layer is kept while its key and the scene's versions stay the same. This is the reason for the rule: the cache cannot see what you did not tell it. Suppose you add a material flag that changes how casters are drawn and leave the key alone. A still camera then keeps showing a layer drawn without the flag, and the bug appears only after the next change of the camera.
:::

## What went wrong before

Strata 0.7.0 fitted each cascade to the receivers that a readback from the GPU reported. Two flaws came from it. After a turn, the shadows sharpened slowly, because the fit waited for several readbacks before it shrank. In the Physics Playground, a ball shot at the camera re-cut the slices, because a ball near the camera changed the nearest receiver depth, and every shadow jumped as the ball passed.

The cure was to remove the readback. The slices now depend on the view alone. Two cases of `GPU.SceneRenderer.ShadowCascades` guard it: one for the first frame after a turn, and one for the ball shot. Both fail if the layout starts to depend on the scene again.

:::example[A layout by hand]
Take the toy's lens and 80 m. For the first split, the logarithmic series gives 1.5 × (80 / 1.5) to the power 1/4 = 4.05 m, and the uniform one 1.5 + 78.5 / 4 = 21.1 m. The blend is 0.9 × 4.05 + 0.1 × 21.1 = 5.76 m, below the cap of 7.5 m.

The first sphere sits at the far end, so its radius is the corner distance 1.178 × 5.76 = 6.79 m, rounded up to 1/16: 6.8125 m. A texel is 2 × 6.8125 / 1980 = 6.9 mm. A screen pixel at 5.76 m is 2 × 5.76 × 0.577 / 1080 = 6.2 mm, so the density is 1.1 pixels per texel.
:::

## Summary

- Splits blend a logarithmic and a uniform series from a fixed 1.5 m by `CascadeDistribution`, and the first ends at most at 7.5 m. At 60 degrees and 16:9 a slice's sphere has a radius of 1.178 times its split, rounded up to 1/16 m, and a texel is the sphere's diameter over the map's size less 68.
- A sphere depends on the slice and the lens alone, so a turn changes no size. Each square snaps to whole texels of absolute light space in double precision, so a texel keeps covering the same patch of world.
- On the CPU path `FindShadowCasters` and `GetCascadeMask` give a caster its cascade bits, and `GatherShadowDraws` sorts its draws by them. On a GPU-driven frame `GetCasterCascades` and `CullCascades` emit its draws, none into a cached cascade.
- The shadows view colors each receiver by screen pixels per shadow texel, green at 1 or less and red at 4 or more, with white cascade edges and hatching on the blend bands. Its statistics give each cascade's median and percentiles, and `renderStats.cascades` gives each slice and its texel size.

## Check yourself

1. At a shadow distance of 200 m, what does the code do with the first split, and why?

   :::answer{tests="compute-layout"}
   The blend alone would end the first cascade at 9.7 m, but `c_MaxFirstSplit` caps it at 7.5 m. Without the cap, curved surfaces near the camera under a low sun show their texels as stripes.
   :::

2. A slice of a 60 degree, 16:9 view ends at 10 m. What are the sphere's radius and the texel size with 2048 texels?

   :::answer{tests="compute-layout"}
   The sphere sits at the far end, so the radius is 1.178 × 10 = 11.78 m, rounded up to 11.8125 m. The texel is 2 × 11.8125 / 1980 = 11.9 mm.
   :::

3. The camera turns by 90 degrees. Which statement is right? (a) The cascades are fitted again to the new view, so their sizes change. (b) The spheres keep their sizes, because they depend on the lens alone, and only their places move. (c) The cascades keep their places, and other cascades cover the new view.

   :::answer{tests="explain-stability"}
   Statement (b) is right. Statement (a) describes the 0.7.0 fit, which Strata dropped. Statement (c) is wrong because each sphere is centered on the view axis relative to the camera, so it turns with the camera. The squares then snap to the texel grid, so the texels stay on the same patches of world.
   :::

4. A shader selects the cascade by depth alone. The normal offset moved a point to 10 texels inside its square's edge. What goes wrong, and what does containment do?

   :::answer{tests="explain-stability"}
   The filter reaches 33 texels, so it reads 23 texels beyond the square's edge, outside the map, and a line shows at the edge. Containment asks for 33 texels inside, so the next cascade shades the point and every filter tap reads inside its own square.
   :::

5. A still GPU-driven frame has five cascades, and a ball touches only cascade 2. Which layers are drawn again, and what changes on the CPU path?

   :::answer{tests="trace-caster"}
   Only layer 2, which the ball's old and new bounds reach, is drawn; the other four keep their pictures because their keys and the scene's versions are unchanged. On the CPU path every cascade is drawn again in every frame.
   :::

6. In the shadows view a floor 3 m away is red. What does that say, and what could you change?

   :::answer{tests="read-shadows-view"}
   Red means 4 or more screen pixels per texel: the cascade that shades the floor is too coarse there. Raise the resolution, use more cascades, shorten the shadow distance or raise `CascadeDistribution` to move texels to the near slices.
   :::

## Exercises

1. **Basic.** Open the Third-Person sample and set the debug view to `shadows` with `viewport.setSettings`. Compare one view at the Medium quality with the same view at High. Which cascade edges move, and what does the median density do?

   :::answer[Worked solution]{tests="read-shadows-view"}
   Run `viewport.setSettings` with `{"debugView": "shadows"}`, change the quality, then read `renderStats.cascades` and the shadows statistics from `viewport.capture`. At High the fifth cascade covers the nearest meters and the maps are larger, so the colors move toward green and the median falls. The extra edge of the near cascade appears at 1.5 m or nearer.
   :::

2. **Medium.** Predict what the sketch below prints in its two columns, then compare. It holds a shadow edge at a fixed place in the world and moves the camera by 3.1 mm per step, less than half a texel.

   :::answer[Worked solution]{tests="explain-stability"}
   The sketch measures where the edge falls inside the square, as a fraction of a texel. Read the sketch, then its output.

   ```cpp sketch="light-sun-shadows-1-snap.cpp"
   // A shadow edge at a fixed place in the world, seen from a square that follows a slow camera: with and without snapping.
   #include <cmath>
   #include <cstdio>

   constexpr double c_Texel = 0.0069; // About the texel of the first Medium cascade, in meters
   constexpr double c_MapSize = 2048.0;
   constexpr double c_EdgeX = 1.0;    // The shadow edge's place in the world, in meters

   // Where the edge falls inside the square, in texels from the square's left side.
   double GetEdgeTexel(double squareCenter)
   {
   	const double left = squareCenter - 0.5 * c_Texel * c_MapSize;
   	return (c_EdgeX - left) / c_Texel;
   }

   int main()
   {
   	std::printf("camera x   unsnapped edge   snapped edge\n");
   	for (int step = 0; step < 6; step++)
   	{
   		const double cameraX = 0.0031 * step;
   		const double snapped = std::floor(cameraX / c_Texel) * c_Texel;
   		const double loose = GetEdgeTexel(cameraX);
   		const double fixedEdge = GetEdgeTexel(snapped);
   		std::printf("%.4f m    %9.3f       %9.3f\n", cameraX, loose - std::floor(loose), fixedEdge - std::floor(fixedEdge));
   	}
   	return 0;
   }
   ```

   ```text output-of="light-sun-shadows-1-snap.cpp"
   camera x   unsnapped edge   snapped edge
   0.0000 m        0.928           0.928
   0.0031 m        0.478           0.928
   0.0062 m        0.029           0.928
   0.0093 m        0.580           0.928
   0.0124 m        0.130           0.928
   0.0155 m        0.681           0.928
   ```

   1. **Line 12:** the left side of the square is half its width left of its center.
   2. **Line 22:** snapping rounds the camera's position down to a whole texel.
   3. **Line 25:** only the fraction of the edge's texel position is printed, because a whole texel is invisible.

   Loose, the fraction changes by 0.45 in every row, so the edge crawls. Snapped, it stays the same in every row.
   :::

3. **Medium.** Write the outline of a unit test for `ShadowCascades::GetLayout`. Which view do you build, and what do you check?

   :::answer[Worked solution]{tests="compute-layout"}
   Build a `ShadowCascadeView` with four cascades, a shadow distance of 80 m, a 60 degree lens and a map of 2048 texels. Check that the splits are 5.76, 13.93, 32.68 and 80 m. Check that the first slice starts at the near clip and each later one at the band before the previous split, and that another near clip moves no split. Run it as a case of `Renderer.ShadowCascades`, and see that it fails when you change the start of 1.5 m.
   :::

4. **Hard.** Trace it yourself: follow one fence post from the scene into a cascade's draws on the CPU path and on a GPU-driven frame. Then read `renderStats.cascades` for both.

   :::answer[Worked solution]{tests="trace-caster"}
   On the CPU path the post's bounds are queried in `SceneRenderer::FindShadowCasters` in `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp`, `GetCascadeMask` sets its cascade bits, and `GatherShadowDraws` pushes one sort key for each bit with `SceneDrawKey::Make`. On a GPU-driven frame `GetCasterCascades` in `Strata/shaders/Scene/Cull.comp.slang` computes the mask and `EmitShadowInstances` writes the draws. The statistics show the same slices for both paths.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Renderer/ShadowCascades.h` and `ShadowCascades.cpp`: the layout (`GetLayout`, `GetSplit`, `GetSliceSphere`, `GetSquare`).
- `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp`: `LayOutShadowCascades`, `FindShadowCasters`, `GetCascadeMask`, `CanShadowView`, `GatherShadowDraws`, `FitCascades`.
- `Strata/src/Strata/Renderer/SceneRendererGPUDriven.cpp`: `PrepareShadowCache`, `DrawGPUShadows`.
- `Strata/shaders/Scene/CascadeFit.comp.slang`, `Strata/shaders/Scene/Cull.comp.slang` and `Strata/shaders/Include/Shadows.slang`.
- `StrataTests/src/Renderer/ShadowCascadesTests.cpp` and `StrataTests/src/Renderer/GPUSceneShadowCascadeTests.cpp`.
- `RendererQualitySettings::ShadowCascades` and `ShadowResolution`; the light's `CascadeBlend` and `CascadeDistribution`.

## Further reading

- Valient, "Stable rendering of cascaded shadow maps", ShaderX6, 2008: the sphere and the snapping; intermediate.
- Lauritzen, Salvi and Lefohn, "Sample distribution shadow maps", 2011: fitting maps by a depth readback; advanced.
- Dimitrov, "Cascaded shadow maps", NVIDIA, 2007: the parallel-split layout; beginner.
- Epic Games, documentation of virtual shadow maps in Unreal Engine 5; intermediate.
