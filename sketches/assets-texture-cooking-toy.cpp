// A toy cook: a box filter builds the mip chain of a gray image, and two size counts are compared for each level.
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <vector>

struct Level
{
	uint32_t Width = 0;
	uint32_t Height = 0;
	std::vector<float> Texels;
};

Level Halve(const Level& source)
{
	Level next;
	next.Width = std::max(1u, source.Width / 2);
	next.Height = std::max(1u, source.Height / 2);
	next.Texels.resize(static_cast<size_t>(next.Width) * next.Height);
	for (uint32_t y = 0; y < next.Height; y++)
	{
		for (uint32_t x = 0; x < next.Width; x++)
		{
			// Each new texel is the mean of the 2x2 texels below it; an odd edge reads its last row or column twice.
			float sum = 0.0f;
			for (uint32_t offset = 0; offset < 4; offset++)
			{
				const uint32_t sourceX = std::min(x * 2 + offset % 2, source.Width - 1);
				const uint32_t sourceY = std::min(y * 2 + offset / 2, source.Height - 1);
				sum += source.Texels[static_cast<size_t>(sourceY) * source.Width + sourceX];
			}
			next.Texels[static_cast<size_t>(y) * next.Width + x] = sum / 4.0f;
		}
	}
	return next;
}

// BC7 stores whole 4x4 blocks of 16 bytes: round the size up to blocks before multiplying.
uint64_t GetBC7Size(uint32_t width, uint32_t height)
{
	const uint64_t blocksX = (width + 3) / 4;
	const uint64_t blocksY = (height + 3) / 4;
	return blocksX * blocksY * 16;
}

int main()
{
	Level level;
	level.Width = 8;
	level.Height = 8;
	for (uint32_t y = 0; y < 8; y++)
	{
		for (uint32_t x = 0; x < 8; x++)
			level.Texels.push_back(static_cast<float>((x + y) * 16));
	}

	for (;;)
	{
		const uint64_t naive = static_cast<uint64_t>(level.Width) * level.Height; // one byte per texel
		std::printf("%ux%u: first texel %.0f, BC7 %llu bytes, one byte per texel %llu\n", level.Width, level.Height, level.Texels[0],
			static_cast<unsigned long long>(GetBC7Size(level.Width, level.Height)), static_cast<unsigned long long>(naive));
		if (level.Width == 1 && level.Height == 1)
			break;
		level = Halve(level);
	}
	return 0;
}
