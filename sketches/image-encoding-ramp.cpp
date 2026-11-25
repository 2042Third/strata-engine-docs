// The largest error of a band's mean code in a dark gradient, when the gradient is rounded and when it is dithered.
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>

uint32_t MixBits(uint32_t x)
{
	x ^= x >> 16u;
	x *= 0x7FEB352Du;
	x ^= x >> 15u;
	x *= 0x846CA68Bu;
	x ^= x >> 16u;
	return x;
}

float PixelRandom(uint32_t pixel, uint32_t stream)
{
	return static_cast<float>(MixBits(pixel ^ MixBits(stream)) >> 8u) / 16777216.0f;
}

float LinearToSRGB(float linear)
{
	return linear <= 0.0031308f ? linear * 12.92f : 1.055f * std::pow(linear, 1.0f / 2.4f) - 0.055f;
}

int main()
{
	constexpr uint32_t c_Width = 1920;
	constexpr uint32_t c_Rows = 16;
	constexpr uint32_t c_Block = 32;
	double largestRounded = 0.0;
	double largestDithered = 0.0;
	for (uint32_t start = 0; start < c_Width; start += c_Block)
	{
		double exactSum = 0.0;
		double roundedSum = 0.0;
		double ditheredSum = 0.0;
		for (uint32_t y = 0; y < c_Rows; y++)
		{
			for (uint32_t x = start; x < start + c_Block; x++)
			{
				const float linear = 0.002f + 0.002f * static_cast<float>(x) / static_cast<float>(c_Width - 1);
				const float value = LinearToSRGB(linear) * 255.0f;
				const uint32_t pixel = y * c_Width + x;
				const float noise = PixelRandom(pixel, 0) + PixelRandom(pixel, 1) - 1.0f;
				exactSum += static_cast<double>(value);
				roundedSum += static_cast<double>(std::floor(value + 0.5f));
				ditheredSum += static_cast<double>(std::floor(value + noise + 0.5f));
			}
		}
		const double count = static_cast<double>(c_Rows * c_Block);
		largestRounded = std::max(largestRounded, std::abs(roundedSum - exactSum) / count);
		largestDithered = std::max(largestDithered, std::abs(ditheredSum - exactSum) / count);
	}
	std::printf("largest band error in codes: rounded %.3f, dithered %.3f\n", largestRounded, largestDithered);
	return 0;
}
