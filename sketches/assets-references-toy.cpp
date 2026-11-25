// A toy dependency graph: a breadth-first closure in two scopes, and a group's progress by count and by bytes.
#include <cstdint>
#include <iostream>
#include <string>
#include <vector>

struct Asset
{
	std::string Name;
	bool IsScene = false;
	uint64_t Kilobytes = 0;
	std::vector<size_t> Dependencies;
};

// The list itself is the queue: the loop reads at the head while the end grows.
std::vector<size_t> GetClosure(const std::vector<Asset>& assets, size_t root, bool loadScope)
{
	std::vector<size_t> closure = { root };
	std::vector<bool> visited(assets.size(), false);
	visited[root] = true;
	for (size_t head = 0; head < closure.size(); head++)
	{
		for (size_t dependency : assets[closure[head]].Dependencies)
		{
			if (visited[dependency] || (loadScope && assets[dependency].IsScene))
				continue;
			visited[dependency] = true;
			closure.push_back(dependency);
		}
	}
	return closure;
}

int main()
{
	const std::vector<Asset> assets = {
		{ "Outpost", true, 40, { 1, 5, 6 } },
		{ "Tower", false, 8, { 2, 3 } },
		{ "TowerMesh", false, 600, { 3 } },
		{ "Stone", false, 2, { 4 } },
		{ "StoneTexture", false, 4000, {} },
		{ "MossTexture", false, 2000, {} },
		{ "Intro", true, 30, { 7 } },
		{ "IntroMesh", false, 1000, {} },
	};

	for (bool loadScope : { false, true })
	{
		std::cout << (loadScope ? "Load:" : "All: ");
		for (size_t index : GetClosure(assets, 0, loadScope))
			std::cout << ' ' << assets[index].Name;
		std::cout << '\n';
	}

	const std::vector<size_t> group = GetClosure(assets, 0, true);
	uint64_t totalKilobytes = 0;
	for (size_t index : group)
		totalKilobytes += assets[index].Kilobytes;

	uint64_t doneKilobytes = 0;
	for (size_t finished = 0; finished < group.size(); finished++)
	{
		doneKilobytes += assets[group[finished]].Kilobytes;
		std::cout << assets[group[finished]].Name << ": " << (finished + 1) * 100 / group.size() << "% by count, "
			<< doneKilobytes * 100 / totalKilobytes << "% by bytes\n";
	}
}
