// Ranks two settings by the median, lowest and highest time over nine layouts, as one run cannot.
#include <algorithm>
#include <cstdio>
#include <vector>

// Prints the median, lowest and highest of a list of times in seconds.
static void Report(const char* name, std::vector<double> times)
{
	std::sort(times.begin(), times.end());
	std::printf("%s: median %.1f s, lowest %.1f s, highest %.1f s\n", name, times[times.size() / 2], times.front(), times.back());
}

int main()
{
	// Invented seconds to 99 % asleep, one entry per layout of the same pit.
	const std::vector<double> threshold008 = { 14.2, 19.8, 12.9, 16.1, 25.3, 13.7, 18.4, 15.0, 17.6 };
	const std::vector<double> threshold005 = { 17.0, 21.5, 16.8, 22.9, 19.4, 24.1, 18.8, 20.2, 26.6 };
	int lowerWins = 0;
	for (int layout = 0; layout < 9; layout++)
		lowerWins += threshold005[layout] < threshold008[layout] ? 1 : 0;
	std::printf("threshold 0.05 wins %d of 9 single runs\n", lowerWins);
	Report("threshold 0.08", threshold008);
	Report("threshold 0.05", threshold005);
	return 0;
}
