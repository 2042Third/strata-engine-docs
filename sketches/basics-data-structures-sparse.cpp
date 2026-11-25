// A sparse set: packed holds the members side by side, sparse maps a number to its place in packed.
#include <iostream>
#include <vector>

int main()
{
	std::vector<size_t> packed;
	std::vector<size_t> sparse(16, 0); // the numbers 0 to 15 are possible
	for (size_t id : { 5, 2, 9 })
	{
		sparse[id] = packed.size(); // add: record the place ...
		packed.push_back(id);       // ... and append the member
	}

	const size_t gone = 5;                // remove 5: the last member fills its place
	packed[sparse[gone]] = packed.back();
	sparse[packed.back()] = sparse[gone];
	packed.pop_back();

	for (size_t id : packed)
		std::cout << id << ' ';
	std::cout << "| has 5: " << (sparse[5] < packed.size() && packed[sparse[5]] == 5);
	std::cout << ", has 2: " << (sparse[2] < packed.size() && packed[sparse[2]] == 2) << '\n';
}
