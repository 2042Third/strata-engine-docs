---
id: light/units-exposure
title: "Light by the numbers: radiometric and photometric units"
description: "What a light's number means: power, intensity, illuminance and luminance, their photometric twins, and why Strata keeps real units and a pre-exposure."
kind: concept
size: L
tracks: [E]
needs: [gpu/frame-tour, basics/numbers, basics/color, basics/math-sphere]
time: 60
learn:
  - id: convert-units
    text: compute the candela, lux and nits that a lamp of a given lumens makes, for a point light, a spot light and a diffuse surface
  - id: read-fields
    text: name the unit of every light field, of the sky and of emission in Strata, and say what Strata never changes by a factor
  - id: why-real-units
    text: explain why Strata keeps one scale of real units and why a frame lit by the sun needs a pre-exposure
  - id: night-scene
    text: compute the lux a lamp makes at a distance and the manual exposure that shows a night scene
status: final
since: 0.6.0
---

Make one scene, switch its sky light off, and light it twice with the sun alone. The first time the sun has an intensity of 65,536, and the camera exposure is -16. The second time the sun has an intensity of 1, and the exposure is 0. The two pictures come out the same, down to the last bit.

::compare{id=equal-pair}

Nothing is wrong. The first sun is 65,536 times stronger, and the first exposure is 65,536 times weaker, because each step of exposure halves or doubles the light that reaches the picture. The two changes cancel.

So a light's number says nothing alone: it means something only together with its unit, and with the exposure that turns the light into a picture. This page teaches the units. It builds the four numbers that describe light, then shows the one choice Strata made: every light has a real unit, and nothing changes it by a hidden factor.

## A bigger number does not say how much light

A beginner's lighting tool gives a light an "intensity" slider. Set it to 5 and the lamp is bright; set it to 10 and it is brighter. That works while you have one lamp and one scene. It stops working at the first question you cannot answer by looking.

Suppose you copy a lamp from one scene to another. Is a 5 in the second scene the same lamp? Suppose a friend gives you a model of a street lamp with a light of intensity 800. Is that a small lamp or a stadium light? How many candles make a sun?

A slider with no unit has no answer to these questions. Each tool then picks its own scale, and every scene is tuned by eye. The scene cannot move, and a number you read from a lamp's box means nothing. The way out is the one that physics took long ago: name the quantity, name its unit, and tie the unit to something you can measure.

## Radiometry measures light as energy

Light carries energy. A lamp sends out energy every second, and that rate is power, measured in watts (W). One watt is one joule of energy per second. The power a source sends out in all directions is its flux, also written $\Phi$. This is the first of four quantities.

Flux alone does not tell you how bright a surface looks, because it says nothing about where the energy goes. A 100 W source in a closed room and the same source on a mountain top have the same flux and light very different things. You need to divide the flux by something. There are two things to divide by, and each gives two quantities.

The first thing is a direction, measured as a :term[solid angle]{id=solid-angle}. Recall from the page on directions on a sphere that a solid angle counts how large a cone of directions is, in :term[steradians]{id=steradian}, and that a whole sphere is $4\pi$ steradians. The second thing is an area, in square meters. The four quantities follow:

- Flux is energy per second, in watts. It has no "per".
- Intensity is flux per solid angle, in watts per steradian: how much one source sends in one direction.
- Irradiance is flux per area, in watts per square meter: how much light arrives on a surface.
- Radiance is flux per area per solid angle, in watts per square meter per steradian: how much light travels along one ray.

:::example[A 100 W source, step by step]
Take a source that sends 100 W evenly in every direction. Its flux is $\Phi = 100$ W. A sphere has a solid angle of $4\pi \approx 12.57$ steradians, so each steradian carries $100 / 12.57 = 7.96$ W. That is the intensity: 7.96 `W/sr`.

Now stand 2 m away and hold up a flat card that faces the source. The source's light spreads over a sphere of radius 2 m, which has an area of $4\pi \times 2^2 = 50.3$ m². Each square meter gets $100 / 50.3 = 1.99$ W. That is the irradiance on the card: about 2 W/m².

Move to 4 m. The sphere's area grows by 4, so the irradiance falls to 0.5 W/m². Doubling the distance quarters the light. The intensity did not change: the source sends the same 7.96 `W/sr` whoever stands in front of it. The short rule is irradiance = intensity / distance², the inverse-square law.
:::

The two quantities that need a name in the rest of the book are the last two. Both are the ones a :term[renderer]{id=renderer} computes.

**Irradiance** is the light power that arrives on a surface, per square meter of that surface, summed over all the directions it comes from.

**Radiance** is the light power per square meter and per steradian that travels along one ray: what one pixel of a picture receives.

A pixel's color is a radiance: the light that comes along one ray into the camera. An irradiance is what a surface collects from the whole sky above it. The two are tied. A surface adds up the radiance of every direction of the sky, and weights each by the :term[cosine]{id=cosine} of its angle to the :term[surface normal]{id=surface-normal}. Light that arrives at a slant spreads over more surface.

A later page of this part, [the one on reflectance](../light/reflectance.md), uses these two quantities again. Here we only need their names, and the fact that one is "per area" and the other "per area and per direction".

## Photometry weighs light by what the eye sees

Radiometry counts energy, but a game shows light to a person, and the eye does not respond to every color with the same strength. A watt of green light looks much brighter than a watt of deep red or blue light, and a watt of infrared light is invisible. Photometry takes the four radiometric quantities and weighs each color by the eye's response. The weight peaks in green, at a wavelength of 555 nm, where one watt counts as 683 lumens. Elsewhere it falls toward zero.

The result is four twins, one for each radiometric quantity. Each has its own name and unit. They are the numbers on every lamp box, camera and light meter, and the numbers Strata uses.

The first twin is flux:

**Lumen** (lm) is the unit of luminous flux: the power of light, weighted by the eye, that a source sends out in all directions.

The second is intensity:

**Candela** (cd) is the unit of luminous intensity: lumens per steradian, the light a source sends along one direction.

The third is irradiance:

**Lux** (lx) is the unit of illuminance: lumens per square meter, the light that arrives on a surface.

The fourth is radiance:

**Nit** is the unit of :term[luminance]{id=luminance}: candela per square meter, the light that leaves a surface toward the eye, along one ray.

| Radiometric | Unit | Photometric twin | Unit | Per |
| --- | --- | --- | --- | --- |
| Flux | W | Luminous flux (lumen) | lm | nothing |
| Intensity | `W/sr` | Luminous intensity (candela) | cd = `lm/sr` | a direction |
| Irradiance | W/m² | Illuminance (lux) | lx = lm/m² | an area |
| Radiance | `W/(m² sr)` | Luminance (nit) | nit = cd/m² | an area and a direction |

The twins differ from the originals only by the eye's weight. So every rule you learn for one pair holds for the other, with lumens in place of watts. A :term[game engine]{id=game-engine} works in the photometric set, since the images are for human eyes.

```mermaid caption="Light leaves a source as lumens, spreads into candela along directions, lands as lux on a surface and leaves that surface as nits toward the eye." alt="A chain of four boxes joined by arrows. A source with a flux in lumens leads to an intensity in candela along a direction. That leads to an illuminance in lux on a surface. The surface leads to a luminance in nits toward the eye. Each arrow carries the rule that turns one quantity into the next."
flowchart LR
    A["Source: flux in lumens (lm)"] -- "divide by 4 pi for a point light" --> B["Intensity in candela (cd), along a direction"]
    B -- "divide by distance squared, times cosine" --> C["Illuminance in lux (lx), on a surface"]
    C -- "times albedo, divide by pi, for a diffuse surface" --> D["Luminance in nits, off the surface toward the eye"]
```

Read the diagram from left to right. Each arrow is a conversion that the next three sections work with numbers.

## Three conversions that every light follows

### A point light: lumens to candela

A household lamp that sends 800 lm in all directions is a point light. A sphere has $4\pi$ steradians, so the intensity is the flux divided by the solid angle.

$$ I = \frac{\Phi}{4\pi} $$

$I$ is the intensity in candela, and $\Phi$ is the flux in lumens. The fraction bar is read "divided by", and $\pi$ is the number 3.14159. For the lamp, $I = 800 / 12.57 = 63.7$ cd. Strata's documents round it to 64 cd.

At 2 m from the lamp, on a card that faces it, the light is $64 / 2^2 = 16$ lux. At 4 m it is 4 lux. The check at the limits: at a distance of 0 the formula gives infinity, which is why a real lamp has a size and Strata's point light has an optional radius for its highlight. At a very large distance the lux tends to 0.

### A diffuse surface: lux to nits

A white diffuse surface under $E$ lux sends back all the light it receives. It sends it equally in all directions of the hemisphere above it, so the eye sees the same brightness from every side. The light that arrives per square meter is spread over a hemisphere, and weighting the directions by their cosine gives a factor of $\pi$.

$$ L = \frac{\rho E}{\pi} $$

$L$ is the luminance in nits, and $E$ is the illuminance in lux. $\rho$ is the albedo, the share of the light the surface sends back: 1 for ideal white, 0.18 for a middle gray card. The check: a perfect white surface under $\pi$ lux shows exactly 1 nit.

:::derivation
Why the factor is pi.

A surface sends the same luminance $L$ in every direction. Its light adds up over the hemisphere above it, with each direction weighted by the cosine of its angle $\theta$ to the normal. A thin ring of the hemisphere at angle $\theta$ has the solid angle $2\pi \sin\theta \, d\theta$. The sum is the integral of $L \cos\theta \cdot 2\pi \sin\theta \, d\theta$ from 0 to a right angle. The integral of $\cos\theta \sin\theta$ over that range is $1/2$, so the total is $L \cdot 2\pi \cdot 1/2 = \pi L$.

The same factor runs the other way. A uniform sky of $L$ nits lights flat ground with $\pi L$ lux. A white diffuse surface under $E$ lux has a luminance of $E / \pi$. Strata states both rules.
:::

Take the sun on flat ground. A clear sun gives about 100,000 lux. A white surface under it shows $100{,}000 / \pi = 31{,}800$ nits, and a middle gray one with $\rho = 0.18$ shows 5,730 nits. A computer monitor shows 100 to 300 nits. The sun makes the page a hundred times brighter than the screen that shows it, so a camera or an eye must scale the scene, which is what exposure does.

### A spot light: the candela stays on the axis

A spot light sends its light into a cone. A designer then asks: if I keep the lumens and narrow the cone, what happens to the candela? The lumens now fill a smaller solid angle, so each steradian carries more.

$$ I = \frac{\Phi}{2\pi (1 - \cos t)} $$

$t$ is the half angle of the cone, the angle between its axis and its edge. The expression $2\pi(1 - \cos t)$ is the solid angle of the cone, in steradians. For 800 lm in a cone of half angle 30°, the solid angle is $2\pi \times 0.134 = 0.842$ steradians, so $I = 800 / 0.842 = 950$ cd. In a cone of half angle 15° it is $2\pi \times 0.0341 = 0.214$ steradians, and $I = 3{,}740$ cd. The check: a half angle of 180° gives $4\pi$ steradians and the point light's formula.

A real lamp follows that physics. Strata does something else, and the difference matters. A Strata spot light has an **Intensity** in candela *along its axis*, and the engine never spreads it over the cone. A narrower cone cuts away light at the edge, and the light in the middle stays as bright. If you want a lamp of $P$ lumens, you compute the candela with the formula above and type it in.

:::example[A lamp and a spot, with the numbers]
You have a bulb of 800 lm and a torch of 800 lm with a cone of half angle 15°. The bulb is a point light of 64 cd. The torch needs 3,740 cd to keep its lumens. Typed as 64 cd, the torch would be as bright on its axis as the bulb, with a narrow edge: 58 times dimmer than a real torch.
:::

## Reference values tie the numbers to the world

A table of real values lets you check a scene by eye. The values below are the ones Strata's documents use. The last column is the manual exposure that puts a surface of albedo 0.18, lit by the source, at middle gray. A manual exposure of $x$ multiplies every luminance by $2^x$, and the picture shows a value of 0.18 as middle gray, so the exposure for $L$ nits solves $2^x L = 0.18$. The two formulas above then give it: such a surface under $E$ lux has $0.18 E / \pi$ nits, and the exposure $\log_2(0.18 / L)$ simplifies to $\log_2(\pi / E)$.

| Light | Value | Powers of ten | Exposure |
| --- | --- | --- | --- |
| Sun in the sky, from mid-morning to noon | 32,000 to 100,000 lux | 4.5 to 5 | -13 to -15 |
| Blue sky, far from the sun | 3,000 to 8,000 nits, which is 10,000 to 25,000 lux on the ground | 3.5 to 4 | -12 |
| Cloudy day | 1,000 to 10,000 lux, under a sky of 300 to 3,000 nits | 3 to 4 | -8 to -12 |
| Office lighting | 300 to 500 lux | 2.5 to 2.7 | -7 |
| Full moon | 0.1 to 0.3 lux | -1 to -0.5 | +3.5 to +5 |
| A household lamp, 800 lm | 64 cd | 1.8 | none |
| Candle | 1 cd | 0 | none |
| A monitor; a lit sign | 100 to 300 nits; about 1,000 nits | 2 to 3 | none |

The "powers of ten" column is the base-10 :term[logarithm]{id=logarithm} of the value. It shows why the table is a log scale: the sun is a million times stronger than the full moon, and a linear axis would show the moon as zero. Each doubling of the light is one more stop, and one stop is a change of 0.3 in that column. From the moon at +4 to the sun at -14.5, the exposure moves 18 to 19 stops, a factor of about 400,000 to 700,000.

A lamp and a candle have no exposure because their numbers are intensities, not what a surface receives. A surface lit by a lamp gets lux that depends on the distance, as in the worked example of the point light. A 64 cd lamp at 2 m gives 16 lux, so exposure $\log_2(\pi/16) = -2.35$. A 1 cd candle at 0.5 m gives 4 lux, exposure -0.35.

**The sun-to-sky ratio** is the illuminance that the sun makes on flat ground divided by the illuminance that the sky makes on the same ground.

The ratio tells you how dark a shadow is, since a surface in shadow gets the sky's light only. With the sun 40° above the horizon, a 120,000 lux sun gives at most $120{,}000 \times \sin 40° = 77{,}000$ lux on flat ground; the air dims it on the way down. The sky gives 10,000 to 25,000 lux there, so the ratio is 3 to 8. A ratio of 1 means no visible shadows, and a ratio of 8 means a shadow with one eighth of the light.

Strata's Basic 3D template keeps the ratio at five or more. The page on [measuring light](../light/measuring-light.md) gives the way to measure it in a scene.

## Engines choose among four ways to number light

Every engine has to pick what a light's number means. There are four common answers, and each one fixes a flaw of the one before.

1. **Arbitrary intensity.** The number is a factor with no unit. It is the simplest to build and the first thing that happens when a renderer is a hobby. The flaw is the one at the top of the page: nothing ties the number to the world, so scenes, lights and models do not move between tools, and the artist tunes everything by eye.
2. **Radiometric watts.** The number is a power or an irradiance, as in a physics text. Blender, for example, gives point lights in watts and the sun in watts per square meter. The numbers are real, but a watt of light has no link to how bright it looks, and the lamps in a shop are sold in lumens. Artists need a conversion, and the conversion differs for each light's color.
3. **Photometric units.** The number is a lumen, candela, lux or nit, the same numbers as on a lamp box. A real lamp, a real sun and the values of a light meter go in without a conversion. Frostbite, in its 2014 physically based rendering notes, uses these units, as do Unreal's physical lighting units and Filament's documentation. The cost is a very wide range of numbers, and a pipeline that must keep them in range, which is why they come with exposure and with a pre-exposure.
4. **Photometric units and a global scale.** Some engines keep the photometric numbers but multiply every light by one constant, to keep numbers small. The flaw is that the constant is hidden. An imported lamp is wrong by that constant, and a developer who adds a feature must remember it.

| Approach | Cost | Quality | Complexity | Used by |
| --- | --- | --- | --- | --- |
| Arbitrary intensity | Lowest | Looks tuned per scene, no exchange | Lowest | Many older engines and tools |
| Radiometric watts | Low | Real, but not what artists measure | Low | Blender, physics texts |
| Photometric units | A wide range of numbers, needs exposure | Real values and imported lights work | Medium | Frostbite, Unreal, Filament |
| Photometric with a hidden scale | Narrow range | Real until a constant is forgotten | Medium | Engines that grew from a unit-free design |

:::elsewhere[Where these names come from]
The ideas are the ones the photometric engines publish: the 2014 course notes on Frostbite, Unreal's documentation of physical lighting units, and the design document of Filament. The last one gives the conversions between lumen, lux, candela and exposure. The sources stand under further reading, with the Blender manual's description of light power.
:::

## Strata keeps every light in real units, with no factor

Strata takes the third way, without a hidden scale. The comment above its light components, in `Strata/src/Strata/Renderer/RendererComponents.h`, says so in words:

> the shading computes physical quantities on one scale, so a directional light's intensity is illuminance in lux, a point or spot light's luminous intensity in candela and the sky's and emissive surfaces' radiance luminance in nits (cd/m^2). Nothing rescales them: exposure maps them to the display.
> — Strata/src/Strata/Renderer/RendererComponents.h

So you have this table of fields. Every one is a physical quantity.

| Field | Unit | Default |
| --- | --- | --- |
| `DirectionalLightComponent::Intensity` | lux, on a surface that faces the light | 3 |
| `PointLightComponent::Intensity` | candela | 10 |
| `SpotLightComponent::Intensity` | candela, along the axis | 20 |
| `SkyLightComponent::AmbientColor`, and the sky's colors | nits | under 1 |
| `SkyLightComponent::SunIntensity` | nits, the sun's disk, times the sun's color | 20 |
| `EmissiveColor` times `EmissiveIntensity` of a material | nits | 0: black color, intensity 1 |

Each field is times its `Color`, which says what shade the light has and keeps its unit. A glTF file that carries the standard lights extension gives its lights in candela and lux, and the importer reads the lights and the emissive strength 1:1. Nothing changes by a factor, so a scene made before this rule keeps its values.

A test, `Renderer.LightUnits`, in `StrataTests/src/Renderer/LightUnitsTests.cpp`, protects the rule. It checks that the descriptions of the sun, the point and spot lights and the sky name the unit, and so do the tooltips of their intensity fields in the Inspector. The emissive properties of a material must name theirs too. A field on its list cannot lose its unit.

:::why[Why real units with no scale?]
The shading computes photometric quantities on one scale, with no factor between them. So real values and lights imported from glTF work as they are, and exposure alone maps them to the display. The cost is range: a frame lit by the sun holds values that a half float cannot carry. A power-of-two pre-exposure scales them exactly, so nothing is lost. The alternative, a hidden constant, makes every imported light wrong by an unknown factor.
:::

The default values are small on purpose: a 3 lux sun, a 10 cd point light and a sky under 1 nit make a dim scene, which looks about middle gray at exposure 0. A scene may use real values, with an exposure to match. The Basic 3D template does: its sun is 120,000 lux above the air, and its automatic exposure finds the match. The page on [the exposure](../image/exposure.md) teaches the second half, and [the light components](../light/lights.md) give each field's range.

## Half floats cannot hold a frame lit by the sun

The renderer stores the scene's light in a target of half floats. You know from the page on color that a half float holds values up to 65,504, that values below $2^{-14}$ lose bits, and that nothing below $2^{-24}$ survives. Now put real numbers in.

The sun's 100,000 lux on a white surface gives 31,800 nits, which fits, but the bright highlights above it do not. A real sun's disk is far worse. The sun fills a solid angle of about $6.7 \times 10^{-5}$ steradians, and 100,000 lux over that is $1.5 \times 10^9$ nits. Strata uses about 1.3 billion nits for the disk. No half float holds that: it would overflow, and Strata's writers clamp such values at 65,000.

The fix uses exposure's own idea. Every writer of the target multiplies its luminance by a pre-exposure $P$, a power of two chosen near the exposure the frame will get, and the tone mapping divides it out again. With manual exposure of -14.58, $P$ is $2^{-15}$. The white surface of 24,600 nits, under the Basic 3D sun at 40°, becomes $24{,}600 \times 2^{-15} = 0.75$, and the sun's disk becomes 39,700, both in range. Multiplying by a power of two only changes a float's :term[exponent]{id=exponent}, so it is exact: no value gains an error, unless it overflows or drops below the normal range.

```mermaid caption="On a log axis the half float's range runs from 2 to the power minus 24 to 65,504. A sun's disk of 1.3 billion nits lies far above it. After a pre-exposure of 2 to the power minus 15 the disk and the white surface both lie inside, and a dark corner of 1 nit sits near the low end." alt="A flow from values of a scene lit by the sun to stored values. Three values on the left: a disk of 1.3 billion nits, a white surface of 24,600 nits and a dark corner of 1 nit. Each arrow, labeled times 2 to the minus 15, leads to the stored value on the right: 39,700 for the disk, 0.75 for the surface and 0.00003 for the corner. A note says the half float range is 2 to the minus 24 up to 65,504."
flowchart LR
    S["Sun disk: 1,300,000,000 nits"] -- "times 2^-15" --> S2["Stored: 39,700 (fits under 65,504)"]
    W["White surface: 24,600 nits"] -- "times 2^-15" --> W2["Stored: 0.75"]
    D["Dark corner: 1 nit"] -- "times 2^-15" --> D2["Stored: 0.00003 (below 2^-14, fewer bits)"]
```

The diagram shows the point: the pre-exposure slides the whole range down together, so the top fits. The cost is at the bottom, where a dark corner of 1 nit lands below $2^{-14}$ and keeps less precision. It still has 512 steps, which the tone mapping hides. A page of the image part, [on the pre-exposure](../image/pre-exposure.md), gives how Strata chooses $P$ and keeps the image exact. This page only needs the reason: real light is wider than a half float, and a power of two fixes that without changing the picture.

## What this choice cannot do

Real units are not free, and they leave some things undone.

- **Real units need exposure.** A scene lit with real values is black or white until exposure matches it. A 3 lux default sun and a 120,000 lux real sun cannot share one fixed exposure; the first needs about 0 and the second about -15.
- **Real units have a very wide range.** About nineteen stops separate the moon from the sun. Fields and controls must reach both, and a small error in the exponent is a big change in the picture.
- **Real units are not color science.** The units weigh light by one eye response. They do not describe how a camera sensor, a display or a person adapts to a color of light.
- **Range cuts the inverse square.** A point or spot light's light fades to zero at its `Range`, 10 m for a new point light and 15 m for a spot. A lamp meant to reach farther needs a larger `Range`.
- **A lamp's lumens are not stored.** Strata's point and spot lights keep candela along an axis. To keep a lamp's lumens you convert by hand, as in the spot light section.

A light of a rectangular shape, the **Rect Light** of 0.8.0, has units of its own. Its **Units** choose how you give its **Intensity**: as nits, the brightness of the glowing face, or as lumens, the power the whole face sends out. [The area lights page](../light/area-lights.md) teaches both. What Strata omits from the whole subject of light is listed in [what Strata does not do](../appendix/not-in-strata.md).

## Common mistakes

- **Taking lumens for candela.** Symptom: an 800 cd lamp, where a household lamp of 800 lm was meant, is 12 times too strong, and the room looks lit by a stadium light. Fix: divide by $4\pi$ for a point light, and type 64.
- **Expecting a narrower spot cone to brighten the light.** Symptom: you narrow the cone to make a torch stronger, and only the lit circle shrinks. Fix: raise the candela yourself, by the cone formula, when the lumens are what you want to keep.
- **Mixing a default sun with real values.** Symptom: a 3 lux sun beside a 10 cd lamp at 1.8 m looks even, then a real 120,000 lux sun makes the lamp vanish, since it adds only 3 lux to 77,000. Fix: use real values for every light of a scene, and set the exposure from the table.
- **Reading lux as nits.** Symptom: a surface "of 100,000" looks like it should be white at any exposure. Fix: a diffuse surface under $E$ lux shows $E/\pi$ nits, times its albedo.
- **Judging a light by the picture.** Symptom: a sun of 65,536 and a sun of 1 look alike. Fix: read the exposure beside the light, as the opening pictures showed.

## Summary

- A lamp of $P$ lumens is $P/4\pi$ candela as a point light, and $P / (2\pi(1 - \cos t))$ candela in a spot cone of half angle $t$; Strata's spot light keeps the candela on its axis whatever the cone. Candela over distance squared gives lux, and a diffuse surface under $E$ lux shows $\rho E/\pi$ nits.
- Strata gives every intensity a unit: the sun's in lux, the candela of points and spots, nits for the sky, the ambient color and emission, and nits or lumens for a rectangle light. Nothing changes by a factor, glTF lights are read 1:1, and the `Renderer.LightUnits` test checks the names.
- Real units need no hidden factor, and exposure maps them to the display. A frame lit by the sun is wider than a half float, so a power-of-two pre-exposure scales it exactly.
- A mid-gray surface under $E$ lux needs a manual exposure of $\log_2(\pi/E)$, so 16 lux from a lamp at 2 m gives -2.35.

## Check yourself

1. A friend says a 25 W-equivalent bulb of 250 lm hangs 1 m above a desk. Which lux does the desk get under the bulb, to the nearest whole number?

   - A. 250 lux
   - B. 20 lux
   - C. 80 lux

   :::answer{tests="convert-units"}
   B. The bulb is a point light: $250 / 4\pi = 19.9$ cd, and at 1 m the lux is $19.9 / 1^2 \approx 20$. Option A takes lumens for lux, the mistake of forgetting the area and direction. Option C divides by $\pi$ instead of $4\pi$, as for a half sphere.
   :::

2. You narrow a Strata spot light's outer cone from 30° to 15° and leave its Intensity at 20. What changes on a surface on the axis?

   - A. It gets four times the lux.
   - B. It gets the same lux, in a smaller circle.
   - C. It gets half the lux.

   :::answer{tests="read-fields"}
   B. The Intensity is the candela along the axis, and Strata does not spread it over the cone. The cone cuts the edge, and the axis keeps its value. Option A is the real-lamp rule that keeps lumens, which you must apply yourself. Option C has no basis in either rule.
   :::

3. A white diffuse wall shows 50 nits. Which illuminance does it get, and what would a wall of albedo 0.5 need to show 50 nits?

   :::answer{tests="convert-units"}
   For $\rho = 1$, $E = \pi L = 157$ lux. With $\rho = 0.5$ the wall needs twice the light, 314 lux, because $L = \rho E/\pi$ gives $E = \pi L / \rho$.
   :::

4. Why is the sun disk's 1.3 billion nits a problem for a half float, and why is a pre-exposure of $2^{-15}$ exact?

   :::answer{tests="why-real-units"}
   The largest half float is 65,504, far below 1.3 billion. A power of two multiplies only the exponent of a :term[floating point]{id=floating-point-number} number and leaves its digits as they are, so no rounding occurs unless the result overflows or becomes smaller than the normal range. Times $2^{-15}$ the disk becomes about 39,700, which fits.
   :::

5. A 64 cd lamp hangs 4 m from a wall in a dark room. Which lux does the wall get, and which manual exposure shows a mid-gray wall as middle gray?

   :::answer{tests="night-scene"}
   The lux is $64 / 4^2 = 4$. The exposure is $\log_2(\pi/4) = -0.35$. Doubling the distance cuts the light to a quarter, two stops, so the exposure of this wall is two stops higher than at 2 m, where it was -2.35.
   :::

## Exercises

1. **Basic.** A spot light of 1,000 lm with a half angle of 20° should be set in Strata. Which Intensity do you type?

   :::answer[Worked solution]{tests="convert-units"}
   The solid angle is $2\pi(1 - \cos 20°) = 2\pi \times 0.0603 = 0.379$ steradians. The candela is $1000 / 0.379 = 2{,}640$. You type 2,640, and set the cone angles to 20°.
   :::

2. **Medium.** In a yard lit by the moon of 0.2 lux you carry a 64 cd lamp. At which distance does the lamp's light on the ground equal the moon's, and which exposure shows each scene?

   :::answer[Worked solution]{tests="night-scene"}
   Set $64 / d^2 = 0.2$, so $d^2 = 320$ and $d = 17.9$ m. Beyond that distance the moon wins. The exposure that shows a mid-gray surface is $\log_2(\pi/E)$: for the moon, $\log_2(15.7) = 3.97$; for the lamp at 2 m (16 lux), $-2.35$. They differ by 6.3 stops, so an exposure for the moon whites out the lamp's circle. In Strata the lamp's `Range` must exceed 17.9 m for the first answer to hold.
   :::

3. **Hard.** Build a night scene as the engine would. Write a program for three scenes: a 0.2 lux moon, a 64 cd lamp at 2 m and a 1 cd candle at 0.5 m. For each, it prints the lux, the nits of a middle gray surface and the manual exposure. Predict the three exposures first, then run it.

   :::question
   The program uses functions, `std::printf` and a namespace: the basics are in [programming 1](../basics/programming-1.md), [programming 2](../basics/programming-2.md) and [programming 3](../basics/programming-3.md).
   :::

   :::answer[Worked solution]{tests="night-scene" solution="sketches/light-units-exposure-nightscene.cpp"}
   Each scene's lux comes from candela over distance squared, the nits from the diffuse rule and the exposure from the middle-gray rule.

   ```cpp sketch="light-units-exposure-nightscene.cpp"
   #include <cmath>
   #include <cstdio>

   namespace
   {
   	constexpr double c_Pi = 3.14159265358979323846;
   	constexpr double c_MiddleGray = 0.18;

   	// Lux that a source of the given candela makes on a surface that faces it, at the given distance in meters.
   	double LuxFromCandela(double candela, double distance)
   	{
   		return candela / (distance * distance);
   	}

   	// Nits of a matte surface of the given albedo under the given lux.
   	double NitsOfMatte(double albedo, double lux)
   	{
   		return albedo * lux / c_Pi;
   	}

   	// The manual exposure, in stops, that shows the given nits as middle gray.
   	double ExposureFor(double nits)
   	{
   		return std::log2(c_MiddleGray / nits);
   	}

   	void Report(const char* name, double lux)
   	{
   		const double nits = NitsOfMatte(c_MiddleGray, lux);
   		std::printf("%-8s %6.2f lux  %7.4f nits  exposure %6.2f\n", name, lux, nits, ExposureFor(nits));
   	}
   }

   int main()
   {
   	Report("moon", 0.2);
   	Report("lamp", LuxFromCandela(64.0, 2.0));
   	Report("candle", LuxFromCandela(1.0, 0.5));
   	return 0;
   }
   ```

   ```text output-of="light-units-exposure-nightscene.cpp"
   moon       0.20 lux   0.0115 nits  exposure   3.97
   lamp      16.00 lux   0.9167 nits  exposure  -2.35
   candle     4.00 lux   0.2292 nits  exposure  -0.35
   ```

   1. **Line 12:** candela over distance squared is the inverse-square law of the lamp's light.
   2. **Line 18:** the rule for diffuse surfaces, albedo times lux over pi.
   3. **Line 24:** the exposure that moves the surface's nits to 0.18, middle gray.
   4. **Lines 36–38:** the three scenes of the exercise, each one call.

   The moon needs about +4, the lamp -2.35 and the candle -0.35, as predicted by $\log_2(\pi/E)$. The lamp and candle are within two stops of each other, and the moon is six stops darker than the lamp.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Renderer/RendererComponents.h`: the light components, `DirectionalLightComponent`, `PointLightComponent`, `SpotLightComponent` and `SkyLightComponent`, with their units in comments.
- `Strata/src/Strata/Renderer/Material.h`: the emissive color and intensity, in nits.
- `StrataTests/src/Renderer/LightUnitsTests.cpp`: the suite `Renderer.LightUnits`, which checks that every intensity names its unit.
- `SceneRenderer::ChoosePreExposure` in `Strata/src/Strata/Renderer/SceneRenderer.h`: the choice of the pre-exposure.
- The command `lighting.applySkyPreset` sets the sun and sky of the presets `Clear`, `Hazy`, `Overcast` and `GoldenHour`, with real values.
- The Inspector shows each field with a tooltip that names its unit.

## Further reading

- Sébastien Lagarde and Charles de Rousiers, "Moving Frostbite to Physically Based Rendering" (SIGGRAPH 2014 course notes): the photometric units in a production engine. Advanced.
- Filament, "Physically Based Rendering" design document: lumens, lux, candela and exposure conversions, with formulas. Intermediate.
- Unreal Engine documentation, "Physical Lighting Units": how its lights map to lumens and candela. Beginner.
- Blender manual, "Light Objects: Power": the radiometric watts approach. Beginner.
