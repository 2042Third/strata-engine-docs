// The same accumulator at the project rate of 120 steps each second, with a cap of 16.
#include <cstdio>
#include <vector>

int main()
{
	const float step = 1.0f / 120.0f;
	const int maxSteps = 16;
	const std::vector<float> frames = { 0.0167f, 0.0340f, 0.0069f, 0.0069f, 0.0069f, 0.2000f, 0.0200f };
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
