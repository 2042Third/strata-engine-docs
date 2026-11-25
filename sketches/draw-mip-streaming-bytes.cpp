#include <cstdint>
#include <cstdio>

int main()
{
	// One byte per texel. A range read raises a 2048 texture from its tail (level 6) to level 2.
	const uint32_t size = 2048;
	const uint32_t firstLevel = 2;
	const uint32_t tailLevel = 6;
	uint64_t total = 0;
	for (uint32_t level = firstLevel; level < tailLevel; level++)
	{
		const uint64_t side = size >> level;
		std::printf("level %u: %llu bytes\n", level, static_cast<unsigned long long>(side * side));
		total += side * side;
	}
	std::printf("read: %llu bytes\n", static_cast<unsigned long long>(total));
	return 0;
}
