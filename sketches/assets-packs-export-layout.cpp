// Lays out entries of a pack the way the writer does, assuming every block is stored as it is.
#include <cstdint>
#include <cstdio>
#include <vector>

int main()
{
	constexpr uint64_t c_BlockSize = 256 * 1024;
	constexpr uint64_t c_EntryAlignment = 4096;
	const std::vector<uint64_t> sizes = { 600000, 100, 0, 262144 };

	uint64_t position = 64; // The header
	uint64_t blockTotal = 0;
	for (size_t index = 0; index < sizes.size(); index++)
	{
		const uint64_t blocks = (sizes[index] + c_BlockSize - 1) / c_BlockSize;
		if (sizes[index] > 0)
			position = (position + c_EntryAlignment - 1) / c_EntryAlignment * c_EntryAlignment;
		std::printf("entry %zu: %llu bytes, %llu blocks, starts at %llu\n", index, static_cast<unsigned long long>(sizes[index]),
			static_cast<unsigned long long>(blocks), static_cast<unsigned long long>(position));
		position += sizes[index];
		blockTotal += blocks;
	}
	const uint64_t tables = sizes.size() * 88 + blockTotal * 24;
	std::printf("data ends at %llu, tables (without strings) take %llu bytes\n", static_cast<unsigned long long>(position),
		static_cast<unsigned long long>(tables));
	return 0;
}
