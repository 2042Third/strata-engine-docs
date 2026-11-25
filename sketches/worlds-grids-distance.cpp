#include <algorithm>
#include <cmath>
#include <cstdio>

double Distance(double minX, double minZ, double maxX, double maxZ, double x, double z)
{
	const double dx = std::max({ minX - x, 0.0, x - maxX });
	const double dz = std::max({ minZ - z, 0.0, z - maxZ });
	return std::sqrt(dx * dx + dz * dz);
}

int main()
{
	// The square of cell (2, -1) of a layer of 32 m cells whose grid starts at (200, -100).
	std::printf("inside: %.1f\n", Distance(264.0, -132.0, 296.0, -100.0, 270.0, -110.0));
	std::printf("beside: %.1f\n", Distance(264.0, -132.0, 296.0, -100.0, 300.0, -100.0));
	std::printf("corner: %.1f\n", Distance(264.0, -132.0, 296.0, -100.0, 299.0, -96.0));
}
