#include <cstdint>
#include <cstdio>
#include <vector>

constexpr uint32_t c_Records = 3;
constexpr uint32_t c_None = 0xFFFFFFFFu;

// A thing the scene could draw: its record names the mesh level and material it would use.
struct Proxy
{
	bool Inside;
	uint32_t Record;
};

struct Cull
{
	std::vector<uint32_t> Counts = std::vector<uint32_t>(c_Records, 0);
	std::vector<uint32_t> Offsets = std::vector<uint32_t>(c_Records, 0);
	std::vector<uint32_t> DrawList;
};

// Both passes call this. Counting adds one to the record's count; writing counts it down and uses the result as the
// place inside the record's range, so the count ends at zero.
void Emit(Cull& cull, bool writing, uint32_t proxy, uint32_t record)
{
	if (!writing)
	{
		cull.Counts[record]++;
		return;
	}
	cull.Counts[record]--;
	cull.DrawList[cull.Offsets[record] + cull.Counts[record]] = proxy;
}

// One "thread" per proxy: the same decision in both passes.
void CullProxy(Cull& cull, const std::vector<Proxy>& proxies, bool writing, uint32_t index)
{
	if (proxies[index].Inside)
		Emit(cull, writing, index, proxies[index].Record);
}

// The build step: a running total gives each record its range of the draw list.
void Build(Cull& cull)
{
	uint32_t total = 0;
	for (uint32_t record = 0; record < c_Records; record++)
	{
		cull.Offsets[record] = total;
		total += cull.Counts[record];
	}
	cull.DrawList.assign(total, c_None);
}

void Run(const std::vector<Proxy>& proxies, const std::vector<uint32_t>& order, const char* name)
{
	Cull cull;
	for (const uint32_t index : order)
		CullProxy(cull, proxies, false, index);
	Build(cull);
	std::printf("%s: counts %u %u %u, starts %u %u %u\n", name, cull.Counts[0], cull.Counts[1], cull.Counts[2],
		cull.Offsets[0], cull.Offsets[1], cull.Offsets[2]);
	for (const uint32_t index : order)
		CullProxy(cull, proxies, true, index);
	std::printf("%s: draw list", name);
	for (const uint32_t entry : cull.DrawList)
		std::printf(" %u", entry);
	std::printf("\n");
}

int main()
{
	const std::vector<Proxy> proxies = { { true, 2 }, { true, 0 }, { false, 1 }, { true, 2 }, { true, 0 },
		{ true, 1 }, { false, 0 }, { true, 2 }, { true, 0 }, { true, 1 } };
	Run(proxies, { 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 }, "forward");
	Run(proxies, { 9, 8, 7, 6, 5, 4, 3, 2, 1, 0 }, "backward");
	return 0;
}
