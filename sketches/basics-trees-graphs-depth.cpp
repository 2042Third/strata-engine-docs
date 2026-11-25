// A depth-first walk of a tree with a stack: go down one branch to its end, then come back.
#include <iostream>
#include <string>
#include <vector>

struct Node
{
	std::string Name;
	std::vector<int> Children; // positions of the children in the list, in order
};

int main()
{
	const std::vector<Node> tree = { { "Level", { 1, 2, 3 } }, { "Walls", { 4, 5 } }, { "Coins", { 6 } }, { "Player", {} }, { "North", {} }, { "South", {} }, { "Gold", {} } };
	std::vector<int> stack = { 0 }; // the root waits first
	while (!stack.empty())
	{
		const Node& node = tree[stack.back()]; // the node pushed last goes first
		stack.pop_back();
		std::cout << node.Name << ' ';
		for (size_t child = node.Children.size(); child > 0; child--) // backwards, so the first child pops first
			stack.push_back(node.Children[child - 1]);
	}
	std::cout << '\n';
}
