// Rounding: a sum that should be 1, and a hit point that should lie exactly on its plane.
#include <cstdio>
#include <glm/glm.hpp>

int main()
{
	float sum = 0.0f;
	for (int i = 0; i < 10; i++)
		sum += 0.1f;
	std::printf("sum %.9g, equal to 1: %d, close to 1: %d\n", sum, sum == 1.0f, glm::abs(sum - 1.0f) < 1e-5f);

	const glm::vec3 normal = glm::normalize(glm::vec3(1.0f, 2.0f, 2.0f));
	const glm::vec3 origin(0.3f, 7.1f, 0.2f);
	const glm::vec3 direction = glm::normalize(glm::vec3(0.2f, -1.0f, 0.1f));
	const float t = -(glm::dot(normal, origin) - 1.0f) / glm::dot(normal, direction);
	const glm::vec3 hit = origin + direction * t;
	std::printf("distance of the hit point from the plane: %g\n", glm::dot(normal, hit) - 1.0f);
	return 0;
}
