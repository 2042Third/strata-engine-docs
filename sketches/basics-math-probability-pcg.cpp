// A PCG32 generator like the SDK's Random, started from three seeds: equal seeds give equal numbers.
#include <cstdint>
#include <cstdio>

struct Pcg32
{
	uint64_t State = 0;

	uint32_t Next()
	{
		const uint64_t old = State;
		State = old * 6364136223846793005ull + 1442695040888963407ull;
		const uint32_t shifted = static_cast<uint32_t>(((old >> 18u) ^ old) >> 27u);
		const uint32_t rotation = static_cast<uint32_t>(old >> 59u);
		return (shifted >> rotation) | (shifted << ((32u - rotation) & 31u));
	}
};

int main()
{
	Pcg32 first{ 0x853c49e6748fea9bull }, second{ 0x853c49e6748fea9bull }, third{ 0x0123456789abcdefull };
	for (int draw = 0; draw < 3; draw++)
		std::printf("%10u %10u %10u\n", first.Next(), second.Next(), third.Next());
	return 0;
}
