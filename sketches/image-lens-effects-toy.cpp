// A toy bloom: a box-filtered pyramid, down and then up.
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <vector>

struct Image
{
	int Size = 0;
	std::vector<float> Pixels;
};

static Image MakeImage(int size)
{
	return Image{ size, std::vector<float>(static_cast<size_t>(size) * size, 0.0f) };
}

static float At(const Image& image, int x, int y)
{
	x = std::clamp(x, 0, image.Size - 1);
	y = std::clamp(y, 0, image.Size - 1);
	return image.Pixels[y * image.Size + x];
}

// Each pixel of the result is the mean of a 2x2 box of the source: the box filter.
static Image Downsample(const Image& source)
{
	Image result = MakeImage(source.Size / 2);
	for (int y = 0; y < result.Size; y++)
		for (int x = 0; x < result.Size; x++)
			result.Pixels[y * result.Size + x] = 0.25f * (At(source, 2 * x, 2 * y) + At(source, 2 * x + 1, 2 * y) + At(source, 2 * x, 2 * y + 1) + At(source, 2 * x + 1, 2 * y + 1));
	return result;
}

// Bilinear read: x and y count texels, and a texel's center is a whole number.
static float Bilinear(const Image& image, float x, float y)
{
	const int x0 = static_cast<int>(std::floor(x));
	const int y0 = static_cast<int>(std::floor(y));
	const float fx = x - static_cast<float>(x0);
	const float fy = y - static_cast<float>(y0);
	const float top = At(image, x0, y0) * (1.0f - fx) + At(image, x0 + 1, y0) * fx;
	const float bottom = At(image, x0, y0 + 1) * (1.0f - fx) + At(image, x0 + 1, y0 + 1) * fx;
	return top * (1.0f - fy) + bottom * fy;
}

static float Mean(const Image& image)
{
	float sum = 0.0f;
	for (const float pixel : image.Pixels)
		sum += pixel;
	return sum / static_cast<float>(image.Pixels.size());
}

int main()
{
	constexpr int c_Levels = 4;
	std::vector<Image> levels = { MakeImage(16) };
	levels[0].Pixels[8 * 16 + 8] = 16.0f; // one bright pixel
	for (int level = 1; level < c_Levels; level++)
		levels.push_back(Downsample(levels[level - 1]));
	for (int level = 0; level < c_Levels; level++)
		std::printf("level %d: %2dx%-2d mean %.4f peak %.3f\n", level, levels[level].Size, levels[level].Size, Mean(levels[level]), *std::max_element(levels[level].Pixels.begin(), levels[level].Pixels.end()));

	// Upsample: each level adds the smaller glow, read bilinearly, to its own pixels.
	Image glow = levels[c_Levels - 1];
	for (int level = c_Levels - 2; level >= 0; level--)
	{
		Image sum = levels[level];
		for (int y = 0; y < sum.Size; y++)
			for (int x = 0; x < sum.Size; x++)
				sum.Pixels[y * sum.Size + x] += Bilinear(glow, (static_cast<float>(x) + 0.5f) / 2.0f - 0.5f, (static_cast<float>(y) + 0.5f) / 2.0f - 0.5f);
		glow = sum;
	}
	std::printf("glow mean %.4f, divided by %d levels %.4f\n", Mean(glow), c_Levels, Mean(glow) / c_Levels);
	std::printf("row 8 of the glow, divided by %d:", c_Levels);
	for (int x = 0; x < glow.Size; x++)
		std::printf(" %.2f", glow.Pixels[8 * glow.Size + x] / c_Levels);
	std::printf("\n");
	return 0;
}
