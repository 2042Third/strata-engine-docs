// The Hammersley set of 8 points: x counts up, y is the index with its bits reversed.
#include <cstdint>
#include <cstdio>

double Reversed(uint32_t index)
{
	uint32_t bits = 0;
	for (int bit = 0; bit < 32; bit++)
		bits |= ((index >> bit) & 1u) << (31 - bit);
	return bits / 4294967296.0;
}

int main()
{
	for (uint32_t index = 0; index < 8; index++)
		std::printf("index %u: x = %u / 8 = %.3f, y = %.3f\n", index, index, index / 8.0, Reversed(index));
	return 0;
}
