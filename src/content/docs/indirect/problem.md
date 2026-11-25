---
id: indirect/problem
title: "The indirect-light problem"
description: "Why a lamp lights more than what it shines on: the rendering equation, path tracing as ground truth, the families of cheap answers and Strata's choice."
kind: concept
size: M
tracks: [E]
needs: [light/brdf, light/sky]
time: 55
learn:
  - id: three-parts
    text: name the three parts of the light that leaves a surface and the technique that approximates each in Strata
  - id: bounce-count
    text: compute how much of a closed room's light the first bounces carry from the walls' albedo
  - id: noise
    text: predict how the error of path tracing falls as its sample count grows
  - id: choose-family
    text: choose a family of indirect-light techniques for a game and name what the choice costs
  - id: world-data
    text: explain why Strata's global illumination traces world data and never the screen
since: 0.3.0
status: final
---

Two pictures show one kind of room, the Cornell box: a white room with a red wall on the left, a green wall on the right and a bright panel under the ceiling. The first comes from Strata's look-dev project with global illumination off. There the panel glows, but nothing receives its light, only a dim constant color that the next section explains. The second comes from the path-tracing program of this page, which computes the light by the slow exact method.

::figure{id=cornell-gi-off}

::figure{id=cornell-reference}

In the second picture the floor near the red wall is faintly red, the floor near the green wall faintly green, and the ceiling is lit although the panel shines only downward. The ceiling gets its light from the floor and the walls, which got theirs from the panel. The program's room is simpler than Strata's: it has no tall box and no sphere.

## A constant color cannot be the answer

The cheapest answer adds one color to every surface, whatever its place. Strata keeps such a color: the `AmbientColor` of the `SkyLightComponent`, a dim blue-gray of 0.03, 0.03 and 0.04 :term[nits]{id=lux}, which lights a surface only when the scene has no environment. It is the last fallback, because it fails three ways at once.

A constant has no occlusion. A crease between a wall and the floor gets the same light as the middle of the floor, although the crease sees less of the room. A constant has no color from the neighborhood: a white floor next to a red wall should turn a little red. It also has no place, so the same value lights a cave and a beach.

Real shadows are not black, and a constant seems to repair that, but it only lifts the dark parts and flattens the picture. Light in a shadow comes from somewhere: from the sky and from the lit surfaces nearby.

## The idea: light that bounced

A surface sends light to the eye. The reflection equation of [How surfaces reflect light](../light/reflectance.md) says how much: the light arriving from each direction, weighted by the surface and by the angle, summed over the hemisphere above the surface. That page took the arriving light as given. Here it is the question, because most of it left another surface a moment earlier. Writing this down gives the rendering equation, which Kajiya published in 1986:

$$L_o = L_e + \int_{\Omega} f \, L_i \cos\theta_i \, d\omega_i$$

The integral sign reads "sum over every direction of the hemisphere". $L_o$ is the :term[radiance]{id=radiance} leaving the point toward the eye, and $L_e$ is the radiance the point emits itself: zero for most surfaces, large for the glowing panel. $\Omega$ is the hemisphere of directions above the surface, $\omega_i$ is one direction in it, and in $d\omega_i$ the $d$ marks a small step of direction. $f$ is the :term[reflectance]{id=reflectance} for that direction and the eye's direction, the bidirectional reflectance distribution function (:term[BRDF]{id=brdf}), the part of the :term[shader]{id=shader} that [The forward shader](../light/brdf.md) takes apart. $L_i$ is the radiance that arrives along $\omega_i$, and $\theta_i$ is the angle between that direction and the surface's normal.

Everything hides in $L_i$. The light that arrives along a direction is the light that leaves the first surface in that direction, which is $L_o$ of another point, so the equation contains itself. Light that comes from a lamp in one step is direct light. Every longer path, such as lamp to wall to floor to eye, is **indirect light**: light that reached the surface after at least one bounce. The sky belongs here as a distant light source, because the air scattered its light before it reached the scene ([The sky as a light](../light/sky.md)).

A real-time engine cannot solve an equation that contains itself for every pixel in 16.7 ms. It splits the light into parts and gives each part a cheap proxy, a stand-in that is right enough. Lamps are direct light, and the engine handles them one by one with formulas. The rest splits by the lobe that reflects it: diffuse light that scatters in all directions, and specular light that reflects like a mirror, blurred by roughness.

```mermaid caption="The light that leaves a surface splits into three parts. Each part has its own cheap approximation in the engine." alt="A box for the light leaving a surface points to three boxes. The first is direct light, from lamps and shadow maps. The second is indirect diffuse light, from the sky, probes, the bounce field and occlusion. The third is indirect specular light, from the sky, probes and screen-space reflections."
flowchart LR
    eq["Light leaving a surface"] --> direct["Direct light: lamps and shadow maps"]
    eq --> diffuse["Indirect diffuse: sky, probes, GI field, occlusion"]
    eq --> specular["Indirect specular: sky, probes, screen-space reflections"]
```

The table says who handles each part in Strata and where this part of the book teaches it.

| Part | What approximates it in Strata | Page |
| --- | --- | --- |
| Direct light | Lights and their shadow maps | [Lights](../light/lights.md) |
| Indirect diffuse, from the sky | The sky's :term[irradiance]{id=irradiance} | [Image-based lighting](../indirect/ibl.md) |
| Indirect diffuse, from a room | Reflection probes | [Probes](../indirect/probes.md) |
| Indirect diffuse, from bounces | The global illumination field | [Global illumination on voxels](../indirect/gi-voxels.md) |
| Darkening of creases | Ambient occlusion | [Ambient occlusion](../indirect/ao.md) |
| Indirect specular | The sky, probe captures, screen-space reflections | [Screen-space reflections](../indirect/ssr.md) |

**Global illumination** (GI) is the whole of a renderer's indirect light, including the light that bounces between surfaces. Many engines use the name for the bounce part alone, and Strata does too: its `GlobalIllumination` setting of the `PostProcessComponent` switches the field that traces bounces, and the sky and the probes work without it.

:::example[Counting the bounces by hand]
How much does bouncing matter? Take a closed room whose walls all have an :term[albedo]{id=albedo} of 0.7: a wall scatters 70 % of the light it receives. Say the lamp's light arriving at the walls is one unit, the direct light.

After the first bounce the walls send back 0.7 units. After the second, 0.7 of 0.7, which is 0.49. After the third, 0.343. The direct light and three bounces give 1 + 0.7 + 0.49 + 0.343 = 2.533 units, so the first three bounces more than double the light in the room.

The bounces never stop in a closed room. The total of 1 + 0.7 + 0.49 + ... is 1 divided by (1 - 0.7), which is 3.33 units. The first three bounces carry 2.533 of 3.33, which is 76 %. With an albedo of 0.9 the total is 10 units, ten times the direct light.
:::

A real room has a window, so some light escapes and the numbers are smaller. They still show that the dark side of a room is not dark, and that the amount and the color depend on the walls.

## The slow, exact answer: path tracing

The equation has an exact answer for a given scene, and a computer can approach it. Monte Carlo path tracing sends a ray from the eye through a pixel. At the surface it hits, it picks one random direction, follows that ray to the next surface, and continues until the ray hits a light or has bounced too often. The color that comes back is one sample of the integral. The average of many samples per pixel converges to the true value ([Probability for games](../basics/math-probability.md)).

One sample is noisy: a ray finds the small light by luck or does not. The error of an average of $n$ samples falls like one over the square root of $n$, so four times the samples halve the error. The program below traces the Cornell box with a fixed seed, so every run gives the same numbers. Its image is the ground truth that [Ambient occlusion](../indirect/ao.md), [Probes](../indirect/probes.md) and [Global illumination with radiance cascades](../indirect/gi-cascades.md) compare themselves against.

:::question
The program uses loops, a `struct`, a `std::vector`, calls such as `std::sqrt(`, and one pointer in `main`. If these are new, read [Programming 2](../basics/programming-2.md), [Programming 3](../basics/programming-3.md) and [Memory in C++](../basics/cpp-memory.md) first.
:::

The program renders a 24 by 24 image at 4, 64 and 1,024 samples per pixel and measures each against a 4,096-sample image. It also prints one floor pixel near the red wall, lit by direct light only and then by every bounce. Read the walls, the ray loop and the last lines.

```cpp sketch="indirect-problem-pathtracer.cpp"
// Path traces a Cornell box: random bounces, a fixed seed, and more samples per pixel for less noise.
#include <glm/glm.hpp>

#include <cmath>
#include <cstdint>
#include <cstdio>
#include <vector>

struct Random
{
	uint64_t State = 12345;

	float Next() // A number in [0, 1)
	{
		State = State * 6364136223846793005ULL + 1442695040888963407ULL;
		return float(State >> 40) / 16777216.0f;
	}
};

struct Wall
{
	int Axis = 0;
	float Position = 0.0f;
	glm::vec3 Albedo = glm::vec3(0.0f);
};

// The box is 2 wide, 2 deep and 2 high with its front open. The last wall is the ceiling, with a light patch in it.
const Wall c_Walls[5] = { { 0, -1.0f, { 0.63f, 0.065f, 0.05f } }, { 0, 1.0f, { 0.14f, 0.45f, 0.09f } },
	{ 2, -1.0f, { 0.7f, 0.7f, 0.7f } }, { 1, 0.0f, { 0.7f, 0.7f, 0.7f } }, { 1, 2.0f, { 0.7f, 0.7f, 0.7f } } };
const float c_LightRadiance = 18.0f;
const float c_LightHalfSize = 0.3f;

bool InsideBox(const glm::vec3& point)
{
	return std::abs(point.x) <= 1.001f && point.y >= -0.001f && point.y <= 2.001f && std::abs(point.z) <= 1.001f;
}

// The light that arrives along a ray, after at most maxBounces scatterings.
glm::vec3 Radiance(glm::vec3 origin, glm::vec3 direction, int maxBounces, Random& random)
{
	glm::vec3 throughput(1.0f);
	for (int bounce = 0; bounce <= maxBounces; bounce++)
	{
		float nearest = 1e30f;
		int hit = -1;
		for (int i = 0; i < 5; i++)
		{
			const float along = direction[c_Walls[i].Axis];
			if (std::abs(along) < 1e-6f)
				continue;
			const float t = (c_Walls[i].Position - origin[c_Walls[i].Axis]) / along;
			if (t > 1e-4f && t < nearest && InsideBox(origin + direction * t))
			{
				nearest = t;
				hit = i;
			}
		}
		if (hit < 0)
			return glm::vec3(0.0f); // The ray left through the open front
		origin += direction * nearest;
		if (hit == 4 && std::abs(origin.x) < c_LightHalfSize && std::abs(origin.z) < c_LightHalfSize)
			return throughput * c_LightRadiance; // The light patch emits and absorbs
		// A rough surface scatters toward a random direction, favoring those near its normal.
		const int axis = c_Walls[hit].Axis;
		const float side = direction[axis] > 0.0f ? -1.0f : 1.0f;
		const float angle = 6.2831853f * random.Next();
		const float radius = std::sqrt(random.Next());
		direction[(axis + 1) % 3] = radius * std::cos(angle);
		direction[(axis + 2) % 3] = radius * std::sin(angle);
		direction[axis] = side * std::sqrt(1.0f - radius * radius);
		throughput *= c_Walls[hit].Albedo; // The cosine and the sampling density cancel
	}
	return glm::vec3(0.0f);
}

std::vector<glm::vec3> Render(int size, int samples, int maxBounces, uint64_t seed)
{
	Random random;
	random.State = seed;
	std::vector<glm::vec3> image(size * size, glm::vec3(0.0f));
	for (int y = 0; y < size; y++)
	{
		for (int x = 0; x < size; x++)
		{
			glm::vec3 sum(0.0f);
			for (int s = 0; s < samples; s++)
			{
				const float u = ((x + random.Next()) / size * 2.0f - 1.0f) * 0.45f;
				const float v = (1.0f - (y + random.Next()) / size * 2.0f) * 0.45f;
				sum += Radiance(glm::vec3(0.0f, 1.0f, 3.4f), glm::normalize(glm::vec3(u, v, -1.0f)), maxBounces, random);
			}
			image[y * size + x] = sum / float(samples);
		}
	}
	return image;
}

float RootMeanSquareError(const std::vector<glm::vec3>& image, const std::vector<glm::vec3>& reference)
{
	double sum = 0.0;
	for (size_t i = 0; i < image.size(); i++)
	{
		const glm::vec3 difference = image[i] - reference[i];
		sum += glm::dot(difference, difference);
	}
	return float(std::sqrt(sum / (3.0 * image.size())));
}

// The picture for the page's figure: gamma-encoded bytes in the PPM format, written when the program gets any argument.
void WritePicture(const std::vector<glm::vec3>& image, int size)
{
	std::printf("P6\n%d %d\n255\n", size, size);
	for (const glm::vec3& color : image)
	{
		for (int channel = 0; channel < 3; channel++)
			std::putchar(int(255.0f * std::pow(glm::clamp(color[channel], 0.0f, 1.0f), 1.0f / 2.2f) + 0.5f));
	}
}

int main(int argc, char**)
{
	if (argc > 1)
	{
		WritePicture(Render(320, 4096, 8, 4), 320);
		return 0;
	}
	const int size = 24;
	const std::vector<glm::vec3> reference = Render(size, 4096, 8, 1);
	for (int samples : { 4, 64, 1024 })
		std::printf("%4d samples: error %.3f\n", samples, RootMeanSquareError(Render(size, samples, 8, 2), reference));

	// One floor pixel near the red wall, lit directly only and then with every bounce.
	const glm::vec3 direct = Render(size, 4096, 1, 3)[20 * size + 6];
	const glm::vec3 full = reference[20 * size + 6];
	std::printf("direct only: red %.3f green %.3f\n", direct.r, direct.g);
	std::printf("all bounces: red %.3f green %.3f\n", full.r, full.g);
	return 0;
}
```

```text output-of="indirect-problem-pathtracer.cpp"
   4 samples: error 0.816
  64 samples: error 0.231
1024 samples: error 0.052
direct only: red 0.252 green 0.252
all bounces: red 0.454 green 0.380
```

1. **Line 28:** the five walls: the axis each one is perpendicular to, its position, and its albedo, red on the left and green on the right.
2. **Line 58:** a ray that leaves through the open front returns black.
3. **Lines 61–62:** the light patch emits and ends the path.
4. **Lines 66–71:** a hit scatters toward a random direction and the path keeps the wall's albedo, as the rendering equation asks.
5. **Line 133:** with at most one bounce, only direct light counts.

The first three lines show the error falling about 3.5 times and then 4.4 times for each growth of the samples by 16. That is close to the rule of a quarter; the reference image has some error of its own.

The last two lines show color bleeding. With direct light only the red and green values are equal, because the floor and the lamp are gray. With every bounce the red value is 0.454 and the green 0.380: the red wall has lent its color to the floor, and its red value is 80 % higher than direct light alone gives.

## How engines solve it

Each family below begins with the flaw of the one before it. A constant ambient has no direction, so engines next give it one: a hemisphere ambient blends a sky color above and a ground color below. It knows up from down but has no occlusion and no place. Image-based lighting replaces the two colors with a picture of the whole sky, which gives the right color from every direction. It is still the same indoors and outdoors.

Local probes capture the surroundings at a point and light everything near it, so a room can have its own ambient light. A probe needs placing by hand, one point stands for a region, and its capture is fixed.

Screen-space effects compute from the picture itself: ambient occlusion darkens creases, screen-space reflections trace the :term[depth buffer]{id=depth-buffer} for mirror reflections, and screen-space global illumination gathers bounce light from nearby pixels. They are cheap and dynamic, but they see only what is on screen. Anything behind a pillar or past the edge is missing.

The baked family computes the light before the game runs. **Radiosity**, a method of the 1980s, solves the exchange of diffuse light between the patches of a scene. Each patch gathers light from the others. The solution goes into lightmaps, which are textures that hold the light of surfaces, or into irradiance volumes, which are grids of light samples that moving objects read.

The quality of a bake is high and the run-time cost is a texture read. Nothing moves, though: a lamp that changes, a door that opens or a day and night cycle needs a new bake.

Dynamic world-space methods keep the light alive in the world and not on the screen. Grids of probes that update every frame store the light at points in space and blend between them. Voxel cone tracing turns the scene into a grid of small cubes, called voxels, and traces cones through it. Signed distance fields, the base of Unreal Engine's :term[Lumen]{id=lumen}, trace rays through a field of distances. Radiance cascades place probes in several levels, finest nearby, and each level covers a larger range of distances with fewer rays.

Hardware ray tracing asks the :term[graphics card]{id=gpu} to test rays against the real triangles. It gives the best quality at the highest cost, and it needs a card that can do it.

| Family | Cost | Quality | Complexity | Used by |
| --- | --- | --- | --- | --- |
| Constant or hemisphere ambient | Nearly none | Flat, no occlusion | Minimal | The fallback of every engine |
| Image-based lighting | One filtered cube | Right color, no place | Low | Filament, Unreal, Unity |
| Local probes | A capture per probe | Good inside the box | Medium: placing and baking | Unity, Unreal, Strata |
| Screen-space effects | A pass over the image | Good on screen, blind off it | Medium: history and noise | Crysis (occlusion), Unreal, Unity |
| Baked lightmaps, radiosity, volumes | A bake, then a lookup | Highest for what is static | Medium: bake tools | Quake, Unreal, Unity |
| Dynamic world-space methods | Memory and several passes every frame | Good, dynamic, leaks through thin walls | High | Lumen, Path of Exile 2, Strata |
| Hardware ray tracing | The most, and a capable card | Closest to the reference | High | Lumen's hardware mode, Metro Exodus |

The source for each row is in Further reading. Engines mix these ideas, so a name stands for a family and not for one fixed method.

## Strata's choice: two gathers, layer over layer

Strata uses most rows of the table, each for the part of the light it approximates well. Its shader of the indirect light is `Strata/shaders/Include/IndirectLight.slang`. `GatherIndirectDiffuse` computes the diffuse part and `GatherIndirectSpecular` the specular part, and `ComposeIndirect` joins them. The two pick their source by a form: the probes, screen-space reflections without probes, the sky, or the constant ambient when nothing else exists.

```slang src="Strata/shaders/Include/IndirectLight.slang#L122-L129"
float3 ComposeIndirect(IndirectInputs inputs, float3 diffuse, float3 specular)
{
	if (inputs.Form == ST_INDIRECT_AMBIENT)
		return diffuse;
	if (inputs.Form == ST_INDIRECT_SKY)
		return (diffuse + specular) * u_Frame.EnvironmentParams.x;
	return diffuse + specular;
}
```

The compose step is short because the work is in the gathers, which stack layers. For specular light, a screen-space reflection replaces the light of the probe or the sky by its confidence, and the probe sits over the sky. For diffuse light, the global illumination field replaces the light of the form by a weight (`GatherIndirectField` and `FieldWeight`), and the constant ambient lies below all of them. [The seam](../indirect/seam.md) draws the whole stack.

The bounce part is the experimental world-space field: radiance cascades over a voxel clipmap, a voxel copy of the area around the camera in levels whose voxels double in size from one to the next. Probes placed in the world send rays across it. A scene asks for it with `GlobalIllumination` in the `PostProcessComponent`, which is off by default, and the graphics quality's row for it is off at the Low and Medium presets. A frame without the field has the image the engine drew before the field existed, bit for bit. [Global illumination on voxels](../indirect/gi-voxels.md) and [Global illumination with radiance cascades](../indirect/gi-cascades.md) teach how it works.

:::why[Why global illumination traces world data and never the screen]
A screen-space method can use only what the depth buffer and the previous image hold. A light source beyond the screen's edge, or the back of a pillar, does not exist for it, so the light changes when the camera turns. To hide its noise it needs temporal accumulation, the average of several frames, which smears light over moving objects and flickers when history is rejected.

Strata's field is a function of the world and of where the camera stands now, never of where it stood or what it saw. A frame has the same light whether the camera walked there or cut there, and a light source off screen lights the room as well as one on screen. The price is memory for the voxels and the probes, and the thin-wall limit of the next section. The engine's developer guide states the rule: world data only, never the screen.
:::

## What Strata's choice cannot do

Strata does not test rays against the scene's triangles with the graphics card's ray tracing. Its field works on a voxel copy of the scene, so it is coarser than path tracing. [What the field cannot do](../indirect/gi-limits.md) lists its limits, such as the leaks of thin walls.

Strata has no lightmaps and no baked global illumination. The only bake is that of reflection probes, which the command `lighting.bakeProbes` renders from the edited scene into a texture. The release notes of 0.7.0 list a baked irradiance volume as planned for a later wave, and the engine has none. [What Strata does not do](../appendix/not-in-strata.md) covers lightmaps and ray-traced lighting in general.

## Common mistakes

- **Treating ambient light as a constant that brightens the shadows.** The symptom is a flat, gray picture in which a cave and a beach look alike. Take the light from the sky, from probes and from the bounce field, and leave `AmbientColor` as the last fallback.
- **Expecting global illumination to be free bounce light.** The symptom is a slower frame and more memory once the field runs. It costs a pass and memory every frame, so enable it where the look needs it.
- **Ignoring leaks through thin walls.** The symptom is light inside a closed room, next to a thin wall that has a bright side. A voxel method cannot see a wall thinner than its voxel. Thicken the wall, or read the limits page before you trust a thin one.

## Summary

- Light leaving a surface has three parts: direct light from lamps, indirect diffuse light and indirect specular light. Strata approximates them with lights, the sky, probes, the bounce field, ambient occlusion and screen-space reflections.
- Bounces add up as a series: for walls of albedo 0.7 the first three bounces carry 76 % of the light of a closed room, and the total is 3.33 times the direct light.
- Monte Carlo path tracing solves the rendering equation by random bounces; its error falls like one over the square root of the samples, so four times the samples halve it.
- Engines choose among constant ambient, image light, probes, screen-space effects, baked light, dynamic world-space methods and ray tracing, trading cost, quality and complexity.
- Strata's global illumination traces world data, never the screen, so it is steady and does not miss what is off screen.

## Check yourself

1. Which of these is indirect light?
   - A. Light from a lamp that reaches a wall in one step.
   - B. Light that bounced off the red wall onto the floor.
   - C. A constant color added to every surface.
   - D. The sky's light reaching a surface.

   :::answer{tests="three-parts"}
   B and D. Indirect light reached the surface after at least one bounce, or came from the sky, a distant light source. A is direct light. C is no light at all: it stands in for the indirect part, and Strata keeps it only as the last fallback.
   :::

2. A closed room has walls of albedo 0.5. What share of its total light do the direct light and two bounces carry?

   :::answer{tests="bounce-count"}
   The total is 1 divided by (1 - 0.5), which is 2 units. The direct light and two bounces give 1 + 0.5 + 0.25 = 1.75 units, which is 1.75 / 2 = 87.5 % of the total. Darker walls converge faster than the 0.7 walls of the page.
   :::

3. The error of path tracing is 0.6 at 16 samples per pixel. At how many samples is it about 0.15?

   :::answer{tests="noise"}
   The target is 0.15 / 0.6, a quarter of the first error. The error falls like one over the square root of the samples, so a quarter needs 16 times the samples: 256. Four times the samples (64) would give only half, 0.3.
   :::

4. A lamp sits beyond the edge of the picture and lights a room. Why would a screen-space method miss its light, and what does Strata do instead?

   :::answer{tests="world-data"}
   A screen-space method knows only what the picture holds, so a lamp beyond the edge does not exist for it. Strata's field traces a voxel copy of the world around the camera, so it lights the room whatever the screen shows. It also needs no history, which avoids flicker and smear.
   :::

5. Which family suits a small game for phones: probes, baked lightmaps or ray tracing? Name the cost of your choice.

   :::answer{tests="choose-family"}
   Baked lightmaps suit it if the level does not change, because a bake costs nothing at run time. The price is that nothing may move: a lamp that changes needs a new bake. Ray tracing needs a card that most phones lack, and Strata itself has no lightmaps.
   :::

## Exercises

1. **Basic.** Predict the error of the page's program at 16 samples per pixel from its errors at 4 and 64. Then change the list of sample counts to 4, 16, 64, 256 and 1,024, run it and compare.

   :::answer[Worked solution]{tests="noise"}
   The rule gives half the error for four times the samples, so 16 samples should give about half of 0.816, which is 0.41, and 256 samples half of 0.231, which is 0.12. The run gives 0.472 and 0.125. The first is a little high because 4 samples are too few for the rule to hold well.
   :::

2. **Medium.** Choose a family of the table for three games and name what each choice costs: a fixed indoor level, an open world with a day and night cycle, and a small game for phones.

   :::answer[Worked solution]{tests="choose-family"}
   The fixed indoor level fits baked lightmaps: the best quality for static light, at the cost of a bake and no moving lamps. The open world needs a dynamic world-space method, such as Strata's field with image light from the sky, at the cost of memory and a pass every frame. The phone game fits image light and a few probes, at the cost of bounce light that is only approximate.
   :::

3. **Medium.** Write a program that prints the share of a closed room's total light after each bounce for walls of albedo 0.7, and stops at the first bounce that reaches 90 %.

   :::answer[Worked solution]{tests="bounce-count" solution="sketches/indirect-problem-bounces.cpp"}
   The total is 1 divided by (1 - albedo). The loop adds the light of each bounce, multiplies the next bounce's light by the albedo and stops once the sum reaches 90 % of the total.

   ```cpp sketch="indirect-problem-bounces.cpp"
   // Counts the bounces a closed room needs before its light is 90 % of the total, for walls of albedo 0.7.
   #include <cstdio>

   int main()
   {
   	const double albedo = 0.7;
   	const double total = 1.0 / (1.0 - albedo); // 1 + 0.7 + 0.49 + ... without end, in units of the direct light
   	double lightSoFar = 0.0;
   	double lightOfBounce = 1.0; // The direct light is bounce 0
   	int bounce = 0;
   	while (lightSoFar / total < 0.9)
   	{
   		lightSoFar += lightOfBounce;
   		std::printf("bounce %d: %.3f of the total\n", bounce, lightSoFar / total);
   		lightOfBounce *= albedo;
   		bounce++;
   	}
   	return 0;
   }
   ```

   ```text output-of="indirect-problem-bounces.cpp"
   bounce 0: 0.300 of the total
   bounce 1: 0.510 of the total
   bounce 2: 0.657 of the total
   bounce 3: 0.760 of the total
   bounce 4: 0.832 of the total
   bounce 5: 0.882 of the total
   bounce 6: 0.918 of the total
   ```

   1. **Line 7:** the total light of the series, in units of the direct light.
   2. **Lines 11–16:** each pass adds one bounce and prints the share so far.
   3. **Line 15:** the light of the next bounce is the albedo times the light of this one.

   The output stops at bounce 6, as the algebra says: 1 - 0.7 to the seventh power is 0.918, while after bounce 5 the share is only 0.882.
   :::

## Where it lives in Strata

- `Strata/shaders/Include/IndirectLight.slang`: the two gathers, the field's gather and the compose step.
- `Strata/src/Strata/Renderer/RendererComponents.h`: `SkyLightComponent` (with `AmbientColor`), `ReflectionProbeComponent` and `PostProcessComponent` (with `GlobalIllumination`, `AmbientOcclusion` and `ScreenSpaceReflections`).
- `lighting.bakeProbes`: the editor command that renders the captures of reflection probes, the only bake.
- `Tools/LookDev/LookDevScene.json` and `Tools/LookDev/Shots.json`: the Cornell box and its shot, with a panel as the only light.
- The graphics quality row `GlobalIllumination`: off at the Low and Medium presets.

## Further reading

- James Kajiya, "The Rendering Equation" (1986): the paper that defines the equation; advanced.
- Matt Pharr, Wenzel Jakob and Greg Humphreys, "Physically Based Rendering", chapters on path tracing: the book on Monte Carlo light transport; intermediate.
- Cindy Goral and others, "Modeling the Interaction of Light Between Diffuse Surfaces" (1984): the origin of radiosity; advanced.
- Cyril Crassin and others, "Interactive Indirect Illumination Using Voxel Cone Tracing" (2011): voxel cone tracing; advanced.
- Zander Majercik, Morgan McGuire and others, "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields" (2019): probe grids; intermediate.
- Alexander Sannikov, "Radiance Cascades" (2023): the method behind Strata's field; advanced.
- Epic Games, the Unreal Engine documentation of Lumen: signed distance fields and hardware ray tracing in a shipped engine; beginner.
