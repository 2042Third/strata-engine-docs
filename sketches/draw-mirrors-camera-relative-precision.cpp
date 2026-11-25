#include <cstdio>
#include <initializer_list>

int main()
{
	// An instance 100 km from the world's origin and a camera 1.5 m from it: both exact as 32-bit floats.
	const float translation = 100003.0f;
	const float camera = 100001.5f;
	std::printf("vertex  world-space error  camera-relative error (millimeters)\n");
	for (const float local : { 0.001f, 0.002f, 0.004f, 0.006f, 0.008f })
	{
		const float world = translation + local;
		const float worldError = (world - camera - 1.5f - local) * 1000.0f;
		const float relative = (translation - camera) + local;
		const float relativeError = (relative - 1.5f - local) * 1000.0f;
		std::printf("%.3f   %+.3f              %+.3f\n", static_cast<double>(local), static_cast<double>(worldError),
			static_cast<double>(relativeError));
	}
	return 0;
}
