#include <algorithm>
#include <cmath>
#include <cstdio>

namespace
{
	constexpr int c_Width = 32;
	constexpr int c_EdgeColumn = 16;

	// An ideal edge: black left of the edge column, white from it.
	float ReadColor(int pixel)
	{
		const int clamped = std::clamp(pixel, 0, c_Width - 1);
		return clamped >= c_EdgeColumn ? 1.0f : 0.0f;
	}

	// The blur of one pixel: the average of samples spread evenly along its own motion, centered on the pixel.
	float Blur(int pixel, float lengthPixels, int sampleCount)
	{
		const float radius = 0.5f * lengthPixels;
		float sum = 0.0f;
		for (int index = 0; index < sampleCount; index++)
		{
			const float position = -1.0f + (2.0f * static_cast<float>(index) + 1.0f) / static_cast<float>(sampleCount);
			const int samplePixel = static_cast<int>(std::floor(static_cast<float>(pixel) + 0.5f + position * radius));
			sum += ReadColor(samplePixel);
		}
		return sum / static_cast<float>(sampleCount);
	}
}

int main()
{
	const float lengthPixels = 12.0f;
	const int sampleCount = 8;
	for (int pixel = 9; pixel <= 22; pixel++)
		std::printf("pixel %2d: %.3f\n", pixel, Blur(pixel, lengthPixels, sampleCount));
	return 0;
}
