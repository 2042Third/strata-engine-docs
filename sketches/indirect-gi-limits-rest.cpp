#include <cstdint>
#include <cstdio>

// What the renderer waits before a moved object counts as resting, by the clock.
const double c_RestSeconds = 0.25;
// What an earlier design waited, by a count of frames.
const uint32_t c_RestFrames = 30;

// Adds one frame's time per frame until the clock reaches the wait; returns the frames that took.
static uint32_t CountFramesToRest(double framesPerSecond)
{
	const double frameSeconds = 1.0 / framesPerSecond;
	double waited = 0.0;
	uint32_t frames = 0;
	while (waited < c_RestSeconds)
	{
		waited += frameSeconds;
		frames++;
	}
	return frames;
}

int main()
{
	const double rates[] = { 30.0, 45.0, 75.0, 90.0 };
	std::printf("fps  frames  clock(s)  count(s)\n");
	for (const double rate : rates)
	{
		const uint32_t frames = CountFramesToRest(rate);
		std::printf("%3.0f  %6u  %8.3f  %8.3f\n", rate, frames, frames / rate, c_RestFrames / rate);
	}
	return 0;
}
