#include <glm/glm.hpp>

#include <algorithm>
#include <cmath>
#include <cstdio>

constexpr float c_Pi = 3.14159265f;

float DistributionGGX(float NoH, float alpha)
{
	const float alpha2 = alpha * alpha;
	const float f = (NoH * alpha2 - NoH) * NoH + 1.0f;
	return alpha2 / (c_Pi * f * f);
}

glm::vec3 NormalAt(float tilt)
{
	return glm::vec3(std::sin(tilt), 0.0f, std::cos(tilt));
}

// The highlight of one pixel. The light and the eye look straight down, so the half vector is +Z and NoH is the normal's Z.
float ShadePixel(float tilt, float tiltStep, float alpha, bool widen)
{
	const glm::vec3 normal = NormalAt(tilt);
	if (widen)
	{
		const glm::vec3 changeX = NormalAt(tilt + tiltStep) - normal;
		const float variance = 0.25f * glm::dot(changeX, changeX);
		alpha = std::sqrt(alpha * alpha + std::min(2.0f * variance, 0.18f));
	}
	return DistributionGGX(normal.z, alpha);
}

int main()
{
	const float alpha = 0.05f;
	const float tiltStep = 0.1f;
	for (const bool widen : { false, true })
	{
		for (const float shift : { 0.05f, 0.0f })
		{
			std::printf("%s, surface shifted by %.2f:", widen ? "widened" : "plain  ", shift);
			float peak = 0.0f;
			for (int pixel = 0; pixel < 5; pixel++)
			{
				const float value = ShadePixel(static_cast<float>(pixel - 2) * tiltStep + shift, tiltStep, alpha, widen);
				std::printf(" %6.2f", value);
				peak = std::max(peak, value);
			}
			std::printf("  peak %6.2f\n", peak);
		}
	}
	return 0;
}
