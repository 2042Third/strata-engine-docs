// Flags base colors whose linear luminance lies outside the range of real materials.
#include <cmath>
#include <cstdint>
#include <cstdio>

struct Paint
{
	const char* Name;
	uint8_t Red;
	uint8_t Green;
	uint8_t Blue;
};

constexpr float c_AlbedoLow = 0.03f;
constexpr float c_AlbedoHigh = 0.85f;

// The sRGB byte of a painted color, as linear light.
float ToLinear(uint8_t byte)
{
	const float encoded = static_cast<float>(byte) / 255.0f;
	if (encoded <= 0.04045f)
		return encoded / 12.92f;
	return std::pow((encoded + 0.055f) / 1.055f, 2.4f);
}

int main()
{
	const Paint paints[] = {
		{ "Pure white", 255, 255, 255 },
		{ "Fresh snow", 240, 240, 240 },
		{ "Concrete", 128, 128, 128 },
		{ "Red brick", 150, 70, 60 },
		{ "Charcoal", 50, 50, 50 },
		{ "Pure black", 0, 0, 0 },
	};
	for (const Paint& paint : paints)
	{
		const float luminance = 0.2126f * ToLinear(paint.Red) + 0.7152f * ToLinear(paint.Green) + 0.0722f * ToLinear(paint.Blue);
		const char* verdict = "ok";
		if (luminance < c_AlbedoLow)
			verdict = "too dark";
		else if (luminance > c_AlbedoHigh)
			verdict = "too bright";
		std::printf("%-11s luminance %.3f  %s\n", paint.Name, luminance, verdict);
	}
	return 0;
}
