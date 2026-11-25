---
id: light/energy
title: "Keeping the energy: directional albedo, the BRDF table and the white furnace"
description: "Why a rough GGX metal loses light, how the BRDF table measures the loss, and how Strata puts the light back and checks it with a white furnace."
kind: internals
size: M
tracks: [E]
needs: [light/brdf, gpu/compute]
time: 60
learn:
  - id: derive-table
    text: compute a surface's directional albedo with importance sampling and read it as the BRDF table's scale plus bias
  - id: compensation
    text: explain why the factor 1 + F0 (1 / E - 1) restores the light that single scattering loses
  - id: furnace
    text: predict what a white furnace shows for a metal and use it to test a shading change
  - id: trace-readers
    text: trace the BRDF table from the place it is made once to the three places that read it
since: 0.7.0
status: final
---

Put a ball of polished white metal in a room whose every wall glows with the same white light. The ball can only reflect: it absorbs nothing. So it must look exactly as bright as the walls and vanish into them, however rough or smooth it is.

A :term[renderer]{id=renderer} that breaks this rule creates light or destroys it. This page covers the part of Strata that keeps the rule. It computes a table once and divides by what the table says a lobe loses. Then it checks the result with a test that renders such a room. It does not cover the prefiltered half of image light or the clear coat's own lobe.

## The problem and how engines solve it

A :term[microfacet]{id=microfacet} surface is a field of tiny mirrors. The specular term of the bidirectional :term[reflectance]{id=reflectance} distribution function (:term[BRDF]{id=brdf}) follows one ray: it comes from the light, hits one mirror and leaves toward the eye. Real rays do not stop there. On a rough surface the mirrors lean steeply, and a ray that leaves one mirror often hits a neighbor before it escapes. The model counts only the first bounce, so the light that bounces twice vanishes.

The loss grows with roughness. A program below measures it: a white metal seen head-on reflects 100 % of the light at roughness 0 and 31 % at roughness 1. The other 69 % is missing. Strata 0.6.0 showed exactly this, and a silver ball at roughness 1 reflected 0.31 of the sky around it.

Artists meet the loss as a symptom. A rough metal looks too dark, so they raise its :term[albedo]{id=albedo} above the measured value or brighten the light. The scene then looks right in one place and wrong under any other light. Fixing the shading model once is better than fixing every material.

The cure is **energy compensation**: a factor that multiplies the specular light and puts back what single scattering drops. Three published methods exist (the Further reading list names them). The first, from 2017, adds a second lobe whose size comes from two tables. It is accurate for any :term[F0]{id=f0} and costs two table reads and extra shading per light. The second, from 2019, derives a closed form for image light, and it needs the same table.

The third multiplies the single lobe by a factor, $1 + F_0 (1/E - 1)$. It needs only one table, and Strata already reads that table for image light: its split sum divides the light of the sky into a blurred sky picture and this table. Strata takes the third method, and the table of alternatives near the end of this page weighs the three.

## The map

Strata computes one small texture, the **BRDF table** (LUT), when the renderer creates its image-based lighting resources. For each pair of a view angle and a roughness, its two channels hold the numbers that integrate the specular lobe against a white environment. The forward :term[shader]{id=shader} reads the table once per pixel and passes what it learns to every light that reaches the pixel.

```mermaid caption="A compute shader makes the table once. The forward shader reads it at the surface, at the clear coat and in the glass code, and the compensation multiplies direct light, image light, the coat and the glass reflection." alt="A compute shader makes the table once at renderer creation. Three readers take it in the forward shader: the surface setup, the clear coat setup and the glass code. All three feed the compensation factor, which multiplies direct light, image light, and the coat and glass reflectance."
flowchart LR
    C["BRDFLut.comp: once"] --> T["BRDF table t5, 128 x 128"]
    T --> S["Surface setup in ShadeLitSurface"]
    T --> K["Coat setup in ShadeLitSurface"]
    T --> G["TransmitLight: glass"]
    S --> F["GetSpecularEnergy"]
    K --> F
    G --> F
    F --> D["Direct light: EvaluateLightWeighted"]
    F --> I["Image light: SpecularColor"]
    F --> R["Coat and glass reflectance"]
```

The table does not depend on the scene, the light or the material, only on the shading model. That is why Strata makes it once and never changes it. The prefiltered environment, the other half of the split sum, changes with the sky and has its own page.

## Directional albedo and the BRDF table

Start with the question the white room asks. Light arrives from every direction, each ray with its own :term[cosine]{id=cosine} weight. How much of it does the lobe send out in total? The answer for one view direction is the **directional albedo** (E): the share of the light that a lobe reflects when you look at the surface from that direction. It lies between 0 (the lobe reflects nothing) and 1 (it reflects everything), and it depends on the angle to the normal and on roughness.

Two cases give a feel for it. A mirror-like lobe at roughness 0, seen head-on, sends every ray of the white room to the eye, so E is 1. At roughness 1 the toy below finds E = 0.31. Three tenths of the light leave by the first bounce, and seven tenths scatter again among the mirrors.

Compute E for a lobe whose :term[Fresnel]{id=fresnel} term is 1 everywhere, that is, F0 = 1. The integral is a sum over the hemisphere of the BRDF times the cosine of the light's angle:

$$E(n \cdot v) = \int_{\Omega} f_s(v, l)\,(n \cdot l)\,d\omega_l$$

$E$ is the directional albedo, $n \cdot v$ the cosine of the angle between the normal and the view, and $f_s$ the BRDF with its Fresnel term set to 1. $l$ is the direction to a light, $\Omega$ the hemisphere above the surface and $\omega_l$ the :term[solid angle]{id=solid-angle} of a light direction, with $d$ marking a tiny slice of it. The sign $\int$ reads "the sum of tiny slices".

No closed form exists, so a program estimates the integral by Monte Carlo: draw $N$ random directions, evaluate the quantity under the sum at each and average. Uniform directions waste most draws, because a narrow lobe is zero for nearly all of them. :term[Importance sampling]{id=importance-sampling} draws directions where the lobe is large and divides each result by the density of the draw. For the :term[Trowbridge-Reitz]{id=ggx} distribution (GGX) the draw is the half vector $h$, the direction between view and light. Its density follows the distribution $D$:

$$p(l) = \frac{D(h)\,(n \cdot h)}{4\,(v \cdot h)}$$

$p$ is the density of the light direction per unit of solid angle, and $h$ is the half vector. $n \cdot h$ and $v \cdot h$ are the cosines of its angles to the normal and the view. The factor 4 turns a density over half vectors into one over light directions. The specular BRDF is $D V$ times the Fresnel term 1, where $V$ is the :term[Smith visibility]{id=smith-visibility-height-correlated} from the page on the BRDF in code. Dividing by $p$ gives one sample's value:

$$\frac{f_s\,(n \cdot l)}{p(l)} = 4\,V\,(n \cdot l)\,\frac{v \cdot h}{n \cdot h}$$

Read the right side: $D$ is gone. It sits in both $f_s$ and $p$ and cancels. The sample no longer depends on the sharp peak of GGX, which is why 512 samples converge. Averaging this value over the draws gives E.

The table splits E in two so that one fetch serves every F0. Schlick's Fresnel is $F = F_0 + (1 - F_0)(1 - v \cdot h)^5$, and it is linear in F0. Write $w$ for the sample value above and $q = (1 - v \cdot h)^5$. Then $F\,w = F_0 (1 - q)\,w + q\,w$.

The average of $(1 - q)\,w$ is the table's scale, and the average of $q\,w$ is its bias. Reflectance equals $F_0 \times \text{scale} + \text{bias}$. With $F_0 = 1$ the two add up to E. One table therefore holds both the reflectance of image light and the number the compensation needs. The table costs 128 by 128 texels of two 16-bit numbers, a 64 KB texture, and one fetch in the shader.

:::example[The silver ball by hand]
Silver has F0 = 0.95. Head-on at roughness 1 the table holds scale 0.3078 and a bias near 0. Single scattering reflects $0.95 \times 0.3078 + 0 = 0.292$ of the light. A mirror of this albedo would reflect 0.95, so the ball looks three times too dark.
:::

## The contract

The table and the factor follow rules that every shading change must respect. Each has a reason.

- The table holds the single-scattering lobe's integral with the same Smith visibility as direct light. Reason: the factor divides by E, so E must be that lobe's own albedo.
- The shader builds the factor with `GetSpecularEnergy` from one table fetch at the surface's view cosine and roughness. Reason: one function holds the formula, so no reader drifts apart from the others.
- The factor multiplies the specular light of every source, direct and image alike. Reason: a lamp and the sky meet the same mirrors, so both lose the same share.
- Diffuse keeps the share that specular leaves. Direct light keeps $1 - F$ and image light keeps $1 - \text{SpecularColor}$. Reason: the compensation adds under 0.5 % to a non-metal's reflection, less than the error of the diffuse model.
- Strata tests a shading change with the white furnace and the debug views, never by eye. Reason: eyes adapt to brightness, but a furnace reads an exact number.

:::rule[Light keeps its energy]
`AGENTS.md` says that light keeps its energy: the specular lobe is compensated for multiple scattering, and lighting changes are checked with the white furnace. The reason is above: only a number catches a loss. The lobe itself is in [the BRDF in code](../light/brdf.md).
:::

The factor is exact only for a white metal. A colored metal absorbs light on every bounce, so the second bounce brings back less, and the steps below show how much.

:::derivation
Where the factor $1 + F_0 (1/E - 1)$ comes from.

The first bounce reflects $F_0 E$: the share $E$ that the lobe reflects, times the $F_0$ the mirror keeps. The share $1 - E$ hits a second mirror, which keeps $F_0$ again, so $F_0^2 (1 - E)$ leaves after two bounces. Ignore the third and further bounces. The sum is $F_0 E + F_0^2 (1 - E)$, which equals $F_0 E\,(1 + F_0 (1/E - 1))$. The first part is what single scattering gives, and the bracket is the factor.
:::

## A toy version

The toy computes E for nine points of the table on the :term[central processing unit]{id=processor} (CPU). Its draws come from the Hammersley pattern, an even spread of points that replaces random draws. Then it mirrors the steps above: a GGX half vector, the light as the view mirrored about it, and the sample value with $D$ cancelled. Find the single division by `halfZ` at the end of the loop: that is the cosine $n \cdot h$ of the formula.

```cpp sketch="light-energy-toy.cpp"
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>

namespace
{

	constexpr double c_Pi = 3.14159265358979;

	// The second coordinate of the Hammersley pattern: the bits of the index mirrored behind the binary point.
	double RadicalInverse(uint32_t index)
	{
		double result = 0.0;
		double digit = 0.5;
		for (uint32_t bits = index; bits != 0; bits >>= 1)
		{
			if (bits & 1u)
				result += digit;
			digit *= 0.5;
		}
		return result;
	}

	// Height-correlated Smith visibility, the same formula the forward shader uses.
	double Visibility(double nov, double nol, double alpha)
	{
		const double alpha2 = alpha * alpha;
		const double lambdaV = nol * std::sqrt((nov - nov * alpha2) * nov + alpha2);
		const double lambdaL = nov * std::sqrt((nol - nol * alpha2) * nol + alpha2);
		return 0.5 / std::max(lambdaV + lambdaL, 1e-5);
	}

	// The share of the light that a GGX lobe of F0 = 1 reflects for one view direction: its directional albedo E.
	double DirectionalAlbedo(double nov, double roughness, uint32_t sampleCount)
	{
		const double alpha = roughness * roughness;
		const double viewX = std::sqrt(1.0 - nov * nov); // The view lies in the x-z plane, the normal is z.
		double sum = 0.0;
		for (uint32_t index = 0; index < sampleCount; index++)
		{
			const double phi = 2.0 * c_Pi * (static_cast<double>(index) / sampleCount);
			const double v = RadicalInverse(index);
			const double halfZ = std::sqrt((1.0 - v) / (1.0 + (alpha * alpha - 1.0) * v));
			const double halfX = std::sqrt(1.0 - halfZ * halfZ) * std::cos(phi);
			const double voh = viewX * halfX + nov * halfZ;
			const double nol = 2.0 * voh * halfZ - nov; // The light is the view mirrored about the half vector.
			if (nol <= 0.0 || voh <= 0.0)
				continue;
			// BRDF * NoL / pdf, where pdf = D * NoH / (4 VoH): the distribution D cancels.
			sum += Visibility(nov, nol, alpha) * 4.0 * nol * voh / std::max(halfZ, 1e-4);
		}
		return sum / sampleCount;
	}

}

int main()
{
	for (const double nov : { 1.0, 0.5, 0.1 })
		for (const double roughness : { 0.1, 0.5, 1.0 })
		{
			const double albedo = DirectionalAlbedo(nov, roughness, 512);
			std::printf("NoV %.1f  roughness %.1f  E %.4f  1/E %.3f\n", nov, roughness, albedo, 1.0 / albedo);
		}
	return 0;
}
```

```text output-of="light-energy-toy.cpp"
NoV 1.0  roughness 0.1  E 1.0000  1/E 1.000
NoV 1.0  roughness 0.5  E 0.9168  1/E 1.091
NoV 1.0  roughness 1.0  E 0.3078  1/E 3.249
NoV 0.5  roughness 0.1  E 1.0001  1/E 1.000
NoV 0.5  roughness 0.5  E 0.8574  1/E 1.166
NoV 0.5  roughness 1.0  E 0.4503  1/E 2.221
NoV 0.1  roughness 0.1  E 0.9932  1/E 1.007
NoV 0.1  roughness 0.5  E 0.9013  1/E 1.110
NoV 0.1  roughness 1.0  E 0.7498  1/E 1.334
```

1. **Line 35:** the function takes the view cosine and roughness, the two axes of the table.
2. **Lines 42–44:** the sampled half vector; its height `halfZ` is the cosine of its angle to the normal.
3. **Line 51:** the whole sample value, with no `D` anywhere.

Read the output down the roughness column. At roughness 0.1, E stays near 1 for every angle. At roughness 1 it falls to 0.31 head-on, 0.45 at 60° (`NoV` 0.5) and 0.75 near grazing (`NoV` 0.1), so the loss is largest when you look straight at a rough surface. The factor $1/E$ is the number the compensation will use, between 1 and 3.25 here. The toy draws 512 samples, as Strata does.

## The real code

The shader `Strata/shaders/IBL/BRDFLut.comp.slang` runs the same loop, with one thread for each texel and with Fresnel split into scale and bias. Find the lines that turn a texel's position into `NoV` and roughness, and the comment about the density.

```slang src="Strata/shaders/IBL/BRDFLut.comp.slang#L20-L49"
void st_Main()
{
	uint2 id = st_GlobalInvocationID.xy;
	if (id.x >= u_Parameters.OutputSize || id.y >= u_Parameters.OutputSize)
		return;

	float NoV = (float(id.x) + 0.5) / float(u_Parameters.OutputSize);
	float roughness = (float(id.y) + 0.5) / float(u_Parameters.OutputSize);
	float alpha = roughness * roughness;
	float3 view = float3(sqrt(1.0 - NoV * NoV), 0.0, NoV);
	float3 normal = float3(0.0, 0.0, 1.0);

	float2 sum = float2(0.0);
	for (uint index = 0u; index < u_Parameters.SampleCount; index++)
	{
		float3 halfVector = ImportanceSampleGGX(Hammersley(index, u_Parameters.SampleCount), normal, alpha);
		float3 light = reflect(-view, halfVector);
		float NoL = clamp(light.z, 0.0, 1.0);
		float NoH = clamp(halfVector.z, 0.0, 1.0);
		float VoH = clamp(dot(view, halfVector), 0.0, 1.0);
		if (NoL <= 0.0)
			continue;

		// pdf = D * NoH / (4 VoH); BRDF * NoL / pdf = 4 * V * NoL * VoH / NoH (D cancels).
		float visibility = VisibilitySmithGGXCorrelated(NoV, NoL, alpha) * 4.0 * NoL * VoH / max(NoH, 1e-4);
		float fresnel = pow(1.0 - VoH, 5.0);
		sum += float2(1.0 - fresnel, fresnel) * visibility;
	}
	o_Output[int2(id)] = float4(sum / float(u_Parameters.SampleCount), 0.0, 0.0);
}
```

1. **Lines 26–27:** texel centers give `NoV` and roughness, so the table has no value at exactly 0 or 1; the sampler's clamp covers the edges.
2. **Line 35:** `ImportanceSampleGGX` and `Hammersley` are the engine's own, and `alpha` is the squared roughness.
3. **Lines 43–44:** the density comment and the sample value, the same as the toy's.
4. **Lines 45–46:** the sample goes into the two channels: scale gets $1 - F$ and bias gets $F$ of the Fresnel factor.

`SceneRenderer::CreateIBLResources` makes the texture and dispatches the shader once. The size is 128 by 128 and the sample count is 512, both constants in `Strata/src/Strata/Renderer/SceneRenderer.cpp`. The texture format is `RG16_FLOAT`, so scale is red and bias is green. The forward pass binds it at `t5` as `u_BRDFLut`, in `Strata/shaders/Include/Scene.slang`.

The factor is built in `Strata/shaders/Include/PBR.slang`.

```slang src="Strata/shaders/Include/PBR.slang#L59-L71"
// The smallest directional albedo the compensation divides by. The BRDF table's x + y stays above 0.2 for every NoV and
// roughness it holds; this only keeps a broken table finite.
static const float c_MinSpecularAlbedo = 0.05;

// Multiple-scattering compensation of the specular lobe: the factor its light is multiplied by. `dfg` is the BRDF table
// (IBL/BRDFLut.comp) at the surface's NoV and roughness: its x + y is the single-scattering lobe's directional albedo E for
// F0 = 1, which reflects only E of the light; the rest scatters again between the microfacets and leaves after further
// bounces, each of which keeps F0 of it. 1 + F0 (1 / E - 1) restores that light: exact for F0 = 1 (the lobe then reflects
// everything), less for colored metals, whose further bounces absorb 1 - F0 each.
float3 GetSpecularEnergy(float3 f0, float2 dfg)
{
	return 1.0 + f0 * (1.0 / max(dfg.x + dfg.y, c_MinSpecularAlbedo) - 1.0);
}
```

1. **Line 61:** the floor of E, 0.05, so that a broken table cannot divide by zero; the comment says the real sum stays above 0.2.
2. **Lines 68–70:** the whole compensation: E is `dfg.x + dfg.y` and the factor is $1 + F_0 (1/E - 1)$.

The surface setup reads the table once per pixel and stores the factor.

```slang src="Strata/shaders/Scene/Forward.frag.slang#L281-L296"
// The split sum's BRDF table at the surface: its specular reflectance of image light and the compensation of its lobe for
// multiple scattering, which direct light takes too.
float NoV = max(dot(surface.Normal, surface.View), 1e-4);
// A dielectric reflects head-on what its IOR gives (MaterialGPU::GetDielectricF0: 0.04 at 1.5), a metal its albedo.
float3 f0 = lerp(float3(material.Absorption.w), surface.Albedo, surface.Metallic);
surface.F0 = f0;
float2 dfg = u_BRDFLut.SampleLevel(u_LinearClampSampler, float2(NoV, surface.Roughness), 0.0).rg;
surface.SpecularEnergy = GetFrameSpecularEnergy(f0, dfg);
float coatNoV = 1.0;
float2 coatDFG = float2(1.0, 0.0);
if (coat.Strength > 0.0)
{
	coatNoV = max(dot(coat.Normal, surface.View), 1e-4);
	coatDFG = u_BRDFLut.SampleLevel(u_LinearClampSampler, float2(coatNoV, coat.Roughness), 0.0).rg;
	coat.SpecularEnergy = GetFrameSpecularEnergy(float3(c_ClearcoatF0), coatDFG).x;
}
```

1. **Lines 287–288:** one fetch at (`NoV`, roughness) and the factor of the surface.
2. **Lines 291–295:** the clear coat fetches with its own normal and roughness; its F0 is the constant `c_ClearcoatF0`, 0.04.

`GetFrameSpecularEnergy` returns what `GetSpecularEnergy` gives in every frame but one kind. When the editor takes a picture with the compensation switched off, to show what it does, the factor is 1.

Now follow the factor through the readers. `EvaluateLightWeighted` multiplies each lamp's specular term by `surface.SpecularEnergy`. The image light's `SpecularColor` is `(f0 * dfg.x + dfg.y) * surface.SpecularEnergy`, the split sum's reflectance, compensated. `TransmitLight`, the glass code, fetches the table again so that what passes through is what the surface does not reflect.

## The white furnace

A **white furnace test** renders an object inside a uniform sky of one unit of light and nothing else. An object that keeps its energy and absorbs nothing shows 1 everywhere. Any other value is a bug or a deliberate loss. The test reads linear values straight from the frame with tone mapping off, because a tone curve would make 0.95 and 0.98 look alike.

Strata has two furnaces. The tests render a sphere under a sky of 1 and read the center and the rim of its picture. The look-dev shot `lookdev.furnace` shows a row of metal spheres of F0 0.95 and a row of gray non-metals at roughness 0, 0.25, 0.5, 0.75 and 1. Its sky is a gray of 0.5 in every direction, with tone mapping set to `None`. There the decoded values at the sphere centers are linear, so a sphere that keeps its light reads half its reflectance.

::compare{id=furnace-pair}

The metal row, enlarged, shows where the two pictures differ: the rough spheres at the right darken without the compensation and match the room with it.

::figure{id=furnace-pair variant=off crop=metals}

::figure{id=furnace-pair variant=on crop=metals}

The test's body shows the rule as numbers.

```cpp src="StrataTests/src/Renderer/GPUSceneLightingTests.cpp#L860-L914"
TEST_CASE("A white furnace keeps a rough metal's light at every roughness")
{
	// Multiple-scattering compensation (PBR.slang's GetSpecularEnergy): a white metal (F0 = 1) reflects all the light it
	// receives at every roughness; 0.6.0's single-scattering lobe kept 0.31 of it for silver at roughness 1.
	GPUContext gpu;
	REQUIRE(gpu.IsValid());
	SceneTestAssets assets;
	const AssetHandle sky = assets.Add(CreateEnvironmentTexture(glm::vec3(1.0f), glm::vec3(1.0f)), "Furnace");
	for (const float roughness : { 0.0f, 0.25f, 0.5f, 0.75f, 1.0f })
	{
		CAPTURE(roughness);
		const FurnaceReading white = RenderFurnace(assets, sky, FurnaceMetal(glm::vec3(1.0f), roughness));
		for (const glm::vec3& value : { white.Center, white.Rim })
		{
			CHECK(value.r >= 0.97f);
			CHECK(value.r <= 1.03f);
			CHECK(value.g >= 0.97f);
			CHECK(value.g <= 1.03f);
		}
	}

	// The look-dev furnace's silver (0.95) keeps at least 0.9 of its F0 at roughness 1.
	const FurnaceReading silver = RenderFurnace(assets, sky, FurnaceMetal(glm::vec3(0.95f), 1.0f));
	CHECK(silver.Center.g >= 0.9f * 0.95f);
	CHECK(silver.Rim.g >= 0.9f * 0.95f);

	// A colored metal keeps less: each further bounce absorbs 1 - F0 of the light. Copper's channels follow the formula
	// with the table read back at the pixel (NoV 1, roughness 1).
	SceneRendererSpecification specification;
	specification.TextureStreaming = false;
	SceneRenderer copperRenderer(specification);
	const glm::vec3 copper(0.95f, 0.64f, 0.54f);
	const FurnaceReading reading = RenderFurnace(assets, sky, FurnaceMetal(copper, 1.0f), &copperRenderer);
	const glm::vec2 dfg = ReadRoughBRDF(copperRenderer);
	const float albedo = dfg.x + dfg.y;
	CAPTURE(albedo);
	for (int channel = 0; channel < 3; channel++)
	{
		CAPTURE(channel);
		const float f0 = copper[channel];
		const float expected = (f0 * dfg.x + dfg.y) * (1.0f + f0 * (1.0f / albedo - 1.0f));
		CHECK(reading.Center[channel] == doctest::Approx(expected).epsilon(0.03));
	}

	// A white dielectric: diffuse gets what specular leaves.
	MaterialProperties dielectric;
	dielectric.BaseColor = glm::vec4(1.0f);
	dielectric.Roughness = 1.0f;
	const FurnaceReading plastic = RenderFurnace(assets, sky, dielectric);
	for (const glm::vec3& value : { plastic.Center, plastic.Rim })
	{
		CHECK(value.g >= 0.97f);
		CHECK(value.g <= 1.03f);
	}
	CHECK(gpu.GetNewErrorCount() == 0);
```

1. **Lines 868–878:** a white metal returns between 0.97 and 1.03 at every roughness, at the center and the rim.
2. **Lines 893–900:** copper's :term[expected value]{id=expected-value} comes from the formula applied to the table's own values read back from the texture, so shader, table and formula must agree.
3. **Lines 908–912:** a white non-metal also keeps the light, because diffuse takes what specular leaves.

Copper keeps less than 1 because its bounces absorb light: 0.48 in the green channel against 0.917 for silver. Other cases cover a non-metal at every index of refraction (:term[IOR]{id=ior}), a sized sun, and a clear coat over a white metal, which must also return 1 because both lobes are compensated.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Second lobe from two tables (2017) | Renderers cited in Further reading | Exact energy for colored metals | A second table, extra shading per light |
| Closed form for image light (2019) | Real-time engines cited in Further reading | Colored metals correct | Direct lamps need another formula |
| Factor from one table (Strata's choice) | Engines that follow the third entry of Further reading | One table, one multiply for every light | Colored metals keep a little less light |
| No compensation | Early physically based engines | No cost | Dull rough metals |
| Brighter albedo by hand | Artists in any engine | Looks right in one scene | Wrong under every other light |

## How it is tested

The suite `GPU.SceneRenderer.Lighting` holds the furnace cases. It renders on the shared device of the :term[graphics processing unit]{id=gpu} (GPU) tests, so ctest runs it inside the test `StrataTests.GPU`, which carries the label `gpu`. Each ends by checking that the run logged no new error.

- `A white furnace keeps a rough metal's light at every roughness`: white metal, silver, copper by formula and a white non-metal.
- `The furnace keeps a dielectric's light at every IOR, and its reflectance is the IOR's`: one case per IOR.
- `A clear coat over a white metal keeps the furnace's light`: the coat over a white metal.

Run only this suite with `StrataTests.exe --test-suite=GPU.SceneRenderer.Lighting`, from `build/windows/bin/Debug/`. The command `ctest --preset windows-debug -R StrataTests.GPU` runs every GPU suite, these among them, and `-LE gpu` excludes them all.

## Changing it safely

The shading model of the table lives in `BRDFLut.comp.slang`, and the factor in `GetSpecularEnergy`. The rules above apply with their reasons, and three more follow from them.

- Change the Smith visibility in direct light and in the table together. Reason: the factor divides by the table's E, so it must match the lobe the shader draws.
- Apply the factor to every specular term you add. Reason: a new light that skips it breaks the furnace for rough metals.
- Run the furnace cases and the look-dev furnace before you commit. Reason: a loss of a few percent is invisible by eye and plain in the number.

## What went wrong before

Strata 0.6.0 kept 0.31 of the sky for silver at roughness 1. The test `A white furnace keeps a rough metal's light at every roughness` is the regression test, and its comment names the old value. A second defect, a non-metal that reflected 0.04 at every IOR, has its own furnace case.

## Summary

- The table integrates the single-scattering lobe once by importance sampling with the Hammersley pattern; the density cancels D, and scale plus bias is the directional albedo E.
- The factor $1 + F_0 (1/E - 1)$ restores the light that single scattering loses; it is exact for F0 = 1, and it multiplies direct light, image light, the coat and glass.
- A white furnace shows 1 for a lobe that keeps its energy; use it, with the debug views, to test every shading change.
- The table is made once in `CreateIBLResources`, and `ShadeLitSurface` (surface and coat) and `TransmitLight` read it.

## Check yourself

1. A white metal sits in a white furnace. At which roughness does Strata show 1 at the sphere's center? (a) only at roughness 0 (b) only at roughness 1 (c) at every roughness (d) at none

   :::answer{tests="furnace compensation"}
   (c). The compensation puts back the share that single scattering loses, so the metal returns the whole sky at every roughness. (a) describes the lobe without compensation, where only the mirror keeps all the light. (b) reverses the loss, and (d) denies the test's checks.
   :::

2. At roughness 1 and `NoV` 1, E is 0.3078. What factor multiplies the specular light of a metal with F0 = 1? (a) 0.3078 (b) 1 (c) 3.249 (d) 0.6922

   :::answer{tests="compensation"}
   (c). The factor is $1 + 1 \times (1/0.3078 - 1)$, which is $1/E$ = 3.249. (a) is E itself, (b) is the factor at roughness 0, and (d) is the lost share, not its inverse.
   :::

3. What happens to $D$ in the sample value $4\,V\,(n \cdot l)\,(v \cdot h)/(n \cdot h)$? (a) it multiplies the value (b) it divides it (c) it cancels (d) it sets the sample count

   :::answer{tests="derive-table"}
   (c). $D$ stands in the BRDF and in the density, so it cancels. (a) and (b) keep it in only one place, and (d) confuses the density with the 512 samples.
   :::

4. A copper channel has F0 = 0.64. With E = 0.3078, what does $F_0 E + F_0^2 (1 - E)$ give?

   :::answer{tests="compensation furnace"}
   $0.64 \times 0.3078 + 0.4096 \times 0.6922 = 0.197 + 0.284 = 0.481$. Copper's green keeps less than half of the sky, because each bounce absorbs 36 % of what reaches it.
   :::

5. Name the three places that read the BRDF table in the forward shader.

   :::answer{tests="trace-readers"}
   The surface setup in `ShadeLitSurface`, the clear coat's setup in the same function, and `TransmitLight`, the glass code. All three read `u_BRDFLut` and call `GetSpecularEnergy`, through `GetFrameSpecularEnergy`, on what they read.
   :::

## Exercises

1. **Basic.** Predict the compensated reflectance of the look-dev silver (F0 = 0.95) at roughness 1, head-on, from E = 0.3078 and a bias of 0. Compare it with the test's bound, 0.9 times F0.

   :::answer[Worked solution]{tests="compensation furnace"}
   The factor is $1 + 0.95 \times (1/0.3078 - 1) = 3.136$. Single scattering gives $0.95 \times 0.3078 = 0.292$, and the product is 0.917. The bound is $0.9 \times 0.95 = 0.855$, so 0.917 passes.
   :::

2. **Medium.** Turn the compensation off in a sketch and measure the loss of silver per roughness at `NoV` 1.

   :::answer[Worked solution]{tests="derive-table furnace" solution="sketches/light-energy-loss.cpp"}
   The sketch integrates scale and bias, then prints the single-scattering value and the compensated one per roughness.

   ```cpp sketch="light-energy-loss.cpp"
   #include <algorithm>
   #include <cmath>
   #include <cstdint>
   #include <cstdio>

   namespace
   {

   	constexpr double c_Pi = 3.14159265358979;

   	// The table's two numbers: the scale and the bias of F0 for one view direction and roughness.
   	struct Reflectance
   	{
   		double Scale;
   		double Bias;
   	};

   	Reflectance IntegrateLobe(double nov, double roughness, uint32_t sampleCount)
   	{
   		const double alpha = roughness * roughness;
   		const double viewX = std::sqrt(1.0 - nov * nov);
   		double scale = 0.0;
   		double bias = 0.0;
   		for (uint32_t index = 0; index < sampleCount; index++)
   		{
   			double v = 0.0;
   			double digit = 0.5;
   			for (uint32_t bits = index; bits != 0; bits >>= 1, digit *= 0.5)
   				v += (bits & 1u) ? digit : 0.0;
   			const double phi = 2.0 * c_Pi * (static_cast<double>(index) / sampleCount);
   			const double halfZ = std::sqrt((1.0 - v) / (1.0 + (alpha * alpha - 1.0) * v));
   			const double voh = viewX * std::sqrt(1.0 - halfZ * halfZ) * std::cos(phi) + nov * halfZ;
   			const double nol = 2.0 * voh * halfZ - nov;
   			if (nol <= 0.0 || voh <= 0.0)
   				continue;
   			const double alpha2 = alpha * alpha;
   			const double lambdaV = nol * std::sqrt((nov - nov * alpha2) * nov + alpha2);
   			const double lambdaL = nov * std::sqrt((nol - nol * alpha2) * nol + alpha2);
   			const double weight = 0.5 / std::max(lambdaV + lambdaL, 1e-5) * 4.0 * nol * voh / std::max(halfZ, 1e-4);
   			const double fresnel = std::pow(1.0 - voh, 5.0);
   			scale += (1.0 - fresnel) * weight;
   			bias += fresnel * weight;
   		}
   		return { scale / sampleCount, bias / sampleCount };
   	}

   }

   int main()
   {
   	const double f0 = 0.95; // The look-dev furnace's silver.
   	for (const double roughness : { 0.0, 0.25, 0.5, 0.75, 1.0 })
   	{
   		const Reflectance table = IntegrateLobe(1.0, roughness, 512);
   		const double albedo = table.Scale + table.Bias;
   		const double single = f0 * table.Scale + table.Bias;
   		const double factor = 1.0 + f0 * (1.0 / albedo - 1.0);
   		std::printf("roughness %.2f  E %.4f  silver alone %.4f  factor %.3f  compensated %.4f\n", roughness, albedo, single, factor, single * factor);
   	}
   	return 0;
   }
   ```

   ```text output-of="light-energy-loss.cpp"
   roughness 0.00  E 1.0000  silver alone 0.9500  factor 1.000  compensated 0.9500
   roughness 0.25  E 0.9961  silver alone 0.9463  factor 1.004  compensated 0.9498
   roughness 0.50  E 0.9168  silver alone 0.8709  factor 1.086  compensated 0.9460
   roughness 0.75  E 0.6279  silver alone 0.5965  factor 1.563  compensated 0.9323
   roughness 1.00  E 0.3078  silver alone 0.2924  factor 3.136  compensated 0.9171
   ```

   1. **Lines 41–42:** the two channels of the table, summed over the draws.
   2. **Lines 56–58:** single scattering is `f0 * scale + bias`; the compensated value multiplies it by the factor.

   Without the factor, silver keeps 0.95 at roughness 0 and 0.292 at roughness 1, a loss of 69 %. With it, the value stays between 0.917 and 0.95.
   :::

3. **Hard.** Trace it yourself. Find with a search where the table is made once (its size, its samples and the dispatch of `BRDFLut.comp`) and every reader of `GetSpecularEnergy`.

   :::answer[Worked solution]{tests="trace-readers"}
   Search `Strata/src` for `BRDFLut`. In `Strata/src/Strata/Renderer/SceneRenderer.cpp` the function `SceneRenderer::CreateIBLResources` holds the constants (size 128, 512 samples), creates the texture and calls `DispatchIBL`. Search `Strata/shaders` for `GetFrameSpecularEnergy`, the frame's form of `GetSpecularEnergy`: the readers are `ShadeLitSurface` (the surface and the coat) and `TransmitLight` in `Strata/shaders/Scene/Forward.frag.slang`.
   :::

## Where it lives in Strata

- `Strata/shaders/IBL/BRDFLut.comp.slang`: the compute shader that fills the BRDF table.
- `Strata/shaders/Include/PBR.slang`: `GetSpecularEnergy`, `c_MinSpecularAlbedo`, and the `SpecularEnergy` fields of `SurfaceData` and `ClearcoatData`.
- `Strata/shaders/Scene/Forward.frag.slang`: `ShadeLitSurface`, `GetIndirectInputs` and `TransmitLight`.
- `Strata/src/Strata/Renderer/SceneRenderer.cpp`: `SceneRenderer::CreateIBLResources` and `SceneRenderer::DispatchIBL`.
- `StrataTests/src/Renderer/GPUSceneLightingTests.cpp`: the furnace cases of `GPU.SceneRenderer.Lighting`.
- `Tools/LookDev/Shots.json`: the shot `lookdev.furnace`.

## Further reading

- Christopher Kulla and Alejandro Conty, "Revisiting Physically Based Shading at Imageworks" (SIGGRAPH 2017 course notes): the second-lobe compensation; advanced.
- Carmelo J. Fdez-Aguera, "A Multiple-Scattering Microfacet Model for Real-Time Image-based Lighting" (Journal of Computer Graphics Techniques, 2019): a closed form for image light; advanced.
- Google, "Filament: Physically Based Rendering" documentation, section "Energy loss in specular reflectance": the factor Strata uses; intermediate.
- Brian Karis, "Real Shading in Unreal Engine 4" (SIGGRAPH 2013 course notes): the split sum and its table; intermediate.
- Eric Heitz, "Understanding the Masking-Shadowing Function in Microfacet-Based BRDFs" (2014): the Smith term the table shares with direct light; advanced.
