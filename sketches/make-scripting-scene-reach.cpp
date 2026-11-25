#include <glm/glm.hpp>

#include <cstdio>
#include <vector>

int main()
{
	const std::vector<glm::vec3> coins = { { -4.0f, 0.8f, 0.0f }, { -2.0f, 0.8f, 2.0f }, { 0.0f, 0.8f, 3.0f }, { 2.0f, 0.8f, 2.0f }, { 4.0f, 0.8f, 0.0f } };
	const glm::vec3 ball(0.0f, 0.8f, 2.6f);
	int left = 0;
	for (const glm::vec3& coin : coins)
	{
		const float distance = glm::distance(coin, ball);
		const bool collected = distance < 0.7f;
		std::printf("coin at x=%.1f: distance %.2f, glows %d, collected %d\n", coin.x, distance, distance < 2.1f ? 1 : 0, collected ? 1 : 0);
		if (!collected)
			left++;
	}
	std::printf("coins left: %d\n", left);
}
