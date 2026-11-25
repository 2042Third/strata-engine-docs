// Prints the capacity of a std::vector each time it grows during 20 appends.
#include <iostream>
#include <vector>

int main()
{
	std::vector<int> values;
	size_t lastCapacity = values.capacity();
	for (int value = 1; value <= 20; value++)
	{
		values.push_back(value);
		if (values.capacity() != lastCapacity)
		{
			lastCapacity = values.capacity();
			std::cout << "size " << values.size() << ": capacity " << lastCapacity << '\n';
		}
	}
	return 0;
}
