#include <algorithm>
#include <cstdio>

constexpr float c_OnEdge = 128.0f / 255.0f;
constexpr float c_PerTexel = 32.0f / 255.0f;
constexpr float c_TexelsPerEm = 32.0f;

float Smoothstep(float low, float high, float value)
{
	const float t = std::clamp((value - low) / (high - low), 0.0f, 1.0f);
	return t * t * (3.0f - 2.0f * t);
}

// Coverage of a pixel whose centre lies offsetPixels inside an axis-aligned edge, for text of the given size in pixels per em.
float Coverage(float pixelsPerEm, float offsetPixels)
{
	const float texelsPerPixel = c_TexelsPerEm / pixelsPerEm;
	const float change = c_PerTexel * texelsPerPixel; // What fwidth reports: the distance value's change per pixel
	const float width = std::max(change * 0.7f, 1e-4f);
	return Smoothstep(c_OnEdge - width, c_OnEdge + width, c_OnEdge + change * offsetPixels);
}

int main()
{
	const float sizes[] = { 8.0f, 32.0f, 128.0f };
	for (const float size : sizes)
	{
		std::printf("%5.0f px per em:", size);
		for (float offset = -1.0f; offset <= 1.01f; offset += 0.5f)
			std::printf(" %.2f", Coverage(size, offset));
		std::printf("\n");
	}
	return 0;
}
