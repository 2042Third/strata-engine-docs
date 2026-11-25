---
id: light/fog
title: "Height fog"
description: "How Strata draws haze that thickens toward the ground: the closed-form integral along each view ray, the light the fog scatters and what it cannot do."
kind: internals
size: M
tracks: [E]
needs: [light/atmosphere]
time: 55
learn:
  - id: tune-fog
    text: choose the density, falloff and base height of a fog from the distance and the thickness a scene needs
  - id: derive-integral
    text: compute the optical depth and the opacity of a view ray from the closed form, and explain why the shader writes it without overflow
  - id: fog-light
    text: name the light that the fog scatters in each case, and the effects that a fog without a volume cannot make
  - id: trace-density
    text: trace the density of a fog from the component to the forward pass and the sky
since: 0.6.0
status: final
---

A valley at dawn is clear overhead and milky at the ground, because the air near the ground holds more water than the air above. **Height fog** is Strata's version of that look. It is a haze whose density falls with height, applied to every pixel by a few instructions in the :term[shader]{id=shader} that colors it, with no extra pass and no volume. This page shows how the fog is computed. It explains why the formula is written as it is, and what the method cannot draw.

## The problem and how engines solve it

Air is never perfectly clear. Each metre of it absorbs a small share of the light that crosses it and sends another share in other directions. Along a ray, the optical depth $\tau$ of [the atmosphere page](../light/atmosphere.md) adds up this loss: the surface keeps the fraction $e^{-\tau}$ of its color, and the fog's own light fills the rest. That rest, $1 - e^{-\tau}$, is the fog's opacity.

Three families of methods draw it. Distance fog gives the air one density everywhere, so the loss depends on the distance $d$ alone: $1 - e^{-\rho d}$ for a density $\rho$. It costs one line of shader code, but it cannot make a fog that lies in a valley, because the air has the same density at the peak and at the floor.

Analytic height fog lets the density fall with height and finds the loss along each ray by a formula. Wenzel described this for games in 2006, and Unreal's exponential height fog uses it too. It keeps the cost of distance fog, and the fog hugs the ground. Its price is that the air is a formula and not a place: it cannot hold a shadow or a shaft of light, because the shader never asks which part of the ray is lit.

Froxel volumetric fog stores the air in a grid of small cells, shaped like the camera's view, called froxels. Wronski described it in 2014. Each cell collects the light that reaches it, with shadows, and each pixel reads its ray's total from the grid. Light shafts, local lights glowing in the haze and fog of any shape all work. The price is a grid to fill every frame, memory for it, and a cost that grows with its size.

Strata uses a froxel grid for the :term[aerial perspective]{id=aerial-perspective} of the atmosphere page, but chose the formula for height fog. The scenes it serves (a valley, a morning, a swamp) need a haze that costs almost nothing. [Alternatives Strata did not choose](#alternatives-strata-did-not-choose) lists what that choice costs.

## The map: one component, one function, three shaders

The component stores your values. Once a frame, the :term[renderer]{id=renderer} finds the active component and turns its values into numbers for the shader. The forward shader fogs each surface after the haze of the air, and the sky shader fogs the sky behind everything.

```mermaid caption="The fog component's values become frame constants once per frame. The forward shader fogs surfaces after aerial perspective, the sky shader fogs the sky, and both call the same fog functions." alt="Flow of boxes. The fog component leads to a function that finds the first active one, then to one that fills the frame constants. These feed the forward shader and the sky shader, and both call the fog include file."
flowchart LR
  C["HeightFogComponent"] --> F["SceneRenderer::FindHeightFog"]
  F --> S["SceneRenderer::SetHeightFog"]
  S --> K["frame constants Fog*"]
  K --> FW["Forward.frag: ApplyAerialPerspective, then ApplyHeightFog"]
  K --> SK["Skybox.frag: ApplyHeightFogToSky"]
  FW --> I["Include/Fog.slang"]
  SK --> I
```

The left half lives in `Strata/src/Strata/Renderer/SceneRenderer.cpp`, the right half in `Strata/shaders/Include/Fog.slang`, which the forward shader and the sky shader include.

## The contract: what you set and what the renderer promises

The component `HeightFogComponent`, named **Height Fog** in the **Rendering** category of the inspector, has eight fields. The first four describe the air, the last four its look.

| Field | Default | Meaning |
| --- | --- | --- |
| `Density` | 0.02 | Extinction per metre at the base height. |
| `HeightFalloff` | 0.2 | Per metre: the density falls by the factor $e$ (about 2.72) every $1/\text{falloff}$ metres above the base. |
| `BaseHeight` | 0 | World height in metres where the density equals `Density`. |
| `StartDistance` | 0 | Metres from the camera before which there is no fog. |
| `MaxOpacity` | 1 | The most that the fog hides of what lies behind it. |
| `Color` | (0.7, 0.8, 0.9) | Linear :term[albedo]{id=albedo}: the fraction of its light that the fog scatters toward the viewer. |
| `ColorFromSky` | on | The sky lights the fog; off, `Color` is the fog's own :term[radiance]{id=radiance}. |
| `SunScattering` | 0.5 | From 0 (the directional light scatters equally in every direction) to 1 (a glow around the light). |

The renderer makes these promises, each for a reason:

1. **One fog applies.** The first active entity with the component wins, and an entity that is inactive in the hierarchy never counts. Two fogs would need a rule for mixing them, and a scene has one air.
2. **Every value is finite.** The renderer replaces a value that is not finite by a safe one (density 0, `StartDistance` 0, `MaxOpacity` 1, `SunScattering` 0). A file or a command can write any bits, and one infinity in a shader blackens a frame.
3. **The falloff stays above zero.** The smallest value is `c_MinHeightFalloff`, 0.0001. A falloff of 0 gives the same density at every height, so the optical depth of a ray that climbs toward the sky never ends.
4. **The camera's height is subtracted in double precision.** A game far from the origin keeps the height above the base exact, because the subtraction happens where a double holds both large numbers, and the shader receives a small one.
5. **A density of 0 changes nothing.** The pixel comes back unchanged to the bit.
6. **There is no volume.** Fog never receives a shadow, never shows light shafts, and never glows around a point or spot light.

:::rule[Scene shaders work in camera-relative space]
Positions reach the shader relative to the camera, so a world far from the origin keeps its precision. The fog follows the rule: the shader sees only the camera's height above the base. [Conventions](../core/conventions.md) states the rules of the engine's code.
:::

## A toy version: the integral by hand, and by machine

A ray's optical depth is the sum of the extinction of its small pieces. When the density changes along the ray, the sum becomes an integral, and for a density that falls with height, you can solve it with no loop.

At a height $h$ above the base the extinction is $\sigma(h) = \rho e^{-kh}$. Here $\rho$ is `Density` in 1/m, $k$ is `HeightFalloff` in 1/m, and $e^{x}$ is the :term[exponential function]{id=exponential-function}: 1 for $x = 0$, falling toward 0 as $x$ grows negative.

$$\sigma(h) = \rho\, e^{-kh}$$

Now a ray. The camera is $s$ metres above the base. The ray climbs $u$ metres per metre travelled, where $u$ is the vertical part of its unit direction: 0 for a level ray, 1 for straight up. The surface lies $D$ metres away. At distance $t$ along the ray the height is $s + ut$, so the optical depth is the integral of the extinction.

$$\tau = \int_0^D \rho\, e^{-k(s+ut)}\,dt = \rho\, e^{-ks}\,\frac{1 - e^{-kuD}}{ku}$$

In this formula $t$ is the distance along the ray in metres, and the integral adds the extinction of every piece from 0 to $D$. The right side uses the rule that the integral of $e^{-ct}$ is $-e^{-ct}/c$. For a level ray, $u = 0$ and the fraction has no value; the limit is $\rho e^{-ks} D$, the density at the camera times the distance.

:::example[A fog of the default values, three rays]
The camera is 2 m above the base, with $\rho = 0.02$ and $k = 0.2$. A level ray to a wall 20 m away has $\tau = 0.02 \times 20 \times e^{-0.4} = 0.268$, so the opacity is $1 - e^{-0.268} = 0.235$, and the wall keeps 76.5 % of its color. A ray that climbs 10 m over its 20 m leaves the thick air near the camera: $\tau = 0.116$ and the opacity is 0.110. A ray that falls 10 m dives into thicker air: $\tau = 0.857$ and the opacity is 0.575.
:::

The formula has two traps for a shader. For a ray that falls, $kuD$ is negative and $e^{-kuD}$ is large. For a nearly level ray, the fraction is 0 over almost 0. The shader avoids both by measuring from the ray's lowest point. The depth is the density at that point, times the distance, times a mean $m$ that always lies between 0 and 1.

$$\tau = \rho\, D\, e^{-k h_{low}}\, m(y), \qquad m(y) = \frac{1 - e^{-y}}{y}$$

Here $h_{low}$ is the height of the ray's lowest point above the base, $s + \min(uD, 0)$ in metres, where $\min$ takes the smaller of two numbers. The symbol $y = k\,|uD|$ is the height difference along the ray in units of the falloff, where $|\cdot|$ is the absolute value. For small $y$ the shader uses $1 - y/2$, the start of the series of $m$, so 0 over 0 never occurs.

:::question
The sketch uses loops and functions ([programming 2](../basics/programming-2.md)), `std::exp(` calls and a struct with fields ([programming 3](../basics/programming-3.md)).
:::

The sketch checks the closed form against a sum of 100,000 small pieces. Its `rise` is $uD$, the height the ray climbs over its distance. For the three rays of the example, it prints the sum, the closed form and the opacity. Then it prints the depth toward the sky of a 30-degree ray ($u = 0.5$) and the :term[phase function]{id=phase-function} that the real code section explains. Compare the first two numbers of each line.

```cpp sketch="light-fog-toy.cpp"
#include <algorithm>
#include <cmath>
#include <cstdio>

struct Fog
{
	double Density = 0.02;
	double Falloff = 0.2;
};

// Adds up the extinction of many short pieces of the ray.
double NumericDepth(const Fog& fog, double startHeight, double rise, double distance)
{
	const int steps = 100000;
	double depth = 0.0;
	for (int step = 0; step < steps; step++)
	{
		const double fraction = (step + 0.5) / steps;
		const double height = startHeight + rise * fraction;
		depth += fog.Density * std::exp(-fog.Falloff * height) * distance / steps;
	}
	return depth;
}

// The same integral in closed form, written like the shader: the density at the lowest point
// times the distance times a mean in (0, 1], so no exponent grows.
double ClosedDepth(const Fog& fog, double startHeight, double rise, double distance)
{
	const double lowest = startHeight + std::min(rise, 0.0);
	const double y = fog.Falloff * std::abs(rise);
	const double mean = y > 1.0e-4 ? (1.0 - std::exp(-y)) / y : 1.0 - 0.5 * y;
	return fog.Density * distance * std::exp(-fog.Falloff * lowest) * mean;
}

double Phase(double g, double cosTheta)
{
	const double denominator = 1.0 + g * g - 2.0 * g * cosTheta;
	return (1.0 - g * g) / (4.0 * 3.14159265358979 * denominator * std::sqrt(denominator));
}

int main()
{
	const Fog fog;
	const double distance = 20.0;
	const double rises[] = { 0.0, 10.0, -10.0 };
	for (double rise : rises)
	{
		const double numeric = NumericDepth(fog, 2.0, rise, distance);
		const double closed = ClosedDepth(fog, 2.0, rise, distance);
		std::printf("rise %5.1f m: numeric %.5f, closed %.5f, opacity %.4f\n", rise, numeric, closed, 1.0 - std::exp(-closed));
	}
	const double toSky = fog.Density * std::exp(-fog.Falloff * 2.0) / (fog.Falloff * 0.5);
	std::printf("sky above 30 degrees: depth %.5f, opacity %.4f\n", toSky, 1.0 - std::exp(-toSky));
	std::printf("phase, SunScattering 0.5: toward %.4f, away %.4f\n", Phase(0.45, 1.0), Phase(0.45, -1.0));
	return 0;
}
```

```text output-of="light-fog-toy.cpp"
rise   0.0 m: numeric 0.26813, closed 0.26813, opacity 0.2352
rise  10.0 m: numeric 0.11592, closed 0.11592, opacity 0.1095
rise -10.0 m: numeric 0.85654, closed 0.85654, opacity 0.5754
sky above 30 degrees: depth 0.13406, opacity 0.1255
phase, SunScattering 0.5: toward 0.3814, away 0.0208
```

1. **Lines 16–21:** the slow way: the extinction of 100,000 pieces, each at its own height.
2. **Lines 29–32:** the closed form: the lowest point, the mean $m$ and its series, and the product.

Both columns match to five digits for rises of 0, +10 and -10 m, which is the claim of the closed form. The toy omits three things that the shader needs. It stops at a finite distance, so it has no answer for the sky. It has no color, no start distance and no cap on the opacity. And it uses doubles, so no :term[exponent]{id=exponent} ever grows past its type.

## The real code, in the order the data flows

The values reach the shader through `SetHeightFog`. Search for what happens to each input before it is stored: it is replaced when it is not finite, and the density and the falloff are clamped to their lowest allowed values.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L1476-L1484" from="const auto finiteOr" to="frame.FogColor = glm::vec4(glm::vec3(SanitizeRadiance(fog->Color)), std::clamp(finiteOr(fog->MaxOpacity, 1.0f), 0.0f, 1.0f));" symbol="SceneRenderer::SetHeightFog"
const auto finiteOr = [](float value, float fallback) { return std::isfinite(value) ? value : fallback; };
const float density = std::max(finiteOr(fog->Density, 0.0f), 0.0f);
const float falloff = std::max(finiteOr(fog->HeightFalloff, HeightFogComponent::c_MinHeightFalloff), HeightFogComponent::c_MinHeightFalloff);
const float startDistance = std::max(finiteOr(fog->StartDistance, 0.0f), 0.0f);
// The camera's height above the base height, subtracted in double so a camera far from the base keeps its precision.
constexpr double c_MaxHeight = 1.0e9;
const double height = static_cast<double>(camera.Position.y) - static_cast<double>(finiteOr(fog->BaseHeight, 0.0f));
frame.FogDensity = glm::vec4(density, falloff, static_cast<float>(std::isfinite(height) ? std::clamp(height, -c_MaxHeight, c_MaxHeight) : 0.0), startDistance);
frame.FogColor = glm::vec4(glm::vec3(SanitizeRadiance(fog->Color)), std::clamp(finiteOr(fog->MaxOpacity, 1.0f), 0.0f, 1.0f));
```

The camera's height above the base is the one value that comes from subtracting large numbers, and the code does it in `double` and clamps it to a billion metres. The toy needs no such guard because its inputs are literals; the engine reads them from files that anyone can edit.

The next piece chooses the sky's light. The first branch that matches wins.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L1489-L1498" from="if (!fog->ColorFromSky)" to="frame.FogLight = SanitizeRadiance(glm::vec3(frame.AmbientColor));" symbol="SceneRenderer::SetHeightFog"
if (!fog->ColorFromSky)
	frame.FogLight = glm::vec4(1.0f, 1.0f, 1.0f, 0.0f);
else if (m_AtmosphereFrame)
	frame.FogLight = glm::vec4(0.0f, 0.0f, 0.0f, 2.0f); // Its sky-view table at the horizon, read on the GPU
else if (m_SkyHorizon)
	frame.FogLight = glm::vec4(*m_SkyHorizon, 0.0f);
else if (frame.EnvironmentParams.w > 0.0f)
	frame.FogLight = glm::vec4(0.0f, 0.0f, 0.0f, 1.0f);
else
	frame.FogLight = SanitizeRadiance(glm::vec3(frame.AmbientColor));
```

1. **Line 1489:** With `ColorFromSky` off, white light makes the fog radiate its own `Color`.
2. **Lines 1491–1498:** The atmosphere, the :term[procedural sky]{id=procedural-sky}, the :term[environment map]{id=environment-map-equirectangular-hdr} and the ambient color follow in that order.

Without `ColorFromSky`, the light is plain white, so the fog radiates its own `Color`. With an atmosphere, the shader reads the sky's color at the horizon in the direction of the ray (`FogLight.w` is 2). With a :term[procedural sky]{id=procedural-sky}, the code stores the sky's horizon color, because the :term[irradiance]{id=irradiance} from above, mostly the top of the sky's color, would make a darker band where the fog meets the sky. With an :term[environment map]{id=environment-map-equirectangular-hdr}, the shader reads the map's irradiance from above (`w` is 1). With none of these, the ambient color lights the fog.

Now the shader. `GetFogOpticalDepth` is the toy's closed form in the same variables: `startHeight` is $s$, `rise` is $uD$ and `distance` is $D$.

```slang src="Strata/shaders/Include/Fog.slang#L22-L27" from="float falloff = u_Frame.FogDensity.y;" to="return u_Frame.FogDensity.x * distance * exp(min(-falloff * lowest, 80.0)) * mean;" symbol="GetFogOpticalDepth"
float falloff = u_Frame.FogDensity.y;
float lowest = startHeight + min(rise, 0.0);
float y = falloff * abs(rise);
float mean = y > 1.0e-4 ? (1.0 - exp(-y)) / y : 1.0 - 0.5 * y;
// The density first: a density of 0 stays 0 through the finite factors after it.
return u_Frame.FogDensity.x * distance * exp(min(-falloff * lowest, 80.0)) * mean;
```

The differences from the toy are the cap and the order. The exponent is capped at 80, and $e^{80}$ is about $5.5 \times 10^{34}$, which a 32-bit float holds (its limit is about $3.4 \times 10^{38}$). A ray that starts that deep in the fog is opaque long before the cap matters. The density multiplies first, so a density of 0 gives exactly 0 whatever the finite factors after it are.

The fog's light comes next. In `GetFogInscattering`, the sky's light is the same in every direction, and the sun's light is weighted by the :term[Henyey-Greenstein]{id=henyey-greenstein} phase function. That formula says how much light a cloud of particles scatters toward a direction, given its angle to the light's own direction. [The atmosphere page](../light/atmosphere.md) derives it; here only its use matters.

```slang src="Strata/shaders/Include/Fog.slang#L53-L58" from="float g = u_Frame.FogParams.y;" to="return u_Frame.FogColor.rgb * light;" symbol="GetFogInscattering"
	float g = u_Frame.FogParams.y;
	float cosTheta = dot(direction, -u_Frame.DirectionalLightDirection.xyz);
	float denominator = 1.0 + g * g - 2.0 * g * cosTheta;
	light += u_Frame.DirectionalLightColor.rgb * ((1.0 - g * g) / (4.0 * PI * denominator * sqrt(denominator)));
}
return u_Frame.FogColor.rgb * light;
```

The bias $g$ is `SunScattering` times `c_MaxSunAsymmetry` (0.9), so it never reaches 1, where the phase would be infinite toward the light. With the default 0.5, $g = 0.45$: the phase is 0.381 per :term[steradian]{id=steradian} looking straight at the sun and 0.021 looking away, a ratio of 18. With `SunScattering` at 1, $g = 0.9$ and the glow toward the sun is 15.1, against 0.080 for $g = 0$. The code multiplies the sum by the albedo `Color`, the one number that says how much light the fog sends on.

The blend turns an optical depth into the final color. The opacity is the smaller of $1 - e^{-\tau}$ and `MaxOpacity`, and the pixel mixes its own color with the fog's light.

```slang src="Strata/shaders/Include/Fog.slang#L61-L67" symbol="BlendFog"
// `color` seen through fog of the given optical depth along `direction`. With a depth of 0 the color comes back unchanged
// to the bit.
float3 BlendFog(float3 color, float3 direction, float opticalDepth)
{
	float opacity = min(1.0 - exp(-opticalDepth), u_Frame.FogColor.w);
	return color * (1.0 - opacity) + GetFogInscattering(direction) * opacity;
}
```

With $\tau = 0$ the opacity is exactly 0, and the first term returns the color to the bit: this is promise 5. Next, `ApplyHeightFog` finds where the ray starts and how much of it lies in the fog.

```slang src="Strata/shaders/Include/Fog.slang#L87-L95" from="float3 start;" to="return BlendFog(color, direction, GetFogOpticalDepth(startHeight, direction.y * distanceInFog, distanceInFog));" symbol="ApplyHeightFog"
float3 start;
float3 direction;
GetFogRay(relativePosition, start, direction);
float startDistance = u_Frame.FogDensity.w;
float distanceInFog = dot(relativePosition - start, direction) - startDistance;
if (!(distanceInFog > 0.0))
	return color;
float startHeight = u_Frame.FogDensity.z + start.y + direction.y * startDistance;
return BlendFog(color, direction, GetFogOpticalDepth(startHeight, direction.y * distanceInFog, distanceInFog));
```

A perspective ray starts at the camera and an orthographic one on the camera's plane; `GetFogRay` handles both. `StartDistance` shortens the ray: the code moves the start along the direction, and a pixel nearer than that returns its color untouched.

The sky has no distance: it is infinitely far. For a ray that climbs ($u > 0$) the integral converges, because the density dies away. In the closed form, $e^{-kuD}$ goes to 0 as $D$ grows, and $\tau = \rho e^{-ks}/(ku)$. A ray that is level or falls never leaves the fog, so its depth is the constant `c_FogEndlessDepth` ($10^{30}$), whose opacity is 1 before the `MaxOpacity` cap. This is why the sky below the horizon shows the cap, and why a falloff of 0 must be impossible: the rate $ku$ that divides the depth would be 0 for every ray.

```slang src="Strata/shaders/Include/Fog.slang#L104-L109" from="float startHeight" to="return BlendFog(color, direction, opticalDepth);" symbol="ApplyHeightFogToSky"
float startHeight = u_Frame.FogDensity.z + start.y + direction.y * u_Frame.FogDensity.w;
float rate = falloff * direction.y;
float opticalDepth = density > 0.0 ? c_FogEndlessDepth : 0.0;
if (rate > 0.0)
	opticalDepth = min(density * exp(min(-falloff * startHeight, 80.0)) / rate, c_FogEndlessDepth);
return BlendFog(color, direction, opticalDepth);
```

In the example, the sky along the 30-degree ray has $\tau = 0.02 \times e^{-0.4} / (0.2 \times 0.5) = 0.134$ and an opacity of 0.1255, while a finite wall at 20 m on that ray gets 0.110. The forward shader calls the aerial perspective first and the height fog second, for opaque and transparent surfaces alike. The value views of the lighting debug modes skip both.

## What each setting does to the picture

Each picture changes one field and holds the rest. Look at the far cube and at the horizon, where the long rays make the effect strongest.

::compare{id=density-sweep}

::compare{id=sun-scattering}

::compare{id=color-from-sky}

`MaxOpacity` below 1 leaves part of the distance visible and gives the sky at the horizon that opacity instead of full cover. A higher `HeightFalloff` squeezes the same fog toward the base, so the haze lies lower and the sky above it clears sooner.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Distance fog, one density everywhere | Older real-time engines | Simpler code | Fog that lies low, and a clear sky above it |
| Height fog with a second layer | Wenzel 2006; Unreal's exponential height fog | A thin ground layer under a wide haze | Constants per layer in the frame data, and a test for each |
| Froxel volumetric fog | Wronski 2014 | Light shafts, shadows in the haze, glow around local lights | A grid to fill each frame, its memory and a cost that grows with its size |
| Fog volumes: boxes of local fog | Not named in this page's sources | Fog in one room or one hollow | A pass to draw or march the boxes |

## How it is tested

The suite `GPU.SceneRenderer.Fog`, in `StrataTests/src/Renderer/GPUSceneFogTests.cpp`, needs a :term[graphics card]{id=gpu} and compares the picture with the same integral computed in double. It holds five test cases.

1. A wall seen through fog matches the integral along every pixel's ray, for rising and falling rays, with a start distance, a cap, a colored fog and the sun's phase. The worst pixel differs by at most 1 of 255.
2. The sky is fogged at an infinite distance: rays that never leave the fog get the cap's opacity.
3. Transparent surfaces are fogged like opaque ones at the same depth.
4. The first active fog applies.
5. A scene renders the same without fog, with a disabled fog and with a fog of density 0, bit for bit.

CTest runs it in one test with the other suites that need a graphics card, `ctest --preset windows-debug -R StrataTests.GPU`. To run it alone, call `build/windows/bin/Debug/StrataTests.exe --test-suite=GPU.SceneRenderer.Fog`. The feature test also checks that its scene's entity with the `HeightFog` component makes the frame report a fog.

## Changing it safely

A new field, such as a second layer, must appear everywhere in the flow. Touch the component and its registration in `Strata/src/Strata/Renderer/RendererComponents.cpp` (range and tooltip), `SetHeightFog` with its checks, the frame constants and `Fog.slang`. Add an exact test against a numeric sum, and an entry in the feature test.

Keep every term of the closed form bounded, as the cap of 80 and the mean $m(y)$ do, and keep a density of 0 bit-identical, or test 5 fails. A loop that marches along the ray in the shader would make the page's promise 6 false and belongs to the planned volumetric work.

## Summary

- Choose the density from the distance that hides half the view ($\ln 2 / \rho$ at the base), the falloff from the layer's thickness ($1/k$ per factor $e$), and the base height from the floor.
- The optical depth of a ray is the density at its lowest point times the distance times a mean $m(y)$ in $(0, 1]$; the opacity is $1 - e^{-\tau}$, capped by `MaxOpacity`.
- The fog scatters the sky's light (a horizon color, an irradiance or the ambient color) and the sun's through the :term[Henyey-Greenstein]{id=henyey-greenstein} phase, times its albedo. It has no volume, so it makes no shafts, no local lights and no shadows.
- `Density` runs from the component through `SetHeightFog` and the frame constants to `ApplyHeightFog` in the forward shader and `ApplyHeightFogToSky` behind it.

## Check yourself

1. A scene has `HeightFalloff` 0, and the sky at the horizon looks wrong. What does the renderer do, and why?

   - A. It uses 0, and every ray to the sky gets an infinite depth.
   - B. It uses `c_MinHeightFalloff`, 0.0001, so that the integral toward the sky stays finite.
   - C. It turns the fog off.

   :::answer{tests="derive-integral"}
   B. A is wrong: `SetHeightFog` replaces any smaller value by the minimum, because a falloff of 0 would give the same density at every height, and a rising ray would never leave the fog. C is wrong too: the fog stays on, and since 1/0.0001 is 10 km, the fog thins out only over that height.
   :::

2. With the default fog, a camera 2 m above the base looks level at a wall 35 m away. What opacity does the wall get?

   :::answer{tests="derive-integral,tune-fog"}
   $\tau = 0.02 \times 35 \times e^{-0.4} = 0.7 \times 0.670 = 0.469$, and the opacity is $1 - e^{-0.469} = 0.374$, so the wall keeps 62.6 % of its color. At the base height itself, $\tau = 0.7$ and the opacity is 0.503: the tooltip of `Density` says that 0.02 hides half at 35 m.
   :::

3. `MaxOpacity` is 0.5 and the camera looks at the sky below the horizon. Which opacity does the shader use?

   :::answer{tests="fog-light"}
   0.5. A ray that falls never leaves the fog, so `ApplyHeightFogToSky` gives it the endless depth, whose opacity $1 - e^{-10^{30}}$ is 1, and `BlendFog` takes the smaller of that and `MaxOpacity`.
   :::

4. A game maker asks for a beam of light through the fog from a window. What do you answer?

   :::answer{tests="fog-light"}
   Height fog cannot make it. The shader finds the depth of a ray with a formula and never asks which part of the ray is lit. A window's beam, a shadow in the fog and a glow around a lamp are therefore outside it, and volumetric fog is planned work.
   :::

5. Where does a density of 0 become exactly 0 in the frame, and where does the 0 come from?

   :::answer{tests="trace-density"}
   The 0 comes from the component, through `SetHeightFog`, into `frame.FogDensity.x`. In `GetFogOpticalDepth` the density multiplies first, so the optical depth is 0, and `BlendFog` computes an opacity of $1 - e^{0} = 0$: the pixel's color returns unchanged.
   :::

## Exercises

1. **Basic.** Plan a valley fog: the base at the floor, a layer about 50 m thick, and a density that hides half of a level view at 35 m. Which `HeightFalloff` and `Density` do you set, and how much does a camera 5 m above the floor see hidden at 35 m?

   :::answer[Worked solution]{tests="tune-fog,derive-integral"}
   A layer 50 m thick means the density falls by the factor $e$ over 50 m, so `HeightFalloff` is $1/50 = 0.02$. Half hidden means $e^{-\tau} = 0.5$, so $\tau = \ln 2 = 0.693$. Over 35 m at the base height, $\tau = 35\rho$, so `Density` is $0.693/35 = 0.0198$, about 0.02. From 5 m up, the density is lower by $e^{-0.02 \times 5} = 0.905$, so $\tau = 0.627$ and 46.6 % is hidden, slightly less than half. Set `BaseHeight` to the floor's height, and raise `SunScattering` toward 1 for a low sun.
   :::

2. **Medium.** Trace it yourself: follow `HeightFogComponent::Density` from the component to the forward pass and the sky with a search of the source, and name each file and function.

   :::answer[Worked solution]{tests="trace-density"}
   Search for `HeightFogComponent` and for `FogDensity`. The field is declared in `Strata/src/Strata/Renderer/RendererComponents.h`. `SceneRenderer::SetHeightFog` in `Strata/src/Strata/Renderer/SceneRenderer.cpp` reads it from the component that `FindHeightFog` returns, cleans it and stores it in `frame.FogDensity.x`; the frame setup calls it. In `Strata/shaders/Include/Fog.slang`, `GetFogOpticalDepth` and `ApplyHeightFogToSky` read it. `Strata/shaders/Scene/Forward.frag.slang` calls `ApplyHeightFog` after `ApplyAerialPerspective`, and `Strata/shaders/Scene/Skybox.frag.slang` calls `ApplyHeightFogToSky`.
   :::

3. **Hard.** Add a second exponential layer to the model: a thin, dense ground fog under the default one. Write the closed form for two layers, test it against a numeric sum, and say which parts of the engine a real second layer touches.

   :::answer[Worked solution]{tests="derive-integral,tune-fog" solution="sketches/light-fog-layers.cpp"}
   Extinctions add, so optical depths add: the total is the sum of each layer's closed form, each with its own base height. The sketch keeps the bounded form for each layer and checks the sum against 200,000 pieces for a level, a rising and a falling ray.

   ```cpp sketch="light-fog-layers.cpp"
   #include <algorithm>
   #include <cmath>
   #include <cstdio>

   struct Layer
   {
   	double Density;
   	double Falloff;
   	double BaseHeight;
   };

   // One layer's optical depth in closed form, the shader's way: the lowest point's density times a mean in (0, 1].
   double LayerDepth(const Layer& layer, double startHeight, double rise, double distance)
   {
   	const double lowest = startHeight - layer.BaseHeight + std::min(rise, 0.0);
   	const double y = layer.Falloff * std::abs(rise);
   	const double mean = y > 1.0e-4 ? (1.0 - std::exp(-y)) / y : 1.0 - 0.5 * y;
   	return layer.Density * distance * std::exp(-layer.Falloff * lowest) * mean;
   }

   // Extinctions add, so optical depths add: the layers are summed.
   double TotalDepth(const Layer* layers, int count, double startHeight, double rise, double distance)
   {
   	double depth = 0.0;
   	for (int index = 0; index < count; index++)
   		depth += LayerDepth(layers[index], startHeight, rise, distance);
   	return depth;
   }

   double NumericDepth(const Layer* layers, int count, double startHeight, double rise, double distance)
   {
   	const int steps = 200000;
   	double depth = 0.0;
   	for (int step = 0; step < steps; step++)
   	{
   		const double height = startHeight + rise * (step + 0.5) / steps;
   		for (int index = 0; index < count; index++)
   			depth += layers[index].Density * std::exp(-layers[index].Falloff * (height - layers[index].BaseHeight)) * distance / steps;
   	}
   	return depth;
   }

   int main()
   {
   	const Layer layers[] = { { 0.02, 0.2, 0.0 }, { 0.004, 0.02, 0.0 } };
   	const double rises[] = { 0.0, 30.0, -12.0 };
   	for (double rise : rises)
   	{
   		const double closed = TotalDepth(layers, 2, 2.0, rise, 60.0);
   		const double numeric = NumericDepth(layers, 2, 2.0, rise, 60.0);
   		std::printf("rise %5.1f m: closed %.5f, numeric %.5f, agree %s\n", rise, closed, numeric, std::abs(closed - numeric) < 1.0e-5 ? "yes" : "no");
   	}
   	return 0;
   }
   ```

   ```text output-of="light-fog-layers.cpp"
   rise   0.0 m: closed 1.03497, numeric 1.03497, agree yes
   rise  30.0 m: closed 0.30713, numeric 0.30713, agree yes
   rise -12.0 m: closed 3.61998, numeric 3.61998, agree yes
   ```

   1. **Lines 15–18:** one layer's bounded form, with the layer's own base height subtracted.
   2. **Lines 24–27:** the layers add.

   In the engine, a second layer needs fields in the component and its registration, checks in `SetHeightFog` and new frame constants. It needs a sum in `GetFogOpticalDepth` and an endless-depth rule for the sky in `ApplyHeightFogToSky`. A test against the numeric sum and an entry in the feature test complete it.
   :::

## Where it lives in Strata

- Component: `HeightFogComponent` in `Strata/src/Strata/Renderer/RendererComponents.h`, registered in `Strata/src/Strata/Renderer/RendererComponents.cpp` as `HeightFog`.
- Renderer: `SceneRenderer::FindHeightFog` and `SceneRenderer::SetHeightFog` in `Strata/src/Strata/Renderer/SceneRenderer.cpp`.
- Shaders: `Strata/shaders/Include/Fog.slang`, used by `Strata/shaders/Scene/Forward.frag.slang` and `Strata/shaders/Scene/Skybox.frag.slang`.
- Tests: the suite `GPU.SceneRenderer.Fog` in `StrataTests/src/Renderer/GPUSceneFogTests.cpp`.

## Further reading

- Wenzel, "Real-time atmospheric effects in games", SIGGRAPH 2006 course notes: the analytic height fog; intermediate.
- Wronski, "Volumetric fog: unified compute shader based solution to atmospheric scattering", SIGGRAPH 2014: the froxel method; advanced.
- Unreal Engine's documentation of Exponential Height Fog: a production use of the same integral; beginner.
