// A toy scene reader: one entity per line, parents linked once every entity is read, cycles refused with a union-find.
#include <cstdio>
#include <map>
#include <numeric>
#include <sstream>
#include <string>
#include <vector>

namespace
{
	constexpr size_t c_NoParent = static_cast<size_t>(-1);

	struct Entity
	{
		std::string Id;
		std::string Parent; // "-": top level
	};

	size_t FindRoot(std::vector<size_t>& connected, size_t index)
	{
		size_t root = index;
		while (connected[root] != root)
			root = connected[root];
		while (connected[index] != root) // Path compression: later searches start closer to the root
		{
			const size_t next = connected[index];
			connected[index] = root;
			index = next;
		}
		return root;
	}

	// The index of each entity's parent. A missing parent or one that would close a cycle leaves the entity at the top level.
	std::vector<size_t> LinkParents(const std::vector<Entity>& entities)
	{
		std::map<std::string, size_t> indexOf;
		for (size_t index = 0; index < entities.size(); index++)
			indexOf[entities[index].Id] = index;

		std::vector<size_t> connected(entities.size());
		std::iota(connected.begin(), connected.end(), size_t(0));
		std::vector<size_t> linked(entities.size(), c_NoParent);
		for (size_t index = 0; index < entities.size(); index++)
		{
			const Entity& entity = entities[index];
			if (entity.Parent == "-")
				continue;
			const auto parent = indexOf.find(entity.Parent);
			if (parent == indexOf.end())
			{
				std::printf("warning: %s: parent %s not found\n", entity.Id.c_str(), entity.Parent.c_str());
				continue;
			}
			const size_t childRoot = FindRoot(connected, index);
			const size_t parentRoot = FindRoot(connected, parent->second);
			if (childRoot == parentRoot) // Both ends already connected: this link would close a loop
			{
				std::printf("warning: %s: parent %s would create a cycle\n", entity.Id.c_str(), entity.Parent.c_str());
				continue;
			}
			connected[childRoot] = parentRoot;
			linked[index] = parent->second;
		}
		return linked;
	}
}

int main()
{
	const std::string document = "Root -\nArm Root\nHand Arm\nLamp Ghost\nPing Pong\nPong Ping\n";
	std::vector<Entity> entities;
	std::istringstream lines(document);
	for (Entity entity; lines >> entity.Id >> entity.Parent;)
		entities.push_back(entity);

	const std::vector<size_t> linked = LinkParents(entities);
	for (size_t index = 0; index < entities.size(); index++)
	{
		if (linked[index] == c_NoParent)
			std::printf("%s: top level\n", entities[index].Id.c_str());
		else
			std::printf("%s: child of %s\n", entities[index].Id.c_str(), entities[linked[index]].Id.c_str());
	}
	return 0;
}
