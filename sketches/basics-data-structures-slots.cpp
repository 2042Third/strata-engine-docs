// A free list reuses slot 2; a version number catches a handle to the destroyed slot.
#include <cstdint>
#include <iostream>
#include <vector>

struct Handle { uint32_t Index; uint32_t Version; };

int main()
{
	std::vector<uint32_t> versions = { 0, 0, 0 }; // three slots, all at version 0
	std::vector<uint32_t> freeSlots;              // unused slot indices, used as a stack
	const Handle first = { 2, versions[2] };

	versions[2]++;          // destroy slot 2: its version changes ...
	freeSlots.push_back(2); // ... and its index joins the free list

	const uint32_t reused = freeSlots.back(); // create: take an index from the free list
	freeSlots.pop_back();
	const Handle second = { reused, versions[reused] };
	std::cout << "same slot: " << (first.Index == second.Index) << '\n';
	std::cout << "first valid: " << (versions[first.Index] == first.Version) << '\n';
	std::cout << "second valid: " << (versions[second.Index] == second.Version) << '\n';
	return 0;
}
