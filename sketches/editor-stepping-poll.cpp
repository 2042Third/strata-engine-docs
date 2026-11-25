#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <optional>
#include <string>

// A paused game that runs one step per frame, with the counters play.step's poll reads.
struct ToyGame
{
	bool Paused = true;
	uint32_t StepFrames = 0;
	uint64_t FixedSteps = 0;
	uint64_t FixedStepsAtResume = 0;
	uint32_t ResumeCount = 0;

	void Resume()
	{
		if (Paused)
		{
			FixedStepsAtResume = FixedSteps;
			ResumeCount++;
		}
		Paused = false;
		StepFrames = 0;
	}

	void Frame()
	{
		if (Paused && StepFrames > 0)
		{
			StepFrames--;
			FixedSteps++;
		}
	}
};

// Returns the answer once the request is over, or nothing while it waits.
std::optional<std::string> Poll(const ToyGame& game, uint64_t first, int64_t steps, uint32_t resumes)
{
	const auto ran = [first, steps](uint64_t count) { return std::clamp<int64_t>(static_cast<int64_t>(count) - static_cast<int64_t>(first), 0, steps); };
	const bool resumed = game.ResumeCount != resumes;
	const uint64_t seen = resumed ? game.FixedStepsAtResume : game.FixedSteps;
	if (seen >= first + steps)
		return "answers: stepsRun " + std::to_string(steps);
	if (resumed)
		return "fails: stepsRun " + std::to_string(ran(seen));
	return std::nullopt;
}

int main()
{
	ToyGame game;
	const uint64_t first = game.FixedSteps + game.StepFrames;
	game.StepFrames += 10;
	const uint32_t resumes = game.ResumeCount;
	for (int frame = 1; frame <= 6; frame++)
	{
		game.Frame();
		if (frame == 4)
			game.Resume();
		const std::optional<std::string> answer = Poll(game, first, 10, resumes);
		std::printf("frame %d: %llu steps run, %s\n", frame, static_cast<unsigned long long>(game.FixedSteps),
			answer ? answer->c_str() : "still waiting");
		if (answer)
			break;
	}
	return 0;
}
