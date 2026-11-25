// A spring that pulls with an acceleration of -x, started at x = 1: the energy 0.5 v² + 0.5 x² should stay at 0.5.
#include <cstdio>

int main()
{
	const float step = 0.5f;
	float explicitX = 1.0f, explicitV = 0.0f;
	float semiX = 1.0f, semiV = 0.0f;
	for (int i = 1; i <= 20; i++)
	{
		const float oldX = explicitX;
		explicitX += explicitV * step; // explicit: the position with the old velocity ...
		explicitV += -oldX * step;     // ... the velocity with the old position
		semiV += -semiX * step;        // semi-implicit: the velocity first ...
		semiX += semiV * step;         // ... the position with the new velocity
		if (i <= 4 || i == 20)
			std::printf("step %2d: explicit x %7.3f energy %6.3f | semi-implicit x %6.3f energy %5.3f\n", i, explicitX,
				0.5f * explicitV * explicitV + 0.5f * explicitX * explicitX, semiX, 0.5f * semiV * semiV + 0.5f * semiX * semiX);
	}
	return 0;
}
