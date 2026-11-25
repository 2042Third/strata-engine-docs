---
id: light/reflectance
title: "How surfaces reflect light: the reflection equation and microfacets"
description: "How much light leaves a surface toward the eye: the reflection equation, Lambert's diffuse term, and the three parts of a microfacet specular lobe."
kind: concept
size: L
tracks: [E]
needs: [light/materials, basics/math-vectors, basics/math-probability, basics/math-sphere]
time: 60
learn:
  - id: reflection-equation
    text: compute the light a surface sends toward the eye from one lamp with the reflection equation
  - id: lambert
    text: explain why Lambert's diffuse term is the albedo divided by pi
  - id: microfacet-parts
    text: name what D, V and F each add to a microfacet BRDF and compute D for a given roughness
  - id: fresnel-f0
    text: compute a non-metal's F0 from its IOR and Schlick's F at an angle
  - id: strata-choice
    text: compare Strata's BRDF with Phong's and say what the choice cannot do
since: 0.3.0
status: final
---

Put a rough ball and a smooth ball under one lamp. The smooth ball shows a small, hard, bright dot of the lamp. The rough ball shows a wide, dim glow. Both balls are made of the same plastic and lit by the same lamp, yet they send different light to your eye.

Now put a ball of water, a ball of glass and a ball of diamond side by side. All three are clear. Diamond mirrors far more of its surroundings than water does, and each ball mirrors more at its edge than at its centre.

A :term[renderer]{id=renderer} must predict all of this for every pixel. Light reaches a point from one direction, and the eye looks at the point from another. How much of the light leaves toward the eye? This page builds the answer from three parts: a rule for how light spreads over a surface, a diffuse term, and a specular term made of tiny mirrors.

## A cosine power cannot reflect light

The oldest answer is **Phong's** :term[cosine]{id=cosine} power. Mirror the direction of the light about the :term[surface normal]{id=surface-normal}, take the angle between that mirrored direction and the direction to the eye, and raise its cosine to a power $n$. A large $n$ gives a small dot and a small $n$ a wide glow. Artists tune $n$ by eye until the ball looks right.

The rule has no sense of how much light there is. The cosine is 1 at the centre of the dot for every $n$, so the peak is the same for a rough ball and a smooth one. The total light sent out is the area under the curve, and the sum of $\cos^n$ over the hemisphere around the mirrored direction is about $2\pi / (n + 1)$ :term[steradians]{id=steradian}. For $n$ = 10 that is 0.57, and for $n$ = 100 it is 0.062. The rough ball with the same peak sends out nine times more light than the smooth one, and nothing in the rule stops a surface from sending out more light than it receives.

Two more faults follow. The rule gives the same reflectance at every angle, but real surfaces reflect more at grazing angles, as the glass ball did at its edge. And the number $n$ says nothing about the material: no value of $n$ means "water" or "diamond". A good model needs three things: a fixed budget of light, an angle-dependent reflectance, and a roughness that means something physical.

## Radiance in, radiance out

**Radiance** is the light along one ray, and **irradiance** is the light that arrives on a surface, per unit of area ([Units and exposure](../light/units-exposure.md) defines both). The idea of the page is one ratio. If a little irradiance $dE$ arrives from direction $\omega_i$, the surface sends radiance $dL_o$ toward direction $\omega_o$. The ratio $dL_o / dE$ is the bidirectional reflectance distribution function (BRDF).

The **BRDF** is the share of arriving light that leaves toward one chosen direction, per steradian.

```mermaid caption="The path of one lamp's light: the cosine spreads it, and the surface decides how much goes to the eye." alt="Four boxes in a row joined by arrows. Light from one direction leads to a box for the cosine of the slant. That leads to a box for the share sent toward the eye, and then to a box for the light that reaches the eye."
flowchart LR
    A["Light from one direction"] --> B["Cosine of the slant"]
    B --> C["BRDF: share toward the eye"]
    C --> D["Light toward the eye"]
```

The cosine comes first. A beam that hits a surface head-on covers a small patch. Tilted by 60° from the normal, the same beam covers a patch twice as long, so each part of the surface gets half as much light: $\cos 60° = 0.5$. The light on the surface is the light facing the lamp, times the cosine of the angle $\theta_i$ between the normal and the direction to the lamp.

:::example[One lamp, one patch of plastic]
A lamp delivers an irradiance of 10 units to a surface turned to face it. The patch is tilted so the angle to the lamp is about 36.9°, which has the cosine 0.8. Its BRDF toward your eye is 0.159 per steradian. The patch receives 10 × 0.8 = 8 units, and sends toward your eye 0.159 × 8 = 1.27 units of radiance. Move the lamp to a grazing angle with the cosine 0.1, and the answer falls to 0.159 × 10 × 0.1 = 0.159.
:::

For one lamp, the reflection equation is a product of three numbers.

$$
L_o = f_r \, E \cos\theta_i
$$

$L_o$ is the radiance toward the eye, $f_r$ is the BRDF for this pair of directions, in 1/steradian. $E$ is the irradiance of the lamp on a surface facing it, and $\theta_i$ is the angle between the surface normal and the direction to the lamp. Check the limits: with the lamp at the horizon, $\cos\theta_i$ is 0 and nothing is reflected; with the lamp overhead the factor is 1. A lamp behind the surface has a negative cosine, and the engine clamps it to 0.

Light from every direction adds the contributions of all the directions $\omega_i$ in the hemisphere above the surface. A sum over many small pieces of solid angle becomes an integral ([Directions on a sphere](../basics/math-sphere.md) builds it).

$$
L_o(\omega_o) = \int_{\Omega} f_r(\omega_i, \omega_o) \, L_i(\omega_i) \cos\theta_i \, d\omega_i
$$

$\Omega$ is the hemisphere above the surface, $\omega_i$ is one direction of incoming light in it, and $\omega_o$ is the direction to the eye. $L_i$ is the radiance arriving from $\omega_i$, and $d\omega_i$ is a small piece of solid angle. A lamp is the special case where $L_i$ is huge on a tiny piece, and the integral collapses to the product above. Light that has bounced off other surfaces first is the subject of [the rendering problem of indirect light](../indirect/problem.md); this page keeps to light that comes from a source.

Strata's :term[shader]{id=shader} follows the one-lamp form. Its `EvaluateLight` function in `Strata/shaders/Include/PBR.slang` takes the lamp's irradiance at normal incidence and multiplies it by the BRDF and the clamped cosine. The BRDF is the rest of this page.

## Lambert's diffuse term is the albedo over pi

Some light does not bounce straight off. It enters the surface, scatters, and leaves in a direction that has forgotten where it came from. **Lambert diffuse** is a model in which the surface sends light equally in every direction. A constant BRDF $c$ is the whole model, and the question is only which value it takes.

The **albedo** of a surface is the fraction of the light that falls on it and leaves again, a number from 0 to 1. A surface of albedo 0.8 must return 80 % of the light it gets. Add up what leaves in all directions: the light leaving through a patch of the hemisphere is the radiance times its cosine times its solid angle. The sum over the whole hemisphere of the cosine is $\pi$, a result of [Directions on a sphere](../basics/math-sphere.md).

$$
\text{albedo} = \int_{\Omega} c \cos\theta \, d\omega = c \, \pi
$$

The albedo is the share of light that leaves, and $c$ is the constant BRDF. $\theta$ is the angle to the normal, and $\omega$ is a direction in the hemisphere. The integral of the cosine over the hemisphere is $\pi$ steradians, so $c$ = albedo / $\pi$. The $\pi$ is not a taste: it is the integral of the cosine weight. With albedo 0.8 the BRDF is 0.8 / 3.14159 = 0.255 per steradian, which is the figure that the one-lamp rule multiplies.

Dividing by $\pi$ twice makes the surface 3.14 times too dark, and never dividing makes it 3.14 times too bright. Strata writes the constant as `INV_PI` in the diffuse line of a later section's code.

## A rough surface is many tiny mirrors

Lambert covers light that enters the surface. Light that bounces off the top needs another model. A polished surface reflects like a mirror, and the lamp's image appears only where the surface normal is exactly halfway between the lamp and the eye. Real surfaces have bumps smaller than a pixel.

The idea of the **microfacet** model is that a rough surface is a field of tiny mirrors, each facing its own way. A pixel shows the average of millions of them.

For a lamp at direction $l$ and an eye at direction $v$ (both :term[unit vectors]{id=unit-vector} from the surface point), only mirrors whose normal is the **half vector** reflect light from $l$ toward $v$. The half vector is the sum $l + v$ scaled to length 1, written $h$. Four numbers then decide the result.

- The share of mirrors that face along $h$ (the distribution $D$).
- The share of those that the lamp and the eye can both see, not hidden by neighbours (the geometry term $G$).
- How much each mirror reflects (the Fresnel term $F$).
- A fixed conversion factor of $4 (n \cdot l)(n \cdot v)$ that comes from the geometry of reflection.

$$
f_s = \frac{D(h) \, G \, F}{4 \, (n \cdot l)(n \cdot v)}
$$

$f_s$ is the specular BRDF, $n$ is the surface normal, $l$ and $v$ point to the lamp and the eye, and the dots are :term[dot products]{id=dot-product}, the cosines of the angles between unit vectors. Strata folds $G$ and the bottom of the fraction into one number, the visibility $V$, so its specular lobe is $D \cdot V \cdot F$.

```mermaid caption="The specular lobe has three parts that multiply: how many mirrors face the half vector, how many of them are seen, and how much each reflects." alt="A box for the half vector splits into three boxes: the distribution D, the visibility V and the Fresnel term F. Arrows join the three boxes into one box for the specular light."
flowchart LR
    H["Half vector h"] --> D["D: mirrors facing h"]
    H --> V["V: mirrors seen by both"]
    H --> F["F: reflectance of each"]
    D --> S["Specular light"]
    V --> S
    F --> S
```

:::derivation
The factor 4 comes from the geometry of reflection: reflecting a direction about a mirror's normal doubles the angle. A small cone of normals of solid angle $d\omega_h$ therefore turns into a cone of reflected directions that is larger by the factor $4 (v \cdot h)$. The light that the mirrors facing $h$ catch spreads over that wider cone, which divides the BRDF by $4 (v \cdot h)$. The area of the mirrors seen from the lamp and from the eye shrinks by the cosines $(l \cdot h)$ and $(v \cdot h)$ on the way in and out. Together with the :term[normalization]{id=normalization} of $D$ below, these factors cancel to the single bottom term $4 (n \cdot l)(n \cdot v)$; the papers in the further reading give every step.
:::

## D widens with roughness and stays normalized

The distribution $D(h)$ says how many mirrors face the direction $h$. The measure is area of mirror per solid angle of normals, per unit of surface. A smooth surface has almost all its mirrors facing the surface normal $n$, so $D$ is a tall narrow peak. A rough surface spreads them, and $D$ is a low wide hill.

The distribution that Strata uses is **Trowbridge-Reitz** (GGX).

Its shape takes one number, the **alpha**, which is the :term[perceptual roughness]{id=perceptual-roughness} squared. The artist's roughness is mapped to alpha by squaring because the squared scale spreads the visible change of the highlight more evenly along the slider ([Materials](../light/materials.md) introduces perceptual roughness).

$$
D(h) = \frac{\alpha^2}{\pi \left( (n \cdot h)^2 (\alpha^2 - 1) + 1 \right)^2}
$$

$\alpha$ is the alpha, $n \cdot h$ is the cosine of the angle between the normal and the half vector, and $\pi$ is 3.14159. Check the limits at $n \cdot h$ = 1, a mirror facing straight along the normal: the bracket is $\alpha^2$, and $D = 1 / (\pi \alpha^2)$. With roughness 0.2 the alpha is 0.04 and the peak is 199. With roughness 0.6 the alpha is 0.36 and the peak is 2.46. For $\alpha$ = 1 the bottom of the fraction is $\pi$ at every angle, and $D = 1/\pi$ everywhere: a surface that is rough in every direction.

Away from the peak the order flips. At $n \cdot h$ = 0.99, about 8° off the normal, the smooth surface has $D$ = 1.1 and the rough one 1.9. The rough surface has fewer mirrors facing the normal and more facing the sides.

:::question
This page shows a few lines of shader code and C++. If calls such as `std::pow(` or a loop look new, read [Programming 1](../basics/programming-1.md), [Programming 2](../basics/programming-2.md) and [Programming 3](../basics/programming-3.md) first.
:::

Here is Strata's function. Search for `NoH`, the code's name for $n \cdot h$: the line with `f` is the bracket of the formula, written in a form that saves a multiplication.

```slang src="Strata/shaders/Include/PBR.slang#L33-L38"
float DistributionGGX(float NoH, float alpha)
{
	float alpha2 = alpha * alpha;
	float f = (NoH * alpha2 - NoH) * NoH + 1.0;
	return alpha2 / (PI * f * f);
}
```

The function takes `alpha`, never the roughness: the caller squares the roughness first (`alpha = roughness * roughness`), and a mix-up of the two is a common mistake. The result has the form $\alpha^2 / (\pi f^2)$ with `f` as the bracket.

The word "normalized" matters: if the tiny mirrors had no fixed total area, a rough surface could reflect more light than it receives. The rule is that the projected area of the mirrors, the sum of $D(h)$ times $(n \cdot h)$ over the hemisphere, equals the area of the surface itself: 1. This is why the peak falls as the surface gets rougher: the same total area is spread over more directions. Exercise 2 checks it with numbers.

:::derivation
D times the cosine integrates to 1: the integral is $\int D(h)\,(n \cdot h)\,d\omega_h$. Use the cosine $c = n \cdot h$ as the variable: the area element of the hemisphere is then $d\omega = dc\,d\varphi$, and the integral over the :term[azimuth]{id=azimuth} gives $2\pi$. With $u = c^2$, so $du = 2c\,dc$, it becomes $\alpha^2 \int_0^1 du / (1 + u(\alpha^2 - 1))^2$. That integral has the closed form $-1 / ((\alpha^2 - 1)(1 + u(\alpha^2 - 1)))$. From $u$ = 0 to 1 it gives $1/\alpha^2$, and times $\alpha^2$ the integral is 1 for every $\alpha$.
:::

## V counts the mirrors that the lamp and the eye both see

Neighbouring mirrors hide each other. A mirror may face $h$ but be covered by a ridge, so the eye cannot see it (**masking**), or the lamp cannot reach it (**shadowing**). At grazing angles most of the mirrors are covered, and without this term a rough surface would glow at the horizon.

The Smith model gives the visible share for this distribution. The **Smith visibility (height-correlated)** is the term that joins the masking-shadowing share $G$ and the bottom of the fraction $4 (n \cdot l)(n \cdot v)$ into one number $V$. The first version of the model multiplied the share seen from the eye by the share seen from the lamp, as if the two events were independent, but they are not. A mirror high on the surface is likely to be visible from both directions, and one deep in a valley is likely to be hidden from both. The height-correlated form respects that, and it gives more light than the product.

$$
V = \frac{G}{4 (n \cdot l)(n \cdot v)}
$$

$$
V = \frac{0.5}{(n \cdot l)\sqrt{(n \cdot v)^2 (1 - \alpha^2) + \alpha^2} + (n \cdot v)\sqrt{(n \cdot l)^2 (1 - \alpha^2) + \alpha^2}}
$$

The symbols are those above. Check a head-on lamp and eye: both cosines are 1, the roots are 1, and $V = 0.5 / 2 = 0.25$, so $G = 1$ and nothing is hidden. Now take a rough surface of roughness 0.6 ($\alpha$ = 0.36), with $n \cdot v$ = 0.1 and $n \cdot l$ = 0.5. The roots are 0.372 and 0.589, so $V$ = 0.5 / (0.5 × 0.372 + 0.1 × 0.589) = 2.04 and $G$ = 4 × 0.5 × 0.1 × 2.04 = 0.41. About 59 % of the mirrors are hidden.

```slang src="Strata/shaders/Include/PBR.slang#L40-L46"
float VisibilitySmithGGXCorrelated(float NoV, float NoL, float alpha)
{
	float alpha2 = alpha * alpha;
	float lambdaV = NoL * sqrt((NoV - NoV * alpha2) * NoV + alpha2);
	float lambdaL = NoV * sqrt((NoL - NoL * alpha2) * NoL + alpha2);
	return 0.5 / max(lambdaV + lambdaL, 1e-5);
}
```

In this code `lambdaV` and `lambdaL` are the two products at the bottom of the fraction, and the `max` keeps the division finite. Their names come from the Smith function's own notation, though they hold the two terms of the sum.

## Fresnel makes reflectance rise toward grazing angles

Look along a calm pond at your feet: you see the bottom. Look far across it: you see a mirror of the sky. The **reflectance** of a surface is the share of the light that it reflects, and it depends on the angle.

The exact value comes from the equations of **Fresnel**, which model light as a wave.

Real-time engines use the **Schlick approximation**, a short formula that matches them closely.

$$
F = F_0 + (1 - F_0)(1 - \cos\theta)^5
$$

$F$ is the reflectance, $F_0$ is the **F0**, the reflectance when the light arrives along the normal, and $\theta$ is the angle between the view direction and the half vector $h$. The mirrors that reflect the lamp to the eye have their normal along $h$, so that angle is the one that counts, and the code calls the cosine `VoH`. Check the limits: at $\theta$ = 0 the power is 0 and $F = F_0$; at $\theta$ = 90° the power is 1, and $F = 1$ for every material, a perfect mirror.

```slang src="Strata/shaders/Include/PBR.slang#L48-L52"
float3 FresnelSchlick(float3 f0, float VoH)
{
	float f = pow(1.0 - VoH, 5.0);
	return f + f0 * (1.0 - f);
}
```

Strata writes the formula as `f + f0 * (1 - f)` with `f` the fifth power: the same formula, rearranged.

## A non-metal's F0 comes from its IOR

Where does $F_0$ come from? For a clear material such as glass, water or plastic (not a metal), the index of refraction (IOR) tells how much the material slows light and bends it.

The **IOR** is one number per material: 1 for air, 1.33 for water, 1.5 for glass and 2.42 for diamond. Fresnel's equation at normal incidence, from air with the index 1, reduces to a closed form.

$$
F_0 = \left( \frac{n - 1}{n + 1} \right)^2
$$

$n$ is the IOR. With $n$ = 1 the surface is invisible, $F_0$ = 0. Water, $n$ = 1.33, gives (0.33 / 2.33)² = 0.020, so water reflects 2 % head-on, not 4 %. Glass, $n$ = 1.5, gives (0.5 / 2.5)² = 0.04. Diamond, $n$ = 2.42, gives (1.42 / 3.42)² = 0.172; the table runs Schlick's curve at three angles.

| IOR | $F_0$ (0°) | $F$ at 60° | $F$ at 85° |
| --- | --- | --- | --- |
| 1.33 (water) | 0.020 | 0.051 | 0.641 |
| 1.5 (glass) | 0.040 | 0.070 | 0.649 |
| 2.42 (diamond) | 0.172 | 0.198 | 0.697 |

The rows differ by a factor of 9 at the centre of the ball, and by only 9 % at the edge. At grazing angles every material becomes a mirror. A metal is different: it absorbs the light that enters, so the light that bounces off carries the metal's colour, and its $F_0$ is its base colour, one value per colour channel.

Strata computes the non-metal value in `GetDielectricF0` and stores it in the fourth number of `MaterialData::Absorption` (the `w` field). Search for the clamp and for the one special case.

```cpp src="Strata/src/Strata/Renderer/MaterialData.cpp#L51-L59"
float GetDielectricF0(const MaterialProperties& properties)
{
	constexpr float c_DefaultF0 = 0.04f; // Glass (1.5): written out, as the formula rounds it to 0.040000003
	if (properties.IOR == 1.5f || !std::isfinite(properties.IOR))
		return c_DefaultF0;
	const float index = std::clamp(properties.IOR, 1.0f, 3.0f);
	const float ratio = (index - 1.0f) / (index + 1.0f);
	return ratio * ratio;
}
```

The IOR is clamped to the range 1 to 3, which caps $F_0$ at 0.25, and a value that is not a finite number returns the glass value. The IOR of exactly 1.5, the default, returns the literal 0.04 because the formula rounds it to 0.040000003 in single precision. The shader then picks `lerp(material.Absorption.w, surface.Albedo, surface.Metallic)`: the IOR value for a non-metal, the albedo for a metal, and a mix between for a blend.

## Diffuse gets what the specular leaves

Light cannot be reflected twice. The part that bounces off the top is $F$, and only the remainder, $1 - F$, enters the surface and can leave as diffuse light. A metal has no diffuse light at all, since it absorbs what enters. Strata therefore weights the Lambert term by $(1 - F)(1 - \text{metallic})$, so the two parts never add up to more than the light that arrived.

Here are the lines of `EvaluateLightWeighted` that combine the three parts. Look at how `F` appears in both the specular and the diffuse line.

```slang src="Strata/shaders/Include/PBR.slang#L142-L146"
float3 F = FresnelSchlick(surface.F0, VoH);
float3 specular = DistributionGGX(NoH, GetLobeAlpha(alpha, sourceAlpha2)) * VisibilitySmithGGXCorrelated(NoV, NoL, alpha) * F * surface.SpecularEnergy;
// Diffuse keeps 1 - F: the compensated light leaves a dielectric's specular under 0.5% brighter, below what the diffuse
// lobe's approximation already is off by.
float3 diffuse = (1.0 - F) * (1.0 - surface.Metallic) * surface.Albedo * INV_PI * diffuseWeight;
```

The specular line is $D \cdot V \cdot F$, scaled by `SpecularEnergy`, a correction that [Energy](../light/energy.md) explains. The diffuse line is the Lambert term with its weights. The sum of the two is multiplied by the lamp's irradiance and `NoL`, the cosine: the reflection equation in one line. How these lines sit in the whole shader is the subject of [the BRDF in code](../light/brdf.md).

## How engines solve it

Each model below fixes a fault of the one before it.

| Model | Cost | Quality | Complexity | Sources |
| --- | --- | --- | --- | --- |
| Phong, cosine power | Lowest | No energy budget, no Fresnel | One power | Phong 1975 |
| Blinn-Phong, cosine of $n \cdot h$ to a power | Lowest | Better shape at grazing angles, still no budget | One power and the half vector | Blinn 1977; fixed-function OpenGL |
| Cook-Torrance with Beckmann | Moderate | Fresnel and masking, a short tail | D, G and F with a normal-like $D$ | Cook and Torrance 1982 |
| Cook-Torrance with GGX | Moderate | A long tail that looks like real highlights | The same parts, a different $D$ | Walter and others 2007; Karis 2013; Filament |
| Disney's principled model | Moderate | One set of parameters for all materials | Cook-Torrance plus extra layers | Burley 2012 |

Blinn-Phong replaced the mirrored direction by the half vector, which is cheaper and behaves better at grazing angles, but it kept the missing budget. Cook and Torrance added physics: a distribution, a masking term and Fresnel's reflectance. Their $D$ followed Beckmann's model, whose highlight falls off quickly and looks too hard. GGX has a long tail: far from the peak, $D$ falls slowly, and the tail gives the soft halo that real rough surfaces show. Disney's principled model, designed so artists tune a few parameters between 0 and 1, made the roughness squared mapping common, with the metallic parameter that Strata and the glTF format use.

## Strata chooses GGX, correlated Smith, Schlick and Lambert

Strata's BRDF takes the last Cook-Torrance row and makes one choice for each part: GGX for $D$, the height-correlated Smith visibility for $V$, Schlick for $F$, and Lambert weighted by $(1 - F)(1 - \text{metallic})$ for the diffuse part. $F_0$ comes from the IOR for a non-metal and from the albedo for a metal, with the glTF metallic-roughness parameters as the inputs.

:::why[Why GGX and Schlick, and not an exact Fresnel?]
Each part answers a cost against a gain. GGX's long tail is the look of real highlights, at the price of one division in $D$. Schlick's formula needs one power where Fresnel's equation needs square roots and complex numbers for metals. The shader follows the glTF metallic-roughness model, so its inputs match imported materials. The cost is a small error at grazing angles for some materials.
:::

The code of the parts is the subject of [the BRDF in code](../light/brdf.md). Perceptual roughness has a floor: the shader uses at least 0.045, which keeps alpha above 0.002, because the shader's own comment says a mirror-like surface causes :term[aliasing]{id=aliasing} and division problems.

## What the choice cannot do

A microfacet model with one bounce loses light. A ray that hits one mirror, then another, is not counted, and the loss grows with roughness: a rough, white metal comes out darker than its colour says. Strata multiplies the specular lobe by `SpecularEnergy` to put the missing light back, and [Energy](../light/energy.md) explains the compensation. Schlick's formula is an approximation of the exact reflectance, so the exact grazing values of some metals differ from it.

Other effects have no place in these three terms: highlights of lamps with a size ([Area lights](../light/area-lights.md)), light from the sky and from other surfaces ([Image-based lighting](../indirect/ibl.md)), and light that passes through a surface. The book lists what Strata does not do at all in [What Strata does not do](../appendix/not-in-strata.md).

## Common mistakes

- **The cosine is missing.** Symptom: surfaces turned away from the lamp are as bright as those facing it, and the light has no shading across a sphere. Fix: multiply by the clamped $n \cdot l$ once, as the reflection equation says.
- **The diffuse term is divided by $\pi$ twice, or never.** Symptom: a surface that is 3.14 times too dark, or 3.14 times too bright. Fix: divide the albedo by $\pi$ exactly once, and check that a white surface under an irradiance of $\pi$ reflects 1.
- **The roughness goes into $D$ where alpha belongs.** Symptom: highlights that stay narrow and sharp until the slider is far up. Fix: square the perceptual roughness first.
- **A Smith term that treats masking and shadowing as independent.** Symptom: rough surfaces too dark at grazing angles. Fix: use the height-correlated visibility, which is as cheap.
- **Water taken for 4 %.** Symptom: puddles that look like glass. Fix: set the IOR to 1.33, so $F_0$ is 0.02, as the Showcase's water material does.
- **Fresnel with the normal where the half vector belongs.** Symptom: a metal edge that shows a bright rim at the wrong angle. Fix: use the cosine of $v \cdot h$.

## Summary

- The reflection equation multiplies the BRDF, the lamp's irradiance and the clamped cosine; for light from every direction it integrates over the hemisphere.
- Lambert's BRDF is the albedo over $\pi$, because the cosine integrates to $\pi$ over the hemisphere and the albedo is the share of light that returns.
- A microfacet specular lobe multiplies D (the mirrors facing the half vector, normalized), V (the mirrors both seen, with the factor 4 folded in) and F (Schlick's reflectance).
- A non-metal's F0 is ((n - 1) / (n + 1))², from its IOR: 0.02 for water, 0.04 for glass, 0.17 for diamond. A metal's F0 is its colour.
- Strata uses GGX, the height-correlated Smith visibility, Schlick and Lambert with the weight (1 - F)(1 - metallic), unlike Phong's budget-less power; single scattering loses light at high roughness.

## Check yourself

1. A white surface (albedo 1) faces a lamp of irradiance $\pi$. How much radiance does the eye get from the Lambert term at any viewing angle? (a) 1 (b) $\pi$ (c) $1/\pi$ (d) 0.5

   :::answer{tests="reflection-equation lambert"}
   (a). The BRDF is $1/\pi$ and the lamp's cosine is 1, so $L_o = (1/\pi) \times \pi \times 1 = 1$. (b) forgets to divide by $\pi$, (c) forgets the irradiance, and (d) halves it with no reason.
   :::

2. Why does the peak of GGX's $D$ fall when roughness grows? (a) The surface reflects less light. (b) The same total area of mirrors spreads over more directions. (c) Fresnel takes the rest. (d) The cosine is smaller.

   :::answer{tests="microfacet-parts"}
   (b). $D$ times the cosine integrates to 1 for every alpha, so a wider hill is a lower one. (a) is false because the total light is fixed, (c) mixes up $F$ with $D$, and (d) names a factor that is not in $D$.
   :::

3. A ball has the IOR 1.33. What share of the light does it reflect head-on? (a) 4 % (b) 2 % (c) 17 % (d) 33 %

   :::answer{tests="fresnel-f0"}
   (b). $(0.33 / 2.33)^2 = 0.020$. (a) is glass, the default of 1.5, (c) is diamond, and (d) reads the digits of the IOR as a share.
   :::

4. Which three factors multiply in Strata's specular lobe? (a) D, G and the cosine (b) D, V and F (c) F, the albedo and the cosine (d) D, F and the IOR

   :::answer{tests="microfacet-parts strata-choice"}
   (b). V holds G and the bottom of the fraction. (a) omits Fresnel, (c) names the diffuse term's parts, and (d) puts the IOR in the lobe, though it enters only through $F_0$.
   :::

5. Phong's power is tuned until a sphere looks right. Name two faults that no tuning fixes.

   :::answer{tests="strata-choice"}
   The peak stays 1, so the total light changes with the power and the surface can send out more than it receives. It also has no Fresnel term: the reflectance does not rise toward grazing angles.
   :::

## Exercises

1. **Basic.** Predict F0 for water, glass and diamond, then Schlick's F at 60° and 85° of each. Check with a sketch that applies the clamp and the glass special case of `GetDielectricF0`.

   :::answer[Worked solution]{tests="fresnel-f0" solution="sketches/light-reflectance-f0.cpp"}
   Predict first with the formula: 0.020, 0.040 and 0.172. For the angles use $\cos 60° = 0.5$, so the power is 0.03125, and $\cos 85° = 0.0872$, so the power is 0.634. The sketch does the same in code.

   ```cpp sketch="light-reflectance-f0.cpp"
   #include <algorithm>
   #include <cmath>
   #include <cstdio>

   namespace
   {

   	// The rule of MaterialGPU::GetDielectricF0: 1.5 is written out, other values are clamped to [1, 3].
   	float GetDielectricF0(float ior)
   	{
   		if (ior == 1.5f)
   			return 0.04f;
   		const float index = std::clamp(ior, 1.0f, 3.0f);
   		const float ratio = (index - 1.0f) / (index + 1.0f);
   		return ratio * ratio;
   	}

   	float FresnelSchlick(float f0, float cosine)
   	{
   		return f0 + (1.0f - f0) * std::pow(1.0f - cosine, 5.0f);
   	}

   }

   int main()
   {
   	const float cosine60 = std::cos(60.0f * 3.14159265f / 180.0f);
   	const float cosine85 = std::cos(85.0f * 3.14159265f / 180.0f);
   	const float indices[] = { 1.33f, 1.5f, 2.42f };
   	for (float ior : indices)
   	{
   		const float f0 = GetDielectricF0(ior);
   		std::printf("IOR %.2f  F0 %.4f  F(60) %.4f  F(85) %.4f\n", ior, f0, FresnelSchlick(f0, cosine60), FresnelSchlick(f0, cosine85));
   	}
   	return 0;
   }
   ```

   ```text output-of="light-reflectance-f0.cpp"
   IOR 1.33  F0 0.0201  F(60) 0.0507  F(85) 0.6412
   IOR 1.50  F0 0.0400  F(60) 0.0700  F(85) 0.6485
   IOR 2.42  F0 0.1724  F(60) 0.1983  F(85) 0.6970
   ```

   1. **Lines 8–16:** the rule of `GetDielectricF0`: the glass value is written out, others are clamped to 1 to 3.
   2. **Lines 18–21:** Schlick's formula of the cosine.
   3. **Lines 29–34:** the loop prints $F_0$ and $F$ for each index, using the cosines of 60° and 85°.

   The output matches the table: water 0.0201, glass 0.0400, diamond 0.1724, and at 85° all three are between 0.64 and 0.70.
   :::

2. **Medium.** Predict whether $D \cdot (n \cdot h)$ integrates to 1 at roughness 0.2 and at 0.6, and whether the peak of $D$ rises or falls. Then check with a sketch that sums it over the hemisphere.

   :::answer[Worked solution]{tests="microfacet-parts" solution="sketches/light-reflectance-ggx.cpp"}
   The calculation above shows 1 for every alpha, and the peak $1/(\pi\alpha^2)$ falls from 199 to 2.46. The sketch sums $D \cdot c$ over two million steps of the cosine $c$ and multiplies by $2\pi$.

   ```cpp sketch="light-reflectance-ggx.cpp"
   #include <cmath>
   #include <cstdio>

   namespace
   {

   	constexpr double c_Pi = 3.14159265358979;

   	// GGX's D for the cosine of the angle between the normal and the half vector.
   	double DistributionGGX(double cosine, double alpha)
   	{
   		const double alpha2 = alpha * alpha;
   		const double f = cosine * cosine * (alpha2 - 1.0) + 1.0;
   		return alpha2 / (c_Pi * f * f);
   	}

   }

   int main()
   {
   	const double roughnesses[] = { 0.2, 0.6 };
   	const int steps = 2000000;
   	for (double roughness : roughnesses)
   	{
   		const double alpha = roughness * roughness;
   		double sum = 0.0;
   		for (int step = 0; step < steps; step++)
   		{
   			const double cosine = (step + 0.5) / steps;
   			sum += DistributionGGX(cosine, alpha) * cosine;
   		}
   		// The area element of the hemisphere is dw = dcos * dphi, so the sum over cos is times 2 pi.
   		std::printf("roughness %.1f  alpha %.2f  peak %.1f  integral %.4f\n", roughness, alpha, DistributionGGX(1.0, alpha), 2.0 * c_Pi * sum / steps);
   	}
   	return 0;
   }
   ```

   ```text output-of="light-reflectance-ggx.cpp"
   roughness 0.2  alpha 0.04  peak 198.9  integral 1.0000
   roughness 0.6  alpha 0.36  peak 2.5  integral 1.0000
   ```

   1. **Lines 9–15:** GGX's $D$ with the bracket named `f`, as the shader does.
   2. **Lines 27–31:** a sum at the middle of each step of $D \cdot c$ over the cosine, one term per step.
   3. **Line 33:** the factor $2\pi$ from the azimuth, then the print of alpha, the peak and the integral.

   Both integrals print 1.0000 and the peak falls, as predicted.
   :::

## Where it lives in Strata

- `Strata/shaders/Include/PBR.slang`: `DistributionGGX`, `VisibilitySmithGGXCorrelated`, `FresnelSchlick`, `EvaluateLightWeighted` and the roughness floor `c_MinRoughness`.
- `Strata/src/Strata/Renderer/MaterialData.cpp`: `GetDielectricF0` and the store into the `w` field of `MaterialData::Absorption`.
- `Strata/src/Strata/Renderer/Material.h`: the material property `IOR`, default 1.5, from 1 (no reflection) up.
- `Strata/shaders/Scene/Forward.frag.slang`: the surface's $F_0$ from `Absorption.w`, the albedo and the metallic value.
- `Docs/Manual/Lighting.md`: the manual's IOR values for water, glass and diamond, and what each reflects head-on.

## Further reading

- Bruce Walter, Stephen Marschner, Hongsong Li and Kenneth Torrance, "Microfacet Models for Refraction through Rough Surfaces" (2007): the paper that introduced GGX to graphics; advanced.
- Brian Karis, "Real Shading in Unreal Engine 4" (SIGGRAPH 2013 course notes): GGX, Smith and Schlick chosen for a game engine, with the reasons; intermediate.
- Brent Burley, "Physically Based Shading at Disney" (SIGGRAPH 2012): the principled model and the roughness squared mapping; intermediate.
- Eric Heitz, "Understanding the Masking-Shadowing Function in Microfacet-Based BRDFs" (2014): the height-correlated Smith term and its derivation; advanced.
- Google, "Filament: Physically Based Rendering" documentation: every term of this page derived, with code; intermediate.
- Matt Pharr, Wenzel Jakob and Greg Humphreys, "Physically Based Rendering", chapter on reflection models: radiance, the BRDF and microfacet models from the start; intermediate.
