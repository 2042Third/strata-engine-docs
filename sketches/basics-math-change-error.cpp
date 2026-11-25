// One second of free fall from 10 m with the semi-implicit step: the error shrinks in proportion to the step.
#include <cstdio>

float FallError(float step)
{
	float height = 10.0f, velocity = 0.0f;
	const int count = static_cast<int>(1.0f / step + 0.5f);
	for (int i = 0; i < count; i++)
	{
		velocity += -9.81f * step;
		height += velocity * step;
	}
	return height - (10.0f - 4.905f); // the exact height after 1 s is 10 - 4.905 t² = 5.095 m
}

int main()
{
	for (float step = 0.5f; step > 0.01f; step *= 0.2f)
		std::printf("step %.2f s: error after 1 s %.3f m\n", step, FallError(step));
	return 0;
}
