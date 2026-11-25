#include <cstdio>
#include <glm/glm.hpp>
#include <optional>

float SignedDistance(const glm::vec4& plane, const glm::vec3& point) { return glm::dot(glm::vec3(plane), point) + plane.w; }

std::optional<float> HitPlane(const glm::vec3& origin, const glm::vec3& direction, const glm::vec4& plane)
{
	const float slope = glm::dot(glm::vec3(plane), direction);
	if (glm::abs(slope) < 1e-8f)
		return std::nullopt; // parallel: the ray never meets the plane
	const float t = -SignedDistance(plane, origin) / slope;
	return t >= 0.0f ? std::optional<float>(t) : std::nullopt; // a negative t lies behind the origin
}

int main()
{
	const glm::vec4 floor(0.0f, 1.0f, 0.0f, -2.0f);
	const glm::vec3 origin(0.0f, 5.0f, 0.0f);
	std::printf("above %g, below %g\n", SignedDistance(floor, glm::vec3(3.0f, 5.0f, 1.0f)), SignedDistance(floor, glm::vec3(0.0f)));
	std::printf("slanted %g, ", HitPlane(origin, glm::vec3(0.6f, -0.8f, 0.0f), floor).value_or(-1.0f));
	std::printf("parallel %g, ", HitPlane(origin, glm::vec3(1.0f, 0.0f, 0.0f), floor).value_or(-1.0f));
	std::printf("behind %g\n", HitPlane(origin, glm::vec3(0.0f, 1.0f, 0.0f), floor).value_or(-1.0f));
}
