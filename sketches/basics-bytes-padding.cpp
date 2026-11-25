#include <cstddef>
#include <cstdint>
#include <cstdio>

struct Loose
{
	uint8_t Kind;
	uint32_t Id;
	uint16_t Count;
};
struct Tight
{
	uint32_t Id;
	uint16_t Count;
	uint8_t Kind;
};
static_assert(sizeof(Loose) == 12 && sizeof(Tight) == 8);

int main()
{
	std::printf("Loose: %zu bytes, Kind at %zu, Id at %zu, Count at %zu\n", sizeof(Loose), offsetof(Loose, Kind), offsetof(Loose, Id), offsetof(Loose, Count));
	std::printf("Tight: %zu bytes, Id at %zu, Count at %zu, Kind at %zu\n", sizeof(Tight), offsetof(Tight, Id), offsetof(Tight, Count), offsetof(Tight, Kind));
}
