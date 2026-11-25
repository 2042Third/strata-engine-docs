// The cross product: a right angle to both, its order, and the normal and area of a triangle.
#include <cstdio>
#include <glm/glm.hpp>

int main()
{
	const glm::vec3 x(1.0f, 0.0f, 0.0f);
	const glm::vec3 y(0.0f, 1.0f, 0.0f);
	const glm::vec3 xy = glm::cross(x, y);
	const glm::vec3 yx = glm::cross(y, x);
	std::printf("cross(x, y) (%g, %g, %g), cross(y, x) (%g, %g, %g)\n", xy.x, xy.y, xy.z, yx.x, yx.y, yx.z);

	const glm::vec3 p0(0.0f, 0.0f, 0.0f);
	const glm::vec3 p1(4.0f, 0.0f, 0.0f);
	const glm::vec3 p2(0.0f, 3.0f, 0.0f);
	const glm::vec3 edges = glm::cross(p1 - p0, p2 - p0);
	const glm::vec3 normal = glm::normalize(edges);
	std::printf("cross of the edges (%g, %g, %g), normal (%g, %g, %g)\n", edges.x, edges.y, edges.z, normal.x, normal.y, normal.z);
	std::printf("triangle area %g\n", glm::length(edges) / 2.0f);
	return 0;
}
