// What a variable step changes: how high the same jump goes, and whether a stiff spring stays calm.
// Both use semi-implicit Euler: the speed changes first, then the position moves with the new speed.
#include <algorithm>
#include <cmath>
#include <cstdio>

namespace
{
	// The highest point of a jump that leaves the ground at 5 m/s, stepped with `deltaTime`.
	float JumpPeak(float deltaTime)
	{
		float height = 0.0f;
		float speed = 5.0f; // m/s
		float peak = 0.0f;
		while (speed > 0.0f)
		{
			speed -= 9.81f * deltaTime;
			height += speed * deltaTime;
			peak = std::max(peak, height);
		}
		return peak;
	}

	// The largest distance from rest that a spring (stiffness 3600 per second squared) reaches in one second.
	float SpringReach(float deltaTime)
	{
		float position = 1.0f; // m
		float speed = 0.0f;    // m/s
		float reach = 1.0f;
		const int steps = static_cast<int>(std::lround(1.0f / deltaTime));
		for (int i = 0; i < steps; i++)
		{
			speed -= 3600.0f * position * deltaTime;
			position += speed * deltaTime;
			reach = std::max(reach, std::abs(position));
		}
		return reach;
	}
}

int main()
{
	const float steps[] = { 1.0f / 240.0f, 1.0f / 60.0f, 1.0f / 30.0f, 1.0f / 15.0f };
	for (const float deltaTime : steps)
		std::printf("step %5.1f ms: jump peak %.3f m\n", deltaTime * 1000.0f, JumpPeak(deltaTime));
	for (const float deltaTime : { 1.0f / 60.0f, 1.0f / 40.0f, 1.0f / 20.0f })
		std::printf("step %5.1f ms: spring reach %.1f m\n", deltaTime * 1000.0f, SpringReach(deltaTime));
}
