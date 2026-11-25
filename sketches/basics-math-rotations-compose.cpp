// Combining two turns: the order decides which axes they turn around.
#include <cstdio>
#include <glm/glm.hpp>
#include <glm/gtc/quaternion.hpp>

void Print(const glm::vec3& v)
{
	const glm::vec3 shown = glm::round(v * 100.0f) / 100.0f + 0.0f; // two places, and no -0
	std::printf("(%g, %g, %g)\n", shown.x, shown.y, shown.z);
}

int main()
{
	const glm::quat yaw = glm::angleAxis(glm::radians(90.0f), glm::vec3(0.0f, 1.0f, 0.0f));
	const glm::quat pitch = glm::angleAxis(glm::radians(90.0f), glm::vec3(1.0f, 0.0f, 0.0f));
	const glm::vec3 forward(0.0f, 0.0f, -1.0f);
	std::printf("yaw * pitch turns forward to ");
	Print(yaw * pitch * forward);
	std::printf("pitch * yaw turns forward to ");
	Print(pitch * yaw * forward);
	std::printf("the conjugate of yaw undoes it: ");
	Print(glm::conjugate(yaw) * (yaw * forward));
	return 0;
}
