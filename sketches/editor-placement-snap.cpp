// Snapping a placement point along a surface: the axis of the normal keeps its value.
#include <glm/glm.hpp>

#include <cmath>
#include <cstdio>

glm::vec3 Snap(const glm::vec3& point, const glm::vec3& normal, float step)
{
	const glm::vec3 magnitude = glm::abs(normal);
	const int axis = magnitude.x > magnitude.y && magnitude.x > magnitude.z ? 0 : (magnitude.y >= magnitude.z ? 1 : 2);
	glm::vec3 snapped = point;
	for (int i = 0; i < 3; i++)
	{
		if (i != axis)
			snapped[i] = std::round(snapped[i] / step) * step;
	}
	return snapped;
}

int main()
{
	const glm::vec3 point(3.27f, 1.89f, -0.81f);
	const glm::vec3 floor = Snap(point, glm::vec3(0.0f, 1.0f, 0.0f), 0.5f);
	const glm::vec3 wall = Snap(point, glm::vec3(1.0f, 0.0f, 0.0f), 0.5f);
	std::printf("floor: (%.2f, %.2f, %.2f)\n", floor.x, floor.y, floor.z);
	std::printf("wall: (%.2f, %.2f, %.2f)\n", wall.x, wall.y, wall.z);
	return 0;
}
