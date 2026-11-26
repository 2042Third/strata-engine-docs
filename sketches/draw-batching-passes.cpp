// How many passes a radix sort of 64-bit keys makes: one per byte in which some key differs from the first, and whether
// equal keys keep their order.
#include <cstdint>
#include <cstdio>
#include <vector>

namespace
{

	struct SortItem
	{
		uint64_t Key = 0;
		uint32_t Value = 0;
	};

	// Sorts the items and returns the number of passes it made.
	uint32_t RadixSort(std::vector<SortItem>& items)
	{
		uint64_t differing = 0;
		for (const SortItem& item : items)
			differing |= item.Key ^ items[0].Key;
		uint32_t passes = 0;
		for (uint32_t shift = 0; shift < 64; shift += 8)
		{
			if (((differing >> shift) & 0xFF) == 0)
				continue;
			passes++;
			uint32_t offsets[257] = {};
			for (const SortItem& item : items)
				offsets[((item.Key >> shift) & 0xFF) + 1]++;
			for (uint32_t digit = 0; digit < 256; digit++)
				offsets[digit + 1] += offsets[digit];
			std::vector<SortItem> sorted(items.size());
			for (const SortItem& item : items)
				sorted[offsets[(item.Key >> shift) & 0xFF]++] = item;
			items = sorted;
		}
		return passes;
	}

	// Every key twice: values 0 to 3 in falling key order, then 100 to 103 in rising order, so a sort that is not stable shows.
	void Report(const char* name, uint64_t (*makeKey)(uint32_t))
	{
		std::vector<SortItem> items;
		for (uint32_t index = 0; index < 4; index++)
			items.push_back(SortItem { makeKey(3 - index), index });
		for (uint32_t index = 0; index < 4; index++)
			items.push_back(SortItem { makeKey(index), 100 + index });
		const uint32_t passes = RadixSort(items);
		bool stable = true;
		for (size_t index = 1; index < items.size(); index++)
		{
			const bool ascending = items[index - 1].Key <= items[index].Key;
			const bool keepsOrder = items[index - 1].Key != items[index].Key || items[index - 1].Value < items[index].Value;
			stable = stable && ascending && keepsOrder;
		}
		std::printf("%s: %u passes, sorted and stable: %s\n", name, passes, stable ? "yes" : "no");
	}

}

int main()
{
	Report("low byte only", [](uint32_t i) { return static_cast<uint64_t>(0x1200 + i); });
	Report("bytes 0, 3 and 6", [](uint32_t i) { return static_cast<uint64_t>(i) | (static_cast<uint64_t>(i) << 24) | (static_cast<uint64_t>(i) << 48); });
	Report("all eight bytes", [](uint32_t i) -> uint64_t { return static_cast<uint64_t>(i) * 0x0101010101010101ull; });
	return 0;
}
