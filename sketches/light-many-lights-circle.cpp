#include <algorithm>
#include <cstdio>
#include <vector>

struct ScreenLight
{
	char Name;
	float X;
	float Y;
	float Radius;
};

constexpr int c_TilesX = 16;
constexpr int c_TilesY = 9;
constexpr float c_TileSize = 80.0f;

// The same test as the cluster shader's: the distance from the circle's center to the nearest point of the tile.
bool CircleTouchesTile(const ScreenLight& light, int tileX, int tileY)
{
	const float minX = static_cast<float>(tileX) * c_TileSize;
	const float minY = static_cast<float>(tileY) * c_TileSize;
	const float dx = light.X - std::clamp(light.X, minX, minX + c_TileSize);
	const float dy = light.Y - std::clamp(light.Y, minY, minY + c_TileSize);
	return dx * dx + dy * dy <= light.Radius * light.Radius;
}

int main()
{
	const std::vector<ScreenLight> lights = {
		{ 'A', 100.0f, 100.0f, 50.0f }, { 'B', 640.0f, 360.0f, 200.0f }, { 'C', 1200.0f, 700.0f, 30.0f },
		{ 'D', 645.0f, 365.0f, 10.0f }, { 'E', 90.0f, 90.0f, 30.0f }
	};

	int entries = 0;
	for (const ScreenLight& light : lights)
	{
		int count = 0;
		for (int y = 0; y < c_TilesY; y++)
			for (int x = 0; x < c_TilesX; x++)
				if (CircleTouchesTile(light, x, y))
					count++;
		std::printf("Light %c touches %d tiles\n", light.Name, count);
		entries += count;
	}
	std::printf("Tile entries: %d\n", entries);
	return 0;
}
