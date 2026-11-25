// A grid: as many columns as the width holds, fixed cells, and a row spacing that differs from the column spacing.
#include <algorithm>
#include <cmath>
#include <cstdio>

int main()
{
	const float width = 350.0f;
	const float cell = 100.0f;
	const float spacingX = 10.0f;
	const float spacingY = 20.0f;
	const int children = 7;

	const int columns = std::max(1, static_cast<int>(std::floor((width + spacingX) / (cell + spacingX) + 1e-4f)));
	std::printf("columns=%d rows=%d\n", columns, (children + columns - 1) / columns);
	for (int index = 0; index < children; index++)
	{
		const float x = static_cast<float>(index % columns) * (cell + spacingX);
		const float y = static_cast<float>(index / columns) * (cell + spacingY);
		std::printf("cell %d at x=%.0f y=%.0f\n", index, x, y);
	}
}
