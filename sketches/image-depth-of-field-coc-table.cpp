#include <algorithm>
#include <cstdio>
#include <initializer_list>

namespace
{

	struct Lens
	{
		float FocalLength;   // Millimeters
		float FNumber;
		float SensorHeight;  // Millimeters
		float FocusDistance; // Meters
	};

	// The signed diameter of the circle of confusion, in pixels, of a point `distance` meters away; negative in front of the focus.
	float GetCircleOfConfusion(const Lens& lens, float distance, float rows)
	{
		const float focus = std::max(lens.FocusDistance * 1000.0f, 1.1f * lens.FocalLength);
		const float scale = lens.FocalLength * lens.FocalLength / (lens.FNumber * (focus - lens.FocalLength));
		const float millimeters = distance * 1000.0f;
		const float onSensor = scale * (millimeters - focus) / millimeters;
		const float pixels = onSensor / lens.SensorHeight * rows;
		const float limit = 0.02f * rows;
		return std::clamp(pixels, -limit, limit);
	}

}

int main()
{
	const Lens lens = { 50.0f, 4.0f, 24.0f, 3.0f };
	for (float distance : { 1.0f, 2.0f, 3.0f, 6.0f, 12.0f, 100.0f })
		std::printf("%6.1f m: %6.1f pixels\n", distance, GetCircleOfConfusion(lens, distance, 1080.0f));
	return 0;
}
