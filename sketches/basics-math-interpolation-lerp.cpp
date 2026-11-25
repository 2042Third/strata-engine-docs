// Linear interpolation of a number, a position and a color, by hand and with glm::mix.
#include <cstdio>
#include <glm/glm.hpp>

float Lerp(float a, float b, float t)
{
	return a + (b - a) * t;
}

int main()
{
	std::printf("10 to 30 at t = 0.25: %g\n", Lerp(10.0f, 30.0f, 0.25f));
	std::printf("t = 0: %g, t = 1: %g, t = 1.5: %g\n", Lerp(10.0f, 30.0f, 0.0f), Lerp(10.0f, 30.0f, 1.0f), Lerp(10.0f, 30.0f, 1.5f));
	std::printf("weighted average: %g\n", 0.75f * 10.0f + 0.25f * 30.0f);
	const glm::vec3 start(0.0f, 1.0f, 0.0f);
	const glm::vec3 coin(4.0f, 1.0f, 8.0f);
	const glm::vec3 point = glm::mix(start, coin, 0.25f); // one call blends all three coordinates
	std::printf("a quarter of the way: (%g, %g, %g)\n", point.x, point.y, point.z);
	const glm::vec3 red(1.0f, 0.0f, 0.0f);
	const glm::vec3 blue(0.0f, 0.0f, 1.0f);
	const glm::vec3 purple = glm::mix(red, blue, 0.5f);
	std::printf("half red, half blue: (%g, %g, %g)\n", purple.x, purple.y, purple.z);
	return 0;
}
