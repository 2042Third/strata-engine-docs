#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>

namespace
{

	constexpr double c_Pi = 3.14159265358979;

	// The second coordinate of the Hammersley pattern: the bits of the index mirrored behind the binary point.
	double RadicalInverse(uint32_t index)
	{
		double result = 0.0;
		double digit = 0.5;
		for (uint32_t bits = index; bits != 0; bits >>= 1)
		{
			if (bits & 1u)
				result += digit;
			digit *= 0.5;
		}
		return result;
	}

	// Height-correlated Smith visibility, the same formula the forward shader uses.
	double Visibility(double nov, double nol, double alpha)
	{
		const double alpha2 = alpha * alpha;
		const double lambdaV = nol * std::sqrt((nov - nov * alpha2) * nov + alpha2);
		const double lambdaL = nov * std::sqrt((nol - nol * alpha2) * nol + alpha2);
		return 0.5 / std::max(lambdaV + lambdaL, 1e-5);
	}

	// The share of the light that a GGX lobe of F0 = 1 reflects for one view direction: its directional albedo E.
	double DirectionalAlbedo(double nov, double roughness, uint32_t sampleCount)
	{
		const double alpha = roughness * roughness;
		const double viewX = std::sqrt(1.0 - nov * nov); // The view lies in the x-z plane, the normal is z.
		double sum = 0.0;
		for (uint32_t index = 0; index < sampleCount; index++)
		{
			const double phi = 2.0 * c_Pi * (static_cast<double>(index) / sampleCount);
			const double v = RadicalInverse(index);
			const double halfZ = std::sqrt((1.0 - v) / (1.0 + (alpha * alpha - 1.0) * v));
			const double halfX = std::sqrt(1.0 - halfZ * halfZ) * std::cos(phi);
			const double voh = viewX * halfX + nov * halfZ;
			const double nol = 2.0 * voh * halfZ - nov; // The light is the view mirrored about the half vector.
			if (nol <= 0.0 || voh <= 0.0)
				continue;
			// BRDF * NoL / pdf, where pdf = D * NoH / (4 VoH): the distribution D cancels.
			sum += Visibility(nov, nol, alpha) * 4.0 * nol * voh / std::max(halfZ, 1e-4);
		}
		return sum / sampleCount;
	}

}

int main()
{
	for (const double nov : { 1.0, 0.5, 0.1 })
		for (const double roughness : { 0.1, 0.5, 1.0 })
		{
			const double albedo = DirectionalAlbedo(nov, roughness, 512);
			std::printf("NoV %.1f  roughness %.1f  E %.4f  1/E %.3f\n", nov, roughness, albedo, 1.0 / albedo);
		}
	return 0;
}
