// A ball falls from 10 m with the explicit Euler step: the position moves by the old velocity, then the velocity changes.
#include <cstdio>

int main()
{
	const float gravity = -9.81f;
	const float step = 0.5f;
	float height = 10.0f;
	float velocity = 0.0f;
	for (int i = 0; i <= 4; i++)
	{
		const float time = static_cast<float>(i) * step;
		const float exact = 10.0f + 0.5f * gravity * time * time;
		std::printf("t = %.1f s: height %.3f m, velocity %.3f m/s, exact height %.3f m\n", time, height, velocity, exact);
		height += velocity * step;  // first the position, with the old velocity
		velocity += gravity * step; // then the velocity
	}
	return 0;
}
