#include <array>
#include <cstdint>
#include <cstdio>

namespace
{
	constexpr uint32_t c_SlotCount = 3;
	constexpr uint32_t c_GPUFrames = 4; // Frames the pretend GPU needs to finish one copy

	struct Slot
	{
		bool Pending = false;
		uint32_t IssuedFrame = 0;
	};

	bool IsReady(const Slot& slot, uint32_t frame)
	{
		return frame >= slot.IssuedFrame + c_GPUFrames;
	}
}

int main()
{
	std::array<Slot, c_SlotCount> slots;
	uint32_t dropped = 0;
	for (uint32_t frame = 0; frame < 9; frame++)
	{
		// Poll: take what is ready, never wait for what is not.
		for (uint32_t index = 0; index < c_SlotCount; index++)
		{
			if (slots[index].Pending && IsReady(slots[index], frame))
			{
				std::printf("frame %u: slot %u holds the copy of frame %u\n", frame, index, slots[index].IssuedFrame);
				slots[index].Pending = false;
			}
		}

		// Issue: the first free slot, or drop this frame's request.
		bool issued = false;
		for (uint32_t index = 0; index < c_SlotCount && !issued; index++)
		{
			if (!slots[index].Pending)
			{
				slots[index] = { true, frame };
				issued = true;
			}
		}
		if (!issued)
		{
			dropped++;
			std::printf("frame %u: every slot is pending, request dropped\n", frame);
		}
	}
	std::printf("dropped %u\n", dropped);
}
