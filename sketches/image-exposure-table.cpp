#include <algorithm>
#include <cmath>
#include <cstdio>

// For a scene's average luminance in nits and the sun's illuminance in lux: the EV100 a meter reads, the manual
// Exposure that puts the average at middle gray, and the exposure key's stops for a key of 0.12.
int main()
{
	const float luminances[] = { 4096.0f, 1000.0f, 30.0f, 0.5f };
	const float sunLux = 100000.0f;
	const float cardNits = sunLux * 0.18f / 3.14159265f;
	const float cardEv100 = std::log2(cardNits) + 3.0f;
	for (float luminance : luminances)
	{
		float ev100 = std::log2(luminance) + 3.0f;
		float exposure = std::log2(0.18f / luminance);
		float key = std::clamp(0.12f * (ev100 - cardEv100), -2.0f, 0.0f);
		std::printf("%8.1f nits: EV100 %5.2f, Exposure %6.2f, key %5.2f\n", luminance, ev100, exposure, key);
	}
	return 0;
}
