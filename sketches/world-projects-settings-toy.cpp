// A toy of project settings: sections of whole-number fields with versions, and stored values that are kept as read.
#include <cstdio>
#include <map>
#include <optional>
#include <string>
#include <vector>

using Value = std::map<std::string, int>;

struct Field
{
	std::string Name;
	int Min = 0;
	int Max = 0;
	int Default = 0;
};

struct Section
{
	std::string Id;
	unsigned Version = 1;
	std::vector<Field> Fields;
};

// The single validation: the version first, then each field in order. The first problem is the reason.
std::optional<Value> ValidateValue(const Section& section, const Value& stored, unsigned version, std::string& error)
{
	if (version == 0 || version > section.Version)
	{
		error = "version " + std::to_string(version) + " is newer than this build reads";
		return std::nullopt;
	}
	Value result;
	for (const Field& field : section.Fields)
	{
		const auto found = stored.find(field.Name);
		if (found == stored.end())
		{
			result[field.Name] = field.Default; // A field added since the stored version
			continue;
		}
		if (found->second < field.Min || found->second > field.Max)
		{
			error = field.Name + " must be from " + std::to_string(field.Min) + " to " + std::to_string(field.Max);
			return std::nullopt;
		}
		result[field.Name] = found->second;
	}
	return result;
}

struct Entry
{
	unsigned Version = 1;
	Value Stored;
	bool Valid = false;
};

// What a project keeps: every stored section, valid or not.
struct Values
{
	std::map<std::string, Entry> Entries;
	std::vector<std::string> Validate(const std::vector<Section>& registry)
	{
		std::vector<std::string> problems;
		for (auto& [id, entry] : Entries)
		{
			const Section* section = nullptr;
			for (const Section& candidate : registry)
			{
				if (candidate.Id == id)
					section = &candidate;
			}
			std::string error;
			std::optional<Value> value;
			if (section)
				value = ValidateValue(*section, entry.Stored, entry.Version, error);
			if (!value)
			{
				if (section) // A section nobody claims is kept silently
					problems.push_back(id + ": " + error);
				continue; // Kept as stored: written back unchanged, its default applies
			}
			entry.Stored = *value;
			entry.Version = section->Version;
			entry.Valid = true;
		}
		return problems;
	}
};

int main()
{
	const std::vector<Section> registry = {
		{ "Game.Tuning", 2, { { "MaxEnemies", 1, 50, 10 }, { "SpawnDelay", 0, 10, 2 } } },
		{ "Game.Audio", 1, { { "Volume", 0, 10, 5 } } } };

	Values values;
	values.Entries["Game.Tuning"] = { 1, { { "MaxEnemies", 20 } }, false };
	values.Entries["Game.Audio"] = { 1, { { "Volume", 99 } }, false };
	values.Entries["Fan.Bonus"] = { 1, { { "Level", 3 } }, false };

	for (const std::string& problem : values.Validate(registry))
		std::printf("refused %s\n", problem.c_str());
	for (const auto& [id, entry] : values.Entries)
	{
		std::printf("%s v%u %s:", id.c_str(), entry.Version, entry.Valid ? "provided" : "kept");
		for (const auto& [name, number] : entry.Stored)
			std::printf(" %s=%d", name.c_str(), number);
		std::printf("\n");
	}
	return 0;
}
