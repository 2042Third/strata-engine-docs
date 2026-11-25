#include <cstdio>
#include <string>

bool IsContinuation(char byte)
{
	return (static_cast<unsigned char>(byte) & 0xC0) == 0x80;
}

int main()
{
	const std::string name = "M\xC3\xBCnze"; // "Münze"
	size_t codePoints = 0;
	for (const char byte : name)
	{
		if (!IsContinuation(byte))
			codePoints++;
	}
	std::printf("%zu bytes, %zu code points\n", name.size(), codePoints);
	size_t cut = 2; // Keep two bytes: the second is half of the u with umlaut
	while (cut > 0 && IsContinuation(name[cut]))
		cut--;
	std::printf("the cut moves back to byte %zu and keeps \"%s\"\n", cut, name.substr(0, cut).c_str());
}
