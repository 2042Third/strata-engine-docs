// The 8-bit codes of a dark sky gradient: how many columns share each code, and the light each code means.
#include <cmath>
#include <cstdio>

float LinearToSRGB(float linear)
{
	return linear <= 0.0031308f ? linear * 12.92f : 1.055f * std::pow(linear, 1.0f / 2.4f) - 0.055f;
}

float SRGBToLinear(float encoded)
{
	return encoded <= 0.04045f ? encoded / 12.92f : std::pow((encoded + 0.055f) / 1.055f, 2.4f);
}

int main()
{
	constexpr int c_Width = 1920;
	int columns[256] = {};
	for (int x = 0; x < c_Width; x++)
	{
		// The light rises from 0.002 to 0.004 of white across the picture.
		const float linear = 0.002f + 0.002f * static_cast<float>(x) / static_cast<float>(c_Width - 1);
		const int code = static_cast<int>(std::lround(LinearToSRGB(linear) * 255.0f));
		columns[code]++;
	}
	for (int code = 0; code < 256; code++)
	{
		if (columns[code] > 0)
			std::printf("code %3d: %4d columns, light %.5f\n", code, columns[code], SRGBToLinear(static_cast<float>(code) / 255.0f));
	}
	return 0;
}
