// A motion history in miniature: a shared buffer of eight instance slots, a log of what was written under each write
// version, and a renderer's own copy that takes only the slots written since the version it last saw.
#include <cstdint>
#include <cstdio>
#include <vector>

namespace
{

	struct Write
	{
		uint64_t Version;
		uint32_t Slot;
	};

	struct SharedBuffer
	{
		std::vector<float> Slots = std::vector<float>(8, 0.0f);
		std::vector<Write> Log;
		uint64_t Version = 0;

		void Set(uint32_t slot, float value)
		{
			Slots[slot] = value;
			Log.push_back({ ++Version, slot });
		}
	};

	struct History
	{
		std::vector<float> Copy = std::vector<float>(8, 0.0f);
		uint64_t Version = 0;

		uint32_t Update(const SharedBuffer& shared)
		{
			uint32_t copied = 0;
			for (const Write& write : shared.Log)
			{
				if (write.Version <= Version)
					continue;
				Copy[write.Slot] = shared.Slots[write.Slot];
				copied++;
			}
			Version = shared.Version;
			return copied;
		}
	};

}

int main()
{
	SharedBuffer shared;
	History historyA;
	History historyB;
	shared.Set(3, 1.0f);
	const uint32_t firstA = historyA.Update(shared);
	const uint32_t firstB = historyB.Update(shared);
	std::printf("frame 1: A copies %u, B copies %u\n", firstA, firstB);
	shared.Set(3, 2.0f);
	shared.Set(5, 7.0f);
	std::printf("frame 2: A copies %u\n", historyA.Update(shared));
	std::printf("frame 3: A copies %u\n", historyA.Update(shared));
	const uint32_t lateB = historyB.Update(shared);
	std::printf("frame 4: B copies %u, its slot 3 holds %.1f\n", lateB, historyB.Copy[3]);
	return 0;
}
