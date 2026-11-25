#include <cmath>
#include <cstdio>

namespace
{
	constexpr double c_Pi = 3.14159265358979323846;
	constexpr double c_MiddleGray = 0.18;

	// Lux that a source of the given candela makes on a surface that faces it, at the given distance in meters.
	double LuxFromCandela(double candela, double distance)
	{
		return candela / (distance * distance);
	}

	// Nits of a matte surface of the given albedo under the given lux.
	double NitsOfMatte(double albedo, double lux)
	{
		return albedo * lux / c_Pi;
	}

	// The manual exposure, in stops, that shows the given nits as middle gray.
	double ExposureFor(double nits)
	{
		return std::log2(c_MiddleGray / nits);
	}

	void Report(const char* name, double lux)
	{
		const double nits = NitsOfMatte(c_MiddleGray, lux);
		std::printf("%-8s %6.2f lux  %7.4f nits  exposure %6.2f\n", name, lux, nits, ExposureFor(nits));
	}
}

int main()
{
	Report("moon", 0.2);
	Report("lamp", LuxFromCandela(64.0, 2.0));
	Report("candle", LuxFromCandela(1.0, 0.5));
	return 0;
}
