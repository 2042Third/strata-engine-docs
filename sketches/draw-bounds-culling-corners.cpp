#include <cmath>
#include <cstdio>

int main()
{
	const float c = std::cos(0.785398f);
	const float s = std::sin(0.785398f);
	const float halfX = 2.0f;
	const float halfY = 1.0f;
	// Wrong: turn only the corners (-2, -1) and (2, 1) and keep the box of those two.
	const float wrongX = std::abs(halfX * c - halfY * s);
	const float wrongY = std::abs(halfX * s + halfY * c);
	// Right (Arvo): add up how far each half size reaches along each axis.
	const float rightX = std::abs(c) * halfX + std::abs(s) * halfY;
	const float rightY = std::abs(s) * halfX + std::abs(c) * halfY;
	// The corner (2, -1) turns to x = 2c + s.
	const float probe = halfX * c + halfY * s;
	std::printf("wrong half sizes: %.3f %.3f\n", wrongX, wrongY);
	std::printf("right half sizes: %.3f %.3f\n", rightX, rightY);
	std::printf("corner (2, -1) turns to x = %.3f\n", probe);
}
