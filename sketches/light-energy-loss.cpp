#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>

namespace
{

	constexpr double c_Pi = 3.14159265358979;

	// The table's two numbers: the scale and the bias of F0 for one view direction and roughness.
	struct Reflectance
	{
		double Scale;
		double Bias;
	};

	Reflectance IntegrateLobe(double nov, double roughness, uint32_t sampleCount)
	{
		const double alpha = roughness * roughness;
		const double viewX = std::sqrt(1.0 - nov * nov);
		double scale = 0.0;
		double bias = 0.0;
		for (uint32_t index = 0; index < sampleCount; index++)
		{
			double v = 0.0;
			double digit = 0.5;
			for (uint32_t bits = index; bits != 0; bits >>= 1, digit *= 0.5)
				v += (bits & 1u) ? digit : 0.0;
			const double phi = 2.0 * c_Pi * (static_cast<double>(index) / sampleCount);
			const double halfZ = std::sqrt((1.0 - v) / (1.0 + (alpha * alpha - 1.0) * v));
			const double voh = viewX * std::sqrt(1.0 - halfZ * halfZ) * std::cos(phi) + nov * halfZ;
			const double nol = 2.0 * voh * halfZ - nov;
			if (nol <= 0.0 || voh <= 0.0)
				continue;
			const double alpha2 = alpha * alpha;
			const double lambdaV = nol * std::sqrt((nov - nov * alpha2) * nov + alpha2);
			const double lambdaL = nov * std::sqrt((nol - nol * alpha2) * nol + alpha2);
			const double weight = 0.5 / std::max(lambdaV + lambdaL, 1e-5) * 4.0 * nol * voh / std::max(halfZ, 1e-4);
			const double fresnel = std::pow(1.0 - voh, 5.0);
			scale += (1.0 - fresnel) * weight;
			bias += fresnel * weight;
		}
		return { scale / sampleCount, bias / sampleCount };
	}

}

int main()
{
	const double f0 = 0.95; // The look-dev furnace's silver.
	for (const double roughness : { 0.0, 0.25, 0.5, 0.75, 1.0 })
	{
		const Reflectance table = IntegrateLobe(1.0, roughness, 512);
		const double albedo = table.Scale + table.Bias;
		const double single = f0 * table.Scale + table.Bias;
		const double factor = 1.0 + f0 * (1.0 / albedo - 1.0);
		std::printf("roughness %.2f  E %.4f  silver alone %.4f  factor %.3f  compensated %.4f\n", roughness, albedo, single, factor, single * factor);
	}
	return 0;
}
