---
id: light/lights
title: "Lights: the sun, points and spots"
description: "How Strata turns light components into one sun in the frame constants and point and spot lights as records, with a windowed falloff and a smooth cone."
kind: internals
size: L
tracks: [E]
needs: [light/brdf, draw/render-scene, world/interpolation]
time: 80
learn:
  - id: falloff
    text: compute the brightness of a point light at a distance from its intensity and range with the windowed falloff
  - id: cone
    text: compute a spot light's factor at an angle off its axis from the inner and outer cone angles
  - id: one-sun
    text: predict which directional light shines, and what the frame holds when none does
  - id: record-path
    text: trace a light component's change through the signals, the sync and the change log to the record the shader reads
  - id: signal-rule
    text: explain why a direct write to a light field needs a signal and what happens without one
since: 0.3.0
status: final
---

A scene stores a light as a component on an entity. The forward pass, the :term[shader]{id=shader} that colors every visible surface, needs lights as plain numbers that it can loop over. This page follows that conversion: one sun goes into the frame constants, a block of numbers the shader reads for the whole frame. Every point, spot and rectangle light becomes a record in the :term[render scene]{id=render-scene}. The page does not teach the units of light, the culling of lights, shadows, highlights of sized lights or the sky, which other pages teach.

## The problem and how engines solve it

Take a lamp on a table in a dark room. A book next to the lamp is bright, a book across the room is dim, and a book in the next room gets nothing. A game must reproduce that for every lamp, every pixel and every frame, and it must do so cheaply.

Three questions follow. How does the brightness fall with distance? Where does the light stop? How many kinds of light does the engine need?

Physics answers the first question. A lamp of luminous intensity $I$ in :term[candela]{id=candela} sends its light out in all directions. At a distance $d$ the light spreads over a sphere, and a surface that faces the lamp receives $I / d^2$ :term[lux]{id=lux}. A lamp of 10 candela gives 10 lux at 1 m, 2.5 lux at 2 m and 0.625 lux at 4 m.

Doubling the distance quarters the light. The page on [light units and exposure](../light/units-exposure.md) explains both units.

The formula never reaches zero. A lamp in a house would then reach every pixel of a city, and the :term[renderer]{id=renderer} would have to test every lamp against every pixel. Engines therefore cut each lamp off at a distance. A hard cut at 10 m shows: a surface at 9.99 m receives $10 / 99.8 \approx 0.1$ lux, a surface at 10.01 m receives nothing, and a bright ring appears on the floor. The cut must arrive smoothly.

Engines have solved this in three ways.

- **Constant, linear and quadratic attenuation.** The fixed-function pipelines of older graphics interfaces divide the light by $k_c + k_l d + k_q d^2$ and give the artist the three numbers. The knobs need no units, but they do not meet physics, and the sum never becomes zero, so no distance bounds the light.
- **Inverse square with a hard cutoff.** The physics is right and the bound exists, but the ring shows.
- **Inverse square times a window.** The physical law is multiplied by a smooth window that equals one near the lamp and falls to exactly zero at the cutoff. Karis described this form for Unreal Engine 4 in 2013 (see Further reading). Strata uses it.

The window has a price. Inside the cutoff the light is a little dimmer than physics says, and close to the cutoff it is much dimmer. You also have to pick the cutoff yourself: nothing derives it from the intensity. The next sections show the numbers.

A **punctual light** is a light with no shape: it shines from one point, as a point light and a spot light do, or from one direction, as the sun does. Real lamps have a size, but a shape costs a lot for every pixel. Real-time engines therefore treat most lights as points and add the size back only in the highlight. Strata's one light with a true shape, a glowing rectangle, has a page of its own ([area lights](../light/area-lights.md)).

The distance at which the window reaches zero is the light's **range**: the bound beyond which a point or spot light adds nothing, used to decide which lights can reach a pixel.

The sun needs no falloff. It is so far away that its rays are parallel and its light is the same everywhere in the scene. One direction, one color and one intensity in lux describe it. A spot light is a point light with a cone: the shade of a lamp or the head of a torch.

Three kinds of punctual light cover what most scenes need. Strata has these three and, since 0.8.0, the **Rect Light**: a glowing rectangle such as a ceiling panel or a sign. This page follows it as far as its record.

## The map: files, owners and data flow

Each point, spot or rectangle light becomes one **light record** in the renderer's copy of the scene. A record holds eight four-number vectors (128 :term[bytes]{id=byte}): the position, the color times the intensity, the direction, the cone, the bounds, the source radius and the two axes of a rectangle's face. The sun has no record. The renderer reads its component again every frame and writes it into the frame constants, a block of numbers the shader reads for the whole frame.

```mermaid caption="Point, spot and rectangle lights travel through signals and the sync into records and a change log. The sun skips the records and goes straight into the frame constants." alt="A diagram with two paths. Point, spot and rectangle light components flow through signals and a sync into records and a change log, then to the graphics copy, the clusters and the shader. The directional light component flows from a once-per-frame search into the frame constants and then to the shader."
flowchart TD
	point["PointLightComponent, SpotLightComponent, RectLightComponent"] -->|"on_construct, on_update, on_destroy"| queue["queue in RenderLights"]
	moves["transform changes, drawn transforms"] --> sync["RenderLights::Sync"]
	queue --> sync
	sync --> records["LightRecord array (128 bytes each)"]
	sync --> log["change log (version, record)"]
	records --> gpu["GPU copy of the records"]
	log --> gpu
	gpu --> cull["cull to LightData (64 bytes) and clusters"]
	cull --> shader["Forward.frag.slang"]
	sun["DirectionalLightComponent"] -->|"every frame"| collect["SceneRenderer::CollectLights"]
	collect --> frame["FrameConstants"]
	frame --> shader
```

The diagram omits the shadow slots and the clusters, which later pages cover. The table shows who owns what.

| Part | File at the pin | Owns |
| --- | --- | --- |
| Components | `Strata/src/Strata/Renderer/RendererComponents.h` | The data of the four light types, their units and the tag of a light's glowing face |
| Records | `Strata/src/Strata/Renderer/RenderLights.cpp` | The record array, the signals, the :term[change log]{id=change-log} |
| Rectangle faces | `Strata/src/Strata/Renderer/AreaLights.cpp` | A rectangle light's face, brightness and bounds |
| Record layouts | `Strata/src/Strata/Renderer/SceneRenderData.h` | `LightRecord` and `LightData` |
| Sun and frame | `Strata/src/Strata/Renderer/SceneRenderer.cpp` | Choosing the sun, the preview sun, the frame constants |
| Falloff and cone | `Strata/shaders/Include/PBR.slang` | The two attenuation functions |
| Use | `Strata/shaders/Scene/Forward.frag.slang` | The loop over the lights of a pixel's cluster |

The :term[main thread]{id=main-thread} runs all of this: the scene, the signals, the sync and the frame collection. The :term[graphics processing unit]{id=gpu} (GPU) copy of the records follows the change log that the sync writes.

## The contract: what the components promise

Four components describe lights, and each field of each is plain data. The sun is `DirectionalLightComponent`: its `Intensity` is a number of lux, with a default of 3, and its `Color` multiplies it. A point light is `PointLightComponent`: `Intensity` is luminous intensity in candela, with a default of 10, and `Range` is 10 m. A spot light is `SpotLightComponent`, which adds the cone and has defaults of its own: 20 candela and 15 m.

Point and spot lights also have a `SourceRadius`, the **Source Radius** of the Inspector: the radius of the bulb or flame in meters, at most 2 m. It widens their highlights and nothing else. The sun's matching size is `ShadowSoftness`, shown as **Angular Diameter**: the disk's size in degrees, 0.53 by default. It sizes both the sun's highlight and its shadows' soft edge.

A rectangle light is `RectLightComponent`: a face of `Width` by `Height` meters, 1 by 0.5 by default, that shines along -Z. Its `Intensity` is the :term[luminance]{id=luminance} of the face in :term[nits]{id=lux}, 25 by default, or its power in :term[lumens]{id=lumen} when `Units` says so. Its `Range` of 10 m is measured from the rectangle. The tag `LightSurfaceComponent`, the **Light Surface** of the Inspector, holds no data. **Make Area Light** adds it to the glowing mesh that shows a panel, so that reflections and the light's own shadows do not count the glow a second time.

Nothing changes these numbers. Exposure alone maps them to the screen.

The listing shows the spot light, which holds everything the point light has plus the cone.

```cpp src="Strata/src/Strata/Renderer/RendererComponents.h#L66-L79"
// Shines along the entity's forward (-Z) direction.
struct SpotLightComponent
{
	glm::vec3 Color = { 1.0f, 1.0f, 1.0f };
	float Intensity = 20.0f; // Luminous intensity in candela along the axis, times Color (not spread over the cone)
	float Range = 15.0f;
	float SourceRadius = 0.0f; // As PointLightComponent's: at most PointLightComponent::c_MaxSourceRadius
	float InnerConeAngle = 20.0f; // Degrees, half angle: full intensity inside
	float OuterConeAngle = 30.0f; // Degrees, half angle: no light outside
	bool CastShadows = false;
	float ShadowBias = 1.0f;         // As PointLightComponent's
	float ShadowNormalBias = 1.5f;
	float ShadowFilterRadius = 1.5f; // At most PointLightComponent::c_MaxShadowFilterRadius
};
```

1. **Line 66:** every light shines along the entity's -Z axis, so you aim a light by rotating its entity.
2. **Line 70:** the candela are the intensity along the axis; the engine does not spread them over the cone.
3. **Line 71:** the range is a distance in meters, a bound and not a brightness.
4. **Line 72:** the source radius changes only the highlight, so a lamp with a large bulb lights a floor as a point would.
5. **Lines 73–74:** the two angles are half angles in degrees, measured from the axis.

The **inner/outer cone angle** are the two half angles of a spot light's cone, measured from its axis in degrees. The light has full strength inside the inner angle and none outside the outer angle, and it fades smoothly between them. A spot light with an inner angle of 20 degrees and an outer angle of 30 degrees lights a circle of 60 degrees across at most.

The rules below hold for every light, and each has a reason.

- **One sun per frame.** Only the brightest active directional light shines; Strata ignores the others without a warning. The reason is cost: the sun has a set of shadow cascades, shadow images that each cover one range of distances from the camera, and the frame constants have room for one direction. An equal intensity keeps the light that the scene's view met first.
- **Inactive lights keep a record.** A light on a disabled entity keeps its record, marked "not drawn", and the record is rebuilt when the entity wakes. The reason is that waking the entity changes one record and moves nothing else.
- **Bad numbers draw nothing.** An intensity or range that is zero, negative or not finite, or a color or matrix that is not finite, makes a record that is not drawn. The reason is that one bad value must never spread through the lighting of the frame.
- **The range is a bound.** Raising it makes the light reach farther. It also changes the window, so a surface at a fixed distance gets a little more light. The light does not become a brighter lamp.
- **Lights sit where the scene draws them.** A light on an entity that :term[fixed steps]{id=fixed-step} move is placed at its :term[drawn transform]{id=drawn-transform}, between its last two poses. The reason is that a lamp on a moving cart must not tremble against the cart ([interpolation](../world/interpolation.md)).

:::rule
A direct write to a light field must signal. Write the field with `registry.patch`, or call `Entity::MarkModified` on the component, or the light's record keeps its old value. The reason is that the render scene builds light records from signals and never scans the lights each frame.

Values written right after `AddComponent` need no signal, because a new component queues its record. In tests, `Validate` names the difference, and Debug syncs assert on it. The [transform contract](../world/scene-graph.md) holds the same rule for transforms.
:::

## A toy version

The toy makes a record from a light, applies the falloff and the cone, and prints numbers. It has no vectors, no positions and no GPU, so every line shows one idea. It refuses a bad light by marking its record not drawn, as the engine does.

```cpp sketch="light-lights-toy.cpp"
#include <algorithm>
#include <cmath>
#include <cstdio>

namespace
{

	constexpr float c_DegreesToRadians = 3.14159265f / 180.0f;

	struct Light
	{
		float Intensity = 0.0f; // Candela
		float Range = 0.0f;     // Meters
		float InnerDegrees = 0.0f;
		float OuterDegrees = 0.0f;
	};

	// What the shader needs, computed once: 1 / range^2 and the cosines of the cone's angles.
	struct Record
	{
		float Intensity = 0.0f;
		float InverseRangeSquared = 0.0f;
		float CosInner = 1.0f;
		float CosOuter = 1.0f;
		bool Drawn = false;
	};

	Record MakeRecord(const Light& light, bool active)
	{
		Record record;
		if (!active || !(light.Intensity > 0.0f) || !(light.Range > 0.0f) || !std::isfinite(light.Intensity) || !std::isfinite(light.Range))
			return record; // Kept, but not drawn
		record.Intensity = light.Intensity;
		record.InverseRangeSquared = 1.0f / (light.Range * light.Range);
		record.CosInner = std::cos(light.InnerDegrees * c_DegreesToRadians);
		record.CosOuter = std::cos(light.OuterDegrees * c_DegreesToRadians);
		record.Drawn = true;
		return record;
	}

	float Falloff(const Record& record, float distance)
	{
		const float ratio = distance * distance * record.InverseRangeSquared;
		const float window = std::clamp(1.0f - ratio * ratio, 0.0f, 1.0f);
		return window * window / std::max(distance * distance, 1e-4f);
	}

	float Cone(const Record& record, float degreesOffAxis)
	{
		const float cosine = std::cos(degreesOffAxis * c_DegreesToRadians);
		const float t = std::clamp((cosine - record.CosOuter) / std::max(record.CosInner - record.CosOuter, 1e-4f), 0.0f, 1.0f);
		return t * t;
	}

}

int main()
{
	const Record point = MakeRecord({ 10.0f, 10.0f, 0.0f, 0.0f }, true);
	for (const float distance : { 1.0f, 5.0f, 8.0f, 9.0f, 10.0f })
		std::printf("d=%4.1f m: windowed %.4f  plain 1/d^2 %.4f  lux %.4f\n", distance, Falloff(point, distance), 1.0f / (distance * distance),
			point.Intensity * Falloff(point, distance));

	const Record spot = MakeRecord({ 20.0f, 15.0f, 20.0f, 30.0f }, true);
	for (const float degrees : { 0.0f, 10.0f, 20.0f, 25.0f, 30.0f, 35.0f })
		std::printf("%4.1f degrees off axis: cone factor %.4f\n", degrees, Cone(spot, degrees));

	const Record broken = MakeRecord({ std::nanf(""), 10.0f, 0.0f, 0.0f }, true);
	const Record switchedOff = MakeRecord({ 10.0f, 10.0f, 0.0f, 0.0f }, false);
	std::printf("NaN intensity drawn: %d, inactive drawn: %d\n", broken.Drawn ? 1 : 0, switchedOff.Drawn ? 1 : 0);
	return 0;
}
```

```text output-of="light-lights-toy.cpp"
d= 1.0 m: windowed 0.9998  plain 1/d^2 1.0000  lux 9.9980
d= 5.0 m: windowed 0.0352  plain 1/d^2 0.0400  lux 0.3516
d= 8.0 m: windowed 0.0054  plain 1/d^2 0.0156  lux 0.0545
d= 9.0 m: windowed 0.0015  plain 1/d^2 0.0123  lux 0.0146
d=10.0 m: windowed 0.0000  plain 1/d^2 0.0100  lux 0.0000
 0.0 degrees off axis: cone factor 1.0000
10.0 degrees off axis: cone factor 1.0000
20.0 degrees off axis: cone factor 1.0000
25.0 degrees off axis: cone factor 0.2990
30.0 degrees off axis: cone factor 0.0000
35.0 degrees off axis: cone factor 0.0000
NaN intensity drawn: 0, inactive drawn: 0
```

1. **Lines 31–32:** an inactive light, or one with a bad intensity or range, gets a record that is kept and not drawn.
2. **Line 34:** the record stores one over the range squared, so the shader never divides by the range.
3. **Lines 43–45:** the window is one minus the fourth power of distance over range, squared again, and then divided by the squared distance.
4. **Line 51:** the cone works with :term[cosines]{id=cosine} and never takes an angle back out of a :term[dot product]{id=dot-product}.

The first rows are the falloff of a lamp of 10 candela with a range of 10 m. At 1 m the window hardly matters: 0.9998 against 1. At 5 m the lux is 0.3516 where the plain law gives 0.4, and at 8 m it is 0.0545 where the plain law gives 0.156. At 10 m the light is exactly zero, with no ring. The spot rows show the cone: full strength up to 20 degrees, 0.2990 at 25 degrees and zero from 30 degrees on.

The real code does the same work, with vectors, with bounds for culling and with a log that tells the GPU what changed.

## The real code

### The falloff and the cone in the shader

The shader has the two functions in one place. Check the order of the steps: the window, then the division.

```slang src="Strata/shaders/Include/PBR.slang#L194-L207"
// Smooth distance falloff for punctual lights: inverse square, windowed to reach zero at the range.
float DistanceAttenuation(float distanceSquared, float inverseRangeSquared)
{
	float ratio = distanceSquared * inverseRangeSquared;
	float window = clamp(1.0 - ratio * ratio, 0.0, 1.0);
	return window * window / max(distanceSquared, 1e-4);
}

float SpotAttenuation(float3 lightToSurface, float3 spotDirection, float cosInner, float cosOuter)
{
	float cd = dot(normalize(lightToSurface), spotDirection);
	float t = clamp((cd - cosOuter) / max(cosInner - cosOuter, 1e-4), 0.0, 1.0);
	return t * t;
}
```

1. **Line 197:** `ratio` is the squared distance over the squared range, which is $(d/r)^2$.
2. **Line 198:** squaring the ratio again gives $(d/r)^4$, and `clamp` makes the window zero beyond the range.
3. **Line 199:** the window is squared and divided by the squared distance, with a floor of 0.0001 so that a surface on the lamp does not divide by zero.
4. **Lines 204–206:** `cd` is the cosine of the angle off the axis, `t` is its position between the two cosines and the result is `t` squared.

Here are the two formulas as the shader computes them. The falloff factor $A$ multiplies the light's color times its intensity.

$$A(d) = \frac{w(d)^2}{d^2}, \qquad w(d) = 1 - \left(\frac{d}{r}\right)^4$$

$A$ is the factor in units of one per square meter, and $d$ is the distance from the light to the surface in meters. $r$ is the range in meters, and $w$ is the window, a number from 1 down to 0. The shader sets $w$ to zero for $d \ge r$. At the limits: for $d$ much smaller than $r$ the window is near 1 and $A$ is the physical $1/d^2$; at $d = r$ the window is 0 and so is $A$.

$$f = t^2, \qquad t = \frac{\cos\theta - \cos\theta_o}{\cos\theta_i - \cos\theta_o}$$

$f$ is the cone factor, a number from 0 to 1. $\theta$ is the angle in degrees between the spot's axis and the direction to the surface, $\theta_i$ is the inner cone angle and $\theta_o$ is the outer cone angle. $t$ is clamped to the range 0 to 1 before it is squared. At $\theta \le \theta_i$ the cosine is at least $\cos\theta_i$ and $t$ is 1; at $\theta \ge \theta_o$ the cosine is at most $\cos\theta_o$ and $t$ is 0.

:::example[A spot light at 25 degrees]
Take the defaults of the spot light: inner 20 degrees, outer 30 degrees. The cosines are $\cos 20^\circ = 0.9397$ and $\cos 30^\circ = 0.8660$, and their difference is 0.0737. A surface 25 degrees off the axis has $\cos 25^\circ = 0.9063$. Then $t = (0.9063 - 0.8660) / 0.0737 = 0.547$ and $f = 0.547^2 = 0.299$.

The surface gets about 30 % of the full cone's light, and not 50 %, because the square makes the edge ease in. At 10 degrees $t$ is above 1 and clamps to 1; at 35 degrees $t$ is below 0 and clamps to 0.
:::

Why use $t^2$ and not $t$? A straight fade from full to nothing has a visible corner at the outer edge, where the brightness changes its slope at once. The square makes the slope zero at the edge, so the rim of a spot looks like a soft shadow and not a drawn line. The cost is that the fade is not physical: no real lamp follows this curve. The cosines cost nothing, because the shader already has the dot product.

### Making a record

The function below builds a record from the world matrix and the component's values. Note the three checks at the top, how the direction comes from the matrix and where the two bounds are chosen.

```cpp src="Strata/src/Strata/Renderer/RenderLights.cpp#L69-L97"
RenderData::LightRecord RenderLights::MakeRecord(const glm::mat4& world, bool active, const glm::vec3& color, float intensity, float range, uint32_t type,
	float innerDegrees, float outerDegrees, float sourceRadius)
{
	RenderData::LightRecord record;
	if (!active || !(intensity > 0.0f) || !(range > 0.0f) || !std::isfinite(intensity) || !std::isfinite(range) || !IsFiniteMatrix(world)
		|| !std::isfinite(color.r) || !std::isfinite(color.g) || !std::isfinite(color.b))
		return record; // Not drawn
	const glm::vec3 position = glm::vec3(world[3]);
	glm::vec3 direction = glm::vec3(world * glm::vec4(0.0f, 0.0f, -1.0f, 0.0f));
	const float length = glm::length(direction);
	direction = length > 1e-6f ? direction / length : glm::vec3(0.0f, 0.0f, -1.0f);
	float inner = 0.0f;
	float outer = 0.0f;
	if (type == RenderData::c_LightSpot)
	{
		outer = std::clamp(outerDegrees, 0.1f, 89.9f);
		inner = std::clamp(innerDegrees, 0.0f, outer);
	}
	const float cosInner = std::cos(glm::radians(inner));
	const float cosOuter = std::cos(glm::radians(outer));
	record.PositionRange = glm::vec4(position, range);
	record.Color = glm::vec4(color * intensity, 1.0f / (range * range));
	record.DirectionType = glm::vec4(direction, static_cast<float>(type));
	record.SpotAngles = glm::vec4(cosInner, cosOuter, RenderData::c_LightRecordDrawn, 0.0f);
	record.Bounds = type == RenderData::c_LightSpot ? GetSpotBounds(position, direction, range, cosOuter, std::sin(glm::radians(outer)))
		: glm::vec4(position, range);
	record.Source = glm::vec4(std::isfinite(sourceRadius) ? std::clamp(sourceRadius, 0.0f, PointLightComponent::c_MaxSourceRadius) : 0.0f, 0.0f, 0.0f, 0.0f);
	return record;
}
```

1. **Lines 73–75:** an inactive light, or any value that is zero, negative or not finite, returns a default record, and a default record is not drawn.
2. **Lines 77–79:** the direction is the entity's -Z axis in :term[world space]{id=world-space}, :term[normalized]{id=normalization}, with -Z as the fallback for a degenerate matrix.
3. **Lines 82–86:** only a spot light has angles. The outer angle is clamped to 0.1 to 89.9 degrees and the inner angle to between 0 and the outer angle, so the cone is never flat and never a half space.
4. **Line 90:** the color is stored already multiplied by the intensity, and the fourth number is one over the range squared, as in the toy.
5. **Lines 93–94:** a point light is bounded by a sphere of its range; a spot light by the sphere that the next function finds.

The bound of a spot light has two cases. The renderer wants the smallest sphere around the cone's lit region, so that the culling of the light is tight.

```cpp src="Strata/src/Strata/Renderer/RenderLights.cpp#L57-L67"
glm::vec4 RenderLights::GetSpotBounds(const glm::vec3& position, const glm::vec3& direction, float range, float cosOuter, float sinOuter)
{
	if (cosOuter >= 0.70710678f)
	{
		// Up to 45 degrees the apex and the rim of the spherical cap lie on the bounding sphere.
		const float radius = range / (2.0f * cosOuter);
		return glm::vec4(position + direction * radius, radius);
	}
	// Wider cones are bounded by the sphere through the rim of the cap.
	return glm::vec4(position + direction * (range * cosOuter), range * sinOuter);
}
```

1. **Line 61:** up to 45 degrees the tip and the rim of the cone's cap lie on one sphere whose center is on the axis.
2. **Line 62:** that sphere has a radius of the range over twice the cosine of the outer angle.
3. **Line 66:** for wider cones the sphere through the rim, centered at the cap's middle, is smaller.

:::derivation
Put the tip at the origin, the axis along $x$, and let the range be $R$ and the outer angle $\theta$. The rim of the cap is at $(R\cos\theta, R\sin\theta)$. A sphere centered at $(c, 0)$ that passes through the tip has radius $c$. It passes through the rim when $c^2 = (R\cos\theta - c)^2 + R^2\sin^2\theta$, which gives $c = R / (2\cos\theta)$. That is the first case.

For $\theta$ above 45 degrees this center lies beyond the cap's middle at $R\cos\theta$, and the sphere around the cap's middle with radius $R\sin\theta$ is smaller, and still holds the tip because $\cos\theta < \sin\theta$ there. At exactly 45 degrees both give a center and a radius of $R/\sqrt{2}$, so the bound is continuous.
:::

A spot light of range 15 m and an outer angle of 30 degrees has $\cos 30^\circ = 0.866$, so its bound is a sphere of radius $15 / 1.732 = 8.66$ m centered 8.66 m along the axis. With an outer angle of 60 degrees the cosine is 0.5, and the bound has a center 7.5 m along the axis and a radius $15 \times 0.866 = 12.99$ m. The first sphere would have had a radius of 15 m, so the second case is tighter.

A rectangle light gets its record from `MakeAreaRecord`, with type 2, `c_LightRect`. The position is the face's center, the color is the luminance times the color and the direction is the face's normal. The bound is a sphere around the center whose radius is the range plus half the face's diagonal. The last two vectors hold the face's axes and half sizes, and they stay zero in point and spot records.

### Keeping records current

Records are not rebuilt every frame. `RenderLights` connects to the registry's signals (the notifications EnTT sends when a component is added, changed or removed) and builds a record only for a light that changed.

The connected signals queue a light for the next sync, except the destroy signal, which frees the record at once. The reason is that the entity and its index can be used again before the next sync. The sync then does the work.

```cpp src="Strata/src/Strata/Renderer/RenderLights.cpp#L331-L368"
uint32_t RenderLights::Sync(const Scene& scene, std::span<const entt::entity> transformChanges, bool allTransforms, bool drawnChanged)
{
	uint32_t updated = 0;
	for (const QueuedLight& queued : m_Queued)
	{
		m_QueuedKeys[GetKey(queued.Entity, queued.Type)] = 0;
		updated += UpdateRecord(scene, queued.Entity, queued.Type) ? 1u : 0u;
	}
	m_Queued.clear();
	if (m_Count == 0)
		return updated;
	if (allTransforms)
	{
		for (uint32_t index = 0; index < m_Entities.size(); index++)
		{
			if (m_Entities[index] != entt::null)
				updated += UpdateRecord(scene, m_Entities[index], m_Types[index]) ? 1u : 0u;
		}
		return updated;
	}
	const auto updateLights = [&](entt::entity entity)
	{
		for (uint32_t type = 0; type < c_LightTypes; type++)
		{
			if (Find(entity, type) != c_InvalidIndex)
				updated += UpdateRecord(scene, entity, type) ? 1u : 0u;
		}
	};
	for (const entt::entity entity : transformChanges)
		updateLights(entity);
	// A light riding what the fixed steps move is drawn with it on every frame, also on frames without a step.
	if (drawnChanged)
	{
		for (const entt::entity entity : scene.GetInterpolatedEntities())
			updateLights(entity);
	}
	return updated;
}
```

1. **Lines 334–338:** each queued light gets its record built again; the queue is then emptied.
2. **Lines 342–350:** when every transform changed, all records are built again.
3. **Lines 359–360:** otherwise only the lights on entities whose transforms changed are updated.
4. **Lines 362–366:** a light on a moving fixed-step entity is placed again at its drawn transform on every frame, also on a frame without a step.

Building a record again does not always change it. When the new record equals the old one byte for byte, and so do the shadow settings, the update returns without a log entry. This keeps a transform change that moves nothing visible from reaching the GPU.

Each real change is logged. The log is a list of pairs: a version number and a record index. A reader of the log, here the GPU copy, remembers the version it last saw and asks for the records changed since. When the reader is too far behind, the answer is "read everything". The log keeps 65,536 changes at most.

A freed record index goes to a list, and the next new light takes it. That keeps the array dense and the GPU copy small. The [render scene](../draw/render-scene.md) page teaches the same pattern for proxies in full.

### The sun and the frame constants

The sun is different. There are few suns and the choice depends on all of them, so the renderer does not keep records for them. It searches the directional lights once per frame.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L2686-L2692"
auto useDirectionalLight = [&](const DirectionalLightComponent& light, const glm::vec3& direction)
{
	frame.DirectionalLightDirection = glm::vec4(direction, 1.0f);
	frame.DirectionalLightColor = glm::vec4(light.Color * light.Intensity, 1.0f);
	// Its highlight takes the disk's size, with or without shadows.
	frame.ReflectionParams.w = RenderData::GetSunLobeAlpha2(light.ShadowSoftness);
	m_SunColor = light.Color;
```

The :term[lambda]{id=lambda} above writes the chosen light into the frame constants. It stores the direction, with a one in the last place to say that a sun exists, the color times the intensity and the size of its disk, which sets the width of its highlight. That size is `ShadowSoftness`, the **Angular Diameter**: the stored name stayed when 0.8.0 made it size the highlight too. The loop that calls the lambda comes next.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L2704-L2719"
float brightest = -1.0f;
for (auto [entity, light, world] : registry.view<DirectionalLightComponent, WorldTransformComponent>().each())
{
	if (!world.ActiveInHierarchy || light.Intensity <= brightest)
		continue;
	// Lights shine along their entity's -Z axis.
	const glm::vec3 direction = glm::vec3(world.Matrix * glm::vec4(0.0f, 0.0f, -1.0f, 0.0f));
	const float length = glm::length(direction);
	if (!(length > 1e-6f))
		continue;
	brightest = light.Intensity;
	useDirectionalLight(light, direction / length);
}
// The preview sun is a default directional light (with shadows). The preview sky's disk follows it, like any sun.
if (preview)
	useDirectionalLight(DirectionalLightComponent(), -GetPreviewSunDirection());
```

1. **Line 2707:** a light that is inactive in the hierarchy, or not brighter than the best so far, is skipped. A tie keeps the first.
2. **Line 2710:** the direction is the world matrix applied to -Z. The sun reads the world matrix, not a drawn transform.
3. **Line 2714:** each brighter light replaces the earlier winner, so the last assignment is the brightest.
4. **Lines 2718–2719:** in an editor view of a scene without lights, a default directional light takes over, aimed along the preview direction.

Before the loop the constants hold a sun of zero color. A scene with no active directional light thus has no sun, and the sky and the point and spot lights alone light it. The sky has the same rule as the sun: the loop for the sky light takes the first active one and stops ([sky](../light/sky.md)).

The sun reads its components every frame, so a write to a `DirectionalLightComponent` field needs no signal. A write to a point or spot field does.

### From record to `LightData`

The renderer selects the records, in its own code or in a compute shader on the GPU, and writes the survivors into a second array of smaller structures, which the shader reads. The record keeps world positions in full; the shader's structure holds camera-relative ones. The renderer subtracts the camera's position in double precision before it gives the positions to the shader ([camera-relative space](../draw/mirrors-camera-relative.md)).

```cpp src="Strata/src/Strata/Renderer/SceneRenderData.h#L264-L273"
struct LightData
{
	glm::vec4 PositionRange; // xyz: camera-relative world position (as uploaded), w: range
	glm::vec4 Color;         // rgb: color * intensity, w: 1 / range^2
	glm::vec4 DirectionType; // xyz: direction the light travels, w: type
	// x: cos(inner), y: cos(outer), z: its shadow slot plus one (0: no shadow; LocalShadowData), w: the source radius in
	// meters (highlights only: LightRecord::Source.x)
	glm::vec4 SpotAngles;
};
static_assert(sizeof(LightData) == 64);
```

1. **Line 266:** the position is camera-relative, and the fourth number is the range, which the shader tests first.
2. **Lines 269–271:** the shadow slot plus one and the source radius share the last vector; the record kept them in separate places.
3. **Line 273:** the structure is 64 bytes, a size that the GPU side mirrors by hand in `Strata/shaders/Include/Scene.slang`.

A rectangle light fills the same structure with its face's center, its luminance and its normal. The axes of its face go to a second array of `LightShape` structures, 48 bytes each, at the same index, and point and spot lights leave theirs zero.

The view is cut into clusters, cells that each list the lights that can reach them ([many lights](../light/many-lights.md) teaches them and the selection of lights). In the forward shader the loop over the lights of a pixel's cluster treats each light in turn. It skips the light when the squared distance is at least the squared range. It multiplies the falloff, then the cone factor for a spot, then the shadow when the slot is not zero. It adds the light's contribution through the shading function of the [surface shading](../light/brdf.md) page.

### Preview lighting

A new scene has no lights, and a scene without lights would be black in the editor. **Preview lighting** is the sun and the sky that an editor view gives a scene that has no light of its own, so that you can see what you build.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L180-L187"
bool SceneRenderer::NeedsPreviewLighting(Scene& scene)
{
	// Any light means the scene is lit the way it is meant to be, a night scene lit by a torch as well as a day, a room lit
	// by its ceiling panels too.
	return !HasActiveComponent<DirectionalLightComponent>(scene) && !HasActiveComponent<SkyLightComponent>(scene)
		&& !HasActiveComponent<PointLightComponent>(scene) && !HasActiveComponent<SpotLightComponent>(scene)
		&& !HasActiveComponent<RectLightComponent>(scene);
}
```

Any active light of any of the five kinds turns the preview off, so a night scene lit by one torch, or a room lit by its ceiling panels, shows as it is. The preview sun is a default directional light, 55 degrees above the horizon, that casts shadows, and the preview sky is the default procedural sky. The renderer applies both only when the view asks. The editor's Scene view asks when its setting for preview lighting is on, which is the default, and the Game view and a played game never ask. An empty room in the Scene view is lit, and the same room in the Game view is black, because the Game view shows what a player sees.

### Imported lights

The model :term[importer]{id=importer} reads the glTF extension for lights (`KHR_lights_punctual`) one to one: its candela and lux become the components' intensity without a conversion. A glTF light may come without a range. Then Strata chooses the distance at which the plain inverse-square law gives 1 % of a unit intensity: $I / d^2 = 0.01$ gives $d = 10\sqrt{I}$ meters. A lamp of 4 candela gets 20 m, and a light without a range gets at least 0.1 m.

A range that glTF gives scales with the model's import scale. Spot cones are clamped to between 1 and 89 degrees, and the inner angle to between 0 and the outer one. The `ImportLights` setting belongs to [glTF models](../assets/models-gltf.md); the [lamps](../make/lamps.md) page shows how to place lamps in a game.

## What Strata does not do

Every light lights every surface inside its range, and Strata has no light cookies, which are projected textures. It has no profiles of the Illuminating Engineering Society (IES), which are the measured light patterns of real lamps. It has no light linking and no lighting channels, so you cannot make a light skip one object or reach one layer only. The reason is cost and simplicity: a mask per light multiplies the cases that the culling and the clusters must handle. If a game needs a lamp that lights only one room, the lamp's range and the walls' shadows do that job.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Constant, linear and :term[quadratic]{id=quadratic-equation} attenuation | Fixed-function graphics interfaces of the past | Three knobs that artists know | Physical units, and a bound for culling |
| Inverse square with a hard cutoff | Simple renderers | The exact physical law inside the range | A visible ring at the cutoff |
| Karis's window with one added to the squared distance | Unreal Engine 4 | A finite brightness at the lamp itself | The exact inverse square close to the lamp |
| One pass per light | Early forward renderers | The simplest shader | Drawing the scene again for every light |
| Several shadowed suns | Engines that support more than one | Two or more suns, as on a binary star | A cascade set per sun, and a larger frame constants block |
| Light cookies, IES profiles, light linking | Many production engines | Patterned lights, and lights that skip objects | A mask or a texture per light in every pass |

## How it is tested

The records are tested on the :term[central processing unit]{id=processor} (CPU) with no GPU. The suite `Renderer.RenderScene` tests point, spot and rectangle lights as records. It checks the positions, the bounds, the "drawn" flag and the log of changes. It also checks an entity with both lights, destroyed entities, copied scenes and the `Validate` check that names a write made without a signal. A second test checks the source radius, and a third the placement of lights at their drawn transforms on frames without a step.

The suite `Renderer.AreaLights` checks the rectangle light's mathematics on the CPU, and `GPU.SceneRenderer.AreaLights` renders it.

The shading is tested on the GPU. The suite `GPU.SceneRenderer.Lighting` renders a floor under a spot light and compares the light at angles off the axis. Inside the inner cone only distance and incidence change the light, and between the angles the factor is about 0.3 at 25 degrees. Outside the outer cone nothing arrives. Other cases check that point lights light nearby surfaces and that one scene at 65,536 lux and exposure -16 renders like a 1 lux scene at exposure 0.

To run them, use the commands of the engine's build: the `RenderScene` tests run on any machine, and the `GPU` suites need a graphics device and carry the label `gpu`.

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=Renderer.RenderScene
build/windows/bin/Debug/StrataTests.exe --test-suite=GPU.SceneRenderer.Lighting
```

Run both commands in the engine's folder after a build. Each prints the number of passed test cases. The command `ctest --preset windows-debug -L gpu` runs every GPU suite at once.

## Changing it safely

A new light type, such as a disk or a tube, reaches four places, as the rectangle light did in 0.8.0. They are its component and registration, the record (`MakeRecord` and the signals), `LightData` and the clusters, and the shading function that the forward shader calls for each light. A change in only one of them gives a light that exists in the editor and does not shine.

- **Change both copies of a layout.** Static assertions hold `LightRecord` at 128 bytes and `LightData` at 64, and the shaders mirror both by hand: `LightRecord` in `Strata/shaders/Include/Lights.slang`, `LightData` in `Strata/shaders/Include/Scene.slang`. When you add a field, add it to both sides and change the assertion, or one side reads garbage.
- **Signal your writes.** The rule above: a direct write to a light field needs `registry.patch` or `MarkModified`.
- **Keep the sun's choice in one place.** Any code that wants "the sun" should use the frame constants, not search the scene again, or two places will disagree after a tie.
- **Keep records comparable.** `RecordsEqual` compares whole records byte by byte, so a field you add takes part in the check at once; give it a defined value in every record.
- **The checks to pass.** `Renderer.RenderScene` on the CPU, `GPU.SceneRenderer.Lighting` and the feature test project, which must use a new component or property.

:::rule
Every new component or engine feature must be used by the feature test project (`StrataTests/FeatureTest/`). The reason is that an unused property cannot be shown to work.
:::

## Summary

- A point light's brightness at a distance is its intensity times a windowed inverse-square factor that falls to exactly zero at its range.
- A spot light's cone factor is the square of a clamped position between the cosines of its outer and inner half angles.
- Only the brightest active directional light shines, and a scene with none has no sun; an editor view of a scene without lights gets a preview sun.
- A point, spot or rectangle light is a 128-byte record kept from signals and transform changes; a change log lets the GPU copy read only what changed.
- A direct write to a point or spot light field must signal, because records are built from signals and not from scans.

## Check yourself

1. A point light has 40 candela and a range of 20 m. What are its factor $A$ and its lux at a surface 10 m away?

   :::answer{tests="falloff"}
   The ratio $(d/r)^2$ is $100/400 = 0.25$, and its square is 0.0625. The window is $1 - 0.0625 = 0.9375$, and its square is 0.8789. Dividing by $d^2 = 100$ gives $A = 0.00879$, and times 40 candela the light is 0.352 lux. The plain law would give 0.4 lux, so the window dims the light by about 12 %.
   :::

2. A spot light has an inner angle of 0 degrees and an outer angle of 60 degrees. A surface lies 45 degrees off the axis. What is the cone factor to two places: 0.17, 0.25, 0.41 or 1?

   :::answer{tests="cone"}
   The answer is 0.17. Here $\cos 45^\circ = 0.7071$, $\cos 60^\circ = 0.5$ and $\cos 0^\circ = 1$, so $t = 0.2071 / 0.5 = 0.414$ and $f = 0.414^2 = 0.17$. The value 0.25 is a straight fade in the angle (45 of 60 degrees off, so a quarter left), which the shader does not use. The value 0.41 forgets the square, and 1 would hold only inside the inner angle.
   :::

3. A scene has three active directional lights with intensities 3, 5 and 5, in that order in the registry, and no other light. Which one shines, and what does the frame hold if all three are disabled?

   :::answer{tests="one-sun"}
   The second light shines: it is the first with the highest intensity, and the third is not brighter than it, so a tie keeps the earlier one. If all three are disabled the frame holds a sun of zero color, a direction straight down and a zero in the fourth place, and the scene has no sun. In an editor view the preview sun then replaces it, because no light of any kind is active.
   :::

4. Which step makes a changed `Intensity` of a point light reach the GPU copy: the component's `on_update` signal, a scan of every light each frame, or the shader reading the component?

   :::answer{tests="record-path,signal-rule"}
   The signal. `OnLightChanged` queues the entity, `Sync` builds the record again with `MakeRecord`, and a changed record is logged so that the GPU copy reads it. A scan each frame would cost time for every light, and the shader never sees components. A write made without a signal is never queued, so the record keeps its old value until something else touches the light.
   :::

5. In the Scene view a new empty scene is lit. In the Game view the same scene is black. Why?

   :::answer{tests="one-sun"}
   The Scene view is an editor view with preview lighting on, and a scene with no active light gets a preview sun and the default sky. The Game view shows what a player sees and never adds a preview, so the scene stays dark until it has a light.
   :::

## Exercises

1. **Basic.** A lamp of 6 candela has a range of 12 m. Compute the window and the lux at 6 m, and at 11 m.

   :::answer[Worked solution]{tests="falloff"}
   At 6 m: the ratio is $36/144 = 0.25$, the window is $1 - 0.0625 = 0.9375$, its square is 0.8789, the factor is $0.8789 / 36 = 0.02441$ and the light is $6 \times 0.02441 = 0.146$ lux. At 11 m: the ratio is $121/144 = 0.8403$, its square 0.7061, the window 0.2939 and its square 0.0864; the factor is $0.0864/121 = 0.000714$ and the light is 0.0043 lux. Near the range the light is almost zero.
   :::

2. **Medium.** A designer asks for a spot light of 800 :term[lumens]{id=lumen} whose cone has a half angle of 30 degrees. Write a function that turns lumens and a half angle into candela, and a unit test with three checks.

   :::answer[Worked solution]{tests="cone" solution="sketches/light-lights-lumens.cpp"}
   The cone's :term[solid angle]{id=solid-angle} is $2\pi(1 - \cos\theta)$ :term[steradians]{id=steradian}, and the candela are the lumens divided by it. For 30 degrees the solid angle is 0.8418 steradians, so 800 lumens give about 950 candela. The helper assumes an even cone; a Strata spot fades between its two angles, so the helper is a starting point and a designer adjusts by eye. The test checks a hemisphere (a half angle of 90 degrees gives $2\pi$ steradians), the 800-lumen case and the ratio between two cones.

   ```cpp sketch="light-lights-lumens.cpp"
   #include <cmath>
   #include <cstdio>

   namespace
   {

   	constexpr float c_Pi = 3.14159265f;

   	// Candela for a spot light of the given lumens whose light fills a cone of the given half angle evenly.
   	float SpotCandelaFromLumens(float lumens, float halfAngleDegrees)
   	{
   		const float solidAngle = 2.0f * c_Pi * (1.0f - std::cos(halfAngleDegrees * c_Pi / 180.0f));
   		return lumens / solidAngle;
   	}

   	int s_Failures = 0;

   	void Expect(const char* name, float actual, float expected, float tolerance)
   	{
   		const bool ok = std::fabs(actual - expected) <= tolerance;
   		std::printf("%s: %.2f cd (expected %.2f) %s\n", name, actual, expected, ok ? "ok" : "FAILED");
   		if (!ok)
   			s_Failures++;
   	}

   }

   int main()
   {
   	// A half angle of 90 degrees is a hemisphere: 2 pi steradians.
   	Expect("hemisphere", SpotCandelaFromLumens(628.3185f, 90.0f), 100.0f, 0.01f);
   	// 800 lumens in a cone of 30 degrees half angle.
   	Expect("narrow cone", SpotCandelaFromLumens(800.0f, 30.0f), 950.3f, 0.5f);
   	// Halving the half angle of a narrow cone roughly quadruples the candela.
   	Expect("ratio", SpotCandelaFromLumens(800.0f, 15.0f) / SpotCandelaFromLumens(800.0f, 30.0f), 3.93f, 0.01f);
   	return s_Failures;
   }
   ```

   ```text output-of="light-lights-lumens.cpp"
   hemisphere: 100.00 cd (expected 100.00) ok
   narrow cone: 950.36 cd (expected 950.30) ok
   ratio: 3.93 cd (expected 3.93) ok
   ```

   1. **Line 12:** a cone of half angle $\theta$ spans $2\pi(1 - \cos\theta)$ steradians.
   2. **Line 13:** the candela are the lumens divided by that solid angle.
   3. **Line 31:** a half angle of 90 degrees must give a hemisphere, $2\pi$ steradians, which checks the formula at a limit.
   4. **Lines 33–35:** the second check is the 800-lumen case and the third the ratio of two cones.
   :::

3. **Hard.** Trace it yourself: a point light's `Intensity` is changed with the `component.set` command. Find where the change becomes a record that the GPU copy reads.

   :::answer[Worked solution]{tests="record-path,signal-rule"}
   Start the editor under a debugger and put a breakpoint in `RenderLights::OnLightChanged` in `Strata/src/Strata/Renderer/RenderLights.cpp`. The command writes the field and signals it: the component registry's `MarkModified` calls `registry.patch`, which sends `on_update`, and `Connect` has registered `OnLightChanged` for it. It calls `Queue`, which adds the entity once.

   A second breakpoint in `RenderLights::Sync` shows the queue; `UpdateRecord` calls `ComputeRecord`, and that calls `MakeRecord`, which multiplies the color by the new intensity. A third breakpoint in `RenderLights::LogChange` shows the new version. The GPU copy then calls `GetChanges` with its last version and receives the record's index.
   :::

## Where it lives in Strata

- Components: `Strata/src/Strata/Renderer/RendererComponents.h` and its registration in `RendererComponents.cpp`.
- Records, signals and the log: `Strata/src/Strata/Renderer/RenderLights.cpp`, with the layouts in `SceneRenderData.h`; a rectangle's face in `AreaLights.cpp`.
- The sun, the preview and the frame constants: `SceneRenderer::CollectLights` and `NeedsPreviewLighting`.
- The falloff and the cone: `DistanceAttenuation` and `SpotAttenuation` in `Strata/shaders/Include/PBR.slang`; the loop in `Strata/shaders/Scene/Forward.frag.slang`.
- Import: `Strata/src/Strata/Asset/GltfImporter.cpp`.
- Tests: `Renderer.RenderScene` (`StrataTests/src/Renderer/RenderSceneTests.cpp`), `GPU.SceneRenderer.Lighting` (`GPUSceneLightingTests.cpp`) and, for rectangle lights, `Renderer.AreaLights` (`AreaLightsTests.cpp`).
- Command: `component.set` changes any light field from outside the editor.

## Further reading

- Brian Karis, "Real Shading in Unreal Engine 4", SIGGRAPH 2013 course notes (intermediate): the windowed falloff and the reasoning behind a bound for every light.
- The glTF extension `KHR_lights_punctual` specification, from the Khronos Group (beginner): the units and cone rules that the importer follows.
