// Inverse lerp, remapping and clamping.
#include <cstdio>
#include <glm/glm.hpp>

float InverseLerp(float a, float b, float value)
{
	return (value - a) / (b - a);
}

float Remap(float value, float inA, float inB, float outA, float outB)
{
	return glm::mix(outA, outB, InverseLerp(inA, inB, value));
}

int main()
{
	std::printf("weight of 25 in 10 to 30: %g\n", InverseLerp(10.0f, 30.0f, 25.0f));
	std::printf("25 from 10..30 to 0..200: %g\n", Remap(25.0f, 10.0f, 30.0f, 0.0f, 200.0f));
	const float weight = InverseLerp(10.0f, 30.0f, 35.0f);
	std::printf("weight of 35: %g, clamped: %g\n", weight, glm::clamp(weight, 0.0f, 1.0f));
	return 0;
}
