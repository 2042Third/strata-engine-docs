// What a walker does on a slope: the move along it keeps the part of the wish that does not point into the slope.
#include <cmath>
#include <cstdio>
#include <initializer_list>

int main()
{
	const float pi = 3.14159265f;
	const float maxSlopeDegrees = 45.0f;
	const float walkSpeed = 2.0f;
	const float cosMaxSlope = std::cos(maxSlopeDegrees * pi / 180.0f);

	for (const float degrees : { 30.0f, 40.0f, 50.0f })
	{
		const float angle = degrees * pi / 180.0f;
		// A plane is walkable when the Y part of its normal, the cosine of the slope angle, reaches the limit's cosine.
		const bool walkable = std::cos(angle) >= cosMaxSlope;
		const float alongSlope = walkable ? walkSpeed * std::cos(angle) : 0.0f;
		const float rise = alongSlope * std::sin(angle);
		std::printf("%2.0f degrees: %s, %.2f m/s along the slope, rising %.2f m/s\n", degrees, walkable ? "walkable" : "a wall", alongSlope, rise);
	}
	return 0;
}
