// How many samples make a level read the same source mip as level 1 does with its 128 samples?
#include <cmath>
#include <cstdio>

constexpr float c_Pi = 3.14159265f;

// The GGX density at the lobe's center, divided by 4 for the reflected direction (N = V).
float CenterPdf(float roughness)
{
	float alpha = roughness * roughness;
	return 1.0f / (c_Pi * alpha * alpha) * 0.25f;
}

int main()
{
	// Level 1 (roughness 0.2) with 128 samples: each sample stands for this solid angle.
	const float target = 1.0f / (128.0f * CenterPdf(0.2f));
	std::printf("target solid angle %.3e\n", target);
	for (int level = 2; level < 6; level++)
	{
		float roughness = static_cast<float>(level) / 5.0f;
		float samples = 1.0f / (CenterPdf(roughness) * target);
		std::printf("level %d  roughness %.1f  needs %.0f samples\n", level, roughness, samples);
	}
	return 0;
}
