#include <algorithm>
#include <cstdio>
#include <glm/glm.hpp>

glm::vec2 Shadow(const glm::vec2 corners[], int count, const glm::vec2& axis) // lowest and highest position on the axis
{
	glm::vec2 range(1e30f, -1e30f);
	for (int i = 0; i < count; i++)
	{
		range.x = std::min(range.x, glm::dot(axis, corners[i]));
		range.y = std::max(range.y, glm::dot(axis, corners[i]));
	}
	return range;
}

int main()
{
	const glm::vec2 box[4] = { glm::vec2(0.0f, 0.0f), glm::vec2(2.0f, 0.0f), glm::vec2(2.0f, 2.0f), glm::vec2(0.0f, 2.0f) };
	const glm::vec2 triangle[3] = { glm::vec2(3.0f, 1.5f), glm::vec2(1.5f, 3.0f), glm::vec2(3.0f, 3.0f) };
	for (const glm::vec2& axis : { glm::vec2(1.0f, 0.0f), glm::vec2(0.0f, 1.0f), glm::vec2(1.0f, 1.0f) })
	{
		const glm::vec2 a = Shadow(box, 4, axis), b = Shadow(triangle, 3, axis);
		std::printf("axis (%g, %g): box %g to %g, triangle %g to %g, %s\n", axis.x, axis.y, a.x, a.y, b.x, b.y, a.y < b.x || b.y < a.x ? "apart" : "overlap");
	}
}
