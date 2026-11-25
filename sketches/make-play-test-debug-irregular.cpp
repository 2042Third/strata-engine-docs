#include <cstdio>
#include <vector>
float Fall(const std::vector<int>& frames)
{
	const float step = 1.0f / 60.0f;
	float height = 3.0f, speed = 0.0f;
	int accumulator = 0;
	for (const int frameTicks : frames)
	{
		accumulator += frameTicks;
		while (accumulator >= 2)
		{
			speed -= 9.81f * step;
			height += speed * step;
			accumulator -= 2;
		}
	}
	return height;
}

int main()
{
	std::printf("even frames:      %.4f m\n", Fall(std::vector<int>(60, 2)));
	std::printf("irregular frames: %.4f m\n", Fall({ 10, 20, 30, 60 }));
}
