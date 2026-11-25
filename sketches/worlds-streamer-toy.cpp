#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <set>
#include <vector>

namespace
{

	constexpr int c_GridSize = 6;
	constexpr double c_CellSize = 32.0;
	constexpr size_t c_MaxLoads = 4;

	struct Source
	{
		double X = 0.0;
		double Z = 0.0;
		double ForwardX = 0.0;
		double ForwardZ = 1.0;
		double Radius = 0.0;
		double ViewBias = 0.25;
	};

	struct Candidate
	{
		uint64_t Key = 0;
		double Distance = 0.0; // View-biased
	};

	uint64_t Pack(int x, int z)
	{
		return (static_cast<uint64_t>(x) << 32) | static_cast<uint64_t>(z);
	}

	// Zero inside the cell's square, else the distance to its nearest point.
	double DistanceToCell(int x, int z, const Source& source)
	{
		const double dx = std::max({ x * c_CellSize - source.X, 0.0, source.X - (x + 1) * c_CellSize });
		const double dz = std::max({ z * c_CellSize - source.Z, 0.0, source.Z - (z + 1) * c_CellSize });
		return std::sqrt(dx * dx + dz * dz);
	}

	// One evaluation: unloads first, then at most c_MaxLoads loads, best first. A load finishes at once in this toy.
	void Evaluate(int frame, const Source& source, std::set<uint64_t>& loaded)
	{
		const double keepRadius = source.Radius + std::max(c_CellSize * 0.5, 0.1 * source.Radius);
		std::set<uint64_t> keep;
		std::vector<Candidate> candidates;
		for (int x = 0; x < c_GridSize; x++)
		{
			for (int z = 0; z < c_GridSize; z++)
			{
				const double distance = DistanceToCell(x, z, source);
				if (distance > keepRadius)
					continue;
				keep.insert(Pack(x, z));
				if (distance > source.Radius)
					continue;
				const double toX = (x + 0.5) * c_CellSize - source.X;
				const double toZ = (z + 0.5) * c_CellSize - source.Z;
				const double length = std::sqrt(toX * toX + toZ * toZ);
				const double ahead = length > 1e-6 ? std::max(0.0, (toX * source.ForwardX + toZ * source.ForwardZ) / length) : 0.0;
				candidates.push_back({ Pack(x, z), distance - source.ViewBias * source.Radius * ahead });
			}
		}

		std::printf("frame %d:", frame);
		for (auto it = loaded.begin(); it != loaded.end();)
		{
			if (keep.contains(*it))
			{
				++it;
				continue;
			}
			std::printf(" unload (%d,%d)", static_cast<int>(*it >> 32), static_cast<int>(*it & 0xFFFFFFFFu));
			it = loaded.erase(it);
		}
		std::sort(candidates.begin(), candidates.end(), [](const Candidate& a, const Candidate& b)
		{
			return a.Distance != b.Distance ? a.Distance < b.Distance : a.Key < b.Key;
		});
		size_t started = 0;
		for (const Candidate& candidate : candidates)
		{
			if (started == c_MaxLoads)
				break;
			if (!loaded.insert(candidate.Key).second)
				continue;
			std::printf(" load (%d,%d)", static_cast<int>(candidate.Key >> 32), static_cast<int>(candidate.Key & 0xFFFFFFFFu));
			started++;
		}
		std::printf("\n");
	}

}

int main()
{
	std::set<uint64_t> loaded;
	Source source;
	source.X = 16.0;
	source.Z = 16.0;
	source.Radius = 48.0;
	Evaluate(1, source, loaded);
	Evaluate(2, source, loaded);
	source.X = 6.0;
	Evaluate(3, source, loaded);
	source.X = -20.0;
	Evaluate(4, source, loaded);
	return 0;
}
