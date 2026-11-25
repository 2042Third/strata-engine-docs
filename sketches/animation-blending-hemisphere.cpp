// Blends two rotations with weights 0.5 and 0.5, with and without the hemisphere test.
#include <cmath>
#include <cstdio>
#include <glm/glm.hpp>
#include <glm/gtc/quaternion.hpp>

float BlendAngle(const glm::quat& a, const glm::quat& b, bool useHemisphere)
{
	const float weight = 0.5f;
	// b and -b are one rotation: flip b when it points away from a.
	const float sign = (useHemisphere && glm::dot(a, b) < 0.0f) ? -1.0f : 1.0f;
	glm::quat sum(a.w * weight + b.w * weight * sign, a.x * weight + b.x * weight * sign,
		a.y * weight + b.y * weight * sign, a.z * weight + b.z * weight * sign);
	sum = glm::normalize(sum);
	return glm::degrees(2.0f * std::atan2(sum.z, sum.w));
}

int main()
{
	const glm::vec3 axis(0.0f, 0.0f, 1.0f);
	const glm::quat a = glm::angleAxis(glm::radians(0.0f), axis);
	const glm::quat b = glm::angleAxis(glm::radians(90.0f), axis);
	const glm::quat minusB(-b.w, -b.x, -b.y, -b.z);
	std::printf("b,  with the test:    %.1f degrees\n", BlendAngle(a, b, true));
	std::printf("-b, with the test:    %.1f degrees\n", BlendAngle(a, minusB, true));
	std::printf("-b, without the test: %.1f degrees\n", BlendAngle(a, minusB, false));
	return 0;
}
