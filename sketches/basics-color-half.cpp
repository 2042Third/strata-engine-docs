// What a half float keeps: a float rounded to 11 significant bits, with its range and its subnormal values.
#include <cmath>
#include <cstdio>

float RoundToHalf(float value)
{
	const float size = std::fabs(value);
	if (size >= 65520.0f) // halfway to the next step after 65504, which a half float does not have
		return value < 0.0f ? -INFINITY : INFINITY;
	if (size < 1.0f / 16384.0f) // below 2^-14 the step stays 2^-24, so fewer bits are kept
		return std::nearbyint(value * 16777216.0f) / 16777216.0f;
	int exponent = 0;
	std::frexp(value, &exponent); // value = m * 2^exponent with m from 0.5 up to 1
	const float scale = std::ldexp(1.0f, 11 - exponent); // 11 bits of m are kept
	return std::nearbyint(value * scale) / scale;
}

int main()
{
	const float values[] = { 1.0009766f, 1.0001f, 2049.0f, 3000.7f, 0.1f, 65504.0f, 70000.0f, 0.00006f, 0.00001f, 1e-8f };
	for (const float value : values)
		std::printf("%-10g is stored as %.8g\n", value, RoundToHalf(value));
	return 0;
}
