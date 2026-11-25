// The null device's clock: how many frames to mix for each frame of the game, with the remainder carried over.
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <vector>

constexpr uint64_t c_ChunkFrames = 1024;
constexpr double c_MaxAdvance = 1.0;
constexpr double c_SampleRate = 48000.0;

// Returns the sizes of the chunks to mix for this call.
std::vector<uint64_t> Advance(double seconds, double& pending)
{
	std::vector<uint64_t> chunks;
	pending += std::min(seconds, c_MaxAdvance) * c_SampleRate;
	uint64_t frames = static_cast<uint64_t>(pending);
	pending -= static_cast<double>(frames);
	while (frames > 0)
	{
		const uint64_t chunk = std::min(frames, c_ChunkFrames);
		chunks.push_back(chunk);
		frames -= chunk;
	}
	return chunks;
}

int main()
{
	double pending = 0.0;
	for (double seconds : { 0.0167, 0.0167, 0.030, 5.0 })
	{
		const std::vector<uint64_t> chunks = Advance(seconds, pending);
		uint64_t total = 0;
		for (uint64_t chunk : chunks)
			total += chunk;
		std::printf("%.4f s: %zu chunks, %llu frames, carry %.2f\n", seconds, chunks.size(), static_cast<unsigned long long>(total), pending);
	}
	return 0;
}
