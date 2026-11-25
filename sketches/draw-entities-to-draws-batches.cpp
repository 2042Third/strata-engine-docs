// Counts the draw calls of a visible set drawn one by one and drawn as instanced batches.
// A batch is every drawable that shares a mesh, a submesh and a level of detail: the material is not in the key.
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
		{ 1, 1, 0, 3 }, { 1, 0, 0, 3 }, { 1, 1, 0, 4 }, { 2, 0, 0, 1 }, { 2, 0, 0, 1 }
	};

	std::map<std::tuple<int, int, int>, int> batches;
	for (const Drawable& drawable : visible)
		batches[{ drawable.Mesh, drawable.Submesh, drawable.Lod }]++;

	std::printf("one draw per drawable: %zu draw calls\n", visible.size());
	std::printf("instanced batches: %zu draw calls\n", batches.size());
	for (const auto& [key, count] : batches)
		std::printf("  mesh %d submesh %d level %d: %d instances\n", std::get<0>(key), std::get<1>(key), std::get<2>(key), count);
	return 0;
}
