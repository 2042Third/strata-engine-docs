---
id: indirect/gi-cascades
title: "Global illumination II: radiance cascades and the irradiance field"
description: "How Strata turns a voxel copy of the world into light on surfaces every frame: probes in cascades, a merge, a field and a join."
kind: internals
size: XL
tracks: [E]
needs: [indirect/gi-voxels, indirect/ao, light/measuring-light, basics/math-sphere, light/atmosphere]
time: 100
learn:
  - id: explain-cascades
    text: explain why a probe needs few directions and many places near it, and the reverse far away
  - id: compute-merge
    text: compute the light of a cascade's ray from its own interval and its parents' weights
  - id: explain-guard
    text: explain why Strata weighs probes by a voxel guard and floors the visible weight
  - id: compute-settle
    text: compute the frames a series of bounces needs to settle
  - id: trace-frame
    text: trace one frame of global illumination from the voxels to a pixel
since: 0.8.0
status: final
---

:term[Global illumination]{id=global-illumination} gives every lit pixel the light that other surfaces and the sky send to it after one bounce or many. This page follows one frame of that work, from a :term[voxel]{id=voxel} copy of the scene to the diffuse light of a pixel. The frame makes its light from the world alone: no screen data, no earlier picture and no blending over frames. The page does not build the voxels, which [Global illumination I: a voxel copy of the world](../indirect/gi-voxels.md) does. Nor does it list what the feature cannot do: [the limits of global illumination](../indirect/gi-limits.md) does that.

## The problem and how engines solve it

[The indirect-light problem](../indirect/problem.md) sets the problem out: a pixel needs light from surfaces that the screen does not show, and every cheap answer is wrong somewhere. Strata tries the direct answer, which is to trace the light in the world around the camera, every frame. The cost of tracing is the difficulty, and one idea, taught below, makes it affordable. The picture shows what the answer adds to a Cornell box, a plain room with a red wall, a green wall and one lamp.

::compare{id=cornell-off-on}

## The map: one frame, six passes

Every frame, after the passes that build the voxels, the :term[graphics processing unit]{id=gpu} (GPU) runs six passes in order. They run in one stage that the :term[profiler]{id=profiler-instrumenting-vs-sampling} shows after the :term[ambient occlusion]{id=ambient-occlusion} and before the reflections. The :term[central processing unit]{id=processor} (CPU) has already chosen which parts of the scene to turn into voxels, and the :term[main thread]{id=main-thread} only submits the passes.

A **probe** is a point in the world, on a regular grid around the camera, that gathers the light arriving from every direction.

A **cascade** is one grid of probes with its own spacing, its own number of directions and its own range of distances.

The first pass is **light injection**: it works out how much light each voxel sends back out, so that the later passes can treat the voxels as lamps.

```mermaid caption="The six passes of one frame, left to right, then the forward pass that reads the result. The dashed arrow carries the field of the frame before back into the voxels, which is how later bounces arrive." alt="A chain of boxes: the voxel levels, light injection, the level pass, probe validity, probe weights, the cascade march and the field reduce, then the forward pass. A dashed arrow runs from the field reduce back to light injection."
flowchart LR
    V["Voxel levels: albedo, normal, occupancy"] --> I["VoxelInject: the light each voxel sends"]
    I --> D["VoxelDownsample: coarse levels"]
    D --> A["ProbeValidity: dead probes, moves"]
    A --> W["ProbeWeights: eight parents each"]
    W --> M["CascadeMarch: top cascade down to 1"]
    M --> R["FieldReduce: cascade 0 into the field"]
    R --> G["Forward pass: gather and join"]
    R -.->|"next frame"| I
```

The passes in words:

- Injection lights every voxel of every level from the sun and the voxel's own glow, and, when bounces are on, from the field of the frame before.
- The level pass gives each coarse level the light of the finer level inside it, so that far marches see the same light as near ones.
- Validity marks the probes that sit inside solids, and moves the probes that sit on surfaces.
- Weights work out how much each probe may borrow from its eight parents in the next cascade.
- The march traces the rays of the cascades from the top one down to cascade 1, merging as it goes.
- The reduce traces cascade 0, finishes each ray with cascade 1's merged ray, and sums the result into the field.

The forward pass of the scene then reads the field for each pixel. At High the field covers 24 by 20 by 24 metres around the camera, and the cascades fire 10,506,240 rays a frame. The reference machine spends about 4.2 ms of GPU time on all of it at 3840 by 2160, which is 25 % of a frame at 60 :term[frames per second]{id=frame-rate}.

## The contract

The **irradiance field** is the result of the passes: for each probe of cascade 0, the light that arrives from each side of it, stored where the forward pass can read it. Callers may assume the first three rules below, and anyone who changes the code must follow the fourth.

- No history. The field is a function of the world's data and of where the camera stands now, never of where it stood. With one bounce, the frame after a sideways step equals the frame of a fresh :term[renderer]{id=renderer} placed at the same camera, bit for bit. With every bounce, the field of the frame before feeds the voxels by design, as the multi-bounce section shows.
- No blocking. A frame is **pending** while the voxels of the three finest levels do not yet cover their windows, which happens after a cut or a jump of the camera. A pending frame does not use the field, and its surfaces keep today's light, the light they had before the field existed.
- A frame is **settled** when the voxel work is done and the bounces no longer change the light. Captures wait only for that. The editor's `viewport.capture` and the project picture wait for a settled frame for at most 54 frames and then take the picture anyway. [The editor camera and viewport state](../editor/camera-viewport.md) shows what a capture reports.
- A separate buffer. The field's constants (its origin, size and fade, and the windows of the three finest voxel levels) travel in their own :term[constant buffer]{id=constant-buffer} at binding b3, not in the frame's constants.

:::rule[A frame without global illumination keeps the old light, bit for bit]
`AGENTS.md` asks that a frame without global illumination keeps the old expression of the :term[indirect light]{id=indirect-light} exactly. That holds when the scene did not ask for it, when the quality row is Off and while the field is pending. Tests can then compare the new engine with the old one pixel by pixel. [The limits of global illumination](../indirect/gi-limits.md) explains the decision and its cost.
:::

:::caution[The reason for the separate buffer is not known]
The engine's own documents report a puzzle. Declaring new fields in the frame's constants changed no :term[shader's]{id=shader} input, but every shader that includes the scene :term[header]{id=header} compiled again. Two passes then stopped repeating exactly from one capture to the next: the ambient occlusion and the screen-space reflections. A buffer of its own avoids the effect, and nobody found the cause. The rule that follows is practical: before you add a frame constant, check that the `ao` view of an unchanged scene still repeats.
:::

## Radiance cascades from zero

A probe wants the :term[radiance]{id=radiance} along every ray that reaches it. That sounds like a loop over directions, and the loop is the problem. Take a lamp 1 m wide at 16 m. It covers $1/16 = 0.0625$ :term[radians]{id=radian}, about 3.6 degrees, so a probe must space its rays 3.6 degrees apart to see it.

A sphere holds $4\pi \approx 12.57$ steradians (the unit of solid angle, from [the page on spheres](../basics/math-sphere.md)), and a 3.6 degree patch holds $0.0625^2 = 0.0039$, so the probe needs about 3,200 rays. Strata's High layout has 92,160 probes in cascade 0 alone, so the plain method fires $92{,}160 \times 3{,}200 \approx 295$ million rays a frame. That is 28 times the 10.5 million of the real layout.

### The penumbra condition

Place a lamp at distance $d$ from a probe, and a second probe $s$ metres to the side. The second probe sees the lamp in a direction that differs by about $s/d$ radians. If that difference is smaller than the angle between two neighbouring rays, the second probe can borrow the first probe's ray for that direction, and nobody notices.

The penumbra condition, named after the soft edge of a shadow, says how finely a probe must resolve places and directions: it depends on the distance of what the probe looks at. Near the probe, $d$ is small and $s/d$ is large. Probes must then stand close together, but the rays can be few, because a near object covers a wide angle. Far away, $s/d$ is small. Probes can then stand far apart, but a distant object covers a narrow angle, so the rays must be many.

:::example[Four cascades at High]
An $n \times n$ direction tile holds $n^2$ rays and covers $4\pi$ steradians, so one ray covers a patch about $\sqrt{4\pi}/n \approx 3.5/n$ radians wide. The table gives each cascade's spacing, tile and interval, and the ratio $s/d$ at the far end of its interval.

| Cascade | Probe spacing | Directions | Interval | Ray patch, radians | Spacing over far end |
| --- | --- | --- | --- | --- | --- |
| 0 | 0.5 m | 64 (8 by 8) | 0 to 0.5 m | 0.44 | 1.0 |
| 1 | 1 m | 64 (8 by 8) | 0.5 to 2 m | 0.44 | 0.5 |
| 2 | 2 m | 256 (16 by 16) | 2 to 8 m | 0.22 | 0.25 |
| 3 | 4 m | 1,024 (32 by 32) | 8 m onwards | 0.11 | none |

For cascades 1 and 2 the last two numbers nearly agree: a neighbour's view of something at the end of the interval differs by about one ray patch. That match is the design. The factors, 2 for the spacing and 4 for the interval, come from the published method named in the further reading.
:::

### Cascades, intervals and tiles

**Radiance cascades** are a stack of probe grids, each tracing only one stretch of every ray and handing the rest of the ray to the grid above it.

An **interval** is the stretch of distances along a ray that one cascade is responsible for. Cascade 1's interval starts where cascade 0's ends, and each interval ends four times as far out as the one before.

A **direction tile** is the square map of the ray directions of one probe: an :term[octahedral map]{id=octahedral-map} of the sphere with one texel per direction, so that 64 rays make an 8 by 8 tile.

Two things change with each step up. The probes get half as many per axis, which is one eighth as many in space, and the directions grow four times as many, except that cascade 1 keeps cascade 0's 64.

In cascades 1 and 2 each texel is also the mean of four rays spread over it, not one. Their texels are as wide as a room's patch of sunlight seen across the room, and one ray would catch it whole or miss it. At High the rays are therefore 5,898,240 for cascade 0 (92,160 probes times 64) and 2,949,120 for cascade 1. Cascade 2 fires 1,474,560 and cascade 3 fires 184,320, which sum to 10,506,240. Each cascade fires half as many as the one below, except the top one, which fires one eighth because it traces one ray a texel.

### The merge

Each ray of a cascade measures two things in its own interval: the light $L$ that it gathers, and the share $T$ of the light that passes through the interval without absorption. If the ray belongs to cascade $k$, the rest of it is the business of cascade $k+1$.

The **merge** continues the ray into the merged ray of its parents and adds the result.

$$R_k = L + T \cdot R_{k+1}$$

Here $R_k$ is the merged radiance of the ray, in :term[nits]{id=lux}. $L$ is the light the ray gathers inside its own interval, also in nits. $T$ is the transmittance of the interval, between 0 (absorbed) and 1 (free), and $R_{k+1}$ is the merged radiance that the parents give for the same direction.

A ray that ends on a surface has $T = 0$ and ignores everything beyond. The parents of a probe are the eight probes of the next cascade around it. Their weights are trilinear: on each axis, 0.75 for the near parent and 0.25 for the far one. Each parent adds the mean of the four of its directions that lie inside the child's texel.

:::example[One merged ray]
A child ray has $L = 2$ nits and $T = 0.6$. Its two near parents have weights 0.75 and 0.25. The first parent's four directions hold 8, 8, 4 and 4 nits, a mean of 6. The second parent's hold 14 nits each, a mean of 14.

With both parents, the merge divides by the weights it used: $(0.75 \times 6 + 0.25 \times 14) / 1 = 8$ nits, so $R_k = 2 + 0.6 \times 8 = 6.8$ nits. Now put a wall between the child and the second parent. The weights pass gives that parent weight 0, and the merge divides by 0.75 alone: $0.75 \times 6 / 0.75 = 6$ nits, so $R_k = 2 + 0.6 \times 6 = 5.6$ nits. The wall cost the ray 1.2 nits, because it removed a view that the child could not share.
:::

## A toy version: two cascades along a line

The toy puts probes on a line and lets them look at the half plane above it, where a lamp glows and a wall absorbs. Cascade 0 has probes 1 m apart with 8 directions and the interval 0 to 1 m. Cascade 1 has probes 2 m apart, 32 directions and the interval from 1 m outwards. The function `BruteForce` is the reference: it shoots 256 rays through each direction from the probe itself. The function `Cascaded` traces one short ray and merges two parents.

:::question
Never read a function, a loop or a call such as `std::cos(angle)`? Read [variables and conditions](../basics/programming-1.md), [loops and functions](../basics/programming-2.md) and [classes and calls](../basics/programming-3.md) first.
:::

Read `Cascaded` first. It holds the whole method in 19 lines: an own ray, a linear weight between two parents and a mean of parent directions.

```cpp sketch="indirect-gi-cascades-toy.cpp"
#include <cmath>
#include <cstdio>
#include <initializer_list>

// Two radiance cascades in a flat world. Probes stand on the line y = 0 and look at the half plane above it, where a lamp
// (a disc) glows and a wall absorbs. A direction is an angle from 0 to pi.
constexpr double c_Pi = 3.14159265358979323846;
constexpr double c_LampX = 4.0, c_LampY = 12.0, c_LampRadius = 3.0, c_LampRadiance = 10.0;
constexpr double c_WallX = 2.2, c_WallBottom = 2.0;
constexpr int c_ChildDirections = 8;   // Cascade 0: probes 1 m apart, the interval [0, 1)
constexpr int c_ParentDirections = 32; // Cascade 1: probes 2 m apart, four times the directions, the interval [1, far)
static double s_WallTop = 3.2;         // The wall stands from c_WallBottom to this height

struct Sample
{
	double Radiance = 0.0;
	double Transmittance = 1.0; // 0 when the ray ended on something
};

// The first thing a ray meets between two distances: the lamp lights it, the wall absorbs it.
Sample Trace(double originX, double angle, double start, double end)
{
	const double dx = std::cos(angle);
	const double dy = std::sin(angle);
	Sample result;
	const double ox = originX - c_LampX;
	const double oy = -c_LampY;
	const double b = ox * dx + oy * dy;
	const double discriminant = b * b - (ox * ox + oy * oy - c_LampRadius * c_LampRadius);
	if (discriminant >= 0.0)
	{
		const double t = -b - std::sqrt(discriminant);
		if (t >= start && t < end)
		{
			end = t;
			result = { c_LampRadiance, 0.0 };
		}
	}
	const double t = (c_WallX - originX) / dx;
	if (t >= start && t < end && t * dy >= c_WallBottom && t * dy <= s_WallTop)
		result = { 0.0, 0.0 };
	return result;
}

// What the cascades give for one of cascade 0's directions: its own short ray, then the merge of the parents' rays.
double Cascaded(double x, int direction)
{
	const Sample own = Trace(x, (direction + 0.5) * c_Pi / c_ChildDirections, 0.0, 1.0);
	const double coordinate = (x - 1.0) / 2.0; // The parents stand at 1, 3, 5 ... 2 m apart
	const int first = static_cast<int>(std::floor(coordinate));
	const double fraction = coordinate - first;
	double merged = 0.0;
	for (int corner = 0; corner < 2; corner++)
	{
		double mean = 0.0; // Four parent directions lie inside this one; each is the mean of four rays
		for (int k = 0; k < 16; k++)
		{
			const double angle = (direction * 4 + (k + 0.5) / 4.0) * c_Pi / c_ParentDirections;
			mean += Trace(1.0 + 2.0 * (first + corner), angle, 1.0, 1000.0).Radiance / 16.0;
		}
		merged += (corner == 0 ? 1.0 - fraction : fraction) * mean;
	}
	return own.Radiance + own.Transmittance * merged;
}

// The answer to compare with: many rays over the direction's whole range, each from the probe itself to the far end.
double BruteForce(double x, int direction)
{
	double sum = 0.0;
	for (int k = 0; k < 256; k++)
		sum += Trace(x, (direction + (k + 0.5) / 256.0) * c_Pi / c_ChildDirections, 0.0, 1000.0).Radiance;
	return sum / 256.0;
}

int main()
{
	for (const double top : { 2.0, 3.2 })
	{
		s_WallTop = top;
		std::printf("%s\n", top > c_WallBottom ? "with the wall" : "without the wall");
		for (const double x : { 1.5, 2.5 })
		{
			for (int direction = 0; direction < c_ChildDirections; direction++)
			{
				const double exact = BruteForce(x, direction);
				const double cascaded = Cascaded(x, direction);
				if (exact > 0.0 || cascaded > 0.0)
					std::printf("  probe x = %.1f, direction %d: brute force %.2f, cascades %.2f\n", x, direction, exact, cascaded);
			}
		}
	}
	return 0;
}
```

```text output-of="indirect-gi-cascades-toy.cpp"
without the wall
  probe x = 1.5, direction 2: brute force 1.52, cascades 1.88
  probe x = 1.5, direction 3: brute force 10.00, cascades 9.69
  probe x = 1.5, direction 4: brute force 1.05, cascades 1.09
  probe x = 2.5, direction 2: brute force 0.00, cascades 0.62
  probe x = 2.5, direction 3: brute force 9.53, cascades 9.06
  probe x = 2.5, direction 4: brute force 3.20, cascades 3.28
with the wall
  probe x = 1.5, direction 2: brute force 1.52, cascades 0.00
  probe x = 1.5, direction 3: brute force 6.91, cascades 9.22
  probe x = 1.5, direction 4: brute force 1.05, cascades 1.09
  probe x = 2.5, direction 3: brute force 9.53, cascades 8.91
  probe x = 2.5, direction 4: brute force 2.38, cascades 3.28
```

1. **Lines 8–9:** the lamp is a disc 12 m up and the wall stands at 2.2 m, absorbing.
2. **Lines 10–11:** the two cascades; the parent has twice the spacing and four times the directions.
3. **Lines 21–43:** `Trace` finds the first thing a ray meets between two distances.
4. **Line 63:** the merge itself, the own light plus the own transmittance times the parents' mean.
5. **Lines 67–73:** `BruteForce` is the exact answer to compare with.

Without the wall, the cascades stay within 0.62 nits of the exact answer in every direction, about 6 % of the lamp's 10 nits. With the wall, the first probe's direction 3 reads 9.22 nits where the truth is 6.91. The wall stands more than 2 m from the probe, so only the parents' rays see it, and they see it from other places. That is the penumbra condition failing: cascade 1's interval stretches to the lamp while its spacing is 2 m. Strata's cascades keep each interval short enough to avoid exactly this, and a third cascade would shorten the toy's.

The toy's merge line follows the **miss rule**: a ray that is not absorbed continues into the merged ray of its parents, never straight into the sky. Only the top cascade, whose interval has no end, reads the sky, and only for rays that leave the voxels.

The toy omits two rules that the real code needs. Both concern the border between one interval and the next.

- The **lead-in** is the occlusion-only stretch that a cascade above cascade 0 marches from the probe up to its interval's start. It stops light at voxels at least 0.3 full and gathers none. Without it, no marched side would cross a wall that lies between a ray's interval and the parents': a leak.
- The **overlap** is a march of one probe spacing past the end of the interval, and it does gather light. A parent's interval starts at the parent, which can stand more than a spacing to the side. A surface a little beyond the child's interval then lies inside the parent's lead-in, where nobody gathers its light. The overlap takes it on the child's own line.

A ray that hits something in its overlap ends there, so its parents' light is multiplied by 0. Nothing counts twice: the doubling that would otherwise appear at interval borders cannot happen.

## Injection: the light of every voxel

The march needs lamps, and the voxels are the lamps. **Occupancy** is how full a voxel is, from 0 (empty) to 1 (solid), and a sample of a march absorbs the share `saturate(occupancy * 2.5)`, so a wall two voxels thick is opaque. The function `saturate` clamps a number into the range 0 to 1. [Global illumination I: a voxel copy of the world](../indirect/gi-voxels.md) builds the voxels, and the injection pass lights them.

The pass `VoxelInject` runs on every voxel of every level, every frame, so that moving the sun lights the :term[clipmap]{id=clipmap} again in the frame it moves. For a surface voxel it computes the :term[albedo]{id=albedo} times the sun's :term[irradiance]{id=irradiance} on the voxel's normal, divided by $\pi$, plus the voxel's own emission. With bounces on, it adds the field of the frame before. The sun's part has a shadow, which comes from a walk through the voxels the ray crosses toward the sun. The shadow maps cannot help here: they cover only the view, and the light must reach surfaces behind the camera too.

The walk is where a sealed room is won or lost. It never skips a solid voxel, because a floor runs on under its walls. A walk that skipped the floor's own voxels at a wall's foot let the sun into a sealed room, and the test `The sun lights no voxel inside a sealed room` guards against it.

After injection, the level pass gives each coarser level the mean light of the eight finer voxels inside it, where those are valid and face the same way. Coarse voxels close small openings, so without the mean a window's patch of sun was a third of its true size in the coarse level.

## Probes: validity, relocation and weights

A probe grid does not care where walls are. Some probes land inside a wall or a box, and some land exactly on a surface.

**Validity** is a number from 0 to 1 for each probe: $1 - \text{saturate}(\text{occupancy} \times 2.5)$ at the probe's place. Validity is continuous, so a probe that a surface approaches fades out instead of switching.

A **dead probe** is a probe whose validity is 0: it lies inside a solid, so Strata does not trace its rays, and no merge or gather takes it.

A probe that sits on a surface is useless too, because half its rays start inside the surface. The validity pass moves it off along the surface's normal, by an amount that grows with the share of the probe that the surface covers. Cascade 0's probes move by up to half a spacing, and the others by up to 1.5 voxels of their cascade's finest level. Without the move, the probe planes that lie on a room's faces all die, and their children take one surviving parent's view from metres away.

**Relocation** goes further for cascade 0. A probe that stays more than half buried after the move searches its own cell for open space. It tries four rings of the 26 neighbouring directions, 0.1 spacings apart, and adds 0.05 to the occupancy of each ring for each step outward, so that the nearest open space wins.

The weights pass then prepares the merge. Each probe has eight parents in the next cascade. A parent's weight is its trilinear weight (0.25 or 0.75 per axis) times its validity times the transmittance of a soft march between the two probes, one voxel a step. A wall between a child and a parent therefore zeroes that parent. A parent outside the grid weighs 0, and every ray of a probe shares its probe's weights.

## The march and the merge in the shader

The march is the shared core of the cascade pass and the field reduce. The function `MarchRay` follows one ray front to back through the voxels and returns the light it gathers and its transmittance. **Transmittance** here is the share of the light that gets through the voxels so far. It starts at 1 and falls at each occupied sample, and the march steps 0.75 of a voxel at a time. At each sample it reads the finest level that holds the point, blended into the next level by that level's weight.

Look at the lead-in at line 31, the runs at lines 45 to 54 and the cutoff at line 61.

```slang src="Strata/shaders/Include/GIMarch.slang#L21-L75"
float4 MarchRay(float3 origin, float3 direction, float start, float end, bool top, uint minimumLevel, out bool left, out float3 hit)
{
	float transmittance = 1.0;
	hit = float3(0.0, 0.0, 0.0);
	float hitTransmittance = 1.0;
	float3 light = float3(0.0, 0.0, 0.0);
	bool inRun = false;
	left = false;
	float3 runRadiance = float3(0.0, 0.0, 0.0);
	float runWeight = 0.0;
	float t = max(0.0, start - u_Pass.Interval.w);
	[loop]
	for (uint step = 0u; step < ST_GI_MAX_MARCH_STEPS && (top || t < end); step++)
	{
		uint finest;
		float3 position = origin + direction * t;
		float occupancy = SampleOccupancy(position, minimumLevel, finest);
		if (finest == ST_GI_MAX_VOXEL_LEVELS)
		{
			left = true;
			break;
		}
		if (occupancy > 0.0 && (t >= start || occupancy >= ST_GI_LEAD_IN_OCCUPANCY))
		{
			if (!inRun || occupancy <= ST_GI_REFRESH_OCCUPANCY)
			{
				light += runWeight * runRadiance;
				runWeight = 0.0;
				runRadiance = SampleSurfaceRadiance(position, minimumLevel, direction);
			}
			inRun = true;
			float absorbed = saturate(occupancy * ST_GI_OCCUPANCY_GAIN);
			if (t >= start)
				runWeight += transmittance * absorbed;
			if (t > 0.0)
			{
				hit += hitTransmittance * absorbed * float3(t, t * t, 1.0);
				hitTransmittance *= 1.0 - absorbed;
			}
			transmittance *= 1.0 - absorbed;
			if (transmittance < ST_GI_TRANSMITTANCE_CUTOFF)
				break;
		}
		else
		{
			light += runWeight * runRadiance;
			runWeight = 0.0;
			inRun = false;
		}
		t += ST_GI_STEP_VOXELS * u_GI.Levels[finest].Origin.w;
	}
	light += runWeight * runRadiance;
	if (transmittance < ST_GI_TRANSMITTANCE_CUTOFF)
		transmittance = 0.0;
	return float4(light, transmittance);
```

1. **Line 31:** the march starts one lead-in's length before the interval, which is the probe for every cascade above cascade 0.
2. **Line 43:** a sample counts only inside the interval, or when it is at least 0.3 full: the lead-in stops solid voxels only.
3. **Lines 45–49:** a run of occupied samples takes its light at the first sample and refreshes it while samples stay under 0.1 full: the layer in front of the surface the ray entered.
4. **Lines 52–54:** each sample absorbs `saturate(occupancy * 2.5)`, and the run's weight grows by the transmittance times that share. Line 60 lowers the transmittance by the same share.
5. **Lines 61–62:** below a transmittance of 0.0001 the ray ends.

A run never reads deeper than the layer in front of its surface. A thin wall's far face, lit by the sun, therefore never lights its near face through the wall. Each run's light carries the weight of what the samples from it onwards absorb. A ray that grazes a floor ends where it meets the floor's patch of sun, not where it first touched the floor's thin layer.

The function `Merge` of the cascade pass is the code of the worked example above. Look at the three things it does with the weights: it skips parents of weight 0, adds a quarter of the parent's four texels, and divides by the sum of the weights it used.

```slang src="Strata/shaders/GI/CascadeMarch.comp.slang#L25-L46"
float4 Merge(uint3 probe, uint2 texel)
{
	float4 weightsA = u_WeightsA.Load(int4(int3(probe), 0));
	float4 weightsB = u_WeightsB.Load(int4(int3(probe), 0));
	int3 base = int3(floor((float3(probe) - 0.5) * 0.5));
	uint parentDirections = u_Pass.ParentGrid.w;
	float4 sum = float4(0.0, 0.0, 0.0, 0.0);
	float total = 0.0;
	[loop]
	for (uint corner = 0u; corner < 8u; corner++)
	{
		float weight = corner < 4u ? weightsA[corner] : weightsB[corner - 4u];
		if (weight <= 0.0)
			continue;
		int3 parent = base + int3(int(corner & 1u), int((corner >> 1) & 1u), int((corner >> 2) & 1u));
		int2 first = parent.xy * int(parentDirections) + int2(texel) * 2;
		float4 rays = u_ParentAtlas.Load(int4(first, parent.z, 0)) + u_ParentAtlas.Load(int4(first + int2(1, 0), parent.z, 0))
			+ u_ParentAtlas.Load(int4(first + int2(0, 1), parent.z, 0)) + u_ParentAtlas.Load(int4(first + int2(1, 1), parent.z, 0));
		sum += weight * 0.25 * rays;
		total += weight;
	}
	return total < 1e-4 ? float4(0.0, 0.0, 0.0, 0.0) : sum / total;
```

1. **Lines 36–38:** a parent of weight 0 takes no part.
2. **Lines 41–43:** the four parent directions inside this texel, weighted and averaged.
3. **Line 46:** divide by the weights used; with none, the light is dark.

The last lines of the pass combine the ray's own light with the merge. Only the top cascade reads the sky.

```slang src="Strata/shaders/GI/CascadeMarch.comp.slang#L94-L99"
float4 rest = float4(0.0, 0.0, 0.0, 0.0);
if (top)
	rest = own.a > 0.0 ? float4(GetSkyRadiance(GetTileDirection(texel, a)), 1.0) * (leftShare / own.a) : float4(0.0, 0.0, 0.0, 0.0);
else if (own.a > 0.0)
	rest = Merge(probe, texel);
o_Atlas[globalID] = float4(own.rgb + own.a * rest.rgb, own.a * rest.a);
```

The first branch is the top cascade: the rays that left every level read the sky, in proportion to the share of the ray that left. The second branch is the merge. The last line is the formula $R_k = L + T \cdot R_{k+1}$ with $T$ in the alpha channel.

## The field reduce and the ambient cube

Cascade 0 is not stored as rays. The pass `FieldReduce` runs a group of 64 threads for each cascade-0 probe, one thread for each of the 64 directions of cascade 1's tile. Each thread marches its ray over cascade 0's interval and continues it into cascade 1's merged ray of the same direction. It multiplies the result by the solid angle of its texel and by the :term[cosine]{id=cosine} to each of six axes.

The sums make an **ambient cube**: six values per probe, one for each of the directions +X, -X, +Y, -Y, +Z and -Z. Each face holds the irradiance over $\pi$ for a surface facing that axis, which is the radiance that a white surface turned that way would show. A read for a normal $n$ blends the three faces that its signs pick, by the squares of its components $n_x^2$, $n_y^2$ and $n_z^2$. The weights always add up to 1, because $n$ has length 1, so a uniform sky gives every normal exactly the sky's radiance.

The same threads keep two other things. The first is each probe's depth moments: the mean and the variance of the distance to the first hit along each ray, filtered over neighbouring rays and stored in a 10 by 10 octahedral tile.

The second thing is the projection of the 64 rays on nine :term[spherical harmonics]{id=spherical-harmonics}, a smooth function of the normal. Drawn surfaces read the harmonics but never take less than the cube. Between 104 and 145 degrees away from the normal the harmonics' weight turns negative, so a probe that sees a strong light behind a wall's plane would read black there. The cube has no negative weight and acts as the floor.

## Multi-bounce by re-injection

One bounce is light that leaves the sun, hits a surface once and arrives at another. Later bounces arrive through a loop. Injection reads the field that the frame before left, at the voxel half a voxel off the surface along its normal, and adds the albedo times that field to the voxel's light. The cascades then carry it onward. Bounce number two arrives in the frame after bounce number one, and so on: each frame adds one more term of a series.

Look at the guard on line 163 and at the clamp on line 168.

```slang src="Strata/shaders/GI/VoxelInject.comp.slang#L163-L169"
if (u_GI.Bounce.x > 0.0 && any(n != float3(0.0, 0.0, 0.0)))
{
	// The field holds irradiance over pi times ST_GI_RADIANCE_SCALE: a Lambertian surface's radiance per albedo.
	float openShare;
	float4 field = SampleIrradianceField(u_GIRepeat, center + n * (0.5 * voxel) + u_GI.Bounce.yzw, n, n, n, false, openShare);
	float3 bounceAlbedo = min(albedo, float3(ST_GI_MAX_BOUNCE_ALBEDO, ST_GI_MAX_BOUNCE_ALBEDO, ST_GI_MAX_BOUNCE_ALBEDO));
	scaled += SanitizeHDR(bounceAlbedo * field.rgb * (field.a * u_GI.Bounce.x));
```

1. **Line 163:** the gain is 0 on a cut, on a pending frame, on the first frame and after a frame that recorded no field, so those start again from one bounce.
2. **Line 167:** the field of the frame before, read half a voxel off the surface with the gather's visibility.
3. **Lines 168–169:** the albedo is clamped to 0.9 and multiplies the field and the gain.

The clamp keeps the ratio of the series below 1, and the gain `BounceGain` (1 by default, always within 0 and 1) scales the whole return. The tests set it to 0 to get one bounce.

```mermaid caption="The field of each frame feeds the voxels of the next. After frame k the light holds the first k terms of the series of bounces." alt="Boxes for frames one, two, three and k in a row. Each frame lights the voxels with the sun and the albedo times the field of the frame before, and an arrow leads from each frame to the next."
flowchart LR
    A["Frame 1: sun only. Field 1 holds bounce 1"] --> B["Frame 2: sun + albedo x field 1. Field 2 holds bounces 1 and 2"]
    B --> C["Frame 3: sun + albedo x field 2. Field 3 holds bounces 1 to 3"]
    C --> D["Frame k: field k holds the first k terms"]
```

Re-injection is not temporal accumulation. A temporal filter, such as [temporal anti-aliasing](../image/taa.md), blends pixels of the last picture into this one, so the image depends on the camera's path. Re-injection reads world data, which is the voxels and the field at fixed places, and the camera enters only through where the field sits. A still scene gives the same bits at every frame once the series has settled, and a test checks that frame 30 equals frame 31.

:::example[Frames to settle]
In a closed room whose bounces keep the ratio $r$, the light after $k$ frames is the first $k$ terms of a :term[geometric series]{id=geometric-series}. The series adds up to $L_1/(1-r)$ in the end, where $L_1$ is the first bounce. After frame $k$ the next frame adds $L_1 r^k$, which is the share $r^k (1-r)$ of that limit. Strata calls the series settled at the first $k$ where the share falls below 0.25 %, and adds two frames of margin.

$$r^{k}(1-r) < 0.0025$$

Here $r$ is the ratio, the brightest albedo of the scene times the gain, and $k$ is the number of frames. For $r = 0.58$: at $k = 9$ the share is $0.58^9 \times 0.42 = 0.0031$, too much, and at $k = 10$ it is $0.0018$. So $k = 10$ and the room settles after 12 frames. For $r = 0.73$ the share is 0.0033 at $k = 14$ and 0.0024 at $k = 15$, so the room settles after 17. At the clamp $r = 0.9$ the first $k$ is 36, and the room settles after 38.
:::

The function `GetSettleFrames` does the same with :term[logarithms]{id=logarithm}. Look at the division inside `std::log` and at the margin it adds.

```cpp src="Strata/src/Strata/Renderer/GlobalIlluminationLayout.cpp#L415-L419"
if (!std::isfinite(ratio) || ratio <= 0.0f)
	return 0;
const double kept = std::min(static_cast<double>(ratio), static_cast<double>(RenderData::c_GIMaxBounceAlbedo));
const double frames = std::ceil(std::log(static_cast<double>(RenderData::c_GISettleChange) / (1.0 - kept)) / std::log(kept));
return static_cast<uint32_t>(std::max(frames, 1.0)) + RenderData::c_GISettleMarginFrames;
```

Only High bounces on. Low's layout bounces once, because its coarser field with every bounce makes the Cornell box's ceiling about 1.8 times as bright as High's (165 to 235 nits for the albedos tested, against 89 to 142). The test `High bounces on, Low once` keeps it so.

```mermaid caption="Share of the final light after each frame for one bounce and for every bounce, with a ratio near six tenths. One bounce stays where the first frame put it. Every bounce climbs toward the limit." alt="Two rows of four boxes. The first row, one bounce, shows the same value in every frame. The second row, every bounce, shows values that rise from frame one to frame four and approach the limit."
flowchart LR
    subgraph one["Gain 0: one bounce"]
        O1["Frame 1: 0.42"] --> O2["Frame 2: 0.42"] --> O3["Frame 3: 0.42"] --> O4["Frame 4: 0.42"]
    end
    subgraph every["Gain 1: every bounce"]
        E1["Frame 1: 0.42"] --> E2["Frame 2: 0.66"] --> E3["Frame 3: 0.80"] --> E4["Frame 4: 0.89"]
    end
```

## The forward gather

The forward pass reads the field once per pixel. It wants the irradiance at a point $P$ on a surface with a normal $N$, and it asks the eight cascade-0 probes around $P$. The natural weights are trilinear: a probe's weight is the product of its closeness on each axis. Two more factors keep out the probes that cannot see $P$, and two small moves keep the question itself honest.

The **normal bias** moves the point where the grid is read 0.25 spacings along the surface's normal. A point on a floor then reads the probes above the floor and not those below it.

The **view bias** moves the point where visibility is tested a further 0.3 spacings toward the viewer, and out of any solid it then lies in. Without it, a point within a voxel of a perpendicular wall lies inside that wall's voxels, where every probe is hidden, and a black line runs along every inner corner.

The **voxel guard** is Strata's test of whether a probe can see the point: the transmittance through the voxels of levels 0 to 2 along the segment from the probe to the point. It takes 16 samples at fixed fractions of the segment. Each counts only the solid core of a voxel, occupancy 0.6 to 0.72, so the soft layer around a surface never hides a probe, and a wall one voxel thick always meets some sample. The guard has a shortcut: if every ray of the probe near that direction travels farther than the point before it hits anything, nothing can hide the point, and the guard does not run. The shortcut saves a third of the gather's cost.

Look at the weight in line 227, the guard in lines 232 and 233, and the two sums in lines 236 and 237.

```slang src="Strata/shaders/Include/GIField.slang#L214-L237"
for (uint corner = 0u; corner < 8u; corner++)
{
	int3 offset = int3(int(corner & 1u), int((corner >> 1) & 1u), int((corner >> 2) & 1u));
	int3 probe = base + offset;
	if (any(probe < int3(0, 0, 0)) || any(probe >= grid))
		continue;
	float4 validity4 = u_GIFieldValidity.Load(int4(probe, 0));
	float validity = validity4.r;
	// Where the probe's light and distances were measured: moved off a surface it sat on (ProbeValidity.comp).
	float3 probePosition = u_GIField.FieldOrigin.xyz + (float3(probe) + 0.5) * spacing + DecodeProbeMove(validity4, spacing);
	float3 toProbe = probePosition - position;
	float facing = smoothstep(-0.05, 0.25, dot(toProbe * rsqrt(max(dot(toProbe, toProbe), 1e-8)), geometricNormal));
	float3 trilinear3 = select(offset != int3(0, 0, 0), fraction, 1.0 - fraction);
	float weight = trilinear3.x * trilinear3.y * trilinear3.z * facing * validity;
	reachable += weight;
	if (weight <= 0.0)
		continue;
	// The guard marches only where the probe's rays around the point hit something before it.
	if (!LiesBeforeProbeHits(probe, probePosition, seen))
		weight *= GetFieldTransmittance(repeat, probePosition, seen);
	if (weight <= 0.0)
		continue;
	sum += weight * ReadProbeIrradiance(probe, shadingNormal);
	total += weight;
```

1. **Lines 216–219:** the eight corners of the cell around the biased point; probes outside the grid are skipped.
2. **Lines 223–225:** the probe is read where relocation put it, and `facing` fades probes behind the surface's plane.
3. **Lines 227–228:** the weight is trilinear times facing times validity; `reachable` keeps what the probes would weigh before the guard.
4. **Lines 232–233:** the guard multiplies in the transmittance, unless open space makes it unnecessary.
5. **Lines 236–237:** the visible light and the visible weight.

After the loop, `SampleIrradianceField` divides the sum by the total. It never divides by less than a quarter of `reachable`. The reason is the error taught next.

:::example[A weight that vanishes]
A point's eight probes would weigh 0.4 in all before the guard, and a wall hides all but one, which weighs 0.02. Dividing by the visible total, 0.02, gives that one probe's light in full, a hundred percent of it. A step later its weight reaches 0, the total is 0, and the light falls to black: the image shows a step at the cell border. With the floor, the division is by $\max(0.02,\ 0.25 \times 0.4) = 0.1$. The light is then 20 % of that probe's, and it falls steadily to 0 as the weight does.
:::

The first design weighed probes by the Chebyshev bound on their depth moments, the test of the Dynamic Diffuse Global Illumination paper. The moments say how likely a point is to lie before the nearest surface, and that likelihood is the weight. Strata used it and dropped it, for reasons that the section on what went wrong before gives. A cubed tail of the bound turned small turns of the view into whole steps of a thin post's weights, so fences crawled. The depth moments stay only to skip the guard.

The gather ends with three smaller pieces. A point that no probe sees takes no field light, and never the sky. A point inside a narrow gap, under about one and a half voxels wide, takes the light of the gap's opening toward the camera. The finest voxels fill such a gap and hide its probes. And at High the field's weight is full up to 7.5 m from the camera across and 5.5 m up or down, and falls to 0 over the next 2 m.

The function also returns the **open share**, the cosine-weighted share of the sky that the surface sees, which the `open` view shows.

:::why[Why the guard reads voxels and not the probe's own rays]
A probe's 64 rays are coarse: each covers 0.44 radians, and a thin wall seen at a grazing angle can slip between two rays. The voxels are the geometry itself, 10 cm wide at High, so a wall one voxel thick always meets a sample. The price is 16 voxel reads for each probe of each pixel, which is why the depth moments skip the guard in open space.
:::

## The join: the field meets the surface

The **join** replaces the diffuse part of the indirect light with the field's, inside the field's reach. The CPU sets two numbers in `RenderFrame`, the `y` and `z` components of `ReflectionParams`. It sets them only when the scene's Post Process asks for global illumination, the quality row is not Off and the field is used (it ran and is not pending). Then `y` is 1 and `z` is `GlobalIlluminationIntensity`, clamped to 0 to 4. Otherwise both stay 0, and the shader runs the old expression.

Look at how the weight $w$ splits the diffuse light between today's light and the field, and at the specular light, which the field never touches.

```slang src="Strata/shaders/Scene/Forward.frag.slang#L432-L442"
indirectInputs.FieldWeight = field.a;
indirectInputs.FieldIrradiance = field.rgb * (u_Frame.ReflectionParams.z / ST_GI_RADIANCE_SCALE);
indirectInputs.FieldOpen = openShare;
if (lightingView == ST_LIGHTING_VIEW_SPECULAR)
	indirect = ComposeIndirect(indirectInputs, float3(0.0), GatherIndirectSpecular(indirectInputs));
else if (lightingView == ST_LIGHTING_VIEW_DIFFUSE)
	indirect = ComposeIndirect(indirectInputs, GatherIndirectDiffuse(indirectInputs, surface) * (1.0 - indirectInputs.FieldWeight), float3(0.0))
		+ GatherIndirectField(indirectInputs, surface) * indirectInputs.FieldWeight;
else
	indirect = ComposeIndirect(indirectInputs, GatherIndirectDiffuse(indirectInputs, surface) * (1.0 - indirectInputs.FieldWeight),
		GatherIndirectSpecular(indirectInputs)) + GatherIndirectField(indirectInputs, surface) * indirectInputs.FieldWeight;
```

1. **Line 432:** the field's weight comes with the sample: 0 outside the field and while pending.
2. **Line 433:** the intensity scales the irradiance; the divisor undoes the scale that keeps stored light inside half floats.
3. **Lines 438–439:** the diffuse view takes today's diffuse light times $1 - w$ plus the field's times $w$.
4. **Lines 441–442:** the full image does the same and adds today's specular light, untouched.

Where $w$ is 0 the code multiplies by 1 and adds 0, so the light is the old light exactly. The function `GatherIndirectField` puts the field's irradiance on the surface's albedo and takes out what the specular gather takes. It scatters the result by the material's diffuse weight and applies the diffuse occlusion without the multi-bounce fit, because the field's bounce is the real one and the fit would count it twice.

The intensity is the setting a game maker changes. At 0, the field still replaces today's diffuse light inside its reach, scaled to nothing, so the indirect diffuse light is dark and not the old light.

::compare{id=intensity-sweep}

## Debug views and statistics

Four debug views show the pieces. The **GI** view draws every surface white and shows only the diffuse indirect light. The **Open** view shows the share of the sky that each surface sees. The **Voxels** view shows the voxel copy of the scene, and the **Probes** view floats the cascade-0 probes in the image. A live probe shows the color of its ambient cube, and a dead probe is dark red.

The pair below shows the first two views, of a sun room.

::compare{id=gi-views}

A debug view of global illumination runs the whole feature, even where the scene does not ask for it or the quality row is Off. At Off it shows High's layout. This is the one exception to the rule that nothing is made when the feature is off.

The statistics of [the page on measuring light](../light/measuring-light.md) carry the numbers in the same way. Each frame reports `GlobalIllumination`, `GlobalIlluminationPending` and `GlobalIlluminationSettled`, with counts of triangles turned into voxels, regions queued and proxies that wait or move. The GPU adds `GIDeadProbes`, `GILiveProbes` and `GISurfaceVoxels`. A capture of one of the four views reports them as `debugView.globalIllumination`. The functions `ReadGlobalIlluminationField` and its siblings block until the GPU is done, so they serve tests and tools and never a frame, as [the page on readback timing](../gpu/readback-timing.md) teaches.

## A sealed room stays dark

The guarantee that all these rules buy is simple to state: a room with no opening stays dark, whether the light's source is on screen or not. The sun lights no voxel inside it, and of two rooms that share a wall, the sealed one stays dark. The suite `GPU.SceneRenderer.GlobalIlluminationRoom` tests it three ways: `The sun lights no voxel inside a sealed room`, `Paired rooms: the sealed one stays dark` and `A sealed room stays dark`. The two room tests check light at a room's points against a bound of 0.17 % of an open room's mean.

::compare{id=sealed-open}

Each rule of the page closes one way for light to get through a wall.

- The sun's walk never skips a solid voxel, and a :term[closed mesh]{id=closed-mesh} fills its inside. No voxel in the room gets sun, and the probes inside walls die.
- A thin wall's two faces make a :term[two-sided voxel]{id=two-sided-voxel}, which sends nothing. One side's light never enters the other.
- A parent beyond the wall gets weight 0 from the weights pass, so a child inside the room never merges its light.
- The lead-in carries the wall to rays that start past the interval, and the overlap takes the surface beyond it, so a marched side always crosses the wall and nothing counts twice.
- The voxel guard hides every probe outside the wall from a point inside, and the floor on the weight stops the one that remains from lighting the point.

The case is the best way to learn why the rules exist: take one away and a test of this suite fails. The sky enters only through the top cascade's rays that leave the voxels, so a ceiling cannot pass it on, and the test `No sky through misses` checks that.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Chebyshev weighting of probes by depth moments | Engines that follow the Dynamic Diffuse Global Illumination paper | One cheap lookup in place of 16 voxel reads | Visibility from a coarse 64-ray tile: contacts go black and thin posts make fences crawl |
| A field of irradiance tiles, one octahedral tile for each probe | The same paper | A smooth function of the normal without harmonics | Memory for a tile of every probe, and a negative-lobe problem that the cube floor already solves |
| Voxel cone tracing | Engines that follow the voxel cone tracing paper | No probes: each pixel traces cones through the voxels | A cost for each pixel, and blur from wide cones |
| Screen-space global illumination | Many real-time engines | A cheap pass with no voxels | Light that depends on the screen: a lamp that leaves the view stops lighting. The project refuses it |
| Blending the field over frames | Most probe systems | Less noise from fewer rays | A smear behind a moving camera, and bits that depend on the camera's path |

Drawn surfaces read the harmonics but never less than the ambient cube. The octahedral tile survives only in the depth moments.

## How it is tested

The suites are GPU tests, so they need a graphics card. Run them with `ctest --preset windows-debug -R GlobalIllumination` or the matching preset. The layout tests need no GPU.

- `GPU.SceneRenderer.GlobalIlluminationRoom` builds a sun room and checks the tint of a red floor, the sealed rooms, the dead probes, the continuity of probe moves and the repeat of still frames.
- `GPU.SceneRenderer.GlobalIlluminationJoin` checks the join: the white furnace, a pending frame, the intensity (the test `Intensity scales the field` measures walls at 1, 2 and 0) and the field's meeting with today's light at its edge.
- `GPU.SceneRenderer.GlobalIlluminationBounce` checks the series: the Cornell box, a glowing closed box that converges to the series, settling after a cut and still frames with bounces.
- `GPU.SceneRenderer.GlobalIlluminationStitching` checks that the light has no steps at probe borders and that the depth moments hold a probe's distances.
- The layout tests in `GlobalIlluminationLayoutTests.cpp` check, without a GPU, the ray counts, `GetSettleFrames` and the rule that High bounces on and Low bounces once.

## Changing it safely

The extension points are few. A new input to what the voxels send goes into the injection pass and into the settle inputs, so that `GlobalIlluminationSettled` waits for it. A new use of the field goes through `SampleIrradianceField`, which owns the guard and the floor.

- Keep every pass a function of world data and the camera's place. A pass that reads an old image makes the light depend on the camera's path, and the bit-for-bit tests fail.
- Keep what follows the march `precise` in the reduce. On one driver, sums in two orders differed by a unit between dispatches, and a camera's field is compared with a fresh renderer's to the :term[byte]{id=byte}.
- Before you add a frame constant, check the `ao` view's repeats, as the contract says.
- A new forward shader variant needs its twin that holds the field, and a plain variant must bind none of the field's slots.
- Run the global illumination suites and `GPU.SceneRenderer.Lighting` before you merge. They cost minutes on a GPU, and a change that skips them has no measurement.

## What went wrong before

The first gather weighed probes by the Chebyshev bound on their depth moments, and two defects showed. In the Cornell box, the floor under the sphere and beside the tall box went black. Each probe's 64 directions were blurred by about 25 degrees, so a contact's surfaces seemed to stand in front of points that the probes in fact saw plainly.

The second defect was the fence crawl. A thin post's probe weights turned in whole steps as the view turned. At a still camera, 0.247 % of the picture's blocks changed from one capture to the next, against a gate of 0.10 %. The voxel guard replaced the weights, and the same measure fell to 0.0230 %. The test `The Cornell box's floor darkens smoothly toward the sphere's and the box's feet` and its neighbours in the stitching suite now guard the floor.

## Summary

- Probes need few directions and many places near them and the reverse far away, so Strata stacks cascades whose spacing doubles while their directions and intervals grow four times.
- A ray's light is its own interval's light plus its transmittance times the merged ray of its parents, and only the top cascade reads the sky.
- The forward gather weighs eight probes by trilinear weight, validity, facing and the voxel guard, and never divides by less than a quarter of the weight it could have had.
- Re-injection adds one bounce a frame, a series that settles after $k + 2$ frames, where $k$ is the first with $r^k(1-r)$ below 0.25 %, with no temporal blending.
- A frame runs the six passes, the forward pass reads the field once per pixel, and the join mixes it with today's diffuse light by the field's weight and the intensity.

## Check yourself

1. A probe stands 0.5 m from a window 1 m wide, and another stands 16 m from a window of the same size. Which probe needs more rays to see the window's shape, and which needs its neighbours closer? (a) The near probe needs more rays, the far one closer neighbours. (b) The far probe needs more rays, the near one closer neighbours. (c) Both need the same.

   :::answer{tests="explain-cascades"}
   Option (b) is right: from 0.5 m the window covers 90 degrees, so a coarse tile sees it. A neighbour 0.5 m away sees it in a direction that differs by about a radian, so neighbours must be close. From 16 m the window covers 3.6 degrees, which needs many rays. Neighbours a few metres apart see it in nearly the same direction. Options (a) and (c) reverse or ignore the penumbra condition.
   :::

2. A child ray has $L = 2$ nits and $T = 0.5$. Its parents have weights 0.6 and 0.2 and mean directions of 10 and 20 nits. What is the merged radiance?

   :::answer{tests="compute-merge"}
   The parents' merged value is $(0.6 \times 10 + 0.2 \times 20)/(0.6 + 0.2) = 10/0.8 = 12.5$ nits, and $R = 2 + 0.5 \times 12.5 = 8.25$ nits. A common slip is to skip the division, which gives $2 + 0.5 \times 10 = 7$ nits, a light that falls whenever a parent is blocked.
   :::

3. A wall hides six of a point's eight probes from it. Before the guard the eight weighed 0.4 in all, and the two that remain weigh 0.05 together. What does the gather divide the sum by, and why not by 0.05?

   :::answer{tests="explain-guard"}
   By $\max(0.05,\ 0.25 \times 0.4) = 0.1$. Dividing by 0.05 would give the two probes the whole light, and as their weight fell to 0 at a cell border the light would jump from full to black. With the floor the light is half of the two probes' and fades steadily.
   :::

4. A scene's brightest albedo is 0.65 and the gain is 1. How many frames does the series take to settle?

   :::answer{tests="compute-settle"}
   $0.65^{11} \times 0.35 = 0.0031$ and $0.65^{12} \times 0.35 = 0.0020$, so $k = 12$, and the margin of two frames gives 14.
   :::

5. A scene has Global Illumination on at High, settled, with `GlobalIlluminationIntensity` 0. What diffuse indirect light does a wall inside the field show? What does a pending frame show?

   :::answer{tests="trace-frame"}
   None from the field: the join gives today's light times $1 - w$ plus the field times $w$, with the field scaled by 0, so the indirect diffuse light is dark. The test `Intensity scales the field` measures exactly 0 at the walls. A pending frame never sets the `y` component of `ReflectionParams`, so it shows today's light, bit for bit.
   :::

## Exercises

1. **Basic.** Derive the settle frames for the albedos 0.58 and 0.73 and say which test holds the numbers.

   :::answer[Worked solution]{tests="compute-settle" solution="sketches/indirect-gi-cascades-settle.cpp"}
   The program below searches for the first $k$ where the next term falls under 0.25 % and adds the margin.

   ```cpp sketch="indirect-gi-cascades-settle.cpp"
   #include <cmath>
   #include <cstdio>
   #include <initializer_list>

   // The frames a re-injected bounce series needs to settle. In a closed room the light after k frames is the first k terms of a
   // geometric series with ratio r, so the next frame adds r^k (1 - r) of the limit.
   constexpr double c_SettleChange = 0.0025; // Settled when the next bounce adds less than this share
   constexpr int c_MarginFrames = 2;

   int SettleFrames(double ratio)
   {
   	int k = 1;
   	while (std::pow(ratio, k) * (1.0 - ratio) >= c_SettleChange)
   		k++;
   	return k + c_MarginFrames;
   }

   int main()
   {
   	for (const double albedo : { 0.58, 0.73, 0.9 })
   	{
   		const int frames = SettleFrames(albedo);
   		const double left = std::pow(albedo, frames - c_MarginFrames);
   		std::printf("albedo %.2f: %d frames, %.1f %% of the limit still to come after frame %d\n", albedo, frames, 100.0 * left,
   			frames - c_MarginFrames);
   	}
   	return 0;
   }
   ```

   ```text output-of="indirect-gi-cascades-settle.cpp"
   albedo 0.58: 12 frames, 0.4 % of the limit still to come after frame 10
   albedo 0.73: 17 frames, 0.9 % of the limit still to come after frame 15
   albedo 0.90: 38 frames, 2.3 % of the limit still to come after frame 36
   ```

   1. **Lines 10–16:** `SettleFrames` loops until $r^k(1-r)$ falls below 0.25 %, then adds the margin.
   2. **Line 23:** the share of the limit still to come after the last frame that counted.

   The answers are 12 and 17, and 38 at the clamp. The test `Bounces settle by the scene's brightest albedo` in `GlobalIlluminationLayoutTests.cpp` checks 12 for 148/255 and 17 for 186/255.
   :::

2. **Medium.** Count the rays that Low fires in a frame. Low has three cascades with grids of 24 by 20 by 24, 12 by 10 by 12 and 6 by 5 by 6 probes. Their tiles are 8, 8 and 16 directions a side, and only cascade 1 has two sub-rays a side. Compare with High's 10,506,240.

   :::answer[Worked solution]{tests="explain-cascades"}
   Cascade 0 has $11{,}520 \times 64 = 737{,}280$ rays. Cascade 1 has $1{,}440 \times 64 \times 4 = 368{,}640$. The top cascade has $180 \times 256 = 46{,}080$. They sum to 1,152,000, which a layout test checks. High fires about 9.1 times as many.
   :::

3. **Hard.** Trace it yourself. Follow `GlobalIlluminationIntensity` from the Post Process to the pixel: where is it clamped, which conditions set the weights, and where does the shader use it? What does a pending frame draw?

   :::answer[Worked solution]{tests="trace-frame"}
   Search for `GlobalIlluminationIntensity` in `Strata/src/Strata/Renderer/`. The component holds it in `RendererComponents.h`, with the range 0 to 4.

   In `SceneRenderer::RenderFrame` in `SceneRenderer.cpp`, `GetPostProcessSettings` reads it. After `SettleGlobalIllumination`, the code sets the `y` component of `ReflectionParams` to 1 and the `z` component to the clamped intensity, only where the scene asked, the row is not Off and the field is used. In `Scene/Forward.frag.slang`, `ShadeLitSurface` scales `field.rgb` by that `z`, `GatherIndirectField` in `IndirectLight.slang` puts that irradiance on the surface, and `ShadeLitSurface` weighs the result by the field's weight. A pending frame leaves `y` at 0, so the shader takes the old expression and draws today's light.
   :::

## Where it lives in Strata

- `Strata/shaders/GI/`: the passes `VoxelInject`, `VoxelDownsample`, `ProbeValidity`, `ProbeWeights`, `CascadeMarch` and `FieldReduce`, and the two views.
- `Strata/shaders/Include/GIMarch.slang`, `Strata/shaders/Include/GIField.slang`, `Strata/shaders/Include/GIProbes.slang` and `Strata/shaders/Include/GlobalIllumination.slang`: the march, the gather, the shared reads and the constants.
- `Strata/src/Strata/Renderer/GlobalIlluminationLayout.cpp` and `Strata/src/Strata/Renderer/GlobalIlluminationLayout.h`: the layout, `ComputeLayout` and `GetSettleFrames`.
- `Strata/src/Strata/Renderer/SceneRendererGlobalIllumination.cpp`: the CPU side of the passes, the b3 buffer and `SettleGlobalIllumination`.
- `Strata/shaders/Scene/Forward.frag.slang` and `Strata/shaders/Include/IndirectLight.slang`: the join.
- `StrataTests/src/Renderer/GPUSceneGlobalIlluminationRoomTests.cpp`, `StrataTests/src/Renderer/GPUSceneGlobalIlluminationTests.cpp` and `StrataTests/src/Renderer/GlobalIlluminationLayoutTests.cpp`: the suites.
- The Post Process properties `GlobalIllumination` and `GlobalIlluminationIntensity`, and the quality row `Renderer.Quality.GlobalIllumination`.

## Further reading

- Alexander Sannikov, "Radiance Cascades" (paper, 2023; advanced): the penumbra condition, the cascades and the merge.
- Zander Majercik and others, "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields" (paper, 2019; advanced): the probe field and the Chebyshev weights Strata dropped.
- Cyril Crassin and others, "Interactive Indirect Illumination Using Voxel Cone Tracing" (paper, 2011; advanced): the alternative in the table.
- Jason Mitchell, Gary McTaggart and Chris Green, "Shading in Valve's Source Engine" (course notes, 2006; intermediate): the ambient cube.
