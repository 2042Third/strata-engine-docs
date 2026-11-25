---
id: assets/models-gltf
title: "Models and the glTF importer"
description: "How Strata turns a glTF file into a model with meshes, materials, textures, a skeleton and clips, and what it repairs, skips or refuses."
kind: internals
size: L
tracks: [E]
needs: [assets/texture-cooking, gpu/geometry-pool, world/prefabs]
time: 80
learn:
  - id: import-result
    text: name the sub-assets a glTF import makes and explain how their keys give each one a stable handle
  - id: settings
    text: choose the import settings for scale, levels of detail and textures for a given file
  - id: support
    text: name which glTF features the importer reads, which it skips with a warning and which it refuses
  - id: mesh-repair
    text: predict what the importer makes for a mesh without normals or tangents
  - id: change-safely
    text: explain when a change to the importer needs a new version and how a new sub-asset gets its handle
since: 0.3.0
status: final
---

An artist makes a 3D model in a program such as Blender and saves it in a file. The game needs that model as data it can draw: triangles, the materials that color them, the images those materials use, and sometimes a skeleton and animations. The **glTF importer** is the code that reads a `.gltf` or `.glb` file and produces all of that. It makes one model, an entity template that you place in scenes, and the :term[sub-assets]{id=sub-asset} the template uses: meshes with levels of detail, materials, textures, a skeleton and clips. It does not draw anything, it does not choose a level of detail at run time, and it reads no other model format.

## The problem and how engines solve it

Every 3D program has its own way to store a model, and the formats differ in what they keep. A :term[game engine]{id=game-engine} has to read the files that artists make.

Four formats are common. `OBJ` is old and simple: it holds triangles and names of materials, but no skeleton and no modern materials. `FBX` is a closed format owned by one company; it holds animation and skins, but its specification is not public, so engines depend on a vendor library. `USD` is a large open format made for film studios; it describes whole scenes with layers and is powerful but heavy. glTF is an open format made for sending models to programs that draw them.

Strata reads glTF only, for three reasons. The format is open and small, so a person can read the specification and the engine can include a :term[parser]{id=parser}, `cgltf`, instead of a vendor library. Its materials are described as physically based rendering (PBR), the same model that Strata's materials follow, so a material arrives without translation. And glTF shares Strata's conventions: :term[right-handed]{id=handedness} axes, +Y up, counter-clockwise :term[front faces]{id=winding-order} and meters. The :term[importer]{id=importer} applies no conversion besides an optional uniform scale.

The choice has a cost. An artist whose program saves only `FBX` or `OBJ` must convert the file first, and Strata offers no importer for them. Other engines read many formats; the price is a large body of code that handles each format's habits. Strata keeps one importer and makes it complete. The rest of this page shows what that importer makes, what it promises, and what it repairs, skips or refuses.

## The map

An import is a function from the :term[bytes]{id=byte} of one file to a set of results. The importer is a class, `GltfImporter`, in `Strata/src/Strata/Asset/GltfImporter.cpp`. Other pieces do the work that the class delegates, as the diagram shows.

```mermaid caption="The importer parses the file, then hands each kind of data to the code that owns it; every result is stored as a sub-asset of the model." alt="A flow from the glTF file through the importer to six results. A parser and a decoder read the file. Images go to the texture code, materials to the material document, and meshes to the mesh functions and the cooked mesh form. The skeleton and clips go to the animation part, and the model is the main result."
flowchart LR
    F["glTF file"] --> P["cgltf parses; meshoptimizer decodes"]
    P --> M["GltfImporter"]
    M --> T["TextureImporter::Decode: images"]
    M --> D["Material document"]
    M --> U["MeshUtils: indices and levels of detail"]
    U --> C["Mesh cooked form STMH"]
    M --> A["Skeleton and clips (animation)"]
    M --> O["Model: entity template"]
```

Each box has one job. `cgltf` parses the :term[JSON]{id=json} and the binary chunk. `meshoptimizer` decodes buffers that the file compressed and simplifies meshes. `TextureImporter::Decode` turns an embedded or external image into a cooked texture, the way [texture cooking](texture-cooking.md) taught.

`MeshUtils` is a set of functions for the mesh data: it sorts indices for the :term[graphics processing unit]{id=gpu} (GPU) caches, makes tangents and builds levels of detail. `Mesh` has the cooked form that is stored. The skeleton and the clips belong to the animation part, covered in [importing animation](../animation/importing.md).

The importer runs on a background job, never on the :term[main thread]{id=main-thread}, and it must never trust the file: the file can be damaged or hostile. Every size it reads is checked, and the geometry an import may expand is limited relative to the bytes it loaded.

## The contract

### What an import makes

The model is the result the file stands for. Like a prefab, which [Prefabs](../world/prefabs.md) taught, it is an entity template: one entity per glTF node, with a transform, a mesh renderer, a camera or a light where the node has them. The sub-assets are the assets the model refers to. Each has a **key**, a text that names it within the model, and its handle follows from the key through `DeriveSubAssetHandle`, as [handles and sub-assets](handles-meta.md) taught. Because the same key gives the same handle on every machine and in every import, scenes that refer to a sub-asset keep working when the file is imported again.

The :term[header]{id=header} of the importer states the keys. The version history of the importer stands below them.

```cpp src="Strata/src/Strata/Asset/GltfImporter.h#L35-L40"
// 6: skins, animations and skinned meshes; 7: buffer views compressed with EXT_meshopt_compression too.
// 8: the import scale is baked into the content instead of the model root's scale.
// 9: levels of detail are simplified with their normals and texture coordinates, with their errors (cooked meshes
// version 3). 10: clear coat, transmission, volume and index of refraction (KHR_materials_clearcoat, _transmission,
// _volume, _ior). 11: BaseColorFactorsAreSRGB.
uint32_t GetVersion() const override { return 11; }
```

The history lists what changed in each version. Version 6 added skins and animations. Version 8 moved the import scale into the content. Version 9 made the levels of detail weigh normals and :term[texture coordinates]{id=texture-coordinates}.

Version 10 added clear coat, transmission, volume and `IOR`. Version 11 added the `BaseColorFactorsAreSRGB` setting. The importer returns 11 at the pin; `Docs/Architecture.md` still says 9, which is an error in that document.

| Key | What it is |
| --- | --- |
| `Mesh/<n>` | One `Mesh` for glTF mesh number n, one :term[submesh]{id=submesh} per primitive, with levels of detail |
| `Mesh/<n>/Skin/<s>` or `Mesh/<n>/Rigid` | A further mesh when nodes draw mesh n with another skin, or with and without one |
| `Material/<n>` | One material document for glTF material n |
| `Texture/<i>/<usage>/<sampler>` | One cooked texture for image i, per use and sampler |
| `Skeleton` | The joints of every skin and of every node an animation moves, with their ancestors |
| `Animation/<name>` | One clip per animation; `Animation/<index>` when the name is missing or repeated |

The texture key carries two decisions. The usage is `Color`, `NormalMap` or `Data`, because a texture is cooked differently for each use: color is stored as :term[sRGB]{id=srgb}, :term[normal maps]{id=normal-map} are scaled back to length 1, data is linear. The sampler is two digits: the wrap mode (0 Repeat, 1 Clamp, 2 Mirror), then the filter (0 Linear, 1 Nearest). The key `Texture/0/Color/00` is the first image, cooked as color, repeating and filtering linearly. If one image serves as color in one material and as data in another, the model gets two textures from it.

:::example
A crate model has one mesh, one material and three images: a color image (0), a normal image (1) and a metallic-roughness image (2). The importer makes `Mesh/0`, `Material/0`, `Texture/0/Color/00`, `Texture/1/NormalMap/00` and `Texture/2/Data/00`, six assets with the model. If the file has an animation named `Open` and a skeleton, `Skeleton` and `Animation/Open` appear too. Importing the file again after you change only the color image gives the same keys, so the same handles; the scene that holds the crate keeps its references.
:::

### The settings

The settings are the part of the import you choose. They live in the asset's :term[import settings]{id=import-settings}, which the asset's inspector edits and the command `asset.setImportSettings` accepts. Their defaults produce a good import of an ordinary file.

| Setting | Default | What it does |
| --- | --- | --- |
| `Scale` | 1 | A uniform scale baked into the content; the inspector offers 0.0001 to 10000, and a value that is not positive warns and uses 1 |
| `GenerateLODs` | on | Makes simplified versions of every mesh |
| `LODCount` | 3 | How many simplified versions, up to 8 |
| `OptimizeMeshes` | on | Sorts vertices and triangles for the GPU's caches |
| `ImportMaterials` | on | Imports materials and their textures; off uses the default material |
| `BaseColorFactorsAreSRGB` | off | Reads the base color factors as sRGB values and converts them to linear |
| `ImportCameras`, `ImportLights` | on | Imports the model's cameras and punctual lights as components |
| `MaxTextureSize` | 0 | The longest side of the model's textures; 0 means only the engine's limit |
| `TextureCompression` | `Auto` | `Auto` or `Uncompressed`, as for a texture asset |
| `TextureQuality` | `High` | `High` or `Fast`, as for a texture asset |

Some settings only matter when another is on. `GetInactiveReason` says why a setting is inactive, and the editor shows the reason. `LODCount` is inactive without `GenerateLODs`. The three texture settings and `BaseColorFactorsAreSRGB` are inactive without `ImportMaterials`, because the textures belong to the materials. `TextureQuality` is also inactive when `TextureCompression` is `Uncompressed`, since quality only chooses how :term[block compression]{id=block-compression-bc1-bc7} encodes.

`BaseColorFactorsAreSRGB` exists because some exporters write color numbers that are already sRGB where glTF expects linear numbers. Take a factor of 0.5. Read as linear, it stays 0.5 and the surface looks too bright. Read as sRGB, it converts to about 0.214, which is what the artist saw. The importer applies the standard sRGB curve to the three :term[color channels]{id=color-channel}; the alpha is linear either way.

### Files outside the model

A `.gltf` file can name external buffers and images. The importer reads them only through `ReadImportDependency`, the function from [Importing](importing.md) that confines reads to the asset folder and records each file as a dependency. A `URL` or an :term[absolute path]{id=absolute-path} fails the import. A missing file, or one outside the asset folder, fails it with a message that says so. Because the model records its dependencies, changing an image on disk imports the model again.

`FindExternalFiles` lists those `uri` values without importing, which is how the editor copies a model together with the files it reads. Data `uri` values and the binary chunk of a `.glb` are no files.

### What is supported and what is not

A glTF file lists the extensions it uses and the extensions it requires. A required extension that the importer does not know fails the import, because the file could not look right without it. A used but optional extension that the importer does not know is skipped, and the import adds a warning that says what was not imported. Warnings do not stop an import. The command `asset.info` returns them as `importWarnings`, and the editor's asset inspector shows them.

| Feature | What the importer does |
| --- | --- |
| `KHR_lights_punctual`, `KHR_materials_emissive_strength`, `KHR_materials_unlit`, `KHR_materials_clearcoat`, `KHR_materials_transmission`, `KHR_materials_volume`, `KHR_materials_ior`, `KHR_texture_transform`, `KHR_mesh_quantization`, `EXT_meshopt_compression` | Reads them |
| A required extension not on that list | Fails the import |
| A primitive with only `Draco` data | Skips the primitive with a warning; fallback data, when present, is imported |
| `KTX2` and `WebP` images | The texture is skipped with a warning |
| A texture on a second set of texture coordinates | The texture is skipped with a warning |
| Texture rotation | Ignored with a warning |
| Different wrap modes for the two axes | Uses the horizontal mode with a warning |
| `EXT_mesh_gpu_instancing` | Not imported, with a warning |
| Skin influences beyond the four strongest | Dropped with a warning |
| An `IOR` above 3 | Clamped to 3 with a warning |
| Morph targets, vertex colors, extra scenes | Not imported, with a warning |
| Specular-glossiness materials | Default metallic-roughness values with a warning |

Two points of the table need a reason. A model's images must be PNG or JPEG; the importer checks the bytes, not the file name, and another format is skipped with the message that the image is not PNG or JPEG. And only one scene of a file is imported: without a scene, every root node belongs to the model, and extra scenes are reported.

:::rule
**Bump `GetVersion()` whenever an importer's output changes.** Otherwise every project keeps stale caches that look current. The rule is in `AGENTS.md`; the cost of ignoring it is a project that shows old meshes until someone deletes its cache. See [importing](importing.md).
:::

## A toy version

:::question
New to calls such as `std::memcpy(`, to pointers and to casts? See [programming 3](../basics/programming-3.md), [memory](../basics/cpp-memory.md) and [modern C++](../basics/cpp-modern.md) first.
:::

The toy reads the smallest useful file: a glTF with one triangle. The JSON names a buffer whose bytes sit in the file as :term[base64]{id=base64} text, two buffer views that cut that buffer into pieces, and two accessors that say how to read each piece. The toy decodes the base64 text, finds the byte offsets and counts, and reads three positions and three indices. It finds numbers by searching the text, which works for this layout only; the real importer parses the JSON as a tree through `cgltf`.

```cpp sketch="assets-models-gltf-toy.cpp"
// A toy glTF reader: one triangle, a base64 buffer, two accessors.
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

static const char* s_Document = R"({
  "asset": { "version": "2.0" },
  "buffers": [ { "byteLength": 44, "uri": "data:application/octet-stream;base64,AAAAAAAAAAAAAAAAAACAPwAAAAAAAAAAAAAAAAAAgD8AAAAAAAABAAIAAAA=" } ],
  "bufferViews": [ { "buffer": 0, "byteOffset": 0, "byteLength": 36 }, { "buffer": 0, "byteOffset": 36, "byteLength": 6 } ],
  "accessors": [
    { "bufferView": 0, "componentType": 5126, "count": 3, "type": "VEC3" },
    { "bufferView": 1, "componentType": 5123, "count": 3, "type": "SCALAR" } ]
})";

// Every number that follows the key, in file order. A real parser reads the JSON tree; the toy trusts this layout.
static std::vector<size_t> NumbersAfter(const std::string& text, const std::string& key)
{
	std::vector<size_t> numbers;
	for (size_t at = text.find(key); at != std::string::npos; at = text.find(key, at + 1))
		numbers.push_back(std::strtoul(text.c_str() + at + key.size() + 1, nullptr, 10));
	return numbers;
}

static std::vector<uint8_t> DecodeBase64(const std::string& text)
{
	const std::string alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
	std::vector<uint8_t> bytes;
	uint32_t bits = 0;
	int count = 0;
	for (char letter : text)
	{
		const size_t value = alphabet.find(letter);
		if (value == std::string::npos)
			break; // The padding "=" ends the data
		bits = (bits << 6) | static_cast<uint32_t>(value);
		count += 6;
		if (count >= 8)
		{
			count -= 8;
			bytes.push_back(static_cast<uint8_t>((bits >> count) & 0xFF));
		}
	}
	return bytes;
}

int main()
{
	const std::string document = s_Document;
	const std::string marker = "base64,";
	const size_t start = document.find(marker) + marker.size();
	const std::vector<uint8_t> buffer = DecodeBase64(document.substr(start, document.find('"', start) - start));

	const std::vector<size_t> offsets = NumbersAfter(document, "\"byteOffset\":");
	const std::vector<size_t> counts = NumbersAfter(document, "\"count\":");
	std::printf("buffer: %zu bytes\n", buffer.size());

	// Accessor 0: three float triples (VEC3, componentType 5126) starting at the first view's offset.
	for (size_t vertex = 0; vertex < counts[0]; vertex++)
	{
		float position[3];
		std::memcpy(position, buffer.data() + offsets[0] + vertex * sizeof(position), sizeof(position));
		std::printf("position %zu: (%g, %g, %g)\n", vertex, position[0], position[1], position[2]);
	}

	// Accessor 1: three 16-bit unsigned integers (SCALAR, componentType 5123) from the second view.
	for (size_t corner = 0; corner < counts[1]; corner++)
	{
		uint16_t index;
		std::memcpy(&index, buffer.data() + offsets[1] + corner * sizeof(index), sizeof(index));
		std::printf("index %zu: %u\n", corner, static_cast<unsigned>(index));
	}
	return 0;
}
```

```text output-of="assets-models-gltf-toy.cpp"
buffer: 44 bytes
position 0: (0, 0, 0)
position 1: (1, 0, 0)
position 2: (0, 1, 0)
index 0: 0
index 1: 1
index 2: 2
```

1. **Lines 9–16:** the file's JSON; the buffer is a data address that holds the bytes as base64 text, where a `.glb` keeps them in a binary chunk.
2. **Lines 19–25:** `NumbersAfter` collects every number that follows a key, which stands in for a real JSON parser.
3. **Lines 27–47:** `DecodeBase64` turns each letter into 6 bits and emits a byte whenever 8 bits are ready.
4. **Line 64:** the 12 bytes of one position are copied from the buffer at the first view's offset.
5. **Line 72:** the 2 bytes of one index are copied from the second view's offset.

The program prints what it found: the buffer size, then the two kinds of data. The buffer holds 44 bytes: 36 bytes for three positions of three 4-byte floats, 6 bytes for three 2-byte indices, and 2 bytes of padding that keep the data aligned. The accessor with `componentType` 5126 reads floats; 5123 reads 16-bit :term[unsigned integers]{id=unsigned-integer}. These two lists are what a mesh is: vertex positions and indices that say which three positions form each triangle.

## The real code

### The order of an import

`Run` is the function that the importer calls for one file. Read it for the order of the work and for the places where a cancelled import stops.

```cpp src="Strata/src/Strata/Asset/GltfImporter.cpp#L236-L286"
bool Run(std::string* outError)
{
	m_Settings = ReadSettings(m_Context.Settings, m_Result.Warnings);
	if (!Load(outError))
		return false;

	// A cancelled import stops between a model's materials (whose textures take the longest) and meshes.
	if (m_Settings.ImportMaterials)
	{
		for (cgltf_size index = 0; index < m_Data->materials_count; index++)
		{
			if (m_Context.IsCancelled())
				return Fail(outError, "cancelled");
			ImportMaterial(index);
		}
	}

#if ST_WITH_ANIMATION
	// The skeleton first: skinned meshes bind to its joints.
	ImportSkeleton();
#endif

	for (cgltf_size index = 0; index < m_Data->meshes_count; index++)
	{
		if (m_Context.IsCancelled())
			return Fail(outError, "cancelled");
		// One mesh per skin it is drawn with (glTF lets nodes draw a mesh with different skins, or without one).
		const std::vector<const cgltf_skin*>& skins = m_MeshSkins[index];
		for (size_t use = 0; use < skins.size(); use++)
		{
			const std::string key = use == 0 ? fmt::format("Mesh/{}", index)
				: fmt::format("Mesh/{}/{}", index, skins[use] ? fmt::format("Skin/{}", cgltf_skin_index(m_Data.get(), skins[use])) : std::string("Rigid"));
			ImportMesh(index, skins[use], key);
		}
	}

#if ST_WITH_ANIMATION
	if (m_Context.IsCancelled())
		return Fail(outError, "cancelled");
	ImportAnimations();
#endif

	if (m_Context.IsCancelled())
		return Fail(outError, "cancelled");
	if (!BuildModel(outError))
		return false;

	for (const std::string& feature : m_SkippedFeatures)
		m_Result.Warnings.push_back(fmt::format("Not imported: {}", feature));
	return true;
}
```

1. **Line 238:** the settings are read first; a bad value becomes a warning and the default is used.
2. **Lines 243–250:** materials go first, because their textures take the longest to decode. The cancel check sits between materials, so the editor can abandon a long import without waiting.
3. **Line 255:** the skeleton comes before the meshes, because a skinned mesh binds to the skeleton's joints.
4. **Lines 266–268:** the first use of a mesh is `Mesh/<index>`; each further use, with another skin or none, gets a longer key.
5. **Lines 278–281:** the model is built last, when every handle it refers to exists. Warnings for skipped features are added at the end.

The toy has none of this: it has no cancel checks, no skeleton, no keys. The real code separates the work into steps so that a failure in one step does not leave half a model behind: a failing import returns an error and produces no results.

### Materials

A glTF material lists factors (numbers) and textures. `ImportMaterial` copies the factors into Strata's material properties and asks for one texture per slot. The code is long; read the lines that clamp, decode and choose a usage.

```cpp src="Strata/src/Strata/Asset/GltfImporter.cpp#L797-L835"
if (source.has_pbr_specular_glossiness && !source.has_pbr_metallic_roughness)
	Warn(fmt::format("Material '{}' uses the specular-glossiness workflow, which is not supported; using metallic-roughness defaults", name));

const cgltf_pbr_metallic_roughness& pbr = source.pbr_metallic_roughness;
properties.BaseColor = glm::make_vec4(pbr.base_color_factor);
// Some exporters (Kenney's kits among them) write sRGB-encoded bytes where glTF expects linear factors: the setting
// decodes them (the alpha is linear either way).
if (m_Settings.BaseColorFactorsAreSRGB)
{
	for (int channel = 0; channel < 3; channel++)
	{
		const float encoded = std::clamp(properties.BaseColor[channel], 0.0f, 1.0f);
		properties.BaseColor[channel] = encoded <= 0.04045f ? encoded / 12.92f : std::pow((encoded + 0.055f) / 1.055f, 2.4f);
	}
}
properties.Metallic = std::clamp(pbr.metallic_factor, 0.0f, 1.0f);
properties.Roughness = std::clamp(pbr.roughness_factor, 0.0f, 1.0f);
properties.EmissiveColor = glm::make_vec3(source.emissive_factor);
properties.EmissiveIntensity = source.has_emissive_strength ? source.emissive_strength.emissive_strength : 1.0f;
properties.DoubleSided = source.double_sided;
properties.Unlit = source.unlit;
switch (source.alpha_mode)
{
	case cgltf_alpha_mode_mask:  properties.AlphaMode = MaterialAlphaMode::Mask; break;
	case cgltf_alpha_mode_blend: properties.AlphaMode = MaterialAlphaMode::Blend; break;
	default:                     properties.AlphaMode = MaterialAlphaMode::Opaque; break;
}
properties.AlphaCutoff = std::clamp(source.alpha_cutoff, 0.0f, 1.0f);

properties.BaseColorMap = ImportTexture(pbr.base_color_texture, TextureUsage::Color, "base color", name);
properties.MetallicRoughnessMap = ImportTexture(pbr.metallic_roughness_texture, TextureUsage::Data, "metallic-roughness", name);
properties.NormalMap = ImportTexture(source.normal_texture, TextureUsage::NormalMap, "normal", name);
if (source.normal_texture.texture)
	properties.NormalScale = source.normal_texture.scale;
properties.OcclusionMap = ImportTexture(source.occlusion_texture, TextureUsage::Data, "occlusion", name);
if (source.occlusion_texture.texture)
	properties.OcclusionStrength = std::clamp(source.occlusion_texture.scale, 0.0f, 1.0f);
properties.EmissiveMap = ImportTexture(source.emissive_texture, TextureUsage::Color, "emissive", name);
ImportClearcoatAndTransmission(source, name, properties);
```

1. **Lines 797–798:** a material of the old specular-glossiness method gets metallic-roughness defaults and a warning.
2. **Lines 804–811:** the sRGB conversion from the contract, using the curve's two pieces: a line near zero and a power of 2.4 above.
3. **Lines 812–813:** metallic and roughness are clamped to the range 0 to 1, so a file with a wrong number cannot break the :term[shader]{id=shader}.
4. **Lines 826–834:** each slot asks for a texture with the usage that suits it: the base color and the light a surface gives off as `Color`. The normal slot gets `NormalMap`, and metallic-roughness and occlusion get `Data`.
5. **Line 835:** clear coat, transmission, volume and `IOR` are read by a second function.

The texture call also builds the key you saw in the contract.

```cpp src="Strata/src/Strata/Asset/GltfImporter.cpp#L751-L759"
if (texture.sampler)
{
	settings.Wrap = ToTextureWrap(texture.sampler->wrap_s);
	if (texture.sampler->wrap_t != texture.sampler->wrap_s)
		m_SkippedFeatures.insert("different horizontal and vertical texture wrap modes");
	settings.Filter = texture.sampler->mag_filter == cgltf_filter_type_nearest ? TextureFilter::Nearest : TextureFilter::Linear;
}

const std::string key = fmt::format("Texture/{}/{}/{}{}", imageIndex, TextureUsageToString(usage), static_cast<int>(settings.Wrap), static_cast<int>(settings.Filter));
```

The sampler's wrap and filter become the last two digits of the key, so two uses of one image with different samplers make two textures. The code compares the two wrap modes and records a skipped feature when they differ. A material also has one `UV` transform only: it comes from the base color texture, or from the normal texture when there is none, and the rotation of a transform is dropped.

### Meshes: scale, missing data and levels of detail

`ImportMesh` makes one `Mesh` from one glTF mesh. For each primitive it reads positions, then multiplies them by the `Scale` setting.

```cpp src="Strata/src/Strata/Asset/GltfImporter.cpp#L1427-L1433"
// The import scale is part of the mesh, before LODs and bounds are made from it: simplification errors and
// recorded bounds are in the model's final units.
if (m_Settings.Scale != 1.0f)
{
	for (glm::vec3& position : primitivePositions)
		position *= m_Settings.Scale;
}
```

The order matters. The scale is applied before bounds and levels of detail are made, so the error of each level and the recorded bounds are in the model's final units. This is also why the model's root keeps scale 1 (see below): the scale is part of the vertices.

:::example
A file from a program that counts in units of 0.01 m holds a chair 90 units tall. Importing it with `Scale` 0.01 multiplies every position by 0.01, so the chair's top vertex lies at 0.9 m. The :term[root entity]{id=root-entity} stays at scale 1, so a chair you placed and scaled by 2 before keeps its doubled size after you change `Scale`: the setting moves the vertices, not the instance.
:::

#### When the file lacks vertex data

A mesh in a game needs two directions at every vertex: a normal, which is the way the surface faces, and a tangent, which is the way the texture's horizontal axis runs along the surface. Lighting and normal maps use both. Files often lack one or both. The importer makes them in three cases.

**Missing normals** become flat face normals. The importer needs one normal per triangle, so it cannot share vertices between triangles. It copies each triangle's three vertices, so every vertex of a triangle carries that triangle's normal. The mesh looks faceted, and the importer warns when normals exist but cannot be used.

**Missing tangents with texture coordinates** become exact per-corner tangents, using the `MikkTSpace` method that most baking tools use. The method finds a tangent for each corner of each triangle from how the texture coordinates change across it. Where the answer differs between two triangles that share a vertex, the vertex is split: this happens on `UV` seams and on mirror lines, so the vertex count can grow.

**Missing tangents without texture coordinates** need no direction: a normal map cannot be sampled without coordinates, so any tangent perpendicular to the normal is as good as another. Read the code that chooses among the three.

```cpp src="Strata/src/Strata/Asset/GltfImporter.cpp#L1485-L1531"
if (!hasTangents && hasTexCoords)
{
	// Exact per-corner MikkTSpace tangents (also creates the flat normals when needed).
	if (!MeshUtils::GenerateSeamTangents(primitivePositions, primitiveAttributes, primitiveIndices, !hasNormals, binding ? &primitiveSkin : nullptr))
	{
		Warn(fmt::format("Primitive '{}': tangent generation failed", primitiveName));
		continue;
	}
}
else if (!hasTangents)
{
	if (!hasNormals)
	{
		// Flat normals without texture coordinates: unwelded triangles with their face normals.
		std::vector<glm::vec3> flatPositions;
		std::vector<MeshVertexAttributes> flatAttributes;
		std::vector<MeshSkinVertex> flatSkin;
		for (size_t corner = 0; corner < primitiveIndices.size(); corner += 3)
		{
			const glm::vec3& a = primitivePositions[primitiveIndices[corner]];
			const glm::vec3& b = primitivePositions[primitiveIndices[corner + 1]];
			const glm::vec3& c = primitivePositions[primitiveIndices[corner + 2]];
			const glm::vec3 faceNormal = glm::cross(b - a, c - a);
			const float length = glm::length(faceNormal);
			MeshVertexAttributes attribute;
			attribute.Normal = length > 1e-12f ? faceNormal / length : glm::vec3(0.0f, 1.0f, 0.0f);
			for (size_t vertex = 0; vertex < 3; vertex++)
			{
				flatPositions.push_back(primitivePositions[primitiveIndices[corner + vertex]]);
				flatAttributes.push_back(attribute);
				if (binding)
					flatSkin.push_back(primitiveSkin[primitiveIndices[corner + vertex]]);
			}
		}
		primitivePositions = std::move(flatPositions);
		primitiveAttributes = std::move(flatAttributes);
		primitiveSkin = std::move(flatSkin);
		for (size_t corner = 0; corner < primitiveIndices.size(); corner++)
			primitiveIndices[corner] = static_cast<uint32_t>(corner);
	}
	// Without texture coordinates any tangent perpendicular to the normal is as good as another.
	for (MeshVertexAttributes& attribute : primitiveAttributes)
	{
		const glm::vec3 reference = std::abs(attribute.Normal.y) < 0.99f ? glm::vec3(0.0f, 1.0f, 0.0f) : glm::vec3(1.0f, 0.0f, 0.0f);
		attribute.Tangent = glm::vec4(glm::normalize(glm::cross(reference, attribute.Normal)), 1.0f);
	}
}
```

1. **Lines 1485–1488:** with texture coordinates and no tangents, `GenerateSeamTangents` makes the tangents; its last arguments say whether to make normals too, and the skin vertices are split with the rest.
2. **Lines 1494–1497:** with no coordinates, the code checks for missing normals first.
3. **Lines 1499–1523:** the flat-normal branch builds a new vertex list with three vertices per triangle, the triangle's face normal on each, and numbers the indices again from 0.
4. **Line 1510:** a triangle with no area gets the normal +Y, so no vertex has an invalid normal.
5. **Lines 1526–1530:** the tangent is the :term[cross product]{id=cross-product} of a reference axis and the normal; the reference is +Y unless the normal is nearly vertical, when it is +X.

:::example
A triangle with corners (0,0,0), (1,0,0) and (0,1,0) and no normals. The face normal is the cross product of (1,0,0) and (0,1,0), which is (0,0,1). It points at the viewer. Its y component is 0, below 0.99, so the reference axis is +Y and the tangent is the cross product of (0,1,0) and (0,0,1), which is (1,0,0): the tangent runs along the triangle's first edge. The exercises ask you to run this.
:::

The mesh then gets its submesh, its bounds, and optionally its sorted indices. After that come the levels of detail.

#### Levels of detail

A level of detail is a simplified copy of a mesh with fewer triangles, drawn when the mesh covers few pixels; [levels of detail](../draw/lod.md) teaches how the renderer chooses. The importer makes the copies in advance so the renderer never simplifies at run time.

```cpp src="Strata/src/Strata/Asset/GltfImporter.cpp#L1541-L1560"
if (m_Settings.OptimizeMeshes)
	MeshUtils::OptimizeIndices(primitiveIndices, primitiveVertexCount);
std::vector<std::vector<uint32_t>> levels = { primitiveIndices };
std::vector<float> levelErrors = { 0.0f }; // MeshLOD::Error of each level (full detail: none)
// Simplifying a large primitive into its levels of detail takes the longest of a mesh.
if (m_Context.IsCancelled())
	return;
if (m_Settings.GenerateLODs && m_Settings.LODCount > 0)
{
	for (MeshUtils::GeneratedLOD& level : MeshUtils::GenerateLODs(primitivePositions, primitiveAttributes, primitiveIndices, m_Settings.LODCount))
	{
		levelErrors.push_back(level.Error);
		levels.push_back(std::move(level.Indices));
	}
}
for (size_t level = 0; level < levels.size(); level++)
{
	submesh.LODs.push_back(MeshLOD { static_cast<uint32_t>(indices.size()), static_cast<uint32_t>(levels[level].size()), levelErrors[level] });
	indices.insert(indices.end(), levels[level].begin(), levels[level].end());
}
```

1. **Lines 1541–1542:** `OptimizeIndices` sorts the triangles so that the GPU's vertex cache is used well.
2. **Lines 1543–1544:** level 0 is the full mesh and its error is 0, meaning "none".
3. **Lines 1546–1547:** simplifying takes the longest part of a mesh, so the import checks for cancel before it.
4. **Lines 1548–1554:** `GenerateLODs` returns the simplified levels, each with its error.
5. **Lines 1556–1560:** all levels of a submesh share one index array; each `MeshLOD` records where its indices start, how many there are, and its error.

`MeshUtils::GenerateLODs` calls the `meshoptimizer` function `meshopt_simplifyWithAttributes`. The function removes edges, one collapse at a time, while the error stays under `c_MaxLODError`, which is 0.02 of the mesh's extent. It weighs normals and texture coordinates together with positions, so a collapse that would tear a `UV` seam or a normal seam costs more and rarely happens; the seams stay closed. It keeps the open borders of a submesh in place, so two submeshes that meet at an edge do not part.

Each level aims at about half the triangles of the one before, and stops early when it cannot reduce the mesh within the limit. Each level's error is recorded, in the mesh's units, never below the previous level's and never zero, because zero means unknown. The renderer uses these errors to decide when a level looks the same as the full mesh.

:::example
A rock mesh is 2 m wide and has 12,000 triangles. With `LODCount` 3 the importer aims at about 6,000, 3,000 and 1,500 triangles. The limit is 0.02 times the 2 m extent, which is 0.04 m: simplifying stops where a move would exceed it. A level that still keeps more than three quarters of the triangles before it is dropped, and the levels end there. A mesh of fewer than 24 triangles gets no levels at all, so a flat quad keeps only its full mesh.
:::

The vertices, indices and submesh table are then stored in the cooked form of the mesh. It starts with the four letters `STMH`.

```cpp src="Strata/src/Strata/Renderer/Mesh.h#L107-L113"
// level's MeshLOD, its error included), and for skinned meshes (flag bit 0) the skin stream, the skin's joints and their
// inverse bind matrices. Versions 1 (without flags or skins) and 2 (levels without errors: they load with Error 0)
// still load. Serialize only meshes that were not uploaded (importers' and tools' meshes): the upload releases the
// vertex attributes and the skin stream.
static constexpr uint32_t c_CookedVersion = 3;
std::vector<uint8_t> Serialize() const;
static Ref<Mesh> Deserialize(std::span<const uint8_t> data, std::string* outError = nullptr);
```

The version is 3; versions 1 and 2 still load, with errors of 0 for levels that come before errors. The comment ends with a warning: only a mesh that was not uploaded can be saved, because the upload releases the vertex attributes. An importer's mesh has not been uploaded, so it qualifies. On the GPU side, the [geometry pool](../gpu/geometry-pool.md) takes over from there.

### The model

The last step builds the template.

```cpp src="Strata/src/Strata/Asset/GltfImporter.cpp#L1972-L2007"
bool BuildModel(std::string* outError)
{
	Scene scene;
	const std::string modelName = FileSystem::ToUTF8(m_Context.SourcePath.stem());
	// The root keeps scale 1: the import scale is part of the content (vertices, translations, joints, clips), so
	// instances placed before a change of the setting follow it, and their root transforms stay theirs.
	Entity root = scene.CreateEntityWithUUID(DeriveSubAssetHandle(m_Context.Handle, "Node/Root"), modelName);

	// Without a scene every root node is part of the model.
	const std::vector<const cgltf_node*> roots = GetRootNodes();
	if (m_Data->scenes_count > 1)
		m_SkippedFeatures.insert(fmt::format("{} additional scenes", m_Data->scenes_count - 1));

	std::string error;
	if (!AddHierarchy(scene, roots, root, error))
		return Fail(outError, error);
#if ST_WITH_ANIMATION
	if (m_SkeletonHandle.IsValid())
	{
		// The model's animator: its skeleton, playing the first animation (a controller can take over).
		AnimatorComponent& animator = root.AddComponent<AnimatorComponent>();
		animator.Skeleton = m_SkeletonHandle;
		animator.Clip = m_ClipHandles.empty() ? UUID::Null() : m_ClipHandles.front();
	}
#else
	if (m_Data->animations_count > 0)
		m_SkippedFeatures.insert("animations (the engine has no animation module)");
#endif

	Ref<Model> model = Model::CreateFromSnapshot(SceneSerializer::SerializeEntities(scene, { root }));
	if (!model)
		return Fail(outError, "building the model failed");
	const std::string document = JsonUtils::Dump(model->Serialize());
	m_Result.Data.assign(document.begin(), document.end());
	return true;
}
```

1. **Line 1978:** the root entity gets a handle derived from the key `Node/Root`, so it is stable across imports.
2. **Lines 1982–1983:** extra scenes are counted for the warning; only the first one's nodes are used.
3. **Line 1986:** `AddHierarchy` creates one entity per node.
4. **Lines 1989–1994:** when the file has a skeleton, the root gets an animator that plays the first clip; a controller can replace it.
5. **Line 2001:** the entity tree is saved as a snapshot in a `Model`, which becomes the import's main data.

The root keeps scale 1 by design. Before version 8, the import scale was the root's scale, and changing the setting changed every placed instance. Now the scale is part of the content, so instances keep their own transforms. Each mesh sub-asset records its bounds and the materials it uses as references, which [references](references.md) teaches; a mesh's bounds are known before the mesh loads.

Compare the toy with the real code. The toy reads two accessors; the real code also reads strided, :term[normalized]{id=normalization} and compressed ones, checks every range and bounds the total work. The toy keeps the triangles it gets; the real code repairs missing data, :term[optimizes]{id=optimization} the order and makes levels. The toy has no key and no handle; the real code derives both so that assets survive a second import.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Import `FBX` through a vendor library | Many engines | Artists could drop in files from programs that export only `FBX` | An opaque dependency with a closed specification, and a second set of rules to test |
| Import `OBJ` | Many tools and small engines | A simple format that every program writes | No skeleton, animation or PBR materials; the format would need extra files |
| Read `USD` | Film pipelines, some engines | Whole scenes with layers and variants | A very large library and concepts that a game seldom needs |
| Simplify meshes at run time | Engines with virtual geometry | No import work and no stored levels | :term[Frame time]{id=frame-time} spent on simplifying, and no control over seams |
| Store only the original mesh | Small engines | Less code and smaller files | Distant meshes would cost full price to draw |
| Fail on a missing normal or tangent | Strict importers | No guessing | Models from many sources would not import at all |

Sources are listed in Further reading.

## How it is tested

The suite is `Asset.Gltf`, in `StrataTests/src/Asset/GltfImporterTests.cpp` and `GltfSkinImportTests.cpp`. Its test cases build small glTF files in memory and import them. They check these points:

- Meshes, materials, textures and the hierarchy come out.
- `BaseColorFactorsAreSRGB` converts the factors.
- A binary `.glb` imports like a text file, and two imports give the same result.
- Scale, levels of detail, cameras and lights follow the settings.
- Referenced files must lie inside the asset folder.
- Damaged layouts, cycles and oversized hierarchies are rejected.
- Missing normals become flat normals, and tangents follow `UV` seams.
- Only PNG and JPEG images on the first set of coordinates import, and a cancelled import stops at its next check.

Run the suite from the build folder with `StrataTests.exe --test-suite=Asset.Gltf`, or through `ctest`. The tests need no GPU. One case, named "Models imported before their levels of detail kept their errors are imported again", checks that an old cache of a model is replaced. That case is the version rule in action.

## Changing it safely

Three rules protect the importer's users.

1. **Bump the version when the output changes.** Version 11 is the number now. Adding a field to the default settings imports every model once again, because the settings changed; a change to only the memory estimate bumps nothing, since it changes no output.
2. **Derive the handle of every new sub-asset with `DeriveSubAssetHandle(parent, key)`.** A handle chosen any other way changes between imports, and scenes lose their references.
3. **Never change a key.** A key is a promise to every scene that refers to the sub-asset. A new kind of sub-asset gets a new key; an old key keeps its meaning.

Also read files only through `ReadImportSource` and `ReadImportDependency`, check the cancel flag between long steps, and add a test file in `Asset.Gltf` for each new case, including a damaged one. A new feature that skips data records it in the skipped-features set, so the import warns instead of staying silent. The checks to pass are the suite above, the asset suites for packs and references, and the feature test.

## What went wrong before

The history has one entry with a test of its own. Version 9 changed how levels of detail are made: they are simplified with their normals and texture coordinates, and each records its error. Models imported before that kept no errors, so the test `Models imported before their levels of detail kept their errors are imported again` checks that an old cache is replaced by a new import.

## Summary

- A glTF import makes a model and sub-assets with keys such as `Mesh/0`, `Material/0` and `Texture/0/Color/00`; the key gives each one a stable handle.
- Settings choose the scale, the levels of detail and the texture treatment, and inactive settings say why.
- The importer reads ten extensions, fails on a required unknown one, and skips or clamps the rest with a warning.
- Missing normals become flat normals on triangles that share no vertices; missing tangents become `MikkTSpace` tangents with texture coordinates and any perpendicular tangent without.
- A change of output needs a new version; new sub-assets need :term[derived handles]{id=derived-handle}; keys never change.

## Check yourself

1. A model has two meshes, one material and one image used as base color and as metallic-roughness. How many textures does the import make?

   :::answer{tests="import-result"}
   Two. A texture is cooked per image, usage and sampler: `Texture/0/Color/00` and `Texture/0/Data/00`. The two meshes and the material add three more sub-assets, besides the model.
   :::

2. A file made in units of 0.01 m is imported with `Scale` 0.01. Which is true? (a) The root entity gets scale 0.01. (b) Positions are multiplied by 0.01 before bounds and levels of detail. (c) Only the model's root transform changes.

   :::answer{tests="settings"}
   (b). The scale is baked into the content, and the root keeps scale 1. (a) and (c) describe the importer before version 8.
   :::

3. A file requires `KHR_draco_mesh_compression`, and another only uses `EXT_mesh_gpu_instancing`. What happens to each?

   :::answer{tests="support"}
   The first fails the import, because a required extension outside the supported list is refused. The second imports with a warning that GPU instancing was not imported.
   :::

4. A mesh has texture coordinates, normals and no tangents. Which branch makes the tangents, and can the vertex count change?

   :::answer{tests="mesh-repair"}
   `MeshUtils::GenerateSeamTangents` makes exact per-corner tangents. Vertices split along `UV` seams and mirror lines, so the count can grow. Without normals, the same call also makes flat normals.
   :::

5. You change how the importer names a texture. What must you do, and what happens to scenes if you skip it?

   :::answer{tests="change-safely"}
   A key never changes, so give the new texture a new key instead and derive its handle with `DeriveSubAssetHandle`. Bump the version if the output changes. Without these steps, scenes lose their references, or projects keep stale caches that look current.
   :::

## Exercises

1. **Basic.** Import a glTF model with its textures into a project, read its sub-assets and their keys, and place it in the scene.

   :::answer[Worked solution]{tests="import-result,settings"}
   Run `asset.import` with `{"file": "<absolute path of the .gltf>"}`; the command copies the model with the files it reads into a folder. Then run `asset.info` with the model's path: `subAssets` lists each sub-asset with its key, and `importWarnings` lists what was skipped. Place the model with `asset.place` and `{"asset": "<model path>", "point": [0, 0, 0]}`. In the editor, drag the file into the Content Browser and then drag the model into the Scene view.
   :::

2. **Medium.** Write a function that takes three positions and returns the face normal and the fallback tangent of the importer, then print both for a wall triangle and a floor triangle.

   :::answer[Worked solution]{tests="mesh-repair" solution="sketches/assets-models-gltf-flat.cpp"}
   The function takes the cross product of two edges for the normal and a cross product of the normal with a reference axis for the tangent.

   ```cpp sketch="assets-models-gltf-flat.cpp"
   // Flat normal of a triangle and the fallback tangent used when a model has no texture coordinates.
   #include <cmath>
   #include <cstdio>
   #include <glm/glm.hpp>

   struct Frame
   {
   	glm::vec3 Normal;
   	glm::vec3 Tangent;
   };

   static Frame MakeFrame(const glm::vec3& a, const glm::vec3& b, const glm::vec3& c)
   {
   	const glm::vec3 faceNormal = glm::cross(b - a, c - a);
   	const float length = glm::length(faceNormal);
   	Frame frame;
   	frame.Normal = length > 1e-12f ? faceNormal / length : glm::vec3(0.0f, 1.0f, 0.0f);
   	// Any direction that is not nearly parallel to the normal gives a perpendicular tangent through a cross product.
   	const glm::vec3 reference = std::abs(frame.Normal.y) < 0.99f ? glm::vec3(0.0f, 1.0f, 0.0f) : glm::vec3(1.0f, 0.0f, 0.0f);
   	frame.Tangent = glm::normalize(glm::cross(reference, frame.Normal));
   	return frame;
   }

   int main()
   {
   	const Frame wall = MakeFrame({ 0.0f, 0.0f, 0.0f }, { 1.0f, 0.0f, 0.0f }, { 0.0f, 1.0f, 0.0f });
   	std::printf("wall:  normal (%g, %g, %g) tangent (%g, %g, %g)\n", wall.Normal.x, wall.Normal.y, wall.Normal.z, wall.Tangent.x, wall.Tangent.y, wall.Tangent.z);
   	const Frame floor = MakeFrame({ 0.0f, 0.0f, 0.0f }, { 0.0f, 0.0f, 1.0f }, { 1.0f, 0.0f, 0.0f });
   	std::printf("floor: normal (%g, %g, %g) tangent (%g, %g, %g)\n", floor.Normal.x, floor.Normal.y, floor.Normal.z, floor.Tangent.x, floor.Tangent.y, floor.Tangent.z);
   	return 0;
   }
   ```

   ```text output-of="assets-models-gltf-flat.cpp"
   wall:  normal (0, 0, 1) tangent (1, 0, 0)
   floor: normal (0, 1, 0) tangent (0, 0, 1)
   ```

   1. **Line 14:** the cross product of two edges is perpendicular to the triangle; its length is twice the area.
   2. **Line 17:** a triangle without area has no direction, so the normal is +Y.
   3. **Line 19:** the reference axis is +Y unless the normal is nearly vertical.
   4. **Line 20:** crossing the reference with the normal gives a tangent perpendicular to both.

   The wall's normal is (0, 0, 1) and its tangent (1, 0, 0). The floor's normal is +Y, which is nearly vertical, so the reference is +X and the tangent is (0, 0, 1).
   :::

3. **Hard.** Trace it yourself: find where the importer decides how to make tangents for a model without them.

   :::answer[Worked solution]{tests="mesh-repair"}
   Search `GltfImporter.cpp` for `GenerateSeamTangents`; the decision is in `ImportMesh`. Put a breakpoint on the `if (!hasTangents && hasTexCoords)` line. With coordinates, `MeshUtils::GenerateSeamTangents` runs and the vertex count after it can exceed the count before. Without coordinates, the `else if (!hasTangents)` branch runs and the loop writes a perpendicular tangent.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Asset/GltfImporter.h` and `GltfImporter.cpp`: the class, `Run`, `ImportMaterial`, `ImportMesh`, `BuildModel`.
- `Strata/src/Strata/Renderer/Mesh.h` and `Mesh.cpp`: the cooked form and `MeshUtils`.
- `StrataTests/src/Asset/GltfImporterTests.cpp`: the suite `Asset.Gltf`.
- Commands `asset.import`, `asset.info`, `asset.place`; the settings are the asset's import settings.

## Further reading

- The glTF 2.0 specification, Khronos Group: the format's rules; intermediate.
- The meshoptimizer project: the simplifier and decoders the importer uses; intermediate.
- Garland and Heckbert, "Surface Simplification Using Quadric Error Metrics" (1997): the idea behind the error of the simplifier; advanced.
