// Base64 of three bytes: their 24 bits are cut into four groups of 6 bits, and each group picks a character.
#include <cstdint>
#include <iostream>
#include <string>

int main()
{
	const char alphabet[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
	const uint8_t bytes[3] = { 'M', 'a', 'n' };
	const uint32_t bits = (bytes[0] << 16) | (bytes[1] << 8) | bytes[2];
	std::string text;
	for (int shift = 18; shift >= 0; shift -= 6)
	{
		const uint32_t group = (bits >> shift) & 0x3F;
		std::cout << group << ' ';
		text += alphabet[group];
	}
	std::cout << "-> " << text << '\n';
}
