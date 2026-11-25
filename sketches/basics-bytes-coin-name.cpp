// The Coin Run exercise on its own: the length of a name in bytes and in code points.
#include <cstdio>
#include <string>

int main()
{
	const std::string name = "M\xC3\xBCnze"; // The coin's name as the engine stores it: UTF-8
	size_t codePoints = 0;
	for (const char byte : name)
	{
		if ((static_cast<unsigned char>(byte) & 0xC0) != 0x80) // Not a continuation byte
			codePoints++;
	}
	std::printf("%zu bytes, %zu code points\n", name.size(), codePoints);
}
