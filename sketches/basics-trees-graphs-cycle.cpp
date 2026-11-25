// Finding a cycle in a directed graph: a depth-first walk meets a node that is still on its own path.
#include <cstdio>
#include <vector>

// A node's state is 0 (new), 1 (on the current path) or 2 (done).
bool HasCycle(const std::vector<std::vector<int>>& arrows, int node, std::vector<int>& state)
{
	state[node] = 1;
	for (int next : arrows[node])
	{
		if (state[next] == 1)
			return true; // an arrow back to the current path closes a loop
		if (state[next] == 0 && HasCycle(arrows, next, state))
			return true;
	}
	state[node] = 2;
	return false;
}

int main()
{
	std::vector<int> first(4), second(4); // all zero: every node is new
	std::printf("chain: %d\n", HasCycle({ { 1 }, { 2 }, { 3 }, {} }, 0, first));
	std::printf("loop: %d\n", HasCycle({ { 1 }, { 2 }, { 3 }, { 1 } }, 0, second));
}
