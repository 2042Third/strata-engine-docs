// Two quarter turns, one about Z (roll) and one about Y (yaw), done in both orders on the right direction.
#include <cmath>
#include <cstdio>
#include <glm/glm.hpp>
#include <glm/gtc/quaternion.hpp>

static void Print(const char* label, const glm::vec3& direction)
{
	std::printf("%s (%.0f, %.0f, %.0f)\n", label, std::round(direction.x) + 0.0f, std::round(direction.y) + 0.0f, std::round(direction.z) + 0.0f);
}

int main()
{
	const glm::vec3 right(1.0f, 0.0f, 0.0f);
	const glm::quat roll = glm::angleAxis(glm::radians(90.0f), glm::vec3(0.0f, 0.0f, 1.0f));
	const glm::quat yaw = glm::angleAxis(glm::radians(90.0f), glm::vec3(0.0f, 1.0f, 0.0f));
	Print("roll first, then yaw:", (yaw * roll) * right);
	Print("yaw first, then roll:", (roll * yaw) * right);
}
