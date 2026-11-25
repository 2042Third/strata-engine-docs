#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <vector>

struct Summary
{
	double MedianMs = 0.0;
	double P95Ms = 0.0;
};

// The median, and the nearest-rank 95th percentile computed in integers so that no rounding moves it.
Summary Summarize(std::vector<double> samples)
{
	std::sort(samples.begin(), samples.end());
	const size_t count = samples.size();
	Summary summary;
	summary.MedianMs = count % 2 == 1 ? samples[count / 2] : (samples[count / 2 - 1] + samples[count / 2]) * 0.5;
	summary.P95Ms = samples[(count * 95 + 99) / 100 - 1];
	return summary;
}

// A pretend workload: 8 ms of work, noise from 0 to 1.5 ms that only ever adds, a cold first call and the time that
// other work on a busy machine takes.
double PretendCall(uint32_t& state, int call, double busyMs)
{
	state ^= state << 13;
	state ^= state >> 17;
	state ^= state << 5;
	const double noise = static_cast<double>(state % 1500) / 1000.0;
	return 8.0 + noise + (call == 0 ? 30.0 : 0.0) + busyMs;
}

// Calls the workload `warmup` times untimed, then `iterations` times, and summarizes the timed calls.
Summary Measure(uint32_t& state, double busyMs, int warmup, int iterations)
{
	std::vector<double> samples;
	for (int call = 0; call < warmup + iterations; call++)
	{
		const double milliseconds = PretendCall(state, call, busyMs);
		if (call >= warmup)
			samples.push_back(milliseconds);
	}
	return Summarize(samples);
}

int main()
{
	constexpr double c_BudgetMs = 12.0; // 1.5 times the 8 ms measured on the reference machine
	constexpr int c_Attempts = 3;
	const double busyMs[c_Attempts] = { 5.0, 5.0, 0.0 }; // The machine is busy for the first two attempts

	uint32_t state = 2463534242u;
	bool passed = false;
	for (int attempt = 1; attempt <= c_Attempts && !passed; attempt++)
	{
		const Summary summary = Measure(state, busyMs[attempt - 1], 1, 21);
		passed = summary.MedianMs <= c_BudgetMs;
		std::printf("attempt %d: median %.3f ms, p95 %.3f ms: %s\n", attempt, summary.MedianMs, summary.P95Ms,
			passed ? "within the budget" : "over the budget, measuring again");
	}
	std::puts(passed ? "the metric passed" : "the metric failed");
	return passed ? 0 : 1;
}
