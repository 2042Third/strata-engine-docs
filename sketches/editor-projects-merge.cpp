#include <cstdio>
#include <map>
#include <string>
#include <vector>

struct SceneLayers
{
	std::string Path;
	std::map<int, std::string> Names;
};

int main()
{
	// The start scene comes first, so that its names win.
	const std::vector<SceneLayers> scenes = {
		{ "Scenes/Main.stscene", { { 1, "Player" }, { 2, "Enemy" } } },
		{ "Scenes/Cave.stscene", { { 2, "Monster" }, { 3, "Enemy" }, { 4, "Pickup" } } } };

	std::map<int, std::string> merged;
	std::vector<std::string> conflicts;
	for (const SceneLayers& scene : scenes)
	{
		for (const auto& [index, name] : scene.Names)
		{
			const auto existing = merged.find(index);
			if (existing != merged.end())
			{
				if (existing->second != name)
					conflicts.push_back(scene.Path + ": layer " + std::to_string(index) + " stays '" + existing->second + "', not '" + name + "'");
				continue;
			}
			bool nameTaken = false;
			for (const auto& [otherIndex, otherName] : merged)
				nameTaken = nameTaken || otherName == name;
			if (nameTaken)
				conflicts.push_back(scene.Path + ": '" + name + "' already names another layer, so layer " + std::to_string(index) + " gets no name");
			else
				merged[index] = name;
		}
	}

	for (const auto& [index, name] : merged)
		std::printf("layer %d: %s\n", index, name.c_str());
	for (const std::string& conflict : conflicts)
		std::printf("conflict: %s\n", conflict.c_str());
}
