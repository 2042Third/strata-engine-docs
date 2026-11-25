// Counts the comparisons of a linear search through a list of names.
#include <iostream>
#include <string>
#include <vector>

int main()
{
	const std::vector<std::string> names = { "Ada", "Bo", "Cy", "Di", "Eve", "Fay", "Gus", "Hal" };
	const std::string wanted = "Gus";

	int steps = 0;
	for (size_t index = 0; index < names.size(); index++)
	{
		steps++; // one comparison
		if (names[index] == wanted)
		{
			std::cout << "found at index " << index << " after " << steps << " steps\n";
			return 0;
		}
	}
	std::cout << "not found after " << steps << " steps\n";
	return 0;
}
