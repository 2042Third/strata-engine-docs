---
id: light/materials
title: "Strata's material model"
description: "How Strata describes a surface with a base color, metallic and roughness, the maps that vary them, and what the model leaves out."
kind: concept
size: L
tracks: [E]
needs: [assets/textures, basics/math-bases, light/units-exposure]
time: 55
learn:
  - id: phong-flaws
    text: explain why a color and a specular power cannot describe a surface a renderer can trust
  - id: three-numbers
    text: compute the diffuse color and the head-on reflectance of a surface from its base color and metallic value
  - id: strata-fields
    text: name the nine maps of a Strata material, their channels and color spaces, and what each factor multiplies
  - id: normal-frame
    text: compute the world normal that a texel of a normal map gives in a tangent frame
  - id: alpha-albedo
    text: choose an alpha mode and plausible albedo values for a surface, and name what the model leaves out
since: 0.3.0
status: final
---

Picture two rows of five spheres in a plain gray room. The spheres of the bottom row are metal, those of the top row are plastic, and in each row the surface is mirror smooth on the left and dull on the right. Nothing else in the room changes, so every difference between two spheres comes from one thing: how that surface sends light back.

::figure{id=furnace-sweep}

An artist who builds a game must describe such surfaces to the :term[renderer]{id=renderer}, and must do it with few numbers. A material with two hundred controls is useless, because nobody can predict what each control does. The renderer, for its part, must turn those numbers into light that behaves like real light under any lamp, any sky and any exposure. This page shows the few numbers Strata uses, why they work, and what the model cannot express.

## A color and a shininess cannot describe a surface

The oldest answer gives a surface a color and a "shininess". Phong's model, from 1975, adds two parts. The diffuse part scatters light evenly in all directions and takes the surface color. The specular part makes a bright highlight, and the shininess is its **specular power**: a number $n$ that sharpens the highlight as it grows.

Try it with numbers. A surface has a diffuse share of 0.8, a specular share of 0.5, and a specular power of 10 for a soft highlight or 200 for a sharp one. Light of strength 1 arrives. The diffuse part returns 0.8 of it and the specular part returns 0.5 of it: together 1.3, which is more light than arrived. Real surfaces cannot do that, so a scene lit this way gains energy from nothing and glows too much where the highlight meets the diffuse color.

The model fails in three ways that matter to a team.

- **No physical meaning.** What does a power of 200 mean for the material? The power has no unit, no measurement and no link to a real surface, so an artist learns it by trial.
- **Extra light.** The two shares are free, so nothing keeps their sum below 1. The picture looks right under one lamp and wrong under the next.
- **Every tool means something else.** One tool writes the power from 1 to 1000, another writes a glossiness from 0 to 1, a third writes a roughness. A material moved between tools changes its look, and nobody can say which version is right.

:::question[Is the power of a highlight the same as the roughness of a surface?]
No. They describe the same spread of light with opposite signs: a high power means a small, sharp highlight, a high roughness means a wide, dull one. The power also has no fixed scale, which is the problem the next sections solve.
:::

## Two kinds of matter and three numbers

Physics gives a better starting point than a highlight: what happens to a ray that meets a surface. Two kinds of matter answer differently. This page names them first and then counts what an artist must set.

A **dielectric** is a material that does not conduct electricity: wood, plastic, stone, skin, paint, glass. Light meets its surface and splits. A small share, about 4 % for most dielectrics, bounces off at once as a white mirror image. The rest enters the material, scatters between its particles, loses some colors and leaves again in all directions. That second part is the diffuse color we see.

A metal is a conductor. Its free electrons stop light from entering at all, so a metal has no diffuse part. A metal reflects most of the light as a mirror image and tints the mirror: gold reflects yellow, copper reflects orange, and steel reflects almost no tint.

Three numbers then describe both kinds. The first is the **albedo**, also called **base color**: the color a dielectric scatters diffusely, or the color of the mirror image of a metal.

The second is **metallic**: 0 for a dielectric and 1 for a metal. Real objects sit near 0 or 1; a value between them describes a surface that is part dielectric at one point, such as a painted metal where the paint has worn thin.

The third is **perceptual roughness**: the artist's roughness from 0 (mirror smooth) to 1 (fully dull). Its square is the *alpha* that the shading formula uses for the spread of the highlight.

```mermaid caption="Base color and metallic split into the diffuse color and the head-on reflectance of the surface; roughness sets how widely the reflection spreads." alt="Three inputs on the left: base color, metallic and perceptual roughness. Base color and metallic lead to the diffuse color and to the head-on reflectance. Roughness leads to the alpha of the highlight."
flowchart LR
    B["Base color"] --> D["Diffuse color"]
    M["Metallic"] --> D
    B --> F["Head-on reflectance"]
    M --> F
    R["Perceptual roughness"] --> A["Alpha = roughness squared"]
```

Why square the roughness? Equal steps of the artist's slider should look like equal steps in the picture. The highlight's width grows slowly near 0 and quickly near 1, so the model squares the slider: 0.5 gives an alpha of 0.25, and 0.1 gives 0.01. An artist who reads 0.5 as "half rough" is right about the look, and wrong if they use 0.5 as the alpha in a formula.

### Worked example: one color, three values of metallic

Take a base color of $(0.8, 0.5, 0.2)$, a warm brown-orange in linear light. The surface keeps a diffuse color of base times $(1 - m)$ and reflects head-on with $F_0$, the share of light a surface reflects when looking straight at it. For a dielectric, $F_0$ is about 0.04 (the [reflectance page](reflectance.md) derives it). For a metal, $F_0$ is the base color.

$$ d = (1 - m)\,c \qquad F_0 = (1 - m)\,0.04 + m\,c $$

Here $c$ is the base color: three numbers, red, green and blue, from 0 to 1 in linear light. The symbol $m$ is the metallic value (0 to 1), $d$ is the diffuse color the surface scatters, and $F_0$ is the head-on reflectance (also three numbers). The factor $(1 - m)$ takes the diffuse part away as the surface becomes a metal. The second formula is a blend between 0.04 and the base color, with $m$ as the weight.

- At $m = 0$ the diffuse color is $(0.8, 0.5, 0.2)$ and $F_0$ is $(0.04, 0.04, 0.04)$: an orange plastic with a faint white highlight.
- At $m = 1$ the diffuse color is $(0, 0, 0)$ and $F_0$ is $(0.8, 0.5, 0.2)$: a copper-like metal with no diffuse color at all, whose mirror image is tinted.
- At $m = 0.5$ the diffuse color is $(0.4, 0.25, 0.1)$ and $F_0$ is $(0.42, 0.27, 0.12)$: a surface that is both, which no solid object is.

Check the limits. If the base color is black, a dielectric reflects only its 4 % highlight, and a metal reflects nothing, which is a black hole in the scene. If the base color is white, a metal reflects everything it sees. Neither is a material in a real room, a point the section on plausible albedos returns to.

## How engines described surfaces

Three families came one after the other, each fixing a flaw of the one before.

**Phong and Blinn-Phong** keep a diffuse color, a specular color and a specular power. They are cheap: a power function. The flaw is the one above: the numbers have no physical meaning and the shares can add light.

**Specular-glossiness** keeps a diffuse color and a specular color, and replaces the power with a glossiness from 0 to 1. Artists paint the maps from photographs, and the specular color can carry the tint of a metal. The flaw is freedom: nothing stops an artist from painting a bright diffuse color and a bright specular color in the same place, which adds light again. Two color maps also cost more memory than one color and a single mask.

**Metallic-roughness** keeps one color, a metallic value and a roughness. Burley published it in 2012 as part of Disney's "principled" shading. Real-time engines then adopted it, and the glTF 2.0 format made it a standard in 2017. The two kinds of matter share one color, so the model cannot add light by a bad choice of colors, and one mask (metallic) switches between them.

| Approach | Cost | Quality | Complexity | Used by |
| --- | --- | --- | --- | --- |
| Phong, Blinn-Phong | Lowest: a power function | Highlights with no energy limit | Two colors and a power | The fixed-function lighting of old graphics interfaces |
| Specular-glossiness | Medium: two color maps | Good, if the artist keeps the colors apart | Three inputs, two of them colors | Older glTF files and some texture painting tools |
| Metallic-roughness | Medium: one color, two single numbers | Good by construction | Three inputs, one a color | Disney's principled shading, glTF 2.0, Unreal Engine 4 |

:::elsewhere[Where metallic-roughness came from]
Burley's course notes "Physically Based Shading at Disney" (2012) introduced the metallic and roughness parameters, and Karis's "Real Shading in Unreal Engine 4" (2013) showed them in a real-time engine. The glTF 2.0 specification (2017) names the model `pbrMetallicRoughness`.
:::

## Strata reads glTF's model as it is

Strata chose the third family and adopted the glTF 2.0 version of it, field for field. The material is an asset of type `Material`, stored as a `.stmat` file, and its parameters are the :term[struct]{id=struct} `MaterialProperties`. The next paragraph says what to search for in it.

:::question[Is the C++ below new to you?]
The struct below holds plain data fields ([programming 2](../basics/programming-2.md)), and the types `glm::vec4` and `AssetHandle` are classes ([programming 3](../basics/programming-3.md)).
:::

Read the struct from the top: first the factors (plain numbers and colors), then the five maps. A map is an `AssetHandle`, the handle of a texture asset, never a path. The comments say the :term[color space]{id=color-space} of each map.

```cpp src="Strata/src/Strata/Renderer/Material.h#L26-L45"
glm::vec4 BaseColor = { 1.0f, 1.0f, 1.0f, 1.0f }; // Linear RGBA
float Metallic = 0.0f;
float Roughness = 0.5f;
// Emitted luminance in nits (cd/m^2): EmissiveColor * EmissiveIntensity, times the emissive map.
glm::vec3 EmissiveColor = { 0.0f, 0.0f, 0.0f };
float EmissiveIntensity = 1.0f;
float NormalScale = 1.0f;
float OcclusionStrength = 1.0f;
MaterialAlphaMode AlphaMode = MaterialAlphaMode::Opaque;
float AlphaCutoff = 0.5f;
bool DoubleSided = false;
bool Unlit = false;
glm::vec2 UVTiling = { 1.0f, 1.0f };
glm::vec2 UVOffset = { 0.0f, 0.0f };

AssetHandle BaseColorMap = UUID::Null();         // sRGB color (+ alpha)
AssetHandle MetallicRoughnessMap = UUID::Null(); // Linear: G = roughness, B = metallic (glTF packing)
AssetHandle NormalMap = UUID::Null();            // Tangent-space normal map
AssetHandle OcclusionMap = UUID::Null();         // Linear: R = ambient occlusion
AssetHandle EmissiveMap = UUID::Null();          // sRGB emissive color
```

1. **Line 26:** the base color holds red, green, blue and alpha in linear light; its default is white.
2. **Lines 27–28:** `Metallic` defaults to 0 and `Roughness` to 0.5. `Roughness` is the perceptual roughness.
3. **Lines 30–31:** the emission is a color and an intensity, together a :term[luminance]{id=luminance} in :term[nits]{id=lux}.
4. **Lines 32–39:** the factors that tune the maps: the normal scale, the occlusion strength, the alpha mode and cutoff, the two flags and the two texture coordinate fields.
5. **Lines 41–45:** the five maps of the glTF model, each tagged with its color space.

A factor multiplies its map. The :term[shader]{id=shader} reads the base color as the factor times the map's color. It reads the roughness as `Roughness` times the map's green channel and the metallic value as `Metallic` times the map's blue channel, then limits both to the range 0 to 1.

A slot with no map reads as white (a flat normal for the :term[normal map]{id=normal-map}), so the factor alone decides. A factor therefore tunes a texture without painting it again: `Roughness` 0.5 halves the roughness that a painter stored.

### The nine maps and their channels

A Strata material has nine texture slots. The five above come from the glTF base model, and four belong to the coat and glass layers of [the clear coat page](clearcoat-transmission.md).

| Map | Channels used | Stored as | Used for |
| --- | --- | --- | --- |
| Base color | Red, green, blue, alpha | :term[sRGB]{id=srgb} | Albedo or metal tint, and coverage (alpha) |
| Metallic-roughness | Green: roughness, blue: metallic | Linear | Roughness and metallic; red is not read |
| Normal | Red and green: X and Y of the normal | Linear | Small bumps without more triangles |
| Occlusion | Red | Linear | Darkening of indirect light in creases |
| Emission | Red, green, blue | sRGB | The color of emitted light |
| Coat strength | Red | Linear | The coat's share, see the clear coat page |
| Coat roughness | Green | Linear | The coat's roughness |
| Coat normal | Red and green | Linear | The coat's own bumps |
| Transmission | Red | Linear | The share of light passed through glass |

The rule behind the column "Stored as" comes from [the textures page](../assets/textures.md): color is read by the eye and stored in sRGB, while data is numbers, stored linear. The base color and the emission map are color. Everything else is data. Import a roughness map as color and its values bend, as the textures page shows for normal maps. The command `material.get` warns when a map's import usage does not fit its slot.

:::why[Why pack roughness in green and metallic in blue?]
Strata copies the layout of glTF, where one map carries both values, so a model made in any tool that exports glTF arrives with its maps in the right channels. The cost is a map whose red channel is wasted in Strata, because occlusion has its own map here. The gain is no conversion at import and the same files in the editor, in Blender and in other glTF viewers.
:::

### Normal maps: data that tilts the light

A flat wall of 12 triangles cannot show every brick edge, because each brick would need triangles of its own. A **normal map** is a texture whose texels store a direction for the shading instead of a color. The surface stays flat, and the light behaves as if each texel's tiny patch faced the stored direction. [The textures page](../assets/textures.md) explains how a normal map is stored and imported; here the point is what its numbers mean.

A texel cannot store a direction in :term[world space]{id=world-space}, because the object moves and turns. It stores one in **tangent space**, a coordinate frame fixed to the surface. The third axis is the surface's own normal $N$, and the other two lie in the surface along the texture's two directions: the tangent $T$ and the :term[bitangent]{id=bitangent} $B$. A direction in this frame is a change relative to the surface, whichever way the object faces. If you have not met the change of space before, [the bases page](../basics/math-bases.md) builds it.

Strata reads only X and Y from the texture and rebuilds Z, so that the vector has length 1.

$$ n_x = 2\,\frac{r}{255} - 1 \qquad n_z = \sqrt{1 - n_x^2 - n_y^2} $$

In the first formula $r$ is the texel's red :term[byte]{id=byte} (0 to 255) and $n_x$ is the X component of the direction (from -1 to 1); the green byte gives $n_y$ the same way. In the second, $n_z$ is the component along the :term[surface normal]{id=surface-normal}, which is always at least 0, because the stored direction never points into the surface. The world normal is then $n_x T + n_y B + n_z N$.

#### Worked example: one texel

Take the texel with red 192 and green 128. Then $n_x = 2 \cdot 192 / 255 - 1 = 0.506$ and $n_y = 2 \cdot 128 / 255 - 1 = 0.004$, which is close to 0. Z is $\sqrt{1 - 0.256 - 0} = 0.863$. A flat texel, (128, 128, 255) in the file, gives X and Y close to 0 and Z close to 1: the surface normal itself.

Now put the patch on a floor whose normal $N$ points up as $(0, 1, 0)$, with a tangent $T = (1, 0, 0)$. Strata takes $B$ as the :term[cross product]{id=cross-product} of $N$ and $T$, times the sign stored in the tangent's fourth number (here +1), so $B = (0, 0, -1)$. The world normal is $0.506\,(1, 0, 0) + 0.004\,(0, 0, -1) + 0.863\,(0, 1, 0)$, close to $(0.506, 0.863, 0)$. The normal leans 30 degrees toward $T$.

The frame must exist. The importer or the model supplies the tangent of each vertex. A vertex whose tangent is zero makes the shader use the plain surface normal, so a model without tangents shows no bumps at all. [The glTF models page](../assets/models-gltf.md) says what the importer does when a file carries none.

The shader rebuilds Z from the stored X and Y first. Then it multiplies X and Y by `NormalScale` and brings the result back to length 1: 0 turns the map off, and 2 makes the normal lean further. How the engine decodes the map when it sends the material to the :term[graphics processing unit]{id=gpu} (GPU) is the subject of [the material data page](material-data.md).

::compare{id=normal-map-compare before=map-off after=map-on}

The difference shows best in the darker right half, enlarged below: smooth streaks without the map, soft gray spots with it.

::figure{id=normal-map-compare variant=map-off crop=right}

::figure{id=normal-map-compare variant=map-on crop=right}

### Occlusion darkens only light that has no shadow

The occlusion map says which texels sit in a crease, where ambient light cannot reach. The shader computes the occlusion value as `lerp(1, map, OcclusionStrength)`, where :term[lerp]{id=linear-interpolation} blends from 1 to the map's red value. A map value of 0.4 with a strength of 0.5 gives 0.7. The screen's own ambient occlusion, which the renderer computes from the depth of the scene, multiplies that value. With 0.8 on screen the product is 0.56.

The result darkens indirect light only: light from the image of the sky, the ambient term and the probes. Direct light from a lamp or the sun has shadows, which are the right way to darken it. Occlusion on top of a shadow would count the same darkness twice.

### The flags and the tiling fields

- `DoubleSided`: Strata draws both faces, with no :term[back-face culling]{id=winding-order} in any pass, the shadow pass included; a back face flips its normal. Use it for leaves and cloth. A closed object keeps it off, because it doubles the work.
- `Unlit`: the surface skips lighting. It shows its base color plus emission, and the coat and glass layers are off.
- `NormalScale`: the lean of the normal map, from 0 to 10.
- `UVTiling` and `UVOffset`: the :term[texture coordinates]{id=texture-coordinates} of every map are multiplied by the tiling and then shifted by the offset, so a tiling of $(4, 4)$ repeats a texture four times in each direction.

### Alpha modes: opaque, mask and blend

The alpha of the base color (factor times map) means three different things, chosen by `AlphaMode`.

**Opaque** ignores alpha: the surface covers what lies behind it. **Mask** keeps a pixel when its alpha is at least `AlphaCutoff` (default 0.5) and discards it otherwise. The cut happens in the :term[depth prepass]{id=depth-prepass}, in the shadow pass and in the forward pass alike, so a leaf's shadow has the leaf's shape. A leaf pixel with an alpha of 0.3 disappears at a cutoff of 0.5, and a pixel with 0.5 stays.

**Blend** mixes the surface with what lies behind it by its alpha. Strata draws blended surfaces after the opaque ones, sorted from back to front. Masked edges are hard and cheap, while blended edges are soft, cost more and can sort wrongly, so prefer Mask for foliage and fences. [The clear coat page](clearcoat-transmission.md) covers blending and premultiplied alpha.

### Emission is a luminance in nits

The emitted light of a surface is `EmissiveColor` times `EmissiveIntensity` times the emission map, and it is a luminance in nits, the unit of [the units page](units-exposure.md). The tooltip of `EmissiveIntensity` gives the scale: a screen shines at roughly 200 nits and a lit sign at roughly 1,000. The default intensity of 1 is therefore almost black beside a lit room. People who expect "1" to mean full brightness meet this surprise often. An emission map that is still loading reads as black, never white.

### Plausible albedos

Real materials reflect between about 3 % and 85 % of the light that reaches them diffusely. Strata's debug view of the albedo marks the base colors whose luminance lies below 0.03 (darker than charcoal) or above 0.85 (brighter than fresh snow) in linear light, because no measured material lies outside. The view belongs to [the measuring light page](measuring-light.md). In bytes, linear 0.03 is about 48 in sRGB and 0.85 is about 237, so the pure black 0 and the pure white 255 of a paint program are both out of range.

:::example[Metals and dielectrics in the look-dev furnace]
The look-dev project of the engine has a scene called `Furnace`: a uniform gray sky, no sun, tone mapping off, and two rows of five spheres at roughness 0, 0.25, 0.5, 0.75 and 1. The metal row has a base color of 0.95 and `Metallic` 1; the dielectric row has 0.5 and `Metallic` 0. The shot `lookdev.furnace` crops them as `metals` and `dielectrics`.

Predict the picture from the formulas. In a uniform environment of brightness $L$, the metal sends back about $0.95\,L$ at every roughness, because roughness changes where the reflection looks, not how much light it keeps. The dielectric sends back its diffuse share (about $0.96 \times 0.5\,L$) plus a 4 % mirror (about $0.04\,L$): near $0.52\,L$ at every roughness.

An environment with no detail should leave the spheres hardly changed from left to right, and a sphere that gets darker as roughness grows has lost energy. The model promises that roughness spreads light and never destroys it, and this scene tests the promise. The [energy page](energy.md) explains how Strata keeps it.
:::

The two rows of the opening picture, enlarged, show the same spheres under one small light: the metal row first, then the plastic row.

::figure{id=furnace-sweep crop=metals}

::figure{id=furnace-sweep crop=dielectrics}

### The glTF extensions the model follows

Strata maps a glTF material onto its fields one to one. The base factors, maps, the alpha mode and cutoff, `doubleSided`, the occlusion strength and the normal scale have direct fields. The extensions that Strata reads add the rest.

| glTF | Strata field |
| --- | --- |
| `KHR_materials_emissive_strength` | `EmissiveIntensity` |
| `KHR_materials_unlit` | `Unlit` |
| `KHR_texture_transform` | `UVTiling`, `UVOffset` (a rotation is skipped with a warning) |
| `KHR_materials_clearcoat` | The clear coat fields |
| `KHR_materials_transmission`, `KHR_materials_volume` | `Transmission`, `Thickness`, `AttenuationColor`, `AttenuationDistance` |
| `KHR_materials_ior` | `IOR` (1 to 3 are imported) |

The default `IOR` of 1.5 gives the 0.04 above, and [the reflectance page](reflectance.md) turns any other value into $F_0$. The lights extension, `KHR_lights_punctual`, creates lights, not materials; [the lights page](lights.md) covers it.

:::why[Why Strata did not invent its own model]
A model that matches glTF imports with no translation, reads the same in Blender and in other glTF viewers, and has a specification that an artist can find. The cost is the limits of glTF's core: the model has one reflectance per material and no tint of the head-on reflection of a dielectric.
:::

## What Strata's material model does not do

Each item here is a choice, and [the list of things Strata does not do](../appendix/not-in-strata.md) keeps the rest.

- **Shaders as assets, material graphs.** Strata has no shader asset type: shaders are compiled when the engine is built and embedded in it. A material only picks values for the one lighting model.
- **Non-photorealistic shading.** There is no toon, cel or hatching shading for objects. The only outlines the engine draws are the selection outline in the editor and the outlines of text.
- **Subsurface scattering, sheen, anisotropy, iridescence, specular maps and thickness maps.** The engine has none of these. Skin, cloth, brushed metal and soap film use the same model as stone, so an artist approximates them with it.
- **Parameters per entity.** Every entity that uses a material shares it, so Strata has no tint or hit flash on one object. A loaded material never changes while a game runs, and scripts have no call that changes a material. A game gives `MeshRenderer.Material` another asset: the Tetris sample sets a different material on a cell to show a piece, and a hit flash is a second material that the script swaps in.

## Common mistakes

| Mistake | Symptom | Fix |
| --- | --- | --- |
| A metal's color in a dielectric: base color gray, `Metallic` 0 | Steel looks like gray plastic, with a white 4 % highlight and no tinted mirror | Set `Metallic` 1 and put the metal's color in the base color |
| A dark metal: a metal painted in a near black base color | The metal reflects almost nothing and looks like a hole | Raise the base color toward the metal's real color |
| Albedo out of range: pure white or pure black base colors | Surfaces glow or vanish in the Albedo debug view, and exposure fights them | Keep luminance between 0.03 and 0.85 in linear light |
| Roughness taken for alpha: reading 0.5 as the highlight width | Highlights look wider than expected; alpha is the square, 0.25 | Treat the slider as perceptual: compare looks, not formulas |
| A data map imported as color | The roughness or normal looks wrong at mid values | Import data maps linear, with the right usage, and read the `material.get` warnings |
| Emission of 1 | The surface looks black beside a lit room | Raise `EmissiveIntensity` to hundreds of nits for a screen or lamp |
| An occlusion map expected to darken a lamp's light | Nothing changes under the lamp, because the map affects indirect light only | Use shadows for direct light and the occlusion map for creases |

## Summary

- A color and a specular power have no physical meaning, can add light and change from tool to tool, so a renderer cannot trust them.
- A surface is a dielectric or a metal, set by three numbers: base color, metallic and perceptual roughness, where the alpha of the highlight is the square of the roughness. The diffuse color is $(1 - m)\,c$ and the head-on reflectance blends 0.04 with the base color by $m$.
- A Strata material follows glTF's metallic-roughness model: factors multiply nine maps, base color and emission in sRGB and the rest linear, with roughness in green and metallic in blue; occlusion darkens only indirect light.
- A normal map stores X and Y of a direction in :term[tangent space]{id=tangent-space}, and the shader rebuilds Z and turns the direction into the world frame with $T$, $B$ and $N$.
- Pick Opaque, Mask or Blend by the surface, keep albedos between 0.03 and 0.85, and give emission in nits. Strata has no material graphs, toon shading, subsurface scattering, per-entity parameters or script changes to a material: a game swaps the material asset instead.

## Check yourself

1. A friend makes a steel door with a mid-gray base color and `Metallic` 0. Which description fits the result?

   - A. A good steel, because gray is the color of steel.
   - B. A gray plastic: a diffuse gray surface with a faint white highlight.
   - C. A mirror, because gray is bright.
   - D. A black surface, because metals have no diffuse color.

   :::answer{tests="three-numbers,phong-flaws"}
   B. At `Metallic` 0 the surface is a dielectric: its gray is diffuse, and its head-on reflectance is 0.04. A is wrong because steel's color belongs in the base color at `Metallic` 1. C and D describe what `Metallic` 1 does with a bright or dark base color.
   :::

2. The perceptual roughness is 0.6. What alpha does the highlight formula use?

   :::answer{tests="three-numbers"}
   The alpha is the square: $0.6 \times 0.6 = 0.36$. Using 0.6 directly is the common mistake of taking roughness for alpha.
   :::

3. A material has `OcclusionStrength` 0.25 and an occlusion map value of 0.2 at a texel, and the screen's occlusion there is 0.9. By what factor is the indirect light multiplied, and the light of the sun?

   :::answer{tests="strata-fields"}
   The blend is $1 + 0.25\,(0.2 - 1) = 0.8$, times 0.9 for the screen: 0.72 for indirect light. The sun's light is not multiplied, because direct light has shadows.
   :::

4. A normal map texel is (255, 128, 128). On a surface with $T = (1, 0, 0)$ and $N = (0, 0, 1)$, what normal does it give?

   :::answer{tests="normal-frame"}
   The X is $2 \cdot 255 / 255 - 1 = 1$ and the Y is about 0, so Z is $\sqrt{1 - 1} = 0$. The normal is $1\,T + 0\,B + 0\,N = (1, 0, 0)$: it lies flat along the tangent, the steepest lean a map can store.
   :::

5. A chain-link fence texture has an alpha of 0 in the holes and 1 on the wire. Which alpha mode, and why?

   :::answer{tests="alpha-albedo"}
   Mask with a cutoff of 0.5: holes are discarded in the depth, shadow and forward passes, so the fence casts a real shadow and needs no sorting. Blend would sort and shade the fence as a transparent surface.
   :::

6. A designer wants a character's armor to flash red when it is hit, by changing one material parameter in a script. Does Strata allow it?

   :::answer{tests="alpha-albedo"}
   No. A loaded material never changes and scripts have no call to change one. The script gives `MeshRenderer.Material` another material asset, one made red, and swaps back later.
   :::

## Exercises

1. **Basic.** Predict, then run: make a material with a white base color, and set `Metallic` to 0 and then to 1 with `material.set`. Say what each looks like under a plain sky before you look.

   ::::answer[Worked solution]{tests="three-numbers"}
   Create the material with `material.create`, then set it with `material.set`:

   ```json
   { "material": "Materials/Test.stmat", "properties": { "BaseColor": [1, 1, 1, 1], "Metallic": 1 } }
   ```

   At `Metallic` 0 the diffuse color is white and $F_0$ is 0.04: a dull white ball with a faint highlight. At `Metallic` 1 the diffuse color is $(0, 0, 0)$ and $F_0$ is $(1, 1, 1)$. The ball takes the color of what it reflects: under a plain sky it looks like the sky, and in a colored room it looks like the room. Roughness then blurs that image.
   ::::

2. **Medium.** Make a material with `material.create` from a base color map, a metallic-roughness map and a normal map, then switch its `AlphaMode` to Mask on a leaf texture with an `AlphaCutoff` of 0.5.

   ::::answer[Worked solution]{tests="strata-fields,alpha-albedo"}
   Create it with the three maps (texture paths of your project) in one command, and read the warnings it returns:

   ```json
   { "path": "Materials/Leaf.stmat", "properties": { "BaseColorMap": "Textures/Leaf.png", "MetallicRoughnessMap": "Textures/Leaf_mr.png", "NormalMap": "Textures/Leaf_n.png" } }
   ```

   A warning means a texture's import usage does not fit its slot, and `material.get` names the command that fixes it. Then run `material.set` with `{"material": "Materials/Leaf.stmat", "properties": {"AlphaMode": "Mask", "AlphaCutoff": 0.5}}`. Pixels of the leaf texture with an alpha below 0.5 disappear, in the shadow too. Because leaves are seen from both sides, also set `DoubleSided`.
   ::::

3. **Hard.** Write a program that turns six painted sRGB colors into linear luminance and flags those outside 0.03 to 0.85.

   ::::answer[Worked solution]{tests="alpha-albedo" solution="sketches/light-materials-albedo.cpp"}
   Convert each byte to linear light, weigh red, green and blue by 0.2126, 0.7152 and 0.0722, and compare the sum with the limits. Strata's constants of the same names are `c_AlbedoLow` and `c_AlbedoHigh`.

   :::question[Is the C++ below new to you?]
   The program uses a structure and loops ([programming 2](../basics/programming-2.md)), and calls such as `std::pow` and `std::printf` ([programming 3](../basics/programming-3.md)).
   :::

   Search the program for the function that converts one byte, the weighted sum and the two comparisons.

   ```cpp sketch="light-materials-albedo.cpp"
   // Flags base colors whose linear luminance lies outside the range of real materials.
   #include <cmath>
   #include <cstdint>
   #include <cstdio>

   struct Paint
   {
   	const char* Name;
   	uint8_t Red;
   	uint8_t Green;
   	uint8_t Blue;
   };

   constexpr float c_AlbedoLow = 0.03f;
   constexpr float c_AlbedoHigh = 0.85f;

   // The sRGB byte of a painted color, as linear light.
   float ToLinear(uint8_t byte)
   {
   	const float encoded = static_cast<float>(byte) / 255.0f;
   	if (encoded <= 0.04045f)
   		return encoded / 12.92f;
   	return std::pow((encoded + 0.055f) / 1.055f, 2.4f);
   }

   int main()
   {
   	const Paint paints[] = {
   		{ "Pure white", 255, 255, 255 },
   		{ "Fresh snow", 240, 240, 240 },
   		{ "Concrete", 128, 128, 128 },
   		{ "Red brick", 150, 70, 60 },
   		{ "Charcoal", 50, 50, 50 },
   		{ "Pure black", 0, 0, 0 },
   	};
   	for (const Paint& paint : paints)
   	{
   		const float luminance = 0.2126f * ToLinear(paint.Red) + 0.7152f * ToLinear(paint.Green) + 0.0722f * ToLinear(paint.Blue);
   		const char* verdict = "ok";
   		if (luminance < c_AlbedoLow)
   			verdict = "too dark";
   		else if (luminance > c_AlbedoHigh)
   			verdict = "too bright";
   		std::printf("%-11s luminance %.3f  %s\n", paint.Name, luminance, verdict);
   	}
   	return 0;
   }
   ```

   ```text output-of="light-materials-albedo.cpp"
   Pure white  luminance 1.000  too bright
   Fresh snow  luminance 0.871  too bright
   Concrete    luminance 0.216  ok
   Red brick   luminance 0.112  ok
   Charcoal    luminance 0.032  ok
   Pure black  luminance 0.000  too dark
   ```

   1. **Lines 20–23:** the sRGB curve has a short straight part near black and a power curve above it.
   2. **Line 38:** the luminance weights follow the eye's sensitivity: green counts most.
   3. **Lines 40–43:** the test compares the luminance with the two limits, in linear light, never with the byte.
   ::::

## Where it lives in Strata

- The material asset: `Material` and `MaterialProperties` in `Strata/src/Strata/Renderer/Material.h`; its properties, ranges and tooltips in `Strata/src/Strata/Renderer/Material.cpp`.
- The record sent to the GPU: `MaterialGPU::Build` and `MaterialGPU::GetTextureMaps` in `Strata/src/Strata/Renderer/MaterialData.cpp`.
- The shading: `Strata/shaders/Scene/Forward.frag.slang` (occlusion, roughness, alpha), `Strata/shaders/Include/MaterialTextures.slang` (the tangent frame) and `Strata/shaders/Include/Scene.slang` (`TransformUV`).
- The albedo limits: `c_AlbedoLow` and `c_AlbedoHigh` in `Strata/src/Strata/Renderer/SceneRenderData.h`.
- Import from glTF: `Strata/src/Strata/Asset/GltfImporter.cpp`.
- Commands: `material.create`, `material.get` and `material.set`; the look-dev scene `Tools/LookDev/LookDevScene.json`.

## Further reading

- Brent Burley, "Physically Based Shading at Disney" (SIGGRAPH 2012 course notes): the metallic and roughness parameters and the reasons for them (advanced).
- Brian Karis, "Real Shading in Unreal Engine 4" (SIGGRAPH 2013 course notes): metallic-roughness in a real-time engine, with the roughness squared (advanced).
- The Khronos glTF 2.0 specification, the section on materials: the model and the extensions Strata reads (intermediate).
- Bui Tuong Phong, "Illumination for Computer Generated Pictures" (1975): the specular power and its history (intermediate).
