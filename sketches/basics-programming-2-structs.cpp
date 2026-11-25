// A struct groups three floats; a function receives a copy, changes it and returns it.
#include <iostream>

struct Point
{
	float X = 0.0f;
	float Y = 0.0f;
	float Z = 0.0f;
};

Point MoveRight(Point point, float distance)
{
	point.X = point.X + distance; // the copy moves
	return point;
}

int main()
{
	Point start = { 1.0f, 2.0f, 3.0f };
	Point moved = MoveRight(start, 4.0f);
	std::cout << "start " << start.X << ", " << start.Y << ", " << start.Z << '\n';
	std::cout << "moved " << moved.X << ", " << moved.Y << ", " << moved.Z << '\n';
	return 0;
}
