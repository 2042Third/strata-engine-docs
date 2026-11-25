// How fine must a sleep's tick be to hold a cap of 120 frames a second? The clock is simulated, in microseconds.
#include <cstdint>
#include <cstdio>
#include <initializer_list>

namespace
{
	// The frames in one second when each wait ends at the first tick at or after the frame's slot.
	int CountFrames(int64_t period, int64_t tick)
	{
		int64_t now = 0;
		int64_t nextFrame = period;
		int frames = 0;
		while (now < 1'000'000)
		{
			now = (nextFrame + tick - 1) / tick * tick;
			frames++;
			nextFrame += period;
			if (nextFrame < now)
				nextFrame = now;
		}
		return frames;
	}
}

int main()
{
	for (const int64_t tick : { 15625, 8000, 4000, 1000 })
		std::printf("tick %6.3f ms: %3d frames at a cap of 120\n", static_cast<double>(tick) / 1000.0, CountFrames(1'000'000 / 120, tick));
	return 0;
}
