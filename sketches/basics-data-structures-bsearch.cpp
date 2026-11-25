// Binary search in a sorted array, printing each probe.
#include <iostream>
#include <vector>

int main()
{
	const std::vector<int> sorted = { 3, 8, 15, 21, 34, 42, 57, 63, 79 };
	const int wanted = 63;
	int low = 0;
	int high = static_cast<int>(sorted.size()) - 1;
	while (low <= high)
	{
		const int middle = (low + high) / 2;
		std::cout << "probe index " << middle << ": " << sorted[middle] << '\n';
		if (sorted[middle] == wanted)
			return 0;
		if (sorted[middle] < wanted)
			low = middle + 1;
		else
			high = middle - 1;
	}
	std::cout << "not found\n";
	return 0;
}
