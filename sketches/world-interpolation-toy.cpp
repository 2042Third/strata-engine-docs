// A toy interpolation: a body steps at 60 Hz, frames come at 144 Hz, and the drawn position is printed both ways.
#include <cstdio>
#include <vector>

int main()
{
	const float step = 1.0f / 60.0f;
	const float speed = 6.0f; // metres per second: 0.1 m a step
	// Mostly 144 Hz frames, with one slow frame of 40 ms in the middle that needs two steps.
	std::vector<float> frames(12, 1.0f / 144.0f);
	frames[6] = 0.040f;

	float accumulator = 0.0f;
	float position = 0.0f; // the simulation's pose, after the latest step
	float from = 0.0f;     // the pose before the latest stepping frame's steps
	float to = 0.0f;       // the pose after them
	int steps = 1;         // how many steps that frame ran
	float lastBlended = 0.0f;
	float lastPlain = 0.0f;

	std::printf("frame steps  alpha  plain(m)  moved(m)  blended(m)  moved(m)\n");
	for (size_t index = 0; index < frames.size(); index++)
	{
		accumulator += frames[index];
		int ran = 0;
		const float before = position;
		while (accumulator >= step)
		{
			position += speed * step;
			accumulator -= step;
			ran++;
		}
		if (ran > 0)
		{
			from = before;
			to = position;
			steps = ran;
		}
		// The drawn time is T + a - h, where T is the end of the latest step and a the accumulator.
		const float alpha = 1.0f - (1.0f - accumulator / step) / static_cast<float>(steps);
		const float blended = from + (to - from) * alpha;
		std::printf("%5zu %5d %6.3f  %8.3f  %8.3f  %10.3f  %8.3f\n", index, ran, alpha, position, position - lastPlain, blended,
			blended - lastBlended);
		lastPlain = position;
		lastBlended = blended;
	}
	return 0;
}
