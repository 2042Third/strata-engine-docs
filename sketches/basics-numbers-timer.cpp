// Practice 6: one frame of 1/60 s added to a float timer and to a double timer, far from the start.
#include <iomanip>
#include <iostream>

int main()
{
	const float frame = 1.0f / 60.0f;
	const float starts[] = { 20000.0f, 600000.0f };
	std::cout << std::setprecision(9);
	for (const float start : starts)
	{
		float asFloat = start;
		double asDouble = start;
		asFloat += frame;
		asDouble += frame;
		std::cout << start << ": float adds " << asFloat - start << ", double adds " << asDouble - start << '\n';
	}
	return 0;
}
