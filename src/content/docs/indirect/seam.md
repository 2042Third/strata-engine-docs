---
id: indirect/seam
title: "Where indirect light meets the surface: inputs, gathers and fallbacks"
description: "How the forward shader gathers every kind of indirect light into one struct, two gathers and a compose step, and which layer wins at a pixel."
kind: internals
size: M
tracks: [E]
needs: [indirect/ibl]
time: 75
learn:
  - id: choose-form
    text: predict which of the four forms of indirect light a pixel takes
  - id: compute-gathers
    text: compute a pixel's diffuse and specular indirect light in each form
  - id: explain-premultiplied
    text: explain why each fallback layer replaces the next by a premultiplied weight
  - id: add-field
    text: add a field to the inputs without changing a bit of the default image
  - id: trace-frame
    text: trace an indirect term of a pixel back to the pass that made it
since: 0.8.0
status: final
---

A lit surface in Strata receives indirect light from up to five places: reflection probes, screen-space reflections, the sky, the constant ambient and the global illumination field. The forward :term[shader]{id=shader} is the one place where all of them meet the surface. It fills one :term[struct]{id=struct} of inputs per pixel, reads that struct in two gathers (one for diffuse light, one for specular light) and adds the two results in a compose step. This page is the map of that join. How each input is made belongs to the later pages of the part; this page does not teach them.

## The problem and how engines solve it

A pixel can be lit by several sources of indirect light, and each source covers only part of the scene. The page [The indirect-light problem](../indirect/problem.md) explains the sources and their costs. The question here is smaller: where in the shader do they meet, and who wins when two of them claim the same pixel? Strata answers with a fixed order of layers in one function, so the answer is the same for every pixel and every material.

## The map

The inputs are made before the forward pass draws anything. On the :term[central processing unit]{id=processor} (CPU), `PrepareGlobalIllumination` runs when the frame uses the field, `GatherReflectionProbes` picks the probes, and `UploadReflectionProbes` uploads their list. On the :term[graphics processing unit]{id=gpu} (GPU) the passes run in the order of the first diagram. Each pass writes a texture or a buffer, and the opaque pass reads them.

```mermaid caption="The passes that make indirect light run in this order before the pass that draws opaque surfaces. Each arrow carries the slot that the drawing pass reads the result from." alt="A chain of boxes: the depth prepass, the sun's screen shadows, ambient occlusion, global illumination, probe conversions with the reflection trace, and the opaque pass. Labels on the arrows name the slots each result is read from."
flowchart LR
    CPU["CPU: PrepareGlobalIllumination, GatherReflectionProbes"] --> P["GPU.Prepass"]
    P --> S["GPU.ScreenShadows"]
    S --> AO["GPU.AO"]
    AO -->|"SRV 11"| GI["GPU.RadianceCascades"]
    GI -->|"b3, SRV 35 37 38 39 40 54"| R["GPU.Reflections"]
    R -->|"SRV 9, 10 and 18"| O["GPU.Opaque"]
```

The opaque pass reads ambient occlusion at texture slot 11, the probes' cubes and list at slots 9 and 10, and the screen-space reflections at slot 18. It reads the field through the :term[constant buffer]{id=constant-buffer} `b3` and the slots 35, 37, 38, 39, 40 and 54. A frame that has no probes, no reflections or no field still binds something at each slot: a black texture or a dummy view. That is what lets the shader read them without a branch on whether they exist.

The second diagram shows one pixel. Each column is a stack of layers: the top layer takes a share of the light, and the layer below fills what is left.

```mermaid caption="One pixel in two columns. In each column the upper layer takes a share and the lower layers fill the rest. The diffuse column ends with the constant ambient, the specular column has none." alt="Two columns of boxes. The specular column lists screen-space reflections, probes, sky. The diffuse column lists the field, probes with the sky's share, sky, constant ambient. Notes on each column name the multipliers: occlusion color and diffuse weight for diffuse, reflectance and specular occlusion for specular."
flowchart TB
    subgraph Specular
        direction TB
        SS["Screen-space reflections: confidence a"] --> SP["Probes: weight w"]
        SP --> SK["Sky: 1 - w"]
        SK --> SM["x SpecularColor x SpecularOcclusion"]
    end
    subgraph Diffuse
        direction TB
        DF["Field: FieldWeight replaces the rest"] --> DP["Probes' irradiance: w"]
        DP --> DS["Sky irradiance: 1 - w"]
        DS --> DA["Constant ambient: only without a sky"]
        DA --> DM["x albedo x (1 - metallic) x occlusion color"]
    end
```

Ambient occlusion darkens both columns, but not in the same way. The diffuse column multiplies by an occlusion color that holds the multi-bounce fit. The specular column multiplies by a specular occlusion that is computed from the diffuse one. Both fits are taught on [ambient occlusion](../indirect/ao.md).

## The contract

Before either gather runs, the shader sorts each pixel into one of four forms by what lights it: probes, screen-space reflections without probes, the sky alone, or the constant ambient alone. Callers and later pages can rely on these rules, and each has a reason.

- **`IndirectInputs` is filled once per pixel.** The function `GetIndirectInputs` makes it, and both gathers only read it. Two gathers that made their own reads would sample the same cubes twice and could disagree about which form the pixel takes.
- **New streams add fields at the end.** The struct in `Strata/shaders/Include/IndirectLight.slang` grows only by appending, as the file's own comment says. A stream that changes an old field changes every pixel that reads it.
- **The four forms keep Strata 0.7.0's branch order and expressions bit for bit.** The forms are `ST_INDIRECT_PROBES`, `ST_INDIRECT_SCREEN`, `ST_INDIRECT_SKY` and `ST_INDIRECT_AMBIENT`. A scene that does not use the new features must render the image it rendered before them.
- **A feature that is off costs nothing and changes no bit, because its input is a dummy.** Without probes the shader samples a black :term[cube array]{id=cube-array}, without reflections a black texture, without the field a black 3D texture. A dummy contributes exactly 0, and adding 0 changes no bit.

:::rule[The renderer's rule: a frame without a feature keeps the old image, bit for bit]
`AGENTS.md` asks that a frame without global illumination keeps the indirect light's old expression, bit for bit, whether the scene did not ask for it, its row is Off or its field is still pending. The reason is that tests can then compare a new frame with an old one exactly. The whole :term[renderer]{id=renderer} follows this rule; its home is [a frame of the scene renderer](../gpu/frame-tour.md). One cost remains: the field's gather is compiled in, so it costs a little even when off, which [the limits of global illumination](../indirect/gi-limits.md) discusses.
:::

## A toy version

:::question
Does the toy's C++ look strange? It uses only structs, an `enum class`, functions and `if`; the pages [Programming 1](../basics/programming-1.md), [Programming 2](../basics/programming-2.md) and [Programming 3](../basics/programming-3.md) teach them.
:::

The toy works on one :term[color channel]{id=color-channel}, with the numbers fixed as constants. It has the same parts as the shader: a struct of inputs, a function that chooses the form, two gathers and a compose step. Note the order in `ChooseForm` and where the sky's intensity is applied in each form, because that is where the forms differ.

```cpp sketch="indirect-seam-toy.cpp"
// A toy of the indirect light's seam on one color channel: one struct of inputs, two gathers and a compose step.
#include <cstdio>

enum class Form
{
	Probes,
	Screen,
	Sky,
	Ambient
};

struct Inputs
{
	Form Kind = Form::Ambient;
	bool Environment = false;
	float ProbeWeight = 0.0f;
	float ProbeIrradiance = 0.0f;
	float ProbeRadiance = 0.0f;
	float ScreenLight = 0.0f; // Premultiplied: the light times the confidence
	float ScreenConfidence = 0.0f;
	float SkyIrradiance = 0.0f;
	float SkyRadiance = 0.0f;
};

constexpr float c_Albedo = 0.5f;
constexpr float c_SpecularColor = 0.1f;
constexpr float c_DiffuseOcclusion = 0.8f;
constexpr float c_SpecularOcclusion = 0.6f;
constexpr float c_ScreenOcclusion = 0.9f;
constexpr float c_Ambient = 0.2f;
constexpr float c_SkyIntensity = 2.0f;

Form ChooseForm(const Inputs& inputs)
{
	if (inputs.ProbeWeight > 0.0f)
		return Form::Probes;
	if (inputs.ScreenConfidence > 0.0f)
		return Form::Screen;
	return inputs.Environment ? Form::Sky : Form::Ambient;
}

float GatherDiffuse(const Inputs& inputs)
{
	const float scatter = c_Albedo * (1.0f - c_SpecularColor);
	const float sky = 1.0f - inputs.ProbeWeight;
	float diffuse = c_Ambient * c_Albedo;
	if (inputs.Kind == Form::Probes)
		diffuse = (inputs.ProbeIrradiance + inputs.SkyIrradiance * c_SkyIntensity * sky) * scatter;
	else if (inputs.Kind == Form::Screen)
		diffuse = inputs.SkyIrradiance * scatter * c_SkyIntensity;
	else if (inputs.Kind == Form::Sky)
		diffuse = inputs.SkyIrradiance * scatter;
	return diffuse * c_DiffuseOcclusion;
}

float GatherSpecular(const Inputs& inputs)
{
	float fallback = inputs.SkyRadiance;
	if (inputs.Kind == Form::Ambient)
		return 0.0f;
	if (inputs.Kind == Form::Probes)
		fallback = inputs.ProbeRadiance + inputs.SkyRadiance * c_SkyIntensity * (1.0f - inputs.ProbeWeight);
	else if (inputs.Kind == Form::Screen)
		fallback = inputs.SkyRadiance * c_SkyIntensity;
	if (inputs.ScreenConfidence > 0.0f)
		return (fallback * c_SpecularOcclusion * (1.0f - inputs.ScreenConfidence) + inputs.ScreenLight * c_ScreenOcclusion) * c_SpecularColor;
	return fallback * c_SpecularColor * c_SpecularOcclusion;
}

float Compose(const Inputs& inputs, float diffuse, float specular)
{
	if (inputs.Kind == Form::Ambient)
		return diffuse;
	if (inputs.Kind == Form::Sky)
		return (diffuse + specular) * c_SkyIntensity;
	return diffuse + specular;
}

void Shade(const char* name, Inputs inputs)
{
	inputs.Kind = ChooseForm(inputs);
	const float diffuse = GatherDiffuse(inputs);
	const float specular = GatherSpecular(inputs);
	std::printf("%-8s form %d: diffuse %.3f specular %.3f total %.3f\n", name, static_cast<int>(inputs.Kind), diffuse, specular,
		Compose(inputs, diffuse, specular));
}

int main()
{
	Inputs probes;
	probes.Environment = true;
	probes.ProbeWeight = 0.75f;
	probes.ProbeIrradiance = 0.6f;
	probes.ProbeRadiance = 0.9f;
	probes.SkyIrradiance = 0.4f;
	probes.SkyRadiance = 0.5f;
	Shade("probes", probes);

	Inputs screen;
	screen.Environment = true;
	screen.ScreenLight = 0.4f;
	screen.ScreenConfidence = 0.5f;
	screen.SkyIrradiance = 0.4f;
	screen.SkyRadiance = 0.5f;
	Shade("screen", screen);

	Inputs sky;
	sky.Environment = true;
	sky.SkyIrradiance = 0.4f;
	sky.SkyRadiance = 0.5f;
	Shade("sky", sky);

	Shade("ambient", Inputs());
}
```

```text output-of="indirect-seam-toy.cpp"
probes   form 0: diffuse 0.288 specular 0.069 total 0.357
screen   form 1: diffuse 0.288 specular 0.066 total 0.354
sky      form 2: diffuse 0.144 specular 0.030 total 0.348
ambient  form 3: diffuse 0.080 specular 0.000 total 0.080
```

1. **Lines 33–39:** `ChooseForm` picks the form once, in the order probes, screen, sky, ambient.
2. **Lines 47–52:** each form builds its diffuse light; only the probes and screen forms scale the sky inside the gather.
3. **Lines 65–66:** a found reflection replaces the fallback by its confidence; the fallback keeps the specular occlusion.
4. **Line 75:** the sky-only form scales the composed sum, which the others do not.

The toy shows three things. The form is chosen once, before either gather runs. The gathers branch on the form and nothing else. The sky's intensity is applied in a different place in each form: inside the sum for probes and the screen, on the composed total for the sky alone.

:::example[Four pixels by hand]
Take :term[albedo]{id=albedo} 0.5, no metal, a :term[reflectance]{id=reflectance} of 0.1, a diffuse occlusion of 0.8, a specular occlusion of 0.6, a constant ambient of 0.2 and a sky intensity of 2. Light that a reflection found keeps an occlusion of 0.9 instead. The first pixel lies inside probe boxes with weight 0.75, so its sky share is 0.25. Its probes give :term[irradiance]{id=irradiance} 0.6 and :term[radiance]{id=radiance} 0.9, the sky gives irradiance 0.4 and radiance 0.5.

Diffuse is (0.6 + 0.4 × 2 × 0.25) × 0.5 × 0.9 = 0.36, and with the occlusion 0.288. The 0.9 is what the reflectance 0.1 leaves to diffuse light. Specular is (0.9 + 0.5 × 2 × 0.25) × 0.1 × 0.6 = 0.069. The sum is 0.357, the toy's first line.

The second pixel has no probes but a reflection with confidence 0.5 and premultiplied light 0.4. Its diffuse light is 0.4 × 0.5 × 0.9 × 2 × 0.8 = 0.288. Its specular light is (0.5 × 2 × 0.6 × 0.5 + 0.4 × 0.9) × 0.1 = 0.066, so the total is 0.354. The sky-only pixel gets (0.144 + 0.03) × 2 = 0.348, and the ambient pixel gets 0.2 × 0.5 × 0.8 = 0.08 with no specular light at all.
:::

## The fallback stack as an idea

The pattern in the diagram is a **fallback stack**: a list of light sources ordered from the most exact to the least. Each layer takes a weight between 0 and 1 and passes the remaining share down. Screen-space reflections are the most exact, because they show what is really on screen. Probes come next, then the sky, then the constant ambient.

A weight alone is not enough. Layers must also be stored so that a missing layer adds no black. The reflection texture holds the found light already multiplied by its confidence, which is called premultiplied storage, with the confidence beside it. A texel that found nothing holds 0 and 0, and the gather computes `fallback × (1 − confidence) + stored light`.

The reason shows in a small case. Take two neighboring texels: one found light 0.8 with confidence 1, the other found nothing. The sampler is bilinear, so a lookup halfway between them averages the stored values. Take a fallback of 1.0.

- Premultiplied: the stored values are (0.8, 1) and (0, 0). The average is (0.4, 0.5), and the pixel gets 1.0 × 0.5 + 0.4 = 0.9. That is right: half of the ray found 0.8, half did not, and 0.9 is the mean of 0.8 and 1.0.
- Not premultiplied: the stored colors are 0.8 and 0, with confidences 1 and 0. The average color is 0.4, and the pixel gets 1.0 × 0.5 + 0.4 × 0.5 = 0.7. The black of the empty texel was counted as light, so the edge of every reflection grows a dark fringe.

The same weighting joins probes and sky. The probes' combined weight `w` is the share of the pixel they cover, and the sky takes `1 − w`. Where a probe fades out at the edge of its box, `w` falls to 0 and the sky or the ambient takes over without a step. The shader's diffuse gather even keeps the constant ambient's share for that case: the test `A probe fading out into the constant ambient meets it without a step` checks it. [Premultiplied alpha](../light/clearcoat-transmission.md) is taught with the coat; the idea is the same.

## The real code, in the order data flows

The first piece is the struct and its forms. Note the four `#define` lines, which name the forms, and for the three fields at the end, which the global illumination stream added.

```slang src="Strata/shaders/Include/IndirectLight.slang#L9-L39"
// The forms of the base's indirect light, by what lights the pixel.
#define ST_INDIRECT_PROBES  0u // Reflection probes; the sky's share (or the constant ambient's) fills what they leave
#define ST_INDIRECT_SCREEN  1u // Screen-space reflections without probes; the sky's intensity scales inside the gathers
#define ST_INDIRECT_SKY     2u // The sky alone; its intensity (EnvironmentParams.x) scales the composed sum
#define ST_INDIRECT_AMBIENT 3u // The constant ambient alone: diffuse only

// What the gathers share. Streams add fields at the end (wave 8's plan: shared and additive).
struct IndirectInputs
{
	uint Form;                    // ST_INDIRECT_*
	bool Environment;             // EnvironmentParams.w > 0: the sky's image light; else the constant ambient
	float3 SpecularColor;         // The split sum's reflectance, f0 dfg.x + dfg.y, compensated for multiple scattering
	float3 Reflected;             // The view reflected about the shading normal
	float3 GeometricNormal;       // The primitive's normal, facing the viewer
	float DiffuseOcclusion;       // Material occlusion x screen-space occlusion
	float3 DiffuseOcclusionColor; // With the multi-bounce of AOParams.y
	float SpecularOcclusion;      // From DiffuseOcclusion (Lagarde), with the horizon fade; 1 in the ambient form
	ProbeLight Probes;            // The reflection probes at the surface (Weight 0 without probes)
	float4 ScreenReflection;      // rgb the reflected luminance x confidence, unexposed; a the confidence (0: none)
	float Sky;                    // 1 - Probes.Weight: the sky's (or the constant ambient's) share
	float3 SkyIrradiance;         // The sky's irradiance at the shading normal (0 without the environment)
	float3 SkyRadiance;           // The sky's prefiltered radiance along Reflected at the surface's roughness (0 without)
	float DiffuseWeight;          // The share of its diffuse light the surface scatters (glass: 1 - transmission)
	float ScreenReflectionOcclusion; // From the material's occlusion alone (Lagarde): what screen-space reflections keep
	// Global illumination joined (ReflectionParams.y; Include/GIField.slang): the field's weight at the surface (0 outside it, in
	// its fade between, and while it is pending or not joined), its irradiance over pi along the shading normal (absolute
	// luminance, the scene's intensity applied) and the share of the sky the surface sees (1 when not joined).
	float FieldWeight;
	float3 FieldIrradiance;
	float FieldOpen;
};
```

1. **Lines 10–13:** the four forms, from the probes down to the constant ambient.
2. **Lines 26–28:** the probes, the reflection and the sky's share are inputs, with weight and confidence inside them.
3. **Lines 36–38:** the field's three inputs come last, as the contract asks.

The second piece is `GetIndirectInputs`, the one function that fills the struct. The steps follow the order of dependence. Reflectance comes first, then probes, reflections and sky, then the form those choose, then the occlusion that the form needs.

```slang src="Strata/shaders/Scene/Forward.frag.slang#L186-L238"
IndirectInputs GetIndirectInputs(SurfaceData surface, float3 f0, float2 dfg, float NoV, float3 geometricNormal, float2 fragCoord,
	float diffuseOcclusion, float3 diffuseOcclusionColor, float diffuseWeight)
{
	IndirectInputs inputs;
	inputs.DiffuseOcclusion = diffuseOcclusion;
	inputs.DiffuseOcclusionColor = diffuseOcclusionColor;
	inputs.DiffuseWeight = diffuseWeight;
	inputs.GeometricNormal = geometricNormal;
	inputs.Reflected = reflect(-surface.View, surface.Normal);
	// Image-based lighting: diffuse irradiance plus split-sum specular (prefiltered radiance x environment BRDF, compensated
	// for multiple scattering); diffuse gets what specular leaves.
	inputs.SpecularColor = (f0 * dfg.x + dfg.y) * surface.SpecularEnergy;
	// Reflection probes whose boxes hold the surface light it first (Include/ReflectionProbes.slang); the sky, or the constant
	// ambient without an environment, fills in what they leave.
	inputs.Probes.Irradiance = float3(0.0);
	inputs.Probes.Radiance = float3(0.0);
	inputs.Probes.Weight = 0.0;
	if (u_ProbeCounts.x > 0u)
		inputs.Probes = EvaluateReflectionProbes(surface.Position, surface.Normal, inputs.Reflected, surface.Roughness);
	inputs.Sky = 1.0 - inputs.Probes.Weight;
	// Screen-space reflections replace the probes' and the sky's specular light by their confidence.
	inputs.ScreenReflection = float4(0.0);
#ifndef ST_FORWARD_TRANSPARENT
	if (u_Frame.ReflectionParams.x > 0.0)
	{
		inputs.ScreenReflection = u_ScreenReflections.SampleLevel(u_LinearClampSampler, fragCoord * u_Frame.ViewportSize.zw, 0.0);
		inputs.ScreenReflection.rgb /= u_Frame.TemporalParams.y;
	}
#endif
	inputs.Environment = u_Frame.EnvironmentParams.w > 0.0;
	inputs.SkyIrradiance = float3(0.0);
	inputs.SkyRadiance = float3(0.0);
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
	// The same on the material's occlusion alone, for what screen-space reflections found (exactly 1 without an occlusion map).
	inputs.ScreenReflectionOcclusion = clamp(pow(NoV + surface.Occlusion, exp2(-16.0 * surface.Roughness - 1.0)) - 1.0 + surface.Occlusion, 0.0, 1.0);
	inputs.FieldWeight = 0.0;
	inputs.FieldIrradiance = float3(0.0);
	inputs.FieldOpen = 1.0;
	return inputs;
}
```

1. **Line 197:** the split-sum reflectance with its :term[energy compensation]{id=energy-compensation}; diffuse takes what it leaves.
2. **Lines 203–205:** probes are evaluated only when the list is not empty; otherwise the sky's share stays 1.
3. **Lines 208–214:** the reflection is read only where reflections ran and never by transparent surfaces; the division by the pre-exposure returns the scene's own :term[luminance]{id=luminance}.
4. **Lines 225–226:** the form, in 0.7.0's order.
5. **Lines 229–233:** the specular occlusion fit, taught on [ambient occlusion](../indirect/ao.md), with the :term[horizon fade]{id=horizon-fade}; the ambient form takes 1; the second value uses the material's occlusion alone, for found light.

The third piece is the diffuse gather. Note how each form builds its irradiance and for the one multiplication that all forms share at the end.

```slang src="Strata/shaders/Include/IndirectLight.slang#L53-L82"
float3 GatherIndirectDiffuse(IndirectInputs inputs, SurfaceData surface)
{
	float3 diffuse;
	if (inputs.Form == ST_INDIRECT_PROBES)
	{
		// The probes' captures hold the scene's luminance (their intensities applied); the sky's share is scaled here.
		float3 irradiance = inputs.Probes.Irradiance + (inputs.Environment ? inputs.SkyIrradiance * u_Frame.EnvironmentParams.x * inputs.Sky : float3(0.0));
		diffuse = irradiance * surface.Albedo * (1.0 - surface.Metallic) * (1.0 - inputs.SpecularColor);
		// The constant ambient's share as the constant ambient lights alone (diffuse only), so that a probe fading out meets it
		// without a step at its box's faces.
		if (!inputs.Environment)
			diffuse += u_Frame.AmbientColor.rgb * inputs.Sky * surface.Albedo * (1.0 - surface.Metallic);
	}
	else if (inputs.Form == ST_INDIRECT_SCREEN)
	{
		// Without the sky the constant ambient lights the diffuse part, as it does without reflections.
		diffuse = inputs.Environment ? inputs.SkyIrradiance * surface.Albedo * (1.0 - surface.Metallic) * (1.0 - inputs.SpecularColor) * u_Frame.EnvironmentParams.x
			: u_Frame.AmbientColor.rgb * surface.Albedo * (1.0 - surface.Metallic);
	}
	else if (inputs.Form == ST_INDIRECT_SKY)
	{
		diffuse = inputs.SkyIrradiance * surface.Albedo * (1.0 - surface.Metallic) * (1.0 - inputs.SpecularColor);
	}
	else
	{
		// Constant ambient without an environment map: diffuse only, modulated by material occlusion.
		diffuse = u_Frame.AmbientColor.rgb * surface.Albedo * (1.0 - surface.Metallic);
	}
	return ScatterDiffuse(diffuse, inputs.DiffuseWeight) * inputs.DiffuseOcclusionColor;
}
```

1. **Lines 59–60:** the probes' irradiance plus the sky's share, times albedo, the non-metal part and what specular leaves.
2. **Lines 63–64:** without an environment, the constant ambient fills the share the probes leave.
3. **Lines 69–70:** the screen form takes the sky, scaled by its intensity inside the gather, or the ambient.
4. **Line 81:** every form ends with the glass scattering and the occlusion color.

The fourth is the specular gather. Look at the two returns: the pixel with a reflection and the pixel without one.

```slang src="Strata/shaders/Include/IndirectLight.slang#L90-L107"
float3 GatherIndirectSpecular(IndirectInputs inputs)
{
	float3 fallback;
	if (inputs.Form == ST_INDIRECT_PROBES)
		fallback = inputs.Probes.Radiance + inputs.SkyRadiance * (inputs.Environment ? u_Frame.EnvironmentParams.x * inputs.Sky : 0.0);
	else if (inputs.Form == ST_INDIRECT_SCREEN)
		fallback = inputs.SkyRadiance * (inputs.Environment ? u_Frame.EnvironmentParams.x : 0.0);
	else if (inputs.Form == ST_INDIRECT_SKY)
		fallback = inputs.SkyRadiance;
	else
		return float3(0.0); // The constant ambient lights the diffuse part only
	if (inputs.ScreenReflection.a > 0.0)
	{
		return (fallback * inputs.SpecularOcclusion * (1.0 - inputs.ScreenReflection.a) + inputs.ScreenReflection.rgb * inputs.ScreenReflectionOcclusion)
			* inputs.SpecularColor;
	}
	return fallback * inputs.SpecularColor * inputs.SpecularOcclusion;
}
```

1. **Lines 93–100:** each form's fallback light; the ambient form has no specular light and returns 0.
2. **Lines 101–105:** with a reflection, the fallback keeps its occlusion and loses its confidence, and the found light keeps only the material's occlusion.
3. **Line 106:** without a reflection, the expression of the forms before.

The fifth is the compose step, short enough to read whole. The field has its own gather, `GatherIndirectField`: the field's irradiance on the diffuse albedo, under the diffuse occlusion without the multi-bounce fit, because the field's own bounce is the real one. Its weight and its join belong to [the field's cascades](../indirect/gi-cascades.md).

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

The sixth piece is the end of `ShadeLitSurface`, in two parts. The first computes the occlusion, calls `GetIndirectInputs` and joins the field. Find the two debug views that keep one kind of light alone.

```slang src="Strata/shaders/Scene/Forward.frag.slang#L407-L451"
float diffuseOcclusion = surface.Occlusion * screenOcclusion;
if (lightingView == ST_LIGHTING_VIEW_AMBIENT_OCCLUSION)
	return float3(diffuseOcclusion);
// Multi-bounce (AOParams.y): occluded corners keep the light their walls, of the surface's diffuse albedo, reflect into
// them (Include/AmbientOcclusionFit.slang). Diffuse light only; specular occlusion keeps the visibility.
float3 diffuseOcclusionColor = u_Frame.AOParams.y > 0.0 ? AOMultiBounce(diffuseOcclusion, surface.Albedo * (1.0 - surface.Metallic))
	: float3(diffuseOcclusion);
float3 surfaceGeometricNormal = normalize(v_Normal) * (st_FrontFacing ? 1.0 : -1.0);
IndirectInputs indirectInputs = GetIndirectInputs(surface, f0, dfg, NoV, surfaceGeometricNormal, st_FragCoord.xy, diffuseOcclusion,
	diffuseOcclusionColor, diffuseWeight);
// The base's image-based light (or constant ambient), which the clear coat covers below.
float3 indirect;
#ifdef ST_FORWARD_FIELD
bool globalIlluminationView = lightingView == ST_LIGHTING_VIEW_GLOBAL_ILLUMINATION || lightingView == ST_LIGHTING_VIEW_OPEN_SHARE;
if (u_Frame.ReflectionParams.y > 0.0 || globalIlluminationView)
{
	// The field, sampled at this one place for the join and the GI views (its gather's loops compiled in once) and only
	// where one of them reads it, after today's inputs as the join always sampled it.
	float openShare;
	float4 field = SampleIrradianceField(u_Samplers[0], surface.Position, surfaceGeometricNormal, surface.Normal, surface.View, true, openShare);
	if (globalIlluminationView)
		return ShadeGlobalIlluminationView(lightingView, surface, field, openShare, surfaceGeometricNormal, f0, dfg, NoV, diffuseOcclusion, diffuseWeight);
	// Global illumination joined (the scene asked, the field is used; .z the intensity): inside the field its diffuse light
	// replaces today's (box probes, the sky or the constant ambient), blended over the field's fade; specular stays today's.
	// Where the field's weight is 0 this is today's light exactly (x * 1 and + 0).
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
}
else
#endif
if (lightingView == ST_LIGHTING_VIEW_SPECULAR)
	indirect = ComposeIndirect(indirectInputs, float3(0.0), GatherIndirectSpecular(indirectInputs));
else if (lightingView == ST_LIGHTING_VIEW_DIFFUSE)
	indirect = ComposeIndirect(indirectInputs, GatherIndirectDiffuse(indirectInputs, surface), float3(0.0));
else
	indirect = ComposeIndirect(indirectInputs, GatherIndirectDiffuse(indirectInputs, surface), GatherIndirectSpecular(indirectInputs));
```

1. **Line 407:** the material's occlusion times the screen's is the diffuse occlusion.
2. **Lines 412–413:** the multi-bounce fit applies only where its setting is above 0.
3. **Lines 419–445:** the field's code is compiled only into the shader variants that carry the field; the others start at line 446.
4. **Lines 441–442:** the field joins only where the scene asked: diffuse is today's light times one minus the weight, plus the field's gather times the weight.
5. **Lines 446–451:** the **Specular** and **Diffuse** views compose one kind of light alone; every other frame adds both, as before.

The second part gives the clear coat its own image light. Look at what the coat does not read.

```slang src="Strata/shaders/Scene/Forward.frag.slang#L453-L471"
float3 emitted = lightingView == ST_LIGHTING_VIEW_INDIRECT || IsLightKindView(lightingView) ? float3(0.0) : surface.Emissive;
if (coat.Strength > 0.0)
{
	// The coat reflects the probes', the sky's or the ambient light by its prefiltered Fresnel (split sum, as the base), and
	// the light under it, the base's and the emission, loses what it reflects.
	float coatReflectance = coat.Strength * (c_ClearcoatF0 * coatDFG.x + coatDFG.y) * coat.SpecularEnergy;
	float3 coatReflected = reflect(-surface.View, coat.Normal);
	float3 coatRadiance = SampleSpecularLight(surface.Position, coat.Normal, coatReflected, coat.Roughness, indirectInputs.Environment);
	float coatOcclusion = clamp(pow(coatNoV + diffuseOcclusion, exp2(-16.0 * coat.Roughness - 1.0)) - 1.0 + diffuseOcclusion, 0.0, 1.0)
		* GetFrameHorizonFade(coatReflected, indirectInputs.GeometricNormal);
	if (lightingView == ST_LIGHTING_VIEW_DIFFUSE)
		indirect = indirect * (1.0 - coatReflectance);
	else
		indirect = indirect * (1.0 - coatReflectance) + coatRadiance * coatReflectance * coatOcclusion;
	emitted *= 1.0 - ClearcoatFresnel(coat, coatNoV);
}
color += indirect;
color += emitted;
return color;
```

1. **Line 453:** the emission is dropped in the indirect view and in the views of one kind of light.
2. **Lines 458–462:** the coat takes its own image light from the probes, the sky or the ambient, with its own occlusion and horizon fade.
3. **Lines 463–466:** the base light loses what the coat reflects, then the coat's light is added; the **Diffuse** view keeps none of the coat's light.

The last piece is the CPU's frame order: three stages before the opaque pass, and what a failed field frame does.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L3663-L3698"
if (postProcess.AmbientOcclusion)
{
	gpuTimer.Next(gpuStages.AO);
	commandList->beginMarker("AmbientOcclusion");
	RenderAmbientOcclusion(commandList, postProcess);
	commandList->endMarker();
}
if (m_GIFrame)
{
	gpuTimer.Next(gpuStages.RadianceCascades);
	commandList->beginMarker("GlobalIllumination");
	if (!RecordGlobalIllumination(commandList))
	{
		// Reported once while it lasts (a degraded frame keeps the error); the voxels did not get the frame's work, so
		// it is neither settled nor done (the next frame starts the clipmap over).
		degraded = true;
		m_Stats.GlobalIlluminationPending = true;
		m_Stats.GlobalIlluminationSettled = false;
		// The forward pass reads no field this frame (a newer version of its constants, which the draws below bind; the
		// buffer's versions count this second write: c_MaxGIFieldConstantWrites).
		m_GIFieldConstants.FieldSize.w = 0.0f;
		commandList->writeBuffer(m_GIFieldConstantBuffer, &m_GIFieldConstants, sizeof(m_GIFieldConstants));
	}
	commandList->endMarker();
}
if (!m_ReflectionProbeConversions.empty() || m_ReflectionFrame)
{
	gpuTimer.Next(gpuStages.Reflections);
	commandList->beginMarker("Reflections");
	ConvertReflectionProbes(commandList);
	if (m_ReflectionFrame && m_SpatialReflectionResources)
		TraceSpatialReflections(commandList, postProcess);
	else if (m_ReflectionFrame)
		TraceScreenReflections(commandList, postProcess);
	commandList->endMarker();
}
```

1. **Lines 3663–3669:** occlusion has its own stage and runs only when the frame asks for it.
2. **Lines 3674–3685:** when the field's frame fails, the frame is degraded and the field's constants are written again with `FieldSize.w` set to 0, so the opaque pass reads no field.
3. **Lines 3692–3696:** probe conversions run first, then one of two reflection traces.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| A separate deferred ambient pass | Deferred renderers that light the screen after the geometry pass | The indirect light of every source in one place, with no cost per mesh | A full-screen pass and a target for the surface data, which the forward pass of Strata does not store |
| One target per term, composed later | Engines that debug or filter each term apart | Each term could be filtered and shown alone | A target for each term, and a bit-exact old image would be lost, because the old path adds in one step |
| A branch per feature in the shader | Many small engines | Simple code for one feature | Branches that multiply, and a new feature would change the arithmetic of the old ones |

## How it is tested

The suite `GPU.SceneRenderer.ReflectionProbes` holds the tests of the probe layer. The test `A scene without reflection probes samples a one-slot black cube array and makes nothing else` checks the dummy. The tests `Two overlapping probes blend by their weights, the stronger over the weaker` and `A probe fading out into the constant ambient meets it without a step` check the weights.

The suite `GPU.SceneRenderer.Lighting` renders :term[image-based lighting]{id=image-based-lighting}: the :term[white furnace test]{id=white-furnace-test} `A white furnace keeps a rough metal's light at every roughness` checks that the specular gather keeps its energy. All tests of both suites need a GPU. Run one suite with the test program's filter, for example `StrataTests.exe --test-suite=GPU.SceneRenderer.ReflectionProbes`.

## Changing it safely

- **Add a field at the end of the struct and set it in `GetIndirectInputs`.** Its default must be a value that adds nothing, so that every old pixel keeps its bits.
- **Keep the order of the forms.** The form is the first branch of every gather, and 0.7.0's order is probes, then reflections, then sky, then ambient.
- **Give a new pass a GPU stage.** `AGENTS.md` asks for a stage registered with its module, and the pass runs before the opaque pass.
- **Keep the transparent variant free of reflections.** The reflection read sits inside `#ifndef ST_FORWARD_TRANSPARENT`, so transparent surfaces never read the texture.
- **Check with the debug views.** The indirect view keeps only the indirect light; use it before and after a change.

## Summary

- A pixel's form is probes if the probes' weight is above 0, else screen if a reflection was found, else sky if there is an environment, else ambient.
- Each gather reads the inputs and applies its form's expression; compose scales the sky-only sum by the sky's intensity and keeps the ambient diffuse only.
- A fallback layer takes a premultiplied weight so a texel that found nothing adds no black.
- A new field goes at the end of the inputs with a default that adds nothing, so the old image keeps every bit.
- The occlusion, field and reflection passes run before the opaque pass, and the CPU sets the probes' count, the reflections' flag and the sky's flag.

## Check yourself

1. A pixel lies outside every probe box. Its reflection has confidence 0.3, and the scene has no sky map. Which form does it take, and what lights its diffuse part?

   :::answer{tests="choose-form"}
   The form is the screen form: the probes' weight is 0, and the reflection's confidence is above 0. Without an environment its diffuse part is the constant ambient times the albedo, times the diffuse occlusion color. The sky's irradiance is 0 in this pixel.
   :::

2. In the toy's screen form, the reflection is fully found: confidence 1, premultiplied light 0.7. What are the specular and the total light, with the other numbers of the example?

   :::answer{tests="compute-gathers"}
   The fallback is multiplied by 1 − 1 = 0, so it vanishes. Specular is 0.7 × 0.9 × 0.1 = 0.063, and the specular occlusion 0.6 does not touch the found light. The diffuse part stays 0.288, so the total is 0.351.
   :::

3. Two texels hold (0.6, 1) and (0, 0). A lookup halfway between them is used with a fallback of 1.0. What does premultiplied storage give, and what does storage that is not premultiplied give?

   :::answer{tests="explain-premultiplied"}
   Premultiplied: the average is (0.3, 0.5), and the pixel gets 1.0 × 0.5 + 0.3 = 0.8. Not premultiplied: the average color is 0.3 with confidence 0.5, so the pixel gets 0.5 + 0.15 = 0.65. The empty texel's black darkens the edge by 0.15.
   :::

4. A coated floor reflects a bright wall. Which pass could have shown the wall in the coat, and why does the coat not show it?

   :::answer{tests="trace-frame"}
   The reflection trace runs in the reflections stage, before the opaque pass, and its result sits at slot 18. The coat does not read that slot: `SampleSpecularLight` takes only the probes, the sky or the ambient. So the coat shows the probes' room, not the wall.
   :::

5. Why is it safe that a new field of the inputs is 0 where its feature is off?

   :::answer{tests="add-field"}
   Adding 0 to a finite value returns the same bits, and multiplying by 1 does too. The old pixels therefore keep their exact bits, and the default image does not change.
   :::

## Exercises

1. **Basic.** Trace it yourself. For one pixel, find which form `GetIndirectInputs` chooses, and find where the CPU sets each value the choice reads: the probes' weight, the first value of `ReflectionParams` and the last of `EnvironmentParams`.

   :::answer[Worked solution]{tests="trace-frame,choose-form"}
   The choice is at lines 224 to 226 of `Strata/shaders/Scene/Forward.frag.slang`, and the forms are defined at lines 10 to 13 of `Strata/shaders/Include/IndirectLight.slang`. The probes' weight comes from `EvaluateReflectionProbes`, whose count `UploadReflectionProbes` writes in `Strata/src/Strata/Renderer/SceneRendererReflectionProbes.cpp` after `GatherReflectionProbes` chose the probes. `ReflectionParams.x` is set in `SceneRenderer::RenderFrame` from `m_ReflectionFrame`. `EnvironmentParams.w` is set to 1 in `SceneRenderer::UpdateEnvironment` and starts at 0.
   :::

2. **Medium.** Add a field `Bounce` for a new term at the end of a toy's inputs. Add it in the compose step, and show that the three old forms keep their exact bits while it is 0.

   :::answer[Worked solution]{tests="add-field" solution="sketches/indirect-seam-extend.cpp"}
   The sketch below appends the field with the default 0 and adds it after the old compose. It compares the old and new results with `memcmp`, which sees bits, not values.

   ```cpp sketch="indirect-seam-extend.cpp"
   // Adds a new term to a toy's inputs at the end and checks that every old pixel keeps its exact bits.
   #include <cstdio>
   #include <cstring>

   enum class Form
   {
   	Probes,
   	Sky,
   	Ambient
   };

   struct Inputs
   {
   	Form Kind = Form::Probes;
   	float Diffuse = 0.0f;
   	float Specular = 0.0f;
   	float Bounce = 0.0f; // The new field, last: what the old code never knew is 0
   };

   float ComposeBefore(const Inputs& inputs)
   {
   	if (inputs.Kind == Form::Ambient)
   		return inputs.Diffuse;
   	if (inputs.Kind == Form::Sky)
   		return (inputs.Diffuse + inputs.Specular) * 2.0f;
   	return inputs.Diffuse + inputs.Specular;
   }

   float ComposeAfter(const Inputs& inputs)
   {
   	return ComposeBefore(inputs) + inputs.Bounce;
   }

   bool SameBits(float a, float b)
   {
   	return std::memcmp(&a, &b, sizeof(float)) == 0;
   }

   int main()
   {
   	const Form forms[] = { Form::Probes, Form::Sky, Form::Ambient };
   	int same = 0;
   	for (const Form form : forms)
   	{
   		Inputs inputs;
   		inputs.Kind = form;
   		inputs.Diffuse = 0.288f;
   		inputs.Specular = 0.069f;
   		same += SameBits(ComposeBefore(inputs), ComposeAfter(inputs)) ? 1 : 0;
   	}
   	std::printf("forms with the same bits while Bounce is 0: %d of 3\n", same);

   	Inputs lit;
   	lit.Diffuse = 0.288f;
   	lit.Specular = 0.069f;
   	lit.Bounce = 0.05f;
   	std::printf("with Bounce 0.05: %.3f instead of %.3f\n", ComposeAfter(lit), ComposeBefore(lit));
   }
   ```

   ```text output-of="indirect-seam-extend.cpp"
   forms with the same bits while Bounce is 0: 3 of 3
   with Bounce 0.05: 0.407 instead of 0.357
   ```

   1. **Line 17:** the new field comes last, with a default that adds nothing.
   2. **Line 31:** the new compose is the old one plus the field.
   3. **Lines 34–36:** `memcmp` compares the :term[bytes]{id=byte} of two floats, so it sees bits.

   The first line shows 3 of 3 forms unchanged; the second shows that a `Bounce` other than 0 does change the light.
   :::

## Where it lives in Strata

- `Strata/shaders/Include/IndirectLight.slang`: `IndirectInputs`, the four forms, `GatherIndirectDiffuse`, `GatherIndirectSpecular`, `GatherIndirectField`, `ComposeIndirect`.
- `Strata/shaders/Scene/Forward.frag.slang`: `GetIndirectInputs`, `SampleSpecularLight` and `ShadeLitSurface`.
- `Strata/src/Strata/Renderer/SceneRenderer.cpp`: `SceneRenderer::RenderFrame` (the frame's order) and `SceneRenderer::UpdateEnvironment`.
- `Strata/src/Strata/Renderer/SceneRendererReflectionProbes.cpp`: `SceneRenderer::UploadReflectionProbes`.
- `StrataTests/src/Renderer/GPUReflectionProbeTests.cpp` and `StrataTests/src/Renderer/GPUSceneLightingTests.cpp`: the suites of this page.

## Further reading

- Sébastien Lagarde and Charles de Rousiers, "Moving Frostbite to Physically Based Rendering" (course notes, 2014; intermediate): the specular occlusion the seam uses.
- Matt Pharr, Wenzel Jakob and Greg Humphreys, "Physically Based Rendering" (book; intermediate): why light is gathered per surface point.
- Thomas Porter and Tom Duff, "Compositing Digital Images" (paper, 1984; intermediate): premultiplied color.
