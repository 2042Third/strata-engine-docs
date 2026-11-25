// A shadow edge at a fixed place in the world, seen from a square that follows a slow camera: with and without snapping.
#include <cmath>
#include <cstdio>

constexpr double c_Texel = 0.0069; // About the texel of the first Medium cascade, in meters
constexpr double c_MapSize = 2048.0;
constexpr double c_EdgeX = 1.0;    // The shadow edge's place in the world, in meters

// Where the edge falls inside the square, in texels from the square's left side.
double GetEdgeTexel(double squareCenter)
{
	const double left = squareCenter - 0.5 * c_Texel * c_MapSize;
	return (c_EdgeX - left) / c_Texel;
}

int main()
{
	std::printf("camera x   unsnapped edge   snapped edge\n");
	for (int step = 0; step < 6; step++)
	{
		const double cameraX = 0.0031 * step;
		const double snapped = std::floor(cameraX / c_Texel) * c_Texel;
		const double loose = GetEdgeTexel(cameraX);
		const double fixedEdge = GetEdgeTexel(snapped);
		std::printf("%.4f m    %9.3f       %9.3f\n", cameraX, loose - std::floor(loose), fixedEdge - std::floor(fixedEdge));
	}
	return 0;
}
