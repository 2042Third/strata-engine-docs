#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <vector>

struct Change
{
	uint64_t Version;
	uint32_t Proxy;
};

// Returns false when the reader is below the floor and must read everything.
bool Follow(const std::vector<Change>& log, uint64_t floor, uint64_t since, std::vector<uint32_t>& out)
{
	if (since < floor)
		return false;
	for (const Change& change : log)
	{
		if (change.Version > since)
			out.push_back(change.Proxy);
	}
	std::sort(out.begin(), out.end());
	out.erase(std::unique(out.begin(), out.end()), out.end());
	return true;
}

int main()
{
	const std::vector<Change> log = { { 8, 3 }, { 9, 5 }, { 10, 3 }, { 11, 7 } };
	for (const uint64_t since : { 7ull, 9ull, 11ull, 4ull })
	{
		std::vector<uint32_t> proxies;
		if (Follow(log, 5, since, proxies))
			std::printf("since %llu: %zu proxies\n", static_cast<unsigned long long>(since), proxies.size());
		else
			std::printf("since %llu: read everything\n", static_cast<unsigned long long>(since));
	}
}
