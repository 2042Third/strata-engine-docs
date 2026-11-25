// A reload with retries: a busy file is tried again 250 ms later, up to a limit of attempts.
#include <cstdio>
#include <vector>

int main()
{
	const int retryMs = 250;
	const int maxAttempts = 4;
	const std::vector<bool> fileBusy = { true, true, true, false }; // What each attempt finds

	int now = 0;
	int attempts = 0;
	while (true)
	{
		const bool busy = fileBusy[static_cast<size_t>(attempts)];
		std::printf("attempt %d at %d ms: %s\n", attempts + 1, now, busy ? "busy" : "loaded");
		if (!busy)
			break;
		if (++attempts >= maxAttempts)
		{
			std::printf("giving up\n");
			break;
		}
		now += retryMs;
	}
	return 0;
}
