// Throws random darts at the unit square; the share inside the quarter circle, times 4, estimates pi.
#include <cmath>
#include <cstdio>
#include <random>

int main()
{
	std::mt19937 generator(1);
	std::uniform_real_distribution<double> unit(0.0, 1.0);
	int inside = 0;
	for (int dart = 1; dart <= 1000000; dart++)
	{
		const double x = unit(generator);
		const double y = unit(generator);
		if (x * x + y * y < 1.0)
			inside++;
		if (dart == 100 || dart == 10000 || dart == 1000000)
		{
			const double estimate = 4.0 * inside / dart;
			std::printf("%8d darts: %.4f, error %.4f\n", dart, estimate, std::fabs(estimate - 3.14159265));
		}
	}
	return 0;
}
