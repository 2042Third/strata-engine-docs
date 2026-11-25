#include <cstdint>
#include <cstdio>

struct Random
{
	explicit Random(uint64_t seed) { Next(); State += seed; Next(); }
	uint32_t Next()
	{
		const uint64_t state = State;
		State = state * 6364136223846793005ull + 1442695040888963407ull;
		const uint32_t xorShifted = static_cast<uint32_t>(((state >> 18u) ^ state) >> 27u), rotation = static_cast<uint32_t>(state >> 59u);
		return (xorShifted >> rotation) | (xorShifted << ((32u - rotation) & 31u));
	}
	uint64_t State = 0;
};

int main()
{
	for (int run = 0; run < 3; run++)
	{
		Random random(run < 2 ? 42 : 7);
		for (int roll = 0; roll < 5; roll++)
			std::printf("%u%c", random.Next() % 6 + 1, roll == 4 ? '\n' : ' ');
	}
}
