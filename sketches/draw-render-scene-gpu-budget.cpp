#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <vector>

constexpr uint64_t c_RecordBytes = 64;
constexpr uint64_t c_InstanceBytes = 64;

// Counts the frames that a queue of new proxies needs. Each entry is a proxy's instance count, oldest first.
uint32_t CountFrames(const std::vector<uint32_t>& instanceCounts, uint64_t budget)
{
	size_t head = 0;
	uint32_t frames = 0;
	while (head < instanceCounts.size())
	{
		uint64_t left = budget;
		uint32_t taken = 0;
		while (head < instanceCounts.size())
		{
			const uint64_t bytes = c_RecordBytes + instanceCounts[head] * c_InstanceBytes;
			// A proxy that does not fit waits, but every frame takes at least one.
			if (bytes > left && taken > 0)
				break;
			left -= std::min(left, bytes);
			taken++;
			head++;
		}
		frames++;
	}
	return frames;
}

int main()
{
	constexpr uint64_t c_SixteenMiB = 16ull << 20;
	std::printf("1000 cubes, 128 proxies a frame: %u frames\n", CountFrames(std::vector<uint32_t>(1000, 1), 128 * 128));
	std::printf("100000 cubes, 16 MiB: %u frame\n", CountFrames(std::vector<uint32_t>(100000, 1), c_SixteenMiB));
	std::printf("100000 proxies of 3 instances, 16 MiB: %u frames\n", CountFrames(std::vector<uint32_t>(100000, 3), c_SixteenMiB));
	std::printf("3 proxies, a budget of zero: %u frames\n", CountFrames(std::vector<uint32_t>(3, 1), 0));
	return 0;
}
