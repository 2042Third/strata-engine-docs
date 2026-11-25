#include <algorithm>
#include <cmath>
#include <cstdio>

constexpr int c_HeadroomStops = 2;
constexpr int c_MaxStops = 24;
constexpr int c_ReadbackDelay = 2;

// The power of two nearest 2^stops, within the range of the pre-exposure.
float PowerOfTwoFor(float stops)
{
	const float limit = static_cast<float>(c_MaxStops);
	return std::ldexp(1.0f, static_cast<int>(std::round(std::clamp(stops, -limit, limit))));
}

// The log2 of the exposure multiplier that a frame meters: daylight, then a dark cave from frame 6.
float MeteredStops(int frame)
{
	return frame < 6 ? -14.3f : -9.0f;
}

int main()
{
	float preExposure = 1.0f;
	for (int frame = 0; frame < 12; frame++)
	{
		// The newest metering that has come back belongs to an earlier frame.
		const int metered = frame - c_ReadbackDelay;
		if (metered >= 0)
		{
			const float target = MeteredStops(metered) - static_cast<float>(c_HeadroomStops);
			// Change only when the current value is more than one stop off.
			if (std::abs(std::log2(preExposure) - target) > 1.0f)
				preExposure = PowerOfTwoFor(target);
		}
		std::printf("frame %2d is drawn with 2^%d\n", frame, static_cast<int>(std::log2(preExposure)));
	}
	return 0;
}
