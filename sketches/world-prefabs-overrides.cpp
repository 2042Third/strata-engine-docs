// A toy override list: the components of one entity in a prefab and in an instance, compared as values.
#include <cstdio>
#include <map>
#include <string>
#include <vector>

using Properties = std::map<std::string, std::string>;
using Components = std::map<std::string, Properties>;

struct Override
{
	std::string Component;
	std::string Property;
	std::string Kind;
};

std::vector<Override> Compare(const Components& prefab, const Components& instance)
{
	std::vector<Override> result;
	for (const auto& [name, properties] : prefab)
	{
		const auto found = instance.find(name);
		if (found == instance.end())
		{
			result.push_back({ name, "", "RemovedComponent" });
			continue;
		}
		for (const auto& [property, value] : properties)
		{
			const auto other = found->second.find(property);
			if (other == found->second.end() || other->second != value)
				result.push_back({ name, property, "Property" });
		}
		for (const auto& [property, value] : found->second)
		{
			if (!properties.contains(property))
				result.push_back({ name, property, "Property" });
		}
	}
	for (const auto& [name, properties] : instance)
	{
		if (!prefab.contains(name))
			result.push_back({ name, "", "AddedComponent" });
	}
	return result;
}

void Print(const char* title, const std::vector<Override>& overrides)
{
	std::printf("%s: %zu override(s)\n", title, overrides.size());
	for (const Override& entry : overrides)
		std::printf("  %s %s.%s\n", entry.Kind.c_str(), entry.Component.c_str(), entry.Property.c_str());
}

int main()
{
	const Components bulb { { "PointLight", { { "Intensity", "5" }, { "Range", "10" } } }, { "AudioSource", { { "Volume", "1" } } } };

	Components brighter = bulb;
	brighter["PointLight"]["Intensity"] = "8";
	Components silent = bulb;
	silent.erase("AudioSource");
	Components flickering = bulb;
	flickering["Flicker"] = { { "Rate", "3" } };

	Print("untouched", Compare(bulb, bulb));
	Print("brighter", Compare(bulb, brighter));
	Print("silent", Compare(bulb, silent));
	Print("flickering", Compare(bulb, flickering));
	return 0;
}
