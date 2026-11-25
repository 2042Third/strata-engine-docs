// A toy gradient sky: the radiance, in nits, that a viewer sees along a direction of a given height (the y of a unit vector).
#include <algorithm>
#include <cmath>
#include <cstdio>

struct Color
{
	float R;
	float G;
	float B;
};

constexpr Color c_Zenith = { 0.045f, 0.08f, 0.155f };
constexpr Color c_Horizon = { 0.165f, 0.185f, 0.21f };
constexpr Color c_Ground = { 0.055f, 0.05f, 0.045f };

Color Mix(const Color& a, const Color& b, float weight)
{
	return { a.R + (b.R - a.R) * weight, a.G + (b.G - a.G) * weight, a.B + (b.B - a.B) * weight };
}

Color SkyRadiance(float height)
{
	height = std::clamp(height, -1.0f, 1.0f);
	if (height >= 0.0f)
	{
		// Above the horizon the zenith color takes over quickly: within about 15 degrees.
		const float weight = 1.0f - std::pow(1.0f - height, 8.0f);
		return Mix(c_Horizon, c_Zenith, weight);
	}
	// Below it the ground takes over within a few degrees.
	const float weight = 1.0f - std::pow(1.0f + height, 16.0f);
	return Mix(c_Horizon, c_Ground, weight);
}

int main()
{
	const float heights[] = { 1.0f, 0.5f, 0.1f, 0.0f, -0.1f, -0.5f };
	for (const float height : heights)
	{
		const Color color = SkyRadiance(height);
		std::printf("height %5.2f: %.4f %.4f %.4f nits\n", height, color.R, color.G, color.B);
	}
	return 0;
}
