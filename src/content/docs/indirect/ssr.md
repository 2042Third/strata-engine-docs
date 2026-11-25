---
id: indirect/ssr
title: "Screen-space reflections"
description: "How Strata finds reflections of what is on screen by marching rays through the depth buffer, validates each hit and resolves the result."
kind: internals
size: XL
tracks: [E]
needs: [indirect/probes, image/taa, light/clearcoat-transmission, indirect/ao]
time: 110
learn:
  - id: march-line
    text: explain why a reflected ray is a straight line in UV and depth, and how a march with bisection and a thickness tolerance finds a hit
  - id: two-traces
    text: compare the Checkerboard and Spatial traces by resolution, history, steps and what each reads
  - id: validation
    text: explain how validated crossings, the edge fade and the facing test stop ghosts, sky wedges and false hits
  - id: resolve-mix
    text: trace how the resolve averages neighbouring rays and how the forward pass mixes the result over the fallback light
  - id: trace-row
    text: trace which trace a quality row runs and what it needs, and name what screen-space reflections cannot show
since: 0.6.0
status: final
---

**Screen-space reflections** (SSR) add to a shiny surface a reflection of what the camera already sees. Each frame the :term[renderer]{id=renderer} shoots a ray from every reflecting pixel, walks it through the :term[depth buffer]{id=depth-buffer} until it meets a surface, and reads that surface's color from the previous frame. The result is laid over the specular light of the probes and the sky, which stay as the fallback wherever a ray finds nothing. Transparent surfaces get no screen-space reflection, and nothing that is off screen can appear in one.

## The problem and how engines solve it

A polished floor shows what stands above it. The [probes](../indirect/probes.md) give it a blurred picture taken from one fixed spot, so a ball that rolls across the floor never appears in it. To show that ball, the renderer needs a ray from the floor pixel in the mirror direction and the first thing the ray meets. A game rarely keeps its geometry in a form a ray can query. It does hold one thing that already describes the visible scene: the depth buffer, a picture that stores for each pixel how far away the surface is.

Treat the depth buffer as a landscape of heights seen from the camera. The reflected ray starts at a pixel and moves away. If it passes behind the surface at some pixel, it has crossed that surface, and the color of that pixel is the reflection. Moving a point along the ray in steps and testing each point against the buffer is called ray marching. It is cheap, since it needs only images the renderer already has, but it knows only the surfaces the camera sees.

### The ray as a line on the screen

Before marching, solve the geometry. A ray in the world is a straight line, and a perspective camera maps straight lines to straight lines on the screen. So the reflected ray is a straight line over the screen's pixels. Strata writes a point of the screen as :term[texture coordinates]{id=texture-coordinates} (UV) and a depth: the pixel's position from 0 to 1 and its depth value. The ray is one straight line in that three-number space.

The depth value is an affine function of 1 over the distance from the camera, as the page on [coordinates](../gpu/coordinates.md) shows. So along the screen line the depth changes evenly, while the distance does not. The march can step evenly along the line and convert to distances only when it compares.

A small side view makes it concrete. The camera sits at the origin and looks along +z, and the screen has 1,000 rows with a focal length of 500 pixels. A point at height $y$ and distance $z$ then lands on row $500 - 500\,y/z$. A floor lies at height −1 and a wall stands 8 meters away, and the floor point at distance 4 sits on row 625. Its mirror ray rises by 1 for each 4 it advances, so it passes (z 6, height −0.5) and meets the wall at (z 8, height 0).

Project those points. The start is row 625 with 1/z = 0.25, and the wall point is row 500 with 1/z = 0.125. The middle point, halfway along the ray in the world, is row 541.7 with 1/z = 0.167. On the line from (625, 0.25) to (500, 0.125) the row 541.7 lies two thirds of the way, and the line's value there is $0.25 - \tfrac23 \cdot 0.125 = 0.167$. The point lies exactly on the line, but two thirds along it and not half, so equal steps in the world are not equal on the screen.

::figure{id=ssr-ray-line}

The ray also needs an end. Left alone it runs forever, so Strata cuts it at the first of three places. One is where it leaves the screen, and another is where it passes the :term[far plane]{id=far-plane} (depth 0 in a :term[reversed-Z]{id=reversed-z} buffer). The third, for a ray that points at the camera, is immediately before the :term[near plane]{id=near-plane}. What remains is a start, a change to the end and a length in pixels, and a ray shorter than one pixel has nothing to march.

### Stepping, thickness and bisection

The march tests points along the line. At each point it reads the depth buffer at the point's pixel, converts both depths to distances, and asks whether the ray's point is behind the surface. A single yes is not enough. A ray that jumps over a thin wall between two steps lands far behind it, and the wall must not count as a hit.

The **thickness tolerance** is the distance behind a surface within which a ray still counts as hitting it. Beyond that distance the surface is taken to be thin, and the ray is taken to have passed behind it.

Take Strata's Checkerboard rule with numbers. A ray point lies 9.0 meters from the camera, the previous point lay at 8.4, and the surface at the new point is at 8.8, so the ray is 0.2 meters behind. The tolerance is the ray's change in distance since the last point, 0.6, plus the larger of 0.05 meters and 2 % of 9.0 meters (0.18), so 0.78. The ray is behind by 0.2, which is less than 0.78, so it hits. If the surface were at 7.9 the ray would be behind by 1.1 meters and would pass.

Steps cannot be fine everywhere. Strata puts them closer together near the start of the ray, because contact reflections near the object matter most. The fraction along the ray is the square of an even fraction. For a ray 480 pixels long and 24 steps the first lands one pixel from the start, the second 1.9 pixels, the third 5.2, the fourth 10.2 and the last about 460. The spacing grows from about 1 pixel to almost 40.

Once a step lands behind a surface, the hit lies between this point and the last one in front. **Bisection** takes the middle of that interval, tests it, and keeps the half that still holds the crossing. Six halvings divide the interval by 64. For a step of 20 pixels the hit is then known within a third of a pixel.

### Skipping empty space: the hierarchical march

Long rays need many steps, and a fixed number of steps can miss thin things. The usual remedy is a **Hi-Z march**: a march over a pyramid of the depth buffer, in which each coarser level stores the nearest depth over a block of pixels. A ray that is in front of the nearest surface of a block skips the whole block at once. Otherwise the march looks at the finer level. Empty space then costs a few reads, and detail costs more.

Strata tried this for the Spatial modes and rejected it. A ray that grazes a floor has nearer floor pixels below it in every coarse block, so the march cannot skip, and it runs out of steps. The contract section and the last exercise return to this.

### Color, confidence and noise

The march finds a pixel, and the reflection needs that pixel's color. The scene's light is not complete in the middle of a frame, so Strata reads the color of the frame before. It moves along the hit pixel's :term[motion vector]{id=motion-vector}, so a moving object is found where it was one frame earlier. The price is that a reflection shows the object as it looked one frame ago, and a surface that was off screen in the last frame has nothing to show.

A hit is not always believed. The **confidence** of a hit is a number from 0 to 1 for how far its reflection is believed. The result's alpha stores it, and the forward pass mixes the reflection with the fallback light by it. It falls to 0 where the surface is too rough or the ray meets a surface from behind, and it falls near the edge the ray leaves the screen through. Past that edge the ray would have met something unknown, so the engine fades toward the fallback.

Last is noise. Marching every pixel at full resolution is costly, so one design traces a few pixels per frame with random starting offsets and lets a temporal filter average the noise. Another traces everything and filters in space. Strata has both, one per quality row, and they are the two traces this page teaches. The table in [Alternatives Strata did not choose](#alternatives-strata-did-not-choose) sets them beside the other ways engines show reflections.

## The map

One component and one quality row decide what happens. The component's `ScreenSpaceReflections` asks for the effect (default off). `ScreenSpaceReflectionsIntensity` scales how much it replaces the fallback (default 1). `ScreenSpaceReflectionsMaxRoughness` (default 0.5) stops it on surfaces that are too rough, and the confidence fades over the last quarter below that value. The quality row `Reflections` then scales what the scene asked for, by preset.

| Preset | Row value | Trace | Steps | Bisections | Rejected candidates |
| --- | --- | --- | --- | --- | --- |
| `Low` | `Off` | none | - | - | - |
| `Medium` | `Checkerboard` | half resolution, one pixel of each block | 24 | 6 | the first hit is taken |
| `High` | `Spatial` | full resolution, validated | 32 | 6 | up to 2 |
| `Ultra` | `SpatialHigh` | full resolution, validated | 48 | 8 | up to 3 |

The first mode, **Checkerboard**, traces a half-resolution target in which each texel stands for a block of 2 by 2 pixels. Each frame it traces another pixel of the block, so four frames cover them all. It reads the history of temporal anti-aliasing (:term[TAA]{id=taa}) for the color and leaves its noise for TAA to average, so it works only with TAA. The other two modes, Spatial and SpatialHigh, trace every pixel at full resolution and resolve in space. They need neither TAA nor a history of their own: they read a copy of the previous frame's color.

```mermaid caption="The two pipelines of a frame. The prepass writes the surface target that both traces read. Checkerboard traces a half-resolution target and reads the TAA history. Spatial and SpatialHigh trace at full resolution, resolve over five by five pixels and read the color copy of the previous frame. The forward pass reads the result." alt="A flow in two rows. In both, the depth prepass writes depth, normals, motion and a surface target. In the first row a half-resolution trace reads the TAA history and writes a result for the forward pass. In the second row a full-resolution trace reads the color copy of the previous frame, a resolve averages it, and the forward pass reads the result."
flowchart LR
	P[Depth prepass: depth, normals, motion, surface target] --> C[Checkerboard trace: half resolution, 24 steps]
	H[(TAA history)] --> C
	C --> F[Forward pass: mix over probes and sky]
	P --> S[Spatial trace: full resolution, 32 or 48 steps]
	K[(Color copy of the previous frame)] --> S
	S --> R[Resolve: 5 by 5, ratio estimator]
	R --> F
	F --> K
```

The **surface target** is a texture that the :term[depth prepass]{id=depth-prepass} writes beside the depth. It holds the view-space normal in octahedral form (a direction packed into two numbers), the roughness the forward pass will shade with (widened by :term[specular anti-aliasing]{id=specular-anti-aliasing-geometric}) and the metallic factor, as four :term[half-float]{id=half-float} channels. A variant of `Strata/shaders/Scene/DepthPrepass.frag.slang` writes it, so the trace needs no material lookups. A surface that lights do not shade writes roughness 1, which the default maximum roughness never lets through. The traces also read the prepass's geometric normals for the confidence and the validation.

The Spatial modes need the previous frame's color. The renderer copies the scene's color after the sky and before the transparent surfaces, every frame at these rows. The copy has full resolution and four :term[bytes]{id=byte} per pixel. Smooth surfaces read it sharp up to roughness 0.05. Rougher surfaces read the blurred levels of the half-resolution copy that glass reads, from roughness 0.15, with a smooth blend between.

Memory follows from the formats, and `ReflectionsBytes` in `Strata/src/Strata/Renderer/RendererQuality.cpp` adds them up. Checkerboard takes 8 bytes per pixel for the surface target and 8 per half-resolution texel for its result: about 20 MiB at 1080p and 79 MiB at 4K. Spatial takes 28 bytes per pixel, from the surface target, the traced texture and the resolved texture at 8 each plus the color copy at 4. With the blurred levels that is about 232 MiB at 4K, 153 MiB more than Checkerboard.

The first frame of a Spatial mode has no copy to read. A :term[camera cut]{id=camera-cut}, a reset or a scene change also leaves none. That frame is not traced, the forward pass keeps the fallback, and the renderer reports the reflections as pending. Captures and thumbnails render up to two more frames for that reason.

## The contract

The code keeps seven rules. Each stands where a bug of the past put it.

1. **SSR light is visible light.** :term[Ambient occlusion]{id=ambient-occlusion} must not darken what a screen ray found. The ray already saw what blocks the light, at the screen's scale. Only the material's own occlusion map, which describes creases below one pixel, darkens a found reflection.
2. **Fade only where rays leave the screen.** The fade belongs to the edge the ray leaves through. A fade near every edge drew wedges of sky.
3. **Keep only validated crossings.** In Spatial, a crossing must lie on one continuous surface. Taking any point behind a surface as a hit turned thin posts into ghosts.
4. **Do not march a hierarchy.** Grazing rays over floors ran out of steps. The textbook algorithm is not always the right one.
5. **Never fill an object's back with its front's colors.** The depth buffer has only fronts, and a rim lit from the front is wrong on a back. Strata tried this and dropped it.
6. **Checkerboard needs TAA.** This is the one named exception to "nothing needs history to look right", and it keeps Medium at the costs of 0.6.0. The decision's home is [temporal anti-aliasing](../image/taa.md).
7. **Results are premultiplied.** A trace stores its color already multiplied by its confidence, so a texel that found nothing adds no black at the edge of a reflection.

:::rule
Reflections march a fixed number of steps, accept only validated hits and fade only at the edge a ray leaves through. The base reflectance comes from the index of refraction, as the [reflectance page](../light/reflectance.md) teaches. Reason: the same view must give the same reflection in every frame, and each of these guards against a fault that a test catches.
:::

Two general rules apply too. Never block a frame on an asset: a texel that cannot be traced falls back to the probes and the sky, as the [probes page](../indirect/probes.md) says. Wrap every pass in a stage of the :term[graphics processing unit]{id=gpu} (GPU) timer: this one runs in the stage named Reflections.

## A toy version

The toy marches one ray in the side view of the problem section: a floor at height −1, a wall 8 meters away and a depth buffer of 1,000 rows. It has the straight line in row and 1 over distance, steps that are closer near the start, the thickness test and six bisections. It has no confidence, no history and no second trace.

:::question
New to C++? Read [Programming from zero 1](../basics/programming-1.md), [Programming from zero 2](../basics/programming-2.md), [Programming from zero 3](../basics/programming-3.md) and [Generic C++](../basics/cpp-generic.md) first.
:::

Read `MakeDepthBuffer` first: it makes the surface distance of every row. `IsBehind` is the hit test, and `main` holds the march and the bisection.

```cpp sketch="indirect-ssr-toy.cpp"
// A screen-space reflection march in a side view: a polished floor and a wall, one ray, with bisection.
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <vector>

constexpr float c_Focal = 500.0f; // Pixels from the eye to the screen
constexpr float c_CenterRow = 500.0f;
constexpr float c_WallDistance = 8.0f;

// The depth buffer: the view distance of the surface each row shows (floor at height -1, wall at distance 8, up to height 3).
std::vector<float> MakeDepthBuffer()
{
	std::vector<float> depth(1000, 1.0e30f);
	for (int row = 0; row < 1000; row++)
	{
		const float slope = (c_CenterRow - (static_cast<float>(row) + 0.5f)) / c_Focal; // Height over distance
		const float floorDistance = slope < 0.0f ? -1.0f / slope : 1.0e30f;
		if (floorDistance < c_WallDistance)
			depth[row] = floorDistance;
		else if (slope * c_WallDistance <= 3.0f)
			depth[row] = c_WallDistance;
	}
	return depth;
}

// Whether the ray's point (row and 1 / distance) lies behind the surface its row shows, by less than the thickness.
bool IsBehind(const std::vector<float>& depth, float row, float inverse, float previousDistance)
{
	const float distance = 1.0f / inverse;
	const float scene = depth[static_cast<size_t>(std::clamp(row, 0.0f, 999.0f))];
	const float thickness = std::abs(distance - previousDistance) + std::max(0.05f, 0.02f * distance);
	return distance > scene && distance - scene < thickness;
}

int main()
{
	const std::vector<float> depth = MakeDepthBuffer();
	// The floor point at distance 4 reflects the eye's ray upward: in screen space a straight line in (row, 1 / distance).
	const float startRow = 625.0f;
	const float startInverse = 0.25f;
	const float deltaRow = 375.0f - startRow; // To the far plane
	const float deltaInverse = 0.0f - startInverse;
	const float pixels = std::abs(deltaRow);
	const int steps = 12;
	float previousAlong = 0.0f;
	float previousDistance = 1.0f / startInverse;
	float hitAlong = -1.0f;
	for (int index = 0; index < steps; index++)
	{
		const float fraction = (static_cast<float>(index) + 0.5f) / static_cast<float>(steps);
		const float along = std::max(fraction * fraction, 1.0f / pixels);
		const float row = startRow + deltaRow * along;
		const float inverse = startInverse + deltaInverse * along;
		const bool behind = IsBehind(depth, row, inverse, previousDistance);
		std::printf("step %2d along %.3f row %6.1f ray %6.2f m surface %6.2f m %s\n", index, along, row, 1.0f / inverse,
			std::min(depth[static_cast<size_t>(row)], 99.99f), behind ? "hit" : "-");
		if (behind)
		{
			hitAlong = along;
			break;
		}
		previousAlong = along;
		previousDistance = 1.0f / inverse;
	}
	if (hitAlong < 0.0f)
		return 0;
	float low = previousAlong;
	float high = hitAlong;
	for (int index = 0; index < 6; index++)
	{
		const float middle = 0.5f * (low + high);
		const float distance = 1.0f / (startInverse + deltaInverse * middle);
		const float scene = depth[static_cast<size_t>(startRow + deltaRow * middle)];
		(distance > scene ? high : low) = middle;
	}
	std::printf("hit at row %.1f, surface %.2f m; the wall point at height 0 is row 500.0 at 8.00 m\n", startRow + deltaRow * high,
		depth[static_cast<size_t>(startRow + deltaRow * high)]);
	return 0;
}
```

```text output-of="indirect-ssr-toy.cpp"
step  0 along 0.004 row  624.0 ray   4.02 m surface   4.02 m -
step  1 along 0.016 row  621.1 ray   4.06 m surface   4.12 m -
step  2 along 0.043 row  614.1 ray   4.18 m surface   4.37 m -
step  3 along 0.085 row  603.7 ray   4.37 m surface   4.83 m -
step  4 along 0.141 row  589.8 ray   4.65 m surface   5.59 m -
step  5 along 0.210 row  572.5 ray   5.06 m surface   6.90 m -
step  6 along 0.293 row  551.6 ray   5.66 m surface   8.00 m -
step  7 along 0.391 row  527.3 ray   6.56 m surface   8.00 m -
step  8 along 0.502 row  499.6 ray   8.03 m surface   8.00 m hit
hit at row 499.6, surface 8.00 m; the wall point at height 0 is row 500.0 at 8.00 m
```

1. **Lines 17–18:** a row's slope is its height over distance, and below the horizon the floor is met at distance −1 over the slope.
2. **Lines 28–34:** a point is a hit when it lies behind its row's surface by less than the thickness, which grows with the change in distance since the last point.
3. **Lines 41–43:** the line runs from row 625 to row 375 and from 1/z = 0.25 to 0, the far plane.
4. **Line 52:** the squared fraction puts the steps close together near the start.
5. **Lines 70–75:** six halvings of the interval between the last point in front and the first point behind.

The march finds the wall at the ninth step, at 0.502 of the way along the line, and the bisection lands on row 499.6. The wall point at height 0 is row 500, so the answer is a tenth of a row off. Steps 0 to 7 stay in front of the floor and the wall, and the start of the ray cannot hit the surface it starts on. The toy hides what the real code must face: thin objects, rays that leave the screen, back faces and noise.

## The real code, in the order of the data

The prepass writes depth, normals, motion and the surface target. One of two compute :term[shaders]{id=shader} traces a ray per texel, the Spatial path resolves, and the forward pass mixes the result. The shaders are under `Strata/shaders/`: `Include/ScreenReflections.slang` holds what the traces share, `Effects/ScreenSpaceReflections.comp.slang` is Checkerboard, `Effects/ScreenSpaceReflectionsSpatial.comp.slang` is Spatial, and `Effects/ReflectionResolve.comp.slang` is the resolve. The forward pass is in `Scene/Forward.frag.slang` and `Include/IndirectLight.slang`. The code that decides which trace runs is `SceneRenderer::TraceScreenReflections` and `SceneRenderer::TraceSpatialReflections` in `Strata/src/Strata/Renderer/SceneRendererScreenReflections.cpp`.

### The shared ray

Both traces start with `BeginScreenRay`. Search for the two projections, the cut at the screen's edge and the refusal of rays into the surface.

```slang src="Strata/shaders/Include/ScreenReflections.slang#L58-L85"
// The ray's far end: far away from the camera, or (toward it) just before the near plane.
float rayLength = c_FarDistance;
if (direction.z > 1e-6)
	rayLength = min(rayLength, 0.999 * (-u_Frame.CameraPosition.w - position.z) / direction.z);
if (rayLength <= 0.0)
	return false;
float4 startClip = mul(u_Frame.Projection, float4(position, 1.0));
float4 endClip = mul(u_Frame.Projection, float4(position + direction * rayLength, 1.0));
// In screen space (UV and depth) the ray is a straight line along which the depth changes linearly.
float3 start = float3(NDCToUV(startClip.xy / startClip.w), startClip.z / startClip.w);
float3 delta = float3(NDCToUV(endClip.xy / endClip.w), endClip.z / endClip.w) - start;
// Cut where it leaves the screen or passes the far plane (depth 0), whichever comes first.
float screenExtent = 1.0;
for (int axis = 0; axis < 2; axis++)
{
	if (delta[axis] > 0.0)
		screenExtent = min(screenExtent, (1.0 - start[axis]) / delta[axis]);
	else if (delta[axis] < 0.0)
		screenExtent = min(screenExtent, -start[axis] / delta[axis]);
}
float depthExtent = delta.z < 0.0 ? -start.z / delta.z : 1.0;
float extent = min(screenExtent, depthExtent);
ray.LeavesScreen = screenExtent < 1.0 && screenExtent <= depthExtent;
delta *= max(extent, 0.0);
ray.Start = start;
ray.Delta = delta;
ray.Pixels = length(delta.xy * u_Frame.ViewportSize.xy);
return ray.Pixels >= 1.0;
```

1. **Lines 59–61:** the ray's far end is 10,000 meters away, or immediately before the near plane when it points at the camera.
2. **Lines 64–68:** both ends go through the projection, and the start and the change are kept in UV and depth.
3. **Lines 70–77:** the ray is cut where it meets an edge of the screen, whichever of the four comes first.
4. **Lines 78–81:** the far plane is a cut too, and the ray remembers whether the screen's edge was the end that won.
5. **Lines 84–85:** the length in pixels, and the refusal of a ray shorter than one pixel.

The function starts above these lines by reflecting the view ray about the normal of the surface target. It refuses a ray that a :term[normal map]{id=normal-map} turned into the geometric surface, since nothing in front of the surface can be reflected there. Orthographic cameras use a fixed view direction instead.

### Hit confidence

`GetHitConfidence` runs on every hit, in both traces. It has two factors. Look at where each one comes from.

```slang src="Strata/shaders/Include/ScreenReflections.slang#L104-L113"
float GetHitConfidence(float2 hitUV, int2 hitPixel, ScreenRay ray)
{
	float facing = clamp(-4.0 * dot(OctahedralDecode(TexelFetch(u_Normals, hitPixel, 0).rg), ray.Direction), 0.0, 1.0);
	float edgeFade = 1.0;
	if (ray.LeavesScreen)
	{
		float remaining = length((ray.Start.xy + ray.Delta.xy - hitUV) * u_Frame.ViewportSize.xy); // Pixels to the exit
		edgeFade = clamp(remaining / (c_EdgeFade * min(u_Frame.ViewportSize.x, u_Frame.ViewportSize.y)), 0.0, 1.0);
	}
	return facing * edgeFade;
```

1. **Line 106:** the facing term is 0 for a surface seen from behind and 1 once the normal opposes the ray by a :term[cosine]{id=cosine} of 0.25 or more.
2. **Lines 108–111:** only a ray that leaves the screen fades, by its distance in pixels to the exit over a tenth of the screen's smaller side.
3. **Line 113:** the two factors multiply.

The first factor catches a ball's back. The depth buffer holds fronts only, so a ray that goes behind a ball stops at a front pixel seen from behind. There the normal points toward the camera, the way the ray runs, so the :term[dot product]{id=dot-product} is positive and the facing term is 0. A back face gets no reflection, and the reflected ball keeps only the crescent that the screen can show.

::figure{id=ssr-crescent-diagram}

::figure{id=ssr-crescent-crop}

The second factor fades a hit near the end of a ray that left the screen. On a screen 1,080 pixels high the fade is 108 pixels wide, so a hit 54 pixels before the exit has confidence 0.5. A ray that ends at the far plane, or at a wall near an edge it never crosses, has `LeavesScreen` false and keeps 1. The 0.7.0 engine faded near every edge, and a floor that reflected a distant wall grew wedges of sky along the sides.

::figure{id=ssr-edge-fade-diagram}

::figure{id=ssr-edge-fade-crop}

### The Checkerboard trace

The Checkerboard shader marches a half-resolution texel from one pixel of its block. The frame count picks the pixel: bit 0 gives the column and bit 1 the row, so frames 0 to 3 visit the four pixels in turn. Watch where the noise goes and how the thickness is made.

```slang src="Strata/shaders/Effects/ScreenSpaceReflections.comp.slang#L75-L97"
// Steps closer together near the start (contact reflections), the first at least a pixel away (the surface itself).
float noise = frac(InterleavedGradientNoise(float2(pixel)) + u_Frame.TemporalParams.z);
float minStep = 1.0 / pixels;
float previousStep = 0.0;
float previousDistance = GetViewDistance(start.z);
float hitStep = -1.0;
for (uint index = 0u; index < c_Steps; index++)
{
	float fraction = (float(index) + noise) / float(c_Steps);
	float along = max(fraction * fraction, minStep);
	float3 point = start + delta * along;
	float sceneDepth;
	float behind = GetDistanceBehind(point, size, sceneDepth);
	float rayDistance = GetViewDistance(point.z);
	float thickness = abs(rayDistance - previousDistance) + max(c_MinThickness, c_ThicknessScale * rayDistance);
	if (behind > 0.0 && behind < thickness)
	{
		hitStep = along;
		break;
	}
	previousStep = along;
	previousDistance = rayDistance;
}
```

1. **Lines 76–77:** the noise turns each frame, and the first step is at least one pixel from the surface.
2. **Lines 81–85:** the same squared steps as the toy, 24 of them, each shifted by the noise.
3. **Lines 89–90:** the thickness is the ray's change in distance plus the margin, as in the example above, and a hit ends the march.

The noise shifts every sample by a fraction of a step that changes with the pixel and the frame, so the frames of the TAA history cover the gaps between steps. The second half bisects and reads the color.

```slang src="Strata/shaders/Effects/ScreenSpaceReflections.comp.slang#L98-L128"
if (hitStep < 0.0)
	return float4(0.0);
// Where between the last point in front and the first behind the ray crosses the surface.
float low = previousStep;
float high = hitStep;
for (uint index = 0u; index < c_RefineSteps; index++)
{
	float middle = 0.5 * (low + high);
	float sceneDepth;
	if (GetDistanceBehind(start + delta * middle, size, sceneDepth) > 0.0)
		high = middle;
	else
		low = middle;
}
float2 hitUV = (start + delta * high).xy;
int2 hitPixel = clamp(int2(hitUV * u_Frame.ViewportSize.xy), int2(0), size - 1);

// The hit surface where the previous frame showed it.
float2 previousUV = hitUV - u_Velocity.Load(int3(hitPixel, 0)).rg;
if (any((previousUV < float2(0.0))) || any((previousUV > float2(1.0))))
	return float4(0.0);
float3 color = u_History.SampleLevel(u_LinearClampSampler, previousUV, 0.0).rgb * u_Reflections.HistoryScale;
#ifdef ST_SSR_LIGHT_SURFACES
// A ray that met a light surface keeps its confidence and sends no light: the probes' and sky's specular are replaced by
// nothing there, and the area light's own highlight is the panel's reflection, once. Every texel the bilinear fetch of the
// color blends counts: a hit beside the panel would otherwise take its light (a bright outline around its image).
if (CountLightSurfaceTexels(hitUV) > 0.0)
	color = float3(0.0);
#endif
float confidence = roughnessFade * GetHitConfidence(hitUV, hitPixel, ray) * min(u_Reflections.Intensity, 1.0);
return float4(SanitizeHDR(color) * confidence, confidence);
```

1. **Line 98:** a march that found no surface returns nothing.
2. **Lines 101–111:** six bisections between the last point in front and the first point behind.
3. **Lines 116–119:** the hit's pixel moved by its motion vector, to where that surface was in the previous frame, and the history there scaled to this frame's :term[pre-exposure]{id=pre-exposure}.
4. **Lines 120–126:** in a frame with a rectangular light, a hit on or beside the light's own surface keeps its confidence and sends no color, because the light's highlight already draws that reflection.
5. **Lines 127–128:** the color times the confidence, with the confidence in alpha.

A hit whose surface was outside the previous frame returns nothing. The color is multiplied by the confidence, so that the forward pass's bilinear lookup blends a reflection's edge with what it replaces and not with black. The frame count belongs to the TAA history. With fewer than two frames of history, or without TAA, nothing is traced at all, because `reflectionsWanted` needs `m_TemporalFrames > 1`.

### The Spatial trace

The Spatial trace has a different goal: no history of its own, every pixel traced every frame, and a validated hit. The march runs over the whole ray. The pixels of a 4 by 4 block start at 16 offsets in the fixed order of the ambient occlusion pass, so each pixel's steps lie between its neighbours', and the resolve averages them later.

A step is a **candidate** when the segment from the previous point crossed a surface: the previous point was in front of the depth at the current pixel, and this point is behind it. A second kind catches a ray that ran in front of a surface and then crosses that surface's plane between two samples. This happens at a wall's top edge or at a post narrower than a step. A candidate is a suspicion only. The code bisects it and asks whether it holds.

```slang src="Strata/shaders/Effects/ScreenSpaceReflectionsSpatial.comp.slang#L241-L281"
MarchPoint previous;
previous.Along = 0.0;
previous.RayDistance = GetViewDistance(ray.Start.z);
previous.SceneDistance = c_SkyDistance; // The start crosses no surface of its own
uint candidates = 0u;
float hitAlong = -1.0;
for (uint index = 0u; index <= u_Reflections.Steps && hitAlong < 0.0; index++)
{
	float fraction = (float(index) + offset) / float(u_Reflections.Steps);
	float along = index < u_Reflections.Steps ? max(fraction * fraction, minStep) : 1.0 - 0.5 * minStep;
	if (index == u_Reflections.Steps && along <= previous.Along)
		break; // A short ray's last step is already past that point
	MarchPoint current = MarchPointAt(ray, along, size);
	bool candidate = false;
	if (previous.RayDistance <= current.SceneDistance && current.RayDistance > current.SceneDistance)
	{
		candidate = true;
		hitAlong = RefineCrossing(ray, previous, current, size);
	}
	else if (previous.SceneDistance < c_SkyDistance && previous.RayDistance <= previous.SceneDistance
		&& current.RayDistance > previous.SceneDistance - GetThickness(previous.SceneDistance))
	{
		float2 previousUV = (ray.Start + ray.Delta * previous.Along).xy;
		int2 previousPixel = clamp(int2(previousUV * u_Frame.ViewportSize.xy), int2(0), size - 1);
		float4 planeView = mul(u_Frame.InverseProjection, float4(UVToNDC((float2(previousPixel) + 0.5) * u_Frame.ViewportSize.zw), u_Depth.Load(int3(previousPixel, 0)).r, 1.0));
		float3 planePoint = planeView.xyz / planeView.w;
		float3 planeNormal = OctahedralDecode(TexelFetch(u_Normals, previousPixel, 0).rg);
		if (dot(GetRayPosition(ray, current.Along) - planePoint, planeNormal) < 0.0)
		{
			candidate = true;
			hitAlong = RefinePlaneCrossing(ray, previous, current, planePoint, planeNormal, size);
		}
	}
	if (candidate && hitAlong < 0.0)
	{
		candidates++;
		if (candidates >= u_Reflections.MaxCandidates)
			break;
	}
	previous = current;
}
```

1. **Lines 241–244:** the march starts on a point that crosses no surface of its own.
2. **Line 250:** the squared steps, and after the last one a final point half a pixel before the end of the ray.
3. **Lines 255–259:** a candidate by depth: in front at the previous point, behind at this one.
4. **Lines 260–273:** a candidate by plane: the ray crossed the previous pixel's plane, found with the geometric normal.
5. **Lines 274–279:** a rejected candidate counts, and the budget `MaxCandidates` ends the march.

A rejected candidate does not end the march, but a cap bounds how many may fail: 2 for Spatial and 3 for SpatialHigh. After the cap the ray finds nothing, the probes fill the gap, and a cluttered scene costs no more than the cap allows. The march also adds a final sample 0.5 pixels short of the ray's end, because the offset steps can stop up to a whole step before it. On a ray toward the far plane the last step would span everything past some tens of meters, so without the extra sample a far wall would show sky.

A **validated crossing** is a candidate that passed `ValidateCrossing`. Its hit lies on a surface and behind it by at most the tolerance plus the interval. The two ends of the interval must also lie on one continuous surface. `BisectCrossing` runs first and treats sky points and points behind a blocking surface with care, so that a post between two points on a wall does not fool it.

```slang src="Strata/shaders/Effects/ScreenSpaceReflectionsSpatial.comp.slang#L159-L173"
float ValidateCrossing(MarchPoint low, MarchPoint high)
{
	float interval = abs(high.RayDistance - low.RayDistance);
	if (high.SceneDistance >= c_SkyDistance)
	{
		if (low.SceneDistance >= c_SkyDistance || IsPassingBehind(low))
			return -1.0;
		float edgeSlack = GetThickness(low.SceneDistance) + interval;
		return high.RayDistance > low.SceneDistance && high.RayDistance - low.SceneDistance <= edgeSlack ? low.Along : -1.0;
	}
	float slack = GetThickness(high.SceneDistance) + interval;
	bool valid = high.RayDistance > high.SceneDistance && high.RayDistance - high.SceneDistance <= slack
		&& (IsPassingBehind(low) || abs(high.SceneDistance - low.SceneDistance) <= slack);
	return valid ? high.Along : -1.0;
}
```

1. **Lines 162–167:** an interval that ends on a surface's last pixel and the sky beyond it counts as a hit at the edge, only if the ray had passed the surface's depth there.
2. **Lines 169–171:** the slack is the tolerance plus the interval, and the ends' distances must be as close.
3. **Line 172:** the hit's place along the ray, or −1 for a false crossing.

The key is the last clause on line 169. A ray that passed behind a thin post has one end on the post and one on the wall far behind it. The two distances differ by much more than the slack, so the crossing is false. A ray that met a wall has both ends on the wall, and it passes. `RefineCrossing` then tries once more from beyond a blocking surface that the bisection closed in on, so the ray still reaches the wall behind a post.

::figure{id=ssr-post-ghost}

::figure{id=ssr-posts-crop}

The two traces differ in cost. At 1080p Checkerboard traces about 0.5 million texels a frame, each with at most 24 steps and 6 bisections. Spatial traces 2.1 million pixels, each with up to 32 steps, 6 bisections for every candidate and up to 2 candidates. The extra work buys a picture that needs no history and shows no noise that crosses frames.

### The color of the hit

The Spatial trace reads the color copy at the hit pixel minus its motion, in two layers. A mirror reads the full-resolution copy alone, and a rougher surface blends toward the half-resolution copy's blurred levels over roughness 0.05 to 0.15. The blurred level is roughness times the level count minus 1. The light is last frame's, carried along the motion to the surface's place in this frame, and nothing accumulates, so each frame's reflections are complete in themselves. The color is scaled to this frame's pre-exposure, multiplied by the confidence and written with the confidence in alpha, as in Checkerboard.

### The resolve

Every pixel of a Spatial mode holds one ray, and neighbouring rays differ, so the traced image shows the 4 by 4 pattern of offsets as a screen door. The resolve averages the 5 by 5 neighbourhood of each pixel. It is a **ratio estimator**: it divides the sum of the neighbours' weighted results, which are premultiplied by their confidence, by the sum of their weights. The weights then decide how much each neighbour's ray counts, and the brightness of the average stays right.

Take a small case: five neighbours of equal weight, three of which found a red surface of brightness 2 with confidence 1 while two found nothing. The averaged color is $(3 \cdot 2)/5 = 1.2$ and the averaged alpha is $3/5 = 0.6$. With a fallback of 0.5 the forward pass shows $0.5 \times (1 - 0.6) + 1.2 = 1.4$. That is what the neighbourhood says: 60 % of the directions see 2 and 40 % see 0.5, and $0.6 \cdot 2 + 0.4 \cdot 0.5 = 1.4$.

The kernel is one row of weights for each axis, $(0.5, 1, 1, 1, 0.5)$, multiplied. Its five weights sum to 4. The two outer pixels share an offset of the pattern, because 4 pixels apart is one full period, so together they weigh 1 like each of the three others. All four offsets of an axis count the same, and the pattern cancels in both axes. A 3 by 3 window, which an earlier version used, kept a third of the pattern, and that third was the screen door of a rough sheet.

::figure{id=ssr-screen-door}

Each neighbour's weight is that kernel product times three more factors. The lobe weight asks how well the neighbour's ray serves the center. The ray left along the neighbour's mirror direction. The center's specular lobe, taken at the half vector of the center's view and that direction, says how likely the center would have sent a ray there. The plane weight and the normal weight keep neighbours on the same surface.

For two surfaces of roughness 0.5, with $\alpha = 0.25$ (the lobe's width, the roughness squared) and $\alpha^2 = 0.0625$, a neighbour whose half vector lies along the center's normal has weight 1. If $n \cdot h = 0.99$, the bottom of the fraction is $0.99^2 (0.0625 - 1) + 1 = 0.0812$, and the weight is $0.0625^2 / 0.0812^2 = 0.59$. A neighbour 1 cm off the plane at 5 meters has plane weight $e^{-50 \cdot 0.01/5} = 0.90$, and normals that agree to a cosine of 0.99 give a normal weight of $0.99^8 = 0.92$.

```slang src="Strata/shaders/Effects/ReflectionResolve.comp.slang#L93-L119"
float4 sum = s_Traced[centerIndex];
float weightSum = 1.0;
for (int y = -2; y <= 2; y++)
{
	for (int x = -2; x <= 2; x++)
	{
		if (x == 0 && y == 0)
			continue;
		int sampleIndex = (center.y + y) * c_Tile + center.x + x;
		float4 normalAlpha = s_NormalAlpha[sampleIndex];
		if (normalAlpha.w <= 0.0)
			continue;
		float4 directionDepth = s_DirectionDepth[sampleIndex];
		float planeDistance = abs(dot(s_Position[sampleIndex].xyz - centerPosition, centerGeometric));
		float planeWeight = exp(-c_PlaneSharpness * planeDistance / centerDepth);
		float normalWeight = pow(max(dot(s_Geometric[sampleIndex].xyz, centerGeometric), 0.0), c_NormalPower);
		float3 halfVector = normalize(view + directionDepth.xyz);
		float nDotH = max(dot(centerNormal, halfVector), 0.0);
		float denominator = nDotH * nDotH * (centerAlpha2 - 1.0) + 1.0;
		// pi alpha_i^2 x D_center(H), with D = alpha_c^2 / (pi denominator^2): the pis cancel.
		float lobeWeight = min(normalAlpha.w * centerAlpha2 / max(denominator * denominator, 1e-12), 1.0);
		float weight = c_Kernel[x + 2] * c_Kernel[y + 2] * lobeWeight * planeWeight * normalWeight;
		sum += s_Traced[sampleIndex] * weight;
		weightSum += weight;
	}
}
o_Reflections[pixel] = sum / weightSum;
```

1. **Lines 93–94:** the sum starts with the center's own result at weight 1.
2. **Lines 107–108:** the plane weight from the distance to the center's tangent plane, and the normal weight from the geometric normals.
3. **Lines 109–113:** the lobe weight, written so that the factors of pi cancel, and capped at 1.
4. **Lines 114–115:** the product of the kernel and the three weights scales the neighbour's premultiplied result.
5. **Line 119:** the ratio of the two sums.

The cap means no neighbour counts for more than the center. A mirror's neighbours weigh less the more their mirror directions differ from its own, and at 3840 by 2160 pixels they still keep 0.97, a softening of about two pixels. The shader loads a 12 by 12 tile into :term[shared memory]{id=shared-memory} for each 8 by 8 group, so every neighbour read is a read of fast memory.

### The forward mix

The forward pass reads the resolved texture at the pixel's UV, except on transparent surfaces, where the sample does not exist.

```slang src="Strata/shaders/Scene/Forward.frag.slang#L208-L214"
#ifndef ST_FORWARD_TRANSPARENT
if (u_Frame.ReflectionParams.x > 0.0)
{
	inputs.ScreenReflection = u_ScreenReflections.SampleLevel(u_LinearClampSampler, fragCoord * u_Frame.ViewportSize.zw, 0.0);
	inputs.ScreenReflection.rgb /= u_Frame.TemporalParams.y;
}
#endif
```

The block runs only when `ReflectionParams.x` is above 0, which the renderer sets when this frame has a result. The division by the frame's pre-exposure returns the stored value to scene units. Then the specular gather mixes it in.

```slang src="Strata/shaders/Include/IndirectLight.slang#L101-L106"
if (inputs.ScreenReflection.a > 0.0)
{
	return (fallback * inputs.SpecularOcclusion * (1.0 - inputs.ScreenReflection.a) + inputs.ScreenReflection.rgb * inputs.ScreenReflectionOcclusion)
		* inputs.SpecularColor;
}
return fallback * inputs.SpecularColor * inputs.SpecularOcclusion;
```

The fallback is the probes' and the sky's specular light. It is multiplied by `(1 - a)`, where `a` is the confidence, and the screen's color joins whole, because it was already multiplied by the confidence. The fallback keeps the :term[specular occlusion]{id=specular-occlusion-lagarde} of the ambient occlusion pass. The found color keeps only `ScreenReflectionOcclusion`, which holds the material's own occlusion and is exactly 1 without an occlusion map. Both are then multiplied by the specular color, the second half of the :term[split sum]{id=split-sum-approximation} that the [seam page](../indirect/seam.md) teaches.

::figure{id=ssr-ao-wet}

A :term[clear coat]{id=clear-coat} gets no screen-space reflection of its own. The mix is for the base's specular light only, and the coat's image light comes from the probes, the sky or the ambient. Transparent surfaces get none either, which the `#ifndef ST_FORWARD_TRANSPARENT` around the sample enforces. The color copy is made before the transparent surfaces, so glass behind glass does not appear in a reflection.

::compare{id=ssr-modes-sweep}

::compare{id=ssr-roughness-sweep}

:::example[One quality row through a frame]
Take a scene with `ScreenSpaceReflections` on, `MaxRoughness` at 0.5 and a floor of roughness 0.3. The roughness fade is $(0.5 - 0.3)/(0.25 \times 0.5) = 1.6$, clamped to 1. At `Medium`, with a TAA history of two frames or more, Checkerboard traces. Frame 5 picks pixel (1, 0) of each block, because 5 & 1 is 1 and (5 >> 1) & 1 is 0. A hit 54 pixels before a screen exit has confidence 0.5, so the result is half the color with alpha 0.5.

At `High` the same floor needs no TAA. The first frame has no color copy, so the renderer reports the reflections as pending and a capture renders again. On the next frame every pixel is traced, the resolve averages 25 of them, and the forward pass mixes. A wall hit at confidence 1 and brightness 4, over a fallback of 0.5, gives $0.5 \times 0 + 4 = 4$ before the specular color.
:::

## Alternatives Strata did not choose

Each row is a way to put reflections in a game. The last two columns weigh it for Strata.

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Linear march only, no validation | Many first implementations | The simplest code and no candidate budget | Thin posts become ghosts and wall edges break; 0.7.0 took this road |
| Hi-Z march | Engines that want long rays at a fixed cost | Few reads over open space | Grazing floors defeat the blocks, and the pyramid costs a pass and memory |
| Random-ray SSR with temporal accumulation | Engines that trace one random ray per pixel and accumulate frames | Rough surfaces from many rays at a low cost per frame | A reflection that depends on history, which Strata keeps to Checkerboard |
| Mirror-plane reflections (draw the scene again, mirrored) | Games with one large mirror or a water surface | An exact reflection of everything, off screen too | A second draw of the scene per plane, and only for flat surfaces |
| Ray tracing hardware | Games that require the hardware | Reflections of off-screen and back surfaces | Hardware Strata does not require, and a scene structure to build and keep |

## How it is tested

The suite `GPU.SceneRenderer.SSR` draws small scenes and compares them with a prediction of the :term[central processing unit]{id=processor} (CPU). Among its tests:

- A mirror floor reflects a red cube where the CPU predicts, alike on both render paths.
- The reflection of a face the rays cross is whole in every frame, without holes.
- A reflection's edges blend into the probes' or the sky's reflection without darkening.
- Rough surfaces and rays that leave the screen keep the sky's reflection.
- Checkerboard without TAA traces nothing and makes no surface target.
- Spatial reflections trace every pixel without TAA, where the CPU predicts.
- A rough metal sheet's reflection shows no screen door.
- Hits fade only where their rays leave the screen.
- Ambient occlusion leaves a mirror's reflection alone.
- Thin posts in front of a mirror leave no ghost columns, and a ball's back is not reflected.

The same suite also moves the camera sideways past a rough sheet and over wet ground and measures how much the reflections flicker. The suite `GPU.SceneRenderer.IndirectFlicker` measures the flicker of the indirect light as the camera moves past a fence and over grass. The meter itself is taught in [test kinds](../engineering/test-kinds.md). The suite `Renderer.ReflectionMetrics` tests the meter's own measures on synthetic images and needs no GPU. Run the first on a machine with a GPU: `build/windows/bin/Debug/StrataTests.exe --test-suite=GPU.SceneRenderer.SSR`.

## Changing it safely

Extension points: a new setting is a field of `RendererQualitySettings` and a row of the presets, and a new count of steps belongs to `ScreenReflectionSteps` and `GetScreenReflectionSteps`. A change to what the traces read changes the surface target, so it changes the prepass variant and the bytes that `ReflectionsBytes` adds up.

The rules that apply, each with its reason:

- Keep the validation. Without it, thin posts return as ghosts.
- Keep the fade on the exit edge only, or sky wedges return.
- Keep ambient occlusion off a found reflection, or wet ground grows dark patches.
- Keep results premultiplied, or a reflection's edge gets a dark halo.
- Keep the Spatial modes free of history. A change that makes them read TAA breaks the rule that nothing but Checkerboard needs it.

Check a change with `GPU.SceneRenderer.SSR` and `GPU.SceneRenderer.IndirectFlicker`, and read the :term[GPU stage]{id=gpu-stage-strata} named Reflections for its cost.

## What went wrong before

Strata 0.7.0 had three faults, each found on the look-dev scenes and each now a test.

- Strata 0.7.0 took any point behind a surface as a hit, so thin posts became ghost columns beside their reflections. The test is "Thin posts in front of a mirror leave no ghost columns".
- Strata 0.7.0 faded near every edge of the screen, so sky wedges grew along the sides of reflections. The test is "Hits fade only where their rays leave the screen".
- Strata 0.7.0 let ambient occlusion darken wet ground that already showed what blocked the light. The test is "Ambient occlusion leaves a mirror's reflection alone".

One wrong comment remains at the pin. The comment on the component's fields in `Strata/src/Strata/Renderer/RendererComponents.h` says screen-space reflections work with TAA only. That holds for Checkerboard alone. Spatial and SpatialHigh run with or without TAA, as `Strata/src/Strata/Renderer/RendererQuality.h` says.

## Summary

- A reflected ray is a straight line in UV and depth. The march steps along it, closer together near the start, and halves the step that goes behind a surface within the thickness tolerance.
- Checkerboard traces half resolution, one pixel of a 2 by 2 block per frame, reads the TAA history along the hit's motion and needs TAA. Spatial and SpatialHigh trace every pixel and read the color copy of the previous frame.
- Validated crossings, the facing test and the fade at the exit edge stop ghosts, false back faces and sky wedges, and the Hi-Z march was rejected for grazing floors.
- The resolve is a 5 by 5 ratio estimator under a specular lobe weight, and the forward pass mixes premultiplied color over the fallback by one minus the confidence, darkening only the fallback.
- The row `Reflections` picks one trace per mode and needs a color copy or a TAA history, and it shows nothing for transparent surfaces, glass behind glass or a clear coat.

## Check yourself

1. A floor point is 4 meters from the camera, and its ray meets a wall at 8 meters, with the middle point at 6 meters in the world. Is that point halfway along the ray on the screen?

   :::answer{tests="march-line"}
   No. On the screen the 1/z values are 0.25, 0.167 and 0.125, so the middle point is two thirds of the way along the screen line. A world step and a screen step differ, which is why the march steps along the screen line and converts depths to distances.
   :::

2. Of Checkerboard and Spatial, which (a) needs TAA, (b) reads the color copy of the previous frame, (c) traces every pixel?

   :::answer{tests="two-traces"}
   (a) Checkerboard, since it reads the TAA history and leaves its noise to TAA. (b) Spatial and SpatialHigh read the copy of the previous frame. (c) Spatial and SpatialHigh trace every pixel at full resolution, while Checkerboard traces one pixel of each 2 by 2 block per frame.
   :::

3. A ray passes behind a 20 cm post and ends on a wall 8 meters behind it. Which rule stops the post from becoming a hit, and what does the crossing test compare?

   :::answer{tests="validation"}
   Validation. A crossing must lie on one continuous surface, so `ValidateCrossing` compares the distances of the interval's two ends. One sits on the post and one on the wall, much farther apart than the slack allows, so the crossing is false and the march continues to the wall.
   :::

4. Three of five equal-weight neighbours found a color of 2 with confidence 1, and the fallback is 0.5. What does the pixel show?

   :::answer{tests="resolve-mix"}
   The resolved color is 6/5 = 1.2 and the alpha is 0.6, so the forward pass shows $0.5 \times 0.4 + 1.2 = 1.4$. Only the material's own occlusion map could darken the 1.2, while the specular occlusion darkens the 0.5 alone.
   :::

5. Which of these does screen-space reflection show: a wet floor reflecting a ball behind the camera, a clear-coated car reflecting the street, a floor reflecting a glass window?

   :::answer{tests="trace-row"}
   None of them. The ball behind the camera is off screen, so no depth pixel holds it. A clear coat's image light comes from the probes, the sky or the ambient, never from the screen trace. The color copy is made before transparent surfaces, so the window's glass is not in it.
   :::

## Exercises

1. **Basic.** Trace it yourself: for a scene with `ScreenSpaceReflections` on, find where the renderer decides which trace a quality row runs, what each trace needs, and what tells the forward pass to sample the result.

   :::answer[Worked solution]{tests="trace-row"}
   `Strata/src/Strata/Renderer/SceneRenderer.cpp` computes `reflectionsAsked` (the component asks and the row is not `Off`) and `spatialReflectionsWanted` (through `RendererQuality::IsSpatialReflections`) at lines 3117 and 3118. A little later, at lines 3184 to 3198, Spatial needs the color copy of the renderer's previous frame. That copy must come from the same :term[render scene]{id=render-scene} or its clone source, with no camera cut and no history reset, while Checkerboard needs `m_TemporalFrame` and `m_TemporalFrames > 1`. Line 3252 sets `ReflectionParams.x` to 1 when `m_ReflectionFrame` is true, and `Strata/shaders/Scene/Forward.frag.slang` (lines 208 to 214) samples the result only then. A bake or a first frame has no copy and no history, so it gets no reflections and keeps the fallback.
   :::

2. **Medium.** Bring back the 0.7.0 acceptance in the Spatial trace and say which test you expect to fail.

   :::answer[Worked solution]{tests="validation"}
   In `ValidateCrossing` (`Strata/shaders/Effects/ScreenSpaceReflectionsSpatial.comp.slang`), delete the continuity clause, the line `&& (IsPassingBehind(low) || abs(high.SceneDistance - low.SceneDistance) <= slack)`. A crossing is then valid when the high end lies behind its surface by at most the slack. Rebuild and run `StrataTests.exe --test-suite=GPU.SceneRenderer.SSR`. The test "Thin posts in front of a mirror leave no ghost columns" is the one to fail, because rays that passed behind a post now hit it. Restore the clause afterward.
   :::

3. **Hard.** Write a sketch of a hierarchical march along a receding floor, count its reads against a linear march of 32 steps, and say why the hierarchy fails.

   :::answer[Worked solution]{tests="march-line,two-traces"}
   The sketch models the failure in one dimension. The floor recedes by 0.1 meters a pixel, and the ray runs 0.05 meters in front of it. A block is skipped when the ray's distance is below the block's nearest surface.

   ```cpp sketch="indirect-ssr-hiz.cpp"
   // A hierarchical march along a receding floor, in one dimension, against a linear march: how many reads each needs.
   #include <cstdio>

   constexpr int c_Pixels = 1024;
   constexpr int c_Levels = 10;

   // The floor's view distance at a pixel along the ray's way: it recedes by 0.1 m a pixel.
   float FloorDistance(int pixel)
   {
   	return 10.0f + 0.1f * static_cast<float>(pixel);
   }

   // The ray runs just in front of the floor, 0.05 m nearer than the surface at its own pixel.
   float RayDistance(int pixel)
   {
   	return FloorDistance(pixel) - 0.05f;
   }

   // The nearest distance inside the aligned cell of 2^level pixels that holds `pixel`: the floor recedes, so its first pixel.
   float NearestInCell(int pixel, int level)
   {
   	return FloorDistance((pixel >> level) << level);
   }

   // Reads until the ray has crossed the floor's pixels. A ray that runs diagonally over the screen enters each new cell
   // `entryShift` pixels past its edge (the rows of the coarse grid and the ray do not line up).
   int CountHierarchicalReads(int entryShift)
   {
   	int reads = 0;
   	int level = c_Levels;
   	int pixel = entryShift;
   	while (pixel < c_Pixels && reads < 4096)
   	{
   		reads++;
   		if (RayDistance(pixel) < NearestInCell(pixel, level))
   		{
   			pixel = (((pixel >> level) + 1) << level) + entryShift; // In front of everything in the cell: skip it
   			level = level < c_Levels ? level + 1 : level;
   		}
   		else if (level > 0)
   			level--; // Something in the cell may be nearer than the ray: look closer
   		else
   			break; // A single pixel in front of the ray: a hit
   	}
   	return reads;
   }

   int main()
   {
   	std::printf("floor receding 0.1 m a pixel, ray 0.05 m in front of it, %d pixels long\n", c_Pixels);
   	std::printf("linear march of 32 steps: 32 reads\n");
   	std::printf("hierarchical march, entering each cell on its edge: %d reads\n", CountHierarchicalReads(0));
   	std::printf("hierarchical march, entering each cell 1 pixel in: %d reads\n", CountHierarchicalReads(1));
   	return 0;
   }
   ```

   ```text output-of="indirect-ssr-hiz.cpp"
   floor receding 0.1 m a pixel, ray 0.05 m in front of it, 1024 pixels long
   linear march of 32 steps: 32 reads
   hierarchical march, entering each cell on its edge: 1 reads
   hierarchical march, entering each cell 1 pixel in: 1033 reads
   ```

   1. **Lines 20–23:** the nearest surface of an aligned block of $2^{level}$ pixels is the floor at the block's first pixel.
   2. **Lines 35–38:** the ray is in front of everything in the block, so the march skips it and tries a coarser level.
   3. **Lines 40–41:** the ray is not in front of the block's nearest surface, so the march looks at a finer level.

   When the ray enters each block on its edge, one read skips the whole floor. A ray that runs diagonally over the screen enters each block a pixel inside, where the block's nearest pixel lies behind the ray's start. No level above the finest can skip it, so the march reads every pixel: 1,033 reads against 32. The linear march reads 32 times and can miss a thin feature of the floor. Strata's Spatial trace therefore uses a fixed number of steps over the line and validates the crossing it finds.
   :::

## Where it lives in Strata

- Shaders: `Strata/shaders/Include/ScreenReflections.slang`, and `Strata/shaders/Effects/ScreenSpaceReflections.comp.slang`, `ScreenSpaceReflectionsSpatial.comp.slang` and `ReflectionResolve.comp.slang` in the same folder as the first. The surface target is in `Strata/shaders/Scene/DepthPrepass.frag.slang`, and the mix in `Strata/shaders/Scene/Forward.frag.slang` and `Strata/shaders/Include/IndirectLight.slang`.
- Code: `SceneRenderer::TraceScreenReflections` and `SceneRenderer::TraceSpatialReflections` in `Strata/src/Strata/Renderer/SceneRendererScreenReflections.cpp`; `ReflectionsQuality` and `ScreenReflectionSteps` in `Strata/src/Strata/Renderer/RendererQuality.h`.
- Tests: `GPU.SceneRenderer.SSR`, `GPU.SceneRenderer.IndirectFlicker`, `Renderer.ReflectionMetrics`.
- Settings: the Post Process fields `ScreenSpaceReflections`, `ScreenSpaceReflectionsIntensity` and `ScreenSpaceReflectionsMaxRoughness`, and the quality row `Reflections`.

## Further reading

- Morgan McGuire and Michael Mara, "Efficient GPU Screen-Space Ray Tracing" (Journal of Computer Graphics Techniques, 2014): the march in screen space with perspective-correct depth. Intermediate.
- Tomasz Stachowiak, "Stochastic Screen-Space Reflections" (SIGGRAPH 2015): one ray per pixel with temporal reuse. Advanced.
- Yasin Uludag, "Hi-Z Screen-Space Cone-Traced Reflections" (GPU Pro 5): the hierarchical march. Advanced.
- Strata's lighting manual, `Docs/Manual/Lighting.md`: the settings for game makers. Beginner.
