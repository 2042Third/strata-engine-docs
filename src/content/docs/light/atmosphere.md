---
id: light/atmosphere
title: "Earth's atmosphere and aerial perspective"
description: "How Strata computes the sky, the sun's color at the ground and the haze of distance from the physics of air, with tables computed in advance."
kind: internals
size: L
tracks: [E]
needs: [light/sky, gpu/compute]
time: 90
learn:
  - id: explain-tables
    text: explain what each of the atmosphere's tables stores, which axes it has and why it is computed apart
  - id: compute-transmittance
    text: compute the transmittance of a ray from its optical depth and the sun's light at the ground
  - id: sun-above-air
    text: explain why the sun's intensity is the illuminance above the air and what the storage scale protects
  - id: aerial-adds
    text: explain what aerial perspective adds to a distant surface and how the haze volume is read
  - id: trace-haze
    text: trace a change of the haze setting through the renderer to the tables computed again
since: 0.6.0
status: final
---

A clear sky is blue, a sunset is red, and a far mountain is pale and blue-gray. All three have one cause: sunlight crosses air, and the air scatters and absorbs some of it. Strata's **physical atmosphere** is a model of a planet's air that computes the sky's color, the sun's color at the ground and the haze of distance from that physics. The page omits the sky light's sources and presets ([the sky page](sky.md)), height fog, the environment cube's filter chain and the pre-exposure.

## The problem and how engines solve it

A sky color is the sum of light that millions of air molecules scatter toward your eye, each lit by a sun that the air above it already dimmed. Computing that for every pixel and every frame is far too slow. Engines choose between three families: a formula fitted to measured skies, a march through the air for each pixel, or tables computed once and read many times.

A fitted formula is cheap but tied to Earth's air and to a viewer on the ground. A march costs hundreds of samples a pixel. Strata takes the third way, published by Bruneton and Neyret in 2008 and made cheap by Hillaire in 2020. A **lookup table (LUT)** is a texture indexed by the question's inputs: an expensive integral runs once for a few thousand questions, and each pixel reads one answer. The [alternatives table](#alternatives-strata-did-not-choose) weighs the other two families.

## What air does to light

Start with one ray of light and one stretch of air. Light on its way through air can pass, be absorbed by a molecule, or be scattered by a molecule into another direction. **Extinction** is the share of light that leaves a ray per kilometer, by absorption or scattering; air has an extinction at each height, higher near the ground where the air is dense.

Think of a crowd that walks through thick fog. Each meter stops the same share of those who arrive at it, not the same number. After ten meters you have lost a share, and after twenty meters the same share again of what is left. Light does the same, and the share that stops per kilometer is the extinction.

Add up the extinction along a ray and you get the **optical depth**, a number without a unit that measures how much air the ray crosses.

The share of light that survives the path is the **transmittance**, a number from 0 (nothing arrives) to 1 (everything does).

The rule that links the two is the **Beer-Lambert law**: transmittance falls exponentially with optical depth.

$$T = e^{-\tau}$$

In this line, $T$ is the transmittance, $\tau$ is the optical depth, and $e$ is the number 2.718 that you met in [the numbers page](../basics/numbers.md).

$$\tau = \int_0^s \sigma(x)\,dx$$

Here $s$ is the length of the ray in kilometers, $x$ is the distance along it, $dx$ is a very small step, and $\sigma(x)$ is the extinction at that distance, per kilometer. The integral sign sums $\sigma$ over very small steps, as [the page on accumulating small steps](../basics/math-change.md) does. Read it as "add up $\sigma$ from the start of the ray to its end".

:::example[One ray through thin air]
Take a ray that crosses 10 km of air with an even extinction of 0.02 per km. The optical depth is $0.02 \times 10 = 0.2$, and the transmittance is $e^{-0.2} = 0.82$: 82 % of the light arrives. Double the length and the optical depth doubles to 0.4, but the transmittance does not halve its loss: it becomes $e^{-0.4} = 0.67$, which is 0.82 squared. Doubling the path squares the transmittance, because every kilometer stops its own share of what remains.
:::

At the limits the law is sensible. With no air, $\tau = 0$ and $T = 1$: nothing is lost. With a very long path, $\tau$ grows without bound and $T$ goes to 0: nothing arrives. The law is also why the sun is orange at sunset, as the toy version below shows.

## What the air is made of

Earth's air has three ingredients that matter for light, and Strata gives each its own height profile. The first is the gas itself.

**Rayleigh** scattering is the scattering by molecules much smaller than the wavelength of light; it is strong for short wavelengths, so blue scatters about six times more than red. Strata's coefficients per kilometer at sea level are 5.802e-3 for red, 13.558e-3 for green and 33.1e-3 for blue, and they fall off as $e^{-h/8}$ with the height $h$ in kilometers. The ratio of blue to red is 5.7, close to the $(700/450)^4 = 5.8$ that the wavelengths give.

The second ingredient is a thin haze of dust, water drops and smoke.

**Mie scattering** is the scattering by particles about as large as the wavelength; it is nearly the same for every color, so it makes the sky white near the sun. It sends light mostly forward. Strata's coefficient is 3.996e-3 per kilometer, with a small absorption of 0.444e-3 beside it. The haze thins out quickly, as $e^{-h/1.2}$, so it hugs the ground.

The third ingredient is a layer of ozone high above.

**Ozone absorption** is the removal of light by ozone without scattering it, mostly green and red. Strata models the layer as a tent: zero density at 10 km, a peak at 25 km and zero again at 40 km. At noon ozone does little, but at sunset the light crosses the layer on a long slant, and ozone keeps the sky overhead blue.

The extinction at a height is the scattering of the air, plus the extinction of the haze (its scattering plus its absorption), plus the ozone. Scattered light leaves the ray but does not vanish: it arrives from another direction. How much goes where is the next idea.

## Where scattered light goes

A **phase function** gives the share of scattered light that goes into each direction, as a function of the angle $\theta$ between the light's old direction and its new one. It is a density over the sphere, so its integral over all directions is 1. [The page on directions on a sphere](../basics/math-sphere.md) covers the solid angle.

For Rayleigh scattering the function gives the same value forward and backward, and less to the sides.

$$p_R(\theta) = \frac{3}{16\pi}\,(1 + \cos^2\theta)$$

Here $p_R$ is the phase function in 1/steradian, $\theta$ is the scattering angle and $\cos^2\theta$ is the :term[cosine]{id=cosine} squared. At $\theta = 0$ and $\theta = 180°$ the value is $3/(16\pi) \times 2 = 0.119$; at 90° it is half of that, 0.0597.

Haze scatters mainly forward, and no simple formula fits real particles. Strata uses the **Henyey-Greenstein** function, a one-parameter curve that tilts the scattering toward the forward direction by a bias $g$.

$$p_M(\theta) = \frac{1 - g^2}{4\pi\,(1 + g^2 - 2g\cos\theta)^{3/2}}$$

Here $p_M$ is the haze's phase function in 1/steradian, and $g$ is the bias, from -1 (all backward) through 0 (even) to 1 (all forward). Strata uses $g = 0.8$. Straight ahead ($\theta = 0$) the value is $0.36 / (4\pi \times 0.008) = 3.58$, and straight back it is $0.36 / (4\pi \times 5.83) = 0.0049$: the forward peak is 729 times the backward one. That peak is the glow around the sun.

## The map: what Strata stores and who reads it

Now put the ideas to work. The sun's light at a point of the sky has crossed air, so you need the transmittance from that point to the top of the air, for many points and directions. The sky's light also has bounces to count.

**Single scattering** is light that scatters exactly once between the sun and your eye.

**Multiple scattering** is light that scatters twice or more; it fills the shadow of the planet's edge and keeps the twilight sky from going black at once.

Strata keeps three tables: the transmittance table, the multiple-scattering table and the sky-view table. A small volume, a fourth table in three dimensions, serves the haze of distance.

**Aerial perspective** is that haze: the air between the camera and a surface dims the surface and adds the light that the air scatters toward the camera.

```mermaid caption="The tables flow from left to right. The transmittance table feeds the multiple-scattering table, and both feed the sky-view table and the haze volume. The background and the environment cube read the sky view, and every surface reads the haze volume." alt="A flow of boxes. A transmittance table of 256 by 64 texels, with height and direction as axes, leads to a multiple-scattering table of 32 by 32, with height and sun height as axes. Both lead to a sky-view table of 192 by 108 and to a volume of 32 by 32 by 32 in-scattering slices and 32 transmittance slices. The sky view leads to the background and the environment cube. The volume leads to the surfaces."
flowchart LR
    T["Transmittance table 256 x 64: height, direction"] --> M["Multiple scattering 32 x 32: height, sun height"]
    T --> S["Sky view 192 x 108: azimuth, elevation"]
    M --> S
    T --> A["Aerial volume 32 x 32 x 32, twice: screen column, depth"]
    M --> A
    S --> B["Sky background"]
    S --> E["Environment cube"]
    A --> F["Surfaces in the forward pass"]
```

Read the diagram from the left. The transmittance table (256 by 64 texels) holds, for a height and a direction, the transmittance to the top of the air. The multiple-scattering table (32 by 32) holds the light of the second and higher orders for a height and a sun height. The sky-view table (192 by 108) holds the sky as the viewer sees it, by :term[azimuth]{id=azimuth} and elevation. The volume holds the haze in 32 by 32 columns across the screen: 32 slices of scattered light and 32 of transmittance.

In these tables the height is the point's distance from the planet's center. It is 6,360 km at the ground and 6,460 km at the top of the air: the air is a shell 100 km thick. The ground is the world's plane $y = 0$.

Each table answers a question that changes at its own pace. The transmittance depends only on the air, so it changes when the settings change. The sky view also depends on the sun and the viewer's height band, so it changes when the sun moves. The haze volume depends on the camera, so it is made every frame. The tables store light per :term[lux]{id=lux} of sun, so a change of the sun's intensity touches none of them.

The tables also share a **storage scale**: the power of two 16,384. They multiply their light by it so that dim sky values stay out of the half float's coarse range, and every reader divides it out. The section [What went wrong before](#what-went-wrong-before) gives the reason. The sky view serves both the background and the environment cube that lights the scene ([the image-based lighting page](../indirect/ibl.md)).

## The contract

The callers of the atmosphere are the sky light, the lighting, the background and the surface :term[shaders]{id=shader}.

1. **The directional light's Intensity is the sun's illuminance above the air.** The real sun's is about 120,000 lux there. The :term[renderer]{id=renderer} dims it and makes it redder on its way to the ground; if you also lower the intensity to make a sunset, you dim it twice.
2. **Every reader of a table multiplies by `EnvironmentParams.x`.** The tables hold the sky per lux of sun, times the storage scale. That frame constant carries the sun's illuminance times the sky light's own Intensity and divides by the storage scale, so the reader's product is the sky in nits. A reader that skips it shows a sky that is 16,384 times too dark.
3. **The settings the renderer reads are finite and not negative.** A value that is not finite takes its default (1 for the density and the haze, 0.3 for the ground :term[albedo]{id=albedo}); a negative value counts as 0; the albedo is also capped at 1.
4. **Aerial perspective applies before the height fog.** The haze is the far air and the fog is the near air, so the fog goes over the haze. The haze works only with a perspective camera and a scale above 0.

:::rule[HDR targets are clamped]
Shaders that write :term[high dynamic range]{id=high-dynamic-range} (HDR) targets clamp with `SanitizeHDR`. One infinite or not-a-number value spreads through the bloom and the exposure and ruins the frame. The sky view and the haze volume clamp to 65,000, and the background calls `SanitizeHDR`.
:::

## A toy version: the optical depth of one ray

The toy does the first step of everything above. It computes the transmittance of one ray from the ground to the top of the air, for a sun at several elevations, with the air and the haze only. It uses the same constants, shell and midpoint quadrature as Strata's code, so its numbers are the engine table's, minus the ozone.

:::question
The program uses functions, loops, `std::exp` and `std::printf`: the basics are in [programming 1](../basics/programming-1.md), [programming 2](../basics/programming-2.md) and [programming 3](../basics/programming-3.md).
:::

The toy has three functions. `ExtinctionAt` returns the extinction of one color at a height, `DistanceToTop` finds where the ray leaves the shell, and `OpticalDepth` adds up the extinction in 40 steps. Search for the sample point of each step: it sits in the middle of its step, the midpoint rule. The program prints, for five sun elevations, the length of the path and the transmittance of red, green and blue.

```cpp sketch="light-atmosphere-toy.cpp"
// The optical depth and transmittance of one ray from the ground to the top of Earth's air.
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdio>
#include <initializer_list>

constexpr double c_BottomRadius = 6360.0; // Kilometers
constexpr double c_TopRadius = 6460.0;
constexpr double c_RayleighScaleHeight = 8.0;
constexpr double c_MieScaleHeight = 1.2;
constexpr int c_Steps = 40;
constexpr double c_Pi = 3.14159265358979323846;

// Per kilometer at sea level, for red, green and blue.
constexpr std::array<double, 3> c_Rayleigh = { 5.802e-3, 13.558e-3, 33.1e-3 };
constexpr double c_MieExtinction = 3.996e-3 + 0.444e-3;

double ExtinctionAt(int channel, double height)
{
	const double air = c_Rayleigh[channel] * std::exp(-height / c_RayleighScaleHeight);
	const double aerosols = c_MieExtinction * std::exp(-height / c_MieScaleHeight);
	return air + aerosols;
}

// The distance from a point at `radius` along a ray of cosine `mu` with the zenith to the top of the air.
double DistanceToTop(double radius, double mu)
{
	const double discriminant = (c_TopRadius - radius) * (c_TopRadius + radius) + radius * radius * mu * mu;
	return -radius * mu + std::sqrt(discriminant);
}

double OpticalDepth(int channel, double radius, double mu)
{
	const double distance = DistanceToTop(radius, mu);
	const double step = distance / c_Steps;
	double depth = 0.0;
	for (int index = 0; index < c_Steps; index++)
	{
		const double t = (index + 0.5) * step;
		const double pointRadius = std::sqrt(radius * radius + t * t + 2.0 * radius * mu * t);
		depth += ExtinctionAt(channel, pointRadius - c_BottomRadius) * step;
	}
	return depth;
}

int main()
{
	std::printf("elevation  path km   red     green   blue\n");
	for (double elevation : { 90.0, 60.0, 20.0, 6.0, 1.0 })
	{
		const double mu = std::sin(elevation * c_Pi / 180.0);
		std::printf("%5.0f deg  %7.1f", elevation, DistanceToTop(c_BottomRadius, mu));
		for (int channel = 0; channel < 3; channel++)
			std::printf("  %.4f", std::exp(-OpticalDepth(channel, c_BottomRadius, mu)));
		std::printf("\n");
	}
	return 0;
}
```

```text output-of="light-atmosphere-toy.cpp"
elevation  path km   red     green   blue
   90 deg    100.0  0.9506  0.8936  0.7648
   60 deg    115.2  0.9432  0.8782  0.7338
   20 deg    277.0  0.8631  0.7216  0.4595
    6 deg    648.2  0.6374  0.3713  0.0951
    1 deg   1026.7  0.2532  0.0542  0.0011
```

1. **Line 17:** the haze's extinction is its scattering plus its absorption.
2. **Lines 21–23:** the extinction is the air's profile plus the haze's, each falling exponentially with height.
3. **Lines 29–30:** the distance to the top of the shell, from the circle's equation.
4. **Lines 40–42:** a sample in the middle of each step, its height from the planet's center, and its extinction times the step.

Read the table from the top. With the sun straight up, the path is the 100 km of the shell, and blue keeps 76 % of its light. At 20° the path is 277 km and blue keeps 46 %, while red keeps 86 %. At 1° the path is over 1,000 km: red keeps a quarter, green keeps 5 % and blue keeps a thousandth. The sun's light has turned from white to deep red by the law $T = e^{-\tau}$ and a longer path.

:::example[The sun's light at the ground, by hand]
Check the blue value of the vertical ray by hand. At the ground the Rayleigh extinction is 33.1e-3 per km, and it falls as $e^{-h/8}$, so a vertical ray sees an optical depth of $33.1\text{e-}3 \times 8 \times (1 - e^{-12.5}) = 0.265$. The haze adds $4.44\text{e-}3 \times 1.2 = 0.0053$. The sum is 0.270, and $e^{-0.270} = 0.763$, which matches the toy's 0.7648 up to the curve of the planet.

For the real sun, weight the colors by the eye's :term[luminance]{id=luminance} weights. At 6° the weights give $0.2126 \times 0.6374 + 0.7152 \times 0.3713 + 0.0722 \times 0.0951 = 0.41$, so 120,000 lux above the air becomes about 49,000 lux at the ground, before the ozone takes some green. The sky adds light of its own, and the ratio of the two is the :term[sun-to-sky ratio]{id=sun-to-sky-ratio} that [the sky page](sky.md) names.
:::

:::figure{id=time-of-day-sweep variant=sun-60}
This picture: the sun at 60°, about 103,100 lux at the ground.
:::

:::figure{id=time-of-day-sweep variant=sun-20}
This picture: the sun at 20°, about 82,500 lux at the ground.
:::

:::figure{id=time-of-day-sweep variant=sun-6}
This picture: the sun at 6°, about 41,900 lux at the ground.
:::

:::figure{id=time-of-day-sweep variant=sun-0}
This picture: the sun at 0°, about 1,770 lux at the ground.
:::

:::figure{id=time-of-day-sweep variant=sun-minus-6}
This picture: the sun at −6°, below the horizon, and no sunlight at the ground.
:::

## The code, in the order the data flows

Four steps take the settings to pixels: the medium (what the air is made of, for the settings), the tables, the sun's light, and the readers.

### The extinction profiles

Strata's :term[central processing unit]{id=processor} (CPU) code holds the profile in one function and the shell's geometry in another. Look at how the three terms of the extinction match the three ingredients.

```cpp src="Strata/src/Strata/Renderer/Atmosphere.cpp#L18-L33"
glm::dvec3 Extinction(const Medium& medium, double height)
{
	height = std::max(height, 0.0);
	const double rayleigh = std::exp(-height / c_RayleighScaleHeight);
	const double mie = std::exp(-height / c_MieScaleHeight);
	const double ozone = std::max(1.0 - std::abs(height - c_OzoneCenterHeight) / c_OzoneHalfWidth, 0.0);
	return medium.RayleighScattering * rayleigh + medium.MieExtinction * mie + medium.OzoneAbsorption * ozone;
}

// Along a ray from `radius` with cosine `mu`, the distance to the top of the atmosphere; the products are formed so
// that nothing cancels near the horizon.
double DistanceToTop(double radius, double mu)
{
	const double discriminant = (c_TopRadius - radius) * (c_TopRadius + radius) + radius * radius * mu * mu;
	return std::max(-radius * mu + std::sqrt(std::max(discriminant, 0.0)), 0.0);
}
```

1. **Line 20:** heights below the ground count as the ground's.
2. **Lines 21–23:** the three profiles: the air and the haze fall exponentially, the ozone is a tent.
3. **Line 24:** each ingredient's coefficient times its profile, added.
4. **Lines 31–32:** the distance to the top, with the products ordered so that nothing cancels near the horizon.

The profile differs from the toy's by the ozone tent. The distance differs in its arithmetic: Strata orders the products so that nothing cancels near the horizon.

The medium comes from `GetMedium`, which takes the sky light's two settings. `AtmosphereDensity` scales the air, the ozone and the haze. `AtmosphereHaze` scales the haze once more, so the haze's scattering follows the product of the two. A density of 0.5 with a haze of 1 gives half of Earth's air and half of its haze. A haze of 4 with a density of 1 gives four times the haze and the same air.

`GroundAlbedo`, 0.3 by default, is the light the ground sends back into the sky.

The CPU evaluates the quadrature in `double`. It also computes the sun's light at the ground once per change, so the light, its shadows and the sky agree without a read back from the :term[graphics processing unit]{id=gpu} (GPU).

### The transmittance table

The GPU fills the transmittance table first. Each texel center stands for a height and a direction, and the mapping crowds samples where the answer changes fastest: directions toward the horizon, heights toward the ground. With $t = 2u - 1$ for the table's horizontal coordinate $u$, the cosine of the angle to straight up is $\mu = t\,|t|$, and the radius is the ground's plus the vertical coordinate squared times 100 km. A test compares the GPU's 16,384 texels with the CPU's evaluation and accepts a difference of 1 %.

### The multiple-scattering table

Here is the idea that makes Hillaire's model cheap. After the first bounce, take the light to arrive equally from every direction, so that the phase functions drop out. Gather the light scattered once toward a point over a sphere of directions, with the ground's reflection of the sun included: that is the second order, $S$. Gather a light that is 1 everywhere in the same way and you get the share $f$ that scattering returns to the point. Each further order is $f$ times the one before, so all orders sum as a geometric series, which [the page on the geometric series](../basics/math-interpolation.md) teaches.

$$S + fS + f^2S + \dots = \frac{S}{1 - f}$$

Here $S$ is the second-order light, per lux of sun, and $f$ is the share that scattering returns, a number from 0 to 1. The dots mean that the sum continues without end. With $S = 0.20$ and $f = 0.25$ the total is $0.20 / 0.75 = 0.267$, a third more than the second order alone. At the limits, $f = 0$ means no extra bounces and the sum is $S$; as $f$ nears 1 the sum grows without bound, which is why the code never divides by less than 0.001.

The compute shader runs one thread per texel of a 32 by 32 table. Search for the two loops over the 64 directions, the inner loop over 20 steps and the single division at the end.

```slang src="Strata/shaders/IBL/AtmosphereMultipleScattering.comp.slang#L29-L80"
float3 secondOrder = float3(0.0);
float3 transfer = float3(0.0);
const float isotropic = 1.0 / (4.0 * PI);
const float directionWeight = 1.0 / float(c_DirectionRings * c_DirectionSectors); // Each direction's share of the sphere
for (uint ring = 0u; ring < c_DirectionRings; ring++)
{
	float mu = 1.0 - 2.0 * (float(ring) + 0.5) / float(c_DirectionRings);
	float horizontal = sqrt(max(1.0 - mu * mu, 0.0));
	for (uint sector = 0u; sector < c_DirectionSectors; sector++)
	{
		float azimuth = TWO_PI * (float(sector) + 0.5) / float(c_DirectionSectors);
		float3 direction = float3(horizontal * cos(azimuth), mu, horizontal * sin(azimuth));
		bool ground = RayMeetsGround(radius, mu);
		float length = ground ? DistanceToGround(radius, mu) : DistanceToAtmosphereTop(radius, mu);
		float step = length / float(c_Steps);
		float3 transmittance = float3(1.0);
		float3 single = float3(0.0);
		float3 gathered = float3(0.0);
		for (uint index = 0u; index < c_Steps; index++)
		{
			float t = (float(index) + 0.5) * step;
			float pointRadius = RadiusAlongRay(radius, mu, t);
			float height = pointRadius - c_AtmosphereBottomRadius;
			float3 scattering = medium.RayleighScattering * exp(-max(height, 0.0) / c_RayleighScaleHeight)
				+ medium.MieScattering * exp(-max(height, 0.0) / c_MieScaleHeight);
			float3 extinction = GetAtmosphereExtinction(medium, height);
			// The point's position and its sun's cosine to its own zenith.
			float3 position = float3(0.0, radius, 0.0) + direction * t;
			float sunMu = dot(position, toSun) / pointRadius;
			// Integrated over the step: what scatters in it, dimmed by what lies before it on the step.
			float3 stepTransmittance = exp(-extinction * step);
			float3 inStep = max(extinction, float3(1.0e-9));
			float3 weight = transmittance * (1.0 - stepTransmittance) / inStep;
			single += weight * scattering * GetSunTransmittance(pointRadius, sunMu) * isotropic;
			gathered += weight * scattering;
			transmittance *= stepTransmittance;
		}
		if (ground)
		{
			// The ground reflects the sun diffusely toward the point.
			float3 groundPosition = float3(0.0, radius, 0.0) + direction * length;
			float3 normal = normalize(groundPosition);
			float sunMu = dot(normal, toSun);
			single += transmittance * GetSunTransmittance(c_AtmosphereBottomRadius, sunMu) * max(sunMu, 0.0) * albedo / PI;
		}
		secondOrder += single * directionWeight;
		transfer += gathered * directionWeight;
	}
}
float3 multiple = secondOrder / max(1.0 - transfer, float3(1.0e-3));
// Stored scaled (ST_ATMOSPHERE_STORAGE_SCALE; GetMultipleScattering divides).
o_Table[texel] = float4(multiple * ST_ATMOSPHERE_STORAGE_SCALE, 1.0);
```

1. **Line 32:** each of the 64 directions carries an equal share of the sphere, so the sum over directions is an average.
2. **Lines 59–62:** the integral over one step: what scatters in it, dimmed by what lies before it, with the sun's transmittance and an even phase.
3. **Line 63:** the same gathering without the sun is the share $f$, which depends on the air alone.
4. **Lines 66–73:** where the ray ends on the ground, the ground adds its diffuse reflection of the sun, the albedo over $\pi$.
5. **Lines 78–80:** the sum $S/(1-f)$ with a floor under the number it divides by, stored times the storage scale.

The shader differs from the toy by gathering over a sphere and reading the sun's transmittance from the table instead of computing it again. Eight rings of eight sectors are a coarse sphere, but this light changes slowly with direction, so the sky shows no error.

### One segment of the sky

The sky-view table and the haze volume integrate the same thing. **In-scattering** is sunlight that the air scatters into a view ray toward the eye; it adds to what the ray carries. One function adds a segment of the ray to a running sum, and both passes call it.

```slang src="Strata/shaders/Include/AtmospherePass.slang#L73-L89"
void AccumulateAtmosphereSegment(AtmosphereMedium medium, float viewerRadius, float mu, float3 direction, float3 toSun, float rayleighPhase,
	float miePhase, float t, float stepLength, inout float3 transmittance, inout float3 light)
{
	float pointRadius = max(RadiusAlongRay(viewerRadius, mu, t), c_AtmosphereBottomRadius);
	float height = pointRadius - c_AtmosphereBottomRadius;
	float3 rayleigh = medium.RayleighScattering * exp(-max(height, 0.0) / c_RayleighScaleHeight);
	float3 mie = medium.MieScattering * exp(-max(height, 0.0) / c_MieScaleHeight);
	float3 extinction = GetAtmosphereExtinction(medium, height);
	float3 position = float3(0.0, viewerRadius, 0.0) + direction * t;
	float sunMu = clamp(dot(position, toSun) / pointRadius, -1.0, 1.0);
	float3 sun = GetSunTransmittance(pointRadius, sunMu);
	float3 multiple = GetMultipleScattering(pointRadius, sunMu);
	float3 scattered = rayleigh * (rayleighPhase * sun + multiple) + mie * (miePhase * sun + multiple);
	float3 stepTransmittance = exp(-extinction * stepLength);
	light += transmittance * (1.0 - stepTransmittance) / max(extinction, float3(1.0e-9)) * scattered;
	transmittance *= stepTransmittance;
}
```

1. **Line 76:** a point below the ground counts as the ground's, so the rays that end on the ground read sane heights.
2. **Lines 83–85:** the sun's light from the transmittance table, the higher orders from the multiple-scattering table. The air and the haze scatter the sun with their own phases and the higher orders evenly.
3. **Lines 86–87:** the segment's own integral: what scatters in the step, dimmed by the light before the step, over the extinction.
4. **Line 88:** the segment dims the rest of the ray by its own extinction.

The sky-view shader calls this function 40 times along each ray, with steps that grow as the square of their index.

```slang src="Strata/shaders/IBL/AtmosphereSkyView.comp.slang#L35-L42"
for (uint index = 0u; index < c_Steps; index++)
{
	float next = length * float((index + 1u) * (index + 1u)) / float(c_Steps * c_Steps);
	float step = next - previous;
	float t = 0.5 * (previous + next);
	previous = next;
	AccumulateAtmosphereSegment(medium, radius, mu, direction, toSun, rayleighPhase, miePhase, t, step, transmittance, light);
}
```

For a ray of 100 km the first step is $100/1600 = 62$ m and the last is 4.9 km. Small steps near the viewer, where the air is dense, and large ones far away, where it is thin, spend the 40 samples where the answer changes. The table's rows crowd toward the horizon in the same way, because the sky changes fastest there. The viewer's height is the middle of a 250 m band, so the sky view is computed again when the camera climbs into the next band, up to a height of 20 km.

### The sun's light at the ground

The sun's color needs no table. The transmittance to the top of the air along the sun's direction is the sun's light at the ground, and the CPU computes it, in `double`, and multiplies the directional light by it.

```cpp src="Strata/src/Strata/Renderer/SceneRendererAtmosphere.cpp#L337-L358"
// The sun's light at the ground: dimmed and reddened by the air it crossed (the same transmittance as the tables',
// evaluated on the CPU once per change), so the lighting, its shadows and the sky agree without a readback.
const float sunSize = std::isfinite(sky.SunSize) ? std::clamp(sky.SunSize, 0.0f, 180.0f) : 0.0f;
const float radius = glm::radians(sunSize) * 0.5f;
if (atmosphere.SunSettings != settings || atmosphere.SunDirection != towardSun || atmosphere.SunRadius != radius)
{
	const Atmosphere::Medium medium = Atmosphere::GetMedium(settings.Density, settings.Haze);
	atmosphere.SunTransmittance = glm::vec3(Atmosphere::ComputeSunTransmittance(medium, glm::dvec3(towardSun), static_cast<double>(radius)));
	atmosphere.SunSettings = settings;
	atmosphere.SunDirection = towardSun;
	atmosphere.SunRadius = radius;
}
const glm::vec3 transmittance = atmosphere.SunTransmittance;
if (hasSun)
{
	frame.DirectionalLightColor = glm::vec4(glm::vec3(frame.DirectionalLightColor) * transmittance, frame.DirectionalLightColor.w);
	m_SunColor *= transmittance;
}
frame.SunDiskDirection = glm::vec4(towardSun, radius);
frame.SunDiskColor = glm::vec4(light * transmittance, 0.0f);
m_Stats.Atmosphere = true;
m_Stats.SunTransmittance = transmittance;
```

1. **Line 341:** the work is done again only when the settings, the sun's direction or the disk's size changed.
2. **Lines 343–344:** the medium from the finite settings, then the sun's transmittance with the disk's share: its center's transmittance times the share of the disk above the horizon.
3. **Lines 350–354:** the directional light's color times the transmittance. The intensity above the air is dimmed here, once, and nowhere else.
4. **Lines 355–356:** the disk's direction and radius, and its color: the illuminance times the transmittance.
5. **Line 358:** the value that tests and tools read as `SceneRendererStats::SunTransmittance`.

The disk's share matters at sunset. The sun's disk is 0.53° wide by default, so its radius is 0.265°. At an elevation of 0° half the disk is above the horizon and the share is 0.5; at 0.1° it is $(0.1 + 0.265)/0.53 = 0.69$; at -0.265° it is 0. The light fades out over the disk's width, not in one frame.

The rule says the intensity is the sun above the air for this reason. The directional light's color is multiplied by the transmittance once, here, and a second dimming by hand would make every sunset too dark. The tables store the sky per lux of the sun's color over its largest component, and the readers multiply by the illuminance.

### The storage scale

Sky values per lux of sun get small after sunset. A half float has a smallest normal number, $2^{-14} = 6.1 \times 10^{-5}$; below it the numbers are :term[subnormal]{id=subnormal-number}, with :term[fixed steps]{id=fixed-step} of $2^{-24} = 6 \times 10^{-8}$. A sky value of $10^{-6}$ per lux then has about 17 levels, and a smooth gradient turns into bands. Multiplying by $2^{14} = 16{,}384$ lifts it to 0.016, which is normal and keeps 1,024 levels per power of two.

A power of two changes only the :term[exponent]{id=exponent}, so values that were normal stay exact. The reader's division by the scale lives in `EnvironmentParams.x`, which is why every reader must multiply by it.

### The environment refresh

The environment cube lights the scene, and the renderer computes it from the sky view in 14 steps. There are six cube faces, two steps for the cube's levels and the :term[irradiance]{id=irradiance}, and six for the prefiltered levels. When the sun moves, the renderer keeps two sets of maps and fills the spare one, one step per frame, while the other lights the scene. A renderer made with `SpreadLightingUpdates` off does all 14 steps in one frame.

```mermaid caption="The environment's refresh cycle. The first environment, and one after the sun is enabled or disabled, is computed at once. Later, a sun that moved half a degree or changed settings starts a refresh that runs one step per frame and then swaps the maps." alt="A state diagram with two states, idle and refreshing. From idle, an arrow labeled the sun moved half a degree, or the settings changed, leads to refreshing. A loop on refreshing is labeled one step per frame, of 14. An arrow from refreshing back to idle is labeled all 14 steps done, swap the maps."
stateDiagram-v2
    [*] --> Idle: first environment, computed at once
    Idle --> Refreshing: sun moved 0.5 degrees or settings changed
    Refreshing --> Refreshing: one step per frame
    Refreshing --> Idle: step 14 done, swap the maps
```

A refresh runs to its end with the settings it started with, even if they change meanwhile, so settings that change every frame still reach the screen. A sun that is enabled or disabled changes the whole sky, so that case computes all 14 steps in one frame, like the first environment.

### The background and the sun's disk

The background shader draws the sky where no surface was drawn. It reads the sky-view table by view direction, multiplies by `EnvironmentParams.x`, and adds the sun's disk.

```slang src="Strata/shaders/Scene/Skybox.frag.slang#L24-L33"
float3 color = u_SkyViewTable.SampleLevel(u_Samplers[0], DirectionToSkyViewUV(direction), 0.0).rgb * u_Frame.EnvironmentParams.x;
float radius = u_Frame.SunDiskDirection.w;
if (radius > 0.0)
{
	float chord = length(direction - u_Frame.SunDiskDirection.xyz);
	float angle = 2.0 * asin(min(chord * 0.5, 1.0));
	float pixelAngle = max(length(fwidth(direction)), 1.0e-6);
	float coverage = clamp((radius - angle) / pixelAngle + 0.5, 0.0, 1.0);
	float solidAngle = TWO_PI * (1.0 - cos(radius));
	color += u_Frame.SunDiskColor.rgb * (coverage / max(solidAngle, 1.0e-12));
```

1. **Line 24:** the sky from the table by direction, times the frame constant that carries the illuminance and divides out the storage scale.
2. **Lines 28–31:** the disk's edge smoothed over one pixel: the angle to the sun's center against its radius.
3. **Lines 32–33:** the disk carries the sun's illuminance over its solid angle, which turns lux into nits.

The disk's radius is 0.265°, so its solid angle is $2\pi(1 - \cos 0.265°) = 6.7 \times 10^{-5}$ :term[steradians]{id=steradian}. An illuminance of 100,000 lux over that is 1.5 billion nits, far above the half float's top; [the pre-exposure page](../image/pre-exposure.md) scales the frame so that the disk fits.

### Aerial perspective

The haze of distance is a volume of 32 by 32 columns across the screen with 32 depth slices, made every frame. For each column the compute shader marches the view ray through the centers of the slices, 2 segments per slice, with the same segment function as the sky view. Slice $k$ holds the in-scattered light up to its depth, and slice $k + 32$ the transmittance. The volume is 32 by 32 by 64 texels of four half floats: 524,288 :term[bytes]{id=byte}.

The depths are not even. Slice $k$ ends at

$$d_k = D\left(\frac{k + 0.5}{32}\right)^2$$

Here $d_k$ is the slice's distance in meters, $D$ is the volume's far distance (the camera's :term[far plane]{id=far-plane}, at most 32,000 m) and $k$ runs from 0 to 31. With $D = 1000$ m, slice 0 is at 0.24 m, slice 15 at 235 m and slice 31 at 969 m. The squares crowd the slices near the camera, where the haze changes fastest, and the last slice holds everything beyond $D$.

The reader inverts the formula. A surface at distance $d$ finds its place at slice $\sqrt{d/D} \times 32 - 0.5$, then fetches twice with trilinear filtering: once for the scattered light and once for the transmittance.

```slang src="Strata/shaders/Include/AerialPerspective.slang#L17-L26"
float3 ApplyAerialPerspective(float3 color, float3 relativePosition, float2 fragCoord)
{
	float2 uv = fragCoord * u_Frame.ViewportSize.zw;
	// Slice k's center lies at D ((k + 0.5) / 32)^2: invert it, clamped to the volume (the first slice holds the camera's near
	// air, the last everything beyond D).
	float slice = clamp(sqrt(length(relativePosition) / u_Frame.FogParams.z) * c_AerialSlices - 0.5, 0.0, c_AerialSlices - 1.0);
	float3 scattering = u_AerialPerspective.SampleLevel(u_LinearClampSampler, float3(uv, (slice + 0.5) / (2.0 * c_AerialSlices)), 0.0).rgb;
	float3 transmittance = u_AerialPerspective.SampleLevel(u_LinearClampSampler, float3(uv, (slice + c_AerialSlices + 0.5) / (2.0 * c_AerialSlices)), 0.0).rgb;
	return color * transmittance + scattering * u_Frame.EnvironmentParams.x;
}
```

1. **Line 22:** the slice number from the distance, clamped to the volume: the first slice is the camera's near air and the last everything beyond $D$.
2. **Lines 23–24:** two fetches at the same screen column, one at the slice and one 32 slices on, where the transmittance lies; the filter blends the two nearest slices.
3. **Line 25:** the surface's color times the transmittance plus the scattered light times `EnvironmentParams.x`: the dimming and the haze in one line.

:::example[A mountain seen through the volume]
Take a camera with a far plane of 5,000 m and a mountain 2,000 m away. The slice is $\sqrt{2000/5000} \times 32 - 0.5 = 19.7$, so the fetch blends slices 19 and 20. At scale 1 the air and the haze give blue an optical depth near $(33.1 + 4.4)\text{e-}3 \times 2 = 0.075$ over 2 km, so 93 % of it arrives: a small world shows no haze.

`AerialPerspectiveScale` multiplies the distances before they enter the air. At scale 6 the same 2 km count as 12 km. The blue depth is near 0.45 and 64 % arrives, so over a third of the mountain's blue is gone and the air's blue replaces it. The scale goes up to 64.
:::

::figure{id=aerial-perspective-scales variant=off}

::figure{id=aerial-perspective-scales variant=scale-1}

::figure{id=aerial-perspective-scales variant=scale-6}

The volume applies in the forward pass before the height fog, for opaque and transparent surfaces alike, so a sheet of glass looks like an opaque surface at its depth. The scaled air is not physical, but it gives a small world the look of a large one.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| A fitted sky formula (Preetham 1999, Hosek and Wilkie 2012) | Many engines, as a first sky | No tables and no computing, one function | The viewer is tied to the ground, no aerial perspective from the same air, no multiple scattering |
| Bruneton and Neyret's tables in four dimensions (2008) | Their reference implementation, and engines that took it | Multiple scattering with the ground and the viewer at any height | Large tables, a slow update when the sun moves, and one table per setting |
| A march through the air for each pixel every frame | Renderers of films | Exact light, and any shape of air | Hundreds of samples a pixel, too slow for a game's frame |
| A painted or photographed sky | Games with a fixed time of day | The best look, no cost | No time of day, no sunset, no haze by distance |

Hillaire's 2020 method, which Strata follows, keeps the tables small and cheap to refresh. It loses the viewer at any height: the sky view is computed for the viewer's height band, and the model is meant for a viewer on a planet's surface.

## How it is tested

The suite `GPU.Atmosphere` lives in `StrataTests/src/Renderer/GPUAtmosphereTests.cpp` and `StrataTests/src/Renderer/GPUAerialPerspectiveTests.cpp`. It needs a GPU; run it with the test program's filter for that suite.

- The GPU's transmittance table is compared with the CPU's evaluation, texel by texel: a difference above 1 % (or 0.0001 where half floats lose precision) fails the test.
- At sunset the directional light is its color times the CPU's transmittance, and the reported `SunTransmittance` agrees with the CPU function; the test also checks that red keeps more than twice the blue.
- A sun that moves less than half a degree does not refresh the environment; a refresh finishes while the settings keep changing; a change of the light's intensity alone computes no table again.
- The night sky at -10° has no bands, and no table of a daytime sky reaches the storage clamp.
- Aerial perspective is clear at the camera and follows the CPU's transmittance at the last slice within 1 %. It matches the sky at the end of a horizontal ray, costs nothing when off, is absent from orthographic views and hazes transparent surfaces like opaque ones.

## Changing it safely

The extension points are the sky light's settings, the constants in `Strata/src/Strata/Renderer/Atmosphere.h` and the shaders in `Strata/shaders/IBL/`.

- **Keep the CPU and the shader constants equal.** `Strata/shaders/Include/Atmosphere.slang` mirrors `Atmosphere.h`. The CPU computes the sun's light with the same quadrature as the GPU's table, and the test compares them; a changed constant on one side makes the sun and the sky disagree.
- **A new table input must join the settings.** The tables are computed again when the settings differ; an input outside them never triggers it.
- **Keep the tables per lux of sun.** An intensity that entered a table would make every change of the sun's intensity compute it again.
- **Pass the checks.** Run `GPU.Atmosphere`, the feature test, and the `GPU*` suites, which end with a zero count of new GPU errors.

## What went wrong before

After sunset the sky looked banded. The tables held the sky per lux of sun in half floats, and at -10° nearly all of the sky view's values were below the smallest normal number. The subnormal steps are fixed, so a smooth twilight gradient became bands of 8 to 17 levels. The fix is the storage scale, and the regression test is `The night sky at -10 degrees has no bands` in the suite `GPU.Atmosphere`.

## Summary

- The atmosphere is computed from Earth's air: Rayleigh scattering of the gas, Mie scattering of the haze and the absorption of ozone, in a shell from 6,360 to 6,460 km. Tables hold the answers: transmittance, multiple scattering and the sky view, plus a haze volume.
- The transmittance of a ray is $e^{-\tau}$ for its optical depth $\tau$; doubling the path squares it. Red keeps a quarter of the sun's light at 1° and blue a thousandth, which makes the sunset.
- The directional light's intensity is the sun's illuminance above the air; the renderer dims it once. The tables hold light times 16,384 so that the twilight stays out of the subnormal range, and the readers divide it out through `EnvironmentParams.x`.
- Aerial perspective adds the air's scattered light and dims a surface by the transmittance, from a 32 by 32 by 32 volume read at slice $\sqrt{d/D} \times 32 - 0.5$, before the height fog. Its scale gives small worlds the haze of large ones.
- A change of `AtmosphereHaze` makes the settings differ, so the transmittance and multiple-scattering tables, the sky view, the sun's transmittance and a new environment are computed again.

## Check yourself

1. A friend lowers a directional light's Intensity from 120,000 to 40,000 lux "so the sunset looks warmer". What happens under the Atmosphere source?

   - A. The sunset is warmer, because the air colors a weaker sun more.
   - B. The sunset is darker and not warmer: the air already makes the light redder, and the lower intensity dims it twice.
   - C. Nothing, because the tables ignore the intensity.

   :::answer{tests="sun-above-air"}
   B. The intensity is the illuminance above the air, and the renderer multiplies it by the transmittance once. Lowering it dims the same light again without changing its color. Option A confuses dimming with coloring: the color comes from the transmittance. Option C is half true, since the tables ignore the intensity, but the light's color on surfaces does not.
   :::

2. A ray crosses a stretch of air with an optical depth of 0.7 for blue. What does the stretch of twice the length leave?

   :::answer{tests="compute-transmittance"}
   One stretch leaves $e^{-0.7} = 0.50$. Twice the length doubles the optical depth to 1.4 and leaves $e^{-1.4} = 0.25$, the square of 0.50: each half stops its share of what is left.
   :::

3. Which of these is a table indexed by azimuth and elevation, and which is read at a slice computed from the distance of a surface?

   - A. The sky-view table, and the aerial perspective volume.
   - B. The transmittance table, and the sky-view table.
   - C. The multiple-scattering table, and the transmittance table.

   :::answer{tests="explain-tables,aerial-adds"}
   A. The sky view holds the sky by azimuth and elevation, and the volume's slices are read at $\sqrt{d/D} \times 32 - 0.5$. Option B names the transmittance table, whose axes are the height and the direction's cosine. Option C names two tables whose axes are heights and cosines, and neither is read by distance.
   :::

4. A reader of the sky-view table forgets to multiply by `EnvironmentParams.x`. What does the reader show?

   :::answer{tests="sun-above-air"}
   A sky that is 16,384 times too dark, and without the sun's illuminance in it. The table holds the sky per lux of sun times the storage scale, and the frame constant carries the illuminance and divides out the scale. Every reader of a table needs it.
   :::

5. You change `AtmosphereHaze` from 1 to 2 in a running scene. Which of these are computed again: the transmittance table, the sky view, the haze volume, the sun's transmittance?

   :::answer{tests="trace-haze"}
   The transmittance and multiple-scattering tables (the settings differ), the sky view (it comes after the tables) and the sun's transmittance (from `GetMedium` with the new haze) are computed again, and an environment refresh starts. The haze volume is made every frame anyway, so it reads the new tables at once.
   :::

## Exercises

1. **Basic.** A camera has a far plane of 2,000 m. At which slice does the volume's reader place a surface 500 m away, and between which slices does the filter blend?

   :::answer[Worked solution]{tests="aerial-adds"}
   The slice is $\sqrt{500/2000} \times 32 - 0.5 = 0.5 \times 32 - 0.5 = 15.5$. The reader fetches at the coordinate $(15.5 + 0.5)/64$, which lies half way between the centers of slices 15 and 16, so the trilinear filter blends those two equally. The transmittance is fetched 32 slices on, in the same way.
   :::

2. **Medium.** Compute the sun's transmittance at the ground for the sun at 4° and at 0°, with the ozone and the disk's share, as the CPU does for the lighting. The tests compare the engine's `SceneRendererStats::SunTransmittance` with the CPU function that this program copies.

   :::answer[Worked solution]{tests="compute-transmittance"}
   The program extends the toy: it adds the ozone tent to the extinction, takes the transmittance of the ground-to-top ray at the sun's elevation, and multiplies by the share of the disk above the horizon.

   ```cpp sketch="light-atmosphere-sunset.cpp"
   // The sun's transmittance at the ground as Strata computes it on the CPU: air, aerosols and ozone, and the disk's share.
   #include <algorithm>
   #include <array>
   #include <cmath>
   #include <cstdio>

   constexpr double c_BottomRadius = 6360.0; // Kilometers
   constexpr double c_TopRadius = 6460.0;
   constexpr int c_Steps = 40;
   constexpr double c_Pi = 3.14159265358979323846;

   constexpr std::array<double, 3> c_Rayleigh = { 5.802e-3, 13.558e-3, 33.1e-3 };
   constexpr std::array<double, 3> c_Ozone = { 0.650e-3, 1.881e-3, 0.085e-3 };
   constexpr double c_MieExtinction = 3.996e-3 + 0.444e-3;

   double ExtinctionAt(int channel, double height)
   {
   	const double air = c_Rayleigh[channel] * std::exp(-height / 8.0);
   	const double aerosols = c_MieExtinction * std::exp(-height / 1.2);
   	const double ozone = c_Ozone[channel] * std::max(1.0 - std::abs(height - 25.0) / 15.0, 0.0);
   	return air + aerosols + ozone;
   }

   double Transmittance(int channel, double mu)
   {
   	const double radius = c_BottomRadius;
   	const double discriminant = (c_TopRadius - radius) * (c_TopRadius + radius) + radius * radius * mu * mu;
   	const double step = (-radius * mu + std::sqrt(discriminant)) / c_Steps;
   	double depth = 0.0;
   	for (int index = 0; index < c_Steps; index++)
   	{
   		const double t = (index + 0.5) * step;
   		const double pointRadius = std::sqrt(radius * radius + t * t + 2.0 * radius * mu * t);
   		depth += ExtinctionAt(channel, pointRadius - c_BottomRadius) * step;
   	}
   	return std::exp(-depth);
   }

   int main()
   {
   	const double diskRadius = 0.53 * 0.5 * c_Pi / 180.0; // The default sun size, in radians
   	for (double elevationDegrees : { 4.0, 0.0 })
   	{
   		const double elevation = elevationDegrees * c_Pi / 180.0;
   		const double visible = std::clamp((elevation + diskRadius) / (2.0 * diskRadius), 0.0, 1.0);
   		std::printf("sun at %.0f deg, %.2f of the disk above the horizon:", elevationDegrees, visible);
   		for (int channel = 0; channel < 3; channel++)
   			std::printf("  %.4f", Transmittance(channel, std::sin(elevation)) * visible);
   		std::printf("\n");
   	}
   	return 0;
   }
   ```

   ```text output-of="light-atmosphere-sunset.cpp"
   sun at 4 deg, 1.00 of the disk above the horizon:  0.4891  0.1966  0.0382
   sun at 0 deg, 0.50 of the disk above the horizon:  0.0532  0.0048  0.0000
   ```

   1. **Line 20:** the ozone tent, which the toy omitted.
   2. **Line 41:** the disk's radius in :term[radians]{id=radian}, from the default size of 0.53°.
   3. **Line 45:** the share of the disk above the horizon.
   4. **Line 48:** the transmittance of the ray along the sun's direction, times that share.

   At 4° the whole disk is up, and red keeps 49 %, green 20 % and blue 4 %: a deep orange. At 0° only half the disk is up, so every value halves, and the long path leaves almost no green or blue. The engine's value agrees in the test to a relative difference of 0.00001 for the same disk radius.
   :::

3. **Hard.** Trace it yourself: in the renderer, find where a change of `AtmosphereHaze` makes the tables compute again, and name the function and the counter that records it.

   :::answer[Worked solution]{tests="trace-haze"}
   The function is `SceneRenderer::UpdateAtmosphere` in `Strata/src/Strata/Renderer/SceneRendererAtmosphere.cpp`. It reads the haze into `AtmosphereSettings` (the density and haze pass through `FiniteAtLeastZero`), and compares them with `TableSettings`. When they differ, it dispatches the transmittance and multiple-scattering passes and counts `AtmosphereTableUpdates`; the sky view follows and counts `AtmosphereSkyViewUpdates`. Later in the function the sun's transmittance is computed again from `GetMedium`, and an environment refresh starts because `m_Environment->Atmosphere` differs. Set a breakpoint on the line that compares `TableSettings` and change the haze in the Inspector to see it stop.
   :::

## Where it lives in Strata

- Constants, the medium and the CPU quadrature: `Strata/src/Strata/Renderer/Atmosphere.h` and `Strata/src/Strata/Renderer/Atmosphere.cpp`.
- The frame's update, the sun's light, the environment refresh and the haze volume: `Strata/src/Strata/Renderer/SceneRendererAtmosphere.cpp`.
- The sky light's fields `AtmosphereDensity`, `AtmosphereHaze`, `GroundAlbedo`, `AerialPerspective` and `AerialPerspectiveScale`: `Strata/src/Strata/Renderer/RendererComponents.h`.
- Shaders: `Strata/shaders/Include/Atmosphere.slang`, `Strata/shaders/Include/AtmospherePass.slang`, `Strata/shaders/IBL/AtmosphereMultipleScattering.comp.slang`, `Strata/shaders/IBL/AtmosphereSkyView.comp.slang`, `Strata/shaders/IBL/AtmosphereAerial.comp.slang`, `Strata/shaders/Include/AerialPerspective.slang` and `Strata/shaders/Scene/Skybox.frag.slang`.
- Tests: the suite `GPU.Atmosphere`.
- The editor command `lighting.applySkyPreset` takes a `sunElevation` and reports a `groundIlluminance`.

## Further reading

- Bruneton and Neyret, "Precomputed Atmospheric Scattering" (2008): the tables that every later method builds on (advanced).
- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique" (2020): the small tables and the multiple-scattering idea that Strata follows (intermediate).
- Preetham, Shirley and Smits, "A Practical Analytic Model for Daylight" (1999): the fitted formula (intermediate).
- Nishita and others, 1993, on displaying the Earth with the scattering of its air: the first march through the air (advanced).
