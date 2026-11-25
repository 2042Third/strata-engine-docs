// The optical depth and transmittance of one ray from the ground to the top of Earth's air.
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdio>
#include <initializer_list>

constexpr double c_BottomRadius = 6360.0; // Kilometers
constexpr double c_TopRadius = 6460.0;
constexpr double c_RayleighScaleHeight = 8.0;
constexpr double c_MieScaleHeight = 1.2;
constexpr int c_Steps = 40;
constexpr double c_Pi = 3.14159265358979323846;

// Per kilometer at sea level, for red, green and blue.
constexpr std::array<double, 3> c_Rayleigh = { 5.802e-3, 13.558e-3, 33.1e-3 };
constexpr double c_MieExtinction = 3.996e-3 + 0.444e-3;

double ExtinctionAt(int channel, double height)
{
	const double air = c_Rayleigh[channel] * std::exp(-height / c_RayleighScaleHeight);
	const double aerosols = c_MieExtinction * std::exp(-height / c_MieScaleHeight);
	return air + aerosols;
}

// The distance from a point at `radius` along a ray of cosine `mu` with the zenith to the top of the air.
double DistanceToTop(double radius, double mu)
{
	const double discriminant = (c_TopRadius - radius) * (c_TopRadius + radius) + radius * radius * mu * mu;
	return -radius * mu + std::sqrt(discriminant);
}

double OpticalDepth(int channel, double radius, double mu)
{
	const double distance = DistanceToTop(radius, mu);
	const double step = distance / c_Steps;
	double depth = 0.0;
	for (int index = 0; index < c_Steps; index++)
	{
		const double t = (index + 0.5) * step;
		const double pointRadius = std::sqrt(radius * radius + t * t + 2.0 * radius * mu * t);
		depth += ExtinctionAt(channel, pointRadius - c_BottomRadius) * step;
	}
	return depth;
}

int main()
{
	std::printf("elevation  path km   red     green   blue\n");
	for (double elevation : { 90.0, 60.0, 20.0, 6.0, 1.0 })
	{
		const double mu = std::sin(elevation * c_Pi / 180.0);
		std::printf("%5.0f deg  %7.1f", elevation, DistanceToTop(c_BottomRadius, mu));
		for (int channel = 0; channel < 3; channel++)
			std::printf("  %.4f", std::exp(-OpticalDepth(channel, c_BottomRadius, mu)));
		std::printf("\n");
	}
	return 0;
}
