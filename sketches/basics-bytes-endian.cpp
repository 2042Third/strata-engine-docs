// Writes 300 as four little-endian bytes, reads it back by shifts and by copying memory.
#include <cstdint>
#include <cstdio>
#include <cstring>

int main()
{
	const uint32_t value = 300; // 0x0000012C
	uint8_t bytes[4] = {};
	for (int index = 0; index < 4; index++)
		bytes[index] = static_cast<uint8_t>(value >> (8 * index)); // The lowest byte goes first
	std::printf("little-endian: %02X %02X %02X %02X\n", bytes[0], bytes[1], bytes[2], bytes[3]);
	std::printf("big-endian:    %02X %02X %02X %02X\n", bytes[3], bytes[2], bytes[1], bytes[0]);

	uint32_t again = 0;
	for (int index = 3; index >= 0; index--)
		again = (again << 8) | bytes[index];
	uint32_t copied = 0;
	std::memcpy(&copied, bytes, sizeof(copied)); // Reads the bytes the way this machine does
	std::printf("by shifts %u, by memcpy %u\n", again, copied);
}
