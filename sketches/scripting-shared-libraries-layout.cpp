#include <cstddef>
#include <cstdint>
#include <cstdio>

struct Loose
{
	uint8_t Flag;
	uint32_t Count;
	uint8_t Mode;
};

struct Tight
{
	uint32_t Count;
	uint8_t Flag;
	uint8_t Mode;
};

int main()
{
	std::printf("Loose: size %zu, Count at %zu, Mode at %zu\n", sizeof(Loose), offsetof(Loose, Count), offsetof(Loose, Mode));
	std::printf("Tight: size %zu, Flag at %zu, Mode at %zu\n", sizeof(Tight), offsetof(Tight, Flag), offsetof(Tight, Mode));
	std::printf("bool %zu, long %zu, wchar_t %zu, pointer %zu\n", sizeof(bool), sizeof(long), sizeof(wchar_t), sizeof(void*));
	return 0;
}
