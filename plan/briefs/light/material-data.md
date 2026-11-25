# Brief: `light/material-data`

| Field | Value |
| --- | --- |
| Title | From a material file to the shader: the material record and its textures |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `light/materials`, `gpu/binding`, `assets/loading` |
| From | new; the GPU half of render-direct ch. 2, which a concept page cannot hold: 1.1 (GPU rows), code #2-#5, figure 5, rules 7-9 and 14 (`MaterialGPU::Build`, the 144-byte `MaterialData`, the texture table, the XY normal decode) |
| Unit | `plan/allocation/light.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

None: the glossary homes no term on this page.
