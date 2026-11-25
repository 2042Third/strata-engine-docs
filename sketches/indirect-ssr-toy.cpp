// A screen-space reflection march in a side view: a polished floor and a wall, one ray, with bisection.
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <vector>

constexpr float c_Focal = 500.0f; // Pixels from the eye to the screen
constexpr float c_CenterRow = 500.0f;
constexpr float c_WallDistance = 8.0f;

// The depth buffer: the view distance of the surface each row shows (floor at height -1, wall at distance 8, up to height 3).
std::vector<float> MakeDepthBuffer()
{
	std::vector<float> depth(1000, 1.0e30f);
	for (int row = 0; row < 1000; row++)
	{
		const float slope = (c_CenterRow - (static_cast<float>(row) + 0.5f)) / c_Focal; // Height over distance
		const float floorDistance = slope < 0.0f ? -1.0f / slope : 1.0e30f;
		if (floorDistance < c_WallDistance)
			depth[row] = floorDistance;
		else if (slope * c_WallDistance <= 3.0f)
			depth[row] = c_WallDistance;
	}
	return depth;
}

// Whether the ray's point (row and 1 / distance) lies behind the surface its row shows, by less than the thickness.
bool IsBehind(const std::vector<float>& depth, float row, float inverse, float previousDistance)
{
	const float distance = 1.0f / inverse;
	const float scene = depth[static_cast<size_t>(std::clamp(row, 0.0f, 999.0f))];
	const float thickness = std::abs(distance - previousDistance) + std::max(0.05f, 0.02f * distance);
	return distance > scene && distance - scene < thickness;
}

int main()
{
	const std::vector<float> depth = MakeDepthBuffer();
	// The floor point at distance 4 reflects the eye's ray upward: in screen space a straight line in (row, 1 / distance).
	const float startRow = 625.0f;
	const float startInverse = 0.25f;
	const float deltaRow = 375.0f - startRow; // To the far plane
	const float deltaInverse = 0.0f - startInverse;
	const float pixels = std::abs(deltaRow);
	const int steps = 12;
	float previousAlong = 0.0f;
	float previousDistance = 1.0f / startInverse;
	float hitAlong = -1.0f;
	for (int index = 0; index < steps; index++)
	{
		const float fraction = (static_cast<float>(index) + 0.5f) / static_cast<float>(steps);
		const float along = std::max(fraction * fraction, 1.0f / pixels);
		const float row = startRow + deltaRow * along;
		const float inverse = startInverse + deltaInverse * along;
		const bool behind = IsBehind(depth, row, inverse, previousDistance);
		std::printf("step %2d along %.3f row %6.1f ray %6.2f m surface %6.2f m %s\n", index, along, row, 1.0f / inverse,
			std::min(depth[static_cast<size_t>(row)], 99.99f), behind ? "hit" : "-");
		if (behind)
		{
			hitAlong = along;
			break;
		}
		previousAlong = along;
		previousDistance = 1.0f / inverse;
	}
	if (hitAlong < 0.0f)
		return 0;
	float low = previousAlong;
	float high = hitAlong;
	for (int index = 0; index < 6; index++)
	{
		const float middle = 0.5f * (low + high);
		const float distance = 1.0f / (startInverse + deltaInverse * middle);
		const float scene = depth[static_cast<size_t>(startRow + deltaRow * middle)];
		(distance > scene ? high : low) = middle;
	}
	std::printf("hit at row %.1f, surface %.2f m; the wall point at height 0 is row 500.0 at 8.00 m\n", startRow + deltaRow * high,
		depth[static_cast<size_t>(startRow + deltaRow * high)]);
	return 0;
}
