#include <cstdio>
#include <string>
#include <vector>

enum class Kind { Edit, Query, Session };

struct Entry
{
	int Id = 0;
	std::string Command;
	Kind CommandKind = Kind::Edit;
	std::string Target;   // The ID the command's parameters name, or empty
	std::string Argument; // Another parameter, or empty
	std::string Produced; // The ID its result holds, or empty
};

static int FindProducer(const std::vector<Entry>& entries, const std::vector<bool>& producing, size_t before, const std::string& id)
{
	for (size_t i = 0; i < before; i++)
	{
		if (producing[i] && entries[i].Produced == id)
			return static_cast<int>(i);
	}
	return -1;
}

static void PrintReplay(const std::vector<Entry>& entries)
{
	const size_t count = entries.size();
	std::vector<bool> producing(count, false);
	std::vector<bool> needed(count, false);
	std::vector<bool> bound(count, false);
	std::vector<int> producer(count, -1);

	// Forward: which entry gave each ID first, and which entries are edits.
	for (size_t i = 0; i < count; i++)
	{
		const Entry& entry = entries[i];
		if (!entry.Target.empty())
			producer[i] = FindProducer(entries, producing, i, entry.Target);
		needed[i] = entry.CommandKind == Kind::Edit;
		producing[i] = entry.CommandKind != Kind::Session && !entry.Produced.empty();
	}

	// Backward: an edit pulls in the entry that gave it an ID.
	for (size_t i = count; i-- > 0;)
	{
		if (!needed[i] || producer[i] < 0)
			continue;
		needed[producer[i]] = true;
		bound[producer[i]] = true;
	}

	for (size_t i = 0; i < count; i++)
	{
		if (!needed[i])
			continue;
		std::printf("%s", entries[i].Command.c_str());
		if (!entries[i].Target.empty() && producer[i] >= 0)
			std::printf(" target=$ref(e%d)", entries[producer[i]].Id);
		else if (!entries[i].Target.empty())
			std::printf(" target=%s", entries[i].Target.c_str());
		if (!entries[i].Argument.empty())
			std::printf(" name=%s", entries[i].Argument.c_str());
		if (bound[i])
			std::printf(" bind=e%d", entries[i].Id);
		std::printf("\n");
	}
}

int main()
{
	const std::vector<Entry> session = {
		{ 1, "entity.create", Kind::Edit, "", "", "A7" },
		{ 2, "selection.get", Kind::Session, "", "", "A7" },
		{ 3, "entity.find", Kind::Query, "", "Sun", "B1" },
		{ 4, "entity.rename", Kind::Edit, "A7", "Box", "" },
		{ 5, "entity.rename", Kind::Edit, "B1", "Lamp", "" },
		{ 6, "entity.find", Kind::Query, "", "Crate", "C2" },
		{ 7, "entity.rename", Kind::Edit, "Z9", "Old", "" } };
	PrintReplay(session);
	return 0;
}
