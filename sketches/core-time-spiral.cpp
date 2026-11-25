// The spiral of death: a step costs 30 ms of work but simulates only 20 ms, so each frame is longer than the one before.
// The cap bounds the spiral; time dilation stops the catch-up steps instead. Times are whole milliseconds.
#include <cstdio>

namespace
{
	constexpr int c_Step = 20;     // ms of game time in one fixed step
	constexpr int c_StepCost = 30; // ms of work one step takes
	constexpr int c_MaxSteps = 8;  // the most steps one frame runs

	void Run(const char* name, bool dilation)
	{
		std::printf("%s\n", name);
		int accumulator = 0;
		int frame = c_Step; // each frame lasts as long as the work of the frame before it
		int gameTime = 0;
		int wallTime = 0;
		for (int number = 1; number <= 8; number++)
		{
			accumulator += frame;
			int steps = 0;
			bool dilated = false;
			while (accumulator >= c_Step && steps < c_MaxSteps)
			{
				// The steps so far took longer than the time they simulated: stop catching up.
				if (dilation && steps > 0 && steps * c_StepCost >= steps * c_Step)
				{
					dilated = true;
					break;
				}
				accumulator -= c_Step;
				steps++;
			}
			if (dilated)
				accumulator %= c_Step; // the steps still due are dropped; a fraction of a step stays
			else if (steps == c_MaxSteps && accumulator > c_Step)
				accumulator = c_Step; // the backlog is dropped
			gameTime += steps * c_Step;
			wallTime += frame;
			std::printf("frame %d: %3d ms long, %d steps, game time %3d ms of %3d ms\n", number, frame, steps, gameTime, wallTime);
			frame = steps * c_StepCost;
		}
	}
}

int main()
{
	Run("cap only", false);
	Run("time dilation", true);
}
