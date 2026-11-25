// How much of a texel the sun's disk covers, from the angle between the texel's direction and the sun's center.
#include <algorithm>
#include <cmath>
#include <cstdio>

constexpr float c_Pi = 3.14159265f;

float Coverage(float radius, float angle, float texelAngle)
{
	return std::clamp((radius - angle) / texelAngle + 0.5f, 0.0f, 1.0f);
}

int main()
{
	const float radius = 0.53f * 0.5f * c_Pi / 180.0f;
	const float texelAngle = 2.0f / 512.0f;
	std::printf("texel %.3f degrees, disk radius %.3f degrees\n", texelAngle * 180.0f / c_Pi, radius * 180.0f / c_Pi);
	const float degrees[] = { 0.0f, 0.15f, 0.2f, 0.265f, 0.3f, 0.35f, 0.4f };
	for (const float angle : degrees)
		std::printf("angle %.3f degrees: coverage %.2f\n", angle, Coverage(radius, angle * c_Pi / 180.0f, texelAngle));
	return 0;
}
