// The Coin Run bug: the angle of one frame turned into radians twice, beside the angle turned once.
#include <cstdio>

float ToRadians(float degrees)
{
	return degrees * 3.14159265f / 180.0f;
}

int main()
{
	const float degreesPerSecond = 90.0f;
	const float deltaTime = 1.0f / 60.0f; // one frame at 60 frames per second
	const float degrees = degreesPerSecond * deltaTime;

	const float correct = ToRadians(degrees);
	const float planted = ToRadians(ToRadians(degrees));

	std::printf("degrees in one frame: %.4f\n", degrees);
	std::printf("correct angle in radians: %.6f\n", correct);
	std::printf("planted angle in radians: %.6f\n", planted);
	std::printf("the planted coin turns %.1f times too slowly\n", correct / planted);
	return 0;
}
