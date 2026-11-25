#include <cstdio>

// A layer as the artist describes it: the color of the surface and how much of the pixel it covers.
struct Layer
{
	float R;
	float G;
	float B;
	float A;
};

// The same layer with its color already multiplied by its coverage.
struct Premultiplied
{
	float R;
	float G;
	float B;
	float A;
};

Premultiplied Premultiply(const Layer& layer)
{
	return { layer.R * layer.A, layer.G * layer.A, layer.B * layer.A, layer.A };
}

// What shows when `top` lies over `bottom`: all of the top, and the share of the bottom the top lets through.
Premultiplied Over(const Premultiplied& top, const Premultiplied& bottom)
{
	const float keep = 1.0f - top.A;
	return { top.R + bottom.R * keep, top.G + bottom.G * keep, top.B + bottom.B * keep, top.A + bottom.A * keep };
}

void Print(const char* label, const Premultiplied& value)
{
	std::printf("%-28s r %.3f  g %.3f  b %.3f  a %.3f\n", label, value.R, value.G, value.B, value.A);
}

int main()
{
	const Premultiplied white = Premultiply({ 1.0f, 1.0f, 1.0f, 1.0f });
	const Premultiplied red = Premultiply({ 1.0f, 0.0f, 0.0f, 0.5f });
	const Premultiplied blue = Premultiply({ 0.0f, 0.0f, 1.0f, 0.5f });

	// Drawing one layer at a time, as the transparent pass does: the order changes the result.
	Print("red, then blue, over white", Over(blue, Over(red, white)));
	Print("blue, then red, over white", Over(red, Over(blue, white)));

	// Premultiplied layers also combine first: blue over red, then the pair over white, gives the first line again.
	const Premultiplied pair = Over(blue, red);
	Print("the pair alone", pair);
	Print("the pair over white", Over(pair, white));

	// Strata's HDR alpha starts at 1 and each blended layer multiplies it by 1 - a: the share of the pixel left uncovered.
	float transmittance = 1.0f;
	transmittance *= 1.0f - 0.5f;
	transmittance *= 1.0f - 0.5f;
	std::printf("transmittance after two layers: %.3f\n", transmittance);
	return 0;
}
