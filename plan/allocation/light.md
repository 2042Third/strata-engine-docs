# Allocation: light

## `light/units-exposure` — Light by the numbers: radiometric and photometric units

**Covers.** The page opens with an experiment: the same scene lit by a 65,536 lux sun at exposure -16 and by a 1 lux sun
at exposure 0 gives the same image, so the numbers of light only mean something together with their units. Then
radiometry from zero: power, and the four quantities (flux, intensity, irradiance, radiance) on one diagram, each with
the solid angle or the area it is "per". Then photometry: the eye's weighting turns watts into lumens, and the four
photometric twins are lumen, candela, lux and nit. Worked conversions follow: a point light of P lumens has P / 4 pi
candela; a white diffuse surface under E lux has a luminance of E / pi nits; a spot light's candela is along its axis,
so a narrower cone does not brighten it, and P / (2 pi (1 - cos t)) keeps its lumens. The approaches engines use come
next (arbitrary "intensity", radiometric watts, photometric units as in Frostbite 2014, Unreal's physical units and
Filament), with a table of their costs. Strata's choice is photometric units on one scale with no hidden factor: lux for
the sun, candela for points and spots, nits for the sky, the ambient color and emission, read 1:1 from glTF; the page
shows the comment of `RendererComponents.h` that states it and the `Renderer.LightUnits` check. The reference table of
real values (sun, sky, overcast day, office, moon, lamp, candle, monitor) is placed on a log scale, and the sun-to-sky
ratio is defined as a quantity (its measurement is `light/measuring-light`'s). One paragraph and one diagram say why the
HDR target needs a pre-exposure: a 100,000 lux sun and a 1.3e9-nit sun disk do not fit half floats, and a power-of-two
scale fixes that exactly (the mechanism is `image/pre-exposure`'s). Both halves are `book.md`'s design decision "Light
is measured in real units, and a pre-exposure keeps the HDR values in range", stated once with its reason in a `:::why`
aside of about 80 words (`image/pre-exposure` names it and links back). One sentence says that 0.8.0's rectangle lights
have units of their own, which `light/area-lights` gives (a movable claim, read again at the pin move). The common
mistakes close the page: lumens taken for candela, a narrower cone expected to brighten, a 3 lux default sun mixed with
a real 120,000 lux one. The page's example is the Basic 3D template's sun with one lamp beside it; its exercise builds a
night scene from the reference values. Figures: no switch, so two diagrams (the units map and the half-float range) and
the equal pair of images. Afterwards the reader can convert between lumens, candela, lux and nits, read any light field
of Strata as a physical quantity, and say why a sunlit frame needs a pre-exposure.

**Leaves out.**

- Exposure, EV100, metering and the exposure key → `image/exposure`
- How the pre-exposure is chosen and kept exact → `image/pre-exposure`
- The light components, falloff and cones → `light/lights`
- Measuring luminance and the sun-to-sky ratio in a scene → `light/measuring-light`
- The units of rectangle lights → `light/area-lights`
- Lighting a scene with real values in the editor → `make/lighting`
- Linear and sRGB values and the half-float range as such → `basics/color`

**Fit.** `fits`: about 4,150 words against L (5,000). Radiometry and photometry taught from zero, with worked
conversions, take most of the page; it holds no code excerpt of its own.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-direct:278` | concept | home | Light as a quantity: radiometric and photometric units, the approaches engines use, Strata's choice and the mistakes |
| `render-direct:101` | feature | home | Photometric units on one scale with no hidden factor; the `Renderer.LightUnits` test that the tooltips name units |
| `render-direct:105` | feature | home | The reference values table (sun, sky, overcast, office, moon, lamp, candle, monitor), on a log scale |
| `render-direct:571` | rule | home | Every intensity has a unit, and nothing rescales it (imported glTF lights read 1:1) |
| `render-direct:573` | rule | home | A spot light's candela is along its axis; P / (2 pi (1 - cos t)) keeps its lumens |
| `render-direct:480` | figure | home | Diagram: the units map (lux on a surface, candela along a direction, nits off a surface), pi L = E, I = P / 4 pi, the reference values on a log scale |
| `render-direct:482` | figure | home | Diagram: the half-float range and a sunlit scene's values before and after a pre-exposure of 2^-19, for the paragraph on why |
| `render-direct:539` | figure | home | The same scene at 65,536 lux and exposure -16 and at 1 lux and exposure 0: equal images (the mirror of the units test) |
| `render-direct:640` | hands-on | home | Exercise: a night scene with a 0.2 lux moon, a 64 cd lamp (800 lm) and a 1 cd candle, exposure set from the reference table |
| `render-direct:695-698` | term | home | Lux, candela, nit and lumen (four glossary entries) |
| `render-direct:755` | term | home | The sun-to-sky ratio as a quantity |
| `new:26` | concept | home | The design decision "Light is measured in real units, and a pre-exposure keeps the HDR values in range", in the page's `:::why` aside (about 80 words): the shading computes photometric quantities on one scale with no factor between them, so real values and glTF lights work as they are and exposure maps them to the display; a sunlit frame's values do not fit the half-float target, so a power-of-two pre-exposure scales them exactly. Evidence: `Docs/DeveloperGuide.md:4005-4006`, `:5322-5323`, `:5335-5336`, `:5365-5372` |
| `render-image:97` | feature | home | The light units that feed exposure, as render-image lists them |
| `render-image:641` | term | home | Nit, lux and candela as render-image defines them (one glossary entry each, shared with `render-direct:695-697`) |
| `render-indirect:570-571` | term | home | Irradiance and radiance as radiometric quantities |
| `render-direct:433` | code | use | The comment of `RendererComponents.h:17-20` that gives each light's unit; the excerpt's home is `light/lights` |
| `render-direct:106` | feature | use | The Basic 3D template's 120,000 lux sun as the page's daylight example; its home is `make/lighting` |
| `render-direct:102` | feature | link | Exposure maps the scene's units to the display; its home is `image/exposure` |
| `render-direct:103` | feature | link | The pre-exposure, in one paragraph on why; its home is `image/pre-exposure` |
| `render-indirect:237` | concept | use | Radiance, irradiance and solid angle, as render-indirect lists them; the outline gives the concept to `light/reflectance` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Powers, logarithms and the exponential function | `basics/numbers` | must |
| Solid angle and the steradian | `basics/math-sphere` | must |
| Linear color and the luminance of an RGB value | `basics/color` | must |
| The half-float range | `basics/color` | must |
| The HDR target the scene renderer writes | `gpu/frame-tour` | must |
| Integrals as areas (flux summed over directions) | `basics/math-probability` | helps |
| Exposure and EV100 | `image/exposure` | helps |
| How the pre-exposure is chosen | `image/pre-exposure` | helps |

## `light/materials` — Strata's material model

**Covers.** The page starts from a picture: a row of spheres from roughness 0 to 1, once as a metal and once as a
dielectric. The problem is to describe how a surface reflects light with a few numbers an artist can set and a renderer
can trust. The naive answer, a color and a "shininess" (Phong's specular power), breaks: it has no physical meaning, it
adds light, and every tool means something else by it. The idea is two kinds of matter, dielectrics and metals, and
three numbers: base color, metallic and perceptual roughness (whose square is the alpha of the shading). The approaches
engines use follow (Phong and Blinn's specular power, specular-glossiness, metallic-roughness from Disney 2012 and
glTF), with a table. Strata's choice is glTF 2.0's metallic-roughness model, shown as the field list of
`MaterialProperties`: factors multiply the maps; the nine maps and their channels (base color and emission in sRGB, the
data maps linear, roughness in G and metallic in B); the occlusion map, lerp(1, map, `OcclusionStrength`), which darkens
only indirect light (image light, ambient, probes), multiplied with the screen's AO, never direct light, which has
shadows; normal maps and tangent space as a concept (color against data, the frame a normal map needs, shown off and on;
one sentence links `assets/models-gltf` for the tangents the importer makes when a glTF has none); one line each for
`DoubleSided` (no back-face culling in any pass, its shadow included; back faces flip the normal), `Unlit` (no lighting,
coat or glass), `NormalScale`, `UVTiling` and `UVOffset`; the alpha modes Opaque, Mask with its cutoff and Blend;
emission as a luminance in nits; plausible albedos (0.03 to 0.85); IOR as a field (its F0 is `light/reflectance`'s);
clear coat and transmission named as fields; and the glTF material extensions the model follows one to one (imported
lights are `light/lights`'). A section says what Strata does not do: no shader assets or material graphs, no
non-photorealistic shading, no subsurface scattering, sheen, anisotropy, iridescence, specular or thickness maps, and no
material parameters per entity (a tint, a hit flash) or material changes from scripts: a loaded material never changes,
and a game gives `MeshRenderer.Material` another asset. Common mistakes close it: a metal's color put in the diffuse,
albedos outside the range, roughness taken for alpha. The example is the look-dev furnace's metals and dielectrics.
Figures: the roughness and metallic sweep, the normal map off and on with a crop; the Albedo view is linked forward.
Exercises: predict, then run, a white base color at Metallic 0 and 1; a material made from three maps, then Mask on a
leaf texture; a sketch that flags linear albedos outside the range. Afterwards the reader can author a
metallic-roughness material with maps, choose an alpha mode and plausible values, and say which glTF material Strata
reads as it is.

**Leaves out.**

- How a material reaches the GPU: the record, the texture table and the XY decode → `light/material-data`
- The reflection equation, Fresnel and F0 from IOR → `light/reflectance`
- Clear coat, glass, blending and premultiplied alpha → `light/clearcoat-transmission`
- Texture formats, sRGB and BC5 → `assets/textures`
- Importing glTF models and their materials → `assets/models-gltf`
- The tangents the importer makes when a glTF has none → `assets/models-gltf`
- Imported glTF lights (`KHR_lights_punctual`) → `light/lights`
- Making materials in the editor → `make/materials`
- The Albedo debug view → `light/measuring-light`

**Fit.** `fits`: about 4,900 words against L (5,000). Two concepts taught from zero, the maps' table, four entries of
"What Strata does not do" and three exercises take the most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-direct:300` | concept | home | The metallic-roughness model: the problem, the approaches, Strata's choice, the mistakes |
| `render-direct:307` | concept | home | Textures as material inputs: color against data, normal maps and tangent space as a concept (Strata's code is `light/material-data`'s) |
| `render-direct:35` | feature | home | The metallic-roughness material and its fields, one line each for `DoubleSided` (drawn without back-face culling in every pass, its shadow included; back faces flip the normal), `Unlit` (skips lighting, the coat and glass), `NormalScale`, `UVTiling` and `UVOffset`; the occlusion map, lerp(1, map, `OcclusionStrength`), darkens only indirect light (image light, ambient, probes), multiplied with the screen's AO, never direct light, which has shadows (`Strata/shaders/Scene/Forward.frag.slang:284-290, 403`) |
| `render-direct:36` | feature | home | The alpha modes Opaque, Mask with `AlphaCutoff`, and Blend |
| `render-direct:37` | feature | home | Emission in nits: `EmissiveColor` times `EmissiveIntensity` times the map |
| `render-direct:39` | feature | home | The nine texture maps and their channels |
| `render-direct:49` | feature | home | The glTF material extensions the model follows; this page keeps the item's home, and its lights half (`KHR_lights_punctual`) is a `use` row on `light/lights`, which says what the import does |
| `render-direct:526` | figure | home | Sweep: spheres of roughness 0 to 1, metal and dielectric (`lookdev.furnace`, regions `metals` and `dielectrics`) |
| `render-direct:531` | figure | home | A normal map off and on, with a crop; the flat-normal case is `light/material-data`'s |
| `render-direct:671-673` | term | home | Albedo or base color, metallic, perceptual roughness |
| `new:1` | not-done | home | Shaders as assets and material graphs: shaders are compiled at build time and embedded. Evidence: `Strata/src/Strata/Asset/AssetTypes.h:14-31`, no shader type; `strata_add_shaders` at `Strata/CMakeLists.txt:80` |
| `new:2` | not-done | home | Non-photorealistic shading (toon, cel, ink outlines on objects); the only outlines are the selection outline and those of text. Evidence: `git grep -niE -e toon -e "cel[ -]shad" -e hatching 822a7a46 -- Strata/src Strata/shaders` finds nothing; `Strata/shaders/Overlay/Outline.frag.slang:5` is the selection outline |
| `new:3` | not-done | home | Subsurface scattering, sheen, anisotropy, iridescence, specular maps and thickness maps. Evidence: `git grep -ni subsurface 822a7a46 -- Strata/src Strata/shaders` finds nothing; `Docs/Roadmap.md:949` |
| `new:27` | not-done | home | Material parameters per entity, such as a tint or a hit flash, and material changes from scripts: a loaded material never changes, and a game gives `MeshRenderer.Material` another asset. Evidence: `Strata/src/Strata/Renderer/Material.h:87-90`; `git grep -ni material 822a7a46 -- StrataScriptCore/Include/StrataScript/ScriptABI.h` finds nothing; `Samples/Tetris/Scripts/TetrisBoard.cpp:365` |
| `new:28` | hands-on | home | Exercises: predict, then run: a white base color at `Metallic` 0 and 1 set by `material.set`, the metal predicted to take the color of what it reflects; a material made with `material.create` from a base color map, a metallic-roughness map and a normal map, then `AlphaMode` Mask on a leaf texture with `AlphaCutoff` 0.5; a sketch that turns base colors from sRGB to linear and flags those outside 0.03 to 0.85. Evidence: `StrataEditor/src/Editor/EditorAssetCommands.cpp:1115`, `:1147`; `Strata/src/Strata/Renderer/Material.cpp:41-42`; `Strata/src/Strata/Renderer/SceneRenderData.h:629-630` |
| `render-direct:434` | code | use | `MaterialProperties` as the model's field list; the excerpt's home is `light/material-data` |
| `render-direct:45` | feature | link | IOR as a field; F0 from IOR is `light/reflectance`'s |
| `render-direct:46-47` | feature | link | Clear coat and transmission as fields; their home is `light/clearcoat-transmission` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Luminance in nits | `light/units-exposure` | must |
| Textures: mips, color spaces, block compression | `assets/textures` | must |
| Linear and sRGB values | `basics/color` | must |
| Vectors and normals | `basics/math-vectors` | must |
| Bases and changes of space (tangent space) | `basics/math-bases` | must |
| Meshes with normals, tangents and texture coordinates | `gpu/geometry-pool` | helps |
| Assets and asset handles | `assets/handles-meta` | helps |
| Blending | `light/clearcoat-transmission` | helps |

## `light/reflectance` — How surfaces reflect light: the reflection equation and microfacets

**Covers.** The problem as the reader meets it: light arrives at a point from one direction; how much leaves toward the
eye? The page shows a rough and a smooth sphere under one light, and water, glass and diamond side by side. The naive
answer, Phong's cosine power, breaks: it is not reciprocal, it adds energy and it has no Fresnel. The idea: radiance in,
radiance out, and the BRDF as their ratio per unit of irradiance; the reflection equation for one light (outgoing
radiance = BRDF times incoming radiance times the cosine), and for light from every direction as an integral over the
hemisphere (the full rendering equation is `indirect/problem`'s). Lambert's diffuse term, albedo over pi, with the pi
derived. Microfacets: a rough surface as many tiny mirrors; the distribution D (GGX, also called Trowbridge-Reitz: how
roughness widens it and why it is normalized), the masking-shadowing term G (Smith, height-correlated, folded with the
denominator into the visibility V), and the Fresnel term F (Schlick's approximation), each derived as far as the primers
carry E1. Fresnel and F0: reflectance rises toward grazing angles; a dielectric's F0 comes from its IOR as ((n - 1) / (n
+ 1))^2 (water 0.02, glass 0.04, diamond 0.17), a metal's from its albedo; diffuse light gets what the specular leaves.
The approaches engines use (Phong, Blinn-Phong, Cook-Torrance with Beckmann or GGX, Disney's principled model) end in a
table. Strata's choice: GGX, height-correlated Smith, Schlick, Lambert weighted by (1 - F)(1 - metallic), F0 from the
IOR clamped to [1, 3] and stored in the record; a bridge to `light/brdf`. What the choice cannot do: single scattering
loses energy at high roughness (`light/energy`). The common mistakes: forgetting the cosine, dividing diffuse by pi
twice or never, an uncorrelated Smith term, water taken for 4%. Figures: the microfacet diagram (D, G and F panels, the
Fresnel curve for 1.33, 1.5, 2.42 and metals) and the IOR sweep. Exercises: F0 and Schlick's F computed in a sketch and
compared with `GetDielectricF0`; D times the cosine integrated to 1 at two roughnesses. Afterwards the reader can write
the BRDF from its three parts and say what each does.

**Leaves out.**

- The BRDF in shader code → `light/brdf`
- Energy lost to multiple scattering → `light/energy`
- The full rendering equation and indirect light → `indirect/problem`
- Radiometric quantities and units → `light/units-exposure`
- Highlights of sized sources → `light/area-lights`
- Image light and the split sum → `indirect/ibl`

**Fit.** `fits`: about 5,150 words against L (5,000). D, G and F derived from zero take the most; the two exercises add
about 500.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-direct:313` | concept | home | The reflection equation for a single light and the BRDF; the mistakes |
| `render-direct:319` | concept | home | Fresnel, F0 and the index of refraction; the mistakes |
| `render-direct:45` | feature | home | F0 from IOR in Strata: n clamped to [1, 3], stored in `MaterialData::Absorption.w`, metals from the albedo (the literal 0.04 is `light/material-data`'s rule) |
| `render-direct:484` | figure | home | Diagram: the microfacet BRDF's anatomy, D widening with roughness, the Fresnel curves |
| `render-direct:530` | figure | home | Sweep: water (1.33), glass (1.5) and diamond (2.42); the Showcase's puddles at 1.33 |
| `render-direct:674-681` | term | home | BRDF, microfacet, GGX, Smith visibility, Fresnel and Schlick, F0, IOR, Lambert |
| `render-direct:56` | feature | use | GGX, Smith, Schlick and Lambert as Strata's choice; the code is `light/brdf`'s |
| `render-indirect:237`, `render-indirect:241` | concept | home | Radiance, irradiance, solid angle and cosine weighting in use; the microfacet recap (GGX, Smith, Fresnel, F0, roughness against alpha) |
| `render-indirect:74` | feature | home | F0 from IOR as render-indirect lists it, taught with `render-direct:45` (passed to `light/material-data`, whose excerpt computes it) |
| `render-indirect:432` | figure | home | Dielectric spheres at IOR 1.33, 1.5 and 2.42 (`lookdev.ior`); with `render-direct:530`, one sweep |
| `render-indirect:578` | term | home | GGX and alpha ("alpha" gets an entry of its own); perceptual roughness links its one entry on `light/materials` (`render-direct:673`) |
| `new:29` | hands-on | home | Exercises: a sketch that computes F0 from the IOR for water, glass and diamond and Schlick's F at 60 and 85 degrees, compared with what `GetDielectricF0` returns (0.04 written out at 1.5); predict, then check with a sketch, that GGX's D times the cosine integrates to 1 over the hemisphere at roughness 0.2 and 0.6 while its peak falls. Evidence: `Strata/src/Strata/Renderer/MaterialData.cpp:51-59`; `Strata/shaders/Include/PBR.slang:33-57` |
| `render-indirect:470` | rule | use | Diffuse gets what specular leaves |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Radiance, irradiance and the light units | `light/units-exposure` | must |
| The material model | `light/materials` | must |
| Vectors, dot products, angles, sine and cosine | `basics/math-vectors` | must |
| Solid angle and integrals over the hemisphere | `basics/math-sphere` | must |
| Integrals as areas | `basics/math-probability` | must |
| Powers and the exponential function | `basics/numbers` | helps |

## `light/material-data` — From a material file to the shader: the material record and its textures

**Covers.** The job: turn a `Material` asset into the 144-byte record the shaders read, with texture table entries,
every frame and without waiting for a texture. One paragraph links `light/materials` for the problem (descriptor sets
per material against bindless tables). The map is the data flow diagram: `.stmat` JSON, `MaterialProperties`,
`MaterialGPU::Build`, `MaterialData`, the texture table entry, the bindless slot, `SampleMaterialTexture`. The contract:
a loaded material never changes; an edit (`material.set`, through `AssetEdit`) publishes a new object with
`ReplaceLoadedAsset`, which is how renderers learn of it; every reader sizes by `sizeof`, `MaterialData` stays 144 bytes
and the shader mirrors it by hand; a map that is still loading reads a neutral fallback. A toy version packs a CPU
struct into a GPU struct and an index table in 40 lines. The real code follows in data order: the `.stmat` document
first (a header with Format "Material" and Version 1, a newer version refused; properties by their reflected names, an
unknown or bad one a warning that keeps its default; the same list drives `material.set`, `material.get` and the
Inspector); the struct with glTF's packing of maps; `Build` with its fallbacks (white, black, the flat normal) and its
flags; the dielectric F0 from the IOR with the literal 0.04 at 1.5 and Beer's absorption from the attenuation color,
both stored in `Absorption`; the texture table entry (a 24-bit slot, a 7-bit sampler, the grayscale bit, the minimum
level of a fading texture); the tangent frame, the XY normal decode with Z reconstructed so that BC5 and RGBA8 shade
alike, and the back-face flip. "What went wrong before" is the flat normal: 0.7.0's 128/255 tilted every unmapped
surface by 0.3 degrees, and the fix stores (0.5, 0.5, 1) in half floats. Alternatives: descriptor sets per material,
direct bindless handles in the record, normal maps with Z. How it is tested: `MaterialTests.cpp`,
`GPU.SceneRenderer.Materials`. Changing it safely: a field changes the C++ record, the Slang mirror and the 144 bytes
together. Exercises: trace one `material.set` from the command to the record built again; store the flat normal as
128/255 once more and watch the test fail. Afterwards the reader can follow a material from its file to a texture sample
in the shader and add a field without breaking the layout.

**Leaves out.**

- What the fields mean for a surface → `light/materials`
- Bindless tables and registers in general → `gpu/binding`
- Mip streaming and the fade-in of new levels → `draw/mip-streaming`
- Mirrored instances and their flipped tangents → `draw/mirrors-camera-relative`
- F0 from IOR as physics → `light/reflectance`
- Beer's law → `light/atmosphere`
- The Inspector's material editor → `editor-ui/inspectors`
- Undo steps of asset documents → `editor/undo`

**Fit.** `fits`: about 4,350 words against L (5,000). The map, a toy, five excerpts (the `.stmat` document first) and
the flat-normal case take the most; the two exercises add about 500.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-direct:38` | feature | home | A loaded material never changes; edits publish a new object through `ReplaceLoadedAsset` |
| `render-direct:40-44` | feature | home | The 144-byte `MaterialData` and its flags, the neutral fallbacks, the exact flat normal, the texture table indirection, normal maps as XY |
| `render-direct:50` | feature | home | `material.create`, `material.set` and `material.get`: how an edit reaches the renderer (commands linked forward to `editor/commands`) |
| `new:30` | code | home | `Strata/src/Strata/Renderer/Material.cpp:95-140`: the `.stmat` document, the first box of the data flow: `Serialize` writes the header (Format "Material", Version 1) and every reflected property by name; `FromJson` refuses another format or a newer version, and an unknown or bad property gives a warning and keeps its default; the same property list drives `material.set`, `material.get` and the Inspector (`StrataEditor/src/Editor/EditorAssetCommands.cpp:1106-1110`) |
| `render-direct:434` | code | home | `Strata/src/Strata/Renderer/Material.h:23-63`: the whole model in one struct, glTF's packing of maps |
| `render-direct:435` | code | home | `Strata/src/Strata/Renderer/MaterialData.cpp:40-59`: Beer's absorption from a color and a distance; F0 from IOR with the bit-exact 1.5 case |
| `render-direct:436` | code | home | `Strata/src/Strata/Renderer/MaterialData.cpp:61-95`: `MaterialGPU::Build`, fallback textures and flags |
| `render-direct:437` | code | home | `Strata/shaders/Include/MaterialTextures.slang:47-65`: the tangent frame, the XY decode, the back-face flip |
| `render-direct:488` | figure | home | Diagram: the data flow of a material, with the memory layout of the 144 bytes |
| `render-direct:583-586` | rule | home | Read normal maps as XY; the flat normal must be exactly flat; F0 0.04 is written out at IOR 1.5 |
| `render-direct:597` | rule | home | Readers size `LightRecord` by `sizeof`; `LightData` stays 64 bytes and `MaterialData` 144 |
| `render-indirect:475` | rule | home | IOR 1.5 stays the literal 0.04, as render-indirect states it (the rule of `render-direct:586`) |
| `assets:165` | feature | home | The grayscale bit of a texture slot, sampled as (r, r, r, 1), and the XY normal decode, as the assets inventory lists them |
| `render-direct:531` | figure | use | The flat-normal crop of the normal-map figure, for "What went wrong before" |
| `new:31` | hands-on | home | Exercises: trace it yourself: one `material.set` of `Roughness` followed with a debugger from the command through `AssetEdit`'s save and `ReplaceLoadedAsset` to the GPU copy marking the material's slot and `RenderSceneGPU::BuildMaterial` calling `MaterialGPU::Build`; modify: the flat normal texture made with 128/255 again, and the case of `GPU.SceneRenderer.Materials` that reads a surface without a normal map fails by about 0.004 in each coordinate. Evidence: `StrataEditor/src/Editor/EditorAssetCommands.cpp:1147`; `StrataEditor/src/Editor/AssetEdit.cpp:90-107`; `Strata/src/Strata/Renderer/RenderSceneGPU.cpp:435-460`, `:584-585`; `Strata/src/Strata/Renderer/Renderer.cpp:111`; `StrataTests/src/Renderer/GPUSceneSpecularTests.cpp:229-270` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The material model | `light/materials` | must |
| Bindless textures, structured buffers and registers | `gpu/binding` | must |
| Shaders in Slang | `gpu/shaders` | must |
| Loading assets, "not loaded yet" and `ReplaceLoadedAsset` | `assets/loading` | must |
| BC5 normal maps with two channels | `assets/textures` | must |
| Struct layout in bytes and alignment | `basics/bytes` | must |
| Shifts and masks | `basics/numbers` | must |
| The fade-in of streamed mip levels | `draw/mip-streaming` | helps |
| F0 from IOR (the excerpt shows the formula, and the page says why 1.5 is written out) | `light/reflectance` | helps |
| Running an editor command | `editor/commands` | helps |
| Beer's law | `light/atmosphere` | helps |

## `light/brdf` — The forward shader and the BRDF in code

**Covers.** The job: the forward pass shades every visible surface once, from its material, the lights and the indirect
light, into the HDR target; culling the lights and drawing the shadows are other pages'. One paragraph links
`light/reflectance` and `gpu/frame-tour` for the problem. The map: the six variants compiled from one source (`Forward`,
`ForwardTransparent` and four `ForwardGlass` variants, by defines), the passes that feed the forward pass in frame order
(a timeline diagram on `gpu/frame-tour`'s stages: setup, the GPU-driven frame's culling, light culling and the clusters
inside the stage before them, which is `GPU.Setup` on the CPU path and `GPU.Cull` on GPU-driven frames, aerial
perspective, shadows, prepass, screen shadows, AO, then the opaque pass; the inventory's slip that puts them in
`GPU.Cull` alone is an erratum here), and the shading order within one pixel (material, shading normal, roughness
widening, sun, cluster lights, indirect light, coat, emission, aerial perspective, fog, glass, pre-exposure,
`SanitizeHDR`). The contract: opaque surfaces are shaded after the depth prepass with an EQUAL test and
`[earlydepthstencil]`, and discard only by the level-of-detail fade; the forward shader samples everything before any
discard (that rule and its Mesa and MoltenVK reason are `gpu/shaders`', linked), and this page adds the rule's second
half: derivatives only of the primitive's own interpolants and textures, in quad-uniform control flow, with explicit
levels in non-uniform flow, so that the CPU and GPU-driven paths shade alike; every HDR write goes through `SanitizeHDR`
(NaN to 0, clamped to 65,000), and the opaque pass writes alpha 1 by the HDR target's alpha convention (its why is
`image/taa`'s). A toy forward shader of 40 lines with one light comes next. The real code: GGX, the height-correlated
Smith term and Schlick in 25 lines; `EvaluateLightWeighted` with Lambert weighted by (1 - F)(1 - metallic); the minimum
roughness 0.045; specular aliasing from zero (a highlight narrower than a pixel sparkles; Toksvig, LEAN and CLEAN maps,
Kaplanyan-Tokuyoshi's screen-space variance) and `WidenRoughness`, capped at 0.18; the shader's main, which samples
everything before any discard. Figures: the timeline and shading-order diagrams, and specular anti-aliasing off and on
with a crop (the switch is a specification field for tests, so the figure takes the test's crops or a build with the
switch). Alternatives: a deferred G-buffer (linked), Toksvig maps, leaving sparkle to TAA. How it is tested:
`GPU.SceneRenderer.Materials` and `.Specular`, `Architecture.Shaders`. Changing it safely: both draw paths, the prepass
and the forward pass agree to the bit (`GPU.SceneRenderer.GPUDriven`). The exercises write a CPU reference of
`EvaluateLightWeighted` and compare it with a one-pixel render, and trace the six variants from the shader list to the
pass that picks each. Afterwards the reader can read `Forward.frag.slang` and `PBR.slang` and change a term safely.

**Leaves out.**

- The cluster loop and local shadows inside `ShadeLitSurface` → `light/many-lights`
- The BRDF table and energy compensation → `light/energy`
- Highlights of sized sources → `light/area-lights`
- The indirect light's inputs and gathers → `indirect/seam`
- Glass and the clear coat → `light/clearcoat-transmission`
- The lighting debug views' branches → `light/measuring-light`
- Derivatives before a discard, and why → `gpu/shaders`
- The sun's shadow comparisons at an explicit level → `light/sun-shadows-2`
- Why the HDR target's alpha has a convention → `image/taa`
- Forward against deferred shading, the depth prepass → `gpu/frame-tour`
- Mirrored instances and flipped tangents → `draw/mirrors-camera-relative`
- The HDR target and the post chain → `image/why-post`

**Fit.** `fits`: about 4,700 words against L (5,000). Four excerpts and the nine lines of `SanitizeHDR`, a toy, specular
aliasing from zero and the contract's rules take the most; the two exercises add about 500.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-direct:56-57` | feature | home | Cook-Torrance GGX with height-correlated Smith, Schlick and weighted Lambert; `c_MinRoughness` 0.045 |
| `render-direct:60` | feature | home | Specular anti-aliasing: the lobe widened by the normal's variance over the pixel, `MaterialParams.z` |
| `render-direct:64-67` | feature | home | The forward variants, the opaque pass with EQUAL and `[earlydepthstencil]`, the derivative rule's own half (derivatives only of the primitive's own interpolants and textures, in quad-uniform flow, explicit levels in non-uniform flow) with the forward shader's use of its first half (everything sampled before any discard; that half's home is `gpu/shaders`), `SanitizeHDR` |
| `render-direct:335` | concept | home | Specular aliasing and how to filter a highlight |
| `render-direct:438` | code | home | `Strata/shaders/Include/PBR.slang:33-57`: GGX D, correlated Smith V, Schlick F |
| `render-direct:439` | code | home | `Strata/shaders/Include/PBR.slang:126-148`: `EvaluateLightWeighted`, the whole direct-light BRDF and its weights |
| `render-direct:442` | code | home | `Strata/shaders/Include/PBR.slang:73-91`: `WidenRoughness`, specular anti-aliasing by the normal's variance |
| `render-direct:451` | code | home | `Strata/shaders/Scene/Forward.frag.slang:374-427`: the main, everything sampled before any discard, the coat and glass set up |
| `render-direct:495` | figure | home | Diagram: the frame timeline of the passes that feed the forward pass, on `gpu/frame-tour`'s stages, with light culling and the clusters marked inside the stage before them: `GPU.Setup` on the CPU path, `GPU.Cull` on GPU-driven frames (`Strata/src/Strata/Renderer/SceneRenderer.cpp:3289`, `:3343-3376`) |
| `render-direct:517` | figure | home | Diagram: the shading order within one pixel |
| `render-direct:533` | figure | home | Specular anti-aliasing off and on, a bumpy metal sphere, with a crop |
| `render-direct:582` | rule | home | Clamp HDR with `SanitizeHDR` |
| `render-direct:588` | rule | home | Derivatives only of the primitive's own interpolants and textures, in quad-uniform flow, so both draw paths shade alike; the rule's half "before any discard" and its Mesa and MoltenVK reason are linked to `gpu/shaders` (`render-core:587`) |
| `render-direct:654` | hands-on | home | Exercise: a CPU reference of `EvaluateLightWeighted` against a one-pixel GPU render |
| `new:32` | hands-on | home | Exercise (trace it yourself): find with a search where the six forward variants are declared, each by its defines, and where a draw's pass picks the pixel shader it runs (opaque, transparent, glass with or without velocity). Evidence: `Strata/CMakeLists.txt:89`, `:174-178`; `Strata/src/Strata/Renderer/SceneRenderer.cpp:301-302`, `:2449-2460` |
| `render-direct:687-688` | term | home | Specular aliasing; specular anti-aliasing (geometric) |
| `render-direct:838` | open | home | The specular anti-aliasing figure needs the test's crops or a build with `SceneRendererSpecification::SpecularAntiAliasing`; the writer settles which |
| `render-direct:204` | feature | use | The area's GPU stages in frame order, for the timeline; their home is `gpu/frame-tour`; light culling and the clusters are timed in `GPU.Cull` only on GPU-driven frames (`new:33`) |
| `new:33` | erratum | home | `plan/inventory/render-core.md:162` and `plan/inventory/render-direct.md:205` time light culling and the light clusters in `GPU.Cull`, and the exercise of `render-direct.md:658` measures them there: `GPU.Cull` starts only on GPU-driven frames, and the light passes recorded after it are timed in `GPU.Cull` there and in `GPU.Setup` on frames of the CPU path. Evidence: `Strata/src/Strata/Renderer/SceneRenderer.cpp:3289`, `:3343`, `:3360`, `:3365-3376` |
| `render-image:35` | feature | use | The HDR alpha convention, one sentence: opaque writers write alpha 1 and blended ones multiply it by 1 - a; the why is `image/taa`'s |
| `render-direct:68` | feature | link | Mirrored instances; their home is `draw/mirrors-camera-relative` |
| `render-indirect:472` | rule | home | The derivative rule as render-indirect states it (`render-direct:588`) |
| `render-image:30` | feature | home | `SanitizeHDR` as render-image lists it (`render-direct:67`) |
| `render-image:397` | code | home | `Strata/shaders/Include/Common.slang:49-57`: `SanitizeHDR`, NaN to 0 and overflow to 65,000, and why neither may reach an HDR target |
| `render-image:525` | rule | home | Every HDR writer clamps with `SanitizeHDR` (the rule of `render-direct:582`) |
| `render-image:640` | term | home | `SanitizeHDR` |
| `render-core:603` | rule | home | HDR writers clamp with `SanitizeHDR`, as render-core states it (`render-direct:582`) |
| `render-indirect:71` | feature | home | GGX, height-correlated Smith and Schlick as render-indirect lists them (`render-direct:56`) |
| `render-indirect:73` | feature | home | Specular anti-aliasing as render-indirect lists it (`render-direct:60`) |
| `render-indirect:265` | concept | home | Specular aliasing and geometric specular anti-aliasing, with the derivative rule |
| `render-indirect:429` | figure | home | Specular anti-aliasing off and on; with `render-direct:533`, one figure |
| `render-scene:477` | rule | home | Shading must not depend on draw order or instance order: this page is the home of shading independent of draw order |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The reflection equation, D, G and F | `light/reflectance` | must |
| The material record and the texture table | `light/material-data` | must |
| Sampling, aliasing and filtering | `basics/signals` | must |
| Shaders in Slang, entry points and defines | `gpu/shaders` | must |
| The depth prepass, EQUAL and forward against deferred | `gpu/frame-tour` | must |
| Pixel quads and screen-space derivatives | `gpu/how-a-gpu-frame-works` | must |
| Derivatives and discard in shaders | `gpu/shaders` | must |
| The half-float range | `basics/color` | must |
| Pipelines and their variants | `gpu/binding` | helps |
| The GPU-driven path's draw order | `draw/gpu-driven` | helps |
| Level-of-detail fades | `draw/lod` | helps |
| Writing a GPU test | `gpu/first-triangle` | helps |

## `light/energy` — Keeping the energy: directional albedo, the BRDF table and the white furnace

**Covers.** The job: a white surface under a uniform white sky stays white at every roughness. This page carries the
full section on the problem: single-scattering GGX loses light at high roughness, so rough metals look dull and tempt
artists to paint wrong albedos; the approaches are Kulla-Conty 2017, Fdez-Aguera 2019 and Filament's factor 1 + F0 (1 /
E - 1), with their costs. The idea: the directional albedo E, the share of light a lobe reflects for one view direction,
and the BRDF table over (NoV, roughness) that holds the scale and bias of F0; this is the second half of the split sum
(its prefiltered half is `indirect/ibl`'s), which the forward pass reads at SRV t5. The map: the table is computed once
by `BRDFLut.comp` and read by `ShadeLitSurface`, glass and the coat. A toy computes E for one (NoV, roughness) by Monte
Carlo on the CPU. The real code: `BRDFLut.comp` importance-samples GGX with the Hammersley pattern, and the probability
density cancels D; `GetSpecularEnergy` and its use in `ShadeLitSurface`, applied to direct and image light alike;
diffuse keeps 1 - F. The white furnace: a uniform 1-nit sky, where an energy-conserving white surface shows 1
everywhere; the furnace tests (metals, dielectrics by IOR, direct specular, coat over metal) and the look-dev shot
`lookdev.furnace`; the rule that shading changes are checked with the furnace and the debug views, not by eye. Figures:
the plot of E and of the factor 1 / E, and the furnace rows without and with compensation. How it is tested:
`GPU.SceneRenderer.Lighting` (the furnace cases). Changing it safely: AGENTS.md's "light keeps its energy". Exercises:
re-derive the table in C++ for a few points; turn the compensation off locally and measure the loss per roughness; trace
the table from where it is made once to its three readers. Afterwards the reader can derive the BRDF table, explain the
compensation, and test a shading change with the furnace.

**Leaves out.**

- The prefiltered environment, the split sum's other half → `indirect/ibl`
- The look-dev harness itself → `engineering/look-dev`
- Monte Carlo integration from zero → `basics/math-probability`
- The coat's lobe and its compensation → `light/clearcoat-transmission`
- The horizon fade of image light → `indirect/ibl`

**Fit.** `over`: about 4,400 words against M (3,000). The importance-sampling derivation, three excerpts (the furnace
test among them), two figures and three exercises pass M's top; by S2 the page takes L (5,000), whose range holds it.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-direct:58-59` | feature | home | The split-sum BRDF table (scale and bias of F0 by NoV and roughness, the same Smith term) and the multiple-scattering compensation |
| `render-direct:324` | concept | home | The split sum as far as the BRDF table, which also drives the compensation |
| `render-direct:329` | concept | home | Energy conservation and multiple scattering; the mistakes |
| `render-direct:440` | code | home | `Strata/shaders/Include/PBR.slang:59-71`: `GetSpecularEnergy`, with its use at `Strata/shaders/Scene/Forward.frag.slang:211-218` |
| `render-direct:441` | code | home | `Strata/shaders/IBL/BRDFLut.comp.slang:20-49`: importance-sampled GGX, the density that cancels D |
| `render-direct:486` | figure | home | Diagram: E(NoV, roughness) from the table and the factor 1 / E |
| `render-direct:528` | figure | home | The white furnace without and with compensation (`lookdev.furnace`, Tonemapper None) |
| `render-direct:591` | rule | home | Check shading changes with the white furnace and the debug views, not by eye |
| `render-direct:655-656` | hands-on | home | Exercises: re-derive the table in C++; measure the loss with the compensation off |
| `new:34` | hands-on | home | Exercise (trace it yourself): find with a search where the BRDF table is made once (its size, samples and the dispatch of `BRDFLut.comp`) and every reader of `GetSpecularEnergy`: the surface in `ShadeLitSurface`'s setup, the coat's lobe and glass. Evidence: `Strata/src/Strata/Renderer/SceneRenderer.cpp:60-61`, `:656-668`; `Strata/shaders/Scene/Forward.frag.slang:218`, `:225`, `:368` |
| `render-direct:683-686` | term | home | BRDF table, directional albedo, energy compensation, white furnace test |
| `render-direct:682` | term | link | The split sum; its home is `indirect/ibl` |
| `render-indirect:59` | feature | home | The BRDF table (128 x 128 RG16F, 512 samples) as render-indirect lists it; the table of `render-direct:58` |
| `render-indirect:72` | feature | home | The compensation as render-indirect lists it (`render-direct:59`) |
| `render-indirect:194-195` | feature | home | The white furnace as tests (`GPU.SceneRenderer.Lighting`) and as the look-dev shot `lookdev.furnace` |
| `render-indirect:259` | concept | home | Energy conservation and the white furnace test; the mistakes |
| `render-indirect:338` | code | home | `Strata/shaders/IBL/BRDFLut.comp.slang:20-49`: the excerpt of `render-direct:441`, shown once |
| `render-indirect:342` | code | home | `Strata/shaders/Include/PBR.slang:59-71`: the excerpt of `render-direct:440`, shown once |
| `render-indirect:343` | code | home | `StrataTests/src/Renderer/GPUSceneLightingTests.cpp:860-914`: the white furnace as a test, copper's expected value from the formula |
| `render-indirect:384`, `render-indirect:427` | figure | home | The energy-loss chart and the furnace pair; with `render-direct:486` and `render-direct:528`, one chart and one pair |
| `render-indirect:467-470` | rule | home | Light keeps its energy, checked with the furnace; diffuse gets what specular leaves |
| `render-indirect:546` | hands-on | home | Exercise: a CPU white furnace, E(NoV, r) plotted and the compensation derived, against `BRDFLut.comp` |
| `render-indirect:587` | term | home | Energy compensation and multiple scattering ("multiple scattering" qualified: `render-direct:749` is the atmosphere's) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The BRDF in code: GGX, Smith, `EvaluateLightWeighted` | `light/brdf` | must |
| Compute shaders and dispatches | `gpu/compute` | must |
| Monte Carlo integration and the Hammersley pattern | `basics/math-probability` | must |
| Integrals over the hemisphere | `basics/math-sphere` | must |
| Writing a GPU test and reading pixels back | `gpu/first-triangle` | must |
| The split sum's prefiltered half | `indirect/ibl` | helps |
| The look-dev harness | `engineering/look-dev` | helps |

## `light/measuring-light` — Measuring light: the debug views and their statistics

**Covers.** The job: show light as numbers, so that a scene is judged by measurement and not by eye on one monitor. The
problem and its approaches in one section: false-color luminance, albedo validation, furnace tests, texel-density views.
The map: a view is chosen per renderer (`SceneLightingView`, through `MaterialParams.y`), the forward pass branches on
it, an overlay draws the legend's colors, and a compute pass counts every pixel into histograms that come back through a
ring of readbacks, never waited for. The views: Lighting (every lit surface white, through the scene's exposure),
AmbientOcclusion and Indirect (one sentence each says what ambient occlusion and indirect light are and links
`indirect/problem`), Luminance (EV100 bands, log2 of nits plus 3, from 5 to 17) and Albedo (values outside 0.03 to 0.85
marked); the value views are written without pre-exposure, because 2^-19 would make an albedo of 0.03 subnormal. The
statistics: quarter-EV histograms of surfaces and background, value bins, percentiles, and the illuminance of the sun
and of the sky on flat ground with their ratio (the sky's is pi times the irradiance map at +Y; one sentence on the sky
as a light links `light/sky`). Access: the Scene view's debug view chip, `viewport.capture {debugView}` and
`viewport.setSettings`, whose result holds `debugView.lighting`; each command is a complete line with one sentence and a
link forward to `editor/commands`. The code: the enum of views, the stats shader's group-shared histograms, and what
comes back (`LightingViewStats`). A toy counts EV100 over an image on the CPU. Figures: the Lighting, Indirect,
Luminance and Albedo views of one scene; the luminance view of a sunlit street and an interior; the Albedo view marking
a black and a white cube. How it is tested: `GPU.SceneRenderer.LightingViews`. Changing it safely: a new view keeps the
enum in the order of `Scene.slang`'s constants, and value views stay unexposed. The exercises make a material set (rough
copper, polished gold, wet asphalt) and audit it in the Albedo view, add a lighting view end to end (the enum, the
forward branch, the overlay, the editor's names, a test), and trace one frame's statistics from the stats pass to a
command's result. The word "debug view" is said in one sentence and links its glossary entry on `gpu/debugging`. The
shadows view is `light/sun-shadows-1`'s, the AO view `indirect/ao`'s, the GI views `indirect/gi-cascades`'. Afterwards
the reader can use every lighting view and read its statistics from the editor and from a command.

**Leaves out.**

- The shadows view → `light/sun-shadows-1`
- The ambient occlusion view → `indirect/ao`
- The GI views (voxels, gi, open, probes) → `indirect/gi-cascades`
- The list of every debug view and how views work → `gpu/debugging`
- EV100, metering and exposure → `image/exposure`
- The white furnace → `light/energy`
- The look-dev harness → `engineering/look-dev`
- The legends as the Scene view draws them → `editor-ui/scene-view`

**Fit.** `over`: about 4,450 words against M (3,000). Five views, their statistics, the agent's access, three excerpts
and three exercises pass M's top; by S2 the page takes L (5,000), whose range holds it.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-direct:422` | concept | home | Measuring lighting instead of eyeballing it; the mistake of tuning exposure to fix wrong albedo |
| `render-direct:161` | feature | home | The sun-to-sky ratio as the lighting views report it (`LightingViewStats`) |
| `render-direct:178-180` | feature | home | The five lighting views, their statistics through a ring of readbacks, editor and agent access |
| `render-direct:540-541` | figure | home | The Luminance view of a sunlit street and an interior; the Albedo view marking out-of-range albedos |
| `render-direct:580` | rule | home | Value views are written without pre-exposure |
| `render-direct:641` | hands-on | home | Exercise: a material set audited in the Albedo view |
| `new:35` | hands-on | home | Exercise (trace it yourself): follow one frame's statistics with a search or a debugger from `LightingViewStats.comp`'s buffer through the ring of readbacks (`ResolveLightingViewStats`) to the `debugView.lighting` result of `viewport.setSettings`, and count the frames they come back after. Evidence: `Strata/src/Strata/Renderer/SceneRendererLightingView.cpp:18-19`, `:223`, `:257`; `StrataEditor/src/Editor/EditorViewportCommands.cpp:277` |
| `render-direct:757` | term | link | Debug view: said in one sentence; its one glossary entry is on `gpu/debugging`, beside `render-scene:182`, which lists every view |
| `new:4` | code | home | `Strata/src/Strata/Renderer/SceneRenderer.h:322-336`: `SceneLightingView`, what each view shows |
| `new:5` | code | home | `Strata/shaders/Effects/LightingViewStats.comp.slang:25-87`: every pixel counted in group-shared histograms, then added to the buffer; the sky's light on a horizontal surface |
| `new:6` | code | home | `Strata/src/Strata/Renderer/SceneRenderer.h:364-387`: `LightingViewStats`, the percentiles and the sun and sky illuminance that come back frames later |
| `render-direct:177` | feature | link | The shadows view; its home is `light/sun-shadows-1` |
| `render-indirect:189-193` | feature | home | The lighting views, value views without pre-exposure, statistics, history and exposure under a view, editor and agent access, as render-indirect lists them |
| `render-indirect:417`, `render-indirect:461` | figure | home | Diagram: the statistics pipeline (histogram pass, ring of readbacks, percentiles); the Lighting, Indirect, Luminance and Albedo views of one scene |
| `render-image:101` | feature | home | The Luminance view for judging exposure |
| `render-indirect:326` | concept | home | Measuring light by numbers as render-indirect lists it (with `render-direct:422`) |
| `render-indirect:548` | hands-on | home | Exercise: a new lighting view end to end (the enum, `ST_LIGHTING_VIEW_*`, the forward branch, the overlay, the editor's names, a test) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Luminance in nits and illuminance in lux | `light/units-exposure` | must |
| The forward shader and its value branches | `light/brdf` | must |
| Plausible albedos | `light/materials` | must |
| Readbacks that never wait | `gpu/readback-timing` | must |
| Overlay passes | `gpu/debug-drawing` | must |
| Group-shared memory and atomics | `gpu/compute` | must |
| Percentiles | `core/profiling` | helps |
| EV100 | `image/exposure` | helps |
| The pre-exposure | `image/pre-exposure` | helps |
| Debug views and the `debugView` parameter | `gpu/debugging` | helps |
| Running an editor command | `editor/commands` | helps |
| The sky as a light | `light/sky` | helps |
| Indirect light and ambient occlusion | `indirect/problem` | helps |

## `light/lights` — Lights: the sun, points and spots

**Covers.** The job: turn light components into what the forward pass shades with: one sun in the frame constants, point
and spot lights as records of the render scene. This page carries the full section on the problem: modelling the sun and
lamps cheaply, with punctual lights whose inverse-square falloff is windowed to a range (Karis 2013), against the legacy
constant, linear and quadratic attenuation. The components as plain data, with the unit of every field in its comment:
`DirectionalLightComponent` (lux, shadows, Angular Diameter, cascade fields), `PointLightComponent` (candela, range,
source radius, shadows) and `SpotLightComponent` (as the point light, with inner and outer half angles and defaults of
its own, 20 cd and 15 m against the point light's 10 cd and 10 m, which the page takes from the generated components
table and the excerpt), shining along the entity's -Z. One sun per frame: the brightest active directional light shines,
the others are ignored. The windowed falloff and the smooth cone (t squared between the cosines) in code; the range is a
culling bound, not a brightness. Light records: one 96-byte record per component, kept from EnTT signals and transform
changes with a change log the GPU copy follows; inactive lights keep a record marked not drawn; `MakeRecord` refuses
non-finite values; the spot's bounding sphere has two cases around 45 degrees; lights are placed where the scene draws
their entity (drawn transforms); `LightData` is 64 bytes, camera-relative, with the shadow slot and the source radius in
`SpotAngles`. The rule that a direct write to a light field must signal, like a transform write. Picking the sun and
filling the frame constants in code. Preview lighting: an editor view of a scene with no light gets a preview sun and
the default procedural sky. Imported lights: the glTF importer reads `KHR_lights_punctual` 1:1 (candela, lux), gives a
light without a glTF range 10 sqrt(I) meters, scales ranges with the model's Scale and clamps spot cones to 1 to 89
degrees. What Strata does not do here: no light cookies, IES profiles, light linking or lighting channels; every light
lights every surface in its range. A toy turns a list of lights into a uniform array. Figures: a spot's inner and outer
angles and a point light's range window as a sweep; preview lighting in the Scene view against the Game view.
Alternatives: one pass per light, several shadowed suns. How it is tested: the spot cone and units cases of
`GPU.SceneRenderer.Lighting`, `RendererComponentsTests.cpp`. Changing it safely: a new light type reaches the record,
`LightData`, the clusters and `ShadeLitSurface`; readers size `LightRecord` (96 bytes) by `sizeof`, and `LightData`
stays 64 bytes, mirrored by hand in `Lights.slang`. The exercises add a "lumens" helper for spot lights with a unit
test, and trace a light's change from its component to the record the GPU copy reads. Afterwards the reader can place
and tune lights and follow a component into a record and the frame constants.

**Leaves out.**

- The units of light → `light/units-exposure`
- Culling lights and assigning them to clusters → `light/many-lights`
- Source radius and sized highlights → `light/area-lights`
- Shadows of lights → `light/shadow-basics`
- The render scene's records and change logs in general → `draw/render-scene`
- The sky light and the preview sky → `light/sky`
- Interpolating fixed steps → `world/interpolation`
- The `ImportLights` setting of a glTF import → `assets/models-gltf`
- Placing lamps in a game → `make/lamps`

**Fit.** `fits`: about 4,550 words against L (5,000). Four excerpts and the record's contract take the most. Phase B
reads again the section on light components and records (W8r): what 0.8.0's rectangle lights add to the components,
`LightRecord` and `LightData`, and whether the entry on light cookies, IES profiles, light linking and lighting channels
still holds.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-direct:74-84` | feature | home | The three light components, one sun per frame, the falloff and the cone, light records, the spot's bounding sphere, drawn transforms, `LightData`, preview lighting; the spot light's defaults are its own (20 cd and 15 m against the point light's 10 cd and 10 m, `Strata/src/Strata/Renderer/RendererComponents.h:53-54`, `:69-70`), and the page takes them from the generated components table and the excerpt, not from the item |
| `render-direct:341` | concept | home | Light sources: directional, point, spot; attenuation and range; the mistakes |
| `render-direct:433` | code | home | `Strata/src/Strata/Renderer/RendererComponents.h:17-78`: the light components as plain data with units in comments, defaults and range constants |
| `render-direct:444` | code | home | `Strata/shaders/Include/PBR.slang:194-207`: windowed inverse-square falloff and the spot cone |
| `render-direct:445` | code | home | `Strata/src/Strata/Renderer/RenderLights.cpp:44-85`: a light record, non-finite values refused, the spot's bounding sphere |
| `render-direct:446` | code | home | `Strata/src/Strata/Renderer/SceneRenderer.cpp:2557-2601`: picking the sun, the preview sun, the frame constants from the components |
| `render-direct:537` | figure | home | Sweep: a spot's inner and outer cone angles on a wall; a point light's range window |
| `render-direct:565` | figure | home | Preview lighting: an unlit scene in the Scene view against the Game view |
| `render-direct:595` | rule | home | Light records are kept from signals: a direct write to a light field must signal |
| `render-direct:616` | rule | home | Only one directional light shines, and only the first active sky light, height fog and post process apply |
| `render-direct:657` | hands-on | home | Exercise: a spot light "lumens" helper that converts to candela for a cone, with a unit test |
| `new:36` | not-done | home | Light cookies (projected textures), IES profiles, light linking and lighting channels: every light lights every surface in its range. Evidence: `git grep -niE -e cookie -e "light ?channel" -e "light ?layer" -e "light ?mask" -e "light ?link" 822a7a46 -- Strata/src Strata/shaders` finds only the DLL-directory cookie of `Strata/src/Platform/Windows/WindowsDynamicLibrary.cpp:21-36` and the socket notifier's cookie of `Strata/src/Platform/Windows/WindowsSocket.cpp:24-26`, `:549-571`; `git grep -nw IES 822a7a46 -- Strata/src Strata/shaders` finds nothing |
| `new:37` | hands-on | home | Exercise (trace it yourself): a point light's `Intensity` changed by `component.set`, followed with a debugger from the EnTT update signal that `RenderLights` connects, through the queued record built again by `MakeRecord` in `Sync`, to the change log that the GPU copy reads with `GetChanges`. Evidence: `Strata/src/Strata/Renderer/RenderLights.cpp:44-85`, `:91-98`, `:276`, `:315-340` |
| `render-direct:704-706` | term | home | Punctual light, range, inner and outer cone angle |
| `render-direct:710` | term | home | Light record |
| `render-direct:756` | term | home | Preview lighting |
| `render-indirect:62` | feature | home | Preview lighting as render-indirect lists it (`render-direct:84`) |
| `editor-core:697` | term | home | Preview lighting as the editor's inventory defines it (one glossary entry with `render-direct:756`) |
| `render-direct:49` | feature | use | The lights half of the glTF extensions, about 80 words: `KHR_lights_punctual` read 1:1, a light without a glTF range gets 10 sqrt(I) meters, ranges scale with the model's Scale, spot cones are clamped to 1 to 89 degrees (`Strata/src/Strata/Asset/GltfImporter.cpp:1828-1863`); the item's home is `light/materials`, and `assets/models-gltf` keeps the `ImportLights` setting |
| `render-direct:597` | rule | use | The rule's light half, under "Changing it safely": readers size `LightRecord` (96 bytes) by `sizeof`, and `LightData` stays 64 bytes, mirrored by hand in `Lights.slang` (`Strata/src/Strata/Renderer/SceneRenderData.h:259`, `:275`); the rule's home, with its material half, is `light/material-data` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Lux and candela | `light/units-exposure` | must |
| `EvaluateLight` and the forward shader | `light/brdf` | must |
| The render scene's records and change logs | `draw/render-scene` | must |
| Drawn transforms between fixed steps | `world/interpolation` | must |
| Components as registered data with properties | `world/reflection` | must |
| EnTT views | `world/ecs` | must |
| EnTT signals | `world/scene-graph` | must |
| The transform contract and change signals | `world/scene-graph` | must |
| Bounding spheres | `basics/math-geometry` | must |
| Camera-relative positions subtracted in double | `draw/mirrors-camera-relative` | must |
| The editor's Scene and Game views | `start/first-game` | helps |

## `light/many-lights` — Many lights: culling and clustered forward shading

**Covers.** The job: give each pixel the few lights that reach it, out of thousands in view. The problem and the
approaches (this page carries the full section; forward against deferred is `gpu/frame-tour`'s): one pass per light,
tiled forward shading with 2D tiles, clustered shading with 3D froxels (Olsson 2012, Doom 2016), with a table of their
costs. The map follows a light from a component change to the cluster lists (the record-flow diagram), with the CPU
branch beside the GPU one. The CPU path: frustum culling of each record's bounding sphere, ranking by relevance (lights
around the camera first, then the projected size r / (d - r)), a cap at `MaxLights` (4,096) with one warning, and the
upload camera-relative with the subtraction in double. The GPU path: `LightCull.comp` tests every record against the
camera-relative frustum and `LightCompact.comp` packs the visible ones in record order, with no cap. The clusters: 16 x
9 x 24 froxels with exponential depth slices, at most 256 lights per cluster, one thread per cluster testing spheres
against the cluster's box through shared memory (the froxel-grid diagram, with the buffer's stride of 257). An advanced
box shows how a full cluster on the GPU path keeps the most relevant lights: a bisection over the ordered bits of the
relevance. The forward loop: the pixel's cluster from its screen tile and log depth, then per light the range test, the
attenuation, the local shadow, the source's lobe and `LightSurface`. The statistics (`CulledLights`, `DroppedLights`,
the GPU counts). A toy assigns lights to 2D tiles on the CPU. The figure is a grid of 1,000 small point lights in the
Lighting view. Alternatives: deferred and tiled deferred, per-object light lists. How it is tested: clustered against
brute force, culling and relevance, the GPU path beyond `MaxLights`. Changing it safely: change the CPU and GPU paths
together, keep the cluster stride in sync. The exercises change the grid to 32 x 18 x 32 and measure the light passes
and `GPU.Opaque` (the light passes are timed in `GPU.Cull` on GPU-driven frames and in `GPU.Setup` on the CPU path, so
the exercise names the path it forces; the inventory's slip is the erratum of `light/brdf`), and trace one pixel's
cluster and the lights it loops over. Afterwards the reader can explain clustered shading, follow the four excerpts and
measure what the grid costs.

**Leaves out.**

- What a light record holds → `light/lights`
- Forward against deferred shading → `gpu/frame-tour`
- Frustum tests in general → `draw/bounds-culling`
- The GPU-driven path and compaction in general → `draw/gpu-driven`
- The shadow slots of shadowed lights → `light/local-shadows`
- The source's lobe → `light/area-lights`
- Measuring GPU time → `gpu/readback-timing`

**Fit.** `fits`: about 4,650 words against L (5,000). Four excerpts, two diagrams and the advanced box take the most.
Phase B reads again the section on the forward light loop (W8r): what 0.8.0's rectangle lights and the local-lights
stream change in it.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-direct:90-95` | feature | home | The CPU and GPU light paths, clustered assignment, the overflow that keeps relevance, the forward cluster loop, the statistics |
| `render-direct:353` | concept | home | Many lights: tiled against clustered shading; the mistakes (linear slices, a cap thought to drop random lights) |
| `render-direct:447` | code | home | `Strata/src/Strata/Renderer/SceneRenderer.cpp:2612-2697`: CPU light culling, ranking, the cap, the camera-relative upload in double |
| `render-direct:448` | code | home | `Strata/shaders/Include/Clusters.slang:4-52`: log depth slices, the cluster index, relevance (the inventory's 49-78 is not at the pin: the file has 54 lines) |
| `render-direct:449` | code | home | `Strata/shaders/Scene/LightClusters.comp.slang:42-101`: building the cluster lists with shared memory; 103-189, the relevance bisection, as an advanced box |
| `render-direct:450` | code | home | `Strata/shaders/Scene/Forward.frag.slang:198-279`: `ShadeLitSurface`, the sun with its mask and the cluster loop with local shadows and source lobes |
| `render-direct:490` | figure | home | Diagram: the light record flow from a component change to the cluster lists, with the CPU branch |
| `render-direct:493` | figure | home | Diagram: the froxel grid, one cluster's box, a light sphere across clusters, the buffer layout |
| `render-direct:538` | figure | home | A grid of 1,000 small point lights built by commands, in the Lighting view |
| `render-direct:658` | hands-on | home | Exercise: change the cluster grid and measure with `editor.perf` the light passes, which are timed in `GPU.Cull` on GPU-driven frames and in `GPU.Setup` on the CPU path (the exercise names the path it forces), and `GPU.Opaque` |
| `new:33` | erratum | use | The inventory's slip about `GPU.Cull`, where the exercise measures the light passes; the erratum's home is `light/brdf` |
| `new:38` | hands-on | home | Exercise (trace it yourself): for one pixel, find with a search which cluster it reads (`GetClusterIndex`, from the screen tile and the log depth) and which lights it loops over, from the forward loop back to `BuildLightClusters`, which dispatches `LightClusters.comp`. Evidence: `Strata/shaders/Include/Clusters.slang:13-24`; `Strata/shaders/Scene/Forward.frag.slang:252-256`; `Strata/src/Strata/Renderer/SceneRenderer.cpp:2745`, `:3375` |
| `render-direct:711-714` | term | home | Relevance, clustered shading and froxel, exponential depth slices, light culling |
| `render-direct:198` | feature | use | `MaxLights`, `LightClusterGrid` and `MaxLightsPerCluster`, the switches this page tunes; the list's home is `reference/renderer` |
| `render-direct:822` | open | use | The documents give no reason for forward over deferred: the page states the trade-off and attributes no motive |
| `render-scene:731` | open | home | The GPU culling of light records (`LightCull.comp`, `LightCompact.comp`) is taught here, though its code lives with the render scene |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Light records and `LightData` | `light/lights` | must |
| Compute shaders, group-shared memory and barriers | `gpu/compute` | must |
| Frustum tests of spheres | `draw/bounds-culling` | must |
| The GPU-driven path and compaction | `draw/gpu-driven` | must |
| Forward against deferred shading | `gpu/frame-tour` | must |
| Logarithms | `basics/numbers` | must |
| The bits of a floating-point number | `basics/numbers` | must |
| Sorting | `basics/trees-graphs` | helps |
| GPU stages and their timing | `gpu/readback-timing` | helps |

## `light/area-lights` — Lights with size: sized highlights and area lights

**Covers.** The problem: real lights have size, and a point light gives a pin-point highlight on a mirror. The
approaches: the representative point (Karis 2013), area lights shaded with linearly transformed cosines (Heitz 2016),
and widening the lobe (roughness modification), with a table. What the pin has: the sun's Angular Diameter and the
`SourceRadius` of point and spot lights widen only the distribution D and keep it normalized; a source of angular radius
t adds (tan t / 1.287)^2, less what the smallest roughness spreads already, to the lobe's alpha squared, and the same
formula runs on the CPU for the sun and on the GPU per pixel for bulbs. The rule: widen only D and renormalize, because
widening the visibility or skipping the normalization adds light; a source radius larger than the real bulb dims and
spreads the highlight, it does not soften the light. Figures: sweeps of the sun's Angular Diameter (0, 0.53 and 10
degrees) on a mirror sphere and of a point light's Source Radius (0, 0.05 and 0.3 m) on wet ground. "What Strata does
not do" at the pin: no disk lights, no diffuse light from a light's size. Then 0.8.0's rectangle lights, as the outline
describes them: their shading with linearly transformed cosines, the light surfaces, editor and script support, disk
lights if their stage lands, the units of their intensity and how they convert to the quantities of
`light/units-exposure`, and the clear coat under them; their soft shadows are `light/local-shadows`'. The exercises
sketch where a rectangle light enters `LightRecord`, `LightData`, the clusters and `ShadeLitSurface`, and compare the
sketch with the merged code, and trace the sun's Angular Diameter and a bulb's Source Radius to the lobe they widen.
Afterwards the reader can explain why a sized highlight keeps its energy, and choose between a sized point light and an
area light.

**Leaves out.**

- The soft shadows of rectangle lights → `light/local-shadows`
- The sun's soft shadow from its Angular Diameter → `light/sun-shadows-2`
- The clear coat in general → `light/clearcoat-transmission`
- Light units in general → `light/units-exposure`
- Placing area lights in a game → `make/lamps`
- Probe bakes that draw no highlights → `indirect/probes`

**Fit.** `fits`: about 4,980 words against L (5,000), with 0.8.0's rectangle lights as the outline gives them (about
2,200); the items at the pin fill about 2,800 with the two exercises. Phase B must read again: the rectangle lights'
components, records and LTC shading, the light surfaces, their units and conversion, the coat under them, disk lights
(stage 5), and whether the two not-done entries still hold.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-direct:61` | feature | home | Highlights of sized sources: D widened and kept normalized, for the sun's disk and for bulbs and flames |
| `render-direct:217` | feature | home | Area lights at the pin: none in `Strata/src` or `Strata/shaders`; what "area-like" lights main has |
| `render-direct:347` | concept | home | Sized sources and highlights: the approaches and the mistake of a large source radius |
| `render-direct:443` | code | home | `Strata/shaders/Include/PBR.slang:12-31`: `GetSourceLobeAlpha2`; with `GetLobeAlpha` at 119-124 and `RenderData::GetSunLobeAlpha2` at `Strata/src/Strata/Renderer/SceneRenderData.h:115-128` |
| `render-direct:535-536` | figure | home | Sweeps: the sun's Angular Diameter on a mirror sphere; a point light's Source Radius on wet ground (the Showcase's fire and lanterns) |
| `render-direct:593` | rule | home | Sized sources widen only D and keep it normalized |
| `render-direct:665` | hands-on | home | Exercise: sketch a rectangle light's path through the renderer, then compare with the merged code |
| `new:39` | hands-on | home | Exercise (trace it yourself): follow with a search the sun's Angular Diameter from the light into the frame constants through `RenderData::GetSunLobeAlpha2`, and a bulb's `SourceRadius` from `LightData::SpotAngles.w` into `GetSourceLobeAlpha2` in the cluster loop, both ending in `GetLobeAlpha`, which widens only D. Evidence: `Strata/src/Strata/Renderer/SceneRenderer.cpp:2573`; `Strata/src/Strata/Renderer/SceneRenderData.h:121`; `Strata/shaders/Scene/Forward.frag.slang:244`, `:276`; `Strata/shaders/Include/PBR.slang:121`, `:143` |
| `render-direct:707-709` | term | home | Source radius and angular diameter, lobe widening, area light and LTC |
| `render-direct:829` | open | home | Area lights and the local-lights stream were branches at the pin; phase B writes the page from 0.8.0 |
| `render-indirect:75` | feature | home | Sized highlights as render-indirect lists them (`render-direct:61`) |
| `render-indirect:454` | figure | home | The sun's sized highlight, Clear against Overcast on a mirror sphere (0.53 against 10 degrees), part of the Angular Diameter sweep |
| `render-indirect:477` | rule | home | A light's size widens only its highlight's D (`render-direct:593`) |
| `new:7` | not-done | home | Disk-shaped area lights (0.8.0 brings rectangle lights; disk lights only if their stage lands). Evidence: `git grep -nw LTC 822a7a46 -- Strata/src Strata/shaders` and `git grep -n -e AreaLight -e RectLight 822a7a46 -- Strata/src Strata/shaders` find nothing |
| `new:8` | not-done | home | Diffuse light from the size of point and spot lights: a light's size widens only its highlight. Evidence: `Docs/Roadmap.md:946-947, 1660`; `AGENTS.md:407-408`; `Docs/Releases/0.7.0.md:409-410` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| GGX's alpha and its normalized lobe | `light/brdf` | must |
| Energy conservation | `light/energy` | must |
| The forward light loop | `light/many-lights` | must |
| Light units | `light/units-exposure` | must |
| Solid angle and angular radius | `basics/math-sphere` | must |
| Linear transforms of directions | `basics/math-matrices` | must |
| The clear coat | `light/clearcoat-transmission` | helps |
| Soft shadows of local lights | `light/local-shadows` | helps |

## `light/shadow-basics` — Shadow mapping from first principles

**Covers.** The problem as the reader meets it: is a point visible from the light? The page shows a scene with and
without the sun's shadow, then acne on a surface the sun grazes. The naive answers and where they break: a ray per pixel
per light (cost), shadow volumes (stencil and fill rate). The idea: render depth from the light, then compare a point's
depth in light space with the stored one (the shadow-mapping diagram): light space, orthographic projections for the sun
and perspective ones for lamps, reversed-Z (nearer to the light is larger), comparison samplers and percentage-closer
filtering. What goes wrong: acne and peter-panning. The four biases: the rasterizer's slope bias, a depth bias of one
texel, a normal offset of 1.5 texels measured in texels, and a receiver-plane bias computed from the inverse transpose
of the light's projection, not from screen derivatives (which are wrong at silhouettes and depend on how the GPU groups
pixels). Pancaking: casters between the light and the near plane are flattened onto it instead of clipped, in two lines
of a vertex shader. Alpha-masked casters discard their cut-out texels in the shadow pass; transparent surfaces (Blend
and glass) cast no shadow at all, into the cascades or the local atlas, on both paths, so there are no partial or
colored shadows. The approaches engines use (shadow volumes, shadow maps, ray-traced shadows) end in a table. Strata's
choice: reversed-Z D32 maps, a hardware comparison sampler, texel-relative biases and the receiver plane; the bridge to
the sun's cascades and to the lamps' atlas. The common mistakes: a constant bias in world units, screen derivatives for
the receiver plane. Figures: the diagram, and acne with both biases at 0 against the defaults at a low sun, with a crop.
Exercises: predict, then run, the shadows of a masked fence at two cutoffs and of a glass pane; a sketch of a shadow map
over a sloped line that counts acne with each bias off and on. Afterwards the reader can explain a shadow map, its
comparison and its biases, and set the biases of a light.

**Leaves out.**

- The sun's cascades → `light/sun-shadows-1`
- Soft shadows and the filter → `light/sun-shadows-2`
- Shadows of point and spot lights → `light/local-shadows`
- Reversed-Z as Strata's depth convention → `gpu/coordinates`
- Sun shadows in a game → `make/lighting`

**Fit.** `fits`: about 4,750 words against L (5,000). The shadow-mapping idea and the four biases, with two short
excerpts, take the most; the two exercises add about 500.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-direct:116` | feature | home | Pancaking: casters before the near plane flattened onto it |
| `render-direct:122` | feature | home | The biases: slope, depth (one texel), normal offset (1.5 texels), receiver plane from the inverse transpose |
| `render-direct:129` | feature | home | Alpha-masked casters: cut-out texels discarded in the shadow pass |
| `new:40` | rule | home | Opaque and masked surfaces cast shadows; transparent ones (Blend, and glass, which is always transparent) never do, into the cascades or the local atlas, on the CPU and the GPU-driven path: no partial or colored shadows (about 80 words). Evidence: `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp:58`, `:1203-1205`; `Strata/src/Strata/Renderer/SceneRendererLocalShadows.cpp:730-731`; `Strata/shaders/Scene/Cull.comp.slang:314-325` |
| `render-direct:361` | concept | home | Shadow mapping: light space, projections, reversed-Z, comparison samplers, acne, the biases, pancaking; the mistakes |
| `render-direct:456` | code | home | `Strata/shaders/Include/Shadows.slang:94-111`: the receiver-plane depth bias from the projection's cofactor |
| `render-direct:459` | code | home | `Strata/shaders/Scene/ShadowMesh.vert.slang:47-51`: pancaking in two lines (the inventory's 46-51 starts at the preprocessor line) |
| `render-direct:498` | figure | home | Diagram: the light's view, the depth comparison, acne and the biases, pancaking |
| `render-direct:547` | figure | home | Acne with `ShadowBias` and `ShadowNormalBias` at 0 against the defaults at a grazing sun (`ow.lowsun`), with a crop |
| `render-direct:715` | term | home | Shadow map |
| `render-direct:717-720` | term | home | Comparison sampler and PCF; shadow acne and peter-panning; depth, slope, normal-offset and receiver-plane bias; pancaking (each a glossary entry) |
| `new:41` | hands-on | home | Exercises: predict, then run: a fence with an alpha-masked material at `AlphaCutoff` 0.1 and 0.9, and a glass pane beside it, under a low sun (which shadows change, and which never appears); a sketch of a shadow map over a sloped line that counts the acne texels with the depth, slope and normal-offset biases off and on, and shows peter-panning when they are too large. Evidence: `Strata/shaders/Scene/ShadowMask.frag.slang:6`, `:15-16`; `Strata/src/Strata/Renderer/MaterialData.cpp:16-21`; `Strata/src/Strata/Renderer/RendererComponents.h:28-29`; `Strata/shaders/Include/Shadows.slang:94-111` |
| `render-direct:716` | term | link | Reversed-Z; its home is `basics/math-projection`, and Strata's depth convention is `gpu/coordinates`' |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Orthographic and perspective projections, depth | `basics/math-projection` | must |
| Reversed-Z and Strata's clip space | `gpu/coordinates` | must |
| Depth buffers and depth tests | `gpu/how-a-gpu-frame-works` | must |
| The sun, points and spots | `light/lights` | must |
| Bilinear filtering | `basics/signals` | must |
| The Mask alpha mode | `light/materials` | must |
| Normals through the inverse transpose | `basics/math-bases` | helps |

## `light/sun-shadows-1` — Sun shadows I: stable cascades

**Covers.** The job: cover the whole view with the sun's shadow maps, finely near the camera, with texels that stay put
when the camera moves. This page carries the full section on the problem: one map cannot cover a view finely; the
approaches are cascaded and parallel-split maps, maps fitted to the receivers (SDSM), stable cascades (Valient 2008) and
virtual shadow maps, with a table. Strata's history is "What went wrong before": 0.7.0 fitted the cascades to the
receivers by readback, so shadows sharpened over a second after a turn and jumped when a ball passed the camera. The
map: one D32 array with a layer per cascade, made with the first shadowed sun; what it costs in memory (five 8192 layers
take 1.25 GiB; the values come from the generated quality tables) and what happens when it does not fit (the size halves
down to 1024, reported once). The layout in code: splits from a fixed 1.5 m, a blend of logarithmic and uniform spacing
by `CascadeDistribution`, the first split at most 7.5 m; the smallest sphere around each slice, from the lens alone;
squares that cover the sphere, the filter's reach and one snapping texel, centered on whole texels of absolute light
space in double; the fifth, near cascade at High and Ultra. Selection by containment: the first cascade whose split lies
beyond the depth and whose square holds the point 33 texels inside, never by depth alone; the blend bands into the next
cascade. The GPU's depth fit for each cascade: why each cascade's depth range is fitted (it spans from the slice's far
side only to the nearest caster toward the light, so the depth's precision goes where the casters are), casters beyond
`c_MaxShadowCasterDistance` (100 km) pancaked onto the near plane, and `CascadeFit.comp` writing `u_Cascades`, which
every shadow reader reads, never `FrameConstants`. The casters, in a section of about 450 words on both paths: the
deterministic search (a job per cascade, chunks merged in order), casters under a texel left out, `FindShadowCasters`
and `CanShadowView`; on GPU-driven frames `CullShadow.comp` (`Cull.comp` built with `ST_CULL_SHADOW`) tests each
caster's light-space box against each cascade's square with the sub-texel test (`GetCasterCascades`), and `CullCascades`
widens the cascades' depth ranges for the fit, keeps the cascade mask under occlusion culling and emits draws into each
cascade's shadow buckets, none into a cached cascade; on feedback frames `FindShadowCasters` only places the cascades;
on the CPU path `GatherShadowDraws` batches the casters by the sort key's cascade field. The cascade cache and the
versions it compares, which run only on GPU-driven frames (the CPU path redraws every cascade every frame), and the
cascades' occlusion culling (`draw/occlusion` links here). The statistics per slice, and the shadows debug view:
receivers colored by screen pixels per shadow texel, cascade edges, hatched bands, with its statistics. The quality rows
`ShadowResolution` and `ShadowCascades` are named, with values from generated tables. A toy computes splits for one lens
in 30 lines. Figures: the stable-cascades and containment diagrams; the shadows view at Medium and at High; cascade
blend 0 against 0.1 across a split; four against five cascades; a sweep of `CascadeDistribution` in the shadows view.
"What Strata does not do": a second shadowed directional light, virtual shadow maps. The Manual's table of cascades per
preset is wrong and the page takes the code's numbers (an erratum). How it is tested: `Renderer.ShadowCascades`, and the
GPU cases (the first frame after a turn final, a strafe without shimmer, the ball shot, the cache, the blend seam).
Exercises: shadow tuning on the Third-Person course; a unit test for `GetLayout`; selection by depth only on a branch; a
trace of one caster into a cascade's draws on both paths. Afterwards the reader can explain and change the cascade
layout, follow a caster into the cascades and read the shadows view.

**Leaves out.**

- Shadow maps, biases and pancaking → `light/shadow-basics`
- The soft filter, the screen-space mask and contact shadows → `light/sun-shadows-2`
- Occlusion culling in general → `draw/occlusion`
- Presets and players' options → `image/quality-settings`
- Shadows of point and spot lights → `light/local-shadows`

**Fit.** `fits`: about 7,450 words against XL (8,000). Five excerpts, the casters section on both paths (about 450), the
shadows view and the caches take the most; the four exercises add about 1,000.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-direct:112-115` | feature | home | The cascade map, the stable layout, the fifth cascade, the GPU depth fit: each cascade's depth range spans from its slice's far side to the nearest caster toward the light, so the depth's precision goes where the casters are; casters beyond `c_MaxShadowCasterDistance` (100 km) are pancaked onto the near plane; `CascadeFit.comp` writes `u_Cascades`, which every shadow reader reads, never `FrameConstants` (`Docs/DeveloperGuide.md:4526-4530`; `Strata/shaders/Scene/CascadeFit.comp.slang:6-10`) |
| `render-direct:117-121` | feature | home | Sub-texel casters dropped, the deterministic caster search, containment selection, cascade blend, the cascade cache, which runs only on GPU-driven frames: the CPU path (`GPUDriven` off, devices without `drawIndirectFirstInstance`, thumbnails) redraws every cascade every frame (`Strata/src/Strata/Renderer/SceneRenderer.cpp:3343-3349`, `:248-251`; `Strata/src/Strata/Renderer/SceneRendererGPUDriven.cpp:164-168`; `Strata/src/Strata/Renderer/SceneRenderer.h:233-239`) |
| `new:43` | feature | home | The cascades' memory and their failure path, about 100 words: five 8192 layers take 1.25 GiB (the values come from the generated quality tables; `image/quality-settings` keeps the estimators); a map that cannot be made halves each way down to 1024, the size every reader then uses, reported once. Evidence: `Strata/src/Strata/Renderer/SceneRenderer.cpp:64-65`, `:1734-1749`; `Docs/DeveloperGuide.md:4691-4692` |
| `render-direct:130` | feature | home | Cascade statistics in `SceneRendererStats::Cascades` and `renderStats.cascades` |
| `render-direct:177` | feature | home | The shadows debug view and its statistics |
| `render-direct:189-190` | feature | home | The quality rows `ShadowResolution` and `ShadowCascades` (values from generated tables) |
| `render-direct:369` | concept | home | Cascaded shadow maps and their stability; why receiver fitting was dropped; the mistakes |
| `render-direct:452` | code | home | `Strata/src/Strata/Renderer/ShadowCascades.cpp:14-21`: logarithmic and uniform splits; with 56-71, why the splits start at a fixed distance |
| `render-direct:453` | code | home | `Strata/src/Strata/Renderer/ShadowCascades.cpp:73-102`: the smallest sphere around a slice, from the lens alone |
| `render-direct:454` | code | home | `Strata/src/Strata/Renderer/ShadowCascades.cpp:104-141`: the layout with blend bands; snapping to texels in double |
| `render-direct:455` | code | home | `Strata/shaders/Include/Shadows.slang:45-92`: selection by containment and the blend weights |
| `render-direct:499` | figure | home | Diagram: stable cascades from above, a second panel with the camera turned 90 degrees and identical spheres |
| `render-direct:501` | figure | home | Diagram: containment, a position near a square's edge moved by the normal offset |
| `render-direct:542` | figure | home | The shadows view at Medium against High on the Third-Person course, with the legend |
| `render-direct:544` | figure | home | Cascade blend 0 against 0.1 across a split (a long fence) |
| `render-direct:551` | figure | home | Four against five cascades in the shadows view (Showcase shot 5) |
| `render-direct:599-604` | rule | home | Select with `SelectShadowCascade`; layouts come only from `GetLayout`; snap in double in absolute light space |
| `render-direct:610` | rule | home | A new input of how casters are drawn changes a version the shadow caches compare |
| `render-direct:627` | rule | home | The Manual's drift: the page takes the code's values, not the Manual's; the cascades' erratum is `new:44`, and the 16 shadowed lights are `new:12` on `light/local-shadows` |
| `new:44` | erratum | home | `Docs/Manual/Lighting.md:156` gives the sun's shadow 3, 4, 4 and 4 cascades at Low, Medium, High and Ultra, and `:160` speaks of "four 8192 texel cascades" that "take 1 GiB" at High and Ultra; the presets' row gives 3, 4, 5 and 5 (`c_ShadowCascadesRow`), and five 8192 layers take 1.25 GiB. Evidence: `Docs/Manual/Lighting.md:156`, `:160`; `Strata/src/Strata/Renderer/RendererQuality.cpp:40`; `Docs/DeveloperGuide.md:4691` |
| `render-direct:642` | hands-on | home | Exercise: acne at a low sun on the Third-Person course, the biases, peter-panning, Medium against High in the shadows view |
| `render-direct:659-660` | hands-on | home | Exercises: a unit test for `ShadowCascades::GetLayout`; selection by depth alone, shown failing in the shadows view |
| `render-direct:721-728` | term | home | CSM, split and slice, logarithmic and uniform splits, stable cascades, texel snapping, blend band, containment, pixels per texel |
| `new:9` | not-done | home | A second shadowed directional light (the moon); virtual shadow maps. Evidence: `Docs/Roadmap.md:949-950, 1670` |
| `new:10` | figure | home | Sweep: `CascadeDistribution` 0, 0.5, 0.9 and 1 in the shadows view, showing where the detail goes. Evidence: `Strata/src/Strata/Renderer/RendererComponents.h:36-39` |
| `render-scene:61`, `render-scene:62`, `render-scene:141`, `render-scene:142` | feature | home | The caster search (`FindShadowCasters`), off-view casters for animators (`CanShadowView`), cascade occlusion, the cascade cache and its versions (on GPU-driven frames only: the CPU path redraws every cascade) |
| `render-scene:448` | figure | home | The cascade cache in numbers on a GPU-driven frame: a still view with `renderStats.cachedCascades` at the cascade count, then a moving object that redraws only the cascades it reaches |
| `render-scene:124` | feature | use | `Cull.comp`'s shadow variant, `CullShadow.comp` (`ST_CULL_SHADOW`, `Strata/CMakeLists.txt:192`), for the casters section; the culling's home is `draw/gpu-driven`, which keeps one sentence that points here |
| `new:42` | code | home | `Strata/shaders/Scene/Cull.comp.slang:399-434`: `CullCascades`, the heart of the casters section (about 450 words with what follows): a caster's light-space box tested against each cascade's square with the sub-texel test (`GetCasterCascades`, 238-270), the cascades' depth ranges widened toward the light for the fit, the cascade mask under occlusion culling, and the draws emitted into each cascade's shadow buckets except those of cached cascades (`EmitShadowInstances`, 314-325; drawn by `DrawGPUShadows`, `Strata/src/Strata/Renderer/SceneRendererGPUDriven.cpp:1382-1412`); on feedback frames `FindShadowCasters` only places the cascades (`Docs/Architecture.md:2504-2507`); on the CPU path `GatherShadowDraws` batches the casters by the sort key's cascade field (`Strata/src/Strata/Renderer/SceneRendererExtraction.cpp:1126-1254`) |
| `new:45` | hands-on | home | Exercise (trace it yourself): one fence post followed into a cascade's draws: on the CPU path from `FindShadowCasters` to its cascade mask and its sort keys in `GatherShadowDraws`, on a GPU-driven frame from `GetCasterCascades` to `EmitShadowInstances`; then `renderStats.cascades` read for both. Evidence: `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp:418`, `:1126-1254`; `Strata/shaders/Scene/Cull.comp.slang:238-270`, `:314-325` |
| `render-scene:489` | rule | home | A new input of how casters are drawn changes a version the shadow caches compare (`render-direct:610`) |
| `render-scene:652-654` | term | home | Shadow caster and cascade, sub-texel caster, shadow cascade cache |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Shadow maps, comparisons and biases | `light/shadow-basics` | must |
| GPU-driven culling | `draw/gpu-driven` | must |
| Occlusion culling and depth pyramids | `draw/occlusion` | must |
| Frustums and bounding spheres | `basics/math-geometry` | must |
| Float precision far from the origin | `basics/numbers` | must |
| Deterministic parallel jobs | `core/jobs` | must |
| Overlay passes | `gpu/debug-drawing` | must |
| The render scene's change logs | `draw/render-scene` | must |
| Blending between two values | `basics/math-interpolation` | helps |
| Quality presets | `image/quality-settings` | helps |
| Running `viewport.capture` | `editor/commands` | helps |

## `light/sun-shadows-2` — Sun shadows II: the soft shadow of a real sun

**Covers.** The job: soften the sun's shadow by the sun's real size, the same in every frame. This page carries the full
section on the problem: penumbrae widen with the distance between blocker and receiver; the approaches are fixed PCF,
PCSS (Fernando 2005), variance, exponential and moment shadow maps, and ray-traced shadows, with a table. It is XL, in
six sections with their own anchors. One, the geometry: a sun of angular radius a over a blocker at separation s draws a
penumbra 2 s tan(a) wide, which a disk of radius s tan(a) reproduces (the PCSS diagram). Two, the classification: a
pyramid of (nearest, farthest) depths over cells of 4, 8 and 16 texels, rounded outward and built right after the
layers, decides lit and umbra exactly and never misses a thin caster (the pyramid diagram and its shader). Three, the
filter in `SampleCascadeShadow`, shown whole: the blocker estimate, a fixed four-tap tent below a texel, a Vogel disk of
8 to 32 taps above one or two texels, turned per pixel by a fixed 64 x 64 blue-noise tile; its comparisons take an
explicit level (`SampleCmpLevelZero` in `CompareShadowMap`): the classification returns early, so the sun is shaded in
non-uniform flow, and zero gradients made the evaluation cost 2.2 to 2.4 times as much; the rule that nothing changes
per frame (never `TemporalParams.z`), so a still view is the same image with and without TAA; the `ShadowFilterQuality`
row. Four, the screen-space mask: after the prepass, every opaque pixel gets the filter into RG8 (the square root of the
visibility, a blur radius), blurred horizontally then vertically with plane-distance and normal weights, and the forward
pass reads it at SRV 28 (the mask-pipeline diagram); the stair-step blur where the tent leaves an edge on a receiver the
light grazes. Five, contact shadows: a screen-space march toward the sun over the prepass depth, which sees every opaque
pixel, ignores `CastShadows`, shimmers in motion and is therefore on in no preset (Custom only; 0.7.0's High and Ultra
had drawn them). Six, transparent receivers: they call `SampleDirectionalShadow` per pixel without blur or contacts, and
both paths change together. A toy is a 1-D PCSS. Figures: the penumbra growing with distance (poles of 3, 5 and 10 cm at
Angular Diameter 0.53 and 2), 8 against 32 taps without TAA, stair steps without and with the blur (a crop), contact
shadows 16 steps against 0, and the sun's Angular Diameter on shadows. Alternatives. How it is tested:
`GPU.SceneRenderer.ShadowFilter` (penumbra width, independence from TAA, a thin caster never lost, tent smoothness,
ranges that hold every texel, contacts), `.ScreenShadows`, `.ContactShadows`, `PerfGPU.Renderer.ScreenShadows4K*`.
Exercises: a penumbra study measured against s tan(a); the pyramid's first level as a debug overlay; a trace of one
pixel's sun visibility from the mask to the forward pass, and of a transparent pixel's. Afterwards the reader can derive
PCSS at physical width, follow `SampleCascadeShadow`, and change the filter without making it depend on history.

**Leaves out.**

- The cascades and their selection → `light/sun-shadows-1`
- Blue noise and the Vogel pattern from zero → `basics/math-probability`
- Temporal anti-aliasing and "nothing needs history" → `image/taa`
- Shadows of point and spot lights → `light/local-shadows`
- The highlight of a sized sun → `light/area-lights`
- Presets and players' options → `image/quality-settings`

**Fit.** `fits`: about 7,200 words against XL (8,000). Three excerpts, the central one long, four diagrams, five figures
and six sections take the most; the three exercises add about 750.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-direct:123-128` | feature | home | The physical PCSS filter, the depth ranges, the screen-space mask, the stair-step blur, contact shadows, transparent receivers |
| `render-direct:194-195` | feature | home | The rows `ShadowFilterQuality` (disk taps) and `ContactShadows` (Custom only) |
| `render-direct:377` | concept | home | Soft shadows: PCF, PCSS, contact hardening, noise; the mistakes |
| `render-direct:384` | concept | home | Screen-space shadow passes and contact shadows; the mistake about `CastShadows` |
| `render-direct:457` | code | home | `Strata/shaders/Include/Shadows.slang:143-260`: `SampleCascadeShadow` whole: classification, blocker estimate, tent, Vogel disk with blue noise |
| `render-direct:458` | code | home | `Strata/shaders/Scene/ShadowRanges.comp.slang:27-70`: a conservative min-max pyramid with outward rounding |
| `render-direct:460` | code | home | `Strata/shaders/Effects/ScreenShadows.frag.slang:53-92`: position and normal from the prepass, visibility encoded as a square root, the blur radius |
| `render-direct:503-507` | figure | home | Diagrams: PCSS geometry and the filter's decisions; the depth-range pyramid; the screen-space mask pipeline |
| `render-direct:545-546` | figure | home | The penumbra growing with distance (`lookdev.thin`); filter taps 8 against 32 without TAA |
| `render-direct:548-550` | figure | home | Stair steps without and with the blur (a crop); contact shadows (`lookdev.contact`) 16 against 0 |
| `render-direct:605-608` | rule | home | The sun's filter uses fixed noise; change both shadow paths together |
| `render-direct:625` | rule | home | The sun's comparisons take an explicit level, about 100 words beside `SampleCascadeShadow`: `CompareShadowMap` calls `SampleCmpLevelZero` because the classification returns early, so the sun is shaded in non-uniform flow, and sampling with zero gradients made the evaluation cost 2.2 to 2.4 times as much (`Strata/shaders/Include/Shadows.slang:119-126`; `Docs/DeveloperGuide.md:4716-4717`) |
| `render-direct:612` | rule | home | Contact shadows come from every opaque pixel on screen |
| `render-direct:643` | hands-on | home | Exercise: the penumbra study, measured against 1.374 s tan(a) |
| `render-direct:661` | hands-on | home | Exercise: the pyramid's first level as a debug overlay |
| `new:46` | hands-on | home | Exercise (trace it yourself): one opaque pixel's sun visibility followed with a search from `ScreenShadows.frag`, which `RenderScreenShadows` draws and blurs, to the forward pass's read at SRV 28; then a transparent pixel's call of `SampleDirectionalShadow`, which skips the mask. Evidence: `Strata/src/Strata/Renderer/SceneRendererScreenShadows.cpp:14-15`, `:186`; `Strata/shaders/Scene/Forward.frag.slang:69`, `:238-240`; `Strata/shaders/Include/Shadows.slang:285` |
| `render-direct:729-733` | term | home | PCSS, umbra and penumbra, contact hardening, depth range pyramid, tent filter |
| `render-direct:736-738` | term | home | Screen-space shadow mask, edge-aware (bilateral) blur, contact shadows |
| `render-direct:826` | open | home | Whether a shipped preset drew contact shadows: the page says 0.7.0's High and Ultra did and 0.8.0 turned them off; the writer checks the 0.7.0 rows |
| `render-image:282` | feature | home | `Tools/GenerateBlueNoise.py` writes the 64 x 64 void-and-cluster tile of `BlueNoise.h` that turns the sun's filter |
| `render-direct:535` | figure | use | The sun's Angular Diameter on shadows; the figure's home is `light/area-lights` |
| `render-direct:734-735` | term | link | Vogel disk and blue noise; their home is `basics/math-probability` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Stable cascades and their selection | `light/sun-shadows-1` | must |
| Shadow maps and biases | `light/shadow-basics` | must |
| Sampling, kernels and filtering | `basics/signals` | must |
| Noise and sampling patterns: blue noise, the Vogel disk | `basics/math-probability` | must |
| Octahedral normals | `basics/math-sphere` | must |
| The depth prepass | `gpu/frame-tour` | must |
| Compute shaders | `gpu/compute` | must |
| Temporal anti-aliasing and its history | `image/taa` | helps |
| The transparent pass | `draw/batching` | helps |
| Quality presets | `image/quality-settings` | helps |

## `light/local-shadows` — Shadows of point and spot lights

**Covers.** The job: shadows for many point and spot lights from one atlas, without blinking and within a redraw budget.
This page carries the full section on the problem: a cube map per light, dual-paraboloid maps, a shared atlas, caching
static shadows, with a table. The map: the file's overview and constants. The atlas: one D32 texture whose size is the
`LocalShadowAtlasSize` row, with tiles from 128 texels to `LocalShadowMaxTile`; what it costs in memory and what happens
when it does not fit (it halves down to 2048, and that frame draws no local shadows; when no atlas can be made, point
and spot lights cast none). The quadtree allocator: tiles of powers of two in Morton order that merge when freed, the
same requests giving the same tiles. Tile sizes follow the pixels a light's range spans on screen, with a band of 1.25
and 0.4 so they do not toggle, halved in rounds from the least relevant light when the atlas is full; lights whose tiles
do not fit even at 128 texels cast no shadow. A spot light is one view (at most 80 degrees half angle), a point light
six cube faces chosen by the major axis; a guard band keeps every tap inside its face. Views are cached by a key in
world space and by content versions, following the bounds of up to 65,536 casters; the key ignores the camera, so a
light that moved keeps its old shadow until the redraw budget draws its views again; at most 12 views are drawn a frame,
nearest first; a light casts its shadow once all its views hold content, and fades in over 8 frames; ranks fade too.
Sampling: 16 Poisson taps clamped to the tile, turned per pixel by interleaved gradient noise that also turns with the
TAA frame (on main the exception to fixed noise). The data per slot at SRV 13 and the local-shadow vertex shaders. The
casters and the culling of local views (`FindLocalShadowCasters`) come with the draw unit's items, on both paths: on
GPU-driven frames the views are culled in batches of at most `ST_CULL_MAX_LOCAL_VIEWS`, later batches by the mode
`ST_CULL_MODE_LOCAL`, each batch drawn before the next is culled. The rule: keep the lamp's mesh out of its own light's
shadow. The quality rows are named with values from generated tables; the Manual's "at most 16" holds only from Medium
up. "What Strata does not do": soft shadows from a light's size. Then 0.8.0's rectangle lights' soft shadows, written in
phase B. A toy allocator of 40 lines. Figures: the atlas diagram with a view's states (no content, drawn, cached, dirty,
redrawn) and the fade; lanterns under trees (`tp.lantern`) with `CastShadows` off and on and `ShadowFilterRadius` 0
against 8. How it is tested: `Renderer.ShadowAtlas`, `GPU.SceneRenderer.LocalShadows`,
`PerfGPU.Renderer.ShadowRedraw4K*`. The exercises move the sampling rotation to the fixed blue-noise tile and show a
still frame identical with and without TAA, and trace one point light from its tile size to the forward pass's sample.
Afterwards the reader can explain the atlas, its caches and budget, and predict what a moving lamp costs.

**Leaves out.**

- Shadow maps and biases → `light/shadow-basics`
- The sun's cascades and their cache → `light/sun-shadows-1`
- Shadow slots in the forward loop → `light/many-lights`
- Interleaved gradient noise and Poisson disks from zero → `basics/math-probability`
- Lamps and their shadows in a game → `make/lamps`

**Fit.** `fits`: about 6,100 words against L (5,000): about 5,600 at the pin and about 500 for 0.8.0's rectangle-light
soft shadows as the outline gives them; the atlas, its allocator, the view caches and three excerpts take the most.
Phase B must read again: the local-lights stream (more than 16 shadowed lights, tile lifetime, fixed noise for local
lights, the scheduler), the soft shadows of rectangle lights, the numbers 16, 12 and 8 and the turning noise, the
exercise (which wave 8 may have done), and the erratum and the not-done entry.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-direct:136-145` | feature | home | The atlas, the quadtree allocator, tile fitting (lights whose tiles do not fit even at 128 texels cast no shadow), views and cube faces, guard bands, the view cache (its key ignores the camera, so a light that moved keeps its old shadow until the redraw budget draws its views again; `Docs/DeveloperGuide.md:4760-4762`, `:4769-4771`), the redraw budget and fades, sampling, the data per slot, the vertex shaders |
| `new:47` | feature | home | The atlas's memory and its failure path, about 100 words: Ultra's 8192 atlas takes 256 MiB (the values come from the generated quality tables); an atlas that cannot be made halves each way down to 2048, reported once, and that frame draws no local shadows while the tiles are placed again; when no atlas can be made, point and spot lights cast no shadows. Evidence: `Strata/src/Strata/Renderer/SceneRendererLocalShadows.cpp:38-39`, `:793-834` |
| `render-direct:191-193` | feature | home | The rows `LocalShadowAtlasSize`, `LocalShadowMaxTile` and `MaxShadowedLocalLights` (values from generated tables) |
| `render-direct:390` | concept | home | Shadows of local lights: atlases, cube faces, caching; the mistakes |
| `render-direct:461` | code | home | `Strata/shaders/Include/LocalShadows.slang:43-97`: cube face selection, biases in texels at depth, Poisson PCF clamped to a tile |
| `render-direct:462` | code | home | `Strata/src/Strata/Renderer/ShadowAtlasAllocator.h:21-59`: the allocator's contract and `FitTileSizes` |
| `render-direct:509` | figure | home | Diagram: the atlas with a point light's six faces and spot lights, guard bands, a view's states and its fade-in |
| `render-direct:553` | figure | home | Lanterns under trees: `CastShadows` off and on; `ShadowFilterRadius` 0 against 8 |
| `render-direct:614` | rule | home | Keep the lamp mesh out of its own light's shadow |
| `render-direct:662` | hands-on | home | Exercise: the sampling rotation moved to the fixed blue-noise tile, a still frame identical with and without TAA |
| `new:48` | hands-on | home | Exercise (trace it yourself): one point light followed with a search or a debugger from its tile size (`FitTileSizes`) through its slot's data (`BuildLocalShadowData`) and its views drawn (`DrawLocalShadows`) to the forward pass's `SampleLocalShadow`, which reads the slot at SRV 13. Evidence: `Strata/src/Strata/Renderer/SceneRendererLocalShadows.cpp:295`, `:762`, `:869`; `Strata/shaders/Scene/Forward.frag.slang:273`; `Strata/shaders/Include/LocalShadows.slang:22`, `:63` |
| `render-direct:739-741` | term | home | Shadow atlas, tile and guard band; quadtree allocator; cube shadow |
| `new:11` | not-done | home | Soft shadows from the size of point and spot lights. Evidence: `Docs/Roadmap.md:946-947, 1660`; `AGENTS.md:407-408`; `Docs/Releases/0.7.0.md:409-410` |
| `new:12` | erratum | home | `Docs/Manual/Lighting.md:180` says at most 16 point and spot lights in view cast shadows; Low allows 4 (`MaxShadowedLocalLights` 4, 16, 16, 16). Evidence: `Docs/Manual/Lighting.md:180`; `Strata/src/Strata/Renderer/RendererQuality.cpp:43` |
| `new:13` | code | home | `Strata/src/Strata/Renderer/SceneRendererLocalShadows.cpp:23-67`: the overview and the constants (tile sizes, hysteresis, rank margin, spot angle, near planes, the normal bias's reach, caster limits) |
| `render-scene:729` | open | home | The culling of local shadow views (`CullLocalShadowViews`, `RunLocalShadowCulling`), on the CPU and the GPU-driven path |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Shadow maps and biases | `light/shadow-basics` | must |
| Shadow caches and their versions | `light/sun-shadows-1` | must |
| The forward light loop and shadow slots | `light/many-lights` | must |
| Sized lights | `light/area-lights` | must |
| Perspective projections and cube faces | `basics/math-projection` | must |
| Trees | `basics/trees-graphs` | must |
| Noise patterns: Poisson disks, interleaved gradient noise | `basics/math-probability` | must |
| GPU-driven culling | `draw/gpu-driven` | must |
| Bit interleaving (Morton order) | `basics/numbers` | helps |
| The TAA frame index | `image/taa` | helps |
| Quality presets | `image/quality-settings` | helps |

## `light/sky` — The sky as a light: sources, sun extraction and presets

**Covers.** The job: light the scene from every direction by the sky, and draw the sky behind it. This page carries the
full section on the problem for itself and `light/atmosphere`: constant ambient light, HDR photographs, analytic skies
(Preetham, Hosek-Wilkie) and physical atmospheres (Bruneton 2008, Hillaire 2020), with a table. The component
`SkyLightComponent`: the first active one applies; `Source` (EnvironmentMap, Procedural, Atmosphere), `Intensity`,
`Rotation`, `ShowBackground`, `BackgroundBlur`, an `AmbientColor` in nits for a scene without an environment, the
procedural colors, the sun's size and intensity; inactive reasons per source; the atmosphere's own fields
(`AtmosphereDensity`, `AtmosphereHaze`, `GroundAlbedo`, `AerialPerspective`, `AerialPerspectiveScale`) are named and
linked to `light/atmosphere`, which teaches them. The code that picks the source each frame, with the constant ambient
used until a map arrives. The environment-map source: an equirectangular HDR texture turned into a 512 cube, then the
filter chain every source shares (the chain is `indirect/ibl`'s). The procedural sky: a zenith, horizon and ground
gradient in nits with the sun's disk where the directional light comes from, recomputed only when its parameters change.
The presets Clear, Hazy, Overcast and GoldenHour as real values in code: a sky and a sun in one undo step, automatic
exposure on with MaxEV 16, and the `groundIlluminance` they return. Extract Sun and Remove Sun: an HDR map's sun becomes
the shadow-casting directional light, and the importer paints it out of the map (the `HDRSun` setting is
`assets/texture-cooking`'s); the mistake of a double sun. What Strata does not do here: no clouds, stars or moon (the
atmosphere's haze is clear aerosol, and the Overcast preset is a nearly uniform procedural sky). A toy gradient sky in
30 lines. Figures: the three sources side by side, the four presets on Basic 3D as a sweep, an HDR map before and after
Extract Sun with Remove Sun (shadows appear). How it is tested: `GPU.ProceduralSky`, `Editor.Lighting`. Exercises: each
preset on Basic 3D with `groundIlluminance` and the sun-to-sky ratio read from the Lighting view; Extract Sun on an HDR
map; a trace of `lighting.applySkyPreset` to its values and its one undo step. Afterwards the reader can choose a sky
source, apply a preset, extract a sun, and say what each source computes.

**Leaves out.**

- The physical atmosphere → `light/atmosphere`
- The sky light's atmosphere fields (density, haze, ground albedo, aerial perspective) → `light/atmosphere`
- The environment filter chain and image-based light → `indirect/ibl`
- The exposure settings the presets change → `image/exposure`
- The `HDRSun` import setting → `assets/texture-cooking`
- The sun-to-sky ratio as a measurement → `light/measuring-light`
- Choosing a sky in a game → `make/lighting`

**Fit.** `over`: about 4,400 words against M (3,000). Three sources, the presets, Extract Sun, three excerpts and three
exercises pass M's top; by S2 the page takes L (5,000), whose range holds it.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-direct:151-153` | feature | home | The sky light component, the environment-map source, the procedural sky; the component's atmosphere fields (`AtmosphereDensity`, `AtmosphereHaze`, `GroundAlbedo`, `AerialPerspective`, `AerialPerspectiveScale`) are named here and linked to `light/atmosphere`, which teaches them |
| `render-direct:159-160` | feature | home | The sun and sky presets; Extract Sun and Remove Sun |
| `render-direct:396` | concept | home | The sky as a light source: approaches, Strata's three sources into one chain, the double-sun mistake |
| `render-direct:555` | figure | home | The three sky sources side by side in one scene |
| `render-direct:558` | figure | home | Sweep: Clear, Hazy, Overcast and GoldenHour on Basic 3D |
| `render-direct:564` | figure | home | Off and on: an HDR map with its sun, before and after Extract Sun and Remove Sun |
| `render-direct:639` | hands-on | home | Exercise: each preset, `groundIlluminance` and the sun-to-sky ratio from the Lighting view's legend |
| `render-direct:648` | hands-on | home | Exercise: Extract Sun, shadows appear and the sky no longer lights twice |
| `new:49` | not-done | home | Clouds, stars and a moon: the atmosphere's haze is clear aerosol, and the Overcast preset is a nearly uniform procedural sky (about 70 words). Evidence: `Strata/src/Strata/Renderer/SkyPresets.cpp:35-37`; `git grep -niwE -e moon -e stars -e starfield -e "clouds?" 822a7a46 -- Strata/src Strata/shaders` finds only that comment, a tooltip's full-moon illuminance (`Strata/src/Strata/Renderer/RendererComponents.cpp:289`) and two comments on cloud placeholder files (`Strata/src/Platform/Windows/WindowsFileSecurity.h:28`, `Strata/src/Strata/Core/Platform.h:104`) |
| `new:50` | hands-on | home | Exercise (trace it yourself): `lighting.applySkyPreset` followed with a search from its registration to `GetSkyPresetValues` and the one `SceneEditTransaction` that makes its undo step. Evidence: `StrataEditor/src/Editor/EditorLightingCommands.cpp:638-641`, `:953`; `Strata/src/Strata/Renderer/SkyPresets.cpp:83` |
| `render-direct:742-743` | term | home | Environment map (equirectangular HDR), procedural sky |
| `new:14` | code | home | `Strata/src/Strata/Renderer/SceneRenderer.cpp:927-1029`: `UpdateEnvironment`, the first active sky light, its three sources, the constant ambient until a map arrives |
| `new:15` | code | home | `Strata/shaders/IBL/ProceduralSky.comp.slang:23-51`: the procedural gradient and the sun's disk with its edge smoothed over a texel |
| `new:16` | code | home | `Strata/src/Strata/Renderer/SkyPresets.cpp:20-59`: the presets as real values (sun illuminance above the air, elevations, the overcast sky in nits) |
| `render-image:99` | feature | home | What the presets do to exposure: manual exposure made automatic, MaxEV raised |
| `render-indirect:53` | feature | home | The sky light component as render-indirect lists it (`render-direct:151`) |
| `render-indirect:63-64` | feature | home | Extract Sun and Remove Sun, and the sky presets, as render-indirect lists them (`render-direct:159-160`) |
| `assets:157` | feature | home | The HDR sun finder (`HDRSun::Find` and `Remove`): it finds the sun in an equirectangular sky, measures its illuminance and paints it out |
| `assets:511` | figure | home | An HDR sky with and without `RemoveSun`, with `lighting.extractSun`; with `render-direct:564`, one figure |
| `render-direct:196` | feature | link | `EnvironmentResolution`, the prefiltered sky's size; its home is `indirect/ibl` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Nits and lux | `light/units-exposure` | must |
| The directional light and preview lighting | `light/lights` | must |
| HDR textures and their import | `assets/texture-cooking` | must |
| Directions on a sphere, equirectangular and cube maps | `basics/math-sphere` | must |
| Loading assets and "not loaded yet" | `assets/loading` | must |
| Compute shaders | `gpu/compute` | must |
| The environment filter chain | `indirect/ibl` | helps |
| Exposure and MaxEV | `image/exposure` | helps |
| Commands and undo steps | `editor/commands` | helps |

## `light/atmosphere` — Earth's atmosphere and aerial perspective

**Covers.** The job: compute Earth's sky, the sun's color at the ground and the haze of distance from the physics of
air. First the home of participating media, from zero: extinction, scattering and absorption, optical depth,
transmittance (the Beer-Lambert law), phase functions (Rayleigh's, and Henyey-Greenstein's for aerosols), single against
multiple scattering, and why engines precompute tables (Bruneton 2008, Hillaire 2020). Strata's model: Earth's Rayleigh,
Mie and ozone, the ground at y = 0, radii of 6,360 and 6,460 km, and the tables (transmittance 256 x 64, multiple
scattering 32 x 32, sky view 192 x 108; the tables diagram with their axes and readers). The sky light's own atmosphere
fields, as `GetMedium` reads them and kept finite: `AtmosphereDensity` scales the air and the aerosols, `AtmosphereHaze`
the aerosols once more, `GroundAlbedo` is the light the ground sends back into the sky, and `AerialPerspectiveScale`
above 1 gives small worlds the haze of large ones. The code in data order: the extinction profiles and a midpoint
quadrature in double on the CPU; how the multiple-scattering table is computed (after the first bounce the light is
taken to arrive equally from every direction; the second order is gathered over a sphere of 64 directions, the ground's
reflection included; every higher order is f times the one before, so all of them sum to the second order over (1 - f),
the idea that makes Hillaire's model cheap); one integration segment of single and multiple scattering and the quadratic
step distribution of the sky-view table; the sun's color through the air, computed in double and faded by the share of
the disk above the horizon, so the light's intensity is the sun above the air (the mistake of dimming it twice); the
storage scale of 2^14 that keeps twilight out of half-float subnormals, and the readers that multiply by
`EnvironmentParams.x`; the environment refresh, double-buffered in 14 steps once the sun moved 0.5 degrees (a state
diagram); the background with the analytic sun disk as illuminance over solid angle; aerial perspective: a 32 x 32 x 32
froxel volume of in-scattering and transmittance per frame, slices at D ((k + 0.5) / 32)^2, two fetches per pixel,
applied before height fog. A toy computes the optical depth of one ray in 30 lines. Figures: times of day as a sweep of
the sun's elevation (60, 20, 6, 0 and -6 degrees) with the ground's illuminance; aerial perspective off and on and its
scale 1 against 6. How it is tested: `GPU.Atmosphere` (the GPU table against the CPU within 1%, a night sky without
bands, no daytime clamp), the aerial perspective tests. The exercises evaluate the transmittance at sunset on the CPU
and compare it with `SceneRendererStats::SunTransmittance`, and trace a change of `AtmosphereHaze` to the tables
computed again. Afterwards the reader can explain the atmosphere's tables, why the sun's intensity is above the air, and
what aerial perspective adds.

**Leaves out.**

- The sky's sources and presets → `light/sky`
- Height fog → `light/fog`
- The atmosphere's environment cube in the filter chain → `indirect/ibl`
- Marching through volumes for global illumination → `indirect/gi-cascades`
- The pre-exposure → `image/pre-exposure`
- A day cycle in a game → `make/reflections`

**Fit.** `fits`: about 5,800 words against L (5,000). Participating media from zero, five excerpts and multiple
scattering made cheap take the most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-direct:154-158` | feature | home | The physical atmosphere, with the sky light's atmosphere fields where the page presents the model (`GetMedium`, settings kept finite: `AtmosphereDensity` scales the air and the aerosols, `AtmosphereHaze` the aerosols once more, `GroundAlbedo` the light the ground sends back into the sky; `Strata/src/Strata/Renderer/RendererComponents.h:110-123`, `Strata/src/Strata/Renderer/Atmosphere.h:50-59`, `Strata/src/Strata/Renderer/SceneRendererAtmosphere.cpp:224-226`), the sun's color through the air, the storage scale, the environment refresh, the background |
| `render-direct:170` | feature | home | Aerial perspective: the froxel volume, its slices, before height fog; `AerialPerspectiveScale` above 1 gives small worlds the haze of large ones |
| `new:51` | concept | home | Multiple scattering made cheap, about 150 words: after the first bounce the light is taken to arrive equally from every direction; the second order is gathered over a sphere of directions, the ground's reflection of the sun included; the same gathering of a light that is 1 everywhere gives the share f that scattering returns, and every higher order is f times the one before, so all of them sum to the second order over (1 - f). Evidence: `Strata/shaders/IBL/AtmosphereMultipleScattering.comp.slang:5-10` |
| `render-direct:402` | concept | home | Participating media and the physical atmosphere; the mistakes |
| `render-direct:463` | code | home | `Strata/src/Strata/Renderer/Atmosphere.cpp:18-33`: extinction profiles and the distance to the top; with 61-101, the midpoint transmittance and the sun's transmittance with the disk's share |
| `new:52` | code | home | `Strata/shaders/IBL/AtmosphereMultipleScattering.comp.slang:18-81`: the multiple-scattering table, per height and sun height: 8 rings by 8 sectors of directions, 20 steps along each, the single scattering toward the point with an even phase and the ground's diffuse reflection of the sun (the second order), the transfer f gathered beside it, and all orders summed as the second over (1 - f), stored times the storage scale; with 5-10, the idea in the file's comment (the finding's 18-92 holds the entry point's boilerplate from 83 on) |
| `render-direct:464` | code | home | `Strata/shaders/Include/AtmospherePass.slang:73-89`: one segment of single and multiple scattering; with `Strata/shaders/IBL/AtmosphereSkyView.comp.slang:16-51`, the quadratic steps |
| `render-direct:465` | code | home | `Strata/shaders/Scene/Skybox.frag.slang:12-50`: the sky background, the sun's disk as illuminance over solid angle, the fogged sky, the pre-exposure |
| `render-direct:467` | code | home | `Strata/shaders/Include/AerialPerspective.slang:17-26`: reading the froxel volume with a quadratic depth mapping |
| `render-direct:511-513` | figure | home | Diagrams: the atmosphere's tables; the environment refresh as a state machine |
| `render-direct:556` | figure | home | Sweep: times of day by `lighting.applySkyPreset {sunElevation}`, with `groundIlluminance` |
| `render-direct:559` | figure | home | Aerial perspective off and on, its scale 1 against 6 (Open World's mountains) |
| `render-direct:575` | rule | home | The sun's intensity is above the atmosphere under the Atmosphere source |
| `render-direct:618` | rule | home | Atmosphere table readers multiply by `EnvironmentParams.x` |
| `render-direct:664` | hands-on | home | Exercise: the transmittance at sunset on the CPU against `SceneRendererStats::SunTransmittance` |
| `new:53` | hands-on | home | Exercise (trace it yourself): a change of `AtmosphereHaze` followed with a debugger through `UpdateAtmosphere`: the settings kept finite, the transmittance and multiple-scattering tables dispatched again (counted in `AtmosphereTableUpdates`), the sky view, and the sun's transmittance computed again from `GetMedium`. Evidence: `Strata/src/Strata/Renderer/SceneRendererAtmosphere.cpp:195`, `:224-226`, `:232`, `:246-253`, `:341-344` |
| `render-direct:692` | term | home | The Beer-Lambert law (`light/clearcoat-transmission` links it) |
| `render-direct:744-752` | term | home | Physical atmosphere, Rayleigh and Mie scattering, ozone absorption, extinction, optical depth and transmittance, phase function and Henyey-Greenstein, single and multiple scattering, the tables, aerial perspective, storage scale |
| `render-direct:754` | term | home | In-scattering |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The sky light and its sources | `light/sky` | must |
| Compute shaders | `gpu/compute` | must |
| The exponential function and the number e | `basics/numbers` | must |
| Accumulating small steps | `basics/math-change` | must |
| The geometric series and its sum | `basics/math-interpolation` | must |
| Solid angle and directions on a sphere | `basics/math-sphere` | must |
| Lux and nits | `light/units-exposure` | must |
| Half-float subnormals | `basics/numbers` | must |
| 3D textures and trilinear filtering | `gpu/how-a-gpu-frame-works` | helps |
| The pre-exposure | `image/pre-exposure` | helps |

## `light/fog` — Height fog

**Covers.** The job: haze that thickens toward the ground, computed in closed form per pixel without a pass. The problem
and the approaches: distance fog, analytic height fog (Wenzel 2006, Unreal's exponential height fog), froxel volumetric
fog (Wronski 2014), with a table. The component `HeightFogComponent` in code: `Density`, `HeightFalloff`, `BaseHeight`,
`StartDistance`, `MaxOpacity`, `Color` as an albedo, `ColorFromSky`, `SunScattering`; the first active one applies, and
`SetHeightFog` keeps every value finite and subtracts the camera's height in double. The integral: the density falls as
exp(-falloff h); along a view ray it integrates in closed form (the diagram of density, ray and optical depth), written
so that no term overflows; the sky is fogged at an infinite distance; a falloff of 0 would make the integral toward the
sky endless, hence `c_MinHeightFalloff`. The fog's light: the sky's (the procedural horizon, an environment map's
irradiance from above, the atmosphere's horizon toward the ray, or the ambient color) and the sun's through the
Henyey-Greenstein phase. The fog is applied after aerial perspective. Its limits: no volume, so no light shafts, no
local lights and no shadows in fog ("What Strata does not do"). A toy compares the numeric and the closed-form integral.
Figures: sweeps of density and falloff, `SunScattering` 0 against 1 toward the sun, `ColorFromSky` off and on,
`MaxOpacity`, with a crop at the horizon. How it is tested: `GPU.SceneRenderer.Fog` (the integral matched, the sky at
infinity, density 0 bit-identical). Exercises: a valley fog tuned by its numbers; a second exponential layer added end
to end with an analytic test; a trace of `Density` from the component to the forward pass and the sky. Afterwards the
reader can tune fog by its parameters and derive its integral.

**Leaves out.**

- Extinction, transmittance and phase functions → `light/atmosphere`
- Aerial perspective → `light/atmosphere`
- Height fog in a game's look → `make/look`
- The first active component of a kind → `world/reflection`

**Fit.** `over`: about 4,500 words against M (3,000). The integral derived from zero, three excerpts and three exercises
pass M's top; by S2 the page takes L (5,000), whose range holds it.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-direct:167-169` | feature | home | The height fog component, the analytic integral, the fog's lighting |
| `render-direct:171` | feature | home | The fog's limits: no volume, no shafts, no local lights, no shadows |
| `render-direct:410` | concept | home | Fog: exponential height fog and aerial perspective; the mistakes |
| `render-direct:466` | code | home | `Strata/shaders/Include/Fog.slang:16-110`: the optical depth that cannot overflow, the in-scattering with Henyey-Greenstein, the blend, the sky at infinity |
| `render-direct:515` | figure | home | Diagram: the density against height, a view ray, the optical depth, the blend |
| `render-direct:560` | figure | home | Sweeps: density, falloff, `SunScattering` 0 against 1 toward the sun, `ColorFromSky` off and on, `MaxOpacity` |
| `render-direct:620-621` | rule | home | Height fog needs a falloff above 0; fog is not a volume |
| `render-direct:646` | hands-on | home | Exercise: valley fog, base at the floor, a 50 m layer, density that hides half at 35 m |
| `render-direct:663` | hands-on | home | Exercise: a second exponential layer end to end with an analytic test and a feature-test entry |
| `new:54` | hands-on | home | Exercise (trace it yourself): `HeightFogComponent::Density` followed with a search from the component through `SetHeightFog`, which fills the frame's `Fog*` constants, to `ApplyHeightFog` in the forward pass and `ApplyHeightFogToSky` behind it. Evidence: `Strata/src/Strata/Renderer/SceneRenderer.cpp:1405`, `:3296`; `Strata/shaders/Include/Fog.slang:7`, `:85`, `:100`; `Strata/shaders/Scene/Forward.frag.slang:445`; `Strata/shaders/Scene/Skybox.frag.slang:48` |
| `render-direct:753` | term | home | Height fog |
| `new:17` | not-done | home | Volumetric fog, light shafts and fog volumes: height fog has no volume. Evidence: `Strata/src/Strata/Renderer/RendererComponents.h:126-129`; `Strata/shaders/Include/Scene.slang:13-14` (SRVs 34 and 36 reserved); `Docs/Roadmap.md:948` |
| `new:18` | code | home | `Strata/src/Strata/Renderer/RendererComponents.h:126-151`: `HeightFogComponent`, its fields and `c_MinHeightFalloff` |
| `new:19` | code | home | `Strata/src/Strata/Renderer/SceneRenderer.cpp:1395-1445`: the first active fog, its values kept finite, the camera's height in double, which light the fog scatters |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Extinction, transmittance and the Henyey-Greenstein phase | `light/atmosphere` | must |
| Exponentials and their integrals | `basics/math-interpolation` | must |
| Overflow and the range of floats | `basics/numbers` | must |
| Where fog applies in the forward shader | `light/brdf` | must |
| Components and the first active one | `world/reflection` | helps |

## `light/clearcoat-transmission` — Transparency, clear coat and glass

**Covers.** The job: surfaces that are layered or let light through. The problem: car paint and varnish, glass that
bends what lies behind it, and surfaces that are only partly there; the approaches are layered BRDFs (Weidlich-Wilkie),
screen-space refraction from a copy of the image, and ray-traced refraction, with a table. First the home of
transparency: blending and premultiplied alpha from zero, why the order of transparent surfaces matters (the
back-to-front order is `draw/batching`'s), and why Blend surfaces are shaded after the opaque ones; one sentence gives
the HDR target's alpha convention (glass, unblended, writes alpha 1 as opaque writers do, and blended surfaces multiply
it by 1 - a; the why is `image/taa`'s). The clear coat in code: a dielectric layer of IOR 1.5 with its own strength,
roughness and normal map; the light it reflects no longer reaches the base (1 - F); image light on the coat by its
prefiltered Fresnel. Glass: `Transmission`, `IOR`, `Thickness` along the normal and the attenuation color and distance;
refraction (Snell's law and `refract`) to an exit point at the thickness scaled by the instance, a mip of the copy
chosen by roughness, Beer's absorption (linked to `light/atmosphere`), the surface's reflectance taken out (the glass
diagram and `TransmitLight`). How it is drawn: first in the transparent pass, unblended, writing depth, entity ids and
motion. The scene-color copy: half resolution, six levels, B10G11R11 or RGBA16F without extended storage formats, made
after the sky and read at SRV 19. The rule: glass is not in the prepass, so it gets no AO, casts no shadow, and the copy
holds no glass behind it. "What Strata does not do": water as an engine feature (water is a material with IOR 1.33),
reflections of and through transparent surfaces and glass behind glass, order-independent transparency. A toy blends two
layers. Figures: the Physics Playground's balls with coat roughness 0 against 0.5 and a coat normal map; its ball-pit
walls with IOR 1.0 against 1.5, `Thickness` 0 against 0.1 and an attenuation color. How it is tested: the
coat-over-metal furnace case, `GPU.SceneRenderer.Materials`, `PerfGPU.Renderer.Transmission`. The exercises make a glass
case with a colored liquid on a varnished base, and trace a material whose `Transmission` turns above 0 into the glass
draws and `TransmitLight`. The coat under rectangle lights is `light/area-lights`'. Afterwards the reader can author
coats and glass, and explain what transparency in Strata can and cannot show.

**Leaves out.**

- The transparent pass's back-to-front order → `draw/batching`
- Beer's law and transmittance → `light/atmosphere`
- Reflections on screen and their limits → `indirect/ssr`
- The coat under rectangle lights → `light/area-lights`
- The TAA's reactive mask for transparent surfaces → `image/taa`
- The sun's shadow on transparent surfaces → `light/sun-shadows-2`
- Glass and alpha modes in a game → `make/materials`

**Fit.** `fits`: about 4,800 words against L (5,000). Blending from zero, four excerpts and three entries of "What
Strata does not do" take the most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-direct:46-48` | feature | home | Clear coat, glass (transmission) and the scene-color copy |
| `render-direct:416` | concept | home | Layered materials and transmission; the limits and the mistakes |
| `render-direct:469` | code | home | `Strata/shaders/Scene/Forward.frag.slang:354-371`: `TransmitLight`, refraction to the exit point, the mip by roughness, Beer's law |
| `render-direct:516` | figure | home | Diagram: the refracted ray to the exit point, sampling the half-resolution copy at a roughness level |
| `render-direct:562-563` | figure | home | Sweeps: coat roughness and the coat normal map; glass IOR, thickness and attenuation color |
| `render-direct:622` | rule | home | Glass is not in the prepass |
| `render-direct:647` | hands-on | home | Exercise: a glass case with a colored liquid and a varnished wooden base |
| `new:55` | hands-on | home | Exercise (trace it yourself): a material whose `Transmission` turns above 0 followed with a search: `IsTransmissive` and the flags that make it transparent and transmissive, the extraction's glass batches drawn first in the transparent pass, unblended, and `TransmitLight` in the glass variant. Evidence: `Strata/src/Strata/Renderer/MaterialData.cpp:14-22`, `:35-38`; `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp:58`; `Strata/src/Strata/Renderer/SceneRenderer.cpp:2711-2725`; `Strata/shaders/Scene/Forward.frag.slang:354-371` |
| `render-direct:690-691` | term | home | Clear coat, transmission |
| `render-direct:693-694` | term | home | Attenuation color and distance, scene-color copy |
| `render-indirect:617` | term | home | Premultiplied alpha |
| `new:20` | not-done | home | Water as an engine feature: water is a material with IOR 1.33. Evidence: `Strata/src/Strata/Renderer/Material.h:59` |
| `new:21` | not-done | home | Reflections of and through transparent surfaces; glass behind glass. Evidence: `Docs/Roadmap.md:939-942, 947-948` |
| `new:22` | not-done | home | Order-independent transparency: glass shows only what was drawn before it. Evidence: `git grep -niE "order[- ]independent" 822a7a46 -- Strata/src Strata/shaders` finds nothing; `Docs/Roadmap.md:939-940` |
| `new:23` | code | home | `Strata/shaders/Include/PBR.slang:157-192`: the coat's data, its Fresnel and `EvaluateClearcoat` with the base's weight |
| `new:24` | code | home | `Strata/src/Strata/Renderer/SceneRendererGlass.cpp:107-129`: the scene-color copy, level 0 from the HDR target and each level from the one above |
| `new:25` | code | home | `Strata/src/Strata/Renderer/SceneRenderer.cpp:2711-2725`: glass drawn first in the transparent pass, unblended, into its own attachments |
| `render-direct:435` | code | use | `GetAbsorption`, Beer's absorption from the attenuation color; the excerpt's home is `light/material-data` |
| `render-direct:692` | term | link | The Beer-Lambert law; its home is `light/atmosphere` |
| `render-image:35` | feature | use | The HDR alpha convention, one sentence where glass and Blend surfaces are drawn: glass, unblended, writes alpha 1 as opaque writers do, and blended surfaces multiply it by 1 - a; the why is `image/taa`'s (`Strata/shaders/Scene/Forward.frag.slang:458-465`) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Energy compensation and the BRDF table | `light/energy` | must |
| Batching and the back-to-front order | `draw/batching` | must |
| The material model's coat and transmission fields | `light/materials` | must |
| Compute shaders | `gpu/compute` | must |
| Mip chains | `assets/textures` | must |
| The Beer-Lambert law | `light/atmosphere` | helps |
| The sun's shadow on transparent surfaces | `light/sun-shadows-2` | helps |
| Screen-space reflections | `indirect/ssr` | helps |

## Passed on

| Item | Type | To | Why |
| --- | --- | --- | --- |
| `render-direct:62` | feature | `indirect/ibl` | The horizon fade belongs to image light; `book.md` makes that page its home |
| `render-direct:63` | feature | `indirect/seam` | The probe-capture mode is part of the indirect light's join, which that page teaches |
| `render-direct:68` | feature | `draw/mirrors-camera-relative` | The home of mirrored transforms and their clockwise pipelines |
| `render-direct:102` | feature | `image/exposure` | The exposure model, EV100 and metering are that page's; `light/units-exposure` links it |
| `render-direct:103-104` | feature | `image/pre-exposure` | The pre-exposure and its settling are that page's mechanism; `light/units-exposure` gives one paragraph on why |
| `render-direct:106` | feature | `make/lighting` | `book.md` makes that page the home of the default template's lighting |
| `render-direct:181` | feature | `engineering/look-dev` | The home of the look-dev harness; `light/energy` uses its furnace shot |
| `render-direct:196` | feature | `indirect/ibl` | `EnvironmentResolution` sizes the prefiltered cube of the filter chain, which that page teaches |
| `render-direct:198` | feature | `reference/renderer` | The list of `SceneRendererSpecification` switches is that reference's; each light page uses the switches it tunes |
| `render-direct:204` | feature | `gpu/frame-tour` | The order of the frame's passes and stages is that page's; `light/brdf` draws the part's timeline from it |
| `render-direct:210` | feature | `reference/renderer` | The table of scene bindings is reference material; each light page names the slots it reads |
| `render-direct:228` | feature | `engineering/test-kinds` | The catalogue of the renderer's test suites is that page's; each light page's "How it is tested" quotes its own suite |
| `render-direct:287` | concept | `image/why-post` | The home of the HDR target and the chain; `basics/color` has the idea and the half-float range, `light/brdf` has `SanitizeHDR` |
| `render-direct:293` | concept | `image/exposure` | The concept is mostly exposure and EV100; its pre-exposure half is taught with `render-direct:103` on `image/pre-exposure` |
| `render-direct:468` | code | `image/pre-exposure` | `ChoosePreExposure` is that page's excerpt, as its outline row says |
| `render-direct:577` | rule | `image/pre-exposure` | Writers multiply by the pre-exposure and readers divide it out: the mechanism's rule |
| `render-direct:624` | rule | `image/exposure` | A real sun needs automatic exposure with MaxEV 16: an exposure setting |
| `render-direct:644` | hands-on | `make/lamps` | The lantern town moves a light with a script; track E meets the entity API of scripts only in part 15, and the page's outline row names the lantern |
| `render-direct:645` | hands-on | `make/reflections` | The day cycle is a script, which track E cannot write yet here; times of day are that page's subject |
| `render-direct:682` | term | `indirect/ibl` | `book.md` makes that page the home of the split sum |
| `render-direct:689` | term | `indirect/ibl` | The horizon fade's home |
| `render-direct:699-701` | term | `image/exposure` | EV100, middle gray and the exposure key are exposure's terms |
| `render-direct:702` | term | `image/pre-exposure` | The pre-exposure's home |
| `render-direct:703` | term | `basics/color` | The home of the half-float range; floating point itself is `basics/numbers`' |
| `render-direct:716` | term | `basics/math-projection` | One glossary entry with `foundation:634` on the page that teaches depth and reversed Z from zero (duplicates.md:30); `gpu/coordinates` keeps Strata's depth convention and links it |
| `render-direct:734-735` | term | `basics/math-probability` | The home of noise and sampling patterns, the Vogel disk and blue noise included |
| `render-direct:757` | term | `gpu/debugging` | One glossary entry with `render-scene:182` on the page that lists every debug view (duplicates.md:58); `light/measuring-light` links it |
| `render-direct:758` | term | `gpu/readback-timing` | The home of GPU timestamps and stages |
| `render-direct:811` | open | `nowhere` | A note about the files the survey did not read |
| `render-direct:820` | open | `nowhere` | A note that exposure metering was only skimmed; render-image surveys it |
| `render-direct:822` | open | `gpu/frame-tour` | Forward against deferred is that page's; it must state the trade-off without a motive the documents do not give (`light/many-lights` follows it) |
| `render-direct:824` | open | `indirect/ibl` | The release of the horizon fade, for that page's `since` |
| `render-direct:835` | open | `nowhere` | A note on how far the survey checked which samples show which features; each figure's recipe checks its scene |
| `render-direct:841` | open | `nowhere` | Repeats `render-direct:627`, which `light/sun-shadows-1` homes |

## Not taken

none

## Questions for the planner

none
