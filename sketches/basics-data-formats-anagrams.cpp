// Practice 4: the toy hash of the data structures page gives "ant" and "tan" one number; FNV-1a does not.
#include <cstdint>
#include <initializer_list>
#include <iostream>
#include <string>

uint64_t FNV1a(const std::string& text)
{
	uint64_t hash = 14695981039346656037ull;
	for (const char character : text)
	{
		hash ^= static_cast<uint8_t>(character);
		hash *= 1099511628211ull;
	}
	return hash;
}

int main()
{
	for (const std::string name : { "ant", "tan" })
		std::cout << name << ": " << std::hex << FNV1a(name) << '\n';
}
