// From a pixel and its depth back to a position in view space, and the direction of the ray through the pixel.
#include <cstdio>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>

int main()
{
	const glm::mat4 projection = glm::perspectiveRH_ZO(glm::radians(90.0f), 2.0f, 100.0f, 1.0f);
	const glm::mat4 inverseProjection = glm::inverse(projection);

	const float pixelX = 550.0f, pixelY = 150.0f, depth = 0.2424f;
	const glm::vec4 ndc(pixelX / 800.0f * 2.0f - 1.0f, 1.0f - pixelY / 400.0f * 2.0f, depth, 1.0f);
	const glm::vec4 back = inverseProjection * ndc;
	const glm::vec3 position = glm::vec3(back) / back.w;
	std::printf("position (%.2f, %.2f, %.2f)\n", position.x, position.y, position.z);

	// The ray needs no depth: x and y at the image plane, one unit in front of the camera.
	const float halfHeight = glm::tan(glm::radians(90.0f) * 0.5f);
	const glm::vec3 direction = glm::normalize(glm::vec3(ndc.x * halfHeight * 2.0f, ndc.y * halfHeight, -1.0f));
	std::printf("direction (%.3f, %.3f, %.3f)\n", direction.x, direction.y, direction.z);
	return 0;
}
