#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <map>
#include <string>
#include <utility>

constexpr int c_Size = 8;
constexpr int c_Padding = 4;
constexpr float c_OnEdge = 128.0f;
constexpr float c_PerTexel = c_OnEdge / c_Padding;

// A glyph as a bitmap: '#' is inside the outline.
const char* const c_Letter[c_Size] = { "........", ".##.....", ".##.....", ".##.....", ".##.....", ".#####..", ".#####..", "........" };

bool IsInside(int x, int y)
{
	return x >= 0 && y >= 0 && x < c_Size && y < c_Size && c_Letter[y][x] == '#';
}

// Brute force: search every texel for the nearest one on the other side of the outline.
uint8_t DistanceValue(int x, int y)
{
	const bool inside = IsInside(x, y);
	float nearest = 1000.0f;
	for (int sy = -c_Padding - 1; sy < c_Size + c_Padding + 1; sy++)
	{
		for (int sx = -c_Padding - 1; sx < c_Size + c_Padding + 1; sx++)
		{
			if (IsInside(sx, sy) != inside)
				nearest = std::min(nearest, std::hypot(float(sx - x), float(sy - y)));
		}
	}
	// The outline lies halfway between the two texels, so the distance to it is half a texel shorter.
	const float signedDistance = (inside ? 1.0f : -1.0f) * (nearest - 0.5f);
	return uint8_t(std::clamp(c_OnEdge + c_PerTexel * signedDistance, 0.0f, 255.0f));
}

struct ToyFont
{
	std::map<char, float> Advance = { { 'A', 0.65f }, { 'V', 0.62f } };
	std::map<std::pair<char, char>, float> Kerning = { { { 'A', 'V' }, -0.08f } };
};

// Shapes one line: each pen position is the sum of the earlier advances and kerning pairs, in em.
void ShapeLine(const ToyFont& font, const std::string& text)
{
	float pen = 0.0f;
	for (size_t index = 0; index < text.size(); index++)
	{
		if (index > 0)
		{
			const auto pair = std::make_pair(text[index - 1], text[index]);
			if (font.Kerning.count(pair) > 0)
				pen += font.Kerning.at(pair);
		}
		std::printf("%c at %.2f\n", text[index], pen);
		pen += font.Advance.at(text[index]);
	}
	std::printf("width %.2f em\n", pen);
}

int main()
{
	std::printf("row 3, texels -4 to 11:");
	for (int x = -4; x < c_Size + 4; x++)
		std::printf(" %d", DistanceValue(x, 3));
	std::printf("\n");
	ShapeLine(ToyFont(), "AVA");
	return 0;
}
