// A toy of the CPU path's batching: pack each draw's state into a key, sort stably by key, and turn runs of equal keys
// into batches. The draw list holds one entry (the draw's index) per instance, in batch order.
#include <cstdint>
#include <cstdio>
#include <vector>

namespace
{

	struct Draw
	{
		uint32_t Mesh = 0;
		uint32_t Material = 0;
	};

	struct SortItem
	{
		uint64_t Key = 0;
		uint32_t Value = 0;
	};

	struct Batch
	{
		uint32_t Mesh = 0;
		uint32_t FirstInstance = 0;
		uint32_t InstanceCount = 0;
	};

	// Mesh in the high bits; the material in the low 16 bits only when batches are split by material.
	uint64_t MakeKey(const Draw& draw, bool acrossMaterials)
	{
		return (static_cast<uint64_t>(draw.Mesh) << 16) | (acrossMaterials ? 0u : (draw.Material & 0xFFFFu));
	}

	// Least significant byte first, stable, and a byte equal in every key gets no pass.
	void RadixSort(std::vector<SortItem>& items)
	{
		uint64_t differing = 0;
		for (const SortItem& item : items)
			differing |= item.Key ^ items[0].Key;
		for (uint32_t shift = 0; shift < 64; shift += 8)
		{
			if (((differing >> shift) & 0xFF) == 0)
				continue;
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
	}

	void Run(const std::vector<Draw>& draws, bool acrossMaterials)
	{
		std::vector<SortItem> items;
		for (uint32_t index = 0; index < draws.size(); index++)
			items.push_back(SortItem { MakeKey(draws[index], acrossMaterials), index });
		RadixSort(items);

		std::vector<Batch> batches;
		std::vector<uint32_t> drawList;
		uint64_t batchKey = 0;
		for (const SortItem& item : items)
		{
			if (batches.empty() || item.Key != batchKey)
			{
				batchKey = item.Key;
				batches.push_back(Batch { draws[item.Value].Mesh, static_cast<uint32_t>(drawList.size()), 0 });
			}
			drawList.push_back(item.Value);
			batches.back().InstanceCount++;
		}

		std::printf("%s materials: %zu draws\n", acrossMaterials ? "across" : "split by", batches.size());
		for (const Batch& batch : batches)
			std::printf("  mesh %u: first instance %u, count %u\n", batch.Mesh, batch.FirstInstance, batch.InstanceCount);
		std::printf("  draw list:");
		for (const uint32_t entry : drawList)
			std::printf(" %u", entry);
		std::printf("\n");
	}

}

int main()
{
	const std::vector<Draw> draws = { { 2, 5 }, { 0, 1 }, { 2, 7 }, { 0, 1 }, { 1, 3 }, { 2, 5 }, { 0, 9 }, { 1, 3 } };
	Run(draws, true);
	Run(draws, false);
	return 0;
}
