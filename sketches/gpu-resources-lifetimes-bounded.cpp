#include <algorithm>
#include <cstdio>
#include <deque>
#include <string>
#include <utility>
#include <vector>

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

	// Like the engine's queue, a release also destroys as many completed resources as it takes over.
	void Release(std::vector<std::string> names)
	{
		MoveCompleted();
		for (size_t index = 0; index < names.size() && !m_Completed.empty(); index++)
			m_Completed.pop_front();
		m_Pending.push_back({ std::move(names), m_Gpu.Submitted });
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

	void MoveCompleted()
	{
		while (!m_Pending.empty() && m_Gpu.HasReached(m_Pending.front().Fence))
		{
			for (std::string& name : m_Pending.front().Names)
				m_Completed.push_back(std::move(name));
			m_Pending.pop_front();
		}
	}

	const FakeGpu& m_Gpu;
	std::deque<Batch> m_Pending;
	std::deque<std::string> m_Completed;
};

int main()
{
	FakeGpu gpu;
	DeletionQueue queue(gpu);

	// A tool that renders without a frame loop: it releases two resources after every submitted frame and never calls Collect.
	for (int step = 1; step <= 8; step++)
	{
		gpu.SubmitFrame();
		gpu.Finish(1);
		queue.Release({ "a", "b" });
		std::printf("step %d: held %zu\n", step, queue.GetHeldCount());
	}
	return 0;
}
