// Coin Run: collected coin names in a vector (linear search, swap-remove) and in a hash set.
#include <iostream>
#include <string>
#include <unordered_set>
#include <vector>

int main()
{
	std::vector<std::string> collected = { "Coin1", "Coin2", "Coin3", "Coin4", "Coin5", "Coin6" };
	std::unordered_set<std::string> collectedSet(collected.begin(), collected.end());

	size_t index = 0;
	while (collected[index] != "Coin3")
		index++; // one comparison per step: index + 1 in all (Coin3 is known to be there)
	collected[index] = collected.back(); // swap-remove: one write
	collected.pop_back();
	const size_t erased = collectedSet.erase("Coin3"); // one hash, one bucket

	std::cout << "vector: " << index + 1 << " comparisons, " << collected.size() << " left\n";
	std::cout << "set: " << erased << " erased, " << collectedSet.size() << " left\n";
	return 0;
}
