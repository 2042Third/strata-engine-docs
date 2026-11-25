// A header claims some records of 16 bytes after 12 header bytes; the file has 60 bytes.
#include <cstdint>
#include <cstdio>
#include <initializer_list>

bool CountFits(uint64_t fileSize, uint32_t count)
{
	return fileSize >= 12 && count <= (fileSize - 12) / 16;
}

int main()
{
	const uint64_t fileSize = 60; // 12 + 3 * 16
	for (const uint32_t count : { 3u, 4u, 0x10000001u })
	{
		const uint32_t naiveEnd = 12 + count * 16; // 32-bit arithmetic wraps around
		std::printf("count %u: naive end %u, naive check %s, bounded check %s\n", count, naiveEnd, naiveEnd <= fileSize ? "passes" : "fails", CountFits(fileSize, count) ? "passes" : "fails");
	}
}
