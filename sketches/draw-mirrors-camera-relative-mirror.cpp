#include <cstdio>
#include <glm/glm.hpp>
#include <initializer_list>

// The normal through the cofactor matrix of the 3x3, with its sign flipped when the determinant is negative.
glm::vec3 TransformNormal(const glm::mat3& matrix, const glm::vec3& normal)
{
	const glm::vec3 sum = glm::cross(matrix[1], matrix[2]) * normal.x + glm::cross(matrix[2], matrix[0]) * normal.y + glm::cross(matrix[0], matrix[1]) * normal.z;
	return glm::determinant(matrix) < 0.0f ? -sum : sum;
}

int main()
{
	for (const float scaleX : { 2.0f, -2.0f })
	{
		const glm::mat3 matrix(glm::vec3(scaleX, 0.0f, 0.0f), glm::vec3(0.0f, 1.0f, 0.0f), glm::vec3(0.0f, 0.0f, 1.0f));
		const glm::vec3 normal = TransformNormal(matrix, glm::vec3(1.0f, 1.0f, 0.0f));
		const glm::vec3 b = matrix * glm::vec3(1.0f, 0.0f, 0.0f);
		const glm::vec3 c = matrix * glm::vec3(0.0f, 1.0f, 0.0f);
		const float winding = b.x * c.y - b.y * c.x;
		std::printf("scale %+.0f: determinant %+.0f, normal (%+.0f, %+.0f), winding %+.0f\n", static_cast<double>(scaleX),
			static_cast<double>(glm::determinant(matrix)), static_cast<double>(normal.x), static_cast<double>(normal.y), static_cast<double>(winding));
	}
	return 0;
}
