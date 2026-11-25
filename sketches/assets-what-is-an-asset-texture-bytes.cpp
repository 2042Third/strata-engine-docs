#include <cstdint>
#include <cstdio>

namespace
{

	// Bytes of one mip level: RGBA8 stores 4 bytes a pixel, BC7 stores each 4 by 4 block of pixels in 16 bytes.
	uint64_t LevelBytes(uint32_t size, bool blockCompressed)
	{
		if (!blockCompressed)
			return uint64_t(size) * size * 4;
		const uint64_t blocks = (size + 3) / 4;
		return blocks * blocks * 16;
	}

	// Every level from the full size down to one pixel, each half the size of the one before.
	uint64_t ChainBytes(uint32_t size, bool blockCompressed)
	{
		uint64_t total = 0;
		for (;; size /= 2)
		{
			total += LevelBytes(size, blockCompressed);
			if (size == 1)
				return total;
		}
	}

}

int main()
{
	const uint32_t size = 1024;
	std::printf("RGBA8, one level:   %llu bytes\n", (unsigned long long)LevelBytes(size, false));
	std::printf("RGBA8, mip chain:   %llu bytes\n", (unsigned long long)ChainBytes(size, false));
	std::printf("BC7, one level:     %llu bytes\n", (unsigned long long)LevelBytes(size, true));
	std::printf("BC7, mip chain:     %llu bytes\n", (unsigned long long)ChainBytes(size, true));
	return 0;
}
