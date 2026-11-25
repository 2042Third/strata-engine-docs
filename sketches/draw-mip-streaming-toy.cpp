#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <vector>

struct Texture
{
	const char* Name;
	uint32_t Size;
	uint32_t MipCount;
	uint32_t Resident;
	float UVPixels;
	float Coverage;
};

uint32_t GetWantedLevel(const Texture& texture)
{
	if (!(texture.UVPixels > 1.0f))
		return texture.MipCount - 1;
	const float level = std::floor(std::log2(static_cast<float>(texture.Size) / texture.UVPixels));
	return static_cast<uint32_t>(std::clamp(level, 0.0f, static_cast<float>(texture.MipCount - 1)));
}

int main()
{
	// A first load holds the tail: the levels up to 32 texels, so level 6 of 2048 and level 5 of 1024.
	std::vector<Texture> textures = {
		{ "Wall", 2048, 12, 6, 512.0f, 0.5f },
		{ "Floor", 2048, 12, 6, 64.0f, 0.8f },
		{ "Statue", 1024, 11, 5, 1024.0f, 0.1f }
	};

	for (uint32_t frame = 1; frame <= 3; frame++)
	{
		Texture* best = nullptr;
		float bestScore = 0.0f;
		for (Texture& texture : textures)
		{
			const uint32_t wanted = GetWantedLevel(texture);
			if (texture.Resident <= wanted)
				continue;
			const float score = static_cast<float>(texture.Resident - wanted) * texture.Coverage;
			if (score > bestScore)
			{
				bestScore = score;
				best = &texture;
			}
		}
		if (!best)
			break;
		std::printf("frame %u: raise %s from level %u to %u (score %.2f)\n", frame, best->Name, best->Resident, GetWantedLevel(*best), bestScore);
		best->Resident = GetWantedLevel(*best);
	}
	return 0;
}
