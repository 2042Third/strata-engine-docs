// How many fixed steps each frame runs, for a list of frame times.
#include <cstdio>
#include <vector>

int main()
{
	const float step = 1.0f / 60.0f;
	const int maxSteps = 8;
	const std::vector<float> frames = { 0.0167f, 0.0340f, 0.0069f, 0.0069f, 0.0069f, 0.2000f, 0.0167f };
	float accumulator = 0.0f;
	for (const float frame : frames)
	{
		accumulator += frame;
		int steps = 0;
		while (accumulator >= step && steps < maxSteps)
		{
			accumulator -= step;
			steps++;
		}
		if (steps == maxSteps && accumulator > step)
			accumulator = step; // Too far behind: drop the rest of the backlog.
		std::printf("frame %.4f s: %d steps, %.4f s left\n", frame, steps, accumulator);
	}
	return 0;
}
