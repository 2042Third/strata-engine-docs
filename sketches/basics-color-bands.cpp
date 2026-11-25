// How many of the 256 codes of a byte describe the shadows, up to 1 % of the light of white.
#include <cmath>
#include <cstdio>

float Decode(float encoded)
{
	return encoded <= 0.04045f ? encoded / 12.92f : std::pow((encoded + 0.055f) / 1.055f, 2.4f);
}

int main()
{
	int linearCodes = 0;
	int srgbCodes = 0;
	for (int code = 0; code < 256; code++)
	{
		const float value = static_cast<float>(code) / 255.0f;
		linearCodes += value <= 0.01f ? 1 : 0;       // the code means light in proportion
		srgbCodes += Decode(value) <= 0.01f ? 1 : 0; // the code means an sRGB value
	}
	std::printf("linear: %d codes, sRGB: %d codes\n", linearCodes, srgbCodes);
	return 0;
}
