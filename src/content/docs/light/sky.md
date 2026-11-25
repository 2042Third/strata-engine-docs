---
id: light/sky
title: "The sky as a light: sources, sun extraction and presets"
description: "How Strata lights a scene from every direction with a sky: its three sources, the procedural gradient, the four presets and extracting the sun from a map."
kind: internals
size: M
tracks: [E]
needs: [light/lights, assets/texture-cooking]
time: 55
learn:
  - id: choose-source
    text: choose a sky source for a scene and name what each source computes
  - id: gradient
    text: compute the radiance of the procedural sky along a direction
  - id: preset
    text: predict what a sky preset writes into the scene and how many undo steps it records
  - id: double-sun
    text: explain why Extract Sun is followed by Remove Sun, and what goes wrong without it
since: 0.3.0
status: final
---

A scene lit by one sun alone has black shadows and a black sky. Real shadows are not black, because the whole sky shines on them. This page is about the part of Strata that makes that light: the `SkyLightComponent`, which lights every surface from every direction and also draws the sky behind the scene. The physical atmosphere belongs to [the atmosphere page](../light/atmosphere.md), and the filtering of the light to [image-based lighting](../indirect/ibl.md).

## The problem and how engines solve it

A surface can be lit by the sun and by the sky. The sun comes from one direction: a directional light does it. The sky comes from every direction at once, so the :term[renderer]{id=renderer} needs one value for each direction, the light the sky sends from there. A sky model is a way to make that table of values. Four families exist, and each trades realism against cost and control.

| Approach | What it gives | What it costs |
| --- | --- | --- |
| One constant color | The same light from every direction | Flat, with no up and down; no sky to draw |
| A :term[high dynamic range]{id=high-dynamic-range} (HDR) photograph | A real sky, with its real clouds and sun | Fixed: the time of day cannot change; a big file |
| A formula sky (published 1999 and 2012) | A fitted formula of the sun's height and the haze gives the color at once | A clear sky only; no view from space |
| A physical atmosphere (published 2008 and 2020) | Light scattered through air and haze, simulated | The most work per frame; many settings |

Strata keeps three of these as the values of the sky light's `Source`. `EnvironmentMap` is the photograph. `Procedural` is a small gradient that you control by hand, a cheaper cousin of the formula skies. `Atmosphere` is the physical model. The constant color survives as `AmbientColor`, which lights a scene that has no sky yet.

All three sources write the same kind of result, a cube of sky :term[radiance]{id=radiance}, so everything after that step is shared.

:::why
One shared result keeps the renderer simple: shading, reflections and the background read a single cube and never ask which source made it. The price is that a source can only express what a cube holds: a color for each direction, seen from one point.
:::

An **environment map** is an image of the sky around one point, stored as an equirectangular HDR texture. Its columns are angles around the vertical axis. Its rows are angles from straight up to straight down.

A **procedural sky** is a sky that the engine computes from a few numbers: a gradient of colors from the ground to straight up, plus a disk for the sun, with no image at all.

## The map of the sky light

```mermaid caption="The first active sky light picks a source each frame, and all three sources feed one shared filter chain." alt="A flow from the sky light component to the renderer's update function, which branches into three sources, an environment map, a procedural sky and an atmosphere. The three join one filter chain, which feeds the scene's light and the background."
flowchart LR
	comp["SkyLightComponent: first active one"] --> pick["SceneRenderer::UpdateEnvironment"]
	pick -->|EnvironmentMap| e2c["EquirectToCube.comp: 512 cube"]
	pick -->|Procedural| proc["ProceduralSky.comp: 512 cube"]
	pick -->|Atmosphere| atm["UpdateAtmosphere: sky tables"]
	e2c --> chain["Shared filter chain"]
	proc --> chain
	atm --> chain
	chain --> out["Scene light and background"]
```

The :term[main thread]{id=main-thread} runs `UpdateEnvironment` once per frame and records its work into the frame's :term[command list]{id=command-list}. The cube it makes has faces of 512 texels (`c_EnvironmentCubeSize`). The filter chain, which makes the blurred copies that rough surfaces need, belongs to [image-based lighting](../indirect/ibl.md).

::figure{id=sky-sources variant=map}

::figure{id=sky-sources variant=procedural}

::figure{id=sky-sources variant=atmosphere}

## The contract: what the component promises

The renderer reads the first active sky light of the scene and ignores the others. A sky light on a disabled entity does not count. The next table lists the fields that this page teaches. The atmosphere's own five fields, `AtmosphereDensity`, `AtmosphereHaze`, `GroundAlbedo`, `AerialPerspective` and `AerialPerspectiveScale`, belong to [the atmosphere page](../light/atmosphere.md).

| Field | Meaning | Default |
| --- | --- | --- |
| `Source` | `EnvironmentMap`, `Procedural` or `Atmosphere` | `EnvironmentMap` |
| `Intensity` | Multiplies the sky's :term[luminance]{id=luminance} in :term[nits]{id=lux} | 1 |
| `Rotation` | Degrees around +Y; environment maps only | 0 |
| `ShowBackground` | Draws the sky behind the scene | on |
| `BackgroundBlur` | 0 sharp to 1 fully blurred; never for the atmosphere | 0 |
| `AmbientColor` | Nits, used when there is no environment | (0.03, 0.03, 0.04) |
| `ZenithColor`, `HorizonColor`, `GroundColor` | The procedural gradient, in nits | clear-day blues and grays |
| `SunSize` | The sun's disk, in degrees across | 0.53 |
| `SunIntensity` | Times the light's color, the disk's luminance in nits | 20 |

A field that the current source ignores shows as inactive, with the reason. With `Source` set to `Procedural`, the map field says "Only an environment map uses it". The colors say "Only the procedural sky uses it" when the source is another one. `SunSize` is inactive for a map, since a map holds its own sun.

`BackgroundBlur` is inactive for the atmosphere, whose background is always sharp. `AmbientColor` is inactive once the sky lights the scene, because the ambient color applies only without an environment.

:::rule
A property that another property can disable gets an :term[inactive reason]{id=inactive-reason}, so that the Inspector says why the field does nothing. See the Inspector rules in the engine's guide.
:::

The units are nits, as [light by the numbers](../light/units-exposure.md) explains, never a plain 0 to 1 color. The defaults give the :term[sun-to-sky ratio]{id=sun-to-sky-ratio} of a clear day against the default sun of 3 lux.

## A toy version: the gradient sky

The toy answers one question: what radiance does a viewer see along a direction, given three colors? It uses the numbers of the default procedural sky. Look at how the two halves of the gradient use a power of the direction's height to make the blend fast near the horizon and flat elsewhere.

```cpp sketch="light-sky-toy.cpp"
// A toy gradient sky: the radiance, in nits, that a viewer sees along a direction of a given height (the y of a unit vector).
#include <algorithm>
#include <cmath>
#include <cstdio>

struct Color
{
	float R;
	float G;
	float B;
};

constexpr Color c_Zenith = { 0.045f, 0.08f, 0.155f };
constexpr Color c_Horizon = { 0.165f, 0.185f, 0.21f };
constexpr Color c_Ground = { 0.055f, 0.05f, 0.045f };

Color Mix(const Color& a, const Color& b, float weight)
{
	return { a.R + (b.R - a.R) * weight, a.G + (b.G - a.G) * weight, a.B + (b.B - a.B) * weight };
}

Color SkyRadiance(float height)
{
	height = std::clamp(height, -1.0f, 1.0f);
	if (height >= 0.0f)
	{
		// Above the horizon the zenith color takes over quickly: within about 15 degrees.
		const float weight = 1.0f - std::pow(1.0f - height, 8.0f);
		return Mix(c_Horizon, c_Zenith, weight);
	}
	// Below it the ground takes over within a few degrees.
	const float weight = 1.0f - std::pow(1.0f + height, 16.0f);
	return Mix(c_Horizon, c_Ground, weight);
}

int main()
{
	const float heights[] = { 1.0f, 0.5f, 0.1f, 0.0f, -0.1f, -0.5f };
	for (const float height : heights)
	{
		const Color color = SkyRadiance(height);
		std::printf("height %5.2f: %.4f %.4f %.4f nits\n", height, color.R, color.G, color.B);
	}
	return 0;
}
```

```text output-of="light-sky-toy.cpp"
height  1.00: 0.0450 0.0800 0.1550 nits
height  0.50: 0.0455 0.0804 0.1552 nits
height  0.10: 0.0967 0.1252 0.1787 nits
height  0.00: 0.1650 0.1850 0.2100 nits
height -0.10: 0.0754 0.0750 0.0756 nits
height -0.50: 0.0550 0.0500 0.0450 nits
```

1. **Lines 28–29:** above the horizon, the weight of the overhead color is one minus a power of the distance from straight up.
2. **Lines 31–33:** below it, a higher power makes the ground color take over faster.
3. **Lines 17–19:** `Mix` blends two colors channel by channel.

The output shows the colors move from the overhead blue at height 1 toward the horizon gray, and the ground color takes over right below height 0. Between height 0.5 and 0.1 the color changes little, then it changes fast. The next sections add a sun disk, a cube instead of a function, and a check that skips needless work.

:::example[One direction by hand]
Take a direction at height 0.1, about 6° above the horizon. The weight toward the overhead color is $w = 1 - (1 - 0.1)^8$. The notation $x^8$ reads "x multiplied by itself 8 times". With $0.9^8 = 0.430$, the weight is $w = 0.570$.

The red channel is $0.165 + (0.045 - 0.165) \times 0.570 = 0.097$ nits, between the horizon's 0.165 and the overhead 0.045. The same height at 0.5 gives $w = 0.996$: almost the overhead color. The haze stays within about 15° of the horizon.
:::

## The real code, in the order the data flows

Every frame, `UpdateEnvironment` first forgets the previous frame's sky parameters, then searches for a sky light. The first quote finds the first active one and handles the cases with no sky.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L963-L988"
const SkyLightComponent* skyLight = nullptr;
for (auto [entity, sky, world] : scene.GetRegistry().view<SkyLightComponent, WorldTransformComponent>().each())
{
	if (world.ActiveInHierarchy)
	{
		skyLight = &sky;
		break;
	}
}
// The preview sky of an unlit scene in an editor view: the default procedural sky.
SkyLightComponent previewSky;
if (!skyLight && preview)
{
	previewSky.Source = SkyLightSource::Procedural;
	skyLight = &previewSky;
}
const bool procedural = skyLight && skyLight->Source == SkyLightSource::Procedural;
const bool atmosphere = skyLight && skyLight->Source == SkyLightSource::Atmosphere;
// The atmosphere's tables and its second set of maps exist only while the sky is the atmosphere.
if (!atmosphere)
	m_Atmosphere.reset();
if (!skyLight || (!procedural && !atmosphere && !skyLight->EnvironmentMap.IsValid()))
{
	m_Environment = nullptr; // Release the maps of a removed environment
	m_EnvironmentHold = nullptr;
	return true;
```

1. **Lines 963–971:** the first sky light whose entity is active in the hierarchy wins; the loop stops at it.
2. **Lines 973–978:** an editor view with no sky light still gets a default procedural sky, so a scene with no lights is not black.
3. **Lines 984–988:** no sky light, or an `EnvironmentMap` source with no map set, releases the old maps and returns. The frame's parameters stay zero, and shading then uses the constant ambient light, `AmbientColor` or its default.

The next quote shows the procedural branch. The parameters are what the compute :term[shader]{id=shader} needs: the three colors, the sun's direction and radius, and the sun's radiance.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L1011-L1018"
else if (procedural)
{
	m_EnvironmentHold = nullptr;
	const RenderData::ProceduralSkyParameters parameters = GetProceduralSkyParameters(*skyLight, frame);
	if (!m_Environment || !m_Environment->Procedural || *m_Environment->Procedural != parameters)
		GenerateProceduralSky(commandList, parameters);
	else if (m_Environment->PrefilteredSize != m_Specification.Quality.EnvironmentResolution)
		ResizePrefilteredMap(commandList);
```

The renderer compares the new parameters with the ones of the last frame, exactly. Only a change runs `GenerateProceduralSky`, so a still sky costs one comparison per frame. The sun's direction comes from the directional light (`GetProceduralSkyParameters` reads `frame.DirectionalLightDirection`), or from a default direction when the scene has no light. That is why `Rotation` is for maps only: moving the light moves the sun.

The map branch is the one that must wait for an asset.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L1020-L1029"
else
{
	Ref<Texture> texture = m_Assets.Resolve<Texture>(skyLight->EnvironmentMap, AssetPriority::High);
	if (!texture || !texture->GetGPUTexture())
	{
		// Constant ambient until the environment arrives (counted as pending by the resolve cache); the map is raised
		// whole as soon as it is loaded.
		HoldEnvironmentMap(skyLight->EnvironmentMap);
		return true;
	}
```

1. **Line 1022:** the renderer asks for the texture at high priority and never blocks on it.
2. **Lines 1025–1028:** while the texture is not loaded, the frame returns at once and the constant ambient light lights the scene. The map is raised whole as soon as it arrives.

When the texture is ready, `ProcessEnvironment` runs `EquirectToCube.comp`, which turns the equirectangular picture into the 512 cube, then runs the filter chain. The environment is computed once per map, not once per frame.

:::analogy
A map is a photograph of a room, taken from the middle: every direction has a color. The cube is the same photograph pasted on the inside of a box, so that the :term[graphics processing unit]{id=gpu} (GPU) can find a direction's color with a simple lookup.

**Where it breaks:** the box has no depth. A surface near a wall of the real room would see the wall closer; the cube cannot show it.
:::

### The procedural sky in the shader

`ProceduralSky.comp.slang` writes the cube's first level from the parameters, with one thread for each texel. The function below is the toy's gradient plus the sun.

```slang src="Strata/shaders/IBL/ProceduralSky.comp.slang#L23-L50"
float3 SkyRadiance(float3 direction, float texelAngle)
{
	float height = clamp(direction.y, -1.0, 1.0);
	float3 color;
	if (height >= 0.0)
	{
		// The horizon color is haze near the horizon: it gives way to the zenith color within about 15 degrees.
		float zenith = 1.0 - pow(1.0 - height, 8.0);
		color = lerp(u_Parameters.HorizonColor.rgb, u_Parameters.ZenithColor.rgb, zenith);
	}
	else
	{
		// Below the horizon the ground takes over within a few degrees.
		float ground = 1.0 - pow(1.0 + height, 16.0);
		color = lerp(u_Parameters.HorizonColor.rgb, u_Parameters.GroundColor.rgb, ground);
	}

	// The sun's disk, its edge smoothed over one texel. The angle comes from the chord between the directions, which
	// stays precise for the small angles involved (acos of a dot product near 1 does not).
	float radius = u_Parameters.SunDirection.w;
	if (radius > 0.0)
	{
		float chord = length(direction - u_Parameters.SunDirection.xyz);
		float angle = 2.0 * asin(min(chord * 0.5, 1.0));
		float coverage = clamp((radius - angle) / texelAngle + 0.5, 0.0, 1.0);
		color = lerp(color, u_Parameters.SunRadiance.rgb, coverage);
	}
	return color;
```

1. **Lines 29–31:** above the horizon, the blend weight is the toy's power of 8.
2. **Lines 35–37:** below it, a power of 16 makes the ground take over faster.
3. **Lines 42–48:** the sun's disk is drawn in the same pass, with an edge smoothed over one texel.

The sun's edge uses the chord between two directions, not the inverse :term[cosine]{id=cosine} of their :term[dot product]{id=dot-product}. For a tiny angle the dot product is within rounding of 1, and `acos` loses the difference. The chord length stays accurate.

The coverage of the sun in a texel is $(r - \theta) / t + 0.5$, clamped between 0 and 1. Here $r$ is the disk's radius and $\theta$ the angle from the disk's center, both in :term[radians]{id=radian}, and $t$ is the texel's angle. For a 512 cube $t = 2 / 512 = 0.0039$ radians, or 0.22°, so the 0.53° disk is about 2.4 texels across. The edge is soft by design, since no cube texel can be sharper.

The shader then clamps every value to 65,000: the cube stores 16-bit :term[floating-point numbers]{id=floating-point-number}, whose largest finite value is 65,504. A sun brighter than that cannot live in the cube. The disk's `SunIntensity` draws the sun in the picture, while the directional light does the sun's real lighting.

## Presets: a sky and a sun in one step

A sky set by hand takes a dozen numbers that must agree. A **sky preset** is a stored bundle of values for the sky light and the sun, in real units. Strata has four, in `SkyPresets.cpp`. The editor offers them as the buttons **Clear**, **Hazy**, **Overcast** and **Golden Hour**, and as the command `lighting.applySkyPreset`.

```cpp src="Strata/src/Strata/Renderer/SkyPresets.cpp#L20-L47"
SkyPresetValues Atmosphere(float density, float haze, float elevation)
{
	SkyPresetValues values;
	values.Source = SkyLightSource::Atmosphere;
	values.AtmosphereDensity = density;
	values.AtmosphereHaze = haze;
	values.GroundAlbedo = 0.3f;
	values.SunElevation = elevation;
	// The sun above the air: the atmosphere dims and reddens it on its way down (about 95,000 lux 40 degrees up).
	values.SunIlluminance = 120000.0f;
	return values;
}

SkyPresetValues Overcast()
{
	// The atmosphere has no clouds (its haze is Earth's clear aerosol): an overcast sky is a near-uniform procedural one
	// of about 7,700 lux on flat ground, over a faint sun 60 degrees up as soft as the light allows (its diameter's
	// maximum), whose disk is not drawn.
	SkyPresetValues values;
	values.Source = SkyLightSource::Procedural;
	values.ZenithColor = glm::vec3(2600.0f, 2650.0f, 2750.0f);
	values.HorizonColor = glm::vec3(2200.0f, 2250.0f, 2300.0f);
	values.GroundColor = glm::vec3(400.0f, 380.0f, 360.0f);
	values.SunDiskIntensity = 0.0f;
	values.SunElevation = 60.0f;
	values.SunIlluminance = 1500.0f;
	values.ShadowSoftness = 10.0f;
	return values;
```

1. **Line 29:** the sun's illuminance is the value above the air, 120,000 lux. The atmosphere dims it on its way down.
2. **Lines 35–37:** a comment says that the atmosphere has no clouds, so a cloudy sky is a near-uniform procedural one.
3. **Lines 40–42:** the cloudy-sky colors are in thousands of nits: an even gray sky.
4. **Line 43:** the sun's disk intensity is 0, so no disk is drawn.
5. **Line 46:** the sun's softness is 10°, the largest the light allows.

```cpp src="Strata/src/Strata/Renderer/SkyPresets.cpp#L52-L57"
static const std::array<SkyPresetEntry, c_SkyPresetCount> s_Entries = { {
	{ SkyPreset::Clear, "Clear", Atmosphere(1.0f, 1.0f, 40.0f) },
	{ SkyPreset::Hazy, "Hazy", Atmosphere(1.2f, 4.0f, 35.0f) },
	{ SkyPreset::Overcast, "Overcast", Overcast() },
	{ SkyPreset::GoldenHour, "GoldenHour", Atmosphere(1.0f, 1.5f, 6.0f) }
} };
```

The entries pass the air's density, its haze and the sun's elevation. The result is this table.

| Preset | Source | Density, haze | Sun elevation | Sun illuminance above the air |
| --- | --- | --- | --- | --- |
| `Clear` | `Atmosphere` | 1, 1 | 40° | 120,000 lux |
| `Hazy` | `Atmosphere` | 1.2, 4 | 35° | 120,000 lux |
| `Overcast` | `Procedural` | gray colors of the quote | 60° | 1,500 lux, disk off |
| `GoldenHour` | `Atmosphere` | 1, 1.5 | 6° | 120,000 lux |

::figure{id=sky-presets variant=clear}

::figure{id=sky-presets variant=hazy}

::figure{id=sky-presets variant=overcast}

::figure{id=sky-presets variant=golden-hour}

The command does more than copy the table. It works in a single `SceneEditTransaction` named "Apply Sky Preset", in these steps:

- The command finds the first active sky light and the brightest directional light, or creates entities named `Sky` and `Sun`.
- The command writes the sky's source and values, sets the sun's illuminance, color and shadow softness, and turns the sun to the preset's elevation. The light keeps its own :term[azimuth]{id=azimuth}, the angle from +X toward +Z, or 20° when there is no light.
- The command makes the active Post Process's manual exposure automatic with a compensation of 0, and raises `AutoExposureMaxEV` to 16 when it is below 15. A real sun clips to white under a manual exposure meant for 3 lux.
- The command returns `groundIlluminance`, the lux on a surface facing the sun at the ground.

A preset applied twice records no second step, because the command compares what it would write with what is there.

:::example[The Clear preset]
The sun's direction at elevation 40° and azimuth 20° is $(\cos 40° \cos 20°,\ \sin 40°,\ \cos 40° \sin 20°)$, which is $(0.720, 0.643, 0.262)$. The light shines the other way, along minus that vector.

The code's comment says the atmosphere leaves about 95,000 lux on a surface facing the sun: that is the `groundIlluminance` a client sees. A flat floor gets $95{,}000 \times \sin 40° = 61{,}000$ lux, since a tilted surface gets the :term[sine]{id=sine} of the sun's elevation. For the `Overcast` preset the sun is 1,500 lux at 60°, so a floor gets $1{,}500 \times 0.866 = 1{,}300$ lux from it.

The code's comment gives the sky about 7,700 lux on flat ground, so the sun-to-sky ratio is $1{,}300 / 7{,}700 = 0.17$: no visible shadows.
:::

A preset's values never change meaning, so a script that applies `Clear` gets the same values after an engine update.

## Extracting the sun from a map

An HDR photograph of a sunny day holds the sun as a few texels of enormous luminance. Used as an environment map alone, the sun lights surfaces but casts no shadow, because a cube holds no geometry to block it. The usual fix is a directional light where the sun is.

Then two things light the scene from that direction: the light, and the sun in the map. This is the **double sun**. The light's shadows fill with the map's sun, and every surface facing the sun is too bright.

Strata gives two steps that remove the problem. **Extract Sun** (the command `lighting.extractSun`) finds the sun in the map's :term[source file]{id=source-file} and writes it into a directional light. **Remove Sun** (the import setting `RemoveSun`, which [texture cooking](../assets/texture-cooking.md) teaches) paints the sun out of the map when it is cooked. The Inspector's **Extract Sun** button runs both, one after the other.

`HDRSun::Find` works on the decoded floats, before the :term[importer]{id=importer} shrinks or clamps them. Its steps are these:

1. `Find` takes the brightest texel. That texel must be at least 8 times the sky around it, or the map has no sun.
2. `Find` takes the connected texels at least 4 times brighter than the sky around, up to 3° across.
3. `Find` sums each texel's radiance times its :term[solid angle]{id=solid-angle} (the texel's area on the sphere, in :term[steradians]{id=steradian}) for each :term[color channel]{id=color-channel}. The sum is the sun's illuminance.
4. `Find` flags a flat-topped peak as clipped: the file saturated, and the light is a lower bound.

The command then writes three values into the light. Its rotation turns it to face away from the sun's place in the sky, with the sky's `Rotation` applied. Its `Color` is the illuminance divided by its largest channel. Its `Intensity` is the largest channel times the sky's `Intensity`.

The step is one undo step named "Extract Sun", and it fails while the game plays. When the map is cooked with `RemoveSun`, `HDRSun::Remove` replaces each texel of the sun with an average of the sky texels at its border.

:::example[A sun in a map]
The real sun is 0.53° across, so its radius is 0.004625 radians. Its solid angle is $\pi r^2 = \pi \times 0.004625^2 = 6.7 \times 10^{-5}$ steradians. The notation $r^2$ reads "r multiplied by itself".

A map with the sun at $1.5 \times 10^9$ nits gives $1.5 \times 10^9 \times 6.7 \times 10^{-5} = 100{,}000$ lux, a good sun. The cube could never hold that value, since 65,000 is its limit. That is why the finder reads the source file, and why the light, not the cube, carries the sun's strength.

If the illuminance is (42,000, 40,000, 36,000) lux, `Intensity` is 42,000 and `Color` is (1, 0.95, 0.86).
:::

::compare{id=extract-sun}

## What Strata does not do here

Strata draws no clouds, stars or moon with the sky light. The atmosphere's haze is the clear air's own tiny particles, and the `Overcast` preset is a nearly uniform procedural sky, not a cloud layer. A photograph can hold clouds, stars and a moon: the sky light then shows them as the photograph does, and cannot change them. A search of the engine library's code finds the word moon only in a tooltip.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| A formula sky as a fourth source | The published daylight models (Further reading) | A realistic clear sky for the cost of a formula | A source that overlaps `Procedural` and `Atmosphere`; more code to test |
| Cloud layers | Games that show weather | Moving clouds and their shadows | A new pass and a large cost; no scene needs it yet |
| Extract the sun on every import | A tool that runs the finder for each map | No double sun by mistake | A directional light made behind the author's back |
| One sky light for each region | Scenes with a probe in each room | Local sky colors | Many cubes and many filter runs |

## How it is tested

The suite `GPU.ProceduralSky` renders on the shared device. Its cases check that the overhead and horizon colors show in their directions, and that the sun's disk sits where the light comes from. They check that a white sphere is brighter on top than below, that the cube is made again only when the sky or the sun changes, and that new skies keep a real sun-to-sky ratio.

The suite `Editor.Lighting` checks `lighting.applySkyPreset`: one undo step, no change when applied twice, missing entities created, a manual exposure made automatic, bad parameters changing nothing, and play mode changing the running copy. The suite `Asset.HDRSun` tests the finder. Run one suite directly:

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=GPU.ProceduralSky
```

The program prints each failing case and a count of passes. A machine without a graphics card skips the suite with `ctest -LE gpu`.

## Changing it safely

- A new source is a new value of `SkyLightSource` and a new branch in `UpdateEnvironment`. Append it at the end, so that the existing values keep their numbers.
- A new field of the component needs its inactive reason, a property row and a use in the feature test project.
- A preset's values never change meaning. Add a preset by appending an entry and a button.
- Never block on a map: `UpdateEnvironment` returns with the ambient light, and no code waits for a load.

## Summary

- `Source` chooses a photograph, a gradient or a physical atmosphere, and each source computes one cube that the shared filter chain reads.
- The procedural sky blends a horizon color with an overhead color or a ground color by a power of the direction's height, and draws the sun's disk with an edge one texel wide.
- A preset writes a sky, a sun and an automatic exposure in one undo step, and returns the ground illuminance.
- Extract Sun turns a map's sun into the shadow-casting light, and Remove Sun paints it out of the map so that the sun does not light the scene twice.

## Check yourself

1. A scene has a sky light with `Source` set to `Procedural` and no directional light. Where is the sun's disk?

   :::answer{tests="choose-source"}
   The disk sits in a default direction, 45° above the horizon. The parameters take the sun's direction from the directional light when there is one, and from a default otherwise. It is not straight up, and `Rotation` does nothing for this source.
   :::

2. A map is assigned to a sky light, but its file is large and still loading. What does the scene look like in the meantime?

   - A) black, until the map arrives
   - B) lit by the constant `AmbientColor`
   - C) lit by the default procedural sky

   :::answer{tests="choose-source"}
   B. `UpdateEnvironment` returns early and the frame's environment parameters stay zero, so shading uses the ambient color. A is wrong because the ambient color is not black by default; C is the preview sky of an editor view with no sky light at all.
   :::

3. Compute the weight of the overhead color at height 0.5.

   :::answer{tests="gradient"}
   $w = 1 - (1 - 0.5)^8 = 1 - 0.0039 = 0.996$. The sky at 30° is already almost the overhead color.
   :::

4. You apply the preset `Clear`, and then apply `Clear` again. How many undo steps exist?

   :::answer{tests="preset"}
   One. The second application writes the same values, the command sees no change, and it records no step. The first step covers the sky, the sun and, when it changed, the exposure.
   :::

5. You extract the sun from a map but never set Remove Sun. Name two symptoms.

   :::answer{tests="double-sun"}
   The light's shadows fill with the map's own sun, so they are lighter than they should be, and surfaces facing the sun receive about twice its light. The Inspector's button sets `RemoveSun` right after the extraction.
   :::

## Exercises

1. **Basic.** Apply each of the four presets to the Basic 3D scene. After each, open the Lighting view and read the sun-to-sky note under its legend, and write down `groundIlluminance` from the command's result.

   :::answer[Worked solution]{tests="preset"}
   Use **Clear**, **Hazy**, **Overcast** and **Golden Hour** in the Sky section, or run `lighting.applySkyPreset` with the preset name. Predict first: `Overcast` has a sun of 1,300 lux on a floor against 7,700 lux of sky, so its ratio is about 0.17, below every other preset's. Golden Hour has the sun 6° up, so its floor gets at most $120{,}000 \times \sin 6° = 12{,}500$ lux before the air dims it. Compare the viewport's numbers with your predictions.
   :::

2. **Medium.** Trace it yourself: find where `lighting.applySkyPreset` gets its values and where its single undo step is made.

   :::answer[Worked solution]{tests="preset"}
   Search the command's name in `StrataEditor/src/Editor/EditorLightingCommands.cpp`. The registration calls `ApplySkyPreset` in the same file. That function reads the values with `GetSkyPresetValues` in `Strata/src/Strata/Renderer/SkyPresets.cpp`. It creates one `SceneEditTransaction` named "Apply Sky Preset", tracks the sky, the light and the Post Process in it, and ends with `FinishEdit`, which records the one step.
   :::

3. **Hard.** Write a program that prints how much of a texel the sun's disk covers at several angles, using the shader's formula, and find from the output how many texels wide the disk's edge is.

   :::answer[Worked solution]{tests="gradient,double-sun" solution="sketches/light-sky-diskedge.cpp"}
   The full solution follows. The coverage is 1 up to 0.153°, 0.5 at the disk's radius of 0.265°, and 0 from 0.377°. The edge spans one texel, 0.22°.

   ```cpp sketch="light-sky-diskedge.cpp"
   // How much of a texel the sun's disk covers, from the angle between the texel's direction and the sun's center.
   #include <algorithm>
   #include <cmath>
   #include <cstdio>

   constexpr float c_Pi = 3.14159265f;

   float Coverage(float radius, float angle, float texelAngle)
   {
   	return std::clamp((radius - angle) / texelAngle + 0.5f, 0.0f, 1.0f);
   }

   int main()
   {
   	const float radius = 0.53f * 0.5f * c_Pi / 180.0f;
   	const float texelAngle = 2.0f / 512.0f;
   	std::printf("texel %.3f degrees, disk radius %.3f degrees\n", texelAngle * 180.0f / c_Pi, radius * 180.0f / c_Pi);
   	const float degrees[] = { 0.0f, 0.15f, 0.2f, 0.265f, 0.3f, 0.35f, 0.4f };
   	for (const float angle : degrees)
   		std::printf("angle %.3f degrees: coverage %.2f\n", angle, Coverage(radius, angle * c_Pi / 180.0f, texelAngle));
   	return 0;
   }
   ```

   ```text output-of="light-sky-diskedge.cpp"
   texel 0.224 degrees, disk radius 0.265 degrees
   angle 0.000 degrees: coverage 1.00
   angle 0.150 degrees: coverage 1.00
   angle 0.200 degrees: coverage 0.79
   angle 0.265 degrees: coverage 0.50
   angle 0.300 degrees: coverage 0.34
   angle 0.350 degrees: coverage 0.12
   angle 0.400 degrees: coverage 0.00
   ```

   1. **Line 10:** the shader's coverage formula, clamped to 0 through 1.
   2. **Line 15:** the disk's radius is half of 0.53°, in radians.
   3. **Line 16:** a texel at the center of a 512 face spans 2 / 512 radians.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Renderer/RendererComponents.h`: `SkyLightComponent` and `SkyLightSource`.
- `Strata/src/Strata/Renderer/SceneRenderer.cpp`: `UpdateEnvironment`, `ProcessEnvironment`, `GenerateProceduralSky`.
- `Strata/shaders/IBL/ProceduralSky.comp.slang` and `Strata/shaders/IBL/EquirectToCube.comp.slang`.
- `Strata/src/Strata/Renderer/SkyPresets.cpp`: the presets.
- `Strata/src/Strata/Asset/HDRSun.h`: `Find` and `Remove`.
- `StrataEditor/src/Editor/EditorLightingCommands.cpp`: `lighting.applySkyPreset` and `lighting.extractSun`.
- Tests: `GPU.ProceduralSky`, `Editor.Lighting`, `Asset.HDRSun`.

## Further reading

- Preetham, Shirley and Smits, "A Practical Analytic Model for Daylight" (1999): the first widely used formula sky (advanced).
- Hosek and Wilkie, "An Analytic Model for Full Spectral Sky-Dome Radiance" (2012): a formula sky with a ground (advanced).
- Bruneton and Neyret, "Precomputed Atmospheric Scattering" (2008): the physical atmosphere with tables (advanced).
- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique" (2020): the atmosphere at game cost (advanced).
