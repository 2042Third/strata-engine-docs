// Each function prints how many calls are open while it runs: that count is the depth of the call stack.
#include <cstdio>
float ToRadians(float degrees, int depth)
{
	std::printf("depth %d: ToRadians\n", depth);
	return degrees * 3.14159265f / 180.0f;
}

float TurnAngle(float degreesPerSecond, float deltaTime, int depth)
{
	std::printf("depth %d: TurnAngle\n", depth);
	return ToRadians(degreesPerSecond * deltaTime, depth + 1);
}

void OnUpdate(float deltaTime)
{
	std::printf("depth 1: OnUpdate\n");
	const float angle = TurnAngle(90.0f, deltaTime, 2);
	std::printf("depth 1: OnUpdate again, angle %.4f\n", angle);
}

int main()
{
	OnUpdate(0.016f);
}
