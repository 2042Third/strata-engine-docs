// The batching sketch with a second level of detail for mesh 2, and the total of the instances.
#include <cstdio>
#include <map>
#include <tuple>
#include <vector>

namespace
{
	struct Drawable
	{
		int Mesh;
		int Submesh;
		int Lod;
		int Material;
	};
}

int main()
{
	const std::vector<Drawable> visible = {
		{ 0, 0, 0, 1 }, { 0, 0, 0, 2 }, { 0, 0, 0, 1 }, { 0, 0, 1, 1 }, { 1, 0, 0, 3 },
		{ 1, 1, 0, 3 }, { 1, 0, 0, 3 }, { 1, 1, 0, 4 }, { 2, 0, 0, 1 }, { 2, 0, 0, 1 },
		{ 2, 0, 1, 1 }, { 2, 0, 1, 1 }
	};

	std::map<std::tuple<int, int, int>, int> batches;
	for (const Drawable& drawable : visible)
		batches[{ drawable.Mesh, drawable.Submesh, drawable.Lod }]++;

	int instances = 0;
	for (const auto& [key, count] : batches)
		instances += count;

	std::printf("instanced batches: %zu draw calls\n", batches.size());
	std::printf("instances: %d\n", instances);
	return 0;
}
