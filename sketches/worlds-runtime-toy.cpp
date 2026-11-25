// A toy of the runtime's rule for runs that end by themselves: every fixed step runs, and the game's played time counts
// steps, never the wall clock. All times are whole milliseconds, so the output is exact.
#include <algorithm>
#include <cstdio>

constexpr int c_StepMs = 20; // One fixed step: 50 steps a second
constexpr int c_MaxSteps = 4; // The most steps one update runs

struct ToyScene
{
	int Accumulator = 0;
	int Steps = 0;
};

// One update: the frame's time is limited to what the most steps can simulate, so no step is ever dropped.
void Update(ToyScene& scene, int frameMs)
{
	scene.Accumulator += std::min(frameMs, c_MaxSteps * c_StepMs);
	while (scene.Accumulator >= c_StepMs)
	{
		scene.Accumulator -= c_StepMs;
		scene.Steps++;
	}
}

double PlayedSeconds(const ToyScene& scene)
{
	return scene.Steps * c_StepMs / 1000.0;
}

void Report(const char* machine, int frameMs)
{
	ToyScene byFrames;
	for (int frame = 0; frame < 250; frame++)
		Update(byFrames, frameMs);
	std::printf("%-8s --frames 250: %5.2f s of game time\n", machine, PlayedSeconds(byFrames));

	ToyScene bySeconds;
	int frames = 0;
	while (PlayedSeconds(bySeconds) < 5.0)
	{
		Update(bySeconds, frameMs);
		frames++;
	}
	std::printf("%-8s --seconds 5:  %3d frames (%.2f s)\n", machine, frames, PlayedSeconds(bySeconds));
}

int main()
{
	Report("fast", 20);
	Report("middle", 50);
	Report("slow", 200);
	return 0;
}
