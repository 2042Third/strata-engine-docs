// Where a cooked texture of 256x256 texels in BC7 keeps its levels: header, mip table, name, then smallest first.
#include <algorithm>
#include <cstdint>
#include <cstdio>

uint64_t AlignUp(uint64_t value, uint64_t alignment)
{
	return (value + alignment - 1) / alignment * alignment;
}

uint64_t GetBC7Size(uint32_t width, uint32_t height)
{
	return static_cast<uint64_t>((width + 3) / 4) * ((height + 3) / 4) * 16;
}

int main()
{
	const uint32_t size = 256;
	const uint32_t mipCount = 9; // 256, 128, 64, 32, 16, 8, 4, 2, 1
	const uint64_t nameLength = 9; // "Brick.png"
	const uint64_t headerBytes = 40;
	const uint64_t tableEntryBytes = 24;

	const uint64_t dataOffset = AlignUp(headerBytes + mipCount * tableEntryBytes + nameLength, 16);
	std::printf("pixel data starts at %llu\n", static_cast<unsigned long long>(dataOffset));

	uint64_t offset = dataOffset;
	for (uint32_t level = mipCount; level-- > 0;)
	{
		const uint32_t side = std::max(1u, size >> level);
		const uint64_t bytes = GetBC7Size(side, side);
		std::printf("level %u (%ux%u): offset %llu, size %llu\n", level, side, side, static_cast<unsigned long long>(offset),
			static_cast<unsigned long long>(bytes));
		offset = AlignUp(offset + bytes, 16);
	}
	std::printf("file ends at %llu\n", static_cast<unsigned long long>(offset));
	return 0;
}
