#include <cstdio>

struct Slot
{
	int Capture = 0; // 0: empty
	unsigned LastUsed = 0;
};

// The slot holding `capture`, else an empty one, else the least recently used one that this gather has not used.
int AcquireSlot(Slot* slots, int count, int capture, unsigned gather)
{
	int replaceable = -1;
	for (int index = 0; index < count; index++)
	{
		if (slots[index].Capture == capture)
			return index;
		if (slots[index].LastUsed == gather)
			continue;
		if (replaceable < 0 || slots[index].Capture == 0 || (slots[replaceable].Capture != 0 && slots[index].LastUsed < slots[replaceable].LastUsed))
			replaceable = index;
	}
	slots[replaceable] = Slot { capture, 0 };
	return replaceable;
}

void Gather(Slot* slots, int count, const int* captures, int captureCount, unsigned gather)
{
	for (int index = 0; index < captureCount; index++)
		slots[AcquireSlot(slots, count, captures[index], gather)].LastUsed = gather;
	std::printf("gather %u:", gather);
	for (int index = 0; index < count; index++)
		std::printf(" [%d used %u]", slots[index].Capture, slots[index].LastUsed);
	std::printf("\n");
}

int main()
{
	Slot slots[3] = {};
	const int first[3] = { 11, 12, 13 };
	const int second[2] = { 11, 14 };
	const int third[3] = { 14, 15, 11 };
	Gather(slots, 3, first, 3, 1);
	Gather(slots, 3, second, 2, 2);
	Gather(slots, 3, third, 3, 3);
	return 0;
}
