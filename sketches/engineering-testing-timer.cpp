// A timer test written three ways, run on three machines. The clock is simulated so the output never varies.
#include <cstdio>

struct Machine
{
	const char* Name;
	int WorkMs;  // when the work under test finishes
	int FrameMs; // how long one frame takes
};

// Way 1: sleep 100 ms, then check.
static bool SleepThenCheck(const Machine& machine)
{
	const int now = 100;
	return now >= machine.WorkMs;
}

// Way 2: let five frames pass, then check.
static bool CountFrames(const Machine& machine)
{
	const int now = 5 * machine.FrameMs;
	return now >= machine.WorkMs;
}

// Way 3: poll every 5 ms until the work is done; the limit only ends a test that would hang.
static int WaitForCondition(const Machine& machine, int limitMs)
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
	};

	std::printf("%-9s %-6s %-7s %s\n", "Machine", "Sleep", "Frames", "Condition");
	for (const Machine& machine : machines)
	{
		const int waited = WaitForCondition(machine, 5000);
		std::printf("%-9s %-6s %-7s %s after %d ms\n", machine.Name, SleepThenCheck(machine) ? "pass" : "FAIL",
			CountFrames(machine) ? "pass" : "FAIL", waited >= 0 ? "pass" : "FAIL", waited);
	}
	return 0;
}
