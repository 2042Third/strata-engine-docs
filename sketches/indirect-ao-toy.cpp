#include <algorithm>
#include <cmath>
#include <cstdio>
#include <vector>

// Horizon occlusion of one slice over a 1D height field. The normal points straight up, so a horizon at elevation e
// leaves the share cos(e)^2 of that side's half of the cosine-weighted hemisphere.
float Visibility(const std::vector<float>& height, int column, int radius)
{
	float highest[2] = { 0.0f, 0.0f }; // tan(elevation) of the highest sample on the left and on the right
	for (int side = 0; side < 2; side++)
	{
		const int direction = side == 0 ? -1 : 1;
		for (int step = 1; step <= radius; step++)
		{
			const int sample = column + direction * step;
			if (sample < 0 || sample >= static_cast<int>(height.size()))
				break;
			const float rise = height[static_cast<size_t>(sample)] - height[static_cast<size_t>(column)];
			highest[side] = std::max(highest[side], rise / static_cast<float>(step));
		}
	}
	const float left = 1.0f / (1.0f + highest[0] * highest[0]);
	const float right = 1.0f / (1.0f + highest[1] * highest[1]);
	return 0.5f * (left + right);
}

int main()
{
	// Flat ground, with a wall 3 units high from column 10 on.
	std::vector<float> height(16, 0.0f);
	for (size_t column = 10; column < height.size(); column++)
		height[column] = 3.0f;

	for (int column = 3; column <= 9; column++)
		std::printf("column %2d: visibility %.3f\n", column, Visibility(height, column, 4));
	return 0;
}
