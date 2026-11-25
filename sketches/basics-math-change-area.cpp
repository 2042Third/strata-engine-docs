// Rectangles under the speed graph v = 2 t between 0 s and 4 s: narrower rectangles come closer to the area, 16 m.
#include <cstdio>

float SumOfRectangles(int count)
{
	const float width = 4.0f / static_cast<float>(count);
	float sum = 0.0f;
	for (int i = 0; i < count; i++)
	{
		const float time = static_cast<float>(i) * width;
		sum += 2.0f * time * width; // the speed at the start of the rectangle times its width
	}
	return sum;
}

int main()
{
	for (int count = 4; count <= 1024; count *= 4)
		std::printf("%d rectangles: %g m\n", count, SumOfRectangles(count));
	return 0;
}
