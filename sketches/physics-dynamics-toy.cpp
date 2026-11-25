// A toy solver: two Euler steps on a spring, then a resting body on a floor with and without an impulse at the contact.
#include <cstdio>

int main()
{
	const float h = 1.0f / 60.0f; // one step
	const float stiffness = 100.0f; // a unit mass on a spring: energy = v * v / 2 + stiffness * x * x / 2

	float explicitX = 1.0f, explicitV = 0.0f; // explicit Euler: move with the old velocity, then change it
	float semiX = 1.0f, semiV = 0.0f;         // semi-implicit Euler: change the velocity first, move with the new one
	for (int step = 0; step < 600; step++)
	{
		const float acceleration = -stiffness * explicitX;
		explicitX += explicitV * h;
		explicitV += acceleration * h;
		semiV += -stiffness * semiX * h;
		semiX += semiV * h;
	}
	std::printf("energy after 10 s: explicit %.0f, semi-implicit %.1f\n",
		explicitV * explicitV / 2 + stiffness * explicitX * explicitX / 2, semiV * semiV / 2 + stiffness * semiX * semiX / 2);

	const float gravity = -9.81f;
	float naiveY = 0.0f, naiveV = 0.0f; // push the overlap out, keep the velocity
	float impulseY = 0.0f, impulseV = 0.0f;
	for (int step = 0; step < 60; step++)
	{
		naiveV += gravity * h;
		naiveY += naiveV * h;
		if (naiveY < 0.0f)
			naiveY = 0.0f;

		impulseV += gravity * h;
		if (impulseY + impulseV * h < 0.0f) // the step would end below the floor: an impulse removes the approach speed
			impulseV += -impulseV;          // impulse = mass * (-velocity), mass 1
		impulseY += impulseV * h;
	}
	std::printf("resting body after 1 s: naive velocity %.2f m/s, impulse velocity %.2f m/s\n", naiveV, impulseV);
}
