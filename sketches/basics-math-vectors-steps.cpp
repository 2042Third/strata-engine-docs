// Steps between positions: subtract, add and scale, one coordinate at a time.
#include <cstdio>
#include <glm/glm.hpp>

int main()
{
	const glm::vec3 start(1.0f, 0.0f, 2.0f); // where the ball is
	const glm::vec3 coin(4.0f, 0.0f, 6.0f);  // where a coin is
	const glm::vec3 step = coin - start;     // the arrow from the ball to the coin
	const glm::vec3 back = start + step;     // the step added to the start lands on the coin
	const glm::vec3 half = step * 0.5f;      // half the step: the same direction, half as long
	std::printf("step (%g, %g, %g)\n", step.x, step.y, step.z);
	std::printf("start + step (%g, %g, %g)\n", back.x, back.y, back.z);
	std::printf("half (%g, %g, %g)\n", half.x, half.y, half.z);

	const glm::vec2 mouse(12.0f, -5.0f); // a mouse movement, in pixels
	const glm::vec2 twice = mouse + mouse;
	std::printf("mouse + mouse (%g, %g)\n", twice.x, twice.y);
	return 0;
}
