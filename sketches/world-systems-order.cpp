// Orders systems by their constraints twice: from the back, as Strata does, and from the front.
#include <cstdio>
#include <functional>
#include <queue>
#include <string>
#include <vector>

namespace
{
	struct System
	{
		std::string Name;
		std::vector<int> After; // indices of the systems that must run before this one
	};

	// Both builds take the ready system that is registered last (from the back) or first (from the front).
	std::vector<int> BuildOrder(const std::vector<System>& systems, bool fromBack)
	{
		const int count = static_cast<int>(systems.size());
		std::vector<std::vector<int>> released(count); // systems that may become ready once this one is placed
		std::vector<int> waiting(count, 0);            // systems each one still waits for
		for (int second = 0; second < count; second++)
		{
			for (int first : systems[second].After)
			{
				// From the back the walk runs against the update order.
				const int from = fromBack ? second : first;
				const int to = fromBack ? first : second;
				released[from].push_back(to);
				waiting[to]++;
			}
		}

		const auto isBelow = [fromBack](int a, int b) { return fromBack ? a < b : a > b; };
		std::priority_queue<int, std::vector<int>, decltype(isBelow)> ready(isBelow);
		for (int index = 0; index < count; index++)
		{
			if (waiting[index] == 0)
				ready.push(index);
		}

		std::vector<int> placed;
		while (!ready.empty())
		{
			const int index = ready.top();
			ready.pop();
			placed.push_back(index);
			for (int next : released[index])
			{
				if (--waiting[next] == 0)
					ready.push(next);
			}
		}
		if (placed.size() != systems.size())
			return {}; // a cycle: Strata refuses the registration
		if (fromBack)
			return std::vector<int>(placed.rbegin(), placed.rend());
		return placed;
	}
}

int main()
{
	// In registration order. Physics runs after Scripting and after Wind; CameraFollow has no constraint.
	const std::vector<System> systems = {
		{ "Scripting", {} },
		{ "Physics", { 0, 3 } },
		{ "CameraFollow", {} },
		{ "Wind", {} },
	};
	for (bool fromBack : { true, false })
	{
		std::printf("%s:", fromBack ? "from the back " : "from the front");
		for (int index : BuildOrder(systems, fromBack))
			std::printf(" %s", systems[index].Name.c_str());
		std::printf("\n");
	}
	return 0;
}
