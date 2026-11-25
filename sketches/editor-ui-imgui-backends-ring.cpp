#include <algorithm>
#include <cstdio>
#include <vector>

// The ring of buffer sets: a set is reused once the GPU finished the frame that drew from it.
struct BufferSet
{
	int DoneFrame = -1; // The frame at whose start the GPU is done with the set (-1: not pending)
	int LastUsed = 0;
};

static const size_t c_MaxSets = 8;

static void Run(int lag, int frameCount)
{
	std::vector<BufferSet> sets;
	int previous = -1; // The set the previous frame drew from
	int waits = 0;
	for (int frame = 0; frame < frameCount; frame++)
	{
		// The previous frame was submitted since: the GPU finishes it `lag` frames later.
		if (previous >= 0)
			sets[static_cast<size_t>(previous)].DoneFrame = frame - 1 + lag;

		int acquired = -1;
		for (size_t index = 0; index < sets.size() && acquired < 0; index++)
		{
			if (sets[index].DoneFrame < 0 || sets[index].DoneFrame <= frame)
				acquired = static_cast<int>(index);
		}
		if (acquired < 0 && sets.size() < c_MaxSets)
		{
			sets.emplace_back();
			acquired = static_cast<int>(sets.size()) - 1;
		}
		if (acquired < 0)
		{
			auto oldest = std::min_element(sets.begin(), sets.end(), [](const BufferSet& a, const BufferSet& b) { return a.LastUsed < b.LastUsed; });
			acquired = static_cast<int>(oldest - sets.begin());
			waits++;
		}
		sets[static_cast<size_t>(acquired)].DoneFrame = -1;
		sets[static_cast<size_t>(acquired)].LastUsed = frame;
		previous = acquired;
	}
	std::printf("GPU %d frames behind: %zu sets, %d waits in %d frames\n", lag, sets.size(), waits, frameCount);
}

int main()
{
	for (int lag : { 1, 2, 3, 12 })
		Run(lag, 40);
	return 0;
}
