// The stored size of a 4096 by 4096 texture with its whole mip chain, in four formats.
#include <cstdint>
#include <cstdio>

struct Format
{
	const char* Name;
	uint32_t BlockSide;     // Texels along one side of a block: 1 for formats that are not compressed
	uint32_t BytesPerBlock;
};

uint64_t GetMipByteSize(const Format& format, uint32_t width, uint32_t height)
{
	const uint64_t blocksX = (width + format.BlockSide - 1) / format.BlockSide;
	const uint64_t blocksY = (height + format.BlockSide - 1) / format.BlockSide;
	return blocksX * blocksY * format.BytesPerBlock;
}

int main()
{
	const Format formats[] = { { "RGBA8", 1, 4 }, { "BC1", 4, 8 }, { "BC7", 4, 16 }, { "RGBA16F", 1, 8 } };
	for (const Format& format : formats)
	{
		uint64_t chain = 0;
		uint32_t levels = 0;
		for (uint32_t side = 4096; side >= 1; side /= 2)
		{
			chain += GetMipByteSize(format, side, side);
			levels++;
		}
		std::printf("%-8s %u levels, level 0 %llu bytes, chain %llu bytes\n", format.Name, levels,
			static_cast<unsigned long long>(GetMipByteSize(format, 4096, 4096)), static_cast<unsigned long long>(chain));
	}
	return 0;
}
