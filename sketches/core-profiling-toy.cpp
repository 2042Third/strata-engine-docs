// A toy stage timer: stages nest, and each one records only its own time (its self time).
// The clock is simulated in whole microseconds, so the output is the same on every machine.
#include <cstdint>
#include <cstdio>

namespace
{
	constexpr uint32_t c_StageCount = 4;
	constexpr uint32_t c_MaxDepth = 3;
	constexpr const char* c_Names[c_StageCount] = { "Update", "Physics", "Render", "Extra" };
	int64_t s_Now = 0; // the simulated clock, in microseconds

	struct OpenStage
	{
		uint32_t Stage = 0;
		int64_t Start = 0;
	};

	int64_t s_SelfTime[c_StageCount] = {};
	OpenStage s_Open[c_MaxDepth] = {};
	uint32_t s_Depth = 0;

	// Returns whether the stage was entered: only then must EndStage follow.
	bool BeginStage(uint32_t stage)
	{
		if (s_Depth == c_MaxDepth)
			return false; // too deep: its time counts for the stage around it
		if (s_Depth > 0) // the stage around this one pauses
			s_SelfTime[s_Open[s_Depth - 1].Stage] += s_Now - s_Open[s_Depth - 1].Start;
		s_Open[s_Depth++] = { stage, s_Now };
		return true;
	}

	void EndStage()
	{
		const OpenStage& inner = s_Open[--s_Depth];
		s_SelfTime[inner.Stage] += s_Now - inner.Start;
		if (s_Depth > 0) // the stage around it resumes
			s_Open[s_Depth - 1].Start = s_Now;
	}

	class StageScope
	{
	public:
		explicit StageScope(uint32_t stage)
			: m_Active(BeginStage(stage))
		{
		}

		~StageScope()
		{
			if (m_Active)
				EndStage();
		}
	private:
		bool m_Active;
	};
}

int main()
{
	{
		StageScope update(0);
		s_Now += 2000;
		{
			StageScope physics(1);
			s_Now += 3000;
			{
				StageScope render(2);
				s_Now += 1000;
				StageScope extra(3); // a fourth level: not timed
				s_Now += 500;
			}
		}
		s_Now += 1000;
	}
	for (uint32_t stage = 0; stage < c_StageCount; stage++)
		std::printf("%-8s %.1f ms\n", c_Names[stage], static_cast<double>(s_SelfTime[stage]) / 1000.0);
	std::printf("elapsed  %.1f ms\n", static_cast<double>(s_Now) / 1000.0);
}
