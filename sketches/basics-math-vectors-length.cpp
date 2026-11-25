// Lengths, distances and unit vectors, computed by glm.
#include <cmath>
#include <cstdio>
#include <glm/glm.hpp>

int main()
{
	const glm::vec2 flat(3.0f, 4.0f);
	std::printf("length of (3, 4): %g\n", glm::length(flat));

	const glm::vec3 a(1.0f, 0.0f, 2.0f);
	const glm::vec3 b(4.0f, 0.0f, 6.0f);
	std::printf("distance from a to b: %g\n", glm::distance(a, b));
	std::printf("length of (1, 2, 2): %g\n", glm::length(glm::vec3(1.0f, 2.0f, 2.0f)));

	const glm::vec3 direction = glm::normalize(b - a);
	std::printf("unit vector (%g, %g, %g), length %g\n", direction.x, direction.y, direction.z, glm::length(direction));

	const glm::vec3 nothing = glm::normalize(glm::vec3(0.0f));
	std::printf("normalize of zero is a number: %s\n", std::isnan(nothing.x) ? "no" : "yes");
	return 0;
}
