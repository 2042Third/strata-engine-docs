#include <cstdint>
#include <cstdio>
#include <vector>

// A ring of staging slots. A slot is free again once the GPU finished the frame whose copies read it.
struct Slot
{
	int64_t FenceFrame = -1; // The frame whose copies read the slot
	bool InFlight = false;
};

class StagingRing
{
public:
	explicit StagingRing(size_t slotCount)
		: m_Slots(slotCount)
	{
	}

	// Polled once per frame: frees every slot whose frame the GPU has finished.
	void BeginFrame(int64_t completedFrame)
	{
		for (Slot& slot : m_Slots)
			if (slot.InFlight && slot.FenceFrame <= completedFrame)
				slot.InFlight = false;
	}

	// Takes a free slot for this frame's copy, or fails: the caller waits for a later frame instead of blocking.
	bool Acquire(int64_t frame)
	{
		for (Slot& slot : m_Slots)
		{
			if (!slot.InFlight)
			{
				slot.InFlight = true;
				slot.FenceFrame = frame;
				return true;
			}
		}
		return false;
	}

private:
	std::vector<Slot> m_Slots;
};

int main()
{
	constexpr uint64_t c_SlotBytes = 4ull << 20;
	constexpr int64_t c_GPULag = 3; // The GPU finishes a frame this many frames after the CPU recorded it
	StagingRing ring(2);
	uint64_t remaining = 20ull << 20;

	for (int64_t frame = 0; remaining > 0; frame++)
	{
		ring.BeginFrame(frame - c_GPULag);
		const uint64_t step = remaining < c_SlotBytes ? remaining : c_SlotBytes;
		if (ring.Acquire(frame))
		{
			remaining -= step;
			std::printf("frame %lld: copied %llu KiB, %llu KiB left\n", static_cast<long long>(frame),
				static_cast<unsigned long long>(step >> 10), static_cast<unsigned long long>(remaining >> 10));
		}
		else
		{
			std::printf("frame %lld: no free slot, nothing copied\n", static_cast<long long>(frame));
		}
	}
	return 0;
}
