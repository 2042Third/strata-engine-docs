// Counts the 36 ways two dice can fall and prints the chance of each sum.
#include <cstdio>

int main()
{
	int counts[13] = {};
	for (int first = 1; first <= 6; first++)
		for (int second = 1; second <= 6; second++)
			counts[first + second]++;
	for (int sum = 2; sum <= 12; sum++)
		std::printf("sum %2d: %d of 36, chance %.3f\n", sum, counts[sum], counts[sum] / 36.0);
	return 0;
}
