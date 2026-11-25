// Counts the exact tests of a brute-force pair search and of a sweep along one axis, for a lattice of 500 balls.
#include <algorithm>
#include <cstdio>
#include <vector>

struct Ball
{
	float X;
	float Y;
	float Z;
};

static bool Touches(const Ball& a, const Ball& b, float diameter)
{
	const float dx = a.X - b.X;
	const float dy = a.Y - b.Y;
	const float dz = a.Z - b.Z;
	return dx * dx + dy * dy + dz * dz < diameter * diameter;
}

int main()
{
	const float diameter = 0.5f;
	const float spacing = 0.48f;
	std::vector<Ball> balls;
	for (int x = 0; x < 10; x++)
		for (int y = 0; y < 10; y++)
			for (int z = 0; z < 5; z++)
				balls.push_back({ x * spacing, y * spacing, z * spacing });

	int bruteTests = 0;
	int bruteTouching = 0;
	for (size_t i = 0; i < balls.size(); i++)
	{
		for (size_t j = i + 1; j < balls.size(); j++)
		{
			bruteTests++;
			if (Touches(balls[i], balls[j], diameter))
				bruteTouching++;
		}
	}

	// Sweep: sort by X, then test a ball only against the balls whose X lies within one diameter after it.
	std::sort(balls.begin(), balls.end(), [](const Ball& a, const Ball& b) { return a.X < b.X; });
	int sweepTests = 0;
	int sweepTouching = 0;
	for (size_t i = 0; i < balls.size(); i++)
	{
		for (size_t j = i + 1; j < balls.size() && balls[j].X - balls[i].X < diameter; j++)
		{
			sweepTests++;
			if (Touches(balls[i], balls[j], diameter))
				sweepTouching++;
		}
	}

	std::printf("brute force: %d tests, %d touching\n", bruteTests, bruteTouching);
	std::printf("sweep:       %d tests, %d touching\n", sweepTests, sweepTouching);
	return 0;
}
