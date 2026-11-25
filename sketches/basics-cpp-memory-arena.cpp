// An arena hands out memory in a row: round the offset up to the alignment, give the bytes, move on.
#include <cstddef>
#include <iostream>

struct Arena
{
	alignas(8) unsigned char Bytes[64];
	std::size_t Used = 0;
	std::size_t Allocate(std::size_t size, std::size_t align)
	{
		std::size_t start = (Used + align - 1) / align * align;
		if (start + size > sizeof(Bytes)) return sizeof(Bytes);
		Used = start + size;
		return start;
	}
};

int main()
{
	Arena arena;
	std::cout << arena.Allocate(1, 1) << ' ' << arena.Allocate(8, 8) << ' ' << arena.Allocate(4, 4) << '\n';
	std::cout << arena.Allocate(100, 1) << ' ';
	arena.Used = 0; // free everything at once
	std::cout << arena.Allocate(8, 8) << '\n';
}
