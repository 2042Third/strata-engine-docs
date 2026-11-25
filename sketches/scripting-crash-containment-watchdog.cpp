// When does the watchdog report a call that never returns? It wakes at a fixed interval and reports at the first
// wake-up at or after the timeout. The interval is a quarter of the timeout, kept between 1 and 250 milliseconds.

#include <algorithm>
#include <chrono>
#include <cstdio>
#include <initializer_list>

int main()
{
	using std::chrono::milliseconds;

	std::printf("timeout  interval  first report\n");
	for (const int timeoutCount : { 4, 100, 250, 1000, 4000 })
	{
		const milliseconds timeout(timeoutCount);
		const milliseconds interval = std::clamp(timeout / 4, milliseconds(1), milliseconds(250));
		const int wakeUps = static_cast<int>((timeout + interval - milliseconds(1)) / interval);
		const milliseconds firstReport = wakeUps * interval;
		std::printf("%5d    %5d     %6d\n", timeoutCount, static_cast<int>(interval.count()), static_cast<int>(firstReport.count()));
	}
	return 0;
}
