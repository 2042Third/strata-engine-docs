#include <cmath>
#include <cstdio>

// Depth of a point z meters ahead of the camera, with a [0, 1] projection (near n, far f).
double StandardDepth(double z, double n, double f)
{
	return f * (z - n) / (z * (f - n));
}

double ReversedDepth(double z, double n, double f)
{
	return n * (f - z) / (z * (f - n));
}

// Meters between two neighbouring float depth values near z: the float spacing divided by the slope of depth.
double DistanceStep(double depth, double z, double n, double f)
{
	const float stored = static_cast<float>(depth);
	const double spacing = static_cast<double>(std::nextafter(stored, 2.0f)) - static_cast<double>(stored);
	const double slope = n * f / (z * z * (f - n));
	return spacing / slope;
}

int main()
{
	const double nearClip = 0.1;
	const double farClip = 10000.0;
	const double distances[] = { 0.2, 1.0, 10.0, 100.0, 1000.0, 9000.0 };

	std::printf("%8s %14s %14s\n", "z (m)", "standard (m)", "reversed (m)");
	for (const double z : distances)
	{
		const double standardStep = DistanceStep(StandardDepth(z, nearClip, farClip), z, nearClip, farClip);
		const double reversedStep = DistanceStep(ReversedDepth(z, nearClip, farClip), z, nearClip, farClip);
		std::printf("%8.1f %14.3g %14.3g\n", z, standardStep, reversedStep);
	}
	return 0;
}
