// A breadth-first walk of a graph in which two paths lead to Stone: the visited list stops a second visit.
#include <iostream>
#include <string>
#include <vector>

int main()
{
	const std::vector<std::string> names = { "Level", "Wall", "Floor", "Stone", "Image" };
	const std::vector<std::vector<int>> arrows = { { 1, 2 }, { 3 }, { 3 }, { 4 }, {} }; // Level to Wall and Floor, both to Stone, Stone to Image
	std::vector<bool> visited = { true, false, false, false, false }; // the walk starts at Level
	std::vector<int> queue = { 0 };
	for (size_t head = 0; head < queue.size(); head++) // read at the head, add at the end
	{
		const int node = queue[head];
		std::cout << names[node] << ' ';
		for (int next : arrows[node])
		{
			if (visited[next])
				continue; // reached before by another path
			visited[next] = true;
			queue.push_back(next);
		}
	}
	std::cout << '\n';
}
