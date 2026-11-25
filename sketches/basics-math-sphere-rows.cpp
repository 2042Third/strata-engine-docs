// The area of the unit sphere as a sum of rows, with and without the sin(theta) of each row.
#include <cmath>
#include <cstdio>
#include <initializer_list>
#include <numbers>

int main()
{
	const float pi = std::numbers::pi_v<float>;
	for (int rows : { 4, 16, 64 })
	{
		const float step = pi / static_cast<float>(rows);
		float flat = 0.0f;
		float weighted = 0.0f;
		for (int row = 0; row < rows; row++)
		{
			const float polar = (static_cast<float>(row) + 0.5f) * step; // the middle of the row
			flat += 2.0f * pi * step; // every row counted as if it had the same size
			weighted += 2.0f * pi * std::sin(polar) * step; // a ring of circumference 2 pi sin(theta)
		}
		std::printf("%2d rows: without sin %.3f, with sin %.3f, exact %.3f\n", rows, flat, weighted, 4.0f * pi);
	}
	return 0;
}
