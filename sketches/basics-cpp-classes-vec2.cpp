// Operators for one's own type, as glm has them: + adds, and the compiler writes ==.
#include <iostream>

struct Vec2
{
	float X = 0.0f;
	float Y = 0.0f;

	Vec2 operator+(const Vec2& other) const { return Vec2 { X + other.X, Y + other.Y }; }
	bool operator==(const Vec2& other) const = default;
};

int main()
{
	const Vec2 sum = Vec2 { 1.0f, 2.0f } + Vec2 { 3.0f, 4.0f };
	std::cout << sum.X << " " << sum.Y << "\n";
	std::cout << std::boolalpha << (sum == Vec2 { 4.0f, 6.0f }) << " " << (sum == Vec2 {}) << "\n";
}
