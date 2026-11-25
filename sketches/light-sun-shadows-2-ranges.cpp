#include <array>
#include <cmath>
#include <cstdint>
#include <cstdio>

namespace
{
	struct Range
	{
		float Nearest; // Toward the sun: the largest depth, because depth is reversed
		float Farthest;
	};

	// Packs a 4 x 4 cell's range into 16 + 16 bits, rounded outward so the range still holds every depth.
	uint32_t PackRange(const std::array<float, 16>& depths)
	{
		float nearest = 0.0f;
		float farthest = 1.0f;
		for (const float depth : depths)
		{
			nearest = std::fmax(nearest, depth);
			farthest = std::fmin(farthest, depth);
		}
		uint32_t high = static_cast<uint32_t>(std::ceil(nearest * 65535.0f));
		if (high < 65535u && static_cast<float>(high) / 65535.0f < nearest)
			high++;
		uint32_t low = static_cast<uint32_t>(std::floor(farthest * 65535.0f));
		if (low > 0u && static_cast<float>(low) / 65535.0f > farthest)
			low--;
		return (high << 16) | low;
	}

	Range UnpackRange(uint32_t packed)
	{
		return { static_cast<float>(packed >> 16) / 65535.0f, static_cast<float>(packed & 0xFFFFu) / 65535.0f };
	}

	const char* Classify(const Range& range, float receiver)
	{
		if (range.Nearest <= receiver)
			return "lit";
		if (range.Farthest > receiver)
			return "umbra";
		return "needs the filter";
	}
}

int main()
{
	std::array<float, 16> depths;
	depths.fill(0.30f);
	depths[5] = 0.9137f; // A pole one texel wide, near the sun
	depths[10] = 0.1234f; // A hole, far from the sun

	const uint32_t packed = PackRange(depths);
	const Range range = UnpackRange(packed);
	bool holds = true;
	for (const float depth : depths)
		holds = holds && depth <= range.Nearest && depth >= range.Farthest;

	std::printf("packed 0x%08X: nearest %.5f, farthest %.5f, holds every depth: %s\n", packed, range.Nearest, range.Farthest, holds ? "yes" : "no");
	for (const float receiver : { 0.05f, 0.50f, 0.95f })
		std::printf("receiver %.2f: %s\n", receiver, Classify(range, receiver));
	return 0;
}
