---
id: light/clearcoat-transmission
title: "Transparency, clear coat and glass"
description: "How Strata draws surfaces that are layered or let light through: blending, the clear coat, glass and the copy of the image that glass bends."
kind: internals
size: L
tracks: [E]
needs: [light/energy, draw/batching]
time: 70
learn:
  - id: blend-order
    text: explain why blended surfaces need an order and why premultiplied alpha lets layers combine
  - id: coat-weight
    text: compute how much light a clear coat reflects at a given angle and how much reaches the base
  - id: glass-path
    text: trace how a glass pixel finds the color behind it and tints it
  - id: copy-limits
    text: name what the scene-color copy cannot show and why Strata accepts it
  - id: author-glass
    text: choose coat and glass values for a glossy base and a colored liquid
since: 0.6.0
status: final
---

Some surfaces are not one opaque layer. A car has paint under a gloss layer, a window bends the street behind it, and a ghost is only partly there. This page covers how Strata draws these: blending for partial coverage, the clear coat for a second layer on top of a surface, and glass for a surface that passes light through. It does not cover the order in which blended surfaces are sorted, which is the job of [batching](../draw/batching.md), or the coat's behavior under rectangle lights, which belongs to [area lights](../light/area-lights.md).

## The problem and how engines solve it

Start with a wooden table with a coat of gloss. Look straight down and you see the grain. Tilt your head until a window reflects in the surface and the grain fades behind a bright mirror image. Two layers act at once: the gloss layer mirrors some light, and the wood below scatters the rest. One lobe of light cannot describe both, because the gloss layer has its own smoothness; the wood can be rough and dull while the gloss layer is a mirror.

Now take a glass of water. You see the table behind it, shifted and bent, and tinted green near the thick parts. The glass reflects a little of the room as well. A third case is a ghost or a smoke puff: a surface that covers only some of a pixel and lets the world show through the rest.

Engines meet each case with a different technique, and each costs something.

- **Layered materials.** A second specular lobe over the base lobe, in the style of the research on layered surfaces cited at the end, with the light the top layer reflects taken from the base. It costs a second lobe per light and per probe, but it needs nothing from the rest of the frame.
- **Screen-space glass.** The glass pixel computes where a bent ray would leave the glass, then reads the image that was already drawn at that place. It costs one copy of the image and shows only what the screen holds.
- **Ray-traced glass.** A ray travels through the glass and out the other side, and finds what it hits, even a second sheet of glass. It shows the most and needs a structure that the :term[graphics processing unit]{id=gpu} (GPU) can search for hits, with a cost per ray.
- **Blending.** A surface mixes its color with the image under it by its alpha, the coverage from 0 to 1. It costs an order: the result depends on which surface came first.

Strata takes the first technique for coats, the second for glass and blending for partial coverage. It does not trace rays. The table near the end of the page lists the choices and what each would gain and lose.

## Where the pieces run in a frame

A frame draws opaque surfaces first, then the sky, then the surfaces that depend on the image so far. Glass reads a copy of that image, so the copy must exist before glass is drawn, and the copy must not hold anything glass will draw. The diagram shows the order.

```mermaid caption="The frame's passes that matter here. The sky comes before the copy, the copy before glass, and glass before the blended surfaces." alt="A left to right chain of boxes: depth prepass, opaque forward pass, sky, scene-color copy, glass, blended surfaces, with a note that the copy is read by glass."
flowchart LR
    P["Prepass: opaque depth"] --> O["Opaque forward pass"]
    O --> S["Sky"]
    S --> C["Scene-color copy: Effects/SceneColorCopy.comp"]
    C --> G["Glass: transmissive materials"]
    G --> B["Blended surfaces, far to near"]
    C -. "read at SRV 19" .-> G
```

The files that own the pieces are few. `Strata/shaders/Scene/Forward.frag.slang` shades coats and glass, and `Strata/shaders/Include/PBR.slang` holds the coat's math. `Strata/src/Strata/Renderer/SceneRendererGlass.cpp` makes the copy, and `Strata/src/Strata/Renderer/SceneRenderer.cpp` records the draws. `Strata/src/Strata/Renderer/MaterialData.cpp` turns a material's fields into the flags and numbers the :term[shader]{id=shader} reads. All of this runs on the :term[main thread's]{id=main-thread} render submission and the GPU, as the rest of the :term[renderer]{id=renderer} does.

## Blending and premultiplied alpha

Before glass, take the plainest case, a surface with an alpha of 0.5. Half of its color should show and half of what lies under it. The rule is one line: the new pixel is the surface's color times alpha, plus the old pixel times one minus alpha. The graphics card does this in fixed hardware, with no shader code, when you enable blending.

:::example
Work one example by hand with a white wall and two sheets of colored plastic, each covering half a pixel. Write colors as red, green and blue between 0 and 1. The wall is $(1, 1, 1)$, the red sheet is $(1, 0, 0)$ and the blue sheet is $(0, 0, 1)$. Draw red first: $(1,0,0)\times 0.5 + (1,1,1)\times 0.5 = (1, 0.5, 0.5)$. Draw blue next: $(0,0,1)\times 0.5 + (1, 0.5, 0.5)\times 0.5 = (0.5, 0.25, 0.75)$.

Swap the order: blue first gives $(0.5, 0.5, 1)$. Red next gives $(1,0,0)\times 0.5 + (0.5,0.5,1)\times 0.5 = (0.75, 0.25, 0.5)$. The two orders differ: purple-blue against purple-red. That is the first rule of transparency. Blended surfaces do not commute, so an engine must draw them from far to near, which [batching](../draw/batching.md) sorts.
:::

The second rule is why blended surfaces come after opaque ones. A blended surface needs the finished color under it, and an opaque surface behind it must already be in the image. If you drew a blended sheet first, an opaque wall drawn later would cover it completely, because the wall writes its color without mixing. So Strata draws the opaque surfaces and the sky, and then the blended ones, in the transparent pass.

The sum has a flaw when you need to combine sheets before you know what lies under them. Mixing red and blue into one sheet needs the straight colors and a rule for the combined alpha, and the formula is awkward. The fix is to store each layer with its color already multiplied by its alpha.

**Premultiplied alpha** stores a layer's color times its alpha beside the alpha itself, so two layers combine with one multiply and one add.

For the example the stored values are these.

- Red at 0.5 is $(0.5, 0, 0)$ with alpha $0.5$, and blue is $(0, 0, 0.5)$ with alpha $0.5$.
- The top layer over the bottom layer is the top color plus the bottom color times $(1 - a_{top})$, and the same for alpha.
- Blue over red gives $(0, 0, 0.5) + (0.5, 0, 0) \times 0.5 = (0.25, 0, 0.5)$ with alpha $0.5 + 0.5 \times 0.5 = 0.75$.
- That pair over the white wall, stored as $(1,1,1)$ with alpha 1, gives $(0.25, 0, 0.5) + (1,1,1)\times 0.25 = (0.5, 0.25, 0.75)$.

The answer matches the one-at-a-time result. Layers can be grouped in any way, as long as their order stays.

In Strata the hardware does the multiplying: the blend state of the transparent pass takes the shader's color times its alpha, plus the old pixel times one minus alpha. The shader writes a straight color and the hardware makes it premultiplied as it blends. The `Blend` alpha mode of a material enables this for its surfaces; `Opaque` and `Mask` surfaces never blend.

The image's alpha channel carries one more number. Every opaque writer stores alpha 1. Each blended surface multiplies the stored alpha by $1 - a$, so after two sheets of 0.5 the channel holds 0.25, the share of the pixel that no blended surface covered. Glass is not blended and writes alpha 1, as opaque writers do. The temporal anti-aliasing reads this channel, and [the temporal anti-aliasing page](../image/taa.md) explains why.

The quote shows the blend state. Look at the four factors: the color uses the shader's alpha and its inverse, and the alpha channel uses zero for the source.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L2622-L2632"
depth.setDepthWriteEnable(false).setDepthFunc(nvrhi::ComparisonFunc::GreaterOrEqual);
// The HDR target's alpha becomes the transmittance through the blended surfaces, the product of their 1 - alpha
// (1 where there are none: everything before writes 1), which the TAA reads as how much of a pixel has no motion
// of its own.
nvrhi::BlendState::RenderTarget blend;
blend.setBlendEnable(true)
	.setSrcBlend(nvrhi::BlendFactor::SrcAlpha)
	.setDestBlend(nvrhi::BlendFactor::InvSrcAlpha)
	.setSrcBlendAlpha(nvrhi::BlendFactor::Zero)
	.setDestBlendAlpha(nvrhi::BlendFactor::InvSrcAlpha);
desc.renderState.blendState.setRenderTarget(0, blend);
```

1. **Line 2622:** blended surfaces test depth but never write it, so they do not hide each other or the surfaces behind them.
2. **Lines 2628–2629:** the color factors, source alpha and one minus source alpha: the sums above.
3. **Lines 2630–2631:** the alpha channel keeps only the old alpha times $1 - a$, since the new surface adds none of its own.

## The contract

Callers and authors of materials can rely on these rules.

- A material is glass when its `Transmission` is above 0 and it is not `Unlit`. It is drawn as glass whatever its alpha mode.
- A clear coat exists when `Clearcoat` is above 0 and the material is not `Unlit`. A coat of 0 costs next to nothing: the shader's branch on the flag is the same for a whole draw.
- Glass is not in the :term[depth prepass]{id=depth-prepass}. It gets no ambient occlusion, casts no shadow, and the scene-color copy holds no glass. The reason: the prepass's depth would hide what lies behind the glass from the copy.
- Glass shows only what was drawn before it: opaque surfaces and the sky. Another sheet of glass behind it does not show, and neither do blended surfaces behind it.
- Glass writes depth, entity ids and motion, as an opaque surface does. The editor can pick it and the temporal anti-aliasing can follow it.
- The copy is made in a frame that draws glass, and in a frame whose screen-space reflections ask for it; otherwise it is skipped. Without it a sheet would show black, so a frame that cannot make it reports an error.

## A toy version

The toy blends two half-covering layers over a white wall in both orders. It then combines the pair first, with premultiplied colors, and tracks the alpha channel's running product.

```cpp sketch="light-clearcoat-transmission-toy.cpp"
#include <cstdio>

// A layer as the artist describes it: the color of the surface and how much of the pixel it covers.
struct Layer
{
	float R;
	float G;
	float B;
	float A;
};

// The same layer with its color already multiplied by its coverage.
struct Premultiplied
{
	float R;
	float G;
	float B;
	float A;
};

Premultiplied Premultiply(const Layer& layer)
{
	return { layer.R * layer.A, layer.G * layer.A, layer.B * layer.A, layer.A };
}

// What shows when `top` lies over `bottom`: all of the top, and the share of the bottom the top lets through.
Premultiplied Over(const Premultiplied& top, const Premultiplied& bottom)
{
	const float keep = 1.0f - top.A;
	return { top.R + bottom.R * keep, top.G + bottom.G * keep, top.B + bottom.B * keep, top.A + bottom.A * keep };
}

void Print(const char* label, const Premultiplied& value)
{
	std::printf("%-28s r %.3f  g %.3f  b %.3f  a %.3f\n", label, value.R, value.G, value.B, value.A);
}

int main()
{
	const Premultiplied white = Premultiply({ 1.0f, 1.0f, 1.0f, 1.0f });
	const Premultiplied red = Premultiply({ 1.0f, 0.0f, 0.0f, 0.5f });
	const Premultiplied blue = Premultiply({ 0.0f, 0.0f, 1.0f, 0.5f });

	// Drawing one layer at a time, as the transparent pass does: the order changes the result.
	Print("red, then blue, over white", Over(blue, Over(red, white)));
	Print("blue, then red, over white", Over(red, Over(blue, white)));

	// Premultiplied layers also combine first: blue over red, then the pair over white, gives the first line again.
	const Premultiplied pair = Over(blue, red);
	Print("the pair alone", pair);
	Print("the pair over white", Over(pair, white));

	// Strata's HDR alpha starts at 1 and each blended layer multiplies it by 1 - a: the share of the pixel left uncovered.
	float transmittance = 1.0f;
	transmittance *= 1.0f - 0.5f;
	transmittance *= 1.0f - 0.5f;
	std::printf("transmittance after two layers: %.3f\n", transmittance);
	return 0;
}
```

```text output-of="light-clearcoat-transmission-toy.cpp"
red, then blue, over white   r 0.500  g 0.250  b 0.750  a 1.000
blue, then red, over white   r 0.750  g 0.250  b 0.500  a 1.000
the pair alone               r 0.250  g 0.000  b 0.500  a 0.750
the pair over white          r 0.500  g 0.250  b 0.750  a 1.000
transmittance after two layers: 0.250
```

1. **Line 23:** the stored color is the straight color times the coverage.
2. **Lines 29–30:** the top layer plus the share of the bottom layer that it lets through, for color and alpha alike.
3. **Lines 45–46:** the same two layers in both orders, drawn one at a time.
4. **Lines 49–51:** the pair combined first gives the one-at-a-time result.
5. **Lines 54–57:** the alpha channel's running product, as the image's alpha holds it.

The first two lines of output are the by-hand results of the section above. The third pair shows that grouping the layers first gives the same pixel, and the last line shows the alpha channel of 0.25. The toy omits depth: a real pass must also test each sheet against the opaque depth, and it must sort.

## The clear coat in code

**Clear coat** is a thin transparent layer over a surface with its own specular lobe, roughness and normal.

Think of the gloss layer on the table. Light that meets the gloss layer does one of two things: the gloss layer mirrors a share of it, and the rest passes into the wood. The share depends on the angle. Strata uses the :term[Fresnel]{id=fresnel} curve of a surface with an `IOR` of 1.5, the value of glass and clear plastic. At head-on view the curve gives 4 %, the base value $F_0 = 0.04$ that [the reflectance page](reflectance.md) derives.

The curve is the same one the base uses. Strata approximates it with a fifth power:

$$F = s \left( 0.04 + 0.96 \, (1 - \cos\theta)^5 \right)$$

$s$ is the coat's strength from 0 to 1. $\theta$ is the angle between the view and the half vector, and $\cos\theta$ is their :term[dot product]{id=dot-product}. $F$ is the share of light the coat reflects, between 0 and 1. A strength of 1 at head-on view gives $F = 0.04$; at $\cos\theta = 0.5$ the fifth power is $0.5^5 = 0.03125$ and $F = 0.04 + 0.96 \times 0.03125 = 0.07$; at $\cos\theta = 0.1$ it is $0.9^5 = 0.59$ and $F = 0.607$. At a grazing angle the gloss layer is a mirror, and the base is nearly hidden.

At the limits the formula behaves: with $s = 0$ the coat reflects nothing and takes nothing. With $\cos\theta = 1$ it reflects the 4 % of a plain non-metal. With $\cos\theta = 0$ it reflects everything, as every surface does at a perfect graze.

The quote holds the coat's data and its Fresnel function. The coat has its own roughness and normal, so a coat can be a mirror over a rough base, or tilt its highlight with a :term[normal map]{id=normal-map}.

```cpp src="Strata/shaders/Include/PBR.slang#L159-L174"
struct ClearcoatData
{
	float Strength;  // 0: no coat
	float Roughness; // Perceptual
	float3 Normal;
	float SpecularEnergy; // GetSpecularEnergy of the coat's lobe (F0 c_ClearcoatF0) at its NoV and roughness
};

static const float c_ClearcoatF0 = 0.04;

// The coat's Fresnel reflectance at the angle `cosine` (between its normal, or the half vector, and the view), times its
// strength: what the coat reflects, and what of the light no longer reaches the base below.
float ClearcoatFresnel(ClearcoatData coat, float cosine)
{
	return coat.Strength * (c_ClearcoatF0 + (1.0 - c_ClearcoatF0) * pow(1.0 - clamp(cosine, 0.0, 1.0), 5.0));
}
```

1. **Line 161:** a strength of 0 means no coat, the value that skips all the coat's work.
2. **Line 167:** the 4 % of an index of 1.5, the same for every coat; no field sets it.
3. **Line 173:** the formula above, times the strength.

The light the coat reflects no longer reaches the base. The coat therefore returns two numbers: the light it reflects and a weight for the base, $1 - F$.

```cpp src="Strata/shaders/Include/PBR.slang#L179-L192"
float3 EvaluateClearcoat(ClearcoatData coat, float3 view, float3 lightDirection, float3 radiance, float sourceAlpha2, out float baseWeight)
{
	float3 H = normalize(view + lightDirection);
	float fresnel = ClearcoatFresnel(coat, dot(view, H));
	baseWeight = 1.0 - fresnel;
	float NoL = clamp(dot(coat.Normal, lightDirection), 0.0, 1.0);
	if (NoL <= 0.0)
		return float3(0.0);
	float NoV = max(dot(coat.Normal, view), 1e-4);
	float NoH = clamp(dot(coat.Normal, H), 0.0, 1.0);
	float roughness = max(coat.Roughness, c_MinRoughness);
	float alpha = roughness * roughness;
	return DistributionGGX(NoH, GetLobeAlpha(alpha, sourceAlpha2)) * VisibilitySmithGGXCorrelated(NoV, NoL, alpha) * fresnel * coat.SpecularEnergy * radiance * NoL;
}
```

1. **Lines 182–183:** the Fresnel at the half vector gives the base's weight; the base keeps $1 - F$ of the light.
2. **Lines 184–186:** a light below the coat's own normal adds no highlight, but the base's weight stays, since the weight does not depend on the normal.
3. **Line 191:** the highlight uses the same distribution and visibility functions as the base, with the coat's roughness, times the coat's energy compensation from [the energy page](energy.md).

In the forward shader the caller combines them: the base's light times the weight, plus the coat's light. The coat's normal comes from its own normal map, which falls back to the vertex normal, and its roughness widens where that normal changes quickly, to avoid sparkle.

Light from the sky and the probes follows the same plan. The coat reflects the environment by its prefiltered Fresnel, using the same split sum as the base, and the indirect light below loses what the coat reflects. The emission loses it too, since the glow sits under the gloss layer. The code for this is in `Strata/shaders/Scene/Forward.frag.slang`, lines 454 to 467.

::figure{id=coat-roughness variant=coat-0}

::figure{id=coat-roughness variant=coat-05}

::figure{id=coat-normal-map}

The sum is checked by energy: a coat on a white metal keeps the white furnace's value, because what the coat takes from the base it reflects back.

## Glass

**Transmission** is the share of light a surface passes through its body instead of scattering from its surface. A material with transmission is drawn as glass. Its fields are:

- `Transmission` from 0 to 1, times the red channel of its map.
- `IOR`, the index that sets how strongly light bends: 1 means no bending, 1.5 is glass, 1.33 is water and 2.42 is diamond.
- `Thickness`, the depth of the volume behind the surface, in the mesh's units, measured along the surface's normal.
- `AttenuationColor` and `AttenuationDistance`, the tint of the volume.

**Attenuation color** is the color white light has after it travels the attenuation distance inside the volume.

Light that enters a denser medium bends toward the surface's normal. The law of bending light gives the angle: $\sin\theta_t = \sin\theta_i / n$, where $\theta_i$ is the angle of the view ray to the normal, $\theta_t$ the angle inside the glass and $n$ the index. A view at 45° into glass of 1.5 gives $\sin\theta_t = 0.7071 / 1.5 = 0.4714$, so $\theta_t = 28.1°$. The shader's `refract` function computes this direction; it is given the ratio $1 / n$ because the light moves from air into glass.

Next the shader finds where that bent ray leaves the glass. It walks the thickness along the bent ray. With `Thickness` 0.1 that is a point 0.047 sideways from where the ray entered, since $0.1 \times 0.4714 = 0.047$. Without bending the ray would end 0.071 sideways, so the point has moved by 0.024. The shader projects the exit point to the screen and reads the copy of the image there, which is the bent view of what lies behind.

Two limits show the idea. With `IOR` 1 the ray does not bend; the exit point stays on the straight line from the camera through the pixel and lands on the same screen position, so nothing shifts whatever the thickness. With `Thickness` 0 the exit point is the surface point itself, so nothing shifts whatever the index. You see the bend only when both are away from their neutral values.

The material's thickness is in the mesh's units, but the entity may be scaled. The shader multiplies it by how much the instance's matrix stretches distances along the normal, so a cube scaled into a thin wall is as thick as the wall. A thickness of 0.1 on a unit cube scaled by 2 along the normal is 0.2 in the world.

::figure{id=glass-index variant=ior-10}

::figure{id=glass-index variant=ior-15}

Roughness blurs what the glass shows. The shader reads the copy at a :term[mip level]{id=mip} of roughness times the number of levels minus one. With six levels, a roughness of 0.5 reads level 2.5, a blend of levels 2 and 3. At 1 it reads level 5, a thirty-second of the copy's size, the blur of frosted glass.

The volume absorbs light by Beer's law, which [the atmosphere page](atmosphere.md) derives. Strata turns the attenuation color into a rate per unit of distance, minus the natural :term[logarithm]{id=logarithm} of the color divided by the distance. A red of 0.5 at a distance of 1 gives a rate of 0.693. After a thickness of 0.5 the red channel keeps $e^{-0.693 \times 0.5} = 0.707$, and after 2 it keeps 0.25. Thicker glass is darker and more saturated, as in real tinted glass.

```cpp src="Strata/src/Strata/Renderer/MaterialData.cpp#L40-L49"
glm::vec3 GetAbsorption(const MaterialProperties& properties)
{
	const float distance = properties.AttenuationDistance;
	if (!(distance > 0.0f) || !std::isfinite(distance))
		return glm::vec3(0.0f);
	// A channel the color removes entirely absorbs as if it kept a ten-thousandth after the distance.
	const glm::vec3 color = glm::clamp(properties.AttenuationColor, glm::vec3(1.0e-4f), glm::vec3(1.0f));
	const glm::vec3 absorption = -glm::log(color) / distance;
	return std::isfinite(absorption.x) && std::isfinite(absorption.y) && std::isfinite(absorption.z) ? absorption : glm::vec3(0.0f);
}
```

1. **Line 43:** a distance of 0, or one that is not a finite number, means no absorption; `AttenuationColor` then does nothing.
2. **Lines 46–47:** a :term[color channel]{id=color-channel} is held between a ten-thousandth and 1, so a channel of 0 cannot give an infinite rate.

::figure{id=glass-thickness variant=thin}

::figure{id=glass-thickness variant=thick-green}

The shader joins everything in one function. Read it in the order the light travels: bend, find the exit, sample, take away what the surface reflects, absorb, tint.

```cpp src="Strata/shaders/Scene/Forward.frag.slang#L487-L504"
float3 TransmitLight(InstanceData instance, MaterialData material, float3 normal, float3 view, float3 albedo, float metallic, float roughness, float transmission)
{
	float3 refracted = refract(-view, normal, 1.0 / material.IOR);
	float thickness = material.Thickness * GetScaleAlongNormal(instance, normalize(v_Normal));
	float3 exitPoint = v_RelativePosition + refracted * thickness;
	float4 clip = mul(u_Frame.ViewProjection, float4(exitPoint, 1.0));
	float2 uv = clip.w > 1e-6 ? NDCToUV(clip.xy / clip.w) : st_FragCoord.xy * u_Frame.ViewportSize.zw;
	float level = roughness * float(TextureLevels(u_SceneColor) - 1);
	float3 behind = u_SceneColor.SampleLevel(u_LinearClampSampler, uv, level).rgb / u_Frame.TemporalParams.y;

	float NoV = max(dot(normal, view), 1e-4);
	float2 dfg = u_BRDFLut.SampleLevel(u_LinearClampSampler, float2(NoV, roughness), 0.0).rg;
	// What the surface reflects, compensated as its specular light is (ShadeLitSurface): the rest passes through.
	float3 f0 = lerp(float3(material.Absorption.w), albedo, metallic);
	float3 reflectance = (f0 * dfg.x + dfg.y) * GetFrameSpecularEnergy(f0, dfg);
	float3 absorbed = exp(-material.Absorption.rgb * thickness);
	return behind * absorbed * albedo * (1.0 - metallic) * (1.0 - reflectance) * transmission;
}
```

1. **Lines 489–491:** `refract` bends the view ray by $1/n$; the thickness, scaled by the instance, moves along it to the exit point.
2. **Lines 492–495:** the exit point goes to a screen position, and the copy is read at the roughness level. A point behind the camera falls back to the pixel's own position. The result divides by the pre-exposure that the copy carries.
3. **Lines 499–501:** the surface's own reflection, computed as the specular light is, so the light that is reflected is not also transmitted.
4. **Lines 502–503:** Beer's absorption over the thickness, the :term[base color]{id=albedo}, no tint for a metal, the transmission, and the rest of the light.

The copy already holds the fog that stands in front of what lies behind, so the function does not fog the result again. The caller adds the transmitted light after the surface's own light and its fog. A glass with a clear coat multiplies the transmitted light by one minus the coat's Fresnel, since the gloss layer reflects its share first. The surface's own diffuse light is scaled by one minus the transmission, so a surface that passes all light has no diffuse color of its own.

## How glass is drawn

A material becomes glass in `GetFlags`. The transparent flag is set for blended materials and for ones with transmission, and a second flag marks glass.

```cpp src="Strata/src/Strata/Renderer/MaterialData.cpp#L14-L22"
uint32_t GetFlags(const MaterialProperties& properties)
{
	// Glass is drawn by the transparent pass (after the copy of what lies behind it), whatever its alpha mode.
	const bool transmissive = IsTransmissive(properties);
	return RenderData::c_CullMaterialAvailable | (properties.DoubleSided ? RenderData::c_CullMaterialDoubleSided : 0u)
		| (properties.AlphaMode == MaterialAlphaMode::Mask ? RenderData::c_CullMaterialAlphaMask : 0u)
		| (properties.AlphaMode == MaterialAlphaMode::Blend || transmissive ? RenderData::c_CullMaterialTransparent : 0u)
		| (transmissive ? RenderData::c_CullMaterialTransmissive : 0u);
}
```

1. **Line 17:** the comment says glass belongs to the transparent pass whatever the alpha mode.
2. **Lines 20–21:** the transparent flag is set for `Blend` or for glass, and a second flag for glass alone.

Extraction counts the transparent draws that are glass; the sort puts them first. In the transparent pass the renderer draws that group first, into its own attachments, without blending.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L2843-L2858"
if (pass == Pass::Transparent && m_GlassBatchCount > 0)
{
	// Glass first, unblended, into its own attachments (with its motion in a frame with motion vectors).
	nvrhi::GraphicsState glassState = state;
	glassState.framebuffer = GetGlassFramebuffer();
	const bool glassVelocity = m_MotionFrame;
	const bool glassField = m_FieldFrame;
	DrawBuckets(commandList, glassState, drawn.first(m_GlassBatchCount), firstArgument,
		[glassVelocity, glassField](const SceneDrawBatch& batch)
		{
			return PipelineKey { Pass::Glass, batch.DoubleSided, batch.Mirrored, batch.Skinned, glassVelocity, false, glassField };
		},
		nullptr, nullptr);
	firstArgument += m_GlassBatchCount;
	drawn = drawn.subspan(m_GlassBatchCount);
}
```

1. **Line 2843:** the branch runs only in the transparent pass and only when the frame has glass.
2. **Line 2847:** glass has its own framebuffer; it also writes entity ids and, in a frame with motion, motion vectors.
3. **Line 2853:** the pipeline's key names a glass pass; double-sided, mirrored and skinned draws get their own variants, like every other pass. The last flag picks the shaders that add the world's indirect light in a frame that uses it.
4. **Lines 2856–2857:** the glass batches leave the list, and the blended draws that remain go through the plain pass.

Glass writes depth with the same test as the others and no blending. That has two effects. A blended surface behind a sheet fails the depth test and stays hidden, and glass shows alpha 1 in the image's alpha channel, as every surface drawn without blending does.

**Scene-color copy** is the half-resolution copy of the finished :term[high dynamic range]{id=high-dynamic-range} (HDR) image, with a chain of blurred levels, that glass reads for what lies behind it.

The copy is made in a compute pass after the sky. It has half the viewport's size, and as many levels as fit up to six, where each level is half the size of the one above. A 1920 by 1080 view gives a copy of 960 by 540 texels with six levels: 960, 480, 240, 120, 60 and 30 texels wide. The format is `B10G11R11` where the device can write it from a compute shader, and a 16-bit float format of four channels otherwise.

```cpp src="Strata/src/Strata/Renderer/SceneRendererGlass.cpp#L107-L120"
void SceneRenderer::CopySceneColor(nvrhi::ICommandList* commandList)
{
	ST_PROFILE_FUNCTION();
	const nvrhi::TextureDesc& desc = m_SceneColorTexture->getDesc();
	nvrhi::ComputeState state;
	state.pipeline = m_SceneColorPipeline;
	for (uint32_t level = 0; level < static_cast<uint32_t>(m_SceneColorSets.size()); level++)
	{
		state.bindings = { m_SceneColorSets[level] };
		commandList->setComputeState(state);
		const uint32_t width = std::max(1u, desc.width >> level);
		const uint32_t height = std::max(1u, desc.height >> level);
		commandList->dispatch((width + c_SceneColorGroupSize - 1) / c_SceneColorGroupSize, (height + c_SceneColorGroupSize - 1) / c_SceneColorGroupSize, 1);
	}
```

1. **Lines 113–119:** one dispatch per level. Level 0 reads the :term[HDR]{id=high-dynamic-range} target and each next level reads the one above, the mean of 2 by 2 texels.

Glass reads the copy at binding slot 19 of the scene's resources, the shader resource view `u_SceneColor`. Reading a half-resolution image costs little and gives the blur for free, since a :term[mip chain]{id=mip-chain} already holds the blur. It also loses detail: a clear sheet at full resolution shows its background slightly soft. A frame without glass skips the copy and spares the cost, unless its screen-space reflections need one.

## What Strata does not do

Three limits follow from the choice of a copy.

- **Water as a feature.** Strata has no water surface that moves, flows or foams. Water is a material with an `IOR` of 1.33, a tint and a thickness. The shape and the motion are yours to make.
- **Reflections of and through transparent surfaces.** Glass reflects the sky and the probes like any surface, but not other glass and not blended surfaces. The screen-space reflection of [the reflections page](../indirect/ssr.md) traces opaque surfaces only. Glass behind glass is not seen either: the copy holds only what was drawn before the first sheet.
- **Order-independent transparency.** Some engines draw blended surfaces in any order and fix the result in a later pass. Strata sorts blended surfaces, so two sheets that cross each other, or a surface that must lie both before and after another, can blend wrongly. Glass shows only what was drawn before it.

The rule from the contract applies to all three: glass is not in the prepass, so it gets no ambient occlusion, and as a transparent surface it casts no shadow.

:::why
Strata keeps glass in the forward pass with one copy of the image instead of tracing. A copy costs one half-resolution pass and works on every device Strata supports, with no ray tracing hardware. The cost is the three limits above, each of which a game can often hide by design: tint instead of reflect, one sheet in front of the view, thin sheets for blends.
:::

:::example
A glossy wooden table with a glass of colored liquid. The table's material has a brown base color, `Roughness` 0.7, `Clearcoat` 1 and `ClearcoatRoughness` 0.1. Seen head-on, the coat reflects 4 % of the light and the wood keeps 96 %. At a graze of $\cos\theta = 0.1$ the coat reflects 61 %, so the window's mirror image appears and the grain dims.

The liquid is a cylinder with `Transmission` 1, `IOR` 1.33, `Thickness` 0.3, `AttenuationColor` $(0.9, 0.4, 0.2)$ and `AttenuationDistance` 0.3. After the thickness of 0.3 the red channel keeps 0.9, the green 0.4 and the blue 0.2, so the table behind the cup shows warm. The coat reflects the sky and the probes, not the cup, since glass is drawn after the table and the coat never sees it.
:::

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Layered materials with full multiple-layer scattering | Film renderers; some engines for car paint | Colored layers that scatter and absorb inside the coat | A heavy shader and many parameters for a small change |
| Ray-traced glass | Engines with hardware ray tracing | Glass behind glass; reflections of glass; exact paths | A ray structure for the scene, a cost per ray and a feature that needs new hardware |
| Order-independent transparency | Engines with weighted blending or per-pixel lists | Blended surfaces in any order; no sort | Memory per pixel or a result that is only approximate; more passes |
| Bending by a flat offset of the screen | Many engines | No exit point to compute | Wrong shifts for thick or tilted glass, and no use of `Thickness` |

Further reading lists the sources for these.

## How it is tested

The GPU suites render small scenes and compare pixel values. Run them with `ctest --preset windows-debug -R GPU` on a machine with a graphics card.

- The suite `GPU.SceneRenderer.Materials` checks that a coat adds a second highlight where its own normal map turns it, and that a coat takes from the base the light it reflects. It checks that glass leaves what it reflects, shows what lies behind it displaced by index and thickness, and writes depth, ids and motion like an opaque surface. It also checks that the copy is made only for glass, in the right format.
- The case "A clear coat over a white metal keeps the furnace's light" lives in the lighting suite. In a uniform white sky a white metal under a rough coat reads 1 within 3 %. If the coat took light and gave none back, the value would fall.
- The metric `Transmission` of the `PerfGPU.Renderer` suite renders 100,000 cubes seen through one large sheet and checks the frame's time against its budget in `StrataTests/Perf/Budgets.json`, and that exactly one copy was made.

## Changing it safely

- A new material field that glass or coat reads follows the rules of [the material data page](material-data.md): the field reaches the GPU in the material table. The :term[importer's]{id=importer} version changes where its output changes, and the feature test uses it.
- A new pass that draws surfaces must decide where it stands against the copy. A surface drawn after the copy is missing from it, so no glass shows it; a surface drawn before the copy shows behind the glass.
- Both paths that decide what is drawn, the :term[central processing unit]{id=processor} (CPU) path and the culling shader, must agree on what a material with transmission is. A static assertion beside the material flags ties the two sets of flag values together; a flag change has to keep it.
- Keep the shaders' coat branch the same for a whole draw, so that a coat of 0 costs nothing.
- Pass `GPU.SceneRenderer.Materials` and the `PerfGPU.Renderer` suite before you merge.

## Summary

- Blended surfaces do not commute, so they draw far to near after the opaque surfaces, and premultiplied alpha lets layers combine in any grouping.
- A clear coat reflects $F$ of the light by its own Fresnel curve, 4 % head-on, and the base keeps $1 - F$.
- Glass bends the view ray by its index, walks the scaled thickness to an exit point, reads the copy at a roughness level, absorbs by Beer's law and tints.
- The scene-color copy holds only opaque surfaces and the sky, so glass shows no glass, no blended surface and gets no occlusion and no shadow.
- Author a coat with strength, roughness and a normal map, and glass with `Transmission`, `IOR`, `Thickness` and an attenuation color and distance.

## Check yourself

1. Two sheets of 50 % red and 50 % blue plastic lie over a white wall. A student draws blue first and says the result equals red first. Which is right?
   - (a) Equal, since the sheets are the same size.
   - (b) Different, since each sheet mixes with whatever is under it.
   - (c) Equal, since premultiplied alpha removes the order.

   :::answer{tests="blend-order"}
   (b) is right: you computed $(0.5, 0.5, 1)$ after blue and $(0.75, 0.25, 0.5)$ after red, against the other order's $(0.5, 0.25, 0.75)$. Answer (a) is wrong because size does not matter. Answer (c) is wrong: premultiplied alpha lets you group layers, but it keeps their order.
   :::

2. A coat of strength 1 is seen at $\cos\theta = 0.5$. What share of the light does the coat reflect, and what share reaches the base?

   :::answer{tests="coat-weight"}
   The coat reflects $0.04 + 0.96 \times 0.5^5 = 0.07$, so 7 %. The base weight is $1 - 0.07 = 0.93$, so 93 % of the light reaches the base.
   :::

3. A sheet has `IOR` 1.5 and `Thickness` 0, in front of a wall. You change `IOR` to 2.0. What changes in the picture?

   :::answer{tests="glass-path"}
   Nothing shifts. With a thickness of 0 the exit point is the surface point, so the pixel reads the copy at its own position. The index changes only the reflectance of the surface, which takes a larger share of light, so the sheet looks a little darker.
   :::

4. A ball of glass floats in front of a second sheet of glass, and a smoke puff of a blended material floats behind the ball. What does the ball show?

   :::answer{tests="copy-limits"}
   The ball shows the wall behind both, not the sheet and not the puff. The copy is made before any glass is drawn, and glass writes depth, which hides blended surfaces behind it. Glass behind glass needs order-independent transparency or ray tracing, which Strata does not have.
   :::

5. Which values suit a green bottle: red 0.2, green 0.6, blue 0.3 at a distance of 0.5, with `Thickness` 0.5? What does the red channel keep?

   :::answer{tests="author-glass"}
   Red keeps $0.2^{0.5 / 0.5} = 0.2$, since thickness equals the distance. Green keeps 0.6 and blue 0.3, so the bottle looks green-yellow. Doubling the thickness squares the numbers: red 0.04. A wall of glass of that thickness would look almost black in red.
   :::

## Exercises

1. **Basic.** A coat has strength 0.5. Compute the share it reflects at $\cos\theta = 1$ and at $\cos\theta = 0.1$.

   :::answer[Worked solution]{tests="coat-weight"}
   At $\cos\theta = 1$: $0.5 \times 0.04 = 0.02$. At $\cos\theta = 0.1$: $0.5 \times (0.04 + 0.96 \times 0.59) = 0.5 \times 0.607 = 0.30$. The base keeps 98 % and 70 %.
   :::

2. **Medium.** Make a glass display case with a colored liquid on a glossy wooden base. Give the values of two materials, a liquid and a base, and say what each field does.

   :::answer[Worked solution]{tests="author-glass"}
   The command `material.create` takes a path and properties. The liquid:

   ```json
   { "path": "Materials/Liquid.stmat", "properties": { "BaseColor": [1, 1, 1, 1], "Roughness": 0.05, "Transmission": 1, "IOR": 1.33, "Thickness": 0.3, "AttenuationColor": [0.9, 0.4, 0.2], "AttenuationDistance": 0.3 } }
   ```

   The base:

   ```json
   { "path": "Materials/Base.stmat", "properties": { "BaseColor": [0.35, 0.2, 0.1, 1], "Roughness": 0.7, "Clearcoat": 1, "ClearcoatRoughness": 0.1 } }
   ```

   `Transmission` 1 makes the liquid glass. `IOR` 1.33 is water, `Thickness` 0.3 is the depth along the normal, and the attenuation pair tints the light. The base's `Clearcoat` is a gloss layer, of roughness 0.1, over a dull wood.
   :::

3. **Hard.** Trace it yourself: a material's `Transmission` becomes 0.5. Find where the engine decides the material is glass, where its draws are sorted and drawn first, and where `TransmitLight` runs.

   :::answer[Worked solution]{tests="glass-path"}
   Search for `IsTransmissive`. It is in `Strata/src/Strata/Renderer/MaterialData.cpp` and returns true for a material that is not `Unlit` with `Transmission` above 0. `GetFlags` in the same file sets the transparent flag and the glass flag; in `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp` the extraction marks the transparent draws that are glass and counts them. `SceneRenderer::DrawBatches` in `Strata/src/Strata/Renderer/SceneRenderer.cpp` draws the glass batches first, with no blending. The shader function `TransmitLight` in `Strata/shaders/Scene/Forward.frag.slang` runs in the glass variant only.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Renderer/Material.h`: the coat and glass fields of `MaterialProperties`.
- `Strata/src/Strata/Renderer/MaterialData.cpp`: `GetFlags`, `IsTransmissive`, `GetAbsorption`.
- `Strata/src/Strata/Renderer/SceneRendererGlass.cpp`: the copy and its levels.
- `Strata/src/Strata/Renderer/SceneRenderer.cpp`: the glass draws and the blend state.
- `Strata/shaders/Scene/Forward.frag.slang`, `Strata/shaders/Include/PBR.slang`, `Strata/shaders/Effects/SceneColorCopy.comp.slang`: the shading and the copy.
- Tests: `GPU.SceneRenderer.Materials` and the metric `Transmission` of the `PerfGPU.Renderer` suite.

## Further reading

- Weidlich and Wilkie, "Arbitrarily Layered Micro-Facet Surfaces" (2007): the layered model behind coats (advanced).
- The Khronos glTF extensions `KHR_materials_clearcoat`, `KHR_materials_transmission`, `KHR_materials_ior` and `KHR_materials_volume`: the fields Strata follows (intermediate).
- McGuire and Bavoil, "Weighted Blended Order-Independent Transparency" (2013): the approach Strata does not take (advanced).
