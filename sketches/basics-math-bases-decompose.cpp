// Decomposing the 3x3 part of a matrix: the lengths of its columns are the scale, if the columns are at right angles.
#include <cstdio>
#include <glm/glm.hpp>

void Report(int number, const glm::mat3& m)
{
	const glm::vec3 scale(glm::length(m[0]), glm::length(m[1]), glm::length(m[2]));
	std::printf("matrix %d: scale (%g, %g, %g), determinant %g, ", number, scale.x, scale.y, scale.z, glm::determinant(m));
	if (glm::min(scale.x, glm::min(scale.y, scale.z)) < 0.0001f)
		std::printf("a zero scale: no rotation to find\n");
	else if (glm::abs(glm::dot(m[0], m[1])) + glm::abs(glm::dot(m[0], m[2])) + glm::abs(glm::dot(m[1], m[2])) > 0.0001f)
		std::printf("columns not at right angles: a shear\n");
	else
		std::printf("%s\n", glm::determinant(m) < 0.0f ? "a mirror: one scale is negative" : "rotation and scale");
}

int main()
{
	Report(1, glm::mat3(glm::vec3(0.0f, 2.0f, 0.0f), glm::vec3(-3.0f, 0.0f, 0.0f), glm::vec3(0.0f, 0.0f, 1.0f)));
	Report(2, glm::mat3(glm::vec3(1.0f, 0.0f, 0.0f), glm::vec3(1.0f, 1.0f, 0.0f), glm::vec3(0.0f, 0.0f, 1.0f)));
	Report(3, glm::mat3(glm::vec3(-1.0f, 0.0f, 0.0f), glm::vec3(0.0f, 1.0f, 0.0f), glm::vec3(0.0f, 0.0f, 1.0f)));
	Report(4, glm::mat3(glm::vec3(1.0f, 0.0f, 0.0f), glm::vec3(0.0f, 1.0f, 0.0f), glm::vec3(0.0f, 0.0f, 0.0f)));
	return 0;
}
