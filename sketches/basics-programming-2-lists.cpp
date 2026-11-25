// A std::array of three floats and a std::vector that grows; the vector is summed two ways.
#include <array>
#include <iostream>
#include <vector>

int main()
{
	std::array<float, 3> speeds = { 10.0f, 20.0f, 30.0f }; // indexes 0, 1 and 2
	std::cout << "first " << speeds[0] << ", last " << speeds[2] << '\n';

	std::vector<float> scores; // starts empty
	scores.push_back(5.0f);
	scores.push_back(7.5f);
	scores.push_back(2.0f);
	std::cout << "count " << scores.size() << '\n';

	float total = 0.0f;
	for (float score : scores) // one turn per element
		total = total + score;
	std::cout << "total " << total << '\n';

	for (std::size_t i = 0; i < scores.size(); i++) // the same walk, with an index
		std::cout << i << ": " << scores[i] << '\n';
	return 0;
}
