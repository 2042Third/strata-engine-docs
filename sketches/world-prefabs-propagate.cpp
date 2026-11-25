// A toy Propagate for one entity: a prefab's change reaches an instance except where the instance overrides it.
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
	}
	for (const auto& [name, properties] : instance)
	{
		if (!prefab.contains(name))
			result.push_back({ name, "", "AddedComponent" });
	}
	return result;
}

// An empty property asks about the whole component: any override of it counts.
bool IsOverridden(const std::vector<Override>& overrides, const std::string& component, const std::string& property)
{
	for (const Override& entry : overrides)
	{
		if (entry.Component != component)
			continue;
		if (entry.Kind != "Property" || property.empty() || entry.Property == property)
			return true;
	}
	return false;
}

void Propagate(const Components& previous, const Components& next, Components& instance)
{
	const std::vector<Override> overrides = Compare(previous, instance);
	for (const auto& [name, values] : next)
	{
		const auto before = previous.find(name);
		if (before == previous.end() && !instance.contains(name))
		{
			instance[name] = values; // The prefab added it
			continue;
		}
		if (!instance.contains(name))
			continue; // The instance removed it
		for (const auto& [property, value] : values)
		{
			const bool known = before != previous.end() && before->second.contains(property);
			const bool changed = !known || before->second.at(property) != value;
			if (changed && !IsOverridden(overrides, name, property))
				instance[name][property] = value;
		}
	}
	for (const auto& [name, values] : previous)
	{
		if (!next.contains(name) && !IsOverridden(overrides, name, ""))
			instance.erase(name); // The prefab removed it
	}
}

void Print(const char* title, const Components& components)
{
	std::printf("%s:", title);
	for (const auto& [name, properties] : components)
	{
		for (const auto& [property, value] : properties)
			std::printf(" %s.%s=%s", name.c_str(), property.c_str(), value.c_str());
	}
	std::printf("\n");
}

int main()
{
	const Components before { { "PointLight", { { "Intensity", "5" }, { "Range", "10" } } }, { "AudioSource", { { "Volume", "1" } } } };
	const Components after { { "PointLight", { { "Intensity", "6" }, { "Range", "15" } } }, { "AudioSource", { { "Volume", "0.5" } } } };

	Components untouched = before;
	Components brighter = before;
	brighter["PointLight"]["Intensity"] = "8";
	Components silent = before;
	silent.erase("AudioSource");

	Propagate(before, after, untouched);
	Propagate(before, after, brighter);
	Propagate(before, after, silent);
	Print("untouched", untouched);
	Print("brighter ", brighter);
	Print("silent   ", silent);
	return 0;
}
