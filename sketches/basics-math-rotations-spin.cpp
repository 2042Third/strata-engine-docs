// An angular velocity turns a rotation in small steps: an axis, a rate and a time.
#include <cstdio>
#include <glm/glm.hpp>
#include <glm/gtc/constants.hpp>
#include <glm/gtc/quaternion.hpp>

glm::quat Spin(const glm::quat& rotation, const glm::vec3& angularVelocity, float deltaTime)
{
	const float rate = glm::length(angularVelocity); // radians per second
	if (rate < 1e-6f)
		return rotation; // no axis to turn around
	const glm::quat step = glm::angleAxis(rate * deltaTime, angularVelocity / rate);
	return glm::normalize(step * rotation); // a turn around world axes goes on the left
}

int main()
{
	glm::quat rotation(1.0f, 0.0f, 0.0f, 0.0f);
	const glm::vec3 angularVelocity(0.0f, glm::pi<float>(), 0.0f); // half a turn per second around Y
	for (int frame = 0; frame < 60; frame++)
		rotation = Spin(rotation, angularVelocity, 1.0f / 60.0f);
	std::printf("after 1 s: %.1f degrees\n", glm::degrees(glm::angle(rotation)));
	return 0;
}
