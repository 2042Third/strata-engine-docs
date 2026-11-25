// A jump that leaves the ground at 5 m/s, simulated with different step sizes; the exact peak is 1.274 m.
#include <cstdio>

float JumpPeak(float step)
{
	float height = 0.0f, velocity = 5.0f, peak = 0.0f;
	while (velocity > 0.0f)
	{
		velocity += -9.81f * step;
		height += velocity * step;
		peak = height > peak ? height : peak;
	}
	return peak;
}

int main()
{
	for (int rate = 30; rate <= 120; rate *= 2)
		std::printf("step 1/%d s: jump peak %.3f m\n", rate, JumpPeak(1.0f / static_cast<float>(rate)));
	return 0;
}
