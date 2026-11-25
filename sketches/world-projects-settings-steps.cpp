// The fixed steps one slow frame runs at each project rate, and what the cap drops: the accumulator loop alone.
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>

// The most steps one update runs: the steps of 2/15 s at the rate, from 1 to 64.
uint32_t GetMaxSteps(uint32_t stepsPerSecond)
{
	const uint32_t steps = (stepsPerSecond * 2 + 14) / 15;
	return std::clamp(steps, 1u, 64u);
}

void RunFrame(uint32_t stepsPerSecond, float frameSeconds)
{
	const float step = 1.0f / static_cast<float>(stepsPerSecond);
	const uint32_t maxSteps = GetMaxSteps(stepsPerSecond);
	float accumulator = frameSeconds;
	uint32_t steps = 0;
	while (accumulator >= step && steps < maxSteps)
	{
		accumulator -= step;
		steps++;
	}
	uint32_t dropped = 0;
	if (steps == maxSteps && accumulator > step)
	{
		dropped = static_cast<uint32_t>(std::floor((accumulator - step) / step));
		accumulator = step;
	}
	std::printf("%3u steps/s: cap %2u, ran %2u, dropped %2u, carried %.1f ms\n", stepsPerSecond, maxSteps, steps, dropped,
		accumulator * 1000.0f);
}

int main()
{
	for (const uint32_t rate : { 30u, 60u, 120u, 240u })
		RunFrame(rate, 0.19f);
	return 0;
}
