// Practice 4: a constexpr function checked by static_assert, and an enum class cast to a number and back.
#include <cstdint>
#include <iostream>

constexpr int Cube(int n) { return n * n * n; }
static_assert(Cube(3) == 27);

enum class Level : uint8_t
{
	Easy = 1,
	Normal = 2,
	Hard = 3
};

int main()
{
	const int number = static_cast<int>(Level::Hard);
	const Level back = static_cast<Level>(number - 1);
	std::cout << "Hard is " << number << ", one lower is Normal: " << (back == Level::Normal) << '\n';
	std::cout << "cube of 3 is " << Cube(3) << '\n';
	return 0;
}
