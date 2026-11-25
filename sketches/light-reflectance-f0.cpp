#include <algorithm>
#include <cmath>
#include <cstdio>

namespace
{

	// The rule of MaterialGPU::GetDielectricF0: 1.5 is written out, other values are clamped to [1, 3].
	float GetDielectricF0(float ior)
	{
		if (ior == 1.5f)
			return 0.04f;
		const float index = std::clamp(ior, 1.0f, 3.0f);
		const float ratio = (index - 1.0f) / (index + 1.0f);
		return ratio * ratio;
	}

	float FresnelSchlick(float f0, float cosine)
	{
		return f0 + (1.0f - f0) * std::pow(1.0f - cosine, 5.0f);
	}

}

int main()
{
	const float cosine60 = std::cos(60.0f * 3.14159265f / 180.0f);
	const float cosine85 = std::cos(85.0f * 3.14159265f / 180.0f);
	const float indices[] = { 1.33f, 1.5f, 2.42f };
	for (float ior : indices)
	{
		const float f0 = GetDielectricF0(ior);
		std::printf("IOR %.2f  F0 %.4f  F(60) %.4f  F(85) %.4f\n", ior, f0, FresnelSchlick(f0, cosine60), FresnelSchlick(f0, cosine85));
	}
	return 0;
}
