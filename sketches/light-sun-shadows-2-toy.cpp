#include <cmath>
#include <cstdio>

namespace
{
	constexpr double c_TexelSize = 0.001;   // Metres per shadow map texel
	constexpr double c_RoofHeight = 2.0;    // Metres from the roof's edge down to the ground
	constexpr double c_SunRadius = 0.265;   // Degrees: half of the sun's 0.53 degrees across
	constexpr double c_SearchRadius = 0.03; // Metres around the receiver where blockers are searched
	constexpr int c_Taps = 16;
	constexpr double c_Pi = 3.14159265358979323846;

	double TanSunRadius()
	{
		return std::tan(c_SunRadius * c_Pi / 180.0);
	}

	// The shadow map of a roof over everything left of x = 0: the height of the surface nearest the sun, per texel.
	double MapHeight(double x)
	{
		const double centre = (std::floor(x / c_TexelSize) + 0.5) * c_TexelSize;
		return centre < 0.0 ? c_RoofHeight : 0.0;
	}

	// The share of the sun's disk that reaches a ground point: taps spread over the disk's width, each weighted by the chord there.
	double Filter(double x, double radius, int taps)
	{
		double lit = 0.0;
		double total = 0.0;
		for (int tap = 0; tap < taps; tap++)
		{
			const double u = 2.0 * (tap + 0.5) / taps - 1.0;
			const double weight = std::sqrt(1.0 - u * u);
			total += weight;
			if (MapHeight(x + u * radius) <= 0.0)
				lit += weight;
		}
		return lit / total;
	}

	double Hard(double x)
	{
		return MapHeight(x) <= 0.0 ? 1.0 : 0.0;
	}

	// PCSS: find the blockers' mean height, turn it into a disk radius, filter with that disk.
	double Pcss(double x)
	{
		double sum = 0.0;
		int count = 0;
		for (double offset = -c_SearchRadius; offset <= c_SearchRadius; offset += c_TexelSize)
		{
			const double height = MapHeight(x + offset);
			if (height > 0.0)
			{
				sum += height;
				count++;
			}
		}
		if (count == 0)
			return 1.0;
		return Filter(x, sum / count * TanSunRadius(), c_Taps);
	}

	// The metres between the 10 % and the 90 % lit points of a profile.
	double EdgeWidth(double (*profile)(double))
	{
		double low = 0.0;
		double high = 0.0;
		for (double x = -0.05; x < 0.05; x += 0.00005)
		{
			if (low == 0.0 && profile(x) >= 0.1)
				low = x;
			if (high == 0.0 && profile(x) >= 0.9)
				high = x;
		}
		return high - low;
	}

	double Exact(double x)
	{
		return Filter(x, c_RoofHeight * TanSunRadius(), 4000);
	}
}

int main()
{
	std::printf("x (mm)  hard  pcss  exact\n");
	for (int millimetres = -12; millimetres <= 12; millimetres += 3)
	{
		const double x = millimetres * 0.001;
		std::printf("%6d  %4.2f  %4.2f  %5.2f\n", millimetres, Hard(x), Pcss(x), Exact(x));
	}
	std::printf("10-90 %% width: pcss %.1f mm, exact %.1f mm\n", EdgeWidth(Pcss) * 1000.0, EdgeWidth(Exact) * 1000.0);
	std::printf("1.374 s tan(a) = %.1f mm\n", 1.374 * c_RoofHeight * TanSunRadius() * 1000.0);
	return 0;
}
