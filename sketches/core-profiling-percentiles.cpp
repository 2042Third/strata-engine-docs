// Mean, P50, P95 and maximum of frame times by nearest rank, and what paces the frames.
#include <algorithm>
#include <cstdio>
#include <vector>

namespace
{
	// The sample at rank ceil(percent * count / 100), counting from 1 at the smallest (whole numbers: no rounding error).
	float AtRank(const std::vector<float>& sorted, size_t percent)
	{
		const size_t rank = (sorted.size() * percent + 99) / 100;
		return sorted[std::max<size_t>(rank, 1) - 1];
	}
}

int main()
{
	// Twenty frames of a game on a 60 Hz display, in milliseconds.
	std::vector<float> frames(20, 16.0f);
	frames[3] = 17.0f;
	frames[8] = 17.0f;
	frames[11] = 50.0f;
	frames[15] = 50.0f;

	float sum = 0.0f;
	for (const float frame : frames)
		sum += frame;
	std::sort(frames.begin(), frames.end());

	const float p50 = AtRank(frames, 50);
	const float p95 = AtRank(frames, 95);
	std::printf("mean %.1f ms, P50 %.1f ms, P95 %.1f ms, max %.1f ms\n", sum / 20.0f, p50, p95, frames.back());

	// The classification of the medians: work 15.5 ms, GPU busy 6.0 ms, interval 16.7 ms.
	const float work = 15.5f;
	const float gpu = 6.0f;
	const float interval = 16.7f;
	const bool gpuBound = gpu >= 0.9f * interval && gpu > work;
	const bool cpuBound = work >= 0.9f * interval;
	std::printf("bound at %.2f ms: %s\n", 0.9f * interval, gpuBound ? "GPU" : (cpuBound ? "CPU" : "Capped"));
	return 0;
}
