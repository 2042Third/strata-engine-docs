---
id: indirect/ao
title: "Ambient occlusion without history"
description: "How Strata darkens the creases of indirect light from depth and normals alone, in one frame, and why no history is needed."
kind: internals
size: L
tracks: [E]
needs: [indirect/seam, gpu/compute, basics/signals]
time: 85
learn:
  - id: gtao
    text: explain how GTAO turns two horizons per slice into one visibility
  - id: no-history
    text: explain why a fixed 4x4 pattern and a tent resolve make a complete image in one frame
  - id: radius
    text: compute the radius on screen that a radius in metres gets, clamp included
  - id: multi-bounce
    text: explain why multi-bounce lifts a bright crease more than a dark one
  - id: change-safely
    text: name the rules that a change to ambient occlusion must keep
since: 0.3.0
status: final
---

Light that arrives from the sky and the walls reaches a point in a crease less than it reaches a point in the open. Ambient occlusion computes how much less. Strata computes it in screen space. A compute pass reads the depth and the normals that the prepass wrote and finds how much of the sky each pixel sees, and a second pass cleans the result. It darkens only the indirect light, never the sun or a lamp, and needs no frame before the current one.

This page covers the two passes, the rules that keep them free of history, and how the forward pass uses their result. It does not cover the occlusion map of a material, which belongs to [materials](../light/materials.md), nor the way the gathers use the terms, which the page on [the seam](seam.md) teaches.

## The problem and how engines solve it

Stand a box on a floor. The floor beside the box sees the whole sky above it. The floor at the foot of the box has a wall on one side that hides part of that sky. The sun's shadow map handles the sun, but the sky and the bounced light come from every direction, and no shadow map holds them. A :term[renderer]{id=renderer} that adds the same ambient light to every pixel makes the foot of the box as bright as the open floor, and the image looks flat.

**Ambient occlusion** (AO) is the share of the ambient light that a point still receives when nearby geometry hides part of its surroundings. A value of 1 means the point sees everything, and 0 means it sees nothing. The renderer multiplies the indirect light by it.

Two definitions exist. Visibility counts what the point sees: the cosine-weighted share of the hemisphere above it that is free. The :term[cosine]{id=cosine} weight comes from the light's angle: light from straight above counts fully, and light from near the horizon counts little. The older approach, **obscurance**, darkens by distance instead: a blocking surface close to the point counts more than a far one, with no regard for angles. Strata computes visibility, with a short fade by distance so that far geometry does not darken.

Take a point on a floor with a long wall to its right, and look at one slice of the world that cuts straight through both. The wall hides the lowest 45 degrees of the sky on that side. Light from near the horizon counts little, yet that strip still carries half of that side's light. The other side sees everything, so the point keeps $0.5 \times (1 + 0.5) = 0.75$ of the open floor's light.

::compare{id=ao-off-on}

Engines meet this problem in five ways, and each costs something.

| Method | What it does | What it costs |
| --- | --- | --- |
| Screen-space ambient occlusion (SSAO) | Compares random points around the pixel with the :term[depth buffer]{id=depth-buffer} | Noise, grey halos, no angles |
| Horizon-based ambient occlusion (HBAO) | Marches horizons across the screen in several directions | Needs a falloff to hide error, still noisy |
| Ground-truth ambient occlusion (GTAO) | Integrates the cosine weight of the visible arc per slice | A few samples per pixel, then a resolve |
| Baked AO maps | Stores the result per surface in a texture | Static: moving objects change nothing |
| Ray-traced AO | Shoots rays into the scene | Ray hardware or a world structure, then a cleaning pass |

The first three work in screen space: they read only the depth buffer and the normals, so they cost the same for any scene. GTAO is the one Strata uses, from a paper of 2016 in the further reading. It aims at the integral that many random rays would estimate, and computes it per slice with none. A baked map cannot follow a door that opens, though Strata does read one: the material's occlusion map.

The second idea is about noise. A pixel that takes 8 samples of a hemisphere gets a rough answer, and neighbors get different rough answers. Many engines pick a new random pattern each frame and let temporal anti-aliasing (TAA) average the frames. That works only with history: the image ghosts behind moving objects, needs frames to settle, and keeps its noise under fast approximate anti-aliasing (FXAA) or none. The page on [TAA](../image/taa.md) explains why Strata refuses this: nothing in the image should need history to look right.

Strata instead gives each pixel of a 4x4 block a different, fixed rotation. All 16 rotations exist in every block, in every frame. A cheap spatial filter then averages a 5x5 block of neighbors, which together saw all 16 rotations. The result is complete in one frame and identical in the next, if the view does not change.

## The map

Three files share the job. `SceneRendererAmbientOcclusion.cpp` holds the :term[central processing unit]{id=processor} (CPU) side: `RenderAmbientOcclusion` fills the settings and records two dispatches. `GTAO.comp.slang` computes the raw visibility. `AODenoise.comp.slang` resolves and blurs it. The forward pass reads the result when it shades a pixel.

```mermaid caption="The prepass writes depth and normals. The first dispatch reads both and writes the raw occlusion, the second reads that and writes the occlusion the forward pass uses." alt="Boxes joined by arrows: depth and normals feed the first pass, its raw texture feeds the second pass, and the forward pass reads the texture of the second pass."
flowchart LR
	P["Depth prepass: depth and normals"] --> G["GTAO.comp: raw occlusion"]
	G --> D["AODenoise.comp: resolve, then blur"]
	D --> F["Forward pass: indirect light times occlusion"]
	C["RenderAmbientOcclusion: clamp, push constants"] --> G
	C --> D
```

The :term[main thread]{id=main-thread} records both dispatches into the frame's :term[command list]{id=command-list}, inside its own stage of the :term[graphics processing unit]{id=gpu} (GPU) timer, after the prepass. The pass runs only while the scene's `PostProcessComponent` has `AmbientOcclusion` on. Its fields are `AmbientOcclusion` (on by default), `AmbientOcclusionRadius` (1 m), `AmbientOcclusionIntensity` (1) and `AmbientOcclusionMultiBounce` (on).

Both targets have the viewport's size. Occlusion lies between 0 and 1, so a half-precision float holds it: the targets use the format `R16_FLOAT` where the device can store it in a compute :term[shader]{id=shader}, and `R32_FLOAT` where it cannot. The shader variants `GTAOHalf` and `AODenoiseHalf` are the same code compiled for the half format.

The quality row `AmbientOcclusionQuality` sets how many slices a pixel takes and how many steps each slice marches on each side.

| Level | Slices | Steps per side | Samples per pixel |
| --- | --- | --- | --- |
| `Low` | 1 | 4 | 8 |
| `Medium` | 2 | 6 | 24 |
| `High` | 3 | 8 | 48 |
| `Ultra` | 4 | 12 | 96 |

The last column is slices times steps times two sides. The renderer reports it as `AmbientOcclusionSamples` in its statistics. The page on [quality settings](../image/quality-settings.md) places this row among the others.

::compare{id=quality-rows}

## The contract

Four rules hold for this part, each with its reason.

- **AO darkens indirect light only.** Direct light has its own visibility, the shadow. Applying AO to the sun would darken a crease lit by the sun twice. Specular light uses a specular occlusion from Lagarde's course notes, shown at the end of the real code, never the raw value, because a mirror-like reflection sees a narrow cone, not the whole hemisphere.
- **No history.** The 4x4 pattern comes from the pixel's place in the screen, never from the frame number. The image is then the same under TAA, under FXAA and with neither, and a still view draws the same frame twice.
- **The radius is clamped on screen.** Whatever its size in metres, the radius covers between 0.3 % of the view's height (at least 1.5 pixels) and 12 % of it. The cost and the look then stay the same at every resolution, and a surface at the lens does not reach across the whole screen.
- **The multi-bounce fit changes only through the generator.** Run `Tools/FitAOMultiBounce.py --write`. Three generated copies must agree: the shader, a C++ :term[header]{id=header} and the test's reference. A test compares the header with the reference, and a GPU test compares the shader's image with the header.

## A toy version

The toy computes the occlusion of one slice over a 1D height field: a row of columns with heights, seen from the side. For each column it walks left and right, finds the highest rise per step, and turns the two slopes into one visibility.

:::question
Never read a loop, a function or a call such as `std::max(a, b)`? Read [variables and conditions](../basics/programming-1.md), [loops and functions](../basics/programming-2.md) and [classes and calls](../basics/programming-3.md) first.
:::

The function `Visibility` has the whole idea: one pass of steps on each side, a slope kept as the highest seen, and a formula at the end. Look at how the slope becomes a share of light.

```cpp sketch="indirect-ao-toy.cpp"
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <vector>

// Horizon occlusion of one slice over a 1D height field. The normal points straight up, so a horizon at elevation e
// leaves the share cos(e)^2 of that side's half of the cosine-weighted hemisphere.
float Visibility(const std::vector<float>& height, int column, int radius)
{
	float highest[2] = { 0.0f, 0.0f }; // tan(elevation) of the highest sample on the left and on the right
	for (int side = 0; side < 2; side++)
	{
		const int direction = side == 0 ? -1 : 1;
		for (int step = 1; step <= radius; step++)
		{
			const int sample = column + direction * step;
			if (sample < 0 || sample >= static_cast<int>(height.size()))
				break;
			const float rise = height[static_cast<size_t>(sample)] - height[static_cast<size_t>(column)];
			highest[side] = std::max(highest[side], rise / static_cast<float>(step));
		}
	}
	const float left = 1.0f / (1.0f + highest[0] * highest[0]);
	const float right = 1.0f / (1.0f + highest[1] * highest[1]);
	return 0.5f * (left + right);
}

int main()
{
	// Flat ground, with a wall 3 units high from column 10 on.
	std::vector<float> height(16, 0.0f);
	for (size_t column = 10; column < height.size(); column++)
		height[column] = 3.0f;

	for (int column = 3; column <= 9; column++)
		std::printf("column %2d: visibility %.3f\n", column, Visibility(height, column, 4));
	return 0;
}
```

```text output-of="indirect-ao-toy.cpp"
column  3: visibility 1.000
column  4: visibility 1.000
column  5: visibility 1.000
column  6: visibility 0.820
column  7: visibility 0.750
column  8: visibility 0.654
column  9: visibility 0.550
```

1. **Line 10:** the highest slope on each side starts at 0, the flat ground, because nothing hides the sky yet.
2. **Lines 14–20:** the loop walks outward one column per step. Dividing the rise by the step gives the slope of the line from the column to the sample; the highest slope is the horizon.
3. **Lines 23–25:** a horizon at elevation $e$ keeps the share $\cos^2 e$ of that side, and $\cos^2 e = 1/(1+\tan^2 e)$. The two sides are averaged.
4. **Lines 30–33:** the field is flat ground with a wall 3 units high from column 10 on.

The numbers fall as the column nears the wall: 1.000 where the radius cannot reach it, then 0.820, 0.750, 0.654 and 0.550 at its foot. Check the last by hand: the wall rises 3 in one step, so the slope is 3, $\cos^2 e = 1/10$, and the visibility is $0.5 \times (1 + 0.1) = 0.55$.

The real shader differs from the toy in three ways. It works in 3D, so a pixel takes several slices turned around the view direction. It works with the view vector, not with an :term[up axis]{id=up-axis}, because a surface has any normal. And it reads positions from the depth buffer.

## The pattern and the resolve, in a toy

Before the real code, a second toy shows why 16 phases and a 5x5 tent give a complete image. A **tent kernel** is a row of weights that rises and falls in a straight line, like a tent: here 0.5, 1, 1, 1, 0.5 over five pixels. The page on [signals](../basics/signals.md) teaches kernels. This one is flat in the middle and half as heavy at the ends, so that two ends that land on the same phase add up to one.

A pixel's phase is its place in the 4x4 block: its x and y, each the remainder after dividing by 4. Two pixels four apart share a phase. Take five taps centered on a pixel, at offsets -2 to 2. The offsets -2 and 2 are four apart, so they share a phase, and their weights 0.5 and 0.5 add up to 1. The three middle taps have the other three phases, each with weight 1.

All four phases of the row weigh 1. A column does the same, so the 25 taps of the 2D kernel give each of the 16 phases the weight 1.

The program below checks this for every center in a block and prints the weights for one.

```cpp sketch="indirect-ao-pattern.cpp"
#include <cstdio>

// How much weight each of the 16 phases of a 4x4 pattern receives from a 5x5 tent kernel centered on one pixel.
int main()
{
	const float tent[5] = { 0.5f, 1.0f, 1.0f, 1.0f, 0.5f };

	bool complete = true;
	for (int centerY = 0; centerY < 4; centerY++)
	{
		for (int centerX = 0; centerX < 4; centerX++)
		{
			float phaseWeight[4][4] = {};
			for (int offsetY = -2; offsetY <= 2; offsetY++)
			{
				for (int offsetX = -2; offsetX <= 2; offsetX++)
				{
					// The tap's phase is its pixel's place in the 4x4 block; +8 keeps the remainder positive.
					const int phaseX = (centerX + offsetX + 8) % 4;
					const int phaseY = (centerY + offsetY + 8) % 4;
					phaseWeight[phaseY][phaseX] += tent[offsetX + 2] * tent[offsetY + 2];
				}
			}
			for (int phaseY = 0; phaseY < 4; phaseY++)
				for (int phaseX = 0; phaseX < 4; phaseX++)
					complete = complete && phaseWeight[phaseY][phaseX] == 1.0f;

			if (centerX == 1 && centerY == 2)
			{
				std::printf("weights by phase for the pixel at cell (1, 2):\n");
				for (int phaseY = 0; phaseY < 4; phaseY++)
					std::printf("%.1f %.1f %.1f %.1f\n", static_cast<double>(phaseWeight[phaseY][0]), static_cast<double>(phaseWeight[phaseY][1]),
						static_cast<double>(phaseWeight[phaseY][2]), static_cast<double>(phaseWeight[phaseY][3]));
			}
		}
	}
	std::printf("every phase weighs 1 for every center: %s\n", complete ? "yes" : "no");
	return 0;
}
```

```text output-of="indirect-ao-pattern.cpp"
weights by phase for the pixel at cell (1, 2):
1.0 1.0 1.0 1.0
1.0 1.0 1.0 1.0
1.0 1.0 1.0 1.0
1.0 1.0 1.0 1.0
every phase weighs 1 for every center: yes
```

1. **Line 6:** the tent weights in one dimension.
2. **Lines 19–21:** each tap adds the product of its two weights to its phase. The `+ 8` keeps the remainder positive for negative offsets.
3. **Line 26:** the program records whether every phase of every center weighs exactly 1.
4. **Lines 28–35:** it prints the table of one pixel.

Every phase weighs 1, so the sum of all weights is 16. A kernel centered on a pixel keeps the pixel's own value at weight 1 and gathers the 15 other phases. The resolved value is the average over all 16 rotations of the slice. That average is what a pixel with 16 times more slices would have computed, one frame and no history needed.

## The real code, in the order data flows

### The CPU side

`RenderAmbientOcclusion` is the whole CPU side of a compute effect: it clamps the user's values, fills the :term[push constants]{id=push-constants} and makes two dispatches. Look at how each value from the component is checked before it reaches the shader.

```cpp src="Strata/src/Strata/Renderer/SceneRendererAmbientOcclusion.cpp#L116-L143"
void SceneRenderer::RenderAmbientOcclusion(nvrhi::ICommandList* commandList, const PostProcessComponent& settings)
{
	const AmbientOcclusionSamples samples = RendererQuality::GetAmbientOcclusionSamples(m_Specification.Quality.AmbientOcclusionQuality);
	const float height = static_cast<float>(m_ViewportSize.y);
	RenderData::AOParameters parameters = {};
	parameters.Radius = std::isfinite(settings.AmbientOcclusionRadius) ? std::clamp(settings.AmbientOcclusionRadius, 0.01f, 10.0f) : 1.0f;
	parameters.Intensity = std::isfinite(settings.AmbientOcclusionIntensity) ? std::clamp(settings.AmbientOcclusionIntensity, 0.0f, 8.0f) : 1.0f;
	parameters.SliceCount = samples.Slices;
	parameters.StepsPerSide = samples.StepsPerSide;
	parameters.MinRadiusPixels = std::max(RenderData::c_AOMinRadiusFraction * height, RenderData::c_AOMinRadiusPixels);
	parameters.MaxRadiusPixels = std::max(RenderData::c_AOMaxRadiusFraction * height, parameters.MinRadiusPixels);
	// The relaxation per step that keeps the relaxation per meter of 0.1 per step at 6 steps.
	parameters.ThinOccluderDecay = 1.0f - std::pow(0.9f, 6.0f / static_cast<float>(samples.StepsPerSide));
	m_Stats.AmbientOcclusionSamples = samples.Slices * samples.StepsPerSide * 2;

	nvrhi::ComputeState state;
	state.pipeline = m_GTAOPipeline;
	state.bindings = { m_GTAOBindingSet };
	commandList->setComputeState(state);
	commandList->setPushConstants(&parameters, sizeof(parameters));
	commandList->dispatch(DispatchGroups(m_ViewportSize.x, c_GTAOGroupSize), DispatchGroups(m_ViewportSize.y, c_GTAOGroupSize), 1);

	state.pipeline = m_AODenoisePipeline;
	state.bindings = { m_AODenoiseBindingSet };
	commandList->setComputeState(state);
	commandList->setPushConstants(&parameters, sizeof(parameters));
	commandList->dispatch(DispatchGroups(m_ViewportSize.x, c_DenoiseGroupSize), DispatchGroups(m_ViewportSize.y, c_DenoiseGroupSize), 1);
}
```

1. **Lines 118–120:** the quality row gives the slices and steps, and the viewport's height gives the scale for the radius limits.
2. **Lines 121–122:** a radius that is not a finite number becomes 1 m, and a finite one is kept between 0.01 and 10 m. The intensity is kept between 0 and 8. A scene file or a script can hold any number, so the renderer never trusts one.
3. **Lines 125–126:** the limits on screen: 0.3 % of the height, at least 1.5 pixels, and 12 % of the height, never below the lower limit.
4. **Line 128:** the decay of the thin-object relaxation, explained below.
5. **Lines 131–142:** two dispatches with the same push constants: the GTAO pass in groups of 8 by 8 pixels, then the cleaning pass in groups of 16 by 16.

### The radius on screen

A radius of 1 m has no fixed size in pixels. Near the camera it spans most of the screen; far away it spans less than a pixel. The shader projects the world radius to pixels and clamps it.

```slang src="Strata/shaders/Effects/GTAO.comp.slang#L62-L73"
float pixelsPerUnit = u_Frame.Projection[1][1] * 0.5 * u_Frame.ViewportSize.y;
if (u_Frame.CameraForward.w < 0.5)
	pixelsPerUnit /= max(-position.z, 1e-4);
// The radius on screen within its fractions of the view's height (cost and look independent of the resolution: distant
// creases keep a line, near surfaces do not reach across the screen); the world radius follows it.
float radiusPixels = clamp(u_AO.Radius * pixelsPerUnit, u_AO.MinRadiusPixels, u_AO.MaxRadiusPixels);
float radius = radiusPixels / pixelsPerUnit;

// The slices' rotation and the steps' offset from the 4x4 pattern (two orders of it, so they do not follow each other).
uint2 cell = uint2(pixel) & 3u;
float noise = (float(c_PatternOrder[cell.y * 4u + cell.x]) + 0.5) / 16.0;
float jitter = (float(c_PatternOrder[cell.x * 4u + cell.y]) + 0.5) / 16.0;
```

1. **Line 62:** pixels per metre at a distance of 1: the projection's vertical scale times half the viewport's height.
2. **Lines 63–64:** a perspective view divides by the distance; an orthographic view has one scale everywhere.
3. **Line 67:** the radius in pixels, kept within the two limits the CPU computed.
4. **Line 68:** the world radius follows the clamped one, so the fade by distance matches what the pixels cover.
5. **Lines 71–73:** the pixel's place in the 4x4 block picks two values from the ordered-dither order: one turns the slices and one moves the steps.

:::example[One radius at five distances]
A 1080-row view with a vertical :term[field of view]{id=field-of-view} of 60 degrees has $1/\tan 30^\circ \approx 1.732$ as its projection scale. At a distance of 1 m, a metre spans $1.732 \times 0.5 \times 1080 = 935$ pixels. The limits are $0.003 \times 1080 = 3.24$ pixels and $0.12 \times 1080 = 129.6$ pixels.

At 2 m a metre spans 468 pixels, so the radius of 1 m becomes 129.6 pixels and the world radius 0.277 m. At 5 m it spans 187 pixels, clamped to 129.6, which is 0.693 m. At 20 m it spans 46.8 pixels, inside the limits, and the radius stays 1 m. At 300 m it spans 3.12 pixels, which is raised to 3.24 pixels, so the world radius is 1.04 m. At 1,000 m it spans 0.94 pixels, raised to 3.24, and the world radius becomes 3.46 m.

The near clamp keeps a wall at the lens from darkening a whole screen. The far clamp keeps a crease far away visible as a line of a few pixels.
:::

::compare{id=radius-sweep}

The ordered-dither order in line 33 of the shader is the same table that `IsLODFadeDrawn` uses: every 4x4 block holds each of the 16 values once. Line 72 reads it by row and column, and line 73 by column and row, so the rotation and the jitter of one pixel do not follow each other.

### Slices and horizons

A **slice** is a plane through the pixel that contains the view direction. The shader turns it around the view axis by an angle $\varphi$, and each pixel takes `SliceCount` slices spread over half a turn, each shifted by the pixel's phase. In a slice the world is a 2D profile: the surface goes through the pixel, and the depth buffer gives its height on both sides.

The **horizon angle** is the angle, measured from the view direction, of the highest direction in the slice that the surface hides. Each side has one. Between them lies the arc the pixel can see. GTAO computes the cosine-weighted size of that arc in closed form.

```slang src="Strata/shaders/Effects/GTAO.comp.slang#L116-L126"
float3 delta = ViewPositionFromDepth(sampleUV, sampleDepth) - position;
float distance = length(delta);
if (distance < 1e-5)
	continue;
// Occluders fade out toward the radius so distant geometry does not darken.
float weight = clamp((radius - distance) / max(radius - falloffStart, 1e-4), 0.0, 1.0);
float sampleCos = lerp(lowHorizonCos[side], dot(delta / distance, view), weight);
// A sample above the horizon raises it; one below relaxes it toward itself (a thin occluder is seen by few
// samples, after which they fall back; a thick one's stay high and keep its occlusion).
horizonCos[side] = sampleCos > horizonCos[side] ? sampleCos
	: max(lerp(horizonCos[side], sampleCos, u_AO.ThinOccluderDecay), lowHorizonCos[side]);
```

1. **Line 116:** the sample's position from its depth, minus the pixel's, gives a direction and a distance.
2. **Line 121:** a sample's weight falls to 0 from 60 % of the radius out to the radius, so far geometry does not darken.
3. **Line 122:** the sample's cosine against the view, mixed with the open horizon by that weight.
4. **Lines 125–126:** a sample above the horizon raises it; a sample below it relaxes it, as the next part explains.

The horizons start at the edge of the hemisphere around the normal, where nothing hides the sky. Each step of each side raises them. After the loops the shader turns the two cosines into angles $h_0$ and $h_1$, clamps them to the hemisphere, and integrates.

```slang src="Strata/shaders/Effects/GTAO.comp.slang#L131-L136"
float h0 = n + clamp(-acos(horizonCos.y) - n, -0.5 * PI, 0.5 * PI);
float h1 = n + clamp(acos(horizonCos.x) - n, -0.5 * PI, 0.5 * PI);
float sinN = sin(n);
float arc0 = -cos(2.0 * h0 - n) + cosNormal + 2.0 * h0 * sinN;
float arc1 = -cos(2.0 * h1 - n) + cosNormal + 2.0 * h1 * sinN;
visibility += projectedLength * 0.25 * (arc0 + arc1);
```

The integral has a closed form, so no further sampling is needed. The result for a slice is the projected normal's length times a quarter of the two arcs' sum. The pixel's value is the mean over its slices, raised to the power `Intensity`: an intensity of 2 squares the occlusion, and 0 disables it.

$$ \text{arc} = -\cos(2h - n) + \cos n + 2h \sin n $$

In the formula $h$ is a horizon angle in :term[radians]{id=radian}, measured from the view direction. $n$ is the angle of the normal projected into the slice, from the view direction. The :term[sine]{id=sine} and cosine take radians.

:::example[One slice by hand]
Take a floor seen from straight above, so $n = 0$ and the normal points at the viewer. The arc becomes $1 - \cos 2h$, which is $2\sin^2 h$. A slice with horizons $h_0$ and $h_1$ gives $\tfrac14 (2\sin^2 h_0 + 2\sin^2 h_1) = \tfrac12 (\sin^2 h_0 + \sin^2 h_1)$.

With nothing in the way, both horizons are at the hemisphere's edge, $h = 90^\circ$, and the slice gives $\tfrac12 (1 + 1) = 1$. With a wall on one side whose top is 45 degrees above the floor, the horizon is 45 degrees from the normal: the elevation and the angle from the normal add up to 90 degrees. The sides give $\tfrac12 (0.5 + 1) = 0.75$. A V-shaped trench with both walls at 45 degrees gives $\tfrac12 (0.5 + 0.5) = 0.5$, and walls at 60 degrees give $0.25$. These are the numbers of the toy and of the problem section.
:::

::figure{id=slice-geometry}

### Thin objects

A depth buffer has no thickness. A pole 2 cm wide is a few pixels of near depth in front of a wall far behind. A method that keeps the highest sample as the horizon treats the pole like a solid block that fills everything behind it, and the wall around the pole's silhouette gets a dark halo.

Strata lets a horizon relax. When a sample lies below the horizon, the horizon moves toward it by a fraction `ThinOccluderDecay` per step. A thin pole is seen by a few steps, after which every sample falls back to the wall and the horizon falls too. A thick board keeps its samples high, so the horizon stays.

The decay depends on the number of steps, so that the same distance relaxes by the same amount at every quality: `1 - 0.9^(6/steps)`. At 6 steps (Medium) it is 0.1. At 4 steps it is 0.146, at 8 steps 0.076 and at 12 steps 0.051. The base 0.9 keeps the relaxation of 0.1 per step that 6 steps give.

:::example[A pole and a board at Medium]
Walk six steps along one side with a decay of 0.1. The horizon is a cosine: a larger value is a higher horizon. A pole shows its second sample at 0.8, and the other five at the wall's 0.2. The horizon jumps to 0.8, then moves a tenth of the way to 0.2 at each later step: 0.74, 0.686, 0.637 and 0.594.

A board shows samples two to four at 0.8, then two at 0.2, and ends at 0.686. Without relaxation both stay at 0.8. The pole leaves more light than the board, which is what the test `Thin occluders darken less than thick ones` expects.
:::

::figure{id=thin-poles}

::figure{id=relaxation-plot}

### The pattern, resolved

The raw texture still holds the pattern: neighbors disagree, because they used different rotations. `AODenoise.comp.slang` resolves it in one dispatch. Its header explains the design, and its constants size a shared tile.

```slang src="Strata/shaders/Effects/AODenoise.comp.slang#L26-L30"
static const int c_Group = 16;
static const int c_Threads = c_Group * c_Group;
static const int c_TileBorder = 4;                    // The resolve's 2 pixels plus the blur's 2
static const int c_Tile = c_Group + 2 * c_TileBorder; // 24: tile coordinates 0 to 23, the group's pixels at 4 to 19
static const int c_Resolved = c_Group + 4;            // 20: the resolved pixels the blur reads, tile coordinates 2 to 21
```

A group is 16 by 16 pixels and loads the 24 by 24 tile around them into group-shared memory (see [compute](../gpu/compute.md)): raw occlusion, linear depth and normal. The border of 4 is the resolve's 2 pixels plus the blur's 2. The group resolves the 20 by 20 pixels that its blur reads, then blurs into its own 16 by 16. Rows and columns run apart, five taps each, so a 5x5 kernel costs 10 taps, not 25.

```slang src="Strata/shaders/Effects/AODenoise.comp.slang#L68-L89"
float ResolveAlong(int2 center, bool alongRows)
{
	float4 centerNormalDepth = s_NormalDepth[TileIndex(center.x, center.y)];
	if (centerNormalDepth.w <= 0.0)
		return 1.0;
	int2 step = alongRows ? int2(1, 0) : int2(0, 1);
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

1. **Line 68:** `center` is a tile pixel; `alongRows` says whether it reads raw values along a row or the row results along a column.
2. **Lines 70–72:** a background pixel (depth 0) has no occlusion, and returns 1.
3. **Line 74:** the depth weight scales with the center's own depth, so it is relative.
4. **Lines 83–84:** each tap's weight is its tent weight times a depth weight $e^{-50 \Delta z / z}$ times a normal weight, the cosine of the angle between the normals to the 8th power. A tap on another surface weighs almost nothing, so the resolve never mixes a wall into the floor.
5. **Line 89:** the center's weight is 1, so the sum of weights is at least 1 and the division is safe.

On a surface that faces the camera, every tap has the same depth and normal as the center. The weights are the pure tent, each phase weighs 1, and the resolve is exact. On a slanted surface, the depth differences between neighbors cut some taps, and a few phases weigh a little less. A small error remains, and the test below bounds it.

::figure{id=pattern-tent}

::compare{id=aa-modes}

After the resolve, a second bilateral blur over 5 by 5 pixels, weighted by depth only, removes what remains. The blur is the one that Strata 0.6.0 had. The page on [sun shadows](../light/sun-shadows-2.md) explains why an edge-aware blur keeps edges.

### Multi-bounce

AO as computed so far treats whatever blocks the sky as black. A real wall is not black: it reflects part of the light it gets, and some of that returns to the crease. A white plaster corner is much brighter than a dark soil corner of the same shape, and AO alone darkens both the same. **Multi-bounce AO** fixes this: it raises the occlusion toward 1 by the light that the crease's own walls send back, which depends on the surface's :term[albedo]{id=albedo}.

Start with a point of visibility $x$ in a cavity whose walls have albedo $\rho$ and are lit like the point. The point gets $x$ straight from the sky. The rest of its directions, $1 - x$, face walls, which send back the share $\rho$ of what they get. The point's total $y$ then obeys $y = x + \rho (1 - x)\, y$, which gives $y = x / (1 - \rho (1 - x))$. This closed form assumes the whole surrounding has the same lighting, which a real crease does not have.

Strata keeps the form and fits one more term to a reference. The reference is 2D radiosity in V-grooves and rectangular trenches with an exact solution. The result is a small formula, written by a generator.

```slang src="Strata/shaders/Include/AmbientOcclusionFit.slang#L9-L15"
static const float4 c_AOMultiBounce = float4(1.330869513, -0.657153797, -0.354764681, 0.678682648);

float3 AOMultiBounce(float visibility, float3 albedo)
{
	float3 enclosure = albedo * (1.0 - visibility) * (c_AOMultiBounce.x + c_AOMultiBounce.y * visibility + albedo * (c_AOMultiBounce.z + c_AOMultiBounce.w * visibility));
	return visibility / max(1.0 - enclosure, float3(max(visibility, 1e-4)));
}
```

The fit reads $y = x / (1 - \rho (1 - x) h)$, where $x$ is the visibility, $\rho$ the albedo, and $h = p_0 + p_1 x + p_2 \rho + p_3 \rho x$ the fitted term. The coefficients $p_0$ to $p_3$ are the four numbers of `c_AOMultiBounce`. The function works per :term[color channel]{id=color-channel}.

Two limits hold by design. At $x = 1$ the result is 1, because nothing blocks the sky. At $\rho = 0$ it is $x$, because black walls reflect nothing. The result is never above 1 and never below $x$.

:::example[A white corner and a dark corner]
Take a corner with visibility 0.5. For an albedo of 0.8, plaster, the term $h$ is 0.99, the enclosure term is $0.8 \times 0.5 \times 0.99 = 0.396$, and the result is $0.5 / (1 - 0.396) = 0.83$. The corner is much lighter than AO alone says.

For an albedo of 0.1, soil, $h$ is 1.0, the enclosure term is 0.05, and the result is 0.526. Dark soil keeps its dark crease. The closed form gives 0.833 and 0.526; the fit differs where real cavities differ from the uniform case.
:::

::figure{id=multibounce-curves}

The script's own account explains why the fit is rational. The first plan was a polynomial $y = x + \rho x (1 - x)(p_0 + p_1 x + p_2 \rho + p_3 \rho x)$. It must go to 0 with $x$, but walls of high albedo light even deep creases, so the polynomial misses the reference by far more than the allowed error. The rational form follows the physical closed form and needs only a fitted correction. The authors of GTAO propose a polynomial in the visibility whose coefficients depend on the albedo; the further reading names their paper.

The reference is not a function of $x$ and $\rho$ alone: two strips of different cavities with the same visibility get different light from their walls. So the fit uses the reference's conditional means, the best any function of the two can do, and the test allows 0.03 of error against them.

### Where AO applies

The forward pass multiplies the AO texture into the diffuse indirect light only.

```slang src="Strata/shaders/Scene/Forward.frag.slang#L405-L413"
float screenOcclusion = u_Frame.AOParams.x > 0.0 ? u_AmbientOcclusion.Load(int3(int2(st_FragCoord.xy), 0)).r : 1.0;
#endif
float diffuseOcclusion = surface.Occlusion * screenOcclusion;
if (lightingView == ST_LIGHTING_VIEW_AMBIENT_OCCLUSION)
	return float3(diffuseOcclusion);
// Multi-bounce (AOParams.y): occluded corners keep the light their walls, of the surface's diffuse albedo, reflect into
// them (Include/AmbientOcclusionFit.slang). Diffuse light only; specular occlusion keeps the visibility.
float3 diffuseOcclusionColor = u_Frame.AOParams.y > 0.0 ? AOMultiBounce(diffuseOcclusion, surface.Albedo * (1.0 - surface.Metallic))
	: float3(diffuseOcclusion);
```

Transparent surfaces take no screen occlusion: it is 1 for them. The value is the material's occlusion times the screen's. The multi-bounce term then lifts it by the surface's diffuse albedo, `Albedo * (1 - Metallic)`: a metal has no diffuse color to bounce. It also works when the screen occlusion is off, so a material's own occlusion map gets it too.

Specular light does not take the multi-bounce value. It takes the **specular occlusion** of Lagarde, the occlusion of a reflection, which depends on how smooth the surface is and from where it is seen.

```slang src="Strata/shaders/Scene/Forward.frag.slang#L229-L233"
inputs.SpecularOcclusion = inputs.Form == ST_INDIRECT_AMBIENT ? 1.0
	: clamp(pow(NoV + diffuseOcclusion, exp2(-16.0 * surface.Roughness - 1.0)) - 1.0 + diffuseOcclusion, 0.0, 1.0)
	* GetFrameHorizonFade(inputs.Reflected, geometricNormal);
// The same on the material's occlusion alone, for what screen-space reflections found (exactly 1 without an occlusion map).
inputs.ScreenReflectionOcclusion = clamp(pow(NoV + surface.Occlusion, exp2(-16.0 * surface.Roughness - 1.0)) - 1.0 + surface.Occlusion, 0.0, 1.0);
```

The formula is $\text{clamp}(( N{\cdot}V + a )^{2^{-16 r - 1}} - 1 + a)$, where $a$ is the occlusion, $N{\cdot}V$ the cosine between the normal and the view, and $r$ the roughness. For a rough surface the :term[exponent]{id=exponent} goes to 0, so the power goes to 1 and the result to $a$. For a smooth surface the exponent is below 1. Seen from the front, the base is above 1 and the result is higher than $a$: a mirror sees a narrow cone, and the cone is less hidden than the hemisphere. At a grazing view the base falls below 1 and the result below $a$.

:::example[Specular occlusion for three views]
Let $a = 0.5$. At $N{\cdot}V = 0.7$ and roughness 0.5 the exponent is $2^{-9}$, and the result is 0.500: rough surfaces use the occlusion as it is. At the same view and roughness 0, the exponent is 0.5, and the result is $\sqrt{1.2} - 0.5 = 0.595$. At a grazing view, $N{\cdot}V = 0.05$, and roughness 0 it is $\sqrt{0.55} - 0.5 = 0.242$: a grazing mirror sees the crease's walls and is darker.
:::

Line 231 multiplies the result by `GetFrameHorizonFade`, the fade for reflections that a :term[normal map]{id=normal-map} turns into the surface (a capture can disable it), taught on the page about [image-based light](ibl.md). Under the constant ambient light, line 229 gives specular occlusion 1. Line 233 repeats the formula with the material's occlusion alone, for what the screen-space reflections found: they saw the real scene, so the screen's AO must not darken them again. Their page, [reflections](ssr.md), explains the rest.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| `HBAO+` | Engines that license NVIDIA's library | A tuned implementation | A vendor dependency and its own noise filter |
| GTAO with temporal accumulation | Engines whose TAA is always on | Fewer samples per frame | A look that depends on the anti-aliasing mode, and ghosting |
| Ray-traced AO | Engines with ray hardware | Occlusion of off-screen geometry | A device requirement, a world structure and a cleaning pass that needs history |
| Bent normals and cones | Engines that store a visible direction per pixel | Better specular occlusion | A second texture and more work in each shader |
| Baked AO maps | Engines with static levels | No cost at run time | Nothing moves; this is the material's map, not this pass |

## How it is tested

Two suites cover this part. `Renderer.AmbientOcclusion` holds one test, "The multi-bounce fit matches its radiosity reference and keeps its bounds". It needs no :term[graphics processing unit]{id=gpu} (GPU). It compares the fit with each conditional mean of the generator's reference within 0.03.

For albedos from 0 to 1 it checks four limits. The result is 1 at full visibility and equals the visibility at albedo 0. It stays between the visibility and 1, and never falls as visibility or albedo grows.

`GPU.SceneRenderer.AmbientOcclusion` renders small scenes and reads the occlusion back. "Ambient occlusion has no pattern without TAA at any quality" measures floor pixels in a row in front of a box. Each must differ from the mean of its two neighbors by at most 0.02 % root mean square (RMS). That holds at all four levels, with FXAA and with none, and two frames of a still view must be equal.

Two more tests check the counts 8, 24, 48 and 96, and the radius limits on a near and a far box. Another checks that a pole 2 cm wide darkens less than a board 1 m wide. A last one compares multi-bounce with the fit on a bright albedo.

Run them with `StrataTests.exe --test-suite=Renderer.AmbientOcclusion` and with `--test-suite=GPU.SceneRenderer.AmbientOcclusion`. The second needs a GPU.

## Changing it safely

- **Keep the frame out of the pattern.** The pattern may come from the pixel and nothing else. Adding the frame number makes "no pattern without TAA" fail; exercise 4 tries it.
- **Change the fit only with the generator.** Edit `Tools/FitAOMultiBounce.py`, run it with `--write`, and commit the three files together.
- **Keep the radius clamp.** The limits are `c_AOMinRadiusFraction`, `c_AOMaxRadiusFraction` and `c_AOMinRadiusPixels` in `SceneRenderData.h`; the shader clamps with what the CPU sends.
- **Keep the tent whole.** A new pattern size needs a kernel that weighs each phase once, and new tile constants.
- **Leave direct light alone.** A new indirect term takes the occlusion, a new reflection takes the form of Lagarde, and nothing direct takes either.

## What went wrong before

:::history
Strata 0.6.0 took two slices of six steps per pixel with interleaved noise, then blurred it within depth edges, and let TAA average the rest. Its test comment records the cost: at Medium the noise left 0.11 % of the occlusion in a row of pixels, 0.55 % at Low and 0.04 % at High. Version 0.7.0 replaced it with the fixed pattern and the resolve, which leave under 0.01 %, and added the radius clamp, the thin-object relaxation and multi-bounce. Its release notes tell game makers that turning **Ambient Occlusion Multi Bounce** off brings back the darker creases of 0.6.0.
:::

## Summary

- GTAO turns two horizon angles in each of a few slices into a cosine-weighted visibility, in closed form, from depth and normals.
- A fixed 4x4 pattern and a 5x5 tent whose weights 0.5, 1, 1, 1, 0.5 weigh each of the 16 phases once give a complete image in one frame, with no history.
- The radius in metres is projected to pixels and clamped between 0.3 % (at least 1.5 pixels) and 12 % of the view's height, so cost and look hold at every resolution.
- Multi-bounce uses a rational fit to radiosity, so a bright corner keeps much of its light and a dark one stays dark; the generator is the only way to change it.
- A change must keep four rules: indirect light only, no history, the radius clamp and the generated fit.

## Check yourself

1. In a slice, the left horizon is 60 degrees from the normal of a flat floor seen from above, and the right one is 90 degrees. What is the slice's visibility?

   :::answer{tests="gtao"}
   Visibility is $\tfrac12 (\sin^2 60^\circ + \sin^2 90^\circ) = \tfrac12 (0.75 + 1) = 0.875$. The wrong answer 0.75 is the left side alone, without the average, and 0.625 uses $\cos^2$ of the angle from the normal, a formula that takes the elevation.
   :::

2. Why does a Gaussian of five taps not resolve the pattern, while the tent 0.5, 1, 1, 1, 0.5 does? (a) A Gaussian is slower. (b) A Gaussian weighs some of the 16 phases more than others. (c) A tent needs history.

   :::answer{tests="no-history"}
   Option (b). Option (a) is false: the cost is the same. Option (c) is false: the tent needs no history, which is its point. Its ends, at offsets -2 and 2, share a phase, so the two halves weigh that phase once.
   :::

3. A view of 1080 rows, a field of view of 60 degrees and the radius 1 m. A surface is 10 m away. What is the radius on screen, and what is the world radius after the clamp?

   :::answer{tests="radius"}
   A metre spans $935.3 / 10 = 93.5$ pixels. It lies between 3.24 and 129.6, so the radius stays 93.5 pixels and 1 m.
   :::

4. A white corner and a dark corner both have visibility 0.5. Which gets the larger multi-bounce value, and why?

   :::answer{tests="multi-bounce"}
   The white one: 0.83 against 0.53. Its walls reflect 80 % of the light that reaches them, and part of it goes into the corner. A dark wall reflects 10 %. AO alone gives both 0.5.
   :::

5. A programmer multiplies the AO texture into the sun's light "to ground the objects better". Which rule breaks, and what does the image show?

   :::answer{tests="change-safely"}
   The rule that AO darkens indirect light only. The side of every crease that the sun lights gets darker than its shadow map says, so the contact shadows count twice.
   :::

## Exercises

1. **Basic.** Trace it yourself. Follow `AmbientOcclusionRadius` from the component to the pixel's radius. Name the file and the function where it is clamped to 0.01 to 10 m, and the line where the shader projects it.

   :::answer[Worked solution]{tests="radius,change-safely"}
   Search for `AmbientOcclusionRadius` in `Strata/src/Strata/Renderer/`. The component is in `RendererComponents.h`. `SceneRenderer::RenderAmbientOcclusion` in `SceneRendererAmbientOcclusion.cpp` clamps it to 0.01 to 10 m and sets the limits in pixels from the viewport's height. In `GTAO.comp.slang`, line 62 computes the pixels per metre and line 67 clamps the projected radius. For a surface at 2 m in a 1080-row view the result is 129.6 pixels, 0.277 m.
   :::

2. **Medium.** Compute the multi-bounce value for visibility 0.25 and albedo 0.6 with the fit, and with the closed form. How far apart are they?

   :::answer[Worked solution]{tests="multi-bounce"}
   The term $h = 1.3309 - 0.6572 \times 0.25 + 0.6 \times (-0.3548 + 0.6787 \times 0.25) = 1.1666 - 0.1111 = 1.0555$. The enclosure term is $0.6 \times 0.75 \times 1.0555 = 0.4750$ and the fit gives $0.25 / 0.5250 = 0.476$. The closed form gives $0.25 / (1 - 0.45) = 0.4545$. They differ by 0.022. The test's 0.03 is against the radiosity reference, not against this closed form.
   :::

3. **Medium.** Write a program that walks the pole and the board of the example for a decay of 0 and of 0.1. Which values of the decay would let the pole and the board end with the same horizon, and is either a good choice?

   :::answer[Worked solution]{tests="gtao,no-history" solution="sketches/indirect-ao-relax.cpp"}
   The program below walks both profiles for each decay.

   ```cpp sketch="indirect-ao-relax.cpp"
   #include <algorithm>
   #include <cstdio>

   // The horizon, as the cosine of its angle to the view, after six samples along one side of a slice.
   float Walk(const float (&samples)[6], float decay)
   {
   	const float edge = 0.0f; // The horizon of the hemisphere itself: nothing occludes
   	float horizon = edge;
   	for (float sample : samples)
   	{
   		if (sample > horizon)
   			horizon = sample;
   		else
   			horizon = std::max(horizon + (sample - horizon) * decay, edge);
   	}
   	return horizon;
   }

   int main()
   {
   	const float pole[6] = { 0.2f, 0.8f, 0.2f, 0.2f, 0.2f, 0.2f };
   	const float board[6] = { 0.2f, 0.8f, 0.8f, 0.8f, 0.2f, 0.2f };
   	const float decays[2] = { 0.0f, 0.1f };
   	for (float decay : decays)
   		std::printf("decay %.1f: pole %.3f, board %.3f\n", static_cast<double>(decay), static_cast<double>(Walk(pole, decay)),
   			static_cast<double>(Walk(board, decay)));
   	return 0;
   }
   ```

   ```text output-of="indirect-ao-relax.cpp"
   decay 0.0: pole 0.800, board 0.800
   decay 0.1: pole 0.594, board 0.686
   ```

   1. **Line 7:** the horizon of the hemisphere, the floor that a horizon cannot fall below.
   2. **Lines 11–14:** a higher sample raises the horizon at once; a lower one moves it a fraction of the way.
   3. **Lines 21–22:** a pole with one high sample, and a board with three.
   4. **Lines 24–26:** the program prints the horizon for each decay.

   Only the two ends make them equal. A decay of 0 leaves both at 0.8: the pole darkens as much as a board. A decay of 1 drops the horizon to each sample at once, so both end at 0.2 and the board loses its occlusion too. Between them the pole falls faster than the board. Neither end is a good choice: the difference is the point.
   :::

4. **Hard.** On a scratch branch, change the pattern so that it depends on the frame, and run `GPU.SceneRenderer.AmbientOcclusion`. Which test fails, and why?

   :::answer[Worked solution]{tests="no-history,change-safely"}
   Add the frame's index to the cell in `GTAO.comp.slang`, for example by shifting the cell's x. Then "Ambient occlusion has no pattern without TAA at any quality" fails: two frames of a still view differ, and without TAA nothing averages the pattern. The pixel row no longer sits within 0.02 % RMS of its neighbors' mean. Undo the change.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Renderer/SceneRendererAmbientOcclusion.cpp`: `SceneRenderer::RenderAmbientOcclusion` and the targets.
- `Strata/shaders/Effects/GTAO.comp.slang` and `Strata/shaders/Effects/AODenoise.comp.slang`: the two passes.
- `Strata/shaders/Include/AmbientOcclusionFit.slang`, `Strata/src/Strata/Renderer/AmbientOcclusionFit.h` and `Tools/FitAOMultiBounce.py`: the fit and its generator.
- `Strata/shaders/Scene/Forward.frag.slang`: where AO and Lagarde's specular occlusion apply.
- `Strata/src/Strata/Renderer/RendererQuality.h`: `AmbientOcclusionLevel`.
- `Strata/src/Strata/Renderer/RendererComponents.h`: the component's fields.
- `StrataTests/src/Renderer/AmbientOcclusionFitTests.cpp` and `StrataTests/src/Renderer/GPUSceneAmbientOcclusionTests.cpp`: the suites.

## Further reading

- Jorge Jimenez, Xian-Chun Wu, Angelo Pesce and Adrian Jarabo, "Practical Real-Time Strategies for Accurate Indirect Occlusion" (paper, 2016; advanced): GTAO, its multi-bounce polynomial and its use of a denoiser.
- Sebastien Lagarde and Charles de Rousiers, "Moving Frostbite to Physically Based Rendering" (course notes, 2014; advanced): the specular occlusion Strata uses.
- Louis Bavoil, Miguel Sainz and Rouslan Dimitrov, "Image-Space Horizon-Based Ambient Occlusion" (talk, 2008; intermediate): the horizons that GTAO integrates.
- Physically Based Rendering, the chapter on light transport (book; advanced): why visibility and cosine weights carry the integral.
