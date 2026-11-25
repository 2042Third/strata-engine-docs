// Variance clipping in one dimension: a box around the mean of three neighbours; the history moves toward the mean until inside.
#include <algorithm>
#include <cmath>
#include <cstdio>

float ClipToVariance(float history, const float (&neighbours)[3], float width)
{
	float sum = 0.0f;
	float squares = 0.0f;
	float low = neighbours[0];
	float high = neighbours[0];
	for (const float value : neighbours)
	{
		sum += value;
		squares += value * value;
		low = std::min(low, value);
		high = std::max(high, value);
	}
	const float mean = sum / 3.0f;
	const float deviation = std::sqrt(std::max(squares / 3.0f - mean * mean, 0.0f));
	// The box is never wider than the plain range of the neighbours.
	const float boxLow = std::max(mean - width * deviation, low);
	const float boxHigh = std::min(mean + width * deviation, high);
	const float offset = history - mean;
	if (offset == 0.0f)
		return mean;
	const float limit = (offset > 0.0f ? boxHigh : boxLow) - mean;
	return mean + std::min(1.0f, limit / offset) * offset;
}

int main()
{
	const float smooth[3] = { 0.4f, 0.5f, 0.6f };
	const float glint[3] = { 0.0f, 0.0f, 1.0f };
	std::printf("smooth, history 0.55: %.3f\n", ClipToVariance(0.55f, smooth, 1.25f));
	std::printf("smooth, history 1.00: %.3f\n", ClipToVariance(1.0f, smooth, 1.25f));
	std::printf("smooth, history 0.00: %.3f\n", ClipToVariance(0.0f, smooth, 1.25f));
	std::printf("glint,  history 0.95: %.3f\n", ClipToVariance(0.95f, glint, 1.25f));
	std::printf("glint,  history 0.95, width 0.5: %.3f\n", ClipToVariance(0.95f, glint, 0.5f));
	return 0;
}
