// Radix sort of 32-bit keys: four stable passes, one byte of the key each, the lowest byte first.
#include <cstdint>
#include <cstdio>
#include <vector>

void RadixSort(std::vector<uint32_t>& keys)
{
	std::vector<uint32_t> scratch(keys.size());
	for (uint32_t shift = 0; shift < 32; shift += 8)
	{
		uint32_t start[257] = {}; // first the count of each byte value, then where its bucket starts
		for (uint32_t key : keys) start[((key >> shift) & 0xFF) + 1]++;
		for (int bucket = 0; bucket < 256; bucket++) start[bucket + 1] += start[bucket];
		for (uint32_t key : keys) scratch[start[(key >> shift) & 0xFF]++] = key; // in order: equal bytes keep their order
		keys.swap(scratch);
	}
}

int main()
{
	std::vector<uint32_t> keys = { 170, 45, 75, 90, 802, 24, 2, 66, 70000, 300 };
	RadixSort(keys);
	for (uint32_t key : keys) std::printf("%u ", key);
	std::printf("\n");
}
