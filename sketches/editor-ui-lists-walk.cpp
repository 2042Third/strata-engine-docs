// The Hierarchy's walk: depth first along sibling links, into expanded entities only, with a resume stack.
#include <cstdio>
#include <vector>

namespace
{

	constexpr int c_None = -1;

	struct Node
	{
		const char* Name = "";
		int FirstChild = c_None;
		int NextSibling = c_None;
		int Depth = 0;
		bool Expanded = false;
	};

}

int main()
{
	// Root1 > [Lamp, Box > [Bulb]], Root2 > [Crate], Camera. Root2 stays collapsed.
	std::vector<Node> nodes = {
		{ "Root1", 1, 4, 0, true },
		{ "Lamp", c_None, 2, 1, false },
		{ "Box", 3, c_None, 1, true },
		{ "Bulb", c_None, c_None, 2, false },
		{ "Root2", 5, 6, 0, false },
		{ "Crate", c_None, c_None, 1, false },
		{ "Camera", c_None, c_None, 0, false },
	};

	std::vector<int> resume; // The next sibling of each expanded ancestor
	int current = 0;
	int visited = 0;
	while (current != c_None)
	{
		const Node& node = nodes[current];
		std::printf("%*s%s\n", node.Depth * 2, "", node.Name);
		visited++;
		if (node.Expanded && node.FirstChild != c_None)
		{
			resume.push_back(node.NextSibling);
			current = node.FirstChild;
			continue;
		}
		current = node.NextSibling;
		while (current == c_None && !resume.empty())
		{
			current = resume.back();
			resume.pop_back();
		}
	}
	std::printf("visited %d of %zu entities\n", visited, nodes.size());
	return 0;
}
