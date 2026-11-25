// A toy prototype copied into a toy scene in slices: capacity is checked first, parents are created before children.
#include <algorithm>
#include <cstdio>
#include <string>
#include <vector>

struct Prototype
{
	std::vector<std::string> Names;
	std::vector<int> Parents; // Index of each entity's parent, -1 for a top-level entity; parents come first
};

struct ToyEntity
{
	std::string Name;
	int Parent;           // Index of the parent in the scene, -1 for none
	size_t TemplateIndex; // The prototype entity this one was made from
};

struct Instantiation
{
	const Prototype* Source = nullptr;
	std::vector<int> Handles; // Per prototype entity: its index in the scene
	size_t Next = 0;
};

struct ToyScene
{
	std::vector<ToyEntity> Entities;
	size_t Capacity = 0;

	bool Begin(const Prototype& prototype, Instantiation& out) const
	{
		if (prototype.Names.size() > Capacity - Entities.size())
			return false; // Nothing is created
		out.Source = &prototype;
		out.Handles.assign(prototype.Names.size(), -1);
		out.Next = 0;
		return true;
	}

	size_t Continue(Instantiation& work, size_t maxEntities)
	{
		const Prototype& prototype = *work.Source;
		const size_t end = std::min(prototype.Names.size(), work.Next + maxEntities);
		for (size_t index = work.Next; index < end; index++)
		{
			const int parent = prototype.Parents[index];
			work.Handles[index] = static_cast<int>(Entities.size());
			const int parentHandle = parent < 0 ? -1 : work.Handles[static_cast<size_t>(parent)];
			Entities.push_back({ prototype.Names[index], parentHandle, index });
		}
		const size_t handled = end - work.Next;
		work.Next = end;
		return handled;
	}
};

int main()
{
	const Prototype lamp { { "Post", "Arm", "Bulb", "Shade", "Cable" }, { -1, 0, 1, 1, 0 } };
	ToyScene scene;
	scene.Capacity = 10;
	scene.Entities.push_back({ "Ground", -1, 0 });
	scene.Entities.push_back({ "Tree", 0, 0 });

	Instantiation work;
	if (scene.Begin(lamp, work))
	{
		for (int frame = 1; work.Next < lamp.Names.size(); frame++)
		{
			const size_t handled = scene.Continue(work, 2);
			std::printf("frame %d: made %zu, the scene holds %zu\n", frame, handled, scene.Entities.size());
		}
	}
	for (const ToyEntity& entity : scene.Entities)
		std::printf("%s under %s\n", entity.Name.c_str(), entity.Parent < 0 ? "nothing" : scene.Entities[static_cast<size_t>(entity.Parent)].Name.c_str());

	scene.Capacity = 8;
	Instantiation second;
	std::printf("a second lamp: %s\n", scene.Begin(lamp, second) ? "begun" : "refused, nothing made");
	return 0;
}
