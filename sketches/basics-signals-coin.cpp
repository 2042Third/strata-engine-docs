// Practice 6: the turn a viewer sees when a coin turns by a fixed angle every frame.
#include <cmath>
#include <iostream>

int main()
{
	const double angles[] = { 350.0, 370.0, 180.0, 90.0 };
	for (const double angle : angles)
		std::cout << angle << " degrees a frame looks like " << std::remainder(angle, 360.0) << " degrees\n";
}
