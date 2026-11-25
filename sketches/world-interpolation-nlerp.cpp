// How far a normalized lerp strays from a slerp: the largest gap over every weight, for a few turns per step.
#include <glm/glm.hpp>
#include <glm/gtc/quaternion.hpp>

#include <algorithm>
#include <cmath>
#include <cstdio>

double AngleBetween(const glm::dquat& a, const glm::dquat& b)
{
	const double cosine = std::min(std::abs(glm::dot(a, b)), 1.0);
	return glm::degrees(2.0 * std::acos(cosine));
}

int main()
{
	const glm::dvec3 axis(0.0, 1.0, 0.0);
	for (const double degrees : { 10.0, 30.0, 90.0, 170.0 })
	{
		const glm::dquat from(1.0, 0.0, 0.0, 0.0);
		const glm::dquat to = glm::angleAxis(glm::radians(degrees), axis);
		double worst = 0.0;
		for (int index = 0; index <= 100; index++)
		{
			const double alpha = static_cast<double>(index) / 100.0;
			const glm::dquat exact = glm::slerp(from, to, alpha);
			const glm::dquat cheap = glm::normalize(from * (1.0 - alpha) + to * alpha);
			worst = std::max(worst, AngleBetween(exact, cheap));
		}
		std::printf("a turn of %5.1f degrees: nlerp strays at most %.3f degrees from slerp\n", degrees, worst);
	}
	return 0;
}
