#include <algorithm>
#include <cstdio>
#include <set>
#include <string>
#include <vector>

struct Node
{
	std::string Name;
	int Parent = -1;
};

int main()
{
	// The file's node tree: an armature with three bones, an animated door and a body mesh.
	const std::vector<Node> nodes = {
		{ "Armature", -1 }, { "Shoulder", 0 }, { "Elbow", 1 }, { "Wrist", 2 }, { "Elbow", -1 }, { "Body", -1 }
	};
	const std::vector<int> skinJoints = { 1, 2, 3 };
	const std::vector<int> animatedNodes = { 4 };

	// Step 1: mark the skin's joints and the animated nodes, then every ancestor of a marked node.
	std::vector<bool> inSkeleton(nodes.size(), false);
	for (int index : skinJoints)
		inSkeleton[index] = true;
	for (int index : animatedNodes)
		inSkeleton[index] = true;
	for (size_t index = 0; index < nodes.size(); index++)
	{
		if (!inSkeleton[index])
			continue;
		for (int parent = nodes[index].Parent; parent >= 0 && !inSkeleton[parent]; parent = nodes[parent].Parent)
			inSkeleton[parent] = true;
	}

	// Step 2: walk from the roots with a stack, so a parent always gets its joint index before its children.
	std::vector<int> jointOfNode(nodes.size(), -1);
	std::vector<std::string> jointNames;
	std::set<std::string> usedNames;
	std::vector<int> stack;
	for (int root = static_cast<int>(nodes.size()) - 1; root >= 0; root--)
	{
		if (nodes[root].Parent < 0)
			stack.push_back(root);
	}
	while (!stack.empty())
	{
		const int node = stack.back();
		stack.pop_back();
		if (!inSkeleton[node])
			continue;
		std::string name = nodes[node].Name;
		if (!usedNames.insert(name).second)
		{
			name += "_" + std::to_string(node); // Clips find joints by name, so a name must be unique.
			usedNames.insert(name);
		}
		jointOfNode[node] = static_cast<int>(jointNames.size());
		jointNames.push_back(name);
		for (int child = static_cast<int>(nodes.size()) - 1; child >= 0; child--)
		{
			if (nodes[child].Parent == node)
				stack.push_back(child);
		}
	}

	// Step 3: the root motion joint is the topmost joint of any skin: the smallest joint index.
	int rootMotion = static_cast<int>(jointNames.size());
	for (int index : skinJoints)
		rootMotion = std::min(rootMotion, jointOfNode[index]);

	for (size_t joint = 0; joint < jointNames.size(); joint++)
		std::printf("joint %zu: %s\n", joint, jointNames[joint].c_str());
	std::printf("root motion joint: %d (%s)\n", rootMotion, jointNames[rootMotion].c_str());
	return 0;
}
