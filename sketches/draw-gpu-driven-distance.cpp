#include <cstdint>
#include <cstdio>
#include <vector>

constexpr uint32_t c_Records = 2;

struct Proxy
{
	float Distance;
	uint32_t Record;
};

// The CPU's rule: a simple loop that counts what each record draws.
std::vector<uint32_t> CountOnCPU(const std::vector<Proxy>& proxies, float maxDistance)
{
	std::vector<uint32_t> counts(c_Records, 0);
	for (const Proxy& proxy : proxies)
	{
		if (proxy.Distance <= maxDistance)
			counts[proxy.Record]++;
	}
	return counts;
}

// The GPU's twin: the same rule, written again where the other code cannot see it, as one thread per proxy.
void CullProxy(std::vector<uint32_t>& counts, const Proxy& proxy, float maxDistance)
{
	if (proxy.Distance > maxDistance)
		return;
	counts[proxy.Record]++; // InterlockedAdd on the GPU
}

int main()
{
	const std::vector<Proxy> proxies = { { 5.0f, 0 }, { 40.0f, 1 }, { 120.0f, 0 }, { 80.0f, 1 }, { 100.0f, 0 } };
	for (const float maxDistance : { 1000.0f, 100.0f, 10.0f })
	{
		const std::vector<uint32_t> cpu = CountOnCPU(proxies, maxDistance);
		std::vector<uint32_t> gpu(c_Records, 0);
		for (const Proxy& proxy : proxies)
			CullProxy(gpu, proxy, maxDistance);
		std::printf("max %.0f: cpu %u %u, gpu %u %u, %s\n", maxDistance, cpu[0], cpu[1], gpu[0], gpu[1],
			cpu == gpu ? "agree" : "DIFFER");
	}
	return 0;
}
