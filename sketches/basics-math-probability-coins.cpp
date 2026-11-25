// Makes 1,000 levels of 20 coins; each coin is gold with chance 0.25. Counts the gold coins over all seeds.
#include <cstdio>
#include <random>

int main()
{
	const int coinsPerLevel = 20;
	int gold = 0;
	for (int seed = 1; seed <= 1000; seed++)
	{
		std::mt19937 generator(seed);
		std::uniform_real_distribution<float> unit(0.0f, 1.0f);
		for (int coin = 0; coin < coinsPerLevel; coin++)
			if (unit(generator) < 0.25f)
				gold++;
	}
	std::printf("gold coins: %d, expected value %.0f\n", gold, 1000 * coinsPerLevel * 0.25);
	return 0;
}
