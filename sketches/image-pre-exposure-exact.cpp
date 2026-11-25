#include <cstdint>
#include <cstdio>

// What the display sees of a luminance: stored at the pre-exposure, then divided out with the multiplier.
float Displayed(float luminance, float preExposure, float multiplier)
{
	const float stored = luminance * preExposure;
	return stored * (multiplier * (1.0f / preExposure));
}

int main()
{
	const float multiplier = 0.000013f;
	const float factors[] = { 8.0f, 16.0f, 10.0f };
	for (const float factor : factors)
	{
		uint32_t state = 12345;
		uint32_t different = 0;
		for (int sample = 0; sample < 100000; sample++)
		{
			state = state * 1664525u + 1013904223u;
			const float luminance = 0.01f + static_cast<float>(state >> 8) * 0.01f;
			different += Displayed(luminance, factor, multiplier) != Displayed(luminance, 1.0f, multiplier) ? 1u : 0u;
		}
		std::printf("pre-exposure %4.0f: %u of 100000 pixels differ from pre-exposure 1\n", factor, different);
	}
	return 0;
}
