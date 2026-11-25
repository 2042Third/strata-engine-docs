#include <cmath>
#include <cstdio>
#include <initializer_list>

// The frames a re-injected bounce series needs to settle. In a closed room the light after k frames is the first k terms of a
// geometric series with ratio r, so the next frame adds r^k (1 - r) of the limit.
constexpr double c_SettleChange = 0.0025; // Settled when the next bounce adds less than this share
constexpr int c_MarginFrames = 2;

int SettleFrames(double ratio)
{
	int k = 1;
	while (std::pow(ratio, k) * (1.0 - ratio) >= c_SettleChange)
		k++;
	return k + c_MarginFrames;
}

int main()
{
	for (const double albedo : { 0.58, 0.73, 0.9 })
	{
		const int frames = SettleFrames(albedo);
		const double left = std::pow(albedo, frames - c_MarginFrames);
		std::printf("albedo %.2f: %d frames, %.1f %% of the limit still to come after frame %d\n", albedo, frames, 100.0 * left,
			frames - c_MarginFrames);
	}
	return 0;
}
