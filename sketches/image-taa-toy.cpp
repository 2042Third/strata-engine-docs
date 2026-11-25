// A temporal anti-aliasing toy in one dimension: a row of 16 pixels and a bar 3.4 pixels wide.
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <vector>

constexpr int c_Width = 16;
constexpr int c_Phases = 8;

float RadicalInverse(int index, int base)
{
	float result = 0.0f;
	float scale = 1.0f / static_cast<float>(base);
	for (; index > 0; index /= base)
	{
		result += static_cast<float>(index % base) * scale;
		scale /= static_cast<float>(base);
	}
	return result;
}

// One sample per pixel, taken at the pixel's centre moved by the jitter: inside the bar is 1, outside it is 0.
std::vector<float> Render(float left, float jitter)
{
	std::vector<float> image(c_Width);
	for (int x = 0; x < c_Width; x++)
	{
		const float position = static_cast<float>(x) + 0.5f + jitter;
		image[x] = (position >= left && position < left + 3.4f) ? 1.0f : 0.0f;
	}
	return image;
}

// The history at a position in pixels: a linear blend of the two texels whose centres surround it.
float SampleHistory(const std::vector<float>& history, float position)
{
	const float shifted = std::clamp(position - 0.5f, 0.0f, static_cast<float>(c_Width - 1));
	const int first = static_cast<int>(std::floor(shifted));
	const int second = std::min(first + 1, c_Width - 1);
	const float fraction = shifted - static_cast<float>(first);
	return history[first] * (1.0f - fraction) + history[second] * fraction;
}

// Reproject (read where the pixel was one frame ago), clamp to the neighbours' range, blend.
std::vector<float> Resolve(const std::vector<float>& current, const std::vector<float>& history, float motion, bool clamp, float weight)
{
	std::vector<float> result(c_Width);
	for (int x = 0; x < c_Width; x++)
	{
		float low = current[x];
		float high = current[x];
		for (int offset = -1; offset <= 1; offset++)
		{
			const float neighbour = current[std::clamp(x + offset, 0, c_Width - 1)];
			low = std::min(low, neighbour);
			high = std::max(high, neighbour);
		}
		float past = SampleHistory(history, static_cast<float>(x) + 0.5f - motion);
		if (clamp)
			past = std::clamp(past, low, high);
		result[x] = past * (1.0f - weight) + current[x] * weight;
	}
	return result;
}

// Frame n (counting from 1) weighs 1 / n until the weight reaches 1/8, as the engine's frames after a reset do.
std::vector<float> Run(float left, float speed, float motion, bool clamp, int frames)
{
	std::vector<float> history;
	for (int frame = 0; frame < frames; frame++)
	{
		const float jitter = RadicalInverse(frame % c_Phases + 1, 2) - 0.5f;
		const std::vector<float> current = Render(left + speed * static_cast<float>(frame), jitter);
		const float weight = std::max(1.0f / static_cast<float>(frame + 1), 1.0f / 8.0f);
		history = frame == 0 ? current : Resolve(current, history, motion, clamp, weight);
	}
	return history;
}

void Print(const char* label, const std::vector<float>& image)
{
	std::printf("%-22s", label);
	for (const float value : image)
		std::printf("%d", static_cast<int>(std::lround(value * 9.0f)));
	std::printf("\n");
}

int main()
{
	Print("still, 1 frame", Run(4.3f, 0.0f, 0.0f, true, 1));
	Print("still, 8 frames", Run(4.3f, 0.0f, 0.0f, true, 8));
	Print("still, 40 frames", Run(4.3f, 0.0f, 0.0f, true, 40));
	Print("moving, current frame", Render(2.0f + 7.0f, RadicalInverse(8, 2) - 0.5f));
	Print("moving, motion known", Run(2.0f, 1.0f, 1.0f, true, 8));
	Print("moving, no motion", Run(2.0f, 1.0f, 0.0f, false, 8));
	Print("moving, no motion+clamp", Run(2.0f, 1.0f, 0.0f, true, 8));
	return 0;
}
