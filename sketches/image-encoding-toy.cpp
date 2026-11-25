// Three ways to store a value in whole codes: rounding, a rectangular dither and a triangular dither.
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <initializer_list>

uint32_t MixBits(uint32_t x)
{
	x ^= x >> 16u;
	x *= 0x7FEB352Du;
	x ^= x >> 15u;
	x *= 0x846CA68Bu;
	x ^= x >> 16u;
	return x;
}

// A value in [0, 1) that depends only on the pixel and the stream: the same pixel always gets the same noise.
float PixelRandom(uint32_t pixel, uint32_t stream)
{
	return static_cast<float>(MixBits(pixel ^ MixBits(stream)) >> 8u) / 16777216.0f;
}

int main()
{
	constexpr uint32_t c_Pixels = 200000;
	for (const float value : { 26.0f, 26.3f, 26.5f })
	{
		double sums[3] = {};
		double squares[3] = {};
		for (uint32_t pixel = 0; pixel < c_Pixels; pixel++)
		{
			const float u0 = PixelRandom(pixel, 0);
			const float u1 = PixelRandom(pixel, 1);
			const float rounded = std::floor(value + 0.5f);
			const float rectangular = std::floor(value + u0);
			const float triangular = std::floor(value + (u0 + u1 - 1.0f) + 0.5f);
			const float stored[3] = { rounded, rectangular, triangular };
			for (int method = 0; method < 3; method++)
			{
				const double error = static_cast<double>(stored[method] - value);
				sums[method] += error;
				squares[method] += error * error;
			}
		}
		std::printf("value %.1f\n", static_cast<double>(value));
		const char* names[3] = { "round", "rectangular", "triangular" };
		for (int method = 0; method < 3; method++)
		{
			const double mean = sums[method] / c_Pixels;
			const double power = squares[method] / c_Pixels;
			std::printf("  %-11s mean error %+.3f, noise power %.3f\n", names[method], mean, power - mean * mean);
		}
	}
	return 0;
}
