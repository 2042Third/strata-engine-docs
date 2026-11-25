// Practice 7: PlaceCoin turns an index into a position, and a loop places five coins in a line.
#include <iostream>

struct Point
{
	float X = 0.0f;
	float Y = 0.0f;
	float Z = 0.0f;
};

Point PlaceCoin(int index, float spacing = 2.0f)
{
	return { index * spacing, 1.0f, 0.0f }; // the coins stand along the X axis
}

int main()
{
	for (int i = 0; i < 5; i++)
	{
		Point spot = PlaceCoin(i);
		std::cout << "coin " << i << " at " << spot.X << ", " << spot.Y << ", " << spot.Z << '\n';
	}
	return 0;
}
