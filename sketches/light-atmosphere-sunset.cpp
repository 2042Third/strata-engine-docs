// The sun's transmittance at the ground as Strata computes it on the CPU: air, aerosols and ozone, and the disk's share.
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdio>

constexpr double c_BottomRadius = 6360.0; // Kilometers
constexpr double c_TopRadius = 6460.0;
constexpr int c_Steps = 40;
constexpr double c_Pi = 3.14159265358979323846;

constexpr std::array<double, 3> c_Rayleigh = { 5.802e-3, 13.558e-3, 33.1e-3 };
constexpr std::array<double, 3> c_Ozone = { 0.650e-3, 1.881e-3, 0.085e-3 };
constexpr double c_MieExtinction = 3.996e-3 + 0.444e-3;

double ExtinctionAt(int channel, double height)
{
	const double air = c_Rayleigh[channel] * std::exp(-height / 8.0);
	const double aerosols = c_MieExtinction * std::exp(-height / 1.2);
	const double ozone = c_Ozone[channel] * std::max(1.0 - std::abs(height - 25.0) / 15.0, 0.0);
	return air + aerosols + ozone;
}

double Transmittance(int channel, double mu)
{
	const double radius = c_BottomRadius;
	const double discriminant = (c_TopRadius - radius) * (c_TopRadius + radius) + radius * radius * mu * mu;
	const double step = (-radius * mu + std::sqrt(discriminant)) / c_Steps;
	double depth = 0.0;
	for (int index = 0; index < c_Steps; index++)
	{
		const double t = (index + 0.5) * step;
		const double pointRadius = std::sqrt(radius * radius + t * t + 2.0 * radius * mu * t);
		depth += ExtinctionAt(channel, pointRadius - c_BottomRadius) * step;
	}
	return std::exp(-depth);
}

int main()
{
	const double diskRadius = 0.53 * 0.5 * c_Pi / 180.0; // The default sun size, in radians
	for (double elevationDegrees : { 4.0, 0.0 })
	{
		const double elevation = elevationDegrees * c_Pi / 180.0;
		const double visible = std::clamp((elevation + diskRadius) / (2.0 * diskRadius), 0.0, 1.0);
		std::printf("sun at %.0f deg, %.2f of the disk above the horizon:", elevationDegrees, visible);
		for (int channel = 0; channel < 3; channel++)
			std::printf("  %.4f", Transmittance(channel, std::sin(elevation)) * visible);
		std::printf("\n");
	}
	return 0;
}
