---
id: light/material-data
title: "From a material file to the shader: the material record and its textures"
description: "How Strata turns a material file into a 144-byte record and texture table entries the shaders read, every frame and without waiting for a texture."
kind: internals
size: L
tracks: [E]
needs: [light/materials, gpu/binding, assets/loading]
time: 75
learn:
  - id: follow-material
    text: trace a material from its file through the record to a texture sample in the shader
  - id: record-layout
    text: explain why the material record stays 144 bytes and what a new field must change
  - id: fallbacks
    text: predict which table index a map reads when it is absent and when it is still loading
  - id: flat-normal
    text: compute the tilt that a flat normal stored as 128/255 gives, and why Strata stores it in half floats
  - id: edit-path
    text: trace how a material edit reaches the shader without changing the loaded material
since: 0.3.0
status: final
---

A material file holds a few dozen numbers and up to nine texture names. The :term[shader]{id=shader} that draws a brick wall needs the same information as plain numbers in memory: a color, a roughness, and for each texture a place to read it. This page follows the road from the file to that memory. The code that builds the record does not wait for a texture, does not change a material that is loaded, and does not know what a pixel looks like. It only copies, converts and chooses a fallback, once for every material whose inputs changed.

## The problem and how engines solve it

A scene holds thousands of surfaces, but the :term[graphics processing unit]{id=gpu} (GPU) draws them in a few big batches. A batch cannot stop and bind a new set of resources for each material. [Binding in the GPU](../gpu/binding.md) names the older answer, one :term[descriptor set]{id=descriptor-set} for each material, and the answer Strata took, one buffer of records and one table of textures. The same page shows how a shader reads both.

Three designs meet here, and each has a price. A descriptor set for each material is simple, but every change of material binds a set and ends a batch. Writing each texture's :term[bindless slot]{id=bindless} into the record needs no sets, but a streaming texture moves from slot to slot, and every record that names it must be written again. Strata puts a table index in the record and the slot in the table entry, so a moving texture costs one small write. This page starts after that choice and asks how the record and the table are made, kept right and kept fresh.

## The map

The data flows in one direction, from a document the artist saves to a sample the shader takes. Read the diagram from the left: each box is a form of the same material, and each arrow is code that converts it.

```mermaid caption="A material travels from its saved file to a loaded object, then to a fixed-size record, and the record's texture numbers lead through the texture table to the memory the shader samples." alt="Flow of boxes. The material file leads to the loaded material object, then to the record builder, then to the 144-byte record in the material buffer. The record points to an entry in the texture table. The entry points to a bindless slot. The shader sample function reads the slot and returns a color."
flowchart LR
    F[".stmat JSON"] -->|"Material::FromJson"| P["MaterialProperties"]
    P -->|"MaterialGPU::Build"| D["MaterialData, 144 bytes"]
    D -->|"map index"| E["texture table entry"]
    E -->|"24-bit slot"| S["bindless slot"]
    S -->|"SampleMaterialTexture"| C["color in the shader"]
```

Three owners share the work. The asset system owns the loaded `Material` object and its textures. The :term[renderer's]{id=renderer} scene copy owns the buffer of records and the table of entries, and rebuilds a record when something it depends on changes. The shader owns only the reading: it never changes a record, and it finds no texture except through a table index.

## The contract

Callers of this code may rely on five rules, and must keep them.

- A loaded material never changes. The class offers only read access, and an edit makes a new object that replaces the old one with `ReplaceLoadedAsset`. Renderers keep a material's flags and texture maps from frame to frame, and this replacement is how they learn that those are stale.
- A record is built from a material and nothing else. `MaterialGPU::Build` takes the material and a function that turns a texture handle into a table index; it never loads a texture and never waits.
- A map that is absent or still loading reads a neutral fallback. The surface then looks plain, never broken, and the right texture appears when it arrives.
- The record is 144 :term[bytes]{id=byte}. Every reader sizes it by `sizeof`, and the shader mirrors the layout by hand, so the C++ record, the :term[Slang]{id=slang} record and the number 144 change together or not at all.
- The record holds table indices, never :term[bindless slots]{id=bindless}. A texture keeps its index for its life, even while the slot behind it moves.

:::rule
Every reader of the material record sizes it by `sizeof`, and `MaterialData` stays 144 bytes. A shader cannot check a C++ layout, so the C++ side states the size with `static_assert`, and a field added on one side only shifts every later field on the other. The table of [binding in the GPU](../gpu/binding.md) shows how such buffers are read.
:::

## A toy version

The toy keeps the whole idea in about eighty lines. A properties :term[struct]{id=struct} plays the file's role, with maps named by strings. A data struct plays the GPU record: only numbers, a fixed size, and indices where the properties had names. A table holds one packed entry for each uploaded texture, with a bindless slot in the low 24 bits, a sampler in the next 7 and a gray flag in the top bit.

Watch three things in the output. While the maps are loading, the record holds the fallback indices 2 and 1, for the flat normal and for black. After the upload, the same `Build` call returns the real indices 3 and 4. When the texture moves to another slot, only the table entry changes.

```cpp sketch="light-material-data-toy.cpp"
// A toy material record: a file's properties packed into a fixed-size GPU record and a table of texture entries.
#include <cstdint>
#include <cstdio>
#include <functional>
#include <string>
#include <unordered_map>
#include <vector>

namespace
{

	constexpr uint32_t c_White = 0;
	constexpr uint32_t c_Black = 1;
	constexpr uint32_t c_FlatNormal = 2;
	constexpr uint32_t c_FlagUnlit = 1;
	constexpr uint32_t c_GrayscaleBit = 1u << 31;

	// What the file holds: a map is named by a string, empty for none.
	struct ToyProperties
	{
		float Roughness = 0.5f;
		bool Unlit = false;
		std::string NormalMap;
		std::string EmissiveMap;
	};

	// What the shader reads: plain numbers of a fixed size.
	struct ToyData
	{
		float Roughness;
		uint32_t Flags;
		uint32_t NormalMap;
		uint32_t EmissiveMap;
	};
	static_assert(sizeof(ToyData) == 16);

	using Resolver = std::function<uint32_t(const std::string& map, uint32_t missing, uint32_t loading)>;

	ToyData Build(const ToyProperties& properties, const Resolver& resolve)
	{
		ToyData data = {};
		data.Roughness = properties.Roughness;
		data.Flags = properties.Unlit ? c_FlagUnlit : 0u;
		data.NormalMap = resolve(properties.NormalMap, c_FlatNormal, c_FlatNormal);
		data.EmissiveMap = resolve(properties.EmissiveMap, c_White, c_Black);
		return data;
	}

	uint32_t PackEntry(uint32_t slot, uint32_t sampler, bool grayscale)
	{
		return (slot & 0xFFFFFFu) | ((sampler & 0x7Fu) << 24) | (grayscale ? c_GrayscaleBit : 0u);
	}

}

int main()
{
	// The table: indices 0 to 2 stand for white, black and the flat normal.
	std::vector<uint32_t> table = { PackEntry(0, 0, false), PackEntry(1, 0, false), PackEntry(2, 0, false) };
	std::unordered_map<std::string, uint32_t> uploaded; // Map name to table index, present once the texture is on the GPU

	const Resolver resolve = [&uploaded](const std::string& map, uint32_t missing, uint32_t loading)
	{
		if (map.empty())
			return missing;
		const auto found = uploaded.find(map);
		return found != uploaded.end() ? found->second : loading;
	};

	ToyProperties properties;
	properties.NormalMap = "brick_n";
	properties.EmissiveMap = "brick_e";
	ToyData data = Build(properties, resolve);
	std::printf("loading:  normal %u, emissive %u\n", data.NormalMap, data.EmissiveMap);

	uploaded["brick_n"] = static_cast<uint32_t>(table.size());
	table.push_back(PackEntry(40, 4, false));
	uploaded["brick_e"] = static_cast<uint32_t>(table.size());
	table.push_back(PackEntry(41, 4, true));
	data = Build(properties, resolve);
	std::printf("uploaded: normal %u, emissive %u\n", data.NormalMap, data.EmissiveMap);

	// The texture gains levels and moves to another bindless slot: only its table entry changes, never the record.
	table[data.NormalMap] = PackEntry(57, 4, false);
	const uint32_t entry = table[data.NormalMap];
	std::printf("entry %u: slot %u, sampler %u, grayscale %u\n", data.NormalMap, entry & 0xFFFFFFu, (entry >> 24) & 0x7Fu, entry >> 31);
	std::printf("record %u bytes, normal index still %u\n", static_cast<unsigned>(sizeof(ToyData)), data.NormalMap);
	return 0;
}
```

```text output-of="light-material-data-toy.cpp"
loading:  normal 2, emissive 1
uploaded: normal 3, emissive 4
entry 3: slot 57, sampler 4, grayscale 0
record 16 bytes, normal index still 3
```

1. **Line 35:** The size check states the record's size in the code, so a field added by mistake stops the build.
2. **Lines 44–45:** Each map names two fallbacks, one for "no map" and one for "still loading", and only the glow map separates them.
3. **Line 51:** The entry packs three numbers into one 32-bit value with shifts and masks.
4. **Lines 62–68:** The lookup returns the fallback until the texture has an entry, so a build never waits.
5. **Line 84:** A moving texture changes its table entry, and the record keeps its index.

The toy shows the shape of the design. The record never holds a slot, so a texture can move without a rebuild of every material that names it. The lookup function receives two fallbacks, one for "no map" and one for "not loaded yet", and the glow map uses different ones for the two cases: white when absent, black while loading. The real code keeps all of this and adds the details a game needs.

## The real code, in the order the data flows

### The document

The file is :term[JSON]{id=json}. Its first member names the format, and its second holds each property by the name the reflection list gives it. A short file looks like this.

```json
{
  "Strata": { "Format": "Material", "Version": 1 },
  "Material": { "BaseColor": [0.8, 0.2, 0.2, 1.0], "Roughness": 0.35, "IOR": 1.5 }
}
```

The :term[loader]{id=loader} reads this with `Material::FromJson`. Notice the three refusals at the top, the loop below them, and what the loop does with a name or a value it cannot use.

```cpp src="Strata/src/Strata/Renderer/Material.cpp#L107-L141" symbol="Material::FromJson"
Ref<Material> Material::FromJson(const nlohmann::json& json, std::string* outError, std::vector<std::string>* outWarnings)
{
	auto fail = [outError](const std::string& message) -> Ref<Material>
	{
		if (outError)
			*outError = message;
		return nullptr;
	};

	const nlohmann::json* header = JsonUtils::Find(json, "Strata");
	if (!header || JsonUtils::GetString(*header, "Format") != "Material")
		return fail("Not a Strata material document");
	const uint64_t version = JsonUtils::GetUInt(*header, "Version", 0);
	if (version == 0 || version > c_FormatVersion)
		return fail(fmt::format("Unsupported material version {}", version));

	const nlohmann::json* properties = JsonUtils::Find(json, "Material");
	if (!properties || !properties->is_object())
		return fail("Material document has no 'Material' object");

	Ref<Material> material = Create();
	for (const auto& [key, value] : properties->items())
	{
		const PropertyInfo* property = FindProperty(GetPropertyInfos(), key);
		std::string error;
		if (!property)
			error = fmt::format("Unknown material property '{}'", key);
		else if (std::optional<PropertyValue> parsed = PropertyValueFromJson(*property, value, &error); parsed && property->SetValue(&material->m_Properties, *parsed, &error))
			continue;

		if (outWarnings)
			outWarnings->push_back(error);
	}
	return material;
}
```

1. **Lines 117–121:** A document of another format, or of a version newer than this build knows, is refused with a message.
2. **Lines 123–125:** A document without a `Material` object is refused too, so the loop below can trust its input.
3. **Line 127:** The material starts with every default, so a property the file omits keeps its default.
4. **Lines 132–134:** An unknown name, or a value of the wrong type or range, makes an error text and no change.
5. **Lines 137–138:** The error becomes a warning the caller can show, and the loop continues with the next property.

The same list of reflected properties, `Material::GetPropertyInfos`, drives three other readers. `Serialize` writes the file from it, the commands `material.get` and `material.set` describe and change values through it, and the Inspector draws its fields from it. A property added to the list therefore appears in the file, the commands and the editor at once. A name that is not in the list is only a warning. A bad value keeps its default and the material still loads, so a hand-edited file with one mistake costs one property, not the whole surface.

### The properties

`MaterialProperties` is the whole model in one struct. Its fields are the numbers of the material model, plus handles for nine maps. The maps follow glTF's packing: roughness sits in the green channel and metal in the blue channel of one texture, and occlusion in the red channel of another. The file stores handles, not paths, so renaming a texture file never breaks a material.

The struct also holds the clear coat and glass fields. Those add a second specular layer and a transmission, and they are why the record is 144 bytes long. The next section shows where the space goes.

### The record

The record has the same fields as the properties, converted for the shader. The table lists its layout in rows of 16 bytes, which is the unit the shader's :term[structured buffer]{id=structured-buffer} aligns vectors to.

| Bytes | Fields |
| --- | --- |
| 0 to 31 | `BaseColor`, then `Emissive` (color times intensity, in :term[nits]{id=lux}) |
| 32 to 63 | `Metallic`, `Roughness`, `NormalScale`, `OcclusionStrength`, `AlphaCutoff`, `Flags`, and the table indices of the :term[base color]{id=albedo} and metallic-roughness maps |
| 64 to 79 | `UVTransform`: tiling in x and y, offset in z and w |
| 80 to 111 | the indices of the normal, occlusion, glow and clear coat maps, then `Clearcoat`, `ClearcoatRoughness`, `Transmission` and `IOR` |
| 112 to 127 | `Thickness` and the indices of the coat roughness, coat normal and transmission maps |
| 128 to 143 | `Absorption`: absorbed light per unit in x, y, z, and in w the F0 of a non-metal, the share of light it reflects head-on |

Nine rows of 16 bytes make 144. A vector that sat across a row boundary would break the shader's reading, which is the reason the order of the fields matters and the reason the C++ side ends with `static_assert(sizeof(MaterialData) == 144)`. The `Flags` field holds one bit each for the alpha mask, the alpha blend, `Unlit`, double sided, clear coat and glass. The coat and glass bits are set only for a lit material with a positive strength, so a shader tests a bit and not a float.

### Build and its fallbacks

`MaterialGPU::Build` fills the record. Read how each map goes through the lookup function with two fallbacks, and which fallback each map chooses.

```cpp src="Strata/src/Strata/Renderer/MaterialData.cpp#L61-L95" symbol="MaterialGPU::Build"
RenderData::MaterialData Build(const Material& material, const TextureIndexResolver& textureIndex)
{
	const MaterialProperties& properties = material.GetProperties();
	RenderData::MaterialData data = {};
	data.BaseColor = properties.BaseColor;
	data.Emissive = glm::vec4(properties.EmissiveColor * properties.EmissiveIntensity, 0.0f);
	data.Metallic = properties.Metallic;
	data.Roughness = properties.Roughness;
	data.NormalScale = properties.NormalScale;
	data.OcclusionStrength = properties.OcclusionStrength;
	data.AlphaCutoff = properties.AlphaCutoff;
	data.Flags = (properties.AlphaMode == MaterialAlphaMode::Mask ? RenderData::c_MaterialAlphaMask : 0u)
		| (properties.AlphaMode == MaterialAlphaMode::Blend ? RenderData::c_MaterialAlphaBlend : 0u)
		| (properties.Unlit ? RenderData::c_MaterialUnlit : 0u)
		| (properties.DoubleSided ? RenderData::c_MaterialDoubleSided : 0u)
		| (HasClearcoat(properties) ? RenderData::c_MaterialClearcoat : 0u)
		| (IsTransmissive(properties) ? RenderData::c_MaterialTransmissive : 0u);
	data.UVTransform = glm::vec4(properties.UVTiling, properties.UVOffset);
	data.BaseColorMap = textureIndex(properties.BaseColorMap, TextureTable::c_White, TextureTable::c_White);
	data.MetallicRoughnessMap = textureIndex(properties.MetallicRoughnessMap, TextureTable::c_White, TextureTable::c_White);
	data.NormalMap = textureIndex(properties.NormalMap, TextureTable::c_FlatNormal, TextureTable::c_FlatNormal);
	data.OcclusionMap = textureIndex(properties.OcclusionMap, TextureTable::c_White, TextureTable::c_White);
	data.EmissiveMap = textureIndex(properties.EmissiveMap, TextureTable::c_White, TextureTable::c_Black);
	data.Clearcoat = HasClearcoat(properties) ? std::min(properties.Clearcoat, 1.0f) : 0.0f;
	data.ClearcoatRoughness = std::clamp(properties.ClearcoatRoughness, 0.0f, 1.0f);
	data.Transmission = IsTransmissive(properties) ? std::min(properties.Transmission, 1.0f) : 0.0f;
	data.IOR = std::max(properties.IOR, 1.0f);
	data.Thickness = std::max(properties.Thickness, 0.0f);
	data.ClearcoatMap = textureIndex(properties.ClearcoatMap, TextureTable::c_White, TextureTable::c_White);
	data.ClearcoatRoughnessMap = textureIndex(properties.ClearcoatRoughnessMap, TextureTable::c_White, TextureTable::c_White);
	data.ClearcoatNormalMap = textureIndex(properties.ClearcoatNormalMap, TextureTable::c_FlatNormal, TextureTable::c_FlatNormal);
	data.TransmissionMap = textureIndex(properties.TransmissionMap, TextureTable::c_White, TextureTable::c_White);
	data.Absorption = glm::vec4(GetAbsorption(properties), GetDielectricF0(properties));
	return data;
}
```

1. **Lines 65–71:** Plain numbers are copied; the glow is the color times the intensity, so the record holds nits.
2. **Lines 72–77:** One expression turns the settings into flag bits, and the coat and glass bits use the checks that exclude `Unlit`.
3. **Lines 79–83:** Each map goes through the lookup with its two fallbacks: white, the flat normal, or black for a glow still loading.
4. **Lines 84–88:** The strengths are limited to their ranges here, so the shader may trust them.
5. **Line 93:** Absorption and F0 share one four-number slot, x, y and z for the light the volume absorbs and w for F0.

The fallbacks follow what each map means, not a single rule. A missing base color, metallic-roughness, occlusion or transmission map reads white, the table's index 0, because white leaves a factor unchanged when it multiplies. A missing :term[normal map]{id=normal-map} reads the flat normal, index 2, because "no bump" must decode to the vertex normal. Only the glow map differs: absent it reads white, since the factor alone then sets the glow, but still loading it reads black. A surface whose glow map arrives late would otherwise flash at full strength for a few frames.

The lookup function is written in `RenderSceneGPU::BuildMaterial`. It asks the :term[asset manager]{id=asset-manager} to peek at the loaded texture, which returns the object or null and requests nothing. It returns the texture's table index when the texture has one, and the loading fallback when it does not. When the material itself is not loaded, the scene copy builds the default material instead, so the surface is never absent.

### F0 and absorption

Two results are computed from the properties and not copied. Both live in `Absorption`. The first is F0, the share of light a non-metal reflects head-on, from its `IOR` value $n$, the number that says how strongly the material bends light. The second is how much light the inside of a glass object absorbs for each unit of distance.

For $n = 1.5$ the reflectance is $((1.5 - 1) / (1.5 + 1))^2 = 0.2^2 = 0.04$ by hand, and the shader needs exactly that number. Single-precision floats round the same formula to 0.040000003, which would move the highlight of every default material by a :term[rounding error]{id=rounding-error}. The code therefore writes 0.04 out for $n = 1.5$ and uses the formula elsewhere, with $n$ limited to the range from 1 to 3. Water at 1.33 gives about 0.02, and diamond at 2.42 gives about 0.17.

```cpp src="Strata/src/Strata/Renderer/MaterialData.cpp#L51-L59" symbol="MaterialGPU::GetDielectricF0"
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

Absorption follows Beer's law: the share of light that survives a distance $d$ in a volume is $e^{-a d}$, where $a$ is the absorption per unit. The file does not store $a$. It stores the color white light has after one attenuation distance, which an artist can choose by eye, and the code solves for $a$.

$$a = \frac{-\ln c}{D}$$

In the formula $c$ is the attenuation color, one channel at a time, and $D$ is the attenuation distance in world units. The unit of $a$ is one per world unit. Read $\ln$ as the natural :term[logarithm]{id=logarithm}, the power to which $e$ is raised to give its argument.

```cpp src="Strata/src/Strata/Renderer/MaterialData.cpp#L40-L49" symbol="MaterialGPU::GetAbsorption"
glm::vec3 GetAbsorption(const MaterialProperties& properties)
{
	const float distance = properties.AttenuationDistance;
	if (!(distance > 0.0f) || !std::isfinite(distance))
		return glm::vec3(0.0f);
	// A channel the color removes entirely absorbs as if it kept a ten-thousandth after the distance.
	const glm::vec3 color = glm::clamp(properties.AttenuationColor, glm::vec3(1.0e-4f), glm::vec3(1.0f));
	const glm::vec3 absorption = -glm::log(color) / distance;
	return std::isfinite(absorption.x) && std::isfinite(absorption.y) && std::isfinite(absorption.z) ? absorption : glm::vec3(0.0f);
}
```

1. **Lines 43–44:** A distance of 0, or one that is not a finite number, means no absorption, and the answer is zero.
2. **Line 46:** The color is clamped to the range from 0.0001 to 1, so the logarithm below never meets 0.
3. **Line 47:** The formula of Beer's law, written for all three channels at once.
4. **Line 48:** A last guard, so the record never carries a value that is not a finite number.

Check the limits. A channel of 1 gives $-\ln 1 = 0$, so it absorbs nothing. A channel near 0 would give an infinite value, so the code first clamps each channel to at least 0.0001, and the strongest absorption is then $9.21 / D$. A distance of 0 means no absorption at all, and the code answers with a vector of zeros. Nothing in this function can return a value that is not finite.

### The texture table entry and the sample

A record names a map by a table index. The table, `TextureTable`, holds one packed 32-bit entry and one float for each index. The entry holds the bindless slot in bits 0 to 23, the sampler in bits 24 to 30 and the gray flag in bit 31. The float is a minimum level of detail: a texture that is streaming in finer levels sets it. The new detail then fades in over a quarter of a second, and [mip streaming](../draw/mip-streaming.md) tells that story.

The shader reads the entry first and the texture second, and this extra step lets a texture move without a rebuild of its materials.

```slang src="Strata/shaders/Include/MaterialTextures.slang#L16-L43"
float4 SampleMaterialTexture(uint textureIndex, float2 uv)
{
	uint2 entry = u_TextureTable[textureIndex];
	uint packedSlot = entry.x;
	uint slot = packedSlot & 0xFFFFFFu;
	uint samplerIndex = min((packedSlot >> 24) & 0x7Fu, uint(ST_SAMPLER_COUNT - 1));
	float minLod = asfloat(entry.y);
	// Taken in uniform control flow, for the fade below.
	float2 uvDx = ddx(uv);
	float2 uvDy = ddy(uv);
	float4 value;
	if (minLod > 0.0 && u_Frame.MaterialParams.x != 0.0)
	{
		float2 size = float2(TextureSize(u_Textures[NonUniformResourceIndex(slot)], 0));
		float lengthX = length(uvDx * size);
		float lengthY = length(uvDy * size);
		// The anisotropic level of detail: the shorter axis, unless the longer one exceeds the anisotropy it filters with.
		float footprint = max(min(lengthX, lengthY), max(lengthX, lengthY) / ST_MATERIAL_MAX_ANISOTROPY);
		float lod = log2(max(footprint, 1e-8));
		float scale = exp2(max(minLod - lod, 0.0));
		value = u_Textures[NonUniformResourceIndex(slot)].SampleGrad(u_Samplers[NonUniformResourceIndex(samplerIndex)], uv, uvDx * scale, uvDy * scale);
	}
	else
	{
		value = u_Textures[NonUniformResourceIndex(slot)].Sample(u_Samplers[NonUniformResourceIndex(samplerIndex)], uv);
	}
	return (packedSlot & ST_TEXTURE_SLOT_GRAYSCALE) != 0u ? float4(value.rrr, 1.0) : value;
}
```

1. **Lines 18–21:** One read of the table gives the slot, the sampler and the flags; the sampler index is limited to the samplers that exist.
2. **Lines 27–36:** A texture that is fading in levels is sampled with scaled gradients, so the hardware picks a coarser level until the fade ends.
3. **Line 42:** A gray texture returns its red value three times, with alpha 1.

The gray bit exists for textures of one channel. The sample returns the red value in all three :term[color channels]{id=color-channel} and 1 in alpha, so the code that reads the map need not know the format. A normal map needs more care. Its Z is not stored, because :term[block compression]{id=block-compression-bc1-bc7} 5 (BC5) keeps only two channels, and a map in red, green, blue and alpha at 8 bits each (RGBA8) must shade the same way.

```slang src="Strata/shaders/Include/MaterialTextures.slang#L47-L65"
float3 GetMappedNormal(uint normalMap, float normalScale, float2 uv, float3 vertexNormal, float4 vertexTangent, bool frontFacing)
{
	// Back faces (double-sided materials) use the negated tangent frame: T, B and N all flip (glTF).
	float side = frontFacing ? 1.0 : -1.0;
	float3 normal = normalize(vertexNormal);
	float3 tangent = vertexTangent.xyz - normal * dot(normal, vertexTangent.xyz);
	float tangentLength = length(tangent);
	if (tangentLength < 1e-5)
		return normal * side;

	tangent /= tangentLength;
	float3 bitangent = cross(normal, tangent) * (vertexTangent.w < 0.0 ? -1.0 : 1.0);
	// Normal maps store X and Y (BC5 keeps only those); Z is reconstructed from them, so every format shades alike.
	float2 sampledXY = SampleMaterialTexture(normalMap, uv).xy * 2.0 - 1.0;
	float3 sampled = float3(sampledXY * normalScale, sqrt(clamp(1.0 - dot(sampledXY, sampledXY), 0.0, 1.0)));
	float3 mapped = mul(transpose(float3x3(tangent, bitangent, normal)), sampled);
	float mappedLength = length(mapped);
	return (mappedLength > 1e-5 ? mapped / mappedLength : normal) * side;
}
```

1. **Lines 50–55:** A back face flips the frame, and a tangent of no length falls back to the vertex normal.
2. **Lines 57–58:** The tangent loses its part along the normal and becomes length 1; the :term[cross product]{id=cross-product} gives the :term[bitangent]{id=bitangent}.
3. **Lines 60–61:** The sample gives X and Y only, and Z is rebuilt from them with the square root.
4. **Lines 62–65:** The sampled vector turns into :term[world space]{id=world-space}, then back to length 1, and the side sign is applied last.

### The tangent frame and the flipped back face

The function builds a frame from the vertex normal and tangent: it removes from the tangent any part along the normal, scales it back to length 1, and takes the :term[bitangent]{id=bitangent} as their :term[cross product]{id=cross-product}. A sign that the tangent carries flips the bitangent for mirrored instances, and [mirrors](../draw/mirrors-camera-relative.md) tells why. A back face, seen on a double-sided material, flips the whole result. The surface then shades as the other side of the same wall.

Z comes from the other two. The decoded X and Y are $x$ and $y$, each in the range from $-1$ to $1$, and a unit normal obeys $x^2 + y^2 + z^2 = 1$.

$$z = \sqrt{1 - x^2 - y^2}$$

Here $z$ is the part of the normal that leaves the surface at a right angle. The shader clamps the value under the root to zero, so a texel that is slightly too long, from rounding, gives $z = 0$ and not an error. A short vector makes a large $z$, and a long vector makes a small one, so every format that stores X and Y decodes the same way.

:::example
Follow one number. A brick wall's file says `"Roughness": 0.35` and no normal map. `FromJson` stores 0.35 in the properties.

`Build` copies it to the record's `Roughness`. Because the normal map handle is null, it writes index 2 into `NormalMap`. The shader reads entry 2, a slot of the flat normal texture, and the sample returns $(0.5, 0.5, 1, 1)$. The decode gives $x = 0.5 \cdot 2 - 1 = 0$ and $y = 0$, so $z = \sqrt{1} = 1$, and the mapped normal equals the vertex normal. Later the artist adds a normal map: the new object carries the texture's handle, the record is built again, and `NormalMap` holds the texture's table index, for example 7.
:::

## How an edit reaches the record

A change must reach the GPU without a loaded material changing. When you run `material.set` with `{"Roughness": 0.6}`, the command calls `AssetEdit::SetMaterialProperties`. That function loads the current material, applies the change to its document, and checks the result with the loader, so a bad document changes nothing. It then calls `ApplyDocument`, which saves the file and calls `ReplaceLoadedAsset` with the new object. The asset manager :term[finalizes]{id=finalize} the object, stores it as the loaded version and publishes a content change for the handle.

The renderer's scene copy reads those changes at the start of its update. It finds the material's slot, marks it, and calls `RenderSceneGPU::BuildMaterial`, which calls `Build` again on the new object. The same path runs when a texture arrives or leaves: the scene copy remembers which materials use each texture and marks all of them. With `save` set to false, the command does the same replacement without a file write or an undo step, and a person who drags a slider sees the surface change in the same frame.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| A :term[descriptor set]{id=descriptor-set} for each material | Renderers on older graphics interfaces and many simple ones | Simple to understand; no table to keep | One bind for each change of material, so batches end; sets to create and free |
| Bindless slots written straight into the record | Renderers whose textures never move | One read less in the shader | A new record for every material that names a texture each time it streams to another slot |
| Normal maps that store all three components | Renderers that keep maps in plain 8-bit formats | No square root in the shader | The two-channel BC5 format, so more memory and :term[bandwidth]{id=bandwidth} for every map |

:::why
The record holds table indices because a texture changes more often than a material. A texture streams in finer levels, and each step can move it to another slot. A material changes when a person edits it. Putting the part that moves into the table means the many records stay still and the few entries change.
:::

## How it is tested

The suite `Renderer.Material` in `StrataTests/src/Renderer/MaterialTests.cpp` runs without a GPU. Its cases check that materials round trip through JSON and that documents are validated. A bad property gives a warning and keeps its default, and the GPU data of a coat and of glass holds the values the rules give.

One case checks the rule for the `IOR` value. The value 1.5 gives exactly 0.04 and the value 1 gives 0. The value 5 clamps to 3, and a value that is not a finite number gives 0.04. The same case checks that `Build` writes the result into the `w` part of `Absorption`.

The suite `GPU.SceneRenderer.Materials` needs a GPU and renders real surfaces. Its case "The surface target holds the roughness the forward pass shades" reads the surface target for a plane without a normal map. It compares the stored normal to the geometric one. Run the first suite with `build/windows/bin/Debug/StrataTests.exe --test-suite=Renderer.Material`, and the second with `ctest --preset windows-debug -L gpu`.

## Changing it safely

To add a field, change four things in one commit. Add it to `MaterialProperties` and to the reflected list, so the file, the commands and the Inspector know it. Add it to the C++ `MaterialData` in a place that keeps every 16-byte row whole, and complete it in `Build`. Add it to the Slang `MaterialData` in the same place and order. Change the number in `static_assert(sizeof(MaterialData) == 144)`, and every test that checks the size.

Each rule has a reason. A field that appears in the C++ record only moves every later field in the shader, and every surface turns wrong with no error. A map without a fallback would make a frame wait for a texture to load. An edit that changes the loaded object in place would never reach the renderers that keep flags from frame to frame. Run `Renderer.Material`, the feature test and `GPU.SceneRenderer.Materials` before the commit.

## What went wrong before

Release 0.7.0 stored the flat normal as an 8-bit texture. The value 0.5 does not exist in 8 bits: the nearest is 128/255, which is 0.50196. The decode gives $x = 128/255 \cdot 2 - 1 = 0.00392$, and the same for $y$. The normal then tilts by an angle whose tangent is $\sqrt{2} \cdot 0.00392 = 0.00554$.

The tilt is 0.3 degrees on every surface without a normal map. A mirror doubled the error, and a wall 10 metres away lost the top 8 centimetres of its image in a mirror floor. The fix stores $(0.5, 0.5, 1, 1)$ exactly, in half floats, the 16-bit :term[floating-point numbers]{id=floating-point-number}, where 0.5 is the bit pattern `0x3800` and 1 is `0x3C00`.

The regression test is the case named above. It reads the stored normal of a plane and fails when a coordinate differs from the exact value by more than 0.0005, where the old texture was off by about 0.004. Exercise 3 repeats the arithmetic.

## Summary

- A material travels from its JSON file through `MaterialProperties` and `MaterialGPU::Build` to a 144-byte record, and its map indices lead through the :term[texture table]{id=texture-table-strata} and a bindless slot to `SampleMaterialTexture`.
- The record stays 144 bytes, nine rows of 16 bytes, and a new field changes the C++ struct, the Slang mirror and the size check together.
- A missing map reads white or the flat normal, and a map still loading reads the same fallback, except that a glow map still loading reads black.
- The flat normal is stored as exact half floats, because 128/255 tilts every surface without a normal map by about 0.3 degrees.
- An edit publishes a new material object with `ReplaceLoadedAsset`, and the scene copy marks the material's slot and builds the record again.

## Check yourself

1. A material has a normal map that is still loading and a glow map that is still loading. Which two table indices does `Build` write?

   :::answer{tests="fallbacks"}
   The normal map reads index 2, the flat normal, and the glow map reads index 1, black. A normal map that is absent also gives 2, but a glow map that is absent gives 0, white. Black while loading keeps the surface from flashing at full strength.
   :::

2. Which statement is true? (a) The record holds the bindless slot of each texture. (b) The record holds a table index, and the entry behind it tracks the slot. (c) The shader reads a texture's path from the record.

   :::answer{tests="follow-material"}
   Statement (b) is true. Statement (a) is wrong because a streaming texture moves between slots, and every record would need a rebuild. Statement (c) is wrong because the record holds only numbers, and assets are never named by path at run time.
   :::

3. An attenuation color of $(1, 0.5, 0.25)$ and a distance of 2 give which absorption?

   :::answer{tests="follow-material"}
   Each channel gives $-\ln c / D$. The first is $0$, the second is $0.693 / 2 = 0.347$, and the third is $1.386 / 2 = 0.693$. After 2 units the survivors are 1, 0.5 and 0.25, the colors the file asked for.
   :::

4. You add a field to the C++ record and forget the Slang record. What happens?

   :::answer{tests="record-layout"}
   The C++ side writes more bytes than the shader reads, so the fields after the new one, and every later record, sit at the wrong offsets for the shader. Surfaces show wrong values, and neither side reports an error. The `static_assert` guards only the C++ size.
   :::

5. A material's `Roughness` changes through `material.set`. Which object changes?

   :::answer{tests="edit-path"}
   None. A new `Material` object holds the value, `ReplaceLoadedAsset` publishes it, and the scene copy builds the record again from it. The old object is never modified.
   :::

6. A flat normal texture stores 128/255 in X and Y. About what angle does the shader's normal tilt, and why does the engine store half floats?

   :::answer{tests="flat-normal"}
   The decoded X and Y are each 0.00392, so the tilt has a tangent of $\sqrt{2} \cdot 0.00392 = 0.00554$, which is about 0.3 degrees. Half floats store 0.5 exactly, and the tilt becomes 0.
   :::

## Exercises

1. **Basic.** Pack the entry for bindless slot 300, sampler 4, with the gray flag set. Give the result in :term[hexadecimal]{id=hexadecimal}.

   :::answer[Worked solution]{tests="record-layout"}
   The slot 300 is `0x12C` and stays in bits 0 to 23. The sampler 4 shifted left by 24 bits is `0x04000000`. The gray flag is bit 31, `0x80000000`. The three combine, with a bitwise or, to `0x8400012C`.
   :::

2. **Medium.** Trace it yourself: run `material.set` on a material with `{"Roughness": 0.6}` and follow it with a debugger, or with a search, from the command to the call of `MaterialGPU::Build`. Name each file and function on the way.

   :::answer[Worked solution]{tests="edit-path"}
   The command is registered in `StrataEditor/src/Editor/EditorAssetCommands.cpp` and calls `AssetEdit::SetMaterialProperties` in `StrataEditor/src/Editor/AssetEdit.cpp`. That calls `ApplyDocument`, which saves with `SaveNativeAsset` and calls `ReplaceLoadedAsset` in `Strata/src/Strata/Asset/AssetManager.cpp`, ending with `PublishContentChange`. In `Strata/src/Strata/Renderer/RenderSceneGPU.cpp` the update marks the material's slot from the content changes and calls `BuildMaterial`, which calls `MaterialGPU::Build`.
   :::

3. **Hard.** Compute the tilt of a flat normal stored as 128/255 and of one stored exactly as 0.5, with a program of your own. Then say which check of `GPU.SceneRenderer.Materials` would fail if `Renderer.cpp` stored 128/255 again, and by how much.

   :::answer[Worked solution]{tests="flat-normal" solution="sketches/light-material-data-flat.cpp"}
   The program decodes X and Y as the shader does, rebuilds Z, and measures the angle from straight up.

   ```cpp sketch="light-material-data-flat.cpp"
   // The tilt of a flat normal stored as 8 bits (128/255) against one stored exactly (0.5), as the shader decodes it.
   #include <cmath>
   #include <cstdio>

   namespace
   {

   	// The angle in degrees between the decoded normal and straight up for a texture that stores (texel, texel, 1).
   	double GetTilt(double texel)
   	{
   		const double x = texel * 2.0 - 1.0;
   		const double y = x;
   		const double z = std::sqrt(1.0 - (x * x + y * y)); // Z is rebuilt from X and Y, as the shader does
   		const double sideways = std::sqrt(x * x + y * y);
   		return std::atan2(sideways, z) * 180.0 / 3.14159265358979;
   	}

   }

   int main()
   {
   	std::printf("8 bits, 128/255: x = %.6f, tilt %.4f degrees\n", 128.0 / 255.0 * 2.0 - 1.0, GetTilt(128.0 / 255.0));
   	std::printf("exact 0.5:       x = %.6f, tilt %.4f degrees\n", 0.5 * 2.0 - 1.0, GetTilt(0.5));
   	return 0;
   }
   ```

   ```text output-of="light-material-data-flat.cpp"
   8 bits, 128/255: x = 0.003922, tilt 0.3178 degrees
   exact 0.5:       x = 0.000000, tilt 0.0000 degrees
   ```

   1. **Line 13:** Z is rebuilt from X and Y with the square root, as the shader does.
   2. **Line 15:** The angle from straight up is the arc tangent of the sideways length over Z, turned into degrees.

   The 8-bit texture tilts the normal by about 0.32 degrees and the exact one by 0. The stored normal of a plane without a normal map would differ from the geometric one by about 0.004 in each coordinate. The check allows 0.0005, so both of its comparisons would fail.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Renderer/Material.h` and `Material.cpp`: the properties, the document, the reflected list.
- `Strata/src/Strata/Renderer/MaterialData.cpp`: `Build`, the flags, F0 and absorption.
- `Strata/src/Strata/Renderer/SceneRenderData.h`: the C++ `MaterialData` and its flag constants.
- `Strata/src/Strata/Renderer/RenderSceneGPU.cpp`: `BuildMaterial` and the marking of slots.
- `Strata/src/Strata/Renderer/TextureTable.h`: the table, its reserved indices and the packed entry.
- `Strata/shaders/Include/Scene.slang` and `Strata/shaders/Include/MaterialTextures.slang`: the shader's record and the sample functions.
- `StrataTests/src/Renderer/MaterialTests.cpp`, suite `Renderer.Material`; the suite `GPU.SceneRenderer.Materials`.
- Commands: `material.create`, `material.get`, `material.set`.

## Further reading

- The glTF 2.0 specification, material section (beginner to intermediate): the metallic-roughness model and the channel packing the properties use.
- Physically Based Rendering, the book by Pharr, Jakob and Humphreys (advanced): the Fresnel term and Beer's law.
