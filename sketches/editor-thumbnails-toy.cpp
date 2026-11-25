#include <cstdint>
#include <cstdio>
#include <map>
#include <string>
#include <utility>
#include <vector>

namespace Toy
{

	// The same hash Strata uses for its keys: FNV-1a over the bytes of a text, continued from a seed.
	uint64_t Fnv1a(const std::string& text, uint64_t seed = 14695981039346656037ull)
	{
		uint64_t hash = seed;
		for (char character : text)
		{
			hash ^= static_cast<uint8_t>(character);
			hash *= 1099511628211ull;
		}
		return hash;
	}

	struct Asset
	{
		uint64_t Stamp = 0;                  // Changes when the file or its import settings change
		std::vector<std::string> DependsOn;  // One level of dependencies is enough for the toy
	};

	class ThumbnailCache
	{
	public:
		ThumbnailCache(uint32_t version, std::map<std::string, uint64_t> index)
			: m_Version(version), m_Index(std::move(index)) {}

		void Request(const std::map<std::string, Asset>& assets, const std::string& name)
		{
			const uint64_t key = ComputeKey(assets, name);
			auto found = m_Index.find(name);
			if (found != m_Index.end() && found->second == key)
			{
				std::printf("%s: read from its file\n", name.c_str());
				return;
			}
			std::printf("%s: rendered again\n", name.c_str());
			m_Index[name] = key;
		}

		const std::map<std::string, uint64_t>& GetIndex() const { return m_Index; }

	private:
		uint64_t ComputeKey(const std::map<std::string, Asset>& assets, const std::string& name) const
		{
			uint64_t key = Fnv1a("Thumbnail " + std::to_string(m_Version));
			const Asset& asset = assets.at(name);
			key = Fnv1a(name + ":" + std::to_string(asset.Stamp) + ";", key);
			for (const std::string& source : asset.DependsOn)
				key = Fnv1a(source + ":" + std::to_string(assets.at(source).Stamp) + ";", key);
			return key;
		}

		uint32_t m_Version;
		std::map<std::string, uint64_t> m_Index;
	};

}

int main()
{
	std::map<std::string, Toy::Asset> assets;
	assets["Rust.png"] = { 100, {} };
	assets["Rusty.stmat"] = { 200, { "Rust.png" } };

	Toy::ThumbnailCache first(1, {});
	std::printf("First session\n");
	first.Request(assets, "Rusty.stmat");
	first.Request(assets, "Rusty.stmat");

	std::printf("The texture changes\n");
	assets["Rust.png"].Stamp = 101;
	first.Request(assets, "Rusty.stmat");

	std::printf("Next session, same version\n");
	Toy::ThumbnailCache second(1, first.GetIndex());
	second.Request(assets, "Rusty.stmat");

	std::printf("Next session, version bumped\n");
	Toy::ThumbnailCache third(2, second.GetIndex());
	third.Request(assets, "Rusty.stmat");
	return 0;
}
