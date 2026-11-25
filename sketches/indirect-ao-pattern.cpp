#include <cstdio>

// How much weight each of the 16 phases of a 4x4 pattern receives from a 5x5 tent kernel centered on one pixel.
int main()
{
	const float tent[5] = { 0.5f, 1.0f, 1.0f, 1.0f, 0.5f };

	bool complete = true;
	for (int centerY = 0; centerY < 4; centerY++)
	{
		for (int centerX = 0; centerX < 4; centerX++)
		{
			float phaseWeight[4][4] = {};
			for (int offsetY = -2; offsetY <= 2; offsetY++)
			{
				for (int offsetX = -2; offsetX <= 2; offsetX++)
				{
					// The tap's phase is its pixel's place in the 4x4 block; +8 keeps the remainder positive.
					const int phaseX = (centerX + offsetX + 8) % 4;
					const int phaseY = (centerY + offsetY + 8) % 4;
					phaseWeight[phaseY][phaseX] += tent[offsetX + 2] * tent[offsetY + 2];
				}
			}
			for (int phaseY = 0; phaseY < 4; phaseY++)
				for (int phaseX = 0; phaseX < 4; phaseX++)
					complete = complete && phaseWeight[phaseY][phaseX] == 1.0f;

			if (centerX == 1 && centerY == 2)
			{
				std::printf("weights by phase for the pixel at cell (1, 2):\n");
				for (int phaseY = 0; phaseY < 4; phaseY++)
					std::printf("%.1f %.1f %.1f %.1f\n", static_cast<double>(phaseWeight[phaseY][0]), static_cast<double>(phaseWeight[phaseY][1]),
						static_cast<double>(phaseWeight[phaseY][2]), static_cast<double>(phaseWeight[phaseY][3]));
			}
		}
	}
	std::printf("every phase weighs 1 for every center: %s\n", complete ? "yes" : "no");
	return 0;
}
