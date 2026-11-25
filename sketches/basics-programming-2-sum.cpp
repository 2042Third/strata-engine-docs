// Practice 3: the speeds of a std::vector<float> summed in a range-based for.
#include <iostream>
#include <vector>

int main()
{
	std::vector<float> speeds;
	speeds.push_back(12.5f);
	speeds.push_back(30.0f);
	speeds.push_back(7.5f);

	float total = 0.0f;
	for (float speed : speeds)
		total = total + speed;
	std::cout << "total " << total << '\n';
	return 0;
}
