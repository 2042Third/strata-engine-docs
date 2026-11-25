// Applies the two gates box3d uses before it recycles a touching contact (the page's numbers).
#include <cmath>
#include <cstdio>

// distance: how far the bodies' relative pose moved, in metres; turnDegrees: how far one body turned.
// extent: the farthest point of the bodies from their centres, in metres; tolerance: the recycle distance.
static bool Recycles(float distance, float turnDegrees, float extent, float tolerance)
{
	const float cosHalfTurn = std::cos(turnDegrees * 0.5f * 3.14159265f / 180.0f);
	const bool turnedLittle = cosHalfTurn * cosHalfTurn > 0.99240388f;
	// The farthest point swings along an arc of about the turn (in radians) times the extent.
	const float arc = turnDegrees * 3.14159265f / 180.0f * extent;
	return turnedLittle && distance + arc < tolerance;
}

int main()
{
	std::printf("3.0 cm, 1 degree:  %s\n", Recycles(0.030f, 1.0f, 0.87f, 0.05f) ? "recycled" : "collided again");
	std::printf("3.6 cm, 1 degree:  %s\n", Recycles(0.036f, 1.0f, 0.87f, 0.05f) ? "recycled" : "collided again");
	std::printf("0.5 cm, 12 degrees: %s\n", Recycles(0.005f, 12.0f, 0.87f, 0.05f) ? "recycled" : "collided again");
	std::printf("3.0 cm, 1 degree, tolerance 0: %s\n", Recycles(0.030f, 1.0f, 0.87f, 0.0f) ? "recycled" : "collided again");
	return 0;
}
