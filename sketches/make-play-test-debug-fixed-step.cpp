// A ball falls for one second, in frames of two lengths; the fixed step is 1/60 s.
#include <cstdio>

float Fall(float frameTime, int frames, bool fixedStep)
{
	float height = 3.0f, speed = 0.0f, accumulator = 0.0f;
	const float step = fixedStep ? 1.0f / 60.0f : frameTime;
	for (int frame = 0; frame < frames; frame++)
	{
		accumulator += frameTime;
		while (accumulator >= step)
		{
			speed -= 9.81f * step;
			height += speed * step;
			accumulator -= step;
		}
	}
	return height;
}

int main()
{
	std::printf("60 frames of 1/60 s: variable %.4f m, fixed %.4f m\n", Fall(1.0f / 60.0f, 60, false), Fall(1.0f / 60.0f, 60, true));
	std::printf("30 frames of 1/30 s: variable %.4f m, fixed %.4f m\n", Fall(1.0f / 30.0f, 30, false), Fall(1.0f / 30.0f, 30, true));
}
