// A gizmo's world offset, turned into a local translation under a parent that moves and scales.
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>

#include <cmath>
#include <cstdio>

int main()
{
	// The parent sits at x = 4 and is twice as large. The crate's local x is 3, so its world x is 4 + 2 * 3 = 10.
	glm::mat4 parentWorld = glm::translate(glm::mat4(1.0f), glm::vec3(4.0f, 0.0f, 0.0f));
	parentWorld = glm::scale(parentWorld, glm::vec3(2.0f));
	const glm::vec3 startLocal(3.0f, 0.0f, 0.0f);
	const glm::vec3 startWorld = glm::vec3(parentWorld * glm::vec4(startLocal, 1.0f));

	// The drag's raw offset in world metres, with the snap step of 0.5 m.
	const float step = 0.5f;
	const float raw = 1.3f;
	const float snapped = std::round(raw / step) * step;

	// An offset is a direction, so w is 0: the parent's translation must not apply to it.
	const glm::vec3 worldOffset(snapped, 0.0f, 0.0f);
	const glm::vec3 localOffset = glm::vec3(glm::inverse(parentWorld) * glm::vec4(worldOffset, 0.0f));
	const glm::vec3 endLocal = startLocal + localOffset;
	const glm::vec3 endWorld = glm::vec3(parentWorld * glm::vec4(endLocal, 1.0f));

	std::printf("start: local %.2f, world %.2f\n", startLocal.x, startWorld.x);
	std::printf("snapped offset: %.2f m in the world, %.2f in the parent's space\n", snapped, localOffset.x);
	std::printf("end: local %.2f, world %.2f\n", endLocal.x, endWorld.x);
	return 0;
}
