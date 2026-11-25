// The fixed-step accumulator with the engine's cap: uneven frames in, whole steps out, a backlog dropped.
// Times are whole milliseconds, so every number is exact. The step is 10 ms and a frame runs at most 8 steps.
#include <algorithm>
#include <cstdio>

int main()
{
	constexpr int c_Step = 10;     // ms of game time in one fixed step
	constexpr int c_MaxSteps = 8;  // the most steps one frame runs
	const int frames[] = { 35, 6, 4, 16, 10000 }; // ms: how long each frame took

	int accumulator = 0; // ms of game time that no step has simulated yet
	for (const int frame : frames)
	{
		accumulator += frame;
		int steps = 0;
		while (accumulator >= c_Step && steps < c_MaxSteps)
		{
			accumulator -= c_Step; // here the engine runs OnFixedUpdate
			steps++;
		}
		int dropped = 0;
		if (steps == c_MaxSteps && accumulator > c_Step)
		{
			dropped = (accumulator - c_Step) / c_Step;
			accumulator = c_Step;
		}
		std::printf("frame %5d ms: %d steps, %3d dropped, %2d ms left\n", frame, steps, dropped, accumulator);
	}
}
