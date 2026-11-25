#include <algorithm>
#include <cmath>
#include <cstdio>

struct Layer
{
	double Density;
	double Falloff;
	double BaseHeight;
};

// One layer's optical depth in closed form, the shader's way: the lowest point's density times a mean in (0, 1].
double LayerDepth(const Layer& layer, double startHeight, double rise, double distance)
{
	const double lowest = startHeight - layer.BaseHeight + std::min(rise, 0.0);
	const double y = layer.Falloff * std::abs(rise);
	const double mean = y > 1.0e-4 ? (1.0 - std::exp(-y)) / y : 1.0 - 0.5 * y;
	return layer.Density * distance * std::exp(-layer.Falloff * lowest) * mean;
}

// Extinctions add, so optical depths add: the layers are summed.
double TotalDepth(const Layer* layers, int count, double startHeight, double rise, double distance)
{
	double depth = 0.0;
	for (int index = 0; index < count; index++)
		depth += LayerDepth(layers[index], startHeight, rise, distance);
	return depth;
}

double NumericDepth(const Layer* layers, int count, double startHeight, double rise, double distance)
{
	const int steps = 200000;
	double depth = 0.0;
	for (int step = 0; step < steps; step++)
	{
		const double height = startHeight + rise * (step + 0.5) / steps;
		for (int index = 0; index < count; index++)
			depth += layers[index].Density * std::exp(-layers[index].Falloff * (height - layers[index].BaseHeight)) * distance / steps;
	}
	return depth;
}

int main()
{
	const Layer layers[] = { { 0.02, 0.2, 0.0 }, { 0.004, 0.02, 0.0 } };
	const double rises[] = { 0.0, 30.0, -12.0 };
	for (double rise : rises)
	{
		const double closed = TotalDepth(layers, 2, 2.0, rise, 60.0);
		const double numeric = NumericDepth(layers, 2, 2.0, rise, 60.0);
		std::printf("rise %5.1f m: closed %.5f, numeric %.5f, agree %s\n", rise, closed, numeric, std::abs(closed - numeric) < 1.0e-5 ? "yes" : "no");
	}
	return 0;
}
