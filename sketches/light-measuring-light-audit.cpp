// Audits linear base colors the way the Albedo view does: by luminance, against 0.03 and 0.85.
#include <cstdio>

struct Material
{
	const char* Name;
	float Red;
	float Green;
	float Blue;
};

constexpr float c_AlbedoLow = 0.03f;
constexpr float c_AlbedoHigh = 0.85f;

float GetLuminance(const Material& material)
{
	return 0.2126f * material.Red + 0.7152f * material.Green + 0.0722f * material.Blue;
}

int main()
{
	const Material materials[] = {
		{ "rough copper", 0.955f, 0.638f, 0.538f },
		{ "polished gold", 1.000f, 0.766f, 0.336f },
		{ "wet asphalt", 0.020f, 0.020f, 0.022f },
	};
	for (const Material& material : materials)
	{
		const float albedo = GetLuminance(material);
		const char* verdict = albedo < c_AlbedoLow ? "marked blue (too dark)" : albedo > c_AlbedoHigh ? "marked red (too bright)" : "in range";
		std::printf("%-14s luminance %.3f: %s\n", material.Name, albedo, verdict);
	}
	return 0;
}
