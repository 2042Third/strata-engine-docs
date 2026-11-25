#include <algorithm>
#include <cstdio>

namespace
{

	constexpr double c_CellSize = 32.0;
	constexpr double c_Radius = 40.0;

	// Counts the loads and unloads of the cell that spans x from 96 to 128 for a source that jitters at its border.
	int CountDecisions(double hysteresis)
	{
		bool loaded = false;
		int decisions = 0;
		for (int frame = 0; frame < 100; frame++)
		{
			const double x = frame % 2 == 0 ? 55.99 : 56.01;
			const double distance = std::max(3.0 * c_CellSize - x, 0.0);
			if (!loaded && distance <= c_Radius)
			{
				loaded = true;
				decisions++;
			}
			else if (loaded && distance > c_Radius + hysteresis)
			{
				loaded = false;
				decisions++;
			}
		}
		return decisions;
	}

}

int main()
{
	std::printf("decisions with no keep ring: %d\n", CountDecisions(0.0));
	std::printf("decisions with a keep ring of 16 m: %d\n", CountDecisions(std::max(c_CellSize * 0.5, 0.1 * c_Radius)));
	return 0;
}
