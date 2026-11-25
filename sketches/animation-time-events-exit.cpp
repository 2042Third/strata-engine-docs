// The exit test alone: does the update that moved the normalized time from previous to current reach the exit time?
#include <cmath>
#include <cstdio>

static bool ExitReached(bool looping, double exitTime, double previous, double current)
{
	if (looping && exitTime < 1.0)
		return std::floor(current - exitTime) > std::floor(previous - exitTime);
	return current >= exitTime;
}

int main()
{
	const double exitTime = 0.5;
	const double step = 0.375; // a binary fraction, so the sums are exact
	double previous = 0.0;
	for (int update = 1; update <= 6; update++)
	{
		const double current = previous + step;
		std::printf("update %d: normalized %.3f looping %d not looping %d\n", update, current, ExitReached(true, exitTime, previous, current) ? 1 : 0,
			ExitReached(false, exitTime, previous, current) ? 1 : 0);
		previous = current;
	}
	return 0;
}
