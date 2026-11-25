#include <algorithm>
#include <cmath>
#include <cstdio>
#include <initializer_list>

int main()
{
	const float maxLengthShare = 0.02f;
	for (const int height : { 720, 1080, 2160 })
	{
		const float maxLength = maxLengthShare * static_cast<float>(height);
		const float minLength = static_cast<float>(height) / 1080.0f;
		const int tileSize = std::max(8, static_cast<int>(std::ceil(maxLength * 0.5f)));
		std::printf("%d rows: longest %.1f px, shortest %.2f px, tile %d px\n", height, maxLength, minLength, tileSize);
	}
	return 0;
}
