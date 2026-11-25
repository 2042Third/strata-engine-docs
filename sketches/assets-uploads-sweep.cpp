#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <vector>

constexpr uint64_t c_MiB = 1ull << 20;

// The finalize contract without a GPU: a finalizer sees the bytes left of the frame and reports what it uploaded.
struct Context
{
	uint64_t UploadBudget = 0;
	bool FirstOfFrame = false;
};

class SteppedAsset
{
public:
	SteppedAsset(uint32_t steps, uint64_t stepBytes)
		: m_Steps(steps), m_StepBytes(stepBytes)
	{
	}

	// Returns the bytes uploaded; Done tells whether the asset is complete.
	uint64_t Finalize(const Context& context, bool& done)
	{
		uint64_t uploaded = 0;
		while (m_Done < m_Steps)
		{
			const bool framesFirst = context.FirstOfFrame && uploaded == 0;
			if (!framesFirst && uploaded + m_StepBytes > context.UploadBudget)
				break;
			uploaded += m_StepBytes;
			m_Done++;
		}
		done = m_Done == m_Steps;
		return uploaded;
	}

private:
	uint32_t m_Steps;
	uint64_t m_StepBytes;
	uint32_t m_Done = 0;
};

int main()
{
	const uint64_t budgets[] = { 1 * c_MiB, 2 * c_MiB, 4 * c_MiB, 8 * c_MiB, 16 * c_MiB };
	for (const uint64_t budget : budgets)
	{
		std::vector<SteppedAsset> queue(2, SteppedAsset(4, 3 * c_MiB));
		size_t next = 0;
		int frames = 0;
		uint64_t largest = 0;
		while (next < queue.size())
		{
			uint64_t uploaded = 0;
			bool first = true;
			while (next < queue.size() && (first || uploaded < budget))
			{
				bool done = false;
				uploaded += queue[next].Finalize(Context { budget - std::min(uploaded, budget), first }, done);
				first = false;
				if (!done)
					break;
				next++;
			}
			largest = std::max(largest, uploaded);
			frames++;
		}
		std::printf("budget %2llu MiB: %d frames, largest frame %2llu MiB%s\n", static_cast<unsigned long long>(budget / c_MiB), frames,
			static_cast<unsigned long long>(largest / c_MiB), largest > budget ? " (over: the first step)" : "");
	}
	return 0;
}
