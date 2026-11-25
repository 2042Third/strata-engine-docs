// One edge pixel of a shrunken icon: opaque white beside fully transparent black, averaged three ways.
#include <cmath>
#include <cstdio>

struct Pixel
{
	double Red = 0.0; // 0 to 255, as stored (sRGB)
	double Alpha = 0.0; // 0 to 255
};

double ToLinear(double stored)
{
	const double value = stored / 255.0;
	return value <= 0.04045 ? value / 12.92 : std::pow((value + 0.055) / 1.055, 2.4);
}

double ToStored(double linear)
{
	const double value = linear <= 0.0031308 ? linear * 12.92 : 1.055 * std::pow(linear, 1.0 / 2.4) - 0.055;
	return value * 255.0;
}

int main()
{
	const Pixel left = { 255.0, 255.0 };
	const Pixel right = { 0.0, 0.0 };

	// Naive: average every channel as stored.
	std::printf("naive: red %.0f alpha %.0f\n", (left.Red + right.Red) / 2.0, (left.Alpha + right.Alpha) / 2.0);

	// Weighted by alpha: a transparent pixel has no say in the color.
	const double weight = left.Alpha + right.Alpha;
	const double weighted = (left.Red * left.Alpha + right.Red * right.Alpha) / weight;
	std::printf("weighted: red %.0f alpha %.0f\n", weighted, weight / 2.0);

	// Weighted and in linear light, the way the export does it.
	const double linear = (ToLinear(left.Red) * left.Alpha + ToLinear(right.Red) * right.Alpha) / weight;
	std::printf("linear and weighted: red %.0f alpha %.0f\n", ToStored(linear), weight / 2.0);

	// Two opaque pixels, black and white: the middle gray differs by the space.
	std::printf("black and white, stored average %.0f, linear average %.0f\n", 127.5, ToStored((ToLinear(255.0) + ToLinear(0.0)) / 2.0));
	return 0;
}
