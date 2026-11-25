#include <cstdio>
#include <vector>

struct Entry
{
	bool IsMain = false;
	int Megabytes = 0;
	int LastUsed = 0;
};

static int PushWhereMainIsEvicted(bool deleteOldEntries)
{
	const int limit = 10240;
	const int setSize = 1377;
	std::vector<Entry> cache = { { true, setSize, 0 } };
	for (int push = 1; push <= 50; push++)
	{
		// Restore: the newest entry of the branch, else main's. Either counts as used now.
		Entry* newest = &cache.back();
		newest->LastUsed = push;
		cache.push_back({ false, setSize, push });
		if (deleteOldEntries)
		{
			// Keep only main's entry and the one just saved.
			std::vector<Entry> kept;
			for (const Entry& entry : cache)
				if (entry.IsMain || entry.LastUsed == push)
					kept.push_back(entry);
			cache = kept;
		}
		int total = 0;
		for (const Entry& entry : cache)
			total += entry.Megabytes;
		while (total > limit)
		{
			size_t oldest = 0;
			for (size_t i = 1; i < cache.size(); i++)
				if (cache[i].LastUsed < cache[oldest].LastUsed)
					oldest = i;
			if (cache[oldest].IsMain)
				return push;
			total -= cache[oldest].Megabytes;
			cache.erase(cache.begin() + static_cast<long>(oldest));
		}
	}
	return 0;
}

int main()
{
	std::printf("without cleanup: main is evicted at push %d\n", PushWhereMainIsEvicted(false));
	std::printf("with cleanup: main is evicted at push %d (0 means never)\n", PushWhereMainIsEvicted(true));
	return 0;
}
