// A toy catch-up: three instances of one prefab part meet a prefab that changed while their scene was closed.
#include <cstdint>
#include <cstdio>
#include <functional>
#include <map>
#include <set>
#include <string>

using Values = std::map<std::string, int>;

uint64_t HashValues(const Values& values)
{
	uint64_t hash = 1469598103934665603ull;
	for (const auto& [name, value] : values)
	{
		hash = (hash ^ std::hash<std::string>{}(name)) * 1099511628211ull;
		hash = (hash ^ static_cast<uint64_t>(value)) * 1099511628211ull;
	}
	return hash;
}

struct Instance
{
	Values Own;
	std::set<std::string> Overrides; // Names of the values this instance keeps different
	uint64_t PartVersion = 0;        // The version of the prefab's part when the instance last took its values
	uint64_t SyncedHash = 0;         // The hash of the instance's own values at that moment
};

void MarkSynced(Instance& instance, const Values& part)
{
	instance.PartVersion = HashValues(part);
	instance.SyncedHash = HashValues(instance.Own);
}

const char* CatchUp(Instance& instance, const Values& part)
{
	if (instance.PartVersion == HashValues(part))
		return "current";
	if (!instance.Overrides.empty())
	{
		for (const auto& [name, value] : part)
		{
			if (!instance.Overrides.contains(name))
				instance.Own[name] = value;
		}
		MarkSynced(instance, part);
		return "took all but its overrides";
	}
	if (HashValues(instance.Own) == instance.SyncedHash)
	{
		instance.Own = part;
		MarkSynced(instance, part);
		return "took every value";
	}
	return "outdated";
}

int main()
{
	Values part = { { "Intensity", 3 }, { "Range", 6 } };
	Instance plain;
	Instance listed;
	Instance legacy;
	for (Instance* instance : { &plain, &listed, &legacy })
	{
		instance->Own = part;
		MarkSynced(*instance, part);
	}

	listed.Own["Intensity"] = 4;
	listed.Overrides.insert("Intensity");
	legacy.Own["Range"] = 9; // Edited, but no list was kept for it

	part = { { "Intensity", 9 }, { "Range", 8 } }; // Applied from another scene
	const char* names[] = { "plain", "listed", "legacy" };
	Instance* instances[] = { &plain, &listed, &legacy };
	for (int index = 0; index < 3; index++)
	{
		const char* verdict = CatchUp(*instances[index], part);
		std::printf("%-6s intensity %d range %d: %s\n", names[index], instances[index]->Own["Intensity"], instances[index]->Own["Range"], verdict);
	}
	return 0;
}
