// How many times AnimationReach::Compute samples a clip: 15 a second, the start and end included, 2 to 48.
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <initializer_list>

constexpr float c_SamplesPerSecond = 15.0f;
constexpr uint32_t c_MaxSamples = 48;

uint32_t SampleCount(float duration)
{
	if (duration <= 0.0f)
		return 1;
	return std::clamp(static_cast<uint32_t>(std::ceil(duration * c_SamplesPerSecond)) + 1u, 2u, c_MaxSamples);
}

int main()
{
	for (const float duration : { 0.0f, 0.05f, 0.5f, 1.0f, 2.0f, 3.1f, 4.0f })
		std::printf("clip of %.2f s: %2u samples\n", duration, SampleCount(duration));
}
