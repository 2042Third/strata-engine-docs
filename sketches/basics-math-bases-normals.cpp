// A normal under a stretch along x: the model matrix tilts it off the surface, the normal matrix does not.
#include <cstdio>
#include <glm/glm.hpp>

int main()
{
	const glm::mat3 model(glm::vec3(2.0f, 0.0f, 0.0f), glm::vec3(0.0f, 1.0f, 0.0f), glm::vec3(0.0f, 0.0f, 1.0f));
	const glm::vec3 tangent(1.0f, 1.0f, 0.0f); // a direction along the surface
	const glm::vec3 normal(1.0f, -1.0f, 0.0f); // at a right angle to it
	const glm::vec3 surface = model * tangent;

	const glm::vec3 wrong = model * normal;
	const glm::mat3 normalMatrix = glm::transpose(glm::inverse(model));
	const glm::vec3 right = normalMatrix * normal;
	std::printf("surface (%g, %g, %g)\n", surface.x, surface.y, surface.z);
	std::printf("model matrix: (%g, %g, %g), dot with the surface %g\n", wrong.x, wrong.y, wrong.z, glm::dot(wrong, surface));
	std::printf("normal matrix: (%g, %g, %g), dot with the surface %g\n", right.x, right.y, right.z, glm::dot(right, surface));

	const glm::mat3 cofactor(glm::cross(model[1], model[2]), glm::cross(model[2], model[0]), glm::cross(model[0], model[1]));
	const glm::vec3 scaled = cofactor * normal;
	std::printf("cofactor: (%g, %g, %g), the normal matrix's result times %g\n", scaled.x, scaled.y, scaled.z, glm::determinant(model));
	return 0;
}
