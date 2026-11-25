// A 2 kg crate at rest is pushed with 6 N for one second at 60 steps per second, then another is given the same impulse.
#include <cstdio>

int main()
{
	const float mass = 2.0f;
	const float step = 1.0f / 60.0f;
	float velocity = 0.0f, position = 0.0f;
	for (int i = 0; i < 60; i++)
	{
		velocity += (6.0f / mass) * step; // force over mass is the acceleration
		position += velocity * step;
	}
	std::printf("pushed for 1 s: velocity %.3f m/s, moved %.3f m\n", velocity, position);

	const float impulse = 6.0f * 1.0f;           // force times time, in newton seconds
	std::printf("impulse of %g N s: velocity %.3f m/s at once\n", impulse, impulse / mass);
	return 0;
}
