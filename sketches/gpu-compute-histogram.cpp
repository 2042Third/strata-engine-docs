#include <array>
#include <cstdio>
#include <vector>

// A CPU emulation of one dispatch: every "group" owns its own small histogram (the shared memory), fills it,
// and only then adds it to the global histogram (the buffer every group shares).
constexpr int c_BinCount = 4;
constexpr int c_GroupSize = 4;

int main()
{
	// Twelve pixels, each already reduced to a bin number from 0 to 3.
	const std::vector<int> pixels = { 0, 1, 1, 3, 2, 2, 2, 0, 3, 3, 3, 1 };
	const int groupCount = (static_cast<int>(pixels.size()) + c_GroupSize - 1) / c_GroupSize;

	std::array<int, c_BinCount> global = {};
	for (int group = 0; group < groupCount; group++)
	{
		std::array<int, c_BinCount> shared = {};
		for (int thread = 0; thread < c_GroupSize; thread++)
		{
			const int pixel = group * c_GroupSize + thread;
			if (pixel < static_cast<int>(pixels.size()))
				shared[pixels[pixel]]++;
		}
		for (int bin = 0; bin < c_BinCount; bin++)
			global[bin] += shared[bin];
		std::printf("group %d: %d %d %d %d\n", group, shared[0], shared[1], shared[2], shared[3]);
	}
	std::printf("global:  %d %d %d %d\n", global[0], global[1], global[2], global[3]);

	// Exclusive prefix sum: the start of each bin's output range.
	int running = 0;
	for (int bin = 0; bin < c_BinCount; bin++)
	{
		std::printf("bin %d starts at %d\n", bin, running);
		running += global[bin];
	}
	return 0;
}
