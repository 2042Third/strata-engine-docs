#include <algorithm>
#include <cmath>
#include <cstdio>

// A camera looking along -Z (yaw 0, pitch 0) with a 60 degree vertical field of view, at a 16:9 view.
constexpr double c_Margin = 1.1;
constexpr double c_Near = 0.1;

int main()
{
	const double tanVertical = std::tan(30.0 * 3.14159265358979323846 / 180.0);
	const double tanHorizontal = tanVertical * 16.0 / 9.0;
	// A box 20 units wide and 1 unit deep and tall, centered on the origin.
	const double half[3] = { 10.0, 0.5, 0.5 };

	// Focus: the bounding sphere against the narrower half field of view (30 degrees: sin = 0.5).
	const double radius = std::sqrt(half[0] * half[0] + half[1] * half[1] + half[2] * half[2]);
	std::printf("focus distance: %.3f\n", radius * c_Margin / 0.5);

	// FitBounds: every corner must lie inside the view, so the camera backs off as far as the worst corner needs.
	double distance = 0.0;
	for (int corner = 0; corner < 8; corner++)
	{
		const double x = std::fabs(corner & 1 ? half[0] : -half[0]);
		const double y = std::fabs(corner & 2 ? half[1] : -half[1]);
		const double z = (corner & 4) ? half[2] : -half[2]; // Along the view: positive is away from the camera
		distance = std::max({ distance, c_Margin * x / tanHorizontal - z, c_Margin * y / tanVertical - z, c_Near * 2.0 - z });
	}
	std::printf("fit distance: %.3f\n", distance);
	return 0;
}
