#include <algorithm>
#include <cmath>
#include <cstdio>
#include <string>
#include <vector>

namespace
{

	constexpr int c_Width = 32;

	// One pixel of a row: its color (0 is black, 1 is white) and the radius of its circle of confusion, in pixels.
	struct Pixel
	{
		float Color;
		float Radius;
	};

	// A white wall far behind the focus (radius 4) with a thin black stripe, and a black card in focus (radius 0) in front of it.
	std::vector<Pixel> MakeRow()
	{
		std::vector<Pixel> row(c_Width, Pixel{ 1.0f, 4.0f });
		for (int x = 12; x < 16; x++)
			row[x] = Pixel{ 0.0f, 0.0f };
		row[26].Color = 0.0f;
		return row;
	}

	// How much a sample whose circle has `radius` covers a pixel `distance` away: all of it inside, fading over the last pixel.
	float Cover(float radius, float distance)
	{
		return std::clamp(radius - distance + 1.0f, 0.0f, 1.0f);
	}

	// Each pixel gathers its neighbors within its own circle. With `useCover` a neighbor counts only when its own circle reaches back.
	std::vector<float> Gather(const std::vector<Pixel>& row, bool useCover)
	{
		std::vector<float> result(row.size());
		for (int x = 0; x < c_Width; x++)
		{
			const int reach = static_cast<int>(std::ceil(row[x].Radius));
			float sum = row[x].Color;
			float total = 1.0f;
			for (int offset = -reach; offset <= reach; offset++)
			{
				if (offset == 0 || std::abs(offset) > row[x].Radius)
					continue;
				const Pixel& sample = row[std::clamp(x + offset, 0, c_Width - 1)];
				const float weight = useCover ? Cover(sample.Radius, static_cast<float>(std::abs(offset))) : 1.0f;
				sum += sample.Color * weight;
				total += weight;
			}
			result[x] = sum / total;
		}
		return result;
	}

	// One digit per pixel: 0 is black, 9 is white.
	std::string Digits(const std::vector<float>& values)
	{
		std::string text;
		for (float value : values)
			text += static_cast<char>('0' + std::lround(value * 9.0f));
		return text;
	}

}

int main()
{
	const std::vector<Pixel> row = MakeRow();
	std::vector<float> sharp;
	for (const Pixel& pixel : row)
		sharp.push_back(pixel.Color);
	std::printf("sharp      %s\n", Digits(sharp).c_str());
	std::printf("no cover   %s\n", Digits(Gather(row, false)).c_str());
	std::printf("with cover %s\n", Digits(Gather(row, true)).c_str());
	return 0;
}
