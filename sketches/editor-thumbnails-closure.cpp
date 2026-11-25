#include <cstdint>
#include <cstdio>
#include <map>
#include <string>
#include <vector>

namespace Toy
{

	struct Asset
	{
		uint64_t Stamp = 0;
		std::vector<std::string> DependsOn;
	};

	// The asset and everything it depends on, each name once, in the order the walk meets them.
	void CollectClosure(const std::map<std::string, Asset>& assets, const std::string& name, std::vector<std::string>& closure)
	{
		for (const std::string& seen : closure)
		{
			if (seen == name)
				return;
		}
		closure.push_back(name);
		for (const std::string& source : assets.at(name).DependsOn)
			CollectClosure(assets, source, closure);
	}

	uint64_t ComputeKey(const std::map<std::string, Asset>& assets, const std::string& name)
	{
		std::vector<std::string> closure;
		CollectClosure(assets, name, closure);
		uint64_t key = 14695981039346656037ull;
		for (const std::string& source : closure)
		{
			for (char character : source + ":" + std::to_string(assets.at(source).Stamp) + ";")
			{
				key ^= static_cast<uint8_t>(character);
				key *= 1099511628211ull;
			}
		}
		return key;
	}

}

int main()
{
	std::map<std::string, Toy::Asset> assets;
	assets["Rust.png"] = { 100, {} };
	assets["Rusty.stmat"] = { 200, { "Rust.png" } };
	assets["Barrel.stprefab"] = { 300, { "Rusty.stmat" } };

	const uint64_t before = Toy::ComputeKey(assets, "Barrel.stprefab");
	assets["Rust.png"].Stamp = 101;
	const uint64_t after = Toy::ComputeKey(assets, "Barrel.stprefab");
	std::printf("The prefab's picture is %s\n", before == after ? "kept" : "rendered again");

	std::vector<std::string> closure;
	Toy::CollectClosure(assets, "Barrel.stprefab", closure);
	std::printf("Closure size: %zu\n", closure.size());
	return 0;
}
