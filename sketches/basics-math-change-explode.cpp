// The semi-implicit step on the spring from before, with larger and larger steps: past a step of 2 s it explodes.
#include <cmath>
#include <cstdio>
#include <vector>

float LargestPosition(float step)
{
	float position = 1.0f, velocity = 0.0f, largest = 1.0f;
	for (int i = 0; i < 20; i++)
	{
		velocity += -position * step;
		position += velocity * step;
		largest = std::fmax(largest, std::fabs(position));
	}
	return largest;
}

int main()
{
	for (float step : std::vector<float>{ 0.5f, 1.0f, 1.9f, 2.1f })
		std::printf("step %.1f s: largest |x| in 20 steps %g\n", step, LargestPosition(step));
	return 0;
}
