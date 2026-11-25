// A dead zone on one axis: values near rest read 0, the rest is rescaled so that full tilt still reads 1.
#include <cmath>
#include <cstdio>

namespace
{
	float ApplyDeadZone(float value, float deadZone)
	{
		const float magnitude = std::fabs(value);
		if (magnitude <= deadZone)
			return 0.0f;
		const float scaled = (magnitude - deadZone) / (1.0f - deadZone);
		return value < 0.0f ? -scaled : scaled;
	}
}

int main()
{
	const float readings[] = { 0.02f, -0.08f, 0.15f, 0.20f, 0.575f, -1.0f, 1.0f };
	for (const float reading : readings)
		std::printf("device %+.3f -> game %+.4f\n", reading, ApplyDeadZone(reading, 0.15f));
	return 0;
}
