// Chasing a target for one second at 30 and at 120 frames per second, with two kinds of weight.
#include <cmath>
#include <cstdio>

float GapAfterOneSecond(int framesPerSecond, bool exponential)
{
	const float k = 2.0f; // per second
	const float deltaTime = 1.0f / framesPerSecond;
	float value = 0.0f; // the target is 1
	for (int frame = 0; frame < framesPerSecond; frame++)
	{
		const float weight = exponential ? 1.0f - std::exp(-k * deltaTime) : 0.0645f; // 0.0645 suits 30 frames per second
		value += (1.0f - value) * weight;
	}
	return 1.0f - value;
}

int main()
{
	std::printf("fixed fraction: gap %.4f at 30 fps, %.4f at 120 fps\n", GapAfterOneSecond(30, false), GapAfterOneSecond(120, false));
	std::printf("1 - exp(-k dt): gap %.4f at 30 fps, %.4f at 120 fps\n", GapAfterOneSecond(30, true), GapAfterOneSecond(120, true));
	return 0;
}
