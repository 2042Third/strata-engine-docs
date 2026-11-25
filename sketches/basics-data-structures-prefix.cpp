// Prefix sums: where each group's items start in one shared array.
#include <iostream>
#include <vector>

int main()
{
	const std::vector<int> counts = { 3, 0, 2, 4 }; // items in groups 0, 1, 2 and 3
	std::vector<int> starts(counts.size() + 1, 0);
	for (size_t group = 0; group < counts.size(); group++)
		starts[group + 1] = starts[group] + counts[group];

	for (size_t group = 0; group < counts.size(); group++)
		std::cout << "group " << group << " starts at " << starts[group] << " and has " << counts[group] << '\n';
	std::cout << "total " << starts.back() << '\n';
	return 0;
}
