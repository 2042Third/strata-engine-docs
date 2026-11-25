#include <cstdint>
#include <cstdio>

namespace
{

	// BC7 bytes of one level: 16 bytes for each 4 by 4 block, partial blocks rounded up.
	uint64_t LevelBytes(uint32_t width, uint32_t height)
	{
		return uint64_t((width + 3) / 4) * ((height + 3) / 4) * 16;
	}

	// A level halves each side but never goes below one pixel; the chain ends at 1 by 1.
	uint64_t ChainBytes(uint32_t width, uint32_t height)
	{
		uint64_t total = 0;
		for (;;)
		{
			total += LevelBytes(width, height);
			if (width == 1 && height == 1)
				return total;
			width = width > 1 ? width / 2 : 1;
			height = height > 1 ? height / 2 : 1;
		}
	}

}

int main()
{
	std::printf("2048 x 1024: %llu bytes\n", (unsigned long long)ChainBytes(2048, 1024));
	std::printf("4096 x 4096: %llu bytes\n", (unsigned long long)ChainBytes(4096, 4096));
	return 0;
}
