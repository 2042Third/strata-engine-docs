// The magnet's step for one frame: a coin within reach moves toward the ball at a fixed speed.
#include <cstdio>
#include <glm/glm.hpp>

glm::vec3 MagnetStep(const glm::vec3& coin, const glm::vec3& ball, float reach, float speed, float deltaTime)
{
	const glm::vec3 toBall = ball - coin;
	const float distance = glm::length(toBall);
	if (distance > reach || distance < 0.001f) // out of reach, or already on the ball: no direction to move in
		return coin;
	return coin + glm::normalize(toBall) * glm::min(speed * deltaTime, distance); // never step past the ball
}

int main()
{
	const glm::vec3 ball(0.0f, 0.5f, 0.0f);
	glm::vec3 coin(2.0f, 0.5f, 0.0f);
	for (int frame = 1; frame <= 5; frame++)
	{
		coin = MagnetStep(coin, ball, 3.0f, 4.0f, 0.125f);
		std::printf("frame %d: coin at (%g, %g, %g)\n", frame, coin.x, coin.y, coin.z);
	}
	std::printf("a coin 5 m away stays at x = %g\n", MagnetStep(glm::vec3(5.0f, 0.5f, 0.0f), ball, 3.0f, 4.0f, 0.125f).x);
	return 0;
}
