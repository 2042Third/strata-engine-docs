#include <cmath>
#include <cstdio>

// Two tone curves on a gray value x that the exposure already scaled: Reinhard, and a toy with a toe, a straight part
// and a shoulder in stops from middle gray, the shape of Strata's Filmic curve with simpler numbers.
constexpr float c_MiddleGray = 0.18f;

float Reinhard(float x)
{
	return x / (1.0f + x);
}

float ToyFilmic(float x)
{
	constexpr float c_Slope = 1.4f;      // log-log slope at middle gray
	constexpr float c_WhiteStops = 6.5f; // stops above middle gray where white is reached
	if (x <= 0.0f)
		return 0.0f;
	const float stops = std::log2(x / c_MiddleGray);
	if (stops >= c_WhiteStops)
		return 1.0f;
	if (stops < 0.0f)
		return c_MiddleGray * std::exp2(c_Slope * stops);
	const float power = c_Slope * c_MiddleGray * std::log(2.0f) * c_WhiteStops / (1.0f - c_MiddleGray);
	return c_MiddleGray + (1.0f - c_MiddleGray) * (1.0f - std::pow(1.0f - stops / c_WhiteStops, power));
}

int main()
{
	std::printf("stops   x      Reinhard  ToyFilmic\n");
	for (int stops = -4; stops <= 7; stops += 1)
	{
		const float x = c_MiddleGray * std::exp2(static_cast<float>(stops));
		std::printf("%+3d  %7.4f  %7.4f  %7.4f\n", stops, x, Reinhard(x), ToyFilmic(x));
	}
	return 0;
}
