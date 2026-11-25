#include <algorithm>
#include <cstdint>
#include <cstdio>

// The swap chain's image count: one more than the surface's minimum and than the frames in flight, and no more than the
// surface's maximum (0 means the surface has no maximum).
uint32_t ChooseImageCount(uint32_t minImageCount, uint32_t maxImageCount, uint32_t framesInFlight)
{
	uint32_t count = std::max(minImageCount + 1, framesInFlight + 1);
	if (maxImageCount > 0)
		count = std::min(count, maxImageCount);
	return count;
}

// 0 is first in, first out (always supported), 1 is mailbox, 2 is immediate.
int ChoosePresentMode(bool vsync, bool hasMailbox, bool hasImmediate)
{
	if (vsync)
		return 0;
	if (hasMailbox)
		return 1;
	return hasImmediate ? 2 : 0;
}

int main()
{
	struct Case
	{
		uint32_t Min;
		uint32_t Max;
		uint32_t Frames;
	};
	const Case cases[] = { { 2, 0, 2 }, { 2, 0, 4 }, { 3, 4, 4 }, { 2, 2, 2 } };
	for (const Case& item : cases)
		std::printf("min %u max %u frames %u -> %u images\n", static_cast<unsigned>(item.Min), static_cast<unsigned>(item.Max),
			static_cast<unsigned>(item.Frames), static_cast<unsigned>(ChooseImageCount(item.Min, item.Max, item.Frames)));
	std::printf("vsync on: mode %d\n", ChoosePresentMode(true, true, true));
	std::printf("vsync off, mailbox: mode %d\n", ChoosePresentMode(false, true, true));
	std::printf("vsync off, only immediate: mode %d\n", ChoosePresentMode(false, false, true));
	std::printf("vsync off, neither: mode %d\n", ChoosePresentMode(false, false, false));
	return 0;
}
