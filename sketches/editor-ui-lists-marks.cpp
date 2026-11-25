// Marking the ancestors of matches: walking to the root for every match, and stopping at a marked ancestor.
#include <cstdio>
#include <vector>

namespace
{

	constexpr int c_ChainLength = 1000;

}

int main()
{
	// A chain: entity 0 is the root and entity i is the child of entity i - 1. Every entity matches.
	std::vector<int> parents(c_ChainLength);
	for (int entity = 0; entity < c_ChainLength; entity++)
		parents[entity] = entity - 1;

	long everyStep = 0;
	for (int match = 0; match < c_ChainLength; match++)
	{
		for (int parent = parents[match]; parent >= 0; parent = parents[parent])
			everyStep++;
	}

	long onceStep = 0;
	std::vector<bool> marked(c_ChainLength, false);
	for (int match = 0; match < c_ChainLength; match++)
	{
		for (int parent = parents[match]; parent >= 0; parent = parents[parent])
		{
			onceStep++;
			if (marked[parent])
				break;
			marked[parent] = true;
		}
	}

	std::printf("steps without the stop: %ld\n", everyStep);
	std::printf("steps with the stop: %ld\n", onceStep);
	return 0;
}
