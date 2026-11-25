// A ring buffer of four numbers: the fifth write overwrites the oldest value.
#include <iostream>
#include <vector>

int main()
{
	std::vector<int> slots(4, 0);
	size_t next = 0;  // where the next value goes
	size_t count = 0; // how many slots hold a value
	for (int value = 1; value <= 6; value++)
	{
		slots[next] = value;
		next = (next + 1) % slots.size(); // after the last slot, return to slot 0
		if (count < slots.size())
			count++;
	}

	// Once the buffer is full, the oldest value sits where the next one would go.
	const size_t oldest = count == slots.size() ? next : 0;
	for (size_t offset = 0; offset < count; offset++)
		std::cout << slots[(oldest + offset) % slots.size()] << ' ';
	std::cout << '\n';
	return 0;
}
