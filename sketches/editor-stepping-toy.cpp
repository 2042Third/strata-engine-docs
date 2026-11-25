#include <cstdint>
#include <cstdio>

// A falling ball moved by fixed steps of 10 ms. Times are whole milliseconds, so the sums are exact.
struct ToyScene
{
	static constexpr uint32_t c_StepMs = 10;

	bool Paused = false;
	uint32_t StepFrames = 0;
	uint64_t FixedSteps = 0;
	uint32_t AccumulatorMs = 0;
	double Height = 100.0;
	double Speed = 0.0;

	void SetPaused(bool paused)
	{
		Paused = paused;
		if (!paused)
			StepFrames = 0;
	}

	void Step(uint32_t frames) { StepFrames += frames; }

	void Update(uint32_t frameMs)
	{
		if (Paused)
		{
			if (StepFrames == 0)
				return;
			StepFrames--;
			RunFixedStep();
			return;
		}
		AccumulatorMs += frameMs;
		while (AccumulatorMs >= c_StepMs)
		{
			AccumulatorMs -= c_StepMs;
			RunFixedStep();
		}
	}

	void RunFixedStep()
	{
		const double seconds = c_StepMs / 1000.0;
		Speed -= 9.8 * seconds;
		Height += Speed * seconds;
		FixedSteps++;
	}
};

int main()
{
	const uint32_t frameLengths[] = { 8, 33 };
	for (const uint32_t frameMs : frameLengths)
	{
		ToyScene waiting;
		for (int frame = 0; frame < 60; frame++)
			waiting.Update(frameMs);

		ToyScene stepped;
		stepped.SetPaused(true);
		stepped.Step(60);
		for (int frame = 0; frame < 60; frame++)
			stepped.Update(frameMs);

		std::printf("frames of %2u ms | wait 60 frames: %3llu steps, height %6.2f | step 60: %llu steps, height %6.2f\n", frameMs,
			static_cast<unsigned long long>(waiting.FixedSteps), waiting.Height, static_cast<unsigned long long>(stepped.FixedSteps),
			stepped.Height);
	}
	return 0;
}
