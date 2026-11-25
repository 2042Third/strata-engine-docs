// A sequence lock: one writer thread hands samples to one reader thread, and neither ever waits for the other.
#include <atomic>
#include <cstdint>
#include <cstdio>
#include <thread>

namespace
{
	struct Sample
	{
		uint32_t Index = 0;
		uint32_t Twice = 0; // always 2 * Index: a sample that mixes two writes breaks this
	};

	class Handoff
	{
	public:
		// The writer thread.
		void Publish(const Sample& value)
		{
			const uint64_t sequence = m_Sequence.load(std::memory_order_relaxed);
			m_Sequence.store(sequence + 1, std::memory_order_relaxed); // odd: a write is running
			std::atomic_thread_fence(std::memory_order_release);
			m_Index.store(value.Index, std::memory_order_relaxed);
			m_Twice.store(value.Twice, std::memory_order_relaxed);
			m_Sequence.store(sequence + 2, std::memory_order_release); // even: the write is done
		}

		// The reader thread: false when nothing new was published or the writer is in the middle of a write.
		bool TakeNew(Sample& outValue)
		{
			const uint64_t sequence = m_Sequence.load(std::memory_order_acquire);
			if (sequence == m_Taken || (sequence & 1u) != 0)
				return false;

			Sample value;
			value.Index = m_Index.load(std::memory_order_relaxed);
			value.Twice = m_Twice.load(std::memory_order_relaxed);
			std::atomic_thread_fence(std::memory_order_acquire);
			if (m_Sequence.load(std::memory_order_relaxed) != sequence)
				return false; // rewritten while it was read

			outValue = value;
			m_Taken = sequence;
			return true;
		}
	private:
		std::atomic<uint64_t> m_Sequence = 0;
		std::atomic<uint32_t> m_Index = 0;
		std::atomic<uint32_t> m_Twice = 0;
		uint64_t m_Taken = 0; // the reader thread only
	};
}

int main()
{
	constexpr uint32_t c_Count = 200000;
	Handoff handoff;
	std::atomic<bool> finished = false;
	std::thread writer([&]()
	{
		for (uint32_t index = 1; index <= c_Count; index++)
			handoff.Publish({ index, 2 * index });
		finished = true;
	});

	uint32_t torn = 0;
	uint32_t last = 0;
	while (true)
	{
		const bool wasFinished = finished.load(); // read first: after the last write, one more take finds the last sample
		Sample sample;
		if (handoff.TakeNew(sample))
		{
			if (sample.Twice != 2 * sample.Index)
				torn++;
			last = sample.Index;
		}
		else if (wasFinished)
			break;
	}
	writer.join();
	std::printf("torn samples: %u\n", torn);
	std::printf("last sample taken: %u\n", last);
	return 0;
}
