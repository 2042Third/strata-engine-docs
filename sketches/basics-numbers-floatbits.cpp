// The 32 bits of three floats, split into the sign, the exponent field and the significand field.
#include <bit>
#include <bitset>
#include <cstdint>
#include <iostream>
#include <string>

int main()
{
	const float values[] = { 0.15625f, 1.0f, -2.5f };
	for (const float value : values)
	{
		const std::bitset<32> bits(std::bit_cast<uint32_t>(value));
		const std::string text = bits.to_string();
		std::cout << value << ": " << text.substr(0, 1) << " " << text.substr(1, 8) << " " << text.substr(9) << '\n';
	}
	return 0;
}
