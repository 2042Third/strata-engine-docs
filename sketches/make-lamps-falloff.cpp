// The light a lamp puts on a surface that faces it: the inverse square law and Strata's window to the range.
#include <algorithm>
#include <cstdio>

float GetLux(float candela, float range, float distance)
{
	const float ratio = (distance * distance) / (range * range);
	const float window = std::clamp(1.0f - ratio * ratio, 0.0f, 1.0f);
	return candela * window * window / (distance * distance);
}

int main()
{
	const float candela = 64.0f;
	const float range = 8.0f;

	std::printf("distance  plain lux  windowed lux\n");
	for (float distance : { 1.0f, 2.0f, 4.0f, 6.0f, 8.0f })
		std::printf("%5.0f m  %9.2f  %12.2f\n", distance, candela / (distance * distance), GetLux(candela, range, distance));
	return 0;
}
