#include <cmath>
#include <cstdio>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>

// The local position of coin `index` of six, on a circle of the given radius in the ring's x-z plane.
static glm::vec3 CoinLocalPosition(int index, float radius)
{
	const float angle = glm::radians(60.0f * static_cast<float>(index));
	return glm::vec3(radius * std::cos(angle), 0.0f, radius * std::sin(angle));
}

int main()
{
	const glm::mat4 identity(1.0f);
	const glm::mat4 ringWorld = glm::translate(identity, glm::vec3(10.0f, 1.0f, 0.0f))
		* glm::rotate(identity, glm::radians(90.0f), glm::vec3(0.0f, 1.0f, 0.0f));
	for (int index = 0; index < 6; index++)
	{
		const glm::mat4 coinWorld = ringWorld * glm::translate(identity, CoinLocalPosition(index, 3.0f));
		const glm::vec3 world = glm::vec3(coinWorld[3]);
		std::printf("coin %d: world (%.2f, %.2f, %.2f)\n", index, world.x + 0.0f, world.y + 0.0f, world.z + 0.0f);
	}
}
