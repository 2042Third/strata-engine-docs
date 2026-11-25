---
id: light/area-lights
title: "Lights with size: sized highlights and area lights"
description: "How Strata gives lights a size: highlights widened without gaining light, and rect lights shaded exactly with linearly transformed cosines."
kind: internals
size: L
tracks: [E]
needs: [light/many-lights, light/energy]
time: 75
learn:
  - id: energy-kept
    text: explain why a sized highlight keeps its energy and what widening the visibility term would do
  - id: lobe-alpha
    text: compute the alpha squared that a sun or a bulb adds to a highlight's lobe
  - id: trace-size
    text: trace a light's size from its component to the lobe it widens
  - id: rect-units
    text: compute a rect light's luminance from lumens and its light below the center
  - id: choose-light
    text: choose between a sized point light and a rect light for a lamp
since: 0.8.0
status: final
---

A candle flame, a ceiling panel and the sun all have a size. A :term[renderer]{id=renderer} that treats each as a single point draws a tiny bright dot on a polished floor, and a harsh, wrong pool of light under a lamp that hangs close above a desk. Strata gives point lights, spot lights and the sun a size only in their highlights, and it shades the rect light of 0.8.0 as a true rectangle, exactly for every pixel. The page omits the soft shadows of rect lights, the sun's soft shadow, the clear coat and the placing of lamps; links lead to each.

## The problem and how engines solve it

Put a polished metal ball under a lantern. In life the ball shows a small bright picture of the bulb, with the bulb's shape and size. A renderer that treats the lantern as a point shows a dot instead, and the dot can shrink below one pixel. Such a dot lands on some pixels and misses their neighbors, so it flickers when the camera moves.

Size matters as an angle, not as a length. A bulb of radius 0.05 m seen from 1 m away spans an angular radius of $\arctan(0.05)$, about 2.9 degrees. The sun's disk spans 0.265 degrees in radius, about ten times less. For a mirror on a wet road, a small lantern is a larger source than the sun.

A point is also wrong for diffuse light. A panel 0.25 m above a desk lights the whole desk from its whole area, and a point at the same place lights a small, hard spot. The toy below puts numbers on that.

Engines use three ideas against these problems, and each one pays for its accuracy in a different place.

- The representative point method, which the 2013 course notes of Unreal Engine 4 describe, picks for each pixel the point of the light's shape that lies nearest to the mirror direction. It shades a point light at that point. It is cheap and it changes only the highlight, so the diffuse light stays that of a point. It also needs a correction that returns the energy the moving point adds, and the correction differs for each shape.
- **LTC**, short for linearly transformed :term[cosines]{id=cosine}, is the method of a 2016 paper: it shades a light shaped like a polygon exactly, with no sampling. Its price is a table of numbers and a few hundred arithmetic operations for each pixel and light.
- **Lobe widening**, also called roughness modification, makes the surface's reflection lobe wider by the angle that the source spans. It costs a few operations and needs no table. It gives no diffuse effect and no shape: every source becomes a round bright spot.

Strata uses two of the three and has no representative point code. Its sun, point lights and spot lights use lobe widening, and its rect light uses linearly transformed cosines (LTC). Two more terms name the lights themselves.

An **area light** is a light that has a surface, so that its light leaves every point of a shape and not one point.

The **source radius** of a light is the radius of the bulb or flame that it stands for, which spans an angular radius when a surface looks at it. The sun's angular diameter is the same size, given as the full width of its disk in degrees.

## The map

Three paths run through the renderer, and they meet in one place, the forward :term[shader's]{id=shader} call for each light. The records of lights are built on the :term[main thread]{id=main-thread} from the components' signals. The shading runs on the :term[graphics processing unit]{id=gpu} (GPU), once for each pixel. Nothing here keeps history from one frame to the next.

```mermaid caption="Three paths carry a light's size to the shading. The sun's lobe is worked out once on the processor. A bulb's radius travels through the light buffer to a per-pixel function, and a rect light's face travels beside the buffer to its own shading function." alt="A flow chart with three rows. In the first row the sun's angular diameter becomes a number for the lobe once a frame and joins the frame constants. In the second row a point or spot light's source radius goes through the light record and the light buffer to a function that works out the lobe for each pixel. Both rows end at the call that evaluates a light and widens the distribution. In the third row a rect light becomes a record with a face, then a buffer entry, and goes to its own shading function."
flowchart LR
    A["Sun: Angular Diameter"] --> B["GetSunLobeAlpha2, once a frame"]
    B --> C["FrameConstants ReflectionParams.w"]
    C --> H["LightSurface"]
    D["Point and spot: SourceRadius"] --> E["LightRecord Source.x"]
    E --> F["LightData SpotAngles.w"]
    F --> G["GetSourceLobeAlpha2, per pixel"]
    G --> H
    H --> I["EvaluateLightWeighted: GetLobeAlpha widens D"]
    J["RectLightComponent"] --> K["AreaLights::MakeRecord"]
    K --> L["LightRecord with AxisX and AxisY"]
    L --> M["LightData and LightShape"]
    M --> N["ShadeAreaLight"]
```

`SceneRenderData.h` owns the sun's number and the layouts of the records. `RenderLights.cpp` turns components into records. `PBR.slang` owns the lobe functions. `AreaLights.h` and `AreaLights.cpp` are the rect light's shading written for the processor, and `AreaLights.slang` repeats it on the GPU. `Forward.frag.slang` calls them all.

## The contract

Callers of these functions may assume the rules below, and must keep them when they change the code. Each rule comes with its reason.

1. A light's size widens only the distribution $D$ and keeps it :term[normalized]{id=normalization}. Reason: the other terms of the highlight belong to the surface. A larger source does not make the surface's :term[microfacets]{id=microfacet} hide each other less or reflect more, so widening the visibility term or skipping the normalization would add light.
2. The sun and the bulbs share one formula. The sun's runs once on the processor, and a bulb's runs for each pixel on the GPU. Reason: a bulb's angle depends on its distance from the pixel, and the sun's does not.
3. A source radius is the real radius of the bulb or flame, never a softness knob. Reason: a larger radius spreads the highlight and lowers its peak, so the light looks dimmer and not softer. Its diffuse light and its shadows do not change.
4. A rect light is a record like the others. Its face travels in a parallel buffer, and the processor's `AreaLights::Shade` is the contract of its shading. Reason: tests can then compute what the GPU must show, and a change to one needs a change to the other.
5. A rect light keeps its energy as other lights do: diffuse light takes what the highlight leaves. Reason: the white furnace of [the energy page](../light/energy.md) must stay white.
6. A scene without rect lights renders as before, bit for bit, because the shaders that shade rect lights are separate binaries. Reason: nobody should pay for a light they do not use.
7. The mesh that shows a rect light's face carries `LightSurface`. Reason: otherwise the panel's glow would count twice, once from the light and once from reflections and probes.

:::rule
`AGENTS.md` says that a light's size widens only its highlight, and that rect lights are records whose shading contract is `AreaLights::Shade`: change it together with `Include/AreaLights.slang` and `GPU.SceneRenderer.AreaLights`. The reason is the one of rules 1 and 4, and [the energy page](../light/energy.md) shows what a change that breaks them does to a white furnace.
:::

## A toy version

The toy below computes the numbers of this page in about 70 lines of complete C++ with plain `double` values. It widens a lobe by a bulb of radius 0 m, 0.05 m and 0.3 m at 1 m, and it adds up the lobe's energy to show that it stays 1. Then it finds the light of a 1 by 0.5 m panel of 25 :term[nits]{id=lux}. It adds the angle that each edge spans to get the panel's form factor, the share of a receiver's light that the panel can give. Then it compares the result with a point light of the same intensity; look at the energy column and at the two lux values of the panel rows.

```cpp sketch="light-area-lights-toy.cpp"
#include <glm/glm.hpp>

#include <algorithm>
#include <array>
#include <cmath>
#include <cstdio>

constexpr double c_Pi = 3.14159265358979;
constexpr double c_LobeHalfMaximum = 1.2871885;
constexpr double c_MinRoughness = 0.045;

double DistributionGGX(double NoH, double alpha)
{
	const double alpha2 = alpha * alpha;
	const double f = (NoH * alpha2 - NoH) * NoH + 1.0;
	return alpha2 / (c_Pi * f * f);
}

// The alpha^2 a sphere of `radius` at `distance` adds to a highlight's lobe (as PBR.slang's GetSourceLobeAlpha2).
double GetSourceAlpha2(double radius, double distance)
{
	const double sine2 = std::min(radius * radius / (distance * distance), 0.5);
	const double minAlpha2 = std::pow(c_MinRoughness, 4.0);
	return std::max(sine2 / ((1.0 - sine2) * c_LobeHalfMaximum * c_LobeHalfMaximum) - minAlpha2, 0.0);
}

// What the lobe sends out: the sum of D (n.h) over the half vectors' hemisphere, which must stay 1.
double LobeEnergy(double alpha)
{
	constexpr int c_Steps = 200000;
	double sum = 0.0;
	for (int step = 0; step < c_Steps; step++)
	{
		const double theta = (step + 0.5) * (c_Pi * 0.5) / c_Steps;
		sum += DistributionGGX(std::cos(theta), alpha) * std::cos(theta) * std::sin(theta);
	}
	return sum * 2.0 * c_Pi * (c_Pi * 0.5) / c_Steps;
}

// The form factor of a rectangle above a receiver that faces up: each edge adds the angle it spans, along the normal of the
// plane through the edge and the receiver (the sum over the edges, divided by 2 pi).
double FormFactor(double halfWidth, double halfHeight, double height)
{
	const std::array<glm::dvec3, 4> corners = { glm::dvec3(-halfWidth, height, -halfHeight), glm::dvec3(halfWidth, height, -halfHeight),
		glm::dvec3(halfWidth, height, halfHeight), glm::dvec3(-halfWidth, height, halfHeight) };
	glm::dvec3 vectorFormFactor(0.0);
	for (size_t index = 0; index < corners.size(); index++)
	{
		const glm::dvec3 start = glm::normalize(corners[index]);
		const glm::dvec3 end = glm::normalize(corners[(index + 1) % corners.size()]);
		vectorFormFactor += std::acos(glm::dot(start, end)) * glm::normalize(glm::cross(start, end));
	}
	return std::abs(vectorFormFactor.y) / (2.0 * c_Pi);
}

int main()
{
	const double alpha = 0.03; // Wet ground, perceptual roughness 0.17
	for (const double radius : { 0.0, 0.05, 0.3 })
	{
		const double widened = std::sqrt(alpha * alpha + GetSourceAlpha2(radius, 1.0));
		std::printf("radius %.2f m at 1 m: alpha %.4f, peak D %.1f, energy %.4f\n", radius, widened, DistributionGGX(1.0, widened), LobeEnergy(widened));
	}
	const double luminance = 25.0, area = 1.0 * 0.5;
	for (const double height : { 4.0, 1.0, 0.25 })
	{
		const double exact = c_Pi * luminance * FormFactor(0.5, 0.25, height);
		const double point = luminance * area / (height * height);
		std::printf("height %.2f m: panel %.2f lux, point light of its intensity %.2f lux\n", height, exact, point);
	}
	return 0;
}
```

```text output-of="light-area-lights-toy.cpp"
radius 0.00 m at 1 m: alpha 0.0300, peak D 353.7, energy 1.0000
radius 0.05 m at 1 m: alpha 0.0491, peak D 132.2, energy 1.0000
radius 0.30 m at 1 m: alpha 0.2461, peak D 5.3, energy 1.0000
height 4.00 m: panel 0.77 lux, point light of its intensity 0.78 lux
height 1.00 m: panel 10.40 lux, point light of its intensity 12.50 lux
height 0.25 m: panel 52.58 lux, point light of its intensity 200.00 lux
```

1. **Line 22:** the :term[sine]{id=sine} squared of the source's angle is its radius over its distance, squared, and stops at one half.
2. **Line 24:** the added alpha squared is the tangent squared over the lobe constant squared, less what the smallest roughness spreads.
3. **Lines 28–38:** the lobe's energy is a sum of the distribution times the cosine of the half vector's angle over the hemisphere.
4. **Lines 44–53:** each edge of the rectangle adds the angle it spans along the normal of its plane, and the sum over $2\pi$ is the form factor.
5. **Lines 67–68:** the panel's light is $\pi$ times its :term[luminance]{id=luminance} times the form factor; the point's is the luminance times the area over the height squared.

The first three lines show the rule of the page. The peak of the lobe falls from 353.7 to 5.3 while its energy stays 1.0000: the highlight spreads and does not brighten. The last three lines show why a panel is not a point. Four meters away the two agree within 2 %, but at 1 m the point has 20 % too much light, and at 0.25 m it has 3.8 times too much. A point puts all of the panel's intensity at one spot, and the panel spreads it over its whole area.

The toy omits everything that a game needs: the table that makes the highlight of a panel cheap, the receiver's horizon, the clear coat, the shadows and the GPU. The next section adds them back, in the order the data flows.

## The real code, in the order data flows

### The sun's disk

The sun is not in the cluster loop. Its size comes from the Directional Light's **Angular Diameter**, which scenes and scripts still call `ShadowSoftness`, and one function turns it into the number that the shader adds to the lobe. Look at how it reads the angle and what it subtracts.

```cpp src="Strata/src/Strata/Renderer/SceneRenderData.h#L132-L139"
inline float GetSunLobeAlpha2(float degrees)
{
	constexpr float c_LobeHalfMaximum = 1.2871885f;
	constexpr float c_MinAlpha = 0.045f * 0.045f; // PBR.slang's c_MinRoughness, squared
	const float radius = glm::radians(std::isfinite(degrees) ? std::clamp(degrees, 0.0f, 10.0f) : 0.0f) * 0.5f;
	const float alpha = std::tan(radius) / c_LobeHalfMaximum;
	return std::max(alpha * alpha - c_MinAlpha * c_MinAlpha, 0.0f);
}
```

Line 136 clamps the angle to the property's 0 to 10 degrees, treats a value that is not a number as 0 and halves it to get the angular radius. Line 137 finds the alpha whose lobe is as wide as that radius: the constant `c_LobeHalfMaximum`, about 1.287, is the angle per unit of alpha at which the lobe falls to half its peak. Line 138 subtracts what the smallest roughness already spreads, so that a mirror shows the disk at its true size, and never goes below 0. `SceneRenderer` stores the result in `ReflectionParams.w` of the frame constants once a frame, with or without shadows.

### The bulb's sphere

A point or spot light's `SourceRadius` has to meet the pixel's distance, so the work moves to the GPU. The function below takes the radius and the squared distance. Search the function for the place where the angle becomes an alpha.

```slang src="Strata/shaders/Include/PBR.slang#L18-L31"
static const float c_LobeHalfMaximum = 1.2871885; // 2 sqrt(sqrt(2) - 1)
static const float c_MaxSourceSine2 = 0.5;        // At most 45 degrees of angular radius (a surface touching the bulb)

// The alpha^2 a sphere of `radius` at `distanceSquared` adds to a highlight's lobe: it spans an angular radius theta with
// sin(theta) = radius / distance, so it widens the lobe by (tan(theta) / c_LobeHalfMaximum)^2, less what the smallest roughness
// spreads already (c_MinRoughness^4), as GetSunLobeAlpha2 does for the sun's disk. 0 for a point.
float GetSourceLobeAlpha2(float radius, float distanceSquared)
{
	if (radius <= 0.0)
		return 0.0;
	float sine2 = min(radius * radius / max(distanceSquared, 1e-8), c_MaxSourceSine2);
	float minAlpha2 = c_MinRoughness * c_MinRoughness * c_MinRoughness * c_MinRoughness;
	return max(sine2 / ((1.0 - sine2) * c_LobeHalfMaximum * c_LobeHalfMaximum) - minAlpha2, 0.0);
}
```

1. **Line 18:** the same constant as the sun's, 2 times the square root of the square root of 2 minus 1.
2. **Line 19:** the :term[sine]{id=sine} squared stops at 0.5, which is 45 degrees: a surface that touches the bulb does not blow the formula up.
3. **Lines 26–27:** a radius of 0 returns 0, so a point light shades as it always did.
4. **Line 28:** the sine of the angular radius is the radius over the distance, and the code squares it.
5. **Line 30:** $\tan^2 = \sin^2 / (1 - \sin^2)$, divided by the constant squared, less the smallest roughness's share, never below 0.

Two more functions finish the job. `GetLobeAlpha` returns $\sqrt{\alpha^2 + s}$ for the added share $s$, and returns the surface's own alpha unchanged when $s$ is 0. The direct-light function then uses the widened alpha in one place only.

```slang src="Strata/shaders/Include/PBR.slang#L139-L143"
float roughness = max(surface.Roughness, c_MinRoughness);
float alpha = roughness * roughness;

float3 F = FresnelSchlick(surface.F0, VoH);
float3 specular = DistributionGGX(NoH, GetLobeAlpha(alpha, sourceAlpha2)) * VisibilitySmithGGXCorrelated(NoV, NoL, alpha) * F * surface.SpecularEnergy;
```

Line 143 shows rule 1 in code. The distribution takes `GetLobeAlpha(alpha, sourceAlpha2)`, and the visibility and the :term[Fresnel]{id=fresnel} term keep the surface's own `alpha` and `F`.

The cluster loop calls it for every point and spot light that reaches the pixel. Notice how late in the loop the call comes: the light has already passed its range, cone and shadow tests.

```slang src="Strata/shaders/Scene/Forward.frag.slang#L386-L394"
uint shadowSlot = uint(light.SpotAngles.z + 0.5);
if (shadowSlot > 0u)
{
	float3 geometricNormal = normalize(v_Normal) * (st_FrontFacing ? 1.0 : -1.0);
	attenuation *= SampleLocalShadow(shadowSlot - 1u, surface.Position, geometricNormal, st_FragCoord.xy);
}
// The highlight takes the bulb's or flame's angular size (SpotAngles.w: its radius; 0, a point, skips it).
float sourceAlpha2 = GetSourceLobeAlpha2(light.SpotAngles.w, distanceSquared);
color += LightSurface(surface, coat, diffuseWeight, lightDirection, light.Color.rgb * attenuation, sourceAlpha2);
```

The radius arrives in `light.SpotAngles.w`: both light-culling paths copy the record's `Source.x` there, after `RenderLights` has clamped it to the range 0 to 2 m. Line 393 calls the function with the squared distance that the loop already computed, and line 394 hands the result to `LightSurface`, which passes it to `EvaluateLightWeighted` and to the clear coat's lobe.

:::example
Work out the three sources of the figures by hand, for a mirror (roughness 0, so $\alpha = 0.045^2 = 0.002025$) and for wet ground ($\alpha = 0.03$).

The sun at 0.53 degrees has an angular radius of 0.265 degrees. Its tangent is 0.004625, and $\alpha_s = 0.004625 / 1.287 = 0.003593$. Then $\alpha_s^2 = 1.291 \times 10^{-5}$, less $0.045^4 = 4.1 \times 10^{-6}$, adds $8.8 \times 10^{-6}$. On the mirror the lobe's alpha becomes 0.003593, which is 1.77 times wider than the point's 0.002025, and its peak falls from 77,600 to 24,700.

The sun at 10 degrees has a radius of 5 degrees, a tangent of 0.0875 and $\alpha_s = 0.0680$. The lobe is 34 times wider than the mirror's, and its peak is 69, about 1,100 times lower. The light the lobe carries is the same.

A bulb of 0.05 m at 1 m has $\sin^2 = 0.0025$, so $\tan^2 = 0.002506$ and it adds $0.002506 / 1.657 - 4.1 \times 10^{-6} = 0.001509$. On wet ground, $\alpha = \sqrt{0.0009 + 0.001509} = 0.0491$. A bulb of 0.3 m at 1 m adds 0.0597 and gives $\alpha = 0.246$, the 5.3 peak of the toy.
:::

Now look at the same lights as pictures. In the first set the sun's Angular Diameter is 0, 0.53 and 10 degrees, reflected in a polished floor.

::figure{id=sun-angular-diameter variant=diameter-0}

::figure{id=sun-angular-diameter variant=diameter-053}

::figure{id=sun-angular-diameter variant=diameter-10}

In the second set a lantern's Source Radius is 0, 0.05 and 0.3 m over wet ground. These close views show only the highlight; the same settings leave rough surfaces and shadows unchanged.

::figure{id=lantern-source-radius variant=radius-0}

::figure{id=lantern-source-radius variant=radius-005}

::figure{id=lantern-source-radius variant=radius-03}

The second set shows rule 3. The 0.3 m radius is a flame's size, and the lantern's bulb is much smaller. With the larger radius the highlight turns into a wide dim patch, much wider than the picture of a small bulb should be. Real sizes are in the manual: about 0.03 to 0.06 m for a lantern's bulb and 0.2 to 0.3 m for a fire pit's flames.

### Rect lights: units and the record

A rect light is a `RectLightComponent`: a Width by Height rectangle in the entity's X-Y plane that shines along the entity's forward, minus Z, direction, from both faces when it is two-sided. The component's **Units** decide what its **Intensity** states, and the two choices connect it to the quantities of [the units page](../light/units-exposure.md). With Nits, the default, the intensity is the :term[luminance]{id=luminance} of the face, the same unit as an emissive material. With :term[Lumens]{id=lumen} it is the power that the light emits, which is what lamp catalogues give. The conversion is one function.

```cpp src="Strata/src/Strata/Renderer/AreaLights.cpp#L242-L250" symbol="AreaLights::GetLuminance"
float GetLuminance(float intensity, AreaLightUnits units, const glm::vec2& halfExtents, bool twoSided)
{
	if (units != AreaLightUnits::Lumens)
		return intensity;
	const float area = 4.0f * halfExtents.x * halfExtents.y;
	if (!(area > 0.0f))
		return 0.0f;
	return intensity / (glm::pi<float>() * area * (twoSided ? 2.0f : 1.0f));
}
```

A flat face that sends the same luminance $L$ in every direction emits $\pi L A$ lumens, where $A$ is its area in square meters. That is why line 249 divides the power $P$ by $\pi A$, and by 2 more for a two-sided light, whose two faces share the power. The area comes from the world scale, so a lumens light keeps its power when you change its size, and a nits light keeps its brightness.

:::example
A 1 by 0.5 m panel with Intensity 25 and Units Nits has $L = 25$ nits and emits $\pi \times 25 \times 0.5 = 39.3$ lumens. Give the same panel 800 lumens and it has $L = 800 / (\pi \times 0.5) = 509$ nits, and 255 nits on each face when two-sided. The luminous intensity along its axis, which is what a point light's :term[candela]{id=candela} states, is $L \times A$: 12.5 cd for the first panel. Its light below the center at 1 m is the 10.4 lux of the toy, where a point light of 12.5 cd would give 12.5 lux.
:::

The record carries everything the shading needs. Look at what goes where.

```cpp src="Strata/src/Strata/Renderer/RenderLights.cpp#L99-L119" symbol="RenderLights::MakeAreaRecord"
RenderData::LightRecord RenderLights::MakeAreaRecord(const glm::mat4& world, bool active, const glm::vec3& color, float luminance, const glm::vec2& halfExtents,
	float range, bool twoSided)
{
	RenderData::LightRecord record;
	const AreaLights::Record area = AreaLights::MakeRecord(world, active, color, luminance, halfExtents, range, twoSided);
	if (!area.Drawn)
		return record; // Not drawn
	// The shading's window takes 1 / range^2 (AreaLights::LoadAreaLight computes it alike).
	const float inverseRangeSquared = 1.0f / (area.Range * area.Range);
	if (!std::isfinite(inverseRangeSquared))
		return record;
	record.PositionRange = glm::vec4(area.Center, area.Range);
	record.Color = glm::vec4(area.Radiance, inverseRangeSquared);
	record.DirectionType = glm::vec4(area.Normal, static_cast<float>(RenderData::c_LightRect));
	record.SpotAngles = glm::vec4(0.0f, 0.0f, RenderData::c_LightRecordDrawn, 0.0f);
	record.Bounds = glm::vec4(area.Center, area.BoundsRadius);
	record.Source = glm::vec4(0.0f, area.TwoSided ? RenderData::c_LightRecordTwoSided : 0.0f, 0.0f, 0.0f);
	record.AxisX = glm::vec4(area.AxisX, area.HalfExtents.x);
	record.AxisY = glm::vec4(area.AxisY, area.HalfExtents.y);
	return record;
}
```

1. **Lines 103–105:** the shared record function decides whether the face is drawn at all, and a face that is not drawn gives the empty record.
2. **Lines 110–111:** the position and the range, then the color, which holds the luminance times the light's color, with one over the range squared in `w`.
3. **Line 112:** the direction slot holds the face's normal, and the type `c_LightRect` in `w`.
4. **Line 114:** the :term[bounding sphere]{id=bounding-sphere} reaches the range plus the face's half diagonal.
5. **Lines 115–117:** the source slot holds the two-sided flag in place of a radius, and the two axes carry the half sizes in `w`.

The record keeps the face's center in `PositionRange.xyz` and the range in its `w`. A :term[bounding sphere]{id=bounding-sphere} of radius Range plus the face's half diagonal makes the light take part in the tests, the ranking and the clusters of every other light, as [the many-lights page](../light/many-lights.md) teaches. `AxisX` and `AxisY` carry the face's two half-axes with the half sizes in their `w`. `LightCompact.comp` and `CollectLights` copy the axes into `LightShape`, the buffer beside the light buffer, so `LightData` stays 64 :term[bytes]{id=byte}.

### Rect lights: diffuse light

Diffuse light needs the form factor: the share of the receiver's cosine-weighted hemisphere that the face fills. For a face wholly above the receiver's horizon, the form factor is a sum over the face's four edges. Each edge adds the angle it spans, seen from the receiver, divided by $2\pi$, along the normal of the plane through the edge and the receiver. The :term[dot product]{id=dot-product} of the sum with the receiver's normal is the form factor, and the light's :term[irradiance]{id=irradiance} is $\pi L$ times it. Strata computes this exactly, and cuts the face at the receiver's horizon first when it dips below it; the toy's `FormFactor` does the same sum without the cut.

Strata uses a cheap fit in place of an arc cosine. It computes each edge's :term[cross product]{id=cross-product} from the face's exact axes, so that a small or far light keeps its precision. There is no sampling, so the result is the same in every frame.

### Rect lights: the highlight

The highlight is harder, because the exact lobe has no closed-form integral over a polygon. The 2016 paper's idea is to fit the lobe with a shape that has one: the clamped cosine, the same shape that a diffuse surface has. A linear transform of directions, a stretch and a shear that a three-by-three matrix describes, bends a cosine into a lobe that matches the exact one closely, for one roughness and one view angle. The lobe's integral over a polygon then equals the cosine's integral over the transformed polygon, and that one is the edge sum above.

```mermaid caption="The highlight of a rect light. A table holds a transform for each roughness and view angle. The face goes through the transform, and the closed edge sum of a cosine over the new face gives the share of the lobe that the light covers." alt="A flow chart from left to right. The roughness and the view angle select a transform in a table. The rectangle's four corners go through that transform and become a new polygon. The closed edge sum of the cosine over that polygon gives the covered share of the lobe, which is multiplied by the surface's reflectance and the light's luminance."
flowchart LR
    A["Roughness and view angle"] --> B["Table: inverse transform"]
    C["Face corners"] --> D["Transformed polygon"]
    B --> D
    D --> E["Cosine edge sum over the polygon"]
    E --> F["Covered share of the lobe"]
    F --> G["Times reflectance and luminance"]
```

The table is the published fit of the 2016 paper, copied value for value: two layers of 64 by 64 entries of four numbers, made by `Tools/ConvertLTCTable.py`. Layer 0 holds the transform, layer 1 holds a term for the horizon. The shader reads four entries and weighs them itself, because linear filtering of 32-bit numbers is an optional feature of graphics devices. The function below picks the transform and shades.

```slang src="Strata/shaders/Include/AreaLights.slang#L294-L299"
float AreaSpecularFraction(float3 position, float3 normal, float3 view, float roughness, AreaLight light)
{
	float cosine = SaturateArea(dot(normal, view));
	float2 uv = float2(max(roughness, c_MinRoughness), sqrt(max(1.0 - cosine, 0.0)));
	return GetAreaLobeCoverage(SampleAreaLightTable(ST_AREA_TABLE_TRANSFORM, uv), position, normal, view, light);
}
```

Line 297 builds the table coordinates: the :term[perceptual roughness]{id=perceptual-roughness}, at least the smallest one, and the square root of 1 minus the cosine of the view angle. Line 298 loads the transform, and `GetAreaLobeCoverage` takes the face through it, cuts the face at the receiver's horizon before and after the transform, and returns a share between 0 and 1. The share, multiplied by the surface's :term[reflectance]{id=reflectance} from the table of the energy page and by its `SpecularEnergy`, is the highlight, so rect, point and image light agree on energy.

### Rect lights: the branch and the clear coat

The forward loop sends a light of type rect and above to its own branch. Look at the weights, the two lines that load the face and shade, and how the loop skips the point-light code.

```slang src="Strata/shaders/Scene/Forward.frag.slang#L331-L347"
if (uint(light.DirectionType.w) >= ST_LIGHT_RECT)
{
#ifdef ST_FORWARD_GLASS
	float areaDiffuseWeight = diffuseWeight;
#else
	float areaDiffuseWeight = 1.0;
#endif
	float areaSpecularWeight = 1.0 - u_Frame.MaterialParams.w;
	// The views of one kind of light keep the rect light's of that kind alone, as LightSurface does for the others
	// (branches on the uniform view: other frames shade with the weights of before).
	uint areaView = GetLightingView();
	if (areaView == ST_LIGHTING_VIEW_SPECULAR)
		areaDiffuseWeight = 0.0;
	else if (areaView == ST_LIGHTING_VIEW_DIFFUSE)
		areaSpecularWeight = 0.0;
	AreaLight area = LoadAreaLight(light, u_LightShapes[lightIndex]);
	float3 areaColor = ShadeAreaLight(surface, coat, coatDFG, dfg, areaDiffuseWeight, area, areaSpecularWeight);
```

1. **Lines 333–337:** glass weights the diffuse light by what it does not transmit, and a surface that is not glass takes all of it.
2. **Line 338:** a reflection probe's capture sets `MaterialParams.w` to 1, which turns the highlight off, because a highlight depends on where it is seen from.
3. **Lines 341–345:** the lighting debug views keep one kind of light, diffuse or specular.
4. **Line 346:** the face comes from `u_LightShapes` at the same index as the light.
5. **Line 347:** one function shades the face; the code after it multiplies the shadow, which [the local shadows page](../light/local-shadows.md) teaches, and the branch ends with `continue`.

A rect light's `SpotAngles.w` holds its shadow mask layer and not a source radius, and the branch ends before the point-light code, so a rect light never calls `GetSourceLobeAlpha2`. The function that does the shading is the last piece.

```slang src="Strata/shaders/Include/AreaLights.slang#L319-L343"
float3 ShadeAreaLight(SurfaceData surface, ClearcoatData coat, float2 coatDFG, float2 dfg, float diffuseWeight, AreaLight light, float specularWeight)
{
	if (GetAreaLightSide(surface.Position, light) == 0.0)
		return float3(0.0);
	float window = GetAreaLightRangeWindow(surface.Position, light);
	if (!(window > 0.0))
		return float3(0.0);

	float3 reflectance = surface.F0 * dfg.x + dfg.y;
	float formFactor = AreaLightFormFactorClipped(surface.Position, surface.Normal, light);
	float3 result = surface.Albedo * ((1.0 - surface.Metallic) * formFactor * diffuseWeight) * (float3(1.0) - reflectance);
	if (specularWeight > 0.0)
	{
		float fraction = AreaSpecularFraction(surface.Position, surface.Normal, surface.View, surface.Roughness, light);
		result += reflectance * surface.SpecularEnergy * (fraction * specularWeight);
	}
	if (coat.Strength > 0.0)
	{
		float coatReflectance = coat.Strength * (c_ClearcoatF0 * coatDFG.x + coatDFG.y) * coat.SpecularEnergy;
		result *= 1.0 - coatReflectance;
		if (specularWeight > 0.0)
			result += float3(AreaSpecularFraction(surface.Position, coat.Normal, surface.View, coat.Roughness, light) * coatReflectance * specularWeight);
	}
	return light.Radiance * (result * window);
}
```

1. **Lines 321–325:** behind a one-sided face, on its plane or out of range the light adds nothing, with no further work.
2. **Lines 327–329:** the diffuse light is the exact form factor times the :term[albedo]{id=albedo}, times what the highlight leaves: one minus the specular reflectance.
3. **Lines 330–334:** the highlight is the covered share times the reflectance and the :term[energy compensation]{id=energy-compensation}, unless a probe capture asked for no highlight.
4. **Lines 335–341:** a clear coat reflects part of the light before it reaches the base. The base loses that share, and the coat adds its own lobe, at its own roughness and normal, times what it reflects.
5. **Line 342:** the luminance times the result times the range window, which falls from 1 at the face to 0 at the range.

The clear coat therefore costs a third evaluation of the integral for each pixel and light, and nothing else. [The clear coat page](../light/clearcoat-transmission.md) teaches the coat itself.

### What a rect light costs and where its fit is weaker

A rect light adds a few hundred arithmetic operations and eight table reads to each pixel it reaches: four for the lobe's transform and four for its horizon term. The diffuse light uses no table, and a clear coat adds a third integral and eight more reads.

A scene that has any rect light, lit or not, draws all its surfaces with larger shaders, and the showcase's opaque pass takes 2.7 % longer at Medium. Scenes without a rect light pay nothing. The highlight is the published fit, which is less exact than the exact lobe at grazing views of medium roughness. Seen 87 degrees from the normal, a face in the mirror direction gets 1.1 to 1.4 times the exact light at roughness 0.25.

### Rect lights in the editor and in scripts

The Hierarchy's Create menu has a **Rect Light** entry, and the context menu of an emissive mesh has **Make Area Light**, also in the Inspector. It runs the command `lighting.makeAreaLight`. The command adds a rect light as a child on the mesh's emitting face, with the mesh's size and its emission as the Intensity in nits, and it tags the mesh `LightSurface`. The tag keeps a panel's glow from counting twice: reflections show the light's highlight in place of the panel's image, probe captures draw the panel dark, and the light's own shadows skip the panel. Scripts reach the light by name, as for any component: `AddComponent("RectLight")` and `SetProperty("RectLight", "Width", 1.5f)`.

## What Strata does not do

At the pin, the rect light is the only shape: Strata has no disk, sphere or tube lights, and its release notes list disk lights as planned for a later wave. A point or spot light's source radius gives no diffuse light and no softer shadow: the penumbras of local lights come from a filter radius, not from the lamp's size. Rect lights are not yet part of global illumination, so a scene with it counts a light surface's light twice, and the notes advise looking at such scenes with global illumination off. Strata has no representative point code either: the sun, bulbs and flames use the lobe, and panels use the table.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Representative point for every light | The 2013 course notes of Unreal Engine 4 describe it | A cheap, shaped highlight for spheres and tubes | A different energy correction for each shape, and diffuse light that stays a point's |
| Linearly transformed cosines for every light | The 2016 paper that introduced it | Exact diffuse light and highlights for lamps with a size, with no change to the sun | Table reads and a few hundred operations for every pixel and every light, and shapes that point lights do not have |
| Sampling the light's surface | Ray-traced renderers and film renderers | Exact results for any shape, shadows included | Noise, which needs many samples or a history that Strata's lights avoid |

## How it is tested

Four groups of tests guard the page. The suite `GPU.SceneRenderer.Lighting` holds the sized-highlight cases: `A sized sun widens its highlight to its disk and keeps its light` compares the half-peak radius of a mirror's glint with the disk's, and its sums at 5 and 10 degrees must agree within 5 %. `A point light's source radius widens its highlight to the bulb's mirror image and keeps its light` does the same for a bulb, and checks that a rough surface's light and the shadow atlas stay the same. In the suite `Renderer.RenderScene`, the test `A light's source radius reaches its record` checks the clamp and the copy into `Source.x`.

The suite `Renderer.AreaLights` runs on the processor with no GPU: it checks the tables, the form factors, the horizon cases and the fit against the exact lobe. The suite `GPU.SceneRenderer.AreaLights` renders planes under rect lights and compares every pixel with `AreaLights::Shade`; its white furnace case checks the energy. Run a suite directly with `StrataTests.exe --test-suite=Renderer.AreaLights`, and the GPU suites through `ctest --preset windows-debug -R StrataTests.GPU`.

## Changing it safely

Change a rect light's shading in three places together: `AreaLights.h` and `.cpp`, `Include/AreaLights.slang` and the test `GPU.SceneRenderer.AreaLights`. Reason: the processor's version is the contract that the test compares every pixel with. Change a lobe formula for the sun and for bulbs together, `GetSunLobeAlpha2` and `GetSourceLobeAlpha2`, because they must give the same alpha for the same angle. The bulb's test compares a distant bulb with the sun's disk.

Keep a widened lobe normalized, and run the white furnace cases after any change to the distribution. Keep scenes without rect lights bit for bit: the rect branch lives only in the separate forward shaders that Strata compiles for scenes with rect lights. A new per-light value goes to a parallel buffer, as `LightShape` does, so that `LightData` stays 64 bytes. A direct write to a light component field must signal the change, as every cached field must.

## What went wrong before

An early version of the highlight shading used the fitted lobe whole. The fit reaches a little below the receiver's horizon on the viewer's side, where the exact lobe has nothing. A rect light therefore drew a faint second image of its face on a polished metal ball. Strata now cuts the face at the receiver's horizon before the transform. The regression tests are `A rect light under a surface's horizon puts no ghost of its face on it` in `GPU.SceneRenderer.AreaLights` and the horizon cases of `Renderer.AreaLights`.

## Summary

- A sized highlight widens only the distribution $D$ and keeps it normalized, so the lobe's energy is unchanged and its peak falls; widening the visibility or skipping the normalization would add light.
- A source adds $(\tan\theta / 1.287)^2$ to the lobe's alpha squared, less what the smallest roughness spreads already: the sun's on the processor, a bulb's per pixel.
- A light's size travels from its component through `LightRecord::Source.x` and `LightData::SpotAngles.w`, or `ReflectionParams.w` for the sun, to `GetLobeAlpha`.
- A rect light takes its intensity in nits or lumens, with $L = P / (\pi A)$, and gets exact diffuse light from its form factor and a highlight from linearly transformed cosines.
- Choose a sized point light for a small flame or bulb whose highlight matters, and a rect light for a panel or sign whose shape and nearby diffuse light matter.

## Check yourself

1. A designer raises a lantern's Source Radius from 0.05 to 0.5 m to get softer light on a wall. What happens? (a) the wall's light softens (b) the wall's brightness stays and glossy surfaces show a wider, dimmer highlight (c) the lantern's shadows blur (d) the lantern gets brighter

   :::answer{tests="energy-kept choose-light"}
   (b). The radius widens only the distribution, so the highlights spread and their peaks fall, and the diffuse light of the wall stays as it was. (a) and (c) are the mistake of rule 3: the radius sizes no diffuse light and no shadow. (d) would need a lobe that gains energy, which the normalization prevents.
   :::

2. A sun of 5 degrees across shines on a mirror. What alpha squared does the sun add? Use $\tan 2.5^\circ = 0.04366$.

   :::answer{tests="lobe-alpha"}
   The angular radius is 2.5 degrees, so $\alpha_s = 0.04366 / 1.287 = 0.03392$ and $\alpha_s^2 = 1.1505 \times 10^{-3}$. Less $0.045^4 = 4.1 \times 10^{-6}$, the sun adds $1.146 \times 10^{-3}$.
   :::

3. Through which field does a point light's `SourceRadius` reach the function that works out its lobe? (a) `FrameConstants::ReflectionParams.w` (b) `LightData::SpotAngles.w` (c) `LightShape::Parameters` (d) `LightData::Color.w`

   :::answer{tests="trace-size"}
   (b). The record's `Source.x` is copied into `SpotAngles.w`, and `GetSourceLobeAlpha2` reads it. (a) is the sun's path, (c) holds a rect light's two-sided flag and its area, and (d) holds one over the range squared.
   :::

4. A two-sided rect light of 2 by 1 m has Intensity 1,200 and Units Lumens. What luminance does each face have?

   :::answer{tests="rect-units"}
   The area is 2 m$^2$, and the divisor is $\pi \times 2 \times 2 = 12.57$, so each face has $1200 / 12.57 = 95.5$ nits. A one-sided light of the same power would have 191 nits.
   :::

5. A fire pit and a ceiling panel above a desk. Which light type fits each?

   :::answer{tests="choose-light"}
   The fire pit fits a point light with a Source Radius of about 0.25 m: only its highlights on wet or shiny things need a size. The panel fits a rect light, because the light on the desk depends on the panel's shape and nearness, and a point would give too much light there.
   :::

## Exercises

1. **Basic.** A one-sided 1 by 0.5 m rect light has 100 lumens. Find its luminance and its luminous intensity along the axis, and compare it with a point light of 100 lumens.

   :::answer[Worked solution]{tests="rect-units"}
   $L = 100 / (\pi \times 0.5) = 63.7$ nits. The intensity along the axis is $L \times A = 31.8$ cd, which is $P / \pi$. A point light of 100 lumens has $100 / 4\pi = 7.96$ cd, four times less along the axis: the panel sends its light into a hemisphere, where the point spreads it over a whole sphere.
   :::

2. **Medium.** Write a sketch that prints the alpha squared that a lantern bulb of 0.04 m and a fire of 0.25 m add at 1, 3 and 10 m. Print the resulting alpha on a mirror and on wet ground too.

   :::answer[Worked solution]{tests="lobe-alpha" solution="sketches/light-area-lights-radius.cpp"}
   The sketch repeats `GetSourceLobeAlpha2` in double precision and prints one line per radius and distance.

   ```cpp sketch="light-area-lights-radius.cpp"
   #include <algorithm>
   #include <cmath>
   #include <cstdio>

   constexpr double c_LobeHalfMaximum = 1.2871885;
   constexpr double c_MinRoughness = 0.045;

   // The alpha^2 a sphere of `radius` at `distance` adds to a highlight's lobe (as PBR.slang's GetSourceLobeAlpha2).
   double GetSourceAlpha2(double radius, double distance)
   {
   	const double sine2 = std::min(radius * radius / (distance * distance), 0.5);
   	const double minAlpha2 = std::pow(c_MinRoughness, 4.0);
   	return std::max(sine2 / ((1.0 - sine2) * c_LobeHalfMaximum * c_LobeHalfMaximum) - minAlpha2, 0.0);
   }

   int main()
   {
   	const double mirrorAlpha = c_MinRoughness * c_MinRoughness;
   	const double wetAlpha = 0.03;
   	for (const double radius : { 0.04, 0.25 })
   	{
   		for (const double distance : { 1.0, 3.0, 10.0 })
   		{
   			const double added = GetSourceAlpha2(radius, distance);
   			std::printf("radius %.2f m at %4.1f m: adds %.6f, mirror alpha %.4f, wet ground alpha %.4f\n", radius, distance, added,
   				std::sqrt(mirrorAlpha * mirrorAlpha + added), std::sqrt(wetAlpha * wetAlpha + added));
   		}
   	}
   	return 0;
   }
   ```

   ```text output-of="light-area-lights-radius.cpp"
   radius 0.04 m at  1.0 m: adds 0.000963, mirror alpha 0.0311, wet ground alpha 0.0432
   radius 0.04 m at  3.0 m: adds 0.000103, mirror alpha 0.0104, wet ground alpha 0.0317
   radius 0.04 m at 10.0 m: adds 0.000006, mirror alpha 0.0031, wet ground alpha 0.0301
   radius 0.25 m at  1.0 m: adds 0.040233, mirror alpha 0.2006, wet ground alpha 0.2028
   radius 0.25 m at  3.0 m: adds 0.004217, mirror alpha 0.0650, wet ground alpha 0.0715
   radius 0.25 m at 10.0 m: adds 0.000373, mirror alpha 0.0194, wet ground alpha 0.0357
   ```

   1. **Lines 9–14:** the shader's function again, in double precision.
   2. **Lines 18–19:** a mirror's alpha is the smallest roughness squared, and wet ground has 0.03.
   3. **Line 24:** the share that a source of this radius and distance adds.
   4. **Lines 25–26:** the lobe's alpha is the square root of the surface's alpha squared plus the added share.

   The bulb widens even a mirror to 0.031 at 1 m, and to 0.003 at 10 m, where it is about as small as the sun's 0.0036. The fire at 1 m gives 0.20 on both surfaces: it dominates the surface's own roughness, so a mirror and wet ground show the same patch.
   :::

3. **Medium.** Trace it yourself: with a search, follow the sun's Angular Diameter from the component to the frame constants, and a bulb's `SourceRadius` from the record to the cluster loop.

   :::answer[Worked solution]{tests="trace-size"}
   Search the engine for `GetSunLobeAlpha2`. The call is in `SceneRenderer.cpp`, in the :term[lambda]{id=lambda} that uses the directional light, and it writes `frame.ReflectionParams.w` from `light.ShadowSoftness`; the function is in `SceneRenderData.h`. For the bulb, search for `GetSourceLobeAlpha2`: the call is in `Scene/Forward.frag.slang`'s cluster loop, and it reads `light.SpotAngles.w`. Search for `Source.x` to find who writes it: `RenderLights::MakeRecord` clamps the radius into the record, `CollectLights` in `SceneRenderer.cpp` copies it on the processor path, and `Scene/LightCompact.comp.slang` copies it on the GPU path. Both ends meet in `GetLobeAlpha` in `Include/PBR.slang`, which widens only $D$.
   :::

4. **Hard.** Sketch where a rect light enters `LightRecord`, `LightData`, the clusters and `ShadeLitSurface`, then compare your sketch with Strata's code.

   :::answer[Worked solution]{tests="trace-size choose-light"}
   The component's size and units become a luminance and a record in `RenderLights::MakeAreaRecord`, which holds the center, the range, the luminance times the color, the normal, a bounding sphere and two axes. The culling passes copy the record into `LightData` and its axes into a parallel `LightShape`. The cluster pass tests only the bounding sphere, so a rect light needs no new cluster code. `ShadeLitSurface` loops over the cluster, branches on the type and calls `ShadeAreaLight`. The real code adds a range window, a branch for the debug views and the shadow masks that a first sketch forgets.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Renderer/SceneRenderData.h`: `GetSunLobeAlpha2`, `LightRecord`, `LightData` and `LightShape`.
- `Strata/shaders/Include/PBR.slang`: `GetSourceLobeAlpha2`, `GetLobeAlpha` and `EvaluateLightWeighted`.
- `Strata/src/Strata/Renderer/AreaLights.h` and `AreaLights.cpp`: the rect light's shading on the processor; `Strata/shaders/Include/AreaLights.slang`: the same on the GPU.
- `Strata/src/Strata/Renderer/RenderLights.cpp`: `MakeAreaRecord` and the clamp of the source radius.
- `Strata/src/Strata/Renderer/RendererComponents.h`: `RectLightComponent` and `LightSurfaceComponent`.
- Tests: `GPU.SceneRenderer.Lighting`, `Renderer.RenderScene`, `Renderer.AreaLights` and `GPU.SceneRenderer.AreaLights`.
- Command: `lighting.makeAreaLight`; editor: **Rect Light** in the Hierarchy's Create menu.

## Further reading

- Brian Karis, "Real Shading in Unreal Engine 4" (SIGGRAPH 2013 course notes): the representative point and sphere normalization; intermediate.
- Eric Heitz, Jonathan Dupuy, Stephen Hill and David Neubelt, "Real-Time Polygonal-Light Shading with Linearly Transformed Cosines" (ACM Transactions on Graphics, 2016): the method and its tables; advanced.
- Stephen Hill and Eric Heitz, "Real-Time Area Lighting: a Journey from Research to Production" (SIGGRAPH 2016 course notes): the clipless form and production advice; advanced.
