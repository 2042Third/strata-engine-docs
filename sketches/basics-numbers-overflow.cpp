// Practice 2: a 16-bit counter that wraps, and division with positive and negative dividends.
#include <cmath>
#include <cstdint>
#include <iostream>

int main()
{
	uint16_t counter = 65535;
	counter = static_cast<uint16_t>(counter + 1);
	std::cout << "65535 + 1 in 16 bits: " << counter << '\n';
	std::cout << "7 / 2 = " << 7 / 2 << '\n';
	std::cout << "-7 / 2 = " << -7 / 2 << '\n';
	std::cout << "-7 % 2 = " << -7 % 2 << '\n';
	std::cout << "floor of -7 / 2.0 = " << std::floor(-7 / 2.0) << '\n';
	return 0;
}
