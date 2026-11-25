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
