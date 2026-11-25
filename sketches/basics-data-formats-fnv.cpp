// FNV-1a of the one-byte text "a": the XOR puts the byte in, and the multiplication spreads it over the 64 bits.
#include <cstdint>
#include <iostream>

int main()
{
	const uint64_t offsetBasis = 14695981039346656037ull;
	const uint64_t prime = 1099511628211ull;
	uint64_t hash = offsetBasis;
	std::cout << std::hex << "start:       " << hash << '\n';
	hash ^= static_cast<uint8_t>('a');
	std::cout << "after XOR:   " << hash << '\n';
	hash *= prime;
	std::cout << "after times: " << hash << '\n';
}
