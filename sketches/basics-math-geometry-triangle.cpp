#include <cstdio>
#include <glm/glm.hpp>
#include <optional>

std::optional<float> HitTriangle(const glm::vec3& origin, const glm::vec3& direction, const glm::vec3 corner[3])
{
	const glm::vec3 normal = glm::cross(corner[1] - corner[0], corner[2] - corner[0]);
	const float slope = glm::dot(normal, direction);
	const float t = glm::dot(normal, corner[0] - origin) / slope;
	if (glm::abs(slope) < 1e-8f || t < 0.0f)
		return std::nullopt; // parallel to the triangle's plane, or the plane lies behind the origin
	const glm::vec3 point = origin + direction * t;
	for (int i = 0; i < 3; i++) // one cross product per edge
		if (glm::dot(glm::cross(corner[(i + 1) % 3] - corner[i], point - corner[i]), normal) < 0.0f)
			return std::nullopt; // the point lies outside this edge
	return t;
}

int main()
{
	const glm::vec3 corner[3] = { glm::vec3(0.0f, 0.0f, 0.0f), glm::vec3(4.0f, 0.0f, 0.0f), glm::vec3(0.0f, 4.0f, 0.0f) };
	const glm::vec3 down(0.0f, 0.0f, -1.0f);
	std::printf("inside %g, ", HitTriangle(glm::vec3(1.0f, 1.0f, 5.0f), down, corner).value_or(-1.0f));
	std::printf("outside %g\n", HitTriangle(glm::vec3(3.0f, 3.0f, 5.0f), down, corner).value_or(-1.0f));
}
