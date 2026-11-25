// Two numbers packed into one 32-bit integer and taken out again, and the zeros below the lowest set bit.
#include <bit>
#include <cstdint>
#include <iostream>

int main()
{
	const uint32_t index = 5;
	const uint32_t version = 3;
	const uint32_t handle = (version << 20) | index;
	std::cout << "handle: " << handle << '\n';
	std::cout << "index: " << (handle & 0xFFFFF) << '\n';
	std::cout << "version: " << (handle >> 20) << '\n';
	std::cout << "trailing zeros of 40: " << std::countr_zero(40u) << '\n';
	return 0;
}
