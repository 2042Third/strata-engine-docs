// What paces a frame, by the 90 % rule: the GPU rule first, then the CPU rule, otherwise capped.
#include <cstdio>

namespace
{
	struct Case
	{
		float WorkMs;
		float GPUBusyMs;
		float IntervalMs;
	};

	const char* Classify(const Case& frame)
	{
		const float bound = 0.9f * frame.IntervalMs;
		if (frame.GPUBusyMs >= bound && frame.GPUBusyMs > frame.WorkMs)
			return "GPU-bound";
		if (frame.WorkMs >= bound)
			return "CPU-bound";
		return "capped";
	}
}

int main()
{
	const Case cases[] = {
		{ 6.0f, 7.0f, 16.7f },
		{ 16.0f, 8.0f, 16.7f },
		{ 9.0f, 16.0f, 16.7f },
		{ 5.0f, 6.5f, 6.9f },
		{ 7.0f, 3.0f, 6.9f },
	};
	for (const Case& frame : cases)
		std::printf("work %4.1f, GPU %4.1f, interval %4.1f: %s\n", frame.WorkMs, frame.GPUBusyMs, frame.IntervalMs, Classify(frame));
	return 0;
}
