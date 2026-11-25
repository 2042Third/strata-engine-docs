---
id: light/shadow-basics
title: "Shadow mapping from first principles"
description: "How a renderer decides whether a point lies in shadow by drawing depth from the light, and how Strata keeps the result free of acne and gaps."
kind: concept
size: L
tracks: [E]
needs: [light/lights, gpu/coordinates, basics/math-projection]
time: 60
learn:
  - id: shadow-map-idea
    text: explain how a shadow map and a depth comparison decide whether a point is lit
  - id: acne-peter
    text: explain why shadow acne and peter-panning appear and which bias causes which
  - id: bias-sizes
    text: compute the world size of Strata's depth bias and normal offset from the texel size of a shadow map
  - id: casters
    text: predict which surfaces cast a shadow in Strata and what pancaking does to a caster
  - id: set-biases
    text: choose the bias values of a light from the symptom that a scene shows
since: 0.3.0
status: final
---

Open a scene with a sun, a ground and a few boxes. Without shadows the boxes seem to float: nothing tells your eye where each box touches the ground. With the sun's shadow they sit down at once. The picture is the same, but the light now knows what stands in its way.

Now lower the sun until its rays graze the ground. In the simplest shadow method, a good shadow can then turn into a field of dark stripes on surfaces that the sun lights. Those stripes are a real bug of the method, and every engine has to fight them. Strata fights them with two corrections that no setting can disable. The pictures below show a yard under a sun at 10°, once with both bias settings at 0 and once with the defaults: the lit ground stays clean in both.

::figure{id=acne-low-sun variant=zero}

::figure{id=acne-low-sun variant=defaults}

The enlarged corners below show the fence's shadow at lower left, with the biases off and at the defaults.

::figure{id=acne-low-sun variant=zero crop=fence-shadow}

::figure{id=acne-low-sun variant=defaults crop=fence-shadow}

This page builds the method from nothing. You learn the question a shadow answers, the cheap trick that answers it, why the trick produces stripes, and the four corrections Strata applies. You finish with a small program that counts the stripes for you.

## A shadow answers one question: can this point see the light?

A point on a surface is lit when nothing stands between it and the light. It is in shadow when something does. That is the whole definition, and any shadow method is a way to answer this question for every visible point, sixty times per second.

The direct answer is a ray. Start at the point, go toward the light, and test the ray against every triangle in the scene. If the ray hits one before it reaches the light, the point is in shadow.

Count the cost on a screen of 1920 by 1080 pixels. That is 2,073,600 pixels, so one light needs 2,073,600 rays per frame. At 60 :term[frames per second]{id=frame-rate} that is about 124 million rays per second for each light, and each ray must search a scene of many thousands of triangles. A game has a sun and perhaps dozens of lamps.

:term[Graphics cards]{id=gpu} have special hardware for rays, but not every card has it. A method that asks no rays at all is cheaper, and it has served engines for decades. The next section shows the idea.

## The idea: draw the scene from the light, then compare depths

Think of the light as a camera. A camera sees the nearest surface along each of its rays and nothing behind it. Whatever the light's camera sees is lit, and everything it does not see is in shadow.

So the engine does two things. First it draws the scene as seen from the light, but it keeps only the depth of each pixel, not a color. That image is a **shadow map**: a texture that stores, for each direction from the light, the depth of the nearest surface.

Second, while it draws the real scene, it asks about each point: how far is this point from the light, along its own ray? It reads the map at that ray. If the map holds a depth nearer to the light than the point's own, something blocks the point.

```mermaid caption="The shadow pass draws depth from the light. The main pass compares each point's depth with the stored one." alt="Two boxes in a flow. The first box, the shadow pass, draws the casters from the light into a depth image. The second box, the main pass, puts each point in light space, reads the stored depth, compares it with its own and shades the point."
flowchart LR
    A["Shadow pass: draw casters from the light"] --> B["Shadow map: nearest depth per direction"]
    B --> C["Main pass: put each point in light space"]
    C --> D["Compare the point's depth with the stored depth"]
    D --> E["Farther than stored: shadow. Not farther: lit"]
```

The diagram shows the order: the map is built once per light and frame, then read many times. A surface that draws into the map is a **caster**; a surface that reads it is a **receiver**. Most objects are both. The next sections name each part of the idea.

### Light space and the two kinds of light camera

**Light space** is the :term[coordinate system]{id=coordinate-space} of that camera: its origin at the light, one axis along the light's direction, and the other two across the image. The matrix that turns a world position into light space and then into the map's image is the light's view-projection matrix. You met this pair for the player's camera in [projections](../basics/math-projection.md).

The kind of projection depends on the light, as you learned in [lights](lights.md). The sun is so far away that its rays are parallel, so its camera is orthographic: a box of space that all rays cross in the same direction. A lamp sends rays from a point, so its camera is perspective. A spot light needs one perspective view. A point light shines in all directions and needs six, one for each face of a cube.

### Depth in Strata's maps: nearer to the light is larger

Strata's depth runs backwards, as [coordinates](../gpu/coordinates.md) explains: the :term[near plane]{id=near-plane} has depth 1 and the :term[far plane]{id=far-plane} has depth 0 (:term[reversed-Z]{id=reversed-z}). A shadow map follows the same rule. A depth stored in the map is larger the nearer the surface lies to the light.

:::example[One point, three depths]
Take a sun camera whose depth range is 50 m: depth 1 at the near plane, depth 0 at 50 m. A depth is then $1 - d / 50$, where $d$ is the distance in metres from the near plane. A roof 12 m from the near plane is stored as $1 - 12/50 = 0.76$.

The ground below the roof is 30 m from the near plane, so its own depth is $1 - 30/50 = 0.40$. The map holds 0.76 for that ray, because the roof is nearer. The stored depth is larger than the point's depth, so the roof blocks it: the ground is in shadow.

Beside the roof, the map holds the ground's own depth, 0.40. The point's depth is 0.40 too. The stored depth is not larger, so nothing blocks the point: it is lit. Equal depths must count as lit, because a surface must not shadow itself. That rule is the seed of the trouble in the section on acne.
:::

Check the limits of the example. A point nearer to the light than anything in the map has a depth larger than the stored one, so it is lit. A ray that meets no surface stores depth 0, and every point is then lit. Both limits are what you expect from an empty direction and from the nearest object.

### Comparing in hardware, and averaging the answers

The comparison happens for every pixel of the screen, so it must be cheap. A graphics card offers a sampler that does it. A **comparison sampler** is a texture sampler that takes a reference depth beside the coordinates. It compares the reference with the stored depth in the hardware and returns the result instead of a depth.

There is a second reason for the comparison sampler. A shadow map is a grid of texels, and a pixel of the screen rarely falls on one texel's center. Reading one texel gives a hard answer, lit or dark, and the shadow edge looks like a staircase. If you compare first and filter after, the sampler compares the reference with four neighbouring texels, then averages the four answers by bilinear weights (as in [signals](../basics/signals.md)). The result is a number between 0 and 1, and the edge is softer.

That average of comparison results is **PCF**, short for percentage-closer filtering: the share of the neighbouring texels that block the light. Averaging the depths first and comparing once would give nonsense, because an average depth belongs to no surface. Strata creates one such sampler, with linear filters and clamped addresses, in `Strata/src/Strata/Renderer/SceneRenderer.cpp`. [Sun shadows, part two](sun-shadows-2.md) builds the wider soft filter on top of it.

## How engines solve it: three families

The shadow map is not the only answer. Engines have used three families, each introduced by a flaw of the one before.

The first family you have met: **rays**. They are exact and need no extra image, but they cost a lot of work per pixel, as counted above. Hardware ray tracing makes rays affordable in the best cases and still costs more than a map.

The second family are shadow volumes. For each caster, the engine builds the volume of space that its shadow fills: the caster's silhouette pushed away from the light. It then counts, per pixel, the volume faces in front of the surface: plus one for a face that enters a volume, minus one for a face that leaves it. A count above zero means the point is inside a volume. The result is exact to the pixel, with no stripes.

The flaw is the cost: every volume face is drawn over the screen, so large shadows touch many pixels. The volumes also need closed, well-formed meshes, and soft edges are hard to add.

The third family is the shadow map you built above. Its cost depends on the map's resolution and not on the number of pixels a shadow covers, it works with any mesh and its edges can be softened by filtering. Its flaw is that it samples the scene at a limited resolution, so the answer is approximate. The rest of this page is about that approximation.

| Approach | Cost | Quality | Complexity | Used by |
| --- | --- | --- | --- | --- |
| Rays per pixel | high; grows with scene size and light count | exact, soft edges by more rays | medium with hardware support | film :term[renderers]{id=renderer}; engines with hardware ray tracing for some lights |
| Shadow volumes | fill rate of every volume face | exact to the pixel, hard edges | closed meshes, silhouettes found every frame | early 2000s engines, for example Doom 3 |
| Shadow maps | one depth image per light view, a lookup per pixel | approximate; acne and gaps to fix; can be softened | low to medium; many biases | most real-time engines, Strata |

## Strata's choice: reversed-Z maps with texel-relative biases

Strata draws its sun shadows and its lamp shadows with shadow maps. A sun's maps are layers of one texture array, one layer for each cascade: a map that covers one range of distances from the camera ([sun shadows, part one](sun-shadows-1.md)). The lamps' maps are tiles of one atlas.

Both store depth in the 32-bit float format D32, in reversed-Z, and both are read with the comparison sampler of the last section. The next pages describe the layers, the tiles and the soft filter. This page teaches what they share, and says where the lamps differ.

:::why[Why a shadow map and not rays or volumes?]
A map's cost is one extra drawing of the scene per light view, and the lookup costs one sampler read per pixel. Volumes need closed meshes, which game artists do not promise. Rays need hardware that not every card has, and Strata has no ray-traced shadows.

The cost of the choice is the approximation: Strata has to correct the stripes and gaps below with four biases, and a shadow cannot be sharper than one texel of its map.
:::

### Shadow acne: the map is a staircase

The map stores one depth for each texel, and a texel covers a small patch of the world. Take a slope that the light crosses at an angle. Over one texel the slope has many different depths, and the map keeps only the one at the texel's center.

A receiver point on the same slope, a little off the center, has its own true depth. On one side of the center that depth is farther from the light than the stored depth. The comparison says: something nearer blocks the light. The something is the surface itself.

**Shadow acne** is that self-shadowing: stripes or dots on a lit surface, because the surface compares its depth with a stored depth that comes from itself. Acne is worst where the light grazes the surface.

:::example[How big the error gets]
Say a sun cascade covers 20 m of ground and the map has 2,048 texels across. One texel is $20/2048 = 0.00977$ m, a little under a centimetre. Call this width $t$.

Let the sun stand at an elevation $e$ above flat ground. A texel of the map covers a patch of ground of length $t / \sin e$ along the sun's direction on the ground. Over that patch the depth changes by $t \cdot \cot e$, where $\cot e$ is $\cos e / \sin e$. A point at the edge of the texel is half a patch from the center, so its error is half of that.

| Sun elevation $e$ | $\cot e$ | Largest error, in texels | Error in metres |
| --- | --- | --- | --- |
| 45° | 1.00 | 0.50 | 0.0049 |
| 30° | 1.73 | 0.87 | 0.0085 |
| 15° | 3.73 | 1.87 | 0.0182 |
| 10° | 5.67 | 2.84 | 0.0277 |
| 5° | 11.43 | 5.71 | 0.0558 |

A bias that moves the comparison toward the light by one texel, 0.0098 m, covers the first two rows and fails from 15° down. At 10° the stripes are three times wider than the bias can cover. That is why the figures at the start put the sun at 10°, where the two settings alone fall short and the corrections that stay on keep the ground clean.
:::

The table has a general lesson: the error grows as $\cot e$ grows, and it has no limit as the sun reaches the horizon. No fixed size of bias is right for all suns. The fix has to be a family of corrections, each for a different cause.

### Four biases, each for a different cause

A **bias** moves the comparison so that a surface does not shadow itself. Strata uses four for the sun and the first three for lamps, and each one is measured in the units where it matters most.

The first is a bias in the :term[rasterizer]{id=rasterization}, the fixed part of the graphics card that turns triangles into pixels. When the shadow pass draws, the card moves each stored depth away from the light by a constant of 16 steps of the depth format plus 1.5 times the triangle's slope across one texel. This is the **slope bias**: the steeper the triangle is to the light, the more it moves. The code is in `Strata/src/Strata/Renderer/SceneRenderer.cpp`, under `c_ShadowDepthBias` and `c_ShadowSlopeDepthBias`.

The second is the **depth bias**: a move of the receiver's depth toward the light, by `ShadowBias` texels (for a lamp, the lookup position moves toward the light by that many texels). The default is 1.0 texel. In the example above that is 0.0098 m, and the :term[shader]{id=shader} writes it as `ShadowBias.x * cascadeData.x / depthRange`, the texel width in metres over the depth range of the cascade.

The third is the **normal offset**: before the lookup, the shader moves the receiver along its :term[surface normal]{id=surface-normal} by `ShadowNormalBias` texels, 1.5 by default. For the same map that is 0.0146 m. A point pushed off the surface samples the map from a place where the surface's own stored depth is farther away from it. Seen from the light, the offset also moves the lookup sideways by the part of the move across the rays.

The fourth is the **receiver-plane bias**, which only the sun's cascades use. The three above use one number for the whole texel, but a tilted surface has a known depth at every offset in the texel. The shader asks which plane the receiver lies in and computes how fast the depth changes per texel along the map's axes. It then compares each filter sample with the receiver's own depth at that offset instead of at the center.

:::question[Why not use screen-space derivatives for the plane?]
The pixel shader can ask the card for how a value changes between neighbour pixels, and it would give a depth slope. Strata does not use it: the derivatives are wrong at silhouettes and depend on how the card groups pixels into 2 by 2 blocks, which changes with the order of the draws.
:::

Strata derives the slope from the surface's normal instead. In the light's orthographic :term[clip space]{id=clip-space} the plane's normal is the world normal pushed through the inverse transpose of the light's projection (as in [bases](../basics/math-bases.md)). A short :term[cross product]{id=cross-product} of the matrix's columns gives that. The function returns how much the receiver's depth changes over the whole map, in map coordinates, and the list after it says what each line does.

```slang src="Strata/shaders/Include/Shadows.slang#L101-L110"
float2 ReceiverDepthGradient(float4x4 cascadeViewProjection, float3 normal)
{
	float3 column0 = transpose(cascadeViewProjection)[0].xyz;
	float3 column1 = transpose(cascadeViewProjection)[1].xyz;
	float3 column2 = transpose(cascadeViewProjection)[2].xyz;
	float3 lightNormal = cross(column1, column2) * normal.x + cross(column2, column0) * normal.y + cross(column0, column1) * normal.z;
	if (abs(lightNormal.z) < 1e-6 * length(lightNormal))
		return float2(0.0);
	// On the plane, depth changes by -(n.x dx + n.y dy) / n.z; uv = (0.5 x + 0.5, 0.5 - 0.5 y), so dx = 2 du and dy = -2 dv.
	return float2(-2.0 * lightNormal.x, 2.0 * lightNormal.y) / lightNormal.z;
```

1. **Lines 103–105:** the first three columns of the cascade's matrix, the first three components of each, are taken as vectors.
2. **Line 106:** each cross product of two columns is one column of the :term[cofactor matrix]{id=cofactor-matrix}, which equals the inverse transpose up to a scale. Weighting them by the world normal's components gives the plane's normal in light space.
3. **Lines 107–108:** when the normal points across the rays so that its depth part is almost zero, the slope would grow without limit, so the function returns zero.
4. **Lines 109–110:** the formula for a plane: depth changes by minus the sideways parts of the normal over its depth part. The factors 2 and -2 convert from clip space, which spans 2 units, to map coordinates, which span 1, and flip the vertical axis.

The caller multiplies the result by the texel size. It limits the correction to the filter's search distance, so that a plane nearly parallel to the rays cannot move the comparison arbitrarily far.

:::example[Which bias does the work at a grazing sun]
At a sun elevation of 10° the depth bias moves the comparison by 1 texel, but the largest error of the center sample is 2.84 texels. The normal offset adds a little: it moves the lookup toward the light by $1.5 \cdot t \cdot \sin e$, which is $1.5 \cdot 0.174 = 0.26$ texels.

The slope bias does the most here. The depth changes by 5.67 texels over one texel of the map, so 1.5 times that is 8.5 texels, and the center sample is clean. The filter, however, reads samples two or three texels away. There the true error is 5.67 times the distance in texels, which is more than the sum of all three biases. Only the receiver plane compares each sample with the plane's own depth at its offset, so only it keeps the error at zero wherever the filter reaches.
:::

### Peter-panning: a bias that is too large

Every bias moves the comparison, and a move large enough to hide a surface's own depth hides a thin gap too. If the depth bias is larger than the gap between a caster and the ground below it, the map's depth no longer blocks the ground. The shadow starts away from the caster's contact point.

**Peter-panning** is that effect: the shadow detaches from the object that casts it, and the object seems to float, like Peter Pan, whose shadow comes loose in the story. A large normal offset has the same effect at a corner, because the lookup moves past the shadow's edge.

Acne and peter-panning are the two ends of one scale. Too little bias gives acne, too much gives peter-panning, and the biases of a light are the way to move along the scale. Because the depth bias and the normal offset are in texels, a sharper map (smaller texels) moves both ends together in world units, and the defaults stay right without a new adjustment.

### Pancaking: casters in front of the near plane

The sun's camera is a box of space: a near plane, a far plane and the sides. The engine fits each cascade's box around a sphere that holds a slice of what the player's camera sees, so that the map's texels go to that part of the world. A tall object, such as a mountain or a tree, can stand between the sun and the near plane. If the shadow pass clipped it, the part before the near plane would vanish from the map, and the shadow of the whole object would have a hole.

**Pancaking** flattens those casters onto the near plane instead. The vertex shader of the shadow pass limits the depth so that it never leaves the box, and the part in front of the near plane is drawn at the near plane. The shadow stays whole, because an :term[orthographic projection]{id=orthographic-projection} keeps the position across the image whatever the depth is.

```slang src="Strata/shaders/Scene/ShadowMesh.vert.slang#L47-L51"
float4 position = mul(u_Cascades[u_Shadow.Cascade].ViewProjection, float4(TransformPositionRelative(instance, localPosition), 1.0));
// Pancaking: casters between the light and the cascade's near plane are flattened onto it (reversed-Z: the near
// plane is depth 1) instead of being clipped, so they still shadow the cascade. The projection is orthographic.
position.z = min(position.z, position.w);
st_Position = position;
```

The two lines that matter are the depth limit and the final write. In reversed-Z the near plane is depth 1, so no value may be larger than 1. The call `min(position.z, position.w)` keeps the clip depth at or below the clip `w`, which is a depth of 1 after the divide. The comment adds that the projection is orthographic. A :term[perspective projection]{id=perspective-projection} would change the position across the image with the depth, so the lamps' views do not use this line.

The lamp branch of the shader is a separate path above it.

### What casts a shadow

The shadow pass draws opaque surfaces with a vertex shader alone, which writes depth and nothing else. A surface with the Mask alpha mode ([materials](materials.md)) needs a fragment shader as well. `Strata/shaders/Scene/ShadowMask.frag.slang` multiplies the material's :term[base color]{id=albedo} alpha by the alpha of its texture and discards the pixel when the result is less than `AlphaCutoff`. A leaf then casts the shadow of a leaf, and a fence made of one square with a cut-out texture casts the shadow of its bars.

A transparent surface never casts. Strata counts the Blend alpha mode and glass (always a transparent surface, whatever its alpha mode) as transparent, and the code that selects casters skips them.

The rule holds for the sun's cascades and for the lamps' atlas, on the :term[central processing unit]{id=processor} (:term[CPU]{id=processor}) path and on the GPU-driven path. The reason is the format: a depth map holds one depth per texel, so a surface can only block the light or not. A partial shadow would need a map of how much light survives, and a colored one a map of what color. Strata has neither, so a stained glass window casts no shadow and no colored light.

:::why[Why are the biases in texels?]
A bias in world units is right for one map and wrong for every other. A bias of 5 mm is fine for a texel of 1 cm and too small for a texel of 5 cm, and a camera that moves farther changes the cascade's texel width. Measuring the depth bias and the normal offset in texels of the map in use means that a value tuned once keeps its meaning at every resolution and distance.

The cost is a mental step: to know a bias in world units you must know the texel size.
:::

## What Strata's choice cannot do

A shadow map has a texel size, and no shadow is sharper than a texel. Features thinner than a texel, such as a wire, cannot be drawn faithfully. A bare shadow map gives a hard edge, and a filter softens it without knowing the size of the light: [sun shadows, part two](sun-shadows-2.md) shows what Strata adds.

Strata draws no shadow from a transparent surface, as above. Light does not dim or take a color when it passes glass, and a thin curtain casts either a cut-out shadow (Mask) or none (Blend). [What Strata does not do](../appendix/not-in-strata.md) lists the lighting features that Strata omits.

## Common mistakes

- **A bias in world units.** The symptom: acne returns when the map's resolution or the cascade's distance changes. The fix: measure biases in texels, as Strata does, and raise the texel biases instead of a metre value.
- **Screen derivatives for the receiver plane.** The symptom: dots along silhouettes that change when the draw order changes. The fix: derive the plane from the surface normal and the light's matrix, as `ReceiverDepthGradient` does.
- **Raising the depth bias against all acne.** The symptom: stripes go away and shadows detach from the feet of objects. The fix: raise `ShadowNormalBias` for grazing surfaces first, keep `ShadowBias` low.
- **A Blend material expected to cast a shadow.** The symptom: a curtain or a window casts nothing. The fix: use Mask with a cut-out texture, or accept a lit room.
- **A Mask cutoff of 0.5 for every texture.** The symptom: the shadow of a leaf looks fatter or thinner than the leaf. The fix: set `AlphaCutoff` so that the cut matches the leaf, since the shadow uses the same cut as the surface.
- **Judging the biases at a high sun.** The symptom: the scene looks clean at noon and shows stripes at sunset. The fix: test at a low sun, such as the 10° of `ow.lowsun`, where the error is largest.

## Summary

- A shadow map is a depth image drawn from the light. A point is in shadow when the stored depth in its direction is nearer to the light than its own depth, which in reversed-Z means the stored depth is larger.
- A shadow map stores one depth per texel, so a sloped surface compares with a depth that is not its own. That gives shadow acne, and a bias that is too large gives peter-panning. Both rise at grazing angles.
- Strata's depth bias is `ShadowBias` texels, its normal offset is `ShadowNormalBias` texels; for a texel of 0.0098 m they are 0.0098 m and 0.0146 m. The rasterizer's slope bias and, for the sun, the receiver plane, computed from the inverse transpose of the light's projection, complete the four.
- Opaque and Mask surfaces cast shadows, and Blend and glass never do. Pancaking flattens casters in front of the near plane onto it, and the Mask cut is the material's own `AlphaCutoff`.
- Acne means raise the normal offset first. Detached shadows mean lower the depth bias. Never set a bias in world units.

## Check yourself

1. A sun camera has a depth range of 20 m: depth 1 at the near plane and 0 at 20 m. A receiver is 15 m from the near plane, and the map holds a surface 6 m from it. Is the receiver in shadow?

   - A. No: its depth 0.25 is smaller than the stored depth 0.70.
   - B. Yes: its depth 0.25 is smaller than the stored depth 0.70, so a nearer surface blocks it.
   - C. Yes: the receiver is farther from the near plane, which always means shadow.
   - D. No: the stored depth 0.70 is too far from the receiver's.

   :::answer{tests="shadow-map-idea"}
   B. The depths are $1 - 15/20 = 0.25$ and $1 - 6/20 = 0.70$. In reversed-Z the stored depth is larger, so that surface is nearer to the light and blocks the receiver. A has the wrong conclusion. C and D invent distance rules.
   :::

2. A wide, sloped hillside shows dark stripes in full sun, and the shadow of a tree on the ground is joined to its trunk. What is the right fix?

   - A. Lower `ShadowBias` to zero.
   - B. Raise `ShadowNormalBias` and keep `ShadowBias` low.
   - C. Raise `ShadowBias` to 10.
   - D. Set a bias of 0.5 m in world units.

   :::answer{tests="acne-peter"}
   B. The stripes are acne from a slope, and the tree's shadow is joined, so peter-panning is absent. Lowering the depth bias (A) brings more acne. A large depth bias (C) fixes stripes and then detaches the trunk's shadow. A world-unit bias (D) is right for one map only and moves shadows when the cascade changes.
   :::

3. A cascade covers 40 m of ground with 2,048 texels. How many metres do the default depth bias and the default normal offset move the comparison?

   :::answer{tests="bias-sizes"}
   A texel is $40/2048 = 0.0195$ m. The depth bias is 1.0 texel, so 0.0195 m. The normal offset is 1.5 texels, so 0.0293 m. Both are twice the numbers for a 20 m cascade, because the texel is twice as wide.
   :::

4. A scene has a fence with a Mask material, a window with a Blend material and a glass sheet. The sun is low. Which of them cast shadows, and what shape does the fence's shadow have?

   :::answer{tests="casters"}
   The fence casts a shadow with the shape of its opaque bars, because the shadow pass discards texels whose alpha is below `AlphaCutoff`. The Blend window casts none, and neither does the glass sheet, whose material is transparent whatever its alpha mode.
   :::

5. Shadows of objects float a hand's width above the ground, and the scene is lit by a sun at 40° of elevation. Which two values would you look at first, and in which direction do you move them?

   :::answer{tests="set-biases"}
   Look at `ShadowBias` and `ShadowNormalBias`, and lower them. Floating shadows are peter-panning, the sign of too much bias. At 40° the surface is not grazing, so values above the defaults of 1.0 and 1.5 texels are more than the slope needs. Lower the depth bias first, in steps, until acne begins and then go one step back.
   :::

## Exercises

1. **Basic.** A fence has a Mask material, and a glass sheet stands beside it under a low sun. Predict which shadows change when you set `AlphaCutoff` of the fence to 0.1 and then to 0.9, and which never appears. Then run it in the Scene view.

   :::answer[Worked solution]{tests="casters"}
   The fence's shadow changes. A texel is discarded when its alpha is less than the cutoff. At 0.1 nearly every texel with any coverage stays, so the bars, soft edges included, cast a thick shadow. At 0.9 only texels that are almost fully opaque stay, so the bars' shadow is thinner. The glass sheet's shadow never appears, at either cutoff, because transparent surfaces are skipped before the cut.
   :::

2. **Medium.** For which sun elevations is the largest error of the receiver, half a texel's depth change, at most the default depth bias of 1 texel? Use the formula that half the error equals $0.5 \cdot \cot e$ texels.

   :::answer[Worked solution]{tests="bias-sizes acne-peter"}
   The condition is $0.5 \cdot \cot e \le 1$, so $\cot e \le 2$, which is $\tan e \ge 0.5$. The angle whose tangent is 0.5 is 26.57°. Above 26.6° the depth bias alone covers the error of the center sample. Below it acne appears, and in practice sooner, because the filter reads samples away from the center.
   :::

3. **Hard.** Write a program with a shadow map of 20 texels of 0.5 m over a ramp with a slope of 0.5, lit from straight above. Count how many of 1000 lit samples the map shadows with each bias off and on: depth, slope, normal offset and receiver plane. For a thin plate 0.3 m above a flat floor, count how many of 100 floor samples under it still lie in shadow.

   :::answer[Worked solution]{tests="acne-peter bias-sizes" solution="sketches/light-shadow-basics-sloped-line.cpp"}
   The program stores the highest surface at each texel's center, applies one bias at a time and counts.

   ```cpp sketch="light-shadow-basics-sloped-line.cpp"
   // A shadow map in two dimensions: the light shines straight down and a "texel" is a column of width 0.5.
   #include <algorithm>
   #include <cmath>
   #include <cstdio>
   #include <vector>

   struct Surface
   {
   	float X0;
   	float X1;
   	float Y0;
   	float Slope;
   };

   struct Biases
   {
   	const char* Name;
   	float Depth;  // in texels, toward the light
   	float Slope;  // in texels of depth per texel of slope, away from the light (the rasterizer's)
   	float Normal; // in texels, along the receiver's normal
   	bool Plane;   // compare against the receiver's own plane at the texel center
   };

   constexpr float c_Texel = 0.5f;
   constexpr int c_TexelCount = 20;

   float HeightAt(const Surface& surface, float x)
   {
   	return surface.Y0 + surface.Slope * (x - surface.X0);
   }

   // The shadow map stores, per texel, the highest surface at the texel's center (nearest to the light).
   std::vector<float> RenderMap(const std::vector<Surface>& surfaces, float slopeBias)
   {
   	std::vector<float> map(c_TexelCount, -1000.0f);
   	for (int texel = 0; texel < c_TexelCount; texel++)
   	{
   		const float center = (static_cast<float>(texel) + 0.5f) * c_Texel;
   		for (const Surface& surface : surfaces)
   			if (center >= surface.X0 && center <= surface.X1)
   				map[texel] = std::max(map[texel], HeightAt(surface, center) - slopeBias * c_Texel * std::fabs(surface.Slope));
   	}
   	return map;
   }

   // Counts the samples of one receiver surface that the map wrongly or rightly puts in shadow.
   int CountShadowed(const std::vector<float>& map, const Surface& receiver, float from, float to, int samples, const Biases& biases)
   {
   	const float length = std::sqrt(1.0f + receiver.Slope * receiver.Slope);
   	int shadowed = 0;
   	for (int sample = 0; sample < samples; sample++)
   	{
   		const float x = from + (to - from) * (static_cast<float>(sample) + 0.5f) / static_cast<float>(samples);
   		const float lookupX = x - receiver.Slope / length * biases.Normal * c_Texel;
   		const float lookupY = HeightAt(receiver, x) + 1.0f / length * biases.Normal * c_Texel;
   		const int texel = std::clamp(static_cast<int>(std::floor(lookupX / c_Texel)), 0, c_TexelCount - 1);
   		float reference = lookupY + biases.Depth * c_Texel;
   		if (biases.Plane)
   			reference += receiver.Slope * ((static_cast<float>(texel) + 0.5f) * c_Texel - lookupX);
   		if (map[texel] > reference)
   			shadowed++;
   	}
   	return shadowed;
   }

   int main()
   {
   	const Biases rows[] = { { "all off", 0.0f, 0.0f, 0.0f, false }, { "depth 0.1", 0.1f, 0.0f, 0.0f, false },
   		{ "depth 1", 1.0f, 0.0f, 0.0f, false }, { "slope 1.5", 0.0f, 1.5f, 0.0f, false },
   		{ "normal 1.5", 0.0f, 0.0f, 1.5f, false }, { "plane", 0.0f, 0.0f, 0.0f, true } };
   	const Surface ramp = { 0.0f, 10.0f, 0.0f, 0.5f };
   	const Surface floor = { 0.0f, 10.0f, 0.0f, 0.0f };
   	const Surface plate = { 4.0f, 5.0f, 0.3f, 0.0f };
   	std::printf("%-11s %-18s %s\n", "bias", "ramp, 1000 lit", "floor under a plate 0.3 above it, 100 dark");
   	for (const Biases& biases : rows)
   	{
   		const int acne = CountShadowed(RenderMap({ ramp }, biases.Slope), ramp, 0.5f, 9.5f, 1000, biases);
   		const int kept = CountShadowed(RenderMap({ floor, plate }, biases.Slope), floor, 4.0f, 5.0f, 100, biases);
   		std::printf("%-11s %-18d %d\n", biases.Name, acne, kept);
   	}
   	return 0;
   }
   ```

   ```text output-of="light-shadow-basics-sloped-line.cpp"
   bias        ramp, 1000 lit     floor under a plate 0.3 above it, 100 dark
   all off     500                100
   depth 0.1   300                100
   depth 1     0                  0
   slope 1.5   0                  100
   normal 1.5  0                  0
   plane       0                  100
   ```

   1. **Line 41:** the map stores, per texel, the height at the center, minus the slope bias.
   2. **Lines 54–55:** the sample moves along the normal, and the map is read in the texel where it lands.
   3. **Lines 57–59:** the depth bias raises the reference, and the receiver plane adds the surface's own change up to the texel center.
   4. **Line 60:** a map depth above the reference counts as shadow.
   :::

## Where it lives in Strata

- `Strata/shaders/Include/Shadows.slang`: `SampleCascadeShadow` (the normal offset and the depth bias) and `ReceiverDepthGradient`.
- `Strata/shaders/Scene/ShadowMesh.vert.slang`: the shadow pass's vertex shader, with the pancaking.
- `Strata/shaders/Scene/ShadowMask.frag.slang`: the discard of cut-out texels.
- `Strata/src/Strata/Renderer/SceneRenderer.cpp`: the rasterizer bias, the comparison sampler and the D32 maps.
- `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp`, `SceneRendererLocalShadows.cpp` and `Strata/shaders/Scene/Cull.comp.slang`: the selection of casters, which skips transparent surfaces.
- `Strata/src/Strata/Renderer/RendererComponents.h`: the defaults of `ShadowBias` and `ShadowNormalBias`, on the `DirectionalLight`, `PointLight` and `SpotLight` components.
- `Strata/src/Strata/Renderer/MaterialData.cpp`: the flags that mark Blend and glass as transparent.

## Further reading

- Lance Williams, "Casting curved shadows on curved surfaces", SIGGRAPH 1978: the invention of shadow maps (advanced).
- Franklin Crow, "Shadow algorithms for computer graphics", SIGGRAPH 1977: shadow volumes (advanced).
- William Reeves, David Salesin and Robert Cook, "Rendering antialiased shadows with depth maps", SIGGRAPH 1987: percentage-closer filtering (advanced).
- Real-Time Rendering, chapter on shadows, by Akenine-Möller, Haines and Hoffman: the families compared (intermediate).
- Christian Schüler, "Eliminating surface acne with gradient shadow mapping", in GPU Pro 4: the receiver-plane bias (advanced).
