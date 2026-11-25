// The finest pyramid level a pixel rectangle reads, for rectangles that start at column 0 of a 9x5 depth buffer.
#include <algorithm>
#include <cstdio>

int main()
{
	const int levelZeroWidth = 5; // 9 halved, rounded up
	const int levelCount = 3;     // 5x3, 2x1, 1x1
	for (int width = 1; width <= 9; width++)
	{
		int highPixel = width - 1;
		int level = 0;
		int high = highPixel >> 1;
		while (level + 1 < levelCount && high > 1)
		{
			level++;
			int last = std::max(levelZeroWidth >> level, 1) - 1;
			high = std::min(highPixel >> (level + 1), last);
		}
		std::printf("width %d: level %d, last texel %d\n", width, level, high);
	}
	return 0;
}
