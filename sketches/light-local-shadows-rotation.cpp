#include <cmath>
#include <cstdio>

float Fraction(float value)
{
	return value - std::floor(value);
}

// The angle of the filter's rotation at a pixel, as LocalShadowSampleRotation works it out, in degrees.
float GetFixedAngle(float x, float y)
{
	return 360.0f * Fraction(52.9829189f * Fraction(x * 0.06711056f + y * 0.00583715f));
}

// An invented rule that also turns by the frame: a pattern like this needs temporal anti-aliasing to average it.
float GetTurningAngle(float x, float y, int frame)
{
	return std::fmod(GetFixedAngle(x, y) + 137.5f * static_cast<float>(frame), 360.0f);
}

int main()
{
	for (int frame = 0; frame < 4; frame++)
		std::printf("frame %d: fixed %.1f, turning %.1f\n", frame, GetFixedAngle(3.0f, 5.0f), GetTurningAngle(3.0f, 5.0f, frame));
	std::printf("neighbours: %.1f %.1f %.1f\n", GetFixedAngle(3.0f, 5.0f), GetFixedAngle(4.0f, 5.0f), GetFixedAngle(3.0f, 6.0f));
	return 0;
}
