// A toy level chooser: by halving the screen fraction, and by the levels' relative errors.
#include <cstdint>
#include <cstdio>
#include <initializer_list>
#include <vector>

// Level 0 is full detail; level n is chosen below threshold / 2^(n-1).
uint32_t ChooseByHalving(float fraction, float threshold, uint32_t levelCount)
{
	if (levelCount <= 1 || !(fraction > 0.0f && fraction < threshold))
		return 0;
	uint32_t level = 1;
	float doubled = fraction * 2.0f;
	while (level + 1 < levelCount && doubled < threshold)
	{
		level++;
		doubled *= 2.0f;
	}
	return level;
}

// The coarsest level whose projected error stays within the threshold. Entry 0 is never read.
uint32_t ChooseByError(float fraction, const std::vector<float>& relativeErrors, float errorThreshold)
{
	if (relativeErrors.size() <= 1 || !(fraction > 0.0f))
		return 0;
	for (size_t level = relativeErrors.size() - 1; level > 0; level--)
	{
		if (fraction * relativeErrors[level] <= errorThreshold)
			return static_cast<uint32_t>(level);
	}
	return 0;
}

int main()
{
	const float viewportHeight = 1080.0f;
	const float errorPixels = 1.0f;
	const float errorThreshold = errorPixels / (viewportHeight * 0.5f);
	const std::vector<float> relativeErrors = { 0.0f, 0.01f, 0.04f, 0.16f };
	std::printf("error threshold %.6f\n", static_cast<double>(errorThreshold));
	for (float fraction : { 0.6f, 0.2f, 0.1f, 0.05f, 0.02f, 0.005f })
	{
		const uint32_t byHalving = ChooseByHalving(fraction, 0.5f, 4);
		const uint32_t byError = ChooseByError(fraction, relativeErrors, errorThreshold);
		std::printf("fraction %.3f: halving level %u, error level %u\n", static_cast<double>(fraction), byHalving, byError);
	}
	return 0;
}
