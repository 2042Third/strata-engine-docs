#include <cmath>
#include <cstdio>

// A CPU-twin check in miniature: the Filmic curve of one channel with Strata's fitted constants, and the three
// things a test can compare it with, the middle-gray value, the slope there and the white point.
constexpr float c_MiddleGray = 0.18f;
constexpr float c_Contrast = 1.39788385f;
constexpr float c_ToeWidth = 3.0f;

float Curve(float x, float toeSlope, float whiteStops, float shoulderPower)
{
	if (x <= 0.0f)
		return 0.0f;
	const float t = std::log2(x / c_MiddleGray);
	if (t < 0.0f)
		return c_MiddleGray * std::exp2(toeSlope * t + (c_Contrast - toeSlope) * c_ToeWidth * (std::exp(t / c_ToeWidth) - 1.0f));
	if (t >= whiteStops)
		return 1.0f;
	return c_MiddleGray + (1.0f - c_MiddleGray) * (1.0f - std::pow(1.0f - t / whiteStops, shoulderPower));
}

int main()
{
	const float toe = 0.5f;
	const float shoulder = 0.5f;
	const float toeSlope = c_Contrast * (0.85f + 0.5f * toe);
	const float whiteStops = 6.5f + 3.0f * (shoulder - 0.5f);
	const float power = c_Contrast * c_MiddleGray * std::log(2.0f) * whiteStops / (1.0f - c_MiddleGray);

	const float step = 1e-3f;
	const float above = std::log2(Curve(c_MiddleGray * std::exp2(step), toeSlope, whiteStops, power));
	const float below = std::log2(Curve(c_MiddleGray * std::exp2(-step), toeSlope, whiteStops, power));
	std::printf("middle gray -> %.5f\n", Curve(c_MiddleGray, toeSlope, whiteStops, power));
	std::printf("slope at middle gray %.4f (contrast %.4f)\n", (above - below) / (2.0f * step), c_Contrast);
	std::printf("white at %.1f stops -> %.1f\n", whiteStops, Curve(c_MiddleGray * std::exp2(whiteStops), toeSlope, whiteStops, power));
	return 0;
}
