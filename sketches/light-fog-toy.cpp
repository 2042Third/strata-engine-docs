#include <algorithm>
#include <cmath>
#include <cstdio>

struct Fog
{
	double Density = 0.02;
	double Falloff = 0.2;
};

// Adds up the extinction of many short pieces of the ray.
double NumericDepth(const Fog& fog, double startHeight, double rise, double distance)
{
	const int steps = 100000;
	double depth = 0.0;
	for (int step = 0; step < steps; step++)
	{
		const double fraction = (step + 0.5) / steps;
		const double height = startHeight + rise * fraction;
		depth += fog.Density * std::exp(-fog.Falloff * height) * distance / steps;
	}
	return depth;
}

// The same integral in closed form, written like the shader: the density at the lowest point
// times the distance times a mean in (0, 1], so no exponent grows.
double ClosedDepth(const Fog& fog, double startHeight, double rise, double distance)
{
	const double lowest = startHeight + std::min(rise, 0.0);
	const double y = fog.Falloff * std::abs(rise);
	const double mean = y > 1.0e-4 ? (1.0 - std::exp(-y)) / y : 1.0 - 0.5 * y;
	return fog.Density * distance * std::exp(-fog.Falloff * lowest) * mean;
}

double Phase(double g, double cosTheta)
{
	const double denominator = 1.0 + g * g - 2.0 * g * cosTheta;
	return (1.0 - g * g) / (4.0 * 3.14159265358979 * denominator * std::sqrt(denominator));
}

int main()
{
	const Fog fog;
	const double distance = 20.0;
	const double rises[] = { 0.0, 10.0, -10.0 };
	for (double rise : rises)
	{
		const double numeric = NumericDepth(fog, 2.0, rise, distance);
		const double closed = ClosedDepth(fog, 2.0, rise, distance);
		std::printf("rise %5.1f m: numeric %.5f, closed %.5f, opacity %.4f\n", rise, numeric, closed, 1.0 - std::exp(-closed));
	}
	const double toSky = fog.Density * std::exp(-fog.Falloff * 2.0) / (fog.Falloff * 0.5);
	std::printf("sky above 30 degrees: depth %.5f, opacity %.4f\n", toSky, 1.0 - std::exp(-toSky));
	std::printf("phase, SunScattering 0.5: toward %.4f, away %.4f\n", Phase(0.45, 1.0), Phase(0.45, -1.0));
	return 0;
}
