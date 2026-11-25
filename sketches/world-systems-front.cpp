// The engine's test case for CameraFollow, Wind and EarlyInput, ordered from the front and from the back.
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

	std::vector<int> BuildOrder(const std::vector<System>& systems, bool fromBack)
	{
		const int count = static_cast<int>(systems.size());
		std::vector<std::vector<int>> released(count);
		std::vector<int> waiting(count, 0);
		for (int second = 0; second < count; second++)
		{
			for (int first : systems[second].After)
			{
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
		if (fromBack)
			return std::vector<int>(placed.rbegin(), placed.rend());
		return placed;
	}

	std::string Join(const std::vector<System>& systems, const std::vector<int>& order)
	{
		std::string text;
		for (int index : order)
			text += (text.empty() ? "" : ", ") + systems[index].Name;
		return text;
	}
}

int main()
{
	// Registration order: the six built-ins, then CameraFollow, Wind (before Physics) and EarlyInput (before Scripting).
	const std::vector<System> systems = {
		{ "UI", {} },
		{ "Scripting", { 0, 8 } },
		{ "Animation", { 1 } },
		{ "World", { 1 } },
		{ "Physics", { 1, 2, 3, 7 } },
		{ "Audio", { 1, 2, 3, 4 } },
		{ "CameraFollow", {} },
		{ "Wind", {} },
		{ "EarlyInput", {} },
	};
	const std::string expected = "UI, EarlyInput, Scripting, Animation, World, Wind, Physics, Audio, CameraFollow";
	const std::string fromBack = Join(systems, BuildOrder(systems, true));
	const std::string fromFront = Join(systems, BuildOrder(systems, false));
	std::printf("from the back : %s\n", fromBack.c_str());
	std::printf("from the front: %s\n", fromFront.c_str());
	std::printf("the test expects the back's order: back %s, front %s\n", fromBack == expected ? "passes" : "fails", fromFront == expected ? "passes" : "fails");
	return 0;
}
