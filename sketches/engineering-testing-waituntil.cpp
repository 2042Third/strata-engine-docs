// Exercise solution: a frame-counting test rewritten to wait for its condition, with a limit.
#include <cstdio>

struct Machine
{
	const char* Name;
	int WorkMs;  // when the work under test finishes; a huge value is work that never finishes
	int FrameMs; // how long one frame takes
};

// Returns the milliseconds waited, or -1 when the limit passes first: the test then fails with a message.
static int WaitUntilDone(const Machine& machine, int limitMs)
{
	for (int now = 0; now <= limitMs; now += 5)
	{
		if (now >= machine.WorkMs)
			return now;
	}
	return -1;
}

int main()
{
	const Machine machines[] = {
		{ "Desktop", 30, 16 },
		{ "Busy", 150, 16 },
		{ "Headless", 30, 1 },
		{ "Hung", 1000000, 16 },
	};

	for (const Machine& machine : machines)
	{
		const int waited = WaitUntilDone(machine, 1000);
		if (waited >= 0)
			std::printf("%-9s pass after %d ms\n", machine.Name, waited);
		else
			std::printf("%-9s FAIL: not done within 1000 ms\n", machine.Name);
	}
	return 0;
}
