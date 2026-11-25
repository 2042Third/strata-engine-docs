#include <algorithm>
#include <cmath>
#include <cstddef>
#include <cstdio>
#include <initializer_list>
#include <vector>

// A light seen on the screen: its center and its radius, in pixels.
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
constexpr int c_Slices = 24;
constexpr float c_Near = 0.1f;
constexpr float c_Far = 1000.0f;

int ClampTile(float pixel, int count)
{
	return std::clamp(static_cast<int>(std::floor(pixel / c_TileSize)), 0, count - 1);
}

int ExponentialSlice(float depth)
{
	const float scale = static_cast<float>(c_Slices) / std::log(c_Far / c_Near);
	return std::clamp(static_cast<int>(std::log(depth / c_Near) * scale), 0, c_Slices - 1);
}

int LinearSlice(float depth)
{
	return std::clamp(static_cast<int>(depth / (c_Far / static_cast<float>(c_Slices))), 0, c_Slices - 1);
}

int main()
{
	const std::vector<ScreenLight> lights = {
		{ 'A', 100.0f, 100.0f, 50.0f }, { 'B', 640.0f, 360.0f, 200.0f }, { 'C', 1200.0f, 700.0f, 30.0f },
		{ 'D', 645.0f, 365.0f, 10.0f }, { 'E', 90.0f, 90.0f, 30.0f }
	};

	// One list of light names per tile: every tile the light's bounding box touches gets the light.
	std::vector<std::vector<char>> tiles(c_TilesX * c_TilesY);
	int entries = 0;
	for (const ScreenLight& light : lights)
	{
		int count = 0;
		for (int y = ClampTile(light.Y - light.Radius, c_TilesY); y <= ClampTile(light.Y + light.Radius, c_TilesY); y++)
		{
			for (int x = ClampTile(light.X - light.Radius, c_TilesX); x <= ClampTile(light.X + light.Radius, c_TilesX); x++)
			{
				tiles[y * c_TilesX + x].push_back(light.Name);
				count++;
			}
		}
		std::printf("Light %c covers %d tiles\n", light.Name, count);
		entries += count;
	}
	std::printf("Tile entries: %d (every light against every tile: %d tests)\n", entries, static_cast<int>(lights.size()) * c_TilesX * c_TilesY);

	size_t busiest = 0;
	for (size_t index = 0; index < tiles.size(); index++)
		if (tiles[index].size() > tiles[busiest].size())
			busiest = index;
	std::printf("Busiest tile (%d,%d) holds %d lights\n", static_cast<int>(busiest) % c_TilesX, static_cast<int>(busiest) / c_TilesX,
		static_cast<int>(tiles[busiest].size()));

	const int pixelX = ClampTile(645.0f, c_TilesX);
	const int pixelY = ClampTile(365.0f, c_TilesY);
	std::printf("Pixel (645,365) is in tile (%d,%d) and loops over:", pixelX, pixelY);
	for (const char name : tiles[pixelY * c_TilesX + pixelX])
		std::printf(" %c", name);
	std::printf("\n");

	for (const float depth : { 0.5f, 5.0f, 50.0f, 480.0f })
		std::printf("Depth %.1f m: exponential slice %d, linear slice %d\n", depth, ExponentialSlice(depth), LinearSlice(depth));

	const size_t clusters = static_cast<size_t>(c_TilesX) * c_TilesY * c_Slices;
	std::printf("Clusters: %zu, buffer: %zu uints\n", clusters, clusters * 257);
	return 0;
}
