// How long a wait of six frames lasts, and how many frames a wait of 100 ms takes, at three frame rates.
#include <cstdio>

int main()
{
	const int rates[] = { 30, 60, 144 };
	for (const int rate : rates)
	{
		const double sixFramesMs = 6.0 * 1000.0 / rate;
		// Whole frames: the first poll at or after the deadline answers.
		const int framesFor100Ms = (100 * rate + 999) / 1000;
		std::printf("%3d frames per second: 6 frames last %5.1f ms; 100 ms take %2d frames\n", rate, sixFramesMs, framesFor100Ms);
	}
	return 0;
}
