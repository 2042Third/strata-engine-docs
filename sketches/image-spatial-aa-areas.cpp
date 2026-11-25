#include <algorithm>
#include <cstdio>

// A Z run of the given length: its line is (x - length / 2) / length, from -0.5 at the first end to +0.5 at the last.
// The area below the edge (the line is negative) and above it (positive), inside the pixel from x = first to first + 1.
float Below(int first, float length)
{
	const float middle = 0.5f * length;
	const float low = static_cast<float>(first);
	const float high = std::min(low + 1.0f, middle);
	if (high <= low)
		return 0.0f;
	return ((middle - low) * (middle - low) - (middle - high) * (middle - high)) / (2.0f * length);
}

float Above(int first, float length)
{
	const float middle = 0.5f * length;
	const float low = std::max(static_cast<float>(first), middle);
	const float high = static_cast<float>(first) + 1.0f;
	if (high <= low)
		return 0.0f;
	return ((high - middle) * (high - middle) - (low - middle) * (low - middle)) / (2.0f * length);
}

int main()
{
	const int length = 7;
	for (int pixel = 0; pixel < length; pixel++)
		std::printf("pixel %d: below %.3f, above %.3f\n", pixel, Below(pixel, static_cast<float>(length)), Above(pixel, static_cast<float>(length)));
	return 0;
}
