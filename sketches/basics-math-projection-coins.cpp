// Counts the coins that a camera sees, from each coin's offset along the camera's axes.
#include <cmath>
#include <cstdio>
#include <vector>
#include <glm/glm.hpp>

bool IsSeen(const glm::vec3& offset, const glm::vec3& right, const glm::vec3& up, const glm::vec3& forward, float tanHalf, float aspect)
{
	const float depth = glm::dot(offset, forward);
	const float halfHeight = depth * tanHalf;
	return depth > 0.0f && std::abs(glm::dot(offset, up)) <= halfHeight && std::abs(glm::dot(offset, right)) <= halfHeight * aspect;
}

int main()
{
	const glm::vec3 camera(0.0f, 1.0f, 10.0f);
	const float aspect = 1600.0f / 900.0f; // In floats: 1600 / 900 with integers gives 1.
	const float tanHalf = std::tan(glm::radians(60.0f) * 0.5f);
	const std::vector<glm::vec3> coins = { { 0, 1, 5 }, { 6, 1, 5 }, { 2, 2, 0 }, { 0, 1, 15 }, { -3, 4, 2 }, { 0, 9, 6 } };
	int seen = 0;
	for (const glm::vec3& coin : coins)
		if (IsSeen(coin - camera, { 1, 0, 0 }, { 0, 1, 0 }, { 0, 0, -1 }, tanHalf, aspect))
			seen++;
	std::printf("%d of %zu coins are in view\n", seen, coins.size());
}
