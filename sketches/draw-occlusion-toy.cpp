// A toy farthest-depth pyramid and an occlusion test, on the CPU. Reversed Z: 1 is near, 0 is far.
#include <algorithm>
#include <cstdio>
#include <vector>

struct Level
{
	int Width = 0;
	int Height = 0;
	std::vector<float> Depth;

	float At(int x, int y) const { return Depth[static_cast<size_t>(y) * Width + x]; }
};

// One level from its source: each texel takes the smallest (farthest) depth of the source texels it covers.
// The last row and column also cover every source texel past them.
Level Reduce(const Level& source, int width, int height, int reduction)
{
	Level level;
	level.Width = width;
	level.Height = height;
	for (int y = 0; y < height; y++)
	{
		for (int x = 0; x < width; x++)
		{
			int lastX = x == width - 1 ? source.Width - 1 : std::min(x * reduction + reduction - 1, source.Width - 1);
			int lastY = y == height - 1 ? source.Height - 1 : std::min(y * reduction + reduction - 1, source.Height - 1);
			float farthest = 1.0f;
			for (int sy = y * reduction; sy <= lastY; sy++)
				for (int sx = x * reduction; sx <= lastX; sx++)
					farthest = std::min(farthest, source.At(sx, sy));
			level.Depth.push_back(farthest);
		}
	}
	return level;
}

std::vector<Level> BuildPyramid(const Level& depth)
{
	std::vector<Level> levels;
	levels.push_back(Reduce(depth, (depth.Width + 1) / 2, (depth.Height + 1) / 2, 2));
	while (levels.back().Width > 1 || levels.back().Height > 1)
	{
		const Level& above = levels.back();
		levels.push_back(Reduce(above, std::max(above.Width / 2, 1), std::max(above.Height / 2, 1), 2));
	}
	return levels;
}

// The finest level where the pixel rectangle covers at most 2x2 texels; prints what the test reads.
bool IsOccluded(const std::vector<Level>& levels, int minX, int minY, int maxX, int maxY, float nearest)
{
	int level = 0;
	int lowX = minX >> 1, lowY = minY >> 1, highX = maxX >> 1, highY = maxY >> 1;
	while (level + 1 < static_cast<int>(levels.size()) && (highX - lowX > 1 || highY - lowY > 1))
	{
		level++;
		int lastX = std::max(levels[0].Width >> level, 1) - 1;
		int lastY = std::max(levels[0].Height >> level, 1) - 1;
		lowX = std::min(minX >> (level + 1), lastX);
		lowY = std::min(minY >> (level + 1), lastY);
		highX = std::min(maxX >> (level + 1), lastX);
		highY = std::min(maxY >> (level + 1), lastY);
	}
	const Level& texels = levels[level];
	float farthest = std::min(std::min(texels.At(lowX, lowY), texels.At(highX, lowY)), std::min(texels.At(lowX, highY), texels.At(highX, highY)));
	std::printf("rect (%d,%d)-(%d,%d): level %d, texels (%d,%d)-(%d,%d), farthest %.1f, nearest %.1f\n", minX, minY, maxX, maxY, level, lowX, lowY, highX, highY, farthest, nearest);
	return nearest < farthest;
}

int main()
{
	// A 9x5 depth buffer: a wall of depth 0.6 on columns 0 to 5, far background 0.1, one hole in the wall.
	Level depth;
	depth.Width = 9;
	depth.Height = 5;
	for (int y = 0; y < depth.Height; y++)
		for (int x = 0; x < depth.Width; x++)
			depth.Depth.push_back(x < 6 ? 0.6f : 0.1f);
	depth.Depth[2 * 9 + 2] = 0.0f;

	std::vector<Level> pyramid = BuildPyramid(depth);
	for (size_t i = 0; i < pyramid.size(); i++)
	{
		std::printf("level %zu is %d x %d:", i, pyramid[i].Width, pyramid[i].Height);
		for (float value : pyramid[i].Depth)
			std::printf(" %.1f", value);
		std::printf("\n");
	}
	std::printf("occluded: %d\n", IsOccluded(pyramid, 0, 0, 1, 1, 0.3f));
	std::printf("occluded: %d\n", IsOccluded(pyramid, 0, 0, 3, 3, 0.3f));
	std::printf("occluded: %d\n", IsOccluded(pyramid, 5, 0, 8, 4, 0.3f));
	return 0;
}
