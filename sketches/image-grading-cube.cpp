#include <cstdio>

// Writes a 3D .cube table of N points each way that lifts blue by a tenth of its distance to 1: cool shadows, white unchanged.
int main()
{
	const int size = 3;
	std::printf("TITLE \"Cool shadows\"\nLUT_3D_SIZE %d\n", size);
	for (int blue = 0; blue < size; blue++)
	{
		for (int green = 0; green < size; green++)
		{
			for (int red = 0; red < size; red++)
			{
				const double last = size - 1;
				const double b = blue / last;
				std::printf("%.6f %.6f %.6f\n", red / last, green / last, b + 0.1 * (1.0 - b));
			}
		}
	}
	return 0;
}
