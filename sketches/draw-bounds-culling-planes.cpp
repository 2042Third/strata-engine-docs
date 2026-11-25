#include <cmath>
#include <cstdio>

struct Plane { float X, Y, D; }; // Inward normal and distance: inside when X*x + Y*y + D >= 0

int main()
{
	const float k = std::sqrt(0.5f);
	// Left, right, near (y >= 1) and far (y <= 10) of a camera at the origin looking along +y.
	const Plane planes[] = { { k, k, 0.0f }, { -k, k, 0.0f }, { 0.0f, 1.0f, -1.0f }, { 0.0f, -1.0f, 10.0f } };
	const float boxes[][4] = { { -1.0f, 3.0f, 1.0f, 5.0f }, { -2.0f, 0.0f, 2.0f, 2.0f }, { 8.0f, 1.5f, 9.0f, 2.0f }, { -12.0f, 9.5f, -10.5f, 11.0f } };
	for (const float* b : boxes) // Each box: minimum x, minimum y, maximum x, maximum y
	{
		bool inside = true;
		bool outside = false;
		for (const Plane& p : planes)
		{
			const float positive = p.X * (p.X >= 0.0f ? b[2] : b[0]) + p.Y * (p.Y >= 0.0f ? b[3] : b[1]) + p.D;
			const float negative = p.X * (p.X >= 0.0f ? b[0] : b[2]) + p.Y * (p.Y >= 0.0f ? b[1] : b[3]) + p.D;
			if (positive < 0.0f)
				outside = true;
			if (negative < 0.0f)
				inside = false;
		}
		std::printf("box at (%.1f, %.1f): %s\n", b[0], b[1], outside ? "outside" : (inside ? "inside" : "intersecting"));
	}
}
