// Counts the luminance of ten pixels into quarter-EV bins and reads percentiles from the bins.
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <cstdio>

constexpr float c_MinEV100 = -8.0f;
constexpr float c_BinsPerEV = 4.0f;
constexpr uint32_t c_BinCount = 128;
constexpr float c_FirstBandEV100 = 5.0f;

// EV100 of a luminance in nits; black reads as a very dark value instead of minus infinity.
float GetEV100(float nits)
{
	return std::log2(std::max(nits, std::exp2(-10.0f))) + 3.0f;
}

// The value below which `fraction` of the counts lie, linear inside the bin it falls in.
float GetPercentile(const std::array<uint32_t, c_BinCount>& bins, float fraction, uint32_t total)
{
	const float target = fraction * static_cast<float>(total);
	uint32_t below = 0;
	for (uint32_t index = 0; index < c_BinCount; index++)
	{
		if (bins[index] == 0)
			continue;
		if (static_cast<float>(below + bins[index]) >= target)
		{
			const float within = (target - static_cast<float>(below)) / static_cast<float>(bins[index]);
			return c_MinEV100 + (static_cast<float>(index) + within) / c_BinsPerEV;
		}
		below += bins[index];
	}
	return c_MinEV100 + static_cast<float>(c_BinCount) / c_BinsPerEV;
}

int main()
{
	const std::array<float, 10> pixels = { 4.0f, 6.0f, 8.0f, 10.0f, 12.0f, 16.0f, 40.0f, 100.0f, 1000.0f, 16000.0f };
	std::array<uint32_t, c_BinCount> bins = {};
	for (float nits : pixels)
	{
		const float ev = GetEV100(nits);
		const uint32_t bin = static_cast<uint32_t>(std::clamp((ev - c_MinEV100) * c_BinsPerEV, 0.0f, static_cast<float>(c_BinCount - 1)));
		const int band = static_cast<int>(std::floor(ev - c_FirstBandEV100));
		bins[bin]++;
		std::printf("%7.0f nits: EV100 %6.3f, bin %3u, band %2d\n", nits, ev, bin, band);
	}
	std::printf("p05 %.3f, p50 %.3f, p95 %.3f\n", GetPercentile(bins, 0.05f, 10), GetPercentile(bins, 0.5f, 10),
		GetPercentile(bins, 0.95f, 10));
	return 0;
}
