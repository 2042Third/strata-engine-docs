#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <vector>

constexpr uint64_t c_MiB = 1ull << 20;

enum class Result
{
	Done,
	Pending
};

// What one call may do: the bytes left of the frame's budget, and whether the call is the frame's first.
struct Context
{
	uint64_t UploadBudget = 0;
	bool FirstOfFrame = false;
	uint64_t* UploadedBytes = nullptr;
};

// An asset that uploads in equal steps. It never records into a graphics API: it only says how many bytes it moved.
class SteppedAsset
{
public:
	SteppedAsset(uint32_t steps, uint64_t stepBytes)
		: m_Steps(steps), m_StepBytes(stepBytes)
	{
	}

	Result Finalize(const Context& context)
	{
		uint64_t uploaded = 0;
		while (m_Done < m_Steps)
		{
			// Only the frame's first step ignores the budget, so every frame makes progress.
			const bool framesFirst = context.FirstOfFrame && uploaded == 0;
			if (!framesFirst && uploaded + m_StepBytes > context.UploadBudget)
				break;
			uploaded += m_StepBytes;
			m_Done++;
		}
		*context.UploadedBytes += uploaded;
		return m_Done < m_Steps ? Result::Pending : Result::Done;
	}

private:
	uint32_t m_Steps;
	uint64_t m_StepBytes;
	uint32_t m_Done = 0;
};

int main()
{
	std::vector<SteppedAsset> queue(3, SteppedAsset(3, c_MiB));
	const uint64_t frameBudget = 2 * c_MiB;
	size_t next = 0;
	for (int frame = 1; next < queue.size(); frame++)
	{
		uint64_t uploaded = 0;
		bool first = true;
		while (next < queue.size())
		{
			if (!first && uploaded >= frameBudget)
				break;
			const Context context { frameBudget - std::min(uploaded, frameBudget), first, &uploaded };
			const Result result = queue[next].Finalize(context);
			first = false;
			if (result == Result::Pending)
				break; // Keeps its place in line
			next++;
		}
		std::printf("frame %d: %llu MiB\n", frame, static_cast<unsigned long long>(uploaded / c_MiB));
	}
	return 0;
}
