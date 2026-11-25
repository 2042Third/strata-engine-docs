// How many levels a bloom radius of 64 / 1080 of the image's height uses at four heights.
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <initializer_list>

int main()
{
	const float radius = 64.0f / 1080.0f;
	const float maxLevels = 8.0f;
	for (const int height : { 720, 1080, 2160, 8640 })
	{
		float span = std::log2(radius * static_cast<float>(height));
		if (std::abs(span - std::round(span)) < 1e-4f) // a span within 1e-4 of a whole number is that number
			span = std::round(span);
		span = std::clamp(span, 1.0f, maxLevels);
		const float levels = std::ceil(span);
		std::printf("%4d rows: span %.3f, %.0f levels, deepest weight %.3f\n", height, span, levels, span - (levels - 1.0f));
	}
	return 0;
}
