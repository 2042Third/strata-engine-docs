#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <unordered_set>
#include <utility>
#include <vector>

// A body key holds the body's generation in its high half and its index in its low half.
static uint64_t MakeKey(uint32_t generation, uint32_t index)
{
	return (static_cast<uint64_t>(generation) << 32) | index;
}

// What the engine does with the shapes a tree reports: order by body index, drop repeats, one entry per entity.
static std::vector<int> Order(std::vector<std::pair<uint64_t, int>> found)
{
	std::sort(found.begin(), found.end(), [](const auto& a, const auto& b)
	{
		const uint32_t indexA = static_cast<uint32_t>(a.first);
		const uint32_t indexB = static_cast<uint32_t>(b.first);
		return indexA != indexB ? indexA < indexB : a.first < b.first;
	});
	found.erase(std::unique(found.begin(), found.end()), found.end());

	std::vector<int> entities;
	std::unordered_set<int> seen;
	for (const auto& [key, entity] : found)
	{
		if (seen.insert(entity).second)
			entities.push_back(entity);
	}
	return entities;
}

int main()
{
	// Bodies 7, 3, 9, 5 and 7 again (a second shape of the same body), in the order a tree might report them.
	// Body 9 belongs to entity 50 too, as a character's presence body would.
	const std::vector<std::pair<uint64_t, int>> found = {
		{ MakeKey(1, 7), 70 }, { MakeKey(2, 3), 30 }, { MakeKey(1, 9), 50 }, { MakeKey(1, 5), 50 }, { MakeKey(1, 7), 70 }
	};
	for (int entity : Order(found))
		std::printf("entity %d\n", entity);
	return 0;
}
