#include <algorithm>
#include <cmath>
#include <cstdio>
#include <vector>

// A CPU version of automatic exposure: a histogram of log2 luminance, a mean inside a percentile window,
// and one step of smoothing. The numbers match Strata's: 256 bins over log2 [-12, 16], bin 0 for black.
constexpr int c_Bins = 256;
constexpr float c_MinLog2 = -12.0f;
constexpr float c_MaxLog2 = 16.0f;

int LuminanceToBin(float luminance)
{
	if (!(luminance > std::exp2(c_MinLog2)))
		return 0;
	float t = std::clamp((std::log2(luminance) - c_MinLog2) / (c_MaxLog2 - c_MinLog2), 0.0f, 1.0f);
	return 1 + static_cast<int>(t * static_cast<float>(c_Bins - 2));
}

float BinToLog2(int bin)
{
	return c_MinLog2 + (static_cast<float>(bin - 1) + 0.5f) / static_cast<float>(c_Bins - 2) * (c_MaxLog2 - c_MinLog2);
}

// The mean log2 luminance of the pixels between the two percentiles, black ignored.
float MeterLog2(const std::vector<float>& luminances, float lowShare, float highShare)
{
	std::vector<float> bins(c_Bins, 0.0f);
	for (float luminance : luminances)
		bins[LuminanceToBin(luminance)] += 1.0f;

	float total = 0.0f;
	for (int bin = 1; bin < c_Bins; bin++)
		total += bins[bin];

	float low = total * lowShare;
	float high = total * highShare;
	float accumulated = 0.0f;
	float sum = 0.0f;
	float weight = 0.0f;
	for (int bin = 1; bin < c_Bins; bin++)
	{
		float inside = std::max(std::min(accumulated + bins[bin], high) - std::max(accumulated, low), 0.0f);
		sum += inside * BinToLog2(bin);
		weight += inside;
		accumulated += bins[bin];
	}
	return weight > 0.0f ? sum / weight : 0.0f;
}

// One frame of smoothing: the same fraction of the way, however long the frames are.
float Adapt(float previous, float target, float speed, float seconds)
{
	return previous + (target - previous) * (1.0f - std::exp(-seconds * speed));
}

int main()
{
	// 10 black pixels, 60 at 4 nits, 20 at 16 nits and 10 of a lamp at 4096 nits.
	std::vector<float> pixels(10, 0.0f);
	pixels.insert(pixels.end(), 60, 4.0f);
	pixels.insert(pixels.end(), 20, 16.0f);
	pixels.insert(pixels.end(), 10, 4096.0f);

	float everything = MeterLog2(pixels, 0.0f, 1.0f);
	float windowed = MeterLog2(pixels, 0.1f, 0.9f);
	std::printf("mean of all lit pixels: %.2f, multiplier %.4f\n", everything, 0.18f / std::exp2(everything));
	std::printf("mean inside the window: %.2f, multiplier %.4f\n", windowed, 0.18f / std::exp2(windowed));

	float oneStep = Adapt(0.0f, windowed, 3.0f, 0.1f);
	float tenSteps = 0.0f;
	for (int step = 0; step < 10; step++)
		tenSteps = Adapt(tenSteps, windowed, 3.0f, 0.01f);
	std::printf("one step of 0.1 s: %.3f, ten steps of 0.01 s: %.3f\n", oneStep, tenSteps);
	return 0;
}
