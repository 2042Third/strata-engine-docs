// A frame-rate cap on a system whose sleep wakes only at timer ticks, against a sleep that wakes at the deadline.
// The clock is simulated in microseconds, so the output is the same on every machine.
#include <cstdint>
#include <cstdio>
#include <initializer_list>

namespace
{
	constexpr int64_t c_Tick = 15625; // 15.625 ms: 64 ticks a second

	// An ordinary sleep: the thread wakes at the first tick at or after the deadline.
	int64_t WakeAtTick(int64_t deadline)
	{
		return (deadline + c_Tick - 1) / c_Tick * c_Tick;
	}

	// The frames a cap lets through in one second, with the schedule of a frame pacer and frames that cost nothing.
	int CountFrames(int64_t period, bool precise)
	{
		int64_t now = 0;
		int64_t nextFrame = period;
		int frames = 0;
		while (now < 1'000'000)
		{
			now = precise ? nextFrame : WakeAtTick(nextFrame);
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
	for (const int rate : { 60, 120 })
	{
		const int64_t period = 1'000'000 / rate;
		std::printf("cap %3d: ordinary sleep %3d frames, precise sleep %3d frames\n", rate, CountFrames(period, false),
			CountFrames(period, true));
	}

	// The start of each frame under a cap of 60 and an ordinary sleep: most frames take one tick and a few take two.
	const int64_t period = 1'000'000 / 60;
	int64_t nextFrame = period;
	int64_t previous = 0;
	std::printf("intervals at cap 60:");
	for (int frame = 0; frame < 20; frame++)
	{
		const int64_t now = WakeAtTick(nextFrame);
		std::printf(" %.1f", static_cast<double>(now - previous) / 1000.0);
		previous = now;
		nextFrame += period;
		if (nextFrame < now)
			nextFrame = now;
	}
	std::printf(" ms\n");
	return 0;
}
