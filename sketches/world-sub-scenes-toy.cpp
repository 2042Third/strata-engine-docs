// A toy of sliced loading: a level of 4,000 entities appears over several frames.
// A simulated clock replaces the real one, so the output is the same on every run.
#include <algorithm>
#include <cstddef>
#include <cstdio>

// What creating the entity with this number costs, in nanoseconds: the first ones are cold.
static double GetRealCost(size_t number)
{
	return number < 1000 ? 6000.0 : 1500.0;
}

// The entities that fit in the time left at the estimated cost, between two limits.
static size_t FitChunk(double remainingNs, double estimateNs, size_t smallest, size_t largest)
{
	if (remainingNs <= 0.0)
		return smallest;
	const double fitting = remainingNs / std::max(estimateNs, 1.0);
	if (fitting >= static_cast<double>(largest))
		return largest;
	return std::max(smallest, static_cast<size_t>(fitting));
}

// A dearer chunk raises the estimate at once; a cheaper one lowers it halfway.
static void RecordChunkCost(double& estimateNs, double elapsedNs, size_t entities)
{
	const double measured = elapsedNs / static_cast<double>(entities);
	estimateNs = std::max(measured, 0.5 * (estimateNs + measured));
}

int main()
{
	constexpr size_t c_Total = 4000;
	constexpr size_t c_MaxPerFrame = 5000;
	constexpr double c_FrameNs = 2'000'000.0;
	double estimateNs = 2000.0;
	size_t created = 0;
	for (int frame = 1; created < c_Total; frame++)
	{
		double spentNs = 0.0;
		size_t thisFrame = 0;
		while (created < c_Total && thisFrame < c_MaxPerFrame && spentNs < c_FrameNs)
		{
			// The first chunk of a frame is whole, so that every frame makes progress.
			size_t chunk = thisFrame == 0 ? 512 : FitChunk(c_FrameNs - spentNs, estimateNs, 32, 512);
			chunk = std::min({ chunk, c_Total - created, c_MaxPerFrame - thisFrame });
			double chunkNs = 0.0;
			for (size_t i = 0; i < chunk; i++)
				chunkNs += GetRealCost(created + i);
			RecordChunkCost(estimateNs, chunkNs, chunk);
			spentNs += chunkNs;
			thisFrame += chunk;
			created += chunk;
		}
		std::printf("frame %d: %zu entities in %.2f ms, estimate %.0f ns\n", frame, thisFrame, spentNs / 1e6, estimateNs);
	}
	return 0;
}
