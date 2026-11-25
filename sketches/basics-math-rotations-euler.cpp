// Euler angles read back, and a gimbal lock: two triples of angles that make one rotation.
#include <cstdio>
#include <glm/glm.hpp>
#include <glm/gtc/quaternion.hpp>

int main()
{
	const glm::quat yawed(glm::radians(glm::vec3(0.0f, 120.0f, 0.0f))); // pitch, yaw, roll, in degrees
	const glm::vec3 back = glm::degrees(glm::eulerAngles(yawed));
	std::printf("yaw 120 reads back as (%.1f, %.1f, %.1f)\n", back.x, back.y, back.z);

	const glm::quat a(glm::radians(glm::vec3(30.0f, 90.0f, 30.0f)));
	const glm::quat b(glm::radians(glm::vec3(0.0f, 90.0f, 0.0f)));
	std::printf("|dot| of (30, 90, 30) and (0, 90, 0): %.4f\n", glm::abs(glm::dot(a, b)));
	return 0;
}
