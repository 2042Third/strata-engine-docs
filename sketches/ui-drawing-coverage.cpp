#include <algorithm>
#include <cmath>
#include <cstdio>

// The fragment shader's rounded rect: the signed distance of a pixel center to the edge, and the coverage it gives.
float GetDistance(float localX, float localY, float halfX, float halfY, float radius)
{
	radius = std::min(radius, std::min(halfX, halfY));
	const float qx = std::fabs(localX) - (halfX - radius);
	const float qy = std::fabs(localY) - (halfY - radius);
	const float outside = std::sqrt(std::max(qx, 0.0f) * std::max(qx, 0.0f) + std::max(qy, 0.0f) * std::max(qy, 0.0f));
	return outside + std::min(std::max(qx, qy), 0.0f) - radius;
}

float GetCoverage(float distance)
{
	return std::clamp(0.5f - distance, 0.0f, 1.0f);
}

int main()
{
	// A 20 by 20 pixel rect with corner radius 6: the pixel centers on its diagonal, from the corner inward.
	for (int pixel = 0; pixel < 4; pixel++)
	{
		const float local = -10.0f + static_cast<float>(pixel) + 0.5f;
		const float distance = GetDistance(local, local, 10.0f, 10.0f, 6.0f);
		std::printf("pixel %d: distance %.3f, coverage %.3f\n", pixel, distance, GetCoverage(distance));
	}
	return 0;
}
