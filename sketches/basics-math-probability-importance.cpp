#include <cmath>
#include <cstdio>
#include <random>
void Report(bool weighted)
{
	const double halfPi = 1.5707963267948966;
	std::mt19937 generator(7);
	double sum = 0.0, squares = 0.0;
	for (int sample = 0; sample < 100000; sample++)
	{
		const double unit = generator() / 4294967296.0;
		const double x = weighted ? std::asin(unit) : halfPi * unit; // Density cos(x), or uniform
		const double f = std::cos(x) * (1.0 + 0.5 * std::sin(x));
		const double value = weighted ? f / std::cos(x) : halfPi * f; // Divide by the density
		sum += value;
		squares += value * value;
	}
	const double mean = sum / 100000;
	std::printf("%s: mean %.4f, spread %.4f\n", weighted ? "importance" : "uniform   ", mean, std::sqrt(squares / 100000 - mean * mean));
}
int main()
{
	Report(false);
	Report(true);
}
