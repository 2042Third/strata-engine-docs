// Practice 5: the gap from a float to the next float, at 1, 1000 and 20000.
#include <cmath>
#include <iomanip>
#include <iostream>

int main()
{
	const float values[] = { 1.0f, 1000.0f, 20000.0f };
	std::cout << std::setprecision(9);
	for (const float value : values)
		std::cout << value << ": " << std::nextafter(value, 1.0e9f) - value << '\n';
	return 0;
}
