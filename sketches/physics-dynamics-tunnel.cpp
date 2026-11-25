// Predict then run: where a fast sphere meets a thin wall, and whether a dropped sphere of restitution 1 bounces.
#include <cmath>
#include <cstdio>

// Positions of the sphere at the ends of steps are 0, 4 and 8 m; the wall spans 5.95 to 6.05 m, the sphere's radius is 0.1 m.
bool Overlaps(float centerA, float radius, float front, float back)
{
	return centerA + radius > front && centerA - radius < back;
}

void Fire(const char* name, bool sweptTest)
{
	const float radius = 0.1f, front = 5.95f, back = 6.05f, stepLength = 4.0f; // 240 m/s at 60 steps per second
	for (int step = 1; step <= 2; step++)
	{
		const float before = stepLength * static_cast<float>(step - 1);
		const float after = stepLength * static_cast<float>(step);
		const bool hit = sweptTest ? Overlaps(0.5f * (before + after), 0.5f * stepLength + radius, front, back)
								   : Overlaps(after, radius, front, back);
		if (hit)
		{
			const float fraction = (front - radius - before) / stepLength; // time of impact as a share of the step
			std::printf("%s: stops at x = %.2f m, %.1f %% into step %d\n", name, front - radius, fraction * 100.0f, step);
			return;
		}
	}
	std::printf("%s: tunnels, ends at x = 8.00 m\n", name);
}

void Drop(float height)
{
	const float speed = std::sqrt(2.0f * 9.81f * height); // speed at the floor
	std::printf("dropped from %.2f m: meets the floor at %.2f m/s, %s\n", height, speed,
		speed > 1.0f ? "bounces" : "does not bounce");
}

int main()
{
	Fire("static wall, swept", true);
	Fire("kinematic wall, no bullet", false);
	Fire("kinematic wall, bullet", true);
	Drop(0.02f);
	Drop(1.0f);
}
