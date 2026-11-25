// The sRGB transfer function, and a 50 % blend of black and white done on each kind of value.
#include <cmath>
#include <cstdio>

float Encode(float linear)
{
	return linear <= 0.0031308f ? linear * 12.92f : 1.055f * std::pow(linear, 1.0f / 2.4f) - 0.055f;
}

float Decode(float encoded)
{
	return encoded <= 0.04045f ? encoded / 12.92f : std::pow((encoded + 0.055f) / 1.055f, 2.4f);
}

int main()
{
	std::printf("light 0.18 is stored as %.4f, byte %.0f\n", Encode(0.18f), Encode(0.18f) * 255.0f);
	std::printf("light 0.001 is stored as %.5f, byte %.1f\n", Encode(0.001f), Encode(0.001f) * 255.0f);
	std::printf("black and white averaged on sRGB values: light %.4f\n", Decode(0.5f));
	std::printf("black and white averaged as light: stored %.4f, byte %.1f\n", Encode(0.5f), Encode(0.5f) * 255.0f);
	return 0;
}
