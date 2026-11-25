#include <algorithm>
#include <cmath>
#include <cstdio>

constexpr double c_LobeHalfMaximum = 1.2871885;
constexpr double c_MinRoughness = 0.045;

// The alpha^2 a sphere of `radius` at `distance` adds to a highlight's lobe (as PBR.slang's GetSourceLobeAlpha2).
double GetSourceAlpha2(double radius, double distance)
{
	const double sine2 = std::min(radius * radius / (distance * distance), 0.5);
	const double minAlpha2 = std::pow(c_MinRoughness, 4.0);
	return std::max(sine2 / ((1.0 - sine2) * c_LobeHalfMaximum * c_LobeHalfMaximum) - minAlpha2, 0.0);
}

int main()
{
	const double mirrorAlpha = c_MinRoughness * c_MinRoughness;
	const double wetAlpha = 0.03;
	for (const double radius : { 0.04, 0.25 })
	{
		for (const double distance : { 1.0, 3.0, 10.0 })
		{
			const double added = GetSourceAlpha2(radius, distance);
			std::printf("radius %.2f m at %4.1f m: adds %.6f, mirror alpha %.4f, wet ground alpha %.4f\n", radius, distance, added,
				std::sqrt(mirrorAlpha * mirrorAlpha + added), std::sqrt(wetAlpha * wetAlpha + added));
		}
	}
	return 0;
}
