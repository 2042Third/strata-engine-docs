#include <algorithm>
#include <cstdio>
#include <deque>
#include <string>
#include <utility>
#include <vector>

// A pretend GPU: it counts the frames it was given and the frames it finished.
struct FakeGpu
{
	int Submitted = 0;
	int Finished = 0;

	void SubmitFrame() { Submitted++; }
	void Finish(int frames) { Finished = std::min(Finished + frames, Submitted); }
	bool HasReached(int fence) const { return Finished >= fence; }
};

class DeletionQueue
{
public:
	explicit DeletionQueue(const FakeGpu& gpu)
		: m_Gpu(gpu)
	{
	}

	// The fence is the number of frames submitted so far: every frame that may use the resources is below it.
	void Release(std::vector<std::string> names)
	{
		m_Pending.push_back({ std::move(names), m_Gpu.Submitted });
	}

	// Destroys completed resources, oldest first, until the budget is spent. Returns how many it destroyed.
	int Collect(int budgetMicroseconds)
	{
		while (!m_Pending.empty() && m_Gpu.HasReached(m_Pending.front().Fence))
		{
			for (std::string& name : m_Pending.front().Names)
				m_Completed.push_back(std::move(name));
			m_Pending.pop_front();
		}

		int spent = 0;
		int destroyed = 0;
		while (!m_Completed.empty())
		{
			m_Completed.pop_front();
			destroyed++;
			spent += 100; // A texture costs about 100 microseconds to destroy.
			if (spent >= budgetMicroseconds)
				break;
		}
		return destroyed;
	}

	size_t GetHeldCount() const
	{
		size_t held = m_Completed.size();
		for (const Batch& batch : m_Pending)
			held += batch.Names.size();
		return held;
	}

private:
	struct Batch
	{
		std::vector<std::string> Names;
		int Fence;
	};

	const FakeGpu& m_Gpu;
	std::deque<Batch> m_Pending;
	std::deque<std::string> m_Completed;
};

int main()
{
	FakeGpu gpu;
	DeletionQueue queue(gpu);

	for (int frame = 0; frame < 3; frame++)
		gpu.SubmitFrame();
	queue.Release({ "t0", "t1", "t2", "t3", "t4", "t5", "t6", "t7" });

	for (int round = 1; round <= 6; round++)
	{
		gpu.SubmitFrame();
		gpu.Finish(1);
		const int destroyed = queue.Collect(250);
		std::printf("frame %d: gpu finished %d of %d, destroyed %d, held %zu\n", round, gpu.Finished, gpu.Submitted, destroyed, queue.GetHeldCount());
	}
	return 0;
}
