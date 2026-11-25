// CRC-32C: the checksum of "ab" differs from that of "ba", and "123456789" gives the standard check value.
#include <cstdint>
#include <iostream>
#include <string>

uint32_t CRC32C(const std::string& text)
{
	uint32_t crc = 0xFFFFFFFFu;
	for (const char character : text)
	{
		crc ^= static_cast<uint8_t>(character);
		for (int bit = 0; bit < 8; bit++)
			crc = (crc & 1u) ? (crc >> 1) ^ 0x82F63B78u : crc >> 1;
	}
	return ~crc;
}

int main()
{
	const std::string texts[] = { "ab", "ba", "123456789" };
	for (const std::string& text : texts)
		std::cout << text << ": CRC-32C " << std::hex << CRC32C(text) << '\n';
}
