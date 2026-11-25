// Counts the bounces a closed room needs before its light is 90 % of the total, for walls of albedo 0.7.
#include <cstdio>

int main()
{
	const double albedo = 0.7;
	const double total = 1.0 / (1.0 - albedo); // 1 + 0.7 + 0.49 + ... without end, in units of the direct light
	double lightSoFar = 0.0;
	double lightOfBounce = 1.0; // The direct light is bounce 0
	int bounce = 0;
	while (lightSoFar / total < 0.9)
	{
		lightSoFar += lightOfBounce;
		std::printf("bounce %d: %.3f of the total\n", bounce, lightSoFar / total);
		lightOfBounce *= albedo;
		bounce++;
	}
	return 0;
}
