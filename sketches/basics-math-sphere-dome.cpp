// Coins on a dome: a uniform polar angle bunches them at the top; a uniform cosine of it spreads them by area.
#include <cmath>
#include <cstdio>
#include <numbers>
#include <random>

int main()
{
	const float pi = std::numbers::pi_v<float>;
	const float maxPolar = 80.0f * pi / 180.0f;
	const float nearTop = 20.0f * pi / 180.0f;
	std::mt19937 random(11);
	std::uniform_real_distribution<float> unit(0.0f, 1.0f);
	int bunched = 0;
	int spread = 0;
	for (int coin = 0; coin < 10000; coin++)
	{
		const float uniformAngle = unit(random) * maxPolar;
		const float cosine = 1.0f - unit(random) * (1.0f - std::cos(maxPolar)); // uniform between cos(max) and 1
		bunched += uniformAngle < nearTop ? 1 : 0;
		spread += std::acos(cosine) < nearTop ? 1 : 0;
	}
	std::printf("within 20 degrees of the top, of 10000 coins: angle uniform %d, cosine uniform %d\n", bunched, spread);
	return 0;
}
