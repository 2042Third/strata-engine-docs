// Coin Run's two effects as plain functions: the collected coin's pop and the follow camera's step.
#include <cmath>
#include <cstdio>
#include <glm/glm.hpp>

float PopHeight(float age) // the coin rises from 1 m to 2.5 m in half a second
{
	const float t = glm::clamp(age / 0.5f, 0.0f, 1.0f); // inverse lerp, clamped
	return glm::mix(1.0f, 2.5f, glm::smoothstep(0.0f, 1.0f, t));
}

float FollowOneSecond(int steps)
{
	float camera = 0.0f;
	for (int step = 0; step < steps; step++)
		camera = glm::mix(camera, 10.0f, 1.0f - std::exp(-3.0f * (1.0f / steps))); // k = 3 per second
	return camera;
}

int main()
{
	std::printf("height at 0, 0.25, 0.5 s: %g %g %g\n", PopHeight(0.0f), PopHeight(0.25f), PopHeight(0.5f));
	std::printf("camera after 1 s: %.3f at 30 steps, %.3f at 120 steps\n", FollowOneSecond(30), FollowOneSecond(120));
	return 0;
}
