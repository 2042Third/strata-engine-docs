// A world point through the view matrix, the projection, the divide and the pixel grid.
#include <cstdio>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>

int main()
{
	const glm::mat4 cameraWorld = glm::translate(glm::mat4(1.0f), glm::vec3(2.0f, 1.0f, 5.0f));
	const glm::mat4 view = glm::inverse(cameraWorld);
	// Near and far swapped: the near plane stores 1, the far plane 0.
	const glm::mat4 projection = glm::perspectiveRH_ZO(glm::radians(90.0f), 2.0f, 100.0f, 1.0f);

	const glm::vec4 world(5.0f, 2.0f, 1.0f, 1.0f);
	const glm::vec4 inView = view * world;
	const glm::vec4 clip = projection * inView;
	const glm::vec3 ndc = glm::vec3(clip) / clip.w;
	const float pixelX = (ndc.x * 0.5f + 0.5f) * 800.0f;
	const float pixelY = (0.5f - ndc.y * 0.5f) * 400.0f;

	std::printf("view  (%g, %g, %g)\n", inView.x, inView.y, inView.z);
	std::printf("clip  (%g, %g, %.4f, %g)\n", clip.x, clip.y, clip.z, clip.w);
	std::printf("ndc   (%g, %g, %.4f)\n", ndc.x, ndc.y, ndc.z);
	std::printf("pixel (%g, %g)\n", pixelX, pixelY);
	return 0;
}
