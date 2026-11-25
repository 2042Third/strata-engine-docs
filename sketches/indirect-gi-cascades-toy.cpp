#include <cmath>
#include <cstdio>
#include <initializer_list>

// Two radiance cascades in a flat world. Probes stand on the line y = 0 and look at the half plane above it, where a lamp
// (a disc) glows and a wall absorbs. A direction is an angle from 0 to pi.
constexpr double c_Pi = 3.14159265358979323846;
constexpr double c_LampX = 4.0, c_LampY = 12.0, c_LampRadius = 3.0, c_LampRadiance = 10.0;
constexpr double c_WallX = 2.2, c_WallBottom = 2.0;
constexpr int c_ChildDirections = 8;   // Cascade 0: probes 1 m apart, the interval [0, 1)
constexpr int c_ParentDirections = 32; // Cascade 1: probes 2 m apart, four times the directions, the interval [1, far)
static double s_WallTop = 3.2;         // The wall stands from c_WallBottom to this height

struct Sample
{
	double Radiance = 0.0;
	double Transmittance = 1.0; // 0 when the ray ended on something
};

// The first thing a ray meets between two distances: the lamp lights it, the wall absorbs it.
Sample Trace(double originX, double angle, double start, double end)
{
	const double dx = std::cos(angle);
	const double dy = std::sin(angle);
	Sample result;
	const double ox = originX - c_LampX;
	const double oy = -c_LampY;
	const double b = ox * dx + oy * dy;
	const double discriminant = b * b - (ox * ox + oy * oy - c_LampRadius * c_LampRadius);
	if (discriminant >= 0.0)
	{
		const double t = -b - std::sqrt(discriminant);
		if (t >= start && t < end)
		{
			end = t;
			result = { c_LampRadiance, 0.0 };
		}
	}
	const double t = (c_WallX - originX) / dx;
	if (t >= start && t < end && t * dy >= c_WallBottom && t * dy <= s_WallTop)
		result = { 0.0, 0.0 };
	return result;
}

// What the cascades give for one of cascade 0's directions: its own short ray, then the merge of the parents' rays.
double Cascaded(double x, int direction)
{
	const Sample own = Trace(x, (direction + 0.5) * c_Pi / c_ChildDirections, 0.0, 1.0);
	const double coordinate = (x - 1.0) / 2.0; // The parents stand at 1, 3, 5 ... 2 m apart
	const int first = static_cast<int>(std::floor(coordinate));
	const double fraction = coordinate - first;
	double merged = 0.0;
	for (int corner = 0; corner < 2; corner++)
	{
		double mean = 0.0; // Four parent directions lie inside this one; each is the mean of four rays
		for (int k = 0; k < 16; k++)
		{
			const double angle = (direction * 4 + (k + 0.5) / 4.0) * c_Pi / c_ParentDirections;
			mean += Trace(1.0 + 2.0 * (first + corner), angle, 1.0, 1000.0).Radiance / 16.0;
		}
		merged += (corner == 0 ? 1.0 - fraction : fraction) * mean;
	}
	return own.Radiance + own.Transmittance * merged;
}

// The answer to compare with: many rays over the direction's whole range, each from the probe itself to the far end.
double BruteForce(double x, int direction)
{
	double sum = 0.0;
	for (int k = 0; k < 256; k++)
		sum += Trace(x, (direction + (k + 0.5) / 256.0) * c_Pi / c_ChildDirections, 0.0, 1000.0).Radiance;
	return sum / 256.0;
}

int main()
{
	for (const double top : { 2.0, 3.2 })
	{
		s_WallTop = top;
		std::printf("%s\n", top > c_WallBottom ? "with the wall" : "without the wall");
		for (const double x : { 1.5, 2.5 })
		{
			for (int direction = 0; direction < c_ChildDirections; direction++)
			{
				const double exact = BruteForce(x, direction);
				const double cascaded = Cascaded(x, direction);
				if (exact > 0.0 || cascaded > 0.0)
					std::printf("  probe x = %.1f, direction %d: brute force %.2f, cascades %.2f\n", x, direction, exact, cascaded);
			}
		}
	}
	return 0;
}
