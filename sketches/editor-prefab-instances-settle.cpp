// A toy of PrefabSync::AreEditsContinuing: when is a mark worked out again during a run of edits?
#include <cstdint>
#include <cstdio>

constexpr uint64_t c_SettleFrames = 12;

struct EditClock
{
	uint64_t LastChangeFrame = 0;
	uint64_t PreviousChangeFrame = 0;

	void SeeChange(uint64_t frame)
	{
		PreviousChangeFrame = LastChangeFrame;
		LastChangeFrame = frame;
	}

	bool AreEditsContinuing(uint64_t frame) const
	{
		return PreviousChangeFrame != 0 && LastChangeFrame - PreviousChangeFrame < c_SettleFrames && frame - LastChangeFrame < c_SettleFrames;
	}
};

int main()
{
	EditClock clock;
	uint64_t changes = 0;
	uint64_t markChanges = 0;
	for (uint64_t frame = 1; frame <= 40; frame++)
	{
		if (frame >= 10 && frame <= 15)
		{
			changes++;
			clock.SeeChange(frame);
		}
		if (markChanges != changes && !clock.AreEditsContinuing(frame))
		{
			markChanges = changes;
			std::printf("frame %llu: the mark is worked out again\n", static_cast<unsigned long long>(frame));
		}
	}
	return 0;
}
