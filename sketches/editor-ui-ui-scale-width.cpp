// A button width of eight font heights, cut to whole pixels, at three UI scales.
#include <cmath>
#include <cstdio>
#include <initializer_list>

float ScaledWidth(float fontSize, float scale)
{
	return std::trunc(8.0f * fontSize * scale);
}

int main()
{
	for (const float scale : { 1.0f, 1.5f, 2.0f })
		std::printf("Scale %.1f: width %.0f\n", scale, ScaledWidth(16.0f, scale));
}
