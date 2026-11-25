// A toy of the world cook's count: the most bodies one source can keep loaded at once, one row of cells.
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <vector>

// Cell i covers [i * cellSize, (i + 1) * cellSize] along X. A source streams the cells within `radius`.
uint64_t MostBodiesInRadius(const std::vector<uint64_t>& bodies, double cellSize, double radius)
{
	// The cook widens the radius: a source may stand anywhere in its cell, and sizes are guesses.
	const double reach = radius + std::max(cellSize * 0.5, 0.1 * radius);
	uint64_t most = 0;
	for (size_t centre = 0; centre < bodies.size(); centre++)
	{
		uint64_t sum = 0;
		for (size_t other = 0; other < bodies.size(); other++)
		{
			// The gap between two cells' edges: 0 for a cell and for its neighbours.
			const double steps = std::abs(static_cast<double>(other) - static_cast<double>(centre));
			const double gap = std::max(0.0, (steps - 1.0) * cellSize);
			if (gap <= reach)
				sum += bodies[other];
		}
		most = std::max(most, sum);
	}
	return most;
}

// 1.25 times the total, rounded up, in integers: a quarter of a number is exact in integer arithmetic.
uint64_t Recommended(uint64_t total)
{
	return total / 4 * 5 + (total % 4 * 5 + 3) / 4;
}

int main()
{
	const std::vector<uint64_t> bodies = { 10, 20, 40, 5, 0, 60 };
	const uint64_t persistent = 30;
	const uint64_t most = MostBodiesInRadius(bodies, 100.0, 100.0);
	std::printf("busiest place: %llu bodies\n", static_cast<unsigned long long>(most));
	for (uint64_t sources = 1; sources <= 2; sources++)
	{
		const uint64_t total = most * sources + persistent;
		std::printf("%llu source(s): total %llu, recommended %llu\n", static_cast<unsigned long long>(sources),
			static_cast<unsigned long long>(total), static_cast<unsigned long long>(Recommended(total)));
	}
	return 0;
}
