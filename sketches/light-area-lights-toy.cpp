#include <glm/glm.hpp>

#include <algorithm>
#include <array>
#include <cmath>
#include <cstdio>

constexpr double c_Pi = 3.14159265358979;
constexpr double c_LobeHalfMaximum = 1.2871885;
constexpr double c_MinRoughness = 0.045;

double DistributionGGX(double NoH, double alpha)
{
	const double alpha2 = alpha * alpha;
	const double f = (NoH * alpha2 - NoH) * NoH + 1.0;
	return alpha2 / (c_Pi * f * f);
}

// The alpha^2 a sphere of `radius` at `distance` adds to a highlight's lobe (as PBR.slang's GetSourceLobeAlpha2).
double GetSourceAlpha2(double radius, double distance)
{
	const double sine2 = std::min(radius * radius / (distance * distance), 0.5);
	const double minAlpha2 = std::pow(c_MinRoughness, 4.0);
	return std::max(sine2 / ((1.0 - sine2) * c_LobeHalfMaximum * c_LobeHalfMaximum) - minAlpha2, 0.0);
}

// What the lobe sends out: the sum of D (n.h) over the half vectors' hemisphere, which must stay 1.
double LobeEnergy(double alpha)
{
	constexpr int c_Steps = 200000;
	double sum = 0.0;
	for (int step = 0; step < c_Steps; step++)
	{
		const double theta = (step + 0.5) * (c_Pi * 0.5) / c_Steps;
		sum += DistributionGGX(std::cos(theta), alpha) * std::cos(theta) * std::sin(theta);
	}
	return sum * 2.0 * c_Pi * (c_Pi * 0.5) / c_Steps;
}

// The form factor of a rectangle above a receiver that faces up: each edge adds the angle it spans, along the normal of the
// plane through the edge and the receiver (the sum over the edges, divided by 2 pi).
double FormFactor(double halfWidth, double halfHeight, double height)
{
	const std::array<glm::dvec3, 4> corners = { glm::dvec3(-halfWidth, height, -halfHeight), glm::dvec3(halfWidth, height, -halfHeight),
		glm::dvec3(halfWidth, height, halfHeight), glm::dvec3(-halfWidth, height, halfHeight) };
	glm::dvec3 vectorFormFactor(0.0);
	for (size_t index = 0; index < corners.size(); index++)
	{
		const glm::dvec3 start = glm::normalize(corners[index]);
		const glm::dvec3 end = glm::normalize(corners[(index + 1) % corners.size()]);
		vectorFormFactor += std::acos(glm::dot(start, end)) * glm::normalize(glm::cross(start, end));
	}
	return std::abs(vectorFormFactor.y) / (2.0 * c_Pi);
}

int main()
{
	const double alpha = 0.03; // Wet ground, perceptual roughness 0.17
	for (const double radius : { 0.0, 0.05, 0.3 })
	{
		const double widened = std::sqrt(alpha * alpha + GetSourceAlpha2(radius, 1.0));
		std::printf("radius %.2f m at 1 m: alpha %.4f, peak D %.1f, energy %.4f\n", radius, widened, DistributionGGX(1.0, widened), LobeEnergy(widened));
	}
	const double luminance = 25.0, area = 1.0 * 0.5;
	for (const double height : { 4.0, 1.0, 0.25 })
	{
		const double exact = c_Pi * luminance * FormFactor(0.5, 0.25, height);
		const double point = luminance * area / (height * height);
		std::printf("height %.2f m: panel %.2f lux, point light of its intensity %.2f lux\n", height, exact, point);
	}
	return 0;
}
