// Samples a 1 Hz and a 9 Hz sine at 10 samples a second: the 9 Hz samples are the 1 Hz ones turned upside down.
#include <cmath>
#include <cstdio>
#include <numbers>

int main()
{
	const double sampleRate = 10.0;
	const double twoPi = 2.0 * std::numbers::pi;
	for (int n = 0; n <= 4; n++)
	{
		const double t = n / sampleRate;
		std::printf("n = %d   1 Hz: %6.3f   9 Hz: %6.3f\n", n, std::sin(twoPi * 1.0 * t), std::sin(twoPi * 9.0 * t));
	}
}
