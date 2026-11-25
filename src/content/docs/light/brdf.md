---
id: light/brdf
title: "The forward shader and the BRDF in code"
description: "How Strata's forward shader colors each pixel: the direct-light BRDF, specular anti-aliasing, the six variants and the rules that keep both draw paths equal."
kind: internals
size: L
tracks: [E]
needs: [light/reflectance, light/material-data, basics/signals]
time: 75
learn:
  - id: forward-order
    text: explain the order in which the forward shader shades one pixel and why opaque surfaces draw with an equal depth test
  - id: brdf-compute
    text: compute the light that EvaluateLightWeighted returns for one light, one view and one material
  - id: specular-aa
    text: explain why a highlight narrower than a pixel sparkles and how WidenRoughness calms it
  - id: shader-rules
    text: name the rules that a change to the forward shader must keep, and the checks that guard them
  - id: variants
    text: find the six forward variants and the pass that picks each one
since: 0.3.0
status: final
---

The forward :term[shader]{id=shader} is the program that colors every visible surface of the scene exactly once. It reads the surface's material, adds the light of the sun, of the local lights and of the sky, and writes the result into the :term[high dynamic range]{id=high-dynamic-range} (HDR) target. This page reads that program from its direct-light function, the bidirectional :term[reflectance]{id=reflectance} distribution function (:term[BRDF]{id=brdf}), to its last line. It does not pick the lights for a pixel or draw shadows: the pages that own those steps are linked where the shader calls them. You need the reflection equation and the terms D, G and F from the reflectance page, and the material record from the material data page.

## The problem and how engines solve it

The surface problem is described in [the reflectance page](../light/reflectance.md): given a light, an eye and a material, how much light reaches the eye? The frame's order, and why Strata shades while it draws instead of storing surface data first, are in [the frame tour](../gpu/frame-tour.md). This page asks what is left once those are settled. How do you turn the formula into a shader that is fast, stays finite for every input, and does not flicker?

The flicker is the hard part. A shader evaluates its formula at one point per pixel, and a sharp highlight can fall between two points. That is the sampling problem of [the signals page](../basics/signals.md): a feature narrower than the sampling distance either lands on a pixel or misses it. As the surface moves, the highlight blinks. Rendering calls this **specular aliasing**.

A number shows the size of the problem. A smooth surface of :term[perceptual roughness]{id=perceptual-roughness} 0.22 has an `alpha` of 0.05, because `alpha` is the roughness squared. Its lobe falls to half its peak when the half vector is 0.032 :term[radian]{id=radian} away from the normal. On a surface with a :term[normal map]{id=normal-map} of small bumps, the normal can turn by 0.1 radian between neighbor pixels, which is three times that width.

One frame samples the lobe at tilts of 0, 0.1 and 0.2 radian, and hits its peak. The next frame samples at 0.05 and 0.15 radian, and misses the peak.

Engines filter the highlight in three ways. A texture-based method stores how much the normals vary inside each texel of a normal map, and widens the lobe by that amount. A screen-space method measures the change of the shading normal from one pixel to the next, with no extra data, and widens the lobe by that. A third family lets the temporal smoothing of the image average the blinking away.

The texture methods cost memory and preparation, and see only what the artist's maps hold. The screen-space method costs a few instructions per pixel, sees geometry as well as maps, and is wrong only where the normal jumps. Strata uses the screen-space method. This page calls it **specular anti-aliasing** (geometric): the shader widens the roughness by the normal's variance over one pixel.

:::elsewhere
Toksvig's method, linear efficient anti-aliased normal (LEAN) mapping and its relative, compositing of LEAN normals (CLEAN) mapping, are the texture-based family. Tokuyoshi and Kaplanyan's geometric filter is the screen-space one. The sources are in Further reading.
:::

## The map

Strata compiles one :term[source file]{id=source-file}, `Strata/shaders/Scene/Forward.frag.slang`, into six variants of the pixel shader, each built in four forms. The build gives each variant its own defines, and the renderer picks a variant by the kind of pass. The shader list is in `Strata/CMakeLists.txt`, in the `VARIANTS` of `strata_add_shaders`.

| Variant | Defines | Chosen by the pass | What it shades |
| --- | --- | --- | --- |
| `Forward` | no define | Opaque | Opaque and alpha-masked surfaces, after the prepass |
| `ForwardTransparent` | the transparent define | Transparent | Alpha-blended surfaces |
| `ForwardGlass` | the transparent and the glass defines | Glass | Glass, with entity ids, without motion |
| `ForwardGlassNoEntityIDs` | those two and the define for no entity ids | Glass | Glass for renderers without entity ids |
| `ForwardGlassVelocity` | the first two and the define for motion | Glass | Glass that also writes motion |
| `ForwardGlassNoEntityIDsVelocity` | all four | Glass | Glass without ids, with motion |

Each row of the list has three parts: the source, the name of the new shader and its defines. The glass variants add one define at a time to the glass define set.

```cmake src="Strata/CMakeLists.txt#L178-L183"
VARIANTS
	"Scene/Forward.frag|Scene/ForwardTransparent.frag|ST_FORWARD_TRANSPARENT"
	"Scene/Forward.frag|Scene/ForwardGlass.frag|ST_FORWARD_TRANSPARENT,ST_FORWARD_GLASS"
	"Scene/Forward.frag|Scene/ForwardGlassNoEntityIDs.frag|ST_FORWARD_TRANSPARENT,ST_FORWARD_GLASS,ST_NO_ENTITY_IDS"
	"Scene/Forward.frag|Scene/ForwardGlassVelocity.frag|ST_FORWARD_TRANSPARENT,ST_FORWARD_GLASS,ST_VELOCITY"
	"Scene/Forward.frag|Scene/ForwardGlassNoEntityIDsVelocity.frag|ST_FORWARD_TRANSPARENT,ST_FORWARD_GLASS,ST_NO_ENTITY_IDS,ST_VELOCITY"
```

The other five rows are the five variants. The renderer loads each shader by its file name when it creates its shaders, and picks it again by the kind of pass.

The list continues past these rows. Each of the six variants is built three more times: with the define for rectangle lights, with the define for the irradiance field of global illumination, and with both. That makes 24 shaders in all. `SceneRenderer::GetScenePipeline` picks the variant by the kind of pass, and the form by two flags of the :term[pipeline key]{id=pipeline-key}, `AreaLights` and `Field`. This page treats the six variants; [the area lights page](../light/area-lights.md) and [the cascades page](../indirect/gi-cascades.md) teach what the two defines add.

The first diagram shows the passes that feed the opaque pass, in frame order. The names are the stages of the :term[graphics processing unit]{id=gpu} (GPU) profiler, the same stages [the frame tour](../gpu/frame-tour.md) lists.

```mermaid caption="The passes before the forward pass, in frame order. The light clusters, and on frames of the GPU-driven path the light culling, run in the stage that comes first, which depends on the path the frame takes." alt="Boxes in a row. Setup, then culling on frames that use the graphics processor for it, then aerial perspective, shadows, the depth prepass, screen shadows, ambient occlusion and last the opaque pass. A note under the first boxes says that light culling and light clusters run there."
flowchart LR
	S["GPU.Setup"] --> C["GPU.Cull (GPU-driven frames only)"]
	C --> A["GPU.Aerial"]
	A --> H["GPU.Shadows"]
	H --> P["GPU.Prepass"]
	P --> M["GPU.ScreenShadows"]
	M --> O["GPU.AO"]
	O --> F["GPU.Opaque: the forward shader"]
	L["Light clusters: in GPU.Setup on the CPU path; light culling and clusters: in GPU.Cull on GPU-driven frames"] -.-> S
	L -.-> C
```

The profiler times light culling and the light clusters in the culling stage only on frames of the GPU-driven path. That stage starts only there, and `SceneRenderer::Render` records the light passes after it. On the path of the :term[central processing unit]{id=processor} (CPU), the processor picks the lights in view itself, and only the cluster pass runs, in the setup stage.

The aerial, shadow, screen shadow and ambient occlusion stages run only when the frame asks for them. The stages for global illumination and reflections sit between ambient occlusion and the opaque pass when enabled.

The second diagram shows the order inside one pixel. The real code follows it from top to bottom.

```mermaid caption="The steps of the forward shader for one pixel. The sun, the cluster lights and the sky each add light, and the fog, the glass and the clamping come last." alt="A column of boxes from top to bottom. The first are material, shading normal and widened roughness. Then come the sun, the lights of the cluster, indirect light, clear coat and emission. The last are aerial perspective, fog, glass, level of detail discard, pre-exposure and clamping."
flowchart TB
	A["Sample the material"] --> B["Shading normal"]
	B --> C["WidenRoughness"]
	C --> D["Sun"]
	D --> E["Cluster lights"]
	E --> F["Indirect light"]
	F --> G["Clear coat"]
	G --> H["Emission"]
	H --> I["Aerial perspective"]
	I --> J["Height fog"]
	J --> K["Glass: light from behind"]
	K --> L["LOD fade discard"]
	L --> M["Pre-exposure"]
	M --> N["SanitizeHDR"]
```

Each box has a reason for its place.

- The material comes first, because every later step needs the :term[albedo]{id=albedo}, the roughness and the metallic value. The shading normal follows, because the roughness widening reads how the normal changes across the pixel.
- The sun comes before the local lights. On opaque surfaces it reads a shadow mask that the screen shadow stage wrote; on transparent surfaces, which the prepass never saw, the shader filters the shadow map per pixel.
- The lights of the pixel's cluster add their light one by one. Their loop and their shadows are on [the many lights page](../light/many-lights.md).
- The indirect light, the coat and the emission end the lit color. The ambient occlusion that darkens the indirect light comes from the screen on opaque surfaces and is 1 on transparent ones.
- The aerial perspective and the fog act on the finished color, so a transparent surface looks like an opaque one at its depth. Glass adds what lies behind it after the fog, because the copy of the scene color it reads already holds that fog.
- The discard for the level-of-detail fade comes last among the decisions, after every sample and derivative. The pre-exposure, a power of two that scales the light of bright scenes into the range of the target, and `SanitizeHDR` prepare the value for the target.

Surfaces that ignore light skip the lit part of this order. They keep their base color and emission, and the fog and the exposure still apply to them.

## The contract

The forward pass relies on the passes before it and makes promises to the passes after it. Each rule has its reason, and [How it is tested](#how-it-is-tested) names the test that guards it.

- The opaque pass tests depth with an equal comparison and forces early depth tests. The prepass wrote the nearest depth of every pixel, so the opaque shader runs only where its fragment is the one that won. `SceneRenderer::GetScenePipeline` sets the depth function of `Pass::Opaque` to `Equal` and turns depth writing off. The shader declares `[earlydepthstencil]` through `ST_EARLY_FRAGMENT_TESTS`, so the test runs before the shader.
- The opaque variant discards only for the level-of-detail fade. The prepass already discarded the masked texels, so the opaque shader repeats only `IsLODFadeDrawn`, the same dither test, and the two passes keep the same pixels. The transparent variants also discard alpha-masked pixels, because no prepass ran for them.
- Everything is sampled before any discard. A discard ends a pixel's work, and its neighbors in the quad, the block of two by two pixels that the GPU shades together, then have no derivatives to choose a texture level from. The reason and the drivers that break are in [the shaders page](../gpu/shaders.md).
- Derivatives come only of the primitive's own :term[interpolants]{id=interpolant} and textures. The first rule below says it in full.
- Every HDR write goes through `SanitizeHDR`.
- The opaque pass writes alpha 1. Opaque writers store alpha 1 and blended ones multiply it by 1 minus their alpha. The reason for this convention is on [the temporal anti-aliasing page](../image/taa.md).

:::rule
The shader takes a screen derivative only of a value built from the primitive's own interpolants and its material's textures. It takes it in control flow that is uniform over a quad, with an explicit level where the flow is not uniform. Then both draw paths shade each pixel alike, whatever the order of draws. A quad belongs to one primitive, so its neighbors hold values of the same triangle, while a value read from a buffer written per draw would change with the order of draws. The driver side of the rule is on [the shaders page](../gpu/shaders.md).
:::

:::rule
Every shader that writes an HDR target clamps its color with `SanitizeHDR`. One :term[NaN]{id=nan} or infinity in a :term[half-float]{id=half-float} target turns black or spreads through every later filter, and nothing repairs the damage afterwards.
:::

The first rule also makes shading independent of the order of draws. The two draw paths submit instances in different orders, and the picture must not notice.

:::why
The prepass draws every opaque mesh a second time, and that costs vertex work and a depth pass. Strata pays it for two gains. The opaque shader, which does the most work per pixel, runs only for the surface that wins the pixel. The screen shadow and ambient occlusion stages also need the depth of the nearest surface before the opaque pass starts.
:::

## A toy version

The toy shades one row of five pixels of a smooth surface under one light. The light and the eye look straight down, so the half vector is the z axis, and the distribution term alone gives the highlight. The normal tilts by 0.1 radian from one pixel to the next, and `alpha` is 0.05. The variance measures how far the normals inside one pixel spread, and the toy estimates it from the change of the normal to the next pixel. The toy runs two frames, with the surface shifted by half a pixel between them, once with plain shading and once with the widening that the real code section explains.

The sketch uses the classes and :term[function calls]{id=function-call} that the earlier pages taught. Watch `ShadePixel`: the `widen` branch is the whole of specular anti-aliasing.

```cpp sketch="light-brdf-toy.cpp"
#include <glm/glm.hpp>

#include <algorithm>
#include <cmath>
#include <cstdio>

constexpr float c_Pi = 3.14159265f;

float DistributionGGX(float NoH, float alpha)
{
	const float alpha2 = alpha * alpha;
	const float f = (NoH * alpha2 - NoH) * NoH + 1.0f;
	return alpha2 / (c_Pi * f * f);
}

glm::vec3 NormalAt(float tilt)
{
	return glm::vec3(std::sin(tilt), 0.0f, std::cos(tilt));
}

// The highlight of one pixel. The light and the eye look straight down, so the half vector is +Z and NoH is the normal's Z.
float ShadePixel(float tilt, float tiltStep, float alpha, bool widen)
{
	const glm::vec3 normal = NormalAt(tilt);
	if (widen)
	{
		const glm::vec3 changeX = NormalAt(tilt + tiltStep) - normal;
		const float variance = 0.25f * glm::dot(changeX, changeX);
		alpha = std::sqrt(alpha * alpha + std::min(2.0f * variance, 0.18f));
	}
	return DistributionGGX(normal.z, alpha);
}

int main()
{
	const float alpha = 0.05f;
	const float tiltStep = 0.1f;
	for (const bool widen : { false, true })
	{
		for (const float shift : { 0.05f, 0.0f })
		{
			std::printf("%s, surface shifted by %.2f:", widen ? "widened" : "plain  ", shift);
			float peak = 0.0f;
			for (int pixel = 0; pixel < 5; pixel++)
			{
				const float value = ShadePixel(static_cast<float>(pixel - 2) * tiltStep + shift, tiltStep, alpha, widen);
				std::printf(" %6.2f", value);
				peak = std::max(peak, value);
			}
			std::printf("  peak %6.2f\n", peak);
		}
	}
	return 0;
}
```

```text output-of="light-brdf-toy.cpp"
plain  , surface shifted by 0.05:   1.30  31.94  31.94   1.30   0.20  peak  31.94
plain  , surface shifted by 0.00:   0.45   5.14 127.32   5.14   0.45  peak 127.32
widened, surface shifted by 0.05:   2.71  23.98  23.98   2.71   0.51  peak  23.98
widened, surface shifted by 0.00:   1.10   7.89  42.47   7.89   1.10  peak  42.47
```

1. **Line 21:** the light and the eye look straight down, so the :term[dot product]{id=dot-product} of the normal with the half vector is the normal's z.
2. **Lines 27–28:** the neighbor pixel's normal gives the change over one pixel, and the variance is a quarter of its squared length.
3. **Line 29:** the kernel, capped at 0.18, is added to the square of alpha, so the highlight widens but keeps its energy.

Read the peaks. Plain shading gives 31.94 in the first frame and 127.32 in the second, a factor of 4 between two frames of a surface that barely moved. That blink is specular aliasing. The widened lobe gives 23.98 and 42.47, a factor of 1.8, and the highlight now covers more pixels with less light in each.

The widening costs a little peak brightness and keeps the total. The toy also shows what it omits: every term but the distribution, and every other light. The real shader multiplies in those, as the next section shows.

The engine's shader widens the lobe the same way on a real surface. The pictures show a smooth metal ball with a normal map of fine bumps, drawn with the widening off and then on.

::compare{id=specular-aa-compare}

The middle of the ball, enlarged, shows the sun's spot alone without the widening and the patch of glints with it.

::figure{id=specular-aa-compare variant=switch-off crop=highlight}

::figure{id=specular-aa-compare variant=switch-on crop=highlight}

## The real code, in the order the data flows

Data flows from the material through the surface terms to the light, and from the light to the pixel written to the target. The sections follow that order.

### Distribution, visibility and Fresnel

`Strata/shaders/Include/PBR.slang` holds the three terms of the specular lobe. Each is one function. Watch the shape of each: D is a ratio, V is a reciprocal of a sum, and F is a weight between the head-on reflectance and 1.

```cpp src="Strata/shaders/Include/PBR.slang#L33-L52"
float DistributionGGX(float NoH, float alpha)
{
	float alpha2 = alpha * alpha;
	float f = (NoH * alpha2 - NoH) * NoH + 1.0;
	return alpha2 / (PI * f * f);
}

float VisibilitySmithGGXCorrelated(float NoV, float NoL, float alpha)
{
	float alpha2 = alpha * alpha;
	float lambdaV = NoL * sqrt((NoV - NoV * alpha2) * NoV + alpha2);
	float lambdaL = NoV * sqrt((NoL - NoL * alpha2) * NoL + alpha2);
	return 0.5 / max(lambdaV + lambdaL, 1e-5);
}

float3 FresnelSchlick(float3 f0, float VoH)
{
	float f = pow(1.0 - VoH, 5.0);
	return f + f0 * (1.0 - f);
}
```

1. **Line 36:** `f` is the bottom of the distribution's fraction, grouped as nested products of `NoH`.
2. **Line 37:** a smaller `alpha` makes the peak taller and narrower, and the lobe stays :term[normalized]{id=normalization}.
3. **Lines 43–44:** each :term[lambda]{id=lambda} is one masking term times the other :term[cosine]{id=cosine}, so `V` already holds the division by four times `NoV` times `NoL`.
4. **Line 45:** the `max` keeps the division finite when both cosines approach 0.
5. **Lines 50–51:** `f` is the fifth power of `1 - VoH`, and the result blends from `f0` head-on to 1 at the grazing angle.

### The direct-light function

`EvaluateLightWeighted` combines the terms for one light. Watch what it returns for a light behind the surface, how it limits the roughness, and how it splits the light between the diffuse and specular lobes.

```cpp src="Strata/shaders/Include/PBR.slang#L129-L148"
float3 EvaluateLightWeighted(SurfaceData surface, float3 lightDirection, float3 radiance, float diffuseWeight, float specularWeight, float sourceAlpha2)
{
	float3 H = normalize(surface.View + lightDirection);
	float NoL = clamp(dot(surface.Normal, lightDirection), 0.0, 1.0);
	if (NoL <= 0.0)
		return float3(0.0);
	float NoV = max(dot(surface.Normal, surface.View), 1e-4);
	float NoH = clamp(dot(surface.Normal, H), 0.0, 1.0);
	float VoH = clamp(dot(surface.View, H), 0.0, 1.0);

	float roughness = max(surface.Roughness, c_MinRoughness);
	float alpha = roughness * roughness;

	float3 F = FresnelSchlick(surface.F0, VoH);
	float3 specular = DistributionGGX(NoH, GetLobeAlpha(alpha, sourceAlpha2)) * VisibilitySmithGGXCorrelated(NoV, NoL, alpha) * F * surface.SpecularEnergy;
	// Diffuse keeps 1 - F: the compensated light leaves a dielectric's specular under 0.5% brighter, below what the diffuse
	// lobe's approximation already is off by.
	float3 diffuse = (1.0 - F) * (1.0 - surface.Metallic) * surface.Albedo * INV_PI * diffuseWeight;
	return (diffuse + specular * specularWeight) * radiance * NoL;
}
```

1. **Lines 132–134:** a light behind the surface returns black before any other work.
2. **Line 135:** `NoV` has a floor of 0.0001, because a normal map can turn the normal away from the eye.
3. **Line 139:** the floor `c_MinRoughness` keeps `alpha` above zero, as the worked example below shows.
4. **Line 143:** D, V and F multiply with `SpecularEnergy`; `GetLobeAlpha` widens only D, for sized sources.
5. **Line 146:** diffuse takes `1 - F` and `1 - Metallic`, and the weights let glass and probe captures scale each lobe.

:::example
Take plastic: albedo 0.8, metallic 0, perceptual roughness 0.5, `F0` 0.04, and a point light of :term[radiance]{id=radiance} 1 straight above, with the eye straight above too. A point light has a `sourceAlpha2` of 0, so `GetLobeAlpha` leaves `alpha` alone; both weights and `SpecularEnergy` are 1. So `NoL`, `NoV`, `NoH` and `VoH` are all 1. The roughness is above the minimum, so `alpha` is 0.25.

D is `alpha2 / (PI * f * f)`, and `f` equals `alpha2`, 0.0625, when `NoH` is 1. That gives 1 / (π × 0.0625) = 5.093. V has both :term[lambdas]{id=lambda} equal to 1, so V is 0.5 / 2 = 0.25. F has `VoH` of 1, so the power term is 0 and F is `F0`, 0.04.

The specular lobe is 5.093 × 0.25 × 0.04 = 0.0509. The diffuse lobe is (1 − 0.04) × 1 × 0.8 / π = 0.2445. The sum, times radiance 1 and `NoL` 1, is 0.2954. Diffuse carries 83 % of the light here. A smoother surface moves light into the specular lobe.

Now set the roughness to 0. Without the floor, `alpha2` is 0, `f` is 0 and D is 0 / 0, a NaN that turns the pixel black. With the floor of 0.045, `alpha` is 0.002 and D peaks at 77,625, a large but finite number. V and F scale it down to a spike of 776. `SanitizeHDR` exists for the values that still escape.
:::

The terms hold three more design choices. The roughness the artist sets is the perceptual one, and the shader squares it to get `alpha`. V uses the height-correlated form of Smith's masking, which counts how a :term[microfacet]{id=microfacet} hides another one from the light and from the eye together. It costs two square roots per light.

The diffuse lobe keeps only the share `1 − F` of the light that the specular lobe did not reflect, and it drops to zero for a metal. A non-metal at `F0` 0.04 and a head-on view loses 4 % of its diffuse light to the specular lobe, so the two lobes never add up to more light than arrived. The factor `SpecularEnergy` that scales the specular term is the multiple-scattering compensation, which [the energy page](../light/energy.md) teaches.

### Widening the roughness

Where does the pixel's own variance come in? `WidenRoughness` takes the perceptual roughness, the screen derivatives of the shading normal and the strength switch, and returns a larger roughness. The inputs are `normalDx` and `normalDy`, and the strength is `MaterialParams.z`: 1 when the renderer's specification asks for the widening and 0 otherwise.

```cpp src="Strata/shaders/Include/PBR.slang#L77-L91"
static const float c_SpecularAAVariance = 0.25;
// The most the lobe's alpha^2 is widened: silhouettes and seams, where the normal jumps, would otherwise turn matte.
static const float c_SpecularAAMaxKernel = 0.18;

// The perceptual roughness widened by the variance of the normal over the pixel: `normalDx` and `normalDy` are the screen
// derivatives of the unit shading normal; `strength` 0 returns the roughness unchanged (MaterialParams.z). Derivatives are
// taken only of the primitive's own interpolants and textures, so both draw paths shade alike (Docs/DeveloperGuide.md,
// "Lighting").
float WidenRoughness(float perceptualRoughness, float3 normalDx, float3 normalDy, float strength)
{
	float variance = c_SpecularAAVariance * (dot(normalDx, normalDx) + dot(normalDy, normalDy));
	float kernel = min(2.0 * variance, c_SpecularAAMaxKernel) * strength;
	float alpha = perceptualRoughness * perceptualRoughness;
	return sqrt(sqrt(clamp(alpha * alpha + kernel, 0.0, 1.0)));
}
```

1. **Line 77:** the variance of the normal over a pixel is a quarter of the squared derivatives.
2. **Line 79:** the cap keeps silhouettes and seams from turning dull.
3. **Line 87:** the variance sums the squared lengths of the normal's change along x and along y.
4. **Line 88:** the kernel is twice the variance, capped, times the strength; strength 0 changes nothing.
5. **Line 90:** the kernel is added to the square of `alpha`, and two square roots return a perceptual roughness.

On a flat surface with no normal map, the normal does not change across a pixel. Both derivatives are zero, and the function hands back the roughness it received. A silhouette is the other extreme. The normal turns sharply between neighbors, and without the cap the edge would turn dull. Strata keeps the highlight's energy while widening it, because the distribution stays :term[normalized]{id=normalization}.

The roughness this function returns reaches more than the sun and the lights. The :term[depth prepass]{id=depth-prepass} has a variant that writes the same widened value into a surface target, so the screen-space reflections trace the lobe that the forward pass shades. The glass variant blurs what lies behind it by the widened roughness, and the clear coat widens its own roughness from its own normal.

### The main function

`main` calls `st_Main`, which samples first and decides afterwards. Watch the order of samples, the branch for surfaces that ignore light, and where the derivatives of the shading normal are taken.

```cpp src="Strata/shaders/Scene/Forward.frag.slang#L507-L541"
void st_Main()
{
	InstanceData instance = u_Instances[v_InstanceIndex];
	MaterialData material = u_Materials[instance.MaterialIndex];
	float2 uv = TransformUV(material, v_TexCoord);

	// The surface is shaded before anything is discarded: a quad whose other pixels discarded has no implicit derivatives
	// (texture levels of detail, the shadow's filter) left (Architecture.Shaders).
	float4 baseColor = material.BaseColor * SampleMaterialTexture(material.BaseColorMap, uv);
	float3 emissive = material.Emissive.rgb * SampleMaterialTexture(material.EmissiveMap, uv).rgb;
#ifdef ST_AREA_LIGHTS
	// A reflection probe's capture (MaterialParams.w 1) draws a light surface's emission as 0, lit or unlit: the probe holds
	// the room its light lit, not the panel, whose light and highlight the area light adds per pixel.
	if ((instance.Flags & ST_INSTANCE_LIGHT_SURFACE) != 0u && u_Frame.MaterialParams.w > 0.5)
		emissive = float3(0.0);
#endif
	float3 color = baseColor.rgb + emissive;
	// The lighting debug view: Lighting shades every lit surface white without its emission (unlit ones draw as they are).
	uint lightingView = GetLightingView();
	bool valueView = IsLightingValueView(lightingView);
	bool whiteView = lightingView == ST_LIGHTING_VIEW_LIGHTING || lightingView == ST_LIGHTING_VIEW_GLOBAL_ILLUMINATION;
	float3 albedo = whiteView ? float3(1.0) : baseColor.rgb;
	float3 surfaceEmissive = whiteView ? float3(0.0) : emissive;
#ifdef ST_FORWARD_GLASS
	float3 transmitted = float3(0.0);
#endif
	if ((material.Flags & ST_MATERIAL_UNLIT) == 0u)
	{
		float4 metallicRoughness = SampleMaterialTexture(material.MetallicRoughnessMap, uv);
		float3 shadingNormal = GetShadingNormal(material, uv, v_Normal, v_Tangent, st_FrontFacing);
		// Specular anti-aliasing (MaterialParams.z): the lobe widened by the shading normal's change across the pixel. Derivatives
		// only of the primitive's interpolants and textures, in a branch on its material (the same for a whole quad), before any
		// discard: both draw paths shade alike.
		float roughness = WidenRoughness(clamp(material.Roughness * metallicRoughness.g, 0.0, 1.0), ddx(shadingNormal), ddy(shadingNormal),
			u_Frame.MaterialParams.z);
```

1. **Lines 509–511:** the instance, its material and the :term[texture coordinates]{id=texture-coordinates} come first.
2. **Lines 515–516:** base color and emission are sampled before any discard, so the quad's derivatives stay defined.
3. **Line 533:** a flag of the material skips all lit shading for surfaces that ignore light.
4. **Lines 535–536:** the metallic and roughness map and the shading normal follow.
5. **Lines 540–541:** `ddx` and `ddy` of the shading normal widen the roughness, in a branch on the material that is the same for a whole quad.

`ShadeLitSurface` runs the lights. It forms `F0` from the material's index of refraction, and moves it toward the albedo by the metallic value. Then it reads the lookup table of the reflection integral and loops over the lights of the cluster. Last it gathers the indirect light and applies the clear coat. The loop and the local shadows belong to [the many lights page](../light/many-lights.md), the indirect light to [the indirect light page](../indirect/seam.md), and the coat to [the clear coat page](../light/clearcoat-transmission.md).

Each light goes through `LightSurface`, which calls `EvaluateLightWeighted` and, when the material has a coat, covers the base with it. Highlights of sized sources use the `sourceAlpha2` argument, which [the area lights page](../light/area-lights.md) explains. A reflection probe's capture sets `MaterialParams.w` to 1, and `LightSurface` then drops the specular term: a highlight depends on where it is seen from, so a captured one would show in the wrong places.

The end of `st_Main` shows the steps after shading. Watch the single discard, the alpha of the output and the pre-exposure.

```cpp src="Strata/shaders/Scene/Forward.frag.slang#L590-L617"
// Every variant hazes and fogs alike, so a transparent surface looks like an opaque one at its depth: the air's haze
// first (aerial perspective), then the height fog, nearer the camera, over it. The value views show the surface's own
// values.
bool fogged = !valueView && !IsLightKindView(lightingView);
if (u_Frame.FogParams.z > 0.0 && fogged)
	color = ApplyAerialPerspective(color, v_RelativePosition, st_FragCoord.xy);
if (u_Frame.FogParams.x > 0.0 && fogged)
	color = ApplyHeightFog(color, v_RelativePosition);
#ifdef ST_FORWARD_GLASS
if (fogged)
	color += transmitted;
#endif

// The prepass's mask: of a fading level, only the pixels whose depth it wrote.
if (!IsLODFadeDrawn(v_LODFade, st_FragCoord.xy))
	discard;
#ifdef ST_FORWARD_TRANSPARENT
if ((material.Flags & ST_MATERIAL_ALPHA_MASK) != 0u && baseColor.a < material.AlphaCutoff)
	discard;
#endif
#if defined(ST_FORWARD_TRANSPARENT) && !defined(ST_FORWARD_GLASS)
float alpha = (material.Flags & ST_MATERIAL_ALPHA_BLEND) != 0u ? baseColor.a : 1.0;
#else
const float alpha = 1.0;
#endif
// Pre-exposed (TemporalParams.y, a power of two: exact unless a value overflows or becomes subnormal), but for the value
// views: a sunlit scene's pre-exposure (2^-19) would make an albedo of 0.03 subnormal in half floats.
o_Color = float4(SanitizeHDR(valueView ? color : color * u_Frame.TemporalParams.y), alpha);
```

1. **Lines 593–597:** haze and then fog act on the finished color, except in the debug views that show plain values or one kind of light.
2. **Lines 598–601:** glass adds the light from behind it.
3. **Lines 604–605:** the one discard of the opaque variant, the same test as the prepass.
4. **Lines 606–614:** the transparent variants discard masked texels, and the alpha is 1 unless the material blends.
5. **Line 617:** the color times the pre-exposure goes through `SanitizeHDR`, and the alpha is written beside it.

### The last step: clamping the color

The last call of the shader is `SanitizeHDR`. The helper lives in `Strata/shaders/Include/Common.slang`.

```cpp src="Strata/shaders/Include/Common.slang#L49-L57"
static const float c_MaxHDRValue = 65000.0;

// Makes a linear color safe to store and process: NaN becomes 0, negative values 0 and overflowing ones (Inf
// included) c_MaxHDRValue. Inf or NaN in an HDR target would turn black or spread through the post-processing.
float3 SanitizeHDR(float3 color)
{
	color = select(isnan(color), float3(0.0), color);
	return clamp(color, float3(0.0), float3(c_MaxHDRValue));
}
```

**`SanitizeHDR`** is the function that makes a :term[linear color]{id=linear-color} safe to store in an HDR target: NaN becomes 0, negative values become 0, and anything above 65,000, infinity included, becomes 65,000. The half-float format holds values up to 65,504, so the limit leaves a margin. The pre-exposure that the shader applies right before it is a power of two, so ordinary colors stay far below that limit.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Deferred shading from a G-buffer | Engines that store surface data first (see the frame tour) | One shading pass per pixel and cheap many-light loops | Memory for the surface targets, and glass and blended surfaces still need a forward pass |
| Toksvig maps | The texture-based family: variance from the length of the filtered normal | No derivative needed in the shader | A preparation step for each normal map, and no effect on geometry that bends |
| LEAN and CLEAN maps | Texture methods that store second moments of the normals | Exact filtering of a map at every distance | Extra texture channels, memory and preparation for every normal map |
| Leave the sparkle to temporal anti-aliasing | Engines whose image is always temporally filtered | No filter in the shader | Sparkle in single images, and in any frame when the temporal filter is off |

## How it is tested

Three groups of tests guard the page's rules. The GPU tests need a graphics processor, and the shader checks do not.

- `GPU.SceneRenderer.Materials` holds the specular anti-aliasing test. It renders a smooth metal sphere with a normal map of small bumps twice, with the switch off and on. It checks that the variance of the highlight falls to half or less and that the sphere's light stays within 15 %. A second test checks that the prepass's surface target holds the widened roughness that the forward pass shades.
- `GPU.SceneRenderer.GPUDriven` renders each of its test scenes, among them "Lit materials", with the CPU path and the GPU-driven path, and compares the pixels. A derivative taken of the wrong value fails here.
- `Architecture.Shaders` reads the shader sources as text. The test "Fragment shaders take every derivative before their first discard" fails when any derivative, direct or through a helper, comes after a `discard`.

The switch that the first test flips is `SceneRendererSpecification::SpecularAntiAliasing`. It is a field of the renderer's specification that defaults to true, and `MaterialParams.z` carries it to the shader. The GPU suites run in the `ctest` entry labelled gpu: `ctest --preset windows-debug -L gpu`. To run one suite, pass a doctest filter to the test program: `build/windows/bin/Debug/StrataTests.exe --test-suite=GPU.SceneRenderer*`.

## Changing it safely

Most changes to a term are small, and most mistakes are in what the term touches. Follow these steps.

1. Find every user of the function. `EvaluateLightWeighted` also serves the clear coat, the glass variants and the reflection probe's capture through its weights, so change a term in a way that each caller accepts.
2. Keep the prepass and the forward pass equal to the bit wherever they share a value. The prepass writes the widened roughness into the surface target for the reflections, so a change to `WidenRoughness` changes both.
3. Never take a derivative after a discard, and keep derivatives to the rule above.
4. Keep both draw paths equal. Run `GPU.SceneRenderer.GPUDriven` after any change to this file.
5. Clamp what you write. Any new HDR write goes through `SanitizeHDR`.
6. Run the shader checks and the GPU suites listed above. When a lighting term changes, also run the white-furnace test that [the energy page](../light/energy.md) describes, and read the debug views of [the measuring light page](../light/measuring-light.md).

## Summary

- The forward shader shades each pixel once, after the prepass, with an equal depth test, early depth tests and a discard only for the level-of-detail fade.
- `EvaluateLightWeighted` multiplies `GGX` D, correlated Smith V and Schlick F, adds :term[Lambert]{id=lambert} weighted by (1 − F) and (1 − metallic), and floors the roughness at 0.045.
- A highlight narrower than a pixel blinks; `WidenRoughness` adds the normal's variance over a pixel to the lobe, capped at 0.18.
- Samples come before any discard, derivatives come only of the primitive's own values, and every HDR write goes through `SanitizeHDR`.
- Six variants come from one source by defines: opaque, transparent and four glass variants, each picked by the pass and each built in four forms for rectangle lights and the irradiance field.

## Check yourself

1. Which statement about discarding in the opaque variant is right? (a) It discards pixels whose alpha is below the cutoff. (b) It discards only pixels that the level-of-detail fade removed. (c) It never discards.

   :::answer{tests="forward-order"}
   (b) is right. (a) is wrong: the prepass already discarded the masked texels, and only the transparent variants test the cutoff. (c) is wrong: `IsLODFadeDrawn` is the one discard of the opaque pass, so that its pixels match the prepass.
   :::

2. A plastic surface (albedo 0.5, `F0` 0.04, roughness 0.5) is lit head-on, seen head-on, by a light of radiance 2. What does `EvaluateLightWeighted` return?

   :::answer{tests="brdf-compute"}
   The specular lobe is 0.0509 as in the worked example. The diffuse lobe is 0.96 × 0.5 / π = 0.1528. The sum is 0.2037, and times radiance 2 and `NoL` 1 the result is 0.407 for each channel.
   :::

3. Predict: in the toy, the surface has no bumps, so the normal does not change between pixels. What does the `widen` branch change?

   :::answer{tests="specular-aa"}
   Nothing. The change of the normal is zero, so the variance and the kernel are zero, and the lobe keeps its `alpha`. A flat surface keeps its roughness exactly, which is the case the widening must not disturb.
   :::

4. A colleague adds a texture sample without an explicit level after the `discard` line of the forward shader. Which check fails, and why does it matter?

   :::answer{tests="shader-rules"}
   `Architecture.Shaders` fails with "Fragment shaders take every derivative before their first discard". A discard ends one pixel's work, and its quad neighbors lose the derivatives that choose the texture level, so some drivers shade wrong pixels.
   :::

5. Which pixel shader does a glass draw use for a renderer without entity ids, in a frame that writes motion?

   :::answer{tests="variants"}
   `ForwardGlassNoEntityIDsVelocity.frag`, in a frame without a rectangle light or the irradiance field. `SceneRenderer::GetScenePipeline` picks the velocity glass shader when the key has motion, and the renderer's choice about entity ids selected the variant without ids when it loaded the shaders. A frame with a rectangle light or the field uses the form whose name ends in `AreaLights`, `Field` or both.
   :::

## Exercises

1. **Basic.** Write a CPU function that returns what `EvaluateLightWeighted` returns for one point light, with both weights 1 and a specular energy of 1. Check it against the worked example, which gives 0.2954 for each channel.

   :::answer[Worked solution]{tests="brdf-compute"}
   Port the three term functions from the quote above, then the body in order: half vector, clamped :term[cosines]{id=cosine}, floored roughness, the specular product and the weighted diffuse. The first line printed is the worked example.

   ```cpp sketch="light-brdf-reference.cpp"
   #include <glm/glm.hpp>

   #include <algorithm>
   #include <cmath>
   #include <cstdio>

   constexpr float c_Pi = 3.14159265f;
   constexpr float c_MinRoughness = 0.045f;

   struct Surface
   {
   	glm::vec3 Normal = glm::vec3(0.0f, 0.0f, 1.0f);
   	glm::vec3 View = glm::vec3(0.0f, 0.0f, 1.0f);
   	glm::vec3 Albedo = glm::vec3(0.8f);
   	float Metallic = 0.0f;
   	float Roughness = 0.5f;
   	glm::vec3 F0 = glm::vec3(0.04f);
   };

   float DistributionGGX(float NoH, float alpha)
   {
   	const float alpha2 = alpha * alpha;
   	const float f = (NoH * alpha2 - NoH) * NoH + 1.0f;
   	return alpha2 / (c_Pi * f * f);
   }

   float VisibilitySmithGGXCorrelated(float NoV, float NoL, float alpha)
   {
   	const float alpha2 = alpha * alpha;
   	const float lambdaV = NoL * std::sqrt((NoV - NoV * alpha2) * NoV + alpha2);
   	const float lambdaL = NoV * std::sqrt((NoL - NoL * alpha2) * NoL + alpha2);
   	return 0.5f / std::max(lambdaV + lambdaL, 1e-5f);
   }

   glm::vec3 FresnelSchlick(const glm::vec3& f0, float VoH)
   {
   	const float f = std::pow(1.0f - VoH, 5.0f);
   	return glm::vec3(f) + f0 * (1.0f - f);
   }

   // The shader's EvaluateLightWeighted for a point light, with both weights 1 and a specular energy of 1.
   glm::vec3 EvaluateLight(const Surface& surface, const glm::vec3& lightDirection, const glm::vec3& radiance)
   {
   	const glm::vec3 H = glm::normalize(surface.View + lightDirection);
   	const float NoL = glm::clamp(glm::dot(surface.Normal, lightDirection), 0.0f, 1.0f);
   	if (NoL <= 0.0f)
   		return glm::vec3(0.0f);
   	const float NoV = std::max(glm::dot(surface.Normal, surface.View), 1e-4f);
   	const float NoH = glm::clamp(glm::dot(surface.Normal, H), 0.0f, 1.0f);
   	const float VoH = glm::clamp(glm::dot(surface.View, H), 0.0f, 1.0f);

   	const float roughness = std::max(surface.Roughness, c_MinRoughness);
   	const float alpha = roughness * roughness;
   	const glm::vec3 F = FresnelSchlick(surface.F0, VoH);
   	const glm::vec3 specular = DistributionGGX(NoH, alpha) * VisibilitySmithGGXCorrelated(NoV, NoL, alpha) * F;
   	const glm::vec3 diffuse = (glm::vec3(1.0f) - F) * (1.0f - surface.Metallic) * surface.Albedo / c_Pi;
   	return (diffuse + specular) * radiance * NoL;
   }

   void Print(const char* name, const glm::vec3& light)
   {
   	std::printf("%-22s %.4f %.4f %.4f\n", name, light.x, light.y, light.z);
   }

   int main()
   {
   	const glm::vec3 radiance(1.0f);
   	Surface plastic;
   	Print("plastic, head-on", EvaluateLight(plastic, glm::vec3(0.0f, 0.0f, 1.0f), radiance));

   	const glm::vec3 slanted = glm::normalize(glm::vec3(1.0f, 0.0f, 1.0f));
   	Print("plastic, light at 45", EvaluateLight(plastic, slanted, radiance));

   	Surface gold;
   	gold.Albedo = glm::vec3(1.0f, 0.77f, 0.34f);
   	gold.Metallic = 1.0f;
   	gold.F0 = gold.Albedo;
   	Print("gold, light at 45", EvaluateLight(gold, slanted, radiance));

   	Surface mirror = plastic;
   	mirror.Roughness = 0.0f;
   	Print("roughness 0 reads 0.045", EvaluateLight(mirror, glm::vec3(0.0f, 0.0f, 1.0f), radiance));
   	return 0;
   }
   ```

   ```text output-of="light-brdf-reference.cpp"
   plastic, head-on       0.2954 0.2954 0.2954
   plastic, light at 45   0.1778 0.1778 0.1778
   gold, light at 45      0.1227 0.0945 0.0417
   roughness 0 reads 0.045 771.9325 771.9325 771.9325
   ```

   1. **Line 20:** the same D as the shader, written in C++.
   2. **Line 27:** the same V, with the same floor on the sum.
   3. **Line 52:** the floor on the roughness, before `alpha` is formed.
   4. **Lines 55–56:** the two lobes, with the diffuse lobe weighted by `1 - F` and the metallic value.
   5. **Lines 80–82:** a roughness of 0 shades as 0.045.

   The last line shows the floor: a roughness of 0 gives a large but finite value. It differs from the exact 776 by under 1 %, because `f` is a difference of numbers near 1 and loses digits in 32-bit floats. To compare with a GPU render, render a sphere under one sun at two strengths and subtract the two images, so that ambient light cancels. Then divide by the frame's pre-exposure.
   :::

2. **Medium.** Trace it yourself: find where the six forward variants are declared and where a draw's pass picks the pixel shader it runs. Use a search, not a guess.

   :::answer[Worked solution]{tests="variants"}
   Search for `ForwardGlassNoEntityIDsVelocity`. The declarations are in `Strata/CMakeLists.txt`, in the `VARIANTS` list of `strata_add_shaders`, each with its defines. The shaders are fetched in `SceneRenderer::CreateResources` (opaque, transparent and the glass without motion) and in `SceneRenderer::EnsureMotionResources` (glass with motion). `SceneRenderer::GetScenePipeline` has a `switch` on the pass type that assigns `desc.PS`.
   :::

3. **Hard.** At a silhouette the normal turns 0.8 radian between neighbors, and `alpha` is 0.05. Compute the widened `alpha`, and say what the cap does.

   :::answer[Worked solution]{tests="specular-aa"}
   The change of the unit normal is 2 sin(0.4) = 0.779, and its square is 0.607. The variance is 0.25 × 0.607 = 0.152, and twice that, 0.303, is above the cap, so the kernel is 0.18. The new `alpha` is the square root of 0.0025 + 0.18, which is 0.427, a perceptual roughness of 0.654. Without the cap, `alpha` would reach 0.55, and a hard edge would turn almost dull.
   :::

## Where it lives in Strata

- Shaders: `Strata/shaders/Scene/Forward.frag.slang`, `Strata/shaders/Include/PBR.slang`, `Strata/shaders/Include/Common.slang`.
- Variants: `Strata/CMakeLists.txt`, the `VARIANTS` of `strata_add_shaders`.
- Renderer: `SceneRenderer::GetScenePipeline` and `SceneRenderer::Render` in `Strata/src/Strata/Renderer/SceneRenderer.cpp`.
- Switch: `SceneRendererSpecification::SpecularAntiAliasing`.
- Tests: `GPU.SceneRenderer.Materials`, `GPU.SceneRenderer.GPUDriven`, `Architecture.Shaders`.

## Further reading

- Toksvig, "Mipmapping Normal Maps" (2005): the first filter for normal maps; beginner to intermediate.
- Olano and Baker, "LEAN Mapping" (2010): second moments of normals; intermediate.
- Baker and Hill, "Rock-Solid Shading" (2012): CLEAN mapping and stable highlights; intermediate.
- Tokuyoshi and Kaplanyan, "Improved Geometric Specular Antialiasing" (2019): the screen-space variance; advanced.
- Heitz, "Understanding the Masking-Shadowing Function in Microfacet-Based BRDFs" (2014): the correlated Smith term; advanced.
