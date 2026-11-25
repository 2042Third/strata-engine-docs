// The same camera move seen by points at three depths: nearer points move farther on screen.
#include <array>
#include <cstdio>

namespace
{

	// Screen x in UV for a point at `pointX` and `depth` in front of a camera at `cameraX` (field of view 90 degrees).
	float ScreenX(float pointX, float cameraX, float depth)
	{
		return ((pointX - cameraX) / depth) * 0.5f + 0.5f;
	}

}

int main()
{
	const float width = 1280.0f;
	const std::array<float, 3> depths = { 2.0f, 4.0f, 8.0f };
	for (const float depth : depths)
	{
		const float motion = ScreenX(1.0f, 0.4f, depth) - ScreenX(1.0f, 0.0f, depth);
		std::printf("depth %.0f: %+.1f pixels\n", depth, motion * width);
	}
	return 0;
}
