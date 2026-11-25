# Brief: `light/materials`

| Field | Value |
| --- | --- |
| Title | Strata's material model |
| Kind | C |
| Size | L |
| Tracks | E |
| Needs | `assets/textures`, `basics/math-bases`, `light/units-exposure` |
| From | render-direct ch. 2 (the model, the maps, alpha modes, emission in nits, plausible albedos, IOR as a field, normal maps and tangent space as a concept) |
| Unit | `plan/allocation/light.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `albedo` | Albedo | base color |
| `metallic` | Metallic | - |
| `perceptual-roughness` | Perceptual roughness | - |
