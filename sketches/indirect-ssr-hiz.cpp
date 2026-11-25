// A hierarchical march along a receding floor, in one dimension, against a linear march: how many reads each needs.
#include <cstdio>

constexpr int c_Pixels = 1024;
constexpr int c_Levels = 10;

// The floor's view distance at a pixel along the ray's way: it recedes by 0.1 m a pixel.
float FloorDistance(int pixel)
{
	return 10.0f + 0.1f * static_cast<float>(pixel);
}

// The ray runs just in front of the floor, 0.05 m nearer than the surface at its own pixel.
float RayDistance(int pixel)
{
	return FloorDistance(pixel) - 0.05f;
}

// The nearest distance inside the aligned cell of 2^level pixels that holds `pixel`: the floor recedes, so its first pixel.
float NearestInCell(int pixel, int level)
{
	return FloorDistance((pixel >> level) << level);
}

// Reads until the ray has crossed the floor's pixels. A ray that runs diagonally over the screen enters each new cell
// `entryShift` pixels past its edge (the rows of the coarse grid and the ray do not line up).
int CountHierarchicalReads(int entryShift)
{
	int reads = 0;
	int level = c_Levels;
	int pixel = entryShift;
	while (pixel < c_Pixels && reads < 4096)
	{
		reads++;
		if (RayDistance(pixel) < NearestInCell(pixel, level))
		{
			pixel = (((pixel >> level) + 1) << level) + entryShift; // In front of everything in the cell: skip it
			level = level < c_Levels ? level + 1 : level;
		}
		else if (level > 0)
			level--; // Something in the cell may be nearer than the ray: look closer
		else
			break; // A single pixel in front of the ray: a hit
	}
	return reads;
}

int main()
{
	std::printf("floor receding 0.1 m a pixel, ray 0.05 m in front of it, %d pixels long\n", c_Pixels);
	std::printf("linear march of 32 steps: 32 reads\n");
	std::printf("hierarchical march, entering each cell on its edge: %d reads\n", CountHierarchicalReads(0));
	std::printf("hierarchical march, entering each cell 1 pixel in: %d reads\n", CountHierarchicalReads(1));
	return 0;
}
