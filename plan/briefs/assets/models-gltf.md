# Brief: `assets/models-gltf`

| Field | Value |
| --- | --- |
| Title | Models and the glTF importer |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `assets/texture-cooking`, `gpu/geometry-pool`, `world/prefabs` |
| From | assets |
| Unit | `plan/allocation/assets.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `assets/models-gltf` — Models and the glTF importer

**Covers.** The job: turn a `.gltf` or `.glb` file into a model, an entity template that instantiates into scenes, and
its sub-assets: meshes with levels of detail and skins, materials, textures, a skeleton and clips. The problem takes one
paragraph: the interchange formats (glTF, FBX, OBJ, USD), and why Strata reads glTF only (it is open, its materials are
PBR, and it shares Strata's conventions: right-handed, +Y up, counter-clockwise front faces, meters). The map:
`GltfImporter` (cgltf parses, meshoptimizer decodes and simplifies), `MeshUtils` (indices and levels of detail),
`TextureImporter::Decode` (embedded and external images), `Model` (the Scene module's template), `Mesh`'s cooked form,
the material document, and the skeleton and clips of the animation part. The contract: the sub-asset keys; the settings
(Scale, GenerateLODs, LODCount, OptimizeMeshes, ImportMaterials, BaseColorFactorsAreSRGB, ImportCameras, ImportLights,
MaxTextureSize, TextureCompression, TextureQuality) and their inactive reasons; external files only inside the asset
directory, read through `ReadImportDependency`, so a changed image imports its model again; and a table of what is
supported and what is not, with the warning each gives (the Asset tab and `importWarnings` of `asset.info` show them):
the supported extensions (lights, emissive strength, unlit, clear coat, transmission, volume, IOR, texture transform,
mesh quantization, meshopt compression); a required extension outside that list fails the import; skipped or clamped
with a warning are primitives with only Draco data, KTX2 and WebP images, textures on a second UV set, texture
rotation, different wrap modes for the two axes, `EXT_mesh_gpu_instancing`, skin influences beyond the four strongest,
an IOR above 3, morph targets, vertex colors, extra scenes and specular-glossiness materials. A toy of about 50 lines
reads a one-triangle glTF (its JSON, a base64 buffer, an accessor) into positions and indices.

The real code: the header's description and its version history (11 at the pin; `Docs/Architecture.md` still says 9);
`Run`, the order of an import with its cancel checks (materials, skeleton, meshes, animations, the model);
`ImportMaterial` (factors, alpha modes, one texture sub-asset per image, usage and sampler, the clear coat and
transmission extensions, `BaseColorFactorsAreSRGB`); `ImportMesh` (the scale baked into positions before bounds and
levels of detail; what it makes when a file lacks vertex data: missing normals become flat face normals on unwelded
triangles, missing tangents with UVs become exact per-corner MikkTSpace tangents, which split vertices on UV seams and
mirror lines, and without UVs any tangent perpendicular to the normal is used; levels with their errors, where a
paragraph of about 150 words says what simplification keeps: `MeshUtils::GenerateLODs` calls meshoptimizer's
`meshopt_simplifyWithAttributes`, which removes edges while the error stays under `c_MaxLODError` (0.02 of the mesh's
extent), weighs normals and texture coordinates so that seams stay closed, keeps open borders in place, and records each
level's error; the further reading names Garland and Heckbert's paper on quadric error metrics, which the simplifier
cites); `BuildModel` (the root keeps scale 1; an animator on the root); and the cooked mesh form (`STMH` version 3). The
references and bounds the importer records are named and linked to `assets/references`. What Strata does not do: OBJ
and FBX. Then the alternatives, the tests (`Asset.Gltf`), and changing it safely (bump the version; derive new
sub-assets' handles with `DeriveSubAssetHandle`; never change a key). Exercises: import a glTF with its textures, read
its sub-assets and their keys, and place it; trace it yourself: a breakpoint in `ImportMesh` on a model without tangents
shows which branch makes them.

**Leaves out.**

- Skeletons, skins and clips as the animation system builds them → `animation/importing`
- Meshes on the GPU and the geometry pool → `gpu/geometry-pool`
- Choosing a level of detail at draw time → `draw/lod`
- Models and prefabs as entity templates → `world/prefabs`
- PBR material fields and what they mean → `light/materials`
- Importing a model as a game maker → `make/assets`

**Fit.** `fits`: about 5,070 words against L (5,000). Six excerpts carry the page, since the inventory read the importer
by its header only; the table of what the importer supports and skips comes next, and the toy stays short.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `assets:158` | feature | home | The glTF importer: what it makes, its settings, `Scale` baked into the content, external files, version 11 |
| `assets:613` | hands-on | home | Import a model and textures, read the sub-assets, place it |
| `new:4` | code | home | `Strata/src/Strata/Asset/GltfImporter.h:8-39`: what an import makes, its keys and settings, the version history |
| `new:5` | code | home | `Strata/src/Strata/Asset/GltfImporter.cpp:236-286`: `Run`, the order of the import and its cancel checks |
| `new:6` | code | home | `Strata/src/Strata/Asset/GltfImporter.cpp:791-856`: `ImportMaterial`, factors, alpha modes and one texture per usage |
| `new:7` | code | home | `Strata/src/Strata/Asset/GltfImporter.cpp:1538-1560`: levels of detail with their errors (the scale before them at 1427-1433) |
| `new:29` | feature | home | What `ImportMesh` makes when a glTF lacks vertex data, about 200 words: missing normals become flat face normals on unwelded triangles; missing tangents with UVs become exact per-corner MikkTSpace tangents (`MeshUtils::GenerateSeamTangents`), which split vertices on UV seams and mirror lines; without UVs any tangent perpendicular to the normal is used; `light/materials` links it where normals and tangents enter. Evidence: `Strata/src/Strata/Asset/GltfImporter.cpp:1472-1531`; `Strata/src/Strata/Renderer/Mesh.h:182-192` |
| `new:30` | feature | home | What the importer supports and skips, as a table with the warning each gives (the Asset tab and `importWarnings` of `asset.info`), about 250 words: a required extension outside the supported list fails the import; primitives with only Draco data, KTX2 (basisu) and WebP images, textures on a second UV set, texture rotation, different wrap modes for the two axes, `EXT_mesh_gpu_instancing`, skin influences beyond the four strongest and an IOR above 3 are skipped or clamped; supported are lights, emissive strength, unlit, clear coat, transmission, volume, IOR, texture transform, mesh quantization and meshopt compression. Evidence: `Strata/src/Strata/Asset/GltfImporter.cpp:46-53`, `:309-320`, `:733-742`, `:755`, `:844`, `:897-902`, `:1252`, `:1402-1406`, `:1795`; `StrataEditor/src/Editor/EditorAssetCommands.cpp:703` |
| `new:31` | hands-on | home | Trace it yourself (D27): a breakpoint in `ImportMesh` on a model without tangents shows which branch makes them (MikkTSpace with UVs, any perpendicular without), and the vertex count before and after. Evidence: `Strata/src/Strata/Asset/GltfImporter.cpp:1472-1531` |
| `new:8` | code | home | `Strata/src/Strata/Asset/GltfImporter.cpp:1972-2007`: `BuildModel`, the model as an entity template whose root keeps scale 1 |
| `new:9` | code | home | `Strata/src/Strata/Renderer/Mesh.h:106-113`: the cooked mesh form `STMH` version 3, which no inventory surveyed |
| `new:10` | not-done | home | No OBJ or FBX import: models are glTF only. Evidence: `Strata/src/Strata/Asset/AssetImporters.cpp:159-177` (`RegisterAssetPipeline` registers no other model importer); `Docs/Releases/0.7.0.md:414-415` |
| `new:11` | erratum | home | `Docs/Architecture.md` gives the glTF importer as version 9; it returns 11. Evidence: `Docs/Architecture.md:2626`; `Strata/src/Strata/Asset/GltfImporter.h:39` |
| `new:12` | erratum | home | The assets inventory places the sub-asset keys at `GltfImporter.h:262-282`, the importer at `:262-309` and its estimate at `:303-308`, but the header has 57 lines. Evidence: `Strata/src/Strata/Asset/GltfImporter.h:10-21` (keys), `:29-55` (the class), `:49-52` (`EstimateImportMemory`) |
| `assets:45` | feature | use | The sub-asset keys a model makes |
| `assets:117` | feature | use | The references and bounds the importer records (taught in `assets/references`) |
| `assets:526` | rule | use | The version bump of both importers |
| `animation:68` | feature | use | The importer's version, as the animation part sees it |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Importers, settings, confined reads and versions | `assets/importing` | must |
| Sub-assets and derived handles | `assets/handles-meta` | must |
| Texture usages, and how images are cooked | `assets/texture-cooking` | must |
| Meshes on the GPU: vertices, indices, submeshes, the geometry pool | `gpu/geometry-pool` | must |
| Entity templates: models and prefabs | `world/prefabs` | must |
| JSON and Base64 | `basics/data-formats` | must |
| Transforms, hierarchies and right-handed axes | `basics/math-matrices` | must |
| Counter-clockwise front faces | `gpu/coordinates` | helps |
| Levels of detail and their error | `draw/lod` | helps |
| Skeletons, skins and clips | `animation/skeletons` | helps |
| PBR material fields | `light/materials` | helps |
| References and bounds an import records | `assets/references` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

None: the glossary homes no term on this page.
