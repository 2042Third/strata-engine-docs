// Degrees and radians, and the angles a rotation shows when it is read back.
#include <cstdio>
#include <glm/glm.hpp>
#include <glm/gtc/quaternion.hpp>

int main()
{
	std::printf("180 degrees = %.4f radians\n", glm::radians(180.0f));
	std::printf("360 degrees = %.4f radians\n", glm::radians(360.0f));

	const glm::vec3 typed(0.0f, 120.0f, 0.0f); // Pitch, yaw, roll as typed
	const glm::quat rotation(glm::radians(typed));
	const glm::vec3 readBack = glm::degrees(glm::eulerAngles(rotation));
	std::printf("typed (%.0f, %.0f, %.0f)\n", typed.x, typed.y, typed.z);
	std::printf("read back (%.0f, %.0f, %.0f)\n", readBack.x, readBack.y, readBack.z);
}
