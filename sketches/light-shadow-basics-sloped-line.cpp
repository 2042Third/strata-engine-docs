// A shadow map in two dimensions: the light shines straight down and a "texel" is a column of width 0.5.
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <vector>

struct Surface
{
	float X0;
	float X1;
	float Y0;
	float Slope;
};

struct Biases
{
	const char* Name;
	float Depth;  // in texels, toward the light
	float Slope;  // in texels of depth per texel of slope, away from the light (the rasterizer's)
	float Normal; // in texels, along the receiver's normal
	bool Plane;   // compare against the receiver's own plane at the texel center
};

constexpr float c_Texel = 0.5f;
constexpr int c_TexelCount = 20;

float HeightAt(const Surface& surface, float x)
{
	return surface.Y0 + surface.Slope * (x - surface.X0);
}

// The shadow map stores, per texel, the highest surface at the texel's center (nearest to the light).
std::vector<float> RenderMap(const std::vector<Surface>& surfaces, float slopeBias)
{
	std::vector<float> map(c_TexelCount, -1000.0f);
	for (int texel = 0; texel < c_TexelCount; texel++)
	{
		const float center = (static_cast<float>(texel) + 0.5f) * c_Texel;
		for (const Surface& surface : surfaces)
			if (center >= surface.X0 && center <= surface.X1)
				map[texel] = std::max(map[texel], HeightAt(surface, center) - slopeBias * c_Texel * std::fabs(surface.Slope));
	}
	return map;
}

// Counts the samples of one receiver surface that the map wrongly or rightly puts in shadow.
int CountShadowed(const std::vector<float>& map, const Surface& receiver, float from, float to, int samples, const Biases& biases)
{
	const float length = std::sqrt(1.0f + receiver.Slope * receiver.Slope);
	int shadowed = 0;
	for (int sample = 0; sample < samples; sample++)
	{
		const float x = from + (to - from) * (static_cast<float>(sample) + 0.5f) / static_cast<float>(samples);
		const float lookupX = x - receiver.Slope / length * biases.Normal * c_Texel;
		const float lookupY = HeightAt(receiver, x) + 1.0f / length * biases.Normal * c_Texel;
		const int texel = std::clamp(static_cast<int>(std::floor(lookupX / c_Texel)), 0, c_TexelCount - 1);
		float reference = lookupY + biases.Depth * c_Texel;
		if (biases.Plane)
			reference += receiver.Slope * ((static_cast<float>(texel) + 0.5f) * c_Texel - lookupX);
		if (map[texel] > reference)
			shadowed++;
	}
	return shadowed;
}

int main()
{
	const Biases rows[] = { { "all off", 0.0f, 0.0f, 0.0f, false }, { "depth 0.1", 0.1f, 0.0f, 0.0f, false },
		{ "depth 1", 1.0f, 0.0f, 0.0f, false }, { "slope 1.5", 0.0f, 1.5f, 0.0f, false },
		{ "normal 1.5", 0.0f, 0.0f, 1.5f, false }, { "plane", 0.0f, 0.0f, 0.0f, true } };
	const Surface ramp = { 0.0f, 10.0f, 0.0f, 0.5f };
	const Surface floor = { 0.0f, 10.0f, 0.0f, 0.0f };
	const Surface plate = { 4.0f, 5.0f, 0.3f, 0.0f };
	std::printf("%-11s %-18s %s\n", "bias", "ramp, 1000 lit", "floor under a plate 0.3 above it, 100 dark");
	for (const Biases& biases : rows)
	{
		const int acne = CountShadowed(RenderMap({ ramp }, biases.Slope), ramp, 0.5f, 9.5f, 1000, biases);
		const int kept = CountShadowed(RenderMap({ floor, plate }, biases.Slope), floor, 4.0f, 5.0f, 100, biases);
		std::printf("%-11s %-18d %d\n", biases.Name, acne, kept);
	}
	return 0;
}
