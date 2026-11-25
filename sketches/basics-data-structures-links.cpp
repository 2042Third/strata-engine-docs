// A doubly linked list kept in an array: links are indices, and -1 means "none".
#include <iostream>
#include <vector>

struct Node
{
	int Value = 0;
	int Next = -1;
	int Prev = -1;
};

int main()
{
	std::vector<Node> nodes = { { 10, 1, -1 }, { 20, 2, 0 }, { 30, -1, 1 } }; // 10, 20, 30
	nodes.push_back({ 15, 1, 0 }); // node 3 joins between node 0 and node 1 ...
	nodes[0].Next = 3;             // ... once its two neighbors point at it
	nodes[1].Prev = 3;

	for (int index = 0; index != -1; index = nodes[index].Next)
		std::cout << nodes[index].Value << ' ';
	std::cout << '\n';
	return 0;
}
