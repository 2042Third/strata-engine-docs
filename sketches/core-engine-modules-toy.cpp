// A toy of the engine's module ordering: Kahn's algorithm that always takes the first ready module in listing order.
#include <cstdio>
#include <string>
#include <vector>

struct Module
{
	std::string Name;
	std::vector<std::string> After; // the modules this one starts after
};

static size_t FindModule(const std::vector<Module>& modules, const std::string& name)
{
	for (size_t index = 0; index < modules.size(); index++)
	{
		if (modules[index].Name == name)
			return index;
	}
	return modules.size();
}

// Returns the start order. What waits for a cycle never becomes ready: its indices go into `stuck`.
static std::vector<size_t> Order(const std::vector<Module>& modules, std::vector<size_t>& stuck)
{
	const size_t count = modules.size();
	std::vector<std::vector<size_t>> dependents(count); // who waits for this module
	std::vector<size_t> pending(count, 0);              // how many modules this one still waits for
	for (size_t index = 0; index < count; index++)
	{
		for (const std::string& name : modules[index].After)
		{
			const size_t target = FindModule(modules, name);
			if (target == count)
				continue; // an optional module that the program does not run
			dependents[target].push_back(index);
			pending[index]++;
		}
	}

	std::printf("waiting:");
	for (size_t index = 0; index < count; index++)
		std::printf(" %s=%zu", modules[index].Name.c_str(), pending[index]);
	std::printf("\n");

	std::vector<bool> placed(count, false);
	std::vector<size_t> order;
	while (order.size() < count)
	{
		size_t next = count;
		for (size_t index = 0; index < count && next == count; index++)
		{
			if (!placed[index] && pending[index] == 0)
				next = index;
		}
		if (next == count)
			break; // nothing is ready: the rest waits for a cycle
		placed[next] = true;
		order.push_back(next);
		std::printf("place %s\n", modules[next].Name.c_str());
		for (const size_t dependent : dependents[next])
			pending[dependent]--;
	}

	for (size_t index = 0; index < count; index++)
	{
		if (!placed[index])
			stuck.push_back(index);
	}
	return order;
}

int main()
{
	const std::vector<std::vector<Module>> programs =
	{
		{ { "C", { "A" } }, { "A", {} }, { "B", { "C" } }, { "D", { "Missing" } } },
		{ { "A", { "C" } }, { "B", { "A" } }, { "C", { "B" } }, { "D", { "C" } }, { "E", {} } }
	};
	for (const std::vector<Module>& modules : programs)
	{
		std::vector<size_t> stuck;
		Order(modules, stuck);
		if (!stuck.empty())
		{
			std::printf("stuck:");
			for (const size_t index : stuck)
				std::printf(" %s", modules[index].Name.c_str());
			std::printf("\n");
		}
		std::printf("\n");
	}
	return 0;
}
