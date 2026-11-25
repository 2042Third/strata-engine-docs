#include <cstdint>
#include <cstdio>
#include <deque>
#include <vector>

// A table of slots whose reuse waits for the frames that may still read them.
class SlotTable
{
public:
	explicit SlotTable(uint32_t framesInFlight)
		: m_FramesInFlight(framesInFlight)
	{
	}

	uint32_t Allocate()
	{
		if (m_Free.empty())
			return m_Next++;
		const uint32_t slot = m_Free.back();
		m_Free.pop_back();
		return slot;
	}

	void Release(uint32_t slot) { m_Pending.push_back({ slot, m_Frame }); }

	void BeginFrame(uint64_t frame)
	{
		m_Frame = frame;
		while (!m_Pending.empty() && m_Pending.front().Frame + m_FramesInFlight + 1 <= frame)
		{
			m_Free.push_back(m_Pending.front().Slot);
			m_Pending.pop_front();
		}
	}

private:
	struct Pending
	{
		uint32_t Slot;
		uint64_t Frame;
	};
	uint32_t m_FramesInFlight;
	uint32_t m_Next = 3; // Slots 0 to 2 are reserved
	uint64_t m_Frame = 0;
	std::vector<uint32_t> m_Free;
	std::deque<Pending> m_Pending;
};

int main()
{
	SlotTable table(2);
	const uint32_t first = table.Allocate();
	table.Release(first);
	for (uint64_t frame = 1; frame <= 4; frame++)
	{
		table.BeginFrame(frame);
		std::printf("frame %llu: next slot %u\n", static_cast<unsigned long long>(frame), table.Allocate());
	}
	return 0;
}
