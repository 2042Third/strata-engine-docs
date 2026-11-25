#include <cstdio>
#include <glm/glm.hpp>

int main()
{
	// The constructor reads its numbers column by column: the first column is (1, 2), the second (3, 4).
	const glm::mat2 m(1.0f, 2.0f, 3.0f, 4.0f);
	std::printf("m[0] = (%g, %g)\n", m[0].x, m[0].y);
	std::printf("m[1] = (%g, %g)\n", m[1].x, m[1].y);
	std::printf("m[1][0] = %g\n", m[1][0]);
	const glm::vec2 result = m * glm::vec2(1.0f, 1.0f);
	std::printf("m * (1, 1) = (%g, %g)\n", result.x, result.y);

	// The identity matrix has the axes themselves as its columns, so it changes nothing.
	const glm::vec2 same = glm::mat2(1.0f) * glm::vec2(3.0f, 1.0f);
	std::printf("identity * (3, 1) = (%g, %g)\n", same.x, same.y);
}
