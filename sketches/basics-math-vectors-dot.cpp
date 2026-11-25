// The dot product: in front or behind, the angle between two directions, a projection and a bounce.
#include <cmath>
#include <cstdio>
#include <glm/glm.hpp>

int main()
{
	const glm::vec3 facing(0.0f, 0.0f, 1.0f);
	std::printf("coin ahead: %g, coin behind: %g\n", glm::dot(facing, glm::vec3(2.0f, 0.0f, 5.0f)), glm::dot(facing, glm::vec3(2.0f, 0.0f, -5.0f)));

	const glm::vec3 a = glm::normalize(glm::vec3(1.0f, 0.0f, 0.0f));
	const glm::vec3 b = glm::normalize(glm::vec3(1.0f, 1.0f, 0.0f));
	std::printf("angle between: %g degrees\n", glm::degrees(std::acos(glm::dot(a, b))));

	const glm::vec3 velocity(3.0f, 2.0f, 0.0f);
	const glm::vec3 up(0.0f, 1.0f, 0.0f);
	const glm::vec3 along = glm::dot(velocity, up) * up; // the part of the velocity along the up axis
	const glm::vec3 flat = velocity - along;             // the part left in the floor's plane
	std::printf("along (%g, %g, %g), flat (%g, %g, %g)\n", along.x, along.y, along.z, flat.x, flat.y, flat.z);

	const glm::vec3 wall(-1.0f, 0.0f, 0.0f); // the wall's normal, pointing back into the room
	const glm::vec3 bounced = glm::reflect(glm::vec3(4.0f, 0.0f, 3.0f), wall);
	std::printf("bounced (%g, %g, %g)\n", bounced.x, bounced.y, bounced.z);
	return 0;
}
