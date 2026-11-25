#include <cmath>
#include <cstdio>

namespace
{

	constexpr double c_Pi = 3.14159265358979;

	// GGX's D for the cosine of the angle between the normal and the half vector.
	double DistributionGGX(double cosine, double alpha)
	{
		const double alpha2 = alpha * alpha;
		const double f = cosine * cosine * (alpha2 - 1.0) + 1.0;
		return alpha2 / (c_Pi * f * f);
	}

}

int main()
{
	const double roughnesses[] = { 0.2, 0.6 };
	const int steps = 2000000;
	for (double roughness : roughnesses)
	{
		const double alpha = roughness * roughness;
		double sum = 0.0;
		for (int step = 0; step < steps; step++)
		{
			const double cosine = (step + 0.5) / steps;
			sum += DistributionGGX(cosine, alpha) * cosine;
		}
		// The area element of the hemisphere is dw = dcos * dphi, so the sum over cos is times 2 pi.
		std::printf("roughness %.1f  alpha %.2f  peak %.1f  integral %.4f\n", roughness, alpha, DistributionGGX(1.0, alpha), 2.0 * c_Pi * sum / steps);
	}
	return 0;
}
