// A toy cascade layout: the splits, the sphere around each slice and the texel size, for one lens.
#include <algorithm>
#include <cmath>
#include <cstdio>

constexpr int c_CascadeCount = 4;
constexpr float c_SplitStart = 1.5f;
constexpr float c_MaxFirstSplit = 7.5f;
constexpr float c_ShadowDistance = 80.0f;
constexpr float c_Distribution = 0.9f;
constexpr float c_Blend = 0.1f;
constexpr int c_MapSize = 2048;
constexpr int c_MarginTexels = 68; // Twice the filter's reach of 33 texels plus one snapping texel
constexpr int c_ScreenRows = 1080;

float GetSplit(int index)
{
	if (index + 1 >= c_CascadeCount)
		return c_ShadowDistance;
	const float fraction = static_cast<float>(index + 1) / static_cast<float>(c_CascadeCount);
	const float logarithmic = c_SplitStart * std::pow(c_ShadowDistance / c_SplitStart, fraction);
	const float uniform = c_SplitStart + (c_ShadowDistance - c_SplitStart) * fraction;
	const float split = c_Distribution * logarithmic + (1.0f - c_Distribution) * uniform;
	return index == 0 ? std::min(split, c_MaxFirstSplit) : split;
}

// The radius of the smallest sphere around the slice [sliceNear, sliceFar] of a 60 degree, 16:9 view.
float GetSphereRadius(float sliceNear, float sliceFar)
{
	const float tanHalf = std::tan(0.5f * 3.14159265f / 3.0f);
	const float reach = tanHalf * std::sqrt(1.0f + (16.0f / 9.0f) * (16.0f / 9.0f));
	const float nearHalf = reach * sliceNear;
	const float farHalf = reach * sliceFar;
	// The sphere's center on the view axis, equally far from the near and far corners, or at the far end.
	float center = (sliceFar * sliceFar - sliceNear * sliceNear + farHalf * farHalf - nearHalf * nearHalf) / (2.0f * (sliceFar - sliceNear));
	center = std::clamp(center, sliceNear, sliceFar);
	const float extent = std::max(std::hypot(center - sliceNear, nearHalf), std::hypot(sliceFar - center, farHalf));
	return std::ceil(extent * 16.0f) / 16.0f;
}

int main()
{
	const float tanHalf = std::tan(0.5f * 3.14159265f / 3.0f);
	float sliceNear = 0.1f;
	float previousSplit = 0.0f;
	for (int cascade = 0; cascade < c_CascadeCount; cascade++)
	{
		const float split = GetSplit(cascade);
		const float radius = GetSphereRadius(sliceNear, split);
		const float texel = 2.0f * radius / static_cast<float>(c_MapSize - c_MarginTexels);
		const float pixel = 2.0f * split * tanHalf / static_cast<float>(c_ScreenRows);
		std::printf("cascade %d: %6.2f to %5.2f m, radius %6.3f m, texel %5.2f mm, %.2f pixels per texel\n", cascade, sliceNear, split, radius, texel * 1000.0f, texel / pixel);
		sliceNear = std::max(split - c_Blend * (split - previousSplit), 0.1f);
		previousSplit = split;
	}
	return 0;
}
