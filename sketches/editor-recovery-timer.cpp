// The journal's write timer: an edit every second from 1 s to 22 s, time counted in tenths of a second.
#include <cstdio>

constexpr int c_QuietTicks = 20;
constexpr int c_MaxIntervalTicks = 100;

int main()
{
	int lastChange = 0;
	int lastWrite = 0;
	bool changed = false;
	for (int now = 0; now <= 300; now++)
	{
		if (now % 10 == 0 && now >= 10 && now <= 220)
		{
			changed = true;
			lastChange = now;
		}
		if (changed && (now - lastChange >= c_QuietTicks || now - lastWrite >= c_MaxIntervalTicks))
		{
			std::printf("write at %d.%d s\n", now / 10, now % 10);
			changed = false;
			lastWrite = now;
		}
	}
}
