#include <algorithm>
#include <cmath>
#include <cstdio>

namespace
{

	constexpr float c_DegreesToRadians = 3.14159265f / 180.0f;

	struct Light
	{
		float Intensity = 0.0f; // Candela
		float Range = 0.0f;     // Meters
		float InnerDegrees = 0.0f;
		float OuterDegrees = 0.0f;
	};

	// What the shader needs, computed once: 1 / range^2 and the cosines of the cone's angles.
	struct Record
	{
		float Intensity = 0.0f;
		float InverseRangeSquared = 0.0f;
		float CosInner = 1.0f;
		float CosOuter = 1.0f;
		bool Drawn = false;
	};

	Record MakeRecord(const Light& light, bool active)
	{
		Record record;
		if (!active || !(light.Intensity > 0.0f) || !(light.Range > 0.0f) || !std::isfinite(light.Intensity) || !std::isfinite(light.Range))
			return record; // Kept, but not drawn
		record.Intensity = light.Intensity;
		record.InverseRangeSquared = 1.0f / (light.Range * light.Range);
		record.CosInner = std::cos(light.InnerDegrees * c_DegreesToRadians);
		record.CosOuter = std::cos(light.OuterDegrees * c_DegreesToRadians);
		record.Drawn = true;
		return record;
	}

	float Falloff(const Record& record, float distance)
	{
		const float ratio = distance * distance * record.InverseRangeSquared;
		const float window = std::clamp(1.0f - ratio * ratio, 0.0f, 1.0f);
		return window * window / std::max(distance * distance, 1e-4f);
	}

	float Cone(const Record& record, float degreesOffAxis)
	{
		const float cosine = std::cos(degreesOffAxis * c_DegreesToRadians);
		const float t = std::clamp((cosine - record.CosOuter) / std::max(record.CosInner - record.CosOuter, 1e-4f), 0.0f, 1.0f);
		return t * t;
	}

}

int main()
{
	const Record point = MakeRecord({ 10.0f, 10.0f, 0.0f, 0.0f }, true);
	for (const float distance : { 1.0f, 5.0f, 8.0f, 9.0f, 10.0f })
		std::printf("d=%4.1f m: windowed %.4f  plain 1/d^2 %.4f  lux %.4f\n", distance, Falloff(point, distance), 1.0f / (distance * distance),
			point.Intensity * Falloff(point, distance));

	const Record spot = MakeRecord({ 20.0f, 15.0f, 20.0f, 30.0f }, true);
	for (const float degrees : { 0.0f, 10.0f, 20.0f, 25.0f, 30.0f, 35.0f })
		std::printf("%4.1f degrees off axis: cone factor %.4f\n", degrees, Cone(spot, degrees));

	const Record broken = MakeRecord({ std::nanf(""), 10.0f, 0.0f, 0.0f }, true);
	const Record switchedOff = MakeRecord({ 10.0f, 10.0f, 0.0f, 0.0f }, false);
	std::printf("NaN intensity drawn: %d, inactive drawn: %d\n", broken.Drawn ? 1 : 0, switchedOff.Drawn ? 1 : 0);
	return 0;
}
