// Blending two rotations: slerp, nlerp and the shorter arc.
#include <cstdio>
#include <glm/glm.hpp>
#include <glm/gtc/quaternion.hpp>

float Degrees(const glm::quat& q)
{
	return glm::degrees(glm::angle(q)); // the angle of the turn the quaternion makes
}

int main()
{
	const glm::quat start(1.0f, 0.0f, 0.0f, 0.0f); // the identity: w comes first
	const glm::quat end = glm::angleAxis(glm::radians(90.0f), glm::vec3(0.0f, 1.0f, 0.0f));
	std::printf("slerp, a quarter of the way: %.1f degrees\n", Degrees(glm::slerp(start, end, 0.25f)));
	std::printf("nlerp, a quarter of the way: %.1f degrees\n", Degrees(glm::normalize(start * 0.75f + end * 0.25f)));

	const glm::quat from = glm::angleAxis(glm::radians(10.0f), glm::vec3(0.0f, 1.0f, 0.0f));
	const glm::quat to = glm::angleAxis(glm::radians(350.0f), glm::vec3(0.0f, 1.0f, 0.0f));
	std::printf("dot of 10 and 350 degrees: %.3f\n", glm::dot(from, to));
	std::printf("slerp halfway: %.1f degrees\n", Degrees(glm::slerp(from, to, 0.5f)));
	std::printf("mix halfway: %.1f degrees\n", Degrees(glm::mix(from, to, 0.5f)));
	return 0;
}
