#include <algorithm>
#include <array>
#include <cmath>
#include <cstdio>

constexpr int c_Width = 12;
constexpr int c_Height = 6;
constexpr float c_Threshold = 0.2f;   // The smallest luma difference that counts as an edge
constexpr float c_BlendWeight = 0.25f; // How far a pixel moves toward the neighbor across its edge

using Image = std::array<std::array<float, c_Width>, c_Height>;

float At(const Image& image, int x, int y)
{
	return image[std::clamp(y, 0, c_Height - 1)][std::clamp(x, 0, c_Width - 1)];
}

Image Smooth(const Image& image)
{
	Image result = image;
	for (int y = 0; y < c_Height; y++)
	{
		for (int x = 0; x < c_Width; x++)
		{
			const float center = At(image, x, y);
			const float neighbors[4] = { At(image, x, y - 1), At(image, x, y + 1), At(image, x - 1, y), At(image, x + 1, y) };
			float across = center;
			for (float neighbor : neighbors)
				if (std::abs(neighbor - center) > std::abs(across - center))
					across = neighbor;
			if (std::abs(across - center) < c_Threshold)
				continue;
			result[y][x] = center + c_BlendWeight * (across - center);
		}
	}
	return result;
}

void Print(const Image& image)
{
	for (const auto& row : image)
	{
		for (float luma : row)
			std::printf("%4ld", std::lround(luma * 100.0f));
		std::printf("\n");
	}
}

int main()
{
	Image image = {};
	for (int y = 0; y < c_Height; y++)
		for (int x = 0; x < c_Width; x++)
			image[y][x] = x < 2 + 2 * y ? 0.9f : 0.1f; // A staircase: bright on the left, 2 pixels more each row
	Print(image);
	std::printf("\n");
	Print(Smooth(image));
	return 0;
}
