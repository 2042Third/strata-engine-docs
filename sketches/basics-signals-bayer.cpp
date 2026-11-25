// Dithers the flat value 100.25 over one 4 by 4 block with the Bayer table and prints the rounded values.
#include <cmath>
#include <iostream>

int main()
{
	const int bayer[16] = { 0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5 };
	const double value = 100.25;
	int raised = 0;
	for (int y = 0; y < 4; y++)
	{
		for (int x = 0; x < 4; x++)
		{
			const double threshold = (bayer[y * 4 + x] + 0.5) / 16.0;
			const int shown = static_cast<int>(std::floor(value + threshold));
			raised += shown - 100;
			std::cout << shown << (x < 3 ? ' ' : '\n');
		}
	}
	std::cout << raised << " of 16 pixels show 101\n";
}
