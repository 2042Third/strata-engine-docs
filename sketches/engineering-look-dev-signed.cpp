// The signed difference image of single grey values: red where brighter, blue where darker.
#include <algorithm>
#include <cstdio>

int main()
{
	const float gain = 32.0f;
	const int deltas[] = { 6, -6, 10, 0 };
	for (int delta : deltas)
	{
		int red = delta > 0 ? std::min(255, static_cast<int>(delta * gain + 0.5f)) : 0;
		int blue = delta < 0 ? std::min(255, static_cast<int>(-delta * gain + 0.5f)) : 0;
		std::printf("delta %d: red %d, blue %d\n", delta, red, blue);
	}
	return 0;
}
