#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <cstdio>

struct Influence
{
	uint32_t Joint = 0;
	float Weight = 0.0f;
};

int main()
{
	// Five influences of one vertex (a skin of 8 joints): the importer keeps the four strongest.
	std::array<Influence, 8> candidates = {};
	candidates[0] = { 3, 0.04f };
	candidates[1] = { 5, 0.50f };
	candidates[2] = { 2, 0.30f };
	candidates[3] = { 7, 0.10f };
	candidates[4] = { 1, 0.06f };

	std::stable_sort(candidates.begin(), candidates.end(), [](const Influence& a, const Influence& b) { return a.Weight > b.Weight; });
	const float total = candidates[0].Weight + candidates[1].Weight + candidates[2].Weight + candidates[3].Weight;

	uint16_t weights[4] = {};
	uint32_t sum = 0;
	for (int influence = 0; influence < 4; influence++)
	{
		weights[influence] = static_cast<uint16_t>(std::lround(candidates[influence].Weight / total * 65535.0f));
		sum += weights[influence];
		std::printf("joint %u: %u\n", candidates[influence].Joint, static_cast<unsigned>(weights[influence]));
	}
	std::printf("sum before the fix: %u\n", sum);

	// Rounding leaves the sum a few units off: the strongest influence takes the difference.
	weights[0] = static_cast<uint16_t>(static_cast<int64_t>(weights[0]) + 65535 - static_cast<int64_t>(sum));
	std::printf("strongest after the fix: %u\n", static_cast<unsigned>(weights[0]));
	return 0;
}
