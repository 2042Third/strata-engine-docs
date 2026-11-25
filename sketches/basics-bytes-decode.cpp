// Decodes valid UTF-8 into code points: the lead byte gives the length, each continuation byte six bits.
#include <cstdint>
#include <cstdio>
#include <string>

int main()
{
	const std::string text = "M\xC3\xBCnze \xE2\x82\xAC \xF0\x9F\x98\x80";
	for (size_t index = 0; index < text.size();)
	{
		const uint8_t lead = static_cast<uint8_t>(text[index]);
		const size_t length = lead < 0x80 ? 1 : lead < 0xE0 ? 2 : lead < 0xF0 ? 3 : 4;
		uint32_t codePoint = lead;
		if (length > 1)
			codePoint &= 0x7Fu >> length; // Keep the lead byte's payload bits
		for (size_t next = 1; next < length; next++)
			codePoint = (codePoint << 6) | (static_cast<uint8_t>(text[index + next]) & 0x3Fu);
		std::printf("length %zu: U+%04X\n", length, codePoint);
		index += length;
	}
}
