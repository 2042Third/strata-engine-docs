// The tilt of a flat normal stored as 8 bits (128/255) against one stored exactly (0.5), as the shader decodes it.
#include <cmath>
#include <cstdio>

namespace
{

	// The angle in degrees between the decoded normal and straight up for a texture that stores (texel, texel, 1).
	double GetTilt(double texel)
	{
		const double x = texel * 2.0 - 1.0;
		const double y = x;
		const double z = std::sqrt(1.0 - (x * x + y * y)); // Z is rebuilt from X and Y, as the shader does
		const double sideways = std::sqrt(x * x + y * y);
		return std::atan2(sideways, z) * 180.0 / 3.14159265358979;
	}

}

int main()
{
	std::printf("8 bits, 128/255: x = %.6f, tilt %.4f degrees\n", 128.0 / 255.0 * 2.0 - 1.0, GetTilt(128.0 / 255.0));
	std::printf("exact 0.5:       x = %.6f, tilt %.4f degrees\n", 0.5 * 2.0 - 1.0, GetTilt(0.5));
	return 0;
}
