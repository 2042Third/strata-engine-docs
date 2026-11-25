---
id: indirect/ibl
title: "Image-based lighting and the split sum"
description: "How Strata turns any sky into an irradiance cube and a prefiltered cube that every surface reads in one or two texture reads."
kind: internals
size: L
tracks: [E]
needs: [light/energy, light/sky, basics/math-sphere, gpu/compute]
time: 75
learn:
  - id: explain-chain
    text: explain how one filter chain turns every sky source into an irradiance cube and a prefiltered cube
  - id: explain-split-sum
    text: explain the split sum and name where it fails
  - id: compute-mip
    text: compute the source mip that filtered importance sampling reads for a roughness and a sample count
  - id: compute-horizon-fade
    text: compute the horizon fade of a reflected vector that points below the surface
  - id: trace-sky-change
    text: trace a change of the sky to the cube and find what makes no new cube
since: 0.3.0
status: final
---

A sky is a picture of light from every direction, and a surface needs one number from it per pixel. **Image-based lighting** (IBL) is the technique that answers this by filtering the picture ahead of time, so that the :term[shader]{id=shader} reads the answer instead of adding up the sky. Strata makes the answer with one chain for every sky source: an environment cube, an :term[irradiance]{id=irradiance} cube and a prefiltered cube. This page follows the chain from a source to the texture reads in the forward pass. It does not teach the sky's own look or its sources (the page on [the sky](../light/sky.md) does), and the table of scale and bias of :term[F0]{id=f0} belongs to [the energy page](../light/energy.md).

## The problem and how engines solve it

A surface in the open sees a whole sphere of light. Shading one pixel would add up thousands of directions of sky, for every pixel of every frame. The ideas below turn that sum into a texture read, in three steps: store the sky, answer the diffuse question, answer the shiny question.

### Storing the sky: equirectangular maps and cubes

A photograph of a whole sky is stored as an **equirectangular** image. Its columns are the angle around the vertical axis, and its rows run from straight up (top row) to straight down (bottom row). A school atlas maps the Earth the same way. The rectangle is convenient to save and edit, but it wastes texels at the poles, where a whole row shows one point.

The :term[renderer]{id=renderer} prefers a **cube map**: a texture of six square faces, one for each of +X, -X, +Y, -Y, +Z and -Z, that is read with a direction instead of a coordinate pair. The hardware picks the face from the direction's largest component and filters across the seams. Every texel of a cube covers a similar share of the sphere.

Each face needs a name for its axes. Strata's rule (`CubeTexelDirection` in `Strata/shaders/Include/IBL.slang`) puts texel row 0 at the top of each face and maps the texel's centre to coordinates $s$ and $t$ between -1 and 1. Face 0 (+X) points along $(1, -t, -s)$, and the other five faces follow the :term[Vulkan]{id=vulkan} and Direct3D convention. One wrong face shows as a seam in the sky, turned by a quarter turn.

:::example[A texel and a direction by hand]
Take a cube with 4 texels on a side. Texel (0, 0) of the +X face has its centre at $s = t = (0.5/4) \times 2 - 1 = -0.75$, so its direction is $(1, 0.75, 0.75)$ before :term[normalizing]{id=normalization}, a point up and to the side of the face's centre. The texel (1, 1) gives $s = t = -0.25$ and the direction $(1, 0.25, 0.25)$, closer to the axis.

To read an :term[equirectangular map]{id=equirectangular-map} in direction $(0, 0, 1)$ (along +Z), `DirectionToEquirect` computes $u = \operatorname{atan2}(z, x)/2\pi + 0.5$ and $v = \arccos(y)/\pi$. Here $\operatorname{atan2}(1, 0)$ is $\pi/2$, so $u = 0.75$ and $v = 0.5$: three quarters of the way across the middle row. For direction $(0, 1, 0)$ both $x$ and $z$ are 0 and $\operatorname{atan2}(0, 0)$ is undefined, so the shader uses $u = 0.5$. At the pole every column is the same point, so the guard only keeps a not-a-number value out of the cube.
:::

```mermaid caption="A direction picks a cube face from its largest component. An equirectangular map reads the same direction as two angles." alt="A flow chart. A direction leads to a cube face and a texel on it. The same direction leads to a column and a row of an equirectangular map. Straight up or down needs a guard."
flowchart LR
  A["Direction (x, y, z)"] --> B["Cube: face of the largest component, texel from the other two"]
  A --> C["Equirectangular: u from atan2(z, x), v from acos(y)"]
  C --> D["Straight up or down: x and z are 0, u = 0.5"]
```

The other fact a texel carries is its **solid angle**, the share of the sphere it covers, in :term[steradians]{id=steradian}. The whole sphere is $4\pi$ steradians, so six faces of $n \times n$ texels give on average $4\pi/(6n^2)$ each. The true value is smaller near a face's corners, where the face is farther away, but the average serves where the text below uses it. [Spheres and solid angles](../basics/math-sphere.md) derives the exact value.

### The diffuse question: the cosine convolution

A diffuse surface with normal $n$ reflects light from the hemisphere above it, and a ray at angle $\theta$ to the normal counts $\cos\theta$ times as much as a ray along it. The total is the sky's :term[radiance]{id=radiance}, averaged over the hemisphere with weight $\cos\theta$. This is a :term[convolution]{id=convolution} of the sky with a :term[cosine]{id=cosine} lobe, and it depends only on $n$. So it is computed once per direction and stored in a small cube of 32 texels a face: smooth light needs few texels.

Strata holds this answer in three stores. The sky stores it as an irradiance cube (this page). A reflection probe stores nine coefficients of :term[spherical harmonics]{id=spherical-harmonics} for each colour channel (the page on [probes](probes.md)). The global illumination field stores one value per axis direction in each cell, an ambient cube (the page on [the cascades](gi-cascades.md)). The cube costs the most memory and has the least error, the nine coefficients cost the least, and all three smooth the sky beyond recognition, which is the point.

### The shiny question: the split sum

A shiny surface reflects a narrow cone of the sky around the mirror direction $R$, and the cone widens with roughness. The reflected light is the integral of the sky times the specular lobe, and the lobe changes with the view, the normal and the roughness. That is too many inputs for one texture.

The **split-sum approximation** (Karis, 2013) cuts the integral into a product of two averages. One is the average of the sky weighted by the lobe. The other is the average of the lobe itself, which [the energy page](../light/energy.md) calls directional albedo and stores as scale and bias of F0. That second factor depends on only the view angle and the roughness.

Strata already has it as a table of the bidirectional :term[reflectance]{id=reflectance} distribution function (:term[BRDF]{id=brdf}) integral. The first factor depends on only a direction and a roughness once you assume the normal, the view and the reflection are one direction, $N = V = R$. It then fits a cube with one level for each roughness.

```mermaid caption="The split sum multiplies two averages: the prefiltered sky along the reflected direction, and the table of scale and bias." alt="A flow chart. The prefiltered sky, read along the reflected direction at the level of the roughness, and the table's scale and bias both lead to the specular image light."
flowchart LR
  A["Prefiltered sky: direction R, level from roughness"] --> C["Specular image light"]
  B["BRDF table: F0 x scale + bias, from NoV and roughness"] --> C
```

:::why[Why accept N = V = R]
Without that assumption the prefiltered sky would need the view too, and a cube would grow into a table with five inputs. The cost is a lobe that is round at every angle: real reflections at grazing angles stretch into long streaks along the surface, which a prefiltered cube cannot show. Strata accepts the loss, as most real-time engines do, and the page on [the seam](seam.md) shows where screen-space reflections and probes take over.
:::

Importance sampling the lobe is how the cube is filled, and [the probability page](../basics/math-probability.md) teaches it. The filter draws directions that cluster around the lobe's centre, weights each by the cosine, and averages. A narrow lobe needs few samples and a wide one thousands, so the chain below makes the loop cheap.

## The map of the filter chain

The chain begins with a **source**: a :term[high dynamic range]{id=high-dynamic-range} (:term[HDR]{id=high-dynamic-range}) map, the :term[procedural sky]{id=procedural-sky} or the atmosphere. Each source becomes the first level of an environment cube of 512 texels a face, in half-precision :term[floating point]{id=floating-point-number} (RGBA16F). The chain then makes the levels of that cube, the irradiance cube and the **prefiltered environment**, the sky's specular cube with six levels for roughness 0 to 1 in steps of 0.2. The prefiltered cube's size is the quality row `EnvironmentResolution`: 256 texels a face in the two lowest presets, 512 in the two highest.

```mermaid caption="Every sky source fills mip 0 of the 512 texel environment cube. One chain then makes the cube's levels, the irradiance cube and the six prefiltered levels, and a reflection probe's capture takes a branch of its own." alt="A flow chart. Three sources, an HDR map, the procedural sky and the atmosphere, lead into the environment cube. The cube leads to a step that makes its levels, then to the irradiance cube and to the six prefiltered levels. A faint branch from a probe capture leads to the same chain."
flowchart LR
  A["HDR map: EquirectToCube"] --> C["Environment cube, mip 0"]
  B["Procedural sky: ProceduralSky.comp"] --> C
  D["Atmosphere cube, 14 frames"] --> C
  C --> E["CubeDownsample: levels 1 to 9"]
  E --> F["Irradiance.comp: 32 texels a face"]
  E --> G["Prefilter.comp: 6 levels"]
  H["Probe capture"] -.-> E
  F --> I["Forward pass: 1 read"]
  G --> I
```

Three rules of the chain shape the code. First, every source goes through the same steps, so a bug in a step shows in all of them. Second, the chain runs only when the sky changes, never every frame. Third, the chain has no :term[graphics processing unit]{id=gpu} (:term[GPU]{id=gpu}) stage of its own for that reason: a stage names work that runs each frame.

A **cube array** is a texture that holds many cubes, one per slot, read with an index. Reflection probes keep their captures in one and run the same shaders on each capture, with sample counts and an irradiance of their own.

## The contract

Callers and shaders rely on the chain's rules. Each has a reason.

- The environment cube holds radiance as the source gave it, in RGBA16F, and a map's values are clamped to 65,000 on the way in. Reason: the sun's disk in an HDR photograph can exceed what a half float holds.
- The prefiltered cube's level $k$ holds roughness $k/5$, and the forward pass reads it at `roughness` times `EnvironmentParams.z`, which is 5. Reason: a shader never needs to know which roughness a level holds, only that the mapping is linear.
- Diffuse light reads the irradiance cube along the :term[surface normal]{id=surface-normal}, and specular light reads the prefiltered cube along $R$; both read through the sky's rotation (maps only) and intensity. Reason: the cubes hold the sky as filtered, and the sky light's rotation and intensity change often, so applying them at the read costs no new cube.
- A still sky makes no new cube. A sky that changes makes one cube, in place. Reason: the chain is the costliest part of the sky, and a sky that does not change needs none of it.
- Without an environment the constant `AmbientColor` lights the base's diffuse only; the clear coat reads it as a uniform sky. Reason: a flat colour has no direction to reflect.

:::rule[Light keeps its energy]
`AGENTS.md` says that light keeps its energy: specular light is compensated for multiple scattering, and lighting changes are checked with the white furnace. The prefiltered cube is one half of that bargain, because it holds the sky's average and not a darker lobe. The reason is on [the energy page](../light/energy.md).
:::

:::rule[Costly knobs are rows of the quality settings]
`AGENTS.md` says that a costly option is a row of `RendererQualitySettings` with its four presets, and that Medium keeps the costs of release 0.6.0. `EnvironmentResolution` is such a row, and the 256 texel cube with 512 samples is 0.6.0's cost. The reason is that a row has a memory function and a preset, so the settings stay consistent; see [the quality settings page](../image/quality-settings.md).
:::

## A toy version

The toy runs the cosine convolution over a cube of 8 texels a face on the :term[central processing unit]{id=processor} (:term[CPU]{id=processor}). The sky is radiance 1 above the horizon and 0 below it, so you can predict every answer by hand. For a normal pointing up, the whole lit half of the sphere lights the surface, and the cosine-weighted sum divided by $\pi$ is exactly 1. For a normal pointing sideways, half of that hemisphere is dark, and the answer is 0.5. For a normal pointing down, no light arrives and the answer is 0.

```cpp sketch="indirect-ibl-toy.cpp"
// A toy irradiance convolution: a tiny cube map of radiance, and the cosine-weighted average of it around a normal.
#include <cmath>
#include <cstdio>

struct Vec3
{
	float X, Y, Z;
};

constexpr int c_Size = 8;
constexpr float c_Pi = 3.14159265f;

// The engine's face convention: +X, -X, +Y, -Y, +Z, -Z, texel row 0 at the top of each face.
Vec3 FaceDirection(float s, float t, int face)
{
	switch (face)
	{
		case 0: return { 1.0f, -t, -s };
		case 1: return { -1.0f, -t, s };
		case 2: return { s, 1.0f, t };
		case 3: return { s, -1.0f, -t };
		case 4: return { s, -t, 1.0f };
		default: return { -s, -t, -1.0f };
	}
}

// The sky: radiance 1 above the horizon, 0 below it.
float SkyRadiance(const Vec3& direction)
{
	return direction.Y > 0.0f ? 1.0f : 0.0f;
}

// The convolution at one normal: sum of radiance * cosine * solid angle, divided by pi.
float Irradiance(const Vec3& normal)
{
	float sum = 0.0f;
	float totalSolidAngle = 0.0f;
	for (int face = 0; face < 6; face++)
		for (int row = 0; row < c_Size; row++)
			for (int column = 0; column < c_Size; column++)
			{
				float s = (static_cast<float>(column) + 0.5f) / c_Size * 2.0f - 1.0f;
				float t = (static_cast<float>(row) + 0.5f) / c_Size * 2.0f - 1.0f;
				Vec3 d = FaceDirection(s, t, face);
				float length = std::sqrt(d.X * d.X + d.Y * d.Y + d.Z * d.Z);
				d = { d.X / length, d.Y / length, d.Z / length };
				// A texel near a face's corner is seen under a smaller angle than one at its center.
				float solidAngle = (2.0f / c_Size) * (2.0f / c_Size) / std::pow(1.0f + s * s + t * t, 1.5f);
				float cosine = d.X * normal.X + d.Y * normal.Y + d.Z * normal.Z;
				totalSolidAngle += solidAngle;
				if (cosine > 0.0f)
					sum += SkyRadiance(d) * cosine * solidAngle;
			}
	std::printf("  solid angles add up to %.4f (4 pi is %.4f)\n", totalSolidAngle, 4.0f * c_Pi);
	return sum / c_Pi;
}

int main()
{
	std::printf("normal up:\n");
	std::printf("  irradiance / pi = %.4f\n", Irradiance({ 0.0f, 1.0f, 0.0f }));
	std::printf("normal sideways:\n");
	std::printf("  irradiance / pi = %.4f\n", Irradiance({ 1.0f, 0.0f, 0.0f }));
	std::printf("normal down:\n");
	std::printf("  irradiance / pi = %.4f\n", Irradiance({ 0.0f, -1.0f, 0.0f }));
	return 0;
}
```

1. **Lines 14–25:** the six faces' directions, the same cases as `CubeTexelDirection`.
2. **Line 48:** the texel's solid angle, smaller at the face's corners than at its centre.
3. **Lines 51–52:** only texels above the surface's horizon count, each weighted by its cosine.

```text output-of="indirect-ibl-toy.cpp"
normal up:
  solid angles add up to 12.6145 (4 pi is 12.5664)
  irradiance / pi = 1.0086
normal sideways:
  solid angles add up to 12.6145 (4 pi is 12.5664)
  irradiance / pi = 0.5043
normal down:
  solid angles add up to 12.6145 (4 pi is 12.5664)
  irradiance / pi = 0.0000
```

The three values come out as predicted, and the solid angles add up to 12.61 where the sphere has 12.57. The 0.4 % surplus is the price of using each texel's centre as if the whole texel were there, and it explains the 1.0086 where the exact answer is 1. A real cube has 512 texels a face, where this error is far smaller. The toy is the answer to one pixel; the real code is the answer for every normal, in parallel, with a smarter way to add.

## The real code

The real code follows the data: how each source becomes the cube, the chain's steps, the prefiltered levels, the irradiance, and then the frame's decisions and the forward pass.

### From a source to the cube

An HDR map takes the compute shader `EquirectToCube` (`Strata/shaders/IBL/EquirectToCube.comp.slang`). For each texel of :term[mip]{id=mip} 0 it builds the texel's direction with `CubeTexelDirection`, converts it with `DirectionToEquirect` and samples the map. It samples a mip of the map whose texel density matches the face (a face spans a quarter of the map's width), and it clamps the colour to 65,000. A cube-map texture asset does not exist in Strata: skies and probe captures are equirectangular HDR textures, made into cubes at run time ([what Strata does not do](../appendix/not-in-strata.md)).

The procedural sky takes `ProceduralSky.comp`, which writes mip 0 from the sky's top, horizon and ground colours and the sun's direction, size and radiance. `UpdateEnvironment` compares the frame's `ProceduralSkyParameters` with those the current cube was made from, and calls `GenerateProceduralSky` only when they differ; each call counts in the statistic `EnvironmentUpdates`. The sky's intensity, background and blur are not parameters: the shading applies them, so they make no new cube. The sun follows the scene's directional light by direction and colour, not by intensity.

::compare{id=sky-source-spheres}

::figure{id=sky-source-spheres-indirect}

The atmosphere's own shaders write its cube, and the renderer refreshes it in 14 frames, a step each: six faces, one step for the cube's levels, one for the irradiance, and six prefiltered levels. `SceneRenderer::c_AtmosphereRefreshSteps` holds that count, and a static assertion ties it to the chain's step count. The refresh, and the half degree of sun movement that starts one, are taught on [the atmosphere page](../light/atmosphere.md). While a refresh runs, the renderer lights with the old maps; the new ones take over when the last step is recorded.

### The chain's steps

`FilterEnvironment` runs the steps in order, and `FilterEnvironmentStep` does one. The split exists so that the atmosphere can spread the steps over frames. There are eight steps: step 0 makes the cube's levels, step 1 the irradiance cube, and steps 2 to 7 one prefiltered level each.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L905-L933" symbol="SceneRenderer::FilterEnvironmentStep"
void SceneRenderer::FilterEnvironmentStep(nvrhi::ICommandList* commandList, const EnvironmentMaps& maps, uint32_t step)
{
	const uint32_t cubeMips = MipCountFor(c_EnvironmentCubeSize);
	if (step == 0)
	{
		for (uint32_t mip = 1; mip < cubeMips; mip++)
		{
			const uint32_t size = std::max(1u, c_EnvironmentCubeSize >> mip);
			DispatchIBL(commandList, m_CubeDownsamplePipeline, maps.Cube, nvrhi::TextureSubresourceSet(mip - 1, 1, 0, 6), nvrhi::TextureDimension::Texture2DArray,
				maps.Cube, mip, nvrhi::TextureDimension::Texture2DArray, RenderData::IBLParameters { size, size * 2, 0.0f, 1 }, 6);
		}
		return;
	}

	const nvrhi::TextureSubresourceSet wholeCube(0, cubeMips, 0, 6);
	if (step == 1)
	{
		DispatchIBL(commandList, m_IrradiancePipeline, maps.Cube, wholeCube, nvrhi::TextureDimension::TextureCube, maps.Irradiance, 0,
			nvrhi::TextureDimension::Texture2DArray, RenderData::IBLParameters { c_IrradianceSize, c_EnvironmentCubeSize, 0.0f, c_IrradianceSamples }, 6);
		return;
	}
	const uint32_t mip = step - 2;
	ST_CORE_ASSERT(mip < c_PrefilteredMipCount, "Environment filter step {} out of range", step);
	const uint32_t size = std::max(1u, maps.PrefilteredSize >> mip);
	const float roughness = static_cast<float>(mip) / static_cast<float>(c_PrefilteredMipCount - 1);
	const uint32_t samples = RendererQuality::GetPrefilterSamples(maps.PrefilteredSize, mip);
	DispatchIBL(commandList, m_PrefilterPipeline, maps.Cube, wholeCube, nvrhi::TextureDimension::TextureCube, maps.Prefiltered, mip,
		nvrhi::TextureDimension::Texture2DArray, RenderData::IBLParameters { size, c_EnvironmentCubeSize, roughness, samples }, 6);
}
```

1. **Lines 908–917:** step 0 builds levels 1 to 9 of the cube, each by `CubeDownsample` from the one above, a 2 by 2 average. Level 0 came from the source.
2. **Lines 920–925:** step 1 makes the irradiance cube with 256 samples a texel; its size is the constant 32.
3. **Lines 926–932:** each later step makes one prefiltered level, of size `PrefilteredSize >> mip` and roughness `mip / 5`, with the sample count from `GetPrefilterSamples`.

The environment texture has 10 levels because a 512 texel cube halves nine times to a single texel. The prefiltered cube has six levels, because six roughness steps are all the shader blends.

### Filtered importance sampling

The job of `Prefilter.comp` is, for each texel of a level, to average the sky inside the specular lobe around the texel's direction. The shader treats that direction as the normal, the view and the reflection at once. At roughness 0 it copies the cube. Otherwise it draws `SampleCount` half vectors from the lobe with `ImportanceSampleGGX` and the Hammersley points, reflects the normal about each to get a light direction, and averages the sky there weighted by the cosine.

::compare{id=mirror-roughness-sweep}

A sample that lands on a bright texel of the full cube gives a noisy sum: a few hundred samples cannot see a small sun. **Filtered importance sampling** fixes this. Each sample reads the mip of the cube whose texels are as large as the part of the sphere the sample stands for. A sample in a wide region reads a blurred texel, and a sample in a narrow lobe reads a sharp one. The estimate is smooth, so 512 samples give no noise.

```mermaid caption="The sample's density gives the solid angle it stands for. Its ratio to a texel's solid angle gives the mip." alt="A flow chart. A sample's density leads to the solid angle the sample stands for. Dividing by a texel's solid angle and taking a logarithm leads to the mip the sample reads."
flowchart LR
  A["Sample's density pdf"] --> B["Solid angle of the sample: 1 / (count x pdf)"]
  B --> C["Divide by the texel's solid angle"]
  C --> D["Mip = 0.5 x log2(ratio) + 1"]
```

The shader below makes one texel of one level. Find the sample count in the loop, the density, and the mip that follows from it.

```cpp src="Strata/shaders/IBL/Prefilter.comp.slang#L22-L59"
void st_Main()
{
	uint3 id = st_GlobalInvocationID;
	if (id.x >= u_Parameters.OutputSize || id.y >= u_Parameters.OutputSize)
		return;

	float3 normal = CubeTexelDirection(id.xy, id.z, u_Parameters.OutputSize);
	if (u_Parameters.Roughness <= 0.0)
	{
		o_Output[int3(id)] = float4(u_Environment.SampleLevel(u_Sampler, normal, 0.0).rgb, 1.0);
		return;
	}

	float alpha = u_Parameters.Roughness * u_Parameters.Roughness;
	float sourceSize = float(u_Parameters.SourceSize);
	float texelSolidAngle = 4.0 * PI / (6.0 * sourceSize * sourceSize);
	float maxMip = log2(sourceSize);

	float3 sum = float3(0.0);
	float weight = 0.0;
	for (uint index = 0u; index < u_Parameters.SampleCount; index++)
	{
		float3 halfVector = ImportanceSampleGGX(Hammersley(index, u_Parameters.SampleCount), normal, alpha);
		float3 light = reflect(-normal, halfVector);
		float NoL = dot(normal, light);
		if (NoL <= 0.0)
			continue;

		// With N = V the half-vector pdf reduces to D(NoH) / 4.
		float NoH = clamp(dot(normal, halfVector), 0.0, 1.0);
		float pdf = DistributionGGX(NoH, alpha) * 0.25;
		float sampleSolidAngle = 1.0 / (float(u_Parameters.SampleCount) * pdf + 1e-4);
		float mip = clamp(0.5 * log2(sampleSolidAngle / texelSolidAngle) + 1.0, 0.0, maxMip);
		sum += u_Environment.SampleLevel(u_Sampler, light, mip).rgb * NoL;
		weight += NoL;
	}
	o_Output[int3(id)] = float4(sum / max(weight, 1e-4), 1.0);
}
```

1. **Lines 28–33:** the texel's direction is the normal, and at roughness 0 the level is a copy of the cube's mip 0.
2. **Lines 44–48:** a half vector is drawn and the light direction reflected; a direction below the horizon of the normal adds nothing.
3. **Lines 50–54:** with $N = V$ the half vector's density reduces to $D/4$, so the sample's solid angle and the mip follow from the formula.
4. **Lines 55–58:** the sample reads the cube at that mip, is weighted by its cosine, and the sum is divided by the weights, not the count.

:::example[Which mip does a sample read?]
Take the 512 texel cube. One of its texels covers $4\pi/(6 \times 512^2) = 7.99 \times 10^{-6}$ steradians. At roughness 0.2, the roughness squared $\alpha$ is 0.04, and the lobe's density at the centre is $D = 1/(\pi \alpha^2) = 198.9$, so the density of the reflected direction is $D/4 = 49.7$. With 128 samples a sample stands for $1/(128 \times 49.7) = 1.57 \times 10^{-4}$ steradians, which is 19.7 texels' worth. The mip is $0.5 \log_2 19.7 + 1 = 3.15$, a level where one texel spans about 9 texels of the full cube on a side.

At roughness 1, $\alpha = 1$, $D = 1/\pi$, that density is 0.0796, and 512 samples stand for 0.0245 steradians. That is 3,070 texels' worth, and the mip is $0.5 \log_2 3070 + 1 = 6.79$. A rough lobe reads very blurred texels, so its samples see the whole cube.
:::

### The budget

The number of samples comes from `GetPrefilterSamples`: 512, except at a size above 256 and levels 1 and 2, where it is 128. A narrow lobe's samples already read fine mips, and four times fewer samples read a mip only one level coarser, so the lobes of level 1 and 2 stay smooth. The 128 also keeps the cost of level 1 at a 512 texel size equal to level 1's cost at 256, because $256^2 \times 6 \times 128$ equals $128^2 \times 6 \times 512$. An atmosphere step then never takes longer than before. The function below holds the rule.

```cpp src="Strata/src/Strata/Renderer/RendererQuality.cpp#L699-L707"
uint32_t GetPrefilterSamples(uint32_t size, uint32_t mip)
{
	// At 512 the narrow lobes of levels 1 and 2 (roughness 0.2 and 0.4) need fewer samples: the filtered importance
	// sampling reads source levels as fine as their lobes, and 128 keeps level 1 at 0.6.0's level 1 cost (256^2 x 6 x
	// 128 = 128^2 x 6 x 512), so a refresh step of the atmosphere never takes longer than before.
	constexpr uint32_t c_Samples = 512;
	constexpr uint32_t c_NarrowLobeSamples = 128;
	return size > 256 && (mip == 1 || mip == 2) ? c_NarrowLobeSamples : c_Samples;
}
```

The constants name the two budgets, and the comment in the function gives the same cost argument. Level 0 takes no samples at all, since it copies the cube.

### The irradiance shader

`Irradiance.comp.slang` is the same idea with the cosine lobe. `SampleCosineHemisphere` draws directions with density $\cos\theta/\pi$, the shader reads the cube at the mip that density implies, and the result is the plain average of the samples. The cube holds the average, not the integral. A diffuse surface therefore multiplies it by its :term[albedo]{id=albedo} and nothing else, which is :term[Lambert diffuse]{id=lambert}.

```cpp src="Strata/shaders/IBL/Irradiance.comp.slang#L33-L42"
float3 sum = float3(0.0);
for (uint index = 0u; index < u_Parameters.SampleCount; index++)
{
	float3 direction = SampleCosineHemisphere(Hammersley(index, u_Parameters.SampleCount), normal);
	float pdf = max(dot(normal, direction), 1e-4) * INV_PI;
	float sampleSolidAngle = 1.0 / (float(u_Parameters.SampleCount) * pdf);
	float mip = clamp(0.5 * log2(sampleSolidAngle / texelSolidAngle) + 1.0, 0.0, maxMip);
	sum += u_Environment.SampleLevel(u_Sampler, direction, mip).rgb;
}
o_Output[int3(id)] = float4(sum / float(u_Parameters.SampleCount), 1.0);
```

1. **Lines 35–38:** a cosine-weighted direction, its density $\cos\theta/\pi$, and the solid angle each sample stands for.
2. **Lines 39–41:** the same mip rule as `Prefilter.comp`, and the plain sum.

### The frame's decisions

`UpdateEnvironment` runs once a frame before drawing, and the map branch holds the loading rules.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L1022-L1062"
Ref<Texture> texture = m_Assets.Resolve<Texture>(skyLight->EnvironmentMap, AssetPriority::High);
if (!texture || !texture->GetGPUTexture())
{
	// Constant ambient until the environment arrives (counted as pending by the resolve cache); the map is raised
	// whole as soon as it is loaded.
	HoldEnvironmentMap(skyLight->EnvironmentMap);
	return true;
}
// The environment is computed from the whole map: this renderer holds it whole in its streamer until then. Once
// computed, the cube is all renderers sample, so nothing asks for the map's levels any more and they drop to its
// tail; a renderer that starts lighting with the map afterwards takes over the environment another one computed.
const uint32_t prefilteredSize = m_Specification.Quality.EnvironmentResolution;
if (m_Environment && texture == m_Environment->Source && m_Environment->PrefilteredSize != prefilteredSize)
{
	// A new EnvironmentResolution: the maps of a renderer of that size, or the current ones with their prefiltered cube
	// filtered again at it from their radiance cube. Never computed again from the map, whose levels dropped to its
	// tail: the scene would lose its sky and image light until they streamed back in.
	if (Ref<const EnvironmentMaps> shared = FindSharedEnvironment(*texture, prefilteredSize))
		m_Environment = std::move(shared);
	else
		ResizePrefilteredMap(commandList);
}
else if (!m_Environment || texture != m_Environment->Source)
{
	if (Ref<const EnvironmentMaps> shared = FindSharedEnvironment(*texture, prefilteredSize))
	{
		m_Environment = std::move(shared);
	}
	else if (texture->GetResidentLevel() > 0)
	{
		HoldEnvironmentMap(skyLight->EnvironmentMap);
		m_Assets.CountPending(skyLight->EnvironmentMap);
		return true;
	}
	else
	{
		ProcessEnvironment(commandList, texture);
	}
}
m_EnvironmentHold = nullptr;
rotation = glm::radians(skyLight->Rotation);
```

1. **Line 1022:** the map is requested at high priority (`AssetPriority::High`).
2. **Lines 1023–1029:** while the map is not on the :term[GPU]{id=gpu}, the frame uses the constant ambient, and `HoldEnvironmentMap` keeps the map whole in the texture streamer so that it can load fully.
3. **Lines 1034–1043:** a new `EnvironmentResolution` takes the maps of a renderer of that size, or filters the prefiltered cube again from the radiance cube. It never reads the map again, whose levels are gone.
4. **Lines 1050–1054:** a map not yet whole counts as pending and keeps the ambient light.
5. **Lines 1058–1062:** the map is whole, so `ProcessEnvironment` makes the cube, the hold ends, and the map drops to its mip tail.

The hold is the same idea as the capture hold of a probe (see [the probes page](probes.md)). A source is read whole once, and the cube is all that renderers read after that. A renderer that starts to draw the sky later takes the maps another renderer made. That is `FindSharedEnvironment`, a registry of weak references keyed by the texture's address and the prefiltered size, so renderers of different `EnvironmentResolution` make their own maps.

Only maps of :term[environment map]{id=environment-map-equirectangular-hdr} textures are shared, since a procedural sky is each renderer's own. The registry holds no map alive; the maps live as long as a renderer lights with them.

### In the forward pass

The forward shader reads the two cubes once per pixel, and the horizon fade guards the specular read.

```cpp src="Strata/shaders/Scene/Forward.frag.slang#L218-L231"
if (inputs.Environment)
{
	inputs.SkyIrradiance = u_IrradianceMap.SampleLevel(u_LinearClampSampler, RotateEnvironmentDirection(surface.Normal), 0.0).rgb;
	inputs.SkyRadiance = u_PrefilteredMap.SampleLevel(u_LinearClampSampler, RotateEnvironmentDirection(inputs.Reflected),
		surface.Roughness * u_Frame.EnvironmentParams.z).rgb;
}
// Strata 0.7.0's branch order: probes first, then screen-space reflections, then the sky, else the constant ambient.
inputs.Form = inputs.Probes.Weight > 0.0 ? ST_INDIRECT_PROBES : inputs.ScreenReflection.a > 0.0 ? ST_INDIRECT_SCREEN
	: inputs.Environment ? ST_INDIRECT_SKY : ST_INDIRECT_AMBIENT;
// Specular occlusion from ambient occlusion (Lagarde): tighter for smooth surfaces and grazing views; reflections a normal
// map turns into the surface fade out (GetHorizonFade).
inputs.SpecularOcclusion = inputs.Form == ST_INDIRECT_AMBIENT ? 1.0
	: clamp(pow(NoV + diffuseOcclusion, exp2(-16.0 * surface.Roughness - 1.0)) - 1.0 + diffuseOcclusion, 0.0, 1.0)
	* GetFrameHorizonFade(inputs.Reflected, geometricNormal);
```

1. **Line 220:** the irradiance cube is read along the surface normal, rotated by the sky's rotation.
2. **Lines 221–222:** the prefiltered cube is read along $R$, at the mip `roughness * EnvironmentParams.z`; the sampler blends two levels.
3. **Lines 225–226:** with no probe, no screen-space hit and no environment, the form is the constant ambient, which lights diffuse only.
4. **Lines 229–231:** the specular occlusion also takes the horizon fade. `GetFrameHorizonFade` is `GetHorizonFade`, except in a capture that turns the fade off.

A :term[normal map]{id=normal-map} can tilt the shading normal so far that the reflected vector $R$ points under the geometric surface. The prefiltered cube would then show light from the other side of the surface. The **horizon fade** removes that light: a smooth ramp that takes the share of image light to zero as $R$ sinks below the geometric surface.

```cpp src="Strata/shaders/Include/PBR.slang#L95-L102"
static const float c_HorizonFadeWidth = 0.25;

// The share of image light a reflection along `reflected` keeps against the surface's `geometricNormal` (both unit).
float GetHorizonFade(float3 reflected, float3 geometricNormal)
{
	float fade = clamp(1.0 + dot(reflected, geometricNormal) / c_HorizonFadeWidth, 0.0, 1.0);
	return fade * fade;
}
```

With $g = R \cdot N_g$ (the reflected vector against the geometric normal), the share is $\operatorname{clamp}(1 + g/0.25, 0, 1)^2$. It is 1 for any $g \geq 0$, falls to 0 at $g = -0.25$, and the square makes the ramp gentle at the start. Since $\arcsin 0.25$ is 14.5 degrees, the fade reaches 0 about 15 degrees below the surface. This is the page that teaches it, and the shader applies it to the sky's specular light, through the occlusion above, and to the clear coat.

```mermaid caption="The share of image light against the reflected vector's height over the geometric surface: full above it, a squared ramp for a quarter of a unit below it, and none beyond." alt="A flow chart. If the reflected vector points above the geometric surface the light is kept whole. If it points below by less than a quarter of a unit the light fades along a squared ramp. Below that the light is gone."
flowchart LR
  A["R dot Ng >= 0"] --> B["Share 1"]
  C["-0.25 < R dot Ng < 0"] --> D["Share (1 + g / 0.25) squared"]
  E["R dot Ng <= -0.25"] --> F["Share 0"]
```

:::example[A normal map at a grazing view]
At a grazing view a strong normal map gives $R \cdot N_g = -0.1$. The ramp gives $1 + (-0.1/0.25) = 0.6$, and the square is 0.36: the surface keeps 36 % of the sky's specular light. At $-0.2$ the fade gives $0.2^2 = 0.04$. A smooth surface that the normal map leaves above the horizon keeps all of it.
:::

### The memory

`EnvironmentBytes` adds six faces of RGBA16F for each prefiltered level: the sum of $256^2$, $128^2$ and so on, times 6 faces and 8 :term[bytes]{id=byte}, about 4 MiB at 256 and about 16 MiB at 512. A scene under the atmosphere keeps a second set while the sun moves, which doubles it. The row has no stage of its own, as the map explained.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| :term[Spherical harmonics]{id=spherical-harmonics} (9 numbers) for the sky's diffuse light | Probes in Strata, many engines for the sky | Smaller memory and no cube read | A sky with sharp contrast rings (negative values) and blurs the sun's side |
| :term[Importance sampling]{id=importance-sampling} per pixel at run time | Film renderers | No prefiltered cube and no refresh | Hundreds of reads per pixel, every frame |
| Cubes baked in a tool before the game runs | Tools that bake cubes | No filter cost at run time | A new source (a time of day) needs a new bake |
| Octahedral environment maps | Probe systems, some engines | One 2D image, no seams | Mapping maths in every read and distortion near the folds |

## How it is tested

The suite `GPU.ProceduralSky` covers the procedural sky: its colours overhead and at the horizon, the sun's place, a white sphere that is brighter on top, and the test `The procedural cube is computed again only when the sky or the sun changes`. The suite `GPU.SceneRenderer.Lighting` holds the furnace tests of [the energy page](../light/energy.md), `Environment filtering conserves energy in every mip and face, and the BRDF lookup table is plausible`, `Rougher prefiltered levels blur the environment`, and the 512 tests `At 512 the prefiltered sky is 512 per face with six levels and a mirror shows finer detail` and `Renderers of different environment resolutions compute their own maps, and a new resolution recomputes them once`. The suite `GPU.TextureStreaming` checks the hold: `A sky light's environment map is read whole once and then keeps only its tail`. The suite `Renderer.Quality` checks the budget.

The GPU suites need a graphics device and carry the label `gpu`. CTest runs every GPU suite as one test: `ctest --preset windows-debug -R StrataTests.GPU`. For one suite, run `StrataTests.exe --test-suite=GPU.ProceduralSky` directly.

## Changing it safely

The first change is the `EnvironmentResolution` row. It holds 256 in the two lowest presets and 512 in the two highest, and a value other than 512 becomes 256. Its memory is the function `EnvironmentBytes`, and the row has no stage of its own because the chain runs only when the sky changes. The second is a new source. It must write mip 0 of a cube and then call the same chain, so that the irradiance and the levels stay one code path for every source.

:::rule[Never block a frame on an asset]
`AGENTS.md` forbids a frame to wait for an asset: a loading asset is skipped or replaced by a stand-in. The sky's map follows this with the constant ambient, a pending count and a hold. The reason is that a stall in the editor looks like a hang.
:::

Before a change to the chain, run the sky and furnace tests above, check the debug views of [the light measuring page](../light/measuring-light.md), and look at the sweeps above. Test the horizon fade with a capture whose renderer switch `HorizonFade` is false: it turns the fade off for that capture alone.

:::history
Image light from HDR maps and the procedural sky began in 0.3.0, and the atmosphere's cube in 0.6.0. Release 0.7.0 added 512 texel :term[prefiltering]{id=prefiltering} in the higher presets, the quality row for it, and the horizon fade, which Strata did not have before.
:::

## Summary

- One filter chain turns an HDR map, the procedural sky or the atmosphere into mip 0 of a 512 texel cube, then makes its levels, a 32 texel irradiance cube and six prefiltered levels.
- The split sum multiplies the prefiltered sky along $R$ by the :term[BRDF table]{id=brdf-table-lut}, under the assumption $N = V = R$; it fails at grazing angles, where reflections stretch.
- Filtered importance sampling reads the mip of $0.5 \log_2$ of the sample's solid angle over the texel's, plus one, so a few hundred samples give no noise.
- The horizon fade keeps $\operatorname{clamp}(1 + R \cdot N_g / 0.25, 0, 1)^2$ of image light, reaching 0 about 15 degrees below the surface.
- A sky change makes one new cube only when the sky's parameters change; its intensity, background and blur make none.

## Check yourself

1. At level 1 of a 512 texel prefiltered cube the shader uses 128 samples and reads mip 3.15. With 512 samples, which mip would it read? (a) 4.15 (b) 2.15 (c) 3.15 (d) 1.15

   :::answer{tests="compute-mip"}
   (b). Four times more samples make each sample stand for a quarter of the solid angle, and $0.5 \log_2(1/4) = -1$. (a) goes the wrong way, because more samples need finer mips. (c) ignores the count, and (d) takes the :term[logarithm]{id=logarithm} without the half.
   :::

2. A normal map gives $R \cdot N_g = -0.15$. What share of image light remains? (a) 0.4 (b) 0.16 (c) 0.6 (d) 0

   :::answer{tests="compute-horizon-fade"}
   (b). The ramp gives $1 + (-0.15/0.25) = 0.4$, and the square is 0.16. (a) forgets the square. (c) uses the wrong sign, and (d) holds only from $-0.25$ down.
   :::

3. Why does the split sum assume $N = V = R$? (a) so that a cube needs only a direction and a roughness (b) so that reflections are exact (c) so that the table is unnecessary (d) so that rough surfaces use fewer levels

   :::answer{tests="explain-split-sum"}
   (a). With the three equal, the first factor depends on two inputs, which a cube with levels stores. (b) is wrong: grazing reflections stretch, and the cube cannot show it. (c) is wrong: the table is the other factor. (d) mixes the number of levels with the assumption.
   :::

4. The map of a sky is loading, and the user changes `EnvironmentResolution` from 256 to 512 once it is on the GPU. Does the renderer compute the prefiltered cube again from the map? (a) yes, from mip 0 (b) no, from the radiance cube (c) no, it keeps 256 (d) it waits for a probe capture

   :::answer{tests="explain-chain"}
   (b). The map's levels dropped to its tail once the chain read it, so the renderer filters the prefiltered cube again from the radiance cube, or takes the maps of a renderer of that size. (a) would lose the sky until the levels streamed back. (c) ignores the row, and (d) confuses two features.
   :::

5. In a test, the sky's `Intensity` changes from 1 to 2. What does `EnvironmentUpdates` count in the next frame? (a) 1 (b) 0 (c) 14 (d) 8

   :::answer{tests="trace-sky-change"}
   (b). Intensity is applied in the shader, not part of the procedural parameters, so no cube is made. (a) is the count after a parameter such as the sun's size. (c) is the atmosphere's refresh and (d) the chain's step count.
   :::

## Exercises

1. **Basic.** Trace it yourself: find where a change of the sky light's `SunSize` becomes a new prefiltered cube.

   :::answer[Worked solution]{tests="trace-sky-change explain-chain"}
   Search for `GenerateProceduralSky` in `Strata/src/Strata/Renderer/SceneRenderer.cpp`. `SceneRenderer::UpdateEnvironment` builds `GetProceduralSkyParameters(*skyLight, frame)`, where `SunSize` becomes the sun direction's fourth component, and compares it with the parameters stored in the current maps. When they differ, `SceneRenderer::GenerateProceduralSky` runs `ProceduralSky.comp` into mip 0 and calls `FilterEnvironment`. The function adds one to `EnvironmentUpdates`. The test `The procedural cube is computed again only when the sky or the sun changes` checks the whole path.
   :::

2. **Medium.** The 512 texel cube's level 1 uses 128 samples at roughness 0.2 and reads mip 3.15. How many samples would level 3 (roughness 0.6) need to read the same mip?

   :::answer[Worked solution]{tests="compute-mip" solution="sketches/indirect-ibl-budget.cpp"}
   Level 1 stands for $1.571 \times 10^{-4}$ steradians a sample. At roughness 0.6, $\alpha = 0.36$ and the density at the centre is $D = 1/(\pi \alpha^2) = 2.456$, so the density of the reflected direction is $D/4 = 0.614$. The count is $1/(0.614 \times 1.571 \times 10^{-4})$, about 10,400 samples. The sketch computes it for every level, and the answer shows why the shader does not spend them: a lobe this wide reads coarse mips whatever the count.

   ```cpp sketch="indirect-ibl-budget.cpp"
   // How many samples make a level read the same source mip as level 1 does with its 128 samples?
   #include <cmath>
   #include <cstdio>

   constexpr float c_Pi = 3.14159265f;

   // The GGX density at the lobe's center, divided by 4 for the reflected direction (N = V).
   float CenterPdf(float roughness)
   {
   	float alpha = roughness * roughness;
   	return 1.0f / (c_Pi * alpha * alpha) * 0.25f;
   }

   int main()
   {
   	// Level 1 (roughness 0.2) with 128 samples: each sample stands for this solid angle.
   	const float target = 1.0f / (128.0f * CenterPdf(0.2f));
   	std::printf("target solid angle %.3e\n", target);
   	for (int level = 2; level < 6; level++)
   	{
   		float roughness = static_cast<float>(level) / 5.0f;
   		float samples = 1.0f / (CenterPdf(roughness) * target);
   		std::printf("level %d  roughness %.1f  needs %.0f samples\n", level, roughness, samples);
   	}
   	return 0;
   }
   ```

   ```text output-of="indirect-ibl-budget.cpp"
   target solid angle 1.571e-04
   level 2  roughness 0.4  needs 2048 samples
   level 3  roughness 0.6  needs 10368 samples
   level 4  roughness 0.8  needs 32768 samples
   level 5  roughness 1.0  needs 80000 samples
   ```

   1. **Line 11:** the density of the lobe's centre, divided by 4 as in the shader.
   2. **Line 17:** the solid angle that level 1 gives each sample.
   3. **Line 22:** the count at which another roughness gives each sample the same solid angle.
   :::

3. **Hard.** At which angle below the surface does the horizon fade keep half the light?

   :::answer[Worked solution]{tests="compute-horizon-fade"}
   Set $\operatorname{clamp}(1 + g/0.25)^2 = 0.5$, so $1 + g/0.25 = 0.7071$ and $g = -0.0732$. The angle below the surface is $\arcsin 0.0732$, about 4.2 degrees.
   :::

## Where it lives in Strata

- `Strata/shaders/Include/IBL.slang`: `CubeTexelDirection`, `DirectionToEquirect`, `Hammersley`, `ImportanceSampleGGX`, `SampleCosineHemisphere`.
- `Strata/shaders/IBL/`: `EquirectToCube`, `ProceduralSky`, `CubeDownsample`, `Irradiance` and `Prefilter`.
- `Strata/src/Strata/Renderer/SceneRenderer.cpp`: `UpdateEnvironment`, `FilterEnvironment`, `FilterEnvironmentStep`, `FindSharedEnvironment`, `HoldEnvironmentMap`.
- `Strata/src/Strata/Renderer/RendererQuality.cpp`: `GetPrefilterSamples`, `EnvironmentBytes`, the row `EnvironmentResolution`.
- `Strata/shaders/Include/PBR.slang`: `GetHorizonFade`.
- `StrataTests/src/Renderer/GPUProceduralSkyTests.cpp`: the suite `GPU.ProceduralSky`.

## Further reading

- Brian Karis, "Real Shading in Unreal Engine 4" (SIGGRAPH 2013 course notes): the split sum and its table; intermediate.
- Ravi Ramamoorthi and Pat Hanrahan, "An Efficient Representation for Irradiance Environment Maps" (SIGGRAPH 2001): nine coefficients for diffuse light; advanced.
- Mark Colbert and Jaroslav Krivanek, "GPU-Based Importance Sampling" (GPU Gems 3, chapter 20): filtered importance sampling; advanced.
