#include <cstdio>
#include <vector>

int main()
{
	std::vector<int> ages(3, -1);
	int skipped = 0;
	for (int tick = 0; tick < 100; tick++)
	{
		int spare = -1;
		for (int i = 0; i < 3; i++)
		{
			if (ages[i] >= 0 && ++ages[i] >= 4)
				ages[i] = -1;
			if (ages[i] < 0 && spare < 0)
				spare = i;
		}
		if (spare < 0)
			skipped++;
		else
			ages[spare] = 0;
	}
	std::printf("fired %d, skipped %d, made %zu\n", 100 - skipped, skipped, ages.size());
}
